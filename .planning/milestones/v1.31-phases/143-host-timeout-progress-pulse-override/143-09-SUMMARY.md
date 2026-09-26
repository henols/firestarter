---
phase: 143-host-timeout-progress-pulse-override
plan: 09
subsystem: host-protocol
tags: [python, pytest, error-handling, serial-protocol, tokenize, host-03]

# Dependency graph
requires:
  - phase: 143-06
    provides: "EpromOperator._apply_write_progress(), _main_phase_send_data's DATA arm and firmware_drives_bar latch -- all in eprom_operations.py, the same file this plan edits (read for context, not modified)"
  - phase: 143-07
    provides: "write's --pulse-us option (click.IntRange(1, 65535), default=None) in cli_handlers.py -- this plan's 0xAE remediation hint names it using its real, shipped spelling"
provides:
  - "_BUDGET_FAILURE_IDS (0xBD/0xBE/0xAE, deliberately excluding the dead 0xB1 per D-20/F-141-06) in eprom_operations.py's module-level constant block"
  - "_budget_failure_hint_message(response) -> Optional[str] -- a second id-keyed hint function on the _boot_block_hint_message seam: for 0xBD/0xBE states the write aborted, what was and was not programmed, and that the firmware stops accepting blocks for this write (D-21); for 0xAE (pre-flight, before any high voltage) names --pulse-us and the refused width (D-16)"
  - "_main_phase_send_data's ERROR branch now composes both the boot-block hint and the budget-failure hint via the same ' -- ' join, disjoint by id today but not by construction"
  - "tests/test_budget_failure_render.py (4 tests) -- the 0xBD/0xBE program-failure render, the 0xAE remediation clause, D-21's forbidden-substring no-continuation-wording proof, and D-20's dead-id source-contract leg"
affects: [143-10, 145, 146]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A second id-keyed hint function added beside an existing one (_boot_block_hint_message), both computed unconditionally in the ERROR branch and joined via a loop over (hint, budget_hint) rather than a fixed two-branch if/elif -- so a third future hint could be added without changing the composition shape, and two hints being simultaneously present (not possible today, since the ids are disjoint) would still produce one readable message"
    - "Python-source comment-stripping via the stdlib tokenize module (COMMENT-token spans blanked to same-shape whitespace) rather than a naive '#-to-end-of-line' regex scan -- this specific scan target (eprom_operations.py) builds its COBS wire frame with a literal `#` marker byte inside a bytes literal (frame = b\"#\" + body + b\"\\x00\"), which a naive scanner would misparse as a comment start"
    - "A source-contract non-vacuity check that pivots on a POSITIVE presence assertion (the new id's name must appear once Task 2 lands) rather than only a negative absence assertion -- this is what makes a 'nothing keys on the dead id' test genuinely RED before the keying mechanism exists, instead of vacuously true throughout, without requiring the test to import the not-yet-existing symbol at module scope"

key-files:
  created:
    - firestarter_app/tests/test_budget_failure_render.py
  modified:
    - firestarter_app/firestarter/eprom_operations.py

