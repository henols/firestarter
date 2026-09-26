---
phase: 127-host-dfu-installer
plan: 08
subsystem: py32-dfu
tags: [dfu, pyusb, refactor, testing, hoist, py32f071]

# Dependency graph
requires:
  - phase: 127-06
    provides: "tests/test_pyusb_api_surface.py + conftest.py collect_ignore gate; the fake-vs-real placeholder this plan fills"
  - phase: 127-07
    provides: "the de-pragma'd _require_usb(); PyusbMissingError coverage this plan's edits do not touch"
provides:
  - "firestarter/py32_dfu.py: exactly one self._finish( call site, in flash(), after the dfuse/plain fork; _download_dfuse/_download_plain now return (base_or_None, next_block) instead of calling _finish"
  - "tests/test_py32_dfu.py: _FakeUsbDevice extended with a DFU_UPLOAD arm, an uploads() helper, upload_image/upload_block_size __init__ params, a pyusb-1.3.1-shaped ctrl_transfer signature (data_or_wLength + timeout), and _interface(attributes=0)"
  - "tests/test_pyusb_api_surface.py: fake-vs-real ctrl_transfer signature comparison (order + defaults + non-vacuity), closing the handoff Plan 127-06 left open"
affects: [127-09, 127-12]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hoisting a side-effecting terminal call (_finish, which leaves DFU mode) out of two private strategy methods into their single caller, converting an ordering convention into a structural one-call-site invariant enforced by grep -c"
    - "Measuring behaviour-neutrality of a structural refactor by capturing device.calls before and after the edit and diffing element-by-element, rather than trusting a green test suite alone"
    - "Extending an in-repo test fake (not replacing it) with defaulted constructor/method parameters so every one of 58 pre-existing call sites is provably unaffected"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/py32_dfu.py
    - firestarter_app/tests/test_py32_dfu.py
    - firestarter_app/tests/test_pyusb_api_surface.py

key-decisions:
  - "D-12/C-5 hoist shape (b), per the operator's 2026-08-01 decision recorded in 127-08-PLAN.md: _download_dfuse and _download_plain now return (base_or_None, next_block) and flash() calls self._finish(...) exactly once, after the dfuse/plain fork and before the completion log line. _finish()'s own signature, docstring and body are byte-identical to their pre-task state (confirmed by git diff showing only call sites moved)."
  - "The hoisted-call comment names D-12/C-5 and uses the method name unqualified (_finish(), never self._finish() form) so it cannot be mistaken for a second call site by the exactly-one-call-site gate (grep -c 'self\\._finish(' returns 1)."
  - "Behaviour-neutrality (A5) converted from [INFERRED] to measured: captured the full device.calls sequence for one DfuSe flash (15 calls) and one plain flash (7 calls) via a throwaway script against the existing fake, before and after the edit, and compared element-by-element -- identical in both cases. See Verification below for the raw sequences."
  - "_FakeUsbDevice is extended, not replaced. ctrl_transfer's 5th parameter renamed data -> data_or_wLength with a trailing timeout=None added (C-6), matching real pyusb 1.3.1's parameter names in order. The calls tuple shape (5-tuple, same field order) is unchanged, so dnloads()/dfuse_commands()/data_blocks() and every assertion built on them needed no edits."
  - "The DFU_UPLOAD arm computes its offset from a locally-written first_upload_block = 2 (a citing comment naming the DfuSe from-block-2 convention), not py32_dfu._DFUSE_FIRST_BLOCK -- keeping the fake an independent model of the wire protocol rather than a mirror of the module under test's private constant. A negative offset (attempted upload of block 0 or 1) clamps to an empty result rather than wrapping; a request past the end of the backing image returns whatever the slice yields (a short read), which Plan 127-09 must handle as a real device behaviour, not a fake bug."
  - "_interface() gains attributes=0 as a defaulted parameter, passed through to DfuInterface. The default of 0 is deliberate (documented in a comment) so all 58 pre-existing tests keep constructing a device with bitCanUpload unset; once Plan 127-09 lands, all 58 take the SKIPPED_NO_UPLOAD path while flash() still returns True (D-10's blast-radius property), unaffected by this plan."
  - "tests/test_pyusb_api_surface.py's new test replaces Plan 127-06's placeholder comment exactly where it said Plan 127-08 would land the comparison. It asserts (1) order-sensitive parameter-name match over the full overlapping prefix including data_or_wLength and timeout, with a failure message printing both lists and naming Plan 127-08/C-6; (2) every real-defaulted parameter is also defaulted on the fake; (3) a non-vacuity guard that both signatures have more than two parameters."
  - "No requirement checkbox in .planning/REQUIREMENTS.md was ticked. HOST-03/HOST-04 cited in commit messages for traceability only -- only Plan 127-12 may tick HOST-01..HOST-08 (the Phase-116 4x premature-tick guard)."

