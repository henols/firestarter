---
phase: 186-the-python-floor-before-the-eol
plan: 01
subsystem: packaging
tags: [python, pyproject, mypy, ruff, tomllib, floor, eol]

requires: []
provides:
  - "All four Python-floor statements at agreement (3.11): requires-python, ruff target-version, mypy python_version, and the already-3.11 CI pins (read, not edited)"
  - "Trimmed classifier list (:: 3.11, :: 3.12, generic :: 3) with no unproven :: 3.13 claim"
  - "Runtime guard in firestarter/main.py raised to (3, 11) with its load-bearing noqa: UP036 intact"
  - "Five falsified py3.9-floor prose sites deleted across pyproject.toml and tests/test_py32_packaging.py"
  - "The falsified UP006 suppression at cli_handlers.py:1814 resolved at the site (dict[str, Any], no noqa)"
  - "The expected 182-finding ruff red (177 UP045, 2 UP017, 2 UP035, 1 I001) captured as plan 186-02's starting point"
affects: [186-02, 186-03, 186-04]

actuals:
  tokens: 1630
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Config-before-sweep ordering: land the floor/target-version bump before the mechanical pyupgrade sweep, because sweeping first would emit 3.11-only syntax (datetime.UTC) against a config still gated at 3.10, producing a false new-type-error signal on the watermark gate"
    - "Delete-not-rewrite for falsified prose: where a clause is falsified by a config change, remove only that clause if the rest still stands on its own; remove the whole coherent unit if it does not — never write a replacement sentence"

key-files:
  created: []
  modified:
    - firestarter_app/pyproject.toml
    - firestarter_app/firestarter/main.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_py32_packaging.py

key-decisions:
  - "Checkpoint (Task 0, D-01 one-way-door confirmation): operator selected proceed-as-locked — raise the floor to 3.11 across all four statements, with the C-5 correction (unpinned pip installs on 3.9/3.10 silently pin to the last compatible release rather than erroring) noted for plan 186-04's release-note wording, not acted on in code."
  - "Task 3 (orchestrator decision 3): resolved the falsified _load_validation_spec suppression at the site — dict[str, Any] and the noqa deleted entirely — rather than merely trimming the parenthetical, because D-11's claim that the pyupgrade sweep (186-02) would resolve it is measurably false (the rule is already active at the old target and the line survives the sweep verbatim)."
  - "Task 2 deliberately narrowed D-10's Site 2 line-range (only the UP: legend's parenthetical removed, not the whole line) and widened Site 4 (the whole 'Why a regex scan, not a TOML parse' docstring paragraph removed, not just the two lines D-10 named) — both recorded as deviations below with reasons, per the plan's own instruction."

requirements-completed: []

coverage:
  - id: D1
    description: "All four Python-floor statements (requires-python, ruff target-version, mypy python_version, CI pins) agree at 3.11"
    requirement: "FLOOR-01"
    verification:
      - kind: unit
        ref: "tomllib read of pyproject.toml + grep of .github/workflows/ — command in Task 1 <verify>"
        status: pass
    human_judgment: false
  - id: D2
    description: "The mypy watermark gate passes at 35/35 (181 files checked) on the Python 3.11 replica interpreter, not the devcontainer's 3.12"
    requirement: "FLOOR-01"
    verification:
      - kind: unit
        ref: "tools/check_mypy_watermark.py run under .venv/ci-replica/bin/python"
        status: pass
    human_judgment: false
  - id: D3
    description: "Runtime guard in main.py raised to (3, 11) with noqa: UP036 preserved so an autofix cannot delete the guard"
    requirement: "FLOOR-01"
    verification:
      - kind: unit
        ref: "grep -n 'sys.version_info' firestarter/main.py; python -m firestarter.main --version"
        status: pass
    human_judgment: false
  - id: D4
    description: "Five falsified py3.9-floor prose sites deleted (pyproject.toml x3, test_py32_packaging.py x2), nothing rewritten, no new word written"
    verification:
      - kind: unit
        ref: "grep counts in Task 2 <acceptance_criteria>; pytest tests/test_py32_packaging.py (7 passed)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Falsified UP006 suppression at cli_handlers.py:1814 resolved at the site, typing import stays live, mypy count unmoved"
    verification:
      - kind: unit
        ref: "grep + tools/check_mypy_watermark.py + pytest (31 passed) — Task 3 <verify>"
        status: pass
    human_judgment: false
  - id: D6
    description: "The one-way-door checkpoint (D-01) was surfaced to the operator with the C-5 correction and answered before any floor edit landed"
    verification: []
    human_judgment: true
    rationale: "A decision-gate confirmation is an operator judgment call by design — no automated check substitutes for it. Recorded here as evidence it was surfaced and answered, per the checkpoint_return_format and the resume instructions received."