key-decisions:
  - "_BUDGET_FAILURE_IDS is a tuple of raw ints (0xBD, 0xBE, 0xAE) with a comment naming each, not a tuple built from imported names -- the plan permitted either shape, and a module-level import of firestarter.messages would have broken the file's existing avoid-import-cycle discipline (every other message-id lookup in this module is a LOCAL import inside a function)."
  - "The 0xB1 exclusion is named by its bare identifier (MSG_ERR_WRITE_FAILED) only inside the #-comment above _BUDGET_FAILURE_IDS -- never inside _budget_failure_hint_message's own docstring, which refers to it only as \"error id 0xB1\". Discovered via Task 2's own verification: a docstring is a STRING token, not a COMMENT token, so tokenize-based comment-stripping (this plan's Test 4 mechanism) does not remove it, and the bare name would have tripped the '0xB1 absent' assertion the moment the docstring shipped it. See Deviations below."
  - "Test 1's exact-type assertion is `type(exc) is EpromOperationError`, not `isinstance(exc, EpromOperationError)` -- ProtocolNotImplementedError is a subclass of EpromOperationError (confirmed by reading tests/test_error_code_seam.py's own Test 3 before writing this), so isinstance() alone would not have distinguished 'raised the 0xBB fork by mistake' from 'raised the plain path correctly'."
  - "The 0xAE hint parses the refused width back out of response.message via a new _PULSE_WIDTH_RE (mirrors _TIMEOUT_ADDR_RE's existing extract-from-text approach immediately above it in the same constant block) rather than requiring a caller to pass it separately -- Test 2 requires the hint ITSELF (not just the composed exception message, which already contains the width via response.message) to name the refused value, so the width must be extracted and re-embedded."
  - "Every one of Test 3's seven forbidden phrases (retry/retrying/try again/resume/resuming/continue from/re-run this block) is built by string concatenation, and Test 3 asserts none of them appears verbatim anywhere in this test module's own source -- this required rewording two unrelated prose passages (an early draft used 'block-retry' and named the third test 'test_hint_offers_no_retry_and_no_resumption', both of which contain 'retry' contiguously) before the module was ever run. Caught by a scratch validation script before writing the real file, not by a failing self-check."

patterns-established:
  - "Pattern: when a new pure hint function is added beside an existing one on the same id-keyed seam, compute both unconditionally and join present ones in a loop, with a comment stating the ids are disjoint today but the composition does not depend on it -- reusable for any future third hint on this seam."
  - "Pattern: a Python source-contract test that needs a genuine pre-implementation RED (not a vacuous pass) without importing the not-yet-existing symbol at module scope should import it LOCALLY inside the test/helper function -- the resulting ImportError propagates as an individual per-test failure (pytest.raises() only swallows the type it names), never a whole-module collection error."

requirements-completed: []

