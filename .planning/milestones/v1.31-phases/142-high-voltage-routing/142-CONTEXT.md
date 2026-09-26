# Phase 142: High-Voltage Routing - Context

**Gathered:** 2026-08-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Make every 27C protocol's high-voltage path **resolved in one place** and **provably de-energised on
every failing exit**. Concretely: route selection moves out of the two duplicated
`protocol == 0x0B || FLAG_VPE_AS_VPP` branches (`firestarter/src/proms/eprom.cpp:190` and `:340`,
current line numbers) into Phase 140's `eprom_params` table `vpp_path` column behind a single shared
resolver; the `pins < 32` drop-bit exclusion in `mem_util_calculate_top_address_register`
(`firestarter/src/proms/memory.cpp:172`) is removed on Rev 2-class hardware; every error exit from the
write path disables every control-register HV route; and the over-voltage refusal gets the gate
VPP-04 assumes already exists.

**Requirements:** VPP-01, VPP-02, VPP-03, VPP-04.

**This phase is SINGLE-REPO — `firestarter/` only.** `commits_land_in:` names `firestarter` (and the
meta repo for planning artifacts). No host change is required: D-06 keeps `--vpe-as-vpp` working
exactly as it does today, and no new message id is claimed (D-08), so no `messages.toml` edit, no
codegen, no `firestarter_app` constants-parity churn. A plan that only *reads* a submodule still
names it — a worktree leaves submodules empty and `files_modified` under-detects.

**Not in this phase:**
- `--pulse-us`, host timeout, host progress rendering, surfacing `MSG_ERR_MAX_PULSES` /
  `MSG_ERR_ENERGY_CAP` as user-facing program failures — **Phase 143** (HOST-01…05).
- Freezing/re-deriving `native_trace_v131`, the frozen-vs-new trace diff, the cross-phase flash/RAM
  reconciliation, the TEST requirement flips — **Phase 144** (TEST-01…08). `native_trace_v131` stays
  RED here by design (D-17).
- Any bench claim about `0x08` silicon. `0x08` is bench-opportunistic this milestone; this phase
  proves its route change in the emitted control-register stream only (D-03).
- Skipping VPP validation on reads / blank-checks, changing erase, chip-ID or bus-remapping
  behaviour. `PROJECT.md`'s own out-of-scope list holds: "Erase, blank-check, chip-ID, bus remapping
  and VPP validation behavior — unchanged except where a change is required for safe shared cleanup."
- Any `chip_database.json` change, any new database field, any second firmware dispatch selector.
  `protocol_id` remains the sole dispatch key (TABLE-05, still binding).
- Any `eprom_params.cpp` **data** change. `0x08` keeps `vpp_path = VPP_PATH_DROP_RESISTOR`; this phase
  makes the hardware honour the row it already ships rather than editing the row (D-01).

</domain>

<decisions>
## Implementation Decisions

### The DIP32 / `0x08` route (VPP-01)

- **D-01:** **The `pins < 32` drop-bit exclusion is removed — it is a VPP *level* bug, not a routing
  guard.** Operator correction, verbatim: *"no exclusion at all — 32 pin IC's with vpp on pin one is
  controlled with a jumper."* That jumper is **JP4** (`JMP_VPP_P1_BYPASS` / silkscreen `P1_VPP_JMP`;
  `firestarter/doc/SHIELD-REVISIONS.md` §7 and §5, present as a 1x2 header on Rev 2.0/2.1/2.2 and a
  2x2 on Rev 2.3). Routing VPP to socket pin 1 on a 32-pin part is therefore a **physical** decision,
  and `CTRL_VPP_VPE_DROP_ENABLE` is orthogonal to it: the drop bit selects the VPP *level* (VPE
  dropped through the resistor to ~13 V) and nothing else. Excluding it for `pins >= 32` does not
  protect a route — it silently programs `0x08` on the **un-dropped** rail. Phase 141's H1 already
  disproved the bit-collision theory the old comment gave as justification.
  **Consequence the planner must carry:** this changes what voltage reaches `0x08` silicon. It is
  therefore a real behaviour change, not a refactor, and D-03 governs what may be claimed about it.
  **AMENDED 2026-08-11 during planning, operator-confirmed — how the record may refer to JP4.**
  Research (`142-RESEARCH.md` §C-7) found JP4 documented two contradictory ways inside this project:
  `firestarter/doc/SHIELD-REVISIONS.md:65` calls `JMP_VPP_P1_BYPASS` / JP4 the VPP-bypass jumper, while
  `.planning/v1.7-SHIELD-REVS.md:37` and `:41-44` place JP4 in the hardware-revision detect divider
  (`JP4 (P1_VPP_JMP) → R41 → A3 → GND`). The alias appears in **no** firmware source file — it is
  documentation-only. The operator chose: **cite the physical-jumper framing above without naming a
  designator or asserting a net.** The phase record must not assert "JP4 routes VPP to socket pin 1" as
  a verified electrical fact. D-01/D-02 need only two facts, both verified: the drop bit is a VPP
  *level* selector (Phase 141 H1), and JP4 is `not-present` on Rev 0 and Rev 1
  (`doc/SHIELD-REVISIONS.md:87`) — which independently reinforces D-02's Rev-2-only gate, since on
  Rev 0/1 there is no jumper to close *in addition to* the bit alias. The documentation contradiction is
  logged as a finding for a later owner, not resolved here.

