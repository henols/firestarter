---
phase: 53-byte-exact-bench-verification-hardware-gated
plan: "01"
subsystem: firestarter_app/tests
tags: [tdd, red-scaffold, fault-inject, ring-fence, write-cycle, serial-comm, cli]
dependency_graph:
  requires: []
  provides:
    - "RED test scaffold for write_cycle_eprom 3-way verdict (consumed by 53-02)"
    - "RED test scaffold for SerialCommunicator._fault_inject_outgoing hook (consumed by 53-02)"
    - "RED test scaffold for FaultInjectingSerialCommunicator subclass (consumed by 53-02)"
    - "RED test scaffold for dev write-cycle + dev fault-inject CLI subcommands (consumed by 53-02)"
    - "GREEN ring-fence compliance test pinning _read_and_parse_lines SHA-256 (GATE-1.8d)"
  affects:
    - "firestarter_app/tests/test_eprom_operations.py"
    - "firestarter_app/tests/test_serial_comm.py"
    - "firestarter_app/tests/test_cli_handlers.py"
tech_stack:
  added: []
  patterns:
    - "Monkeypatch-of-operator-internals: _make_fake_ctx + _make_fake_state_machine (mirrors test_consistency_check.py)"
    - "CliRunner smoke test with Mock(spec=EpromOperator) — dev subcommand pattern"
    - "inspect.getsource + SHA-256 ring-fence snapshot test"
    - "__new__ constructor-bypass for SerialCommunicator in fault-inject tests"
key_files:
  created: []
  modified:
    - "firestarter_app/tests/test_eprom_operations.py — added TestWriteCycleEprom class (4 RED tests)"
    - "firestarter_app/tests/test_serial_comm.py — added 4 RED fault-inject + 1 GREEN ring-fence tests"
    - "firestarter_app/tests/test_cli_handlers.py — added 4 RED dev subcommand smoke tests"
decisions:
  - "Ring-fence snapshot captured as SHA-256 digest (not verbatim source string) to keep the test file concise and avoid multi-line raw-string escaping issues"
  - "test_fault_inject_outgoing_none asserts hasattr(_fault_inject_outgoing) so it fails RED before 53-02 adds the attribute to __init__"
  - "Pre-existing I001 ruff warnings in test_eprom_operations.py lines 264/277 are out of scope (Phase 44 code, unrelated to this plan)"
metrics:
  duration: "~20 minutes"
  completed: "2026-06-02"
  tasks_completed: 3
  files_modified: 3
---

# Phase 53 Plan 01: RED Test Scaffold for Byte-Exact Bench Verification Harness Summary

Wave 0 failing-test scaffold for the Phase 53 software harness. 13 new tests across 3 files — 12 RED (fail until 53-02 implementation) and 1 GREEN ring-fence compliance assertion pinning `_read_and_parse_lines` SHA-256 against the GATE-1.8d baseline.

## What Was Built

**Task 1 — TestWriteCycleEprom (test_eprom_operations.py, 4 RED tests):**
- `test_write_cycle_eprom_pass` — monkeypatched erase/write/read-back all OK, payload matches source → asserts return 0
- `test_write_cycle_eprom_mismatch` — read-back payload differs from source → asserts return 1
- `test_write_cycle_eprom_hw_error` — `_run_state_machine` returns `(False, "timeout")` → asserts return 2 (NOT collapsed to 1)
- `test_write_cycle_eprom_erase_fail` — `erase_eprom` returns False → asserts return 2

All four fail RED with `AttributeError: 'EpromOperator' object has no attribute 'write_cycle_eprom'`.

