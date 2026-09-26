---
phase: 143-host-timeout-progress-pulse-override
plan: 06
subsystem: host-protocol
tags: [python, pytest, serial-protocol, progress-bar, tqdm, mock-autospec, host-02]

# Dependency graph
requires:
  - phase: 143-04
    provides: "WRITE_BLOCK_TIMEOUT_FALLBACK_S, EpromOperator._write_block_timeout(), _main_phase_send_data's response_timeout kwarg, and write_eprom's pulse_us parameter -- all in eprom_operations.py, the file this plan also edits"
  - phase: 143-05
    provides: "the firmware's time-gated MSG_DATA_PROGRESS (0xE0) emission from inside the per-byte write loop (leonardo/native only, compiled out on uno/uno328pb per BF-2) -- the frame this plan renders on the host side"
provides:
  - "EpromOperator._apply_write_progress(response, progress, start_addr) -> bool -- applies a mid-block MSG_DATA_PROGRESS frame's absolute-minus-start-address position directly, without ever calling set_progress() or send_ack()"
  - "_main_phase_send_data's DATA arm (between the ERROR branch and the '!= OK' raise) plus its firmware_drives_bar latch on the chunk-handoff update()"
  - "tests/test_write_progress.py (6 tests) -- render-not-raise, never-ack, offset arithmetic, no-rebuild, no-rewind, and the Uno-class non-regression control"
affects: [143-08, 143-10, 145, 146]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Latch a competing progress source via a boolean flag set from a helper's own return value, checked at the ONE call site that would otherwise double-count -- rather than deleting the original source (which would regress boards that never deliver the new one)"
    - "Bypass a shared render helper's rebuild-on-differing-total by performing its final three operations directly, instead of routing through it with an argument it would misinterpret"
    - "Delegating patch.object(..., autospec=True, side_effect=...) recorder applied to a plain (non-serial) method (ClassProgressHandler.start, SerialCommunicator.send_ack) to get an exact invocation count/argument list without a stub breaking control flow -- the same idiom 143-04 established for SerialCommunicator.get_response, generalized to two more methods"

key-files:
  created:
    - firestarter_app/tests/test_write_progress.py
  modified:
    - firestarter_app/firestarter/eprom_operations.py

key-decisions:
  - "Test 5's negative control was split into its own function (test_bar_still_advances_with_zero_progress_frames), as the plan explicitly permits ('six if test 5's negative is split') -- so the module collects 6 tests, not 5, and the full-suite count is 1568, not the plan's stated 1567. Recorded per the plan's own instruction: 'If the count differs, record the actual figure and account for the difference rather than adjusting the expectation silently.'"
  - "Tests 3, 4 and 5(positive) each needed an explicit `ok is True` check folded in specifically to avoid a vacuous pre-Task-2 pass -- a value recorded only BEFORE the loop's unconditional abort on the first DATA frame (the initial (0, total) callback entry; the single start() call) is identical whether or not the DATA branch exists. This mirrors Phase 143 Plan 04's own documented fix for the identical trap on ITS Test 4 and Test 5."
  - "_apply_write_progress placed between _main_phase_simple and _main_phase_send_data (inside the 'Main Phase Handlers' section, immediately before its only caller) -- the plan specifies the method's signature and behaviour but not its exact position in the file."

patterns-established:
  - "Pattern: latch a competing progress source via a boolean set from a helper's return value, not by deleting the original call site -- reusable anywhere two update mechanisms (a coarse handoff-based one and a fine frame-based one) must cooperate without one regressing the other's absent-delivery case."

requirements-completed: []

