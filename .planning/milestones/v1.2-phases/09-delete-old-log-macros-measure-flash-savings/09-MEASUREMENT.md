---
phase: 09-delete-old-log-macros-measure-flash-savings
slug: 09-MEASUREMENT
status: TASK_1_GREEN_BENCH_PENDING
created: 2026-05-19
requirements: [LFW-03, LFW-04, LMIG-04]
---

# Phase 9 — Flash + SRAM Budget Measurement (LMIG-04 milestone-close)

**Measured:** 2026-05-19
**Boards:** Leonardo + Uno
**Repo state at measurement:**
- `firestarter` HEAD = `ace9274c7b697036351b585b5e78f9fb60e03831` (Phase 9 Plan 04 close — host-stubs trim)
- `firestarter_app` HEAD = `7f9b944073714cfc9f0d810abd6b0f40c5be2ebf` (Phase 9 Plan 03 close — FIRESTARTER_DEV_ALLOW_PRE_V12 comment refresh)
- meta-repo HEAD = `ede1593` (Phase 9 Plan 04 SUMMARY committed)

**Phase 8 close reference:** Leonardo 85.6% (24,538 / 28,672 bytes), 4,134 B free; Uno 69.2% (22,330 / 32,256 bytes), 9,926 B free.

---

## Anchor Table

Extends `08-MEASUREMENT.md:310-316` with the Phase 9 close row replacing the prior TARGET/TBD placeholder. This is the canonical 5-row milestone table; Phase 10 DOC-02 will quote the v1.1 → Phase 9 row verbatim into `MILESTONES.md`.

| Snapshot | Leonardo Flash | Uno Flash | SRAM (Uno) | Notes |
|----------|----------------|-----------|------------|-------|
| **v1.1 close** | 98.7% (~28,299 / 28,672) | not formally recorded | — | ROADMAP-pinned baseline; per-byte derived from %. |
| **Phase 6 close** | 98.7% (28,292 / 28,672), 380 B free | 80.9% (26,100 / 32,256), 6,156 B free | 1,683 B / 2,048 B (Uno) | LMIG-01: new ID infrastructure alongside legacy text; no call-sites converted yet. |
| **Phase 7 close** | 94.3% (27,026 / 28,672), 1,646 B free | 77.0% (24,838 / 32,256), 7,418 B free | 1,587 B / 2,048 B (Uno) | LMIG-02: all ERROR/WARN/INFO call-sites converted; dead-code deleted. |
| **Phase 8 close** | 85.6% (24,538 / 28,672), 4,134 B free | 69.2% (22,330 / 32,256), 9,926 B free | 1,497 B / 2,048 B (Uno) | LMIG-03: OK/INIT/MAIN/END state-machine acks + MSG_DATA_CHUNK streaming + R-01 SRAM win. |
| **Phase 9 close (LMIG-04)** | **85.3% (24,456 / 28,672), 4,216 B free** | **68.9% (22,226 / 32,256), 10,030 B free** | **1,497 B / 2,048 B (Uno)** | LMIG-04: legacy macro tower deletion (`send_ack`, `send_ack_const`, `rurp_log*`, `_firestarter_log_*`, `LOG_OK_MSG`, `debug_setup`, `log_debug`); inline `OK: FW: ` bootstrap (D-01); FW version → 3.0.0-dev. |

**Leonardo SRAM:** 57.2% (1,465 / 2,560 bytes used), 1,095 B free.

**LMIG-04 SC#4 gate:** Leonardo Flash 85.3% < 90.0% — **PASS** (4,216 B headroom).
**LMIG-04 SC#5 gate:** Uno Flash recorded alongside (68.9%) — **PASS**.

---

## 4-Delta Attribution

Per `09-RESEARCH.md` §"Deltas to compute and record" — Phase 9's row contributes four comparison points against the locked anchor rows. Byte counts are authoritative (PROGMEM rounds to 1 decimal place per RESEARCH.md Risk #6); percentage-point deltas computed from absolute % values.

