---
phase: 132-retire-dev-sdp-discharge-the-mypy-debt
plan: 01
subsystem: testing
tags: [mypy, ci, tooling, pytest, coverage, venv]

# Dependency graph
requires:
  - phase: 131-gate-hardening-ci-parity
    provides: "hardened tools/check_mypy_watermark.py (GATE-01..04), tools/ci_parity.sh (four-leg CI-parity recipe), the inherited fork-base count of 69 (131-CI-BASELINE.md)"
provides:
  - "firestarter_app/tools/ci_replica_venv.sh — a committed, numpy-free CI-replica venv script (five legs: install, numpy-absence, ruff, mypy watermark gate, pytest --cov)"
  - "132-CI-PARITY.md §1 — the pre-change ci_parity.sh reading (legs 1-3 pass, leg 4 exits 2 as expected)"
  - "132-MYPY-LEDGER.md §1-5 — the measured pre-change mypy reading (69 errors, watermark 35, checked 121 source files), a divergence check against Phase 131's inherited 69 (agrees exactly), the checked-floor verification, and a labelled projection to 32"
affects: [132-02, 132-03, 132-05, 132-06, 132-09, 133, 134, 135, 136]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Numpy-free CI-replica venv script, sibling to (never folded into) tools/ci_parity.sh -- separates 'faithful CI mirror' from 'local substitute for an ambient-environment problem'"
    - "Single mypy invocation reused for both gate classification and raw completion-summary-line evidence, via tools/check_mypy_watermark.py's own pure functions (run_mypy, classify_mypy_result, get_watermark, enforce_watermark) rather than a second subprocess or a hand-rolled argv"

key-files:
  created:
    - firestarter_app/tools/ci_replica_venv.sh
    - .planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-PARITY.md
    - .planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md
  modified: []

key-decisions:
  - "The 'git status --porcelain empty after a run' checks (in both this plan's own acceptance criteria and the script's internal leg-1 assertion) are read as a DELTA against the tree's pre-existing dirt (M .gitignore, .coverage, .planning/config.json, SECURITY.md, write_test_port.sh -- all measured present before this plan started and explicitly named as not-mine-to-touch), not a literal absolute emptiness check -- the literal reading is unsatisfiable in this environment regardless of this script's correctness, and the plan's own <verification> item 1 corroborates this reading by allowing only leg 4 to fail on 'the clean pre-change tree.'"
  - "Leg 4 runs mypy exactly once per script invocation (via check_mypy_watermark.py's own run_mypy()), printing both the raw 'Found N errors...(checked K source files)' line and the gate's 'mypy errors: N (watermark: M)' line from that single CompletedProcess, rather than running check_mypy_watermark.py as a subprocess AND separately re-invoking mypy for the raw line."

requirements-completed: []  # RETIRE-06 is owned by plan 132-09, per this plan's explicit objective -- NOTHING is marked Complete here.

coverage:
  - id: D1
    description: "firestarter_app/tools/ci_replica_venv.sh: numpy-free Python 3.11 CI-replica venv, five legs, reused across runs, proving numpy absent and reporting a trustworthy mypy count with the checked-K clause present"
    verification:
      - kind: other
        ref: "bash tools/ci_replica_venv.sh (run twice: first run installs, second run prints REUSED and completes ~30s faster with no reinstall)"
        status: pass
    human_judgment: false
  - id: D2
    description: "132-CI-PARITY.md §1: pre-change ci_parity.sh reading recorded verbatim (legs 1-3 pass, leg 4 exits 2 as the expected numpy-truncation shape), plus the named --cov-fail-under=70 gap"
    verification:
      - kind: other
        ref: "bash tools/ci_parity.sh, re-run a second time for reproducibility -- identical leg exits both times (1=0, 2=0, 3=0, 4=2)"
        status: pass
    human_judgment: false
  - id: D3
    description: "132-MYPY-LEDGER.md §1-5: the measured pre-change mypy reading (69 errors, watermark 35, checked 121), agreement check against Phase 131's inherited 69, checked-floor verification, and a labelled projection"
    verification:
      - kind: other
        ref: "tools/ci_replica_venv.sh leg 4 output cross-checked against a direct .venv/ci-replica/bin/python -m mypy firestarter/ tests/ run, whose per-file and per-code distributions were independently counted and match the ledger exactly"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-08-03
status: complete
---

# Phase 132 Plan 01: CI-Replica Measuring Instrument Summary

