---
phase: 143-host-timeout-progress-pulse-override
plan: 07
subsystem: host-protocol
tags: [python, click, cli, pytest, syrupy, pulse-override, host-04, host-05]

# Dependency graph
requires:
  - phase: 143-04
    provides: "write_eprom's pulse_us: int = 0 parameter (HOST-04 transport half) and tests/test_pulse_us_override.py's module skeleton (docstring, _REAL_27C_CHIP, _w27c512_programmer_dict, _fresh_serial_and_comm, four transport tests) that this plan extends in place"
provides:
  - "write's --pulse-us option: click.IntRange(1, 65535), default=None, positioned between --vpe-as-vpp and --skip-sdp-unlock in the decorator stack"
  - "Parse-time refusal of out-of-range/non-integer values at exit 2, before any code path that could open a serial port runs (HOST-05)"
  - "The D-17 mandatory, default-visible click.echo report line naming both the replaced database pulse and the override, authored as a sibling `if` beside the D-04/D-13 blocks"
  - "pulse_us=pulse_us or 0 threaded into the existing write_eprom call, translating Click's None into the transport layer's 0 sentinel (143-04)"
  - "Six new CliRunner tests in tests/test_pulse_us_override.py (module now ten tests total) plus two regenerated write --help golden snapshots in test_characterization.ambr"
affects: [143-10, 145, 146]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "click.IntRange(N, M) with default=None as the specification for any future microsecond-style bounded CLI option -- default=0 is fatal when paired with IntRange because Click's type-caster runs on the DEFAULT too, not just user-supplied values (RESEARCH Pitfall 3, measured)"
    - "caplog.set_level(logging.DEBUG) + a click.echo-vs-logger.info oracle: assert a required substring appears in CliRunner's captured stdout AND that no caplog record at the lowest threshold contains that SAME distinguishing phrase -- proves a report line cannot have travelled through the logging module, without depending on ambient handler wiring. Needle must be specific (a loose word like 'pulse' collides with unrelated pre-existing DEBUG logging that dumps the whole EPROM data dict)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_pulse_us_override.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "default=None, never 0 -- the plan's one measured trap, implemented exactly as specified and pinned by test_write_without_pulse_us_still_works"
  - "--pulse-us positioned between --vpe-as-vpp and --skip-sdp-unlock, i.e. BEFORE the existing 'D-14 / RETIRE-07 tripwire, edit point 2 of 2' comment -- that comment textually refers only to the --skip-sdp-unlock option immediately below it, so the new option had to land before the comment, not between the comment and skip-sdp-unlock's own @click.option."
  - "The D-17 report line sits immediately after `eprom_data = resolve_chip(...)`, BEFORE the D-04 auto-set block -- a separate sibling `if`, not chained onto D-04/D-13, so all three can co-fire on the same chip."
  - "JSON_KEY_PULSE_DELAY was NOT added -- this was already decided by the plan itself (a documented mechanical gray area), not re-decided here; the 'pulse-delay' string literal stays at its existing two sites."
  - "Two write --help golden snapshots in test_characterization.ambr were regenerated (syrupy --snapshot-update) -- a direct, necessary consequence of adding a new option + docstring paragraph to a real subprocess-invoked --help; diff verified to contain exactly the new option line and new docstring paragraph, nothing else. Treated as a Rule 3 auto-fix (blocking issue caused directly by this task's own change), not scope creep."
  - "Case 4 (test_refusal_opens_no_port) and Case 5 (test_write_without_pulse_us_still_works) pass BOTH before and after Task 2's implementation, by design -- honestly recorded as permanently-true safety-net assertions rather than forced into an artificial RED. This is the SAME pattern this phase's own prior plans already established (143-04's Test 6; 143-06's split negative control), not a new exception invented here."

patterns-established:
  - "Pattern: when a plan's acceptance criteria hard-codes an exact total test count (here, 'ten'), author multi-value cases as ONE test function with an internal loop and per-value assertion messages, not @pytest.mark.parametrize -- parametrize silently multiplies the collected-test count and breaks a fixed-total acceptance check."

