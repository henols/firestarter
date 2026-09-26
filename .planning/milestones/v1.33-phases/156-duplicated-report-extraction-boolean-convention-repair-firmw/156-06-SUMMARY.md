---
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "06"
subsystem: firmware
tags: [source-contract, gate, boolean-convention, dedup-04, pytest, non-vacuous]

requires:
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 05
    provides: "the flipped boolean convention this gate pins -- six op_execute_stateful_operation return sites, nine wrapper !-removals in src/eprom_operations.cpp, and the single surviving negation at the callback delegation. Commit 735aff5 is this plan's PRE_SHA and the real-tree GREEN anchor."
provides:
  - "tests/test_boolean_convention_source_contract_v133.py -- a standalone pytest module scanning src/eprom_operations.cpp and src/operation_utils.cpp: absence of the negated wrapper-return form, exactly-one surviving negated call in the engine (named as the callback delegation), exactly nine forwarding calls present, the two early-return refusal literals unchanged, four non-vacuity legs, a cannot-be-silently-skipped leg, and a self-match leg -- 7 tests total, all proven both RED (four distinct planted violations) and GREEN (the real committed tree at 735aff5)"
affects: [156-07]

tech-stack:
  added: []
  patterns:
    - "Plain substring count (not a \\b-wrapped identifier match) for a forbidden PREFIX needle: 'return !op_execute_' is a prefix of two larger identifiers and never a standalone word, so word-boundary regex would never fire against it and would pass vacuously forever. This is a new pattern this repo's other source-contract gates (which only ever absence-check COMPLETE identifiers) had not needed before."
    - "A single extended comment-AND-literal stripper (borrowed from test_protocol_branch_inventory.py) applied uniformly to both scan targets, adopted specifically because src/operation_utils.cpp (unlike the sibling gate's eprom.cpp/memory.cpp pair) contains character and string literals outside comments (the 'O'/'K'/'D'/'#' state-machine literals and PSTR(\"DONE\") in op_get_message) -- literal-safety by construction rather than by one-off inspection of each target."
    - "An 'exactly one, not zero' absence leg for a deliberately surviving negation, with the sole match's captured identifier asserted to be the expected one (`callback`) -- stronger than a bare count, catching both a wrongly-removed survivor (count 0) and a new stray negation elsewhere (count >1 or wrong identity)."

key-files:
  created:
    - firestarter/tests/test_boolean_convention_source_contract_v133.py
  modified: []

key-decisions:
  - "Did NOT reuse the sibling gate's `_assert_identifier_absent` (word-boundary-both-ends) for the wrapper's negated-return absence check. Verified analytically that a \\b-wrapped search for 'return !op_execute_' can never match the real violation text (`return !op_execute_stateful_operation(...)`), because 'op_execute_' is a PREFIX of a larger identifier and there is no word/non-word transition between 'op_execute_' and the 'stateful_operation'/'simple_operation' suffix that follows it in real source -- the check would pass vacuously forever regardless of whether the violation was present. Used a plain substring count instead, and confirmed empirically against a planted violation before committing (see Deviations)."
  - "Reused `_assert_identifier_absent` (word-boundary variant, copied in shape from the sibling gate) for exactly one leg where the boundary logic is actually valid: the 'own needles do not appear verbatim in this module' self-check, where a de-concatenation regression would surround the needle with quote characters (always non-word), making the boundary assertion correct there."
  - "Extended `_strip_comments` to also strip string/char literal contents (borrowed from test_protocol_branch_inventory.py's own stripper), applied uniformly to both scan targets, rather than keeping the sibling's comment-only stripper -- re-confirmed per the plan's own instruction that the sibling's 'no literal outside a comment or #include' justification does not carry over unchecked. src/eprom_operations.cpp was independently confirmed clean; src/operation_utils.cpp was NOT (op_get_message()'s 'O'/'K'/'D'/'#' char literals and its PSTR(\"DONE\") string literal), so the safer of the two prescribed remedies (extend the stripper) was taken for both targets uniformly rather than special-casing one file."
  - "The engine's 'exactly one negated call' leg additionally asserts the sole match's captured identifier equals `callback` (not just that the count is 1), strengthening the leg against a future edit that removes the callback negation while introducing an unrelated one elsewhere in the same function -- a scenario a bare count==1 assertion would miss."

requirements-completed: []

