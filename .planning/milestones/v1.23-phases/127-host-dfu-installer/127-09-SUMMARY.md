---
phase: 127-host-dfu-installer
plan: 09
subsystem: py32-dfu
tags: [dfu, dfuse, pyusb, py32f071, verification, enum, honesty-ledger]

# Dependency graph
requires:
  - phase: 127-08
    provides: "the hoisted single _finish() call site in flash(); _FakeUsbDevice's DFU_UPLOAD arm, uploads() helper, upload_image/upload_block_size, attributes=-capable _interface()"
  - phase: 127-03
    provides: "tests/test_dfu_opcode_anchors.py, the independent opcode oracle; the bitCanUpload mask anchored as a bare literal pending this plan's production constant"
provides:
  - "firestarter/py32_dfu.py: _DFU_BIT_CAN_UPLOAD, VerifyResult enum (VERIFIED/SKIPPED_NO_UPLOAD/SKIPPED_PLAIN_DFU/MISMATCH), Py32DfuFlasher.verify_result/verify_reason, _read_back(), _verify_readback(), and the download -> readback -> _finish() sequence in flash()"
  - "firestarter/firmware.py: verify-aware logging in _install_with_dfu -- 'written but NOT verified' completion line when verify_result is not VERIFIED"
  - "tests/test_py32_dfu.py: TestReadbackVerification (8 tests pinning the four VerifyResult outcomes) and TestInstallWithDfuVerifyLogging (3 caplog tests)"
  - "tests/test_dfu_opcode_anchors.py: closed the handoff -- _DFU_BIT_CAN_UPLOAD now asserted against the independently-anchored bitCanUpload mask literal"
affects: [127-12, 130-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The codebase's first enum.Enum (VerifyResult), used specifically for a locked-decision result state (D-10) while flash() keeps returning bool for blast-radius reasons -- an explicit, documented departure from the existing module-level-string-plus-dict-router idiom (firmware.py's FLASH_METHOD_*)"
    - "Soft-fail vs hard-fail split on the SAME enum: two members (SKIPPED_NO_UPLOAD, SKIPPED_PLAIN_DFU) never raise; one member (MISMATCH) always pairs with a raised exception -- the attribute is set before the raise so a caller inspecting the flasher after catching the exception still sees the state"
    - "Ordering asserted on a recorded call sequence (device.calls indices) rather than trusted from code structure alone -- last DFU_UPLOAD strictly before the zero-length DFU_DNLOAD _finish() sends"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/py32_dfu.py
    - firestarter_app/firestarter/firmware.py
    - firestarter_app/tests/test_py32_dfu.py
    - firestarter_app/tests/test_dfu_opcode_anchors.py

key-decisions:
  - "D-10's enum shape implemented literally: VerifyResult(enum.Enum) with exactly VERIFIED/SKIPPED_NO_UPLOAD/SKIPPED_PLAIN_DFU/MISMATCH, auto() values, no StrEnum (py3.9 floor), no IntEnum. flash() unchanged: still returns bool. grep -c 'StrEnum' firestarter/py32_dfu.py == 0."
  - "D-09's dialect fork implemented in _verify_readback: plain DFU 1.1 (not interface.is_dfuse) sets SKIPPED_PLAIN_DFU with verify_reason exactly 'load address not under host control' -- converting flash()'s existing runtime warning into a recorded fact, not a new claim. DfuSe with bitCanUpload unset sets SKIPPED_NO_UPLOAD."
  - "D-11/D-12 ordering: _verify_readback() is called between the downloader and the single _finish() call in flash(). A MISMATCH raises DfuProtocolError inside _verify_readback(), before _finish() runs, so the device is deliberately left in DFU mode rather than told to leave (and manifest a bad image). grep -c 'self\\._finish(' firestarter/py32_dfu.py stayed exactly 1 -- the readback call site did not disturb the single-call-site invariant 127-08 established."
  - "_read_back reads DFU_UPLOAD blocks numbered from _DFUSE_FIRST_BLOCK via self._dev.ctrl_transfer(_IN, DFU_UPLOAD, block, self._index, request_length) -- all five arguments positional, per the plan's instruction to keep tests/test_pyusb_gating.py's ast call-site scan passing. Stops on a short read (device has no more to give) or once length bytes are collected; may return fewer than length bytes, and the caller (_verify_readback) is what turns a short readback into a MISMATCH."
  - "127-03's deferred handoff closed: tests/test_dfu_opcode_anchors.py's test_bit_can_upload_mask_matches_usb_dfu_11_section_4_1_3 (renamed from ..._is_anchored_pending_plan_127_09) now asserts py32_dfu._DFU_BIT_CAN_UPLOAD == the independently-written 0x02 literal. Nothing else in that file changed."
  - "_install_with_dfu (firmware.py) reads flasher.verify_result after a successful flash(): VERIFIED extends the existing success line ('...and verified via DFU_UPLOAD readback'); either SKIPPED_* outcome emits a WARNING naming flasher.verify_reason and changes the completion line to 'Firmware written but NOT verified on {board} ({elapsed}s)'. Return value and type are unchanged. A comment records the DfuProtocolError -> FirmwareOperationError -> ClickException -> exit 1 chain and D-11's rule that a mismatch must never be downgraded to a warning here."
  - "No CLI option, --force flag, or environment-variable opt-out was added anywhere. firestarter/cli_handlers.py was not touched by this plan (files_modified did not name it, and nothing in this plan needed to)."
  - "No requirement checkbox in .planning/REQUIREMENTS.md was ticked. HOST-03 is cited in every commit message for traceability only -- confirmed HOST-01..HOST-08 are still all '[ ] Pending' after this plan's final commit. Only Plan 127-12 may tick them."