duration: 25min
completed: 2026-09-12
status: complete
---

# Phase 186 Plan 01: The Python Floor Tracer Summary

**Raised the advertised Python floor from 3.9 to 3.11 across all four statements (metadata, lint target, type target, CI pin), deleted every falsified 3.9-floor claim rather than rewriting it, and resolved one falsified lint suppression at its site — all measured on the numpy-free Python 3.11 CI-replica interpreter, never the devcontainer's 3.12.**

## Performance

- **Duration:** ~25 min (across the checkpoint pause and this continuation)
- **Completed:** 2026-09-12
- **Tasks:** 3 code tasks executed (Task 0 was a checkpoint:decision, no code)
- **Files modified:** 4

## Accomplishments

- **Task 0 (checkpoint, answered):** The one-way-door confirmation for D-01 was surfaced to the operator with the C-5 correction in hand (an unpinned `pip install firestarter` on 3.9/3.10 silently pins to the last `>=3.9` release rather than erroring, contrary to D-12's assumption). The operator selected `proceed-as-locked`; no consumer notice or `CHANGELOG.md` was added (option 2 not selected).
- **Task 1 (tracer):** `requires-python`, `[tool.ruff] target-version`, and `[tool.mypy] python_version` all now read `3.11`/`py311`; the classifier list is trimmed to `:: 3.11` / `:: 3.12` / the generic `:: 3` entry with no `:: 3.13` minted; the three CI workflow pins were confirmed already `'3.11'` and left untouched; the runtime guard in `main.py` was raised to `(3, 11)` with its message and its load-bearing `# noqa: UP036` intact. The mypy watermark gate passes 35/35 across 181 checked files on the py3.11 replica. `ruff check` now reports the expected 182-finding red (177 UP045, 2 UP017, 2 UP035, 1 I001) — a lint backlog for plan 186-02, not a defect.
- **Task 2:** Five falsified py3.9-floor prose sites were deleted — three in `pyproject.toml` (the py32/pyusb comment's satisfiability clause, the `UP:` legend's parenthetical, and the whole 16-line `[tool.mypy]` rationale block) and two in `tests/test_py32_packaging.py` (the "Why a regex scan, not a TOML parse" docstring paragraph, and the `_EXPECTED_PYUSB_SPEC` comment's satisfiability clause). Nothing was rewritten; every surviving sentence stands on its own. The file's seven tests still pass and the formatter is still clean.
- **Task 3:** Resolved the falsified `# noqa: UP006 (python3.9 compat)` suppression at `cli_handlers.py:1814` at the site — `_load_validation_spec` now returns the builtin `dict[str, Any]` generic with no trailing directive — per orchestrator decision 3, since D-11's claim that the plan-186-02 sweep would resolve it is measurably false (the rule is already active at the old target).

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter_app` on branch `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`:

1. **Task 1: TRACER — the floor moves end to end** - `176c22d` (feat)
2. **Task 2: Delete every claim the floor raise falsified** - `bd25270` (docs)
3. **Task 3: Resolve the falsified suppression at cli_handlers.py:1814** - `2fd23ca` (fix)

**Plan metadata:** this SUMMARY.md, committed in the meta repo at `/workspaces` (separate commit, per repository_layout instructions).

**Note on repo layout:** all three code commits above live in `firestarter_app` (a separate git repository, submodule-tracked from the meta repo). The meta repo's gitlink for `firestarter_app` is deliberately NOT advanced by this plan — plan 186-04 owns that single bump, per this plan's dispatch instructions.

## Files Created/Modified

- `firestarter_app/pyproject.toml` - `requires-python`, `[tool.ruff] target-version`, `[tool.mypy] python_version` retargeted to 3.11; classifier list trimmed; three falsified prose sites deleted
- `firestarter_app/firestarter/main.py` - runtime guard's version tuple and message raised to 3.11, suppression preserved
- `firestarter_app/firestarter/cli_handlers.py` - `_load_validation_spec`'s return annotation modernised to `dict[str, Any]`, its `# noqa: UP006` directive removed
- `firestarter_app/tests/test_py32_packaging.py` - two falsified prose sites deleted; no assertion or constant changed (still 7 passed)

## Decisions Made

- **Checkpoint answered (D-01, one-way door):** `proceed-as-locked`, the operator's explicit choice with the C-5 correction (silent-pin behaviour on unpinned 3.9/3.10 installs, not a pip error) shown in full. C-5 is a wording correction to plan 186-04's release-note fragment, not a scope change here — nothing about it was written into any source file.
- **Task 3 fallback not needed:** the site-resolution (`dict[str, Any]`, suppression deleted) passed both the watermark gate (still 35/35) and the targeted 31-test run cleanly on the first attempt, so the plan's stated fallback (trim only the parenthetical, keep the bare `# noqa: UP006`) was not invoked.
- **Two deliberate narrowing/widening deviations from D-10's literal line ranges** — see Deviations below.

## Deviations from Plan

### Documented, non-code deviations (both explicitly anticipated and pre-authorized by the plan text itself)

**1. [Plan-authorized deviation] Site 2 (UP: legend) narrowed to the parenthetical only**
- **Found during:** Task 2
- **Issue:** D-10 named the whole `# UP: pyupgrade (modernise syntax within py39 bounds — UP007/UP045 no-ops on py39)` line as falsified.
- **Resolution:** Only the parenthetical was deleted; the bare `# UP: pyupgrade` label survives, matching the shape of the `E:`, `F:`, `I:` legend entries above it — deleting the whole line would leave `select` listing four rule families and the legend explaining three.
- **Files modified:** `firestarter_app/pyproject.toml`
- **Verification:** `grep -c '^# UP:' pyproject.toml` → `1`, no `(` on that line
- **Committed in:** `bd25270`

**2. [Plan-authorized deviation] Site 4 (regex-scan docstring paragraph) widened to the whole paragraph**
- **Found during:** Task 2
- **Issue:** D-10 named two lines inside the "Why a regex scan, not a TOML parse" paragraph.
- **Resolution:** The whole paragraph was deleted, not just the two named lines — its argument (tomllib unavailable at this project's floor) no longer follows from its premise once `tomllib` is stdlib at the new 3.11 floor, and excising two lines from the middle would leave a rewrite-by-omission the hard rule forbids.
- **Files modified:** `firestarter_app/tests/test_py32_packaging.py`
- **Verification:** `grep -c 'tomllib' tests/test_py32_packaging.py` → `0`; 7 tests still pass
- **Committed in:** `bd25270`

### Auto-fixed Issues

None — no Rule 1/2/3 auto-fixes were needed. Every deviation above was explicitly authorized by the plan's own text (D-10's narrowing/widening allowance) rather than discovered mid-execution.

### Acceptance-criterion authoring defect (recorded, not silently skipped)

Task 1's acceptance criteria included `grep -c 'Programming Language :: Python :: 3$' pyproject.toml` prints `1`. This literal command cannot pass on this file regardless of implementation: every classifier entry is a quoted, comma-terminated TOML array element (`"Programming Language :: Python :: 3",`), so no line ever ends in a bare `3` — it always ends in `3",`. This is a criterion-authoring artifact predating this plan's edits (the array's trailing-comma style was already in place), not an implementation gap. The intent — exactly one generic (non-version-specific) classifier line — is verified equivalently: `grep -c 'Programming Language :: Python :: 3\.' pyproject.toml` prints `2` (the two version-specific entries) and manual inspection of line 36 confirms the sole generic entry (`"Programming Language :: Python :: 3",`) is present and unique. No code change was made to chase the literal `3$` regex.

---

**Total deviations:** 2 plan-authorized (both explicitly named as allowed narrowing/widening in the plan text) + 1 acceptance-criterion authoring defect (verified via equivalent check, not silently skipped).
**Impact on plan:** None of these affected scope or correctness. All floor statements, the runtime guard, the falsified-prose deletions, and the site-level suppression resolution landed exactly as specified.

## Issues Encountered

None beyond the acceptance-criterion authoring defect noted above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The floor is proven at 3.11 end to end: metadata, lint target, type target, CI pin (read), and runtime guard all agree, measured on the py3.11 replica.
- `ruff check` is RED at exactly the predicted 182 findings (177 UP045, 2 UP017, 2 UP035, 1 I001) — this is plan 186-02's starting point, captured here rather than re-derived.
- `firestarter/py32_dfu.py`'s 14 pre-existing UP045 suppressions remain untouched, as this plan's scope excludes them (orchestrator ruling 4, carried in `186-CONTEXT.md`) — plan 186-04's note is expected to record this as the phase's named residual gap.
- FLOOR-01 and FLOOR-02 remain `Pending` in `.planning/REQUIREMENTS.md` — both are multi-plan requirements (FLOOR-01 spans 186-01/02/03; FLOOR-02 spans 186-01/03) and this is only the first contributing plan. No checkbox was flipped by this plan.
- Plan 186-04's release-note fragment should carry the corrected C-5 wording (silent-pin behaviour on unpinned 3.9/3.10 installs), surfaced at the Task 0 checkpoint and not acted on in code here.
- No blockers for 186-02 or 186-03.

---
*Phase: 186-the-python-floor-before-the-eol*
*Completed: 2026-09-12*

## Self-Check: PASSED

- `firestarter_app/pyproject.toml`, `firestarter_app/firestarter/main.py`, `firestarter_app/firestarter/cli_handlers.py`, `firestarter_app/tests/test_py32_packaging.py` all exist and carry the described changes.
- Commit `176c22d` (Task 1), `bd25270` (Task 2), `2fd23ca` (Task 3) all found in `firestarter_app`'s `git log --oneline --all`.
- Commit `4d7ab18b` (this SUMMARY, in the meta repo) found in `git log --oneline --all`.
- All plan-level `<acceptance_criteria>` re-verified passing except the one authoring-defect criterion documented above under "Acceptance-criterion authoring defect", which is verified via an equivalent check instead.
- Plan-level `<verification>` block re-run: tomllib prints `>=3.11 py311 3.11`; 3 CI workflow lines all `'3.11'`; watermark gate `checked 181 source files` / `mypy errors: 35 (watermark: 35)` / `OK: error count at watermark.`; `python -m firestarter.main --version` exits 0 and prints `Firestarter, version 3.0.0b38`; 31 targeted tests passed; `ruff format --check` reports `179 files already formatted`; `ruff check` RED at 182 findings (177 UP045, 2 UP017, 2 UP035, 1 I001) as expected; `git status --porcelain` in `firestarter_app` names only the two pre-existing untracked datasheet PDFs, no tracked file outside this plan's `files_modified` list.

## Correction (appended 2026-09-12, after `186-REVIEW.md` WR-01)

This plan's `<objective>` describes its output as "the runtime refusal inside the shipped wheel".
**That phrase is false as written.** `firestarter/main.py:20` re-exports `main = cli`, and
`pyproject.toml:88` declares the console script as `firestarter.main:main`, so the installed
`firestarter` command calls Click's `cli` directly and never enters the `if __name__ == "__main__":`
block at `main.py:29` where the guard lives. No pip-installed user is protected by it.

What this plan actually delivered is the narrower must-have it was held to, which remains true: the
guard's two halves were moved together and its load-bearing `# noqa: UP036` survived. The
unreachable-guard shape predates this phase; `186-VERIFICATION.md` ruled it falsifies no must-have
and no ROADMAP success criterion. It is carried forward as backlog **999.68**.

Recorded here rather than by editing the plan, per `/workspaces/CLAUDE.md` — rationale belongs in
the phase SUMMARY, and the plan is a historical record of what was asked, not of what was true.
