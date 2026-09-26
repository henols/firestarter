---
phase: 186-the-python-floor-before-the-eol
plan: 03
subsystem: packaging
tags: [python, tomllib, ruff, mypy, ci, floor-agreement, regression-gate]

requires:
  - phase: 186-02
    provides: "All four floor statements at 3.11, the py311 ruff sweep absorbed, mypy watermark unmoved at 35/35, CAP-03 parity gate repaired -- a clean tree for the agreement gate to assert over"
provides:
  - "tests/test_python_floor_agreement.py: a seven-leg, zero-comment, dependency-free fail-closed gate asserting requires-python, ruff target-version, mypy python_version and every CI python-version pin all normalise to the same value, with two planted-file fail-closed legs and a disagreement leg proven RED-then-GREEN by hand perturbation"
  - "firestarter_app/.planning/codebase/STACK.md corrected to the 3.11 floor at all three claim sites, with a pointer naming the meta repository and notes/python-floor-decision.md for an app-repo-only reader"
  - "CI-REPLICA: PASS measured on the genuine py3.11 CI-replica interpreter (not the devcontainer's 3.12), with the ci_replica_venv.sh INTERPRETER-DIVERGENCE stamp resolved by a PATH fix rather than --refresh"
  - "FLOOR-01 and FLOOR-02 marked Complete in .planning/REQUIREMENTS.md; FLOOR-03 left Pending for 186-04"
affects: [186-04]

actuals:
  tokens: 4100
  raw_tokens: 4100
  tasks: 3
  commits: 2
  plan_head_before: "7f53886a1c9dfe57ee6cf3e30bc3d7b3f2e0d5b6"

tech-stack:
  added: []
  patterns:
    - "One shared helper called by both the real assertion leg and its planted-file fail-closed counterpart (_parsed_pyproject, _workflow_python_versions, _assert_floor_statements_agree) -- the fail-closed leg exercises the exact same code path the real leg relies on, not a parallel implementation written to fail"
    - "A gate's own docstring must not literally spell the forbidden dependency names it argues against (pyyaml, tomli) when the acceptance criteria greps the file for those exact substrings -- describe the alternative generically (a third-party TOML/YAML-parsing package) instead of naming the package"
    - "A disagreement-planted leg should read through the SAME aggregation the real leg uses (here _floor_statements(), which merges a monkeypatched pyproject with the real, untouched workflow directory) rather than a narrower helper, so the diagnostic message it proves also covers every source category, not just the ones deliberately mismatched"
    - "ci_replica_venv.sh's INTERPRETER stamp is computed by resolve_base_python() on every invocation regardless of --refresh, purely from PATH -- reusing an existing 3.11 venv does not by itself suppress an INTERPRETER-DIVERGENCE stamp if python3.11 is not resolvable on PATH; prepend the uv-managed interpreter's bin dir instead of passing --refresh"

