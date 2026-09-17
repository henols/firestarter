# Phase 194: Real Page Size Reaches the Firmware — Pattern Map

**Mapped:** 2026-09-15
**Files analyzed:** 17 (14 MODIFY, 3 CREATE; 2 of the 14 are build outputs, never hand-edited)
**Analogs found:** 15 / 17 (2 need no analog — they are regenerated artefacts)
**Sweep tool:** `/usr/bin/grep` only. The devcontainer `grep` is ugrep and honours `.gitignore`.
**Tracked-source gate:** every analog path below was confirmed with `git ls-files` in its own
repository (meta, `firestarter_fw`, `firestarter_app`). No gitignored mirror path appears here.

---

## File Classification

Repo column: `M` = meta (`/workspaces`), `A` = `firestarter_app`, `F` = `firestarter_fw`.

| Repo | New/Modified File | Action | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|---|---|
| M | `tools/catalog/messages.toml` | MODIFY | config (catalog) | transform (codegen input) | the `MSG_ERR_FL4_BOOT_BLOCK_LOCKED` stanza at `:670-676` | exact |
| M | `.planning/v1.39/<27-row record>.md` | CREATE | doc artefact | batch record | `.planning/v1.33/sweep-outcome-record.md` | exact |
| A | `tools/build_db.py` | MODIFY | generator / transform | batch (XML → JSON) | its own two arms: `:378-384` (fatal) and `:697-715` (provenance emit) | self |
| A | `firestarter/data/chip_database.json` | REGENERATE | build output | batch | **none — generated**, see §Generated Artefacts | n/a |
| A | `firestarter/exceptions.py` | MODIFY | model (exception) | request-response | `ChipNotImplementedError`, `exceptions.py:74-89` | exact |
| A | `firestarter/eprom_operations.py` | MODIFY | service (operator) | request-response | `require_acknowledged(...)` call at `:2002-2007` | exact |
| A | `firestarter/cli_handlers.py` | MODIFY | controller (CLI) | request-response | `jp5_gate.confirm_or_refuse` at `:758-759`; `map_typed_errors` `:186-223` | exact |
| A | new pre-flight predicate (see §Assignments) | CREATE-or-inline | utility (pure predicate) | request-response | `firestarter/flash4_erase_gate.py` (inverted) + `jp5_gate.require_acknowledged` `:84-107` | exact |
| A | `firestarter/database.py` | MODIFY (delete only) | service | transform | §Comment-Deletion Boundary | n/a |
| A | `firestarter/constants.py` | MODIFY (delete only) | config | transform | §Comment-Deletion Boundary | n/a |
| A | `tests/test_page_size_invariants.py` | MODIFY | test (data gate) | batch | its own legs 4 (`:237-247`) and 6 (`:265-272`) + identity frozensets `:69-108` | self |
| A | `tests/test_vcc_margin_rail.py` | MODIFY | test (absence gate) | batch | its own `:231-241` two surviving assertions | self |
| A | `tests/golden/chip_database_field_inventory.json` | RE-DERIVE | golden | batch | its own `how_to_update` + `phase_149_update` precedent | self |
| A | `tests/test_wire_dict_equivalence.py` | MODIFY | test (golden+delta) | batch | its own 153-layer block `:238-257` and 182-layer block `:262-279` | exact |
| A | `tests/golden/wire_dict_expected_deltas_194.json` | CREATE | golden (delta layer) | batch | `tests/golden/wire_dict_expected_deltas_149.json` | exact |
| F | `src/proms/flash_5v_page.cpp` | MODIFY | handler (prom) | streaming (byte loop) | `src/proms/eeprom_28c.cpp:387-418` + `:455` | exact (one divergence) |
| F | `include/messages.h` | REGENERATE | build output | — | **none — generated** | n/a |
| F | `src/json_parser.c`, `include/firestarter.h` | MODIFY (delete only) | parser / model | transform | §Comment-Deletion Boundary | n/a |
| F | `test/native/avr/_shared/host_stubs_common.inc` | MODIFY | test harness | event-driven (recorder) | its own strobe recorder `:75-105` (`#define` cap + overflow flag) | exact, same file |
| F | `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` | MODIFY | test (native Unity) | streaming | its own `:185-199` fixture + `:236-274` SDP oracle; `test_val_eprom` for saturation | exact |

