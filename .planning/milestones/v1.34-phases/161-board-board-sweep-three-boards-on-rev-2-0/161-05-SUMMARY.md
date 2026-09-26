---
phase: 161-board-board-sweep-three-boards-on-rev-2-0
plan: 05
subsystem: hardware-validation
tags: [bench, on-device, leonardo, atmega32u4, rev-2-0, avrdude, vpp-calibration, v1.31-reference-rig, sweep-close]

requires:
  - phase: 161-board-board-sweep-three-boards-on-rev-2-0 (plans 03/04)
    provides: "A1's derived W29C020 ceiling (391.748s = 4x97.937s), A1's 262144B read baseline (73.344s), A2's VPP miscalibration finding (~0.8V high) and the shared W27C512's inherited condition uncertainty"
provides:
  - "Cell A3/B2 — four evidence positions on v1.31's own reference rig (Leonardo + Rev 2.0), all four clean SHA-judged matches"
  - "All twelve sweep positions of Phase 161 now exist (A1x4, A2x4, A3/B2x4), reconciled with no duplicate position_id"
  - "HEADLINE FINDING: the VPP ADC error is ratiometric (~+7.5%), consistent with a shield-wide gain/divider fault rather than board-specific EEPROM miscalibration"
  - "Forward revision of A2's leading low-VPP hypothesis (does not edit 161-04-SUMMARY.md)"
  - "The only valid v1.31 timing comparison in v1.34, stated on this rig with its method difference named"
affects: [162-chip-test-sweep, 163-shield-sweep, 165-root-cause-analysis, 166-honesty-ledger]

tech-stack:
  added: []
  patterns:
    - "Ratiometric (percentage) comparison across paired firmware/meter VPP readings, not additive offset, when isolating a gain-vs-offset ADC error"
    - "Forward supersession of a prior cell's committed hypothesis via a later SUMMARY, never by editing the earlier committed record"

key-files:
  created:
    - .planning/v1.34/bench/cells/A3-B2/CELL.md
    - .planning/v1.34/bench/cells/A3-B2/POT.md
    - .planning/v1.34/bench/cells/A3-B2/WRITE.md
    - .planning/v1.34/bench/cells/A3-B2/provenance_A3-B2__{control,v133}__{w27c512,w29c020}.json
    - .planning/v1.34/bench/cells/A3-B2/WRV-VERDICT_A3-B2__{control,v133}__{w27c512,w29c020}.json
    - .planning/v1.34/bench/cells/A3-B2/READBACK-VERDICT.json
    - .planning/v1.34/bench/cells/A3-B2/readback_control/, readback_v133/
  modified:
    - .planning/v1.34/bench/EVIDENCE.jsonl
    - .planning/v1.34/bench/EVIDENCE.md
    - .planning/STATE.md

key-decisions:
  - "12.3V firmware / 11.44V meter ruled IN BAND (guard window 11.4-12.5V, eprom.cpp:713/:736) — no exact-equality-to-target criterion invented"
  - "VPP ADC error recorded as ratiometric (~+7.5%), consistent with a shield-wide gain fault — an inference, explicitly not established from three points against one meter"
  - "A2's low-VPP hypothesis revised forward in this SUMMARY, not by editing 161-04-SUMMARY.md"
  - "No pot adjustment chasing the on-board ADC — real rail set from the multimeter, not the firmware reading"

requirements-completed: [BOARD-03, BOARD-04]

coverage:
  - id: D1
    description: "Cell A3/B2 (Leonardo + Rev 2.0, v1.31's own reference rig) — four evidence positions, both arms, both chips, each with an independent avr109 read-back proof and a full-device SHA-judged write/read verdict"
    requirement: "BOARD-03"
    verification:
      - kind: other
        ref: "bench/EVIDENCE.jsonl rows position_id=A3-B2__{control,v133}__{w27c512,w29c020}, all outcome=validated, sha_verdict_judged=match"
        status: pass
    human_judgment: false
  - id: D2
    description: "All twelve sweep positions of Phase 161 measured with a non-null write_duration_wallclock_s, closing BOARD-04"
    requirement: "BOARD-04"
    verification:
      - kind: other
        ref: "bench/EVIDENCE.jsonl — 12 sweep rows across A1/A2/A3-B2, no duplicate position_id, every row has write_duration_wallclock_s"
        status: pass
    human_judgment: false
  - id: D3
    description: "Ratiometric VPP-ADC headline finding and forward revision of cell A2's low-VPP hypothesis"
    verification: []
    human_judgment: true
    rationale: "An inference about root cause (shield-wide gain fault vs board-specific calibration) drawn from three data points against one meter — requires human/Phase-165 judgment to accept, extend, or falsify, not mechanically verifiable from this plan's own artifacts alone"

