---
phase: 109-destructiveness-gate-safety
plan: 03
subsystem: testing
tags: [ast, static-analysis, ci-gate, pytest, dev-test, safety]

# Dependency graph
requires:
  - phase: 109-01
    provides: derive_plan strip+advisory (SAFE-01) and UV small-region write cap (PATT-03) in firestarter_app/firestarter/chip_test.py -- the clean source this checker scans
  - phase: 109-02
    provides: SAFE-02 orchestrator-only verification tests (proves run_plan already routes through resolve_chip, sets no VPP, no raw wire dict, no --force)
provides:
  - "tools/check_devtest_orchestrator.py -- AST-based CI checker denying VPP-set / raw-wire-dict / --force in dev test's orchestrator code paths (SAFE-03)"
  - "tests/test_check_devtest_orchestrator.py -- mandatory anti-hollow paired pytest (subprocess exit 0 clean / non-zero on 4 planted violation classes)"
affects: [110-report-model, 112-dev-test-cli-handler]

# Tech tracking
tech-stack:
  added: []
  patterns: ["AST-based CI checker (ast.parse + ast.NodeVisitor) gated by a subprocess-invoking pytest with env-override negative fixtures -- the anti-hollow gate pattern"]

key-files:
  created:
    - firestarter_app/tools/check_devtest_orchestrator.py
    - firestarter_app/tests/test_check_devtest_orchestrator.py
  modified: []

key-decisions:
  - "Deny-list vocab: VPP-set names {set_vpp, enable_vpp, write_vpp, vpp_enable, set_voltage, assert_vpp, raise_vpp}; wire-dict keys {cmd, algorithm, vpp_mv, bus-config, pin-count, chip-id, flags, pulse-delay, memory-size} with a >=2-key-match threshold to avoid single-incidental-key false positives; force detection covers both force=True keyword args and bare \"--force\" string literals."
  - "Host-only assertion scoped narrowly: rejects only paths resolving INTO the sibling firestarter/ firmware sub-repo, not paths outside firestarter_app generally -- this permits the mandatory pytest tmp_path env-override injection seam (FIRESTARTER_DEVTEST_SRC) to work without weakening the real firmware-untouched guarantee."
  - "Phase-112 dev_test_cli.py handler path is scanned-if-present, silently skipped if absent (D-02 scope tolerance); checker fails loudly instead if NO target exists at all, avoiding a vacuous pass with zero files scanned."

patterns-established:
  - "Anti-hollow CI checker pairing: tools/<checker>.py + tests/test_<checker>.py where the pytest subprocess-invokes the real checker binary and asserts both a clean-pass AND a planted-violation non-zero exit via an env-override path seam -- mirrors tools/check_dispatch.py + tests/test_check_dispatch_invariants.py."

requirements-completed: [SAFE-03]

coverage:
  - id: D1
    description: "AST-based checker tools/check_devtest_orchestrator.py denies VPP-set call sites, raw command-dict/wire-JSON construction, and force=True/--force pass-through in chip_test.py; asserts firmware sub-repo is never in scan scope"
    requirement: "SAFE-03"
    verification:
      - kind: unit
        ref: "tools/check_devtest_orchestrator.py invoked directly: `cd firestarter_app && python tools/check_devtest_orchestrator.py` exits 0 with PASS: line"
        status: pass
    human_judgment: false
  - id: D2
    description: "Paired anti-hollow pytest proves the checker exits 0 on clean source AND non-zero on each of 4 planted violation classes (VPP-set, raw-wire-dict, force=True, --force string) injected via FIRESTARTER_DEVTEST_SRC env-override"
    requirement: "SAFE-03"
    verification:
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py -- all 6 tests (clean-pass + 4 planted-violation + env-override-seam-sanity)"
        status: pass
    human_judgment: false

# Metrics
duration: 35min
completed: 2026-07-02
status: complete
---

# Phase 109 Plan 03: SAFE-03 Machine-Enforced Orchestrator-Only Gate Summary

