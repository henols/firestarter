---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 10
subsystem: host-cli
tags: [python, click, serial-protocol, sdp, wire-flags, host-firmware-contract]

# Dependency graph
requires:
  - phase: 120 (Plan 03)
    provides: "_log_rurp_feedback INFO-band promotion (untouched by this plan)"
  - phase: 120 (Plan 06)
    provides: "sdp_unlock/sdp_lock payload-free ops, keyword-only skip_sdp_unlock in build_flags"
  - phase: 120 (Plan 08)
    provides: "D-14 MSG_ERR_UNKNOWN_CMD -> firmware-too-old CLI mapping; carried-forward finding re: error-propagation swallow"
  - phase: 120 (Plan 09)
    provides: "write --skip-sdp-unlock CLI surface, D-18 warn-and-proceed for non-0x0D chips, D-04 auto-set"
  - phase: 119
    provides: "MSG_WARN_SDP_UNLOCK_SKIPPED (0x86) firmware ack, tip 0048b3d"
provides:
  - "SerialCommunicator.seen_message_ids: bounded per-connection record of every decoded frame id"
  - "write_eprom D-15 check: requires 0x86 ack when FLAG_SKIP_SDP_UNLOCK set on a protocol-0x0D write, fails loudly when absent"
  - "HOST-06 closed: all six HOST-01..HOST-06 requirements now Complete"
