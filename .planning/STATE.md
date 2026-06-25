---
gsd_state_version: 1.0
milestone: v1.15
milestone_name: — Bench Validation of Operator Inventory
status: Awaiting next milestone
stopped_at: "Phase 84 Plan 06 complete — DECODE-AUDIT.md finalized; FIX-01 closed per D-43; GRAD-03/FUT-03 DEFERRED D-22; SC#3 gate GREEN; ready for /gsd-verify-work"
last_updated: "2026-06-25T10:43:10.715Z"
last_activity: 2026-06-25 — Milestone v1.15 completed and archived
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 15
  completed_plans: 15
  percent: 100
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-06-16

## Current Position

Phase: Milestone v1.15 complete
Plan: —
Status: Awaiting next milestone
Last activity: 2026-06-25 — Milestone v1.15 completed and archived

## Quick Tasks Completed

| ID | Task | Date | Status | Commit |
|----|------|------|--------|--------|
| 260625-f1g | Group dev write-cycle/consistency-check run folders under `firestarter-runs/` (was dumping in launch dir) | 2026-06-25 | complete ✓ | firestarter_app@bc55b29 |

## Project Reference

See: `.planning/PROJECT.md` (v1.15 Current Milestone section + Key Decisions)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative
from upstream XML → DB → wire JSON → firmware handler. No guessing. **v1.15 proves that
contract holds on real silicon** for the operator's 11-chip physical inventory.

**Current focus:** Phase 84 — db-decode-audit-conditional-defect-rca-milestone-evidence-co
read+blank-check sweep across all 11 chips on Leonardo + RURP Rev 2.0, establishing the evidence
record and the bench-safety baseline (SAFE-01/02/03) with zero chips consumed. Board LOCKED =
Leonardo + Rev 2.0 (only trustworthy program/write/verify combo); mostly host-side; firmware
untouched unless a bench-surfaced defect forces a lockstep fix. v1.14 `3.0.0b11` lockstep beta cut
remains OPERATOR-GATED (gitlinks PINNED). Standing carry-forward: deferred v1.9 read-bug RCA
(resumes at Phase 45 → FUT-C).

## Roadmap Summary

**v1.15 ACTIVE — 4 phases (81–84), 23/23 requirements mapped. Non-destructive-first ordering:**

- **Phase 81: 2516 DB Entry + Non-Destructive Read Sweep** (GRAD-01/02, SWEEP-01/02, EVID-01/02/03,
  DB-02, SAFE-01/02/03) — host-only, zero chips consumed. Author the `2516` user-override entry in
  `~/.firestarter/database.json` (algorithm 0x0B, pinout DIP24_2716, UV-EPROM, vpp_mv 25000, 2048 B)

  + **manual safety review** (the override bypasses `check_dispatch.py`/`diff_db.py`). Read +
  blank-check ALL 11 chips on Leonardo + Rev 2.0; record the per-chip EVIDENCE.{md,json} rows + the
  3 UV-EPROM blank-states (gates Phase 83). **Pre-write code review:** confirm `FLAG_CAN_ERASE` is
  derived for BOTH `EEPROM` and `Flash/EEPROM` types. Homes the SAFE-01/02/03 bench discipline.

- **Phase 82: Electrically-Rewritable Silicon Validation** (REWR-01..05, DB-01) — full
  write→(auto-erase)→read→verify with SHA for the 8 freely-rewritable chips: W27C512/W27E512/
  SST27SF512 (0x07), W27E040 (0x08), SST39SF040 (0x06), W29C020+W29C040 (0x05, confirm Flash/EEPROM
  auto-erase), FM1608 (0x40 overwrite). Reuse `write_test.sh` / `dev validate-family`; non-vacuous
  PASS (N≥3 Leonardo read + negative control); confirm DB decode vs silicon per chip.

- **Phase 83: UV-EPROM Write Proof** (UV-01..04, GRAD-03) — gated on Phase 81 blank-state; spend-vs-
  preserve decided per chip live at the bench (operator has no eraser → every UV write is
  irreversible). Blank → full image; non-blank → all-`0x00`/AND-mask (1→0 only). ST M27C512 (0x07) +
  AM27C020 (0x08) read+decode + write-proof-if-spent. The `2516` bench proof on the ~22.4V VPE rail
  (read via `firestarter vpe`, N≥3 SHA, fw under-voltage warning documented) **closes FUT-03**
  (best-effort per v1.14 D-07; over-voltage stays blocked).

- **Phase 84: DB Decode Audit + Conditional Defect RCA** (FIX-01) — consolidate the per-chip evidence
  into a decode-correctness audit (all 11 chips vs DB: pinout/VPP/type/algorithm/size). Conditional:
  any bench-surfaced defect is root-caused + fixed (host-only or dual-repo lockstep) + re-verified,
  with `check_dispatch.py`/`diff_db.py`/host suite green; else records "none found / bench clean".

**Build order (research-locked, safety-load-bearing):** 81 → 82 → 83 → 84 (non-destructive →
rewritable → UV-spend → audit). Phases 81–83 are sequential (Phase 83 cannot start until Phase 81's
UV blank-states are known). Phase 84 is conditional (documentation-only if 81–83 are clean).

**Cross-cutting safety (SAFE-01/02/03, homed in Phase 81, recur in 82–84):** every bench task records
board=Leonardo, shield=Rev 2.0 (operator-stated), `controller:` port identity, live R1/R2 readback
(`r1 ≈ 270000`); host suite green incl. the 0xA4 `test_init_phase_data_frames_not_acked` guard before
any session; no non-Leonardo read is authoritative; no UV part written before blank-check + explicit
spend decision; over-voltage blocked (under-voltage warn-and-proceed accepted best-effort).

