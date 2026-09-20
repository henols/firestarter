---
phase: 202-one-comparison-engine-on-the-host
plan: 05
subsystem: verification
tags: [python, click, mypy, streaming-compare, eprom, cli]

# Dependency graph
requires:
  - phase: 202-01
    provides: "`firestarter/compare.py`'s streaming engine, `verify_eprom` rewritten onto `COMMAND_READ` with the D-10 exit-code contract (0/1/2), and the WINDOWS.md id-1 deviation (verify's provisional read-bounding) this plan reconciles"
  - phase: 202-04
    provides: "`_main_phase_read_data`'s additive `abort_predicate` seam and the D-08 abort-vs-fault discrimination this plan's shared drive reuses for `check_eprom_blank`"
provides:
  - "`EpromOperator._drive_region_compare`: the one shared compare drive `verify_eprom` and `check_eprom_blank` both call -- accumulator, abort predicate, D-08 discrimination, D-13/D-14 rendering, D-10 int verdict, all in exactly one place"
  - "`check_eprom_blank` rewritten onto `COMMAND_READ`: returns int (0 blank / 1 not blank / 2 refusal), compares against a constant blank byte via the module-level `_blank_expected_bytes` D-04 pull callback, and the SRAM/FRAM short-circuit now refuses (2) instead of returning a false `False` (D-12)"
  - "`verify` CLI gains `-s/--size`; `blank` CLI gains `-a/--address`, `-s/--size`, `--full` -- spelled exactly as `read` spells them (CMP-08)"
  - "`cli_handlers._region_refusal_exit_code`: D-17's region resolution and its two pre-wire refusals (an explicit size shorter than verify's input file; a region running past the chip's declared size), fired before either command opens the serial port"
  - "`verify_eprom` gains a `size_str` parameter, an explicit size winning over the input-file-length default (closes WINDOWS.md id 1)"
  - "A wire-level proof (`TestOrdinalsNeverSentByVerifyOrBlank`) that no command dict composed by any of a clean/mismatching verify or a clean/non-blank blank ever carries ordinal 4 or 6 (CMP-01, CMP-02, phase success criterion 1)"
  - "An exit-code matrix proving 0/1/2 for both commands with two distinct routes to 2 each, each distinguished from a Click usage error by its own message (CMP-07)"
  - "`consistency_check_eprom`'s docstring repaired: no longer claims to be the only `EpromOperator` method returning int"
affects: [203, 204, 205, 206]

# Actuals (#2632)
actuals:
  tokens: 23094
  tasks: 3
  commits: 7
  plan_head_before: "app b210dea / meta 45f4250b"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One shared compare drive for two callers: `_drive_region_compare` takes the D-04 pull callback plus `full`/`region_length` flags, so `verify_eprom` and `check_eprom_blank` differ only in what they compare against (a file vs. a constant), never in how the compare, abort, discrimination or rendering work."
    - "Pre-wire region refusals live in the CLI tier, not the service layer: `_operation_context` is what opens the serial port, so a refusal that must fire before the port opens cannot live downstream of it -- `cli_handlers._region_refusal_exit_code` decides before either command ever calls into `EpromOperator`."
    - "A malformed --address/--size string is deliberately NOT re-validated by the new refusal helper -- it returns 'no refusal decided' and lets `_setup_operation`'s own `parse_address`/`parse_size` `ValueError` handling (pre-existing, also pre-wire, also exit 2) run instead, so there is exactly one place that validates the string."

key-files:
  modified:
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_eprom_operations.py
    - firestarter_app/tests/test_cli_handlers.py
    - firestarter_app/tests/test_erase_blank_step_nonregression.py
    - firestarter_app/tests/test_write_response_budget.py
    - firestarter_app/tests/fake_chip.py
    - firestarter_app/tests/plan_corpus.py
    - firestarter_app/tests/fixtures/report_shapes.py
    - firestarter_app/tests/test_chip_test_cycle.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py
    - firestarter_app/tests/test_chip_test_timing.py
    - firestarter_app/tests/test_chip_test_uv_slot_write.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_devtest_firmware_error_propagation.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
    - .planning/WINDOWS.md

