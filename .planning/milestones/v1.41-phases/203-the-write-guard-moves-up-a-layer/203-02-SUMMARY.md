---
phase: 203-the-write-guard-moves-up-a-layer
plan: 02
subsystem: host-write-path
tags: [python, blank-guard, write-eprom, pytest, database-coupling, negative-address, tdd]

requires:
  - phase: 203-01
    provides: "write_blank_guard.py predicate module (GUARDED_PROTOCOL_IDS, NAMED_EXEMPT_PROTOCOL_IDS, requires_blank_check, is_erase_exempt, refusal_text), CompareResult.first_actual, the write_eprom guard wiring"
provides:
  - "tests/test_write_blank_guard_pinning.py: the narrows-or-widens pinning test for GUARDED_PROTOCOL_IDS/NAMED_EXEMPT_PROTOCOL_IDS, proven RED in both directions"
  - "Named-exemption reasoning for SRAM/FRAM, flash4, and 28C parallel spelled out at each exemption's own site in write_blank_guard.py"
  - "Coverage of the bypass flag (-b), --skip-erase re-arming (D-03), and --force's non-bypass (D-09) at both the unit and drive tier"
  - "Proof that dev test and dev write-cycle are behaviourally unchanged (356 unmodified tests pass), with the dispatch-shape claim and the guard-behaviour claim stated separately"
  - "write_blank_guard.require_non_negative_address and exceptions.NegativeStartAddressError -- the host half of the folded negative-write-start-address todo, wired into both cli_handlers.write() and EpromOperator.write_eprom()"
affects: [203-03, 203-04, 205-firmware-blank-check-removal]

actuals:
  tokens: 8825
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Pinning test via full-set equality (not containment) so narrowing or widening either fails the assertion"
    - "Per-test-scoped (function-local) imports for a genuinely task-scoped RED, rather than a whole-module collection crash that would also fail already-green tests from earlier tasks"
    - "Pure pre-connect gate (F3) wired at two tiers -- the CLI handler (mirroring the existing page_size_gate double-call) and the operator method itself (protecting non-CLI callers)"

key-files:
  created:
    - firestarter_app/tests/test_write_blank_guard_pinning.py
  modified:
    - firestarter_app/firestarter/write_blank_guard.py
    - firestarter_app/firestarter/exceptions.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/test_write_blank_guard.py

key-decisions:
  - "Wired require_non_negative_address at BOTH the CLI tier (cli_handlers.write(), before app.eprom_operator.write_eprom is called) and the operator tier (inside write_eprom itself). The plan's <action> text named only the write_eprom call site, but its own acceptance criterion (\"a CLI run ... never calls write_eprom\", tested via CliRunner + Mock(spec=EpromOperator)) is only satisfiable if the gate ALSO runs before the operator call -- exactly mirroring the existing page_size_gate.require_page_size/require_page_alignment double-call already present in cli_handlers.write(). Documented at both call sites."
  - "Chose AT28C256 (28C parallel, protocol 0x0D) as the 'unguarded family' CLI-level negative-address test target instead of the plan-suggested flash4 W29C020 -- W29C020 requires a page-aligned length for its protocol-0x05 write, and a 4-byte payload against its 128-byte page size trips require_page_alignment's PageAlignmentError before the negative-address gate ever runs. AT28C256 has no such precondition and still proves the gate fires on an unguarded family."
  - "Task 1 and Task 2 needed no new production code -- GUARDED_PROTOCOL_IDS, requires_blank_check, is_erase_exempt, _build_op_flags and the chip_test.py UV write-shortcut expression all already existed correctly from Plan 01. Both tasks are pure characterization/pinning work and were each committed as a single test(...) commit rather than a RED/GREEN pair, since there was no genuine RED to gather against already-correct code."
  - "For Task 3 (the one task that adds real behavior -- require_non_negative_address, NegativeStartAddressError), gathered genuine per-test RED evidence by keeping the new symbols' imports function-local inside each new test rather than at module scope, so the RED failed 7 of 22 tests on real ImportError/AssertionError causes while the 15 already-green legs from Tasks 1-2 kept passing -- avoiding a whole-module collection crash that would have been INVALID_RED under #3770's criteria."
  - "Did not run gsd_run query requirements.mark-complete for WRITE-02/WRITE-03. WRITE-03 is also declared by the not-yet-executed 203-04-PLAN.md; the shared-ID gate requires every declaring plan to finish before either ID is marked, and this plan's own instructions scope state writes to the orchestrator. requirements-completed below lists both IDs verbatim per the plan's own frontmatter, but REQUIREMENTS.md itself is left for the orchestrator/next stage to reconcile."