coverage:
  - id: D1
    description: "HOST-03 / D-19: a 0xBD (MSG_ERR_MAX_PULSES) or 0xBE (MSG_ERR_ENERGY_CAP) budget failure surfaces as EpromOperationError (never the 0xBB ProtocolNotImplementedError fork) carrying the matching error_code and a message naming the failing address in the catalog's 0x%06x form, plus a non-None disposition hint"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_budget_failure_render.py::test_max_pulses_is_a_program_failure"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_budget_failure_render.py::test_energy_cap_and_pulse_too_wide"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-16: MSG_ERR_PULSE_TOO_WIDE (0xAE), a pre-flight refusal raised before any high voltage is enabled, surfaces with a hint naming --pulse-us literally and the exact refused width the firmware reported"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_budget_failure_render.py::test_energy_cap_and_pulse_too_wide"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-21: the 0xBD/0xBE hint states the write aborted, what was and was not programmed, and that the firmware stops accepting blocks for this write, while containing none of seven forbidden continuation/repeat phrases (machine-checked, concatenation-built, and proven absent from the test module's own source); the 0xAE hint is the permitted exception, naming --pulse-us"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_budget_failure_render.py::test_hint_states_abort_without_continuation_wording"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-20 / F-141-06: no host path keys on MSG_ERR_WRITE_FAILED (0xB1) for the 27C family -- a non-vacuous, comment-stripped source-contract leg over eprom_operations.py, re-confirmed by a fresh firmware-side grep this session"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_budget_failure_render.py::test_no_host_path_expects_write_failed_on_27c"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-08-13
status: complete
---

# Phase 143 Plan 09: Budget-Failure Render and Remediation Hint (HOST-03) Summary

**A 0xBD/0xBE per-byte program-budget failure now raises `EpromOperationError` naming the failing address plus a hint stating the write aborted and the firmware will not accept another block for it (no continuation implied), and a 0xAE pre-flight `--pulse-us` refusal raises with a hint naming the flag and the exact refused width -- both composed on the existing `_boot_block_hint_message` seam, with zero new exception types or message ids.**

## Performance

- **Duration:** ~30 min
- **Started:** ~2026-08-13T04:11Z (STATE.md hand-off from 143-08)
- **Completed:** 2026-08-13T04:41Z
- **Tasks:** 2 completed (both `type="auto"`, no checkpoints)
- **Files touched:** 2 (1 created, 1 modified)

## Accomplishments

- `firestarter/eprom_operations.py` gained `_BUDGET_FAILURE_IDS = (0xBD, 0xBE, 0xAE)` and `_PULSE_WIDTH_RE` in the module-level constant block (beside `_BOOT_BLOCK_SIZE`/`_TIMEOUT_ADDR_RE`/`_FLASH4_PROTOCOL_ID`/`WRITE_BLOCK_TIMEOUT_FALLBACK_S`), and a new module-level `_budget_failure_hint_message(response) -> Optional[str]` inserted immediately after `_boot_block_hint_message`. For `MSG_ERR_MAX_PULSES`/`MSG_ERR_ENERGY_CAP` it returns a fixed disposition hint: the write aborted at this address, bytes before the block were already programmed, the block is partially programmed, no later block was attempted, the firmware stops accepting blocks for this write, and a byte that will not converge usually means insufficient program voltage or a worn/failing cell -- with none of D-21's seven forbidden continuation phrases. For `MSG_ERR_PULSE_TOO_WIDE` it parses the refused width out of `response.message` via `_PULSE_WIDTH_RE` and returns a hint naming `--pulse-us` and that exact width, stating no byte was programmed and the chip is unchanged (returns `None` if the width cannot be parsed, mirroring `_boot_block_hint_message`'s own "no hint without a parsable value" precedent).
- `_main_phase_send_data`'s ERROR branch now computes both `_boot_block_hint_message` and `_budget_failure_hint_message` unconditionally and joins whichever are present with the existing `" -- "` separator (a `for extra_hint in (hint, budget_hint):` loop, commented that the ids are disjoint today but the composition does not depend on it) before calling the unchanged `_raise_for_error_response`.
- `tests/test_budget_failure_render.py` (new, 4 tests): the 0xBD program-failure render, the 0xBE render plus the 0xAE remediation clause, D-21's forbidden-substring no-continuation-wording contract (with its own concatenation-needle self-check), and D-20's comment-stripped dead-id source-contract leg with a non-vacuity guard.
- Full host suite: **1578 passed** (1574 after 143-07, plus this plan's 4), coverage **82.92%** (>= 70% floor, up from 143-07's 82.89%). `ruff check`/`ruff format --check` clean. mypy watermark exit 0 (33 errors, unmoved from 143-06/143-07's baseline). `git diff` confirms exactly 3 hunks in `eprom_operations.py` (the constant block, the new function, the ERROR-branch composition) and zero hunks in `messages.py`, `serial_comm.py`, `cli_handlers.py`, or `constants.py`.
- D-20 re-confirmed fresh this session, twice: `grep -rn "MSG_ERR_WRITE_FAILED" src/` run inside `/workspaces/firestarter` returns zero matches (exit 1) both before Task 1 and again at final verification.
- `firestarter` (firmware) repo porcelain was clean before the coverage leg -- no L-6 deselection was needed (`git -C /workspaces/firestarter status --porcelain` returned nothing, checked before Task 2's coverage leg), recorded per the plan's instruction even though the empty case "needs no note."

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter_app` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Author `tests/test_budget_failure_render.py` -- four HOST-03 tests including the D-20 source-contract leg, all RED** - `154d35b` (test)
2. **Task 2: Add `_BUDGET_FAILURE_IDS` and `_budget_failure_hint_message`, wire them into the ERROR branch, and turn the module GREEN** - `f77b0ea` (feat)

**Plan metadata:** committed in the meta repo (`/workspaces`), see below.

## Files Created/Modified

- `firestarter_app/firestarter/eprom_operations.py` - `_BUDGET_FAILURE_IDS`, `_PULSE_WIDTH_RE` (new constants); `_budget_failure_hint_message` (new function); `_main_phase_send_data`'s ERROR branch now composes it alongside `_boot_block_hint_message`. Three hunks total -- `git diff` confirms zero hunks anywhere else in the file, including `_boot_block_hint_message`, `_raise_for_error_response`, `ClassProgressHandler`, `_handle_progress_response`, `_execute_phase`, `_apply_write_progress`, `_write_block_timeout` and `_setup_operation`.
- `firestarter_app/tests/test_budget_failure_render.py` (new, 4 tests) - HOST-03 render/hint/no-continuation/dead-id proofs, mirroring `tests/test_boot_block_hint.py`'s synthetic-`Response` shape.

## Decisions Made

- **`_BUDGET_FAILURE_IDS` is a raw-int tuple with a naming comment, not an imported-name tuple.** The plan offered both shapes; a module-level import of `firestarter.messages` would have broken this module's existing avoid-import-cycle discipline (every other message-id lookup here is a local import inside a function), so the raw-int-plus-comment form was the only one consistent with the established pattern.
- **The 0xB1 exclusion is spelled out by name only inside a `#`-comment, never inside `_budget_failure_hint_message`'s own docstring.** See "Deviations from Plan" below -- this was a genuine mid-task discovery, not a decision made in advance.
- **Test 1 asserts `type(exc) is EpromOperationError`, not `isinstance(exc, EpromOperationError)`.** `ProtocolNotImplementedError` is a subclass of `EpromOperationError` (confirmed by reading `tests/test_error_code_seam.py`'s own Test 3 before writing this test), so `isinstance()` alone would pass even if `_raise_for_error_response` had wrongly forked through the 0xBB path.
- **The 0xAE hint re-parses and re-embeds the refused width** (via a new `_PULSE_WIDTH_RE`, mirroring `_TIMEOUT_ADDR_RE`'s existing pattern) rather than relying on the width already being present in `response.message` alone -- Test 2's own wording requires the hint itself, not just the final composed exception text, to name the value.
- **Test 3's seven forbidden phrases are concatenation-built, and the module is self-checked to contain none of them verbatim** -- an early draft's prose (`"block-retry"` and a test function named `test_hint_offers_no_retry_and_no_resumption`) both contained `"retry"` contiguously and were reworded before the file was ever committed, caught by a scratch validation script rather than a failing test.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `_budget_failure_hint_message`'s docstring initially spelled out `MSG_ERR_WRITE_FAILED` by name, defeating Test 4's own absence check**
- **Found during:** Task 2 (running `tests/test_budget_failure_render.py -x` to confirm GREEN)
- **Issue:** The docstring's D-20 paragraph originally read "...never on `MSG_ERR_WRITE_FAILED` (0xB1)...". Docstrings are Python `STRING` tokens, not `COMMENT` tokens, so Test 4's `tokenize`-based comment-stripper (correctly) leaves them untouched -- meaning the bare identifier survived stripping and tripped the "0xB1's name must be absent" assertion, which is a genuine correctness signal (the whole point of D-20) rather than a test bug.
- **Fix:** Reworded the docstring to say "never on error id 0xB1 ... see `_BUDGET_FAILURE_IDS`'s own comment, above, for its name" -- the bare identifier now appears exactly once in the file, inside the `#`-comment directly above `_BUDGET_FAILURE_IDS`, which the stripper does remove before the scan.
- **Files modified:** `firestarter_app/firestarter/eprom_operations.py`
- **Verification:** all 4 tests pass after the reword; `git diff` confirms the change is confined to one docstring paragraph, no behavioural change.
- **Committed in:** `f77b0ea` (bundled with Task 2's production commit -- the reword corrects the very function being authored in that same commit, matching 143-07's own precedent for a same-commit correction discovered while turning that task's target module GREEN).

**2. [Rule 1 - Bug] Two prose spots in the test module itself contained "retry" contiguously, which would have failed the module's own concatenation self-check**
- **Found during:** Task 1 (pre-flight validation of the drafted test module, before ever running it)
- **Issue:** An early draft's module docstring used the phrase "the OLD block-retry loop's failure id" (twice) and Test 3 was originally named `test_hint_offers_no_retry_and_no_resumption` -- both contain the literal substring `"retry"`, which Test 3's own self-check (`needle not in own_text`) would have flagged as a forbidden needle appearing verbatim in the module's own source.
- **Fix:** Reworded both prose mentions to "the OLD, now-retired per-block loop's failure id" and renamed the test function to `test_hint_states_abort_without_continuation_wording`.
- **Files modified:** `firestarter_app/tests/test_budget_failure_render.py`
- **Verification:** confirmed via a standalone scratch script checking all seven forbidden needles against the drafted file's raw text before the file was ever written to its real path; re-confirmed after the file was written and after `ruff format` touched it.
- **Committed in:** `154d35b` (Task 1's own commit -- caught before the file was ever run, not a post-hoc fix).

---

**Total deviations:** 2 auto-fixed (both Rule 1, both self-caught before or during the task's own GREEN verification, neither escaping to a later task or a failing CI run).
**Impact on plan:** Both fixes are wording-only corrections inside the two files this plan already owns (the new function's docstring; the new test module's own prose and one test name) -- neither touches `_boot_block_hint_message`, `_raise_for_error_response`, or any file outside this plan's declared scope. No scope creep.

## Issues Encountered

- **Genuine-RED design for Test 4 required more care than a simple absence check.** A source-contract leg that only asserts "0xB1's name is absent from `eprom_operations.py`" would be vacuously true both before AND after Task 2 (that name was never going to be added either way), which is exactly the T-143-HINTVACUOUS threat the plan's own threat register names. Fixed by pairing it with a POSITIVE non-vacuity assertion -- "0xBD's name IS present" -- which is false before Task 2 (confirmed by grep: neither name appears in the file pre-plan) and true after (once `_BUDGET_FAILURE_IDS`'s comment names it), making the leg genuinely RED-then-GREEN rather than a standing-true control. This mirrors the phase's established "avoid a vacuous pre-Task-2 pass" discipline (143-04's Test 4/5, 143-06's Tests 3-5), applied here to a source-scan leg rather than a behavioural one.
- **Confirmed, rather than assumed, that a naive comment-stripper would be unsafe on this specific file.** `eprom_operations.py` builds its COBS wire frame with `frame = b"#" + body + b"\x00"` -- a `#`-to-end-of-line regex scan would misparse the marker byte inside the bytes literal as a comment start and truncate the line. Verified with a standalone probe script (comparing the stripped output's exact bytes on that line against the original) before relying on the `tokenize`-based stripper in the real test module.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HOST-03's render-and-hint half is complete and verified independently of any hardware: a 0xBD/0xBE/0xAE error now surfaces with the right exception type, the right `error_code`, an address (or width) in the message, and a hint with the correct disposition and no continuation implication. HOST-03's OTHER half (the 10s write-path timeout that used to fire before this error frame was ever seen) was fixed by plan 143-04, independently -- neither plan alone satisfies the requirement.
- This plan intentionally marks no requirement Complete (frontmatter `requirements: []`, `requirements-completed: []` here, matching plans 143-06/143-07's own precedent); plan **143-10** flips the five `HOST-*` checkboxes once every piece of phase evidence exists.
- The `tokenize`-based Python comment-stripper (`_strip_py_comments`, this module) and the "pair an absence check with a positive non-vacuity presence check" pattern are both reusable analogs for any later plan needing a genuinely-RED Python source-contract test in this repo.
- No blockers. `_boot_block_hint_message`, `_raise_for_error_response`, `ClassProgressHandler`, `_handle_progress_response`, `_execute_phase`, `_apply_write_progress`, `_write_block_timeout`, `_setup_operation`, `messages.py`, `serial_comm.py`, `cli_handlers.py` and `constants.py` are all confirmed untouched by `git diff`. `/workspaces/firestarter` (firmware) porcelain is confirmed clean at this plan's end -- this plan wrote nothing there, per its own `commits_land_in: [firestarter_app, firestarter]` (the latter read-only).

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_budget_failure_render.py` (created)
- FOUND: `firestarter_app/firestarter/eprom_operations.py` (modified)
- FOUND commit `154d35b` (Task 1)
- FOUND commit `f77b0ea` (Task 2)

---
*Phase: 143-host-timeout-progress-pulse-override*
*Completed: 2026-08-13*