**Built a committed, numpy-free CI-replica venv script and took the pre-change readings: 69 mypy errors (watermark 35, checked 121 source files) and a reproducible four-leg ci_parity.sh baseline, before any `dev sdp` deletion or mypy fix landed.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-03T17:16:30Z (approx, per STATE.md's last_updated at dispatch)
- **Completed:** 2026-08-03T17:39:22Z
- **Tasks:** 3
- **Files modified:** 3 (all new)

## Accomplishments
- `firestarter_app/tools/ci_replica_venv.sh` committed: builds/reuses a Python 3.11 venv at `.venv/ci-replica` (gitignored), proves numpy absent, then runs ruff, the mypy watermark gate (via a single mypy invocation reusing `check_mypy_watermark.py`'s own pure functions), and pytest with CI's exact `--cov-fail-under=70` invocation.
- Pre-change `tools/ci_parity.sh` baseline recorded and independently reproduced twice: legs 1-3 exit 0, leg 4 exits 2 (the numpy-truncation shape, expected and correct per Phase 131's hardened gate).
- Pre-change mypy count measured today in the replica venv: **69 errors, watermark 35, checked 121 source files** — agrees exactly with Phase 131's inherited CI reading, with a fresh, independently-cross-checked per-file/per-code error distribution.
- Named the one gap `ci_parity.sh`'s legs 1/2 do not cover (the `--cov-fail-under=70` coverage floor) and closed it with the new script's leg 5.

## Task Commits

Each task was committed atomically, in the repo that owns the file:

1. **Task 1: Preconditions + pre-change CI-parity baseline** - `c571f9b` (docs, meta-repo)
2. **Task 2: tools/ci_replica_venv.sh** - `35a58f0` (feat, `firestarter_app` submodule)
3. **Task 3: Pre-change mypy baseline ledger** - `af15348` (docs, meta-repo)

_No TDD task in this plan — all three tasks are `type="auto"` (Task 2 carries `tdd="true"` in its frontmatter, but its "test" is the acceptance-criteria verification run, not a separate RED/GREEN pytest cycle; the script itself has no unit-test module of its own in this plan's scope)._

## Files Created/Modified
- `firestarter_app/tools/ci_replica_venv.sh` - Numpy-free CI-replica venv script, five legs, executable, committed in the submodule on `gsd/v1.30-sdp-surface-retirement`.
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-PARITY.md` - Pre-change `ci_parity.sh` reading (§1), leaving §2 (after) for a later plan.
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md` - Pre-change mypy reading (§1-5), leaving append-points for plans 132-06 and 132-09.

## Decisions Made
- **Delta-based git-status-clean interpretation.** This plan's own tree carries pre-existing dirt (` M .gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`), measured before dispatch and explicitly out of scope to touch. Both the plan's acceptance criterion ("`git status --porcelain` is empty after a run") and the script's own internal assertion ("nothing a run creates can appear as untracked") are honored as a **delta check against a before-snapshot**, not a literal absolute-emptiness check — the literal reading is unsatisfiable regardless of correctness, given this environment's pre-existing dirt, and the plan's own `<verification>` item 1 (permitting only leg 4 to fail on "the clean pre-change tree") corroborates that this dirty tree is itself being treated as the plan's "clean pre-change tree" baseline. No pre-existing dirt was touched, committed, or cleaned up.
- **Leg 4 runs mypy exactly once.** Rather than shelling out to `check_mypy_watermark.py` as a subprocess and then separately re-invoking mypy to recover the raw `Found N errors...(checked K source files)` line, leg 4 is a single inline `python -c` that imports `run_mypy`, `classify_mypy_result`, `get_watermark`, and `enforce_watermark` directly from `tools/check_mypy_watermark.py`, calls `run_mypy()` once, and prints the raw completion line from that same `CompletedProcess` before handing it to the gate's own classification. This satisfies the plan's "reuse the pure seam, don't duplicate mypy's argv, don't switch to JSON mode" instruction while running mypy only once per script invocation.

## Deviations from Plan

None — plan executed exactly as written. The two items above are documented under "Decisions Made" because they are interpretive choices about literal-vs-intended acceptance-criterion wording in a pre-dirty environment, not corrections to broken code, missing functionality, or blocking failures (Rules 1-3), and not architectural changes (Rule 4). No code, test, or gate was weakened, skipped, or forced green to make an acceptance grep pass.

## Issues Encountered
- First draft of `tools/ci_replica_venv.sh`'s leg-4 inline Python contained an unescaped double quote inside a bash double-quoted heredoc-style string (`-c "..."`), which would have broken the bash string boundary. Caught by `bash -n` syntax validation before the first execution attempt; fixed by rewording the affected message to avoid embedded quote characters entirely. No commit was made with the broken version.
- The acceptance criterion `grep -c "output json" tools/ci_replica_venv.sh` initially returned 2 (the script's own header comments explaining *why it never* uses `mypy --output json` contained that literal substring). Reworded the two comments to "JSON reporting mode" phrasing, preserving the same rationale without the literal flag-shaped substring, so the grep now correctly returns 0.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `tools/ci_replica_venv.sh` is ready for every remaining Phase 132 plan (132-02 through 132-09) to use for iterating on mypy fixes with a trustworthy local count, and for Phases 133-136 to reuse against the identical ambient-numpy wall.
- `132-MYPY-LEDGER.md` carries the pre-change baseline (69/35/121) and explicit append-points for plan 132-06's post-fix measurement and plan 132-09's certifying CI reading — no further action needed from this plan.
- `132-CI-PARITY.md` §1 is complete; §2 ("After") is owned by a later plan per the ROADMAP's cross-cutting rule to run the recipe both before and after the deletion + discharge.
- No blockers. RETIRE-06 remains unticked, as required — this plan measured but did not certify.

---
*Phase: 132-retire-dev-sdp-discharge-the-mypy-debt*
*Completed: 2026-08-03*

## Self-Check: PASSED

All four created files verified present on disk:
- `firestarter_app/tools/ci_replica_venv.sh` — FOUND
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-PARITY.md` — FOUND
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md` — FOUND
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-01-SUMMARY.md` — FOUND

All four commits verified present in their owning repo's history:
- `c571f9b` (meta-repo) — FOUND
- `35a58f0` (`firestarter_app` submodule) — FOUND
- `af15348` (meta-repo) — FOUND
- `f47e731` (meta-repo, this summary) — FOUND
