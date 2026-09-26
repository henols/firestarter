---
phase: 132-retire-dev-sdp-discharge-the-mypy-debt
plan: 07
subsystem: cli
tags: [sdp, retirement, tripwire, d-14, mypy]

# Dependency graph
requires:
  - phase: 132-06
    provides: "measured mypy baseline of 32 (checked 122 source files, watermark 35), plus the typed make_app_context delegate in tests/test_write_skip_sdp_unlock.py that plan 132-05 already installed"
provides:
  - "A comment-only tripwire at the host's write auto-unlock DECISION site in cli_handlers.py (not the ring-fenced audit site), naming RETIRE-01 and the companion test, plus pointer comments at both places a developer would actually edit to disable the default"
  - "A short append-only note at FLAG_SKIP_SDP_UNLOCK's definition in constants.py, pointing back at the decision site and the named test, with the pre-existing firmware-sync caveat preserved verbatim"
  - "test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on in tests/test_write_skip_sdp_unlock.py -- named for the dependency, asserting both the auto-set-when-refused leg and the discriminating not-set-when-allowed leg, proven RED on a planted inversion with a legible failure message, then reverted to a clean tree"
  - "RETIRE-07 marked Complete in REQUIREMENTS.md"
affects: [132-09]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Tripwire-by-construction placement: a safety argument recorded as a comment adjacent to every line a developer would actually edit (the decision condition plus both its defaults), each proven within a measured line distance, rather than a comment placed once anywhere in the file"
    - "Independent (fake_serial, make_comm) pair construction inside a test body, mirroring conftest.py's fixture factory verbatim, for a test that needs two full independent write drives in one function -- the fixture-injected pair cannot be reused because the first successful write's SerialCommunicator closes its fake serial port"
    - "RED-then-improve-message-then-revert as an explicit in-task step for a tripwire test: plant the exact inversion the tripwire guards against, read the raw assertion failure, add a descriptive assertion message if the raw failure is opaque, re-confirm the improved message is legible, then revert and re-confirm GREEN and a clean diff"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/constants.py
    - firestarter_app/tests/test_write_skip_sdp_unlock.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The decision-site comment sits directly above `if is_protocol_0x0d and not allowed and not skip_sdp_unlock:` (line 653), not near the plan-cited coordinates from 132-CONTEXT.md's D-14 paragraph or the pattern map's `:622-645` range -- both had shifted by the time this plan ran (132-05/06 edited nothing in this function, but re-measurement per D-14's own discipline still applied). Re-measured live rather than trusted."
  - "The tripwire test reuses the module's existing _drive_write helper for both legs but cannot reuse the same fixture-injected (fake_serial, make_comm) pair for the second leg, because the first successful write closes its fake serial port. Added a small local `_fresh_serial_and_comm()` helper in the test file (not conftest.py, which is out of this plan's files_modified list) that duplicates conftest's make_comm factory body exactly, scoped to this one test's need."
  - "The RED demonstration's raw assertion (`assert (0 & 256)`) was judged opaque and improved with a descriptive message naming RETIRE-01/RETIRE-07/D-14 and the invalidated decision, before the plant was reverted -- per the task's own instruction to improve the assertion message if the failure text does not make the invalidated decision legible to someone who did not write it."
  - "Test 2's discriminating leg (capability-allowed 0x0D part must NOT get the bit) also received a descriptive failure message, even though it was not the leg exercised by the planted inversion, so a future developer who breaks that direction instead gets the same legible failure text."

requirements-completed: [RETIRE-07]

coverage:
  - id: D1
    description: "A tripwire comment sits at the host auto-unlock decision site, naming RETIRE-01 and the companion test; pointer comments sit at both default sites a developer would actually edit; a note is appended at the flag definition, with the existing firmware-sync caveat preserved verbatim."
    verification:
      - kind: unit
        ref: "grep -c RETIRE-01 firestarter/cli_handlers.py -- 4; grep -c test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on firestarter/cli_handlers.py -- 1; grep -c D-14 firestarter/cli_handlers.py -- 6 (3 new + 3 pre-existing, unrelated D-14 uses at :949/:1078/:1104); grep -c D-14 firestarter/constants.py -- 1; grep -c test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on firestarter/constants.py -- 1"
        status: pass
      - kind: unit
        ref: "git diff -- firestarter/constants.py | grep -cE '^-[^-]' -- 0 (pure addition, firmware-sync caveat survives verbatim)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every line a developer would edit to disable auto-unlock is within 10 lines of a tripwire comment, and that enumeration is recorded (D-14's criterion: reachability, not coordinates)."
    verification:
      - kind: unit
        ref: "measured line distances (see Reachability Enumeration below) -- max distance 5 lines, all under the 10-line bound"
        status: pass
    human_judgment: false
  - id: D3
    description: "The diff on the CLI handler is comment-only; no output was added to the write path; the constants edit is pure addition; the ring-fenced eprom_operations.py and pyproject.toml are untouched."
    verification:
      - kind: unit
        ref: "git diff HEAD~2 -- firestarter/cli_handlers.py | grep -E '^[+-][^+-]' | grep -vcE '^[+-]\\s*#' -- 0; git diff HEAD~2 -- firestarter/cli_handlers.py | grep -cE '^\\+[^+].*(click\\.echo|logger\\.)' -- 0; git diff --stat firestarter/eprom_operations.py pyproject.toml -- empty"
        status: pass
    human_judgment: false
  - id: D4
    description: "The named test exists with its byte-exact name, asserts both directions, and has been seen to fail on an inverted condition with a legible message; it added no mypy error."
    verification:
      - kind: unit
        ref: "grep -c 'def test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on' tests/test_write_skip_sdp_unlock.py -- 1; docstring regex asserts RETIRE-01/RETIRE-07/D-14 all present -- DOCSTRING OK"
        status: pass
      - kind: integration
        ref: "planted inversion (negated the capability check in the auto-set condition) -> test failed with a message naming the invalidated decision -> reverted -> git diff --stat cli_handlers.py empty -> test passes again"
        status: pass
      - kind: integration
        ref: "bash tools/ci_replica_venv.sh -- all 5 legs PASS; Leg 4: 'Found 32 errors in 12 files (checked 122 source files)', 'mypy errors: 32 (watermark: 35)' -- no higher than plan 132-06's 32"
        status: pass
    human_judgment: false
  - id: D5
    description: "The full test suite remains green and ruff stays clean after all three tasks."
    verification:
      - kind: unit
        ref: "python -m pytest tests/ -q -- 1296 passed, 30 snapshots passed; ruff check firestarter/ tests/ and ruff format --check firestarter/ tests/ -- both exit 0"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-03
status: complete
---

# Phase 132 Plan 07: The RETIRE-07 Tripwire -- Comment at the Decision Site + a Named Test Summary

**Placed a comment-only tripwire at the host's write auto-unlock DECISION site in `cli_handlers.py` (not the ring-fenced audit site the record's stale coordinate pointed at), a pointer note at the flag's definition in `constants.py`, and one named test in `test_write_skip_sdp_unlock.py` that has been seen to fail on a planted inversion of the condition it pins -- mypy holds at 32, unchanged from plan 132-06.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-03T20:45:00Z (STATE.md's prior session marker, 132-06 complete)
- **Completed:** 2026-08-03T21:30:00Z (approximate)
- **Tasks:** 3
- **Files modified:** 4 (`cli_handlers.py`, `constants.py`, `test_write_skip_sdp_unlock.py`, `REQUIREMENTS.md`)

