---
phase: 87-naming-documentation-pass
plan: "01"
subsystem: firmware-documentation
tags: [protocols, vocabulary, invariant-matrix, name-04-corrections, flash-baseline]
dependency_graph:
  requires: [phase-86-variant-decode-correct-db-regen]
  provides: [PROTOCOLS.md canonical vocabulary, INV-01..09 traceability matrix, pre-phase flash baseline]
  affects: [plan-87-02 handler comments, plan-87-03 native tests, plan-87-04 flash-delta gate]
tech_stack:
  added: []
  patterns: [SHIELD-REVISIONS.md doc style, two-name scheme, anchored datasheet citations, INV-id greppability]
key_files:
  created:
    - firestarter/doc/PROTOCOLS.md
    - firestarter/.flash-baseline-87.txt
  modified: []
decisions:
  - "Live bucket set re-verified from chip_database.json before authoring (DB is authoritative, not memory)"
  - "FM1608 decimal-40/hex-0x28 conflation explicitly retired in §1.10; true tuple type4/proto0x07/variant0x4126->0x28 documented"
  - "X88C64 EEPROM electrical.type correction documented in §1.12; FUT-01 PCB-blocked disposition confirmed"
  - "INV-01..09 planned test names use test_inv0N_<family>_<behavior> convention for grep-intact SAFE-02 handoff"
  - "0x2B infeasible bucket documented as 'likely IC2_ALG_GAL20' with honest uncertainty — protocol-id.md gap noted"
metrics:
  duration: "15min"
  completed_date: "2026-06-26"
  tasks_completed: 3
  files_changed: 2
---

# Phase 87 Plan 01: Vocabulary + INV Matrix Summary

**One-liner:** Protocol vocabulary doc (`firestarter/doc/PROTOCOLS.md`) with 12-bucket NAME-01 facets, datasheet citations, FM1608/X88C64 NAME-04 corrections, Honest non-protocols section, and INV-01..09 traceability matrix with per-INV suite paths — plus pre-phase Leonardo flash baseline capture (25654 bytes).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 0 | Capture pre-phase Leonardo flash baseline | `bddb8ee` | `firestarter/.flash-baseline-87.txt` |
| 1 | Per-bucket vocabulary + NAME-04 corrections + Honest non-protocols | `b22333b` | `firestarter/doc/PROTOCOLS.md` (402 lines) |
| 2 | INV-01..09 traceability matrix + planned test names + suite paths | `b22333b` | `firestarter/doc/PROTOCOLS.md` (§3 matrix section) |

Tasks 1 and 2 are in the same commit because PROTOCOLS.md is a single document authored in one pass — the file was not partially committed mid-task; the INV matrix was written as §3 of the completed document.

## Deliverables

### firestarter/.flash-baseline-87.txt

Pre-phase Leonardo flash byte count captured BEFORE any firmware edit (Wave 1, Plans 02/03 are the first firmware touches in Wave 2). Capture command (verbatim per plan spec):

```bash
pio run -e leonardo 2>&1 | grep -E '^Flash:' | grep -oE 'used [0-9]+ bytes' | head -1 | grep -oE '[0-9]+' > .flash-baseline-87.txt
```

**Result:** `25654` (89.5% of 28672 bytes). This is the frozen-world zero-flash anchor. Plan 04 Task 2 subtracts post-phase Leonardo bytes against this integer and FAILS if the delta exceeds the threshold (NAME-05/D-10).

### firestarter/doc/PROTOCOLS.md (402 lines)

**Orientation + reader-router:** Mirrors `SHIELD-REVISIONS.md` opening pattern — one-paragraph "what this doc is", `[§N (label)](#anchor)` reader-router, pointer to deeper meta-repo sources.

**Canonical bucket summary table:** All 12 real buckets with hex, DB chip count, handler, datasheets folder slug (col 1, D-02 unchanged), and algorithm-axis name (col 2).

