---
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
plan: 02
subsystem: wire-format
tags: [wire-format, serial, firmware, arduino, tdd, w-04, u16-len]

# Dependency graph
requires:
  - phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
    plan: 01
    provides: MSG_DATA_CHUNK catalog entry (bytes param type, id=0xE6)
provides:
  - u16 big-endian len field in every emitted ID frame (firmware _firestarter_emit_frame)
  - u16 big-endian len decode in host _read_and_parse_lines
  - bytes param type decode in host _decode_param (MSG_DATA_CHUNK path)
  - bytes-type rendering filter in _decode_id_frame (printf-safe)
  - test_decoder.py 14 tests green (12 baseline + 2 new W-04 gap tests)
  - native test_messages suite green with u16 byte-offset assertions
affects:
  - 08-03 (host parser prefix-matching deletion — now on a u16-len wire)
  - 08-04..08-05 (call-site conversions — all emit into the u16 wire)

# Tech tracking
tech-stack:
  added:
    - "bytes param type decode in _decode_param (consumes buf[cursor:] as raw bytes)"
    - "bytes-value filter before printf rendering in _decode_id_frame"
  patterns:
    - "u16 big-endian len: SERIAL_PORT.write(len_u16 >> 8); SERIAL_PORT.write(len_u16 & 0xFF)"
    - "host read: struct.unpack_from('>H', self.connection.read(2))[0]"
    - "bytes param consumes all remaining params_bytes — no length prefix in wire format"

key-files:
  modified:
    - "firestarter/src/boards/rurp_serial_utils.cpp — u16 len emit, guard 253→65533"
    - "firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp — +1 byte-offset shift"
    - "firestarter_app/firestarter/serial_comm.py — read(2) + struct.unpack + bytes decode"
    - "firestarter_app/tests/conftest.py — struct.pack('>H', length) in build_frame"
    - "firestarter_app/tests/test_decoder.py — 2 new tests + WR-03 update"

key-decisions:
  - "Firmware param_count stays uint8_t — guard widened to 65533 for forward-compat; no API change needed for current callers"
  - "bytes param decode: consume all remaining bytes (no wire length prefix); frame u16 len is the delimiter"
  - "bytes values filtered from printf tuple — MSG_DATA_CHUNK format string has no % specifier"
  - "test_wire_format_text_catalog_id_rejected updated: MSG_OK_FW_HANDSHAKE (0x06) now id_frame per Plan 01 P-04 — only 0x03 retains text guard"
  - "test_oversize_param_count_rejected rewritten: 254/255 now emit (valid under u16); 253 shows 0x00FF layout"

requirements-completed: [LMIG-03]

# Metrics
duration: 19min
completed: 2026-05-18
---

# Phase 8 Plan 02: Wire-Format len u8→u16 Widening (W-04) Summary

**Wire-format major bump landed: firmware emits 2-byte big-endian len, host reads 2-byte big-endian len, all 14 decoder tests green, both AVR builds clean.**

## Performance

- **Duration:** ~19 min
- **Started:** 2026-05-18T18:50:27Z (approximately)
- **Completed:** 2026-05-18T19:09:33Z
- **Tasks:** 2 (TDD RED + GREEN)
- **Files modified:** 5 (2 firmware, 3 host)

## Accomplishments

- `_firestarter_emit_frame` now writes `len` as 2 bytes big-endian (MSB then LSB); guard raised from 253 to 65533
- `_read_and_parse_lines` now reads 2 bytes for frame_len and decodes via `struct.unpack_from(">H", ...)`
- `_decode_param` now handles `bytes` param type (consumes all remaining buf[cursor:]); `_decode_id_frame` filters bytes values before printf rendering
- `conftest.build_frame` emits u16 len via `struct.pack(">H", length)` — all existing tests automatically use new format
- `test_rurp_log_id.cpp` assertions shifted +1 for every offset >= 4; size expectations incremented; oversize test rewritten for u16 semantics
- 2 new W-04 gap tests added: `test_data_chunk_body_over_253_bytes_decodes` (512-byte payload) and `test_data_chunk_body_254_bytes_at_old_u8_limit` (254-byte body)
- 14/14 host decoder tests pass; 5/5 native test_messages tests pass; both AVR builds clean

## Build Measurements (Phase 8 Wire-Format Baseline)

| Board    | RAM Used      | Flash Used          |
|----------|---------------|---------------------|
| Uno      | 77.5% (1587/2048 B) | 77.1% (24856/32256 B) |
| Leonardo | 60.6% (1551/2560 B) | 94.3% (27042/28672 B) |

(Phase 7 baseline for reference: Uno Flash 77.0% / 24838 B, Leonardo Flash 94.3% / 27026 B — delta is +18 B Uno, +16 B Leonardo from the extra SERIAL_PORT.write call for the len MSB byte)

## Task Commits

