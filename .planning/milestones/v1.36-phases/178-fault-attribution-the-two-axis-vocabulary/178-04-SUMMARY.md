---
phase: 178-fault-attribution-the-two-axis-vocabulary
plan: 04
subsystem: dev-test-diagnostics
tags: [diagnostic_report, submit, status-axis, honesty-disclosure, requirements-close, phase-seal]

# Dependency graph
requires:
  - phase: 178-fault-attribution-the-two-axis-vocabulary
    provides: "plan 178-01's STATUS_COMPLETE/ERROR/SKIP vocabulary and run_status field, plan 178-02's ATTR-04 Leg B and ATTR-05 non-suppression proofs, and plan 178-03's 18-shape frozen corpus with the status-axis-bearing shape registered -- this plan adds the ATTR-06 disclosure on top of that surface and closes the phase"
provides:
  - "rail_reading_disclosure: a module-level _RAIL_READING_DISCLOSURE sentence, rendered as a console row (\"rail reading\") and exported as a to_dict() top-level key, computed once and read off the exported dict at the render site"
  - "ATTR-06's own parenthetical repaired to name both bits the CMD_READ_VPP branch sets (CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE), confirmed read-only against firestarter/src/hardware_operations.cpp:27"
  - "the stale chip_test.py:2461 citation repaired (four sites across REQUIREMENTS.md and FEATURES.md) to the re-derived, currently-measured chip_test.py:2567-2574"
  - "the measured ATTR-04 record in MILESTONES.md (18-shape corpus, 17 inherited hashes unmoved, RK-174-09 after_hash still None) plus T3-void / T4-out-of-scope / FP_TRANSPORT-out-of-scope records"
  - "ATTR-01 through ATTR-06 flipped Complete in REQUIREMENTS.md; RIG-01 untouched, still Deferred"
  - "COVERAGE.md and the full-suite, all-gates, both-repos phase seal (evidence/178-04-phase-seal.txt)"
affects: []

# Actuals (#2632) -- pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 10465
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The write_coverage/sdp_hold_state single-sourcing discipline extended to a third field: a module constant computed once, exported by to_dict(), read by render() off the exported dict -- never recomputed at the render site."
    - "A plan's own baked-in file:LINE citation is re-derived against the live tree at execution time rather than trusted, even when the plan author measured it correctly at authoring time -- earlier-landing plans in the same phase can move it before this plan runs."

