# Phase 201: A partial write is gated on its own region - Pattern Map

**Mapped:** 2026-09-19
**Files analyzed:** 14 (7 firmware source/header, 3 firmware test, 4 host)
**Analogs found:** 13 / 14
**Repos:** dual — `firestarter_fw/` (C/C++) and `firestarter_app/` (Python). All paths below are
relative to their sub-repo root unless prefixed. Every analog named here was confirmed
git-tracked in its own submodule.

**Authority note.** Where CONTEXT.md and RESEARCH.md disagree, RESEARCH.md wins (it re-measured).
This map follows RESEARCH.md: `region-end` / `uint32_t region_end` (absolute end, not a length,
per C-3), the host key goes in `_setup_operation` and **not** `convert_to_programmer` (C-1),
the coupled host test is `test_chip_test_uv_slot_write.py` and **not** `test_uv_mask.py` (C-2).

---

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|---|
| `include/firestarter.h` (new `uint32_t region_end` member) | fw | model / struct | request-response | `firestarter.h:186-190` — `uint16_t page_size` | exact |
| `src/json_parser.c` (key string + FIELD row + assert + reset) | fw | parser / config | transform | `json_parser.c` `page_size` — 4 sites | exact |
| `include/memory_utils.h` (new region declaration) | fw | header | — | `memory_utils.h:18-22` — `mem_util_blank_check` + `memory_verify_execute`'s "exposed so" comment | exact |
| `src/proms/memory.cpp` (region form + wrapper) | fw | service | batch scan | itself — `mem_util_blank_check:450-513` is the body being split | in-place (no external analog) |
| `src/proms/eprom.cpp:145` (call site) | fw | controller | request-response | `eprom.cpp:129-158` — the body + single-exit HV wrapper | in-place |
| `src/eprom_operations.cpp:90,128` (`mem_size` → op end) | fw | service | streaming | itself — `_process_incoming_data` | in-place |
| `test/native/avr/test_val_eprom/host_stubs.cpp` (address-keyed seeding) | fw | test harness | event-driven mock | `host_stubs.cpp:86-131` — the 16-slot model it replaces/extends | partial (see "No analog") |
| `test/native/avr/test_val_eprom/test_val_eprom.cpp` (3 new cases) | fw | test | request-response | `test_val_5v_page.cpp:207-219, 789-816` | role-match (one inversion) |
| `tests/test_blank_check_region_source_contract.py` (new, D-15.3) | fw | test / gate | file-I/O scan | `tests/test_write_path_source_contract_v131.py:140-200` | exact |
| `tests/golden/protocol_branch_inventory.json` (re-derive) | fw | golden | — | its own `meta.how_to_update` + RESEARCH.md G-2 script | exact |
| `tests/test_progress_emission_is_leonardo_only.py:606-613` | fw | test / gate | file-I/O scan | itself | in-place |
| `firestarter/constants.py` (new `JSON_KEY_REGION_END`) | app | config | — | `constants.py:134-147` — `JSON_KEY_PAGE_SIZE` block | exact |
| `firestarter/eprom_operations.py` (`_setup_operation`/`_operation_context`/`write_eprom`/`verify_eprom`) | app | service | request-response | `eprom_operations.py:490-495` — the read path's `memory-size` narrowing | exact |
| `tests/fake_chip.py:265-288` (`_is_blank` widening) | app | test double | CRUD | `FakeChip.write_eprom:137-158` — region slicing already there | exact |
| `tests/test_eprom_operations.py` (2 new host legs) | app | test | request-response | `test_eprom_operations.py:283-296` + `:314-320` | exact |

---

## Pattern Assignments — Firmware

### `include/firestarter.h` — the new handle member (model, struct)

**Analog:** `firestarter.h:186-190`, quoted verbatim in RESEARCH.md § "The handle struct".

Copy the comment shape exactly (purpose / `0 = absent` / "reset per command in json_parse").
**Placement is load-bearing:** after `page_size`, **before `char data_buffer[DATA_BUFFER_SIZE]`**.
`data_buffer` is 1024 on leonardo, so any parsed member after it blows the `uint8_t` offset column
in the `FIELD` macro. Type is `uint32_t` (a 512 KiB part needs 20 bits).