requirements-completed: []  # HOST-03 intentionally left unticked -- only Plan 127-12 may tick HOST-01..HOST-08 (Phase-116 4x premature-tick guard).

coverage:
  - id: D1
    description: "_DFU_BIT_CAN_UPLOAD == 0x02 exists with a DFU 1.1 Sec 4.1.3 citation; VerifyResult is a plain enum.Enum with exactly the four D-10 members in order, using auto() values; StrEnum is absent from the file"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "inline probe (plan's verify command): VERIFY_STATE_OK -- issubclass checks, member-name list, _DFU_BIT_CAN_UPLOAD == 0x02, verify_result/verify_reason both None on construction"
        status: pass
      - kind: unit
        ref: "grep -c 'StrEnum' firestarter/py32_dfu.py == 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "flash() runs download -> _verify_readback() -> _finish() as a single sequence; grep -c 'self\\._finish(' firestarter/py32_dfu.py stays exactly 1 after adding the readback call"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "grep -c 'self\\._finish(' firestarter/py32_dfu.py == 1 (re-checked after Task 1's edits)"
        status: pass
    human_judgment: false
  - id: D3
    description: "All four VerifyResult outcomes pinned against the mock: bitCanUpload=0 and plain-DFU-1.1 both fail soft with the exact cause string and zero DFU_UPLOAD calls; a matching multi-block readback verifies; a byte-differing and a truncated readback both raise DfuProtocolError naming the offset/byte-counts and set MISMATCH"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "tests/test_py32_dfu.py::TestReadbackVerification (8/8 passed): test_bit_can_upload_unset_fails_soft, test_plain_dfu11_fails_soft_with_cause_named, test_matching_readback_verifies, test_differing_readback_is_a_hard_failure, test_truncated_readback_is_a_hard_failure_too, test_ordering_last_upload_precedes_finish, test_mismatch_never_manifests, test_pre_existing_construction_still_skips_soft"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-12's ordering asserted on device.calls indices (last DFU_UPLOAD strictly before the zero-length DFU_DNLOAD _finish() sends); a MISMATCH is proven to never reach a zero-length DFU_DNLOAD (_finish() never ran)"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "tests/test_py32_dfu.py::TestReadbackVerification::test_ordering_last_upload_precedes_finish, ::test_mismatch_never_manifests"
        status: pass
    human_judgment: false
  - id: D5
    description: "Blast-radius property: all 58 pre-existing tests (constructing _interface() with no attributes=) still pass and take the SKIPPED_NO_UPLOAD path; flash() still returns True. tests/test_py32_dfu.py now collects 66 tests (58 + 8 new in Task 2)"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "tests/test_py32_dfu.py -- 66 passed (58 pre-existing unmodified + 8 new)"
        status: pass
      - kind: unit
        ref: "tests/test_py32_dfu.py::TestReadbackVerification::test_pre_existing_construction_still_skips_soft"
        status: pass
    human_judgment: false
  - id: D6
    description: "127-03's deferred handoff closed: tests/test_dfu_opcode_anchors.py asserts _DFU_BIT_CAN_UPLOAD against its independently-anchored literal; the forward-holding no-source==source-oracle test in that file still passes"
    requirement: "HOST-06"
    verification:
      - kind: unit
        ref: "tests/test_dfu_opcode_anchors.py (7/7 passed, including test_bit_can_upload_mask_matches_usb_dfu_11_section_4_1_3 and test_test_py32_dfu_still_contains_no_source_source_opcode_oracle)"
        status: pass
    human_judgment: false
  - id: D7
    description: "_install_with_dfu says 'written but NOT verified' when verify_result is not VERIFIED (WARNING naming the reason, INFO completion line changed); a VERIFIED install extends the success line instead and never emits that wording; a MISMATCH raises FirmwareOperationError naming the offset -- proving the error chain reaches the layer the CLI converts to exit 1"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "tests/test_py32_dfu.py::TestInstallWithDfuVerifyLogging (3/3 passed): test_unverified_install_warns_and_says_not_verified, test_verified_install_reports_verification_not_the_warning, test_mismatch_raises_firmware_operation_error_naming_the_offset"
        status: pass
      - kind: unit
        ref: "grep -c 'written but NOT verified' firestarter/firmware.py == 1"
        status: pass
    human_judgment: false
  - id: D8
    description: "asset_candidates() is byte-identical to its pre-plan state and still returns the Phase 128 contract list; the D-17 comment at flash_method() and _install_with_avrdude are untouched"
    verification:
      - kind: unit
        ref: "inline probe (plan's verify command): ASSET_CANDIDATES_UNCHANGED (body-diff against git show HEAD~1), PHASE128_CONTRACT_OK (asset_candidates('py32f071') == ['firestarter_py32f071.hex', 'firestarter_py32f071.bin'])"
        status: pass
    human_judgment: false
  - id: D9
    description: "Full app suite green with 0 skipped; coverage >= 70%; ruff check, ruff format --check, and the mypy watermark all pass after every task, including after ruff-format auto-reformatted two files for line-length"
    verification:
      - kind: unit
        ref: "pytest tests/ -q --no-cov -> 1287 passed, 0 failed, 0 skipped (final run, all three tasks committed)"
        status: pass
      - kind: unit
        ref: "pytest tests/ --cov=firestarter --cov-fail-under=70 -> TOTAL 82% (exit 0); py32_dfu.py 79%, firmware.py 75%"
        status: pass
      - kind: other
        ref: "ruff check firestarter/ tests/ (clean); ruff format --check firestarter/ tests/ (clean, 114 files); python tools/check_mypy_watermark.py (1 error vs watermark 35, passes)"
        status: pass
    human_judgment: false
  - id: D10
    description: "No requirement checkbox ticked in REQUIREMENTS.md; no git push/gh workflow/git stash subcommand run; /workspaces/firestarter left untouched"
    verification: []
    human_judgment: true
    rationale: "Absence of a command/tick cannot be proven by a unit test; confirmed by re-reading REQUIREMENTS.md's HOST-01..HOST-08 rows unchanged (still [ ] Pending), review of every Bash invocation in this session (none contains git push, gh workflow run, or any git stash subcommand), and git -C /workspaces/firestarter status --short returning empty both before and after this plan's execution."

# Metrics
duration: ~65min
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 09: DFU_UPLOAD Readback Verification Summary

**Written flash is now read back over `DFU_UPLOAD` and compared byte-for-byte with the payload, recorded as a `VerifyResult` enum on the flasher — soft-failing with a named cause when verification cannot be attempted (plain DFU 1.1, or `bitCanUpload = 0`), and hard-failing with the first differing offset when it can be attempted and the bytes differ — closing the gap where py32 was the project's only install path that wrote without verifying.**

## Performance

- **Duration:** ~65 min
- **Started:** 2026-08-01 (following STATE.md's Plan 08 checkpoint)
- **Completed:** 2026-08-01
- **Tasks:** 3/3 executed
- **Files modified:** 4 (2 production, 2 test)

## Accomplishments

- **Task 1 (`690ffcf`):** Added `_DFU_BIT_CAN_UPLOAD = 0x02` (DFU 1.1 §4.1.3, bit 1 of `bmAttributes`) and the module's first `enum.Enum`, `VerifyResult`, with exactly the four D-10 members (`VERIFIED`, `SKIPPED_NO_UPLOAD`, `SKIPPED_PLAIN_DFU`, `MISMATCH`), `enum.auto()` values, and a docstring recording the `flash()`-stays-`bool` blast-radius decision, the `None`-means-not-run convention, and the honest note that this is the codebase's first `enum` (existing idiom elsewhere is module-level strings plus a dict router). `Py32DfuFlasher.__init__` gained `verify_result`/`verify_reason`, both `None`-initialised. Added `_read_back()` (issues `DFUSE_SET_ADDRESS`, then reads `DFU_UPLOAD` blocks from `_DFUSE_FIRST_BLOCK`, all five `ctrl_transfer` arguments positional, stopping on a short read) and `_verify_readback()` (the seven-step D-09..D-12 decision tree: plain-DFU skip with the exact reason string `load address not under host control`; no-upload skip naming `bitCanUpload = 0`; full-payload compare; truncation and byte-mismatch both set `MISMATCH` and raise `DfuProtocolError` naming the offset in `0x%08X` and both byte values in `0x%02X`; a clean compare sets `VERIFIED`). Wired `self._verify_readback(interface, base, payload)` into `flash()` between the downloader and the single hoisted `_finish()` call, with a comment naming D-11/D-12 and using the unqualified method name so the exactly-one-call-site gate (`grep -c 'self\._finish('` == 1) is not tripped by the comment itself. Closed 127-03's deferred handoff in `tests/test_dfu_opcode_anchors.py`: `test_bit_can_upload_mask_matches_usb_dfu_11_section_4_1_3` now asserts `_DFU_BIT_CAN_UPLOAD` against the independently-anchored `0x02` literal (nothing else in that file changed).
- **Task 2 (`dd9f5af`):** Added `TestReadbackVerification` (8 tests) to `tests/test_py32_dfu.py`, using the existing `_FakeUsbDevice`/`_interface`/`find_dfu_interfaces`-monkeypatch idiom and a 200-byte payload spanning several 64-byte transfer blocks. Covers: `bitCanUpload = 0` fails soft with zero `DFU_UPLOAD` calls; plain DFU 1.1 (with `attributes=0x02`, so the skip is attributable to the dialect, not the attribute) fails soft with `verify_reason` exactly `load address not under host control`; a matching readback verifies and the total bytes requested across all `DFU_UPLOAD` calls covers the whole payload (proving a full-payload compare, not a spot-check); a one-byte-differing readback and a truncated readback both raise `DfuProtocolError` naming the offset/byte-counts and set `MISMATCH`; D-12's ordering asserted on `device.calls` indices (last `DFU_UPLOAD` strictly before `_finish()`'s zero-length `DFU_DNLOAD`); a `MISMATCH` path contains no zero-length `DFU_DNLOAD` at all (`_finish()` never ran); and the blast-radius property that a pre-existing-shaped `_interface(_FakeUsbDevice())` call (no `attributes=`) still returns `True` and records `SKIPPED_NO_UPLOAD`. `tests/test_py32_dfu.py` now collects 66 tests (58 pre-existing + 8 new), all passing; full suite 1284 passed / 0 failed / 0 skipped at this point.
- **Task 3 (`8a265ef`):** `_install_with_dfu` (`firmware.py`) now inspects `flasher.verify_result` after a successful `flash()`: `VERIFIED` extends the existing success line to say the readback was verified; either `SKIPPED_*` outcome emits a `WARNING` naming `flasher.verify_reason` and changes the completion line to `"Firmware written but NOT verified on {board} ({elapsed:.2f}s)"` instead of reporting a bare success. Return type/value unchanged. A comment records the `DfuProtocolError` → `FirmwareOperationError` → `ClickException` → exit-1 chain and D-11's rule that a mismatch must never be downgraded to a warning in this branch. Verified `asset_candidates()` byte-identical to its pre-Task-3 state (Phase 128's Criterion 4 contract intact) and that `flash_method()`'s D-17 comment / `_install_with_avrdude` were untouched. Added `TestInstallWithDfuVerifyLogging` (3 `caplog` tests) — the phase's only log-text assertions, with a class docstring explaining why that is consistent with D-10 (the *state* is asserted as an enum in Task 2; the operator-facing *wording* is itself a named requirement checkable only as text). Full suite: 1287 passed / 0 failed / 0 skipped; `ruff check`, `ruff format --check` (after auto-reformatting two files for a line-length rule), and the mypy watermark all pass.

