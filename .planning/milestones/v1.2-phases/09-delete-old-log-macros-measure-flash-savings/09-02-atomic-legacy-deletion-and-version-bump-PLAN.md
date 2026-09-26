---
phase: 09-delete-old-log-macros-measure-flash-savings
plan: 02
type: execute
wave: 2
depends_on: [09-01-dev-tools-send-ack-conversion]
files_modified:
  - firestarter/include/logging.h
  - firestarter/src/logging.c
  - firestarter/include/version.h
  - firestarter/src/hardware_operations.cpp
  - firestarter/src/boards/rurp_serial_utils.cpp
  - firestarter/include/rurp_serial_utils.h
  - firestarter/include/rurp_shield.h
  - firestarter/src/boards/uno_rurp_shield.cpp
  - firestarter/src/boards/leonardo_rurp_shield.cpp
  - firestarter/src/firestarter.cpp
  - firestarter/include/operation_utils.h
  - firestarter/include/rurp_hw_rev_utils.h
  - firestarter/src/eprom_operations.cpp
  - firestarter/src/json_parser.c
  - firestarter/src/operation_utils.cpp
  - firestarter/src/proms/eeprom_28c.cpp
  - firestarter/src/proms/eprom.cpp
  - firestarter/src/proms/flash_intel.cpp
  - firestarter/src/proms/flash_type_3.cpp
  - firestarter/src/proms/flash_type_4.cpp
  - firestarter/src/proms/flash_utils.cpp
  - firestarter/src/proms/memory.cpp
  - firestarter/src/proms/sram.cpp
autonomous: true
requirements:
  - LFW-03
  - LFW-04
requirements_addressed:
  - LFW-03
  - LFW-04
tags:
  - logging
  - firmware
  - deletion
  - version-bump
user_setup: []
must_haves:
  truths:
    - "The legacy text-prefix log infrastructure (send_ack, send_ack_const, rurp_log, rurp_log_P, _firestarter_log_ram, _firestarter_log_progmem, LOG_OK_MSG, debug_setup, log_debug) is deleted from firestarter/src/ + firestarter/include/ + firestarter/lib/"
    - "logging.h and logging.c are deleted as files; all 20 #include \"logging.h\" sites have the include line removed"
    - "fw_get_version() at hardware_operations.cpp emits the LFW-05 bootstrap line via an inline F(\"OK: FW: \") + println(FW_VERSION) + flush 3-liner; post-D-01 wire shape is `OK: FW: <FW_VERSION>` (e.g. `OK: FW: 3.0.0-dev:uno`). This INTENTIONALLY adds the literal `FW: ` substring vs pre-D-01 `OK: <FW_VERSION>` and is required by host `_probe_port` at `serial_comm.py:747-748`."
    - "VERSION = \"3.0.0-dev\" in version.h:11 (was \"2.0.11-dev\")"
    - "All four #ifdef SERIAL_DEBUG blocks referencing debug_setup / log_debug / debugSerial / RX_DEBUG / TX_DEBUG are deleted atomically (firestarter.cpp:38-40, uno_rurp_shield.cpp:22-25 [the four-line `#ifdef SERIAL_DEBUG / #define RX_DEBUG A0 / #define TX_DEBUG A1 / #endif` block], uno_rurp_shield.cpp:144-161, leonardo_rurp_shield.cpp:144-146)"
    - "pio run -e uno and pio run -e leonardo both build SUCCESS"
    - "firestarter_app/tests/test_fwguard.py reports 4 PASS (SC#3 host-guard regression is satisfied by the version bump exercising the existing major<3 refuse path)"
    - "grep gate: zero hits in firestarter/src/ + firestarter/include/ + firestarter/lib/ for send_ack | send_ack_const | rurp_log\\b | rurp_log_P | _firestarter_log_ | LOG_OK_MSG | log_info_const | log_error_format | log_warn\\b | debug_setup | log_debug\\b"
  artifacts:
    - path: "firestarter/include/version.h"
      provides: "Firmware version macro at 3.0.0-dev (major bump satisfies host guard at serial_comm.py:761)"
      contains: '#define VERSION "3.0.0-dev"'
    - path: "firestarter/src/hardware_operations.cpp"
      provides: "Inlined LFW-05 bootstrap emit (the sole surviving text-format log line)"
      contains: 'SERIAL_PORT.print(F("OK: FW: "))'
    - path: "firestarter/src/boards/rurp_serial_utils.cpp"
      provides: "Surviving rurp_log_id / rurp_log_id_wide ID-frame helpers; rurp_log + rurp_log_P + _firestarter_log_* deleted"
      contains: "rurp_log_id"
  key_links:
    - from: "firestarter/src/hardware_operations.cpp"
      to: "firestarter/include/version.h"
      via: "inline print(F(\"OK: FW: \")) + println(FW_VERSION)"
      pattern: 'OK: FW: '
    - from: "firestarter_app/firestarter/serial_comm.py:756-762"
      to: "firestarter/include/version.h"
      via: "host major<3 refuse guard now actively engaged on pre-Phase-9 firmware"
      pattern: "major.*<.*3"
---

<objective>
Atomic deletion of the entire legacy text-prefix logging infrastructure from the firmware, combined with the LFW-05 bootstrap inline (D-01) and the firmware major version bump to 3.0.0-dev (D-06). This plan must land as a single coherent change because (a) deleting `send_ack` / `rurp_log` macros without inlining `fw_get_version()` first would break compilation, and (b) the host's `major < 3` refuse guard at `serial_comm.py:761` becomes load-bearing the moment this firmware reports `3.0.0-dev`, so the SC#3 regression test must run against the same artifact.

Purpose: implement LFW-03 (zero legacy log callers / definitions remain) + LFW-04 (zero PROGMEM strings exist solely to feed log functions) + LFW-05 firmware side (major version bump). The Phase 8 close left exactly this surface; Phase 9 Plan 02 removes it.
Output: Firmware that builds clean on Uno + Leonardo with only the inline `OK: FW: 3.0.0-dev` text line as a non-ID-frame emit; legacy-macro grep gate returns zero hits; host test_fwguard.py passes unchanged.
</objective>

<execution_context>
@/workspaces/firestarter_prom/.claude/get-shit-done/workflows/execute-plan.md
@/workspaces/firestarter_prom/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-VALIDATION.md
@.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-01-SUMMARY.md
@firestarter/CLAUDE.md
@firestarter/include/logging.h
@firestarter/include/version.h
@firestarter/src/hardware_operations.cpp
@firestarter/src/boards/rurp_serial_utils.cpp
@firestarter/include/rurp_serial_utils.h
@firestarter/src/boards/uno_rurp_shield.cpp
@firestarter/src/boards/leonardo_rurp_shield.cpp
@firestarter/src/firestarter.cpp
@firestarter/include/rurp_shield.h

