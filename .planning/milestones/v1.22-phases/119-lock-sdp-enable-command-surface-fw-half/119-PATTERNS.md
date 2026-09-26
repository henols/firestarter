# Phase 119: LOCK — SDP-enable + command surface (FW half) - Pattern Map

**Mapped:** 2026-07-28
**Files analyzed:** 21 (13 modified, 8 new)
**Analogs found:** 20 / 21
**Repos:** firmware `firestarter/` @ `v1.22-…` (branch verified), host `firestarter_app/` @ `v1.22-…` (branch verified), meta `/workspaces`

> Every excerpt below was read from live source in this session. Line numbers are live, not
> transcribed from RESEARCH.md.

---

## File Classification

### Firmware — production C++ (`firestarter/`)

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `include/firestarter.h` (MOD — `CMD_SDP_UNLOCK 9`, `CMD_SDP_LOCK 10`, `is_memory_cmd()`) | config / header predicate | request-response (admission) | same file `:34-51` (CMD block) + `include/operation_utils.h:41-51` (`static inline` precedent) | exact |
| `src/firestarter.cpp` (MOD — guard site, 2 new `case` arms) | dispatcher | request-response | same file `:76-95` (guard) + `:212-220` (`CMD_ERASE` case arm) | exact (self-analog) |
| `src/operation_utils.cpp` (MOD — NULL-`main` refusal at `:83`) | middleware / op layer | event-driven (state machine) | `src/eprom_operations.cpp:34-41` (`MSG_ERR_NOT_SUPPORTED` refusal shape) | role-match |
| `src/eprom_operations.cpp` (MOD — `eprom_sdp_lock` / `eprom_sdp_unlock`) | controller / command entry | request-response | same file `:34-41` `eprom_erase` | exact |
| `src/proms/eeprom_28c.cpp` (MOD — `EEPROM_SDP_ENABLE[3]`, lock/unlock ops, shared bracket helper, `configure_eeprom28c` arms, page-load tracker) | service / protocol handler | batch + transform (bus stream emission) | same file `:108-130` (table), `:222-238` (emitter), `:296-384` (bracket), `:132-145` (switch) | exact (self-analog) |

### Firmware — build + CI

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `platformio.ini` (NEW `[env:native_nodevtools]`) | config | — | same file `[env:native]` `:69-156` | exact |
| `.github/workflows/build.yml` (MOD — one new step) | config / CI | — | same file `:90-91` ("Run native unit tests") | exact |

### Firmware — native (Unity) tests

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `test/native/avr/test_cmd_admission/test_cmd_admission.cpp` (NEW) | test (truth table) | transform (pure predicate) | `test/native/avr/test_dispatch/test_configure_memory.cpp` | role-match |
| `test/native/avr/test_cmd_admission/host_stubs.cpp` (NEW) | test stub | — | `test/native/avr/test_dispatch/host_stubs.cpp` (35 lines, pure pass-through) | **exact** |
| `test/native/avr/test_cmd_admission/avr/pgmspace.h` (NEW, if needed) | test shim | — | `test/native/avr/test_dispatch/avr/pgmspace.h` (67 lines) | **exact — copy verbatim** |
| `test/native/avr/_shared/sdp_expected.h` (MOD — 4 × `SDP_FIXED_LOCK_*`) | test fixture / golden store | — | same file `:124+` (`SDP_SHIPPED_*` / `SDP_FIXED_*` arrays) | exact |
| `test/native/avr/test_sdp_harness/test_sdp_harness.cpp` (MOD — 3-way identity + distinctness) | test (invariant guard) | — | same file `:291-311` (2-way identity), `:325-330+` (FIX-05 guards), `:152-159` (`sdp_tables_identical`) | exact |
| `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (MOD — lock stream cases, no-payload, budget, `micros()` queue) | test (golden trace) | — | same file `:212-216` (micros mock), `:248-258` (handle factory) | exact |
| `test/native/avr/test_dispatch/test_configure_memory.cpp` (MOD — cmd 9/10 arms, never-NULL-main invariant) | test (dispatch) | — | same file `:151-176` (`_sets_operation` assertion pair) | exact |

### Host (`firestarter_app/`) — generated code + source-scanning gates ONLY

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tools/check_is_memory_cmd_no_ifdef.py` (NEW) | utility / gate | file-I/O (source scan) | `tools/check_no_log_in_sdp_window.py` (402 lines) | **exact — brace-matched C++ scan + env seam** |
| `tests/test_check_is_memory_cmd_no_ifdef.py` (NEW) | test | file-I/O (subprocess) | `tests/test_check_no_log_in_sdp_window.py` (321 lines) | exact |
| `tests/fixtures/planted_ifdef_in_predicate.h` (NEW) | test fixture | — | `tests/fixtures/planted_log_in_window.cpp` (68 lines) | exact |
| `tools/check_no_log_in_sdp_window.py` (MOD — append emit anchor) | utility / gate | file-I/O | same file `_EMIT_ANCHOR_PATTERNS` (append-only by contract) | exact |
| `tests/test_check_no_log_in_sdp_window.py` + fixture (MOD — repair) | test | — | same files | exact |
| `tests/test_sdp_table_parity.py` (MOD — optional `EEPROM_SDP_ENABLE` leg) | test | file-I/O | same file `:117-125` (`_extract_byte_flip_pairs`) | exact |
| `firestarter/messages.py` (REGEN — **never hand-edit**) | generated | — | — | n/a (codegen) |

### Meta-repo

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tools/catalog/messages.toml` (MOD — 2 new INFO ids) | config (canonical catalog) | — | same file `:274-292` (118's `MSG_INFO_SDP_UNLOCK` pair) | exact |
| `.planning/phases/119-…/119-MEASUREMENT.md` (NEW) | doc | — | `118-MEASUREMENT.md` (§1..§7 + Disposition) | exact |
| `.planning/phases/119-…/119-NONREGRESSION.md` (NEW) | doc | — | `118-NONREGRESSION.md` (§1..§8 + Sweep summary) | exact |

---

## ⚠ Open Question 1 is NOT resolved — analogs recorded for BOTH placements

RESEARCH.md F-F leaves one blocking choice. **Both analogs are captured here so the planner can
commit either way without re-searching.** Note F-F Consequence 1 already forces one half of the
answer independently: `[env:native]`'s `build_src_filter` compiles **only** `src/proms/`,
`src/boards/rurp_serial_utils.cpp` and `src/json_parser.c` (verified `platformio.ini:155`), so
`is_memory_cmd()` **must be header-inline** to be natively linkable regardless of which option is
picked for D-06's guard.

### Option (a) — RECOMMENDED: widen `build_src_filter` with `+<operation_utils.cpp>`

**Analog for the filter line** — `firestarter/platformio.ini:142-156`:

```ini
; Phase 12 Wave 1: pull in ONLY src/proms/*.cpp from the firmware tree so
; configure_memory() and the configure_*() handlers link into the host
; test binary. AVR-only sources (src/boards/*.cpp, src/dev_tools.cpp,
; src/eprom_operations.cpp, src/logging.c) are excluded; ...
; Phase 44 Plan 02: include json_parser.c for test_read_timing suite
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>
test_build_src = yes
```

Precedent: the filter has already been widened twice (`rurp_serial_utils.cpp` for Phase 6,
`json_parser.c` for Phase 44), each time with an in-file comment naming the consuming suite. Copy
that comment discipline.

**Analog for the ArduinoFake risk this option carries** — `test_sdp_harness.cpp:75-90`. Adding
`operation_utils.cpp` pulls `millis`/`delay` into **all 16** suite binaries; only 4 mock them
today. The load-bearing mock block to replicate in any suite that aborts:

```cpp
    /* REQUIRED by D-05: ... ArduinoFake ABORTS (SIGABRT) on any unmocked
     * virtual — this reads exactly like the D-13 Unity-teardown flake, but a
     * SIGABRT in a NEW suite is this (Pitfall 3), not that. Do not remove
     * these as "unused" — they are load-bearing. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();
    When(Method(ArduinoFake(), delay)).AlwaysReturn();
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);
```

### Option (b) — FALLBACK: `static inline bool op_refuse_if_no_main(handle)` in `operation_utils.h`

**Analog** — `firestarter/include/operation_utils.h:41-51`, the existing `static inline`
header-helper precedent (the only `operation_utils` symbols `src/proms/` links today):

```c
static inline void set_operation_in_progress(firestarter_handle_t* handle) {
    handle->operation_state |= OPERATION_IN_PROGRESS;
}

static inline bool is_operation_in_progress(const firestarter_handle_t* handle) {
    return (handle->operation_state & OPERATION_IN_PROGRESS) == OPERATION_IN_PROGRESS;
}
```

Under (b) the one-line call site at `operation_utils.cpp:89` stays natively unproven and D-08's
cmd × protocol enumeration is **prose, not a test** — record that explicitly if taken.

---

## Pattern Assignments

### `include/firestarter.h` — `CMD_SDP_UNLOCK 9` / `CMD_SDP_LOCK 10` + `is_memory_cmd()`

**Analog:** same file, `:34-51`.

**Command-define block** (`firestarter.h:34-51`) — note slots 9/10 are the gap between
`CMD_DEV_REGISTER 8` and `CMD_READ_VPP 11`, and that the two `CMD_DEV_*` defines are themselves
`#ifdef`-guarded (F-C: the truth-table test therefore **must** use numeric `7`/`8`):

```c
#define CMD_IDLE 0
#define CMD_READ 1
#define CMD_WRITE 2
#define CMD_ERASE 3
#define CMD_BLANK_CHECK 4
#define CMD_CHECK_CHIP_ID 5
#define CMD_VERIFY 6

#ifdef DEV_TOOLS
#define CMD_DEV_ADDRESS 7
#define CMD_DEV_REGISTER 8
#endif

#define CMD_READ_VPP 11
```

**Comment-block pattern for a deliberate, milestone-scoped addition** (`firestarter.h:70-76`) —
`FLAG_SKIP_SDP_UNLOCK` is 118's precedent for "firmware-only this phase, host surface in Phase 120".
Copy this shape for the two new `CMD_*`:

```c
// Declines the SDP (Software Data Protection) auto-unlock command sequence
// on protocol 0x0D (eeprom_28c.cpp), so a write against an SDP-protected
// AT28C part will not land -- an honest tradeoff reported via
// MSG_WARN_SDP_UNLOCK_SKIPPED rather than a silent no-op. Firmware-only in
// this milestone phase (v1.22 Phase 118 OBS-02): the host CLI surface
// (--skip-sdp-unlock / constants.py) arrives in Phase 120 HOST-03.
#define FLAG_SKIP_SDP_UNLOCK 0x100
```

**`static inline` predicate shape:** copy `operation_utils.h:41-51` (excerpt above). D-01's set is
`{CMD_READ, CMD_WRITE, CMD_ERASE, CMD_BLANK_CHECK, CMD_CHECK_CHIP_ID, CMD_VERIFY, CMD_SDP_UNLOCK,
CMD_SDP_LOCK}` with **no `#ifdef` inside the body** (D-02).

---

### `src/firestarter.cpp` — the admission guard and two new `case` arms

**Analog:** same file, `:76-95` (the guard being replaced) and `:212-220` (the arm shape to copy).

**Guard site as it stands today** (`firestarter.cpp:73-91`) — the `#ifdef DEV_TOOLS` wrapper around
`:79` is **mandatory today**, not gratuitous, because `CMD_DEV_ADDRESS` does not exist in a release
build (F-C). `is_memory_cmd()` removes the `#ifdef` by not naming those symbols at all:

```cpp
    if (handle->cmd < CMD_READ_VPP) {
        json_parse(handle->data_buffer, tokens, token_count, handle);
#ifdef DEV_TOOLS
        if (handle->cmd < CMD_DEV_ADDRESS) {
#endif
            LOG_DEBUG_ID_SUB_U8(DBG_FLAG_FORCE, is_flag_set(FLAG_FORCE));
            /* ...4 more flag debug lines... */
            if (!op_execute_function(configure_memory, handle)) {
                LOG_ERROR_ID(MSG_ERR_SETUP);
                return false;
            }
#ifdef DEV_TOOLS
        } else {
            LOG_DEBUG_ID_SUB_U8(DBG_FLAG_OUTPUT_EN, is_flag_set(FLAG_OUTPUT_ENABLE));
            LOG_DEBUG_ID_SUB_U8(DBG_FLAG_CHIP_EN, is_flag_set(FLAG_CHIP_ENABLE));
        }
#endif
    } else if (handle->cmd == CMD_CONFIG) { /* ... */ }
```

**⚠ Second live site to check:** `firestarter.cpp:124` carries an independent
`handle->cmd > CMD_IDLE && handle->cmd < CMD_READ_VPP` range test gating three debug lines. It is
the same ordinal-range idiom and neither CONTEXT.md nor RESEARCH.md names it. Decide explicitly
whether it also becomes `is_memory_cmd()`; do not let a verifier find it.

**`case` arm pattern** (`firestarter.cpp:207-215`) — `CMD_ERASE` / `CMD_CHECK_CHIP_ID` are the
payload-free precedent; the new arms are two more of these, **outside** any `#ifdef`:

```cpp
        case CMD_ERASE:
            finished = eprom_erase(&handle);
            break;
        case CMD_BLANK_CHECK:
            finished = eprom_blank_check(&handle);
            break;
        case CMD_CHECK_CHIP_ID:
            finished = eprom_check_chip_id(&handle);
            break;
```

**`default:` arm to preserve** (`firestarter.cpp:243-246`) — this is what cmd 7/8 fall to in a
release build after D-01, and (per F-B2) what `CMD_IDLE` does *not* reach:

```cpp
        default:
            LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, handle.cmd);
            finished = true;
            break;
```

---

### `src/eprom_operations.cpp` — `eprom_sdp_lock` / `eprom_sdp_unlock`

**Analog:** same file, `:34-41` (`eprom_erase`) — the precondition-refusal + single-step wrapper
shape, and the tree's existing `MSG_ERR_NOT_SUPPORTED` caller.

**Imports pattern** (`eprom_operations.cpp:8-14`) — no new include is needed:

```cpp
#include "eprom_operations.h"

#include "firestarter.h"
#include "logging_id.h"
#include "messages.h"
#include "operation_utils.h"
#include "rurp_shield.h"
```

**Core pattern** (`eprom_operations.cpp:34-50`) — note `return true` means *finished*, and the
`!op_execute_simple_operation(handle)` inversion:

```cpp
bool eprom_erase(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_ERASE_PROM);
    if (!is_flag_set(FLAG_CAN_ERASE)) {
        LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED);
        return true;
    }
    return !op_execute_simple_operation(handle);
}

bool eprom_check_chip_id(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CHECK_CHIP_ID_OP);
    if (handle->chip_id == 0) {
        LOG_ERROR_ID(MSG_ERR_NO_CHIP_ID);
        return true;
    }
    return !op_execute_simple_operation(handle);
}
```

The simplest new entry point is `eprom_blank_check`'s shape (`:52-55`) — a bare
`LOG_DEBUG_ID_SUB` + `return !op_execute_simple_operation(handle);` — since D-06 moves the refusal
to the op layer and no per-command precondition flag exists for SDP.

---

### `src/operation_utils.cpp` — the ONE generic NULL-`main` refusal (D-06/D-07)

**Analog:** the refusal *idiom* is `eprom_operations.cpp:36-39` above; the *site* is a self-analog.

**Site as it stands** (`operation_utils.cpp:62-90`) — `:83`'s bare `return false` is the
phantom-success mechanism. Every caller inverts it, so the command reports **finished** with
`response_code` left at the `RESPONSE_CODE_OK` `loop()` set at `firestarter.cpp:196`, and emits
nothing at all:

```cpp
bool op_execute_stateful_operation(bool (*callback)(firestarter_handle_t* handle), firestarter_handle_t* handle) {
    if (handle->firestarter_operation_main) {
        if (is_all_operations_done()) {
            if (op_get_message(handle) == OP_MSG_INCOMPLETE) {
                return true;  // Not finished yet, waiting for final ACK
            }
            return false;  // Received final ACK (or junk), command is finished.
        }

        int res = _execute_operation_house_keeping(handle);
        if (res != CONTINUE) {
            return res == RETURN;
        }
        if (is_operation_started(MAIN)) {
            return callback(handle);
        }
        return true;
    }
    return false;          // <-- :83  PHANTOM SUCCESS. Refusal goes HERE.
}
```

**Refusal to insert** (idiom copied verbatim from `eprom_operations.cpp:37`, plus the
`response_code` store that `configure_not_implemented` and `eeprom28c_wait_for_page_write` use):

```cpp
    LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED);          /* 0xA5 — already exists, messages.toml:419 */
    handle->response_code = RESPONSE_CODE_ERROR;
    return false;
```

**Response-code store analog** (`eeprom_28c.cpp:480-483`):

```cpp
        LOG_ERROR_ID_BYTES(MSG_ERR_EEPROM_TIMEOUT, _b, 5);
    }
    handle->response_code = RESPONSE_CODE_ERROR;
    return false;
```

**Scoping evidence to cite, not re-derive:** `op_execute_simple_operation` is a thin wrapper
(`operation_utils.cpp:58-60`) and `_single_step_operation_callback` (`:271-295`) has exactly one
command-specific branch — `if (handle->cmd == CMD_BLANK_CHECK)` at `:281` — which simply does not
fire for cmd 9/10. The wrapper is otherwise generic.

---

### `src/proms/eeprom_28c.cpp` — the biggest surface

**Analog:** the file is its own best analog on all five sub-changes.

#### (1) `EEPROM_SDP_ENABLE[3]` — copy `EEPROM_SDP_DISABLE`'s shape verbatim

`eeprom_28c.cpp:103-124`. The `extern` line at `:122` is **load-bearing** (it grants external
linkage so the test guard can pin the *production* array); the comment block is the rationale-comment
format D-10 wants:

```cpp
// AT28C SDP disable: 6-write sequence to magic addresses.
// D-10: kept 0x0D-local (not driving the byte-identical
// FLASH_DISABLE_WRITE_PROTECTION from the FIX-04-frozen flash_utils.h)
// ... External linkage is granted here (FIX-05
// preparation) so that guard can read this PRODUCTION array directly rather
// than a transcribed test-local copy; in C++ a const array at namespace
// scope has internal linkage unless a prior declaration with external
// linkage is visible, so the extern declaration below is load-bearing.
extern const byte_flip_t EEPROM_SDP_DISABLE[6];
const byte_flip_t EEPROM_SDP_DISABLE[6] = {
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x80},
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0x20},
};
```

**Forward-declaration block to extend** (`eeprom_28c.cpp:96-101`) — new file-`static` ops go here;
`eeprom_28c.h` exports only `configure_eeprom28c`, so **no header change is needed** (F-Q), which
keeps the host gates' scanned surface stable:

```cpp
void eeprom28c_write_init(firestarter_handle_t* handle);
void eeprom28c_write_execute(firestarter_handle_t* handle);
static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length);
static void eeprom28c_wait_for_sdp_completion(firestarter_handle_t* handle);
static bool eeprom28c_wait_for_page_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected);
static bool eeprom28c_verify_page_readback(firestarter_handle_t* handle, uint32_t first_index, uint32_t last_index);
```

#### (2) `configure_eeprom28c`'s new arms

`eeprom_28c.cpp:126-139` — the switch D-05 constrains. `CMD_READ` and `CMD_VERIFY` **reach this
switch and fall through it**, keeping the generic mains `configure_memory` pre-set. A `default:`
arm here refuses them on all 84 chips. If any arm is added, spell it
`case CMD_ERASE: case CMD_CHECK_CHIP_ID:` — never `default:`:

```cpp
void configure_eeprom28c(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_EEPROM_28C);
    // AT28C page write timing requires fast consecutive writes; no pulse delay needed
    handle->pulse_delay = 0;
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eeprom28c_write_init;
            handle->firestarter_operation_main = eeprom28c_write_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
    }
}
```

**Why a `default:` here is fatal** — the pre-set at `src/proms/memory.cpp:44-58`, which runs
*before* the protocol chain:

```cpp
void configure_memory(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_MEMORY);
    handle->firestarter_operation_init = NULL;
    handle->firestarter_operation_main = NULL;
    handle->firestarter_operation_end = NULL;

    switch (handle->cmd) {
        case CMD_READ:   handle->firestarter_operation_main = memory_read_execute;   break;
        case CMD_WRITE:  handle->firestarter_operation_main = memory_write_execute;  break;
        case CMD_VERIFY: handle->firestarter_operation_main = memory_verify_execute; break;
    }
    /* ... pointers ... */
    mem_util_set_address(handle, 0);              /* :68 — writes registers! */
    if (handle->protocol == PROTO_FLASH_INTEL) { configure_flash_intel(handle); return; }
    if (handle->protocol == PROTO_EEPROM_PARALLEL) { configure_eeprom28c(handle); return; }
    /* ... chain ends at configure_not_implemented(handle); :113 */
}
```

#### (3) The shared emitter — reuse, do NOT touch its body

`eeprom_28c.cpp:214-230`. Its own comment at `:212-221` states the hard constraint: nothing
bus-visible beyond `rurp_set_data_output()` and the `set_data` loop, and **no `LOG_` call**:

```cpp
static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length) {
    rurp_set_data_output();
    for (size_t i = 0; i < length; i++) {
        handle->firestarter_set_data(handle, sequence[i].address, sequence[i].byte);
    }
}
```

Its comment at `:206-210` already names this phase as an intended consumer: *"and Phase 119 (a
standalone CMD_SDP_LOCK/CMD_SDP_UNLOCK arm driving it with a different table and no payload)"*.

#### (4) The `micros()` bracket + t_BLC budget check — D-14's factoring target

`eeprom_28c.cpp:296-384` (the `!is_flag_set(FLAG_SKIP_SDP_UNLOCK)` branch). The exact code to
factor into a shared helper:

```cpp
        size_t sdp_seq_len = sizeof(EEPROM_SDP_DISABLE) / sizeof(EEPROM_SDP_DISABLE[0]);

        LOG_ID(MSG_INFO_SDP_UNLOCK);                       /* bare LOG_ID on an INFO id — 118 D-01 */

        uint32_t sdp_emit_start_us = micros();
        eeprom28c_emit_command_sequence(handle, EEPROM_SDP_DISABLE, sdp_seq_len);
        uint32_t sdp_emit_us = (uint32_t)(micros() - sdp_emit_start_us);

        LOG_ID_U32(MSG_INFO_SDP_UNLOCK_DONE_US, sdp_emit_us);

        uint32_t sdp_tblc_budget_us = (uint32_t)sdp_seq_len * AT28C_TBLC_MAX_US;
        if (sdp_emit_us > sdp_tblc_budget_us) {
            LOG_WARN_ID_U32(MSG_WARN_SDP_TBLC_EXCEEDED, sdp_emit_us);   /* no response_code write */
        }

        eeprom28c_wait_for_sdp_completion(handle);
    } else {
        LOG_WARN_ID(MSG_WARN_SDP_UNLOCK_SKIPPED);
    }
```

⚠ **The report lines are unconditional `LOG_ID` / `LOG_ID_U32` on INFO-band ids, NOT the
`FLAG_VERBOSE`-gated `LOG_INFO_ID*` family** (see the 18-line rationale at `:304-321`). These are
the tree's only such call sites. The lock's pair must use the same spelling or a default
`dev sdp enable` goes silent.

⚠ **Moving the emit call into the helper breaks the host gate** — see Shared Pattern 4 below.

#### (5) The lock's own wait — D-11 declines reusing this

`eeprom_28c.cpp:260-273`. It is `delay(t_WC)` **plus** up to 32 reads through
`firestarter_get_data`, and a `memory_get_data` read folds `READ_FLAG` into
`DIP32_28C512_EEPROM`'s CONTROL bit — which is why the lock uses `delay(AT28C_TWC_MAX_MS)` alone:

```cpp
static void eeprom28c_wait_for_sdp_completion(firestarter_handle_t* handle) {
    delay(AT28C_TWC_MAX_MS);
    uint8_t previous = handle->firestarter_get_data(handle, EEPROM28C_TOGGLE_POLL_ADDRESS);
    for (uint8_t j = 0; j < AT28C_TOGGLE_POLL_MAX_READS; j++) {
        delayMicroseconds(10);
        uint8_t observed = handle->firestarter_get_data(handle, EEPROM28C_TOGGLE_POLL_ADDRESS);
        if ((observed & AT28C_DQ6_TOGGLE_MASK) == (previous & AT28C_DQ6_TOGGLE_MASK)) {
            return;
        }
        previous = observed;
    }
}
```

Constants: `AT28C_TWC_MAX_MS 10` (`:42`), `AT28C_TBLC_MAX_US 100` (`:58`) — both `#define`s local to
this `.cpp`, **not** exported by `eeprom_28c.h`. A test must mirror the value as a named local with
an explicit `eeprom_28c.cpp:54` citation (existing Case 11 does this).

#### (6) D-16's worst-case page-load tracker

`eeprom_28c.cpp:417-470`. The per-byte loop is `:446-469`; the existing gh#11 citation comment at
`:431-445` is the wording to reuse (it already frames gh#11 as a **conflation** bug, not a
sampling-rate bug):

```cpp
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, data);

        bool page_end = ((address + 1) % PAGE_SIZE) == 0;
        bool last_byte = (i == handle->data_size - 1);
        if (page_end || last_byte) {
            if (!eeprom28c_wait_for_page_write(handle, address, data)) {
                return;
            }
            if (!eeprom28c_verify_page_readback(handle, window_start, i)) {
                return;
            }
            window_start = i + 1;
        }
    }
```

The single trailing report line goes **after** this loop. Note both early `return`s — a tracker
threaded as a file-static survives them; a report line placed only at the loop's normal exit does
not fire on a failed write.

---

### `platformio.ini` — `[env:native_nodevtools]`

**Analog:** `[env:native]` at `:69-156`. Copy its shape **exactly**, with three deliberate changes.

**The `-D DEV_TOOLS` leak being worked around** (`platformio.ini:18-27`) — it lives in the shared
`[env]` block, inherited by all three AVR envs **and** `native`:

```ini
[env]
monitor_speed = 250000

build_flags = 
	-D MONITOR_SPEED=${env.monitor_speed}
	-D HARDWARE_REVISION
	-D DEV_TOOLS
```

**The two parallel 16-entry lists** (`:102-118` `test_filter`, `:123-138` `-I`) — a suite is
invisible until it appears in **both**. Both lists gain `native/avr/test_cmd_admission` in
`[env:native]` *and* in the new env:

```ini
test_filter =
	native/avr/test_dispatch
	native/avr/test_not_implemented
	; ... 12 more ...
	native/avr/test_sdp_harness
	native/avr/test_eeprom28c_sdp
build_flags =
	${env.build_flags}
	-std=gnu++17
	-I include
	-I test/native/avr/test_dispatch
	; ... 15 more -I lines ...
	-D RURP_BOARD_NAME=\"native\"
lib_deps =
	fabiobatsilva/ArduinoFake@^0.4.0
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>
test_build_src = yes
```

**The three deliberate changes for the new env** (F-N, empirically validated in RESEARCH's
throwaway experiment):
1. `build_flags` must **not** begin `${env.build_flags}` — spell out `-D MONITOR_SPEED=250000` and
   `-D HARDWARE_REVISION` instead. ⚠ `-D HARDWARE_REVISION` is load-bearing:
   `_shared/host_stubs_common.inc:208-224` gates four hardware-revision stubs on it.
2. Duplicate the whole `test_filter` **and** the whole `-I` list (RESEARCH resolved the discretion
   item in favour of the *full* filter: zero porting cost, ~52 s CI).
3. ⚠ **Do not add the new env to `default_envs`** (`:16`) — `pio run` would try to link a
   `main()`-less target. The existing comment at `:12-15` explains exactly this.

---

### `.github/workflows/build.yml` — the second native test step

**Analog:** `build.yml:85-91`. Add one sibling step immediately after:

```yaml
      # Phase 6 WR-01: run the native Unity suite (host-side, no AVR board
      # required) in CI. test_messages pins the CRC8 polynomial + the exact
      # wire-frame byte sequence — a silent refactor that breaks the locked
      # frame contract from CONTEXT D-01..D-04 must fail CI, not slip
      # through because CI only built and never executed the tests.
      - name: Run native unit tests
        run: pio test -e native
```

Note the workflow's `on:` triggers are `main` only, so it will not fire on the milestone branch —
the in-phase proof is the local run, exactly as with `catalog-sync-check.yml`.

---

### `test/native/avr/test_cmd_admission/` (NEW suite)

**Analog:** `test/native/avr/test_dispatch/` — the closest match by role (a pure,
side-effect-free dispatch/predicate assertion suite) and the smallest.

**`host_stubs.cpp` — copy near-verbatim** (`test_dispatch/host_stubs.cpp`, 35 lines, a pure
pass-through to the shared include; only the header comment's suite name changes):

```cpp
#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

#include "../_shared/host_stubs_common.inc"
```

**`avr/pgmspace.h` — copy verbatim** from `test_dispatch/avr/pgmspace.h` (67 lines: `PROGMEM`,
`PSTR`, `PGM_P`, `pgm_read_*`, `strncmp_P`, all `#ifndef`-guarded).

**Test-body pattern** (`test_configure_memory.cpp:36-62, 178-204`):

```cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;

void setUp(void) {
    ArduinoFakeReset();
    /* Stub Serial.write and Serial.flush so that LOG_ERROR_ID_* calls in the
     * error dispatch path ... don't abort. */
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}

void tearDown(void) {}

/* ... void test_xxx(void) { ... TEST_ASSERT_*_MESSAGE(...); } ... */

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_protocol_0x06_dispatches_nor_unlock);
    /* ... */
    return UNITY_END();
}
```

⚠ **F-C constraint for this suite specifically:** the truth table must **not** name
`CMD_DEV_ADDRESS` / `CMD_DEV_REGISTER` — those macros do not exist in `native_nodevtools`. Use
numeric literals `7` and `8` with a comment citing `firestarter.h:42-45`. The host's
`tests/test_revision_constants_parity.py:110-112` already carries the same idiom and the same
reason — quote it.

**Never-NULL-main invariant assertion pattern** (`test_configure_memory.cpp:151-158`) — the shape
for both the new cmd 9/10 dispatch cases and LOCK-04's "READ/WRITE/VERIFY are never NULL-main"
positive invariant:

```cpp
void test_5v_page_check_chip_id_0x05_sets_operation(void) {
    firestarter_handle_t h = make_handle(0x05, 0, CMD_CHECK_CHIP_ID);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "CMD_CHECK_CHIP_ID on 0x05 must not error");
    TEST_ASSERT_NOT_NULL_MESSAGE(h.firestarter_operation_main,
        "CMD_CHECK_CHIP_ID on 0x05 must set a non-NULL operation_main");
}
```

⚠ `firestarter/CLAUDE.md`'s "Reuse pattern for future native tests" claims *"The `[env:native]`
configuration in `platformio.ini` does not need changes for new suites."* **That is stale** — the
positive `test_filter` allowlist (added later, see `platformio.ini:86-87`) makes it false. Plan for
the `platformio.ini` edit and consider correcting `CLAUDE.md`.

---

### `test/native/avr/_shared/sdp_expected.h` — `SDP_FIXED_LOCK_*` goldens

**Analog:** same file. Storage shape (`:124+`): a `static const sdp_strobe_t NAME[]` of
`{kind, pin, value}` triples plus `#define NAME_LEN (int)(sizeof(NAME)/sizeof(NAME[0]))`.

**Comparators to reuse — never re-implement** (`sdp_expected.h:64-122`):

```cpp
/* Never counts anything — D-06's anti-pattern list forbids it —
 * every comparison is positional. */
static int  sdp_first_divergence(const sdp_strobe_t* expected, int expected_len);
static void sdp_assert_stream_equals(const sdp_strobe_t* expected, int expected_len, const char* ctx);
/* Snapshot the LIVE recorded stream ... since clear_strobes() wipes the
 * recorder between drives. */
static int  sdp_snapshot(sdp_strobe_t* out, int max_len);
```

**Authoring discipline, stated in the file's own header** (`:12-16`): *"Every literal array below
was authored EMPIRICALLY from a recorded dump of real production code (never hand-derived)"*. The
dump helper is `test_sdp_harness.cpp:167-178` behind `#ifdef SDP_TRACE_DUMP`, and
`pio test` swallows `printf` — run `.pio/build/native/firestarter_native` directly.

⚠ **This file's whole-file blob SHA necessarily changes** (D-10), so 117/118's whole-file-SHA
identity shorthand no longer applies. Shift to **per-array byte-identity of the pre-existing
arrays** and say so in `119-NONREGRESSION.md`. The other two `_shared/` files
(`host_stubs_common.inc`, `sdp_bus_config.h`) should stay blob-SHA-identical — assert that.

---

### `test/native/avr/test_sdp_harness/test_sdp_harness.cpp` — the three-way identity guard

**Analog:** the two-way leg **already exists** at `:297-311`. The new guard belongs immediately
beside it and beside `test_fix05_terminal_byte_and_table_identity_guards` (`:325+`).

**The existing two-way leg, with the comment that constrains what may be added**
(`test_sdp_harness.cpp:291-311`):

```cpp
/* LOCK-05 finding, recorded as a case (not prose): FLASH_ENABLE_WRITE_PROTECTION
 * and FLASH_ENABLE_WRITE are byte-identical tables in flash_utils.h (Atmel
 * doc0270 section 19 note 2 -- this duplication is datasheet-correct).
 * Phase 119 LOCK-05 requires the duplication be PRESERVED, not deduplicated.
 * A trace-based negative between THESE TWO SPECIFIC tables is therefore
 * impossible by construction -- a later editor must not try to add one. */
void test_lock05_enable_write_and_write_protection_identical(void) {
    firestarter_handle_t h1 = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h1, FLASH_ENABLE_WRITE_PROTECTION,
        sizeof(FLASH_ENABLE_WRITE_PROTECTION) / sizeof(FLASH_ENABLE_WRITE_PROTECTION[0]), 0x00);
    sdp_strobe_t snap[32];
    int len = sdp_snapshot(snap, 32);

    firestarter_handle_t h2 = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h2, FLASH_ENABLE_WRITE, sizeof(FLASH_ENABLE_WRITE) / sizeof(FLASH_ENABLE_WRITE[0]), 0x00);

    TEST_ASSERT_EQUAL_MESSAGE(-1, sdp_first_divergence(snap, len),
        "LOCK-05: FLASH_ENABLE_WRITE_PROTECTION and FLASH_ENABLE_WRITE are byte-identical tables and "
        "must therefore produce element-wise identical streams");
    sdp_assert_stream_equals(snap, len, "LOCK-05: identity between the two 3-write tables");
}
```

**Table-comparison helper to reuse** (`:152-159`) — positional only, no counting:

```cpp
static bool sdp_tables_identical(const byte_flip_t* a, const byte_flip_t* b, size_t len) {
    for (size_t i = 0; i < len; i++) {
        if (a[i].address != b[i].address || a[i].byte != b[i].byte) {
            return false;
        }
    }
    return true;
}
```

**Production-array pinning pattern** (`:43-48`) — the extern that makes D-10's guard read the real
array, not a transcription. Add the same three lines for `EEPROM_SDP_ENABLE[3]`:

```cpp
/* FIX-05 (D-11, plan 117-04): EEPROM_SDP_DISABLE is DEFINED in
 * src/proms/eeprom_28c.cpp, which [env:native] links into every test binary
 * (build_src_filter = +<proms/>, test_build_src = yes). Plan 117-02 granted
 * this array external linkage ... so this guard can pin the PRODUCTION table
 * directly, not a transcription. */
extern const byte_flip_t EEPROM_SDP_DISABLE[6];
```

**Exact-divergence-index discipline** (`:280-289`) — the pattern for the lock's negatives. Assert
the **index**, never `!= -1` alone:

```cpp
void test_negativeB_lock_table_swapped_for_write_prefix(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive(&h, FLASH_ENABLE_WRITE_PROTECTION, /* len */, 0x00);

    int div = sdp_first_divergence(SDP_SHIPPED_DIP28_28C256, SDP_SHIPPED_DIP28_28C256_LEN);
    TEST_ASSERT_EQUAL_MESSAGE(26, div,
        "Negative B: three-write lock/write-prefix table must diverge from the six-write unlock "
        "stream at index 26 -- write #3's payload byte (0xA0 vs 0x80)");
}
```

**Load-bearing drive-order helper** (`:127-145`) — `configure_memory` itself writes registers, so
`reset_register_cache` and `clear_strobes` must both come **after** it:

```cpp
static void drive_reference_emitter(firestarter_handle_t* h, const byte_flip_t* table, size_t len, rurp_register_t ctrl_seed) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, ctrl_seed);
    clear_strobes();
    for (size_t i = 0; i < len; i++) {
        h->firestarter_set_data(h, table[i].address, table[i].byte);
    }
}
```

For driving the **new lock op** natively, substitute `h->firestarter_operation_main(h)` for the loop
(`init`/`end` are NULL by design) after setting `h.cmd = CMD_SDP_LOCK`.

**Distinct-objects assertion precedent:** `test_fix05_terminal_byte_and_table_identity_guards`
(`:325+`) already carries the alias-refactor pointer guard for the unlock table (RESEARCH cites
`:257-260`). Extend that shape to `(const void*)A != (const void*)B` for all three pairs.

---

### `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`

**Analog:** same file. Two specific seams.

**`micros()` mock — the 2-slot parity alternator D-16 breaks** (`:124-138`, `:212-216`):

```cpp
/* Controllable micros() tick source (Plan 118-04's OBS-04 duration bracket:
 * eeprom28c_write_init reads micros() once immediately before
 * eeprom28c_emit_command_sequence's call and once immediately after, so
 * EXACTLY TWO reads occur per write_init drive). Indexed by call count
 * modulo 2 rather than an absolute count ... */
static uint32_t s_micros_ticks[2];
static int      s_micros_call_count;

    When(Method(ArduinoFake(), micros)).AlwaysDo([]() -> unsigned long {
        unsigned long v = s_micros_ticks[s_micros_call_count % 2];
        s_micros_call_count++;
        return v;
    });
```

⚠ D-16's per-byte tracker adds 1–2 `micros()` calls per byte inside `write_execute`, so the parity
model breaks for any case driving both phases. **Upgrade to a scripted queue** (a `std::vector<uint32_t>`
with a monotonic cursor and a documented default-tail value — the file already includes `<vector>`
for `captured_frames` at `:150`), then **explicitly re-verify Cases 11 and 12**. Reset the new state
alongside the existing block at `:218-230`.

**Handle factory with a default-arg extension seam** (`:248-258`) — the pattern for adding a cmd
parameter without churning existing call sites:

```cpp
/* Plan 118-05 (D-08): extra_flags defaults to 0, so every one of cases 1-8's
 * existing make_sdp_handle(row) call sites is byte-for-byte unaffected --
 * no signature churn at those eight sites. */
static firestarter_handle_t make_sdp_handle(const sdp_bus_config_row_t& row, uint32_t extra_flags = 0) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = 0;
    h.mem_size = row.mem_size;
    h.bus_config = row.bus_config;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | extra_flags;
    return h;
}
```

**Frame-id capture for D-12's message-text / frame-id assertions** (`:150-181`) — reuse
`captured_frames` + `sdp_captured_frame_ids()` + `sdp_ids_contains()`; content-order membership,
never a count.

---

### `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` (NEW gate)

**Analog:** `tools/check_no_log_in_sdp_window.py` (402 lines) — an **exact** structural match: a
fail-closed, brace-matched C++ scan with an env-override seam and a committed planted fixture. Copy
its five structural elements.

**1. Env-overridable path constant** (`check_no_log_in_sdp_window.py:92-112`):

```python
_HERE = os.path.dirname(__file__)
_DEFAULT_SDP_SRC = os.path.join(
    _HERE, "..", "..", "firestarter", "src", "proms", "eeprom_28c.cpp"
)

# Env-override seam: lets the paired pytest point this checker at a
# deliberately-violating fixture file (tests/fixtures/planted_log_in_window.cpp)
# without editing the real, clean eeprom_28c.cpp (anti-hollow contract, D-04).
FIRESTARTER_SDP_SRC = os.environ.get("FIRESTARTER_SDP_SRC", _DEFAULT_SDP_SRC)
```

New gate's equivalent: `FIRESTARTER_CMD_ADMISSION_SRC` → `firestarter/include/firestarter.h`.
Fail-closed idiom: a `FIRESTARTER_*_SRC` pointing at a missing file must be an **error**, never a
silent pass.

**2. Definition-only function pattern** (`:115-126`) — ⚠ note it requires the return type to be
literally `void`. `is_memory_cmd()` returns `bool` and is `static inline`, so the new gate needs its
own pattern (e.g. `\bstatic\s+inline\s+bool\s+is_memory_cmd\s*\([^)]*\)\s*\{`). Preserve the
docstring habit of naming which properties are load-bearing:

```python
def _func_def_pattern(func_name: str) -> re.Pattern[str]:
    """Build a function-DEFINITION-only pattern (body-opening `{`), never
    matching a forward-declaration prototype (which ends in `;`).
    ... the trailing `\\{` is what excludes the `;`-terminated forward
    declarations a few lines above each definition in the real file. """
    return re.compile(r"\bvoid\s+" + re.escape(func_name) + r"\s*\([^)]*\)\s*\{")
```

**3. Comment-stripping before the scan** — `_strip_comments` blanks `//` and `/* */` spans
length- and line-preservingly, so a comment naming a forbidden token is never a false positive.
This is directly load-bearing for the new gate: the predicate will carry a rationale comment that
may mention `#ifdef DEV_TOOLS` by name.

**4. Fail-closed `ValueError` with a maintainer-facing fix** (`:271-316`) — every unresolvable
input names the fix rather than passing:

```python
    emitter_body = _find_function_body(cleaned_text, _EMITTER_FUNC_NAME)
    if emitter_body is None:
        raise ValueError(
            f"{_EMITTER_FUNC_NAME}() not found (or not brace-balanced) in "
            "source -- if the emitter was renamed or replaced, add the new "
            "anchor/name for _EMITTER_FUNC_NAME in "
            "check_no_log_in_sdp_window.py rather than deleting this gate"
        )
```

**5. `main()` exit-code + PASS/FAIL output contract** (`:355-398`):

```python
def main() -> int:
    path = FIRESTARTER_SDP_SRC
    if not os.path.isfile(path):
        print(f"ERROR: source file not found: {path}", file=sys.stderr)
        return 1
    # ... read, then:
    try:
        violations, emitter_range, poll_range = scan(source_text)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if violations:
        print(f"FAIL: ...")
        for line_no, macro in violations[:20]:
            print(f"  line {line_no}: {macro}(...)")
        return 1
    print(f"PASS: no logging call in SDP timing window ({path}, {range_desc})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

The new gate must assert **two** things (D-04): (a) the body contains no `#ifdef DEV_TOOLS`, and
(b) it enumerates exactly the eight expected commands.

---

### `firestarter_app/tests/test_check_is_memory_cmd_no_ifdef.py` (NEW)

**Analog:** `tests/test_check_no_log_in_sdp_window.py` (321 lines).

**Subprocess runner + line-derivation helpers** (`:57-85`) — copy both:

```python
_FA_DIR = Path(__file__).parent.parent
_FIXTURE = _FA_DIR / "tests" / "fixtures" / "planted_log_in_window.cpp"


def _run_checker(env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, "tools/check_no_log_in_sdp_window.py"],
        cwd=str(_FA_DIR), capture_output=True, text=True, env=env,
    )


def _line_number_of_marker(text: str, marker: str) -> int:
    """Return the 1-indexed line number of the first line containing
    `marker` ... rather than hardcoding a second literal that a future
    re-plant could silently desync from."""
```

**The load-bearing anti-hollow case** (`:112-140`) — exit code **plus** output content, with the
line number derived from the fixture at test time:

```python
def test_checker_exits_nonzero_on_committed_planted_violation() -> None:
    assert _FIXTURE.is_file(), f"committed fixture missing: {_FIXTURE}"
    fixture_text = _FIXTURE.read_text(encoding="utf-8")
    planted_line = _line_number_of_marker(fixture_text, "PLANTED VIOLATION")

    result = _run_checker({"FIRESTARTER_SDP_SRC": str(_FIXTURE)})
    assert result.returncode == 1, (...)
    assert "FAIL:" in result.stdout
    assert f"line {planted_line}" in result.stdout, (...)
    assert "LOG_INFO_ID" in result.stdout
```

**Case-coverage plan to mirror** (docstring `:22-49`): 1 clean control, 2 committed planted
violation, 3 out-of-window control (discriminates by *position*, not presence), 4
comment-not-a-violation control, 5 missing-path fail-closed, 6 function-absent fail-closed. For the
new gate the analogues are: clean `firestarter.h`; planted `#ifdef` inside the body; an `#ifdef`
*outside* the predicate body (must PASS); an `#ifdef DEV_TOOLS` mentioned only in a comment inside
the body (must PASS); missing path; predicate absent/renamed.

---

### `firestarter_app/tests/fixtures/planted_ifdef_in_predicate.h` (NEW)

**Analog:** `tests/fixtures/planted_log_in_window.cpp` (68 lines). Copy its header-comment contract
verbatim in spirit — it is the "do NOT fix this file" notice that keeps the gate honest:

```cpp
/*
 * DELIBERATELY-VIOLATING fixture for
 * tests/test_check_no_log_in_sdp_window.py (Phase 116 Plan 04, TRACE-03c).
 *
 * This file is a minimal, standalone, never-compiled C++ source. It is not
 * built by platformio.ini and is not part of any firmware target. It exists
 * ONLY so the paired pytest can point ... FIRESTARTER_SDP_SRC env-override
 * seam at it and prove the checker actually exits non-zero ...
 *
 * "Fixing" this file (i.e. removing the planted LOG_INFO_ID(...) call below)
 * would silently hollow TRACE-03's third negative -- the anti-hollow gate
 * this project has required since the v1.12 hollow-GATE-03 tech debt. Do
 * NOT "fix" this file.
 */

static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length) {
    rurp_set_data_output();
    LOG_INFO_ID(MSG_DEBUG);  // PLANTED VIOLATION -- inside the SDP timing window
    /* ... */
}
```

The `// PLANTED VIOLATION` marker string is the contract with `_line_number_of_marker` — keep it.

---

### `tools/catalog/messages.toml` — the two new lock ids

**Analog:** 118's pair at `messages.toml:274-292` (`MSG_INFO_SDP_UNLOCK` name at `:278`,
`MSG_INFO_SDP_UNLOCK_DONE_US` at `:286`):

```toml
[[messages]]
id          = 0x5E
name        = "MSG_INFO_SDP_UNLOCK"
severity    = "INFO"
format      = "SDP unlock: disabling write protection"
params      = []
wire_format = "id_frame"

[[messages]]
id          = 0x5F
name        = "MSG_INFO_SDP_UNLOCK_DONE_US"
severity    = "INFO"
format      = "SDP unlock emitted in %lu us"
params      = [{ type = "u32", render = "dec" }]
wire_format = "id_frame"
```

Free ranges: INFO from `0x60`, WARN from `0x88`. `MSG_ERR_NOT_SUPPORTED` already exists (`:419`) —
D-06 needs **no** new ERROR id. Keep names ≤32 chars (118-02's `messages.h` column-reflow finding).
D-12's honesty requirement lives in the `format` string itself.

---

### `119-MEASUREMENT.md` / `119-NONREGRESSION.md`

**Analogs (mirror section-for-section):**

`118-MEASUREMENT.md`: `## 1. What was measured, and what it is not` → `## 2. Provenance block` →
`## 3. Raw captured log` → `## 4. The number` → `## 5. Socket state, stated plainly` →
`## 6. Validation ceiling` → `## 7. Downstream consumers` → `## Disposition`.
§1 and §6 are the wording that survived ceiling review (D-20) — follow them. §2 and §3 repeat
**per board** for D-18's three boards, each with its `controller:` identity line.

`118-NONREGRESSION.md`: `## 1. The … claim, stated precisely` → `## 2. The enumerated
serial-channel exception — the whole list, in one table` → `## 3. Why the bus stream is genuinely
unchanged` → `## 4. Flash and RAM` → `## 5. The CORRECTION-4 item-4 gate table` → `## 6.
Known-and-explained conditions — never silent` → `## 7. Validation ceiling` → `## 8. Deliberately
not taken` → `## Sweep summary`.
§4 is where D-15's arithmetic goes (base Leonardo `25680/28672`, 2992 B free); §5 is the gate table
this phase must extend with the new D-04 gate.

---

## Shared Patterns

### 1. Refusal + severity — `MSG_ERR_NOT_SUPPORTED`, no new catalog id
**Source:** `src/eprom_operations.cpp:36-39`
**Apply to:** `operation_utils.cpp`'s new NULL-`main` guard; any narrowly-scoped
`configure_eeprom28c` arm.
```cpp
    if (!is_flag_set(FLAG_CAN_ERASE)) {
        LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED);
        return true;                      /* true == finished */
    }
```

### 2. Report lines on the SDP path — unconditional `LOG_ID`, `response_code` untouched
**Source:** `src/proms/eeprom_28c.cpp:322`, `:352`, `:374`
**Apply to:** both new lock catalog emissions and the shared bracket helper.
```cpp
LOG_ID(MSG_INFO_SDP_UNLOCK);                          /* NOT LOG_INFO_ID — 118 D-01 */
LOG_ID_U32(MSG_INFO_SDP_UNLOCK_DONE_US, sdp_emit_us);
LOG_WARN_ID_U32(MSG_WARN_SDP_TBLC_EXCEEDED, sdp_emit_us);   /* severity via band only */
```
Permanently enforced by `test_case8_completion_poll_preserves_prior_severity`. The SDP path
**never** writes `response_code` (117 D-05 / 118 D-02).

### 3. Native test assertion discipline — ordered stream content, never a count
**Source:** `_shared/sdp_expected.h:60-63`
**Apply to:** every new golden/negative case.
> *"Never counts anything — D-06's anti-pattern list forbids it — every comparison is positional."*

Production register-write elision is invisible to a call-counting test. Assert the **exact
divergence index**, not `!= -1`.

### 4. ⚠ Cross-repo gate coupling — the failure mode that has bitten 4× in this milestone
**Source:** `firestarter_app/tools/check_no_log_in_sdp_window.py:129-140` (`_EMIT_ANCHOR_PATTERNS`
/ `_WAIT_ANCHOR_PATTERNS`, **append-only by contract**) + `:300-316` (fail-closed `ValueError`)
**Apply to:** every firmware edit in this phase.

D-14's shared bracket helper, if it wraps the emit call, removes the literal
`eeprom28c_emit_command_sequence(handle, EEPROM_SDP_DISABLE` from `eeprom28c_write_init`'s body →
`emit_anchor is None` → `raise ValueError` → **exit 1**, while the firmware suite stays 112/112
green. Named task work: **append** a new anchor (keep both superseded patterns), repair the paired
pytest + fixture, and re-run `python3 tools/check_no_log_in_sdp_window.py` after **every** firmware
edit. Two further tripwires: `_func_def_pattern` requires the return type to be literally `void`
(changing the emitter to return `bool` breaks window resolution); and the helper's own body must
**not** be added as a third scanned window — it contains `LOG_*` calls by design.
Baseline this session: `PASS: … emitter lines 222-238, completion-poll lines 272-285`, exit 0.

### 5. Every gate ships a committed planted-violation fixture
**Source:** `firestarter_app/tests/fixtures/planted_log_in_window.cpp` + its paired pytest
**Apply to:** the new D-04 gate. Exit-code-only assertions are insufficient — pair with an
output-content assertion, and derive the line number from the fixture at test time.

### 6. Generated artifacts — never hand-edit, never hand-normalise
**Source:** `tools/catalog/sync_to_subrepos.sh:1-19`; `firestarter/.github/workflows/build.yml:60-66`
**Apply to:** `firestarter/include/messages.h`, `firestarter_app/firestarter/messages.py`.
```bash
# Authoritative source: tools/catalog/{messages.toml,codegen.py}
# Generated firmware artifact: firestarter/include/messages.h
# Generated host artifact:     firestarter_app/firestarter/messages.py
# Idempotent: re-running with no upstream change is a no-op.
# Run after every catalog or codegen edit.
```
Drift gate: `python3 tools/catalog/codegen.py --catalog … --check` then `git diff --exit-code`.
`catalog-sync-check.yml` is red-until-merge by design (checks out sub-repos at `ref: main`).

### 7. ArduinoFake SIGABRT on any unmocked virtual
**Source:** `test_sdp_harness.cpp:75-90`
**Apply to:** the new `test_cmd_admission` suite and, under Option (a), any of the 16 suites that
starts linking `operation_utils.cpp`. `delay` / `delayMicroseconds` / `millis` / `micros` mocks are
load-bearing, not decorative — a SIGABRT here reads exactly like the deferred Unity-teardown flake
but is not it.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| The `is_memory_cmd()` **truth-table over `c ∈ [0,255]` in two build configurations** | test | transform | No existing suite is parameterised over a value range, and no suite runs in two envs today. The *suite scaffolding* analog is `test_dispatch/` (captured above) but the double-env semantic-equivalence proof shape is new. Use RESEARCH.md F-B's full 16-row command table as the expected-value source, and `firestarter_app/tests/test_revision_constants_parity.py:110-112` for the numeric-literals-not-macros idiom. |

---

## Metadata

**Analog search scope:** `firestarter/{include,src,src/proms,test/native/avr,.github/workflows}`,
`firestarter/platformio.ini`, `firestarter_app/{tools,tests,tests/fixtures}`,
`/workspaces/tools/catalog/`, `.planning/phases/118-*/`.
**Files read in full:** 12. **Files read in targeted ranges:** 9.
**Branch precondition:** verified — both sub-repos on `v1.22-at28c-software-data-protection-lifecycle`.
**Pattern extraction date:** 2026-07-28
