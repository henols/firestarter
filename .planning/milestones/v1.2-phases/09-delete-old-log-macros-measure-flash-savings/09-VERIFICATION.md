---
phase: 09-delete-old-log-macros-measure-flash-savings
verified: 2026-05-19T00:00:00Z
status: human_needed
score: 5/5 success criteria verified (autonomous side); 2 hardware-pending UAT items awaiting operator-on-bench
overrides_applied: 0
carry_over_assessment:
  assessed: 2026-08-09
  by: v1.31 pre-close carry-over sweep
  status_unchanged: human_needed
  reason_still_open: "Both items are bench-hardware runs. NOT rubber-stamped."
  autonomous_side: COMPLETE (5/5 success criteria, unchanged)
  item_1_chipless_matrix:
    note: |
      The `OK: FW: 3.0.0-dev:<board>` strings this item expects are from the May-2026
      dev-version scheme. The firmware has since shipped b8..b13; a re-run today would
      assert a different version string than the one written here. The item needs
      restating before it can be run, not just running.
  item_2_phase08_carryover:
    status: SCOPE REDUCED — same reduction as Phase 08
    note: |
      This is explicitly the Phase 08 SC#2/SC#3 carry-over. Its blocker (0xA4
      MSG_ERR_EMPTY_INPUT) is RESOLVED — host fix `ack_data=False` on INIT/END at
      firestarter_app/firestarter/eprom_operations.py:488, guarded by
      tests/test_eprom_operations.py:135. The Leonardo leg is superseded by Phase 91's
      W27C512 PASS (chip-ID 0xDA08, erase SHA e16b2a5b). Residual = the Uno leg plus an
      explicit byte-identity diff. See 08-VERIFICATION.md carry_over_assessment.
  recommended_disposition: |
    Resolve jointly with Phase 08 — they are the same underlying bench task. Item 1
    additionally needs its expected version string updated before it is runnable.
    OPERATOR DECISION — not taken here.
re_verification:
  previous_status: none
  previous_score: n/a
  gaps_closed: []
  gaps_remaining: []
  regressions: []
human_verification:
  - test: "Task 2 of Plan 09-05 — Chipless bench wire-protocol matrix re-run on Uno + Leonardo at 3.0.0-dev (no FIRESTARTER_DEV_ALLOW_PRE_V12 prefix)"
    expected: "Uno `fw` output contains `OK: FW: 3.0.0-dev:uno`; Leonardo `fw` output contains `OK: FW: 3.0.0-dev:leonardo`; no FirmwareOutdatedError; all other frames byte-identical to Phase 8 baseline severity-band shape."
    why_human: "Requires physical Uno + Leonardo boards connected to operator's bench; cannot execute programmatically from this environment. SC#3 autonomous half (pytest fwguard 4/4) PASS; this is the additional bench-side native-pass confirmation."
    operator_recovery_commands: |
      cd /workspaces/firestarter_prom/firestarter
      pio run -t upload -e uno --upload-port /dev/ttyACM0
      pio run -t upload -e leonardo --upload-port /dev/ttyACM1
      firestarter -p /dev/ttyACM0 fw       # expect: OK: FW: 3.0.0-dev:uno, HW: Rev1, Cmd: 0x0b
      firestarter -p /dev/ttyACM1 fw       # expect: OK: FW: 3.0.0-dev:leonardo, HW: Rev1, Cmd: 0x0b
      firestarter -p /dev/ttyACM0 hw && firestarter -p /dev/ttyACM1 hw
      firestarter -p /dev/ttyACM0 config && firestarter -p /dev/ttyACM1 config
      firestarter -p /dev/ttyACM0 vpp && firestarter -p /dev/ttyACM1 vpp
      firestarter -p /dev/ttyACM0 vpe && firestarter -p /dev/ttyACM1 vpe
      firestarter -p /dev/ttyACM0 id W27C512 && firestarter -p /dev/ttyACM1 id W27C512
  - test: "Task 3 of Plan 09-05 — Phase 8 SC#2 + SC#3 chip-seated W27C512 write + readback carry-over on Uno + Leonardo"
    expected: "Both boards: write completes with success message; INIT/MAIN/END acks decoded from id-frame (no raw text prefix); `OK: FW: 3.0.0-dev:<board>` bootstrap line present; readback `diff <baseline.bin> <readback.bin>` returns zero output (byte-identical). If Leonardo readback diverges, re-seat per project_leonardo-shield-socket-wonky before declaring regression."
    why_human: "Requires physical Uno + Leonardo + W27C512 chip on operator's bench; chip seating + readback comparison cannot run programmatically. This is the Phase 8 SC#2/SC#3 carry-over (per CONTEXT.md Claude's-Discretion bundle), not a Phase 9-introduced gap."
    operator_recovery_commands: |
      # Seat W27C512 in Uno shield socket, then:
      firestarter -p /dev/ttyACM0 write -e W27C512 <test.hex>
      firestarter -p /dev/ttyACM0 read  -e W27C512 -o /tmp/ph9-uno-readback.bin
      diff <baseline.bin> /tmp/ph9-uno-readback.bin
      # Move chip to Leonardo:
      firestarter -p /dev/ttyACM1 write -e W27C512 <test.hex>
      firestarter -p /dev/ttyACM1 read  -e W27C512 -o /tmp/ph9-leonardo-readback.bin
      diff <baseline.bin> /tmp/ph9-leonardo-readback.bin
      # If no chip available: annotate "no chip available — carrying Phase 8 SC#2/SC#3 to Phase 10".