## Task Commits

1. **Task 1: VerifyResult, the DFU_UPLOAD readback, and the download → readback → _finish sequence** — `690ffcf` (feat)
2. **Task 2: The HOST-03 behaviour and ordering tests against the mock device** — `dd9f5af` (test)
3. **Task 3: "written but NOT verified" — verify-aware logging in _install_with_dfu** — `8a265ef` (feat)

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

All three commits are on `firestarter_app`'s `v1.23-py32f071-integration` branch.

## Files Created/Modified

- `firestarter_app/firestarter/py32_dfu.py` — `_DFU_BIT_CAN_UPLOAD`, `VerifyResult` enum, `Py32DfuFlasher.verify_result`/`verify_reason`, `_read_back()`, `_verify_readback()`, and the `download → readback → _finish` sequence in `flash()`
- `firestarter_app/firestarter/firmware.py` — verify-aware logging in `_install_with_dfu` ("written but NOT verified" completion line, WARNING naming the reason)
- `firestarter_app/tests/test_py32_dfu.py` — `TestReadbackVerification` (8 tests), `TestInstallWithDfuVerifyLogging` (3 `caplog` tests), `VerifyResult` added to the import list
- `firestarter_app/tests/test_dfu_opcode_anchors.py` — closed 127-03's deferred `_DFU_BIT_CAN_UPLOAD` equality assertion