coverage:
  - id: D1
    description: "Wrapper absence leg: zero occurrences of the negated-call return form in the comment-and-literal-stripped src/eprom_operations.cpp"
    requirement: "DEDUP-04"
    verification:
      - kind: unit
        ref: "pytest tests/test_boolean_convention_source_contract_v133.py::test_wrapper_negated_return_is_absent"
        status: pass
    human_judgment: false
  - id: D2
    description: "Engine leg: exactly one surviving negated call in src/operation_utils.cpp, identified as the callback delegation -- Plan 05's honest nine-to-one reduction, asserted rather than forbidden"
    requirement: "DEDUP-04"
    verification:
      - kind: unit
        ref: "pytest tests/test_boolean_convention_source_contract_v133.py::test_engine_retains_exactly_one_negated_call"
        status: pass
    human_judgment: false
  - id: D3
    description: "Positive counterpart: exactly nine forwarding calls (stateful + simple) present in the wrapper file, closing the vacuity a deleted/truncated file would otherwise satisfy"
    requirement: "DEDUP-04"
    verification:
      - kind: unit
        ref: "pytest tests/test_boolean_convention_source_contract_v133.py::test_the_nine_forwarding_calls_are_present"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both early-return refusal literals (FLAG_CAN_ERASE, zero-chip-id) survive, asserted by function name and returned literal, never by line number"
    requirement: "DEDUP-04"
    verification:
      - kind: unit
        ref: "pytest tests/test_boolean_convention_source_contract_v133.py::test_the_two_early_return_refusal_literals_survive"
        status: pass
    human_judgment: false
  - id: D5
    description: "Four non-vacuity legs (both scan targets), the cannot-be-silently-skipped leg, and the own-needles-do-not-self-match leg"
    requirement: "DEDUP-04"
    verification:
      - kind: unit
        ref: "pytest tests/test_boolean_convention_source_contract_v133.py::test_scan_targets_are_non_vacuous, ::test_this_module_cannot_be_silently_skipped, ::test_own_needles_do_not_appear_verbatim_in_this_module"
        status: pass
    human_judgment: false
  - id: D6
    description: "The gate proven RED against four distinct planted violations (reintroduced negation, deleted forwarding call, emptied scan target, flipped early-return literal) in throwaway worktrees named `firestarter`, and GREEN against the real committed tree at 735aff5 -- both directions recorded in this SUMMARY with exact failure messages"
    requirement: "DEDUP-04"
    verification:
      - kind: other
        ref: "Manual planted-violation sweep in /tmp/probe156f/firestarter (git worktree add 735aff5), four violations each run individually and reverted with git checkout --, worktree removed and pruned afterward; see 'Non-Vacuity Evidence' section below for verbatim assertion messages"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-08-23
status: complete
---

# Phase 156 Plan 06: Boolean-Convention Source-Contract Gate Summary

**Added `tests/test_boolean_convention_source_contract_v133.py` -- a 7-leg, non-vacuous pytest source-contract gate pinning Plan 05's boolean-convention flip in `src/eprom_operations.cpp` (nine forwarding call sites, two untouched refusal literals) and `src/operation_utils.cpp` (exactly one deliberately-surviving negated call), proven RED against four distinct planted violations including an emptied scan target and GREEN against the real tree at `735aff5`.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-23T16:55:00Z
- **Tasks:** 2
- **Files modified:** 1 created, 0 modified

## Accomplishments

