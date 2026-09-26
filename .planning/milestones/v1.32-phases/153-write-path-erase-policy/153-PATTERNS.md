# Phase 153: Write-Path Erase Policy — Pattern Map

**Mapped:** 2026-08-21
**Files analyzed:** 19 (2 fw source, 4 fw test/baseline, 5 host source, 6 host test, 2 doc)
**Analogs found:** 17 / 19 (2 files need no analog — they are pure deletions)

> Every line number below was re-verified against the working tree on branch
> `gsd/v1.32-at28c-write-path-root-cause-report-provenance` this session. Two RESEARCH.md line
> numbers moved: `flash_5v_page_write_init`'s blank-check conditional is at **`:87-89`** (not 88-90),
> and `ic_layout.py`'s `can_erase_str` block is at **`:578-586`**. `eeprom_28c.cpp:517-519`,
> `database.py:617-622`, `test_configure_memory.cpp:311-318`, `test_eeprom28c_sdp.cpp:1448-1473`,
> `test_database_conversion.py:98-117`, `test_chip_test_blank_check_order.py:121-129` all confirmed.

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|---|
| `src/proms/eeprom_28c.cpp` — new `CMD_ERASE` arm | fw | protocol handler (dispatch table) | request-response | **same file**, `case CMD_SDP_LOCK:` at `:232-234` | exact (same function) |
| `src/proms/eeprom_28c.cpp` — new `eeprom28c_erase_execute` | fw | protocol handler (bus op) | streaming (byte writes) | **same file**, `eeprom28c_sdp_lock_execute` at `:455-461` | exact |
| `src/proms/eeprom_28c.cpp` — delete blank check `:547-549` | fw | handler init | — | pure deletion | n/a |
| `src/proms/flash_5v_page.cpp` — delete blank check `:87-89` | fw | handler init | — | pure deletion (byte-identical to the above) | n/a |
| `firestarter/database.py` `:620` + `:588-616` comment | host | model/derivation | transform | **same file**, the algorithm-5 rationale block `:580-586` (the half that STAYS) | exact |
| `firestarter/chip_test.py` `:307`, `:745-750` | host | service (plan derivation) | transform | **same file**, `_PROTOCOL_FLASH4` arm `:748` reason string | exact |
| `firestarter/cli_handlers.py` `:797-804` | host | controller (CLI) | request-response | **same file**, the C-8 comment at `:790-796` that already scopes the warning | exact |
| `firestarter/ic_layout.py` `:578-586` | host | view/formatter | transform | **NO EDIT — assertion only** (confirmed, see below) | n/a |
| `test/native/avr/test_dispatch/test_configure_memory.cpp` | fw | test (dispatch unit) | — | **same file**, Case group 3 at `:299-307` (the `TEST_ASSERT_NOT_NULL` shape) | exact |
| `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — Case 25 inversion | fw | test (end-to-end unit) | request-response | **same file**, Case 25 itself at `:1391-1416` (invert in place) | exact |
| `test_eeprom28c_sdp.cpp` — new stream-divergence case | fw | test (stream equality) | streaming | **same file**, `test_case19_lock_diverges_from_chip_erase_at_exact_index` `:1108-1124` | exact |
| `test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — new no-VPP case | fw | test (validation/no-VPP) | — | **same file**, `test_eeprom28c_blank_check_configure_no_vpp` `:202-209` | exact |
| `test/native/avr/test_val_5v_page/` — new negative case | fw | test (validation) | — | `test_val_eeprom28c.cpp:202-209` (same `assert_no_vpp_in_recording` idiom) | role-match |
| `tests/test_database_conversion.py` `:98-117` | host | test (unit) | — | **same file**, `test_convert_uv_eprom_no_flag_can_erase` `:89-95` + `..._w29c040_...` `:120-131` (negative controls, stay green) | exact |
| new host leg: exhaustive 84-row flag assertion | host | test (exhaustive DB invariant) | batch | `tests/test_page_size_invariants.py` `_select_0x0d_chips` `:125-137` + `test_exactly_20_page_size_carriers_across_all_746_rows` `:256-266` | exact |
| `tests/test_chip_test_blank_check_order.py` `:121-129` | host | test (plan-shape ordering) | — | **same file**, case 1 `test_m8720_...` (the "erase executable → blank-check moves" leg) | exact |
| `tests/test_ic_layout.py` — new agreement leg | host | test (cross-axis) | — | `tests/test_database_conversion.py` `:82-86` (the `flags & FLAG_CAN_ERASE` positive assert) | role-match |
| `scripts/baseline/size_baseline.json` + `scripts/check_size_baseline.py` | fw | config + gate | — | `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES` block `:251-323` + `merge05_clause` (json `:23`) | exact |
| `tests/test_check_size_baseline.py` + `tests/fixtures/*_v153*` | fw | test (tripwire) | file-I/O | the 13-file `*_v151*` family + the Plan 151-10 module-docstring severance record `:284-340` | exact |
| `doc/PROTOCOLS.md:305` §1.6 / `doc/protocol-id.md:22` | both | doc | — | no code analog; prose correction | n/a |

---

## Pattern Assignments

### `firestarter/src/proms/eeprom_28c.cpp` — the `CMD_ERASE` dispatch arm (ERASE-03, fw half)

**Analog:** the same file's own switch, `configure_eeprom28c` `:222-235`. **Copy the local shape, not
`flash_5v_page.cpp`'s.**

**Current switch, verbatim** (`eeprom_28c.cpp:214-227`) — note the D-05 comment at `:208-220` that must
be read before touching it, and that this function assigns **no** `firestarter_operation_init`/`_end`
before the switch, so the new arm has nothing to null:

```c
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eeprom28c_write_init;
            handle->firestarter_operation_main = eeprom28c_write_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
        case CMD_SDP_UNLOCK:
            handle->firestarter_operation_main = eeprom28c_sdp_unlock_execute;
            break;
        case CMD_SDP_LOCK:
            handle->firestarter_operation_main = eeprom28c_sdp_lock_execute;
            break;
    }
```

**Pattern to copy:** the two-line `case CMD_SDP_LOCK:` arm exactly. One `firestarter_operation_main`
assignment, one `break`, no init, no end, no default.

**Also required by the same edit:** a forward declaration alongside the existing block at
`eeprom_28c.cpp:117-121`, which uses this shape:

```c
static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length);
static void eeprom28c_wait_for_sdp_completion(firestarter_handle_t* handle);
```

and `:126`: `static void eeprom28c_sdp_unlock_execute(firestarter_handle_t* handle);`

---

### `firestarter/src/proms/eeprom_28c.cpp` — `eeprom28c_erase_execute` (ERASE-04)

**Analog: `eeprom28c_sdp_lock_execute` (`eeprom_28c.cpp:427-433`).** This is the closest structural
match in the tree: *emit one table through the timed wrapper, then one unconditional `delay()`, no
completion poll, no `response_code` write, no read.* That is exactly the AN-0544B erase shape.

```c
// firestarter/src/proms/eeprom_28c.cpp:427-433 — COPY THIS SHAPE
static void eeprom28c_sdp_lock_execute(firestarter_handle_t* handle) {
    size_t sdp_seq_len = sizeof(EEPROM_SDP_ENABLE) / sizeof(EEPROM_SDP_ENABLE[0]);
    eeprom28c_emit_sdp_sequence_timed(handle, EEPROM_SDP_ENABLE, sdp_seq_len, MSG_INFO_SDP_LOCK,
                                       MSG_INFO_SDP_LOCK_DONE_US);
    delay(AT28C_TWC_MAX_MS);
}
```

Contrast `eeprom28c_sdp_unlock_execute` (`:437-442`), which *does* poll — the erase must **not** (AN
0544B Note 2 forbids traffic after the 6-byte load):

```c
static void eeprom28c_sdp_unlock_execute(firestarter_handle_t* handle) {
    size_t sdp_seq_len = sizeof(EEPROM_SDP_DISABLE) / sizeof(EEPROM_SDP_DISABLE[0]);
    eeprom28c_emit_sdp_sequence_timed(handle, EEPROM_SDP_DISABLE, sdp_seq_len, MSG_INFO_SDP_UNLOCK,
                                       MSG_INFO_SDP_UNLOCK_DONE_US);
    eeprom28c_wait_for_sdp_completion(handle);   // <-- DO NOT copy into the erase
}
```

**The shared emitter to reuse** (`eeprom_28c.cpp:314-330`) — the window
`tools/check_no_log_in_sdp_window.py` scans, so **no `LOG_*` may be added inside it**; any reporting
belongs at the erase call site, mirroring the timed wrapper:

```c
static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length) {
    rurp_set_data_output();
    for (size_t i = 0; i < length; i++) {
        handle->firestarter_set_data(handle, sequence[i].address, sequence[i].byte);
    }
}
```

**The timed wrapper** (`eeprom_28c.cpp:416-428`) — logging here is BY DESIGN (D-12/D-14) and its body
must never become a third scanned window:

```c
static void eeprom28c_emit_sdp_sequence_timed(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length,
                                               uint8_t emitted_msg_id, uint8_t done_us_msg_id) {
    LOG_ID(emitted_msg_id);
    uint32_t sdp_emit_start_us = micros();
    eeprom28c_emit_command_sequence(handle, sequence, length);
    uint32_t sdp_emit_us = (uint32_t)(micros() - sdp_emit_start_us);
    LOG_ID_U32(done_us_msg_id, sdp_emit_us);

    uint32_t sdp_tblc_budget_us = (uint32_t)length * AT28C_TBLC_MAX_US;
    if (sdp_emit_us > sdp_tblc_budget_us) {
        LOG_WARN_ID_U32(MSG_WARN_SDP_TBLC_EXCEEDED, sdp_emit_us);
    }
}
```

**The six-pair sequence, already in-tree twice.** `firestarter/include/flash_utils.h:34-41` (read-only;
FIX-04 frozen) is the byte oracle — do **not** retype the bytes, and do **not** reference this table
from `eeprom_28c.cpp` (internal linkage per TU ⇒ a third 30 B `.data` copy, A2):

```c
    const byte_flip_t FLASH_ERASE[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x80},
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x10},
    };
```

**The local table convention, if a `.data` table is chosen anyway** (`eeprom_28c.cpp:145-152`) — note
the load-bearing `extern` declaration that grants external linkage so native tests can pin the
**production** array, and that this form costs **+30 B RAM** (measured):

```c
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

**Constant convention for `tEC`** (`eeprom_28c.cpp:53`): `#define AT28C_TWC_MAX_MS 10`. A new
`#define AT28C_TEC_MAX_MS 20` follows it verbatim in form and placement.

**⚠ ANTI-PATTERN — excerpt it so an executor recognises it on sight.**
`flash_5v_page_erase_execute` (`flash_5v_page.cpp:198-230`) is the **12 V-on-OE hardware path**. It sits
in the file the executor is already editing for ERASE-02. **It must not be copied.** Zero occurrences of
`firestarter_set_control_register`, `CTRL_VPE`, `CTRL_VPP_REGULATOR_ENABLE`, `rurp_chip_enable` or
`rurp_chip_disable` may appear in `eeprom28c_erase_execute`'s brace-matched body:

