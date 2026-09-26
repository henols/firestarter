---
phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half
plan: 06
subsystem: testing
tags: [non-regression, sweep, catalog, gate-checklist, sdp, cross-repo]

# Dependency graph
requires:
  - phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half (plan 05)
    provides: "112/112 native suite, OBS-02/OBS-03 Complete, three _shared/ blob SHAs, resolved gate window ranges (222-238/272-285), the running host baseline (974 passed/1 pre-existing failure)"
provides:
  - "118-NONREGRESSION.md: the enumerated 4-id serial-channel exception to OBS-05's byte-identity claim, the 9-row CORRECTION-4 gate table (all PASS), both boards' base-vs-HEAD flash/RAM figures re-derived via a throwaway git worktree at f8d10a5, the 3 _shared/ blob SHAs re-derived, and the deliberately-not-taken section"
  - "OBS-01 and OBS-05 marked Complete in REQUIREMENTS.md"
affects: ["118-07 (Leonardo OBS-04 measurement; this plan's Leonardo flash figure 25680/28672 is the build the measurement plan uploads)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Throwaway git worktree at the phase-base commit to re-derive (not copy) both boards' base flash/RAM figures for the delta computation"

key-files:
  created:
    - .planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-NONREGRESSION.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Split the plan's 8 bulleted gate-checklist items into 9 table rows: gen_sdp_bus_config.py (generator) and test_sdp_bus_config_drift.py (its own pytest) as two separate rows since each has an independent PASS/FAIL; check_dispatch.py and build_db.py kept as one combined row since the plan bullet presents them jointly with a single shared disposition (expected untouched, confirm not assume) and neither has its own dedicated pytest"
  - "Base flash/RAM figures re-derived via a throwaway git worktree checked out at f8d10a5 (built, measured, removed) rather than copied from 118-03-SUMMARY's pre-task baseline -- matched exactly (Leonardo 25528/28672, Uno 23390/32256), confirming the copied figures were valid but the re-derivation satisfies the plan's 're-derived rather than copied' requirement literally"
  - "Recorded the test_no_programmer_found_* divergence with more precision than prior waves: live serial devices (/dev/ttyACM0, /dev/ttyACM1, /dev/ttyUSB0) ARE present in this sweep's environment, yet the pair still passed 2/2 -- so the absence of the second anticipated failure is not explained by 'no board attached' as the plan's own framing suggested; the divergence is recorded honestly as unexplained-by-board-absence rather than force-fit to a convenient story"

requirements-completed: [OBS-01, OBS-05]  # OBS-02/OBS-03 already Complete (set by Plan 118-05), left untouched. OBS-04 explicitly NOT marked -- Plan 118-07 owns it.

coverage:
  - id: D1
    description: "Full sweep executed: native 112/112 (test_eeprom28c_sdp 12/12, no SIGABRT), both board builds with base figures re-derived via throwaway worktree at f8d10a5, all 9 CORRECTION-4 gate rows PASS, host pytest 974 passed/1 pre-existing failure, catalog three-way cmp + both codegen --check gates clean, both regenerate-and-diff legs clean, 3 _shared/ blob SHAs re-derived identical to base"
    requirement: "OBS-01, OBS-05"
    verification:
      - kind: unit
        ref: "cd /workspaces/firestarter && pio test -e native (112/112); pio run -e leonardo -e uno (both SUCCESS, +152 B flash each vs re-derived f8d10a5 base)"
        status: pass
      - kind: unit
        ref: "cd /workspaces/firestarter_app && python -m pytest --tb=no (974 passed, 1 failed -- test_audit_coverage_matrix only)"
        status: pass
    human_judgment: false
  - id: D2
    description: "118-NONREGRESSION.md written with all 8 required sections (OBS-05 claim precisely stated, 4-id serial exception table, bus-stream-unchanged proof, flash/RAM with both phase deltas provenanced, 9-row gate table, 3 known-and-explained conditions, validation ceiling quoted verbatim, 2 deliberately-not-taken items); line-by-line review found no sentence claiming AT28C silicon validation"
    requirement: "OBS-05"
    verification:
      - kind: unit
        ref: ".planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-NONREGRESSION.md (all 8 sections present)"
        status: pass
    human_judgment: false
  - id: D3
    description: "REQUIREMENTS.md updated: OBS-01 and OBS-05 marked Complete (checkbox + traceability table); OBS-04 confirmed left Pending; OBS-02/OBS-03 re-confirmed already Complete from Plan 118-05, not re-derived"
    requirement: "OBS-01, OBS-05"
    verification:
      - kind: unit
        ref: ".planning/REQUIREMENTS.md lines 58-62 and traceability table rows 165-169"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-07-28
status: complete
---

# Phase 118 Plan 06: Non-Regression Sweep + OBS-05 Exception Enumeration Summary

**Ran the full three-repo non-regression sweep (native 112/112, both board builds re-derived via a throwaway worktree at the phase base, all 9 CORRECTION-4 gate rows, full host pytest, catalog three-way identity, golden blob-SHA re-check) and wrote `118-NONREGRESSION.md` — the single artifact enumerating OBS-05's serial-channel exception, the +152 B flash delta against Phase 117's +204 B reference, and both deliberately-not-taken items — closing OBS-01 and OBS-05.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-07-28
- **Completed:** 2026-07-28
- **Tasks:** 2
- **Files modified:** 2 (1 created, 1 modified), meta repo only

## Accomplishments

- **Leg 1 (native suite):** `pio test -e native` — **112/112 passed**, `test_eeprom28c_sdp` **12/12**, zero `SIGABRT`/`ERRORED`/`FAILED` (grep across the full output confirmed, not just the tail summary line).
- **Leg 2 (board builds + flash delta):** Built both boards at HEAD (Leonardo 25680/28672 flash, 89.6%, RAM 1998/2560 unchanged; Uno 23542/32256 flash, 73.0%, RAM 1559/2048 unchanged). **Re-derived the phase-base figures** via a throwaway `git worktree add <scratch-path> f8d10a5`, built both boards there (Leonardo 25528/28672; Uno 23390/32256 — matching the copied figures from 118-03-SUMMARY exactly), then removed the worktree. Delta: **+152 B flash on both boards, +0 B RAM** — reported against Phase 117's measured **+204 B** Leonardo reference (not the research's predicted saving), with both figures' provenance recorded in `118-NONREGRESSION.md` §4.
- **Leg 3 (9-row CORRECTION-4 gate checklist):** All nine rows executed and PASS — `check_no_log_in_sdp_window.py` (PASS, emitter 222-238/poll 272-285), `test_check_no_log_in_sdp_window.py` (7 passed), `test_sdp_table_parity.py` (4 passed), `test_dispatch_mirror.py` (2 passed), `test_sdp_db_invariant.py` (4 passed), `gen_sdp_bus_config.py` (regenerated, zero drift), `test_sdp_bus_config_drift.py` (4 passed), `test_revision_constants_parity.py` (6 passed), `check_dispatch.py` + `build_db.py` (both exit 0, `chip_database.json` byte-unchanged after a live re-fetch-and-regen).
- **Leg 4 (full host pytest):** `974 passed, 1 failed` — only `test_audit_coverage_matrix::test_golden_file_matches` (pre-existing golden drift). **`test_no_programmer_found_read`/`_erase` did NOT fail** (re-run in isolation: 2/2 passed) — notably, this sweep's environment DOES have live serial devices present (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0`), so the divergence from the plan's anticipated two-failure baseline is recorded honestly as unexplained-by-board-absence, not force-fit to a convenient story.
- **Leg 5 (host lint):** `ruff check .` (4 errors) and `ruff format --check .` (4 files) both flagged pre-existing violations, all confirmed via `git diff --name-only 9dd11a9..HEAD` to be **outside this phase's 5-file host diff** — none are `check_no_log_in_sdp_window.py`, `messages.py`, `messages.toml`, or either test/fixture file this phase touched.
- **Leg 6 (catalog three-way identity):** Local `cmp` of all three `messages.toml` copies both exit 0; both sub-repos' `codegen.py --check` PASS (70 messages, version 1); regenerate-and-`git diff --exit-code` clean for both `firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py`. `catalog-sync-check.yml`'s `ref: main` pinning confirmed at lines 33/40 (drifted slightly from the plan's cited 27/38 line numbers but same pinning) — recorded expected-red-until-milestone-merge.
- **Leg 7 (frozen `_shared/` artifacts):** All three blob SHAs re-derived via `git rev-parse f8d10a5:<path>` vs `HEAD:<path>` — identical to Plan 118-05's recorded values.
- **Leg 8 (Python version disclosure):** `python3 --version` → `3.12.13`; `python3.11` absent. Every Python leg in this sweep recorded CI-PENDING/structurally-green under 3.12.13.

## `118-NONREGRESSION.md` — Line-by-Line Validation-Ceiling Review

Reviewed the entire document sentence by sentence before committing. Every claim has code or a
captured byte stream as its subject (a recorded register-trace strobe, a captured serial frame's
id byte, a git blob SHA, a `pio run` size line, a pytest exit code). No sentence claims AT28C
silicon validation, SDP lock/unlock working on real hardware, or a chip's `support_status`
change. `0x0D` stays `UNVERIFIED`; the 84-chip count is not referenced as changed; no
`PROTOCOL-LEDGER` edit was made. **Confirmed: no wording crosses the validation ceiling.**

## Task Commits

Single commit in the meta repo, per the plan's repo mechanics (this plan writes only
`.planning/` paths):