### `src/json_parser.c` — four edits, three copied and one hand-changed (parser, transform)

**Analog:** `page_size`, at four sites. RESEARCH.md § "`json_parser.c` — the exact shapes D-03 says
to copy" quotes all four verbatim; do not re-read the file to get them.

| Edit | Template site | Note |
|---|---|---|
| PROGMEM key string | `:66-70` (`key_page_size`) | Wire key is the **hyphen** form. Copy the hyphen-vs-underscore warning comment. |
| `FIELD(...)` row in `key_parsers[]` | `:150-152` | Third column (clamp) must be `0` — a clamp is `uint16_t` and cannot hold a 20-bit end. |
| Offset `_Static_assert` | **`:204-207`** | CONTEXT.md D-16.3's citation `:164-166` is **wrong** (that is inside the comment block `:155-163`). |
| Row-count `_Static_assert` | `:208-210` | **EDIT, not add: `== 11` → `== 12`.** The only literal in the file that must change by hand. |
| Per-command reset in `json_parse` | `:257-275` (`handle->page_size = 0;`) | **Non-negotiable, and for a stronger reason than `page_size`'s.** `handle` is one file-scope global (`src/firestarter.cpp:33`) with no per-command memset; under D-04 a stale non-zero value **narrows** a later whole-device check — fail-**open**. Say so in the new comment; do not copy `page_size`'s wording unchanged. |

The `FIELD` macro itself (`:108-110`) derives offset and width from `offsetof`/`sizeof`, so **no
offset is ever hand-written**. Input-validation policy: `store_field`'s SATURATE clamp at
`:243-249` plus `memcpy` at `:255`.

### `include/memory_utils.h` — declaring the region form

**Analog** (`memory_utils.h:16-22`, read this session):

```c
void mem_util_blank_check(firestarter_handle_t* handle);
/* Exposed so eprom.cpp's VERIFY_PER_PULSE_PLUS_FINAL arm can CALL the
 * canonical full-block verify instead of carrying a byte-identical copy.
 * Defined in src/proms/memory.cpp as the CMD_VERIFY operation_main. */
void memory_verify_execute(firestarter_handle_t* handle);
```

The house pattern for a newly-exposed internal is: declaration + a block comment saying **why it is
exposed and where it is defined**. Copy that shape for
`void mem_util_blank_check_region(firestarter_handle_t* handle, uint32_t start, uint32_t end);`,
and state that the plain form is a wrapper over it so the two cannot drift.

### `src/proms/memory.cpp` — the split (service, batch scan)

**No external analog — the body being split is its own template.** RESEARCH.md § "`mem_util_blank_check`
as it stands today" quotes `:450-513` verbatim with line anchors; work from that quote.

The four `mem_size` reads that become `end`-relative in the region form: `:456` (completion test),
`:465` (scan upper bound), `:501` (clamp), `:510` (progress denominator). `:453`
(`blank_check_saved_address = handle->address`) stays — on the write-init path the saved address
and the region start are the same value.

Constraints carried by the existing code, all with written rationale in-file:
- `static uint32_t blank_check_saved_address;` (`:437`) with a "do not replace with a heap
  allocation" rationale at `:425-436`. **Do not add a second cross-call static** — that is the
  reason C-3 rejects a length on the wire.
- `#define BLANK_CHECK_CHUNK_SIZE 8192` at `:442`.
- The `handle->cmd == CMD_BLANK_CHECK` emit fork at `:480` is untouched.

**Recommended home for the `0 = absent` fallback** (RESEARCH.md Open Question 1): resolve it here,
in the wrapper/region entry, and once at the top of `_process_incoming_data`. Resolving it inside
`eprom.cpp` adds a ternary row to the branch-inventory golden (G-2 ternary trap); resolving it in
`memory.cpp` does not. Fail-closed form is `min(region_end, mem_size)`.

