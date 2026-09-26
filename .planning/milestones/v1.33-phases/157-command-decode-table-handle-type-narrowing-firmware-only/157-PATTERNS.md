<!--
  Phase 157 PATTERNS — v1.33 Source Hygiene & Firmware Size Reduction.

  ⚠ CITATION STALENESS. Every `file:LINE` in this document was measured against
  the CURRENT tree (firestarter @ 1151dc4, post-Phase-154 sweep) in this
  session. These citations will themselves be remapped by Phase 159
  (REMAP-01..04) — see `.planning/v1.33/CITATIONS-STALE.md`. Do NOT trust any
  `json_parser.c:NNN` citation found in a `.planning/` document written BEFORE
  Phase 154: that file lost 198 of 198 provenance citations in the sweep.

  Phase 157 also ADDS two `#include` lines to `src/json_parser.c`
  (`<stddef.h>`, `<string.h>`), which shifts every line number in this document
  by +2 the moment the executor lands the first edit. Cite by symbol name where
  a plan can, not by line.
-->

# Phase 157: Command-Decode Table + Handle Type Narrowing — Pattern Map

**Mapped:** 2026-08-23
**Firmware anchor:** `firestarter` @ `1151dc4`, branch `gsd/v1.33-source-hygiene-firmware-size-reduction`, tree clean
**Files analyzed:** 6 (4 source/test, 2 planning records)
**Analogs found:** 4 of 6 with a real analog; **the crux table has NO true analog** — see §1.

---

## Headline answer, up front

**The `{key, offset, width, clamp}` table is a NEW idiom for this tree.** Three of its four
mechanisms do not exist anywhere in `firestarter/` today:

| Mechanism | Occurrences in `src/ include/ test/ lib/` | Verdict |
|---|---|---|
| `offsetof` | **ZERO** | new idiom |
| `sizeof(((T*)0)->member)` | **ZERO** | new idiom |
| `_Static_assert` (C) | **ZERO** | new idiom |
| `static_assert` (C++) | **exactly one**, `include/eprom_params.h:62`, `#ifdef __cplusplus`-guarded | partial precedent |
| A PROGMEM array of structs with a **string** member, walked by a generic worker | **exactly one — `key_parsers[]` itself**, the thing being replaced | no external model |

Commands run:
```bash
grep -rn "offsetof" src/ include/ test/ lib/            # → no output
grep -rn "sizeof(((" src/ include/ test/                # → no output
grep -rn "_Static_assert\|static_assert" src/ include/ lib/ test/
#   → include/eprom_params.h:62 only
```

So the planner must treat the table shape, the width-derivation idiom and the assertion mechanism
as **design decisions requiring a written rationale**, not as copies. §1 gives the nearest
structural cousin — `src/proms/eprom_params.cpp` — which is a genuinely close *cousin* (PROGMEM
struct table + key column + linear scan + fail-closed) and which supplies the tree's mandated
PROGMEM-access convention and its one static-assert precedent. Copy its conventions; the
offset/width machinery is new.

---

## File Classification

| New/Modified file | Role | Data flow | Closest analog | Match quality |
|---|---|---|---|---|
| `firestarter/src/json_parser.c` — the field table + `store_field` | parser / decode table | transform (wire text → struct field) | `src/proms/eprom_params.cpp` (PROGMEM struct table, parallel key column, linear scan, fail-closed) | **partial** — role-match on "PROGMEM data table replacing dispatch", but no `offsetof`/`sizeof`/string-key precedent |
| `firestarter/src/json_parser.c` — deleting the eleven `get_*` stubs | parser | transform | the **five surviving sibling getters** in the same file (`get_r1`, `get_r2`, `get_rev`, `get_rw_pin`, `get_vpp_pin`) | **exact** — same file, identical helper idiom, and they are the phase's own proof case |
| `firestarter/src/json_parser.c` — `READ_TIMING_MAX_US` hoist + `clamp` column | config constant | transform | `get_read_settling` / `get_read_strobe` (the clamp logic being folded in) | **exact** |
| `firestarter/include/firestarter.h` — `protocol` u32→u8, `ctrl_flags` u32→u16 | model / struct | n/a | `include/eprom_params.h:52-58` `eprom_params_t` (largest-first field order + a `sizeof` static-assert, *because* AVR/host alignment differ) | **exact on the reasoning**, and load-bearing — see §4 |
| `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` — cases S1, S3–S5, DECODE-06 | test | request-response | itself (T1–T9 already in the file) | **exact** |
| the same file — case **S2** (dispatch fail-closes) | test | request-response | `test/native/avr/test_not_implemented/test_not_implemented.cpp` | **exact** — the only suite that asserts a *refusal* outcome with op-pointer checks |
| `.planning/v1.33/157-before-figures.md` / `157-after-figures.md` | record | n/a | `.planning/v1.33/156-before-figures.md` / `156-after-figures.md` | **exact** |
| `firestarter/include/json_parser.h` | header | n/a | — | **NO CHANGE NEEDED** — see §3 |

---

## 1. The crux — the PROGMEM data table

