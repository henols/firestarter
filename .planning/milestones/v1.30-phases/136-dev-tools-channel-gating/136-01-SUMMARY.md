---
phase: 136-dev-tools-channel-gating
plan: 01
subsystem: cli
tags: [click, channel-gating, env-var, fail-closed, mypy, ci-parity]

# Dependency graph
requires:
  - phase: 134-the-plan-derived-sdp-oracle-in-dev-test
    provides: closing mypy/coverage/test-count baseline (33/35, 126 checked, 1437 passed, 82.12%) that this plan's own fresh measurement happens to match byte-for-byte
provides:
  - "136-CI-PARITY.md's `## Before (pre-edit)` section: the phase's only legitimate mypy/test/coverage starting count (RESEARCH §7: nothing to inherit)"
  - "An empirically-pinned Click 8.x fact: `get_command` (not `resolve_command`) is the hook a gated-but-unregistered command name must be refused from"
  - "`channel.py`'s four new symbols (`BETA_ONLY_DEV_COMMANDS`, `dev_tools_enabled_by_env`, `is_dev_tools_enabled`, `dev_command_gate_message`) that plan 136-02's `_DevGroup` imports"
affects: [136-02, 136-03, 136-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fail-closed env-var gate: exact-string equality (`== \"1\"`), never `bool(...)` coercion, `.strip()`, or case-folding — the Python-side mirror of avoiding the firmware `-D X=${sysenv.VAR}` fail-OPEN trap"
    - "Click Group subclass overrides only `get_command`; `resolve_command` and `list_commands` need no override when a gated name is simply never registered"

key-files:
  created:
    - .planning/phases/136-dev-tools-channel-gating/136-CI-PARITY.md
    - firestarter_app/tests/test_click_group_gate_hook.py
    - firestarter_app/tests/test_dev_tools_channel_gate.py
  modified:
    - firestarter_app/firestarter/channel.py

key-decisions:
  - "D-02/D-03 (136-CONTEXT.md) implemented as written: reuse is_prerelease_build(), never a second detector; FIRESTARTER_DEV_TOOLS fails closed on every value except the exact literal \"1\""
  - "Module docstring in channel.py corrected (Rule 1 doc-bug): it previously claimed \"Nothing here reads the environment\", which the new dev_tools_enabled_by_env() makes literally false; rewritten to name the one deliberate, fail-closed exception"

patterns-established:
  - "Non-vacuity proof for a fail-closed gate: plant the exact bool(os.environ.get(...)) mutation the design doc warns against, observe the named failure cases RED, restore byte-identically before commit"

requirements-completed: []  # This plan MAY tick none — CHAN-06/CHAN-07 are contributed to, not closed. See 136-01-PLAN.md and the executor's explicit ticking-scope instruction. Closed by plan 136-03.

coverage:
  - id: D1
    description: "Pre-edit CI-parity + CI-replica baseline recorded before any production line moved: mypy 33 errors (watermark 35), checked 126 source files, 1437 tests passed, 82.12% coverage"
    verification:
      - kind: other
        ref: ".planning/phases/136-dev-tools-channel-gating/136-CI-PARITY.md ## Before section"
        status: pass
    human_judgment: false
  - id: D2
    description: "Click's get_command hook (not resolve_command) empirically shown to intercept a gated-but-unregistered command name before Click's own generic error, while a genuine typo still gets Click's unmodified generic error"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_click_group_gate_hook.py (7 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "channel.py bench-override vocabulary (BETA_ONLY_DEV_COMMANDS, dev_tools_enabled_by_env, is_dev_tools_enabled, dev_command_gate_message) added and proven fail-closed, including a planted-mutation non-vacuity check"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dev_tools_channel_gate.py (27 tests)"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-08-05
status: complete
---

# Phase 136 Plan 01: Pre-edit CI-Parity Baseline + Click-Hook Spike + channel.py Dev-Tools Vocabulary Summary

**Measured a fresh mypy/test baseline with no number to inherit, empirically pinned `get_command` (not `resolve_command`) as Click's gate hook via a throwaway spike, and added a fail-closed `FIRESTARTER_DEV_TOOLS` bench-override vocabulary to `channel.py` — proven fail-closed by a planted `bool()`-coercion mutation observed RED then restored byte-identically.**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-08-05T10:44:00Z (approx.)
- **Completed:** 2026-08-05T11:06:00Z
- **Tasks:** 3 (Task 3 followed TDD RED → GREEN)
- **Files modified:** 4 (1 meta-repo doc, 1 submodule production file, 2 submodule test files)

## Accomplishments
- `136-CI-PARITY.md` records the phase's only legitimate starting budget: mypy `33` errors (watermark `35`, headroom `2`), `checked 126 source files` (margin `6` above the `120` floor), `1437` tests passed, `30` snapshots passed, `82.12%` coverage — measured via `tools/ci_replica_venv.sh`, never the devcontainer's own mypy (which exits 2 against the ambient numpy PEP-695 stub).
- `tests/test_click_group_gate_hook.py` is a standalone, in-process spike (no import of `firestarter.cli_handlers`) that proves, against this environment's real installed Click: (1) `get_command` intercepts a gated-but-unregistered name before Click's own `resolve_command`/`UsageError` fallback fires; (2) a genuine typo still gets Click's unmodified generic error, i.e. the override does not swallow real typos; (3) the one real registered command runs normally; (4) `resolve_command` is structurally never overridden; (5) `list_commands` needs no override because a gated-but-unregistered name is simply absent from `self.commands`. This settles 136-RESEARCH.md §1's open question for plan 136-02's `_DevGroup`.
- `firestarter/channel.py` gained four fully-typed, fully-tested symbols: `BETA_ONLY_DEV_COMMANDS` (the six gated `dev` subcommand names, informative-refusal lookup only), `dev_tools_enabled_by_env()` (fails closed on everything except the exact literal `"1"`), `is_dev_tools_enabled()` (`is_prerelease_build() or dev_tools_enabled_by_env()`), and `dev_command_gate_message(name)` (mirrors `beta_only_message`'s shape). `channel.py` itself still calls no `open(` anywhere (asserted by a dedicated test) — the file-scoped contribution to CHAN-07.
- The fail-closed matrix was proven non-vacuous: `dev_tools_enabled_by_env` was temporarily broadened to `bool(os.environ.get("FIRESTARTER_DEV_TOOLS"))`, 14 of 27 tests in `test_dev_tools_channel_gate.py` went RED (including the `"0"` and `"false"` cases named in the plan's acceptance criteria, plus every other fail-closed value), and the function was restored to the exact-match comparison byte-identically (`git diff` confirmed empty for that line before the commit).

## Task Commits

Each task was committed atomically:

1. **Task 1: Record the pre-edit CI-parity + CI-replica baseline** - `73c8c85` (meta repo, docs) — `.planning/phases/136-dev-tools-channel-gating/136-CI-PARITY.md`
2. **Task 2: Empirically settle which Click hook carries the informative refusal** - `09803f6` (submodule, test) — `firestarter_app/tests/test_click_group_gate_hook.py`
3. **Task 3: `channel.py` bench-override vocabulary + fail-closed proof + non-vacuity** (TDD):
   - RED - `21c6d10` (submodule, test) — `firestarter_app/tests/test_dev_tools_channel_gate.py`, 26 failed / 1 passed (the source-scan test passed vacuously — it asserts a pre-existing invariant, not new behavior)
   - GREEN - `893490a` (submodule, feat) — `firestarter_app/firestarter/channel.py`, all 27 new tests pass; non-vacuity obligation discharged in the same working session before this commit (mutation observed RED, restored byte-identically — see below)

**Plan metadata:** committed separately below (docs: complete plan).

_Note: this plan spans two git repositories — the meta repo (`/workspaces`, Task 1 only) and the `firestarter_app` submodule (Tasks 2-3), per the plan's own `<repo_topology>` instruction. Commit hashes above are each scoped to their own repo._

## Files Created/Modified
- `.planning/phases/136-dev-tools-channel-gating/136-CI-PARITY.md` (meta repo) - pre-edit CI-parity + CI-replica baseline record; `## After` section left for plan 136-04
- `firestarter_app/tests/test_click_group_gate_hook.py` - standalone Click-mechanism spike (7 tests), independent of `firestarter.cli_handlers`
- `firestarter_app/tests/test_dev_tools_channel_gate.py` - fail-closed matrix, truth table, message shape, and no-`open()` source-scan tests (27 tests)
- `firestarter_app/firestarter/channel.py` - added `BETA_ONLY_DEV_COMMANDS`, `dev_tools_enabled_by_env()`, `is_dev_tools_enabled()`, `dev_command_gate_message()`; corrected the module docstring's now-stale "nothing here reads the environment" claim

## Decisions Made
- Followed 136-CONTEXT.md D-02 and D-03 exactly as locked: one detector (`is_prerelease_build`), reused not duplicated; the bench override is fail-closed by exact-string-equality construction, not by convention.
- `dev_tools_enabled_by_env()` and `is_dev_tools_enabled()` are call-time functions (mirroring `config.py`'s `get_config_dir()` style), explicitly documented as needing import-time capture by any caller (plan 136-02's `_DevGroup`) that requires a frozen-at-import decision — this is stated in both docstrings so a future reader does not accidentally call them from inside a hot Click callback expecting import-time semantics.
- The Click-hook spike (Task 2) intentionally never imports `firestarter.cli_handlers` — it tests a fact about the installed `click` package, not about this project's own gate, matching D-04's reasoning that only the project's *own* channel test needs a subprocess (that proof is plan 136-03's).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected `channel.py`'s module docstring, which the new code made false**
- **Found during:** Task 3
- **Issue:** The existing module docstring stated flatly "Nothing here reads the environment. A channel gate that can be flipped by an env var is not a gate...". Adding `dev_tools_enabled_by_env()` (which deliberately does read `os.environ`) would leave that claim literally false for a future reader, in the same file that documents the exact firmware fail-OPEN trap this new function is designed to avoid falling into.
- **Fix:** Rewrote the docstring to state precisely which functions read nothing from the environment (`is_prerelease_build`, `is_board_available`, `available_boards` — unchanged) and which one deliberate, fail-closed exception now exists (`dev_tools_enabled_by_env`, composed into `is_dev_tools_enabled`), with the reasoning inline.
- **Files modified:** `firestarter_app/firestarter/channel.py`
- **Verification:** `ruff check`/`ruff format --check` pass; no test asserts docstring text, so this is a documentation-accuracy fix with no behavioral surface.
- **Committed in:** `893490a` (Task 3 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 documentation bug)
**Impact on plan:** Documentation-only; no behavioral change, no scope creep. Necessary so `channel.py`'s own docstring does not contradict its own code the moment this plan lands.

## Issues Encountered

**Click version differs between the two local interpreters this phase's tooling actually uses.** The devcontainer's ambient `python3` (used for a quick manual check) reports Click `8.3.3`, matching 136-RESEARCH.md §1's measurement exactly. But `.venv/ci-replica/bin/python` — the interpreter every acceptance-criteria command in this plan actually runs under — has Click `8.4.2` installed (both satisfy `pyproject.toml`'s unpinned `click>=8.1`). Verified live that the load-bearing facts hold on both: `click.MultiCommand` is absent from `dir(click)` but still reachable as a deprecated alias (`click.core._MultiCommand`) on both 8.3.3 and 8.4.2, and `click.Group.get_command`/`resolve_command`/`list_commands` all carry the same signatures on both. `tests/test_click_group_gate_hook.py` deliberately does not hardcode an assertion that the installed version equals `"8.3.3"` — it captures `importlib.metadata.version("click")` at import time (per the plan's own instruction to cite that, not the deprecated `click.__version__`) purely so a future reader can see which version a given test run measured against, without the test breaking on a routine Click patch bump. Not a blocker; recorded because a later plan reading 136-RESEARCH.md §1 in isolation would reasonably expect only `8.3.3` to be present in this environment.

**A pre-existing project doc line names a design principle this plan deliberately makes a bounded exception to.** `firestarter_app/CLAUDE.md`'s `channel.py` bullet says "Never gate on an env var — it fails open." Read literally against the new `dev_tools_enabled_by_env()`, that could look like a contradiction. It is not: that line documents the reasoning behind `BETA_ONLY_BOARDS`/`is_prerelease_build`'s design (still true — those remain env-var-free), and 136-CONTEXT.md D-03 explicitly designs `FIRESTARTER_DEV_TOOLS` as the deliberate, narrow, *fail-closed* exception to exactly that failure mode (the opposite of "fails open"). `channel.py`'s own module docstring was updated (see Deviation 1 above) to state this distinction inline. `firestarter_app/CLAUDE.md` itself was left untouched — it is outside this plan's `files_modified` list and its existing bullet is not made false by this change (env-var gating still fails open in general; this one override is the named, tested exception). Flagging this for the plan-checker / a future reader rather than silently editing project-level documentation outside this plan's declared scope.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 136-02 can now import `BETA_ONLY_DEV_COMMANDS`, `is_dev_tools_enabled`, and `dev_command_gate_message` from `channel.py` and implement `_DevGroup.get_command` using exactly the mechanism Task 2's spike pinned.
- `136-CI-PARITY.md`'s `## Before` section is in place for plan 136-04 to pair with an `## After` section at phase close.
- No blockers. CHAN-06 and CHAN-07 remain open (by design — this plan ticks neither; see `requirements-completed: []` above and 136-01-PLAN.md's own "MAY tick: none" statement). Zero requirements marked Complete by this plan.

## TDD Gate Compliance

Task 3 was `tdd="true"`. Gate sequence verified in `firestarter_app` git log:
1. RED — `21c6d10` `test(136-01): add failing tests for channel.py dev-tools bench-override vocabulary` (26 failed / 1 passed).
2. GREEN — `893490a` `feat(136-01): add fail-closed dev-tools bench-override vocabulary to channel.py` (27 passed).
3. REFACTOR — none needed; no separate `refactor(...)` commit.

Both RED and GREEN gate commits present, in order. Compliant.

## Self-Check: PASSED

All 4 declared files confirmed present on disk; all 4 commit hashes (1 meta-repo, 3 submodule) confirmed present in their respective `git log --oneline --all`. No missing items.

---
*Phase: 136-dev-tools-channel-gating*
*Completed: 2026-08-05*