requirements-completed: []  # HOST-03 intentionally left unticked -- discharged jointly by 127-08 and 127-09, ticked only by 127-12. This plan cites HOST-03/HOST-04 in commit messages for traceability only.

coverage:
  - id: D1
    description: "Exactly one self._finish( call site exists, inside flash(), passing dfuse=interface.is_dfuse; _finish()'s own signature/docstring/body byte-identical to before; both downloaders return the base/next_block pair instead of calling _finish"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "grep -c 'self\\._finish(' firestarter/py32_dfu.py == 1"
        status: pass
      - kind: unit
        ref: "tests/test_py32_dfu.py (58 tests, all pass unmodified)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Behaviour-neutrality measured: device.calls sequences for one DfuSe flash and one plain flash captured before and after the hoist and compared element-by-element -- identical. A5 converted from [INFERRED] to measured."
    requirement: "HOST-03"
    verification:
      - kind: other
        ref: "throwaway capture script (scratchpad), before.json == after.json, dfuse 15/15 calls equal, plain 7/7 calls equal"
        status: pass
    human_judgment: false
  - id: D3
    description: "_FakeUsbDevice extended with a DFU_UPLOAD arm (correct bytes at blocks 2 and 3, negative-offset clamp, short-read-as-is), an uploads() helper, and a real-pyusb-shaped ctrl_transfer signature (data_or_wLength, timeout)"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "inline probe (plan's verify command): FAKE_EXTENSION_OK"
        status: pass
      - kind: unit
        ref: "inline probe: CLAMP_AND_SHORT_READ_OK (negative offset -> b''; short read at end of image returns the short slice)"
        status: pass
      - kind: unit
        ref: "tests/test_py32_dfu.py (58 tests, still collects 58, all pass)"
        status: pass
    human_judgment: false
  - id: D4
    description: "_interface() accepts and passes through attributes=, defaulting to 0"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "inline probe: _interface(d).attributes == 0; _interface(d, attributes=0x02).attributes == 0x02"
        status: pass
    human_judgment: false
  - id: D5
    description: "The fake's ctrl_transfer signature (order + defaults, non-vacuity-guarded) matches real pyusb 1.3.1, asserted in the ci-py32 leg only"
    requirement: "HOST-04"
    verification:
      - kind: unit
        ref: "tests/test_pyusb_api_surface.py::test_fake_ctrl_transfer_signature_matches_the_real_one (rehearsed in a throwaway .[test,py32] venv, 6/6 module tests passed)"
        status: pass
    human_judgment: false
  - id: D6
    description: "tests/test_pyusb_gating.py's ast call-site scan still passes (no new keyword-passed 5th argument); no new skip reason added"
    requirement: "HOST-05"
    verification:
      - kind: unit
        ref: "tests/test_pyusb_gating.py (6/6 passed)"
        status: pass
      - kind: unit
        ref: "tests/test_skip_census.py (5/5 passed, ALLOWED_SKIP_REASONS unchanged)"
        status: pass
    human_judgment: false
  - id: D7
    description: "No requirement checkbox in .planning/REQUIREMENTS.md was ticked by this plan; no git push/gh workflow run/git stash subcommand was run"
    verification: []
    human_judgment: true
    rationale: "Absence of a command/tick cannot be proven by a unit test; confirmed by re-reading REQUIREMENTS.md's HOST-01..HOST-08 rows unchanged (still [ ] Pending) and by review of every Bash invocation in this session (none contains git push, gh workflow run, or any git stash subcommand)."

# Metrics
duration: ~55min
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 08: Hoist `_finish()` + Extend `_FakeUsbDevice` with an UPLOAD Arm Summary

