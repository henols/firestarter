# Phase 138: Preconditions & Baseline - Pattern Map

**Mapped:** 2026-08-08
**Files analyzed:** 11 (10 from RESEARCH §"Wave 0 gaps", one of which is a 2-file pair)
**Analogs found:** 11 / 11 (10 exact, 1 role-match-plus-gap)

**Scope note.** This document does *not* re-derive `138-RESEARCH.md`'s mechanism findings, figures, or
git ground truth. It answers one question per new/modified file: *which existing file does the
executor copy, and which exact lines?* Every excerpt below was read live this session from the path
and line range named.

**Repo ownership reminder** (meta `CLAUDE.md`): items 1–8 land **inside the `firestarter` submodule**
(`/workspaces/firestarter`, its own git repo, on the milestone branch); items 9–10 land in the **meta**
repo under `.planning/`. Paths in the tables are relative to the owning repo.

---

## File Classification

| New/Modified File | Owner repo | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|---|
| `test/native/avr/_shared/host_stubs_common.inc` (MODIFY, additive) | firestarter | shared test stub layer | event-driven (record-on-call) | **the same file's own `HOST_STUBS_REAL_REGISTER_UTILS` block**, `host_stubs_common.inc:55-130` | exact (self-analog) |
| `test/native/avr/_shared/eprom_v131_expected.h` (CREATE) | firestarter | frozen test fixture + comparator | transform (ordered stream compare) | `test/native/avr/_shared/sdp_expected.h` | exact |
| `test/native/avr/test_trace_eprom_v131/host_stubs.cpp` (CREATE) | firestarter | per-suite stub/config TU | config (link-time) | `test/native/avr/test_sdp_harness/host_stubs.cpp` (primary) + `test/native/avr/test_val_eprom/host_stubs.cpp` (secondary) | exact |
| `test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp` (CREATE) | firestarter | test (Unity suite) | streaming capture → positional assert | `test/native/avr/test_sdp_harness/test_sdp_harness.cpp` (primary) + `test_val_eprom/test_val_eprom.cpp` (secondary) | exact |
| `platformio.ini` (MODIFY) | firestarter | config (build env) | config | `[env:native_pinmap_provisional]`, `platformio.ini:255-292` | exact |
| `tests/golden/eprom_v131_trace_inventory.json` (CREATE) | firestarter | data fixture (identity record) | file-I/O record | `tests/golden/sdp_expected_inventory.json` | exact |
| `tests/test_golden_trace_identity_eprom_v131.py` (CREATE) | firestarter | test (pytest gate) | file-I/O + subprocess(git) | `tests/test_golden_trace_identity.py` | exact |
| `scripts/baseline/size_baseline_v131.json` (CREATE) | firestarter | immutable measurement record | batch measurement | `scripts/baseline/size_baseline_base01.json` (schema) + `scripts/baseline/size_baseline.json` (`meta.note`, `meta.warm_vs_cold_correction`, `meta.deltas_vs_base01`) | exact |
| `.planning/phases/138-preconditions-baseline/138-BASELINE.md` (CREATE) | meta | narrative record | document | `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md` | exact |
| `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` (CREATE) | meta | self-checking utility script | batch transform (JSON → histogram) | `.planning/phases/136.1-sdp-partition-provenance/136.1-check-blast-radius.py` + `firestarter_app/firestarter/database.py:128-143` (the parser to import, not reimplement) | exact |
| `.planning/phases/138-preconditions-baseline/138-0N-PULSE-DISTRIBUTION.md` (CREATE, the script's committed output) | meta | verbatim output record | document | `.planning/phases/136.1-sdp-partition-provenance/136.1-01-BLAST-RADIUS.md` | exact |

---

## Pattern Assignments

### 1. `firestarter/test/native/avr/_shared/host_stubs_common.inc` — MODIFY (additive `HOST_STUBS_RECORD_TIMING`)

**Analog:** the same file's two existing recorder blocks. Copy their *shape*; do not restructure them.

**Guard-contract header comment** — `host_stubs_common.inc:55-80`. This is the exact prose contract
the new block's comment must mirror (opt-IN, "no existing suite may define it", the byte-exact claim,
and an enumerated (a)…(e) rationale):

```c
/* Ordered strobe recorder (flag: HOST_STUBS_REAL_REGISTER_UTILS) — Phase 116 TRACE-01 / D-05 / D-07.
 * Define HOST_STUBS_REAL_REGISTER_UTILS before including this file to
 * activate this SECOND, independent opt-in layer (it composes with, does
 * not replace, HOST_STUBS_RECORD_BUS above). This is an opt-IN guard: no
 * existing suite may define it — flag off must stay byte-exact for all 14
 * pre-existing suites.
 *
 * (a) Opt-IN: the defining suite's host_stubs.cpp must `#define
 *     HOST_STUBS_REAL_REGISTER_UTILS` BEFORE `#include`-ing this file.
 * (b) Why: ...
 * (e) No existing suite may define this flag — flag off is byte-exact. */
```

> Two corrections the new comment must NOT inherit: (i) the "composes with, does not replace" claim is
> false at the preprocessor level — the structure is `#ifdef …:81 / #elif defined(HOST_STUBS_RECORD_BUS):131 / #else:153`;
> (ii) the "14 pre-existing suites" count is stale — `platformio.ini`'s pinned envs carry **17**.
> State the true count and the true composition in the new block.

**Guard open + cap constant + companion opt-out `#define`s** — `host_stubs_common.inc:81-91`:

```c
#ifdef HOST_STUBS_REAL_REGISTER_UTILS
#define HOST_STUBS_MAX_STROBES 512
#define HOST_STUBS_CUSTOM_CONTROL_PIN
#define HOST_STUBS_CUSTOM_DATA_BUFFER
#define HOST_STUBS_CUSTOM_HW_REVISION_BLOCK
```

**Kind enum + entry struct + TU-local storage + `extern "C"` accessors** — `host_stubs_common.inc:92-107`
(this is the block `HOST_STUBS_RECORD_TIMING` clones, with `{kind, us, seq}` instead of `{kind, pin, value}`):

```c
enum { STROBE_KIND_DATA = 1, STROBE_KIND_PIN = 2 };
struct strobe_entry_t {
    uint8_t kind;
    uint8_t pin;
    uint8_t value;
};
static strobe_entry_t s_strobes[HOST_STUBS_MAX_STROBES];
static int s_strobe_count = 0;
static int s_strobe_overflow = 0;

extern "C" void clear_strobes()     { s_strobe_count = 0; s_strobe_overflow = 0; }
extern "C" int  strobe_count()      { return s_strobe_count; }
extern "C" int  strobe_overflowed() { return s_strobe_overflow; }
extern "C" uint8_t strobe_kind(int i)  { return s_strobes[i].kind; }
extern "C" uint8_t strobe_pin(int i)   { return s_strobes[i].pin; }
extern "C" uint8_t strobe_value(int i) { return s_strobes[i].value; }
```

**Push function with the overflow-flag-not-abort discipline** — `host_stubs_common.inc:109-118`
(`timing_push` copies this verbatim in shape, including the trailing-comment style):

```c
static void strobe_push(uint8_t kind, uint8_t pin, uint8_t value) {
    if (s_strobe_count < HOST_STUBS_MAX_STROBES) {
        s_strobes[s_strobe_count].kind  = kind;
        s_strobes[s_strobe_count].pin   = pin;
        s_strobes[s_strobe_count].value = value;
        s_strobe_count++;
    } else {
        s_strobe_overflow = 1;  /* tail dropped; prefix stays valid — Pitfall 2 */
    }
}
```

