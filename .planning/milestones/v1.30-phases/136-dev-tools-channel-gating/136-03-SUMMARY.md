---
phase: 136-dev-tools-channel-gating
plan: 03
subsystem: cli
tags: [click, channel-gating, subprocess-testing, non-vacuity, source-scan, mypy, ci-parity]

# Dependency graph
requires:
  - phase: 136-dev-tools-channel-gating
    plan: 01
    provides: "channel.py's BETA_ONLY_DEV_COMMANDS, dev_tools_enabled_by_env, is_dev_tools_enabled, dev_command_gate_message"
  - phase: 136-dev-tools-channel-gating
    plan: 02
    provides: "cli_handlers.py's _DevGroup(click.Group), _DEV_TOOLS_ENABLED module constant, six conditionally-registered @dev.command blocks, the rewritten dev() docstring"
provides:
  - "tests/test_dev_group_channel_gating.py -- subprocess dual-channel harness proving CHAN-01, CHAN-02, CHAN-03, CHAN-04, CHAN-06 from outside the process, in two separate child processes (simulated-stable, simulated-prerelease)"
  - "tests/test_dev_gate_reads_no_firmware_source.py -- comprehensive CHAN-07 proof: no `open(` call and no firmware-path token anywhere in the gate's five new callables, plus a whole-module check on channel.py"
  - "Two observed, byte-identically-restored non-vacuity mutations proving both D-01 mechanisms are load-bearing, not coincidentally-passing"