**Standing bench precondition (every phase 81–84):** **Leonardo + RURP Rev 2.0 is the ONLY trustworthy
program/write/verify combo** (v1.9 read bug corrupts the oracle on Rev-0/Rev-2.0 elsewhere; uno328pb
N/A for program/write). For the 2516/0x0B NMOS rail use `firestarter vpe` (NOT `vpp` — that reads the
~15–19V dropped rail); chip-OUT before any Uno-class sideload (Leonardo EXEMPT); ASK which silkscreen
shield rev is mounted; verify `controller:` port identity per task after any USB event.

**Reuse-first:** NO new harness or third-party dependency (EVID-02). Reuse `firestarter write/read/
verify`, `dev validate-family`, `write_test.sh`, `check_dispatch.py`, `diff_db.py`. One new artifact:
`.planning/v1.15/bench/EVIDENCE.{md,json}` (extends, not replaces, the v1.13 per-family matrix).

**Pre-req:** Branches off `beta`. v1.14's `3.0.0b11` lockstep beta cut is operator-gated (gitlinks
PINNED); v1.15 host work proceeds on the `v1.14-feasible-gap-implementation` continuation / a v1.15
branch per standing policy. Firmware likely untouched (Leonardo ~89.5% flash, `configure_eprom`
0x07/0x08/0x0B handles all UV families incl. the 2516).

**Prior milestones:** v1.14 SHIPPED 2026-06-23 (Phases 77–80; first chip graduations since v1.0). v1.13
SHIPPED 2026-06-18. v1.12 SHIPPED 2026-06-16. v1.11 SHIPPED 2026-06-10. v1.10 SHIPPED 2026-06-07. v1.9
Read-Bug RCA DEFERRED (Phases 45–48; resume at Phase 45 → FUT-C).

## Accumulated Context

### Roadmap Evolution

- v1.15 roadmap created 2026-06-23: 4 phases (81–84) derived from the 23 v1.15 requirements
  (EVID/SWEEP/REWR/UV/GRAD/DB/FIX/SAFE) along the research-locked non-destructive-first spine
  (81 read-sweep+2516-entry → 82 rewritable write/verify → 83 UV-spend → 84 audit/RCA). 23/23
  mapped, no orphans/duplicates (Phase 81: 11 · Phase 82: 6 · Phase 83: 5 · Phase 84: 1).
  SAFE-01/02/03 cross-cutting, homed in Phase 81 (first bench phase establishing the
  port-identity + r1 + Leonardo-only-authoritative discipline) and recurring as preconditions/
  success-criteria in 82–84 (v1.14 SAFE-pattern precedent). GRAD-01/02 (2516 research + entry +
  manual review) home in Phase 81; GRAD-03 (2516 bench proof, closes FUT-03) in Phase 83. DB-02
  (FLAG_CAN_ERASE Flash/EEPROM review) precedes any write → Phase 81; DB-01 (per-chip decode-vs-
  silicon) in Phase 82. FIX-01 is conditional (closes "none found" if the bench is clean) → Phase

  84. Phases 81→82→83 sequential (Phase 83 gated on Phase 81 UV blank-states); Phase 84
  documentation-only if clean. Phase 83 (2516 NMOS under-voltage at ~22.4V VPE) flagged for
  `--research-phase` at planning (no prior 2516 silicon data; second NMOS data point after Phase 79).

- v1.14 roadmap created 2026-06-18: 4 phases (77–80) derived from the 15 v1.14 requirements
  (ERASE/XIC/NMOS/ADPT/SAFE) — one phase per feasible gap along the operator-locked build order
  999.4 → 999.5 → 999.7 → 999.6. 15/15 mapped, no orphans/duplicates. SAFE-01/02/03 cross-cutting,
  mapped to Phase 77 (first graduation establishing guard-removal-last + check_dispatch + lockstep
  parity) and recurring as success criteria in 78–80. Each phase's graduation gate (flip
  `support_status`→`supported` + drop the host guard) is the FINAL step. Phase 78 (X88C64) leads
  with an ALE-routing bench investigation + a `pio run -e leonardo` ≤~90% flash gate; Phase 79 (25V)
  leads with an `autonomous: false` operator multimeter ≥25V dry-run; Phase 80 (adapter) is
  hardware-blocked and defers cleanly. The ROADMAP §v1.14 Backlog stubs 999.4–999.7 were promoted
  (marked ✅ PROMOTED → Phase 77/78/79/80) and removed from the pending backlog.