coverage:
  - id: D1
    description: "A mid-block MSG_DATA_PROGRESS frame on the write path is rendered (not raised on) and is never acked -- the DATA arm sits before _main_phase_send_data's 'got {type}' raise and never routes through _handle_progress_response"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_write_progress.py::test_data_frame_in_main_phase_is_rendered"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_write_progress.py::test_progress_frame_is_not_acked"
        status: pass
    human_judgment: false
  - id: D2
    description: "The bar position is absolute-minus-start-address (0xE0 carries an absolute chip address; the write bar's origin is the write's own start address) and the bar is never rebuilt despite a frame's total differing from file_size"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_write_progress.py::test_offset_write_bar_starts_at_zero"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_write_progress.py::test_differing_total_does_not_rebuild_the_bar"
        status: pass
    human_judgment: false
  - id: D3
    description: "A latch stops the chunk-handoff update() once the firmware starts driving the bar (no rewind across a two-chunk write), while a board that never delivers a mid-block frame keeps advancing via handoff alone (no regression to a dead bar)"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_write_progress.py::test_bar_does_not_rewind_when_firmware_drives_it"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_write_progress.py::test_bar_still_advances_with_zero_progress_frames"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-13
status: complete
---

# Phase 143 Plan 06: Host-Side Write Progress Rendering (HOST-02 Host Half) Summary

**A mid-block `MSG_DATA_PROGRESS` frame on the write path is now rendered instead of raised on, is never acked, positions the bar as `absolute - start_addr` without ever re-entering `set_progress`'s rebuild arm, and a latch stops the chunk-handoff `update()` once the firmware starts driving the bar -- while a board that never delivers a mid-block frame keeps today's handoff-based bar unchanged.**

## Performance

- **Duration:** ~35 min
- **Started:** ~2026-08-13T02:16:53Z (STATE.md hand-off from 143-05)
- **Completed:** 2026-08-13T02:49Z
- **Tasks:** 2 completed (both `type="auto"`, no checkpoints)
- **Files touched:** 2 (1 created, 1 modified)

## Accomplishments