**Moved `_finish()`'s two call sites out of `_download_dfuse()`/`_download_plain()` into a single call in `flash()` (D-12/C-5's structural fix), measured the wire sequence byte-identical before and after via `device.calls` comparison (A5 → measured), and extended the shared `_FakeUsbDevice` fake with a `DFU_UPLOAD` arm and a real-pyusb-1.3.1-shaped `ctrl_transfer` signature — all without touching a single one of the 58 pre-existing tests.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-01 (approx, following STATE.md's 14:00:25Z checkpoint)
- **Completed:** 2026-08-01 (this session)
- **Tasks:** 3/3 executed
- **Files modified:** 3 (1 production, 2 test)

## Accomplishments

- **Task 1 (`6bad9d9`):** `_download_dfuse` and `_download_plain` no longer call `self._finish(...)` as their last statement — they now `return (base_or_None, next_block)`. `flash()` captures that pair from whichever branch ran and calls `self._finish(finish_base, next_block, dfuse=interface.is_dfuse)` exactly once, after the fork and before the completion log line. `grep -c 'self\._finish(' firestarter/py32_dfu.py` returns exactly 1. `_finish()`'s own signature, docstring and body are untouched (confirmed by `git diff` — only its call sites moved). A comment above the hoisted call names D-12/C-5, states why `_finish()` must be last, and names Plan 127-09 as the place the readback goes — written with the method name unqualified (`_finish()`) so the exactly-one-call-site gate isn't tripped by the comment itself.
- **Behaviour-neutrality measurement (Task 1):** wrote a throwaway capture script (not committed) that monkeypatches `find_dfu_interfaces` with the existing `_FakeUsbDevice`/`_interface` test helpers and runs `Py32DfuFlasher().flash(...)` for one DfuSe image (130 bytes → 3 blocks, 1 sector) and one plain-DFU-1.1 image (100 bytes → 2 blocks). Captured `device.calls` before the edit and after, and diffed programmatically: **DfuSe 15/15 calls identical, plain 7/7 calls identical** — both dialects byte-for-byte unchanged. This converts research assumption A5 from `[INFERRED]` to measured.
- **Task 2 (`18c95fa`):** Extended `_FakeUsbDevice` (not replaced). `ctrl_transfer`'s 5th parameter renamed `data` → `data_or_wLength`, trailing `timeout=None` added — matching real pyusb 1.3.1's parameter order (C-6). `__init__` gained `upload_image` (default `b""`) and `upload_block_size` (default `64`), both defaulted so all 58 pre-existing constructions are unaffected. A `DFU_UPLOAD` arm sits before the catch-all: computes the offset from `wValue` using a locally-written `first_upload_block = 2` (a citing comment naming the DfuSe from-block-2 convention, deliberately not importing `py32_dfu._DFUSE_FIRST_BLOCK`), clamps a negative offset to `b""`, and returns whatever slice the backing image yields — including a short read past the end. `uploads()` returns every `DFU_UPLOAD` call as `(wBlockNum, requested_length)`. `_interface()` gained a defaulted `attributes=0` parameter passed through to `DfuInterface`, with a comment recording that the default of 0 is deliberate (preserves all 58 tests; makes them take `SKIPPED_NO_UPLOAD` once 127-09 lands).
- **Task 3 (`71c86d7`):** Added the fake-vs-real `ctrl_transfer` signature comparison to `tests/test_pyusb_api_surface.py`, filling the placeholder Plan 127-06 deliberately left. Imports `_FakeUsbDevice` from `tests.test_py32_dfu` and asserts: (1) order-sensitive parameter-name match over the full overlapping prefix (7 params: `self, bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout`), failure message printing both lists and naming Plan 127-08/C-6; (2) every real-defaulted parameter is also defaulted on the fake; (3) a non-vacuity guard that both signatures have more than two parameters. Rehearsed in a throwaway `.[test,py32]` venv (deleted afterward): module 6/6 passed, full suite 1282/1282 passed (1276 devcontainer baseline + 6 py32-only tests).

## Task Commits

1. **Task 1: Hoist `_finish()` into `flash()`** — `6bad9d9` (refactor)
2. **Task 2: Extend `_FakeUsbDevice` with an UPLOAD arm** — `18c95fa` (test)
3. **Task 3: Assert the fake's signature against real pyusb** — `71c86d7` (test)

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

All three commits are on `firestarter_app`'s `v1.23-py32f071-integration` branch.

## Files Created/Modified

- `firestarter_app/firestarter/py32_dfu.py` — `_download_dfuse`/`_download_plain` return `(base_or_None, next_block)` instead of calling `_finish`; `flash()` calls `_finish()` once, with a D-12/C-5 comment
- `firestarter_app/tests/test_py32_dfu.py` — `_FakeUsbDevice` extended (`ctrl_transfer` signature aligned, `upload_image`/`upload_block_size`, `DFU_UPLOAD` arm, `uploads()`); `_interface(attributes=0)`; `DFU_UPLOAD` added to the module's import list
- `firestarter_app/tests/test_pyusb_api_surface.py` — `_FakeUsbDevice` imported; new `test_fake_ctrl_transfer_signature_matches_the_real_one`; docstring updated; placeholder comment removed

## Decisions Made

- Followed D-12/C-5's operator-chosen shape (b), the hoist, verbatim — see key-decisions above for the full rationale chain.
- Kept the DfuSe first-upload-block constant as an independent local literal in the test file (`first_upload_block = 2`) rather than importing `py32_dfu._DFUSE_FIRST_BLOCK`, per the plan's explicit instruction that the fake model the protocol independently.
- `ctrl_transfer`'s parameters were split across multiple lines with per-parameter `# noqa: N803` comments (rather than one line-level suppression) because ruff's N803 rule flags each non-lowercase argument name individually once the signature wraps.
- Task 1 and Task 2 were committed separately (not combined), since both had a fully green intermediate state — unlike Plan 127-06's Tasks 1+2, which had a hard dependency forcing a single commit.

## Deviations from Plan

None (Rule 1/2/3 sense) — plan executed exactly as written. No scope creep: only the three files named in the plan's `files_modified` were touched. `/workspaces/firestarter` remains untouched (verified `git status --short` clean both before this plan's first read and after its last commit). No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked. No task ran `git push`, `gh workflow run`, or any `git stash` subcommand. The five known pre-existing working-tree lines in `firestarter_app` (`.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`) were left untouched throughout.

