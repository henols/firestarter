---
phase: 161-board-board-sweep-three-boards-on-rev-2-0
plan: 04
subsystem: bench
tags: [bench, on-device, cell-A2, uno328pb, atmega328pb, rev-2-0, w27c512, w29c020, sweep-position, expected-failure, backlog-999.2, vpp-miscalibration, board-02]

# Dependency graph
requires:
  - phase: 161-board-board-sweep-three-boards-on-rev-2-0 (plan 01)
    provides: append_evidence.py, PROCEDURE.md Amendment 3
  - phase: 161-board-board-sweep-three-boards-on-rev-2-0 (plan 02)
    provides: D-10 pre-proof (v1.33-arm judged match on ATmega328PB at span 23000)
  - phase: 161-board-board-sweep-three-boards-on-rev-2-0 (plan 03)
    provides: derived D-08 W29C020 stall ceiling (391.748 s), A1's 262144 B read baseline (73.344 s)
provides:
  - "Cell A2 (uno328pb + Rev 2.0) fully swept: four evidence positions, all `skipped-with-reason`, four genuinely distinct failure mechanisms"
  - "HEADLINE FINDING: this uno328pb's VPP ADC reads ~0.8 V high (operator multimeter 11.7 V vs firmware-reported 12.5 V) — no pot position satisfies both the firmware guard and a correct rail on this board"
  - "N=3 read-instability escalation for position 3 recorded UNRUN (blocked by the VPP finding); the v133-specific-vs-board-wide question left explicitly UNDETERMINED"
  - "BOARD-02 closed in full; A2's four figures contribute to BOARD-04 (still needs A3/B2's)"
affects: [161-05, 165-triage-and-rca]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Escalation artifacts (ESCALATION_<id>/, FINAL_READBACK_<arm>/) live at distinct cell-relative paths so no prior read-back or provenance record is ever overwritten mid-cell"
    - "A guard-fire mid-escalation (VPP HIGH) is handled exactly as P-06 itself prescribes for the historical case — never bypassed with --force, the step is recorded as blocked with a named reason rather than retried or faked"
    - "A read-only escalation (no re-write) isolates the read-path variable from the write-path variable when testing arm-vs-board attribution of an observed instability"

key-files:
  created:
    - .planning/v1.34/bench/cells/A2/ (CELL.md [621 lines], POT.md, WRITE.md [350 lines], board_probe.json, board_probe_teardown.json, check_arms_pre_cell.json, check_arms_teardown.json, 4x provenance_<id>.json, 4x WRV-VERDICT_<id>.json, READBACK-VERDICT.json, readback_control/, readback_v133/, ESCALATION_A2__control__w27c512/, FINAL_READBACK_v133/, logs/ [49 invocation groups])
  modified:
    - .planning/v1.34/bench/EVIDENCE.jsonl (+4 rows, all A2 positions)
    - .planning/v1.34/bench/EVIDENCE.md (re-rendered after each append)
    - .planning/STATE.md (SAFETY line hand-edited to the true post-teardown state incl. the VPP finding; plan pointer advanced 4->5)

key-decisions:
  - "The scheduled N=3 escalation was corrected mid-run from a write+3-read design to a READ-ONLY 3-read design, on the reasoning that the escalation tests read stability, not write success, and a re-write would replace the very residual content (position 3's failed v1.33 write) the comparison needed to hold constant."
  - "The escalation's read-only measurement was blocked by a discovery, not a tooling failure: all three attempted control-arm reads failed identically at device init with the firmware's own VPP-HIGH guard (12.5V > 12.0V target). A single confirming vpp read matched (stable 12.5V). The operator then took an independent multimeter reading: 11.7V at the same moment -- revealing this board's VPP ADC reads ~0.8V high. No pot position satisfies both the firmware guard and a correct rail on this board; the guard was never bypassed with --force, and the escalation is recorded as unrun with this named reason rather than forced through or silently dropped."
  - "This is explicitly NOT a P-H1 rig halt: P-H1 covers a broken oracle, and this milestone's judged oracle (judge_wrv.py / judge_readback.py) never consults VPP calibration and is unaffected. The uno328pb is the specimen in this cell, so its apparent ADC miscalibration is a finding about the specimen, recorded per this plan's own no-fix rule and hard prohibition on product-code changes -- RCA is Phase 165's."
  - "Every retroactive or causal claim connected to the VPP finding is stated as an inference or hypothesis, never as a measured historical fact or a proven cause: the ~11.1V real-rail estimate for this cell's four positions assumes the offset held constant across the session (only directly cross-checked once); the one-shared-cause reframing of the four distinct failure mechanisms is offered to Phase 165 as a hypothesis; the Backlog 999.2 connection is named as a lead with its evidential limits stated, not asserted as 999.2's cause; and A1's own VPP ADC accuracy is explicitly left unknown in both directions, since A1's Uno was never meter-checked."

