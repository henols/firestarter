# Phase 141: Per-Byte Program Loop - Context

**Gathered:** 2026-08-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace `firestarter/src/proms/eprom.cpp`'s block-level mismatch-mask retry loop with a **per-byte
pulse→verify loop** driven by Phase 140's `eprom_params_for()` table: fixed-width pulses counted per
byte, verify after every pulse, overprogram and energy-cap rules read from the table, hard-fail on
budget exhaustion with the failing address and its pulse count, skip logic for already-matching and
`0xFF` bytes, a 32-bit-safe delay helper, and VPE asserted once per block rather than per byte.

**Requirements:** LOOP-01, LOOP-02, LOOP-03, LOOP-04, LOOP-05, LOOP-06, LOOP-07, LOOP-08.

**This phase is TRI-REPO** (see D-04). `commits_land_in:` must name **all three**:
- `firestarter/` — the loop rewrite, the delay helper, the new native suite, the re-derived D-13 gate golden.
- `tools/catalog/messages.toml` in the **meta repo** — the two new message IDs are authored here (this
  is the canonical catalog; both sub-repos carry synced copies).
- `firestarter_app/` — **generated files only**, produced by `tools/catalog/sync_to_subrepos.sh` +
  codegen. No host CLI behaviour changes here.

A plan that only *reads* a submodule still names it — a worktree leaves submodules empty and
`files_modified` under-detects.

**Not in this phase:**
- VPP/VPE routing consolidation, the shared routing-mask set, and disable-on-every-exit as a
  *general* guarantee — **Phase 142** (VPP-01…04). This phase must satisfy LOOP-05's own
  disable-on-max-pulse-failure exit, and Phase 142 re-verifies every exit rather than assuming it.
- `--pulse-us`, host timeout, host progress rendering, and turning the new message IDs into
  user-facing program failures — **Phase 143** (HOST-01…05).
- Freezing the old golden trace, authoring the new one, and diffing them; the flash/RAM delta
  reconciliation; the TEST-01 requirement flip — **Phase 144** (TEST-01…08).
- Any `chip_database.json` change, any new database field, any second firmware dispatch selector.
  `protocol_id` remains the sole dispatch key (TABLE-05, still binding).

</domain>

<decisions>
## Implementation Decisions

### `0x0B` energy-cap arithmetic (the discussed area)

- **D-01:** When the next full-width pulse would cross the 50 ms cap, the loop EMITS that pulse, then
  stops. Overshoot is bounded by exactly one pulse width. Chosen over stop-before-overshoot
  (which leaves the tail of the budget unused) and over truncating the final pulse (which would emit
  a pulse of a different width than every other pulse and muddy LOOP-01's fixed-width guarantee and
  the golden trace).
  **Consequence the planner must carry:** with `--pulse-us` at its uint16 ceiling the effective
  per-byte ceiling becomes `50000 + 65535 ≈ 115 ms`, not 50 ms. D-03's pre-flight refusal is what
  keeps that bounded in the pathological direction; the one-pulse overshoot is accepted deliberately.
  With every *shipped* database width the cap divides evenly (500 µs → 100 pulses, 1000 → 50,
  200 → 250), so this rule is only reachable via `--pulse-us`.

- **D-02: The accumulated total counts PULSE WIDTHS ONLY — `accumulated = N × pulse_delay`.**
  (Operator delegated: "you decide".) It is the datasheet's own meaning of `t_w(PR)` — time VPE is
  actually applied through CE — and it is the only variant a native test can assert, since the
  native stubs record no time at all (`delay()` is unstubbed, so a wall-clock rule would be
  untestable off-hardware). Explicitly **not** counted: `memory_set_data`'s 3 µs pre-pulse settle,
  the verify read's strobe, and address-setup time. A verify read is not programming.
  *Rejected:* wall-clock elapsed (non-deterministic pulse counts, untestable natively);
  pulse + 3 µs overhead (makes the expected pulse count depend on a constant buried in `memory.cpp`,
  for ~0.6% of the budget at 500 µs).