requirements-completed: [WRITE-02, WRITE-03]

coverage:
  - id: D1
    description: "GUARDED_PROTOCOL_IDS pinned to exactly {0x06,0x07,0x08,0x0B,0x10} and NAMED_EXEMPT_PROTOCOL_IDS to exactly {0x05,0x0D,0x0E,0x27,0x28,0x29} by full-set equality; a test fails whether the guarded set narrows OR widens by a single id, and the coupling test derives both a database-side and a resolve_chip-side set independently and asserts them equal with a sorted symmetric-difference failure message (WRITE-02 criterion 2, D-01, D-02)."
    requirement: WRITE-02
    verification:
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_guarded_protocol_ids_is_exactly_the_five_firmware_pre_flighted_ids"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_named_exempt_protocol_ids_is_exactly_the_six_named_ids"
        status: pass
      - kind: integration
        ref: "tests/test_write_blank_guard_pinning.py#test_predicate_matches_real_database_guarded_rows_exactly"
        status: pass
      - kind: integration
        ref: "tests/test_write_blank_guard_pinning.py#test_unguarded_set_is_non_empty_and_covers_flash4_28c_parallel_and_an_sram_id"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_guarded_row_count_equals_the_sum_of_the_five_guarded_algorithm_counts"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_refusal_text_message_shape_is_pinned_by_equality_and_carries_no_forbidden_content"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_is_guarded_protocol_fails_closed_on_absent_evidence"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_is_guarded_protocol_false_for_an_id_in_neither_set"
        status: pass
    human_judgment: false
  - id: D2
    description: "SRAM/FRAM, flash4 (0x05), and 28C parallel (0x0D) are named exemptions with their reasoning stated at each exemption's own site in write_blank_guard.py, including the 28C-parallel family's 84-row/15-vendor scope and why it is named explicitly rather than left implicit."
    requirement: WRITE-02
    verification:
      - kind: manual_procedural
        ref: "firestarter/write_blank_guard.py NAMED_EXEMPT_PROTOCOL_IDS docstring, SRAM_PROTOCOL_IDS docstring"
        status: pass
    human_judgment: false
  - id: D3
    description: "write -b sets FLAG_SKIP_BLANK_CHECK and not FLAG_SKIP_ERASE (and vice versa for --skip-erase); --skip-erase re-arms the guard on an erase-capable part (D-03); --force never bypasses the guard (D-09) -- each pinned at the unit tier and the two erase/-b legs additionally driven through the genuine write_eprom over a fake serial port."
    requirement: WRITE-03
    verification:
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_build_op_flags_blank_check_false_sets_only_the_skip_blank_check_bit"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_build_op_flags_skip_erase_sets_only_the_skip_erase_bit"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_requires_blank_check_skip_erase_rearms_the_guard_on_an_erase_capable_part"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_requires_blank_check_flag_legs_for_a_flags_zero_guarded_part"
        status: pass
      - kind: integration
        ref: "tests/test_write_blank_guard.py#test_write_with_skip_erase_on_erase_capable_part_refuses_a_non_blank_region"
        status: pass
      - kind: integration
        ref: "tests/test_write_blank_guard.py#test_write_no_blank_check_via_build_op_flags_on_erase_capable_part_pays_no_guard_read"
        status: pass
    human_judgment: false
  - id: D4
    description: "dev test's monotonic-masked UV write-shortcut expression (the exact write_flags derivation chip_test.py's dispatch site uses) keeps requires_blank_check False, and the unmasked case is now True; dev write-cycle's erase-then-write cycle performs no guard read ([COMMAND_ERASE, COMMAND_WRITE, COMMAND_READ], no extra read between erase and write); the five dev-test/chip-test modules (356 tests) pass with an empty git diff, proving the dispatch shape is unchanged -- and, stated separately, that they do NOT exercise the guard because they drive FakeChip/Mock operators."
    requirement: WRITE-03
    verification:
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_dev_test_uv_write_shortcut_keeps_working_and_the_unmasked_case_is_guarded"
        status: pass
      - kind: integration
        ref: "tests/test_write_blank_guard.py#test_write_cycle_eprom_for_an_erase_capable_part_performs_no_guard_read"
        status: pass
      - kind: integration
        ref: "tests/test_chip_test.py, tests/test_chip_test_cycle.py, tests/test_chip_test_uv_slot_write.py, tests/test_chip_test_sdp_leg.py, tests/test_dev_test_cmd.py (356 tests, unmodified)"
        status: pass
    human_judgment: false
  - id: D5
    description: "A negative write start address (decimal or hex) is refused before the serial port opens, on both a guarded family (M27C512) and an unguarded one (AT28C256) -- one host-voiced line, exit 1, no 'Programmer error:' prefix, and write_eprom is never called at the CLI tier; the operator-tier gate inside write_eprom also fires before _operation_context for callers that bypass the CLI (dev test, dev write-cycle). address_parser.py and its own test module are untouched."
    requirement: WRITE-02
    verification:
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_require_non_negative_address_raises_for_a_negative_decimal_address"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_require_non_negative_address_raises_for_a_negative_hex_address"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_require_non_negative_address_is_a_no_op_for_none_and_a_valid_address"
        status: pass
      - kind: unit
        ref: "tests/test_write_blank_guard_pinning.py#test_require_non_negative_address_is_a_no_op_for_an_unparseable_address"
        status: pass
      - kind: integration
        ref: "tests/test_write_blank_guard_pinning.py#test_write_eprom_negative_start_address_refuses_before_operation_context"
        status: pass
      - kind: integration
        ref: "tests/test_write_blank_guard_pinning.py#test_cli_write_negative_address_refuses_on_an_unguarded_family_too"
        status: pass
      - kind: integration
        ref: "tests/test_write_blank_guard_pinning.py#test_cli_write_negative_address_refuses_on_a_guarded_family_too"
        status: pass
    human_judgment: false
  - id: D6
    description: "A second identical guarded write to the same non-blank region is refused, because the first write left the region non-blank -- matching today's firmware behaviour, not a regression."
    verification: []
    human_judgment: true
    rationale: "The plan's own must_haves.truths entry marks this verification kind as 'backstop' -- a property that follows structurally from requires_blank_check's definition (nothing about a second identical write changes any flag or protocol input) rather than one this plan adds a dedicated test for. No test asserts it directly; recorded here for the verifier's visibility rather than silently omitted."