duration: ~71min (17:42:56Z first commit -> 18:53:49Z last commit; two executor sessions separated by a user interrupt at 17:45:54Z; this resumed session ran ~18:04:53Z -> 18:53:49Z, roughly 49 min)
completed: 2026-08-27
status: complete
---

# Phase 161 Plan 05: Cell A3/B2 (Leonardo + Rev 2.0) — Board Sweep Close, Ratiometric VPP-ADC Finding Summary

**Closed the board sweep's last cell on v1.31's own reference rig — all four positions clean SHA-judged matches, and a ratiometric (~+7.5%) VPP-ADC finding across two independently-calibrated boards that revises cell A2's leading low-VPP failure hypothesis forward, without editing A2's committed record.**

## HEADLINE — the VPP ADC finding, escalated beyond cell A2

Three paired firmware-vs-meter VPP readings now exist across two boards and three pot positions:

| Cell / board | Firmware VPP | Operator meter | Additive offset | Ratio (fw/meter) |
|---|---|---|---|---|
| A2 (uno328pb) | 12.5 V | 11.70 V | +0.80 V | x1.068 (+6.8%) |
| A3/B2 (Leonardo, 1st reading) | 12.9-13.0 V | 12.00 V | +0.90-1.00 V | x1.075-1.083 (+7.5-8.3%) |
| A3/B2 (Leonardo, 2nd reading, post pot-adjustment) | 12.3 V | 11.44 V | +0.86 V | x1.075 (+7.5%) |

**The ratio holds far tighter than the additive offset — approximately +7.5% (range 6.8-8.3%) across two boards and three pot positions.** Recorded as **CONSISTENT WITH** a ratiometric (gain) error — a wrong voltage-divider ratio, the kind the R1/R2 values in `rurp_configuration_t` encode — rather than a fixed additive offset. **This is an inference, not established:** three points against one meter cannot conclusively separate a gain error from an offset error; that limit is stated explicitly and is not overstated anywhere in this record.

## It refutes the board-specific reading this cell's read was expected to establish

The orchestrator's working prediction going into this cell's `P-06` was that a clean ~12.0 V match would establish A2's ~0.8 V error as that board's own EEPROM calibration — **board-specific**. It did the opposite: two boards with **independent** EEPROM calibrations show the **same proportional** error. That points at the **shared component** — the Rev 2.0 shield itself, which carries the pot and the divider the ADC measures — not at either board's own calibration. Flagged explicitly as an inference from ratio consistency, not a proven root cause, and the prediction it overturned is recorded as having been wrong, not quietly dropped.

## It revises cell A2's leading hypothesis — a forward supersession, not an edit

`161-04-SUMMARY.md` filed low real-rail VPP as the **leading hypothesis** for A2's four write failures, inferring a real rail near ~11.1-11.2 V from firmware's 12.5 V reading via that cell's own ~0.8 V offset. If the error is shield-wide (this cell's evidence), then **A1's firmware reading of 12.0 V also corresponded to a real rail near ~11.0-11.2 V — and A1 passed all four positions at that voltage.** A1 passing where A2 failed, at a comparable inferred real rail, **substantially weakens** low-VPP as A2's explanation.

**This SUMMARY records the revision forward. `161-04-SUMMARY.md` and `bench/cells/A2/CELL.md` are left exactly as committed** — this is not a retraction by edit, it is a superseding record for a later reader (Phase 165) to reconcile. Full reasoning and the ratio table live in `bench/cells/A3-B2/POT.md`.

