---
status: complete
phase: 54-even-block-data-transfers-full-buffer-aligned-host-fw-chunks
source: [54-01-SUMMARY.md, 54-02-SUMMARY.md, 54-03-SUMMARY.md]
started: 2026-06-04T15:00:44Z
updated: 2026-06-04T16:30:00Z
---

## Current Test

[testing complete — 5/5 passed; 1 sub-issue resolved (R1 recalibration); 2 items captured to backlog]

## Tests

### 1. Firmware advertises maxchunk in identity string
expected: Firmware identity is a 4-field string `<ver>:<board>:<buf>:<maxchunk>` (e.g. `3.0.0b8:uno:512:512`); 4th field equals full DATA_BUFFER_SIZE (512 Uno / 1024 Leonardo).
result: pass
note: "Verified live by Claude. Flashed Phase 54 firmware to uno328pb (Rev 2.0 shield, socket empty). `firestarter fw` reports 4-field identity `3.0.0b6:uno328pb:512:512` — 4th field (maxchunk)=512=DATA_BUFFER_SIZE. Host FW-handshake (real write/verify probe path) parses firmware_max_chunk=512 and _calculate_buffer_size() returns 512 (full buffer, no buf−2). MINOR OBSERVATION: firmware version field still reads `3.0.0b6`, not the `3.0.0b8` used illustratively in the 54-01 SUMMARY — the version macro was not bumped this phase. Not an EVEN-01 deliverable (the 4th maxchunk field is the deliverable and is present/correct), but flag for a version-bump before the v1.10 beta cut."

### 2. Full-buffer write/verify against a real EPROM
expected: Writing then verifying an EPROM (e.g. `./write_test.sh [EPROM]`) completes successfully. Host→fw data blocks are now full buffer-sized (512 Uno / 1024 Leonardo) with NO `buffer−2` reduction. Even-block transfer — 65536-byte chips divide cleanly with no remainder/short final chunk.
result: pass
note: |
  PASS — full-buffer even-block write+verify completed end-to-end on the LEONARDO
  (board swap mid-test). Sequence on /dev/ttyACM0 after flashing Phase 54 firmware
  (identity 3.0.0b6:leonardo:1024:1024, maxchunk=1024):
    • write all-0x00 64KB, -b -f → 0x10000/0x10000 complete in 83s (1024-byte
      even-block chunks, 64 chunks, NO buf−2; 65536 % 1024 == 0)
    • verify → "Verify for W27C512 successful (5.59s)"
    • independent read-back → byte-IDENTICAL to source (cmp clean, full 64KB)
  EVEN-01 transport also corroborated on the uno328pb (Test 1: maxchunk=512,
  _calculate_buffer_size()=512; 72×512B chunks streamed on the read path).

  RESOLVED sub-issue (originally logged here): firmware reported "VPP is low: 1.8V"
  while bench multimeter read ~12.2V. Root cause = stale EEPROM R1=1000 (should be
  270000); recalibrated via `firestarter config -r1 270000` → VPP then read
  correctly. Latent firmware default-propagation bug captured to backlog (see Gaps).

  SEPARATE bench/hardware finding (NOT EVEN-01, captured to backlog): on the
  uno328pb + Rev 2.0, the chip-PROGRAM path hangs on the first block (deterministic
  across 6 attempts incl. reflash + reseat + random/zero payloads; firmware stops
  responding the moment it drives program current at VPP 12.7V / VCC 5.3V —
  suspected VPP-regulator brownout). The SAME firmware + chip + calibration writes
  & verifies perfectly on the Leonardo, proving the hang is uno328pb-board-specific.

### 3. Outdated-firmware rejection (no silent fallback)
expected: When connected to firmware that does NOT advertise the maxchunk field (old/3-field identity), the host raises a clear `FirmwareOutdatedError` and refuses to proceed — it does NOT silently fall back to the old `buf−2` chunk size.
result: pass
note: "Verified live by Claude against the real board on /dev/ttyUSB0 (running pre-Phase-54 firmware 3.0.0b6:uno328pb:512 — 3-field identity, no maxchunk). Host parsed firmware_max_chunk=None and _calculate_buffer_size() raised FirmwareOutdatedError: 'Firmware does not advertise a max-chunk capacity field. Please upgrade the firmware using firestarter fw --install.' No silent buf−2 fallback. Non-destructive (FW-identity read only, no chip operation)."

### 4. Firmware builds within RAM ceiling on all three boards
expected: `pio run -e uno`, `-e uno328pb`, and `-e leonardo` all build SUCCESS. RAM stays well within the 2 KB / 2.5 KB SRAM (Uno 1552 B / 496 B free, uno328pb 1556 B / 492 B free, Leonardo 1993 B / 567 B free). Firmware links and runs. (Note: Uno/uno328pb exceed the Phase-50-vintage 1503 B literal ceiling — attributed to Phase 53 growth, not Phase 54; Phase 54 added only 4 B.)
result: pass
note: "Verified live by Claude — all 3 builds SUCCESS; RAM matched summaries exactly (Uno 1552B/496 free, uno328pb 1556B/492 free, Leonardo 1993B/567 free)."

