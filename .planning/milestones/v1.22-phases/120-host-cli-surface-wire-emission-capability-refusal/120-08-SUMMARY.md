---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 08
subsystem: cli
tags: [click, sdp, at28c, cli-gates, host-cli]

requires:
  - phase: 120 (plans 01, 02, 06)
    provides: sdp_capability() allow-list predicate, COMMAND_SDP_UNLOCK/LOCK + FLAG_SKIP_SDP_UNLOCK constants, EpromOperator.sdp_lock/sdp_unlock payload-free ops
provides:
  - firestarter dev sdp <chip> <enable|disable> command with D-08's four-gate order
  - D-14 MSG_ERR_UNKNOWN_CMD -> FirmwareOutdatedError mapping
  - D-10 honest, symmetric, duration-free summary line
  - D-11 plain 0/1 exit-code contract
affects: [120-09, 120-10, 121, 122]

tech-stack:
  added: []
  patterns:
    - "click.Choice mode argument instead of a second Click sub-group, to preserve the locked chip-first surface"
    - "Gate-order proof via three independent assertions (no-confirm, no-port-opened, reason-text) instead of exit-code-only refusal tests"

key-files:
  created:
    - firestarter_app/tests/test_dev_sdp_cmd.py
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - .planning/REQUIREMENTS.md

key-decisions:
  - "dev sdp's four gates run in D-08's order (absent -> capability -> support-status -> confirm -> serial), the exact reverse of dev test's in-tree confirm-before-absent-chip ordering"
  - "No --destructive-style mode flag (D-05): the enable/disable subcommand argument IS the mode"
  - "Off-TTY without -y refuses (D-06), inverting dev test's off-TTY-proceeds behaviour, because dev sdp has no flag that could stand in for consent"
  - "One confirm gate, two prompt strings (D-07) rather than two gates"
  - "MSG_ERR_UNKNOWN_CMD is keyed by message id (not text) and mapped to FirmwareOutdatedError naming 'firestarter fw --install' (D-14)"
  - "D-10 summary line uses click.echo, not logger.info, after logger.info proved unreliable under CliRunner capture for a mocked-operator invocation"

requirements-completed: [HOST-01, HOST-05]

coverage:
  - id: D1
    description: "firestarter dev sdp <chip> <enable|disable> command exists on the existing dev group, chip-first mode-second, with -y/--yes and no --destructive-style flag"
    requirement: "HOST-01"
    verification:
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_surface_is_chip_then_mode_with_a_yes_flag"
        status: pass
    human_judgment: false
  - id: D2
    description: "Four gates run in D-08's order (absent-chip, capability, support-status, consent, serial) with no confirm shown and no port opened on any refusal, proven for all nine adapter-required 0x0D parts plus FRAM/pre-SDP/non-0x0D refusals"
    requirement: "HOST-01"
    verification:
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_gate_order_absent_chip_refuses_before_confirm_and_before_serial"
        status: pass
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_gate_order_capability_refusal_refuses_before_confirm_and_before_serial"
        status: pass
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_adapter_required_part_hears_the_capability_reason_not_the_adapter_reason"
        status: pass
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_non_0x0d_chip_is_refused_with_the_wrong_protocol_reason"
        status: pass
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_no_port_opened_on_any_refusal_with_a_real_operator"
        status: pass
    human_judgment: false
  - id: D3
    description: "Consent gate: TTY confirm with -y bypass, off-TTY refuses without -y, decline exits 0, one gate with two mode-specific strings"
    requirement: "HOST-01"
    verification:
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_consent_matrix"
        status: pass
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_enable_and_disable_share_one_gate_with_different_text"
        status: pass
    human_judgment: false
  - id: D4
    description: "MSG_ERR_UNKNOWN_CMD on the SDP path renders as a firmware-too-old refusal naming 'firestarter fw --install'"
    requirement: "HOST-05"
    verification:
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_firmware_too_old_is_reported_when_unknown_cmd_comes_back"
        status: pass
    human_judgment: false
  - id: D5
    description: "Honest, symmetric summary line: unreadable-state caveat on both directions, no duration figure, no fabricated lock/unlock state boolean, plain 0/1 exit with 0x87 WARN staying in text"
    requirement: "HOST-05"
    verification:
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_summary_line_carries_the_unreadable_state_caveat_on_both_directions"
        status: pass
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_summary_line_carries_no_duration_figure"
        status: pass
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_no_fabricated_lock_state_boolean_in_the_report"
        status: pass
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_tblc_warn_prints_at_warning_and_exit_code_stays_zero"
        status: pass
      - kind: unit
        ref: "tests/test_dev_sdp_cmd.py#test_success_exit_zero_and_failure_exit_one"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 08: dev sdp CLI Surface Summary

