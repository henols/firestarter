---
phase: 188-the-tools-directory
plan: 05
subsystem: testing
tags: [pytest, ruff, ci, deletion, d-04, d-05, d-06, d-07, d-08, d-09, d-15]

requires:
  - phase: 188-04
    provides: "the measured 2175-collected, 0-error baseline this plan's starting point; tools/ holding zero check_*.py gates"
  - phase: 188-01
    provides: "diff_db.py's relocated copy at .claude/skills/devtest-rootcause/scripts/diff_db.py, tracked in the meta repo before this plan's Task 1 precondition allows the host original to be deleted"
provides:
  - "The six GSD-process tools retired whole (audit_coverage_matrix.py, diff_db.py, measure_plan_shapes.py, measure_part_number_delta.py, snapshot_report_shapes.py, build_devtest_issue_corpus.py) with their five dedicated test files and two orphaned data artifacts"
  - "audit_coverage_matrix.py --check's literal pre-deletion behaviour measured for TOOLS-07's honest discharge: exit 1, zero bytes on both stdout and stderr"
  - "The two CI mirrors, the derive_sdp_partition.py orphan, and the host half of the frame-vector wire-byte contract deleted whole, with its two CI steps, in one commit"
  - "firestarter_app/tools/ ends at exactly the six D-14 survivors"
  - "The two residual render_shape prose mentions 188-04 deferred (WINDOWS.md entry 7) settled now that snapshot_report_shapes.py is actually gone"
affects: ["188-07 (provenance sweep; the four already-swept comment blocks in pyproject.toml and the settled cross-references in test_skip_census.py/test_voltage_field_census.py are candidates to confirm swept)", "188-09 (verdict note needs: the coverage-matrix checker's measured exit-1/zero-output, what the frame-vector contract test asserted, the plan-check discrepancy on the version-specifier regex, and REQUIREMENTS.md TOOLS-01/04/06/07 still reading Pending pending the whole-phase RETIRED amendment)"]

actuals:
  tokens: 143842
  tasks: 2
  commits: 3
  plan_head_before: 0f251f0df1e73bcf7ec6e58c06cd5259d7ba077c

tech-stack:
  added: []
  patterns:
    - "When a constant is shared between a real-file scan test and a synthetic non-vacuity test, check ALL its consumers before deleting it -- _AUDIT_COVERAGE_MATRIX_FORBIDDEN_TOKEN was kept (only its path-constant sibling and the real-file-scan test were deleted) because test_scan_helper_detects_planted_forbidden_tokens still exercises it as one of four synthetic planted tokens."
    - "A diff-line regex verify leg written to catch a moved dependency specifier can also fire on prose: a deleted comment line describing 'Upper bound <3' contains the same character shape the regex polices, with no way to satisfy both 'remove every mention of the retired tool' and 'zero diff lines match a version-specifier pattern' at once. Documented as a plan-check discrepancy (matching 188-06's precedent) rather than forced -- the actual dependency line is unchanged, confirmed separately."
    - "A sibling plan's SUMMARY can explicitly hand off a settle-later item (188-04's WINDOWS.md entry 7, the two render_shape prose mentions it deliberately left in place pending this plan's deletion of the file they named) -- read the prior plan's Next Phase Readiness section before assuming a file outside your own files_modified needs no attention."