---

# Phase 9: Delete Old Log Macros + Measure Flash Savings — Verification Report

**Phase Goal:** All legacy firmware log infrastructure (`rurp_log`, `rurp_log_P`, `LOG_*_MSG` PROGMEM string literals, and the `log_info_const` / `log_error_format` / `log_warn` macros) is deleted from `firestarter/src/`, `firestarter/include/`, and `firestarter/lib/`. The firmware major version bumps to 3.0.0 so old hosts refuse to talk to new firmware (and vice versa). A formal flash-usage measurement is recorded for both Uno and Leonardo, with the Leonardo number compared to the v1.1 baseline of 98.7%.

**Verified:** 2026-05-19
**Status:** human_needed (autonomous side PASS; 2 hardware-pending UAT items)
**Re-verification:** No — initial verification

---

## Goal Achievement — Success Criteria Summary

| # | Success Criterion | Status | Live Evidence |
|---|-------------------|--------|---------------|
| SC#1 | PROGMEM exemption audit; remaining hits enumerated in `09-MEASUREMENT.md` | **PASS** | Live grep: 21 raw hits, 12 named-symbol declarations (1 MAGIC_PREAMBLE + 1 CRC8_TABLE + 10 json_parser keys/key_parsers[]); 9 comment-only lines; 0 uncategorized log-purposed PROGMEM. Matches `09-MEASUREMENT.md` Table (a). |
| SC#2 | Legacy log macros zero hits | **PASS** | Live grep returns **0 hits** for `send_ack\|rurp_log\b\|rurp_log_P\|_firestarter_log_\|LOG_OK_MSG\|log_info_const\|log_error_format\|log_warn\b\|debug_setup\|log_debug\b` across `firestarter/src + include + lib`. |
| SC#3 | Firmware FW handshake reports `3.0.0-dev`; host pre-Phase-6 guard regression-tested | **PASS (autonomous halves)** + **PASS-WITH-HARDWARE-PENDING (bench native-pass)** | Source: `firestarter/include/version.h:11 #define VERSION "3.0.0-dev"`. Pytest: `tests/test_fwguard.py` 4 passed. Bench native-pass confirmation = Task 2 of Plan 09-05 (operator-on-bench). |
| SC#4 | `pio run -e leonardo` Flash < 90% with measurable headroom vs 98.7% baseline | **PASS** | Cold-cache build: Flash 85.3% (used 24456 / 28672 bytes), 4216 B free. Δ vs v1.1 baseline (98.7%) = **−13.4 pp / −3,843 B**. |
| SC#5 | `pio run -e uno` Flash usage recorded alongside Leonardo | **PASS** | Cold-cache build: Flash 68.9% (used 22226 / 32256 bytes), 10030 B free. |

**Score:** 5 / 5 success criteria verified on the autonomous side. The 2 hardware-pending UAT items (Plan 09-05 Tasks 2 + 3) are explicit operator-on-bench checkpoints per the plan frontmatter (`autonomous=false`) and CONTEXT.md Claude's-Discretion bundle; they do not gate phase closure, they extend it.

---

## Live Verification Command Outputs

### 1. SC#2 LFW-03 grep gate (live)

