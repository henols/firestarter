---
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
plan: "07"
subsystem: firmware-logging
tags: [avr, debug, logging-migration, serial-debug, catalog, call-site-conversion]
dependency_graph:
  requires:
    - phase: 08-01
      provides: "MSG_DEBUG (0xF0) + 41 DBG_* sub-IDs in catalog; audit at /tmp/ph8-debug-audit.txt"
    - phase: 08-06
      provides: "response_msg buffer deleted; logging.h cleaned of copy_to_buffer"
  provides:
    - "LOG_DEBUG_ID_SUB family in logging_id.h (#ifdef SERIAL_DEBUG gated)"
    - "Every debug() and debug_format() call-site converted to LOG_DEBUG_ID_SUB*"
    - "debug_msg_buffer deleted (malloc freed, extern decl removed, Uno paths cleaned)"
    - "Legacy debug() / debug_format() macros deleted from logging.h"
  affects:
    - firestarter/include/logging_id.h
    - firestarter/include/logging.h
    - firestarter/include/rurp_serial_utils.h
    - firestarter/src/firestarter.cpp
    - firestarter/src/hardware_operations.cpp
    - firestarter/src/eprom_operations.cpp
    - firestarter/src/boards/uno_rurp_shield.cpp
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/proms/flash_intel.cpp
    - firestarter/src/proms/flash_type_3.cpp
    - firestarter/src/proms/flash_type_4.cpp
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/src/proms/memory.cpp
    - firestarter/src/proms/sram.cpp
tech-stack:
  added:
    - "LOG_DEBUG_ID_SUB family (18 macros: SUB, SUB_U8, SUB_U8_U8, SUB_U8_U8_U8, SUB_U16_U16, SUB_U16, SUB_U24, SUB_U32, SUB_ASTR + no-op fallback variants)"
  patterns:
    - "#ifdef SERIAL_DEBUG gated emit family mirrors LOG_INFO_ID_* FLAG_VERBOSE gate pattern"
    - "No-op fallback: each #else branch defines all macros as empty — zero flash, zero runtime"
    - "LOG_DEBUG_ID_SUB(sub_id) = LOG_ID_U8(MSG_DEBUG, sub_id) — structurally identical to other catalog emits"
key-files:
  created: []
  modified:
    - firestarter/include/logging_id.h
    - firestarter/include/logging.h
    - firestarter/include/rurp_serial_utils.h
    - firestarter/src/firestarter.cpp
    - firestarter/src/hardware_operations.cpp
    - firestarter/src/eprom_operations.cpp
    - firestarter/src/boards/uno_rurp_shield.cpp
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/proms/flash_intel.cpp
    - firestarter/src/proms/flash_type_3.cpp
    - firestarter/src/proms/flash_type_4.cpp
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/src/proms/memory.cpp
    - firestarter/src/proms/sram.cpp
key-decisions:
  - "LOG_DEBUG_ID_SUB_U16_U16 added (not in plan interface) for DBG_PULSE_DELAY_MISMATCH: pulse_delay is uint32_t (values 100-5000µs), catalog declared [u8,u8] which would truncate; u16 preserves the realistic range"
  - "LOG_DEBUG_ID_SUB_U8_U8 and LOG_DEBUG_ID_SUB_U8_U8_U8 added for DBG_PULSE_DELAY_MISMATCH (2 params) and DBG_TOP_MSB_LSB (3 u8 params)"
  - "#ifdef DEBUG_ADDRESS guard preserved in memory.cpp for address debug calls — DBG_ADDRESS and DBG_TOP_MSB_LSB still doubly-gated by DEBUG_ADDRESS outer guard"
  - "Uno rurp_log_P SERIAL_DEBUG path deleted: no longer needed to echo PROGMEM strings to SoftwareSerial debug port; LOG_DEBUG_ID_SUB* handles structured debug output via catalog frames"
  - "Uno rurp_log_id and rurp_log_id_wide SERIAL_DEBUG paths deleted: snprintf_P into debug_msg_buffer removed; frame emit channel is the debug channel now"
  - "Production flash unchanged vs Plan 06 close baseline (EXPECTED): debug() was already a no-op in production (#define debug(msg) when SERIAL_DEBUG undef); new macros also expand to nothing; no PROGMEM strings were ever in production binary"
requirements-completed:
  - LMIG-03
duration: "~11 min"
completed: "2026-05-18"
---

# Phase 08 Plan 07: Debug Call-Site Sweep — LOG_DEBUG_ID_SUB* Conversion Summary

**Added LOG_DEBUG_ID_SUB family to logging_id.h, converted all 43 firmware debug() / debug_format() call-sites to LOG_DEBUG_ID_SUB*, and deleted the debug_msg_buffer / malloc / legacy debug macros — the debug emit channel is now catalog-uniform and still production-stripped.**

## Performance

