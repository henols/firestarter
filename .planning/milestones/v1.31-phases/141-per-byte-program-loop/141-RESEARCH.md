# Phase 141: Per-Byte Program Loop - Research

**Researched:** 2026-08-10
**Domain:** AVR firmware — 27C EPROM per-byte program/verify loop; PROGMEM parameter-table consumption; tri-repo message catalog; native (host) Unity test architecture
**Confidence:** HIGH (every claim below is read from the live working tree at firmware `e2e25b5`, meta `3345eed5`, or measured this session)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

Copied from `.planning/phases/141-per-byte-program-loop/141-CONTEXT.md`. **The planner MUST honor
these.** The operator recorded explicitly that the four structural gray areas are "decided here, not
deferred — research and planning must treat them as settled and not re-open them with the operator."
Nothing in this research re-litigates a D-NN; where research corrects a *supporting premise*, the
decision itself is preserved and the correction is labelled as such.

### Locked Decisions

- **D-01: When the next full-width pulse would cross the 50 ms cap, the loop EMITS that pulse, then
  stops.** Overshoot is bounded by exactly one pulse width. Chosen over stop-before-overshoot (which
  leaves the tail of the budget unused) and over truncating the final pulse (which would emit a pulse
  of a different width than every other pulse and muddy LOOP-01's fixed-width guarantee and the golden
  trace).
  **Consequence the planner must carry:** with `--pulse-us` at its uint16 ceiling the effective
  per-byte ceiling becomes `50000 + 65535 ≈ 115 ms`, not 50 ms. D-03's pre-flight refusal is what
  keeps that bounded in the pathological direction; the one-pulse overshoot is accepted deliberately.
  With every *shipped* database width the cap divides evenly (500 µs → 100 pulses, 1000 → 50,
  200 → 250), so this rule is only reachable via `--pulse-us`.

- **D-02: The accumulated total counts PULSE WIDTHS ONLY — `accumulated = N × pulse_delay`.**
  (Operator delegated: "you decide".) It is the datasheet's own meaning of `t_w(PR)` — time VPE is
  actually applied through CE — and it is the only variant a native test can assert, since the native
  stubs record no time at all (`delay()` is unstubbed, so a wall-clock rule would be untestable
  off-hardware). Explicitly **not** counted: `memory_set_data`'s 3 µs pre-pulse settle, the verify
  read's strobe, and address-setup time. A verify read is not programming.
  *Rejected:* wall-clock elapsed (non-deterministic pulse counts, untestable natively); pulse + 3 µs
  overhead (makes the expected pulse count depend on a constant buried in `memory.cpp`, for ~0.6% of
  the budget at 500 µs).

- **D-03: A pulse wider than the row's energy cap is REFUSED pre-flight, before any high voltage is
  enabled.** In `configure_eprom`, when `energy_cap_us > 0 && pulse_delay > energy_cap_us`, fail
  closed with a named error. Without this, D-01's rule would apply a single up-to-65 ms VPE pulse to
  real silicon and then report a *verify* failure — a misconfiguration wearing a silicon-failure
  costume. This is also the firmware-side backstop for Phase 143's `--pulse-us` bounds, independent of
  host validation.
  *Rejected:* accepting the uniform rule (smallest flash, but applies HV before failing and produces a
  misleading diagnostic); silently clamping the pulse to the cap (a silent substitution — the emitted
  width would no longer match what the user asked for or what the trace claims).

- **D-04: The two budget limits get DISTINCT message IDs — `max_pulses` exhaustion and energy-cap
  exhaustion are separately named on the wire.** (Phase 140 D-07 requires the error to report which
  limit tripped; this decides how.) Authored in **meta's `tools/catalog/messages.toml`**, synced with
  `tools/catalog/sync_to_subrepos.sh` and regenerated in **both** sub-repos so the generated files
  match. Phase 141 stops there — Phase 143's HOST-03 owns turning an ID into a user-facing program
  failure.
  **Cost correction, recorded because the discussion carried the wrong figure at first:**
  `messages.h` is **ID-only `#define`s** (`MSG_ERR_WRITE_FAILED 0xB1`); the wording lives host-side.
  Two new IDs cost the extra call sites, **not** two PROGMEM strings. The option was chosen under a
  materially overstated flash cost, and the real cost is lower.
  **Never hand-edit generated output:** `codegen.py` emits ruff-clean, format-stable `messages.py`; do
  not normalize it. The new IDs are in scope for Phase 144 / TEST-04's cross-repo constants parity leg.
  *Rejected:* one message + a reason discriminator byte (a reason byte is invisible in the host's
  message table and needs a second decode layer); no discriminator (the host holds no copy of the
  table, so it cannot tell 255 pulses-by-count from 250 pulses-by-energy apart).

### Claude's Discretion

The operator answered **"[No preference]"** to the four structural gray areas and delegated D-02.
These are **decided, not deferred** — treat them as settled and do not re-open them with the operator.

- **D-05: The loop reuses `handle->firestarter_set_data` / `handle->firestarter_get_data` as its pulse
  and verify primitives — no EPROM-local duplicate write path is written.** A duplicate would bypass
  `mem_util_remap_address_bus` (the per-chip bus config), which is a correctness hazard, and would cost
  more flash than LOOP-02's removals free. Reusing them also keeps Phase 144 / TEST-06's trace diff
  attributable to *cadence* changes rather than to a new primitive emitting different register writes.

- **D-06: LOOP-07's safe delay helper is applied at BOTH `delayMicroseconds(handle->pulse_delay)`
  sites, and it lives beside `mem_util_*` (`memory_utils.h` / `memory.cpp`), not in `eprom.cpp`.**
  LOOP-07's claim is global ("no call path can reach `delayMicroseconds()` above 16383 µs"), and the
  full site inventory is exactly two: `memory.cpp:329` (`memory_set_data` — the pulse, reached by every
  protocol) and `eprom.cpp:283` (the erase pulse). Every other `delayMicroseconds()` call in the tree
  takes a compile-time constant (1/3/4/10) or an already-clamped read-timing value (`memory.cpp:225`/
  `:235`, capped at 1000 µs at parse time). Fixing `memory_set_data` alone would leave the erase pulse
  unsafe and LOOP-07 false.
  **Structure it as a pure split + the delay calls** so the ms/µs split is unit-testable.

- **D-07: The overprogram pulse is expressed by save/restore of `handle->pulse_delay` around a single
  `firestarter_set_data` call — the existing `org_delay` idiom (`eprom.cpp:161,172`), not a new width
  parameter.** Adding a width argument to the primitive would change every call site's signature across
  every protocol handler — a large diff to serve a path unreachable with shipped data (see D-08).

- **D-08: LOOP-03 is proven through a PURE FUNCTION, not through the table.** Phase 140 shipped
  `overprogram_factor = 0` on **all three rows** (140-PARAM-TABLE-RECORD §§3-4), so no live row can
  exercise the overprogram path. Extract the duration as a pure
  `(pulse_count, pulse_us, factor, cap_us) → us` function and test it directly at `factor = 3`,
  including the clamp at `overprogram_cap_us` and 32-bit overflow safety at `3 × 25 × 65535`.
  Separately assert that all three **live** rows emit zero extra pulses.
  **State the non-claim plainly in the phase record:** the end-to-end overprogram path is proven only
  in its arithmetic and its gating, never in the loop. Hand that to Phase 146 alongside F-140-05.
  *Rejected:* a test-only injection seam (`#ifdef`/weak symbol) into the production table; shipping it
  untested (TEST-01 asks for proof).

- **D-09: LOOP-08's DIP32 clause is discharged by an explicit guarded path plus a test — the ROUTE
  choice stays Phase 142's.** `mem_util_calculate_top_address_register` (`memory.cpp:159-173`) adds
  `CTRL_VPP_VPE_DROP_ENABLE` to the preserved mask **only when `pins < 32`**; on a 32-pin part that bit
  *is* A16 and is driven by the address, so the drop path cannot be held across a block. `0x08` is
  `PROTO_EPROM_32PIN` *and* ships `vpp_path = VPP_PATH_DROP_RESISTOR`, so this is the row where the
  collision actually bites. The existing mechanism is `eprom_internal_set_control_register`'s
  `using_p1_as_vpp()` remap (`eprom.cpp:320`, `memory_utils.h:24`).
  **Phase 141's obligation:** the loop must not silently depend on the drop bit surviving `set_address`
  on `pins >= 32`; the DIP32 case is a named, commented branch, and a native test asserts the emitted
  CONTROL writes across a block that crosses an A16 boundary on a 32-pin part. Consolidating the masks
  and picking the final route is VPP-01/VPP-03, Phase 142.
  > **Research note (mechanism corrected, decision and obligation intact):** on every *shipped* build
  > the two bits are **distinct** (`CTRL_ADDRESS_LINE_16 = 0x01`, `CTRL_VPP_VPE_DROP_ENABLE = 0x100`).
  > The drop route still fails to survive `set_address` on `pins >= 32`, via the preserve-mask guard
  > rather than a bit collision. See §"DIP32 / A16 truth table". D-09's obligation is unchanged and is
  > now better grounded; the guarded branch should key on `handle->pins >= 32`, not on `protocol`.

- **D-10: `native_trace_v131` goes RED in this phase and is NOT re-frozen here.** Phase 140's D-10 kept
  it GREEN deliberately so the first legitimate trace movement would be this phase's; a fixture
  re-frozen by the phase that breaks it stops being evidence. Phase 141 (a) captures the new trace as a
  committed artifact so Phase 144 / TEST-06 has both sides, and (b) names the RED explicitly in its
  record so no reader mistakes it for a regression.
  **Because that fixture cannot verify this phase, Phase 141 authors its own native suite** — a
  **sixth** env on the `native_params_v131` precedent: it names only its own suite in `test_filter`, is
  never folded into `native` / `native_nodevtools` (both pinned at exactly 141 cases / 17 suites by the
  live `size_baseline.json`), is never in `default_envs`, and is never passed to
  `check_size_baseline.py` (unknown env → uncaught `KeyError`, exit 1 — F-138-05) or
  `check_build_warnings.py` (exit 2). It runs in **no CI leg of either repo** — a run-by-name
  obligation recorded in the phase record, never implied as CI coverage.
  **Seam with Phase 144:** TEST-01 owns the requirement flip and the consolidated accounting; this
  phase's suite is its *own* verification. Record it so Phase 144 does not double-author.

- **D-11: The D-13 protocol-branch-inventory gate WILL go RED, and must be re-derived by its own
  scanner — never hand-edited.** `firestarter/tests/test_protocol_branch_inventory.py` +
  `tests/golden/protocol_branch_inventory.json` pin 3 tier-1 (protocol-keyed) and 21 tier-2
  (handle-field-keyed) predicate sites in `eprom.cpp` (F-140-10 corrected the count from the 3 the
  research pass predicted). Rewriting the write path moves the tier-2 inventory. **Record the shrinkage
  as evidence of LOOP-02's removals.** The loop must add **no new tier-1 site**: it reads the table,
  and D-03's pre-flight refusal is keyed on `energy_cap_us`, not on `protocol`.

- **D-12: Phase 141 adds NO chunking and NO progress emission — but must not structurally preclude
  them.** HOST-01/02 are Phase 143's. Keep the loop shaped so it can later adopt
  `mem_util_blank_check`'s operation-in-progress + `progress_data` pattern without another rewrite.
  **Finding to hand forward:** the roadmap calls Phase 143 "independent of 140–142 (different repo)",
  yet HOST-02's own named precedent is a **firmware** pattern. If HOST-02 needs intra-block emission,
  part of Phase 143 lands in `firestarter/`. Name this before Phase 143 plans, not after.

- **Free within the above:** the loop's exact function decomposition and naming; `uint8_t` vs
  `uint16_t` for the per-byte pulse counter (`max_pulses` is `uint8_t`; `0x0B` ships 255); the pure
  helper's signatures; the sixth env's name and its `test_filter` / `-I` entries; plan and wave
  structure.

### Deferred Ideas (OUT OF SCOPE)

- **The shared routing-mask set, `eprom_check_vpp()`'s duplicated branch (`eprom.cpp:218`), and the
  disable-every-route-on-every-exit guarantee** — VPP-01…04, **Phase 142**. This phase satisfies
  LOOP-05's own exit; it does not generalize.
- **Choosing the DIP32 route (P1 vs drop resistor) and consolidating the masks** — Phase 142, handed
  D-09's finding.
- **`--pulse-us` bounds, pre-validation, host timeout, host progress rendering, and surfacing the two
  new message IDs as user-facing program failures** — HOST-01…05, **Phase 143**.
- **Possible firmware chunking / intra-block progress emission for HOST-02** — Phase 143.
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

### Also out of scope (CONTEXT.md `<domain>` "Not in this phase")

- VPP/VPE routing consolidation and disable-on-every-exit *as a general guarantee* — Phase 142.
- `--pulse-us`, host timeout, host progress rendering, user-facing program failures — Phase 143.
- Golden-trace freezing/authoring/diffing; flash/RAM delta reconciliation; the TEST-01 flip — Phase 144.
- Any `chip_database.json` change, any new database field, any second firmware dispatch selector.
  `protocol_id` remains the sole dispatch key (TABLE-05, still binding).

### Reviewed Todos (not folded — do not fold them here either)

`skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads` (Phase 142 territory),
`at28c256-write-path-failure-gh20` (protocol `0x0D`), `cobs-decoder-framelevel-deadline-wr01`
(transport layer), `build_db_diff ladder_state`, `JP4 labels + Rev-2 revision block`,
`response_code into the handler-layer log macro` — all bare-word matches, none touches this phase.

**One exception worth a glance during planning:**
`fm1608-byte0-write-never-lands-register-cache-elision` — a real write-path defect on an NVRAM part
outside the three 27C protocols, whose fix lives in the register-cache layer. **Register-write elision
is the one bug class this phase's native suite is structurally blind to unless
`rurp_register_utils.h` is included in the stubs** — and §"Native test architecture" shows the
`HOST_STUBS_REAL_REGISTER_UTILS` guard that closes exactly that blind spot.
</user_constraints>

<phase_requirements>
## Phase Requirements

Verbatim from `.planning/REQUIREMENTS.md:181-201` (§"Per-Byte Program Loop"); all eight are `[ ]`
Pending, and the coverage table at `:309-316` maps each to Phase 141.

| ID | Requirement (abridged — full text at `REQUIREMENTS.md:183-201`) | Research Support |
|----|------------------------------------------------------------------|------------------|
| **LOOP-01** | Fixed-width pulses, verify after each, count the pulses that byte required; width does not grow | §"Per-byte loop shape" fixes the predicate order; primitives at `memory.cpp:321`/`:203` (D-05). Pulse-count oracle: `trace_readback_seed(idx, target, converge_after)` (`test_trace_eprom_v131/host_stubs.cpp:137`) |
| **LOOP-02** | Remove `program_mismatched_bytes()`, `verify_and_update_mask()`, the flat `NUMBER_OF_RETRIES` block loop, and the adaptive growth | Removal targets confirmed at `eprom.cpp:20`, `:114-126`, `:129-141`, `:163-179`, `:177`. RAM donor: `mismatch_bitmask[DATA_BUFFER_SIZE/8]` at `:155`. Two catalog IDs orphan — see §"Orphaned catalog IDs" |
| **LOOP-03** | `overprogram_factor > 0` → one `3 × N × pulse` pulse, capped at `overprogram_cap_us` | Unreachable with shipped data: `overprogram_factor = 0` on all three rows, **read from source** (`eprom_params.cpp:46-48`). §"Overprogram arithmetic" gives the boundary values incl. `3 × 25 × 65535 = 4,915,125` and the clamp at `75000` |
| **LOOP-04** | `0x0B` accumulated program time per byte capped at 50 ms, no overprogram | `0x0B` ships `energy_cap_us = 50000`, `max_pulses = 255`, `overprogram_factor = 0` (`eprom_params.cpp:48`). §"Energy-cap arithmetic" derives the exact predicate that makes D-01's own worked example true, and states the honest worst case |
| **LOOP-05** | Miss within `max_pulses` → hard-fail the block, disable every HV route, report address + pulse count | §"What 'hard-fails the block' actually does" traces the abort `eprom_operations.cpp:115-117` → `operation_utils.cpp:186-191` → `command_done()` (`firestarter.cpp:162-171`). Free ID slots: `0xBD`/`0xBE`. **Vacuity trap named** — `command_done()` zeroes the control register regardless |
| **LOOP-06** | Already-matching and `0xFF` bytes skipped with no pulse | `data_buffer` is `char[]` (`firestarter.h:202`) so the `(uint8_t)` cast at `eprom.cpp:132` is required. The existing trace fixture's block `{0x3C, 0xFF, 0x55, 0xAA}` already contains a `0xFF` byte |
| **LOOP-07** | Safe 32-bit ms/µs-splitting helper; no path reaches `delayMicroseconds()` above 16383 µs | **Complete inventory established** (§"delayMicroseconds call-site inventory"): 12 direct sites + 1 macro indirection, exactly 2 over-ceiling-capable — **D-06 CONFIRMED**. The 16383 boundary verified in `framework-arduino-avr/cores/arduino/wiring.c:167-183`. Native oracle: `HOST_STUBS_RECORD_TIMING` records the argument |
| **LOOP-08** | VPE asserted+settled once per block, survives the verify read; DIP32 exception explicit | §"LOOP-08 mechanics" + §"DIP32 / A16 truth table" replace the false "a verify read does not disturb the control register" premise with the real mechanism (preserve mask `memory.cpp:161` + cache elision `rurp_register_utils.h:38-41`) and scope the DIP32 problem to `pins >= 32` — protocol `0x08` alone among the three rows |
</phase_requirements>

## Summary