```bash
$ grep -rn 'send_ack\|rurp_log\b\|rurp_log_P\|_firestarter_log_\|LOG_OK_MSG\|log_info_const\|log_error_format\|log_warn\b\|debug_setup\|log_debug\b' firestarter/src firestarter/include firestarter/lib | grep -v 'Phase 9: deleted' | wc -l
0
```

Result: **0 hits.** PASS.

### 2. SC#3 firmware version source assertion

```bash
$ grep -n '^#define VERSION' firestarter/include/version.h
11:#define VERSION "3.0.0-dev"
```

Result: VERSION = `"3.0.0-dev"`. PASS.

### 3. SC#3 host pre-v1.2 guard regression

```bash
$ cd firestarter_app && pytest tests/test_fwguard.py -v
collected 4 items
tests/test_fwguard.py ....                                          [100%]
============================== 4 passed in 0.03s ===============================
```

Result: 4 passed. PASS.

### 4. SC#4 Leonardo Flash < 90% (cold-cache build)

```bash
$ cd firestarter && pio run -e leonardo -t clean && pio run -e leonardo | grep -E "^(RAM|Flash):"
leonardo       SUCCESS   00:00:00.344
RAM:   [======    ]  57.2% (used 1465 bytes from 2560 bytes)
Flash: [========= ]  85.3% (used 24456 bytes from 28672 bytes)
```

Result: Flash 85.3% < 90.0%, headroom 4216 B. PASS. (Byte-identical to Plan 09-02 SUMMARY + 09-MEASUREMENT.md — cold-cache reproducibility confirmed.)

### 5. SC#5 Uno Flash recorded

```bash
$ cd firestarter && pio run -e uno -t clean && pio run -e uno | grep -E "^(RAM|Flash):"
uno            SUCCESS   00:00:00.357
RAM:   [=======   ]  73.1% (used 1497 bytes from 2048 bytes)
Flash: [=======   ]  68.9% (used 22226 bytes from 32256 bytes)
```

Result: Flash 68.9% (22226 B used, 10030 B free). PASS. (Byte-identical to Plan 09-02 SUMMARY + 09-MEASUREMENT.md.)

### 6. Native test regression (scoped)

```bash
$ cd firestarter && pio test -e native -f '*test_dispatch*' -f '*test_messages*'
=================================== SUMMARY ===================================
Environment    Test                      Status    Duration
-------------  ------------------------  --------  -------------
native         native/avr/test_dispatch  PASSED    00:00:01.1000
native         native/avr/test_messages  PASSED    00:00:01.972
================= 20 test cases: 20 succeeded in 00:00:03.972 =================
```

Result: 20 / 20 succeeded across both scoped suites (15 dispatch + 5 messages). PASS.

### 7. Host decoder regression

```bash
$ cd firestarter_app && pytest tests/test_decoder.py -q
.........................                                                [100%]
25 passed in 0.25s
```

Result: 25 passed. PASS.

### 8. SC#1 PROGMEM exemption audit (live)

```bash
$ grep -rn 'PROGMEM' firestarter/src firestarter/include 2>/dev/null | wc -l
21
```

Live category breakdown (cross-checked against `09-MEASUREMENT.md` §"SC#1 — PROGMEM Exemption Audit" Table (a)):

| Source location | Symbol/site | Category |
|-----------------|-------------|----------|
| `boards/rurp_serial_utils.cpp:105` | `MAGIC_PREAMBLE[4] PROGMEM` | (a1) MAGIC_PREAMBLE (frame infra) |
| `boards/rurp_serial_utils.cpp:108` | `CRC8_TABLE[256] PROGMEM` | (a2) CRC8_TABLE (frame infra) |
| `json_parser.c:66-74` (9 entries) | `key_mem_size` … `key_algorithm` `PROGMEM` | (a3) json_parser keys |
| `json_parser.c:97` | `key_parsers[] PROGMEM` | (a3) key_parsers[] table |
| `hardware_operations.cpp:86`, `rurp_shield.h:128`, `rurp_serial_utils.{h:13,cpp:13,cpp:230}`, `boards/uno_rurp_shield.cpp:75`, `boards/rurp_serial_utils.cpp:148,192`, `logging_id.h:255` (9 hits) | Comment-only references | Not a declaration; excluded from gate |