### `src/proms/eprom.cpp:145` — the one call site (controller, request-response)

**Analog / in-place context** (`eprom.cpp:129-158`, read this session):

```c
static void eprom_internal_write_init_body(firestarter_handle_t* handle) {
    if(!is_operation_in_progress(handle)){
        eprom_generic_init(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
        if (is_flag_set(FLAG_CAN_ERASE)) {
            if (!is_flag_set(FLAG_SKIP_ERASE)) {
                eprom_internal_erase(handle);
            } else {
                LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);
            }
        }
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);        // <- the one line that changes
    }
}

void eprom_write_init(firestarter_handle_t* handle) {
    eprom_internal_write_init_body(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        handle->firestarter_set_control_register(handle, EPROM_HV_ALL_OFF_MASK, 0);
    }
```

The pattern to preserve is the **single-exit wrapper**: the body's comment (`:120-128`) states that
the property "a `return` added inside the body later cannot bypass it" is structural. The region
call must add **no new `return`** to the body.

Two hard line-number couplings on this file:
- `tests/test_protocol_branch_inventory.py` asserts `protocol_lines == [70]` — **do not insert any
  line, including a comment, above `eprom.cpp:70`.** `:145` is safely below.
- `:397` is the only other `mem_size` read in the file (the Leonardo-only progress emit) — see G-1.

### `src/eprom_operations.cpp:90, :128` — bounding write **and** verify (service, streaming)

**In-place**, quoted verbatim in RESEARCH.md § "`_process_incoming_data`". The function is reached
from both `eprom_write` (`:23`) and `eprom_verify` (`:29`) via
`op_execute_stateful_operation(_process_incoming_data, handle)` — one edit bounds both, which is
D-07's mechanism. Resolve the operation-end local once at the top of the function and use it at
both sites.

---

## Pattern Assignments — Firmware tests

### `test/native/avr/test_val_eprom/host_stubs.cpp` — address-keyed seeding (test harness)

**Analog is the thing being replaced**, `host_stubs.cpp:86-131`, quoted verbatim in RESEARCH.md
§ "The `firestarter_get_data` mock". The exported-helper convention to copy (read this session):

```c
extern "C" void val_readback_seed(uint8_t idx, uint8_t target, uint8_t converge_after);  // :104 def
extern "C" int  val_recording_saturated();                                               // :115 def
```
declared at the top of the test TU as `extern "C"` prototypes (`test_val_eprom.cpp:50-51`) and
called from cases at `:319, :347`. A new `val_shadow_seed(uint32_t address, uint8_t value)` should
follow exactly that shape: `extern "C"` definition in `host_stubs.cpp`, `extern "C"` prototype at
the top of `test_val_eprom.cpp`, reset in `setUp`.

**Why new work is unavoidable:** the existing model recovers the byte index as
`address & (VAL_EPROM_READBACK_SLOTS - 1)` with 16 slots, so it aliases modulo 16 across the whole
address space — seeding "non-blank outside the region" also seeds inside it. The stub's own comment
(`:70-84`, read this session) concedes the scope: it is valid only "for a block based at address 0
because LOOP_BUS_CONFIG_0x07 leaves address bits 0-7 identity-mapped". Two further constraints:
`HOST_STUBS_MAX_RECORDING` is 256 and drops silently past it (so index recovery must **not** depend
on the recording for a whole-device scan), and `millis()` is pinned to 0 in `setUp`
(`test_val_eprom.cpp:69`) so no progress frame is observable here. RESEARCH.md's A4 recommends a
flat shadow array with a small `mem_size` (16384 → 2 chunks); the sparse `(address, value)` list is
the equally-valid alternative.

### `test/native/avr/test_val_eprom/test_val_eprom.cpp` — the three new cases (test)

**Analog:** `test/native/avr/test_val_5v_page/test_val_5v_page.cpp:207-219` (handle factory) and
`:789-816` (drive + assert), both quoted verbatim in RESEARCH.md § "The reusable driving pattern".

