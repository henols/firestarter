---
phase: 132-retire-dev-sdp-discharge-the-mypy-debt
plan: 04
subsystem: cli
tags: [click, sdp, retirement, mypy, snapshot-testing]

# Dependency graph
requires:
  - phase: 132-03
    provides: "tests/test_sdp_honesty.py holding the four honesty assertions retargeted onto firestarter/sdp_honesty.py (no CliRunner driving dev_sdp), and 132-PRUNE-LEDGER.md accounting for every dropped test case"
provides:
  - "firestarter/cli_handlers.py's dev_sdp span (registration decorator through EOF) permanently deleted, along with its four gates (absent-chip, capability, support-status, consent)"
  - "the dev group's subcommand roster reduced from nine to exactly eight, proven by positive enumeration"
  - "the orphaned firestarter.sdp_honesty import removed from cli_handlers.py -- the helper module itself survives untouched as a library with no production caller until Phase 134"
  - "tests/__snapshots__/test_characterization.ambr's test_help_dev entry updated by exactly one deleted line, node-scoped"
  - "the D-05 residual (no user-reachable carrier for the honesty caveat between this phase and Phase 134) stated plainly"
  - "RETIRE-01 marked Complete in REQUIREMENTS.md"
affects: [132-05, 132-06, 132-07, 132-08, 132-09, 134, 135, 136]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Tail-truncation deletion: the last function in a module is removed by truncating the file at the preceding function's final line plus its two-blank-line separator, rather than a line-range sed/awk delete -- avoids off-by-one boundary errors at EOF"
    - "Node-scoped snapshot update (pytest node-id + --snapshot-update) followed by a git diff --stat shape check before trusting the result, per D-13 -- never a bare module/session-wide --snapshot-update"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "The deletion boundary was re-measured live rather than trusting the plan's pre-rewire line numbers: the span had shifted to :2196 (decorator) - :2213 (def) - :2304 (EOF) after plan 132-02's rewire, not the plan's originally-cited :2321 EOF. Confirmed by grepping the sibling dev_test registration and counting forward."
  - "Only the firestarter.sdp_honesty import was removed from the import block. Confirm, FirmwareOutdatedError, EpromOperationError, sdp_capability, resolve_chip, and ChipNotFoundError were individually grep-counted inside vs. outside the deleted span (all have live uses outside, at lines 187-1796) and were left untouched. The firestarter.messages import for MSG_ERR_UNKNOWN_CMD was reconfirmed absent -- already removed by plan 132-02 -- and not re-added."
  - "Task 3's post-deletion code sweep (`grep -rn \"dev sdp\" --include='*.py'`) returned 5 hits, not the plan's acceptance-criterion-expected 0. All five are historical-provenance prose inside firestarter/sdp_honesty.py's and tests/test_sdp_honesty.py's own docstrings (created by plans 132-02/132-03, explaining each module's origin from the now-retired command) -- not code that drives or references a live command. Task 3 is declared read-only (`<files>none</files>` in its own frontmatter) and neither file is in this plan's `files_modified` list, so these docstrings were left untouched rather than edited to satisfy a grep the plan's own 'measured anchors' section got wrong. Recorded here as a plan-measurement discrepancy, not fixed."

requirements-completed: [RETIRE-01]

coverage:
  - id: D1
    description: "The dev_sdp subcommand and its four gates (absent-chip, capability, support-status, consent with both the on-TTY Confirm.ask branch and the off-TTY refusal) are permanently deleted from cli_handlers.py; the dev group's roster is exactly eight, proven by positive enumeration; invoking the retired command fails with Click's no-such-command error."
    requirement: "RETIRE-01"
    verification:
      - kind: unit
        ref: "python -c \"from firestarter.cli_handlers import dev; names=sorted(dev.commands); assert names==['addr','consistency-check','fault-inject','read','reg','test','validate-family','write-cycle']\" -- ROSTER OK 8"
        status: pass
      - kind: integration
        ref: "python -c \"import subprocess; r=subprocess.run(['firestarter','dev','sdp','--help'],capture_output=True,text=True); assert r.returncode!=0; assert 'No such command' in (r.stderr+r.stdout)\" -- REFUSED OK"
        status: pass
      - kind: unit
        ref: "ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/ -- both exit 0, proving the import block is exactly right"
        status: pass
    human_judgment: false
  - id: D2
    description: "The help snapshot (test_characterization.ambr's test_help_dev entry) loses exactly one line -- node-scoped update, zero insertions anywhere, no neighbouring snapshot disturbed."
    requirement: "RETIRE-01"
    verification:
      - kind: unit
        ref: "git diff --stat tests/__snapshots__/test_characterization.ambr -- '1 file changed, 1 deletion(-)', 0 insertions"
        status: pass
      - kind: unit
        ref: "tests/test_characterization.py::test_help_dev (passes without --snapshot-update) and the full module (30 snapshots passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "No output was added to the write auto-unlock path (D-05); the residual is stated plainly rather than engineered around."
    requirement: "RETIRE-01"
    verification:
      - kind: unit
        ref: "git diff -- firestarter/cli_handlers.py | grep -c '^+.*click.echo' -- returns 0"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-03