requirements-completed: []

coverage:
  - id: D1
    description: "HOST-04, CLI half: firestarter write --pulse-us N reaches the wire's existing 'pulse-delay' key verbatim through the real CLI, and a bare write with no --pulse-us still works and still carries the database value (Pitfall-3 regression guard)"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_pulse_us_override.py::test_override_reaches_the_wire_through_the_cli"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_pulse_us_override.py::test_write_without_pulse_us_still_works"
        status: pass
    human_judgment: false
  - id: D2
    description: "HOST-05: an out-of-range or non-integer --pulse-us is refused at Click parse time with exit 2 (not the app's usual exit 1), naming the offending value and the accepted range, and never calls find_and_connect -- no serial byte is ever sent"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_pulse_us_override.py::test_out_of_range_is_refused_at_parse_time"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_pulse_us_override.py::test_refusal_opens_no_port"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-17: every --pulse-us invocation prints a mandatory, default-visible (no -v needed) click.echo report line naming the chip, the database pulse replaced, and the override -- and the line does not travel through the logging module"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_pulse_us_override.py::test_override_always_reports"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-18: --pulse-us exists on write ONLY -- read/verify/blank/erase refuse it as an unrecognised option (exit 2), and a source-level check of the Click Command objects' own parameter names confirms only write registers pulse_us"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_pulse_us_override.py::test_flag_is_write_only"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-08-13
status: complete
---

# Phase 143 Plan 07: --pulse-us CLI Option, Bounds and Provenance Line (HOST-04 CLI Half + HOST-05) Summary

**`firestarter write --pulse-us N` (`click.IntRange(1, 65535)`, `default=None`) overrides the database program pulse through the existing `pulse-delay` wire field, refuses out-of-range/non-integer values at Click parse time with exit 2 and no port ever opened, always prints a default-visible provenance line naming both values, and is exposed on `write` alone -- with a bare `write` (no flag) still working, per the plan's one measured trap.**

## Performance

- **Duration:** ~30 min
- **Started:** ~2026-08-13T02:52Z (STATE.md hand-off from 143-06)
- **Completed:** 2026-08-13T03:21Z
- **Tasks:** 2 completed (both `type="auto"`, no checkpoints)
- **Files touched:** 3 (0 created, 3 modified)

## Accomplishments

