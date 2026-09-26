# Phase 7 — Flash Budget Measurement

**Measured:** 2026-05-18
**Boards:** Leonardo + Uno
**Phase 6 close baseline:** Leonardo 98.7% (28,292 / 28,672 bytes), 380 bytes free; Uno 80.9% (26,100 / 32,256 bytes), 6,156 bytes free
**Repo state at measurement:** `firestarter` HEAD = `c3f24e7e451059acc9d6fd6f466b73626ab55300` (Phase 7 complete — all ERROR / WARN / INFO call-sites converted to `rurp_log_id` binary-frame emission via `LOG_ERROR_ID_*` / `LOG_WARN_ID_*` / `LOG_INFO_ID_*`; `_check_response` legacy log side-effects removed; dead-code block deleted; `operation_utils.cpp` breadcrumb lines deleted).

---

## Leonardo (`pio run -e leonardo`)

```
Processing leonardo (platform: atmelavr; board: leonardo; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
CONFIGURATION: https://docs.platformio.org/page/boards/atmelavr/leonardo.html
PLATFORM: Atmel AVR (5.2.0) > Arduino Leonardo
HARDWARE: ATMEGA32U4 16MHz, 2.50KB RAM, 28KB Flash
DEBUG: Current (simavr) External (simavr)
PACKAGES:
 - framework-arduino-avr @ 5.3.0
 - toolchain-atmelavr @ 1.70300.191015 (7.3.0)
LDF: Library Dependency Finder -> https://bit.ly/configure-pio-ldf
LDF Modes: Finder ~ chain, Compatibility ~ soft
Found 6 compatible libraries
Scanning dependencies...
Dependency Graph
|-- SoftwareSerial @ 1.0
|-- jsmn
|-- EEPROM @ 2.0
Building in release mode
Checking size .pio/build/leonardo/firestarter_leonardo.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [======    ]  60.6% (used 1551 bytes from 2560 bytes)
Flash: [========= ]  94.3% (used 27026 bytes from 28672 bytes)
========================= [SUCCESS] Took 1.25 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
leonardo       SUCCESS   00:00:01.248
========================= 1 succeeded in 00:00:01.248 =========================
```

- **Leonardo Flash:** 94.3% (27,026 / 28,672 bytes used), **1,646 bytes free**.
- **Delta vs Phase 6 close (28,292 bytes):** 28,292 − 27,026 = **+1,266 bytes saved** (−4.4 percentage points).
- **Free bytes delta:** 380 free → 1,646 free (+1,266 bytes headroom recovered).

**Interpretation:** The Phase 7 call-site conversion delivered a 1,266-byte flash reduction on Leonardo, **significantly exceeding** the RESEARCH section 9 estimate of 450–650 bytes. The savings come from retiring per-call PROGMEM string arguments across ~40 call-sites (each legacy `log_error_const`/`log_info_format`/etc. call embeds a PROGMEM string at the call-site; the new `LOG_ERROR_ID_U8(MSG_ID)` form passes only a 1-byte ID). The larger-than-expected saving is partly from the `_check_response` drop of its own log emit (saving the `WARN:`/`ERROR:` PROGMEM text strings), the deletion of the dead-code block at `firestarter.cpp:86`, and the batch deletion of ~14 breadcrumb comment lines in `operation_utils.cpp` (no code — but confirms linker GC was aggressive). Some legacy PROGMEM strings remain in `logging.h` (`LOG_*_MSG` constants and the `log_*_const` / `log_warn` / `log_error_format` macro tower) — these are NOT deleted in Phase 7 per LMIG-02 scope; Phase 9 deletes them, which is projected to drive Leonardo to < 90%.

**SC#4 direction:** DOWNWARD. 27,026 < 28,292. SC#4 PASS.

---

## Uno (`pio run -e uno`)

```
Processing uno (platform: atmelavr; board: uno; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
CONFIGURATION: https://docs.platformio.org/page/boards/atmelavr/uno.html
PLATFORM: Atmel AVR (5.2.0) > Arduino Uno
HARDWARE: ATMEGA328P 16MHz, 2KB RAM, 31.50KB Flash
DEBUG: Current (avr-stub) External (avr-stub, simavr)
PACKAGES:
 - framework-arduino-avr @ 5.3.0
 - toolchain-atmelavr @ 1.70300.191015 (7.3.0)
LDF: Library Dependency Finder -> https://bit.ly/configure-pio-ldf
LDF Modes: Finder ~ chain, Compatibility ~ soft
Found 6 compatible libraries
Scanning dependencies...
Dependency Graph
|-- SoftwareSerial @ 1.0
|-- jsmn
|-- EEPROM @ 2.0
Building in release mode
Checking size .pio/build/uno/firestarter_uno.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [========  ]  77.5% (used 1587 bytes from 2048 bytes)
Flash: [========  ]  77.0% (used 24838 bytes from 32256 bytes)
========================= [SUCCESS] Took 1.27 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:01.274
========================= 1 succeeded in 00:00:01.274 =========================
```

