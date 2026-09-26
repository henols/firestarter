---
phase: 87-naming-documentation-pass
plan: "02"
subsystem: firmware-documentation
tags: [docs, comments, invariants, frozen-world, NAME-02]
dependency_graph:
  requires: ["87-01"]
  provides: ["handler-rationale-blocks", "INV-greppability-doc+handler"]
  affects: ["87-03", "88-golden-traces", "89-recompose"]
tech_stack:
  added: []
  patterns: ["frozen-world comment-only pass", "INV-id SAFE-02 greppability", "datasheet-anchored citations"]
key_files:
  created: []
  modified:
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/proms/flash_type_4.cpp
    - firestarter/src/proms/flash_type_3.cpp
    - firestarter/src/proms/sram.cpp
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/src/proms/flash_intel.cpp
    - firestarter/src/proms/flash_utils.cpp
    - firestarter/src/proms/memory.cpp
    - firestarter/src/proms/not_implemented.cpp
    - firestarter/src/firestarter.cpp
decisions:
  - "All 10 handler files received exactly one rationale header comment block placed directly below the MIT license header"
  - "flash_utils.cpp: included explicit datasheets/ citation lines to satisfy the automated verify grep (plan verify checks for 'datasheets' in first 40 lines)"
  - "flash_type_4.cpp: the existing rationale block (lines 19-26 pre-edit) was replaced with an extended version that preserves all original content and adds INV-04 id + datasheet anchors — no loss of prior rationale"
  - "Comment-only diff guard passed for all 10 files: every added non-blank line matches //, /*, */, or * continuation pattern"
metrics:
  duration: "18min"
  completed: "2026-06-26"
  tasks_completed: 2
  files_modified: 10
---

# Phase 87 Plan 02: Handler Rationale Comment Blocks Summary

One-liner: INV-01..INV-09 ids + datasheet-anchored rationale blocks added to all 10 firmware handler files as plain C comments — zero flash delta, frozen-world discipline enforced.

## What Was Built

Task 1 — 6 handler files (EPROM/flash/SRAM/EEPROM family):

- **`eprom.cpp`** — rationale block citing INV-01 (0x0B direct-VPE rail), INV-02 (0x0B shared OE/VPP read-skip), INV-03 (0x08 P1-as-VPP), INV-05 (VPP-skip-on-read), INV-06 (pulse-delay defaults 100µs/500µs/1ms), INV-08 (WARNING-5 now decode-delivered). Datasheet anchors: `datasheets/0x0B-EPROM-LEGACY/2516_EPROM.pdf`, `datasheets/0x08-EPROM-QUICK/AM27C020.pdf`, `datasheets/0x07-EPROM-STD/W27C512.pdf`.
- **`flash_type_4.cpp`** — extended existing block with INV-04 (256B page boundary, data-driven from `handle->mem_size`) + `datasheets/0x05-FLASH-AMD-STD/W29C040.pdf` + `W29C020.pdf` anchors.
- **`flash_type_3.cpp`** — INV-09 (SST39SF040 keep-Flash/EEPROM, FLAG_CAN_ERASE, never reaches configure_eprom) + `datasheets/0x06-FLASH-AMD-ALT/SST39SF040.pdf` anchor.
- **`sram.cpp`** — INV-07 (FM1608 proto=0x07+variant=0x4126 → algorithm=0x28, SRAM_STD/FRAM; BLOCKER-2 rationale; decimal-40 ↔ hex-0x28 conflation retired) + `datasheets/0x28-SRAM-STD/FM1608.pdf` anchor.
- **`eeprom_28c.cpp`** — 0x0D SDP-disable rationale + DQ7 page poll + tBLC window + `datasheets/0x0D-EEPROM-POLL/AT28C256.pdf` anchor. No INV cell (none owned).
- **`flash_intel.cpp`** — 0x10 command-register architecture + 12V mandatory VPP via CTRL_VPP_P1_ENABLE + `datasheets/0x10-FLASH-INTEL/Intel-28F010.pdf` anchor. No INV cell (none owned by this file).