key-files:
  created: []
  modified:
    - firestarter_app/tools/audit_coverage_matrix.py (deleted, 1952 lines)
    - firestarter_app/tools/diff_db.py (deleted, 984 lines -- relocated copy already tracked at .claude/skills/devtest-rootcause/scripts/diff_db.py)
    - firestarter_app/tools/measure_plan_shapes.py (deleted, 370 lines)
    - firestarter_app/tools/measure_part_number_delta.py (deleted, 303 lines)
    - firestarter_app/tools/snapshot_report_shapes.py (deleted, 190 lines)
    - firestarter_app/tools/build_devtest_issue_corpus.py (deleted, 345 lines)
    - firestarter_app/tests/test_audit_coverage_matrix.py (deleted, 646 lines)
    - firestarter_app/tests/test_audit_coverage_matrix_default_paths.py (deleted, 147 lines)
    - firestarter_app/tests/test_diff_db_gate.py (deleted, 234 lines)
    - firestarter_app/tests/test_plan_shapes_drift.py (deleted, 201 lines)
    - firestarter_app/tests/test_part_number_delta_drift.py (deleted, 170 lines)
    - firestarter_app/tests/fixtures/plan_shapes.json (deleted, 828 lines)
    - firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md (deleted, 1270 lines)
    - firestarter_app/tests/test_numeric_schema_source_scan.py (repaired: test 2 leg + its path constant deleted, docstring renumbered, non-vacuity comment trimmed; token constant kept since test 4 still uses it; 8->7 collected)
    - firestarter_app/pyproject.toml (5 stale comment blocks naming deleted tools amended, zero dependency specifiers touched)
    - firestarter_app/tests/test_skip_census.py (dropped the now-unreachable "meta-repo ledger not available at" allow-listed skip reason and its explanatory comment; not in files_modified, Rule 1)
    - firestarter_app/tests/test_voltage_field_census.py (dropped the test_diff_db_gate.py entry from _FALSE_POSITIVE_CANDIDATE_NAMES and the docstring prose; also settled the already-stale test_check_dispatch_invariants.py docstring mention orphaned by 188-03; not in files_modified, Rule 1)
    - firestarter_app/tools/ci_parity.sh (deleted, 162 lines)
    - firestarter_app/tools/ci_replica_venv.sh (deleted, 363 lines)
    - firestarter_app/tools/derive_sdp_partition.py (deleted, 263 lines)
    - firestarter_app/tools/catalog/codegen_vectors.py (deleted, 418 lines)
    - firestarter_app/tools/catalog/frame-vectors.toml (deleted, 120 lines)
    - firestarter_app/firestarter/frame_vectors.py (deleted, 129 lines)
    - firestarter_app/tests/test_frame_vectors.py (deleted, 282 lines, 13 tests)
    - firestarter_app/.github/workflows/ci.yml (two vector CI steps deleted; catalog/messages.py pair untouched)
    - firestarter_app/tests/test_blast_radius_invariance.py (settled WINDOWS.md entry 7: two residual render_shape prose mentions removed, follow-up commit; not in files_modified, Rule 1)

key-decisions:
  - "diff_db.py deleted from firestarter_app only after confirming its relocated copy was tracked at .claude/skills/devtest-rootcause/scripts/diff_db.py in the meta repo (precondition verify leg: git ls-files count = 1, checked before any deletion)."
  - "_AUDIT_COVERAGE_MATRIX_FORBIDDEN_TOKEN was kept in test_numeric_schema_source_scan.py (only its path constant _AUDIT_COVERAGE_MATRIX_PY and its own test function were deleted) because test_scan_helper_detects_planted_forbidden_tokens' non-vacuity leg still feeds it into _find_forbidden_tokens as one of four synthetic planted tokens -- deleting it would have broken a surviving test, not just removed dead code."
  - "The pyproject.toml version-specifier diff-line regex verify leg (T-188-20's guard) trips on a false positive: the deleted 'Upper bound <3 (Phase 131 D-14): tools/check_mypy_watermark.py's...' comment contains '<3' in prose, which the regex cannot distinguish from an actual moved dependency pin. Documented as a plan-check discrepancy (matching 188-06's precedent for its own literal-count mismatches) rather than forced -- the actual mypy>=2.1.0,<3 dependency line is confirmed unchanged in the diff."
  - "Settled 188-04's deferred WINDOWS.md entry 7 (the two render_shape prose mentions in test_blast_radius_invariance.py) in a follow-up commit after Task 1 deleted snapshot_report_shapes.py, since 188-04 explicitly named this as this plan's job to confirm once the referenced file was actually gone. Removed only the stale file citation from each docstring (pure subtraction, no new prose), leaving the surrounding rationale intact; marked WINDOWS.md entry 7 status=fixed via `gsd-tools windows fixed 7`, verified .planning/config.json unpruned afterward."
  - "REQUIREMENTS.md TOOLS-01/04/06/07 deliberately left reading 'Pending' rather than hand-amended to RETIRED here, following 188-03's and 188-04's own precedent of not touching REQUIREMENTS.md despite completing their own share of TOOLS-03's work -- the whole-phase ledger amendment is deferred to 188-09's verdict note (D-22). requirements-completed below is copied verbatim from this plan's frontmatter as a documentation record of this plan's contribution, not a claim that the ledger reflects Complete."