```c
void flash_5v_page_erase_execute(firestarter_handle_t* handle) {
    uint32_t address;
    address = mem_util_remap_address_bus(handle, 0, READ_FLAG);
    handle->firestarter_set_address(handle, address);
    rurp_chip_disable();
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE, 0);
    delay(2);
    //^CE -> LOW
    rurp_chip_enable();
    //^OE -> 12v
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE, 1);
    delay(2);
    ...
}
```

---

### `firestarter/src/proms/eeprom_28c.cpp:517-519` (ERASE-01) and `flash_5v_page.cpp:87-89` (ERASE-02)

Both are the identical three-line block. Pure deletion; no analog needed. Verbatim, current:

```c
// eeprom_28c.cpp:517-519 (tail of eeprom28c_write_init, immediately after the
// LOG_WARN_ID(MSG_WARN_SDP_UNLOCK_SKIPPED) arm at :543)
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}
```

```c
// flash_5v_page.cpp:87-89 (tail of flash_5v_page_write_init, immediately after
// the FLAG_CAN_ERASE / FLAG_SKIP_ERASE block at :79-86)
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}
```

**Do not touch** the surrounding `flash_5v_page_write_init` erase block (`:79-86`) — and do **not** add
its counterpart to `eeprom28c_write_init` (D-07 wants erase standalone):

```c
        if (is_flag_set(FLAG_CAN_ERASE)) {
            if (!is_flag_set(FLAG_SKIP_ERASE)) {
                flash_5v_page_erase_execute(handle);
            } else {
                LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);
            }
        }
```

Leave a replacement comment naming D-07 and stating `FLAG_SKIP_BLANK_CHECK` is now unread on this
protocol. Keep `eeprom28c_write_init`'s signature and its SDP emit/wait call sites byte-unchanged —
`check_no_log_in_sdp_window.py` brace-matches this function as a rename tripwire and fails **closed**.

---

### `firestarter_app/firestarter/database.py:617-622` (ERASE-03 host half) + `:588-616` (ERASE-07)

**Analog: the algorithm-5 rationale in the same comment block, `:580-586`** — this is the half that
STAYS, and it is the voice/shape the corrected algorithm-13 paragraph must match (a live
hardware-hazard argument, stated with its scope):

```python
        # Algorithm 5 (flash4) — FIX-01a / T-93-CANERASE: flash4 auto-erases per
        # page during the page-write; no separate 12V bulk erase is needed or
        # safe. Setting FLAG_CAN_ERASE for 0x05 routes firmware
        # flash4_write_init → flash4_erase_execute which asserts
        # CTRL_VPP_REGULATOR_ENABLE on a 5V-only chip (12V on a 5V part —
        # hardware-damage hazard). Scope: algorithm==5 only; the 0x07 and
        # 0x0D paths are unaffected by this particular exclusion.
```

**The edit site, verbatim current (`:617-622`)** — the change is `(5, 13)` → `(5,)` on **line 620**:

```python
        simple_flags = 0
        algo = programmer_data["algorithm"]  # already computed above from protocol-id
        if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
            if algo not in (5, 13):
                simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE is 0x02
        programmer_data["flags"] = simple_flags
```

**The two false sentences to correct, verbatim** (grep criteria: both counts → 0):
- `:588-592` — *"…has no erase operation at\n # all, so advertising FLAG_CAN_ERASE for these 84 chips is a false\n # capability statement."*
- `:601-603` — *"…the 0x0D firmware path genuinely never reads\n # FLAG_CAN_ERASE — that part of the old note remains true — …"*

**Reversal-record voice pattern to copy** (`:596-598`, the existing header of the paragraph being
corrected). This phase's correction is the *fourth* recorded reversal and must use the same
mechanism-corrected/intent-satisfied framing:

```python
        # REVERSAL RECORD (Phase 121 D-12, third recorded reversal this
        # phase after 119 D-18 / 120 D-20): this line previously carried a
        # D-03 note stating that leaving the flag SET on 0x0D was
        # firmware-inert and "must stay unchanged." D-12 REVERSES that
        # POLICY, not the FACT: ...
```

The same in-firmware precedent exists at `eeprom_28c.cpp:219-220`: *"record this as
mechanism-corrected, intent-satisfied — never as failed."*

---

### `firestarter_app/firestarter/chip_test.py` (G-2 + the Pitfall-4 plan ripple)

**Analog: the `_PROTOCOL_FLASH4` reason arm in the same `else:` block** — a one-line, family-fact
reason with no flag name. Current false 0x0D arm, verbatim (`:745-750`), inside the arm at `:723`:

```python
        if protocol == _PROTOCOL_FLASH4:
            reason = "flash4 (0x05) auto-erases per page; no separate erase op"
        elif etype == "UV-EPROM":
            reason = "UV-EPROM has no electrical erase (UV light only)"
        elif protocol == _PROTOCOL_EEPROM_28C:
            # ...DEVTEST-01 requires the FAMILY FACT: protocol 0x0D and
            # the 28C family simply has no erase operation, ever -- never
            # the flag name.
            reason = (
                "protocol 0x0D (28C family) has no erase operation; "
                "each page write auto-erases internally"
            )
```

After ERASE-03 the `elif protocol == _PROTOCOL_EEPROM_28C:` arm becomes **unreachable** for
algorithm-13 rows (they now satisfy `can_erase and protocol != _PROTOCOL_FLASH4` at `:723`). The
planner must decide explicitly: delete the arm, or keep it as a defensive fallthrough with corrected
text. Same for the module constant comment at `:306-311`, which asserts *"has no erase operation at
all"*, and for `_PROTOCOL_EEPROM_28C` itself (`:312`) which may become unused → **ruff F401/F841 risk**.