**Task 2 — Fault-inject hooks + ring-fence (test_serial_comm.py, 4 RED + 1 GREEN):**
- `test_fault_inject_outgoing_none` — asserts `hasattr(comm, "_fault_inject_outgoing")` plus no-op frame integrity → fails RED (attribute not declared in `__init__`)
- `test_fault_inject_outgoing_corrupt_crc8` — hook flips `frame[-2]`; asserts CRC mismatch → fails RED (hook not invoked)
- `test_fault_inject_outgoing_drop_delimiter` — hook drops trailing `0x00`; asserts delimiter absent → fails RED (hook not invoked)
- `test_fault_inject_incoming_subclass` — `FaultInjectingSerialCommunicator` one-shot flip; asserts `_fault_fired` flag → fails RED (class not importable)
- `test_read_and_parse_lines_ringfence_unchanged` — SHA-256 of `_read_and_parse_lines` source == pinned digest → **GREEN** (GATE-1.8d enforcement)

Pinned digest: `544433068cb14ac14677939435cb4f0ea78783b503315ed645b5f88c5c44a444` (captured 2026-06-02)

**Task 3 — dev write-cycle / dev fault-inject CLI smoke tests (test_cli_handlers.py, 4 RED):**
- `test_dev_write_cycle_pass` — Mock `write_cycle_eprom` returns 0; invokes `["dev","write-cycle","W27C512",<source>]` → fails RED (Mock spec rejects `write_cycle_eprom`)
- `test_dev_write_cycle_hardware_error` — Mock returns 2; asserts exit 2 NOT 1 → fails RED
- `test_dev_fault_inject_pass` — Mock `fault_inject_cycle` returns True → fails RED (Mock rejects `fault_inject_cycle`)
- `test_dev_fault_inject_fail` — Mock returns False; asserts exit 1 → fails RED

## Test Suite State

Pre-existing tests: **423 passed** (no regressions).
New RED tests: **12 failed** (expected — 53-02 will turn them green).
New GREEN tests: **1 passed** (ring-fence compliance).

## Deviations from Plan

### Auto-fixed Issues

None.

### Minor Design Adjustments

**1. [Rule 2 - Missing critical functionality] `test_fault_inject_outgoing_none` strengthened with `hasattr` assertion**
- **Found during:** Task 2
- **Issue:** The plan's description asked for a test that "fails RED" for the `_fault_inject_outgoing=None` case. Without a formal attribute check, the test would pass even before 53-02 (Python allows arbitrary instance attribute assignment; without the attribute in `__init__`, setting it manually on the instance and sending the command still produces an unmodified frame — which is what the test asserts).
- **Fix:** Added `assert hasattr(comm, "_fault_inject_outgoing")` as the first assertion, making the test fail RED until 53-02 adds `self._fault_inject_outgoing = None` to `SerialCommunicator.__init__`.
- **Files modified:** `firestarter_app/tests/test_serial_comm.py`
- **Commit:** 8983971

**2. Pre-existing ruff I001 warnings in test_eprom_operations.py (lines 264, 277)**
- **Scope:** Pre-existing in Phase 44 code (import-sort warnings in `test_read_timing_*` functions). Not introduced by this plan. Left untouched per scope-boundary rule.
- **Deferred to:** `deferred-items.md` entry for cleanup in a dedicated linting pass.

## Threat Surface

T-53-01 (Tampering — ring-fence): **MITIGATED** — `test_read_and_parse_lines_ringfence_unchanged` is GREEN and pinned. Any future edit to `_read_and_parse_lines` body will fail this test immediately.

T-53-02 (Tampering — monkeypatched class attrs): **ACCEPTED** — pytest `monkeypatch` auto-reverts all patches. No persistent state mutation risk.

## Known Stubs

None — this plan adds tests only; no production stubs introduced.

## Self-Check: PASSED

- [x] `firestarter_app/tests/test_eprom_operations.py` modified (contains `write_cycle` class)
- [x] `firestarter_app/tests/test_serial_comm.py` modified (contains `fault_inject` + `ringfence` tests)
- [x] `firestarter_app/tests/test_cli_handlers.py` modified (contains `write_cycle` + `fault_inject` CLI tests)
- [x] Commits ad434f7, 8983971, 2ff0a7b exist in firestarter_app submodule
- [x] 12 RED + 1 GREEN test count verified
- [x] No production modules modified
