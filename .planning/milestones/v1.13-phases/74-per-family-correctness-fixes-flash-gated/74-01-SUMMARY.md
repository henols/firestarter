---
phase: 74
plan: 01
subsystem: documentation / comment reconciliation
tags: [fix-01, fix-03, sram, flash4, 0x39, 0x35, closure, evidence-based]
dependency_graph:
  requires:
    - 73-04 (VAL-06 FM1608 bench run — table-stakes-PASS verdict + val-results artifacts)
    - 72-01 (GAP-5 protocol enumeration — 0 DB chips on 0x39/0x35 confirmed)
  provides:
    - 74-FIX01-CLOSURE.md (FIX-01 closed not-needed with evidence citations)
    - firestarter/CLAUDE.md (0x35/0x39 symmetric phantom framing)
    - database.py / ic_layout.py (cross-repo forward-compat note)
  affects:
    - Phase 74 Plans 02 and 03 (FIX-01 and FIX-03 resolved; only FIX-02 flash4 work remains)
tech_stack:
  added: []
  patterns:
    - evidence-based closure (documentation replaces implementation when bench proves no defect)
    - cross-repo comment parity (firmware CLAUDE.md + host database.py + ic_layout.py all tell the same story)
key_files:
  created:
    - .planning/phases/74-per-family-correctness-fixes-flash-gated/74-FIX01-CLOSURE.md
  modified:
    - firestarter/CLAUDE.md
    - firestarter_app/firestarter/database.py
    - firestarter_app/firestarter/ic_layout.py
decisions:
  - "FIX-01 closed not-needed: VAL-06 (Phase 73) bench-proved configure_sram persists data via generic_memory_write_execute; no SRAM firmware fix warranted"
  - "FIX-03 closed not-needed: 0x39/0x35 have 0 DB chips each (GAP-5, Phase 72); the requirements premise of 2 chips was false; reconciliation is comment-only"
  - "Consistent cross-repo framing: firmware dispatches 0x35/0x39 → configure_flash4 (forward-compat); host excludes both from KNOWN_PROTOCOLS and routes to not_implemented"
metrics:
  duration: "~3 minutes"
  completed: "2026-06-18"
  tasks_completed: 2
  tasks_total: 2
  files_created: 1
  files_modified: 3
---

# Phase 74 Plan 01: FIX-01 Closure + FIX-03 Comment Reconciliation Summary

**One-liner:** FIX-01 closed not-needed via VAL-06 bench evidence (configure_sram persists data); FIX-03 comment-reconciled across firmware CLAUDE.md and host database.py/ic_layout.py with consistent 0-DB-chip phantom framing for 0x35 and 0x39.

---

## Objective

Close FIX-01 with recorded bench evidence and reconcile the firmware/host story for protocols 0x39 and 0x35 so both repos describe them identically as 0-DB-chip phantom entries. No SRAM code change, no wire/messages.toml change.

---

## Tasks Completed

### Task 1: FIX-01 Closure Document

**Commit:** `4555d0f` (meta-repo)

Created `.planning/phases/74-per-family-correctness-fixes-flash-gated/74-FIX01-CLOSURE.md` documenting:

- **Disposition:** CLOSED NOT-NEEDED — the requirement's "IF VAL-06 shows it already works" evidence branch is satisfied.
- **Primary evidence:** `firestarter_app/val-results/sram/val06-perbyte-verdict.txt` — verdict line "VAL-06 = table-stakes-PASS"; FM1608 two-pattern A/B (0x5A / 0xA5), N=2 runs, zero mismatches, negative control exit 1, D-09 hard gate SATISFIED.
- **Secondary evidence:** `firestarter_app/val-results/sram/validation-matrix.json` — `verdict=PASS`, `pass_type=authoritative`, `retry_count=2`.
- **Tertiary evidence:** Phase 73 VERIFICATION.md SC#4 — 4/4 must-haves verified; definitive VAL-06 verdict confirmed.
- **Mechanism confirmed:** `configure_sram` is NOT a silent no-op; the `generic_memory_write_execute` path fires correctly and persists data to real SRAM/FRAM hardware.
- **No code change:** `sram.cpp` and `memory.cpp` unmodified.

### Task 2: FIX-03 Comment Reconciliation (0x39/0x35 phantom framing)

**Commits:** `30ad80e` (firestarter sub-repo), `7769a42` (firestarter_app sub-repo)

