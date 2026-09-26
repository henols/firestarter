# Phase 201: A partial write is gated on its own region - Research

**Researched:** 2026-09-19
**Domain:** AVR firmware (C/C++), host Python CLI, dual-repo wire-protocol lockstep
**Confidence:** HIGH — every claim below was produced by reading the live source or running the
named command in this session. No claim rests on training memory.

---

## Summary

CONTEXT.md is right about nearly everything it measured. This document does three things and
deliberately does nothing else: it **closes the one question CONTEXT.md left open** (where the host
can compute the region), it **contradicts four CONTEXT.md claims loudly**, and it **names five gates
CONTEXT.md did not name** — four of which will turn a plan authored from CONTEXT.md alone RED at
execute time.

The headline answers:

1. **The host-side ordering question resolves cleanly with no restructure.** `write_eprom` and
   `verify_eprom` both receive `input_file_path` as a *parameter* and both enter `_operation_context`
   **after** they already have it. `write_eprom` already calls `os.path.getsize(input_file_path)`
   *before* connecting, inside `require_page_alignment`. One new keyword parameter threaded through
   `_operation_context` → `_setup_operation` serves both commands. D-05 and D-07 hold.
2. **`tests/test_progress_emission_is_leonardo_only.py:607` asserts the emit's second argument is the
   string `handle->mem_size` verbatim.** D-06 changes exactly that argument. This gate is **not**
   named anywhere in CONTEXT.md and it is the single most likely thing to make the plan look broken.
3. **The firmware `pytest tests/` suite is RED in this devcontainer before anyone touches anything**
   — 17 failures, all pre-existing, all from a stale meta-repo scan path. CI never sees them. A
   verify block that runs `pytest tests/ -v` without the workaround below will read as a phase
   failure.

**Primary recommendation:** make the wire field an **absolute end address** (`handle->region_end`),
not a length. §"The multi-call stability constraint" shows the length form is *mechanically unsound*
across the blank check's multi-call resumption, for a reason CONTEXT.md's D-03 discretion note did
not anticipate.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

CONTEXT.md's `<decisions>` block (D-01 … D-16), `Claude's Discretion` and `Deferred Ideas` are
locked premises for this phase and are **not reproduced here**; read
`.planning/phases/201-a-partial-write-is-gated-on-its-own-region/201-CONTEXT.md` directly. This
research assumes them and only reports where it **confirms**, **contradicts**, or **extends** them.

Two locked decisions are contradicted below on evidence, and both contradictions are narrow (they
touch *where a thing lives* and *which file is coupled*, never *what the phase does*):

| Locked item | Status here |
|---|---|
| D-03 naming (`region-size`, `handle->region_size`) | **Contradicted on the unit.** A length cannot survive the multi-call resumption; an absolute end can. See C-3. |
| D-16.2's coupled file (`tests/test_uv_mask.py:201`) | **Contradicted.** That file never touches the fake. The real coupled file is `tests/test_chip_test_uv_slot_write.py`. See C-2. |
| Integration Points: "`database.py:520-580` … the natural home for the new key" | **Contradicted.** That home reddens a gate and is structurally wrong. See C-1. |
| Code Insights: "Firmware CI is exactly three legs" | **Contradicted.** One of the three is pull-request-only. See C-4. |
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BLANK-01 | The write-init blank check applies to the region being written, not the whole device, so a non-erasable part holding data outside the target region accepts a write into a blank region. | §"Firmware seam" gives the exact current control flow of `mem_util_blank_check` with line-cited quotes; §"Host seam" gives the exact call graph and the minimal diff that supplies the region; §"The multi-call stability constraint" gives the unit the field must carry for the seam to be correct. |
| BLANK-02 | `mem_util_blank_check`'s whole-device behaviour unchanged for the standalone command and the erase-end check; the multi-call chunking through `blank_check_saved_address` still resumes. | §"Caller census" enumerates all 9 reference sites (CONTEXT.md says "four"); §"The three denominators" confirms which emit moves; §"Native harness" confirms `test_val_eprom` runs in both CI envs and gives the seeding pattern. |
| BLANK-03 | A UV part holding data outside the target slot accepts a slot write, proved by the regression test whose absence is why this shipped. | §"Native harness" reports the **blocking defect in the existing `firestarter_get_data` mock** (16-slot modulo aliasing) that makes the naive D-16.1 test impossible to write as specified; §"Host regression leg" confirms D-16.2's vacuity claim verbatim and names the correct coupled file. |
</phase_requirements>

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Deciding *what region* a write covers | Host (Python CLI) | — | Only the host knows the payload file's size. Measured: firmware `handle->data_size` is first written in MAIN (`firestarter_fw/src/operation_utils.cpp:151`), strictly after INIT runs the blank check. |
| Carrying the region across the seam | Wire protocol (JSON command frame) | — | The `FIELD(...)` table in `json_parser.c` is the only mechanism; `serial_comm.py` is key-agnostic (`json.dumps(command_dict)` at `firestarter_app/firestarter/serial_comm.py:256`), so no transport change is needed. |
| Enforcing the region (blank check) | Firmware — `memory.cpp` | Firmware — `eprom.cpp` | `mem_util_blank_check` owns the scan; `eprom_internal_write_init_body` owns the call site. |
| Bounding the data-transfer loop | Firmware — `eprom_operations.cpp` | — | `_process_incoming_data` is shared by write and verify (`firestarter_fw/src/eprom_operations.cpp:23-31`), so it bounds both. |
| Progress denominator | Firmware, split across three sites | Host (discards it) | `_apply_write_progress` already ignores the frame's total — confirmed verbatim below. |
| Proving the fix on non-erasable silicon | Bench (operator) | — | No CI leg can reach a UV part. D-14 gates the phase on it. |

---

## Contradictions of CONTEXT.md — read these first

### C-1. The new wire key must **not** go in `convert_to_programmer`

CONTEXT.md § Integration Points: *"`firestarter_app/firestarter/database.py:520-580` —
`convert_to_programmer`'s wire dict … the natural home for the new key."*

**It is not, on two independent grounds.**

**(a) It is structurally impossible there.** `convert_to_programmer(self, full_eprom_data: dict)`
(`firestarter_app/firestarter/database.py:514`) converts a *database row* to a wire dict. It has no
access to the payload file, the `--address` argument, or the command being run. The region is a
property of the *operation*, not of the *chip*. [VERIFIED: firestarter_app/firestarter/database.py:514-582]

**(b) Putting it there reddens a gate CONTEXT.md did not name.**
`firestarter_app/tests/test_wire_dict_equivalence.py:508` —
`test_wire_key_union_is_exactly_nine_keys()` — captures `convert_to_programmer`'s output across all
746 DB rows and asserts the key union equals exactly:

```python
_EXPECTED_WIRE_KEYS = {
    "algorithm",
    "bus-config",
    "chip-id",
    "flags",
    "memory-size",
    "page-size",
    "pin-count",
    "pulse-delay",
    "vpp_mv",
}
```
[VERIFIED: firestarter_app/tests/test_wire_dict_equivalence.py:175-185, 508-518 — quoted verbatim]

The capture helper reads `db.convert_to_programmer(mapped)` and nothing else
(`tests/test_wire_dict_equivalence.py:208`), so a key added in `_setup_operation` is **invisible to
this gate** and it stays GREEN. A key added in `convert_to_programmer` turns it RED.

**Correct home:** `_setup_operation` (`firestarter_app/firestarter/eprom_operations.py:456`), beside
the read path's existing narrowing arithmetic at `:490-495`.

### C-2. `tests/test_uv_mask.py` does not touch the fake at all

CONTEXT.md D-16.2: *"`tests/test_uv_mask.py:201` leans on the fake's current behaviour, so that is a
coupled edit."*

`tests/test_uv_mask.py` imports exactly two things:

```
15:import pytest
17:from firestarter.chip_test import (
```
[VERIFIED: firestarter_app/tests/test_uv_mask.py:15-17 — full import list, `grep -n "^from\|^import"`]

It imports neither `FakeChip` nor `WriteInitPreflightChip`, and `grep -n "WriteInitPreflightChip\|FakeChip\|blank" tests/test_uv_mask.py` returns only two prose hits at `:290` and `:300`. Line 201 is
`assert target.current_is_probe_read is False` — a `WriteTarget` dataclass default, unrelated to
blankness. [VERIFIED: firestarter_app/tests/test_uv_mask.py:197-203]

**The real coupled file is `firestarter_app/tests/test_chip_test_uv_slot_write.py`**, the only
consumer of the fake:

```
tests/test_chip_test_uv_slot_write.py:81:  from .fake_chip import WriteInitPreflightChip
tests/test_chip_test_uv_slot_write.py:104, :112, :276, :324, :413, :417
```
[VERIFIED: `grep -rn "WriteInitPreflightChip" tests/*.py`, run this session]

Teaching `WriteInitPreflightChip._is_blank` about a region therefore couples to
`test_chip_test_uv_slot_write.py` (6 sites), not to `test_uv_mask.py`.

### C-3. The field must carry an absolute **end address**, not a length

This is the finding that most changes the plan. D-03 names `region-size`; "Claude's Discretion"
leaves "length versus end address" open. **Length is mechanically unsound.** See §"The multi-call
stability constraint" below for the derivation. Short form: `eprom_internal_write_init_body` is
re-entered once per chunk, and `handle->address` is the scan cursor on every call but the first, so
`end = handle->address + region_size` evaluates differently on every call. An absolute end is
stable by construction, needs no arithmetic, and matches `_process_incoming_data`'s existing
comparison shape.

Suggested spelling, honouring D-03's "name it for the region, not for writing" rationale:
wire key `region-end`, handle member `uint32_t region_end`, `0 = absent = whole device` (D-04
unchanged).

### C-4. Firmware CI is **not** three unconditional legs

CONTEXT.md § Established Patterns: *"Firmware CI is exactly three legs: `pio test -e native`,
`pio test -e native_nodevtools`, and `pytest tests/ -v` (`.github/workflows/build.yml:109-130`)."*

The first is **pull-request-only**:

```yaml
109:      - name: Run native unit tests (DEV_TOOLS, pull requests only)
110:        if: github.event_name == 'pull_request'
111:        run: pio test -e native
```
[VERIFIED: firestarter_fw/.github/workflows/build.yml:109-111 — quoted verbatim]

On a plain push to the milestone branch, only `pio test -e native_nodevtools` (`:123-124`) and
`pytest tests/ -v` (`:129-130`) run. There are also two further unconditional legs CONTEXT.md omits:
`pio run` (`:161-162`, builds uno/uno328pb/leonardo) and "Assert no AVR image gained the dev
commands" (`:164`). The push trigger is `branches: ['**', '!beta']` (`:34`), so `beta` pushes run
`beta-build.yml` instead. [VERIFIED: firestarter_fw/.github/workflows/build.yml:16-44, 109-165]

Consequence for the plan: **the DEV_TOOLS native leg only runs once a PR exists.** A new native test
that passes under `native_nodevtools` but fails under `native` will not be caught on the milestone
branch. Run both locally; the commands are in §"Runnable verify commands".

---

## Project Constraints (from CLAUDE.md)

| Directive | Binding here |
|---|---|
| Serial-protocol changes stay in sync between `serial_comm.py` and `firestarter.cpp` | **Satisfied structurally, not by edit.** `serial_comm.send_json_command` serialises whatever dict it is handed (`firestarter_app/firestarter/serial_comm.py:256`: `json_bytes = json.dumps(command_dict, separators=(",",":")).encode("ascii")`). It enumerates no keys. No `serial_comm.py` change is required or wanted. |
| Constants/flag bits duplicated between `constants.py` and three firmware headers — change in the same commit pair | The new wire key is a **string constant**, not a flag bit. The `JSON_KEY_*` precedent lives at `firestarter_app/firestarter/constants.py:138-147`. No flag bit changes. |
| Messages generated only in the meta repo | **No new message id is needed.** The region change reuses `MSG_ERR_NOT_BLANK`, `MSG_ERR_OUT_OF_RANGE` and `MSG_DATA_PROGRESS`. Do not regenerate `messages.h`/`messages.py`. |
| Board buffer sizes differ (Uno 512, Leonardo 1024) | Measured below — the added key costs ~20 JSON bytes against a 226-byte worst case. No risk. |
| A push to `beta` in either sub-repo PUBLISHES; no path filter | Unchanged and binding. This is a dual-repo lockstep phase. |
| Milestone work forks off `beta` in all three repos; never commit to `beta`/`main` | Current branch in all three checkouts is `v1.40-program-parameter-fidelity`. [VERIFIED: `git rev-parse --abbrev-ref HEAD` in `/workspaces`, `/workspaces/firestarter_fw`, `/workspaces/firestarter_app`] |

---

## The host seam — the open question, closed

### The call graph, measured

```
write_eprom(self, eprom_name, eprom_data_dict, input_file_path, ...)      :1968
  require_acknowledged(...)                                               :2003
  require_page_size(eprom_name, eprom_data_dict, "write")                 :2009
  require_page_alignment(eprom_name, eprom_data_dict, "write",
                         address_str, input_file_path)                    :2010   <-- reads the file
  with self._operation_context(eprom_name, eprom_data_dict,
                               COMMAND_WRITE, operation_flags,
                               address_str) as (cmd_data, ...)            :2014   <-- dict built HERE
      ...
      self._run_state_machine(..., main_phase_handler=self._main_phase_send_data,
                              input_file_path=input_file_path, ...)       :2036
          _main_phase_send_data:  file_size = os.path.getsize(...)        :763
```
[VERIFIED: firestarter_app/firestarter/eprom_operations.py — line numbers from
`grep -n "require_acknowledged\|require_page_size\|require_page_alignment\|with self._operation_context"`
and `grep -n "    def write_eprom\|    def verify_eprom"`, both run this session]

**`input_file_path` is a parameter of `write_eprom`.** It is in scope at line 1968, four calls and
46 lines before the command dict is built at 2014. CONTEXT.md's worry — "the command dict is built
and sent before that" — was about `:763`, which is a *second, later* read inside the MAIN-phase
handler, not the earliest availability.

**Precedent already in the write path**: `require_page_alignment` (`firestarter/page_size_gate.py:136`)
does exactly this arithmetic, pre-connect:

```python
    try:
        start = parse_address(address_str) or 0
    except ValueError as e:
        ...
    try:
        length = os.path.getsize(input_file_path)
    except OSError as e:
        raise PageAlignmentError(...)
```
[VERIFIED: firestarter_app/firestarter/page_size_gate.py:162-172 — quoted verbatim]

So the write path **already** computes `start` and `length` before connecting, in a file whose whole
job is pre-connect guards. `write_eprom` calls it at `:2010`, four lines above `_operation_context`.

### The minimal change — no restructure

`_setup_operation`'s relevant body, verbatim:

```python
        command_dict = eprom_data_dict.copy()                              # :476
        command_dict["cmd"] = cmd                                          # :477
        command_dict["flags"] = eprom_data_dict.get("flags", 0) | operation_flags   # :479
        addr = 0
        if address:
            try:
                addr = parse_address(address) or 0
                command_dict["address"] = addr                             # :484
            except ValueError:
                ...
        # Special handling for read operation size
        if cmd == COMMAND_READ and size:
            try:
                read_size = parse_size(size) or 0
                # 'memory-size' in command_dict will define the end address for read
                command_dict["memory-size"] = addr + read_size             # :495
```
[VERIFIED: firestarter_app/firestarter/eprom_operations.py:476-495 — quoted verbatim]

`addr` is already computed here. The region end is `addr + payload_length`. The only thing missing
is `payload_length`.

**Recommended diff shape (three signatures, one new keyword, no control-flow change):**

1. `_setup_operation(..., region_length: int | None = None)` — add, after the `COMMAND_READ` block:
   ```python
   if region_length is not None and cmd in (COMMAND_WRITE, COMMAND_VERIFY):
       command_dict[JSON_KEY_REGION_END] = addr + region_length
   ```
2. `_operation_context(..., region_length: int | None = None)` — forward it verbatim (the context
   manager already forwards every parameter positionally at `:521-529`).
3. `write_eprom` at `:2014` and `verify_eprom` at `:2115` — pass
   `region_length=os.path.getsize(input_file_path)`.

`COMMAND_WRITE` / `COMMAND_VERIFY` are already imported (`eprom_operations.py:40-41`).
[VERIFIED: firestarter_app/firestarter/eprom_operations.py:40-41]

**Answer to the research question, plainly stated: it can be done without a restructure.** Six lines
of host code across two functions plus one constant.

### D-07 — verify's dict construction is the *same* construction

`verify_eprom` does not build its own dict:

```python
    def verify_eprom(                                    # :2107
        self, eprom_name, eprom_data_dict, input_file_path,
        operation_flags: int = 0, address_str: str | None = None,
    ) -> bool:
        with self._operation_context(                    # :2115
            eprom_name, eprom_data_dict, COMMAND_VERIFY, operation_flags, address_str,
        ) as (cmd_data, buf_size, op_name):
```
[VERIFIED: firestarter_app/firestarter/eprom_operations.py:2107-2120 — quoted verbatim]

**Confirmed: write and verify share one dict-construction path** (`_operation_context` →
`_setup_operation`). One change serves both. `verify_eprom` also receives `input_file_path` as a
parameter, so the size is equally available. Note `verify_eprom` does **not** call
`require_page_alignment`, so it must call `os.path.getsize` itself — a one-liner, and the same
`OSError` surface `write_eprom` already accepts.

**Ordering caveat worth one plan sentence:** `os.path.getsize` raises `OSError` on a missing file.
On the write path `require_page_alignment` already converts that to a `PageAlignmentError` at
`:169-172` — but only for protocol-0x05 parts (it returns early at `:157-159` otherwise). So a
missing file on a non-0x05 write currently first surfaces at `_main_phase_send_data:750`
(`if not os.path.exists(input_file_path): raise EpromOperationError(...)`), i.e. **after** connecting.
Adding a `getsize` at `_setup_operation` time moves that failure earlier for some parts. Decide
deliberately: either guard it (`try/except OSError: region_length = None`, preserving today's
ordering exactly) or accept the earlier, better error. The guarded form is the zero-behaviour-change
option and is what a "one code path, no branch on address presence" (D-05) plan should prefer.

---

## The firmware seam

### `mem_util_blank_check` as it stands today

Full current body, `firestarter_fw/src/proms/memory.cpp:450-513`, quoted verbatim with line
numbers from `grep -n` run this session:

```c
450  void mem_util_blank_check(firestarter_handle_t* handle) {
451      if (!is_operation_in_progress(handle)) {
452          set_operation_in_progress(handle);
453          blank_check_saved_address = handle->address;
454          handle->address = 0;
455      } else {
456          if (handle->address >= handle->mem_size) {
457              clear_operation_in_progress(handle);
458              handle->address = blank_check_saved_address;
459              return;
460          }
461      }
462
463      // for (uint32_t i = handle->address; i < handle->address + BLANK_CHECK_CHUNK_SIZE; i++) {
464      uint32_t end_address = handle->address + BLANK_CHECK_CHUNK_SIZE;
465      for (uint32_t i = handle->address; i < end_address && i < handle->mem_size; i++) {
466          uint8_t val = handle->firestarter_get_data(handle, i);
467          if (val != 0xFF) {
...
480              if (handle->cmd == CMD_BLANK_CHECK) {
                     /* stash offset+value in data_buffer, data_size = 4 */
                 } else {
                     LOG_ERROR_ID_BYTES(MSG_ERR_NOT_BLANK, _b, 4);
                 }
                 handle->response_code = RESPONSE_CODE_ERROR;
                 return;
             }
         }