## Real-rail disclosure and the shield's own ceiling

This cell ran at a real rail of **~11.44 V** against a 12.0 V nominal target — marginally below the W27C512's typical programming spec, and this is the **best achievable** setting on this shield: the firmware's own HIGH guard (`eprom.cpp:713`, fires above target+500 mV = 12.5 V) caps the achievable real rail at roughly **11.64 V** by the same ~7.5% ratio — no pot position on this shield can push the real rail meaningfully higher without tripping the guard. A1 ran lower still (inferred real ~11.1-11.2 V) and passed all four positions.

## Comparability caveat across the three cells

A1 ran at firmware 12.0 V (inferred real ~11.1-11.2 V); A2 ran at firmware 11.9 V (inferred real ~11.05 V); this cell ran at firmware 12.3 V / real **11.44 V** — a **higher** real rail than either of the other two. **The three cells did not run at identical real voltages; any cross-cell write-outcome comparison carries this caveat.**

## Non-claim, stated in both directions

**A1's Uno was never meter-checked.** Any offset attributed to A1 is **inferred** from the shield-wide-gain hypothesis above, not measured. This record does **not** assert A1 ran low, and does **not** assert it did not.

## Performance

- **Duration:** ~71 min total plan span (two executor sessions separated by a user interrupt at 17:45:54Z); this resumed session ran ~49 min (18:04:53Z → 18:53:49Z)
- **Started:** 2026-08-27T17:42:56Z (`bede9a5f`, prior executor)
- **Completed:** 2026-08-27T18:53:49Z (`a6bc52aa`, this executor)
- **Tasks:** 14 of 14 (2 by the prior, interrupted executor; 12 by this resumed executor)
- **Files modified:** 90 (per `git diff --stat` across the full plan span)

## All twelve sweep positions now exist

| Cell | Positions | Outcomes | Wallclock write durations |
|---|---|---|---|
| A1 (Uno, plan 03) | 4/4 | `validated` | 41.305 / 41.037 / 97.937 / 97.916 s |
| A2 (uno328pb, plan 04) | 4/4 | `skipped-with-reason` | 15.813 / 10.245 / 4.019 / 14.288 s |
| A3/B2 (Leonardo, this plan) | 4/4 | `validated` | 37.172 / 37.118 / 66.671 / 66.674 s |

`bench/EVIDENCE.jsonl` holds exactly **12 sweep rows** across `A1`/`A2`/`A3/B2` (four each, `bringup_row_exclusion` correctly excludes the pre-existing `BRINGUP-*` rows), **no `position_id` appears twice anywhere in the file**, and every row carries a non-null `write_duration_wallclock_s`. **SC#5 verified as arithmetic:** exactly one row per (arm x chip) bearing `cell_id == "A3/B2"` — `render_evidence.append_row_to_file` structurally refuses a duplicate `position_id`, so this is a property the mechanism itself enforces, not merely asserted. **Phase 163 will cite these four A3/B2 rows and must not produce a second set.** BOARD-03 and BOARD-04 are both closed.

## The A/B result on this rig — one write per position, a data point, not a spread

| Chip | Control (wall/app) | v1.33 (wall/app) | Wall-clock delta |
|---|---|---|---|
| W27C512 | 37.172 s / 33.37 s | 37.118 s / 33.37 s | **-0.054 s** |
| W29C020 | 66.671 s / 62.99 s | 66.674 s / 62.99 s | **+0.003 s** |

App-reported figures are identical to two decimals on both chips; written images are byte-identical between arms except for the address-derived mask (by design). **The control and v1.33 arms are behaviourally indistinguishable on this rig, on both chips, at this real VPP rail.** Each figure is a single write per position — a data point, never a spread, and never presented as if it carried the statistical weight of a repeated measurement.

## v1.31 comparison — the only place in v1.34 it is valid