**Test-tree and CI attribution.** `firestarter_fw` has two test trees. Every firmware test file
above is in the **PlatformIO `test/native/avr/`** tree, which CI runs as `pio test -e native`
and `pio test -e native_nodevtools`. `test_val_5v_page` is already registered in
`platformio.ini:97` `test_filter` and `:122` include path, so **no `platformio.ini` change is
required** — extending it avoids the four-line two-env registration rule. The separate
`firestarter_fw/tests/*.py` source-scanner tree (~286 tests, also CI-run as `pytest tests/ -v`)
holds **no** file this phase touches.

---

## Pattern Assignments

### `firestarter_fw/src/proms/flash_5v_page.cpp` (handler, streaming)

**Analog:** `firestarter_fw/src/proms/eeprom_28c.cpp` — same role, same data flow, reviewed,
CI-covered. **One behavioural divergence to carry: `eeprom_28c` falls back. `flash_5v_page`
must refuse.**

**Ceiling `#define` pattern** (`eeprom_28c.cpp:28-29`, with the rationale it carries at `:24-27`):

```c
#define AT28C_PAGE_SIZE_FALLBACK 64
#define AT28C_PAGE_SIZE_MAX 512
```

`AT28C_PAGE_SIZE_MAX` is **local to the `.cpp`**, in no header — confirmed by
`/usr/bin/grep -rn "AT28C_PAGE_SIZE" firestarter_fw/`. Copy that placement: the new ceiling is a
`#define` local to `flash_5v_page.cpp`, board-invariant (**not** `DATA_BUFFER_SIZE`, which is 512
on uno/native and 1024 on leonardo).

**Validator pattern — the zero-before-power-of-two ordering** (`eeprom_28c.cpp:402-410`):

```c
static uint32_t eeprom28c_page_mask(uint16_t requested) {
    if (requested == 0) {
        return (uint32_t)AT28C_PAGE_SIZE_FALLBACK - 1;
    }
    if (requested <= AT28C_PAGE_SIZE_MAX && (requested & (requested - 1)) == 0) {
        return (uint32_t)requested - 1;
    }
    return (uint32_t)AT28C_PAGE_SIZE_FALLBACK - 1;
}
```

Copy the **test order** exactly: `requested == 0` first, because `(0 & (0-1)) == 0` is true on an
unsigned type. Do **not** copy the return-a-mask contract — a returned `0` is indistinguishable
from a legitimate 1-byte page and `0xFFFFFFFF` is the dangerous direction. Use an out-parameter
plus a `bool` success return.

**Resolve-once-in-`operation_main` pattern** (`eeprom_28c.cpp:418`, inside
`eeprom28c_write_execute`, not `write_init`):

```c
    const uint32_t page_mask = eeprom28c_page_mask(handle->page_size);
```

Both reasons hold for this file: `flash_5v_page_write_init` returns early on
`RESPONSE_CODE_ERROR` (`flash_5v_page.cpp:69-73`), and the native suite drives
`h.firestarter_operation_main(&h)` without ever calling `operation_init`
(`test_val_5v_page.cpp:263-292`).

**Mask-consumption pattern** (`eeprom_28c.cpp:455`):

```c
        bool page_end = ((address + 1) & page_mask) == 0;
```

The two sites to convert are `flash_5v_page.cpp:92` and `:100` — **two, not three**. Line 82 is
the derivation call deleted by D-06, not a modulo (`/usr/bin/grep -n "%"` on the file returns only
92 and 100 in executable code). This corrects the `:82,92,100` "three `%` sites" citation in
CONTEXT.md §canonical_refs.

**Refusal pattern — parameterless-or-scalar `LOG_ERROR_ID*` + response code + return.** Prefer the
scalar form so the rejected value is diagnosable. Closest analogs, same file family:

```c
// firestarter_fw/src/proms/eeprom_28c.cpp:181
            LOG_ERROR_ID_U32(MSG_ERR_MEM_SIZE_TOO_SMALL, (uint32_t)handle->mem_size);
// firestarter_fw/src/proms/eprom.cpp:102
    LOG_ERROR_ID_U32(MSG_ERR_PULSE_TOO_WIDE, handle->pulse_delay);
// firestarter_fw/src/proms/not_implemented.cpp:17
    LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol);
```

