---
phase: 206-dev-test-keeps-its-fidelity-on-one-session
plan: 03
subsystem: testing
tags: [dev-test, serial-comm, eprom-operator, session-lease, connect-cost]

requires:
  - phase: 206-02
    provides: "compare_path_tag / StepResult.compare_evidence schema work (DEVTEST-01/02), the frozen 19-case dedup_fingerprint corpus proven unmoved"
provides:
  - "SerialCommunicator.setup_command -- the extracted send/ack/gate half of the cold port probe, callable on an already-open link"
  - "EpromOperator.lease() -- default-off, one call site (cli_handlers.dev_test), holds one validated link across every EpromOperator call inside the block"
  - "The lease's exact revert target: commit 3853b55, machine-verified as touching exactly three paths, revert rehearsed clean"
affects: [206-04-lease-measurement]

actuals:
  tokens: 78000
  tasks: 2
  commits: 3
  plan_head_before: 81ff585

tech-stack:
  added: []
  patterns:
    - "Shared-method extraction with a caller-decides-the-teardown-policy split: setup_command never disconnects on a falsy result, leaving that decision to each of its two callers (_probe_port's port-walk vs. a lease's drop-and-cold-reconnect)"
    - "Default-off feature seam as ONE mechanically-verified commit (git show --name-only pinned to an exact sorted path list), so a structural revert stays a true single-sha take-back rather than an unpick -- mirrors the on_result opt-in precedent from Phase 203"

key-files:
  created:
    - firestarter_app/tests/test_session_lease.py
  modified:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_serial_comm.py
    - firestarter_app/tests/test_hw_revision_gate.py
    - firestarter_app/tests/test_write_verify.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/fake_chip.py

key-decisions:
  - "setup_command's internal is_connected() guard was dropped -- the literal <behavior> prose ('called on a link that is not connected returns falsy') broke 12 pinned tests whose stubbed __init__ never sets self.connection at all. send_bytes already raises SerialError('Not connected.') for that case, unchanged, and both production callers only invoke setup_command on a link they just confirmed open."
  - "The lease commit (3853b55) is machine-verified as EXACTLY three paths (cli_handlers.py, eprom_operations.py, tests/test_session_lease.py). A third, necessary test-infrastructure commit (d723cf7) was deliberately kept separate and landed AFTER the revert rehearsal, so the rehearsal measured the lease commit alone."
  - "Ack-repopulation confirmed complete: _decode_id_frame unconditionally reassigns firmware_max_chunk/hw_revision/firmware_identity/write_block_budget_s on every successfully-decoded MSG_OK_READY on the same live instance -- a second setup_command on an already-open link repopulates all four fields; none goes stale."

requirements-completed: [SESS-01]

coverage:
  - id: D1
    description: "SerialCommunicator.setup_command extracted from _probe_port -- behaviour-identical, permanent regardless of SESS-02's outcome"
    requirement: "SESS-01"
    verification:
      - kind: unit
        ref: "tests/test_serial_comm.py#test_setup_command_is_the_path_the_cold_probe_takes"
        status: pass
      - kind: unit
        ref: "tests/test_serial_comm.py#test_setup_command_refuses_when_the_firmware_gate_fails"
        status: pass
      - kind: unit
        ref: "tests/test_serial_comm.py#test_setup_command_recovers_past_a_spurious_decode_error_frame"
        status: pass
      - kind: integration
        ref: "tests/test_serial_characterization.py (unchanged, passing)"
        status: pass
    human_judgment: false
  - id: D2
    description: "EpromOperator.lease() -- a dev test plan opens one validated serial link and reuses it across its EpromOperator calls, default off, one call site, one revertible commit"
    requirement: "SESS-01"
    verification:
      - kind: unit
        ref: "tests/test_session_lease.py#test_a_leased_plan_opens_one_link_and_a_cold_plan_opens_one_per_call"
        status: pass
      - kind: unit
        ref: "tests/test_session_lease.py#test_the_cold_path_is_byte_identical_when_the_lease_is_never_acquired"
        status: pass
      - kind: unit
        ref: "tests/test_session_lease.py#test_a_leased_setup_drains_input_before_sending_the_setup_command"
        status: pass
      - kind: unit
        ref: "tests/test_session_lease.py#test_a_leased_setup_runs_the_firmware_and_hardware_gates"
        status: pass
      - kind: unit
        ref: "tests/test_session_lease.py#test_a_mid_plan_serial_error_drops_the_lease_and_the_plan_continues"
        status: pass
      - kind: unit
        ref: "tests/test_session_lease.py#test_the_lease_always_disconnects_on_exit"
        status: pass
      - kind: integration
        ref: "tests/test_dev_test_cmd.py (70 tests, unchanged behaviour with the lease active)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The lease is exactly ONE revertible commit; its sha and a clean revert rehearsal are recorded as the SESS-02 revert target"
    requirement: "SESS-01"
    verification:
      - kind: other
        ref: "git show --name-only 3853b55 -- exact 3-path assertion (source-inspection script, see Verification section)"
        status: pass
      - kind: other
        ref: "git revert --no-commit 3853b55 + full suite (2357 passed, 0 failed) on the reverted tree"
        status: pass
    human_judgment: false

