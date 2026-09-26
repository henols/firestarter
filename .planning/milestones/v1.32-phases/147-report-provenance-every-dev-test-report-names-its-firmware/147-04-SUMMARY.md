---
phase: 147-report-provenance-every-dev-test-report-names-its-firmware
plan: 04
subsystem: testing
tags: [python, pytest, dev-test, provenance, hardware, ruff]

# Dependency graph
requires:
  - phase: 147-02
    provides: "ProgrammerIdentity NamedTuple, _scrub_identity(), read_programmer_identity() on firestarter/hardware.py; make_hardware_manager(fw_board_identity=...) fixture; 1599-passed baseline"
  - phase: 147-03
    provides: "NOT_REPORTED constant + _identity_cell() render-boundary helper on firestarter/diagnostic_report.py"
provides:
  - "First-ever unit coverage of read_programmer_identity() in tests/test_hardware.py (13 -> 22 tests)"
  - "PROV-02's one-connection/one-disconnect claim proven mechanically (call_count == 1, disconnect.assert_called_once())"
  - "D-04's two failure paths (revision-ack-fails-identity-survives; transport-raises-both-absent) proven independent, including the failed-after-harvest case"
  - "D-07's scrub proven in both directions: mangled stays visibly faulty, empty collapses to absent, all-non-printable does not collapse"
  - "D-13(b) handler-level leg: an absent identity renders the NOT_REPORTED marker and saves typed null in tests/test_dev_test_cmd.py"
