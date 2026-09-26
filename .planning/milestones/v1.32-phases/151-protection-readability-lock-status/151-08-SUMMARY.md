---
phase: 151-protection-readability-lock-status
plan: 08
subsystem: firmware-protocol
tags: [firmware, avr, platformio, flash, wire-protocol, unity]

# Dependency graph
requires:
  - phase: 151-03
    provides: "CMD_LOCK_STATUS 16, is_memory_cmd()'s ninth admitted case, the widened parse gate"
  - phase: 151-04
    provides: "151-SEQUENCES.md — the two pinned, cited byte tables this plan transcribes"
  - phase: 151-05
    provides: "MSG_DATA_PROTECTION_STATUS = 0xE1, DATA severity, two u8 params"
provides:
  - "flash_util_read_in_id_mode(handle, address) — shared AMD/JEDEC ID-mode single-byte read, beside flash_util_get_chip_id"
  - "Pinned, cited constants: FLASH_NOR_UNLOCK_PROTECT_VERIFY_ADDR/_UNPROTECTED/_PROTECTED (0x06); FLASH_5V_PAGE_BOOT_BLOCK_STATUS_ADDR/_UNLOCKED/_LOCKED (0x05)"
  - "flash_nor_unlock_read_protection_execute and flash_5v_page_read_protection_execute, each reached by one new CMD_LOCK_STATUS dispatch arm"
  - "eprom_lock_status + loop()'s CMD_LOCK_STATUS arm — the command now reaches an operation end-to-end"
  - "Five new native legs each in test_val_nor_unlock.cpp / test_val_5v_page.cpp: dispatch, sequence pinning, 5V-only, raw-byte fidelity, mode bracketing"
affects: [151-09, 151-10, 151-11, 151-13]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A protect-verify read is the existing AMD/JEDEC ID-mode entry/exit with a caller-supplied read address, not a new sequence — flash_util_get_chip_id and flash_util_read_in_id_mode now share that mode explicitly."
    - "Raw silicon byte rides the wire unmodified; a firmware decode failure degrades to RESPONSE_CODE_WARNING + 0xFF, never coerced into a definite class and never an ERROR."
    - "Wire-byte capture in a native Unity suite via ArduinoFake's Serial.write(uint8_t) AlwaysDo hook (test_messages/test_rurp_log_id.cpp precedent), reused here to assert on an emitted DATA id-frame's exact bytes."

key-files:
  created: []
  modified:
    - firestarter/include/flash_utils.h
    - firestarter/src/proms/flash_utils.cpp
    - firestarter/include/flash_nor_unlock.h
    - firestarter/src/proms/flash_nor_unlock.cpp
    - firestarter/include/flash_5v_page.h
    - firestarter/src/proms/flash_5v_page.cpp
    - firestarter/include/eprom_operations.h
    - firestarter/src/eprom_operations.cpp
    - firestarter/src/firestarter.cpp
    - firestarter/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp
    - firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp

key-decisions:
  - "Decided AGAINST emitting the pre-existing MSG_WARN_FL4_BOOT_BLOCK_LOCKED (0x85) on the 0x05 reads-as-locked branch: its catalog wording ('...not programmable... write forced') is worded for a write-path failure this read-only operation never causes, and emitting it would misrepresent an observation as a write event against a tight Caterina-cliff budget. Decision recorded in a code comment; the id stays available, unemitted, for a future write-path pre-flight."
  - "flash_util_get_chip_id left functionally unchanged — re-expressing it on top of flash_util_read_in_id_mode would enter/exit ID mode twice for what is today one entry/exit pair; both chip-ID native legs still pass unmodified, proving no regression."
  - "Neither family file references the literal force-flag macro name, satisfying the source-scan gate while still documenting the reasoning (--force is host-side-only per 151-DESIGN.md §6/C-16) via periphrasis ('the 0x01 force ctrl flag') rather than the literal token."
  - "Mode-bracketing leg asserts POSITION (7 total MSB-register writes: 3 entry + 1 read + 3 exit) rather than raw byte-value pattern matching, because FLASH_ENABLE_ID and FLASH_DISABLE_ID share byte-identical addresses (0x5555/0x2AAA/0x5555) — only the differing DATA byte (unrecorded by the bus stub) distinguishes them, so position is the only reliable oracle."