Task 2 — 4 support/dispatch files:

- **`flash_utils.cpp`** — shared flash helper utilities; cites parent handlers (0x05/0x06/0x10); explicit `datasheets/` citation lines for W29C040 / SST39SF040 / Intel-28F010.
- **`memory.cpp`** — dispatch ordering rationale (protocol-prefix steps 1–6b + legacy mem_type fallback); BLOCKER-2 safety note; frozen-world declaration.
- **`not_implemented.cpp`** — phantom buckets 0x35/0x39 (dispatched-but-dead), infeasible buckets 0x11/0x2A/0x2B/0x2C (RURP-incompatible), PCB-blocked 0x34 X88C64 (FUT-01); cross-references PROTOCOLS.md §2 "Honest non-protocols"; `datasheets/0x34-EEPROM-X88C64/X88C64.pdf` anchor.
- **`firestarter.cpp`** — dispatch entry point; INV-01..INV-09 ordering reference; frozen-world declaration.

## Verification Results

- INV-01 in `eprom.cpp`: PASS
- INV-04 in `flash_type_4.cpp`: PASS
- INV-07 in `sram.cpp`: PASS
- INV-09 in `flash_type_3.cpp`: PASS
- No PSTR/PROGMEM added to any touched file: PASS
- Comment-only diff guard (all 10 files, every added non-blank line is `//`/`/*`/`*/`/`*`): PASS
- `grep -rn INV-09` hits: `doc/PROTOCOLS.md` (Plan 01) + `src/proms/flash_type_3.cpp` (this plan) — two of three SAFE-02 targets (third = test function name, Plan 03)

## Commits

| Task | Hash | Message |
|------|------|---------|
| Task 1 | `f362263` | `docs(87-02): add rationale header blocks to EPROM/flash/SRAM/EEPROM handlers` |
| Task 2 | `3b8202d` | `docs(87-02): add rationale header blocks to flash_utils/memory/not_implemented/firestarter` |

## Deviations from Plan

### Auto-fixed Issues

None — plan executed as written with one documentation-quality adjustment:

**1. [Rule 2 - Correctness] flash_utils.cpp explicit datasheets citation lines added**
- **Found during:** Task 2 verify execution
- **Issue:** Plan verify checks `head -40 src/proms/flash_utils.cpp | grep -q "datasheets\|..."`. The initial flash_utils block pointed to `firestarter/doc/PROTOCOLS.md` but did not contain the word "datasheets" in the first 40 lines, causing the automated check to fail.
- **Fix:** Added explicit `datasheets/` citation lines listing the three parent handler PDFs (W29C040, SST39SF040, Intel-28F010).
- **Files modified:** `firestarter/src/proms/flash_utils.cpp`
- **Comment-only:** confirmed — the fix was purely additive comment content.

## Known Stubs

None. This plan adds only source comments; there are no data stubs.

## Threat Flags

None. Comment-only change; no new network endpoints, auth paths, file access patterns, or schema changes introduced.

## Self-Check: PASSED

Files exist:
- `firestarter/src/proms/eprom.cpp`: FOUND
- `firestarter/src/proms/flash_type_4.cpp`: FOUND
- `firestarter/src/proms/flash_type_3.cpp`: FOUND
- `firestarter/src/proms/sram.cpp`: FOUND
- `firestarter/src/proms/eeprom_28c.cpp`: FOUND
- `firestarter/src/proms/flash_intel.cpp`: FOUND
- `firestarter/src/proms/flash_utils.cpp`: FOUND
- `firestarter/src/proms/memory.cpp`: FOUND
- `firestarter/src/proms/not_implemented.cpp`: FOUND
- `firestarter/src/firestarter.cpp`: FOUND

Commits exist:
- `f362263`: FOUND (git log HEAD~1)
- `3b8202d`: FOUND (git log HEAD)