**The three coupled sites (all in this file), verbatim:**
```python
    can_erase = bool(prog.get("flags", 0) & FLAG_CAN_ERASE)                          # :572
    erase_is_executable = can_erase and protocol != _PROTOCOL_FLASH4 and write_execute  # :615
    if can_erase and protocol != _PROTOCOL_FLASH4:                                    # :723
```

**How a prior phase funded exactly this plan-shape change — the analog the planner should budget from:**
`tests/test_chip_test_blank_check_order.py` (quick task **260807-kaq**) is a whole dedicated test module
authored for one `derive_plan` placement change, written and **observed RED before the fix landed**. Its
docstring (`:7-32`) enumerates all four placement cases against the real on-disk DB, and its fixture
idiom is module-level:

```python
_REAL_DB = EpromDatabase(skip_local_override=True)
_CHIP_ERASABLE = "M8720"      # protocol 0x08, EEPROM, FLAG_CAN_ERASE set
_CHIP_UV = "AM27512"          # UV-EPROM
_CHIP_AUTO_ERASE_28C = "AT28C256"
```

**Budget signal for the planner:** one dedicated module + a TDD-RED observation per plan-shape change,
not an incidental assertion tweak. Phase 153 changes the plan shape on **all 84** algorithm-13 rows.

---

### `firestarter_app/firestarter/cli_handlers.py:797-804` (G-1)

**Analog: the C-8 comment immediately above it (`:788-796`)**, which already establishes the pattern of
*scoping a warning and recording why it does not extend* — and whose own reasoning now inverts:

```python
    # this line printed. RESEARCH C-8: this arm deliberately does NOT extend
    # to `-b`/`--no-blank-check` — since Phase 92 that flag skips only the
    # blank check, not the erase, and it is genuinely useful on a non-blank
    # 0x0D part precisely because there is no erase to make the part blank;
    # a "nothing to skip" line on that flag would be a false statement. ...
    if skip_erase and is_protocol_0x0d:
        click.echo(
            f"{eprom.upper()}: --skip-erase has nothing to skip on this "
            "chip's protocol — the 28C family (protocol 0x0D) has no erase "
            "operation at all; each page write auto-erases internally. "
            "Proceeding with a normal write."
        )
```

**Correct the text, keep the arm** (`--skip-erase` is still vacuous on the *write path*), and per
Pitfall 5 add **no** second warning for `-b`. Note the string is pinned by
`tests/test_write_skip_erase_0x0d.py` leg 1, and the message uses an em-dash — match it.

---

### `firestarter_app/firestarter/ic_layout.py:578-586` — CONFIRMED: NO EDIT NEEDED

RESEARCH.md's ERASE-06 conclusion is **confirmed against the code**. The block keys on `etype` only and
already returns `yes` for every algorithm-13 row; restoring the wire flag makes the two axes agree with
zero change here:

```python
        # D-02: "Can be erased" derived from electrical.type, NOT protocol_id.
        # EEPROM/Flash/EEPROM → electrically erasable; UV-EPROM → UV-only;
        # SRAM → omit row (volatile); absent/unknown → omit row (safe fallback).
        if etype in ("EEPROM", "Flash/EEPROM"):
            output_data["can_erase_str"] = "yes (electrically erasable)"
        elif etype == "UV-EPROM":
            output_data["can_erase_str"] = "no (UV erase only)"
        # SRAM and absent/unknown: no can_erase_str row
```

**Plan ERASE-06 as an assertion task.** Note the identical `("EEPROM", "Flash/EEPROM")` membership test
appears in `database.py:619` — the two axes are structurally aligned already, which is the fact the new
`test_ic_layout.py` leg pins in both directions.

---

### `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:310-318` — MANDATORY INVERSION

**Current, verbatim (must become false):**

```c
/* Case group 4 — DEVTEST-01's firmware half and the 0x0D gaps. */
void test_case_group4_0x0d_erase_and_chip_id_null_main_devtest01(void) {
    firestarter_handle_t h_erase = make_handle(0x0D, 0, CMD_ERASE);
    configure_memory(&h_erase);
    TEST_ASSERT_NULL_MESSAGE(h_erase.firestarter_operation_main,
        "Case group 4 (DEVTEST-01 fw half): CMD_ERASE on 0x0D must leave firestarter_operation_main "
        "NULL -- configure_eeprom28c has no case CMD_ERASE: arm, so this is now refused by the "
        "generic op-layer guard rather than silently reporting OK having erased nothing ('dev test' "
        "phantom erase)");
```

**Invert onto the shape of Case group 3 in the same file (`:299-307`)** — a positive `NOT_NULL` plus two
`NULL` assertions on init/end, which is exactly right for the new arm (it assigns neither):

```c
    TEST_ASSERT_NOT_NULL_MESSAGE(h_lock.firestarter_operation_main,
        "Case group 3 (LOCK-02): CMD_SDP_LOCK on 0x0D must set a non-NULL operation_main");
    TEST_ASSERT_NULL_MESSAGE(h_lock.firestarter_operation_init,
        "Case group 3 (LOCK-02, F-T correction): CMD_SDP_LOCK's init is NULL, same correction as "
        "unlock above");
    TEST_ASSERT_NULL_MESSAGE(h_lock.firestarter_operation_end,
        "Case group 3 (LOCK-02, F-T correction): CMD_SDP_LOCK's end is NULL, same correction as "
        "unlock above");
```

The `CMD_CHECK_CHIP_ID` half of Case group 4 (`:320+`) stays **NULL** — do not touch it. Consider
splitting the function so its name stops claiming both are NULL.

---

### `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1448-1473` — MANDATORY INVERSION (Case 25)

