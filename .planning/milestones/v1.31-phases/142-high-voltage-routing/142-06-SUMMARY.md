---
phase: 142-high-voltage-routing
plan: 06
subsystem: firmware
tags: [pytest, source-contract, gate, eprom, vpp, hv-routing, command_done, rurp_pinout, planted-red]

# Dependency graph
requires:
  - phase: 142-04
    provides: "the eprom.cpp rewrite this plan pins structurally -- eprom_hv_route_mask exposed in eprom.h as the single vpp_path-driven resolver called from at least two sites, the two conditional single-exit wrappers, the four EPROM_HV_ALL_OFF_MASK conversions, and the deletion of eprom_internal_ensure_regulator_enabled"
  - phase: 142-01
    provides: "the two EPROM_HV_* composites in include/rurp_pinout.h that this plan's include/-wide composite-count leg asserts are each defined exactly once"
  - phase: 142-05
    provides: "the behavioural half of VPP-03 (eprom_check_vpp and the write path emit the same physical control byte) -- this plan supplies the structural half"
provides:
  - "New firestarter/tests/test_hv_routing_source_contract_v142.py -- 16 pytest legs, two import-time env seams (FIRESTARTER_HV_SCAN_DISPATCH_SOURCE, FIRESTARTER_HV_SCAN_EPROM_SOURCE): D-09's owed command_done() source contract (exactly one definition; all three zeroing registers asserted individually inside a brace-matched body; both dispatch call arms asserted individually; the idle-command assignment) plus VPP-03's structural half (one resolver, >=2 calls, one static def each of the two inner bodies, the wrapper's conditional-disable shape, exactly one #define of each composite across include/, and three concatenation-built absence legs: no second algorithm-selector predicate, no hand-rolled regulator/drop OR sequence in either order, no return of the deleted dead regulator-enable guard helper) plus three self-protection legs (non-vacuous scan targets across all three targets including include/, cannot-be-silently-skipped, own-needles-absent-from-own-source)"
  - "Nine planted-RED transcripts (3 dispatcher zeroing-register plants, 2 dispatcher call-arm plants, 4 eprom.cpp structural plants), each captured failing on its own named assertion, never on an import/decode/path error, all run via the seam in a child process against a scratch copy, all reverted with zero production-file diff"