affects: [147-05, 147-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Wrap a real (non-Mock) SerialCommunicator's disconnect with Mock(wraps=comm.disconnect) to assert call counts on an object built via __new__, since it isn't itself a mock"
    - "Replace a bound method on a real communicator instance (comm.expect_ack = Mock(side_effect=...)) to prove ordering (harvest-before-teardown) independent of the fake-serial byte stream"
    - "Line-scoped bare-None assertion (filter result.output to lines mentioning the field name, then regex \\bNone\\b on just those lines) instead of a whole-output substring scan, to avoid a false positive against the deliberately-untouched chip_id (expected/actual) row"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_hardware.py
    - firestarter_app/tests/test_dev_test_cmd.py

key-decisions:
  - "D-04's leg-2 transport-error test is parametrized over ProgrammerNotFoundError and SerialTimeoutError (2 cases from 1 function) rather than two separate functions, since both exceptions must reach the exact same except clause and assertion"
  - "The D-07 mangled leg imports NOT_REPORTED from firestarter.diagnostic_report for its 'not equal to the unknown marker' assertion, as a forward defense against a future refactor that has _scrub_identity return the render-layer marker literal directly instead of collapsing to None"
  - "Task 3's negative assertion filters result.output to only the lines containing 'fw_board_identity' or 'hw_revision' before regexing for a bare None, because the same table's chip_id (expected/actual) row legitimately renders 'None / None' for the M8720 fixture chip and a blanket scan would false-positive there (mirrors 147-03's own per-row precision fix for the identical hazard)"

requirements-completed: [PROV-01, PROV-02]

coverage:
  - id: D1
    description: "read_programmer_identity() harvests fw_board_identity verbatim off the single connection and returns hw_revision from the CMD_HW_VERSION ack, read by field name (PROV-01 unit oracle, W-1)"
    requirement: "PROV-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_read_programmer_identity_happy_path_harvests_the_identity_verbatim"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_read_programmer_identity_default_comm_yields_the_absent_case"
        status: pass
    human_judgment: false
  - id: D2
    description: "Exactly one find_and_connect and one disconnect() per call, and no EpromOperator attribute written -- PROV-02's connection-count claim proven mechanically, not argued from source"
    requirement: "PROV-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_read_programmer_identity_opens_one_connection_and_disconnects_once"
        status: pass
      - kind: other
        ref: "python3 tools/check_devtest_orchestrator.py => PASS (0 VPP-set, 0 raw-wire-dict, 0 --force, 0 broad-except)"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-04's two failure paths are independent: a revision-ack failure still returns the harvested identity, and a transport exception (before or after the harvest) never degrades to a bare None"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_read_programmer_identity_revision_fails_but_identity_survives"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_read_programmer_identity_transport_error_returns_both_absent"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_read_programmer_identity_transport_error_after_harvest_keeps_the_identity"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-07's scrub is pinned in both directions: a U+FFFD-bearing identity stays visibly faulty (never collapsed to the unknown marker), an empty identity collapses to None, and an all-non-printable identity does not collapse"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_read_programmer_identity_scrub_keeps_a_mangled_identity_visibly_faulty"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_hardware.py::test_read_programmer_identity_scrub_collapses_an_empty_identity_to_absent"
        status: pass
    human_judgment: false
  - id: D5
    description: "D-13(b): an absent identity at handler level renders the NOT_REPORTED marker on both identity rows and saves typed null for both auto_capture.fw_board_identity and auto_capture.hw_revision in the saved report JSON, proven through the existing spec-bound make_hardware_manager mock"
    requirement: "PROV-05 (advances, not completed by this plan)"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dev_test_cmd.py::TestReportDestination::test_unknown_identity_renders_the_marker_and_saves_typed_null"
        status: pass
    human_judgment: false
  - id: D6
    description: "Full app test suite green with 10 new tests over the 147-03 baseline; the D-05 ring fence (serial_comm.py, test_fwguard.py, test_fw_version_guard.py) held; ci_parity.sh legs 1-3 green, leg 4 exits 2 as documented"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts=\"\" -q  =>  1609 passed, 1 warning in 292.74s"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter_app && bash tools/ci_parity.sh  =>  legs 1/2/3 exit 0, leg 4 exit 2 (expected)"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter_app && pytest tests/test_fwguard.py tests/test_fw_version_guard.py -o addopts=\"\" -q  =>  16 passed; git diff --stat names neither file"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-18
status: complete
---

# Phase 147 Plan 04: Unit oracles for the capture seam + D-13(b) handler leg Summary

**Built the first-ever unit coverage of `read_programmer_identity()` in `tests/test_hardware.py` (13 → 22 tests) proving PROV-02's one-connection/one-disconnect claim mechanically and D-04's two independent failure paths, plus the D-13(b) handler-level leg proving an absent identity renders the explicit marker while the saved JSON stays typed `null`.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-08-18
- **Tasks:** 3
- **Files modified:** 2 (`tests/test_hardware.py`, `tests/test_dev_test_cmd.py`)

## Accomplishments

- Added 8 new tests to `tests/test_hardware.py` (13 → 22; 9 new test *cases* once the transport-error parametrization is counted): the happy path harvesting the identity verbatim by field name (PROV-01), the one-connection/one-disconnect mechanical proof with no `EpromOperator` anywhere in the test's graph (PROV-02, SAFE-02), the free absent-case leg from `make_comm()`'s fail-closed default, both D-04 failure-path legs (revision-ack-fails-identity-survives, and transport-raises-both-absent parametrized over `ProgrammerNotFoundError`/`SerialTimeoutError`), the failed-after-harvest leg proving the harvest-before-teardown ordering is load-bearing (with `disconnect()` still asserted to run), and both D-07 scrub legs (mangled stays visibly faulty, empty collapses to absent with an all-non-printable companion case that does *not* collapse).
- Added `test_unknown_identity_renders_the_marker_and_saves_typed_null` to `tests/test_dev_test_cmd.py`'s `TestReportDestination` class, closing D-13's handler-level half: driven through the existing spec-bound `make_hardware_manager(hw_revision=None, fw_board_identity=None)`, it asserts in one test that the rendered output carries the imported `NOT_REPORTED` marker (never restated as a literal) with no bare `None` on either identity row, while the saved report JSON keeps both `auto_capture.fw_board_identity` and `auto_capture.hw_revision` typed `null`.
- Reused the file's existing `hw_config`/`make_comm`/`fake_serial` fixtures and `patch("firestarter.serial_comm.SerialCommunicator.find_and_connect")` idiom throughout; added no new fixture and no serial port.
- Confirmed the module's declared safety boundary (no `set_vpp_voltage`/`set_vpe_voltage` *calls*) and confirmed no test asserts on the confusable `comm.hw_revision` CAP-02 byte.
- Full suite: 1609 passed (147-03 baseline 1599 + 3 + 6 + 1 new test cases). `ci_parity.sh` legs 1-3 green, leg 4 exits 2 as documented design. The D-05 ring fence (`serial_comm.py`, `test_fwguard.py`, `test_fw_version_guard.py`) held throughout — `git diff --stat` names only the two files in `files_modified`.

## Task Commits

1. **Task 1: W-1 part A — happy path and one-connection/one-disconnect proof** - `2ea5802` (test)
2. **Task 2: W-1 part B — independent failure paths and the scrub** - `42b9d63` (test)
3. **Task 3: D-13(b) — absent identity at handler level renders the marker and saves typed null** - `223d7e1` (test)

**Plan metadata:** committed via this SUMMARY + STATE.md + ROADMAP.md docs commit (see below), plus a `chore(147-04)` gitlink bump in the meta repo.

## Files Created/Modified

- `firestarter_app/tests/test_hardware.py` - 8 new tests (9 cases with parametrization) covering `read_programmer_identity()`'s happy path, connection count, both D-04 failure paths (including failed-after-harvest), and both D-07 scrub directions
- `firestarter_app/tests/test_dev_test_cmd.py` - `NOT_REPORTED` import added; one new test (`test_unknown_identity_renders_the_marker_and_saves_typed_null`) in `TestReportDestination` proving D-13(b)

## Decisions Made

- Parametrized the D-04 leg-2 transport-error test over `ProgrammerNotFoundError` and `SerialTimeoutError` (both `SerialError` subclasses landing in the same `except` clause per RESEARCH F-17) rather than writing two near-identical functions.
- Imported `NOT_REPORTED` from `firestarter.diagnostic_report` into the D-07 mangled-identity unit test purely as a forward-defense comparison (`identity.fw_board_identity != NOT_REPORTED`) — `_scrub_identity()` itself has no dependency on that constant today; the assertion guards against a future refactor accidentally coupling the two.
- Used a line-scoped regex check (`\bNone\b` only on lines mentioning `fw_board_identity`/`hw_revision`) for Task 3's negative assertion instead of a whole-output substring scan, because the same rendered table's `chip_id (expected/actual)` row legitimately shows `None / None` for the `M8720` fixture chip — a blanket scan would have false-positived on that unrelated, deliberately-untouched row (the exact hazard 147-03's own per-row-cell test design flagged).

## Deviations from Plan

None — plan executed exactly as written. One documentation-accuracy note (not a deviation, since no plan text was altered and no code changed as a result):

- **Acceptance-criteria literal mismatch (Task 1):** the plan's acceptance criterion `grep -c 'set_vpp_voltage\|set_vpe_voltage' tests/test_hardware.py` prints `0` does not hold — it prints `2`, both from the file's pre-existing (pre-dating this plan) module-docstring safety-boundary text at lines 4-5 ("this file does NOT exercise ``set_vpp_voltage`` or ``set_vpe_voltage``"), confirmed present in the file at `HEAD~3` before any of this plan's edits. The functional invariant the criterion exists to protect — no actual *call* to either method — was verified directly: `grep -c '\.set_vpp_voltage(\|\.set_vpe_voltage(' tests/test_hardware.py` prints `0`. The module's declared safety boundary is intact; the plan's literal grep expression just also matches the docstring's own prose describing that boundary.

## Issues Encountered

- The full-suite `pytest` run and `bash tools/ci_parity.sh` each exceed the 120s default Bash timeout and were run in the background; results read directly from the background output files.
- `ruff format` auto-reformatted one line in Task 2's new parametrize decorator (wrapped it to fit the line-length limit) before commit — a formatting-only, non-functional change caught and applied before staging.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- PROV-01 and PROV-02 are now fully proven at both levels the requirements table names: the handler-level oracle landed in 147-02, and the unit-level oracle (this plan) proves the connection-count and harvest-verbatim claims mechanically. Both requirement IDs marked complete.
- PROV-05's D-13 unknown-identity leg is now proven at both levels D-13 names: the render-level leg (147-03) and this plan's handler-level leg. PROV-05 itself is still advanced-not-completed — the issue-parser surfaces (PROV-06) remain for 147-05/147-06.
- `tests/test_hardware.py` pre-task count was 13; post-plan count is 22 (13 + 9 test cases across 8 new functions, one parametrized into 2 cases).
- `tests/test_dev_test_cmd.py` pre-task count was 58 (147-02 baseline); post-plan count is 59.
- Full-suite count: **1609 passed, 1 warning** (147-03 baseline 1599 + 10 new test cases) — the new Phase 147 regression floor for 147-05/147-06.
- `bash tools/ci_parity.sh`: legs 1-3 exit 0; leg 4 exits 2 as documented design (ambient numpy PEP-695 stub truncating mypy in this devcontainer) — recorded as expected, no `|| true` added.
- No blockers for 147-05/147-06.

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_hardware.py` contains `test_read_programmer_identity_happy_path_harvests_the_identity_verbatim`, `test_read_programmer_identity_opens_one_connection_and_disconnects_once`, `test_read_programmer_identity_default_comm_yields_the_absent_case`, `test_read_programmer_identity_revision_fails_but_identity_survives`, `test_read_programmer_identity_transport_error_returns_both_absent`, `test_read_programmer_identity_transport_error_after_harvest_keeps_the_identity`, `test_read_programmer_identity_scrub_keeps_a_mangled_identity_visibly_faulty`, `test_read_programmer_identity_scrub_collapses_an_empty_identity_to_absent`
- FOUND: `firestarter_app/tests/test_dev_test_cmd.py` contains `test_unknown_identity_renders_the_marker_and_saves_typed_null`
- FOUND: commit `2ea5802` in `firestarter_app` (`git log --oneline --all | grep 2ea5802`)
- FOUND: commit `42b9d63` in `firestarter_app` (`git log --oneline --all | grep 42b9d63`)
- FOUND: commit `223d7e1` in `firestarter_app` (`git log --oneline --all | grep 223d7e1`)

---
*Phase: 147-report-provenance-every-dev-test-report-names-its-firmware*
*Completed: 2026-08-18*