- **D-02:** **The removal is gated on Rev 2-class hardware at runtime, not made unconditional.** On
  Rev 0 / Rev 1, `rurp_map_ctrl_reg_for_hardware_revision()`
  (`firestarter/include/rurp_hw_rev_utils.h:28-32`) maps `CTRL_VPP_VPE_DROP_ENABLE` onto physical
  `0x01` — the **same line** as `CTRL_ADDRESS_LINE_16`. Preserving the drop bit across `set_address`
  on a 32-pin part there would force A16 permanently high. On Rev 2-class the two are distinct
  (`0x01` vs `0x100`, `firestarter/include/rurp_pinout.h:95-96`), so both can coexist. Rev 0 / Rev 1
  and any legacy non-`HARDWARE_REVISION` build (where the macros are genuine aliases,
  `rurp_pinout.h:75-76`) keep today's stripping behaviour.
  *Rejected — remove unconditionally:* the argument for it was that `eprom_check_vpp()` already
  refuses Rev 0 with `MSG_WARN_REV0_VPP_UNSUPPORTED` before any route is enabled, so Rev 0 VPP is
  already declared unsupported. That covers Rev 0 but **not Rev 1**, which has no such guard.
  *Rejected — remove plus an explicit Rev 0/1 refusal:* would need a new ERROR id, and `0xBF` is the
  band's last free slot (F-141-05), contested with Phase 143.
  **Cost is not a concern, verified:** `rurp_get_hardware_revision()`
  (`firestarter/include/rurp_hw_rev_utils.h:100-106`) returns either the EEPROM config override or
  `rurp_get_physical_hardware_revision()`, which returns a **boot-cached static** (`:43-45`) — no ADC
  read per call. `rurp_map_ctrl_reg_for_hardware_revision()` already calls it on **every** control
  register write, so the gate adds no new class of cost even inside
  `mem_util_calculate_top_address_register`, which runs twice per byte.
  **AMENDED 2026-08-11 during planning, operator-confirmed — what the gate keys on.** Research
  (`142-RESEARCH.md` §Open Question 3, §L-3) established that `mem_util_calculate_top_address_register`
  sees only `handle` and `address`, so the preserve arm can key on revision alone, on a new `handle`
  field, or on `handle->protocol` (ruled out — it would create a fourth tier-1 protocol-keyed site and
  violate TABLE-05). The operator chose **revision alone**: `REVISION_2_x` ⇒ preserve the drop bit for
  all `pins >= 32`. Zero new plumbing, zero RAM. Its nominal reach widens to every 32-pin protocol on
  Rev 2-class (`0x0E`, `0x29`, `0x10`, 32-pin flash), but none of them ever *sets* the drop bit, so
  there is nothing for the new arm to preserve. That "nothing" is **paid for with a proof, not an
  argument**: a native case driving a 32-pin **non-EPROM** protocol (`0x10`) at
  `hardware_revision = REVISION_2_2`, asserting the recorded control-value sequence is byte-identical
  before and after the change. A new 1-byte `handle` field was offered and **rejected** (RAM cost plus
  a plumbing seam, for a blast radius the proof already closes).