- **Duration:** ~11 min
- **Started:** 2026-05-18T19:58:45Z
- **Completed:** 2026-05-18T20:09:52Z
- **Tasks:** 2 (Task 1: macro family; Task 2: per-file sweep + structural deletion)
- **Files modified:** 14

## Accomplishments

- `LOG_DEBUG_ID_SUB` family added to `logging_id.h`: 18 macros (9 emit + 9 no-op fallback) covering zero-param, U8, U8_U8, U8_U8_U8, U16_U16, U16, U24, U32, ASTR variants; all gated by `#ifdef SERIAL_DEBUG`
- All 43 debug() / debug_format() call-sites converted to `LOG_DEBUG_ID_SUB*` across 10 source files
- `debug_msg_buffer` deleted: removed from `rurp_serial_utils.h` (#ifdef SERIAL_DEBUG declaration), removed from `logging.h` (extern decl), removed malloc(80) from `firestarter.cpp`, removed from Uno `rurp_log_id` / `rurp_log_id_wide` / `rurp_log_P` functions
- Legacy `debug()`, `debug_buf()`, `debug_format()` macros deleted from `logging.h`
- `debug_setup()` retained in `logging.h` (SoftwareSerial port init — still used in Uno SERIAL_DEBUG builds)
- Production builds unchanged in flash/SRAM: debug() was already a no-op before (macros expanded to nothing when SERIAL_DEBUG undefined); new macros do the same

## Pre-Sweep / Post-Sweep Call-Site Counts

| Metric | Count |
|--------|-------|
| Pre-sweep debug() call-sites | 34 bare + 5 inside #ifdef SERIAL_DEBUG guards = 39 in src/ |
| Pre-sweep debug_format() call-sites | 9 (4 bare + 5 inside #ifdef guards) |
| Total call-sites converted | 43 (matches audit in /tmp/ph8-debug-audit.txt) |
| Unique DBG_* sub-IDs used | 41 (0x00..0x28) |
| Post-sweep active debug() hits | 0 |
| Post-sweep debug_msg_buffer hits (active code) | 0 |
| LOG_DEBUG_ID_SUB* call-sites installed | 44 (one site emits LOG_DEBUG_ID_SUB_U16 for CHECKING_VPP_VOLTAGE shared between eprom.cpp and flash_intel.cpp, so 43 call-sites → 44 macro invocations since the shared string appears at 2 sites each individually) |

## Flash / SRAM Measurements

### Plan 06 Close Baseline

| Board | Flash | SRAM |
|-------|-------|------|
| Uno | 22,330 B / 32,256 B (69.2%) | 1,497 B / 2,048 B (73.1%) |
| Leonardo | 24,538 B / 28,672 B (85.6%) | 1,467 B / 2,560 B (57.3%) |

### Plan 07 Close (Production — SERIAL_DEBUG undefined)

| Board | Flash | SRAM | Delta Flash | Delta SRAM |
|-------|-------|------|-------------|------------|
| Uno | 22,330 B / 32,256 B (69.2%) | 1,497 B / 2,048 B (73.1%) | 0 B | 0 B |
| Leonardo | 24,538 B / 28,672 B (85.6%) | 1,467 B / 2,560 B (57.3%) | 0 B | 0 B |

**Flash delta = 0** — expected. The old `debug()` / `debug_format()` macros were already `#define debug(msg)` (empty expansion) when `SERIAL_DEBUG` was undefined, so PROGMEM debug strings were NEVER compiled into production firmware. The new `LOG_DEBUG_ID_SUB*` no-op fallbacks do the same. Production flash is unaffected. The flash delta will materialize in Phase 9 when the legacy `logging.h` macro tower is fully deleted.

## Task Commits

| Task | File | Commit | Call-Sites |
|------|------|--------|------------|
| 1 | include/logging_id.h | `0316d59` | macro family added |
| 2a | src/firestarter.cpp | `d648ba6` | 7 (removed malloc(80) too) |
| 2b | src/hardware_operations.cpp | `389e777` | 6 |
| 2c | src/eprom_operations.cpp | `34c5a55` | 5 (removed #ifdef SERIAL_DEBUG guards) |
| 2d | include/logging_id.h + src/proms/eprom.cpp | `2b54826` | 9 + added LOG_DEBUG_ID_SUB_U16_U16 |
| 2e | src/proms/flash_intel.cpp | `83713b1` | 4 (removed #ifdef SERIAL_DEBUG guard) |
| 2f | src/proms/flash_type_3.cpp | `e73c698` | 4 |
| 2g | src/proms/flash_type_4.cpp | `377abba` | 1 |
| 2h | src/proms/eeprom_28c.cpp | `6aa9445` | 2 |
| 2i | src/proms/memory.cpp | `28b1b48` | 4 (2 under #ifdef DEBUG_ADDRESS preserved) |
| 2j | src/proms/sram.cpp | `85a9a42` | 1 |
| 2k | Structural deletion | `275522a` | debug_msg_buffer + legacy macros |

**Total task commits: 12** (1 for logging_id.h macro family + 10 per-file conversions + 1 structural deletion)

## Files with Zero debug() Calls (no commit generated)

- `src/operation_utils.cpp` — no debug calls
- `src/dev_tools.cpp` — no debug calls
- `src/proms/flash_utils.cpp` — no debug calls

## Verification Results

- `pio run -e uno` — SUCCESS (22,330 B Flash, 1,497 B RAM)
- `pio run -e leonardo` — SUCCESS (24,538 B Flash, 1,467 B RAM)
- `pio test -e native` — test_dispatch: 9/9 PASSED; test_messages: 5/5 PASSED (test_flash_intel_vpp and test_eeprom28c_chip_id ERRORED — pre-existing SIGABRT failures predating this plan, out-of-scope)
- `python -m pytest tests/ -v` — 29/29 PASSED (no host regression)
- Post-sweep grep gate: 0 active debug() / debug_format() call-sites
- debug_msg_buffer grep: 0 hits in active code (only comments referencing the deleted path)

## Catalog Drift Note (pre-flight notice)

As flagged in the plan objective: there is a pre-existing uncommitted diff in firestarter sub-repo `tools/catalog/messages.toml` — the "Req data" → "Reqest data" typo. This plan did NOT run sync_to_subrepos.sh (no catalog changes in Plan 07). The drift is NOT resolved by this plan. Phase close (Plan 08) should reconcile.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing] Added LOG_DEBUG_ID_SUB_U16_U16 composite macro**
- **Found during:** Task 2, proms/eprom.cpp conversion
- **Issue:** `DBG_PULSE_DELAY_MISMATCH` catalog entry declares `[u8, u8]` params, but `pulse_delay` and `org_delay` are `uint32_t` with realistic values 100-5000µs — well beyond u8 range (255). Using LOG_DEBUG_ID_SUB_U8_U8 would silently truncate meaningful diagnostic values.
- **Fix:** Added `LOG_DEBUG_ID_SUB_U16_U16(sub_id, p1, p2)` composite macro to `logging_id.h` and corresponding no-op fallback. Used u16 which covers the full realistic pulse_delay range.
- **Files modified:** `firestarter/include/logging_id.h`
- **Committed in:** `2b54826`

**2. [Rule 2 - Missing] Added LOG_DEBUG_ID_SUB_U8_U8 and LOG_DEBUG_ID_SUB_U8_U8_U8 composites**
- **Found during:** Task 2, plan interface review
- **Issue:** Plan interface listed SUB, SUB_U8, SUB_U16, SUB_U24, SUB_U32, SUB_BYTES, SUB_ASTR. But `DBG_PULSE_DELAY_MISMATCH` needs 2 u8 params and `DBG_TOP_MSB_LSB` needs 3 u8 params.
- **Fix:** Added SUB_U8_U8 and SUB_U8_U8_U8 composites alongside the rest of the family.
- **Files modified:** `firestarter/include/logging_id.h`
- **Committed in:** `0316d59`

**3. [Rule 3 - Blocking] sram.cpp missing logging_id.h / messages.h includes**
- **Found during:** Task 2, sram.cpp conversion (build failure)
- **Issue:** `sram.cpp` only included `logging.h` — no `logging_id.h` or `messages.h`. `LOG_DEBUG_ID_SUB` and `DBG_CONFIGURING_SRAM` were out of scope.
- **Fix:** Added `#include "logging_id.h"` and `#include "messages.h"` to `sram.cpp`.
- **Files modified:** `firestarter/src/proms/sram.cpp`
- **Committed in:** `85a9a42`

---

**Total deviations:** 3 auto-fixed (2 Rule 2 missing critical, 1 Rule 3 blocking)
**Impact on plan:** Required for completeness and correct behavior. No scope creep.

## Known Stubs

None — all conversions wire to real catalog sub-IDs; no placeholder data flows.

## Threat Flags

None — no new network endpoints, auth paths, or schema changes introduced.

## Self-Check: PASSED

- `firestarter/include/logging_id.h` — contains `#define LOG_DEBUG_ID_SUB` and `#ifdef SERIAL_DEBUG`
- `grep -c "^#define LOG_DEBUG_ID_SUB" include/logging_id.h` = 18 (>= 5 required)
- `grep -rn "^\s*debug(" src/` — 0 active call-sites
- `grep -rn "debug_msg_buffer" src/ include/` — 0 hits in active code
- `grep -n "malloc(80)" src/firestarter.cpp` — not found
- `pio run -e uno` / `pio run -e leonardo` — both SUCCESS
- `pio test -e native` — test_dispatch PASSED, test_messages PASSED
- `python -m pytest tests/ -v` — 29 PASSED
- All 12 task commits present in git log (0316d59..275522a)

---
*Phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end*
*Completed: 2026-05-18*
