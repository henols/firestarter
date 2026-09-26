---
phase: 136-dev-tools-channel-gating
plan: 02
subsystem: cli
tags: [click, channel-gating, conditional-registration, mypy, ci-parity]

# Dependency graph
requires:
  - phase: 136-dev-tools-channel-gating
    plan: 01
    provides: "channel.py's BETA_ONLY_DEV_COMMANDS, dev_tools_enabled_by_env, is_dev_tools_enabled, dev_command_gate_message; the empirically-pinned get_command Click hook (tests/test_click_group_gate_hook.py)"
provides:
  - "cli_handlers.py's _DevGroup(click.Group) -- the D-01 informative-refusal half of the gate, wired onto @cli.group(name=\"dev\", cls=_DevGroup)"
  - "cli_handlers.py's _DEV_TOOLS_ENABLED module constant, frozen at import time"
  - "Six @dev.command blocks (reg, addr, consistency-check, write-cycle, fault-inject, validate-family) conditionally registered under `if _DEV_TOOLS_ENABLED:`"
  - "The CHAN-06 tripwire comment at the dev reg block"
  - "The rewritten dev() group docstring (CHAN-05)"
affects: [136-03, 136-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "D-01's 'both mechanisms, not either': a Click Group subclass supplying an informative UsageError refusal (get_command override, CHAN-03) is paired with conditional registration at module scope (if _DEV_TOOLS_ENABLED: around each @dev.command block, CHAN-02) -- neither alone satisfies both requirements"
    - "_DEV_TOOLS_ENABLED: bool = is_dev_tools_enabled() captured once at import time, mirroring the existing _PY32_ENABLED / _BOARD_CHOICES pattern one screen above in the same file, so a wheel's fixed __version__ decides the registration set once, correctly, rather than re-evaluating a call-time function per invocation"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Split the plan's three described tasks into three separate atomic commits (wiring / conditional registration / docstring), reconstructing the working tree between commits via a scoped `git checkout -- firestarter/cli_handlers.py` restore-and-reapply rather than committing all edits in one lump, per the executor's per-task commit protocol"
  - "The tripwire comment literally names the FIRESTARTER_DEV_TOOLS environment variable (not just the two function names) so the acceptance criterion's grep target and a future reader searching for the env var by name both find the tripwire at the dev reg site"
  - "Left tests/__snapshots__/test_characterization.ambr untouched, exactly as instructed -- both test_help_dev AND test_help now fail (see Deviations), deliberately deferred to plan 136-04"

coverage:
  - id: CHAN-05
    description: "The dev group docstring no longer frames read/test as merely 'for development purposes' -- it now states plainly that on a stable install only read and test are available and both are fully supported end-user commands"
    verification:
      - kind: unit
        ref: "tests/test_cli_handlers.py (66 tests, unchanged, passing) + direct docstring assertion (dev.callback.__doc__ contains 'stable', 'read', 'test')"
        status: pass
    human_judgment: false
  - id: CHAN-01 (contributes, not ticked)
    description: "read and test remain the only two commands unconditionally registered at module scope; the six others are now behind if _DEV_TOOLS_ENABLED: guards"
    verification:
      - kind: unit
        ref: "python -c import check: {reg,addr,consistency-check,write-cycle,fault-inject,validate-family} <= cli_handlers.dev.commands.keys() (true in this pre-release checkout); stable-channel non-registration proof is 136-03's subprocess harness"
        status: pass
    human_judgment: false
  - id: CHAN-02 (contributes, not ticked)
    description: "Genuine non-registration: each of the six gated @dev.command blocks is wrapped in if _DEV_TOOLS_ENABLED: at module scope, so the function name itself never binds when the gate is closed"
    verification:
      - kind: unit
        ref: "grep -c 'if _DEV_TOOLS_ENABLED:' firestarter/cli_handlers.py == 6; python -c ast.parse(...) syntax check"
        status: pass
    human_judgment: false
  - id: CHAN-03 (contributes, not ticked)
    description: "_DevGroup.get_command raises an informative UsageError (channel.dev_command_gate_message) for a name in BETA_ONLY_DEV_COMMANDS that resolves to nothing real; a genuine typo still falls through to None"
    verification:
      - kind: unit
        ref: "tests/test_cli_handlers.py regression pass (in-process can't exercise the stable branch -- 136-03's subprocess proof closes this)"
        status: pass
    human_judgment: false
  - id: CHAN-06 (contributes, not ticked)
    description: "Tripwire comment at the dev reg block names FIRESTARTER_DEV_TOOLS, dev_tools_enabled_by_env, and is_dev_tools_enabled's OR-composition, and states what narrowing the override or removing the OR would strand"
    verification:
      - kind: other
        ref: "grep -c 'FIRESTARTER_DEV_TOOLS' firestarter/cli_handlers.py == 3 (tripwire comment, twice, plus the docstring's own mention)"
        status: pass
    human_judgment: false

duration: ~23min
completed: 2026-08-05
status: complete
---

# Phase 136 Plan 02: `_DevGroup` + Conditional Registration + CHAN-05 Docstring Summary

**Wired both D-01 mechanisms into `cli_handlers.py` -- a `_DevGroup(click.Group)` subclass supplying an informative refusal, and `if _DEV_TOOLS_ENABLED:` guards genuinely un-registering the six beta-only `dev` subcommands -- then rewrote the `dev` group's own docstring so it stops warning off the two commands (`read`, `test`) being kept in stable specifically for its own audience.**

## Performance

- **Duration:** ~23 min
- **Started:** 2026-08-05T11:13:00Z (approx., immediately following 136-01's completion)
- **Completed:** 2026-08-05T11:37:00Z
- **Tasks:** 3 (all `type="auto"`, none `tdd="true"`)
- **Files modified:** 2 (1 submodule production file across 3 commits, 1 meta-repo requirements doc)

## Accomplishments

- `_DEV_TOOLS_ENABLED: bool = is_dev_tools_enabled()` -- a module-level constant frozen at import time, mirroring the existing `_PY32_ENABLED` / `_BOARD_CHOICES` pattern already in this file, so a wheel's fixed `__version__` decides the six commands' registration set once, correctly, rather than re-evaluating `channel.is_dev_tools_enabled()` (a call-time, unmemoized function per its own docstring) on every invocation.
- `_DevGroup(click.Group)` -- holds no callback, only consults `channel.BETA_ONLY_DEV_COMMANDS` inside its sole overridden method, `get_command`. The override shape (`super().get_command()` first; raise `click.UsageError(dev_command_gate_message(cmd_name), ctx=ctx)` only for a recognized gated name; otherwise `None`) is copied exactly from plan 136-01's empirically-proven spike (`tests/test_click_group_gate_hook.py`) -- `resolve_command` and `list_commands` needed no override, per that spike's own findings. `@cli.group(name="dev")` became `@cli.group(name="dev", cls=_DevGroup)`.
- All six gated `@dev.command` blocks (`reg`, `addr`, `consistency-check`, `write-cycle`, `fault-inject`, `validate-family`) are now wrapped, decorator-through-body, in `if _DEV_TOOLS_ENABLED:` at module scope -- content otherwise byte-identical, just re-indented four spaces. `read` and `test` stay unconditional, per CHAN-01. A `python -c "import ast; ast.parse(...)"` check confirmed syntactic validity immediately after wrapping, before any test ran.
- A CHAN-06 tripwire comment, in the file's own `RETIRE-07` style, sits immediately above the (now-indented) `dev reg` decorator: it names the `FIRESTARTER_DEV_TOOLS` environment variable explicitly, explains `dev reg`'s role as the held-erase-rail DMM proxy, and states that narrowing the accepted override value or removing the `OR` in `channel.is_dev_tools_enabled` strands that bench tooling without warning.
- The `dev()` group docstring no longer says "Debug command for development purposes." -- it now opens with "Development and diagnostic commands for the RURP shield." and states plainly that `read`/`test` are the two stable-available, fully-supported-for-end-users commands, with the rest being pre-release-only bench tooling. The real hardware note ("USR button will break command and return.") is preserved verbatim.
- Verified throughout: `tests/test_cli_handlers.py` (66 tests), the RESEARCH §5 blast-radius suite (244 tests across 8 files), `tests/test_py32_channel_gating.py` (14 tests, the regression-floor row), `python -c` registration/import checks, `ast.parse` syntax check, `ruff check`/`ruff format --check` (both directory-scoped and file-scoped), and a fresh `mypy firestarter/ tests/` run via `.venv/ci-replica`: **33 errors (watermark 35, headroom 2), checked 128 source files** -- unchanged from plan 136-01's baseline. The new `_DevGroup.get_command` is fully annotated (`ctx: click.Context`, `cmd_name: str`, return `Optional[click.Command]`) and introduced zero new mypy errors.

## Task Commits

Each task was committed atomically, in the submodule (`firestarter_app`, on `gsd/v1.30-sdp-surface-retirement`):

1. **Task 1: `_DevGroup` subclass + `_DEV_TOOLS_ENABLED` + group wiring** - `6e2fb39` - `firestarter/cli_handlers.py`
2. **Task 2: Conditional registration of the six gated commands + CHAN-06 tripwire** - `88ec58e` - `firestarter/cli_handlers.py`
3. **Task 3: CHAN-05 -- rewrite the `dev` group's docstring** - `c8f8a53` - `firestarter/cli_handlers.py`

**Plan metadata:** committed separately below (meta repo, this SUMMARY + REQUIREMENTS.md + STATE.md + ROADMAP.md).

_Note: per this plan's own `<repo_topology>`, all production code lives inside the `firestarter_app` submodule; this SUMMARY and requirement-ticking land in the meta repo (`/workspaces`, `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`). The two branch names deliberately diverge._

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` (submodule) -- `_DevGroup`, `_DEV_TOOLS_ENABLED`, six conditionally-registered `dev` subcommand blocks, the CHAN-06 tripwire comment, and the rewritten `dev()` docstring.
- `.planning/REQUIREMENTS.md` (meta repo) -- **CHAN-05** ticked Complete (checkbox + traceability-table row). No other requirement row touched -- confirmed by a scoped `git diff` before committing, which showed exactly two hunks, both on CHAN-05's own lines.

## Decisions Made

- **Split into three atomic per-task commits, not one lump commit.** The plan describes three distinct tasks with three distinct acceptance-criteria sets; committing them separately (via a scoped `git checkout -- firestarter/cli_handlers.py` restore-and-reapply between commits, sanctioned by the destructive-git-prohibition's own carve-out for a single file the executor is actively editing) keeps each commit's diff reviewable against its own task, exactly as Task 1's own action text asks for ("this task's diff is reviewable as 'wiring only'").
- **The tripwire comment names `FIRESTARTER_DEV_TOOLS` literally**, not just its two companion function names, so both a grep for the env var and a human reader scanning the `dev reg` site find the dependency immediately.
- **Followed the plan's explicit instruction to leave `tests/__snapshots__/test_characterization.ambr` untouched** even though this task's docstring change breaks it -- see Deviations below for the one place this went further than the plan anticipated.

## Deviations from Plan

### Auto-fixed Issues

None. Every fix this plan needed was already specified in the plan's own action text (the tripwire comment's exact content, the wrapping shape, the docstring's three required parts) -- there was no bug, missing functionality, or blocking issue outside the plan's own instructions to auto-fix.

### Plan-Time Gap Discovered During Execution (documented, not fixed)

**1. The CHAN-05 docstring change breaks TWO snapshot tests, not the one the plan named.**
- **Found during:** Task 3's post-edit full-suite verification.
- **Issue:** The plan's Task 3 `<read_first>` names only `tests/__snapshots__/test_characterization.ambr`'s `test_help_dev` entry as the snapshot this docstring rewrite will change, and explicitly defers its re-baselining to plan `136-04`. What the plan did not anticipate: Click renders a group's `short_help` (used in the *parent* command's `Commands:` listing) from the *same* first-line-of-docstring text. So `firestarter --help`'s own top-level listing line -- `dev     Debug command for development purposes.` -- also changed, breaking `test_help`'s snapshot too, by the identical mechanism, in the same file.
- **Action taken:** Left both `test_help` and `test_help_dev` failing, exactly as the plan's own instruction for `test_help_dev` alone already authorized ("plan 136-04 re-baselines it; this task does not touch the snapshot"). Re-baselining snapshots is explicitly reserved for plan `136-04` by this plan's own scope discipline (see Task 3's action text on the module-docstring "6 sub-commands" enumeration: "touching it here would be uncontrolled scope creep against this plan's single concern"). Fixing a second, previously-unnamed snapshot would be the identical class of action.
- **Files affected:** `firestarter_app/tests/__snapshots__/test_characterization.ambr` -- NOT modified by this plan.
- **Verification:** `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` -- 1469 passed, 2 failed (`test_help`, `test_help_dev`), 1471 collected. This is a **larger deferred-red count than 136-VALIDATION.md's wave-4 row anticipated** (it named only `test_help_dev`); flagging for plan `136-04`'s executor so both snapshots are re-baselined together, diff-scoped to the docstring text only.
- **Not committed as a fix** -- no commit touches the snapshot file.

---

**Total deviations:** 0 auto-fixed. 1 plan-time gap discovered and documented (not fixed, per the plan's own scope discipline) for plan 136-04 to pick up.
**Impact on plan:** None on this plan's own scope or requirement (CHAN-05 is a pure docstring-text fact, fully discharged in-process, independent of any snapshot's pass/fail state). The impact is entirely on plan 136-04's inherited to-do list, which now needs to re-baseline one additional snapshot entry.

## Known Test Regressions (Deferred to Plan 136-04)

| Test | File | Cause | Owner |
|------|------|-------|-------|
| `test_help_dev` | `tests/test_characterization.py` | `dev` group docstring text changed (CHAN-05) | 136-04 (named in 136-VALIDATION.md wave 4) |
| `test_help` | `tests/test_characterization.py` | Same docstring change also alters the `dev` group's rendered `short_help` in the top-level `Commands:` listing | 136-04 (newly discovered here; NOT named in 136-VALIDATION.md) |

Both are snapshot-only failures (`syrupy`) with no logic defect -- the rendered CLI text simply differs from the stale snapshot, in exactly the way CHAN-05 intends. `tools/ci_replica_venv.sh`'s leg 5 (full pytest run) will show these two failures until 136-04 re-baselines both entries.

## Issues Encountered

None beyond the plan-time gap documented above. mypy, ruff, and every targeted test command ran clean on the first attempt for each task.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Plan `136-03` can now build its subprocess dual-channel proof (`tests/test_dev_group_channel_gating.py`) against a finished `_DevGroup` + six-block conditional-registration shape -- nothing in this file's `dev`-group surface is expected to change again before 136-03 reads it, other than the `cls=_DevGroup` removal / `_DEV_TOOLS_ENABLED` hardcoding / `open()`-planting mutations 136-03's own non-vacuity obligations call for (each restored byte-identically after observation, per 136-VALIDATION.md's table).
- Plan `136-04` inherits two snapshot entries to re-baseline (`test_help`, `test_help_dev`), not the one 136-VALIDATION.md named -- see the table above.
- Zero requirements ticked beyond **CHAN-05**. CHAN-01, CHAN-02, CHAN-03, CHAN-04, CHAN-06, CHAN-07 remain `Pending`, to be closed by plan `136-03` per this plan's own ticking-scope instruction and 136-VALIDATION.md's disjoint-ownership table.

## Self-Check: PASSED

All 3 declared task commits (`6e2fb39`, `88ec58e`, `c8f8a53`) confirmed present in `firestarter_app`'s `git log --oneline --all`; `firestarter/cli_handlers.py` confirmed to contain exactly 1 `class _DevGroup`, 1 `_DEV_TOOLS_ENABLED: bool = is_dev_tools_enabled()`, 1 `cls=_DevGroup`, 6 `if _DEV_TOOLS_ENABLED:` guards, and 3 occurrences of `FIRESTARTER_DEV_TOOLS`. `.planning/REQUIREMENTS.md`'s diff confirmed scoped to exactly CHAN-05's checkbox and traceability row. No missing items.

---
*Phase: 136-dev-tools-channel-gating*
*Completed: 2026-08-05*

## Self-Check: PASSED (re-verified)

Re-confirmed independently before the final commit: `136-02-SUMMARY.md` present on disk; `firestarter_app/firestarter/cli_handlers.py` present on disk; all 3 commit hashes (`6e2fb39`, `88ec58e`, `c8f8a53`) found in `git log --oneline --all` inside the submodule. No missing items.