493      handle->address += BLANK_CHECK_CHUNK_SIZE;
     #ifdef RAW_DATA_PROGRESS
         ...
     #else
501      if (handle->address > handle->mem_size) {
502          handle->address = handle->mem_size;
503      }
509      if (handle->cmd != CMD_BLANK_CHECK) {
510          LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size);
511      }
     #endif
513  }
```
[VERIFIED: firestarter_fw/src/proms/memory.cpp:450-513; line anchors from
`grep -n "blank_check_saved_address\|BLANK_CHECK_CHUNK_SIZE\|void mem_util_blank_check\|handle->cmd == CMD_BLANK_CHECK\|handle->cmd != CMD_BLANK_CHECK\|if (handle->address > handle->mem_size)\|handle->address >= handle->mem_size" src/proms/memory.cpp`]

Supporting facts, all confirmed:

- `static uint32_t blank_check_saved_address;` at `:437`, with the "do not replace it with a heap
  allocation" rationale at `:425-436`. [VERIFIED: memory.cpp:425-437]
- `#define BLANK_CHECK_CHUNK_SIZE 8192` at `:442`. [VERIFIED: memory.cpp:442]
- The emit fork at `:480` is exactly as CONTEXT.md describes. [VERIFIED: memory.cpp:480]
- The `mem_size`-keyed clamp at `:501-502` and the write-init/erase-end emit at `:509-510` are
  exactly as D-06 describes. [VERIFIED: memory.cpp:501-510]
- Declaration to extend: `void mem_util_blank_check(firestarter_handle_t* handle);` at
  `firestarter_fw/include/memory_utils.h:18`. The region form needs a sibling declaration there.
  [VERIFIED: firestarter_fw/include/memory_utils.h:18]

**Four `mem_size` reads in this function, all four must become `end`-relative in the region form:**
`:456` (completion test), `:465` (scan upper bound), `:501` (clamp), `:510` (progress denominator).
`:453` reads `handle->address`, which is the region *start* on the first call.

### The multi-call stability constraint — the load-bearing new finding

`eprom_internal_write_init_body` is called **once per chunk**, not once. The mechanism:

```c
        if (_execute_operation(callback, handle) == ERROR) {
            return ERROR;
        }

        if (is_operation_in_progress(handle)) {
            return RETURN;
        }
```
[VERIFIED: firestarter_fw/src/operation_utils.cpp:203-208 — quoted verbatim, inside
`_execute_operation_house_keeping_func`]

`mem_util_blank_check` sets `is_operation_in_progress` on its first call (`memory.cpp:452`), so the
housekeeping loop returns and re-enters the INIT callback on the next iteration. A 64 KiB part is
8 chunks — 9 entries into `eprom_internal_write_init_body`.

On entry 2..n, `handle->address` is **the scan cursor**, not the region start. Therefore:

- `start = handle->address` is only meaningful on entry 1 — harmless, because the region form only
  *uses* `start` inside the `!is_operation_in_progress` branch.
- **`end = handle->address + region_length` is wrong on every entry after the first.** With
  `region_length = 4096` and a cursor at 8192, entry 2 computes `end = 12288` instead of the correct
  `4096`, and the scan runs past the region. This is a silent correctness bug, not a compile error.

**Two ways out, one clearly better:**

| Option | Mechanism | Assessment |
|---|---|---|
| **Absolute end on the wire** (`handle->region_end`) | `end` is read directly off a handle member that nothing mutates. `start` is `handle->address`, read only on entry 1. | **Recommended.** Zero arithmetic, zero state, matches `_process_incoming_data`'s `handle->address >= X` comparison shape and the read path's existing `memory-size = addr + read_size` overload (`eprom_operations.py:495`). |
| Length on the wire, end latched into a second file static alongside `blank_check_saved_address` | Compute `end` on entry 1, stash it, reuse it. | Works, but adds a second piece of cross-call static state to the one function whose existing static already carries a written warning about its fragility (`memory.cpp:425-436`). Strictly more to get wrong. |

