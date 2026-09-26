---
phase: 151-protection-readability-lock-status
plan: 10
subsystem: build-gates
tags: [platformio, avr, flash-budget, size-baseline, pytest]

# Dependency graph
requires:
  - phase: 151-08
    provides: "The dev lock-status firmware read end-to-end (CMD_LOCK_STATUS dispatch, flash_util_read_in_id_mode, both *_read_protection_execute operations, eprom_lock_status + loop() arm), the firmware growth this plan measures and funds"
provides:
  - "151-SIZE-TRANSCRIPTS.md: cold rm -rf + single pio run/test capture for all three AVR targets and all three native envs, deltas against both BASE-01 and the pre-151 live baseline on both axes, ten-item byte inventory, leonardo Caterina margin"
  - "MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES = 288 in check_size_baseline.py -- the third named, SHA-attributed flash exemption, flash-only, no new RAM exemption"
  - "size_baseline.json re-recorded to the cold post-151 figures (uno 25418/1575, uno328pb 25468/1581, leonardo 27500/2016; native/native_nodevtools 163 cases/17 suites)"
  - "A new *_v151* fixture family (13 files) and eight repointed/extended legs in test_check_size_baseline.py, all 14 legs green"
affects: [151-13]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A third MERGE-05 exemption stacks additively beside the first two, never folded into either, with the same eight-part comment shape (attribution, byte inventory + SHA attribution, three rejected alternatives, named-not-laundered sentence, armed-tripwire arithmetic, SCOPE line, Evidence Ceiling sentence, the constant)."
    - "A stale fixture family is severed onto a new *_vNNN* family rather than edited in place; retired families are kept, never deleted, per this directory's own convention."

key-files:
  created:
    - .planning/phases/151-protection-readability-lock-status/151-SIZE-TRANSCRIPTS.md
    - firestarter/tests/fixtures/captured_build_v151_uno.log
    - firestarter/tests/fixtures/captured_build_v151_uno328pb.log
    - firestarter/tests/fixtures/captured_build_v151_leonardo.log
    - firestarter/tests/fixtures/merge05_base01_anchor_v151_uno.log
    - firestarter/tests/fixtures/merge05_base01_anchor_v151_uno328pb.log
    - firestarter/tests/fixtures/merge05_base01_anchor_v151_leonardo.log
    - firestarter/tests/fixtures/merge05_lock_status_v151_uno.log
    - firestarter/tests/fixtures/merge05_lock_status_v151_uno328pb.log
    - firestarter/tests/fixtures/merge05_lock_status_v151_leonardo.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth_v151.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band_v151.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved_v151.log
    - firestarter/tests/fixtures/planted_size_baseline_flash_regression_v151.log
  modified:
    - firestarter/scripts/check_size_baseline.py
    - firestarter/scripts/baseline/size_baseline.json
    - firestarter/tests/test_check_size_baseline.py
    - firestarter/tests/fixtures/README.md
    - firestarter/tests/fixtures/captured_test_native_summary.log
    - firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log

key-decisions:
  - "No second RAM exemption authored: Phase 151's own RAM growth measured at exactly 0 B on all three AVR targets (cold, rm -rf + pio run). The pre-existing +2 B RAM delta against BASE-01 is Phase 149's, unmoved, and remains fully covered by MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2. Authoring an unneeded RAM exemption would be exactly the laundering these clauses exist to prevent."
  - "Leonardo's Caterina-safe growth budget (28672 - flash_used) is a DIFFERENT, UNGUARDED axis from the MERGE-05 flash band -- no checker in this repository enforces it. Measured margin 1172 B; no overshoot; no compensating guard added (declined twice, T-a7w-01 and CONTEXT.md's Deferred Ideas)."
  - "Cold measurement matched the orchestrator-supplied warm table exactly on all three targets/axes -- no discrepancy to report."
  - "test_policy_merge05_fires_on_ram_move was repointed onto the new *_v151* family purely for family-consistency (no leg left reading a retired family), with its asserted values unchanged since no RAM exemption moved."

requirements-completed: []