duration: 95min
completed: 2026-09-23
status: complete
---

# Phase 206 Plan 03: `setup_command` extracted, then `EpromOperator.lease()` lands default-off, one call site Summary

**`SerialCommunicator.setup_command` is now the shared send/ack/gate half of a connect, callable on an already-open link; `EpromOperator.lease()` uses it to hold one validated serial link across an entire `dev test` plan instead of one open-and-teardown per call — default off, acquired at exactly one call site, and reachable by a single clean `git revert` of commit `3853b55` if SESS-02's bench measurement says it isn't worth keeping.**

## Performance

- **Duration:** ~95 min
- **Started:** 2026-09-23 (continuation of the 206 wave sequence, after 206-02)
- **Completed:** 2026-09-23T10:25:00Z
- **Tasks:** 2 (both `tdd="true"`)
- **Files modified:** 8 (2 production files touched twice each across the two tasks, counted once; 1 new test file; 5 other test files updated as necessary consequences)

## THE LEASE REVERT TARGET (read this first if you are Plan 04)

**Commit `3853b55`** is the entire `EpromOperator.lease()` feature: the `_leased` attribute, `lease()` itself, both conditionals in `_setup_operation`/`_operation_context`, and the one `with app.eprom_operator.lease():` call site in `cli_handlers.dev_test` — together with its own test module, `tests/test_session_lease.py`.

- **Machine-verified exact path list:** `git show --name-only --format= 3853b55` sorts to exactly `firestarter/cli_handlers.py`, `firestarter/eprom_operations.py`, `tests/test_session_lease.py`. No other file is touched by this commit.
- **Revert rehearsed clean, in isolation, before any later commit existed:** `git revert --no-commit 3853b55` applied with **zero conflicts**. The full suite was then run on the reverted tree: **2357 passed, 0 failed** (in 231.99s). The working tree was then restored to its pre-rehearsal state (`git checkout HEAD -- <the 3 paths>` + `git reset`) and the stashed follow-up work was restored.
- **If SESS-02 decides the lease is not worth it:** `git revert 3853b55` is the entire action. It removes the feature, its one call site, and its tests together, with no unpick. A small, separate follow-up commit (`d723cf7`, test-infrastructure only — see Deviations) does **not** need reverting for this to work: none of its changes reference anything that stops existing after the lease is reverted (a `Mock` attribute that is simply never read again, a `FakeChip.lease()` method that is simply never called again). The one exception is `test_write_verify.py`'s `_setup_operation`-return-count pin, which would need manually moving back from `4` to `3` after a real, permanent revert — this was NOT re-tested as part of the rehearsal above (the rehearsal predates `d723cf7`), so **Plan 04 or a future revert must account for this one pin by hand** if the revert is made permanent.

## Accomplishments

