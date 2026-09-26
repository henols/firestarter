---
phase: 152-outward-facing-close-operator-gated
plan: 02
subsystem: testing
tags: [claim-gate, regex, honesty-ledger, python, fixtures, pytest]

requires:
  - phase: 152-outward-facing-close-operator-gated
    provides: "152-check-claims.py and 152-CLAIM-CLASSES.md, built in Plan 152-01"
provides:
  - "test_check_claims_152.py: the paired suite proving the gate rather than a copy of its tables"
  - "Eight new fixtures (five donor-carried forbidden-class plants, three missing-caveat plants), completing the fifteen-fixture set"
  - "152-CLAIM-GATE-TRANSCRIPTS.md: the committed plant-and-revert evidence, every RED pasted verbatim"
affects: [152-13, 152-20, "every later 152 plan that extends _DEFAULT_TARGETS or reruns this transcript"]

tech-stack:
  added: []
  patterns:
    - "Self-maintaining arming leg (asserts structural properties of _DEFAULT_TARGETS plus a no-argv no-seam subprocess exit) instead of a pre-authored pin against one named file, so the leg stays true as later plans extend the target list"
    - "Parametrised pytest legs for a family of sibling fixtures (three issue-closed controls, three missing-caveat rows) so each sibling is its own counted test node rather than one loop hidden inside a single test"

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_proven_unqualified.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_graduation.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_support_status_change.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_at28c256_fixed.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_page_size_proven.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_missing_caveat_software_proven.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_missing_caveat_no_at28c.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_missing_caveat_unverified.md
    - .planning/phases/152-outward-facing-close-operator-gated/test_check_claims_152.py
    - .planning/phases/152-outward-facing-close-operator-gated/152-CLAIM-GATE-TRANSCRIPTS.md

key-decisions:
  - "Legs 2-4 of the paired suite (planted overclaim / missing caveat / bare claim word) point at this phase's own committed fixtures rather than re-deriving single-purpose donor-shaped analogs, since a like-for-like fixture did not exist in this phase's set for every donor leg"
  - "The arming leg (test_armed_against_the_real_152_artifacts) is written self-maintaining -- structural assertions plus a live subprocess exit check -- rather than a pin against one named artifact, per the plan's explicit instruction, so it survives later plans extending the target list without editing"
  - "The two family-of-siblings legs (issue-closed still-fires, required-caveat independence) are pytest-parametrised so each of the three fixtures per family is a separately counted, separately reportable test node"

requirements-completed: [OUT-05]

duration: 25min
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 02: Claim Gate Fixture Suite and Transcript Summary

**Completed the fifteen-fixture set, built the thirty-leg paired suite `test_check_claims_152.py`, and committed the plant-and-revert transcript with every RED pasted verbatim -- proving Plan 152-01's gate fails on a planted violation before any pass is believed.**

## Performance

- **Duration:** 25 min
- **Tasks:** 3 completed
- **Files modified:** 10 created

## Accomplishments

- Authored the eight donor-class fixtures this plan owed: five plants for the donor-carried
  forbidden-phrase rows (a bare bench-compound claim word, a protocol-graduation claim, a
  support-status-field claim, a hardware-completion claim, and a page-dimension validation claim),
  each carrying all three required caveats so it fails for exactly one reason; and three
  missing-caveat plants, each omitting exactly one of the three required-caveat sentences while
  carrying zero forbidden phrases. Every fixture was probed through the env seam before commit and
  fails for exactly its own labelled reason.
- Built `test_check_claims_152.py`: copied the phase 149 donor's paired suite, applied the seven
  mandatory rename sites (own basename, scanner path, env seam, by-path import module name, three
  caveat needles in place of the donor's one, a self-maintaining arming leg, and a three-label meta
  map), transcribed all twenty donor legs, and extended the non-target leg to also exclude
  `152-VALIDATION.md` and `152-PATTERNS.md`. Added six new legs proving the two added labels, the
  modified label's narrowing, the mandated withdrawal word order, D-05's required gh#32 statement,
  and the independence of the three required-caveat rows. One leg (the narrowing-forward test) came
  out red on first run because its throwaway document fell to the fail-closed full caveat set under
  an unrecognised basename; fixed by adding the two other required sentences to the fixture text, a
  locator-only change, not a weakening of the assertion.
