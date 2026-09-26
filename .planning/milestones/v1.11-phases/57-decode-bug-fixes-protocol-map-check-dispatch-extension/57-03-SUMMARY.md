---
phase: 57-decode-bug-fixes-protocol-map-check-dispatch-extension
plan: "03"
subsystem: database
tags: [python, chip_database, build_db, check_dispatch, infoic, baseline-diff, syrupy, pytest]

# Dependency graph
requires:
  - phase: 57-01
    provides: "Corrected build_db.py with all four decode bug fixes (BUG-1..4)"
  - phase: 57-02
    provides: "Extended check_dispatch.py with full-class VPP-safety guard (GATE-03)"
  - phase: 56-01
    provides: "tools/baseline/chip_database.baseline.json — Phase 56 pre-milestone snapshot for before/after diffing"
provides:
  - "Regenerated firestarter/data/chip_database.json from corrected decode pipeline (734 chips, live upstream fetch)"
  - "Baseline diff proving only pulse_duration + vcc/vdd field classes changed; zero algorithm/pinout/vpp_mv/type diffs; zero chips added/removed"
  - "GATE-03 re-run on regenerated DB: exits 0, 734 chips, 0 violations of all guard classes"
  - "tests/golden/v1.3-COVERAGE-MATRIX.md refreshed (pulse_duration column now shows 100 us for W27C512 family)"
  - "Full suite green: 480 tests, coverage >= 70%, ruff check + format clean"
  - "DEC-03 user-visible surface: firestarter info W27C512 exits 0, shows Pulse delay: 100uS (via separate debug fix 8088141)"
affects: [phase-58, phase-59]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Live upstream fetch via python tools/build_db.py; retry on transient network errors; halt on fetch failure before committing"
    - "Baseline diff by field class (jq / inline Python) to confirm only intended changes landed"

key-files:
  created: []
  modified:
    - "firestarter_app/firestarter/data/chip_database.json — regenerated from corrected build_db.py"
    - "firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md — pulse_duration column refreshed"

key-decisions:
  - "tests/__snapshots__/test_characterization.ambr did NOT require updating — the .ambr snapshots render CLI help/list/search output only, not pulse_duration values; the file that genuinely needed refreshing was tests/golden/v1.3-COVERAGE-MATRIX.md"
  - "test_info_known_chip no longer pins a crash — the vpp-pin TypeError was fixed in parallel debug session (commit 8088141); task scope was DB regeneration + GATE-03 + full suite, not the info crash fix"
  - "Separate debug fix 8088141 on the same branch delivers the DEC-03 CLI surface (firestarter info W27C512 exits 0, 100µS); tracked outside Phase 57 in .planning/debug/firestarter-info-vpp-pin-crash.md"

patterns-established:
  - "Regeneration is wave-2 integration: wave-1 fixes source-only; wave-2 runs build_db + baseline diff + GATE-03 + suite"
  - "Baseline diff must classify every changed chip by field class before committing; unexpected classes halt the task"

requirements-completed: [DEC-02, DEC-03, DEC-04, GATE-03]

# Metrics
duration: ~45min (prior executor tasks) + checkpoint approval
completed: 2026-06-08
---

# Phase 57 Plan 03: DB Regeneration + Baseline Diff + GATE-03 Verification Summary

**Regenerated chip_database.json (734 chips) from corrected build_db.py — W27C512 pulse_duration corrected to 100 us, AT28C256/AT28C64 vcc now "4V", GATE-03 exits clean on regenerated set, 480-test suite green**

## Performance

- **Duration:** ~45 min (Tasks 1-3 by prior executor) + operator checkpoint approval
- **Started:** 2026-06-08 (wave 2, continuation of Phase 57)
- **Completed:** 2026-06-08
- **Tasks:** 4 (3 auto + 1 checkpoint:human-verify — operator approved)
- **Files modified:** 2

## Accomplishments

- Regenerated `firestarter/data/chip_database.json` from the corrected `build_db.py` (live upstream fetch, 734 chips); baseline diff confirmed only the two intended field classes changed
- GATE-03 re-run (`python tools/check_dispatch.py`) against the regenerated chip set exits 0: 734 chips, 0 SRAM→configure_eprom violations, 0 DIP28_2764 violations, 0 vpp-pin Flash/EEPROM violations, 0 wire-key regressions
- Full pytest suite green (480 tests), coverage >= 70%, ruff check + format --check clean on all touched files

## Baseline Diff Summary (regenerated vs tools/baseline/chip_database.baseline.json)

| Field class | Chips changed | Notes |
|---|---|---|
| `programming.pulse_duration` | 252 | Protocols 0x07/0x0B: 10000 us → 100 us (BUG-2 fix); W27C512 confirmed 100 us |
| `electrical.vcc` | 369 | vcc/vdd un-swap (BUG-3) + new nibble 0x02/0x03 decode (BUG-1) |
| `electrical.vdd` | 315 | Same causes as vcc |
| `programming.algorithm` | 0 | No unexpected changes |
| `pinout` | 0 | No unexpected changes |
| `electrical.vpp_mv` | 0 | No unexpected changes |
| `electrical.type` | 0 | No unexpected changes |
| Chips added | 0 | Total stays at 734 |
| Chips removed | 0 | Total stays at 734 |