affects: [136-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Subprocess dual-channel harness, structurally adapted from tests/test_py32_channel_gating.py's _CHILD_PROGRAM/_run_cli shape: assign firestarter.__version__ before firestarter.cli_handlers is ever imported in the child, guarded by the child's own sys.modules pre-assertion, so the simulated channel is a structural fact rather than an in-process assumption (D-04)"
    - "env_overrides merged into a FIRESTARTER_DEV_TOOLS-stripped copy of os.environ for every child call (override or not), so a 'no override' test cannot silently inherit an ambient value from the developer's own shell"
    - "inspect.getsource() scoped to exactly the gate's own new callables (not a whole-file text scan of cli_handlers.py), so the CHAN-07 proof stays immune to unrelated open() calls already present elsewhere in that large, pre-existing file"

key-files:
  created:
    - firestarter_app/tests/test_dev_group_channel_gating.py
    - firestarter_app/tests/test_dev_gate_reads_no_firmware_source.py
  modified: []

key-decisions:
  - "Task 1 and Task 2 were each committed as a single `test(...)` commit rather than split RED/GREEN -- both tasks author proof tests against mechanisms 136-01/136-02 already shipped; there is no corresponding production code left to write in this plan, so the tests pass immediately on first run by design (this plan's own purpose, stated in its objective, is proof, not new production code). See Deviations for the full reasoning."
  - "Task 3 makes no permanent source change, exactly as its own action text specifies -- both mutations were observed RED then restored byte-identically before any commit; the record lives entirely in this SUMMARY, not in a submodule commit"
  - "A final, non-overlapping confirmatory tools/ci_replica_venv.sh run was performed after both Task 3 mutations were fully reverted, to rule out any risk that an earlier background ci-replica run's ~215s pytest leg had overlapped in wall-clock time with either mutation window"

coverage:
  - id: CHAN-01
    description: "On a stable install, dev --help lists only read and test -- proven via subprocess (simulated __version__ = 3.0.0, no env override), not by in-process assumption"
    verification:
      - kind: unit
        ref: "tests/test_dev_group_channel_gating.py::test_simulated_stable_help_lists_only_read_and_test"
        status: pass
    human_judgment: false
  - id: CHAN-02
    description: "Beta-only dev subcommands are gated by genuine non-registration, proven by direct registry introspection (cli_handlers.dev.commands.keys() reported by the child) equalling exactly {read, test} on simulated-stable, not merely 'excludes the six'"
    verification:
      - kind: unit
        ref: "tests/test_dev_group_channel_gating.py::test_simulated_stable_dev_commands_is_exactly_read_and_test"
        status: pass
    human_judgment: false
  - id: CHAN-03
    description: "Invoking a gated dev subcommand on simulated-stable refuses at non-zero exit with the channel-specific message identifying the cause; a genuine typo gets Click's own generic 'No such command' message instead, with no channel-refusal text present -- the typo control that rules out 'swallows all errors'"
    verification:
      - kind: unit
        ref: "tests/test_dev_group_channel_gating.py::test_simulated_stable_gated_command_refuses_with_channel_message, ::test_simulated_stable_genuine_typo_gets_clicks_generic_message"
        status: pass
    human_judgment: false
  - id: CHAN-04
    description: "dev --help output is pinned on both channels via subprocess, in the same test module, asserting both directions (stable output != prerelease output; each channel's own gated/ungated names checked independently)"
    verification:
      - kind: unit
        ref: "tests/test_dev_group_channel_gating.py::test_dev_help_differs_between_channels_and_is_pinned_each_way"
        status: pass
    human_judgment: false
  - id: CHAN-06
    description: "dev reg's bench-tooling role survives via FIRESTARTER_DEV_TOOLS=1 set in a simulated-stable child's environment before import -- all six gated names ARE registered and dev reg --help genuinely runs (exit 0), not merely appears in the registry"
    verification:
      - kind: unit
        ref: "tests/test_dev_group_channel_gating.py::test_simulated_stable_with_env_override_registers_all_six_gated_names, ::test_simulated_stable_env_override_lets_gated_command_actually_run"
        status: pass
    human_judgment: false
  - id: CHAN-07
    description: "The gate reads no firmware source -- comprehensively proven across channel.py's four symbols plus cli_handlers._DevGroup.get_command (no open( call, no firmware-path token), plus a whole-module check on channel.py; non-vacuity discharged by planting open(\"/dev/null\") and observing the scan name is_dev_tools_enabled as the offender"
    verification:
      - kind: unit
        ref: "tests/test_dev_gate_reads_no_firmware_source.py (11 tests, parametrized over 5 callables x 2 properties + 1 whole-module check)"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-05
status: complete
---

# Phase 136 Plan 03: Subprocess Dual-Channel Proof + CHAN-07 Source Scan + Non-Vacuity Summary

**Proved, from outside the process in real subprocesses, everything plans 136-01/136-02 built: a dual-channel Click harness pinning `dev --help` and `dev.commands` on both simulated channels (CHAN-01/02/03/04/06), a comprehensive no-firmware-read source scan across the gate's five new callables (CHAN-07), and two named source mutations each observed to break a specific assertion before being restored byte-identically.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-05T12:05:00Z (approx., immediately following 136-02's completion)
- **Completed:** 2026-08-05T12:40:00Z
- **Tasks:** 3 (`type="auto"`; Tasks 1-2 `tdd="true"` but pass on first run by design -- see Deviations)
- **Files modified:** 2 new test files (submodule); 0 permanent production changes (Task 3's two mutations were both observed then reverted before any commit)

## Accomplishments

- `tests/test_dev_group_channel_gating.py` -- a direct structural adaptation of `test_py32_channel_gating.py`'s `_CHILD_PROGRAM`/`_run_cli` subprocess shape for the `dev` group. The child program imports `firestarter` bare, asserts `"firestarter.cli_handlers" not in sys.modules`, assigns the simulated `__version__`, THEN imports `cli_handlers` for the first time in that process and reports `_DEV_TOOLS_ENABLED` and `sorted(dev.commands.keys())` back as JSON -- making the import-time-frozen registration decision a structural fact per process, never an in-process patch applied after `cli_handlers` was already live.
- 12 tests, all green: simulated-stable proves `dev --help` lists only `read`/`test`, `dev.commands.keys()` is exactly `{"read", "test"}` (the stronger exact-set assertion, not just "excludes the six"), a gated name (`dev reg`) refuses with `channel.dev_command_gate_message`'s text at non-zero exit, and a genuine typo (`dev totally-bogus-name`) gets Click's own generic "No such command" message with no channel-refusal text present. Simulated-prerelease is the positive control: all eight names listed and registered. `FIRESTARTER_DEV_TOOLS=1` set in a simulated-stable child's environment (via an extended `env_overrides` parameter, merged onto a `FIRESTARTER_DEV_TOOLS`-stripped copy of `os.environ` so no test can accidentally inherit an ambient shell value) re-registers all six gated names AND lets `dev reg --help` genuinely run (exit 0) -- not merely appear registered.
- `tests/test_dev_gate_reads_no_firmware_source.py` -- `inspect.getsource()` scoped to exactly the five callables the gate introduced (`channel.is_prerelease_build`, `channel.dev_tools_enabled_by_env`, `channel.is_dev_tools_enabled`, `channel.dev_command_gate_message`, `cli_handlers._DevGroup.get_command`), parametrized so a failure names which one violated the property. Asserts no `"open("` substring and none of a forbidden-token tuple (`firestarter/include`, `.h"`, `.ino`, `serial_comm`, `frame_parser`) in any of the five. A sixth check asserts no `"open("` anywhere in `inspect.getsource(channel)` (whole-file, not just the four callables) -- the stronger, file-wide claim CHAN-07's own touch note asks for. 11 tests total, all green.
- **Non-vacuity obligation #4 (CHAN-07) discharged**: temporarily planted `open("/dev/null")` inside `channel.is_dev_tools_enabled`'s body, re-ran the module, observed 2 failures naming `is_dev_tools_enabled` (and the whole-module check) as the offending callable(s), then restored `channel.py` byte-identically (`git diff --stat firestarter/channel.py` empty) before green again. Verbatim RED output below.
- **Non-vacuity obligations #2 and #3 (Task 3) discharged** against `cli_handlers.py`: Mutation A (`cls=_DevGroup` removed from `@cli.group(name="dev", cls=_DevGroup)`) broke exactly the informative-refusal assertion (`test_simulated_stable_gated_command_refuses_with_channel_message`), reverting to Click's generic `No such command 'reg'.`; Mutation B (`_DEV_TOOLS_ENABLED: bool = True` hardcoded) broke the exact-`{read, test}` registry assertion (plus five others that depend on the stable channel actually excluding the six). Both mutations were restored byte-identically (`git diff --stat firestarter/cli_handlers.py` empty) with no commit -- Task 3 adds no permanent source change, per its own action text.
- Verified throughout: `ruff check`/`ruff format --check` clean, `tools/ci_replica_venv.sh` mypy watermark gate **33 errors (watermark 35), checked 130 source files** -- unchanged error count from 136-02's baseline (checked count rose from 128 to 130, exactly the two new test files added), and the full suite: **1492 passed, 2 failed** -- exactly the two pre-existing, already-deferred-to-136-04 snapshot regressions (`test_help`, `test_help_dev`), confirmed by name, no third failure.

## Task Commits

Each task was committed atomically, in the submodule (`firestarter_app`, on `gsd/v1.30-sdp-surface-retirement`):

1. **Task 1: Subprocess dual-channel harness -- CHAN-01, CHAN-02, CHAN-03, CHAN-04, CHAN-06** - `16ff598` (test) - `tests/test_dev_group_channel_gating.py`
2. **Task 2: CHAN-07 -- comprehensive no-firmware-read assertion** - `11c5de4` (test) - `tests/test_dev_gate_reads_no_firmware_source.py`
3. **Task 3: Non-vacuity -- the gate is load-bearing** - no submodule commit (by design; see Decisions Made). Both mutations observed RED then restored byte-identically; the record is this SUMMARY.

**Plan metadata:** committed separately below (meta repo, this SUMMARY + REQUIREMENTS.md + STATE.md + ROADMAP.md).

_Note: per this plan's own `<repo_topology>`, all production/test code lives inside the `firestarter_app` submodule; this SUMMARY and requirement-ticking land in the meta repo (`/workspaces`, `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`). The two branch names deliberately diverge._

## Files Created/Modified

- `firestarter_app/tests/test_dev_group_channel_gating.py` (submodule, new) -- subprocess dual-channel harness (12 tests)
- `firestarter_app/tests/test_dev_gate_reads_no_firmware_source.py` (submodule, new) -- comprehensive no-firmware-read source scan (11 tests)
- `.planning/REQUIREMENTS.md` (meta repo) -- **CHAN-01, CHAN-02, CHAN-03, CHAN-04, CHAN-06, CHAN-07** ticked Complete (six checkboxes + six traceability-table rows). CHAN-05 (already `[x]` from 136-02) untouched. No other requirement row touched -- confirmed by a scoped `git diff` before committing, which showed exactly the twelve CHAN-0X hunks (six checkbox lines, six table rows) and nothing else, after manually reverting two unrelated blank-line insertions the `requirements mark-complete` tool made elsewhere in the file (see Deviations).

## Decisions Made

- **Tasks 1 and 2 committed as single `test(...)` commits, not split RED/GREEN**, despite carrying `tdd="true"`. Both tasks author proof tests against mechanisms `136-01`/`136-02` already fully implemented; there is no `<implementation>` step left for this plan to perform, and the plan's own objective states its purpose is proof, not new production code ("Prove, from the outside, everything plans 136-01/136-02 built"). The tests therefore pass on first run by design -- this is the correct, expected outcome for an evidencing plan, not a TDD violation. See Deviations for the full reasoning this diverges from the strict RED-must-fail-first shape.
- **Task 3 makes no permanent source change** -- both mutations were reverted before any commit, exactly as its own action text specifies ("this task adds no permanent source change, only the SUMMARY record of the two observed failures").
- **A clean, non-overlapping final `tools/ci_replica_venv.sh` run** was performed after both Task 3 mutations were fully restored, specifically to rule out the risk that an earlier background run's ~215s pytest leg had executed concurrently with either mutation's brief window on disk. The final run's numbers (33/35 mypy, 1492 passed / 2 failed) are the authoritative ones recorded in this SUMMARY.
- **Manually reverted two blank-line insertions** the `requirements mark-complete` CLI tool made in unrelated sections of `REQUIREMENTS.md` (near two `f2f280c` commit-citation lines under LEG-01/LEG-04, and near the "Coverage" bullet list at the bottom) while ticking the six CHAN checkboxes -- kept the diff scoped to exactly the CHAN rows, matching 136-02's own precedent of a diff scoped to "exactly two hunks, both on CHAN-05's own lines."

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Reverted unrelated blank-line insertions the requirements-marking tool made outside CHAN-0X's own lines**
- **Found during:** Requirement-ticking step, after running `gsd-sdk requirements mark-complete CHAN-01 CHAN-02 CHAN-03 CHAN-04 CHAN-06 CHAN-07`.
- **Issue:** The tool's diff included two unrelated blank-line insertions inside the LEG-01/LEG-04 entries (between a `**Complete**` line and its own `+ \`f2f280c\`...` continuation) and two more in the "Coverage" bullet list near the bottom of the file -- none touching CHAN rows, all cosmetic markdown reflow with no content change, but outside this plan's declared scope (CHAN-01/02/03/04/06/07 only).
- **Fix:** Reverted the four extraneous blank lines via targeted `Edit` calls, leaving only the twelve CHAN-0X hunks (six checkbox lines + six traceability-table rows) in the final diff.
- **Files modified:** `.planning/REQUIREMENTS.md`
- **Verification:** `git diff .planning/REQUIREMENTS.md` shows exactly the CHAN-0X changes, nothing else.
- **Committed in:** the plan-metadata commit (this SUMMARY + REQUIREMENTS.md + STATE.md + ROADMAP.md), meta repo.

### Plan-Time Gap Discovered During Execution (documented, not fixed)

**1. Tasks 1 and 2's `tdd="true"` RED phase does not apply in the strict sense -- tests pass on first run.**
- **Found during:** Task 1's initial test run, immediately after authoring `test_dev_group_channel_gating.py`.
- **Issue:** The standard `tdd_execution` flow calls for a RED commit (tests fail) followed by a GREEN commit (implementation makes them pass). Both Task 1 and Task 2 in this plan author proof-only test files against mechanisms `136-01`/`136-02` already shipped in full; there is no corresponding `<implementation>` step and no new production code for this plan to write. All 12 (Task 1) and 11 (Task 2) tests passed on the very first run.
- **Action taken:** Committed each task as a single `test(...)` commit rather than a RED/GREEN pair, since a RED commit asserting deliberately-broken tests against already-correct code would misrepresent the plan's own nature (proof, not implementation) and there was no genuine implementation gap to bridge. This matches the plan's own framing in its `<objective>` ("Prove... everything plans 136-01/136-02 built") and its opening comment in `136-CONTEXT.md`'s cross-reference ("you are the plan that evidences the gate 136-02 built, which is why the ticks land here rather than there").
- **Not a defect**: every acceptance criterion in both tasks was met (Task 1: ≥10 tests, exact-set assertion present, env-override assertion present, typo-control assertion present, regression floor green; Task 2: ≥6 tests, non-vacuity RED captured and reverted).

---

**Total deviations:** 1 auto-fixed (1 Rule 1 out-of-scope tooling side-effect reverted), 1 plan-time gap documented (not a defect -- TDD framing does not literally apply to a proof-only plan, by the plan's own stated purpose).
**Impact on plan:** None on this plan's own scope, requirements, or non-vacuity obligations -- all four obligations (one inherited from 136-01, three owned by this plan) are discharged with verbatim RED output below.

## Non-Vacuity Obligations -- Verbatim RED Output

### Obligation (Task 2 / CHAN-07): `open("/dev/null")` planted inside `channel.is_dev_tools_enabled`

Mutation applied to `firestarter/channel.py`:
```python
def is_dev_tools_enabled() -> bool:
    ...
    _ = open("/dev/null")  # TEMPORARY non-vacuity plant (136-03 Task 2) -- reverted before commit
    return is_prerelease_build() or dev_tools_enabled_by_env()
```

`pytest tests/test_dev_gate_reads_no_firmware_source.py -o addopts="" -q -vv` (verbatim):
```
FAILED tests/test_dev_gate_reads_no_firmware_source.py::test_gate_callable_source_contains_no_open_call[channel.is_dev_tools_enabled]
_ test_gate_callable_source_contains_no_open_call[channel.is_dev_tools_enabled] _
AssertionError: channel.is_dev_tools_enabled's source contains an 'open(' call -- CHAN-07 requires the gate's own new code to read no file at all
assert 'open(' not in 'def is_dev_...d_by_env()\n'

FAILED tests/test_dev_gate_reads_no_firmware_source.py::test_channel_module_source_contains_no_open_call_anywhere
assert 'open(' not in '"""\nProjec...t."\n    )\n'

2 failed, 9 passed in 0.21s
```

Both failures correctly named `is_dev_tools_enabled` as (or as containing) the offending callable. `channel.py` was then restored byte-identically -- `git diff --stat firestarter/channel.py` printed nothing before the Task 2 commit -- and re-run to green (11 passed).

### Obligation (Task 3 / Mutation A): `cls=_DevGroup` removed

Mutation applied to `firestarter/cli_handlers.py`:
```python
@cli.group(name="dev")          # was: @cli.group(name="dev", cls=_DevGroup)
```

`pytest tests/test_dev_group_channel_gating.py -o addopts="" -q -vv` (verbatim, failing test only):
```
FAILED tests/test_dev_group_channel_gating.py::test_simulated_stable_gated_command_refuses_with_channel_message
_______ test_simulated_stable_gated_command_refuses_with_channel_message _______
    result = _run_cli(_STABLE_VERSION, ("dev", "reg", "0", "0", "0x86"))
    assert result.exit_code != 0
>   assert "dev reg" in result.output
E   assert 'dev reg' in "Usage: cli dev [OPTIONS] COMMAND [ARGS]...\nTry 'cli dev --help' for help.\n\nError: No such command 'reg'.\n"

1 failed, 11 passed in 2.82s
```

Exactly the predicted failure mode: with `_DevGroup` removed, the plain `click.Group` falls through to Click's own generic `No such command 'reg'.` instead of the channel-specific refusal. `cli_handlers.py` was then restored byte-identically -- `git diff --stat firestarter/cli_handlers.py` printed nothing -- and re-run to green (12 passed).

### Obligation (Task 3 / Mutation B): `_DEV_TOOLS_ENABLED` hardcoded to `True`

Mutation applied to `firestarter/cli_handlers.py`:
```python
_DEV_TOOLS_ENABLED: bool = True          # was: is_dev_tools_enabled()
```

`pytest tests/test_dev_group_channel_gating.py -o addopts="" -q -vv` (verbatim, failing test names):
```
FAILED tests/test_dev_group_channel_gating.py::test_simulated_stable_help_lists_only_read_and_test
FAILED tests/test_dev_group_channel_gating.py::test_simulated_stable_dev_tools_enabled_is_false
FAILED tests/test_dev_group_channel_gating.py::test_simulated_stable_dev_commands_is_exactly_read_and_test
_________ test_simulated_stable_dev_commands_is_exactly_read_and_test __________
    result = _run_cli(_STABLE_VERSION, ("dev", "--help"))
>   assert set(result.dev_commands) == _STABLE_NAMES
E   AssertionError: assert {'addr', 'con..., 'test', ...} == frozenset({'read', 'test'})
E     Extra items in the left set:
E     'write-cycle'
E     'addr'
E     'validate-family'
E     'reg'
E     'fault-inject'...
FAILED tests/test_dev_group_channel_gating.py::test_simulated_stable_gated_command_refuses_with_channel_message
FAILED tests/test_dev_group_channel_gating.py::test_dev_help_differs_between_channels_and_is_pinned_each_way
FAILED tests/test_dev_group_channel_gating.py::test_simulated_stable_dev_tools_env_override_absent_by_default

6 failed, 6 passed in 2.73s
```

The specific assertion the plan named (`test_simulated_stable_dev_commands_is_exactly_read_and_test`) failed as predicted -- all eight names registered regardless of simulated channel -- along with five other assertions that transitively depend on the stable channel genuinely excluding the six gated names. `cli_handlers.py` was then restored byte-identically -- `git diff --stat firestarter/cli_handlers.py` printed nothing before this task's (nonexistent, by design) commit -- and re-run to green (12 passed).

## Issues Encountered

None beyond the plan-time gap documented above (TDD framing not literally applicable to a proof-only plan) and the requirements-tool's cosmetic side-effect (reverted, see Auto-fixed Issues). mypy, ruff, and every targeted test command ran clean on every attempt.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Plan `136-04` can now proceed to re-baseline the `test_help`/`test_help_dev` snapshots (both named as deferred, per `136-02-SUMMARY.md`'s "Known Test Regressions" table) and record `136-CI-PARITY.md`'s `## After` section, using this plan's final measured numbers as the pre-136-04 starting point: mypy **33 errors (watermark 35), checked 130 source files**; full suite **1492 passed, 2 failed** (both snapshot-only, both already named for 136-04).
- All six requirements this plan owns (CHAN-01, CHAN-02, CHAN-03, CHAN-04, CHAN-06, CHAN-07) are ticked Complete in `.planning/REQUIREMENTS.md`, alongside CHAN-05 (ticked by 136-02). All seven CHAN requirements are now Complete; 136-VALIDATION.md's disjoint tick-ownership table is fully discharged.
- No blockers for 136-04.

## Self-Check: PASSED

Both declared files confirmed present on disk (`firestarter_app/tests/test_dev_group_channel_gating.py`, `firestarter_app/tests/test_dev_gate_reads_no_firmware_source.py`). Both commit hashes (`16ff598`, `11c5de4`) confirmed present in `firestarter_app`'s `git log --oneline --all`. `git diff --stat firestarter/cli_handlers.py firestarter/channel.py` confirmed empty (both files byte-identical to pre-plan state) immediately before this SUMMARY was written. `.planning/REQUIREMENTS.md`'s diff confirmed scoped to exactly the six CHAN-0X checkbox lines and six traceability-table rows.

---
*Phase: 136-dev-tools-channel-gating*
*Completed: 2026-08-05*