Result: 12 named-symbol declarations, all categorized; 0 uncategorized log-purposed PROGMEM hits. **Matches 09-MEASUREMENT.md byte-for-byte.** PASS.

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/include/logging.h` | DELETED | VERIFIED | `ls` returns "No such file or directory" — confirmed deleted (Plan 09-02 commit `3fa25fd`). |
| `firestarter/src/logging.c` | DELETED | VERIFIED | `ls` returns "No such file or directory" — confirmed deleted. |
| `firestarter/include/version.h` | VERSION = `"3.0.0-dev"` | VERIFIED | Line 11: `#define VERSION "3.0.0-dev"`. |
| `firestarter/src/hardware_operations.cpp` | Inline LFW-05 bootstrap `F("OK: FW: ") + println(FW_VERSION) + flush()` | VERIFIED | Single inline F() literal at line 88; D-01 rationale comment at line 85-87. |
| `firestarter/src/dev_tools.cpp` | Two `LOG_OK_ID(MSG_OK_READY)` (lines 108 + 154) | VERIFIED | Plan 09-01 commits `bfd203b` + `ad5233a`. |
| `firestarter/src/firestarter.cpp` | `#ifdef SERIAL_DEBUG / debug_setup() / #endif` deleted | VERIFIED | No `debug_setup` references anywhere. |
| `firestarter/include/rurp_shield.h` | `rurp_log` + `rurp_log_P` decls deleted; `rurp_log_id` survivors preserved | VERIFIED | Live grep for `rurp_log\b\|rurp_log_P` returns 0 hits across firmware tree. |
| `firestarter/include/rurp_serial_utils.h` | `_firestarter_log_ram` + `_firestarter_log_progmem` decls deleted | VERIFIED | Live grep for `_firestarter_log_` returns 0 hits. |
| `firestarter/src/boards/rurp_serial_utils.cpp` | Helper bodies + weak defaults deleted; `_firestarter_emit_frame*` + `rurp_log_id*` preserved | VERIFIED | MAGIC_PREAMBLE + CRC8_TABLE remain; legacy bodies removed. |
| `firestarter/src/boards/uno_rurp_shield.cpp` | RX/TX_DEBUG defines + SoftwareSerial debug + `debug_setup` + `log_debug` + Uno strong overrides for legacy log helpers deleted | VERIFIED | Live grep for `debug_setup\|log_debug\b\|RX_DEBUG\|TX_DEBUG\|SoftwareSerial.*debug` returns 0 hits in production source. |
| `firestarter/src/boards/leonardo_rurp_shield.cpp` | `debug_setup` stub deleted | VERIFIED | Live grep returns 0 hits. |
| `firestarter_app/firestarter/serial_comm.py` | `FIRESTARTER_DEV_ALLOW_PRE_V12` rationale comment refreshed (post-Phase-9 framing); mechanism intact | VERIFIED | Plan 09-03 commit `firestarter_app@7f9b944`; pytest fwguard 4/4 PASS confirms guard mechanism unchanged. |
| `firestarter/test/native/avr/_shared/host_stubs_common.inc` | 8 `LOG_*_MSG` externs + 2 `rurp_log` no-op stubs deleted (27 dead lines trimmed) | VERIFIED | Native test suite still 20/20 PASS (15 dispatch + 5 messages) — link succeeds, surviving register-surface stubs preserved. Plan 09-04 commit `ace9274`. |
| `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md` | Phase-close measurement artifact with all SC sections | VERIFIED | 403-line file with anchor table extension, 4-delta attribution, two-table PROGMEM audit, LFW-03 gate result, SC#3/4/5 results, bench placeholders for Tasks 2+3. |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `firestarter/src/hardware_operations.cpp:88` (`fw_get_version()`) | host `_probe_port` parser at `serial_comm.py:747-748` | Inline `F("OK: FW: ") + println(FW_VERSION)` emit → host regex `r"FW:\s*([\d.x]+)"` | WIRED | LFW-05 bootstrap supplies the `FW: ` prefix unconditionally; FW_VERSION composes `3.0.0-dev:<board>`. |
| Firmware `VERSION 3.0.0-dev` | Host major<3 refuse guard at `serial_comm.py:761` | Numeric comparison of parsed major version | WIRED | pytest test_fwguard.py 4/4 PASS confirms: (a) pre-v1.2 firmware refused unless env-var set, (b) v3.x firmware accepted, (c) env-var bypass works, (d) version parse handles edge cases. |
| Plan 09-01 `LOG_OK_ID(MSG_OK_READY)` emit sites in `dev_tools.cpp` | id-frame emit infrastructure in `rurp_serial_utils.cpp` | `rurp_log_id_wide()` → `_firestarter_emit_frame*` | WIRED | Native `test_messages` 5/5 PASS — `test_zero_param_frame`, `test_u32_param_frame`, `test_multi_param_frame`, `test_crc_polynomial_smoke`, `test_oversize_param_count_rejected`. |
| Plan 09-03 refreshed comment block at `serial_comm.py:752-754` | Active refuse-guard logic at `serial_comm.py:755-769` | Inline doc commentary above the `if major < 3 ...` check | WIRED | Comment-only refactor; `FIRESTARTER_DEV_ALLOW_PRE_V12` env-var still referenced exactly twice (one in comment, one in `os.environ.get`); pytest fwguard unchanged. |

