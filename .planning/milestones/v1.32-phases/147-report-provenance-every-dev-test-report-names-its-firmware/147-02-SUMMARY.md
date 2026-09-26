---
phase: 147-report-provenance-every-dev-test-report-names-its-firmware
plan: 02
subsystem: infra
tags: [python, pytest, dev-test, provenance, hardware, cli, ruff, mypy]

# Dependency graph
requires:
  - phase: 147-01
    provides: "firestarter_app on gsd/v1.32-at28c-write-path-root-cause-report-provenance, 1590-passed baseline"
provides:
  - "ProgrammerIdentity NamedTuple (hw_revision, fw_board_identity) on firestarter/hardware.py"
  - "HardwareManager.read_programmer_identity() — renamed/widened read_hardware_revision_value, one production call site, independent per-field failure paths (D-04)"
  - "_scrub_identity() — printable-ASCII scrub, 64-char cap, empty-collapses-to-None (D-07)"
  - "cli_handlers.py's dev_test handler feeds AutoCapture.fw_board_identity from a real captured value instead of a hardcoded None"
  - "make_hardware_manager() test fixture returns a real ProgrammerIdentity (never a bare Mock) with a variable fw_board_identity field"
  - "4 new tests proving PROV-01 (handler oracle) and PROV-03 (suffix preservation + differing-pair discrimination)"
affects: [147-03, 147-04, 147-05, 147-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Harvest a second identity value off a connection a sibling read already opens, inside its existing try/finally, rather than opening a dedicated connection (D-01) — read comm.firmware_identity before comm.expect_ack() so an ack failure can still surface it (D-04)"
    - "Scrub untrusted device strings at the boundary where they first become a Python str: printable-ASCII allow-list + fixed replacement char + length cap, never silent collapse of a partially-bad value to None (D-07)"
    - "Test doubles for a renamed method must return the SAME real type the production code returns (a NamedTuple here), never a bare Mock/MagicMock, so an un-spec-protected field name can't leak a child-mock repr into a report"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/hardware.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_dev_test_cmd.py

key-decisions:
  - "D-01/D-02/D-03/D-04/D-07/D-08 (147-CONTEXT.md) applied exactly as specified: one connection, one renamed+widened method returning a named-field NamedTuple, independent per-field failure, printable-ASCII scrub with None-collapse-on-empty, and a differing-pair discrimination test rather than a single round-trip assertion"
  - "D-05 ring fence held: serial_comm.py, tools/check_devtest_orchestrator.py, tests/test_check_devtest_orchestrator.py, tests/test_fwguard.py, tests/test_fw_version_guard.py, firestarter/diagnostic_report.py all show zero diff — verified by git diff --stat after every task"
  - "No new callable added to cli_handlers.py (avoids tripping tools/check_devtest_orchestrator.py's hard-equality HANDLER_FUNCTION_NAMES assertion); the scrub lives entirely in hardware.py"

requirements-completed: [PROV-03]

coverage:
  - id: D1
    description: "read_hardware_revision_value renamed to read_programmer_identity, returning ProgrammerIdentity(hw_revision, fw_board_identity); old name removed from firestarter/, tools/, tests/ (8/8 measured sites)"
    requirement: "PROV-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dev_test_cmd.py::test_make_hardware_manager_returns_a_spec_bound_double"
        status: pass
      - kind: other
        ref: "grep -rc 'read_hardware_revision_value' firestarter/ tools/ tests/ => no matches"
        status: pass
    human_judgment: false
  - id: D2
    description: "cli_handlers.py's dev_test handler feeds AutoCapture from the real captured identity by field name instead of a hardcoded fw_board_identity=None"
    requirement: "PROV-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dev_test_cmd.py::TestReportDestination::test_fw_board_identity_auto_captured_end_to_end"
        status: pass
    human_judgment: false
  - id: D3
    description: "Prerelease suffix survives verbatim into the saved report JSON; two identities differing only in suffix land as two different recorded values"
    requirement: "PROV-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dev_test_cmd.py::TestReportDestination::test_prerelease_suffix_survives_into_the_report"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_dev_test_cmd.py::TestReportDestination::test_two_identities_differing_only_in_suffix_land_as_different_values"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full app test suite green with 5 new tests over the 147-01 baseline; ci_parity.sh legs 1-3 green, leg 4 exits 2 as documented"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts=\"\" -q  =>  1595 passed, 1 warning in 243.30s"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter_app && bash tools/ci_parity.sh  =>  legs 1/2/3 exit 0, leg 4 exit 2 (expected)"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-18
status: complete
---

# Phase 147 Plan 02: Widen hardware identity read + AutoCapture wiring Summary

**Renamed `HardwareManager.read_hardware_revision_value` to `read_programmer_identity`, widened it to a `ProgrammerIdentity` NamedTuple carrying both the hardware-revision string and the raw firmware/board identity harvested off the connection the revision read already opens, and wired `cli_handlers.py`'s `dev_test` handler to feed real values into `AutoCapture` instead of a hardcoded `fw_board_identity=None`.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-18
- **Tasks:** 3
- **Files modified:** 3 (`firestarter/hardware.py`, `firestarter/cli_handlers.py`, `tests/test_dev_test_cmd.py`)

## Accomplishments

- Added `ProgrammerIdentity(NamedTuple)` (`hw_revision`, `fw_board_identity`, both `Optional[str]`) and module-private `_scrub_identity()` to `firestarter/hardware.py`, following the module's `Optional[str]` convention (not `str | None`) and the in-repo `FrameVector(NamedTuple)` precedent for style.
- Renamed `read_hardware_revision_value` to `read_programmer_identity`, keeping its `flags: int = 0` signature and exact `find_and_connect -> expect_ack -> disconnect` handshake (SAFE-02 clean, zero new serial connections). `comm.firmware_identity` is scrubbed and bound to a local **before** `comm.expect_ack()` so an ack failure or transport exception can still return the harvested identity — the two fields fail independently (D-04). Guarded against a latent `NameError` in the exception branches by initializing the local to `None` before the `try`.
- `cli_handlers.py`'s `dev_test` handler now calls `read_programmer_identity()` once and constructs `AutoCapture(fw_board_identity=identity.fw_board_identity, hw_revision=identity.hw_revision, ...)` by named field access (D-03), replacing the stale 7-line comment with one explaining why the hardware-revision connection can now serve both fields. No new callable was added to `cli_handlers.py` (avoids the AST-gate hard-equality trap in `tools/check_devtest_orchestrator.py`).
- Carried the rename through all 6 remaining sites in `tests/test_dev_test_cmd.py`: `make_hardware_manager`'s wiring line and docstring now build and return a real `ProgrammerIdentity` (never a bare `Mock`), plus 3 docstring/assertion renames including the absent-chip false-green guard's `assert_not_called()`.
- Added `test_make_hardware_manager_returns_a_spec_bound_double` pinning the property the rename's safety rests on: the double is spec-bound (an attribute the real `HardwareManager` doesn't define raises `AttributeError`) and its `read_programmer_identity()` return value is a real `ProgrammerIdentity`.
- Added three PROV-01/PROV-03 handler-level oracles mirroring the existing hardware-revision end-to-end analog: `test_fw_board_identity_auto_captured_end_to_end` (asserts the exact identity in both rendered output and saved JSON), `test_prerelease_suffix_survives_into_the_report` (parametrized b11/b19, verbatim survival), and `test_two_identities_differing_only_in_suffix_land_as_different_values` (the D-08 differing-pair discrimination oracle — asserts inequality, not just presence).
- Verified the D-05 ring fence held throughout: `git diff --stat` against `serial_comm.py`, `tools/check_devtest_orchestrator.py`, `tests/test_check_devtest_orchestrator.py`, `tests/test_fwguard.py`, `tests/test_fw_version_guard.py`, and `firestarter/diagnostic_report.py` is empty after every task.