- `firestarter/eprom_operations.py` gained `EpromOperator._apply_write_progress(response, progress, start_addr) -> bool`, placed between `_main_phase_simple` and `_main_phase_send_data`. It returns `False` (applying nothing) when the frame's message is absent or has no `"/"`, or when either half fails `(ValueError, TypeError)`-specific int conversion (copied verbatim from `_handle_progress_response`'s existing tolerance arm -- never a bare `except Exception`, which ruff's `[E, F, I, UP]` select would not flag). On success it computes `position = max(0, absolute - start_addr)`, sets `progress.current_step`, calls `progress.progress_callback` (if any) with `(position, progress.total_steps)`, updates `progress.pbar.n` + `refresh()` (if any) -- performing `set_progress`'s final three operations directly rather than calling it -- and returns `True`.
- `_main_phase_send_data` gained `start_addr = (eprom_data_dict or {}).get("address", 0)` and `firmware_drives_bar = False` before its loop, a `response.type == "DATA"` arm inserted between the ERROR branch and the `if response.type != "OK": raise` line (calling `_apply_write_progress` and latching `firmware_drives_bar = True` on a `True` return, then `continue` -- never acking, never reaching the raise), and the chunk-handoff `progress.update(len(data_chunk))` now fires only `if not firmware_drives_bar`.
- `tests/test_write_progress.py` (new, 6 tests): all five plan-mandated tests plus Test 5's split negative control, each pinning one of D-04/D-05/Pitfall 1/Pitfall 2 as described in Decisions Made below.
- Full host suite: **1568 passed** (1562 after plan 143-04, plus this plan's 6 -- see Decisions Made for why 6, not the plan's stated 5), coverage **82.87%** (>= 70% floor, up from 143-04's 82.80%). `ruff check` / `ruff format --check` clean. mypy watermark exit 0 (33 errors, unmoved from 143-04's baseline). `git diff` confirms zero hunks in `ClassProgressHandler`, `_handle_progress_response`, `_execute_phase`, `_calculate_buffer_size`, `_setup_operation`, `_boot_block_hint_message`, `verify_eprom`, `serial_comm.py`, `cli_handlers.py`, `constants.py`, or `messages.py`.
- `firestarter` (firmware) repo porcelain was clean before the coverage leg -- no L-6 deselection was needed (`git -C /workspaces/firestarter status --porcelain` returned nothing), recorded per the plan's instruction even though the empty case "needs no note."

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter_app` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Author `tests/test_write_progress.py` -- five (six) HOST-02 host-side tests, all RED** - `86c97ec` (test)
2. **Task 2: Add `_apply_write_progress`, the MAIN-phase DATA branch and the latch, and turn the module GREEN** - `6742367` (feat)

**Plan metadata:** committed in the meta repo (`/workspaces`), see below.

## Files Created/Modified

- `firestarter_app/firestarter/eprom_operations.py` - `_apply_write_progress` (new method); `_main_phase_send_data`'s `start_addr`/`firmware_drives_bar` locals, its new DATA arm, and its now-latched chunk-handoff `update()` call. Four hunks total, all inside the "Main Phase Handlers" section between `_main_phase_simple`'s end and `_main_phase_send_data`'s close -- `git diff` confirms zero hunks anywhere else in the file.
- `firestarter_app/tests/test_write_progress.py` (new, 6 tests) - HOST-02 host-side render/ack/offset/no-rebuild/no-rewind proofs, plus the Uno-class non-regression control.

## Decisions Made

- **Test 5's negative was authored as a split sibling function, per the plan's own explicit allowance** ("six if test 5's negative is split"). The module therefore collects 6 tests, and the full-suite count is **1568 passed**, not the plan's stated **1567** (1562 + 5). This is exactly the "record the actual figure and account for the difference" case the plan's own acceptance criteria anticipates -- the difference is fully explained by the permitted split, not a discrepancy.
- **Tests 3, 4 and 5 (positive half) each lead with, or fold in, an explicit `ok is True` check specifically to avoid a vacuous pre-Task-2 pass.** See "Genuine-RED Reasoning" below -- this mirrors Phase 143 Plan 04's own documented fix for the identical trap.
- **`_apply_write_progress`'s placement** (between `_main_phase_simple` and `_main_phase_send_data`) is not specified by the plan; chosen so the new write-only helper sits inside the "Main Phase Handlers" section, immediately before its only caller, rather than beside the phase-agnostic `_handle_progress_response` it is deliberately NOT built on top of.
- **`absolute, _total_ignored = map(int, ...)`** (matching `_handle_progress_response`'s exact existing idiom) rather than a generator-expression form -- `_handle_progress_response` is the file's own established precedent for this exact parse, and the plan instructs copying its tolerance arm verbatim.

## Genuine-RED Reasoning (D-25, and why three tests needed a compound assertion)

`_main_phase_send_data`'s loop raises unconditionally on the very first DATA frame it sees today (pre-Task-2), and that raise is caught by `_run_state_machine` and converted to `ok=False` -- no exception ever reaches a test. This means any test assertion built ONLY from values recorded strictly BEFORE that first frame is examined would be **identical** whether or not the DATA branch exists, and would therefore pass on the pre-Task-2 code for the wrong reason:

- **Test 3** (`test_offset_write_bar_starts_at_zero`): a literal "the first recorded position is 0" check is always true, because `ClassProgressHandler.start()` unconditionally records `(0, total)` as the very first callback entry, regardless of any frame ever arriving. Fixed by asserting `ok is True` first, then isolating the LAST two recorded positions (this drive's single chunk means exactly one handoff precedes the frames).
- **Test 4** (`test_differing_total_does_not_rebuild_the_bar`): a literal "`start()` called exactly once" check is also always true pre-Task-2, because the abort happens before any SECOND call to `start()` could ever occur -- the only call that ever fires is the initial `progress.start(file_size)`. Fixed with a single compound assertion, `ok is True and start_calls == [file_size]`, so the pre-Task-2 failure is genuine (on `ok`) rather than vacuous (on `start_calls` alone).
- **Test 5** (`test_bar_does_not_rewind_when_firmware_drives_it`): a "monotonically non-decreasing" or "exact position count" check over a TWO-ELEMENT list (`[0, chunk-1-handoff]`, the only entries recorded before the abort on chunk 1's own first frame) is trivially true. Fixed by asserting `ok is True` first.

This is the same trap Phase 143 Plan 04's SUMMARY documents for its own Test 4 and Test 5 ("both passed vacuously on the pre-Task-2 code... strengthened with a same-drive contrast assertion"), encountered here for the analogous reason: the shared abort-on-unexpected-response-type mechanism truncates the recorded evidence at exactly the point where the interesting behaviour would begin.

Tests 1 and 2 needed no such strengthening: Test 1's `ok is True` assertion IS the direct claim under test (the write must succeed despite a mid-block frame), and Test 2's `send_ack()` call-count comparison is disrupted by the SAME abort in a way that produces a genuine, non-vacuous mismatch (2 acks with the abort vs. 4 without) rather than an identical value either way.

## D-25 Evidence: RED before, GREEN after (verbatim)

**RED** (`pytest tests/test_write_progress.py -o addopts="" -v`, run against the code as committed at the end of Task 1, before any Task 2 edit):

```
collecting ... collected 6 items