### 1a. Nearest real cousin: `src/proms/eprom_params.cpp` (ranked #1, partial)

This is the tree's one other "replace a dispatch selector with a data table" implementation, and
its authoring comments read like a specification for Phase 157. Verbatim, `src/proms/eprom_params.cpp:15-58`:

```c
/*
 * protocol_id is the sole lookup key: the accessor below is a
 * linear SCAN over the table, never a switch -- a switch here would be
 * exactly the second dispatch selector this table is designed not to have.
 */
#include "eprom_params.h"

/* Lookup key array, positionally parallel to EPROM_PARAMS below. */
static const uint8_t EPROM_PARAM_KEYS[] PROGMEM = { 0x07, 0x08, 0x0B };

static const eprom_params_t EPROM_PARAMS[] PROGMEM = {
    /* 0x07 PROTO_EPROM_28PIN */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x08 PROTO_EPROM_32PIN */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x0B PROTO_EPROM_24PIN */ { 75000UL, 50000UL, 255, 0, VERIFY_PER_PULSE,            VPP_PATH_DIRECT_VPE    },
};

const eprom_params_t* eprom_params_for(uint32_t protocol) {
    for (size_t i = 0; i < sizeof(EPROM_PARAM_KEYS) / sizeof(EPROM_PARAM_KEYS[0]); i++) {
        if ((uint32_t)pgm_read_byte(&EPROM_PARAM_KEYS[i]) == protocol) {
            return &EPROM_PARAMS[i];
        }
    }
    return NULL; /* Fail closed: a null pointer with zero hardware side effects, never &EPROM_PARAMS[0]. */
}
```

**Copy from it:** the row-comment style (each row prefixed with the key it serves), the
`sizeof(arr)/sizeof(arr[0])` loop bound, and — most important — the **fail-closed tail with a
named comment** rather than a default row.

**Where it does NOT match:** its key is a `uint8_t`, not a PROGMEM string; it returns a row pointer
instead of writing a field; and there is no offset/width column. It does not model `store_field`.

### 1b. The PROGMEM access convention — mandated, and it is per-column

Two conventions exist in the tree. The **production** one is per-column `pgm_read_*`, and
`include/eprom_params.h:73-76` states it as a contract:

```c
/*
 * Linear-scans the protocol_id-keyed table and returns a POINTER INTO
 * PROGMEM -- every field must be read back with pgm_read_byte /
 * pgm_read_dword, never dereferenced directly (a direct read compiles and
 * silently returns RAM garbage on AVR).
 */
```

`src/proms/eprom_budget.cpp:91-99` shows the enforced form:

```c
    /* Every PROGMEM column read individually with pgm_read_* -- never a
     * struct dereference, which compiles and silently returns RAM garbage
     * on AVR (eprom_params.h's own PROGMEM contract). verify_mode and
     * vpp_path are not read here -- neither one is part of the time
     * budget. */
    uint8_t  max_pulses         = pgm_read_byte(&row->max_pulses);
    uint8_t  overprogram_factor = pgm_read_byte(&row->overprogram_factor);
    uint32_t energy_cap_us      = pgm_read_dword(&row->energy_cap_us);
    uint32_t overprogram_cap_us = pgm_read_dword(&row->overprogram_cap_us);
```

`json_parser.c`'s own existing loop already uses this form (`json_parser.c:315,318`):

```c
            PGM_P key = (PGM_P)pgm_read_ptr(&key_parsers[j].key);
            if (jsoneq_(json, key_token, key) == 0) {
                bool (*parser_func)(const char*, jsmntok_t*, int, firestarter_handle_t*) = (void*)pgm_read_ptr(&key_parsers[j].parser_func);
```

So the new table's row must be read as
`pgm_read_ptr(&key_parsers[j].key)` / `pgm_read_byte(&key_parsers[j].offset)` /
`pgm_read_byte(&key_parsers[j].width)` / `pgm_read_word(&key_parsers[j].clamp)`.

The **whole-row `memcpy_P`** alternative exists only in test code
(`test/native/avr/test_frame_vectors/test_frame_vectors.cpp:209`:
`memcpy_P(&vec, &FRAME_VECTORS[i], sizeof(frame_vector_t));`) against
`include/frame_vectors.h:36` `static const frame_vector_t FRAME_VECTORS[] PROGMEM = {…}`. That is
a legitimate structural cousin for "PROGMEM array of structs", but it is **not** the production
convention and using it in `json_parser.c` would break the local pattern *and* copy a 6-byte row
into RAM per iteration.

### 1c. Other PROGMEM structural cousins, ranked

| Rank | Site | Why it is/isn't a model |
|---|---|---|
| 2 | `include/frame_vectors.h:27-51` — `frame_vector_t` + `FRAME_VECTORS[] PROGMEM` + `FRAME_VECTOR_COUNT` | closest *shape* match (array of structs in PROGMEM), but test-fixture-only and read with `memcpy_P` |
| 3 | `src/boards/rurp_serial_utils.cpp:359` — `static const uint8_t CRC8_TABLE[256] PROGMEM` | scalar lookup table, no struct, no key column |
| 4 | `src/boards/rurp_serial_utils.cpp:356` — `static const uint8_t MAGIC_PREAMBLE[4] PROGMEM` | scalar; cited at `src/hardware_operations.cpp:95` as a named "PROGMEM with no named symbol" exemption class — relevant only if the size gate flags the new table |