v1.31's **0.37 s** is the **spread** (max minus min) across three full 64 KiB write cycles' app-reported figures — 106.06 / 105.69 / 106.06 s — measured on this exact **Leonardo + Rev 2.0** rig, firmware `ebe9cb3`. It is a spread, not a duration, and Phase 145 drew no comparative claim from it. **v1.34 takes one write per position per arm, so there is no v1.34 spread to set against v1.31's.** The honest comparison: the two v1.34 app-reported W27C512 figures (both **33.37 s**) and their difference (**0.00 s** to two decimals), presented beside v1.31's 0.37 s spread — **never** a single v1.34 figure "compared to 0.37 s". Both v1.34 figures land far below v1.31's ~106 s baseline because of **PR #55's per-byte VPE-settle amortisation** (105.9 s to 33.35 s, firmware `3.0.0b22`), present in **both** arms' merge bases — not a v1.33-specific improvement.

## The N=3 data point for cell A2's open, undetermined question

This cell's v1.33-arm W27C512 read set (position 11) was **perfectly stable** (`distinct_read_shas=1`) on the **same physical W27C512 chip** that returned **three distinct SHAs** under the identical v1.33 arm in cell A2's position 3, whose disambiguating control-arm escalation was **blocked** by the VPP finding and closed **UNDETERMINED**. Stated with its limits: this single stable result, on a **different board**, with **different on-chip content going in** and **different conditions** (real VPP rail, EEPROM calibration), cannot resolve A2's own instability — it is **not** offered as a resolution. It **does** point away from the chip itself as an unconditional cause and toward the uno328pb or its state at the time being the more likely locus. **Handed to Phase 165 alongside A2's own unresolved record.**

## Cross-board chunk-size effect

This rig's control-arm W29C020 write (66.671 s) is **~32% faster** than A1's control-arm W29C020 write on the Uno (97.937 s), consistent with the Leonardo's 1024-byte transfer chunks versus the Uno-class boards' 512. Named as a **board characteristic**, not a v1.33 signal — both figures compared are control-arm.

## The interrupt and how this session resumed

A prior executor instance was killed by a user interrupt mid-`P-04`, at 17:45:54Z, after the control-arm flash had already succeeded (avrdude self-reported `28170 bytes of flash written`/`verified`) but before the independent read-back proof had run. This session did **not** re-flash: it verified the flash's completeness from its own untracked logs, confirmed the `firestarter` gitlink was still at control `8695ee5` with an empty porcelain, then ran only the independent `judge_readback.py` proof (D-01: the uploader's own verify pass is never the oracle). The first touch+judge attempt hit a transient post-touch USB re-enumeration race, matching the pattern `BRINGUP-leonardo-provenance/PREPROOF.md` already documented for this exact board — discarded and recorded, not silently retried away; the immediate retry succeeded cleanly (`judged_match=true`, `judged_span_bytes=28170`).

## The Leonardo chip-out exemption

Exercised through the `P-10`/`P-04` v1.33 flash — the W29C020 stayed seated through that firmware flash rather than being pulled first, per Standing bench rule 2. **This is the only cell in the phase where that exemption applies**; A1 and A2 both pulled their chip before every flash (Uno-class chip-out rule).

## The shared W27C512's condition caveat — CLOSED

The W27C512 handled eight times across A1 and A2, its physical condition never assessed, threw a `0x303` contact fault in A2. At this cell's `P-05` (the chip's **ninth** handling), the operator inspected it and reported **"nothing looks of[f]"** — the first physical assessment of this part anywhere in the phase. Recorded precisely: an operator **visual inspection** reporting nothing anomalous, **not** a clean bill of health from a measurement, and **not** retroactive clearance for A2's own `0x303` fault, which stands as its own recorded event. The confirmation was sought in two parts — the inspection answer, then a separately-sought state confirmation — the same class of reply ambiguity cell A2's own checkpoint recorded.

## Task Commits