- `firestarter/cli_handlers.py`: added `--pulse-us` (`type=click.IntRange(1, 65535)`, `default=None`) to `write`'s decorator stack between `--vpe-as-vpp` and `--skip-sdp-unlock`, with an inline comment recording the measured `default=0` trap and its anti-precedent (`--read-settling`/`--read-strobe`). Added `pulse_us: Optional[int]` to `write`'s signature and a `TRAP #7 / D-14..D-18` docstring paragraph recording all five decisions, including the corrected D-15 mechanism. Added the D-17 report line as a separate sibling `if` immediately after `eprom_data = resolve_chip(...)`, using `click.echo` and the file's `f"{eprom.upper()}: ..."` prefix convention, naming both the replaced database pulse and the override. Threaded `pulse_us=pulse_us or 0` into the existing `write_eprom` call.
- `tests/test_pulse_us_override.py`: extended plan 143-04's four-test transport-half module with six new `CliRunner`-based cases (module now ten tests total): end-to-end wire reach through the real CLI, the mandatory report line (with a `caplog`-based proof it is not routed through the logging module), parse-time refusal at exit 2 for `0`/`65536`/`abc`, the no-port-opened negative for the same three values, the no-flag Pitfall-3 regression guard, and the write-only scope (both a runtime exit-2 check on `read`/`verify`/`blank`/`erase` and a source-level check of the Click `Command` objects' own parameter names).
- `tests/__snapshots__/test_characterization.ambr`: regenerated the two `write --help` golden snapshots (`test_help_write`, `test_no_blank_check_polarity`) -- a direct, necessary consequence of the new option and docstring paragraph; diff confirmed to contain exactly those two additions.
- Full host suite: **1574 passed** (see "Baseline Reconciliation" below for why this, not the plan's literal 1568/1573, is the correct figure), coverage **82.89%** (>= 70% floor). `ruff check`/`ruff format --check` clean. mypy watermark exit 0 (33 errors, 2 below the 35 watermark -- pre-existing, unmoved from 143-04/143-06's baseline). `git diff` confirms zero hunks in `serial_comm.py`, `database.py`, `eprom_operations.py`, `constants.py`, `messages.py`; all four hunks in `cli_handlers.py` sit inside `write`'s own decorator stack, signature, docstring and body.
- `firestarter` (firmware) repo porcelain was clean before the coverage leg -- no L-6 deselection was needed (`git -C /workspaces/firestarter status --porcelain` returned nothing, checked twice), recorded per the plan's instruction even though the empty case "needs no note."

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter_app` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Extend `tests/test_pulse_us_override.py` with six CliRunner cases for HOST-04's CLI half and all of HOST-05, all RED** - `2413431` (test)
2. **Task 2: Add the `--pulse-us` option, the D-17 report line and the threading, and turn the module GREEN** - `36c574f` (feat)

**Plan metadata:** committed in the meta repo (`/workspaces`), see below.

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` - `--pulse-us` option; `write`'s `pulse_us: Optional[int]` parameter and `TRAP #7` docstring paragraph; the D-17 sibling-`if` report line; `pulse_us=pulse_us or 0` threaded into `write_eprom`. Four hunks total, all inside `write`'s own decorator stack / signature / docstring / body -- `git diff` confirms zero hunks anywhere else in the file (including `read`, `verify`, `blank`, `erase`, `dev_consistency_check`).
- `firestarter_app/tests/test_pulse_us_override.py` (extended, +6 tests, now 10) - the CLI half: `make_app_context` (local copy), `runner` fixture, `_drive_write_via_cli` driver, and the six new cases.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` (regenerated, 2 snapshots) - `write --help`'s golden output, now including `--pulse-us` and the `TRAP #7` docstring paragraph.

## Decisions Made

- **`default=None`, never `0`** -- the plan's one measured trap, implemented exactly as specified.
- **Option placement precedes the existing tripwire comment.** `cli_handlers.py` already carried a comment reading "D-14 / RETIRE-07 tripwire, edit point 2 of 2: this option's `default=False`..." directly above `--skip-sdp-unlock`'s own `@click.option`. That comment's "this option" refers to `--skip-sdp-unlock` specifically. `--pulse-us` therefore had to be inserted **before** that comment (i.e., directly after `--vpe-as-vpp`), not between the comment and `--skip-sdp-unlock` -- otherwise the tripwire comment would misleadingly appear to describe `--pulse-us`.
- **The D-17 report line sits before the D-04 auto-set block**, immediately after `eprom_data = resolve_chip(...)`, as its own top-level sibling `if` -- not an `elif` on D-04, and not nested inside it. This lets a capability-refused protocol-0x0D chip driven with `--pulse-us` print all three possible lines (D-17, D-04, D-13) independently.
- **`JSON_KEY_PULSE_DELAY` was not added.** This was already decided by the plan itself before this plan ran (a recorded mechanical gray area: both upstream documents call it cosmetic, and `143-PATTERNS.md` would require it at both `database.py` and the CLI site or not at all, for zero behavioural gain). This plan followed that decision; it was not re-litigated here. The `"pulse-delay"` string literal stays at its existing two sites (`database.py` and `eprom_operations.py`, both from plan 143-04).
- **Two `write --help` golden snapshots were regenerated.** See "Deviations from Plan" below.
- **Cases 4 and 5 are honest, permanently-passing controls, not weakened tests.** See "Genuine-RED Reasoning" below.

## Record Corrections and Provenance Notes (plan-mandated)

The plan's acceptance criteria required five specific facts to be stated in this SUMMARY. Stating them explicitly, together, here:

1. **HOST-04 spans two plans; neither marks it Complete.** Plan 143-04 landed the transport half (`write_eprom`'s `pulse_us` parameter riding the `pulse-delay` DB-dict key). This plan (143-07) landed the CLI half (the `--pulse-us` option, its bounds, and the threading). `requirements: []` in this plan's frontmatter is deliberate and was not repopulated.
2. **HOST-05 is satisfied entirely by this plan** (parse-time `IntRange` refusal, exit 2, no port opened) **but is flipped centrally by plan 143-10**, after every piece of phase evidence exists -- not by this plan.
3. **The corrected D-15 mechanism:** D-15's original justification ("refuses before `AppContext` builds") is false -- Click's `cli()` group callback runs FIRST, before `write()`'s own parameters are even type-converted, so `AppContext` already exists by the time a parse-time refusal fires. The guarantee that actually holds, and that HOST-05 actually needs, is that **nothing in `cli()` or `AppContext` construction opens a serial port** -- port-opening is confined to `SerialCommunicator.find_and_connect`, called only from inside `write_eprom`'s own body, which a parse-time refusal never reaches. This corrected mechanism is stated in `write`'s own docstring (the `TRAP #7` paragraph) and in `test_refusal_opens_no_port`'s docstring, and is proven (not just asserted) by that same test's `captured == {}` check.
4. **The bound's provenance is minipro parity, not a wire-type limit, and H3 is Phase 146's.** The option's `help=` text and `write`'s docstring both state that `1..65535` is minipro parity (`-o pulse=N` is a `uint16`), NOT the wire type -- `pulse-delay` is parsed by the firmware's `extract_long` into an **unclamped** `uint32_t`, so an over-ceiling value is reachable on the wire today, independently of this flag. That full reconciliation is named as Phase 146 / CLOSE-04's, not this plan's, in both the `--help` text and the docstring.
5. **The decision to skip `JSON_KEY_PULSE_DELAY`** is recorded above under "Decisions Made."

## Baseline Reconciliation (full-suite count)

The plan's own text predicted **1568 passed** (1562 after 143-04, plus this plan's six) **or 1573** "if plan 143-06's five have already landed in this wave." Neither number matches the measured **1574**, and the plan explicitly anticipates this: "record the observed number and account for the difference rather than treating a higher count as a failure."

The reconciliation: 143-06 had already landed (confirmed via `git log` before this plan started: commits `86c97ec`/`6742367`), and 143-06's own SUMMARY documents that it added **six** tests, not five -- its Test 5 was authored as an explicitly-permitted split into two functions, which the plan's own acceptance criteria for 143-06 anticipated ("six if test 5's negative is split"). So the correct pre-this-plan baseline is **1562 + 6 (143-06, actual) = 1568**, not 1562 or "1562 + 5". Adding this plan's six new tests: **1568 + 6 = 1574** -- exactly the measured figure. No discrepancy; the plan's "1573" prediction was built on 143-06's own pre-execution estimate of five, which 143-06's actual execution (documented in its SUMMARY, landed before this plan ran) superseded.

## D-25 Evidence: RED before, GREEN after, verbatim

**RED** (`pytest tests/test_pulse_us_override.py -o addopts="" -v`, run against the code as committed at the end of Task 1, before any Task 2 edit):

```
collecting ... collected 10 items

tests/test_pulse_us_override.py::test_override_rides_the_db_dict PASSED  [ 10%]
tests/test_pulse_us_override.py::test_override_does_not_mutate_the_caller_dict PASSED [ 20%]
tests/test_pulse_us_override.py::test_no_new_wire_field_is_added PASSED  [ 30%]
tests/test_pulse_us_override.py::test_absent_flag_leaves_db_pulse PASSED [ 40%]
tests/test_pulse_us_override.py::test_override_reaches_the_wire_through_the_cli FAILED [ 50%]
tests/test_pulse_us_override.py::test_override_always_reports FAILED     [ 60%]
tests/test_pulse_us_override.py::test_out_of_range_is_refused_at_parse_time FAILED [ 70%]
tests/test_pulse_us_override.py::test_refusal_opens_no_port PASSED       [ 80%]
tests/test_pulse_us_override.py::test_write_without_pulse_us_still_works PASSED [ 90%]
tests/test_pulse_us_override.py::test_flag_is_write_only FAILED          [100%]

4 failed, 6 passed in 3.51s
```