---

## Data-Flow Trace (Level 4)

| Artifact | Data variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `fw_get_version()` inline emit (`hardware_operations.cpp:85-88`) | `FW_VERSION` literal | `VERSION ":" RURP_BOARD_NAME` macro composition in `version.h:11` + board ENV define | Yes — emits real `3.0.0-dev:<board>` string over SERIAL_PORT | FLOWING |
| 09-MEASUREMENT.md anchor table (Phase 9 close row) | Flash byte counts | Cold-cache `pio run` output for both AVR targets | Yes — measurements reproduce byte-for-byte across independent runs (this verifier confirmed live) | FLOWING |
| 09-MEASUREMENT.md PROGMEM audit table | 12 declaration sites | Live grep of `firestarter/src + include` for `PROGMEM` keyword | Yes — verifier re-ran the grep and got byte-identical category counts | FLOWING |
| `serial_comm.py` refuse-guard comment | Inline doc text | Plan 09-03 edit | N/A — comment artifact, not a data-flowing artifact | N/A |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Leonardo AVR build links cleanly | `pio run -e leonardo -t clean && pio run -e leonardo` | SUCCESS, Flash 85.3% / 24456 B | PASS |
| Uno AVR build links cleanly | `pio run -e uno -t clean && pio run -e uno` | SUCCESS, Flash 68.9% / 22226 B | PASS |
| Native dispatch + messages tests pass | `pio test -e native -f '*test_dispatch*' -f '*test_messages*'` | 20 / 20 succeeded | PASS |
| Host firmware-guard pytest green | `pytest tests/test_fwguard.py` | 4 passed | PASS |
| Host decoder pytest green | `pytest tests/test_decoder.py` | 25 passed | PASS |
| LFW-03 grep gate clean | `grep -rn 'send_ack\|rurp_log\b\|...' firestarter/{src,include,lib}` | 0 hits | PASS |
| SC#1 PROGMEM audit categorization | Live grep + cross-check vs `09-MEASUREMENT.md` Table (a) | 12 named-symbol decls all in {MAGIC_PREAMBLE, CRC8_TABLE, json_parser keys + key_parsers[]}; 0 uncategorized | PASS |
| `logging.h` / `logging.c` deletion | `ls firestarter/include/logging.h firestarter/src/logging.c` | both "No such file or directory" | PASS |

---

## Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|---------------|-------------|--------|----------|
| **LFW-03** | 09-01, 09-02, 09-04, 09-05 | All firmware log call-sites that today use `OK:` / `INIT:` / `MAIN:` / `END:` / `INFO:` / `WARN:` / `ERROR:` PROGMEM strings are converted to `rurp_log_id` (or the LOG_* macro form). Every former format-string is represented as a single entry in the canonical catalog. | **COVERED** | SC#2 live grep gate returns 0 hits across firmware tree; host_stubs trim (Plan 09-04) removes the last test-side references to the deleted production symbols; Plan 09-01 converts the final `send_ack("")` call-sites in dev_tools.cpp. |
| **LFW-04** | 09-02, 09-05 | `firestarter/src/`, `firestarter/include/`, `firestarter/lib/` contain zero PROGMEM string literals that exist only to be passed to a log function. (`DATA:` prefix marker and any non-log PROGMEM strings are exempt and noted explicitly.) | **COVERED** | SC#1 live audit: 12 named-symbol PROGMEM declarations, all in non-log exemption classes (MAGIC_PREAMBLE / CRC8_TABLE / json_parser keys); 0 uncategorized log-purposed PROGMEM. `logging.c` (which held `LOG_OK_MSG` PROGMEM) deleted outright. |
| **LMIG-04** | 09-02, 09-03, 09-05 | Old `rurp_log` / `rurp_log_P` / `LOG_*_MSG` PROGMEM definitions and `log_info_const` / `log_error_format` / `log_warn` macros are removed. `pio run -e leonardo` produces a final flash-savings number documented in the milestone close. Target: bring Leonardo flash below 90% with measurable headroom. | **COVERED** (autonomous side); bench native-pass + chip UAT pending (Plan 09-05 Tasks 2+3, hardware) | SC#4 Leonardo 85.3% < 90% with 4216 B headroom; 09-MEASUREMENT.md publishes the milestone-close acceptance number (−3843 B / −13.4 pp vs v1.1 baseline 98.7%). Phase 10 DOC-02 will quote verbatim. The phase-target "Leonardo flash below 90% with measurable headroom" is satisfied; chip-seated UAT extends operational confirmation but does not change the milestone number. |