- `SerialCommunicator.setup_command` extracted from `_probe_port` (`fa6c8e8`): the setup-command send, the ack read (including the spurious-decode-error recovery window bounded by `SETUP_ACK_RECOVERY_TIMEOUT_S`), and both the firmware-version and hardware-revision gates, now callable standalone on an already-open, connected link. `_probe_port` delegates to it and keeps only the port-walk policy (candidate iteration, disconnect-and-try-next-port) for itself. Behaviour-identical: `test_serial_characterization.py` passes unmodified.
- `EpromOperator.lease()` (`3853b55`): a `@contextmanager` that holds one validated link open across every `EpromOperator` call made inside the block. Default off (`_leased` starts `False`); `_setup_operation` takes the leased branch only when a lease is active AND the held link is still connected, draining pending input via `consume_remaining_input()` before every leased setup and running both validation gates through `setup_command` unconditionally.
- D-06 failure policy: a `SerialError` raised while a leased setup is in flight (including a gate refusal — `FirmwareOutdatedError`/`HardwareRevisionUnsupportedError` are `SerialError` subclasses) drops the held link (`_disconnect_programmer()`) but leaves `_leased` set, so the NEXT operation cold-connects instead of the whole plan failing. The exception still propagates to the caller unchanged.
- Acquired at exactly one call site: `cli_handlers.dev_test` wraps its `run_plan(...)` call in `with app.eprom_operator.lease():`. `HardwareManager`'s own connects (the pre-plan identity read, the voltage sampler) are untouched (D-05), capping the measurable saving — stated here rather than discovered at the bench.
- Ack-repopulation finding recorded (see below): a second `setup_command` on the same link correctly repopulates all four `_decode_id_frame`-set fields.
- All six `test_session_lease.py` legs assert both the cold path and the leased path, per the plan's own hard requirement — no test in the suite passes only under a lease.

## Ack-repopulation finding (Task 1 requirement)

`_decode_id_frame` (`firestarter/serial_comm.py:335-415`) is an **instance method**, not a one-shot initializer. It unconditionally reassigns `self.firmware_max_chunk`, `self.hw_revision`, `self.firmware_identity`, and `self.write_block_budget_s` every time it successfully decodes an `MSG_OK_READY` id frame — which happens on every `expect_ack()` call via `get_response()` → `_read_and_parse_lines()` → this override, regardless of how many times it has already run on the same `SerialCommunicator` instance. Evidence: none of the four assignments is guarded by "if this is the first time" or by any `is None` check; each is set directly off the freshly-decoded `params_bytes` of the CURRENT ack.

**Conclusion: a second `setup_command` call on the same already-open link repopulates all four fields correctly from the fresh ack.** None goes stale under a lease. This was the load-bearing precondition for Task 2's design — if any field went stale, a leased plan's later steps could act on outdated firmware/hardware identity, which the plan's `<behavior>` explicitly forbids.

## Task Commits

Each task was committed atomically (both `tdd="true"`; RED transcripts below):

1. **Task 1: extract `setup_command` from the port probe** — `fa6c8e8` (feat, tdd) — includes `tests/test_hw_revision_gate.py`'s one-line fix (see Deviations)
2. **Task 2: `EpromOperator.lease()`** — `3853b55` (feat, tdd) — **the SESS-02 revert target**, machine-verified as exactly 3 paths
3. **Follow-up: test infrastructure catch-up** — `d723cf7` (test) — deliberately separate from commit 2 (see Deviations)

**Plan metadata:** (this commit, following)

## RED transcripts

**Task 1** (`tests/test_serial_comm.py`, run against the source BEFORE the extraction, via a temporary `git stash` of `serial_comm.py`):
```
FAILED tests/test_serial_comm.py::test_setup_command_is_the_path_the_cold_probe_takes
FAILED tests/test_serial_comm.py::test_setup_command_refuses_when_the_firmware_gate_fails
FAILED tests/test_serial_comm.py::test_setup_command_recovers_past_a_spurious_decode_error_frame
======================= 3 failed, 44 deselected in 0.11s =======================
```
All three failed with `AttributeError: 'SerialCommunicator' object has no attribute 'setup_command'` — the intended reason (the method genuinely did not exist). After the extraction, all three pass.

