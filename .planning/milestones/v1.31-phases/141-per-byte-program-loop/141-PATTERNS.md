# Phase 141: Per-Byte Program Loop - Pattern Map

**Mapped:** 2026-08-10
**Files analyzed:** 18 (13 firmware, 1 meta, 3 host, 1 phase artifact)
**Analogs found:** 17 / 18 (1 partial — the pure overprogram function has no in-tree precedent)

**Read before this file:** `141-CONTEXT.md` (D-01…D-12, locked) and `141-RESEARCH.md` (the citation audit;
**where RESEARCH corrects CONTEXT, RESEARCH wins**). This document does not re-derive either. Its only
job is to hand the planner the **exact excerpts** an executor should be told to `read_first` and copy.

**Three line-number corrections established by this pass** (all verified against the live tree this
session, on top of RESEARCH's own three):

| Claim | Stated as | Actually |
|---|---|---|
| `rurp_write_to_register`'s CONTROL cache-elision | `rurp_register_utils.h:38-41` (RESEARCH) | **`:39-42`** — `case CONTROL_REGISTER:` is `:39`, the `if (control_register == data) { return; }` is `:40-42` |
| The `CTRL_VPP_P1_ENABLE` set→clear settle | `rurp_register_utils.h:56-58` (RESEARCH) | **`:57-59`** — `delayMicroseconds(4)` is on `:58` |
| `rurp_read_from_register` (cached, not a hardware read) | `rurp_register_utils.h:92-100` (RESEARCH) | **`:91-100`** — signature is `:91` |

None of these changes a decision; they matter only because a plan that hands an executor an
`offset`/`limit` read of the wrong window wastes a turn.

---

## File Classification

### `firestarter/` — firmware submodule (13 files)

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/proms/eprom.cpp` (M) | protocol handler | per-byte pulse→verify loop | itself (`:143-193` replaced) + `memory.cpp:333-353` `memory_verify_execute` + `memory.cpp:393-460` `mem_util_blank_check` | exact (in-file idioms) |
| `src/proms/memory.cpp` (M) | utility / primitive layer | transform (pure split) + hardware I/O | `memory.cpp:223-307` (clamp-a-host-timing-value) + `memory.cpp:151-173` (`mem_util_*` computed-value shape) | role-match |
| `include/memory_utils.h` (M) | header / declaration | n/a | itself, `:17-22` declaration block | exact |
| `include/messages.h` (G) | generated constants | n/a | the file itself — **ID-only `#define`s, DO NOT EDIT** | exact (generated) |
| `tools/catalog/messages.toml` (S) | vendored config | n/a | synced by `sync_to_subrepos.sh:38-55` | exact (synced) |
| `tools/catalog/codegen.py` (S) | vendored tooling | n/a | synced; byte-identical today → **zero diff** | exact (synced) |
| `platformio.ini` (M) | build config | n/a | **`[env:native_params_v131]` `:331-371`** | exact |
| `test/native/avr/<new_suite>/<new_suite>.cpp` (N) | test (native Unity) | event-driven assertion over a recorded stream | `test_trace_eprom_v131.cpp` (recorders, drive-`_main`) + `test_eprom_params_v131.cpp` (handle hygiene, PROGMEM readback) | exact |
| `test/native/avr/<new_suite>/host_stubs.cpp` (N) | test harness | stateful model + recorder | **`test_trace_eprom_v131/host_stubs.cpp`** (all 149 lines) | exact |
| `tests/<new_absence_gate>.py` (N) | test (pytest source-scan gate) | file-I/O source scan | `test_protocol_branch_inventory.py` (module conventions) + `test_vpp_seam_manual_on_every_board.py:389-468` (absence assertions) | exact |
| `tests/test_protocol_branch_inventory.py` (M) | test (gate) | file-I/O source scan | itself, `:443-452` — **one literal at `:446`** | exact |
| `tests/golden/protocol_branch_inventory.json` (R) | fixture (golden) | data | itself — re-derive via `_extract_predicates` | exact |
| `CLAUDE.md` (M) | docs | n/a | itself, §"Algorithm Handlers" `0x07`/`0x08`/`0x0B` rows | exact |

### `/workspaces` — meta repo (2 files)

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tools/catalog/messages.toml` (M) | canonical config | n/a | the `0xB0` entry (`:543-552`) — the **exact `[u24 hex_addr, u8]` shape** | exact |
| `.planning/phases/141-.../141-NEW-TRACE.md` (N) | phase artifact | data capture | `test_trace_eprom_v131.cpp:350-376` dump format + 140-PARAM-TABLE-RECORD §7 precedent | role-match |

### `firestarter_app/` — host submodule, GENERATED ONLY (3 files)

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/messages.py` (G) | generated constants | n/a | its own `0xB1` entries, `:108` (constant) + `:625-633` (`MessageDef`) | exact (generated) |
| `tools/catalog/messages.toml` (S) | vendored config | n/a | synced | exact |
| `tools/catalog/codegen.py` (S) | vendored tooling | n/a | synced; zero diff | exact |

Legend: **M** modified · **N** new · **G** generated (never hand-edit) · **S** synced (never hand-edit) · **R** re-derived by its own scanner

---

## Pattern Assignments

### 1. `firestarter/src/proms/eprom.cpp` (protocol handler, per-byte pulse→verify)

**File is 332 lines — read it in ONE call, extract everything.** Every idiom the rewrite needs is
already inside it.

**Imports pattern** (`:8-17`) — note `<Arduino.h>` at `:10`, which is why the delay helper's
implementation is free to call `delay()`/`delayMicroseconds()` from `memory.cpp` (also `<Arduino.h>`,
`memory.cpp:10`) but `eprom_params.cpp` must never gain it (Pitfall 6):

```c
#include "eprom.h"

#include <Arduino.h>

#include "firestarter.h"
#include "logging_id.h"
#include "memory_utils.h"
#include "rurp_shield.h"
#include "rurp_pinout.h"
#include "operation_utils.h"
```

`eprom_params.h` must be **added** here (it is the first `src/` consumer). It is dependency-free by
construction (`eprom_params.h:35-36` pulls only `<stdint.h>` + `rurp_platform_compat.h`), so adding it
costs no new warnings.

**`configure_eprom` — the single pre-hardware refusal point** (`:41-77`). D-03's refusal goes **after**
`:69-76`, because a `pulse_delay` of `0` compares as "not greater than the cap" vacuously:

```c
void configure_eprom(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_EPROM);

    handle->firestarter_operation_init = eprom_generic_init;

    switch (handle->cmd) {                                    // :46  tier-2 site (cmd)
        case CMD_WRITE:
            handle->firestarter_operation_init = eprom_write_init;
            handle->firestarter_operation_main = eprom_write_execute;
            break;
        ...
    }

    ep_set_control_register = handle->firestarter_set_control_register;   // :66
    handle->firestarter_set_control_register = eprom_internal_set_control_register;  // :67

    // Set default pulse_delay from protocol when Python doesn't supply one
    if (handle->pulse_delay == 0) {                           // :70  tier-2 site (pulse_delay)
        switch (handle->protocol) {                           // :71  TIER-1 SITE — MUST SURVIVE
            case 0x08: handle->pulse_delay = 100;  break;     // EPROM_QUICK: 100µs
            case 0x0B: handle->pulse_delay = 500;  break;     // EPROM_LEGACY: 500µs
            default:   handle->pulse_delay = 1000; break;     // EPROM_STD: 1ms
        }
    }
}                                                             // :77  ← D-03's refusal goes ABOVE this
```

**Fail-closed refusal shape to copy** — the in-tree idiom is `memory.cpp:67-71` (see Shared Pattern S3).
`configure_eprom` returns `void`, so the refusal is `LOG_ERROR_ID_* ; response_code = RESPONSE_CODE_ERROR ; return;`.
That is exactly what `eprom_write_init:96-98` already checks:

```c
// firestarter/src/proms/eprom.cpp:96-98 — the consumer of a refused configure
if (handle->response_code == RESPONSE_CODE_ERROR) {
    return;
}
```

**The block loop being REPLACED** (`:143-193`) — quoted in full because LOOP-02 names its parts by
identity, and because every idiom the new loop reuses is visible in it:

```c
void eprom_write_execute(firestarter_handle_t* handle) {
    if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0) {   // :144 idempotency guard — KEEP
        if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {                       // :145 TIER-1 — KEEP VERBATIM (Phase 142 owns it)
            // EPROM_LEGACY: direct VPE path — no CTRL_VPP_VPE_DROP_ENABLE dropping resistor
            handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);   // :147
        } else {
            // EPROM_STD / EPROM_QUICK: CTRL_VPP_VPE_DROP_ENABLE dropping path for precise VPP
            handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1);  // :150
        }
        delay(500);                                            // :152  MUST STAY ABOVE THE BYTE LOOP (LOOP-08)
    }

    uint8_t mismatch_bitmask[DATA_BUFFER_SIZE / 8];            // :155  REMOVE — 64 B (Uno) / 128 B (Leo) of stack
    memset(mismatch_bitmask, 0xFF, sizeof(mismatch_bitmask));  // :157  REMOVE

    int mismatch = 0;
    int retries = 0;
    uint32_t org_delay = handle->pulse_delay;                  // :161  KEEP — D-07's save half

    for (int w = 0; w < NUMBER_OF_RETRIES; w++) {              // :163  REMOVE (the flat block loop)
        program_mismatched_bytes(handle, mismatch_bitmask);    // :164  REMOVE
        mismatch = verify_and_update_mask(handle, mismatch_bitmask);  // :166 REMOVE

        if (!mismatch) {
            if (retries > 0) {
                LOG_INFO_ID_U8(MSG_INFO_RETRIES, (uint8_t)retries);  // :170 REMOVE (orphans catalog 0x51)
            }
            handle->pulse_delay = org_delay;                   // :172  KEEP — D-07's restore half
            return;
        }

        retries = w + 1;
        handle->pulse_delay = org_delay + (org_delay * retries / NUMBER_OF_RETRIES);   // :177 REMOVE (adaptive growth)
        LOG_DEBUG_ID_SUB_U16_U16(DBG_PULSE_DELAY_MISMATCH, (uint16_t)org_delay, (uint16_t)handle->pulse_delay);  // :178 REMOVE (orphans debug 0x15)
    }

    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 0);    // :181 the single-route disable
    {
        uint8_t _b[6];                                         // :182-191 the failure-report block
        _b[0] = (uint8_t)((handle->address >> 16) & 0xFF);
        _b[1] = (uint8_t)((handle->address >> 8)  & 0xFF);
        _b[2] = (uint8_t)( handle->address        & 0xFF);
        _b[3] = (uint8_t)retries;
        _b[4] = (uint8_t)(((uint16_t)mismatch >> 8) & 0xFF);
        _b[5] = (uint8_t)( (uint16_t)mismatch       & 0xFF);
        LOG_ERROR_ID_BYTES(MSG_ERR_WRITE_FAILED, _b, 6);       // :190
    }
    handle->response_code = RESPONSE_CODE_ERROR;               // :192
}
```

**Two functions to DELETE outright** (LOOP-02) — `:114-126` and `:129-141`. Note `:132`'s `(uint8_t)`
cast on `handle->data_buffer[i]`: `data_buffer` is `char[]` (`firestarter.h:202`), so **the new loop
needs that cast too**:

```c
// firestarter/src/proms/eprom.cpp:131-137  (the cast idiom the new loop must preserve)
for (uint32_t i = 0; i < handle->data_size; i++) {
    if (handle->firestarter_get_data(handle, (handle->address + i)) != (uint8_t)handle->data_buffer[i]) {
        mismatch_count++;
        mismatch_bitmask[i / 8] |= (1 << (i % 8));
    } else {
        mismatch_bitmask[i / 8] &= ~(1 << (i % 8));
    }
}
```

**The dead-code assert-and-settle helper** (`:327-332`) — an almost-exact template for LOOP-08's
once-per-block route assert. Zero callers anywhere in `src/`, `include/`, `test/`, `tests/`; already
`--gc-sections`-collected, so **deleting it reclaims 0 B** (do not count it):

```c
void eprom_internal_ensure_regulator_enabled(firestarter_handle_t* handle) {
    if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0) {
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
        delay(500);
    }
}
```

⚠️ The D-13 golden pins its predicate at `:328` with a `reason` claiming it is "used by callers outside
the write path" — **that reason is factually false** and must be corrected when the golden is re-derived
(see §7).

**The erase pulse — LOOP-07's second site** (`:274-288`, the call at `:283`):

```c
void eprom_internal_erase(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_INTERNAL_ERASE);
    rurp_chip_input();
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
    delay(100);
    handle->firestarter_set_address(handle, 0x0000);
    handle->firestarter_set_control_register(handle, CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE, 1);
    delay(100);
    rurp_chip_enable();
    delayMicroseconds(handle->pulse_delay);          // :283  ← route through the helper (D-06 site 2)
    rurp_chip_disable();
    ...
}
```

**The `using_p1_as_vpp` remap** (`:318-325`) — D-09's existing escape, and the reason the loop must
reach the control register through `handle->firestarter_set_control_register`, never
`memory_set_control_register` directly:

```c
// Use this function to set the control register and flip CTRL_VPE_ENABLE bit to CTRL_VPE_ENABLE or CTRL_VPP_P1_ENABLE
void eprom_internal_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle)) {   // :320
        bit &= ~CTRL_VPE_ENABLE;
        bit |= CTRL_VPP_P1_ENABLE;
    }
    ep_set_control_register(handle, bit, state);
}
```

**Do NOT touch** `:20` `#define NUMBER_OF_RETRIES 20`'s neighbours beyond removal, and do **not** touch
`eprom_check_vpp` (`:209-272`) — its `:218` duplicated predicate is Phase 142's. Its line number will
shift as the file above it shrinks; that shift is exactly what `test_protocol_branch_inventory.py:446`
must be updated for.

---

### 2. `firestarter/src/proms/memory.cpp` (utility, transform + hardware I/O)

**File is 390 lines — one read.** Three separate patterns live here.

**The pulse — LOOP-07 site 1** (`:249-259`). This is the primitive D-05 reuses; the loop must reach it
via `handle->firestarter_set_data`, never re-implement it:

```c
void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_chip_input();
    address = mem_util_remap_address_bus(handle, address, WRITE_FLAG);   // :251 per-chip bus config

    handle->firestarter_set_address(handle, address);
    rurp_write_data_buffer(data);
    delayMicroseconds(3);  // Needed for slower address changes like slow ROMs and "Power through address lines"   // :255 NOT counted (D-02)
    rurp_chip_enable();
    delayMicroseconds(handle->pulse_delay);   // :257  ← route through the helper (D-06 site 1)
    rurp_chip_disable();
}
```

**The verify read** (`:203-241`) — and, in `:219-235`, **the in-tree idiom for clamping a host-supplied
timing value**, which is the closest structural analog for the new delay helper's own bounds reasoning:

```c
    if (handle->read_settling_us) {
        uint32_t settling = handle->read_settling_us > 1000UL ? 1000UL : handle->read_settling_us;  // :220
        delayMicroseconds(settling);                                                                // :221
    }

    rurp_chip_enable();

    uint32_t strobe = handle->read_strobe_us ? handle->read_strobe_us : 3UL;   // :233  0-as-sentinel
    if (strobe > 1000UL) strobe = 1000UL;   /* T-44-01 secondary guard */      // :234
    delayMicroseconds(strobe);                                                 // :235
```

Note the difference the planner must carry: **read timings clamp, `pulse_delay` must not.** D-03 refuses
and LOOP-07 splits; a silent clamp of the pulse was explicitly rejected in D-03.

**Where the helper's DECLARATION belongs and what shape it takes** — the existing `mem_util_*`
computed-value functions (`:151-173`), which are the same "small, named, in-`memory.cpp`, declared in
`memory_utils.h`" shape:

```c
rurp_register_t mem_util_calculate_lsb_register(firestarter_handle_t* handle, uint32_t address) {
    return address & 0xFF;
}

rurp_register_t mem_util_calculate_msb_register(firestarter_handle_t* handle, uint32_t address) {
    return ((address >> 8) & 0xFF);
}
```

**D-09's `pins < 32` preserve mask** (`:159-173`) — read this before writing the guarded branch. The A16
bit and the drop bit are **distinct** on every shipped build (`0x01` vs `0x100`); the drop route dies
because the bit is excluded from the *preserve mask*, not because of a collision. **The in-file comment
at `:163-164` states the collision theory and is now known wrong** — RESEARCH §"DIP32 / A16 truth table"
supersedes it. Whether to correct that comment is a plan decision; leaving a comment that contradicts
the phase's own finding is the kind of thing Phase 146 will have to reconcile:

```c
rurp_register_t mem_util_calculate_top_address_register(firestarter_handle_t* handle, uint32_t address) {
    rurp_register_t top_address = ((uint32_t)address >> 16) & (CTRL_ADDRESS_LINE_16 | CTRL_ADDRESS_LINE_17 | CTRL_ADDRESS_LINE_18 | CTRL_READ_WRITE);   // :160
    rurp_register_t mask = CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_VPP_REGULATOR_ENABLE;   // :161 UNCONDITIONAL preserve set — this is why VPE survives
    if (handle->pins < 32) {                                                     // :162  ← D-09's actual mechanism
        // CTRL_VPP_VPE_DROP_ENABLE and CTRL_ADDRESS_LINE_16 share the same CONTROL bit — preserving CTRL_VPP_VPE_DROP_ENABLE
        // would corrupt A16 for 32-pin (512KB) chips. DIP32 chips use CTRL_VPP_P1_ENABLE instead.
        mask |= CTRL_VPP_VPE_DROP_ENABLE;                                        // :165
    }
    top_address |= rurp_read_from_register(CONTROL_REGISTER) & mask;              // :167 cached logical value
    if (handle->pins == 28) {
        top_address |= CTRL_ADDRESS_LINE_17;
    }
    return top_address;
}
```

**`mem_util_set_address`** (`:175-191`) — the unconditional CONTROL write at `:186` that disproves
CONTEXT's "a verify read does not disturb the control register":

```c
    rurp_register_t top_address = mem_util_calculate_top_address_register(handle, address);
    rurp_write_to_register(CONTROL_REGISTER, top_address);   // :186  EVERY byte, both pulse and verify
```

**The per-byte error-report shape** (`:261-281`) — this is the closest analog for the two new failure
frames, and it is a shape the host already renders (`MSG_ERR_VERIFY`, 5 bytes):

```c
void memory_verify_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint8_t byte = handle->firestarter_get_data(handle, handle->address + i);
        uint8_t expected = handle->data_buffer[i];
        if (byte != expected) {
            {
                uint32_t addr = (uint32_t)(handle->address + i);
                uint8_t _b[5] = {
                    (uint8_t)expected,
                    (uint8_t)byte,
                    (uint8_t)((addr >> 16) & 0xFF),
                    (uint8_t)((addr >> 8) & 0xFF),
                    (uint8_t)(addr & 0xFF),
                };
                LOG_ERROR_ID_BYTES(MSG_ERR_VERIFY, _b, 5);
            }
            handle->response_code = RESPONSE_CODE_ERROR;
            return;
        }
    }
}
```

If a plan adopts RESEARCH's recommended `verify_mode == VERIFY_PER_PULSE_PLUS_FINAL` final pass, **this
function is the pattern to mirror** — same `MSG_ERR_VERIFY` id, same 5-byte payload, same
`response_code` + early `return`.

**D-12's shape-compatibility target — `mem_util_blank_check`** (`:321-390`). CONTEXT.md cites `:307-341`;
**that is stale — the function is `:321-390`** (F: RESEARCH's citation audit). The pieces D-12 asks the
loop not to preclude:

```c
typedef struct {                                    // :309-311  the progress_data payload type
    uint32_t address;
} blank_check_progress_data_t;

#define BLANK_CHECK_CHUNK_SIZE 2048                 // :313

void mem_util_blank_check(firestarter_handle_t* handle) {
    blank_check_progress_data_t* progress_data;
    if (!is_operation_in_progress(handle)) {         // :323  first entry
        set_operation_in_progress(handle);
        handle->progress_data = malloc(sizeof(blank_check_progress_data_t));
        progress_data = (blank_check_progress_data_t*)handle->progress_data;
        progress_data->address = handle->address;    // stash the caller's address
        handle->address = 0;
    } else {                                        // :329  re-entry
        progress_data = (blank_check_progress_data_t*)handle->progress_data;
        if (handle->address >= handle->mem_size) {   // :331  completion
            clear_operation_in_progress(handle);
            handle->address = progress_data->address;
            free(handle->progress_data);
            handle->progress_data = NULL;
            return;
        }
    }

    uint32_t end_address = handle->address + BLANK_CHECK_CHUNK_SIZE;              // :341  the chunk loop
    for (uint32_t i = handle->address; i < end_address && i < handle->mem_size; i++) {
        ...
    }
    handle->address += BLANK_CHECK_CHUNK_SIZE;                                     // :370  advance
    ...
    if (handle->cmd != CMD_BLANK_CHECK) {
        LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size); // :387  the emit
    }
}
```

**What "shape-compatible" concretely means for the planner:** the per-byte loop's cursor should be a
single index derived from `handle->address` and bounded by an expression the way `:341-342` is, so a
later phase can substitute `end_address` with a chunk bound and add the re-entry prologue **without
touching the loop body**. It does **not** mean adding `progress_data`, `malloc`, or an
`is_operation_in_progress` branch now — D-12 forbids that.

---

### 3. `firestarter/include/memory_utils.h` (header, declaration)

**Analog:** itself. 33 lines — one read. The two new declarations go in the `:17-22` block, beside the
other `mem_util_*` names, inside the existing `extern "C"` wrapper:

```c
#ifndef __MEMORY_UTILS_H__
#define __MEMORY_UTILS_H__
#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif
#define WRITE_FLAG 0
#define READ_FLAG 1

uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t address, uint8_t read_write);
void mem_util_blank_check(firestarter_handle_t* handle);
void mem_util_set_address(firestarter_handle_t* handle, uint32_t address);
rurp_register_t mem_util_calculate_lsb_register(firestarter_handle_t* handle, uint32_t address);
rurp_register_t mem_util_calculate_msb_register(firestarter_handle_t* handle, uint32_t address);
rurp_register_t mem_util_calculate_top_address_register(firestarter_handle_t* handle, uint32_t address);
                                                    // ← the two new declarations belong here (:22)

static inline bool using_p1_as_vpp(const firestarter_handle_t* handle) {   // :24
    return (handle->pins == 32 && handle->bus_config.vpp_line == VPP_P1_32_DIP) ||
           (handle->pins == 28 && handle->bus_config.vpp_line == VPP_P1_28_DIP) ||
           (handle->pins == 24 && handle->bus_config.vpp_line == VPP_P21_24_DIP);
}
#ifdef __cplusplus
}
#endif

#endif  // MEMORY_UTILS_H
```

**Two constraints this file imposes:** (a) it is inside `extern "C"`, so the helpers get C linkage —
which is what lets the new native suite call `mem_util_split_delay` directly from a C++ TU without a
name-mangling dance; (b) it includes only `firestarter.h`, so the declarations must not reference a type
that would drag in `<Arduino.h>` (plain `uint32_t`/`uint16_t` are fine).

---

### 4. `firestarter/platformio.ini` — the sixth env (config)

**Analog: `[env:native_params_v131]` (`:331-371`) — copy it wholesale, comments included (D-10).**
Reproduced verbatim here so the planner can hand it over without a second read:

```ini
[env:native_params_v131]
; Phase 140 Plan 04 (TABLE-03, TABLE-01, D-11): a FIFTH native environment,
; whose sole purpose is to compile+run test_eprom_params_v131 -- the suite
; that exercises the pulse_delay == 0 fallback in configure_eprom
; (src/proms/eprom.cpp:69-76) for protocols 0x07/0x08/0x0B, and proves
; eprom_params_for()'s row resolution (plan 140-01) behaviourally. 0 of the
; 329 shipped 27C chips yield pulse_delay == 0 (F-140-04), so this native
; suite is the ONLY possible oracle for TABLE-03 -- no bench run in Phase 145
; can reach this branch.
;
; HARD CONSTRAINT -- MUST NEVER be folded into [env:native] or
; [env:native_nodevtools]'s test_filter. Both of those are pinned at exactly
; the same 17-entry test_filter list and a live gate (check_size_baseline.py's
; compare_native) asserts 141 cases / 17 suites on BOTH of them by exact
; count. This env's test_filter therefore names ONLY its own new suite (1
; entry, not 18), and this env is NOT added to default_envs (:16) -- pio run
; would try to link a main()-less target ("undefined reference to main").
;
; FURTHER CAVEAT (measured, F-138-05): do not feed "native_params_v131" to
; either live gate -- check_size_baseline.py hardcodes NATIVE_ENVS =
; ("native", "native_nodevtools") and an unknown env name raises an
; UNCAUGHT KeyError (exit 1, a false regression signal, not the documented
; exit-2); check_build_warnings.py handles it cleanly (exit 2) but has no
; baseline entry for this env either way. This env's own counts are recorded
; ONLY in this plan's SUMMARY and the phase record, never asserted by either
; gate.
;
; NO CI COVERAGE (F-140-11, D-11): neither build.yml nor beta-build.yml runs
; any `pio test` env beyond native and native_nodevtools -- this env's counts
; are a LOCAL, run-by-name obligation. Never imply CI covers it.
platform = native
test_framework = unity
test_filter =
	native/avr/test_eprom_params_v131
build_flags =
	${env:native.build_flags}
	-I test/native/avr/test_eprom_params_v131
lib_deps =
	fabiobatsilva/ArduinoFake@^0.4.0
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>
test_build_src = yes
```

**Mechanical facts the retargeted copy must preserve (all verified this session):**

| Constraint | Where enforced | What breaks if ignored |
|---|---|---|
| `test_filter` names **one** entry, its own suite | `size_baseline.json:native_envs` via `check_size_baseline.py`'s `compare_native` | `native`/`native_nodevtools` leave 141 cases / 17 suites → live gate RED |
| Not added to `default_envs` (`platformio.ini:16` = `uno, uno328pb, leonardo`) | `pio run` | "undefined reference to main" |
| Never passed to `check_size_baseline.py` | `NATIVE_ENVS` hardcoded `("native","native_nodevtools")` | uncaught `KeyError` → exit 1, a **false** regression signal (F-138-05, accepted, not fixed) |
| Never passed to `check_build_warnings.py` | no baseline entry | exit 2 |
| `build_flags` starts `${env:native.build_flags}` | inherits `-D HARDWARE_REVISION` (`:23`), `-std=gnu++17`, `-I include`, and **all 17 sibling `-I` entries** | dropping `HARDWARE_REVISION` changes which stubs compile (`host_stubs_common.inc:289`) |
| `build_src_filter` byte-identical to the four sibling native envs | `:163`, `:252`, `:290`, `:328`, `:370` — all five are the same string | a different TU set changes what links, silently |

Also copy the **precedent-following comment** the file already carries at `:293-318` (`native_trace_v131`)
and `:255-279` (`native_pinmap_provisional`): both restate the same HARD CONSTRAINT block. This will be
the **sixth** env; the comment should say so, and should name Phase 141 / D-10 as its origin.

`firestarter/CLAUDE.md` §"Native (Host) Test Environment" carries an explicit
**"Exception (Phase 140 D-11)"** paragraph that overrides its own general "add a new suite to *both*
pinned envs" instruction. **Extend that paragraph for the sixth env in the same change** — CONTEXT
`<canonical_refs>` requires it, and leaving it naming only `native_params_v131` makes the general
instruction read as still binding.

---

### 5. `firestarter/test/native/avr/<new_suite>/host_stubs.cpp` (test harness, NEW)

**Analog: `test_trace_eprom_v131/host_stubs.cpp` — all 149 lines. Copy its structure, not just its
guards.** The `test_eprom_params_v131/host_stubs.cpp` (39 lines) is the *pure pass-through* variant and
is the wrong analog here: the new suite needs all three recorder layers.

**Guard composition — the exact order** (`:52-78`). Every guard is read **at include time**; a `#define`
after the `#include` silently does nothing:

```cpp
#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

/* Activate the ordered strobe recorder (opt-IN). MUST precede the include. */
#define HOST_STUBS_REAL_REGISTER_UTILS
/* Activate the timing recorder (opt-IN, Task 1). MUST precede the include,
 * and requires HOST_STUBS_REAL_REGISTER_UTILS above (its sequence key is
 * s_strobe_count, which only exists in that block). */
#define HOST_STUBS_RECORD_TIMING
/* Opt OUT of the shared .inc's default rurp_read_data_buffer (always 0), so
 * this file can supply a stateful one instead. MUST precede the include. */
#define HOST_STUBS_CUSTOM_READ_DATA_BUFFER

#include "../_shared/host_stubs_common.inc"

/* production's real cache-compare + latch-strobe sequencing + timing */
#include "rurp_register_utils.h"          /* AFTER the .inc — real elision, not a replica */
```

**Do NOT additionally define `HOST_STUBS_CUSTOM_HW_REVISION`.** `HOST_STUBS_REAL_REGISTER_UTILS` already
defines `HOST_STUBS_CUSTOM_HW_REVISION_BLOCK` (`host_stubs_common.inc:105`), so the four
hardware-revision stubs come from the real `rurp_hw_rev_utils.h`. `test_val_eprom/host_stubs.cpp` defines
the narrower guard and **must not be copied here** — the trace suite's own header (`:39-49`) records this
collision as a correction.

**The register-cache reset seam** (`:89-93`) — mandatory, because the three globals initialise to `0xff`
and persist across Unity cases in one binary, ORing `CTRL_VPP_REGULATOR_ENABLE` (`0x80`) into the first
address write of any case that forgets:

```cpp
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl) {
    lsb_address = lsb;
    msb_address = msb;
    control_register = ctrl;
}
```

**The pulse-count oracle** (`:122-149`) — the single most reusable thing in the tree for LOOP-01/04/06:

```cpp
struct trace_readback_state_t {
    uint8_t target;
    uint8_t converge_after;
    uint8_t read_count;
};
static trace_readback_state_t s_trace_readback[4];

extern "C" void trace_readback_reset() {
    for (int i = 0; i < 4; i++) {
        s_trace_readback[i].target = 0xFF;
        s_trace_readback[i].converge_after = 0;
        s_trace_readback[i].read_count = 0;
    }
}

extern "C" void trace_readback_seed(uint8_t idx, uint8_t target, uint8_t converge_after) {
    s_trace_readback[idx].target = target;
    s_trace_readback[idx].converge_after = converge_after;
    s_trace_readback[idx].read_count = 0;
}

extern "C" uint8_t rurp_read_data_buffer() {
    uint8_t idx = (uint8_t)(rurp_read_from_register(LEAST_SIGNIFICANT_BYTE) & 0x03);
    trace_readback_state_t* st = &s_trace_readback[idx];
    uint8_t result = (st->read_count < st->converge_after) ? 0xFF : st->target;
    st->read_count++;
    return result;
}
```

**Three things to carry over verbatim when copying it:**

1. **It is per-suite, not shared.** Write your own copy; widen the 4-entry array and the `& 0x03` mask if
   the new suite uses a larger block. **Re-derive the byte-index reasoning if you change the chip or
   base the block anywhere but address 0** — the derivation comment at `:104-121` is the load-bearing
   part, not the code.
2. **The read-count ↔ pulse-count mapping shifts by one under LOOP-06.** The old loop pulsed
   unconditionally on pass 1; the new loop reads *first* (the skip check). `converge_after = N` now means
   "matches on read N+1", i.e. **N pulses**. State this in a comment in the suite (Pitfall 4 —
   "the single easiest place for the new suite to be silently off by one").
3. Seed one byte with `converge_after = 0` as a **control**: it must produce **zero** pulses (LOOP-06).

**What the shared `.inc` already gives you** (`host_stubs_common.inc`, 353 lines — one read):

| Symbol | Line | Purpose |
|---|---|---|
| `#error` fail-closed guard | `:92-94` | `HOST_STUBS_RECORD_TIMING` without `HOST_STUBS_REAL_REGISTER_UTILS` refuses to compile |
| `clear_strobes / strobe_count / strobe_overflowed / strobe_kind / strobe_pin / strobe_value` | `:117-122` | ordered strobe read side, cap 512 |
| `strobe_push`, `STROBE_KIND_DATA=1`, `STROBE_KIND_PIN=2` | `:107-133` | the recorder itself; overflow sets a flag, prefix stays valid |
| `clear_timings / timing_count / timing_overflowed / timing_kind / timing_us / timing_after_strobe` | `:180-185` | timing read side, cap 512 |
| `timing_push(kind, us)`, `TIMING_KIND_DELAY_US=3`, `TIMING_KIND_DELAY_MS=4` | `:170`, `:187-196` | the write entry point the suite's `setUp()` hooks call; `seq = s_strobe_count` at push time |
| the two hooks | `:204-209` | `rurp_write_data_buffer` and `rurp_set_control_pin` are the only two recorded points |
| `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` opt-out | `:264-268` | lets the suite supply a stateful read-back |

**Extend the `.inc` only if a genuinely new `rurp_*` symbol appears.** Nothing in Phase 141 adds one, so
the expected diff to `host_stubs_common.inc` is **zero bytes**. Its stability is load-bearing for 17
other suites.

---

### 6. `firestarter/test/native/avr/<new_suite>/<new_suite>.cpp` (test, NEW)

**Two analogs, and the plan should name both:** `test_trace_eprom_v131.cpp` for the recorder/drive
machinery, `test_eprom_params_v131.cpp` for handle hygiene, PROGMEM readback and `main()` shape.

**Includes + extern decls** (`test_trace_eprom_v131.cpp:34-66`):

```cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <string.h>
#include <stdio.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;

extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);
extern "C" void timing_push(uint8_t kind, uint32_t us);
extern "C" void trace_readback_reset();
extern "C" void trace_readback_seed(uint8_t idx, uint8_t target, uint8_t converge_after);
```

A suite `.cpp` **may** include `<Arduino.h>` + `<ArduinoFake.h>` — Pitfall 6's 14-warning trap bites
*production* TUs that pair `<Arduino.h>` with the `avr/pgmspace.h` shim, not test TUs. The new suite will
also need `#include "eprom_params.h"` (for the enums) and `#include "memory_utils.h"` (to call the pure
split helper directly). The recorder enums must be **re-declared locally** — `#define`s inside
`host_stubs.cpp`'s TU are invisible in this, a separate TU. The trace suite does exactly this at `:275-276`:

```cpp
/* Mirrors host_stubs_common.inc's own cap constants (HOST_STUBS_MAX_STROBES /
 * HOST_STUBS_MAX_TIMINGS, both 512) — restated here because #defines inside
 * host_stubs.cpp's TU are not visible in this, a SEPARATE translation unit. */
#define V131_STROBE_CAP 512
#define V131_TIMING_CAP 512
```

**`setUp()` — the hooks that make both oracles work** (`test_trace_eprom_v131.cpp:72-98`). This is the
LOOP-07 oracle's entire mechanism:

```cpp
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();

    /* THE hook (D-02). ... Capture-less lambdas: timing_push is a free
     * extern "C" symbol, nothing needs capturing. Do not remove these as
     * "unused" — every protocol case's cadence depends on them. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysDo([](unsigned int us) {
        timing_push(TIMING_KIND_DELAY_US, (uint32_t)us);
    });
    When(Method(ArduinoFake(), delay)).AlwaysDo([](unsigned long ms) {
        timing_push(TIMING_KIND_DELAY_MS, (uint32_t)ms);
    });
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);     // ArduinoFake SIGABRTs on any unmocked call
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);

    clear_strobes();
    clear_timings();
    reset_register_cache(0x00, 0x00, 0x00);
}
```

**Why this is a real oracle, not an accident:** ArduinoFake declares
`virtual void delayMicroseconds(unsigned int)`, and on a 64-bit Linux host `unsigned int` is **32-bit**,
so an over-ceiling value arrives **intact and visible** rather than truncated the way AVR's 16-bit
`unsigned int` would truncate it.

**Handle hygiene — fresh, zero-initialised per case** (`test_eprom_params_v131.cpp:70-85`; the trace
suite's fuller variant is `test_trace_eprom_v131.cpp:215-229`):

```cpp
/* Fresh handle per case (Pitfall 4) -- json_parse never resets pulse_delay,
 * protocol, mem_size, vpp_mv or pins, so a stale global handle would leak
 * state between cases. */
static firestarter_handle_t make_handle(uint32_t protocol, uint32_t pulse_delay_us) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.mem_size = 2048;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    h.pulse_delay = pulse_delay_us;
    return h;
}
```

**The three derived `bus_config_t` literals** (`test_trace_eprom_v131.cpp:171-213`) — **copy these,
do not invent new ones.** A zeroed `bus_config` is *degenerate*, not an identity remap:
`mem_util_remap_address_bus` starts `reorg_address = config.address_mask & address`, so
`address_mask == 0` collapses every address to 0. The derivation command is recorded at `:140-148`:

```cpp
/* AM27C512 (protocol 0x07) — pinout DIP28_27512, mem_size 65536, pulse 100 us */
static const bus_config_t V131_BUS_CONFIG_0x07 = {
    { 0x00, 0x01, ..., 0x0F, 0xFF }, 0x0000FFFFUL, 16, 0xFF, 0xFF, 0x00000000UL
};
/* AM27C020 (protocol 0x08) — DIP32_27C020, 262144, 100 us. vpp_pin=21=0x15=VPP_P1_32_DIP,
 * so using_p1_as_vpp(handle) is TRUE (pins==32). */
static const bus_config_t V131_BUS_CONFIG_0x08 = {
    { 0x00, ..., 0x10, 0x14, 0xFF }, 0x0011FFFFUL, 17, 0x16, 0x15, 0x00000000UL
};
/* AM2716 (protocol 0x0B) — DIP24_2716, 2048, 500 us. vpp_pin=11=0x0B=VPP_P21_24_DIP,
 * so using_p1_as_vpp(handle) is also TRUE (pins==24). */
static const bus_config_t V131_BUS_CONFIG_0x0B = {
    { 0x00, ..., 0x0A, 0xFF }, 0x000007FFUL, 11, 0xFF, 0x0B, 0x00002000UL
};
```

⚠️ **D-09's DIP32 case needs a 32-pin part whose block crosses an A16 boundary.** `V131_BUS_CONFIG_0x08`
is the only 32-pin config in the tree, but the trace fixture drives it at address 0 with a 4-byte block.
The new suite must drive it near `0x00FFFF`→`0x010000`. Because that changes the base address, the
read-back model's `& 0x03` index derivation is **no longer valid** — re-derive it (the comment at
`host_stubs.cpp:104-121` shows what "re-derive" means) or key the model on the full latched LSB+MSB pair.
This is the single highest-risk seam in the new suite.

**Drive `_main` directly, never the whole command** (`test_trace_eprom_v131.cpp:243-270`). This is what
makes LOOP-05's disable assertion non-vacuous — `command_done()` (`firestarter.cpp:162-171`) zeroes the
whole control register on **every** exit, so a whole-command test passes even if
`eprom_write_execute` disables nothing:

```cpp
static void drive_v131_write(firestarter_handle_t* h) {
    configure_memory(h);                          // itself writes address 0 (memory.cpp:93)
    reset_register_cache(0x00, 0x00, 0x00);       // AFTER configure_memory
    trace_readback_reset();
    trace_readback_seed(0, V131_SYNTHETIC_BLOCK[0], 0);
    ...
    clear_strobes();
    clear_timings();
    h->address = 0;
    h->data_size = 4;
    for (int i = 0; i < 4; i++) {
        h->data_buffer[i] = (char)V131_SYNTHETIC_BLOCK[i];
    }
    h->firestarter_operation_main(h);              // NOT _init — keeps the capture scoped to the loop
}
```

**Never re-assign `firestarter_get_data` / `firestarter_set_data`.** Keeping the real
`memory_get_data`/`memory_set_data` in the path is what captures the verify read's own bus activity
(the trace suite's recorded "R2 over R1" choice) and is D-05's rationale expressed as a test constraint.

**PROGMEM readback — the accessor idiom to copy verbatim** (`test_eprom_params_v131.cpp:176-191`). A
direct `row->max_pulses` compiles, passes every native test, and returns **RAM garbage on AVR**;
`rurp_platform_compat.h` defines `pgm_read_*` as plain dereferences off-AVR, so **no native test can
catch this**:

```cpp
    const eprom_params_t* row = eprom_params_for(protocol);
    TEST_ASSERT_NOT_NULL_MESSAGE(row, ctx);

    uint32_t overprogram_cap_us = pgm_read_dword(&row->overprogram_cap_us);
    uint32_t energy_cap_us      = pgm_read_dword(&row->energy_cap_us);
    uint8_t  max_pulses         = pgm_read_byte(&row->max_pulses);
    uint8_t  overprogram_factor = pgm_read_byte(&row->overprogram_factor);
    uint8_t  verify_mode        = pgm_read_byte(&row->verify_mode);
    uint8_t  vpp_path           = pgm_read_byte(&row->vpp_path);
```

`pgm_read_dword` for the two `uint32_t` columns, `pgm_read_byte` for the four `uint8_t` columns.
**The `src/` call site in `eprom.cpp` must use the identical form, hoisted once per block** — never
re-read inside the byte loop (each is an `LPM` sequence on AVR).

**Non-vacuity and negative controls** (`test_eprom_params_v131.cpp:113-135`) — the suite's own comment
states the rule the new suite must follow: *"Without these, cases 1-3 could pass vacuously on a handle
the fallback never actually touched."* Every new assertion needs a paired control.

**Soundness + determinism wrapper** (`test_trace_eprom_v131.cpp:288-321`) — worth copying even though
the new suite has no frozen fixture: overflow flags, `response_code`, a non-vacuous/under-cap length
bound, and a second drive compared positionally.

**The `main()` shape** (`test_eprom_params_v131.cpp:203-220`) — explicit `RUN_TEST` list, no auto-discovery:

```cpp
int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_...);
    ...
    return UNITY_END();
}
```

**Never use `TEST_IGNORE_MESSAGE`** to park a RED case — `platformio.ini:100-101` records the rule:
"an IGNORED result does not demonstrate RED."

**The dump harness — D-10's "capture the new trace as a committed artifact"**
(`test_trace_eprom_v131.cpp:350-376`). Permanently behind `#ifdef EPROM_V131_TRACE_DUMP`, which no env
defines, and **must be run by invoking the built binary directly** because `pio test` swallows `printf`:

```cpp
#ifdef EPROM_V131_TRACE_DUMP
static void dump_v131_merged_ready_to_paste(const char* tag) {
    int n = v131_merged_length();
    printf("##### %s total=%d strobe_overflow=%d timing_overflow=%d\n",
           tag, n, strobe_overflowed(), timing_overflowed());
    for (int i = 0; i < n; i++) {
        v131_trace_entry_t e;
        v131_merged_at(i, &e);
        printf("    {%d, 0x%02X, 0x%02X, %luUL}, /* %d */\n",
               e.kind, e.pin, e.value, (unsigned long)e.us, i);
    }
}
#endif
```

Commit that output as the phase artifact. **Do NOT** write it into `_shared/eprom_v131_expected.h` —
that file's blob SHA is pinned by `tests/test_golden_trace_identity_eprom_v131.py`, and re-freezing is
Phase 144 / TEST-06's job.

---

### 7. `firestarter/tests/<new_absence_gate>.py` (test, pytest source-scan gate, NEW)

**Two analogs. Name both in the plan.**

#### 7a. Module conventions — `tests/test_protocol_branch_inventory.py` (565 lines)

Copy its **shape**, not its extraction logic. The conventions it establishes:

**Path resolution — never from the environment for the default targets** (`:88-104`):

```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_EPROM_REL = "src/proms/eprom.cpp"
_PARAMS_REL = "src/proms/eprom_params.cpp"
_INVENTORY_JSON = _HERE / "golden" / "protocol_branch_inventory.json"

# Environment seams -- bind at IMPORT time. See module docstring
# "Environment seams" section above. Tests 1 and 6 deliberately never read
# either of these.
_SCAN_EPROM = Path(
    os.environ.get("FIRESTARTER_BRANCH_SCAN_SOURCE", _REPO_ROOT / _EPROM_REL)
)
```

**Fail-closed, never skip** (`:119-136`) — the D-15 discipline expressed in code:

```python
def _resolve_git():
    """Resolve the `git` binary, fail-closed.

    Deliberately never bypassed via any decorator or runtime call that
    would mark this outcome as skipped, anywhere in this module ...
    """
    git_bin = shutil.which(os.environ.get("GIT", "git"))
    assert git_bin is not None, (
        "git not found on PATH (checked $GIT, falling back to 'git'). This "
        "must FAIL the suite, never be silently skipped ..."
    )
    return git_bin
```

**The non-vacuity guard** (`:455-484`) — the pattern every new leg needs. Note it asserts the scan
target **exists and is non-empty**, and that the live scan returned something:

```python
    targets = (_SCAN_EPROM, _SCAN_PARAMS)
    existing_nonempty = [p for p in targets if p.is_file() and p.stat().st_size > 0]
    sizes = {str(p): (p.stat().st_size if p.is_file() else None) for p in targets}
    assert len(existing_nonempty) == 2, (
        "non-vacuous guard: expected exactly 2 scan targets to exist and "
        f"be non-empty, found {len(existing_nonempty)} of 2 -- sizes="
        f"{sizes}. A vacuous (missing or empty) scan target must FAIL, "
        "never silently pass as if nothing needed checking."
    )

    live = _extract_predicates(_SCAN_EPROM.read_text())
    assert len(live) > 0, (
        f"non-vacuous guard: the live re-parse of {_SCAN_EPROM} returned "
        f"{len(live)} predicates -- a zero-predicate scan must FAIL, never "
        "read as 'nothing to report'."
    )
```

**The `_HERE`-resolves-to-the-wrong-directory landmine, closed by construction** (`:512-542`):

```python
def test_default_targets_resolve_inside_this_repository():
    default_eprom = _REPO_ROOT / _EPROM_REL
    ...
        assert p.is_file(), f"default {label} target {p} does not exist on disk"
        assert p.stat().st_size > 0, f"default {label} target {p} is empty"
        assert p.resolve().is_relative_to(_REPO_ROOT), (
            f"default {label} target {p} resolves outside _REPO_ROOT ..."
        )
```

**The comment-stripper** (`:159-203`) — reusable if the absence gate must not match a mention inside a
comment. It replaces every stripped span with whitespace **of the same shape, so line numbers are
preserved exactly**. `test_params_table_has_no_second_selector`'s own docstring records why it matters:
*"the real file's own docstring uses the English word 'switch' twice while explaining that it contains
none."* An LOOP-02 absence gate has exactly this problem — the rewritten `eprom.cpp` will very plausibly
carry a comment saying *"replaces the former NUMBER_OF_RETRIES block loop"*.

**No `conftest.py`, ever** (`:68-79`) — `firestarter/tests/` has none anywhere in the repo; a recorded
house-rule, not an omission. Stdlib + pytest only. Deliberately **not** named `check_*.py`, so it stays
outside `test_checker_convention.py`'s glob and incurs none of that convention's obligations.

**Self-check that the fail-closed contract cannot be edited away** (`:545-565`):

```python
def test_git_is_required_not_optional():
    this_source = Path(__file__).read_text()
    for line in this_source.splitlines():
        stripped = line.strip()
        assert not stripped.startswith("pytest.skip"), (...)
        assert not stripped.startswith("@pytest.mark.skipif"), (...)
```

#### 7b. Absence assertions — `tests/test_vpp_seam_manual_on_every_board.py:389-468`

This is the closest in-tree analog for *"assert construct X is ABSENT from file Y"*, which is exactly
LOOP-02's own wording and LOOP-07's "global" claim.

**Regex-anchored absence, with the whole file in the failure message** (`:412-421`):

```python
    assert not re.search(r"^\s*#\s*define\s+RURP_HAS_VPP_DAC\b", board_header_text, re.MULTILINE), (
        f"expected {_PY32_BOARD_HEADER} to contain NO #define of "
        f"RURP_HAS_VPP_DAC -- the board header must only ever consume this "
        f"macro (indirectly, via include/rurp_vpp.h), never define it "
        f"itself. Finding a #define here means the hollow-guard defect has "
        f"returned ...\nGot:\n{board_header_text}"
    )
```

**Count-based presence (the inverse), for LOOP-07's "both sites now call the helper"** (`:424-444`):

```python
def test_seam_source_is_dependency_free():
    text = _SEAM_SRC.read_text()
    includes = re.findall(r'^\s*#\s*include\s+"([^"]+)"', text, re.MULTILINE)
    assert len(includes) == 1, (
        f"expected exactly one #include directive in {_SEAM_SRC} ... "
        f"got {len(includes)}: {includes!r}.\nGot:\n{text}"
    )
```

For LOOP-07 the shape is: `delayMicroseconds(handle->pulse_delay)` appears **zero** times across
`src/`, `include/`, `lib/`, `platform/`, **and** `mem_util_delay_us(handle->pulse_delay)` appears
**exactly twice** (`memory.cpp` once, `eprom.cpp` once). A pure-absence assertion alone is vacuous if
the call was deleted rather than rerouted — pair it with the positive count.

**The concatenated-needle trick** (`:447-468`) — mandatory for a gate whose own failure messages quote
the very tokens it forbids. Without it the gate matches itself:

```python
    """The two needle strings below are built via concatenation (not written
    verbatim) so this test's own assertion text does not trip its own
    check -- the literal substrings must appear NOWHERE in this file,
    including inside this test's failure messages."""
    own_text = Path(__file__).read_text()
    skip_call = "pytest" + ".skip"
    skipif_marker = "mark" + ".skipif"
```

An LOOP-02 absence gate that names `NUMBER_OF_RETRIES`, `program_mismatched_bytes` and
`verify_and_update_mask` in its own failure strings **must** build those needles by concatenation, or
scope the search to a comment-stripped `eprom.cpp` only (never to its own source). This is the single
most likely way the new gate ships broken-but-green.

**⚠️ Honest CI framing** (`:31-35`) — copy this paragraph's spirit:

> This module executes in NO CI leg on this branch: `pytest tests/ -v` appears only in build.yml
> (push/PR to main) and beta-build.yml (push to beta) — neither fires on the firmware milestone branch.

RESEARCH corrects the scope: `pytest tests/ -v` **is** in both workflows (`build.yml:161`,
`beta-build.yml:134`), so a new module under `tests/` **will** run in CI once the branch reaches
`main`/`beta` — which is precisely why the D-13 gate going RED is a CI failure. State the branch-local
reality without implying the module is permanently CI-invisible.

---

### 8. `firestarter/tests/test_protocol_branch_inventory.py` (M) — the one literal

**Analog: itself.** The whole edit is `:446`. Note the failure text's own wording constrains the fix —
**the count must stay three**:

```python
def test_exactly_three_protocol_keyed_sites_at_the_pinned_lines():
    live = _extract_predicates(_SCAN_EPROM.read_text())
    protocol_lines = sorted(s["line"] for s in live if s["tier"] == "protocol")
    assert protocol_lines == [71, 145, 218], (          # :446  ← THE EDIT
        "expected exactly three tier-protocol sites at lines [71, 145, "
        f"218], found {protocol_lines}. A fourth protocol-keyed branch "
        "site is a second algorithm selector and a TABLE-05 violation -- "
        "fewer than three means one of the pinned sites was removed "
        "without updating this inventory."
    )
```

The three sites that must survive: `:71` the fallback switch (Phase 140 D-03 keeps it), `:145` the VPP
predicate **kept verbatim, only its line moves** (Phase 142 owns replacing it), `:218` untouched (its
line shifts only because the file above it shrinks).

**This is "fix the locator, not the assertion."** The line list *is* the locator. Re-deriving the JSON
does **not** fix this literal (Pitfall 7).

---

### 9. `firestarter/tests/golden/protocol_branch_inventory.json` (R) — re-derive, never hand-edit

**Analog: itself.** Live structure, verified this session: top-level `meta`, `sites` (24), `counts`,
`params_table`. Current state: 3 tier-1 + 21 tier-2, `blob_shas` matching HEAD exactly.

**Per-site shape** — note `reason` is **hand-authored**; `_extract_predicates` does not emit it, yet
`test_inventory_is_non_vacuous` (`:463-467`) asserts every site has a non-empty one:

```json
{
  "line": 71,
  "predicate": "switch (handle->protocol)",
  "keyed_on": ["protocol"],
  "tier": "protocol",
  "class": "algorithm_selector",
  "reason": "THE tier-1 algorithm-shape selector this gate exists to keep unique: ..."
}
```

**The four things to update, and only the first is machine-derived:**

1. `sites[]` — `(line, predicate, keyed_on, tier)`, straight from the re-derivation command below.
2. `sites[].reason` and `sites[].class` — **hand-authored.** Carry forward each surviving site's reason;
   author new ones. **Correct the `:328` entry** (`eprom_internal_ensure_regulator_enabled`): its reason
   currently claims the function is "used by callers outside the write path", which is false — zero
   callers anywhere.
3. `meta.blob_shas["src/proms/eprom.cpp"]` — computable **before** committing:
   `git hash-object src/proms/eprom.cpp` equals `git rev-parse HEAD:src/proms/eprom.cpp` for a committed
   file. Rewrite → `hash-object` → write into the golden → commit source **and** golden in the **same
   commit**, or `test_blob_shas_match_the_recorded_inventory` fails (Pitfall 8).
   `eprom_params.cpp`'s SHA is unchanged — leave it.
4. `counts.{total_sites,protocol_keyed_sites,other_sites}` — keep consistent with `sites[]`. Also update
   `meta.recorded_at_head` / `meta.recorded_by` (asserted by no test) and **re-point `meta.frozen_for`
   at Phase 142** — it currently anticipates *this* phase by name.

**The re-derivation command** — `meta.how_to_update` names it the only sanctioned route
("Diffing the extractor's live output against this JSON is the only sanctioned way to update it"), and
there is **no re-derivation script**; `_extract_predicates` exists only inside the test module:

```bash
cd /workspaces/firestarter && python3 -c "
import sys, json
sys.path.insert(0, 'tests')
import test_protocol_branch_inventory as m
live = m._extract_predicates((m._REPO_ROOT / 'src/proms/eprom.cpp').read_text())
print(json.dumps(live, indent=2))
print('tier1 lines:', sorted(s['line'] for s in live if s['tier'] == 'protocol'))
print('counts:', len(live), 'tier1:', sum(1 for s in live if s['tier']=='protocol'))
"
```

**Predict the before/after counts in the plan, then record the measured pair in the phase record.** The
golden's own `meta.frozen_for` says an unchanged site count across this phase "would itself be
suspicious." Deletions remove `:119`, `:131` (loop bounds), `:132` (the comparison) and possibly `:144`.

---

### 10. `/workspaces/tools/catalog/messages.toml` (M) — the canonical catalog

**Analog: the `0xB0` `MSG_ERR_NOT_BLANK` entry (`:543-552`) — it is already the exact
`[u24 hex_addr, u8]` 4-byte shape RESEARCH recommends for both new IDs:**

```toml
[[messages]]
id          = 0xB0
name        = "MSG_ERR_NOT_BLANK"
severity    = "ERROR"
format      = "Not blank, at 0x%06x, v: 0x%02x"
params      = [
    { type = "u24", render = "hex_addr" },
    { type = "u8", render = "hex_byte" },
]
wire_format = "id_frame"
```

Compare the current `0xB1` (`:554-564`), whose three-param shape becomes emitted-by-nothing on the 27C
path once the block loop dies:

```toml
[[messages]]
id          = 0xB1
name        = "MSG_ERR_WRITE_FAILED"
severity    = "ERROR"
format      = "Failed to write memory, 0x%06x, retries: %d, bad bytes: %d"
params      = [
    { type = "u24", render = "hex_addr" },
    { type = "u8" },
    { type = "u16" },
]
wire_format = "id_frame"
```

And the last-assigned ERROR slot, `0xBC` (`:662-668`), which the two new blocks should follow in id order:

```toml
[[messages]]
id          = 0xBC
name        = "MSG_ERR_FL4_BOOT_BLOCK_LOCKED"
severity    = "ERROR"
format      = "boot block locked -- 0x%06lx not programmable (W29C040 section 6.6 irreversible lockout)"
params      = [{ type = "u24", render = "hex_addr" }]
wire_format = "id_frame"
```

**Authoring rules, from the file's own header (`:1-11`):**

```toml
# Firestarter v1.2 log-message catalog (canonical source — meta-repo authoritative)
#
# DO NOT REORDER ENTRIES. Codegen sorts by id ascending; the source file order
# is preserved for human-edit diff readability.
#
# Distribution: copied byte-identically into firestarter/tools/catalog/ and
# firestarter_app/tools/catalog/ by tools/catalog/sync_to_subrepos.sh.
# Edit ONLY this meta-repo copy; run the sync script after every edit.
```

- Free ERROR-band slots: **`0xAE`, `0xBD`, `0xBE`, `0xBF`**. RESEARCH recommends `0xBD` + `0xBE`
  (contiguous, immediately after `0xBC`). After this phase **only two ERROR slots remain** — name that
  in the phase record for Phase 142/143's benefit.
- **Codegen Rule 9 is the easy one to trip:** the printf-specifier count must equal the non-`bytes`
  param count. `hex_addr` renders through `%s` in Python and `%06x` in the format string here —
  **check against `0xB0` rather than guessing.** Rule 9 fires at regen time, so a wrong shape is caught
  immediately, not silently.
- **No severity-band validation exists** — `validate_catalog()` enforces 10 rules, none tying `ERROR`
  to `0xA0..0xBF`. The band is convention.

**The distinct-ID-per-condition precedent** — `flash_intel.cpp:161-185` is a real in-tree analog for
D-04's "separately named on the wire", and its call-site shape is the one the two new failure paths
should mirror (emit → set `response_code` → clean up hardware → return):

```c
static bool flash_intel_poll_sr(firestarter_handle_t* handle, uint16_t timeout_ms) {
    unsigned long deadline = millis() + timeout_ms;
    while (millis() < deadline) {
        uint8_t sr = handle->firestarter_get_data(handle, 0);
        if (sr & 0x80) {
            if (sr & 0x10) {
                LOG_ERROR_ID(MSG_ERR_INTEL_VPP);              // 0xB4
                handle->response_code = RESPONSE_CODE_ERROR;
                handle->firestarter_set_data(handle, 0, 0xFF);
                return false;
            }
            if (sr & 0x08) {
                LOG_ERROR_ID(MSG_ERR_INTEL_PROGRAM);          // 0xB5
                handle->response_code = RESPONSE_CODE_ERROR;
                handle->firestarter_set_data(handle, 0, 0xFF);
                return false;
            }
            return true;
        }
    }
    LOG_ERROR_ID(MSG_ERR_INTEL_SR_TIMEOUT);                   // 0xB6
    handle->response_code = RESPONSE_CODE_ERROR;
    handle->firestarter_set_data(handle, 0, 0xFF);
    return false;
}
```

Three distinct IDs for three failure conditions on one loop — exactly D-04's shape, already shipped.
Use this to answer any "wouldn't a reason byte be cheaper?" reflex during planning: the house already
chose distinct IDs for this exact problem.

**Emission macros available** (`include/logging_id.h:105-110`):

```c
#define LOG_ERROR_ID(id)               LOG_ID(id)
#define LOG_ERROR_ID_U8(id, p1)        LOG_ID_U8((id), (p1))
#define LOG_ERROR_ID_U24(id, p1)       LOG_ID_U24((id), (p1))
#define LOG_ERROR_ID_U32(id, p1)       LOG_ID_U32((id), (p1))
#define LOG_ERROR_ID_BYTES(id, b, n)   LOG_ID_BYTES((id), (b), (n))
```

For a `(u24 address, u8 pulse_count)` payload, `LOG_ERROR_ID_BYTES(id, _b, 4)` with the `_b[]` packing
idiom from `eprom.cpp:182-191` / `memory.cpp:338-348`.

---

### 11. Generated + synced files (never hand-edit)

**Analog: `sync_to_subrepos.sh` itself.** The one command:

```bash
bash /workspaces/tools/catalog/sync_to_subrepos.sh
```

**Exactly which files move** (script lines cited):

| Repo | File | How it changes |
|---|---|---|
| meta | `tools/catalog/messages.toml` | **hand-authored** — the canonical edit |
| `firestarter/` | `tools/catalog/messages.toml` | copied (`:29`, `:38-55`) |
| `firestarter/` | `tools/catalog/codegen.py` | copied — byte-identical today, **zero diff** |
| `firestarter/` | `include/messages.h` | **generated** (`--language cpp`, `:79-82`) — two new `#define`s |
| `firestarter_app/` | `tools/catalog/messages.toml` | copied (`:30`) |
| `firestarter_app/` | `tools/catalog/codegen.py` | copied — zero diff |
| `firestarter_app/` | `firestarter/messages.py` | **generated** (`--language python`, `:92-95`) — two constants + two `MessageDef` entries |

**⚠️ Two latent defects in the script — its own success messages prove nothing.** Lines `:84` and `:97`
are `diff -q "$X" "$X"` — a file compared to **itself**:

```bash
if diff -q "$FS_ROOT/include/messages.h" "$FS_ROOT/include/messages.h" >/dev/null 2>&1; then
    echo "  OK: firestarter/include/messages.h regenerated."     # :84-86 — a tautology
fi
```

The genuine invariant checks are step 1's per-file `diff` (`:48`) and the cross-sub-repo comparison
(`:65`). **Verify the regen independently:**

```bash
git -C /workspaces/firestarter diff --stat -- include/messages.h tools/catalog/messages.toml
git -C /workspaces/firestarter_app diff --stat -- firestarter/messages.py tools/catalog/messages.toml
```

**Expected generated shapes** (so a plan can state the diff before running it):

```c
/* firestarter/include/messages.h — ID-only #define, aligned column */
#define MSG_ERR_FL4_BOOT_BLOCK_LOCKED     0xBC
```

```python
# firestarter_app/firestarter/messages.py:108 — the constant
MSG_ERR_WRITE_FAILED = 0xB1

# firestarter_app/firestarter/messages.py:625-633 — the MessageDef entry
    0xB1: MessageDef(
        id=0xB1,
        name="MSG_ERR_WRITE_FAILED",
        severity=SEVERITY_ERROR,
        format="Failed to write memory, 0x%06x, retries: %d, bad bytes: %d",
        params=(("u24", "hex_addr"), ("u8", "dec"), ("u16", "dec")),
        param_bytes=6,
        wire_format="id_frame",
    ),
```

Also: `codegen.py` writes `Total messages: 73` into both generated headers
(`messages.py:14`); it becomes **75**. **No test asserts that count**, so the header comment moving is
expected, not a gate.

**Never hand-normalize `messages.py`.** Codegen emits ruff-clean, format-stable output. And
`firestarter_app/tests/test_revision_constants_parity.py` scans `firestarter.h` (`CMD_*`, `FLAG_*`) and
`rurp_pinout.h` (`CTRL_*`) — **not `messages.h`** — so two new message IDs trip **no** existing host
parity gate. Adding a `messages.h`↔`messages.py` parity leg is Phase 144 / TEST-04. **Do not pre-build
it here.**

---

### 12. `firestarter/CLAUDE.md` (M) — the three Algorithm Handlers rows

**Analog: itself.** The current rows (verbatim, so the planner can diff a proposal against them):

| Protocol | VPP | Notes (current text) |
|---|---|---|
| `0x07` | 13V via `CTRL_VPP_VPE_DROP_ENABLE` | "…verify per pulse + 1 final full-array pass; `max_pulses` 25; no overprogram." |
| `0x08` | 13V via `CTRL_VPP_VPE_DROP_ENABLE` | "…verify per pulse + final full-array pass; `max_pulses` 25; no overprogram (D-06…)." |
| `0x0B` | 12–25V direct | "…verify per pulse, no final full-array pass; per-byte accumulated-energy cap 50ms; no overprogram." |

**Two things this phase makes newly false or newly true, and the plan must decide which:**

1. **`verify_mode`.** All three rows already *document* the `PLUS_FINAL` distinction. If the plan does
   not consume `verify_mode`, `0x07`/`0x08`'s "+ 1 final full-array pass" becomes false the moment the
   block loop (whose last action was always a full verify pass) is replaced. Either consume it or correct
   these rows — silence is not an option (RESEARCH Open Question 1 / A2).
2. **`0x08`'s "13V via `CTRL_VPP_VPE_DROP_ENABLE`" is already false today** — RESEARCH's DIP32 truth
   table shows the drop bit is cleared by the first `set_address` on any `pins >= 32` part. That is a
   pre-existing defect Phase 142 owns; naming it in the row (rather than silently fixing or silently
   keeping it) is the honest move D-09 asks for.

Also extend the **"Exception (Phase 140 D-11)"** paragraph in §"Native (Host) Test Environment" for the
sixth env (see §4).

---

### 13. `.planning/phases/141-.../141-NEW-TRACE.md` (N) — the D-10 artifact

**Analog: the dump harness output format (§6) + `140-PARAM-TABLE-RECORD.md` §7's precedent** for
recording a non-CI env's case/suite counts in prose rather than in a baseline JSON.

Record, at minimum: the `##### <TAG> total=N strobe_overflow=0 timing_overflow=0` banner per protocol,
the full entry list, the exact build+run commands, and the observed case/suite counts of the sixth env
(as `native_trace_v131` = 5/1 and `native_params_v131` = 9/1 are recorded). **Never** in
`size_baseline.json` or `size_baseline_v131.json`.

---

## Shared Patterns

### S1 — File header block (every new C/C++ and Python file)

**Source:** every file in the tree. Firmware/C++ form (`eprom_params.cpp:1-18`,
`test_trace_eprom_v131/host_stubs.cpp:1-50`):

```c
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase <N> Plan <NN> (<REQ-IDs>, <D-NNs>) -- <one-sentence purpose>.
 * <the constraint that a future reader would otherwise break>
 */
```

Python form (`test_protocol_branch_inventory.py:1-79`) — a docstring carrying `Requirements:`, the
defect class closed, a numbered `Coverage:` list matching the test functions 1:1, and an
`Environment seams:` section if any exist.

**Apply to:** the new suite `.cpp`, its `host_stubs.cpp`, the new pytest gate.

### S2 — PROGMEM read, always through the accessor

**Source:** `test_eprom_params_v131.cpp:179-184` (§6) and `eprom_params.cpp:53`.
**Apply to:** `configure_eprom`'s new table read and every table read in the new suite.
**Hoist all six reads once per block**, into locals, before the byte loop. Never inside it.

### S3 — Fail closed with zero hardware side effects

**Source:** `memory.cpp:67-71` (Phase 124 MERGE-04) — the canonical shape:

```c
if (rurp_pinmap_refuses(handle->cmd)) {
    LOG_ERROR_ID_U8(MSG_ERR_NOT_SUPPORTED, (uint8_t)handle->cmd);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;                     // operation pointers stay NULL; nothing is energised
}
```

Second instance: `eprom_params_for()` returning `NULL`, never `&EPROM_PARAMS[0]`
(`eprom_params.cpp:61`). Third: `configure_memory:138`'s terminal `configure_not_implemented(handle)`.

**Apply to:** D-03's pre-flight refusal and the `eprom_params_for() == NULL` refusal, both in
`configure_eprom`. Both must run **after** the `:69-76` fallback switch resolves `pulse_delay`.

### S4 — `messages.h` is codegen-generated and ID-only

**Source:** `sync_to_subrepos.sh` (§11) + `messages.h`'s own DO-NOT-EDIT header.
**Apply to:** anything tempted to `#define` a new id in `eprom.cpp`. Author in meta's `messages.toml`,
run the sync, verify with two `git diff --stat` calls. Two new IDs cost **call sites**, not PROGMEM
strings — the wording lives host-side.

### S5 — Positive-allowlist test plumbing

**Source:** `platformio.ini` — `[env:native]`'s `test_filter` (`:102-119`) **and** its parallel `-I` list
(`:124-140`). A suite directory is invisible to `pio test` until its path appears in `test_filter`, and
its headers are unreachable until a matching `-I test/native/avr/<dirname>` exists.
**Apply to:** the sixth env only — **never** to `[env:native]` or `[env:native_nodevtools]` (§4).

### S6 — Native-suite hygiene (five rules, each with a recorded reason)

| Rule | Source | Why |
|---|---|---|
| Fresh, zero-initialised handle per case | `test_eprom_params_v131.cpp:70-85` | `json_parse()` never resets `pulse_delay`/`protocol`/`mem_size`/`vpp_mv`/`pins` |
| Reset the register cache deliberately, **after** `configure_memory` | `test_trace_eprom_v131.cpp:97`, `:256` | the three globals default to `0xff` and persist across Unity cases; `0xff` ORs `CTRL_VPP_REGULATOR_ENABLE` into the first address write |
| Drive `firestarter_operation_main` directly, never `_init`, never the whole command | `test_trace_eprom_v131.cpp:243-253` | `eprom_write_execute` enables the regulator itself; and `command_done()` zeroes CONTROL on every exit, making a whole-command HV assertion vacuous |
| Never re-assign `firestarter_get_data`/`firestarter_set_data` | same comment | keeps the real primitives (and the verify read's bus activity) in the trace — D-05 as a test constraint |
| Mock `millis`/`micros` even if unused | `test_eprom_params_v131.cpp:64-65` | ArduinoFake **SIGABRTs** on any unmocked call |

### S7 — Committed-gate discipline (D-15)

**Source:** `test_protocol_branch_inventory.py` (§7a) + `test_vpp_seam_manual_on_every_board.py` (§7b).
**Apply to:** every new leg. Plant the violation, watch it go RED **for the reason it was planted**
(never a decode/import/path error), capture the transcript, then fix **the locator, not the assertion**.
Phase 140 recorded 12 planted-RED runs across three gates — match that standard.

Env seams bind at **import**: a planted-violation run must set `FIRESTARTER_BRANCH_SCAN_SOURCE` /
`FIRESTARTER_BRANCH_SCAN_PARAMS_SOURCE` in a **child process**, never via monkeypatch. **Unset them
afterwards** — a stray value left set makes tests 2/3/4/5 fail loudly (which is the safe direction, but
still a wasted debugging cycle).

### S8 — `pio` must run with cwd `/workspaces/firestarter`

**Source:** RESEARCH Pitfall 9 (verified). `/workspaces/platformio.ini` is a gitignored devcontainer file
carrying **two `[platformio]` sections**; `pio -d <dir>` and `-c` do **not** help.
**Apply to:** every `<automated>` verify block containing a `pio` call — each needs a leading
`cd /workspaces/firestarter && …`.

> ⚠️ **Compounding hazard, recorded from a prior failure in this project.** A planner once emitted the
> HTML-escaped form of `&&` (ampersand-a-m-p-semicolon, twice) into `<automated>` blocks, making 30/37
> verification legs unrunnable while self-reporting `bash -n` PASS. After writing the plans, check the
> bytes on disk: grepping the PLAN files for that escaped sequence must return **0** matches, and each
> block must pass `bash -n` **read from the file**, not from a re-typed copy. Scope the grep to
> `141-*-PLAN.md` only — this document quotes the sequence by description precisely so it cannot be a
> false positive.

### S9 — Use `-o addopts=""` for pytest

**Source:** `pytest` config carries `-ra -q` in `addopts`; doubling `-q` suppresses the count line.
**Apply to:** every pytest leg: `python3 -m pytest tests/ -q -o addopts=""`.

---

## No Analog Found

| File / construct | Role | Data Flow | Reason |
|---|---|---|---|
| The **pure overprogram arithmetic function** (`eprom_overprogram_us` or equivalent, D-08) | utility (pure) | transform | **No pure, hardware-free, table-free arithmetic function exists anywhere under `src/proms/` that is unit-tested in isolation.** The nearest structural analogs — `mem_util_calculate_lsb_register` / `_msb_register` (`memory.cpp:151-157`) — are the right *shape* (small, named, `mem_util_*`, declared in `memory_utils.h`) but take a `handle`, and `_top_address_register` additionally reads the register cache, so none is pure. **Planner should take the signature and boundary table from RESEARCH §"Overprogram arithmetic"** (which supplies six named cases including the `3 × 25 × 65535 = 4,915,125` overflow case and the "cap of zero" decision the plan must make and comment) rather than from any in-tree analog. Same applies to `mem_util_split_delay` — RESEARCH §"Code Examples 1" gives it and its 8-row boundary table. |

Everything else has an analog. Two near-misses worth naming so the planner does not go looking:

- **A firmware source-scan gate asserting a construct is absent** — `test_vpp_seam_manual_on_every_board.py:412-421`
  is the closest (§7b), but it scans a *header* for a `#define`, not a `.cpp` for an identifier, and its
  companion legs compile-and-run rather than scan. Treat it as a partial match on the assertion idiom
  only, and take the module conventions from `test_protocol_branch_inventory.py` instead.
- **A native suite asserting on the recorded timing stream** — the timing recorder exists
  (`host_stubs_common.inc:167-197`) and the hooks exist (`test_trace_eprom_v131.cpp:86-91`), but
  **no existing case asserts a bound on `timing_us(i)`.** The two smoke cases (`:120-134`) assert exact
  values for two direct calls. RESEARCH §"Code Examples 4" supplies the LOOP-07 assertion shape; it is
  new code, not a copy.

---

## Anti-Patterns — flag any of these in review

Each one is either recorded in-tree or measured by RESEARCH. Listed here so a plan's action text can
name the specific trap it is avoiding.

| Anti-pattern | Consequence | Where recorded |
|---|---|---|
| Dereferencing a PROGMEM field (`row->max_pulses`) | Compiles, passes **every** native test, returns RAM garbage on AVR. No native oracle exists | `eprom_params.h:71-79`; RESEARCH Pitfall 1 |
| Re-reading PROGMEM inside the byte loop | Slower and larger — each read is an `LPM` sequence | RESEARCH A4 |
| Implementing D-01's prose literally (`if (accumulated + pulse > cap) { emit; break; }`) | **101** pulses at 500 µs instead of 100, contradicting D-01's own worked example. Use `while (accumulated < cap)` | RESEARCH Pitfall 2 |
| `accumulated >= energy_cap_us` without the `energy_cap_us &&` guard | `0x07`/`0x08` abort after the **first** pulse — `0` means uncapped | `eprom_params.h:53`; RESEARCH Pitfall 3 |
| Branching on `protocol` for the DIP32 case | A **fourth** tier-1 site → `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines` RED. Branch on `handle->pins >= 32` | `test_protocol_branch_inventory.py:443-452` |
| Replacing the `:145` VPP predicate with the table's `vpp_path` | Tier-1 drops to 2 and the gate's error message becomes correct about a real regression. **Phase 142 owns it** | golden `meta.frozen_for` |
| Asserting "no CONTROL strobe during a verify read" | False — `mem_util_set_address:186` writes CONTROL unconditionally on **every** byte, for both pulse and verify | `memory.cpp:189`; RESEARCH's correction to the LOOP-08 premise |
| Asserting HV-disabled **after** the command completes | `command_done()` (`firestarter.cpp:162-171`) zeroes CONTROL regardless → passes vacuously | RESEARCH Pitfall 5 |
| Asserting "exactly one CONTROL strobe per block" | For a chip with `bus_config.rw_line == 22`, alternating pulse↔verify flips `CTRL_READ_WRITE` and re-strobes CONTROL **twice per byte** — expected, not a violation | RESEARCH §"LOOP-08 mechanics" |
| Adding a new `.cpp` under `src/` | `platform/py32f071/CMakeLists.txt`'s `FIRESTARTER_COMMON_SOURCES` must name it; `test_check_cmake_manifest.py::test_armed_and_passing_on_the_real_tree` runs against the real tree **inside CI-covered `pytest tests/ -v`**. **This is why D-06 puts the helper in `memory.cpp`** | RESEARCH §"Alternatives Considered" |
| Pairing `<Arduino.h>` with the `avr/pgmspace.h` shim in one **production** TU | 14 macro-redefinition warnings against a watermark at exactly **1166 with zero headroom** | F-140-01; `eprom_params.cpp:11-14` |
| Hand-editing `messages.h`, `messages.py`, or either sub-repo `tools/catalog/` copy | Diverges the moment codegen next runs | S4 |
| Re-freezing `_shared/eprom_v131_expected.h` | Its blob SHA is pinned by `test_golden_trace_identity_eprom_v131.py`; re-freezing is **Phase 144 / TEST-06** | RESEARCH §"Gates" |
| Adding the new suite to either pinned env | 141 cases / 17 suites assertion RED | §4 |
| Passing the sixth env name to `check_size_baseline.py` | Uncaught `KeyError` → exit 1, a **false regression signal** (F-138-05, accepted, not fixed) | §4 |
| `TEST_IGNORE_MESSAGE` to park a RED case | An IGNORED result does not demonstrate RED | `platformio.ini:100-101` |
| A new absence gate that quotes its own forbidden tokens verbatim | The gate matches **itself** and can never pass, or is scoped so loosely it matches nothing. Build needles by concatenation | `test_vpp_seam_manual_on_every_board.py:453-460` |
| `pio` invoked from `/workspaces` | `configparser.DuplicateSectionError` — two `[platformio]` sections | S8 |
| Counting `eprom_internal_ensure_regulator_enabled`'s deletion as reclaimed flash | It is already `--gc-sections`-collected: **0 B** | RESEARCH A5 |
| Mutating `handle->pulse_delay` outside the overprogram save/restore window | A failure between save and restore leaks a modified width into the handle. The existing loop restores only on success (`:172`) because the failure path returned into a torn-down command | RESEARCH Pitfall 11 |

---

## Metadata

**Analog search scope:**
`/workspaces/firestarter/{src/proms,include,test/native/avr,tests,tools/catalog,scripts/baseline}`,
`/workspaces/tools/catalog`, `/workspaces/firestarter_app/{firestarter,tools/catalog,tests}`,
`/workspaces/.planning/phases/140-parameter-table`.

**Files read in full this pass:** `firestarter/src/proms/eprom.cpp` (332),
`firestarter/src/proms/memory.cpp` (390), `firestarter/include/memory_utils.h` (33),
`firestarter/include/eprom_params.h` (85), `firestarter/src/proms/eprom_params.cpp` (62),
`firestarter/platformio.ini` (371), `firestarter/test/native/avr/_shared/host_stubs_common.inc` (353),
`firestarter/test/native/avr/test_trace_eprom_v131/host_stubs.cpp` (149),
`firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp` (397),
`firestarter/test/native/avr/test_eprom_params_v131/host_stubs.cpp` (39),
`firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp` (221),
`firestarter/tests/test_protocol_branch_inventory.py` (565),
`/workspaces/tools/catalog/sync_to_subrepos.sh` (102), `firestarter/CLAUDE.md`.

**Files read in targeted windows:** `firestarter/include/rurp_register_utils.h` (`:1-60`, `:86-100`),
`firestarter/include/rurp_shield.h` (`:114-136` grep), `firestarter/include/messages.h` (`:85-100`),
`firestarter/include/firestarter.h` (`:188-210`), `firestarter/include/logging_id.h` (`:105-110` grep),
`firestarter/src/proms/flash_intel.cpp` (`:150-189`),
`firestarter/tests/test_vpp_seam_manual_on_every_board.py` (`:1-96`, `:389-468`),
`/workspaces/tools/catalog/messages.toml` (`:1-20`, `:520-669`),
`firestarter_app/firestarter/messages.py` (`:1-25`, `:620-640`),
`firestarter/tests/golden/protocol_branch_inventory.json` (parsed programmatically).

**Files scanned (grep/listing only):** all 26 modules in `firestarter/tests/`, all 22 suite directories
in `firestarter/test/native/avr/`, `/workspaces/.claude/skills/` (4 skills: `devtest-rootcause`,
`devtest-triage`, `find-skills`, `skill-writer` — none applies to a firmware-loop phase).

**Project instructions honoured:** `/workspaces/CLAUDE.md` (meta-repo layout, constants-in-two-places
rule, protocol-sync rule) and `/workspaces/firestarter/CLAUDE.md` (dispatch order, Algorithm Handlers
table, native-env conventions incl. the Phase 140 D-11 exception).

**Pattern extraction date:** 2026-08-10
**Firmware tree state:** branch `gsd/v1.31-27c-programming-algorithm-fidelity`, HEAD `e2e25b5`
**Meta tree state:** `3345eed5`

⚠️ **Shelf life:** every `eprom.cpp` and `memory.cpp` line number in this document invalidates on the
**first commit that touches either file** — i.e. immediately once the phase starts. Later plans in the
phase must re-locate rather than quote this document. The `platformio.ini`, `host_stubs_common.inc`,
`messages.toml` and gate-module references are stable for the whole phase.