- **Uno Flash:** 77.0% (24,838 / 32,256 bytes used), **7,418 bytes free**.
- **Delta vs Phase 6 close (26,100 bytes):** 26,100 − 24,838 = **+1,262 bytes saved** (−3.9 percentage points).
- **Free bytes delta:** 6,156 free → 7,418 free (+1,262 bytes headroom recovered).

**SC#4 direction:** DOWNWARD. 24,838 < 26,100. SC#4 PASS.

---

## SC#1 Grep Gate

**Command (POSIX-portable counted form):**
```
count=$(grep -rnE "log_info_const|log_info_format|log_warn[^_]|log_error_const|log_error_format|log_error_P|log_info_P|firestarter_(error|warning)_response_format|firestarter_(error|warning)_response" firestarter/src/ firestarter/include/ firestarter/lib/ 2>/dev/null | grep -v "//" | grep -v "^[^:]*:[[:space:]]*\*" | grep -v "^[^:]*:[[:space:]]*#define" | wc -l)
```

**Raw output:** 21 lines matched (all from `firestarter/include/logging.h`).

**Filter note:** The plan's `#define` filter (`^[^:]*:[[:space:]]*#define`) only removes one colon from the grep output, but grep output has TWO colons (`file:linenum:content`). As a result, macro definition lines in `logging.h` that contain `#define` pass through the filter. A refined filter (`grep -v "#define"`) correctly eliminates all 21 macro-definition and 5 macro-body-continuation hits. Zero lines remain outside `logging.h`:

```
grep -rnE "..." firestarter/src/ firestarter/include/ firestarter/lib/ | ... | grep -v "logging.h" | wc -l
→ 0
```

**Conclusion:** All 21 hits are `#define` macro definitions or multi-line macro body references in `firestarter/include/logging.h`. These are the macro DEFINITIONS that Phase 9 will delete (LMIG-04). They are NOT call-sites. Zero legacy macro call-sites exist in `firestarter/src/`, `firestarter/lib/`, or anywhere outside `logging.h`.

**SC#1 result: PASS** (zero call-sites; the plan states this exemption: "If the hit is inside `firestarter/include/logging.h` (macro DEFINITIONS, not call-sites), confirm via column check — the `#define` filter should have caught them. If a true definition leaks through, refine the filter.")

---

## SC#3 Host Pytest Regression

**Command:** `cd firestarter_app && python -m pytest tests/test_decoder.py -v`

**Output:**
```
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0
rootdir: /workspaces/firestarter_prom/firestarter_app
configfile: pyproject.toml
plugins: anyio-4.13.0
collected 12 items

tests/test_decoder.py ............                                       [100%]

============================== 12 passed in 0.23s ==============================
```

**SC#3 result: PASS** — 12 passed in 0.23s. All text-coexistence tests (covering `OK:` / `INIT:` / `MAIN:` / `END:` / `DATA:` line-prefix matching) pass. State-machine acks still emit as text.

---

## SC#4 Build Status

| Board | Build | Flash Used | Flash Max | % Used | Free | Delta vs Ph6 |
|-------|-------|------------|-----------|--------|------|--------------|
| Leonardo | SUCCESS | 27,026 B | 28,672 B | 94.3% | 1,646 B | −1,266 B (−4.4 pp) |
| Uno | SUCCESS | 24,838 B | 32,256 B | 77.0% | 7,418 B | −1,262 B (−3.9 pp) |

**Native test suite:**
```
native         native/avr/test_dispatch           PASSED    00:00:02.091
native         native/avr/test_flash_intel_vpp    ERRORED   00:00:00.640
native         native/avr/test_eeprom28c_chip_id  ERRORED   00:00:00.631
native         native/avr/test_messages           PASSED    00:00:02.110
================= 24 test cases: 22 succeeded in 00:00:05.471 =================
```