<interfaces>
<!-- The deletion targets and their exact line ranges. Source: 09-RESEARCH.md §"Deletion Inventory" + §"File-Fate Audits". -->

LFW-05 inline target (firestarter/src/hardware_operations.cpp:82-88, current state):
```cpp
bool fw_get_version(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_FW_VERSION);
    // Phase 8 / P-01 / LFW-05: MSG_OK_FW_VERSION stays text-emitted to preserve
    // the host's _probe_port bootstrap path, which parses "FW: ..." as text.
    send_ack_const(FW_VERSION);
    return true;
}
```

After D-01:
```cpp
bool fw_get_version(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_FW_VERSION);
    // Phase 9 / LFW-05: lone surviving text-format emit. Inlined here after the
    // legacy send_ack_const / rurp_log_P chain was deleted. F("OK: FW: ") keeps
    // the literal in PROGMEM with no named symbol — same exemption class as
    // MAGIC_PREAMBLE / CRC8_TABLE (SC#1).
    SERIAL_PORT.print(F("OK: FW: "));
    SERIAL_PORT.println(FW_VERSION);
    SERIAL_PORT.flush();
    return true;
}
```

FW_VERSION macro (firestarter/include/firestarter.h:16):
```cpp
#define FW_VERSION VERSION ":" RURP_BOARD_NAME
```
FW_VERSION is the BARE composed string (no `FW:` prefix). After the version bump in Task 2, FW_VERSION expands at compile time to e.g. `"3.0.0-dev:uno"`. The literal `F("OK: FW: ")` supplies the `OK: FW: ` prefix; the wire output is `OK: FW: 3.0.0-dev:uno`.

logging.h symbols to delete (entire file deleted):
- `extern const char LOG_OK_MSG[] PROGMEM;` (line 22)
- `send_ack(msg)` macro (lines 25-26)
- `send_ack_const(msg)` macro (lines 28-29)
- `#ifdef SERIAL_DEBUG / void debug_setup(); / void log_debug(...); / #else / #define debug_setup() / #define log_debug(...) / #endif` (lines 31-41)

logging.c symbols to delete (entire file deleted):
- `const char LOG_OK_MSG[] PROGMEM = "OK";`

rurp_serial_utils.cpp deletion targets (full source unchanged for frame-emit code; lines per 09-RESEARCH.md):
- Lines 14-28 (approx): `_firestarter_log_ram(PGM_P, const char*)` + `_firestarter_log_progmem(PGM_P, PGM_P)` function bodies
- Lines 246-251: `__attribute__((weak)) void rurp_log(PGM_P, const char*)` + `__attribute__((weak)) void rurp_log_P(PGM_P, PGM_P)` weak defaults

rurp_serial_utils.h deletion targets (lines 14-17 per 09-RESEARCH.md):
- `void _firestarter_log_ram(PGM_P type, const char* msg);`
- `void _firestarter_log_progmem(PGM_P type, PGM_P p_msg);`

rurp_shield.h deletion targets (lines 132-133 per 09-RESEARCH.md):
- `void rurp_log(PGM_P type, const char* msg);`
- `void rurp_log_P(PGM_P type, PGM_P msg);`
(KEEP: `void rurp_log_id(...)` and `void rurp_log_id_wide(...)` declarations on adjacent lines.)

uno_rurp_shield.cpp deletion targets:
- Lines 22-25: the complete `#ifdef SERIAL_DEBUG / #define RX_DEBUG A0 / #define TX_DEBUG A1 / #endif` block (four lines — confirmed against current source)
- Lines 80-91: `void rurp_log(...)` Uno strong override + `void rurp_log_P(...)` Uno strong override
- Lines 152-169: `#ifdef SERIAL_DEBUG / #include <SoftwareSerial.h> / SoftwareSerial debugSerial(...); / void debug_setup() { ... } / void log_debug(...) { ... } / #endif`
(KEEP: `rurp_log_id` Uno strong override surrounding lines 98-110.)

leonardo_rurp_shield.cpp deletion target:
- Lines 144-146: `#ifdef SERIAL_DEBUG / void debug_setup() {} / #endif`

firestarter.cpp deletion target:
- Lines 38-40 (inside `setup()`): `#ifdef SERIAL_DEBUG / debug_setup(); / #endif`

20 #include "logging.h" sites — DROP the include line at each (see Task 4 list).