| Delta | Leonardo bytes saved | Leonardo pp Δ | Uno bytes saved | Uno pp Δ | Significance |
|-------|----------------------|---------------|-----------------|----------|--------------|
| **v1.1 (98.7%) → Phase 9 close** | **−3,843 B** (28,299 → 24,456) | **−13.4 pp** | — (Uno v1.1 not formally recorded) | — | **LMIG-04 acceptance number — Phase 10 DOC-02 cites verbatim into MILESTONES.md** |
| Phase 6 close → Phase 9 close | −3,836 B (28,292 → 24,456) | −13.4 pp | −3,874 B (26,100 → 22,226) | −12.0 pp | "Pure migration recovery" — catalog overhead cost recovered, net positive |
| Phase 7 close → Phase 9 close | −2,570 B (27,026 → 24,456) | −9.0 pp | −2,612 B (24,838 → 22,226) | −8.1 pp | "State-machine + cleanup contribution" — Phase 8 + Phase 9 combined |
| **Phase 8 close → Phase 9 close** | **−82 B** (24,538 → 24,456) | **−0.3 pp** | **−104 B** (22,330 → 22,226) | **−0.3 pp** | **"Logging.h macro tower deletion, isolated"** — the Phase 9 surface win, attributable purely to Plan 09-01/02 changes |

**Phase 9 incremental win attribution** (per 09-CONTEXT.md D-08 — both rows must appear):
- Plan 09-01 (dev_tools `send_ack` → `LOG_OK_ID(MSG_OK_READY)` conversions): −36 B Leonardo / −48 B Uno (informational baseline from 09-01-SUMMARY.md).
- Plan 09-02 (atomic legacy deletion + version bump + inline LFW-05 bootstrap): −46 B Leonardo / −56 B Uno (delta from 09-01 baseline 24,508 / 22,282 to Plan 09-02 close 24,456 / 22,226 — the macro-tower deletion plus `_firestarter_log_*` helper removal plus `LOG_OK_MSG` PROGMEM deletion). Note: Plan 09-02 SUMMARY's recorded Flash numbers (24,456 / 22,226) match this measurement byte-for-byte — confirming cold-cache reproducibility and that Plans 09-03 (host-only) + 09-04 (test-stub-only) introduced zero firmware Flash change, as expected.
- Plan 09-03 (host comment refresh): 0 B firmware change (host-side only).
- Plan 09-04 (host_stubs trim): 0 B firmware change (test-stub file only; excluded from `[env:uno]` + `[env:leonardo]` builds).
- **Phase 9 total:** −82 B Leonardo / −104 B Uno vs Phase 8 close.

The Phase 9 surface win is smaller than the Phase 8 incremental win (−2,488 B Leonardo / −2,508 B Uno) by ~30x — expected, because Phase 8 deleted active code (PARSE_RESPONSE composite + format-string templates), while Phase 9 deletes infrastructure that was *already* mostly inlined-away by the AVR optimizer in production (`debug_setup` was an empty `SERIAL_DEBUG`-gated stub; `rurp_log` weak defaults were inline-thin wrappers; `LOG_OK_MSG` was a 3-byte literal). The win that matters is the LMIG-04 milestone-close number (−3,843 B Leonardo vs v1.1), not the incremental Phase 8 → Phase 9 number.

---

## Build Output Excerpts

Both excerpts captured from **cold-cache** builds (`pio run -e {env} -t clean && pio run -e {env}`) per `09-RESEARCH.md` §"Risks & Landmines #5 + #7". The byte count (not the percentage) is the authoritative figure per Risk #6.

### Leonardo (`pio run -e leonardo`)

