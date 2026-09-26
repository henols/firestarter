# Phase 156: Duplicated-Report Extraction + Boolean-Convention Repair (firmware-only) — Pattern Map

**Mapped:** 2026-08-23
**Files analyzed:** 13 (10 modified, 1 created, 2 optional-new)
**Analogs found:** 13 / 13 — every file this phase touches has a concrete in-tree analog. Nothing here needs an invented shape.
**Repo scope:** every path below is relative to `/workspaces/firestarter` (firmware sub-repo) unless prefixed `.planning/`. Firmware HEAD verified `adf1a31`, branch `gsd/v1.33-source-hygiene-firmware-size-reduction`. All reads were non-mutating; no source file was edited.

---

## ⚠ Headline finding — open question A4 is RESOLVED, and the answer is better than the research feared

VALIDATION.md calls the id-capture facility "the plan's biggest shape risk". **It is not a risk. `test_eeprom28c_sdp` already has one**, and it is *not* `count_logged_id` in a `host_stubs.cpp` — it is a suite-local Serial-frame walker in the test TU itself:

| Suite | Env | id-capture facility | Where | Mechanism |
|---|---|---|---|---|
| `test_vpp_eprom_v131` | `native_loop_v131` (not CI) | `logged_id_count/at/param_count` + `count_logged_id` / `find_logged_id` | `host_stubs.cpp:271-322` (recorder) + `test_vpp_eprom_v131.cpp:348-362` (helpers) | **strong `rurp_log_id` override** of the `__attribute__((weak))` default at `src/boards/rurp_serial_utils.cpp:480` |
| `test_eeprom28c_sdp` | `native` (**CI**) | `captured_frames` + `sdp_captured_frame_ids()` + `sdp_ids_contains()` (+ `sdp_decode_u32_param_for_id()`) | `test_eeprom28c_sdp.cpp:182-232`, cleared in `setUp` at `:303`, fed by the `Serial.write(uint8_t)` `AlwaysDo` hook at `:259-263` | **decodes the real wire frame** emitted by the real `rurp_log_id` |
| `test_sdp_harness` | `native` (**CI**) | **NONE.** `Serial.write` is `.AlwaysReturn(1)` at `test_sdp_harness.cpp:82-83` — bytes are discarded | — | — |

**Consequences the planner must take:**