1. **Task 1 (sweep) + Task 2 (write `118-NONREGRESSION.md` + update REQUIREMENTS.md)** —
   `e48cf8d` — `docs(118-06): record the Phase 118 non-regression sweep and the enumerated OBS-05 exception (OBS-01, OBS-05)`

No commits made inside either submodule — `git -C firestarter status --short` clean;
`git -C firestarter_app status --short` shows only the same pre-existing unrelated dirty files
noted in every prior Phase 118 wave (`.gitignore`, `.coverage`, `.planning/config.json`,
`SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh`). Meta `firestarter`/`firestarter_app`
gitlinks left unstaged (no-in-milestone-bump convention).

## Files Created/Modified

- `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-NONREGRESSION.md` — created; all 8 required sections.
- `.planning/REQUIREMENTS.md` — OBS-01 and OBS-05 marked Complete (checkbox lines 58/62, traceability table rows 165/169); OBS-02/OBS-03/OBS-04 rows left as-is (Complete/Complete/Pending).

## Decisions Made

- **9-row gate table construction** — see `key-decisions` in the frontmatter for the exact split rationale (gen_sdp_bus_config.py + its drift test as 2 rows; check_dispatch.py + build_db.py as 1 combined row).
- **Base flash/RAM figures re-derived via a throwaway git worktree** rather than copied from `118-03-SUMMARY.md`, satisfying the plan's literal "re-derived rather than copied" requirement — see `key-decisions`.
- **`test_no_programmer_found_*` divergence recorded with the live-board-present detail** rather than the "no board attached" explanation prior waves implicitly suggested — see `key-decisions`.