requirements-completed: [BOARD-02]

coverage:
  - id: D1
    description: "Cell A2 holds four evidence positions (control x W27C512, control x W29C020, v1.33 x W27C512, v1.33 x W29C020), each with a full-device read-back SHA verdict or a named reason for its absence -- all four attempted on both arms, none skipped"
    requirement: "BOARD-02"
    verification:
      - kind: manual_procedural
        ref: "EVIDENCE.jsonl: 4 rows with cell_id==A2, each position_id exactly once, all outcome=skipped-with-reason (mismatch x2, disagreement x1, incomplete-read-set x1), each with a non-null write_duration_wallclock_s; judge_wrv.py runtime output for each position"
        status: pass
    human_judgment: false
  - id: D2
    description: "A2's program failure is observed on both arms and recorded with its symptom -- where in the program it stops and exactly what the host printed -- never asserted from Backlog 999.2"
    requirement: "BOARD-02"
    verification:
      - kind: manual_procedural
        ref: "WRITE.md: four positions, four genuinely distinct mechanisms (host serial timeout / firmware verify timeout at 0x7f / chip-ID 0x303 then firmware pulse-convergence at 0x179 / bare connect-level pre-handshake timeout), each with full stdout/stderr quoted and an on-chip read-back-after-failure cross-check"
        status: pass
    human_judgment: false
  - id: D3
    description: "All four positions carry captured_at_step==2 provenance and an arm confirmed by independent on-device read-back, judged under this target's vector-exclusion policy"
    requirement: "BOARD-02"
    verification:
      - kind: manual_procedural
        ref: "4x provenance_A2__*.json: captured_at_step==2; READBACK-VERDICT.json (control, preserved in readback_control/): judged_match=true, judged_span_bytes=26074; READBACK-VERDICT.json (v133, preserved in readback_v133/ and re-proven again at FINAL_READBACK_v133/): judged_match=true, judged_span_bytes=23000 -- neither leg ever compares sha_actual_judged to sha_expected_judged"
        status: pass
    human_judgment: false
  - id: D4
    description: "Each of the four positions records a measured write duration, including positions where the write never succeeded"
    requirement: "BOARD-04"
    verification:
      - kind: manual_procedural
        ref: "EVIDENCE.jsonl write_duration_wallclock_s non-null for all 4 A2 rows (15.813/4.019/10.245/14.288 s); write_duration_app_reported_s honestly 'not measured -- <reason>' for all four, since none produced a success line"
        status: pass
    human_judgment: false
  - id: D5
    description: "The N=3 read-disagreement escalation question (v133-specific vs board-wide instability) is either resolved with evidence or explicitly left undetermined with a stated reason -- never resolved by omission"
    requirement: "BOARD-02"
    verification:
      - kind: manual_procedural
        ref: "CELL.md 'Escalation recorded as UNRUN' section: three read-only attempts all failed at the VPP-HIGH guard before any bytes were read; question left explicitly UNDETERMINED, naming what would resolve it (a 3-read set on a board with a confirmed-calibrated VPP ADC)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Each position's EVIDENCE.jsonl row was appended as that position completed, paired atomically with a render_evidence.py re-render; per-cell gate green at close"
    requirement: "BOARD-02"
    verification:
      - kind: manual_procedural
        ref: "render_evidence.py --check green after each of the 4 append_evidence.py calls; gate_record.py --jsonl 0 violations; run_gates.sh 12/12 selftests + 5/5 live gates, exit 0 captured directly"
        status: pass
    human_judgment: false