## Accomplishments

- **Task 1 (D-14, RETIRE-07):** Re-measured the decision site live rather than trusting either `132-CONTEXT.md`'s D-14 coordinates or the pattern map's `:622-645` range. The actual auto-set condition, unchanged since Phase 120/122, is `if is_protocol_0x0d and not allowed and not skip_sdp_unlock:` at line **653**. Added a 16-line decision-site comment directly above it, naming RETIRE-01 (the removal this tripwire protects), the named test, and the constants.py note, tagged D-14/RETIRE-07 throughout. Added two 5-line pointer comments at the two places a developer would actually edit to disable the default: above `_build_op_flags`'s `skip_sdp_unlock: bool = False` parameter (line 306) and above the `--skip-sdp-unlock` Click option decorator whose `default=False` sits at line 571. The write handler's own `skip_sdp_unlock: bool` parameter (line 578, unchanged) is a required, non-defaulted parameter, per the plan's own correction to `132-CONTEXT.md` -- it received no pointer, as instructed. Verified the diff is comment-only (`git diff | grep -vE '^[+-]\s*#'` returns 0 non-comment changed lines) and that no `click.echo`/`logger.` line was added. Committed as `5ec3a89`.
- **Task 2 (D-14):** Appended an 11-line note to the existing comment block above `FLAG_SKIP_SDP_UNLOCK = 0x100` in `constants.py`, stating the same dependency from the constant's point of view and pointing at both the decision site and the named test. The existing firmware-sync caveat (the `0x100`/no-`0x200` clarification and the `CTRL_VPP_VPE_DROP_ENABLE` disambiguation) survives verbatim -- confirmed by `git diff | grep -cE '^-[^-]'` returning 0 (pure addition). The flag's value (`0x100`) is unchanged; the stale-anchor block near `:67-72` (plan 132-08's territory) was read but not touched. Committed as `1fdb455`.
- **Task 3 (RETIRE-07):** Added `test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on` to `tests/test_write_skip_sdp_unlock.py`, reusing the module's existing `_drive_write` helper for both legs: a capability-refused 0x0D part (`FM28V020`) with no flag gets the bit auto-set plus the mandatory report line, and a capability-allowed 0x0D part (`AT28C256`) with no flag does not get the bit set (the discriminating leg against a blanket unconditional set). Discovered mid-task that the module's fixture-injected `(fake_serial, make_comm)` pair cannot be reused for a second `_drive_write` call within the same test: the first successful write's `SerialCommunicator` closes its fake serial port (`_FakeSerial.close()` sets `is_open = False`), so the second drive failed with "Not connected" -- not the RED demonstration, a plain test bug from fixture reuse. Fixed by adding a small local `_fresh_serial_and_comm()` helper (test-file-local, not a `conftest.py` edit, which is outside this plan's file scope) that duplicates `conftest.py`'s `make_comm` factory body exactly, used only for the second leg. See "Deviations from Plan" below.
  - **RED demonstration:** planted `if is_protocol_0x0d and allowed and not skip_sdp_unlock:` (negated the capability check) in `cli_handlers.py`, ran the named test, and got a raw `assert (0 & 256)` failure -- judged opaque per the task's own instruction, since it names no decision. Improved all three assertions in the new test with descriptive messages naming RETIRE-01/RETIRE-07/D-14 and the invalidated decision; re-ran with the plant still active and confirmed the improved message is legible (verbatim below). Reverted the plant, confirmed `git diff --stat firestarter/cli_handlers.py` was empty, and confirmed the test passes again.
  - Verified via `bash tools/ci_replica_venv.sh`: all 5 legs PASS, mypy holds at **32 errors in 12 files (checked 122 source files)** against watermark 35 -- unchanged from plan 132-06, so the new test introduced no mypy error.
