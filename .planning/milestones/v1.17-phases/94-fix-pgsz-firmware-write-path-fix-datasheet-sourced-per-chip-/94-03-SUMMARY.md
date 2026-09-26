---
phase: 94-fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-
plan: "03"
subsystem: firmware-diagnostics
tags: [flash4, w29c040, boot-block, eprom-operations, codegen, messages, native-test]

# Dependency graph
requires:
  - phase: 94-01
    provides: FIX-01a firmware erase guard (protocol 0x05 blocked from 12V erase)
  - phase: 94-02
    provides: PGSZ-02/03 page-size wire field (handle->page_size + host emit)
  - phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
    provides: H5 confirmed silicon boot-block lockout; 16K boundary (0x3F00 FAIL / 0x4000 PASS)
provides:
  - "FIX-01b host heuristic: flash4 verify-timeout in first/last 16K emits boot-block inference hint"
  - "FIX-01b firmware §6.6 DETECT: flash4_detect_boot_block_lockout() in flash_type_4.cpp"
  - "MSG_ERR_FL4_BOOT_BLOCK_LOCKED (0xBC) — codegen-emitted, lockstep host+firmware"
  - "FIX-02 confirmed: golden write trace and dispatch-mirror guard unchanged after Plan 01+02"
  - "16 native tests in test_val_flash4 (was 14)"
  - "703 host tests pass"
affects: [94-04, phase-95]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Boot-block hint in error render path: extract failing address from MSG id_frame param,
       apply 16K boot-block boundary check (< 0x4000 / >= mem_size - 0x4000), append inference
       text only when address falls in known boot-block region"
    - "Firmware detect via reused FLASH_ENABLE_ID / FLASH_DISABLE_ID command tables (§6.6
       uses same ID-mode entry/exit as chip-ID read)"
    - "Native test: force poll timeout by setting data_buffer[0]=0xFF while stub returns 0x00;
       scripted-byte mock returns 0xFF at detect address 0x00002 (re-assign AFTER configure_memory
       to override Pitfall 3)"

key-files:
  created:
    - firestarter_app/tests/test_boot_block_hint.py
  modified:
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/messages.py
    - firestarter_app/tools/catalog/messages.toml
    - firestarter/include/messages.h
    - firestarter/src/proms/flash_type_4.cpp
    - firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp

key-decisions:
  - "FIX-01b host heuristic is the primary deliverable; firmware DETECT is the STRETCH (bonus) layer"
  - "Hint uses inference language ('may be locked') not confirmation — T-94-MISLABEL mitigated"
  - "Detect runs ONLY on error path (poll timeout) — golden write trace (clean data) unaffected (FIX-02)"
  - "MSG_ERR_FL4_BOOT_BLOCK_LOCKED = 0xBC: next free id in 0xBx range above 0xBB"
  - "Detect address: 0x00002 for first 16K block; 0x7FFF2 for last 16K block (per W29C040 §6.6)"
  - "Platform: 0xFF = locked, 0xFE = unlocked (W29C040 §6.6 spec)"
  - "golden_flash4_write.inc NOT re-blessed — trace confirmed identical; no re-pin needed"

patterns-established:
  - "codegen-only messages: new firmware errors added to messages.toml, regenerated via codegen, never hand-edited"
  - "test_boot_block_hint.py pattern: drive _boot_block_hint_message() directly with synthetic Response objects"

requirements-completed: [FIX-01, FIX-02]

# Metrics
duration: ~90min (across 2 sessions)
completed: 2026-06-27
---

# Phase 94 Plan 03: FIX-01b Boot-Block Locked Diagnostics Summary

**W29C040 §6.6 boot-block lockout diagnosed host-side (heuristic hint) and firmware-side (DETECT read); MSG_ERR_FL4_BOOT_BLOCK_LOCKED 0xBC added via codegen; golden write trace confirmed unchanged**

## Performance

- **Duration:** ~90 min (two sessions)
- **Started:** 2026-06-26
- **Completed:** 2026-06-27
- **Tasks:** 3 (Task 1 primary, Task 2 verification, Task 3 stretch — all done)
- **Files modified:** 7 (4 host app, 3 firmware)

## Accomplishments

- **FIX-01b host heuristic (primary)**: `_boot_block_hint_message()` in `eprom_operations.py` appends an inference hint to any flash4 `MSG_ERR_FL4_VERIFY_TIMEOUT` whose failing address is in the first 16K (< 0x4000) or last 16K (>= mem_size - 0x4000). Mid-region addresses are unaffected (T-94-MISLABEL mitigated). 7 host tests in `test_boot_block_hint.py` cover first-16K, boundary inclusive/exclusive, last-16K, mid-region no-hint, non-flash4 protocol, and non-timeout message id.
- **FIX-01b firmware DETECT (stretch, shipped)**: `flash4_detect_boot_block_lockout()` in `flash_type_4.cpp` performs the W29C040 §6.6 DETECT read (FLASH_ENABLE_ID → read 0x00002 or 0x7FFF2 → FLASH_DISABLE_ID). On confirmed lock (status == 0xFF), emits `MSG_ERR_FL4_BOOT_BLOCK_LOCKED` instead of the generic timeout. Runs only on error path — golden write trace unaffected.
- **MSG_ERR_FL4_BOOT_BLOCK_LOCKED = 0xBC**: Added to `messages.toml`, regenerated `messages.py` (66 messages, ruff-clean, idempotent) and `messages.h` via codegen. Drift gate confirmed: fresh codegen matches disk exactly.
- **FIX-02 confirmed**: `pio test -e native` 110/110 PASS; `golden_flash4_write.inc` not re-blessed — trace is byte-identical after Plan 01+02 changes.
- **Flash budget**: Leonardo 25560 / 28672 B = 89.1% (within 92% ceiling; headroom confirmed before proceeding with stretch task).