# Metrics
duration: ~3h10min (executor wall-clock across the session; spans ten operator physical checkpoints and one mid-escalation discovery requiring an eleventh)
completed: 2026-08-27
status: complete
---

# Phase 161 Plan 04: Cell A2 — uno328pb, the Expected-Failure Cell, Summary

**Cell A2 fully swept on the uno328pb (ATmega328PB, Rev 2.0 shield): all four positions failed by four genuinely distinct mechanisms — but the cell's real result is that this board's on-board VPP ADC reads ~0.8 V high (operator multimeter 11.7 V vs firmware-reported 12.5 V), a finding that reframes every other observation in the cell and promotes low VPP from a long shot to the leading candidate explanation for Backlog 999.2's brownout — BOARD-02 closed.**

## HEADLINE FINDING — this board's VPP ADC reads ~0.8 V high

**The paired measurement, operator-taken (multimeter readings are operator-only, Standing bench
rule 3):** while the firmware simultaneously reported **12.5 V** (triggering its own HIGH init
guard), a multimeter on the same rail read **11.7 V**. **This board's VPP ADC reads
approximately 0.8 V high.** The rail itself did not run away — the instrument measuring it inside
the firmware is inaccurate.

**Why no pot adjustment was possible, the cleanest form of the finding:** on this specific board,
the firmware guard and a correct rail cannot be satisfied simultaneously.
- Adjust until the **firmware** reads 12.0 V → the real rail falls to **~11.2 V**, below the
  firmware's own 11.4 V LOW threshold in real terms — genuinely too low for reliable programming.
- Adjust until the **meter** reads 12.0 V → the firmware would read **~12.8 V**, and the HIGH
  guard fires harder.
- **There is no pot position that gives both.** No `--force` was used or considered.

**Ruling — not a P-H1 rig halt.** This milestone's judged oracle (`judge_wrv.py`/
`judge_readback.py`) never consults VPP calibration and is unaffected. The uno328pb is the
**specimen** here; its apparent miscalibration is a finding *about the specimen*, recorded per
this plan's no-fix rule — the board's EEPROM calibration was not touched, `firestarter config`
was not run, and the pot was not adjusted.

**Seven recorded consequences, each stated at its true evidential weight:**

1. **Retroactive inference, not measured history:** Task 4's confirming read said 11.9 V. **If**
   the ~0.8 V offset held constant, the real rail during all four positions may have been
   **~11.1 V** — below the firmware's own 11.4 V floor. Stated as an inference from one paired
   measurement with an assumed-constant offset, never as a measured fact.
2. **Reframes the four distinct failure mechanisms** as plausibly **one shared cause** (an
   under-volted programming rail failing at different points) rather than four independent
   faults — offered to Phase 165 as a **hypothesis**, not asserted as this cell's finding.