- **D-03:** **Ship the route change; claim nothing about silicon.** The phase record states that the
  `0x08` route change is proven in the **emitted control-register stream only**, never on a part. No
  `support_status` change, no "fixes AM27C020", no "0x08 now programs correctly". `0x08` is
  bench-opportunistic this milestone and AM27C020 is a known stress case (v1.18 Phase 99: write#1
  60/64, write#2 0/64), so it is not a pass/fail oracle either way.
  **The safety argument that *is* permitted:** after this change `eprom_check_vpp()` and the write
  path finally apply the **same** routing. Today they do not — `check_vpp` measures `0x08` with the
  drop bit **on** (`eprom.cpp:345`) while the write strips it before the first pulse, so the
  measured-and-validated voltage is not the voltage applied. Closing that gap is a correctness claim
  about the firmware, provable off-hardware, and it is the honest headline for this phase.

- **D-04:** **Phase 141's explicit `handle->pins >= 32` clear (`eprom.cpp:217-219`) is removed by this
  phase, not preserved.** It exists only to make the incidental stripping observable in the strobe
  stream and it explicitly says so in its own comment ("choosing the final DIP32 route … is Phase
  142 / VPP-01 and VPP-03 — this branch deliberately does not pre-empt that choice"). Once D-01/D-02
  land, keeping it would actively defeat the fix on Rev 2-class hardware.

### Route selection and the shared mask set (VPP-01, VPP-03)

- **D-05:** **One resolve function, not just shared constants.** A single
  `eprom_hv_route_mask(handle)`-shaped resolver (exact name/signature is the planner's) folds the
  table's `vpp_path`, the `FLAG_VPE_AS_VPP` override, and the pins/revision condition into **the mask
  actually used**, and both `eprom_check_vpp()` and the write path call it. Plus one all-off
  composite for the disable guarantee.
  **Why the stronger form:** sharing bit *constants* alone satisfies VPP-03's literal wording at zero
  flash cost but leaves the *selection* duplicated at two sites — which is precisely the duplication
  that let `check_vpp` and the write path drift apart on `0x08` (D-03). VPP-03's purpose is
  non-divergence, and only centralising the selection delivers it.

- **D-06:** **`--vpe-as-vpp` still overrides the table.** The table supplies the default; the flag
  forces the direct-VPE path on top of it. It is a live user-facing flag
  (`firestarter_app/firestarter/cli_handlers.py:574`, "Use VPE as VPP voltage"), set by **no**
  database entry — a pure human escape hatch that matters for the 25 V NMOS parts and the manual-pot
  workflow. Keeping it means no host change in a firmware-only phase.
  **Consequence for Phase 140's D-13 inventory gate:** the predicate survives but is demoted from a
  **tier-1** protocol-keyed site to a **tier-2** flag site. Combined with D-01/D-04/D-05, this is the
  deliberate inventory movement `firestarter/tests/golden/protocol_branch_inventory.json`'s own
  `frozen_for` note demands of this phase by name — it states an unchanged site count across Phase
  142 "would itself be suspicious."

- **D-07 (Claude's discretion — operator said "you decide"):** **Where the shared mask set lives.**
  Recorded default: named composite masks in `firestarter/include/rurp_pinout.h`, beside the `CTRL_*`
  bits they are built from — header-only `#define`s cost zero flash, both `eprom.cpp` and `memory.cpp`
  already include it, and a composite defined next to its own bit definitions cannot drift from them.
  Research may override on include-graph or flash-budget grounds; `eprom.h` / `eprom_params.h` is the
  alternative, but `memory.cpp` serves every protocol and would then have to include an
  EPROM-family header to compute its preserve mask.

- **D-08:** **No new message id is claimed by this phase.** `0xBF` is the last free slot in the
  `0xA0..0xBF` ERROR band (F-141-05) and Phase 143 also wants it. Every option in this discussion
  that would have needed one — a Rev 0/1 refusal (D-02), a flag-contradicts-table refusal (D-06) —
  was rejected partly on that ground. If planning discovers a genuine need, it is a checkpoint to the
  operator, not a quiet claim.

### The disable guarantee (VPP-02)

- **D-09:** **"Success" in VPP-02 means the write OPERATION's success exit, not each block's.** Local,
  immediate disable at every **error / abort** exit inside `eprom.cpp`; the per-block success exit
  deliberately leaves the rail up, and `command_done()` is the operation-level disable — made
  **provable by a test** rather than assumed.
  **Why:** `eprom_write_execute` runs once per 512 B (Uno) / 1024 B (Leonardo) block. Clearing
  `CTRL_VPP_REGULATOR_ENABLE` at each block's success exit re-arms the
  `if (get_control_register(CTRL_VPP_REGULATOR_ENABLE) == 0)` check at `eprom.cpp:189` and re-pays
  `delay(500)` per block — **~64 s added to a 64 K Uno write** (128 blocks × 0.5 s) against a typical
  `0x07` @100 µs total of ~32 s. It would more than triple the write, on a milestone whose stated
  benefit is "faster than today in the typical case", and it would undo LOOP-08's whole point.
  **The backstop is real, not hopeful:** Phase 141's record §4 traces that `command_done()`
  (`firestarter/src/firestarter.cpp:162-171`) zeroes `CONTROL_REGISTER`, `LEAST_SIGNIFICANT_BYTE` and
  `MOST_SIGNIFICANT_BYTE` and fires on **both** the success and the abort paths. Because the
  top-address bits and the `vpp_line` bit all live in those three registers, that zeroing fully
  de-energises. **This reading is recorded explicitly here so it is a decision, not a fudge** — and
  the phase owes a test proving `command_done()` actually clears, since nothing tests it today.
  *Rejected — literal block-level disable:* the ~64 s cost above.
  *Rejected — block-level with a shortened re-settle:* the 500 ms is sized for a cold boost ramp; any
  shorter value would be a guess this milestone cannot put on a scope, and a too-short settle
  programs at the wrong voltage.

- **D-10:** **Single-exit wrapper, not a disable call before every `return`.** Rename the current body
  to a `static` inner function; the public `eprom_write_execute` calls it and then disables
  **conditionally on `handle->response_code == RESPONSE_CODE_ERROR`**. A future edit adding a `return`
  inside the inner body **cannot** escape the guarantee — the invariant is structural rather than
  gate-enforced, and it is roughly flash-neutral.
  **AMENDED 2026-08-11 during planning, operator-confirmed.** This decision originally said the
  wrapper "unconditionally disables", which contradicts D-09's "the per-block success exit
  deliberately leaves the rail up". Research (`142-RESEARCH.md` §C-1) found the tiebreaker is a test
  that exists and passes today: `test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1307`
  (`test_loop05_a_successful_block_does_not_disable_the_route`) asserts a **successful** block leaves
  `CTRL_VPP_REGULATOR_ENABLE` **set**, and its own comment (`:1290-1292`) says generalising
  disable-on-every-exit *"is Phase 142 / VPP-02's job"* — it was authored anticipating this phase and
  encodes D-09's success-exit exemption as an assertion. The operator chose the conditional wrapper:
  it keeps that assertion GREEN, does not re-pay `delay(500)` per block (~64 s on a 64 K Uno write),
  and still delivers the structural property D-10 wanted. Only the literal word "unconditionally" is
  given up. A literal unconditional disable was offered and **rejected**.
  *Rejected — explicit call at each `return`:* greppable, but a new return can still forget it, which
  makes a source gate the only thing holding the invariant.
  *Rejected — both (wrapper plus a source-contract pytest gate):* the wrapper already makes the
  property structural; a second mechanism costs a gate module to author and plant-RED for no
  additional guarantee.

- **D-11:** **The guarantee covers control-register routes only. The address-bus `vpp_line` bit is an
  explicit non-claim.** `mem_util_remap_address_bus` (`firestarter/src/proms/memory.cpp:418-420`)
  sets `1UL << config.vpp_line` **ignoring `read_write`** — it is asserted on reads too. Clearing it
  on write-path exit would therefore be a read-path behaviour change, which this milestone excluded.
  The phase record states plainly: the disable guarantee covers control-register routes; the
  address-latch `vpp_line` bit is cleared by `command_done()` at operation end and by nothing else.

- **D-12 (Claude's discretion — operator said "you decide"):** **Which functions carry the
  guarantee.** Recorded default: `eprom_write_init` and `eprom_write_execute` — the two functions a
  `CMD_WRITE` actually runs, including `write_init`'s erase leg, which is the **only** write-path code
  that asserts `CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE` (remapped to `CTRL_VPP_P1_ENABLE` by
  `eprom_internal_set_control_register`'s `using_p1_as_vpp()` check, `eprom.cpp:441-447`). The
  boundary must be drawn from a **full map of every control-register assertion in `eprom.cpp`**
  produced during research, not from this list — widening to `erase_execute` / `get_chip_id` /
  `check_chip_id` as standalone commands is permitted only where it is genuinely shared cleanup, per
  `PROJECT.md`'s out-of-scope line.
  **Fact worth carrying:** during a 27C **write** the only control-register HV bit asserted is
  `CTRL_VPP_REGULATOR_ENABLE` (plus the drop bit). No `P1`/`A9`/`VPE`. VPP reaches the socket through
  the address bus (D-11). The disable set is therefore small — the value of VPP-02 is the
  *guarantee*, not the number of bits.

### Verification and budget (VPP-04, TEST seam)

- **D-13:** **VPP-04's "existing gate" does not exist for the EPROM path — this phase authors it, and
  says so.** Verified by grep: `MSG_ERR_VPP_HIGH` appears in **no** EPROM test. `test_val_eprom` pins
  `handle->vpp_mv = 0` against a `0`-returning stub precisely so the comparison never fires;
  `test_flash_intel_vpp` is a different protocol family (`0x10`, SAF-04); `native_loop_v131` does not
  mock `rurp_read_voltage_mv` at all. VPP-04 as written ("re-verified against the existing gate
  rather than assumed intact") rests on a premise that does not hold. The requirement is discharged
  by **authoring** the gate and recording that correction, not by pointing at a gate for another
  family.

- **D-14:** **The gate lives in a new suite inside the EXISTING `native_loop_v131` env.** Add a
  `test_vpp_eprom_v131` suite directory to that env's `test_filter` **and** its `-I` list (both are
  required — Phase 119 D-04), opting into `HOST_STUBS_CUSTOM_VOLTAGE_MV`, the seam
  `firestarter/test/native/avr/_shared/host_stubs_common.inc:274` already provides and
  `test_flash_intel_vpp` already uses. **No seventh env**, no `platformio.ini` env churn, no pinned
  baseline edit.
  **The constraint that forces this:** `native` and `native_nodevtools` are asserted at exactly
  **141 cases / 17 suites** by `scripts/baseline/size_baseline.json` through
  `check_size_baseline.py`'s `compare_native`, so adding a case to `test_val_eprom` turns a live gate
  RED.
  **The honest cost, to be restated in the phase record:** `native_loop_v131` runs in **no CI leg of
  either repository**. This gate is a local run-by-name obligation, never implied CI coverage — the
  same terms `native_params_v131`, `native_trace_v131` and `native_loop_v131` already carry.
  *Rejected — re-baseline `native` to get real CI coverage:* Phase 144 / TEST-08 owns baseline
  reconciliation; editing a live gate's baseline here would move a gate this phase does not own.

- **D-15:** **The gate must prove three things, not one.** (a) An injected out-of-range reading
  produces `MSG_ERR_VPP_HIGH` + `RESPONSE_CODE_ERROR`; (b) **no HV route is left asserted** on that
  refusal path — the final control-register write leaves the route bits clear, the SAF-04 shape
  `test_flash_intel_vpp` already uses (`:186-189`); (c) the `FLAG_FORCE` leg still downgrades to
  `MSG_WARN_VPP_HIGH` + `RESPONSE_CODE_WARNING`, since that **is** the refusal's semantics.
  *Rejected — refusal only:* it would pass even if the rewrite left the rail energised on the refusal
  path, which is the exact failure VPP-02 exists to prevent.
  Every new gate leg is seen RED on a planted violation before its GREEN is believed — the standing
  D-15 discipline from Phases 140 and 141 (12 and 13 planted runs respectively), with each transcript
  captured verbatim in its plan's SUMMARY.

- **D-16:** **Flash posture: measure cold, record, MERGE-05 stays RED.** Same disposition the operator
  already made for Phase 141 ("Continue; 141-09 records it"). No shrink ladder this phase, no
  baseline JSON edit — Phase 144 / TEST-08 owns reconciliation.
  **Starting point (Phase 141 tip, cold):** `uno` 24424 B (75.7 %), `uno328pb` 24474 B (75.6 %),
  `leonardo` 26400 B (**92.1 % — 2272 B headroom**). RAM 1573 / 1579 / 2014, exact-0 delta vs BASE-01.
  MERGE-05 verdict at that tip: +492 / +498 / +328 against bands of 64 / 64 / 0 B.
  **Two things the planner must watch anyway:** the `leonardo` 28672 B ceiling is a **build failure**,
  not a gate — and Phase 143 still has to fit. And `check_build_warnings.py`'s native watermark sits
  at **1166 with zero headroom**, so any new warning in a native TU turns that gate RED. Consolidation
  plausibly shrinks (two duplicated selection branches collapse into one resolver), but that is a
  prediction, not a promise.

- **D-17 (carried, restated):** **`native_trace_v131` stays RED and is NOT re-frozen here.** Phase
  141's D-10 left it RED by design and Phase 144 / TEST-06 owns the freeze and the diff. This phase
  changes the strobe stream again (D-01, D-04, D-09, D-10); it captures nothing as a new frozen
  fixture and names the RED in its record so `/gsd-verify-work` reads it as expected.

- **D-18:** **Phase 140's D-13 protocol-branch inventory golden is re-derived by this phase, by its
  own scanner.** The golden's `how_to_update` is binding: re-derive by running an independent parse
  against the new file, never hand-edit a line number, a `keyed_on` set, a class or a count, and state
  in the commit message which site changed and why. Both `eprom.cpp` and `eprom_params.cpp` blob SHAs
  are pinned in it, so every commit touching `eprom.cpp` breaks the D-13 gate until the golden is
  re-derived — Phase 141 handled this by confining all `eprom.cpp` edits to **one** plan so the gate
  went RED once, for one reason. That precedent is worth repeating here. The pinned `protocol_lines`
  literal in `firestarter/tests/test_protocol_branch_inventory.py` (at `:446` as of Phase 141) moves
  with it.

### Claude's Discretion

This is an **index** of the discretionary items, not a second definition site — D-07 and D-12 are
defined in full above. Their IDs are deliberately unbolded here: a `- **D-NN**` bullet without a `:` or
` — ` inside the bold makes the decision-coverage gate fail closed with `reason: could-not-parse`, and
D-12's label wrapped across lines, which the same gate cannot read. All four items were resolved during
planning; resolutions recorded inline.

- D-07 — where the shared mask set lives (default: `rurp_pinout.h` composites).
  **RESOLVED:** two `EPROM_HV_*` composites in `rurp_pinout.h` after `:97`, per research's include-graph
  and per-variant analysis. The **preserve** mask cannot be a `#define` in any variant (the drop↔A16
  alias), so only the all-off composite is a macro. Note the header has **zero** bitwise-OR composite
  precedent — this establishes a form rather than following one. Owned by plan `142-01`.
- D-12 — the exact function boundary for the disable guarantee (default: `eprom_write_init` +
  `eprom_write_execute`, drawn from a research-produced map of every control-register assertion in
  `eprom.cpp`).
  **RESOLVED:** the default holds, on the strength of the map research actually produced —
  `eprom_write_execute` (mandatory: all four leaking exits are there, including the untouched
  verify-failure exit) plus `eprom_write_init` (defensive, already exit-safe today). **Not** widened to
  `erase_execute` / `get_chip_id`: both already clear everything they assert, so `PROJECT.md`'s
  out-of-scope line forbids it. Owned by plan `142-04`.
- Naming and signature of the resolver in D-05, and whether the all-off composite is a `#define` or a
  small inline.
  **RESOLVED:** the resolver is **exposed** via `eprom.h` rather than kept file-static, which buys a
  direct `(protocol, ctrl_flags)` truth-table oracle and reaches the fail-closed NULL-row arm no drive
  can reach (research Open Question 4). The all-off composite is a `#define`.
- Plan decomposition, wave structure, and which plan owns the D-13 golden re-derivation.
  **RESOLVED:** 7 plans in 6 waves. `142-04` owns **all** `eprom.cpp` edits *and* the D-18 golden
  re-derivation, in **one task and one commit**, so the blob-SHA-pinned gate goes RED once for one
  reason; `142-02` (`memory.cpp`) lands before it, since the reverse order would briefly leave `0x08`
  with no drop route at all.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase requirements and milestone framing
- `.planning/REQUIREMENTS.md` §"High-Voltage Routing" — VPP-01…04, the exact requirement text.
- `.planning/ROADMAP.md` §"Phase 142: High-Voltage Routing" — goal, dependency on Phase 141, the four
  success criteria. **Note:** SC1's wording ("`0x07` and `0x08` route through the regulator +
  VPE-to-VPP dropping path") is satisfied by D-01/D-02 on Rev 2-class hardware and explicitly *not* on
  Rev 0/Rev 1 — the record must say so rather than restate SC1 unqualified.
- `.planning/PROJECT.md` §v1.31 — in-scope bullet "VPP routing protocol-correct and disabled on every
  exit"; the out-of-scope list; the 6.25 V evidence ceiling; the bench asymmetry (`0x07` required,
  `0x08`/`0x0B` opportunistic). **Its lines 125-127 caveat ("on DIP32 that bit *is* A16 … DIP32 uses
  `CTRL_VPP_P1_ENABLE` instead") is the pre-H1 theory and is superseded by D-01/D-02** — do not
  implement from it.

### Prior-phase records (the hand-offs this phase consumes)
- `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md` — §1 (the cold flash measurement and
  the MERGE-05 RED), §4 (what "hard-fails the block" actually does, including the `command_done()`
  trace D-09 depends on), §5 (the ERROR band's single free slot), §12 hand-off **H1** (the corrected
  drop-bit mechanism, owned by VPP-01/VPP-03), §15 findings register.
- `.planning/phases/141-per-byte-program-loop/141-CONTEXT.md` — D-09 (the DIP32 route handed here),
  D-10 (`native_trace_v131` stays RED), and the Deferred Ideas list naming this phase.
- `.planning/phases/140-parameter-table/140-CONTEXT.md` — the table's shape, `vpp_path` as an abstract
  enum chosen to leave this phase a free hand, and the D-13 inventory-gate rationale.
- `.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md` — the shipped row values and their
  citations.

### Firmware source (current line numbers — re-locate before relying on them)
- `firestarter/src/proms/eprom.cpp` — `:189-198` write-path route selection; `:217-219` the Phase 141
  `pins >= 32` clear (removed by D-04); `:173-182` `eprom_internal_report_budget_failure` (the one
  exit that already disables); `:296-314` the final verify pass and its early return; `:331-394`
  `eprom_check_vpp` incl. the Rev 0 warning return and the over-voltage / under-voltage branches;
  `:396-410` `eprom_internal_erase` (the only `A9|VPE` assertion on the write path); `:441-447`
  `eprom_internal_set_control_register`'s `using_p1_as_vpp` remap.
- `firestarter/src/proms/memory.cpp` — `:163-190` `mem_util_calculate_top_address_register` and the
  `pins < 32` preserve-mask guard D-01/D-02 change; `:294-304` `memory_set_data` (the program pulse);
  `:329-352` `mem_util_remap_address_bus` and the `vpp_line` bit of D-11.
- `firestarter/include/rurp_pinout.h` — `:75-96` the `CTRL_*` bit values per build variant (the
  distinct-vs-aliased question D-02 turns on); `:107-126` the `_REV1` / `_REV2` families.
- `firestarter/include/rurp_hw_rev_utils.h` — `:17-41` the revision→physical control-register mapper;
  `:43-45` `rurp_get_physical_hardware_revision` (the boot-cached static); `:100-106`
  `rurp_get_hardware_revision`.
- `firestarter/include/memory_utils.h` — `:43-47` `using_p1_as_vpp`.
- `firestarter/include/eprom_params.h` — `:46` the `VPP_PATH_*` enum; `:57` the `vpp_path` column.
- `firestarter/src/proms/eprom_params.cpp` — `:50-52` the three shipped rows (read-only this phase).
- `firestarter/src/firestarter.cpp` — `:162-171` `command_done()`, `:215-291` the dispatch switch that
  reaches it. D-09's backstop.

### Gates, tests and budget artifacts
- `firestarter/tests/golden/protocol_branch_inventory.json` — read `meta.how_to_update` and
  `meta.frozen_for` in full **before** touching `eprom.cpp`; `frozen_for` names Phase 142 by name and
  states what movement it expects.
- `firestarter/tests/test_protocol_branch_inventory.py` — the seven-test D-13 gate and the pinned
  `protocol_lines` literal (`:446` as of Phase 141).
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — `:274-278` the
  `HOST_STUBS_CUSTOM_VOLTAGE_MV` seam D-14 uses; the opt-in recorder layers list at the top.
- `firestarter/test/native/avr/test_flash_intel_vpp/` — the SAF-04 shape D-15(b) copies:
  `host_stubs.cpp:39` for the mock and `test_flash_intel_vpp.cpp:160-189` for the
  "high-VPP ERROR must leave the regulator cleared" assertions.
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` — the existing 6-case EPROM
  validation suite (in the pinned envs; **do not add cases**, D-14).
- `firestarter/test/native/avr/test_loop_eprom_v131/` — the Phase 141 suite and its `host_stubs.cpp`;
  the env D-14 extends.
- `firestarter/platformio.ini` — `[env:native_loop_v131]` (`:373`) and the surrounding comment block
  documenting why it is fed to neither live gate.
- `firestarter/scripts/baseline/size_baseline.json` + `scripts/check_size_baseline.py` — the
  141 cases / 17 suites pin and the MERGE-05 policy. **Read-only this phase** (D-16).
- `firestarter/scripts/check_build_warnings.py` — the 1166 native watermark with zero headroom.

### Hardware reference
- `firestarter/doc/SHIELD-REVISIONS.md` — §6 the per-rev capability matrix (every revision including
  Rev 0/Rev 1 claims 32-pin DIP support, which is why D-02 gates rather than removes unconditionally);
  §7 the `CTRL_*` / `PIN_*` / `RES_*` / `JMP_*` alias namespace and the `JMP_VPP_P1_BYPASS` = JP4 row.
- `.planning/v1.7-SHIELD-REVS.md` §5 — JP4's per-rev footprint history (1x2 → 2x2 at Rev 2.3). The
  meta-side copy; the sub-repo doc above is its subset and the two move in lockstep.
- `firestarter/CLAUDE.md` §"Algorithm Handlers" — the `0x07` / `0x08` / `0x0B` rows. The `0x08` row's
  "Pre-existing defect" paragraph describes the state D-01 changes and must be updated in the same
  change.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`HOST_STUBS_CUSTOM_VOLTAGE_MV`** (`_shared/host_stubs_common.inc:274`) — the voltage-injection
  seam already exists; D-14's gate needs one `#define` plus one function, not a new stub layer.
- **`test_flash_intel_vpp`'s SAF-04 assertions** — a working, in-tree template for "high-VPP ERROR
  must leave no route asserted". Copy the shape, not the protocol.
- **`eprom_internal_report_budget_failure`** (`eprom.cpp:173-182`) — already disables
  `CTRL_VPP_REGULATOR_ENABLE` before returning, and its own comment states generalising that to every
  exit is this phase's job. It becomes a caller of the shared all-off composite rather than a
  hand-rolled disable.
- **`native_loop_v131`'s recorder layers** — the ordered strobe recorder
  (`HOST_STUBS_REAL_REGISTER_UTILS`) already captures control-register writes, which is exactly what
  D-15(b) and the D-01/D-04 route-change proof need.
- **`eprom_params_for(protocol)`** — the table accessor Phase 140 shipped; `vpp_path` is already
  hoisted and `(void)`-cast in `eprom_write_execute:233-234` awaiting this phase's consumer.

### Established Patterns
- **`PROGMEM` table reads** go through `pgm_read_byte`/`pgm_read_dword` — the resolver must not
  dereference row fields directly.
- **Revision-conditional code** is written as a `switch` over `rurp_get_hardware_revision()` inside
  `#ifdef HARDWARE_REVISION`, with a fail-safe `default` (`rurp_hw_rev_utils.h:33-37` sets
  `ctrl_reg = 0` — no VPP, no VPE — for `REVISION_UNKNOWN`). D-02's gate should fail the same
  direction: **unknown revision keeps today's stripping behaviour**, never the new one.
- **`rurp_write_to_register()` elides a write when the value is unchanged** — F-141-09 records that
  register-write elision is invisible to a native suite unless `rurp_register_utils.h` is in the
  stubs. The route-change proof must not be built on a strobe the elision can swallow.
- **One plan owns all `eprom.cpp` edits** — the Phase 141 precedent that keeps the blob-SHA-pinned
  D-13 gate going RED once, for one reason.
- **Every new gate leg is seen RED on a planted violation first** (D-15 discipline, 12 and 13 planted
  runs in Phases 140 and 141), transcripts verbatim in the plan SUMMARY.

### Integration Points
- **`mem_util_calculate_top_address_register`** (`memory.cpp:163`) is shared by **every** protocol,
  not just 27C. D-01/D-02's change is inside a `handle->pins`-keyed guard, so no non-EPROM protocol's
  behaviour may move; a test proving that is cheap insurance.
- **`eprom_check_vpp()`** is reached from `eprom_generic_init`, which is the default
  `firestarter_operation_init` for **every** EPROM command — read, blank-check and chip-ID included.
  Changing its route resolution touches more commands than `write`. This is also why the "skip VPP
  checks on reads" todo keeps landing here (deferred again, see below).
- **`firestarter/CLAUDE.md`** carries the `0x07`/`0x08`/`0x0B` behaviour table and the `0x08`
  "Pre-existing defect" paragraph; both go stale the moment D-01 lands and must move in the same
  change.

</code_context>

<specifics>
## Specific Ideas

- The operator's own framing of the hardware, verbatim, because it is the correction the whole phase
  turns on: *"no exclusion at all — 32 pin IC's with vpp on pin one is controlled with a jumper."*
  Pin-1 VPP routing on DIP32 is **physical** (JP4); the drop bit is a level selector. Any plan or
  research output that reasons about the drop bit as a *routing* control is reasoning from the
  superseded model.
- The honest headline for this phase is **"`eprom_check_vpp()` and the write path now apply the same
  routing"** — a firmware-correctness claim, provable off-hardware. Not "`0x08` VPP is fixed."

</specifics>

<deferred>
## Deferred Ideas

- **Bench-validating the `0x08` route change on AM27C020** — Phase 145 at best, and only
  opportunistically. The operator chose "ship it, claim nothing" over adding a bench attempt, so this
  is not a Phase 145 obligation; if the part is on the bench anyway it is free evidence.
- **Removing the `pins < 32` exclusion on Rev 0 / Rev 1** — blocked by the physical bit alias, not by
  scope. Would require either a hardware modification or an explicit refusal with a new ERROR id.
- **Clearing the address-bus `vpp_line` bit as part of de-energisation** — D-11's non-claim. Reaches
  into `mem_util_remap_address_bus`, which every protocol shares, and touches the read path.
- **A shortened, measured re-settle constant** — D-09 rejected guessing it. Needs a scope on the
  boost rail, which is a bench task, not a firmware one.
- **Claiming `0xBF`** — left free for Phase 143 (F-141-05).
- **`native_trace_v131` re-freeze and the frozen-vs-new diff** — Phase 144 / TEST-06.
- **Cross-phase flash/RAM reconciliation and the baseline JSON update** — Phase 144 / TEST-08.
- **Reconciling `PROJECT.md`'s lines 125-127 DIP32 caveat, and the `0x08` row in
  `firestarter/CLAUDE.md`, against what actually shipped** — the `CLAUDE.md` row moves *in this phase*
  (it is firmware documentation for code this phase changes); `PROJECT.md`'s milestone text is
  Phase 146 / CLOSE-04's, alongside the C3, F-140-05 and F-140-07 corrections already queued there.
- **Fixing F-141-11** (`test_flash_path_record_sync.py` asserting whole-repo `git status --porcelain`
  instead of the one file it tests) — orphaned, unassigned. It will bite this phase too: commit
  in-flight changes before running the full firmware suite.
- **Fixing F-138-05** (`check_size_baseline.py`'s uncaught `KeyError` on an unknown native env) —
  inherited, accepted, not fixed. Owner `henols`. Do not pass `native_loop_v131` to it.

### Reviewed Todos (not folded)

- **"Skip VPP error/warning checks when VPP is unused (reads/blank-checks)"**
  (`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`, score **0.9**) —
  reviewed, **deferred again**, and this time with the reason recorded so it stops being
  re-litigated: `PROJECT.md`'s v1.31 out-of-scope list says "VPP validation behavior — unchanged
  except where a change is required for safe shared cleanup." Skipping the check on reads is a
  behaviour change, not shared cleanup. Deferred here by `139-CONTEXT.md`, `140-CONTEXT.md`,
  `141-CONTEXT.md` and now this phase; it needs an owner outside v1.31.
- **"Prove the PlatformIO dev-tools build flag fails CLOSED"** (score 0.9) — matched on
  "phase"/"check"/"set"; a build-flag question unrelated to HV routing.
- **"CONFIG_VERSION is not bumped when a calibration default changes"** (score 0.7) — matched on
  "vpp"; EEPROM config migration, backlog 999.1's territory, no overlap with routing.
- **"AT28C256 write-path failure (gh#20)"** (score 0.6) — protocol `0x0D`, a different family.
- **"Reply on gh#12 after `dev sdp` is retired"**, **"Photograph operator's Modified Rev 0 board"**
  (score 0.6) — bare-word matches; neither touches this phase. The Modified Rev 0 photo item is
  *adjacent* to D-02 (that board's revision detection is operator-attested only) but changes nothing:
  D-02's gate keeps today's behaviour on anything that does not resolve as Rev 2-class.

</deferred>

---

*Phase: 142-High-Voltage-Routing*
*Context gathered: 2026-08-11*
