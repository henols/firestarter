---
phase: 09-delete-old-log-macros-measure-flash-savings
plan: 03
subsystem: logging
tags: [logging, host, comment-only, fwguard, FIRESTARTER_DEV_ALLOW_PRE_V12]

# Dependency graph
requires:
  - phase: 06-finish-firmware-id-encoded-log-pipeline
    provides: pre-v1.2 firmware refuse-guard (`if major < 3 ...`) and the `FIRESTARTER_DEV_ALLOW_PRE_V12=1` bypass env-var (LFW-05 + LHOST-04)
  - phase: 09-delete-old-log-macros-measure-flash-savings (sibling plans)
    provides: 09-CONTEXT.md Claude's-Discretion call to KEEP the env-var and refresh its rationale comment after the firmware bumps to major=3
provides:
  - Refreshed inline rationale comment at `firestarter_app/firestarter/serial_comm.py:752-754` describing the post-Phase-9 role of `FIRESTARTER_DEV_ALLOW_PRE_V12` as a bench-testing escape hatch for running a current host against historical (v2.x) firmware builds
affects: [phase-10+, bench-testing-docs, regression-testing-host-against-v2.x-firmware]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Phase-tagged inline comment voice preserved: `# Phase N (LXXX-NN): ...` (per 09-PATTERNS.md §Shared Patterns)"

key-files:
  created:
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-03-SUMMARY.md
  modified:
    - firestarter_app/firestarter/serial_comm.py (4-line → 3-line comment block at L752; mechanism untouched)

key-decisions:
  - "Drop \"until then [Phase 9 firmware bump]\" framing — after Phase 9 ships, the framing is false (the firmware HAS bumped to major=3). Reframe the env-var as a forward-looking escape hatch for bench-testing a current host against a historical (v2.x) firmware build."
  - "KEEP the FIRESTARTER_DEV_ALLOW_PRE_V12 mechanism rather than deleting it — it still has a legitimate bench-testing role per 09-CONTEXT.md §Claude's Discretion."

patterns-established:
  - "Comment-only refactors honour the scope boundary strictly: only firestarter/serial_comm.py is staged; other pre-existing sub-repo modifications (config.py, main.py) are NOT bundled into this commit."
  - "Acceptance criteria gate uses byte-precise greps (`grep -c 'until then'`, `grep -c 'FIRESTARTER_DEV_ALLOW_PRE_V12'`) to prove the mechanism stays at exactly 2 occurrences (one in comment, one in the `os.environ.get(...)` check) — protects against accidental mechanism breakage during prose edits."

requirements-completed: [LMIG-04]

# Metrics
duration: ~5 min
completed: 2026-05-19
---

# Phase 9 Plan 3: Host Comment Refresh Summary

**Refreshed the post-Phase-9 rationale comment for the `FIRESTARTER_DEV_ALLOW_PRE_V12` escape hatch at `serial_comm.py:752-754` — 4-line → 3-line, mechanism untouched, regression suites green unchanged.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-05-19T07:55:00Z (approx)
- **Completed:** 2026-05-19T07:59:50Z
- **Tasks:** 1
- **Files modified:** 1 (`firestarter_app/firestarter/serial_comm.py`)

## Accomplishments
- Dropped the stale "until then [Phase 9 firmware bump]" framing — the firmware HAS bumped, so the framing was factually wrong post-Phase 9.
- Reframed `FIRESTARTER_DEV_ALLOW_PRE_V12=1` as a forward-looking bench-testing escape hatch for running a current host against historical (v2.x) firmware builds.
- Confirmed the mechanism (the `if major < 3 and os.environ.get(...)` refuse-guard at lines 755-769) is byte-identical to pre-edit — only the comment changed.
- Both host regression suites stayed green unchanged: `test_fwguard.py` (4 PASS), `test_decoder.py` (25 PASS).

## Task Commits

Per-task atomic commit in the `firestarter_app` sub-repo:

1. **Task 1: Refresh the FIRESTARTER_DEV_ALLOW_PRE_V12 inline comment** — `firestarter_app@7f9b944` (docs)

_No meta-repo commit is included for this plan since the only edit lives in the sub-repo; the meta-repo will see the gitlink bump when the orchestrator merges the wave._