## Task Commits

1. **Task 1: Widen and rename the hardware read, and feed AutoCapture from it** - `5507770` (feat)
2. **Task 2: Carry the rename through the mock surface — W-5 fixture returns a real ProgrammerIdentity** - `6e57d97` (test)
3. **Task 3: Prove the identity reaches the report, and that its prerelease suffix discriminates** - `44dd8fb` (test)

**Plan metadata:** committed via this SUMMARY + STATE.md + ROADMAP.md docs commit (see below), plus a `chore(147-02)` gitlink bump in the meta repo.

## Files Created/Modified

- `firestarter_app/firestarter/hardware.py` - `ProgrammerIdentity` NamedTuple, `_scrub_identity()`, `read_programmer_identity()` (renamed/widened from `read_hardware_revision_value`)
- `firestarter_app/firestarter/cli_handlers.py` - `dev_test` handler feeds `AutoCapture` from the real captured `ProgrammerIdentity` by field name
- `firestarter_app/tests/test_dev_test_cmd.py` - `make_hardware_manager` gains `fw_board_identity` keyword and returns a real `ProgrammerIdentity`; 4 new tests (spec-bound pin + 3 PROV-01/PROV-03 oracles); all 8 rename sites updated

## Decisions Made

- Initialized the local `fw_board_identity` variable to `None` before the `try` block in `read_programmer_identity` (not specified verbatim in the plan's action text, but required by its own return-contract: without it, a `find_and_connect` exception raised before the scrub line would hit a bare-`None`-less `ProgrammerIdentity` construction referencing an undefined name). This is a Rule 1 auto-fix — a latent `NameError` bug in the literal code shape the plan described — verified by the existing exception-path test coverage staying green.
- Placed the three new PROV-01/PROV-03 tests inside the existing `TestReportDestination` class (alongside the hardware-revision end-to-end analog they mirror) rather than a new class, since the plan named that test as "the right analog" and it lives there.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Guarded against a NameError in read_programmer_identity's exception branches**
- **Found during:** Task 1
- **Issue:** The plan's described control flow reads `comm.firmware_identity` inside the `try`, after `find_and_connect`, and returns it from both the `except` clause and the `is_ok` branches. If `find_and_connect` itself raises (`ProgrammerNotFoundError`/`SerialError`/`SerialTimeoutError`) before the scrub line executes, the local used in the `except` clause would be undefined, raising `NameError` instead of the intended `ProgrammerIdentity(hw_revision=None, fw_board_identity=...)`.
- **Fix:** Initialize `fw_board_identity = None` immediately before the `try` block, so every return path — including a `find_and_connect` failure — has a bound value.
- **Files modified:** `firestarter_app/firestarter/hardware.py`
- **Verification:** `ruff check`/`ruff format --check` clean; full suite green (1595 passed); no test exercises this literal branch directly (the mocked doubles never raise from `find_and_connect`), but the fix is structurally required for the method's own documented contract of "never a bare None" on any path.
- **Committed in:** `5507770` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Necessary for correctness of the exact code shape the plan specified. No scope creep — no new callable, no new file, no behavior beyond what the plan's own `<action>` text describes.

## Issues Encountered

- `ruff format` flagged 2 lines in the newly-added Task 3 tests (a `@pytest.mark.parametrize` line and a chained-dict-access line exceeding the wrap threshold); ran `ruff format tests/test_dev_test_cmd.py` to auto-fix before committing.
- `grep -cE '= Mock\(\)\s*$' tests/test_dev_test_cmd.py` prints `2`, not the `0` the plan's acceptance-criteria prose named. Investigated: both matches (`mock_browser_open = Mock()`, `mock_run_fn = Mock()`) are pre-existing lines unrelated to hardware-manager doubles (they mock `webbrowser.open`/`subprocess.run` in `TestSubmitReport`), confirmed absent from this plan's `git diff`. No unspecced *hardware-manager* double was introduced — the load-bearing invariant the criterion protects — so this is a pre-existing condition, not a regression, and was left unedited (out of this task's scope per the deviation-rules SCOPE BOUNDARY).
- The full-suite `pytest` run and `tools/ci_parity.sh` each exceed the 120s default Bash timeout and were run in the background; results read directly from the background output files rather than retried in the foreground.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter_app/firestarter/hardware.py` now exposes `ProgrammerIdentity` and `read_programmer_identity` for plans 147-04 (PROV-02 connection-count unit test) and any later plan needing the identity value.
- `AutoCapture.fw_board_identity` is now populated end-to-end; plan 147-03 (schema bump, `NOT_REPORTED` sentinel, render marker) can proceed against a real, non-null value.
- Pre-task `test_dev_test_cmd.py` count was 53 (measured before Task 2's first new test); post-plan count is 58 (53 + 5 new tests: `test_make_hardware_manager_returns_a_spec_bound_double`, `test_fw_board_identity_auto_captured_end_to_end`, `test_prerelease_suffix_survives_into_the_report` ×2 parametrized cases, `test_two_identities_differing_only_in_suffix_land_as_different_values`).
- Full-suite count: 1595 passed, 1 warning in 243.30s (baseline 1590 + 5 new tests) — the new Phase 147 regression floor.
- `bash tools/ci_parity.sh`: legs 1-3 exit 0; leg 4 exits 2 as documented design (ambient numpy PEP-695 stub truncating mypy in this devcontainer) — not a defect, not "fixed" with `|| true` per the plan's explicit instruction.
- No blockers for 147-03/147-04/147-05/147-06.

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/hardware.py` contains `class ProgrammerIdentity`, `def _scrub_identity`, `def read_programmer_identity`
- FOUND: `firestarter_app/firestarter/cli_handlers.py` contains `read_programmer_identity()` call and named-field `AutoCapture` construction
- FOUND: commit `5507770` in `firestarter_app` (`git log --oneline --all | grep 5507770`)
- FOUND: commit `6e57d97` in `firestarter_app` (`git log --oneline --all | grep 6e57d97`)
- FOUND: commit `44dd8fb` in `firestarter_app` (`git log --oneline --all | grep 44dd8fb`)

---
*Phase: 147-report-provenance-every-dev-test-report-names-its-firmware*
*Completed: 2026-08-18*