No orphaned requirements — REQUIREMENTS.md line 119 maps Phase 9 to exactly `LFW-03, LFW-04, LMIG-04`, and all three are claimed by the plans.

---

## Anti-Patterns Scan

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter/include/version.h` | (all) | TBD/FIXME/XXX/TODO debt markers | (none) | No debt markers in any modified production file. |
| `firestarter/src/hardware_operations.cpp` | (all) | TBD/FIXME/XXX/TODO | (none) | Clean. |
| `firestarter/src/firestarter.cpp` | (all) | TBD/FIXME/XXX/TODO | (none) | Clean. |
| `firestarter/include/rurp_shield.h` | (all) | TBD/FIXME/XXX/TODO | (none) | Clean. |
| `firestarter/include/rurp_serial_utils.h` | (all) | TBD/FIXME/XXX/TODO | (none) | Clean. |
| `firestarter/src/boards/rurp_serial_utils.cpp` | (all) | TBD/FIXME/XXX/TODO | (none) | Clean. |
| `firestarter/src/boards/uno_rurp_shield.cpp` | (all) | TBD/FIXME/XXX/TODO | (none) | Clean. |
| `firestarter/src/boards/leonardo_rurp_shield.cpp` | (all) | TBD/FIXME/XXX/TODO | (none) | Clean. |
| `firestarter_app/firestarter/serial_comm.py` | (all) | TBD/FIXME/XXX/TODO | (none) | Clean. |
| `firestarter/test/native/avr/_shared/host_stubs_common.inc` | (all) | TBD/FIXME/XXX/TODO | (none) | Clean. |
| `firestarter/include/logging_id.h` | 13 | Stale doc comment: "Coexists with the legacy log_*_const / log_*_format macros in logging.h (LMIG-01)" — `logging.h` has now been deleted | INFO | Non-load-bearing header doc commentary describing Phase 6 design intent; the reference to a now-deleted file is historically accurate (it described the LMIG-01 transitional state). Could be refreshed in a follow-up doc pass but does not affect compilation, behavior, or any verification gate. Not introduced by Phase 9 — the comment dates from Phase 6 (LMIG-01). |

Spot-checks for empty/stub patterns: all modified files exercise the full intended behavior (LFW-05 inline emit, ID-frame infrastructure, fwguard regression, etc.); no `return null` / `return {}` / `=> {}` stubs introduced.

---

## Out-of-Scope Concerns (NOT Introduced by Phase 9)

| Concern | Status | Phase 9 Impact |
|---------|--------|---------------|
| `native/avr/test_flash_intel_vpp` ERRORED (SIGABRT mid-suite — 1 case PASSED before abort) | Pre-existing per `09-RESEARCH.md` §"Risks & Landmines" #5 and `09-01-SUMMARY.md` §"Issues Encountered" | None — this suite exercises `flash_intel.cpp` (Intel 28F command-register flash); Phase 9 deletes only logging infrastructure. The suite ERRORED pre- and post-Phase-9 per Plan 09-02 SUMMARY. The full native suite reports 22/24 succeed; the 2 ERRORs are stable. |
| `native/avr/test_eeprom28c_chip_id` ERRORED (aborted before any test ran) | Pre-existing per `09-RESEARCH.md` and Plan 09-01/02 SUMMARYs | None — this suite exercises `eeprom_28c.cpp` chip-ID flow; Phase 9 deletes only logging infrastructure. Should be tracked separately (recommend filing as deferred technical debt for a follow-on plan). |
| Stale doc comment in `firestarter/include/logging_id.h:13` referencing now-deleted `logging.h` | INFO (non-blocking) | Cosmetic; pre-Phase-9 commentary from LMIG-01 Phase 6 design. Could be refreshed in Phase 10 close docs. |
| Pre-existing `feature/phase-10-static-pins` work-in-progress in `firestarter/` sub-repo | Out-of-scope — explicitly preserved per Plan 09-02 (only Phase 9 files were staged) | None — Phase 10 work-in-progress is intact; no merge conflicts created. |

---

## Hardware-Pending UAT Items

These are the same `checkpoint:human-verify` items surfaced by Plan 09-05 (the only non-autonomous plan in Phase 9). Both are documented operator-on-bench tasks, not Phase 9 implementation gaps. The plan frontmatter explicitly marks Tasks 2 + 3 as non-autonomous, and CONTEXT.md Claude's-Discretion bundles the Phase 8 SC#2/SC#3 carry-over here as well. **The phase is functionally complete on the autonomous side; these UAT items are operational confirmation.**

### UAT-1 — Task 2 of Plan 09-05: Chipless bench wire-protocol matrix re-run

**Test:** Flash both Uno + Leonardo with the 3.0.0-dev firmware; exercise `firestarter -p <port> fw / hw / config / vpp / vpe / id W27C512` on both boards **without** the `FIRESTARTER_DEV_ALLOW_PRE_V12=1` env-var prefix.

**Expected:**
- No `FirmwareOutdatedError` on either board (confirms SC#3 native-pass — `major=3` accepted natively, not via the env-var bypass).
- Uno `fw` output contains substring `OK: FW: 3.0.0-dev:uno`.
- Leonardo `fw` output contains substring `OK: FW: 3.0.0-dev:leonardo`.
- All other frames byte-identical to the Phase 8 baseline severity-band shape (per 08-MEASUREMENT.md:332-342).

**Why human:** Requires physical Uno + Leonardo boards on operator's bench (ports `/dev/ttyACM0` + `/dev/ttyACM1`); cannot execute programmatically from this environment.

**Operator recovery commands:**

```bash
cd /workspaces/firestarter_prom/firestarter
pio run -t upload -e uno --upload-port /dev/ttyACM0
pio run -t upload -e leonardo --upload-port /dev/ttyACM1
firestarter -p /dev/ttyACM0 fw       # expect: OK: FW: 3.0.0-dev:uno, HW: Rev1, Cmd: 0x0b
firestarter -p /dev/ttyACM1 fw       # expect: OK: FW: 3.0.0-dev:leonardo, HW: Rev1, Cmd: 0x0b
firestarter -p /dev/ttyACM0 hw       && firestarter -p /dev/ttyACM1 hw
firestarter -p /dev/ttyACM0 config   && firestarter -p /dev/ttyACM1 config
firestarter -p /dev/ttyACM0 vpp      && firestarter -p /dev/ttyACM1 vpp
firestarter -p /dev/ttyACM0 vpe      && firestarter -p /dev/ttyACM1 vpe
firestarter -p /dev/ttyACM0 id W27C512  && firestarter -p /dev/ttyACM1 id W27C512
```

Operator transcribes observed outputs into the Bench Verification section of `09-MEASUREMENT.md` (placeholders pre-filled in the artifact's per-row table). Resume signal: `bench-chipless-approved`.

### UAT-2 — Task 3 of Plan 09-05: Phase 8 SC#2 + SC#3 chip-seated W27C512 write + readback carry-over

**Test:** Run `firestarter write -e W27C512 <hex>` + `firestarter read -e W27C512 -o <out.bin>` + `diff <baseline.bin> <out.bin>` on **both** Uno + Leonardo with a physical W27C512 chip seated in each shield socket in turn.

**Expected:**
- Both boards: write completes with success message (no ERROR-band frame).
- Both boards: INIT / MAIN / END acks rendered as decoded id-frame text (NOT raw `INIT:` / `MAIN:` / `END:` text prefixes — confirms Phase 8 W-01 wire-format preserved through Phase 9 deletions).
- Both boards: `OK: FW: 3.0.0-dev:<board>` bootstrap line present at command start (LFW-05 preserved).
- `diff` returns zero output on both boards (byte-identical readback vs operator's pre-Phase-8 baseline `.bin`).
- If Leonardo readback diverges, at least one re-seat attempt is documented before declaring regression (per project memory `[[project_leonardo-shield-socket-wonky]]`).

**Why human:** Requires physical Uno + Leonardo + W27C512 chip (or substitute) on operator's bench; chip seating + binary readback comparison cannot run programmatically. This is the Phase 8 SC#2/SC#3 carry-over per CONTEXT.md Claude's-Discretion bundle, NOT a Phase 9-introduced gap.

**Operator recovery commands:**

```bash
# Per [[feedback_ic-removal-autonomy]] — chip-swap cycles without per-cycle operator confirmation
# Seat W27C512 in Uno shield socket, then:
firestarter -p /dev/ttyACM0 write -e W27C512 <test.hex>
firestarter -p /dev/ttyACM0 read  -e W27C512 -o /tmp/ph9-uno-readback.bin
diff <baseline.bin> /tmp/ph9-uno-readback.bin