Note `timing_push` must be reachable from the suite's `setUp()` lambda, so — unlike `strobe_push`
(`static`) — it needs `extern "C"` linkage. Its `seq` field is `s_strobe_count` at push time
(RESEARCH option B); that read is only valid while both guards are defined, so the new block must
either sit **inside** `#ifdef HOST_STUBS_REAL_REGISTER_UTILS` or `#error` when timing is requested
without it.

**Opt-out guard shape for R2's `HOST_STUBS_CUSTOM_READ_DATA_BUFFER`** — copy `host_stubs_common.inc:179-183`
(`#ifndef` wrapping, no `#else`), applied to the currently-**unguarded** definition at `:185-187`:

```c
#ifndef HOST_STUBS_CUSTOM_DATA_BUFFER
extern "C" void rurp_write_data_buffer(uint8_t data) {
    (void)data;
}
#endif
```
```c
extern "C" uint8_t rurp_read_data_buffer() {      /* :185-187 — the R2 edit site, today unguarded */
    return 0;
}
```

**Opt-out registration comment** — new opt-out names go in the file's own header list at `:22-28`:

```c
 * Per-suite opt-outs (define BEFORE including this file):
 *   - HOST_STUBS_CUSTOM_VOLTAGE_MV   — suite provides its own
 *                                      rurp_read_voltage_mv (e.g.,
 *                                      test_flash_intel_vpp mocks it).
 *   - HOST_STUBS_CUSTOM_HW_REVISION  — suite provides its own
 *                                      rurp_get_hardware_revision (e.g.,
 *                                      test_flash_intel_vpp mocks it).
```

**Do not** define `delay()` / `delayMicroseconds()` here (duplicate symbol against ArduinoFake's
`FunctionFake.cpp`). The hook goes in the suite's `setUp()` — see item 4.

---

### 2. `firestarter/test/native/avr/_shared/eprom_v131_expected.h` — CREATE

**Analog:** `test/native/avr/_shared/sdp_expected.h` (426 lines, read in full).

**Header guard + includes** — `sdp_expected.h:28-33`:

```c
#ifndef __SDP_EXPECTED_H__
#define __SDP_EXPECTED_H__

#include <stdint.h>
#include <unity.h>
#include "firestarter.h"  /* LEAST_SIGNIFICANT_BYTE / MOST_SIGNIFICANT_BYTE / OUTPUT_ENABLE / CHIP_ENABLE (via rurp_shield.h) */
```

**Recorder-accessor declarations, declared once for all consumers** — `sdp_expected.h:35-43`
(the new header declares these *plus* the six timing accessors):

```c
/* Recorder accessors — symbols compiled because host_stubs.cpp defines
 * HOST_STUBS_REAL_REGISTER_UTILS (116-01). Declared once here so both
 * Phase-116 suites get them from a single place. */
extern "C" void    clear_strobes();
extern "C" int     strobe_count();
extern "C" int     strobe_overflowed();
extern "C" uint8_t strobe_kind(int i);
extern "C" uint8_t strobe_pin(int i);
extern "C" uint8_t strobe_value(int i);
```

**Locally-named mirror struct + `#define`d mirrors of the TU-local enum** — `sdp_expected.h:45-58`.
The naming rationale (*"given its own name here since the recorder's own struct is TU-local"*) is
load-bearing and must be restated for the new type:

```c
/* Matches host_stubs_common.inc's strobe_entry_t exactly (kind/pin/value),
 * given its own name here since the recorder's own struct is TU-local
 * (defined inside the host_stubs.cpp .inc-include, not exported). */
typedef struct {
    uint8_t kind;
    uint8_t pin;
    uint8_t value;
} sdp_strobe_t;

/* Mirrors host_stubs_common.inc's `enum { STROBE_KIND_DATA = 1, STROBE_KIND_PIN = 2 };` ... */
#define STROBE_KIND_DATA 1
#define STROBE_KIND_PIN  2
```

**`first_divergence()` — never counts, treats length mismatch as divergence at the shorter length** — `sdp_expected.h:64-78`:

```c
static int sdp_first_divergence(const sdp_strobe_t* expected, int expected_len) {
    int recorded_len = strobe_count();
    int n = (recorded_len < expected_len) ? recorded_len : expected_len;
    for (int i = 0; i < n; i++) {
        if (strobe_kind(i) != expected[i].kind ||
            strobe_pin(i)  != expected[i].pin  ||
            strobe_value(i) != expected[i].value) {
            return i;
        }
    }
    if (recorded_len != expected_len) {
        return n; /* length mismatch, no earlier element difference: diverge at the shorter length */
    }
    return -1;
}
```

**`assert_stream_equals()` — overflow check FIRST, then length, then element-by-element, failing with
the index and both triples** — `sdp_expected.h:86-107`:

```c
static void sdp_assert_stream_equals(const sdp_strobe_t* expected, int expected_len, const char* ctx) {
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), ctx);
    TEST_ASSERT_EQUAL_MESSAGE(expected_len, strobe_count(), ctx);

    int div = sdp_first_divergence(expected, expected_len);
    if (div != -1) {
        char msg[320];
        int rec_len = strobe_count();
        if (div < rec_len && div < expected_len) {
            snprintf(msg, sizeof(msg),
                "%s: diverges at index %d -- expected {kind=%u pin=%u value=0x%02X}, recorded {kind=%u pin=%u value=0x%02X}",
                ctx, div, ...);
        } else {
            snprintf(msg, sizeof(msg),
                "%s: diverges at index %d (length mismatch -- expected_len=%d recorded_len=%d)",
                ctx, div, expected_len, rec_len);
        }
        TEST_FAIL_MESSAGE(msg);
    }
}
```

The v1.31 comparator asserts **both** `strobe_overflowed() == 0` and `timing_overflowed() == 0`
before anything else, then walks the merged stream (strobes spliced with timings at their `seq`
boundary).

**Snapshot helper for stream-vs-stream comparison** — `sdp_expected.h:113-122`:

```c
static int sdp_snapshot(sdp_strobe_t* out, int max_len) {
    int n = strobe_count();
    if (n > max_len) n = max_len;
    for (int i = 0; i < n; i++) { out[i].kind = strobe_kind(i); ... }
    return n;
}
```

**Array declaration form + provenance comment + `_LEN` macro** — `sdp_expected.h:124-168`. The
declaration line shape is what the python gate's regex keys on (see item 7), and the per-array
comment must record *how it was obtained* and *what non-obvious behaviour it encodes*:

```c
/* ─── SHIPPED stream ────────────────────────────────────────────────────────
 * ...
 * Elision is real and load-bearing: write #4 (address 0x5555, payload 0xAA)
 * emits NO address latch at all (index 30) because the cached LSB/MSB
 * already hold 0x55/0x55 from write #3 -- rurp_write_to_register returns
 * early (rurp_register_utils.h:28-37). A raw call-log golden would assert 6
 * phantom entries here that the shield never sees (Pitfall 4).
 */
static const sdp_strobe_t SDP_SHIPPED_DIP28_28C256[] = {
    /* write #1  addr 0x5555  payload 0xAA */
    {1, 0, 0x55}, {2, 1, 1}, {2, 1, 0},
    ...
};
#define SDP_SHIPPED_DIP28_28C256_LEN (int)(sizeof(SDP_SHIPPED_DIP28_28C256) / sizeof(SDP_SHIPPED_DIP28_28C256[0]))
```

Also copy the file-level provenance banner at `sdp_expected.h:7-26` — *"Every literal array below was
authored EMPIRICALLY from a recorded dump of real production code (never hand-derived)"* — and the
closing `#endif /* __SDP_EXPECTED_H__ */` at `:426`.

**Element-literal convention to preserve:** entries are written as bare `{kind, pin, value}` triples
with a `/* write #N … */` comment per logical group, not one entry per line. A v1.31 merged-stream
array should keep that density and mark each timing entry inline.

---

### 3. `firestarter/test/native/avr/test_trace_eprom_v131/host_stubs.cpp` — CREATE

