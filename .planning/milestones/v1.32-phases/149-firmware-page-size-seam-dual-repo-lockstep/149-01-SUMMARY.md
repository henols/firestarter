---
phase: 149-firmware-page-size-seam-dual-repo-lockstep
plan: 01
subsystem: firmware-build-infra
tags: [platformio, avr, git-submodule, baseline, provenance]

# Dependency graph
requires: []
provides:
  - "firestarter submodule forked onto gsd/v1.32-at28c-write-path-root-cause-report-provenance off origin/beta, verified by content"
  - "cold pre-edit flash/RAM/warning baseline for uno, uno328pb, leonardo at the v1.32 fork point"
  - "149-PAGE-SIZE.md skeleton carrying the fork point, D-13 baseline, and D-01 provenance evidence"
affects: [149-02, 149-03, 149-04, 149-05, 149-06, 149-07, 149-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fork verification by content (5 checks: constant presence, file existence, symbol count, diff --stat emptiness) instead of git merge-base --is-ancestor, because squash-merged PRs produce false-negative ancestry checks"
    - "Cold baseline capture (rm -rf build dir + single pio run) taken at fork point before any firmware edit, so later plans' deltas are attributable"

key-files:
  created:
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-baseline-cold-uno.log
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-baseline-cold-uno328pb.log
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-baseline-cold-leonardo.log
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md
  modified: []

key-decisions:
  - "Forked firestarter's v1.32 branch off origin/beta (7f6afc65be2022575989772cc0a5945611741831), not off the stale v1.31 tip (6992271), verified by five content checks with zero ancestry checks (D-13/P-1)"
  - "Cold capture at the fork point matched size_baseline.json exactly on all six figures per env (0 inherited delta) and matched BASE-01 within the already-adjudicated +96 B Phase 145 exemption"

patterns-established:
  - "149-PAGE-SIZE.md as the phase's single D-16 review artifact, built incrementally across plans with named placeholder sections for work not yet done"

requirements-completed: []  # PGSZ-04/PGSZ-05 span multiple plans; this plan contributes evidence only, per phase planner_decisions

# Metrics
duration: ~20min
completed: 2026-08-19
status: complete
---

# Phase 149 Plan 01: Fork v1.32 Firmware Branch and Cold Pre-Edit Baseline Summary

**Forked `firestarter` onto the v1.32 milestone branch off `origin/beta` (verified by content, not ancestry), captured a cold pre-edit flash/RAM/warning baseline for all three AVR targets, and created the phase's `149-PAGE-SIZE.md` review-artifact skeleton with the D-01 provenance evidence pre-loaded.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-08-19
- **Tasks:** 3/3 completed
- **Files modified:** 4 (3 baseline logs + 1 review artifact, all in the meta repo; no file was created or modified inside `firestarter`)

## Accomplishments

- `firestarter/` is now on `gsd/v1.32-at28c-write-path-root-cause-report-provenance`, forked off `origin/beta` at `7f6afc65be2022575989772cc0a5945611741831`. Verified by five content checks (MERGE-05 constants present, `size_baseline_base01.json` exists, `eprom_internal_program_pulse` appears 4×, `CAP-02` present in `firestarter.cpp`, and an empty `diff --stat` for every file this phase will touch, against the old v1.31 tip `6992271`). Zero `git merge-base --is-ancestor` invocations were used anywhere.
- Cold `pio run` captured for `uno`, `uno328pb`, `leonardo` (one `rm -rf .pio/build/<env>` + one uninterrupted `pio run` each), all three ending `[SUCCESS]` with zero `warning:` lines. All six flash/RAM figures matched `size_baseline.json` exactly — zero inherited delta from the v1.31→beta merge. Delta vs BASE-01 (`size_baseline_base01.json`) is +96 B flash on all three envs (Phase 145's already-funded W27C512 fix) and 0 B RAM on all three.
- Leonardo's MERGE-05 flash headroom recorded as the number **0 bytes** (band 0 + exemption 96, current delta already +96); uno-class headroom recorded as **64 bytes**. v1.31's open MERGE-05 band breach is named explicitly in the artifact, not silently absorbed.
- `149-PAGE-SIZE.md` created with all 13 required `##` headings (8 filled by this plan, 5 placeholders for plans 03–08), the D-01 upstream-provenance table (47/19/18 → 84 rows, 66 promoted vs 18 native), the 15 movers and 3 no-change part lists, the citation chain (`infoic-field-dictionary.md:241`, pinned `infoic.xml` md5), and the three measured non-claims (no silicon claim, AT28C256/gh#21 unchanged, 16/32-row floor safety stated as unproven).
- `firestarter`'s working tree was confirmed clean (`git status --porcelain` empty) both before and after all three builds — no commit and no file edit was made inside the submodule, per this plan's scope.
- Every figure this plan recorded (the fork verification, the cold baseline, the provenance table) is a host-compiler or AVR-build-toolchain measurement; no AT28C part was involved anywhere in this plan. Like every artifact this phase produces, the page-size seam this plan begins measuring is **software-proven and unvalidated on silicon**.

## Task Commits

| Task | Commit | Repo | Description |
|------|--------|------|-------------|
| 1 | (none — branch creation only, nothing to stage) | firestarter | Forked `gsd/v1.32-at28c-write-path-root-cause-report-provenance` off `origin/beta`, verified by 5 content checks |
| 2 | `0b108c35` | meta | Committed 3 cold pre-edit AVR baseline transcripts |
| 3 | `35cbe5c3` | meta | Created `149-PAGE-SIZE.md` skeleton with fork point and D-01 evidence |

## Deviations from Plan

None — plan executed exactly as written. All predicted figures (24920/24970/27002 flash, 1573/1579/2014 RAM, zero warnings) matched the cold capture exactly, so no "inherited from the v1.31 merge" finding was needed.

## Requirement Status

Per this phase's `planner_decisions`, PGSZ-04 and PGSZ-05 are contributed to by this plan but **not** marked complete — no `PGSZ-0N` checkbox or traceability row was touched in `REQUIREMENTS.md` or `ROADMAP.md`. Plan 08 alone flips all five PGSZ requirements once the whole-phase gate is green.

## Self-Check: PASSED

- FOUND: `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-baseline-cold-uno.log`
- FOUND: `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-baseline-cold-uno328pb.log`
- FOUND: `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-baseline-cold-leonardo.log`
- FOUND: `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md`
- FOUND commit: `0b108c35` (meta)
- FOUND commit: `35cbe5c3` (meta)
- CONFIRMED: `firestarter` on `gsd/v1.32-at28c-write-path-root-cause-report-provenance` @ `7f6afc65be2022575989772cc0a5945611741831`, working tree clean
