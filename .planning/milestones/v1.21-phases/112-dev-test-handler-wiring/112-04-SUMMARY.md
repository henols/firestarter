---
phase: 112-dev-test-handler-wiring
plan: 04
subsystem: cli
tags: [click, cli-handlers, diagnostic-report, hardware, provenance-descope, python]

# Dependency graph
requires:
  - phase: 112-02
    provides: "dev_test handler wiring (derive_plan -> run_plan -> DiagnosticReport -> render/artifacts -> exit code) with prompt_provenance/Provenance/hardcoded-None auto-capture fields as originally landed"
  - phase: 112-03
    provides: "SAFE-03 checker repointed at cli_handlers.py::dev_test, dedicated CliRunner test module test_dev_test_cmd.py"
  - phase: 110-diagnostic-report-model
    provides: "DiagnosticReport/AutoCapture/TransportHealth/DbDiff, prompt_provenance, is_submittable (the model this plan reworks)"
provides:
  - "Auto-capture-only diagnostic report model: AutoCapture.hw_revision field, is_submittable(ac) derived purely from auto-capture completeness, no Provenance concept anywhere"
  - "HardwareManager.read_hardware_revision_value() -- value-returning sibling of get_hardware_revision(), the auto-capture source for hw_revision"
  - "Prompt-free dev_test handler: the ONLY interactive input remaining is the --destructive safety confirm (SAFE-03); zero tester-input prompts"
affects: [113-submission-flow, phase-111-sc2-bench-reverify]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Value-returning hardware read sibling: read_hardware_revision_value() mirrors get_hardware_revision()'s exact find_and_connect -> expect_ack -> disconnect handshake but returns the string instead of only logging it (same relationship sample_vpp_mv bears to read_vpp_voltage) -- established in Phase 111, reused here for a third HardwareManager field."
    - "Docstring/comment wording must avoid literal reintroduced-symbol substrings when a test/verify script does inspect.getsource() substring scanning (Phase 109/110 lesson, re-applied here for prompt_provenance/Provenance/SHIELD_REV_CHOICES/_CHIP_ORIGIN_CHOICES mentions in prose)."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/hardware.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_provenance.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_diagnostic_report.py

key-decisions:
  - "REVERSAL (operator-approved per 112-UAT.md test 2): the entire interactive tester-input-collection model (RPT-04, D-04/D-05/D-06) is removed. prompt_provenance(), the Provenance dataclass, and SHIELD_REV_CHOICES/_CHIP_ORIGIN_CHOICES are deleted outright, not deprecated -- their choice strings contained a path-separator character that collided with rich.prompt.Prompt.ask's own separator-rendered choice display, rejecting natural inputs like new/used/2.0."
  - "is_submittable(ac: AutoCapture) redefined on auto-capture completeness only: bool(chip) and bool(protocol) and bool(host_version). hw_revision and fw_board_identity are informational-best-effort and deliberately excluded from the gate -- an honest None on either must never flip an otherwise-complete report to not-submittable."
  - "fw_board_identity sourcing decision: stays None (honest not-measured), NOT populated-from-X. Re-confirmed (not newly discovered) that EpromOperator.comm is torn down (self.comm = None) inside _operation_context's disconnect after every single operator call -- by the time dev_test regains control after run_plan returns, there is no live comm.programmer_info to read. FirmwareManager.check_current_firmware() was evaluated as an alternative source and rejected: it opens its OWN fresh SerialCommunicator.find_and_connect connection, which is exactly the extra/extraneous connection the orchestrator-only (SAFE-02) contract forbids. No orchestrator-safe source yields version:board without an extra connection; this exhausts the reachable host-side identity sources per the plan's requirement before accepting None."
  - "hw_revision IS populated (unlike fw_board_identity) via a NEW, orchestrator-safe value-returning HardwareManager.read_hardware_revision_value() -- a dedicated, purpose-built energize/query read (one serial connection, no VPP-set, no wire-dict, no --force), distinct from the transient per-EPROM-op comm object. This is the key structural difference: hw_revision has its own clean acquisition path; fw_board_identity's only live source is entangled with the destructive per-operation connection lifecycle."
  - "--pot-adjusted flag: explicitly OUT OF SCOPE for this plan (confirmed, not implemented) -- a possible future addition per the operator's own descope rationale (112-UAT.md), not reintroduced here in any form, no prompt, no flag stub."
  - "_is_uv_eprom() and its _PROTOCOL_UV_EPROM module constant deleted as dead code -- their only caller was prompt_provenance's owns_eraser gate, confirmed via grep before removal."
  - "Pre-existing, environment-specific test failures (test_characterization.py::test_no_programmer_found_read/erase) are NOT introduced by this plan -- reproduced identically at the pre-Task-1 base commit (8f59374) in isolation. Root cause: real bench hardware (/dev/ttyACM0) is reachable in this devcontainer session (per project MEMORY.md's USB-passthrough note), so SerialCommunicator.find_and_connect succeeds despite the test's serial.tools.list_ports.comports() monkeypatch. Logged here rather than silently ignored, in addition to the plan's documented test_audit_coverage_matrix.py pre-existing failure."