Representative failures, each on Click's "no such option" path (the pre-implementation shape the plan predicted), not a collection error:

```
test_override_reaches_the_wire_through_the_cli:
  AssertionError: expected a successful write; got exit 2, output:
  Error: No such option '--pulse-us'.
  assert 2 == 0

test_out_of_range_is_refused_at_parse_time:
  AssertionError: HOST-05: refusing --pulse-us '0' must mention '0' (an
  actionable message naming the offending value and the accepted range);
  output: ... Error: No such option '--pulse-us'.
  assert '0' in "...Error: No such option '--pulse-us'.\n"

test_flag_is_write_only:
  AssertionError: D-18: write's own Click Command object must register a
  'pulse_us' parameter; got {'vpe_as_vpp', 'blank_check', 'eprom',
  'skip_sdp_unlock', 'address', 'skip_erase', 'force', 'input_file'}
```

`test_refusal_opens_no_port` and `test_write_without_pulse_us_still_works` PASSED at RED time, by design -- see "Genuine-RED Reasoning" below.

**GREEN** (`pytest tests/test_pulse_us_override.py -x -o addopts="" -v`, after Task 2's production edit and the caplog-substring fix below):

```
collecting ... collected 10 items

tests/test_pulse_us_override.py::test_override_rides_the_db_dict PASSED  [ 10%]
tests/test_pulse_us_override.py::test_override_does_not_mutate_the_caller_dict PASSED [ 20%]
tests/test_pulse_us_override.py::test_no_new_wire_field_is_added PASSED  [ 30%]
tests/test_pulse_us_override.py::test_absent_flag_leaves_db_pulse PASSED [ 40%]
tests/test_pulse_us_override.py::test_override_reaches_the_wire_through_the_cli PASSED [ 50%]
tests/test_pulse_us_override.py::test_override_always_reports PASSED     [ 60%]
tests/test_pulse_us_override.py::test_out_of_range_is_refused_at_parse_time PASSED [ 70%]
tests/test_pulse_us_override.py::test_refusal_opens_no_port PASSED       [ 80%]
tests/test_pulse_us_override.py::test_write_without_pulse_us_still_works PASSED [ 90%]
tests/test_pulse_us_override.py::test_flag_is_write_only PASSED          [100%]

10 passed in 4.37s
```

## Genuine-RED Reasoning (why two of the six new cases pass both before and after)

`test_refusal_opens_no_port` and `test_write_without_pulse_us_still_works` are **not** weakened tests -- they are structurally incapable of failing pre-Task-2, for reasons specific to what each one actually proves, and this phase already has a standing precedent (143-04's Test 6; 143-06's split negative) of recording exactly this honestly rather than forcing an artificial failure:

- **`test_refusal_opens_no_port`**'s oracle (`captured == {}`) is insensitive to *why* a refusal happens. Pre-Task-2, `--pulse-us` is simply an unrecognised option, so Click refuses before `find_and_connect` is ever reached; post-Task-2, an out-of-range value is refused by `IntRange` before the same point. Both refusals leave `captured` empty for the same reason (Click's own parameter-processing order), so the property this test proves -- "a CLI-layer refusal opens no port" -- is true independent of which specific refusal fired. There is no way to make this test fail pre-Task-2 without asserting a different, narrower property (which Case 3 already does).
- **`test_write_without_pulse_us_still_works`** guards against a regression that, by construction, does not exist yet: a bare `write` with no `--pulse-us` flag behaves identically whether or not the option has been added, UNLESS the option is added with the fatal `default=0` shape. Since the option didn't exist pre-Task-2, this invocation was already a perfectly ordinary, already-passing `write` -- exactly like every `write` invocation that predates this plan. Its purpose is to catch a **future** possible regression (the exact one RESEARCH Pitfall 3 measured), not a **current** bug, so it is correct for it to pass at every point in this plan's history.

