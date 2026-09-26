---
phase: quick-260913-e7t
plan: 01
subsystem: docs
tags: [claim-hygiene, prose-correction, ci, mypy, pre-commit]

requires:
  - phase: 188-the-tools-directory
    provides: retirement of the host `tools/check_*.py` gate family and the mypy CI leg, which left the five stale claims this task closes
provides:
  - Four stale-enforcement-claim corrections in firestarter_app (WR-02, WR-03, WR-04, WR-06a)
  - One stale-comment correction in firestarter (WR-05)
  - A durable record of the mypy claim's survival in host-tools-retirement.md (WR-06b)
  - An explicit, reasoned disposition for WR-01 (deletion via the provenance sweep, not fixed here)
affects: [claim-hygiene-milestone, provenance-strip-sweep]

actuals:
  tokens: 8100
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_sdp_db_invariant.py
    - firestarter_app/tests/test_numeric_schema_source_scan.py
    - firestarter_app/tests/test_build_db_inclusion.py
    - firestarter_app/CLAUDE.md
    - firestarter/.github/workflows/beta-build.yml
    - .planning/notes/host-tools-retirement.md
    - .planning/todos/pending/2026-09-13-close-six-stale-claims-wr01-wr06.md
    - .planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md

key-decisions:
  - "WR-06a required a rewrite, not a deletion: .pre-commit-config.yaml still wires mypy as a local hook (ruff-check -> ruff-format -> mypy), so deleting the word from CLAUDE.md would have manufactured a second false claim (that pre-commit no longer runs mypy). The line now states CI enforces ruff+pytest only, and mypy is a local pre-commit-only hook."
  - "The retirement note's mypy paragraph lives in section 1 ('What was retired'), not section 2, as measured directly in the file -- both the source todo and the plan brief cited section 2, which was corrected here by locating the paragraph by its bold lead string rather than trusting the section number."
  - "WR-01 is NOT fixed in this task. It is a source comment at firestarter_app/tools/parse_devtest_issue.py:215; the operator's hard rule forbids any comment in product source, including a corrected one, so its only compliant disposition is deletion, folded into the existing provenance-strip sweep rather than a reword here."
  - "The source todo (2026-09-13-close-six-stale-claims-wr01-wr06.md) stays under todos/pending/, not completed/, because its own 'Done when' block requires all six WRs closed and WR-01 remains open -- filing a five-of-six todo as completed would itself be a claim-hygiene violation."

requirements-completed: [WR-02, WR-03, WR-04, WR-05, WR-06]

coverage:
  - id: D1
    description: "WR-02 fixed: test_sdp_db_invariant.py no longer attributes the widening direction to a deleted tools/check_sdp_capability_invariants.py script"
    requirement: WR-02
    verification:
      - kind: unit
        ref: "grep gate: 0 occurrences of 'already gates elsewhere' in test_sdp_db_invariant.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "WR-03 fixed: test_numeric_schema_source_scan.py's two plural cross-references now agree with the module docstring (singular 'test 1')"
    requirement: WR-03
    verification:
      - kind: unit
        ref: "grep gate: 0 occurrences of 'tests 1 and 2' in test_numeric_schema_source_scan.py; both corrected strings present"
        status: pass
    human_judgment: false
  - id: D3
    description: "WR-04 fixed: test_build_db_inclusion.py's module docstring no longer claims the deleted SC#3 dispatch-safety enforcement"
    requirement: WR-04
    verification:
      - kind: unit
        ref: "grep gate: 0 occurrences of 'SC#3' in test_build_db_inclusion.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "WR-06a fixed: firestarter_app/CLAUDE.md's Tooling gate line now describes mypy as a local pre-commit-only hook, not a CI gate"
    requirement: WR-06
    verification:
      - kind: unit
        ref: "grep gate: 0 occurrences of 'mypy...all enforced by' plus presence of 'is **not** a CI gate' in CLAUDE.md"
        status: pass
    human_judgment: false
  - id: D5
    description: "WR-05 fixed: beta-build.yml's no-DEV_TOOLS comment no longer references the deleted vector-gate steps; YAML still parses and the step is intact"
    requirement: WR-05
    verification:
      - kind: unit
        ref: "yaml.safe_load parse + step-name assertion; grep gate for dead back-reference absence"
        status: pass
    human_judgment: false
  - id: D6
    description: "WR-06b recorded in host-tools-retirement.md Section 1, plus WR-01's disposition recorded in both todos"
    requirement: WR-06
    verification:
      - kind: unit
        ref: "grep gates confirming '260913-e7t', 'pre-commit', 'parse_devtest_issue.py' and 'WR-01' present in the three .planning/ files"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-09-13