**Task 2** (`tests/test_session_lease.py`, run against the source BEFORE `lease()` existed, via a temporary `git stash` of `eprom_operations.py`/`cli_handlers.py`):
```
FAILED tests/test_session_lease.py::test_a_leased_plan_opens_one_link_and_a_cold_plan_opens_one_per_call
FAILED tests/test_session_lease.py::test_the_cold_path_is_byte_identical_when_the_lease_is_never_acquired
FAILED tests/test_session_lease.py::test_a_leased_setup_drains_input_before_sending_the_setup_command
FAILED tests/test_session_lease.py::test_a_leased_setup_runs_the_firmware_and_hardware_gates
FAILED tests/test_session_lease.py::test_a_mid_plan_serial_error_drops_the_lease_and_the_plan_continues
FAILED tests/test_session_lease.py::test_the_lease_always_disconnects_on_exit
============================== 6 failed in 0.17s ===============================
```
Five failed with `AttributeError: 'EpromOperator' object has no attribute 'lease'`; the one test that never calls `.lease()` directly (`test_the_cold_path_is_byte_identical_when_the_lease_is_never_acquired`) failed with `AttributeError: 'EpromOperator' object has no attribute '_leased'` — both the intended reason. After landing `lease()`/`_leased`, 5 of 6 passed immediately; the sixth (`test_a_leased_setup_drains_input_before_sending_the_setup_command`) needed one iteration fix — its assertion was originally placed AFTER the `with operator.lease():` block closed, so it picked up the lease's own exit `disconnect` event. Moved the assertion inside the block (before exit); all 6 then passed.

## Files Created/Modified

- `firestarter_app/firestarter/serial_comm.py` — `setup_command` extracted; `_probe_port` delegates to it
- `firestarter_app/firestarter/eprom_operations.py` — `_leased` attribute, `lease()`, the leased branch in `_setup_operation`, the conditional teardown in `_operation_context`
- `firestarter_app/firestarter/cli_handlers.py` — `dev_test` wraps `run_plan(...)` in `with app.eprom_operator.lease():`
- `firestarter_app/tests/test_serial_comm.py` — 3 new legs for `setup_command`
- `firestarter_app/tests/test_session_lease.py` — new, 6 legs, every one asserting both the cold and leased path
- `firestarter_app/tests/test_hw_revision_gate.py` — one-line fix (Deviation 2)
- `firestarter_app/tests/test_write_verify.py` — return-count pin 3→4 (Deviation 3)
- `firestarter_app/tests/test_dev_test_cmd.py` — 6 `Mock(spec=EpromOperator)` builders configured for `.lease()` (Deviation 4)
- `firestarter_app/tests/fake_chip.py` — `FakeChip.lease()` no-op contextmanager (Deviation 4)

## Decisions Made

See `key-decisions` in the frontmatter, and the "THE LEASE REVERT TARGET" section above for the full reasoning behind keeping the lease commit exactly 3 paths.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `setup_command`'s internal `is_connected()` guard was dropped**
- **Found during:** Task 1, full-suite verification after the extraction
- **Issue:** Task 1's `<behavior>` prose states `setup_command` called on a link that is not connected should return falsy rather than raising. Implementing this literally (`if not self.is_connected(): return False` at the top of `setup_command`) broke 12 existing tests across `test_hw_revision_gate.py`, `test_fw_update_path_gate.py`, and `test_fwguard.py`: all 12 patch `SerialCommunicator.__init__` to a fully-stubbed no-op lambda that never sets `self.connection` at all (relying on `_probe_port`'s ORIGINAL inline code never referencing `self.connection` directly — every interaction was through mocked methods). `is_connected()` raised `AttributeError: 'SerialCommunicator' object has no attribute 'connection'` on these doubles.
- **Fix:** Removed the internal connectivity guard from `setup_command`. Documented in its docstring that `send_bytes` already raises `SerialError("Not connected.")` for that case — pre-existing, unchanged behaviour — and that both production callers (`_probe_port` on a communicator it just constructed; the lease's setup site on `self.comm` after its own `is_connected()` check) only ever invoke `setup_command` on a link already confirmed open, so "not connected" reaching here at all is already a caller bug, not a state this method needs to anticipate silently.
- **Files modified:** `firestarter_app/firestarter/serial_comm.py`
- **Verification:** Full suite green (2363 passed after all 3 commits)
- **Committed in:** `fa6c8e8` (Task 1 commit)

**2. [Rule 1 - Stale pin] `test_hw_revision_gate.py`'s `_probe()` helper needed `port_name`**
- **Found during:** Task 1, full-suite verification after the extraction
- **Issue:** `setup_command`'s logging and `config_manager.remember_port(...)` call read `self.port_name` (the extraction moved that code out of `_probe_port`'s own local-variable closure, where it read the `port_name` parameter directly). `test_hw_revision_gate.py`'s `_probe()` helper stubs `__init__` as `lambda self, port, **k: None`, which never set `self.port_name` — 2 tests failed with `AttributeError: 'SerialCommunicator' object has no attribute 'port_name'`.
- **Fix:** One-line change: `lambda self, port, **k: setattr(self, "port_name", port)`.
- **Files modified:** `firestarter_app/tests/test_hw_revision_gate.py`
- **Verification:** All 50 tests in the 3 affected modules pass
- **Committed in:** `fa6c8e8` (Task 1 commit)