- **Requirements marked Complete: RETIRE-07.** No other RETIRE id touched (`git diff .planning/REQUIREMENTS.md` confirmed changes confined to the RETIRE-07 checkbox line and its Traceability-table row).

## Reachability Enumeration (D-14's criterion, not a grep)

Every line a developer would edit to disable the host's auto-unlock, and the nearest tripwire comment's distance to it, measured post-commit:

| Edit point | Line | Nearest tripwire comment | Distance |
|---|---|---|---|
| `_build_op_flags`'s `skip_sdp_unlock: bool = False` default | `cli_handlers.py:306` | comment block starts `:301` | 5 lines |
| `--skip-sdp-unlock` Click option's `default=False` | `cli_handlers.py:571` | comment block starts `:562` | 5 lines (comment sits directly above the `@click.option(` decorator, which opens 4 lines before `default=False` itself) |
| The auto-set decision condition | `cli_handlers.py:653` | comment block starts `:636`, ends `:652` | 1 line |

All three distances are well under the plan's 10-line bound. The write handler's own `skip_sdp_unlock: bool` parameter (`:578`) is a required, non-defaulted parameter and is not an edit point for disabling the default -- correctly excluded per the plan's own correction.

## RED Demonstration (verbatim)

**Plant:** in `cli_handlers.py`, changed the decision line from
`if is_protocol_0x0d and not allowed and not skip_sdp_unlock:` to
`if is_protocol_0x0d and allowed and not skip_sdp_unlock:  # RETIRE-07 PLANTED INVERSION -- negated capability check`.