coverage:
  - id: D1
    description: "Cold triple-target + triple-native-env measurement transcript, funding the exemption from measured figures rather than guessed ones"
    verification:
      - kind: other
        ref: "python3 scripts/check_build_warnings.py --rebuild (PASS); cold pio run -e {uno,uno328pb,leonardo} and pio test -e {native,native_nodevtools} re-run this session, matching 151-SIZE-TRANSCRIPTS.md exactly"
        status: pass
    human_judgment: false
  - id: D2
    description: "Third named, SHA-attributed flash exemption (288 B) funding dev lock-status, stacked additively; no second RAM exemption; every printing site shows the new term; default mode gains no <=64"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py (14/14 passed, including test_base01_is_not_re_anchored_by_the_new_exemption's four-way source-scan)"
        status: pass
    human_judgment: false
  - id: D3
    description: "BASE-01 provably frozen; eight legs severed onto a new *_v151* fixture family; no fullflash fixture edited or deleted"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py::test_base01_is_not_re_anchored_by_the_new_exemption; git diff --stat scripts/baseline/size_baseline_base01.json (empty); git diff --name-status tests/fixtures/ (zero D entries)"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-08-20
status: complete
---

# Phase 151 Plan 10: Firmware Size-Baseline Re-measure & Third MERGE-05 Exemption Summary

**Cold-measured Phase 151's own firmware growth at a uniform +288 B flash / +0 B RAM on all three AVR targets, funded it with a third named, SHA-attributed MERGE-05 flash exemption (no new RAM exemption), re-recorded the live baseline, and severed eight legs onto a new `*_v151*` fixture family.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-20 (continuation of an interrupted prior session — Task 1 was already committed)
- **Completed:** 2026-08-20
- **Tasks:** 3 completed (Task 1 was already committed at session start; Tasks 2-3 completed this session)
- **Files modified:** 20 (2 modified in Task 2; 6 modified + 13 created in Task 3)

## Accomplishments

- **Task 1 (already committed at `8d6399c1` before this session began):** `151-SIZE-TRANSCRIPTS.md` records the cold `rm -rf .pio/build/<env>` + single `pio run -e <env>` capture for uno/uno328pb/leonardo and the cold `pio test -e <env>` capture for native/native_nodevtools/native_pinmap_provisional, deltas against both BASE-01 and the pre-151 live baseline on both axes, the seven accounting firmware commit SHAs, a ten-item byte inventory (one item measured at zero — no new `byte_flip_t` table was needed), the three native-env test summaries, and the Caterina check (`28672 - 27500 = 1172 B, UNGUARDED, no overshoot`).
- This session re-ran the full cold measurement independently (three AVR `rm -rf` + `pio run`, two native `rm -rf` + `pio test`) as a cross-check: **every figure matched the committed transcript exactly** (uno 25418/1575, uno328pb 25468/1581, leonardo 27500/2016; native/native_nodevtools 163/163 cases, 17 suites) — no discrepancy against the orchestrator's own warm-measurement table, so no report was needed per the STOP-and-report clause.
- Added `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES = 288` to `check_size_baseline.py`, in the established ~55-line eight-part comment shape, SHA-attributed to Plan 151-08's firmware commits (`32c32e7`, `f66d817`, `8db7e55`, `0444b1c`, `3ff9f34`). Widened `_merge05_flash_allowance()` to a 6-tuple and every printing site (the FAIL decomposition, the PASS-line compact form, the module docstring's exemption enumeration) without folding the new term into either existing exemption or the unnamed leonardo `band = 0` inline literal at `:506`.
- **No second RAM exemption.** Phase 151's own RAM growth measured at exactly 0 B on all three targets; the pre-existing +2 B against BASE-01 is Phase 149's, unchanged, already fully covered.
- Re-recorded `scripts/baseline/size_baseline.json`'s `avr_targets` (`flash_used`/`ram_used`/`flash_free`/`ram_free`) and `native_envs` (native/native_nodevtools cases 151→163) to the cold post-151 figures, and rewrote `meta.deltas_vs_base01`'s three `merge05_clause` prose fields in the established accepted-trade style, all SHA-attributed. `size_baseline_base01.json` untouched — confirmed via `git diff --stat` (empty) both before and after.
- Verified all four firing legs by direct observation, not just by reading the plan: for each of leonardo-growth, uno-over-band, ram-move and the default-mode flash-regression plant, ran a temporary "one byte inside the allowance" variant (confirmed PASS/exit 0) immediately before running the committed `allowance + 1` fixture (confirmed FAIL/exit non-zero with the correct decomposition text).
- Created 13 new `*_v151*` fixtures (3 `captured_build_v151_*`, 3 `merge05_base01_anchor_v151_*`, 3 `merge05_lock_status_v151_*` — the new exemption's own admission proof at exactly the new ceiling, zero headroom on leonardo — and 4 `allowance+1` plants) and repointed/extended eight legs in `test_check_size_baseline.py`: `test_clean_avr_all_three_envs_pass`, `test_default_mode_is_unchanged_by_the_new_flag`, `test_planted_flash_regression_flips_checker_to_failure`, `test_baseline_seam_precedence_flips_clean_log_to_fail`, `test_policy_merge05_fires_on_{uno_class_over_band,leonardo_growth,ram_move}`, and a new Arm 3 on `test_policy_merge05_admits_the_documented_defect_fix`. Extended `test_base01_is_not_re_anchored_by_the_new_exemption`'s source-scan with a fourth pin (`MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES = 288`). Updated `captured_test_native{,_nodevtools}_summary.log` in place (151→163 cases), following the Phase 149 precedent for the one leg that reads them.
- No `_fullflash` fixture edited or deleted; `tests/fixtures/README.md` gained a `_v151` severance section mirroring the a7w section's shape.
- 14/14 legs green in `test_check_size_baseline.py`; full `firestarter/tests/` suite on the committed tree: **315 passed** (unchanged count — no test file gained or lost a test).

## Task Commits

Each task was committed atomically in `firestarter/`:

1. **Task 1: Cold triple-target re-measure and transcript** — committed in the meta repo at `8d6399c1` (docs, prior session; this plan's own `commits_land_in` treats the transcript as a meta-only artifact)
2. **Task 2: The third flash exemption and every site that prints it** — `03ed1a3` (feat)
3. **Task 3: Sever the eight reddened legs onto a new `*_v151*` fixture family** — `373d6da` (test)

**Plan metadata:** recorded in this SUMMARY commit (meta repo).

## Files Created/Modified

- `.planning/phases/151-protection-readability-lock-status/151-SIZE-TRANSCRIPTS.md` — the cold measurement transcript (Task 1, prior session)
- `firestarter/scripts/check_size_baseline.py` — third named flash exemption, widened allowance resolver and every printing site
- `firestarter/scripts/baseline/size_baseline.json` — re-recorded live baseline (avr_targets, native_envs, deltas_vs_base01 prose)
- `firestarter/tests/test_check_size_baseline.py` — eight legs repointed/extended, source-scan strengthened, module docstring severance record
- `firestarter/tests/fixtures/README.md` — `_v151` severance section
- `firestarter/tests/fixtures/captured_test_native_summary.log`, `captured_test_native_nodevtools_summary.log` — updated in place, 151→163 cases
- 13 new `firestarter/tests/fixtures/*_v151*.log` fixtures (see key-files above)

## Decisions Made

- No second RAM exemption authored — see key-decisions above.
- Leonardo's Caterina-safe growth budget (1172 B, unguarded) is kept structurally distinct from the MERGE-05 flash band (594 B, guarded) in every artifact this plan touches; neither figure is quoted in place of the other.
- `test_policy_merge05_fires_on_ram_move` repointed onto the new family for consistency only, values unchanged (no RAM exemption moved this phase).
- Cold re-measurement this session matched the committed Task 1 transcript exactly on every figure — recorded as a cross-check, not a re-derivation.

## Deviations from Plan

None beyond the continuation itself — plan executed exactly as written. This session was a continuation of an interrupted prior session: Task 1 (the transcript) and part of Task 2's code edits were already present and uncommitted/committed at session start. This session verified Task 1's transcript by independent cold re-measurement (exact match), completed and committed Task 2 (the exemption's printing-site wiring plus the baseline re-record, which had not yet been done), and executed Task 3 in full.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 151-13 (which owns the LOCK-02/03/04 requirement flips) can now cite this plan's funded exemption and re-recorded baseline as closed groundwork.
- `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json` exits 0 on all three AVR targets, printing the full four-term decomposition, with leonardo at exactly zero headroom (594 B delta against a 594 B allowance) — any further AVR flash growth in this milestone needs its own new named exemption or a reduction elsewhere.
- Leonardo's Caterina-safe margin is 1172 B remaining, unguarded by any checker in this repository — future AVR-side work on this milestone should keep computing `28672 - flash_used` inline until a compensating guard is authored (not planned; declined twice).

## Self-Check: PASSED

All created/modified files confirmed present on disk; all three commits (meta `8d6399c1` Task 1, firestarter `03ed1a3` Task 2, firestarter `373d6da` Task 3) confirmed present in their respective repos' `git log --oneline --all`.
