---
phase: 190-endpoints-that-do-not-depend-on-a-redirect
plan: 01
subsystem: firmware-release-management
tags: [click, requests, github-releases-api, pytest, cli]

requires: []
provides:
  - "The three FIRESTARTER_*_URL constants in firestarter_app/firestarter/constants.py address henols/firestarter_fw directly, proved with a live redirect-count reading of 0"
  - "FirmwareManager.list_releases returns None on a failed fetch and [] on a genuine empty result -- two distinguishable states instead of one"
  - "fw --list discriminates the two states, exits 1 with a stderr diagnostic naming the board and the endpoint on failure, and still exits 0 with the header row and a per-board line on a genuine empty result"
  - "fw --list --json emits no document on stdout (neither [] nor null) on the failure path"
affects: [190-02, 190-03, 190-04]

actuals:
  tokens: 3316
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Identity guard (`is None`) ahead of a json_output branch, so a failure path never reaches an output-formatting branch at all"
    - "CliRunner().invoke(cli, argv) with no obj= kwarg, used whenever a test needs to assert on which stream (stdout vs stderr) a message landed on -- obj= short-circuits the group callback before the production logging handler is installed"

key-files:
  created:
    - firestarter_app/tests/test_fw_list_failure_vs_empty.py
  modified:
    - firestarter_app/firestarter/constants.py
    - firestarter_app/firestarter/firmware.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_py32_pyusb_absent.py

key-decisions:
  - "Followed the plan's harness instruction verbatim: patched FirmwareManager.list_releases at the class for the four CLI-level tests (no obj= means the CLI constructs a real FirmwareManager, so an injected mock has nothing to attach to), and patched firmware.requests.get for the two service-layer tests."
  - "Split the JSON-failure behaviour into two separate test functions (exit code, then document-parseability) rather than one combined assertion, so the reachability check (guard reverted) produces enough independently-failing tests: a combined single test only counts as one failure no matter how many of its internal asserts break."
  - "Used a plain class instead of MagicMock for the successful-empty-page HTTP stub in the new test module, matching the shape _fetch_all_releases actually reads (json(), raise_for_status(), headers) without pulling in unittest.mock for a fixture that needs no call recording."

requirements-completed: [URL-01, URL-04]

coverage:
  - id: D1
    description: "All three FIRESTARTER_*_URL constants address henols/firestarter_fw, confined edit, proved by a boundary-aware sweep with a non-vacuity control and a live zero-redirect reading"
    requirement: "URL-01"
    verification:
      - kind: other
        ref: "/usr/bin/grep -c 'henols/firestarter_fw' firestarter/constants.py (prints 3)"
        status: pass
      - kind: other
        ref: "git grep -lE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- firestarter/constants.py | wc -l (prints 0)"
        status: pass
      - kind: other
        ref: "live GET against FIRESTARTER_RELEASE_URL: status 200, redirects: 0, resolved == requested"
        status: pass
      - kind: other
        ref: "firestarter fw --list --stable --board uno against the live renamed endpoint (asset URLs read henols/firestarter_fw/releases/download/...)"
        status: pass
    human_judgment: false
  - id: D2
    description: "list_releases returns None on a failed fetch and [] on a genuine empty result -- two distinguishable states"
    requirement: "URL-04"
    verification:
      - kind: unit
        ref: "tests/test_fw_list_failure_vs_empty.py#test_list_releases_returns_none_on_fetch_failure"
        status: pass
      - kind: unit
        ref: "tests/test_fw_list_failure_vs_empty.py#test_list_releases_returns_empty_list_on_no_matching_asset"
        status: pass
    human_judgment: false
  - id: D3
    description: "fw --list exits 1 with a stderr diagnostic naming board + endpoint on a failed fetch, and emits no document on stdout in either the plain or --json form"
    requirement: "URL-04"
    verification:
      - kind: unit
        ref: "tests/test_fw_list_failure_vs_empty.py#test_fw_list_plain_on_failure_reports_endpoint_and_board_to_stderr"
        status: pass
      - kind: unit
        ref: "tests/test_fw_list_failure_vs_empty.py#test_fw_list_json_on_failure_exits_1"
        status: pass
      - kind: unit
        ref: "tests/test_fw_list_failure_vs_empty.py#test_fw_list_json_on_failure_emits_no_document"
        status: pass
    human_judgment: false
  - id: D4
    description: "fw --list still exits 0 on a genuine empty result, printing the header row and a per-board line (plain) or an empty JSON array (--json), and the pre-existing D-13 tests stay green unedited"
    requirement: "URL-04"
    verification:
      - kind: unit
        ref: "tests/test_fw_list_failure_vs_empty.py#test_fw_list_plain_on_genuine_empty_prints_header_and_board_line"
        status: pass
      - kind: unit
        ref: "tests/test_fw_list_failure_vs_empty.py#test_fw_list_json_on_genuine_empty_parses_to_empty_list"
        status: pass
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_fw_list_plain and #test_fw_list_with_json (byte-unchanged, both pass)"
        status: pass
    human_judgment: false
  - id: D5
    description: "test_py32_pyusb_absent.py's offline fw --list vehicle adapted from a raised transport exception (now the failure path) to a successful empty release response, preserving the test's actual purpose (usb never imported)"
    verification:
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_fw_list_exits_zero_with_header_row"
        status: pass
      - kind: unit
        ref: "tests/test_py32_pyusb_absent.py::test_nothing_imported_usb (both parametrizations)"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-09-13
