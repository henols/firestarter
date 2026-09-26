# Phase 142: High-Voltage Routing - Pattern Map

**Mapped:** 2026-08-11
**Repo state:** `firestarter/` @ `4921388` on `gsd/v1.31-27c-programming-algorithm-fidelity`, working tree clean.
**Files analyzed:** 10 (3 created, 7 modified)
**Analogs found:** 9 / 10 with a usable in-tree analog; **1 with NO precedent** (composite `#define` in `rurp_pinout.h` - see §E)

> Every `file:line` below was re-read against the working tree at `4921388` during this pass. Where
> RESEARCH.md or CONTEXT.md cited a number I re-located it; four **new** stale citations are flagged
> inline (§A-6, §B-4, §J, §K-3). Do not paste a line number from CONTEXT.md without checking here.

---

## File Classification

| New/Modified file | Role | Data flow | Closest analog | Match |
|---|---|---|---|---|
| **C** `test/native/avr/test_vpp_eprom_v131/host_stubs.cpp` | test stub layer | event-driven recorder (record + inject) | `test/native/avr/test_loop_eprom_v131/host_stubs.cpp` (whole file, 281 lines) | **exact** |
| **C** `test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` | test (native Unity) | request-response drive + strobe assertion | `test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` | **exact** |
| **C** `command_done()` source-contract pytest leg | test (source-scan gate) | batch / file transform | `tests/test_write_path_source_contract_v131.py` | **exact** |
| **M** `include/rurp_pinout.h` (+2 `EPROM_HV_*` after `:97`) | config / constants header | compile-time | **none** - no bitwise-OR composite `#define` exists anywhere in `include/` | **NO ANALOG** |
| **M** `src/proms/eprom.cpp` (resolver, wrapper, `:217-219` delete, 4 composite conversions) | protocol handler | request-response + single-exit invariant | itself: `:173-182`, `:441-447`, `:449-454`; `include/eprom.h:18-35` for the expose-a-pure-helper form | **exact (self)** |
| **M** `src/proms/memory.cpp` (`:163-196` revision-gated preserve) | shared utility (bus layer) | transform | `src/proms/flash_intel.cpp:26-34` (in-`.cpp` revision guard) + `include/rurp_hw_rev_utils.h:15-41` (switch + fail-safe default) | **role-match** |
| **M** `platformio.ini` (2 lines into `[env:native_loop_v131]`) | config | n/a | `[env:native_loop_v131]` itself, `:404-414`; and `[env:native_params_v131]` `:361-371` | **exact** |
| **M** `tests/golden/protocol_branch_inventory.json` + `tests/test_protocol_branch_inventory.py:446` | test golden + pinned literal | batch derive | commits `876ce35` (golden) then `86128af` (literal) - Phase 141 plan 141-05 | **exact** |
| **M** `CLAUDE.md` (`:64`/`:65`/`:66` algorithm rows) | docs | n/a | commit `a0c4e08` (`docs(141-05)`) - **docs-only commit, NOT bundled with code** | **exact** |
| **M** `test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` (2 cases move) | test | request-response | itself - verbatim current text in §K | **exact (self)** |

---

# Pattern Assignments

## §A - `test_vpp_eprom_v131/host_stubs.cpp` (test stub layer, event-driven recorder)

**Analog:** `firestarter/test/native/avr/test_loop_eprom_v131/host_stubs.cpp` - **281 lines, copy ~95% verbatim.**

### A-0. The copy map, block by block

| Analog block | Lines | Disposition |
|---|---|---|
| File banner comment | `:1-48` | **REWRITE** - names Phase 141 plan 03 and lists exactly THREE opt-in layers. Must name Phase 142 / VPP-04 and **four**. Keep the two pitfall paragraphs (`:35-39`, `:41-47`) verbatim in substance. |
| `#include` block | `:50-57` | **VERBATIM** |
| The three opt-in `#define`s | `:60-69` | **VERBATIM** |
| `#define HOST_STUBS_CUSTOM_VOLTAGE_MV` | - | **NEW - the only added guard.** Must sit with the other three, i.e. before `:71`. |
| `#include "../_shared/host_stubs_common.inc"` | `:71` | **VERBATIM** (ordering is load-bearing) |
| `#include "rurp_register_utils.h"` **after** the `.inc` | `:73-80` | **VERBATIM** (comment included - it explains why AFTER) |
| `reset_register_cache` | `:82-95` | **VERBATIM** (comment + body) |
| readback model (`loop_readback_*` + `rurp_read_data_buffer`) | `:97-214` | **VERBATIM.** Rename `loop_` -> `vpp_` only if desired; there is no shared link step (`host_stubs_common.inc:16-20`), so verbatim names cannot collide with the sibling suite. |
| logged-id capture (`rurp_log_id` + accessors) | `:216-281` | **VERBATIM** - this is what makes "assert `MSG_ERR_VPP_HIGH` **by id**" possible; nothing else in the tree does it. |
| voltage mock | - | **NEW** - see §C. |

### A-1. The opt-in header block (VERBATIM + one added line)

`test_loop_eprom_v131/host_stubs.cpp:59-71`:

```c
/* Activate the ordered strobe recorder (opt-IN). MUST precede the include. */
#define HOST_STUBS_REAL_REGISTER_UTILS
/* Activate the timing recorder (opt-IN). MUST precede the include, and
 * requires HOST_STUBS_REAL_REGISTER_UTILS above -- its sequence key is
 * s_strobe_count, which only exists in that block (enforced by an #error in
 * the shared .inc if this is requested alone). */
#define HOST_STUBS_RECORD_TIMING
/* Opt OUT of the shared .inc's default rurp_read_data_buffer (always
 * returns 0), so this file can supply the stateful, 16-bit-keyed model
 * below instead. MUST precede the include. */
#define HOST_STUBS_CUSTOM_READ_DATA_BUFFER

#include "../_shared/host_stubs_common.inc"
```

The `#error` the second comment refers to is real - `host_stubs_common.inc:92-94`:

```c
#if defined(HOST_STUBS_RECORD_TIMING) && !defined(HOST_STUBS_REAL_REGISTER_UTILS)
#error "HOST_STUBS_RECORD_TIMING requires HOST_STUBS_REAL_REGISTER_UTILS (its sequence key is s_strobe_count, which only exists in that block)"
#endif
```

### A-2. `#include "rurp_register_utils.h"` AFTER the `.inc` - `:73-80` VERBATIM

```c
/* D-02/D-05 precedent (test_trace_eprom_v131): production's real
 * cache-compare + latch-strobe sequencing + timing ...
 * MUST come AFTER the shared .inc -- the .inc suppresses the real
 * declarations only inside its HOST_STUBS_REAL_REGISTER_UTILS arm. */
#include "rurp_register_utils.h"
```

### A-3. `reset_register_cache` - signature and body, `:91-95` VERBATIM

```c
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl) {
    lsb_address = lsb;
    msb_address = msb;
    control_register = ctrl;
}
```

Copy its comment too (`:82-90`) - it is the L-7 landmine in-source: the three globals are non-`static`,
`0xff`-initialised, and `0xff` ORs `CTRL_VPP_REGULATOR_ENABLE` into the first write of any case that forgets.

### A-4. The readback / converge model - `:132-214`

Struct + seed + reset (`:132-179`) and the keyed reader (`:200-214`) VERBATIM:

```c
struct loop_readback_entry_t {
    uint16_t addr16;
    uint8_t target;
    uint16_t converge_after;
    uint16_t read_count;
    uint8_t seeded;
};

#define LOOP_READBACK_MAX_ENTRIES 8
static loop_readback_entry_t s_loop_readback[LOOP_READBACK_MAX_ENTRIES];
```

```c
extern "C" uint8_t rurp_read_data_buffer(void) {
    uint16_t key = (uint16_t)((uint16_t)rurp_read_from_register(LEAST_SIGNIFICANT_BYTE)
                 | (uint16_t)((uint16_t)rurp_read_from_register(MOST_SIGNIFICANT_BYTE) << 8));
    for (int i = 0; i < LOOP_READBACK_MAX_ENTRIES; i++) {
        if (s_loop_readback[i].seeded && s_loop_readback[i].addr16 == key) {
            loop_readback_entry_t* e = &s_loop_readback[i];
            uint8_t result = (e->read_count < e->converge_after) ? 0xFF : e->target;
            e->read_count++;
            return result;
        }
    }
    /* Unseeded address: return 0xFF and do NOT silently create an entry --
     * the negative-control property loop_readback_seeded_count() proves. */
    return 0xFF;
}
```

**The converge contract, stated at `:124-129` and needed verbatim for the X4 (`MSG_ERR_VERIFY`) case:**
`converge_after = N` means the byte matches on read `N+1`, i.e. after exactly `N` pulses;
`loop_readback_reads(addr) == 1 + pulses`; a byte the loop skips under the `0xFF` rule is never read
(count stays 0). Because the model is **read-count sensitive**, a target that converges in the per-byte
loop and then mismatches on the final pass is expressible - that is X4's oracle.

### A-5. The `rurp_log_id` capture - `:243-281` VERBATIM

```c
extern "C" void clear_logged_ids(void) { s_logged_id_count = 0; s_logged_id_overflow = 0; }
extern "C" int      logged_id_count(void)          { return s_logged_id_count; }
extern "C" uint8_t  logged_id_at(int i)            { return s_logged_ids[i].id; }
extern "C" uint8_t  logged_id_param_count(int i)   { return s_logged_ids[i].param_count; }
extern "C" uint8_t  logged_id_param(int i, int j)  { return s_logged_ids[i].params[j]; }
extern "C" int      logged_ids_overflowed(void)    { return s_logged_id_overflow; }

extern "C" void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {
    if (s_logged_id_count >= LOOP_LOGGED_ID_MAX_ENTRIES) {
        s_logged_id_overflow = 1;  /* tail dropped; prefix stays valid */
        return;
    }
    loop_logged_id_entry_t* e = &s_logged_ids[s_logged_id_count];
    uint8_t n = (param_count > LOOP_LOGGED_ID_MAX_PARAMS) ? (uint8_t)LOOP_LOGGED_ID_MAX_PARAMS : param_count;
    e->id = id;
    e->param_count = n;
    for (uint8_t j = 0; j < n; j++) { e->params[j] = params[j]; }
    s_logged_id_count++;
}
```

Its comment (`:216-228`) carries the caveat the VPP-04(a) leg must respect: this captures **every** logged
frame including `LOG_DEBUG_ID_SUB`'s `MSG_DEBUG` entries, so filter by id (`count_logged_id`, §B-6),
never assume index 0 is your frame.

### A-6. Landmine already in this analog's own comments - do not copy blindly

- The `HOST_STUBS_REAL_REGISTER_UTILS` arm also `#define`s `HOST_STUBS_CUSTOM_HW_REVISION_BLOCK`
  (`host_stubs_common.inc:105`), which suppresses all four hw-revision stubs, so the **real**
  `rurp_get_hardware_revision()` runs and returns `rurp_get_config()->hardware_revision` == `0` ==
  `REVISION_0` from the zero-init `s_host_config` (`host_stubs_common.inc:310`). The narrower
  `HOST_STUBS_CUSTOM_HW_REVISION` guard lives inside `#if defined(HARDWARE_REVISION) &&
  !defined(HOST_STUBS_CUSTOM_HW_REVISION_BLOCK)` (`:289-296`), so it is **structurally dead** in this
  configuration - confirming RESEARCH's "incompatible". Do not add it. Override per case instead (§B-5).
- **New stale-citation flag:** the analog's own header comment cites
  `test_trace_eprom_v131/host_stubs.cpp:33-37` and `rurp_register_utils.h:12-14`; both still resolve.
  But `:100-130`'s derivation prose cites `memory.cpp` behaviour without line numbers - fine to copy.

---

## §B - `test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` (test, native Unity)

**Analog:** `test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` (1723 lines). Copy the
harness; author only the VPP cases.

### B-1. Includes + local kind constants - `:25-62` VERBATIM

```c
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <string.h>
#include <stdio.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"
#include "eprom.h"
#include "eprom_params.h"
#include "memory_utils.h"
#include "messages.h"  /* MSG_ERR_MAX_PULSES / MSG_ERR_ENERGY_CAP -- neither
                        * firestarter.h nor eprom.h/eprom_params.h/
                        * memory_utils.h pulls this in transitively. */

using namespace fakeit;

#define STROBE_KIND_DATA     1
#define STROBE_KIND_PIN      2
#define TIMING_KIND_DELAY_US 3
#define TIMING_KIND_DELAY_MS 4
```

`messages.h` is what makes `MSG_ERR_VPP_HIGH` / `MSG_WARN_VPP_HIGH` / `MSG_WARN_VPP_LOW` /
`MSG_WARN_REV0_VPP_UNSUPPORTED` nameable - keep it. `REVISION_2_2` / `REVISION_1` / `REVISION_UNKNOWN`
(`rurp_shield.h:25-31`) and `CTRL_*` arrive transitively via `firestarter.h`; the analog uses
`REVISION_2_2` at `:1524` with no extra include. `rurp_get_config()` likewise.

### B-2. `extern "C"` seam declarations - `:72-105` VERBATIM, plus one line

```c
extern "C" void    clear_strobes();
extern "C" int     strobe_count();
extern "C" int     strobe_overflowed();
extern "C" uint8_t strobe_kind(int i);
extern "C" uint8_t strobe_pin(int i);
extern "C" uint8_t strobe_value(int i);

extern "C" void     clear_timings();
extern "C" int      timing_count();
extern "C" int      timing_overflowed();
extern "C" uint8_t  timing_kind(int i);
extern "C" uint32_t timing_us(int i);
extern "C" int      timing_after_strobe(int i);
extern "C" void     timing_push(uint8_t kind, uint32_t us);

extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);

extern "C" void loop_readback_reset(void);
extern "C" void loop_readback_seed(uint16_t addr16, uint8_t target, uint16_t converge_after);
extern "C" int  loop_readback_reads(uint16_t addr16);
extern "C" int  loop_readback_seeded_count(void);

extern "C" void     clear_logged_ids(void);
extern "C" int      logged_id_count(void);
extern "C" uint8_t  logged_id_at(int i);
extern "C" uint8_t  logged_id_param_count(int i);
extern "C" uint8_t  logged_id_param(int i, int j);
extern "C" int      logged_ids_overflowed(void);
```

**ADD:** `extern "C" void set_mock_vpp_mv(uint16_t mv);` - the §C seam's setter.

### B-3. `setUp` - the four-timing-function mock block, `:111-141` VERBATIM

```c
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();

    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysDo([](unsigned int us) {
        timing_push(TIMING_KIND_DELAY_US, (uint32_t)us);
    });
    When(Method(ArduinoFake(), delay)).AlwaysDo([](unsigned long ms) {
        timing_push(TIMING_KIND_DELAY_MS, (uint32_t)ms);
    });
    /* Unused by any case in this plan, but ArduinoFake SIGABRTs on any
     * unmocked call -- cheap insurance matching house convention. */
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);

    clear_strobes();
    clear_timings();
    clear_logged_ids();
    loop_readback_reset();
    reset_register_cache(0x00, 0x00, 0x00);
}
```

**This is the C-2 fix.** `test_flash_intel_vpp.cpp:55-65` mocks only `delay` - that is the suite that
SIGABRTs. All four go in. **ADD** `set_mock_vpp_mv(0);` here (the `test_flash_intel_vpp.cpp:60`
precedent puts the voltage reset in `setUp`).

### B-4. `tearDown` - unconditional revision reset, `:143-151` VERBATIM

```c
void tearDown(void) {
    /* ... reset any hardware-revision override back to the file's default
     * (REVISION_0, via host_stubs_common.inc's zero-initialised
     * s_host_config) so it can never leak into a case that runs after one
     * of the DIP32 cases below -- Unity calls tearDown() even when a case
     * fails via TEST_ASSERT's longjmp, so this reset is unconditional and
     * always runs. */
    rurp_get_config()->hardware_revision = 0;
}
```

Note `test_flash_intel_vpp.cpp:67-68` has an **empty** `tearDown` - do not copy that one.
**New stale-citation flag:** the analog's comment cites `host_stubs_common.inc`'s `s_host_config`
without a line; it is at `host_stubs_common.inc:310`, not `:306` as RESEARCH's landmine section says.

### B-5. Handle factory - COPY, then **one mandatory change**

`test_loop_eprom_v131.cpp:164-176`:

```c
[[maybe_unused]] static firestarter_handle_t make_loop_handle(uint32_t protocol, uint8_t pins, uint32_t mem_size,
                                                                uint32_t pulse_delay_us, const bus_config_t& bus_config) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.pins = pins;
    h.mem_size = mem_size;
    h.pulse_delay = pulse_delay_us;
    h.bus_config = bus_config;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    return h;
}
```

> **MUST CHANGE - this is the vacuity trap D-13 named.** `make_loop_handle` never sets `vpp_mv`, so it
> is `0`, and `eprom_check_vpp`'s compares are `0 > 0 + 500` (false) and `0 < 0 * 95 / 100` (false) -
> **exactly** the `test_val_eprom.cpp:74` failure mode. The new factory must take a `vpp_mv` setpoint,
> as `test_flash_intel_vpp.cpp:77-90`'s `make_intel_handle(uint16_t vpp_setpoint, uint32_t ctrl_flags)`
> does (`h.vpp_mv = vpp_setpoint;` at `:82`, `h.chip_id = 0;` at `:84` to skip the chip-id branch,
> `ctrl_flags | FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE` at `:83`).
> **Do NOT copy `test_flash_intel_vpp.cpp:85-88`** (the four `h.firestarter_* = mock_*` assignments) -
> that is the C-5 interception defect.

Keep `LOOP_BUS_CONFIG_0x07` / `_0x08` / `_0x0B` **verbatim** from `:201-246` including their derivation
comments (`:178-246`). A zeroed `bus_config` is degenerate, not identity.

### B-6. `drive_vpp_init(...)` - copy the SHAPE from `drive_loop_write`, change the terminal call

`test_loop_eprom_v131.cpp:275-288` (the analog):

```c
[[maybe_unused]] static void drive_loop_write(firestarter_handle_t* h, uint32_t base,
                                               const uint8_t* block, uint8_t n) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();
    clear_timings();
    clear_logged_ids();
    h->address = base;
    h->data_size = n;
    for (uint8_t i = 0; i < n; i++) {
        h->data_buffer[i] = (char)block[i];
    }
    h->firestarter_operation_main(h);
}
```

| Element | Disposition for `drive_vpp_init` |
|---|---|
| `configure_memory(h)` first | **VERBATIM** - installs `eprom_internal_set_control_register` via `configure_eprom:65-66`, which is the remap C-5 says must stay in the path. |
| `reset_register_cache(0,0,0)` **after** `configure_memory` | **VERBATIM** - `configure_memory` calls `mem_util_set_address(handle, 0)` at `memory.cpp:97`, so the cache must be reset after it, not before. |
| three `clear_*()` calls after that | **VERBATIM** - scopes the capture to the drive. |
| `h->firestarter_operation_main(h)` | **CHANGE to `h->firestarter_operation_init(h)`** - VPP-04 needs `eprom_check_vpp`, reached only via `_init` (`eprom_generic_init:412-413`, installed as the default at `configure_eprom:43`). |
| `base` / `block` / `n` seeding | **OPTIONAL** - an `_init` drive needs no data block; keep the parameter only if a case also drives `_main`. |
| the "never `_init`, never the whole command" comment `:256-267` | **REWRITE** - the "never the whole command / `command_done()` would zero the register" half still applies verbatim and is the vacuity guard; the "never `_init`" half is exactly inverted here and must say so. |

### B-7. The strobe accessors - `:1136-1173` VERBATIM (all three)

```c
static int control_write_count(void) {
    int n = strobe_count();
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) == STROBE_KIND_PIN && strobe_pin(i) == CONTROL_REGISTER && strobe_value(i) == 1) c++;
    }
    return c;
}

static int control_write_strobe_index(int idx) {
    int n = strobe_count();
    int c = 0;
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) == STROBE_KIND_PIN && strobe_pin(i) == CONTROL_REGISTER && strobe_value(i) == 1) {
            if (c == idx) return i;
            c++;
        }
    }
    return -1;
}

/* The Nth (0-indexed) non-elided CONTROL_REGISTER write's PHYSICAL byte
 * value -- i.e. AFTER rurp_map_ctrl_reg_for_hardware_revision's per-
 * revision remap ... */
static int control_write_value(int idx) {
    int strobe_idx = control_write_strobe_index(idx);
    if (strobe_idx <= 0 || strobe_kind(strobe_idx - 1) != STROBE_KIND_DATA) return -1;
    return (int)strobe_value(strobe_idx - 1);
}
```

Every non-elided CONTROL write appears as a fixed 3-entry group (`:1122-1134`):
`[DATA pin=0 value=physical byte]`, `[PIN pin=CONTROL_REGISTER value=1]`, `[PIN ... value=0]`.
`control_write_value` reads the DATA entry immediately before the rise. `-1` means "not decodable" and
every assertion in the analog checks `v >= 0` first - keep that.

Also copy `count_logged_id` / `find_logged_id` (`:426-441`) and `first_genuine_pulse_strobe_index`
(`:1183-1193`):

```c
static int count_logged_id(uint8_t id) {
    int n = logged_id_count();
    int c = 0;
    for (int i = 0; i < n; i++) { if (logged_id_at(i) == id) c++; }
    return c;
}

static int find_logged_id(uint8_t id) {
    int n = logged_id_count();
    for (int i = 0; i < n; i++) { if (logged_id_at(i) == id) return i; }
    return -1;
}
```

### B-8. The revision override idiom - `:1511-1524` VERBATIM

```c
    /* Override the hardware-revision mapping to REVISION_2_2 for the
     * duration of this case (reset unconditionally in tearDown()) so the
     * recorded PHYSICAL control byte does not conflate CTRL_ADDRESS_LINE_16
     * and CTRL_VPP_VPE_DROP_ENABLE -- on the default REVISION_0/1 mapping
     * both remap onto the SAME physical bit (0x01) ... On REVISION_2_x they
     * map to distinct physical bits: CTRL_ADDRESS_LINE_16_REV2 (0x20) vs
     * CTRL_VPP_VPE_DROP_ENABLE_REV2 (0x01). This changes nothing about the
     * LOGICAL behaviour under test ... it only disambiguates what THIS test
     * can prove from the strobe stream. */
    rurp_get_config()->hardware_revision = REVISION_2_2;
```

Mandatory for every drop-bit assertion (L-6), **and** mandatory for every VPP-04 case: on the default
`REVISION_0` `eprom_check_vpp` takes the early return at `eprom.cpp:334-338` and never reaches the
over-voltage compare, making D-15(a) silently vacuous.

### B-9. The D-15(b) assertion idiom - `:1269-1283` VERBATIM (last-clear + paired non-vacuity)

```c
    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n >= 2, "non-vacuity: at least the top-of-block assert and the budget-failure disable must both have written CONTROL");

    int last = control_write_value(n - 1);
    TEST_ASSERT_TRUE_MESSAGE(last >= 0, "the last CONTROL write must be a genuine, decodable value");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_REGULATOR_ENABLE) == 0,
        "the LAST control value emitted by operation_main must have CTRL_VPP_REGULATOR_ENABLE CLEAR -- eprom_internal_report_budget_failure's own disable");

    bool saw_earlier_set = false;
    for (int i = 0; i < n - 1; i++) {
        int v = control_write_value(i);
        if (v >= 0 && (v & CTRL_VPP_REGULATOR_ENABLE)) { saw_earlier_set = true; break; }
    }
    TEST_ASSERT_TRUE_MESSAGE(saw_earlier_set,
        "an EARLIER control value must have CTRL_VPP_REGULATOR_ENABLE SET -- otherwise the 'last value clear' assertion is vacuously true of a register that was never energised at all");
```

The VPP-04(b) leg is this shape with `(last & CTRL_VPP_VPE_DROP_ENABLE_REV2) == 0` added.

### B-10. The strobe-walk idiom - `:1658-1663` VERBATIM (every-value assertion with a per-index message)

```c
    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n > 0, "non-vacuity: the block must have produced at least one CONTROL write");
    for (int i = 0; i < n; i++) {
        int v = control_write_value(i);
        char msg[80];
        snprintf(msg, sizeof(msg), "control write %d (0x%02X) must carry CTRL_VPP_VPE_DROP_ENABLE_REV1 -- pins<32 keeps it in the preserve mask", i, v);
        TEST_ASSERT_TRUE_MESSAGE(v >= 0 && (v & CTRL_VPP_VPE_DROP_ENABLE_REV1) != 0, msg);
    }
```

Every LOOP-08 case pairs a positive walk with `TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), ...)`
as a soundness precondition (`:1407`, `:1466`, `:1499`, `:1544`, `:1587`, `:1655`) - copy that too.

### B-11. `main()` - `:1666-1723` shape VERBATIM

```c
int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    RUN_TEST(test_setup_leaves_all_three_recorders_clean);
    /* ... one RUN_TEST per case, grouped by requirement with a comment
     *     header naming the plan and task, e.g.:
     * // LOOP-08 (plan 141-08, task 3) */
    return UNITY_END();
}
```

The analog's own first case (`:301-308`) is the harness self-check worth copying verbatim as
`test_setup_leaves_all_three_recorders_clean` - it proves the recorders start clean.

---

## §C - The `HOST_STUBS_CUSTOM_VOLTAGE_MV` seam contract

**Seam definition, `test/native/avr/_shared/host_stubs_common.inc:274-278` VERBATIM:**

```c
#ifndef HOST_STUBS_CUSTOM_VOLTAGE_MV
extern "C" uint16_t rurp_read_voltage_mv() {
    return 0;
}
#endif
```

**Contract:** the guard is read at include time. The suite must `#define HOST_STUBS_CUSTOM_VOLTAGE_MV`
**before** `#include "../_shared/host_stubs_common.inc"` (documented at `host_stubs_common.inc:22-23`;
every suite restates the pitfall), and must then supply exactly:

```c
extern "C" uint16_t rurp_read_voltage_mv()
```

no parameters (declared `include/rurp_shield.h:140`).

**Working consumer - `test/native/avr/test_flash_intel_vpp/host_stubs.cpp:27-39`, copy the seam usage:**

```c
/* Opt out of the shared defaults for the two mockable symbols. The shared
 * include conditions its `rurp_read_voltage_mv` and `rurp_get_hardware_revision`
 * definitions on the absence of these macros. */
#define HOST_STUBS_CUSTOM_VOLTAGE_MV
#define HOST_STUBS_CUSTOM_HW_REVISION

#include "../_shared/host_stubs_common.inc"

/* Suite-local mockable VPP voltage — TU-private state; test TU calls
 * set_mock_vpp_mv() to inject a value before calling into flash_intel_write_init. */
static uint16_t s_mock_vpp_mv = 0;
extern "C" void set_mock_vpp_mv(uint16_t mv) { s_mock_vpp_mv = mv; }
extern "C" uint16_t rurp_read_voltage_mv() { return s_mock_vpp_mv; }
```

**Copy `:30` + `:37-39` only.** Explicitly do NOT copy:

| Do not copy | Why | Evidence |
|---|---|---|
| `#define HOST_STUBS_CUSTOM_HW_REVISION` (`:31`) and the `:41-47` block | Structurally dead once `HOST_STUBS_REAL_REGISTER_UTILS` is on: that flag defines `HOST_STUBS_CUSTOM_HW_REVISION_BLOCK` (`host_stubs_common.inc:105`) and the narrower guard lives inside `#if defined(HARDWARE_REVISION) && !defined(HOST_STUBS_CUSTOM_HW_REVISION_BLOCK)` (`:289-296`) | source-verified |
| its `setUp` (`test_flash_intel_vpp.cpp:55-65`) | mocks `delay` only; the suite SIGABRTs mid-run (C-2) | RESEARCH C-2, measured |
| its interception mechanism (`test_flash_intel_vpp.cpp:182` re-assigning `h.firestarter_set_control_register` after `configure_memory`) | On the EPROM family this removes `eprom_internal_set_control_register`'s VPE->P1 remap (`eprom.cpp:441-447`) from the path under test | C-5 |
| its SAF-04 assertions verbatim (`:185-189`, using `s_ctrl_writes_with_p1_low` / `s_last_ctrl_reg`) | Those read a handle-level mock, not the post-remap physical byte, and the case has **never been observed to run** | C-2 |

**Use instead:** §B-9's `control_write_value(n-1)` + `saw_earlier_set` pairing, which observes the
post-remap physical byte *below* `rurp_write_to_register`'s elision.

The SAF-04 case's *intent* is still worth quoting into the new case's comment -
`test_flash_intel_vpp.cpp:159-171`:

```
 * SAF-04 regression: high-VPP ERROR must leave the regulator cleared.
 * ... the original write_init early-returned on RESPONSE_CODE_ERROR without
 * driving CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_P1_ENABLE low, leaving 12V
 * applied to socket pin 1 after the firmware had just detected unsafe
 * over-voltage — the exact hazard the safety check exists to prevent.
```

---

## §D - The `command_done()` source-contract pytest leg

**Analog:** `firestarter/tests/test_write_path_source_contract_v131.py` (593 lines, 12 legs, all green).
The whole module is the template. Copy the skeleton; author the needles.

### D-1. Module skeleton and file location - `:138-155` VERBATIM shape

```python
import os
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_EPROM_REL = "src/proms/eprom.cpp"
_MEMORY_REL = "src/proms/memory.cpp"

# Environment seam -- binds at IMPORT time. See the module docstring's
# "Environment seams" section above.
_SCAN_EPROM = Path(
    os.environ.get("FIRESTARTER_WRITE_PATH_SCAN_SOURCE", str(_REPO_ROOT / _EPROM_REL))
)
_SCAN_MEMORY = _REPO_ROOT / _MEMORY_REL
```

For `command_done()` the target is `src/firestarter.cpp`. The env-seam pattern is what makes the D-15
planted-RED run possible **without editing the real file**: point the seam at a fixture copy in a child
process (the module docstring at `:98-101` states the seam binds at import, so a post-import
monkeypatch will not work).

> **`_HERE`-resolution landmine, already closed by this analog:** `_REPO_ROOT = _HERE.parent` plus
> `test_scan_targets_are_non_vacuous`'s `p.resolve().is_relative_to(_REPO_ROOT)` assertion
> (`:536-541`) is the deliberate fix for the `check_permitted_claims.py` defect where `_HERE` resolved
> to the wrong phase dir. Copy both halves.

### D-2. `_strip_comments` - `:203-235` VERBATIM

Shape-preserving comment stripper (a newline stays a newline) so **every line number in the result
matches the original file exactly**. Copy verbatim; do not re-invent.

### D-3. The def-count / call-count assertion shape - `:187-190` + `:395-406` VERBATIM

Compiled patterns:

```python
_BUDGET_FAILURE_DEF_RE = re.compile(r"\bvoid\s+eprom_internal_report_budget_failure\s*\(")
_BUDGET_FAILURE_CALL_RE = re.compile(
    r"\beprom_internal_report_budget_failure\s*\(\s*handle\s*,"
)
```

Assertions:

```python
    def_count = len(_BUDGET_FAILURE_DEF_RE.findall(stripped))
    call_count = len(_BUDGET_FAILURE_CALL_RE.findall(stripped))
    assert def_count == 1, (
        "expected exactly 1 definition of the per-byte budget-failure "
        f"reporter in {_EPROM_REL}, found {def_count}.\n"
        f"Got (comment-stripped {_EPROM_REL}):\n{stripped}"
    )
    assert call_count >= 2, (
        "expected at least 2 call sites of the per-byte budget-failure "
        f"reporter in {_EPROM_REL} (one per LOOP-05 budget limit), found "
        f"{call_count}.\nGot (comment-stripped {_EPROM_REL}):\n{stripped}"
    )
```

**This is the exact shape both new legs need:**
- **command_done:** one `def` match for `void command_done(firestarter_handle_t* handle) {`, three
  `rurp_write_to_register(<REG>, 0x00)` matches, and `>= 2` call sites. Ground truth
  (`src/firestarter.cpp:162-171`, `:176`, `:290`):

```c
void command_done(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CMD_FINISHED);
    rurp_set_programmer_mode();
    rurp_chip_disable();
    rurp_write_to_register(CONTROL_REGISTER, 0x00);
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
    handle->cmd = CMD_IDLE;
    rurp_set_communication_mode();
}
```
  `grep -n command_done src/firestarter.cpp` -> `30` (decl), `162` (def), `176` (timeout-abort arm),
  `290` (`if (finished)` arm). Exactly two call sites; assert `>= 2` **and** name both arms, so a
  future deletion of the abort arm fails.
- **VPP-03 one-resolver:** one `def` of the resolver, `>= 2` calls, and **zero** remaining
  `handle->protocol == 0x0B` occurrences.

### D-4. The `_NEEDLE_*` self-match-avoidance trick - `:157-173` VERBATIM

```python
# ---------------------------------------------------------------------------
# Concatenation-built needles. Coverage 12 asserts none of these appear
# verbatim anywhere in this module's own source -- see the module docstring
# and the plan's own warning: a gate that quotes its forbidden tokens
# verbatim matches itself and can never pass.
# ---------------------------------------------------------------------------
_NEEDLE_RETRY_MACRO = "NUMBER" + "_OF_RETRIES"
_NEEDLE_PROGRAM_MISMATCHED_BYTES = "program_mismatched" + "_bytes"
_NEEDLE_VERIFY_AND_UPDATE_MASK = "verify_and_update" + "_mask"
_NEEDLE_MISMATCH_BITMASK = "mismatch_bit" + "mask"

_ALL_SELF_CHECK_NEEDLES = (
    ("the retry-count macro", _NEEDLE_RETRY_MACRO),
    ...
)
```

Plus the helper `:283-290`:

```python
def _assert_identifier_absent(needle, label, stripped, target_rel):
    matches = re.findall(r"\b" + re.escape(needle) + r"\b", stripped)
    assert matches == [], (
        f"found {len(matches)} occurrence(s) of {label} in the "
        f"comment-stripped {target_rel} -- ...\nGot:\n{stripped}"
    )
```

And the self-check leg `:578-593`:

```python
def test_own_needles_do_not_appear_verbatim_in_this_module():
    own_text = Path(__file__).read_text()
    for label, needle in _ALL_SELF_CHECK_NEEDLES:
        assert needle not in own_text, (
            f"the concatenation-built needle for {label} appears verbatim "
            "in this module's own source -- rebuild it from at least two "
            "literal pieces so this gate cannot match itself."
        )
```

**Relevant to VPP-03:** the absence needle for `handle->protocol == 0x0B` must be concatenation-built
for the same reason. Also note the **naming note** at `:116-126`: two legs were deliberately named
after what a function *did* rather than its identifier, because the obvious test name would itself
contain the needle. The VPP-03 leg has the same hazard.

### D-5. The two mandatory self-protection legs - `:519-576` VERBATIM

- `test_scan_targets_are_non_vacuous` (`:519-546`) - target exists, non-empty, resolves inside the
  repo, comment-stripped text non-empty. A missing target must **FAIL**, never pass.
- `test_this_module_cannot_be_silently_skipped` (`:549-575`) - the module's own text contains no
  `pytest.skip`, no `mark.skipif`, no `importorskip`, each checked via a concatenation-built needle:

```python
    own_text = Path(__file__).read_text()
    skip_call = "pytest" + ".skip"
    skipif_marker = "mark" + ".skipif"
    dependency_skip_call = "importor" + "skip"
```

### D-6. Legs in this analog that Phase 142 must not break

`test_write_path_source_contract_v131.py` pins, against `src/proms/eprom.cpp`:

| Leg | Pin | Phase-142 consequence |
|---|---|---|
| `:395-401` | `def_count == 1` for `eprom_internal_report_budget_failure` | **Do not rename or delete it.** Making it a caller of the shared composite is fine. |
| `:402-406` | `call_count >= 2` | unaffected |
| `:382-394` | `firestarter_set_data`, `firestarter_get_data`, `MSG_ERR_MAX_PULSES`, `MSG_ERR_ENERGY_CAP` all `> 0` | unaffected |
| `:430-456` | exactly one `mem_util_delay_us(handle->pulse_delay)` in **each** of `eprom.cpp` and `memory.cpp` | the wrapper must not duplicate or drop `eprom.cpp:405` |
| `:194` `_ALLOWED_DELAY_US_ARGS = {"settling","strobe","rem"}` scanned over `src/ include/ lib/ platform/` | any new `delayMicroseconds(x)` with a non-literal, non-allowed arg name anywhere fails | do not add one |

---

## §E - `include/rurp_pinout.h`: two `EPROM_HV_*` composites after `:97`

### E-1. **NO composite-`#define` precedent exists. Stated plainly.**

```
$ grep -rn "^#define [A-Z_0-9]*  *(.*|.*)" include/ | wc -l
0
```

There is **no** bitwise-OR composite `#define` anywhere in `include/`, let alone in `rurp_pinout.h`.
This is a genuinely new construct in this header. Two nearest things:

**(a) Single-token macro alias** - the only "derived macro" form the header uses, three instances:

```c
rurp_pinout.h:76    #define CTRL_ADDRESS_LINE_16          CTRL_VPP_VPE_DROP_ENABLE
rurp_pinout.h:115   #define CTRL_ADDRESS_LINE_16_REV1          CTRL_VPP_VPE_DROP_ENABLE_REV1
rurp_pinout.h:127   #define CTRL_ADDRESS_LINE_18_REV2          CTRL_VPP_P1_ENABLE_REV2
```

`:128` is C-4's alias - on Rev 2-class logical A18 and logical P1 are the same physical `0x08`.
Note CONTEXT's `canonical_refs` range `:107-126` **omits `:128`**; the block is `:105-129`.

**(b) The recorded 0-B `#define` rule** - `rurp_pinout.h:63-64` VERBATIM, the authority D-07 rests on:

```c
// #define (NOT constexpr) per Phase 33 D-07 — preprocessor constants resolve
// at compile time and contribute 0 B to the .hex until referenced.
```

**(c) The idiom the composite replaces** - the same OR-list spelled inline, repeatedly:

```
src/proms/eprom.cpp:195   CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1
src/proms/eprom.cpp:327   CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE, 0
src/proms/eprom.cpp:345   CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1
src/proms/eprom.cpp:393   CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 0
src/proms/eprom.cpp:409   CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE, 0
src/proms/flash_5v_page.cpp:147/156/172   CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE
src/proms/eeprom_28c.cpp:251              CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE
src/hardware_operations.cpp:28            CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE
```

`flash_5v_page.cpp` and `eeprom_28c.cpp` are **out of scope** - the composite is `EPROM_`-scoped per
C-4; do not "helpfully" convert them.

### E-2. Placement and per-variant structure to match

Insert after `:97` (the close of the wide arm), before `:99`'s `CTRL_ADDRESS_LINE_13`. The arms to be
correct in both:

```c
rurp_pinout.h:74    #ifndef HARDWARE_REVISION
rurp_pinout.h:75    #define CTRL_VPP_VPE_DROP_ENABLE      0x01
rurp_pinout.h:76    #define CTRL_ADDRESS_LINE_16          CTRL_VPP_VPE_DROP_ENABLE
...
rurp_pinout.h:85    #else
rurp_pinout.h:88    #define CTRL_ADDRESS_LINE_16          0x01
rurp_pinout.h:96    #define CTRL_VPP_VPE_DROP_ENABLE      0x100
rurp_pinout.h:97    #endif
```

A composite placed **after** `:97` expands at the use site and therefore picks up whichever arm is
live automatically - no `#ifdef` duplication needed. (CONTEXT D-02's cite of `:95-96` for
"`0x01` vs `0x100`" is wrong; `:95` is `CTRL_VPP_REGULATOR_ENABLE 0x80`. The correct pair is `:88` + `:96`.)

### E-3. Naming - collision check re-run this pass

```
$ grep -rn "EPROM_HV" . --include=*.h --include=*.cpp --include=*.c --include=*.inc --include=*.py
(no output)
```

Free. The header is `extern "C"`-bracketed (`:37-39` / `:131-133`); `#define`s are unaffected by that
but keep the insertion inside the existing brackets for consistency.

---

## §F - `src/proms/memory.cpp`: the revision-gated drop-bit preserve

### F-1. The site to change - `:163-196` VERBATIM (current text)

```c
rurp_register_t mem_util_calculate_top_address_register(firestarter_handle_t* handle, uint32_t address) {
    rurp_register_t top_address = ((uint32_t)address >> 16) & (CTRL_ADDRESS_LINE_16 | CTRL_ADDRESS_LINE_17 | CTRL_ADDRESS_LINE_18 | CTRL_READ_WRITE);
    // CTRL_VPE_ENABLE, CTRL_VPP_P1_ENABLE, CTRL_VPP_A9_ENABLE and CTRL_VPP_REGULATOR_ENABLE are
    // UNCONDITIONALLY preserved below — this is why VPE survives a per-byte verify read. ...
    rurp_register_t mask = CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_VPP_REGULATOR_ENABLE;
    if (handle->pins < 32) {
        // ... [18-line comment, :173-187, whose last three lines hand this choice to Phase 142] ...
        mask |= CTRL_VPP_VPE_DROP_ENABLE;
    }
    top_address |= rurp_read_from_register(CONTROL_REGISTER) & mask;

    if (handle->pins == 28) {
        top_address |= CTRL_ADDRESS_LINE_17;
    }
    return top_address;
}
```

Exact anchors: mask init `:171`, guard `:172`, comment `:173-187`, `mask |= CTRL_VPP_VPE_DROP_ENABLE;`
`:188`, closing brace `:189`, preserve OR-in `:190`, `pins == 28` A17 force `:192-194`.
The `:173-187` comment **must be rewritten** - it currently asserts the stripping is deliberate and
hands the choice to Phase 142 by name.

### F-2. Revision-conditional analog - the in-`.cpp` house form

The **only** three `rurp_get_hardware_revision()` call sites outside the mapper:

```
src/proms/eprom.cpp:334        if (rurp_get_hardware_revision() == REVISION_0) {
src/proms/flash_intel.cpp:29   if (rurp_get_hardware_revision() == REVISION_0) {
src/hardware_operations.cpp:20 if (rurp_get_hardware_revision() == REVISION_0) {
```

Full instance - `src/proms/flash_intel.cpp:26-37`:

```c
static void flash_intel_check_vpp(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CHECK_VPP_INTEL);
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        LOG_WARN_ID(MSG_WARN_REV0_VPP_UNSUPPORTED);
        handle->response_code = RESPONSE_CODE_WARNING;
        return;
    }
#endif
```

**Two things this establishes:** (1) every revision read in a `.cpp` is wrapped in
`#ifdef HARDWARE_REVISION` - mandatory, `rurp_get_hardware_revision()` does not exist otherwise
(`rurp_shield.h:149-151`, `rurp_hw_rev_utils.h:4`); (2) the `.cpp` form is a plain `if`, not a switch.

### F-3. The fail-safe-`default` form - `include/rurp_hw_rev_utils.h:15-41` VERBATIM

This is the pattern the new arm's **direction** must match:

```c
uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    uint8_t ctrl_reg = 0;
    uint8_t hw = rurp_get_hardware_revision();
    switch (hw) {
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2:
    case REVISION_2_3:  // <-- NEW (D-07 — ctrl-reg layout identical to REV_2_x per §4 row 6)
        ctrl_reg = data & (CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_ADDRESS_LINE_17 | CTRL_READ_WRITE | CTRL_VPP_REGULATOR_ENABLE);
        ctrl_reg |= data & CTRL_VPP_VPE_DROP_ENABLE ? CTRL_VPP_VPE_DROP_ENABLE_REV2 : 0;
        ctrl_reg |= data & CTRL_ADDRESS_LINE_16 ? CTRL_ADDRESS_LINE_16_REV2 : 0;
        ctrl_reg |= data & CTRL_ADDRESS_LINE_18 ? CTRL_ADDRESS_LINE_18_REV2 : 0;
        break;
    case REVISION_0:
    case REVISION_1:
        ctrl_reg = data;
        ctrl_reg |= data & CTRL_VPP_VPE_DROP_ENABLE ? CTRL_VPP_VPE_DROP_ENABLE_REV1 : 0;
        break;
    default:
        // REVISION_UNKNOWN + any unrecognized byte fall through to ctrl_reg = 0
        // (fail-safe — no VPP enables, no VPE enables; EEPROM override is the
        // operator escape hatch per RESEARCH §Caller Audit row 3).
        break;
    }

    return ctrl_reg;
}
```

**Three properties the new `memory.cpp` arm must copy:**
1. **Rev 2-class is an explicit four-case set**, `REVISION_2_0 | 2_1 | 2_2 | 2_3` - never a
   `>= REVISION_2_0` range test. `rurp_shield.h:25-31` values are `0,1,2,3,4,5,0xFE`, so a range test
   would silently swallow a future `REVISION_2_4`.
2. **The fail-safe direction is the `default` doing nothing.** `REVISION_UNKNOWN` (`0xFE`) must fall
   into the arm that keeps **today's** stripping - i.e. the new preserve must be added only in the
   positive Rev-2 arm, never subtracted in a negative arm.
3. **The comment states the fail-safe direction in words** next to the `default`. Do the same.

Skeleton the executor should pattern-match (structure only, values are the plan's):

```c
    rurp_register_t mask = CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_VPP_REGULATOR_ENABLE;
    if (handle->pins < 32) {
        mask |= CTRL_VPP_VPE_DROP_ENABLE;
    }
#ifdef HARDWARE_REVISION
    else {
        switch (rurp_get_hardware_revision()) {
        case REVISION_2_0:
        case REVISION_2_1:
        case REVISION_2_2:
        case REVISION_2_3:
            mask |= CTRL_VPP_VPE_DROP_ENABLE;   /* D-01/D-02 */
            break;
        default:
            /* REVISION_0 / REVISION_1 / REVISION_UNKNOWN and any
             * unrecognised byte keep TODAY'S stripping -- on Rev 0/1 the
             * drop bit and A16 map onto the same physical 0x01. */
            break;
        }
    }
#endif
```

**Callability:** `rurp_get_hardware_revision()` is declared in `rurp_shield.h:151`, which `memory.cpp`
already includes (`memory.cpp:24`), so no new include edge. `REVISION_*` come from `rurp_shield.h:25-31`,
inside that file's own `#ifdef HARDWARE_REVISION` at `:22` - hence the `#ifdef` wrapper is mandatory.

### F-4. The no-leak proof's own analog

D-02's amendment owes a native case driving a 32-pin **non-EPROM** protocol (`0x10`) at
`REVISION_2_2`. The negative-control shape already exists in the analog suite -
`test_loop_eprom_v131.cpp:1477-1508` (`test_loop08_route_presence_is_not_vacuous`): it drives a
**different** operation (`h.cmd = CMD_BLANK_CHECK` set **before** `configure_memory`) through the
identical accessor filter and asserts the bit is ABSENT throughout. Copy that shape.

---

## §G - `src/proms/eprom.cpp`: resolver, wrapper, composite conversions

`eprom.cpp` is its own best analog. Every construct this phase needs already exists in the file.

### G-1. Expose-a-pure-helper-to-a-native-oracle precedent - `include/eprom.h:18-35` VERBATIM

The house pattern for RESEARCH Open Question 4 (expose the resolver or keep it file-static):

```c
    /*
     * Phase 141 Plan 04 (LOOP-03, D-08) -- pure overprogram-duration
     * arithmetic. Exposed here (not file-static in eprom.cpp) because D-08
     * requires direct native testing: overprogram_factor is 0 on all three
     * shipped eprom_params rows (0x07/0x08/0x0B), so the per-byte write
     * loop can never reach this path with today's data, and a pure
     * function is the only possible oracle for LOOP-03's correctness.
     * ...
     */
    uint32_t eprom_overprogram_us(uint8_t pulse_count, uint32_t pulse_us, uint8_t factor, uint32_t cap_us);
```

Shape to copy: a non-`static` declaration in `eprom.h` inside the `extern "C"` block, with a comment
that states **why** it is exposed rather than file-static. The header includes only `firestarter.h`
(`eprom.h:11`), so a `firestarter_handle_t*` parameter is already available; a `rurp_register_t`
return type is **not** (`rurp_pinout.h` / `rurp_types.h` are not included there) - either return
`rurp_register_t` and add the include, or return `uint16_t`, or keep the resolver file-static.

### G-2. `static` helper + disable form - `:162-182` VERBATIM

The model for both the wrapper's inner `static` function and the "one place a disable happens":

```c
/*
 * Phase 141 Plan 04 (LOOP-05, D-04) -- the single place a per-byte program
 * budget failure is reported. Disables the VPP route exactly as the old
 * block-loop's failure path did ... This covers only LOOP-05's own two
 * budget-failure exits; generalising the disable to every exit in the file
 * is Phase 142 / VPP-02's job, which re-verifies every exit rather than
 * assuming this one.
 */
static void eprom_internal_report_budget_failure(firestarter_handle_t* handle, uint32_t address, uint8_t pulse_count, uint8_t msg_id) {
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 0);
    ...
    handle->response_code = RESPONSE_CODE_ERROR;
}
```

Note `static` + a block comment naming the plan/decision it implements + an explicit hand-off sentence.
**This function's name is pinned by `test_write_path_source_contract_v131.py:395-401`** - convert its
`:174` mask to the composite, do not rename it.

### G-3. The four hand-rolled disables to convert (all re-verified this pass)

```c
eprom.cpp:174   handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 0);
eprom.cpp:327   handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE, 0);
eprom.cpp:393   handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 0);
eprom.cpp:409   handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE, 0);
```

### G-4. The remap layer the composite must respect - `:440-447` VERBATIM

```c
// Use this function to set the control register and flip CTRL_VPE_ENABLE bit to CTRL_VPE_ENABLE or CTRL_VPP_P1_ENABLE
void eprom_internal_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle)) {
        bit &= ~CTRL_VPE_ENABLE;
        bit |= CTRL_VPP_P1_ENABLE;
    }
    ep_set_control_register(handle, bit, state);
}
```

Installed for every EPROM command at `configure_eprom:65` (`ep_set_control_register = handle->firestarter_set_control_register;`),
with the file-scope function pointer declared non-`static` at `:36`. **Consequence for the composite:
name `CTRL_VPE_ENABLE`, never `CTRL_VPP_P1_ENABLE`** - naming both makes `:443` strip VPE from the mask
so the physical VPE line is never cleared.

### G-5. The two predicates the resolver replaces - byte-identical text, `:190` and `:340`

```c
eprom.cpp:189       if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0) {
eprom.cpp:190           if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {
eprom.cpp:192               handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
eprom.cpp:193           } else {
eprom.cpp:195               handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1);
eprom.cpp:196           }
eprom.cpp:197           delay(500);  // settle stays amortised once per block -- the whole of LOOP-08
eprom.cpp:198       }
```

```c
eprom.cpp:340       if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {
eprom.cpp:342           handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
eprom.cpp:343       } else {
eprom.cpp:345           handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1);
eprom.cpp:346       }
```

### G-6. The block D-04 deletes - `:200-219` VERBATIM (comment + branch)

```c
    // D-09: on a 32-pin part, mem_util_calculate_top_address_register's
    // preserve mask (memory.cpp) excludes CTRL_VPP_VPE_DROP_ENABLE whenever
    // handle->pins >= 32, ... Choosing the final DIP32
    // route (P1 vs drop resistor) and consolidating the mask sets is
    // Phase 142 / VPP-01 and VPP-03 -- this branch deliberately does not
    // pre-empt that choice.
    if (handle->pins >= 32) {
        handle->firestarter_set_control_register(handle, CTRL_VPP_VPE_DROP_ENABLE, 0);
    }
```

### G-7. The `PROGMEM` row-read idiom the resolver must use - `:221-234` VERBATIM

```c
    const eprom_params_t* row = eprom_params_for(handle->protocol);
    if (row == NULL) {
        // Already refused in configure_eprom (task 2) -- unreachable in
        // practice. Re-checked here so this function never dereferences a
        // NULL row on its own; returns without touching hardware further.
        return;
    }
    uint32_t overprogram_cap_us = pgm_read_dword(&row->overprogram_cap_us);
    uint32_t energy_cap_us      = pgm_read_dword(&row->energy_cap_us);
    uint8_t  max_pulses         = pgm_read_byte(&row->max_pulses);
    uint8_t  overprogram_factor = pgm_read_byte(&row->overprogram_factor);
    uint8_t  verify_mode        = pgm_read_byte(&row->verify_mode);
    uint8_t  vpp_path           = pgm_read_byte(&row->vpp_path);
    (void)vpp_path;  // hoisted for completeness; Phase 142 / VPP-01 is its consumer
```

`(void)vpp_path;` at `:234` is the seam awaiting this phase. **Removing it while leaving `vpp_path`
unread on some path emits an unused-variable warning against the zero-headroom 1166 watermark.**
The contract that forces `pgm_read_*` - `include/eprom_params.h:71-78`:

```c
/*
 * Linear-scans the protocol_id-keyed table and returns a POINTER INTO
 * PROGMEM -- every field must be read back with pgm_read_byte /
 * pgm_read_dword, never dereferenced directly (a direct read compiles and
 * silently returns RAM garbage on AVR). Returns NULL when no row matches
 * `protocol`, so an unrecognised value fails closed with zero hardware
 * side effects (D-05); it never returns a default row.
 */
const eprom_params_t* eprom_params_for(uint32_t protocol);
```

And the enum the resolver switches on - `eprom_params.h:43-46`:

```c
/* vpp_path names an ABSTRACT route, not a control-register bitmask -- Phase
 * 142 owns the mask sets, and naming a mask here would force this
 * dependency-free header to pull in the shield's register header. */
enum { VPP_PATH_DROP_RESISTOR = 0, VPP_PATH_DIRECT_VPE = 1 };
```

### G-8. The exits the wrapper must cover, and the dead code beside them

`eprom_write_execute` is `:184-315`. Its five exits: `:226` (`row == NULL`), `:268`, `:275`,
`:311` (`MSG_ERR_VERIFY` - the headline gap, quoted below), `:315` (success fall-through).

```c
eprom.cpp:309                LOG_ERROR_ID_BYTES(MSG_ERR_VERIFY, _b, 5);
eprom.cpp:310                handle->response_code = RESPONSE_CODE_ERROR;
eprom.cpp:311                return;
```

`eprom_write_init` is `:127-145`; single `return` at `:131`.

Dead code adjacent to the rewrite - `:449-454` VERBATIM, zero callers, duplicates the `:189-198` guard:

```c
void eprom_internal_ensure_regulator_enabled(firestarter_handle_t* handle) {
    if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0) {
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
        delay(500);
    }
}
```

Its tier-2 inventory site is `:450`; touching it moves the golden. Decide deliberately (L-10).

---

## §H - `platformio.ini`: the two lines into `[env:native_loop_v131]`

**Analog: the env itself.** Current text, `platformio.ini:404-414` VERBATIM:

```ini
platform = native
test_framework = unity
test_filter =
	native/avr/test_loop_eprom_v131
build_flags =
	${env:native.build_flags}
	-I test/native/avr/test_loop_eprom_v131
lib_deps =
	fabiobatsilva/ArduinoFake@^0.4.0
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>
test_build_src = yes
```

`test_loop_eprom_v131` appears in **exactly two** places - `:407` (`test_filter`) and `:410` (`-I`).
Both are required (Phase 119 D-04). The new suite gets one tab-indented line after each. Indentation is
a **hard tab**, matching `:407` / `:410`.

The env header comment (`:373-403`) is the analog for what a new env would need; **this phase adds no
env**, so nothing there changes. `[env:native_params_v131]` (`:361-371`) is the identical two-list shape,
confirming the pattern is stable across two prior phases.

Restate in the record: a bare `pio test -e native_loop_v131` will then report **2 suites** and
`39 + N` cases instead of `1 suite / 39 cases`. That figure is asserted by no gate.

---

## §I - The D-18 golden re-derivation

**Analog: Phase 141 plan 141-05, TWO commits.** This is the exact precedent to copy, including the
commit-message shape.

### I-1. Commit 1 - `876ce35` `test(141-05): re-derive protocol-branch-inventory golden after the loop rewrite`

Touched **one file** (`tests/golden/protocol_branch_inventory.json`, `+79 / -51`). Message body shape:

```
D-11: the per-byte loop rewrite (141-04) moved this inventory. Re-derived
sites[] verbatim from _extract_predicates (never hand-typed) against the
committed src/proms/eprom.cpp -- 27 total sites (was 24): tier-1 holds at
exactly 3 (now at lines 70/190/340), tier-2 grew 21->24 (6 added, 3 removed).

- 3 removed: <named, with why>
- 6 added: <each named with its line and what it is>
- Corrected the :450 (was :328) reason: <the one prose correction, justified>
- meta.blob_shas.src/proms/eprom.cpp updated to the current committed blob;
  eprom_params.cpp's SHA is untouched (no table value moved).
- meta.frozen_for re-pointed at Phase 142 (VPP-branch rewrite at :190/:340).

Surviving sites' hand-authored reason/class text carried forward verbatim
per plan instruction; a few contain now-stale internal line cross-references
... -- documented in 141-05-SUMMARY.md rather than silently rewritten, since
the plan named exactly one correction.

Leaves test_protocol_branch_inventory.py:446's hard-coded [71, 145, 218]
literal unedited -- that is task 2's own commit.
```

Every element is a required beat: which sites moved, added/removed counts with reasons, what was
**not** touched, and where the deferred half went.

### I-2. Commit 2 - `86128af` `test(141-05): re-pin the tier-1 line locator to the post-rewrite sites`

The whole diff, VERBATIM:

```diff
@@ -443,9 +443,9 @@ def test_branch_sites_match_the_recorded_inventory():
 def test_exactly_three_protocol_keyed_sites_at_the_pinned_lines():
     live = _extract_predicates(_SCAN_EPROM.read_text())
     protocol_lines = sorted(s["line"] for s in live if s["tier"] == "protocol")
-    assert protocol_lines == [71, 145, 218], (
-        "expected exactly three tier-protocol sites at lines [71, 145, "
-        f"218], found {protocol_lines}. A fourth protocol-keyed branch "
+    assert protocol_lines == [70, 190, 340], (
+        "expected exactly three tier-protocol sites at lines [70, 190, "
+        f"340], found {protocol_lines}. A fourth protocol-keyed branch "
         "site is a second algorithm selector and a TABLE-05 violation -- "
         "fewer than three means one of the pinned sites was removed "
         "without updating this inventory."
```

**The literal appears in three places in one assertion** - the list, the message prefix, and the
f-string. All three moved together. Current state, `tests/test_protocol_branch_inventory.py:443-452`:

```python
def test_exactly_three_protocol_keyed_sites_at_the_pinned_lines():
    live = _extract_predicates(_SCAN_EPROM.read_text())
    protocol_lines = sorted(s["line"] for s in live if s["tier"] == "protocol")
    assert protocol_lines == [70, 190, 340], (
        "expected exactly three tier-protocol sites at lines [70, 190, "
        f"340], found {protocol_lines}. A fourth protocol-keyed branch "
        ...
    )
```

That commit's message also carries the D-15 planted-RED transcript beats verbatim - copy this shape:

```
D-15 proof the leg is armed, not merely quiet (both run in a child process
against a scratch copy under /tmp, via FIRESTARTER_BRANCH_SCAN_SOURCE, seam
unset afterwards -- env | grep -c FIRESTARTER_BRANCH_SCAN reports 0):
- Planted violation A (inserted a fourth `handle->protocol == 0x08` branch):
  RED, found [70, 190, 219, 345] -- four tier-1 lines, failing on the
  assertion itself.
- Planted violation B (removed the :340 site's handle->protocol read):
  RED, found [70, 190] -- two tier-1 lines, failing on the assertion itself.
```

Note the **env-seam-in-a-child-process** technique and the explicit "seam unset afterwards" proof.
`_SCAN_EPROM` is `Path(os.environ.get("FIRESTARTER_BRANCH_SCAN_SOURCE", _REPO_ROOT / _EPROM_REL))`
(`tests/test_protocol_branch_inventory.py:97-99`), binding at import.

### I-3. Golden structure to preserve

Re-verified this pass:

```
top-level keys : ["meta", "sites", "counts", "params_table"]
meta keys      : sources, blob_shas, recorded_at_head, recorded_by, requirement,
                 decision, why_two_checks, how_to_update, frozen_for, allowlist_rationale
site key order : ["line", "predicate", "keyed_on", "tier", "class", "reason"]
counts         : {"total_sites": 27, "protocol_keyed_sites": 3, "other_sites": 24}
meta.sources   : ["src/proms/eprom.cpp", "src/proms/eprom_params.cpp"]
recorded_by    : "Phase 141 Plan 05"      -> becomes "Phase 142 Plan NN"
```

`meta.how_to_update` is at json `:16`, `meta.frozen_for` at `:17`, `meta.allowlist_rationale` at `:18`
(the one with the stale `:145/:218/:320/:71` prose, C-6 - fix during re-derivation), `sites` array
opens at `:20`, `counts` at `:294`.

**The gate compares only `(line, predicate, keyed_on, tier)`** - `tests/test_protocol_branch_inventory.py:417-440`:

```python
    recorded = [(s["line"], s["predicate"], s["keyed_on"], s["tier"]) for s in inventory["sites"]]
    live = [(s["line"], s["predicate"], s["keyed_on"], s["tier"])
            for s in _extract_predicates(_SCAN_EPROM.read_text())]
```

`class` and `reason` are hand-authored prose the extractor cannot produce - budget for re-writing a
`reason` paragraph per moved site. Blob-SHA leg, `:398-414`, reads the **committed** blob
(`git rev-parse HEAD:<path>`), so it goes RED only after commit, while the sites leg reads the working
tree and goes RED on the first keystroke. Both are fixed by re-deriving **in the same commit** as the
source change - or, following the 141-05 precedent, in the commit immediately after, with the
`protocol_lines` literal in a third.

---

## §J - `firestarter/CLAUDE.md`: the `0x07`/`0x08`/`0x0B` rows

### J-1. **Correction to CONTEXT: the house pattern is a SEPARATE docs-only commit, not "the same commit as the code."**

CONTEXT's Integration Points and L-11 both say the rows "must move in the same change." Checked: of the
last 10 commits touching `CLAUDE.md`, **zero** also touched `src/proms/`:

```
a0c4e08 docs(141-05): reconcile Algorithm Handlers rows with the shipped loop   :: CLAUDE.md
e2e25b5 fix(140-06): correct CLAUDE.md Algorithm Handlers rows + record D-11    :: CLAUDE.md
6029423 feat(141-03): add [env:native_loop_v131], extend CLAUDE.md exception    :: CLAUDE.md platformio.ini
96b3138 docs(101-02): sync CLAUDE.md dispatch/handler tables to PROTO_ tokens   :: CLAUDE.md
```

The invariant the tree actually holds is **same plan / same phase**, in a `docs(NNN-NN):`-prefixed
docs-only commit. That is also the safer reading here: L-2 wants all `eprom.cpp` edits in one commit
so the blob-SHA gate goes RED once, and bundling a `CLAUDE.md` prose edit into it adds nothing.

### J-2. Analog: commit `a0c4e08` (`docs(141-05)`) - the exact edit shape

Three table rows replaced in place, each a single line. Current rows: `CLAUDE.md:64` (`0x07`),
`:65` (`0x08`), `:66` (`0x0B`); header at `:62`, section heading `### Algorithm Handlers` at `:57`.

The `0x08` row's two Phase-142-stale spans, verbatim from `:65`:

- **VPP column:** `13V via CTRL_VPP_VPE_DROP_ENABLE (pre-existing defect on this row -- see Notes)`
- **Notes paragraph:** `**Pre-existing defect, not introduced by Phase 141:** on this `pins == 32` row,
  `mem_util_calculate_top_address_register`'s preserve mask excludes `CTRL_VPP_VPE_DROP_ENABLE`
  whenever `handle->pins >= 32`, so the drop bit asserted above does not survive the block's first
  `set_address()` -- it is cleared before the first pulse is ever emitted, on every board revision (not
  a bit collision: ...). Phase 141 makes the clearing explicit and observable via a named
  `handle->pins >= 32` branch (`eprom.cpp`) instead of leaving it incidental; choosing the final route
  (P1 vs. drop resistor) and consolidating the mask sets is Phase 142 / VPP-01 and VPP-03's job.`

The `0x07` and `0x0B` rows' VPP columns are `13V via CTRL_VPP_VPE_DROP_ENABLE` and `12–25V direct`.

**Also stale, and NOT in CONTEXT's list:** `CLAUDE.md:114`, in the `### Constants` section at `:110`:

```
- `CTRL_VPP_VPE_DROP_ENABLE (0x01 legacy / 0x100 rev2)` — drop VPE through resistor to VPP level
```

That description ("drop VPE through resistor to VPP level") is correct and is in fact D-01's own
level-selector framing - worth citing rather than editing.

### J-3. Commit-message beats from `a0c4e08` to copy

- One bullet per row changed, naming what claim moved and its source of truth (`eprom_params.cpp`, an
  id + hex, a measured figure).
- An **arithmetic correction** called out explicitly, with the method: *"Verified by brute-force search
  over all w in [1, 50000] before writing the number down."*
- A closing negative statement: *"Does not touch the 'Native (Host) Test Environment' section -- plan
  141-03's native_loop_v131 paragraph is untouched."*

For Phase 142 the equivalent closing beat is D-03's non-claim: state that the row change describes the
**emitted control-register stream**, not silicon behaviour.

---

## §K - `test_loop_eprom_v131.cpp`: the two cases that move

Both are extracted verbatim so an executor rewriting assertions has the current text in front of it.

### K-1. `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route` - `:1246-1284`, WIDENED

```c
void test_loop05_the_loops_own_strobes_disable_the_high_voltage_route(void) {
    /* Same drive as the case above -- re-seeded fresh (setUp() clears all
     * three recorders and the register cache between cases). */
    firestarter_handle_t h = make_loop_handle(0x07, 28, 65536, 100, LOOP_BUS_CONFIG_0x07);
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    loop_readback_seed(0, block[0], 1);
    loop_readback_seed(1, block[1], 65535);
    loop_readback_seed(2, block[2], 1);
    loop_readback_seed(3, block[3], 1);
    drive_loop_write(&h, 0, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "response_code (sanity, matches the case above)");

    /* VACUITY TRAP, named explicitly -- this is why this case exists rather
     * than driving the whole command: command_done() (src/firestarter.cpp:
     * 162-171) writes CONTROL_REGISTER = 0x00 on EVERY command exit,
     * unconditionally. An assertion driven through the whole command would
     * pass even if eprom_write_execute's own budget-failure path disabled
     * nothing at all, because command_done() would zero the register
     * anyway on the way out. drive_loop_write calls
     * firestarter_operation_main DIRECTLY (never the whole command, never
     * command_done()), so this assertion is scoped to eprom_write_execute's
     * OWN CONTROL strobes and is therefore meaningful. */
    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n >= 2, "non-vacuity: at least the top-of-block assert and the budget-failure disable must both have written CONTROL");

    int last = control_write_value(n - 1);
    TEST_ASSERT_TRUE_MESSAGE(last >= 0, "the last CONTROL write must be a genuine, decodable value");
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_REGULATOR_ENABLE) == 0,
        "the LAST control value emitted by operation_main must have CTRL_VPP_REGULATOR_ENABLE CLEAR -- eprom_internal_report_budget_failure's own disable");

    bool saw_earlier_set = false;
    for (int i = 0; i < n - 1; i++) {
        int v = control_write_value(i);
        if (v >= 0 && (v & CTRL_VPP_REGULATOR_ENABLE)) { saw_earlier_set = true; break; }
    }
    TEST_ASSERT_TRUE_MESSAGE(saw_earlier_set,
        "an EARLIER control value must have CTRL_VPP_REGULATOR_ENABLE SET -- otherwise the 'last value clear' assertion is vacuously true of a register that was never energised at all");
}
```

**Change needed:** add a drop-bit leg to the `last` assertion. **This case runs on the DEFAULT
`REVISION_0`** - it sets no revision override - so `CTRL_VPP_VPE_DROP_ENABLE_REV1` (`0x01`) is
indistinguishable from `CTRL_ADDRESS_LINE_16` there. A drop-bit assertion in this case therefore also
needs `rurp_get_config()->hardware_revision = REVISION_2_2;` (§B-8) and
`CTRL_VPP_VPE_DROP_ENABLE_REV2`. Widening the assertion without adding the override would be
undecidable, not merely weak.

### K-2. `test_loop05_a_successful_block_does_not_disable_the_route` - `:1286-1309`, MUST STAY GREEN

```c
void test_loop05_a_successful_block_does_not_disable_the_route(void) {
    /* Paired negative control: a block that fully converges must leave the
     * route SET. Without this, the case above would pass on an
     * implementation that disables the route unconditionally on every
     * exit -- generalising disable-on-every-exit to every exit in the file
     * is Phase 142 / VPP-02's job; this phase satisfies only LOOP-05's own
     * budget-failure exit. */
    ...
    TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_REGULATOR_ENABLE) != 0,
        "a SUCCESSFUL block must leave CTRL_VPP_REGULATOR_ENABLE SET -- nothing in this phase's scope disables it on the success path");
}
```

This is C-1's tiebreaker and the reason D-10's wrapper is conditional on `RESPONSE_CODE_ERROR`.
**No edit.** Its comment's "is Phase 142 / VPP-02's job" sentence becomes stale prose once the wrapper
lands - updating that sentence (not the assertion) is the honest move.

### K-3. `test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse` - `:1573-1632`, INVERTED

```c
void test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse(void) {
    /* Same handle shape as the case above -- same override reasoning. */
    rurp_get_config()->hardware_revision = REVISION_2_2;

    firestarter_handle_t h = make_loop_handle(0x08, 32, 262144, 100, LOOP_BUS_CONFIG_0x08);
    const uint32_t base = 0x00FFFEUL;
    const uint8_t block[4] = {0x3C, 0x55, 0xAA, 0x0F};
    const uint16_t keys[4] = {0xFFFE, 0xFFFF, 0x0000, 0x0001};
    for (int i = 0; i < 4; i++) {
        loop_readback_seed(keys[i], block[i], 1);
    }
    drive_loop_write(&h, base, block, 4);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "response_code");
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "strobe_overflowed -- small block, must be sound");

    int n = control_write_count();
    TEST_ASSERT_TRUE_MESSAGE(n >= 2, "non-vacuity: at least the top-of-block assert (drop SET) and the explicit pins>=32 clear must both have written CONTROL");

    int first_pulse_idx = first_genuine_pulse_strobe_index(block, 4);
    TEST_ASSERT_TRUE_MESSAGE(first_pulse_idx >= 0, "non-vacuity: a genuine chip-data pulse must have been recorded");

    /* [D-09 finding, in full] the drop bit is excluded from
     * mem_util_calculate_top_address_register's preserve mask whenever
     * handle->pins >= 32 (memory.cpp:161-162), so it would be cleared by
     * the very first set_address() of the block ANYWAY -- the explicit
     * `handle->pins >= 32` branch in eprom_write_execute
     * (src/proms/eprom.cpp:217-219) makes that deliberate and OBSERVABLE
     * rather than incidental. ... Consolidating the
     * mask sets and choosing the final DIP32 route (P1 vs drop resistor)
     * is Phase 142 / VPP-01 and VPP-03 -- this case does not pre-empt that
     * choice, it only makes the existing clear observable. */
    int v0 = control_write_value(0);
    TEST_ASSERT_TRUE_MESSAGE(v0 >= 0 && (v0 & CTRL_VPP_VPE_DROP_ENABLE_REV2) != 0,
        "control write 0 (the top-of-block assert) must have the drop bit SET -- the 0x08 row's ELSE branch asserts regulator|drop together");

    int v1 = control_write_value(1);
    TEST_ASSERT_TRUE_MESSAGE(v1 >= 0 && (v1 & CTRL_VPP_VPE_DROP_ENABLE_REV2) == 0,
        "control write 1 (the explicit pins>=32 clear) must have the drop bit CLEAR");
    int clear_strobe_idx = control_write_strobe_index(1);
    char ordmsg[112];
    snprintf(ordmsg, sizeof(ordmsg), "the clearing write (stream index %d) must precede the first genuine data pulse (stream index %d)", clear_strobe_idx, first_pulse_idx);
    TEST_ASSERT_TRUE_MESSAGE(clear_strobe_idx < first_pulse_idx, ordmsg);

    /* From that clearing write onward ... the drop bit
     * never reappears: it is excluded from the preserve mask forever
     * after, on pins>=32. */
    for (int i = 1; i < n; i++) {
        int v = control_write_value(i);
        char msg[96];
        snprintf(msg, sizeof(msg), "control write %d (0x%02X) must not carry CTRL_VPP_VPE_DROP_ENABLE_REV2 -- pins>=32 excludes it from the preserve mask", i, v);
        TEST_ASSERT_TRUE_MESSAGE(v >= 0 && (v & CTRL_VPP_VPE_DROP_ENABLE_REV2) == 0, msg);
    }
}
```

**Inverted parts:** `v1`'s `== 0` at `:1614-1615`, the whole `i = 1..n` walk at `:1626-1631`, and the
`clear_strobe_idx` ordering assertion at `:1616-1619` (which has no successor - there is no clearing
write to order once `:217-219` is gone). `v0`'s "drop bit SET" assertion at `:1609-1611` **survives
unchanged**. The rewritten case becomes VPP-01's positive proof; rename it accordingly and update
`main()`'s `RUN_TEST` at `:1719`.

**New stale-citation flag:** this case's own comment cites `memory.cpp:161-162` for the guard; the
guard is at `:172` and the mask OR at `:188`. Do not carry that number forward.

### K-4. The paired control that must stay green - `test_loop08_the_28_pin_row_keeps_its_drop_bit`, `:1634-1663`

Runs on the DEFAULT `REVISION_0` deliberately (its comment `:1635-1645` explains why physical `0x01`
can only mean the drop bit for a 4-byte block at base 0), and asserts
`CTRL_VPP_VPE_DROP_ENABLE_REV1` present in **every** control value. Unaffected by D-01/D-02 (it is
`pins == 28`), and it is the non-vacuity partner for the rewritten K-3. Leave it alone.

---

## Shared Patterns

### S-1. Comment-as-hand-off (applies to every firmware file this phase edits)

Every construct Phase 141 left for this phase carries an explicit sentence naming Phase 142 and the
requirement. Five in-source hand-offs must be **consumed and rewritten**, not left dangling:

| Location | Sentence to retire |
|---|---|
| `eprom.cpp:186-188` | "Replacing this tier-1 predicate with the table's vpp_path column is Phase 142 / VPP-01" |
| `eprom.cpp:213-216` | "Choosing the final DIP32 route ... is Phase 142 / VPP-01 and VPP-03 -- this branch deliberately does not pre-empt that choice" |
| `eprom.cpp:169-171` | "generalising the disable to every exit in the file is Phase 142 / VPP-02's job" |
| `eprom.cpp:234` | "`(void)vpp_path;` // hoisted for completeness; Phase 142 / VPP-01 is its consumer" |
| `memory.cpp:187-190` | "choosing the final DIP32 route and consolidating the mask sets is Phase 142's (VPP-01 / VPP-03) -- this comment does not pre-empt that choice" |
| `eprom_params.h:43-45` | "Phase 142 owns the mask sets" |
| `test_loop_eprom_v131.cpp:1290-1292`, `:1595-1608` | "is Phase 142 / VPP-02's job" / "does not pre-empt that choice" |

Each replacement should name what was decided and its authority (`D-01`, `C-1`, etc.), matching the
existing style. **Do not delete a hand-off sentence without replacing it.**

### S-2. Non-vacuity pairing (applies to every new native assertion)

Every positive assertion in `test_loop_eprom_v131.cpp` is paired with a control that would fail if the
mechanism were absent: `:1277-1283` (`saw_earlier_set`), `:1286-1309` (successful block leaves it set),
`:1477-1508` (a different command's stream shows the bit ABSENT under the identical filter),
`:1634-1663` (the 28-pin partner), and `strobe_overflowed() == 0` as a soundness precondition on every
strobe-walking case. Copy this discipline; a lone positive assertion is not the house standard.

### S-3. Fail-closed / fail-toward-today's-behaviour

| Precedent | Direction |
|---|---|
| `rurp_hw_rev_utils.h:33-37` `default: break;` leaving `ctrl_reg = 0` | unknown revision -> no VPP, no VPE |
| `eprom_params.h:71-78` `eprom_params_for` returns NULL, "never returns a default row" | unknown protocol -> zero hardware side effects |
| `eprom.cpp:222-226` re-checks `row == NULL` even though `configure_eprom:86-90` already refused | defend locally anyway |
| `test_write_path_source_contract_v131.py:519-546` a missing scan target must FAIL | never a silent skip |

The `memory.cpp` gate (§F-3) and the resolver's NULL path (§G-7) both inherit this.

### S-4. Planted-RED discipline

Two mechanisms in-tree, both already used by the analogs:
- **Native suites:** temporarily edit the production source, run, capture, revert (the `86128af`
  message's "Planted violation A / B" shape, with the observed output quoted).
- **pytest gates:** point the import-time env seam at a scratch copy in a **child process**, then prove
  the seam is unset (`env | grep -c FIRESTARTER_..._SCAN` reports 0). Seams available:
  `FIRESTARTER_WRITE_PATH_SCAN_SOURCE`, `FIRESTARTER_BRANCH_SCAN_SOURCE`,
  `FIRESTARTER_BRANCH_SCAN_PARAMS_SOURCE`. A new gate should add its own on the same shape
  (`test_write_path_source_contract_v131.py:150-152`).

### S-5. `commits_land_in` / repo hygiene

- L-1 stands: `tests/test_flash_path_record_sync.py` asserts whole-repo `git status --porcelain == ""`.
  Commit before running the full pytest suite.
- `git status --porcelain` in `firestarter/` was **empty** at the start of this pass; the pinned blob
  SHAs still match. Arrival state is the one RESEARCH measured.

---

## No Analog Found / Unsuitable Analogs

| Item | Status | Substitute |
|---|---|---|
| Composite (bitwise-OR) `#define` in `include/` | **NO PRECEDENT** - `grep` returns 0 across the whole include tree | Use the alias form's placement conventions (`rurp_pinout.h:76`/`:116`/`:128`) and the 0-B `#define` rule at `:63-64`; the construct itself is new. Values verified correct in both variant arms: legacy `0x87` / wide `0x186` for `REGULATOR|DROP|A9|VPE`. |
| `test_flash_intel_vpp` as "a working template" for D-15(b) | **UNSUITABLE** - in no `test_filter`; forced to run it SIGABRTs after case 1, and the SAF-04 case is `RUN_TEST` #6 (`test_flash_intel_vpp.cpp:199`), so `:184-189` has never been observed to pass | Copy **only** `host_stubs.cpp:30` + `:37-39` (the seam). Take the assertions from `test_loop_eprom_v131.cpp:1269-1283` (§B-9) and the `setUp` from `:111-141` (§B-3). |
| `test_flash_intel_vpp.cpp:182` interception | **UNSUITABLE for the EPROM family** - re-assigning `h.firestarter_set_control_register` after `configure_memory` removes `eprom_internal_set_control_register`'s VPE->P1 remap (`eprom.cpp:441-447`, installed at `configure_eprom:65`) | Observe at the `rurp_*` layer via `control_write_value()` (§B-7). Fallback: override the non-`static` global `ep_set_control_register` (`eprom.cpp:36`) **after** `configure_memory`. |
| `HOST_STUBS_RECORD_BUS` for any drop-bit claim | **STRUCTURALLY INCAPABLE** - `host_stubs_common.inc:228` stores `(uint8_t)data`, truncating `0x100`; `rurp_read_from_register` returns 0 (`:239-242`) | `HOST_STUBS_REAL_REGISTER_UTILS` only. The truncation is documented in-tree at `test_val_eprom.cpp:92-96`. |
| `HOST_STUBS_CUSTOM_HW_REVISION` (`test_val_eprom/host_stubs.cpp`) | **DEAD** under `HOST_STUBS_REAL_REGISTER_UTILS` - its guard sits inside `!defined(HOST_STUBS_CUSTOM_HW_REVISION_BLOCK)` (`host_stubs_common.inc:289-296`) which the strobe-recorder arm defines at `:105` | Per-case `rurp_get_config()->hardware_revision = REVISION_2_2;` + unconditional `tearDown` reset (§B-4, §B-8). |
| A behavioural oracle for `command_done()` | **IMPOSSIBLE in a native env** - `firestarter.cpp` is outside every native `build_src_filter` (`+<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>`), and `host_stubs_common.inc:323-335` stubs `op_reset_timeout` precisely because that TU is absent | Source-contract pytest, §D. Label it a source-contract claim. |
| A standalone golden regenerator script | **DOES NOT EXIST** - the extractor is `_extract_predicates` inside `tests/test_protocol_branch_inventory.py` | Import the module's own extractor and dump live output (RESEARCH §D-18 step 3), then diff. |
| A commit pairing `CLAUDE.md` with `src/proms/` | **DOES NOT EXIST** in the last 10 `CLAUDE.md` commits | The house pattern is a `docs(NNN-NN):` docs-only commit in the same plan - §J-1. |

---

## Metadata

**Analog search scope:** `firestarter/{src,include,test,tests,scripts,doc}`, `firestarter/platformio.ini`,
`firestarter/CLAUDE.md`, plus `git log` / `git show` on `tests/golden/protocol_branch_inventory.json`,
`tests/test_protocol_branch_inventory.py` and `CLAUDE.md`.

**Files read in full:** `test_loop_eprom_v131/host_stubs.cpp`, `_shared/host_stubs_common.inc`,
`include/rurp_pinout.h`, `include/rurp_hw_rev_utils.h`, `include/eprom.h`,
`test_flash_intel_vpp/host_stubs.cpp`.
**Files read in targeted ranges:** `test_loop_eprom_v131.cpp` (`:1-180`, `:180-309`, `:400-519`,
`:1120-1319`, `:1391-1723`), `tests/test_write_path_source_contract_v131.py` (`:1-180`, `:183-312`,
`:375-414`, `:519-593`), `src/proms/eprom.cpp` (`:30-45`, `:100-239`, `:290-454`),
`src/proms/memory.cpp` (`:86-96`, `:140-239`), `src/proms/flash_intel.cpp` (`:18-67`),
`src/firestarter.cpp` (`:150-184`), `platformio.ini` (`:355-414`),
`tests/test_protocol_branch_inventory.py` (`:85-124`, `:396-455`),
`test_flash_intel_vpp/test_flash_intel_vpp.cpp` (`:50-201`), `include/eprom_params.h` (`:38-84`).

**Read-only commands run:** `git rev-parse HEAD`, `git status --porcelain`, `git log`, `git show`
(3 commits), `wc -l`, `grep`, `sed -n`, `awk`, and one `python3 -c` that only `json.load`s the golden.
No source file was modified. No build or test was run.

**Line numbers valid until:** the next commit touching `src/proms/eprom.cpp`, `src/proms/memory.cpp`,
`include/rurp_pinout.h`, `platformio.ini`, `test/native/avr/**`, `tests/**` or `CLAUDE.md`.
Anchored to `firestarter` @ `4921388`.

**Pattern extraction date:** 2026-08-11