**AST-based CI checker (`tools/check_devtest_orchestrator.py`) denies VPP-set / raw-wire-dict / `--force` in `dev test`'s code paths, paired with a mandatory anti-hollow pytest that proves the gate actually fails on 4 planted violation classes -- closing this project's v1.12 hollow-GATE-03 tech debt.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-07-02T19:35:00Z (approx)
- **Completed:** 2026-07-02T20:10:00Z
- **Tasks:** 2 (both `type="auto"`)
- **Files modified:** 2 (both new files, submodule `firestarter_app/`)

## Accomplishments

- Created `firestarter_app/tools/check_devtest_orchestrator.py`: a genuinely-populated `ast.parse` + `ast.NodeVisitor`-based checker (fresh AST walk -- `tools/check_dispatch.py` is a DB-scanning checker with no AST precedent in this codebase, so only its tool *shape* was mirrored: env-overridable path constant, buckets → per-bucket `FAIL:` → `sys.exit(1)`, `PASS:` line, `if __name__ == "__main__": main()`). Scans `chip_test.py` (default target, overridable via `FIRESTARTER_DEVTEST_SRC`) and the not-yet-existing Phase-112 `dev_test_cli.py` handler (silently skipped if absent — scope tolerance).
- The checker denies three violation classes: VPP-set call sites (7-name deny-list: `set_vpp`, `enable_vpp`, `write_vpp`, `vpp_enable`, `set_voltage`, `assert_vpp`, `raise_vpp`), raw command-dict/wire-JSON construction (dict literals matching >=2 of 9 wire-protocol keys), and `force=True` keyword args / bare `"--force"` string literals. It also asserts the firmware sub-repo is never in scan scope (host-only framing), narrowly scoped to reject only paths resolving into the sibling `firestarter/` firmware repo (not a blanket "must be inside firestarter_app" check, which would have broken the mandatory pytest env-override injection seam).
- Verified the checker exits 0 with a `PASS:` line on the real, clean, post-109-01/109-02 `chip_test.py` source (confirms zero VPP-set, zero raw-wire-dict, zero `--force` today).
- Created `firestarter_app/tests/test_check_devtest_orchestrator.py`: 6 tests mirroring `test_check_dispatch_invariants.py`'s `_FA_DIR = Path(__file__).parent.parent` cwd-independence idiom. Test 1 is the clean-pass baseline (subprocess, `returncode == 0`, `"PASS:"` in stdout). Tests 2-5 are the mandatory anti-hollow planted-violation proofs -- each writes a real temp `.py` fixture (VPP-set call, raw wire dict, `force=True`, bare `"--force"` string) and injects it via the `FIRESTARTER_DEVTEST_SRC` env-override at the subprocess level (never an in-process synthetic), asserting `returncode != 0` and `"FAIL:"` in stdout. Test 6 is an env-override-seam sanity check proving a *clean* fixture routed through the same injection seam still passes, isolating tests 2-5's failures as genuinely caused by the planted violations rather than the injection mechanism itself.
- Ran `python -m ruff check` and `python -m ruff format --check` on both new files -- both clean (format required one auto-reformat pass, applied and re-verified).
- Ran the full `firestarter_app` test suite: 796 passed, 1 pre-existing failure (`tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` -- documented in the plan's `<baseline_note>` as unrelated coverage-matrix golden drift, expected to stay red).

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`):

1. **Task 1 + Task 2 (combined single commit — both new files land together as one coherent checker+test pairing):** `29f0057` (feat) — "AST-based orchestrator-only checker + anti-hollow pytest (SAFE-03)"

**Plan metadata:** this commit (docs: complete plan) — committed in the meta repo, not the submodule.

_Note: the plan's two tasks (checker, then paired test) were implemented and verified sequentially per the plan's own dependency order, but committed as a single atomic commit in the submodule since the checker is not independently meaningful without its mandatory anti-hollow test (D-03: "a checker with no negative-fixture test is a failure of this plan") — landing them separately would have created an intermediate commit where the SAFE-03 gate was still hollow._

## Files Created/Modified

- `firestarter_app/tools/check_devtest_orchestrator.py` — AST-based orchestrator-only checker (new, 209 lines)
- `firestarter_app/tests/test_check_devtest_orchestrator.py` — paired anti-hollow pytest (new, 178 lines)

## Decisions Made

- **Host-only assertion scope:** narrowed from "target path must resolve inside `firestarter_app`" to "target path must NOT resolve into the sibling `firestarter/` firmware sub-repo." The broader check initially failed `pytest`'s own `tmp_path` fixture (used for the mandatory env-override negative-fixture injection, which necessarily lives outside `firestarter_app` in `/tmp`) — the narrower check preserves the real safety property (firmware repo never in scope) while permitting the test seam the plan itself mandates.
- **Combined single commit for both tasks:** the checker and its paired anti-hollow test were committed together rather than as two separate task commits, because D-03 explicitly treats a checker without its negative-fixture test as an incomplete/failed deliverable — there is no meaningful intermediate state to commit between them.
- **>=2-key wire-dict threshold:** a dict literal must match at least 2 of the 9 wire-protocol keys to be flagged, avoiding false positives on an unrelated dict that coincidentally uses one overlapping key name (e.g. a generic `"flags"` key in unrelated code).

## Deviations from Plan

None — plan executed exactly as written. The only in-flight adjustment (host-only assertion scoping) was discovered and fixed during Task 1/2 verification itself, before any commit, and is documented above as a decision rather than a post-commit deviation.

## Issues Encountered

- Initial `_assert_host_only` implementation was too strict (rejected any path outside `firestarter_app`, including the pytest `tmp_path` fixtures used for negative-fixture injection) — caught immediately by the paired test's own env-override-seam sanity test (Test 6) failing with a false `FAIL: host-only framing violation`. Fixed by narrowing the check to specifically reject the sibling firmware repo path rather than everything outside `firestarter_app` (see Decisions Made). Re-verified: all 6 tests pass, checker still exits 0 on the real source.
- `ruff format --check` flagged both new files on first pass (minor line-wrapping); ran `ruff format` to auto-fix, re-verified `ruff check` + `ruff format --check` both clean and re-ran the checker + pytest suite to confirm the reformat didn't change behavior.

## User Setup Required

None — no external service configuration required. No `ci.yml` changes were made (per D-03, a dedicated CI step is optional/discretionary; the existing `Run pytest with coverage` step is the enforcement point and already runs `pytest tests/` which picks up the new test file automatically).

## Next Phase Readiness

- SAFE-03's machine-enforced contract is now live and build-failing: any future edit adding a VPP-set call, raw wire-dict construction, or `--force` pass-through to `chip_test.py` (or the eventual Phase-112 `dev_test_cli.py` handler) will fail `pytest tests/` in CI.
- Phase 112 (the `@dev.command("test")` CLI handler) can either land at `firestarter/dev_test_cli.py` (matching this checker's `_DEVTEST_CLI_HANDLER` constant, in which case the checker automatically starts scanning it with zero changes needed) or at a different path (in which case Phase 112 updates the constant) — either way the scope-tolerance mechanism means Phase 112 is not blocked by this checker's current absence-of-file skip.
- This closes Phase 109's SAFE-03 success criterion. Phases 109-01 and 109-02 (SAFE-01/PATT-03 and SAFE-02) were already complete; Phase 109 now has all three of its SAFE-0x + SWEEP-05/PATT-03 requirements addressed across its 3 plans.

---
*Phase: 109-destructiveness-gate-safety*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: firestarter_app/tools/check_devtest_orchestrator.py
- FOUND: firestarter_app/tests/test_check_devtest_orchestrator.py
- FOUND: .planning/phases/109-destructiveness-gate-safety/109-03-SUMMARY.md
- FOUND (submodule commit): 29f0057
- FOUND (meta commit): cf68523
