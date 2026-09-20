---
phase: 200-an-elevated-programming-supply-is-stated
plan: 02
subsystem: cli
tags: [firestarter_app, test_characterization, snapshot, vcc, tracer]

# Dependency graph
requires:
  - phase: 200-an-elevated-programming-supply-is-stated
    plan: 200-01
    provides: "_SHIELD_FIXED_VCC_MV, programming_vcc_over_rail_mv, _format_v_prose, and the live Programming VCC: row + warning block in firestarter/eprom_info.py, which this plan pins through the real entry point"
provides:
  - "test_info_mbm27c1000 and test_info_mbm27c4001 in tests/test_characterization.py -- subprocess snapshot pins for the rail-slot class (281/284) and the datasheet-cited class (3/284)"
  - "a numerically-proved zero-deletion diff on tests/__snapshots__/test_characterization.ambr, both per-task and cumulative against the phase base 0d6be3f"
affects: [200-03]

# Actuals (#2632)
actuals:
  tokens: 1593
  tasks: 2
  commits: 2
plan_head_before: 077fce2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scoped --snapshot-update per single node id, proved narrow by git diff --numstat before commit (T-200-05 mitigation) -- reused verbatim from Phase 199's discipline, with the numstat expectation changed to insertions-with-zero-deletions rather than 199's 1-1, because this phase adds entries rather than rewriting one"

key-files:
  modified:
    - firestarter_app/tests/test_characterization.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "D-04 cited in both task commits: the two pinned parts are one from each class RESEARCH.md § G-1 separated -- MBM27C1000 (VCC_VOLTAGES[0x0D] rail slot, gh#70's part) and MBM27C4001 (one of exactly 3 datasheet-cited overrides). Both decode to 6000 mV vdd_mv and render identical Programming VCC:/warning blocks."
  - "Baseline-count discrepancy (not a deviation, a correction): the orchestrator's prompt stated the suite should move from 2087/32 to 2089/34. Measured actual: 2089 passed / 36 snapshots. Each new test pins TWO named snapshot entries (stdout + a separately-named stderr), so two new tests add 4 entries (32+4=36), not 2. The task count (2089 passed, +2 tests) matches exactly; only the snapshot-entry arithmetic in the prompt undercounted."

requirements-completed: [VCC-01, VCC-02]

coverage:
  - id: D1
    description: "The rendered `info` output an operator actually sees is pinned byte-for-byte for two elevated parts, through the real installed entry point, for both the rail-slot class (281/284 rows) and the datasheet-cited class (3/284 rows)."
    requirement: "VCC-01"
    verification:
      - kind: e2e
        ref: "tests/test_characterization.py::test_info_mbm27c1000 (subprocess, real entry point)"
        status: pass
      - kind: e2e
        ref: "tests/test_characterization.py::test_info_mbm27c4001 (subprocess, real entry point)"
        status: pass
      - kind: unit
        ref: "inline pathlib/re block asserting VCC:/Programming VCC:/VPP: ordering and blank-line/warning shape in both new .ambr blocks, and absence in the two pre-existing info blocks"
        status: pass
    human_judgment: false
  - id: D2
    description: "The snapshot change to tests/__snapshots__/test_characterization.ambr is purely additive -- git diff --numstat against the phase base 0d6be3f reports insertions with exactly zero deletions, a byte-identity proof for every pre-existing line."
    requirement: "VCC-02"
    verification:
      - kind: unit
        ref: "git diff --numstat (per task, uncommitted tree) -- Task 1: 59 0; Task 2: 59 0"
        status: pass
      - kind: unit
        ref: "git diff --numstat 0d6be3f -- tests/__snapshots__/test_characterization.ambr (cumulative, uncommitted tree before Task 2's commit) -- 118 0"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-09-19
status: complete
---

# Phase 200 Plan 02: An elevated programming supply is stated Summary

**`firestarter info MBM27C1000` and `firestarter info MBM27C4001` are now pinned by subprocess snapshot through the real installed entry point — both render `Programming VCC: 6.0v` and the two-line shortfall warning — and the `.ambr` diff against the phase base is proved to be 118 insertions, 0 deletions.**

