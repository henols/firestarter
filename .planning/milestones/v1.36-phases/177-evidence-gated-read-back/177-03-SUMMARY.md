---
phase: 177-evidence-gated-read-back
plan: 03
subsystem: testing
tags: [chip_test, dev-test, read-back-inventory, seed-amendment, phase-seal]

requires:
  - phase: 177-02
    provides: "The declared re-key (RK-174-01/05/06/07/09), the re-baselined FROZEN_HASHES, and the full app suite green at 2210 passed -- the baseline this plan seals the phase against."
provides:
  - "PRUNE-04 closed as measured-empty within the dev test engine: an ast census over chip_test.py proving exactly two operator.read_eprom call sites, both named-and-excluded, with the census SEEN to redden against a planted third site"
  - "The eight-row read-back call-site inventory (177-READBACK-INVENTORY.md), naming write_cycle_eprom as the one genuine match in the package outside the engine"
  - "PRUNE-07 closed: the seed's R1 sentence replaced in place with an affirmative exclusion, R2 corrected for its cross-cycle predicate and synthesized-match reporting, status frontmatter recording the fired trigger"
  - "COVERAGE.md's reasoned no-external-API declaration"
  - "Phase 177 sealed: every gate in the battery measured green, no firmware or database drift across the whole phase, five requirements marked Complete"
affects: []

actuals:
  tokens: 7287
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "AST-based census over line-number containment: an FunctionDef's span (lineno..end_lineno) picks the innermost enclosing function for a matched Call node, instead of a stack-based visitor -- correct regardless of ast.walk's traversal order."
    - "In-place seed amendment with a dated headed block (the 380210ed precedent, PY32F071 seed): replace the destructive sentence where it stands, do not merely annotate past it, and record what changed and why in a trailing dated paragraph rather than editing history."
    - "Measured, not asserted: every gate in the phase-seal battery is a command whose output is captured and grepped for an exact literal, not a claim in prose."

key-files:
  created:
    - firestarter_app/tests/test_readback_inventory.py
    - .planning/phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md
    - .planning/phases/177-evidence-gated-read-back/COVERAGE.md
    - .planning/phases/177-evidence-gated-read-back/evidence/177-03-readback-census.txt
    - .planning/phases/177-evidence-gated-read-back/evidence/177-03-seed-amendment.txt
    - .planning/phases/177-evidence-gated-read-back/evidence/177-03-phase-seal.txt
  modified:
    - .planning/seeds/dev-test-adaptive-sequencing.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "D-177-1 (Option A, from 177-01/DECISIONS.md) implemented here: PRUNE-04 closes as measured-empty within the engine. chip_test.py has exactly two operator.read_eprom sites (_dispatch_read, _read_region), both name-and-excluded; eprom_operations.write_cycle_eprom is the one genuine match in the package, outside the engine, named and excluded as the uno328pb read-repeatability oracle."
  - "PA-20 (commit-range base for the D-11 topology leg): resolved the phase base as the parent of 177-01's behaviour commit (df2978e, the last 176-04 commit) rather than a literal HEAD~6, since the plan's own literal resolution would have reached one commit further back into phase 176 -- both bases agree on the same result (0 comment-opening additions, 5 commits, no fixtures/chip_test.py collision), so no correction was needed, only the wider base recorded."

requirements-completed: [PRUNE-04, PRUNE-07]

coverage:
  - id: D1
    description: "The dev test engine's whole population of operator.read_eprom call sites is enumerated by an ast census (not asserted in prose), and the census is SEEN to redden against a planted third call site"
    requirement: PRUNE-04
    verification:
      - kind: unit
        ref: "tests/test_readback_inventory.py#test_engine_has_exactly_two_read_eprom_call_sites"
        status: pass
      - kind: unit
        ref: "tests/test_readback_inventory.py#test_a_planted_third_call_site_reddens_the_census"
        status: pass
      - kind: unit
        ref: "tests/test_readback_inventory.py#test_an_empty_enclosing_allow_list_fails_rather_than_passing_vacuously"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both engine read sites (fingerprint read-back, SDP leg) are named-and-excluded with their reasons pinned by the code's own docstrings and verify_eprom's signature"
    requirement: PRUNE-04
    verification:
      - kind: unit
        ref: "tests/test_readback_inventory.py#test_verify_eprom_signature_names_the_replacement_primitive"
        status: pass
      - kind: unit
        ref: "tests/test_readback_inventory.py#test_read_region_docstring_still_pins_the_one_slice_site"
        status: pass
      - kind: unit
        ref: "tests/test_readback_inventory.py#test_dispatch_sdp_leg_docstring_still_pins_the_verdict"
        status: pass
    human_judgment: false
  - id: D3
    description: "write_cycle_eprom is named, located and excluded in the committed eight-row inventory, so PRUNE-04 closes as measured rather than unexamined"
    requirement: PRUNE-04
    verification:
      - kind: other
        ref: ".planning/phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md (row 6, and the closure statement)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The seed's R1 sentence is replaced in place (not merely deleted) with an affirmative exclusion naming both protected read-backs and why; R2's predicate is corrected; status frontmatter records the fired trigger; schema stays four fields"
    requirement: PRUNE-07
    verification:
      - kind: other
        ref: "evidence/177-03-seed-amendment.txt (destructive_sentence_present=0, affirmative_exclusion=1, r2_cross_cycle=2, dated_block=1, frontmatter_fields=4, status_still_dormant=0)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every gate in the phase-seal battery passes: ruff check/format, mypy watermark 35/35, snapshot drift check, blast-radius/rekey/issue-corpus suites, orchestrator checker, cross-tree ledger checker, full suite at 2216 passed, no firmware/database drift"
    verification:
      - kind: other
        ref: "evidence/177-03-phase-seal.txt (8 rc=0 lines, mypy errors: 35 (watermark: 35), full_suite_passed=2216)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Exactly PRUNE-01, PRUNE-02, PRUNE-03, PRUNE-04, PRUNE-07 marked Complete in REQUIREMENTS.md; no other requirement touched"
    verification:
      - kind: other
        ref: ".planning/REQUIREMENTS.md traceability table (reqs_complete=5, prune08_untouched=1 in evidence/177-03-phase-seal.txt)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-05
