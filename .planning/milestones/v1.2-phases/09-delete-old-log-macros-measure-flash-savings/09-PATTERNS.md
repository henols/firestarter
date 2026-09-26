# Phase 9: Delete Old Log Macros + Measure Flash Savings — Pattern Map

**Mapped:** 2026-05-19
**Files analyzed:** 18 (firmware deletion + firmware modification + host comment + measurement artifact)
**Analogs found:** 18 / 18 (every touched file has an in-tree analog from Phases 6/7/8 to copy patterns from)

Phase 9 is a small-surface, high-precision cleanup. Every pattern needed for it has already shipped — this map points to the exact prior commit, line range, or function the planner / executor should clone.

---

## File Classification

| New/Modified File | Role | Data Flow | Touch Kind | Closest Analog | Match Quality |
|---|---|---|---|---|---|
| `firestarter/include/logging.h` | firmware header | n/a | DELETE-ENTIRE-FILE | `firestarter/src/messages.c` (deleted in commit `891108c`) | exact — outright file deletion, no callers remain |
| `firestarter/src/logging.c` | firmware unit | n/a | DELETE-ENTIRE-FILE | `firestarter/src/messages.c` (commit `891108c`) | exact — single-symbol .c file removed when symbol goes |
| `firestarter/src/boards/rurp_serial_utils.cpp` | firmware emit (board common) | request-response | DELETE-LINES-AND-DECLS | Same file: `_firestarter_emit_frame` survivor (lines 156–242) | exact — surgical deletion of legacy log helpers, frame path stays |
| `firestarter/include/rurp_serial_utils.h` | firmware header (decls) | n/a | DELETE-LINES-AND-DECLS | Same file: surviving frame-emit declarations | exact — siblings of removed decls remain |
| `firestarter/include/rurp_shield.h` | firmware header (decls) | n/a | DELETE-LINES-AND-DECLS | Same file: `rurp_log_id` / `rurp_log_id_wide` decls (still live) | exact — keep the ID-frame decls, drop the text decls |
| `firestarter/src/boards/uno_rurp_shield.cpp` | firmware emit (Uno strong) | request-response | DELETE-LINES-AND-DECLS | Same file: surviving `rurp_log_id` Uno override (lines 98–110) | exact — pattern of board-specific override stays for ID path |
| `firestarter/src/boards/leonardo_rurp_shield.cpp` | firmware emit (Leonardo) | request-response | DELETE-LINES (`#ifdef SERIAL_DEBUG` stub) | Same file: live `rurp_set_data_*` functions surround the block | role-match |
| `firestarter/src/firestarter.cpp` | firmware controller (setup) | request-response | MODIFY-IN-PLACE (`#ifdef SERIAL_DEBUG` block delete) | Phase 8 commit `275522a` (debug_msg_buffer atomic deletion across multiple files) | exact — multi-file atomic cleanup of SERIAL_DEBUG-only code |
| `firestarter/src/hardware_operations.cpp:82–88` | firmware service (`fw_get_version`) | request-response | MODIFY-IN-PLACE (inline 3-liner) | Same file: `_firestarter_log_progmem` body (lines 23–28) AND same file: `LOG_OK_ID(MSG_OK_READY)` site at line 42 | exact — same `SERIAL_PORT.print(F(...))` + `println` + `flush` idiom |
| `firestarter/src/dev_tools.cpp:108` | firmware service (`dt_set_registers`) | request-response | MODIFY-IN-PLACE (1-line convert) | `hardware_operations.cpp:42` (live `LOG_OK_ID(MSG_OK_READY)` site, Phase 8 P-02 conversion) | exact — same conversion already shipped for the same catalog ID |
| `firestarter/src/dev_tools.cpp:154` | firmware service (`dt_set_address`) | request-response | MODIFY-IN-PLACE (1-line convert) | `hardware_operations.cpp:42` (same as above) | exact |
| `firestarter/include/version.h:11` | firmware config | n/a | MODIFY-IN-PLACE (string bump) | Commit `bbf0e0c` (`chore: bump VERSION to 2.0.7-dev to surface drift...`) | exact — same single-line `#define VERSION "..."` shape |
| 20× `#include "logging.h"` sites (see Includer Enumeration below) | various firmware | n/a | DELETE-INCLUDE-LINE | Phase 8 commit `451756f` (cross-file include cleanup when macros went) | exact — same pattern of "delete macro defs + sweep their includes in one commit" |
| `firestarter/test/native/avr/_shared/host_stubs_common.inc:45–67` | native test stub | n/a | TRIM | Same file: lines 69–170 (surviving rurp_* stubs) | exact — keep the structural pattern, delete the dead `LOG_*_MSG` block |
| `firestarter_app/firestarter/serial_comm.py:752–755` | host CLI (comment-only) | n/a | MODIFY-IN-PLACE (comment text update) | Same file: lines 42–46 + 138–141 + 400–410 (phase-tagged comment style) | exact — same `# Phase X (LXXX-NN): ...` voice |
| `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md` | phase artifact | n/a | CREATE | `.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md` (entire file) | exact — Phase 9 extends the same anchor table + reuses the bench matrix |