patterns-established:
  - "A report's submittability gate must only ever depend on fields that are ALWAYS auto-capturable and never on a field whose honest value is None/absent by design -- gating on an optional informational field would make a good report artificially non-submittable."

requirements-completed: [RPT-04, SAFE-03, VOLT-01, XPORT-01]

coverage:
  - id: D1
    description: "prompt_provenance(), Provenance dataclass, SHIELD_REV_CHOICES, _CHIP_ORIGIN_CHOICES fully deleted from diagnostic_report.py; is_submittable(ac) redefined on AutoCapture completeness only"
    requirement: "RPT-04"
    verification:
      - kind: unit
        ref: "tests/test_provenance.py::test_no_interactive_provenance_symbols, tests/test_provenance.py::test_is_submittable_auto_capture_only"
        status: pass
      - kind: other
        ref: "grep -rn 'prompt_provenance|SHIELD_REV_CHOICES|_CHIP_ORIGIN_CHOICES|class Provenance' firestarter/ -- 0 hits"
        status: pass
    human_judgment: false
  - id: D2
    description: "dev_test handler issues zero interactive tester-input prompts; the --destructive safety confirm (SAFE-03) is preserved unchanged in behavior"
    requirement: "SAFE-03"
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestPromptGating (test_off_tty_no_confirm_prompt, test_on_tty_destructive_confirm_gates, test_on_tty_declining_confirm_aborts_before_write, test_yes_bypasses_confirm_on_a_tty)"
        status: pass
      - kind: other
        ref: "python tools/check_devtest_orchestrator.py (exits 0, scans cli_handlers.py::dev_test)"
        status: pass
    human_judgment: false
  - id: D3
    description: "AutoCapture.hw_revision added and auto-captured via new HardwareManager.read_hardware_revision_value(); flows through _auto_capture_dict()/to_dict()/render() single-source"
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "tests/test_provenance.py::test_hw_revision_auto_captured, tests/test_dev_test_cmd.py::TestPromptGating::test_hw_revision_auto_captured_end_to_end"
        status: pass
    human_judgment: false
  - id: D4
    description: "fw_board_identity sourcing exhausted (FirmwareManager.check_current_firmware rejected as an extraneous-connection source) and honestly left None; protocol populated from the DB-derived algorithm string (unchanged from 112-02)"
    requirement: "XPORT-01"
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py (existing D-04/D-05 sampler + artifact tests unaffected; auto_capture.protocol still asserted populated)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Full tooling gate green: ruff check/format on the 6 changed files, mypy strict on cli_handlers.py, mypy watermark, pytest with coverage >= 70%"
    verification:
      - kind: unit
        ref: "cd firestarter_app && ruff check firestarter/diagnostic_report.py firestarter/hardware.py firestarter/cli_handlers.py tests/test_provenance.py tests/test_dev_test_cmd.py tests/test_diagnostic_report.py && python -m mypy firestarter/cli_handlers.py && python tools/check_mypy_watermark.py"
        status: pass
      - kind: unit
        ref: "cd firestarter_app && python -m pytest tests/ -q --cov=firestarter --cov-fail-under=70 (80.66% coverage; 3 pre-existing unrelated failures, none introduced by this plan)"
        status: pass
    human_judgment: false

# Metrics
duration: 40min
completed: 2026-07-03
status: complete
---

# Phase 112 Plan 04: Descope Interactive Provenance, Auto-Capture-Only Model Summary

**Deleted `dev test`'s four interactive provenance prompts (the `/`-in-choice-string bug that rejected `new`/`used`/`2.0`), replaced them with firmware-auto-captured `hw_revision`, and redefined `is_submittable` on auto-capture completeness only -- the `--destructive` SAFE-03 safety confirm is untouched.**

## Performance

- **Duration:** 40 min
- **Started:** 2026-07-03T10:40:00Z
- **Completed:** 2026-07-03T11:20:00Z
- **Tasks:** 3
- **Files modified:** 6 (3 source, 3 test)

## Accomplishments

