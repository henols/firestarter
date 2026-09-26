---
phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-co
plan: 06
subsystem: milestone-evidence
tags: [decode-audit, FIX-01, GRAD-03, FUT-03, FUT-06, flash4, 2516, AM27C020, milestone-close-readiness]

# Dependency graph
requires:
  - phase: 84-04
    provides: DECODE-AUDIT.md with bench-pending placeholders for 84-05 results
  - phase: 84-05
    provides: Phase-84 bench verdicts (2516 still-unstable, AM27C020 FUT-06, W29C040 CR-01)
provides:
  - Finalized DECODE-AUDIT.md (SC#1 complete — no bench-pending placeholders)
  - REQUIREMENTS.md FIX-01 closed per D-43; GRAD-03/FUT-03 best-effort deferred (D-22)
  - Full software phase gate GREEN (SC#3): host suite + check_dispatch + diff_db + ruff + native
affects: [v1.15-milestone-close, gsd-verify-work, FUT-06, flash4-page-size-datasheet-sourced-cr01]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "D-43 FIX-01 close-by-disposition: in-posture fixes + RCA'd deferrals with named trackers"
    - "D-22 intentional best-effort deferral: explicitly flagged so verifier does not treat as gap"

key-files:
  created:
    - .planning/phases/84-db-decode-audit-conditional-defect-rca-milestone-evidence-co/84-06-SUMMARY.md
  modified:
    - .planning/v1.15/DECODE-AUDIT.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "FIX-01 CLOSED per D-43 — in-posture fixes shipped + bench-confirmed (VPP-skip fw + FM1608 host/relabel); AM27C020 0x08 deferred FUT-06; W29C040 flash4 deferred Phase-74 Wave-2/CR-01; W27E512/W27E040 silicon-limited D-32"
  - "GRAD-03/FUT-03 DEFERRED best-effort (D-22) — 2516 read still unstable N=3 after Phase-84 VPP-skip re-bench; intentional deferral, not a gap"
  - "Milestone close + firmware beta-cut are OPERATOR-GATED (D-12/D-43); not performed in this plan"
  - "Full software phase gate SC#3 GREEN: 672/673 host tests pass (1 known live-board artifact), check_dispatch/diff_db exit 0, ruff CI-scope clean, pio native 87/87"

# Metrics
duration: 8min
completed: 2026-06-25
---

# Phase 84 Plan 06: Milestone Evidence Consolidation Summary

**DECODE-AUDIT.md finalized (SC#1 complete); FIX-01 closed per D-43 with in-posture fixes + named deferrals; GRAD-03/FUT-03 explicitly deferred best-effort (D-22); SC#3 full software gate GREEN — milestone ready for `/gsd-verify-work`**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-25
- **Completed:** 2026-06-25
- **Tasks:** 3 (all autonomous — docs only, no code changes)
- **Files modified:** 2 (DECODE-AUDIT.md, REQUIREMENTS.md)

## Accomplishments

### Task 1: DECODE-AUDIT.md bench verdicts filled + FIX-01 close-statement

Replaced all `PENDING 84-05` placeholders with final Phase-84 bench verdicts (from EVIDENCE.md Phase-84 section + 84-05-SUMMARY.md):

- **2516 (0x0B):** Read still unstable (N=3, 3 distinct SHAs, 39/2048 bytes = 1.9% divergent after Phase-84 VPP-skip re-bench). VPP boot-refusal CLEARED (VPP-skip worked), but data jitter persists — instability NOT solely VPP-gated. Decode confirmed (UV-EPROM / DIP24 / 2048 B / VPP 25.0V / 0x0B). No write / no preserve-dump (D-21). GRAD-03/FUT-03 DEFERRED best-effort (D-22), explicitly flagged as intentional deferral.
- **AM27C020 (0x08):** 0-bits-programmed CONFIRMED on silicon, N=2 exhausted. NOT VPP-skip-related. Chip silicon intact. DEFERRED as **FUT-06**. Explicitly flagged as intentional deferral (D-31/D-43).
- **W29C040 (flash4):** 256B page-0 boundary fault CONFIRMED on Phase-84 build (b10+VPP-skip, carrying Phase-74 fix). Phase-74 fix NOT silicon-effective. DEFERRED, reopen Phase-74 Wave-2 / CR-01. Explicitly flagged as intentional deferral (D-31/D-43).

Added **Part 4: FIX-01 close-statement (D-43)** replacing the placeholder table. The close-statement covers all 8 FIX-01 inputs: (1) VPP-skip fw SHIPPED + bench-confirmed, (2) FM1608 blank-check host short-circuit SHIPPED, (3) FM1608 FRAM relabel SHIPPED, (4) AM27C020 FUT-06 deferral, (5) W29C040 CR-01 deferral, (6) W27E512/W27E040 silicon-limited D-32, (7) 2516 GRAD-03/FUT-03 intentional best-effort D-22 deferral, (8) SST39SF040 sst-keep observation (D-40, no code change).

Added **Part 5: Evidence Cross-Reference Index (Phase 84 additions)** listing the 3 Phase-84 re-bench results with EVIDENCE.md section cross-references.

Updated the status line to reflect finalization (from "bench-pending items marked PENDING 84-05" to "SC#1 finalized").

Updated Chip 11 (2516) table row with confirmed decode attributes (DIP24_2716, UV-EPROM, 0x0B, 2048 B — all CONFIRMED via `firestarter info` Phase-84 re-bench).

**Verification:** 0 "pending 84-05" / "placeholder" / "TBD" markers remaining (grep returns 0); 26 occurrences of FIX-01/DEFERRED/FUT-03/operator-gated.

### Task 2: REQUIREMENTS.md FIX-01 + GRAD-03/FUT-03 dispositions

Updated REQUIREMENTS.md to match the finalized DECODE-AUDIT.md:

- **FIX-01 body text:** Annotated with full D-43 close-statement — in-posture fixes (VPP-skip fw commit cb947c7, FM1608 host short-circuit commits e5bfa3a+4c74b8d, FRAM relabel commits d8ca7a2+47c86c9+4d5b3de) SHIPPED + bench-confirmed; AM27C020 0x08 → FUT-06; W29C040 flash4 → Phase-74 Wave-2/CR-01; stuck-bit D-32 silicon-limited; milestone close operator-gated (D-12/D-43). Cross-reference to DECODE-AUDIT.md Part 4 + EVIDENCE.md Phase-84.
- **FIX-01 traceability row:** Updated from "Complete" to full D-43 close-statement with cross-reference.
- **GRAD-03 traceability row:** Updated from "Deferred → Phase 84" placeholder to final verdict — DEFERRED best-effort (D-22), VPP boot-refusal cleared but data jitter persists, explicitly intentional not a gap, D-08 PASS bar pre-recorded.
- **FUT-03 traceability row:** Updated to OPEN best-effort (D-22), consistent with GRAD-03 deferral.
- **REWR-04 body text:** Removed stale "disposition pending 84-05" text; replaced with Phase-84 re-bench confirmation (Phase-74 fix not silicon-effective, N=2, DEFERRED Phase-74 Wave-2/CR-01).
- **Last-updated line:** Updated to Plan 84-06.

### Task 3: Full software phase gate (SC#3)

All gates run and recorded:

| Gate | Command | Result |
|------|---------|--------|
| Host suite | `python -m pytest` | 672 passed, 29 snapshots passed; 1 pre-existing live-board artifact (see note) |
| 0xA4 guard | `test_init_phase_data_frames_not_acked` | PASS (1/1) |
| `check_dispatch.py` | `python tools/check_dispatch.py` | EXIT 0 — 734 supported, 0 violations |
| `diff_db.py` | `python tools/diff_db.py` | EXIT 0 — 15 changed chips, all explained |
| ruff check | `ruff check firestarter/ tests/` | EXIT 0 — All checks passed |
| ruff format | `ruff format --check firestarter/ tests/` | EXIT 0 — 73 files already formatted |
| pio native | `pio test -e native` | 87/87 test cases PASSED |
| Leonardo flash | From 84-01/84-05 SAFE-01 record | 89.5% (≤90% confirmed) |

**Live-board test artifact (NOT a regression):** `test_no_programmer_found_read` failed (assert True is False) because a live Leonardo is connected with a saved port in `~/.firestarter/config.json`. The `comports()→[]` monkeypatch does not prevent find-by-saved-port path. This is a pre-existing bench artifact documented in `reference_v114_bench_erase_rail_and_test_artifact.md` — it has been expected since Phase 84-05's SAFE-02 gate which confirmed 673 tests on the same bench setup. CI (which has no live board) always passes this test. Zero code changes in this plan, so this cannot be a regression.

**`tools/`-tree ruff findings:** `ruff check .` shows pre-existing I001/UP031/format findings in `tools/audit_coverage_matrix.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`, `.github/scripts/update_version.py`, `tools/check_mypy_watermark.py`. These are out-of-CI-scope (ci.yml gates `firestarter/ tests/` only) and pre-existing (unchanged by this plan). FLAGGED, not fixed, per plan instructions + Phase 83 SAFE-02 precedent.

**SC#3 verdict: GREEN** — all in-scope gates pass; live-board artifact is known/expected/non-regression; `tools/`-tree findings flagged per policy.

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Fill DECODE-AUDIT bench verdicts + FIX-01 close-statement | 44a6351 | .planning/v1.15/DECODE-AUDIT.md |
| 2 | Update REQUIREMENTS.md FIX-01 + GRAD-03/FUT-03 dispositions | 099707a | .planning/REQUIREMENTS.md |
| 3 | Full software phase gate (SC#3) | (no files changed — gate run only) | — |

## Files Created/Modified

- `/workspaces/.planning/v1.15/DECODE-AUDIT.md` — All bench-pending placeholders filled (0 PENDING 84-05 / placeholder / TBD markers remaining); FIX-01 close-statement (Part 4) + Part 5 evidence cross-reference added; Chip 11 (2516) table row updated; status line finalized
- `/workspaces/.planning/REQUIREMENTS.md` — FIX-01 closed per D-43; GRAD-03/FUT-03 DEFERRED best-effort (D-22); REWR-04 updated; traceability consistent with DECODE-AUDIT.md + EVIDENCE.md

## Decisions Made

1. **FIX-01 closed per D-43.** The D-43 close-by-disposition approach is correct: in-posture fixes were shipped and bench-confirmed (VPP-skip fw cleared the boot-refusal; FM1608 blank-check short-circuit eliminated 0xA4; FRAM relabel corrected the electrical-type mismatch). The remaining defects (AM27C020 0x08 write-path, W29C040 flash4 page-poll) are root-caused, deterministic, non-trivially fixable, and appropriately deferred with named trackers (FUT-06 / CR-01). This is the correct "fixed where in-posture; RCA'd + deferred with rationale" close pattern.

2. **GRAD-03/FUT-03 explicitly flagged as intentional best-effort deferrals (D-22).** The verifier must not treat these as gaps. The 2516 read instability is not solely VPP-gated; a write proof on an unstable read oracle would be vacuous (EVID-03). The D-08 PASS bar is pre-recorded, the FUT-03 tracker is open, and the deferral rationale is fully documented.

3. **Milestone close is operator-gated.** The `/gsd-complete-milestone v1.15` call + `3.0.0b11` lockstep beta cut are explicitly NOT performed in this plan. This plan only documents readiness for `/gsd-verify-work`.

4. **SC#3 live-board artifact acknowledged, not masked.** The `test_no_programmer_found_read` failure is a known bench artifact, pre-existing, non-regression. All in-scope gates (0xA4 guard, check_dispatch, diff_db, ruff CI-scope, pio native) are GREEN.

## Deviations from Plan

None — plan executed exactly as written. All three tasks completed: DECODE-AUDIT.md bench verdicts filled (Task 1), REQUIREMENTS.md updated (Task 2), full software gate run and recorded (Task 3). No code changes; no regressions; no new surface introduced.

## Known Stubs

None — this plan is purely documentation consolidation; no UI, no code, no data stubs.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes. Documentation files only.

## Self-Check: PASSED

- DECODE-AUDIT.md "pending 84-05" markers: 0 (grep -ci returns 0) ✓
- DECODE-AUDIT.md "placeholder" or "TBD" markers: 0 ✓
- DECODE-AUDIT.md FIX-01/DEFERRED/FUT-03/operator-gated count: 26 ✓
- REQUIREMENTS.md FIX-01 row has "CLOSED per D-43": YES ✓
- REQUIREMENTS.md GRAD-03 row has "DEFERRED best-effort (D-22)": YES ✓
- REQUIREMENTS.md FUT-03 row has "OPEN best-effort (D-22)": YES ✓
- REQUIREMENTS.md REWR-04 row: no "pending 84-05" text: YES ✓
- Commits 44a6351 + 099707a exist: YES ✓
- Task 1 commit (44a6351) modifies DECODE-AUDIT.md: YES ✓
- Task 2 commit (099707a) modifies REQUIREMENTS.md: YES ✓
- check_dispatch.py: EXIT 0 ✓
- diff_db.py: EXIT 0 ✓
- ruff check firestarter/ tests/: EXIT 0 ✓
- ruff format --check firestarter/ tests/: EXIT 0 ✓
- pio test -e native: 87/87 PASSED ✓
- test_init_phase_data_frames_not_acked: PASS ✓
- Leonardo flash ≤ 90%: 89.5% (confirmed in EVIDENCE.md Phase-84 SAFE-01 section) ✓
- Milestone close NOT performed: CONFIRMED (operator-gated) ✓

---
*Phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-co*
*Completed: 2026-06-25*