tests/test_write_progress.py::test_data_frame_in_main_phase_is_rendered FAILED [ 16%]
tests/test_write_progress.py::test_progress_frame_is_not_acked FAILED    [ 33%]
tests/test_write_progress.py::test_offset_write_bar_starts_at_zero FAILED [ 50%]
tests/test_write_progress.py::test_differing_total_does_not_rebuild_the_bar FAILED [ 66%]
tests/test_write_progress.py::test_bar_does_not_rewind_when_firmware_drives_it FAILED [ 83%]
tests/test_write_progress.py::test_bar_still_advances_with_zero_progress_frames PASSED [100%]

========================= 5 failed, 1 passed in 3.75s ==========================
```

Each of the five failures' assertion message, with the captured firmware-side raise it stems from:

```
test_data_frame_in_main_phase_is_rendered:
  AssertionError: HOST-02: a mid-block MSG_DATA_PROGRESS frame must be rendered, not
  raised on -- ...; got ok=False
  assert False is True
  [log] ERROR EpromOperator: Programmer error during WRITE: Programmer did not
  request data chunk, got DATA: 2048/65536

test_progress_frame_is_not_acked:
  AssertionError: HOST-02/D-05: send_ack()'s call count with three mid-block progress
  frames present must equal the count with zero frames -- ...; got 2 (with frames,
  ok=False) vs 4 (zero frames)
  assert 2 == 4
  [log] ERROR EpromOperator: ... got DATA: 10/65536

test_offset_write_bar_starts_at_zero:
  AssertionError: HOST-02/D-04: a write with mid-block progress frames at a non-zero
  --address must still succeed; got ok=False
  assert False is True
  [log] ERROR EpromOperator: ... got DATA: 4096/65536

test_differing_total_does_not_rebuild_the_bar:
  AssertionError: HOST-02/D-04 (Pitfall 2): expected the write to succeed with
  ClassProgressHandler.start() invoked exactly once ...; got ok=False,
  start_calls=[8]
  assert (False is True)
  [log] ERROR EpromOperator: ... got DATA: 100/65536

test_bar_does_not_rewind_when_firmware_drives_it:
  AssertionError: HOST-02/Pitfall 1: a two-chunk write with mid-block progress frames
  for both chunks must succeed; got ok=False
  assert False is True
  [log] ERROR EpromOperator: ... got DATA: 600/65536
```

Every failure is on the predicted line (an `ok is True`/compound assertion, or the ack-count comparison), never on `ModuleNotFoundError`, an `AttributeError` on `EpromOperator`, or a collection error. `test_bar_still_advances_with_zero_progress_frames` (the split negative) PASSED at RED time, by design -- it exercises the handoff path alone, which this plan does not change (see Decisions Made and "Genuine-RED Reasoning" above); matches Phase 143 Plan 04's own Test 6 precedent of an honestly-recorded always-passing control.

**GREEN** (`pytest tests/test_write_progress.py -x -o addopts="" -v`, after Task 2's production edit):

```
collecting ... collected 6 items

tests/test_write_progress.py::test_data_frame_in_main_phase_is_rendered PASSED [ 16%]
tests/test_write_progress.py::test_progress_frame_is_not_acked PASSED    [ 33%]
tests/test_write_progress.py::test_offset_write_bar_starts_at_zero PASSED [ 50%]
tests/test_write_progress.py::test_differing_total_does_not_rebuild_the_bar PASSED [ 66%]
tests/test_write_progress.py::test_bar_does_not_rewind_when_firmware_drives_it PASSED [ 83%]
tests/test_write_progress.py::test_bar_still_advances_with_zero_progress_frames PASSED [100%]

