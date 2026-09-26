---
phase: 121-dev-test-fix-gates-docs-redesign
plan: 04
subsystem: testing
tags: [pytest, monkeypatch, serial-comm, characterization, hardening]

# Dependency graph
requires:
  - phase: 121-01
    provides: baseline test suite green (1064 passed) and pyproject ruff extend-exclude
provides:
  - Hardened no_programmer_found_read/erase characterization tests that patch the real port-enumeration seam
  - Negative-call proof (serial.Serial.assert_not_called()) as the load-bearing assertion instead of the return value alone
affects: [121-14]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Patch the real production seam (SerialCommunicator._list_potential_ports, raising=True), not a downstream call it happens to route through (comports())"
    - "Negative-call assertion (mock.assert_not_called()) as the load-bearing proof for absent-hardware characterization tests, per the read_hardware_revision_value.assert_not_called() precedent"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_characterization.py

key-decisions:
  - "D-19 (operator-authorised scope addition, recorded the same way Phase 119 recorded its cross-family regression sweep): hardened both no_programmer_found tests against a live board / saved config port defeat vector, outside the phase's nine tracked requirements"
  - "Kept the comports() monkeypatch alongside the new _list_potential_ports patch (belt and suspenders / documents original intent) rather than removing it"

patterns-established:
  - "Absent-hardware characterization tests must patch the seam that decides the candidate port list (_list_potential_ports), and must assert the mock was never called — a comports()-only patch and a bare `result is False` assertion are both insufficient"

requirements-completed: []  # GATE-03 CONTRIBUTES ONLY here — closed by plan 121-14, not this plan. Per plan frontmatter and requirement_ownership block, this plan may mark nothing Complete.

coverage:
  - id: D1
    description: "test_no_programmer_found_read and test_no_programmer_found_erase patch SerialCommunicator._list_potential_ports (raising=True) instead of relying solely on serial.tools.list_ports.comports"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_characterization.py::test_no_programmer_found_read"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_characterization.py::test_no_programmer_found_erase"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both tests assert serial.Serial (MagicMock) was never called — the negative-call proof, not the False return value"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_characterization.py::test_no_programmer_found_read (mock_serial.assert_not_called())"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_characterization.py::test_no_programmer_found_erase (mock_serial.assert_not_called())"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 04: Harden no-programmer-found characterization tests Summary

**Both `no_programmer_found` characterization tests now patch `SerialCommunicator._list_potential_ports` (the real port-enumeration seam) with `raising=True` and assert `serial.Serial` was never called, closing the defeat vector where a live board or a saved config `"port"` value could sneak a candidate port past a `comports()`-only monkeypatch.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-29T17:20:00Z (approx)
- **Completed:** 2026-07-29T17:46:10Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Reproduced the defeat vector with a throwaway (uncommitted) probe script: with `FIRESTARTER_CONFIG_DIR` pointed at a temp dir containing `{"port": "/dev/ttyACM0"}` and `serial.tools.list_ports.comports` patched to return `[]`, `SerialCommunicator._list_potential_ports(preferred_port)` still returned `["/dev/ttyACM0"]` — proving a `comports()`-only patch is defeated by a saved config port. Confirmed via direct call, output: `potential ports (comports patched to []): ['/dev/ttyACM0']`.
- Checked the current devcontainer's actual state at time of the run: `ConfigManager().get_value("port")` returned `None` (no saved port on this bench today), but `ls /dev/ttyACM* /dev/ttyUSB*` showed real attached devices: `/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` (an extra ACM1 appeared between the reproduction probe and the final check — device set is not perfectly static in this container). The reproduction therefore used a simulated saved-port config rather than relying on today's environment, per the plan's explicit instruction not to treat "it passes now" as proof.
- Patched both `test_no_programmer_found_read` and `test_no_programmer_found_erase`:
  - Added `monkeypatch.setattr("firestarter.serial_comm.SerialCommunicator._list_potential_ports", lambda preferred_port=None: [], raising=True)` — the load-bearing patch, `raising=True` so a future rename of the method fails loudly.
  - Kept the pre-existing `serial.tools.list_ports.comports` patch (belt and suspenders, documents original intent).
  - Added a `MagicMock()` patched onto `firestarter.serial_comm.serial.Serial`, with `mock_serial.assert_not_called()` after each operation — the load-bearing negative-call proof that no port was ever opened, since `result is False` alone cannot distinguish "no programmer found" from "found a real board and it refused".
  - Rewrote the section-header comment above both tests to explain that `_list_potential_ports` prepends `preferred_port` (from `config_manager.get_value("port")`) before ever calling `comports()`, so a saved config port defeats a `comports`-only patch, and that the negative-call assertion — not the return value — is what proves the no-programmer-found path.