key-decisions:
  - "One shared drive (`_drive_region_compare`), not two parallel copies -- D-02's single-implementation rule, applied one layer up from `classify_fingerprint`."
  - "D-17's region resolution and both refusals live in the CLI tier (`cli_handlers.py`), never in `EpromOperator` -- the port-opening boundary is `_operation_context`, and the refusal must fire before it."
  - "A malformed --address/--size string is left to the existing `_setup_operation`/`parse_*` `ValueError` path rather than re-validated by the new refusal helper -- one validator, not two with potentially different error text."
  - "`_blank_expected_bytes` is a module-level function, not a closure inside `check_eprom_blank`, so the D-04 per-chunk allocation bound is directly unit-testable."
  - "WINDOWS.md id 1 (202-01's provisional verify read-bounding) is marked `fixed`, not left open -- this plan's real `-s/--size` on `verify_eprom` is exactly the reconciliation it was filed for."

requirements-completed: [CMP-01, CMP-02, CMP-07, CMP-08]

coverage:
  - id: D1
    description: "check_eprom_blank reads the chip with COMMAND_READ (never COMMAND_BLANK_CHECK) and compares on the host through the same engine verify_eprom uses, exiting 0/1/2 per D-10/D-12"
    requirement: "CMP-02"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestCheckEpromBlankHostSideRead::test_no_composed_command_dict_carries_the_blank_check_ordinal"
        status: pass
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestCheckEpromBlankHostSideRead::test_all_blank_chip_returns_zero"
        status: pass
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestCheckEpromBlankHostSideRead::test_one_non_blank_byte_returns_one"
        status: pass
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestCheckEpromBlankHostSideRead::test_setup_failure_returns_two"
        status: pass
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestSramBlankCheckShortCircuit::test_sram_blank_check_short_circuits_before_setup"
        status: pass
    human_judgment: false
  - id: D2
    description: "verify_eprom and check_eprom_blank share one compare drive rather than two copies of the accumulator loop"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestCheckEpromBlankSharesTheOneCompareDrive::test_both_methods_call_the_shared_drive_helper"
        status: pass
    human_judgment: false
  - id: D3
    description: "The blank-check pull callback allocates at most the requested chunk length per call, never a device-sized buffer"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestBlankExpectedBytesPullCallback::test_allocates_exactly_the_requested_length"
        status: pass
    human_judgment: false
  - id: D4
    description: "verify and blank accept -a/--address and -s/--size spelled exactly as read spells them, and a region-scoped comparison reads and compares only that region"
    requirement: "CMP-08"
    verification:
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_region_scoped_verify_composes_a_command_dict_bounding_exact_region"
        status: pass
      - kind: other
        ref: "firestarter verify --help / firestarter blank --help (option spellings) -- see __snapshots__/test_characterization.ambr"
        status: pass
    human_judgment: false
  - id: D5
    description: "An explicit size wins; without it verify's region is the input file's length and blank's is the whole chip; a short input file and an over-long region are both refused before the port opens"
    requirement: "CMP-08"
    verification:
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_verify_refuses_size_larger_than_input_file_before_opening_the_port"
        status: pass
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_region_past_chip_end_is_refused_before_opening_the_port"
        status: pass
    human_judgment: false
  - id: D6
    description: "verify and blank exit 0/1/2 with two distinct routes to 2 per command, each distinguishable from a Click usage error by its message"
    requirement: "CMP-07"
    verification:
      - kind: unit
        ref: "tests/test_cli_handlers.py (test_verify_happy_path, test_verify_operator_returns_mismatch, test_verify_operator_returns_setup_failure, test_blank_happy_path, test_blank_operator_returns_mismatch, test_blank_operator_returns_setup_failure, test_service_setup_failure_route_to_exit_2_names_its_own_message, test_usage_error_also_exits_2_but_never_reaches_the_operator, test_map_typed_errors_still_exits_one_for_a_third_command)"
        status: pass
    human_judgment: false
  - id: D7
    description: "No command dict composed by a verify or a blank run carries ordinal 4 or 6, against firmware that still implements both"
    requirement: "CMP-01"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#TestOrdinalsNeverSentByVerifyOrBlank::test_no_run_composes_either_retired_ordinal"
        status: pass
    human_judgment: false
  - id: D8
    description: "consistency_check_eprom's docstring no longer claims to be the only EpromOperator method returning an int"
    verification:
      - kind: other
        ref: "python -c \"...assert 'ONLY' not in d and 'only EpromOperator method' not in d...\""
        status: pass
    human_judgment: false