requirements-completed: [TOOLS-01, TOOLS-04, TOOLS-06, TOOLS-07]

coverage:
  - id: D1
    description: "Retire the six GSD-process tools whole (audit_coverage_matrix.py, diff_db.py, measure_plan_shapes.py, measure_part_number_delta.py, snapshot_report_shapes.py, build_devtest_issue_corpus.py) with their five dedicated test files and two orphaned data artifacts (plan_shapes.json fixture, v1.3-COVERAGE-MATRIX.md golden file); repair test_numeric_schema_source_scan.py, test_skip_census.py and test_voltage_field_census.py's stale cross-references; amend five stale pyproject.toml comment blocks without touching any dependency specifier"
    requirement: "TOOLS-04"
    verification:
      - kind: other
        ref: "git ls-files (all 13 deletion targets + 4 named cross-reference edits) -> 0 survivors; pytest tests/ --co -q -o addopts='' -> 2142 collected, 0 errors; pytest tests/ -o addopts='' -q -> 2142 passed; ruff check/format --check firestarter/ tests/ -> clean"
        status: pass
    human_judgment: false
  - id: D2
    description: "Measure audit_coverage_matrix.py --check's literal current behaviour before deletion, for TOOLS-07's honest discharge (the requirement is dissolved by deletion per D-06, not fixed)"
    requirement: "TOOLS-07"
    verification:
      - kind: other
        ref: "python tools/audit_coverage_matrix.py --check -> exit 1, 0 bytes stdout, 0 bytes stderr (measured 2026-09-13, matches CONTEXT.md's prior measurement exactly)"
        status: pass
    human_judgment: false
  - id: D3
    description: "diff_db.py deleted from firestarter_app only after confirming plan 188-01's relocated copy is tracked in the meta repo (precondition gate)"
    requirement: "TOOLS-04"
    verification:
      - kind: other
        ref: "git -C /workspaces ls-files -- .claude/skills/devtest-rootcause/scripts/diff_db.py | wc -l -> 1 (checked before Task 1's deletions)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Retire the two CI mirrors (ci_parity.sh, ci_replica_venv.sh), the derive_sdp_partition.py orphan, and the host half of the frame-vector wire-byte contract (codegen_vectors.py, frame-vectors.toml, frame_vectors.py, test_frame_vectors.py) whole, with its two CI steps, in one commit; no packaging edit; ruff check tools/ clean; coverage floor holds"
    requirement: "TOOLS-06"
    verification:
      - kind: other
        ref: "git ls-files (7 deletion targets) -> 0; repo-wide git grep codegen_vectors|frame_vectors|frame-vectors -> 0 hits anywhere in firestarter_app; grep ci.yml for codegen_vectors -> 0, for the two surviving message steps -> 2; git status --porcelain pyproject.toml (this task's commit) -> empty; ruff check tools/ -> clean; pytest tests/ --cov=firestarter --cov-fail-under=70 -o addopts='' -q -> 2129 passed, TOTAL 5871/896/84.74%"
        status: pass
    human_judgment: false
  - id: D5
    description: "Settle 188-04's deferred WINDOWS.md entry 7 (two residual render_shape prose mentions in test_blast_radius_invariance.py) now that snapshot_report_shapes.py is actually deleted"
    requirement: "TOOLS-06"
    verification:
      - kind: other
        ref: "grep -c render_shape|snapshot_report_shapes tests/test_blast_radius_invariance.py -> 0; pytest tests/test_blast_radius_invariance.py -o addopts='' -q -> 68 passed; test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree (D-10 closure) -> 1 passed standalone; WINDOWS.md entry 7 status -> fixed"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-09-13
