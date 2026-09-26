# Phase 142: High-Voltage Routing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-11
**Phase:** 142-high-voltage-routing
**Areas discussed:** 0x08 DIP32 route truth, Disable-on-every-exit scope, FLAG_VPE_AS_VPP vs the table, VPP-04's missing gate

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| 0x08 DIP32 route truth | Drop bit stripped on pins>=32; table says drop-resistor but socket gets the un-dropped rail; check_vpp measures the other routing | ✓ |
| Disable-on-every-exit scope | Route bits vs regulator; the 500 ms per-block settle; the address-register vpp_line bit; wrapper vs per-return | ✓ |
| FLAG_VPE_AS_VPP vs the table | Live `--vpe-as-vpp` CLI flag vs table-driven `vpp_path`; shape of the shared mask set | ✓ |
| VPP-04's missing gate | No native over-voltage gate exists for the EPROM path; where to author it; flash-budget posture | ✓ |

**User's choice:** all four.

---

## 0x08 DIP32 route truth

### Q1 — What should Phase 142 do about the physical route?

| Option | Description | Selected |
|--------|-------------|----------|
| No HV change; record it | Keep the preserve-mask exclusion; make the resolved route honest in code and name the 0x08 consequence as a non-claim | |
| Make the drop survive on DIP32 | Change the preserve mask so the drop bit is held across set_address on pins>=32 | |
| Correct 0x08's table row instead | Change eprom_params.cpp's 0x08 row to name the route that physically happens | |
| **Other (operator)** | *"no exclutionn at all 32 pin ic's with vpp on pin one is controlled with a jumper"* | ✓ |

**User's choice:** free text — remove the exclusion entirely; pin-1 VPP routing on a 32-pin part is
handled by a **physical jumper**, not by the drop bit.

**Notes:** The jumper is JP4 (`JMP_VPP_P1_BYPASS`, silkscreen `P1_VPP_JMP`;
`firestarter/doc/SHIELD-REVISIONS.md` §7). This reframes the whole area: the drop bit is a VPP
**level** selector (VPE dropped through the resistor to ~13 V), so the `pins < 32` exclusion is a
level bug, not a routing guard. It also means removing it makes the write path finally match what
`eprom_check_vpp()` already measures. Phase 141's H1 had already disproved the bit-collision
justification the old comment gave. Became **D-01**.

### Q2 — How should the removal handle Rev 0 / Rev 1, where the drop bit and A16 are the same physical line?

| Option | Description | Selected |
|--------|-------------|----------|
| Remove unconditionally | Drop the guard on all revisions; Rev 0 VPP is already refused by `MSG_WARN_REV0_VPP_UNSUPPORTED` | |
| Gate on Rev 2-class at runtime | Preserve the drop bit only when the resolved revision is Rev 2-class; keep old behaviour on Rev 0/Rev 1 | ✓ |
| Remove + refuse 32-pin on Rev 0/1 | Drop the guard and add an explicit refusal — needs the last free ERROR id (0xBF) | |

**User's choice:** Gate on Rev 2-class at runtime.

**Notes:** The unconditional option's argument covered Rev 0 (already guarded) but **not Rev 1**,
which has no such guard. Cost concern raised and then retired during the discussion:
`rurp_get_hardware_revision()` resolves to a boot-cached static, and
`rurp_map_ctrl_reg_for_hardware_revision()` already calls it on every control-register write — so the
gate adds no new class of cost inside the per-byte address path. Became **D-02**.

### Q3 — Where should VPP-03's one shared routing-mask set live?

| Option | Description | Selected |
|--------|-------------|----------|
| rurp_pinout.h composites | Named composites beside the CTRL_* bits they are built from; header-only, zero flash | |
| eprom.h / eprom_params.h | With the 27C algorithm layer that owns vpp_path | |
| You decide | Let research/planning pick from the include graph and flash budget | ✓ |

**User's choice:** Claude's discretion.

**Notes:** Recorded default is the `rurp_pinout.h` composites, with the reasoning preserved so
research can override it on include-graph grounds. Became **D-07**.

### Q4 — Bench posture on changing the voltage that reaches 0x08 silicon?

| Option | Description | Selected |
|--------|-------------|----------|
| Ship it, claim nothing | Prove it in the control-register stream only; no support_status change, no "fixes AM27C020" | ✓ |
| Ship it, and try AM27C020 at 145 | Add an opportunistic bench attempt to Phase 145's list | |
| Hold the change for a bench-first phase | Land only the consolidation and the disable guarantee now | |

