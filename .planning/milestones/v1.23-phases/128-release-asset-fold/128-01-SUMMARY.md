---
phase: 128-release-asset-fold
plan: 01
subsystem: infra
tags: [ci, github-actions, pytest, checker, firmware, release-assets]

# Dependency graph
requires:
  - phase: 123-non-regression-baselines-gate-hardening
    provides: "check_size_baseline.py's house checker shape (docstring blocks, FIRESTARTER_SIZE_BASELINE env seam, manual argv parser, anti-hollow test convention) and test_checker_convention.py's BASE-08 enforcement mechanism"
  - phase: 124-firmware-integration-merge
    provides: "the post-landing scripts/baseline/size_baseline.json avr_targets keys (uno, uno328pb, leonardo) this checker derives its required set from"
provides:
  - "scripts/check_release_assets.py — the AVR-assets-present gate, exit 0/1/2 taxonomy"
  - "tests/test_check_release_assets.py — 10-item anti-hollow pytest pairing"
  - "three committed pio_build/-rooted fixture trees (clean control + two planted violations)"
  - "the FIRESTARTER_PIO_BUILD_ROOT env seam (new; mirrors FIRESTARTER_SIZE_BASELINE)"
  - "raised test_checker_convention.py floors (FLOOR=6, FIXTURE_FLOOR=15) plus a corrected pre-existing FIXTURE_FLOOR drift"