affects: [142-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Brace-depth body extraction (open-brace-to-matching-close on comment-stripped text) so a same-shaped call elsewhere in the file cannot satisfy a body-scoped assertion -- empirically proven, not merely asserted, by pairing one planted removal with an identical decoy call outside the target function and confirming the leg still fails for the removal, not the decoy"
    - "Paired-count-in-one-message assertion for a conditional-guard shape (an error-code comparison count and a shared-composite reference count asserted together, not as two independently-passable counts) so the SHAPE of a conditional wrapper is what is pinned, not two coincidental totals"
    - "Whitespace-tolerant regex built FROM a concatenation-built needle (split on literal spaces, escaped pieces joined by \\s*) so a self-check needle registration and its actual detection regex share one source of truth instead of two independently-typo-able strings"

key-files:
  created:
    - firestarter/tests/test_hv_routing_source_contract_v142.py
  modified: []

key-decisions:
  - "The include/-wide composite-count leg (Coverage 10) is left UNPLANTED, by decision, not oversight. Adding a third, glob-scoped env seam to reach it would contradict this module's own fixed two-seam contract (Task 1's acceptance criteria pin exactly FIRESTARTER_HV_SCAN_DISPATCH_SOURCE and FIRESTARTER_HV_SCAN_EPROM_SOURCE, 'both scan targets'), and the plan explicitly forbids planting it by editing the real include/rurp_pinout.h given the header's zero-headroom warning watermark. The other nine planted fixtures already exceed the plan's own numeric floor ('at least nine')."
  - "The two hand-rolled-OR-sequence absence needles cover BOTH operand orders (regulator-then-drop and drop-then-regulator) even though the removed code only ever wrote one order -- defensive against a future reintroduction that happens to write the operands in the other order, at the cost of one extra needle and one extra planted-RED case that was not strictly required to prove the mechanism (only the regulator-then-drop order was planted, matching the historical shape; the drop-then-regulator regex was exercised only by the module's own 16-leg green run, not by a dedicated plant)."
  - "The wrapper-conditional-shape leg (Coverage 5) asserts its error-gate count and its all-off-composite-reference count TOGETHER in one assert/message, per the plan's explicit instruction, rather than as two separate test functions -- so a reader sees both numbers and the requirement they jointly defend in a single failure, not two unrelated-looking counts."
  - "command_done's body is extracted by brace-depth counting rather than a fixed-line-count slice, and this was verified empirically rather than merely asserted: the CONTROL_REGISTER removal plant additionally inserted an identical decoy `rurp_write_to_register(CONTROL_REGISTER, 0x00)` call OUTSIDE command_done (inside op_reset_timeout) and the leg still failed on the missing in-body write -- proving a same-shaped call elsewhere in the file cannot satisfy this leg, not merely arguing it structurally by construction."
  - "Coverage 5, 8, 9 and 13 (the wrapper-conditional leg, the two static-body-definition legs, and the dead-helper-absence leg) were not planted in Task 3 -- the plan's own enumerated planted-violation list names exactly nine fixtures (3 zeroing registers + 2 call arms + 4 eprom.cpp structural legs: second resolver definition, one resolver call deleted, protocol-equality predicate reintroduced, hand-rolled OR sequence reintroduced), and those nine were run precisely as specified rather than extended with additional, unrequested plants."

patterns-established: []

requirements-completed: []  # Frontmatter requirements: [] is deliberate per <requirements_scope> -- plan 142-07 is the only plan authorized to flip VPP-01..04.

coverage:
  - id: D1
    description: "command_done()'s source contract (D-09's owed test, labelled a source-contract claim, not behavioural): exactly one definition; its body (extracted by brace-matching) zeroes CONTROL_REGISTER, LEAST_SIGNIFICANT_BYTE and MOST_SIGNIFICANT_BYTE, each asserted individually; both dispatch call arms (loop()'s timeout-abort branch and its if(finished) branch) asserted individually; and the body assigns the idle command to handle->cmd"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_hv_routing_source_contract_v142.py::test_command_done_is_defined_exactly_once tests/test_hv_routing_source_contract_v142.py::test_command_done_body_zeroes_all_three_latch_registers_individually tests/test_hv_routing_source_contract_v142.py::test_command_done_is_called_from_both_dispatch_arms_individually tests/test_hv_routing_source_contract_v142.py::test_command_done_sets_the_command_to_idle -o addopts=\"\" -q -- 4 passed"
        status: pass
      - kind: other
        ref: "3 planted violations (one per zeroing register, each removing that line from src/firestarter.cpp's command_done body in a scratch copy, driven via FIRESTARTER_HV_SCAN_DISPATCH_SOURCE in a child process) -- each RED on its own register-specific assertion ('found 0' for the removed register, others still 1). The CONTROL_REGISTER plant additionally added an identical decoy call OUTSIDE command_done and the leg still correctly failed on the in-body count, proving the brace-matched extraction excludes it."
        status: pass
      - kind: other
        ref: "2 planted violations (one per dispatch call arm, each removing that arm's command_done(&handle) call site from a scratch copy) -- each RED on its OWN arm-specific assertion (abort-arm plant failed at test_hv_routing_source_contract_v142.py:475's assert len(abort_arm_hits) >= 1; finished-arm plant failed at :482's assert len(finished_arm_hits) >= 1), never on the generic total-count assertion at :489."
        status: pass
    human_judgment: false
  - id: D2
    description: "VPP-03's structural half: exactly one route-resolver definition and >=2 call sites passing the handle; exactly one static definition each of the write-execute and write-init inner bodies; the write-path wrappers' disable gated on an error response code (paired with the composite-reference count in one assertion); exactly one #define of each of the two EPROM high-voltage composites across every header under include/, with the all-off composite's own #define line confirmed not to name the P1-routing bit (correction C-4); and three concatenation-built absence legs (no second algorithm-selector equality predicate, no hand-rolled regulator/drop OR sequence in either order, no return of the deleted dead regulator-enable guard helper, scanning both src/ and include/)"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_hv_routing_source_contract_v142.py -o addopts=\"\" -q -- 16 passed (includes all Coverage 5-13 legs)"
        status: pass
      - kind: other
        ref: "4 planted violations against a scratch copy of src/proms/eprom.cpp, each driven via FIRESTARTER_HV_SCAN_EPROM_SOURCE in a child process: (1) a second, duplicate eprom_hv_route_mask definition inserted -- RED, 'assert 2 == 1'; (2) the eprom_check_vpp call site deleted (replaced with a literal mask) -- RED, 'assert 1 >= 2'; (3) a `handle->protocol == 0x0B` predicate reintroduced into the resolver -- RED, matched the exact planted text verbatim; (4) a literal `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` sequence reintroduced into eprom_internal_erase -- RED, matched the exact planted text verbatim"
        status: pass
    human_judgment: false
  - id: D3
    description: "Three mandatory self-protection legs: every default scan target (both files AND the include/ directory) exists, is non-empty, resolves inside the repository, and (for the two files) has non-empty comment-stripped text; the module's own source contains no skip-bypass/skipif/import-or-skip construct; and none of the four concatenation-built needles (protocol-equality, both OR-sequence orders, the dead-helper identifier) appears verbatim anywhere in the module's own source"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_hv_routing_source_contract_v142.py::test_scan_targets_are_non_vacuous tests/test_hv_routing_source_contract_v142.py::test_this_module_cannot_be_silently_skipped tests/test_hv_routing_source_contract_v142.py::test_own_needles_do_not_appear_verbatim_in_this_module -o addopts=\"\" -q -- 3 passed"
        status: pass
      - kind: other
        ref: "python3 -c one-off sanity check confirming all four needle strings ('handle->protocol ==', both OR-sequence orderings, the dead-helper identifier) return False for containment in the module's own raw source text, independent of the pytest leg itself"
        status: pass
    human_judgment: false
  - id: D4
    description: "The full firmware pytest suite is green after the new module lands (256 -> 272, +16), both pinned native environments and native_loop_v131 are unmoved, no production file under src/ or include/ was touched by any of the nine planted-and-reverted runs, and both env seams are confirmed unset afterward"
    verification:
      - kind: unit
        ref: "cd firestarter && python3 -m pytest tests/ -o addopts=\"\" -q -- 272 passed (was 256 before this plan; run AFTER the commit per L-1, since the new untracked file trips test_flash_path_record_sync.py's whole-repo porcelain assertion beforehand)"
        status: pass
      - kind: unit
        ref: "pio test -e native -- 141 test cases: 141 succeeded, 17 suites (unmoved); pio test -e native_nodevtools -- 141 test cases: 141 succeeded, 17 suites (unmoved); pio test -e native_loop_v131 -- 71 test cases: 71 succeeded (unmoved, matching the 142-05 tip)"
        status: pass
      - kind: other
        ref: "After all nine planted-and-reverted runs: git diff --exit-code -- src/ include/ exits 0; git status --porcelain src/ include/ is empty; env | grep -c FIRESTARTER_HV_SCAN reports 0; the real (unseamed) module re-run is green (16/16)"
        status: pass
    human_judgment: false

duration: ~31min (approx -- start-of-session timestamp not explicitly captured; see Issues Encountered)
completed: 2026-08-12
status: complete
---

# Phase 142 Plan 06: High-Voltage Routing -- command_done() Source Contract + VPP-03 Structural Gate Summary

**New firestarter/tests/test_hv_routing_source_contract_v142.py (16 legs, two import-time env seams): D-09's owed command_done() source contract pinning all three zeroing registers and both dispatch call arms individually inside a brace-matched body, plus VPP-03's structural half (one resolver, one definition of each composite across include/, zero surviving hand-rolled equivalents) -- nine planted-RED transcripts, each failing on its own named assertion, all reverted with zero production-file diff.**

## Performance

- **Duration:** ~31 min (approx.)
- **Started:** ~2026-08-12T00:22Z (approximate -- see Issues Encountered)
- **Completed:** 2026-08-12T00:53:08Z
- **Tasks:** 3 (landed in one commit -- see Task Commits)
- **Files modified:** 1 (new, inside the `firestarter` submodule)

## Accomplishments

- Authored `tests/test_hv_routing_source_contract_v142.py` (806 lines, 16 `test_` functions) closing D-09's owed test and VPP-03's structural half with a mechanical, CI-visible oracle. Module docstring names `Requirements: VPP-02, VPP-03`, the two-part defect class it closes, a numbered `Coverage:` list matching the 16 test functions 1:1, an `Environment seams:` section naming both seams and stating they bind at import time, a naming note explaining why three legs are named after what they forbid rather than after the forbidden token, and an explicit L-12 statement that D-03's non-claim discipline is prose-enforced only this phase.
- **command_done() source contract (Coverage 1-4).** Labelled explicitly as a source-contract claim, not a behavioural one, with the reason recorded in the docstring: `src/firestarter.cpp` sits outside every native environment's `build_src_filter`, and pulling it in would collide with the suite's own `main()` and require a seventh native environment, forbidden by D-14. Body extraction uses brace-depth counting on the comment-stripped text (open-brace to matching close), so a same-shaped `rurp_write_to_register(..., 0x00)` call elsewhere in the file cannot satisfy the leg -- proven empirically, not just structurally, by pairing one planted removal with an identical decoy call outside the function (see Task 3). All three registers (`CONTROL_REGISTER`, `LEAST_SIGNIFICANT_BYTE`, `MOST_SIGNIFICANT_BYTE`) are asserted individually, both dispatch call arms (the timeout-abort branch and the `if (finished)` branch) are asserted individually and ordered BEFORE the generic total so a future single-arm deletion is attributed to the correct arm, and a separate leg confirms the body assigns the idle command to `handle->cmd`.
- **VPP-03 structural legs (Coverage 5-13).** One definition of `eprom_hv_route_mask` (returning `rurp_register_t`), at least two call sites passing `handle`; exactly one `static` definition each of `eprom_internal_write_execute_body` and `eprom_internal_write_init_body`; the two single-exit wrappers' conditional-disable shape pinned by asserting an error-response-code comparison count and an all-off-composite reference count TOGETHER in one message (4 and 6 respectively against the live tree); exactly one `#define` of each of `EPROM_HV_ROUTE_MASK` and `EPROM_HV_ALL_OFF_MASK` across every header under `include/`, plus confirmation that the all-off composite's own `#define` line does not name `CTRL_VPP_P1_ENABLE` (correction C-4); and three concatenation-built absence legs (zero `handle->protocol`-keyed equality predicates, zero literal regulator/drop-bit OR sequences in either operand order, zero occurrences anywhere in `src/` or `include/` of Open Question 6's deleted dead regulator-enable guard helper's identifier).
- **Three self-protection legs (Coverage 14-16).** Non-vacuous scan targets extended to cover all three roots this module reads (both files AND the `include/` directory, recomputed fresh from `_REPO_ROOT`, never through the env seams); the module cannot be silently skipped (no skip/skipif/import-or-skip construct, concatenation-built needles); and none of the four absence needles appears verbatim anywhere in the module's own source, confirmed both by the pytest leg itself and by an independent one-off `python3 -c` sanity check.
- **Task 3 -- nine planted-violation transcripts, every one RED on its own named assertion.** Three against a scratch copy of `src/firestarter.cpp` (one per zeroing register -- the `CONTROL_REGISTER` plant additionally carried a decoy identical call outside `command_done`, in `op_reset_timeout`, and the leg still correctly failed on the missing in-body write); two more against the same file (one per dispatch call arm, each failing on its own arm-specific assertion, not the generic total); and four against a scratch copy of `src/proms/eprom.cpp` (a second resolver definition; one resolver call site deleted; a `handle->protocol == 0x0B`-shaped predicate reintroduced; a literal `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` sequence reintroduced). Every plant used `FIRESTARTER_HV_SCAN_DISPATCH_SOURCE` or `FIRESTARTER_HV_SCAN_EPROM_SOURCE` pointed at a scratch copy under the session scratchpad, set on the command line of the `pytest` child process -- no production file was ever edited. After the last plant: both seams confirmed unset (`env | grep -c "FIRESTARTER_HV_SCAN"` == 0), `git diff --exit-code -- src/ include/` exits 0, and the real module re-ran green (16/16).
- **The include/-wide composite-count leg (Coverage 10) is recorded as UNPLANTED, by decision.** Reaching it with a planted duplicate `#define` would require either a third, glob-scoped env seam (contradicting this module's own fixed two-seam contract, which Task 1's acceptance criteria pin explicitly to the two file-scoped seams) or a transient edit to the real `include/rurp_pinout.h` (which the plan explicitly forbids, given the header's zero-headroom warning watermark). The other nine planted fixtures already exceed the plan's own "at least nine" floor.
- Committed the new module (`test(142-06):`), then ran the full pytest suite per L-1 (commit before running, since the new untracked file trips `test_flash_path_record_sync.py`'s whole-repo porcelain assertion): 256 -> 272 passed (+16). Confirmed both pinned native environments (141 cases / 17 suites each) and `native_loop_v131` (71 cases) unmoved.

## Task Commits

This plan's three tasks land in a **single** commit, matching the established precedent for this file shape (142-05): Task 1 authored the module and its command_done legs, Task 2 added the VPP-03 structural legs to the same new file, and Task 3's action text is the only place in the plan a commit instruction appears (after the planted-RED proofs). Since the file does not exist until Task 1 creates it and only Task 3 instructs a commit, splitting into three commits would have no natural boundary.

1. **Task 1 (command_done contract + seams + self-protection legs) + Task 2 (VPP-03 structural legs) + Task 3 (nine planted-RED proofs + commit)** - `2266536` (test, in the `firestarter` submodule, branch `gsd/v1.31-27c-programming-algorithm-fidelity`)

**Plan metadata:** committed separately in the meta repo (this SUMMARY + STATE.md + ROADMAP.md).

## Files Created/Modified

- `firestarter/tests/test_hv_routing_source_contract_v142.py` (new) - 16-leg source-contract gate: `command_done()`'s zeroing/call-arm/idle-assignment contract (Coverage 1-4), VPP-03's single-resolver/single-composite structure (Coverage 5-13), and three self-protection legs (Coverage 14-16)

## Decisions Made

See `key-decisions` in the frontmatter for the full list. Summarized:
- The include/-wide composite-count leg is left unplanted, by explicit decision documented both here and in the commit body, rather than adding a third env seam that would contradict the module's fixed two-seam contract.
- Both operand orders of the hand-rolled regulator/drop OR-sequence absence check are covered defensively, even though only one order matches the historically removed code's shape.
- The wrapper-conditional-shape leg pairs its two counts in one assertion/message, per the plan's explicit instruction, so the conditional SHAPE is what is pinned rather than two independently-passable totals.
- `command_done`'s body-extraction-by-brace-matching claim ("a write elsewhere in the file cannot satisfy this leg") was verified empirically with a paired decoy-plus-removal plant, not merely asserted by construction.

## Deviations from Plan

None (Rules 1-4) -- the plan executed exactly as written on the first implementation attempt. All 16 legs passed on first pytest run against the live tree; all nine required planted violations went RED on the first attempt against their intended assertion (no iteration needed to correct a wrong plant), except one authoring-time correction caught before any test run (see Issues Encountered).

## Issues Encountered

- **First draft of planted-violation E1 used a differently-named decoy function.** While constructing the "second resolver definition" plant, the first attempt named the duplicate function `eprom_hv_route_mask_decoy_second_definition` rather than reusing the exact identifier `eprom_hv_route_mask`. Since `test_route_resolver_is_defined_exactly_once`'s regex matches on the specific identifier, a differently-named decoy would not have tripped it. Caught before running the plant (by inspecting the generated fixture's `grep` output) and corrected to use the identical function name, producing the intended "found 2, not 1" failure. Not logged as a plan deviation since it was caught and corrected before any test was executed against it -- no incorrect result was ever observed or reported.
- **Start-of-session timestamp not explicitly captured**, the same issue 141-06-SUMMARY flagged for itself. The `record_start_time` execution-flow step's `date -u` command was not run before beginning file reads. The duration above is a reasonable approximation using `STATE.md`'s `last_updated` timestamp from the end of plan 142-05's own metadata commit (`2026-08-12T00:22:28.599Z`) as a start proxy against this plan's own completion timestamp (`2026-08-12T00:53:08Z`). Affects only this SUMMARY's own duration bookkeeping, not any committed code or test artifact.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 142-07 now has every piece of evidence VPP-02 and VPP-03 need from this plan: `command_done()`'s source-contract proof (D-09) and VPP-03's structural half (one resolver, one composite pair, no surviving hand-rolled equivalents) sit alongside plan 142-05's behavioural proofs. VPP-01's evidence (142-04/142-05) and VPP-04's evidence (142-03) were already complete entering this plan.
- No requirement was marked complete (`requirements: []` by design, per this plan's explicit scope boundary) -- `VPP-01`...`VPP-04` remain open for plan 142-07 to flip in one hand edit, per the 141-05/141-09 convention, after every piece of evidence exists.
- The L-12 caveat is now stated explicitly in this module's own docstring and commit body, not merely in the phase record: D-03's non-claim discipline is prose-enforced only on this branch, since CLOSE-01's `check_permitted_claims.py` is Phase 146's and Phase 139 shipped only a Phase-139-scoped script. A future reader of this module alone (without this SUMMARY open) still gets that caveat.
- Every pre-existing gate confirmed unmoved: `native`/`native_nodevtools` at 141/17 each, `native_loop_v131` at 71 cases, and the pytest suite green at 272 (was 256, +16 from this module only). The warning watermark (998/1166) and `size_baseline.json` were not re-measured by full rebuild in this plan -- unlike 142-01 through 142-05, this plan touched zero files under `src/` or `include/` (confirmed via `git diff --exit-code -- src/ include/` after every one of the nine planted-and-reverted runs and again after the real commit), so there is no mechanism by which either could have moved; a full `pio run`/`check_build_warnings.py --rebuild` pass was not run since this plan's own `<verification>` section does not name it and the zero-diff proof already covers the same ground. `native_trace_v131`'s expected-RED state (D-17) was likewise not re-run for the same reason -- it is unmoved by construction, not by fresh measurement in this plan's session.
- `firestarter/tests/test_write_path_source_contract_v131.py` and `firestarter/tests/test_protocol_branch_inventory.py` are confirmed byte-unchanged (`git diff --exit-code` on both exits 0) -- this plan added a wholly independent new module and touched neither analog.

---
*Phase: 142-high-voltage-routing*
*Completed: 2026-08-12*

## Self-Check: PASSED

- FOUND: firestarter/tests/test_hv_routing_source_contract_v142.py
- FOUND commit: 2266536 (firestarter submodule)
- Re-verified `python3 -m pytest tests/ -q -o addopts=""` = 272 passed in the firestarter submodule, `git status --porcelain` there is empty, and `git rev-parse --abbrev-ref HEAD` is `gsd/v1.31-27c-programming-algorithm-fidelity`, matching this document's claims.