## Issues Encountered

None. All three tasks' automated verification passed on the first attempt; no auto-fix cycles were needed.

## User Setup Required

None — no external service configuration required. The operator-gated CI dispatch remains a later plan's action; this plan only ran local test suites and rehearsals.

## Next Phase Readiness

- D-12's ordering constraint is now structural: there is exactly one place in `py32_dfu.py` where DFU mode is left, and it is the last statement of `flash()`. Plan 127-09 can insert the readback immediately above the hoisted `_finish()` call with no ambiguity about where it belongs.
- `_FakeUsbDevice` can now serve `DFU_UPLOAD` reads from a settable backing image and advertise `bitCanUpload` via `_interface(attributes=...)`, without a second fake class and without any of the 58 pre-existing tests changing behaviour (they all still construct `attributes=0` implicitly, which Plan 127-09's `VerifyResult.SKIPPED_NO_UPLOAD` path is built to handle).
- The fake's `ctrl_transfer` contract is now pinned against real pyusb 1.3.1 in the `ci-py32` leg — a future signature drift in either the fake or a pyusb upgrade will fail loudly instead of silently.
- Full app suite in the devcontainer (pyusb absent): **1276 collected / 1276 passed / 0 failed / 0 skipped** (unchanged from the 127-07 baseline — this plan added no new devcontainer-collected tests, only extended existing fixtures and one pyusb-gated module). `ruff check`, `ruff format --check` both clean. `tools/check_mypy_watermark.py`: 1 error vs watermark 35 (unaffected, passes).
- Rehearsed in a throwaway `.[test,py32]` venv (deleted afterward): `tests/test_pyusb_api_surface.py` — **6/6 passed** (5 from 127-06 + this plan's new comparison); full suite — **1282/1282 passed**. Devcontainer confirmed still pyusb-absent afterward.
- `tests/test_pyusb_gating.py`: **6/6 passed** — the ast call-site scan confirms no production `ctrl_transfer` call-site passes its 5th argument by keyword. `tests/test_skip_census.py`: **5/5 passed** — no new skip reason added.
- HOST-01..HOST-08 all remain `[ ]` Pending in `.planning/REQUIREMENTS.md` — unaffected by this plan, as instructed. Only Plan 127-12 may tick them.
- `/workspaces/firestarter` remains untouched (read-only input), confirmed clean before and after this plan's execution.

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/py32_dfu.py` (modified)
- FOUND: `firestarter_app/tests/test_py32_dfu.py` (modified)
- FOUND: `firestarter_app/tests/test_pyusb_api_surface.py` (modified)
- FOUND: commit `6bad9d9` in `firestarter_app` git log
- FOUND: commit `18c95fa` in `firestarter_app` git log
- FOUND: commit `71c86d7` in `firestarter_app` git log
- FOUND: `.planning/phases/127-host-dfu-installer/127-08-SUMMARY.md`