Two adaptations the analog does not give you:
1. **Add a new factory; do not mutate the shared one.** `test_val_eprom.cpp`'s own `make_handle`
   (`:79-89`) sets `ctrl_flags = FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE` and `mem_size = 65536`;
   six existing cases depend on it. The new cases need `ctrl_flags = 0` and a small `mem_size`.
2. **The oracle inverts.** In the 5v_page analog the check was *deleted*, so
   `is_operation_in_progress == FALSE` after one call proves it did not run. Here the check *does*
   run, so one call leaves it TRUE. Drive `h.firestarter_operation_init(&h)` **in a loop until
   `is_operation_in_progress` goes false**, then assert `response_code != RESPONSE_CODE_ERROR`. A
   single call proves nothing — the non-blank byte may live in a later chunk.

`native/avr/test_val_eprom` is in `[native_base] test_filter` and both `[env:native]` and
`[env:native_nodevtools]` extend it, so one filter entry serves both CI envs.

### `tests/test_blank_check_region_source_contract.py` (new gate, D-15.3)

**Analog:** `tests/test_write_path_source_contract_v131.py`. Structural excerpt, read this session
(`:146-176`):

```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_EPROM_REL = "src/proms/eprom.cpp"
_MEMORY_REL = "src/proms/memory.cpp"

# Environment seam -- binds at IMPORT time.
_SCAN_EPROM = Path(
    os.environ.get("FIRESTARTER_WRITE_PATH_SCAN_SOURCE", str(_REPO_ROOT / _EPROM_REL))
)
# memory.cpp has no override -- see the "Environment seams" docstring section for why.
_SCAN_MEMORY = _REPO_ROOT / _MEMORY_REL

# Concatenation-built needles. Coverage 12 asserts none of these appear
# verbatim anywhere in this module's own source.
_NEEDLE_RETRY_MACRO = "NUMBER" + "_OF_RETRIES"
_NEEDLE_PROGRAM_MISMATCHED_BYTES = "program_mismatched" + "_bytes"
```

Elements to copy, each with its purpose:
- `_HERE`/`_REPO_ROOT` from `Path(__file__).resolve().parent` — closes the
  `check_permitted_claims.py` `_HERE`-resolves-wrong trap.
- Two scan targets, **one env-overridable and one not** — the seam exists so a planted violation can
  be scanned; the non-seam target proves a stray env value cannot make the gate vacuous.
- Concatenation-built needles so the module does not self-match.
- **Paired negative + positive legs** (`:66-72`: "a deleted call satisfies Coverage 6 vacuously and
  fails here"). This is the element D-15.3 most needs — a gate asserting only "no caller passes a
  region" passes vacuously if every caller is deleted.
- Explicit non-vacuity leg (Coverage 10, `:637`) and self-skip-proof legs (Coverage 11 `:667`,
  Coverage 12 `:696`).
- `_strip_comments` before scanning — the real files discuss forbidden constructs in prose.
- Python `Path.read_text()` + `re`, **never a shell `grep`** (bare `grep` in this devcontainer is
  ugrep and honours `.gitignore`, silently under-scanning).

Leg set to write, derived from RESEARCH.md's 9-site caller census (3 direct calls + 6
function-pointer assignments, at `eprom.cpp:145 / flash_intel.cpp:95 / flash_nor_unlock.cpp:105`
and `eprom.cpp:53, :57`, `flash_nor_unlock.cpp:44`, `flash_5v_page.cpp:47`, `eeprom_28c.cpp:151`,
`flash_intel.cpp:62`): exactly 1 region call, in `eprom.cpp`, inside the brace-matched body of
`eprom_internal_write_init_body`; zero region calls in the four other protocol files; the wrapper
defined exactly once and its body passing `0` and `handle->mem_size`; exactly 6 function-pointer
assignments of the plain form.

The existing module already scans `src/proms/memory.cpp` (`_MEMORY_REL`, `:149`) but only for
`delayMicroseconds` / `mem_util_delay_us` / `MEM_UTIL_DELAY_US_MAX`, so D-09's split leaves it GREEN.

### `tests/test_progress_emission_is_leonardo_only.py` — the gate CONTEXT.md missed

