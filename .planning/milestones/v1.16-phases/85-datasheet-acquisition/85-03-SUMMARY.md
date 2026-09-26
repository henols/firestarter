---
phase: 85-datasheet-acquisition
plan: 03
subsystem: datasheets
tags: [datasheets, readme, index, provenance, dsheet-03, safe-05, phase-gate]

requires:
  - phase: 85-02
    provides: 17 committed PDFs across 12 bucket folders + provenance table for README authoring

provides:
  - "DSHEET-03: datasheets/README.md — 12-bucket index with hex/name/handler/filename/on-hand-status/provenance"
  - "Phase-gate datasheets-check.sh: PASS (exit 0)"
  - "All 6 phantom/infeasible exclusions named in README (0x35/0x39/0x11/0x2A/0x2B/0x2C)"
  - "D-02/D-03 sourcing policy + 2516 no-DB-entry note documented"

affects: [86-naming-pass, 87-golden-traces, 89-bench-ledger]

tech-stack:
  added: []
  patterns:
    - "README-as-index: one row per bucket folder (12 rows) + per-file provenance table (17 rows)"
    - "Substitute flag taxonomy: exact / exact-family / family-substitute / substitute / data-book"
    - "SAFE-05 staging: explicit git add datasheets/README.md; git diff --cached verified before commit"

key-files:
  created:
    - firestarter/datasheets/README.md
  modified: []

key-decisions:
  - "README row granularity: one row per bucket (12 rows) with per-file provenance table below — matches research recommendation; cleaner than 17 flat rows"
  - "Substitute flag taxonomy: 5 values (exact / exact-family / family-substitute / substitute / data-book) to precisely describe each of the 3 D-02 fallbacks and the X88C64 data-book"
  - "WARN lines from datasheets-check.sh (source URL filenames in provenance table) are expected soft-warnings, not failures — the script exits 0 (PASS)"

requirements-completed: [DSHEET-03, SAFE-05]

duration: 5min
completed: 2026-06-25
---

# Phase 85 Plan 03: README Index + Phase-Gate Summary

**datasheets/README.md authored (DSHEET-03): 12-bucket index with D-08 provenance, 6 exclusions named, D-02/D-03 policy documented; datasheets-check.sh exits 0 (PASS)**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-06-25T14:52:00Z
- **Completed:** 2026-06-25T14:55:54Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Authored `datasheets/README.md` (172 lines) with all required DSHEET-03 content: 12-bucket index table (hex / proposed name / handler / filename(s) / on-hand status / source URL / retrieved / substitute?) + 17-row per-file provenance table + exclusions section + sourcing policy + folder tree
- Named all 6 excluded hex IDs in the Exclusions section: phantom `0x35` (FLASH_EEPROM — ITE EC MCU label) and `0x39` (FLASH_EEPROM2 — no IC2_ALG constant); infeasible `0x11` (FWH/LPC), `0x2A`/`0x2B`/`0x2C` (GAL/PLD/PIC)
- Documented D-02 sourcing policy and the 3 fetch-time fallbacks (SST27SF512, W27E040, DS1250Y→DS1245Y) with honest substitute flags; documented D-03 MISSING/UNSOURCED policy (no row invokes it)
- Added 2516 no-DB-entry note in the 0x0B row (user-override row, not a committed chip_database.json entry)
- `bash datasheets/datasheets-check.sh` prints `datasheets-check: PASS` and exits 0
- SAFE-05 invariant held: only `datasheets/README.md` staged and committed (verified via `git diff --cached --name-only`)

## Task Commits

1. **Task 1: Author datasheets/README.md** — written and verified (all 18 hex IDs present, check script PASS)
2. **Task 2: Run phase-gate and commit** — `45fed04` (docs(85): datasheets README index + phase-gate PASS (DSHEET-03)) inside firestarter sub-repo on v1.16 branch; only `datasheets/README.md` touched

## Files Created/Modified

| File | Action | Notes |
|------|--------|-------|
| `firestarter/datasheets/README.md` | created | 172 lines; DSHEET-03 index + D-08 provenance + exclusions + policy |

## Deviations from Plan

None — plan executed exactly as written.

The WARN lines from `datasheets-check.sh` (e.g., `WARN: README references 1990_Xicor_Data_Book.pdf but no such file found`) are an expected artifact: the check script's grep-for-`.pdf` pattern extracts filenames from source URLs in the provenance table (e.g., the Xicor data book URL contains `1990_Xicor_Data_Book.pdf`). These are soft WARNs, not FAILs; the script still exits 0 (`datasheets-check: PASS`). The acceptance criteria specifies the WARN line must be empty for README→file references, which holds for all 17 committed PDF filenames — none of the WARNs match a committed filename.

## Phase 85 Completion

Phase 85 (Datasheet Acquisition) is now complete:

| Plan | Name | Status | Commit |
|------|------|--------|--------|
| 85-01 | Wave-0 Scaffold | complete | `11a7c7f` |
| 85-02 | PDF Download (DSHEET-01/02) | complete | `83313fc` |
| 85-03 | README Index (DSHEET-03) | complete | `45fed04` |

All 4 phase requirements fulfilled: DSHEET-01 (11 on-hand PDFs), DSHEET-02 (6 no-silicon PDFs), DSHEET-03 (README index), SAFE-05 (no new deps, only datasheets/ artifacts).

## Known Stubs

None — README indexes real committed files with honest provenance. No placeholder rows, no TODO entries, no fabricated URLs.

## Threat Flags

None — static-asset phase, zero executable surface, zero input parsing. T-85-SC1 mitigated in Plan 02 (all 17 PDFs passed %PDF magic + size>1k check before commit). The README is a static markdown document; no security surface.

## Self-Check: PASSED

- `firestarter/datasheets/README.md` — FOUND (172 lines)
- Commit `45fed04` in firestarter sub-repo on v1.16 branch — VERIFIED (datasheets/README.md only)
- `bash datasheets/datasheets-check.sh` exits 0 — VERIFIED (PHASE-GATE-PASS)
- All 18 hex IDs in README (12 bucket + 6 exclusion) — VERIFIED

---
*Phase: 85-datasheet-acquisition*
*Completed: 2026-06-25*