patterns-established:
  - "A read-only status operation reports its raw observation unconditionally and downgrades an unrecognised value to WARNING rather than ERROR or a coerced guess — the shape any future protection-status read in this codebase should copy."

requirements-completed: []

coverage:
  - id: D1
    description: "flash_util_read_in_id_mode + pinned, cited sequence constants for both 0x06 and 0x05 families, transcribed byte-for-byte from 151-SEQUENCES.md"
    verification:
      - kind: unit
        ref: "test_val_nor_unlock.cpp#test_nor_unlock_lock_status_pinned_sequence, test_val_5v_page.cpp#test_5v_page_lock_status_pinned_sequence"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both families reach a CMD_LOCK_STATUS operation through one new dispatch arm each, emitting a two-byte DATA frame (raw byte + decode code) with an unrecognised value surfacing as 0xFF/WARNING, never coerced"
    verification:
      - kind: unit
        ref: "test_val_nor_unlock.cpp#test_nor_unlock_lock_status_dispatch,#test_nor_unlock_lock_status_raw_byte_fidelity; test_val_5v_page.cpp#test_5v_page_lock_status_dispatch,#test_5v_page_lock_status_raw_byte_fidelity"
        status: pass
    human_judgment: false
  - id: D3
    description: "The 0x06/0x05 CMD_LOCK_STATUS operations are 5V-only reads — no VPP-enable control-register bit ever appears"
    verification:
      - kind: unit
        ref: "test_val_nor_unlock.cpp#test_nor_unlock_lock_status_no_vpp; test_val_5v_page.cpp#test_5v_page_lock_status_no_vpp"
        status: pass
    human_judgment: false
  - id: D4
    description: "eprom_lock_status + loop()'s CMD_LOCK_STATUS arm reach the command end-to-end; default: arm (MSG_ERR_UNKNOWN_CMD) undisturbed"
    verification:
      - kind: other
        ref: "python3 source-scan (see Task 3 verify block) confirming eprom_lock_status has no LOG_DEBUG_ID_SUB and loop()'s default: arm unchanged"
        status: pass
    human_judgment: false
  - id: D5
    description: "All three native envs pass with platformio.ini and include/messages.h untouched; leonardo stays inside the unguarded 28672 B Caterina cliff"
    verification:
      - kind: other
        ref: "pio test -e native (163/163), -e native_nodevtools (163/163), -e native_pinmap_provisional (11/11); git diff --stat platformio.ini and git status --porcelain include/messages.h both empty; pio run -e leonardo -> 27500 B, margin 1172 B (UNGUARDED)"
        status: pass
    human_judgment: false

duration: ~70min
completed: 2026-08-20
status: complete
---

# Phase 151 Plan 08: `CMD_LOCK_STATUS` Read Sequences Summary

**Landed both protection-status read sequences end-to-end — a shared AMD/JEDEC ID-mode single-byte read, two family-specific operations emitting a two-byte raw-byte-plus-decode DATA frame, their dispatch arms, and the `loop()` arm — with five new native legs per family proving dispatch, pinned bytes, 5V-only safety, raw-byte fidelity, and mode bracketing.**

## Performance

- **Duration:** ~70 min
- **Started:** ~2026-08-20T15:00Z (approximate — not captured at session start)
- **Completed:** 2026-08-20T16:10Z
- **Tasks:** 3 completed
- **Files modified:** 11 (7 firmware source/header, 2 firmware native-test, 2 firmware include-header-only for family declarations)

## Accomplishments