duration: ~140min
completed: 2026-09-20
status: complete
---

# Phase 202 Plan 05: Blank Joins the Engine, Region Options, Exit-Code Closure Summary

**`firestarter blank` now reads the chip and compares against a constant blank byte through the same host-side engine `verify` uses; both commands gained `-a`/`-s`/`--full` region options with D-17's pre-wire refusals, and a wire-level test proves neither retired firmware ordinal is ever sent.**

## Performance

- **Duration:** ~140 min
- **Completed:** 2026-09-20
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 19 in `firestarter_app` (0 created), plus 4 in the meta repo `.planning/`; across 3 app commits + 4 meta commits (3 gitlink advances + this metadata commit)

## Accomplishments

- `EpromOperator._drive_region_compare` extracted: the one compare drive (accumulator, abort predicate, D-08 discrimination, D-13/D-14 rendering, D-10 verdict) both `verify_eprom` and `check_eprom_blank` call, rather than each carrying its own copy (D-02).
- `check_eprom_blank` rewritten onto `COMMAND_READ`: compares chunk by chunk against a constant `0xFF` supplied by the module-level `_blank_expected_bytes` D-04 pull callback (never a device-sized buffer), returns an int (0 blank / 1 not blank / 2 refusal), and the SRAM/FRAM pre-wire short-circuit now returns 2 -- an honest refusal -- in place of the old false `False` "not blank" verdict (D-12). `dev test`'s `OP_BLANK_CHECK` dispatch adapts with a `== 0` comparison, the same shape 202-01 gave `verify_eprom`.
- `verify` CLI gained `-s/--size`; `blank` CLI gained `-a/--address`, `-s/--size` and `--full` -- spelled exactly as `read` spells them (CMP-08). `verify_eprom` itself gained a `size_str` parameter so an explicit CLI size wins over its file-length default.
- `cli_handlers._region_refusal_exit_code`: D-17's region resolution and its two pre-wire refusals (an explicit `--size` shorter than `verify`'s input file; a start+size region running past the chip's declared size for either command) fire in the CLI tier, before either command calls into `EpromOperator` -- `_operation_context` is what opens the serial port, and the refusal must fire before that. `map_typed_errors` is untouched, byte-identical (D-11).
- `TestOrdinalsNeverSentByVerifyOrBlank` drives a clean verify, a mismatching verify, a clean blank and a non-blank blank end to end, collecting every composed command dict into one list and asserting none carries ordinal 4 (`COMMAND_BLANK_CHECK`) or 6 (`COMMAND_VERIFY`) and every one carries ordinal 1 (`COMMAND_READ`) -- CMP-01, CMP-02, phase success criterion 1. The write recorder independently confirms no raw frame on the wire carries either ordinal's JSON encoding.
- The CLI exit-code matrix is proven for both commands across 0/1/2, with two distinct routes to 2 per command (a real service-layer setup failure, driven through a genuine `EpromOperator` and asserted via `caplog`; and a CLI-tier region refusal, asserted via `result.output`), each distinguished from a Click `UsageError` (which also exits 2, D-10's accepted cost) by its own message rather than by exit code alone.
- `consistency_check_eprom`'s docstring repaired: no longer claims to be the only `EpromOperator` method returning int -- names `verify_eprom` and `check_eprom_blank` as sharing the same D-10 convention now.
- WINDOWS.md id 1 (202-01's provisional verify read-bounding, filed for this plan to reconcile) is closed: `verify_eprom`'s real `size_str` parameter is the reconciliation, and the ledger entry is marked `fixed`.
- All eight CMP requirements (CMP-01 through CMP-08) are now `Complete` in REQUIREMENTS.md.

## Task Commits

1. **Task 1: `blank` joins the one engine** -- app `92f9cbe`, meta `2ff49d6c`
2. **Task 2: Region options, and refusals that fire before the port opens** -- app `ee0743c`, meta `c541ef07`
3. **Task 3: Prove the ordinals are never sent, prove the exit-code matrix, repair the stale claim** -- app `2e40650`, meta `6af0ba09`

**Plan metadata:** *(this commit, immediately following)*

## Files Created/Modified

- `firestarter_app/firestarter/eprom_operations.py` -- `_drive_region_compare` extracted; `verify_eprom` rewritten onto it, gains `size_str`; `check_eprom_blank` rewritten onto `COMMAND_READ`/the shared drive, gains `address_str`/`size_str`/`full`, D-12 refusal; module-level `_blank_expected_bytes`; `consistency_check_eprom` docstring repaired; unused `COMMAND_BLANK_CHECK` import dropped
- `firestarter_app/firestarter/cli_handlers.py` -- `_region_refusal_exit_code` (D-17); `verify` gains `-s/--size`; `blank` gains `-a/--address`, `-s/--size`, `--full`; both docstrings name all three exit codes; both `sys.exit` on the service's int verdict directly
- `firestarter_app/firestarter/chip_test.py` -- `OP_BLANK_CHECK` dispatch arm's `== 0` adapter over `check_eprom_blank`'s new int return
- `firestarter_app/tests/test_eprom_operations.py` -- new `TestCheckEpromBlankHostSideRead` (4 tests), `TestCheckEpromBlankSharesTheOneCompareDrive`, `TestBlankExpectedBytesPullCallback`, `TestOrdinalsNeverSentByVerifyOrBlank`; `TestSramBlankCheckShortCircuit` updated for the D-12 return-value change
- `firestarter_app/tests/test_cli_handlers.py` -- `blank` exit-code tests updated to the int contract; new region-refusal tests, region-scoped wire-shape test, `map_typed_errors` source/behavioural tests, exit-code-matrix tests
- `firestarter_app/tests/test_erase_blank_step_nonregression.py` -- `blank` CLI tests updated to the int contract
- `firestarter_app/tests/test_write_response_budget.py` -- new `_drive_blank_check_and_record_timeouts` driver (blank moved off the `_main_phase_simple` group onto the read-pull shape); D-12's negative proof re-driven for blank
- `firestarter_app/tests/fake_chip.py`, `plan_corpus.py`, `fixtures/report_shapes.py`, `test_chip_test.py`, `test_chip_test_cycle.py`, `test_chip_test_sdp_leg.py`, `test_chip_test_timing.py`, `test_chip_test_uv_slot_write.py`, `test_dev_test_cmd.py`, `test_devtest_firmware_error_propagation.py`, `test_diagnostic_report.py` -- every hand-rolled `check_eprom_blank` mock/fake adapted from bool to the 0 (blank) / 1 (not blank) convention
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` -- `verify --help` / `blank --help` snapshots regenerated
- `.planning/REQUIREMENTS.md` -- CMP-01, CMP-02, CMP-07, CMP-08 marked Complete (checklist + traceability table); all eight CMP ids now Complete
- `.planning/ROADMAP.md` -- 202-05 checkbox flipped; Phase 202 marked 5/5 plans complete
- `.planning/STATE.md` -- Current Position, Session, Decisions, Performance Metrics updated for Phase 202's close (hand-edited; `state.advance-plan` failed cleanly on an unlabelled `## Current Position` block rather than corrupting anything, per its own error contract)
- `.planning/WINDOWS.md` -- id 1 marked `fixed`

## Decisions Made

See `key-decisions` in frontmatter. In short: one shared compare drive rather than two; both D-17 refusals live in the CLI tier because that is the layer with a chance to run before the port opens; a malformed address/size string is left to the pre-existing `_setup_operation` validator rather than re-validated; the blank pull callback is module-level so it is directly unit-testable; WINDOWS.md id 1 is closed, not left open.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `check_eprom_blank`'s return-type migration (bool -> int) broke every hand-rolled mock/fake feeding it, far beyond the plan's own named test file**

- **Found during:** Task 1's own `<verify>` command (the targeted test run the plan's text specifies), which surfaced failures the moment `chip_test.py`'s `OP_BLANK_CHECK` dispatch arm started comparing the return value against `0`.
- **Issue:** `chip_test.py`'s `_dispatch_op` is the ONE production call site for `check_eprom_blank`, but (mirroring 202-01's identical experience with `verify_eprom`) it backs every hand-rolled `check_eprom_blank` mock across the `dev test`/`run_plan` fixture ecosystem -- 10 test files beyond the plan's named `test_chip_test.py`: `fake_chip.py` (the real `FakeChip`/`WriteInitPreflightChip` classes, not a `Mock`), `plan_corpus.py`, `fixtures/report_shapes.py`, `test_chip_test_cycle.py`, `test_chip_test_sdp_leg.py`, `test_chip_test_timing.py`, `test_chip_test_uv_slot_write.py`, `test_dev_test_cmd.py`, `test_devtest_firmware_error_propagation.py`, `test_diagnostic_report.py`. Every one fed the dispatch's new `== 0` comparison a bare `True`/`False`, which -- exactly as 202-01's SUMMARY warned for the sibling method -- silently INVERTS under the new convention: `False == 0` reads `True` (blank), `True == 0` reads `False` (not blank). Left unfixed, this would have been a correctness regression far worse than a test failure: a real `dev test` run would report the opposite blank-check verdict.
- **Fix:** Adjusted every `check_eprom_blank` mock/fake to the 0 (blank) / 1 (not blank) convention, including the two real `FakeChip`/`WriteInitPreflightChip` class methods (not just `Mock` configs), leaving every other method's bool contract (`write_eprom`, `erase_eprom`, `sdp_lock`, `sdp_unlock`) untouched -- that migration is phase 206's job per CONTEXT.md.
- **Files modified:** listed above under "Files Created/Modified".
- **Verification:** full suite green (2211 tests, up from 2190 before this plan); the two new regression tests added to `test_chip_test.py` (`test_blank_check_step_records_pass_verdict_when_operator_returns_zero`, `test_blank_check_step_records_bad_verdict_when_operator_returns_one`) pin the dispatch adapter directly.
- **Committed in:** `92f9cbe` (Task 1).