Both are documented in their own docstrings as such, and both remain part of the ten-test permanent regression suite going forward.

## Verification Results (final state)

| Check | Result |
|---|---|
| `pytest tests/test_pulse_us_override.py -x -o addopts=""` | 10 passed |
| `pytest tests/test_write_skip_sdp_unlock.py -x -o addopts=""` | 8 passed |
| `pytest tests/test_write_skip_sdp_unlock.py tests/test_cli_handlers.py -x -o addopts=""` | 74 passed |
| `pytest tests/ --cov=firestarter --cov-fail-under=70 -o addopts=""` | **1574 passed**, coverage **82.89%** (30 snapshots passed) |
| `ruff check firestarter/ tests/` | All checks passed |
| `ruff format --check firestarter/ tests/` | 133 files already formatted |
| `tools/check_mypy_watermark.py` | exit 0; 33 errors, 2 below the 35 watermark (unmoved from 143-04/143-06) |
| `git diff --exit-code -- firestarter/constants.py firestarter/database.py firestarter/eprom_operations.py firestarter/serial_comm.py firestarter/messages.py` (vs pre-plan HEAD) | clean |
| `git diff` hunks in `firestarter/cli_handlers.py` | 4 hunks, all inside `write`'s decorator stack / signature / docstring / body |
| Grep `--pulse-us` `@click.option` declarations in `cli_handlers.py` | exactly 1, on `write` |
| Grep `energy_cap_us` / `JSON_KEY_PULSE_DELAY` in `cli_handlers.py` | `energy_cap_us` appears only in the D-16 docstring prose (no mirrored check); `JSON_KEY_PULSE_DELAY` not present |
| `git -C /workspaces/firestarter status --porcelain` (L-6 check, before the coverage leg) | clean -- no deselection needed |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_override_always_reports`'s click.echo-vs-logger.info oracle used too loose a substring**
- **Found during:** Task 2 (confirming GREEN for `test_pulse_us_override.py`)
- **Issue:** The `caplog` assertion checked for the substring `"pulse"` in any captured log record. The write pipeline's own pre-existing `_setup_operation` DEBUG logging dumps the entire composed EPROM data dict (which legitimately contains the `"pulse-delay"` key) -- an unrelated, correct piece of production logging that coincidentally contains the word "pulse", producing a false-positive failure unrelated to the D-17 line.
- **Fix:** Narrowed the needle to `"overrides the database"`, the D-17 line's own distinguishing phrase, which cannot appear in unrelated logging.
- **Files modified:** `firestarter_app/tests/test_pulse_us_override.py`
- **Verification:** all 10 tests pass; the fix is a pure test-authoring correction, no production behaviour changed.
- **Committed in:** `36c574f` (bundled with Task 2's production commit, since it corrects test-authoring code discovered while turning that same task's target module GREEN -- same pattern 143-04's SUMMARY documents for its own analogous fix).

**2. [Rule 3 - Blocking] Two stale `write --help` golden snapshots regenerated**
- **Found during:** Task 2 (the full-suite-with-coverage verification leg)
- **Issue:** `tests/test_characterization.py::test_help_write` and `::test_no_blank_check_polarity` run the REAL, installed `firestarter` entry point as a subprocess and pin its exact `write --help` stdout via a `syrupy` snapshot. Adding `--pulse-us` (with its help text) and the `TRAP #7` docstring paragraph is an intended, direct consequence of this plan's own change, and it legitimately altered that output -- blocking the full-suite-green verification the plan's own `<verification>` block requires.
- **Fix:** Ran `pytest tests/test_characterization.py::test_help_write tests/test_characterization.py::test_no_blank_check_polarity -o addopts="" --snapshot-update`, then inspected the resulting `git diff` on `tests/__snapshots__/test_characterization.ambr` line by line to confirm it contained exactly two additions (the new `--pulse-us` option line at its correct position between `--vpe-as-vpp` and `--skip-sdp-unlock`, and the new `TRAP #7` docstring paragraph) and nothing else, in both of the file's two identical snapshot blocks.
- **Files modified:** `firestarter_app/tests/__snapshots__/test_characterization.ambr`
- **Verification:** both tests pass; full suite subsequently reports 1574 passed, 30 snapshots passed (was 28 passed / 2 failed before the regeneration).
- **Committed in:** `36c574f` (bundled with Task 2's production commit -- the snapshot update is a mechanical, zero-judgment consequence of that same commit's `cli_handlers.py` change).