1. **Task 1: P-01 — mount Rev 2.0 on Leonardo, declare** — `bede9a5f` (feat, prior executor, pre-existing)
2. **Task 2: P-02 — Leonardo identity + 4 pending provenance records** — `c6baa661` (feat, prior executor, pre-existing)
3. **Task 3: P-04 (control) — resume after interrupt, prove flash by independent read-back** — `2e0d3b81` (feat)
4. **Task 4: P-05/P-06 — W27C512 seated, chip-condition caveat closed, VPP-high finding halts** — `3fb01b46` (feat) + `56a6d866` (docs, orchestrator ruling: 12.3V/11.44V in band, ratiometric finding recorded)
5. **Task 5: P-07 position 1 (`A3-B2__control__w27c512`)** — `95270401` (feat)
6. **Task 6: P-08 — swap to W29C020** — `6f9c8ea9` (docs)
7. **Task 7: P-09 position 2 (`A3-B2__control__w29c020`)** — `464bccde` (feat)
8. **Task 8: P-10 to P-04 (v1.33) — preserve control read-back, flash v1.33, prove** — `58de49bd` (feat)
9. **Task 9: P-05 (second arm) — swap back to W27C512** — `430740f0` (docs)
10. **Task 10: P-07 position 3 (`A3-B2__v133__w27c512`)** — `cd05821d` (feat, N=3 stable, BOARD-04 comparison paragraph)
11. **Task 11: P-08 (second arm) — swap to W29C020 for position 12** — `6ea981b1` (docs)
12. **Task 12: P-09 position 4 (`A3-B2__v133__w29c020`)** — `1df33992` (feat, N=3 stable, last of the twelve)
13. **Task 13: P-11 (D-11) — swap back to W27C512** — folded into `a6bc52aa` (physical confirmation recorded as part of teardown)
14. **Task 14: P-11 teardown, reconciliation, handover** — `a6bc52aa` (feat)

**Plan metadata:** this commit (`docs: complete 161-05 plan`) — created after this SUMMARY.

## Files Created/Modified

- `.planning/v1.34/bench/cells/A3-B2/CELL.md` — full cell narrative, P-01 through P-11
- `.planning/v1.34/bench/cells/A3-B2/POT.md` — the VPP ratio finding and orchestrator ruling
- `.planning/v1.34/bench/cells/A3-B2/WRITE.md` — four position write/read/judge records + BOARD-04 comparison paragraph + four-position A/B summary
- `.planning/v1.34/bench/cells/A3-B2/provenance_A3-B2__*.json` (4), `WRV-VERDICT_A3-B2__*.json` (4)
- `.planning/v1.34/bench/cells/A3-B2/READBACK-VERDICT.json`, `readback_control/`, `readback_v133/`
- `.planning/v1.34/bench/cells/A3-B2/board_probe.json`, `board_probe_teardown.json`, `check_arms_pre_cell.json`, `check_arms_teardown.json`
- `.planning/v1.34/bench/EVIDENCE.jsonl` — +4 rows (positions 9-12); `EVIDENCE.md` re-rendered
- `.planning/STATE.md` — SAFETY line rewritten to carry the ratiometric VPP finding and D-11 leave-state forward

## Decisions Made

- **12.3 V firmware / 11.44 V meter ruled IN BAND**, per the firmware's own guard window (`eprom.cpp:713`/`:736`, [11.4, 12.5] V for a 12000 mV target) — not by demanding an exact match to the 12.0 V target, consistent with the ruling that overturned an earlier executor's stricter, invented criterion elsewhere in this phase.
- **The VPP ADC error recorded as ratiometric (~+7.5%)**, consistent with a shield-wide gain fault, explicitly flagged as an inference with its limits (three points against one meter cannot separate gain from offset conclusively).
- **A2's low-VPP hypothesis revised forward** in this SUMMARY and in `CELL.md`, not by editing `161-04-SUMMARY.md` or `bench/cells/A2/CELL.md` — those stay exactly as committed.
- **No pot adjustment was made to chase the on-board ADC.** The real rail was set and confirmed from the operator's multimeter, never from the firmware's own `vpp` reading — the STATE.md SAFETY line carries an explicit warning against a future session "correcting" the pot toward the faulty reading.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Transient post-touch USB re-enumeration race during P-04's read-back proof**
- **Found during:** Task 3 (P-04 control read-back)
- **Issue:** First `judge_readback.py` attempt failed with `OS error: cannot open port /dev/ttyACM0: Input/output error` — a genuine hardware-timing race, the identical class already documented in `BRINGUP-leonardo-provenance/PREPROOF.md` for this board.
- **Fix:** Discarded the failed attempt (recorded, not erased), re-ran the identical touch-then-judge pair immediately; the retry succeeded cleanly.
- **Files modified:** `.planning/v1.34/bench/cells/A3-B2/logs/08_touch_for_read_control.*`, `09_judge_readback_control.*`, `CELL.md`
- **Verification:** `judged_match=true`, `judged_span_bytes=28170` on the retry.
- **Committed in:** `2e0d3b81`