```
Processing leonardo (platform: atmelavr; board: leonardo; framework: arduino)
--------------------------------------------------------------------------------
PLATFORM: Atmel AVR (5.2.0) > Arduino Leonardo
HARDWARE: ATMEGA32U4 16MHz, 2.50KB RAM, 28KB Flash
DEBUG: Current (simavr) External (simavr)
PACKAGES:
 - framework-arduino-avr @ 5.3.0
 - toolchain-atmelavr @ 1.70300.191015 (7.3.0)
LDF: Library Dependency Finder -> https://bit.ly/configure-pio-ldf
LDF Modes: Finder ~ chain, Compatibility ~ soft
Building in release mode
Linking .pio/build/leonardo/firestarter_leonardo.elf
Checking size .pio/build/leonardo/firestarter_leonardo.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [======    ]  57.2% (used 1465 bytes from 2560 bytes)
Flash: [========= ]  85.3% (used 24456 bytes from 28672 bytes)
Building .pio/build/leonardo/firestarter_leonardo.hex
========================= [SUCCESS] Took 1.14 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
leonardo       SUCCESS   00:00:01.137
========================= 1 succeeded in 00:00:01.137 =========================
```

### Uno (`pio run -e uno`)

```
Processing uno (platform: atmelavr; board: uno; framework: arduino)
--------------------------------------------------------------------------------
PLATFORM: Atmel AVR (5.2.0) > Arduino Uno
HARDWARE: ATMEGA328P 16MHz, 2KB RAM, 31.50KB Flash
DEBUG: Current (avr-stub) External (avr-stub, simavr)
PACKAGES:
 - framework-arduino-avr @ 5.3.0
 - toolchain-atmelavr @ 1.70300.191015 (7.3.0)
LDF: Library Dependency Finder -> https://bit.ly/configure-pio-ldf
LDF Modes: Finder ~ chain, Compatibility ~ soft
Building in release mode
Linking .pio/build/uno/firestarter_uno.elf
Checking size .pio/build/uno/firestarter_uno.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [=======   ]  73.1% (used 1497 bytes from 2048 bytes)
Flash: [=======   ]  68.9% (used 22226 bytes from 32256 bytes)
Building .pio/build/uno/firestarter_uno.hex
========================= [SUCCESS] Took 1.19 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:01.190
========================= 1 succeeded in 00:00:01.190 =========================
```

---

## SC#1 — PROGMEM Exemption Audit

Per `09-RESEARCH.md` §"Risks & Landmines #8" and `09-CONTEXT.md` D-01, this audit produces **two distinct labeled tables** representing two mutually-exclusive syntactic patterns:

- **Table (a) — named-symbol PROGMEM declarations:** the SC#1 acceptance gate. Every hit must fall in one of the three documented exemption classes (`MAGIC_PREAMBLE`, `CRC8_TABLE`, json_parser keys + `key_parsers[]` table). Any uncategorized hit is an SC#1 violation.
- **Table (d) — inline `F("...")` Arduino-macro literal sites:** anonymous compiler-generated PROGMEM, **exempt by definition** per CONTEXT.md D-01 (the LFW-05 inline bootstrap uses `F("OK: FW: ")`). Documented for completeness; **does not gate SC#1 acceptance**.

The two tables are mutually exclusive — `F("...")` literals do NOT yield named symbols and so cannot match `grep PROGMEM`, while named-symbol PROGMEM declarations do not use the `F(...)` macro. No site appears in both tables.

### Table (a) — Named-symbol PROGMEM declarations (the SC#1 acceptance gate)

Raw `grep -rn 'PROGMEM' firestarter/src firestarter/include` returned **21 hits**; of these, **12 are actual named-symbol declarations** and the remaining 9 are comment-only references (e.g. `// Magic preamble (4 bytes from PROGMEM)`, breadcrumb comments referencing the deleted `_firestarter_log_*` helpers, debug doc commentary in `logging_id.h`). The categorization below uses only the 12 declarations:

| # | File:line | Symbol | Category | Exempt class | Notes |
|---|-----------|--------|----------|--------------|-------|
| 1 | `firestarter/src/boards/rurp_serial_utils.cpp:105` | `static const uint8_t MAGIC_PREAMBLE[4] PROGMEM` | (a1) | **MAGIC_PREAMBLE** (frame infra) | 4-byte frame-start sentinel; emitted unconditionally as the first 4 bytes of every id-frame; not log-related. |
| 2 | `firestarter/src/boards/rurp_serial_utils.cpp:108` | `static const uint8_t CRC8_TABLE[256] PROGMEM` | (a2) | **CRC8_TABLE** (frame infra) | 256-entry lookup table for the per-frame CRC8 checksum; not log-related. |
| 3 | `firestarter/src/json_parser.c:66` | `const char key_mem_size[] PROGMEM = "memory-size"` | (a3) | **json_parser keys** (parser infra) | EPROM JSON command-payload key (consumed by `parse_json`); not log-related. |
| 4 | `firestarter/src/json_parser.c:67` | `const char key_address[] PROGMEM = "address"` | (a3) | **json_parser keys** | same; parser infra. |
| 5 | `firestarter/src/json_parser.c:68` | `const char key_flags[] PROGMEM = "flags"` | (a3) | **json_parser keys** | same; parser infra. |
| 6 | `firestarter/src/json_parser.c:69` | `const char key_chip_id[] PROGMEM = "chip-id"` | (a3) | **json_parser keys** | same; parser infra. |
| 7 | `firestarter/src/json_parser.c:59` | `const char key_pin_count[] PROGMEM = "pin-count"` | (a3) | **json_parser keys** | same; parser infra. |
| 8 | `firestarter/src/json_parser.c:71` | `const char key_pulse_delay[] PROGMEM = "pulse-delay"` | (a3) | **json_parser keys** | same; parser infra. |
| 9 | `firestarter/src/json_parser.c:72` | `const char key_vpp_mv[] PROGMEM = "vpp_mv"` | (a3) | **json_parser keys** | same; parser infra. |
| 10 | `firestarter/src/json_parser.c:62` | `const char key_type[] PROGMEM = "type"` | (a3) | **json_parser keys** | same; parser infra. |
| 11 | `firestarter/src/json_parser.c:74` | `const char key_algorithm[] PROGMEM = "algorithm"` | (a3) | **json_parser keys** | same; parser infra. |
| 12 | `firestarter/src/json_parser.c:97` | `static const key_parser_t key_parsers[] PROGMEM` | (a3) | **key_parsers[] table** (parser infra) | Table of `(key, handler)` pairs binding each key string to its parse callback; not log-related. |

**Categorization summary:**
- (a1) MAGIC_PREAMBLE (frame infra): **1 hit**
- (a2) CRC8_TABLE (frame infra): **1 hit**
- (a3) json_parser keys + key_parsers[] (parser infra): **10 hits**
- **(a-uncat) Uncategorized log-purposed PROGMEM strings: 0 hits**

**SC#1 acceptance gate: PASS** — every named-symbol PROGMEM declaration falls in a documented exemption class; zero hits in an "uncategorized log-purposed PROGMEM" bucket. LFW-04 satisfied.

The 9 comment-only hits (lines containing the word `PROGMEM` in a `//` comment) are NOT declarations and so are correctly excluded from the gate. For completeness, those 9 are: `hardware_operations.cpp:86` (D-01 rationale comment for the inline `F("OK: FW: ")` literal); `rurp_shield.h:128`, `rurp_serial_utils.h:13`, `rurp_serial_utils.cpp:13,227`, `uno_rurp_shield.cpp:75` (six breadcrumb comments describing the deleted `_firestarter_log_ram` + `_firestarter_log_progmem` "RAM body + PROGMEM body" helpers — per Plan 09-02 grep-gate-safety convention); `logging_id.h:255` (debug-channel doc commentary mentioning PROGMEM as the contrast for "no PROGMEM allocation"); `rurp_serial_utils.cpp:148,192` (two `// Magic preamble (4 bytes from PROGMEM)` comments describing the emit-frame helpers).

### Table (d) — Inline `F("...")` Arduino-macro literal sites (informational, exempt by definition)