---

**Total deviations:** 2 auto-fixed (1 Rule-1 test bug, 1 Rule-3 blocking snapshot regeneration).
**Impact on plan:** No production-code defect was found beyond the plan's own intended change. Both fixes are corrections to test-authoring artifacts (a test's own assertion; a golden snapshot of the plan's own intended CLI surface change), not scope creep -- neither touches `eprom_operations.py`, `serial_comm.py`, `database.py`, `constants.py` or `messages.py`.

## Issues Encountered

- **Self-corrected test-authoring approach for Task 1 (not a deviation from the plan's content, but from an interim drafting choice):** the first draft of Cases 3 and 4 used `@pytest.mark.parametrize("bad_value", ["0", "65536", "abc"])`, which collected 14 tests total (4 existing + 10, since each parametrized case expands to 3 items) instead of the plan's explicitly mandated **ten**. Caught immediately by running `pytest --collect-only` before ever committing: rewrote both cases as single test functions with an internal `for bad_value in (...)` loop and per-value assertion messages, restoring the collection count to exactly ten. No functional coverage was lost -- each of the three sub-values is still asserted individually, with its own failure message.
- No other issues. The `caplog`-based click.echo/logger.info oracle idiom (Case 2) was sanity-checked by first running it against a deliberately-broken substring (see Deviation 1 above), which is precisely how the false positive was caught before it could mask a real regression.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HOST-04's CLI half and all of HOST-05 are complete and verified independently of any hardware (all software-only, CliRunner-driven, per this plan's own scope). HOST-04's transport half (143-04) and CLI half (this plan) are both done, but **neither plan marks HOST-04 Complete** -- `requirements: []` stays empty here, as instructed.
- Plan **143-10** is the one that flips the `HOST-04`/`HOST-05` checkboxes in `REQUIREMENTS.md`, after every piece of phase evidence (including firmware-side plans 143-05/143-08/143-09 and any bench evidence) exists.
- Phase **145**'s bench evidence and Phase **146** / CLOSE-04's H3 reconciliation (the firmware's unclamped `extract_long` on `pulse-delay`) are both named, not attempted, by this plan -- consistent with the plan's own scope boundary.
- `_drive_write_via_cli` and this module's local `make_app_context` (both new, this plan) are reusable analogs for any later plan needing a hardware-free, real-`AppContext` CLI-level write drive with wire-command-dict capture.
- No blockers. `serial_comm.py`, `database.py`, `eprom_operations.py`, `constants.py` and `messages.py` are all confirmed untouched by `git diff`; `read`, `verify`, `blank`, `erase` and `dev_consistency_check` are all confirmed untouched inside `cli_handlers.py`.

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/cli_handlers.py` (modified)
- FOUND: `firestarter_app/tests/test_pulse_us_override.py` (modified, now 10 tests)
- FOUND: `firestarter_app/tests/__snapshots__/test_characterization.ambr` (modified, 2 snapshots regenerated)
- FOUND commit `2413431` (Task 1)
- FOUND commit `36c574f` (Task 2)

---
*Phase: 143-host-timeout-progress-pulse-override*
*Completed: 2026-08-13*