**Current, verbatim.** Its four-beat shape — precondition → drive → response code → frame id — transfers
directly to the new "erase now dispatches and emits the six-write stream" case:

```c
void test_case25_cmd_erase_on_0x0d_refused_end_to_end_devtest01(void) {
    firestarter_handle_t h = make_lock_handle(SDP_BUS_CONFIGS[0]); /* protocol 0x0D, ctrl_flags 0 */
    h.cmd = CMD_ERASE;
    configure_memory(&h);
    TEST_ASSERT_NULL_MESSAGE(h.firestarter_operation_main,
        "Case 25 precondition: configure_eeprom28c must leave CMD_ERASE's main NULL on 0x0D -- no "
        "case CMD_ERASE: arm exists in its switch");
    reset_register_cache(0x00, 0x00, 0x00);
    clear_strobes();

    bool still_in_progress = op_execute_simple_operation(&h);

    TEST_ASSERT_FALSE_MESSAGE(still_in_progress, "...");
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "Case 25 (DEVTEST-01 fw half): CMD_ERASE on 0x0D must now set RESPONSE_CODE_ERROR ...");

    std::vector<uint8_t> ids;
    sdp_captured_frame_ids(&ids);
    TEST_ASSERT_TRUE_MESSAGE(sdp_ids_contains(ids, (uint8_t)MSG_ERR_NOT_SUPPORTED),
        "Case 25 (DEVTEST-01 fw half): MSG_ERR_NOT_SUPPORTED must appear in the captured frame ids "
        "for a CMD_ERASE attempt on protocol 0x0D");
}
```

**Inversion, all four beats kept positive:** `NOT_NULL` precondition; `RESPONSE_CODE_OK`;
`sdp_ids_contains(... MSG_ERR_NOT_SUPPORTED)` → `TEST_ASSERT_FALSE_MESSAGE` (negative-presence, keep it).

---

### `test_eeprom28c_sdp.cpp` — new erase stream cases

**Analog: `test_case19_lock_diverges_from_chip_erase_at_exact_index` (`:1108-1124`).** Copy it
verbatim in shape. **Rule, load-bearing: assert an EXACT index, never `!= -1`.**

```c
void test_case19_lock_diverges_from_chip_erase_at_exact_index(void) {
    firestarter_handle_t h = make_lock_handle(SDP_BUS_CONFIGS[0]); /* AT28C256 */
    drive_lock_op(&h, 0x00);
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "Case 19: lock-stream snapshot must not overflow");
    sdp_strobe_t lock_snapshot[64];
    int lock_len = sdp_snapshot(lock_snapshot, 64);

    firestarter_handle_t h_erase = make_sdp_handle(SDP_BUS_CONFIGS[0]);
    drive_reference_emitter(&h_erase, FLASH_ERASE, sizeof(FLASH_ERASE) / sizeof(FLASH_ERASE[0]), 0x00);
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), "Case 19: erase-reference drive must not overflow");

    int div = sdp_first_divergence(lock_snapshot, lock_len);
    TEST_ASSERT_EQUAL_MESSAGE(27, div,
        "Case 19 (...): the lock stream diverges from the chip-erase stream at EXACTLY index 27 ...");
}
```

**Harness primitives available (all already in this suite):** `make_lock_handle` / `make_sdp_handle` /
`drive_lock_op` / `drive_reference_emitter` / `sdp_snapshot` / `sdp_first_divergence` /
`strobe_overflowed` / `clear_strobes` / `sdp_captured_frame_ids` / `sdp_ids_contains` /
`reset_register_cache`, plus `SDP_BUS_CONFIGS[0..3]` (AT28C256, 28C64, 2816, 28C512).

**Mandatory sequencing note from Case 18's own comment (`:1074-1081`):** `drive_reference_emitter`
calls `clear_strobes()`, so the production op's stream must be **snapshotted first**.

**Cases 1-5 (`*_stream_matches_fixed`) must stay green UNMODIFIED** — they are ERASE-01's
write-stream non-regression oracle.

---

### `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — new no-VPP case

**Analog: `test_eeprom28c_blank_check_configure_no_vpp` (`:202-209`).** Two asserts, one idiom. Copy it
with `CMD_BLANK_CHECK` → `CMD_ERASE`:

```c
void test_eeprom28c_blank_check_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(CMD_BLANK_CHECK);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x0D CMD_BLANK_CHECK");
    assert_no_vpp_in_recording(
        "configure_eeprom28c CMD_BLANK_CHECK must NOT set any VPP-enable CTL bit");
}
```

**Registration pattern** (`:396-399`) — the new `RUN_TEST` goes in the existing 5V-only block, and
`main`'s registration list must be updated or the case never runs:

```c
    /* 5V-only proof: no VPP-enable CTL bit for any command in the configure phase */
    RUN_TEST(test_eeprom28c_read_configure_no_vpp);
    RUN_TEST(test_eeprom28c_write_configure_no_vpp);
    RUN_TEST(test_eeprom28c_blank_check_configure_no_vpp);
```

Note this covers only the **configure** phase. The GATE-03 control for the erase *body* is the
brace-matched negative source scan (Pitfall 2), not this case — plan both.

---

### `firestarter_app/tests/test_database_conversion.py:98-117` — MANDATORY INVERSION

**Current, verbatim (assertion at `:117`):**

```python
def test_convert_at28c256_flash_eeprom_flag_can_erase_cleared(
    db: EpromDatabase,
) -> None:
    """REVERSAL RECORD (Phase 121 D-12): this test previously asserted AT28C256
    (Flash/EEPROM, routed to 0x0D) carried FLAG_CAN_ERASE, ...
    D-12 clears the flag for protocol 0x0D at the source (`database.py`), so this test now
    asserts the bit is CLEAR.
    """
    full = db.get_eprom("AT28C256")
    assert full is not None
    out = db.convert_to_programmer(full)
    assert out["flags"] & FLAG_CAN_ERASE == 0
```