**In-place.** `:606-613` asserts `arg2 == "handle->mem_size"` verbatim, and D-06 changes exactly
that argument. Three hazards in one gate, all detailed in RESEARCH.md G-1:
(a) the literal must change **and** the gate's stated design argument ("0xE0 must keep exactly one
payload meaning") must be restated in its docstring in the same commit — not silently swapped;
(b) the capture group `(?P<arg2>[^,()]+?)` (`:311`) **cannot match an argument containing
parentheses**, so an inline ternary makes the locator find **zero** blocks and two legs fail with
"found 0" — resolve the fallback into a plain local (`op_end`) before the emit and assert
`arg2 == "op_end"`; (c) the forbidden needle `handle->data_size` (`:265`) must not appear near the
emit.

### `tests/golden/protocol_branch_inventory.json` — re-derivation

No analog needed: the golden's own `meta.how_to_update` forbids hand-editing, and RESEARCH.md G-2
supplies a runnable re-derivation script plus four obligations (hand-written `reason` for each new
site; floor `>= 21`; `protocol_lines == [70]`; `blob_shas` from `git hash-object` on the working
tree before staging, `recorded_at_head` = the **parent** commit). The `counts` block is currently
21/1/20 while `sites` has 22 entries — unasserted drift, fix for honesty. Source change and
re-derivation land in the **same commit**; Phase 199 Plan 03 is the precedent for stating a
deviation rather than hiding one.

---

## Pattern Assignments — Host

### `firestarter/constants.py` — `JSON_KEY_REGION_END` (config)

**Analog** (`constants.py:134-147`, read this session):

```python
# Dev sweep knobs — Firmware sync: json_parser.c (key_read_settling, key_read_strobe)
# JSON key name strings for host-tunable read-timing parameters.
# MUST stay in sync with the PROGMEM key strings in firmware json_parser.c.
JSON_KEY_READ_SETTLING_DELAY = "read-settling-delay"
JSON_KEY_READ_STROBE_US = "read-strobe-us"
# Per-chip page size wire field. Emitted by database.py's
# convert_to_programmer only when the DB supplies a page_size --
# emit-when-present, mirrors the chip-id pattern.
# Firmware sync: json_parser.c (key_page_size).
JSON_KEY_PAGE_SIZE = "page-size"
```

Copy the shape: hyphen wire string, a `Firmware sync: json_parser.c (key_...)` line naming the
PROGMEM symbol, and a sentence on absent-semantics. **State D-04's inversion here** — absent means
whole device, the opposite of `page_size` — and say it is emitted by `_setup_operation`, not by
`convert_to_programmer`.

### `firestarter/eprom_operations.py` — the emit (service, request-response)

**Analog:** the read path's narrowing in `_setup_operation`, quoted verbatim in RESEARCH.md
§ "The minimal change" (`:476-495`), whose key line is
`command_dict["memory-size"] = addr + read_size  # :495`. `addr` is already computed there.

Add after the `COMMAND_READ` block:

```python
if region_length is not None and cmd in (COMMAND_WRITE, COMMAND_VERIFY):
    command_dict[JSON_KEY_REGION_END] = addr + region_length
```

`COMMAND_WRITE` / `COMMAND_VERIFY` are already imported (`:40-41`). Guard the command explicitly
(RESEARCH.md A2).

**Threading pattern — one gotcha not in RESEARCH.md's diff sketch.** `_operation_context` forwards
to `_setup_operation` **positionally** for the leading parameters and by keyword only for
`fault_inject_outgoing` (read this session, `:516-540`):

```python
    @contextmanager
    def _operation_context(
        self, eprom_name, eprom_data_dict, cmd,
        operation_flags: int = 0, address: str | None = None, size: str | None = None,
        fault_inject_outgoing: Callable[[bytes], bytes] | None = None,
    ):
        command_dict, buffer_size = self._setup_operation(
            eprom_name, eprom_data_dict, cmd, operation_flags, address, size,
            fault_inject_outgoing=fault_inject_outgoing,
```