version.h:11:
- Before: `#define VERSION "2.0.11-dev"`
- After:  `#define VERSION "3.0.0-dev"`
</interfaces>
</context>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Inline LFW-05 bootstrap in fw_get_version() — D-01</name>
  <read_first>
    - firestarter/src/hardware_operations.cpp (read lines 1-100; the target function is at lines 82-88; the live LOG_OK_ID(MSG_OK_READY) analog is at lines 40-42)
    - firestarter/src/boards/rurp_serial_utils.cpp lines 22-30 (the `_firestarter_log_progmem` body — the idiom being transplanted inline)
    - firestarter/include/firestarter.h line 16 (the FW_VERSION macro definition — CONFIRMED as `VERSION ":" RURP_BOARD_NAME`, a bare composed string with NO `FW:` prefix)
    - firestarter_app/firestarter/serial_comm.py lines 740-770 (the `_probe_port` `'FW:' in msg` substring test + `r"FW:\s*([\d.x]+)"` regex — the load-bearing host parse)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md §"LFW-05 bootstrap path" — D-01
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md §"Pattern Assignment 1"
  </read_first>
  <files>firestarter/src/hardware_operations.cpp</files>
  <behavior>
    - Before: `fw_get_version()` calls `send_ack_const(FW_VERSION);` which expands to `rurp_log_P(LOG_OK_MSG, PSTR(FW_VERSION))` → wire output `OK: <FW_VERSION>` (e.g. `OK: 2.0.11-dev:uno`).
    - After: `fw_get_version()` directly emits via `SERIAL_PORT.print(F("OK: FW: "))` + `SERIAL_PORT.println(FW_VERSION)` + `SERIAL_PORT.flush()` → wire output `OK: FW: <FW_VERSION>` (e.g. `OK: FW: 3.0.0-dev:uno` after Task 2's version bump).
    - **Wire-shape change is INTENTIONAL, not byte-identical.** Post-D-01 emit ADDS the literal `FW: ` substring (was `OK: <version>`, becomes `OK: FW: <version>`). This is REQUIRED by the host's `_probe_port` parse at `serial_comm.py:747-748` which tests `if msg and 'FW:' in msg:` then runs `re.search(r"FW:\s*([\d.x]+)", msg)`. Plan 05 Task 2's bench step validates the post-D-01 wire shape end-to-end with `firestarter -p <port> fw` returning `OK: FW: 3.0.0-dev:<board>`.
    - The `LOG_DEBUG_ID_SUB(DBG_GET_FW_VERSION)` at the top of the function STAYS (Phase 8 debug-channel emit).
    - The `#include "logging.h"` at line 7 is DROPPED in Task 4 (include sweep); do NOT drop it in this task — Task 4 is the atomic sweep.
    - `#include "logging_id.h"` at line 8 stays (provides LOG_DEBUG_ID_SUB).
  </behavior>
  <action>
    At `firestarter/src/hardware_operations.cpp:82-88`, replace the body of `fw_get_version()` so the `send_ack_const(FW_VERSION);` call (one line) is replaced by the inline three-liner from D-01 / 09-PATTERNS.md §"Pattern Assignment 1":

    The new body keeps `LOG_DEBUG_ID_SUB(DBG_GET_FW_VERSION);` as the first statement, replaces the existing comment with the new LFW-05 rationale comment (per 09-PATTERNS.md exact wording: "Phase 9 / LFW-05: lone surviving text-format emit. Inlined here after the legacy send_ack_const / rurp_log_P chain was deleted. F(\"OK: FW: \") keeps the literal in PROGMEM with no named symbol — same exemption class as MAGIC_PREAMBLE / CRC8_TABLE (SC#1)."), then emits `SERIAL_PORT.print(F("OK: FW: "));` followed by `SERIAL_PORT.println(FW_VERSION);` and `SERIAL_PORT.flush();`, then `return true;`.

    FW_VERSION is defined in `firestarter/include/firestarter.h:16` as `VERSION ":" RURP_BOARD_NAME` — a BARE version string (no `FW:` prefix). Emit the 3-liner exactly as CONTEXT.md D-01 specifies: `SERIAL_PORT.print(F("OK: FW: "))` + `SERIAL_PORT.println(FW_VERSION)` + `SERIAL_PORT.flush()`. The wire produces `OK: FW: 3.0.0-dev:uno` (after Task 2's version bump), which the host's `_probe_port` regex at `serial_comm.py:747-748` matches on the `FW:` substring test. There is no conditional branch — FW_VERSION never contains `FW:` so the inline form supplies the prefix unconditionally.

    Do NOT touch the `#include "logging.h"` at line 7 in this task — Task 4 owns the atomic include sweep across all 20 sites. Do NOT touch any other code in the file.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_prom/firestarter &amp;&amp; grep -c 'SERIAL_PORT.print(F("OK: FW: "))' src/hardware_operations.cpp &amp;&amp; grep -c 'SERIAL_PORT.println(FW_VERSION)' src/hardware_operations.cpp &amp;&amp; grep -c 'SERIAL_PORT.flush()' src/hardware_operations.cpp &amp;&amp; [ "$(grep -c 'send_ack_const' src/hardware_operations.cpp)" = "0" ]</automated>
  </verify>
  <acceptance_criteria>
    - `grep -n 'SERIAL_PORT.print(F("OK: FW: "))' firestarter/src/hardware_operations.cpp` returns exactly 1 line (the new inline emit)
    - `grep -n 'SERIAL_PORT.println(FW_VERSION)' firestarter/src/hardware_operations.cpp` returns exactly 1 line
    - `grep -c 'send_ack_const' firestarter/src/hardware_operations.cpp` returns 0
    - `grep -c 'LOG_DEBUG_ID_SUB(DBG_GET_FW_VERSION)' firestarter/src/hardware_operations.cpp` is unchanged (Phase 8 debug emit retained)
  </acceptance_criteria>
  <done>
    - `fw_get_version()` body emits the LFW-05 line inline via three `SERIAL_PORT.*` calls
    - The new rationale comment per 09-PATTERNS.md §"Pattern Assignment 1" is present
    - No `send_ack_const` references remain in `hardware_operations.cpp`
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Bump firmware version to 3.0.0-dev — D-06</name>
  <read_first>
    - firestarter/include/version.h (current state)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md §"Version bump shape" — D-06 + D-07
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md §"Pattern Assignment 3" (the `bbf0e0c` analog 1-line diff)
    - firestarter_app/firestarter/serial_comm.py lines 750-770 (the host major&lt;3 refuse guard)
  </read_first>
  <files>firestarter/include/version.h</files>
  <behavior>
    - Before: `#define VERSION "2.0.11-dev"` (at version.h:11)
    - After: `#define VERSION "3.0.0-dev"`
    - No other changes to version.h (no banner/comment edits, no struct changes)
    - The `-dev` suffix stays — Phase 10 release-tag op strips it
  </behavior>
  <action>
    At `firestarter/include/version.h:11`, change the string literal in `#define VERSION "2.0.11-dev"` to `"3.0.0-dev"`. Preserve all surrounding lines exactly: the include-guard `#ifndef __VERSION_H__`, the `#define __VERSION_H__`, the copyright header, the trailing `#endif // __VERSION_H__`. The macro name `VERSION` is unchanged. This is the literal 1-line diff per 09-PATTERNS.md §"Pattern Assignment 3" (analog: prior commit `bbf0e0c`).
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_prom/firestarter &amp;&amp; grep -c '#define VERSION "3.0.0-dev"' include/version.h &amp;&amp; [ "$(grep -c '#define VERSION "2.0.11-dev"' include/version.h)" = "0" ]</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c '#define VERSION "3.0.0-dev"' firestarter/include/version.h` returns exactly 1
    - `grep -c '2.0.11-dev' firestarter/include/version.h` returns 0
    - File still contains the include guard `#ifndef __VERSION_H__` / `#define __VERSION_H__` / `#endif`
  </acceptance_criteria>
  <done>
    - VERSION macro is `"3.0.0-dev"` (major bump = 3 satisfies the host's `major < 3` refuse guard at `serial_comm.py:761`)
    - No other content in version.h has changed
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 3: Delete legacy log macro tower + debug_setup/log_debug + SoftwareSerial — D-02 + D-08 Claude's Discretion</name>
  <read_first>
    - firestarter/include/logging.h (the entire file — being deleted)
    - firestarter/src/logging.c (the entire file — being deleted)
    - firestarter/src/boards/rurp_serial_utils.cpp (read lines 1-30 and 240-267 — the surfaces being deleted)
    - firestarter/include/rurp_serial_utils.h (read lines 1-30)
    - firestarter/include/rurp_shield.h (read lines 125-145 — surrounding the rurp_log + rurp_log_P decls)
    - firestarter/src/boards/uno_rurp_shield.cpp (read lines 1-30, 75-95, 145-171 — confirm the `#ifdef SERIAL_DEBUG / #define RX_DEBUG A0 / #define TX_DEBUG A1 / #endif` block at lines 22-25 and the larger SoftwareSerial block at 152-169 before editing)
    - firestarter/src/boards/leonardo_rurp_shield.cpp (read lines 140-148)
    - firestarter/src/firestarter.cpp (read lines 30-50)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md §"Deletion Inventory" (full per-symbol grep tables) + §"Risks & Landmines" #1, #2, #3
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md §"Implementation Decisions" — D-02, D-08
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md §"Pattern Assignment 4" + §"Pattern Assignment 5"
  </read_first>
  <files>
    firestarter/include/logging.h,
    firestarter/src/logging.c,
    firestarter/src/boards/rurp_serial_utils.cpp,
    firestarter/include/rurp_serial_utils.h,
    firestarter/include/rurp_shield.h,
    firestarter/src/boards/uno_rurp_shield.cpp,
    firestarter/src/boards/leonardo_rurp_shield.cpp,
    firestarter/src/firestarter.cpp
  </files>
  <behavior>
    - `firestarter/include/logging.h` — file removed from disk
    - `firestarter/src/logging.c` — file removed from disk
    - `firestarter/src/boards/rurp_serial_utils.cpp` — lines 14-28 (`_firestarter_log_ram` + `_firestarter_log_progmem` function bodies) removed; lines 246-251 (`rurp_log` + `rurp_log_P` weak defaults) removed; the surviving `rurp_log_id` / `rurp_log_id_wide` weak defaults and `_firestarter_emit_frame` stay
    - `firestarter/include/rurp_serial_utils.h` — `_firestarter_log_ram` + `_firestarter_log_progmem` declarations (lines 14-17 approx) removed; surviving `_firestarter_emit_frame` decl stays
    - `firestarter/include/rurp_shield.h` — `void rurp_log(PGM_P type, const char* msg);` + `void rurp_log_P(PGM_P type, PGM_P msg);` declarations (lines 132-133 per 09-RESEARCH.md) removed; surviving `rurp_log_id` + `rurp_log_id_wide` declarations stay
    - `firestarter/src/boards/uno_rurp_shield.cpp` — three blocks removed atomically: (a) the complete `#ifdef SERIAL_DEBUG / #define RX_DEBUG A0 / #define TX_DEBUG A1 / #endif` block at lines 22-25 (four lines — confirmed against current source); (b) `rurp_log` + `rurp_log_P` Uno strong-override function bodies at lines 80-91; (c) the entire `#ifdef SERIAL_DEBUG` block at lines 152-169 (containing `#include <SoftwareSerial.h>` + `SoftwareSerial debugSerial(...);` + `debug_setup()` + `log_debug()`). The surviving `rurp_log_id` Uno strong override (lines ~98-110) stays
    - `firestarter/src/boards/leonardo_rurp_shield.cpp` — `#ifdef SERIAL_DEBUG / void debug_setup() {} / #endif` block at lines 144-146 removed
    - `firestarter/src/firestarter.cpp` — `#ifdef SERIAL_DEBUG / debug_setup(); / #endif` block inside `setup()` at lines 38-40 removed (the `setup()` body's surrounding code stays exactly as before — no other reordering)
  </behavior>
  <action>
    Atomic deletion across 8 files. Follow the analog: Phase 8 commit `275522a` (multi-file SERIAL_DEBUG cleanup) per 09-PATTERNS.md §"Pattern Assignment 5".

    1. **Delete `firestarter/include/logging.h`** outright (rm the file). Per 09-RESEARCH.md §"File-Fate Audits" → "logging.h — DELETE the file" the file's substantive content (LOG_OK_MSG extern, send_ack macros, debug_setup/log_debug decls) has zero remaining callers after this commit completes.

    2. **Delete `firestarter/src/logging.c`** outright. Per 09-RESEARCH.md §"File-Fate Audits" → "logging.c — DELETE the file" the file contains only `const char LOG_OK_MSG[] PROGMEM = "OK";` and two includes; both go. `platformio.ini` requires NO changes (the `[env:native]` `src_filter` is positive-only inclusion; production builds pick up `.c` files via default pattern and will simply not find this one).

    3. **Edit `firestarter/src/boards/rurp_serial_utils.cpp`**: delete the `_firestarter_log_ram(PGM_P type, const char* msg) { ... }` function body (lines ~14-20) AND the `_firestarter_log_progmem(PGM_P type, PGM_P p_msg) { ... }` function body (lines ~22-28). Also delete the two weak-default function bodies at lines 246-251: `__attribute__((weak)) void rurp_log(PGM_P type, const char* msg) { ... }` and `__attribute__((weak)) void rurp_log_P(PGM_P type, PGM_P msg) { ... }`. The surviving `rurp_log_id` / `rurp_log_id_wide` weak defaults and `_firestarter_emit_frame` body (lines ~156-242) MUST stay — only the legacy text-frame helpers go.

    4. **Edit `firestarter/include/rurp_serial_utils.h`**: delete the `void _firestarter_log_ram(PGM_P type, const char* msg);` declaration (line 15) and `void _firestarter_log_progmem(PGM_P type, PGM_P p_msg);` declaration (line 18). Per 09-RESEARCH.md §"Deletion Inventory" → "_firestarter_log_ram" / "_firestarter_log_progmem" these are the only legacy-helper decls in this header.

    5. **Edit `firestarter/include/rurp_shield.h`**: delete `void rurp_log(PGM_P type, const char* msg);` at line 132 and `void rurp_log_P(PGM_P type, PGM_P msg);` at line 133. Surrounding decls (`rurp_log_id`, `rurp_log_id_wide` on adjacent lines) MUST stay.

    6. **Edit `firestarter/src/boards/uno_rurp_shield.cpp`** — three separate block deletions atomic in this file:
        - (a) Delete the complete `#ifdef SERIAL_DEBUG / #define RX_DEBUG A0 / #define TX_DEBUG A1 / #endif` block at lines 22-25 (the RX/TX defines are dead after step (c) below removes the SoftwareSerial consumer). Anchor on the syntactic block, not the brittle line range — confirm the four-line block by re-reading lines 20-30 before deletion.
        - (b) Lines 80-91 (approx): delete the `void rurp_log(PGM_P type, const char* msg) { ... }` Uno strong-override function body AND the `void rurp_log_P(PGM_P type, PGM_P msg) { ... }` Uno strong-override function body. Per 09-RESEARCH.md §"Deletion Inventory" the Uno overrides are at lines 80-90 of the current source.
        - (c) Lines 152-169 (approx): delete the entire `#ifdef SERIAL_DEBUG / #include <SoftwareSerial.h> / SoftwareSerial debugSerial(RX_DEBUG, TX_DEBUG); / void debug_setup() { debugSerial.begin(57600); } / void log_debug(PGM_P type, const char* msg) { ... } / #endif` block.
        - The surviving `rurp_log_id` Uno strong-override function body (lines ~98-110 per 09-PATTERNS.md File Classification) MUST stay — only the legacy text-frame Uno overrides + SERIAL_DEBUG bodies go.

    7. **Edit `firestarter/src/boards/leonardo_rurp_shield.cpp`**: delete the `#ifdef SERIAL_DEBUG / void debug_setup() {} / #endif` block at lines 144-146. The surrounding `rurp_set_data_*` / Leonardo-specific functions stay.

    8. **Edit `firestarter/src/firestarter.cpp`**: delete the `#ifdef SERIAL_DEBUG / debug_setup(); / #endif` block at lines 38-40 (inside `setup()`). The surrounding code in `setup()` — Serial init, hardware init — stays exactly as before. Per 09-RESEARCH.md §"Risks & Landmines #1" this is the lone non-SERIAL_DEBUG-gated caller of `debug_setup()` (wrapped in `#ifdef SERIAL_DEBUG` itself); deletion is safe and required to keep SERIAL_DEBUG builds linkable in the future.

    All 8 file changes MUST land in this task (or in a single commit if the executor batches commits). Per 09-PATTERNS.md §"Atomic multi-file commit" pattern (analog: `275522a`) — partial state poisons the SERIAL_DEBUG build path. Production builds (`-D SERIAL_DEBUG` commented out per `platformio.ini:17`) will still compile clean even with partial state, so the executor MUST verify atomicity by running both `pio run -e uno` AND `pio run -e leonardo` AND grep gates before declaring the task done.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_prom/firestarter &amp;&amp; [ ! -f include/logging.h ] &amp;&amp; [ ! -f src/logging.c ] &amp;&amp; [ "$(grep -rln '^#include "logging.h"' src/ include/ 2>/dev/null | wc -l)" = "0" ] &amp;&amp; [ "$(grep -c '_firestarter_log_ram\|_firestarter_log_progmem' src/boards/rurp_serial_utils.cpp include/rurp_serial_utils.h)" = "0" ] &amp;&amp; [ "$(grep -E 'rurp_log[^_]|rurp_log_P' src/boards/rurp_serial_utils.cpp src/boards/uno_rurp_shield.cpp include/rurp_shield.h 2>/dev/null | grep -v 'rurp_log_id' | wc -l)" = "0" ] &amp;&amp; [ "$(grep -c 'debug_setup\|log_debug\b' src/boards/uno_rurp_shield.cpp src/boards/leonardo_rurp_shield.cpp src/firestarter.cpp 2>/dev/null)" = "0" ]</automated>
  </verify>
  <acceptance_criteria>
    - `[ ! -f firestarter/include/logging.h ]` — file does not exist
    - `[ ! -f firestarter/src/logging.c ]` — file does not exist
    - The complete `#ifdef SERIAL_DEBUG / #define RX_DEBUG A0 / #define TX_DEBUG A1 / #endif` block (the four-line syntactic block at lines 22-25 of the pre-edit `firestarter/src/boards/uno_rurp_shield.cpp`) is removed; `grep -n 'RX_DEBUG\|TX_DEBUG' firestarter/src/boards/uno_rurp_shield.cpp` returns ZERO hits
    - `grep -rn '_firestarter_log_ram\|_firestarter_log_progmem' firestarter/src/ firestarter/include/` returns ZERO hits
    - `grep -rn 'rurp_log\b\|rurp_log_P' firestarter/src/ firestarter/include/ firestarter/lib/ | grep -v 'rurp_log_id' | grep -v '^.*//'` returns ZERO non-comment hits (the `rurp_log_id` ID-frame surface is preserved)
    - `grep -rn 'debug_setup\|log_debug\b' firestarter/src/ firestarter/include/` returns ZERO hits
    - `grep -rn 'LOG_OK_MSG' firestarter/src/ firestarter/include/` returns ZERO hits
    - `grep -rn 'SoftwareSerial' firestarter/src/ firestarter/include/` returns ZERO hits (the only SoftwareSerial reference was in the SERIAL_DEBUG block at uno_rurp_shield.cpp:144-161)
    - `grep -rn 'RX_DEBUG\|TX_DEBUG' firestarter/src/ firestarter/include/` returns ZERO hits
    - `grep -rn 'send_ack\b\|send_ack_const' firestarter/src/ firestarter/include/ firestarter/lib/` returns ZERO hits (the macros are gone because logging.h is gone; callers were converted by Plan 01 + Task 1 of this plan)
  </acceptance_criteria>
  <done>
    - All 8 file modifications committed
    - All grep gates above return ZERO hits
    - `rurp_log_id` / `rurp_log_id_wide` ID-frame surface is preserved (untouched)
    - The `LOG_DEBUG_ID_SUB` debug-channel emit at `hardware_operations.cpp:fw_get_version` still works (replacement for the deleted `log_debug` path per `09-CONTEXT.md` §"Risk 11")
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 4: Sweep all 20 #include "logging.h" sites — drop the include line</name>
  <read_first>
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md §"File-Fate Audits" → "Includer enumeration" (the 20-row table)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md §"Pattern Assignment 4" (includer enumeration verbatim)
    - All 20 includer files (read just the include block at the top of each — 5 lines each)
  </read_first>
  <files>
    firestarter/include/operation_utils.h,
    firestarter/include/rurp_hw_rev_utils.h,
    firestarter/include/rurp_serial_utils.h,
    firestarter/src/boards/leonardo_rurp_shield.cpp,
    firestarter/src/boards/uno_rurp_shield.cpp,
    firestarter/src/dev_tools.cpp,
    firestarter/src/eprom_operations.cpp,
    firestarter/src/firestarter.cpp,
    firestarter/src/hardware_operations.cpp,
    firestarter/src/json_parser.c,
    firestarter/src/operation_utils.cpp,
    firestarter/src/proms/eeprom_28c.cpp,
    firestarter/src/proms/eprom.cpp,
    firestarter/src/proms/flash_intel.cpp,
    firestarter/src/proms/flash_type_3.cpp,
    firestarter/src/proms/flash_type_4.cpp,
    firestarter/src/proms/flash_utils.cpp,
    firestarter/src/proms/memory.cpp,
    firestarter/src/proms/sram.cpp
  </files>
  <behavior>
    - 19 source/header files (Task 3 already removed logging.c which had the 20th include) have their `#include "logging.h"` line deleted
    - No other code changes in these files
    - In files where `logging_id.h` is already included on an adjacent line (dev_tools.cpp:15, hardware_operations.cpp:8), the `logging_id.h` include stays
    - In `uno_rurp_shield.cpp` and `leonardo_rurp_shield.cpp` and `firestarter.cpp`, the SERIAL_DEBUG blocks referencing the deleted helpers were already removed in Task 3; the include drop in Task 4 simply removes the dangling `#include "logging.h"` that fed those (now-gone) blocks
  </behavior>
  <action>
    For each of the 19 files in the `<files>` list (logging.c was deleted in Task 3 so it is not included here), delete the single line `#include "logging.h"` at the line number specified in 09-RESEARCH.md §"File-Fate Audits" → "Includer enumeration" (and verbatim in 09-PATTERNS.md §"Pattern Assignment 4"):

    | File | Line |
    | --- | --- |
    | `firestarter/include/operation_utils.h` | 19 |
    | `firestarter/include/rurp_hw_rev_utils.h` | 10 |
    | `firestarter/include/rurp_serial_utils.h` | 8 |
    | `firestarter/src/boards/leonardo_rurp_shield.cpp` | 13 |
    | `firestarter/src/boards/uno_rurp_shield.cpp` | 13 |
    | `firestarter/src/dev_tools.cpp` | 14 |
    | `firestarter/src/eprom_operations.cpp` | 11 |
    | `firestarter/src/firestarter.cpp` | 16 |
    | `firestarter/src/hardware_operations.cpp` | 7 |
    | `firestarter/src/json_parser.c` | 12 |
    | `firestarter/src/operation_utils.cpp` | 14 |
    | `firestarter/src/proms/eeprom_28c.cpp` | 14 |
    | `firestarter/src/proms/eprom.cpp` | 13 |
    | `firestarter/src/proms/flash_intel.cpp` | 13 |
    | `firestarter/src/proms/flash_type_3.cpp` | 14 |
    | `firestarter/src/proms/flash_type_4.cpp` | 14 |
    | `firestarter/src/proms/flash_utils.cpp` | 11 |
    | `firestarter/src/proms/memory.cpp` | 18 |
    | `firestarter/src/proms/sram.cpp` | 12 |

    Use grep to confirm each file currently has exactly one `#include "logging.h"` line before deleting. After deletion, run `grep -rln '#include "logging.h"' firestarter/src/ firestarter/include/` — expect ZERO matches. Then run both AVR builds. NONE of these files should migrate to `logging_id.h` — every file that needs `logging_id.h` (`hardware_operations.cpp`, `dev_tools.cpp`, and the per-PROM source files) already has it via Phase 7/8 work; this task is purely a stale-include sweep, not a migration.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_prom/firestarter &amp;&amp; [ "$(grep -rln '#include "logging.h"' src/ include/ lib/ 2>/dev/null | wc -l)" = "0" ] &amp;&amp; pio run -e leonardo 2>&amp;1 | tail -5 | grep -q SUCCESS &amp;&amp; pio run -e uno 2>&amp;1 | tail -5 | grep -q SUCCESS</automated>
  </verify>
  <acceptance_criteria>
    - `grep -rln '#include "logging.h"' firestarter/src/ firestarter/include/ firestarter/lib/` returns ZERO files
    - `pio run -e leonardo` SUCCESS
    - `pio run -e uno` SUCCESS
    - Files where `logging_id.h` was on an adjacent line still have that include (verify by `grep -l 'logging_id.h' firestarter/src/dev_tools.cpp firestarter/src/hardware_operations.cpp` returns both files)
  </acceptance_criteria>
  <done>
    - Zero `#include "logging.h"` lines remain anywhere in the firmware
    - Both AVR builds compile clean
    - The `logging.h` deletion from Task 3 is now fully orphaned (no consumer references it)
  </done>
</task>

<task type="auto" tdd="false">
  <name>Task 5: Plan-level acceptance — LFW-03 / LFW-04 grep gates + dual AVR build + host fw-guard regression</name>
  <read_first>
    - firestarter_app/tests/test_fwguard.py (the 4 SC#3 regression cases)
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-VALIDATION.md §"Per-Task Verification Map" rows 9-02 + SC#3
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-RESEARCH.md §"Host-side Surface" → "test_fwguard.py — already SC#3-complete"
  </read_first>
  <files>(no file modifications in this task — verification only)</files>
  <behavior>
    - All LFW-03 / LFW-04 / SC#3 grep + build + pytest gates from the plan-level acceptance are green
    - Result is recorded in 09-02-SUMMARY.md
    - All shell invocations use absolute paths to avoid cwd-drift across `&&` chains
  </behavior>
  <action>
    Run the plan-level acceptance gate as a series of shell commands and record the output in `09-02-SUMMARY.md`. No code is modified by this task. All `cd` invocations use the absolute path `/workspaces/firestarter_prom/...` so the gate is order-independent and idempotent. Per 09-VALIDATION.md row 9-02 the gates are:

    1. LFW-03 / LFW-04 grep gate (from 09-VALIDATION.md):
       ```
       cd /workspaces/firestarter_prom && grep -rn 'send_ack\|rurp_log\b\|rurp_log_P\|_firestarter_log_\|LOG_OK_MSG\|log_info_const\|log_error_format\|log_warn\b\|debug_setup\|log_debug\b' firestarter/src firestarter/include firestarter/lib 2>/dev/null | grep -v 'rurp_log_id' | grep -v '^[^:]*:\s*//' | grep -v 'Phase 9: deleted' | wc -l
       ```
       Expected: 0 (zero hits, accounting for `rurp_log_id` survivors, comment-only `//` lines, AND any deliberately-retained `// Phase 9: deleted ...` history-referencing comments inserted by Plan 01 / 03 / 04).

    2. PROGMEM exemption survey (informational — full enumeration will land in Plan 05's `09-MEASUREMENT.md`):
       ```
       cd /workspaces/firestarter_prom && grep -rn 'PROGMEM' firestarter/src firestarter/include 2>/dev/null | grep -v 'MAGIC_PREAMBLE\|CRC8_TABLE\|key_' | tee /tmp/ph9-progmem-survey.txt | wc -l
       ```
       Expected: a small number (`F(...)` literals from `_firestarter_emit_frame`, `hardware_operations.cpp` fw_get_version, and other Arduino-string call-sites). All hits MUST be either inline `F(...)` Arduino-macro use or json_parser keys — no remaining named-symbol PROGMEM strings that feed log functions.

    3. Dual AVR build (absolute-path `cd` to avoid cwd-drift; each subshell rooted at the firmware sub-repo):
       ```
       cd /workspaces/firestarter_prom/firestarter && pio run -e leonardo -t clean && pio run -e leonardo 2>&1 | grep '^Flash:'
       cd /workspaces/firestarter_prom/firestarter && pio run -e uno -t clean && pio run -e uno 2>&1 | grep '^Flash:'
       ```
       Expected: both report SUCCESS with a `Flash:` line. Record the Flash percentage + byte count for both. (Plan 05 will use the same numbers for the measurement artifact; the clean build here ensures Plan 05 measures from a deterministic baseline.)

    4. SC#3 host-guard regression — `firestarter_app/tests/test_fwguard.py`:
       ```
       cd /workspaces/firestarter_prom/firestarter_app && pytest tests/test_fwguard.py -v
       ```
       Expected: 4 PASS. No edits to test code are needed per 09-RESEARCH.md §"test_fwguard.py — already SC#3-complete".

    5. Host decoder regression (no Phase 9 changes should regress it):
       ```
       cd /workspaces/firestarter_prom/firestarter_app && pytest tests/test_decoder.py -q
       ```
       Expected: 25 PASS (unchanged from Phase 8 close).

    6. Native dispatch regression:
       ```
       cd /workspaces/firestarter_prom/firestarter && pio test -e native -f '*test_dispatch*' -f '*test_messages*'
       ```
       Expected: 22+ PASS. (test_dispatch may show pre-existing 2 ERRORs in test_flash_intel_vpp + test_eeprom28c_chip_id per 09-RESEARCH.md — those are pre-Phase-7 baseline noise, NOT regressions.)

    Record every command's output in `09-02-SUMMARY.md` under a `## Acceptance Gate Output` heading. If any gate fails, do NOT mark the plan complete; instead enumerate the failure in the SUMMARY and stop for operator review.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_prom &amp;&amp; [ "$(grep -rn 'send_ack\|rurp_log\b\|rurp_log_P\|_firestarter_log_\|LOG_OK_MSG\|log_info_const\|log_error_format\|log_warn\b\|debug_setup\|log_debug\b' firestarter/src firestarter/include firestarter/lib 2>/dev/null | grep -v 'rurp_log_id' | grep -v '^[^:]*:\s*//' | grep -v 'Phase 9: deleted' | wc -l)" = "0" ] &amp;&amp; cd /workspaces/firestarter_prom/firestarter &amp;&amp; pio run -e leonardo 2>&amp;1 | grep -q SUCCESS &amp;&amp; cd /workspaces/firestarter_prom/firestarter &amp;&amp; pio run -e uno 2>&amp;1 | grep -q SUCCESS &amp;&amp; cd /workspaces/firestarter_prom/firestarter_app &amp;&amp; pytest tests/test_fwguard.py tests/test_decoder.py -q 2>&amp;1 | tail -3 | grep -E 'passed' &amp;&amp; cd /workspaces/firestarter_prom/firestarter &amp;&amp; pio test -e native -f '*test_dispatch*' 2>&amp;1 | tail -3 | grep -qE '(PASSED|OK|22|23|24)'</automated>
  </verify>
  <acceptance_criteria>
    - LFW-03 grep gate returns 0 (excluding `rurp_log_id` survivors, comment-only `//` lines, AND any `// Phase 9: deleted ...` history-referencing comments — the `grep -v 'Phase 9: deleted'` exclusion is INTENTIONAL: Plan 01 / 03 / 04 may insert `// Phase 9: deleted send_ack_const(...) — see 09-CONTEXT.md D-02` style breadcrumb comments at converted call-sites for historical traceability; these comments are not legacy callers and must not trip the gate)
    - Both AVR builds report SUCCESS with a recorded Flash line
    - `pytest tests/test_fwguard.py` reports 4 PASS
    - `pytest tests/test_decoder.py` reports 25 PASS (unchanged from Phase 8 close)
    - `pio test -e native -f '*test_dispatch*'` reports 22+ PASS (pre-existing 2 ERRORs in unrelated suites are NOT regressions per 09-RESEARCH.md)
    - 09-02-SUMMARY.md records every gate output
  </acceptance_criteria>
  <done>
    - All five gates green
    - Plan 02 is acceptance-ready; Plan 05 (measurement) can run against this firmware tree without further changes
    - LFW-03 + LFW-04 + LFW-05 (firmware side, version bump) are satisfied; SC#3 (host-guard regression) is satisfied
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| firmware → host (serial wire) | The LFW-05 bootstrap `OK: FW: <version>` line crosses this boundary as text (the lone surviving non-id-frame emit). Wire shape changes from pre-D-01 `OK: <version>` to post-D-01 `OK: FW: <version>` — the literal `FW: ` substring is ADDED, not byte-identical. This is required by the host `_probe_port` `'FW:' in msg` substring test at `serial_comm.py:747-748`. |
| build system → committed firmware | Build-cache stale objects from the file-deletion operation could leave dangling references that pass `pio run` on a warm cache but fail on a cold checkout (Risk #7 from 09-RESEARCH.md). |
| host (Phase 9) ↔ firmware (pre-Phase-9) | After this plan ships `3.0.0-dev`, the host's `major < 3` refuse guard at `serial_comm.py:761` becomes actively load-bearing. Any operator pointing the new host at a pre-Phase-9 firmware sees `FirmwareOutdatedError` unless `FIRESTARTER_DEV_ALLOW_PRE_V12=1` is set. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-09-02-01 | Tampering | Host `_probe_port` substring test `'FW:' in msg` + regex `r"FW:\s*([\d.x]+)"` against the new inline-emit wire form | mitigate | Post-D-01 wire shape ADDS the literal `FW: ` substring to the bootstrap emit: was `OK: <FW_VERSION>` (e.g. `OK: 2.0.11-dev:uno`), becomes `OK: FW: <FW_VERSION>` (e.g. `OK: FW: 3.0.0-dev:uno`). This is INTENTIONAL — `FW_VERSION` is defined in `firestarter/include/firestarter.h:16` as `VERSION ":" RURP_BOARD_NAME` (a bare composed string), and the host parse at `serial_comm.py:747-748` requires the `FW:` substring to be present. Task 1 acceptance criterion explicitly requires the wire output contain the `OK: FW: ` literal. The 09-PATTERNS.md §"Pattern Assignment 1" "wire-format invariant" note + 09-RESEARCH.md §"Bench Verification Matrix Re-use" §"Tests invalidated" both lock the post-D-01 observable to `OK: FW: 3.0.0-dev:<board>, ...`. Plan 05 Task 2's bench step validates the post-D-01 wire shape end-to-end. |
| T-09-02-02 | Denial of Service | Protocol-version mismatch — pre-Phase-9 host crashing on a new firmware reply, or new host refusing all pre-Phase-9 firmware | mitigate | Already mitigated by Phase 6 LFW-05 host guard + Phase 6 Plan 04 `FIRESTARTER_DEV_ALLOW_PRE_V12` escape hatch. SC#3 regression test (`pytest tests/test_fwguard.py`) verifies the guard behavior post-bump. No code changes needed — the Phase 6 wiring becomes load-bearing. |
| T-09-02-03 | Denial of Service | Build-cache stale `.o` / `.d` files in `.pio/build/<env>/` linking against deleted symbols | mitigate | Task 5 prefixes the acceptance build with `pio run -t clean` per 09-RESEARCH.md §"Risks & Landmines #7". Cold-cache rebuilds prove the deletion is complete. Plan 05 measurement re-runs `clean` for the same reason. |
| T-09-02-04 | Tampering | `MSG_OK_FW_VERSION` (0x03) catalog entry abuse — a malicious peer could emit `id=0x03` as a binary frame to bypass the host's text-path FW-version guard | mitigate | KEEP the catalog entry with `wire_format = "text"` (Claude's Discretion, 09-CONTEXT.md). The host's WR-03 reject-id-frame guard at `serial_comm.py:398-410` then drops binary frames for `id=0x03` with a warning. Zero firmware cost (codegen emits a single `#define`; no PROGMEM string). Task 3 does NOT touch the catalog. |
| T-09-02-05 | Information Disclosure | Operator-side automation scripts grepping for `OK: ` empty-body literal from the dev_tools commands | accept | RESEARCH.md §"Risks & Landmines #4" grep-verified zero scripts depend on the empty body. Plan 01's conversion changes the visible body from `OK: ` to `OK: Ready` (an improvement). |
| T-09-02-06 | Elevation of Privilege | SERIAL_DEBUG re-enablement after Phase 9 — operator un-comments `-D SERIAL_DEBUG` in platformio.ini expecting `debug_setup()` / `log_debug()` to work | mitigate | Per 09-RESEARCH.md §"Risks & Landmines #11" the replacement is `LOG_DEBUG_ID_SUB*` shipped in Phase 8 Plan 07, routing debug emits through the main serial port via id-frames. Task 3 deletes the SERIAL_DEBUG infrastructure; the SERIAL_DEBUG flag still exists but is unused. Plan 05's measurement artifact will document this as part of SC#1's exemption survey. |
</threat_model>

<verification>
### Plan-level acceptance gate (run after all 5 tasks complete)

```bash
# 1. LFW-03 grep gate: zero legacy log surface remains (excluding rurp_log_id survivors, comment-only lines, and deliberate `Phase 9: deleted` history breadcrumbs)
[ "$(grep -rn 'send_ack\|rurp_log\b\|rurp_log_P\|_firestarter_log_\|LOG_OK_MSG\|log_info_const\|log_error_format\|log_warn\b\|debug_setup\|log_debug\b' firestarter/src firestarter/include firestarter/lib 2>/dev/null | grep -v 'rurp_log_id' | grep -v '^[^:]*:[[:space:]]*//' | grep -v 'Phase 9: deleted' | wc -l)" = "0" ] || { echo "FAIL: LFW-03 grep gate"; exit 1; }

# 2. logging.h / logging.c deleted
[ ! -f firestarter/include/logging.h ] || { echo "FAIL: logging.h still exists"; exit 1; }
[ ! -f firestarter/src/logging.c ] || { echo "FAIL: logging.c still exists"; exit 1; }

# 3. Zero #include "logging.h" anywhere
[ "$(grep -rln '#include "logging.h"' firestarter/src/ firestarter/include/ firestarter/lib/ 2>/dev/null | wc -l)" = "0" ] || { echo "FAIL: stale includes"; exit 1; }

# 4. Version bumped
grep -q '#define VERSION "3.0.0-dev"' firestarter/include/version.h || { echo "FAIL: version not bumped"; exit 1; }

# 5. Dual AVR cold build (absolute paths to avoid cwd-drift)
cd /workspaces/firestarter_prom/firestarter && pio run -e leonardo -t clean && pio run -e leonardo 2>&1 | grep -q SUCCESS || { echo "FAIL: leonardo build"; exit 1; }
cd /workspaces/firestarter_prom/firestarter && pio run -e uno -t clean && pio run -e uno 2>&1 | grep -q SUCCESS || { echo "FAIL: uno build"; exit 1; }

# 6. SC#3 host-guard regression
cd /workspaces/firestarter_prom/firestarter_app && pytest tests/test_fwguard.py -v 2>&1 | tail -5 | grep -q '4 passed' || { echo "FAIL: fwguard regression"; exit 1; }

# 7. Host decoder regression (no break)
cd /workspaces/firestarter_prom/firestarter_app && pytest tests/test_decoder.py -q 2>&1 | tail -3 | grep -q '25 passed' || { echo "FAIL: decoder regression"; exit 1; }

# 8. Native dispatch regression (no break)
cd /workspaces/firestarter_prom/firestarter && pio test -e native -f '*test_dispatch*' 2>&1 | tail -3 | grep -qE '(PASSED|22|23|24)' || { echo "FAIL: native dispatch"; exit 1; }

echo "PLAN 02 GREEN"
```
</verification>

<success_criteria>
- LFW-03 satisfied: zero legacy log surface (`send_ack`, `send_ack_const`, `rurp_log`, `rurp_log_P`, `_firestarter_log_*`, `LOG_OK_MSG`, `log_info_const`, `log_error_format`, `log_warn`, `debug_setup`, `log_debug`) anywhere in `firestarter/src/` + `firestarter/include/` + `firestarter/lib/` (excluding `rurp_log_id` survivors, comment-only lines, and `// Phase 9: deleted ...` history breadcrumbs)
- LFW-04 (firmware side) satisfied: `logging.h` and `logging.c` deleted; `LOG_OK_MSG` PROGMEM string gone; only inline `F("OK: FW: ")` Arduino-macro use remains as a non-named-symbol PROGMEM literal at `fw_get_version()` (SC#1 exemption per CONTEXT.md D-01)
- LFW-05 (firmware side) satisfied: firmware reports `3.0.0-dev` via the inline `OK: FW: 3.0.0-dev:<board>` line; host major&lt;3 refuse guard at `serial_comm.py:761` is now load-bearing against pre-Phase-9 firmware
- SC#3 satisfied: `pytest tests/test_fwguard.py` reports 4 PASS unchanged
- `pio run -e uno` and `pio run -e leonardo` both report SUCCESS on a cold-cache rebuild
- All grep gates from `<verification>` return ZERO hits
</success_criteria>

<output>
After completion, create `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-02-SUMMARY.md` recording:
- Files deleted: `firestarter/include/logging.h`, `firestarter/src/logging.c`
- Files modified: count + list (per `files_modified` frontmatter)
- Symbols deleted: `send_ack`, `send_ack_const`, `rurp_log`, `rurp_log_P`, `_firestarter_log_ram`, `_firestarter_log_progmem`, `LOG_OK_MSG`, `debug_setup`, `log_debug`, `SoftwareSerial debugSerial`, `RX_DEBUG`, `TX_DEBUG`
- Inline LFW-05 bootstrap shape: the exact 3 `SERIAL_PORT.*` calls + wire-format note (post-D-01 emit `OK: FW: 3.0.0-dev:<board>` ADDS the `FW: ` substring vs pre-D-01 `OK: <version>` — intentional, required by host `_probe_port` at `serial_comm.py:747-748`)
- Version bump: `2.0.11-dev` → `3.0.0-dev`
- Dual AVR Flash numbers (informational; Plan 05 owns the formal measurement)
- All 8 acceptance-gate command outputs verbatim under `## Acceptance Gate Output`
</output>
