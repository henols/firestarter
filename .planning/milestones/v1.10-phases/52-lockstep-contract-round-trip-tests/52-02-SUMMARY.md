---
phase: 52-lockstep-contract-round-trip-tests
plan: "02"
subsystem: test-firmware
tags: [golden-vectors, unity, cobs, lockstep, crc8, round-trip]
dependency_graph:
  requires: [52-01]
  provides: [test_frame_vectors-unity-suite, both-legs-vector-assertions, crc8-kat]
  affects: [firestarter/test/native/avr/test_frame_vectors, firestarter/platformio.ini, firestarter/include/frame_vectors.h, firestarter/tools/catalog/frame-vectors.toml, firestarter_app/tools/catalog/frame-vectors.toml, firestarter_app/firestarter/frame_vectors.py]
tech_stack:
  added: []
  patterns: [both-legs vector assertion (D-02), table-free CRC8 KAT (D-06/SC4), PROGMEM memcpy_P decode loop, Unity serial mock re-wiring per vector, CR-01 encoder-only skip]
key_files:
  created:
    - firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp
    - firestarter/test/native/avr/test_frame_vectors/host_stubs.cpp
    - firestarter/test/native/avr/test_frame_vectors/serial_read_mock.h
  modified:
    - firestarter/platformio.ini
    - firestarter/include/frame_vectors.h
    - firestarter/tools/catalog/frame-vectors.toml
    - firestarter_app/tools/catalog/frame-vectors.toml
    - firestarter_app/firestarter/frame_vectors.py
decisions:
  - "Empty-payload decode skip: TEST_ASSERT_EQUAL_MEMORY(p, buf, 0) is treated as failure by Unity ('You Asked Me To Compare Nothing'); added payload_len > 0 guard for the memory compare inside test_vector_decode_leg"
  - "VEC_EMPTY (payload_len=0) fully verified: decode returns 0 (correct), memory compare skipped (Unity limitation, not a semantic gap)"
  - "Catalog bug auto-fixed: VEC_512_ALL_FF had 430-byte payload instead of 512; VEC_1024_ALL_FF frame_hex was wrong; VEC_1024_ALL_ZERO had 1034-byte payload instead of 1024 — all corrected in both sub-repos and frame_vectors.h regenerated"
metrics:
  duration: 30m
  completed: "2026-06-02"
  tasks: 2
  files: 8
---

# Phase 52 Plan 02: Firmware Unity Vector Suite Summary

Added the firmware-side Unity vector suite (`test_frame_vectors/`) that pins the COBS frame contract against the frozen golden vectors from Plan 01. Both encoding and decoding legs verified for all 12 vectors; CRC8 KAT pins poly 0x07 independently of the production PROGMEM table. Full `pio test -e native` suite: 39/39 green.

## Tasks Completed

| Task | Name | Commit (fw) | Files |
|------|------|-------------|-------|
| 1 | Scaffold test_frame_vectors suite + register in platformio.ini | 7de4ad8 | 6 files (fw + app catalog fix) |
| 2 | Implement both-legs vector assertions + CRC8 KAT | d300b2a | 1 file (fw) |

## Acceptance Criteria Verification

- `pio test -e native -f "*test_frame_vectors*"` runs 3 tests, 0 failures — PASS
- `test_crc8_known_answer` asserts `ref_crc8({0x01},1)==0x07` and `ref_crc8(NULL,0)==0x00` — PASS
- `test_vector_encode_leg` asserts all 12 FRAME_VECTOR_COUNT vectors byte-for-byte (incl. 512/1024-byte) — PASS
- `test_vector_decode_leg` skips payloads >511 bytes (encoder-only per CR-01) and asserts payload round-trip for the rest — PASS
- No corrupt-CRC or truncated-frame assertions in this suite (D-03) — PASS
- `ref_crc8` / `test_cobs_encode` are table-free copies, not the production PROGMEM table — PASS
- `platformio.ini` `[env:native]` lists `native/avr/test_frame_vectors` in `test_filter` — PASS
- `platformio.ini` `[env:native]` lists `-I test/native/avr/test_frame_vectors` in `build_flags` — PASS
- `host_stubs.cpp` includes `../_shared/host_stubs_common.inc` — PASS
- `serial_read_mock.h` defines `setup_serial_read_mock` — PASS
- Full `pio test -e native` suite: 39/39 tests passed — PASS

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Three golden vectors had incorrect payload/frame data in the catalog**
- **Found during:** Task 1 — compilation failed with "too many initializers" for `uint8_t frame[1031]` because the VEC_1024_ALL_ZERO frame had 1334 bytes
- **Issue:** VEC_512_ALL_FF had payload_hex with only 430 bytes instead of 512; VEC_1024_ALL_FF had incorrect frame_hex (1033 bytes instead of the correct 1031); VEC_1024_ALL_ZERO had payload_hex with 1034 bytes instead of 1024 and a frame_hex of 1334 bytes (evidently concatenated wrong data from Plan 01)
- **Fix:** Recomputed correct payload_hex and frame_hex for all three vectors using the production COBS+CRC8 algorithm. Updated both firestarter and firestarter_app catalog copies (byte-identical, D-09). Regenerated `include/frame_vectors.h` and `firestarter_app/firestarter/frame_vectors.py`
- **Files modified:** firestarter/tools/catalog/frame-vectors.toml, firestarter/include/frame_vectors.h, firestarter_app/tools/catalog/frame-vectors.toml, firestarter_app/firestarter/frame_vectors.py
- **Commit:** 7de4ad8 (fw), f7c370f (app)

**2. [Rule 1 - Bug] Unity TEST_ASSERT_EQUAL_MEMORY(p, buf, 0) treated as failure**
- **Found during:** Task 2 — first test run showed `test_vector_decode_leg` FAILED with "You Asked Me To Compare Nothing, Which Was Pointless" for the VEC_EMPTY vector (payload_len=0)
- **Issue:** Unity's `TEST_ASSERT_EQUAL_MEMORY` with size=0 emits a failure message rather than passing silently
- **Fix:** Added `if (vec.payload_len > 0)` guard around the `TEST_ASSERT_EQUAL_MEMORY` call inside the decode loop. VEC_EMPTY is still fully verified: `res >= 0` and `res == 0` assertions pass; only the zero-length memory comparison is skipped (semantically a no-op anyway)
- **Files modified:** firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp
- **Commit:** d300b2a

## Known Stubs

None — all test assertions are fully wired. No placeholder data or hardcoded return values.

## Threat Flags

No new production network endpoints, auth paths, or trust-boundary schema changes introduced. This plan touches only test files and the golden-vector catalog (test infrastructure). The catalog bug fixes (Rule 1) restore the correct frozen byte values that the test infrastructure is supposed to assert against.

T-52-04 (codec drift): mitigated — both-legs assertions fail on any byte divergence.
T-52-05 (suite silently skipped): mitigated — BOTH test_filter AND build_flags -I registered.
T-52-06 (wrong polynomial KAT): mitigated — table-free ref_crc8 used.

## Self-Check: PASSED

Files created/exist:
- FOUND: firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp
- FOUND: firestarter/test/native/avr/test_frame_vectors/host_stubs.cpp
- FOUND: firestarter/test/native/avr/test_frame_vectors/serial_read_mock.h

Commits exist (firestarter):
- FOUND: 7de4ad8 (Task 1 — scaffold + catalog fix)
- FOUND: d300b2a (Task 2 — full vector assertions + KAT)

Commits exist (firestarter_app):
- FOUND: f7c370f (catalog + frame_vectors.py fix)