**Invert onto the positive-assert shape already in the same file (`:82-86`):**

```python
    out = db.convert_to_programmer(full)
    assert out["flags"] & FLAG_CAN_ERASE
```

**Rename the function** (its name states the outcome) and extend the docstring with the *second*
reversal, matching the existing REVERSAL RECORD voice.

**Two negative controls stay byte-unchanged and green** — cite them in the plan as the scope proof:
- `test_convert_uv_eprom_no_flag_can_erase` (`:89-95`, M27C512 UV-EPROM)
- `test_convert_w29c040_no_flag_can_erase` (`:120-131`, algorithm 5 — the still-valid hazard exclusion)

---

### New host leg — exhaustive 84-of-746-row flag assertion

**Analog: `tests/test_page_size_invariants.py`.** Two patterns to copy.

**(a) The nested selector, with its anti-vacuity warning (`:125-137`)** — a top-level scan finds nothing
and makes every downstream assertion pass vacuously:

```python
def _select_0x0d_chips(db: dict) -> list[tuple[str, dict]]:
    """Select every (manufacturer, chip) pair with programming.algorithm == 13.

    The DB shape is {manufacturer: [chip, ...]}; a top-level scan on db
    (rather than this nested per-chip access) finds nothing and would make
    every downstream assertion pass vacuously.
    """
    selected = []
    for mfr, chips in db.items():
        for chip in chips:
            if chip["programming"]["algorithm"] == _ALGORITHM_0X0D:
                selected.append((mfr, chip))
    return selected
```

**(b) The exhaustive-count leg, with the 746 total re-asserted in the same test (`:256-266`)** — this
total-row assert is what makes the count meaningful, and offenders are named in the message:

```python
def test_exactly_20_page_size_carriers_across_all_746_rows() -> None:
    db = _load_db(_DB_FILE)
    total_rows = sum(len(chips) for chips in db.values())
    assert total_rows == 746, f"expected 746 total rows, found {total_rows}"
    carriers = _select_page_size_carriers(db)
    assert len(carriers) == 20, (
        f"expected exactly 20 page_size carriers (18 native + 2 curated) "
        f"across all 746 rows, found {len(carriers)}: "
        f"{[(m, c.get('part_number', '?')) for m, c in carriers]}"
    )
```

Target assertion: **exactly 84** rows gain `FLAG_CAN_ERASE`, **0** non-13 rows change, total 746. Note
this suite reads the raw JSON via `_load_db(_DB_FILE)`, whereas the flag needs
`convert_to_programmer` — so the new leg composes pattern (a)'s selector with
`test_database_conversion.py`'s `db.convert_to_programmer(full)` call. Rows key on `part_number` (there
is no `name` key).

---

### `firestarter_app/tests/test_chip_test_blank_check_order.py:121-129` — MANDATORY INVERSION (case 3)

**Current, verbatim:**

```python
def test_at28c256_blank_check_is_na_with_family_fact_reason():
    """Case 3: protocol 0x0D auto-erases per page during write -- no step
    in this plan can ever leave the device blank, so blank-check flips to
    NA at its original position (index 2) with a family-fact reason, never
    the internal flag name FLAG_CAN_ERASE."""
    plan = derive_plan(_CHIP_AUTO_ERASE_28C, _REAL_DB, write_scope="full")
    ops = [s.op for s in plan.steps]
    assert ops.index(OP_BLANK_CHECK) == 2

    blank_check_step = next(s for s in plan.steps if s.op == OP_BLANK_CHECK)
    assert blank_check_step.supported is False
```

**Invert onto case 1 in the same file** (`test_m8720_...`, the "executable erase exists ⇒ blank-check
moves after erase and before the SDP leg" leg) — AT28C256 now behaves like M8720. Case 2's
`write_scope="none"` leg (`:98-105`) also moves: `locked_ops` gains `erase` for AT28C256:

```python
    locked_ops = {op for op, _reason in plan.locked_destructive}
    assert locked_ops == {"write", "verify", "erase"}
```

Case 4 (`test_am27512_uv_...`, `:108-118`) stays byte-unchanged as the negative control.

---

### `firestarter/scripts/check_size_baseline.py` + `scripts/baseline/size_baseline.json` (ERASE-08)

**Analog: `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES` (`:251-323`), the most recent named exemption.**
Copy its constant-comment structure exactly. The required elements, all present in that block:

1. Ordinal + scope in the first sentence: *"The THIRD, SEPARATELY-NAMED, SHA-attributed flash
   exemption, in bytes, ADDED to each target's allowance alongside …"*
2. Phase + decision attribution: *"Phase 151 (LOCK-02, D-01/D-02)."*
3. The single-consumer property: *"the single place this literal lives is `_merge05_flash_allowance()`
   below."*
4. **"What the N bytes ARE"** — an itemised, per-commit breakdown with SHAs and a transcript pointer:
   *"(commit 32c32e7); … (commit f66d817); … (commit 8db7e55); … (commit 0444b1c); … (commit
   3ff9f34). No new byte_flip_t table was needed for either family — both reuse
   FLASH_ENABLE_ID/FLASH_DISABLE_ID verbatim, measured at exactly 0 B, a zero-byte item recorded rather
   than omitted."*
5. A **WHY a named exemption rather than …** rejection list (see the RAM constant `:325-367` for the
   fullest form: not a general loosening, not folded into another constant, not shrunk to fit).