## Decisions Made

- Followed D-09..D-12 verbatim, per the plan's `must_haves.truths` — see key-decisions above for the full rationale chain on each.
- Wrote the no-upload reason as `"device does not advertise upload support (bitCanUpload = 0)"` rather than a bare `"bitCanUpload = 0"`, satisfying the acceptance criterion's substring requirement while giving the operator/log-reader more context; the plain-DFU reason, by contrast, is the exact string the plan mandated (`"load address not under host control"`) with no wrapping, since that one was specified as an exact match.
- Used a 200-byte payload (spanning 4 blocks at the fake's 64-byte transfer size: 64+64+64+8) for every `TestReadbackVerification` test, so the block-numbering arithmetic in both `_read_back` and the fake's `DFU_UPLOAD` arm is genuinely exercised, not trivially satisfied by a single block.
- Detected `_finish()`'s terminating zero-length `DFU_DNLOAD` by scanning `device.calls` for any `DFU_DNLOAD` whose payload is falsy (`not call[4]`), rather than hardcoding a block number — the only naturally-empty `DNLOAD` in the whole sequence is that terminator, since every data block in a 200-byte/64-byte-chunk transfer carries a non-empty payload and every DfuSe command (`wBlockNum == 0`) carries a non-empty command byte.
- `TestInstallWithDfuVerifyLogging` bypasses the channel gate via `monkeypatch.setattr(firmware, "is_board_available", lambda board: True)` (matching the existing `test_dfu_install_refused_on_stable` idiom) so the class exercises verify-aware logging in isolation from `TestBetaChannelGate`'s gate-behaviour tests.
- Ran `ruff format` once after Task 3 to auto-wrap two lines that exceeded the line-length preference (one in `firmware.py`'s new logging block, one in the new `caplog` test) rather than hand-wrapping them, since the formatter's own preferred wrapping was simpler than what had been written by hand.

## Deviations from Plan

None (Rule 1/2/3 sense) — plan executed exactly as written. No scope creep: only the four files named in the plan's `files_modified` were touched. `/workspaces/firestarter` remains untouched (`git status --short` verified clean both before this plan's first read and after its last commit). No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked — HOST-01..HOST-08 all still `[ ]` Pending. No task ran `git push`, `gh workflow run`, or any `git stash` subcommand. No CLI option, `--force` flag, or environment-variable opt-out was added anywhere; `firestarter/cli_handlers.py` was not touched. The five known pre-existing working-tree lines in `firestarter_app` (`.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`) were left untouched throughout — only `firestarter/py32_dfu.py`, `firestarter/firmware.py`, `tests/test_py32_dfu.py`, and `tests/test_dfu_opcode_anchors.py` were staged and committed.

## Issues Encountered

- `ruff format` flagged two newly-written multi-line f-string blocks (one in `firmware.py`, one in a new `caplog` test) as reformattable after Task 3's edits — not a defect, just the formatter's preferred single-line wrapping for lines under its length threshold. Ran `ruff format firestarter/firmware.py tests/test_py32_dfu.py` to apply it, then re-verified `ruff check`/`ruff format --check`/the full suite/coverage all still passed with the reformatted files.
- The full 1287-test suite (`pytest tests/ -q --no-cov`) takes ~170-185s per run, which exceeds a single 120s-capped foreground call; ran it via the background-task mechanism (or a longer explicit timeout) each time, consistent with 127-03's prior observation about this suite's runtime. Not a defect.

## User Setup Required

None — no external service configuration required.

## Mock-Only Ceiling (for Phase 130's CLOSE-02 honesty ledger)

**Everything HOST-03 built and tested in this plan is exercised against a mock, never against silicon.** `firestarter_app/firestarter/py32_dfu.py`'s `_read_back()` docstring, `tests/test_py32_dfu.py::TestReadbackVerification`'s class docstring, and this paragraph all state the same non-claim, in a form Plan 127-12 can lift verbatim:

> The `DFU_UPLOAD` readback sequence (`_read_back`, `_verify_readback`, and the four `VerifyResult` outcomes) has never run against a PY32F071. No PCB exists as of this writing. No public evidence exists that any tool — `dfu-util` included — has ever driven a PY32 upload. The DfuSe-vs-plain-DFU-1.1 fork this module implements is entirely untested against real silicon, and one of its two branches (`SKIPPED_PLAIN_DFU` vs. the DfuSe readback path) has never been the branch a real bootloader actually takes. HOST-03's permitted claim is literally *asserted against a mock*: the mock answers exactly as told (a matching backing image, an altered byte, a short slice), and the tests prove the flasher's logic responds correctly to each of those told answers — nothing more. This plan does **not** claim the DFU install works, that firmware runs on a PY32F071, or that any part of this sequence is bench- or hardware-validated.

Both soft-fail cases are genuinely distinguishable from success in user-visible output, proven by `TestInstallWithDfuVerifyLogging`: a device reporting `bitCanUpload = 0` and a plain-DFU-1.1 dialect both produce the WARNING + `"written but NOT verified"` completion line rather than a bare success line — "could not verify" never renders as success.

## Next Phase Readiness

- Full app suite: **1287 collected / 1287 passed / 0 failed / 0 skipped** (1276 devcontainer baseline at the start of Phase 127's Plan 08 + 8 new `TestReadbackVerification` tests + 3 new `TestInstallWithDfuVerifyLogging` tests). `ruff check`, `ruff format --check` (114 files) both clean. `tools/check_mypy_watermark.py`: 1 error vs watermark 35 (unaffected, passes). Coverage: `--cov-fail-under=70` passes at 82% total (`py32_dfu.py` 79%, `firmware.py` 75%).
- `tests/test_py32_dfu.py` now collects 69 tests total (58 pre-existing + 8 `TestReadbackVerification` + 3 `TestInstallWithDfuVerifyLogging`), all passing.
- `tests/test_dfu_opcode_anchors.py` collects 7 tests, all passing — 127-03's deferred `bitCanUpload` handoff is now fully closed; no forward-holding placeholder remains for HOST-03/HOST-06 in that file.
- py32 is no longer the project's only install path that writes without verifying: a matching readback records `VERIFIED` and says so; a device that cannot support verification (either dialect reason) is recorded as `SKIPPED_*` and the operator is told the write was **not** verified rather than reading a bare success; a genuine mismatch is a hard exit-1 failure via the existing `DfuError` → `FirmwareOperationError` conversion, and the device is never told to leave DFU mode on that path.
- HOST-01..HOST-08 all remain `[ ]` Pending in `.planning/REQUIREMENTS.md` — unaffected by this plan, as instructed. Only Plan 127-12 may tick them. This plan's mock-only-ceiling paragraph above is written specifically so Plan 127-12 can quote it verbatim into Phase 130's CLOSE-02 honesty ledger.
- `/workspaces/firestarter` remains untouched (read-only input), confirmed clean before and after this plan's execution.
- Blast radius held: `flash()` still returns `bool`, all 58 pre-existing `test_py32_dfu.py` tests pass unmodified (now taking the `SKIPPED_NO_UPLOAD` path), and Phase 128's `asset_candidates()` contract is provably byte-identical.

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/py32_dfu.py` (modified)
- FOUND: `firestarter_app/firestarter/firmware.py` (modified)
- FOUND: `firestarter_app/tests/test_py32_dfu.py` (modified)
- FOUND: `firestarter_app/tests/test_dfu_opcode_anchors.py` (modified)
- FOUND: commit `690ffcf` in `firestarter_app` git log
- FOUND: commit `dd9f5af` in `firestarter_app` git log
- FOUND: commit `8a265ef` in `firestarter_app` git log
- FOUND: `.planning/phases/127-host-dfu-installer/127-09-SUMMARY.md`