---

## Pattern Assignments

### 1. `firestarter/src/hardware_operations.cpp:82–88` — `fw_get_version()` inline 3-liner (D-01)

**Role:** firmware service · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE

**Primary analog (same idiom, same file, soon-to-be-deleted):** `_firestarter_log_progmem` at `rurp_serial_utils.cpp:20–28` is the canonical 3-line `SERIAL_PORT.print(F(...))` + `println(... PROGMEM ...)` + `flush()` shape that Phase 9 inlines into `fw_get_version()`.

```cpp
// firestarter/src/boards/rurp_serial_utils.cpp:20-25 (analog — being deleted in Phase 9
// but its idiom is what D-01 transplants into hardware_operations.cpp).
void _firestarter_log_progmem(PGM_P type, PGM_P p_msg) {
    SERIAL_PORT.print((const __FlashStringHelper*)type);
    SERIAL_PORT.print(F(": "));
    SERIAL_PORT.println((const __FlashStringHelper*)p_msg);
    SERIAL_PORT.flush();
}
```

**Current call-site to be replaced** (`firestarter/src/hardware_operations.cpp:82–88`):

```cpp
bool fw_get_version(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_FW_VERSION);
    // Phase 8 / P-01 / LFW-05: MSG_OK_FW_VERSION stays text-emitted to preserve
    // the host's _probe_port bootstrap path, which parses "FW: ..." as text.
    send_ack_const(FW_VERSION);
    return true;
}
```

**Target after D-01** (note: `FW_VERSION` is a `const char*` macro from `version.h`; `SERIAL_PORT.println(const char*)` is the correct overload — no `F()` wrapper around it):

```cpp
bool fw_get_version(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_FW_VERSION);
    // LFW-05 bootstrap: the lone surviving text-format emit. Inlined here in
    // Phase 9 after the legacy send_ack_const / rurp_log_P chain was deleted.
    // F("OK: FW: ") keeps the literal in PROGMEM with no named symbol — same
    // PROGMEM-exemption category as MAGIC_PREAMBLE / CRC8_TABLE (SC#1).
    SERIAL_PORT.print(F("OK: FW: "));
    SERIAL_PORT.println(FW_VERSION);
    SERIAL_PORT.flush();
    return true;
}
```

**Include cleanup** in this same file (`hardware_operations.cpp:7`): drop `#include "logging.h"` — every other Phase 9 deletion eliminates the macros this header still defined. `logging_id.h` (line 8) provides `LOG_DEBUG_ID_SUB` and stays.

**Byte-identical wire-format invariant:** the host `_probe_port` regex `r"FW:\s*([\d.x]+)"` (`serial_comm.py:748`) extracts `current_version` from any line containing `FW:` followed by version digits. The pre-D-01 output `OK: FW: 2.0.11-dev` and post-D-01 output `OK: FW: 3.0.0-dev` are produced through the identical wire path. **No host change required.**

---

### 2. `firestarter/src/dev_tools.cpp:108` and `:154` — `send_ack("")` → `LOG_OK_ID(MSG_OK_READY)` (D-04)

**Role:** firmware service · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (1-line conversion ×2)

**Primary analog (already-shipped LOG_OK_ID(MSG_OK_READY) site):** `hardware_operations.cpp:42` — shipped in Phase 8 commit `ea2a3fb` (`feat(hardware_operations): convert Ready + VPP/VPE + hw_get_version + hw_get_config to ID frames (P-02, P-03, W-01, W-03); fw_get_version stays text per LFW-05`).