**12 per-bucket sections (§1.1–§1.12):** Each covers the 4 NAME-01 facets with anchored datasheet citations in the form `datasheets/<slug>/<file>.pdf p.N §section`. Covers:
- 0x05 FLASH-AMD-STD (5V page-write flash)
- 0x06 FLASH-AMD-ALT (AMD/SST unlock-sequence NOR flash)
- 0x07 EPROM-STD (28-pin UV-EPROM / EE-EPROM, 13V VPP)
- 0x08 EPROM-QUICK (32-pin UV-EPROM / EE-EPROM, 13V VPP)
- 0x0B EPROM-LEGACY (24-pin UV-EPROM, 12–25V direct-VPE rail)
- 0x0D EEPROM-POLL (5V parallel EEPROM, SDP + DQ7 page poll)
- 0x0E SRAM-32PIN (32-pin battery-backed NVRAM)
- 0x10 FLASH-INTEL (Intel 28F command-register NOR flash, 12V VPP mandatory)
- 0x27 SRAM-24PIN (24-pin async SRAM, 5V)
- 0x28 SRAM-STD (28-pin SRAM/FRAM, NAME-04 FM1608 call-out in §1.10)
- 0x29 SRAM-512K-1M (32-pin large battery-backed NVRAM)
- 0x34 EEPROM-X88C64 (XICOR 8051-bus EEPROM, PCB-blocked, NAME-04 X88C64 call-out in §1.12)

**NAME-04 corrections (§1.10 and §1.12):**
- FM1608: true tuple `type4/proto0x07/variant0x4126 → 0x28 SRAM_STD/FRAM`; the "FM1608 algorithm 40 = 0x28" decimal/hex conflation is explicitly retired
- X88C64: true tuple `type1/proto0x34/variant0x3100/flags0x00414200 (flags&0x10==0) → EEPROM`; PCB-blocked FUT-01 disposition documented

**Honest non-protocols (§2):**
- Phantom 0x35/0x39: named as dispatched-but-dead (zero DB chips, firmware dispatch preserved for forward-compat)
- Infeasible 0x11/0x2A/0x2B/0x2C: named as structurally infeasible on RURP hardware (fail-closed, zero DB chips)

**INV-01..09 traceability matrix (§3):** All 9 invariants in D-04 ordering with 5 columns each — INV id, one-line behavior, owning handler file, planned native test function name (e.g. `test_inv01_eprom_0x0B_direct_vpe_rail`), matrix-assigned suite path. Per-INV suite path contract stated; SAFE-02 handoff noted.

## Verification

All plan verification checks passed:

```
BASELINE_OK 25654
```

```
grep -c "Honest non-protocols" + all 12 buckets + all 6 non-protocols: OK
```

```
all INV-01..INV-09 + all 4 suite paths in PROTOCOLS.md: OK
```

```
git diff HEAD~2 HEAD --name-only: .flash-baseline-87.txt  doc/PROTOCOLS.md  (no firmware/DB changes)
```

## Deviations from Plan

None — plan executed exactly as written. Tasks 1 and 2 were committed together in a single commit since PROTOCOLS.md is authored as a single document (not incrementally), consistent with the "write then commit" instruction. The plan did not require separate commits for tasks 1 and 2.

## Known Stubs

None. PROTOCOLS.md is a documentation-only file; all 12 buckets have substantive content. The INV-07 planned test name `test_inv07_sram_fm1608_routes_to_sram` and the other 8 INV test names are intentional placeholders for Plan 03 to implement — these are the contract, not stubs in the UI-rendering sense.

## Threat Flags

None. This plan modified only documentation files (`firestarter/doc/PROTOCOLS.md` and `firestarter/.flash-baseline-87.txt`). No new network endpoints, auth paths, file access patterns, or schema changes. The frozen-world constraint (D-09) was verified: no firmware/DB/datasheet-folder modifications.

## Self-Check: PASSED

- `firestarter/doc/PROTOCOLS.md` exists: FOUND
- `firestarter/.flash-baseline-87.txt` exists: FOUND
- Commit `bddb8ee` exists: FOUND
- Commit `b22333b` exists: FOUND