The absolute-end form also makes D-06's three substitutions textual rather than arithmetic:
`handle->mem_size` → `handle->region_end` at `eprom_operations.cpp:90`, `:128`, and
`eprom.cpp:397`, with a `? :` fallback for the `0 = absent` case (see the regex trap in G-1 below —
the fallback must **not** be written inline at `eprom.cpp:397`).

### Caller census — 9 reference sites, not 4

CONTEXT.md D-09 says "the four callers". The measured census, from
`grep -rn "mem_util_blank_check" --include=*.h --include=*.cpp --include=*.c .` (excluding `.pio`):

| Kind | Site | Role |
|---|---|---|
| declaration | `include/memory_utils.h:18` | header |
| definition | `src/proms/memory.cpp:450` | the scan |
| **direct call** | `src/proms/eprom.cpp:145` | **write-init — the one that changes** |
| direct call | `src/proms/flash_intel.cpp:95` | write-init (out of scope, D-10) |
| direct call | `src/proms/flash_nor_unlock.cpp:105` | write-init (out of scope, D-10) |
| fn-ptr assign | `src/proms/eprom.cpp:53` | `CMD_ERASE` → `firestarter_operation_end` |
| fn-ptr assign | `src/proms/eprom.cpp:57` | `CMD_BLANK_CHECK` → `firestarter_operation_main` |
| fn-ptr assign | `src/proms/flash_nor_unlock.cpp:44` | `CMD_BLANK_CHECK` main |
| fn-ptr assign | `src/proms/flash_5v_page.cpp:47` | `CMD_BLANK_CHECK` main |
| fn-ptr assign | `src/proms/eeprom_28c.cpp:151` | `CMD_BLANK_CHECK` main |
| fn-ptr assign | `src/proms/flash_intel.cpp:62` | `CMD_BLANK_CHECK` main |

[VERIFIED: `grep -rn "mem_util_blank_check" --include=*.h --include=*.cpp --include=*.c .` run in
`/workspaces/firestarter_fw` this session]

That is **3 direct calls + 6 function-pointer assignments = 9 reference sites**, plus the
declaration and definition. **D-15.3's source-contract gate must enumerate all of these**, or it
will pass vacuously on a file it forgot. In particular the 6 function-pointer assignments are the
"whole-device entry point" that must keep pointing at the wrapper — a future edit repointing one of
them at the region form is exactly the widening D-15.3 exists to prevent, and a gate that only
counts direct calls would not see it.

The `eprom.cpp:46-59` dispatch, verbatim, for the two sites D-15.2 exercises:

```c
        case CMD_ERASE:
            handle->firestarter_operation_main = eprom_erase_execute;
            if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
                handle->firestarter_operation_end = mem_util_blank_check;
            }
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
```
[VERIFIED: firestarter_fw/src/proms/eprom.cpp:51-59 — quoted verbatim]

### The three denominators — confirmed exactly

`grep -n "MSG_DATA_PROGRESS" src/proms/eprom.cpp src/proms/memory.cpp src/operation_utils.cpp`:

```
src/operation_utils.cpp:235:  LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size);
src/proms/eprom.cpp:397:      LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address + i, handle->mem_size);
src/proms/memory.cpp:510:     LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size);
```
[VERIFIED: run this session — `handle->mem_size` appears at exactly these three sites, and
`grep -n "mem_size" src/proms/eprom.cpp` returns only `:381` (a comment) and `:397`]

CONTEXT.md D-06's three-way split is **confirmed byte for byte**, including that `eprom.cpp:397` is
the only `mem_size` *read* in `eprom.cpp`.

D-06's cheap verification is also confirmed. `_apply_write_progress`'s own docstring:

> *"Applies the frame's `current` and IGNORES its `total` … The write bar is started with the file
> size while the frame carries the chip's memory size — for a short file or an --address-offset
> write those differ, so every frame would tear the bar down and rebuild it."*

and the code: `absolute, _total_ignored = map(int, response.message.split("/"))`.
[VERIFIED: firestarter_app/firestarter/eprom_operations.py:690-721 — quoted verbatim]

### `_process_incoming_data` — the two sites D-06 moves

```c
static inline bool _process_incoming_data(firestarter_handle_t* handle) {
    ...
    if (handle->address >= handle->mem_size) {          // :90  done-condition
        set_operation_to_done(handle);
        return true;
    }
    ...
        case OP_MSG_DATA:
            if (handle->address + handle->data_size > handle->mem_size) {   // :128
                LOG_ERROR_ID(MSG_ERR_OUT_OF_RANGE);
                return false;
            }
```
[VERIFIED: firestarter_fw/src/eprom_operations.cpp:86-131 — quoted verbatim; shared by
`eprom_write` (`:23`) and `eprom_verify` (`:29`), both calling
`op_execute_stateful_operation(_process_incoming_data, handle)`]

### `json_parser.c` — the exact shapes D-03 says to copy

**The `FIELD` macro** (this is what the "offset column" means):

```c
#define FIELD(k, member, cl)                                                 \
    { (k), (uint16_t)(cl), (uint8_t)offsetof(firestarter_handle_t, member),  \
      (uint8_t)sizeof(((firestarter_handle_t*)0)->member) }
```
[VERIFIED: firestarter_fw/src/json_parser.c:108-110 — quoted verbatim]

The offset column is a **`uint8_t`**. The `_Static_assert` proves the compiler-derived
`offsetof(...)` still fits in it, and that `sizeof(...)` fits the 32-bit `memcpy` store at
`json_parser.c:255` (`memcpy((uint8_t*)handle + offset, &value, width);`).
[VERIFIED: json_parser.c:255]