**Before improving the assertion message**, the raw failure was:
```
>       assert refused_captured["command_dict"]["flags"] & FLAG_SKIP_SDP_UNLOCK
E       assert (0 & 256)
```
Judged opaque -- it names no decision, so a developer with no context would not know what broke.

**After improving the assertion message**, re-run with the plant still active:
```
E       AssertionError: RETIRE-07/D-14 TRIPWIRE FIRED: a capability-refused protocol-0x0D part did NOT get FLAG_SKIP_SDP_UNLOCK auto-set on a plain write. The host's SDP auto-unlock is no longer default-on for this case, which is the removal-safety argument RETIRE-01 (Phase 132, deleting `firestarter dev sdp`) rests on -- that removal decision must be revisited alongside whatever change broke this.
E       assert (0 & 256)
```
Judged legible: names RETIRE-01, RETIRE-07, D-14, and states the required next action.

**Revert:** restored the original condition. `git diff --stat firestarter/cli_handlers.py` confirmed empty (identical to the state committed in Task 1). `python -m pytest "tests/test_write_skip_sdp_unlock.py::test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on" -q` passed. `git status --porcelain` showed only this plan's own modified `test_write_skip_sdp_unlock.py` plus the pre-existing tree dirt (`.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`).

## Task Commits

Each task was committed atomically, in the repo that owns the file:

1. **Task 1: tripwire comments at the decision site (cli_handlers.py)** -- `5ec3a89` (feat, `firestarter_app` submodule)
2. **Task 2: append note at the flag definition (constants.py)** -- `1fdb455` (feat, `firestarter_app` submodule)
3. **Task 3: named tripwire test (test_write_skip_sdp_unlock.py)** -- `cc5d223` (test, `firestarter_app` submodule)