affects: [121-devtest-and-gates, 122-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bounded observed-id record via the _decode_id_frame override seam (Phase 55 firmware_max_chunk precedent), never a whitelist, never sized from frame content"
    - "Detect-after-the-fact ack requirement in place of a version floor, when the host cannot observe the firmware pre-release suffix"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/test_eprom_operations.py
    - firestarter_app/tests/conftest.py
    - firestarter_app/tests/test_serial_comm.py
    - firestarter_app/tests/test_write_skip_sdp_unlock.py
    - firestarter_app/tests/test_protocol_not_implemented_production_path.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "D-15: write_eprom requires firmware's MSG_WARN_SDP_UNLOCK_SKIPPED (0x86) ack when FLAG_SKIP_SDP_UNLOCK was set; absence fails the write loudly and names `firestarter fw --install`"
  - "D-15 scoped to protocol 0x0D only (mirroring 120-09's is_protocol_0x0d/D-18 predicate): firmware only reads the flag bit and only emits 0x86 on 0x0D writes, so requiring the ack on any other protocol would be a false positive"
  - "D-16: no version floor introduced; the sequencing invariant (firmware Phase 119 tip 0048b3d, host Phase 120) is recorded as a fact with commit provenance instead of gated by a version comparator"
  - "seen_message_ids records EVERY decoded id, not a whitelist of interesting ones, via the same _decode_id_frame override seam Phase 55 already uses for firmware_max_chunk"

requirements-completed: [HOST-06]

coverage:
  - id: D1
    description: "Bounded per-connection seen_message_ids record populated through the _decode_id_frame override seam"
    requirement: "HOST-06"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#test_seen_message_ids_records_decoded_ids_and_stays_bounded"
        status: pass
      - kind: unit
        ref: "tests/test_serial_comm.py + tests/test_decoder.py (full suite)"
        status: pass
    human_judgment: false
  - id: D2
    description: "write_eprom fails loudly when --skip-sdp-unlock was set on a 0x0D chip and firmware never acked (0x86 absent)"
    requirement: "HOST-06"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#test_missing_sdp_ack_fails_the_write_loudly"
        status: pass
    human_judgment: false
  - id: D3
    description: "Converse leg: ack present produces no complaint and an unchanged successful result"
    requirement: "HOST-06"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#test_sdp_ack_honoured_produces_no_complaint"
        status: pass
    human_judgment: false
  - id: D4
    description: "Not-set leg: flag not set means the check never runs, regardless of ack presence"
    requirement: "HOST-06"
    verification:
      - kind: unit
        ref: "tests/test_eprom_operations.py#test_ack_check_does_not_run_when_the_flag_was_not_set"
        status: pass
    human_judgment: false
  - id: D5
    description: "HOST-06 requirement ticked with D-14/D-15/D-16 asymmetry, limitation, and landing-order provenance recorded"
    requirement: "HOST-06"
    verification:
      - kind: other
        ref: ".planning/REQUIREMENTS.md HOST-06 row (manual diff review)"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 10: 0x86 Ack Requirement for --skip-sdp-unlock Summary

**`write_eprom` now requires firmware's `MSG_WARN_SDP_UNLOCK_SKIPPED` (0x86) ack when `--skip-sdp-unlock` was set on a protocol-0x0D chip, failing loudly when it never arrives — closing HOST-06 by exploiting the detectability asymmetry between an unknown command (loud error) and an unknown flag bit (silence).**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-07-29T12:31Z
- **Tasks:** 3
- **Files modified:** 8 (2 production, 5 test, 1 planning doc)

## Accomplishments

- `SerialCommunicator.seen_message_ids`: a bounded `set[int]`, populated per-connection through the already-documented `_decode_id_frame` override seam (the same seam Phase 55 uses for `firmware_max_chunk`). Every successfully decoded frame id is recorded unconditionally — no whitelist, nothing sized from frame content.
- `write_eprom` now checks, inside the `_operation_context` `with` block (before `_disconnect_programmer()` runs), whether `FLAG_SKIP_SDP_UNLOCK` was set **and** the chip is protocol 0x0D. If so, it requires `MSG_WARN_SDP_UNLOCK_SKIPPED` (`0x86`) to be present in `seen_message_ids`. Absence forces the write to fail and logs a plain report: the opt-out was requested, firmware did not acknowledge it, the unlock ran anyway, and `firestarter fw --install` is the remedy.
- The check is explicitly scoped to protocol 0x0D, mirroring plan 120-09's `is_protocol_0x0d` predicate (D-18): firmware only reads the flag bit — and only ever emits `0x86` — on 0x0D writes, so an unscoped check would misfire (false positive) on every legitimate non-0x0D `--skip-sdp-unlock` write, which 120-09's own tests already exercise and correctly expect to succeed.
- Four new tests: both ack directions, the flag-not-set case, and a direct proof that `seen_message_ids` is a bounded set of integers that a dropped unknown id never enters.
- HOST-06 ticked with the full asymmetry (D-14 command / D-15 flag), the honest "detects, does not prevent" limitation, and D-16's landing-order fact with commit provenance (firmware Phase 119 tip `0048b3d`, `version.h` still `3.0.0b11`, host Phase 120). All six HOST-01..HOST-06 requirements now read Complete.

## Task Commits

Firestarter_app submodule (branch `v1.22-at28c-software-data-protection-lifecycle`):

1. **Task 1: Record observed message ids in the `_decode_id_frame` override seam** - `a9db4d8` (feat)
2. **Task 2: Require the 0x86 ack in write_eprom when the flag was set** - `da001f4` (feat)
   - Follow-up fix (found while running Task 3's verification): `dfe70e3` (fix) — corrected the protocol-0x0D scoping predicate's key name and, in the same commit, added Task 3's new test module and the two other test-infrastructure mirror sites (see Deviations). The bundling was incidental (staged together before commit), not a design choice.
3. **Task 3: Test both ack directions + not-set case; tick HOST-06** - test content landed inside `dfe70e3` above (git staging bundled it with the Task 2 fix commit rather than a separate commit).

**Plan metadata:** committed separately via the meta-repo's final docs commit (SUMMARY.md, STATE.md, ROADMAP.md, REQUIREMENTS.md).

## Files Created/Modified

- `firestarter_app/firestarter/serial_comm.py` - adds `seen_message_ids: set[int]`, populated in `_decode_id_frame`
- `firestarter_app/firestarter/eprom_operations.py` - `write_eprom`'s D-15 ack-required check, scoped to protocol 0x0D
- `firestarter_app/tests/test_eprom_operations.py` - 4 new tests (additions only, verified via `git diff --stat`)
- `firestarter_app/tests/conftest.py` - `make_comm` factory mirrors the new `seen_message_ids` attribute (bypasses `__init__`)
- `firestarter_app/tests/test_serial_comm.py` - `FaultInjectingSerialCommunicator` raw `__new__` test site mirrors the new attribute
- `firestarter_app/tests/test_write_skip_sdp_unlock.py` - `_drive_write` helper now feeds the 0x86 ack for protocol-0x0D chips (real post-Phase-119 firmware behavior its fake stream had not modeled)
- `firestarter_app/tests/test_protocol_not_implemented_production_path.py` - 4 raw `__init__`/`__new__`-bypass sites mirror the new attribute
- `.planning/REQUIREMENTS.md` - HOST-06 ticked, traceability row Complete; HOST-01..HOST-05 untouched

## Decisions Made

- **D-15** (this plan): require the `0x86` ack; absence fails the write loudly, presence/not-set is a no-op. Detects after the fact, does not prevent — stated in-source and in REQUIREMENTS.md.
- **D-16** (this plan): no version floor. The landing-order invariant is recorded as fact (firmware Phase 119 `0048b3d`, host Phase 120, `version.h` unbumped at `3.0.0b11`), not enforced by a comparator the host cannot evaluate correctly (the pre-release suffix is invisible to `_probe_port`'s regex).
- **Protocol-0x0D scoping** (deviation from the plan's literal, unscoped wording — see below): the D-15 check only fires when `eprom_data_dict.get("algorithm") == SDP_PROTOCOL_ID (13)`. Required for correctness (firmware never emits `0x86` outside 0x0D) and to avoid regressing plan 120-09's already-landed non-0x0D `--skip-sdp-unlock` warn-and-proceed tests.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] D-15 check needed protocol-0x0D scoping, not the plan's literal unscoped wording**
- **Found during:** Task 2, confirmed by Task 3's verification run
- **Issue:** The plan's `<action>` text for Task 2 describes the check firing whenever `FLAG_SKIP_SDP_UNLOCK` is set, with no protocol condition. Implementing it literally broke 5 pre-existing, already-landed tests in `tests/test_write_skip_sdp_unlock.py` (plan 120-09): those tests set the flag on non-0x0D chips (D-18's own warn-and-proceed contract) and expect a normal successful exit, because firmware never reads the bit — and therefore never emits `0x86` — outside protocol 0x0D. An unscoped check is a false positive on every such write.
- **Fix:** Added `is_protocol_0x0d = eprom_data_dict.get("algorithm") == SDP_PROTOCOL_ID` (mirroring 120-09's own `is_protocol_0x0d` predicate in `cli_handlers.py`, imported from `firestarter.sdp_capability` rather than from the forbidden `cli_handlers.py`) and gated the ack requirement on it.
- **Files modified:** `firestarter/eprom_operations.py`
- **Verification:** Full `test_write_skip_sdp_unlock.py` + `test_eprom_operations.py` suites pass.
- **Committed in:** `da001f4` (initial, using the wrong key `protocol-id`), corrected in `dfe70e3`

**2. [Rule 1 - Bug] Wrong dict key for the protocol-0x0D predicate (`protocol-id` vs `algorithm`)**
- **Found during:** Task 3 verification, running `test_write_skip_sdp_unlock.py`
- **Issue:** `write_eprom`'s `eprom_data_dict` parameter, as actually called from `cli_handlers.py`, is `resolve_chip()`'s composed programmer dict, which carries the protocol id under the key `"algorithm"` (per `firestarter_app/CLAUDE.md`: "the `algorithm` field carries the upstream `protocol_id` integer"). The raw db-row key `"protocol-id"` belongs to a *different* dict (`app.db.get_eprom()`'s entry), which is what 120-09's own `cli_handlers.py` D-18 check reads. Using `"protocol-id"` on `resolve_chip()`'s output always returned `None`, so the scoping predicate was permanently `False` and the check never ran on any chip.
- **Fix:** Switched to `eprom_data_dict.get("algorithm")`.
- **Files modified:** `firestarter/eprom_operations.py`
- **Verification:** `test_missing_sdp_ack_fails_the_write_loudly` now correctly returns `False`.
- **Committed in:** `dfe70e3`

**3. [Rule 1 - Bug] Four pre-existing test-infrastructure sites bypass `SerialCommunicator.__init__` and needed the new attribute mirrored**
- **Found during:** Task 1 verification (`test_serial_comm.py`/`test_decoder.py`), then again running the full suite
- **Issue:** `tests/conftest.py`'s `make_comm` factory, `tests/test_serial_comm.py`'s `FaultInjectingSerialCommunicator` raw `__new__` construction, and three `mock_init`/`_make_fake_comm` sites in `tests/test_protocol_not_implemented_production_path.py` all construct `SerialCommunicator` instances via `__new__`/monkeypatched `__init__`, bypassing the real `__init__` and therefore never getting `seen_message_ids`. `_decode_id_frame` unconditionally calls `self.seen_message_ids.add(msg_id)`, so any decoded frame on these instances raised `AttributeError`.
- **Fix:** Added `instance.seen_message_ids = set()` (or `comm.seen_message_ids = set()`) at each site, mirroring the existing `firmware_max_chunk = None` mirror lines already present for the same reason.
- **Files modified:** `tests/conftest.py`, `tests/test_serial_comm.py`, `tests/test_protocol_not_implemented_production_path.py`
- **Verification:** Full test suite green except the known pre-existing `test_audit_coverage_matrix.py` RED.
- **Committed in:** `a9db4d8` (conftest.py + test_serial_comm.py, part of Task 1), `dfe70e3` (test_protocol_not_implemented_production_path.py, found later during the full-suite run)

**4. [Rule 1 - Bug] `test_write_skip_sdp_unlock.py`'s `_drive_write` helper needed to feed the 0x86 ack for 0x0D chips, at the correct phase position**
- **Found during:** Task 3 verification
- **Issue:** `_drive_write`'s fake frame stream (`INIT_DONE -> OK_REQ_DATA -> MAIN_DONE -> END_DONE`) predates the D-15 ack requirement and never fed `0x86`, so its 0x0D-chip legs (which set `FLAG_SKIP_SDP_UNLOCK`, explicitly or via D-04 auto-set) started failing once the ack check went live. Additionally, the first attempt to feed the ack placed it between `INIT_DONE` and `OK_REQ_DATA` — inside the MAIN phase's tight request/response loop — which raised `EpromOperationError` because `_main_phase_send_data` only tolerates `MAIN`/`ERROR`/OK-request-chunk responses, not an interleaved `WARN`.
- **Fix:** `_drive_write` now feeds `MSG_WARN_SDP_UNLOCK_SKIPPED` *before* `INIT_DONE` (inside the INIT phase window, which tolerates WARN via `_handle_progress_response`) whenever the driven chip resolves to protocol 0x0D — matching real post-Phase-119 firmware behavior. The same ordering was used in this plan's own new `test_eprom_operations.py` tests.
- **Files modified:** `tests/test_write_skip_sdp_unlock.py`
- **Verification:** All 7 tests in that module pass, including the 3 that previously regressed.
- **Committed in:** `dfe70e3`

---

**Total deviations:** 4 auto-fixed (all Rule 1 — bugs directly caused by this task's own change interacting with pre-existing code/tests)
**Impact on plan:** All four were necessary for correctness or to avoid regressing already-landed, in-scope-adjacent tests. No scope creep beyond what was required to make the D-15 check both correct and non-regressive; `cli_handlers.py` and the firmware repo remain untouched.

## Issues Encountered

**Carried-forward finding from 120-08 (`EpromOperationError`/`MSG_ERR_UNKNOWN_CMD` swallowed twice in `_probe_port`'s `expect_ack()` and `_run_state_machine`'s except clause):** assessed and **not** addressed by this plan (branch (b) per the dispatch instructions). This plan's D-15 mechanism is a wholly separate seam — it never raises or catches `EpromOperationError`; it reads a bounded observed-id set populated by `_decode_id_frame` and checks it after `_run_state_machine` returns, regardless of how that method internally handles exceptions. Repairing the double-swallow would require touching `_probe_port` (explicitly forbidden by this plan's prohibitions, since it borders the ring-fenced version-capture path) and/or `_run_state_machine`'s except clause (outside this plan's task list). Recorded here as an explicit, actionable follow-up for plan 120-12's non-regression pass or a later phase:
- **File/function 1:** `firestarter/serial_comm.py`, `SerialCommunicator.find_and_connect` → `_probe_port`'s `expect_ack()` call — swallows `EpromOperationError` carrying `error_code == MSG_ERR_UNKNOWN_CMD` at probe time.
- **File/function 2:** `firestarter/eprom_operations.py`, `EpromOperator._run_state_machine`'s `except EpromOperationError as e:` clause — swallows the same error class a second time, converting it to a plain `(False, str(e))` tuple rather than letting plan 120-08's CLI-side D-14 mapping see the real exception.
- **Net effect (unchanged by this plan):** D-14's CLI mapping is currently only exercised via a mocked operator raising `EpromOperationError` directly; the real wire-to-CLI propagation path for an unknown command is still dead in production.

No other issues.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HOST-06 closed; all six HOST-01..HOST-06 requirements for phase 120 now read Complete.
- Firmware repo (`firestarter/`) remains byte-untouched at tip `0048b3d`, `version.h` still `3.0.0b11` — confirmed via `git status --porcelain` (empty) and `git rev-parse HEAD`.
- Carried-forward finding on the double-swallowed `EpromOperationError`/`MSG_ERR_UNKNOWN_CMD` propagation path remains open; flagged above for plan 120-12 or a later phase.
- Full `firestarter_app` test suite green apart from the pre-existing, out-of-scope `test_audit_coverage_matrix.py::test_golden_file_matches` RED (stale golden, 186034 vs 184631 bytes) — not a regression from this plan.

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/serial_comm.py
- FOUND: firestarter_app/firestarter/eprom_operations.py
- FOUND: firestarter_app/tests/test_eprom_operations.py
- FOUND: .planning/REQUIREMENTS.md
- FOUND: .planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-10-SUMMARY.md
- FOUND commit a9db4d8 (firestarter_app)
- FOUND commit da001f4 (firestarter_app)
- FOUND commit dfe70e3 (firestarter_app)
- FOUND commit d057e4f (meta repo, this SUMMARY)

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*