6. The Evidence-Ceiling sentence, which Phase 153 must repeat verbatim-in-kind (`:246-248`):
   *"The change this constant funds is **software-proven and unvalidated on silicon** (Evidence
   Ceiling, v1.32 PROJECT.md): no AT28C part was involved in measuring it, and the figure says nothing
   about runtime behaviour on real hardware."* — this doubles as ERASE-09's grep target.
7. A tripwire-still-armed sentence naming the specific test leg.

```python
MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96          # :191  Phase 145
MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = 210     # :249  Phase 149
MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES = 288   # :323  Phase 151
MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2   # :367  Phase 149 (RAM, fully consumed)
```

Consumers: `_merge05_flash_allowance()` (`:508-510`) and `_merge05_ram_allowance()` (`:525`).
A `MERGE05_ERASE_*_EXEMPTION_BYTES` must be added to **both** the constant block and the relevant
allowance function, and the docstring at `:480-481`/`:538-542` enumerates the stacked exemptions and
must be extended.

**`size_baseline.json` `merge05_clause` shape (`:23`, leonardo; `:28`/`:33` uno-class).** Three clauses,
one per target, each an in-place-extended single string. Its mandatory beats:
- `"ADJUDICATED AND ADMITTED (… + …), not laundered."`
- the printed allowance expression, verbatim: `` `+594<=594=band0+exempt96+seam210+lock288` `` for flash
  and `` `+2<=2=seam2` `` for RAM → a fourth term appends here
- **`WHAT WAS NOT CHANGED:`** — BASE-01 not re-anchored (its byte-unchanged figures **recited**:
  uno 24824 / uno328pb 24874 / leonardo 26906, RAM 1573/1579/2014); band literals untouched; no fix
  shrunk; the archived v1.23 MERGE-05 requirement not edited
- **`TRIPWIRE STILL ARMED:`** — *"proven at 151-10 by four re-planted fixtures … on a NEW `*_v151*`
  fixture family, each re-derived from allowance+1 and **observed** to fail, not merely asserted to fail."*
- the Caterina paragraph, stated as a **distinct** figure: *"28672-27500 = 1172 B … this MERGE-05
  clause and that budget are never the same figure and must not be confused."*

Also `meta.roadmap_cross_check` (`:14`) gets a superseding entry, and `native_envs` must move in the
**same** revision (Pitfall 7 — default mode requires byte identity on `cases`/`suites` too; currently
163 cases / 17 suites in both `native` and `native_nodevtools`, with `envs_agree: true`).

---

### `firestarter/tests/test_check_size_baseline.py` + a new `*_v153*` fixture family

**Analog: the `*_v151*` family and the Plan 151-10 severance record in the module docstring
(`:284-340`).** **Do NOT edit the `*_v151*` family** — sever onto a new one; the `*_fullflash*` family
is the precedent for *retired, not repointed, keep-not-delete*.

**The 13-file family to model on, verbatim from disk (`firestarter/tests/fixtures/`):**

```
captured_build_v151_{uno,uno328pb,leonardo}.log            # cold rm -rf + one `pio run -e <env>` capture
merge05_base01_anchor_v151_{uno,uno328pb,leonardo}.log      # SYNTHETIC: `used` set to BASE-01's anchor
merge05_lock_status_v151_{uno,uno328pb,leonardo}.log        # the exemption's own admission proof
planted_size_baseline_policy_leonardo_growth_v151.log       # 27501 = allowance+1
planted_size_baseline_policy_uno_over_band_v151.log         # 25483 = allowance+1
planted_size_baseline_policy_ram_moved_v151.log             # 1576  = RAM tolerance+1
planted_size_baseline_flash_regression_v151.log             # 28012 = the standing +512 B offset
```