**Nothing in the tree is a model for a generic offset-driven setter.** State this in the plan.

---

## 2. The five zero-cost sibling getters and the helper machinery

These are the phase's **proof case** (identical logic, called with a literal key from a direct
`else if` chain, and absent from the `uno` symbol table — 0 B). Verbatim from `src/json_parser.c`:

```c
bool get_rw_pin(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("rw-pin", handle->bus_config.rw_line);
}

bool get_vpp_pin(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("vpp-pin", handle->bus_config.vpp_line);
}

bool get_r1(const char* json, jsmntok_t* tokens, int pos, rurp_configuration_t* config) {
    extract_long("r1", config->r1);
}

bool get_r2(const char* json, jsmntok_t* tokens, int pos, rurp_configuration_t* config) {
    extract_long("r2", config->r2);
}

bool get_rev(const char* json, jsmntok_t* tokens, int pos, rurp_configuration_t* config) {
    extract_int("rev", config->hardware_revision);
}
```

**Exact current helper signatures** — `store_field` must be written in this idiom:

```c
static unsigned long simple_strtoul(const char* s) {
    unsigned long val = 0;
    // Note: This simple implementation only handles positive decimal numbers.
    while (*s >= '0' && *s <= '9') {
        val = val * 10 + (*s - '0');
        s++;
    }
    return val;
}

#define jsoneq(json, tok, s) \
    jsoneq_(json, tok, PSTR(s))
```

```c
static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
    if (tok->type == JSMN_STRING && (int)strlen_P(s) == tok->end - tok->start &&
        strncmp_P(json + tok->start, s, tok->end - tok->start) == 0) {
        return 0;
    }
    return -1;
}

#define extract_num(element, register, type)           \
    if (jsoneq(json, &tokens[pos], element) == 0) {    \
        register = type(json + tokens[pos + 1].start); \
        return 1;                                      \
    }                                                  \
    return 0;

#define extract_long(element, register) \
    extract_num(element, register, simple_strtoul)

#define extract_int(element, register) extract_long(element, register)
```

Note for the plan: `extract_int` is a **bare alias** of `extract_long` — confirming correction C-6
that `pins`/`chip_id`/`vpp_mv`/`page_size` already truncate `simple_strtoul`'s `unsigned long`
silently today. `store_field` is the first bound check `json_parser.c` will ever have.

`get_flags` is the one stub that must **survive** (two direct call sites in two different
functions — `json_parse_config` and `json_get_cmd`, per C-1):

```c
bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("flags", handle->ctrl_flags);
}
```

### The clamp logic being folded into the table's `clamp` column

Verbatim — including the comment block the plan should preserve and hoist with the `#define`:

```c
/*
 * Read-timing sweep knobs.
 *
 * Both knobs are clamped to READ_TIMING_MAX_US at parse time so
 * an absurd JSON value cannot pass an unbounded value to delayMicroseconds()
 * in the read loop.  Values < 3µs are below delayMicroseconds() accuracy on
 * 16 MHz AVR — documented by the caller in memory_get_data().
 *
 * Zero-ambiguity:
 *   read_settling_us == 0 → no settling delay (explicit test point)
 *   read_strobe_us   == 0 → use firmware default 3µs (preserves current behaviour)
 */
#define READ_TIMING_MAX_US 1000UL   /* T-44-01 sane max (~1ms); caps both knobs */

bool get_read_settling(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    if (jsoneq(json, &tokens[pos], "read-settling-delay") == 0) {
        unsigned long v = simple_strtoul(json + tokens[pos + 1].start);
        handle->read_settling_us = (uint32_t)(v > READ_TIMING_MAX_US ? READ_TIMING_MAX_US : v);
        return 1;
    }
    return 0;
}
```