So add `region_length` as a **keyword-passed trailing parameter on both signatures** and forward it
by name; do not insert it among the positional six.

**Precedent for computing the size pre-connect:** `firestarter/page_size_gate.py:162-172` already
does `parse_address(address_str)` + `os.path.getsize(input_file_path)` before connecting, and
`write_eprom` calls it at `:2010`, four lines above `_operation_context` at `:2014`.
`verify_eprom` (`:2107-2120`) takes `input_file_path` too but does **not** call
`require_page_alignment`, so it must `getsize` itself. Prefer the zero-behaviour-change guarded
form `try: ... except OSError: region_length = None`, so a missing file keeps surfacing where it
does today (`_main_phase_send_data:750`) rather than moving earlier for non-0x05 parts.

**Do not touch `database.py:convert_to_programmer`.** `tests/test_wire_dict_equivalence.py:508`
pins its key union to exactly nine keys; a key added there turns it RED, and the region is a
property of the operation, not of the chip row.

### `tests/fake_chip.py` — teaching the fake the region (test double, CRUD)

**Analog is one level up in the same file** — `FakeChip.write_eprom:137-158` already does the
region arithmetic (read this session):

```python
        start = _parse_addr_or_size(address_str) or 0
        incoming = Path(input_file_path).read_bytes()
        end = start + len(incoming)
        if start < 0 or end > self.memory_size:
            return False
        ...
            self.data[start:end] = incoming
```