# Move chip to Leonardo, then:
firestarter -p /dev/ttyACM1 write -e W27C512 <test.hex>
firestarter -p /dev/ttyACM1 read  -e W27C512 -o /tmp/ph9-leonardo-readback.bin
diff <baseline.bin> /tmp/ph9-leonardo-readback.bin

# If Leonardo readback diverges, re-seat per [[project_leonardo-shield-socket-wonky]] before declaring a regression.
# If no chip available, annotate "no chip available — carrying Phase 8 SC#2/SC#3 to Phase 10".
```

Operator transcribes observed outputs into the Phase 8 SC#2 + Phase 8 SC#3 sections of `09-MEASUREMENT.md`. Resume signal: `chip-uat-approved` or `no chip available — carrying Phase 8 SC#2/SC#3 to Phase 10` or `readback-regression` (the latter is a STOP — would indicate Phase 9 broke the wire format).

---

## Goal-Backward Analysis

Working backward from the phase goal:

1. **"All legacy firmware log infrastructure deleted from `firestarter/src/`, `firestarter/include/`, `firestarter/lib/`"** — VERIFIED. Live LFW-03 grep returns 0 hits across the full firmware tree. `logging.h` + `logging.c` confirmed deleted. SC#2 ✓.
2. **"Firmware major version bumps to 3.0.0 so old hosts refuse to talk to new firmware (and vice versa)"** — VERIFIED on both halves. Source: `version.h:11` = `"3.0.0-dev"`; host: pytest `test_fwguard.py` 4/4 PASS confirming the refuse-guard rejects `major<3` unless env-var bypass set. Bench native-pass (actual wire output from physical 3.0.0-dev firmware) = UAT-1 — additional operational evidence, not strictly required for SC#3 closure. SC#3 ✓ (autonomous halves) + ⏸ (bench).
3. **"Formal flash-usage measurement recorded for both Uno and Leonardo, with the Leonardo number compared to the v1.1 baseline of 98.7%"** — VERIFIED. `09-MEASUREMENT.md` published (403 lines); anchor table extends 08-MEASUREMENT.md:310-316 with the Phase 9 close row; 4-delta attribution computes the LMIG-04 acceptance number (−3843 B / −13.4 pp vs v1.1). SC#4 ✓ (Leonardo 85.3% < 90%) + SC#5 ✓ (Uno 68.9% recorded). PROGMEM exemption audit (SC#1) closed with 12 named-symbol declarations all categorized, 0 uncategorized log-purposed hits.

**Union of all 5 plans achieves every SC.** LFW-03 + LFW-04 + LMIG-04 all closed by the implemented work (autonomous side). The two operator-on-bench UAT items are operational confirmation for Phase 9's wire format + chip-seated programming, not gaps in the implementation.

---

## Gaps Summary

**No autonomous-side gaps.** All 5 success criteria PASS against the live codebase:

- SC#1: 12/12 PROGMEM declarations categorized; 0 uncategorized log-purposed hits.
- SC#2: 0 hits in the LFW-03 grep gate.
- SC#3: VERSION = `3.0.0-dev` in source; host fwguard pytest 4/4 PASS.
- SC#4: Leonardo Flash 85.3% < 90%, 4216 B headroom; −3843 B / −13.4 pp vs v1.1 baseline.
- SC#5: Uno Flash 68.9% recorded.

Two hardware-pending UAT items (UAT-1 + UAT-2 above) require operator-on-bench; these are explicit checkpoints from Plan 09-05 (`autonomous=false`), not Phase 9 implementation gaps. Same pattern as Phase 8 SC#2/SC#3 hardware-pending carry-over. Status: `human_needed`.

---

*Verified: 2026-05-19*
*Verifier: Claude (gsd-verifier, opus-4.7 1M-ctx)*