status: complete
---

# Phase 190 Plan 01: Repointed Firmware Release Endpoints Summary

**All three `FIRESTARTER_*_URL` constants now address `henols/firestarter_fw` directly (proved with a live zero-redirect reading), and `fw --list` exits 1 with a named stderr diagnostic and no stdout document when the release fetch fails, while a genuinely empty result still exits 0 with the header row and a per-board line.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-09-13T17:08:11Z
- **Tasks:** 2 (Task 1 tracer, Task 2 TDD test module)
- **Files modified:** 4 modified, 1 created

## Accomplishments

- Repointed all three firmware release endpoint constants from `henols/firestarter` to `henols/firestarter_fw`, confirmed with a live GET showing `redirects: 0` and `resolved == requested` (the bare slug would answer with a transparent 301 and identical asset URLs, so this is the only reading that actually distinguishes done from undone).
- Widened `FirmwareManager.list_releases`'s return contract to `List[ReleaseInfo] | None`: `None` means the fetch itself did not succeed, `[]` means it succeeded and nothing matched — the two states are no longer conflated.
- Added an identity guard (`if releases is None`) in `fw --list`'s handler, placed before the `json_output` branch so a failed fetch can never reach either rendering path. On failure: one message to stderr naming the board and the actual endpoint addressed (`FIRESTARTER_RELEASES_URL`), then `sys.exit(1)`. On a genuine empty result: header row, a new `No releases found for board {board}.` line, `sys.exit(0)` — unchanged for the JSON surface (`[]`).
- Adapted `test_py32_pyusb_absent.py::test_fw_list_exits_zero_with_header_row`'s HTTP stub from a raised transport exception (which is now the failure path and exits 1) to a successful empty release response, preserving the test's real purpose — proving `usb` is never imported — rather than repurposing it into an endpoint test. Deleted the stale comment stating the superseded "returns an empty list" contract; authored no replacement per the no-comments rule.
- Added `tests/test_fw_list_failure_vs_empty.py`: 7 tests (2 service-layer, 5 CLI-level) pinning the split on the production streams. Every CLI-level `invoke` omits the injected `AppContext`, so `result.stdout`/`result.stderr` route exactly as production does — no existing test in this repository had ever asserted `result.stderr` on a `click.testing.Result` before this module.
- Manually verified reachability: reverting Task 1's `is None` guard alone (nothing else touched) fails 3 of the 7 new tests (`test_fw_list_plain_on_failure_reports_endpoint_and_board_to_stderr`, `test_fw_list_json_on_failure_exits_1`, `test_fw_list_json_on_failure_emits_no_document`); restoring the guard returns the module to 7/7. Command: `pytest tests/test_fw_list_failure_vs_empty.py -o addopts= -q` run against a temporary in-place removal of the guard block, then against the restored file.

## Task Commits

Both commits are in the `firestarter_app` submodule, on `v1.38-repository-rename`:

1. **Task 1: End-to-end — repoint the endpoints and make fw --list distinguish a failed fetch from an empty one** - `a134a91` (feat)
2. **Task 2: Pin the failure-versus-empty split with tests that measure the production streams** - `cf872a6` (test)

No meta-repo (`/workspaces`) commit is made by this plan — this `SUMMARY.md` is written to `.planning/` and committed separately by the executor/orchestrator per the phase's artifact-ownership split. The gitlink advance to these two commits is `190-04`'s job, not this plan's.