**2. [Rule 3 - Blocking, tooling-harness artifact] Outer Bash timeout killed the N=3 W29C020 read set mid-run-3**
- **Found during:** Task 12 (P-09 position 4, `A3-B2__v133__w29c020`)
- **Issue:** The calling shell's own outer timeout (not the tool's own `--signal=INT 200` ceiling, which was never approached) killed the `dev consistency-check` process mid-third-run, leaving a partial `run_03.bin` (163840/262144 B).
- **Fix:** Discarded the partial file, re-ran the identical three-run command under a longer outer timeout; the clean re-run produced three agreeing, complete reads.
- **Files modified:** `.planning/v1.34/bench/cells/A3-B2/reads/A3-B2__v133__w29c020/`, `logs/21_consistency_check_v133_w29c020.*`, `WRITE.md`
- **Verification:** `judge_wrv.py`: `sha_verdict_judged=match`, `read_count=3`, `distinct_read_shas=1`.
- **Committed in:** `1df33992`

---

**Total deviations:** 2 auto-fixed (1 Rule 1 hardware-timing race, 1 Rule 3 tooling-harness artifact)
**Impact on plan:** Both were transient, discarded-and-retried per the same discipline the plan already applies to touch/probe races and chip re-seats. No scope creep; no data from a discarded attempt was retained as if it were the judged record.

## Issues Encountered

- **A genuinely off-target VPP reading (12.9-13.0 V, above the firmware's own HIGH guard threshold) appeared at the first `P-06` confirming read.** Per the plan's own decision branch for this case, the write was **not** attempted and the finding was escalated for a ruling rather than self-resolved. The operator subsequently adjusted the pot and reported "12.3v from board is 11.44 in reality"; the orchestrator ruled this in-band per the firmware's own guard window, and the cell proceeded. This produced the ratiometric VPP finding that is this plan's headline result — an issue that turned into the cell's most significant output.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Phase 162 inherits the rig standing exactly as it needs it**: Leonardo connected at `/dev/ttyACM0`, Rev 2.0 shield mounted, v1.33 arm flashed (fw `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`), **W27C512 (DIP28) seated** — the only cell in the phase ending with a chip in — pot untouched at firmware 12.3 V / real 11.44 V, in band. **No reconfiguration and no re-flash needed** for Phase 162's 11-part `dev test` sweep.
- **Phase 163 must cite, never re-run, this cell's four A3/B2 rows** in `bench/EVIDENCE.jsonl` (SC#5/SHIELD-03).
- **Phase 165 inherits three carried findings to reconcile:** the ratiometric VPP-ADC hypothesis and its forward revision of A2's low-VPP explanation; the N=3 stability data point relevant to (but not resolving) A2's own undetermined instability question; and a **third** recurrence of the `~/.firestarter/config.json` mtime-change leak (content byte-identical to baseline both times, only mtime advances — A1, A2, now this cell).
- **Phase 166's honesty ledger should note:** the on-board VPP instrument used for every reading across this entire milestone reads ~7.5% high; program-window VPP/VCC under load remains unmeasured (the pre-existing DTR-reset-on-close tooling gap).
- Both `firestarter` and `firestarter_app` sub-repos remain byte-unchanged in content across this plan; the `firestarter` gitlink sits at v1.33 `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463` with an empty porcelain.
- No blockers for Phase 162.

---
*Phase: 161-board-board-sweep-three-boards-on-rev-2-0*
*Completed: 2026-08-27*

## Self-Check: PASSED

All referenced files exist on disk; all 14 referenced commit hashes are present in `git log --all`. No missing items.