key-files:
  created:
    - firestarter_app/tests/test_python_floor_agreement.py
  modified:
    - firestarter_app/.planning/codebase/STACK.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Reworded the module docstring to avoid the literal substrings 'tomli' and 'yaml' -- the plan's own acceptance criteria greps the file for exactly those and requires a zero count, which the first draft (naming both packages explicitly, following the analog's phrasing) failed. Rationale is preserved generically ('a third-party TOML-parsing package', 'a third-party YAML-parsing package') without naming the forbidden packages by their exact spelling."
  - "Factored _assert_floor_statements_agree(statements) as a shared helper called by both the real agreement leg and the disagreement-planted leg, and changed the disagreement leg to read through _floor_statements() (merging the planted, mismatched pyproject with the REAL, untouched workflow directory) rather than _parsed_pyproject() alone. The original draft's disagreement leg duplicated the assertion body inline and only ever produced three source labels (the pyproject-side ones); the fix makes it call the identical code the real leg calls and report every source in play, genuinely proving the report is diagnostic across all statement kinds, not just the three that were deliberately mismatched."
  - "Fixed ci_replica_venv.sh's INTERPRETER-DIVERGENCE stamp by prepending /home/vscode/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin to PATH before invoking the script, WITHOUT --refresh. resolve_base_python() stamps INTERPRETER unconditionally on every run (even when the existing venv is reused, not rebuilt), and this container's ambient PATH resolves python3.11 to neither of the two probed locations, falling through to bare python3 (3.12.14). The first invocation (killed mid-run once this was noticed) would have produced a CI-REPLICA: PASS output carrying INTERPRETER-DIVERGENCE, which the plan's own acceptance criteria explicitly says does not satisfy success criterion 2 regardless of the verdict line."
  - "FLOOR-01 and FLOOR-02 marked Complete in .planning/REQUIREMENTS.md by hand-edit (not the requirements.mark-complete verb, to avoid the known whole-file reformat) -- this is their last contributing plan (186-01/186-02/186-03) and both are genuinely satisfied: all four statements move together, and a fail-closed gate now asserts it. FLOOR-03 stays Pending; 186-04 creates notes/python-floor-decision.md, which FLOOR-03's own text requires."
  - "The residual-claim scan (Task 3) found 5 tracked-file hits for the old floor, not the predicted 2. All three extras are dispositioned, not fixed: pyproject.toml:63 and tests/test_py32_packaging.py:71 quote pyusb 1.3.1's OWN PyPI Requires-Python (>=3.9.0) as justification for the [py32] extra's version pin -- a fact about a third-party package, not a claim about this project's floor, and both survived 186-01's D-10 deletion pass correctly (the falsifying clause 'satisfiable on this project's py39 floor' was already removed, leaving only the true pyusb fact). tests/test_python_floor_agreement.py itself contributes 3 lines, all mandated literally by the plan's own <behavior> spec (py39 -> 3.9 normalisation test cases, and the disagreement leg's deliberately-mismatched planted fixture) -- test data proving the gate handles the old spelling, not a claim about the project's own floor."

requirements-completed: [FLOOR-01, FLOOR-02]

coverage:
  - id: D1
    description: "The four-way floor agreement gate (seven legs, zero comments, no new dependency) is installed and green"
    requirement: "FLOOR-01"
    verification:
      - kind: unit
        ref: "tests/test_python_floor_agreement.py -o addopts=\"\" -q -- Task 1 <verify>, 7 passed"
        status: pass
      - kind: unit
        ref: "grep -c '^[[:space:]]*#' tests/test_python_floor_agreement.py -- 0; grep -c 'yaml|tomli\\b|import toml$' -- 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "The two planted-file fail-closed legs and the disagreement leg were each observed genuinely RED (via a deliberate, then-reverted weakening of the guard they exercise) before being observed GREEN again"
    requirement: "FLOOR-01"
    verification: []
    human_judgment: true
    rationale: "The RED state was produced by temporarily weakening each guard in place and re-running the single affected test, then immediately reverting; it is not a persisted, re-runnable regression check (the point was to prove the guard CAN fail, not to keep it failing). A human should read the three captured RED transcripts in this SUMMARY's Deviations/Evidence section to judge that the perturbation genuinely exercised the guard being tested, rather than re-running the (now green) suite."
  - id: D3
    description: "firestarter_app/.planning/codebase/STACK.md's three floor claims all name 3.11, the quoted specifier matches pyproject.toml, and one line points an app-repo-only reader at the meta repo's rationale note"
    requirement: "FLOOR-03"
    verification:
      - kind: unit
        ref: "grep -c '3\\.9' STACK.md -- 0; grep -c '3\\.11' STACK.md -- 3; grep -n 'python-floor-decision.md' STACK.md -- present with firestarter_prom -- Task 2 <verify>"
        status: pass
    human_judgment: false
  - id: D4
    description: "The whole phase's app-repo change is proven at the floor: CI-REPLICA: PASS, INTERPRETER names a genuine 3.11 with no divergence stamp, all five legs exit 0, coverage floor met (84.76%), 2366 passed"
    requirement: "FLOOR-02"
    verification:
      - kind: unit
        ref: "bash tools/ci_replica_venv.sh (PATH-prepended, no --refresh) -- Task 3 <verify>, CI-REPLICA: PASS"
        status: pass
    human_judgment: false
  - id: D5
    description: "The tracked-file residual scan for the old floor (3.9 / py39 / python3.9 / (3, 9)) returns 5 hits, not the predicted 2 -- all 3 extras dispositioned as legitimate non-claims rather than a floor surface the phase missed"
    requirement: "FLOOR-02"
    verification: []
    human_judgment: true
    rationale: "Whether pyproject.toml:63, test_py32_packaging.py:71 (both quoting pyusb's own third-party Requires-Python) and this plan's own new test fixtures (mandated literally by the plan's <behavior> spec) are legitimate non-claims, rather than a floor surface the phase missed, is a judgment call recorded in the key-decisions above for verifier review -- not something a grep count alone can settle."