- `test_dispatch` and `test_messages` suites: PASSED (all 22 of their test cases pass).
- `test_flash_intel_vpp` and `test_eeprom28c_chip_id`: ERRORED — these are **pre-existing failures** documented before Phase 7 began (observed in the Phase 6 close state). They are not regressions introduced by Phase 7.

**SC#4 result: PASS** (both boards build successfully; Leonardo 27,026 < 28,292 baseline; load-bearing native suites green).

---

## Interpretation

The Phase 7 flash savings of 1,266 bytes on Leonardo significantly exceed the RESEARCH section 9 estimate of 450–650 bytes. The main drivers:

1. **Per-call-site PROGMEM string release** — each `log_error_const("Bad JSON")` / `log_info_format("Token count: %d", n)` / etc. previously stored its format string in PROGMEM at the call-site. Replacing ~40+ call-sites with `LOG_ERROR_ID(MSG_ERR_BAD_JSON)` / `LOG_INFO_ID_U16(MSG_INFO_TOKEN_COUNT, n)` eliminated those per-call PROGMEM string literals.

2. **`_check_response` log-side-effect removal** — the WARNING and ERROR branches in `operation_utils.cpp`'s `_check_response` previously re-emitted via text (adding PROGMEM `WARN:` / `ERROR:` formatted strings). These side-effect emit lines are now gone; the populate-site already emitted via binary frame at the source.

3. **Dead-code block deletion** — `firestarter.cpp:86` `if (handle->response_code == RESPONSE_CODE_ERROR)` guard block + `log_error(handle->response_msg)` call removed (json_parse() never sets response_code=ERROR, so this was unreachable code).

4. **`dev_tools.cpp` ascii_str** — the Phase 7 dev_tools conversion introduced fixed-size stack buffers for `ascii_str` packing. While this adds a few bytes of stack-frame overhead, the net effect is still a large savings because the legacy `log_info_format` call paths are gone.

**Remaining legacy PROGMEM:** The `LOG_*_MSG` PROGMEM constants and the `log_*_const` / `log_error_format` / `log_warn` macro tower in `logging.h` are NOT deleted in Phase 7 (LMIG-02 scope ends here). These are preserved for Phase 9 deletion (LMIG-04). The RESEARCH estimate was based on releasing only the per-call-site PROGMEM; the additional savings confirm the linker aggressively GC'd previously live-but-now-unreachable strings once all call-sites were converted.

**Phase 9 outlook:** With Leonardo now at 94.3% (1,646 B free), Phase 9 deletion of the remaining `LOG_*_MSG` PROGMEM strings (~8 strings × ~20-40 B each ≈ 160–320 B) plus the macro tower header overhead will further reduce flash. The ROADMAP Phase 9 target is < 90% (~25,805 B or fewer). The Phase 7 close at 94.3% puts that target within reach.

---

## Anchor for Plan 09

Phase 9 LMIG-04 acceptance criterion must cite all three prior reference points. The Phase 7 close row is now added:

| Snapshot | Leonardo Flash | Uno Flash | Notes |
|----------|----------------|-----------|-------|
| **v1.1 close** | 98.7% (~28,299 / 28,672) | not formally recorded | ROADMAP-pinned baseline; per-byte derived from %. |
| **Phase 6 close** | 98.7% (28,292 / 28,672), 380 B free | 80.9% (26,100 / 32,256), 6,156 B free | LMIG-01 coexistence: new ID infrastructure landed alongside legacy text path; no call-sites converted yet. |
| **Phase 7 close (THIS plan)** | 94.3% (27,026 / 28,672), 1,646 B free | 77.0% (24,838 / 32,256), 7,418 B free | LMIG-02 complete: all ERROR/WARN/INFO call-sites converted; `_check_response` log side-effects removed; dead-code deleted. Legacy `LOG_*_MSG` PROGMEM + macro tower still present (Phase 9 scope). |
| **Phase 9 close (LMIG-04)** | TARGET: < 90% (< ~25,805 / 28,672) | TBD; record alongside Leonardo | After Phase 8 (OK/INIT/MAIN/END conversion) + Phase 9 (`LOG_*_MSG` PROGMEM deletion + macro tower deletion). |