affects: [128-04, 128-07, 128-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Sixth firmware checker following the check_X.py <-> test_check_X.py <-> planted_X* triple (BASE-08 house convention)"
    - "Directory-tree fixture build roots named pio_build/ (never .pio/) to avoid the repo's any-depth .gitignore pattern, reached through a dedicated env seam"

key-files:
  created:
    - firestarter/scripts/check_release_assets.py
    - firestarter/tests/test_check_release_assets.py
    - firestarter/tests/fixtures/clean_release_assets_all_three/README.md
    - firestarter/tests/fixtures/clean_release_assets_all_three/pio_build/uno/firestarter_uno.hex
    - firestarter/tests/fixtures/clean_release_assets_all_three/pio_build/uno328pb/firestarter_uno328pb.hex
    - firestarter/tests/fixtures/clean_release_assets_all_three/pio_build/leonardo/firestarter_leonardo.hex
    - firestarter/tests/fixtures/planted_release_assets_missing_uno328pb/README.md
    - firestarter/tests/fixtures/planted_release_assets_missing_uno328pb/pio_build/uno/firestarter_uno.hex
    - firestarter/tests/fixtures/planted_release_assets_missing_uno328pb/pio_build/leonardo/firestarter_leonardo.hex
    - firestarter/tests/fixtures/planted_release_assets_zero_byte_leonardo/README.md
    - firestarter/tests/fixtures/planted_release_assets_zero_byte_leonardo/pio_build/uno/firestarter_uno.hex
    - firestarter/tests/fixtures/planted_release_assets_zero_byte_leonardo/pio_build/uno328pb/firestarter_uno328pb.hex
    - firestarter/tests/fixtures/planted_release_assets_zero_byte_leonardo/pio_build/leonardo/firestarter_leonardo.hex
  modified:
    - firestarter/tests/test_checker_convention.py
    - firestarter/tests/fixtures/README.md

key-decisions:
  - "D-11/D-12 implemented exactly: scripts/check_release_assets.py derives its required set from size_baseline.json's avr_targets keys, never hardcoded filenames, with a never-vacuous guard on an empty key set"
  - "Task 2's three files (checker, paired test, floor bump) landed in ONE commit per the plan's explicit override of the generic RED/GREEN TDD split — test_checker_convention.py's own docstring mandates both floors rise in the same commit as the checker"
  - "FIXTURE_FLOOR corrected from 10 to 15 (not just 14) — the plan flagged a pre-existing drift (10 recorded vs 13 actual before this phase) that Phases 124/126 left uncorrected; this commit fixes it in the same breath as adding the phase's own two planted entries"
  - "Did not mark REL-02 or REL-03 complete in REQUIREMENTS.md — both are multi-plan requirements; this plan closes only the checker slice (REL-03) and the fail_on_unmatched_files invariant slice (REL-02); Plan 128-10 owns closure"

patterns-established:
  - "A checker's paired test module both proves the checker's own exit-code behavior AND, when a workflow-invariant test is folded in (Coverage 10), asserts over comment-stripped YAML with an explicit non-vacuity guard so a rewritten/broken source file fails loudly rather than passing vacuously"

requirements-completed: []  # REL-03 and REL-02 are multi-plan; only their checker/invariant slices close here. Plan 128-10 marks completion.

coverage:
  - id: D1
    description: "scripts/check_release_assets.py exits 0 on the clean AVR-assets tree, 1 on a missing or zero-byte hex, 1 on an empty avr_targets key set, and 2 on a malformed baseline or argv"
    requirement: "REL-03"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_release_assets.py (10 tests, subprocess-based against committed fixtures)"
        status: pass
    human_judgment: false
  - id: D2
    description: "beta-build.yml never sets the release action's fail_on_unmatched_files input as a YAML key, over comment-stripped source with a non-vacuity guard"
    requirement: "REL-02"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_release_assets.py::test_beta_build_yml_never_sets_fail_on_unmatched_files_key"
        status: pass
    human_judgment: false
  - id: D3
    description: "test_checker_convention.py's floors raised in the same commit as the checker (FLOOR 5->6, FIXTURE_FLOOR 10->15, correcting a pre-existing drift)"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_checker_convention.py (7 tests, all pass with the new checker/fixtures discovered)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-01
status: complete
---

# Phase 128 Plan 01: AVR-Assets-Present Gate Summary

**`scripts/check_release_assets.py` — a sixth firmware checker deriving its required AVR set from `size_baseline.json`, proven against three committed `pio_build/`-rooted fixtures and a comment-stripped `beta-build.yml` invariant test**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-01T20:47:00Z
- **Tasks:** 3/3 completed
- **Files modified:** 15 (13 created, 2 modified)

## Accomplishments
- Landed `scripts/check_release_assets.py`: derives the required AVR set from `scripts/baseline/size_baseline.json`'s `avr_targets` keys (never three hardcoded filenames), requires each `firestarter_<key>.hex` present and non-empty under a build root resolved via `FIRESTARTER_PIO_BUILD_ROOT`/`--build-root`, and never mentions or requires the py32f071 image (REL-03's tolerance).
- Landed `tests/test_check_release_assets.py`: 10 subprocess-based coverage items, including both seam-precedence tests (`FIRESTARTER_PIO_BUILD_ROOT` and `FIRESTARTER_SIZE_BASELINE`) and the REL-02 `fail_on_unmatched_files` invariant test over comment-stripped `beta-build.yml` source.
- Committed three fixture trees under non-dotted `pio_build/` build roots (`clean_release_assets_all_three`, `planted_release_assets_missing_uno328pb`, `planted_release_assets_zero_byte_leonardo`), all verified tracked via `git ls-files`, never `git add`'s exit code.
- Raised `test_checker_convention.py`'s `FLOOR` (5→6) and `FIXTURE_FLOOR` (10→15) in the same commit as the checker, correcting a pre-existing `FIXTURE_FLOOR` drift left by Phases 124 and 126.

## Task Commits

Each task was committed atomically inside `/workspaces/firestarter` on branch `v1.23-py32f071-integration`:

1. **Task 1: Commit the three release-assets fixture trees under non-dotted build roots** - `e40593d` (test)
2. **Task 2: Add check_release_assets.py, its paired pytest, and the raised convention floors** - `98d5baf` (feat) — landed as ONE commit per the plan's explicit instruction, not a RED/GREEN split (see TDD Gate Compliance below)
3. **Task 3: Prove the triple is committed, not merely on disk** - `2bac870` (docs)

**Plan metadata:** committed in the meta-repo (`.planning/phases/128-release-asset-fold/128-01-SUMMARY.md`, `STATE.md`, `ROADMAP.md`).

## TDD Gate Compliance

