---
phase: 188-the-tools-directory
plan: 04
subsystem: testing
tags: [pytest, ruff, ci, ast-gate, deletion, d-25, d-01, d-02, d-13]

requires:
  - phase: 188-03
    provides: "the measured 2307-collected, 0-error baseline this plan's precondition asserts, plus the eight-not-nine gate-count correction and the two settled fail-closed indexes (scan-path pair, exists-proxy enumeration) this plan continues from"
provides:
  - "The op-registration parity module deleted whole (7 tests) with its one collateral repaired against the surviving product module, zero collateral"
  - "The v1.36 blast-radius oracle trimmed to exactly its two render_shape sites (750-771, 805-829 pre-edit): 68 of 106 collected tests survive, GATE-01/02/03 and D-07/D-10 intact, the nineteen committed snapshots byte-unchanged and still asserted against by a passing D-10 closure test"
  - "All eight remaining check_*.py gates retired whole from tools/, with their eight test files (85 tests, three naming conventions) and seven planted-violation fixtures"
  - "tests/test_lock_status_class_partition.py repaired in the same commit (17->15), its surviving AST leg's docstring corrected to no longer claim a now-deleted pairing makes it non-decorative"
  - "The mypy CI step (and every mention of mypy anywhere in ci.yml, including a comment the plan's own read_first did not name) deleted in the same commit as the script it invokes"
  - "The Regression guard sentences in firestarter_app/CLAUDE.md removed; the 12V hazard paragraph they followed left intact and unedited"
  - "Whole suite measured 2307 -> 2262 (Task 1) -> 2175 (Task 2), 0 errors at both boundaries, both ruff legs green at both boundaries"
affects: ["188-05 (inherits render_shape/snapshot_report_shapes.py still live, and the two remaining prose mentions of it in test_blast_radius_invariance.py)", "188-07 (phase-wide provenance sweep; several out-of-file-list stale-reference fixes this plan made are candidates to confirm swept)", "188-09 (verdict note needs: WR-01's death, the decorative AST leg, the eight-not-nine gate count, tools/baseline/dispatch_baseline.json's orphaned-data status, and the CLAUDE.md Tooling-gate line's now-partial inaccuracy)"]

actuals:
  tokens: 94800
  tasks: 2
  commits: 2
  plan_head_before: 7ebdef85df813a95f6a35a82fe74914de165b8fc