status: complete
---

# Phase 177 Plan 03: Close PRUNE-04 and PRUNE-07, Seal the Phase Summary

**Measured the engine's whole device-read-back population at exactly two named-and-excluded call sites (closing PRUNE-04 empty), replaced the seed's self-contradicting R1 sentence in place with an affirmative exclusion (closing PRUNE-07), and sealed Phase 177 with every gate in the battery green -- full suite at 2216 passed, no firmware or database drift across the whole phase.**

## Performance

- **Duration:** 55 min
- **Completed:** 2026-09-05
- **Tasks:** 3 (all completed this session)
- **Files modified:** 8 (1 in `firestarter_app`, 7 in the meta repo)

## Accomplishments

- **Task 1 -- PRUNE-04 closed by census.** Wrote `firestarter_app/tests/test_readback_inventory.py`: an `ast` walk over `firestarter/chip_test.py` proves exactly two `operator.read_eprom(...)` call sites, enclosed by `_dispatch_read` and `_read_region` and no others. Two anti-vacuity legs prove the gate is a gate: one plants a third call site into an in-memory copy of the source and asserts the census reports three (SEEN to redden), one asserts an emptied expected enclosing-function set fails rather than passing vacuously. Three more legs pin the disposition reasons where a reader will find them: `EpromOperator.verify_eprom`'s five-parameter signature, `_read_region`'s "ONE place this slice lives" docstring, and `_dispatch_sdp_leg`'s "verdict" docstring. The committed `177-READBACK-INVENTORY.md` reproduces the full eight-row call-site table (search method stated), names `eprom_operations.write_cycle_eprom` as the one genuine read-to-compare-a-held-buffer site in the package -- outside the engine, the uno328pb read-repeatability oracle -- and states PRUNE-04's closure as measured-empty within the engine.
- **Task 2 -- PRUNE-07: the seed corrected.** Replaced R1's final paragraph in `.planning/seeds/dev-test-adaptive-sequencing.md` in place: the sentence that told a planner "this applies to the fingerprint read-backs" (an instruction to convert it to a verify) is gone, replaced by an affirmative exclusion naming both the fingerprint read-back and the SDP leg as read-backs that "must stay real reads," with the reason for each, closing with the project's own seam ("verify decides; a read-back diagnoses"). R2 gained the missing cross-cycle predicate correction and the synthesized-match sentence ("the read-back is what costs; the classification is free"), and its `ff_ratio` false-PASS paragraph now names Phase 175's structural sentinel as what makes the dependency asserted rather than assumed. The frontmatter `status` field now states what fired (R1/R2 by Phase 177) and what remains (R3 for Phase 180, R4 deferred) inside the unchanged four-field schema. R3, R4, the projected-effect table, the per-class characteristics section and the out-of-scope section are byte-for-byte untouched.
- **Task 3 -- the phase sealed by measurement.** Wrote `COVERAGE.md`'s reasoned no-external-API declaration. Ran the full gate battery from `/workspaces`: `ruff check`/`ruff format --check` clean on `firestarter/ tests/`, `tools/check_mypy_watermark.py` at exactly `mypy errors: 35 (watermark: 35)`, `tools/snapshot_report_shapes.py --check` (17 snapshots match), `test_blast_radius_invariance.py`/`test_rekey_ledger.py`/`test_devtest_issue_corpus.py` (153 passed), `tools/check_devtest_orchestrator.py` (`PASS: scanned...`), `tools/rekey/check_rekey_ledger.py` from `/workspaces` (`OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound`), and the whole `firestarter_app` suite at **2216 passed, 0 failed** (329.91s) -- `test_skip_census.py` was not among the failures, so PA-18's re-run-at-base-commit fallback was not needed. Confirmed `git -C firestarter status --porcelain` and `git -C firestarter_app status --porcelain firestarter/data/chip_database.json` both empty across the whole phase. Confirmed the D-11 commit topology by inspection: 5 commits in the `firestarter_app` phase range, none touching both `tests/fixtures/` and `firestarter/chip_test.py`. Hand-flipped PRUNE-01, PRUNE-02, PRUNE-03, PRUNE-04, PRUNE-07 to Complete in `.planning/REQUIREMENTS.md`'s traceability table and their v1 checkboxes; `PRUNE-08 | Phase 180 | Pending` and every other row is untouched.