**Primary analog:** `test/native/avr/test_sdp_harness/host_stubs.cpp` (60 lines — the only
`HOST_STUBS_REAL_REGISTER_UTILS` consumer pair, and the file that owns `reset_register_cache`).
**Secondary analog:** `test/native/avr/test_val_eprom/host_stubs.cpp` (46 lines — the named analog;
copy its "Suite-specific extensions" doc-block shape and its PITFALL note).

**Doc-block + PITFALL shape** — `test_val_eprom/host_stubs.cpp:10-19`:

```c
 * Suite-specific extensions:
 *   - HOST_STUBS_RECORD_BUS: activate the recording buffer so the test can
 *     observe all rurp_write_to_register calls and assert VPP-enable CTL bits.
 *   - HOST_STUBS_CUSTOM_HW_REVISION: override hardware revision to return 1
 *     (non-REV0) so eprom_check_vpp does NOT take the REVISION_0 early-return
 *     path — the VPP write that the positive test asserts WILL fire.
 *
 * PITFALL 1 (from 71-PATTERNS.md): HOST_STUBS_RECORD_BUS MUST be defined
 * BEFORE #include of host_stubs_common.inc — the guard reads at include time.
```

**Include order + opt-in define + the real-header include AFTER the `.inc`** — `test_sdp_harness/host_stubs.cpp:26-43`
(this exact order is load-bearing; `test_val_eprom/host_stubs.cpp:21-38` shows the same first half):

```c
#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

/* Activate the ordered strobe recorder (opt-IN). MUST precede the include. */
#define HOST_STUBS_REAL_REGISTER_UTILS

#include "../_shared/host_stubs_common.inc"

/* D-05: production's real cache-compare + latch-strobe sequencing, instead of
 * a hand-maintained replica that could silently drift from
 * rurp_write_to_register / rurp_internal_write_to_register. */
#include "rurp_register_utils.h"
```

The v1.31 suite defines `HOST_STUBS_REAL_REGISTER_UTILS` **and** `HOST_STUBS_RECORD_TIMING` (and, if
R2 is chosen, `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` plus its own stateful `rurp_read_data_buffer()`),
all before the `.inc` include.