CONTEXT.md's D-01…D-12 are locked and this research does not re-open any of them. What it does is make
them *plannable*: it verifies all ~40 `file:line` citations against the live tree (**37 correct, 1
materially stale, 2 imprecise**), establishes the complete `delayMicroseconds()` call-site inventory
(**D-06's "exactly two over-ceiling-capable sites" is CONFIRMED**), reads the shipped parameter-table
values from source (**CONTEXT.md's assertions are CONFIRMED, plus one column — `verify_mode` — that no
decision covers**), and resolves the flash-headroom conflict by **building all three AVR targets this
session** (the 42 B / 36 B / 56 B budget applies, not F-138-02's 8 B / 2 B).

Three findings change how the phase must be planned, none of which contradicts a locked decision:

1. **D-09's stated mechanism is wrong; its conclusion is right.** On every shipped build
   (`-D HARDWARE_REVISION` is inherited by all six envs) `CTRL_ADDRESS_LINE_16` is `0x01` and
   `CTRL_VPP_VPE_DROP_ENABLE` is `0x100` — **distinct bits, no collision**. The drop route nonetheless
   fails to survive `set_address` on `pins >= 32`, because the `pins < 32` guard at `memory.cpp:162`
   excludes the bit from the *preserve mask* regardless of board revision. The collision is real only
   on legacy non-`HARDWARE_REVISION` builds (macro alias) and, physically, on Rev 0/Rev 1 boards (both
   map to physical `0x01`). §"DIP32 / A16 truth table" gives the source-verified version.
2. **The D-13 gate cannot be discharged by re-deriving the golden alone.**
   `test_protocol_branch_inventory.py:446` hard-codes `protocol_lines == [71, 145, 218]` **in the test
   module**, not in the JSON. And `pytest tests/ -v` **runs in CI** (`build.yml:161`,
   `beta-build.yml:134`) — so this gate going RED is a **CI failure**, not a local-only one.
3. **The pulse-width truncation hazard is live today, not gated on Phase 143.** `pulse-delay` is parsed
   with `extract_long` into a `uint32_t` with **no clamp at all** (`json_parser.c:503`), while AVR's
   `delayMicroseconds` takes a 16-bit `unsigned int` and overflows its `us <<= 2` at 16384. LOOP-07's
   helper closes a *currently reachable* wire-level defect; it is not merely pre-positioning for
   `--pulse-us`.

**Primary recommendation:** Rewrite `eprom_write_execute` as a per-byte loop that reads all six table
columns through `pgm_read_byte`/`pgm_read_dword`, keeps the `:145` `protocol == 0x0B` VPP predicate
verbatim (only its line moves — Phase 142 owns replacing it), puts the delay helper in
`memory_utils.h`/`memory.cpp` so **no new TU** is created (which would trip the CI-covered CMake
manifest gate), and budgets against 42 B (`uno`) / 36 B (`uno328pb`) / 56 B (`leonardo`) of measured
flash headroom with RAM delta exactly 0.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Per-byte pulse→verify cadence | Firmware — `src/proms/eprom.cpp` | — | The loop must run between two bus operations with µs-scale timing; no host round-trip can sit inside it |
| Pulse and verify primitives | Firmware — `src/proms/memory.cpp` (`memory_set_data` / `memory_get_data`) | — | D-05: already the only code that owns `mem_util_remap_address_bus`; duplicating it would bypass per-chip bus config |
| Algorithm *shape* (max_pulses, overprogram, energy cap, verify mode, vpp path) | Firmware — `src/proms/eprom_params.cpp` PROGMEM table | — | Milestone D-01: protocol owns shape. `protocol_id` is the sole key (TABLE-05) |
| Pulse *width* | Host database → wire `pulse-delay` → `handle->pulse_delay` | Firmware fallback switch (`eprom.cpp:70-76`) | Milestone D-01: database owns the pulse. Fallback is unreachable on all 329 shipped chips (F-140-04) |
| 32-bit-safe long delay | Firmware — `memory_utils.h` / `memory.cpp` | — | D-06. Placement inside an existing TU avoids the CMake manifest gate; AVR-only concern (ARM shim is already `uint32_t`) |
| Budget-exhaustion diagnosis (which limit tripped) | Meta `tools/catalog/messages.toml` → generated `messages.h` + `messages.py` | — | D-04. IDs are authored once and synced; the host holds no copy of the table so it cannot infer the reason |
| Rendering a budget failure to the user | Host — `firestarter_app/` | — | **Phase 143 / HOST-03.** Out of scope here; Phase 141 only emits the IDs |
| High-voltage route selection from `vpp_path` | Firmware — `eprom.cpp` | — | **Phase 142 / VPP-01.** Phase 141 keeps the existing `protocol == 0x0B` predicate untouched |
| Pre-flight configuration refusal | Firmware — `configure_eprom` (`eprom.cpp:41-77`) | — | D-03. The single place that runs before any hardware is touched |

---

## Citation Audit — CONTEXT.md against the live tree

Firmware HEAD `e2e25b5a7cfd09cefb349827fb97ceba96e60ac7`, branch `gsd/v1.31-27c-programming-algorithm-fidelity`.

### `firestarter/src/proms/eprom.cpp` (332 lines) — all CONFIRMED

| CONTEXT.md citation | Live | Verdict |
|---|---|---|
| `:20` `NUMBER_OF_RETRIES` | `:20` `#define NUMBER_OF_RETRIES 20` | ✅ exact |
| `:114-126` `program_mismatched_bytes()` | `:114-126` (signature `:114`, body `:115-125`, close `:126`) | ✅ exact |
| `:129-141` `verify_and_update_mask()` | `:129-141` | ✅ exact |
| `:143-193` `eprom_write_execute` | `:143-193` | ✅ exact |
| `:177` adaptive growth formula | `:177` `handle->pulse_delay = org_delay + (org_delay * retries / NUMBER_OF_RETRIES);` | ✅ exact |
| `:181` single-route disable | `:181` `set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 0)` | ✅ exact |
| `:182-191` failure report | `:182-191` (`_b[6]` block ending `LOG_ERROR_ID_BYTES(MSG_ERR_WRITE_FAILED, _b, 6)` at `:190`) | ✅ exact |
| `:41-77` `configure_eprom` | `:41-77` | ✅ exact |
| `:70-76` fallback switch (stays) | `:70-76` (`if (pulse_delay == 0)` at `:70`, `switch` at `:71`, arms `:72-74`) | ✅ exact |
| `:161,172` `org_delay` save/restore | `:161` `uint32_t org_delay = handle->pulse_delay;` / `:172` `handle->pulse_delay = org_delay;` | ✅ exact |
| `:283` the erase pulse | `:283` `delayMicroseconds(handle->pulse_delay);` inside `eprom_internal_erase` | ✅ exact |
| `:320` `using_p1_as_vpp` remap | `:319` function signature, `:320` `if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle))` | ✅ exact |
| `:218` `eprom_check_vpp`'s duplicated branch | `:218` is the duplicated `protocol == 0x0B \|\| is_flag_set(FLAG_VPE_AS_VPP)` predicate. The **function** starts at `:209` | ⚠️ imprecise in `<canonical_refs>` (which reads "`:218` `eprom_check_vpp`"); exactly right in `<deferred>` |

**Undocumented function the phase should know about:** `eprom_internal_ensure_regulator_enabled`
(`eprom.cpp:327-332`) is **dead code** — grep across `src/`, `include/`, `test/`, `tests/` finds zero
callers. It is nonetheless an almost-exact template for LOOP-08's once-per-block assert-and-settle
(`if (get_control_register(REGULATOR) == 0) { set(REGULATOR,1); delay(500); }`), and
`eprom_write_execute:144-153` inlines a near-duplicate of it. The D-13 golden JSON pins its predicate
at `:328` with a `reason` claiming it is "used by callers outside the write path" — **that reason is
factually false** and must be corrected when the golden is re-derived. Because AVR builds use
`-ffunction-sections` + `-Wl,--gc-sections` (verified in
`~/.platformio/platforms/atmelavr/builder/frameworks/arduino.py:98,111`), it currently contributes
~0 B; do **not** count deleting it as reclaimed flash.

### `firestarter/src/proms/memory.cpp` (390 lines) — one STALE citation

| CONTEXT.md citation | Live | Verdict |
|---|---|---|
| `:249-258` `memory_set_data` (the pulse) | `:249-259` (signature `:249`, body `:250-258`, close `:259`) | ✅ substantively exact |
| `:257` the pulse `delayMicroseconds` | `:257` `delayMicroseconds(handle->pulse_delay);` | ✅ exact |
| `:203-241` `memory_get_data` (verify read) | `:203-241` | ✅ exact |
| `:159-173` `mem_util_calculate_top_address_register` | `:159-173`; `if (handle->pins < 32)` at `:162`, `mask \|= CTRL_VPP_VPE_DROP_ENABLE` at `:165` | ✅ exact |
| `:221` / `:235` clamped read-timing delays | `:221` `delayMicroseconds(settling)` (clamped `>1000UL → 1000UL` at `:220`); `:235` `delayMicroseconds(strobe)` (clamped at `:234`) | ✅ exact |
| **`:307-341` `mem_util_blank_check`** | **`:321-390`.** `:307` is the closing brace of `mem_util_remap_address_bus`. Supporting parts: `blank_check_progress_data_t` `:309-311`, `BLANK_CHECK_CHUNK_SIZE 2048` `:313`, `uint32_to_bytes` `:314-319` | ❌ **STALE — off by ~14 lines and truncated.** Use `:321-390`; the in-progress init is `:322-338`, the chunk loop `:341-369`, the advance + `MSG_DATA_PROGRESS` emit `:370-389` |
| `:115` `configure_eprom` dispatch | `:115` is the `if`, `:116` the call | ✅ substantively exact |

### `firestarter/include/` — CONFIRMED with one framing correction

| CONTEXT.md citation | Live | Verdict |
|---|---|---|
| `rurp_shield.h:108-131` — chip enable/output are dedicated pins | The four `static inline` helpers are `:114-136` (`rurp_set_chip_enable` `:114`, `rurp_chip_enable` `:122`, `rurp_chip_disable` `:126`, `rurp_chip_output` `:130`, `rurp_chip_input` `:134`); the explanatory comment is `:111-113`. All four route to `rurp_set_control_pin(CHIP_ENABLE\|OUTPUT_ENABLE, state)`, which is **not** the shift-register `CONTROL_REGISTER` | ✅ line range exact. ⚠️ **the inference stated on it is wrong** — see below |
| `memory_utils.h:24` — `using_p1_as_vpp()` | `:24-28` | ✅ exact |
| `firestarter.h:194-203` — `mem_size`, `address`, `pulse_delay` (uint32_t), `data_size` | `mem_size` `:194`, `address` `:195`, `pulse_delay` `:197` (`uint32_t` ✓), `data_buffer` `:202` (`char[DATA_BUFFER_SIZE]`), `data_size` `:203` | ✅ exact. Note `data_buffer` is `char`, so byte comparisons need a `(uint8_t)` cast — the idiom already at `eprom.cpp:132` |
| `eprom_params.h` — six columns, two enums, PROGMEM warning | `:41` `VERIFY_PER_PULSE=0 / VERIFY_PER_PULSE_PLUS_FINAL=1`; `:46` `VPP_PATH_DROP_RESISTOR=0 / VPP_PATH_DIRECT_VPE=1`; struct `:51-58`; `static_assert(sizeof == 12)` `:62-65`; accessor + PROGMEM warning `:71-79` | ✅ exact |
| `messages.h:91` `MSG_ERR_VERIFY 0xAF`, `:93` `MSG_ERR_WRITE_FAILED 0xB1` | `:91` and `:93` | ✅ exact |

> **Correction to the LOOP-08 premise as written in `<canonical_refs>`.** CONTEXT.md says
> `rurp_shield.h:108-131` is "the mechanical basis for LOOP-08: a verify read does not disturb the
> control register, so VPE survives it." **A verify read DOES write the control register.**
> `memory_get_data` → `handle->firestarter_set_address` → `mem_util_set_address`
> (`memory.cpp:175-191`) → `mem_util_calculate_top_address_register` → `rurp_write_to_register(CONTROL_REGISTER, top_address)`
> unconditionally, on every single byte, for both the pulse and the verify.
>
> What is true is narrower and still sufficient: (a) `rurp_chip_enable/disable/output/input` are
> dedicated pins and do not touch the control register; and (b) VPE survives because
> `CTRL_VPE_ENABLE` **is in the unconditional preserve mask** at `memory.cpp:161`, and because
> `rurp_write_to_register` **elides the write entirely** when the recomputed value equals the cached
> one (`rurp_register_utils.h:38-41`). Plan and comment against (a)+(b), not against "the control
> register is untouched" — a test written on the false premise would assert zero CONTROL strobes and
> fail for the wrong reason.

---

## Standard Stack

This is an existing embedded C/C++ codebase. **No new external dependency is required or recommended.**
Everything the phase needs is already in the tree or in the installed toolchain.

### Core (all already present)
| Component | Version | Purpose | Why standard |
|-----------|---------|---------|--------------|
| PlatformIO Core | 6.1.19 | build + native test driver | pinned in `size_baseline.json:meta.platformio_core` [VERIFIED: `pio --version`] |
| `platform-atmelavr` | 5.2.0 | AVR toolchain wrapper | pinned in baseline meta [VERIFIED: baseline JSON] |
| `avr-gcc` | 7.3.0 | AVR compiler | `~/.platformio/packages/toolchain-atmelavr/bin/avr-gcc-7.3.0` [VERIFIED: filesystem] |
| `framework-arduino-avr` | 5.3.0 | `delay`/`delayMicroseconds`/PROGMEM | pinned in baseline meta [VERIFIED] |
| Unity (via PlatformIO) | bundled | native test framework | `test_framework = unity` in every native env [VERIFIED: `platformio.ini`] |
| ArduinoFake | `^0.4.0` | host mocks for `delay*`, `Serial` | `lib_deps` in all five native envs [VERIFIED: `platformio.ini:143,289,327,369`] |
| Python | 3.12.13 | gate/checker suite | devcontainer interpreter [VERIFIED: `python3 --version`] |
| pytest | 9.1.1 | firmware gate suite (`tests/`) | [VERIFIED: `pytest --version`] |

### Supporting (in-tree assets to reuse, not rebuild)
| Asset | Location | Purpose | When to use |
|-------|----------|---------|-------------|
| `eprom_params_for()` | `src/proms/eprom_params.cpp:51-58` | PROGMEM row lookup, NULL on no match | The loop's single table entry point (first `src/` caller) |
| `memory_set_data` / `memory_get_data` | `memory.cpp:321`, `:203` | the pulse / the verify read | D-05: reach both via `handle->firestarter_set_data` / `_get_data` |
| `org_delay` save/restore idiom | `eprom.cpp:161,172` | emit a non-default pulse width | D-07: the overprogram pulse |
| `HOST_STUBS_REAL_REGISTER_UTILS` | `_shared/host_stubs_common.inc:96-134` | opt-in ordered strobe recorder; compiles against the **real** `rurp_register_utils.h` so cache-elision is exercised | The new suite's register-write oracle |
| `HOST_STUBS_RECORD_TIMING` | `_shared/host_stubs_common.inc:136-197` | opt-in `(kind, us, seq)` recorder | **The LOOP-07 oracle** — records the *argument* of every `delay`/`delayMicroseconds` call |
| `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` + `trace_readback_seed(idx, target, converge_after)` | `test_trace_eprom_v131/host_stubs.cpp:122-149` | stateful chip read-back model so a program/verify loop converges | **The pulse-count oracle** — seed `converge_after=N` and assert N pulses |
| `EPROM_V131_TRACE_DUMP` dump harness | `test_trace_eprom_v131.cpp:348-378` | prints ready-to-paste trace initialisers | **D-10's "capture the new trace as a committed artifact"** |
| `[env:native_params_v131]` | `platformio.ini:331-371` | complete worked single-suite env with the HARD CONSTRAINT comment block | D-10's sixth env template |
| `_extract_predicates()` | `tests/test_protocol_branch_inventory.py:277-368` | the ONLY re-derivation path for the D-13 golden | D-11's re-derivation |

**Installation:** none. Every dependency is already resolved in `.pio/libdeps/{native,native_nodevtools,native_params_v131,native_pinmap_provisional,native_trace_v131}/`.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Helper in `memory_utils.h`/`memory.cpp` (D-06) | a new `src/proms/delay_utils.cpp` | **Rejected by consequence, not taste:** any new source under `src/` must be added to `platform/py32f071/CMakeLists.txt`'s `FIRESTARTER_COMMON_SOURCES` or allow-listed with a reasoned `# PY32_EXCLUDED:` comment, and `tests/test_check_cmake_manifest.py::test_armed_and_passing_on_the_real_tree` invokes that checker **against the real tree** inside the CI-run `pytest tests/ -v`. D-06's placement sidesteps a CI-visible gate |
| Reuse `MSG_ERR_WRITE_FAILED 0xB1` with new semantics | two new IDs (D-04) | Locked. Note `0xB1`'s existing shape is `[u24 hex_addr, u8, u16]` = 6 bytes and is asserted verbatim by `test_messages/test_rurp_log_id.cpp:147-176` — but that test calls `rurp_log_id(0xB1, …)` directly with a literal, so it is **unaffected** by the loop rewrite |

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external package in any of the three repositories.**

The full dependency set is already vendored or pinned: `ArduinoFake@^0.4.0` (pre-existing `lib_deps`
in five native envs, resolved in `.pio/libdeps/`), the PlatformIO-managed `atmelavr` toolchain, and
stdlib-only Python for the gate suite. No `npm install`, `pip install`, or `cargo add` appears anywhere
in the phase's scope. `slopcheck` was therefore not run, and there is no package for the planner to
gate behind a `checkpoint:human-verify`.

If a plan later proposes a new dependency, it is out of scope per CONTEXT.md `<domain>` and should be
refused rather than audited.

---

## Shipped parameter table — read from source

`firestarter/src/proms/eprom_params.cpp:45-49`. Column order is largest-first so `sizeof == 12` on
both AVR (1-byte alignment) and a 64-bit host (`eprom_params.h:62-65` `static_assert`).

| protocol | `overprogram_cap_us` | `energy_cap_us` | `max_pulses` | `overprogram_factor` | `verify_mode` | `vpp_path` |
|---|---|---|---|---|---|---|
| `0x07` `PROTO_EPROM_28PIN` | `75000` | `0` (uncapped) | `25` | **`0`** | `VERIFY_PER_PULSE_PLUS_FINAL` (1) | `VPP_PATH_DROP_RESISTOR` (0) |
| `0x08` `PROTO_EPROM_32PIN` | `75000` | `0` (uncapped) | `25` | **`0`** | `VERIFY_PER_PULSE_PLUS_FINAL` (1) | `VPP_PATH_DROP_RESISTOR` (0) |
| `0x0B` `PROTO_EPROM_24PIN` | `75000` | **`50000`** | `255` | **`0`** | `VERIFY_PER_PULSE` (0) | `VPP_PATH_DIRECT_VPE` (1) |

**CONTEXT.md's two assertions about this table are CONFIRMED** [VERIFIED: `eprom_params.cpp:46-48`]:
`overprogram_factor = 0` on all three rows, and `overprogram_cap_us` is therefore inert everywhere
(the clamp `min(3 × N × pulse, cap)` evaluates to `0` on every live row).

Keys are `{0x07, 0x08, 0x0B}` in a positionally parallel `EPROM_PARAM_KEYS[] PROGMEM`
(`eprom_params.cpp:22`); `eprom_params_for()` is a **linear scan**, never a switch (a switch here would
itself be the second dispatch selector TABLE-05 forbids), and returns `NULL` on no match — never
`&EPROM_PARAMS[0]` (`:55-62`, D-05 fail-closed).

### ⚠️ Gap: `verify_mode` is a column no decision covers

`verify_mode` ships **`VERIFY_PER_PULSE_PLUS_FINAL` on `0x07`/`0x08`** and `VERIFY_PER_PULSE` on
`0x0B`. CONTEXT.md's D-01…D-12 cover `max_pulses` (LOOP-05), `energy_cap_us` (LOOP-04/D-01/D-02/D-03),
`overprogram_factor` + `overprogram_cap_us` (LOOP-03/D-07/D-08) and defer `vpp_path` to Phase 142 —
but **never mention `verify_mode`**. `firestarter/CLAUDE.md`'s Algorithm Handlers table already
*documents* the behaviour it encodes: `0x07`/`0x08` do "verify per pulse **+ 1 final full-array pass**",
`0x0B` does "verify per pulse, **no final full-array pass**".

This is a genuine planning decision the planner must make (and record), not an operator question:
LOOP-01 requires per-pulse verify unconditionally, and the *only* behaviour `verify_mode` adds is the
final full-array pass on the two `PLUS_FINAL` rows. Three defensible dispositions, in preference order:

1. **Consume it** — after the per-byte loop completes, if `verify_mode == VERIFY_PER_PULSE_PLUS_FINAL`,
   run one more full-block read-and-compare pass. This is the only option that makes CLAUDE.md's
   documented behaviour true, and it costs a small loop the removed `verify_and_update_mask` already
   funds. Note the pre-change loop's *last* action was always a full verify pass, so this preserves an
   existing property rather than adding one.
2. **Read it and assert it, without acting on it** — smallest diff, but leaves CLAUDE.md's row wrong
   and leaves a shipped column with no consumer, which is the exact "looks load-bearing but isn't"
   problem 140-PARAM-TABLE-RECORD §5 went out of its way to avoid for `overprogram_cap_us`.
3. **Defer to Phase 142/144 explicitly in the phase record.** Acceptable only if named — silence here
   reads as an oversight.

**Recommendation: option 1**, with the final pass emitting `MSG_ERR_VERIFY` (`0xAF`) on mismatch —
which is what `memory_verify_execute` (`memory.cpp:333-353`) already does and is a shape the host
already renders. Whatever is chosen, `firestarter/CLAUDE.md`'s three Algorithm Handlers rows must end
the phase consistent with what shipped (CONTEXT.md `<canonical_refs>` already requires this).

### PROGMEM accessor pattern — the exact idiom to copy

Phase 140's own test proves the pattern; `src/` call sites must use the identical form
[VERIFIED: `test_eprom_params_v131/test_eprom_params_v131.cpp:176-184`]:

```c
const eprom_params_t* row = eprom_params_for(handle->protocol);
if (row == NULL) { /* fail closed, zero hardware side effects — Phase 140 D-05 */ }

uint32_t overprogram_cap_us = pgm_read_dword(&row->overprogram_cap_us);
uint32_t energy_cap_us      = pgm_read_dword(&row->energy_cap_us);
uint8_t  max_pulses         = pgm_read_byte(&row->max_pulses);
uint8_t  overprogram_factor = pgm_read_byte(&row->overprogram_factor);
uint8_t  verify_mode        = pgm_read_byte(&row->verify_mode);
uint8_t  vpp_path           = pgm_read_byte(&row->vpp_path);
```

`pgm_read_dword` for the two `uint32_t` columns, `pgm_read_byte` for the four `uint8_t` columns. A
direct `row->max_pulses` **compiles cleanly and silently returns RAM garbage on AVR** while working
perfectly on the native host — so a native-only test cannot catch this class of bug. The macros are
supplied by `rurp_platform_compat.h:19-49`, which maps them to `<avr/pgmspace.h>` on AVR and to plain
dereferences elsewhere.

**Flash-cost note:** hoist the six reads **out** of the per-byte loop into locals before the loop
starts. On AVR each `pgm_read_*` is an `LPM` sequence; re-reading six PROGMEM fields per byte across a
512/1024-byte block is both slower and larger than six reads per block. This also makes the loop body
read like the algorithm rather than like table plumbing — which is `<specifics>`'s "honest test to
write against."

---

## `delayMicroseconds()` call-site inventory — LOOP-07's global claim

LOOP-07's claim is **global** ("no call path can reach `delayMicroseconds()` with a value above its
16383 µs ceiling"), so an incomplete inventory makes the requirement false. This is the complete set
across `firestarter/src/`, `firestarter/include/`, `firestarter/lib/` and `firestarter/platform/`
[VERIFIED: `grep -rn "delayMicroseconds" src/ include/ lib/ platform/`].

### Direct call sites (12)

| # | Site | Argument | Provenance | Over-ceiling capable? |
|---|------|----------|-----------|----------------------|
| 1 | `src/proms/memory.cpp:327` | `3` | compile-time literal | No |
| 2 | **`src/proms/memory.cpp:329`** | **`handle->pulse_delay`** | **`uint32_t`, host-supplied, UNCLAMPED** | **YES — D-06 site 1 (the pulse)** |
| 3 | `src/proms/memory.cpp:225` | `settling` | clamped `> 1000UL → 1000UL` at `:220`, and again at parse time (`json_parser.c:47`) | No |
| 4 | `src/proms/memory.cpp:307` | `strobe` | clamped `> 1000UL → 1000UL` at `:234`, and at parse time (`json_parser.c:362`) | No |
| 5 | **`src/proms/eprom.cpp:283`** | **`handle->pulse_delay`** | **`uint32_t`, host-supplied, UNCLAMPED** | **YES — D-06 site 2 (the erase pulse)** |
| 6 | `src/proms/flash_5v_page.cpp:112` | `10` | literal | No |
| 7 | `src/proms/eeprom_28c.cpp:352` | `10` | literal | No |
| 8 | `src/proms/eeprom_28c.cpp:679` | `10` | literal | No |
| 9 | `src/boards/leonardo_rurp_shield.cpp:41` | `1` | literal | No |
| 10 | `src/boards/rurp_serial_utils.cpp:15` | `1` | literal | No |
| 11 | `include/rurp_register_utils.h:58` | `4` | literal (the P1 set→clear settle) | No |
| 12 | `include/rurp_register_utils.h:86` | `1` | literal (post-latch strobe) | No |

### Macro indirection (1) — checked, and it is not a hole

`RURP_DELAY_US(value)` is defined three times in `include/rurp_platform.h`: `:25` (ARM → `rurp_delay_us((uint32_t)value)`),
`:35` (AVR → `delayMicroseconds(value)`), `:44` (native → `delayMicroseconds(value)`). Its **only**
call site in the entire tree is `platform/py32f071/include/Arduino.h:23`, inside the PY32's own
`static inline void delayMicroseconds(uint32_t value)` shim. **No `src/` code calls `RURP_DELAY_US`**,
so on AVR the macro contributes no additional path.

### Verdict

**D-06's claim is CONFIRMED: exactly two over-ceiling-capable sites, `memory.cpp:329` and
`eprom.cpp:283`.** Both take `handle->pulse_delay`; every other site takes a literal or an
already-clamped value. Fixing only `memory_set_data` would leave the erase pulse unsafe and LOOP-07
false, exactly as D-06 states.

### The ceiling, and the failure mode, from the toolchain source

`framework-arduino-avr` 5.3.0, `cores/arduino/wiring.c` [VERIFIED: filesystem read]:

- `:120` — `void delayMicroseconds(unsigned int us)`. **`unsigned int` is 16-bit on AVR**, so any
  `uint32_t` argument above 65535 is truncated by the ABI *before the function body runs*.
- `:167-183` — the `F_CPU >= 16000000L` arm (the one that compiles for `uno`, `uno328pb` and
  `leonardo`, all 16 MHz): `if (us <= 1) return;` then `us <<= 2;` then `us -= 5;`. The `<<= 2` on a
  16-bit value **overflows at `us >= 16384`**. Hence the exact safe maximum is **16383**.
- `:106` — `void delay(unsigned long ms)` is 32-bit. Safe for the ms half of the split.

**The failure mode is a silently SHORT delay, not a hang or a crash.** `delayMicroseconds(20000)`
computes `20000 << 2 = 80000 mod 65536 = 14464`, minus 5 → **~3615 µs instead of 20000 µs**. On real
silicon that under-programs the byte, which then fails to verify, which burns pulses and eventually
reports a *verify* failure — a timing bug wearing a silicon-failure costume, precisely the diagnostic
confusion D-03 exists to prevent for the configuration case.

Also note `delayMicroseconds(0)` and `(1)` return immediately and are safe, so a split helper may pass
`us % 1000 == 0` to `delayMicroseconds` without a guard.

### Corrections this establishes to milestone C3 and to CONTEXT.md's `<specifics>`

CONTEXT.md `<specifics>` says `--pulse-us` "is the only live caller LOOP-07's helper will have" and
that from database data alone `delayMicroseconds()` never sees an over-ceiling value. The first half of
that is **too generous to the current code**:

- **The wire field is already unbounded.** `pulse-delay` is parsed by `get_delay()` with
  `extract_long("pulse-delay", handle->pulse_delay)` (`json_parser.c:503-497`) into a `uint32_t` with
  **no clamp of any kind** — unlike `read-settling-delay` / `read-strobe-us`, which json_parser
  explicitly clamps to `READ_TIMING_MAX_US = 1000` (`:348-362`). So a host sending
  `"pulse-delay": 100000` today produces a truncated, silently-short VPE pulse on both site 2 and
  site 5. **LOOP-07 closes a currently reachable defect; it is not merely pre-positioning for
  Phase 143.** That strengthens the C3 correction CONTEXT.md hands to Phase 146.
- **The database half is CONFIRMED.** Re-measured this session against the shipped
  `firestarter_app/firestarter/data/chip_database.json`: the complete numeric `pulse_duration` set
  across the whole database is `{10, 20, 50, 100, 200, 500, 1000}` µs, **maximum 1000 µs**, and all
  329 numeric entries belong to algorithms 7/8/11. Per-protocol:

  | protocol | n | distribution |
  |---|---|---|
  | `0x07` | 170 | 100 µs ×113, 200 ×27, **1000 ×22**, 500 ×4, 50 ×4 |
  | `0x08` | 127 | 100 µs ×104, 50 ×11, 10 ×7, 200 ×2, 1000 ×2, 20 ×1 |
  | `0x0B` | 32 | 500 µs ×21, 1000 ×6, 200 ×5 |

  Byte-identical to STATE.md's C2 and to `firestarter/CLAUDE.md`'s modal figures, and the 22 `0x07`
  1 ms parts are F-140-05's Intel family. The 329 total matches F-140-04.
- **The `65535` ceiling is minipro's CLI, not the wire.** STATE.md §C2 sources it to minipro's
  `-o pulse=N` (uint16). The Firestarter wire field is `uint32`. Phase 143 chooses `--pulse-us`'s
  bound; D-03's firmware refusal is the backstop either way.

---

## Energy-cap arithmetic (LOOP-04 / D-01 / D-02)

D-02 fixes the meaning: `accumulated = N × pulse_delay`, counting pulse widths only. D-01 fixes the
stopping rule. **The exact loop predicate matters, and only one reading makes D-01's own worked example
true.**

**Use `while (accumulated < energy_cap_us)` — emit pulse `k` iff the accumulated total *before* it is
strictly below the cap.** Equivalently: emit, add, then stop when `accumulated >= cap`.

Worked check against D-01's own numbers, `energy_cap_us = 50000`:

| pulse width | pulses emitted | accumulated | D-01's stated expectation | Match |
|---|---|---|---|---|
| 200 µs | 250 | 50000 | "200 → 250" | ✅ |
| 500 µs | 100 | 50000 | "500 µs → 100 pulses" | ✅ |
| 1000 µs | 50 | 50000 | "1000 → 50" | ✅ |
| 30000 µs | 2 | 60000 | overshoot ≤ one pulse width (10000 < 30000) | ✅ |
| 49999 µs | 2 | 99998 | overshoot ≤ one pulse width (49999) | ✅ |
| 50000 µs | 1 | 50000 | — | ✅ |

**The plausible-looking alternative is off by one.** `if (accumulated + pulse > cap) { emit; break; }`
gives **101** pulses at 500 µs (at `accumulated = 50000`, `50500 > 50000` fires one more), directly
contradicting D-01's "500 µs → 100 pulses". Do not implement D-01's prose literally; implement the
predicate that reproduces its example.

### Honest statement of the real ceiling — LOOP-04's wording needs care in the record

LOOP-04 and ROADMAP success criterion 2 both say "accumulated program time per byte **capped at
50 ms**". Under D-01's deliberate one-pulse overshoot that is exactly true only when the cap divides
evenly by the width — which **all three shipped `0x0B` widths do** (200/500/1000 → 250/100/50 pulses,
accumulated exactly 50000 µs). For an arbitrary `--pulse-us` value `w`, the bound is
`accumulated < energy_cap_us + w`, and since D-03 refuses `w > energy_cap_us`, the absolute worst case
is **`2 × 50000 − 1 = 99999 µs ≈ 100 ms`, reached at `w = 49999 µs`**.

CONTEXT.md D-01's "`50000 + 65535 ≈ 115 ms`" figure is the bound *without* D-03; with D-03 in place it
is arithmetically unreachable, because `w ≤ 50000`. Both statements are consistent with the decision —
D-01 itself says "D-03's pre-flight refusal is what keeps that bounded" — but **the phase record must
state the achievable figure (≈100 ms worst case, exactly 50 ms on every shipped width), not the
115 ms figure**, or a Phase 146 reader reconciling against gh#15 will find a third wrong number.

### Which limit trips first, per shipped row

| protocol | `max_pulses` | `energy_cap_us` | shipped widths | binding limit | max program time / byte |
|---|---|---|---|---|---|
| `0x07` | 25 | 0 (uncapped) | 50/100/200/500/1000 | `max_pulses` always | 25 × w → 1.25 ms … **25 ms** at 1000 µs |
| `0x08` | 25 | 0 (uncapped) | 10/20/50/100/200/1000 | `max_pulses` always | 25 × w → 0.25 ms … **25 ms** at 1000 µs |
| `0x0B` | 255 | 50000 | 200/500/1000 | **`energy_cap_us` always** (250/100/50 pulses, all < 255) | **exactly 50 ms** |

This table is the concrete answer to `<specifics>`'s "honest test": for any byte, a reader can now say
how many pulses it will get, of what width, when it stops, and which limit stopped it. **On no shipped
row do both limits trip simultaneously**, so the two new message IDs are unambiguous in practice — but
the loop must still check `energy_cap_us > 0` before consulting it, because `0` means uncapped
(`eprom_params.h:53`), not "cap at zero".

---

## Overprogram arithmetic (LOOP-03 / D-07 / D-08)

Unreachable with shipped data — `overprogram_factor = 0` on all three rows. D-08's pure function is the
only possible oracle. Suggested shape and the boundary values a test must cover:

```c
/* Pure: no handle, no hardware, no PROGMEM. Returns 0 when no overprogram applies. */
uint32_t eprom_overprogram_us(uint8_t pulse_count, uint32_t pulse_us,
                              uint8_t factor, uint32_t cap_us);
```

| Case | Inputs | Expected | Why it matters |
|---|---|---|---|
| Gating — every live row | `factor = 0` | `0` | LOOP-03's guard; proves all three shipped rows emit zero extra pulses |
| Nominal | `N=1, pulse=100, factor=3, cap=75000` | `300` | the `3 × N × pulse` form |
| At the clamp boundary | `N=25, pulse=1000, factor=3, cap=75000` | `75000` | `3 × 25 × 1000 = 75000` — exactly the cap, the Intel-Intelligent worst case cited on gh#15 |
| Above the clamp | `N=25, pulse=1001, factor=3, cap=75000` | `75000` | D-08/Phase 140 D-08: the cap **CLAMPS**, it does not refuse |
| 32-bit overflow safety | `N=25, pulse=65535, factor=3, cap=75000` | `75000` | the raw product is `4,915,125` — fits `uint32_t` (max 4,294,967,295) but **overflows any `uint16_t` intermediate**. Compute in `uint32_t` throughout: `(uint32_t)factor * pulse_count * pulse_us` |
| Cap of zero | `N=5, pulse=100, factor=3, cap=0` | decide and document | `overprogram_cap_us = 0` ships on no row; treat `0` as "no clamp" or as "clamp to 0"? Pick one, comment it, test it |

**Delivery via D-07's idiom** — save `handle->pulse_delay`, set it to the computed width, one
`firestarter_set_data` call, restore:

```c
uint32_t op_us = eprom_overprogram_us(pulse_count, org_delay, overprogram_factor, overprogram_cap_us);
if (op_us) {
    handle->pulse_delay = op_us;                              /* org_delay idiom, eprom.cpp:161,172 */
    handle->firestarter_set_data(handle, addr, (uint8_t)handle->data_buffer[i]);
    handle->pulse_delay = org_delay;
}
```

Note the interaction with LOOP-07: `op_us` can be up to `75000` µs, which is **4.6× the 16383 ceiling**
— so `memory_set_data`'s `delayMicroseconds` must already be routed through the safe helper before this
path is even plausible. That is precisely why D-06 puts the helper at the primitive rather than in
`eprom.cpp`: the overprogram pulse gets its safety for free from site 2's fix.

**Record the non-claim plainly** (D-08): the end-to-end overprogram path is proven only in its
arithmetic and its gating, never through the loop, because no shipped row reaches it. Hand that to
Phase 146 alongside F-140-05.

---

## LOOP-08 mechanics — what actually happens to the control register

Traced from source, because the premise stated in CONTEXT.md `<canonical_refs>` ("a verify read does not
disturb the control register") is false and would send a test after the wrong assertion.

### The real chain

1. **Once per block**, `eprom_write_execute` asserts the route:
   `handle->firestarter_set_control_register(...)` → `eprom_internal_set_control_register`
   (`eprom.cpp:319-325`, which remaps `CTRL_VPE_ENABLE` → `CTRL_VPP_P1_ENABLE` when
   `using_p1_as_vpp(handle)`) → `memory_set_control_register` (`memory.cpp:141-145`, read-modify-write)
   → `rurp_write_to_register(CONTROL_REGISTER, data)`.
2. **Per byte, twice** (once for the pulse, once for the verify), both `memory_set_data` (`:249`) and
   `memory_get_data` (`:203`) call `handle->firestarter_set_address` → `mem_util_set_address`
   (`:175-191`), which **unconditionally** calls
   `rurp_write_to_register(CONTROL_REGISTER, mem_util_calculate_top_address_register(...))` at `:186`.
3. `mem_util_calculate_top_address_register` (`:159-173`) rebuilds the whole register from two parts:
   - address bits: `(address >> 16) & (A16 | A17 | A18 | CTRL_READ_WRITE)`
   - preserved bits: `rurp_read_from_register(CONTROL_REGISTER) & mask`, where
     `mask = CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_VPP_REGULATOR_ENABLE`
     (`:161`), **plus `CTRL_VPP_VPE_DROP_ENABLE` only when `handle->pins < 32`** (`:162-166`).
4. `rurp_read_from_register(CONTROL_REGISTER)` returns the **cached logical** value
   (`rurp_register_utils.h:92-100`), not a hardware read-back.
5. `rurp_write_to_register(CONTROL_REGISTER, data)` (`rurp_register_utils.h:24-59`):
   **`if (control_register == data) return;`** at `:38-41` — the write is **elided entirely**, no
   strobe, when nothing changed. A `CTRL_VPP_P1_ENABLE` set→clear transition additionally sets
   `settle = true` → `delayMicroseconds(4)` at `:56-58`.

### Consequences the loop must be built on

- **VPE survives the verify read** because `CTRL_VPE_ENABLE` (and `CTRL_VPP_P1_ENABLE`, and
  `CTRL_VPP_REGULATOR_ENABLE`) are in the **unconditional** preserve mask — *not* because the verify
  read leaves the register alone. Comment it that way.
- **Within a block that stays in one 64 K page and one R/W direction, the CONTROL write is elided** and
  costs nothing. So "assert and settle once per block" is already the natural cost profile — LOOP-08 is
  mostly about *not breaking* it.
- **The R/W direction can flip the register twice per byte.** `mem_util_remap_address_bus` is called
  with `WRITE_FLAG` for the pulse (`memory.cpp:323`) and `READ_FLAG` for the verify (`:205`), and
  `CTRL_READ_WRITE` (`0x40`) is part of the top-address mask, i.e. logical address bit 22. For a chip
  whose `bus_config.rw_line == 22`, alternating pulse↔verify flips that bit and the CONTROL register
  **is** re-strobed twice per byte. That is expected, is not a LOOP-08 violation, and will show in the
  new trace — but a test asserting "exactly one CONTROL strobe per block" would be wrong.
- **The `delay(500)` settle must not move inside the per-byte loop.** It sits at `eprom.cpp:152` today,
  guarded by the `get_control_register(CTRL_VPP_REGULATOR_ENABLE) == 0` idempotency check at `:144`.
  Keep that guard-plus-settle above the byte loop. `eprom_internal_ensure_regulator_enabled`
  (`:327-332`) is a dead-code helper with exactly this shape and is a cleaner home for it than the
  inline duplicate.

### Recommended assertion set for the sixth env's LOOP-08 case

Using `HOST_STUBS_REAL_REGISTER_UTILS` (so production's real elision runs) plus the strobe recorder:

1. Exactly **one** CONTROL strobe carries the VPE/route bit going 0→1, and it occurs **before** the
   first data strobe of the block.
2. Across every byte of the block, **every** CONTROL value written has the VPE/route bit **set**
   (i.e. `value & CTRL_VPE_ENABLE` or, for `using_p1_as_vpp` parts, `CTRL_VPP_P1_ENABLE`).
3. On a 32-pin part with a block crossing an A16 boundary (D-09): the A16 bit toggles in the emitted
   CONTROL values, and the route bit still never clears.
4. **Non-vacuity control:** a case with no route asserted must show the bit absent — otherwise
   assertion 2 passes on an empty or mis-keyed stream.

---

## DIP32 / A16 truth table — D-09's mechanism, corrected from source

CONTEXT.md D-09 states "on a 32-pin part that bit *is* A16". **That is true on only some builds and
boards.** The bit-identity depends on two independent axes, and the *observable consequence* D-09 relies
on comes from a third.

### Axis 1 — the compile-time macro layout (`include/rurp_pinout.h`)

| Branch | `CTRL_ADDRESS_LINE_16` | `CTRL_VPP_VPE_DROP_ENABLE` | Collide? |
|---|---|---|---|
| `#ifndef HARDWARE_REVISION` (legacy, `:74-83`) | `CTRL_VPP_VPE_DROP_ENABLE` (macro alias) | `0x01` | **YES — same bit** |
| `#else` HARDWARE_REVISION (wide, `:86-97`) | `0x01` | **`0x100`** | **NO — distinct** |

**`-D HARDWARE_REVISION` is in the shared `[env]` `build_flags` (`platformio.ini:23`) and is inherited
by `uno`, `uno328pb`, `leonardo`, `native`, and every `native_*` env** (`native_nodevtools` spells it out
explicitly at `:172`, with a comment noting it is "load-bearing, not incidental"). **Every build this
project produces takes the wide branch, where there is no macro-level collision.**

### Axis 2 — the per-revision physical mapping (`include/rurp_hw_rev_utils.h:15-41`)

`rurp_map_ctrl_reg_for_hardware_revision()` maps the 9-bit logical register onto the 8-bit shift
register:

| Board revision | drop → physical | A16 → physical | Collide physically? |
|---|---|---|---|
| `REVISION_2_0` / `2_1` / `2_2` / `2_3` (`:19-27`) | `CTRL_VPP_VPE_DROP_ENABLE_REV2` = `0x01` | `CTRL_ADDRESS_LINE_16_REV2` = `0x20` | **NO** |
| `REVISION_0` / `REVISION_1` (`:28-32`) | `CTRL_VPP_VPE_DROP_ENABLE_REV1` = `0x01` | passes through as logical `0x01` | **YES — both land on physical `0x01`** |
| `REVISION_UNKNOWN` / unrecognised (`:33-37`) | `ctrl_reg = 0` (fail-safe: no VPP, no VPE) | — | n/a |

### Axis 3 — the actual mechanism, and it is revision-independent

`mem_util_calculate_top_address_register`'s `if (handle->pins < 32)` guard (`memory.cpp:162`) excludes
`CTRL_VPP_VPE_DROP_ENABLE` from the **preserve mask** for every 32-pin part, **on every board revision
and both macro layouts**. So on `pins >= 32`:

- the recomputed `top_address` carries no drop bit;
- `control_register != data`, so the write is **not** elided — it is strobed;
- **the drop route is cleared by the first `set_address` of the block.**

### What this means for `0x08` today (a pre-existing defect Phase 141 must not depend on)

`eprom_write_execute:148-151` asserts `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` for
`0x07`/`0x08`, waits `delay(500)`, then the first `memory_set_data` → `set_address` **clears the drop
bit before the first pulse is emitted**. So on protocol `0x08` (`pins == 32`,
`vpp_path = VPP_PATH_DROP_RESISTOR`) the "13 V via `CTRL_VPP_VPE_DROP_ENABLE`" behaviour that
`firestarter/CLAUDE.md`'s Algorithm Handlers row claims survives exactly zero address writes. On `0x07`
(`pins == 28 < 32`) the drop bit **is** preserved and the row's claim holds. On `0x0B`
(`pins == 24`, `VPP_PATH_DIRECT_VPE`) the drop bit is never set in the first place (`:147`).

**So D-09's conclusion is exactly right — `0x08` is the row where this bites — while its stated
mechanism is not.** Phase 141's obligation is unchanged: a **named, commented branch** rather than
inherited-by-accident behaviour, plus a native test on the emitted CONTROL writes across an A16
crossing. Two additional planning notes:

- **Key the branch on `handle->pins >= 32`, not on `protocol`.** That is the actual condition the
  preserve mask uses, it keeps `0x07` and `0x0B` on one path, and — decisively — it adds **no new
  tier-1 (protocol-keyed) site**, satisfying D-11. A `protocol == 0x08` predicate would be a fourth
  tier-1 site and would fail `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines`.
- **`handle->pins` is host-supplied**, parsed from the `pin-count` JSON field (`json_parser.c:503`), and
  is *not* derived from `protocol`. A `0x08` command with `pins != 32` is representable on the wire, so
  the guard must read `pins`, which is what the mask reads too.
- **`using_p1_as_vpp()` is the existing escape** (`memory_utils.h:24-28`): true when
  `pins == 32 && vpp_line == VPP_P1_32_DIP (0x15)`, and `CTRL_VPP_P1_ENABLE (0x08)` **is** in the
  unconditional preserve mask, so a P1-routed VPE survives every `set_address`. The `AM27C020`
  `DIP32_27C020` pinout used by the existing trace fixture has `vpp_line == 21 == 0x15`, so
  `using_p1_as_vpp` is **true** for it [VERIFIED: `test_trace_eprom_v131/host_stubs.cpp:113-115`].
  **Choosing P1 vs drop resistor is Phase 142's (VPP-01/VPP-03) — hand this finding forward, do not
  pre-empt it.**

---

## What "hard-fails the block" actually does (LOOP-05)

CONTEXT.md `<specifics>` asks for this to be explicit. Traced end to end:

1. `eprom_write_execute` sets `handle->response_code = RESPONSE_CODE_ERROR` (the existing shape at
   `eprom.cpp:192`) after disabling the route and emitting the error frame.
2. `_process_incoming_data` (`src/eprom_operations.cpp:115-117`) calls
   `op_execute_function(handle->firestarter_operation_main, handle)`; on false it **returns false
   immediately and does NOT advance `handle->address` (`:124`)**.
3. `op_execute_function` (`src/operation_utils.cpp:186-191`) returns
   `_execute_operation(...) != ERROR`; the `RESPONSE_CODE_ERROR` → `ERROR` mapping is the switch arm at
   `operation_utils.cpp:420`.
4. The `eprom_*` caller inverts the result, the command reports finished, and **`command_done()` runs**
   (`src/firestarter.cpp:162-171`): `rurp_set_programmer_mode()`, `rurp_chip_disable()`,
   `rurp_write_to_register(CONTROL_REGISTER, 0x00)`, LSB and MSB zeroed, `cmd = CMD_IDLE`,
   `rurp_set_communication_mode()`.

**Answers for the phase record:**

- **"Hard-fails the block" and "the write aborts" are the same event.** The firmware processes **no
  further blocks** — the streaming pump exits, it does not skip ahead. There is no partial-continue path.
- **The host observes** the `MSG_ERROR`-severity ID frame (one of the two new IDs) followed by normal
  command termination. Phase 143 / HOST-03 renders it. Nothing here requires a host change.
- **`command_done()` zeroing the whole control register is a second, orthogonal safety net** —
  it disables every HV route regardless of what `eprom_write_execute` did. LOOP-05's own disable is
  still required (it must happen before the error is reported and before the pump unwinds), and
  Phase 142 / VPP-02 generalises it to every exit.
- ⚠️ **Vacuity trap for the LOOP-05 test.** Because `command_done()` zeroes the register
  unconditionally, a test that drives the whole command and then asserts "no HV route is active" **will
  pass even if `eprom_write_execute` disables nothing**. The assertion must be scoped to the CONTROL
  writes `eprom_write_execute` itself emits — i.e. drive `firestarter_operation_main` directly (the
  existing `drive_v131_write` pattern at `test_trace_eprom_v131.cpp:254-269` does exactly this) and
  assert on the recorded strobe stream, with a paired negative control.

---

## Per-byte loop shape (LOOP-01 / LOOP-06)

Not a locked decision — D-12's last bullet leaves "the loop's exact function decomposition and naming"
free. This is the shape the source constraints imply; the planner may restructure it, but the ordering
constraints below are load-bearing.

```
eprom_write_execute(handle):
  row = eprom_params_for(handle->protocol)        # NULL -> fail closed (Phase 140 D-05)
  hoist all six columns via pgm_read_* into locals   # once per block, not per byte
  org_delay = handle->pulse_delay                   # eprom.cpp:161 idiom

  # --- once per block (LOOP-08) ---
  if regulator not already enabled:                 # eprom.cpp:144 idempotency guard
      assert route (protocol == 0x0B || FLAG_VPE_AS_VPP ? direct : drop)   # KEEP verbatim, Phase 142 owns it
      delay(500)                                    # eprom.cpp:152 settle, stays above the byte loop
  explicit, commented pins >= 32 branch             # D-09; keyed on pins, never on protocol

  for i in 0 .. data_size-1:
      expected = (uint8_t)handle->data_buffer[i]    # char[] -> cast required (firestarter.h:202)
      addr = handle->address + i

      # --- LOOP-06 skips, before any pulse ---
      if expected == 0xFF: continue                 # no read needed; a blank cell is already 0xFF
      if get_data(handle, addr) == expected: continue

      # --- LOOP-01 fixed-width pulse -> verify ---
      pulses = 0; accumulated = 0
      loop:
          set_data(handle, addr, expected)          # pulse; width is org_delay, NEVER grown
          pulses += 1; accumulated += org_delay     # D-02: pulse widths only
          if get_data(handle, addr) == expected: break -> converged
          if pulses >= max_pulses:            -> fail(MSG_ERR_..._MAX_PULSES, addr, pulses)
          if energy_cap_us && accumulated >= energy_cap_us:
                                              -> fail(MSG_ERR_..._ENERGY_CAP, addr, pulses)

      # --- LOOP-03, unreachable on shipped rows ---
      op_us = eprom_overprogram_us(pulses, org_delay, overprogram_factor, overprogram_cap_us)
      if op_us: handle->pulse_delay = op_us; set_data(...); handle->pulse_delay = org_delay

  if verify_mode == VERIFY_PER_PULSE_PLUS_FINAL:     # see the verify_mode gap above
      one final full-block read-and-compare pass
```

### Ordering constraints that are not stylistic

- **`0xFF` check before the read.** A `0xFF` target byte can never need a pulse on a UV EPROM (erased
  state is all-ones and programming only clears bits), so checking it first saves one bus read per
  `0xFF` byte across the whole block. Doing the read first is correct but wasteful, and on a mostly-`0xFF`
  image the difference is a whole extra read pass.
- **Skip-check read, then pulse, then verify — the read count per byte is `1 + pulses`.** The old block
  loop pulsed every byte on pass 1 unconditionally (`mismatch_bitmask` is `memset` to `0xFF` at
  `eprom.cpp:157`) and read once per pass, i.e. `passes` reads. **This shifts the readback model's
  indexing by one**, which matters when reusing `trace_readback_seed(idx, target, converge_after)`:
  `converge_after = N` now means "matches on read N+1", i.e. **N pulses** after the skip-check read
  returns a mismatch. Seed and assert accordingly, and state the mapping in a comment — this is the
  single easiest place for the new suite to be silently off by one.
- **`energy_cap_us && ...` guard is mandatory.** `0` means uncapped (`eprom_params.h:53`); an unguarded
  `accumulated >= energy_cap_us` would abort `0x07`/`0x08` after the first pulse.
- **Check `max_pulses` and the energy cap *after* the failed verify**, so a byte that converges on its
  last permitted pulse succeeds rather than failing at the boundary.
- **`handle->pulse_delay` must be restored on every exit path**, including the two failure paths — the
  existing loop restores it only on success (`eprom.cpp:172`) because the failure path returned into a
  torn-down command. With the overprogram save/restore added, a failure between save and restore would
  leak a modified width into the handle. Cheapest fix: never mutate `pulse_delay` except inside the
  overprogram block, and restore immediately after the single call.

### Counter width

`max_pulses` is `uint8_t` and `0x0B` ships `255`. A `uint8_t` counter with `pulses >= max_pulses`
checked **after** increment reaches `255` without wrapping, so `uint8_t` is sufficient and is the
cheaper choice on AVR. If the planner prefers `uint16_t` for headroom, note it costs flash in the
comparison and is not required by any shipped row. `accumulated` must be `uint32_t` (`50000` exceeds
`uint16_t` at 50 ms, and `energy_cap_us` is `uint32_t`).

---

## Gates, baselines and fixtures — measured state and what this phase does to each

Complete sweep of `firestarter/tests/*.py`, `firestarter/scripts/check_*.py`, the five native envs, and
both firmware CI workflows. **Everything below is GREEN at the live branch tip** — `pytest tests/ -q`
reports **244 passed in 10.74s** [VERIFIED: run this session], matching 140-PARAM-TABLE-RECORD §7.

### Which gates run in CI, and which do not

`.github/workflows/build.yml` and `beta-build.yml` each run exactly four firmware legs:

| Leg | build.yml | beta-build.yml |
|---|---|---|
| `pio test -e native` | `:142` | `:122` |
| `pio test -e native_nodevtools` | `:155` | `:128` |
| **`pytest tests/ -v`** | **`:161`** | **`:134`** |
| `pio run` (all three AVR envs) | `:193` | `:145` |

**`check_size_baseline.py`, `check_build_warnings.py` and `check_cmake_manifest.py` are invoked in NO CI
leg** [VERIFIED: `grep -rn "check_size_baseline\|check_build_warnings\|check_cmake_manifest" .github/workflows/` → no matches].
They are local, run-by-name gates. **But their pytest wrappers are CI-covered**, and two of those
wrappers assert against the *real tree*, which changes the risk picture materially:

| Gate module | Asserts against the real tree? | CI-covered? |
|---|---|---|
| `tests/test_protocol_branch_inventory.py` | **YES** — 7 tests, live re-parse of `src/proms/eprom.cpp` | **YES** |
| `tests/test_check_cmake_manifest.py::test_armed_and_passing_on_the_real_tree` (`:90-110`) | **YES** — subprocess-invokes the checker on the live manifest | **YES** |
| `tests/test_golden_trace_identity_eprom_v131.py` | **YES** — 6 tests, blob SHA of `_shared/eprom_v131_expected.h` | **YES** |
| `tests/test_eprom_params_citations.py` | **YES** — blob SHAs of `eprom_params.h` + `eprom_params.cpp` only | **YES** |
| `tests/test_check_size_baseline.py` / `test_check_build_warnings.py` | No — fixture logs only | YES (but tests the checker, not the tree) |

### Per-gate disposition for Phase 141

| Gate / fixture | State now | Phase 141 effect | Action required |
|---|---|---|---|
| **`tests/test_protocol_branch_inventory.py`** (7 tests) + `tests/golden/protocol_branch_inventory.json` | GREEN. Golden's `blob_shas` match live HEAD exactly (`eprom.cpp` → `8dfa4cc…`, `eprom_params.cpp` → `5dffe84…`); 24 sites = 3 tier-1 + 21 tier-2 — **D-11's counts CONFIRMED** | **RED, and it is a CI failure.** Three of the seven tests break | Re-derive the golden **and edit one assertion literal** — see the recipe below |
| **`native_trace_v131`** (`test/native/avr/test_trace_eprom_v131/`) | GREEN, 5 cases / 1 suite | **RED by design (D-10).** The suite still compiles — no signature it calls changes — and fails only on `v131_assert_stream_equals` | Leave RED. Do **not** re-freeze. Capture the new trace as a committed artifact |
| **`tests/test_golden_trace_identity_eprom_v131.py`** (6 tests) | GREEN | **Must stay GREEN.** It pins the blob SHA of `_shared/eprom_v131_expected.h` and requires `test_trace_eprom_v131.cpp` to still `#include` it | Do not touch `eprom_v131_expected.h`; do not delete or disable the trace suite |
| **`tests/test_eprom_params_citations.py`** (10 tests) | GREEN | Unaffected — scans `eprom_params.h`/`.cpp` only, and this phase changes neither | None. If a plan *does* touch the table, this gate goes RED — treat that as a signal, not an obstacle |
| **`tests/test_check_cmake_manifest.py`** | GREEN, armed | **RED if any new `.cpp` is added under `src/`.** `platform/py32f071/CMakeLists.txt` already names `memory.cpp` (`:59`), `eprom.cpp` (`:60`), `eprom_params.cpp` (`:61`) | **This is why D-06's placement matters.** Keep the helper in `memory.cpp`/`memory_utils.h` → zero manifest work |
| **`check_size_baseline.py` default (byte-identity)** | GREEN (measured this session, see below) | **RED — any flash byte changes.** Not CI-visible | Expected. Use `--policy merge05` for the judged verdict; Phase 144 / TEST-08 owns reconciling the live baseline |
| **`check_size_baseline.py --policy merge05 --baseline .../size_baseline_base01.json`** | GREEN with 42/36/56 B headroom | Must stay GREEN | Budget against it — see §"Flash and RAM budget" |
| **`check_build_warnings.py`** | GREEN, `native`/`native_nodevtools` both `== 1166` watermark with **zero headroom** (F-140-01) | RED if the change adds any native warning | Never pair `<Arduino.h>` with the `avr/pgmspace.h` shim in one TU. `eprom_params.cpp` and `not_implemented.cpp` are the two TUs that model the safe include discipline |
| **`native` / `native_nodevtools`** | 141 cases / 17 suites each, pinned by `size_baseline.json:native_envs` | Must stay **exactly** 141/17 | **Never** add the new suite to either `test_filter` or `-I` list. Both must keep their 17-entry lists byte-identical to each other |
| **`tests/test_pr45_non_ancestry.py`** | GREEN | Unaffected — pins `include/rurp_vpp.h` and `src/rurp_vpp.cpp` only (`:113-116`) | None |
| **`test/native/avr/test_messages/test_rurp_log_id.cpp:147-176`** | GREEN | Unaffected — calls `rurp_log_id(0xB1, params, 6)` with a **literal** id, not through the loop | None. Do not "fix" it to reference the new IDs; that would add a case to a pinned env |

### Re-deriving the D-13 golden — the exact mechanics

**There is no re-derivation script.** `_extract_predicates()` exists only inside the test module
[VERIFIED: `grep -rln "_extract_predicates" --include="*.py" --include="*.sh" .` → one match]. The
sanctioned path (`meta.how_to_update`: "Diffing the extractor's live output against this JSON is the
only sanctioned way to update it") is to import it:

```bash
cd /workspaces/firestarter && python3 -c "
import sys, json
sys.path.insert(0, 'tests')
import test_protocol_branch_inventory as m
live = m._extract_predicates((m._REPO_ROOT / 'src/proms/eprom.cpp').read_text())
print(json.dumps(live, indent=2))
print('tier1 lines:', sorted(s['line'] for s in live if s['tier'] == 'protocol'))
print('counts:', len(live), 'tier1:', sum(1 for s in live if s['tier']=='protocol'))
"
```
[VERIFIED: executed this session against the unchanged file — returns 24 sites, `tier1 lines: [71, 145, 218]`, byte-matching the committed golden.]

Four things must then be updated, and **only the first is machine-derived**:

1. `sites[]` — the `(line, predicate, keyed_on, tier)` tuples, straight from the command above.
2. **`sites[].reason` — hand-authored.** `_extract_predicates` does **not** emit `reason`, yet
   `test_inventory_is_non_vacuous` (`:463-467`) asserts every site has a non-empty one. Carry forward
   the existing reason for each surviving site; author new ones for new sites. **Correct the `:328`
   entry's reason** — it currently claims `eprom_internal_ensure_regulator_enabled` is "used by callers
   outside the write path", which is false (zero callers anywhere).
3. `meta.blob_shas["src/proms/eprom.cpp"]` — computable **before** committing, because a blob SHA depends
   only on content: `git hash-object src/proms/eprom.cpp` equals `git rev-parse HEAD:src/proms/eprom.cpp`
   for a committed file [VERIFIED: both return `8dfa4cc…` this session]. So: rewrite → `git hash-object`
   → write into the golden → commit both **in the same commit**, or `test_blob_shas_match_the_recorded_inventory`
   fails. `eprom_params.cpp`'s SHA is unchanged; leave it.
4. `counts.{total_sites,protocol_keyed_sites,other_sites}` — keep consistent with `sites[]`. Also update
   `meta.recorded_at_head` and `meta.recorded_by` (not asserted by any test, but `meta.frozen_for`
   explicitly anticipates this phase and should be re-pointed at Phase 142).

### ⚠️ The one assertion literal that must be hand-edited

`test_exactly_three_protocol_keyed_sites_at_the_pinned_lines` (`:443-452`) asserts
`protocol_lines == [71, 145, 218]` **against a hard-coded list in the test module, not against the JSON**.
Re-deriving the golden does **not** fix it. The rewrite shifts `eprom_write_execute`'s VPP predicate off
line 145 and `eprom_check_vpp`'s off line 218, so **`test_protocol_branch_inventory.py:446` must be
edited** with the new line numbers.

This is consistent with the house rule "fix the locator, not the assertion" — the line list *is* the
locator. But note the failure text explicitly says "fewer than three means one of the pinned sites was
removed without updating this inventory", so **the count must stay three**:

- **`:71` `switch (handle->protocol)`** — the `pulse_delay == 0` fallback switch. Phase 140 D-03 keeps it.
- **`:145` `protocol == 0x0B || FLAG_VPE_AS_VPP`** — inside `eprom_write_execute`, the function being
  rewritten. **Keep this predicate verbatim; only its line moves.** Replacing it with the table's
  `vpp_path` column is VPP-01, **Phase 142** — and the golden's own `meta.frozen_for` says so:
  "Phase 142 rewrites the VPP branches at `:145`/`:218` into the eprom_params table's vpp_path column".
- **`:218`** — inside `eprom_check_vpp`, untouched by this phase; its line shifts only because the file
  above it shrinks.

If a plan instead removes the `:145` predicate, tier-1 drops to 2 and the gate's own error message
becomes correct about a real regression. Do not do that here.

### Expected inventory movement (record it — D-11 / `<specifics>`)

Deletions remove these tier-2 sites: `:119` and `:131` (`i < handle->data_size` loop bounds), `:132`
(the `verify_and_update_mask` comparison), and `:144` (`get_control_register(...) == 0`) only if the
idempotency guard is restructured. The new loop adds its own byte loop bound, the `0xFF`/match skip
predicates, the `max_pulses` and `energy_cap_us` checks, and the `pins >= 32` branch. **Predict the
before/after counts in the plan, then record the measured pair in the phase record** — the tier-2 count
moving is the most legible single proof that LOOP-02's removals happened, and an unchanged count would
itself be suspicious (the golden's own `meta.frozen_for` says exactly that).

---

## Message catalog mechanics (D-04) — tri-repo, verified

### Current state: all three copies are byte-identical

[VERIFIED: `diff -q` this session] `tools/catalog/messages.toml` and `codegen.py` in the meta repo are
byte-identical to `firestarter/tools/catalog/` and `firestarter_app/tools/catalog/`. So
`sync_to_subrepos.sh` is currently a no-op and will produce exactly the expected diffs.

### Free ID space near `MSG_ERR_VERIFY 0xAF` / `MSG_ERR_WRITE_FAILED 0xB1`

The catalog holds **73 messages**. The ERROR band `0xA0..0xBF` is nearly full — assigned `0xA0..0xAD`,
`0xAF..0xBC`. **Free ERROR-band slots: `0xAE`, `0xBD`, `0xBE`, `0xBF`** [VERIFIED: `tomllib` enumeration
of `messages.toml`].

**Recommendation: `0xBD` and `0xBE`.** Contiguous, immediately after the last-assigned `0xBC`
(`MSG_ERR_FL4_BOOT_BLOCK_LOCKED`), preserving the band's ascending layout and leaving `0xAE` (a
historical gap) and `0xBF` (the band's last slot) free. **After this phase only two ERROR slots remain**
— worth naming in the phase record for Phase 142/143's benefit.

**No severity-band validation exists.** `validate_catalog()` (`codegen.py:167-320`) enforces 10 rules —
id range/uniqueness, `^MSG_[A-Z][A-Z0-9_]*$` naming, non-empty format, param types, render hints,
severity from the allowed set, `wire_format`, printf-spec-vs-param-count parity, and a ≤ 24-byte fixed
param budget — but **nothing ties an `ERROR` severity to the `0xA0..0xBF` range**. The band is
convention, honoured for readability, not machine-enforced.

### Authoring format

Follow the shape of `MSG_ERR_WRITE_FAILED` (`messages.toml`, the `0xB1` entry). A suggested pair —
`[u24 hex_addr, u8]` = 4 param bytes each, comfortably inside the 24-byte budget:

```toml
[[messages]]
id          = 0xBD
name        = "MSG_ERR_MAX_PULSES"
severity    = "ERROR"
format      = "Byte at %s failed to program within %d pulses"
params      = [{ type = "u24", render = "hex_addr" }, { type = "u8" }]
wire_format = "id_frame"

[[messages]]
id          = 0xBE
name        = "MSG_ERR_ENERGY_CAP"
severity    = "ERROR"
format      = "Byte at %s exceeded its program-energy budget after %d pulses"
params      = [{ type = "u24", render = "hex_addr" }, { type = "u8" }]
wire_format = "id_frame"
```

Rule 9 is the easy one to trip: the printf-specifier count must equal the non-`bytes` param count.
`hex_addr` renders through `%s`, plain `u8` through `%d` — check against an existing entry with the same
shapes rather than guessing. `messages.toml:1-8` also warns **DO NOT REORDER ENTRIES** (codegen sorts by
id; source order exists for diff readability), so append each new block in id order near its neighbours.

Firmware emission uses the existing macros in `include/logging_id.h`:
`LOG_ERROR_ID_BYTES(id, buf, n)` (`:110`) for a packed multi-param payload — the shape
`eprom.cpp:182-191` already uses — or `LOG_ERROR_ID_U24` / `_U8` for single params.

### The sync + regen command, and exactly which files move

```bash
bash /workspaces/tools/catalog/sync_to_subrepos.sh
```

| Repo | File | How it changes |
|---|---|---|
| **meta** | `tools/catalog/messages.toml` | **hand-authored** — the canonical edit |
| **`firestarter/`** | `tools/catalog/messages.toml` | **copied** by the script (`:29`, `:38-54`) |
| **`firestarter/`** | `tools/catalog/codegen.py` | copied — byte-identical today, so no diff |
| **`firestarter/`** | `include/messages.h` | **generated** (`--language cpp`, `:79-82`) — two new `#define`s |
| **`firestarter_app/`** | `tools/catalog/messages.toml` | **copied** (`:30`) |
| **`firestarter_app/`** | `tools/catalog/codegen.py` | copied — no diff |
| **`firestarter_app/`** | `firestarter/messages.py` | **generated** (`--language python`, `:92-95`) — two new constants + two `MessageDef` entries |

> **Completion to CONTEXT.md D-04's tri-repo list.** D-04 says `firestarter/` gets "the loop rewrite,
> the delay helper, the new native suite, the re-derived D-13 gate golden". It omits that
> **`firestarter/tools/catalog/messages.toml` also receives a synced copy**, and that
> `firestarter_app/` receives **two** files, not one. Both sub-repos carry a vendored catalog copy that
> the script asserts byte-identical to each other (`:63-70`). Name all of them in `commits_land_in:`.

⚠️ **Two latent defects in the sync script, worth knowing before trusting its output.** Lines `:84` and
`:97` are `diff -q "$X" "$X"` — a file compared to **itself**. Both are tautologies, so the
`OK: … regenerated.` messages after steps 2 and 3 **prove nothing**. The genuine invariant checks are
step 1's per-file `diff` (`:48`) and the cross-sub-repo comparison (`:65`). Verify the regen independently:

```bash
git -C /workspaces/firestarter diff --stat -- include/messages.h tools/catalog/messages.toml
git -C /workspaces/firestarter_app diff --stat -- firestarter/messages.py tools/catalog/messages.toml
```

Also: `codegen.py` writes `Total messages: 73` into both generated headers
(`codegen.py:127`, `:145`); it becomes 75. **No test asserts that count** [VERIFIED: grep across both
sub-repos' `tests/`], so the header comment moving is expected, not a gate.

### Cross-repo parity: what does and does not cover the new IDs

`firestarter_app/tests/test_revision_constants_parity.py` scans **`firestarter/include/firestarter.h`**
(`CMD_*`, `FLAG_*`) and **`rurp_pinout.h`** (`CTRL_*`) — **not `messages.h`** [VERIFIED: `:148`, `:620-644`].
So two new message IDs do **not** trip the existing host parity gate. Adding a `messages.h`↔`messages.py`
parity leg is **Phase 144 / TEST-04**, exactly as CONTEXT.md D-04 states. Phase 141 breaks nothing here
and should not pre-build TEST-04's leg.

### Orphaned catalog IDs — a LOOP-02 side effect to decide about

LOOP-02's removals leave two catalog entries with **zero firmware callers**:

| ID | Name | Emitted at | Catalog entry | Note |
|---|---|---|---|---|
| `0x51` | `MSG_INFO_RETRIES` | `eprom.cpp:170` (removed) | `messages.toml:161-167`, `severity = "INFO"`, format `"Number of retries: %d"` | The concept ("retries") is what LOOP-01 abolishes |
| `0x15` (debug) | `DBG_PULSE_DELAY_MISMATCH` | `eprom.cpp:178` (removed) | `messages.toml:890-894`, format `"Mismatch, retrying with increased pulse delay from %d to %d"` | **Its text encodes the adaptive growth LOOP-02 removes** |

**No orphan-ID gate exists** [VERIFIED: no such assertion in `firestarter/tests/` or
`firestarter_app/tests/`], so leaving them costs nothing mechanically. But `DBG_PULSE_DELAY_MISMATCH`'s
*wording* will actively contradict shipped behaviour, and a wording-only catalog change produces a
**zero-byte firmware diff** (`messages.h` is ID-only) — so retiring or rewording it is nearly free.
Also note a pre-existing shape mismatch: its params are declared `u8, u8` while `eprom.cpp:178` passed
`(uint16_t)org_delay, (uint16_t)handle->pulse_delay` via `LOG_DEBUG_ID_SUB_U16_U16`. Removing the call
site removes the mismatch. **Recommendation: leave both IDs assigned** (deleting an id risks reuse
confusion and touches the host's generated table for no behavioural gain) **and state in the phase
record that both are now unreferenced by firmware**, handing the wording question to Phase 146 / CLOSE-03
alongside the other doc reconciliations.

---

## Flash and RAM budget — measured this session, conflict RESOLVED

CONTEXT.md flags a conflict: `size_baseline_v131.json` implies +22/+28/−56 B while F-138-02 says live
headroom is 8 B / 2 B. **Resolved by measurement and by ancestry.**

### The branch is NOT on the drifted `beta` tip

[VERIFIED: git, this session, in `/workspaces/firestarter`]

- `HEAD` = `e2e25b5a7cfd09cefb349827fb97ceba96e60ac7` on `gsd/v1.31-27c-programming-algorithm-fidelity`
- `git merge-base HEAD origin/beta` = **`3085084`** — the decided, undrifted fork base
- `git merge-base --is-ancestor 67d6061 HEAD` → **YES** (the tree both baselines were measured on)
- `git merge-base --is-ancestor 6fab4ea HEAD` → **NO** (`origin/beta`'s drifted tip, +34 B uniform)

**F-138-02's 8 B / 2 B figure describes `origin/beta`'s tip, which is not in this branch's ancestry.**
It becomes relevant only when the drift merges in — Phase 144 / TEST-08's problem, as F-138-02's own
owner column says.

### Measured at the live branch tip

`pio run -e uno`, `-e uno328pb`, `-e leonardo` [VERIFIED: run this session, all SUCCESS]:

| env | flash used | flash total | RAM used | RAM total |
|---|---|---|---|---|
| `uno` | **23954** | 32256 | **1573** | 2048 |
| `uno328pb` | **24004** | 32384 | **1579** | 2048 |
| `leonardo` | **26016** | 28672 | **2014** | 2560 |

**Byte-identical to both `size_baseline.json` and `size_baseline_v131.json`** (whose `avr_targets`
blocks are themselves identical to each other). This independently confirms Phase 140's P1/P2 exact-zero
predictions still hold at the branch tip, and confirms F-140-02's mechanism: `-ffunction-sections`
`-fdata-sections` `-Wl,--gc-sections` [VERIFIED: `atmelavr/builder/frameworks/arduino.py:98,111`] drop
the unreferenced PROGMEM table and accessor entirely.

### The budget Phase 141 actually has

MERGE-05's band policy is "Leonardo flash must not grow; Uno-class flash growth ≤ 64 B; RAM unchanged"
(`check_size_baseline.py:17-18`), with `MERGE05_UNO_CLASS_FLASH_BAND = 64` (`:107`) and the comparison
made against **BASE-01**, named explicitly via `--baseline`:

| env | BASE-01 flash | live flash | delta | band | **growth budget remaining** |
|---|---|---|---|---|---|
| `uno` | 23932 | 23954 | +22 | 64 | **42 B** |
| `uno328pb` | 23976 | 24004 | +28 | 64 | **36 B** |
| `leonardo` | 26072 | 26016 | −56 | 0 (must not grow) | **56 B** (must stay ≤ 26072) |
| RAM (all three) | 1573 / 1579 / 2014 | identical | 0 | exactly 0 | **0 B — equality enforced on all three**, deliberately stronger than MERGE-05's text (`check_size_baseline.py:224-227`) |

**The binding constraint is `uno328pb` at 36 B.** `leonardo`'s 56 B is the second tightest; `uno`'s 42 B
is not binding.

The judged command:

```bash
cd /workspaces/firestarter && python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=<log> --avr-log uno328pb=<log> --avr-log leonardo=<log>
```

Never pass `native_trace_v131` or `native_params_v131` (or the new sixth env) to it — `NATIVE_ENVS` is
hardcoded to `("native", "native_nodevtools")` (`:100`) and `compare_native` does a bare dict lookup, so
an unknown env raises an uncaught `KeyError` → exit 1, a **false regression signal** (F-138-05, accepted
and not fixed). `check_build_warnings.py` exits 2 cleanly for the same env but has no baseline entry.

### Ingredients for the flash-delta prediction (state it before measuring — Phase 140's discipline)

**Adds:** `EPROM_PARAMS[]` 3 × 12 = 36 B PROGMEM + `EPROM_PARAM_KEYS[]` 3 B, both currently
gc-collected; `eprom_params_for()`'s linear-scan body; six `pgm_read_*` hoists; the per-byte loop with
its four predicates; the pure overprogram function; the ms/µs split helper plus **two** call sites
(`memory.cpp:329`, `eprom.cpp:283` — the erase site pays too, for LOOP-07's global claim); two new
`LOG_ERROR_ID_*` call sites; the `pins >= 32` branch; optionally the `verify_mode` final pass.

**Removes:** `program_mismatched_bytes()` (`:114-126`), `verify_and_update_mask()` (`:129-141`), the
`NUMBER_OF_RETRIES` block loop and its adaptive-growth arithmetic (`:163-179`, including a 32-bit
multiply and divide), two `LOG_*` call sites (`MSG_INFO_RETRIES`, `DBG_PULSE_DELAY_MISMATCH`), and the
`memset` at `:157`. `eprom_internal_ensure_regulator_enabled` (`:327-332`) is already gc-collected —
deleting it reclaims **0 B**; do not count it.

**RAM must be exactly 0 delta, and the removals help rather than hurt:** `mismatch_bitmask[DATA_BUFFER_SIZE / 8]`
(`:155`) is a stack array — **64 B on Uno-class** (512/8), **128 B on Leonardo** (1024/8). It does not
appear in the linker's static `ram_used` figure (it is stack, not `.bss`/`.data`), so removing it will
not *show* as a RAM win — but it removes 64/128 B of peak stack depth on parts with 475/546 B of static
headroom. Worth recording as a non-metric safety improvement. The new loop's locals (six hoisted table
values, `pulses`, `accumulated`, `org_delay`) are a handful of registers/stack slots, far less.

**Measurement discipline:** the baseline's own `meta.note` records that a default 2-minute timeout
truncates a cold toolchain build and silently contaminates the measurement — use
`pio run -t clean -e <env>` then `pio run -e <env>` with a long timeout, one uninterrupted invocation
per env. For AVR *flash/RAM* figures warm and cold agree; the warm/cold distinction in that note
concerns native *warning* counts only.

---

## Native test architecture — the sixth env, and two corrected blind spots

### `host_stubs_common.inc` (353 lines) — what it actually provides

CONTEXT.md names "two known blind spots: the stubs record no time (`delay()` unstubbed), so no test can
prove a timing change; and register-write elision is invisible unless `rurp_register_utils.h` is included
in the stubs." **Both are stale as of Phase 138 — the mechanisms to close them already exist in the
shared `.inc`.** This matters a great deal: it is the difference between LOOP-07 being testable and not.

| Opt-in guard | Location | What it gives | Status |
|---|---|---|---|
| `HOST_STUBS_RECORD_BUS` | `:47-57` | `(reg, data)` pair recorder | Phase 71, pre-existing |
| **`HOST_STUBS_REAL_REGISTER_UTILS`** | `:59-134` | Suppresses six stub symbols so the suite can `#include "rurp_register_utils.h"` **after** the `.inc` and drive **production's real cache-compare elision + latch-strobe sequencing**. Provides `clear_strobes()`, `strobe_count()`, `strobe_overflowed()`, `strobe_kind/pin/value(i)`, cap 512 | Phase 116 TRACE-01. **Closes blind spot 2** |
| **`HOST_STUBS_RECORD_TIMING`** | `:86-197` | `(kind, us, seq)` recorder with `clear_timings()`, `timing_count()`, `timing_kind/us/after_strobe(i)`, `timing_push()`, `TIMING_KIND_DELAY_US = 3` / `_DELAY_MS = 4`, cap 512. Each entry's `seq` is `s_strobe_count` **at push time**, so timings splice into the strobe stream positionally | Phase 138 PREP-03. **Substantially closes blind spot 1** |
| `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` | `:29-32` | Opt out of the default always-0 `rurp_read_data_buffer` so the suite can model chip read-back | Pre-existing |
| `HOST_STUBS_CUSTOM_VOLTAGE_MV` / `_HW_REVISION` | `:24-28` | per-suite ADC / revision overrides | Pre-existing |

**Every guard must be `#define`d BEFORE the `#include` of the `.inc`** — all of them are read at include
time (`test_trace_eprom_v131/host_stubs.cpp:33-37` restates this as a PITFALL). There is a fail-closed
`#error` at `:93-95`: `HOST_STUBS_RECORD_TIMING` requires `HOST_STUBS_REAL_REGISTER_UTILS`, because the
timing recorder's interleave key is `s_strobe_count`, which only exists inside that block. And
`HOST_STUBS_REAL_REGISTER_UTILS` already defines `HOST_STUBS_CUSTOM_HW_REVISION_BLOCK`, so a suite must
**not** additionally define the narrower hw-revision guard (`host_stubs.cpp:39-49` records this exact
collision as a correction to `test_val_eprom`'s pattern — do not copy `test_val_eprom` here).

### The corrected blind-spot statement, and why it makes LOOP-07 provable

**What a native test still cannot do:** measure elapsed wall-clock time. `delay()` and
`delayMicroseconds()` are free functions **defined by ArduinoFake's `FunctionFake.cpp`**, never stubbed
in the `.inc` (a definition there would be a duplicate-symbol link error), so no real time passes.
D-02's justification for counting pulse widths only therefore stands unchanged.

**What a native test CAN do, contrary to CONTEXT.md's framing:** observe **every argument** passed to
`delay()`/`delayMicroseconds()`, in order, interleaved with the register-strobe stream. The suite hooks
them in its own `setUp()` via fakeit `.AlwaysDo(lambda)` and forwards to `timing_push()`
[VERIFIED: `test_trace_eprom_v131.cpp:78-90`]:

```cpp
When(Method(ArduinoFake(), delayMicroseconds)).AlwaysDo([](unsigned int us) {
    timing_push(TIMING_KIND_DELAY_US, (uint32_t)us);
});
When(Method(ArduinoFake(), delay)).AlwaysDo([](unsigned long ms) {
    timing_push(TIMING_KIND_DELAY_MS, (uint32_t)ms);
});
```

**Therefore LOOP-07's global claim is directly assertable natively:**
*for every recorded `TIMING_KIND_DELAY_US` entry, `timing_us(i) <= 16383`.* And crucially,
ArduinoFake declares `virtual void delayMicroseconds(unsigned int)`
[VERIFIED: `.pio/libdeps/native/ArduinoFake/src/FunctionFake.h:23`] — on a 64-bit Linux host
`unsigned int` is **32-bit**, so an over-ceiling value arrives **intact and visible**, not truncated the
way it would be by AVR's 16-bit `unsigned int`. The oracle is real, not accidental.

D-06 says a test "can only assert the arithmetic, never the elapsed duration." Both halves are true, but
the *first* half understates the available coverage: a test can assert the **full emitted sequence** —
`delay(75)` then `delayMicroseconds(0)` for a 75000 µs request, in that order, at the right position
relative to the CE strobe. Plan for the stronger oracle; it costs the same env.

### The pulse-count oracle — `trace_readback_seed`

`test_trace_eprom_v131/host_stubs.cpp:122-149` supplies a stateful, index-keyed read-back model:

```c
extern "C" void trace_readback_reset();
extern "C" void trace_readback_seed(uint8_t idx, uint8_t target, uint8_t converge_after);
extern "C" uint8_t rurp_read_data_buffer() {   /* :143-149 */
    uint8_t idx = (uint8_t)(rurp_read_from_register(LEAST_SIGNIFICANT_BYTE) & 0x03);
    trace_readback_state_t* st = &s_trace_readback[idx];
    uint8_t result = (st->read_count < st->converge_after) ? 0xFF : st->target;
    st->read_count++;
    return result;
}
```

**This is the mechanism the new suite needs** — seed a byte to converge after N reads and assert the
loop emitted exactly N pulses. Three things to carry over:

1. **It is per-suite, not shared.** It lives in the trace suite's own `host_stubs.cpp`, so the new suite
   writes its own copy (and may widen the 4-entry array and the `& 0x03` mask).
2. **The index derivation is only valid because bits 0-7 are identity-mapped** for all three derived
   `bus_config`s — `mem_util_remap_address_bus`'s remap loop starts at `config.matching_lines` (≥ 11 for
   all three chips) and `static_high_mask`/`vpp_line` bits are all ≥ bit 8. The comment at `:105-121`
   derives this from source. Preserve the reasoning if the new suite reuses the trick, and re-derive it
   if it uses a different chip or a block not based at address 0.
3. **The read-count↔pulse-count mapping shifts by one under LOOP-06** — see §"Per-byte loop shape".
   The skip-check read consumes one `read_count` before the first pulse.

### Predicted RED of the existing trace fixture (so nobody mistakes it for a build break)

The pre-change fixture seeds `V131_SYNTHETIC_BLOCK = {0x3C, 0xFF, 0x55, 0xAA}` with
`converge_after = {0, 0, 2, 1}` (`test_trace_eprom_v131.cpp:241`, `:258-261`). Walking the **new** loop
against that model: byte 0 (`0x3C`, converge 0) → the skip-check read returns `0x3C` immediately →
**skipped, zero pulses**; byte 1 (`0xFF`) → skipped by LOOP-06's `0xFF` rule → **zero pulses**; byte 2
(`0x55`, converge 2) → 2 pulses; byte 3 (`0xAA`, converge 1) → 1 pulse. The old loop pulsed all four
bytes on pass 1 and ran three passes.

So the suite **compiles unchanged** (no signature it calls moves), keeps `RESPONSE_CODE_OK`, and fails
**only** on `v131_assert_stream_equals`'s ordered positional comparison. That is D-10's intended RED.
Pleasant side effect: the fixture's own synthetic block already contains a `0xFF` byte, so **LOOP-06 is
exercised by the pre-change fixture's own data** and the shrinkage is legible in the diff Phase 144 will
review.

### Capturing the new trace as a committed artifact (D-10 half (a))

The dump harness already exists and is the sanctioned route
[VERIFIED: `test_trace_eprom_v131.cpp:348-378`]. It is permanently behind `#ifdef EPROM_V131_TRACE_DUMP`,
which no env defines, and it **must be run by invoking the built binary directly** because `pio test`
swallows `printf`:

```bash
cd /workspaces/firestarter
# build the suite's env with the dump flag, then run the binary directly:
pio test -e <sixth_env> --without-testing        # or pio run, per the env's shape
./.pio/build/<sixth_env>/firestarter_native      # prints ready-to-paste initialisers
```

Its output format is `{kind, 0x%02X pin, 0x%02X value, %luUL us}, /* index */` per entry, with a
`##### <TAG> total=N strobe_overflow=0 timing_overflow=0` banner. Commit that output as the phase's
artifact; **do not** write it into `_shared/eprom_v131_expected.h` (that file's blob SHA is pinned by
`test_golden_trace_identity_eprom_v131.py`, and re-freezing is Phase 144 / TEST-06's job).

### The sixth env — copy `[env:native_params_v131]` wholesale

`platformio.ini:331-371` is the template, comments included. Its structure:

```ini
[env:native_<name>_v131]
; <HARD CONSTRAINT block — copy it, retargeted>
platform = native
test_framework = unity
test_filter =
	native/avr/<new_suite_dir>            ; ONE entry, never the 17-entry list
build_flags =
	${env:native.build_flags}             ; inherits -D HARDWARE_REVISION, -std=gnu++17, -I include
	-I test/native/avr/<new_suite_dir>
lib_deps =
	fabiobatsilva/ArduinoFake@^0.4.0
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>
test_build_src = yes
```

Three constraints the copied comment block must keep stating, all verified:

- **Never fold the suite into `[env:native]` or `[env:native_nodevtools]`.** Both are pinned at exactly
  **141 cases / 17 suites** by `size_baseline.json:native_envs` [VERIFIED: JSON read], asserted by
  `check_size_baseline.py`'s `compare_native`. Their `test_filter` lists (`:102-119` and `:207-224`) and
  `-I` lists must stay byte-identical to each other. `firestarter/CLAUDE.md` carries an explicit
  "Exception (Phase 140 D-11)" paragraph overriding its own general "add to both envs" instruction —
  extend that paragraph for the sixth env in the same change.
- **Never add it to `default_envs`** (`:16` = `uno, uno328pb, leonardo`) — `pio run` would try to link a
  `main()`-less target.
- **Never pass its name to either check script** (F-138-05: `KeyError` → exit 1 from
  `check_size_baseline.py`; exit 2 from `check_build_warnings.py`). Record its case/suite counts in the
  phase record instead, as `native_trace_v131` (5/1) and `native_params_v131` (**9/1**, per
  140-PARAM-TABLE-RECORD §7 — note this corrects the frozen baseline's absence of an entry) already do.
- **It runs in no CI leg of either repository** (F-140-11) — a **run-by-name obligation**. Never imply CI
  coverage for it. Also note existing precedent: `native_params_v131` and `native_trace_v131` are absent
  from the *live* `size_baseline.json:native_envs` (which holds only `native`, `native_nodevtools`,
  `native_pinmap_provisional`), while `native_trace_v131` **is** present in the frozen
  `size_baseline_v131.json`. Follow `native_params_v131`: record in the phase record only.

### Suite hygiene carried from existing suites

- **Fresh, zero-initialised handle per case.** `json_parse()` does not reset `pulse_delay`, `protocol`,
  `mem_size`, `vpp_mv` or `pins`, so a stale global handle leaks state between cases
  (`test_eprom_params_v131.cpp:70-85` is the pattern: a `make_handle()` returning `firestarter_handle_t h = {}`).
- **Reset the register cache deliberately.** `lsb_address`, `msb_address` and `control_register` are
  non-static globals initialised to `0xff` (`rurp_register_utils.h:12-14`) and persist across Unity
  cases in one binary; `0xff` ORs `CTRL_VPP_REGULATOR_ENABLE` into the first address write of any case
  that does not reset them (`test_trace_eprom_v131/host_stubs.cpp:80-93` supplies
  `reset_register_cache(lsb, msb, ctrl)`).
- **Drive `firestarter_operation_main` directly, not `_init`** (`test_trace_eprom_v131.cpp:243-253`
  explains why: `eprom_write_execute` enables the regulator itself on entry, and skipping `_init` keeps
  the capture scoped to the loop). This is also what makes LOOP-05's disable assertion non-vacuous.
- **Never re-assign `firestarter_get_data`/`firestarter_set_data`** — keeping the real
  `memory_get_data`/`memory_set_data` in the path is what captures the verify read's own bus activity
  (D-05's rationale, and the trace suite's "R2 over R1" choice).
- **Mock `millis`/`micros`** as well as the two delays; ArduinoFake **SIGABRTs on any unmocked call**
  (`test_sdp_harness.cpp:85-97` records this).
- **Never use `TEST_IGNORE_MESSAGE`** to park a RED case — an IGNORED result does not demonstrate RED
  (`platformio.ini:100-101`).

---

## Architecture Patterns

### System Architecture Diagram

```
                          HOST (firestarter_app) — unchanged this phase
   chip_database.json ──► pulse_duration ──► JSON "pulse-delay" ──┐
   pinout ────────────► bus_config, pin-count ───────────────────┤
   algorithm (protocol_id) ───────────────────────────────────────┤
                                                                  │ 250000 baud, COBS
                                       ═══════════════════════════▼═══════════════════
                                        FIRMWARE  src/json_parser.c
                                          extract_long → handle->pulse_delay (uint32, UNCLAMPED)
                                          → handle->protocol, ->pins, ->data_buffer[], ->data_size
                                                       │
                            src/proms/memory.cpp:115 ──▼── configure_memory dispatch
                                                       │  (protocol ∈ {0x07,0x08,0x0B})
                                    ┌──────────────────▼───────────────────────┐
                                    │ configure_eprom  (eprom.cpp:41-77)       │
                                    │  · install write_init / write_execute    │
                                    │  · pulse_delay == 0 fallback  [:70-76]   │
                                    │  · eprom_params_for(protocol)  ◄── NEW   │──► NULL ► fail closed
                                    │  · D-03 pre-flight refusal    ◄── NEW   │──► pulse > cap ► fail closed
                                    └──────────────────┬───────────────────────┘   (before ANY high voltage)
                                                       │
              src/eprom_operations.cpp:115 ────────────▼──── per 512/1024 B block, streamed
                                    ┌──────────────────▼───────────────────────────────────┐
                                    │ eprom_write_execute        ← REWRITTEN THIS PHASE     │
                                    │                                                      │
                                    │ ONCE PER BLOCK (LOOP-08):                            │
                                    │   regulator idempotency guard → assert route         │
                                    │   → delay(500) settle                                │
                                    │   → pins >= 32 guarded branch (D-09)                 │
                                    │   → hoist 6 table columns via pgm_read_*             │
                                    │                                                      │
                                    │ PER BYTE:                                            │
                                    │   0xFF? ──yes──► skip (LOOP-06)                      │
                                    │   read == expected? ──yes──► skip (LOOP-06)          │
                                    │        │no                                           │
                                    │        ▼  ┌──────────── fixed width, never grown ───┐ │
                                    │      pulse ─► verify ─► match? ──yes──► overprogram  │ │
                                    │        ▲                  │no          (factor>0)   │ │
                                    │        │                  ▼                          │ │
                                    │        │        pulses >= max_pulses? ──► FAIL 0xBD   │ │
                                    │        │        accumulated >= cap?  ──► FAIL 0xBE    │ │
                                    │        └──────────────────┘                          │ │
                                    │                                                      │
                                    │ END OF BLOCK: verify_mode == PLUS_FINAL → final pass  │
                                    └──────┬────────────────────────┬──────────────────────┘
                                           │ success                │ FAIL
                                           │                        ▼ disable route, emit ID,
                                           │                          response_code = ERROR
                    ┌──────────────────────▼────────────────────────▼────────────┐
                    │ memory.cpp primitives (D-05 — reused, never duplicated)     │
                    │  memory_set_data :249  chip_input → remap(WRITE)            │
                    │      → set_address → 3µs → chip_enable                      │
                    │      → SAFE DELAY(pulse_delay) ◄── LOOP-07 site 1           │
                    │      → chip_disable                                         │
                    │  memory_get_data :203  chip_output → remap(READ)            │
                    │      → set_address → settling → chip_enable → strobe → latch │
                    └──────────────────────┬─────────────────────────────────────┘
                                           ▼
                    mem_util_set_address :175 ─► calculate_top_address_register :159
                                           │      address bits | (cached CONTROL & preserve mask)
                                           │      preserve mask += DROP  ONLY IF pins < 32  ◄── D-09
                                           ▼
                    rurp_write_to_register :24 ─► cache-compare ELIDES if unchanged
                                           ▼      P1 set→clear ► delayMicroseconds(4)
                                    rurp_internal_write_to_register ─► shift register + LE strobe
                                           ▼
                    rurp_map_ctrl_reg_for_hardware_revision ─► per-revision physical bit layout

  ON ANY EXIT: eprom_operations returns false ─► command_done() (firestarter.cpp:162)
               ─► chip_disable + CONTROL = 0x00 + LSB/MSB = 0   (orthogonal HV backstop)
```

### Repository layout touched by this phase

```
/workspaces/                                  ← META repo (tracks .planning/ + tools/)
├── tools/catalog/
│   ├── messages.toml                          ← EDIT: two new [[messages]] blocks (canonical)
│   ├── codegen.py                             ← unchanged (validator + emitter)
│   └── sync_to_subrepos.sh                    ← RUN after the edit
└── .planning/phases/141-per-byte-program-loop/ ← plans, summaries, phase record, new-trace artifact

/workspaces/firestarter/                       ← FIRMWARE submodule
├── src/proms/eprom.cpp                        ← REWRITE the write path; add D-03 refusal
├── src/proms/memory.cpp                       ← ADD the safe delay helper; route :257 through it
├── include/memory_utils.h                     ← DECLARE the helper (beside mem_util_*)
├── include/messages.h                         ← GENERATED (do not hand-edit)
├── tools/catalog/{messages.toml,codegen.py}   ← SYNCED copies (do not hand-edit)
├── platformio.ini                             ← ADD the sixth [env:native_*_v131]
├── tests/test_protocol_branch_inventory.py    ← EDIT :446's pinned line list
├── tests/golden/protocol_branch_inventory.json← RE-DERIVE (never hand-edit a line/tier/count)
├── test/native/avr/<new_suite>/               ← NEW suite: test_*.cpp + host_stubs.cpp
├── test/native/avr/_shared/host_stubs_common.inc ← extend only if a new rurp_* symbol appears
└── CLAUDE.md                                  ← UPDATE the 0x07/0x08/0x0B Algorithm Handlers rows

/workspaces/firestarter_app/                   ← HOST submodule — GENERATED FILES ONLY
├── firestarter/messages.py                    ← GENERATED (ruff-clean; never normalize)
└── tools/catalog/{messages.toml,codegen.py}   ← SYNCED copies
```

### Pattern 1 — Fail closed with zero hardware side effects, before any high voltage

**What:** every refusal happens in `configure_eprom`, which runs before any operation pointer is invoked
and therefore before any register carries high voltage.
**When to use:** D-03's `energy_cap_us > 0 && pulse_delay > energy_cap_us` refusal, and the
`eprom_params_for() == NULL` refusal (Phase 140 D-05).
**Example** — the in-tree idiom, from the generic dispatch guard:

```c
// Source: firestarter/src/proms/memory.cpp:67-71 (Phase 124 MERGE-04)
if (rurp_pinmap_refuses(handle->cmd)) {
    LOG_ERROR_ID_U8(MSG_ERR_NOT_SUPPORTED, (uint8_t)handle->cmd);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;                     // operation pointers stay NULL; nothing is energised
}
```

Note `configure_eprom` currently returns `void` and installs pointers **before** the fallback switch
(`:44-67`, then `:69-76`). D-03's refusal must run **after** the fallback switch has resolved
`pulse_delay` (otherwise a `0` pulse compares as "not greater than the cap" vacuously) and must leave the
handle in the refused shape. Setting `response_code = RESPONSE_CODE_ERROR` is what `eprom_write_init`
already checks at `:96`.

### Pattern 2 — `org_delay` save/restore for a one-off pulse width (D-07)

**What:** temporarily overwrite `handle->pulse_delay`, make exactly one primitive call, restore.
**When to use:** the overprogram pulse. Never for the base pulse — LOOP-01 requires a fixed width.

```c
// Source: firestarter/src/proms/eprom.cpp:161,172 (the existing idiom)
uint32_t org_delay = handle->pulse_delay;
...
handle->pulse_delay = org_delay;        // restore on EVERY exit path, including failures
```

### Pattern 3 — Opt-in native recorder layers, composed in the right order

```cpp
// Source: firestarter/test/native/avr/test_trace_eprom_v131/host_stubs.cpp:61-78
#define HOST_STUBS_REAL_REGISTER_UTILS      /* MUST precede the include */
#define HOST_STUBS_RECORD_TIMING            /* requires the above (#error enforces it) */
#define HOST_STUBS_CUSTOM_READ_DATA_BUFFER  /* so this file can supply a stateful model */
#include "../_shared/host_stubs_common.inc"
#include "rurp_register_utils.h"            /* AFTER the .inc — real elision, not a replica */
```

### Anti-Patterns to Avoid

- **Dereferencing a PROGMEM field directly** (`row->max_pulses`) — compiles, passes every native test,
  returns RAM garbage on AVR. Always `pgm_read_byte`/`pgm_read_dword`.
- **Re-reading PROGMEM inside the per-byte loop** — hoist once per block.
- **Implementing D-01's prose literally** (`if (accumulated + pulse > cap) { emit; break; }`) — off by
  one against D-01's own worked example. Use `while (accumulated < cap)`.
- **Branching on `protocol` for the DIP32 case** — adds a fourth tier-1 site and fails the D-13 gate.
  Branch on `handle->pins >= 32`.
- **Asserting "no CONTROL strobe during a verify read"** — false; the register is rewritten (and usually
  elided) on every address change.
- **Asserting HV-disabled *after* the command completes** — `command_done()` zeroes the register
  regardless, so the assertion passes vacuously.
- **Adding a new `.cpp` under `src/`** without updating `platform/py32f071/CMakeLists.txt` — RED in a
  CI-covered gate. Prefer D-06's placement.
- **Pairing `<Arduino.h>` with the `avr/pgmspace.h` shim in one TU** — 14 macro-redefinition warnings
  against a watermark with **zero headroom** (F-140-01).
- **Hand-editing `messages.h`, `messages.py`, or either sub-repo's `tools/catalog/` copy** — all
  generated or synced. Author in meta, run the sync script.
- **Re-freezing `_shared/eprom_v131_expected.h`** — Phase 144 / TEST-06 owns it; its blob SHA is pinned.
- **Running `pio` with cwd `/workspaces`** — see §"Environment Availability". It crashes.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Programming pulse + address remap | an EPROM-local write path | `handle->firestarter_set_data` → `memory_set_data` (`memory.cpp:321`) | D-05. A duplicate bypasses `mem_util_remap_address_bus`, which encodes per-chip bus config: address-line reordering, `rw_line`, `vpp_line`, `static_high_mask`. Getting it wrong energises the wrong socket pin |
| Verify read | a local read using `rurp_read_data_buffer` | `handle->firestarter_get_data` → `memory_get_data` (`memory.cpp:207`) | Same remap dependency, plus the clamped settling/strobe knobs (`:219-235`) |
| Control-register read-modify-write | your own mask arithmetic | `handle->firestarter_set_control_register` → `eprom_internal_set_control_register` (`eprom.cpp:319`) | It performs the `CTRL_VPE_ENABLE` → `CTRL_VPP_P1_ENABLE` remap for `using_p1_as_vpp` parts. Bypassing it routes VPE to the wrong pin on DIP32/28 P1 parts |
| Per-revision control-register bit layout | a `#define` for "the drop bit" | `rurp_write_to_register` → `rurp_map_ctrl_reg_for_hardware_revision` (`rurp_hw_rev_utils.h:15`) | Logical bit ≠ physical bit, and the mapping differs across Rev 0/1 and Rev 2.x. See the DIP32 truth table |
| Long delay on AVR | `delay(us/1000); delayMicroseconds(us%1000);` inline at each site | one helper in `memory_utils.h`/`memory.cpp`, applied at both sites (D-06) | LOOP-07's claim is global. Two inline copies is two places to get the `us <= 16383` short-circuit and the `%`/`/` split wrong, and a new TU costs a CMake manifest edit |
| Table lookup | a `switch (protocol)` in the loop | `eprom_params_for()` (`eprom_params.cpp:51`) | TABLE-05: a second switch IS the second dispatch selector. The D-13 gate mechanically catches it, and `test_params_table_has_no_second_selector` asserts `switch_statements == 0` in that TU |
| Message wording / IDs | a `#define` in `eprom.cpp` or a PROGMEM string | `tools/catalog/messages.toml` + `sync_to_subrepos.sh` | The host holds the wording; firmware holds only IDs. A hand-added `#define` diverges the moment codegen next runs |
| Register-strobe recording in tests | a hand-maintained replica of the latch sequence | `HOST_STUBS_REAL_REGISTER_UTILS` (`host_stubs_common.inc:59`) | A replica silently drifts from `rurp_write_to_register`'s real cache-elision — and elision is exactly the bug class the FM1608 todo documents |
| Timing capture in tests | wrapping delays in your own counter | `HOST_STUBS_RECORD_TIMING` + the `.AlwaysDo` hook | Already provides `(kind, us, seq)` with strobe-interleave positioning, plus overflow flags |
| Chip read-back convergence in tests | pointer-swapping `firestarter_get_data` | `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` + a `converge_after` model | A pointer swap removes the real `memory_get_data` from the trace, losing the verify read's own bus activity (the trace suite's recorded "R2 over R1" choice) |
| Re-deriving the D-13 golden | hand-editing lines/tiers/counts | import `_extract_predicates` from the test module | `meta.how_to_update` names this the only sanctioned route; hand-editing a line number to make a surprise disappear is the exact failure the gate exists to prevent |

**Key insight:** in this codebase the per-chip electrical configuration lives entirely in
`bus_config` + the control-register mapping layers, and *every* shortcut past
`memory_set_data`/`memory_get_data`/`set_control_register` silently discards part of it. The loop's job is
cadence and bookkeeping — pulse counting, budget arithmetic, skip logic, diagnosis — and nothing else.
Every hardware detail it appears to need is already owned by a lower layer that Phase 141 must not
reimplement.

---

## Runtime State Inventory

This is a refactor phase (a write-path rewrite plus a cross-repo catalog change), so the canonical
question applies: **after every file in all three repos is updated, what runtime systems still have the
old behaviour cached, stored, or registered?**

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | **None.** No database, datastore, or persisted record keys on any string or value this phase changes. `chip_database.json` is explicitly out of scope (TABLE-05) and is read-only input. Arduino EEPROM holds `rurp_configuration_t` (R1/R2 resistor values, `hw_revision`) — **verified unrelated**: `grep -rn "pulse\|retries\|max_pulses" src/rurp_config_utils.cpp src/boards/rurp_config_storage_eeprom.cpp` returns nothing. No config-storage migration is needed | none |
| **Live service config** | **None.** This project has no service whose configuration lives outside git — no n8n, no Datadog, no Cloudflare. The only external system is GitHub Actions, whose workflows are tracked (`.github/workflows/{build,beta-build,py32f071}.yml`) | none |
| **OS-registered state** | **None.** No Task Scheduler entry, pm2 process, launchd plist, or systemd unit references anything this phase changes. The bench boards are USB serial devices with no persistent host-side registration | none |
| **Secrets / env vars** | **None new.** Three pre-existing seams are read at import/binding time and are unchanged by this phase: `FIRESTARTER_SIZE_BASELINE` (both check scripts), `FIRESTARTER_BRANCH_SCAN_SOURCE` / `FIRESTARTER_BRANCH_SCAN_PARAMS_SOURCE` (D-13 gate, bind at **import** — a planted-violation run must set them in a **child process**, never via monkeypatch: `test_protocol_branch_inventory.py:51-66`), and `FIRESTARTER_META_ROOT` / `FIRESTARTER_FW_ROOT`. **Do not leave any of them set** in a shell that later runs the real gate | none — but unset the scan seams after any planted run |
| **Build artifacts / installed state** | **THREE items, all real.** (1) **`.pio/build/{uno,uno328pb,leonardo,native,native_nodevtools,native_params_v131,native_trace_v131}/` are all warm** — a stale object file will silently produce a wrong flash figure. (2) **The programmed EPROM itself.** A chip left half-written by an aborted `max_pulses` failure carries partially-cleared bits; on a UV part those bits **cannot be restored without UV erase**, and on a `0x07` EEPROM-class part they need an erase cycle. This is physical state no code change reverts. (3) **Flashed firmware on the three bench boards** still runs the pre-change loop until re-flashed | (1) `pio run -t clean -e <env>` before any measurement that will be recorded as evidence; (2) Phase 145's bench scope — use sacrificial or erasable parts when exercising the failure path; (3) `fw --install` per board before Phase 145, remembering it flashes the **attached** board and ignores `--board` |

**Additional non-obvious carry-over:** the D-13 golden and `size_baseline.json` are themselves *recorded
runtime state* about a tree that this phase changes. Both are covered above under §"Gates"; neither is a
runtime system, but both will report a stale truth until updated in the same commit as the code.

---

## Common Pitfalls

### Pitfall 1 — PROGMEM dereference: passes every native test, garbage on AVR
**What goes wrong:** `row->max_pulses` instead of `pgm_read_byte(&row->max_pulses)`.
**Why it happens:** `rurp_platform_compat.h:35-45` defines `pgm_read_*` as plain dereferences on
non-AVR targets, so the direct form is *correct* on the host. Every native suite passes. On AVR the
pointer is a program-space address read through a data-space instruction and returns whatever RAM lives
at that numeric address.
**How to avoid:** copy the accessor block from `test_eprom_params_v131.cpp:179-184` verbatim; hoist all
six reads to the top of `eprom_write_execute`.
**Warning signs:** a native suite that is green while a bench run reports absurd pulse counts, an
instant `max_pulses` failure, or a `max_pulses` of 0. **No native test can catch this** — the only
oracles are code review and a bench run (Phase 145).

### Pitfall 2 — The energy-cap off-by-one
**What goes wrong:** 101 pulses at 500 µs instead of 100, contradicting D-01's own example.
**Why it happens:** D-01's prose ("when the next full-width pulse would *cross* the cap, EMIT that pulse,
then stop") reads naturally as `if (accumulated + pulse > cap) { emit; break; }`, which fires one extra
pulse at the exact-division boundary that all three shipped `0x0B` widths hit.
**How to avoid:** `while (accumulated < energy_cap_us)` — emit iff the total *before* the pulse is
strictly below the cap. Verify against the six-row table in §"Energy-cap arithmetic".
**Warning signs:** a `0x0B` test expecting 100 pulses at 500 µs sees 101; the trace has one more
`us=500` entry than the arithmetic predicts.

### Pitfall 3 — The `0` sentinel in `energy_cap_us`
**What goes wrong:** `0x07`/`0x08` abort after the first pulse.
**Why it happens:** `energy_cap_us = 0` means **uncapped** (`eprom_params.h:53`); an unguarded
`accumulated >= energy_cap_us` is true after the first pulse.
**How to avoid:** always `if (energy_cap_us && accumulated >= energy_cap_us)`. The same sentinel shape
appears in `pulse_delay == 0` (means "use the fallback") and `read_strobe_us == 0` (means "use 3 µs") —
this codebase uses `0`-as-sentinel consistently, so read every zero as a possible sentinel.
**Warning signs:** every `0x07`/`0x08` byte fails at exactly 1 pulse.

### Pitfall 4 — The read-count↔pulse-count off-by-one in the new suite
**What goes wrong:** the suite asserts N pulses and sees N−1, or vice versa.
**Why it happens:** the pre-change loop pulsed unconditionally on pass 1 and read once per pass; the new
loop reads **first** (LOOP-06's skip check) and then pulses. Reusing `trace_readback_seed`'s
`converge_after` (which counts **reads**) without adjusting shifts the mapping by one.
**How to avoid:** state the mapping in a comment in the suite — `converge_after = N` means the byte
matches on read `N+1`, i.e. after **N pulses**, given exactly one skip-check read. Seed one byte with
`converge_after = 0` as a control: it must produce **zero** pulses (LOOP-06).
**Warning signs:** every expected pulse count is uniformly off by one — a signature of a mapping bug
rather than a loop bug.

### Pitfall 5 — Vacuous LOOP-05 disable assertion
**What goes wrong:** the test passes even if `eprom_write_execute` disables nothing.
**Why it happens:** `command_done()` (`firestarter.cpp:162-171`) does
`rurp_write_to_register(CONTROL_REGISTER, 0x00)` on **every** command exit, success or failure.
**How to avoid:** drive `handle->firestarter_operation_main` directly (never the whole command) and
assert on the recorded CONTROL strobes, with a paired negative control that shows the assertion can
fail. This is D-15's rule applied locally: plant the violation (comment out the disable), watch it go
RED, then restore.
**Warning signs:** the assertion passes on the very first run without ever having been seen RED.

### Pitfall 6 — Native watermark has zero headroom
**What goes wrong:** `check_build_warnings.py` goes RED on 14 new macro-redefinition warnings.
**Why it happens:** any TU that includes **both** `<Arduino.h>` and the `avr/pgmspace.h` host shim emits
exactly 14 warnings (F-140-01), and the `native`/`native_nodevtools` watermark sits at exactly **1166**
with no slack.
**How to avoid:** the new suite's `.cpp` may include `<Arduino.h>` + `<ArduinoFake.h>` (existing suites
do); the constraint bites production TUs. `eprom_params.cpp` and `not_implemented.cpp` are the two
`src/proms/` TUs that deliberately omit `<Arduino.h>` — if the delay helper's implementation needs
`delay()`/`delayMicroseconds()`, note that `memory.cpp` **already** includes `<Arduino.h>` (`:10`), so
D-06's placement costs nothing here.
**Warning signs:** `pio test -e native 2>&1 | grep -cE 'warning: *"[^"]+" +redefined'` returns > 1166.

### Pitfall 7 — Re-deriving the golden but not the assertion literal
**What goes wrong:** two of the three broken D-13 tests go green, and CI still fails.
**Why it happens:** `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines` compares against a
hard-coded `[71, 145, 218]` in the **test module** (`:446`), not against the JSON.
**How to avoid:** update `:446` in the same change, keeping the count at **three**.
**Warning signs:** `test_branch_sites_match_the_recorded_inventory` passes while
`test_exactly_three_protocol_keyed_sites_at_the_pinned_lines` fails naming the new lines.

### Pitfall 8 — Committing the golden's blob SHA in a separate commit
**What goes wrong:** `test_blob_shas_match_the_recorded_inventory` fails on the first of the two commits.
**Why it happens:** it compares against `git rev-parse HEAD:<path>`, which is a property of the commit.
**How to avoid:** `git hash-object src/proms/eprom.cpp` **before** committing yields the identical SHA
[VERIFIED this session]. Write it into the golden, then commit source + golden **together**.

### Pitfall 9 — `pio` is unusable from the repo root
**What goes wrong:** every `pio` command dies with
`InvalidProjectConfError: … 'section 'platformio' already exists'`.
**Why it happens:** `/workspaces/platformio.ini` is a gitignored devcontainer IDE convenience file
generated by `.devcontainer/gen-platformio-ini.py`; the generator emits its own `[platformio]` block and
then concatenates `firestarter/platformio.ini`, which has one too — **two `[platformio]` sections**
(root file lines 7 and 26). `pio -d <dir>` and `-c` do **not** help: PlatformIO resolves `core_dir` from
the cwd's config before honouring either flag [VERIFIED: both attempted this session].
**How to avoid:** every `pio` invocation must have cwd `/workspaces/firestarter`. In an `<automated>`
verify block that means a leading `cd /workspaces/firestarter && …`.
**Warning signs:** a traceback ending in `configparser.DuplicateSectionError`.

> ⚠️ **Compounding hazard for the planner.** This project has a recorded prior failure where the planner
> wrote literal `&amp;&amp;` into `<automated>` blocks, making 30/37 verification legs unrunnable while
> self-reporting `bash -n` PASS. Every `pio` leg in Phase 141's plans now **requires** an `&&`. After
> writing the plans, verify the bytes on disk — e.g.
> `grep -c 'amp;' .planning/phases/141-per-byte-program-loop/141-*-PLAN.md` must return 0 — and run each
> block through `bash -n` reading the file, not a re-typed copy.

### Pitfall 10 — A gate leg that has only ever passed (D-15)
**What goes wrong:** a new assertion is believed because it is green, but it was never reachable.
**Why it happens:** a locator that resolves to the wrong file, or an env seam left set, makes a gate scan
nothing and exit 0. `check_permitted_claims.py`'s `_HERE`-resolves-to-the-wrong-phase-dir bug and
`test_protocol_branch_inventory.py`'s own `test_default_targets_resolve_inside_this_repository` (`:512-543`,
written specifically to close that class) are the in-tree precedents.
**How to avoid:** plant the violation, watch each new leg go RED for the reason it was planted (never a
decode/import/path error), then fix **the locator, not the assertion**. Phase 140 ran 12 planted-RED
runs across three gates and recorded each transcript — match that discipline.

### Pitfall 11 — Restoring `pulse_delay` on the failure paths
**What goes wrong:** a `max_pulses` or energy-cap failure inside the overprogram save/restore window
leaks a modified `pulse_delay` into the handle.
**Why it happens:** the existing loop restores only on success (`eprom.cpp:172`) because the failure path
fell into a torn-down command. With D-07's save/restore added per byte, the window is per byte.
**How to avoid:** never mutate `handle->pulse_delay` except inside the overprogram block, and restore
immediately after the single call — no failure exit can occur between them.

### Pitfall 12 — Assuming the sixth env is covered by CI
**What goes wrong:** the phase record implies coverage that does not exist; a later green CI run is
mistaken for proof the suite still passes.
**Why it happens:** neither `build.yml` nor `beta-build.yml` runs any `pio test` env beyond `native` and
`native_nodevtools` (F-140-11) [VERIFIED: workflow read].
**How to avoid:** state the run-by-name obligation explicitly in the phase record, with the exact
command and the observed case/suite counts, exactly as 140-PARAM-TABLE-RECORD §7 does.

---

## Code Examples

### 1. The safe delay helper (LOOP-07 / D-06)

```c
// firestarter/include/memory_utils.h — beside the other mem_util_* declarations (:17-22)
/*
 * 32-bit-safe microsecond delay. AVR's delayMicroseconds() takes a 16-bit
 * `unsigned int` and its 16 MHz arm computes `us <<= 2`, which overflows at
 * 16384 -- so any request above 16383 us silently produces a MUCH SHORTER
 * delay (20000 -> ~3615 us), never a longer one. Splits into whole
 * milliseconds via delay() (unsigned long, 32-bit) plus the sub-ms remainder.
 * Source: framework-arduino-avr 5.3.0 cores/arduino/wiring.c:120, :167-183.
 */
void mem_util_delay_us(uint32_t us);

/* Pure, testable split -- exposed so a native case can assert the arithmetic
 * without needing elapsed time (native stubs record no time; see
 * test/native/avr/_shared/host_stubs_common.inc:136-150). */
void mem_util_split_delay(uint32_t us, uint32_t* out_ms, uint16_t* out_us);
```

```c
// firestarter/src/proms/memory.cpp — implementation
#define MEM_UTIL_DELAY_US_MAX 16383UL   /* AVR delayMicroseconds() accurate ceiling */

void mem_util_split_delay(uint32_t us, uint32_t* out_ms, uint16_t* out_us) {
    if (us <= MEM_UTIL_DELAY_US_MAX) {
        *out_ms = 0;
        *out_us = (uint16_t)us;         /* <= 16383, fits and is accurate */
        return;
    }
    *out_ms = us / 1000UL;
    *out_us = (uint16_t)(us % 1000UL);  /* <= 999, always under the ceiling */
}

void mem_util_delay_us(uint32_t us) {
    uint32_t ms; uint16_t rem;
    mem_util_split_delay(us, &ms, &rem);
    if (ms) { delay(ms); }              /* unsigned long -- 32-bit safe */
    if (rem) { delayMicroseconds(rem); }
}
```

Then both over-ceiling-capable sites route through it:

```c
// firestarter/src/proms/memory.cpp:329  (was: delayMicroseconds(handle->pulse_delay);)
mem_util_delay_us(handle->pulse_delay);

// firestarter/src/proms/eprom.cpp:283   (was: delayMicroseconds(handle->pulse_delay);)
mem_util_delay_us(handle->pulse_delay);
```

Boundary cases a native case should cover, all assertable through `mem_util_split_delay` directly plus
the timing recorder for `mem_util_delay_us`:

| `us` | `ms` | `rem` | emitted calls | note |
|---|---|---|---|---|
| 0 | 0 | 0 | none | both `if`s skip; also matches `delayMicroseconds`'s own `us <= 1` short-circuit |
| 100 | 0 | 100 | `delayMicroseconds(100)` | the modal shipped width |
| 16383 | 0 | 16383 | `delayMicroseconds(16383)` | **the exact ceiling — must NOT split** |
| 16384 | 16 | 384 | `delay(16)`, `delayMicroseconds(384)` | **first value that must split** |
| 50000 | 50 | 0 | `delay(50)` only | `0x0B`'s energy cap as a single pulse |
| 75000 | 75 | 0 | `delay(75)` only | the overprogram clamp |
| 65535 | 65 | 535 | `delay(65)`, `delayMicroseconds(535)` | minipro's `-o pulse=` ceiling |
| 4294967295 | 4294967 | 295 | `delay(4294967)`, `delayMicroseconds(295)` | `uint32_t` max — no overflow in `/` or `%` |

Note the split rule is deliberately **`> 16383` splits, `<= 16383` does not**. Splitting everything
would change the emitted trace for every existing pulse width and destroy Phase 144's ability to
attribute the trace diff to *cadence*.

### 2. Table read with fail-closed handling (Phase 140 D-05 + PROGMEM)

```c
// firestarter/src/proms/eprom.cpp — inside configure_eprom, AFTER the :70-76 fallback switch
const eprom_params_t* row = eprom_params_for(handle->protocol);
if (row == NULL) {
    /* Unrecognised protocol: fail closed with zero hardware side effects.
     * Phase 140 D-05 -- never fall back to EPROM_PARAMS[0], which would route
     * 13V through the drop resistor for an unknown part (T-140-17). */
    LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}

/* D-03 pre-flight refusal: a pulse wider than the row's energy budget would
 * apply a single up-to-cap VPE pulse and then report a *verify* failure.
 * Refuse BEFORE any high voltage is enabled. Keyed on energy_cap_us, never on
 * protocol -- no new tier-1 site (D-11). */
uint32_t energy_cap_us = pgm_read_dword(&row->energy_cap_us);
if (energy_cap_us > 0 && handle->pulse_delay > energy_cap_us) {
    LOG_ERROR_ID_U32(MSG_ERR_..., handle->pulse_delay);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}
```

### 3. Sixth-env suite skeleton (the `setUp` that makes both oracles work)

```cpp
// firestarter/test/native/avr/<new_suite>/<new_suite>.cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
extern "C" { #include "memory.h" }
#include "firestarter.h"
#include "eprom_params.h"

using namespace fakeit;

extern "C" void timing_push(uint8_t kind, uint32_t us);
extern "C" void clear_strobes(); extern "C" int strobe_count();
extern "C" void clear_timings(); extern "C" int timing_count();
extern "C" uint32_t timing_us(int i); extern "C" uint8_t timing_kind(int i);
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);
extern "C" void readback_reset();
extern "C" void readback_seed(uint8_t idx, uint8_t target, uint8_t converge_after);

enum { TIMING_KIND_DELAY_US = 3, TIMING_KIND_DELAY_MS = 4 };  /* mirrors the .inc; separate TU */

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();

    /* THE hooks: turn every mocked delay into a recorded timing entry. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysDo([](unsigned int us) {
        timing_push(TIMING_KIND_DELAY_US, (uint32_t)us);
    });
    When(Method(ArduinoFake(), delay)).AlwaysDo([](unsigned long ms) {
        timing_push(TIMING_KIND_DELAY_MS, (uint32_t)ms);
    });
    /* ArduinoFake SIGABRTs on any unmocked call -- mock these even if unused. */
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);

    clear_strobes();
    clear_timings();
    reset_register_cache(0x00, 0x00, 0x00);   /* globals default to 0xff and leak across cases */
}
```

### 4. The LOOP-07 global assertion, stated as a test

```cpp
/* LOOP-07: no call path reaches delayMicroseconds() above its 16383 us ceiling.
 * ArduinoFake declares delayMicroseconds(unsigned int) -- 32-bit on this host
 * (FunctionFake.h:23) -- so an over-ceiling value arrives INTACT and visible,
 * not truncated the way AVR's 16-bit unsigned int would truncate it. */
void test_no_recorded_us_delay_exceeds_the_avr_ceiling(void) {
    /* ... drive a write block with pulse_delay = 50000 (over-ceiling) ... */
    TEST_ASSERT_TRUE_MESSAGE(timing_count() > 0, "non-vacuity: no timing entries recorded");
    for (int i = 0; i < timing_count(); i++) {
        if (timing_kind(i) != TIMING_KIND_DELAY_US) continue;
        char msg[80];
        snprintf(msg, sizeof msg, "entry %d: delayMicroseconds(%lu) exceeds 16383",
                 i, (unsigned long)timing_us(i));
        TEST_ASSERT_TRUE_MESSAGE(timing_us(i) <= 16383UL, msg);
    }
}
```

Pair it with a **planted-violation run** (D-15): temporarily call `delayMicroseconds(20000)` directly and
confirm this case goes RED naming entry index and value — otherwise the loop body may never have executed.

---

## State of the Art

"Current" here means the state of *this codebase and its own published claims*, not an external
ecosystem — this is bespoke AVR firmware with no third-party algorithm library in play.

| Old approach | Current approach | When changed | Impact on Phase 141 |
|---|---|---|---|
| Block-level mismatch-mask retry with **adaptive pulse growth** (`pulse = org + org*retries/20`, 20 passes) | Per-byte fixed-width pulse→verify with a per-byte pulse count and a named budget | **This phase** (LOOP-01/LOOP-02) | The whole premise. The adaptive formula has no datasheet basis in any of the three families' primary datasheets |
| `mem_type` / `type` legacy dispatch axis alongside `protocol` | `protocol_id` is the **sole** dispatch key end to end | v1.20, Phases 105-107 | TABLE-05 still binding: the loop reads the table, never `switch (protocol)`. Mechanically enforced by the D-13 gate |
| Per-protocol pulse constants in firmware | Pulse width is a **database datum** (`pulse_duration` → wire `pulse-delay`); firmware keeps only a `pulse_delay == 0` fallback | v1.31 milestone D-01 / Phase 140 TABLE-02 | The loop must never introduce a pulse-width column or constant under any name |
| Algorithm shape implicit in handler code | Algorithm shape is a `const` PROGMEM table keyed on `protocol_id` | Phase 140 (TABLE-01) | Phase 141 is the **first `src/` consumer** — the table's real flash cost lands here (F-140-02) |
| `messages.h` carried PROGMEM format strings | `messages.h` is **ID-only `#define`s**; wording lives host-side in `messages.py` | v1.2 catalog / codegen | Two new IDs cost call sites, not PROGMEM strings (D-04's cost correction) |
| Native suites could not observe timing | `HOST_STUBS_RECORD_TIMING` records every `delay`/`delayMicroseconds` **argument** with strobe-interleave position | **Phase 138 PREP-03** | Makes LOOP-07's global claim natively assertable — CONTEXT.md's "stubs record no time" blind spot is now half-closed |
| Native suites used hand-maintained register replicas | `HOST_STUBS_REAL_REGISTER_UTILS` compiles against the real `rurp_register_utils.h`, exercising production's cache-elision | **Phase 116 TRACE-01** | Closes the register-elision blind spot the FM1608 todo documents |

**Published claims now known wrong — do not implement from them** (all three are Phase 146 / CLOSE-04's
to reconcile; this phase names them and edits no published text):

- `PROJECT.md`'s v1.31 throughput table gives `0x07`/`0x08` a `3 × N` overpulse. **Shipped value is `0`
  on both rows** (F-140-05; verified from `eprom_params.cpp:46-47` this session).
- Milestone **C3**'s "no *pulse* comes near [16383 µs]" is true of database data (max **1000 µs**,
  re-measured this session) but false of the wire — `pulse-delay` is an **unclamped `uint32_t`**
  (`json_parser.c:503`), so an over-ceiling pulse is reachable **today**, before `--pulse-us` ships.
  This is a strengthening of the correction CONTEXT.md `<specifics>` hands forward.
- **F-140-07**: gh#15's published justification for `0x0B`'s `energy_cap_us = 50000` — "`100 × 500 µs` is
  exactly the classic 2716 *total* programming time" — is wrong; the TI TMS 2516 total is 100 **seconds**
  and 50 ms is the per-location `t_w(PR)` TYP. The **value** is right and datasheet-grounded; only the
  reason is wrong.
- `firestarter/doc/PROTOCOLS.md` §§1.3-1.5's "JEDEC Intelligent Programming … 3× overpulse" claim and its
  nonexistent `W27C512.pdf §6.2` citation were **already corrected in 140-06** (F-140-09) — do not
  re-introduce that framing in any new comment.

---

## Assumptions Log

Every claim tagged `[ASSUMED]` in this document. Everything not listed here was read from the live tree,
executed, or measured this session.

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The two new message IDs should be `0xBD` and `0xBE`, with shape `[u24 hex_addr, u8]` and names `MSG_ERR_MAX_PULSES` / `MSG_ERR_ENERGY_CAP` | Message catalog mechanics | **Low.** The free-slot set `{0xAE, 0xBD, 0xBE, 0xBF}` and the absence of band validation are VERIFIED; only the *choice* and the naming/shape are a recommendation. Any free slot works; the planner may pick differently. A wrong shape is caught by codegen Rule 9 at regen time |
| A2 | `verify_mode`'s `VERIFY_PER_PULSE_PLUS_FINAL` should be consumed as one final full-block verify pass (option 1) | Shipped parameter table | **Medium.** The shipped values and `CLAUDE.md`'s documented behaviour are VERIFIED; the *disposition* is a judgement call CONTEXT.md does not cover. If the planner defers instead, `CLAUDE.md`'s rows must be corrected to match, or the phase ships a documented behaviour it does not implement |
| A3 | The `pulse_delay == 0` fallback must resolve **before** D-03's refusal compares against the cap | Pattern 1 | **Low.** Ordering follows from the code (`:69-76` runs after pointer installation) and from the refusal being vacuous on `0`. Not independently tested — no shipped chip reaches the fallback (F-140-04) |
| A4 | Hoisting the six `pgm_read_*` calls out of the byte loop is smaller **and** faster than reading per byte | Shipped parameter table; Flash budget | **Low.** Standard AVR `LPM` reasoning, not measured. If wrong, the measurement in the phase's own flash delta will show it |
| A5 | Deleting `eprom_internal_ensure_regulator_enabled` reclaims 0 B | Citation audit; Flash budget | **Low.** `-ffunction-sections`/`--gc-sections` presence is VERIFIED and the zero-caller state is VERIFIED; that the linker actually drops *this* symbol is inferred from the same mechanism F-140-02 measured for the table |
| A6 | The `0x0B` energy-cap worst case with an arbitrary `--pulse-us` is `2 × cap − 1 = 99999 µs` | Energy-cap arithmetic | **Low.** Pure arithmetic under D-01's predicate + D-03's refusal; derived, not measured. Matters only for the honesty of the phase record's wording |
| A7 | The existing `native_trace_v131` suite still **compiles** after the rewrite and fails only on stream equality | Native test architecture | **Medium.** No signature it calls changes, and its `RESPONSE_CODE_OK` assertion survives the walked model — but this is a prediction, not a run. If it fails to compile instead, D-10's "leave it RED" needs re-reading, because a build break is not the same evidence as a stream divergence. **Verify early in the phase** |
| A8 | A `0xFF` target byte never needs a pulse on any of the three 27C families | Per-byte loop shape | **Low** for UV parts (erased = all ones; programming only clears bits) — this is the same premise `mem_util_blank_check` already relies on. Note `0x07` includes EEPROM-class parts (W27C512) where the erased state is also `0xFF`, so the premise holds there too. LOOP-06 mandates the behaviour regardless |
| A9 | `pio run -t clean` before a recorded measurement is required for flash figures too, not just native warning counts | Flash budget | **Low.** The baseline's own `meta.note` documents the cold-truncation trap for native warnings; extending the discipline to AVR sizes is conservative. The warm figures measured this session already match both baselines byte-for-byte, which is corroborating evidence that warm AVR figures are trustworthy |

**No `[ASSUMED]` claim in this document concerns a compliance requirement, retention policy, security
standard, or performance target.** The three highest-risk items (A2, A7 and A1's shape) are all
resolvable inside the phase by a plan decision or an early verification step, not by an operator question
— consistent with CONTEXT.md's instruction not to re-open decided ground.

---

## Open Questions (RESOLVED)

**All four items below are RESOLVED inside this phase's plan set — none escalates to the operator.**
Each item carries a `RESOLVED:` bullet naming the plan that discharges it. No recommendation's
substance changed; the markers were added during plan revision so the resolution is machine-legible
rather than implied by a `**Recommendation:**` bullet.

### 1. `verify_mode` has no decision (RESOLVED — the only genuine gap)
- **What we know:** `0x07`/`0x08` ship `VERIFY_PER_PULSE_PLUS_FINAL`, `0x0B` ships `VERIFY_PER_PULSE`
  (`eprom_params.cpp:46-48`), and `firestarter/CLAUDE.md`'s Algorithm Handlers rows already describe the
  resulting behaviour ("+ 1 final full-array pass" vs "no final full-array pass"). The pre-change block
  loop's last action was always a full verify pass, so the `PLUS_FINAL` behaviour exists today by accident
  of structure.
- **What's unclear:** whether Phase 141 consumes the column, reads-and-asserts it, or defers it. No D-NN
  mentions it; ROADMAP success criteria 1-5 do not mention it; LOOP-01…08 do not mention it.
- **Recommendation:** **consume it** (option 1 in §"Shipped parameter table"). It preserves an existing
  property rather than adding one, keeps `CLAUDE.md` true, avoids a second shipped column with no
  consumer, and is funded by `verify_and_update_mask`'s removal. Whatever is chosen, **record it in the
  phase record and reconcile `CLAUDE.md`'s three rows in the same change**. Do not escalate to the
  operator — this is inside "the loop's exact function decomposition" that D-12's last bullet delegates.
- **RESOLVED:** carried into plan **141-04**, which consumes the column — one final full-block
  read-and-compare pass on the two `VERIFY_PER_PULSE_PLUS_FINAL` rows and none on `0x0B`. Proven by
  plan **141-07**'s `test_loop04_0x0B_runs_no_final_full_block_verify_pass`, with `CLAUDE.md`'s three
  Algorithm Handlers rows reconciled in plan **141-05** and the disposition recorded in plan
  **141-09**'s phase record.

### 2. Which byte's pulse count is reported when a block has many failures (RESOLVED)
- **What we know:** LOOP-05 says "the failing address plus its pulse count are reported" (singular), and
  the loop aborts on the first byte that exhausts its budget, so there is only ever one.
- **What's unclear:** nothing behaviourally — but the old `MSG_ERR_WRITE_FAILED` payload carried a
  *mismatch count* for the whole block (`_b[4..5]`, `eprom.cpp:188-189`), and the host may render that
  field. Phase 143 / HOST-03 owns the rendering.
- **Recommendation:** report exactly `(address, pulse_count)` and let the block-level count die with the
  block-level loop. Name in the phase record that `MSG_ERR_WRITE_FAILED 0xB1`'s three-param shape is now
  emitted by nothing on the 27C path, so Phase 143 knows not to expect it.
- **RESOLVED:** carried into plan **141-04**'s single `eprom_internal_report_budget_failure`, which
  emits exactly `(address, pulse_count)` for both budget limits; plan **141-09** task 3 records
  `MSG_ERR_WRITE_FAILED 0xB1`'s three-param shape as emitted by nothing on the 27C path, for
  **Phase 143 / HOST-03**.

### 3. Whether `native_trace_v131`'s determinism leg also fails (RESOLVED)
- **What we know:** `assert_v131_protocol_case` drives the block **twice** and asserts positional
  identity between the two runs (`test_trace_eprom_v131.cpp:311-321`). The read-back model's
  `read_count` is reset by `trace_readback_reset()` inside `drive_v131_write`, so the second run should
  reproduce the first.
- **What's unclear:** whether the new loop's read counts interact with the model differently across the
  two drives (the register cache is *not* re-reset between them beyond what `drive_v131_write` does).
- **Recommendation:** expect the stream-equality assertion to fail and the determinism assertion to pass.
  If determinism also fails, that is worth investigating rather than accepting as part of D-10's RED —
  a non-reproducible new cadence would poison Phase 144's diff. Check it explicitly when the RED is
  captured.
- **RESOLVED:** carried into plan **141-04**'s expected-RED statement (assumption A7) and discharged by
  plan **141-09** task 1, whose acceptance criteria require recording that the determinism assertion
  still **passes** and that the sole failure is `v131_assert_stream_equals` with its first divergent
  index named — plus an explicit STOP-and-report if determinism fails too.

### 4. Whether `MSG_INFO_RETRIES` / `DBG_PULSE_DELAY_MISMATCH` should be retired (RESOLVED)
- **What we know:** both become caller-less; no orphan gate exists; a wording-only catalog change
  produces a zero-byte firmware diff.
- **What's unclear:** whether the operator wants the debug id's now-false wording ("retrying with
  increased pulse delay") left in the catalog.
- **Recommendation:** leave both IDs assigned, state their unreferenced status in the phase record, and
  hand the wording question to Phase 146 / CLOSE-03 with the other doc reconciliations. Deleting an id
  risks later reuse confusion for zero behavioural gain.
- **RESOLVED:** carried into plan **141-01** task 1, which states "do NOT touch `MSG_INFO_RETRIES 0x51`
  or the debug entry `DBG_PULSE_DELAY_MISMATCH 0x15`" and leaves both IDs assigned and unedited, and
  into plan **141-09** task 3, which records their unreferenced status and hands the wording question
  to **Phase 146 / CLOSE-03**.

---

## Environment Availability

Probed this session in the devcontainer.

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | firmware build + native tests | ✓ | 6.1.19 | — |
| `platform-atmelavr` | `uno`/`uno328pb`/`leonardo` builds | ✓ | installed (`~/.platformio/platforms/atmelavr`) | — |
| `platform-native` | five native envs | ✓ | installed | — |
| `avr-gcc` | AVR compile | ✓ | 7.3.0 (`toolchain-atmelavr`, **not on `PATH`** — invoke via `pio`) | — |
| `framework-arduino-avr` | `delay`/`delayMicroseconds`/PROGMEM | ✓ | installed + MiniCore variant for `uno328pb` | — |
| ArduinoFake | native suites | ✓ | resolved in `.pio/libdeps/` for all five envs | — |
| Python 3 | gate suite, codegen, sync | ✓ | 3.12.13 | — |
| pytest | `pytest tests/ -q` | ✓ | 9.1.1 (**244 passed** this session) | — |
| `tomllib` | reading `messages.toml` | ✓ | stdlib in 3.12 | — |
| `git` | D-13 + trace-identity + citation gates (all fail-closed on missing `git`) | ✓ | present | none — these gates FAIL rather than skip, by design |
| `bash`, `cp`, `diff`, `mkdir` | `sync_to_subrepos.sh` (`:18`) | ✓ | — | — |
| Node.js | `gsd-tools.cjs` | ✓ | v22.23.2 at `/usr/local/share/nvm/current/bin/node` (**not on bare `PATH`** — use the absolute path or `.claude/gsd-core/bin/gsd-tools.cjs`) | — |
| ARM toolchain (`arm-none-eabi-gcc`) | PY32 CMake build | ✗ | — | Not needed: no `pio` env builds PY32, and `check_cmake_manifest.py` is a **text** manifest gate that never invokes a compiler. Adding no new `src/` TU keeps it green |
| Bench hardware (`/dev/ttyACM*`, `/dev/ttyUSB*`) | write→verify on real silicon | not probed | — | **Phase 145's scope.** Nothing in Phase 141 requires a board |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** ARM toolchain — not required, as reasoned above.

### ⚠️ Two environment traps that will bite an `<automated>` verify block

1. **`pio` must run with cwd `/workspaces/firestarter`.** `/workspaces/platformio.ini` (gitignored,
   generated by `.devcontainer/gen-platformio-ini.py`) contains **two `[platformio]` sections** — line 7
   from the generator's own header, line 26 from the concatenated `firestarter/platformio.ini` — so every
   `pio` subcommand invoked from the repo root dies with
   `InvalidProjectConfError … 'section 'platformio' already exists'`. **`pio -d <dir>` does not help**
   (verified). Every leg needs `cd /workspaces/firestarter && pio …`.
2. **`node` is not on the bare `PATH`.** Use `/usr/local/share/nvm/current/bin/node` or the repo's
   `.claude/gsd-core/bin/gsd-tools.cjs` with an absolute interpreter path.

Both are pre-existing devcontainer facts, not defects this phase should fix.

---

## Validation Architecture

`.planning/config.json` has no `workflow.nyquist_validation` key, so it is treated as **enabled**.

### Test Framework

| Property | Value |
|---|---|
| Firmware unit/behaviour framework | Unity via PlatformIO `test_framework = unity` (+ ArduinoFake `^0.4.0` for mocks) |
| Firmware gate framework | pytest 9.1.1 against `firestarter/tests/` |
| Config files | `firestarter/platformio.ini` (six envs after this phase); `firestarter/tests/` has **no `conftest.py`** anywhere — a recorded house-rule, not an omission |
| Quick run command (per task commit) | `cd /workspaces/firestarter && python3 -m pytest tests/ -q -o addopts="" && pio test -e <sixth_env>` |
| Full suite command (per wave merge) | `cd /workspaces/firestarter && pio test -e native && pio test -e native_nodevtools && pio test -e <sixth_env> && python3 -m pytest tests/ -q -o addopts="" && pio run` |

Use `-o addopts=""` — doubling pytest's `-q` (already in `addopts` as `-ra -q`) suppresses the count line.

### Phase Requirements → Test Map

| Req | Behaviour | Test type | Automated command | File exists? |
|---|---|---|---|---|
| LOOP-01 | fixed width, verify per pulse, count per byte | unit (native) | `cd /workspaces/firestarter && pio test -e <sixth_env> -f "*<suite>*"` | ❌ Wave 0 |
| LOOP-02 | four constructs absent from the write path | gate (grep/AST over `src/proms/eprom.cpp`) + the D-13 inventory shrinkage | `cd /workspaces/firestarter && python3 -m pytest tests/test_protocol_branch_inventory.py -q -o addopts=""` | ⚠️ gate exists; **a LOOP-02 absence assertion does not** — Wave 0 |
| LOOP-03 | overprogram duration + clamp + overflow safety | unit (native, pure function per D-08) | same env | ❌ Wave 0 |
| LOOP-04 | `0x0B` energy cap; exactly 100/50/250 pulses at 500/1000/200 µs; no overprogram | unit (native) | same env | ❌ Wave 0 |
| LOOP-05 | abort + route disable + `(address, pulses)` reported | unit (native), scoped to `_main`'s own CONTROL strobes | same env | ❌ Wave 0 |
| LOOP-06 | `0xFF` and already-matching bytes emit zero pulses | unit (native) | same env | ❌ Wave 0 |
| LOOP-07 | **global**: no recorded `delayMicroseconds` argument > 16383 | unit (native, timing recorder) + a source-scan gate for the two sites | same env | ❌ Wave 0 |
| LOOP-08 | route asserted once, present in every per-byte CONTROL write, survives A16 crossing on `pins >= 32` | unit (native, strobe recorder) | same env | ❌ Wave 0 |
| — | table values unchanged | existing | `python3 -m pytest tests/test_eprom_params_citations.py -q -o addopts=""` | ✅ |
| — | frozen fixture untouched | existing | `python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q -o addopts=""` | ✅ |
| — | no new `src/` TU unmanifested | existing | `python3 -m pytest tests/test_check_cmake_manifest.py -q -o addopts=""` | ✅ |
| — | flash/RAM inside MERGE-05's band | existing checker | `cd /workspaces/firestarter && python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=<log> --avr-log uno328pb=<log> --avr-log leonardo=<log>` | ✅ |
| — | native warning watermark | existing checker | `cd /workspaces/firestarter && python3 scripts/check_build_warnings.py …` (never with the sixth env name) | ✅ |
| — | catalog synced + regenerated | manual + `git diff --stat` | `bash /workspaces/tools/catalog/sync_to_subrepos.sh` then `git -C /workspaces/firestarter diff --stat -- include/messages.h tools/catalog/messages.toml` | ✅ script |

**Nothing here is manual-only.** Bench proof on real silicon is BENCH-01…03, **Phase 145**, and is
explicitly not a Phase 141 verification.

### Sampling Rate

- **Per task commit:** `python3 -m pytest tests/ -q -o addopts=""` (~11 s) plus `pio test -e <sixth_env>`.
- **Per wave merge:** the full-suite command above, including `pio run` for all three AVR targets.
- **Phase gate:** `native` and `native_nodevtools` at **exactly 141 cases / 17 suites** each, `pytest tests/`
  fully green with the re-derived D-13 golden, the sixth env green by name, `--policy merge05` green, and
  `native_trace_v131` **RED and recorded as such** — the one expected non-green, which the phase record
  must name explicitly so `/gsd-verify-work` does not read it as a regression.

### Wave 0 Gaps

- [ ] `test/native/avr/<new_suite>/<new_suite>.cpp` — covers LOOP-01, LOOP-03, LOOP-04, LOOP-05, LOOP-06, LOOP-07, LOOP-08
- [ ] `test/native/avr/<new_suite>/host_stubs.cpp` — `HOST_STUBS_REAL_REGISTER_UTILS` + `HOST_STUBS_RECORD_TIMING` + `HOST_STUBS_CUSTOM_READ_DATA_BUFFER`, plus a `converge_after` read-back model and `reset_register_cache`
- [ ] `platformio.ini` — the sixth `[env:native_*_v131]` with its HARD CONSTRAINT comment block
- [ ] A **LOOP-02 absence assertion** — the D-13 inventory proves the *shape* moved, not that the four
      named constructs are gone. A small source-scan gate (`NUMBER_OF_RETRIES`,
      `program_mismatched_bytes`, `verify_and_update_mask`, the growth expression all absent from
      `src/proms/eprom.cpp`) closes LOOP-02's own wording. Follow `test_protocol_branch_inventory.py`'s
      standalone-module conventions: live re-parse, non-vacuity guard, fail-closed on a missing target,
      no `pytest.skip`
- [ ] A **LOOP-07 source-scan leg** — the native test proves no *executed* path exceeds the ceiling; a
      grep-class gate asserting both former sites now call the helper closes the "global" wording
- [ ] Re-derived `tests/golden/protocol_branch_inventory.json` + the edited `:446` literal
- [ ] The committed new-trace artifact (via `-D EPROM_V131_TRACE_DUMP`, binary run directly)
- **Framework install:** none — every dependency is already resolved

**D-15 applies to every new leg:** plant the violation, watch it go RED for the reason it was planted,
capture the transcript, then fix the locator rather than the assertion. Phase 140 recorded 12 planted-RED
runs across three gates; match that standard.

---

## Security Domain

`.planning/config.json` has no `security_enforcement` key, so it is treated as enabled. This is embedded
firmware with **no network stack, no authentication surface, and no untrusted multi-user input** — the
threat model is *physical and electrical*, not adversarial. Mapped honestly rather than padded.

### Applicable ASVS Categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | **No** | No user, session, or credential exists. The device trusts whatever is on its USB serial port by design |
| V3 Session Management | **No** | The three-phase INIT→MAIN→END state machine is a protocol sequence, not a security session |
| V4 Access Control | **No** | Single-operator physical device |
| **V5 Input Validation** | **YES — and this phase strengthens it** | Firmware-side bounds checking on wire-supplied values. **`pulse-delay` is currently parsed unclamped** (`json_parser.c:503`), unlike `read-settling-delay`/`read-strobe-us` which clamp to `READ_TIMING_MAX_US = 1000` (`:348-362`). D-03's pre-flight refusal plus LOOP-07's helper are the phase's V5 contributions. `handle->pins` and `handle->protocol` are likewise host-supplied and must be treated as untrusted (hence: branch on `pins >= 32`, and fail closed on an unrecognised `protocol`) |
| V6 Cryptography | **No** | No crypto anywhere in the write path. Nothing to hand-roll |
| V7 Error Handling & Logging | **Partially** | The two new IDs must not leak anything sensitive (they carry an address and a count — both already public in existing frames) and must not be silently swallowed. The fail-closed-with-a-named-error idiom is the in-tree standard |
| V10 Malicious Code | **Indirectly** | No new dependency is introduced (see §"Package Legitimacy Audit"), so no supply-chain surface is added |
| V12 Files / V13 API / V14 Config | **No** | No filesystem, no HTTP API, no deployment config |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard mitigation | Phase 141 status |
|---|---|---|---|
| **Integer truncation on a narrower ABI** (`uint32_t` → 16-bit `unsigned int`) silently shortening a hardware timing | Tampering / Denial of Service | Validate-and-split at the boundary rather than trusting the callee's width | **This is LOOP-07.** Two truncations stack today: the ABI narrowing at > 65535 and the `us <<= 2` overflow at > 16383 |
| **Unbounded wire value reaching a hardware primitive** | Tampering | Clamp or refuse at parse time; refuse pre-flight before energising | **D-03** (refusal). Note the parser itself stays unclamped — Phase 143/HOST-04 owns `--pulse-us` bounds; the firmware refusal is the backstop |
| **Unrecognised selector falling back to a default that energises the wrong route** | Tampering / physical damage | Fail closed, never `&TABLE[0]` | Already handled: `eprom_params_for()` returns `NULL` (Phase 140 D-05); `configure_memory` fail-closes every unknown protocol to `configure_not_implemented` |
| **High voltage left asserted on an error exit** | Denial of Service / physical damage | Disable every route on every exit | **LOOP-05** covers this exit; **Phase 142 / VPP-02** generalises it. `command_done()` (`firestarter.cpp:166`) is an orthogonal backstop that zeroes the control register |
| **Over-voltage applied to a part** | Physical damage | ADC read-back + refusal | `eprom_check_vpp` (`eprom.cpp:209-272`) refuses above `vpp_mv + 500` unless `FLAG_FORCE`. **Unchanged by this phase; VPP-04 re-verifies it** |
| **Stack exhaustion on a 2 KB part** | Denial of Service | Bound stack allocations | **Improved:** removing `mismatch_bitmask[DATA_BUFFER_SIZE/8]` frees 64 B (Uno-class) / 128 B (Leonardo) of peak stack against 475/546 B of static headroom |
| **A gate that silently passes** (scan target missing, env seam left set) | Repudiation | Fail-closed gates with non-vacuity guards and planted-RED proof | D-15 discipline; the existing gate modules already implement `test_..._is_non_vacuous` and `test_git_is_required_not_optional` patterns to copy |

**No secret, credential, token, or PII is touched by this phase in any of the three repositories.**

---

## Sources

### Primary (HIGH confidence — read or executed this session)

**Firmware working tree** at `e2e25b5a7cfd09cefb349827fb97ceba96e60ac7`, branch
`gsd/v1.31-27c-programming-algorithm-fidelity`:
- `src/proms/eprom.cpp` (332 lines, full read)
- `src/proms/memory.cpp` (390 lines, full read)
- `src/proms/eprom_params.cpp`, `include/eprom_params.h` (full reads)
- `include/rurp_pinout.h`, `include/rurp_shield.h`, `include/rurp_register_utils.h`,
  `include/rurp_hw_rev_utils.h`, `include/rurp_platform.h`, `include/rurp_platform_compat.h`,
  `include/memory_utils.h`, `include/firestarter.h`, `include/operation_utils.h`,
  `include/logging_id.h`, `include/messages.h`
- `src/json_parser.c`, `src/eprom_operations.cpp`, `src/operation_utils.cpp`, `src/firestarter.cpp`
- `platformio.ini` (all six sections), `platform/py32f071/CMakeLists.txt`,
  `platform/py32f071/include/Arduino.h`
- `tests/test_protocol_branch_inventory.py`, `tests/test_golden_trace_identity_eprom_v131.py`,
  `tests/test_eprom_params_citations.py`, `tests/test_check_cmake_manifest.py`,
  `tests/test_pr45_non_ancestry.py`, `scripts/check_size_baseline.py`
- `tests/golden/protocol_branch_inventory.json`, `scripts/baseline/{size_baseline,size_baseline_v131,size_baseline_base01}.json`
- `test/native/avr/_shared/host_stubs_common.inc`, `test/native/avr/test_trace_eprom_v131/{test_trace_eprom_v131.cpp,host_stubs.cpp}`,
  `test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp`,
  `test/native/avr/test_messages/test_rurp_log_id.cpp`
- `.github/workflows/{build.yml,beta-build.yml}`, `firestarter/CLAUDE.md`

**Meta repo** at `3345eed5`: `CLAUDE.md`, `.planning/{config.json,STATE.md,ROADMAP.md,REQUIREMENTS.md}`,
`.planning/phases/141-per-byte-program-loop/141-CONTEXT.md`,
`.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md`,
`.planning/phases/138-preconditions-baseline/138-BASELINE.md`,
`tools/catalog/{messages.toml,codegen.py,sync_to_subrepos.sh}`,
`.devcontainer/gen-platformio-ini.py`

**Host repo:** `firestarter_app/firestarter/data/chip_database.json`,
`firestarter_app/firestarter/messages.py`, `firestarter_app/tests/test_revision_constants_parity.py`,
`firestarter_app/tools/catalog/messages.toml`

**Toolchain source:** `~/.platformio/packages/framework-arduino-avr/cores/arduino/wiring.c` (`:106`,
`:120`, `:167-183`), `.../cores/arduino/Arduino.h:144`,
`~/.platformio/platforms/atmelavr/builder/frameworks/arduino.py` (`:98`, `:111`),
`.pio/libdeps/native/ArduinoFake/src/FunctionFake.h:23`

**Commands executed this session (all outputs quoted above):**
`git rev-parse` / `merge-base --is-ancestor` / `hash-object`; `pio run -e uno`, `-e uno328pb`,
`-e leonardo`; `python3 -m pytest tests/ -q -o addopts=""` (244 passed);
`grep -rn "delayMicroseconds" src/ include/ lib/ platform/`; `python3` enumeration of `messages.toml`
via `tomllib`; `python3` aggregation of `chip_database.json` `pulse_duration` by `algorithm`;
`python3 -c "import test_protocol_branch_inventory …"` live re-parse; `diff -q` across all three catalog
copies; `pio project config` cwd probe.

### Secondary (MEDIUM confidence — in-repo records cross-checked against source)

- `140-PARAM-TABLE-RECORD.md` §§5-11 — cross-checked: §2's row values match `eprom_params.cpp:46-48`
  exactly; §6's P1/P2 zero-delta predictions match this session's three builds; §7's `native_params_v131`
  9/1 count is a record-only figure not present in any baseline JSON (accepted as stated).
- `138-BASELINE.md` §7 F-138-02/04/05/06 — cross-checked: the 8 B / 2 B headroom is confirmed as a
  `origin/beta`-tip figure, and this branch's non-ancestry of `6fab4ea` is independently verified.
- `firestarter/CLAUDE.md` §"Algorithm Handlers" — its `0x07`/`0x08`/`0x0B` rows match the shipped table
  and the DB modal widths measured this session; its `verify_mode`-derived claims are the basis for
  Open Question 1.
- `.planning/STATE.md` §C2 — pulse distributions re-derived independently this session and found
  byte-identical.

### Tertiary (LOW confidence — none)

No claim in this document rests on a WebSearch result or an unverified single source. **No web search was
performed**: the phase's entire domain is this repository plus its pinned toolchain, both readable
directly, and Context7 has no entry for a bespoke AVR firmware tree.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Citation audit (~40 refs) | **HIGH** | Every reference opened in the live tree; 37 exact, 1 stale (`mem_util_blank_check`), 2 imprecise. Corrections given with exact replacements |
| Shipped table values | **HIGH** | Read from `eprom_params.cpp:45-49`; independently corroborated by `test_eprom_params_v131.cpp:194-201`'s frozen expectations |
| `delayMicroseconds` inventory (LOOP-07) | **HIGH** | Exhaustive grep across `src/`, `include/`, `lib/`, `platform/`; every argument's provenance traced; the macro indirection followed to its single call site; the 16383 boundary read from the toolchain's own source |
| Flash / RAM budget | **HIGH** | All three AVR targets built this session; figures byte-identical to both baselines; the branch's non-ancestry of the drifted `beta` tip verified with `git merge-base --is-ancestor` |
| Gate and fixture dispositions | **HIGH** | Every gate module read; CI legs read from both workflows; the D-13 re-derivation path executed; blob-SHA equivalence of `hash-object` and `rev-parse` demonstrated |
| Message catalog mechanics | **HIGH** | `messages.toml` parsed with `tomllib` for the free-slot set; `codegen.py`'s 10 validation rules read; `sync_to_subrepos.sh` read line by line (including its two tautological `diff` calls); all three copies confirmed byte-identical |
| DIP32 / A16 mechanism | **HIGH** | Derived from `rurp_pinout.h`'s two macro branches, `rurp_hw_rev_utils.h`'s per-revision mapping, `memory.cpp:159-173`'s preserve mask, and `rurp_register_utils.h`'s elision — four independent files agreeing |
| Native test architecture | **HIGH** | `host_stubs_common.inc` and both consuming suites read in full; ArduinoFake's declaration checked in `.pio/libdeps` |
| Energy-cap / overprogram arithmetic | **HIGH** (derivation) / **MEDIUM** (D-01 prose fit) | The arithmetic is checkable; the claim that `while (accumulated < cap)` is the reading D-01 intended rests on matching D-01's three worked examples, which it does exactly while the alternative does not |
| `verify_mode` disposition | **MEDIUM** | The gap is verified; the recommended resolution is a judgement call (A2) |
| `native_trace_v131` still compiles | **MEDIUM** | Predicted from signature stability, not run (A7). Flagged for early verification |

**Overall: HIGH.** Everything a plan will build a task on — line numbers, table values, gate behaviour,
free ID slots, flash budget, command invocations — was verified against the live tree or executed. The
two MEDIUM items are both resolvable inside the phase.

**Research date:** 2026-08-10
**Valid until:** ~2026-09-09 (30 days) for the toolchain and architecture findings. **Shorter for
three things:** the AVR flash figures and the D-13 golden's blob SHAs invalidate on the **first commit
that touches `src/proms/eprom.cpp`** (i.e. immediately once the phase starts); the free message-ID set
invalidates if any other phase claims a slot; and the `origin/beta` non-ancestry finding invalidates the
moment the drift is merged (Phase 144's concern). Re-verify the flash headroom before the phase's final
measurement rather than quoting this document.
