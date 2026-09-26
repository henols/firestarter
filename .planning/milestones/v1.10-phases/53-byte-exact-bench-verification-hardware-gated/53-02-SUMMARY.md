---
phase: 53-byte-exact-bench-verification-hardware-gated
plan: "02"
subsystem: firestarter_app/firestarter
tags: [tdd, green-phase, write-cycle, fault-inject, serial-comm, cli, coverage]
dependency_graph:
  requires:
    - phase: "53-01"
      provides: "RED test scaffold for write_cycle_eprom, fault-inject hooks, dev subcommands"
  provides:
    - "EpromOperator.write_cycle_eprom() — erase→write→read-back→SHA-256 compare, 3-way verdict"
    - "EpromOperator.fault_inject_cycle() — corrupted-then-clean COBS resync proof"
    - "SerialCommunicator._fault_inject_outgoing hook (getattr-guarded, default None)"
    - "FaultInjectingSerialCommunicator subclass — one-shot _decode_id_frame incoming flip"
    - "dev write-cycle and dev fault-inject Click subcommands"
  affects:
    - "firestarter_app/firestarter/eprom_operations.py"
    - "firestarter_app/firestarter/serial_comm.py"
    - "firestarter_app/firestarter/cli_handlers.py"
    - "firestarter_app/tests/test_eprom_operations.py"
    - "firestarter_app/tests/test_serial_comm.py"
    - "firestarter_app/tests/test_cli_handlers.py"
    - "firestarter_app/tests/conftest.py"
tech_stack:
  added: []
  patterns:
    - "write_cycle_eprom: reuse-not-duplicate — read-back block copied verbatim from consistency_check_eprom"
    - "fault-inject hook: getattr-guarded attribute on SerialCommunicator.__init__ (T-53-03)"
    - "FaultInjectingSerialCommunicator: subclass overrides only _decode_id_frame, not _read_and_parse_lines (GATE-1.8d)"
    - "3-way verdict passthrough: sys.exit(verdict_int) in CLI — no bool-to-int wrap"
key_files:
  created: []
  modified:
    - "firestarter_app/firestarter/eprom_operations.py — write_cycle_eprom() + fault_inject_cycle()"
    - "firestarter_app/firestarter/serial_comm.py — _fault_inject_outgoing attr + hook in send_json_command + FaultInjectingSerialCommunicator"
    - "firestarter_app/firestarter/cli_handlers.py — dev write-cycle + dev fault-inject subcommands"
    - "firestarter_app/tests/test_eprom_operations.py — 3 new fault_inject_cycle coverage tests (Rule 2)"
    - "firestarter_app/tests/conftest.py — mirror _fault_inject_outgoing = None in make_comm factory"
    - "firestarter_app/tests/__snapshots__/test_characterization.ambr — updated dev --help snapshot"
key-decisions:
  - "fault_inject_cycle sets the outgoing hook INSIDE _operation_context (after self.comm is set), not before — this is the correct production flow since _setup_operation assigns self.comm"
  - "conftest.py make_comm factory updated to mirror __init__ attribute _fault_inject_outgoing = None (Rule 2: make_comm bypasses __init__; test would always fail RED without the mirror)"
  - "3 coverage-gate tests for fault_inject_cycle added (Rule 2) — CLI tests only mock the method, leaving 130 lines uncovered; direct unit tests restore coverage to 71.33%"
  - "Snapshot test test_help_dev updated — new dev subcommands appear in --help output; this is expected"
requirements-completed: [XACT-01, XACT-02]
duration: ~35 minutes
completed: "2026-06-02"
tasks_completed: 3
files_modified: 7
---

# Phase 53 Plan 02: Software Harness GREEN Phase — write_cycle_eprom + fault-inject hooks + dev subcommands

**write_cycle_eprom() (3-way verdict erase→write→read-back→SHA-256 compare), outgoing fault-inject hook (getattr-guarded), FaultInjectingSerialCommunicator subclass, and dev write-cycle/fault-inject Click subcommands — all 12 53-01 RED tests GREEN at 71.33% coverage**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-06-02
- **Completed:** 2026-06-02
- **Tasks:** 3
- **Files modified:** 7 (3 production, 4 test/config)

## Accomplishments

- All 12 RED tests from Plan 53-01 now GREEN (4 write_cycle + 4 fault_inject serial + 4 CLI)
- GATE-1.8d ring-fence compliance test stays GREEN (`_read_and_parse_lines` body SHA-256 unchanged)
- `write_cycle_eprom()` implements erase→write→N read-backs with host-side SHA-256 comparison (D-06) — verbatim reuse of consistency_check_eprom read-back block (D-03)
- `_fault_inject_outgoing` hook in `send_json_command` is getattr-guarded; production frame byte-identical when None (T-53-03)
- `FaultInjectingSerialCommunicator` subclass overrides only `_decode_id_frame` — the ring-fenced `_read_and_parse_lines` body untouched (T-53-04)
- `dev write-cycle` and `dev fault-inject` subcommands wired to operator methods with 3-way verdict passthrough (no bool-to-int wrap)
- Full host suite: 438 passed, 0 failed; coverage 71.33% (floor maintained)

## Task Commits

All commits inside the `firestarter_app/` submodule on `v1.10-serial-transport-hardening`:

1. **Task 1: write_cycle_eprom() write→read-back→compare N-cycle** - `9130e47` (feat)
2. **Task 2: outgoing fault-inject hook + FaultInjectingSerialCommunicator + fault_inject_cycle()** - `088dc2b` (feat)
3. **Task 3: dev write-cycle and dev fault-inject Click subcommands** - `52e3639` (feat)

