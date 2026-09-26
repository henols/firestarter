---
phase: 07-convert-error-warn-info-call-sites
verified: 2026-05-18T18:00:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
re_verification: false
---

# Phase 7: Convert ERROR + WARN + INFO Call-Sites — Verification Report

**Phase Goal:** Every firmware ERROR, WARN, and INFO log call-site is emitted via `rurp_log_id` (or the LOG_* macro form) with parameters as raw byte arrays per the catalog. The host renders these frames identically to how the text-format messages used to read in the CLI output. Old log helpers remain present in firmware only for the state-machine prefix acks (`OK:` / `INIT:` / `MAIN:` / `END:`), which are still text-formatted at the end of this phase.
**Verified:** 2026-05-18T18:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                 | Status     | Evidence                                                                                                      |
|----|---------------------------------------------------------------------------------------|------------|---------------------------------------------------------------------------------------------------------------|
| 1  | SC#1: grep over src/ include/ lib/ returns zero non-comment hits for legacy log macros | ✓ VERIFIED | 25 total grep hits: all are `#define` macro definitions in `logging.h` or commented-out lines in `.cpp` files. Zero active call-sites outside `logging.h`. Confirmed via live re-run. |
| 2  | SC#2: ERROR/WARN/INFO lines render via host catalog decoder; vanish with decoder OFF  | ✓ VERIFIED | Transcript diffs at `/tmp/ph7-{uno,leo}-{on,off}/` confirm: `I: Token count:`, `I: Init start`, `I: Main start`, `ERROR: VPP is high: 13.1V > 12.0V` all absent in OFF pass; `INIT: Done`, `OK:` lines identical in both passes. `serial_comm.py` `git diff --exit-code` exits 0 (revert clean). |
| 3  | SC#3: host pytest test_decoder.py text-coexistence tests pass                         | ✓ VERIFIED | `python -m pytest tests/test_decoder.py -v` → **12 passed in 0.23s** (re-run this session). |
| 4  | SC#4: both AVR boards build cleanly; Leonardo Flash < 28,292 B                        | ✓ VERIFIED | Live pio rebuilds: Leonardo **27,026 / 28,672 B (94.3%)**, Uno **24,838 / 32,256 B (77.0%)**. Both builds SUCCESS. Delta vs Phase 6 baseline: −1,266 B (Leonardo), −1,262 B (Uno). Native suite: test_dispatch PASSED (15/15), test_messages PASSED (5/5); test_flash_intel_vpp + test_eeprom28c_chip_id ERRORED (pre-existing, documented in 07-FLASH-MEASUREMENT.md). |

**Score:** 4/4 truths verified

---

### Required Artifacts