**2. [Rule 1 - Bug] `test_write_response_budget.py`'s D-12 blank-check timeout proof drove the wrong wire shape for the new `check_eprom_blank`**

- **Found during:** Task 1's full-suite verify.
- **Issue:** This pre-existing test fed `check_eprom_blank` the OLD payload-free `_main_phase_simple` frame script (`[MSG_INIT_DONE, MSG_MAIN_DONE, MSG_END_DONE]`, no `MSG_DATA_CHUNK`), which the new `COMMAND_READ`-based `check_eprom_blank` never receives that way any more -- the driven blank-check saw zero compared bytes against the whole chip's declared size and returned a mismatch/incomplete verdict (1) instead of a match, failing the test's `is True` assertion.
- **Fix:** Added a dedicated `_drive_blank_check_and_record_timeouts` driver (mirroring the existing verify driver's shape): feeds one `MSG_DATA_CHUNK` of all-`0xFF` bytes bounded by an explicit `size_str`, so the driven blank-check is genuinely blank (`ok == 0`). Corrected the module's own docstring claim that `check_eprom_blank`/`erase_eprom` both "fall through to `_main_phase_simple`" -- only `erase_eprom` still does.
- **Files modified:** `tests/test_write_response_budget.py`.
- **Verification:** `pytest tests/test_write_response_budget.py` -- 6/6 passed.
- **Committed in:** `92f9cbe` (Task 1).

**3. [Rule 3 - Blocking] Unused `COMMAND_BLANK_CHECK` import after `check_eprom_blank`'s rewrite**

- **Found during:** Task 2's `ruff check` run.
- **Issue:** `check_eprom_blank` no longer references `COMMAND_BLANK_CHECK` as a Python name (only in comments/docstrings), so `ruff`'s `F401` flagged the import as dead.
- **Fix:** Dropped the import. The constant itself is untouched and still reachable through `COMMAND_NAMES` -- only the now-unused import binding in `eprom_operations.py` was removed.
- **Files modified:** `firestarter_app/firestarter/eprom_operations.py`.
- **Verification:** `ruff check firestarter/ tests/` clean; `python -c "from firestarter.constants import COMMAND_NAMES, COMMAND_BLANK_CHECK; assert COMMAND_NAMES[COMMAND_BLANK_CHECK]"` still passes.
- **Committed in:** `ee0743c` (Task 2).

**4. [Rule 1 - Bug] `blank`'s CLI tests (both in `test_cli_handlers.py` and `test_erase_blank_step_nonregression.py`) used bool return values, now incompatible with `blank`'s new `sys.exit(verdict)` shape**

- **Found during:** Task 2's own `<verify>` run against `test_cli_handlers.py` (not yet updated at that point) and the broader full-suite check.
- **Issue:** Once `cli_handlers.blank` calls `sys.exit(verdict)` directly on the service's int return (matching `verify`'s existing shape) instead of `sys.exit(0 if ok else 1)`, a `Mock`-configured `check_eprom_blank.return_value = True` becomes `sys.exit(True)`, which Click/Python resolve to exit code `1` (`int(True) == 1`) rather than the test's expected `0` -- and `return_value = False` resolves to exit `0` rather than the expected `1`. Both pre-existing tests were exercising the CLI's OLD `0 if ok else 1` wrapping and needed updating to the new int-verdict convention.
- **Fix:** Updated `test_blank_happy_path`/`test_blank_operator_returns_false` (renamed to `test_blank_operator_returns_mismatch`) to use `0`/`1`, and added `test_blank_operator_returns_setup_failure` (exit 2) to match `verify`'s existing three-test shape. Updated `test_erase_blank_step_nonregression.py`'s two `blank`-driving tests identically.
- **Files modified:** `tests/test_cli_handlers.py`, `tests/test_erase_blank_step_nonregression.py`.
- **Verification:** both files green; full suite green.
- **Committed in:** `ee0743c` (Task 2).

