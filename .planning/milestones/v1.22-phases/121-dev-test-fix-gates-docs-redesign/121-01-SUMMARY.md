---
phase: 121-dev-test-fix-gates-docs-redesign
plan: 01
subsystem: testing
tags: [ruff, pytest, audit-coverage-matrix, golden-file, ci-parity]

# Dependency graph
requires: []
provides:
  - "[tool.ruff] extend-exclude = [\"tests/golden\", \"tests/fixtures\"] in firestarter_app/pyproject.toml, closing the ruff-version/golden collision before any formatter runs in Phase 121"
  - "Regenerated tests/golden/v1.3-COVERAGE-MATRIX.md — test_golden_file_matches now GREEN"
  - "A CI-parity Python 3.11 venv at /tmp/venv311 (ruff 0.16.0) for later Phase 121 plans to reuse when reporting ruff verdicts"
  - "Full firestarter_app host suite proven at 1052 passed / 0 failed, zero DEVTEST code in the tree at this commit"
affects: [121-02, 121-03, 121-04, 121-05, 121-06, 121-07, 121-08, 121-09, 121-10, 121-11, 121-12, 121-13, 121-14]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "ruff extend-exclude for byte-asserted golden fixtures that also happen to contain fenced Python code blocks a formatter would rewrite"
    - "Regenerating a byte-identity golden via a scratch COPY of its input ledger, never the live committed ledger, because generate_matrix unconditionally save_ledger()s back to whatever ledger_path it's given (auto-registers new fingerprints)"

key-files:
  created: []
  modified:
    - firestarter_app/pyproject.toml
    - firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md

key-decisions:
  - "D-18 regen commit contains zero DEVTEST-shaped file changes (chip_test.py/cli_handlers.py/database.py/diagnostic_report.py/submit.py all confirmed clean via git status --porcelain before commit), so any later Phase 121 matrix delta is attributable in isolation to Phase 121 work"
  - "Regeneration used a scratch COPY of the committed meta ledger (.planning/v1.3-defect-coverage-ids.json), not the live file directly — generate_matrix's save_ledger() call mutates whatever ledger_path it receives (it auto-registers newly-discovered defect fingerprints), so passing the live path would have silently rewritten the meta repo's committed ledger. Two independent scratch-copy runs produced byte-identical (cmp) output, proving determinism without ever touching the real ledger (git status --porcelain on it stayed empty throughout)"
  - "Did not pin ruff==0.15.* — kept the unbound ruff>=0.15.14 floor and closed the collision via extend-exclude instead, per RESEARCH's rejection of freezing lint hygiene project-wide for one markdown file"

requirements-completed: []  # GATE-03 is contributed-to-only in this plan; closed later by 121-14 per requirement_ownership lock. Nothing marked Complete in REQUIREMENTS.md (untouched).

coverage:
  - id: D1
    description: "ruff extend-exclude closes the CI-resolved-ruff-vs-byte-asserted-golden collision before any formatter run in the phase"
    verification:
      - kind: unit
        ref: "/tmp/venv311/bin/ruff format --check firestarter/ tests/ (exit 0, CI-parity ruff 0.16.0)"
        status: pass
      - kind: unit
        ref: "ruff format --check firestarter/ tests/ (exit 0, devcontainer ruff 0.15.20)"
        status: pass
      - kind: unit
        ref: "/tmp/venv311/bin/ruff check firestarter/ tests/ (exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Stale audit-coverage-matrix golden regenerated; test_golden_file_matches flips RED to GREEN with zero DEVTEST code in the tree"
    requirement: "GATE-03"
    verification:
      - kind: unit
        ref: "tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches"
        status: pass
      - kind: unit
        ref: "tests/ -p no:cacheprovider -q (1052 passed, 0 failed)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 01: D-18 Golden Regen + Ruff/Golden Collision Fix Summary