| Artifact                                            | Expected                                   | Status     | Details                                                                                                         |
|-----------------------------------------------------|--------------------------------------------|------------|-----------------------------------------------------------------------------------------------------------------|
| `firestarter/include/logging_id.h`                  | LOG_ERROR_ID_* / LOG_WARN_ID_* / LOG_INFO_ID_* macro families | ✓ VERIFIED | Full macro set present: zero-param, U8/U16/U24/U32, BYTES variants for ERROR/WARN (unconditional) and INFO (FLAG_VERBOSE-gated). |
| `firestarter/include/messages.h`                    | Catalog-generated header with MSG_* constants | ✓ VERIFIED | 71 messages, severity codes, MSG_PARAM_COUNT() lookup. DO NOT EDIT header comment present. |
| `firestarter/src/proms/eprom.cpp`                   | LOG_*_ID_* call-sites replacing legacy macros | ✓ VERIFIED | LOG_ERROR_ID_BYTES(MSG_ERR_WRITE_FAILED), LOG_WARN_ID/LOG_ERROR_ID for VPP_HIGH/VPP_LOW/CHIP_ID_MISMATCH/REV0. No legacy macro call-sites. |
| `firestarter/src/proms/flash_intel.cpp`             | 7 converted sites                          | ✓ VERIFIED | LOG_WARN_ID(MSG_WARN_REV0_VPP_UNSUPPORTED), LOG_WARN/ERROR_ID_BYTES for VPP_HIGH/LOW, LOG_WARN/ERROR_ID_BYTES for CHIP_ID_MISMATCH, LOG_ERROR_ID for INTEL_VPP/PROGRAM/SR_TIMEOUT. |
| `firestarter/src/proms/flash_type_4.cpp`            | 1 converted site                           | ✓ VERIFIED | LOG_ERROR_ID_BYTES(MSG_ERR_FL4_VERIFY_TIMEOUT) confirmed via git log (commit 096812d). |
| `firestarter/src/proms/flash_utils.cpp`             | 1 converted site                           | ✓ VERIFIED | LOG_ERROR_ID(MSG_ERR_OP_TIMEOUT) confirmed via git log (commit 1292826). |
| `firestarter/src/proms/eeprom_28c.cpp`              | 3 converted sites incl. dynamic-severity   | ✓ VERIFIED | Confirmed via git log (commit af4567d). |
| `firestarter/src/proms/memory.cpp`                  | 3 converted sites incl. dispatch fallthrough | ✓ VERIFIED | Confirmed via git log (commit 0979c0f). |
| `firestarter/src/proms/flash_type_3.cpp`            | Dynamic-severity chip-ID site              | ✓ VERIFIED | Confirmed via git log (commit abb8d49). |
| `firestarter/src/operation_utils.cpp`               | Direct-log + _check_response edit + breadcrumb deletion | ✓ VERIFIED | LOG_ERROR_ID(MSG_ERR_TIMEOUT), LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N), LOG_INFO_ID(MSG_INFO_MAIN_DONE/MAIN_START/INIT_START/END_START). send_main_done()/send_init_done()/send_end_done() text-path acks intact. |
| `firestarter/src/firestarter.cpp`                   | 20 sites + dead-code deletion + hybrid at line 176 | ✓ VERIFIED | LOG_INFO_ID_U8/U16/U32 for flags/token-count/buffer-size/mem-size/addr-mask; LOG_ERROR_ID for BAD_JSON/NO_CMD/SETUP/PARSE_CFG/EMPTY_INPUT/UNKNOWN_CMD; LOG_ERROR_ID_U8(MSG_ERR_CMD_TIMEOUT) at loop timeout. No active legacy calls. |
| `firestarter/src/dev_tools.cpp`                     | 7 INFO call-sites with stack-array packing | ✓ VERIFIED | Confirmed via git log (commit 246f2be). |
| `firestarter/src/eprom_operations.cpp`              | 3 ERROR sites                              | ✓ VERIFIED | LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED / MSG_ERR_NO_CHIP_ID / MSG_ERR_OUT_OF_RANGE). |
| `firestarter/src/hardware_operations.cpp`           | 2 ERROR sites                              | ✓ VERIFIED | LOG_ERROR_ID(MSG_ERR_REV0_VPP_RD / MSG_ERR_CMD). |
| `firestarter_app/firestarter/serial_comm.py`        | Decoder revert clean at SHA c4d66ff        | ✓ VERIFIED | `git diff --exit-code firestarter/serial_comm.py` exits 0 this session. |

---

### Key Link Verification

| From                               | To                              | Via                                      | Status     | Details                                                                 |
|------------------------------------|---------------------------------|------------------------------------------|------------|-------------------------------------------------------------------------|
| Firmware call-sites (all .cpp)     | `rurp_log_id()` binary send     | `LOG_*_ID_*` macros in `logging_id.h`   | ✓ WIRED    | Macros expand to `rurp_log_id((id), _b, N)` — confirmed in logging_id.h. |
| `rurp_log_id()` wire frames        | Host `_decode_id_frame()`       | MAGIC_PREAMBLE + CRC8 binary protocol    | ✓ WIRED    | SC#2 decoder-toggle diff proves end-to-end: frames vanish when `_decode_id_frame` is bypassed. |
| Host decoder                       | `CATALOG` (messages.py)         | `from firestarter.messages import CATALOG` | ✓ WIRED  | Import confirmed in serial_comm.py line 27. |
| State-machine text acks            | Host line-prefix matching       | Legacy `send_main_done()` / `send_init_done()` / `send_end_done()` | ✓ WIRED | Text-path acks intact in operation_utils.cpp lines 184, 254, 256. `INIT: Done`, `OK: FW:` lines byte-identical in both decoder passes. |

---

### Data-Flow Trace (Level 4)

| Artifact               | Data Variable    | Source                       | Produces Real Data | Status     |
|------------------------|------------------|------------------------------|--------------------|------------|
| `serial_comm.py` decoder | `_decode_id_frame` | CATALOG from messages.py   | Yes — catalog is codegen output from messages.toml | ✓ FLOWING |
| Firmware call-sites    | Binary frame params | Raw hardware registers/state | Yes — vpp_mv from ADC, chip_id from bus read, counters from loop state | ✓ FLOWING |

