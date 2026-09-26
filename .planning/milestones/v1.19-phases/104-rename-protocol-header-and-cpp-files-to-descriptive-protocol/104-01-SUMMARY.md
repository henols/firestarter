---
phase: 104-rename-protocol-header-and-cpp-files-to-descriptive-protocol
plan: 01
subsystem: firmware
tags: [firmware, dispatch, refactor, naming, arduino, platformio]

# Dependency graph
requires:
  - phase: 101-fw
    provides: PROTO_<NAME> constants (proto_constants.h) and PROTO_FLASH_NOR_UNLOCK / PROTO_FLASH_5V_PAGE dispatch keys used unchanged here
provides:
  - flash_nor_unlock.{h,cpp} (renamed from flash_type_3.{h,cpp}, 0x06 AMD-unlock NOR handler)
  - flash_5v_page.{h,cpp} (renamed from flash_type_4.{h,cpp}, 0x05 + phantom 0x35/0x39 page-write handler)
  - memory.cpp dispatch chain referencing the renamed headers/functions at both call-site groups
  - corrected, unique header guards (__FLASH_NOR_UNLOCK_H__, __FLASH_5V_PAGE_H__) replacing the misspelled/mismatched originals
affects: [104-02-rename-native-tests, 104-03-rename-native-tests]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "File-pair rename via git mv BEFORE content edits, so git records R (rename) status not delete+add"
    - "File-internal static helper stems renamed alongside the public entry point for full consistency (flash3_* -> flash_nor_unlock_*, flash4_* -> flash_5v_page_*)"

key-files:
  created:
    - firestarter/include/flash_nor_unlock.h
    - firestarter/include/flash_5v_page.h
    - firestarter/src/proms/flash_nor_unlock.cpp
    - firestarter/src/proms/flash_5v_page.cpp
  modified:
    - firestarter/src/proms/memory.cpp
    - firestarter/include/flash_utils.h
    - firestarter/src/proms/flash_utils.cpp

key-decisions:
  - "Renamed file-internal flash3_*/flash4_* static helpers to flash_nor_unlock_*/flash_5v_page_* stems (discretionary per 104-PATTERNS.md) for full identifier consistency within each renamed file — no cross-file impact since they are file-internal"
  - "flash4_page_size (static helper) renamed to flash_5v_page_page_size following the same stem convention"
  - "Left the pre-existing unrelated platformio.ini whitespace diff (trailing-space removal on a comment line) untouched — out of scope for this plan, not introduced by this work"

patterns-established:
  - "Two-call-site-group dispatch update: memory.cpp has both a protocol-chain (PROTO_*) group and a legacy mem_type fallback group referencing the same handler — both must be updated together on any handler rename"

requirements-completed: [RENAME-01, RENAME-02]

coverage:
  - id: D1
    description: "flash_type_3.{h,cpp} renamed to flash_nor_unlock.{h,cpp} via git mv (history preserved), guard fixed to __FLASH_NOR_UNLOCK_H__, public function configure_flash3 -> configure_flash_nor_unlock, internal flash3_* helpers renamed"
    requirement: "RENAME-01"
    verification:
      - kind: unit
        ref: "git status --porcelain shows R status for include/flash_nor_unlock.h and src/proms/flash_nor_unlock.cpp; grep for configure_flash3/flash_type_3/__FALSH__TYPE_3 returns empty"
        status: pass
    human_judgment: false
  - id: D2
    description: "flash_type_4.{h,cpp} renamed to flash_5v_page.{h,cpp} via git mv (history preserved), guard fixed (was mismatched __FALSH__TYPE_4_H__ vs __FLASH__TYPE_4_H__) to __FLASH_5V_PAGE_H__, public function configure_flash4 -> configure_flash_5v_page, internal flash4_* helpers renamed"
    requirement: "RENAME-01"
    verification:
      - kind: unit
        ref: "git status --porcelain shows R status for include/flash_5v_page.h and src/proms/flash_5v_page.cpp; grep for configure_flash4/flash_type_4/FALSH returns empty"
        status: pass
    human_judgment: false
  - id: D3
    description: "memory.cpp dispatch (both the protocol-chain PROTO_FLASH_NOR_UNLOCK/PROTO_FLASH_5V_PAGE arms and the legacy mem_type TYPE_FLASH_TYPE_3/TYPE_FLASH_TYPE_4 fallback arms) updated to call the renamed functions via the renamed #include headers; flash_utils.h/.cpp comments updated; both boards compile clean after a full clean build"
    requirement: "RENAME-02"
    verification:
      - kind: unit
        ref: "pio run -t clean && pio run -e uno && pio run -e leonardo (both SUCCESS)"
        status: pass
      - kind: unit
        ref: "grep for flash_type_3/flash_type_4/configure_flash3/configure_flash4 in memory.cpp and flash_utils.{h,cpp} returns empty"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-02
status: complete
---

# Phase 104 Plan 01: Rename flash_type_3/4 to flash_nor_unlock/flash_5v_page Summary

**Renamed the two minipro-heritage firmware handler file-pairs (flash_type_3 -> flash_nor_unlock, flash_type_4 -> flash_5v_page) and their public + file-internal functions to descriptive protocol names, fixing two long-standing misspelled header guards along the way; both Uno and Leonardo builds compile byte-identical in flash size.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-02T07:17:51Z
- **Completed:** 2026-07-02T07:23:09Z
- **Tasks:** 3
- **Files modified:** 7 (4 renamed + 3 edited)