**User's choice:** Ship it, claim nothing.

**Notes:** The permitted headline is that `eprom_check_vpp()` and the write path now apply the same
routing — a firmware-correctness claim provable off-hardware. Became **D-03**.

---

## Disable-on-every-exit scope

### Q1 — Does VPP-02's "success" mean each block's success exit, or the write operation's?

| Option | Description | Selected |
|--------|-------------|----------|
| Operation-level success | Local disable at every error/abort exit; per-block success keeps the rail up; command_done() is the operation-level disable, made provable | ✓ |
| Block-level success too | Literal reading; costs ~64 s on a 64K Uno write (128 blocks x 500 ms settle) against a ~32 s typical write | |
| Block-level with a cheaper settle | Shorten the re-settle — but the value would be an unmeasurable guess this milestone | |

**User's choice:** Operation-level success.

**Notes:** The throughput arithmetic was decisive — the literal reading would more than triple a 64 K
write on a milestone whose stated benefit is "faster than today in the typical case", and would undo
LOOP-08. The backstop is traced, not hoped for: Phase 141 record §4 shows `command_done()` zeroes
`CONTROL_REGISTER` + both address bytes on **both** the success and abort paths. The phase owes a
test proving it, since nothing tests it today. Became **D-09**.

### Q2 — How should the disable be wired?

| Option | Description | Selected |
|--------|-------------|----------|
| Single-exit wrapper | Static inner function; the public entry point calls it then unconditionally disables | ✓ |
| Explicit call at each return | Named helper before every return; greppable but forgettable | |
| Both | Wrapper plus a source-contract pytest gate | |

**User's choice:** Single-exit wrapper.

**Notes:** Structural rather than gate-enforced — a future `return` inside the inner body cannot
escape it. "Both" was declined as a second mechanism for no additional guarantee. Became **D-10**.

### Q3 — Does the address-bus vpp_line bit count as a route to disable?

| Option | Description | Selected |
|--------|-------------|----------|
| No — control-register only | vpp_line is set on reads too (memory.cpp:418 ignores read_write); clearing it would be a read-path change the milestone excluded | ✓ |
| Yes — include it | Clear it on write-path exit for fuller de-energisation | |

**User's choice:** No — control-register only, recorded as a named non-claim.

**Notes:** `command_done()` clears the address latch at operation end; nothing else does. Became
**D-11**.

### Q4 — Which functions carry the guarantee?

| Option | Description | Selected |
|--------|-------------|----------|
| write_init + write_execute | The two functions a CMD_WRITE runs, including write_init's erase leg | |
| Every HV function in eprom.cpp | Also erase_execute, get_chip_id, check_chip_id, check_vpp as standalone commands | |
| You decide | Draw the boundary from a research-produced map of every control-register assertion | ✓ |

**User's choice:** Claude's discretion.

**Notes:** Recorded default is `write_init` + `write_execute`, with the boundary to be drawn from a
full map rather than from that list. Became **D-12**.

---

## FLAG_VPE_AS_VPP vs the table

### Q1 — What happens to --vpe-as-vpp once vpp_path drives selection?

| Option | Description | Selected |
|--------|-------------|----------|
| Still overrides the table | Table supplies the default; the flag forces direct-VPE on top | ✓ |
| Table wins; flag ignored on 27C | Pure table-driven selection; leaves a live CLI flag doing nothing | |
| Refuse when flag contradicts table | Fail closed — needs the last free ERROR id | |

**User's choice:** Still overrides the table.

**Notes:** It is a live user-facing flag (`cli_handlers.py:574`) set by **no** database entry — a pure
human escape hatch that matters for the 25 V NMOS parts and the manual-pot workflow. Keeping it means
no host change in a firmware-only phase, and it demotes the predicate from tier-1 protocol to tier-2
flag in the D-13 inventory — exactly the movement the golden's `frozen_for` note expects. Became
**D-06**.

### Q2 — Shape of the shared mechanism?

| Option | Description | Selected |
|--------|-------------|----------|
| One resolve function | Folds table vpp_path + flag + pins/revision into the mask actually used; called by check_vpp AND the write path | ✓ |
| Named mask constants only | Satisfies VPP-03's literal wording at zero flash cost but leaves selection duplicated | |

**User's choice:** One resolve function.

**Notes:** Centralising the **selection**, not just the bit constants, is what stops `check_vpp` and
the write path measuring different routings — the exact `0x08` defect that started this phase. Became
**D-05**.