duration: ~50min
completed: 2026-09-21
status: complete
---

# Phase 203 Plan 02: The Write Guard Moves Up a Layer -- Pinning, Bypass Flags, and the Negative-Address Gate Summary

**Pins the exact five-protocol guarded set with a narrows-or-widens equality test (proven RED both directions), covers the `-b`/`--skip-erase`/`--force` flag legs and `dev test`/`dev write-cycle` behavioural equivalence, and closes the host half of the folded negative-write-start-address todo with a new `require_non_negative_address` pre-connect gate wired at both the CLI and operator tiers.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-09-21T12:59:59Z
- **Tasks:** 3
- **Files modified:** 5 (1 created, 5 modified, one file -- write_blank_guard.py -- touched across two tasks)

## Accomplishments

- `GUARDED_PROTOCOL_IDS == frozenset({0x06, 0x07, 0x08, 0x0B, 0x10})` and `NAMED_EXEMPT_PROTOCOL_IDS == frozenset({0x05, 0x0D, 0x0E, 0x27, 0x28, 0x29})` are pinned by full-set equality. **Proven to genuinely fail in both directions**, not just asserted to (see "Pinning Test Perturbation Proof" below).
- Each named exemption (SRAM/FRAM, flash4, 28C parallel) now carries its own reasoning at its own site in `write_blank_guard.py`, including the 28C-parallel family's 84-row/15-vendor scope, which D-01's own prose does not name explicitly.
- The bypass flag (`-b` -> `FLAG_SKIP_BLANK_CHECK`), `--skip-erase`'s guard re-arming (D-03), and `--force`'s non-bypass (D-09) are each pinned at the unit tier, with the erase-exempt and `-b` legs additionally driven through the genuine `write_eprom` over a fake serial port.
- `dev test`'s monotonic-masked UV write-shortcut expression and `dev write-cycle`'s erase-then-write exemption are proven correct via the real `chip_test._is_monotonic_masked_target` expression and a genuine `write_cycle_eprom` drive; the five `dev test`/`chip_test` modules (356 tests) pass with an empty `git diff`, and the summary states separately that they prove dispatch shape, not guard behaviour.
- `write_blank_guard.require_non_negative_address` and `exceptions.NegativeStartAddressError` close the host half of the folded negative-write-start-address todo -- wired into both `cli_handlers.write()` and `EpromOperator.write_eprom()`, refusing before the serial port opens on a guarded family (M27C512) and an unguarded one (AT28C256) alike.