The in-file error+abort shape to mirror (`flash_5v_page.cpp:128-129`) is
`LOG_ERROR_ID_*(...)` followed by `handle->response_code = RESPONSE_CODE_ERROR;` and a return. With a `u16`
param the macro is `LOG_ERROR_ID_U16` — the analog is `src/operation_utils.cpp:148`
(`LOG_ERROR_ID_U16(MSG_ERR_DATA_ERR_N, (uint16_t)res)`).

**No comment is written.** The block comment at `flash_5v_page.cpp:19-26` is deleted with the function
it documents. No replacement.

---

### `tools/catalog/messages.toml` (config, codegen input) — meta repo only

**Analog:** the `MSG_ERR_FL4_BOOT_BLOCK_LOCKED` stanza, `tools/catalog/messages.toml:670-676` —
same handler prefix, same `wire_format`, single scalar param:

```toml
[[messages]]
id          = 0xBC
name        = "MSG_ERR_FL4_BOOT_BLOCK_LOCKED"
severity    = "ERROR"
format      = "boot block locked -- 0x%06lx not programmable"
params      = [{ type = "u24", render = "hex_addr" }]
wire_format = "id_frame"
```

**Ordering rule, from the file's own header (`:1-8`):** "DO NOT REORDER ENTRIES. Codegen sorts by
id ascending. The source file order is preserved for human-edit diff readability." The last ERROR
stanza is `MSG_ERR_ENERGY_CAP` at `0xBE`, `:689-698`. Insert the new `0xBF` stanza immediately
after it and before the `# ---` DATA banner at `:700`.

**Sync pattern — the whole of it, run from `/workspaces`:**

```bash
python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check
bash tools/catalog/sync_to_subrepos.sh
```

`ruff` must be on PATH or `messages.py` is written unnormalised. **No CI gate catches a forgotten
sync** — make it an explicit step with a `git status` check after it.

---

### Generated Artefacts — pattern is the regeneration, not the content

| Artefact | Regenerated by | Gate that must **re-derive**, never hand-edit |
|---|---|---|
| `firestarter_app/firestarter/data/chip_database.json` | `tools/build_db.py` (fetches the SHA-pinned minipro XML over the network; no `--xml` flag, no local fallback) | `tests/golden/chip_database_field_inventory.json` |
| `firestarter_fw/include/messages.h` | `tools/catalog/sync_to_subrepos.sh` (meta repo only) | none in CI |
| `firestarter_app/firestarter/messages.py` | same script, then `ruff format` + `ruff check --add-noqa` | none in CI |

Messages are generated **only in the meta repo**. The sub-repos carry no catalog copy, confirmed:
`firestarter_fw/tools/catalog/` does not exist and `firestarter_app/tools/catalog/` holds only
`__pycache__`.

---

### `firestarter_app/tools/build_db.py` (generator, batch)

**No lint/type analog to conform to.** `firestarter_app/tools/` is outside `ruff check`,
`ruff format --check` and the `mypy` watermark — CI scopes those to `firestarter/ tests/`. It **is**
inside the planning-citation gate. Do not invent a type/lint convention. Hold the edit to the
surrounding file's own style by hand.

**Emit-arm pattern to extend, verbatim (`build_db.py:707-715`):**

```python
                        **(
                            {"page_size": _PAGE_SIZE_BY_PART[_canon]}
                            if _canon in _PAGE_SIZE_BY_PART
                            else (
                                {"page_size": raw_page_size}
                                if _upstream_proto_id == 0x0D
                                else {}
                            )
                        ),
```

**⚠ Keep the arm an `ast.IfExp` inside the same `**{...}` unpacking.** `tests/
test_chip_database_field_inventory.py:194-258` ast-walks `chip_entry` and handles `ast.IfExp`
branches specifically. A restructure into a statement-level
`chip_entry["programming"]["page_size"] = ...` changes which code path that leg exercises.

**Fail-closed-emit pattern to mirror (`build_db.py:378-384`)** — raise before any JSON is written:

```python
        raise ValueError(
            f"chip with protocol {protocol_id:#04x} has unparseable "
            f"pulse_delay {raw_hex!r} — refusing to default to 0 us"
        ) from None
```

**Deletion target (`build_db.py:96-115`):** the `_PAGE_SIZE_BY_PART` dict and its leading comment
block. Its two values, recorded for reversibility: `"W29C040": 256`, `"W29C020": 128`.

---

### Host fail-closed guard (utility + service + controller, request-response)

**Analog 1 — the module shape:** `firestarter_app/firestarter/flash4_erase_gate.py`. Already
`0x05`-specific, pre-connect, pure-predicate, names the chip. Reuse its constant so the `0x05`
predicate stays single-sourced (`:41-65`):

```python
FLASH4_PROTOCOL_ID = 5

def is_flash4(programmer_data: Mapping[str, Any] | None) -> bool:
    if not programmer_data:
        return False
    return programmer_data.get("algorithm") == FLASH4_PROTOCOL_ID
```

**Invert its polarity.** Its own docstring (`:22-29`) states it "FAILS OPEN"; this guard must fail
closed.

**Analog 2 — the fail-closed raising shape:** `jp5_gate.require_acknowledged`, `jp5_gate.py:84-107`:

```python
def require_acknowledged(
    chip_name: str,
    bus_config: dict | None,
    operation: str,
    acknowledged: bool,
) -> None:
    if operation not in DAMAGE_CAPABLE_OPERATIONS:
        return
    if not bus_config or not bus_config.get("bus"):
        raise Pin1HazardRefusedError(
            f"{chip_name.upper()}: refusing to {operation} -- no bus "
            "configuration is available to prove socket pin 1 is safe, and "
            "absent evidence is never treated as safe."
        )
```

**Analog 3 — the exception class:** `exceptions.py:74-89`, `ChipNotImplementedError`. Subclass
`EpromOperationError`, and note its docstring already states the property this phase wants
("The guard fires BEFORE any wire dict is built or serial byte emitted").

```python
class ChipNotImplementedError(EpromOperationError):
    """Raised when the host refuses a program-capable operation on a non-supported chip.
    ...
    """
```

**Analog 4 — the `except` arm, and its ordering constraint.** `cli_handlers.py:186-223`. The
`ChipNotImplementedError` arm sits at `:203-211` and renders `str(e)` verbatim. The generic
`EpromOperationError` arm at `:216-217` prefixes `"Programmer error: "`. **A new
`EpromOperationError` subclass needs its own arm above `:216` or it is unreachable:**

```python
        except ChipNotImplementedError as e:
            raise click.ClickException(str(e)) from e
        ...
        except EpromOperationError as e:
            raise click.ClickException(f"Programmer error: {e}") from e
```

**Analog 5 — the two call sites.** Both citations verified unchanged.

Operator layer, `eprom_operations.py:2002-2007` — the sibling to add, immediately before the
`with self._operation_context(...)` at `:2009` where the port opens. This is the layer that also
covers `dev test` and every non-CLI entry point:

```python
        require_acknowledged(
            eprom_name,
            eprom_data_dict.get("bus-config"),
            "write",
            pin1_hazard_acknowledged,
        )
```

CLI pre-flight, `cli_handlers.py:758-759` — `eprom_data` is the fully resolved wire dict and
`app.eprom_operator.write_eprom(...)` at `:761` is the first line that touches serial:

```python
    if not jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "write"):
        sys.exit(1)
```

**No wire-path change.** `database.py:413-415` and `:553-554` are algorithm-agnostic truthiness
tests. The 25 newly-emitting rows start sending `page-size` with zero host code change — which is
exactly why the wire-dict golden gate moves.

---

### `firestarter_fw/test/native/avr/_shared/host_stubs_common.inc` (test harness, event-driven)

**Analog is in the same file — the strobe recorder at `:75-105`.** It is the only recorder here
that already carries an overflow flag, and it is the shape to copy onto the bus recorder:

```c
#define HOST_STUBS_MAX_STROBES 512
...
static int s_strobe_overflow = 0;

extern "C" void clear_strobes()     { s_strobe_count = 0; s_strobe_overflow = 0; }
extern "C" int  strobe_overflowed() { return s_strobe_overflow; }

static void strobe_push(uint8_t kind, uint8_t pin, uint8_t value) {
    if (s_strobe_count < HOST_STUBS_MAX_STROBES) {
        ...
        s_strobe_count++;
    } else {
        s_strobe_overflow = 1;  /* tail dropped; prefix stays valid — Pitfall 2 */
    }
}
```

The bus recorder it must be applied to (`:168-189`) has **no** flag and an unconditional cap:

```c
#elif defined(HOST_STUBS_RECORD_BUS)
#define HOST_STUBS_MAX_RECORDING 256
...
extern "C" void rurp_write_to_register(uint8_t reg, rurp_register_t data) {
    if (s_bus_recording_count < HOST_STUBS_MAX_RECORDING) {
        ...
    }
}
```

Two changes: `#ifndef`-guard the cap (so existing suites are byte-unchanged at the default and a
suite can raise it), and add the saturation accessor.

**Analog for the saturation accessor itself, already in-tree and CI-green:**
`test/native/avr/test_val_eprom/host_stubs.cpp:115-117` — a suite-local reporter written precisely
because the shared recorder has none:

```c
extern "C" int val_recording_saturated() {
    return s_bus_recording_count >= HOST_STUBS_MAX_RECORDING;
}
```

---

### `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (test, streaming)

**Fixture to fix (`:185-199`)** — `h.page_size` is never set, so `{}` zero-initialises it, and both
existing cases assert `RESPONSE_CODE_OK`. They go RED under D-05:

```c
static firestarter_handle_t make_write_handle_with_data(void) {
    firestarter_handle_t h = {};
    h.protocol   = 0x05;
    h.cmd        = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id    = 0; /* skip chip-id branch in write_init */
    h.mem_size   = 524288; /* 512 KB (W29C040) */
    h.address    = 0;
    h.data_size  = 4; /* small: 4 zero bytes at page 0; poll passes immediately */
    return h;
}
```

The affected cases are `test_5v_page_write_execute_emits_sdp` (`:263-274`) and
`test_5v_page_write_execute_no_vpp` (`:281-292`).

**Drive pattern (`:263-274`)** — `configure_memory`, then clear, then the dispatched pointer:

```c
    firestarter_handle_t h = make_write_handle_with_data();
    configure_memory(&h);
    clear_bus_recording(); /* reset after configure_memory's set_address call */

    h.firestarter_operation_main(&h);
```

**Boundary oracle — elision-immune, use this, not a record count (`:236-258`):**

```c
static bool recording_contains_sdp_signature(void) {
    int msb_seq_index = 0;
    const uint8_t msb_pattern[3] = {0x55, 0x2A, 0x55};
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == MOST_SIGNIFICANT_BYTE) {
            ...
        }
    }
    return false;
}
```

`flash_execute_command(FLASH_ENABLE_WRITE)` is emitted exactly once per page start
(`flash_5v_page.cpp:92-96`), and its three addresses `0x5555/0x2AAA/0x5555` differ from each other
and from the data addresses, so no cache-compare elision can remove the MSB writes this oracle keys
on. Generalise it to **count** signatures and record their positions.

**Do not switch this suite's `host_stubs.cpp` to `HOST_STUBS_REAL_REGISTER_UTILS`.** It is a
one-line opt-in file (`#define HOST_STUBS_RECORD_BUS` then the `.inc` include). That other flag
redefines six symbols and pulls in `HOST_STUBS_CUSTOM_DATA_BUFFER`, changing the 15 currently green
cases.

**Saturation-assertion analog, CI-green today** —
`test/native/avr/test_val_eprom/test_val_eprom.cpp:323-326`, paired with a non-vacuity control in
the same case:

```c
    TEST_ASSERT_FALSE_MESSAGE(val_recording_saturated(),
        "recorder saturated at " "256" " entries -- every count below would be silently wrong; shrink the block");
    TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code,
        "non-vacuity: the block must actually CONVERGE, otherwise no pulse was ever verified and the counts below describe nothing");
```