- Authored `tests/test_boolean_convention_source_contract_v133.py` following `tests/test_write_path_source_contract_v131.py`'s idiom: an import-time-bound environment seam (`FIRESTARTER_BOOLEAN_CONVENTION_SCAN_SOURCE`, overriding only the wrapper scan target -- the engine target is fixed, matching the sibling's own `memory.cpp` precedent), concatenation-built needles so the module never quotes its own forbidden token verbatim, and a docstring documenting Coverage, Environment seams, and CI framing in full.
- **Re-confirmed rather than copied** the sibling gate's literal-stripping justification: `src/eprom_operations.cpp` was independently confirmed to contain no string/char literal outside a comment or `#include`, but `src/operation_utils.cpp` was NOT clean -- `op_get_message()`'s serial message-framing parser contains four character literals (`'O'`, `'K'`, `'D'`, `'#'`) and one string literal (`PSTR("DONE")`) outside any comment. Extended `_strip_comments` to also strip literal contents (borrowed from `tests/test_protocol_branch_inventory.py`'s own stripper) and applied it uniformly to both scan targets, so literal-safety holds by construction.
- Implemented the wrapper absence leg as a **plain substring count**, not a word-boundary identifier match, after analytically confirming that `_assert_identifier_absent`'s `\b`-wrapped design (the sibling's own helper, which this module also copies and reuses correctly elsewhere) can never fire against the forbidden `return !op_execute_` prefix: that phrase is a prefix of a larger identifier (`op_execute_stateful_operation` / `op_execute_simple_operation`), so there is never a word/non-word transition immediately after it in real source, and a `\b`-wrapped search would pass vacuously forever regardless of whether the violation existed. This was the single most important design decision in this plan -- getting it wrong would have shipped a gate that could never go RED.
- Implemented `test_engine_retains_exactly_one_negated_call` to assert not just a count of 1 but that the sole surviving match's captured identifier is `callback` -- the MAIN-phase delegation Plan 05 deliberately left unflipped -- so a future edit that both removes the callback negation and introduces an unrelated one elsewhere would still be caught.
- Implemented `test_the_nine_forwarding_calls_are_present` (the positive counterpart to the absence leg, reading `_EXPECTED_FORWARD_TOTAL = 9` from a single named constant) and `test_the_two_early_return_refusal_literals_survive` (brace-matched function-body extraction, asserting on function name and returned literal, never on a line number).
- All 7 legs pass on the real tree: `python3 -m pytest tests/test_boolean_convention_source_contract_v133.py -v` -- 7 passed.
- Proved the gate can fail four distinct ways, each in a throwaway `git worktree add <PRE_SHA>` named `firestarter` at `/tmp/probe156f/firestarter`, reverting with `git checkout --` between violations and removing/pruning the worktree afterward. See "Non-Vacuity Evidence" below for the full table and verbatim messages.
- Ran the seam demonstration in a genuine child process (`FIRESTARTER_BOOLEAN_CONVENTION_SCAN_SOURCE=/tmp/does-not-exist-156-06.cpp python3 -m pytest ...`), confirming the docstring's import-time-binding claim: Coverage 1, 3 and 4 (the three legs that read the overridden path) failed loudly with `FileNotFoundError`, while Coverage 2, 5, 6 and 7 (documented as never reading the seam) were unaffected.
- Committed exactly one file (`git add tests/test_boolean_convention_source_contract_v133.py`, never `git add -A`), anchored `git rev-list --count 735aff5..HEAD == 1`.
- Post-commit: `python3 -m pytest tests/ -q` -- **355 passed, 0 failed** (348 from Plan 05's own post-commit baseline + this module's 7 new legs = 355 exactly). `pio test -e native` -- **172 test cases: 172 succeeded**, unchanged from before this plan.

## Non-Vacuity Evidence