**Plan metadata:** this summary + STATE.md/ROADMAP.md/REQUIREMENTS.md updates (meta-repo, separate commit per `<final_commit>`).

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` -- decision-site tripwire comment (16 lines) above the D-04 auto-set condition; two pointer comments (5 lines each) at the builder default and the Click option default.
- `firestarter_app/firestarter/constants.py` -- 11-line append to `FLAG_SKIP_SDP_UNLOCK`'s comment block, pure addition, existing firmware-sync caveat preserved verbatim.
- `firestarter_app/tests/test_write_skip_sdp_unlock.py` -- new import (`_FakeSerial`), new local helper `_fresh_serial_and_comm()`, new named test with both legs and descriptive failure messages.
- `.planning/REQUIREMENTS.md` -- RETIRE-07 checkbox and Traceability-table row marked Complete; no other RETIRE id touched.

## Decisions Made

- **Re-measured every anchor live rather than trusting the plan's or the pattern map's cited coordinates**, per D-14's own "criterion, not coordinates" discipline -- the decision line landed at `:653`, not the `:622-645`/`:626-640` ranges either artifact cited (both were plausible pre-plan-time estimates, not measured against the file as it now stands after 132-05/06).
- **Added a test-file-local `_fresh_serial_and_comm()` helper rather than editing `conftest.py`**, because `conftest.py` is not in this plan's `files_modified` list and the need (two independent write drives in one test function) is local to this one test.
- **Improved the tripwire test's assertion messages before reverting the plant**, because the raw `assert (0 & 256)` failure did not name the invalidated decision -- exactly the condition the task's own instruction calls out as requiring an improvement before considering the RED demonstration complete.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixture-reuse bug in the initially-drafted two-leg test caused a false failure unrelated to the RED demonstration.**
- **Found during:** Task 3, first run of the newly-written test (before any inversion was planted).
- **Issue:** The test's second leg (`_ALLOWED_CHIP`, no flag) failed with `SystemExit(1)` / "Not connected" when reusing the fixture-injected `fake_serial`/`make_comm` pair for a second `_drive_write` call. Root cause: the first leg's successful write closes its `SerialCommunicator`'s fake serial port (`_FakeSerial.close()` sets `is_open = False`), so the second drive's `make_comm()` factory returned an instance wrapping an already-closed port.
- **Fix:** Added `_fresh_serial_and_comm()`, a local helper that builds an independent `_FakeSerial` + `SerialCommunicator.__new__`-wired factory, mirroring `conftest.py`'s `make_comm` fixture body exactly. Used only for the second leg.
- **Files modified:** `firestarter_app/tests/test_write_skip_sdp_unlock.py`.
- **Commit:** `cc5d223`.

**2. [Rule 1 - Bug] Opaque RED failure message improved before considering the tripwire demonstration complete.**
- **Found during:** Task 3, first RED run against the planted inversion.
- **Issue:** The raw `assert (0 & 256)` failure text named no decision, failing the task's own legibility bar.
- **Fix:** Added descriptive messages to all three assertions in the new test (both legs), naming RETIRE-01/RETIRE-07/D-14 and the specific invalidated decision each assertion protects.
- **Files modified:** `firestarter_app/tests/test_write_skip_sdp_unlock.py`.
- **Commit:** `cc5d223` (same commit as the test itself -- the message improvement and the test are one unit of work per the task's own instructions).

**Total deviations:** 2 auto-fixed under Rule 1. Neither changed the test's intended behaviour or scope; both were discovered and resolved within Task 3 before its commit.
**Impact on plan:** None -- the named test exists exactly as specified, asserts both directions, and has been proven to fail legibly on the exact inversion it guards against.

## Issues Encountered

None beyond the two items documented above under Deviations from Plan, both resolved in-task.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- The tripwire is in place at all three named locations, each pointing at the other two, and reachability is proven by measured line distance rather than by a grep alone.
- `mypy` count holds at **32** (checked 122 source files, watermark 35) -- unchanged from plan 132-06, confirming the typed factory (132-05, D-10) that this plan's new test call sites onto adds zero errors.
- Full suite green: **1296 passed** (1295 + this plan's one new test), 30/30 snapshots passed, coverage 81.72% (floor 70%). `ruff check` + `ruff format --check` both exit 0.
- `git diff --stat firestarter/eprom_operations.py pyproject.toml` is empty across all three commits -- the ring-fence and the watermark both held.
- RETIRE-07 is Complete. RETIRE-01/02/03/05 (already Complete) remain untouched; RETIRE-04/RETIRE-08 (132-08) and RETIRE-06 (132-09) remain untouched, as required.
- Plan 132-08 can proceed against `constants.py` and `cli_handlers.py` as they now stand -- this plan's edits to `constants.py` are confined to the `FLAG_SKIP_SDP_UNLOCK` block (`:112-131`), leaving the stale-anchor block near `:67-72` untouched for 132-08's correction.

---
*Phase: 132-retire-dev-sdp-discharge-the-mypy-debt*
*Completed: 2026-08-03*

## Self-Check: PASSED

Created/modified files verified present on disk:
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-07-SUMMARY.md` -- FOUND
- `firestarter_app/firestarter/cli_handlers.py` -- FOUND (tripwire comments confirmed present)
- `firestarter_app/firestarter/constants.py` -- FOUND (append confirmed present)
- `firestarter_app/tests/test_write_skip_sdp_unlock.py` -- FOUND (named test confirmed present)

Commits verified present in the owning repo's history:
- `5ec3a89` (`firestarter_app` submodule) -- FOUND
- `1fdb455` (`firestarter_app` submodule) -- FOUND
- `cc5d223` (`firestarter_app` submodule) -- FOUND