**3. [Rule 1 - Stale pin] `test_write_verify.py`'s exactly-three-`(None, 0)`-returns pin**
- **Found during:** Task 2, full-suite verification after the lease landed
- **Issue:** `_setup_operation`'s new leased-setup-rejected-ack arm returns `(None, 0)` too (deliberately, "treated identically to a cold connect failure" per the plan's own action text), moving the count from 3 to 4. `test_setup_operation_has_exactly_three_none_zero_returns` asserted `== 3` and failed with `assert 4 == 3`.
- **Fix:** Updated the assertion to `== 4` and extended the docstring to name the new arm and why it is classified the same way as a cold connect failure (the caller cannot and need not tell the two apart).
- **Files modified:** `firestarter_app/tests/test_write_verify.py`
- **Verification:** Test passes; no other assertion in the module depends on the old count
- **Committed in:** `d723cf7` (follow-up commit — kept separate from the lease commit; see "THE LEASE REVERT TARGET" above for why)

**4. [Rule 3 - Blocking] `Mock(spec=EpromOperator)`/`FakeChip` test doubles needed `.lease()` support**
- **Found during:** Task 2, full-suite verification after the lease landed
- **Issue:** `cli_handlers.dev_test` now unconditionally wraps `run_plan(...)` in `with app.eprom_operator.lease():`. `Mock(spec=EpromOperator)`'s auto-created `.lease` attribute is a plain `Mock`, not a `MagicMock`, and does not support the context-manager protocol — every `dev test` CLI test using a `Mock(spec=EpromOperator)` operator (6 construction sites in `test_dev_test_cmd.py`) raised `TypeError: 'Mock' object does not support the context manager protocol`. `FakeChip` (the hand-written stateful double) had no `.lease` attribute at all and raised `AttributeError`.
- **Fix:** (a) All 6 `Mock(spec=EpromOperator)` construction sites in `test_dev_test_cmd.py` now set `operator.lease.return_value = contextlib.nullcontext()`. (b) `FakeChip.lease()` added as a no-op `@contextmanager` (`yield` with no side effects), matching its existing "duck-types the whole `EpromOperator` surface" convention. The one `Mock(spec=EpromOperator)` construction site that hard-fails BEFORE reaching the lease (the chip-not-found test) needed no change.
- **Files modified:** `firestarter_app/tests/test_dev_test_cmd.py`, `firestarter_app/tests/fake_chip.py`
- **Verification:** `test_dev_test_cmd.py` — 70 passed
- **Committed in:** `d723cf7` (follow-up commit, deliberately separate from the lease's own 3-path commit — see "THE LEASE REVERT TARGET" above)

---

**Total deviations:** 4 auto-fixed (2 Rule 3 - blocking, 2 Rule 1 - stale pin).
**Impact on plan:** All four are necessary consequences of extracting `setup_command` (deviations 1-2) and landing `lease()` at its one call site (deviations 3-4). No scope creep: no file outside the transport (deviation 1-2) or outside test infrastructure reacting to the new call site (deviation 3-4) was touched. Deviations 3-4 are the reason a THIRD commit exists, and its separation from the lease's own commit is itself a deliberate, documented choice preserving the exact-3-path revert-target property the plan requires.

## Issues Encountered

None beyond the deviations above. The revert rehearsal (see "THE LEASE REVERT TARGET") surfaced the ordering requirement — rehearse before the follow-up commit lands — which is now recorded as a note for anyone reverting `3853b55` permanently: `test_write_verify.py`'s pin must be moved back to `3` by hand in that case, since the rehearsal (performed before `d723cf7` existed) does not cover that interaction.

## Verification

- `pytest tests/test_serial_comm.py tests/test_serial_characterization.py -o addopts="" -p no:cacheprovider -q` — 51 passed
- `pytest tests/test_session_lease.py -o addopts="" -p no:cacheprovider -v` — 6 passed, each asserting both arms
- `pytest tests/test_dev_test_cmd.py tests/test_serial_comm.py tests/test_serial_characterization.py -o addopts="" -p no:cacheprovider -q` — 121 passed
- AST structural check (Task 1): `setup_command` fully annotated, `_probe_port` delegates to it, recovery constant moved — confirmed
- AST structural check (Task 2): `lease` is a contextmanager, `_leased` initialised in `__init__`, `_operation_context`'s `finally` references `_leased`, exactly one `.lease()` acquisition in `cli_handlers.py` — confirmed
- Exact-path check on `fa6c8e8`: does not touch `eprom_operations.py`/`cli_handlers.py`/`hardware.py` — confirmed
- Exact-path check on `3853b55`: touches exactly `cli_handlers.py`, `eprom_operations.py`, `tests/test_session_lease.py` — confirmed
- `git revert --no-commit 3853b55` + full suite on the reverted tree: applied cleanly, 2357 passed, 0 failed — confirmed, then restored
- `pytest tests/ -o addopts="" -p no:cacheprovider -q` (final, all 3 commits applied) — **2363 passed, 0 failed** (2354 at plan 02's close + 9: 3 `setup_command` tests + 6 lease tests)
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` — both clean
- `mypy firestarter/serial_comm.py firestarter/cli_handlers.py` — clean (both are mypy-strict-island modules; `eprom_operations.py` is deliberately excluded from the island per D-07/GATE-1.8d)
- Every `<automated>` leg ran through `/workspaces/firestarter_app/.venv311/bin/python`

## Threat Flags

None beyond what the PLAN's `<threat_model>` already declared and this plan's tasks mitigated (T-206-04, T-206-02, T-206-05, T-206-12, T-206-13, T-206-SC). No new report field, no new wire constant, no firmware change of any kind — confirmed by the exact-path checks above (neither `constants.py` nor any firmware header appears in either commit's diff).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 04 (the bench measurement) can proceed: the lease's revert target sha (`3853b55`) is recorded above, its revert has been rehearsed clean, and the ack-repopulation precondition Task 2 depended on is confirmed correct.
- **Read "THE LEASE REVERT TARGET" section above before running Plan 04's bench measurement or its possible revert** — it names the one hand-fix (`test_write_verify.py`'s return-count pin) a PERMANENT revert would additionally need, beyond a plain `git revert 3853b55`.
- No blockers. Full host suite green (2363 passed), `ruff`/`mypy` clean, both structural gates (exact-path, revert-rehearsal) passed.

## Self-Check: PASSED

- `firestarter_app/firestarter/serial_comm.py` — FOUND (modified)
- `firestarter_app/firestarter/eprom_operations.py` — FOUND (modified)
- `firestarter_app/firestarter/cli_handlers.py` — FOUND (modified)
- `firestarter_app/tests/test_session_lease.py` — FOUND (created)
- `firestarter_app/tests/test_serial_comm.py` — FOUND (modified)
- `firestarter_app/tests/test_hw_revision_gate.py` — FOUND (modified)
- `firestarter_app/tests/test_write_verify.py` — FOUND (modified)
- `firestarter_app/tests/test_dev_test_cmd.py` — FOUND (modified)
- `firestarter_app/tests/fake_chip.py` — FOUND (modified)
- Commit `fa6c8e8` — FOUND in `git log --oneline --all`
- Commit `3853b55` — FOUND in `git log --oneline --all`
- Commit `d723cf7` — FOUND in `git log --oneline --all`
- `git show --name-only 3853b55` exact-path list — CONFIRMED (3 paths, matches plan)
- Revert rehearsal (`git revert --no-commit 3853b55` + full suite) — CONFIRMED clean, then restored
- Full host suite — 2363 passed, 0 failed

---
*Phase: 206-dev-test-keeps-its-fidelity-on-one-session*
*Completed: 2026-09-23*