**What adding a handle member does to it:** `offsetof` and `sizeof` are compiler-derived, never
literals (the macro's own comment at `:100-107` states this is deliberate, because "the AVR and
native struct layouts differ at every member from `protocol` down"). So adding a member does **not**
require hand-editing any offset. It requires exactly three additions and one edit:

1. **PROGMEM key string**, after `key_page_size`:
   ```c
   /* Per-chip page-write size delivered by the host.
    * Wire key is the HYPHEN form "page-size" -- the internal database key
    * programming.page_size uses an underscore, so a PROGMEM string written
    * against the underscore form would silently never match. */
   const char key_page_size[]     PROGMEM = "page-size";
   ```
   [VERIFIED: firestarter_fw/src/json_parser.c:66-70 — quoted verbatim, the template]

2. **`FIELD(...)` table row**, last in `key_parsers[]`:
   ```c
       /* page-size -> handle->page_size */
       FIELD(key_page_size, page_size, 0),
   };
   ```
   [VERIFIED: firestarter_fw/src/json_parser.c:150-152 — quoted verbatim, the template. `0` in the
   third column means "no clamp"; the region end must use `0`, since a clamp is a `uint16_t` and a
   512 KiB part needs 20 bits.]

3. **Offset `_Static_assert`**, in the guard block:
   ```c
   _Static_assert(offsetof(firestarter_handle_t, page_size) < 256 &&
                      sizeof(((firestarter_handle_t*)0)->page_size) <= 4,
                  "page_size: a struct reorder moved it past the uint8_t offset column's range, "
                  "or gave it a width the 32-bit store cannot carry");
   ```
   [VERIFIED: firestarter_fw/src/json_parser.c:204-207 — quoted verbatim, the template]

4. **EDIT, not add — the row-count assert:**
   ```c
   _Static_assert(sizeof(key_parsers) / sizeof(key_parsers[0]) == 11,
                  "key_parsers row count changed -- add or remove the matching per-member offset "
                  "guard above to match");
   ```
   [VERIFIED: firestarter_fw/src/json_parser.c:208-210 — quoted verbatim]
   **`11` must become `12`.** Forgetting this is a compile-time failure, which is the good outcome —
   but it is the one line in the file that is a literal and must be hand-changed.

**Correction to a CONTEXT.md citation:** D-16.3 cites *"the `_Static_assert` on the handle member's
offset (`firestarter_fw/src/json_parser.c:164-166`)"*. Lines 164-166 are inside the explanatory
comment block (`:155-163`); the asserts themselves run `:167-207` and the row-count assert is at
`:208-210`. `page_size`'s own assert is at `:204-207`. Cite those.

**The per-command reset block**, verbatim — this is the D-03 "reset per command" shape:

```c
int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle) {
    handle->address = 0;
    handle->ctrl_flags = 0;
    ...
    handle->chip_id = 0;
    /* page_size resets to 0 exactly like chip_id above. handle is a
     * single file-scope global with no per-command memset, and page-size is
     * emit-when-present, so without this reset a 128 parsed for one chip
     * would persist into the next command and "absent means 64" becomes
     * false in practice -- the exact overrun this reset exists to prevent.
     * The two read-timing knobs (read_settling_us, read_strobe_us) are
     * deliberately NOT in this reset block: that is a pre-existing latent
     * instance of the same defect, filed as a todo, so their absence here is
     * not an oversight. */
    handle->page_size = 0;
```
[VERIFIED: firestarter_fw/src/json_parser.c:257-275 — quoted verbatim]

**The reset is load-bearing for D-04 and cannot be skipped.** `handle` is a single file-scope global
(`firestarter_fw/src/firestarter.cpp:33`: `firestarter_handle_t handle;`) with no per-command
`memset`. Without the reset, a `region-end` from one write would persist into the next command — and
because D-04 makes `0 = whole device`, a stale non-zero value would **narrow** a subsequent
whole-device blank check. That is a fail-**open** direction, strictly worse than the `page_size` case
the comment describes. [VERIFIED: firestarter_fw/src/firestarter.cpp:33]

**The handle struct and `page_size`'s comment template:**

```c
    uint16_t chip_id;
    uint16_t page_size;          /* per-chip page-write size delivered by the host over the wire;
                                   * 0 = absent. Reset per command in json_parse,
                                   * exactly like chip_id above. */
    char data_buffer[DATA_BUFFER_SIZE];
```
[VERIFIED: firestarter_fw/include/firestarter.h:186-190 — quoted verbatim]

Place the new `uint32_t region_end` **after** `page_size` and **before** `data_buffer`. Rationale:
`data_buffer` is `DATA_BUFFER_SIZE` (1024 on leonardo), so every member after it has an offset above
255 and would blow the `uint8_t` offset column. `offsetof(page_size)` today is comfortably small;
adding 4 bytes before `data_buffer` keeps every parsed member below 256. **Do not place the new
member after `data_buffer`** — the `_Static_assert` would catch it, but only after a confusing
diagnostic.

### Wire-frame budget — the trap checked and cleared

`NUMBER_JSNM_TOKENS` is 64 (`firestarter_fw/include/json_parser.h:17`) and the parse is
`jsmn_parse(&parser, handle->data_buffer, handle->data_size, tokens, NUMBER_JSNM_TOKENS)`
(`firestarter_fw/src/firestarter.cpp:57`). Adding a key-value pair costs 2 tokens.
[VERIFIED: firestarter_fw/include/json_parser.h:17, src/firestarter.cpp:54-57]

Measured worst case across all 746 DB rows, using `convert_to_programmer` plus `cmd`/`flags`/
`address` exactly as `_setup_operation` builds them:

```
worst tokens/len: (46, 226)
part: ASD AE29F1008
json: {"memory-size":131072,"algorithm":5,"pin-count":32,"vpp_mv":12000,"pulse-delay":0,
       "chip-id":56001,"bus-config":{"bus":[0,1,...,21],"rw-pin":22},"page-size":128,
       "flags":0,"cmd":8,"address":0}
```
[VERIFIED: script run this session against the real DB via
`/workspaces/firestarter_app/.venv/ci-replica/bin/python`, `EpromDatabase(skip_local_override=True)`]

**48 of 64 tokens and ~246 of 512 bytes after the addition.** Ample headroom on the Uno. No risk.

### Flash headroom — measured, because nothing automated checks it

CONTEXT.md is right that there is no size gate: `scripts/` holds only
`check_cmake_manifest.py`, `check_erase_no_vpp.py`, `check_landing_range.py`,
`check_orphan_provisional.py`; `scripts/baseline/` does not exist.
[VERIFIED: `ls scripts/ scripts/baseline/` run this session]

`pio run` baseline on the current tree:

| env | Flash used | Board JSON max | Real ceiling | Headroom |
|---|---|---|---|---|
| uno | 21698 B (66.2%) | 32768 | 32768 | ~11 KB |
| uno328pb | 21742 B (66.4%) | 32768 | 32768 | ~11 KB |
| leonardo | 23816 B (72.7%) | 32768 *(overridden)* | **28672** (Caterina) | **4856 B** |

[VERIFIED: `pio run` in `/workspaces/firestarter_fw`, run this session]

`board_upload.maximum_size = 32768` at `platformio.ini:82` deliberately overrides the Caterina-reduced
28672, with the file's own written warning that "the linker no longer protects the top 4096 B".
[VERIFIED: firestarter_fw/platformio.ini:78-82]

**So the linker will not fail** if this change pushes leonardo past 28672 — it will silently produce
an image that overwrites the bootloader. 4856 B is generous for this change, but the plan should
record a post-change `pio run` measurement rather than assume it.

---

## Gates that will redden, and exactly how to re-derive each

### G-1. `tests/test_progress_emission_is_leonardo_only.py` — **NOT NAMED IN CONTEXT.md. This one WILL break.**

```python
    arg2 = re.sub(r"\s+", "", hits[0].group("arg2"))
    assert arg2 == "handle->mem_size", (
        "expected the emit's second argument to be handle->mem_size (the "
        f"chip's absolute geometry), found {hits[0].group('arg2')!r} -- "
        "D-04: 0xE0 must keep exactly one payload meaning across its two "
        "emitters; a block-relative pair would give the id a second "
        "meaning depending on which operation emitted it.\n"
```
[VERIFIED: firestarter_fw/tests/test_progress_emission_is_leonardo_only.py:606-613 — quoted verbatim]

D-06 changes exactly this argument at `eprom.cpp:397`. **Three distinct hazards, all in one gate:**

**(a) The literal assertion.** `arg2 == "handle->mem_size"` must be updated to the new spelling.
Straightforward — but the gate's own message names *a design argument* ("0xE0 must keep exactly one
payload meaning"), not just a string. The plan must **state the argument it is overruling**: after
D-06, 0xE0's denominator means "the end of the operation's range", which is `mem_size` for a
whole-device operation and `region_end` for a bounded one — one meaning, expressed by a field that
happens to equal `mem_size` when absent. Update the gate's docstring and message text with that
reasoning, in the same commit. Do not silently swap the string.

**(b) A regex trap that will read as a phantom failure.** The `arg2` capture group is
`(?P<arg2>[^,()]+?)` — [VERIFIED: test_progress_emission_is_leonardo_only.py:311, quoted verbatim].
It **cannot match an expression containing parentheses**. So writing

```c
LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address + i,
                    (handle->region_end ? handle->region_end : handle->mem_size));
```

makes `_EMIT_BLOCK_RE` match **zero** blocks, and Coverage 5 and 6 both fail with
*"expected exactly 1 time-gated MSG_DATA_PROGRESS emit block … found 0"* — a message that points
nowhere near the real cause. The module's own comment at `:290-306` records that this exact class of
breakage already happened once during the `w27c512-write-slow-3x` session. **Resolve the absent-case
fallback into a plain local or a bare handle member before the emit**, e.g.

```c
const uint32_t op_end = handle->region_end ? handle->region_end : handle->mem_size;
...
LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address + i, op_end);
```

and then assert `arg2 == "op_end"`. This also keeps the same resolution reusable at
`eprom_operations.cpp:90` and `:128`, and is an argument for **resolving the fallback once, at
`json_parse` time or at write-init entry**, rather than at each of the three use sites.

**(c) The forbidden-needle check.** The same test asserts the needle
`_NEEDLE_DATA_SIZE_PAYLOAD = "handle" + "->data_size"`
[VERIFIED: test_progress_emission_is_leonardo_only.py:265] does not appear inside the emit's own
block. Nothing in this phase wants `data_size` there, so this leg stays green — but do not
accidentally write `handle->address + handle->data_size` as a bound near the emit.

### G-2. `tests/test_protocol_branch_inventory.py` + `tests/golden/protocol_branch_inventory.json`

**CONTEXT.md's claims, adjudicated:**

| CONTEXT.md claim | Verdict |
|---|---|
| "pins `src/proms/eprom.cpp`'s blob SHA" | **Confirmed.** `test_blob_shas_match_the_recorded_inventory` runs `git rev-parse HEAD:src/proms/eprom.cpp` and compares to `meta.blob_shas`. Current value `c16c1972b4d30779b77fc5b03e0f44d08810ec1b` matches `git hash-object src/proms/eprom.cpp`. [VERIFIED: test file `:392-410`; `git hash-object` run this session] |
| "every branch predicate positionally on `(line, predicate, keyed_on, tier)`" | **Confirmed verbatim.** `test_branch_sites_match_the_recorded_inventory` builds exactly that 4-tuple from both recorded and live and compares index by index, naming the first divergence. [VERIFIED: test file `:413-441`] |
| "currently 21 sites" | **Contradicted — there are 22.** `len(inventory["sites"]) == 22`. The `counts` block still reads `{"total_sites": 21, "protocol_keyed_sites": 1, "other_sites": 20}` while `meta.recorded_by`'s own final paragraph says *"total_sites 21 -> 22, other_sites 20 -> 21"*. **`counts` is never read by any test** (`grep -n "counts" tests/test_protocol_branch_inventory.py` returns nothing), so the drift is silent. Fix it for honesty while re-deriving; it is not a gate. [VERIFIED: python dump of the golden + `grep -n "counts"`, both run this session] |
| "`{"line": 144, "predicate": "if (!is_flag_set(FLAG_SKIP_BLANK_CHECK))"}`" | **Confirmed** — present at index 9 of `sites`. |
| "the re-derivation and the source change must land in the **same commit**" | **Confirmed**, and the golden's `meta.recorded_by` records that this property has been **deviated from once before**, with the deviation stated rather than hidden (Phase 199 Plan 03: "the gate was legitimately RED in between"). That precedent exists if the plan's task boundaries make one-commit impossible. |

**Baseline: GREEN.** `pytest tests/test_protocol_branch_inventory.py -o addopts="" -q` → `7 passed in 0.08s`. [VERIFIED: run this session]

**Is there a re-derivation script? No.** `meta.how_to_update` says:

> *"re-derive it by running an independent parse against the new file (never hand-edit a line
> number, a keyed_on set, a class, or a count merely to make a surprise disappear) … Diffing the
> extractor's live output against this JSON is the only sanctioned way to update it."*
[VERIFIED: golden `meta.how_to_update`, quoted verbatim]