**`firestarter dev sdp <chip> <enable|disable>` lands D-08's four-gate order (absent → capability → support-status → confirm → serial), with all three deliberate inversions of `dev test`'s analog applied on purpose rather than copied by accident.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-07-29T10:52:00Z (approx.)
- **Completed:** 2026-07-29T11:47:45Z
- **Tasks:** 3
- **Files modified:** 4 (`cli_handlers.py`, new `test_dev_sdp_cmd.py`, `test_characterization.ambr` snapshot, `.planning/REQUIREMENTS.md`)

## Accomplishments

- New `firestarter dev sdp <chip> <enable|disable>` command on the existing `dev` Click group, using a `click.Choice` mode argument (the only form matching the locked chip-first surface — a Click sub-group would have forced `dev sdp enable <chip>`)
- All four D-08 gates in the correct order, with the three deliberate inversions from `dev test`'s nearest analog: gate order reversed (absent-chip hard-fail now precedes the confirm, not the other way around), no `--destructive`-style mode flag (D-05 — the subcommand IS the mode), off-TTY refuses without `-y` (D-06 — `dev test` proceeds off-TTY because its flag is the consent; `dev sdp` has no such flag)
- D-14's `MSG_ERR_UNKNOWN_CMD` → `FirmwareOutdatedError` mapping, keyed on the message id rather than text, naming `firestarter fw --install`
- D-10's honest, symmetric summary line: states the sequence was emitted (never that the resulting state was verified), carries the unreadable-state caveat identically for `enable` and `disable`, and contains no duration figure and no lock/unlock state boolean
- D-11's plain 0/1 exit-code contract: explicit decline exits 0, host-imposed refusal exits non-zero, a `MSG_WARN_SDP_TBLC_EXCEEDED` (`0x87`) frame prints at WARNING without changing the exit code
- 26 new tests in `tests/test_dev_sdp_cmd.py` proving gate order (not just gate presence) via three independent assertions per refusal leg — no-confirm-shown, no-port-opened, and reason text — including all nine `adapter-required` 0x0D parts individually parametrised, and one leg using a **real** `EpromOperator` (not a mock) to prove no port is genuinely opened
- HOST-01 and HOST-05 marked Complete in `.planning/REQUIREMENTS.md`; HOST-02, HOST-04, HOST-06 untouched (still Pending)

## Task Commits

Each task was committed atomically (submodule `firestarter_app`, branch `v1.22-at28c-software-data-protection-lifecycle`):

1. **Task 1: Add the dev sdp handler with D-08's gate order, D-14's mapping, D-10's summary line and D-11's exit code** - `e0582f2` (feat)
2. **Task 2: Prove gate ORDER, not gate presence** - `4bc515d` (test)
3. **Task 3: Prove report honesty and the exit-code contract; then tick HOST-01 and HOST-05** - `3ae0238` (test, submodule) + `ad5e63d` (test, submodule snapshot fix) + `bc9a56e` (docs, meta repo REQUIREMENTS.md)

**Plan metadata:** pending final `docs(120-08): complete dev sdp CLI surface plan` commit (this SUMMARY + STATE.md + ROADMAP.md).

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` - New `dev_sdp` Click command: four gates, D-14 error mapping, D-10 summary line via `click.echo`, plain 0/1 exit
- `firestarter_app/tests/test_dev_sdp_cmd.py` - 26 tests: surface shape, gate-order proofs (absent/capability/adapter-required ×9/non-0x0D), consent matrix, report honesty, exit-code contract, firmware-too-old mapping
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` - Regenerated `test_help_dev` snapshot to include the new `sdp` row
- `.planning/REQUIREMENTS.md` - HOST-01 and HOST-05 ticked Complete with parenthetical detail; HOST-02/04/06 untouched