status: complete
---

# Phase 132 Plan 04: Delete `dev sdp` and Update the Help Snapshot Summary

**Deleted the ~112-line `dev_sdp` span (registration decorator through EOF) and its four gates from `cli_handlers.py`, removed the one orphaned `sdp_honesty` import, and node-scoped the `test_help_dev` snapshot down by exactly one line -- the `dev` group's roster is now eight commands, proven by positive enumeration, and the retired command fails with Click's no-such-command error.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-03T18:52:59Z (per STATE.md's prior session marker)
- **Completed:** 2026-08-03T19:16:00Z (approx)
- **Tasks:** 3
- **Files modified:** 2 (`cli_handlers.py`, `test_characterization.ambr`); 0 files created

## Accomplishments

- **Task 1 (RETIRE-01):** Deleted the entire `dev_sdp` command span from `firestarter/cli_handlers.py` -- the `@dev.command(name="sdp")` registration decorator, the `eprom`/`mode` arguments, the `-y/--yes` option decorator, `pass_obj`/`map_typed_errors`, the function definition, docstring, and body through end of file (re-measured live at `:2196-2304`, not the plan's pre-rewire `:2321` EOF, since plan 132-02's rewire had already shifted the tail). All four gates went with it: Gate 1 (absent-chip hard-fail), Gate 2 (capability refusal), Gate 3 (support-status resolution), Gate 4 (consent, both the on-TTY `Confirm.ask` branch and the off-TTY refusal). File truncated at the preceding `dev_test` function's final `sys.exit(code)` line plus its existing two-blank-line separator -- no line-range surgery needed. Removed the now-orphaned `from firestarter.sdp_honesty import emission_summary, map_unknown_cmd_to_outdated` line; `Confirm`, `FirmwareOutdatedError`, `EpromOperationError`, `sdp_capability`, `resolve_chip`, and `ChipNotFoundError` were each grep-counted inside vs. outside the deleted span and confirmed to have live uses elsewhere (lines 187-1796), so none were touched. The `firestarter.messages` import for `MSG_ERR_UNKNOWN_CMD` was reconfirmed absent (already removed by 132-02) and not re-added. Committed as `259a0f0`.
- **Task 2 (D-13):** Ran `pytest tests/test_characterization.py::test_help_dev --snapshot-update`, node-scoped to that single test id. **`git diff --stat` (verbatim):** ` tests/__snapshots__/test_characterization.ambr | 1 -` / ` 1 file changed, 1 deletion(-)`. Zero insertions anywhere in the file (`grep -c '^+[^+]'` returns 0). The node-scoped test then passes with no update flag, and the full `test_characterization.py` module (30 snapshots) stays green, proving no neighbouring snapshot was disturbed. Route used: **the primary node-scoped `--snapshot-update` route** (not the restore-and-hand-edit fallback), because the diff came back in the exact expected shape (one deletion, zero insertions) on the first attempt. Committed as `323c515`.
- **Task 3 (sweep, no code change):** Re-ran the acceptance-leg sweeps as measured facts, not inherited claims.
  - Markdown sweep: `grep -rl "dev sdp" /workspaces/firestarter_app --include='*.md' | wc -l` → **0**.
  - Non-vacuity proof: `find /workspaces/firestarter_app -name '*.md' -not -path '*/.git/*' | wc -l` → **38** files scanned; `grep -rl "firestarter" /workspaces/firestarter_app --include='*.md' | wc -l` → **24** files hit on a known-present token -- the file set is real and the pattern mechanism works over it.
  - Code sweep: `grep -rn "dev sdp" /workspaces/firestarter_app --include='*.py' | wc -l` → **5**, not the plan's acceptance-criterion-expected 0. See "Deviations from Plan" below.
  - mypy re-measurement via `bash tools/ci_replica_venv.sh`: **63 errors** (checked 122 source files; watermark 35), down from the plan-time pre-change reading of **69** recorded in `132-MYPY-LEDGER.md` §1. Arithmetic: 69 − 63 = **6**, matching the expected six-error reduction from plan 132-03's removal of `test_dev_sdp_cmd.py`'s local `make_app_context` factory (its per-file distribution row in the ledger: 6 errors) exactly. `Found 63 errors in 16 files (checked 122 source files)` -- the `checked` value (122) clears the `MIN_CHECKED_SOURCE_FILES = 120` floor with 2 to spare.
  - `bash tools/ci_replica_venv.sh` leg 5 (`pytest --cov=firestarter --cov-fail-under=70`, CI's exact invocation): **1295 passed, coverage 81.72%** -- the deletion introduced no coverage-floor regression despite removing ~112 covered production lines and their driving tests.
  - `python -m pytest tests/ -q`: **0 failures**, 30/30 snapshots passed.
  - `git -C /workspaces/firestarter_app status --porcelain`: matches the pre-existing dirt exactly (` M .gitignore`, `?? .coverage`, `?? .planning/config.json`, `?? SECURITY.md`, `?? write_test_port.sh`) -- nothing of this plan's own left uncommitted.
- **Requirements marked Complete:** RETIRE-01. No other RETIRE id touched.

## Task Commits

Each task was committed atomically, in the repo that owns the file:

1. **Task 1: delete the `dev_sdp` span + orphaned import** — `259a0f0` (feat, `firestarter_app` submodule)
2. **Task 2: node-scoped snapshot update** — `323c515` (test, `firestarter_app` submodule)
3. **Task 3: post-deletion sweep** — read-only, no commit (findings recorded above and below)

**Plan metadata:** this summary + STATE.md/ROADMAP.md/REQUIREMENTS.md updates (meta-repo, separate commit per `<final_commit>`).

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` — `dev_sdp` command and its four gates deleted (112 lines removed: 111-line span + 1 import line); roster now eight commands.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — `test_help_dev`'s `sdp` line removed (1 deletion, 0 insertions).

## Decisions Made

- **Re-measured the deletion boundary live rather than trusting either the plan's pre-rewire anchors or the phase-level pattern map's post-rewire anchors verbatim.** Both cited slightly different EOF line numbers (`:2321` in `132-04-PLAN.md`'s `<measured_anchors>`, still describing the pre-rewire file). The actual current file (`8caf77f` + 132-02/03's six commits) had `@dev.command(name="sdp")` at `:2196` and EOF at `:2304`. Confirmed by grepping every `@dev.command`/`def dev_` pair in the file and counting forward from the sibling `dev_test` registration, per D-11's "function names first, numbers alongside, re-measure at plan time" discipline.
- **Removed only the `firestarter.sdp_honesty` import, nothing else.** Every other symbol named in the plan's import-survival warning (`Confirm`, `FirmwareOutdatedError`, `EpromOperationError`, `sdp_capability`, `resolve_chip`, `ChipNotFoundError`) was individually grep-counted inside the deleted span (lines 2196-2304) versus outside it (lines 1-2195), and every one had at least one live use outside (e.g. `Confirm.ask` at `:1990`, `sdp_capability(` at `:626`, `resolve_chip(` at 13 other call sites). `emission_summary`/`map_unknown_cmd_to_outdated` (the two `sdp_honesty` imports) had zero uses outside the span, so that import line alone was removed.
- **Chose the node-scoped `--snapshot-update` route over the restore-and-hand-edit fallback**, because the first run already produced the exact expected diff shape (`git diff --stat` showing one deletion, zero insertions) — the plan's fallback route is only needed when the diff comes back wider than expected.
- **Did not edit `firestarter/sdp_honesty.py` or `tests/test_sdp_honesty.py` to satisfy Task 3's `grep -rn "dev sdp" --include='*.py'` acceptance criterion.** See Deviations below.

## Deviations from Plan

### Recorded discrepancy (not auto-fixed — see rationale)

**1. [Not a Rule 1-4 case — plan-measurement discrepancy, left as-is] Task 3's code-sweep acceptance criterion (`grep -rn "dev sdp" --include='*.py'` returns 0) does not hold; measured count is 5.**
- **Found during:** Task 3 (post-deletion sweep)
- **What the plan claimed:** the `<measured_anchors>` section states "The only in-tree references to the subcommand token were in the test module plan 132-03 rewrote and the registration decorator this plan deletes... zero markdown files... mention the command." The acceptance criterion for Task 3 then hard-codes `grep -rn "dev sdp" --include='*.py' | wc -l` returning 0.
- **What is actually there:** five hits, all inside docstrings in two files this plan does not own: `firestarter/sdp_honesty.py:3,17,35` and `tests/test_sdp_honesty.py:3,5`. Every hit is historical-provenance prose deliberately authored by plans 132-02 and 132-03 — e.g. `sdp_honesty.py`'s module docstring states "Phase 132 (RETIRE-03), D-01/D-02: `firestarter dev sdp` -- the only production..." and `test_sdp_honesty.py`'s docstring states "helper directly rather than driving `dev sdp` through Click's test harness." Both are accurate descriptions of the module's origin, not code that drives or references a live command.
- **Why not fixed:** Task 3's own `<files>` frontmatter tag is `none -- read-only sweep and measurement; findings go in this plan's SUMMARY`, and neither `sdp_honesty.py` nor `test_sdp_honesty.py` is in this plan's `files_modified:` list (`cli_handlers.py` and the `.ambr` file only). Editing either file's docstrings to strip a historical citation would be scope creep into files this plan is explicitly barred from touching, purely to satisfy a grep whose own premise (the "only in-tree references" claim) the plan-time measurement got wrong. Per this task's own action text, in-tree *markdown* prose is the category instructed to be fixed if found outward-facing-inappropriate; these are in-tree *code-file docstrings*, already reviewed and accepted by two prior plans as accurate history, not outward publication text and not incorrect.
- **Verification:** the five hits were individually read and confirmed to be prose-only, non-executable docstring citations with no `click`, `cli`, or subcommand-invocation code nearby.
- **Impact:** none on RETIRE-01's substance — the subcommand is deleted, the roster is eight, invocation fails. This is purely a documentation-citation discrepancy between the plan's own measured-anchors claim and reality, now recorded for whichever later phase (134/135/137) next touches these two files.

---

**Total deviations:** 1 recorded discrepancy (not an auto-fix under Rules 1-4 — no bug, no missing critical functionality, no blocker, no architectural change; a plan's own acceptance criterion measured against reality and found imprecise).
**Impact on plan:** None on RETIRE-01's delivery. The discrepancy is stated plainly per the phase's own honesty discipline rather than silently satisfied by editing out-of-scope files.

## Issues Encountered

None beyond the item documented above under Deviations from Plan.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `dev sdp` no longer exists; `dev`'s roster is exactly eight commands (`addr`, `consistency-check`, `fault-inject`, `read`, `reg`, `test`, `validate-family`, `write-cycle`), proven by positive enumeration and by a failing invocation.
- **D-05 residual, stated plainly:** no honesty caveat was added to the `write` auto-unlock path in this phase. Between this phase and Phase 134 (the wording's next intended caller, via `firestarter/sdp_honesty.py`), the caveat has **no user-reachable carrier at all** — the helper module exists, is type-checked, and is unit-tested (`tests/test_sdp_honesty.py`), but nothing in the CLI calls it. This is an inherited, deliberate gap (first stated by plan 132-02/03), not newly introduced here.
- **mypy count moved exactly as projected:** 69 → 63 (−6), matching `132-MYPY-LEDGER.md` §4's projection for plan 132-03's contribution. Plans 132-05 (typed fixture, −25 projected) and 132-06 (the six `[var-annotated]` fixes, −6 projected) remain to reach the 32 projected floor against the unchanged watermark of 35. This plan fixed **zero** mypy errors, per its own scope (deletion + snapshot only) — the 6-error movement is a side effect of plan 132-03's prior work, re-measured here, not new work in this plan.
- **`git diff --stat` for `eprom_operations.py`, `constants.py`, and `pyproject.toml` is empty across both commits** — the ring-fence and D-09's no-watermark-edit rule both held.
- **Coverage floor holds:** `pytest --cov=firestarter --cov-fail-under=70` passes at 81.72%, closing the one gap `ci_parity.sh`'s bare `pytest -q` legs cannot see (STATE.md's flagged risk for this exact deletion).
- Plan 132-05 (typed `AppContext` fixture) can proceed: `cli_handlers.py` no longer imports `sdp_honesty`, and `tests/test_sdp_honesty.py` no longer needs (and does not have) a local `make_app_context`.
- No blockers. RETIRE-01 is Complete; RETIRE-02/RETIRE-03 (132-03) remain Complete and un-touched; RETIRE-04 (132-08), RETIRE-05 (132-05), RETIRE-06 (132-09), RETIRE-07 (132-07), RETIRE-08 (132-08) remain untouched, as required.

---
*Phase: 132-retire-dev-sdp-discharge-the-mypy-debt*
*Completed: 2026-08-03*

## Self-Check: PASSED

Created/modified files verified present on disk:
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-04-SUMMARY.md` — FOUND
- `firestarter_app/firestarter/cli_handlers.py` — FOUND (dev_sdp span confirmed absent)
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — FOUND (sdp line confirmed absent)

Commits verified present in their owning repo's history:
- `259a0f0` (`firestarter_app` submodule) — FOUND
- `323c515` (`firestarter_app` submodule) — FOUND
- `99187d5` (meta-repo, this summary) — FOUND