**Regenerated the stale, pre-existing-RED `v1.3-COVERAGE-MATRIX.md` golden (DIP32 pinout-split drift from Phase 98's `362bfa0`) in a DEVTEST-free commit, and closed the ruff-0.16-vs-byte-asserted-golden collision via `extend-exclude` before any formatter runs in this phase.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-29T16:14:55Z (approx, from STATE.md session start)
- **Completed:** 2026-07-29T16:34:51Z
- **Tasks:** 2 completed
- **Files modified:** 2

## Accomplishments
- `firestarter_app/pyproject.toml`: added `[tool.ruff] extend-exclude = ["tests/golden", "tests/fixtures"]`, reproducing then closing the collision where CI-resolved ruff 0.16.0 wants to reformat an embedded Python block inside the byte-asserted golden markdown file (devcontainer ruff 0.15.20 does not reproduce the collision).
- Verified/reused a CI-parity Python 3.11.15 venv at `/tmp/venv311` with `ruff 0.16.0` installed editable (`-e '.[test]'`) — already provisioned from a prior session, confirmed correct and reusable by later Phase 121 plans.
- Regenerated `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md`, flipping `test_golden_file_matches` from RED (produced 186034 bytes vs golden 184631 bytes, first divergence at index 1178) to GREEN.
- Root-caused and documented the drift: Phase 98's `362bfa0` (`feat(98-01)`) reassigned 88 chips (`proto_id==0x08 && mem_size<=262144`) from pinout `DIP32_STD` to `DIP32_27C020`; the coverage-matrix golden was never regenerated after that DB change. This is pre-existing DB drift, unrelated to Phase 121/DEVTEST work — `audit_coverage_matrix.py` has no `dev test` op vocabulary at all (confirmed by grep, matching RESEARCH C-2).
- Proved the full `firestarter_app` host suite green at this commit: **1052 passed, 0 failed** (exit code 0; verified via dot-count in `-q` output since this environment's pytest run does not print the standard final summary line — see Issues Encountered).

## Task Commits

Each task was committed atomically in `firestarter_app`:

1. **Task 1: Add the ruff exclusion that protects the byte-asserted golden and the planted-violation fixtures** - `2fa2e5a` (fix)
2. **Task 2: Regenerate the stale audit-matrix golden, alone, and prove the host suite green at that commit** - `098702c` (fix)

No separate plan-metadata commit was made in `firestarter_app` (per repo topology, code commits land directly in the submodule; this SUMMARY is the meta-repo commit).

## Files Created/Modified
- `firestarter_app/pyproject.toml` - added `[tool.ruff] extend-exclude` covering `tests/golden` and `tests/fixtures`, with a two-reason comment (byte-identity vs formatter collision; fixture-input-not-source rationale)
- `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` - regenerated via `generate_matrix()` against a scratch copy of the committed meta ledger; 275 insertions / 273 deletions, reflecting the `DIP32_STD` → `DIP32_27C020` pinout split for 88 chips plus 18 newly-registered `DEFECT-COV-78..95` entries the generator's auto-registration surfaced for that reclassified cluster

## Decisions Made
- **Ledger-copy regeneration, not live-ledger regeneration.** The plan's action text named the committed meta ledger path directly as `ledger_path`, but `generate_matrix()`'s `save_ledger(ledger, ledger_path)` call unconditionally writes back to whatever path it's given — it auto-registers newly-discovered defect fingerprints into the ledger. Pointing it directly at `/workspaces/.planning/v1.3-defect-coverage-ids.json` (tried first, then reverted via `git checkout --`) would have silently added 18 new `DEFECT-COV-78..95` entries to the meta repo's committed ledger, which this plan is explicitly forbidden from touching ("The meta repo is read-only here"). Followed the same pattern `test_golden_file_matches` itself uses (seed a tmp copy, run against the copy) instead: copied the real ledger to two independent scratch paths, ran `generate_matrix` against each copy separately, `cmp`'d the two outputs (byte-identical, proving determinism), and confirmed via `git -C /workspaces status --porcelain .planning/v1.3-defect-coverage-ids.json` that the real committed ledger stayed byte-unchanged throughout. This satisfies both the plan's literal acceptance criterion ("the generator did not mutate its own input") and its underlying intent (byte-identical input pair to the test).
- Did not pin the `ruff` dependency floor — closed the collision at the config level (`extend-exclude`) rather than at the dependency-version level, per RESEARCH's explicit rejection of pinning `ruff==0.15.*` for one markdown file.
- Never ran a bare `ruff format` (without `--check`) at any point, per the plan's hard constraint.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Regeneration input corrected from live ledger to scratch-copied ledger**
- **Found during:** Task 2
- **Issue:** The plan's literal action text says to call `generate_matrix` with `ledger_path` set directly to the committed meta ledger. Doing so once (to reproduce the intended flow) mutated `.planning/v1.3-defect-coverage-ids.json` in place — `git -C /workspaces status --porcelain` showed 18 new lines added, violating the plan's own acceptance criterion that the ledger stay untouched and violating "the meta repo is read-only here."
- **Fix:** Reverted the accidental mutation (`git -C /workspaces checkout -- .planning/v1.3-defect-coverage-ids.json`), then re-ran the regeneration against two independent scratch copies of the ledger instead of the live file, matching `test_golden_file_matches`'s own tmp-seeding methodology (named explicitly in this task's `read_first`).
- **Files modified:** None beyond the two task-scoped files; the accidental ledger mutation was reverted before it was ever staged or committed.
- **Verification:** `git -C /workspaces status --porcelain .planning/v1.3-defect-coverage-ids.json` empty after the corrected run; two scratch-copy regenerations `cmp`-identical.
- **Committed in:** `098702c` (Task 2 commit) — the ledger mutation itself was never committed anywhere.

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug in following the plan's literal instruction, corrected against the plan's own acceptance criteria and threat-model mitigation T-121-01)
**Impact on plan:** Necessary correction to avoid silently rewriting a read-only meta-repo artifact. No scope creep — the fix is a change in *how* the regeneration ran, not *what* it produced (same golden bytes either way, since the auto-registered ledger additions do not feed back into the matrix output on the same run).