---

**Total deviations:** 4 auto-fixed (2 Rule 3, 2 Rule 1). None were scope creep: deviation 1 was necessary to avoid shipping an inverted blank-check verdict (a correctness regression, not merely a test failure), and the other three were direct, unavoidable consequences of the return-type/CLI-wiring changes this plan's own tasks specify.
**Impact on plan:** All four were required for the suite to reflect reality and for the shipped behavior to be correct. No unrequested functionality was added.

## Issues Encountered

None beyond what is documented above under Deviations.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Phase 202 is now fully complete: all 5 plans summarized, all 8 CMP requirements (CMP-01 through CMP-08) `Complete` in REQUIREMENTS.md, ROADMAP.md's Phase 202 block shows 5/5 plans and all five success criteria are met (criterion 1 proven for both commands now; criteria 2-5 were already closed by 202-01 through 202-04).
- `verify` and `blank` both stand alone on the host, reading with `COMMAND_READ` and comparing on the host, against firmware that still carries `COMMAND_VERIFY` (6) and `COMMAND_BLANK_CHECK` (4) -- neither ordinal is ever sent, proven at the wire level for both commands (phase success criterion 1, the phase's own safety property for Phases 204/205's later removals).
- `EpromOperator._drive_region_compare` and the module-level `_blank_expected_bytes` are available for phase 203's `write --verify` to reuse if it needs a third caller of the same drive -- CONTEXT.md's D-05 anticipated exactly this widening.
- WINDOWS.md is now empty of open entries from this phase (id 1 closed); `open_count: 0`.
- Both `firestarter_app` and the meta repo remain on `v1.41-verification-to-host`; no stray branch. `firestarter_app` HEAD before this plan: `b210dea`; meta HEAD before this plan: `45f4250b`.
- Full suite: 2211 tests passed (up from 2190 before this plan; 2198 after Task 1 alone), 187s, coverage 85.83% (`Required test coverage of 70% reached`), 36/36 snapshots. `ruff check`/`ruff format --check` clean over `firestarter/ tests/`. `mypy firestarter/cli_handlers.py firestarter/main.py firestarter/compare.py`: no issues. `mypy firestarter/ tests/` (full CI scope): 32 errors in 12 files, unchanged from the 202-01/202-04 baseline.
- Phase 203 ("The write guard moves up a layer") is next, per ROADMAP.md — not yet planned.