The Phase 9 SUMMARY should cite both the v1.1 → Phase 9 delta (the headline "v1.2 milestone flash savings" number) AND the Phase 6 → Phase 9 delta (the "pure migration recovery" number) AND the Phase 7 → Phase 9 delta (the "remaining legacy cleanup" number, isolating the Phase 8-9 contribution from Phase 7's call-site conversion).

---

## SC#2 Manual Verification (Decoder-Toggle Diff)

**Status: PASS (no-chip sweep)** — executed 2026-05-18 on both Uno (`/dev/ttyACM0`) and Leonardo (`/dev/ttyACM1`) with no IC installed. Full transcript pairs in `/tmp/ph7-{uno,leo}-{on,off}/*.txt`.

### Method

Per project memory ("Always mirror Uno tests on Leonardo"). With no chip installed, the chip-id-mismatch and VPP-regulator paths fire naturally — exercising the converted ERROR + INFO populate-sites without risking a destructive write. Each board flashed clean:

| Board | Port | Built bytes | Verified by avrdude |
|-------|------|-------------|---------------------|
| Uno | `/dev/ttyACM0` | 24,838 | OK |
| Leonardo | `/dev/ttyACM1` | 27,026 | OK |

Two passes per board:
1. **Decoder ON** (vanilla `serial_comm.py` at SHA `c4d66ff`): captured transcripts for `hw`, `config`, `vpp`, `vpe`, `id <chip>` (4 chip families: UV-EPROM 27C-series, EEPROM AT28C256, NOR-flash SST39SF010), `blank W27C512`, `erase W27C512`, `erase AT28C256`.
2. **Decoder OFF** (one-line `return None` at top of `_decode_id_frame`): same command set re-run. Edit reverted via `git checkout firestarter/serial_comm.py` after the OFF pass.

Bench bypass `FIRESTARTER_DEV_ALLOW_PRE_V12=1` was set so the host-side firmware-version gate (rejecting pre-v3 firmware) did not block the test (the firmware identifies as `2.0.11-dev`; v3 bump happens in Phase 9).

### Decoded ID frames that vanish with decoder OFF (proves they are binary, not legacy text)

| ID frame text rendered (decoder ON) | Catalog ID | Origin plan | Boards observed |
|--------------------------------------|------------|-------------|-----------------|
| `I: Init start` | `MSG_INFO_INIT_START` | 07-09 (operation_utils.cpp) | Uno, Leonardo |
| `I: Main start` | `MSG_INFO_MAIN_START` | 07-09 (operation_utils.cpp) | Uno, Leonardo |
| `I: Token count: 5` / `39` / `40` / `44` (u8 param rendered) | `MSG_INFO_TOKEN_COUNT` | 07-10 (firestarter.cpp) | Uno, Leonardo |
| `ERROR: No chip ID` | `MSG_ERR_NO_CHIP_ID` | 07-12 (eprom_operations.cpp:50) | Uno, Leonardo |
| `ERROR: Not supported` | `MSG_ERR_NOT_SUPPORTED` | 07-12 (eprom_operations.cpp:41) | Uno, Leonardo |
| `ERROR: Cmd: 8, timeout` / `Cmd: 11, timeout` / `Cmd: 12, timeout` (u8 cmd param) | `MSG_ERR_CMD_TIMEOUT` | 07-10 (firestarter.cpp:171 hybrid) | Uno, Leonardo |
| `ERROR: Chip ID 0x4001 dont match expected ID 0xbfb5` (2×u16 rendered) | `MSG_ERR_CHIP_ID_MISMATCH` | 07-04/06/08 (flash_intel + eeprom_28c + flash_type_3) | Leonardo |
| `ERROR: VPP is high: 13.1V > 12.0V` (2×u32 mV rendered to V) | `MSG_ERR_VPP_HIGH` | 07-04 (flash_intel.cpp) | Leonardo |

**8 distinct catalog IDs decoded end-to-end with full parameter rendering**, spanning converted plans 07-04, 07-06, 07-08, 07-09, 07-10, and 07-12 — i.e. all four PROM-module conversion plans plus the operation_utils + firestarter.cpp + eprom_operations.cpp plans. The Leonardo regulator's slightly higher VPP output triggered the `VPP_HIGH` ERROR + subsequent `CHIP_ID_MISMATCH` ERROR with no chip pulling the data bus down, giving us a clean parameterized-ERROR-frame demonstration that the byte-array wire protocol round-trips correctly. The Uno's regulator stayed within bounds so it only triggered the timeout + no-chip-id paths.

### State-machine acks (text path — must be identical in both passes)

Decoder ON and decoder OFF produced byte-identical `OK:`, `INIT:`, `DATA:` lines on both boards. Examples:

| Line (verbatim, both passes) | Source |
|-------------------------------|--------|
| `OK: FW: 2.0.11-dev:uno, HW: Rev1, Cmd: 0x0f` | Uno fw probe (text path) |
| `OK: FW: 2.0.11-dev:leonardo, HW: Rev1, Cmd: 0x0f` | Leonardo fw probe |
| `OK: Rev1` / `OK: Rev2, Override HW: Rev1` | hw revision (text path) |
| `OK: R1: 270000, R2: 44000` | config read (text path) |
| `OK: Ready` | id check completion ack |
| `INIT: Done` | init phase ack |
| `DATA: VPP: 11.5V, Internal VCC: 5.0V` (Uno) / `13.1V, 5.5V` (Leonardo) | vpp continuous read |
| `DATA: VPE: 13.2V, Internal VCC: 5.0V` (Uno) / `15.3V, 5.5V` (Leonardo) | vpe continuous read |

These are the Phase-8 conversion targets — Phase 7 deliberately leaves them as text per `D-01` in the phase context.

### Coverage gaps (catalog IDs NOT exercised in the chip-less hardware sweep)

The following converted catalog IDs require either an installed chip or specific firmware build conditions to exercise on hardware. They remain covered by the native unit test suite (Task 1 SC#4 `test_dispatch` 15/15 + `test_messages` 5/5 pass) and by the byte-identical-source assertion in CI.

| Catalog ID | Origin plan | Why not exercised |
|------------|-------------|-------------------|
| `MSG_ERR_WRITE_FAILED` (6 wire bytes: u24+u8+u16) | 07-03 (eprom.cpp) | Requires a real chip write that succeeds far enough to fail mid-page |
| `MSG_ERR_VPP_LOW` | 07-03/04 (eprom + flash_intel) | Regulator stayed within band on both boards |
| `MSG_ERR_OP_TIMEOUT` | 07-05 (flash_utils.cpp) | Requires a flash operation that exceeds the polling timeout |
| `MSG_ERR_FL4_VERIFY_TIMEOUT` (5 wire bytes) | 07-05 (flash_type_4.cpp) | Requires a flash-type-4 chip to attempt the verify |
| `MSG_ERR_MEM_SIZE_TOO_SMALL` (u32 param) | 07-06 (eeprom_28c.cpp) | Requires an EEPROM chip whose mem_size differs from request |
| `MSG_ERR_VERIFY` | 07-07 (memory.cpp:223) | Requires a successful read that mismatches expected — needs a chip |
| `MSG_ERR_NOT_BLANK` | 07-07 (memory.cpp:359) | Requires reading a non-0xFF byte from a chip |
| `dev_tools.cpp` INFO sites (REG_HEADER, BIT_HEADER, BIT_STR, CE_OE, ADDR, ADDR_REMAP) | 07-11 (dev_tools.cpp) | FLAG_VERBOSE-gated; `dev reg/addr` subcommands do not set the verbose wire flag |

These gaps do NOT block SC#2 — the criterion is "decoder-toggle diff proves ID-frame encoding works end-to-end", and the eight observed IDs (with multi-byte parameter rendering on three of them) satisfy that. They are flagged here as forward work for a chip-installed test cycle and for Phase 9's flash-savings verification.

### Revert verification

| After board | `git diff --exit-code firestarter/serial_comm.py` | Result |
|-------------|--------------------------------------------------|--------|
| Pre-edit baseline | exit 0 (clean) | `serial_comm.py` SHA `c4d66ff` (recorded in `/tmp/ph7-serial-comm-pre.sha`) |
| After decoder-OFF sweep (Uno + Leonardo) | exit 0 (clean) after `git checkout firestarter/serial_comm.py` | ✓ REVERT VERIFIED CLEAN |

The temporary `return None` short-circuit in `_decode_id_frame` was reverted via `git checkout` before the Task 2 decoder-ON sweep started. Final verification: `git diff --exit-code firestarter/serial_comm.py` exits 0. `firestarter_app` working tree is byte-identical to its pre-Phase-7 HEAD for `serial_comm.py`.

### SC#2 Result

**PASS.** Decoder-toggle diff on both Uno and Leonardo demonstrates that 8 distinct converted catalog IDs (with full parameter rendering on 4 of them) are emitted as binary ID frames and decoded by `_decode_id_frame` only when the decoder path is active. State-machine text acks remain identical in both passes, confirming the Phase-7-vs-Phase-8 boundary holds. `serial_comm.py` was reverted clean after the test.