## Performance

- **Duration:** ~35 min (includes a ~2m50s full-suite run)
- **Completed:** 2026-09-19
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `tests/test_characterization.py` gains `test_info_mbm27c1000` (the rail-slot class, gh#70's part) and `test_info_mbm27c4001` (the datasheet-cited class — one of exactly 3 of the 284 elevated rows), placed immediately after `test_info_at28c256`, each with a paired named `_stderr` snapshot proving the warning is on stdout.
- `tests/__snapshots__/test_characterization.ambr` gains four new entries: `test_info_mbm27c1000`, `test_info_mbm27c1000[test_info_mbm27c1000_stderr]`, `test_info_mbm27c4001`, `test_info_mbm27c4001[test_info_mbm27c4001_stderr]`.
- Both new blocks show the exact D-04 shape: `VCC:                5.0v` / `Programming VCC:    6.0v` / `VPP:                12.5v`, then a blank line, then `WARNING: this part's programming supply decodes to 6.0 V; the shield supplies a fixed 5.0 V.`, then `Programming will be attempted at 5.0 V.`
- The two pre-existing `info` snapshots (`test_info_known_chip`, `test_info_at28c256`, both `vdd_mv` 5000) are confirmed byte-identical: `git diff --numstat 0d6be3f` on the `.ambr` reports `118  0` — insertions only, zero deletions, across the whole phase.
- `ruff check` and `ruff format --check` pass over `firestarter/` and `tests/`. The full suite passes on the Python 3.11 CI replica: **2089 passed, 36 snapshots** (baseline was 2087 passed, 32 snapshots).
- The entry-point precondition was asserted, not assumed: `command -v firestarter` resolves to `/home/vscode/.local/bin/firestarter`, and `firestarter.__file__` (on `.venv/ci-replica`) resolves to `/workspaces/firestarter_app/firestarter/__init__.py` — the editable install tracks this working tree.

## Numstat Evidence (the plan's whole proof)

| Point measured | Command | Result |
|---|---|---|
| Task 1, uncommitted tree, immediately after re-record | `git diff --numstat -- tests/__snapshots__/test_characterization.ambr` | `59  0` |
| Task 2, uncommitted tree, immediately after re-record | same | `59  0` |
| Cumulative, uncommitted tree, before Task 2's commit | `git diff --numstat 0d6be3f -- tests/__snapshots__/test_characterization.ambr` | `118  0` |

Every leg reports a non-zero insertion count and a deletion count of exactly zero. No pre-existing line in the 1333(+118)-line file moved.

## Recorded Snapshot Excerpt (`test_info_mbm27c1000`)

```
  VCC:                5.0v
  Programming VCC:    6.0v
  VPP:                12.5v
  Chip ID:            0x4e5
  Pulse delay:        500µS

  WARNING: this part's programming supply decodes to 6.0 V; the shield supplies a fixed 5.0 V.
  Programming will be attempted at 5.0 V.
```

`test_info_mbm27c4001`'s block carries the identical three-row/warning shape (both parts decode to 6000 mV); it differs only in `Name:`, `Manufacturer:`, pin count/layout, and `Chip ID:`.

## Task Commits

Each task was committed atomically, inside `firestarter_app` on `v1.40-program-parameter-fidelity`:

1. **Task 1: The rail-slot class, pinned — MBM27C1000 through the real entry point** - `afeb11d` (test)
2. **Task 2: The datasheet-cited class, pinned — MBM27C4001, plus the no-collateral-movement proof** - `cc99e03` (test)

**Gitlink advance:** `f97cb503` (docs, meta repo) — advances the `firestarter_app` submodule pointer to `cc99e03`.

**Plan metadata:** committed separately in the meta repo per this plan's `<commit_protocol>`.

_`plan_head_before: 077fce2` is the `firestarter_app` HEAD immediately before this plan's first commit (the HEAD 200-01 left it at); `git rev-list --count 077fce2..HEAD` inside `firestarter_app` reports 2, matching the two task commits above (the gitlink advance is a meta-repo commit, counted separately)._

## Files Created/Modified

- `firestarter_app/tests/test_characterization.py` — `test_info_mbm27c1000`, `test_info_mbm27c4001`.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — four new syrupy entries (2 stdout blocks, 2 empty stderr blocks).

## Decisions Made

- Named `test_info_mbm27c4001` as the sibling to `test_info_mbm27c1000`, per the plan's naming instruction, so a reader finds both classes side by side.
- Confirmed via `tools/datasheet_overrides.json` that `FUJITSU/MBM27C4001`'s override is datasheet-cited (`datasheets/MBM27C4001.pdf`, gh#66's attached datasheet, VCC 6.0V ± 0.25V during programming) rather than a rail-table slot — the docstring cites this so a later reader can re-derive the classification without re-running the research measurement.
- Advanced the meta gitlink once, after both tasks, matching the precedent 200-01-SUMMARY.md set (one gitlink-advance commit per plan, not per task).