## Task Commits

Each task was committed atomically; Task 3 additionally split into a genuine RED/GREEN pair per its `tdd="true"` attribute (Tasks 1 and 2 needed no new production code -- see "Decisions Made"):

1. **Task 1: Pin the exact guarded set -- narrows or widens** - `ffa08da` (test)
2. **Task 2: The bypass, the re-arming, and the two dev callers** - `a3ddfa1` (test)
3. **Task 3: A negative start address is refused before the port opens** - `fbafddb` (test, RED) + `0a107d3` (feat, GREEN)

**Plan metadata:** this commit, in the meta repo.

## Files Created/Modified

- `firestarter_app/tests/test_write_blank_guard_pinning.py` -- new test module, 22 tests across 9 numbered coverage legs (the exact set, disjointness, database coupling, not-a-blanket-refusal, per-row census, message shape, flag legs, absent-evidence, negative-address gate).
- `firestarter_app/firestarter/write_blank_guard.py` -- named-exemption reasoning breadth for the 28C-parallel family; new `_NEGATIVE_ADDRESS_REFUSAL_FORMAT` and `require_non_negative_address`.
- `firestarter_app/firestarter/exceptions.py` -- new `NegativeStartAddressError(EpromOperationError)`.
- `firestarter_app/firestarter/cli_handlers.py` -- `write()` calls `write_blank_guard.require_non_negative_address` before invoking the operator; `map_typed_errors` gains a `NegativeStartAddressError` arm above the generic `EpromOperationError` arm.
- `firestarter_app/firestarter/eprom_operations.py` -- `write_eprom()` calls the same gate immediately after `require_page_alignment` and before the `os.path.getsize` block.
- `firestarter_app/tests/test_write_blank_guard.py` -- three new drive-level tests: `--skip-erase` re-arming on W27C512, the real `_build_op_flags(blank_check=False)` mapping paying no guard read, and `write_cycle_eprom`'s erase-write-readback cycle paying no guard read.

## Decisions Made