**The severance-record pattern the docstring must carry** (copy this structure): plan id + what the
exemption is + the measured figure and its transcript pointer + which family is *retired vs repointed*
+ the file-by-file inventory with each plant's **single cause and its one-byte-past-the-ceiling role,
never its absolute figure (D-18)** + the explicit list of legs repointed + the legs deliberately
**UNTOUCHED** and why (*"both assert at fixed, sub-allowance deltas … so the widened allowance changes
nothing either leg asserts"*).

**Eight legs were repointed in 151-10** — the same set is the candidate list for `v153`:
`test_clean_avr_all_three_envs_pass`, `test_default_mode_is_unchanged_by_the_new_flag`,
`test_planted_flash_regression_flips_checker_to_failure`,
`test_baseline_seam_precedence_flips_clean_log_to_fail`,
`test_policy_merge05_fires_on_uno_class_over_band`, `test_policy_merge05_fires_on_leonardo_growth`,
`test_policy_merge05_fires_on_ram_move`, and Arm 2 of
`test_policy_merge05_admits_the_documented_defect_fix` (+ a new Arm reading the three
`merge05_*_v153_*.log`). `test_base01_is_not_re_anchored_by_the_new_exemption` is **strengthened, not
repointed** — it reads BASE-01 and the checker source directly, never a fixture.

**Do not author a criterion of the form "tests byte-unchanged"** — the standing lesson is that
re-anchoring reddens four legs unless you sever onto a new fixture family.

---

## Shared Patterns

### The `case CMD_X:` dispatch arm (firmware)
**Source:** `eeprom_28c.cpp:224-226` (local) — cross-checked against `flash_5v_page.cpp:47-49`,
`flash_intel.cpp:92-94`, `flash_nor_unlock.cpp:39-42`.
**Apply to:** the one new `CMD_ERASE` arm.
```c
        case CMD_SDP_LOCK:
            handle->firestarter_operation_main = eeprom28c_sdp_lock_execute;
            break;
```
`configure_eeprom28c` assigns no init/end before its switch, so — unlike `flash_nor_unlock.cpp:59-62` —
the new arm nulls nothing. **No `default:` arm** (`eeprom_28c.cpp:208-220` records why).

### Cited-constant + decision-attributed comment (both repos)
**Source:** `eeprom_28c.cpp:145-152` (`[CITED: …]` above a table), `check_size_baseline.py:246-248`
(the Evidence-Ceiling sentence), `database.py:580-586` (scope-qualified rationale).
**Apply to:** every new constant, table and reason string in this phase. Cite AN 0544B Rev. 0544B-10/98
by name at the erase body, state the AT28C256 DS20006386B Table 6-1 hardware path as the thing
**deliberately not** implemented, and name D-07.

### Reversal-record voice
**Source:** `database.py:596-598` (host) and `eeprom_28c.cpp:219-220` (firmware): *"record this as
mechanism-corrected, intent-satisfied — never as failed."*
**Apply to:** ERASE-07's comment correction, the `test_database_conversion.py` docstring, and the phase
record. This is the **fourth** recorded reversal in the D-12 chain.

### Exact-index / no-vacuity test discipline
**Source:** `test_eeprom28c_sdp.cpp:1179` (`TEST_ASSERT_EQUAL_MESSAGE(27, div, …)`),
`test_page_size_invariants.py:127-131` (the nested-scan anti-vacuity docstring),
`test_chip_test_blank_check_order.py:30-32` (observed RED before the fix landed).
**Apply to:** every new test leg. Never `!= -1`; never a top-level DB scan; every new gate leg must be
**observed** to fail on a planted violation before it is trusted.

### Negative source-scan as the primary safety control
**Source:** the pattern exists as tooling (`tools/check_no_log_in_sdp_window.py`'s brace-matching), not
as an in-tree assertion for this shape — so this is a **new leg with a tooling analog only**.
**Apply to:** the GATE-03 control. Brace-match `eeprom28c_erase_execute` and assert **0** occurrences of
`CTRL_VPE`, `CTRL_VPP_REGULATOR_ENABLE`, `firestarter_set_control_register`, `rurp_chip_enable`,
`rurp_chip_disable`. `check_dispatch.py` structurally cannot catch a handler-body register write; this
scan is the only real control, and it must be **observed** to fail on a planted `CTRL_VPE_ENABLE`.

### Host test fixture idiom
**Source:** `test_chip_test_blank_check_order.py:48` — `_REAL_DB = EpromDatabase(skip_local_override=True)`
at module scope, with named `_CHIP_*` constants each carrying a one-comment justification.
**Apply to:** every new host leg (`test_ic_layout.py`, the exhaustive 84-row leg).
Run host tests with `-o addopts=""` (`addopts` is `-ra -q`; doubling `-q` hides the count line).

---

## No Analog Found

| File / work item | Role | Data Flow | Reason |
|---|---|---|---|
| `firestarter/doc/PROTOCOLS.md:305` §1.6 erase-model prose | doc | — | Prose; no code analog. `test_dispatch_mirror.py` parses only §0's table, so **nothing gates this paragraph** — the plan must make the correction an explicit task with a grep criterion. |
| `firestarter_app/doc/protocol-id.md:22` | doc | — | Prose, ungated. |
| `.planning/PROJECT.md:44-45`, `:80-88`; `.planning/ROADMAP.md:37` (D-15) | planning record | — | Meta-repo records. `ROADMAP.md:163` is already amended; these three are not. |
| A `PROGMEM` `byte_flip_t` table + per-entry copy (if that form is chosen) | firmware data | — | **No in-tree precedent.** Every existing sequence table is `.data`; `eeprom28c_emit_command_sequence` dereferences `sequence[i].address` directly. Choosing this form means writing a second emitter with no analog — a reason to prefer the six-inline-writes form. |
| The negative brace-matched source scan for the erase body | test/gate | — | Tooling analog only (`check_no_log_in_sdp_window.py`); no existing *test* asserts the absence of a control-register write inside a named function body. New leg. |

---

## Planner Notes

1. **`eeprom_28c.cpp` is ONE task, not two waves.** ERASE-01's deletion and ERASE-03/04's addition are
   in the same file under one-writer-per-file.
2. **Four inversions are mandatory.** Never author "tests byte-unchanged" / "git diff --quiet" over a
   `test/` path. Each inversion must keep a **positive** assertion.
3. **Wave 0 owes a decision, not code:** which erase supply form. A `.data` table costs **+30 B RAM**
   against a fully-consumed 2 B RAM exemption. A flash exemption is needed regardless of form
   (leonardo flash headroom is **0 B**).
4. **Budget the `dev test` plan-shape ripple explicitly** (Pitfall 4): three coupled sites in
   `chip_test.py` (`:572`, `:615`, `:723`), 84 rows affected, and the precedent cost is a dedicated
   test module observed RED first (quick task 260807-kaq).
5. **`_PROTOCOL_EEPROM_28C` may become unused** after the reason-arm correction — ruff `select` is
   `[E,F,I,UP]`, so an unused module constant is not flagged but an unused import is. Check.
6. **Two distinct size figures**, never conflated: MERGE-05 leonardo flash headroom **0 B**; Caterina
   cliff headroom **1172 B, UNGUARDED** (past 28672 B bricks the USB bootloader).

## Metadata

**Analog search scope:** `firestarter/src/proms/`, `firestarter/include/`, `firestarter/test/native/avr/`,
`firestarter/scripts/`, `firestarter/tests/fixtures/`, `firestarter_app/firestarter/`,
`firestarter_app/tests/`
**Files read this session:** 16 (targeted, non-overlapping ranges)
**Pattern extraction date:** 2026-08-21