### Q3 — The 0.9-scoring "Skip VPP checks when VPP is unused" todo?

| Option | Description | Selected |
|--------|-------------|----------|
| Defer again | Out of scope per PROJECT.md's own "VPP validation behavior — unchanged" line | ✓ |
| Fold it in | Cheapest it will ever be, since the phase is already inside eprom_check_vpp | |
| Promote it to the backlog | Give it a numbered slot and an owner outside v1.31 | |

**User's choice:** Defer again — with the reason recorded so it stops being re-litigated.

**Notes:** Deferred here by `139-CONTEXT.md`, `140-CONTEXT.md`, `141-CONTEXT.md` and now this phase.

---

## VPP-04's missing gate

### Q1 — Where should the EPROM over-voltage gate live?

| Option | Description | Selected |
|--------|-------------|----------|
| New suite in native_loop_v131 | Add test_vpp_eprom_v131 to the existing env's test_filter + -I; no seventh env, no baseline edit | ✓ |
| A seventh env, native_vpp_v131 | Cleaner separation; another run-by-name obligation and more platformio.ini surface | |
| Re-baseline native and put it there | The only option with real CI coverage; edits a live gate Phase 144 owns | |

**User's choice:** New suite inside the existing `native_loop_v131` env.

**Notes:** Forced by the pinned envs — `native` / `native_nodevtools` are asserted at exactly 141
cases / 17 suites, so a new case in `test_val_eprom` turns a live gate RED. The honest cost, to be
restated in the phase record: `native_loop_v131` runs in **no CI leg of either repository**. Became
**D-14**.

### Q2 — What must the gate prove?

| Option | Description | Selected |
|--------|-------------|----------|
| Refusal + no route left up | MSG_ERR_VPP_HIGH + ERROR, no HV route asserted on the refusal path, plus the FLAG_FORCE downgrade leg | ✓ |
| Refusal only | Smallest gate satisfying VPP-04's literal wording | |
| You decide | Let the planner derive the leg list | |

**User's choice:** Refusal + no route left up (+ FLAG_FORCE downgrade).

**Notes:** Refusal-only would pass even if the rewrite left the rail energised on the refusal path —
the exact failure VPP-02 exists to prevent. Became **D-15**. During this area it was also established
that VPP-04's "existing gate" **does not exist** for the EPROM path at all, recorded as **D-13**.

### Q3 — Flash-budget posture?

| Option | Description | Selected |
|--------|-------------|----------|
| Measure, record, stay RED | Same disposition as Phase 141; Phase 144 / TEST-08 reconciles | ✓ |
| Require net non-positive | Hold a consolidation phase to no growth on any target | |
| Hard stop on leonardo headroom | Add an explicit halt below a headroom floor | |

**User's choice:** Measure, record, stay RED.

**Notes:** Starting point recorded in CONTEXT.md D-16: leonardo at 26400 B / 92.1 % with 2272 B
headroom, and the 28672 B ceiling is a build **failure**, not a gate — Phase 143 still has to fit.

---

## Claude's Discretion

- **D-07** — where the shared mask set lives (default: `rurp_pinout.h` composites).
- **D-12** — the function boundary for the disable guarantee (default: `eprom_write_init` +
  `eprom_write_execute`, drawn from a research-produced map).
- Resolver naming/signature; whether the all-off composite is a `#define` or a small inline.
- Plan decomposition, wave structure, and which plan owns the D-13 golden re-derivation.

## Deferred Ideas

- Bench-validating the `0x08` route change on AM27C020 — opportunistic at Phase 145, not an obligation.
- Removing the exclusion on Rev 0 / Rev 1 — blocked by the physical bit alias.
- Clearing the address-bus `vpp_line` bit — D-11's non-claim.
- A measured, shortened re-settle constant — needs a scope on the boost rail.
- Claiming `0xBF` — left free for Phase 143.
- `native_trace_v131` re-freeze and the trace diff — Phase 144 / TEST-06.
- Cross-phase flash/RAM reconciliation and the baseline JSON — Phase 144 / TEST-08.
- Reconciling `PROJECT.md`'s DIP32 caveat (lines 125-127) against what shipped — Phase 146 / CLOSE-04.
- F-141-11 (`test_flash_path_record_sync.py`'s whole-repo porcelain assertion) — orphaned, unassigned.
- F-138-05 (`check_size_baseline.py`'s `KeyError` on an unknown native env) — inherited, owner `henols`.
- The "Skip VPP checks when VPP is unused" todo — deferred a fourth time; needs an owner outside v1.31.