**`reset_register_cache` seam — copy verbatim, comment included** — `test_sdp_harness/host_stubs.cpp:45-59`
(Pitfall 5; without this the first Unity case's trace is contaminated by the `0xff` init value):

```c
/* Pitfall 1 / Runtime State Inventory (116-RESEARCH.md): lsb_address,
 * msb_address and control_register are non-static globals
 * (rurp_register_utils.h:12-14) initialised to 0xff. They persist across
 * Unity test cases in this single binary, and the 0xff CONTROL value ORs a
 * VPP-regulator bit (CTRL_VPP_REGULATOR_ENABLE, 0x80) into the FIRST address
 * write of any case that does not reset them ... Every case must reset the cache
 * deliberately before driving anything.
 */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl) {
    lsb_address = lsb;
    msb_address = msb;
    control_register = ctrl;
}
```

**Suite-local mock pattern (if a hw-revision override is needed)** — `test_val_eprom/host_stubs.cpp:40-46`:

```c
#ifdef HARDWARE_REVISION
static uint8_t s_mock_hw_rev = 1;
extern "C" void set_mock_hw_rev_eprom(uint8_t r) { s_mock_hw_rev = r; }
extern "C" uint8_t rurp_get_hardware_revision() { return s_mock_hw_rev; }
#endif
```

> Note: `HOST_STUBS_REAL_REGISTER_UTILS` already defines `HOST_STUBS_CUSTOM_HW_REVISION_BLOCK`
> (`host_stubs_common.inc:90`), so the four hw-revision stubs come from the real
> `rurp_hw_rev_utils.h` — do **not** additionally define `HOST_STUBS_CUSTOM_HW_REVISION` the way
> `test_val_eprom` does, or the symbols collide.

---

### 4. `firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp` — CREATE

**Primary analog:** `test_sdp_harness/test_sdp_harness.cpp` (strobe assertions, drive ordering,
address-keyed read mock). **Secondary analog:** `test_val_eprom/test_val_eprom.cpp` (the 27C handle
construction and the `main()`/`RUN_TEST` block).

**Fixture include + reset-seam extern** — `test_sdp_harness.cpp:60-67`:

```c
#include "../_shared/sdp_bus_config.h"
#include "../_shared/sdp_expected.h"

using namespace fakeit;

/* host_stubs.cpp's reset seam (D-05) — must run after configure_memory, which
 * itself writes address 0 (mem_util_set_address(handle, 0), memory.cpp:68). */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl);
```

The literal string `_shared/eprom_v131_expected.h` in this file is what item 7's
consumer-inclusion check greps for — keep the relative-include spelling identical.

**`setUp()` — the ArduinoFake mock set, with the "these are load-bearing, do not remove" comment** — `test_sdp_harness.cpp:80-110`:

```c
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    /* REQUIRED by D-05: the real rurp_register_utils.h calls delayMicroseconds
     * ... ArduinoFake ABORTS (SIGABRT) on any unmocked
     * virtual ... Do not remove these as "unused" — they are load-bearing. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();
    When(Method(ArduinoFake(), delay)).AlwaysReturn();
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);

    clear_strobes();
    reset_register_cache(0x00, 0x00, 0x00);
    ...
}
```

The v1.31 suite replaces the two `.AlwaysReturn()` timing mocks with recording hooks and adds
`clear_timings()`. `test_val_eprom.cpp:59-61` documents *why* `delay` must be mocked at all
(`eprom_check_vpp` calls `delay(100)`, `eprom_write_execute` calls `delay(500)`).

**`.AlwaysDo(λ)` with argument capture — the only supported timing seam.** Two in-repo precedents:

`test_messages/serial_read_mock.h:93-100` (captures the call's arguments):

```cpp
When(Method(ArduinoFake(Serial), readBytes))
    .AlwaysDo([&queue, &pos](char* buf, size_t length) -> size_t {
        size_t count = 0;
        while (count < length && pos < queue.size()) {
            buf[count++] = (char)queue[pos++];
        }
        return count;
    });
```

`test_messages/test_rurp_log_id.cpp:59-63` (accumulates each call into host-side storage — the
closest analog to `timing_push`, per its own header note at `:31-32`, *"one .AlwaysDo handler
accumulates every write into a host std::vector"*):

```cpp
When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
    .AlwaysDo([](uint8_t b) -> size_t {
        captured.push_back(b);
        return (size_t)1;
    });
```

Note both existing `.AlwaysDo` uses return a value; `delay`/`delayMicroseconds` are `void`, so the
new lambdas' return type is `void` (capture-less lambdas, since `timing_push` is a free `extern "C"`
symbol — matching `test_rurp_log_id.cpp`'s capture-less form rather than `serial_read_mock.h`'s
`[&queue, &pos]`).

**Handle construction, 27C** — `test_val_eprom.cpp:69-79` (the closest 27C handle in the tree; note
its `h = {}` leaves `bus_config` zeroed, which is exactly the gap RESEARCH Q1/A3 flags):

```c
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol   = protocol;
    h.cmd        = cmd;
    h.response_code = RESPONSE_CODE_OK;
    h.vpp_mv     = 0;  /* vpp setpoint=0 matches stub voltage=0: no warn/error */
    h.chip_id    = 0;  /* skip chip-ID branch */
    h.mem_size   = 65536; /* 64 KB — keeps blank_check from NULL-ptr in mock */
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    return h;
}
```

…and the `bus_config`-carrying variant to copy for a traced write — `test_sdp_harness.cpp:118-128`:

```c
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

**The load-bearing drive order** — `test_sdp_harness.cpp:130-142`. Copy the comment as well as the
code; the ordering is the difference between a valid and a contaminated trace:

```c
/* Load-bearing order: configure_memory (which itself writes address 0) ->
 * reset_register_cache -> clear_strobes -> flash_util_byte_flipping. The
 * cache reset and strobe clear MUST both come after configure_memory
 * (test_val_5v_page.cpp:150-175 records this same hazard). ... */
static void drive(firestarter_handle_t* h, const byte_flip_t* table, size_t len, rurp_register_t ctrl_seed) {
    configure_memory(h);
    reset_register_cache(0x00, 0x00, ctrl_seed);
    clear_strobes();
    flash_util_byte_flipping(h, table, len);
}
```

**Read-back convergence model (R1) — address-keyed mock, and re-assigning BOTH pointers after
`configure_memory`** — `test_sdp_harness.cpp:565-590` and `:612-618`:

```c
/* Pattern 3: dispatch on ADDRESS, not call order. Virgin 0xFF everywhere
 * except the two planted manufacturer/device identity bytes. ... */
static void mock_set_data_keyed(firestarter_handle_t*, uint32_t, uint8_t) {}
static uint8_t mock_get_data_keyed(firestarter_handle_t*, uint32_t addr) {
    if (addr == s_mfr_addr_keyed) { s_reads_at_mfr_addr++; return s_mfr_hi_keyed; }
    ...
    return 0xFF;
}
```
```c
    configure_memory(&h);
    /* configure_memory() overwrites BOTH firestarter_get_data AND
     * firestarter_set_data (Pattern 3) -- the retired suite's own comment
     * covered only get_data. Re-assign both. */
    h.firestarter_get_data = mock_get_data_keyed;
    h.firestarter_set_data = mock_set_data_keyed;
    h.firestarter_operation_init(&h);
```

A v1.31 pulse-counting variant keys on `addr` and returns `0xFF` until the per-address pulse count
reaches N, then the target byte — so `eprom_write_execute`'s retry loop converges in ~3 passes
instead of running all 20 and overflowing the recorder.

**Recorder-accessor externs in the test TU + assertion helper style** — `test_val_eprom.cpp:48-52`
and `:82-100`:

```c
/* Recording API — symbols compiled because host_stubs.cpp defines HOST_STUBS_RECORD_BUS. */
extern "C" void clear_bus_recording();
extern "C" int  bus_recording_count();
extern "C" uint8_t recorded_reg(int i);
extern "C" uint8_t recorded_data(int i);
```

(For the v1.31 suite these come from `_shared/eprom_v131_expected.h` instead — item 2's
"declared once here so both suites get them from a single place" convention.)

**`main()` with grouped `RUN_TEST` comments** — `test_val_eprom.cpp:205-220`:

```c
int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();

    /* POSITIVE: write + init path enables VPP regulator, one test per protocol */
    RUN_TEST(test_eprom_0x07_write_enables_vpp_regulator);
    ...
    return UNITY_END();
}
```

**Empirical-authoring workflow to reuse** (`sdp_expected.h:312-336` records it): a temporary
`#ifdef …_TRACE_DUMP` block in the suite prints ready-to-paste triples; run the built binary
directly (`.pio/build/<env>/firestarter_native`) because **`pio test` swallows `printf`**; hand-check;
paste; delete the dump block.

---

### 5. `firestarter/platformio.ini` — MODIFY (`[env:native_trace_v131]`)

**Analog:** `[env:native_pinmap_provisional]`, `platformio.ini:255-292` — copy it whole and rename.
It is the in-repo precedent for a dedicated extra native env, and its comment already states the
constraint Phase 138 must honour:

```ini
[env:native_pinmap_provisional]
; Phase 124 Plan 08 (MERGE-04, D-11): a THIRD native environment, whose sole
; purpose is ...
;
; HARD CONSTRAINT -- MUST NEVER be folded into [env:native] or
; [env:native_nodevtools]'s test_filter. Both of those are pinned at
; exactly the same 17-entry test_filter list ... and MERGE-06 asserts 141 cases / 17 suites on BOTH of them by
; exact count. This env's test_filter therefore names ONLY its own new
; suite (1 entry, not 18), and this env is NOT added to default_envs
; (:16) -- pio run would try to link a main()-less target.
;
; Also do not feed "native_pinmap_provisional" to check_build_warnings.py
; until Plan 124-10 adds it to the baseline's warnings block -- an unknown
; env name is exit 2 there today.
platform = native
test_framework = unity
test_filter =
	native/avr/test_pinmap_provisional
build_flags =
	${env:native.build_flags}
	-I test/native/avr/test_pinmap_provisional
	-D RURP_PINMAP_PROVISIONAL=1
lib_deps =
	fabiobatsilva/ArduinoFake@^0.4.0
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>
test_build_src = yes
```

Load-bearing details for the copy:
- `build_flags` inherits via `${env:native.build_flags}` (NOT `${env.build_flags}`), which brings the
  whole 17-entry `-I` list plus `-std=gnu++17`, `-I include`, `-D RURP_BOARD_NAME=\"native\"`.
- Add exactly one `test_filter` line (`native/avr/test_trace_eprom_v131`) and one matching
  `-I test/native/avr/test_trace_eprom_v131` — *both*, per `firestarter/CLAUDE.md` §"Reuse pattern
  for future native tests" (v1.22 Phase 119 D-04 correction).
- Do **not** touch `default_envs` at `platformio.ini:16` (`uno, uno328pb, leonardo`).
- Do **not** add the suite to `[env:native]`'s list (`:102-119` filter, `:120-141` includes) or
  `[env:native_nodevtools]`'s (`:206-223`, `:224-246`) — both pinned at 17 entries / 141 cases.
- Indentation in this file is a **literal tab** before each list entry.
- Optional extra `-D` for the new env if the timing guard is set env-wide rather than in
  `host_stubs.cpp` — mirror `-D RURP_PINMAP_PROVISIONAL=1`'s placement.

**The gate caveat to carry into the plan** (RESEARCH, measured): `check_size_baseline.py:99-100`
hardcodes `NATIVE_ENVS = ("native", "native_nodevtools")` and `compare_native` does a bare
`rec = baseline["native_envs"][env]` at `:278` → an unknown env name raises an uncaught `KeyError`
(exit 1, not the documented exit 2 that `check_build_warnings.py:181` produces). Never pass
`native_trace_v131` to either gate; record its counts only in `size_baseline_v131.json`.

---

### 6. `firestarter/tests/golden/eprom_v131_trace_inventory.json` — CREATE

**Analog:** `tests/golden/sdp_expected_inventory.json` (22 lines — reproduced in full; this *is* the
schema, key names included):

```json
{
  "meta": {
    "source": "test/native/avr/_shared/sdp_expected.h",
    "recorded_by": "Phase 124 Plan 03",
    "requirement": "MERGE-06",
    "blob_sha": "dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83",
    "recorded_at_head": "17c7614d7d3ec1701cd618711a366dc11253299f",
    "why_two_checks": "A whole-file blob match alone cannot distinguish 'unchanged' from 'an array deleted together with the assertions that consumed it' -- ... so the per-array name+entry-count inventory is what makes a deletion visible.",
    "how_to_update": "If this file legitimately changes, re-derive this inventory from the file with an independent parse (never hand-edit the numbers) AND state in the commit message which array changed and why -- never edit this JSON merely to make a surprise disappear."
  },
  "arrays": [
    { "name": "SDP_SHIPPED_DIP28_28C256", "entries": 54 },
    { "name": "SDP_FIXED_DIP28_28C256", "entries": 54 },
    ...
    { "name": "SDP_FIXED_LOCK_DIP32_28C512_EEPROM", "entries": 33 }
  ]
}
```

Copy conventions exactly: 8 `meta` keys with those spellings; `arrays` is an **ordered** list of
`{name, entries}` objects (order must match declaration order in the header); `blob_sha` is a git
blob SHA obtainable **without committing** via `git hash-object <path>` (measured identical to
`git rev-parse HEAD:<path>`), so fixture + inventory land in one commit. `recorded_by` /
`requirement` become `"Phase 138 Plan NN"` / `"PREP-03"`. Consider adding a v1.31-specific
`meta` key recording the measured entry counts and the `strobe_overflowed()==0` observation, and a
`meta.frozen_for` naming Phase 144/TEST-06 as the consumer of the diff.

---

### 7. `firestarter/tests/test_golden_trace_identity_eprom_v131.py` — CREATE (parallel module, not a refactor)

**Analog:** `tests/test_golden_trace_identity.py` (245 lines, read in full). Author a **parallel**
module with new constants — check 6 scans *its own source*, so hollowing it into a shared helper
breaks its self-enforcement.

**House rules confirmed live:** `find /workspaces/firestarter -name conftest.py` returns **nothing** —
stdlib + pytest only, self-contained path resolution, no conftest. Stated in the module docstring at
`:61-64`:

```python
Self-contained path resolution below -- NOT in conftest.py (firestarter/
tests/ has no conftest.py anywhere in the repo; a recorded house-rule pattern
decision per test_update_version.py's own comment, not an omission).
Stdlib and pytest only.
```

**Docstring shape** — `:1-65`: title line naming Phase/Plan, a `Requirements:` line, a **"Defect class
this closes"** paragraph, then a numbered `Coverage:` list with one entry per test function.

**Constants block — the five things that must be re-pointed** — `:67-88`:

```python
import json, os, re, shutil, subprocess
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_FIXTURE_PATH = "test/native/avr/_shared/sdp_expected.h"
_INVENTORY_JSON = _HERE / "golden" / "sdp_expected_inventory.json"
_CONSUMERS = (
    _REPO_ROOT / "test" / "native" / "avr" / "test_sdp_harness" / "test_sdp_harness.cpp",
    _REPO_ROOT / "test" / "native" / "avr" / "test_eeprom28c_sdp" / "test_eeprom28c_sdp.cpp",
)

_ARRAY_DECL_RE = re.compile(
    r"static const sdp_strobe_t\s+(\w+)\[\]\s*=\s*\{(.*?)\};",
    re.DOTALL,
)
_ENTRY_RE = re.compile(r"\{[^{}]*\}")
```

New values: `_FIXTURE_PATH = "test/native/avr/_shared/eprom_v131_expected.h"`,
`_INVENTORY_JSON = _HERE / "golden" / "eprom_v131_trace_inventory.json"`, `_CONSUMERS` = the single
new suite `.cpp`, `_ARRAY_DECL_RE` retyped to the new struct name, and the non-vacuity floor
(literal `>= 9` at `:199`) set to the new array count.

**`_resolve_git()` — fail-closed via a plain `assert`, never a skip** — `:90-108`:

```python
def _resolve_git():
    """Resolve the `git` binary, fail-closed. ..."""
    git_bin = shutil.which(os.environ.get("GIT", "git"))
    assert git_bin is not None, (
        "git not found on PATH (checked $GIT, falling back to 'git'). This "
        "must FAIL the suite, never be silently skipped ..."
    )
    return git_bin
```

**`_git()` — list-form argv, `cwd=_REPO_ROOT`, assert clean exit** — `:111-127`.

**`_parse_arrays()` — an INDEPENDENT re-parse that strips comments first** — `:130-142`:

```python
def _parse_arrays(text):
    """Re-derive the ordered (name, entries) pairs ... independently of the committed inventory JSON.
    Strips C-style comments first so commented-out entries can never inflate a count."""
    arrays = []
    for m in _ARRAY_DECL_RE.finditer(text):
        name, body = m.group(1), m.group(2)
        body_nc = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
        body_nc = re.sub(r"//[^\n]*", "", body_nc)
        arrays.append((name, len(_ENTRY_RE.findall(body_nc))))
    return arrays
```

**The six tests to copy** (names, and the exact assertion messages' discipline):

1. `test_blob_sha_matches_the_recorded_inventory` — `:153-163`, `_git("rev-parse", f"HEAD:{_FIXTURE_PATH}")`
   vs `meta.blob_sha`, with the "re-derive … never hand-edit the SHA" remediation in the message.
2. `test_array_names_match_the_recorded_inventory` — `:166-172`, ordered list equality.
3. `test_array_entry_counts_match_the_recorded_inventory` — `:175-193`, positional loop raising
   `AssertionError(f"first divergence at index {i} -- recorded={{…}}, live={{…}}")`, **then** a
   length-equality assert. Never a bare "lists differ".
4. `test_inventory_is_non_vacuous` — `:196-207`, `len(arrays) >= N` **and** every `entries >= 1`.
5. `test_consuming_suites_still_include_the_fixture` — `:210-217`, literal-substring check per consumer.
6. `test_git_is_required_not_optional` — `:220-245`, self-scan:

```python
    this_source = Path(__file__).read_text()
    for line in this_source.splitlines():
        stripped = line.strip()
        assert not stripped.startswith("pytest.skip"), (...)
        assert not stripped.startswith("@pytest.mark.skipif"), (...)
```

Note the `startswith()` (not `in`) choice is deliberate — it avoids the module self-matching its own
prose, per the recorded 124-01 Deviation #3 fix.

---

### 8. `firestarter/scripts/baseline/size_baseline_v131.json` — CREATE (never rewrite `size_baseline.json`)

**Schema analog:** `scripts/baseline/size_baseline_base01.json` (93 lines).
**Prose-convention analog:** `scripts/baseline/size_baseline.json` (`meta.note` `:17`,
`meta.warm_vs_cold_correction` `:18`, `meta.deltas_vs_base01` `:19-35`, `warnings.counting_command` `:118`).

**Top-level shape** — `size_baseline_base01.json`: `meta` (`:2-18`), `avr_targets` (`:19-44`, 6 keys
per target: `flash_used`, `flash_total`, `flash_free`, `ram_used`, `ram_total`, `ram_free`),
`native_envs` (`:45-58`, 4 keys per env: `cases`, `succeeded`, `suites`, `all_passed`), `envs_agree`
(`:59`), `envs_agree_note` (`:60`), `warnings` (`:61-92`, with `avr`/`native`/`policy`/
`counting_command`/`note`).

**`meta` key list to reproduce** — `size_baseline_base01.json:2-18`:

```json
  "meta": {
    "generated": "2026-07-30",
    "phase": "123",
    "generated_by": "123-01-PLAN.md Task 2 measurement",
    "firmware_tree_sha": "5c9160a34b665878b05403ab014b959926feb6bf",
    "host_app_tree_sha": "e7d3ee8c8a41cd20e9159ab43b5cd969603d773e",
    "platformio_core": "6.1.19",
    "platform_atmelavr": "5.2.0",
    "toolchain_atmelavr": "1.70300.191015",
    "avr_gcc": "7.3.0",
    "framework_arduino_avr": "5.3.0",
    "framework_arduino_avr_minicore": "3.1.2",
    "roadmap_cross_check": "...",
    "supersedes": "...",
    "consumed_by": "...",
    "note": "Every figure below was re-measured in this session (D-03) via `pio run -t clean -e <env> && pio run -e <env>` for the three AVR targets and `pio test -e <env>` for the two native environments, on the firmware tree at firmware_tree_sha above ... Nothing here is recalled from ROADMAP.md or PROJECT.md prose."
  },
```

**`meta.note` — the command-attribution + cold-procedure discipline** (`size_baseline.json:17`), the
sentence pair the v131 note must carry:

> "The three native envs … were each measured in BOTH build states, in this exact sequence per env:
> `rm -rf .pio/build/<env>` then a single `pio test -e <env>` invocation with an extended 540000ms
> timeout (the COLD figure — a default 2-minute Bash timeout truncates the toolchain build mid-compile
> and silently contaminates the measurement …), immediately followed by a second `pio test -e <env>`
> invocation with no intervening clean (the WARM figure …)."

**`meta.warm_vs_cold_correction`** (`size_baseline.json:18`) closes with the rule to restate:

> "A future reader who wants to LOWER any of these three watermarks must re-measure cold first, in
> this exact rm -rf + single-invocation sequence, and never guess a new figure down from prose."

**`meta.deltas_vs_*` block shape** — `size_baseline.json:19-35` (per-target `flash_used_delta`,
`ram_used_delta`, `merge05_clause`):

```json
      "uno": {
        "flash_used_delta": 22,
        "ram_used_delta": 0,
        "merge05_clause": "Uno-class flash growth <= 64 B permitted -- +22 is inside the MERGE05_UNO_CLASS_FLASH_BAND=64 band; RAM must be exactly unchanged -- 0 satisfies it exactly."
      },
```

v131 needs **two** such blocks (`deltas_vs_base01` and `deltas_vs_size_baseline`), because the two
records now disagree — and the `merge05_clause` prose should name the remaining headroom against
`MERGE05_UNO_CLASS_FLASH_BAND = 64` (`check_size_baseline.py:107`).

**`warnings.counting_command`** — `size_baseline_base01.json:90` / `size_baseline.json:118`:

```
pio test -e <env> 2>&1 | grep -cE 'warning: *"[^"]+" +redefined'   # macro-redefinition count
pio test -e <env> 2>&1 | grep -cE 'warning:'                       # total
```

**Env seam, for the artifact's own prose** — `check_size_baseline.py:95-96` and
`check_build_warnings.py:82-83` both read
`os.environ.get("FIRESTARTER_SIZE_BASELINE", str(REPO_ROOT / "scripts" / "baseline" / "size_baseline.json"))`,
and an explicit `--baseline PATH` wins (`check_size_baseline.py:392`,
`check_build_warnings.py:271`). One file, two consumers — reuse the seam, add none.

**Additions v131 needs beyond BASE-01's shape:** a `native_envs` entry for
`native_pinmap_provisional` (BASE-01 predates it) and, if the new trace env is measured, one for
`native_trace_v131` — recorded here **only** so a future gate does not raise, mirroring
`size_baseline.json:84`'s `envs_agree_note` carve-out language ("deliberately EXCLUDED from this
agreement claim").

---

### 9. `.planning/phases/138-preconditions-baseline/138-BASELINE.md` — CREATE

**Analog:** `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md` (187 lines, read in
full). Copy the nine-section skeleton and the four discipline devices.

**Title + owner-requirement line** — `131-CI-BASELINE.md:1-4`:

```markdown
# 131-CI-BASELINE: Real fork-base CI run — GATE-07

**Owner requirement:** GATE-07 (delivered here; tick deferred to 131-07 per D-11/D-12 and this
plan's own "may mark NOTHING Complete" rule). **Status:** recorded, RED by design.
```

**§1 The run — a `| Field | Value |` table + the read-only attestation + the "not the stale run" note** — `:6-25`:

```markdown
| Field | Value |
|---|---|
| Run id | `30822281624` |
| URL | https://github.com/henols/firestarter_app/actions/runs/30822281624 |
| Event | `workflow_dispatch` |
| Head branch | `beta` |
| Head SHA | `16a313a040389aa7c88a98b85f79a7d667ca2f6f` (exactly the fork base `16a313a`) |
| Created | `2026-08-03T14:21:13Z` |
| Conclusion | `failure` (terminal) |

Dispatched by the **operator**, per `131-HANDOFF.md`'s procedure. No agent ran
`gh workflow run`; every command in this document ... is a read-only `gh run view` / `gh run list` call.
```

**§2 Fail-closed precondition, six checkboxes each marked `pass`, from ONE json call** — `:27-41`:

```markdown
All six conditions checked via `gh run view 30822281624 --repo henols/firestarter_app
--json event,headBranch,headSha,conclusion,url,createdAt` (read-only):

- run id `30822281624` is numeric — pass
- `gh run view` resolves it — pass
- `event` is `workflow_dispatch` — pass
- `headBranch` is `beta` — pass
- `headSha` begins `16a313a` — pass (`16a313a040389aa7c88a98b85f79a7d667ca2f6f`)
- id is not the prior run `30708836339` — pass
- `conclusion` is terminal (`failure`, not `null`/in-progress) — pass, keying on `conclusion`
  per the v1.23 lesson that `outcome` and `conclusion` are distinct fields
```

**§3 per-step table** (`:43-66`, with sibling jobs explicitly scoped out), **§4 verbatim output**
(`:68-81`, *"the **only substantive lines** that step emitted, quoted verbatim, in order"*),
**§5 a named correction** (`:83-135` — F-07: mechanism, four handling actions, and *"Running mypy
locally to manufacture one would violate D-12's 'read, never compute' rule"*), **§6 resolved tool
versions** (`:137-145`, *"Both read from the log, never invoked locally."*), **§7 What this number is
— and is not** (`:147-158`, including the explicit overclaim warning), **§8 divergence check**
(`:160-175`, stating the rule that *had* they differed, **the measured number wins and both are
recorded without reconciliation**), **§9 Not established by this run** (`:177-181`).

**Footer** — `:183-187`:

```markdown
---

*Phase: 131-gate-hardening-ci-parity — Plan 05, Task 3*
*Recorded: 2026-08-03, from the real run dispatched by the operator per `131-HANDOFF.md`.*
```

**Adaptations 138 needs:** the F-NN correction section (§5) is where PREP-01's squash-merge
adjudication and the two D-07-class gate findings go — one named finding each, with an owner, and no
fix; §1 becomes *per repo* (the firmware's `build.yml` has no `workflow_dispatch`, so its "run" is a
push-triggered run — say which per repo); §3/§4 carry the local cold-measurement commands and their
verbatim tail lines alongside the CI steps; and every figure names the exact command and the tree/SHA
it was measured on, per `131-CI-BASELINE.md`'s attribution style and `size_baseline.json`'s `meta.note`.

---

### 10a. `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` — CREATE

**Analog:** `.planning/phases/136.1-sdp-partition-provenance/136.1-check-blast-radius.py` (201 lines).

**Shebang + docstring: title, numbered assertions, exit-code contract, own non-vacuity obligation,
env-var seams** — `136.1-check-blast-radius.py:1-35`:

```python
#!/usr/bin/env python3
"""136.1-01 blast-radius proof: chip_database.json's PROV-01 regeneration is additive-only.

Compares a PRE-regen snapshot ... and mechanically asserts:

  1. Same set of manufacturers; ...
  2. For every chip entry, every top-level key OTHER than "programming" is byte-identical ...
  ...

Exits 0 and prints a summary on a clean additive-only diff. Exits non-zero, naming the
first offending entry, on ANY violation -- this script's own non-vacuity obligation
(Nyquist #1 in 136.1-VALIDATION.md) is that it must be capable of failing, not merely of
passing.

Both comparison targets are overridable via env vars so this script stays re-runnable
later as a standing regression proof, not a one-shot with hardcoded temp paths:

  PRE_DB_REF    -- git ref to read the PRE-regen file from (default: HEAD~1)
  PRE_DB_PATH   -- if set, read PRE directly from this file path instead of `git show`
  POST_DB_PATH  -- path to the POST-regen file (default: the working tree's
                   firestarter/data/chip_database.json)
  SUBMODULE_DIR -- the firestarter_app git checkout `git show` runs against
                   (default: /workspaces/firestarter_app)
"""
```

**Stdlib-only imports + module constants + env seams (no argparse)** — `:37-47`:

```python
import json
import os
import subprocess
import sys

_NEW_KEYS = {"protect_off_before", "protect_on_after", "infoic_page_size_raw"}
_SUPPLEMENT_PARTS = {"2516", "2532"}  # TEXAS INSTRUMENTS, tools/extra_chips.json
_SUBMODULE_DIR = os.environ.get("SUBMODULE_DIR", "/workspaces/firestarter_app")
_DEFAULT_POST_PATH = os.path.join(
    _SUBMODULE_DIR, "firestarter", "data", "chip_database.json"
)
```

**Loader helpers, env-var-first** — `:50-68` (`_load_pre()` reads `PRE_DB_PATH` or `git -C
_SUBMODULE_DIR show <ref>:<path>` via list-form argv with `check=True`; `_load_post()` reads
`POST_DB_PATH`).

**`main()` — violations list, counters, banner, labelled summary, `VIOLATIONS: N`, `RESULT: PASS|FAIL`,
return 0/1** — `:71-78` and `:176-197`:

```python
def main() -> int:
    ...
    violations: list[str] = []
    entries_compared = 0
    ...
    print("=" * 78)
    print("136.1-01 BLAST-RADIUS PROOF -- chip_database.json regeneration, additive-only")
    print("=" * 78)
    print(f"Total chip entries compared:        {entries_compared}")
    ...
    if violations:
        print(f"VIOLATIONS: {len(violations)}")
        for v in violations:
            print(f"  - {v}")
        print()
        print("RESULT: FAIL -- diff is NOT additive-only. Do not force this through.")
        return 1

    print("VIOLATIONS: 0")
    print("RESULT: PASS -- diff is additive-only (only the three named keys added).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**The parser to MIRROR, not reimplement** — `firestarter_app/firestarter/database.py:128-143`
(verified live at that line range; the docstring's own wording is the D-11 layer statement):

```python
def _parse_pulse_duration(pulse_str: str) -> int:
    """Parse a pulse_duration string from chip_database.json into microseconds.

    Accepts values like "100 us", "1000 us", "Algorithm Controlled", or "".
    Returns the integer microsecond value, or 0 for unknown / algorithm-controlled.
    """
    if not pulse_str:
        return 0
    # Format: "<integer> us"
    parts = pulse_str.split()
    if len(parts) == 2 and parts[1] == "us":
        try:
            return int(parts[0])
        except ValueError:
            pass
    return 0
```

The 136.1 script's precedent is to `git show`/`open()` the JSON and compute in-script. Here the
parser is production code the artifact's credibility depends on, so import it
(`sys.path.insert(0, SUBMODULE_DIR)` then `from firestarter.database import _parse_pulse_duration`)
and let the seam default to `/workspaces/firestarter_app` exactly as `_SUBMODULE_DIR` does. Bucket
from the **raw string**, never the parsed int (parsed `0` is a four-way collision). Read the shipped
`firestarter/data/chip_database.json` directly, or `EpromDatabase(skip_local_override=True)` — a
plain `EpromDatabase()` merges `~/.firestarter/database.json` and skews the distribution
(`firestarter_app/CLAUDE.md`, `database.py`'s `skip_local_override` seam).

**Discretion note:** CONTEXT leaves the location to the planner. The 136.1 precedent is the **phase
directory in meta**, named `<phase>-<name>.py`; both the script and its output landed in the **same
meta commit** (`3624205`) and the invocation is named in the plan's `<verify>` block. The project's
"skills must own their scripts" rule applies to `.claude/skills/*` only — no skill is involved here.

---

### 10b. `.planning/phases/138-preconditions-baseline/138-0N-PULSE-DISTRIBUTION.md` — CREATE (the committed output)

**Analog:** `.planning/phases/136.1-sdp-partition-provenance/136.1-01-BLAST-RADIUS.md` (79 lines).

**Header — names the script, the requirement it proves, and how many runs are recorded** — `:1-14`:

```markdown
# Plan 136.1-01 Task 2 — Blast-Radius Proof (verbatim)

Records the verbatim output of `.planning/phases/136.1-sdp-partition-provenance/136.1-check-blast-radius.py`
proving PROV-01's `chip_database.json` regeneration is additive-only.

Two runs were made:

1. **Pre-commit run** (`PRE_DB_REF=HEAD` override, ...) — the "run this script, stop if non-zero" check the
   plan's action step names, executed before the submodule commit existed.
2. **Post-commit run** (default invocation, no env override ...) — the literal reproducible command this plan's own `<verify>` block names,
   executed after commit `f294821` ... Both runs agree exactly.
```

**Each run: a `##` heading, then a fenced block whose FIRST line is the literal command** — `:16-29`:

```markdown
## Run 1 — pre-commit (`PRE_DB_REF=HEAD`)

```
$ cd /workspaces/firestarter_app && PRE_DB_REF=HEAD python3 /workspaces/.planning/phases/136.1-sdp-partition-provenance/136.1-check-blast-radius.py
==============================================================================
136.1-01 BLAST-RADIUS PROOF -- chip_database.json regeneration, additive-only
==============================================================================
Total chip entries compared:        746
...
VIOLATIONS: 0
RESULT: PASS -- diff is additive-only (only the three named keys added).
```
```

**Reconciliation paragraph against an independent source** — `:46-53` (bolded figures, each tied to
where else the same number appears):

```markdown
**746 total entries compared** (744 upstream-decoded + 2 `extra_chips.json` supplement
entries) — matches `build_db.py`'s own regeneration print exactly ("744 upstream chips
processed + 2 non-upstream supplement chip(s) = 746 total"). ... **0 violations** on both runs: ...
```

**One or more `## Independent confirmation — <mechanism>` sections**, each with its own verbatim
command + output — `:55-66` (`git diff --stat`) and `:68-79` (a pytest run).

For PREP-04 the independent confirmations are: the seed's C2 table (every count reproduced), the
`chip_database.json` blob SHA (identical across all candidate trees), and the
`329 + 417 = 746` whole-DB partition. Per CONTEXT, this file's text is destined to be **quoted
verbatim into a public GitHub comment in Phase 139** — write for a stranger who cannot run the repo,
and keep the D-11 layer sentence (`pulse_duration` string → `pulse-delay` int-µs at
`database.py:128`) in the body, not a footnote.

---

## Shared Patterns

### A. Opt-IN stub guard with a byte-exact flag-off contract
**Source:** `firestarter/test/native/avr/_shared/host_stubs_common.inc:22-28` (opt-out list),
`:46-53` + `:55-80` (opt-IN contracts), `:81-91` (guard open + companion defines).
**Apply to:** items 1, 3.
- Guard names are `HOST_STUBS_<VERB>_<NOUN>`: opt-**IN** = `HOST_STUBS_RECORD_*` /
  `HOST_STUBS_REAL_*`; opt-**OUT** = `HOST_STUBS_CUSTOM_*`.
- The suite `#define`s it **before** `#include`-ing the `.inc` (the guard reads at include time).
- Every new storage/accessor line lives **inside** the new `#ifdef` — nothing outside it changes, so
  flag-off is byte-exact by construction.
- The block's header comment states the contract in the first sentence.

### B. Two independent mechanisms per frozen artifact
**Source:** `firestarter/tests/golden/sdp_expected_inventory.json` `meta.why_two_checks`;
`firestarter/tests/test_golden_trace_identity.py:11-22`.
**Apply to:** items 2, 6, 7 (and, in spirit, 8).
The file and its recorded expectation are read by **separate** readers and compared, so a change to
either alone is visible. `_parse_arrays()` deliberately re-derives rather than importing a shared
helper (`test_golden_trace_identity.py:52-59`).

### C. Ordered full-stream positional equality, naming the first diverging index
**Source:** `firestarter/test/native/avr/_shared/sdp_expected.h:60-107`.
**Apply to:** items 2, 4.
Never a sub-sequence scan, never a count. Assert `overflowed() == 0` **first**, then length, then
element-by-element, failing with the index and both values.

### D. Register-cache reset and mock-installation ordering
**Source:** `firestarter/test/native/avr/test_sdp_harness/host_stubs.cpp:45-59` (the seam),
`test_sdp_harness.cpp:103` (called in `setUp`), `:130-142` (drive order), `:612-618` (both pointers
re-assigned **after** `configure_memory`).
**Apply to:** items 3, 4.
`lsb_address` / `msb_address` / `control_register` are non-`static` globals initialised `0xff` and
persist across Unity cases in one binary; `configure_memory()` overwrites **both**
`firestarter_get_data` and `firestarter_set_data`.

### E. A new native suite costs two lines per env — and never joins a pinned env
**Source:** `firestarter/platformio.ini:16` (`default_envs`), `:102-141` / `:206-246` (the two pinned
17-entry lists), `:255-292` (the dedicated-env precedent + its HARD CONSTRAINT comment);
`firestarter/CLAUDE.md` §"Reuse pattern for future native tests".
**Apply to:** item 5 (and it is what keeps items 3–4 invisible to the pinned envs).

### F. Baseline JSON provenance: every figure attributed to the command that produced it
**Source:** `firestarter/scripts/baseline/size_baseline_base01.json:2-18`;
`size_baseline.json:17-18`, `:84`, `:118-119`.
**Apply to:** items 8, 9.
`meta.note` names the exact invocation sequence and the tree SHA; `meta.warm_vs_cold_correction`
records the trap and both build states; `supersedes` / `consumed_by` state load-bearingness; the
closing rule is "never guess a figure down from prose or from a warm re-run".

### G. Reproducible script + verbatim committed output, in one commit
**Source:** `.planning/phases/136.1-sdp-partition-provenance/136.1-check-blast-radius.py` +
`136.1-01-BLAST-RADIUS.md`.
**Apply to:** items 10a, 10b.
Stdlib only; env-var seams documented in the docstring (no argparse); `"=" * 78` banner; labelled
summary; `VIOLATIONS: N`; `RESULT: PASS|FAIL`; `sys.exit(main())`. Output artifact records **each run
preceded by its literal `$ cd … && python3 …` line**, then reconciles the numbers against an
independent source.

### H. Findings are recorded with an owner, never silently reconciled or fixed
**Source:** `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md:83-135` (§5's F-07
handling: mechanism → four required actions → the "read, never compute" rule) and `:160-175` (§8's
"the measured number wins and both are recorded without reconciliation").
**Apply to:** item 9, and to every divergence the plan's measurement tasks surface (D-07's RED gate,
the `KeyError`-vs-exit-2 taxonomy defect, PREP-01's squash adjudication).

---

## No Analog Found

Files/mechanisms with no close in-repo match. The planner should lean on `138-RESEARCH.md` §"Trace
Capture Mechanism (D-02)" for these, and require the executor to *measure* rather than assume.

| Item | Role | Data Flow | Reason |
|---|---|---|---|
| The timing recorder itself (`HOST_STUBS_RECORD_TIMING` storage + `timing_push` + 6 accessors) | shared stub layer | event-driven | **No timing recorder exists.** `host_stubs_common.inc` has no `delay`/`delayMicroseconds` involvement at all; those symbols are defined by ArduinoFake's `FunctionFake.cpp` and only ever `.AlwaysReturn()`-mocked. Structural analog = the strobe block (item 1); *behavioural* analog for the hook = `test_rurp_log_id.cpp:59-63` and `serial_read_mock.h:93-100`, neither of which records time. |
| The **merged** strobe+timing comparator | test fixture helper | transform | `sdp_assert_stream_equals` compares **one** stream. Splicing timings at their `seq` boundary is new code; copy the failure-message and overflow-first discipline, not the loop. |
| A 27C `bus_config` row for the trace handle | test data | — | `_shared/sdp_bus_config.h` is generated (`tools/gen_sdp_bus_config.py`) and carries **5 rows, all 28C** (`SDP_BUS_CONFIG_COUNT 5`; AT28C256/AT28C64/AT28C16/AT28C010/AT28C040 — verified live). No `DIP28_27256` / `DIP32_27C020` / `DIP24_2716` row exists. Either extend the generator (cross-repo; honours "generated files are never hand-edited") or document a minimal in-fixture config — RESEARCH Q1/A3. |
| `native_trace_v131` coverage by the live gates | config | — | `check_size_baseline.py:99-100` hardcodes `NATIVE_ENVS`; the new env is **unmeasured** by both gates (and raises `KeyError` if passed). Record its counts only in `size_baseline_v131.json`. |

---

## Constraints Re-stated for the Executor (verified against the analogs)

- **No edit to `src/proms/eprom.cpp`, `src/proms/memory.cpp`, or any other write-path source.** The
  program pulse lives at `memory.cpp:329` (`delayMicroseconds(handle->pulse_delay)`); it is observed
  through the stub layer, never modified. Instrumentation lives under `test/` only.
- **Never rewrite `scripts/baseline/size_baseline.json`.** `size_baseline_v131.json` is a new sibling
  read through the existing `FIRESTARTER_SIZE_BASELINE` seam or an explicit `--baseline`.
- **`firestarter_app/firestarter/data/chip_database.json` is GENERATED** — item 10a reads it only.
- **`include/messages.h` is codegen-generated** — untouched by this phase.
- **Flag-off proof wording:** do not write an "empty `git diff`" or "byte-identical file" criterion.
  Scope it to *assertions-unchanged* + named blob SHAs, and prove behaviour by re-asserting
  141 cases / 17 suites / all PASSED on **both** pinned envs via `check_size_baseline.py`'s
  `compare_native`.
- **Fixture + inventory land in ONE commit** — `git hash-object <path>` yields the same SHA as
  `git rev-parse HEAD:<path>` (measured), so no two-commit dance.

---

## Metadata

**Analog search scope:** `/workspaces/firestarter/test/native/avr/` (all suites + `_shared/`),
`/workspaces/firestarter/tests/` (+ `tests/golden/`), `/workspaces/firestarter/scripts/baseline/`,
`/workspaces/firestarter/platformio.ini`, `/workspaces/firestarter_app/firestarter/database.py`,
`/workspaces/.planning/phases/131-gate-hardening-ci-parity/`,
`/workspaces/.planning/phases/136.1-sdp-partition-provenance/`.

**Files read in full:** `host_stubs_common.inc` (272), `sdp_expected.h` (426),
`test_val_eprom/host_stubs.cpp` (46), `test_val_eprom.cpp` (220), `platformio.ini` (291),
`sdp_expected_inventory.json` (22), `test_golden_trace_identity.py` (245),
`size_baseline_base01.json` (93), `size_baseline.json` (121), `131-CI-BASELINE.md` (187),
`136.1-check-blast-radius.py` (201), `136.1-01-BLAST-RADIUS.md` (79),
`test_sdp_harness/host_stubs.cpp` (60).
**Files read in part:** `test_sdp_harness.cpp` (1-150, 540-649), `database.py` (110-149),
`serial_read_mock.h` (40-124), `test_rurp_log_id.cpp` (28-72), `sdp_bus_config.h` (1-60).
**Project instructions consulted:** `/workspaces/CLAUDE.md`, `/workspaces/firestarter/CLAUDE.md`,
`/workspaces/firestarter_app/CLAUDE.md`. Skills present (`.claude/skills/`: `devtest-rootcause`,
`devtest-triage`, `find-skills`, `skill-writer`) — none applies to this phase's file set.

**Read-only compliance:** no source file was modified; no git write command was run in the meta repo
or either submodule; no branch was created, switched, or pushed. The only file written is this one.

**Pattern extraction date:** 2026-08-08
