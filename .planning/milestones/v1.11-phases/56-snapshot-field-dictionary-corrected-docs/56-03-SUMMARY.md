---
phase: 56-snapshot-field-dictionary-corrected-docs
plan: "03"
subsystem: firestarter_app/doc
tags: [docs, decode-correctness, protocol-id, protocol-flags, package-details, v1.11]
dependency_graph:
  requires: ["56-02"]
  provides: ["DOC-01", "DOC-02", "DOC-03"]
  affects: ["Phase 57 code fixes cite these docs as authority"]
tech_stack:
  added: []
  patterns: ["derived-doc pattern: docs rewritten fresh from field dictionary authority"]
key_files:
  created: []
  modified:
    - firestarter_app/doc/protocol-id.md
    - firestarter_app/doc/protocol-flags.md
    - firestarter_app/doc/package-details.md
decisions:
  - "Rewrote all three docs fresh from infoic-field-dictionary.md (D-08) — no surgical edits"
  - "Bits 3/6/7 marked UNKNOWN in both protocol-flags.md and package-details.md — consistent with field dictionary authority"
  - "Bit 4 corrected to MP_ERASE_MASK / can_erase in both flag docs — consistent with WARNING-5 predicate"
  - "0x39 labeled PHANTOM in protocol-id.md — removed FLASH_INTEL_ALT/AT49F040 reference"
  - "0x3C labeled INVENTED in protocol-id.md — not in minipro source at a8efaedc"
  - "package-details.md retitled to 'package_details Field Reference' — describes the package_details uint32 AND the flags bit table"
metrics:
  duration: "~25 minutes"
  completed: "2026-06-08T12:22:00Z"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 3
---

# Phase 56 Plan 03: Corrected Decode Docs Summary

**One-liner:** Rewrote three decode docs fresh from the field dictionary — canonical IC2_ALG names, 0x39 phantom fixed, bit-4 MP_ERASE_MASK corrected, bits 3/6/7 UNKNOWN, package-details retitled; regression gate green at 72% coverage.

---

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Rewrite protocol-id.md (DOC-03) and protocol-flags.md (DOC-02) | `a56d874` | `doc/protocol-id.md`, `doc/protocol-flags.md` |
| 2 | Rewrite package-details.md (DOC-01) and run regression gate | `f1858a5` | `doc/package-details.md` |

---

## What Was Built

### protocol-id.md (DOC-03)

Complete rewrite derived from `infoic-field-dictionary.md`. Key corrections:

- All 11 in-scope IDs now carry canonical `IC2_ALG_*` names from `database.h@a8efaedc` (e.g., `IC2_ALG_ROM28P_1` for `0x07`, `IC2_ALG_EE28C32P` for `0x0D`)
- `0x39` corrected: was `FLASH_INTEL_ALT` (AT49F040). Now labeled **PHANTOM** — no `IC2_ALG` constant exists in `database.h`; appears only in legacy INFOIC (not INFOIC2PLUS); INFOIC2PLUS-unreachable
- `0x3C` corrected: was `FLASH_4MB`. Now labeled **INVENTED** — no entry in minipro source at commit `a8efaedc`
- `0x2A`/`0x2C`/`0x2E`/`0x35`: correct IC2_ALG names (`GAL16`, `GAL22`, `PIC32X_2`, `ITE`) with exclusion rationale (PLD/MCU `type=3`/`type=2`, zero DIP memory chips)
- `0x11`: exclusion rationale (LPC serial, 3.3V, not parallel-bus)
- WARNING-5 override explained in context of `IC2_ALG_ROM28P_1` (0x07)
- BUG-4 note deferred to Phase 57

### protocol-flags.md (DOC-02)

Complete rewrite derived from `infoic-field-dictionary.md`. Key corrections:

- **Bit 4 fixed:** was "Requires explicit write-enable or software unlock sequence." Now: `MP_ERASE_MASK` = "Can be electrically erased" — the WARNING-5 discriminator (`build_db.py` uses `flags & 0x10`)
- **Bits 3/6/7 marked UNKNOWN:** no `MP_*` constant in `database.c` lines 39–50; prior inferred meanings removed
- All source-confirmed bits (1, 4, 5, 12, 13, 14, 15, 18, 19, 20-21) documented with `MP_*` constant names
- WARNING-5 note explains how `MP_ERASE_MASK` drives the `DIP28_2764 + 0x07 + Flash/EEPROM → 0x0D` override

### package-details.md (DOC-01)

Complete rewrite derived from `infoic-field-dictionary.md`. Key corrections:

- **Retitled** to `package_details Field Reference` — was misleadingly about inferred flag meanings only; now covers both the `package_details` uint32 layout AND the `flags` bit table
- **`package_details` uint32 layout** documented: bit 31 SMD, bits 29-24 pin count, bits 15-8 ICSP serial index, bits 7-0 adapter type; PLCC adapter remapping table included
- **build_db.py DIP filter** documented: `24 <= pin_count <= 32`, `is_smd == 0`, `is_serial == 0`, `type_int in [1, 4]`
- **Flags bits table** with Status column: 10 CONFIRMED bits with `MP_*` constant names; bits 3/6/7 explicitly UNKNOWN
- **Bit 4** = `MP_ERASE_MASK` = can-erase (consistent with WARNING-5)

---

## Regression Gate

`cd /workspaces/firestarter_app && python -m pytest tests/ --cov-fail-under=70`

**Result:** 470 passed, **72% coverage** (floor = 70%). Suite green. No non-doc changes crept in; `build_db.py` and `chip_database.json` unchanged.

---

## Verification Gates Passed

- `DOCS_AB_OK`: `grep IC2_ALG`, `grep -i phantom`, `! grep FLASH_INTEL_ALT`, `grep MP_ERASE_MASK`, `grep UNKNOWN`, logo-header checks — all passed
- `DOC_C_AND_REGRESSION_OK`: `grep UNKNOWN`, `grep -i flags`, logo-header, `pytest --cov-fail-under=70` — all passed
- `build_db.py` and `chip_database.json`: confirmed unchanged (`git diff --name-only` returns empty)

---

## Deviations from Plan

None — plan executed exactly as written. All three docs rewritten fresh from the field dictionary, regression gate green, no decode-behavior changes.

---

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes. This plan adds only `.md` documentation files — no executable code paths introduced.

---

## Known Stubs

None. All three docs are source-grounded from the field dictionary. No placeholder text or deferred wiring.

---

## Self-Check

Files exist:
- `/workspaces/firestarter_app/doc/protocol-id.md` — FOUND
- `/workspaces/firestarter_app/doc/protocol-flags.md` — FOUND
- `/workspaces/firestarter_app/doc/package-details.md` — FOUND

Commits exist in firestarter_app:
- `a56d874` (Task 1: protocol-id.md + protocol-flags.md) — FOUND
- `f1858a5` (Task 2: package-details.md) — FOUND

## Self-Check: PASSED