## Accomplishments
- `flash_type_3.{h,cpp}` -> `flash_nor_unlock.{h,cpp}` via `git mv` (rename history preserved); guard fixed from misspelled `__FALSH__TYPE_3_H__` to correct `__FLASH_NOR_UNLOCK_H__`; public `configure_flash3` -> `configure_flash_nor_unlock`; internal `flash3_*` helpers -> `flash_nor_unlock_*`.
- `flash_type_4.{h,cpp}` -> `flash_5v_page.{h,cpp}` via `git mv`; guard fixed from a three-way mismatch (`__FALSH__TYPE_4_H__` on `#ifndef`/`#define` vs `__FLASH__TYPE_4_H__` on the trailing `#endif` comment) to a single correct `__FLASH_5V_PAGE_H__`; public `configure_flash4` -> `configure_flash_5v_page`; internal `flash4_*` helpers (including the `flash4_page_size` static function) -> `flash_5v_page_*`.
- `memory.cpp` updated at all four call sites (2 `#include`s + protocol-chain dispatch arm for `PROTO_FLASH_NOR_UNLOCK`/`PROTO_FLASH_5V_PAGE` + legacy `mem_type` fallback arm for `TYPE_FLASH_TYPE_3`/`TYPE_FLASH_TYPE_4`) to reference the renamed headers/functions; `flash_utils.h`/`flash_utils.cpp` descriptive comments updated to name the new handlers.
- Verified via full clean rebuild: `pio run -t clean && pio run -e uno && pio run -e leonardo` both SUCCESS. Leonardo flash usage unchanged at 25654 B / 89.5% (identical to the pre-rename baseline), confirming a pure identifier rename with zero behavior or size change.

## Task Commits

Each task was committed atomically:

1. **Task 1: git mv + rename flash_type_3 -> flash_nor_unlock (0x06 handler)** - `99c6f7d` (feat)
2. **Task 2: git mv + rename flash_type_4 -> flash_5v_page (0x05 + phantom handler)** - `63e130e` (feat)
3. **Task 3: Update memory.cpp dispatch + flash_utils comments; compile both boards** - `e636af7` (feat)

_Note: all three commits were made inside the `firestarter/` submodule, on its current branch `v1.19-protocol-naming-labels` (no gitlink bump — consistent with standing policy)._

## Files Created/Modified
- `firestarter/include/flash_nor_unlock.h` - renamed header (was flash_type_3.h), guard `__FLASH_NOR_UNLOCK_H__`, declares `configure_flash_nor_unlock`
- `firestarter/src/proms/flash_nor_unlock.cpp` - renamed source (was flash_type_3.cpp), public entry `configure_flash_nor_unlock`, internal helpers renamed to `flash_nor_unlock_*` stem
- `firestarter/include/flash_5v_page.h` - renamed header (was flash_type_4.h), guard `__FLASH_5V_PAGE_H__`, declares `configure_flash_5v_page`
- `firestarter/src/proms/flash_5v_page.cpp` - renamed source (was flash_type_4.cpp), public entry `configure_flash_5v_page`, internal helpers renamed to `flash_5v_page_*` stem (incl. `flash_5v_page_page_size`)
- `firestarter/src/proms/memory.cpp` - `#include` lines + all 4 dispatch call sites updated to renamed headers/functions
- `firestarter/include/flash_utils.h` - comment referencing `flash_type_3`/`flash_type_4` updated to `flash_nor_unlock`/`flash_5v_page`
- `firestarter/src/proms/flash_utils.cpp` - comment referencing `flash3`/`flash4` updated to `flash_nor_unlock`/`flash_5v_page`

## Decisions Made
- Renamed the file-internal `flash3_*`/`flash4_*` static helpers to the `flash_nor_unlock_*`/`flash_5v_page_*` stem for full consistency within each file (discretionary choice explicitly offered by `104-PATTERNS.md` §internal-helpers; these symbols are file-internal with no cross-repo dependency, so the extra rename carries zero risk).
- Left the pre-existing, unrelated `platformio.ini` whitespace diff (trailing-space removal on a `; -D SERIAL_DEBUG` comment line, present before this plan started) untouched — it is out of this plan's declared `files_modified` scope and was not introduced by this work.

## Deviations from Plan

None - plan executed exactly as written. The optional internal-helper rename (flagged as "discretionary" in 104-PATTERNS.md) was taken, matching the plan's own `<action>` instructions for both Task 1 and Task 2.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plans 02 and 03 (native test-suite dir renames: `test_val_flash3` -> `test_val_nor_unlock`, `test_val_flash4` -> `test_val_5v_page`) are unblocked. The following files still reference the old `flash_type_3`/`flash_type_4`/`configure_flash3`/`configure_flash4` names by design (explicitly out of this plan's scope, called out in the 104-01-PLAN.md artifacts note): `test/native/avr/test_val_flash3/test_val_flash3.cpp`, `test/native/avr/test_val_flash4/test_val_flash4.cpp`, `test/native/avr/test_dispatch/test_configure_memory.cpp`, `test/native/avr/_shared/validation_matrix.h`.
- No blockers. Both firmware boards compile green; wire protocol integers, `TYPE_FLASH_TYPE_3`/`TYPE_FLASH_TYPE_4` `#define`s, `chip_database.json`, and CLI grammar were all left untouched per the plan's prohibitions (GATE-01/02/03 non-regression intact).

---
*Phase: 104-rename-protocol-header-and-cpp-files-to-descriptive-protocol*
*Completed: 2026-07-02*

## Self-Check: PASSED

All created files verified present on disk (firestarter/include/flash_nor_unlock.h,
firestarter/include/flash_5v_page.h, firestarter/src/proms/flash_nor_unlock.cpp,
firestarter/src/proms/flash_5v_page.cpp) and all commit hashes verified present in
git history (firestarter submodule: 99c6f7d, 63e130e, e636af7; meta repo: ab6bc67).