- Ran the adversarial proof required by the acceptance criteria: temporarily changed the `_list_potential_ports` stub in both tests to return `["/dev/ttyNONEXISTENT0"]`, re-ran `pytest -k no_programmer_found`, and confirmed **both** tests failed with `AssertionError` on `mock_serial.assert_not_called()` (captured log: `WARNING ... Timeout waiting for a response from /dev/ttyNONEXISTENT0.`), proving the negative-call assertion is load-bearing. Restored the original file from a pre-edit backup afterward; `git diff` confirms the bogus-path edit left no trace in the committed version.
- Verified `git status --porcelain` was clean of the temporary adversarial edit before staging/committing.

## Task Commits

Each task was committed atomically:

1. **Task 1: Reproduce the defeat vector, then patch the real port-enumeration seam** - `1fdb369` (test) — repo: `firestarter_app`, branch `v1.22-at28c-software-data-protection-lifecycle`

**Plan metadata:** this SUMMARY commit (meta repo)

## Files Created/Modified
- `firestarter_app/tests/test_characterization.py` - Both `no_programmer_found_read`/`no_programmer_found_erase` tests now patch `SerialCommunicator._list_potential_ports` (raising=True) and assert `serial.Serial` (MagicMock) was never called; updated in-source comment explaining the real seam and the negative-call proof.

## Decisions Made
- D-19: recorded as an operator-authorised scope addition outside the phase's nine tracked requirements (GATE-03, DEVTEST-01..08 etc.) — same shape as Phase 119's cross-family regression sweep. GATE-03 is listed in this plan's `requirements` frontmatter solely because the hardening strengthens GATE-03's sweep credibility; GATE-03 itself is closed by plan 121-14, not here.
- Kept both the `comports()` patch and the new `_list_potential_ports` patch rather than removing the former, per the plan's explicit "belt and suspenders" instruction.

## Deviations from Plan

None - plan executed exactly as written. The throwaway reproduction probe and the adversarial-proof edit were both explicitly required by the plan's task action/acceptance criteria and were not committed (verified via `git status --porcelain` and `git show --stat HEAD` showing exactly one file).

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

- Both `no_programmer_found` tests are now defeat-proof against a live board or a saved config port; GATE-03's later "green" run therefore carries a stronger proof (green WITH hardware attached) than a quiet/detached bench would.
- Plan 121-14 owns final GATE-03 requirement-row closure across all contributing plans (121-01, this plan, 121-14) — no action needed here.
- Full suite verified GREEN: `1064 passed` (baseline unchanged — 2 existing tests hardened in place, no new test functions added), 0 failed, with hardware attached (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`).
- `ruff check tests/` and `ruff format --check tests/` both exit 0 on the modified file.

## Self-Check: PASSED
- FOUND: firestarter_app/tests/test_characterization.py contains `_list_potential_ports` monkeypatch and `assert_not_called()` in both tests (verified via grep post-commit).
- FOUND: commit `1fdb369` exists in `firestarter_app` git log (`git log --oneline --all | grep 1fdb369`).
- FOUND: `git -C /workspaces/firestarter_app show --stat HEAD` lists exactly one file: `tests/test_characterization.py`.

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*