## Task Commits

1. **Task 1: PRUNE-04 closed by census** - `0a29d8b` (test, `firestarter_app`) and `b5d4d1c6` (docs, meta)
2. **Task 2: PRUNE-07 -- replace the sentence that told a planner to delete the diagnostic** - `dbf487d4` (docs, meta)
3. **Task 3: Seal the phase by measurement** - `be6ff0d9` (docs, meta)

## Files Created/Modified

- `firestarter_app/tests/test_readback_inventory.py` - the ast census, the two anti-vacuity legs, the three disposition-pinning legs
- `.planning/phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md` - the eight-row call-site inventory and PRUNE-04's closure statement
- `.planning/seeds/dev-test-adaptive-sequencing.md` - R1's paragraph replaced in place, R2 corrected, `status` frontmatter updated, dated block appended
- `.planning/phases/177-evidence-gated-read-back/COVERAGE.md` - the no-external-API declaration
- `.planning/REQUIREMENTS.md` - PRUNE-01/02/03/04/07 flipped to Complete
- `.planning/phases/177-evidence-gated-read-back/evidence/177-03-{readback-census,seed-amendment,phase-seal}.txt` - this session's verification transcripts

## Decisions Made

See `key-decisions` in the frontmatter. One in-session note beyond what is recorded there: the seed's R1 replacement wraps "must stay real reads" across a single unbroken markdown line rather than the initial draft's line-wrap split across two lines, after the seal-time grep for that exact substring caught the split -- fixed before any commit landed, so it is not a deviation, just the verify loop working as designed.

## Deviations from Plan

None - plan executed exactly as written. The one correction (the "must stay real reads" line-wrap, above) was caught and fixed inside Task 2's own verification loop before that task's commit, per the plan's acceptance-criteria gate, not after.

## Issues Encountered

None. The full-suite run (Task 3) took ~330s, within the plan's stated baseline; it was run once as a background job to avoid the harness's 120s foreground timeout, per the plan's own note that the measured full-suite baseline exceeds that window.

**Consumer impact, noted per the plan's instruction, not fixed here:** `.claude/skills/devtest-triage/SKILL.md` reads `dedup_fingerprint` as a dedup key only, at five sites, and reads neither the classification string nor `ladder_state` -- no skill edit is forced by this phase's re-key, but the re-key does orphan the historical dedup groups the skill relies on, and an all-OK run is now ladder-promotable where it previously was not.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 177 is sealed. All five requirements it owns (PRUNE-01, PRUNE-02, PRUNE-03, PRUNE-04, PRUNE-07) are Complete in `.planning/REQUIREMENTS.md`. The full `firestarter_app` suite is green at 2216 passed, 0 failed (329.91s); `ruff check`, `ruff format --check`, the mypy watermark (35/35), the snapshot drift check, the orchestrator checker and the cross-tree re-key checker all pass. No file in the `firestarter/` firmware submodule and no line of `chip_database.json` changed across the whole phase. Ready for the orchestrator's code review, regression gate and phase verifier; Phase 178 (ATTR-01..06, the status/result two-axis model) is next in the roadmap and can build on the re-anchored `RK-174-09` baseline this phase's predecessor plan declared.

---
*Phase: 177-evidence-gated-read-back*
*Completed: 2026-09-05*

## Self-Check: PASSED

- All 8 claimed files confirmed present via `[ -f ]`: `firestarter_app/tests/test_readback_inventory.py`, `.planning/phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md`, `.planning/phases/177-evidence-gated-read-back/COVERAGE.md`, `.planning/seeds/dev-test-adaptive-sequencing.md`, `.planning/REQUIREMENTS.md`, and the three evidence files.
- All 4 commit hashes confirmed present via `git log --oneline --all`: `0a29d8b` (firestarter_app), `b5d4d1c6`, `dbf487d4`, `be6ff0d9` (meta).
- Re-ran plan-level `<verification>` at close: census reports `engine_read_sites=2`, `enclosing=_dispatch_read,_read_region`; `tests/test_readback_inventory.py` collects 6 node ids and all pass; the inventory names `write_cycle_eprom`, the SDP leg and `_dispatch_read` with dispositions; the seed's swept-in sentence counts 0, all four required phrases count non-zero, exactly one dated block, frontmatter still 4 keys, `status` no longer `dormant`; the gate battery shows 8 `rc=0` lines, watermark `35 (watermark: 35)`, full suite `2216 passed`; `.planning/REQUIREMENTS.md` shows `reqs_complete=5`, `prune08_untouched=1`.
- `git -C /workspaces/firestarter status --porcelain` and `git -C /workspaces/firestarter_app status --porcelain` both empty; meta repo clean except the expected `firestarter_app` gitlink bump, left uncommitted per instructions.