1. **Blind spot 2 (chip-ID message id) closes in `test_eeprom28c_sdp` with ZERO new infrastructure.** Add two `sdp_ids_contains` assertions to `test_case7_mismatching_chip_id_with_force_warns` (`:792-806`). No `host_stubs.cpp` edit, no new case, `cases` stays 172.
2. **`test_sdp_harness::test_migrated_mismatching_chip_id_errors` (`:607`) cannot assert an id today.** Two options, both mechanical: (a) **recommended** — put *both* directions of the id assertion in `test_eeprom28c_sdp` instead (Case 7 gives the WARN direction under `FLAG_FORCE`; a non-force twin is already implied by the suite's `make_identity_handle(0x1F08, 0)` idiom), leaving `test_sdp_harness` untouched; or (b) port the ~55 lines of `captured_frames` + `sdp_captured_frame_ids` + `sdp_ids_contains` + the `AlwaysDo` hook from `test_eeprom28c_sdp.cpp:182-232,259-263,303` into `test_sdp_harness`, which is a real edit to an always-green suite for one assertion. **Take (a).**
3. **Do NOT add a `rurp_log_id` strong override to `test_eeprom28c_sdp/host_stubs.cpp`.** That suite links `src/boards/rurp_serial_utils.cpp` (its `build_src_filter` at `platformio.ini:205`) and *relies* on the real emitter producing real frames for `sdp_assert_stream_equals` / the `RED-BASELINE.md` blob-SHA record. A strong override would silence the whole frame stream and could turn other cases vacuous. The two suites use two different, both-legitimate mechanisms; **match the mechanism the suite already has, never import the other one.**

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/proms/memory.cpp` (+2 helpers) | firmware service (shared memory-utility layer) | transform + emit | `mem_util_split_delay` / `mem_util_delay_us` at `src/proms/memory.cpp:305-324` — same file, same `mem_util_*` family, same "small pure helper hoisted out of duplicated call sites" motive | **exact** |
| `include/memory_utils.h` (+2 decls) | header / contract | declaration only | `memory_verify_execute` decl at `include/memory_utils.h:29` (a decl added *specifically* to de-duplicate a byte-identical copy — this phase's exact motive) | **exact** |
| `src/proms/eprom.cpp` (2 VPP + 1 chip-ID block) | protocol handler | request-response | `src/proms/flash_intel.cpp` twin blocks; and `eprom.cpp:481-510`'s own precedent of replacing a byte-identical fork with a shared call | **exact** |
| `src/proms/flash_intel.cpp` (2 VPP + 1 chip-ID block) | protocol handler | request-response | `src/proms/eprom.cpp` twin blocks | **exact** |
| `src/proms/flash_utils.cpp` (1 chip-ID block + 1 `#include`) | protocol utility | request-response | `src/proms/flash_intel.cpp:14` (already has `#include "memory_utils.h"`) | **exact** |
| `src/proms/eeprom_28c.cpp` (1 chip-ID block, redundant casts) | protocol handler | request-response | `src/proms/flash_utils.cpp:104` (the cast-free twin) | **exact** |
| `src/eprom_operations.cpp` (9 `!` dropped, 3 comment lines) | command wrapper layer | event-driven (loop polarity) | the file's own 9 sites are each other's analog; `eprom_erase:37` / `eprom_check_chip_id:46` are the **do-not-touch** analogs | **exact** |
| `src/operation_utils.cpp` (6 returns) | op engine | state machine (INIT→MAIN→END) | no analog needed — the 6 sites are enumerated verbatim in RESEARCH §DEDUP-04 | **exact (research-supplied)** |
| `include/operation_utils.h:71,85` (2 `@return` docs) | header / contract | doc | each other | **exact** |
| `test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` (new under-voltage cases) | native test | behavioural | `test_vpp04_a` (`:630-651`) + `test_vpp04_d` (`:740-756`) in the same file | **exact** |
| `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (Case 7 strengthened; Case 24 flipped; Case 25 de-vacuumed) | native test | behavioural | Case 11's anti-hollow control at `:966-982`; Case 24's own existing `sdp_ids_contains` legs at `:1433-1439` | **exact** |
| `tests/golden/protocol_branch_inventory.json` + `tests/test_protocol_branch_inventory.py` | committed golden + pytest gate | source contract | itself — four prior re-derivations documented in its own `meta.recorded_by` | **exact** |
| *(optional)* `tests/test_boolean_convention_source_contract_v133.py` | pytest gate | source contract | `tests/test_write_path_source_contract_v131.py` | **exact** |
| *(Wave 0)* `.planning/v1.33/156-before-figures.md` | planning record | measurement | `.planning/v1.33/155-before-figures.md` | **exact** |

---

## Pattern Assignments

### `src/proms/memory.cpp` — the two new helpers (service, transform + emit)

**Primary analog — house style for a small `mem_util_*` helper** (`src/proms/memory.cpp:305-324`, read verbatim):

```c
void mem_util_split_delay(uint32_t us, uint32_t* out_ms, uint16_t* out_us) {
    if (us <= MEM_UTIL_DELAY_US_MAX) {
        *out_ms = 0;
        *out_us = (uint16_t)us;  // <= 16383, fits and is accurate
        return;
    }
    *out_ms = us / 1000UL;
    *out_us = (uint16_t)(us % 1000UL);  // <= 999, always under the ceiling
}
```

House conventions this establishes and the new helpers must match: `void` return; `firestarter_handle_t* handle` first where a handle is needed; explicit-width fixed types everywhere; an early `return` for the trivial case; trailing `//` comments that justify a width/bound claim; no `static` (declared in `include/memory_utils.h`).

**Reference implementation — take VERBATIM from the preserved ref.** `git show wip/v1.33-size-reduction-survey-preserved:src/proms/memory.cpp`, the +46-line block inserted immediately after `mem_util_calculate_top_address_register` and immediately before `mem_util_split_delay`:

```c
/* Shared VPP-mismatch report (payload unchanged):
 *   [measured_V u16 BE][measured_tenths u16 BE][expected_V u16 BE][expected_tenths u16 BE]
 * Four byte-identical copies existed -- eprom.cpp x2, flash_intel.cpp x2 --
 * holding 24 of the firmware's 30 __udivmodhi4 call sites between them.
 * Arithmetic preserved EXACTLY, so this is de-duplication, not a behaviour
 * change. Severity rides entirely in msg_id, because every
 * LOG_{WARN,ERROR}_ID_BYTES macro is the same alias of LOG_ID_BYTES. */
void mem_util_report_voltage(firestarter_handle_t* handle, uint16_t measured_mv,
                             uint16_t expected_mv, uint8_t msg_id, uint8_t response_code) {
    uint16_t _v0 = (uint16_t)((measured_mv + 50) / 1000);
    uint16_t _v1 = (uint16_t)((((measured_mv + 50) / 100) % 10));
    uint16_t _v2 = (uint16_t)((expected_mv + 50) / 1000);
    uint16_t _v3 = (uint16_t)((((expected_mv + 50) / 100) % 10));
    uint8_t _b[8];
    _b[0] = (uint8_t)((_v0 >> 8) & 0xFF);
    _b[1] = (uint8_t)(_v0 & 0xFF);
    _b[2] = (uint8_t)((_v1 >> 8) & 0xFF);
    _b[3] = (uint8_t)(_v1 & 0xFF);
    _b[4] = (uint8_t)((_v2 >> 8) & 0xFF);
    _b[5] = (uint8_t)(_v2 & 0xFF);
    _b[6] = (uint8_t)((_v3 >> 8) & 0xFF);
    _b[7] = (uint8_t)(_v3 & 0xFF);
    LOG_ID_BYTES(msg_id, _b, 8);
    handle->response_code = response_code;
}
```

**🚩 ONE defect in that comment: "24 of the firmware's 30 `__udivmodhi4` call sites" — the total is 31 at `adf1a31`, not 30 (RESEARCH C-2). Copy the code character-for-character; rewrite `30` to `31` in the comment.** The derived "24" is confirmed correct and stays.

**⚠ `uint16_t measured_mv` / `uint16_t expected_mv` are LOAD-BEARING and must not be "improved".** Both operands at all four call sites are `uint16_t` (`eprom.cpp:711`, `flash_intel.cpp:36`, `firestarter.h:214`), so `(x + 50)` promotes to 16-bit `unsigned int` on AVR (`sizeof(int) == 2`) and `/1000` compiles to `__udivmodhi4`. Widening to `uint32_t` swaps in `__udivmodsi4`, erases the −426 B, and changes the wrap point above 65485 mV. The `(uint32_t)` casts that *do* appear — `vpp_mv > (uint32_t)handle->vpp_mv + 500` — are at the **comparison** sites, outside the extracted block, and must stay exactly where they are.

The chip-ID helper (same ref, immediately below) is quoted verbatim in RESEARCH §Architecture Patterns Pattern 1 and its comment needs no correction. Note its structural asymmetry: it derives **both** id and `response_code` from one `warn_only` bool (transposition-proof on one axis); `mem_util_report_voltage` takes them as **two independent parameters** (transposable). That asymmetry is DEDUP-03's whole subject.

---

### `include/memory_utils.h` — the two declarations (header / contract)

**Analog:** `include/memory_utils.h:19-29` — the `memory_verify_execute` declaration, which exists for *exactly* this phase's reason and says so:

```c
/*
 * Debug session w27c512-write-slow-3x: exposed so eprom.cpp's
 * VERIFY_PER_PULSE_PLUS_FINAL arm can CALL the canonical full-block verify
 * instead of carrying a byte-identical copy of it. eprom.cpp's own comment
 * already said its copy "mirrors memory_verify_execute exactly: same
 * MSG_ERR_VERIFY id, same 5-byte payload, same early return" -- this
 * declaration turns that comment into a linkage. Definition stays in
 * src/proms/memory.cpp; ...
 */
void memory_verify_execute(firestarter_handle_t* handle);
```

**Idiom to match:** a block comment naming *what duplication the declaration retires* and *where the definition lives*, then the bare prototype. Everything sits inside the file's `extern "C" { ... }` guard (`:11-13` / `:60-61`), so `bool` in `mem_util_report_chip_id`'s signature compiles in both C and C++ TUs (`firestarter.h` is included at `:10`).

**Insertion point — verbatim from the preserved ref** (`git diff HEAD wip/v1.33-size-reduction-survey-preserved -- include/memory_utils.h`): immediately above `void mem_util_split_delay(...)` at `:51`.

```c
void mem_util_report_voltage(firestarter_handle_t* handle, uint16_t measured_mv,
                             uint16_t expected_mv, uint8_t msg_id, uint8_t response_code);
void mem_util_report_chip_id(firestarter_handle_t* handle, uint16_t actual, bool warn_only);
```

**🚩 The ref inserts these with NO comment, directly under `mem_util_delay_us`'s long block comment — which makes that comment read as if it documents the new prototypes.** Do not copy that placement blindly: add a short block comment of its own (per the `memory_verify_execute` idiom above), or insert *below* `mem_util_delay_us`.

---

### `src/proms/eprom.cpp` / `flash_intel.cpp` — the four VPP blocks (protocol handler, request-response)

**The block being extracted, quoted verbatim from `src/proms/eprom.cpp:713-718`** (this is the shape the planner will see four times; `flash_intel.cpp:39-44` is byte-identical in its packing):

```c
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
        {
            uint16_t _v0 = (uint16_t)((vpp_mv + 50) / 1000);
            uint16_t _v1 = (uint16_t)((((vpp_mv + 50) / 100) % 10));
            uint16_t _v2 = (uint16_t)((handle->vpp_mv + 50) / 1000);
            uint16_t _v3 = (uint16_t)((((handle->vpp_mv + 50) / 100) % 10));
            uint8_t _b[8];
            _b[0] = (uint8_t)((_v0 >> 8) & 0xFF);
            ...
            _b[7] = (uint8_t)(_v3 & 0xFF);
            if (is_flag_set(FLAG_FORCE)) {
                LOG_WARN_ID_BYTES(MSG_WARN_VPP_HIGH, _b, 8);
                handle->response_code = RESPONSE_CODE_WARNING;
            } else {
                LOG_ERROR_ID_BYTES(MSG_ERR_VPP_HIGH, _b, 8);
                handle->response_code = RESPONSE_CODE_ERROR;
            }
        }
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {
        {
            ... same 12 lines ...
            LOG_WARN_ID_BYTES(MSG_WARN_VPP_LOW, _b, 8);
            handle->response_code = RESPONSE_CODE_WARNING;
        }
    }
```

**Replacement pattern — two parallel ternaries on one boolean** (RESEARCH Pattern 2; measured 244 B cheaper than the `if`/`else` pair):

```c
    bool force = is_flag_set(FLAG_FORCE);
    mem_util_report_voltage(handle, vpp_mv, handle->vpp_mv,
                            force ? MSG_WARN_VPP_HIGH : MSG_ERR_VPP_HIGH,
                            force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR);
```

Under-voltage arm collapses to one call with `(MSG_WARN_VPP_LOW, RESPONSE_CODE_WARNING)`.

**Fences (all verified in the tree):**
- ⚠ `flash_intel.cpp`'s two blocks are lexically inside `static void flash_intel_check_vpp(firestarter_handle_t*)` at `:26`, **not** `flash_intel_write_init` (C-1). Confirmed by reading `:26-80`.
- The trailing `handle->firestarter_set_control_register(handle, EPROM_HV_ALL_OFF_MASK, 0);` at `eprom.cpp:720` is the VPP-03 shared composite clear guarded by `tests/test_hv_routing_source_contract_v142.py`. **Do not disturb it, `eprom_hv_route_mask`, or the `LOG_DEBUG_ID_SUB_U16(DBG_CHECKING_VPP_VOLTAGE, ...)` line.**
- `LOG_ID_BYTES` with a runtime id is safe — `include/logging_id.h:39-40` is a plain function call, and `:105`/`:119` prove `LOG_WARN_ID_BYTES` and `LOG_ERROR_ID_BYTES` are the *same* alias. Severity rides entirely in the id.

---

### `src/proms/flash_utils.cpp` / `eeprom_28c.cpp` / `eprom.cpp` — the four chip-ID blocks (protocol handler / utility)

**Cast-free canonical form, `src/proms/flash_utils.cpp:104-107` (Site A — copy this shape):**

```c
void flash_util_check_chip_id_execute(firestarter_handle_t* handle) {
    uint16_t chip_id = flash_util_get_chip_id(handle);
    if (chip_id != handle->chip_id) {
        uint8_t _b[4];
        _b[0] = (uint8_t)((chip_id >> 8) & 0xFF);
        _b[1] = (uint8_t)(chip_id & 0xFF);
        _b[2] = (uint8_t)((handle->chip_id >> 8) & 0xFF);
        _b[3] = (uint8_t)(handle->chip_id & 0xFF);
        if (is_flag_set(FLAG_FORCE)) { ... WARN ... } else { ... ERROR ... }
    }
}
```

**Site C's divergence, `src/proms/eeprom_28c.cpp:292-290` — redundant casts + a superfluous brace level, both provable no-ops:**

```c
    if (chip_id != handle->chip_id) {
        {
            uint8_t _b[4];
            _b[0] = (uint8_t)(((uint16_t)chip_id >> 8) & 0xFF);
            _b[2] = (uint8_t)(((uint16_t)handle->chip_id >> 8) & 0xFF);
```

`chip_id` is `uint16_t` (`eeprom_28c.cpp:288`) and `handle->chip_id` is `uint16_t` (`firestarter.h:223`). Drop both.

**Site D's divergence — `src/proms/eprom.cpp:768-772` keys severity on a PARAMETER, not the flag:**

```c
void eprom_internal_check_chip_id(firestarter_handle_t* handle, uint8_t error_code) {
    ...
        if (error_code == RESPONSE_CODE_WARNING) { WARN } else { ERROR }
```

**⚠ Divergence 1 must be PARAMETERISED, never collapsed.** `eprom.cpp` has two callers of Site D with different policies — `eprom_generic_init:791` passes `is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR` (verified at `:785-792`), while `eprom_check_chip_id_execute:119` passes `RESPONSE_CODE_ERROR` unconditionally. Folding `is_flag_set(FLAG_FORCE)` into the helper would silently make standalone `CMD_CHECK_CHIP_ID` honour `--force`. Callers pass `warn_only`: A/B/C `is_flag_set(FLAG_FORCE)`, D `error_code == RESPONSE_CODE_WARNING`.

**Divergence 6 — one `#include "memory_utils.h"` must be added to `flash_utils.cpp`.** Analog: `flash_intel.cpp:14` already has it. This single added line shifts **all 97** `.planning/` citations into `flash_utils.cpp` — expected, close-blocked by REMAP-04 (D-05). **Do not remap in this phase.**

---

### `src/eprom_operations.cpp` — the 9 `!` and the comment (command wrapper layer, event-driven)

**The 9 sites, read live** (`eprom_read:20`, `eprom_write:25`, `eprom_verify:31`, `eprom_erase:40`, `eprom_check_chip_id:49`, `eprom_blank_check:54`, `eprom_sdp_unlock:69`, `eprom_sdp_lock:73`, `eprom_lock_status:86`). `sed -i 's/return !op_execute_/return op_execute_/'` hits exactly these 9 and nothing else — `grep -c` confirms 9.

**⚠ The two do-not-touch analogs, quoted verbatim** — these `return true;` literals are correct under *both* conventions and flipping them breaks the refusals:

```c
bool eprom_erase(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_ERASE_PROM);
    if (!is_flag_set(FLAG_CAN_ERASE)) {
        LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED);
        return true;                      // <-- DO NOT FLIP (:37)
    }
    return !op_execute_simple_operation(handle);   // <-- flip this one only
}
```
(`eprom_check_chip_id:46` is the identical shape for `chip_id == 0`.)

**The comment edit — C-6, verified by reading `:57-67`.** Only the last three lines are dead:

```c
// LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK
// ... (5 lines of LOCK rationale that must SURVIVE) ...
// is exactly op_execute_simple_operation's single-step shape; op_execute_   <-- :65
// simple_operation returns true when FINISHED, so the `!` inversion here is <-- :66
// load-bearing (mirrors eprom_erase/eprom_blank_check above).               <-- :67
```

Delete `:65-67` (and re-terminate `:64`'s sentence). **Deleting `:57-67` wholesale destroys LOCK-01/LOCK-02 rationale unrelated to the boolean convention.**

**Honest framing the plan must adopt:** `op_execute_stateful_operation`'s site 4 becomes `return !callback(handle);` because the three callbacks keep their own documented "returns true on success/continue, false on error" convention (`eprom_operations.cpp:84`, read live). **The `!` moves from 9 sites to 1; it is not eliminated.** Say that, not "the inversion is gone".

**Comment blast radius, all six locations verified live:** `eprom_operations.cpp:65-63` (delete 3), `operation_utils.cpp:98-100` (the D-06 mega-comment's mechanism narrative — "Every `eprom_*` caller inverts that return"), `operation_utils.cpp:~155` ("every `eprom_*` caller **still** inverts it" — read at `:155-156`), `include/operation_utils.h:71` and `:85` (both read `@return true if the operation is still ongoing ... false when fully completed` — invert both), and `test_eeprom28c_sdp.cpp:1469` + `:1492` (both quote `return !op_execute_...` as the contract under test — read live at `:1409-1412` and `:1491-1493`).

---

### `test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` — the under-voltage severity pairing (native test, blind spot 1)

**Analog: `test_vpp04_a` (`:630-651`) — the exact house style for asserting a severity pairing in both directions:**

```c
void test_vpp04_a_overvoltage_refusal_fires_by_id_with_payload_shape(void) {
    rurp_get_config()->hardware_revision = REVISION_2_2;  /* mandatory: on
        REVISION_0 eprom_check_vpp takes the early return at eprom.cpp:334-338 ... */
    firestarter_handle_t h = make_vpp_handle(0x07, 28, 65536, 100, 13000, 0, VPP_BUS_CONFIG_0x07);
    set_mock_vpp_mv(13501);  /* one mV past the 13000+500 over-voltage boundary -- pins the boundary */
    drive_vpp_init(&h);

    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "an injected 13501 mV reading (setpoint 13000, boundary 13500) must refuse with RESPONSE_CODE_ERROR");
    TEST_ASSERT_EQUAL_MESSAGE(1, count_logged_id(MSG_ERR_VPP_HIGH),
        "MSG_ERR_VPP_HIGH (0xB8) must be logged exactly once, BY ID -- no test in this tree asserts this before this plan (D-13)");
    TEST_ASSERT_EQUAL_MESSAGE(0, count_logged_id(MSG_WARN_VPP_HIGH),
        "the hard-ERROR fork must NOT also log the WARNING id -- pins the FLAG_FORCE fork in both directions");
    int idx = find_logged_id(MSG_ERR_VPP_HIGH);
    TEST_ASSERT_TRUE_MESSAGE(idx >= 0, "MSG_ERR_VPP_HIGH must actually be present in the logged-id stream");
    TEST_ASSERT_EQUAL_MESSAGE(8, logged_id_param_count(idx),
        "the ERROR frame must carry the 8 payload bytes eprom.cpp:369-371 (LOG_ERROR_ID_BYTES) emits");
}
```

**The exact four-assertion shape the new under-voltage case must copy:** `response_code == RESPONSE_CODE_WARNING`, `count_logged_id(MSG_WARN_VPP_LOW) == 1`, **`count_logged_id(MSG_ERR_VPP_HIGH) == 0` and `count_logged_id(MSG_WARN_VPP_HIGH) == 0`** (the "not the other fork" legs — this pair is what makes probe B RED), plus `logged_id_param_count(find_logged_id(MSG_WARN_VPP_LOW)) == 8`.

**Harness already present, no new infrastructure:** `make_vpp_handle`, `set_mock_vpp_mv` (`host_stubs.cpp:253`), `drive_vpp_init`, `count_logged_id` / `find_logged_id` (`test_vpp_eprom_v131.cpp:348-362`, both `[[maybe_unused]] static int`), `logged_id_param_count` (`extern "C"`, declared at `:95`ff).

**Boundary to inject:** under-voltage fires at `vpp_mv < handle->vpp_mv * 95 / 100`. With `vpp_mv` setpoint 13000 that is `< 12350`, so **inject `12349`** — one mV inside the boundary, matching `test_vpp04_a`'s "pin the boundary, not a wildly out-of-range value" discipline. `REVISION_2_2` is mandatory for the same reason `test_vpp04_a` states.

**Analog for the mandatory anti-vacuity control: `test_vpp04_d` (`:740-756`)** — an in-range reading (`set_mock_vpp_mv(13000)`) asserting all three ids are 0, with the docstring "a control that cannot fail is not a control." That case *already* asserts `count_logged_id(MSG_WARN_VPP_LOW) == 0`, so the new case plus `test_vpp04_d` form a complete both-directions pair.

**Gate freedom confirmed:** `tests/test_requirement_case_mapping_v131.py`'s per-suite check is a **floor** (≥32, live 33) and `check_size_baseline.py::compare_native` reads only `native` / `native_nodevtools`. Adding cases here is free. **Must be labelled NO CI COVERAGE** (env `native_loop_v131`).

**`flash_intel.cpp`'s two blocks have no executing coverage in any env** (`test_flash_intel_vpp` is in no `test_filter`). Its regression evidence is the `eprom.cpp` twin plus source-level byte-identity — state it that way; do not imply a `flash_intel` leg exists.

---

### `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — three edits (native test, CI-visible)

**(1) Case 7 strengthened — the chip-ID message id (blind spot 2).** Live at `:792-806`:

```c
void test_case7_mismatching_chip_id_with_force_warns(void) {
    s_mfr_addr_keyed = 32768 - 64;
    s_mfr_hi_keyed = 0xDE;
    s_mfr_lo_keyed = 0xAD;
    firestarter_handle_t h = make_identity_handle(0x1F08, FLAG_FORCE);
    configure_memory(&h);
    h.firestarter_get_data = mock_get_data_keyed;
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();
    h.firestarter_operation_init(&h);
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_WARNING, h.response_code,
        "migrated (RED, CORRECTION 2): mismatching identity + FLAG_FORCE must WARN, not have its "
        "severity destroyed by the unconditional SDP-disable completion wait");
}
```

**Add, in the id-capture idiom this suite already uses (`:1433-1439` shows it verbatim in Case 24):**

```c
    std::vector<uint8_t> ids;
    sdp_captured_frame_ids(&ids);
    TEST_ASSERT_TRUE_MESSAGE(sdp_ids_contains(ids, (uint8_t)MSG_WARN_CHIP_ID_MISMATCH),
        "...MSG_WARN_CHIP_ID_MISMATCH must appear -- severity rides ENTIRELY in the id "
        "(logging_id.h:105,119 alias WARN and ERROR to the same LOG_ID_BYTES), so the "
        "response_code assertion above cannot see a transposed id (probe D)");
    TEST_ASSERT_FALSE_MESSAGE(sdp_ids_contains(ids, (uint8_t)MSG_ERR_CHIP_ID_MISMATCH),
        "...and the ERROR id must NOT also appear -- pins the fork in both directions");
```

`captured_frames` is cleared per-case in `setUp` (`:303`), so no manual clear is needed. `sdp_captured_frame_ids` / `sdp_ids_contains` are `static` in this TU (`:192`, `:206`) — no declaration to add.

**Anti-hollow-control analog to imitate — Case 11 (`:966-982`)**, which re-drives with `captured_frames.clear()` and a second handle to prove the id is *conditional* rather than always emitted:

```c
    sdp_script_micros({0, 0});
    captured_frames.clear();
    firestarter_handle_t h2 = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive_write_init(&h2, 0x00);
    std::vector<uint8_t> ids_default;
    sdp_captured_frame_ids(&ids_default);
    TEST_ASSERT_FALSE_MESSAGE(sdp_ids_contains(ids_default, (uint8_t)MSG_WARN_SDP_TBLC_EXCEEDED),
        "Case 11 (anti-hollow control): ... proves the check is conditional ...");
```

**This is the pattern for the ERROR direction too** — a second, in-case matching-identity or non-force drive after `captured_frames.clear()` gives both fork directions **inside one existing case**, keeping `cases == 172` (`compare_native` asserts exact equality — Pitfall 6).

**(2) Case 24 polarity flip — `:1416-1439`, measured RED by construction.** Live:

```c
    bool still_in_progress = op_execute_stateful_operation(NULL, &h);

    TEST_ASSERT_FALSE_MESSAGE(still_in_progress,
        "Case 24 (D-06/D-07): op_execute_stateful_operation must return false on a NULL main -- "
        "every eprom_* caller inverts this return to report the command as finished, unchanged "
        "semantics from before this task");
```

`TEST_ASSERT_FALSE_MESSAGE` → `TEST_ASSERT_TRUE_MESSAGE`, and the message's "every `eprom_*` caller inverts this return" clause must be rewritten (it stops being true). The `RESPONSE_CODE_ERROR` and `MSG_ERR_NOT_SUPPORTED` legs below it are unaffected. Also update the case's own header comment at `:1411`, which quotes `return !op_execute_stateful_operation(callback, handle)`.

**(3) Case 25 de-vacuumed — `:1509-1537`, measured to pass while taking 1 call instead of 4.** Live drive loop:

```c
    bool still_in_progress = true;
    int calls = 0;
    const int MAX_CALLS = 10; /* deterministic trace needs exactly 4; generous margin, not an escape hatch */
    while (still_in_progress && calls < MAX_CALLS) {
        still_in_progress = op_execute_simple_operation(&h);
        calls++;
    }
    TEST_ASSERT_FALSE_MESSAGE(still_in_progress, "Case 25 ... must reach completion (false) ...");
```

Flip to `bool finished = false; while (!finished && calls < MAX_CALLS) { finished = op_execute_simple_operation(&h); calls++; }`, assert `TEST_ASSERT_TRUE_MESSAGE(finished, ...)`, **and add the non-vacuity leg the research proved necessary:**

```c
    TEST_ASSERT_EQUAL_MESSAGE(4, calls,
        "Case 25 non-vacuity: completion must take exactly FOUR op_execute_simple_operation "
        "calls (INIT-start ack, MAIN-start ack + erase run, END-start ack, final ack) -- the "
        "count this case's own comment documents. Measured during 156 research: after the "
        "DEDUP-04 flip the un-flipped loop exited after 1 call and still reported PASSED.");
```

The `Expected 4 Was 1` probe is already recorded in the research; **never delete the case.** The `4` is documented in the case's own DEVIATION comment at `:1497-1508`. Also update the `:1492` quote of `return !op_execute_simple_operation(handle);`.

**Message idiom across all three edits** (matches every case in this suite and the Phase 155 finding): `TEST_ASSERT_*_MESSAGE`, message prefixed `"Case NN (REQ-ID): "`, ` -- ` as the reason separator, 4-space continuation indent, `/* … * … */` comment blocks with a `─────` banner for a new group.

---

### `tests/golden/protocol_branch_inventory.json` + `tests/test_protocol_branch_inventory.py` (golden + source-contract gate)

**Analog: itself.** `meta` (read live) carries `sources`, `blob_shas`, `recorded_at_head`, `recorded_by`; `counts` is `{"total_sites": 23, "protocol_keyed_sites": 1, "other_sites": 22}`; each entry of `sites` is `{line, predicate, keyed_on, tier, class, reason}`. Blob SHA for `src/proms/eprom.cpp` is `838aca47986103969be4caca3cef71a033bac069` — **matches the live file, so the gate is GREEN on arrival and this phase's edit is what breaks it.**

**Four prior re-derivations are documented in `meta.recorded_by`, and they establish the exact convention to copy:**
- `blob_shas['src/proms/eprom.cpp']` = `git hash-object src/proms/eprom.cpp` run on the **working tree, before staging**.
- `recorded_at_head` names this commit's **PARENT** — the deliberate one-commit offset, explicitly "not a mistake".
- `recorded_by` is **appended to, never replaced**, and states in prose which sites moved and *why*, plus whether predicates/keyed_on/tier were machine-checked as byte-identical.
- **Re-derive with the module's own `_extract_predicates()`**, never a hand-edited line number. The runnable snippet is in RESEARCH §Code Examples.

**Target counts: `total_sites` 23 → 21, `protocol_keyed_sites` 1 → 1, `other_sites` 22 → 20.** Two removed, none added.

**⚠ The `recorded_by` prose must say the `chip_id != handle->chip_id` predicate MOVED into `mem_util_report_chip_id` in `src/proms/memory.cpp` — a file this gate does not scan — not that a safety branch was deleted.** "Duplication merely relocated elsewhere" is precisely what the sibling gate `tests/test_hv_routing_source_contract_v142.py` exists to catch.

**One-commit property:** the golden and the `eprom.cpp` edit land in the **same commit**, so the gate goes RED once for one reason.

---

### *(optional, high value)* `tests/test_boolean_convention_source_contract_v133.py` (pytest, source contract)

**Analog: `tests/test_write_path_source_contract_v131.py` (715 lines).** Copy four things.

**(a) Root + env-seam header** (`:146-159`), the canonical way a pytest here locates firmware source — no fixture, no conftest:

```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_EPROM_REL = "src/proms/eprom.cpp"
_MEMORY_REL = "src/proms/memory.cpp"

# Environment seam -- binds at IMPORT time. See the module docstring's
# "Environment seams" section above.
_SCAN_EPROM = Path(
    os.environ.get("FIRESTARTER_WRITE_PATH_SCAN_SOURCE", str(_REPO_ROOT / _EPROM_REL))
)
```

Use `src/eprom_operations.cpp` + `src/operation_utils.cpp` as the two targets, one env seam, and record in the docstring that the seam binds at import time so a planted-violation run must set it in a **child process**.

**(b) `_strip_comments` — copy VERBATIM** (`:222-255`). Replaces each stripped span with same-shape whitespace so line numbers survive:

```python
def _strip_comments(text):
    """Strip `//` line comments and `/* ... */` block comments, replacing
    each stripped span with whitespace of the SAME SHAPE (a newline stays a
    newline, everything else becomes a single space) so every line number
    in the result matches the original file exactly -- the same technique
    test_protocol_branch_inventory.py's own comment-and-literal stripper
    uses, narrowed to comments only. ..."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            out.append("  ")
            i += 2
            while i < n and not (text[i] == "*" and i + 1 < n and text[i + 1] == "/"):
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            if i < n:
                out.append("  ")
                i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)
```

**⚠ That docstring's justification for skipping literal-stripping ("both scan targets contain no string or character literal outside a comment or `#include`") was confirmed for `eprom.cpp`/`memory.cpp` at authoring time — RE-CONFIRM it for `eprom_operations.cpp` and `operation_utils.cpp`, or extend the stripper.**

**(c) The absence-assertion helper** (`:302-315`) and its concatenation-built needle discipline (`:167-172`) — a gate that quotes its forbidden token verbatim matches itself and can never pass:

```python
_NEEDLE_INVERTED_CALL = "return !op_" + "execute_"

def _assert_identifier_absent(needle, label, stripped, target_rel):
    matches = re.findall(r"\b" + re.escape(needle) + r"\b", stripped)
    assert matches == [], (
        f"found {len(matches)} occurrence(s) of {label} in the "
        f"comment-stripped {target_rel} -- ..."
    )
```

**(d) The MANDATORY non-vacuity legs.** VALIDATION.md flags this and the repo has been bitten by it: a zero-match grep passes trivially against a deleted or empty file. Copy `test_scan_targets_are_non_vacuous` (`:641-669`) **verbatim in spirit** — it asserts each default target `is_file()`, is non-empty, `resolve().is_relative_to(_REPO_ROOT)` (closing the `check_permitted_claims.py` `_HERE`-resolves-wrong landmine **by construction**), and that its comment-stripped text is non-empty. Then add the **positive counterpart** in the shape of `test_the_per_byte_loop_constructs_are_present` (`:394-425`): assert `return op_execute_stateful_operation` / `return op_execute_simple_operation` appear **exactly 9 times combined** in `eprom_operations.cpp`, so a deleted file or a deleted call fails loudly instead of satisfying the absence leg vacuously. Also copy `test_this_module_cannot_be_silently_skipped` (`:671-698`) and `test_own_needles_do_not_appear_verbatim_in_this_module` (`:700-715`).

**Naming/frontmatter note:** the module docstring is the *only* environment-seam inventory in this repo, so it must be written in full (project/copyright header, phase + requirement IDs, "Defect class this closes", numbered `Coverage:` list, `Environment seams:`, and an honest `CI framing` paragraph noting `pytest tests/ -v` runs at `build.yml:161` / `beta-build.yml:134` but not on the milestone branch).

---

### The planted-negative / mutation-proof pattern (DEDUP-03's evidence discipline)

**Analog: `tests/test_check_no_heap_or_64bit_symbols.py` — Phase 155's own gate, landed at `076abc2` and `adf1a31`.** Its structure is the template:

| Leg | Line | Role |
|---|---|---|
| `test_planted_prechange_listing_exits_one_and_names_the_symbols` | `:157` | **the armed negative** — a committed fixture that MUST fail, asserting the literal exit code **1** and that the output *names* the offending symbols |
| `test_derived_clean_listing_exits_zero_and_names_the_target` | `:181` | a **synthetic** clean control, derived from the planted fixture by construction at test time |
| `test_real_postchange_listing_exits_zero` | `:214` | the **real** clean control, a committed unedited capture at a named SHA |
| `test_missing_listing_path_exits_two` / `..._without_anchors_exits_two` / `test_malformed_argv_exits_two` | `:233,247,276` | fail-closed taxonomy: exit **2** ≠ exit **1** |
| `test_scan_targets_are_non_vacuous` | `:321` | the fixture exists, is non-empty, resolves inside `_REPO_ROOT`, and **contains at least one of each forbidden class** — so a filtered fixture cannot make the armed leg vacuous |

Note the discipline in the real-control docstring, which the plan should mirror for its own captures: *"the REAL, committed, unedited … listing … (captured at FW_POST_SHA 98e70af1…), not a synthetic derivative filtered from the pre-change listing at test time."*

**For DEDUP-03's four severity transpositions the equivalent is a run-and-record, not a committed fixture** (the mutation is in C source, not a capturable artifact). The template is RESEARCH §Code Examples' four `sed -i` probes, verbatim and re-runnable. Each new assertion must be **seen RED against its planted transposition and GREEN against the real tree, both directions recorded in the plan's own SUMMARY.**

**⚠ Worktree naming trap (measured):** `tests/test_checker_convention.py::test_scope_is_firmware_only` hard-codes the directory name (`parts[-2:] == ("firestarter", "scripts")`). **Any throwaway worktree for a planted-negative proof must be named `firestarter`** — e.g. `/tmp/probe/firestarter` — or this leg fails spuriously and reads like a real red.

---

### *(Wave 0)* `.planning/v1.33/156-before-figures.md` (planning record, measurement)

**Analog: `.planning/v1.33/155-before-figures.md`** (and its landing twin `155-after-figures.md`). Copy the frontmatter block and section shape:

```yaml
---
title: Before-figures record — milestone v1.33, Phase 156 (...)
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "01"
measured: 2026-08-23
status: AUTHORITATIVE — this file is the ONLY source for Phase 156's before-half figures.
  Phases 157 and 158 each invalidate the measurements captured here...
supersedes: >
  ROADMAP.md Phase 156 criteria 1 and 4, and REQUIREMENTS.md DEDUP-01/DEDUP-04 prose,
  wherever they state a figure this file corrects (C-1 … C-7).
requirements: [DEDUP-01, DEDUP-02, DEDUP-03, DEDUP-04]
---
```

Then `## 1. Git anchors` as a `| Field | Value |` table (`FW_PRE_SHA`, branch, `git status --porcelain` empty, `git worktree list`), every figure labelled **WARM** and carrying **the verbatim command that produced it**. Filenames are lowercase-hyphenated with the phase number prefixed. Must include: 3 flash/RAM pairs, `eprom_check_vpp` 524 B, `flash_intel_write_init` 562 B, and `__udivmodhi4` = **31** (ROADMAP says 30 — C-2).

`avr-nm` / `avr-objdump` are **not on `PATH`** — invoke as `~/.platformio/packages/toolchain-atmelavr/bin/avr-{nm,objdump}`.

---

## Shared Patterns

### Extract the shared MECHANISM, parameterise the divergent POLICY
**Source:** `src/proms/memory.cpp:305-324` (`mem_util_split_delay`/`mem_util_delay_us`) and `include/memory_utils.h:19-29` (`memory_verify_execute`).
**Apply to:** both new helpers, all eight call sites.
The packing and the emit are shared; severity stays at the call site (`msg_id` + `response_code`, or `warn_only`). This is what makes the change de-duplication rather than behaviour change.

### Severity rides ENTIRELY in the message id
**Source:** `include/logging_id.h:39-40`, `:105`, `:119`.
**Apply to:** every DEDUP-01/02/03 artifact.
```c
#define LOG_ID_BYTES(id, buf_array, count) \
    rurp_log_id((id), (const uint8_t*)(buf_array), (uint8_t)(count))
#define LOG_ERROR_ID_BYTES(id, b, n)   LOG_ID_BYTES((id), (b), (n))
#define LOG_WARN_ID_BYTES(id, b, n)    LOG_ID_BYTES((id), (b), (n))
```
A plain function call, so a runtime `uint8_t msg_id` is safe; identical expansions, so a `response_code` assertion **cannot** see a transposed id and vice-versa. This is what makes the consolidation cheap and what makes it dangerous.

### No new message id, and `include/messages.h` is untouched
**Source:** `grep include/messages.h` — all five ids exist: `MSG_WARN_VPP_LOW 0x81`, `MSG_WARN_VPP_HIGH 0x82`, `MSG_WARN_CHIP_ID_MISMATCH 0x83`, `MSG_ERR_VPP_HIGH 0xB8`, `MSG_ERR_CHIP_ID_MISMATCH 0xB9`.
**Apply to:** all plans. `messages.h` is codegen-generated from meta's `tools/catalog/messages.toml`; **zero catalog edits, zero `codegen.py` runs.** I found no reason this phase would need a new id — it is de-duplication, and both payload widths (8 and 4) and all five ids are preserved exactly.

### Non-vacuity is mandatory, in every register
**Sources:** `test_write_path_source_contract_v131.py:641-669` (pytest), `test_check_no_heap_or_64bit_symbols.py:321-349` (fixture), `test_vpp_eprom_v131.cpp:740-837` (native control), `test_eeprom28c_sdp.cpp:1023-1039` (native anti-hollow re-drive), `test_vpp_eprom_v131.cpp:679-681` (`saw_earlier_set` — "otherwise the assertion is vacuously true of a register that was never energised at all").
**Apply to:** every new assertion and every new gate leg in this phase. Every one of these five is quotable in a plan.

### Unity assertion idiom
**Source:** every case in `test_eeprom28c_sdp.cpp` and `test_vpp_eprom_v131.cpp`.
`TEST_ASSERT_*_MESSAGE` always (never the bare form); message prefixed `"Case NN (REQ-ID): "` or `"REQ-ID: "`; ` -- ` as the reason separator; 4-space continuation indent; group banners as `/* ───── ... ───── */`.

### Anti-patterns (all measured this phase)
- Asserting `.hex`/ELF **byte**-identity for DEDUP-04 — the SHA changes on all three targets while sizes do not (C-4). The oracle is `flash_used` + `ram_used`.
- Pinning a `.constprop.NN` clone suffix (C-5: it is `.42` today, not `.44`).
- Hand-editing `protocol_branch_inventory.json` — its own `how_to_update` forbids it.
- Folding `is_flag_set(FLAG_FORCE)` into `mem_util_report_chip_id`.
- Widening the voltage helper's parameters to `uint32_t`.
- Deleting `eprom_operations.cpp:57-63` wholesale (C-6).
- Adding a **new** case to `native` / `native_nodevtools` (`compare_native` asserts `cases == 172` exactly).
- Adding a strong `rurp_log_id` override to `test_eeprom28c_sdp/host_stubs.cpp` (see the A4 finding).
- Running `pytest tests/` on a dirty tree — 4 modules assert repo porcelain and several read `git rev-parse HEAD:<path>`. **Commit, then run.**
- Blaming a native failure on N=1 (D-04); a real failure also inflates the reported count (173 vs 172).

---

## No Analog Found

None. Every file has one. Two weak spots worth naming, both with a stated fallback:

| Item | Gap | Fallback |
|---|---|---|
| `test_sdp_harness` chip-ID id assertion | no id-capture facility in that suite (`Serial.write` is `.AlwaysReturn(1)`, `test_sdp_harness.cpp:82-83`) | put both fork directions in `test_eeprom28c_sdp` (which has the facility) — recommended over porting 55 lines into an always-green suite |
| The 8-byte payload's **byte values** | no oracle exists anywhere; `test_vpp04_a` asserts the **length** is 8 only | source-level identity of the arithmetic + parameter types, plus the `__udivmodhi4` (not `__udivmodsi4`) corroboration. **Never write "the payload bytes were compared."** |

---

## Metadata

**Analog search scope:** `firestarter/{include,src,src/proms,src/boards,test/native/avr,tests,tests/golden,scripts,.github/workflows}`, `firestarter/platformio.ini`, `wip/v1.33-size-reduction-survey-preserved` (via `git show`/`git diff`, no checkout), `.planning/v1.33/`, `.planning/phases/155-*/155-PATTERNS.md`.
**Files read:** 21 (11 firmware source/header, 5 native test/stub, 3 pytest, 1 golden, 1 planning record) — every read targeted, no range re-read.
**Read-only confirmed:** only `git show`, `git diff`, `git log`, `sed -n`, `grep`, `cat -n`, `ls`, `wc`, and a read-only `json.load`. No source file modified; nothing built; nothing committed.
**Pattern extraction date:** 2026-08-23