============================== 6 passed in 3.65s ===============================
```

## Verification Results (final state)

| Check | Result |
|---|---|
| `pytest tests/test_write_progress.py -x -o addopts=""` | 6 passed |
| `pytest tests/test_eprom_operations.py tests/test_write_skip_sdp_unlock.py tests/test_write_response_budget.py tests/test_pulse_us_override.py -x -o addopts=""` | 61 passed |
| `pytest tests/ --cov=firestarter --cov-fail-under=70 -o addopts=""` | **1568 passed** (1562 + 6), coverage **82.87%** |
| `ruff check firestarter/ tests/` | All checks passed |
| `ruff format --check firestarter/ tests/` | 133 files already formatted |
| `tools/check_mypy_watermark.py` | exit 0; 33 errors, 2 below the 35 watermark (unmoved from 143-04) |
| `git diff --exit-code -- firestarter/serial_comm.py firestarter/cli_handlers.py firestarter/constants.py firestarter/messages.py` (vs pre-plan HEAD) | clean |
| `git diff` hunks in `firestarter/eprom_operations.py` | 4 hunks, all between `_main_phase_simple`'s end and `_main_phase_send_data`'s close |
| Grep `_apply_write_progress`'s body for an actual `.set_progress(`/`.send_ack(` call site | none found (only prose mentions in its own docstring, explaining what it deliberately avoids) |
| `git -C /workspaces/firestarter status --porcelain` (L-6 check, before the coverage leg) | clean -- no deselection needed |

## Deviations from Plan

None - plan executed exactly as written. (Test 5's split into two functions and the compound `ok is True` strengthening on Tests 3-5 are both explicitly anticipated and permitted by the plan's own text -- see Decisions Made and "Genuine-RED Reasoning" above, not deviations from it.)

## Issues Encountered

None. The `patch.object(..., autospec=True, side_effect=...)` recorder shape for `ClassProgressHandler.start` and `SerialCommunicator.send_ack` was sanity-checked with a small standalone probe script before being relied on in five tests (confirming, as Phase 143 Plan 04 empirically confirmed for `SerialCommunicator.get_response`, that the recorded `args` inside the wrapper already excludes `self`) -- this avoided any wasted RED/GREEN iteration on a wrong assumption about mock argument binding.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HOST-02's host-side rendering is complete and verified independently of any hardware: this module proves the write path RENDERS a mid-block frame correctly (not-raised, not-acked, correctly offset, non-rebuilding, non-rewinding, and non-regressing for boards that deliver none) -- it does **not** prove *delivery* (a firmware/board property; D-06's non-claim, EPROM path only, `leonardo` only, proven by plan 143-05 and pinned mechanically by plan 143-08's Leonardo-only source-contract gate) and it does **not** prove real bar motion on hardware (Phase 145's).
- This plan intentionally marks no requirement Complete (frontmatter `requirements: []`, `requirements-completed: []` here); plan **143-10** flips the `HOST-*` checkboxes once every plan's evidence (including firmware and bench) exists.
- `_drive_write_with_progress_frames` and `_fresh_serial_and_comm` (this module) are reusable analogs for any later plan needing a hardware-free write drive with controllable mid-block `MSG_DATA_PROGRESS` frames.
- No blockers. `ClassProgressHandler`, `_handle_progress_response`, `_execute_phase`, `verify_eprom`, `serial_comm.py`, `cli_handlers.py`, `constants.py` and `messages.py` are all confirmed untouched by `git diff`.
- Plan 143-07 runs in the same wave against the same `firestarter_app` checkout (per 143-05's own "Wave 3, and why not wave 2" note) -- this plan's own porcelain scope check at Task 1 (`git status --porcelain -- tests/test_write_progress.py firestarter/eprom_operations.py`) was deliberately narrowed for exactly that reason and showed no interference.

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/eprom_operations.py` (modified)
- FOUND: `firestarter_app/tests/test_write_progress.py` (created)
- FOUND commit `86c97ec` (Task 1)
- FOUND commit `6742367` (Task 2)

---
*Phase: 143-host-timeout-progress-pulse-override*
*Completed: 2026-08-13*
