# Phase 9: Delete Old Log Macros + Measure Flash Savings — Research

**Researched:** 2026-05-19
**Domain:** Final-stage firmware cleanup (legacy log infra deletion) + flash measurement + firmware version bump
**Confidence:** HIGH (every claim verified against the live source tree)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions (D-01..D-10)

- **D-01 — Inline LFW-05 FW-version emit.** Replace `send_ack_const(FW_VERSION)` at `firestarter/src/hardware_operations.cpp:86` with the literal three-liner:
  ```cpp
  SERIAL_PORT.print(F("OK: FW: "));
  SERIAL_PORT.println(FW_VERSION);
  SERIAL_PORT.flush();
  ```
  Must produce a byte-identical line on the wire. The `F(...)` literal is exempt from SC#1 (same category as `MAGIC_PREAMBLE` / `CRC8_TABLE`).
- **D-02 — Delete entire legacy macro tower.** `send_ack`, `send_ack_const`, `rurp_log`, `rurp_log_P`, `_firestarter_log_ram`, `_firestarter_log_progmem`, `LOG_OK_MSG`. Possibly entire `logging.h` file (see D-08 Claude's discretion).
- **D-03 — `host_stubs.cpp` (native tests) cleanup.** Drop dead `LOG_*_MSG` PROGMEM externs and dead `rurp_log` / `rurp_log_P` no-op stubs from the shared include. `pio test -e native` must stay green.
- **D-04 — Reuse `MSG_OK_READY` (0x01) for `dev_tools.cpp` `send_ack("")` conversion.** Two sites at `dev_tools.cpp:108` (inside `dt_set_registers`) and `dev_tools.cpp:154` (inside `dt_set_address`) → `LOG_OK_ID(MSG_OK_READY)`. NOTE: CONTEXT.md names the first function `dt_dump_register` — actual source name is `dt_set_registers`; line number is correct.
- **D-05 — Deletion order.** D-04 conversions are precondition for D-02 deletions (must remove every `send_ack` caller before deleting the macro).
- **D-06 — `VERSION = "3.0.0-dev"`.** Bump `firestarter/include/version.h:11`. `-dev` suffix stripped on tag in Phase 10.
- **D-07 — SC#3 regression test.** Already covered by existing `firestarter_app/tests/test_fwguard.py` suite (4 tests, all green on `aa75c05`). No new test infrastructure required.
- **D-08 — `09-MEASUREMENT.md` carries BOTH deltas.** Phase 8 → Phase 9 incremental + v1.1 (98.7%) → Phase 9 milestone close. Single source of truth for Phase 10 DOC-02.
- **D-09 — Extend the anchor table in `08-MEASUREMENT.md` (lines 308–319) with a Phase 9 row.** Same 5-column layout.
- **D-10 — Bench verification re-runs Phase 8's chipless wire-protocol matrix post-`3.0.0-dev` bump.** Both Uno + Leonardo (per project memory `feedback_always-mirror-uno-leonardo-tests`).

### Claude's Discretion (proposed answers — confirmed by this research)

- **`MSG_OK_FW_VERSION` (0x03) catalog entry fate.** **KEEP** with `wire_format = "text"`. Confirmed load-bearing on host (WR-03 guard at `serial_comm.py:404-410`). Zero firmware cost (codegen emits only a `#define`; no PROGMEM string).
- **`FIRESTARTER_DEV_ALLOW_PRE_V12` env-var fate.** **KEEP, rewrite comment.** The comment at `serial_comm.py:752-755` says "until then [Phase 9 firmware bump]…" — drop the "until then" framing; the mechanism stays for regression-testing old firmware against new hosts.
- **`debug_setup` / `log_debug` SERIAL_DEBUG functions.** **DELETE both** — but with care. One non-SERIAL_DEBUG caller of `debug_setup()` exists at `firestarter.cpp:39` BUT it is wrapped in `#ifdef SERIAL_DEBUG` (line 38). Verified safe to delete the no-op fallback macro AND the function (and the `#ifdef SERIAL_DEBUG` block in `firestarter.cpp:setup()`).
- **`logging.h` file fate.** **DELETE OUTRIGHT.** Confirmed nothing remains after macro deletion. 20 `#include "logging.h"` sites identified across firmware (production + test); ALL become removable.
- **`logging.c` file fate.** **DELETE OUTRIGHT.** Only contained `LOG_OK_MSG`. Production builds (`env:uno`, `env:leonardo`) pick it up via default pattern (no `src_filter` set); native build's `src_filter = +<proms/> +<boards/rurp_serial_utils.cpp>` never included it. Deleting the file changes no build config.
- **Commit cadence.** 4-wave recommendation per CONTEXT.md; planner may differ.
- **Phase 8 SC#2/SC#3 carry-over.** Bundle into Phase 9 bench step (both boards required for D-10 anyway).

### Deferred Ideas (OUT OF SCOPE)

- Strip `-dev` → `3.0.0` (Phase 10 release-tag op).
- Phase 10 milestone-close documentation (DOC-02).
- v1.1 leftover items (FM1608 hw bug, WARNING-4, v1.1 DOC-01).
- Future host-side `FIRESTARTER_DEV_ALLOW_PRE_V12` cleanup.
- Future `MSG_OK_FW_VERSION` (0x03) catalog deletion.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID       | Description (from REQUIREMENTS.md)                                                                                          | Research Support                                                                                                                                                                                                                                                                                                                                  |
|----------|-----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| LFW-03   | All firmware log call-sites that today use OK / INIT / MAIN / END / INFO / WARN / ERROR PROGMEM strings are converted.       | Already 100% complete through Phase 8. The Phase 8 "Catalog Orphan Audit" enumerates every emit-site as USED via `LOG_*_ID` macros. Phase 9 leaves these conversions untouched.                                                                                                                                                                  |
| LFW-04   | After conversion, firmware tree contains zero PROGMEM string literals that exist only to be passed to a log function.       | Verified: after Phase 9 deletes `LOG_OK_MSG`, the only remaining PROGMEM strings in `firestarter/src/` + `include/` + `lib/` are: `MAGIC_PREAMBLE` (4-byte frame infra), `CRC8_TABLE` (256-byte frame infra), 9 json_parser key strings + 1 `key_parsers[]` table (parser infra, non-log), and inline `F(...)` literals (frame infra, no symbol).  |
| LMIG-04  | Delete + measure. Old log macros + PROGMEM strings removed; flash-savings number recorded; Leonardo below 90% with headroom. | Phase 8 close already at 85.6% Leonardo; Phase 9 inherits this and is expected to drop further by ~50–300 B (LOG_OK_MSG = 3 B + `_firestarter_log_*` helpers ~100–200 B + macro expansion at deleted call-sites). All measurement infrastructure verified (`pio run -e leonardo` / `pio run -e uno` report exact byte + percentage usage). |
</phase_requirements>

---

## Phase 9 Research Summary

Phase 9 is a small-surface, high-precision cleanup phase. CONTEXT.md has locked decisions D-01..D-10 plus seven Claude's-Discretion items; this research validates each of them against the live source tree (`firestarter@2520575`, `firestarter_app@aa75c05` — both at Phase 8 close). **No architectural alternatives were investigated** — the v1.2 logging migration path is in its final cleanup phase.

The deletion inventory is **clean**: every symbol CONTEXT.md flags for removal has exactly the callers CONTEXT.md anticipated, plus one minor discrepancy that does not change the plan (CONTEXT.md refers to `dt_dump_register` at `dev_tools.cpp:108`; the actual function name there is `dt_set_registers` — the file/line are correct, the function name is a CONTEXT.md typo). No BLOCKER-class surprises were found. The catalog entries `MSG_OK_FW_VERSION` (0x03) and `MSG_OK_READY` (0x01) behave as CONTEXT.md predicts: the former is load-bearing on the host's WR-03 guard at zero firmware cost; the latter is a context-free ack token whose D-04 reuse for `dev_tools` is operationally safe.

**Primary recommendation:** proceed with the planner exactly along the CONTEXT.md D-01..D-10 path. The four-wave commit cadence in CONTEXT.md "Claude's Discretion" is sound. The single watch-item is the `firestarter.cpp:39` `debug_setup()` call wrapped in `#ifdef SERIAL_DEBUG` — that block, along with the SERIAL_DEBUG-only `log_debug` / `debug_setup` function bodies in `uno_rurp_shield.cpp`, must come out atomically with the macro deletion (both function definitions are gated on `SERIAL_DEBUG`; the production no-op fallback macros in `logging.h:39-40` go too).

---

## Deletion Inventory

Per-symbol grep of `firestarter/src/`, `firestarter/include/`, `firestarter/lib/` (production tree) plus `firestarter/test/` (native test tree) for every symbol CONTEXT.md lists as "to delete."

### `send_ack(msg)` — macro

| Location | Role | Action |
|---|---|---|
| `firestarter/include/logging.h:25-26` | Macro definition: `rurp_log(LOG_OK_MSG, msg)` | DELETE (with rest of `logging.h`) |
| `firestarter/src/dev_tools.cpp:108` (`dt_set_registers`) | Caller: `send_ack("")` | CONVERT to `LOG_OK_ID(MSG_OK_READY)` (D-04 / W1) |
| `firestarter/src/dev_tools.cpp:154` (`dt_set_address`) | Caller: `send_ack("")` | CONVERT to `LOG_OK_ID(MSG_OK_READY)` (D-04 / W1) |

**Comment block reference** at `logging.h:24`: `"send_ack called from dev_tools.cpp, send_ack_const from hardware_operations.cpp"` — informational, vanishes when `logging.h` is deleted.

**No other callers anywhere in firmware.** CONFIRMED clean.

### `send_ack_const(msg)` — macro

| Location | Role | Action |
|---|---|---|
| `firestarter/include/logging.h:28-29` | Macro definition: `rurp_log_P(LOG_OK_MSG, PSTR(msg))` | DELETE (with rest of `logging.h`) |
| `firestarter/src/hardware_operations.cpp:86` (`fw_get_version`) | Caller: `send_ack_const(FW_VERSION)` | REPLACE with inline D-01 three-liner |

**No other callers.** CONFIRMED clean.

### `rurp_log(PGM_P type, const char* msg)` — function

| Location | Role | Action |
|---|---|---|
| `firestarter/include/rurp_shield.h:127` | Declaration | DELETE |
| `firestarter/src/boards/rurp_serial_utils.cpp:243-245` | Weak default definition (`__attribute__((weak))`) | DELETE |
| `firestarter/src/boards/uno_rurp_shield.cpp:77-82` | Uno strong override | DELETE |
| `firestarter/test/native/avr/_shared/host_stubs_common.inc:59-62` | Host no-op stub (`extern "C"`) | DELETE (D-03) |
| `firestarter/include/logging.h:26` (inside `send_ack`) | Macro expansion site | DELETED transitively |

**No `rurp_log` callers in `.cpp` / `.c` files** after `send_ack`/`send_ack_const` macros vanish. Phase 8 already eliminated every other call-site. CONFIRMED clean.

### `rurp_log_P(PGM_P type, PGM_P msg)` — function

| Location | Role | Action |
|---|---|---|
| `firestarter/include/rurp_shield.h:128` | Declaration | DELETE |
| `firestarter/src/boards/rurp_serial_utils.cpp:246-248` | Weak default definition | DELETE |
| `firestarter/src/boards/uno_rurp_shield.cpp:84-88` | Uno strong override | DELETE |
| `firestarter/test/native/avr/_shared/host_stubs_common.inc:64-67` | Host no-op stub | DELETE (D-03) |
| `firestarter/include/logging.h:29` (inside `send_ack_const`) | Macro expansion site | DELETED transitively |

**No `rurp_log_P` direct callers outside the macro.** CONFIRMED clean.

### `_firestarter_log_ram(PGM_P, const char*)` — helper

| Location | Role | Action |
|---|---|---|
| `firestarter/include/rurp_serial_utils.h:15` | Declaration | DELETE |
| `firestarter/src/boards/rurp_serial_utils.cpp:12-17` | Definition | DELETE |
| `firestarter/src/boards/rurp_serial_utils.cpp:244` | Called from `rurp_log` weak default | DELETED transitively |
| `firestarter/src/boards/uno_rurp_shield.cpp:80` | Called from `rurp_log` Uno strong override | DELETED transitively |

**CONFIRMED clean** — only callers are the `rurp_log` functions that are themselves being deleted.

### `_firestarter_log_progmem(PGM_P, PGM_P)` — helper

| Location | Role | Action |
|---|---|---|
| `firestarter/include/rurp_serial_utils.h:15` | Declaration | DELETE |
| `firestarter/src/boards/rurp_serial_utils.cpp:20-25` | Definition | DELETE |
| `firestarter/src/boards/rurp_serial_utils.cpp:247` | Called from `rurp_log_P` weak default | DELETED transitively |
| `firestarter/src/boards/uno_rurp_shield.cpp:86` | Called from `rurp_log_P` Uno strong override | DELETED transitively |

**CONFIRMED clean** — only callers are the `rurp_log_P` functions that are themselves being deleted.

### `LOG_OK_MSG` — PROGMEM string

| Location | Role | Action |
|---|---|---|
| `firestarter/include/logging.h:22` | `extern const char LOG_OK_MSG[] PROGMEM;` | DELETE (with `logging.h`) |
| `firestarter/src/logging.c:9` | `const char LOG_OK_MSG[] PROGMEM = "OK";` | DELETE (with `logging.c`) |
| `firestarter/include/logging.h:26` (inside `send_ack`) | Macro expansion site | DELETED transitively |
| `firestarter/include/logging.h:29` (inside `send_ack_const`) | Macro expansion site | DELETED transitively |
| `firestarter/test/native/avr/_shared/host_stubs_common.inc:46` | Host PROGMEM stub | DELETE (D-03) |

**CONFIRMED clean.** Note: lines 47-53 of the same `host_stubs_common.inc` define 7 other dead PROGMEM stubs (`LOG_INIT_DONE_MSG`, `LOG_MAIN_DONE_MSG`, `LOG_END_DONE_MSG`, `LOG_INFO_MSG`, `LOG_DATA_MSG`, `LOG_WARN_MSG`, `LOG_ERROR_MSG`) that Phase 8 already eliminated from production but left in the shared host-stub for now. Phase 9 should drop all 8 stubs together (D-03 follow-on).

### `debug_setup()` — function

| Location | Role | Action |
|---|---|---|
| `firestarter/include/logging.h:36` (under `#ifdef SERIAL_DEBUG`) | Declaration | DELETE |
| `firestarter/include/logging.h:39` (under `#else`) | Empty-macro no-op fallback | DELETE |
| `firestarter/src/boards/uno_rurp_shield.cpp:148-150` (under `#ifdef SERIAL_DEBUG`) | Definition: `debugSerial.begin(57600);` | DELETE |
| `firestarter/src/boards/leonardo_rurp_shield.cpp:145` (under `#ifdef SERIAL_DEBUG`) | Empty `void debug_setup() {}` | DELETE |
| `firestarter/src/firestarter.cpp:39` (inside `#ifdef SERIAL_DEBUG` block at lines 38-40 of `setup()`) | Caller: `debug_setup();` | DELETE entire `#ifdef SERIAL_DEBUG` block at firestarter.cpp:38-40 |

**One caller** at `firestarter.cpp:39` — already gated by `#ifdef SERIAL_DEBUG` (only compiled when the build flag is set, which it currently is not in `platformio.ini`). Safe to delete the entire `#ifdef SERIAL_DEBUG` / `debug_setup();` / `#endif` block in `setup()`. CONFIRMED — CONTEXT.md's "DELETE both" stands.

### `log_debug(type, msg)` — function

| Location | Role | Action |
|---|---|---|
| `firestarter/include/logging.h:37` (under `#ifdef SERIAL_DEBUG`) | Declaration | DELETE |
| `firestarter/include/logging.h:40` (under `#else`) | Empty-macro no-op fallback | DELETE |
| `firestarter/src/boards/uno_rurp_shield.cpp:152-160` (under `#ifdef SERIAL_DEBUG`) | Definition (writes to SoftwareSerial) | DELETE |
| `firestarter/src/boards/uno_rurp_shield.cpp:78` (inside `rurp_log` Uno override) | Caller | DELETED transitively (the whole `rurp_log` body goes) |

**No callers outside `rurp_log` Uno strong override.** Once `rurp_log` is deleted, `log_debug` has zero callers. CONFIRMED — D-08 Claude's discretion "DELETE both" is correct.

### `log_info_const` / `log_error_format` / `log_warn` / `log_info_format` / `log_warn_format` — macro family

| Location | Status |
|---|---|
| All instances | ALREADY DELETED (Phase 8 housekeeping pass per `08-MEASUREMENT.md` §"Dead Symbol Deletion") |

**Empty grep**. CONFIRMED: zero remaining references in `firestarter/src/`, `firestarter/include/`, `firestarter/lib/`. The CONTEXT.md mention of these macros being "deleted in Phase 9" is technically inaccurate — they are already gone. SC#2 grep gate is already passing for these specifically. The Phase 9 deletion targets are the surviving macros (`send_ack`, `send_ack_const`) and underlying functions.

### `LOG_*_MSG` PROGMEM string family (other variants)

| Symbol | Where (post-Phase-8) | Action |
|---|---|---|
| `LOG_OK_MSG` | logging.c:9 + logging.h:22 + host_stubs_common.inc:46 | DELETE (Phase 9) |
| `LOG_INIT_DONE_MSG`, `LOG_MAIN_DONE_MSG`, `LOG_END_DONE_MSG`, `LOG_INFO_MSG`, `LOG_DATA_MSG`, `LOG_WARN_MSG`, `LOG_ERROR_MSG` | Already deleted from logging.h + logging.c by Phase 8. Remain only in `host_stubs_common.inc:47-53` as dead host-link-only externs. | DELETE host_stubs_common.inc lines 47-53 (D-03 follow-on) |

### `dt_dump_register` (CONTEXT.md typo audit)

CONTEXT.md D-04 names `dev_tools.cpp:108` as `dt_dump_register`. **No such function exists.** The actual function bodies in `dev_tools.cpp` are:
- `dt_decode_register` (helper at line 23)
- `dt_set_registers` (line 72, contains `send_ack("")` at line 108)
- `dt_set_address` (line 130, contains `send_ack("")` at line 154)

CONTEXT.md's line numbers + planned change (convert to `LOG_OK_ID(MSG_OK_READY)`) are correct. Only the function-name reference is wrong; the planner should write `dt_set_registers` and `dt_set_address` in the plan.

### Summary

| Status | Count | Symbols |
|---|---|---|
| Anticipated by CONTEXT.md, callers match | 8 | `send_ack`, `send_ack_const`, `rurp_log`, `rurp_log_P`, `_firestarter_log_ram`, `_firestarter_log_progmem`, `LOG_OK_MSG`, `log_debug` |
| Anticipated by CONTEXT.md, caller surface narrower than CONTEXT.md implied (better, not worse) | 1 | `debug_setup` (only caller is `#ifdef SERIAL_DEBUG`-gated, fully safe to delete) |
| Already deleted (CONTEXT.md is slightly out-of-date — Phase 8 already cleared) | 5 | `log_info_const`, `log_error_format`, `log_warn`, `log_info_format`, `log_warn_format` |
| Surprises / BLOCKERS | **0** | — |
| Doc-only confusion (function name typo in CONTEXT.md) | 1 | `dt_dump_register` → actual: `dt_set_registers` |

**No BLOCKERS.** The deletion target list is complete and the planner can proceed.

---

## File-Fate Audits

### `firestarter/include/logging.h` — DELETE the file

**Post-deletion content audit:**
1. `#include <avr/pgmspace.h>` + `#include <Arduino.h>` (line 11, 13) — re-includes, not strictly needed (downstream files include these directly).
2. `#include "firestarter.h"` + `#include "rurp_shield.h"` (line 15, 16) — same.
3. `extern const char LOG_OK_MSG[] PROGMEM;` (line 22) — DELETED.
4. `send_ack` + `send_ack_const` macros (lines 25-29) — DELETED.
5. `#ifdef SERIAL_DEBUG` block (lines 31-41) declaring `debug_setup()` + `log_debug()` — DELETED.

**Nothing of substance remains.** File can be deleted outright.

**Includer enumeration** (20 sites; every one becomes either remove-include OR migrate-to-`logging_id.h`):

| Includer (path) | Currently uses (post-Phase 8) | Action |
|---|---|---|
| `firestarter/include/operation_utils.h:19` | nothing from logging.h | DROP include |
| `firestarter/include/rurp_hw_rev_utils.h:10` | nothing from logging.h | DROP include |
| `firestarter/include/rurp_serial_utils.h:8` | nothing from logging.h | DROP include |
| `firestarter/src/boards/leonardo_rurp_shield.cpp:13` | `debug_setup` (SERIAL_DEBUG only) | DROP include |
| `firestarter/src/boards/uno_rurp_shield.cpp:13` | `debug_setup`, `log_debug`, `_firestarter_log_ram`, `_firestarter_log_progmem`, `rurp_log`, `rurp_log_P` (SERIAL_DEBUG only) | DROP include (entire SERIAL_DEBUG body and rurp_log/rurp_log_P override functions are themselves being deleted) |
| `firestarter/src/dev_tools.cpp:14` | `send_ack` | DROP include (replaced by `logging_id.h` which is already included at line 15) |
| `firestarter/src/eprom_operations.cpp:11` | nothing post-Phase-8 | DROP include |
| `firestarter/src/firestarter.cpp:16` | `debug_setup` (SERIAL_DEBUG only) | DROP include (caller block also gone) |
| `firestarter/src/hardware_operations.cpp:7` | `send_ack_const` | DROP include (replaced by inline `F(...)` literal + already includes `logging_id.h` at line 8) |
| `firestarter/src/json_parser.c:12` | nothing post-Phase-8 | DROP include |
| `firestarter/src/logging.c:1` | DELETED with the .c file | N/A |
| `firestarter/src/operation_utils.cpp:14` | nothing post-Phase-8 | DROP include |
| `firestarter/src/proms/eeprom_28c.cpp:14` | nothing post-Phase-8 | DROP include |
| `firestarter/src/proms/eprom.cpp:13` | nothing post-Phase-8 | DROP include |
| `firestarter/src/proms/flash_intel.cpp:13` | nothing post-Phase-8 | DROP include |
| `firestarter/src/proms/flash_type_3.cpp:14` | nothing post-Phase-8 | DROP include |
| `firestarter/src/proms/flash_type_4.cpp:14` | nothing post-Phase-8 | DROP include |
| `firestarter/src/proms/flash_utils.cpp:12` | nothing post-Phase-8 | DROP include |
| `firestarter/src/proms/memory.cpp:18` | nothing post-Phase-8 | DROP include |
| `firestarter/src/proms/sram.cpp:12` | nothing post-Phase-8 | DROP include |

**Verification path:** after deleting `logging.h` and stripping all 20 includes, `pio run -e uno` and `pio run -e leonardo` must build clean. Any compile error means a missed symbol reference; planner runs the build to verify.

**Recommendation:** D-08 Claude's discretion to DELETE the file is CONFIRMED. Total of 20 include lines to remove plus the file itself.

### `firestarter/src/logging.c` — DELETE the file

**Post-deletion content audit:** the file contains only:
- `#include "logging.h"` (deleted with logging.h)
- `#include "firestarter.h"` (gone with the file)
- `const char LOG_OK_MSG[] PROGMEM = "OK";` (the only substantive symbol — deleted per D-02)

**Nothing remains.** File can be deleted outright.

**Build-system impact verification:**

| Build env | Includes logging.c? | After deletion |
|---|---|---|
| `[env:uno]` | YES (default pattern picks up all `src/*.c`) | No-op — file simply isn't there to compile |
| `[env:leonardo]` | YES (same) | No-op |
| `[env:native]` | NO (`src_filter = +<proms/> +<boards/rurp_serial_utils.cpp>` — positive-only, excludes everything else by default) | No change — already excluded |

**Important nuance:** the comment in `platformio.ini` (lines 55-65) mentions `src/logging.c` as "excluded" in the context of explaining what the test stubs replace. The actual `src_filter` directive is **positive-only inclusion**, not an exclusion list. Deleting `logging.c` requires **no change** to `platformio.ini`. CONTEXT.md's claim ("`platformio.ini` `src_filter` for `[env:native]` already excludes `src/logging.c`; production build picks it up automatically via the default build pattern and will not miss the removed source file") is correct in outcome but slightly misleading in mechanism — confirmed safe to delete.

**Recommendation:** D-08 Claude's discretion to DELETE the file is CONFIRMED. Zero `platformio.ini` changes required.

### `firestarter/test/native/avr/_shared/host_stubs_common.inc` — TRIM the file

This file (`.inc`, included from 4 sibling `host_stubs.cpp` files) is the **single point of cleanup** for D-03. The 4 `host_stubs.cpp` files (test_dispatch, test_messages, test_flash_intel_vpp, test_eeprom28c_chip_id) all `#include "../_shared/host_stubs_common.inc"` and do not duplicate the symbols.

**Exact diff required** (lines 45-67 of `host_stubs_common.inc`):

```diff
- /* PROGMEM log-tag strings — defined in src/logging.c on AVR; replicated here
-  * so the [env:native] link finds them. The PSTR() macro in the pgmspace stub
-  * is a no-op, so these are plain const char[] in the host binary. */
- extern "C" {
- const char LOG_OK_MSG[] PROGMEM = "OK";
- const char LOG_INIT_DONE_MSG[] PROGMEM = "INIT";
- const char LOG_MAIN_DONE_MSG[] PROGMEM = "MAIN";
- const char LOG_END_DONE_MSG[] PROGMEM = "END";
- const char LOG_INFO_MSG[] PROGMEM = "INFO";
- const char LOG_DATA_MSG[] PROGMEM = "DATA";
- const char LOG_WARN_MSG[] PROGMEM = "WARN";
- const char LOG_ERROR_MSG[] PROGMEM = "ERROR";
- }
-
- /* rurp_log* — no-op on host. The dispatch tests never read serial output;
-  * test_messages exercises rurp_log_id (binary frame path) which does not
-  * route through these text-frame helpers. */
- extern "C" void rurp_log(PGM_P type, const char* msg) {
-     (void)type;
-     (void)msg;
- }
-
- extern "C" void rurp_log_P(PGM_P type, PGM_P msg) {
-     (void)type;
-     (void)msg;
- }
```

**Verification path:** after the diff, `pio test -e native` must still pass all 22+ test cases (test_dispatch + test_messages currently passing; test_flash_intel_vpp + test_eeprom28c_chip_id are pre-existing ERRORs from before Phase 7 — not regressions).

Additionally, check the per-suite `host_stubs.cpp` files — none of them currently define any `LOG_*_MSG` or `rurp_log` symbols themselves (verified by reading all four; they are pure pass-through includes plus a few mock state extensions in `test_flash_intel_vpp`). No per-suite changes required.

**Note on the `avr/pgmspace.h` shim files** (one per test directory, 4 total) — these contain comment references to `rurp_log` / `rurp_log_P` (line 27-28 of each) describing why `PGM_P` is needed. Those are pure comments; no code change required. The `PGM_P` typedef itself is still needed by `rurp_shield.h` even after rurp_log/rurp_log_P go (the type is in scope for other AVR macros), so leave the shim files alone.

---

## Catalog Entry Status

### `MSG_OK_READY` (0x01) — KEEP, reuse for `dev_tools` conversions

**Catalog entry** (`tools/catalog/messages.toml:33-39`):
```toml
[[messages]]
id          = 0x01
name        = "MSG_OK_READY"
severity    = "OK"
format      = "Ready"
params      = []
wire_format = "id_frame"
```

**Existing emit-site:** `firestarter/src/hardware_operations.cpp:42` (inside `hw_read_voltage` state 0 → state 1 transition, after voltage-stabilization delay).

**Host consumers:** Only one — the generic catalog decode path in `serial_comm.py:380-463` (`_decode_id_frame`). It:
1. Looks up the catalog entry by ID.
2. Verifies `wire_format == "id_frame"` (WR-03 guard — passes for MSG_OK_READY).
3. Decodes zero params (empty `params` list).
4. Renders the format string `"Ready"`.
5. Emits `LogMessage(severity="OK", text="Ready", id=0x01, payload=None)`.

**No code path assumes single emit-site.** `expect_ack()` (`serial_comm.py:609-621`) just checks `response.type == "OK"` and returns the message body. Zero context-sensitivity.

**D-04 reuse impact on `dev_tools` flow:**
- BEFORE: firmware emits `OK: ` (empty body via `send_ack("")` → text path). Host's `expect_ack()` returns `(True, "")`.
- AFTER: firmware emits ID frame 0x01 → host catalog decodes → host renders `OK: Ready`. `expect_ack()` returns `(True, "Ready")`.

**Host call sites that call `expect_ack()` after the dev_tools commands:**
- `firestarter_app/firestarter/eprom_operations.py:513` — `is_ok, _ = self.comm.expect_ack()` (the second return value is discarded → no script depends on body content).
- No other host code path inspects the body of the dev_tools ACK.

**CONFIRMED: D-04 reuse is operationally clean.** The visible operator log line changes from `OK: ` to `OK: Ready` — arguably an improvement (the empty body was a known eyesore). No sub_id discriminator or new catalog entry needed.

### `MSG_OK_FW_VERSION` (0x03) — KEEP catalog entry post-D-01

**Catalog entry** (`tools/catalog/messages.toml:54-60`):
```toml
[[messages]]
id          = 0x03
name        = "MSG_OK_FW_VERSION"
severity    = "OK"
format      = "FW: {0}"
params      = []
wire_format = "text"
```

**After D-01:** Firmware NO LONGER emits id=0x03 as a real frame. The replacement is an inline `F("OK: FW: ")` literal printed via `SERIAL_PORT.print/println`. The text line travels on the wire as it did before D-01 (byte-identical).

**Codegen impact** (`tools/catalog/codegen.py:274-285` + line 615):
- `wire_format = "text"` entries are emitted in `firestarter/include/messages.h` as a `#define` constant (verified at `messages.h:41`: `#define MSG_OK_FW_VERSION 0x03`).
- They are emitted in `firestarter_app/firestarter/messages.py` as a `MessageDef(... wire_format="text" ...)` entry in the `CATALOG` dict (verified at `messages.py:135`).
- **No PROGMEM string is generated by codegen for `MSG_OK_FW_VERSION`** — the format string `"FW: {0}"` lives only in host `messages.py`. Firmware cost of keeping this catalog entry is exactly **1 preprocessor `#define`** (zero runtime/Flash impact).

**Why the entry is load-bearing post-D-01 — WR-03 guard verification:**

The host's `_decode_id_frame` (`serial_comm.py:380-463`) processes every incoming binary frame:
1. Reads magic preamble (4 bytes) + length + body + CRC + 0x0A.
2. Looks up `entry = CATALOG.get(msg_id)`.
3. **WR-03 reject** at lines 404-410: `if entry.wire_format != "id_frame": logger.warning(...); return None`.

If a misbehaving or malicious peer emits `id=0x03` as a binary frame (valid CRC, valid preamble), the catalog entry's `wire_format="text"` causes the host to **drop the frame with a warning** and continue. Without the catalog entry, `CATALOG.get(0x03)` returns `None`, triggering the earlier "unknown ID" warning instead — which is a weaker protection because the host's pre-v1.2 firmware guard at `_probe_port` (which uses the TEXT path) could conceivably be bypassed if an attacker constructed a valid binary frame with `id=0x03` and a payload that rendered as `"FW: 3.0.0"` via the catalog format string. The defense is exactly:
- **With entry, `wire_format="text"`:** binary frame for 0x03 is rejected → text-path FW-version guard sees nothing → either real FW-version arrives via text (legit) or timeout (defense holds).
- **Without entry:** binary frame for 0x03 yields "Unknown ID" warning → text-path FW-version guard sees nothing → same defense, BUT the next firmware update that adds an `id=0x03` for a different purpose would silently bypass the guard. Defense-in-depth weaker.

**Cost-benefit:** 1 firmware `#define` (zero Flash) + 1 host catalog entry vs. removing an active reject-path defense. **KEEP.**

**Recommendation:** D-08 Claude's discretion to KEEP `MSG_OK_FW_VERSION` is CONFIRMED. Zero changes to the catalog file or codegen required in Phase 9.

---

## Host-side Surface

### `FIRESTARTER_DEV_ALLOW_PRE_V12` — KEEP, update comment wording

**Current code** (`firestarter_app/firestarter/serial_comm.py:752-770`):
```python
# Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2
# firmware. The firmware bumps to major=3 in
# Phase 9; until then, bench scripts use
# FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass.
try:
    major = int(current_version.split(".")[0])
except (ValueError, IndexError):
    major = 0
if (
    major < 3
    and os.environ.get("FIRESTARTER_DEV_ALLOW_PRE_V12") != "1"
):
    raise FirmwareOutdatedError(
        f"Firmware version {current_version} is pre-v1.2 (text-format logging). "
        f"This host expects v1.2+ firmware emitting ID-encoded log frames. "
        f"Please upgrade the firmware to v3.0.0 or later using 'firestarter fw --install'. "
        ...
    )
```

**Post-Phase-9 semantic:** the env var lets a developer point a current (Phase-9+) host at a pre-Phase-9 firmware build (any v2.x firmware) for regression testing. The "until then [Phase 9 firmware bump]" framing in the comment is wrong after Phase 9 ships — the firmware HAS bumped.

**Exact lines to update** (`serial_comm.py:752-755`):

```diff
- # Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2
- # firmware. The firmware bumps to major=3 in
- # Phase 9; until then, bench scripts use
- # FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass.
+ # Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2 firmware. The firmware bumped
+ # to major=3 in Phase 9. Set FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass when
+ # bench-testing a current host against a historical (v2.x) firmware build.
```

**Recommendation:** D-08 Claude's discretion to KEEP + rewrite comment is CONFIRMED. The mechanism stays exactly as-is; only the inline rationale comment changes.

### `firestarter_app/tests/test_fwguard.py` — already SC#3-complete, no edits needed

The 4 existing tests are:

| # | Name | Asserts | Already SC#3-ready? |
|---|---|---|---|
| 1 | `test_refuse_pre_v3_firmware` | Mock `FW: 2.0.11` → `pytest.raises(FirmwareOutdatedError, match="pre-v1.2")` + body contains `"2.0.11"`, `"firestarter fw --install"`, `"v3.0.0 or later"` | YES |
| 2 | `test_accept_v3_firmware` | Mock `FW: 3.0.0` → no raise | YES |
| 3 | `test_dev_escape_hatch_env_var` | `FIRESTARTER_DEV_ALLOW_PRE_V12=1` + mock `FW: 2.0.11` → no raise | YES |
| 4 | `test_malformed_version_defaults_to_refuse` | Mock `FW: x.x.x` → raises with `match="pre-v1.2"` | YES |

**Verification:**
- The test message at `serial_comm.py:765-770` contains `"pre-v1.2"`, `"v3.0.0 or later"`, and `"firestarter fw --install"` — all 3 strings test #1 asserts on. Match.
- Test #2 mocks `"FW: 3.0.0"` which would be the actual firmware reply after Phase 9 (`OK: FW: 3.0.0-dev` → host regex extracts `3.0.0` → `major=3` → guard passes). Match.
- Test #3 keeps the env-var bypass behavior intact. Match.
- Test #4 exercises the malformed-version refuse path. Independent of the version bump.

**No file edits required.** All 4 tests stay green unchanged after the Phase 9 firmware bump.

**SC#3 closure rationale:** D-07 says "Test is exercised by a unit test that mocks a pre-v1.2 FW handshake reply OR by manual regression against an older firmware build." Test #1 is exactly the mocked path; planner can mark SC#3 satisfied by `pytest tests/test_fwguard.py` returning 4/4 PASS after the firmware bump. Manual regression against a real pre-Phase-9 firmware is OPTIONAL — both boards plus the new firmware are on the operator's bench during D-10, so a one-shot "flash an old `firestarter@275522a` build then try a current host command" check is achievable as a belt-and-braces validation. Recommend the planner make manual regression a **soft** acceptance item, not a blocker — the mocked test is the load-bearing SC#3 evidence.

### `test_decoder.py` — unaffected by version bump

The decoder test suite (`firestarter_app/tests/test_decoder.py`) uses `b"2.0.11-dev"` as a synthetic FW-version test payload at lines 374 and 389. This is **test input data**, not a version-string assertion. The tests construct synthetic MSG_OK_FW_HANDSHAKE frames with this string and verify the decoder renders them correctly. No edits required after the Phase 9 firmware bump (the firmware version on the wire is independent of test fixture content).

---

## Flash Measurement Recipe

### Reproducible measurement protocol

**Step 1 — clean both build trees** (forces full recompile so the measurement reflects the deletion, not cached objects):

```bash
cd /workspaces/firestarter_prom/firestarter
pio run -e leonardo -t clean
pio run -e uno -t clean
```

**Step 2 — measure Leonardo:**

```bash
cd /workspaces/firestarter_prom/firestarter
pio run -e leonardo
```

Grep the exact lines:
```
RAM:   [======    ]  XX.X% (used NNNN bytes from NNNN bytes)
Flash: [========= ]  XX.X% (used NNNNN bytes from 28672 bytes)
```

**Step 3 — measure Uno:**

```bash
cd /workspaces/firestarter_prom/firestarter
pio run -e uno
```

Grep the exact lines (same shape, max Flash is 32256 bytes for Uno).

### Reproducibility properties

| Property | Verified | Notes |
|---|---|---|
| PlatformIO version | `5.2.0` (per `08-MEASUREMENT.md` header) | Pin to environment; check `pio --version` if a co-developer reports drift. |
| Toolchain | `toolchain-atmelavr @ 1.70300.191015 (7.3.0)` | Pinned via `platform = atmelavr` in env config. |
| Arduino framework | `framework-arduino-avr @ 5.3.0` | Pinned via `framework = arduino`. |
| Optimization level | Release mode default (`-Os`) | No `-O0`/`-O3` overrides in `platformio.ini`. |
| Build determinism | Deterministic byte count on identical source | Phase 6/7/8 close measurements reproduced consistently. |
| `name_firmware.py` `extra_scripts` | Yes (renames the output ELF) | No effect on size measurement. |

**Build flag inventory** (verified against `platformio.ini`):
- Common: `-D MONITOR_SPEED=250000`, `-D HARDWARE_REVISION`, `-D DEV_TOOLS`
- Disabled (commented): `-D SERIAL_DEBUG`, `-D DEBUG_ADDRESS`, `-D EXTRA_INFO_LOGGING`
- Uno-only: `-D RURP_BOARD_NAME=\"uno\"`, `-D SERIAL_ON_IO`
- Leonardo-only: `-D RURP_BOARD_NAME=\"leonardo\"`, `-D DATA_BUFFER_SIZE=512`

The Leonardo `DATA_BUFFER_SIZE=512` override (noted as "TEMP" in platformio.ini line 40) makes Leonardo's buffer match Uno's. This is in place for the Phase 8 close baseline; Phase 9 must measure with the same flag to maintain the apples-to-apples comparison. **Do not change `DATA_BUFFER_SIZE` in Phase 9.**

### Deltas to compute and record in `09-MEASUREMENT.md`

The `08-MEASUREMENT.md` "Anchor for Plan 9" table (lines 308-319) defines the 5 reference rows. Phase 9's job is to add row 5 and compute 4 deltas:

| Delta | Reference row | Significance |
|---|---|---|
| v1.1 (98.7%) → Phase 9 close | Row 1 | **LMIG-04 acceptance number** — Phase 10 DOC-02 cites this verbatim |
| Phase 6 close → Phase 9 close | Row 2 | "Pure migration recovery" — what the catalog overhead cost vs final state |
| Phase 7 close → Phase 9 close | Row 3 | "State-machine + cleanup contribution" |
| Phase 8 close → Phase 9 close | Row 4 | **"Logging.h macro tower deletion, isolated"** — the Phase 9 surface win, attributable purely to Phase 9 changes |

**Acceptance gate (LMIG-04):** Leonardo Flash < 90% (i.e., < ~25,805 / 28,672 bytes). Current Phase 8 close is 85.6% — already below the threshold. Phase 9 should land further below.

**Expected magnitude of Phase 8 → Phase 9 incremental delta:**
- `LOG_OK_MSG[] PROGMEM = "OK"`: 3 bytes (string itself, no null term in PROGMEM literal-array form).
- `_firestarter_log_ram` + `_firestarter_log_progmem`: ~80-150 bytes each (function bodies + Serial.print + Serial.print(F(": ")) + Serial.println + Serial.flush — verifying with `avr-size --format=sysv` after deletion is the way to nail the exact number).
- `rurp_log` + `rurp_log_P` weak defaults + Uno strong overrides: ~30-50 bytes (each is essentially a thin wrapper).
- Macro expansion at deleted call-sites (`send_ack("")` × 2 + `send_ack_const(FW_VERSION)` × 1): zero net change (the inline `F("OK: FW: ")` literal at `hardware_operations.cpp:86` replaces what was already PROGMEM, and `LOG_OK_ID(MSG_OK_READY)` is smaller than `rurp_log(LOG_OK_MSG, "")`).

**Estimate:** 100-300 B Flash reduction on each board. SRAM unchanged (the Phase 8 R-01 96-byte win was the only SRAM lever; Phase 9 touches no SRAM-resident state).

### Anchor table update (D-09)

The exact row to add (replacing the TARGET placeholder at row 5 of `08-MEASUREMENT.md:316`):

```markdown
| **Phase 9 close (LMIG-04)** | XX.X% (NNNNN / 28,672), NNNN B free | XX.X% (NNNNN / 32,256), NNNN B free | NNNN B / 2,048 B (Uno) | LMIG-04: legacy macro tower deletion (`send_ack`, `send_ack_const`, `rurp_log*`, `_firestarter_log_*`, `LOG_OK_MSG`, `debug_setup`, `log_debug`); inline `OK: FW: ` bootstrap (D-01); FW version → 3.0.0-dev. |
```

Phase 9's `09-MEASUREMENT.md` extends this with the 4-delta attribution table. Phase 10 DOC-02 quotes the v1.1 → Phase 9 row verbatim into `MILESTONES.md`.

---

## Bench Verification Matrix Re-use

The `08-MEASUREMENT.md` §"Bench Verification — Chipless Wire-Protocol Validation" matrix (lines 322-384) is Phase 9's re-run target. **Phase 9 re-runs this entire matrix unchanged on `3.0.0-dev` firmware.**

### Tests in the matrix

| Band | Frame | Test command (Uno) | Test command (Leonardo) | Version-string sensitivity? |
|---|---|---|---|---|
| OK composite (P-04) | MSG_OK_FW_HANDSHAKE u8+u8+ascii_str | `firestarter -p /dev/ttyACM0 fw` | `firestarter -p /dev/ttyACM1 fw` | **YES — displayed string changes from `2.0.11-dev` to `3.0.0-dev`** |
| OK fixed (P-02) | MSG_OK_REV u8+u8 | `firestarter -p /dev/ttyACM0 hw` | `firestarter -p /dev/ttyACM1 hw` | No |
| OK fixed (P-03) | MSG_OK_CFG u32+u32+u8 | `firestarter -p /dev/ttyACM0 config` | `firestarter -p /dev/ttyACM1 config` | No |
| INFO | MSG_INFO_* free-text | (incidental) | (incidental) | No |
| INIT | MSG_INIT_DONE | `firestarter -p /dev/ttyACM0 id W27C512` | (preempted by ERROR on Leo, OK) | No |
| DATA (W-03) | MSG_DATA_VPP_VOLTAGE u16+u16 | `firestarter -p /dev/ttyACM0 vpp` | `firestarter -p /dev/ttyACM1 vpp` | No |
| DATA (W-03) | MSG_DATA_VPE_VOLTAGE u16+u16 | `firestarter -p /dev/ttyACM0 vpe` | `firestarter -p /dev/ttyACM1 vpe` | No |
| ERROR | MSG_ERROR_* (parameterized) | (incidental during `id`) | (incidental, observed in Phase 8 — VPP high) | No |
| Wire-format u16 len (W-04) | implicit | every frame | every frame | No |

### Tests invalidated by the version bump

**Exactly one observable changes:** the P-04 `firestarter fw` output. Phase 8 observed:
```
OK: FW: 2.0.11-dev:uno, HW: Rev1, Cmd: 0x0b
OK: FW: 2.0.11-dev:leonardo, HW: Rev1, Cmd: 0x0b
```
Phase 9 will observe:
```
OK: FW: 3.0.0-dev:uno, HW: Rev1, Cmd: 0x0b
OK: FW: 3.0.0-dev:leonardo, HW: Rev1, Cmd: 0x0b
```
This is the **expected** observable for Phase 9 — it directly demonstrates SC#3 (firmware version handshake reports 3.0.0).

### Bench commands re-used (note: no `FIRESTARTER_DEV_ALLOW_PRE_V12` needed)

Phase 8's bench session used `FIRESTARTER_DEV_ALLOW_PRE_V12=1` prefix on every command because the firmware was still `2.0.11-dev` and the host guard wanted `major ≥ 3`. **After Phase 9 ships `3.0.0-dev`, the env-var is no longer needed** — the guard passes natively. Phase 9's bench commands should DROP the `FIRESTARTER_DEV_ALLOW_PRE_V12=1` prefix to exercise the SC#3 native-pass path.

```bash
# Flash both boards with the Phase 9 firmware
cd firestarter
pio run -t upload -e uno --upload-port /dev/ttyACM0
pio run -t upload -e leonardo --upload-port /dev/ttyACM1

# SC#3 native-pass verification: no env-var, must succeed against 3.0.0-dev
firestarter -p /dev/ttyACM0 fw       # expect: OK: FW: 3.0.0-dev:uno, ...
firestarter -p /dev/ttyACM1 fw       # expect: OK: FW: 3.0.0-dev:leonardo, ...

# Full chipless matrix re-run on both boards
firestarter -p /dev/ttyACM0 hw       # P-02 sentinel
firestarter -p /dev/ttyACM1 hw       # P-02 sentinel
firestarter -p /dev/ttyACM0 config   # P-03 sentinel
firestarter -p /dev/ttyACM1 config   # P-03 sentinel
firestarter -p /dev/ttyACM0 vpp      # MSG_DATA_VPP_VOLTAGE
firestarter -p /dev/ttyACM1 vpp
firestarter -p /dev/ttyACM0 vpe      # MSG_DATA_VPE_VOLTAGE
firestarter -p /dev/ttyACM1 vpe
firestarter -p /dev/ttyACM0 id W27C512   # exercises INIT_DONE
firestarter -p /dev/ttyACM1 id W27C512
```

**No tests in the matrix are invalidated by the version bump** — only the displayed FW-version-string content changes, and that change is the very thing SC#3 demands.

---

## Phase 8 UAT Carry-over

Phase 8 has two PENDING acceptance items recorded in `08-MEASUREMENT.md`:

### SC#2 (Phase 8) — Write end-to-end on a chip

**Status quote** (08-MEASUREMENT.md:200-211):
> SC#2 requires verifying that `firestarter write -e W27C512` runs end-to-end on both Uno and Leonardo with:
> - INIT / MAIN / END acks rendered from ID-frame decoding alone (no `INIT:` / `MAIN:` / `END:` text prefix visible in CLI output)
> - Bootstrap `OK: FW: ...` text line still present at command start (LFW-05 preserved)
> - Write completes with a success message

**Status:** PENDING — no chip was seated during the Phase 8 bench session.

**Phase 9 bundling rationale:** The version bump invalidates any prior chip-seated test (the host's pre-Phase-9 firmware refusal path is now actively engaged on old firmware). Both boards are on the operator's bench for D-10 anyway. Re-running SC#2 on `3.0.0-dev` firmware closes Phase 8 SC#2 AND validates Phase 9's wire shape integrity end-to-end.

### SC#3 (Phase 8) — Byte-identical readback

**Status quote** (08-MEASUREMENT.md:216-227):
> SC#3 requires verifying that `firestarter read -e W27C512 -o out.bin` produces a byte-identical binary file vs a pre-Phase-8 baseline.
> 1. Capture a pre-Phase-8 baseline (from a pre-Phase-8 git checkout) if not already available
> 2. Flash Phase 8 firmware to both boards
> 3. Run `firestarter read` on both boards and `diff` the output against the baseline

**Status:** PENDING — no chip was seated; baseline file may already exist on the operator's bench.

**Phase 9 bundling rationale:** Same as Phase 8 SC#2 — chip seated on both boards anyway, version-bump invalidates prior chip-seated tests. If the pre-Phase-8 baseline exists, the operator runs `firestarter read -e W27C512 -o phase9.bin && diff phase8-baseline.bin phase9.bin`. If no baseline exists, the operator captures a fresh baseline from `3.0.0-dev` and notes it as the new reference for v1.2+.

### Bundled acceptance list for Phase 9 bench step

The Phase 9 bench-verification task should explicitly close:

1. **Phase 9 SC#3** — host guard regression test (4 tests pass after firmware bump, exercised via `pytest tests/test_fwguard.py`).
2. **Phase 9 SC#4** — Leonardo Flash < 90% with measurable headroom recorded.
3. **Phase 9 SC#5** — Uno Flash recorded alongside.
4. **Phase 9 SC#1** — PROGMEM exemption audit list published (frame infra + parser keys + inline F() literals only).
5. **Phase 9 SC#2** — legacy macros zero hits via grep gate.
6. **Phase 8 SC#2 (carried)** — `firestarter write -e W27C512` end-to-end on Uno AND Leonardo, success message verified, INIT/MAIN/END all ID-frame.
7. **Phase 8 SC#3 (carried)** — `firestarter read -e W27C512 -o out.bin` byte-identical to baseline on Uno AND Leonardo.

**Project memory active throughout:**
- `[[feedback_always-mirror-uno-leonardo-tests]]` — every bench step runs on BOTH boards.
- `[[project_leonardo-shield-socket-wonky]]` — if Leonardo readback differs from Uno on SC#3 carried, suspect chip contact first before declaring a regression.
- `[[feedback_ic-removal-autonomy]]` — chip swap cycles between boards do not need per-cycle confirmation.

---

## Validation Architecture

> Required per `.planning/config.json` (no `nyquist_validation: false` flag set). The plan-checker uses this section to enforce Nyquist dimension 8.

### Test Framework

| Property | Value |
|---|---|
| Firmware native tests | PlatformIO + Unity, `[env:native]` with `test_framework = unity` |
| Host tests | pytest 9.0.3 + pytest pyproject config |
| Firmware framework config | `firestarter/platformio.ini` `[env:native]` (lines 43-67) |
| Host framework config | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| Firmware quick run | `cd firestarter && pio test -e native -f '*test_dispatch*'` (~2 s) |
| Firmware full native | `cd firestarter && pio test -e native` (~5 s; 22 of 24 tests PASS; 2 pre-existing ERRORs unrelated to Phase 9) |
| Host quick run | `cd firestarter_app && pytest tests/test_fwguard.py -q` (<1 s) |
| Host full | `cd firestarter_app && pytest -q` (29 tests, <1 s) |
| Firmware build (Leonardo) | `cd firestarter && pio run -e leonardo` (~1.2 s) |
| Firmware build (Uno) | `cd firestarter && pio run -e uno` (~1.1 s) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test type | Automated command | File exists? |
|---|---|---|---|---|
| LFW-03 | All legacy log call-sites already converted; no new call-sites remain | grep gate | `bash -c "grep -rn 'send_ack\\|send_ack_const\\|rurp_log\\b\\|rurp_log_P\\|_firestarter_log_\\|LOG_OK_MSG\\|log_info_const\\|log_error_format\\|log_warn\\b' firestarter/src/ firestarter/include/ firestarter/lib/ \| wc -l"` (expect: 0) | YES (script-able) |
| LFW-04 | No PROGMEM string literals exist solely to be passed to a log function | enumeration | `bash -c "grep -rn 'PROGMEM' firestarter/src/ firestarter/include/ \| grep -v 'MAGIC_PREAMBLE\\|CRC8_TABLE\\|key_'"` (expect: only F() literals + frame infra) | YES (manual review of grep output) |
| LMIG-04 | Leonardo Flash < 90% with measurable headroom vs v1.1's 98.7% | build | `cd firestarter && pio run -e leonardo \| grep '^Flash:'` (parse % and bytes) | YES (build target) |
| SC#3 host guard regression | Pre-v1.2 firmware refused; v3.0.0+ accepted; env-var escape hatch works | unit | `cd firestarter_app && pytest tests/test_fwguard.py -v` (expect: 4 PASS) | **YES — no edits needed** |
| Phase 9 firmware FW version handshake | Firmware reports `3.0.0-dev` | bench (manual) | `firestarter -p /dev/ttyACM0 fw` (expect: `OK: FW: 3.0.0-dev:uno, ...`) | YES (bench step) |
| Phase 9 SC#2 grep gate | Legacy log macros zero hits | grep | Same as LFW-03 above | YES |
| Phase 9 SC#1 PROGMEM audit | Documented exemption list | enumeration | Same as LFW-04 above; output captured into `09-MEASUREMENT.md` | YES |
| Phase 8 carried SC#2 | W27C512 write end-to-end on both boards | hardware integration | `firestarter -p /dev/ttyACM0 write -e W27C512 <hex>` (operator verifies success) | bench |
| Phase 8 carried SC#3 | W27C512 byte-identical readback on both boards | hardware integration | `firestarter -p /dev/ttyACM0 read -e W27C512 -o out.bin && diff baseline.bin out.bin` | bench |
| Native test regression (no break) | `pio test -e native` test_dispatch + test_messages still pass | unit | `cd firestarter && pio test -e native -f '*test_dispatch*' -f '*test_messages*'` (expect: 22+ PASS, same as Phase 8) | YES |
| Host decoder regression (no break) | 25 decoder tests still pass | unit | `cd firestarter_app && pytest tests/test_decoder.py -q` (expect: 25 PASS) | YES |

### Sampling Rate

- **Per task commit:** `cd firestarter && pio run -e leonardo` (verifies the firmware builds; ~1 s) AND `cd firestarter_app && pytest tests/test_fwguard.py tests/test_decoder.py -q` (host regression; <1 s).
- **Per wave merge:** Add `cd firestarter && pio test -e native -f '*test_dispatch*' -f '*test_messages*'` (~5 s) for native test regression. Run `pio run -e uno` AND `pio run -e leonardo` to confirm both production builds clean.
- **Phase gate:** Full suite — `pio run -e uno && pio run -e leonardo && pio test -e native && cd firestarter_app && pytest -q` — all must be green AND `09-MEASUREMENT.md` published AND bench-verification matrix re-run on both boards AND Phase 8 SC#2/SC#3 closed via chip-seated test.

### Wave 0 Gaps

**None — existing test infrastructure covers all Phase 9 requirements.** Specifically:
- `test_fwguard.py` already has the 4 SC#3 regression cases on the locked wording. No file edits needed.
- The `pio run` build-output parsing for Flash % is a standard PlatformIO behavior (no new framework needed).
- The grep gates for LFW-03/LFW-04 are one-liners runnable in any shell.
- The bench-verification recipe is documented in `08-MEASUREMENT.md` and re-used unchanged.

**No new test file creation, no fixture refactor, no framework install required.**

---

## Risks & Landmines

### 1. `firestarter.cpp:39` `debug_setup()` block — must be deleted atomically with macro removal

**Risk:** If the planner deletes `debug_setup()` from `uno_rurp_shield.cpp` and `leonardo_rurp_shield.cpp` BUT forgets to delete the `firestarter.cpp:38-40` `#ifdef SERIAL_DEBUG` block referencing `debug_setup()`, a SERIAL_DEBUG build will fail to link. Current production builds DO NOT define SERIAL_DEBUG (it is commented out in `platformio.ini:17`), so `pio run -e uno` and `pio run -e leonardo` will SUCCEED even with the dangling reference. The break would only surface if a developer un-comments `-D SERIAL_DEBUG` later.

**Mitigation:** Plan must include explicit deletion of `firestarter.cpp:38-40` (the `#ifdef SERIAL_DEBUG` / `debug_setup();` / `#endif` block) in the same atomic commit as the `debug_setup()` function-body deletion. Optionally, after Phase 9 lands, the planner may want to do a one-time `-D SERIAL_DEBUG` build to confirm no other dangling references (this is precautionary; not required for SC pass).

### 2. `#ifdef SERIAL_DEBUG` cleanup completeness

**Risk:** `logging.h` lines 31-41 contain a `#ifdef SERIAL_DEBUG / #else / #endif` block. Phase 9 deletes the entire file. But are there OTHER `#ifdef SERIAL_DEBUG` blocks in the firmware that reference deleted symbols?

**Verification:**

```bash
$ grep -rn '#ifdef SERIAL_DEBUG\|#ifndef SERIAL_DEBUG' firestarter/src/ firestarter/include/
firestarter/src/boards/uno_rurp_shield.cpp:22:#ifdef SERIAL_DEBUG
firestarter/src/boards/uno_rurp_shield.cpp:144:#ifdef SERIAL_DEBUG
firestarter/src/boards/leonardo_rurp_shield.cpp:144:#ifdef SERIAL_DEBUG
firestarter/src/firestarter.cpp:38:#ifdef SERIAL_DEBUG
```

- `uno_rurp_shield.cpp:22` — `#define RX_DEBUG A0 / #define TX_DEBUG A1` (line 23-24). KEEP for now (still needed if SERIAL_DEBUG is re-enabled) OR delete with the whole SoftwareSerial body at line 152-169. Recommend: delete (the SoftwareSerial body is the only thing that references these).
- `uno_rurp_shield.cpp:144` — `#include <SoftwareSerial.h>` + `SoftwareSerial debugSerial(...)` + `debug_setup()` body + `log_debug()` body. ENTIRE BLOCK deleted by Phase 9 (per D-08 Claude's discretion + caller deletion).
- `leonardo_rurp_shield.cpp:144` — single empty `void debug_setup() {}` body. DELETED.
- `firestarter.cpp:38` — `debug_setup();` caller. DELETED.

**Recommendation:** Plan must include explicit deletion of ALL FOUR `#ifdef SERIAL_DEBUG` blocks in the same wave. Also recommend deleting the `RX_DEBUG`/`TX_DEBUG` `#define`s at `uno_rurp_shield.cpp:23-24` (dead after the SoftwareSerial block goes).

### 3. `extern "C"` linkage across .c/.cpp boundary for deleted helpers

**Risk:** `_firestarter_log_ram` and `_firestarter_log_progmem` are declared without `extern "C"` in `rurp_serial_utils.h` (lines 15, 18), but are defined in a `.cpp` file (`rurp_serial_utils.cpp`). The declarations are at file scope (no `extern "C"` wrapper). If they were called from `.c` files, the mangling would mismatch.

**Verification:** `rurp_serial_utils.h:13-28` is at file scope (no `extern "C"` block). However, `rurp_serial_utils.h:8` includes `"logging.h"`, which itself is included by `.cpp` files only after Phase 8. **No `.c` file currently includes `rurp_serial_utils.h`.**

Confirmed via grep:
```bash
$ grep -n '#include "rurp_serial_utils.h"' firestarter/src/*.c firestarter/src/proms/*.c 2>/dev/null
# (empty — no .c file includes this header)
```

The two helpers are only called from `.cpp` files (`rurp_serial_utils.cpp`, `uno_rurp_shield.cpp`). Deletion is safe from a linkage perspective. **Low risk.**

### 4. `dev_tools.cpp` `send_ack("")` → `LOG_OK_ID(MSG_OK_READY)` observable change

**Risk:** The visible CLI log line changes from `OK: ` (empty body) to `OK: Ready`. If any operator-side automation script or downstream test harness greps for the empty-body form, it breaks.

**Audit:**

```bash
$ grep -rn '"OK: "\|"OK:"' firestarter_app/ --include='*.py' 2>/dev/null
# (no hits — no script depends on the empty-body literal)
$ grep -rn '"OK: "\|"OK:"' /workspaces/firestarter_prom/firestarter_test.sh /workspaces/firestarter_prom/firestarter_app/firestarter_test.sh /workspaces/firestarter_prom/firestarter_app/write_test.sh 2>/dev/null
# (no shell-script dependency)
```

**Low risk** — confirmed no automation script depends on the empty-body form. The change is purely operator-cosmetic (and an improvement). CONTEXT.md "minor semantic stretch" assessment is correct.

### 5. Flash measurement non-determinism

**Risk:** The same source tree compiled twice may produce different byte counts if link-order changes (e.g., if `pio` reshuffles object-file ordering between invocations).

**Mitigation:** PlatformIO's link order is deterministic for a given source tree (verified by Phase 6/7/8 re-measurements producing identical numbers when re-run). However, if the planner inserts file-deletion operations between two measurements without a `clean`, partial cache invalidation can show smaller-than-true savings.

**Plan must include `pio run -e leonardo -t clean && pio run -e uno -t clean` BEFORE the measurement** (recorded as the deltas). Phase 8's measurement already followed this discipline.

### 6. `pio run` Flash-percentage display rounding

**Risk:** PlatformIO rounds the displayed percentage to 1 decimal (e.g., 85.6%). A 0.05% incremental win could read as "no change." Always read the byte count, not the percentage.

**Mitigation:** The recipe above grabs **both** the percentage and the byte count. The byte count is the authoritative number; the percentage is reported alongside for human readability.

### 7. Build-cache stale objects after file deletion

**Risk:** Deleting `logging.c` or `logging.h` may leave stale `.o` / `.d` files in `.pio/build/<env>/` that link unexpected symbols.

**Mitigation:** Same as Risk #5 — `pio run -e ... -t clean` before the measurement run.

### 8. PROGMEM literals inside `F()` macros looking like dead patterns

**Risk:** `F("OK: FW: ")` and other `F(...)` Arduino macro uses create transient PROGMEM string-arrays at the call-site (compiler-generated, anonymous). A naive grep for `PROGMEM` strings won't find them. After Phase 9 inlines the `F("OK: FW: ")` literal, a strict reading of SC#1 ("zero PROGMEM string literals that exist only to be passed to a log function") could be misinterpreted as forbidding this.

**Mitigation:** SC#1 explicitly exempts `DATA:` prefix marker and non-log PROGMEM. The CONTEXT.md D-01 commentary places the inline `F("OK: FW: ")` literal in the SAME exemption class as `MAGIC_PREAMBLE` / `CRC8_TABLE` (frame-infrastructure, not log infrastructure). The planner's SC#1 verification artifact in `09-MEASUREMENT.md` must explicitly enumerate this `F("OK: FW: ")` literal as the LFW-05 bootstrap exemption and note that any `F(...)` Arduino macro use is anonymous compiler-generated PROGMEM (not a named symbol).

### 9. CRC catalog regen not needed but byte-identity must be preserved

**Risk:** Phase 9 does not modify `tools/catalog/messages.toml`. The codegen output (`firestarter/include/messages.h` + `firestarter_app/firestarter/messages.py`) should be byte-identical before and after Phase 9.

**Verification path:** the CI drift gate (`catalog-sync-check.yml` in the meta-repo + `build.yml` in firestarter + `ci.yml` in firestarter_app) runs codegen and asserts `git diff --exit-code`. If Phase 9 work somehow nudges the catalog, CI will catch it. Plan should NOT touch the catalog or codegen; this is just a guard-rail.

### 10. `dev_tools` SoftwareSerial deletion side-effect

**Risk:** Deleting the `#include <SoftwareSerial.h>` from `uno_rurp_shield.cpp:145` removes a library dependency. PlatformIO's dependency graph (visible in the build header) currently lists `SoftwareSerial @ 1.0`. After deletion, the dependency is no longer needed — but it's still discovered by PlatformIO via LDF (Library Dependency Finder) on a cold build. The dependency might disappear from the build header or remain (LDF default mode is `chain ~ soft`). Either way, this is informational, not load-bearing.

**Low risk** — does not affect build success or measurement.

### 11. Operator may want to retain SERIAL_DEBUG capability

**Risk:** If a future debugging session wants to re-enable `-D SERIAL_DEBUG`, Phase 9 has now removed the entire infrastructure (`debug_setup`, `log_debug`, `debugSerial`). The SERIAL_DEBUG code path is dead.

**Mitigation:** CONTEXT.md D-08 explicitly decides to DELETE both. The replacement debug path is `LOG_DEBUG_ID_SUB*` (added in Phase 8 Plan 07), which writes to the main serial port as a structured frame (visible in normal host log output). Operators no longer need a separate SoftwareSerial channel for debug output. This is by design.

**Document in `09-MEASUREMENT.md`** that SERIAL_DEBUG is now unused-but-defined-flag (the `#ifdef SERIAL_DEBUG` checks all evaluate to false because there are no more `#ifdef SERIAL_DEBUG` blocks after Phase 9). Optionally remove the `; -D SERIAL_DEBUG` commented-out line from `platformio.ini` to avoid operator confusion. **Recommend keeping** the commented-out line as a marker that SERIAL_DEBUG once existed.

### 12. CONTEXT.md `dt_dump_register` typo — minor risk of planner error

**Risk:** If the planner copies CONTEXT.md's function name `dt_dump_register` verbatim into the plan, a developer searching for that function will find nothing and may be confused.

**Mitigation:** This research file calls out the typo (Deletion Inventory section, "`dt_dump_register` (CONTEXT.md typo audit)"). The planner should use the actual function name `dt_set_registers` (and `dt_set_address` is already correct).

---

## Sources

### Primary (HIGH confidence — direct source-tree verification)

- `firestarter/include/logging.h` (43 lines, full read)
- `firestarter/src/logging.c` (10 lines, full read)
- `firestarter/include/version.h` (13 lines, full read)
- `firestarter/include/rurp_shield.h` lines 132-141 (declarations of log + log_id surface)
- `firestarter/include/rurp_serial_utils.h` (45 lines, full read)
- `firestarter/src/boards/rurp_serial_utils.cpp` (267 lines, full read)
- `firestarter/src/boards/uno_rurp_shield.cpp` (171 lines, full read)
- `firestarter/src/boards/leonardo_rurp_shield.cpp` lines 130-148 (debug_setup tail)
- `firestarter/src/hardware_operations.cpp` (123 lines, full read)
- `firestarter/src/dev_tools.cpp` (167 lines, full read)
- `firestarter/src/firestarter.cpp` lines 1-90 (setup() + parse_json)
- `firestarter/include/logging_id.h` lines 1-100 (LOG_OK_ID surface)
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` (171 lines, full read)
- `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` (36 lines, full read)
- `firestarter/test/native/avr/test_messages/host_stubs.cpp` (38 lines, full read)
- `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp` (48 lines, full read)
- `firestarter/test/native/avr/test_eeprom28c_chip_id/host_stubs.cpp` (35 lines, full read)
- `firestarter/platformio.ini` (67 lines, full read)
- `firestarter/include/operation_utils.h` (140 lines, full read)
- `firestarter/include/rurp_hw_rev_utils.h` (71 lines, full read)
- `firestarter/include/messages.h` lines 1-80 (catalog-emitted #defines)
- `firestarter_app/firestarter/serial_comm.py` lines 1-180, 385-485, 600-720, 720-820 (key segments)
- `firestarter_app/firestarter/messages.py` MSG_OK_READY + MSG_OK_FW_VERSION rows
- `firestarter_app/tests/test_fwguard.py` (126 lines, full read)
- `firestarter_app/tests/test_decoder.py` lines 360-410 (FW handshake decoder tests)
- `firestarter_app/firestarter/eprom_operations.py` lines 470-540 (dev_set_registers/dev_set_address_mode)
- `tools/catalog/messages.toml` lines 30-110 (OK band catalog entries)
- `tools/catalog/codegen.py` wire_format handling (lines 274-285, 570, 615, 648, 657)

### Phase planning artifacts (HIGH confidence — locked decisions)

- `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-CONTEXT.md` (183 lines, full read — D-01..D-10 + Claude's-Discretion items)
- `.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md` (528 lines, full read — anchor table at lines 308-319, bench matrix at 322-384, housekeeping at 388+)
- `.planning/REQUIREMENTS.md` (LFW-03, LFW-04, LMIG-04 — verified)
- `.planning/STATE.md` (v1.2 decisions context)
- `.planning/ROADMAP.md` §"Phase 9" (Goal + SC #1-5)
- `./CLAUDE.md`, `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md` (project-level guidelines)

### Project memory (always-on)

- `[[feedback_always-mirror-uno-leonardo-tests]]` — every Uno bench test paired with Leonardo control.
- `[[project_leonardo-shield-socket-wonky]]` — suspect chip contact on Leonardo first if readback differs.
- `[[feedback_ic-removal-autonomy]]` — IC removal granted; no per-cycle chip-removal confirmation.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| (none) | All claims in this research were verified against the live source tree or the locked CONTEXT.md / REQUIREMENTS.md / ROADMAP.md. No `[ASSUMED]` claims to enumerate. | — | — |

**This table is empty:** all research findings are sourced from direct file reads or repository state checks performed during this session. No user confirmation needed.

---

## Metadata

**Confidence breakdown:**
- Deletion inventory: HIGH — every symbol grep-verified end-to-end across firmware + tests; no surprises.
- File-fate audits (logging.h / logging.c / host_stubs_common.inc): HIGH — full content reads + includer enumeration; deletion is mechanical.
- Catalog entry status (MSG_OK_READY, MSG_OK_FW_VERSION): HIGH — host consumer paths read end-to-end; WR-03 defense verified at exact line ranges.
- Host-side surface (FIRESTARTER_DEV_ALLOW_PRE_V12, test_fwguard.py, test_decoder.py): HIGH — full test suite read; comment-update diff is two lines; test wording matches exception text byte-for-byte.
- Flash measurement recipe: HIGH — Phase 8 anchor table + bench commands re-used unchanged; reproducibility properties verified against PlatformIO + platformio.ini.
- Bench verification matrix re-use: HIGH — exactly one observable changes (FW version string), and that is the SC#3 evidence.
- Phase 8 UAT carry-over: HIGH — bundled acceptance list extracted from 08-MEASUREMENT.md verbatim.
- Validation Architecture: HIGH — all commands verified runnable in the current dev container; no Wave 0 gaps.
- Risks & landmines: HIGH — 12 items enumerated; each has a verified mitigation or evidence-of-no-impact.

**Research date:** 2026-05-19
**Valid until:** 2026-06-19 (30-day window — Phase 9 is the immediate next phase to execute; the source tree may shift if Phase 9 work begins).

---

## RESEARCH COMPLETE

Phase 9 deletion targets are fully inventoried and verified; the CONTEXT.md D-01..D-10 plan is sound with zero BLOCKERs and one minor CONTEXT.md function-name typo (`dt_dump_register` → actual `dt_set_registers`) that does not change the plan.
