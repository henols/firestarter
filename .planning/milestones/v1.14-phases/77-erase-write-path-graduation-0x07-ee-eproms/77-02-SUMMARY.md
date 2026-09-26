---
phase: 77-erase-write-path-graduation-0x07-ee-eproms
plan: 02
subsystem: testing
tags: [0xA4, ack_data, send_ack, write-path, regression, desync]

requires:
  - phase: 77-erase-write-path-graduation-0x07-ee-eproms
    provides: FLAG_CAN_ERASE wiring that makes the no-`-b` write the common path
provides:
  - host-side regression test pinning ack_data=False on INIT/END DATA frames (send_ack once per phase)
affects: [77-04, write-path]

tech-stack:
  added: []
  patterns: [magicmock-side-effect-state-machine-test]

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_eprom_operations.py

key-decisions:
  - "Use fully-mocked comm (MagicMock side_effect DATA,DATA,INIT) and count send_ack directly — no MSG_DATA_PROGRESS constant needed"

patterns-established:
  - "State-machine ack invariants pinned by counting send_ack on a MagicMock comm"

requirements-completed: [ERASE-01]

duration: 4min
completed: 2026-06-22
---

# Phase 77 Plan 02: 0xA4 Write-Path Desync Regression Guard Summary

**A host regression test pins the `ack_data=False` invariant — `_execute_phase("INIT", ...)` fed DATA,DATA,INIT calls `send_ack` exactly once — so the auto-erase default write path cannot silently re-trigger the 0xA4 (MSG_ERR_EMPTY_INPUT) desync.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-06-22T06:52:00Z
- **Completed:** 2026-06-22T06:56:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Added `test_init_phase_data_frames_not_acked`: builds a real `EpromOperator(ConfigManager())`, assigns a `MagicMock` comm with `get_response.side_effect = [DATA "1/128", DATA "64/128", INIT "OK"]`, runs `_execute_phase("INIT", progress)`, and asserts `send_ack.assert_called_once()`.
- Test targets the INIT phase (`ack_data=False`), not MAIN (`ack_data=True`) — Pitfall 5 avoided.
- Docstring cites D-07, commit fcf7974, and that the auto-erase path emits the same blank-check DATA frames this guard protects.

## Task Commits

1. **Task 1: 0xA4 INIT-DATA-not-acked regression test (D-07)** — `5d8a5b1` (test)

(committed inside the `firestarter_app` submodule on branch `v1.14-feasible-gap-implementation`)

## Files Created/Modified
- `firestarter_app/tests/test_eprom_operations.py` — `test_init_phase_data_frames_not_acked` (MagicMock recipe)

## Decisions Made
- None beyond the plan; used the PATTERNS.md "Alternative simpler approach" (MagicMock) as recommended.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None. Test green on first run; ruff clean (`target-version=py39`).

## Next Phase Readiness
- T-77-A4 mitigation locked in software. Plan 04's seated write doubles as the live no-`-b` clean-completion proof.

---
*Phase: 77-erase-write-path-graduation-0x07-ee-eproms*
*Completed: 2026-06-22*