## Decisions Made

- **`click.Choice` mode argument over a Click sub-group.** The locked surface is `firestarter dev sdp <chip> <enable|disable>` — chip first, mode second. A sub-group (`dev sdp enable <chip>` / `dev sdp disable <chip>`) would put the mode first and violate the locked surface; a single command with a `click.Choice("enable"|"disable")` argument is the only form that matches.
- **Exit-code decisions, settled explicitly (D-11):** operation ran → `sys.exit(0 if ok else 1)`; explicit user decline at the confirm → `sys.exit(0)` (a decline is not an error — the user got what they asked for, mirroring `dev test`'s own decline precedent); host-imposed refusal (absent/capability/support-status/off-TTY-without-`-y`) → non-zero via `click.ClickException`. No tri-state was introduced.
- **D-10's "no duration" property is mechanically enforced, not merely disciplined.** `get_response()` filters the entire INFO band (`NON_RESPONSE_PREFIXES = ["INFO", "DEBUG"]`) out at `serial_comm.py:424`, so the operation layer literally cannot see the firmware's `0x5F`/`0x61` duration frame to plumb a figure through even if someone tried — a test asserting "no duration on the host line" is pinning a structural fact, not a style choice.
- **The unreadable-state caveat is symmetric across both directions on purpose**, because firmware's `0x5F` (`MSG_INFO_SDP_UNLOCK_DONE_US`) frame carries no honesty caveat where `0x61` (`MSG_INFO_SDP_LOCK_DONE_US`) does (F-120-03, deferred catalog fix to Phase 121/122) — the host line is therefore the *only* carrier of the caveat on the unlock direction until that catalog gap closes.
- **D-14 keys on the message id, not the text**, exploiting the one real asymmetry in the wire surface: an unknown *command* produces a detectable error (`MSG_ERR_UNKNOWN_CMD`), whereas an unknown *flag bit* produces silence — which is why the flag half of HOST-06 needs plan 120-09's ack requirement instead of an error-mapping approach.
- **Row 9 of the nine-row CORRECTION-4 gate table was the one host-side gate genuinely at risk in this plan.** `tools/check_devtest_orchestrator.py` scans `cli_handlers.py` (among other files) for the "firmware untouched (host-only, asserted)" claim; this plan edits that exact file. Re-ran both `check_devtest_orchestrator.py` and `tests/test_check_devtest_orchestrator.py` after landing the handler — both green (0 VPP-set, 0 raw-wire-dict, 0 `--force`), confirming nothing in the new command tripped that gate.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `logger.info` did not reliably surface in CliRunner-captured output**
- **Found during:** Task 3 (writing the summary-line honesty tests)
- **Issue:** The D-10 summary line was initially implemented via `logger.info(...)`. Three tests (unreadable-state caveat, no-duration, no-fabricated-state) asserted on `result.output` and failed with an empty string, even though pytest's own log capture showed the record was emitted. A full-wire test using a **real** `EpromOperator` (the `0x87` WARN test) *did* see its `logger.warning` line in `result.output`, but the mocked-operator invocations of the CLI handler's own `logger.info` call did not — an inconsistency traced to how `logging_redirect_tqdm()` and `SingleLineStatusHandler`'s bound stream interact across the two code paths, not fully root-caused given the scope of this plan.
- **Fix:** Switched the D-10 summary line from `logger.info` to `click.echo`, which is unconditionally captured by `CliRunner` regardless of logging configuration or which code path emits it. This matches the plan's own text, which explicitly allowed either ("one `logger.info` (or `click.echo`, whichever the sibling `dev` commands use for user-facing prose)").
- **Files modified:** `firestarter_app/firestarter/cli_handlers.py`
- **Verification:** All three previously-failing tests pass; the full `tests/test_dev_sdp_cmd.py` suite (26 tests) is green.
- **Committed in:** `3ae0238` (Task 3 commit)

**2. [Rule 3 - Blocking] `test_help_dev` snapshot drifted after adding the new subcommand**
- **Found during:** full-suite regression run after Task 3
- **Issue:** `tests/test_characterization.py::test_help_dev` pins a `syrupy` snapshot of `firestarter dev --help`'s rendered output. Adding `sdp` to the `dev` group's command list changed that output by exactly one row, failing the pinned snapshot.
- **Fix:** Regenerated the snapshot via `pytest tests/test_characterization.py::test_help_dev --snapshot-update`; diffed the result to confirm the change is a single added line (`sdp    Enable or disable Software Data Protection (SDP) on...`) with no other drift.
- **Files modified:** `firestarter_app/tests/__snapshots__/test_characterization.ambr`
- **Verification:** `pytest -q` full suite green apart from the pre-existing `test_audit_coverage_matrix` golden-drift RED (named below, not this plan's regression).
- **Committed in:** `ad5e63d`

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking test-snapshot drift)
**Impact on plan:** Both fixes were necessary for the plan's own tests to pass honestly; no scope creep, no behavior beyond what the plan specified.

## Issues Encountered

- **`_setup_operation`/`find_and_connect`'s current architecture cannot actually surface `MSG_ERR_UNKNOWN_CMD` as a raised `EpromOperationError` with `error_code` set in production today.** Tracing the wire path: the first command ack for an unrecognized `cmd` value arrives via `SerialCommunicator._probe_port`'s `expect_ack()` call (serial_comm.py:719), which only raises for `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` — for any other ERROR id (including `MSG_ERR_UNKNOWN_CMD`) it returns `(False, msg)`, causing `_probe_port` to return `None` and `find_and_connect` to eventually raise a bare `ProgrammerNotFoundError` that discards the original message and error code entirely. Separately, `_run_state_machine`'s own `except EpromOperationError` clause (which *would* see an id-carrying exception raised by `_raise_for_error_response` during INIT/MAIN/END) also swallows it into `(False, str(e))`, again losing `error_code`. **Net effect: in the current architecture, `sdp_lock`/`sdp_unlock` cannot actually propagate an `EpromOperationError` with `error_code == MSG_ERR_UNKNOWN_CMD` up to the CLI layer.** This plan's `files_modified` scope is limited to `cli_handlers.py` + the new test file + `REQUIREMENTS.md`, and `serial_comm.py`/`eprom_operations.py` are explicitly the domain of already-landed plans (120-03, 120-06) — so the CLI-side handler was implemented exactly as the plan specifies (a defensive `except EpromOperationError` mapping `error_code == MSG_ERR_UNKNOWN_CMD` to `FirmwareOutdatedError`), and Task 3's test proves that mapping correctly via a **mocked** operator raising the exception directly (as the plan's own action text instructs: "make the operator raise `EpromOperationError` with `error_code` set to `MSG_ERR_UNKNOWN_CMD`"). This is not a regression in this plan — it is a pre-existing wire-level gap that a later plan (likely 120-09 or 120-10, which own HOST-06's closure) will need to address if `MSG_ERR_UNKNOWN_CMD` is meant to reach the CLI in real usage against pre-Phase-119 firmware. Flagging here so it is not silently assumed solved.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `dev sdp` is fully wired and gate-order-proven; plan 120-09 (which closes HOST-02 and HOST-04 for `write --skip-sdp-unlock`) can proceed — it edits the same `cli_handlers.py` but is scoped to the `write` command path, not `dev sdp`, per this plan's own prohibition boundary.
- Plan 120-10 (closing HOST-06) should be aware of the wire-level gap noted above under "Issues Encountered" before relying on `MSG_ERR_UNKNOWN_CMD` reaching any CLI handler in a live run against old firmware.
- Firmware repo (`firestarter/`) confirmed byte-untouched at `0048b3d` throughout this plan.

## Known Stubs

None.

## Threat Flags

None — the four STRIDE threats named in the plan's threat model (T-120-27 through T-120-31) are the surface this plan mitigates directly; no new surface was introduced beyond what the plan specified.

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/cli_handlers.py`
- FOUND: `firestarter_app/tests/test_dev_sdp_cmd.py`
- FOUND (submodule): `e0582f2`, `4bc515d`, `3ae0238`, `ad5e63d`
- FOUND (meta): `bc9a56e`, `24f8ef0`