Task 2 carried `tdd="true"`, but the plan's own action text explicitly overrode the generic RED→GREEN split: *"Write ... then commit all three together. `test_checker_convention.py`'s own docstring (lines 53-66) mandates that both floors rise in the SAME commit that adds the checker; splitting them across commits leaves an intermediate red suite."* This is a deliberate, plan-directed exception (matching how Phases 123/124 landed their own checker/floor pairs), not a missed gate. No separate `test(...)` RED commit exists for this task by design; the single `feat(98d5baf)` commit includes the checker, its 10-test pairing, and the floor bump together, verified green as a unit before committing.

## Files Created/Modified
- `firestarter/scripts/check_release_assets.py` - the AVR-assets-present checker (exit 0/1/2 taxonomy, two env seams, manual argv parser)
- `firestarter/tests/test_check_release_assets.py` - 10-test anti-hollow pairing, subprocess-based against committed fixtures
- `firestarter/tests/fixtures/clean_release_assets_all_three/` - control fixture (all three AVR hexes present, no py32 image)
- `firestarter/tests/fixtures/planted_release_assets_missing_uno328pb/` - planted violation: `uno328pb/` absent entirely
- `firestarter/tests/fixtures/planted_release_assets_zero_byte_leonardo/` - planted violation: `leonardo`'s hex truncated to 0 bytes
- `firestarter/tests/test_checker_convention.py` - `FLOOR` 5→6, `FIXTURE_FLOOR` 10→15 (drift-corrected), docstring updated
- `firestarter/tests/fixtures/README.md` - new inventory section naming the three release-assets fixture trees

## Decisions Made
- Followed D-11/D-12 exactly: the checker's required set is derived from `size_baseline.json`'s `avr_targets` keys via a `FIRESTARTER_SIZE_BASELINE` seam already established by `check_size_baseline.py`; the new `FIRESTARTER_PIO_BUILD_ROOT` seam exists solely because `.gitignore`'s bare `.pio` pattern matches at any depth (research finding F-6) and would otherwise make the fixture uncommittable.
- `FIXTURE_FLOOR` raised to 15, not 14 — the plan explicitly flagged a pre-existing drift (10 recorded vs 13 actual pre-phase) that this commit corrects alongside adding this phase's own two `planted_*` entries (13 + 2 = 15).
- Did not mark REL-02 or REL-03 complete in `REQUIREMENTS.md` per the plan's explicit scope boundary — both requirements are multi-plan; Plan 128-10 is the sole owner of their closure.

## Deviations from Plan

None — plan executed exactly as written, including the explicit single-commit override for Task 2's TDD flow (documented above under "TDD Gate Compliance", not treated as a deviation since the plan itself mandated it).

## Issues Encountered
- The checker's initial never-vacuous-guard failure message contained the literal substring `PASS:` inside its own explanatory text (`"...must not print PASS:)"`), which broke `test_empty_avr_targets_never_vacuous`'s `"PASS:" not in result.stdout` assertion. Reworded the message to `"...must not report success"` (Rule 1 — bug fix, applied inline during Task 2 before committing; no separate commit needed since the file was not yet committed).

## User Setup Required
None - no external service configuration required. All work is local pytest-provable; no CI dispatch occurred in this plan (that is Plan 128-10's scope).

## Next Phase Readiness
- `scripts/check_release_assets.py` exists as a callable exit-code gate; Plan 128-07 wires its call site into `beta-build.yml` before the `Release` step.
- The `FIRESTARTER_PIO_BUILD_ROOT` seam is proven live and ready for Plan 128-07 to point at the real `.pio/build` (or leave at its default) in the actual workflow invocation.
- No blockers. Full firmware pytest suite green (180 passed); both native pio test envs (`native`, `native_nodevtools`) unchanged at 141/141 passing, confirming this plan touched no compiled surface.

---
*Phase: 128-release-asset-fold*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/scripts/check_release_assets.py`
- FOUND: `/workspaces/firestarter/tests/test_check_release_assets.py`
- FOUND: `/workspaces/.planning/phases/128-release-asset-fold/128-01-SUMMARY.md`
- FOUND commit `e40593d` (Task 1) in `firestarter`
- FOUND commit `98d5baf` (Task 2) in `firestarter`
- FOUND commit `2bac870` (Task 3) in `firestarter`
- FOUND commit `9dc90ff` (SUMMARY.md) in the meta-repo