Updated comments only — NO behavioral/wire change:

**`firestarter/CLAUDE.md`:**
- Dispatch table row 4: now states "0x05 has DB chips; 0x35 and 0x39 are phantom entries (0 DB chips each — forward-compat dispatch preserved in firmware; host excludes both from KNOWN_PROTOCOLS and routes them to not_implemented)"
- Algorithm Handlers table: 0x35 row now shows "0 DB chips (phantom — IC2_ALG_ITE is an ITE EC MCU label)" symmetrically with 0x39's existing "0 DB chips (phantom — no IC2_ALG constant exists)"; both rows note the host routing to not_implemented

**`firestarter_app/firestarter/database.py`** (~line 60):
- Extended existing "removed in Phase 57 (DEC-05)" comment with: "Firmware still dispatches 0x35 and 0x39 → configure_flash4 for forward-compat (memory.cpp:89), but the host excludes them from KNOWN_PROTOCOLS so they route to not_implemented here."

**`firestarter_app/firestarter/ic_layout.py`** (~line 228):
- Extended existing comment with same cross-repo note: "0 DB chips (both phantoms), firmware forward-compat dispatch, host routes to not_implemented (excluded from KNOWN_PROTOCOLS)."

---

## Verification Results

| Check | Command | Result |
|-------|---------|--------|
| 74-FIX01-CLOSURE.md exists + "table-stakes-PASS" | `grep -q "table-stakes-PASS"` | PASS |
| FIX-01 disposition "not-needed" present | `grep -qi "NOT-NEEDED"` | PASS |
| 0x39 in firestarter/CLAUDE.md | `grep -ql "0x39" firestarter/CLAUDE.md` | PASS |
| 0x39 in database.py | `grep -ql "0x39" database.py` | PASS |
| 0x39 in ic_layout.py | `grep -ql "0x39" ic_layout.py` | PASS |
| phantom/forward-compat framing in CLAUDE.md | `grep -qi "phantom\|forward-compat\|0 DB chips"` | PASS |
| check_dispatch.py | `python3 tools/check_dispatch.py` | PASS (744 chips, 0 regressions) |
| diff_db.py | `python3 tools/diff_db.py` | PASS (0 changed chips) |
| sram.cpp unmodified | `git status --porcelain src/proms/sram.cpp` | empty (PASS) |
| memory.cpp unmodified | `git status --porcelain src/proms/memory.cpp` | empty (PASS) |
| No messages.toml changes | `git status --porcelain \| grep messages.toml` | empty (PASS) |

---

## Deviations from Plan

None — plan executed exactly as written.

---

## FIX-03 Acceptance: "2 chip" Premise Superseded

The REQUIREMENTS.md FIX-03 entry referenced "2 current 0x39 DB chips." This premise is **false**, as confirmed by:

1. **Phase 72 GAP-5** (`v1.13-PROTOCOL-ENUMERATION.md` line 257): "0 current DB chips on 0x39" — phantom, no IC2_ALG constant; `memory.cpp:89` comment is accurate.
2. **Host source verification:** `build_db.py:134-148` KNOWN_PROTOCOLS excludes 0x39; `database.py:60` and `ic_layout.py:228` both confirm no DB chip uses 0x39.
3. **Phase 57 DEC-05:** 0x35 and 0x39 were deliberately removed from the host pipeline at v1.11.

FIX-03 is **CLOSED NOT-NEEDED with evidence** — the comment reconciliation IS the resolution. No code, DB, or wire change was required.

---

## Known Stubs

None. All three modified files contain substantive comment text grounded in documented evidence (GAP-5, DEC-05, Phase 73 VAL-06). No placeholder values.

---

## Threat Surface Scan

This plan changes documentation comments and adds a closure document only. No code path, no serial/wire surface, no hardware register access, no new protocol introduced. T-74-DOC-01 (doc drift) mitigated by acceptance grep confirming cross-repo consistency + check_dispatch.py/diff_db.py confirming no DB/dispatch behavior changed.

---

## Self-Check: PASSED

| Item | Status |
|------|--------|
| `74-FIX01-CLOSURE.md` exists on disk | FOUND |
| `74-01-SUMMARY.md` exists on disk | FOUND |
| Meta-repo commit `4555d0f` exists | FOUND |
| Firestarter sub-repo commit `30ad80e` exists | FOUND |
| Firestarter_app sub-repo commit `7769a42` exists | FOUND |