## Files Created/Modified

- `firestarter_app/firestarter/constants.py` - the three `FIRESTARTER_*_URL` values now read `henols/firestarter_fw`; nothing else in the file touched
- `firestarter_app/firestarter/firmware.py` - `list_releases`'s return annotation widened to `List[ReleaseInfo] | None`; its `except requests.RequestException` arm now returns `None` instead of `[]`; docstring extended with the two-state contract
- `firestarter_app/firestarter/cli_handlers.py` - imports `FIRESTARTER_RELEASES_URL`; `fw --list`'s branch gained the `is None` guard (stderr diagnostic + exit 1) ahead of `json_output`, and the plain-table path gained a `No releases found for board {board}.` line for the genuine-empty case
- `firestarter_app/tests/test_py32_pyusb_absent.py` - `_CHILD_PROGRAM_TEMPLATE`'s HTTP stub changed from a raised `requests.RequestException` to a successful empty-page response object; the stale comment describing the old "returns an empty list" contract deleted
- `firestarter_app/tests/test_fw_list_failure_vs_empty.py` (new) - 7 tests: 2 driving `list_releases`'s real body through the HTTP seam, 5 driving the CLI end to end with no injected context so stream routing matches production

## Decisions Made

- Patched `FirmwareManager.list_releases` at the class (not through an injected mock) for the four CLI-level failure/empty tests, because omitting `obj=` means the CLI constructs its own real `FirmwareManager` — there is no injected instance to attach a mock to. The two service-layer tests instead patch `firmware.requests.get`, driving `list_releases`'s real body.
- Split the JSON-failure behaviour into two separate test functions (`test_fw_list_json_on_failure_exits_1` and `test_fw_list_json_on_failure_emits_no_document`) instead of one combined test with two assertions. A single combined test only ever registers as one pytest failure regardless of how many of its internal `assert`s break, and the plan's acceptance criterion requires reverting the guard to fail *at least three* tests in the module — the split makes that number of independently-observable failures reachable.
- Used a small plain class (`_SuccessfulEmptyPageResponse`, exposing `json()`, `raise_for_status()`, `headers`) rather than `MagicMock` for the new module's successful-empty-page stub, since no call-recording is needed and the shape mirrors what `test_firmware_install.py`'s `mock_releases_factory` already establishes as the contract `_fetch_all_releases` reads.
- Kept the `logger.error` line inside `list_releases`'s exception arm exactly as it was (D-07): it is retained rationale for a reader, and in production it still reaches stdout through `SingleLineStatusHandler`. The new guard's contract is "no JSON document on stdout," not "stdout is silent" — documented explicitly in this module's tests and docstrings so the residue is not mistaken for an oversight.

## Deviations from Plan

None — plan executed exactly as written. The one adjustment worth flagging as a clarification rather than a deviation: the plan's task description for Task 2 sketched a single JSON-failure test; it was authored as two tests to satisfy the plan's own reachability acceptance criterion ("at least three tests in this module fail" on guard reversion), which a single combined test could not do. This is a faithful expansion of the plan's stated intent, not a departure from it.

## Issues Encountered

- Ran the plan's verify legs for `result.output` / `obj=` absence literally as written (`grep -c` with no `-F`, so `.` matches any character): the first draft of the module docstring used the exact substrings `result.output` and `obj=` in its own rationale prose (explaining *why not* to use them), which the same grep that polices the test bodies also matched. Reworded the docstring to describe both without ever spelling either substring contiguously (e.g. "the attribute that concatenates both streams into one" instead of naming `result.output`; "no injected `AppContext` is handed to `invoke`" instead of naming `obj=`). No test logic changed — this was a documentation-prose fix caught by re-running the plan's own verify commands before committing.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The `FIRESTARTER_RELEASES_URL` import added to `cli_handlers.py` and the `list_releases` two-state contract are available for `190-03`'s update-path work (D-06 guard), which touches the same service layer.
- `190-02`'s `test_endpoint_constants.py` pin and `190-04`'s evidence capture (redirect-count transcript, CI-equivalent run, slug sweep with its `henols/firestarter_prom` control) can both build directly on this plan's constants and tests without further changes here.
- No blockers. The live legs in this plan's verify block depend on `api.github.com` reachability, which was available throughout this session.

---
*Phase: 190-endpoints-that-do-not-depend-on-a-redirect*
*Completed: 2026-09-13*