### 5. Dual-repo test suites + frame-vectors drift gate green
expected: Firmware native suite 42/42 PASSED (all 7 allowlisted suites incl. test_frame_vectors). Host suite 456/456 PASSED, coverage ≥ 70% (71.55%). frame-vectors drift gate clean in BOTH repos (12 vectors, exit 0), TOML byte-identical across repos, and CMD_FRAME_MAX parity (firmware == host == 512).
result: pass
note: "Verified live by Claude — FW native 42/42 succeeded; host 456 passed (71.55% cov, floor 70); FW+host codegen --check exit 0 (12 vectors); TOML diff exit 0 (byte-identical); CMD_FRAME_MAX firmware=DATA_BUFFER_SIZE(512)==host 512."

## Summary

total: 5
passed: 5
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

# RESOLVED during this UAT session — kept for the record. EVEN-01 itself had NO gaps;
# Test 2's full write+verify now passes (on Leonardo). The two follow-ups below are
# OUT of EVEN-01 scope and were captured to backlog per operator decision.

- truth: "Firmware reports an accurate VPP voltage (≈12V) so the program/write path can complete; full-buffer even-block write+verify of an EPROM succeeds end-to-end."
  status: resolved
  resolution: "Stale EEPROM R1=1000 on the uno328pb recalibrated to 270000 via `firestarter config -r1 270000` → VPP then read correctly. Full write+verify subsequently completed end-to-end on the Leonardo (1024-byte even-block, 64KB, read-back byte-identical). EVEN-01 transport verified sound throughout."
  reason: "User reported: This is a fw bug, it measures 12.2v — firmware reported 'VPP is low: 1.8V < 12.0V' while bench multimeter measured ~12.2V. Misread blocked the program path."
  severity: major
  test: 2
  root_cause: "Stale EEPROM calibration on this uno328pb board: rurp_configuration_t.r1 holds the legacy ~1000 instead of the correct 270000. rurp_read_voltage_mv math is correct — gain = (r1+r2)/r2; with r1=1000,r2=44000 gain≈1.02× so true 12.2V computes as ≈1.75V≈1.8V (exact symptom + 6.8× ratio match). Latent firmware bug: rurp_validate_config re-applies defaults ONLY when config->version != CONFIG_VERSION ('VER06'); Phase 44 changed VALUE_R1 default 1000→270000 in rurp_shield.h WITHOUT bumping CONFIG_VERSION, so already-calibrated boards keep the stale r1 forever — the code fix never reaches their EEPROM. PRE-EXISTING; Phase 54 (f8249b8/c1ae294) touched only COBS cap + FW identity + native tests, not VPP/r1/config code. EVEN-01 transport itself verified sound (72×512B chunks streamed)."
  artifacts:
    - path: "firestarter/src/boards/rurp_common.cpp:52-71"
      issue: "rurp_read_voltage_mv — math correct but trusts stale EEPROM r1/r2"
    - path: "firestarter/src/rurp_config_utils.cpp:32-39"
      issue: "rurp_validate_config — version-gated default refresh; changed default never reaches an already-calibrated board"
    - path: "firestarter/include/rurp_shield.h:46,49-50"
      issue: "CONFIG_VERSION 'VER06' not bumped when VALUE_R1 default changed 1000→270000 (Phase 44); VALUE_R2 44000"
  missing:
    - "BENCH (immediate, non-code): recalibrate this board's EEPROM R1 to 270000 (firestarter config), then re-run Test 2 full write+verify"
    - "FIRMWARE (durable, separate from EVEN-01 scope): make corrected R1/R2 defaults propagate to already-calibrated boards — bump CONFIG_VERSION on default change, OR add a sanity-range guard rejecting implausible r1, OR a targeted r1==1000 migration"
  debug_session: .planning/debug/firmware-vpp-misread.md

## Backlog (out of EVEN-01 scope — captured for future phases)

- item: "Firmware: corrected R1/R2 calibration defaults don't propagate to already-calibrated boards"
  origin: "Phase 54 UAT diagnosis (debug session firmware-vpp-misread.md)"
  detail: "rurp_validate_config re-applies defaults only on CONFIG_VERSION ('VER06') mismatch; Phase 44's VALUE_R1 1000→270000 change didn't bump CONFIG_VERSION, so boards calibrated under VER06 silently keep a stale r1 → wildly wrong VPP reading. Fix options: bump CONFIG_VERSION on any default change; add a sanity-range guard rejecting implausible r1; or a targeted r1==1000 migration."
  severity: major

- item: "Bench/hardware: uno328pb + Rev 2.0 chip-PROGRAM path hangs on first block (suspected VPP-regulator brownout)"
  origin: "Phase 54 UAT Test 2 (uno328pb)"
  detail: "Deterministic across 6 attempts (reflash + reseat + random/zero payloads): firmware stops responding the instant it drives program current at VPP 12.7V / VCC 5.3V; host times out at first block. SAME firmware + chip + R1=270000 calibration writes & verifies cleanly on the Leonardo (VPP 13.1V), so the fault is uno328pb-board-specific, not firmware/EVEN-01. Needs bench investigation: VPP regulator level, VCC stability under program load, board power."
  severity: major