**Mismatch-test analog for the refusal fork.** No matching-id trace proves a WARN/ERROR fork fired.
The in-tree shape for an explicit negative is `test_read_timing_params.cpp:188-262`
(`test_out_of_range_algorithm_saturates_not_truncates`,
`test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size`) — assert the **rejecting**
outcome, not the absence of a message. For each refusal case assert both
`h.response_code == RESPONSE_CODE_ERROR` **and** `bus_recording_count() == 0`. "Refuses" without
"performs no write" is not D-05.

**Timing is unassertable here.** `delay()` / `delayMicroseconds()` are ArduinoFake-stubbed and the
recorder stores no time. Assert only on the recorded address/register stream. Keep `data_buffer`
all-zero so `rurp_read_data_buffer()` (`host_stubs_common.inc:223`, returns 0) makes the poll
converge on iteration 1.

---

### Host data gates

**`tests/test_page_size_invariants.py`** — self-analog. Leg 4, the count (`:237-247`):

```python
def test_exactly_20_page_size_carriers_across_all_746_rows() -> None:
    db = _load_db(_DB_FILE)
    total_rows = sum(len(chips) for chips in db.values())
    assert total_rows == 746, f"expected 746 total rows, found {total_rows}"
    carriers = _select_page_size_carriers(db)
    assert len(carriers) == 20, (
        f"expected exactly 20 page_size carriers (18 native + 2 curated) "
        ...
    )
```

The function **name** encodes the number. Rename it with the new value. Leg 6's allow-list is built from
frozensets at `:69-108`:

```python
_CURATED_PAGE_SIZE_IDENTITIES = frozenset({...})            # 2, subsumed
_NATIVE_0X0D_PAGE_SIZE_IDENTITIES_128 = frozenset({...})    # 15, unchanged
_NATIVE_0X0D_PAGE_SIZE_IDENTITIES_64 = frozenset({...})     # 3, unchanged
_ALL_PROVENANCE_CORROBORATED_IDENTITIES = (
    _CURATED_PAGE_SIZE_IDENTITIES | _NATIVE_0X0D_PAGE_SIZE_IDENTITIES
)
```

The 27 `0x05` identities are already written down in-repo at
`tests/test_lock_status_class_partition.py:296-327` as `_ALGORITHM_0X05_KEYS` with a module-level
`assert len(...) == 27`. **Import or duplicate it. Do not relocate it** — that module's own leg asserts
the live DB population against it. Separator differs (`MFG/part` string there, tuple here), so an
adapter is needed. Keep the two synthetic non-vacuity legs (`:376`, `:395`). They are what stops
the widened allow-list passing vacuously.

**`tests/test_vcc_margin_rail.py`** — assert absence, do not delete the leg. Two of the three
assertions at `:231-241` are untouched; `hasattr` is the right predicate because after D-01
`len(build_db._PAGE_SIZE_BY_PART)` would raise `AttributeError` (a test *error*, not a readable
failure). The module docstring at `:31-32` also names the count and must be reworded, not extended
— it is a docstring, which the citation gate does not scan, but the no-comments rule still says
reword rather than add prose.