status: complete
---

# Phase 188 Plan 05: Retire the six GSD-process tools, the two CI mirrors, the orphan, and the host frame-vector apparatus Summary

**Deleted all six GSD-process tools (audit_coverage_matrix.py, diff_db.py, measure_plan_shapes.py, measure_part_number_delta.py, snapshot_report_shapes.py, build_devtest_issue_corpus.py) with their five tests and two orphaned data artifacts, then the two CI mirrors, the derive_sdp_partition.py orphan, and the host half of the frame-vector wire-byte contract with its two CI steps in one commit — suite measured 2175 -> 2142 -> 2129, 0 errors both boundaries, coverage floor holds at 84.74%, `tools/` now holds exactly the six D-14 survivors.**

## Performance

- **Duration:** ~40 min (two long full-suite/coverage-scale pytest runs, ~4.5-6 min each)
- **Tasks:** 2/2 completed
- **Files modified:** 27 (20 deleted, 7 edited/repaired — 3 of the 27 outside this plan's own `files_modified` list, justified below)

## Accomplishments

- **Precondition confirmed:** `.venv311/bin/python` reports 3.11.16; `.claude/skills/devtest-rootcause/scripts/diff_db.py` confirmed tracked in the meta repo (plan 188-01's relocated copy) before any deletion; app suite collected 2175 tests, 0 errors, matching 188-04's measured end state exactly.
- **Task 1 — the six GSD-process tools retired whole, their tests and orphaned data gone, three stale cross-references repaired:**
  - Measured `audit_coverage_matrix.py --check`'s literal pre-deletion behaviour for TOOLS-07's honest discharge: **exit 1, zero bytes on both stdout and stderr** — matching CONTEXT.md's D-06 measurement exactly.
  - Deleted `tools/audit_coverage_matrix.py`, `diff_db.py`, `measure_plan_shapes.py`, `measure_part_number_delta.py`, `snapshot_report_shapes.py`, `build_devtest_issue_corpus.py` (6 tools, 4144 lines), their five dedicated test files (`test_audit_coverage_matrix.py`, `test_audit_coverage_matrix_default_paths.py`, `test_diff_db_gate.py`, `test_plan_shapes_drift.py`, `test_part_number_delta_drift.py`), and two orphaned data artifacts (`tests/fixtures/plan_shapes.json`, `tests/golden/v1.3-COVERAGE-MATRIX.md`). `diff_db.py` is deleted only because plan 188-01 already relocated the skill's own copy — confirmed tracked in the meta repo before deletion, satisfying the Task 1 precondition and D-21's ordering constraint.
  - `tests/test_devtest_issue_corpus.py`, `tests/test_canonical_part_number.py`, `tests/fixtures/part_number_delta.json` and `tests/fixtures/devtest_issue_corpus.json` confirmed still tracked (surviving consumers, read committed data rather than invoking their generators). `tests/golden/` confirmed still holding its 7 other files.
  - Repaired `tests/test_numeric_schema_source_scan.py`: deleted the whole-file scan leg reading the now-gone `audit_coverage_matrix.py` (its own test function, its `_AUDIT_COVERAGE_MATRIX_PY` path constant, and the docstring bullet enumerating it), renumbered the remaining docstring bullets and section headers (2->1 shift), and trimmed the surviving non-vacuity leg's docstring reference from "tests 1 and 2" to "test 1". **Kept** `_AUDIT_COVERAGE_MATRIX_FORBIDDEN_TOKEN`, since `test_scan_helper_detects_planted_forbidden_tokens` (the non-vacuity leg) still feeds it into `_find_forbidden_tokens` as one of four synthetic planted tokens — deleting it would have broken a surviving test. 8 -> 7 collected in this module, all passing.
  - Amended five stale `pyproject.toml` comment blocks naming tools this phase deletes (the mypy `<3` upper-bound rationale citing `check_mypy_watermark.py`; the ruff `extend-exclude` justification citing `audit_coverage_matrix.py`'s golden-file byte-identity; the mypy `tests/fixtures/` exclude rationale citing both `check_diagnostic_report_claims.py` and `check_mypy_watermark.py`; a `[[tool.mypy.overrides]]` comment citing `check_mypy_watermark.py`) — deletions-only, zero dependency specifiers touched (`mypy>=2.1.0,<3` unchanged). `grep -cE 'audit_coverage_matrix|check_mypy_watermark|check_diagnostic_report_claims' pyproject.toml` -> 0.
  - Found and fixed two stale cross-references outside this task's own `files_modified` list, both directly orphaned by this task's own deletions (Rule 1): `tests/test_skip_census.py`'s `ALLOWED_SKIP_REASONS` allow-list entry `"meta-repo ledger not available at"` (the only producer of that skip reason was the now-deleted `test_audit_coverage_matrix.py`) and its explanatory comment; and `tests/test_voltage_field_census.py`'s `_FALSE_POSITIVE_CANDIDATE_NAMES` entry `"test_diff_db_gate.py"` plus its docstring prose — while there, also settled the already-stale `test_check_dispatch_invariants.py` docstring mention that 188-03 orphaned but never swept from this file's top docstring (the frozenset entry itself was already correctly removed by 188-03).
  - Whole suite: 2175 -> 2142 collected, 0 errors, 2142 passed. Both ruff legs clean.
  - Committed at `0c6a1c4`.
- **Task 2 — the two CI mirrors, the orphan, and the host frame-vector apparatus retired with its two CI steps, one commit:**
  - Deleted `tools/ci_parity.sh` and `tools/ci_replica_venv.sh` (both existed solely to make the now-removed mypy watermark leg trustworthy, D-02/D-07) and `tools/derive_sdp_partition.py` (no test, no code reference anywhere in any of the three repos, retired on operator judgment about value per D-15).
  - Deleted the host half of the frame-vector wire-byte contract whole: `tools/catalog/codegen_vectors.py`, `tools/catalog/frame-vectors.toml`, `firestarter/frame_vectors.py`, `tests/test_frame_vectors.py` (13 tests across 5 classes: `TestFrameVectorsEncodeLeg`, `TestFrameVectorsDecodeLeg`, `TestCrc8KnownAnswer`, `TestHostChunkFitsFirmwareDecodeCap`, `TestPerBoardBufferNegotiation`). No fragment preserved under any name — a repo-wide `git grep` for `codegen_vectors`/`frame_vectors`/`frame-vectors` returns **zero hits anywhere in firestarter_app**, cleaner than the firmware side's four historical-narration hits recorded in 188-06.
  - Deleted the two CI steps that invoked the retired generator (`Vector catalog validity check`, `Codegen drift gate (frame_vectors.py)`) in the same commit, confirmed via `grep -c codegen_vectors .github/workflows/ci.yml` -> 0 and the surviving `Catalog validity check` / `Codegen drift gate (messages.py)` pair -> 2 (untouched, D-10). YAML confirmed still parses; no double blank line.
  - No packaging edit: `pyproject.toml` byte-unchanged by this task (`git status --porcelain -- pyproject.toml` empty in this commit's scope) — `packages = ["firestarter"]` is declared at package level and never named the frame-vector module individually.
  - `ruff check tools/` clean (the plan's predicted "six errors" measured as only one live error pre-deletion, entirely inside the now-deleted `codegen_vectors.py`; zero after).
  - Whole suite: 2142 -> 2129 collected/passed, 0 errors. Coverage TOTAL 5871/896/**84.74%** (>= 70% floor; 7 statements lighter than 188-04's baseline of 5878 — exactly `frame_vectors.py`'s own statement count). Both ruff legs clean.
  - Committed at `ccf203b`.
- **Follow-up — settled 188-04's deferred WINDOWS.md entry 7:** with `snapshot_report_shapes.py` now genuinely deleted, the two `render_shape` prose mentions 188-04 deliberately left in `tests/test_blast_radius_invariance.py` (to preserve that plan's own added=0 diff invariant) were now factually false. Removed only the stale file citation from each docstring (pure subtraction, no new prose authored), leaving the surrounding rationale intact. `grep -cE 'render_shape|snapshot_report_shapes' tests/test_blast_radius_invariance.py` -> 0; all 68 collected tests in that module still pass; the D-10 closure test (`test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree`) passes standalone. Marked WINDOWS.md entry 7 `status: fixed` via `gsd-tools windows fixed 7`; `.planning/config.json` confirmed unpruned afterward. Committed at `216ce23`.
- **Final-state verification (post all three commits, tree clean):** `pytest tests/ --co -q -o addopts=""` -> **2129 collected, 0 errors**; `ruff format --check firestarter/ tests/` -> 155 files already formatted. `tools/` listing: exactly `build_db.py`, `catalog/codegen.py`, `gen_sdp_bus_config.py`, `gen_validation_header.py`, `parse_devtest_issue.py`, `gen_test_image.py` (D-14's six survivors), plus out-of-scope non-script data (`DECODE-NOTES.md`, `extra_chips.json`, `validation_matrix_spec.json`, `variant-decode-diff.txt`, `pin-layouts.odt`, `baseline/`, `catalog/messages.toml`).

## Task Commits

1. **Task 1: Retire the six GSD-process tools, their tests and their orphaned data** — `0c6a1c4` (feat, in `firestarter_app`)
2. **Task 2: Retire the two CI mirrors, the orphan, and the host half of the frame-vector apparatus, with its CI steps, one commit** — `ccf203b` (feat, in `firestarter_app`)
3. **Follow-up: settle WINDOWS.md entry 7's two residual render_shape mentions** — `216ce23` (fix, in `firestarter_app`)

**Plan metadata:** this SUMMARY commit (meta repo)

## Files Created/Modified

See `key-files.modified` in the frontmatter for the full list (27 files: 20 deleted, 7 edited/repaired — 3 of the 7 outside this plan's own `files_modified` list, justified in Deviations).

## Decisions Made

See `key-decisions` in the frontmatter. In summary: kept `_AUDIT_COVERAGE_MATRIX_FORBIDDEN_TOKEN` (a surviving test still uses it), documented the version-specifier regex's false-positive trip as a plan-check discrepancy rather than forcing an unnatural edit, settled 188-04's explicitly-deferred WINDOWS.md entry 7 now that its referenced file is actually gone, and left REQUIREMENTS.md's TOOLS-01/04/06/07 rows reading "Pending" per the established 188-03/188-04 precedent of deferring the whole-phase RETIRED amendment to 188-09.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Stale skip-reason allow-list entry in test_skip_census.py, orphaned by this task's own deletion**
- **Found during:** Task 1, sweeping for cross-references to the six deleted tools before finalizing
- **Issue:** `ALLOWED_SKIP_REASONS` carried the entry `"meta-repo ledger not available at"` with a comment explaining it as legitimate only for `tests/test_audit_coverage_matrix.py`'s standalone-checkout skip. That test is now deleted, and `git grep` confirms no other module produces this skip reason.
- **Fix:** Removed the entry and its six-line explanatory comment. This is a permit-list (extra unused entries are harmless, confirmed by reading `test_every_skip_reason_is_allow_listed`'s logic), so this is cleanup, not a required fix, but directly caused by this task's own deletion.
- **Files modified:** `firestarter_app/tests/test_skip_census.py`
- **Verification:** `pytest tests/test_skip_census.py --co -q -o addopts=""` -> 5 collected, unchanged; ruff clean.
- **Committed in:** `0c6a1c4`

**2. [Rule 1 - Bug] Stale test_diff_db_gate.py cross-reference in test_voltage_field_census.py, plus an already-stale sibling entry found while editing**
- **Found during:** Task 1, cross-checking 188-03's SUMMARY note (which explicitly named `test_diff_db_gate.py` as this plan's entry to settle) before deleting `tests/test_diff_db_gate.py`
- **Issue:** `_FALSE_POSITIVE_CANDIDATE_NAMES` carried `"test_diff_db_gate.py"`, and the module's top docstring named both `tests/test_diff_db_gate.py` and `tests/test_check_dispatch_invariants.py` (the latter deleted by 188-03, whose frozenset entry was already correctly removed but whose docstring mention was never swept) in its list of files with unrelated `vpp_mv`/`vpe_mv` textual hits.
- **Fix:** Removed `"test_diff_db_gate.py"` from the frozenset, and removed both stale file names from the docstring's enumeration in the same edit (since I was already touching that exact sentence for `test_diff_db_gate.py`).
- **Files modified:** `firestarter_app/tests/test_voltage_field_census.py`
- **Verification:** `pytest tests/test_voltage_field_census.py -o addopts="" -q` -> 4 passed, unchanged; ruff clean.
- **Committed in:** `0c6a1c4`

**3. [Rule 1 - Bug] Settled 188-04's deliberately-deferred WINDOWS.md entry 7**
- **Found during:** post-Task-1 review of 188-04's SUMMARY, which explicitly named this plan as the point where the two `render_shape` prose mentions in `tests/test_blast_radius_invariance.py` would become genuinely false
- **Issue:** 188-04 left two docstring mentions of `tools/snapshot_report_shapes.py:render_shape` in place to preserve its own added=0 diff invariant, since the file didn't exist yet to make the mentions false. Task 1 of this plan deletes `snapshot_report_shapes.py`, making both mentions stale.
- **Fix:** Removed only the file-citation clause from each docstring (pure subtraction), leaving the surrounding rationale (why the helper mirrors composition rather than duplicating it) intact. Not part of either task's own `files_modified`, so committed separately.
- **Files modified:** `firestarter_app/tests/test_blast_radius_invariance.py`
- **Verification:** `grep -cE 'render_shape|snapshot_report_shapes'` -> 0; `pytest tests/test_blast_radius_invariance.py -o addopts="" -q` -> 68 passed; D-10 closure test passes standalone.
- **Committed in:** `216ce23`

### Plan-authored check discrepancies (not code deviations)

**4. The pyproject.toml version-specifier diff-line regex verify leg trips on a false positive, not a real pin move.**
- The verify leg `git diff -U0 -- pyproject.toml | grep -E '^[+-][^+-]' | grep -cE '(>=|<=|==|~=|<[0-9]|>[0-9])'` is designed to catch an actual dependency pin changing. Its regex also matches "<3" appearing in ordinary prose. The deleted comment line `"# Upper bound <3 (Phase 131 D-14): tools/check_mypy_watermark.py's"` contains exactly that shape, so the leg reports 1, not 0, purely from a deleted comment's own wording — not from any dependency specifier moving. Confirmed separately: `mypy>=2.1.0,<3` is unchanged context in the diff (never touched), and this is inherent — any edit that both removes every literal mention of `check_mypy_watermark.py` (a hard acceptance criterion) and avoids ever touching a line containing "<3" in prose is not achievable, since the tool's name and the version-bound description share the same comment. Treated as a plan-check discrepancy (matching 188-06's precedent for its own literal-count/line-count mismatches), not a code defect.

---

**Total deviations:** 3 auto-fixed (all Rule 1 — stale references directly caused by this plan's own deletions, none in this plan's own `files_modified`) + 1 documented plan-check discrepancy (a verify leg's regex over-matches prose, not a real dependency pin move).
**Impact on plan:** No scope creep — all three auto-fixes are narrowly scoped to references this plan's own deletions orphaned, one of them explicitly handed off by a sibling plan's SUMMARY. The one discrepancy is a false positive in the verify leg's own regex, confirmed harmless by directly inspecting the diff for the actual dependency line.

## Issues Encountered

None beyond the deviations documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter_app/tools/` now holds exactly the six D-14 survivors (`build_db.py`, `catalog/codegen.py`, `gen_sdp_bus_config.py`, `gen_validation_header.py`, `parse_devtest_issue.py`, `gen_test_image.py`) plus out-of-scope non-script data files. Zero GSD-process tools, zero CI mirrors, zero orphans, zero frame-vector fragments remain on the host side.
- The frame-vector apparatus is now gone on BOTH sides (host here, firmware in 188-06) — D-08's disclosed, accepted cost (T-188-18: no mechanism left proving host and firmware agree on the same wire bytes) is fully realized. `tests/test_cobs.py` independently covers COBS/CRC8 on the host side; no product coverage is stranded.
- REQUIREMENTS.md's TOOLS-01, TOOLS-04, TOOLS-06 and TOOLS-07 rows still read "Pending" — this plan deliberately did not hand-amend them to RETIRED, following 188-03/188-04's own precedent of deferring the whole-phase ledger amendment (D-22) to plan 188-09's verdict note. 188-09 needs: this SUMMARY's measured coverage-matrix checker behaviour, the frame-vector contract test's assertions (recorded above), and the version-specifier regex plan-check discrepancy.
- WINDOWS.md entry 7 is now `fixed` (settled in this plan). Entries 6 and 8 (WR-01's death, the now-decorative AST leg in `test_lock_status_class_partition.py`) remain open, both disclosed D-01/D-04 costs for 188-09's verdict note to cite.
- This plan is file-disjoint from 188-07/188-08's own primary scopes, aside from the three out-of-file-list stale-reference repairs documented above (all narrowly justified, all confirmed non-breaking) and the pyproject.toml comment sweep, which is a candidate for 188-07's own provenance-sweep confirmation pass.
- No blockers for the remaining phase-188 plans.

## Self-Check: PASSED

- `FOUND: 188-05-SUMMARY.md` — `.planning/phases/188-the-tools-directory/188-05-SUMMARY.md` exists on disk.
- `git log --oneline --all` in `firestarter_app` shows all three commits present: `216ce23` (follow-up, HEAD) with parent `ccf203b` (Task 2) with parent `0c6a1c4` (Task 1) with parent `0f251f0` (188-04's Task 2, this plan's pinned base) — confirmed via `git rev-parse HEAD`, `HEAD^`, `HEAD^^`, `HEAD^^^`.
- `git rev-list --count 0f251f0..HEAD` in `firestarter_app` -> 3, matching `actuals.commits`.
- All Task 1 and Task 2 `<verify>` legs re-run clean at final HEAD: whole-suite collect 2129 (0 errors), whole-suite pass 2129, both ruff legs clean, coverage TOTAL 5871/896/84.74% (>= 70% floor), `ruff check tools/` clean, zero repo-wide hits for `codegen_vectors`/`frame_vectors`/`frame-vectors`, zero hits for `audit_coverage_matrix`/`check_mypy_watermark`/`check_diagnostic_report_claims` in `pyproject.toml`, the D-10 closure test passes standalone, `tools/` listing matches D-14 exactly.
- `git -C /workspaces status --porcelain .planning/config.json` -> empty at every check point (config.json never pruned during this plan's `gsd-tools` calls, including the `windows fixed` call).
- `firestarter_app`'s `HEAD` is on branch `gsd/v1.37-operator-safety-answered-reports-claim-hygiene` (verified before the first commit and re-verified before each subsequent commit); `git status --short` in `firestarter_app` shows only the pre-existing untracked operator datasheets (`datasheets/MBM27C1001.pdf`, `datasheets/MX27C4000.pdf`), nothing else.

---
*Phase: 188-the-tools-directory*
*Completed: 2026-09-13*