## Issues Encountered
- This devcontainer's pytest run (syrupy 5.3.4 + cov 7.1.0 plugins active) does not print the standard final `pytest` terminal summary line (e.g., "1052 passed in 1.23s") when running the full `tests/` directory — output ends after the last progress-bar line and the syrupy snapshot-report footer ("29 snapshots passed."), with no `pytest` summary line at all, reproduced identically with and without `-p no:cacheprovider`, redirected to a file (ruling out terminal-width truncation). Verified 1052 passed / 0 failed via three independent checks instead: exit code 0; counting the exact number of `.` progress characters across all lines (1052, matching 1051 pre-existing + 1 now-fixed); and confirming zero `F`/`E`/`s`/`x` characters anywhere in the raw output. Single-file runs (e.g. `pytest tests/test_audit_coverage_matrix.py -v`) do print the normal summary line correctly, so this is scoped to the full-suite run in this environment, not a broken pytest install.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `test_golden_file_matches` is GREEN and the full host suite is 1052/1052 — later Phase 121 plans (121-02 through 121-14) that touch `dev test` code will now see any *new* matrix regression cleanly, not masked by this pre-existing drift.
- `[tool.ruff] extend-exclude` is in place before any formatter runs in the phase, including 121-03's two new fixture files under `tests/fixtures/` which this exclusion already anticipates.
- `/tmp/venv311` (Python 3.11.15, ruff 0.16.0) is available for every later plan to report a CI-parity ruff verdict rather than the devcontainer's ruff 0.15.20.
- No blockers. GATE-03 stays contributed-to-only (not closed) — 121-04 and 121-14 still own their portions.

## Self-Check: PASSED

Verified below.

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*