- `flash_util_read_in_id_mode(handle, address)` added beside `flash_util_get_chip_id` in `flash_utils.{h,cpp}`: `FLASH_ENABLE_ID` → one `handle->firestarter_get_data` read → `FLASH_DISABLE_ID`. `flash_util_get_chip_id` itself is untouched — both its native legs (in each family suite) still pass unmodified.
- Both sequences pinned as named, cited constants in `flash_utils.h`, transcribed byte-for-byte from `151-SEQUENCES.md` (comparison table below): `FLASH_NOR_UNLOCK_PROTECT_VERIFY_ADDR`/`_UNPROTECTED`/`_PROTECTED` for the 0x06 AMD Autoselect family, `FLASH_5V_PAGE_BOOT_BLOCK_STATUS_ADDR`/`_UNLOCKED`/`_LOCKED` for the 0x05 Winbond family. Neither mode entry/exit needed a new `byte_flip_t` table — both reuse `FLASH_ENABLE_ID`/`FLASH_DISABLE_ID` verbatim, exactly as `151-SEQUENCES.md` records. `flash_utils.h` carries the required "change detector, not a correctness proof" sentence and a `§`-cited provenance comment for each sequence; no `_BOOT_BLOCK_SIZE`/`0x4000` geometry constant was introduced; `FLASH_ENABLE_WRITE_PROTECTION`/`FLASH_DISABLE_WRITE_PROTECTION` remain referenced by zero lines in the three `src/proms/` files this plan touches.
- `flash_nor_unlock_read_protection_execute` and `flash_5v_page_read_protection_execute` each reached by one new `CMD_LOCK_STATUS` dispatch arm (modelled on the existing `CMD_CHECK_CHIP_ID` query arm); `flash_nor_unlock`'s arm nulls `firestarter_operation_init` (this file assigns one before the switch), `flash_5v_page`'s does not (it never assigns one). Neither switch gained a `default:` arm. Neither file references the force-control-flag macro name on this path — a comment in each explains why (151-DESIGN.md §6/C-16) without reintroducing the literal token the source-scan gate forbids.
- Byte 0 of the emitted `MSG_DATA_PROTECTION_STATUS` payload is always the raw silicon byte, unmodified; byte 1 is `0x00`/`0x01` on a definite decode (`RESPONSE_CODE_OK`) or `0xFF` on an unrecognised value (`RESPONSE_CODE_WARNING`, never `ERROR` — the DATA frame still reaches the host either way).
- Decided explicitly **against** emitting the pre-existing `MSG_WARN_FL4_BOOT_BLOCK_LOCKED` (0x85) on the 0x05 reads-as-locked branch: its catalog format string ("...not programmable... write forced") is worded for a write-path failure this read-only operation never causes. The decision and its byte-budget/semantic-mismatch reasoning is recorded in a code comment; the id stays unemitted, available for a future write-path pre-flight.
- `eprom_lock_status` added to `eprom_operations.{h,cpp}` in `eprom_blank_check`'s single-step shape but **without** a `LOG_DEBUG_ID_SUB` line, per `151-DESIGN.md` §7 (command 16 falls outside the diagnostic-ordinal range at `firestarter.cpp:132-142`, unchanged by this phase). `loop()` gained exactly one `CMD_LOCK_STATUS` arm after `CMD_SDP_LOCK`, outside every preprocessor conditional; the `default:` arm (`MSG_ERR_UNKNOWN_CMD`) is byte-for-byte undisturbed.
- Five new legs landed in **both** `test_val_nor_unlock.cpp` and `test_val_5v_page.cpp` (no new native suite — the 17-entry `test_filter` is untouched): **(1) Dispatch** — `firestarter_operation_main`/`_init` wiring, matching each file's own rule. **(2) Sequence pinning** — every `{address, byte}` pair and named constant asserted by symbol, docstring states "change detector, not a correctness proof" verbatim. **(3) 5V-only** — no VPP-enable bit in any recorded `CONTROL_REGISTER` write during the actual operation (not just configure phase). **(4) Raw-byte fidelity** — a stubbed unrecognised raw value (`0x37`) survives onto the wire byte-for-byte with the `0xFF` sentinel, captured via a `Serial.write` hook (the `test_messages`/`test_rurp_log_id.cpp` precedent). **(5) Mode bracketing** — asserts the *position* of 7 total `MOST_SIGNIFICANT_BYTE`-register writes (3 entry + 1 read + 3 exit), because `FLASH_ENABLE_ID`/`FLASH_DISABLE_ID` share byte-identical addresses and only their unrecorded DATA byte distinguishes them — position, not value-pattern, is the only valid oracle. `test_val_nor_unlock.cpp`'s `setUp` additionally needed a `delayMicroseconds` stub, newly required once its legs execute a real operation body rather than only `configure_memory`.
- Full firmware pytest suite (`tests/`) run on the fully committed tree: **315 passed**, confirming no pinned-line-number regression (`test_config_schema_pinned.py`'s 3 `firestarter.cpp` sites at lines 41/119/125 are unaffected — this plan's edits all land after line 150).

## Task Commits

Each task was committed atomically in `firestarter/`:

1. **Task 1: `flash_util_read_in_id_mode` and the pinned sequence tables** — `8db7e55` (feat)
2. **Task 2: The two family read operations and their dispatch arms** — `0444b1c` (feat)
3. **Task 3: The `loop()` arm, `eprom_lock_status`, and native legs in both existing family suites** — `3ff9f34` (feat)

**Plan metadata:** recorded in this SUMMARY commit (meta repo).

_Note: this plan's `commits_land_in: [firestarter]` — no meta-repo code commit exists for Tasks 1-3; only STATE.md/ROADMAP.md/this SUMMARY and the firestarter gitlink bump are committed in the meta repo._

## Files Created/Modified

- `firestarter/include/flash_utils.h` — `flash_util_read_in_id_mode` declaration; pinned, cited sequence/decode constants for both families
- `firestarter/src/proms/flash_utils.cpp` — `flash_util_read_in_id_mode` definition
- `firestarter/include/flash_nor_unlock.h` — `flash_nor_unlock_read_protection_execute` declaration
- `firestarter/src/proms/flash_nor_unlock.cpp` — the operation, its `CMD_LOCK_STATUS` dispatch arm
- `firestarter/include/flash_5v_page.h` — `flash_5v_page_read_protection_execute` declaration
- `firestarter/src/proms/flash_5v_page.cpp` — the operation (with the boot-block-warning non-emission decision comment), its `CMD_LOCK_STATUS` dispatch arm
- `firestarter/include/eprom_operations.h` — `eprom_lock_status` declaration
- `firestarter/src/eprom_operations.cpp` — `eprom_lock_status` definition
- `firestarter/src/firestarter.cpp` — `loop()`'s `CMD_LOCK_STATUS` arm
- `firestarter/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp` — 5 new legs, wire-capture setUp, `delayMicroseconds` stub
- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` — 5 new legs, wire-capture setUp

## Byte-for-byte comparison: `151-SEQUENCES.md` vs. landed firmware

| Sequence element | `151-SEQUENCES.md` | Firmware (`flash_utils.h` / existing tables) | Match |
|---|---|---|---|
| Seq A (0x06) mode entry | `{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0x90}` | `FLASH_ENABLE_ID` (unchanged, reused) | Yes |
| Seq A (0x06) mode exit | `{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0xF0}` | `FLASH_DISABLE_ID` (unchanged, reused) | Yes |
| Seq A (0x06) read address | `SA(0x0000)+0x02 = 0x0002` | `FLASH_NOR_UNLOCK_PROTECT_VERIFY_ADDR = 0x0002` | Yes |
| Seq A (0x06) decode | `0x00`=unprotected, `0x01`=protected | `FLASH_NOR_UNLOCK_PROTECT_UNPROTECTED=0x00`, `_PROTECTED=0x01` | Yes |
| Seq B (0x05) mode entry/exit | same AA/55/90 / AA/55/F0 as `FLASH_ENABLE_ID`/`_DISABLE_ID` (a finding) | `FLASH_ENABLE_ID`/`FLASH_DISABLE_ID` (unchanged, reused) | Yes |
| Seq B (0x05) read address | `0x0002` (structural analogy — lowest-confidence citation) | `FLASH_5V_PAGE_BOOT_BLOCK_STATUS_ADDR = 0x0002` | Yes |
| Seq B (0x05) decode | `0xFF`=unlocked, `0xFE`=locked | `FLASH_5V_PAGE_BOOT_BLOCK_UNLOCKED=0xFF`, `_LOCKED=0xFE` | Yes |

The 0x05 mode entry reused `FLASH_ENABLE_ID`/`FLASH_DISABLE_ID` verbatim — `151-SEQUENCES.md` records this as a **finding** (this project has no Product-ID-mode entry distinct from `FLASH_ENABLE_ID`, and `flash_util_get_chip_id` already exercises that exact sequence on this part family), not an assumption, so no new `byte_flip_t` table was authored for either family.

## Decisions Made

- Decided against emitting `MSG_WARN_FL4_BOOT_BLOCK_LOCKED` — see Accomplishments above.
- Left `flash_util_get_chip_id` functionally unchanged rather than re-expressing it atop the new helper (would double the mode entry/exit cost for a two-byte read).
- Mode-bracketing leg asserts positional shape (7 MSB writes) rather than a byte-pattern match, because `FLASH_ENABLE_ID`/`FLASH_DISABLE_ID` are byte-identical in their address table and only the unrecorded DATA byte distinguishes them.
- Neither family file spells the literal force-flag macro name, satisfying the plan's source-scan gate while still documenting the reasoning via periphrasis.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `test_val_nor_unlock.cpp` aborted (SIGABRT) on an unmocked `delayMicroseconds` call**
- **Found during:** Task 3, first run of the new `test_nor_unlock_lock_status_no_vpp` leg
- **Issue:** This suite's pre-existing legs only ever call `configure_memory()` (function-pointer wiring only, no operation body). The new CMD_LOCK_STATUS legs are the first in this suite to actually execute an operation (`flash_nor_unlock_read_protection_execute`), which reaches `memory_get_data`'s unconditional `delayMicroseconds(strobe)` call. ArduinoFake aborts on any unmocked method call, and this suite's `setUp` never stubbed `delayMicroseconds` (unlike `test_val_5v_page.cpp`'s `setUp`, which already needed it for its own operation-phase write-execute legs).
- **Fix:** Added `When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();` to `test_val_nor_unlock.cpp`'s `setUp`, mirroring the pre-existing pattern in `test_val_5v_page.cpp`.
- **Files modified:** `firestarter/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp`
- **Verification:** All 9 cases in the suite pass, including the 5 new CMD_LOCK_STATUS legs.
- **Committed in:** `3ff9f34` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary to make the new legs runnable at all; no scope creep — the fix is confined to test infrastructure already present in the sibling suite.

## Issues Encountered

- A minor commit-message imprecision in Task 3's commit (`3ff9f34`): it states leonardo's flash figure as "unchanged... from this task," but the actual delta was +2 B (27498 B → 27500 B) — the op-layer additions (`eprom_lock_status` + the `loop()` arm) are not literally free, just very cheap. Corrected here: **final leonardo flash_used = 27500 B**, Caterina margin = 28672 − 27500 = **1172 B (UNGUARDED)**. No functional impact; recorded for the record's accuracy.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `CMD_LOCK_STATUS` is now fully wired end-to-end on the firmware side: wire admission (151-03) → catalog id (151-05) → sequences and operations (this plan). Plan 151-09 (host-side wire build/parse) and 151-11 (host-side decode consumption) can now drive a real command against this firmware.
- Warm (non-cold-rebuild) `pio run` figures for all three AVR targets, **not** the 151-10 authoritative cold-rebuild measurement:
  - uno: 25418 B flash / 1575 B RAM
  - uno328pb: 25468 B flash / 1581 B RAM
  - leonardo: 27500 B flash / 2016 B RAM — Caterina margin **28672 − 27500 = 1172 B, UNGUARDED**, well inside the 1460 B budget this plan was given (total delta across all three tasks: +252 B on leonardo, from the 27248 B 151-05 baseline).
- `firestarter/tests/` = **315 passed** on the fully committed tree (`test_config_schema_pinned.py`'s 3 pinned `firestarter.cpp` sites — lines 41/119/125 — unaffected; no re-pin needed).
- Both extended native suites run locally via:
  - `pio test -e native -f "*test_val_nor_unlock*"` → 9/9 passed
  - `pio test -e native -f "*test_val_5v_page*"` → 13/13 passed
  - `pio test -e native` (all 17 filtered suites) → 163/163 passed
  - `pio test -e native_nodevtools` → 163/163 passed
  - `pio test -e native_pinmap_provisional` → 11/11 passed (includes the pre-existing `test_pinmap_provisional_refuses_cmd_lock_status` from 151-03)
- `python3 scripts/check_build_warnings.py --rebuild`: PASS — AVR `macro_redefinition == 0` on all three targets; native/native_nodevtools at 998/1166 (168 B headroom below the zero-headroom-adjacent watermark).
- `git diff --stat platformio.ini` and `git status --porcelain include/messages.h` both empty throughout.
- No requirement was flipped (`requirements: []`); this plan **advances** `LOCK-02`. Per orchestrator constraint, 151-13 owns the LOCK-02 checkbox flip and 151-10 owns funding any MERGE-05 exemption for the accumulated firmware growth — no exemption constant was authored here, matching the constraint's instruction.

---
*Phase: 151-protection-readability-lock-status*
*Completed: 2026-08-20*

## Self-Check: PASSED

All 11 files created/modified verified present on disk; all 3 commits
(firestarter `8db7e55`, `0444b1c`, `3ff9f34`) verified present in the
firestarter repository's `git log --oneline --all`.