- **Deleted the entire interactive tester-input-collection surface** from `diagnostic_report.py`: `prompt_provenance()`, the `Provenance` dataclass, and the `SHIELD_REV_CHOICES`/`_CHIP_ORIGIN_CHOICES` module constants are gone. The choice strings contained a `/` character that collided with `rich.prompt.Prompt.ask`'s own `/`-separated choice-list rendering, silently rejecting natural inputs like `new`, `used`, `2.0` -- this was the UAT's reported "trigger bug."
- **Added `AutoCapture.hw_revision: str | None`** (coarse silkscreen-bucket string or honest `None`), surfaced through `_auto_capture_dict()`, `to_dict()`, and `render()` -- the single-source `to_dict()` -> `render()`/`to_json_block()` invariant (RPT-01) is preserved; no second hand-maintained field list was introduced.
- **Redefined `is_submittable(ac: AutoCapture) -> bool`** on auto-capture completeness only (`chip` + `protocol` + `host_version` all present). No human-provenance field gates it anymore. `hw_revision`/`fw_board_identity` are deliberately excluded from the gate -- an honest `None` on either must never make an otherwise-complete report non-submittable.
- **Added `HardwareManager.read_hardware_revision_value()`** -- a value-returning sibling of `get_hardware_revision()`, mirroring the `sample_vpp_mv`/`_sample_one_voltage` pattern established in Phase 111. Reuses the exact `find_and_connect -> expect_ack -> disconnect` handshake but returns the revision string (or `None` on any transport error) instead of only logging it. Does not change `get_hardware_revision`'s existing bool contract (`dev hw` still depends on it).
- **Reworked the `dev_test` handler**: removed the `prompt_provenance()` call and both TTY/off-TTY `Provenance` branches; `DiagnosticReport(...)` no longer takes a `provenance=` argument. The `--destructive` TTY confirm (SAFE-03) is preserved byte-for-byte in behavior -- it is a safety gate, not provenance, and stays the ONLY interactive input in the handler. Deleted the now-dead `_is_uv_eprom()` helper and `_PROTOCOL_UV_EPROM` constant (their only caller was the deleted `owns_eraser` gate). `AutoCapture` is now constructed with `hw_revision=app.hardware_manager.read_hardware_revision_value()`.
- **Rewrote all three affected test modules** for the new model: `test_provenance.py` fully rewritten (auto-capture flow-through, honest-None, auto-capture-only submittability, reintroduction guard); `test_dev_test_cmd.py`'s `TestPromptGating` reworked to test only the `--destructive` confirm plus a new end-to-end `hw_revision` wiring test; `test_diagnostic_report.py`'s three provenance-composition tests replaced with one auto-capture-derived-submittability test.

## Task Commits