```cpp
// firestarter/src/hardware_operations.cpp:40-42 (live analog)
// Send a ready signal to the client to prompt it for the first ACK.
// This establishes a handshake and avoids a race condition.
LOG_OK_ID(MSG_OK_READY);
```

**Before / after at `dev_tools.cpp:108` (`dt_set_registers`):**

```cpp
// BEFORE (line 108)
    send_ack("");

// AFTER (D-04)
    LOG_OK_ID(MSG_OK_READY);  // D-04: was send_ack(""); semantics ≈ "setup done, waiting on user button"
```

**Before / after at `dev_tools.cpp:154` (`dt_set_address`):**

```cpp
// BEFORE (line 154)
    send_ack("");

// AFTER (D-04)
    LOG_OK_ID(MSG_OK_READY);  // D-04: was send_ack(""); semantics ≈ "setup done, waiting on user button"
```

**Include posture in `dev_tools.cpp`:** lines 14–15 currently are:

```cpp
#include "logging.h"      // line 14 — DROP (provides send_ack which goes)
#include "logging_id.h"   // line 15 — KEEP (provides LOG_OK_ID + MSG_OK_READY)
```

**Catalog catalog entry to KEEP unchanged** (`tools/catalog/messages.toml:33–39`): no edits — `MSG_OK_READY` is already `wire_format = "id_frame"`, no params, format `"Ready"`. RESEARCH.md confirms no host caller of `expect_ack()` inspects the body string for dev_tools commands; the visible output flips from `OK: ` to `OK: Ready` which is operationally an improvement.

---

### 3. `firestarter/include/version.h:11` — VERSION bump (D-06)

**Role:** firmware config · **Data Flow:** n/a · **Touch:** MODIFY-IN-PLACE (single-line `#define`)

**Primary analog (prior version-bump commit on this exact file):** `bbf0e0c` — `chore: bump VERSION to 2.0.7-dev to surface drift past 2.0.6 tag`.

**Commit-message style to mirror** (Henrik wrote this; Phase 9's commit should match the voice):

```
chore: bump VERSION to 3.0.0-dev (LFW-05 major bump, v1.2 milestone)

Phase 9 (LMIG-04) deletes the legacy text-prefix log infrastructure
(send_ack, send_ack_const, rurp_log, rurp_log_P, _firestarter_log_*,
LOG_OK_MSG) and the SERIAL_DEBUG debug_setup/log_debug functions. With
the host already wired in Phase 6 to refuse pre-v1.2 firmware (major<3)
this bump flips the guard from "always-warn pending firmware bump" to
"actively load-bearing against pre-Phase-9 firmware".

VERSION = "3.0.0-dev" — the -dev suffix is stripped to "3.0.0" on the
release tag in Phase 10 (DOC-02). Bench scripts can still talk to
historical v2.x firmware via FIRESTARTER_DEV_ALLOW_PRE_V12=1.
```

**Diff shape** (mirrors `bbf0e0c`'s 1-line diff):

```diff
-#define VERSION "2.0.11-dev"
+#define VERSION "3.0.0-dev"
```

**Host side regression: zero edits.** `firestarter_app/tests/test_fwguard.py` already asserts "Please upgrade the firmware to v3.0.0 or later" wording (RESEARCH.md §"Host-side Surface" lines 437–456 enumerates all 4 cases — all already green on the pre-bumped firmware via test mocking).

---

### 4. `firestarter/include/logging.h` — DELETE entire file (D-02 + D-08 Claude's discretion)

**Role:** firmware header · **Data Flow:** n/a · **Touch:** DELETE-ENTIRE-FILE

**Primary analog (prior whole-file deletion commit in the same repo):** `891108c` — `chore(catalog): drop unused MSG_PARAM_COUNT helper + delete messages.c`.

**Commit-message structure to mirror** (Henrik's voice — 3-line subject, then rationale, then explicit `Changes in this submodule:` enumeration):

```
refactor(logging): delete legacy macro tower (logging.h, logging.c, rurp_log*, debug_setup, log_debug)

After Phase 9 D-01 inlines the LFW-05 FW-version emit into
fw_get_version() and D-04 converts the last two send_ack("") sites in
dev_tools.cpp to LOG_OK_ID(MSG_OK_READY), the entire legacy text-prefix
log path has zero callers. The deletion is atomic with the inline emit
(D-01) and version bump (D-06) so the firmware compiles continuously.

Changes in this submodule:
- delete include/logging.h (extern LOG_OK_MSG, send_ack/send_ack_const
  macros, #ifdef SERIAL_DEBUG debug_setup/log_debug decls + no-op
  fallback macros)
- delete src/logging.c (sole symbol LOG_OK_MSG[] PROGMEM = "OK")
- delete _firestarter_log_ram/_firestarter_log_progmem from
  rurp_serial_utils.cpp + .h (weak text-frame emit helpers; only
  callers were the rurp_log/rurp_log_P functions also deleted)
- delete rurp_log/rurp_log_P weak defaults from rurp_serial_utils.cpp
  (lines 246-251) and Uno strong overrides from uno_rurp_shield.cpp
  (lines 80-91)
- delete debug_setup()/log_debug() SERIAL_DEBUG bodies +
  SoftwareSerial debugSerial block from uno_rurp_shield.cpp
  (lines 152-169) and empty stub from leonardo_rurp_shield.cpp
  (lines 144-146); RX_DEBUG/TX_DEBUG #defines at uno_rurp_shield.cpp
  lines 22-25 go with them
- delete #ifdef SERIAL_DEBUG / debug_setup(); / #endif from
  firestarter.cpp:38-40 (the lone non-SERIAL_DEBUG-gated caller of
  debug_setup is itself wrapped in SERIAL_DEBUG; dangling reference
  would only break SERIAL_DEBUG builds, but goes anyway)
- drop #include "logging.h" from 20 files (see Phase 9 RESEARCH.md
  "logging.h — Includer enumeration"); 0 files migrate to
  logging_id.h (they already include it where needed)
- trim test/native/avr/_shared/host_stubs_common.inc:45-67 (8
  LOG_*_MSG PROGMEM externs + rurp_log/rurp_log_P no-op stubs)
- bump include/version.h: "2.0.11-dev" -> "3.0.0-dev"
```

**Includer enumeration to action in this commit** (20 sites; RESEARCH.md lines 229–253 has the full table — replicated here so the executor doesn't have to cross-reference):

```
firestarter/include/operation_utils.h:19       — DROP include
firestarter/include/rurp_hw_rev_utils.h:10     — DROP include
firestarter/include/rurp_serial_utils.h:8      — DROP include
firestarter/src/boards/leonardo_rurp_shield.cpp:13 — DROP include
firestarter/src/boards/uno_rurp_shield.cpp:13  — DROP include
firestarter/src/dev_tools.cpp:14               — DROP include (logging_id.h at line 15 stays)
firestarter/src/eprom_operations.cpp:11        — DROP include
firestarter/src/firestarter.cpp:16             — DROP include
firestarter/src/hardware_operations.cpp:7      — DROP include (logging_id.h at line 8 stays)
firestarter/src/json_parser.c:12               — DROP include
firestarter/src/logging.c:1                    — N/A (file deleted)
firestarter/src/operation_utils.cpp:14         — DROP include
firestarter/src/proms/eeprom_28c.cpp:14        — DROP include
firestarter/src/proms/eprom.cpp:13             — DROP include
firestarter/src/proms/flash_intel.cpp:13       — DROP include
firestarter/src/proms/flash_type_3.cpp:14      — DROP include
firestarter/src/proms/flash_type_4.cpp:14      — DROP include
firestarter/src/proms/flash_utils.cpp:12       — DROP include
firestarter/src/proms/memory.cpp:18            — DROP include
firestarter/src/proms/sram.cpp:12              — DROP include
```

---

### 5. `#ifdef SERIAL_DEBUG` block deletion — atomic across 4 files (RESEARCH.md §Risks #1+#2)

**Primary analog (prior multi-file atomic SERIAL_DEBUG cleanup in this repo):** Phase 8 commit `275522a` — `refactor(debug-buffer): delete debug_msg_buffer, legacy debug macros, and Uno debug_msg_buffer paths` — touched `firestarter.cpp`, `uno_rurp_shield.cpp`, `leonardo_rurp_shield.cpp`, and `logging.h` in a single commit so neither production nor SERIAL_DEBUG builds bisect to a broken state.

**4 sites to delete atomically in the Phase 9 W2 commit:**

```cpp
// 1. firestarter/src/firestarter.cpp:38-40 — CALLER
#ifdef SERIAL_DEBUG
    debug_setup();
#endif
// → DELETE all 3 lines from setup()

// 2. firestarter/src/boards/uno_rurp_shield.cpp:22-25 — RX/TX defines (dead after #3 goes)
#ifdef SERIAL_DEBUG
#define RX_DEBUG  A0
#define TX_DEBUG  A1
#endif
// → DELETE block

// 3. firestarter/src/boards/uno_rurp_shield.cpp:144-161 — SoftwareSerial body
#ifdef SERIAL_DEBUG
#include <SoftwareSerial.h>
SoftwareSerial debugSerial(RX_DEBUG, TX_DEBUG);
void debug_setup() { debugSerial.begin(57600); }
void log_debug(PGM_P type, const char* msg) { /* ... */ }
#endif
// → DELETE block (and the outer `#endif` that closes ARDUINO_AVR_UNO stays)

// 4. firestarter/src/boards/leonardo_rurp_shield.cpp:144-146 — empty stub
#ifdef SERIAL_DEBUG
void debug_setup() {}
#endif
// → DELETE block
```

**Risk mitigation (per RESEARCH.md §"Risks & Landmines" #1+#2):** Production builds do NOT define `SERIAL_DEBUG` (`platformio.ini:17` commented out), so `pio run -e uno` / `pio run -e leonardo` will SUCCEED even with a partial deletion. The break would only surface if a future developer enables `-D SERIAL_DEBUG`. Atomic commit is mandatory; partial state poisons the SERIAL_DEBUG build.

---

### 6. `firestarter/test/native/avr/_shared/host_stubs_common.inc:45–67` — TRIM (D-03)

**Role:** native test stub · **Data Flow:** n/a · **Touch:** TRIM (lines 45–67)

**Primary analog (live editing convention in the same file):** the surviving stubs at lines 69–170 (rurp_write_to_register, rurp_read_from_register, etc.) — every stub uses `extern "C"` linkage with no-op body or hardcoded return; comments are 3-line prose paragraphs preceding each functional group.

**Exact deletion (lines 42–67 — preserve the comment ABOVE line 45 about "PROGMEM log-tag strings" only if any string remains; since all 8 strings + both rurp_log functions go, delete the comment block too):**

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

**Verification recipe** (from VALIDATION.md row 9-04): `cd firestarter && pio test -e native -f '*test_dispatch*'` — must still pass 22+ test cases (no change vs Phase 8 close).

**Note on `avr/pgmspace.h` shim files:** RESEARCH.md line 318 confirms the 4 shim files contain *comment-only* references to `rurp_log` / `rurp_log_P` — leave them alone. The `PGM_P` typedef stays in scope (referenced by other AVR macros). No additional edits required.

---

### 7. `firestarter_app/firestarter/serial_comm.py:752–755` — comment-update only

**Role:** host CLI · **Data Flow:** n/a · **Touch:** MODIFY-IN-PLACE (comment text)

**Primary analog (phase-tagged comment style in the same file):** lines 42–46 + 138–141 + 400–410 — all use the format `# Phase N (LXXX-NN): <description>`. Phase 9's update preserves this voice exactly.

```python
# Same-file analog 1 — firestarter_app/firestarter/serial_comm.py:138-141
# Phase 8 W-01: INIT/MAIN/END removed (now arrive as ID frames via the catalog
# decoder above; the prefix path is dead weight that the legacy bootstrap text
# line briefly resurrects).

# Same-file analog 2 — firestarter_app/firestarter/serial_comm.py:400
# (LFW-05). A buggy or malicious peer emitting id=0x03 / id=0x06 as a
# binary frame would bypass the FW-version text-path check; the WR-03
# guard below rejects them.
```

**Exact diff** (`serial_comm.py:752–755`):

```diff
-                                # Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2
-                                # firmware. The firmware bumps to major=3 in
-                                # Phase 9; until then, bench scripts use
-                                # FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass.
+                                # Phase 6 (LFW-05 + LHOST-04): refuse pre-v1.2 firmware. The firmware bumped
+                                # to major=3 in Phase 9. Set FIRESTARTER_DEV_ALLOW_PRE_V12=1 to bypass when
+                                # bench-testing a current host against a historical (v2.x) firmware build.
```

**Verification gate (VALIDATION.md row 9-03):** `grep -n 'until then' firestarter_app/firestarter/serial_comm.py | wc -l` → expect `0`. Mechanism is unchanged; only the inline rationale comment changes. No `test_fwguard.py` edits.

---

### 8. `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md` — CREATE

**Role:** phase artifact · **Data Flow:** n/a · **Touch:** CREATE

**Primary analog (entire file):** `.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md`. Phase 9 reuses three sections verbatim in shape:

#### (a) 5-column Anchor Table — extend with Phase 9 close row

Verbatim from `08-MEASUREMENT.md:310-316`:

```markdown
| Snapshot | Leonardo Flash | Uno Flash | SRAM (Uno) | Notes |
|----------|----------------|-----------|------------|-------|
| **v1.1 close** | 98.7% (~28,299 / 28,672) | not formally recorded | — | ROADMAP-pinned baseline; per-byte derived from %. |
| **Phase 6 close** | 98.7% (28,292 / 28,672), 380 B free | 80.9% (26,100 / 32,256), 6,156 B free | 1,683 B / 2,048 B (Uno) | LMIG-01: new ID infrastructure alongside legacy text; no call-sites converted yet. |
| **Phase 7 close** | 94.3% (27,026 / 28,672), 1,646 B free | 77.0% (24,838 / 32,256), 7,418 B free | 1,587 B / 2,048 B (Uno) | LMIG-02: all ERROR/WARN/INFO call-sites converted; dead-code deleted. |
| **Phase 8 close (THIS plan)** | 85.6% (24,538 / 28,672), 4,134 B free | 69.2% (22,330 / 32,256), 9,926 B free | 1,497 B / 2,048 B (Uno) | LMIG-03: OK/INIT/MAIN/END state-machine acks + MSG_DATA_CHUNK streaming + R-01 SRAM win. Hardware verification (SC#2+SC#3) pending Task 2. |
| **Phase 9 close (LMIG-04)** | TARGET: < 90% (< ~25,805 / 28,672) | TBD; record alongside Leonardo | TBD | After Phase 9: `LOG_*_MSG` PROGMEM deletion + legacy macro tower deletion. |
```

Phase 9's `09-MEASUREMENT.md` replaces row 5's `TARGET / TBD` cells with measured values (per the recipe in RESEARCH.md §"Flash Measurement Recipe"). It also adds a *4-delta attribution table* immediately below the anchor table — RESEARCH.md §"Deltas to compute and record" (lines 517–537) is the exact spec:

```markdown
| Delta | Reference row | Significance |
|---|---|---|
| v1.1 (98.7%) → Phase 9 close | Row 1 | **LMIG-04 acceptance number** — Phase 10 DOC-02 cites verbatim |
| Phase 6 close → Phase 9 close | Row 2 | "Pure migration recovery" |
| Phase 7 close → Phase 9 close | Row 3 | "State-machine + cleanup contribution" |
| Phase 8 close → Phase 9 close | Row 4 | **"Logging.h macro tower deletion, isolated"** |
```

#### (b) Build-output excerpts — verbatim `pio run` blocks

From `08-MEASUREMENT.md:15-44` (Leonardo) and `:59-88` (Uno): paste the full `Processing leonardo`/`uno` PIO output, then the bullet summary line ("Leonardo Flash: XX.X% (NN / 28,672 bytes used), NNNN bytes free"). Phase 9 copies this format exactly so the table cells are auditable from the raw PIO output.

#### (c) Bench Verification — Chipless Wire-Protocol Validation

Verbatim from `08-MEASUREMENT.md:322-384` (the Severity-band frame coverage table + Sentinel-byte branch coverage + Bench commands + Outcome sections). Phase 9 re-runs the **identical matrix** with two deltas:

1. **Drop the `FIRESTARTER_DEV_ALLOW_PRE_V12=1` prefix** on every command (per RESEARCH.md line 584 — after `3.0.0-dev` ships the env-var is no longer needed; dropping it exercises the SC#3 native-pass path).
2. **The `fw` command's observed output changes** from `OK: FW: 2.0.11-dev:uno, HW: Rev1, Cmd: 0x0b` to `OK: FW: 3.0.0-dev:uno, HW: Rev1, Cmd: 0x0b`. This is the **expected** SC#3 observable.

**Per project memory `[[feedback_always-mirror-uno-leonardo-tests]]`:** every Uno command is paired with a Leonardo run as the control.

#### (d) Phase 8 SC#2/SC#3 UAT carry-over (recommended bundle)

Phase 9 owns Phase 8's pending chip-seated UAT (RESEARCH.md §"Phase 8 UAT Carry-over" lines 612–656). The structure of Phase 8's `## SC#2 Manual Verification Plan` and `## SC#3 Manual Verification Plan` blocks (`08-MEASUREMENT.md:200-227`) is the template — Phase 9 appends the same headed sections with the chip-seated results.

---

## Shared Patterns

### Phase-tagged inline comment voice
**Source:** `serial_comm.py:42`, `:138`, `:400`, `:752`; `hardware_operations.cpp:84`; `uno_rurp_shield.cpp:90`.
**Apply to:** every new Phase 9 inline comment.
**Format:** `// Phase N / <REQ-ID> / <DECISION-ID>: <one-line rationale>` (firmware) or `# Phase N (<REQ-ID>): <rationale>` (host).
**Example pattern in the wild:**
```cpp
// firestarter/src/hardware_operations.cpp:84
// Phase 8 / P-01 / LFW-05: MSG_OK_FW_VERSION stays text-emitted to preserve
// the host's _probe_port bootstrap path, which parses "FW: ..." as text.
```
Phase 9 replaces this comment as part of D-01 (the rationale flips from "stays text" to "inlined, lone text survivor"); use the same voice.

### Commit message style (Henrik's convention)
**Source:** `firestarter` log (`bbf0e0c`, `891108c`, `451756f`, `275522a`).
**Apply to:** every Phase 9 commit (firmware + host).
**Format:** Conventional Commits subject (`<type>(<scope>): <subject>` ≤ 72 chars) + blank line + rationale paragraph(s) + explicit `Changes in this submodule:` enumeration when ≥ 3 files touched. No emojis. No `Co-Authored-By:` line unless the operator requests it (current `firestarter` log has no Claude attribution lines).

### Atomic multi-file commit when symbol callers and definitions are split
**Source:** Phase 8 commits `275522a` (debug_msg_buffer) and `451756f` (dead macros).
**Apply to:** Phase 9 W2 (D-01 inline + D-02 deletion + D-06 version bump must land together).
**Pattern:** Define the deletion edge precisely; verify `pio run -e uno && pio run -e leonardo` builds clean on the staged tree BEFORE committing; commit-then-verify-then-push (no intermediate broken commits).

### Drift-gate / sync workflow for catalog edits
**Source:** Phase 7/8 catalog commits + `08-PATTERNS.md` line 78.
**Apply to:** Phase 9 — NOT NEEDED (no catalog edits in Phase 9). The catalog stays untouched: `MSG_OK_FW_VERSION` (0x03) and `MSG_OK_READY` (0x01) both stay as-is per Claude's Discretion.

### Native-test stub editing
**Source:** `host_stubs_common.inc` (lines 69–170 surviving stubs).
**Apply to:** D-03 trim.
**Convention:** every stub uses `extern "C"`; no-op bodies cast `(void)param;`; 3-line comment paragraphs precede each functional group. Deletion preserves this style for the surviving stubs.

### Project-memory protocols (always-on)
- `[[feedback_always-mirror-uno-leonardo-tests]]` — every Uno bench command paired with a Leonardo run.
- `[[project_leonardo-shield-socket-wonky]]` — if Leonardo readback differs from Uno on Phase 8 SC#3 carry-over, suspect chip contact first.
- `[[feedback_ic-removal-autonomy]]` — chip-swap cycles do not require per-cycle operator confirmation.

---

## No Analog Found

**None.** Phase 9 has zero green-field surface — every touched file maps to a same-file, same-function, or prior-commit analog. This is the expected character of a "final cleanup" phase: it removes infrastructure, it does not introduce any.

---

## Metadata

**Analog search scope:**
- `firestarter/src/`, `firestarter/include/`, `firestarter/test/native/avr/_shared/`
- `firestarter_app/firestarter/`
- `firestarter` git log (`--all --oneline` ≤ 30 commits + targeted `--grep`)
- `.planning/phases/08-*/` for prior PATTERNS/MEASUREMENT shape
- `.planning/phases/06-*/`, `.planning/phases/07-*/` (referenced via 09-RESEARCH.md citations, not re-read here — RESEARCH.md already extracts what Phase 9 needs)

**Files scanned (in-context reads):** 9 (CONTEXT, RESEARCH §1 + §2, VALIDATION, hardware_operations.cpp, dev_tools.cpp, rurp_serial_utils.cpp, uno_rurp_shield.cpp, leonardo_rurp_shield.cpp, logging.h, version.h, firestarter.cpp, host_stubs_common.inc, serial_comm.py §752, 08-MEASUREMENT.md §anchor + §bench, 08-PATTERNS.md §intro). All reads are targeted; no whole-file reload of large files.

**Files not re-read (relied on RESEARCH.md extraction):**
- `firestarter/src/boards/uno_rurp_shield.cpp` lines 246–251 of `rurp_serial_utils.cpp` was read; the rest of board files trusted via RESEARCH.md inventory.
- `firestarter/include/rurp_shield.h:127-128` decls — trusted via RESEARCH.md line 111.
- `firestarter/include/rurp_serial_utils.h:14-17` decls — trusted via RESEARCH.md line 112.

**Pattern extraction date:** 2026-05-19

---

## PATTERN MAPPING COMPLETE

**Phase:** 09 - Delete Old Log Macros + Measure Flash Savings
**Files classified:** 18 (8 firmware deletions + 5 firmware modifications + 20 include-line drops collapsed into the W2 atomic commit + 1 host comment + 1 native-test trim + 1 measurement artifact create)
**Analogs found:** 18 / 18 (every touched file has an in-tree analog)

### Coverage
- Files with exact analog (same file or near-identical idiom): 16
- Files with role-match analog: 2 (leonardo_rurp_shield.cpp `#ifdef SERIAL_DEBUG` stub deletion + firestarter.cpp `setup()` SERIAL_DEBUG block deletion — both rely on the Phase 8 `275522a` atomic-multi-file precedent)
- Files with no analog: 0

### Key Patterns Identified
- `SERIAL_PORT.print(F("...")) ; SERIAL_PORT.println(...) ; SERIAL_PORT.flush();` is the canonical 3-line Arduino emit idiom — already in `_firestarter_log_progmem` (being deleted) and reused inline at `fw_get_version()` per D-01.
- `LOG_OK_ID(MSG_OK_READY)` is a shipped-and-validated 1-line conversion target — same conversion already at `hardware_operations.cpp:42` from Phase 8 commit `ea2a3fb`; `dev_tools.cpp:108/:154` just replays it.
- Phase 8 commit `275522a` is the multi-file SERIAL_DEBUG-block atomic-deletion template — the 4 `#ifdef SERIAL_DEBUG` blocks Phase 9 deletes (firestarter.cpp:38, uno_rurp_shield.cpp:22+:152, leonardo_rurp_shield.cpp:144) MUST land together in W2 per this precedent.
- `08-MEASUREMENT.md` is the structural template for `09-MEASUREMENT.md`: 5-column anchor table extended with the Phase 9 row + 4-delta attribution table + verbatim bench-verification matrix re-run (minus the `FIRESTARTER_DEV_ALLOW_PRE_V12=1` env-prefix per RESEARCH.md line 584) + Phase 8 SC#2/SC#3 chip-seated UAT carry-over sections.

### File Created
`.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md`

### Most Important Pattern
**Phase 9 ships zero new code.** Every change is a deletion or a relocation of an already-shipped idiom — the 3-line Arduino serial-print at `_firestarter_log_progmem:23-28` migrates inline to `fw_get_version()`, the `LOG_OK_ID(MSG_OK_READY)` conversion from Phase 8 `ea2a3fb` replays at two `dev_tools.cpp` sites, and the multi-file SERIAL_DEBUG atomic-deletion template from Phase 8 `275522a` is reused for the four `#ifdef SERIAL_DEBUG` blocks. The planner should treat Phase 9 as a "clone-and-delete" pass, not a "design and implement" pass.