- Wrote `152-CLAIM-GATE-TRANSCRIPTS.md`: eleven RED blocks (thirteen `EXIT=1` lines across the two
  added labels, the three still-fires controls for the modified label, the five donor-carried rows,
  and the three required-caveat rows) and three ALLOW/GREEN blocks (`EXIT=0`), every one a literal
  paste of the command, the gate's stdout and the `EXIT=` line -- none paraphrased, none
  reconstructed. Stubbed the two later-plan sections, each naming its owning plan.
- Ran `python3 -m pytest test_check_claims_152.py -q -o addopts=""` -> 30 passed, with the count
  line visible; ran `python3 152-check-claims.py` (defaults, no argv, no seam) -> `PASS:`, exit 0,
  both before and after the transcript was added.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the eight donor-class fixtures** - `69182742` (test)
2. **Task 2: Build test_check_claims_152.py, 30 legs green** - `302cf866` (test)
3. **Task 3: Write 152-CLAIM-GATE-TRANSCRIPTS.md** - `bf56b2da` (docs)

_No TDD tasks in this plan; no plan-metadata commit yet (see final commit below)._

## Files Created/Modified

- `fixtures/planted_proven_unqualified.md` - donor-carried label plant, all three caveats present
- `fixtures/planted_graduation.md` - donor-carried label plant, all three caveats present
- `fixtures/planted_support_status_change.md` - donor-carried label plant, all three caveats present
- `fixtures/planted_at28c256_fixed.md` - donor-carried label plant, all three caveats present
- `fixtures/planted_page_size_proven.md` - donor-carried label plant, all three caveats present
- `fixtures/planted_missing_caveat_software_proven.md` - omits caveat 1 of 3, zero forbidden phrases
- `fixtures/planted_missing_caveat_no_at28c.md` - omits caveat 2 of 3, zero forbidden phrases
- `fixtures/planted_missing_caveat_unverified.md` - omits caveat 3 of 3, zero forbidden phrases
- `test_check_claims_152.py` - the paired suite, 30 legs, subprocess-driven behavioural legs throughout
- `152-CLAIM-GATE-TRANSCRIPTS.md` - the committed plant-and-revert evidence register, not a gate target

## Decisions Made

- Legs 2-4 of the paired suite point at this phase's own committed fixtures rather than re-deriving
  donor-shaped single-purpose analogs no such fixture existed for.
- The arming leg is self-maintaining (structural checks plus a live subprocess exit check) rather
  than a pin against one named artifact, per the plan's explicit instruction.
- The two family-of-siblings legs are pytest-parametrised so pytest counts and reports each sibling
  fixture as its own test node.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Narrowing-forward leg's throwaway document fell to the full caveat set**
- **Found during:** Task 2, first full run of the new suite.
- **Issue:** `test_the_required_phrase_alone_does_not_trip_the_narrowed_proven_pattern` wrote a
  `tmp_path` document carrying only the mandated `software-proven-unvalidated` compound. Its
  basename is not in `_CAVEAT_RULES`, so `_required_caveats_for()` fails closed to the full
  three-label caveat set, and the document was missing the other two required sentences -- the gate
  correctly reported two missing-caveat violations, which the leg's assertion (checking only for
  exit code 0 and the absence of the bare-claim-word label -- `FORBIDDEN_PATTERNS` table row 10)
  did not anticipate.
- **Fix:** Added the two other required sentences to the fixture text so the document satisfies the
  full caveat set while still containing the mandated compound as its only occurrence of the claim
  word. Locator-only: the assertion itself (exit 0, no bare-claim-word label) was not changed.
- **Files modified:** `test_check_claims_152.py`
- **Commit:** `302cf866`

### None Other

All other work executed exactly as planned; no auth gates encountered (this plan is offline,
stdlib-only Python plus pytest, with no network or package-manager calls).

## Known Stubs

The transcript's "Extended target list (Plan 152-13)" and "Final target list (close-out, Plan
152-20)" sections are intentional placeholders, each naming the plan that fills it in -- not stubs
this plan failed to complete, but the documented handoff shape the plan itself specifies.

## Threat Flags

None. T-152-05 through T-152-08 are all satisfied by mechanisms built in this plan (leg-isolation
assertions with non-vacuity guards, every new leg observed to pass with one locator-only fix, the
non-target leg for the transcript file, and the distinct suite basename), and T-152-SC records that
no package install occurred.

This ships software-proven and unvalidated on silicon.

## Self-Check: PASSED

All 10 created files found on disk; all 3 task commits (`69182742`, `302cf866`, `bf56b2da`) found in
`git log --oneline --all`.