Each task committed atomically inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`):

1. **Task 1: Descope the Provenance model, rework diagnostic_report.py to auto-capture-only submittability** - `18baa91` (feat)
2. **Task 2: Wire auto-capture into dev_test, add value-returning hardware-revision helper** - `2e41622` (feat)
3. **Task 3: Rewrite test_provenance.py and update dev-test/report tests for the auto-capture-only model** - `37fe93d` (test)

**Plan metadata:** (this commit, meta-repo) — docs: complete plan

## Files Created/Modified

- `firestarter_app/firestarter/diagnostic_report.py` — Deleted `prompt_provenance()`, `Provenance`, `SHIELD_REV_CHOICES`, `_CHIP_ORIGIN_CHOICES`; added `AutoCapture.hw_revision`; redefined `is_submittable(ac)`; removed `DiagnosticReport.provenance` field, `_provenance_dict()`, and the provenance rows in `to_dict()`/`render()`. Removed the now-unused `rich.prompt` import.
- `firestarter_app/firestarter/hardware.py` — Added `HardwareManager.read_hardware_revision_value()`.
- `firestarter_app/firestarter/cli_handlers.py` — Removed the provenance-prompt call/branches and `Provenance`/`prompt_provenance` imports; removed dead `_is_uv_eprom()`/`_PROTOCOL_UV_EPROM`; kept the `--destructive` confirm unchanged; populated `AutoCapture.hw_revision` from the new hardware helper.
- `firestarter_app/tests/test_provenance.py` — Fully rewritten for the auto-capture-only model.
- `firestarter_app/tests/test_dev_test_cmd.py` — `TestPromptGating` reworked to `--destructive`-confirm-only tests; `make_hardware_manager` now stubs `read_hardware_revision_value`; report-keys assertion drops `provenance`, adds `hw_revision` check; new end-to-end hw_revision test.
- `firestarter_app/tests/test_diagnostic_report.py` — Replaced the three provenance-composition tests with `test_is_submittable_derived_from_auto_capture`; `_build_report`'s `AutoCapture` now carries `hw_revision`; renamed the four-sub-objects end-to-end test to reflect provenance's removal.

## Decisions Made

See `key-decisions` in frontmatter for the full list. Highlights:

- **RPT-04 / D-04 / D-05 / D-06 reversal** (operator-approved per `112-UAT.md` test 2): the interactive provenance model is deleted, not deprecated or feature-flagged. The root cause was a `/`-in-choice-string collision with `rich.prompt.Prompt.ask`'s own separator rendering, compounded by every question being either firmware/DB-queryable or self-reported-and-unverifiable.
- **`fw_board_identity` sourcing decision (explicitly required by the plan): stays `None`, honestly.** This is a RE-CONFIRMATION of 112-02's original finding, not a new discovery — `EpromOperator.comm` is torn down (`self.comm = None`) inside `_operation_context`'s `disconnect()` after every single operator call, so by the time `dev_test` regains control after `run_plan` returns, there is no live `comm.programmer_info` to read. This plan additionally evaluated `FirmwareManager.check_current_firmware()` as a candidate alternative source and rejected it: that method opens its OWN fresh `SerialCommunicator.find_and_connect` connection — exactly the extra, unaccounted-for hardware touch the orchestrator-only (SAFE-02) contract forbids. No orchestrator-safe source yields `version:board` without an extra connection.
- **`hw_revision` IS populated** (in contrast to `fw_board_identity`) because it has its own dedicated, purpose-built acquisition path (`read_hardware_revision_value()`) — a single clean energize/query connection, structurally decoupled from the destructive per-EPROM-operation connection lifecycle that entangles `fw_board_identity`.
- **`--pot-adjusted` flag: confirmed out of scope**, not implemented in any form (no flag stub, no prompt, no dead code referencing it).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Reworded module/section docstrings to avoid literal reintroduced-symbol substrings**
- **Found during:** Task 1 verification
- **Issue:** The plan's own verify script does `inspect.getsource(module)` and asserts `'prompt_provenance' not in src`. My first-draft docstrings explaining the reversal literally quoted the deleted symbol names (`prompt_provenance()`, `SHIELD_REV_CHOICES`, `_CHIP_ORIGIN_CHOICES`) in prose, which made the substring-scan verify script fail even though the actual code was correctly deleted. This is the same class of pitfall the codebase already has a precedent for (Phase 109/110's `ast.walk`-vs-substring-grep lesson, and the "reworded prose to avoid literal substrings" decision recorded for Phase 109 in STATE.md).
- **Fix:** Reworded the affected docstrings/comments in `diagnostic_report.py` and `test_dev_test_cmd.py` to describe the deleted symbols without quoting their literal names verbatim (e.g., "a collector function" instead of "`prompt_provenance()`").
- **Files modified:** `firestarter_app/firestarter/diagnostic_report.py`, `firestarter_app/tests/test_dev_test_cmd.py`
- **Verification:** Re-ran both verify scripts; both pass.
- **Committed in:** `18baa91` (Task 1), `37fe93d` (Task 3)

**2. [Rule 1 - Bug] Removed unused `table` variable assignment flagged by ruff (F841) in test_diagnostic_report.py**
- **Found during:** Task 3 verification (`ruff check tests/...`)
- **Issue:** The pre-existing test `test_full_report_all_four_sub_objects_single_source` (renamed to `...all_sub_objects...` by this plan) ends with `table = report.render()  # must not raise`. Confirmed via `git stash` that this ruff F841 error is PRE-EXISTING at the base commit (`8f59374`), unrelated to this plan's changes, but since it lives inside a test function this plan is directly editing/renaming (a file/line in the exact scope of the plan's own `ruff check tests/test_diagnostic_report.py` verify command), leaving it red would fail this plan's own required gate.
- **Fix:** Changed `table = report.render()` to `report.render()` (same call, unused-assignment removed); the "must not raise" intent is preserved via the bare call.
- **Files modified:** `firestarter_app/tests/test_diagnostic_report.py`
- **Verification:** `ruff check tests/test_diagnostic_report.py` passes; `pytest tests/test_diagnostic_report.py` still green.
- **Committed in:** `37fe93d` (Task 3)

---

**Total deviations:** 2 auto-fixed (1 Rule 3 blocking, 1 Rule 1 bug — a pre-existing lint error inside code this plan directly touches).
**Impact on plan:** Both fixes were necessary to make this plan's own required verification gates pass; neither changes behavior beyond what the plan specified. No scope creep.