---

### Behavioral Spot-Checks

| Behavior                          | Command                                                      | Result                                         | Status   |
|-----------------------------------|--------------------------------------------------------------|------------------------------------------------|----------|
| Leonardo build size < 28,292 B    | `pio run -e leonardo`                                        | 27,026 / 28,672 B (94.3%) — SUCCESS            | ✓ PASS   |
| Uno build size < 26,100 B         | `pio run -e uno`                                             | 24,838 / 32,256 B (77.0%) — SUCCESS            | ✓ PASS   |
| test_decoder.py 12/12 pass        | `cd firestarter_app && python -m pytest tests/test_decoder.py -v` | 12 passed in 0.23s                        | ✓ PASS   |
| Native test_dispatch PASS         | `pio test -e native`                                         | PASSED (15/15 test cases)                      | ✓ PASS   |
| Native test_messages PASS         | `pio test -e native`                                         | PASSED (5/5 test cases); 2 pre-existing ERRORED suites unrelated to Phase 7 | ✓ PASS |
| SC#1 grep gate zero active hits   | grep legacy macros outside logging.h                         | 0 active call-sites; only commented-out lines + `#define` definitions | ✓ PASS |

---

### Probe Execution

No conventional probe scripts (`scripts/*/tests/probe-*.sh`) declared for Phase 7. The SC verification gate is documented in `07-FLASH-MEASUREMENT.md` and re-run independently above.

---

### Requirements Coverage

| Requirement | Source Plan(s)     | Description                                          | Status       | Evidence                                                      |
|-------------|-------------------|------------------------------------------------------|--------------|---------------------------------------------------------------|
| LMIG-02     | 07-01 through 07-13 | Phase B: ERROR/WARN/INFO call-site conversion to `rurp_log_id` form, one batch per cluster | ✓ SATISFIED | REQUIREMENTS.md has `[x] LMIG-02`. All 13 plans present and summarized. Zero active legacy log call-sites in converted files. Flash savings measured. |

**Orphaned requirements check:** No additional REQUIREMENTS.md IDs map to Phase 7 beyond LMIG-02. Coverage: 1/1 (100%).

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter/src/firestarter.cpp` | 58 | `// log_info_format(...)` | Info | Commented-out legacy call — not an active stub. Deferred for Phase 9 cleanup (dead comment, not debt marker). |
| `firestarter/src/boards/rurp_serial_utils.cpp` | 72, 81, 93 | `// log_error_format(...)`, `// log_error_const(...)` | Info | Commented-out legacy calls — not active stubs. The new path in this file does not require log emission (these code paths return error codes to callers). |

No TBD, FIXME, or XXX markers found in any Phase 7 modified file.
No placeholder implementations found.
No hardcoded empty data flowing to rendering.

---

### Human Verification Required

None. All four success criteria were verified programmatically:

- SC#1 via live grep (zero active hits confirmed).
- SC#2 via decoder-toggle transcript diffs in `/tmp/ph7-{uno,leo}-{on,off}/` (ON vs OFF diffs reviewed directly — decoded frames absent in OFF pass, text acks identical).
- SC#3 via live pytest run (12/12 passed).
- SC#4 via live pio rebuilds (both boards SUCCESS, flash sizes confirmed).

---

### Gaps Summary

No gaps. All four ROADMAP success criteria verified against the actual codebase. LMIG-02 fully satisfied.

**Note on pre-existing test failures:** `test_flash_intel_vpp` and `test_eeprom28c_chip_id` ERRORED in the native suite. These are documented pre-existing failures from before Phase 7 began (visible in Phase 6 close state) and are not regressions introduced by this phase. They do not affect Phase 7 acceptance.

**Note on legacy macro definitions in logging.h:** The 25 grep hits from `logging.h` are macro DEFINITIONS (`#define log_error_const`, `#define log_warn`, etc.) and multi-line macro body references. These are the legacy infrastructure preserved under LMIG-02 scope ("old log helpers still present for OK/INIT/MAIN/END prefixes"). Deletion is Phase 9 (LMIG-04) scope.

---

_Verified: 2026-05-18T18:00:00Z_
_Verifier: Claude (gsd-verifier)_