tech-stack:
  added: []
  patterns:
    - "When a docstring/comment names a symbol or file being deleted by the SAME commit, delete the naming clause rather than rewrite it -- applied to two CI header-comment enumerations, one CLAUDE.md guard paragraph, one test-module docstring paragraph and coverage-list line, and two same-directory prose asides discovered while confirming fixture consumers (none of the four target files were in this plan's own files_modified list)."
    - "When two explicit plan invariants conflict (a strict zero-occurrence grep vs. an explicit 'leave this function exactly as it is' / 'diff must be deletions-only' instruction), prefer the invariant with a stated threat-model rationale (T-188-13's added=0 check exists so the milestone's own oracle cannot be silently rewritten) over a blanket textual grep that does not distinguish a functional reference from accurate, still-true documentation prose."
    - "git grep -ln across tests/ tools/ .github/ pyproject.toml before deleting any fixture, even ones a plan's file list already scopes -- two of the seven fixtures deleted here had an extra hit each, both confirmed to be docstring/comment mentions rather than loads, exactly as the plan's read_first predicted."

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_op_registration_parity.py (deleted, 7 tests)
    - firestarter_app/tests/test_blast_radius_invariance.py (trimmed: -47 lines net, 106->68 tests, deletions-only diff)
    - firestarter_app/tests/test_chip_test.py (repaired: import replaced with in-function derivation, 159 tests unchanged)
    - firestarter_app/tools/check_devtest_orchestrator.py (deleted)
    - firestarter_app/tools/check_is_memory_cmd_no_ifdef.py (deleted)
    - firestarter_app/tools/check_mypy_watermark.py (deleted)
    - firestarter_app/tools/check_no_community_support_status_write.py (deleted)
    - firestarter_app/tools/check_no_exists_proxy.py (deleted)
    - firestarter_app/tools/check_no_log_in_sdp_window.py (deleted)
    - firestarter_app/tools/check_protection_readability_invariants.py (deleted)
    - firestarter_app/tools/check_sdp_capability_invariants.py (deleted)
    - firestarter_app/tests/test_check_devtest_orchestrator.py (deleted)
    - firestarter_app/tests/test_check_is_memory_cmd_no_ifdef.py (deleted)
    - firestarter_app/tests/test_check_mypy_watermark.py (deleted)
    - firestarter_app/tests/test_check_no_community_support_status_write.py (deleted)
    - firestarter_app/tests/test_check_no_exists_proxy.py (deleted)
    - firestarter_app/tests/test_check_no_log_in_sdp_window.py (deleted)
    - firestarter_app/tests/test_check_protection_readability.py (deleted)
    - firestarter_app/tests/test_check_sdp_capability.py (deleted)
    - firestarter_app/tests/fixtures/planted_ifdef_in_predicate.h (deleted)
    - firestarter_app/tests/fixtures/planted_log_in_window.cpp (deleted)
    - firestarter_app/tests/fixtures/planted_no_exists_proxy.py (deleted)
    - firestarter_app/tests/fixtures/planted_permit_by_default.py (deleted)
    - firestarter_app/tests/fixtures/planted_widenable_allowset.py (deleted)
    - firestarter_app/tests/fixtures/planted_protection_widenable_tokenset.py (deleted)
    - firestarter_app/tests/fixtures/planted_protection_permit_by_default.py (deleted)
    - firestarter_app/tests/test_lock_status_class_partition.py (repaired: -63 lines, 17->15 tests, two stale docstring clauses removed)
    - firestarter_app/.github/workflows/ci.yml (mypy step + 3 mypy mentions removed, zero mypy occurrences remain, 8 other steps confirmed present)
    - firestarter_app/CLAUDE.md (Regression guard sentences removed, hazard paragraph intact)
    - firestarter_app/tests/fixtures/synthetic_nonzero_chip_id.py (stale clause naming a deleted fixture removed, not in files_modified)
    - firestarter_app/tests/test_sdp_db_invariant.py (stale sentence naming a deleted gate+fixture removed, not in files_modified)
    - firestarter_app/tests/test_voltage_field_census.py (settled the check_devtest_orchestrator.py entry 188-03's SUMMARY named for this plan, not in files_modified)

key-decisions:
  - "Reverted an initial attempt to also scrub two render_shape/snapshot_report_shapes.py prose mentions inside test_blast_radius_invariance.py (in the _DB_DIFF_KEYS docstring and _to_dict_with_db_diff's docstring) after the edit produced added=2 in the file's numstat diff, violating the plan's explicit 'deletions-only, T-188-13' invariant and its explicit instruction to leave _to_dict_with_db_diff exactly as it is. Kept the file diff strictly deletions-only (added=0, deleted=47) and left those two mentions in place -- they are not yet false, since render_shape itself survives until plan 188-05. This means the plan's own 'grep -c render_shape/snapshot_report_shapes == 0' acceptance criterion is not fully met (measured 2, not 0); logged as WINDOWS.md deviation entry 7 rather than silently accepted."
  - "Found and fixed three stale references to files this task deletes, outside this task's own files_modified list: tests/fixtures/synthetic_nonzero_chip_id.py's aside naming planted_permit_by_default.py, tests/test_sdp_db_invariant.py's sentence naming check_sdp_capability_invariants.py + planted_widenable_allowset.py, and tests/test_voltage_field_census.py's check_devtest_orchestrator.py entry (explicitly named as this plan's job in 188-03's own SUMMARY). All three are deletion-only clause/entry removals with zero collected-count change in their own modules (confirmed: 4, 9, and 4 tests respectively, unchanged)."
  - "Left firestarter_app/CLAUDE.md's separate 'Tooling gate (v1.8)' line untouched even though it now overstates mypy's CI enforcement (mypy still runs locally via .pre-commit-config.yaml, but no longer via ci.yml) -- the plan's own instruction was to remove ONLY the sentences beginning 'Regression guard:', and this line is a different paragraph the plan's read_first and acceptance criteria never named. Flagged here for 188-09's verdict note rather than fixed silently."
  - "Settled test_voltage_field_census.py's check_devtest_orchestrator.py entry in _FALSE_POSITIVE_CANDIDATE_NAMES and its docstring clause in this same commit, completing the two-entry handoff 188-03's SUMMARY explicitly named for this plan (the sibling entry, test_diff_db_gate.py, stays for plan 188-05 to settle when it deletes that file)."

requirements-completed: []

coverage:
  - id: D1
    description: "Delete tests/test_op_registration_parity.py whole (7 tests, all consuming the retired orchestrator gate's handler allow-list) and repair the one collateral test in tests/test_chip_test.py (test_run_status_is_complete_when_no_step_errored) by deriving the same two op-vocabulary sets in-function from firestarter.chip_test, rather than importing them from the deleted module -- collateral zero, 159 collected tests in that module unchanged"
    requirement: "TOOLS-03"
    verification:
      - kind: other
        ref: "pytest tests/test_blast_radius_invariance.py tests/test_chip_test.py --co -q -o addopts='' -> 227 collected (68+159); pytest tests/ --co -q -o addopts='' -> 2262 collected, 0 errors; ruff check/format --check firestarter/ tests/ -> clean"
        status: pass
    human_judgment: false
  - id: D2
    description: "Trim tests/test_blast_radius_invariance.py to its two render_shape-consuming sites only (test_committed_snapshot_matches_a_fresh_regeneration / WR-01, and test_composing_a_db_diff_never_leaks_onto_a_cached_build_shape / CR-01's second aliasing path), leaving 68 of 106 tests, GATE-01/02/03 and D-07/D-10 intact, the nineteen committed snapshots byte-unchanged, and a deletions-only diff (added=0)"
    requirement: "TOOLS-03"
    verification:
      - kind: other
        ref: "pytest tests/test_blast_radius_invariance.py --co -q -o addopts='' -> 68 collected; pytest tests/test_blast_radius_invariance.py::test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree -> 1 passed; git diff --numstat <pinned base> -- tests/test_blast_radius_invariance.py -> added=0; git diff --numstat <pinned base> -- tests/fixtures/reports/ -> empty (0 files changed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Retire the eight remaining check_*.py gates whole from tools/, their eight test files (85 collected tests across all three D-03 naming conventions) and the seven planted-violation fixtures whose only consumers were those tests; confirm each gate-to-test mapping and each fixture's consumer set by reading/grep rather than assuming"
    requirement: "TOOLS-03"
    verification:
      - kind: other
        ref: "git ls-files -- 'tools/check_*.py' 'tests/test_check_*.py' -> 0 files; git ls-files -- tools/*.py -> 14 files; git ls-files -- <7 deleted fixture paths> -> 0; git ls-files -- <3 kept fixture/data paths> -> 3; pytest tests/ --co -q -o addopts='' -> 2175 collected, 0 errors"
        status: pass
    human_judgment: false
  - id: D4
    description: "Repair tests/test_lock_status_class_partition.py in the same commit: delete the subprocess helper and the two tests routing the now-deleted protection-permit-by-default fixture through the retired gate (17->15 collected), and delete the docstring clause in the surviving AST test that named that pair as what made it non-decorative (it is now decorative, disclosed as a second D-01 cost)"
    requirement: "TOOLS-03"
    verification:
      - kind: other
        ref: "pytest tests/test_lock_status_class_partition.py --co -q -o addopts='' -> 15 collected; ruff check/format --check -> clean"
        status: pass
    human_judgment: false
  - id: D5
    description: "Delete the mypy CI step and every mention of mypy anywhere in ci.yml (its own name/run lines, the D-07 header enumeration, the CI-runs-on-every-branch historical note, and the ci-py32 job's own comment naming it -- found while confirming the header-only edit, not named in the plan's read_first) in the same commit as tools/check_mypy_watermark.py; leave the two vector CI steps (188-05's) and the catalog/ruff/pytest/smoke steps untouched"
    requirement: "TOOLS-03"
    verification:
      - kind: other
        ref: "grep -ci mypy .github/workflows/ci.yml -> 0; grep -c <8 named surviving step strings> .github/workflows/ci.yml -> 8; awk double-blank-line scan -> 0; python3 -c yaml.safe_load(...) -> OK"
        status: pass
    human_judgment: false
  - id: D6
    description: "Remove the Regression guard sentences in firestarter_app/CLAUDE.md naming the already-deleted tools/check_dispatch.py, leaving the 12V-hazard paragraph (manufacturer list, seven-exception sentence) intact and unedited -- confirmed coherent by a manual read-back, not just a grep"
    requirement: "TOOLS-03"
    verification:
      - kind: other
        ref: "grep -c 'Regression guard' CLAUDE.md -> 0; grep -c 'hardware-damage path' CLAUDE.md -> 1; manual read-back of CLAUDE.md:95-127 confirms the paragraph reads coherently without the removed sentences"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-09-13
status: complete
---

# Phase 188 Plan 04: Finish the D-25 parity/blast-radius deletions and retire the eight remaining check_*.py gates whole Summary

**Deleted the op-registration parity module and trimmed the v1.36 blast-radius oracle to its two render_shape sites (68/106 tests survive, GATE-01/02/03 and D-07/D-10 intact, nineteen snapshots byte-unchanged), then retired all eight remaining `check_*.py` gates, their tests, seven planted fixtures, the mypy CI step and the CLAUDE.md guard prose -- suite measured 2307 -> 2262 -> 2175, 0 errors at both boundaries.**

## Performance

- **Duration:** ~50 min (two long full-suite/coverage-scale pytest runs, ~4.5-5 min each)
- **Tasks:** 2/2 completed
- **Files modified:** 32 (23 deleted, 9 edited/trimmed/repaired -- 3 of the 9 outside this plan's own `files_modified` list, justified below)

## Accomplishments

- **Precondition confirmed:** `.venv311/bin/python` reports 3.11.16; the app suite collected 2307 tests, 0 errors, matching 188-03's measured end state exactly.
- **Task 1 -- the parity module deleted, the blast-radius oracle trimmed, the one collateral repaired:**
  - `tests/test_op_registration_parity.py` deleted whole (7 tests). Nothing relocated -- the allow-list it consumed dies with `tools/check_devtest_orchestrator.py` in Task 2.
  - `tests/test_chip_test.py::test_run_status_is_complete_when_no_step_errored` repaired in the same commit: its in-function import of `_ALL_OPS`/`_MULTIWORD_OP_VALUES` from the deleted module replaced with the exact two comprehensions that module used, derived in-function from `firestarter.chip_test` (the 17th such `import firestarter.chip_test as chip_test_mod` idiom in this file). Docstring and all three assertions unchanged. 159 collected tests in that module, unchanged.
  - `tests/test_blast_radius_invariance.py` trimmed to exactly its two `render_shape`-consuming sites: `test_committed_snapshot_matches_a_fresh_regeneration` (WR-01, 19 parametrized tests) and `test_composing_a_db_diff_never_leaks_onto_a_cached_build_shape` (CR-01's second aliasing path, 19 parametrized tests) deleted, each with its parametrize decorator and exactly one surrounding blank-line pair (confirmed by a manual read-back at both cut points: no stray decorator, no dangling docstring fragment, tests immediately above and below each cut intact). 68 of 106 collected tests survive; GATE-01, GATE-02, GATE-03, D-07 and D-10 untouched. The diff over this file is deletions-only: `added=0`, `deleted=47`.
  - `tests/fixtures/reports/` (19 committed snapshots) confirmed byte-unchanged: `git diff --numstat` against this plan's pinned pre-phase base is empty for that directory. `test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree` (D-10's four-way closure) passes standalone.
  - Whole suite: 2307 -> 2262 collected, 0 errors, matching the plan's own ledger exactly.
  - Committed at `a163dd9`.
- **Task 2 -- the eight remaining gates retired whole, with their tests, seven fixtures, the mypy CI step and the guard prose, one commit:**
  - All eight remaining `tools/check_*.py` gates deleted: `check_devtest_orchestrator.py`, `check_is_memory_cmd_no_ifdef.py`, `check_mypy_watermark.py`, `check_no_community_support_status_write.py`, `check_no_exists_proxy.py`, `check_no_log_in_sdp_window.py`, `check_protection_readability_invariants.py`, `check_sdp_capability_invariants.py`. `git ls-files -- 'tools/check_*.py'` returns zero.
  - Their eight test files deleted with them (85 collected tests), each mapping confirmed by reading the test file's own imports first (not assumed): five follow `test_<gate>.py`; `test_check_protection_readability.py` and `test_check_sdp_capability.py` drop the `_invariants` suffix (D-03's two non-obvious names; the third, the dispatch gate's test, already left with plan 188-03).
  - Seven planted-violation fixtures deleted with their gates, each consumer set confirmed by `git grep -ln` across `tests/ tools/ .github/ pyproject.toml` before deletion (not trusted from the plan's list): `planted_ifdef_in_predicate.h`, `planted_log_in_window.cpp`, `planted_no_exists_proxy.py`, `planted_permit_by_default.py`, `planted_widenable_allowset.py`, `planted_protection_widenable_tokenset.py`, `planted_protection_permit_by_default.py`. Two of the seven had one extra hit each beyond their primary gate/test pair -- both confirmed to be docstring/comment mentions rather than loads (see Deviations). `planted_unparsable.py` (a live `pyproject.toml` mypy-exclude rationale) and `part_number_delta.json` (loaded directly by the surviving `tests/test_canonical_part_number.py`) confirmed still tracked.
  - `tests/test_lock_status_class_partition.py` repaired in the same commit: the subprocess helper `_run_protection_readability_checker` and the two tests routing the now-deleted `planted_protection_permit_by_default.py` fixture through the retired protection-readability gate deleted (17 -> 15 collected, confirmed clean two-blank-line boundary). The surviving AST leg's (`test_silicon_only_tokens_never_appear_in_a_return_value_ast`) docstring clause naming that pair as what made it non-decorative removed -- it is now decorative, since nothing left proves the AST rule can fail; disclosed as a second D-01 cost. Two further now-stale mentions in the same module (the top-of-file docstring's "unreachability leg (leg 4) consumes..." bullet, and the Task-2 coverage-list line "paired with the planted fixture routed through the subprocess gate seam") trimmed for the same reason -- both are full-clause/full-bullet deletions, not rewrites. `os`/`subprocess`/`sys` imports, now unused, removed.
  - `.github/workflows/ci.yml`: the mypy step (name + run line + the one trailing blank separator) deleted, leaving no double blank. Three separate mentions of "mypy" removed: the D-07 header enumeration ("gate steps: ruff check, ruff format --check, mypy watermark, pytest --cov" -> without "mypy watermark,"), the CI-runs-on-every-branch historical note ("ruff, the mypy watermark and the coverage floor" -> "ruff and the coverage floor"), and a third the plan's read_first did not name: the `ci-py32` job's own comment ("Runs no ruff/ruff-format/mypy/coverage/codegen-drift step" -> without "mypy/"). `grep -ci mypy` over the whole file returns 0. The two vector CI steps (188-05's) and the catalog/ruff/pytest/smoke steps confirmed present (8/8 named strings found); the file still parses as valid YAML.
  - `firestarter_app/CLAUDE.md`: the `Regression guard:` sentences naming `tools/check_dispatch.py` (already deleted since 188-03, one wave earlier than the previous plan draft assumed) removed. The 12V hazard paragraph -- the manufacturer list and the seven-chip exception sentence -- confirmed intact by a manual read-back, reading coherently without the removed sentences.
  - `tools/baseline/dispatch_baseline.json` left in place: orphaned data with zero consumers after this plan, but D-14 scopes this phase to scripts, retained data files out of scope. Confirmed still tracked.
  - Whole suite: 2262 -> 2175 collected, 0 errors, matching the plan's own ledger exactly.
  - Committed at `0f251f0`.
- **Final-state verification (post both commits, tree clean):** `pytest tests/ -o addopts="" -q` -> **2175 passed, 1 warning** (a pre-existing Click `MultiCommand` deprecation warning, unrelated to this plan) in 274.90s; `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both clean; the D-10 closure test re-run standalone at final HEAD, 1 passed.

## Task Commits

1. **Task 1: Delete the parity module whole, trim the blast-radius oracle to its two render_shape sites, repair the one collateral** - `a163dd9` (feat, in `firestarter_app`)
2. **Task 2: Retire the eight remaining gates, their tests, seven fixtures, the mypy CI step and the guard prose** - `0f251f0` (feat, in `firestarter_app`)

**Plan metadata:** this SUMMARY commit (meta repo)

## Files Created/Modified

See `key-files.modified` in the frontmatter for the full list (32 files: 23 deleted, 9 edited).

## Decisions Made

See `key-decisions` in the frontmatter. In summary: kept `tests/test_blast_radius_invariance.py`'s diff strictly deletions-only (reverting an initial attempt to also scrub two still-accurate `render_shape` prose mentions), fixed three stale cross-references outside this plan's own file list (justified by direct causation from this plan's own deletions, two of them confirmed via the plan's own predicted "docstring mention, not a load" pattern), and settled `test_voltage_field_census.py`'s `check_devtest_orchestrator.py` entry as explicitly handed off by 188-03's SUMMARY.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] A third `mypy` mention in ci.yml the plan's read_first did not name**
- **Found during:** Task 2, re-verifying `grep -ci mypy` after the two header edits the plan explicitly named
- **Issue:** The `ci-py32` job's own comment block ("Runs no ruff/ruff-format/mypy/coverage/codegen-drift step: the primary `ci` job already gates all of those over the whole tree") also named mypy, and remained false once the primary job stopped running it. The plan's read_first cited only the D-07 header line and the historical note.
- **Fix:** Removed "mypy/" from the enumeration, leaving "Runs no ruff/ruff-format/coverage/codegen-drift step".
- **Files modified:** `firestarter_app/.github/workflows/ci.yml`
- **Verification:** `grep -ci mypy .github/workflows/ci.yml` -> 0; YAML still parses; 8/8 named surviving steps present.
- **Committed in:** `0f251f0`

**2. [Rule 1 - Bug] Two same-directory prose mentions of soon-to-be-deleted files, outside this task's own fixture list**
- **Found during:** Task 2, running `git grep -ln` over each of the seven planted fixtures' consumers before deleting (per the plan's own read_first instruction to confirm rather than trust)
- **Issue:** `tests/fixtures/synthetic_nonzero_chip_id.py` named `planted_permit_by_default.py` in an aside, and `tests/test_sdp_db_invariant.py` named both `check_sdp_capability_invariants.py` and `planted_widenable_allowset.py` in a closing sentence. Neither file is in this plan's `files_modified`, but both mentions become stale the moment this task's own deletions land, in the same commit.
- **Fix:** `synthetic_nonzero_chip_id.py` -- deleted only the parenthetical `(planted_permit_by_default.py et al.)`, keeping the general "AST-scan-only planted fixtures beside it" claim (still true; several other planted_* fixtures remain). `test_sdp_db_invariant.py` -- deleted the whole closing sentence, since the mechanism it described (gate + fixture) is being removed in full, not partially.
- **Files modified:** `firestarter_app/tests/fixtures/synthetic_nonzero_chip_id.py`, `firestarter_app/tests/test_sdp_db_invariant.py`
- **Verification:** `ruff check`/`ruff format --check` clean on both; collected counts unchanged (4 and 9 respectively).
- **Committed in:** `0f251f0`

**3. [Rule 1 - Bug] Settled test_voltage_field_census.py's check_devtest_orchestrator.py entry, as 188-03's SUMMARY explicitly handed off**
- **Found during:** Task 2, cross-checking 188-03's SUMMARY note before deleting `tools/check_devtest_orchestrator.py`
- **Issue:** 188-03 removed the `test_check_dispatch_invariants.py` entry from `_FALSE_POSITIVE_CANDIDATE_NAMES` and its matching docstring clause, but explicitly left the `check_devtest_orchestrator.py` entry/clause "for 188-04" since that file wasn't yet deleted.
- **Fix:** Removed `"check_devtest_orchestrator.py"` from `_FALSE_POSITIVE_CANDIDATE_NAMES` and the docstring clause naming it ("`tools/check_devtest_orchestrator.py`'s wire-dict key set carries the same name;"), in the same commit that deletes the tool. Left `test_diff_db_gate.py`'s entry untouched, per 188-03's note that it's plan 188-05's to settle.
- **Files modified:** `firestarter_app/tests/test_voltage_field_census.py`
- **Verification:** `ruff check`/`ruff format --check` clean; `pytest tests/test_voltage_field_census.py -o addopts="" -q` -> 4 passed, unchanged.
- **Committed in:** `0f251f0`

### Reverted attempt (not a code deviation -- a corrected in-progress edit)

**4. Two render_shape/snapshot_report_shapes.py docstring mentions in test_blast_radius_invariance.py were edited, then reverted, before this file was committed**
- **What happened:** After trimming the two `render_shape`-consuming test functions (Task 1), an initial pass also edited the `_DB_DIFF_KEYS` pin's docstring and `_to_dict_with_db_diff`'s docstring to remove their own `render_shape` mentions, chasing the plan's literal "grep -c render_shape/snapshot_report_shapes == 0" acceptance criterion. That produced `added=2` in the file's numstat diff against the pinned base, violating the plan's own stricter, threat-model-backed invariant (T-188-13: "the numstat leg requires zero ADDED lines so the oracle cannot have been rewritten") and its explicit instruction to leave `_to_dict_with_db_diff` "exactly as they are."
- **Resolution:** Reverted both docstring edits (`git checkout HEAD -- tests/test_blast_radius_invariance.py`, then re-applied only the two clean function deletions). The file's diff is now genuinely deletions-only (`added=0`, `deleted=47`), and `_to_dict_with_db_diff` is byte-identical to its pre-plan state.
- **Consequence, logged rather than hidden:** the plan's own `grep -c -e render_shape -e snapshot_report_shapes tests/test_blast_radius_invariance.py -> 0` acceptance criterion is measured at **2**, not 0 (the two docstring mentions, both still accurate -- `render_shape` is not deleted until plan 188-05). Logged as WINDOWS.md deviation entry 7. **This is a deliberate, judged choice to satisfy the stronger invariant (do not touch the oracle beyond the two named sites) over the literal-but-conflicting zero-occurrence check**, not an oversight.
- **Verification:** `git diff --numstat <pinned base> -- tests/test_blast_radius_invariance.py` -> `added=0 deleted=47`; `git diff --numstat <pinned base> -- tests/fixtures/reports/` -> empty.

---

**Total deviations:** 3 auto-fixed (all Rule 1 -- stale references directly caused by this plan's own deletions, none in this plan's `files_modified`) + 1 reverted-and-logged conflict between two of the plan's own acceptance criteria.
**Impact on plan:** No scope creep -- all four are narrowly scoped to references this plan's own deletions orphaned. The one unresolved acceptance-criterion gap (2 residual `render_shape` prose hits) is a deliberate priority call favoring the stronger, explicitly-threat-mitigated invariant, logged in both this SUMMARY and `.planning/WINDOWS.md` for 188-09's verdict note and 188-05's own read_first (which will delete `render_shape` itself and can settle these two remaining mentions then).

## Issues Encountered

None beyond the deviations documented above. A background full-suite-plus-ruff pytest run started early in Task 1 (before that task's edits were staged) completed independently with `2262 passed, 1 warning` and both ruff legs clean -- consistent with, and corroborating, the explicit Task-1-boundary checks run afterward. A second, unrelated `pytest` process (started by a different actor in this shared devcontainer, running with `--ignore=tests/test_skip_census.py`) was observed but never touched by this plan's work and is unrelated to it.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter_app/tools/` now holds exactly 6 scripts (`build_db.py`, `catalog/codegen.py`, `gen_sdp_bus_config.py`, `gen_validation_header.py`, `parse_devtest_issue.py`, `gen_test_image.py`) plus `catalog/` support files and `baseline/dispatch_baseline.json` -- zero `check_*.py` gates remain. Plan 188-05 (the six GSD-process tools, `diff_db.py`'s relocation, and the frame-vector apparatus including `render_shape`) is unaffected by anything in this plan beyond the two now-live prose mentions of `render_shape` it should confirm settling.
- WR-01 (snapshot-drift coverage over 19 shape ids) is dead with no replacement, as decided by D-01/D-04/D-23 -- named here and in `.planning/WINDOWS.md` (entry 6) for plan 188-09's verdict note.
- `tests/test_lock_status_class_partition.py`'s surviving AST leg is now decorative -- named here and in `.planning/WINDOWS.md` (entry 8) as a second disclosed D-01 cost.
- This plan retired **eight** gates, not the nine the phase's ROADMAP line still predicts (188-03 took two, not one, under the D-25 replan) -- plan 188-09 should correct that line when it amends the phase section.
- `tools/baseline/dispatch_baseline.json` is now orphaned data (zero consumers) but stays, per D-14's scripts-only scope.
- `firestarter_app/CLAUDE.md`'s separate "Tooling gate (v1.8)" line now overstates mypy's CI enforcement (still local via pre-commit, no longer via `ci.yml`) -- left untouched per this plan's narrower "remove only the Regression guard sentences" instruction; flagged here for 188-09's verdict note or 188-07's provenance sweep.
- This plan is file-disjoint from 188-05/188-06/188-07/188-08's own primary scopes, aside from the three out-of-file-list stale-reference repairs documented above (all narrowly justified, all confirmed non-breaking).
- No blockers for the remaining phase-188 plans.

## Self-Check: PASSED

- `FOUND: 188-04-SUMMARY.md` -- `.planning/phases/188-the-tools-directory/188-04-SUMMARY.md` exists on disk.
- `git log --oneline --all` in `firestarter_app` shows both task commits present: `0f251f0` (Task 2, HEAD) with parent `a163dd9` (Task 1) with parent `7ebdef8` (188-03's Task 2, this plan's pinned base) -- confirmed via `git rev-parse HEAD`, `git rev-parse HEAD^`, `git rev-parse HEAD^^`.
- `git rev-list --count 7ebdef8..HEAD` in `firestarter_app` -> 2, matching `actuals.commits`.
- Both tasks' full `<verify>` legs re-run clean at final HEAD: whole-suite collect 2175 (0 errors), whole-suite pass 2175 (1 pre-existing warning), both ruff legs clean, D-10 closure test 1 passed standalone, zero `mypy` mentions in `ci.yml`, `Regression guard` count 0 / `hardware-damage path` count 1 in `CLAUDE.md`, 19 tracked snapshot files with an empty numstat diff against the pinned base.
- `git -C /workspaces status --porcelain .planning/config.json` -> empty at every check point (config.json never pruned during this plan's `gsd-tools` calls).
- `firestarter_app`'s `HEAD` is on branch `gsd/v1.37-operator-safety-answered-reports-claim-hygiene` (verified before the first commit and re-verified before the second); `git status --short` in `firestarter_app` shows only the pre-existing untracked operator datasheets (`datasheets/MBM27C1001.pdf`, `datasheets/MX27C4000.pdf`), nothing else.

---
*Phase: 188-the-tools-directory*
*Completed: 2026-09-13*