## Issues Encountered

- **`Plan`/`BannerCounts` dataclass field-order gotcha** in the new `test_provenance.py`: `Plan` requires `name` as its first positional field (not just `steps`/`locked_destructive`) — caught immediately via a `TypeError` on first test run, fixed by passing `name=` explicitly in the new `_minimal_report()` helper.
- **Click `Command` object is not directly `inspect.getsource()`-able** — `dev_test` is registered via `@dev.command(name="test")`, so `h.dev_test` is a `click.Command` instance, not a plain function; `inspect.getsource(h.dev_test)` raises `TypeError`. Used `h.dev_test.callback` (the underlying wrapped function Click stores) instead, both here and matching how the plan's own verify script presumably needs to resolve it. Documented for any future test/verify script touching this handler.
- **Three pre-existing, unrelated test failures were confirmed (not introduced) during full-suite runs**, all reproduced identically at the pre-Task-1 base commit (`8f59374`) via `git stash`/checkout comparison:
  1. `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` — the plan's documented pre-existing stale-golden failure (unrelated DB-change origin, per `reference_audit_coverage_matrix_golden_stale` memory note).
  2. `tests/test_characterization.py::test_no_programmer_found_read` and `::test_no_programmer_found_erase` — NOT documented in the plan's environment notes, but confirmed environment-specific and pre-existing (fails identically at `8f59374` before any of this plan's edits, both in isolation and inside the full suite). Root cause: this devcontainer session has real bench hardware reachable at `/dev/ttyACM0` (per the project's own `reference_usb_passthrough_bench` MEMORY.md note), so `SerialCommunicator.find_and_connect` succeeds despite the test's `serial.tools.list_ports.comports()` monkeypatch returning an empty list — some other path in the connect logic still reaches the real device. This is orthogonal to any of this plan's diff (`diagnostic_report.py`/`hardware.py`/`cli_handlers.py`/the three test files) and requires a dedicated fix/mock-hardening in a future session, not this gap-closure plan.
- **5 pre-existing `ruff check`/`ruff format` failures in `tools/*.py` and `tests/test_validate_family_cmd.py`** (confirmed via base-commit comparison, `git diff --stat 8f59374 HEAD -- tools/ tests/test_validate_family_cmd.py` shows zero overlap with this plan's diff) — matches the "4 pre-existing ruff/format failures" carry-forward documented in earlier phase SUMMARYs (e.g. Phase 104-03, Phase 107-03). Not fixed here (out of scope, `tools/` files never touched by this plan).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter dev test <chip> --destructive` on a real terminal now issues **zero** interactive provenance prompts. The only interactive input remaining is the `--destructive` safety confirm (SAFE-03), unchanged in behavior.
- The Phase-111 SC2 bench re-verify (deferred in `112-UAT.md` test 1, blocked by the broken prompts) is now unblocked for a future bench session on Leonardo + Rev 2.0 with an electrically-erasable chip (W27C512/W29C020).
- `fw_board_identity` remains an honest `None` in every run — this is a structural limitation of `EpromOperator`'s per-operation connection lifecycle, not a bug in this plan. A future phase wanting a live `version:board` capture would need to either (a) widen `EpromOperator`'s contract to expose a post-op identity snapshot before disconnecting, or (b) accept a single additional orchestrator-owned connection explicitly scoped for identity capture (a SAFE-02 policy decision, not something this plan can unilaterally introduce).
- The two newly-surfaced environment-specific `test_characterization.py` failures should be flagged to a future session for a dedicated fix (likely needs a more thorough serial-discovery mock, e.g. also patching whatever `find_and_connect` fallback path is reaching the real `/dev/ttyACM0` device) — not blocking for this gap-closure plan since they are demonstrably pre-existing and orthogonal.

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/diagnostic_report.py
- FOUND: firestarter_app/firestarter/hardware.py
- FOUND: firestarter_app/firestarter/cli_handlers.py
- FOUND: firestarter_app/tests/test_provenance.py
- FOUND: firestarter_app/tests/test_dev_test_cmd.py
- FOUND: firestarter_app/tests/test_diagnostic_report.py
- FOUND: .planning/phases/112-dev-test-handler-wiring/112-04-SUMMARY.md
- FOUND: commit 18baa91 (Task 1, firestarter_app submodule)
- FOUND: commit 2e41622 (Task 2, firestarter_app submodule)
- FOUND: commit 37fe93d (Task 3, firestarter_app submodule)

---
*Phase: 112-dev-test-handler-wiring*
*Completed: 2026-07-03*