`WriteInitPreflightChip._is_blank` (`:265-268`) compares the **whole** buffer, and `write_eprom`
gates on it at `:282` — so a `write -a` regression leg passes **vacuously** until the fake learns
the region. Widen by default argument (RESEARCH.md G-5's suggested body), keeping `blank_override`
as the first check so every existing caller is unaffected.

**Leave `FakeChip.check_eprom_blank` (`:205-211`) alone** — it models the *standalone* command,
whose behaviour BLANK-02 freezes.

**Coupled file is `tests/test_chip_test_uv_slot_write.py`** (6 references to
`WriteInitPreflightChip` at `:81, :104, :112, :276, :324, :413/:417`), **not** `test_uv_mask.py`,
which imports neither the fake nor `FakeChip`. The default-argument form means those 6 sites need
no edit unless they assert on the refusal.

### `tests/test_eprom_operations.py` — the two host legs (test)

**Analog, and the only compliant shape** after the 2026-09-14 operator ruling (`088d2b7`) that
deleted 24 host source-scanning modules **including the `json_key_parity` gate D-16.3 describes**:

```python
def test_read_timing_settling_key_constant() -> None:
    """JSON_KEY_READ_SETTLING_DELAY must equal the firmware PROGMEM key string.

    The firmware declares: const char key_read_settling[] PROGMEM = "read-settling-delay";
    (json_parser.c). If the host string drifts, the firmware silently ignores the param
    (Pitfall 2 — RESEARCH.md). This test pins the constant to the firmware source of truth.
    """
    from firestarter.constants import JSON_KEY_READ_SETTLING_DELAY
    assert JSON_KEY_READ_SETTLING_DELAY == "read-settling-delay"
```
(`tests/test_eprom_operations.py:283-296` — asserts a production constant against a **literal**,
reads no file, names the firmware declaration in prose.)

Second leg, the data-driven emission pin — `_make_captured_setup_operation` (`:263-281`) +
`test_read_timing_settling_emitted_in_command` (`:314+`), read this session:

```python
def _make_captured_setup_operation(captured: list):
    def _fake_setup_operation(self_op, eprom_name, eprom_data_dict, cmd, *args, **kwargs):
        captured.append(dict(eprom_data_dict))
        return None, 0
    return _fake_setup_operation

    with patch.object(EpromOperator, "_setup_operation",
                      _make_captured_setup_operation(captured)):
        operator.consistency_check_eprom(...)
```

Note the capture records `eprom_data_dict` (the *input*). For this phase the assertion is on the
**emitted `command_dict`**, so patch one level lower (wrap the real `_setup_operation` and capture
its return) or assert via the serial layer — the `*args, **kwargs` passthrough and the
`return None, 0` early-exit idiom are the parts to copy. Write one leg for `write` and one for
`verify` (D-05 / D-07).

**Split the cross-repo parity obligation:** a literal-pinned host constant here + a firmware-side
source-contract gate there. Do **not** rebuild a cross-repo scanner — the technique fails open
(71 legs silently skipped for a whole milestone).

---

## Shared Patterns

### Absent-value semantics on a wire field
**Source:** `json_parser.c:257-275` (the `json_parse` per-command reset) + `firestarter.h:186-190`.
**Apply to:** the handle member, the parser, `constants.py`, and every firmware use site.
`0 = absent`. `handle` is a single file-scope global (`src/firestarter.cpp:33`) with **no
per-command memset**, so the reset is what makes "absent" true in practice. Under D-04 a stale
value narrows a later whole-device check — fail-**open**, strictly worse than `page_size`'s case.

### Single-exit HV wrapper
**Source:** `eprom.cpp:120-158`.
**Apply to:** any edit inside `eprom_internal_write_init_body`. Add no `return`.

### Source-contract gate, firmware side only
**Source:** `tests/test_write_path_source_contract_v131.py`.
**Apply to:** D-15.3. Paired negative+positive legs, concatenation needles, one non-overridable
scan target, explicit non-vacuity and self-skip-proof legs, Python file reads (never shell `grep`).

### Exact counts asserted as equalities, proved non-vacuous by a planted mutation
**Source:** the Phase 199 / Phase 200 discipline, and `test_protocol_branch_inventory.py`'s own
`test_inventory_is_non_vacuous`.
**Apply to:** the 6-function-pointer and 1-region-call counts in D-15.3.

### Verify-command hygiene (applies to every plan's `<automated>` block)
- Firmware pytest: **`FIRESTARTER_META_ROOT=/tmp/no-meta`** is mandatory — without it 17
  **pre-existing** failures in `test_flash_path_record_sync.py` (a stale `.planning` scan path,
  invisible to CI) read as a phase failure. Baseline with the var: `269 passed, 32 skipped`.
- Host pytest: use `.venv/ci-replica/bin/python` (3.11.16; devcontainer default is 3.12) and
  `-o addopts=""` (pyproject sets `-ra -q`, so a second `-q` hides the count line).
- `pio test -e native` is **pull-request-only** in CI; run it locally every time alongside
  `native_nodevtools`.
- Any shell-based scan must use `/usr/bin/grep` (bare `grep` is ugrep 7.8.4, honours `.gitignore`).

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `test/native/avr/test_val_eprom/host_stubs.cpp` — address-keyed read model | test harness | event-driven mock | The only in-repo readback models are the 16-slot modulo-aliasing one here and `test_trace_eprom_v131`'s, which recovers the index from a **real register cache** (`HOST_STUBS_REAL_REGISTER_UTILS`) this suite deliberately does not define. Neither can express "non-blank at an absolute address outside the region". **New harness work; plan it as its own task**, sequenced before the D-16.1 test so the RED-first state is capturable (RESEARCH.md Open Question 4). |

---

## Metadata

**Analog search scope:** `firestarter_fw/{src,include,test,tests}`, `firestarter_app/{firestarter,tests}`.
**Files read this session (beyond CONTEXT.md/RESEARCH.md):** `firestarter_fw/include/memory_utils.h`,
`firestarter_fw/src/proms/eprom.cpp:126-160`, `firestarter_fw/tests/test_write_path_source_contract_v131.py:140-200`,
`firestarter_fw/test/native/avr/test_val_eprom/host_stubs.cpp:55-90`,
`firestarter_app/firestarter/constants.py:130-150`, `firestarter_app/firestarter/eprom_operations.py:500-540`,
`firestarter_app/tests/fake_chip.py:137-160`, `firestarter_app/tests/test_eprom_operations.py:260-330`.
All other excerpts are cited to RESEARCH.md's verbatim quotes rather than duplicated.
**Pattern extraction date:** 2026-09-19