**`tests/golden/chip_database_field_inventory.json`** — the machine-read count is
`"page_size": 20` at **line 42** (CONTEXT.md's `:14` is prose). `"page_size"` also appears at line
65 as a name-list entry, which does **not** move. Prose mentions at lines 9 and 14 do. The
precedent for how to record the change is the `meta.phase_149_update` string already in the file,
which states the re-derivation explicitly. Follow the `how_to_update` literally: re-derive **every**
number by independent traversal and name the changed key, its level and the reason in the commit
message.

**`tests/golden/wire_dict_expected_deltas_194.json`** — analog
`tests/golden/wire_dict_expected_deltas_149.json`. Top-level keys are `deltas` and `meta`. Delta
keys are `MFG|part_number|<positional index>`; values are `{"page-size": N}`. The `meta` block
carries `decision`, `honesty`, `how_to_update`, `phase`, `provenance` — and its own `provenance`
string states the key suffix is a positional index and must be **generated programmatically, never
transcribed by hand**. Do that. Count must be 25.

**`tests/test_wire_dict_equivalence.py`** — the 182 layer (`:262-279`) is the smallest complete
per-layer block and the best template: a `missing_from_golden_*` assertion, an `already_present_*`
assertion keyed on **the layer's own field**, and an exact-count assertion. The 149 block's own
comment at `:228-230` fixes the count form: "must stay an equality, not a floor". Then extend
`layer_pairs` (`:280-284`) from three pairs to six:

```python
    layer_pairs = (
        ("149", deltas_149, "153", deltas_153),
        ("149", deltas_149, "182", deltas_182),
        ("153", deltas_153, "182", deltas_182),
    )
```

**⚠ `194 × 149` is the one dangerous pair** — both layers carry the field `page-size`, so the
existing check only passes because they are key-disjoint (`0x05` rows vs `0x0D` rows). Add the pair
and let that assertion prove it. `_GOLDEN_PAGE_SIZE_RECORD_KEYS` and the leg at `:201-211` do **not**
move: they assert a property of the frozen golden, which is never re-captured.

---

### `.planning/v1.39/<27-row record>.md` (doc artefact, batch)

**Analog:** `.planning/v1.33/sweep-outcome-record.md` (tracked, meta repo). Note
`.planning/v1.39/` does **not exist yet** — the task creates the directory. Pattern to copy:

```markdown
---
title: Post-sweep outcome record — milestone v1.33, Phase 154
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "12"
measured: 2026-08-23
status: AUTHORITATIVE — the "after" side of every before/after pair in Phase 154
pairs_with: .planning/v1.33/baseline-pre-sweep.md
requirements: [SWEEP-05 (after-half), SWEEP-10, ...]
---
```

Its body convention, worth copying: "Every number below carries the command that produced it" —
each measurement is stated with its reproducing command, and nothing is quoted from research
without re-measurement or explicit attribution. Carry the evidence-class split verbatim:
**0 of 9 on hardware, 9 of 9 on the database comparison.**

---

## Comment-Deletion Boundary (no replacement text — hard rule)

Four inherited comments are falsified by this phase. The pattern to map is the **deletion
boundary**, not comment authorship. Line ranges verified this session.

| File:line | Delete these clauses | Must survive |
|---|---|---|
| `firestarter_app/firestarter/constants.py:140-147` | `(curated or, provenance-keyed for upstream-native 0x0D rows)`; `(algorithm 13 / 0x0D only; other algorithms' handlers do not consume this key at all)` | `Firmware sync: json_parser.c (key_page_size).` and the `commit 58c6a3c` PROGMEM-dispatch note |
| `firestarter_app/firestarter/database.py:401-412` | `either for a datasheet-curated [CITED:] chip or,`; `(algorithm 13 / EEPROM_POLL only)`; `(algorithm 13 only; other algorithms' handlers never consume this key)` | the TRUTHINESS-test explanation and the underscore-vs-hyphen key note — both still true |
| `firestarter_app/firestarter/database.py:545-552` | `(curated or provenance-keyed for an upstream-native 0x0D row)`; `firmware (algorithm 13 / 0x0D only) falls back to its own named AT28C page-size floor constant` | the TRUTHINESS-test clause |
| `firestarter_fw/src/json_parser.c:150-155` | `Validation of power-of-two, range and the silent fallback still live in the 0x0D handler (eeprom28c_page_mask)` | the saturation clause (`the table now also saturates an out-of-range value…`) — still true |
| `firestarter_fw/include/firestarter.h:186-189` | `so the 0x0D handler applies its own named fallback floor` | **`Reset per command in json_parse, exactly like chip_id above.`** and `0 = absent` |

Deletion only. No reword and no replacement text. Itemise the deletions in `194-SUMMARY.md`.

---

## Shared Patterns

### Fail-closed refusal before any I/O
**Sources:** `firestarter/jp5_gate.py:84-107` (raise), `firestarter/flash4_erase_gate.py:41-79`
(pure predicate + refusal text), `firestarter/exceptions.py:74-89` (exception class).
**Apply to:** the new host guard, its exception, and both call sites.

### Resolve-once-outside-the-loop, mask never `%`
**Source:** `firestarter_fw/src/proms/eeprom_28c.cpp:402-418, 455`.
**Apply to:** `flash_5v_page.cpp`. `__udivmodsi4` has seven callers in the linked `uno` ELF, so
removing these two `%` sites frees no flash (measured +6 B on both envs). Do the swap for the
call-site bytes, the hot-loop cycles and consistency — not as a flash saving.

### Non-vacuity beside every new assertion
**Sources:** `tests/test_page_size_invariants.py:376,395` (synthetic-offender legs);
`tests/test_wire_dict_equivalence.py:214-235` (`already_present` + exact count);
`test/native/avr/test_val_eprom/test_val_eprom.cpp:323-326` (saturation + convergence control).
**Apply to:** every widened count, every new delta layer, every new native boundary case.

### Golden re-derivation, never a hand edit
**Sources:** `tests/golden/chip_database_field_inventory.json` `meta.how_to_update`;
`tests/golden/wire_dict_expected_deltas_149.json` `meta.how_to_update` + `meta.decision` (D-17).
**Apply to:** the field inventory and the new 194 delta layer. `wire_dict_baseline.json` is never
re-captured — add a layer instead.

### Planning-citation gate scope
Forbidden in `#` and `/* */` comments across app `firestarter tests tools` and firmware
`src include test tests scripts platform tools ...`: `.planning`, GSD artefact names,
`Phase NNN`, `D-NN`, `REQ-NN`. **Python docstrings are string expressions and are never scanned**
— which is how `test_page_size_invariants.py:1` legitimately cites its origin phase. C/C++ has no
such exemption, and the no-comments rule forbids the comment there outright.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `firestarter_app/firestarter/data/chip_database.json` | build output | batch | Generated. There is no pattern to copy — only the regeneration procedure and its re-deriving gate. |
| `firestarter_fw/include/messages.h`, `firestarter_app/firestarter/messages.py` | build outputs | — | Generated by `tools/catalog/sync_to_subrepos.sh` in the meta repo. Never hand-edited. |

No file in this phase lacks a usable analog for reasons of novelty.

---

## Corrected Citations (drift found while mapping)

| Cited in | Citation | Corrected |
|---|---|---|
| CONTEXT.md §canonical_refs | `flash_5v_page.cpp:82,92,100` — "three `%` sites" | **Two** `%` sites: `:92` and `:100`. `:82` is the derivation call deleted by D-06. |
| CONTEXT.md §canonical_refs | `eeprom_28c.cpp:392-410` — `eeprom28c_page_mask()` | Function body `:402-410`; doc comment `:387-401`; resolve-once site `:418`. Use `:387-418`. |
| CONTEXT.md §canonical_refs | `chip_database_field_inventory.json:14` — "records the count of 20" | Machine-read count is at **`:42`**. `:14` is prose. `"page_size"` at `:65` is a name-list entry and does not move. |
| CONTEXT.md §canonical_refs | `constants.py:141-149` | Comment block is `:140-147`; `JSON_KEY_PAGE_SIZE` is at `:148`. |
| CONTEXT.md §canonical_refs | `database.py:401-415` and `:545-554` | Comment blocks `:401-412` and `:545-552`; code `:413-415` and `:553-554`. Code unchanged. |
| `.planning/todos/pending/runtime-info-log-naming-the-effective-page-size.md` | `firestarter/tools/catalog/messages.toml:1124` | **Path does not exist.** Canonical path is `tools/catalog/messages.toml` in the meta repo. Do **not** edit the todo (D-09 keeps it unmodified); record the drift in `194-SUMMARY.md`. |

Verified unchanged and safe to cite as written: `build_db.py:102`, `:332`, `:348`, `:378-384`,
`:696-714`; `firestarter.h:186`; `json_parser.c:150-156`, `:271-280`;
`eprom_operations.py:2002`; `cli_handlers.py:758`; `test_vcc_margin_rail.py:234-248`.

---

## Metadata

**Analog search scope:** `/workspaces/tools/catalog/`, `/workspaces/.planning/v1.33/`,
`firestarter_app/{firestarter,tools,tests}/`, `firestarter_fw/{src,include,test,tests,scripts}/`.
**Search tool:** `/usr/bin/grep` exclusively (the devcontainer `grep` is ugrep and honours
`.gitignore`).
**Tracked-source verification:** `git ls-files` per repository — all 15 analog paths tracked.
**Pattern extraction date:** 2026-09-15