## Files Created/Modified

- `/workspaces/firestarter_app/firestarter/eprom_operations.py` — `write_cycle_eprom()` (3-way verdict, reuse-not-duplicate read-back) + `fault_inject_cycle()` (outgoing hook + incoming subclass swap)
- `/workspaces/firestarter_app/firestarter/serial_comm.py` — `_fault_inject_outgoing = None` in `__init__`; getattr-guarded hook before `send_bytes` in `send_json_command`; `FaultInjectingSerialCommunicator` subclass
- `/workspaces/firestarter_app/firestarter/cli_handlers.py` — `dev_write_cycle` + `dev_fault_inject` Click subcommands under `dev` group
- `/workspaces/firestarter_app/tests/test_eprom_operations.py` — 3 new `TestFaultInjectCycle` tests (coverage gate, Rule 2 deviation)
- `/workspaces/firestarter_app/tests/conftest.py` — `make_comm` factory mirrors `_fault_inject_outgoing = None`
- `/workspaces/firestarter_app/tests/__snapshots__/test_characterization.ambr` — updated `dev --help` snapshot

## Decisions Made

- **outgoing hook placement:** The `_fault_inject_outgoing` hook is applied INSIDE `_operation_context` after `self.comm` is set by `_setup_operation` (not before), because `self.comm` is None until `SerialCommunicator.find_and_connect` runs. This is the correct production flow.
- **conftest.py mirror:** `make_comm` bypasses `__init__` via `__new__`, so `_fault_inject_outgoing = None` must be explicitly set in the factory to mirror `__init__`. Without this, `test_fault_inject_outgoing_none` would always fail.
- **Coverage gate tests:** 3 direct unit tests for `fault_inject_cycle` added as a Rule 2 deviation — the CLI smoke tests only mock the method; without direct tests the 130-line function would pull total coverage below 70%.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] conftest.py make_comm factory missing _fault_inject_outgoing**
- **Found during:** Task 2 (serial_comm.py + fault-inject tests)
- **Issue:** `make_comm` creates `SerialCommunicator` via `__new__`, bypassing `__init__`. After adding `self._fault_inject_outgoing = None` to `__init__`, the `test_fault_inject_outgoing_none` test's `hasattr(comm, "_fault_inject_outgoing")` assertion still failed because the factory didn't replicate the attribute.
- **Fix:** Added `instance._fault_inject_outgoing = None` to the `_factory()` closure in `conftest.py`, mirroring the `__init__` attribute.
- **Files modified:** `firestarter_app/tests/conftest.py`
- **Verification:** All 5 fault-inject + ring-fence tests pass.
- **Committed in:** `088dc2b` (Task 2 commit)

**2. [Rule 2 - Missing critical functionality] Direct unit tests for fault_inject_cycle (coverage gate)**
- **Found during:** After all 3 tasks, running full suite
- **Issue:** Total coverage dropped to 69.91% (below 70% floor). `fault_inject_cycle()` adds ~130 lines; CLI smoke tests only mock the method at the interface boundary, leaving the function body entirely uncovered.
- **Fix:** Added `TestFaultInjectCycle` class (3 tests) to `test_eprom_operations.py`: outgoing-pass, drop-delimiter, and corrupted-unexpectedly-succeeds (False path). Coverage restored to 71.33%.
- **Files modified:** `firestarter_app/tests/test_eprom_operations.py`
- **Verification:** `pytest --cov-fail-under=70` passes with 71.33% coverage.
- **Committed in:** `9130e47` (Task 1 commit, same file)

**3. [Rule 1 - Bug] Snapshot test_help_dev required update**
- **Found during:** Task 3 full-suite run
- **Issue:** `tests/test_characterization.py::test_help_dev` snapshot failed because `dev --help` now lists `fault-inject` and `write-cycle` subcommands.
- **Fix:** Updated snapshot via `pytest --snapshot-update`. This is expected behavior — the subcommands were intentionally added.
- **Files modified:** `firestarter_app/tests/__snapshots__/test_characterization.ambr`
- **Committed in:** `52e3639` (Task 3 commit)

---

**Total deviations:** 3 auto-fixed (2 Rule 2 missing-critical, 1 Rule 1 expected snapshot update)
**Impact on plan:** All fixes necessary for correctness and coverage floor compliance. No scope creep. Ring-fence constraint honored throughout.

## Threat Surface

No new network endpoints, auth paths, or schema changes. `FaultInjectingSerialCommunicator` is dev-scope only (not exported from `__init__.py`). `_fault_inject_outgoing` defaults to None in production (T-53-03 mitigated).

## Known Stubs

None — all new functions are fully implemented. `fault_inject_cycle()` is functional (not mocked); the CLI tests mock it only for interface testing.

## Self-Check: PASSED

- [x] `firestarter_app/firestarter/eprom_operations.py` contains `def write_cycle_eprom` and `def fault_inject_cycle`
- [x] `firestarter_app/firestarter/serial_comm.py` contains `_fault_inject_outgoing` and `class FaultInjectingSerialCommunicator`
- [x] `firestarter_app/firestarter/cli_handlers.py` contains `write-cycle` and `fault-inject` dev subcommands
- [x] Commits 9130e47, 088dc2b, 52e3639 exist in firestarter_app submodule
- [x] 438 passed, 0 failed; coverage 71.33% >= 70%
- [x] `_read_and_parse_lines` SHA-256 ring-fence test GREEN (GATE-1.8d)
- [x] `ruff check + ruff format --check` clean on all 3 production files
- [x] `mypy` error count = 9 (pre-existing watermark, no new errors introduced)