**AT28C256 / AT28C64 spot-check:** `electrical.vcc` changed from "5V" to "4V"; `electrical.vdd` stays "5V". This confirms the BUG-1 benefit — nibble 0x02 (4V) now decodes correctly; these chips previously defaulted to 5V due to the missing VCC_VOLTAGES entry.

## Task Commits

1. **Task 1: Regenerate chip_database.json and diff against the Phase 56 baseline** — `12286df` (feat)
2. **Task 2: Re-run GATE-03 and refresh snapshot/golden against the regenerated DB** — `914919e` (feat)
3. **Task 3: Full suite + ruff gate green** — `914919e` (included in Task 2 commit — suite run confirmed clean in same session)
4. **Task 4: Checkpoint:human-verify — operator approved** (no code commit; operator approved the DEC-03 CLI surface and baseline diff)

## Files Created/Modified

- `firestarter_app/firestarter/data/chip_database.json` — Regenerated from corrected build_db.py; 734 chips; W27C512 pulse_duration = "100 us"; AT28C256/AT28C64 vcc = "4V"
- `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` — Pulse Duration column refreshed to show "100 us" for W27C512-family chips (was "10000 us" in the pre-Phase-57 golden)

## Decisions Made

- **Deviation on files_modified:** The plan's `files_modified` frontmatter listed `tests/__snapshots__/test_characterization.ambr` as the snapshot to refresh. At execution time, that file did NOT require updating — the `.ambr` characterization snapshots render CLI help/list/search output and a pinned-crash case; none of them contain pulse_duration values. The file that genuinely needed refreshing was `tests/golden/v1.3-COVERAGE-MATRIX.md`, which carries a per-chip Pulse Duration column. The plan's Task 2 action correctly identified this; the `.ambr` deviation is documented below.

- **Separate debug fix 8088141:** The plan text stated that `test_info_known_chip` pins an existing `firestarter info W27C512` crash that is out of scope for Phase 57. That crash was fixed in a separate debug session (commit 8088141 on the same branch: `fix(info): resolve vpp-pin TypeError in ic_layout and pulse_duration mapping`). As a result, the DEC-03 CLI surface (`firestarter info W27C512` exits 0 and displays "Pulse delay: 100µS") was completed by debug fix 8088141, tracked outside Phase 57 in `.planning/debug/firestarter-info-vpp-pin-crash.md`. Phase 57 plan 03's own scope — DB regeneration + baseline diff + GATE-03 re-run + full suite — all passed independently.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Snapshot file to refresh was tests/golden/v1.3-COVERAGE-MATRIX.md, not test_characterization.ambr**
- **Found during:** Task 2 (Re-run GATE-03 and refresh snapshots)
- **Issue:** The plan's `files_modified` frontmatter and Task 2 action cited `tests/__snapshots__/test_characterization.ambr` as the snapshot requiring refresh. At execution time the `.ambr` file did NOT need updating — it renders only CLI help/list/search output, not pulse_duration values. The file that actually required refreshing was `tests/golden/v1.3-COVERAGE-MATRIX.md`, which carries a per-chip Pulse Duration column auto-generated by `tools/audit_coverage_matrix.py` and referenced in the plan's Task 2 action text.
- **Fix:** Refreshed `tests/golden/v1.3-COVERAGE-MATRIX.md` instead; confirmed the `.ambr` file byte-identical (no spurious changes). The plan's Task 2 body already called this out under "do NOT blanket-update if a non-pulse_duration / non-voltage line changed."
- **Files modified:** `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md`
- **Verification:** `git diff tests/__snapshots__/test_characterization.ambr` showed no changes; test_characterization.py passed after the golden refresh
- **Committed in:** 914919e (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — wrong target file in plan frontmatter; actual refresh target correctly identified from plan action text and execution behavior)
**Impact on plan:** The plan's acceptance criteria were fully met. The deviation was in the frontmatter filename listing, not in the intended outcomes. No scope creep.

## Issues Encountered

None beyond the deviation documented above. The live upstream fetch completed successfully (no retry needed). Coverage stayed above 70% floor without adding new tests (the Phase 57-01 decoder tests already covered the new branches).

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. The regeneration uses the existing requests/upstream infoic.xml fetch path already present in `build_db.py` from prior phases. GATE-03 confirmed no new VPP-routing exposure in the regenerated set.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 57 complete. All four decode bugs are fixed in `build_db.py` (Phase 57-01), GATE-03 is extended to full-class VPP guard (Phase 57-02), and the corrected DB is regenerated and verified (this plan).
- Phase 58 (Pinout Re-derivation + 24-pin EEPROM Unblock) is unblocked: corrected field values (voltages, flags, protocol) are now in the regenerated DB; GATE-03 guard is in place before any re-derivation changes land.
- Requirements DEC-02, DEC-03, DEC-04, and GATE-03 are complete.

---
*Phase: 57-decode-bug-fixes-protocol-map-check-dispatch-extension*
*Completed: 2026-06-08*