- v1.14 captured to Backlog 2026-06-18 (operator request): 4 feasible-gap **implementation** phases that
  graduate chips to `supported` (OUT of v1.13's validation-only scope) → ROADMAP §Backlog 999.4–999.7.
  999.4 erase write-path (skipped v1.13 Phase 75, most ready), 999.5 X88C64 0x34 handler, 999.6 AT28C04/16
  adapter graduation (hardware-blocked), 999.7 25V NMOS M2716/M2732 ceiling raise (was infeasible at 22V —
  operator opted to implement assuming HW can do 25V; gating risk = confirm a shield can produce 25V VPP).
  Promote via `/gsd-new-milestone v1.14` after v1.13 close (operator-gated beta cut still pending), NOT into v1.13.

- v1.13 roadmap created 2026-06-16: 6 phases (71–76) derived from the HARN/RSCH/VAL/FIX/ERASE/GAP
  requirements along the research-derived harness→validate→fix→gaps spine, flash-ceiling-ordered.
  17/17 requirements mapped, no orphans/duplicates. FIX-01 (SRAM) is evidence-gated on VAL-06;
  GAP-01/02 are spec-only (graduation to `supported` deferred). RSCH-01 (Phase 72) lands before any
  flash-budget firmware commit. Phases 75 + 76 flagged for `--research-phase` at planning (erase
  12V→14V rail; X88C64 0x34 protocol; DIP24 adapter pin-map).

### v1.13 Scope Notes (research 2026-06-16, HIGH confidence)

- **No new third-party deps** — both substrates installed + green: firmware native = PlatformIO
  `[env:native]` + Unity + ArduinoFake `^0.4.0` (8 suites passing); host = pytest + syrupy + ruff/mypy

  + pyserial with `make_comm`/`fake_serial` no-port fixtures. REUSE `write_test.sh`,
  `eprom_operations.py` cycle methods, `check_dispatch.py`, `diff_db.py` — do NOT rewrite/fork.

- **v1.12 "feasible set complete" overstated** — 3 genuine RURP-feasible gaps survive: erase path
  (0x07, electricals exist), `configure_sram` empty no-op (validate-first), X88C64 0x34
  (parallel 5V DIP EEPROM, MEDIUM — needs datasheet protocol). Anti-features stay fail-closed.

- **Two coupled failure classes dominate:** false-PASS (untrustworthy verify read board → pin PASS
  to Leonardo + clean shield, N≥5 SHA, negative control) and chip-destruction (wrong VPP/algorithm →
  register-bit native tests via recording stub + chip-OUT VPP meter dry-run, never bypass host guard).

- **999.1 / 999.2 are confounders, not in-scope fixes** — live R1/R2 readback at every VPP-dependent
  bench task is the discriminator; uno328pb = N/A for program/write.

### ⏸ v1.9 DEFERRED (operator 2026-06-08 — resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused. Phase 44 (Bug A RCA) complete; Phase 48 plan 48-01 (COBS
verdict) complete. Remaining: Phases 45–48. The v1.13 verify oracle is pinned to Leonardo precisely
to avoid the v1.9 shield-fleet read bug; v1.13 does NOT touch it.

### v1.10 Substrate (carry-forward)

- Transport provably byte-exact (COBS `0x00` + CRC8-CCITT) — settled variable.
- GATE-1.8d ring-fence: `_read_and_parse_lines` body byte-identical; baseline binaries valid.

### Pending Todos (carried forward)

- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred
- `large-read-data-jitter-uno328pb.md` (HIGH, v1.8-seed) — v1.9 RCA target (NOT v1.13)

### Blockers / Concerns

None at roadmap start. v1.13 closes at PARTIAL bench coverage under hybrid gating — Tier 1/2 are
fully software-provable; Tier 3 is best-effort on parts-on-hand. Dual-repo lockstep (firmware + host)
applies to any wire-touching fix; watch the py3.12-masks-CI-3.11 ruff/codegen drift trap.

## Session Continuity

Last session: 2026-06-25T10:12:21.730Z
Stopped at: Phase 84 Plan 06 complete — DECODE-AUDIT.md finalized; FIX-01 closed per D-43; GRAD-03/FUT-03 DEFERRED D-22; SC#3 gate GREEN; ready for /gsd-verify-work
Resume: Phase 83 (UV-EPROM Write Proof) — `/gsd-discuss-phase 83` or `/gsd-plan-phase 83`. **GATED:** Phase 83 needs the Phase-81 UV blank-states (ST M27C512 BLANK / AM27C020 NOT-BLANK / 2516 read-unstable→no write until read path stable); operator has no eraser so every UV write is irreversible (spend-vs-preserve decided live). **BENCH NOTE:** board is now **fw 3.0.0b10** (reflashed in Phase 82, was b8); flash4 has no bulk-erase (per-page auto-erase via `write -b`). Carry-forward: W29C040 flash4 page-write fault → Phase 84 / reopen Phase-74 Wave-2; deferred v1.9 read-bug RCA (Phase 45); v1.14 FUT-01/03/04; operator-gated lockstep beta cut (`3.0.0b11`, gitlinks PINNED).

## Decisions

- [Phase 79-02, 2026-06-23]: NMOS-02 executed under the CONTEXT D-07 operator override (supersedes D-05/D-06). Despite the 79-01 gate being below the strict ≥25V bar (VPE = 22.4V DMM / 23.9V fw `firestarter vpe`; the ~15-19V earlier logged was VPP, not VPE), the operator authorized BEST-EFFORT graduation with NO hardware change ever. Raised RURP_VPP_CEILING_MV 22000->25000 (build_db.py) + check_dispatch.py configure_eprom invariant (0,22000)->(0,25000) in one commit; regenerated chip_database.json so INTEL M2716, INTEL 2732/2732A/M2732/M2732A, SGS-THOMSON ETC2716, ST ETC2716 graduate vpp-exceeds-max->supported (algo 0x0B, vpp_mv=25000); zero vpp-exceeds-max chips remain; M2732A (21V) untouched; check_dispatch.py exits 0 (734/10/0). The chips attempt a write on the existing 0x0B direct-VPE rail where the firmware warns-and-proceeds on under-voltage (over-voltage still blocked) — best-effort, the user opts in. FUT-02 (>25V fail-closed) preserved by the strict-greater compare + a new negative-control test. Re-anchored 7 vpp-exceeds-max test exemplars to X88C64P/AT28C04 + added 3 non-vacuous tests; regenerated the golden coverage matrix (4 chips 0x00->0x0B). REQUIREMENTS.md FUT-03 corrected to the manual-potentiometer + best-effort framing. Submodule commits 1498786 (feat) + 26cc62d (test) on v1.14-feasible-gap-implementation; gitlink pinned. 79-03 demoted to informational bench validation.
- [Phase 79-01, rail-corrected 2026-06-23]: NMOS-01 gate measured at MAX pot on leonardo @ /dev/ttyACM0, shield Rev 2.0, R1=270000/R2=44000. RAIL READINGS (operator-corrected): **VPP ~15-19V** (DMM) / 18.7V (fw `firestarter vpp`, dropped path); **VPE = 22.4V** (DMM, authoritative) / 23.9V (fw `firestarter vpe`, direct path). The 4 NMOS chips are 0x0B → eprom_check_vpp + eprom_write_execute use CTRL_VPP_REGULATOR_ENABLE-only (0x80, = `firestarter vpe`), so they program off the **~22.4V VPE rail** (~90% of 25V). At the strict ≥25V bar this is NOT CLEARED (22.4 < 25), but that bar was RETIRED by operator override D-07 (best-effort graduation, no HW change ever). Firmware warns under-voltage (22.4V < 23.75V = 95% thresh) and proceeds; over-voltage stays blocked. CAVEAT: the fw ADC reads the regulator rail (23.9V), not the socket-delivered pin (22.4V DMM) — definitive proof is the 79-03 bench write+SHA. CORRECTS the earlier entry that mis-attributed the ~15-19V VPP reading to VPE and wrongly concluded a boost-stage HW change was needed. Supersedes the 2026-06-22 wrong-rail `firestarter vpp` run below.
- [Phase 79-01 — SUPERSEDED 2026-06-22 wrong-rail run]: prior NOT-CLEARED used `firestarter vpp`, which forces the DROPPED 0x07/0x08 ~12V path (hardware_operations.cpp:28) — the wrong rail for these 0x0B chips. Verdict superseded by the corrected re-run above (CONTEXT D-03). Kept for history; do NOT treat its ~12V / PCB-resistor framing as current.