status: complete
---

# Quick Task 260913-e7t: Close Stale Enforcement Claims WR-02..WR-06 Summary

**Corrected five stale post-retirement claims across three repositories as pure prose edits — zero behavior change, zero comments added to product source, and WR-01 explicitly deferred to the provenance-strip sweep with its reasoning recorded.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-09-13T10:15Z (approx)
- **Completed:** 2026-09-13T10:50Z (approx)
- **Tasks:** 3 (one per repository)
- **Files modified:** 8 (4 in firestarter_app, 1 in firestarter, 3 in the meta repo)

## Accomplishments

- Corrected four stale enforcement claims in `firestarter_app` in one commit: WR-02 (dead `tools/check_*.py` attribution), WR-03 (self-contradicting plural cross-references), WR-04 (deleted SC#3 enforcement claim), WR-06a (CLAUDE.md's mypy-as-CI-gate claim, rewritten to describe the surviving local pre-commit hook accurately).
- Corrected WR-05 in `firestarter`: the no-DEV_TOOLS CI step comment no longer points at deleted vector-gate steps; the step and its substance are unchanged.
- Recorded WR-06b in `.planning/notes/host-tools-retirement.md` (Section 1, the mypy-CI-leg paragraph), and gave WR-01 an explicit, reasoned disposition (deletion via the provenance sweep, not a reword) in both the source todo and the provenance-sweep todo.

## Task Commits

Each task was committed atomically, one per repository:

1. **Task 1: Correct four stale claims in firestarter_app** — `71cc762` (docs) — `firestarter_app` repo
2. **Task 2: Make the no-DEV_TOOLS CI comment self-contained** — `447b73e` (ci) — `firestarter` repo
3. **Task 3: Record the mypy claim's survival and dispose of WR-01** — `3de9f3a8` (docs) — meta repo

No plan-metadata commit was made in the meta repo per this task's constraints (the orchestrator handles the docs commit and gitlink advancement).

## Files Created/Modified

- `firestarter_app/tests/test_sdp_db_invariant.py` — WR-02: replaced the "Direction matters" paragraph's closing sentence to stop naming a deleted checker script
- `firestarter_app/tests/test_numeric_schema_source_scan.py` — WR-03: singular/plural fix in a docstring opener and an assertion message, matching the already-correct module docstring
- `firestarter_app/tests/test_build_db_inclusion.py` — WR-04: dropped the trailing SC#3 dispatch-safety enforcement clause from the module docstring
- `firestarter_app/CLAUDE.md` — WR-06a: rewrote the "Tooling gate (v1.8)" line to state CI enforces ruff+pytest only, and mypy is a local pre-commit-only hook
- `firestarter/.github/workflows/beta-build.yml` — WR-05: replaced the three-line dead-referencing comment with a two-line self-contained one; step and run command untouched
- `.planning/notes/host-tools-retirement.md` — WR-06b: appended the mypy-claim-survival record to Section 1's existing mypy-CI-leg paragraph
- `.planning/todos/pending/2026-09-13-close-six-stale-claims-wr01-wr06.md` — added a dated Disposition section; annotated "Done when" to reflect WR-01 as the sole remaining condition
- `.planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md` — added a carry-over line qualifying the `firestarter_app/tools/` discharge (it covered `.planning/` citations only, not WR-01's comment)

## Decisions Made

- **WR-06a rewrite over deletion:** `.pre-commit-config.yaml` still wires `ruff-check → ruff-format → mypy` as measured at plan time, so the CLAUDE.md line was rewritten to say CI enforces `ruff check` + `ruff format --check` + `pytest --cov-fail-under=70`, and mypy is a local pre-commit-only hook — not simply deleting the word, which would have left the line's implicit "pre-commit mirrors CI" claim false in the other direction.
- **Section 1, not Section 2:** both the source todo and this plan's brief cited the retirement note's mypy paragraph as living in "§2". Measured directly in the file, it is in **§1** ("What was retired"), as the last paragraph, identified by its bold lead string `**The mypy CI leg (D-02) — retired, no replacement:**` rather than by section number. The correction was applied there.
- **WR-01 deliberately not touched:** it is a source comment at `firestarter_app/tools/parse_devtest_issue.py:215`. The hard no-comments-in-source rule forbids rewording it (that would still be a comment); its only compliant disposition is deletion, which belongs to the existing provenance-strip sweep. Recorded as the sole open item in the source todo, with a carry-over line added to the provenance-sweep todo so the Phase 188 "DISCHARGED" measurement (which covered `.planning/` citations only) is not misread as covering it.
- **Todo stays under `pending/`:** the source todo's own "Done when" block requires all six WRs closed; five-of-six is not "done" in a milestone named Claim Hygiene, so it was not moved to `completed/`. Its "Done when" block was updated in place to name WR-01's deletion as the sole remaining condition.

## Deviations from Plan

None — plan executed exactly as written, in the specified task order. One measurement in the plan's overall `<verification>` step 5 differed from its stated expectation; reported here rather than restated:

- **Tree-wide staleness sweep (plan step 5) measured 5, not 0.** The plan expected `grep -rn 'already gates elsewhere\|tests 1 and 2\|Same rationale as the vector gates' firestarter_app/tests firestarter/.github | wc -l` to return 0. It returned **5**, all five in `firestarter_app/tests/test_skip_census.py` (lines 66, 71, 321, 331, 345), an unrelated module with no connection to WR-03. That file's own numbered test list genuinely has two tests named "1" and "2" in its own docstring — its "tests 1 and 2" phrase is a correct, in-scope self-reference, not a stale claim left over from the WR-03 file (`test_numeric_schema_source_scan.py`). Verified by reading the file: it documents five tests (`test_no_skip_claims_firmware_absent_while_marker_present`, `test_every_skip_reason_is_allow_listed`, plus three more), and its "tests 1 and 2" references are internally consistent with that numbering. Out of scope per the plan's own file list for WR-03 (`firestarter_app/tests/test_numeric_schema_source_scan.py` only); not modified.

## Issues Encountered

- The firmware repo's own test suite (`test_requirement_case_mapping_v131.py`, `test_trace_segment_exhaustiveness_v131.py`) asserts its own working tree is porcelain-clean via `_git_porcelain`. Running the full suite before committing Task 2's edit produced 5 failures (dirty tree from the uncommitted `beta-build.yml` edit). This was expected and resolved by committing first, then running the suite — matching the plan's own task ordering (commit, then verify), not a real regression.
- A concurrent, unrelated commit (`d957001d`, "docs: capture exploration — 999.9 repo rename impact and sequencing", authored by the operator) landed on the shared branch in the meta repo after this task's commit (`3de9f3a8`). It touches no file this task modified; noted here for the record, not a deviation from this plan.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All five WR-02..WR-06 stale claims are closed. WR-01 remains open, tracked in both `.planning/todos/pending/2026-09-13-close-six-stale-claims-wr01-wr06.md` (as the sole remaining item) and `.planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md` (carry-over line).
- The orchestrator still needs to advance the meta repo's submodule gitlinks onto commits `71cc762` (firestarter_app) and `447b73e` (firestarter) — deliberately not done here per this task's constraints.
- Measured test counts, matching the pre-edit baseline exactly: firestarter_app **2129 passed** (ruff check clean, ruff format 155 files formatted); firestarter **316 passed**. `beta-build.yml` parses as valid YAML.

## Self-Check: PASSED

All 8 modified/created files verified present on disk; all 3 commit hashes (`71cc762` in `firestarter_app`, `447b73e` in `firestarter`, `3de9f3a8` in the meta repo) verified present in their respective repository histories.

---
*Quick task: 260913-e7t*
*Completed: 2026-09-13*
