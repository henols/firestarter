---
phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-co
plan: "04"
subsystem: meta-repo
tags: [decode-audit, traceability, documentation, SC#1, D-41, D-42]
dependency_graph:
  requires: ["84-01", "84-02", "84-03"]
  provides: [SC1-consolidated-decode-audit, D41-traceability-honest]
  affects:
    - .planning/v1.15/DECODE-AUDIT.md
    - .planning/REQUIREMENTS.md
tech_stack:
  added: []
  patterns: [milestone-close-audit, disposition-ledger]
key_files:
  created:
    - .planning/v1.15/DECODE-AUDIT.md
  modified:
    - .planning/REQUIREMENTS.md
decisions:
  - "UV-01..04 checkbox drift (D-41): already corrected in Phase 83 verification commit 3a9f18b; confirmed [x] on all four in the current REQUIREMENTS.md — no additional change needed"
  - "REWR-01/02/04 annotations follow satisfied-by-disposition semantics — STATUS not changed, silicon FAIL/deferral facts added as parenthetical notes in both definition and traceability rows"
  - "SST39SF040 sst-keep observation carried forward verbatim from 84-03 SUMMARY into DECODE-AUDIT Dispositions section (D-40 explicit observation mandate)"
  - "FM1608 fm-fram-full: DECODE-AUDIT records the correction as RESOLVED (84-03 shipped the DB fix)"
metrics:
  duration: "4 minutes"
  completed_date: "2026-06-25"
  tasks: 2
  files_modified: 2
---

# Phase 84 Plan 04: Decode-Correctness Audit + REQUIREMENTS Annotations Summary

**One-liner:** Consolidated 11-chip decode-correctness audit (SC#1) in `.planning/v1.15/DECODE-AUDIT.md` with per-attribute CONFIRMED/MISMATCH verdicts cross-referencing EVIDENCE; REWR-01/02/04 traceability annotated with silicon FAIL/deferral dispositions; UV-01..04 checkbox drift confirmed already corrected (D-41).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Author DECODE-AUDIT.md — SC#1 consolidated 11-chip decode-correctness audit | 75f1662 | .planning/v1.15/DECODE-AUDIT.md (created, 202 lines) |
| 2 | Annotate REWR-01/02/04 silicon dispositions + confirm UV checkbox drift fixed | 1e46e6c | .planning/REQUIREMENTS.md |

## Task 1: DECODE-AUDIT.md (SC#1)

Created `.planning/v1.15/DECODE-AUDIT.md` as the SC#1 standalone milestone-close artifact (D-42). Structure:

**Part 1 — Per-Chip Decode-Correctness Table (11 chips, 5 attributes each):**

All chips cross-referenced to `EVIDENCE.{md,json}` rows.

| Chip | Pinout | VPP | Electrical Type | Algorithm | Size | Overall |
|------|--------|-----|-----------------|-----------|------|---------|
| W27C512 | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | PASS |
| W27E512 | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | FAIL (genuine D-32) |
| SST27SF512 | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | PASS |
| W27E040 | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | FAIL (genuine D-32) |
| ST M27C512 | CONFIRMED | MISMATCH (plan-text 12V vs actual DB 13V) | CONFIRMED | CONFIRMED | CONFIRMED | PASS |
| SST39SF040 | CONFIRMED | CONFIRMED | MISMATCH (sst-keep observation) | CONFIRMED | CONFIRMED | PASS |
| W29C040 | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | FAIL (write-path, pending 84-05) |
| W29C020 | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | PASS |
| FM1608 | CONFIRMED | MISMATCH (vpp_mv artifact, now hidden) | MISMATCH → CORRECTED (SRAM→FRAM, 84-03) | CONFIRMED | CONFIRMED | PASS |
| AM27C020 | CONFIRMED | MISMATCH (plan-text 12V vs actual DB 13V) | CONFIRMED | CONFIRMED | CONFIRMED | ANOMALY (write, pending 84-05) |
| 2516 | Pending | MISMATCH (VPP 15.3V on OE/VPP pin) | CONFIRMED | CONFIRMED | Pending | ANOMALY (read, pending 84-05) |

**Mismatch notes:**
- ST M27C512 and AM27C020 VPP: plan text stated 12V; actual DB is 13V. Plan-text error only — DB is correct. Not a DB defect.
- SST39SF040 electrical type: DB says `Flash/EEPROM`; upstream classification is `Flash`. sst-keep disposition — functionally correct for RURP (FLAG_CAN_ERASE preservation).
- FM1608 electrical type: originally `SRAM`; corrected to `FRAM` in Phase 84-03. Now RESOLVED.
- 2516 VPP: DB records 25V NMOS; bench read shows 15.3V on the shared OE/VPP pin. 0x0B path instability — pending re-bench.

**Part 2 — Dispositions (all five categories):**

1. VPP-skip firmware gate: SHIPPED (Phase 84-01, commit cb947c7, FIX-01 firmware half)
2. FM1608 blank-check host short-circuit: SHIPPED (Phase 84-02, commits e5bfa3a + 4c74b8d, FIX-01 host half)
3. SST39SF040 sst-keep + FM1608 fm-fram-full: Phase 84-03 outcomes recorded; D-40 STOPPED part (SST39SF040) documented as explicit observation
4. W27E512 + W27E040 stuck-bit FAILs: D-32 silicon-limited, NOT FIX-01 material
5. AM27C020 + W29C040 + 2516: RCA-and-defer, PENDING 84-05 bench

**Part 3 — EVIDENCE cross-reference index:** All 11 chips mapped to EVIDENCE.{md,json} cells.

**Part 4 — Bench-pending placeholder table:** 5 items (P1–P5) explicitly labeled "PENDING 84-05" for Plan 84-06 fill-in.

## Task 2: REQUIREMENTS.md Annotations (D-41)

**REWR-01 (definition + traceability):**
- Definition now reads: "*(Silicon outcome: W27C512 PASS + SST27SF512 PASS; W27E512 FAIL — genuine stuck erase bit @0x3d, reads 0x7F want 0xFF, deterministic across N=3 reseats, D-32 silicon-limited...)*"
- Traceability: "Complete *(partial silicon — W27C512 PASS + SST27SF512 PASS; W27E512 FAIL: genuine stuck bit @0x3d, silicon-limited D-32, not a DB/algo fault)*"

**REWR-02 (definition + traceability):**
- Definition now reads: "*(Silicon outcome: W27E040 FAIL — genuine stuck erase bit @0x7db, reads 0xEF want 0xFF, deterministic across N=2 reseats, D-32 silicon-limited. No positive 0x08 write PASS...deferred FUT-05...)*"
- Traceability: "Complete *(satisfied-by-disposition — W27E040 FAIL: genuine stuck bit @0x7db, silicon-limited D-32; no positive 0x08 PASS; deferred FUT-05, needs a functional 0x08 chip)*"

**REWR-04 (definition + traceability):**
- Definition now reads: "*(Silicon outcome: W29C020 PASS — FLAG_CAN_ERASE Flash/EEPROM branch first silicon confirmation; W29C040 FAIL — flash4 256B page-write timeout...W29C040 disposition: handed to Phase 84 FIX-01 re-bench pending 84-05...)*"
- Traceability: "Complete *(partial silicon — W29C020 PASS (Flash/EEPROM auto-erase silicon proof); W29C040 FAIL: flash4 256B page-write timeout, handed to Phase 84 FIX-01 re-bench; disposition pending 84-05)*"

**UV-01..04 checkbox drift:** Confirmed already corrected in Phase 83 verification commit `3a9f18b`. All four show `[x]` in both definition and traceability rows. No additional change needed.

**No requirement STATUS changed:** `[x]` marks and traceability `Complete` designations are preserved — only annotation text added.

## Deviations from Plan

**1. [Rule 2 - Missing context] UV-01..04 checkbox drift pre-corrected — D-41 partially pre-satisfied**

- **Found during:** Task 2 verification
- **Issue:** The plan tasks said to fix UV-01..04 definition checkboxes from `[ ]` to `[x]`. But checking the actual file shows they were already `[x]` (corrected in Phase 83 verification commit `3a9f18b: docs(phase-83): verification PASSED 5/5 + tick UV-01..04 checkboxes`).
- **Resolution:** Confirmed as already correct. Task 2 noted this finding explicitly and did not make a redundant change. The D-41 annotation work (REWR-01/02/04) was performed as specified.
- **Files modified:** None extra

## Verification Results

- `test -f .planning/v1.15/DECODE-AUDIT.md` → EXISTS ✓
- `grep -c "CONFIRMED\|MISMATCH\|disposition\|EVIDENCE" DECODE-AUDIT.md` → 27 occurrences ✓
- All 11 chips appear in the document (67 chip-name hits) ✓
- Dispositions section: 5 categories covered (22 hits including VPP-Skip/FM1608/sst-keep/D-32/PENDING) ✓
- REWR-01/02/04 annotated in definition + traceability rows ✓
- `grep -c "^- \[x\] \*\*UV-0" REQUIREMENTS.md` → 4 (all UV checkboxes correctly `[x]`) ✓
- No requirement STATUS changed ✓

## Success Criteria Assessment

- [x] SC#1 consolidated decode audit delivered as a standalone doc (D-42): `.planning/v1.15/DECODE-AUDIT.md`, 202 lines
- [x] DECODE-AUDIT.md lists all 11 chips with per-attribute verdicts cross-referencing EVIDENCE
- [x] Dispositions section covers all five categories (VPP-skip shipped; FM1608 shipped; relabel/STOP outcome; stuck-bit D-32 silicon-limited; 0x08/flash4/2516 RCA-and-defer pending 84-05)
- [x] D-40 STOPped part (SST39SF040 sst-keep) appears as explicit observation in Dispositions
- [x] Bench-pending placeholders marked clearly for 84-06 fill-in
- [x] REWR-01/02/04 annotated with silicon FAIL/deferral dispositions in definition + traceability
- [x] UV-01..04 checkbox drift: D-41 confirmed resolved (pre-corrected in Phase 83)
- [x] No requirement STATUS changed (annotations only)
- [x] Milestone-audit documentation-accuracy tech-debt closed (D-41)

## Known Stubs

None — this plan produces documentation artifacts only. The "PENDING 84-05" placeholders in DECODE-AUDIT.md are intentional design: they are bench outcomes from the next plan's hardware session, not documentation stubs.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes. Documentation-only plan (no code changes). T-84-11 (REWR overstated traceability) mitigated by D-41 annotations. T-84-12 (D-40 STOPped part omitted) mitigated — SST39SF040 sst-keep recorded as explicit observation in DECODE-AUDIT.md Dispositions.

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| `.planning/v1.15/DECODE-AUDIT.md` exists | FOUND ✓ |
| `.planning/REQUIREMENTS.md` exists | FOUND ✓ |
| commit 75f1662 (Task 1) | FOUND in git log ✓ |
| commit 1e46e6c (Task 2) | FOUND in git log ✓ |
| DECODE-AUDIT.md min_lines ≥ 40 (actual: 202) | PASSED ✓ |
| DECODE-AUDIT.md contains "REWR-04" | FOUND ✓ |
| DECODE-AUDIT.md cross-references EVIDENCE | FOUND (27 occurrences) ✓ |
| REQUIREMENTS.md contains "REWR-04" | FOUND ✓ |
| No requirement [x] status changed to [ ] | CONFIRMED ✓ |