_(v1.13 decisions will be recorded here as phases execute.)_

- [Phase 82, 2026-06-24]: SHIPPED — rewritable A→B silicon validation, 8 chips, **5 PASS / 3 FAIL**, verification PASSED (REWR-02 operator-deferred). PASS: W27C512, SST27SF512 (0x07), SST39SF040 (0x06), FM1608 (0x40 overwrite), W29C020 (0x05 — auto-erase proven = FLAG_CAN_ERASE Flash/EEPROM branch first silicon confirmation, REWR-04 SC#3). Every PASS non-vacuous (consistency-check N=3 + neg-control verify(A) RC=1). FAILs: W27E512 (0x07 stuck bit @0x3d) + W27E040 (0x08 stuck bit @0x7db) = genuine silicon wear (deterministic across reseats, decode/erase engaged correctly — NOT algo/DB faults); W29C040 (0x05) flash4 page-write timeout @0xff/256B boundary. EVIDENCE.{md,json} = 19 cells (11 Phase-81 read preserved + 8 Phase-82 write). One code artifact: firestarter_app/tools/gen_test_image.py (deterministic random.Random(seed) image oracle) + 12 pinning tests, ruff-clean, 663 host tests green (SAFE-02). No inline chip_database.json edit; 3 DB-01 type observations recorded for Phase 84.
- [Phase 82, 2026-06-24] FW DEVIATION: board reflashed **3.0.0b8 → 3.0.0b10** mid-phase (operator-authorized) to get the Phase-74 flash4 W29C040 SDP/256B-page fix. NO firmware SOURCE changed (firestarter submodule untouched on beta; b10 is the existing v1.13 release via `firestarter fw --install --firmware-version 3.0.0b10`). Calibration persisted (R1=270000/R2=44000), port stayed /dev/ttyACM0. Phase 81 + 82-02 ran on b8; 82-03 on b10. flash4 has NO working bulk-erase on either (standalone `erase` is a 0.06s no-op) — per-page auto-erase fires during `write -b` (write-cycle blank-checks so it can't drive flash4; used direct `write -b` like FM1608).
- [Phase 82, 2026-06-24] CRITICAL → Phase 84 / reopen Phase-74 Wave-2: **W29C040 (512KB flash4) FAILs on real silicon** at the 256B page-0 boundary (mid-page-poll timeout @0xff, byte stays 0x00) on b10 — this is the FIRST real-silicon test of the Phase-74 W29C040 SDP/256B-page fix (Phase-74 Wave-2 re-bench was DEFERRED, fix was native-test-only). Inverts the CR-01 expectation: the supposedly-affected W29C020 (256KB) PASSED clean, the supposedly-correct W29C040 (512KB) FAILED. Phase-84 FIX-01 headline (likely dual-repo lockstep firmware fix).

<details>
<summary>v1.12 decisions (archived — milestone shipped 2026-06-16)</summary>

- [Phase 62-01]: D-BETA-STATE: beta branch already has 0x35/0x39 explicit dispatch arms; TestDispatchGate02 tests 1+2 are GREEN now (not RED as planned); only protocol!=0 not_implemented arm is missing
- [Phase 62-02]: D-CHIP-COUNT: DB on v1.12 branch has 734 chips (not 743 as plan expected) — v1.11 work not yet reconciled into beta; dispatch_baseline.json correctly captures the actual current DB state
- [Phase 63-01]: D-01 honored (0xBB mirrors 0xAE); D-04 honored (py3.11.13 from source, drift gates green); D-05 honored (firestarter_app gitlink not bumped)
- [Phase 65-01]: _raise_for_error_response(response, message): response.id for typed dispatch, message for EpromOperationError framing
- [Phase 65-01]: SC#2 test asserts on _execute_phase — outer _run_state_machine except swallows typed raise before caller sees it
- [Phase 65-01]: GATE-1.8d ringfence pin updated for planned Response.id addition (v1.12 in-scope)
- [Phase 65-02]: Option B applied — expect_ack raises ProtocolNotImplementedError when response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED; Tuple[bool, Optional[str]] arity unchanged; zero caller-unpacking edits needed
- [Phase 65-02]: WR-02 closed — all 4 state-machine ERROR sites now route through _raise_for_error_response; production-path proven by Test A integration test (REAL EpromOperator + CliRunner)
- [Phase 66-03]: support_status taxonomy (supported|protocol-not-implemented|adapter-required|vpp-exceeds-max) now on every chip in chip_database.json (744 chips); RURP_VPP_CEILING_MV=22000; highest-VPP-wins for NMOS combined entries (M2716/M2732=25V/vpp-exceeds-max, M2732A=21V/supported)
- [Phase 66-03]: D-11 authorized: dispatch_baseline.json regenerated to 744 chips; all 10 new chips enumerated in commit message and SUMMARY.md
- [Phase 66-03]: D-03 HARD honored: adapter-required 24-pin EEPROMs keep original proto_id, no working handler wired; check_dispatch assertion 1 confirms all 9 carry unsupported_reason
- [Phase 66-04]: CR-01 Option A applied — NON_DISPATCHABLE_ALGO=0x00 at Site B (adapter-required) + Site C (vpp-exceeds-max); dispatch(0x00, None)→ERROR; D-03 HARD enforced at data layer; DB-05 SATISFIED
- [Phase 66-04]: CR-02 applied — non_supported_dispatchable bucket in check_dispatch.py; PASS message truthful; gate now detects dangerous inverse (non-supported→real handler)
- [Phase 66-04]: IN-03 applied — 8th CI test pins SC#3 invariant; 494 tests green; cov≥70
- [Phase 66-04]: D-11 authorized deviation — 13 dispatch_baseline.json triples changed (0x0B/configure_eprom → 0x00/ERROR); reviewed and enumerated in SUMMARY.md
- [Phase 66-04]: errors bucket fix (Rule 1) — guard on chip_ss==supported so non-supported ERROR outcomes are not false-failed
- [Phase 66-05]: D-12 honored — ChipNotImplementedError host guard in resolve_chip closes 12V-VPP hazard; check_dispatch realigned to _map_data etype fallback; DB-05 satisfied at runtime boundary
- [Phase 69-01]: Inline scalar-extraction at each pin-field site — no named helper, matching database.get_bus_config pattern
- [Phase 69-02]: REAL EpromConsolePresenter(db) injection required for info tests — default Mock returns None from prepare_detailed_eprom_data and masks the ic_layout fix
- [Phase 69-02]: All three SC#3 non-supported statuses pinned at CLI: vpp-exceeds-max (M2716), adapter-required (AT28C16), protocol-not-implemented (X88C64P); info DISPLAYS all three; chip-ops refuse with typed exit 1
- [Phase 69-02]: X88C64P is the sole protocol-not-implemented chip in chip_database.json (part_number alias "X88C64P,X88C64S", protocol 0x34 XICOR NovRAM); no DB churn needed
- [Phase 69-03]: Watermark bumped 26→29: honest post-fix floor (ic_layout fix 2 new mypy errors + Phase 65 test 1); no config loosening; SC#4 full CI gate green
- [Phase 67.1-01]: D-02 Option B applied — native-28-pin SRAM block in main() loop after fm1608 override; avoids resolve_pinout_key signature change; parallels existing fm1608 override pattern
- [Phase 67.1-01]: D-01 Approach A applied — unsupported_reason strings reworded in build_db.py (Sites A/B/C); DB is single source of truth; Plan 02 will print f"{e}" verbatim
- [Phase 67.1-01]: DB-02 closed — 14 SRAM chips corrected (4 × DIP24_6116 Group 1; 10 × DIP28_JEDEC_SRAM_8K/DIP28_28C256 Group 2); diff_db: 14 SRAM_PINOUT; check_dispatch: 730/14 GREEN
- [Phase 67.1-01]: DB-04 SC#2 source half closed — reason strings begin with "VPP Xv exceeds programmer max" / "adapter required:" / "protocol not implemented:"; 520 tests green
- [DB-04 Approach A]: map_typed_errors renders ChipNotImplementedError reason verbatim; dropped Chip not usable prefix — DB string is single source of truth for both info display and chip-op refusal
- [DB-04 SC#1]: info injection gated on support_status != supported (Pitfall 3 compliance); caplog used to capture logger.warning in CliRunner tests where _setup_logging is bypassed

</details>

- [Phase 71]: HARN-03 closure: TRUST write_cycle_eprom return code directly; verdict_int==0 maps to board-class PASS via pass_type field, no source==source self-compare
- [Phase 71-08]: CR-02 resolution: flash4 host matrix trimmed to protocols=[5]; 0x35/0x39 omitted (zero DB chips, host never dispatches); rationale in protocols_note; firmware truth + native coverage preserved in test_val_flash4.cpp; drift gate green at 11 rows
- [Phase ?]: A1-RESOLVED: standalone erase already reaches eprom_internal_erase; Phase 75 scope = wire FLAG_CAN_ERASE from electrical.type in convert_to_programmer
- [Phase ?]: A2-RESOLVED: 0x2B is GAL/PLD family (memory.cpp:107-110); protocol-id.md lacks 0x2B row (documentation debt)
- [Phase ?]: SRAM-VERDICT: 0x0E/0x27/0x28/0x29 classified feasible-and-implemented (behavior deferred Phase 73 VAL-06); generic memory_write_execute fires before configure_sram
- [Phase ?]: V1.12-OVERSTATED: 3 areas - SRAM no-op (sram.cpp:15-17), FLAG_CAN_ERASE routing gap (database.py:594-597), X88C64 0x34 feasible-gap
- [Phase ?]: [Phase 73-01]: firestarter config -r1 writes to Arduino EEPROM only; r1 gate armed by writing r1=270000 directly to ~/.firestarter/config.json
- [Phase ?]: 73-02: A1-CONFIRMED: W27C512 erase fires correctly in write_cycle_eprom; Tier-3 PASS authoritative on Leonardo
- [Phase 73-03]: DEV: flash3/AM29F040 SKIP-deferred (no chip, operator 2026-06-17); flash4/W29C040 FAIL (hw-error): erase doesn't produce 0xFF blank, write verification timeout → Phase-74 candidate
- [Phase 73-03]: configure_flash4 (algorithm 5) incompatible with W29C040 SDP/page-write sequence; erase "succeeds" but chip not erased to 0xFF; write init blank-check fails; standalone write -b times out at 0x3f
- [Phase ?]: VAL-06 = table-stakes-PASS: configure_sram writes via generic_memory_write_execute; FIX-01 closed not-needed with evidence
- [Phase ?]: FM1608 erase probe: exit 1 (Not supported) — configure_sram CMD_ERASE errors; write -b direct path is the only viable FRAM write approach (Pitfall 3 confirmed)
- [Phase ?]: D-03 named arm fires AFTER Site B to overwrite generic reason with named-arm wording referencing AT28C04-ADAPTER.md; proto_id demotion stays in Site B
- [Phase ?]: D-02 X88C64P reason: parallel DIP24 5V EEPROM, 8051 multiplexed-bus (ALE/WR/RD); feasible-candidate, handler not implemented; no support_status change
- [Phase ?]: D-04: two-layer adapter spec (firestarter/doc/ + .planning/), pin-map verified, /WE reroute chip pin 21 → socket pin 30, DIP32_28C512_EEPROM confirmed
- [Phase ?]: D-01: X88C64P NO STORE/RECALL pins (those are X2210/X2212 NOVRAM family); X88C64P is parallel DIP24 with 8051 multiplexed ALE/WR/RD bus; MEDIUM feasibility-candidate; handler deferred, 0x34 not committed
- [Phase ?]: [Phase 78-01]: A6 VERDICT PCB-BLOCKED (HIGH) — control register fully allocated 0x01..0x80 (rurp_pinout.h:74-97); 0x100 non-transmissible via uint8_t rurp_write_data_buffer (rurp_shield.h:118); no free 74HC573 strobe; D-02 bar prohibits busy-bit reuse. Plan 02 takes deferral branch.
- [Phase ?]: [Phase 78-01]: XIC-04 graduation deferred to FUT-01 — no physical X88C64P chip/adapter (D-04) + PCB-blocked ALE; X88C64 stays protocol-not-implemented + host-refused; SAFE-01/02/03 hold trivially (no code change).
- [Phase 78-02]: Contingent handler-write plan took DEFER branch (Branch A) — leading [BLOCKING] gate read A6 VERDICT: PCB-BLOCKED directly; D-02 prohibits busy-bit reuse so proceed-path unauthorized. Appended `Branch A — ALE PCB-blocked, no handler code; graduation deferred FUT-01.` to X88C64-FEASIBILITY.md; Tasks 2-5 skipped; firestarter src/include/test + firestarter_app pinouts/DB/chip_resolver all CLEAN; X88C64P support_status unchanged (protocol-not-implemented); host-guard intact. XIC-02/03 vacuous on this branch.
- [Phase ?]: gen_test_image.py uses random.Random(seed) for deterministic full-size images; seed recorded in EVIDENCE enables reproducible SHA oracle
- [Phase 83-01, 2026-06-24]: SAFE-02 software preflight GREEN — host suite 663 tests + 0xA4 guard `test_init_phase_data_frames_not_acked` + CI-scoped ruff (`firestarter/ tests/`) all pass. Generated the 2 UV write payloads in `/tmp/firestarter_bench_p83/`: `ST_M27C512_img.bin` (65536B, `gen_test_image 65536 seed=1`, SHA `604d9570…1645d637`, reproducible) + `AM27C020_zeros.bin` (262144B all-0x00, SHA `8a39d2ab…589b4a90` == sha256 of 262144 zero bytes). EVIDENCE.md Phase 83 section scaffolded: scope to 2 read-stable UV chips (ST M27C512 + AM27C020), 2516/GRAD-03/SC#4/FUT-03 DEFERRED to Phase 84 (D-01) with the D-08 PASS bar pre-recorded, empty write-proof results table. Zero source/firmware/dep change (EVID-02). Broad `ruff check .` `tools/`-tree findings flagged out-of-CI-scope (pre-existing, ci.yml gates `firestarter/ tests/` only), NOT masked.
- [Phase ?]: Phase 84-02: D-30 SRAM/FRAM blank-check short-circuit implemented in check_eprom_blank() via _SRAM_PROTO_IDS = frozenset({0x0E, 0x27, 0x28, 0x29}). Detection by electrical-type (SRAM/FRAM) OR protocol-id membership fires before _operation_context. Prevents 0xA4 MSG_ERR_EMPTY_INPUT for FM1608 and all SRAM families. Wire/firmware/messages.py unchanged (D-11/D-30).
- [Phase ?]: Phase 84-03 sst-keep: SST39SF040 stays Flash/EEPROM; relabeling drops FLAG_CAN_ERASE; Phase-77/82 auto-erase preserved
- [Phase ?]: Phase 84-03 fm-fram-full: FM1608 SRAM→FRAM at build_db.py codegen layer; _ELECTRICAL_TYPE_LABEL['FRAM']='FRAM'; VPP gate not-in-{SRAM,FRAM}; CAN_ERASE unaffected (FRAM not in {EEPROM,Flash/EEPROM}); 673/673 tests green
- [Phase 84-05]: 2516 read still unstable (N=3, 3 distinct SHAs, 1.9% divergence) after VPP-skip; instability not solely VPP-gated; GRAD-03/FUT-03 DEFERRED (D-22); AM27C020 0x08 write 0-bits (FUT-06); W29C040 flash4 Phase-74 fix not silicon-effective (reopen CR-01/Phase-74-Wave-2); FIX-01 closed by disposition
- [Phase ?]: FIX-01 CLOSED per D-43 — in-posture fixes shipped + bench-confirmed; deferrals named (FUT-06/CR-01); milestone close operator-gated
- [Phase ?]: GRAD-03/FUT-03 DEFERRED best-effort (D-22) — 2516 read still unstable N=3 after Phase-84 VPP-skip re-bench; intentional deferral, not a gap
- [Phase ?]: SC#3 full software gate GREEN — check_dispatch/diff_db/ruff/native all exit 0; pio native 87/87; live-board test artifact is pre-existing/non-regression

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| _(v1.13 metrics recorded here as plans execute)_ | | | |

<details>
<summary>v1.11 / v1.12 performance metrics (archived)</summary>

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| 57 | 01 | 26min | DEC-02/03/04/05 decode fixes in build_db.py; 10 new tests; ruff clean |
| 57 | 02 | 18min | GATE-03 full-class VPP guard; check_dispatch.py extended; 0 violations |
| 57 | 03 | ~45min | DB regenerated (734 chips); W27C512=100us; GATE-03 on regen set; 480 tests green |
| 58 | 02 | 35min | 2 tasks / 5 files |
| 59 | 02 | ~4min | GATE-04 SRAM audit; configure_sram near-no-op confirmed; 3 NVRAM truths documented |
| 61 | 01 | 40min | — |
| 62 | 01 | 10min | 2 tasks / 1 file |
| 62 | 02 | 8min | 1 task / dispatch_baseline.json |
| 62 | 03 | 15min | 2 tasks / 1 file |
| 63 | 01 | 35min | — |
| 65 | 01 | 17min | — |
| 65 | 02 | 10min | 3 tasks / 3 files |
| 66 | 03 | 40min | 2 tasks / 5 files |
| 66 | 04 | 45min | 3 tasks / 7 files |
| 66 | 05 | 40min | — |
| 69 | 01 | 20min | 2 tasks / 5 files |
| 69 | 02 | 20min | 2 tasks / 2 files |
| 69 | 03 | 10min | 1 task / 1 file |
| 67.1 | 01 | 35min | 2 tasks / 3 files; 14 SRAM pinouts corrected; 7 new tests; 520 tests green |
| 67.1 | 02 | 25min | — |

</details>
| Phase 71 P07 | 8min | 2 tasks | 3 files |
| Phase 71 P08 | 7min | 2 tasks | 4 files |
| Phase 72 P01 | 45min | - tasks | - files |
| Phase 73 P02 | 3min | - tasks | - files |
| Phase 73 P03 | 8min | 1 task | 6 files (flash3 SKIP-deferred + flash4 FAIL verdict W29C040) |
| Phase 73 P04 | 8min | - tasks | - files |
| Phase 74 P01 | 3min | 2 tasks | 4 files |
| Phase 76 P01 | 8min | 3 tasks | 3 files |
| Phase 76 P02 | 12min | - tasks | - files |
| Phase 78 P01 | 12min | 2 tasks | 1 files |
| Phase 78 P02 | 6min | 1 task | 1 files (DEFER branch — zero code changes) |
| Phase 82 P01 | 20min | - tasks | - files |
| Phase 83 P01 | 7min | 2 tasks | 1 files |
| Phase 84 P01 | 12 minutes | 3 tasks | 3 files |
| Phase 84 P02 | 9min | - tasks | - files |
| Phase 84 P05 | 15min | 3 tasks | 2 files |
| Phase 84 P06 | 8min | 3 tasks | 2 files |

## Deferred Items

**Re-acknowledged at v1.15 milestone close (2026-06-25):** the pre-close `audit-open` reported **12 open
items** — all either pre-existing carry-forwards (re-confirmed below; none are v1.15 work) or intentional
v1.15 deferrals. The operator chose **Acknowledge & close**. Notable v1.15-specific dispositions: Phase 84
VERIFICATION reads `human_needed` only because the D-22/D-43 disposition sign-offs are operator judgment
calls — **both already operator-accepted** (the frontmatter status line was simply not flipped); 2 new
firmware/docs todos (`skip-vpp...on-reads` — VPP-skip already SHIPPED in 84-01; `gather-protocol-datasheets`
— v1.16 seed) are deferred captures, not gaps. The stale `v1.15-MILESTONE-AUDIT.md` (`gaps_found`) predates
Phase 84; its two gaps (GRAD-03, FIX-01) are now closed-by-disposition. See
`.planning/milestones/v1.15-MILESTONE-AUDIT.md` (stale) + Phase-84 VERIFICATION/SECURITY for rationale.

**Re-acknowledged at v1.14 milestone close (2026-06-23):** the 9 cross-milestone open-artifact
items below were re-confirmed via `gsd-tools audit-open` — **none are v1.14 work** (all pre-existing
from v1.0–v1.13: out-of-scope, accepted tech debt, or hardware-gated). Plus **3 v1.14-specific
hardware-gated deferrals** (FUT-01/03/04) — the intentional, operator-authorized gaps the v1.14
milestone audit flagged (`gaps_found`, but deferrals-by-design, not failures). See
`.planning/milestones/v1.14-MILESTONE-AUDIT.md` for the full v1.14 deferral rationale.

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| debug | firmware-vpp-misread (999.1) | diagnosed | uno328pb R1 recal applied Phase 54 UAT; CONFIG_VERSION propagation gate = ROADMAP Backlog 999.1; v1.13 guards via live-R1 precondition |
| debug | uno328pb program brownout (999.2) | parked | ROADMAP Backlog 999.2; v1.13 marks uno328pb N/A for program/write |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 | Pre-v1.10 FRAM byte-0 write investigation; out of v1.13 scope |
| uat | Phase 08 (08-HUMAN-UAT.md) | partial (2 pending) | v1.0-era logging phase; out of scope |
| verification | Phase 08 / Phase 09 VERIFICATION.md | human_needed | v1.0-era logging phases; out of scope |
| todo | avrdude-mcu-detection-fallback.md | low | Carry-forward; out of scope |
| todo | cobs-decoder-framelevel-deadline-wr01.md | medium | v1.10 COBS follow-up (WR-01); deferred |
| todo | flash4-page-size-datasheet-sourced-cr01.md | medium | v1.13 Phase 74 CR-01 — data-driven page size shipped; replace residual capacity heuristic with datasheet per-chip value (refinement) |
| verification | Phase 71 (71-VERIFICATION.md) | gaps_found (stale) | Both verifier gaps CLOSED by follow-up plans 71-07 (non-vacuous oracle) + 71-08 (flash4 spec-trim); status line never re-run |
| phase-deferral | Phase 74 Wave-2 (W29C040 HW re-bench) + Phase 75 (erase path) | deferred to v1.14 | Backlog 999.4; hardware-gated (Leonardo+Rev2.0 T-74-VPP multimeter gate; erase 12V→14V rail confirm under 22V ceiling) |
| phase-graduated | Phase 79 NMOS-02 (25V ceiling raise + NMOS graduation) | DONE best-effort (D-07) | NMOS-02 shipped 2026-06-23: ceiling 22000→25000, 4 NMOS chips `supported` (0x0B). VPE rail = 22.4V DMM / 23.9V fw (~90% of 25V); ≥25V bar retired by operator (no HW change ever); chips program best-effort where FW warns under-voltage + proceeds. The earlier ~15-19V was VPP, not VPE. 79-03 bench write+SHA is informational, deferred (no chip on hand). Evidence: 79-01-SUMMARY.md + 79-CONTEXT.md D-07 |
| FUT-01 (v1.14) | X88C64 0x34 graduation (Phase 78) | deferred — PCB-blocked | A6 ALE-routing PCB-BLOCKED (HIGH); control register fully allocated, no free 74HC573 strobe. X88C64 stays protocol-not-implemented/host-refused. Unblock requires a shield modification. XIC-02/03/04. |
| FUT-03 (v1.14) | NMOS bench SHA-match (Phase 79 NMOS-03) | deferred — no chip | Definitive Leonardo write+verify SHA-match of the 4 graduated NMOS chips on the ~22.4V VPE rail; demoted to informational (chips stay `supported` without it); deferred for lack of an NMOS chip on hand. |
| FUT-04 (v1.14) | AT28C04/16 adapter graduation (Phase 80) | deferred — adapter not built | ADPT-01 gate NOT CLEARED: DIP24→DIP32 adapter not built, no AT28C chip on hand. 9 chips stay honestly `adapter-required`. Unblock = build adapter + DMM-verify (/WE pin 21→30) + chip on hand. ADPT-01/02/03. |
| FUT-05 (v1.15) | REWR-02 0x08 write→read→verify SHA-match proof (Phase 82) | deferred — no functional 0x08 chip | Operator-deferred 2026-06-24: the only 0x08 rewritable chip (W27E040) FAILed on a genuine stuck bit @0x7db (deterministic; erase path engaged at correct decode params). No sibling 0x08 chip for positive proof. Unblock = a functional W27E040 (or other 0x08 rewritable chip) on hand. NOT a gap. |
| CR-01 / Phase-74 Wave-2 (v1.15) | W29C040 flash4 256B page-write fault | open — reopened by Phase 84 | Phase-84 FIX-01 re-bench (N=2) confirmed the Phase-74 SDP/256B-page fix is NOT silicon-effective: deterministic page-0 boundary timeout @0x0000FF. RCA'd, not fixed in-posture (D-43). Reopen Phase-74 Wave-2 (likely dual-repo lockstep firmware fix). W29C020 (256KB) passes clean — inverts CR-01 expectation. |
| FUT-06 (v1.15) | AM27C020 0x08 32-pin write/VPP path (0-bits-programmed) | deferred — RCA'd, not trivially fixable | Phase-84 FIX-01 (N=2): deterministic 0-bits-programmed, NOT VPP-skip-related, chip silicon intact. Requires 0x08 32-pin Large EPROM write/VPP path root-cause. Named-tracked deferral per D-43, not a gap. |
| FUT-03 (v1.15, ⊃ v1.14) | 2516 0x0B read instability + write proof (GRAD-03) | deferred best-effort (D-22) | Phase-84 VPP-skip cleared the 18.8V boot-refusal but the 2516 read remains unstable (N=3, 3 distinct SHAs, 1.9% byte jitter) — instability NOT solely VPP-gated (shared OE/VPP pin). No write / no preserve-dump (D-21). GRAD-03 deferred best-effort; closes v1.14 FUT-03 NMOS write+SHA when a future bench session root-causes the read path. info/read decode confirmed correct. |
| todo (v1.15) | 2026-06-24-skip-vpp...on-reads.md | done-superseded | The VPP-skip on CMD_READ/CMD_BLANK_CHECK SHIPPED in Phase 84-01 (fw `cb947c7`); the captured todo predates the fix. Close on next triage. |
| todo (v1.16 seed) | gather-protocol-datasheets.md | deferred | Feeds the v1.16 protocol-first architecture rebuild (datasheets verify; minipro DB stays ground truth). Out of v1.15 scope. |
| verification (v1.15) | Phase 84 (84-VERIFICATION.md) | human_needed — operator-accepted | The 2 items are the D-22/D-43 disposition sign-offs, already operator-accepted (recorded in STATE stopped_at + this close). Frontmatter status line not flipped; not a gap. |
| Phase-84 input (v1.15) — RESOLVED | W29C040 flash4 page-write fault (handed off from Phase 82) | resolved → see CR-01 row above | Phase 84 ran the RCA: Phase-74 fix not silicon-effective (N=2). Disposition moved to the CR-01 / Phase-74 Wave-2 row. |
| release-gate (v1.14 → carries to v1.15) | Lockstep beta cut `3.0.0b11` + submodule gitlink bump | OPERATOR-GATED | Standing v1.11–v1.14 policy: sub-repos stay on their milestone branches, meta gitlinks PINNED; the beta cut (version bump + gitlink bump + PyPI/GitHub pre-release) + stable promotion are deferred to manual operator authorization. v1.15 sub-repo work (fw `cb947c7` / app `4d5b3de`) is NOT in the beta gitlink yet. |

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone
