# Phase 117: FIX — remap-aware `0x0D` emitter + honest completion signal - Pattern Map

**Mapped:** 2026-07-28
**Files analyzed:** 6 touch targets (1 production, 1 config, 2 test-file edits, 2 discretionary test homes)
**Analogs found:** 6 / 6 (all exact or role-match — this phase adds no new machinery)
**Research:** none (ROADMAP marks Phase 117 "Research flag: no — standard pattern"); file list taken verbatim from `117-CONTEXT.md` `<code_context>` → `### Integration Points`

> **Read-only contract of this document.** Nothing here proposes a design. D-01..D-13 in
> `117-CONTEXT.md` are locked; every excerpt below exists to show the planner *what shape already
> exists in the tree*. **Validation ceiling:** every claim's subject is code. No AT28C part is on
> the bench; nothing below is evidence about silicon state.

---

## File Classification

| Touch target | Role | Data flow | Closest analog | Match quality |
|---|---|---|---|---|
| `firestarter/src/proms/eeprom_28c.cpp` **(the only production edit)** | protocol handler (AVR C++) | bus-strobe emit + poll (request-response per byte) | `firestarter/src/proms/flash_5v_page.cpp` — **READ-ONLY ANALOG (FIX-04 frozen)** | exact (same role, same page-write+poll flow) |
| `firestarter/platformio.ini` `[env:native]` | build config | allowlist / declarative | itself, :98-133 (14 existing `test_filter` + `-I` pairs) | exact |
| `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` | native Unity test (ordered-stream oracle) | trace assertion | `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp` | exact (sibling suite, same recorder, same helper names) |
| `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` | evidence doc | append-only record | itself (§ headings at :12/:41/:194/:219/:229/:278) | exact |
| **FIX-05 guard home (discretion)** → `test_sdp_harness/test_sdp_harness.cpp` | native Unity test (constant/table guard) | pure-data assertion | in-file: `test_negativeA_…` :206-240 and `test_lock05_…` :261-275 | exact |
| **FIX-06 test home (discretion)** → `test_val_eeprom28c/test_val_eeprom28c.cpp` | native Unity test (Tier-1 validation) | side-effect recording | in-file 3 cases :87-114 (**`HOST_STUBS_RECORD_BUS` recorder, NOT the strobe recorder** — see §Conventions) | role-match only (different recorder layer) |

### READ-ONLY ANALOGS — FIX-04 frozen, never edit targets

| File | Why the planner reads it |
|---|---|
| `firestarter/src/proms/flash_5v_page.cpp` | **READ-ONLY ANALOG (FIX-04 frozen)** — the single most important FIX-06 shape template |
| `firestarter/src/proms/flash_utils.cpp` | **READ-ONLY ANALOG (FIX-04 frozen)** — the shipped emitter + `fu_flash_data_poll` counter-example |
| `firestarter/include/flash_utils.h` | **READ-ONLY ANALOG (FIX-04 frozen)** — `FLASH_ERASE` / `FLASH_DISABLE_WRITE_PROTECTION` literals FIX-05 guards |
| `firestarter/src/proms/flash_nor_unlock.cpp` | **READ-ONLY ANALOG (FIX-04 frozen)** |
| `firestarter/src/proms/memory.cpp` | source-of-truth for `memory_set_data` / `memory_get_data` / `mem_util_remap_address_bus` |
| `firestarter/include/rurp_register_utils.h` | source-of-truth for cache-compare elision + `rurp_set_data_output()` |
| `firestarter/test/native/avr/_shared/sdp_expected.h` | comparator + golden arrays (D-12 scoped so **no regeneration**) |
| `firestarter/test/native/avr/_shared/host_stubs_common.inc` | the recorder + opt-in flag contract |
| `firestarter/test/native/avr/_shared/sdp_bus_config.h` | generated `DO NOT EDIT` `bus_config_t` literals |

---

## Pattern Assignments

### 1. `eeprom_28c.cpp` — FIX-01: how a handler emits a multi-byte command sequence

**Two call shapes exist side by side in the tree. FIX-01 replaces the first with the second.**

**Shape A — the SHIPPED path (what is there now).** `eeprom_28c.cpp:104`, expanding through
`flash_utils.h:15-16` into `flash_utils.cpp:21-28`:

```cpp
// flash_utils.h:15-16 — the macro; note it captures `handle` from the caller's scope
#define flash_execute_command(command) \
    flash_util_byte_flipping(handle, command, sizeof(command) / sizeof(command[0]));
```

```cpp
// flash_utils.cpp:21-28 — READ-ONLY ANALOG (FIX-04 frozen). The loop body FIX-01's
// replacement is shaped against.
void flash_util_byte_flipping(firestarter_handle_t* handle, const byte_flip_t* byte_flips, size_t size) {
    handle->firestarter_set_control_register(handle, CTRL_READ_WRITE, 0);
    for (size_t i = 0; i < size; i++) {
        fu_flash_flip_data(handle, byte_flips[i].address, byte_flips[i].byte);
    }
    handle->firestarter_set_control_register(handle, CTRL_READ_WRITE, 0);
}
```

```cpp
// flash_utils.cpp:53-67 — READ-ONLY ANALOG (FIX-04 frozen). :53 is D-12's parity argument
// (the shipped path DID set data direction). :61-66 is the bypass: LSB/MSB only, never
// CONTROL_REGISTER, never handle->bus_config.
void fu_flash_flip_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_set_data_output();
    fu_flash_fast_address(handle, address);
    rurp_write_data_buffer(data);
    rurp_chip_input();
    rurp_chip_enable();
    rurp_chip_disable();
}

void fu_flash_fast_address(firestarter_handle_t* handle, uint32_t address) {
    uint8_t lsb = address & 0xFF;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    uint8_t msb = ((address >> 8) & 0xFF);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, msb);
}
```

**Shape B — the `handle->firestarter_set_data` call site that already exists in this very file.**
`eeprom_28c.cpp:123`, inside `eeprom28c_write_execute`:

```cpp
handle->firestarter_set_data(handle, address, data);
```

**Shape B, driven as a table loop — the exact per-element shape FIX-01 needs**, already written
twice in the test tree as `drive_reference_emitter`
(`test_sdp_harness.cpp:121-128`, byte-identical helper in `test_eeprom28c_sdp.cpp:155-162`):

```cpp
for (size_t i = 0; i < len; i++) {
    h->firestarter_set_data(h, table[i].address, table[i].byte);
}
```

**What `handle->firestarter_set_data` resolves to** — `memory.cpp:228-306`
(READ-ONLY ANALOG). Note: routes through `mem_util_remap_address_bus`, writes CONTROL via
`firestarter_set_address`, and **never calls `rurp_set_data_output()`** (D-12's finding):

```cpp
void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_chip_input();
    address = mem_util_remap_address_bus(handle, address, WRITE_FLAG);

    handle->firestarter_set_address(handle, address);
    rurp_write_data_buffer(data);
    delayMicroseconds(3);  // Needed for slower address changes ...
    rurp_chip_enable();
    delayMicroseconds(handle->pulse_delay);
    rurp_chip_disable();
}
```

**The remap `fu_flash_fast_address` skips** — `memory.cpp:331-354` (READ-ONLY ANALOG), abridged to
the two clauses that matter for the `0x5555`/`0x2AAA` loads:

```cpp
uint32_t mem_util_remap_address_bus(const firestarter_handle_t* handle, uint32_t address, uint8_t read_write) {
    bus_config_t config = handle->bus_config;
    uint32_t reorg_address = config.address_mask & address;
    ...
    if (config.rw_line != 0xFF) {
        reorg_address |= (uint32_t)read_write << config.rw_line;
    }
    ...
    reorg_address |= config.static_high_mask;
    return reorg_address;
}
```

**The local table FIX-01 drives (D-10 keeps it local)** — `eeprom_28c.cpp:25-33`:

```cpp
// AT28C SDP disable: 6-write sequence to magic addresses
const byte_flip_t EEPROM_SDP_DISABLE[] = {
    {0x5555, 0xAA}, {0x2AAA, 0x55}, {0x5555, 0x80},
    {0x5555, 0xAA}, {0x2AAA, 0x55}, {0x5555, 0x20},
};
```

**Existing `rurp_set_data_output()` call sites** (D-12's explicit call) — `flash_utils.cpp:54` and
`:40`, plus the incidental restoration inside `rurp_register_utils.h:77-81` (Uno/328PB-only
`MOST_SIGNIFICANT_BYTE` branch). Declared in `host_stubs_common.inc:176` as a no-op, so it is
**invisible to the strobe recorder** — consistent with D-12's "no `SDP_FIXED_*` regeneration".

---

### 2. `eeprom_28c.cpp` — the current defect, verbatim

**`eeprom28c_write_init`** — `eeprom_28c.cpp:97-117` (FIX-01 replaces :109, FIX-02 deletes :111-113):

```cpp
void eeprom28c_write_init(firestarter_handle_t* handle) {
    // Check chip identity via A9-12V (SAF-05) BEFORE SDP-disable (D-08: fail-fast
    // on identity leaves the chip write-protected on mismatch).
    if (handle->chip_id > 0) {
        eeprom28c_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    // Disable SDP (Software Data Protection) before writing.
    // The 6-write sequence must complete within the inter-byte timing window.
    // flash_util_byte_flipping uses fu_flash_flip_data which has no pulse_delay.
    flash_execute_command(EEPROM_SDP_DISABLE);
    // Wait for SDP disable internal write cycle to complete
    if (!eeprom28c_wait_for_write(handle, 0x5555, 0x20)) {
        return;
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}
```

**`eeprom28c_write_execute`** — `eeprom_28c.cpp:119-133` (FIX-06's subject; note the conflated
`eeprom28c_wait_for_write(address, data)` at :128 doing both completion and data-landed duty):

```cpp
void eeprom28c_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, data);

        bool page_end = ((address + 1) % PAGE_SIZE) == 0;
        bool last_byte = (i == handle->data_size - 1);
        if (page_end || last_byte) {
            if (!eeprom28c_wait_for_write(handle, address, data)) {
                return;
            }
        }
    }
}
```

**`eeprom28c_wait_for_write`** — `eeprom_28c.cpp:135-155`. **:153 is the unconditional
`RESPONSE_CODE_ERROR` that destroys severity** (D-05's rejected "unconditional ERROR" arm; the
`response_code` write RED-BASELINE case 7 catches):

```cpp
static bool eeprom28c_wait_for_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected) {
    uint8_t observed = 0;
    for (uint16_t j = 0; j < 2000; j++) {
        delayMicroseconds(10);
        observed = handle->firestarter_get_data(handle, address);
        if (observed == expected) {
            return true;
        }
    }
    {
        uint8_t _b[5];
        _b[0] = (uint8_t)((address >> 16) & 0xFF);
        _b[1] = (uint8_t)((address >> 8) & 0xFF);
        _b[2] = (uint8_t)(address & 0xFF);
        _b[3] = (uint8_t)expected;
        _b[4] = (uint8_t)observed;
        LOG_ERROR_ID_BYTES(MSG_ERR_EEPROM_TIMEOUT, _b, 5);
    }
    handle->response_code = RESPONSE_CODE_ERROR;
    return false;
}
```

**`PAGE_SIZE 64`** — `eeprom_28c.cpp:19` (D-13's comment target; today it carries no comment):

```cpp
#define PAGE_SIZE 64
```

The in-tree precedent for a comment that records deliberate page-size reasoning at the definition
site is `flash_5v_page.cpp:19-31` — **READ-ONLY ANALOG (FIX-04 frozen)**, whose 12-line block
names worked examples and the original bug. D-13 rejects the *helper*, not the *comment shape*.

---

### 3. `eeprom_28c.cpp` — FIX-06: the in-tree page-write + poll template

**`flash_5v_page.cpp:79-106` — READ-ONLY ANALOG (FIX-04 frozen). CONTEXT.md names this the single
most important FIX-06 analog. Copy the shape; do not refactor into shared code.**

```cpp
void flash_5v_page_write_execute(firestarter_handle_t* handle) {
    uint32_t page_size = flash_5v_page_page_size(handle->mem_size);
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t expected = handle->data_buffer[i];

        /* SDP 3-byte unlock at the start of each page load (AMD/JEDEC SDP). ...
         * Call per-page-START (not per-byte) — calling per-byte would abort
         * the current page load and restart it after each byte. */
        bool is_page_start = (address % page_size) == 0;
        bool is_first_byte = (i == 0);
        if (is_page_start || is_first_byte) {
            flash_execute_command(FLASH_ENABLE_WRITE);
        }

        handle->firestarter_set_data(handle, address, expected);

        bool reached_page_end = ((address + 1) % page_size) == 0;
        bool is_last_byte = i == handle->data_size - 1;
        if (reached_page_end || is_last_byte) {
            if (!flash_5v_page_wait_for_page_write(handle, address, expected)) {
                return;
            }
        }
    }
}
```

Its poll — `flash_5v_page.cpp:108-130` (READ-ONLY ANALOG). **Note this is the *same*
equality-compare shape as `eeprom28c_wait_for_write`**, i.e. the analog supplies the loop/timeout/
error-payload skeleton and the per-page gating, **not** the DQ7-complement semantics D-07 requires:

```cpp
static bool flash_5v_page_wait_for_page_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected) {
    // poll the last byte written until it's correct.
    uint8_t observed = 0;
    for (uint16_t j = 0; j < 1024; j++) {
        delayMicroseconds(10);
        observed = handle->firestarter_get_data(handle, address);
        if (observed == expected) {
            return true;
        }
    }
    {
        uint8_t _b[5];
        _b[0] = (uint8_t)expected;
        _b[1] = (uint8_t)((address >> 16) & 0xFF);
        ...
        LOG_ERROR_ID_BYTES(MSG_ERR_FL4_VERIFY_TIMEOUT, _b, 5);
        handle->response_code = RESPONSE_CODE_ERROR;
    }
    return false;
}
```

**The only DQ7-mask poll that exists in the tree** — `flash_utils.cpp:30-51` (READ-ONLY ANALOG,
FIX-04 frozen). This is the DQ7-bit-compare *idiom* (`(x & 0x80) == (expected & 0x80)`, read twice
to confirm) the planner may reference for FIX-06's completion arm:

```cpp
void flash_util_verify_operation(firestarter_handle_t* handle, uint8_t expected_data) {
    handle->firestarter_set_control_register(handle, CTRL_READ_WRITE, 1);
    unsigned long timeout = millis() + 150;
    while (millis() < timeout) {
        // Data Polling: Read from the address and check DQ7.
        if ((fu_flash_data_poll() & 0x80) == (expected_data & 0x80)) {
            if ((fu_flash_data_poll() & 0x80) == (expected_data & 0x80)) {
                rurp_set_data_output();
                rurp_chip_disable();
                rurp_chip_input();
                return;
            }
        }
    }
    LOG_ERROR_ID(MSG_ERR_OP_TIMEOUT);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```

**Why D-06 forbids this poll's *transport*** — `flash_utils.cpp:69-77` (READ-ONLY ANALOG). It emits
four `rurp_*` strobes per read, **all of them recorded** by
`host_stubs_common.inc:125-130` (`rurp_set_control_pin` → `STROBE_KIND_PIN`). Using it in the
completion path would inject entries into the stream cases 1-5 compare for full equality:

```cpp
uint8_t fu_flash_data_poll() {
    rurp_set_data_input();
    rurp_chip_enable();      // recorded: PIN CHIP_ENABLE 0
    rurp_chip_output();      // recorded: PIN OUTPUT_ENABLE 1
    uint8_t data = rurp_read_data_buffer();
    rurp_chip_disable();     // recorded: PIN CHIP_ENABLE 1
    rurp_chip_input();       // recorded: PIN OUTPUT_ENABLE 0
    return data;
}
```

By contrast a read through `handle->firestarter_get_data` in a test is *mocked* — see
`mock_get_data_keyed` (`test_eeprom28c_sdp.cpp:134-148`), which contributes **zero** strobes across
all 2000 poll iterations. That asymmetry is the whole mechanism behind D-06's hard constraint.

**Contrast reference for D-05 (poll must never write `response_code`)** — the closest in-tree
severity-preserving fork is `flash_utils.cpp:98-104` / `eeprom_28c.cpp:86-92`
(`is_flag_set(FLAG_FORCE)` → WARNING else ERROR). D-05 rejects even that arm for the poll; the
pattern is cited here only so the planner can point at what "writing response_code" looks like and
assert its **absence**.

---

### 4. Native test asserting on an ordered bus-strobe stream

**Analog:** `test_sdp_harness/test_sdp_harness.cpp` (always-green sibling of the parked suite).

**Drive helper (reference emitter)** — `:117-128`:

```cpp
/* The FIX-01 reference emitter: h->firestarter_set_data is memory_set_data
 * (assigned by configure_memory), which routes through
 * mem_util_remap_address_bus -- the remap-aware target stream, with zero
 * hand derivation. */
static void drive_reference_emitter(firestarter_handle_t* h, const byte_flip_t* table, size_t len, rurp_register_t ctrl_seed) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, ctrl_seed);
    clear_strobes();
    for (size_t i = 0; i < len; i++) {
        h->firestarter_set_data(h, table[i].address, table[i].byte);
    }
}
```

**Load-bearing ordering rule** — `:103-109` (verbatim comment, applies to every new case):
`configure_memory` (which itself writes address 0) → `reset_register_cache` → `clear_strobes` →
drive. Cache reset and strobe clear **must both** come after `configure_memory`.

**A full reference-emitter guard case** — `:282-287`:

```cpp
void test_fixed_guard_at28c256(void) {
    firestarter_handle_t h = make_sdp_handle(SDP_BUS_CONFIGS[0]); /* AT28C256 */
    drive_reference_emitter(&h, FLASH_DISABLE_WRITE_PROTECTION, 6, 0x00);
    sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN,
        "reference-emitter guard: AT28C256 / DIP28_28C256");
}
```

**Handle factory** — `test_sdp_harness.cpp:91-101` (identical in the parked suite at :106-116):

```cpp
static firestarter_handle_t make_sdp_handle(const sdp_bus_config_row_t& row) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = 0;
    h.mem_size = row.mem_size;
    h.bus_config = row.bus_config;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK;
    return h;
}
```

**Mandatory `setUp()` body** — `test_sdp_harness.cpp:59-83` / `test_eeprom28c_sdp.cpp:76-98`.
The three ArduinoFake mocks are **load-bearing, not unused** (ArduinoFake SIGABRTs on any unmocked
virtual; `rurp_register_utils.h:58,86` and the polls all call `delayMicroseconds`/`delay`):

```cpp
When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();
When(Method(ArduinoFake(), delay)).AlwaysReturn();
When(Method(ArduinoFake(), millis)).AlwaysReturn(0);

clear_strobes();
reset_register_cache(0x00, 0x00, 0x00);
```

**Comparator + snapshot helper signatures** — `_shared/sdp_expected.h` (READ-ONLY ANALOG):

```cpp
// :38-43 — recorder accessors (compiled because host_stubs.cpp defines HOST_STUBS_REAL_REGISTER_UTILS)
extern "C" void    clear_strobes();
extern "C" int     strobe_count();
extern "C" int     strobe_overflowed();
extern "C" uint8_t strobe_kind(int i);
extern "C" uint8_t strobe_pin(int i);
extern "C" uint8_t strobe_value(int i);

// :48-52 — the element type; :57-58 STROBE_KIND_DATA 1 / STROBE_KIND_PIN 2
typedef struct { uint8_t kind; uint8_t pin; uint8_t value; } sdp_strobe_t;

// :64  — index of first divergence, or -1; length mismatch diverges at the shorter length
static int  sdp_first_divergence(const sdp_strobe_t* expected, int expected_len);
// :86  — asserts !overflowed, then count, then element-wise; failure message names the index
static void sdp_assert_stream_equals(const sdp_strobe_t* expected, int expected_len, const char* ctx);
// :113 — copy the LIVE stream out before a second drive wipes it (returns entries copied)
static int  sdp_snapshot(sdp_strobe_t* out, int max_len);
```

**Cache-reset seam declaration** (both suites, `:56` / `:46`):

```cpp
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);
```

**The two-drives-in-one-case pattern (snapshot first, then re-drive)** — `test_sdp_harness.cpp:229-239`;
also used by the parked suite's cases 4/5 at `:297-312` and `:336-350`.

---

### 5. D-01/D-02 edit points in the parked suite

**D-01 — the `set_data` un-mock.** Three sites assign the no-op mock:

```cpp
// test_eeprom28c_sdp.cpp:133 — the no-op itself
static void mock_set_data_keyed(firestarter_handle_t*, uint32_t, uint8_t) {}

// :169-176 drive_write_init
static void drive_write_init(firestarter_handle_t* h, rurp_register_t ctrl_seed) {
    configure_memory(h);
    h->firestarter_get_data = mock_get_data_keyed;
    h->firestarter_set_data = mock_set_data_keyed;   // <-- D-01 drops this line
    reset_register_cache(0x00, 0x00, ctrl_seed);
    clear_strobes();
    h->firestarter_operation_init(h);
}

// :191 inside drive_write_init_after_real_read — same single line
// :379 (case 6) and :407 (case 7) — inline, alongside their own get_data assignment
```

The `get_data` mock that **stays** — `:134-148`; its `addr == 0x5555 → 0xFF` arm at :143-146 is what
collapses the 2000-iteration poll to zero strobes.

**D-02 — the five `RESPONSE_CODE_ERROR` assertions to flip.** Exact sites:

| Case | Line | Assertion today |
|---|---|---|
| 1 | `:214` | `TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, …)` |
| 2 | `:228` | same |
| 3 | `:241` | same |
| 4 | `:294` | same |
| 5 | `:333` | same |

The "must not be ERROR" form already exists in the file at `:383` (case 6) — copy that:

```cpp
TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "...");
```

**D-02's new severity-preservation case** — the shape to copy is case 7 at `:400-414`, whose comment
at `:396-399` already names the `reference_golden_trace_misses_severity_fork.md` lesson:

```cpp
void test_case7_mismatching_chip_id_with_force_warns(void) {
    s_mfr_addr_keyed = 32768 - 64;
    s_mfr_hi_keyed = 0xDE;
    s_mfr_lo_keyed = 0xAD;
    firestarter_handle_t h = make_identity_handle(0x1F08, FLAG_FORCE);
    configure_memory(&h);
    h.firestarter_get_data = mock_get_data_keyed;
    h.firestarter_set_data = mock_set_data_keyed;
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_WARNING, h.response_code, "...");
}
```

Every case must also be registered in `main()` — `:420-433`, one `RUN_TEST(...)` line per case.

**Case-rename discretion (CONTEXT.md).** The five names are at
`:211, :225, :238, :291, :318`; the suite header comment at `:7-35` and `RED-BASELINE.md`'s
`# What Phase 117 must do` (:12) cross-reference them.

---

### 6. FIX-05 guard — analog: the planted-mutation negative already in `test_sdp_harness`

**`test_sdp_harness.cpp:199-240` is the closest analog and the natural home** (D-11's guard is the
constant-level formalisation of what this case already proves at the stream level). The test-local
table + its provenance comment:

```cpp
/* TRACE-03a: the six-write unlock table with the terminal byte mutated from
 * the SDP-disable value (0x20) to the chip-erase value (0x10) -- a one-nibble
 * slip that turns SDP-disable into chip erase (see FLASH_ERASE vs
 * FLASH_DISABLE_WRITE_PROTECTION in flash_utils.h -- they differ ONLY in
 * this terminal byte). Test-local copy: EEPROM_SDP_DISABLE has internal
 * linkage (116-RESEARCH.md §F6) ... */
static const byte_flip_t TEST_UNLOCK_MUTATED_TERMINAL[] = {
    {0x5555, 0xAA}, {0x2AAA, 0x55}, {0x5555, 0x80},
    {0x5555, 0xAA}, {0x2AAA, 0x55},
    {0x5555, 0x10}, /* mutated: 0x20 (SDP-disable) -> 0x10 (chip-erase) */
};
```

**The table-identity assertion shape** (D-11's "byte-identical to
`FLASH_DISABLE_WRITE_PROTECTION`" clause) — `:261-275`, `test_lock05_enable_write_and_write_protection_identical`,
which proves identity between two tables via snapshot + `sdp_first_divergence(…) == -1`.

**The literals FIX-05 guards** — `flash_utils.h:34-41` and `:53-60`
(**READ-ONLY ANALOG (FIX-04 frozen)**). They differ *only* in the terminal byte:

```cpp
const byte_flip_t FLASH_ERASE[] = {
    {0x5555, 0xAA}, {0x2AAA, 0x55}, {0x5555, 0x80},
    {0x5555, 0xAA}, {0x2AAA, 0x55}, {0x5555, 0x10},   // terminal 0x10
};
const byte_flip_t FLASH_DISABLE_WRITE_PROTECTION[] = {
    {0x5555, 0xAA}, {0x2AAA, 0x55}, {0x5555, 0x80},
    {0x5555, 0xAA}, {0x2AAA, 0x55}, {0x5555, 0x20},   // terminal 0x20
};
```

`FLASH_ENABLE_WRITE_PROTECTION[]` (Phase 119 LOCK-05 preserves it) is at `flash_utils.h:48-52`.

**Linkage caveat carried by `:204-205`:** `EEPROM_SDP_DISABLE` is declared `const` at file scope in
`eeprom_28c.cpp` with no header declaration — the harness's own comment records that it has
internal linkage from a test TU's perspective, which is why that suite transcribes a test-local copy
rather than referencing it.

---

### 7. FIX-06's planted-partial-write test — analogs for the old-vs-new side-by-side

**Prefer the C++ in-tree precedent over the Python one.** Two in-tree shapes compose into D-09:

1. **Planted-fault negative, C++** — `test_sdp_harness.cpp:215-240`
   (`test_negativeA_unlock_mutated_diverges_and_matches_erase`). Structure: drive the *planted*
   variant → assert it diverges at a named index → `sdp_snapshot` → drive the *real* table →
   assert element-wise identity. This is the "both halves execute in CI forever" property D-09 asks
   for, in C++, in this exact suite family.
2. **Address-keyed mock as the fault-planting seam** — `test_eeprom28c_sdp.cpp:129-148`
   (`mock_get_data_keyed`). Its per-address dispatch (with `s_reads_at_*` counters at `:70-74`,
   reset in `setUp()` at `:93-97`) is the mechanism for D-09's planted scenario ("mock accepts the
   page's last byte but leaves an earlier byte at its old value") — add an address arm, do not
   change the dispatch style. Its own comment forbids call-ordinal dispatch: *"dispatch on ADDRESS,
   not call order."*

**Python analog (v1.21 SAFE-03/DISP-01), for the *discipline* only — `firestarter_app` is read-only
this phase.** `firestarter_app/tests/test_check_no_community_support_status_write.py`. Its shape:
`test_checker_exits_zero_on_clean_source` (:66) **paired with**
`test_checker_exits_nonzero_on_planted_report_violation` (:89) **and** an isolation control
`test_env_override_report_points_at_clean_fixture_still_passes` (:162) whose docstring states it
exists to prove the non-zero exit came from the planted violation and *not* the injection seam. The
third test is the part most easily dropped — it is what makes the pair non-hollow. Siblings:
`test_check_no_log_in_sdp_window.py`, `test_check_devtest_orchestrator.py`,
`test_sdp_bus_config_drift.py`.

**If FIX-06's test lands in `test_val_eeprom28c`** — that suite uses a **different recorder**. Its
existing case shape (`:87-94`) and helper (`:73-84`):

```cpp
void test_eeprom28c_read_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "...");
    assert_no_vpp_in_recording("...");
}
```

Its `setUp()` (`:49-55`) mocks **only** the three Serial methods and calls `clear_bus_recording()` —
it does **not** mock `delay`/`delayMicroseconds`/`millis`. Any new write-path case there that
reaches a poll will need those three mocks added (the SIGABRT hazard documented at
`test_sdp_harness.cpp:64-70`). Its handle factory (`:59-67`) also sets **no `bus_config`**.

---

## Shared Patterns

### Conventions — adding/enabling a suite in `[env:native]`

**Source:** `firestarter/platformio.ini`. A suite needs **two** entries: a `test_filter` line and an
`-I` line. `test_eeprom28c_sdp` **already has the `-I` entry** (`:133`) and is absent from
`test_filter` **by design**.

The PARKED comment block (`:89-97`, D-03's commit-1 edits both it and the list):

```ini
; PARKED (D-01): native/avr/test_eeprom28c_sdp is authored RED ON PURPOSE
; (v1.22 Phase 116 Plan 06, TRACE-02/TRACE-04/TRACE-06). It has an -I entry
; below (so it compiles) but is deliberately NOT in this test_filter
; allowlist, so `pio test -e native` stays green throughout Phase 116 and
; GATE-03 keeps meaning something. TODO(v1.22 Phase 117): adding this
; suite's one line to test_filter IS the RED-to-GREEN proof that
; eeprom28c_write_init has been rebuilt on the remap-aware, CONTROL-writing
; emitter FIX-01 targets — do not add it before that fix lands, and do not
; use TEST_IGNORE_MESSAGE here (an IGNORED result does not demonstrate RED).
```

The allowlist (`:98-113`, 15 entries today, tab-indented, ends at `native/avr/test_sdp_harness`) and
the `-I` block (`:117-133`, ends at `-I test/native/avr/test_eeprom28c_sdp`). Also relevant:
`build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>` and
`test_build_src = yes` at `:150-151`; the pre-existing KNOWN-FLAKY note at `:72-85`.

Note the drift with `firestarter/CLAUDE.md:169-174`, which still claims *"The `[env:native]`
configuration in `platformio.ini` does not need changes for new suites."* The positive allowlist
(`:86-87`: *"test_ignore was being honored inconsistently"*) supersedes that sentence.

### Conventions — `host_stubs.cpp` opt-in flag contract

**Source:** `_shared/host_stubs_common.inc` (READ-ONLY ANALOG). Two independent **opt-IN** layers,
selected by `#ifdef HOST_STUBS_REAL_REGISTER_UTILS` / `#elif defined(HOST_STUBS_RECORD_BUS)` at
`:81` / `:131` — so `HOST_STUBS_REAL_REGISTER_UTILS` **wins** if both are defined.

| Flag | What it gives you | Which suites define it |
|---|---|---|
| `HOST_STUBS_REAL_REGISTER_UTILS` (`:55-130`) | ordered strobe recorder hooking `rurp_write_data_buffer` (`:125`) + `rurp_set_control_pin` (`:128`); accessors `clear_strobes`/`strobe_count`/`strobe_overflowed`/`strobe_kind`/`strobe_pin`/`strobe_value` (`:102-107`); cap `HOST_STUBS_MAX_STROBES 512` (`:87`) with overflow flag (`:116`) | `test_sdp_harness`, `test_eeprom28c_sdp` **only** |
| `HOST_STUBS_RECORD_BUS` (`:46-53`, impl `:131-152`) | `{reg, data}` recording of `rurp_write_to_register`; accessors `clear_bus_recording`/`bus_recording_count`/`recorded_reg`/`recorded_data`; cap 256 | `test_val_*` suites incl. `test_val_eeprom28c` |
| neither | no-op `rurp_write_to_register` (`:154`) | **MUST stay undefined** for `test_dispatch`, `test_cobs_*`, `test_read_timing`, `test_messages`, `test_data_input`, `test_not_implemented`, `test_frame_vectors` (`:49-53`, `:80`: *"flag off must stay byte-exact for all 14 pre-existing suites"*) |

**Ordering pitfall (both flags):** the `#define` must precede the `#include` of
`host_stubs_common.inc`. See `test_eeprom28c_sdp/host_stubs.cpp:38-40`:

```cpp
/* Activate the ordered strobe recorder (opt-IN). MUST precede the include. */
#define HOST_STUBS_REAL_REGISTER_UTILS

#include "../_shared/host_stubs_common.inc"

/* D-05: production's real cache-compare + latch-strobe sequencing ... */
#include "rurp_register_utils.h"
```

`HOST_STUBS_REAL_REGISTER_UTILS` also implies `HOST_STUBS_CUSTOM_CONTROL_PIN`,
`HOST_STUBS_CUSTOM_DATA_BUFFER`, `HOST_STUBS_CUSTOM_HW_REVISION_BLOCK` (`:88-90`) and suppresses six
symbols the real `rurp_register_utils.h`/`rurp_hw_rev_utils.h` pair supplies (`:69-75`).

**Global-state pitfall:** `lsb_address`, `msb_address`, `control_register` are non-`static` globals
initialised to `0xff` (`rurp_register_utils.h:12-14`) and **persist across Unity cases in one
binary**; `0xff` CONTROL ORs in `CTRL_VPP_REGULATOR_ENABLE`. Every case must call
`reset_register_cache(...)`. Documented at `test_eeprom28c_sdp/host_stubs.cpp:45-59`.

**`rurp_set_data_output()` / `rurp_set_data_input()` are unconditional no-ops** at
`host_stubs_common.inc:176-177` — outside both `#ifdef` blocks. D-12's explicit call is therefore
recorder-invisible, which is the mechanical basis of "no `SDP_FIXED_*` regeneration is needed".

### Assertion discipline (applies to every new case)

**Source:** `_shared/sdp_expected.h:63` and `:83-85` — *"Never counts anything — D-06's anti-pattern
list forbids it — every comparison is positional"*; ordered full-stream equality, never a
sub-sequence scan or a count. Register-write elision (`rurp_register_utils.h:26-53`) is invisible to
a call-counting test. Overflow must be asserted 0 before any content assertion
(`sdp_assert_stream_equals` does it at `:87`; cases also assert it explicitly, e.g.
`test_eeprom28c_sdp.cpp:299`).

### `RED-BASELINE.md` append target (D-03)

**Source:** `test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`. Existing section headings, for the
planner to place the post-suite-edit capture against:

```
:12  # What Phase 117 must do
:27  # Validation ceiling (read this before citing anything below)
:41  # The seven cases and their observed RED reasons
:58  ## Cases 1-3 — ordered capture per DIP28/DIP24 pinout (TRACE-02)
:84  ## Cases 4-5 — DIP32_28C512_EEPROM, deliberate stale-upper-address state
:155 ## Cases 6-7 — migrated identity-gate assertions, RED half
:194 ## Response code observed after `eeprom28c_write_init`, per pinout
:219 ## First-divergence index per trace case
:229 ## Design decisions this suite embodies
:278 ## Declined widening, recorded as an open hook (D-07 scoping)
```

The file's established evidence style: verbatim captured output, a per-case "observed RED reason",
and per-pinout tables (e.g. the CORRECTION 4 66-of-84 table). §"Declined widening" (`:278`) is
D-12's named Phase-118 hook and should not be re-scoped by this phase.

---

## No Analog Found

| Concern | Role | Data flow | Why no analog |
|---|---|---|---|
| DQ7-**complement** completion poll (D-07) | handler-local poll | request-response | The tree has DQ7-**mask-equality** polling (`flash_utils.cpp:38-40`) and last-byte-equality polling (`flash_5v_page.cpp:113-115`, `eeprom_28c.cpp:134`), but **no complement-compare** anywhere. `flash_5v_page.cpp` supplies the skeleton; the complement semantics have no in-tree precedent. |
| A named `t_WC`-style timing constant (D-04/D-06) | handler constant | n/a | Timing bounds are inline magic numbers today (`2000` iterations × `delayMicroseconds(10)` at `eeprom_28c.cpp:131-132`; `1024` at `flash_5v_page.cpp:111`; `millis() + 150` at `flash_utils.cpp:34`). The named-constant convention Phase 118 OBS-03 will cite (`AT28C_TBLC_MAX_US = 100`) does not exist yet — this phase's constant is its first instance. |
| Per-byte read-back with failing-address attribution (D-07/D-08) | handler-local verify | batch verify | Closest is `memory_verify_execute` (`memory.cpp:308-328`), which does per-byte compare + `MSG_ERR_VERIFY` with `{expected, observed, addr[3]}` — but it is a **whole-operation MAIN handler**, not an in-page read-back. Payload shape is copyable; placement is not. |
| A `handle->firestarter_get_data`-only poll asserted to emit zero strobes | native test | trace assertion | Today the zero-strobe property is a *by-product* of the mock, asserted only indirectly via `strobe_overflowed() == 0` and full-stream equality. No case asserts the completion path's strobe contribution directly. |

---

## Metadata

**Analog search scope:** `firestarter/src/proms/`, `firestarter/include/`,
`firestarter/test/native/avr/` (all suites + `_shared/`), `firestarter/platformio.ini`,
`firestarter_app/tests/` (grep only, for the planted-violation precedent).
**Files read in full:** `eeprom_28c.cpp`, `flash_5v_page.cpp`, `flash_utils.cpp`, `flash_utils.h`,
`rurp_register_utils.h`, `sdp_expected.h`, `host_stubs_common.inc`, `test_sdp_harness.cpp`,
`test_eeprom28c_sdp.cpp`, `test_val_eeprom28c.cpp`, `firestarter/CLAUDE.md`, `117-CONTEXT.md`.
**Files read in part:** `memory.cpp` (:170-289), `platformio.ini` (:55-158),
`test_eeprom28c_sdp/host_stubs.cpp` (:1-60), `RED-BASELINE.md` (headings + tail).
**Repo state:** `firestarter` on `v1.22-at28c-software-data-protection-lifecycle`. No file was
modified by this mapping pass; no build was run.
**Pattern extraction date:** 2026-07-28
