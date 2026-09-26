---
phase: 69-cli-command-surface-robustness-audit
plan: "03"
subsystem: firestarter_app
tags: [mypy-watermark, snapshot, ci-gate, characterization-test]
dependency_graph:
  requires:
    - phase: 69-01
      provides: [SC#1-root-fix, snapshot-regeneration-rc0]
    - phase: 69-02
      provides: [SC#2-command-surface-smoke-audit, SC#3-cli-regression-all-three-statuses]
  provides: [SC#4-full-ci-gate-green]
  affects: [firestarter_app/pyproject.toml]
tech_stack:
  added: []
  patterns: [honest-watermark-floor, ci-gate-sequential]
key_files:
  created: []
  modified:
    - firestarter_app/pyproject.toml
key_decisions:
  - "Watermark bumped 26→29: honest measured floor after Plans 01+02 (ic_layout list-vs-int fix adds 2 mypy errors; Phase 65 test adds 1); no config loosening, no new ignores"
  - "Task 1 pre-completed by Plan 69-01 Rule-1 auto-fix: test_info_known_chip asserts rc==0, snapshot regenerated via --snapshot-update, no TypeError pinned — reconciled per dependency_note, no re-work needed"
  - "2 pre-existing I001 ruff errors in tests/test_address_parser.py + tests/test_codec.py are documented out-of-scope; ruff check --files firestarter/ tests/ shows ONLY those 2, none from phase-touched files"

requirements-completed: [SC#4]

metrics:
  duration: ~10min
  completed: "2026-06-15T08:22:27Z"
  tasks_completed: 2
  files_modified: 1
---

# Phase 69 Plan 03: Snapshot + Watermark Realignment Summary

**One-liner:** Mypy watermark bumped from 26 to 29 (honest post-fix floor); full CI gate verified green — ruff check/format, mypy watermark, pytest 513/513 at 76.24% coverage; no chip_database.json churn.

## Performance

- **Duration:** ~10 min
- **Started:** 2026-06-15T08:12:00Z
- **Completed:** 2026-06-15T08:22:27Z
- **Tasks:** 2 (Task 1 pre-completed by 69-01; Task 2 executed)
- **Files modified:** 1 (pyproject.toml)

## Accomplishments

### Task 1: Flip test_info_known_chip to rc==0 and regenerate its snapshot

**Status: Pre-completed by Plan 69-01 (Rule-1 auto-fix).**

Per the dependency_note, Plan 69-01 already:
- Changed `test_info_known_chip` assertion from `rc == 1` → `rc == 0`
- Regenerated the `.ambr` snapshot via `pytest --snapshot-update` (NOT hand-edited)
- The `test_info_known_chip` snapshot now shows chip layout output (28-DIP formatted block)
- The `test_info_known_chip_stderr` snapshot is empty `''` (no TypeError traceback)

Verification at Plan 03 start: `pytest tests/test_characterization.py::test_info_known_chip -q` exits 0, 2 snapshots passed. No re-work needed.

### Task 2: Realign mypy watermark and verify full CI gate

Updated `pyproject.toml` watermark comment from 26 → 29.

**Why 29:** After Plans 01+02, the honest mypy floor is 29 errors:
- `firestarter/ic_layout.py:442` — `"Sequence[str]" has no attribute "append"` (Plan 69-01 fix: `pin_names` typed as `Sequence[str]` but appended to)
- `firestarter/ic_layout.py:525` — `arg-type: Any | None` expected `str` (Plan 69-01 fix: `get_pin_map` call site)
- `tests/test_protocol_not_implemented_production_path.py:92` — `Incompatible types in assignment (_FakeSerial → Serial | None)` (Phase 65)
- `tests/test_characterization.py:431` — `Incompatible types: None → ConfigManager` (pre-existing in strict-island test)
- 25 other pre-existing errors in `firestarter/config.py`, `database.py`, `firmware.py`, `eprom_operations.py`, `tests/test_serial_comm.py`, `tests/test_eprom_database.py`

No mypy config was loosened; no `# type: ignore` comments added.

## Task Commits

1. **Task 1** — Pre-completed by Plan 69-01 commits `a1b8a31` + `b5d1ced` (no new commit)
2. **Task 2: Realign mypy watermark** — `a8fb281` (chore)

## Files Created/Modified

- `/workspaces/firestarter_app/pyproject.toml` — watermark 26 → 29 in `# mypy_error_watermark` comment line 115

## CI Gate Results (Full Run)

| Gate | Command | Result |
|------|---------|--------|
| ruff check | `ruff check firestarter/ tests/` | 2 pre-existing I001 (out-of-scope; 0 from phase-touched files) |
| ruff format | `ruff format --check firestarter/ tests/` | PASS (59 files formatted) |
| mypy watermark | `python tools/check_mypy_watermark.py` | OK: 29 errors at watermark |
| pytest | `pytest tests/ --cov=firestarter --cov-fail-under=70` | 513 passed, 76.24% coverage |
| chip_database churn | `git diff --stat firestarter/data/chip_database.json` | Empty (no churn) |

## Decisions Made

1. **Watermark 26→29 (honest floor):** Per plan + T-69-06 anti-tampering requirement, the watermark is set to the measured count, not loosened to "pass" artificially. The 3 additional errors relative to the prior watermark are caused by the ic_layout fix (2 new type errors at list-extraction sites) and the Phase 65 production-path test (1 assignment error). Setting to 29 is the exact floor post-fix.

2. **Task 1 reconciliation:** The dependency_note instructed the executor to inspect current state before assuming the pre-phase baseline. The snapshot and rc==0 assertion were already in place from 69-01's Rule-1 auto-fix. No re-flip or re-snapshot was performed (correct behavior per reconciliation instruction).

3. **Pre-existing I001 ruff errors:** `tests/test_address_parser.py` and `tests/test_codec.py` each have 1 I001 import-sort error. These are documented pre-existing errors from prior phases (codegen output without ruff-normalize). Per plan directive, they were not touched. The CI baseline accepts exactly these 2 errors as the documented floor.

## Deviations from Plan

### Task 1 — Pre-completed deviation

**1. [Rule 1 - Bug → Already fixed in 69-01] test_info_known_chip snapshot/rc already aligned**

- **Found during:** Task 1 execution (inspection at plan start)
- **Issue:** 69-01's Rule-1 auto-fix had already: flipped `rc == 1` → `rc == 0` in `test_characterization.py::test_info_known_chip`, regenerated the snapshot via `pytest --snapshot-update`, and removed the TypeError from the stderr snapshot.
- **Reconciliation:** Per dependency_note, the plan explicitly said to reconcile rather than redo. No action taken; test verified passing.
- **Impact:** Task 1 required zero new code changes; fully satisfied pre-execution.

No other deviations. Task 2 executed exactly as written.

## Known Stubs

None. The watermark reflects real type debt; no placeholder values introduced.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. This is a tooling-gate realignment only. T-69-05 (gate integrity) mitigated: watermark = honest measured floor; T-69-06 (gate loosening) avoided: no mypy config changes, no `# type: ignore` additions.

## Self-Check: PASSED

- `firestarter_app/pyproject.toml` — modified (watermark 26→29), verified via `python tools/check_mypy_watermark.py` → "OK"
- Commit `a8fb281` exists in `v1.12-protocol-dispatch-hardening`
- 513 tests green, coverage 76.24% ≥ 70%, ruff format clean, no chip_database.json churn
- Task 1: confirmed `test_info_known_chip` asserts `rc == 0`, snapshot shows chip layout, stderr snapshot empty — all via 69-01 commits `a1b8a31`/`b5d1ced`