## Deviations from Plan

None — plan executed exactly as written. The gate-checklist row-count reconciliation (8 bullets → 9 table rows) is a faithful reading of the plan's own "nine rows" acceptance-criteria language against its 8-bullet action text, not a deviation from either.

## Issues Encountered

None. All nine gate rows, all pytest legs, both board builds, and the catalog identity checks passed on the first run. No auto-fixes, no blockers, no architectural questions.

## Host Repo Untouched (confirmed, not assumed)

`git -C /workspaces/firestarter_app status --short` after running the full sweep (9 gate-checklist commands, full pytest suite, ruff, build_db.py, codegen regen) shows only the same pre-existing unrelated dirty files noted in every prior Phase 118 wave — zero files added or modified by this plan.

## STATE.md Tooling Defect Check

Per the plan's `<state_tracking>` instructions, hand-verified after the state-mutating calls in the State Updates section below: `current_phase_name` and `progress.total_plans`/`progress.percent` checked against the known em-dash/parenthetical-mangling and percent-reversion defects documented in STATE.md's own note block. See the State Updates section for the exact outcome and any hand-correction applied.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- OBS-01 and OBS-05 are Complete in `.planning/REQUIREMENTS.md`; OBS-02/OBS-03 remain Complete (unchanged); OBS-04 remains Pending — Plan 118-07's Leonardo measurement.
- Plan 118-07 depends on this plan's recorded Leonardo flash figure (**25680/28672 bytes, 89.6%**) matching the build it uploads — no firmware or config file was touched by this plan, so the figure Plan 118-04 originally produced (and this plan re-confirmed) is exactly what 118-07 will flash.
- No blockers for Plan 118-07.

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-NONREGRESSION.md`
- FOUND: commit `e48cf8d` in meta repo (`git log --oneline --all`)
- FOUND: `.planning/REQUIREMENTS.md` shows OBS-01 and OBS-05 as `[x]` / Complete

---
*Phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half*
*Completed: 2026-07-28*