All four violations were planted in the SAME throwaway worktree, `git worktree add /tmp/probe156f/firestarter 735aff5` (directory name `firestarter`, matching the project's own worktree-naming requirement so `test_scope_is_firmware_only` in `tests/test_checker_convention.py` does not fire spuriously). Each violation was reverted with `git checkout -- src/eprom_operations.cpp` before the next was planted. The worktree was removed (`git worktree remove --force`) and pruned (`git worktree prune`) after all four, and `git -C firestarter worktree list` was confirmed to show only the primary tree and the untouched `firestarter_py32_ci` sibling.

| # | Violation | Worktree path | Failing leg(s) | Assertion message (verbatim, trimmed) |
|---|---|---|---|---|
| 1 | Reintroduced the negation on `eprom_read`'s forwarding return (`return !op_execute_stateful_operation(_process_outgoing_data, handle);`) | `/tmp/probe156f/firestarter` | `test_wrapper_negated_return_is_absent`, `test_the_nine_forwarding_calls_are_present` | "found 1 occurrence(s) of the negated op-layer call form in the comment-and-literal-stripped src/eprom_operations.cpp -- Plan 05 removed the leading `!` from all nine eprom_* wrapper bodies; this construct must not return." AND "expected exactly 9 forwarding return sites (stateful + simple) in src/eprom_operations.cpp, found 8 (2 stateful, 6 simple)" |
| 2 | Deleted `eprom_read`'s entire `return op_execute_stateful_operation(...)` statement, leaving an empty function body | `/tmp/probe156f/firestarter` | `test_the_nine_forwarding_calls_are_present` (the absence leg PASSED vacuously) | "expected exactly 9 forwarding return sites (stateful + simple) in src/eprom_operations.cpp, found 8 (2 stateful, 6 simple) -- a deleted or truncated wrapper file would satisfy the absence leg above vacuously; this positive count is what catches that." `test_wrapper_negated_return_is_absent` passed (0 occurrences) -- the deletion satisfies the absence leg while the positive count leg correctly catches it. |
| 3 | Truncated `src/eprom_operations.cpp` to zero bytes (`: > src/eprom_operations.cpp`) | `/tmp/probe156f/firestarter` | `test_scan_targets_are_non_vacuous`, `test_the_nine_forwarding_calls_are_present`, `test_the_two_early_return_refusal_literals_survive` (the absence leg PASSED vacuously) | "default eprom_operations.cpp scan target ... is empty\nassert 0 > 0" AND "expected exactly 9 forwarding return sites ... found 0 (0 stateful, 0 simple)" AND "could not locate `bool eprom_erase(...) {` in the comment-and-literal-stripped scan target -- has this function been renamed or removed?" `test_wrapper_negated_return_is_absent` PASSED (0 occurrences in an empty file) -- **this is the exact vacuity shape the project has been bitten by before: the absence leg alone would have passed against a deleted/emptied file, and only the non-vacuity and positive-count legs caught it.** |
| 4 | Flipped `eprom_erase`'s `FLAG_CAN_ERASE` refusal literal from `return true;` to `return false;` | `/tmp/probe156f/firestarter` | `test_the_two_early_return_refusal_literals_survive` (only) | "expected eprom_erase() to contain exactly one `return true;` (the FLAG_CAN_ERASE refusal), found 0.\nGot:\n{ ... if (!is_flag_set(FLAG_CAN_ERASE)) { LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED); return false; } return op_execute_simple_operation(handle); }" |

**Seam demonstration (child process, proving the import-time-binding claim):**
```
FIRESTARTER_BOOLEAN_CONVENTION_SCAN_SOURCE=/tmp/does-not-exist-156-06.cpp python3 -m pytest tests/test_boolean_convention_source_contract_v133.py -v
```
Result: `3 failed, 4 passed`. The three that read `_SCAN_WRAPPERS` (`test_wrapper_negated_return_is_absent`, `test_the_nine_forwarding_calls_are_present`, `test_the_two_early_return_refusal_literals_survive`) each failed with `FileNotFoundError: [Errno 2] No such file or directory: '/tmp/does-not-exist-156-06.cpp'` raised from `Path.read_text()` inside the test body -- confirming the seam value was bound into `_SCAN_WRAPPERS` at IMPORT time (before any test ran) and that a nonexistent override fails loudly rather than silently passing. The four legs documented as never reading the seam (`test_engine_retains_exactly_one_negated_call`, `test_scan_targets_are_non_vacuous`, `test_this_module_cannot_be_silently_skipped`, `test_own_needles_do_not_appear_verbatim_in_this_module`) were unaffected, exactly as the docstring's "Environment seams" section states.

**GREEN control (the real, committed, unedited tree, not a synthetic derivative):**
```
$ git rev-parse HEAD
735aff5192427442c835a67f9049d51d10e7d56e   # before this plan's own commit
$ python3 -m pytest tests/test_boolean_convention_source_contract_v133.py -v
...
7 passed in 0.02s
```
Re-confirmed after this plan's own commit (`1151dc4`), with `git status --porcelain` empty both before and after.

## Task Commits

1. **Task 1 (author the gate) + Task 2 (prove RED, then commit) -- single commit, per the plan's own instruction that Task 1 authors but does not commit:** `1151dc4` (test) -- `tests/test_boolean_convention_source_contract_v133.py`, 1 file, 442 insertions, anchored `git rev-list --count 735aff5..HEAD == 1`.

**Plan metadata:** committed in the meta repo immediately after this SUMMARY (see the meta repo's own commit log).

## Files Created/Modified

- `firestarter/tests/test_boolean_convention_source_contract_v133.py` -- new, 7 test legs, 442 lines. No other file touched.

## Decisions Made

- Did not reuse `_assert_identifier_absent`'s word-boundary regex for the wrapper's negated-return absence check (analytically proven it could never match a real violation); used a plain substring count instead and verified this empirically against Violation 1 before committing.
- Reused `_assert_identifier_absent` correctly for exactly one leg (the own-needles self-check), where the boundary logic is valid because a de-concatenation regression would surround the needle with quote characters.
- Extended the comment-only stripper to also strip literal contents, applied uniformly to both scan targets, after confirming `src/operation_utils.cpp` (unlike the sibling gate's targets) contains literals outside comments.
- Strengthened the engine's "exactly one negated call" leg to also assert the captured identifier's name (`callback`), not just the count.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, caught before commit] The plan's own read_first instruction to reuse `_assert_identifier_absent` for the wrapper absence leg would have shipped a vacuous check**
- **Found during:** Task 1, while designing the wrapper absence leg.
- **Issue:** The plan's action text (156-06-PLAN.md, task 1 action (d)) instructs: "Copy `_assert_identifier_absent` ... Apply it to the wrapper file." That helper wraps its needle in `\b...\b` on both sides. Analysis showed that for the forbidden needle `return !op_execute_` (a PREFIX of `op_execute_stateful_operation` / `op_execute_simple_operation`, never a standalone word), the trailing `\b` can never be satisfied against real source text, because "op_execute_" is immediately followed by more identifier characters ("stateful_operation" / "simple_operation") with no word/non-word transition. A literal reuse of this helper for this specific needle would have produced a leg that reported "0 occurrences" unconditionally, whether or not the violation was present -- exactly the vacuous-gate defect class this whole plan exists to prevent (T-156-39/40 in this plan's own threat register).
- **Fix:** Implemented the wrapper absence leg as a plain substring count (`stripped.count(_NEEDLE_INVERTED_CALL)`) instead, with the design rationale documented in both the module docstring and the leg's own docstring. Verified empirically: planted Violation 1 (reintroducing the negation) and confirmed the leg correctly went RED (`found 1 occurrence(s)`) before ever committing the module.
- **Files modified:** `firestarter/tests/test_boolean_convention_source_contract_v133.py` (authored with the corrected design from the start -- no rework was needed after the analysis, since this was caught during authoring rather than after a first, broken attempt).
- **Verification:** Task 2's full four-violation sweep, all recorded above; Violation 1 specifically proves this leg fires correctly.
- **Committed in:** `1151dc4` (the module's only commit).

---

**Total deviations:** 1 auto-fixed (Rule 1 -- a design-time bug catch, not a runtime code defect; no rework needed since it was caught before authoring the flawed version).
**Impact on plan:** None on scope or schedule. This is exactly the kind of defect the plan's own non-vacuity requirement exists to force out during authoring rather than after a false-green ships.

## Issues Encountered

None beyond the design-time catch documented above, resolved before any commit.

## User Setup Required

None -- no external service configuration required. This plan adds one firmware test file only.

## Next Phase Readiness

- `firestarter` is now at `1151dc4` on `gsd/v1.33-source-hygiene-firmware-size-reduction`, tree clean (`git -C firestarter status --porcelain` empty), `git -C firestarter worktree list` shows only the primary tree and the untouched `firestarter_py32_ci` sibling.
- The nine wrapper call sites now have the one mechanical check their translation unit permits: a non-vacuous source contract, proven RED four distinct ways (including the exact emptied-target vacuity shape this project has been bitten by before) and GREEN against the real tree.
- `python3 -m pytest tests/ -q`: 355 passed, 0 failed (348 baseline + 7 new legs, exact accounting -- no other test count moved). `pio test -e native`: 172/172, unchanged.
- No DEDUP-0X requirement was marked Complete in `.planning/REQUIREMENTS.md` -- Plan 07 is the landing plan that closes them, per this plan's explicit instructions. This plan's contribution: DEDUP-04's optional mechanical gate, closing RESEARCH open question 4 and the VALIDATION Wave 0 optional high-value item.
- Plan 07 has this plan's full evidence record available: the module's exact leg names, the four planted-violation results, the seam demonstration, and the corrected pytest total (355, up from 348) for its own `.planning/v1.33/156-after-figures.md`.

---
*Phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw*
*Completed: 2026-08-23*

## Self-Check: PASSED

- `.planning/phases/156-duplicated-report-extraction-boolean-convention-repair-firmw/156-06-SUMMARY.md` exists on disk -- FOUND
- `firestarter` commit `1151dc4` (test(156-06): pin the boolean convention with a non-vacuous source contract) exists in `git -C firestarter log --oneline --all` -- FOUND
- `firestarter/tests/test_boolean_convention_source_contract_v133.py` exists on disk -- FOUND
- `git -C firestarter worktree list` shows exactly two entries (`/workspaces/firestarter`, `/workspaces/firestarter_py32_ci`) -- FOUND, matches pre-plan state

No missing items.