3. **Promotes the low-VPP hypothesis** already named at position 3 (the firmware's own
   diagnostic text: "insufficient program voltage or a worn or failing cell, not a timing
   problem") from a long shot to the **leading candidate explanation** — the firmware pointed
   here independently, before any multimeter was involved.
4. **Backlog 999.2 implication, a lead not a resolution:** raises the possibility 999.2's
   "uno328pb cannot finish a program" is a miscalibrated VPP ADC on *this specific board*,
   rather than a firmware or silicon defect — recorded with its evidential limits stated, **not**
   asserted as 999.2's cause.
5. **Exposes a limit in `P-06` itself:** the procedure takes exactly one confirming read per
   cell and treats it as standing for the cell's duration — sound only if that reading is
   accurate and stable. Recorded as a procedure limitation for Phase 166's honesty ledger,
   directly tied to the milestone's own declared non-claim: program-window VPP/VCC **under
   load** is unmeasured (the Phase-97 DTR-reset-on-close tooling gap). This finding gives that
   disclosed non-claim concrete teeth.
6. **Non-claim about cell A1:** A1's Uno was never meter-checked — whether *its* VPP ADC is
   accurate is genuinely unknown in both directions. A1's four positions' judged SHA verdicts are
   unaffected either way (the oracle never consults VPP).
7. **The N=3 escalation is recorded UNRUN**, not completed and not fabricated — blocked by this
   same discovery (see below).

## The N=3 escalation — UNDETERMINED, not resolved by omission

Position 3 (`A2__v133__w27c512`) returned **three distinct read SHAs** — a genuine instability.
The scheduled retroactive control-arm escalation was corrected mid-run to a **read-only** design
(three reads of the chip's existing content, no re-write, so the comparison holds the on-chip
content constant and only the arm varies) — but all three attempted reads failed identically at
device init with the VPP-HIGH guard, before a single byte was read. **The question this
escalation exists to answer — whether position 3's instability is v1.33-specific or a board-wide
property present on both arms — remains explicitly UNDETERMINED.** What would resolve it: a
three-read set taken on a board whose VPP ADC is confirmed calibrated, or a re-run of this same
measurement after this board's VPP calibration is corrected.

## Four positions, four distinct mechanisms

| # | Position | Mechanism | Wall-clock | Stop point |
|---|---|---|---|---|
| 5 | `A2__control__w27c512` | host-side serial-response timeout, no firmware reply | 15.813 s | first-block boundary (0x0200); 431/512 B of block 1 actually written (measured from an on-chip read-back) |
| 6 | `A2__control__w29c020` | **firmware-reported** verify-timeout (data-poll) | 4.019 s | byte 0x7f; partial read (113152/262144 B) independently returns the same stop value (0x13) the firmware quoted |
| 7 | `A2__v133__w27c512` | attempt 1: chip-ID mismatch at INIT (0x303, contact-fault signature); **rule-8 re-seat**; attempt 2: **firmware-reported** program-convergence failure | 4.077 s / 10.245 s | attempt 2: byte 0x000179; 3-run read set FAILED, 3 distinct SHAs |
| 8 | `A2__v133__w29c020` | bare **connect-level** failure, never reached INIT/chip-ID | 14.288 s | never reached; partial read (4096/262144 B) is 99.1% identical to a stale image from cell A1's earlier use of this same physical chip |

**No two positions failed by the identical mechanism.** Every position stopped the chip-program
path — consistent with Backlog 999.2's overall prediction — but the specific failure point and
manner varied every time, which is materially more precise than "it hangs" alone. **No completion
occurred on either arm anywhere in this cell** — 999.2 is not contradicted by an unexpected
success.

## Backlog 999.2, confirmed in conclusion, complicated in characterization

999.2 predicted a write that "hangs deterministically on the FIRST program block." **Position 1
matched that prediction closely** (host timeout, stopped 431/512 bytes into block 1). **Positions
2, 3 and 4 did not** — a firmware-diagnosed verify timeout, a firmware-diagnosed program-pulse
convergence failure (after a contact-fault re-seat), and a bare connect-level failure before the
program path was even reached. This board **cannot complete a program on either arm** — 999.2's
core conclusion holds — but "hangs deterministically on the first block" is not an accurate
description of what actually happens across all four positions. That distinction is the value
this cell adds over the backlog's own text.

## The A/B conclusion — pre-existing, not v1.33-caused

**The control arm — the pre-v1.33 merge-base — failed all four of its own two positions the same
way this board fails on v1.33.** This establishes the failures as **pre-existing on this board**,
not introduced by v1.33 — the comparison v1.31 itself could never make, for lack of a control arm.
v1.33 is not implicated as the cause of this board's brownout.

## Performance

- **Duration:** ~3h10min executor wall-clock (14:25-17:35 UTC), across ten operator physical
  checkpoints plus one mid-escalation VPP discovery requiring an eleventh
- **Completed:** 2026-08-27T17:35Z
- **Tasks:** 15 plan tasks (11 operator checkpoints including the escalation's own, plus the
  escalation's method correction), fully executed to close
- **Files modified:** 169 files across 19 task/sub-task commits (bench cell artifacts,
  `EVIDENCE.jsonl`/`.md`, `STATE.md`)

## Accomplishments

- **All four A2 positions recorded**, each `skipped-with-reason` (never `validated` — this board
  cannot complete a program on either arm), each with a genuinely distinct failure mechanism, a
  measured write duration, and (where the run got far enough) an on-chip read-back-after-failure
  cross-check independently confirming the firmware's own quoted stop value.
- **The cell's headline result — a VPP ADC miscalibration finding** — surfaced mid-escalation via
  a guard-fire that blocked the scheduled N=3 read-instability escalation, then confirmed by an
  operator multimeter reading. Recorded with all seven of its stated consequences, each at its
  true evidential weight (inference vs. hypothesis vs. lead vs. non-claim), never overstated.
- **Both arms proven and distinguishable by independent read-back:** control `judged_match=true`,
  `judged_span_bytes=26074`; v1.33 `judged_match=true`, `judged_span_bytes=23000` — the v1.33
  flash's `sha_actual_judged` reproduces plan 161-02's D-10 pre-proof exactly, and reproduces
  itself exactly again at the cell's final flash-back. Neither leg ever compares the two raw-span
  SHAs, per this target's vector-exclusion policy.
- **A rule-8 re-seat happened once, correctly bounded:** position 3's chip-ID mismatch (0x303,
  matching this project's own contact-fault signature) triggered exactly one clean re-seat and
  one re-run, with the discarded attempt fully recorded alongside the re-run, never just the
  latter. The operator's inspection did not identify a specific physical defect — recorded as
  "not assessed," never as "found sound."
- **The chip-out precondition's own limit was surfaced and recorded, not glossed over:** an
  ambiguous operator reply ("Remove W27C512") at one gate was explicitly re-confirmed rather than
  interpreted, because the chip-out precondition for any avrdude flash rests on operator word
  alone — there is no non-avrdude way to detect a seated chip.
- **The shared W27C512's physical condition was never assessed**, across eight handlings within
  this cell alone (on top of two uses in cell A1) — recorded as uncertainty for plan 161-05 to
  inherit, never as a clearance.
- **`~/.firestarter/config.json` CHANGED again — a second recurrence** of the identical class of
  finding cell A1 recorded, within the same milestone. Strengthens the case this is a systemic
  `firestarter_app` behavior rather than session noise. Not fixed here (D-16 boundary).
- **Per-cell gate (D-04) green:** `run_gates.sh` exit 0 (captured directly via `$?`), 12/12 tool
  selftests, ALL GATES PASSED (5/5 live gates). `gate_record.py --jsonl`: 0 violations.
- **All four positions force-added** under the commit-on-failure exception (none judged a clean
  match), so Phase 165's RCA has the actual bytes.
- **Both sub-repos byte-unchanged.** `firestarter/` ends on the v1.33 arm exactly as required
  (HEAD `5759dc8d`, meta's gitlink diff empty); `firestarter_app/` untouched throughout. No
  product code changed anywhere in this plan.

## Task Commits

Each task was committed atomically (19 commits spanning the full cell run and the escalation):

1. **Task 1: P-01 — shield moved to uno328pb, socket empty** - `a028c8aa` (feat)
2. **Task 2: P-02 — board-identity probe + pending provenance (4 positions)** - `8e2e27d0` (feat)
3. **Task 3: P-04 (control) — flash + judge under vector-exclusion** - `8c3d5d14` (feat)
4. **Task 4: P-05/P-06 — seat W27C512, pot confirmed in-band (firmware guard window)** - `438465d9` (feat)
5. **Task 5: P-07 position 1 (`A2__control__w27c512`) — observed MAIN-phase stall** - `237991c5` (feat)
6. **Task 6: P-08 — swap to W29C020, safety clearance given** - `33ee3a60` (docs)
7. **Task 7: P-09 position 2 (`A2__control__w29c020`) — distinct firmware failure** - `96470188` (feat)
8. **Task 8+9: P-10/P-04 (v1.33) — preserve control read-back, flash v133, judge span 23000** - `41cf7ece` (feat)
9. **Task 10+11: P-05(2nd arm)+P-07 position 3 — rule-8 re-seat, different mechanism** - `e3e5c2fc` (feat)
10. **Task 12: P-08 (2nd arm) — swap to W29C020, chip condition NOT assessed** - `2863d27f` (docs)
11. **Task 13: P-09 position 4 — fourth distinct mechanism, closes the square** - `5e9f61a0` (feat)
12. **Task 14+15 (partial): P-11 teardown — probe unchanged, config-dir CHANGED (2nd recurrence)** - `f4c0f977` (feat)
13. **Escalation method correction (docs)** - `3b5bc5bc` (docs)
14. **Escalation chip-out gate — ambiguous reply, re-confirmed explicitly** - `5fc00c10` (docs)
15. **Escalation step 2 — control arm re-flashed, judged span 26074** - `ff9e7a33` (feat)
16. **Escalation step 4 BLOCKED — VPP guard fires HIGH, unexpectedly** - `20dde305` (feat)
17. **HEADLINE FINDING — VPP ADC reads ~0.8V high; escalation UNRUN** - `f55c597f` (docs)
18. **Task 15 (final): P-11 teardown — cell A2 CLOSED, four positions gate-clean, force-added** - `56792158` (feat)

**Plan metadata:** _pending — this SUMMARY's own commit_

## Files Created/Modified

- `.planning/v1.34/bench/cells/A2/` — `CELL.md` (621 lines, full narrative including the VPP
  finding), `POT.md`, `WRITE.md` (350 lines, per-position sections + the four-mechanism table),
  `board_probe.json`/`board_probe_teardown.json`, `check_arms_pre_cell.json`/
  `check_arms_teardown.json`, 4x `provenance_A2__*.json`, 4x `WRV-VERDICT_A2__*.json`,
  `READBACK-VERDICT.json` (cell-root, ends on v133), `readback_control/` + `readback_v133/`
  (preserved six-artifact sets, both arms), `ESCALATION_A2__control__w27c512/` (the control
  re-flash proof + three failed read attempts), `FINAL_READBACK_v133/` (the final flash-back
  proof), `logs/` (49 numbered invocation groups)
- `.planning/v1.34/bench/EVIDENCE.jsonl` / `EVIDENCE.md` — +4 rows (all A2 positions, all
  `skipped-with-reason`), re-rendered after each append
- `.planning/STATE.md` — SAFETY line hand-edited to the true post-teardown state (uno328pb
  connected on `/dev/ttyUSB0`, socket empty, v1.33 arm, pot **not adjusted** with the VPP
  discrepancy carried explicitly so the next session doesn't "fix" the pot against the faulty
  ADC), plus the `~/.firestarter` second-recurrence finding and the shared-chip uncertainty; plan
  pointer advanced 4 of 5 -> 5 of 5

## Decisions Made

- **The escalation's method was corrected mid-run from write+read to read-only**, on the
  reasoning that the escalation tests read stability specifically, and a re-write would replace
  the very content (position 3's residual failed v1.33 write) the comparison needed held
  constant — recorded as a deliberate method correction, not a mistake requiring a deviation
  entry, since it happened before any measurement was taken under the wrong method.
- **The VPP-HIGH guard fire during the escalation was never bypassed** — handled per this
  project's Phase 145 D-17 permanent prohibition on `--force`, and per `P-06`'s own prescribed
  behavior for a guard fire (adjust until in band, restart clean) — except no adjustment was
  possible here (see the unsatisfiable-gate finding), so the step was recorded as blocked with a
  named reason instead of forced or faked.
- **The escalation was ruled NOT a P-H1 rig halt** — the judged oracle (SHA-based read-back and
  write/read verdicts) never consults VPP calibration, so no oracle is broken; the finding is
  about the specimen board, handled per this plan's own recording-not-fixing discipline.
- **Every causal or retroactive claim tied to the VPP finding was deliberately hedged to its true
  evidential weight** — inference (the ~11.1V retroactive estimate), hypothesis (the one-cause
  reframing), lead (the Backlog 999.2 connection), and explicit non-claim (A1's own ADC accuracy)
  — rather than allowing a single strong measurement to read as a proven conclusion.

## Deviations from Plan

### Auto-fixed Issues

None that required a code change — this plan touches only bench artifacts and hand-edited
planning docs, never `firestarter/` or `firestarter_app/` source.

### Findings Recorded, Not Fixed (Rule 4 territory — architectural/specimen/out-of-scope, surfaced rather than resolved)

**1. [Recorded, not auto-fixed — specimen finding, D-16 boundary] This uno328pb's VPP ADC reads
~0.8 V high**
- **Found during:** escalation step 4 (the scheduled N=3 read-instability escalation)
- **Issue:** the firmware-reported VPP reading (12.5 V, triggering its own HIGH guard) disagreed
  with a simultaneous operator multimeter reading (11.7 V) by ~0.8 V. No pot position satisfies
  both the firmware guard and a correct rail on this specific board.
- **Fix:** None applied — this is a specimen-board calibration finding, not a rig-tooling defect
  or product-code bug; the board's EEPROM calibration was not touched, `firestarter config` was
  not run, and the pot was not adjusted, per this plan's forbidden-actions list.
- **Files modified:** None in `firestarter/` or `firestarter_app/` (both confirmed byte-unchanged).
  Documentation only: `CELL.md`, `STATE.md`, this SUMMARY.
- **Verification:** operator multimeter reading (Standing bench rule 3, operator-only) cross-checked
  against the firmware's simultaneous `vpp` CLI reading; both readings recorded in `CELL.md`.
- **Committed in:** `20dde305` (discovery), `f55c597f` (full finding record)

**2. [Recorded, not auto-fixed — D-16 boundary, second recurrence] `~/.firestarter/config.json`
CHANGED from the Amendment 3 pinned baseline, again**
- **Found during:** Task 15 teardown, config-dir assertion 1 of 2
- **Issue:** identical class of finding to cell A1's own (`bench/cells/A1/CELL.md`) — a second
  recurrence within this same milestone. Content now `{"port": "/dev/ttyUSB0"}`; frozen
  `FIRESTARTER_CONFIG_DIR` content SHA independently confirmed unchanged (assertion 2), so no
  judged result in this cell is affected.
- **Fix:** None applied — product-code (`firestarter_app`) behavior, forbidden to touch. Handed
  to Phase 165, same as A1's identical finding.
- **Files modified:** None in `firestarter_app/`. Documentation only: `CELL.md`.
- **Committed in:** `f4c0f977`

---

**Total deviations:** 0 code fixes; 2 findings recorded and investigated but deliberately not
fixed (both specimen/product-code, out of scope, handed to Phase 165). One deliberate escalation
method correction (write+read -> read-only), made before any measurement was taken under the
original design, not counted as a deviation requiring a fix-attempt entry.
**Impact on plan:** None on this cell's own completeness — all four positions are recorded with
their genuine results regardless. The VPP finding is the cell's single most consequential result
and materially reframes how every other observation in this cell (and potentially Backlog 999.2
itself) should be read by Phase 165 — surfaced explicitly rather than left implicit in a passing
guard check nobody happened to trip.

## Issues Encountered

- **The chip-out gate for the escalation's control-arm flash rested on operator word alone, with
  no independent way to verify it.** One reply ("Remove W27C512") was ambiguous between restating
  the instruction and confirming it done; the orchestrator declined to interpret it and re-sought
  an explicit confirmation before proceeding, rather than risk an avrdude flash with silicon
  seated. This is a real, stated limitation of the chip-out rule as currently designed — there is
  no non-avrdude way to detect a seated chip, and the probe that would detect one is itself the
  operation the rule forbids.
- **The shared W27C512's physical condition was never assessed**, across eight handlings within
  this cell alone. The operator was asked directly at one gate and did not answer; at later gates
  they were told an answer wasn't required and again did not volunteer one. Recorded honestly as
  "not assessed" at every occurrence, never softened into "found sound" — plan 161-05 inherits
  this same physical part and must treat its condition as uncertain.
- **The `dev consistency-check` read command aborts after its first run's own hard failure**
  rather than continuing to attempt runs 2 and 3 (position 4's read set) — a real tool behavior,
  observed and recorded (`read_count` reflects only the runs actually attempted), not a bug in
  this plan's own tooling.

## Known Stubs

None. Every field in every artifact this plan produced is either a real measured value or an
explicit `"not measured — <reason>"` placeholder — no blank or fabricated value anywhere,
including every write-duration figure, every SHA, and the escalation's own recorded-as-unrun
status with its named reason.

## Threat Flags

None beyond the plan's own `<threat_model>` (T-161-17..22, T-161-SC), all of which this plan's
execution satisfies as designed: every failure was observed and recorded with its stop point and
host output, never asserted from Backlog 999.2 (T-161-17); every leg asserted `judged_match` plus
a runtime `hex_span_expected_by_arm` lookup, never the raw-SHA pair (T-161-18); D-08 ceilings
bounded every write attempt, none of which ever needed them (T-161-19); zero forbidden flags
reached any command, including through the VPP guard-fire crisis where `--force` was never used
or considered (T-161-20); D-07's operator safety carve-out was presented at every `P-08` gate
(T-161-21); the commit-on-failure exception correctly force-added all four non-clean positions'
bytes for Phase 165's RCA (T-161-22); zero package installs (T-161-SC).

## User Setup Required

None — no external service configuration required. The one item worth flagging for the next bench
session: this board's VPP pot is currently left at a position where the firmware reads ~12.5 V and
a multimeter reads ~11.7 V — do not "correct" it against the firmware's own reading without first
re-confirming with a meter.

## Next Phase Readiness

- **Plan 161-05 (cell A3/B2, Leonardo)** inherits: the derived D-08 W29C020 stall ceiling
  (391.748 s, from cell A1, unchanged by this cell) and A1's 262144 B control-arm read baseline
  (73.344 s). Also inherits the **shared W27C512**, whose physical condition has never been
  assessed across ten total handlings between cells A1 and A2 — treat this as genuine
  uncertainty, not a clearance. And inherits a standing caution this cell's own headline finding
  establishes: a board's on-board VPP ADC reading is not guaranteed accurate, and a fresh
  multimeter cross-check early in a cell (rather than trusting the single confirming `vpp` read
  alone) is now a demonstrated, not merely theoretical, precaution.
- **BOARD-02 is closed.** BOARD-04 remains open, still needing A3/B2's figures before it can close.
- **Phase 165's RCA queue gains its most consequential lead from this cell:** the VPP ADC
  miscalibration hypothesis for Backlog 999.2, stated with its full evidential limits and never
  overstated as a proven cause.
- Both sub-repos (`firestarter/`, `firestarter_app/`) confirmed byte-unchanged
  (`git status --porcelain` empty) throughout; `firestarter/`'s gitlink ends at the v1.33 SHA
  with zero diff to commit — identical to how it began before this plan.

---
*Phase: 161-board-board-sweep-three-boards-on-rev-2-0*
*Completed: 2026-08-27*

## Self-Check: PASSED

All claimed files verified present on disk; all claimed commit hashes (`a028c8aa`, `8e2e27d0`,
`8c3d5d14`, `438465d9`, `237991c5`, `33ee3a60`, `96470188`, `41cf7ece`, `e3e5c2fc`, `2863d27f`,
`5e9f61a0`, `f4c0f977`, `3b5bc5bc`, `5fc00c10`, `ff9e7a33`, `20dde305`, `f55c597f`, `56792158`)
verified in `git log --oneline --all`.