- **D-03:** A pulse wider than the row's energy cap is REFUSED pre-flight, before any high voltage is
  enabled. In `configure_eprom`, when `energy_cap_us > 0 && pulse_delay > energy_cap_us`, fail
  closed with a named error. Without this, D-01's rule would apply a single up-to-65 ms VPE pulse to
  real silicon and then report a *verify* failure — a misconfiguration wearing a silicon-failure
  costume. This is also the firmware-side backstop for Phase 143's `--pulse-us` bounds, independent
  of host validation.
  *Rejected:* accepting the uniform rule (smallest flash, but applies HV before failing and produces
  a misleading diagnostic); silently clamping the pulse to the cap (a silent substitution — the
  emitted width would no longer match what the user asked for or what the trace claims).

- **D-04:** The two budget limits get DISTINCT message IDs — `max_pulses` exhaustion and energy-cap
  exhaustion are separately named on the wire. (Phase 140 D-07 requires the error to report which
  limit tripped; this decides how.) Authored in **meta's `tools/catalog/messages.toml`**, synced with
  `tools/catalog/sync_to_subrepos.sh` and regenerated in **both** sub-repos so the generated files
  match. Phase 141 stops there — Phase 143's HOST-03 owns turning an ID into a user-facing program
  failure.
  **Cost correction, recorded because the discussion carried the wrong figure at first:**
  `messages.h` is **ID-only `#define`s** (`MSG_ERR_WRITE_FAILED 0xB1`); the wording lives host-side.
  Two new IDs cost the extra call sites, **not** two PROGMEM strings. The option was chosen under a
  materially overstated flash cost, and the real cost is lower — the decision stands on better
  ground than it was made on.
  **Never hand-edit generated output:** `codegen.py` emits ruff-clean, format-stable `messages.py`;
  do not normalize it. The new IDs are in scope for Phase 144 / TEST-04's cross-repo constants parity
  leg.
  *Rejected:* one message + a reason discriminator byte (fewer IDs, but a reason byte is invisible in
  the host's message table and needs a second decode layer); no discriminator (the host holds no copy
  of the table, so it cannot tell 255 pulses-by-count from 250 pulses-by-energy apart).

### Claude's Discretion

The operator answered **"[No preference]"** to the four structural gray areas and delegated D-02.
These are **decided here, not deferred** — research and planning must treat them as settled and not
re-open them with the operator.

- **D-05:** The loop reuses `handle->firestarter_set_data` / `handle->firestarter_get_data` as its
  pulse and verify primitives — no EPROM-local duplicate write path is written. A duplicate would
  bypass `mem_util_remap_address_bus` (the per-chip bus config), which is a correctness hazard, and
  would cost more flash than LOOP-02's removals free. Reusing them also keeps Phase 144 / TEST-06's
  trace diff attributable to *cadence* changes rather than to a new primitive emitting different
  register writes.

- **D-06:** LOOP-07's safe delay helper is applied at BOTH `delayMicroseconds(handle->pulse_delay)`
  sites, and it lives beside `mem_util_*` (`memory_utils.h` / `memory.cpp`), not in `eprom.cpp`.
  LOOP-07's claim is global ("no call path can reach `delayMicroseconds()` above 16383 µs"), and the
  full site inventory is exactly two: `memory.cpp:329` (`memory_set_data` — the pulse, reached by
  every protocol) and `eprom.cpp:283` (the erase pulse). Every other `delayMicroseconds()` call in
  the tree takes a compile-time constant (1/3/4/10) or an already-clamped read-timing value
  (`memory.cpp:225`/`:235`, capped at 1000 µs at parse time). Fixing `memory_set_data` alone would
  leave the erase pulse unsafe and LOOP-07 false.
  **Structure it as a pure split + the delay calls** so the ms/µs split is unit-testable — native
  stubs record no time, so a test can only assert the arithmetic, never the elapsed duration.

- **D-07:** The overprogram pulse is expressed by save/restore of `handle->pulse_delay` around a single
  `firestarter_set_data` call — the existing `org_delay` idiom (`eprom.cpp:161,172`), not a new width
  parameter. Adding a width argument to the primitive would change every call site's signature
  across every protocol handler — a large diff to serve a path that is unreachable with shipped data
  (see D-08).

- **D-08: LOOP-03 is proven through a PURE FUNCTION, not through the table.** Phase 140 shipped
  `overprogram_factor = 0` on **all three rows** (140-PARAM-TABLE-RECORD §§3-4 — three vendors'
  datasheets each specify no overprogram step), so no live row can exercise the overprogram path.
  Extract the duration as a pure `(pulse_count, pulse_us, factor, cap_us) → us` function and test it
  directly at `factor = 3`, including the clamp at `overprogram_cap_us` and 32-bit overflow safety
  at `3 × 25 × 65535`. Separately assert that all three **live** rows emit zero extra pulses.
  **State the non-claim plainly in the phase record:** the end-to-end overprogram path is proven only
  in its arithmetic and its gating, never in the loop, because no shipped row reaches it. Hand that
  to Phase 146 alongside F-140-05.
  *Rejected:* a test-only injection seam (`#ifdef`/weak symbol) into the production table — a
  production seam that exists only for tests; shipping it untested (TEST-01 asks for proof).

- **D-09:** LOOP-08's DIP32 clause is discharged by an explicit guarded path plus a test — the ROUTE
  choice stays Phase 142's. `mem_util_calculate_top_address_register` (`memory.cpp:159-173`) adds
  `CTRL_VPP_VPE_DROP_ENABLE` to the preserved mask **only when `pins < 32`**; on a 32-pin part that
  bit *is* A16 and is driven by the address, so the drop path cannot be held across a block. `0x08`
  is `PROTO_EPROM_32PIN` *and* ships `vpp_path = VPP_PATH_DROP_RESISTOR`, so this is the row where
  the collision actually bites. The existing mechanism is
  `eprom_internal_set_control_register`'s `using_p1_as_vpp()` remap (`eprom.cpp:320`,
  `memory_utils.h:24`).
  **Phase 141's obligation:** the loop must not silently depend on the drop bit surviving
  `set_address` on `pins >= 32`; the DIP32 case is a named, commented branch, and a native test
  asserts the emitted CONTROL writes across a block that crosses an A16 boundary on a 32-pin part.
  Consolidating the masks and picking the final route is VPP-01/VPP-03, Phase 142 — hand it this
  finding rather than pre-empting it.

- **D-10: `native_trace_v131` goes RED in this phase and is NOT re-frozen here.** Phase 140's D-10
  kept it GREEN deliberately so the first legitimate trace movement would be this phase's; a fixture
  re-frozen by the phase that breaks it stops being evidence. Phase 141 (a) captures the new trace as
  a committed artifact so Phase 144 / TEST-06 has both sides, and (b) names the RED explicitly in its
  record so no reader mistakes it for a regression.
  **Because that fixture cannot verify this phase, Phase 141 authors its own native suite** — a
  **sixth** env on the `native_params_v131` precedent: it names only its own suite in `test_filter`,
  is never folded into `native` / `native_nodevtools` (both pinned at exactly 141 cases / 17 suites
  by the live `size_baseline.json`), is never in `default_envs`, and is never passed to
  `check_size_baseline.py` (unknown env → uncaught `KeyError`, exit 1 — F-138-05) or
  `check_build_warnings.py` (exit 2). It runs in **no CI leg of either repo** — a run-by-name
  obligation recorded in the phase record, never implied as CI coverage.
  **Seam with Phase 144:** TEST-01 owns the requirement flip and the consolidated accounting; this
  phase's suite is its *own* verification. Same split as 140-04 vs TEST-01 — record it so Phase 144
  does not double-author.

- **D-11:** The D-13 protocol-branch-inventory gate WILL go RED, and must be re-derived by its own
  scanner — never hand-edited. `firestarter/tests/test_protocol_branch_inventory.py` +
  `tests/golden/protocol_branch_inventory.json` pin 3 tier-1 (protocol-keyed) and 21 tier-2
  (handle-field-keyed) predicate sites in `eprom.cpp` (F-140-10 corrected the count from the 3 the
  research pass predicted). Rewriting the write path moves the tier-2 inventory. **Record the
  shrinkage as evidence of LOOP-02's removals** — that visibility is exactly what D-13 was built for.
  The loop must add **no new tier-1 site**: it reads the table, and D-03's pre-flight refusal is
  keyed on `energy_cap_us`, not on `protocol`.

- **D-12:** Phase 141 adds NO chunking and NO progress emission — but must not structurally preclude
  them. HOST-01/02 are Phase 143's. Keep the loop shaped so it can later adopt
  `mem_util_blank_check`'s operation-in-progress + `progress_data` pattern (`memory.cpp:379-413`)
  without another rewrite.
  **Finding to hand forward:** the roadmap calls Phase 143 "independent of 140–142 (different repo)",
  yet HOST-02's own named precedent — the blank-check progress/chunk pattern — is a **firmware**
  pattern. If HOST-02 needs intra-block emission, part of Phase 143 lands in `firestarter/`, not
  `firestarter_app/`. Name this before Phase 143 plans, not after.

- Free within the above: the loop's exact function decomposition and naming; `uint8_t` vs `uint16_t`
  for the per-byte pulse counter (`max_pulses` is `uint8_t`; `0x0B` ships 255); the pure helper's
  signatures; the sixth env's name and its `test_filter` / `-I` entries; plan and wave structure.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone decision record (locked — do not re-litigate)
- `.planning/PROJECT.md` §"Current Milestone: v1.31" — the C1/C2/C3 correction table, milestone
  **D-01** (protocol owns *shape*, database owns the *pulse*), **D-02** (`0x0B`'s 50 ms energy cap,
  reasoned not derived), the expected-throughput table, and the **~6.25 V evidence ceiling**.
  **Two of its statements are now known wrong and are Phase 146's to reconcile — do not implement
  from them:** its throughput table gives `0x07`/`0x08` a `3 × N` overpulse (shipped value is `0` on
  both — F-140-05, and §4 of the Phase 140 record), and **C3**'s "no *pulse* comes near
  [16383 µs]" is true of database pulses but false once `--pulse-us` ships (see `<specifics>`).
- `.planning/ROADMAP.md` §"Phase 141: Per-Byte Program Loop" — the five success criteria; and
  §"Phase 142" / §"Phase 143" / §"Phase 144" for the seams D-09, D-12 and D-10 hand forward.
- `.planning/REQUIREMENTS.md` §"Per-Byte Program Loop" lines 183-201 — LOOP-01…08 verbatim.
- `.planning/phases/140-parameter-table/140-CONTEXT.md` — Phase 140's D-01…D-15. **D-03** (the
  `pulse_delay == 0` fallback switch stays in `configure_eprom`), **D-05** (NULL row → fail closed),
  **D-07** (on `0x0B` both `max_pulses` and `energy_cap_us` bind, whichever trips first, and the
  error reports which), **D-08** (the overprogram cap CLAMPS), **D-15** (every gate seen RED on a
  planted violation first) all bind here.
- `.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md` — **the shipped row values (§2)
  are the authority, not `PROJECT.md`'s prose.** §3/§4 name why `overprogram_factor = 0` everywhere;
  §5 states `overprogram_cap_us` is inert on every row; §9 lists what Phase 140 did **not** verify;
  §11 is the explicit hand-off to this phase.
- `.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md` — the frozen, publicly posted
  correction. What this phase ships must reconcile against it in Phase 146 / CLOSE-04.

### Firmware code this phase rewrites
- `firestarter/src/proms/eprom.cpp` — the whole write path. `:20` `NUMBER_OF_RETRIES`;
  `:114-126` `program_mismatched_bytes()`; `:129-141` `verify_and_update_mask()`; `:143-193`
  `eprom_write_execute` (the block loop, the `:177` adaptive growth formula, the `:181` single-route
  disable, the `:182-191` failure report); `:41-77` `configure_eprom` (D-03's pre-flight refusal goes
  here, beside the `:70-76` fallback switch that **stays**); `:283` the erase pulse (D-06's second
  site); `:320` `eprom_internal_set_control_register`'s `using_p1_as_vpp` remap (D-09).
- `firestarter/src/proms/memory.cpp` — `:249-258` `memory_set_data` (**the pulse**: `chip_input` →
  remap(WRITE) → `set_address` → 3 µs settle → `chip_enable` → `delayMicroseconds(pulse_delay)` →
  `chip_disable`); `:203-241` `memory_get_data` (**the verify read**: `chip_output` → remap(READ) →
  `set_address` → strobe); `:159-173` `mem_util_calculate_top_address_register` (**D-09's
  `pins < 32` mask**); `:307-341` `mem_util_blank_check` (D-12's progress/chunk precedent).
- `firestarter/include/rurp_shield.h:108-131` — `rurp_chip_enable/disable/output/input` are
  **dedicated pins**, not shift-register control bits. This is the mechanical basis for LOOP-08:
  a verify read does not disturb the control register, so VPE survives it and the settle stays
  amortized once per block.
- `firestarter/include/memory_utils.h:24` — `using_p1_as_vpp()`, D-09's existing mechanism.
- `firestarter/include/firestarter.h:194-203` — `mem_size`, `address`, `pulse_delay` (`uint32_t`),
  `data_size`.
- `firestarter/include/eprom_params.h` — `eprom_params_t`'s six columns, the two enums, and
  `eprom_params_for()`. **Read the header comment:** the returned pointer is into PROGMEM and every
  field must be read with `pgm_read_byte` / `pgm_read_dword` — a direct dereference compiles and
  silently returns RAM garbage on AVR.
- `firestarter/src/proms/eprom_params.cpp` — `EPROM_PARAM_KEYS[]` / `EPROM_PARAMS[]`, the linear-scan
  accessor, NULL on no match.

### Message catalog (tri-repo, D-04)
- `tools/catalog/messages.toml` — **meta repo, the canonical catalog.** New IDs are authored here.
- `tools/catalog/sync_to_subrepos.sh` and `tools/catalog/codegen.py` — the sync + regen path.
- `firestarter/include/messages.h` — **generated, ID-only `#define`s, DO NOT EDIT.** Existing
  `MSG_ERR_WRITE_FAILED 0xB1` (`:93`), `MSG_ERR_VERIFY 0xAF` (`:91`).

### Gates, baselines and fixtures this phase disturbs
- `firestarter/tests/test_protocol_branch_inventory.py` + `tests/golden/protocol_branch_inventory.json`
  — D-11: goes RED, re-derive with the scanner, never hand-edit.
- `firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp` — full ordered
  positional equality against the frozen pre-change trace. D-10: goes RED here, **not** re-frozen.
- `firestarter/platformio.ini` §`[env:native_trace_v131]` and §`[env:native_params_v131]` — the
  template for D-10's sixth env, including the HARD CONSTRAINT comment block.
- `firestarter/scripts/baseline/size_baseline.json` — the **live** baseline; asserts exactly
  141 cases / 17 suites on both pinned native envs. Adding a case to either turns it RED.
- `firestarter/scripts/baseline/size_baseline_v131.json` — frozen for Phase 144 / TEST-08; read only
  via an explicit `--baseline` argument. Uno-class headroom: **+22/64 B (`uno`), +28/64 B
  (`uno328pb`), −56 B (`leonardo`, must-not-grow)**; RAM delta must be **exactly 0**.
- `.planning/phases/138-preconditions-baseline/138-BASELINE.md` §7 — **F-138-02** (headroom at the
  live `beta` tip is 8 B / 2 B, not 42/36) and **F-138-05** (both live gates are blind to a
  non-pinned native env).
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — the shared native stub layer; extend
  it rather than re-deriving `rurp_*` stubs. **Two known blind spots:** the stubs record no time
  (`delay()` unstubbed), so no test can prove a timing change; and register-write elision is invisible
  unless `rurp_register_utils.h` is included in the stubs.
- `firestarter/CLAUDE.md` §"Algorithm Handlers" — its `0x07`/`0x08`/`0x0B` rows were corrected in
  140-06 against the shipped citations. If this phase changes observable behaviour those rows
  describe, update them in the same change.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`memory_set_data()` / `memory_get_data()` (`memory.cpp:321`, `:203`)** — already the pulse and
  the verify read. D-05 reuses them via the `handle->firestarter_*` indirection rather than writing
  EPROM-local duplicates.
- **The `org_delay` save/restore idiom (`eprom.cpp:161,172`)** — the existing, in-tree way to emit a
  pulse of a width other than `handle->pulse_delay`. D-07 reuses it for the overprogram pulse.
- **`mem_util_blank_check`'s operation-in-progress + `progress_data` pattern
  (`memory.cpp:379-413`)** — D-12's shape-compatibility target, and HOST-02's named precedent.
- **`[env:native_params_v131]` (`platformio.ini`)** — a complete worked instance of a native env
  that names only its own suite, stays out of `default_envs`, and is deliberately excluded from both
  live gates, with the reasoning written in as comments. D-10 copies it wholesale, comments included.
- **`configure_eprom`'s existing structure (`eprom.cpp:41-77`)** — already the single place that
  runs before any hardware is touched. D-03's pre-flight refusal belongs here, next to the
  `pulse_delay == 0` fallback switch it must run after.

### Established Patterns
- **`protocol_id` is the sole dispatch key, end to end.** The loop reads the table; it does not
  branch on `handle->protocol`. TABLE-05 and D-11 both enforce this mechanically.
- **Fail closed with zero hardware side effects** (`memory.cpp` steps 6a/6b/7, Phase 64 / v1.20) —
  the idiom D-03's refusal and `eprom_params_for()`'s NULL return both follow.
- **A gate that has only ever passed is untrusted** (D-15). Plant the violation, watch it go RED,
  then fix it — and fix the locator, not the assertion, because a pre-authored gate leg can be
  unreachable.
- **`messages.h` is codegen-generated and ID-only** — authored in the meta catalog and regenerated,
  never hand-edited. A wording-only change produces a zero-byte firmware diff.
- **Cite by commit or `file:line`, never by recollection.**
- **Baselines are frozen deliberately, never moved by the phase that breaks them.**

### Integration Points
- `configure_eprom` → `eprom_params_for(handle->protocol)` — **the first `src/` call site of Phase
  140's table.** The AVR flash cost `--gc-sections` deferred out of Phase 140 (F-140-02) lands here,
  funded by LOOP-02's removals. Predict the delta before measuring it; a surprise here is Phase 144 /
  TEST-08's problem to reconcile.
- `eprom_write_execute` ← `memory.cpp:115`'s `configure_eprom` dispatch — unchanged.
- Phase 142 replaces this phase's `vpp_path` consumers and re-verifies every exit's disable.
- Phase 143 consumes the two new message IDs (HOST-03) and may need the D-12 chunking seam.
- Phase 144 diffs the trace, flips TEST-01, and reconciles the flash/RAM delta.

</code_context>

<specifics>
## Specific Ideas

- **The `--pulse-us` / 16383 µs interaction corrects milestone C3, and it is this phase's finding.**
  Measured live against the shipped `chip_database.json` during this discussion: **zero** chips carry
  a pulse width above 1000 µs (the full set is 10/20/50/100/200/500/1000 µs; 417 entries read
  "Algorithm Controlled"). So from database data alone `delayMicroseconds()` never sees an
  over-ceiling value — C3 is right about that. But `--pulse-us` is a uint16 wire field with a 65535 µs
  ceiling, **4× `delayMicroseconds()`'s 16383 µs limit**, so the *base* pulse becomes an over-ceiling
  caller the moment Phase 143 ships. C3's "the helper is needed for the overprogram pulse, not for any
  bare pulse" is therefore true of the database and false of the CLI. Since `overprogram_factor = 0`
  on every shipped row, **`--pulse-us` is the only live caller LOOP-07's helper will have.** Hand this
  to Phase 146 / CLOSE-04 alongside F-140-05 and F-140-07 — three published statements now needing
  reconciliation, not one.

- **State the flash-delta prediction before measuring it, as Phase 140 did.** This phase both *adds*
  (the table's 3 × 12 B PROGMEM + accessor, finally referenced; the per-byte loop; the delay helper;
  two call sites) and *removes* (`program_mismatched_bytes`, `verify_and_update_mask`, the 64-byte
  `mismatch_bitmask` stack array, the adaptive growth formula, `NUMBER_OF_RETRIES`). The Uno-class
  band is genuinely tight — **8 B / 2 B at the live `beta` tip** per F-138-02 — and RAM delta must be
  **exactly 0**, which the removed `DATA_BUFFER_SIZE / 8` stack array helps rather than hurts. A
  prediction committed before the measurement is what makes the measurement evidence.

- **Name the D-13 inventory shrinkage rather than just letting the gate turn green again.** The
  tier-2 site count dropping is the most legible single proof that LOOP-02's removals actually
  happened. Record the before/after counts in the phase record.

- **The honest test to write against:** a reader holding gh#15, its posted correction, Phase 140's
  table and this loop should be able to say, for any byte, exactly how many pulses it will get, of
  what width, when it stops, and which limit stopped it — without reading the source. Anything in the
  loop that cannot be stated that plainly is a design smell, not just an implementation detail.

- **Do not let "hard-fails the block" quietly become "hard-fails the write".** LOOP-05 says the write
  aborts; `eprom_write_execute` operates on one 512/1024-byte block and the host streams the rest.
  Be explicit in the record about what the firmware does with the remaining blocks and what the host
  observes — Phase 143's HOST-03 has to render it.

</specifics>

<deferred>
## Deferred Ideas

- **The shared routing-mask set, `eprom_check_vpp()`'s duplicated branch (`eprom.cpp:218`), and the
  disable-every-route-on-every-exit guarantee** — VPP-01…04, **Phase 142**. This phase satisfies
  LOOP-05's own exit; it does not generalize.
- **Choosing the DIP32 route (P1 vs drop resistor) and consolidating the masks** — Phase 142, handed
  D-09's finding.
- **`--pulse-us` bounds, pre-validation, host timeout, host progress rendering, and surfacing the two
  new message IDs as user-facing program failures** — HOST-01…05, **Phase 143**. D-03's refusal is
  the firmware-side backstop, not the host-side validation.
- **Possible firmware chunking / intra-block progress emission for HOST-02** — Phase 143, flagged by
  D-12 as possibly landing in `firestarter/` despite the roadmap's "different repo" framing.
- **Freezing the old golden trace, authoring the new one, diffing them, and flipping TEST-01** —
  TEST-01/TEST-06, **Phase 144**. This phase leaves `native_trace_v131` RED by design.
- **The flash/RAM delta reconciliation across Phases 140-143** — TEST-08, Phase 144.
- **Reconciling `PROJECT.md`'s throughput table, C3's "no bare pulse", and F-140-07's wrong
  `100 × 500 µs` justification against what shipped** — CLOSE-04, **Phase 146**. This phase names the
  C3 correction; it edits no published text.
- **A possible `0x07` family split for the 22 Intel-family 1 ms parts** (F-140-05) — Phase 146
  candidate. Forbidden here: a second row keyed on anything but `protocol_id` is a second dispatch key.
- **Fixing F-138-05** (`check_size_baseline.py`'s uncaught `KeyError` on an unknown native env) —
  inherited, accepted, not fixed. Owner `henols`.

### Reviewed Todos (not folded)

- **"Skip VPP error/warning checks when VPP is unused (reads/blank-checks)"**
  (`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`, score 0.6) — reviewed,
  not folded. A VPP-routing behaviour change: Phase 142 territory. Deferred there by both
  `139-CONTEXT.md` and `140-CONTEXT.md`; deferred again here for the same reason.
- **"AT28C256 write-path failure (gh#20)"** (`at28c256-write-path-failure-gh20.md`, score 0.6) —
  protocol `0x0D`, a different family; matched on the bare words "write"/"verify"/"path".
- **"FM1608 byte 0 write never lands — register cache-skip elides all three shift-register strobes"**
  (`fm1608-byte0-write-never-lands-register-cache-elision.md`, score 0.6) — a real write-path defect,
  but on an NVRAM part outside the three 27C protocols, and its fix lives in the register-cache layer.
  **Worth a glance during planning anyway:** register-write elision is the one class of bug this
  phase's native suite is structurally blind to unless `rurp_register_utils.h` is included in the
  stubs.
- **"Add a frame-level deadline to the firmware COBS decoder byte-wait (WR-01)"**
  (`cobs-decoder-framelevel-deadline-wr01.md`, score 0.6) — transport layer, unrelated to the EPROM
  algorithm; matched on "byte"/"phase".
- **"`build_db_diff`'s `ladder_state` no longer reaches `community-reported`"**, **"Fix JP4 labels +
  Rev-2 revision block"**, **"Fold response_code into the handler-layer log macro"** (all score 0.6)
  — bare-word matches; none touches this phase.

</deferred>

---

*Phase: 141-Per-Byte Program Loop*
*Context gathered: 2026-08-10*