**Firmware (sub-repo: firestarter):**
- Task 1+2 combined: `f242dbb` — `feat(wire): widen frame len field from u8 to u16 big-endian (W-04)`
  - Files: `src/boards/rurp_serial_utils.cpp`, `test/native/avr/test_messages/test_rurp_log_id.cpp`

**Host (sub-repo: firestarter_app):**
- Task 1+2 combined: `b7ee710` — `feat(wire): widen frame len field from u8 to u16 big-endian (W-04)`
  - Files: `firestarter/serial_comm.py`, `tests/conftest.py`, `tests/test_decoder.py`

**Wire-format major bump assertion:** Firmware commit `f242dbb` and host commit `b7ee710` land together; host commit body cross-references firmware SHA.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added `bytes` param type decode to `_decode_param`**
- **Found during:** Task 2 (GREEN verification — `test_data_chunk_body_over_253_bytes_decodes` failed with "Unknown param type: bytes")
- **Issue:** The `_decode_param` function in `serial_comm.py` had no handler for `ptype == "bytes"` (added to catalog in Plan 01), so MSG_DATA_CHUNK frames raised ValueError during param decode and returned None from the decoder.
- **Fix:** Added `bytes` handler that returns `buf[cursor:]` (all remaining params bytes); added filter in `_decode_id_frame` to exclude bytes-type values from the printf-format tuple (format string has no `%` specifier for bytes params).
- **Files modified:** `firestarter_app/firestarter/serial_comm.py`
- **Committed in:** `b7ee710`

**2. [Rule 1 - Bug] Updated `test_wire_format_text_catalog_id_rejected` for MSG_OK_FW_HANDSHAKE catalog change**
- **Found during:** Task 2 (GREEN verification — test asserted `CATALOG[MSG_OK_FW_HANDSHAKE].wire_format == "text"` but Plan 01 already changed it to `id_frame` per P-04)
- **Issue:** The test pinned the old wire_format='text' state for 0x06 (MSG_OK_FW_HANDSHAKE), which was correctly changed to 'id_frame' in Plan 01. The test was stale.
- **Fix:** Updated test to assert the current correct state (`wire_format="id_frame"` for 0x06) and removed the 0x06 rejection assertion; added a docstring explaining the P-04 catalog change. Only 0x03 (MSG_OK_FW_VERSION) retains wire_format='text' per LFW-05.
- **Files modified:** `firestarter_app/tests/test_decoder.py`
- **Committed in:** `b7ee710`

**3. [Rule 1 - Bug / Plan adaptation] test_oversize_param_count_rejected rewritten for u16 semantics**
- **Found during:** Task 1 (RED step — analyzing what the updated test should assert)
- **Issue:** The plan specified testing param_count = 65534 rejection and param_count = 65533 acceptance, but `param_count` is `uint8_t` (max 255). No uint8_t value can exceed the new 65533 guard. The old "254/255 reject" cases now PASS.
- **Fix:** Rewrote the test to verify: 253 params emits with 0x00FF layout (len MSB=0, LSB=255); 254 params emits with 0x0100 layout; 255 params emits with 0x0101 layout. This proves the guard is effectively disabled for all uint8_t values and that the u16 len is emitted correctly at/near the uint8_t boundary.
- **Files modified:** `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp`
- **Committed in:** `f242dbb`

---

**Total deviations:** 3 auto-fixed (1 Rule 2 missing critical, 2 Rule 1 bugs)
**Impact on plan:** All auto-fixes required for test correctness and decoder completeness. No scope creep.

## TDD Gate Compliance

- RED gate: Task 1 changed test files without changing firmware/host impl → 11 of 14 tests failed as expected
- GREEN gate: Task 2 changed `_firestarter_emit_frame` (firmware) + `_read_and_parse_lines` (host) → all 14 tests pass
- Both commits share the same `feat(wire):` subject prefix per plan's W-04 anti-pattern avoidance

## Next Phase Readiness

- Plan 03 (host parser prefix-matching deletion for OK/INIT/MAIN/END) can begin: wire is fully u16-len
- Plan 04-05 (call-site conversions) can begin: all emitted frames go through u16 len emit path
- The Wave-0 VALIDATION gap (MSG_DATA_CHUNK body > 253 bytes) is exercised and green

## Self-Check: PASSED

### Files verified:
- [x] firestarter/src/boards/rurp_serial_utils.cpp — `len_u16`, `65533` guard present
- [x] firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp — `captured[6]` present
- [x] firestarter_app/firestarter/serial_comm.py — `struct.unpack_from(">H"` present, `bytes` type handler present
- [x] firestarter_app/tests/conftest.py — `struct.pack`, `import struct` present
- [x] firestarter_app/tests/test_decoder.py — `test_data_chunk_body_over_253_bytes_decodes` present

### Commits verified:
- [x] f242dbb — feat(wire) in firestarter sub-repo
- [x] b7ee710 — feat(wire) in firestarter_app sub-repo