## Deviations from Plan

None — plan executed exactly as written. The one discrepancy worth recording is not a deviation in behavior but a measurement correction: the orchestrator's prompt stated the full-suite count should move to "2089 / 34"; the measured actual is 2089 / 36. The task-count component (2089, i.e. +2 over the 2087 baseline) matches exactly the two new tests. The snapshot-entry component undercounted because each new test pins two named snapshot entries (a stdout block and a separately-named stderr block), so two new tests add four entries, not two (32 + 4 = 36). This plan's own frontmatter `must_haves` never asserted a specific total, only "the full suite passes... before/after counts stated," which is satisfied by the measured 2087/32 → 2089/36 figures reported here.

## Human-Check (from Task 2's `<verify>` block)

The plan's Task 2 `<verify>` includes a `human-check` asking the operator to confirm, at end-of-phase UAT: (1) the two spellings — `6.0v` in the field-row cell (via `format_mv`) versus `6.0 V` in the warning prose — are both wanted, and (2) the amended-verb sentence (`"...programming supply decodes to 6.0 V..."`) reads as intended. This executor did not run that human-check (it requires the operator, not an agent, per the plan's own instruction); it is **pending end-of-phase UAT**. The wording itself is unchanged from what 200-01 shipped and this plan pins byte-for-byte — no new wording decision was made in this plan.

## Backlog Observations (not acted on, per plan instruction)

- The misaligned `Support status:`/`Reason:` rows (one column right of every `pos`-formatted row) remain unfixed, per the plan's explicit prohibition — fixing them would move the two pre-existing `info` snapshots and destroy the zero-deletions gate this plan's whole proof rests on. Already filed by 200-01; not re-filed here.

## Issues Encountered

None. Both tasks' `<verify>` chains passed on first attempt with no auto-fixes needed.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `tests/test_characterization.py` now carries committed evidence for both classes of elevated-supply row (`test_info_mbm27c1000` for the 281-row rail-slot class, `test_info_mbm27c4001` for the 3-row datasheet-cited class), ready for plan 200-03's full-database census module (`tests/test_programming_vcc_census.py`) to build on without needing further characterization coverage.
- No blockers. STATE.md, ROADMAP.md, and REQUIREMENTS.md updates are deferred to the orchestrator per this plan's execution instructions.

---
*Phase: 200-an-elevated-programming-supply-is-stated*
*Completed: 2026-09-19*

## Self-Check: PASSED

- `FOUND: firestarter_app/tests/test_characterization.py`
- `FOUND: firestarter_app/tests/__snapshots__/test_characterization.ambr`
- Commit `afeb11d` (test, Task 1) present in `firestarter_app` history
- Commit `cc99e03` (test, Task 2) present in `firestarter_app` history
- Commit `f97cb503` (gitlink advance) present in meta history
- `git -C firestarter_app rev-parse --abbrev-ref HEAD` == `v1.40-program-parameter-fidelity`
- `git rev-parse --abbrev-ref HEAD` (meta) == `v1.40-program-parameter-fidelity`