See `key-decisions` in the frontmatter for the full rationale on each of the five decisions. In short: the negative-address gate is wired at both the CLI and operator tiers (not just the operator tier the plan's action text named) because the plan's own acceptance criterion requires it; AT28C256 replaced the plan-suggested W29C020 as the "unguarded family" CLI test target because W29C020's page-alignment gate fires first on a short test payload; Tasks 1-2 needed no new production code so were each a single `test(...)` commit; Task 3's RED/GREEN split used function-local imports to get a genuinely scoped RED; and `requirements.mark-complete` was deliberately not run because WRITE-03 is shared with the not-yet-executed 203-04.

## Pinning Test Perturbation Proof

Per the plan's own acceptance criterion, the guarded-set pin was perturbed in both directions against the final, committed test suite, and both RED outputs were captured before reverting:

**Narrowing (removing `0x0B` from `GUARDED_PROTOCOL_IDS`):**
```
F.....................                                                   [100%]
=================================== FAILURES ===================================
___ test_guarded_protocol_ids_is_exactly_the_five_firmware_pre_flighted_ids ____
    assert GUARDED_PROTOCOL_IDS == frozenset({0x06, 0x07, 0x08, 0x0B, 0x10})
E   assert frozenset({6, 7, 8, 16}) == frozenset({6, 7, 8, 11, 16})
E
E   Extra items in the right set:
E   11
=========================== short test summary info ============================
FAILED tests/test_write_blank_guard_pinning.py::test_guarded_protocol_ids_is_exactly_the_five_firmware_pre_flighted_ids
1 failed, 21 passed in 0.44s
```

**Widening (adding `0x0D` to `GUARDED_PROTOCOL_IDS`):**
```
=================================== FAILURES ===================================
[... test_guarded_protocol_ids_is_exactly_the_five_firmware_pre_flighted_ids fails on the same equality ...]
_ test_unguarded_set_is_non_empty_and_covers_flash4_28c_parallel_and_an_sram_id _
    assert SDP_PROTOCOL_ID in unguarded_algorithms
E   assert 13 in {5, 14, 39, 40, 41, 52}
=========================== short test summary info ============================
FAILED tests/test_write_blank_guard_pinning.py::test_guarded_protocol_ids_is_exactly_the_five_firmware_pre_flighted_ids
FAILED tests/test_write_blank_guard_pinning.py::test_guarded_and_named_exempt_sets_are_disjoint
FAILED tests/test_write_blank_guard_pinning.py::test_predicate_matches_real_database_guarded_rows_exactly
FAILED tests/test_write_blank_guard_pinning.py::test_unguarded_set_is_non_empty_and_covers_flash4_28c_parallel_and_an_sram_id
4 failed, 18 passed in 0.47s
```

Widening additionally breaks the disjointness leg and the real-database coupling leg (some algorithm-13 rows fail `resolve_chip`'s support-status filter, which the raw-database "expected" side does not apply, so the two derivations diverge once the sets overlap) -- a stronger proof than the plan's own claim of "leg 1 and leg 3 red." The file was restored to the committed state and re-verified GREEN (22 passed) after each perturbation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `WriteTarget` construction for the dev-test UV-shortcut leg needed the real `mask_write_pattern`/`bits_cleared_by`/`bits_retained_by` helpers**
- **Found during:** Task 2, writing `test_dev_test_uv_write_shortcut_keeps_working_and_the_unmasked_case_is_guarded`
- **Issue:** A hand-built masked `WriteTarget` with `bits_cleared=64, bits_retained=0` raised `ValueError` from `WriteTarget.__post_init__`'s `_UV_MIN_RETAINED_BITS` (64) floor -- both cleared and retained bit counts must independently clear 64, which a hand-picked pattern could not satisfy without risking an inconsistent fixture.
- **Fix:** Reused the exact recipe `tests/test_chip_test_uv_slot_write.py::test_fixed_policy_with_the_witness_sets_the_flag` already uses: `current = b"\xff" * 256`, `desired = generate_pattern(...)`, `pattern = mask_write_pattern(current, desired)`, with `bits_cleared_by`/`bits_retained_by` deriving the counts.
- **Files modified:** tests/test_write_blank_guard_pinning.py
- **Verification:** Test passes; `WriteTarget.__post_init__` validation satisfied.
- **Committed in:** a3ddfa1

**2. [Rule 1 - Bug] The initial "unguarded family" CLI negative-address test target (W29C020) tripped an unrelated pre-existing gate**
- **Found during:** Task 3, writing the CLI-level negative-address tests
- **Issue:** W29C020 is protocol 0x05 (flash4), which carries its own page-alignment requirement; a 4-byte test payload against its 128-byte page size raised `PageAlignmentError` before `require_non_negative_address` ever ran, making the test assert the wrong refusal text.
- **Fix:** Switched the "unguarded family" test target to AT28C256 (28C parallel, protocol 0x0D), which carries no page-alignment precondition and still proves the negative-address gate fires on an unguarded family.
- **Files modified:** tests/test_write_blank_guard_pinning.py
- **Verification:** Both CLI-level negative-address tests (guarded M27C512, unguarded AT28C256) pass.
- **Committed in:** fbafddb (test) / 0a107d3 (feat) -- the fix was applied before the RED commit was captured, so both commits reflect the corrected target.

---

**Total deviations:** 2 auto-fixed (both Rule 1 -- bugs in test construction, not production code). **Impact on plan:** Neither affected production code or scope; both were necessary to get the intended coverage working correctly.

## Issues Encountered

None beyond the two deviations above.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- 203-03 (`write --verify`) and 203-04 (session-cost measurement) can proceed: the guarded-set pin, the flag-leg coverage, and the negative-address gate are all committed, unit- and integration-tested, and the full suite is green.
- `write_blank_guard.py`'s public surface (`GUARDED_PROTOCOL_IDS`, `NAMED_EXEMPT_PROTOCOL_IDS`, `requires_blank_check`, `is_erase_exempt`, `refusal_text`, `require_non_negative_address`) is stable and covered; no further symbols were added beyond what this plan's frontmatter declared.
- `WRITE-03` remains shared with 203-04's frontmatter; REQUIREMENTS.md was deliberately left untouched by this plan (see "Decisions Made") and should be reconciled once 203-04 completes.
- No blockers. `firestarter_fw/` was not touched -- confirmed by scope (this plan only operates inside `firestarter_app/`).

## Self-Check: PASSED

- `firestarter_app/firestarter/write_blank_guard.py` -- FOUND
- `firestarter_app/firestarter/exceptions.py` -- FOUND
- `firestarter_app/firestarter/cli_handlers.py` -- FOUND
- `firestarter_app/firestarter/eprom_operations.py` -- FOUND
- `firestarter_app/tests/test_write_blank_guard_pinning.py` -- FOUND
- `firestarter_app/tests/test_write_blank_guard.py` -- FOUND
- Commit `ffa08da` -- FOUND in `git log --oneline --all`
- Commit `a3ddfa1` -- FOUND in `git log --oneline --all`
- Commit `fbafddb` -- FOUND in `git log --oneline --all`
- Commit `0a107d3` -- FOUND in `git log --oneline --all`
- `git -C firestarter_app status --porcelain` shows only the pre-existing, unrelated untracked `datasheets/LST62832I.pdf`.
- Full suite: 2269 passed, 0 failed, 36 snapshots passed (baseline 2244 + 25 new tests: 22 in `test_write_blank_guard_pinning.py`, 3 in `test_write_blank_guard.py`).
- Coverage: 86.00% (floor 70%); `write_blank_guard.py` at 100%.
- `ruff check` / `ruff format --check` clean on `firestarter/` and `tests/`.
- `mypy` on `write_blank_guard.py`/`cli_handlers.py`/`eprom_operations.py`: 10 pre-existing `union-attr` errors in `eprom_operations.py`, all outside this plan's diff (confirmed identical before/after); `write_blank_guard.py` and `cli_handlers.py` are mypy-clean.
- `tests/test_chip_test.py`, `test_chip_test_cycle.py`, `test_chip_test_uv_slot_write.py`, `test_chip_test_sdp_leg.py`, `test_dev_test_cmd.py`: 356 tests pass, `git diff --name-only` over them is empty.
- `firestarter/address_parser.py` / `tests/test_address_parser.py`: `git diff --name-only` is empty.
- Guarded-set pin perturbation: narrowing and widening `GUARDED_PROTOCOL_IDS` both produce a nonzero-exit, failing test run (transcripts above); reverted and re-verified GREEN.

---
*Phase: 203-the-write-guard-moves-up-a-layer*
*Completed: 2026-09-21*