## Files Created/Modified

- `firestarter_app/firestarter/serial_comm.py` — Replaced the 4-line comment block at `L752-755` with a 3-line block per 09-PATTERNS.md §"Pattern Assignment 7". 32-space indentation preserved; no imports added/removed; the `try: major = int(...)` block and the `if major < 3 and os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") != "1": raise FirmwareOutdatedError(...)` mechanism unchanged.

### Diff

```diff
-                                # Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2
-                                # firmware. The firmware bumps to major=3 in
-                                # Phase 9; until then, bench scripts use
-                                # FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass.
+                                # Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2 firmware. The firmware bumped
+                                # to major=3 in Phase 9. Set FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass when
+                                # bench-testing a current host against a historical (v2.x) firmware build.
```

## Decisions Made

- **Keep, not delete, the env-var mechanism.** Per `09-CONTEXT.md §Claude's Discretion`, the `FIRESTARTER_DEV_ALLOW_PRE_V12` env-var has a legitimate bench-testing role for regressing a current host against a historical (v2.x) firmware build. This plan refreshes the rationale instead of removing the mechanism.
- **Scope boundary held.** The sub-repo had pre-existing unrelated modifications to `firestarter/config.py` and `firestarter/main.py` at execution start. These were NOT touched and NOT included in this plan's commit — `git add` staged only `firestarter/serial_comm.py`. Pre-existing changes are surface unrelated to LMIG-04 and remain for whichever plan/work introduced them to commit separately.

## Deviations from Plan

None — plan executed exactly as written.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** Single-task comment-only edit shipped clean; all 5 acceptance criteria passed first attempt; both regression suites stayed green unchanged.

## Verification Results

Plan-level acceptance gate (from `<verification>` block):

| # | Check | Command | Result |
|---|-------|---------|--------|
| 1 | Stale framing removed | `grep -c 'until then' firestarter_app/firestarter/serial_comm.py` | 0 (PASS) |
| 2 | New wording present | `grep -c 'bench-testing a current host against a historical (v2.x) firmware build' firestarter_app/firestarter/serial_comm.py` | 1 (PASS) |
| 3 | Mechanism intact (env-var ref count) | `grep -c 'FIRESTARTER_DEV_ALLOW_PRE_V12' firestarter_app/firestarter/serial_comm.py` | 2 (PASS — one in comment, one in `os.environ.get(...)`) |
| 4 | `test_fwguard.py` green | `pytest tests/test_fwguard.py -v` | 4 passed in 0.04s (PASS) |
| 5 | `test_decoder.py` green | `pytest tests/test_decoder.py -q` | 25 passed in 0.26s (PASS) |
| 6 | Combined post-commit re-run | `pytest tests/test_fwguard.py tests/test_decoder.py` | 29 passed in 0.27s (PASS) |

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Threat Flags

None — the surface (env-var + refuse-guard) was already in the plan's `<threat_model>`. This plan IS the mitigation for T-09-03-01 (stale rationale comment) and verifies T-09-03-02 (mechanism untouched) via the 2-occurrence grep + green pytest gate.

## Known Stubs

None.

## Next Phase Readiness

- **LMIG-04 complete:** Host-side rationale for `FIRESTARTER_DEV_ALLOW_PRE_V12` now correctly describes the post-Phase-9 reality.
- **Wave 1 sibling (Plan 02 — firmware atomic deletion in `firestarter/`) is independent** — disjoint sub-repo, no merge conflicts expected.
- **Ready for Phase 10:** No blockers carried forward. The escape-hatch mechanism remains available for any future bench-testing of v2.x firmware against the current host.

## Self-Check: PASSED

- `firestarter_app/firestarter/serial_comm.py` exists on disk and contains the new 3-line comment block at L752-754 (verified via Read post-edit).
- Sub-repo commit `7f9b944` exists (verified via `git log --oneline -3` in `firestarter_app/`).
- All 5 plan-level acceptance criteria PASS (verified via the table above).
- Combined post-commit pytest re-run: 29/29 PASS.

---
*Phase: 09-delete-old-log-macros-measure-flash-savings*
*Completed: 2026-05-19*