**The exact procedure** (the module's own extractor, invoked directly — this satisfies "the
extractor's live output"):

```bash
cd /workspaces/firestarter_fw
python3 - <<'PY'
import json, sys
sys.path.insert(0, "tests")
from test_protocol_branch_inventory import _extract_predicates, _SCAN_EPROM, _INVENTORY_JSON
live = _extract_predicates(_SCAN_EPROM.read_text())
inv  = json.loads(_INVENTORY_JSON.read_text())
old  = {(s["predicate"], tuple(s["keyed_on"]), s["tier"]): s.get("reason") for s in inv["sites"]}
for s in live:
    key = (s["predicate"], tuple(s["keyed_on"]), s["tier"])
    s["reason"] = old.get(key, "TODO -- NEW SITE: write the reason by hand")
inv["sites"] = live
inv["counts"] = {
    "total_sites": len(live),
    "protocol_keyed_sites": sum(1 for s in live if s["tier"] == "protocol"),
    "other_sites": sum(1 for s in live if s["tier"] != "protocol"),
}
print(json.dumps(inv["counts"]))
print([s["line"] for s in live if s["reason"].startswith("TODO")])
_INVENTORY_JSON.write_text(json.dumps(inv, indent=2) + "\n")
PY
# then, BEFORE staging:
git hash-object src/proms/eprom.cpp        # -> meta.blob_shas["src/proms/eprom.cpp"]
git rev-parse HEAD                          # -> meta.recorded_at_head (this commit's PARENT)
```

Four non-obvious obligations the procedure must honour:

1. **Every site needs a non-empty `reason`.** `test_inventory_is_non_vacuous` asserts
   `s.get("predicate") and s.get("reason")` for every entry — but `reason` is **not** part of the
   positional 4-tuple. So a new site needs a hand-written reason; the script above flags them.
   [VERIFIED: test file `:459-473`]
2. **`test_inventory_is_non_vacuous` has a floor of `>= 21` sites.** Not 24 — the module docstring's
   ">= 24" is stale. [VERIFIED: test file `:456-458`]
3. **`test_exactly_one_protocol_keyed_site_at_the_pinned_line` asserts `protocol_lines == [70]`** —
   a hard-coded line number. Line 70 is `switch (handle->protocol)` in `configure_eprom`.
   **Any line inserted above `eprom.cpp:70` breaks this**, including a comment. The write-init edit
   at `:144-145` is safely below it. Do not add a file-header comment. [VERIFIED: test file `:444-454`]
4. **`meta.blob_shas` must come from `git hash-object` on the working tree before staging**, and
   `recorded_at_head` names the **parent** commit. The golden's `recorded_by` field records seven
   prior re-derivations under that exact rule; append an eighth paragraph stating what moved and why.

**Predicted impact of this phase's `eprom.cpp` edit:** adding a region argument to the
`mem_util_blank_check(handle)` call at `:145` and adding the `op_end` local + emit change near
`:390-397` adds **no new branch predicate** if written as recommended (a `? :` in a plain assignment
statement *is* a ternary and **will** be extracted — see below). Every site from the insertion point
downward shifts by the number of lines added.

> **Ternary trap.** `_extract_predicates` extracts **every ternary `?:` condition** whose text
> references a handle field (`test_protocol_branch_inventory.py:322-349`, and `_is_relevant` at
> `:266-274`). So `const uint32_t op_end = handle->region_end ? handle->region_end : handle->mem_size;`
> **adds a new tier-`other` site** keyed on `region_end`+`mem_size`. That is fine and correct — but
> it means the re-derivation adds a row, not merely shifts lines, and that row needs a hand-written
> `reason`. If the plan instead resolves the fallback **inside `json_parse`** (`handle->region_end =
> handle->region_end ? handle->region_end : handle->mem_size` is impossible there — `mem_size` may
> parse after `region-end`) or in `memory.cpp`/`eprom_operations.cpp` rather than `eprom.cpp`, no new
> site appears in the inventory at all. **Resolving it in `eprom_generic_init` or at the top of
> `eprom_internal_write_init_body` keeps it inside `eprom.cpp` and does add a site; resolving it in
> `memory.cpp` does not.** Either is fine; choose deliberately and state which.

### G-3. `tests/test_write_path_source_contract_v131.py` — the shape D-15.3 should follow

711 lines, 12 coverage legs. The reusable structure, all verified by reading the module:

| Element | Location | Why D-15.3 needs it |
|---|---|---|
| `_HERE` / `_REPO_ROOT` computed from `Path(__file__).resolve().parent` | `:146-147` | Closes the `check_permitted_claims.py` `_HERE`-resolves-wrong trap. |
| Two scan targets, one env-seam-overridable and one not | `:148-159` (`_SCAN_EPROM` seam-aware, `_SCAN_MEMORY` **not**) | The seam exists **only** so a planted violation can be scanned; the non-seam target proves a stray env value cannot make the gate vacuous. |
| Concatenation-built needles | `:165-168`, e.g. `_NEEDLE_RETRY_MACRO = "NUMBER" + "_OF_RETRIES"` | So the module's own source does not self-match. |
| Paired negative + positive legs | Coverage 1-4 (absent) / Coverage 5 (present) | *"A deleted call satisfies Coverage 6 vacuously and fails here"* (`:66-72`). **This is the pattern D-15.3 most needs**: a gate that only asserts "no caller passes a region" passes vacuously if every caller is deleted. |
| Explicit non-vacuity leg | Coverage 10, `test_scan_targets_are_non_vacuous` `:637` | Both targets exist, are non-empty, resolve inside the repo, and their comment-stripped text is non-empty. |
| Self-skip-proof legs | Coverage 11 `:667`, Coverage 12 `:696` | No `pytest.skip`, no `@pytest.mark.skipif`, and the needles do not appear verbatim. |
| Comment-stripping before scanning | `_strip_comments` | The real files' comments discuss the forbidden constructs in prose. |

**It already scans `src/proms/memory.cpp`** (`_MEMORY_REL = "src/proms/memory.cpp"`, `:149`). Its
Coverage 6/7/9 legs assert things about `delayMicroseconds`, `mem_util_delay_us` and
`MEM_UTIL_DELAY_US_MAX` — **none of which D-09's split touches**, so this module stays GREEN under
the memory.cpp edit. Confirmed by the baseline run below.

**Concrete D-15.3 leg set, derived from the census in §"Caller census":**
- negative: zero call sites of `mem_util_blank_check_region(` outside `src/proms/eprom.cpp` and
  `src/proms/memory.cpp`;
- negative: zero call sites of `mem_util_blank_check_region(` inside `flash_intel.cpp`,
  `flash_nor_unlock.cpp`, `flash_5v_page.cpp`, `eeprom_28c.cpp`;
- positive: the wrapper `mem_util_blank_check` is defined exactly once and its body passes
  `0` and `handle->mem_size` (a positive counterpart, so deleting the wrapper fails);
- positive: exactly **6** `firestarter_operation_main|end = mem_util_blank_check` assignments, at
  the 6 sites listed in the census, and **zero** assignments of the region form to a function
  pointer (the region form's signature does not match the pointer type, so this is belt-and-braces —
  say so in the docstring rather than implying a type error is possible);
- positive: exactly **1** `mem_util_blank_check_region(` call in `eprom.cpp` and it is inside the
  brace-matched body of `eprom_internal_write_init_body`.

### G-4. `tests/test_flash_path_record_sync.py` — **BASELINE RED IN THIS DEVCONTAINER, 17 FAILURES**

**Not caused by this phase. Will be blamed on it if the plan does not say so.**

```
cd /workspaces/firestarter_fw && python3 -m pytest tests/ -o addopts="" -q
  ...
  17 failed, 284 passed in 16.22s
```
[VERIFIED: run this session]

Root cause, from the failure trace:

```
tests/test_flash_path_record_sync.py:425: in _copy_text
    return _meta_doc().read_text()
tests/test_flash_path_record_sync.py:377: in _meta_doc
    return meta_path(".planning", _META_DOC_REL)
parts = ('.planning', 'v1.23-FLASH-PATH-DECISION.md')
```
[VERIFIED: `pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_three_tiers_and_non_retirement -o addopts="" -q`, run this session]

`_META_DOC_REL = "v1.23-FLASH-PATH-DECISION.md"` (`tests/test_flash_path_record_sync.py:77`) is
resolved under `META_ROOT/.planning/`, but the file now lives at
`/workspaces/.planning/milestones/v1.23-FLASH-PATH-DECISION.md`. `ls /workspaces/.planning/v1.23-FLASH-PATH-DECISION.md`
→ *No such file or directory*. The `.planning` layout reorganisation moved it and the scan path was
never updated. [VERIFIED: both `ls` commands run this session]

**Why CI is green and the devcontainer is not.** `META_ROOT` defaults to the firmware repo's parent,
`META_PRESENT = (META_ROOT / ".git").exists()`, and the legs carry `@requires_meta`
(`tests/meta_presence.py:74-96`). In CI the firmware repo is checked out standalone — no parent
`.git` — so all 17 legs **skip**. In `/workspaces`, `.git` exists, so `MissingScanTargetError` fires
by design (the module's own docstring calls this "the hard-failure half of the split").
[VERIFIED: firestarter_fw/tests/meta_presence.py:64-96, quoted verbatim]

**Workaround for any local verify block, confirmed working:**

```bash
cd /workspaces/firestarter_fw
mkdir -p /tmp/no-meta
FIRESTARTER_META_ROOT=/tmp/no-meta python3 -m pytest tests/ -o addopts="" -q
# -> 269 passed, 32 skipped in 14.55s
```
[VERIFIED: run this session — exact output quoted]

The env var **must** be set in the child process environment (it binds at import time;
`meta_presence.py:79`). A monkeypatch will not work.

**Recommendation:** the plan's verify blocks should use the `FIRESTARTER_META_ROOT` form and state
in a comment that it reproduces CI's meta-absent condition. Repairing `_META_DOC_REL` is a separate,
out-of-scope fix (it belongs with the `.planning` layout change that caused it) — but the plan
**must** say the 17 failures are pre-existing, or the first executor to run `pytest tests/ -v` will
halt.

### G-5. `firestarter_app/tests/fake_chip.py` — D-16.2 confirmed verbatim

```python
243  class WriteInitPreflightChip(FakeChip):
...
265      def _is_blank(self) -> bool:
266          if self.blank_override is not None:
267              return self.blank_override
268          return bytes(self.data) == b"\xff" * self.memory_size
...
282          if not (operation_flags & FLAG_SKIP_BLANK_CHECK) and not self._is_blank():
283              self.last_firmware_error_code = MSG_ERR_NOT_BLANK
284              self.last_firmware_error_message = (
285                  "Error: EPROM not blank at address 0x000000, value 0xAB"
286              )
287              return False
```
[VERIFIED: firestarter_app/tests/fake_chip.py:243, 265-268, 282-287 — quoted verbatim]

**D-16.2's vacuity claim is exactly right.** The fake models the whole-device check precisely, so a
`write -a` leg against it passes vacuously today. The base-class `FakeChip.write_eprom` already
knows about regions — `start = _parse_addr_or_size(address_str) or 0` at `:147`, and it slices
`self.data[start:end]` at `:153-157` — so the region arithmetic the fake needs already exists one
level up. [VERIFIED: firestarter_app/tests/fake_chip.py:137-157]

**What the fake must learn**, minimally and additively:

```python
    def _is_blank(self, start: int = 0, end: int | None = None) -> bool:
        if self.blank_override is not None:
            return self.blank_override
        end = self.memory_size if end is None else end
        return bytes(self.data[start:end]) == b"\xff" * (end - start)
```

with `write_eprom` computing `start = _parse_addr_or_size(address_str) or 0` and
`end = start + os.path.getsize(input_file_path)`, mirroring what the base class already does at
`:147-157`. Keeping `blank_override` as the first check preserves every existing caller.
The default-argument form keeps the no-argument call signature working, so the 6 call sites in
`test_chip_test_uv_slot_write.py` (C-2) need no edit unless they assert on the refusal.

`FakeChip.check_eprom_blank` at `:205-211` uses the same whole-buffer comparison and models the
**standalone** blank-check command — **BLANK-02 says that behaviour must not change.** Leave it
alone. [VERIFIED: firestarter_app/tests/fake_chip.py:205-211]

### G-6. **Host-side source-scanning gates were BANNED by operator ruling on 2026-09-14** — bears directly on D-16.3

This is the most consequential unnamed constraint. `firestarter_app` commit `088d2b7`,
*"test: remove source-introspecting tests from the host suite"*:

> *"Operator ruling: source-text scanning is not a legitimate testing technique, and the ruling
> covers ast-based introspection as well as literal substring matching. Keep criterion: only
> data-driven tests that exercise production code."*
>
> *"Deleted 24 modules: cross-repo parity scanners (**json_key_parity**, sdp_table_parity,
> **revision_constants_parity**, parse_gate_admission, cap03_ack_layout_parity) …"*
>
> *"Context: the v1.38 submodule rename moved the sibling checkout out from under fw_presence.py's
> hardcoded FW_ROOT, so all 71 @requires_fw legs began skipping. No CI workflow in either repository
> sets FIRESTARTER_FW_ROOT or checks out the firmware, so those legs had never run in CI at all …
> That is the failure mode of the technique: host-side source-scanning gates fail open."*
[VERIFIED: `git log -1 --format=%B 088d2b7` in `/workspaces/firestarter_app`, quoted verbatim]

Consequences for D-16.3 ("Host — constants and wire parity … so the host key and the `json_parser.c`
`FIELD` entry cannot drift"):

1. **`json_key_parity` — the exact gate D-16.3 describes — was deliberately deleted.** Re-creating it
   re-violates a standing operator ruling.
2. **`tests/test_revision_constants_parity.py` no longer exists.** Only `__pycache__` artefacts
   remain (`find . -name "*revision_constants*"` → three `.pyc` files, no `.py`). The comment in
   `firestarter_fw/include/firestarter.h:181-184` — *"bidirectionally pinned at max 0x100 by
   firestarter_app/tests/test_revision_constants_parity.py"* — **is stale and names a file that does
   not exist.** [VERIFIED: `find`, run this session; firestarter.h:181-184 quoted]
3. **`tests/fw_presence.py` does not exist either** (`ls` → no such file), despite
   `firestarter_fw/tests/meta_presence.py:67-69` still citing "firestarter_app/tests/fw_presence.py's
   sibling arithmetic". Also stale. [VERIFIED: `ls tests/fw_presence.py`, run this session]
4. **No host test reads any firmware source today.** `grep -rn "firestarter_fw\|FIRESTARTER_FW"
   tests/*.py` returns only URL-slug assertions in `test_endpoint_constants.py`,
   `test_fw_list_failure_vs_empty.py` and `test_fw_update_dead_endpoint.py`. [VERIFIED: run this session]

**The compliant shape that survived the purge** — this is what D-16.3 should copy:

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
[VERIFIED: firestarter_app/tests/test_eprom_operations.py:283-296 — quoted verbatim; still live,
survived `088d2b7`]

It asserts a **production constant against a literal**, reads no file, and names the firmware
declaration in prose. The firmware half of the parity obligation stays in the firmware repo, where
source-contract gates are still the house pattern (G-3). **Split the obligation across the two
repos; do not rebuild a cross-repo scanner.**

There is also a second live leg worth copying — `test_read_timing_settling_emitted_in_command`
(`tests/test_eprom_operations.py:314+`) monkeypatches `_setup_operation` to capture the command dict
and asserts the key is present. That is a **data-driven** emission test, exactly compliant, and it is
the right shape for pinning that the new key reaches the wire on write **and** on verify (D-05/D-07).
[VERIFIED: firestarter_app/tests/test_eprom_operations.py:266-274, 314-320]

### G-7 … G-9. Gates checked and cleared

| Gate | Touches | Verdict |
|---|---|---|
| `firestarter_app/tests/test_wire_dict_equivalence.py` | `convert_to_programmer` output only | **GREEN if and only if C-1 is honoured.** RED if the key goes in `database.py`. |
| `firestarter_fw/tests/test_jsmn_token_layout_source_contract_v158.py` | the `jsmntok` struct fields only (`:276`, `:336`) | Unaffected by a `key_parsers` row or a handle member. |
| `firestarter_fw/tests/test_golden_trace_identity.py`, `test_trace_segment_exhaustiveness_v131.py` | trace goldens | Green in the baseline run. D-15 already rules out using a trace diff as *evidence*; these are not *broken* by the change either, per the 269-passed baseline. Re-run after the edit to confirm. |
| `firestarter_fw/tests/test_hv_routing_source_contract_v142.py` | `eprom.cpp` HV routing | Green in baseline; the region change touches no HV predicate. Re-run. |
| `firestarter_app` ruff (`ruff check firestarter/ tests/`, `ruff format --check firestarter/ tests/`) | all new host code | Both are CI gate steps (`ci.yml:57-61`). `line-length = 88`, `target-version = "py311"` (`pyproject.toml:100-101`). |
| `firestarter_app` coverage floor `--cov-fail-under=70` | whole host suite | `ci.yml:64`. Six added lines will not move it. |

---

## The native test harness

### Does `test_val_eprom` exist, and does it run in both envs?

**Yes and yes.**

```
test/native/avr/test_val_eprom/host_stubs.cpp        131 lines
test/native/avr/test_val_eprom/test_val_eprom.cpp    388 lines
```
[VERIFIED: `ls` + `wc -l`, run this session]

`native/avr/test_val_eprom` is listed in `[native_base] test_filter` (`platformio.ini:85-102`), and
both `[env:native]` (`:134`) and `[env:native_nodevtools]` (`:141`) declare `extends = native_base`.
So **one filter serves both envs** — CONTEXT.md's D-16.1 claim is confirmed.
[VERIFIED: firestarter_fw/platformio.ini:83-145]

Baseline: `pio test -e native_nodevtools` → **232 test cases: 232 succeeded in 00:01:04.841**, with
`native/avr/test_val_eprom PASSED 00:00:01.214`. [VERIFIED: run this session]

### The `firestarter_get_data` mock — and the defect that blocks D-16.1 as written

`firestarter_get_data` is **not** directly mockable. It is set by the production dispatcher:

```c
    handle->firestarter_get_data = memory_get_data;
```
[VERIFIED: firestarter_fw/src/proms/memory.cpp:78; `memory_get_data` defined at `:319`]

`memory_get_data` drives the real address bus and then calls `rurp_read_data_buffer()`. **That stub
is the seam.** `test_val_eprom/host_stubs.cpp` overrides it (`#define HOST_STUBS_CUSTOM_READ_DATA_BUFFER`
at `:36`, before the shared include) with a stateful model:

```c
#define VAL_EPROM_READBACK_SLOTS 16

struct val_eprom_readback_t { uint8_t target; uint8_t converge_after; uint8_t read_count; };
static val_eprom_readback_t s_val_readback[VAL_EPROM_READBACK_SLOTS];

extern "C" uint8_t rurp_read_data_buffer() {
    uint8_t idx = 0;
    for (int i = s_bus_recording_count - 1; i >= 0; i--) {
        if (s_bus_recording[i].reg == LEAST_SIGNIFICANT_BYTE) {
            idx = (uint8_t)(s_bus_recording[i].data & (VAL_EPROM_READBACK_SLOTS - 1));
            break;
        }
    }
    val_eprom_readback_t* st = &s_val_readback[idx];
    uint8_t result = (st->read_count < st->converge_after) ? 0xFF : st->target;
    st->read_count++;
    return result;
}
```
[VERIFIED: firestarter_fw/test/native/avr/test_val_eprom/host_stubs.cpp:86-131 — quoted verbatim]

**The blocking defect for D-16.1:** the byte index is `address & 0x0F`. The model has **16 slots and
aliases modulo 16 across the entire address space.** Seeding "non-blank at address A" via
`val_readback_seed(A & 15, 0x00, 0)` also makes A±16, A±32, … non-blank — *including addresses
inside the target region*. The region-scoped blank check would then legitimately find a non-blank
byte inside the region and refuse, and the test would go RED for the wrong reason and stay RED after
the fix.

The stub's own comment concedes its scope: *"That is valid for a block based at address 0 because
LOOP_BUS_CONFIG_0x07 leaves address bits 0-7 identity-mapped"* — it was built for a 16-byte
write-cadence block, not an address-space-wide scan. [VERIFIED: host_stubs.cpp:65-84]

**What the plan must therefore add:** an address-keyed seeding facility in
`test/native/avr/test_val_eprom/host_stubs.cpp`. The smallest sufficient form is a sparse list of
`(absolute_address, value)` pairs consulted before the 16-slot model, with a full absolute index
recovered from **both** `LEAST_SIGNIFICANT_BYTE` and `MOST_SIGNIFICANT_BYTE` (and
`TOP_ADDRESS`, for parts above 64 KiB) writes in the recording, rather than the LSB alone.
Alternative, cheaper and equally valid: a flat `uint8_t` shadow array sized to a **small** `mem_size`
(e.g. `mem_size = 16384` → two `BLANK_CHECK_CHUNK_SIZE` chunks, 16 KB of host RAM), addressed by the
recovered absolute index. **This is new harness work that CONTEXT.md's "directly reusable" framing
does not account for, and it should be its own plan task.**

Two further mock constraints the plan must respect:

- **`HOST_STUBS_MAX_RECORDING` is 256** and the recorder drops silently past it; the suite exposes
  `val_recording_saturated()` for exactly this reason, with the written warning *"a dropped tail
  would both corrupt the backward index scan below and make an assert-count assertion quietly
  wrong."* A whole-device blank check over 64 KiB performs ~65536 `mem_util_set_address` calls and
  will saturate the recorder long before it finishes. **If the index recovery depends on the
  recording, keep `mem_size` small** — this is a second, independent argument for the flat shadow
  array with a small `mem_size`. [VERIFIED: host_stubs.cpp:107-115]
- `millis()` is pinned to 0 in `setUp` (`test_val_eprom.cpp:69`), so the time-keyed progress emit
  never fires in this suite. D-15's two legs must not depend on observing a progress frame here.
  [VERIFIED: test_val_eprom.cpp:56-70]

### The reusable driving pattern — `test_val_5v_page.cpp`, confirmed

CONTEXT.md cites `:200-230` and `:785-820`. Both are exactly what it says.

`:207-219` — the handle factory, with the blank-check axis live:

```c
static firestarter_handle_t make_write_init_handle_blank_check_enabled(void) {
    firestarter_handle_t h = {};
    h.protocol   = 0x05;
    h.cmd        = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id    = 0; /* skip chip-id branch in write_init */
    h.mem_size   = 2048;
    h.address    = 0;
    h.data_size  = 0;
    /* ctrl_flags = 0: FLAG_CAN_ERASE clear, FLAG_SKIP_BLANK_CHECK clear
     * (the blank-check axis is live). */
    return h;
}
```
[VERIFIED: firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp:207-219 — quoted verbatim]

`:789-819` — driving init through the dispatched pointer and asserting on the two observables:

```c
void test_5v_page_write_init_no_blank_check_erase02(void) {
    firestarter_handle_t h = make_write_init_handle_blank_check_enabled();
    configure_memory(&h);
    clear_bus_recording();

    h.firestarter_operation_init(&h);

    TEST_ASSERT_FALSE_MESSAGE(is_operation_in_progress(&h), "...");
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code, "...");
```
[VERIFIED: test_val_5v_page.cpp:789-816 — quoted verbatim]

**One inversion the plan must get right.** In the 5v_page case the blank check was *deleted*, so
`is_operation_in_progress` **FALSE** after one call is the oracle that it did not run. On the EPROM
path the check **does** run, so after one `eprom_write_init` call `is_operation_in_progress` will be
**TRUE** (the multi-call INIT loop is pending) and `response_code` will still be OK. The D-16.1 test
must drive `h.firestarter_operation_init(&h)` **in a loop until `is_operation_in_progress` goes
false**, then assert `response_code != RESPONSE_CODE_ERROR`. A single call proves nothing, because
the non-blank byte may live in a later chunk.

`test_val_eprom.cpp`'s own `make_handle` sets `h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;`
and `h.mem_size = 65536` with the comment *"keeps blank_check from NULL-ptr in mock"*
[VERIFIED: test_val_eprom.cpp:79-89, quoted verbatim]. **The new cases need a different factory**
with `ctrl_flags = 0` and a small `mem_size` — do not mutate the shared one; six existing cases
depend on it.

### D-15's two legs — feasibility

| Leg | Feasible in `test_val_eprom` today? | Notes |
|---|---|---|
| D-15.1 multi-chunk resumption through `CMD_BLANK_CHECK` | **Yes**, with `mem_size > 8192` (e.g. 16384 → 2 chunks + completion call) and a `handle.address` seeded non-zero to observe the restore. `blank_check_saved_address` is `static` and file-local, so it is **not directly observable** — the observable is `handle->address` being restored to its pre-call value at completion (`memory.cpp:458`). That is exactly the contract BLANK-02 names. | Drive `handle.firestarter_operation_main(&h)` in a loop; assert the cursor advances by 8192 per call and returns to the seed on the final call. |
| D-15.2 erase-end arm scans from 0 | **Yes.** `configure_eprom` sets `firestarter_operation_end = mem_util_blank_check` for `CMD_ERASE` with `FLAG_SKIP_BLANK_CHECK` clear (`eprom.cpp:51-56`). Seed `handle.address` non-zero, drive `firestarter_operation_end`, assert the first scanned address is 0. | The first scanned address is observable via the recording's first `LEAST_SIGNIFICANT_BYTE`/`MOST_SIGNIFICANT_BYTE` pair after `clear_bus_recording()`. |

---

## Runnable verify commands

### Firmware (`/workspaces/firestarter_fw`)

```bash
# Native, DEV_TOOLS build (CI runs this on PULL REQUESTS ONLY -- run it locally every time)
cd /workspaces/firestarter_fw && pio test -e native

# Native, no-DEV_TOOLS build (CI runs this on every push)
cd /workspaces/firestarter_fw && pio test -e native_nodevtools

# Python gate suite -- MUST set FIRESTARTER_META_ROOT to reproduce CI's meta-absent condition.
# Without it, 17 PRE-EXISTING failures in test_flash_path_record_sync.py mask the real result (G-4).
cd /workspaces/firestarter_fw && mkdir -p /tmp/no-meta && \
  FIRESTARTER_META_ROOT=/tmp/no-meta python3 -m pytest tests/ -v

# Single gate, fast
cd /workspaces/firestarter_fw && python3 -m pytest tests/test_protocol_branch_inventory.py -o addopts="" -q
cd /workspaces/firestarter_fw && python3 -m pytest tests/test_progress_emission_is_leonardo_only.py -o addopts="" -q

# AVR builds + flash headroom (no CI size gate exists -- measure deliberately)
cd /workspaces/firestarter_fw && pio run
```

Measured baselines on the current tree, all run this session:

| Command | Result |
|---|---|
| `pio test -e native_nodevtools` | 232 test cases: 232 succeeded, 00:01:04 |
| `FIRESTARTER_META_ROOT=/tmp/no-meta pytest tests/ -o addopts="" -q` | **269 passed, 32 skipped** in 14.55s |
| `pytest tests/ -o addopts="" -q` (no env var) | **17 failed, 284 passed** — pre-existing, see G-4 |
| `pytest tests/test_protocol_branch_inventory.py -o addopts="" -q` | 7 passed in 0.08s |
| `pio run` | uno 21698 B, uno328pb 21742 B, leonardo 23816 B — all SUCCESS |

Note: the firmware repo has **no `addopts`** in any pytest config, so `-o addopts=""` is harmless
there but not required. It is required in the app repo — see below.

### Host (`/workspaces/firestarter_app`)

```bash
# CI-replica interpreter. CI pins Python 3.11 (.github/workflows/ci.yml:50-52);
# the devcontainer default is 3.12, which masks 3.11-only defects.
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python --version   # -> Python 3.11.16

# Full suite. `-o addopts=""` is REQUIRED: pyproject.toml:97 sets addopts = "-ra -q",
# so a second -q suppresses the pass/fail count line entirely.
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q

# The two lint gates CI runs, verbatim (.github/workflows/ci.yml:57-61)
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m ruff check firestarter/ tests/
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m ruff format --check firestarter/ tests/

# The coverage gate CI runs, verbatim (.github/workflows/ci.yml:63-64)
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ \
  --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```

**Project-memory claims, all re-verified against the real config this session:**

| Memory claim | Verdict |
|---|---|
| `firestarter_app` needs `pip install -e '.[test]'` | **Confirmed** — `ci.yml:54-55`: `run: pip install -e .[test]`. The `.venv/ci-replica` already has it. |
| pytest `addopts` is `-ra -q`, so a doubled `-q` hides the count line | **Confirmed** — `pyproject.toml:95-97`: `[tool.pytest.ini_options]` / `testpaths = ["tests"]` / `addopts = "-ra -q"`. |
| The devcontainer runs 3.12 while app CI pins 3.11; a `.venv/ci-replica` exists | **Confirmed** — `python3 --version` → 3.12.14; `.venv/ci-replica/bin/python --version` → 3.11.16; `ci.yml:48-52` sets up 3.11. |

Measured baseline: `2100 passed in 169.58s` (36 snapshots passed), via the ci-replica interpreter.
[VERIFIED: run this session]

---

## Recorded traps — each re-checked against the live environment

| Trap | Still applies? | Evidence and consequence |
|---|---|---|
| Devcontainer `grep` is `ugrep` and honours `.gitignore`, silently under-scanning | **YES.** `grep --version` → `ugrep 7.8.4`. `/usr/bin/grep` and `/bin/grep` are the **real** GNU grep (203152-byte binaries dated Jan 2024) — `grep` on `PATH` is a ugrep alias. | Every `grep` in this document was run as `/usr/bin/grep`. **Any gate or verify block that shells out to bare `grep` may under-scan.** Note the existing firmware gates do *not* shell out to grep — they read files in Python — so this trap does not affect them. It affects any new shell-based verify leg. |
| `grep -qF` with a dash-leading pattern exits 2, so the gate fails open; use `-qFe` | **YES**, unchanged property of GNU grep. Not triggered by anything in this phase's likely verify blocks (no dash-leading needle), but the `--skip-erase` / `-b` CLI flags are dash-leading and a naive `grep -qF -- "--skip-erase"` in a bench-transcript check would hit it. Use `-qFe`. |
| Devcontainer Python 3.12 vs app CI 3.11 | **YES.** Confirmed above. Use `.venv/ci-replica/bin/python`. |
| Worktrees leave submodules empty | **YES**, and `config.json` has `"use_worktrees": false`, so this phase should not create one. If one is created, `firestarter_fw/` and `firestarter_app/` will be empty and every gate will under-detect. |
| Native trace stubs record no time and miss register-write elision | **YES**, and independently corroborated in-repo: `test_val_eprom/host_stubs.cpp:71-79` states this suite deliberately does **not** define `HOST_STUBS_REAL_REGISTER_UTILS` precisely so there is "no cache-compare elision", and `setUp` pins `millis()` to a constant (`test_val_eprom.cpp:69`). D-15's rejection of the trace diff is well founded. |
| `test_flash_path_record_sync` asserts repo porcelain / needs a commit first | **Superseded.** The current failure is **not** porcelain — it is a stale scan path (G-4). The `FIRESTARTER_META_ROOT` workaround greens it regardless of working-tree state (verified with the tree dirty). |
| `.planning/` layout is `milestones/v1.X-DOC.md`, root holds 10 files only | **YES** — and this is the *cause* of G-4. |
| Firmware CI has no size-baseline gate | **Confirmed.** `scripts/baseline/` does not exist. Leonardo headroom measured above. |

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Getting a new wire field to the firmware | A new command, a flag bit, or an overloaded existing key | One `FIELD(...)` row + one handle member + one reset, copying `page_size` end to end | The table's `offset`/`width` are compiler-derived (`json_parser.c:108-110`); anything hand-written is correct on one architecture and wrong on the other. |
| Narrowing what the firmware writes | Narrowing `memory-size` on writes | The new field | D-08's reason is confirmed live: `eeprom_28c.cpp` derives `mfr_addr` from `handle->mem_size` and drives 12 V on A9. Hardware safety, not style. |
| Resuming a chunked scan across calls | A second static, a heap allocation, or a length recomputed per call | An absolute end address on the handle | `memory.cpp:425-436` carries a written warning about the one static that already exists; C-3 shows a length is wrong across calls. |
| Pinning host↔firmware key parity | A cross-repo source scanner | A literal-pinned host constant (`test_eprom_operations.py:283-296`) + a firmware source-contract gate | Operator ruling `088d2b7`; the technique fails open (71 legs silently skipped for a whole milestone). |
| Detecting that a branch moved in `eprom.cpp` | Eyeballing the diff | Re-derive the branch-inventory golden from the module's own `_extract_predicates` | The golden's `how_to_update` names this as "the only sanctioned way". |
| Seeding a non-blank byte at a chosen address in the native suite | Reusing `val_readback_seed` as-is | An address-keyed extension to `rurp_read_data_buffer` | The existing model aliases modulo 16 (§"Native harness"). |

---

## Common Pitfalls

### Pitfall 1: the phantom "found 0 emit blocks" failure
**What goes wrong:** `test_progress_emission_is_leonardo_only` Coverage 5 and 6 both fail with
*"expected exactly 1 time-gated MSG_DATA_PROGRESS emit block … found 0"*.
**Why:** the `arg2` capture is `[^,()]+?` — an argument containing parentheses (a ternary in
parentheses, a function call, a cast) makes the whole locator miss.
**Avoid:** resolve the region-vs-device fallback into a plain identifier before the emit.
**Warning sign:** two legs failing together with a count of 0 rather than a wrong-value message.

### Pitfall 2: a region end computed per call
**What goes wrong:** the blank check scans past the region on parts larger than 8192 bytes; small
parts pass, so it looks fine on the bench rehearsal and fails on a 512 KiB part.
**Why:** `handle->address` is the scan cursor from entry 2 onward (`memory.cpp:453-454`).
**Avoid:** absolute end on the wire (C-3).
**Warning sign:** a test with `mem_size <= 8192` passing while a multi-chunk one fails — which is
exactly what D-15.1 is for. Write D-15.1 **before** D-16.1.

### Pitfall 3: the region-end value persisting into the next command
**What goes wrong:** a whole-device `blank-check` immediately after a partial `write` scans only the
write's region and reports blank.
**Why:** `handle` is one file-scope global (`firestarter.cpp:33`) with no per-command `memset`; D-04
makes `0` mean "whole device", so a stale value **narrows** — fail-open.
**Avoid:** the `json_parse` reset, in the block at `json_parser.c:257-275`, non-negotiable.
**Warning sign:** a native test that passes in isolation and fails when run after another case.

### Pitfall 4: the branch-inventory golden updated in the wrong commit
**What goes wrong:** the gate reads RED at a commit boundary.
**Why:** `meta.recorded_at_head` must be the source change's **parent**, and `blob_shas` must be
`git hash-object` on the working tree **before staging**.
**Avoid:** one commit carrying both, or — if the plan's task structure forbids it — state the
deviation in `recorded_by`, as Phase 199 Plan 03 already did.

### Pitfall 5: re-running the whole app suite for a six-line change
**What goes wrong:** 170 s per verify block, times every task.
**Avoid:** `-k` the relevant modules for per-task verification and run the full suite once per wave.
Baseline is 2100 tests / 169.58 s.

### Pitfall 6: treating the pre-existing 17 firmware failures as the phase's fault
See G-4. This is the single most likely cause of a spurious halt.

---

## Security Domain

This phase changes a **refusal** into a **conditional refusal** and adds an externally-supplied
value that bounds a hardware operation. The relevant surface is input validation and hardware
safety, not authentication or cryptography.

| ASVS Category | Applies | Standard control, as it exists here |
|---|---|---|
| V2 Authentication | no | Serial link, physically local, no identity model. |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| **V5 Input Validation** | **yes** | The `FIELD(...)` table's SATURATE policy at `json_parser.c:243-249` clamps any value wider than the member to the member's maximum, and `store_field`'s `memcpy` writes exactly `width` bytes at a compiler-derived offset. A `uint32_t region_end` needs `clamp = 0` (no `uint16_t` clamp), and its worst case — a host sending a value larger than `mem_size` — must still be safe. **`min(region_end, mem_size)` at the point of use is the fail-closed form** and costs two instructions. Do not rely on the host to be correct: D-06 itself calls the out-of-range refusal "a fail-closed guard against a host/file mismatch". |
| V6 Cryptography | no | The frame carries CRC8 for integrity only; nothing here changes it. |

| Threat pattern | STRIDE | Mitigation in this phase |
|---|---|---|
| A host (or a corrupted frame) supplies `region_end > mem_size`, widening a scan past the device | Tampering | Clamp to `mem_size` at the point of use; `_process_incoming_data:128`'s `MSG_ERR_OUT_OF_RANGE` remains as the second gate. |
| A stale `region_end` narrows a later whole-device blank check (fail-open) | Tampering / Repudiation | The `json_parse` per-command reset. Pitfall 3. |
| A host omits the field against new firmware, or sends it to old firmware | Tampering | D-04's `0 = whole device` makes both directions degrade to today's behaviour. jsmn ignores unknown keys, so an old firmware silently drops `region-end` and applies the whole-device check — a strictly-stricter, safe degradation. |
| The relaxation escapes to the two out-of-scope protocols | Elevation of privilege (of the write path) | D-15.3's source-contract gate, enumerating all 9 reference sites (§"Caller census"). |
| A narrowed `memory-size` reaches `eeprom28c_check_chip_id` and drives 12 V on A9 at an arbitrary address | Tampering / hardware damage | **Avoided by construction** — D-08 keeps `mem_size` meaning device size. This is why the new field exists rather than an overload. |

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | `pio test`, `pio run` | ✓ | 6.2.0 (`/usr/local/bin/pio`) | — |
| `firestarter_fw` checkout | every firmware leg | ✓ | branch `v1.40-program-parameter-fidelity` | — |
| `firestarter_app` checkout | every host leg | ✓ | branch `v1.40-program-parameter-fidelity`, HEAD `b3a777e` | — |
| Python 3.11 (CI replica) | host suite, ruff, coverage | ✓ | 3.11.16 at `.venv/ci-replica/bin/python` | `.venv311`, `.venv-ci-188` also present |
| Python 3.12 (devcontainer default) | firmware `pytest tests/` | ✓ | 3.12.14 | — |
| GNU grep | any shell-based scan | ✓ | `/usr/bin/grep` (bare `grep` is ugrep 7.8.4) | always use the absolute path |
| `git` | branch-inventory gate (`_resolve_git`, fail-closed) | ✓ | on `PATH` | none — the gate FAILS, never skips, if absent |
| W27C512 (`0xDA08`) | D-12 rehearsal | operator bench | validated 2026-08-31 | — |
| TMS27C512 (`0x9785`) | D-12 confirmation | operator bench | validated 2026-09-12 on fw `3.0.0b27` | **none — D-14 forbids deferral** |
| AVR board (leonardo or uno-class) | the bench runs | operator bench | — | — |

**Blocking with no fallback:** the bench session (D-14). Everything else is available now.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | Adding `uint32_t region_end` between `page_size` and `data_buffer` keeps `offsetof` below 256 on both AVR and native. | Firmware seam / json_parser | None at runtime — the `_Static_assert` at build time is exactly the check. Listed because I computed it by reading the struct, not by compiling. Resolved the moment the plan's first firmware task builds. |
| A2 | The recommended six-line host diff does not disturb the read path's `memory-size` narrowing, because the new key is emitted only for `COMMAND_WRITE`/`COMMAND_VERIFY`. | Host seam | Low — a missing command guard would add the key to reads, where the firmware would read it into `region_end` and (with D-06 scoped to `_process_incoming_data`) ignore it. Still, guard explicitly. |
| A3 | `test_golden_trace_identity.py` and `test_trace_segment_exhaustiveness_v131.py` stay GREEN under the `eprom.cpp`/`memory.cpp` edits. | G-7 | Medium. I confirmed they are green *in the baseline*, not green *after the change* — the change does not exist yet. The plan must re-run them; if a trace golden does move, the re-derivation obligation is the trace suite's own, not documented here. |
| A4 | A flat shadow array with `mem_size = 16384` is a workable replacement for the 16-slot readback model. | Native harness | Low. The defect in the current model is proven (modulo-16 aliasing, quoted source); the *replacement* is a recommendation, not a measurement. The planner may choose the sparse-list form instead. |
| A5 | The narrowed `uv-write-shortcut` divergence now warrants "neither" (no new report key). | Folded todos | Low, and it is a judgement the phase is asked to *record*, not to verify. Supporting facts confirmed: `plan.is_uv` now reaches the report (`firestarter_app/firestarter/diagnostic_report.py:1022`, `"is_uv": self.plan.is_uv`) and `write_current_source` is exported (`diagnostic_report.py:946`), so both of the todo's stated reasons for "neither" now hold *with* RPT-A4 landed rather than pending. Phase 181 closed under v1.36 (`.planning/milestones/v1.36-phases/181-.../181-CLOSURE.md`). |

---

## Open Questions

1. **Where should the `region_end ? region_end : mem_size` fallback be resolved?**
   - Known: it must be resolved *somewhere*, it must not appear inline at `eprom.cpp:397` (G-1b), and
     resolving it inside `eprom.cpp` adds a ternary site to the branch-inventory golden (G-2 ternary trap).
   - Unclear: whether resolving it once in `eprom_generic_init` / write-init entry (one site, one new
     golden row) beats resolving it at each of the three use sites in `memory.cpp` and
     `eprom_operations.cpp` (three sites, zero new golden rows, but three places to get wrong).
   - Recommendation: **resolve once, in `memory.cpp`'s region wrapper and once at the top of
     `_process_incoming_data`** — zero new `eprom.cpp` branch sites, and the `op_end` local at
     `eprom.cpp:397` is a plain read of an already-resolved handle member. State the choice in the plan.

2. **Does the `MSG_DATA_PROGRESS` "one payload meaning" contract survive D-06, and how is that argued?**
   - Known: the gate at `test_progress_emission_is_leonardo_only.py:606-613` encodes the contract as
     a literal string and an explicit design argument.
   - Unclear: whether the operator wants the contract restated ("the denominator is the operation's
     end") or the gate relaxed.
   - Recommendation: restate the contract in the gate's own docstring in the same commit that changes
     the assertion. A silent string swap would erase the reasoning the gate exists to carry.

3. **Should `_META_DOC_REL` in `test_flash_path_record_sync.py` be repaired as part of this phase?**
   - Known: it is broken (G-4), it is invisible to CI, and it is unrelated to BLANK-01..03.
   - Recommendation: **no.** Use the `FIRESTARTER_META_ROOT` workaround and file a todo. Repairing it
     inside a bench-gated dual-repo lockstep phase adds an unrelated firmware-repo commit to a
     lockstep whose commit pairing already matters.

4. **How is the D-16.1 RED-first state captured, given the harness defect?**
   - Known: D-16.1 requires the native leg to be *seen* RED before the fix. But the test cannot be
     written at all until the address-keyed mock exists (§"Native harness"), and the mock is new code.
   - Recommendation: sequence it as (i) mock extension + a positive control proving the mock can make
     a chosen address non-blank; (ii) the D-16.1 test, run and **seen** RED with the transcript
     captured; (iii) the firmware fix. Three tasks, not one.

---

## Sources

### Primary (HIGH confidence) — files read and commands run in this session
- `firestarter_fw/src/proms/memory.cpp` (`:78`, `:319`, `:425-513`)
- `firestarter_fw/src/proms/eprom.cpp` (`:41-105`, `:128-158`, `:380-400`)
- `firestarter_fw/src/eprom_operations.cpp` (`:16-145`)
- `firestarter_fw/src/operation_utils.cpp` (`:112-245`)
- `firestarter_fw/src/json_parser.c` (`:40-320`)
- `firestarter_fw/src/firestarter.cpp` (`:30-80`)
- `firestarter_fw/include/firestarter.h` (`:136-138`, `:160-206`), `include/memory_utils.h` (`:10-30`), `include/json_parser.h` (`:17`)
- `firestarter_fw/tests/test_protocol_branch_inventory.py` (all 571 lines), `tests/golden/protocol_branch_inventory.json`
- `firestarter_fw/tests/test_progress_emission_is_leonardo_only.py` (`:1-340`, `:575-640`)
- `firestarter_fw/tests/test_write_path_source_contract_v131.py` (`:1-220` + symbol map)
- `firestarter_fw/tests/meta_presence.py` (`:38-110`), `tests/test_flash_path_record_sync.py` (`:77`, `:375-430`)
- `firestarter_fw/test/native/avr/test_val_eprom/{host_stubs.cpp,test_val_eprom.cpp}`
- `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (`:190-235`, `:780-825`)
- `firestarter_fw/platformio.ini` (`:60-170`), `.github/workflows/build.yml` (`:16-201`)
- `firestarter_app/firestarter/eprom_operations.py` (`:440-560`, `:690-780`, `:1968-2140`)
- `firestarter_app/firestarter/{database.py,page_size_gate.py,serial_comm.py,constants.py,cli_handlers.py,chip_test.py,diagnostic_report.py}`
- `firestarter_app/tests/{fake_chip.py,test_uv_mask.py,test_wire_dict_equivalence.py,test_eprom_operations.py}`
- `firestarter_app/.github/workflows/ci.yml`, `pyproject.toml` (`:95-102`)
- `/workspaces/.planning/todos/pending/2026-08-30-write-init-blank-check-is-whole-device.md`,
  `/workspaces/.planning/todos/pending/2026-09-08-uv-write-shortcut-disclosure-key.md`
- `/workspaces/CLAUDE.md`, `/workspaces/.planning/config.json`, `/workspaces/.planning/REQUIREMENTS.md`
- Commands run: `pio test -e native_nodevtools`, `pio run`, `pytest` (4 invocations across both
  repos), `git hash-object`, `git log -1 --format=%B 088d2b7`, `git rev-parse --abbrev-ref HEAD` ×3,
  the token/length measurement script against the real DB, `grep --version`, `ls`/`find` for the
  deleted-test census.

### Secondary (MEDIUM confidence)
- `firestarter_app` commit message `088d2b7` — an operator ruling recorded in git, quoted verbatim,
  but a policy statement rather than an executable gate. Treated as binding.

### Tertiary (LOW confidence)
- None. No web search was performed and no external documentation was consulted; every question in
  the brief was answerable from the two repositories and the running environment.

### Not consulted
- `.planning/graphs/graph.json` — `gsd-tools graphify status` reports `stale: true`, 38 h old,
  **144 commits behind** (`built_at_commit: d11d37e`, `current_commit: db9231c`). Direct source reads
  were used throughout in preference; no finding here depends on the graph.

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** Both repositories' dependency sets are
unchanged: the firmware change is C/C++ against the existing `ArduinoFake@^0.4.0` test dependency
(`platformio.ini:97-98`, already present), and the host change adds six lines of standard-library
Python (`os.path.getsize`, already imported in `eprom_operations.py`). No `npm`, `pip` or `cargo`
install appears in any recommendation above.

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| Host-side cross-repo source-scanning parity gates (`json_key_parity`, `revision_constants_parity`, `fw_presence`) | Literal-pinned host constants + firmware-side source-contract gates | 2026-09-14, commit `088d2b7` (operator ruling) | **D-16.3 must follow the new shape.** See G-6. |
| `scripts/check_size_baseline.py` + `scripts/baseline/size_baseline.json` in CI | No automated size gate; `pio run` output read by hand | before this milestone | Flash headroom must be measured deliberately (leonardo: 4856 B against the real 28672 ceiling). |
| Two write-init blank checks that *scope* the check | `eeprom_28c.cpp:379-385` and `flash_5v_page.cpp:74-78` **deleted** theirs outright | v1.3x | The precedent exists and is documented in CONTEXT.md; it is the wrong answer for UV parts and is already in Deferred Ideas. Do not re-propose it. |
| `mem_util_blank_check` allocating a 4-byte `malloc` for the saved address | a file-scope `static uint32_t blank_check_saved_address` | before v1.31 | The region form must not reintroduce a heap allocation; `memory.cpp:425-436` carries the written rationale. |
| `handle->page_size` absent ⇒ **refuse** (Phase 194) | This field absent (`0`) ⇒ **whole device** | this phase, deliberately | D-04's inversion. The `json_parse` reset is what makes both directions safe. |

**Deprecated / stale references encountered, all worth correcting opportunistically:**
- `firestarter_fw/include/firestarter.h:181-184` cites `firestarter_app/tests/test_revision_constants_parity.py` — **that file no longer exists.**
- `firestarter_fw/tests/meta_presence.py:67-69` cites `firestarter_app/tests/fw_presence.py` — **that file no longer exists.**
- `firestarter_fw/tests/test_protocol_branch_inventory.py`'s module docstring says "exactly three tier-`protocol` sites, at lines 71, 145 and 218" and ">= 24 sites"; the live code asserts `== [70]` and `>= 21`. **Docstring stale, code correct.**
- `firestarter_fw/tests/golden/protocol_branch_inventory.json` `counts` reads 21/1/20 while `sites` has 22 entries. **Unasserted drift.**

---

## Metadata

**Confidence breakdown:**
- Host seam / ordering question: **HIGH** — every line quoted from the live file; the conclusion
  (no restructure needed) follows from `input_file_path` being a parameter, which is not a judgement call.
- Firmware seam / control flow: **HIGH** — full function quoted with line numbers from `grep -n`.
- The multi-call stability constraint (C-3): **HIGH** — derived from `operation_utils.cpp:203-208`
  and `memory.cpp:451-461`, both quoted; the failure mode is arithmetic, not empirical.
- Gate census: **HIGH for the six named** (each read, each with a quoted assertion, three run);
  **MEDIUM for completeness** — I scanned both `tests/` trees for references to the touched files
  and ran both full suites, but a gate that scans a file this phase does not obviously touch could
  still surprise. The two full-suite baselines are the mitigation: re-run them after every task.
- Native harness defect: **HIGH** — the aliasing is visible in the quoted `rurp_read_data_buffer`
  (`& (VAL_EPROM_READBACK_SLOTS - 1)` with 16 slots) and conceded by the stub's own comment.
- Bench parts and D-12/D-14: **not re-verified** — out of this researcher's reach; CONTEXT.md's
  measurements stand.

**Research date:** 2026-09-19
**Valid until:** 2026-10-19 for the firmware/host source claims (stable code, milestone branch);
**7 days** for the gate-baseline numbers (269/32, 2100, 232) — any commit on either sub-repo moves them.