`get_read_strobe` is the same body against `"read-strobe-us"` / `handle->read_strobe_us`.
`get_page_size` carries a comment explicitly justifying the *non*-clamp form ("validation …
lives in the 0x0D handler (eeprom28c_page_mask)") — that comment becomes **stale** once
`store_field` saturates `page_size`; the plan must update or retire it, not leave it contradicting
the new code.

### The current table + dispatch loop (to be replaced)

```c
typedef struct {
    PGM_P key;
    bool (*parser_func)(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
} key_parser_t;

static const key_parser_t key_parsers[] PROGMEM = {
    {key_mem_size, get_memory_size}, {key_address, get_address},         {key_flags, get_flags},
    {key_chip_id, get_chip_id},      {key_pin_count, get_pin_count},     {key_pulse_delay, get_delay},
    {key_vpp_mv, get_vpp_mv},        {key_algorithm, get_algorithm},
    /* Read-timing sweep knobs. */
    {key_read_settling, get_read_settling},                              {key_read_strobe, get_read_strobe},
    /* Page-size seam. */
    {key_page_size, get_page_size},
};
```

**OD-2 shape constraint, restated concretely.** The host gate's regex is
`key_parsers\s*\[\s*\]\s*PROGMEM\s*=\s*\{(?P<body>.*?)\};`
(`firestarter_app/tests/test_json_key_parity.py:114`) and it harvests the `key_*` identifiers from
the body. So the new table must keep: the identifier `key_parsers`, the literal
`[] PROGMEM = {` … `};` form, and the `key_*` identifier as the **first** member of each row. The
row *type* name (`key_parser_t` → e.g. `field_desc_t`) is free.

---

## 3. `include/json_parser.h` — NO EDIT REQUIRED (verified)

The eleven `get_*` symbols are **not** declared in the public header. They are file-local forward
declarations at the top of `src/json_parser.c`:

```c
bool get_flags(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_memory_size(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
bool get_address(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
… (eleven in all, plus get_rw_pin / get_vpp_pin / get_r1 / get_r2 / get_rev)
```

`include/json_parser.h` exports exactly three functions and one constant:

```c
#define NUMBER_JSNM_TOKENS 64

    uint8_t json_get_cmd(const char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle);
    int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle);
    int json_parse_config(const char* json, jsmntok_t* tokens, int token_count, rurp_configuration_t* config, firestarter_handle_t* handle);
```

**Consequence:** deleting the ten stubs touches the forward-declaration block in `json_parser.c`
only. `include/json_parser.h` stays byte-identical, and the whole 27-line header needs no review.
The research listed this file as "possibly touched"; it is **not**.

---

## 4. `include/firestarter.h` — the narrowing, and the alignment precedent

Current struct head (`include/firestarter.h:205-227`):

```c
typedef struct firestarter_handle {
    uint8_t cmd;
    uint8_t operation_state;
    uint8_t response_code;
    uint32_t protocol;
    uint8_t pins;
    uint32_t mem_size;
    uint32_t address;
    uint16_t vpp_mv;
    uint32_t pulse_delay;
    uint32_t read_settling_us;   /* address-settling delay before /CE assert (µs; 0 = no settling delay) */
    uint32_t read_strobe_us;     /* /CE read-strobe pulse width (µs; 0 = use default 3µs) */
    uint32_t ctrl_flags;
    uint16_t chip_id;
    uint16_t page_size;          /* … Reset per command in json_parse, exactly like chip_id above (D-05). */
    char data_buffer[DATA_BUFFER_SIZE];
```

**Analog for the reasoning — `include/eprom_params.h:52-67`, and it is directly load-bearing:**

```c
/* Six columns, largest-first (see (b) above). No pulse-width field of any
 * name exists here (TABLE-02) … */
typedef struct {
    uint32_t overprogram_cap_us;  /* … */
    uint32_t energy_cap_us;       /* … */
    uint8_t  max_pulses;          /* … */
    uint8_t  overprogram_factor;  /* … */
    uint8_t  verify_mode;         /* … */
    uint8_t  vpp_path;            /* … */
} eprom_params_t;

/* Compile-time sizeof check only -- NOT the rejected __attribute__((used)) / force-the-table-into-the-image pattern (D-10); do not delete this thinking it is one. */
#ifdef __cplusplus
static_assert(sizeof(eprom_params_t) == 12,
              "sizeof(eprom_params_t) must be 12 on every target -- Pitfall 2: "
              "field order is largest-first because avr-gcc gives every type "
              "1-byte alignment while a 64-bit host does not.");
#endif
```

**Why this matters to Phase 157, concretely.** The research's measured `FIELDS` size of **66 B =
11 × 6 B** is an AVR-only fact: the proposed row `{PGM_P key; uint8_t offset; uint8_t width;
uint16_t clamp;}` is 6 B on AVR (2-byte pointer, 1-byte alignment) but **16 B on x86-64** (8-byte
pointer + padding). `eprom_params.h`'s comment is the tree's own written warning about exactly this
trap, and its largest-first ordering rule is the fix. The plan should order the new row
largest-first (`key` first is already both largest *and* required by the host gate — convenient)
and **must not** author a `sizeof(row) == 6` assertion without a target guard.

---

## 5. The compile-time assertion — no C precedent, and the portable fallback

| Question | Answer, measured |
|---|---|
| Existing `_Static_assert` in C anywhere? | **No.** Zero occurrences in `src/ include/ lib/ test/`. |
| Existing `static_assert`? | One, `include/eprom_params.h:62`, wrapped in `#ifdef __cplusplus` — i.e. it is **inert in every C TU**, including `json_parser.c`. |
| Existing negative-array (`char[1-2*!(cond)]`) idiom? | **No.** Zero occurrences. |
| What C standard does the build actually pass? | **No `-std=` reaches any AVR C compilation.** `[env]` `build_flags` (`platformio.ini:21-28`) carry only `-D MONITOR_SPEED=…`, `-D HARDWARE_REVISION`, `-D DEV_TOOLS`; `[env:uno]`, `[env:uno328pb]`, `[env:leonardo]` add `${env.build_flags}` plus `-D RURP_BOARD_NAME=…` / `-D SERIAL_ON_IO`. So `.c` files compile at avr-gcc 7.3.0's **default, `gnu11`** → `_Static_assert` is available (C11, and gcc has had it since 4.6). The only `-std=` in the file is `-std=gnu++17` on `[env:native]` (`platformio.ini:266-269`) and the derived native envs, which PlatformIO routes to `CXXFLAGS`. |

**Comparable compile-time invariant already enforced in the tree:** only the one at
`eprom_params.h:62`, and it is C++-only. So `_Static_assert` in `json_parser.c` establishes a **new
idiom for this repo** — the plan must say so explicitly and name the fallback rather than assume
one exists.

**Recommended fallback, for the per-row form C-14 asks for.** `_Static_assert` cannot appear inside
an initializer expression, so the eleven-field guard needs either (a) eleven file-scope
`_Static_assert(offsetof(firestarter_handle_t, m) < 256, "…")` lines emitted by a second macro pass
over the same field list, or (b) the negative-array trick folded into `FIELD()`:

```c
+ 0 * sizeof(char[1 - 2 * (offsetof(firestarter_handle_t, member) > 255)])
```

(b) works pre-C11 and inside an initializer; it has **no precedent in this tree**, so it needs a
comment explaining what it is or a future reader will delete it — precisely the failure mode
`eprom_params.h:60`'s "do not delete this thinking it is one" comment exists to prevent. **Copy
that comment's spirit verbatim.**

---

## 6. Test file patterns

### 6a. The file being extended — `test/native/avr/test_read_timing/test_read_timing_params.cpp`

`setUp` (`:40-49`), already stubbing `Serial.write`/`flush` so a `LOG_ERROR_ID_*` on the refusal
path cannot abort:

```cpp
void setUp(void) {
    ArduinoFakeReset();
    /* Stub Serial.write and Serial.flush so LOG_ERROR_ID_* calls in any
     * transitive parse path don't abort. Tests never assert on serial. */
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t)))
        .AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}

void tearDown(void) {}
```

`make_handle` + `parse_json` (`:53-75`) — the exact harness S1–S5 must use:

```cpp
/* Build a zero-initialized handle suitable for JSON parse tests. */
static firestarter_handle_t make_handle(uint8_t cmd) {
    firestarter_handle_t h = {};   /* zero-init: ensures new fields default 0 */
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

static int parse_json(const char* json_str, firestarter_handle_t* handle) {
    jsmntok_t tokens[NUMBER_JSNM_TOKENS];
    jsmn_parser parser;
    jsmn_init(&parser);
    int token_count = jsmn_parse(&parser, json_str, strlen(json_str),
                                 tokens, NUMBER_JSNM_TOKENS);
    if (token_count < 0) return token_count;
    return json_parse(json_str, tokens, token_count, handle);
}
```

The existing clamp assertion (`:105-116`) — the `<=` that DECODE-06 tightens to `==`:

```cpp
/* T4: value above cap → read_settling_us clamped to READ_TIMING_MAX_US
 * (T-44-01 mitigation: an absurd JSON value cannot hang the read loop). */
void test_read_settling_us_capped_at_max(void) {
    /* Use a value well above 1000µs to confirm the cap fires */
    const char* json = "{\"cmd\":1,\"read-settling-delay\":9999}";
    firestarter_handle_t h = make_handle(CMD_READ);
    int rc = parse_json(json, &h);
    TEST_ASSERT_EQUAL_INT(0, rc);
    /* After cap: handle.read_settling_us must not exceed READ_TIMING_MAX_US */
    TEST_ASSERT_TRUE_MESSAGE(h.read_settling_us <= READ_TIMING_MAX_US,
                             "read_settling_us must be capped at READ_TIMING_MAX_US");
}
```

The best in-file model for a **non-vacuous, message-bearing** assertion (copy this style for S1/S4,
not the bare `TEST_ASSERT_TRUE` above) is T7 at `:142-156`:

```cpp
    TEST_ASSERT_EQUAL_UINT16_MESSAGE(0, h.page_size,
        "a stale 128 surviving into the next, page-size-absent command "
        "makes \"absent means 64\" false in practice -- the exact page "
        "overrun PGSZ-02 exists to prevent");
```

The `main()` / `RUN_TEST` block (`:181-195`) — nine entries today, appended in declaration order:

```cpp
int main(int argc, char** argv) {
    (void)argc;
    (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_read_settling_us_parsed_from_json);
    RUN_TEST(test_read_strobe_us_parsed_from_json);
    RUN_TEST(test_read_timing_fields_default_zero_when_absent);
    RUN_TEST(test_read_settling_us_capped_at_max);
    RUN_TEST(test_page_size_parsed_from_json);
    RUN_TEST(test_page_size_defaults_zero_when_absent);
    RUN_TEST(test_page_size_resets_between_two_parses_on_the_same_handle);
    RUN_TEST(test_unknown_key_before_a_known_key_does_not_desync_the_token_walk);
    RUN_TEST(test_unknown_key_before_page_size_does_not_desync_the_token_walk);
    return UNITY_END();
}
```

The file's local duplicate constant (`:36-38`), the drift risk C-8 names:

```cpp
/* Maximum allowed value for read-timing knobs (T-44-01 / RESEARCH §Security
 * Domain). Mirrors the cap defined in memory.cpp / json_parser.c. */
#define READ_TIMING_MAX_US 1000UL
```

⚠ **`configure_memory` is not currently reachable from this file's includes.** The suite includes
`json_parser.h`, `jsmn.h` and `firestarter.h` only (`:24-32`). Case S2 must add
`extern "C" { #include "memory.h" }` — the include form both dispatch suites use (see 6b). The TU
*links* (both suites are in the same `[env:native]` `build_src_filter = … +<proms/> …`), so this is
an include line, not a `platformio.ini` change.

### 6b. The dispatch-outcome analog for case S2 — `test/native/avr/test_not_implemented/test_not_implemented.cpp`

This is the **only** suite in the tree that asserts a *refusal* by both response code and op
pointers, and it is exactly what S2 needs. Header comment (`:6-14`) — it also documents *why* the
pointer assertions are safe here and not in its sibling:

```cpp
/*
 * dispatch unit tests for configure_not_implemented() and
 * fail-closed dispatch arms.
 *
 * Tests assert RESPONSE_CODE_ERROR and all-three-NULL op pointers (unlike
 * the sibling test_configure_memory.cpp which avoids pointer checks because
 * configure_sram() is a stub with NULL firestarter_operation_init).
 * The not-implemented handler is self-contained and always leaves all
 * three pointers NULL — pointer assertions are safe here.
 */
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"
```

The case shape (`:52-59`) — **the idiom S2 must copy**:

```cpp
void test_protocol_0x11_fwh_not_implemented(void) {
    firestarter_handle_t h = make_handle(0x11, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_NULL(h.firestarter_operation_init);
    TEST_ASSERT_NULL(h.firestarter_operation_main);
    TEST_ASSERT_NULL(h.firestarter_operation_end);
}
```

**So S2's assertion is `TEST_ASSERT_NULL(h.firestarter_operation_main)`, not "is not
`flash_5v_page`'s".** The tree has no idiom for comparing against a named handler's function
pointer, and `configure_flash_5v_page`'s symbol is not exported to tests. Asserting
`RESPONSE_CODE_ERROR` + all-three-NULL is stronger, matches local precedent, and directly proves
the fail-closed tail was reached. Use it.

### 6c. The non-regression analog for case S3 — `test/native/avr/test_dispatch/test_configure_memory.cpp`

Its header comment (`:19-22`) is the authority on **why not to assert an operation pointer for a
success case**:

```cpp
/*
 * Why TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, ...) and not an operation-
 * pointer check? `configure_sram()` is a stub today and leaves the
 * firestarter_operation_init pointer NULL — pointer-set assertions would
 * spuriously fail. response_code is the robust dispatch-success signal.
 */
```

The case shape S3 should copy (`:73-77`):

```cpp
void test_protocol_0x05_dispatches_5v_page(void) {
    firestarter_handle_t h = make_handle(0x05, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}
```

⚠ **Narrowing hazard in both dispatch suites.** Both declare
`static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd)` and
assign `h.protocol = protocol;` (`test_configure_memory.cpp:56-63`,
`test_not_implemented.cpp:42-48`). After `protocol` becomes `uint8_t` this is an implicit narrowing
conversion in C++. No `-Wconversion` / `-Wnarrowing` / `-Werror` appears in any `build_flags`, so it
should compile silently — but the native warnings watermark is at zero headroom (project memory),
so **run `scripts/check_build_warnings.py` and do not assume**. If it warns, the fix is to narrow
the parameter to `uint8_t` in both files (both are already only ever called with values ≤ 0x39).

---

## 7. `is_flag_set` / protocol call-site shapes — narrowing surfaces

**Definition** (`include/firestarter.h:191-192`) — a macro that captures `handle` from the
enclosing scope, so **no call site names a type**:

```c
#define is_flag_set(flag) \
    ((handle->ctrl_flags & flag) == flag)
```

Representative call sites (all in `src/`, 40 textual uses per C-5):

```c
src/proms/eprom.cpp:52     if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
src/proms/eprom.cpp:150    if (is_flag_set(FLAG_CAN_ERASE)) {
src/proms/eprom.cpp:294    if (is_flag_set(FLAG_VPE_AS_VPP)) {
```

**Varargs / logging exposure — checked, and it is CLEAN:**

| Surface | Finding |
|---|---|
| `ctrl_flags` in a log payload | Never. The only logging that touches flags passes the macro's **`bool` result**, not the field: `src/firestarter.cpp:99-111`, e.g. `LOG_DEBUG_ID_SUB_U8(DBG_FLAG_FORCE, is_flag_set(FLAG_FORCE));` — seven such lines. Narrowing `ctrl_flags` cannot change the emitted byte. |
| `protocol` in a log payload | Two sites, **both already explicitly cast**: `src/proms/not_implemented.cpp:17` and `src/proms/eprom.cpp:87`, both `LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol);`. The cast makes the narrowing a no-op at both. |
| printf-style format strings | **None.** The project's logging is id-and-typed-params (`LOG_*_ID_U8/U16/U24/U32`), so there is no format specifier to desync. |
| `sizeof` on either field in a wire or EEPROM layout | **None.** Verified by grep; neither field appears in a `sizeof` expression. |
| `rurp_configuration_t` (the EEPROM-persisted struct) | Contains `r1`, `r2`, `hardware_revision` — **neither `protocol` nor `ctrl_flags`**. Not EEPROM-visible. |
| `uint32_t` parameter surfaces | `src/firestarter.cpp:242` `eprom_block_budget_s(handle->protocol, …)` and `src/proms/eprom.cpp:85,297,341` `eprom_params_for(handle->protocol)` keep `uint32_t` parameters; `uint8_t` promotes. `src/proms/eprom_params.cpp:53` compares `(uint32_t)pgm_read_byte(...) == protocol`, unaffected. |
| Protocol comparison shape (17 sites on 9 lines, `src/proms/memory.cpp:99-133`) | All against unsigned constants ≤ 0x39, e.g. `if (handle->protocol == PROTO_FLASH_5V_PAGE \|\| handle->protocol == PROTO_PHANTOM_0x35 \|\| …)`. `uint8_t` promotes to `int`; truth values identical. Plus one `switch (handle->protocol)` at `src/proms/eprom.cpp:70`. |

**Conclusion for the planner:** the classic varargs-narrowing break does **not** exist here. The
only real risk found is the `make_handle(uint32_t protocol, …)` test-side narrowing in §6c.

---

## 8. The before/after figures ledger — format to match

**Precedent files:** `.planning/v1.33/156-before-figures.md`, `156-after-figures.md` (immediate),
`155-before-figures.md`, `155-after-figures.md`.

**Frontmatter shape (copy verbatim structure)** — from `156-before-figures.md:1-15`:

```yaml
---
title: Before-figures record — milestone v1.33, Phase 156 (…)
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "01"
measured: 2026-08-23
status: AUTHORITATIVE — this file is the ONLY source for Phase 156's before-half figures. …
supersedes: >
  ROADMAP.md Phase 156 criteria 1 (…) and 4 (…);
  REQUIREMENTS.md DEDUP-01 (…) prose, wherever they state a figure this file corrects. …
requirements: [DEDUP-01, DEDUP-02, DEDUP-03, DEDUP-04]
---
```

Note `phase:` is **truncated to 62 chars** in 156's frontmatter. For 157 that is
`157-command-decode-table-handle-type-narrowing-firmware-only`. `requirements:` becomes
`[DECODE-01 … DECODE-07]`.

**Section skeleton — `157-before-figures.md`** (mirroring 156-before's 10 + summary):

| # | 156-before heading | 157 equivalent |
|---|---|---|
| 1 | Git anchors | same — `FW_PRE_SHA` full+abbrev, branch, porcelain asserted **before AND after**, meta HEAD, `worktree list`, plus the `firestarter_app` gitlink drift note (copy it — it is still true) |
| 2 | AVR image figures, WARM | same — 3 targets × flash/RAM/total, **explicitly labelled WARM**, plus Leonardo Caterina headroom vs 28672 |
| 3 | Per-symbol ledger, `uno` | the eleven-stub ledger (1012 B total, 84–110 B range) + `key_parsers` 44 B + the five siblings' **absence** |
| 4 | `__udivmodhi4` call sites | → **the string-duplication ledger** (the two 118 B vaddr blocks, offset-resolved) |
| 5 | Test and gate baselines, on the clean committed tree | same — both native envs' case counts, host `pytest tests/`, warnings, both `check_size_baseline` modes |
| 6 | The golden's arrival state | → **struct offsets, both architectures** (the `offsetof`-probe table) |
| 7 | Reference carriers | same — the patch subset + `wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8`, and C-11's non-applicability |
| 8 | The one-sided size gate, and the pre-existing red | same, verbatim intent (D-03) |
| 9 | The honest coverage ceilings — stated, not implied | same — at minimum: −5 B RAM is **AVR-only** (`sizeof` is 655 both before and after on native); the `flags` duplicate vanishing is **measured-but-unexplained**; every figure is WARM |
| 10 | The corrections index | C-1 … C-16, each `C-N | claim | measured | superseded document` |
| — | Summary of what this record proves | same |

**Section skeleton — `157-after-figures.md`** (mirroring 156-after's 10 + self-verification):
git anchors → the phase ledger (before vs after, per target) → the mechanical criteria →
**the gate ledger, all legs** → per-requirement evidence tables → the coverage ceilings, final
form → **the corrections ledger, every row closed out** → handoffs → self-verification.

Two 157-specific sections the 156 skeleton has no slot for, both of which the plan must add:
- **DECODE-07's record-only section** (the rejected `switch`, its measurement or its explicit
  `[UNVERIFIED at this position]` label with the survey as provenance).
- **The 999.35 / v1.28 non-additivity warning** — a reader of `157-after-figures.md` will not
  reach the backlog entry that carries it.

**Correction numbering convention:** `C-N` where N is sequential per phase, each stated as a `###`
heading in the phase's RESEARCH and then **closed out** as a row in the after-record's corrections
ledger. 155 additionally used `OQ-N` for open questions carried between the before- and
after-records; 157's RESEARCH already opens `OQ-1` (the 600 vs 601 B handle-size discrepancy), so
carry that convention too.

**Handoff obligations the record must carry** (LAND-01 / Phase 158 depends on them): the new native
case count (172 → N) for both `native` and `native_nodevtools`, and the WARM-vs-cold status of every
figure.

---

## Shared Patterns

### Fail-closed refusal with a named comment
**Source:** `src/proms/eprom_params.cpp:57`
**Apply to:** `store_field`'s out-of-range branch, and the S1/S2/S4 test comments.
```c
    return NULL; /* Fail closed: a null pointer with zero hardware side effects, never &EPROM_PARAMS[0]. */
```
The tree's convention is that a refusal carries an inline comment naming *what it refuses* and
*what it deliberately does not do instead*. `store_field`'s mask-vs-saturate split (OD-1) must be
commented in exactly this register — especially the `ctrl_flags` MASK row, whose whole reason for
existing is that the obvious alternative is fail-open.

### The "do not delete this thinking it is X" guard comment
**Source:** `include/eprom_params.h:60`
**Apply to:** the `_Static_assert` block (or the negative-array trick, which needs it more).
```c
/* Compile-time sizeof check only -- NOT the rejected __attribute__((used)) / force-the-table-into-the-image pattern (D-10); do not delete this thinking it is one. */
```

### Serial-stub `setUp` for any suite whose path can log
**Source:** `test_read_timing_params.cpp:48-57`, identically at `test_not_implemented.cpp:27-34`
and `test_configure_memory.cpp:37-47`.
**Apply to:** any new native case. Already present in the file being extended — no action, but do
not remove it: S2's refusal path emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`.

### Per-column PROGMEM reads, never a struct dereference
**Source:** `include/eprom_params.h:73-76` (the contract), `src/proms/eprom_budget.cpp:91-99` (the
enforcement), `src/json_parser.c:315,318` (already in the file).
**Apply to:** the new `key_parsers[]` row reads.

### Non-vacuous, message-bearing Unity assertions
**Source:** `test_read_timing_params.cpp:181-189` (T7), `test_not_implemented.cpp:52-59`.
**Apply to:** all five new DECODE-05 cases and the DECODE-06 tightenings. Prefer
`TEST_ASSERT_EQUAL_*_MESSAGE` with a message that states the defect the case exists to catch —
this is the local house style and it is what makes the RED-first anti-tautology check legible.

---

## No Analog Found

| Item | Role | Data flow | Reason |
|---|---|---|---|
| `store_field` — a generic `offsetof`/`width`-driven struct setter | utility | transform | **`offsetof` appears nowhere in the tree.** No file writes a struct member through a computed offset. Design decision, not a copy. Nearest cousin in *spirit* is `mem_util_*` in `src/proms/memory.cpp`, but it writes named fields. |
| `sizeof(((firestarter_handle_t*)0)->member)` width derivation | utility | transform | **Zero occurrences of the null-pointer-cast `sizeof` idiom.** New. |
| `_Static_assert` in a C TU | config / invariant | n/a | **Zero occurrences.** The one `static_assert` is C++-guarded (`eprom_params.h:62`) and therefore inert in `json_parser.c`. New idiom — needs the fallback named in §5. |
| A PROGMEM row containing a `PGM_P` **plus** integer columns | model | transform | `key_parsers[]` itself is the only PROGMEM struct with a string member, and it is what is being replaced. The mixed-width alignment trap this creates has a written precedent (`eprom_params.h:52-67`) but no implementation to copy. |
| Asserting "the selected operation is *not* handler X" | test | request-response | No suite compares against a named handler's function pointer. Use `test_not_implemented.cpp`'s all-three-NULL + `RESPONSE_CODE_ERROR` form instead (§6b) — it is strictly stronger and it is local convention. |

---

## Metadata

**Analog search scope:** `firestarter/src/`, `firestarter/include/`, `firestarter/lib/`,
`firestarter/test/native/avr/` (all 17+ suites listed by `grep -rln`), `firestarter/platformio.ini`,
`.planning/v1.33/`.
**Read-only:** no source file was modified by this mapping. `git -C firestarter status --porcelain`
was not disturbed.
**Pattern extraction date:** 2026-08-23, firmware `1151dc4`.
**Citation warning, restated:** every `file:LINE` above is measured against the current
(post-Phase-154) tree and will be remapped by Phase 159. Phase 157's own two new `#include` lines
shift `src/json_parser.c` by +2 on first edit — prefer symbol names over line numbers in the plan.