---
*Phase: 202-one-comparison-engine-on-the-host*
*Completed: 2026-09-20*

## Self-Check: PASSED

- `firestarter_app/firestarter/eprom_operations.py` -- FOUND, modified (`_drive_region_compare`, `check_eprom_blank` rewrite, `verify_eprom` `size_str`, docstring repair)
- `firestarter_app/firestarter/cli_handlers.py` -- FOUND, modified (`_region_refusal_exit_code`, `verify`/`blank` region options and docstrings)
- `firestarter_app/firestarter/chip_test.py` -- FOUND, modified (`OP_BLANK_CHECK` `== 0` adapter)
- `.planning/REQUIREMENTS.md` -- FOUND, modified (CMP-01/02/07/08 Complete)
- `.planning/ROADMAP.md` -- FOUND, modified (202-05 checkbox, 5/5 plans)
- `.planning/WINDOWS.md` -- FOUND, modified (id 1 fixed)
- App commits `92f9cbe`, `ee0743c`, `2e40650` -- FOUND in `git -C firestarter_app log --oneline --all`
- Meta commits `2ff49d6c`, `c541ef07`, `6af0ba09` -- FOUND in `git log --oneline --all`
- Both repos on `v1.41-verification-to-host`, no stray branch
- `tests/test_eprom_operations.py`: 70/70 passed (includes `TestCheckEpromBlankHostSideRead`, `TestOrdinalsNeverSentByVerifyOrBlank`)
- `tests/test_cli_handlers.py`: 82/82 passed
- `tests/test_chip_test.py tests/test_chip_test_sdp_leg.py tests/test_chip_test_cycle.py tests/test_chip_test_timing.py tests/test_chip_test_uv_slot_write.py tests/test_diagnostic_report.py tests/test_devtest_firmware_error_propagation.py tests/test_dev_test_cmd.py`: 307/307 passed
- `tests/test_write_response_budget.py`: 6/6 passed
- Full suite (`pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70 -q`): green, `Required test coverage of 70% reached. Total coverage: 85.83%`, 36/36 snapshots, exit 0; `-o addopts=""` run reported `2211 passed in 187.05s`
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`: clean
- `mypy firestarter/cli_handlers.py firestarter/main.py firestarter/compare.py`: no issues
- `mypy firestarter/ tests/` (full CI scope): 32 errors in 12 files -- unchanged from the 202-01/202-04 baseline
- `python -c "...assert 'ONLY' not in d and 'only EpromOperator method' not in d..."`: `stale claim repaired`
- `python -c "from firestarter.constants import COMMAND_NAMES, COMMAND_BLANK_CHECK, COMMAND_VERIFY; ..."`: `ordinals still defined`