duration: 34min
completed: 2026-09-12
status: complete
---

# Phase 186 Plan 03: The Four-Way Floor Agreement Gate, the App-Repo Stack Record, and the Py3.11 Proof Summary

**Installed a seven-leg, zero-comment `tests/test_python_floor_agreement.py` that fail-closes on any future drift among `requires-python`, ruff's `target-version`, mypy's `python_version` and every CI `python-version:` pin; corrected the app repo's own `STACK.md` to 3.11 with a pointer to the rationale note 186-04 will write; and proved the whole phase at the floor with `CI-REPLICA: PASS` on a genuine py3.11 interpreter, catching and fixing an `INTERPRETER-DIVERGENCE` stamp along the way.**

## Performance

- **Duration:** 34 min
- **Completed:** 2026-09-12
- **Tasks:** 3
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- **Task 1 (the gate):** Wrote `tests/test_python_floor_agreement.py` — module globals `_APP_ROOT` (resolved, never cwd-relative), `_PYPROJECT`, `_WORKFLOWS_DIR`, `_WORKFLOW_PIN_FLOOR = 3`; helpers `_parsed_pyproject()` (fail-closed `tomllib` read of the three pyproject-side statements), `_workflow_python_versions()` (fail-closed, sorted glob + line-regex extraction of every CI pin, non-vacuous at `>= 3`), `_normalise_ruff_target()` (variable-width minor: `py311` -> `3.11`, never a fixed two-character split), `_normalise_requires_python()` (bare-lower-bound shape only, raises on a comma range, a compatible-release operator, or a bare version), `_floor_statements()` (merges all sources by human-readable name), and `_assert_floor_statements_agree()` (the one helper both the real leg and the disagreement-planted leg call). Seven legs, all passing: the real four-way equality assertion, the ruff-minor unit test, the requires-python-shape unit test, the workflow-inventory non-vacuity leg, two planted-file fail-closed legs, and the disagreement leg. Zero `#` comments; no `pyyaml`/`tomli`/`toml` import; no `from __future__`/`Optional`/`typing.Dict`; `ruff check` and `ruff format --check` both green with the new file inside scope (`180 files already formatted`, one more than 186-02's 179); mypy watermark unmoved at `35 (watermark: 35)`, `checked 182 source files`.
- **Task 2 (the app-repo stack record):** All three floor claims in `firestarter_app/.planning/codebase/STACK.md` (`:7`, `:12`, `:57`) now name 3.11; the `:7` claim's quoted specifier (`requires-python = ">=3.11"`) matches `pyproject.toml` verbatim and carries a new pointer naming `henols/firestarter_prom` and `.planning/notes/python-floor-decision.md` for a reader with only the app repo checked out. The `:12` dev-machine-runtime figure (`Python 3.13.5`) was left untouched per plan instruction and is recorded below as a separate, out-of-scope observation — it is in fact stale (this devcontainer measures `3.12.14`).
- **Task 3 (the proof):** No file was edited. `bash tools/ci_replica_venv.sh` (PATH-prepended with the uv-managed `python3.11` bin dir, never `--refresh`) produced `CI-REPLICA: PASS` with `INTERPRETER: .../python3.11 Python 3.11.16` and no `INTERPRETER-DIVERGENCE:` line, all five legs `exit 0`, `Required test coverage of 70% reached. Total coverage: 84.76%`, `2366 passed, 1 warning in 384.57s` (up from 186-02's 2359 — the new gate's own 7 tests). The residual-claim scan over tracked files (excluding golden/data/datasheet/image trees) returned 5 hits, not the predicted 2 — see Deviations below. `git status --porcelain` confirmed no tracked file was modified by the act of measuring.

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter_app` on branch `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`:

1. **Task 1: The four-way floor agreement gate** - `b1d9d85` (test)
2. **Task 2: Correct the app repo's own stack record** - `612aa69` (docs)
3. **Task 3: Prove the phase at the floor** - no commit (measurement only, no file changed)

**Plan metadata:** this SUMMARY.md, `.planning/STATE.md` and `.planning/REQUIREMENTS.md`, committed in the meta repo at `/workspaces` (separate commit, per repository_layout instructions). The meta repo's gitlink for `firestarter_app` is deliberately NOT advanced by this plan — plan 186-04 owns that bump.

## Files Created/Modified

- `firestarter_app/tests/test_python_floor_agreement.py` - the seven-leg four-way agreement gate (new)
- `firestarter_app/.planning/codebase/STACK.md` - three floor claims corrected to 3.11, one pointer to the rationale note added
- `.planning/REQUIREMENTS.md` - FLOOR-01 and FLOOR-02 marked Complete (checkbox + traceability row); FLOOR-03 left Pending

## Decisions Made

See `key-decisions` in the frontmatter for full detail. In brief: reworded the gate's docstring away from the literal substrings the acceptance criteria forbid; factored a shared `_assert_floor_statements_agree` helper and widened the disagreement leg to read through `_floor_statements()` so it genuinely proves the report is diagnostic across all four statement kinds, not just the mismatched three; fixed the `ci_replica_venv.sh` `INTERPRETER-DIVERGENCE` stamp via a PATH prepend rather than `--refresh`; marked FLOOR-01/FLOOR-02 Complete (last contributing plan for both) while leaving FLOOR-03 Pending for 186-04; and dispositioned the residual scan's 3 extra hits as legitimate non-claims rather than fixing them.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The gate's initial docstring literally contained the forbidden substrings 'tomli' and 'yaml'**
- **Found during:** Task 1, first acceptance-criteria pass
- **Issue:** The module docstring's rationale paragraph named `toml`/`tomli` and `pyyaml` explicitly (following the primary analog's phrasing), which the task's own acceptance criteria greps for and requires a zero count. `grep -c 'yaml\|tomli\b\|import toml$'` printed `1`.
- **Fix:** Reworded the paragraph to describe the alternatives generically ("a third-party TOML-parsing package", "a third-party YAML-parsing package") without naming the forbidden packages by their exact spelling. Re-verified: count `0`.
- **Files modified:** `firestarter_app/tests/test_python_floor_agreement.py`
- **Verification:** `grep -c 'yaml\|tomli\b\|import toml$' tests/test_python_floor_agreement.py` → `0`; `pytest` still `7 passed`.
- **Committed in:** `b1d9d85` (Task 1 commit; fixed before commit, not a follow-up)

**2. [Rule 1 - Bug] `ruff format --check` initially failed on the new file (one line needed re-wrapping)**
- **Found during:** Task 1, acceptance-criteria pass
- **Issue:** The disagreement message's `"\n".join(...)` line exceeded the formatter's preferred wrap width.
- **Fix:** Ran `ruff format tests/test_python_floor_agreement.py`; re-verified `ruff format --check firestarter/ tests/` → `180 files already formatted`.
- **Files modified:** `firestarter_app/tests/test_python_floor_agreement.py`
- **Verification:** `ruff format --check` green; `pytest` still `7 passed`; `ruff check` still `All checks passed!`.
- **Committed in:** `b1d9d85` (fixed before commit)

**3. [Rule 1 - Bug] The disagreement-planted leg only produced three source labels, not "all four", and duplicated the real leg's assertion body inline**
- **Found during:** Task 1, re-reading the plan's own `<behavior>` spec against the initial draft
- **Issue:** `test_a_disagreeing_planted_pyproject_names_all_four_values` called `_parsed_pyproject()` directly, which returns only the three pyproject-side statements — its own docstring claim ("names all four source labels") was not actually true of the code, and the assertion body (`assert len(values) == 1, "..."`) was copy-pasted rather than shared with the real leg, breaking the plan's explicit "ONE HELPER RULE".
- **Fix:** Factored `_assert_floor_statements_agree(statements)` as a shared helper; changed both the real leg and the disagreement leg to call it; changed the disagreement leg to build its `statements` via `_floor_statements()` (which merges the planted, mismatched pyproject with the REAL, untouched workflow directory) instead of `_parsed_pyproject()` alone, so the report now genuinely includes every source category.
- **Files modified:** `firestarter_app/tests/test_python_floor_agreement.py`
- **Verification:** `pytest tests/test_python_floor_agreement.py -o addopts="" -q` → `7 passed`; RED-then-GREEN perturbation re-run for this leg specifically (see Evidence below).
- **Committed in:** `b1d9d85` (fixed before commit)

**4. [Rule 1 - Bug] `ci_replica_venv.sh`'s first run carried an `INTERPRETER-DIVERGENCE` stamp**
- **Found during:** Task 3, first invocation
- **Issue:** `resolve_base_python()` prints `INTERPRETER: /usr/local/bin/python3 Python 3.12.14` plus `INTERPRETER-DIVERGENCE: using 3.12.14, CI uses 3.11` on every invocation (regardless of `--refresh`) whenever `python3.11` is not resolvable on `PATH` — measured true in this container even though the existing `.venv/ci-replica` venv itself is genuinely 3.11.16. The plan's own acceptance criteria says a 3.12 measurement does not satisfy success criterion 2 "regardless of the verdict line", so the first (killed) run's output could not be used as evidence even though its actual gate legs (which run via `${VENV_DIR}/bin/...`) were correct.
- **Fix:** Killed the in-flight run before it completed (no file was touched by it), then re-ran with `PATH="/home/vscode/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin:$PATH"` prepended and still no `--refresh` — `resolve_base_python()` then finds `python3.11` on `PATH` directly, matching the venv's own interpreter, and stamps `INTERPRETER: .../python3.11 Python 3.11.16` with no divergence line. `RESEARCH.md` §7 P-1 names this exact PATH-prepend workaround; it was not needed by 186-01/186-02 because they did not invoke this script.
- **Files modified:** none (no source file touched; a measurement-environment fix only)
- **Verification:** the corrected run's log: `INTERPRETER: /home/vscode/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11 Python 3.11.16` (no divergence line), ending `CI-REPLICA: PASS`.
- **Committed in:** n/a (no commit; environment-only)

---

**Total deviations:** 4 auto-fixed (3 Rule 1 bugs in the new test file, caught by its own acceptance criteria before commit; 1 Rule 1 bug in the measurement environment, caught before trusting the result).
**Impact on plan:** All four were caught and fixed within Task 1/Task 3's own verification loop, before any commit or before the evidence was trusted. No scope creep; the fixes make the gate and the measurement match what the plan actually specified.

## Fail-Closed Evidence (Task 1 acceptance criterion: each guard observed RED before GREEN)

**Leg 1 — `test_gate_fails_closed_on_a_planted_pyproject_with_no_floor_statements`.** Weakened `_parsed_pyproject()` to use `.get(...)` defaults instead of raising `AssertionError` on a missing key, then ran only this test:

```
FAILED tests/test_python_floor_agreement.py::test_gate_fails_closed_on_a_planted_pyproject_with_no_floor_statements
E       Failed: DID NOT RAISE AssertionError
```

Restored the `try`/`except`/`raise AssertionError` blocks; re-ran the full file: `7 passed`.

**Leg 2 — `test_gate_fails_closed_on_an_empty_planted_workflows_dir`.** Weakened the count-floor assertion in `_workflow_python_versions()` from `assert len(pins) >= _WORKFLOW_PIN_FLOOR` to `assert len(pins) >= 0`, then ran only this test:

```
FAILED tests/test_python_floor_agreement.py::test_gate_fails_closed_on_an_empty_planted_workflows_dir
E       Failed: DID NOT RAISE AssertionError
```

Restored `_WORKFLOW_PIN_FLOOR`; re-ran the full file: `7 passed`.

**Leg 3 — `test_a_disagreeing_planted_pyproject_names_all_four_values`.** Weakened `_assert_floor_statements_agree` from `assert len(values) == 1, (...)` to `assert len(values) == 1 or True, (...)` (never raises), then ran only this test:

```
FAILED tests/test_python_floor_agreement.py::test_a_disagreeing_planted_pyproject_names_all_four_values
E       Failed: DID NOT RAISE AssertionError
```

Restored the assertion; re-ran the full file: `7 passed`. `git status --porcelain` confirmed no diff to `pyproject.toml` or `.github/` at any point during these three probes — every perturbation was applied to, and reverted in, only the new test file itself.

## Residual-Claim Scan Disposition (Task 3)

The tracked-file scan for `3\.9|py39|python3\.9|\(3, 9\)` (excluding `tests/golden/`, `firestarter/data/`, `datasheets/`, `images/`) returned **5** hits, not the predicted 2:

| File | What matched | Disposition |
|---|---|---|
| `tools/check_mypy_watermark.py` | mypy's own `"...python_version: 3.9 is not supported..."` output, quoted as an example in a comment | **Expected** (D-11: leave unchanged — a fixture of mypy's own message, not a claim about this project) |
| `tests/test_check_mypy_watermark.py` | the same mypy message, held as fixture text in `CONFIG_REJECTION_OUTPUT` | **Expected** (same reasoning) |
| `pyproject.toml:63` | `# time, Requires-Python >=3.9.0.` — pyusb 1.3.1's OWN PyPI-declared floor, quoted as justification for the `[py32]` extra's version pin | **Legitimate, not a miss.** Describes a third-party package's metadata, not this project's floor. 186-01's D-10 deletion pass correctly removed only the falsifying clause ("satisfiable on this project's py39 floor") that used to follow it, leaving this true fact intact. |
| `tests/test_py32_packaging.py:71` | `# >=3.9.0); <2 refuses a future major...` — the same pyusb fact, quoted in `_EXPECTED_PYUSB_SPEC`'s justifying comment | **Legitimate, not a miss.** Same reasoning as above. |
| `tests/test_python_floor_agreement.py` (3 lines: `:50`, `:204`, `:207` pre-format, and the disagreement leg's planted `"3.9"` literal) | This plan's own new gate's `_normalise_ruff_target` docstring/unit-test literals (`py39` → `3.9`) and the disagreement leg's deliberately-mismatched planted fixture | **Legitimate, not a miss.** Every one of these is mandated literally by the plan's own `<behavior>` spec (`test_ruff_target_minor_is_not_fixed_width` must assert `_normalise_ruff_target("py39") == "3.9"`; the disagreement leg must plant a mismatched `python_version = "3.9"`). Test data proving the gate correctly HANDLES the old spelling, not a claim about this project's own floor. |

No third **surface the phase missed** was found; all three extras beyond the two expected mypy-fixture hits are dispositioned above, per the acceptance criterion's instruction to disposition rather than wave through.

## Issues Encountered

- The `ci_replica_venv.sh` `INTERPRETER-DIVERGENCE` stamp (see Deviations #4) — resolved before trusting any result, not a blocker.
- The dev-machine runtime figure at `STACK.md:12` (`Python 3.13.5`) does not match this devcontainer's actual `python3` (`3.12.14`, confirmed via `python3 --version`). Left unedited per plan instruction (out of scope for this task — only the minimum-supported figure was this phase's to change); recorded here as an observation for whoever next touches that file.
- None of the above blocked any task; both are resolved-before-trust or explicitly deferred.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- FLOOR-01 and FLOOR-02 are Complete in `.planning/REQUIREMENTS.md`. FLOOR-03 remains Pending — plan 186-04 must create `.planning/notes/python-floor-decision.md` (meta repo) and correct the three meta-repo records (`STACK.md`, `STRUCTURE.md`, `CONVENTIONS.md`) that still state the old floor, per `186-PATTERNS.md`'s edited-files table.
- The new gate (`firestarter_app/tests/test_python_floor_agreement.py`) now runs on every `pytest tests/` invocation and inside `ruff check`/`ruff format --check`/the mypy watermark scope — any future drift among the four floor statements will fail closed, by name, without a human having to notice a prose claim went stale.
- `firestarter_app` is at `612aa69` on `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`; the meta repo's gitlink for `firestarter_app` is deliberately NOT advanced — 186-04 owns that bump.
- No blockers for 186-04.

---
*Phase: 186-the-python-floor-before-the-eol*
*Completed: 2026-09-12*

## Self-Check: PASSED

- `firestarter_app/tests/test_python_floor_agreement.py` exists (287 lines) and matches the described seven-leg, zero-comment shape.
- `firestarter_app/.planning/codebase/STACK.md` carries `3.11` at all three claim sites, `requires-python = ">=3.11"` quoted verbatim, and the `python-floor-decision.md` / `firestarter_prom` pointer.
- Commits `b1d9d85` (Task 1) and `612aa69` (Task 2) both found in `firestarter_app`'s `git log --oneline --all`.
- All plan-level `<acceptance_criteria>` re-verified passing: `pytest tests/test_python_floor_agreement.py -o addopts="" -q` → `7 passed`; comment count `0`; `tomllib` import present; `yaml|tomli\b|import toml$` count `0`; `from __future__|Optional|typing.Dict` count `0`; `_WORKFLOW_PIN_FLOOR = 3` at module scope; `sorted(` present on the workflow glob; one `Path(__file__).resolve().parent.parent` anchor; `ruff check` → `All checks passed!`; `ruff format --check` → `180 files already formatted`; mypy watermark → `mypy errors: 35 (watermark: 35)`, `OK: error count at watermark.`, `checked 182 source files`; `pyyaml|tomli` count in `pyproject.toml` → `0`.
- Plan-level `<verification>` block re-run: `bash tools/ci_replica_venv.sh` (PATH-corrected) → `CI-REPLICA: PASS`, `INTERPRETER: .../python3.11 Python 3.11.16`, no divergence line, all 5 legs exit 0, `Required test coverage of 70% reached. Total coverage: 84.76%`, `2366 passed, 1 warning in 384.57s`.
- `git status --porcelain` in `firestarter_app` names only the two pre-existing untracked datasheet PDFs; no tracked file outside this plan's `files_modified` list, and no diff to `pyproject.toml` or `.github/` at any point.
- `.planning/REQUIREMENTS.md` diff confirmed scoped to FLOOR-01/FLOOR-02 (checkbox + traceability row); FLOOR-03 unchanged.
- `.planning/STATE.md` diff confirmed internally consistent after hand-repair of the `state.*` verb's frontmatter-zeroing bug (progress.completed_phases/percent/completed_plans, repeated across four separate `state.*` invocations) — final diff shows `completed_phases: 4`, `completed_plans: 27`, `percent: 67` unchanged from pre-plan values except the deliberate plan-count increment, `stopped_at`/`last_activity_desc`/`Current Position` all naming 186-03, three new decision bullets, one new metrics-table row, and a consistent `## Session` block.