## Task Commits

1. **Task 1: FIX-01b host heuristic hint + test** — `c4c68c4` (feat — firestarter_app)
2. **Task 2: FIX-02 golden trace confirmation** — (verified by native test run; golden .inc unchanged, no separate commit needed)
3. **Task 3 (stretch): firmware DETECT + 0xBC catalog** — firmware `2e91503`, host `d7d0a7e`
   - `2e91503`: feat(94-03) FIX-01b firmware §6.6 boot-block detect + native test (firestarter)
   - `d7d0a7e`: feat(94-03) add MSG_ERR_FL4_BOOT_BLOCK_LOCKED (0xBC) to messages catalog (firestarter_app)
4. **Meta gitlinks bump** — `f6818ff` (chore — meta-repo)

## Files Created/Modified

- `/workspaces/firestarter_app/firestarter/eprom_operations.py` — added `_BOOT_BLOCK_SIZE`, `_TIMEOUT_ADDR_RE`, `_FLASH4_PROTOCOL_ID` constants; `_boot_block_hint_message()`; modified `_main_phase_send_data` to accept `eprom_data_dict` and apply hint on ERROR
- `/workspaces/firestarter_app/tests/test_boot_block_hint.py` — 7 tests for FIX-01b host heuristic
- `/workspaces/firestarter_app/tools/catalog/messages.toml` — added 0xBC entry (MSG_ERR_FL4_BOOT_BLOCK_LOCKED)
- `/workspaces/firestarter_app/firestarter/messages.py` — regenerated via codegen (66 messages, ruff-clean)
- `/workspaces/firestarter/include/messages.h` — regenerated via codegen (added `#define MSG_ERR_FL4_BOOT_BLOCK_LOCKED 0xBC`)
- `/workspaces/firestarter/src/proms/flash_type_4.cpp` — added `flash4_detect_boot_block_lockout()`; hooked in `flash4_wait_for_page_write` error path
- `/workspaces/firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` — added `flash4_mock_boot_block_locked_get_data` scripted-byte mock; `test_fix01b_boot_block_locked_sets_error_code`; `test_fix01b_clean_write_no_boot_block_detect`

## Decisions Made

- Hint inference-worded ("may be locked") to satisfy T-94-MISLABEL: host can only infer from address range; only firmware DETECT can confirm via the 0xFF/0xFE status byte.
- Firmware DETECT proceeds only when address is in boot-block region (caller guards); region check: `addr < 0x4000` OR `mem_size > 0x4000 && addr >= mem_size - 0x4000`.
- Detect uses FLASH_ENABLE_ID / FLASH_DISABLE_ID (same tables as chip-ID read) — no new command sequences needed.
- No re-bless of golden traces: FIX-01a is host-only (no firmware change); PGSZ-02 W29C040 page_size resolves to 256 identical to heuristic; detect only runs on error path.

## Deviations from Plan

None — plan executed exactly as specified. All three tasks completed:
- Task 1 (primary): host heuristic hint, 7 tests
- Task 2: FIX-02 confirmed, no re-pin
- Task 3 (stretch): firmware DETECT shipped (budget 89.1% < 92% ceiling)

## Known Stubs

None — no hardcoded placeholder values introduced.

## Threat Flags

None — no new network endpoints, auth paths, or file access patterns introduced.

## Issues Encountered

- ruff UP032 (format() → f-string) and UP006 (Optional[Dict] → Optional[dict]) in initial eprom_operations.py implementation — fixed before commit.
- Hint text initially used "may have" instead of "may be locked" — fixed to match test assertion.
- `git diff --exit-code` on messages.py showed uncommitted changes (correct: changes not yet staged). Verified idempotency by comparing fresh codegen output against disk: diff empty.

## Next Phase Readiness

- Plan 94-04 (writable-region proof) can proceed: FIX-01b host + firmware diagnostics shipped, FIX-02 golden trace confirmed, flash budget 89.1%.
- W29C040 §6.6 boot-block lockout is now surfaced with clear diagnostics (heuristic host + confirmed firmware DETECT).
- Page-0 non-programmability remains documented as a Phase-93 hardware block; Plan 04 demonstrates the writable region (0x4000+).

---
*Phase: 94-fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-*
*Completed: 2026-06-27*

## Self-Check: PASSED

- test_boot_block_hint.py: FOUND
- 94-03-SUMMARY.md: FOUND
- c4c68c4 (host heuristic hint): FOUND
- d7d0a7e (messages.toml + messages.py 0xBC): FOUND
- 2e91503 (firmware DETECT + native test): FOUND
- f6818ff (meta gitlinks bump): FOUND
- 8bb7f87 (metadata commit): FOUND