Raw `grep -rn 'F("' firestarter/src firestarter/include` returned **2 hits**; of these, **1 is an actual `F("...")` literal site** (the other is a comment that contains the string `F("OK: FW: ")` in its rationale prose):

| # | File:line | Site | Notes |
|---|-----------|------|-------|
| 1 | `firestarter/src/hardware_operations.cpp:85` | `// legacy send-ack-const / rurp-log-P chain was deleted. F("OK: FW: ") keeps` | **Comment only** — rationale for the inline emit on the next line. Not an actual `F()` literal evaluation. |
| 2 | `firestarter/src/hardware_operations.cpp:88` | `SERIAL_PORT.print(F("OK: FW: "));` | **The single inline `F("...")` literal in production firmware.** The LFW-05 bootstrap from CONTEXT.md D-01. Yields an anonymous compiler-generated PROGMEM literal-array at call-site; no named symbol. |

**Inline F() literal count:** **1** (the LFW-05 bootstrap at `hardware_operations.cpp:88`).

**Note (mandatory per the planner's instruction):**

> Category (a) named-symbol PROGMEM declarations gate SC#1; category (d) inline F() literals are exempt per CONTEXT.md D-01 + RESEARCH.md Risk #8 and are documented for completeness only. No site is double-counted between the two tables — the syntactic patterns (`PROGMEM` keyword in a declaration vs. `F(` macro invocation in an expression) cannot match the same source location.

---

## SC#2 — Legacy Macro Grep Gate

Per `09-VALIDATION.md` row 9-02, the canonical LFW-03 gate is:

```bash
grep -rn 'send_ack\|rurp_log\b\|rurp_log_P\|_firestarter_log_\|LOG_OK_MSG\|log_info_const\|log_error_format\|log_warn\b\|debug_setup\|log_debug\b' \
  firestarter/src firestarter/include firestarter/lib 2>/dev/null \
  | grep -v 'rurp_log_id' \
  | grep -v '^[^:]*:[[:space:]]*//' \
  | wc -l
```

**Result:** `0` hits.

The grep output (`/tmp/ph9-grep-legacy.txt`) is empty — zero legacy macro callers, declarations, or non-comment references remain in `firestarter/src/` + `firestarter/include/` + `firestarter/lib/` outside of the `rurp_log_id` survivors (preserved per CONTEXT.md, the ID-frame surface) and comment-only lines (Phase 9 breadcrumb prose).

**SC#2 acceptance gate: PASS** — LFW-03 satisfied.

---

## SC#3 — Host fw-guard Regression

Per `09-VALIDATION.md` row 9-03 + `09-RESEARCH.md` §"Host-side Surface" — exercised via `pytest tests/test_fwguard.py`:

```
$ cd firestarter_app && pytest tests/test_fwguard.py -v
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0
rootdir: /workspaces/firestarter_prom/firestarter_app
configfile: pyproject.toml
plugins: anyio-4.13.0
collected 4 items

tests/test_fwguard.py ....                                               [100%]

============================== 4 passed in 0.03s ===============================
```

**SC#3 host-side gate: PASS** — 4 / 4 fw-guard cases green. The major<3 refuse-guard at `serial_comm.py:761` continues to reject pre-v1.2 firmware unless `FIRESTARTER_DEV_ALLOW_PRE_V12=1` is set; the bench-side native-pass exercise (no env-var prefix, firmware reports `3.0.0-dev`) is captured in the bench section below — operator-on-bench step.

---

## SC#4 + SC#5 — Flash Recorded (Phase 9 anchor row, inline for readability)

| Board | Flash Used | Flash Total | Pct | Bytes Free | Phase 8 → Phase 9 Δ |
|-------|-----------:|------------:|-----:|----------:|-------------------:|
| Leonardo | 24,456 B | 28,672 B | **85.3%** | 4,216 B | **−82 B** (−0.3 pp) |
| Uno | 22,226 B | 32,256 B | **68.9%** | 10,030 B | **−104 B** (−0.3 pp) |

**LMIG-04 SC#4 acceptance:** Leonardo Flash 85.3% < 90.0% with **4,216 B of headroom** — **PASS**.
**LMIG-04 SC#5 acceptance:** Uno Flash 68.9% recorded alongside (10,030 B free) — **PASS**.

---

## Bench Verification — Chipless Wire-Protocol Validation

**Status:** ⏸ **Pending operator-on-bench** (Task 2 of Plan 09-05).

Per `09-RESEARCH.md` §"Bench Verification Matrix Re-use" — re-run the Phase 8 chipless wire-protocol matrix on `3.0.0-dev` firmware **without** the `FIRESTARTER_DEV_ALLOW_PRE_V12=1` prefix to exercise the SC#3 native-pass guard path. Per project memory `[[feedback_always-mirror-uno-leonardo-tests]]` every Uno command is paired with a Leonardo run as the control.

### Bench commands to run (operator)

```bash
# 1. Flash both boards with the Phase 9 firmware
cd /workspaces/firestarter_prom/firestarter
pio run -t upload -e uno --upload-port /dev/ttyACM0
pio run -t upload -e leonardo --upload-port /dev/ttyACM1   # adjust port if different

# 2. SC#3 native-pass verification (no FIRESTARTER_DEV_ALLOW_PRE_V12 prefix)
firestarter -p /dev/ttyACM0 fw       # expect: OK: FW: 3.0.0-dev:uno, HW: Rev1, Cmd: 0x0b
firestarter -p /dev/ttyACM1 fw       # expect: OK: FW: 3.0.0-dev:leonardo, HW: Rev1, Cmd: 0x0b

# 3. Full chipless matrix re-run (mirrors 08-MEASUREMENT.md lines 322-384)
firestarter -p /dev/ttyACM0 hw       # P-02 sentinel
firestarter -p /dev/ttyACM1 hw
firestarter -p /dev/ttyACM0 config   # P-03 sentinel
firestarter -p /dev/ttyACM1 config
firestarter -p /dev/ttyACM0 vpp      # MSG_DATA_VPP_VOLTAGE
firestarter -p /dev/ttyACM1 vpp
firestarter -p /dev/ttyACM0 vpe      # MSG_DATA_VPE_VOLTAGE
firestarter -p /dev/ttyACM1 vpe
firestarter -p /dev/ttyACM0 id W27C512   # exercises INIT_DONE
firestarter -p /dev/ttyACM1 id W27C512   # may ERROR on VPP-overshoot on Leonardo — expected, validates ERROR-band rendering
```

### Expected outputs (operator transcribes observed values into the table below)

Per `08-MEASUREMENT.md:332-342`, the severity-band frame-coverage table. **Only the `fw` output should differ from the Phase 8 baseline** — the FW-version string changes from `2.0.11-dev` to `3.0.0-dev`. All other frames should be byte-identical in wire shape.

| Band | Frame | Uno result (observed) | Leonardo result (observed) |
|------|-------|-----------------------|----------------------------|
| OK composite (P-04) | MSG_OK_FW_HANDSHAKE u8+u8+ascii_str | _pending — expect `OK: FW: 3.0.0-dev:uno, HW: Rev1, Cmd: 0x0b`_ | _pending — expect `OK: FW: 3.0.0-dev:leonardo, HW: Rev1, Cmd: 0x0b`_ |
| OK fixed (P-02) | MSG_OK_REV u8+u8 | _pending — expect `Rev1` (0xFF sentinel)_ | _pending — expect `Rev1, Override HW: Rev2` (non-sentinel)_ |
| OK fixed (P-03) | MSG_OK_CFG u32+u32+u8 | _pending — expect `R1: 270000, R2: 44000`_ | _pending — expect `R1: 270000, R2: 44000, Override HW: Rev1`_ |
| INFO | MSG_INFO_* free-text | _pending_ | _pending_ |
| INIT | MSG_INIT_DONE | _pending — expect `INIT: (init done)` from `id W27C512`_ | _pending — may be preempted by VPP-overshoot ERROR_ |
| DATA (W-03) | MSG_DATA_VPP_VOLTAGE u16+u16 | _pending — expect `DATA: VPP: ~11.5V, Internal VCC: ~5.0V`_ | _pending — expect `DATA: VPP: ~13.1V, Internal VCC: ~5.5V`_ |
| DATA (W-03) | MSG_DATA_VPE_VOLTAGE u16+u16 | _pending — expect `DATA: VPE: ~13.2V, Internal VCC: ~5.0V`_ | _pending — expect `DATA: VPE: ~15.3V, Internal VCC: ~5.5V`_ |
| ERROR | MSG_ERROR_* (parameterized) | _pending — likely not triggered chipless_ | _pending — likely `ERROR: VPP is high: 13.1V > 12.0V` on Leonardo `id W27C512`_ |

**Acceptance criteria for Task 2:**
- No `FirmwareOutdatedError` on either board (confirms SC#3 native-pass — `major=3` accepted natively).
- Uno `fw` output contains the substring `OK: FW: 3.0.0-dev:uno`.
- Leonardo `fw` output contains the substring `OK: FW: 3.0.0-dev:leonardo`.
- Every other frame matches the Phase 8 baseline severity-band shape; sentinel branch coverage between the two boards remains complete.

### Operator notes

- Per `[[feedback_always-mirror-uno-leonardo-tests]]` — every Uno command paired with Leonardo control.
- Per `[[project_leonardo-shield-socket-wonky]]` — chipless matrix does NOT seat a chip; socket-contact issues should not apply here.

---

## Phase 8 SC#2 (carried) — Chip-Seated Write

**Status:** ⏸ **Pending operator-on-bench** (Task 3 of Plan 09-05; Phase 8 carry-over per CONTEXT.md Claude's-Discretion).

Per `08-MEASUREMENT.md` §"SC#2 Manual Verification Plan" + `09-RESEARCH.md` §"Phase 8 UAT Carry-over" — verify `firestarter write -e W27C512 <hex>` runs end-to-end on both Uno and Leonardo with:

1. Success message (no ERROR-band frame).
2. INIT / MAIN / END acks rendered as decoded id-frame text (NOT raw `INIT:` / `MAIN:` / `END:` text prefixes — Phase 8 W-01 wire-format change confirmed).
3. Bootstrap `OK: FW: 3.0.0-dev:<board>` text line present at command start (LFW-05 preserved).

### Operator bench commands

```bash
# Per [[feedback_ic-removal-autonomy]] no per-cycle chip-removal confirmation needed.

# Uno: seat W27C512 in Uno shield socket, then:
firestarter -p /dev/ttyACM0 write -e W27C512 <test.hex>

# Leonardo: move chip to Leonardo shield socket, then:
firestarter -p /dev/ttyACM1 write -e W27C512 <test.hex>
# If Leonardo write fails or behaves erratically, re-seat first per [[project_leonardo-shield-socket-wonky]]
```

### Acceptance criteria for Task 3 SC#2

- Both boards: command completes with success message.
- Both boards: INIT/MAIN/END decoded from id-frame (no raw `INIT:`/`MAIN:`/`END:` text prefix in CLI output).
- Both boards: `OK: FW: 3.0.0-dev:<board>, ...` bootstrap line present.
- If Leonardo write fails: at least one re-seat attempt documented before declaring regression.

### Operator transcript (to fill)

```
# Uno write transcript:
_pending operator transcription_

# Leonardo write transcript:
_pending operator transcription_
```

OR if no W27C512 available: "no chip available — carrying Phase 8 SC#2 to Phase 10".

---

## Phase 8 SC#3 (carried) — Byte-Identical Readback

**Status:** ⏸ **Pending operator-on-bench** (Task 3 of Plan 09-05; Phase 8 carry-over per CONTEXT.md Claude's-Discretion).

Per `08-MEASUREMENT.md` §"SC#3 Manual Verification Plan" + `09-RESEARCH.md` §"Phase 8 UAT Carry-over" — verify `firestarter read -e W27C512 -o out.bin` produces a byte-identical binary file vs the operator's pre-Phase-8 baseline (or capture a fresh `3.0.0-dev` baseline if none exists, noting it as the new v1.2+ reference).

### Operator bench commands

```bash
# Uno readback:
firestarter -p /dev/ttyACM0 read -e W27C512 -o /tmp/ph9-uno-readback.bin
diff <baseline.bin> /tmp/ph9-uno-readback.bin

# Leonardo readback:
firestarter -p /dev/ttyACM1 read -e W27C512 -o /tmp/ph9-leonardo-readback.bin
diff <baseline.bin> /tmp/ph9-leonardo-readback.bin
# If non-zero diff on Leonardo only: re-seat chip per [[project_leonardo-shield-socket-wonky]] and re-run before declaring a regression
```

### Acceptance criteria for Task 3 SC#3

- Both boards: `diff` returns zero output (byte-identical readback).
- If Leonardo readback diverges from Uno: re-seat attempt(s) documented per `[[project_leonardo-shield-socket-wonky]]`.
- If both boards diverge consistently after re-seat: STOP — this would indicate Phase 9 broke the wire format despite Task 2's chipless validation. Surface as `readback-regression` blocker.

### Operator transcript (to fill)

```
# Uno read + diff transcript:
_pending operator transcription_

# Leonardo read + diff transcript:
_pending operator transcription_
```

OR if no baseline / no chip available: "no chip available — carrying Phase 8 SC#3 to Phase 10" (with rationale).

---

## Project Memory Active During Bench Steps

- `[[feedback_always-mirror-uno-leonardo-tests]]` — every Uno bench command paired with Leonardo control. Applied throughout Tasks 2 + 3.
- `[[project_leonardo-shield-socket-wonky]]` — suspect chip contact first when Leonardo chip-seated readback diverges; re-seat before declaring a regression.
- `[[feedback_ic-removal-autonomy]]` — chip-swap cycles between boards proceed without per-cycle operator confirmation.

---

## Summary

| Gate | Status | Notes |
|------|--------|-------|
| SC#1 — PROGMEM exemption audit (named-symbol + inline F() tables) | ✓ PASS | 12 named-symbol declarations all categorized (MAGIC_PREAMBLE / CRC8_TABLE / json_parser keys); 1 inline F() literal site (LFW-05 bootstrap, exempt). Zero uncategorized hits. |
| SC#2 — Legacy macro grep gate | ✓ PASS | 0 hits in `firestarter/src/include/lib`. |
| SC#3 — Host fw-guard regression (pytest) | ✓ PASS | 4 / 4 PASS. |
| SC#3 — Bench native-pass (firmware reports 3.0.0-dev) | ⏸ Pending bench | Operator runs Task 2. |
| SC#4 — Leonardo Flash < 90% with headroom | ✓ PASS | 85.3%, 4,216 B free. |
| SC#5 — Uno Flash recorded alongside | ✓ PASS | 68.9%, 10,030 B free. |
| Phase 8 SC#2 (carried) — chip-seated W27C512 write on both boards | ⏸ Pending bench | Operator runs Task 3. |
| Phase 8 SC#3 (carried) — byte-identical readback on both boards | ⏸ Pending bench | Operator runs Task 3. |

**Phase 9 close LMIG-04 acceptance number:** Leonardo Flash **85.3% (24,456 / 28,672 bytes)** — a **−3,843-byte reduction (−13.4 percentage points)** vs the v1.1 close baseline of 98.7% (28,299 / 28,672). This is the figure Phase 10 DOC-02 quotes verbatim into `MILESTONES.md`.

---

*Phase: 09-delete-old-log-macros-measure-flash-savings*
*Plan: 05-measurement-and-bench-uat (Task 1 of 3 complete; Tasks 2 + 3 pending operator-on-bench)*
*Measurement date: 2026-05-19*