key-files:
  created:
    - .planning/phases/178-fault-attribution-the-two-axis-vocabulary/COVERAGE.md
    - .planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-04-attr06.txt
    - .planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-04-attr06-doc.txt
    - .planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-04-phase-seal.txt
  modified:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_submit.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/fixtures/reports/*.json (all 18 regenerated)
    - .planning/REQUIREMENTS.md
    - .planning/research/FEATURES.md
    - .planning/MILESTONES.md

key-decisions:
  - "The transport-fault handler's true current location is chip_test.py:2567-2574, not the plan's own baked-in chip_test.py:2524-2541 -- that citation was correct when 178-04-PLAN.md was authored but drifted stale once plans 178-01/02/03 landed lines ahead of it in the same phase. Re-derived from source (grep + sed) rather than trusted, per the explicit orchestrator instruction to treat every citation in this plan as suspect. All four repaired sites (REQUIREMENTS.md's Fault Attribution intro, and FEATURES.md lines 58/230/306) now cite :2567-2574. This is documented as a deviation below rather than silently substituted, since it makes the plan's own literal `<automated>` verify string (grep for '2524-2541') unsatisfiable as written."
  - "rail_reading_disclosure took the TOP-LEVEL to_dict() route (like sdp_hold_state), not the voltage sub-dict route -- per the plan's own reasoning, this keeps Phase 181's vpp_mv/vpe_mv deletion pin (_VOLTAGE_KEYS) on a separate axis from this phase's addition (_TO_DICT_KEYS)."
  - "D-13's 'same commit' instruction is read as: Task 2 lands immediately after Task 1 in this same plan, with a commit message cross-referencing Task 1's hash, since firestarter_app and the meta repo are separate git repositories and a literal single commit spanning both is impossible."
  - "Followed the plan's D-09/D-11/D-15/D-16 exactly for the MILESTONES.md prose: no new ledger row, no ledger cell changed (8 rows before and after), quoting the numbers from 178-03-attr04-seal.txt rather than restating them from memory."

patterns-established: []

requirements-completed: [ATTR-01, ATTR-02, ATTR-03, ATTR-04, ATTR-05, ATTR-06]

coverage:
  - id: D1
    description: "The ATTR-06 disclosure sentence reaches both the rendered console output (a \"rail reading\" row immediately after the two vpp/vpe rows) and the exported to_dict() dict (top-level rail_reading_disclosure key), unconditionally -- including when no rail was measured"
    requirement: "ATTR-06"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_rail_reading_disclosure_is_exported_and_rendered"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_rail_reading_disclosure_renders_when_no_rail_was_measured"
        status: pass
      - kind: unit
        ref: "tests/test_submit.py#test_sanitize_leaves_the_rail_reading_disclosure_byte_identical"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-04-attr06.txt (measured_rendered=True, unmeasured_rendered=True, sanitized_identical=True, render_reads_dict=True, render_reads_constant=False, top_key_count=13, to_dict_pin_len=13, disclosure_pinned=True, stale_frozen=, corpus_size=18, snapshot_count=18)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The wording clears all 14 forbidden over-claim patterns (never asserts socket continuity), and adding the key moved zero frozen dedup_fingerprint hashes across the 18-shape corpus"
    requirement: "ATTR-06"
    verification:
      - kind: unit
        ref: "firestarter_app/tools/check_diagnostic_report_claims.py (PASS: 216 string literals checked, zero forbidden matches)"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-04-attr06.txt (stale_frozen=, corpus_size=18)"
        status: pass
    human_judgment: false
  - id: D3
    description: "ATTR-06's own parenthetical is repaired to name both bits the CMD_READ_VPP branch sets, with the substantive no-socket-routing-bit conclusion measured intact, and the stale chip_test.py:2461 citation is repaired everywhere it appears in .planning/ -- no firmware file touched"
    requirement: "ATTR-06"
    verification:
      - kind: other
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-04-attr06-doc.txt (attr06_names_regulator=1, attr06_names_drop=1, attr06_keeps_conclusion=1, attr06_keeps_noclaim=1, stale_req=0, stale_feat=0, fresh_req=1, fresh_feat=3, rig01_deferred=1, fw_clean=yes, app_clean=yes)"
        status: pass
    human_judgment: false
  - id: D4
    description: "ATTR-01 through ATTR-06 are Complete against Phase 178 with ATTR-04's holding recorded as a measurement (18-shape corpus, 17 hashes unmoved, RK-174-09 after_hash still None), T3/T4/FP_TRANSPORT recorded void/out-of-scope, and RIG-01 stays Deferred"
    requirement: "ATTR-01"
    verification:
      - kind: other
        ref: "REQUIREMENTS.md traceability table (6 rows Complete) + MILESTONES.md prose"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-04-phase-seal.txt (reqs_complete=6, rig01_still_deferred=1, milestones_attr04_record=2, milestones_t3_void=1, milestones_t4_oos=1, milestones_fp_transport=1)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every gate in both repositories is green on the sealed phase, with zero source-comment lines added across all seven commits this phase made"
    requirement: "ATTR-04"
    verification:
      - kind: integration
        ref: "firestarter_app full suite (pytest tests/) -- 2241 passed"
        status: pass
      - kind: e2e
        ref: ".planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-04-phase-seal.txt (ruff check/format clean, mypy 35/35, snapshot --check 18/18, check_devtest_orchestrator.py PASS, check_diagnostic_report_claims.py PASS, check_rekey_ledger.py OK 8/8, full_suite_passed=2241, phase_added_comments=0, firmware_diff=clean, chip_database_diff=clean, app_tree=clean)"
        status: pass
    human_judgment: false

duration: 44min
completed: 2026-09-06
status: complete
---

# Phase 178 Plan 04: Fault Attribution -- the Two-Axis Vocabulary Summary

**The report now says, in a rendered console row and an exported `rail_reading_disclosure` JSON key, that a rail reading measures the regulator only and never shows whether the socket is connected -- ATTR-06's own parenthetical is repaired to name both bits `CMD_READ_VPP` actually sets, all four stale `chip_test.py:2461` citations are repaired to the re-derived `:2567-2574`, and ATTR-01 through ATTR-06 close the phase with a measured (not asserted) ATTR-04 record.**

## Performance

- **Duration:** ~44 min
- **Completed:** 2026-09-06T12:59:11Z
- **Tasks:** 3
- **Files modified:** 29 (4 production/test files + 18 regenerated snapshots in `firestarter_app`; 3 doc files + 4 new evidence/coverage files in the meta repo)

## Accomplishments

- **Task 1 (the disclosure itself):** Added `_RAIL_READING_DISCLOSURE` beside `NOT_MEASURED`/`NOT_REPORTED` in `diagnostic_report.py`, exported it as a top-level `to_dict()` key (`rail_reading_disclosure`), and rendered it as one row ("rail reading") immediately after the two vpp/vpe rows -- read off the exported dict, never recomputed at the render site. Widened `_TO_DICT_KEYS` 12 -> 13 in sorted position, regenerated all 18 frozen report-shape snapshots (zero `dedup_fingerprint` hashes moved), and added two new tests proving both the measured and unmeasured-rail edges reach both surfaces, plus a sanitizer byte-identity test.
- **Task 2 (the evidence repair):** Repaired ATTR-06's parenthetical in `REQUIREMENTS.md` to name both bits the `CMD_READ_VPP` branch sets (confirmed read-only against `firestarter/src/hardware_operations.cpp:27`), keeping the substantive no-socket-routing-bit conclusion intact. Repaired all four sites citing the stale `chip_test.py:2461` (`REQUIREMENTS.md`'s intro plus three sites in `FEATURES.md`) to the re-derived, currently-true `chip_test.py:2567-2574` -- **not** the plan's own baked-in `:2524-2541`, which had itself drifted stale by the time this plan ran (see Deviations).
- **Task 3 (the seal):** Recorded the measured ATTR-04 holding in `MILESTONES.md` (prose only, ledger table untouched at 8 rows) plus T3-void / T4-out-of-scope / `FP_TRANSPORT`-out-of-scope. Flipped ATTR-01 through ATTR-06 to Complete in `REQUIREMENTS.md` (checkbox + traceability table), left RIG-01 Deferred. Wrote `COVERAGE.md`. Ran every gate in both repositories -- full suite (2241 passed), ruff, mypy watermark (35/35), both AST/claims gates, the snapshot checker, the cross-tree rekey-ledger checker (8/8 bound), and a whole-phase comment census (zero `#` lines added across all seven commits) -- and recorded the full seal to `evidence/178-04-phase-seal.txt`.

## Task Commits

1. **Task 1: The sentence the report has never said** - `43e7a8a` (feat, firestarter_app)
2. **Task 2: Repair ATTR-06's own evidence, and the stale handler citation** - `867e98af` (docs, meta-repo)
3. **Task 3: Seal the phase** - `24ec1232` (docs, meta-repo)

**Plan metadata:** committed separately in the meta-repo (`.planning/`), together with this SUMMARY and the WINDOWS.md ledger entry below.

## Files Created/Modified

- `firestarter_app/firestarter/diagnostic_report.py` - `_RAIL_READING_DISCLOSURE` constant, `to_dict()` export, `render()` row
- `firestarter_app/tests/test_diagnostic_report.py` - two ATTR-06 tests (measured + unmeasured-rail edge)
- `firestarter_app/tests/test_submit.py` - sanitizer byte-identity test for the new key
- `firestarter_app/tests/test_blast_radius_invariance.py` - `_TO_DICT_KEYS` widened 12 -> 13 in sorted position
- `firestarter_app/tests/fixtures/reports/*.json` - all 18 committed snapshots regenerated
- `.planning/REQUIREMENTS.md` - ATTR-06 parenthetical repaired, stale citation repaired, ATTR-01..06 marked Complete
- `.planning/research/FEATURES.md` - three stale citation sites repaired
- `.planning/MILESTONES.md` - ATTR-04 measured-and-held record, T3/T4/FP_TRANSPORT records (prose only, ledger table unchanged)
- `.planning/phases/178-fault-attribution-the-two-axis-vocabulary/COVERAGE.md` - reasoned no-external-API declaration (new)
- `.planning/phases/178-fault-attribution-the-two-axis-vocabulary/evidence/178-04-attr06.txt`, `178-04-attr06-doc.txt`, `178-04-phase-seal.txt` - measured evidence (new)

## Decisions Made

- Followed the plan's D-13/D-14 exactly for the disclosure's mechanics (single-computation, top-level export, render-site read-off) and D-09/D-11/D-15/D-16 exactly for the MILESTONES.md prose.
- Re-derived the transport-fault handler's true current line citation (`chip_test.py:2567-2574`) from source rather than trusting the plan's own baked-in `:2524-2541`, which had drifted stale by the time this plan ran (see Deviations).
- Took the top-level `to_dict()` route for `rail_reading_disclosure` (the `sdp_hold_state` analog), keeping Phase 181's `_VOLTAGE_KEYS` deletion pin on a separate axis from this phase's addition.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, self-caught] Removed an added `#`-comment section header before committing**
- **Found during:** Task 1 (post-implementation comment-count check, before committing)
- **Issue:** The new ATTR-06 test section in `test_diagnostic_report.py` initially added a `#`-comment section-header block (mirroring the file's own pre-existing convention), which would have shown up as six added `^\+\s*#` diff lines -- violating the project's standing no-comments rule and the plan's own zero-added-comment acceptance criterion.
- **Fix:** Converted the section header to a bare triple-quoted string-literal expression, the compliant carrier already shipped elsewhere in this file and in `test_blast_radius_invariance.py`.
- **Files modified:** `firestarter_app/tests/test_diagnostic_report.py`
- **Verification:** re-ran `git diff -- firestarter/ tests/ | grep -cE '^\+[[:space:]]*#'` -- 0, before the Task 1 commit
- **Committed in:** `43e7a8a` (corrected before the commit was made)

**2. [Rule 1 - Bug] The plan's own baked-in `chip_test.py:2524-2541` citation was itself stale; repaired to the re-derived `chip_test.py:2567-2574` instead**
- **Found during:** Task 2 (read_first verification against the live `chip_test.py` source, before editing)
- **Issue:** `178-04-PLAN.md`'s Task 2 instructs repairing the stale `chip_test.py:2461` citation to `chip_test.py:2524-2541`, and its own `<automated>` verify script literally greps for that string. Measuring the actual current source (`grep -n "except (SerialError, HardwareOperationError)" firestarter/chip_test.py`) showed the transport-fault handler now sits at lines 2567-2574; `:2524-2541` is a stale range inside `_run_step_untimed`'s docstring and `_resolve_or_none` call, not the handler at all. This drift happened because plans 178-01/178-02/178-03 landed lines ahead of the citation between plan authoring and this plan's execution -- the orchestrator's own prompt explicitly warned that every citation in this plan, including its own, should be treated as suspect and re-derived.
- **Fix:** Repaired all four sites (REQUIREMENTS.md's Fault Attribution intro, and FEATURES.md lines 58/230/306) to `chip_test.py:2567-2574`, confirmed against the live source, rather than to the plan's stale `:2524-2541`. Ran an adapted verification checking for the correct string instead of running the plan's `<automated>` block unmodified (which would have failed on `fresh_req=0`/`fresh_feat=0` had I used the correct value, or silently embedded a second wrong citation had I used the plan's stale one).
- **Files modified:** `.planning/REQUIREMENTS.md`, `.planning/research/FEATURES.md`
- **Verification:** `evidence/178-04-attr06-doc.txt` -- `fresh_req=1`, `fresh_feat=3` (both referring to `:2567-2574`), `stale_req=0`, `stale_feat=0`; cross-checked the handler's true position and the absence of the three socket-routing bits directly against `firestarter/src/hardware_operations.cpp:27` (read-only)
- **Committed in:** `867e98af` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 self-caught comment-rule violation, 1 bug -- a stale citation baked into the plan's own verify script). Both logged to `.planning/WINDOWS.md` as ledger entries (deviation kind) for visibility at ship time.
**Impact on plan:** Deviation 1 is a self-correction against the plan's own explicit gate, no scope creep. Deviation 2 changes which line number the repair points to (the correct current one, not the plan's stale one) -- the substance of the repair (fix the citation, don't leave it stale) is exactly what the plan asked for; only the literal target string differs from what the plan's automated check expected.

## Issues Encountered

None -- all three tasks' `<verify>` blocks passed (Task 2's ran against an adapted string per the deviation above), and the plan-level `<verification>` (full suite, snapshot check, both AST/claims gates, rekey ledger, ruff, mypy watermark, zero-comment census, firmware/database porcelain) all passed as recorded in `evidence/178-04-phase-seal.txt`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 178 (Fault Attribution -- the Two-Axis Vocabulary) is complete: ATTR-01 through ATTR-06 are all Complete against Phase 178, with ATTR-04's holding recorded as a measurement rather than an assertion.
- RIG-01 remains Deferred, unopened, for the reason ATTR-06 states -- no rig-sanity leg was built on the rail-only instrument.
- The frozen 18-shape corpus, the status-axis vocabulary, and the ATTR-06 disclosure are all in place for Phase 179 (UV Slot Writes) and Phase 181 (Report Fidelity, which will delete `vpp_mv`/`vpe_mv` from `_VOLTAGE_KEYS` -- a separate pin from this phase's `_TO_DICT_KEYS` addition) to build on without further changes to this surface.
- No blockers.

---
*Phase: 178-fault-attribution-the-two-axis-vocabulary*
*Completed: 2026-09-06*

## Self-Check: PASSED
- FOUND: firestarter_app/firestarter/diagnostic_report.py
- FOUND: firestarter_app/tests/test_diagnostic_report.py, test_submit.py, test_blast_radius_invariance.py
- FOUND: .planning/REQUIREMENTS.md, .planning/research/FEATURES.md, .planning/MILESTONES.md
- FOUND: .planning/phases/178-fault-attribution-the-two-axis-vocabulary/COVERAGE.md
- FOUND: evidence/178-04-attr06.txt, 178-04-attr06-doc.txt, 178-04-phase-seal.txt
- FOUND: commit 43e7a8a (Task 1, firestarter_app)
- FOUND: commit 867e98af (Task 2, meta-repo)
- FOUND: commit 24ec1232 (Task 3, meta-repo)
