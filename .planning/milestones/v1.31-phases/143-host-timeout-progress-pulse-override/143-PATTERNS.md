# Phase 143: Host Timeout, Progress & Pulse Override - Pattern Map

**Mapped:** 2026-08-12
**Files analyzed:** 20 code/test/fixture files (9 in `firestarter/`, 11 in `firestarter_app/`) + 1 firmware doc
**Analogs found:** 20 / 20 files (1 file — `cli_handlers.py` — has a partial: its option-decorator
shape has an analog, its `IntRange` bounds mechanism has **none** in either repo)

**DUAL-REPO (D-01).** Every analog below lives inside a submodule working tree, never in meta.
Paths are given repo-relative with the repo named. Meta tracks only `.planning/`, so the phase
record artifacts (`143-*-RECORD.md`) are the only meta-repo files and need no code analog.

> **Every line number below was re-located in the working tree this session** against
> `firestarter` @ `gsd/v1.31-27c-programming-algorithm-fidelity` and `firestarter_app` @ the same
> branch. Where RESEARCH.md or CONTEXT.md cite a number that has moved or was wrong, the corrected
> number appears here and the discrepancy is listed in **§Corrections to Upstream Citations** — read
> that section before quoting any upstream line number into a plan.

---

## File Classification

### Firmware — `/workspaces/firestarter/`

| New/Modified File | Role | Data Flow | Closest Analog | Match |
|-------------------|------|-----------|----------------|-------|
| `include/eprom_budget.h` (NEW) | header / pure API decl | transform | `include/eprom_params.h` | exact |
| `src/proms/eprom_budget.cpp` (NEW) | utility (pure arithmetic over a PROGMEM table) | transform | `src/proms/eprom_params.cpp` | exact |
| `src/firestarter.cpp` (MOD — CAP-02 port + CAP-03 append) | controller / dispatcher (ack emitter) | request-response | its own `:157` ack site + the CAP-02 emit in commit `13eb350` on `origin/beta` | exact (a port of shipped code) |
| `src/proms/eprom.cpp` (MOD — time-gated `0xE0` emission, ONE commit per D-23) | service (device-driver loop) | streaming / event-driven | `src/proms/memory.cpp:541-560` (`mem_util_blank_check`'s `0xE0` emitter) | exact |
| `src/eprom_operations.cpp` (MOD — stale comment at `:93`) | comment only | — | n/a | n/a |
| `test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` (MOD) | test (native Unity) | event capture + transform | `test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp:141-168` (advancing `millis()`) + this suite's own `host_stubs.cpp:230-281` | exact |
| `tests/test_progress_emission_is_leonardo_only.py` (NEW) | test (source-contract gate) | file-I/O (source scan) | `tests/test_hv_routing_source_contract_v142.py` | exact |
| `tests/golden/protocol_branch_inventory.json` (MOD — re-derived) | fixture / golden | config | itself (`meta.how_to_update` is binding) | exact |
| `CLAUDE.md` (MOD — D-06's two-dimension non-claim on the 27C rows) | documentation | — | its own §"Algorithm Handlers" 0x07/0x08/0x0B rows | exact |

### Host — `/workspaces/firestarter_app/`

| New/Modified File | Role | Data Flow | Closest Analog | Match |
|-------------------|------|-----------|----------------|-------|
| `firestarter/serial_comm.py` (MOD — CAP-03 arm, new attribute, clamp const) | transport / service | request-response (frame decode) | its own `_decode_id_frame` CAP-01 arm `:356-363` + CAP-02 arm `:364-376`; class-attr block `:104-113` | exact |
| `firestarter/eprom_operations.py` (MOD — timeout kwarg, DATA branch, 2 helpers, `pulse_us`) | service / state machine | streaming + request-response | 5 in-file analogs: `:538-593`, `:480-488`, `:106-170`, `:766-773`, `:300-313` | exact |
| `firestarter/cli_handlers.py` (MOD — `--pulse-us` + D-17 report line) | controller (CLI) | request-response | `write`'s own option stack `:549-589` + D-04 report line `:666-675`; `--read-strobe` `:1476-1482` for the µs-option shape | **partial** — `IntRange` has no in-tree precedent |
| `firestarter/constants.py` (OPTIONAL MOD — `JSON_KEY_PULSE_DELAY`) | config | — | `:139-149` `JSON_KEY_*` block | exact |
| `tests/conftest.py` (MOD — `make_comm` gains the attribute) | test fixture | — | `:216-228` | exact |
| `tests/test_hw_revision_gate.py` (MOD — extend `_cap02_params`) | test | byte layout | `:162-219` | exact |
| `tests/test_write_response_budget.py` (NEW) | test (call-argument oracle) | request-response | `tests/test_eprom_operations.py:1207-1259` + `tests/test_submit.py`'s `call_args` idiom | exact |
| `tests/test_write_progress.py` (NEW) | test | streaming render | `tests/test_eprom_operations.py:98` + `:1207-1259` | role-match |
| `tests/test_budget_failure_render.py` (NEW) | test (pure-function hint) | transform | `tests/test_boot_block_hint.py:42-104` | exact |
| `tests/test_pulse_us_override.py` (NEW) | test (CliRunner + wire capture) | request-response | `tests/test_write_skip_sdp_unlock.py:132-195` | exact |

---

## Pattern Assignments

### `firestarter/include/eprom_budget.h` (NEW — header, transform)

**Analog:** `firestarter/include/eprom_params.h`

**Include discipline + the PROGMEM-read contract** (`include/eprom_params.h:12-36, 69-80`):

```c
/* (a) No Arduino framework header is included here, or by anything this
 *     file includes (see 140-RESEARCH.md Pitfall 1): a translation unit
 *     that pairs that header with the avr/pgmspace.h PROGMEM shim emits 14
 *     macro-redefinition warnings, and the native build's warning
 *     watermark sits at exactly 1166 with zero headroom -- so this
 *     dependency stays out end to end. */
#include <stdint.h>
#include "rurp_platform_compat.h" /* PROGMEM + pgm_read_* on AVR and host alike */
...
/*
 * Linear-scans the protocol_id-keyed table and returns a POINTER INTO
 * PROGMEM -- every field must be read back with pgm_read_byte /
 * pgm_read_dword, never dereferenced directly (a direct read compiles and
 * silently returns RAM garbage on AVR). ...
 */
const eprom_params_t* eprom_params_for(uint32_t protocol);
```

**Copy:** the `#include <stdint.h>` + `rurp_platform_compat.h` pair (NOT `<avr/pgmspace.h>`, NOT
`Arduino.h`), the `#ifndef __X_H__` guard shape, the `extern "C" {` wrapper, and the practice of
stating the PROGMEM-read obligation in the declaring header's own comment.

**Do NOT copy:** the `static_assert(sizeof(...) == 12)` — `eprom_budget.h` declares no struct.

---

### `firestarter/src/proms/eprom_budget.cpp` (NEW — utility, transform)

**Analog:** `firestarter/src/proms/eprom_params.cpp`

**Include discipline** (`src/proms/eprom_params.cpp:11-15, 23`) — this is the *only* other
`src/proms/` TU besides `not_implemented.cpp` that omits the Arduino header, and it says so:

```c
/*
 * No Arduino framework header is included here (140-RESEARCH.md Pitfall 1):
 * src/proms/not_implemented.cpp is the only other translation unit under
 * src/proms/ that omits it, and this file follows that include discipline
 * verbatim so it adds zero macro-redefinition warnings on the native build.
 */
#include "eprom_params.h"
```

**PROGMEM read pattern to copy** (`src/proms/eprom.cpp:310-314`) — read every column into a local
first, one `pgm_read_*` per field, never a struct dereference:

```c
uint32_t overprogram_cap_us = pgm_read_dword(&row->overprogram_cap_us);
uint32_t energy_cap_us      = pgm_read_dword(&row->energy_cap_us);
uint8_t  max_pulses         = pgm_read_byte(&row->max_pulses);
uint8_t  overprogram_factor = pgm_read_byte(&row->overprogram_factor);
uint8_t  verify_mode        = pgm_read_byte(&row->verify_mode);
```

**The UNCAPPED guard to mirror** (`src/proms/eprom.cpp:354-360`) — D-11's trap, guarded exactly this
way at the shipped site:

```c
// energy_cap_us == 0 means UNCAPPED (eprom_params.h) -- without
// this guard, 0x07/0x08 (both ship energy_cap_us == 0) would
// abort after their very first pulse.
if (energy_cap_us && accumulated >= energy_cap_us) {
    eprom_internal_report_budget_failure(handle, addr, pulses, MSG_ERR_ENERGY_CAP);
    return;
}
```

**The pulse-count arithmetic the budget must mirror** (`src/proms/eprom.cpp:338-361`) — note
`accumulated += org_delay` happens **before** the `>= energy_cap_us` test, which is exactly why
BF-3's `ceil(C/P)` is load-bearing and `min(M*P, C)` is wrong:

```c
uint8_t pulses = 0;
uint32_t accumulated = 0;
for (;;) {
    handle->firestarter_set_data(handle, addr, expected);
    pulses++;
    accumulated += org_delay;  // D-02: pulse widths only
    if (handle->firestarter_get_data(handle, addr) == expected) {
        break;  // converged
    }
    if (pulses >= max_pulses) { ... MSG_ERR_MAX_PULSES ... return; }
    if (energy_cap_us && accumulated >= energy_cap_us) { ... MSG_ERR_ENERGY_CAP ... return; }
}
```

**The overprogram function to CALL, not restate** (`src/proms/eprom.cpp:189-195`) — signature is
`(pulse_count, pulse_us, factor, cap_us)` and the `3` in `eprom_params.h`'s comment is **not** in it:

```c
uint32_t eprom_overprogram_us(uint8_t pulse_count, uint32_t pulse_us, uint8_t factor, uint32_t cap_us) {
    if (factor == 0) {
        return 0;
    }
    uint32_t product = (uint32_t)factor * pulse_count * pulse_us;
    return product > cap_us ? cap_us : product;
}
```

**Shipped row values the budget computes from** (`src/proms/eprom_params.cpp:45-49`) — read-only this
phase. Column order is **largest-first**, `overprogram_cap_us` FIRST:

```c
static const eprom_params_t EPROM_PARAMS[] PROGMEM = {
    /* 0x07 PROTO_EPROM_28PIN */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x08 PROTO_EPROM_32PIN */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x0B PROTO_EPROM_24PIN */ { 75000UL, 50000UL, 255, 0, VERIFY_PER_PULSE,            VPP_PATH_DIRECT_VPE    },
};
```

**Why this file and not `eprom.cpp`:** `tests/golden/protocol_branch_inventory.json`'s
`meta.blob_shas` pins `src/proms/eprom.cpp` and `src/proms/eprom_params.cpp` only. A new TU under
`src/proms/` is unpinned, is still natively compiled (`build_src_filter` is the directory glob
`+<proms/>`), and keeps the arithmetic out of D-23's single-commit constraint.

---

### `firestarter/src/firestarter.cpp` (MOD — controller, request-response)

**Analog A (the site being replaced):** `src/firestarter.cpp:151-158`

```c
    LOG_INFO_ID_ASTR(MSG_INFO_FW, FW_VERSION);
#ifdef HARDWARE_REVISION
    LOG_INFO_ID_U8(MSG_INFO_PHYSICAL_HW, (uint8_t)rurp_get_physical_hardware_revision());
    LOG_INFO_ID_U8(MSG_INFO_HW, (uint8_t)rurp_get_hardware_revision());
#endif
    LOG_INFO_ID_U8(MSG_INFO_CMD, (uint8_t)handle->cmd);
    LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE);   // <-- CAP-01 ONLY. BF-1 CONFIRMED.
    op_reset_timeout();
```

**BF-1 is verified true at this line:** the branch emits a bare 2-byte ack. There is no CAP-02 tail
to append CAP-03 after. Port CAP-02 first, in the same pack block.

**Analog B (the CAP-02 emit to port):** `git -C /workspaces/firestarter show 13eb350 -- src/firestarter.cpp`
(present only on `origin/beta`; `git branch -a --contains 13eb350` names no local branch). Read it
directly rather than re-inventing the pack; RESEARCH §Code Example 2 reproduces its shape.

**Macro to switch to** (`include/logging_id.h:125-128`):

```c
#define LOG_OK_ID_U16(id, p1)          LOG_ID_U16((id), (p1))
#define LOG_OK_ID_BYTES(id, b, n)      LOG_ID_BYTES((id), (b), (n))
```

**Ordering fact — RESEARCH Open Question 1 / A6 is RESOLVED YES.** `handle->pulse_delay` has already
had `configure_eprom`'s `pulse_delay == 0` fallback applied when the ack is packed, so there is **no**
spurious-2 s-budget path. Chain, all verified this session:

- `src/firestarter.cpp:86-95` — `parse_json()` calls `op_execute_function(configure_memory, handle)`
  inside `if (is_memory_cmd(handle->cmd))`
- `src/firestarter.cpp:130` — `init_programmer_framed()` calls `parse_json(handle)`
- `src/firestarter.cpp:157` — the ack is emitted 27 lines later
- `src/proms/eprom.cpp:68-75` — the fallback switch that `configure_memory` → `configure_eprom` runs

```c
    // Set default pulse_delay from protocol when Python doesn't supply one
    if (handle->pulse_delay == 0) {
        switch (handle->protocol) {
            case 0x08: handle->pulse_delay = 100;  break;  // EPROM_QUICK: 100µs
            case 0x0B: handle->pulse_delay = 500;  break;  // EPROM_LEGACY: 500µs
            default:   handle->pulse_delay = 1000; break;  // EPROM_STD: 1ms
        }
    }
```

**Residual (state it, do not fix it):** `configure_memory` runs only for `is_memory_cmd(handle->cmd)`.
On a non-memory command `pulse_delay` stays 0 — but `eprom_params_for()` returns NULL for a non-EPROM
protocol, the budget function returns 0, and the host's `[1, MAX]` clamp then leaves the attribute
`None` so D-10's fallback applies. The A5 "advertise on every command" decision is safe by that route.

---

### `firestarter/src/proms/eprom.cpp` (MOD — service, streaming; ONE plan / ONE commit per D-23)

**Analog:** `firestarter/src/proms/memory.cpp:541-560` — the **only** existing `0xE0` emitter.

```c
    handle->address += BLANK_CHECK_CHUNK_SIZE;
...
    // Send progress back to the client. For the standalone blank-check command the
    // emit is deferred to _single_step_operation_callback (communication mode): this
    // function runs in programmer mode where the Uno's com_mode-gated rurp_log_id
    // drops frames. Other callers (write-init / erase-end) keep the direct emit.
    // (#transport-protocol-verify)
    if (handle->cmd != CMD_BLANK_CHECK) {
        LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size);
    }
```

**Copy:** the payload contract verbatim — `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, <absolute address>,
handle->mem_size)`. D-04 keeps **one** meaning for `0xE0`; the host's write branch is what differs.

**Copy the WARNING too, not just the call.** This site already carries BF-2's exact trap in prose
(`memory.cpp:522-527` states it a second time at the `MSG_ERR_NOT_BLANK` emit). The existing emitter's
mitigation is a *runtime* `handle->cmd` gate; BF-2's mitigation is a *compile-time* `#ifndef
SERIAL_ON_IO` guard. Both are the same defect class — say so in the new comment and cite both sites.

**Guard-scoping facts verified this session:**

| Fact | Location |
|------|----------|
| `-D SERIAL_ON_IO` appears on exactly two envs (`uno`, `uno328pb`) | `platformio.ini:38`, `:55` |
| Both mode functions are typed no-ops without it | `include/rurp_shield.h:64` (`#ifdef SERIAL_ON_IO`) |
| `#define DEFERRED_LOG_MAX 4` / `#define DEFERRED_PARAM_MAX 8` | `src/boards/uno_rurp_shield.cpp:34-35` |
| Silent-drop arm: `// else: buffer full (should not happen in production...)` | `src/boards/uno_rurp_shield.cpp:124` |
| `com_mode = false` on programmer mode / `= true` on communication mode | `src/boards/uno_rurp_shield.cpp:97`, `:89` |

**Insertion-point pattern** (`src/proms/eprom.cpp:321-333`) — the outer per-byte loop and the two
LOOP-06 skips. Placing the emit at the top of the loop body makes cadence independent of skips:

```c
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint8_t expected = (uint8_t)handle->data_buffer[i];
        uint32_t addr = handle->address + i;

        if (expected == 0xFF) {
            continue;
        }
        if (handle->firestarter_get_data(handle, addr) == expected) {
            continue;
        }
```

**Single-exit wrapper to leave alone** (`src/proms/eprom.cpp:424-429`) — the emission goes inside the
*body*, which the wrapper already covers. Do not add an exit:

```c
void eprom_write_execute(firestarter_handle_t* handle) {
    eprom_internal_write_execute_body(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        handle->firestarter_set_control_register(handle, EPROM_HV_ALL_OFF_MASK, 0);
    }
}
```

**The one surviving tier-1 site not to disturb** (`src/proms/eprom.cpp:70`, the `switch
(handle->protocol)` above): the golden pins `protocol_lines == [70]`. A time-keyed `millis()`
predicate contains neither `handle->` nor a named helper, so `_is_relevant`
(`tests/test_protocol_branch_inventory.py:268`) will not record it as a site — but every site *below*
the insertion shifts line, so the golden must still be re-derived.

---

### `firestarter/tests/golden/protocol_branch_inventory.json` (MOD — fixture, config)

**Analog:** itself. `meta.how_to_update` is binding and was read in full this session:

> "If eprom.cpp or eprom_params.cpp legitimately change in a way that moves this inventory,
> re-derive it by running an independent parse against the new file (never hand-edit a line number, a
> keyed_on set, a class, or a count merely to make a surprise disappear), and state in the commit
> message which site changed, or was added or removed, and why. Diffing the extractor's live output
> against this JSON is the only sanctioned way to update it."

**Current pinned state** (arrival values the plan must move from, not to):

| Key | Value |
|-----|-------|
| `meta.blob_shas["src/proms/eprom.cpp"]` | `17f5f4185b8a11590e2343d6d8d289cafcb19a45` |
| `meta.blob_shas["src/proms/eprom_params.cpp"]` | `5dffe841aeb7013f9f53e9991a6248b203ae22da` |
| `meta.recorded_at_head` | `4a890b93c4844a3b980465aa1feb5488bcb7feca` |
| `counts` | `{"total_sites": 26, "protocol_keyed_sites": 1, "other_sites": 25}` |

**`meta.recorded_by` precedent to copy** — Phase 142 documented the deliberate one-commit offset
(`recorded_at_head` names the new commit's PARENT because golden + source land together). Reuse that
wording shape rather than inventing an explanation.

**Gate legs that move with it** (`tests/test_protocol_branch_inventory.py`): `:398`
`test_blob_shas_match_the_recorded_inventory`, `:417` `test_branch_sites_match_the_recorded_inventory`,
`:443` `test_exactly_one_protocol_keyed_site_at_the_pinned_line` with the `protocol_lines == [70]`
literal at `:452-453`.

---

### `firestarter/tests/test_progress_emission_is_leonardo_only.py` (NEW — test, source-contract)

**Analog:** `firestarter/tests/test_hv_routing_source_contract_v142.py` (807 lines; Phase 142's
`command_done()` gate). This is the *exact* class of gate BF-2 requires, and the analog explains in its
own docstring why a behavioural oracle is impossible for a `#ifdef`-scoped guard.

**Copy the module skeleton** (`:188-212`) — stdlib only, `_REPO_ROOT` recomputed from `_HERE.parent`,
import-time env seams:

```python
import os
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_DISPATCH_REL = "src/firestarter.cpp"
_EPROM_REL = "src/proms/eprom.cpp"

# Environment seams -- bind at IMPORT time. See the module docstring's
# "Environment seams" section above.
_SCAN_EPROM = Path(
    os.environ.get("FIRESTARTER_HV_SCAN_EPROM_SOURCE", str(_REPO_ROOT / _EPROM_REL))
)
```

**Copy the comment stripper verbatim** (`:214-247`) — it preserves line numbers by replacing each
stripped span with whitespace *of the same shape*, and its own docstring records that it was itself
copied from `test_write_path_source_contract_v131.py:203-235`:

```python
def _strip_comments(text):
    """Strip `//` line comments and `/* ... */` block comments, replacing
    each stripped span with whitespace of the SAME SHAPE (a newline stays a
    newline, everything else becomes a single space) so every line number
    in the result matches the original file exactly -- copied verbatim
    from tests/test_write_path_source_contract_v131.py:203-235 ..."""
```

**Copy the brace-matching body extractor** (`:369-402`) so a match *elsewhere in the file* cannot
satisfy a leg. For this phase the body to extract is
`static void eprom_internal_write_execute_body(firestarter_handle_t* handle) {` — the regex already
exists at `:326-328`:

```python
_WRITE_EXECUTE_BODY_DEF_RE = re.compile(
    r"\bstatic\s+void\s+eprom_internal_write_execute_body\s*\(\s*firestarter_handle_t\s*\*\s*handle\s*\)\s*\{"
)
```

**Copy the three self-protection legs** (`:716-806`) — these are what make D-25 achievable:

- `test_scan_targets_are_non_vacuous` (`:716`) — recomputes defaults from `_REPO_ROOT` **without
  reading `os.environ`**, asserts each target exists, is non-empty, `is_relative_to(_REPO_ROOT)`, and
  has non-empty stripped text. Its docstring names the `check_permitted_claims.py`
  `_HERE`-resolves-wrong landmine this closes by construction.
- `test_this_module_cannot_be_silently_skipped` (`:764`) — concatenation-built needles
  `"pytest" + ".skip"`, `"mark" + ".skipif"`, `"importor" + "skip"`.
- `test_own_needles_do_not_appear_verbatim_in_this_module` (`:792`) — proves the concatenation
  discipline stays machine-checked.

**Copy the honest-CI framing** (`:169-175`) verbatim in shape: `pytest tests/ -v` appears in
`.github/workflows/build.yml:161` and `beta-build.yml:134`, so the module runs in CI **only once the
branch reaches `main`/`beta`** — never claim milestone-branch CI coverage.

**Needle discipline for this phase's legs:** the guard token `SERIAL_ON_IO` will appear in this
module's own source (it is part of the assertion's English name), so build the *forbidden* needles by
concatenation and name each test after what it forbids, per the analog's Naming note (`:155-167`).

---

### `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` (MOD — test)

**Analog A (the advancing `millis()` mock):** `test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp:141-168`

```c
/* Monotonically-increasing millis counter used by the millis() mock. ...
 * Incrementing by 100 each call ensures that at most ~20 calls exhaust the
 * 2000 ms window, preventing an infinite spin when the mock queue is empty. */
static unsigned long millis_counter;

void setUp(void) {
    ArduinoFakeReset();
    ...
    millis_counter = 0;
    /* millis() — monotonically increasing ... Each invocation advances by 100 ms. */
    When(Method(ArduinoFake(Function), millis))
        .AlwaysDo([&]() -> unsigned long {
            millis_counter += 100;
            return millis_counter;
        });
}
```

**Analog B (the mock to REPLACE):** `test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:133`

```c
    /* Unused by any case in this plan, but ArduinoFake SIGABRTs on any
     * unmocked call -- cheap insurance matching house convention. */
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);
```

A time-gated emission with `millis()` frozen at 0 **never fires** — a cadence case would pass
vacuously with zero frames. Replace the `millis` line with Analog A's advancing counter, keep
`micros`, and state in the file *why* the mock changed. The existing `setUp` also resets
`clear_strobes(); clear_timings(); clear_logged_ids(); loop_readback_reset();
reset_register_cache(0x00, 0x00, 0x00);` (`:141-145`) — leave that block intact.

**Analog C (the frame-capture API — CORRECTED LOCATION):**
`test/native/avr/test_loop_eprom_v131/host_stubs.cpp:230-281`. RESEARCH.md cites
`test/native/avr/_shared/host_stubs_common.inc:268`; that file contains **no** `rurp_log_id` at all
(verified by grep). The strong override and its accessors live in this suite's own stub TU:

```c
#define LOOP_LOGGED_ID_MAX_ENTRIES 32
#define LOOP_LOGGED_ID_MAX_PARAMS 8
...
extern "C" void    clear_logged_ids(void);
extern "C" int     logged_id_count(void);
extern "C" uint8_t logged_id_at(int i);
extern "C" uint8_t logged_id_param_count(int i);
extern "C" uint8_t logged_id_param(int i, int j);
extern "C" int     logged_ids_overflowed(void);

extern "C" void rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count) {
    if (s_logged_id_count >= LOOP_LOGGED_ID_MAX_ENTRIES) {
        s_logged_id_overflow = 1;  /* tail dropped; prefix stays valid */
        return;
    }
    ...
}
```

The `extern "C"` declarations are already mirrored into the test TU at
`test_loop_eprom_v131.cpp:100-105`, so a new case needs no new plumbing.

**Two capture facts that shape the assertions** (`host_stubs.cpp:222-228`): this override captures
**every** logged frame from any TU in the `build_src_filter`, *including* `LOG_DEBUG_ID_SUB`'s
`MSG_DEBUG` entries — so a cadence case must **filter by id** (`logged_id_at(i) == MSG_DATA_PROGRESS`),
never assume the array holds only its own frames. There is **no** `com_mode` gate in this stub, so the
native oracle is structurally blind to BF-2; that is why the guard needs the source-contract gate above.

**Env facts** (`platformio.ini`, `[env:native_loop_v131]`): this env already runs two suites
(`test_loop_eprom_v131`, `test_vpp_eprom_v131`), is in **no** `default_envs`, runs in **no** CI leg,
and must never be passed to `check_size_baseline.py` (uncaught `KeyError`) or
`check_build_warnings.py`. Extending an existing suite needs no `test_filter` / `-I` change.

---

### `firestarter_app/firestarter/serial_comm.py` (MOD — transport, request-response)

**Analog:** its own `_decode_id_frame` override, `:319-377`. This is the sanctioned seam; the
ring-fence header begins at `:379`.

**The two prior length-discriminated arms to extend** (`:349-377`):

```python
            if msg_id == MSG_OK_READY:
                params_bytes = body[1:-1]  # strip id byte and trailing CRC
                # CAP-01 buffer size occupies the first 2 bytes in BOTH the
                # legacy 2-byte ack and the CAP-02 extended ack, so the length
                # test is >= 2 rather than == 2. ...
                if len(params_bytes) >= 2:
                    value = struct.unpack(">H", params_bytes[:2])[0]
                    # Plausibility clamp: reject values outside [1, 4096].
                    # ... Values outside this range leave
                    # firmware_max_chunk unset so the 512 floor applies (T-55-06).
                    if 1 <= value <= 4096:
                        self.firmware_max_chunk = value
                # CAP-02 tail: [hw_revision u8][ver_len u8][ver bytes]. Absent
                # on pre-CAP-02 firmware, which leaves both attributes None ...
                if len(params_bytes) >= 4:
                    self.hw_revision = params_bytes[2]
                    ver_end = 4 + params_bytes[3]
                    if ver_end <= len(params_bytes):
                        self.firmware_identity = params_bytes[4:ver_end].decode(
                            "ascii", errors="replace"
                        )
        return result
```

**Copy exactly four things:** (1) the `>=` length gate before any indexing; (2) `struct.unpack(">H",
…)` — same call form as CAP-01, no second pattern; (3) the plausibility clamp with its "outside this
range leaves the attribute unset" comment; (4) reading at the **computed `ver_end`**, nested inside
the CAP-02 arm's own `if ver_end <= len(params_bytes)` so a truncated tail cannot yield a partial value.

**Class-level attribute declaration is mandatory, not stylistic** (`:104-113`) — the comment states the
failure mode:

```python
    # CAP-02 identity fields, declared at CLASS level on purpose. __init__ also
    # assigns them, but plenty of call sites never run __init__ — conftest's
    # make_comm builds instances via __new__, and several suites patch __init__
    # to a no-op lambda to avoid opening a real port. _probe_port reads
    # firmware_identity unconditionally, so an instance-only attribute turns
    # every one of those into an AttributeError swallowed by the broad
    # `except Exception` in _probe_port, which degrades to "no programmer
    # found". Class defaults of None keep the gates fail-closed instead.
    firmware_identity: Optional[str] = None
    hw_revision: Optional[int] = None
```

**`__init__` companion block to mirror** (`:135-153`) — same annotate-and-comment-the-degradation shape.

**Constant placement** (`:65-67`) — a new `WRITE_BUDGET_MAX_S` belongs in this module-level block
beside `DEFAULT_RESPONSE_TIMEOUT`, which D-12 leaves untouched:

```python
DEFAULT_SERIAL_TIMEOUT = 1.0  # seconds for read operations
DEFAULT_RESPONSE_TIMEOUT = 10  # seconds for waiting for a specific response
CONNECTION_STABILIZE_DELAY = 2.0  # seconds after opening port
```

**`get_response(timeout)` is already a supported call form** (`:518` def, `:540` caller) — no new API:

```python
    def get_response(self, timeout: float = DEFAULT_RESPONSE_TIMEOUT) -> Response:
...
            response = self.get_response(timeout)   # expect_ack, :540
```

**Ring-fence boundary — read before editing anything below `:379`** (`:379-389`), and note the
**corrected** reset line: the reset that fires for a decoded **binary id frame** (which is what a
`0xE0` progress frame is) is at **`:502`**, not `:448`/`:513` as CONTEXT/RESEARCH state:

```python
                decoded = self._decode_id_frame(frame_len, body)
                if decoded is not None:
                    ...
                    self._log_rurp_feedback(response)
                    yield response
                    start_time = time.time()      # <-- :502, the id-frame reset
                continue
```

`:448` is the pre-preamble text flush; `:513` is the newline text path. Neither fires for a progress
frame. Quote `:502` when arguing that D-02's emission feeds the response window.

---

### `firestarter_app/firestarter/eprom_operations.py` (MOD — service, streaming + request-response)

This file receives five separate changes. Each has an in-file analog.

**(1) Write-path timeout kwarg — analog: `_main_phase_send_data`'s own signature and `get_response`
call** (`:538-544`, `:563-564`):

```python
    def _main_phase_send_data(
        self,
        progress: ClassProgressHandler,
        input_file_path: str,
        buffer_size: int,
        eprom_data_dict: Optional[dict] = None,
    ) -> None:
        """Main phase handler for writing or verifying data.

        ``eprom_data_dict`` is forwarded from the write/verify caller so that
        the boot-block-locked heuristic hint (FIX-01b, Phase 94) can be appended
        ... Passing None (the default) keeps behaviour identical to
        pre-FIX-01b for all other callers.
        """
...
            while True:
                response = self.comm.get_response()
```

The `eprom_data_dict: Optional[dict] = None` parameter is the **exact precedent** for a write-only
kwarg on a function `verify_eprom` also calls: `write_eprom` passes it (`:1609`), `verify_eprom` does
not (`:1696-1701`), and the docstring already states the "default keeps behaviour identical" contract.
Copy that shape for `response_timeout`.

**Kwarg forwarding is already verbatim** (`:442`): `final_msg = main_phase_handler(progress=progress,
**handler_kwargs)` — no `_run_state_machine` change is needed.

**(2) The DATA branch — analog: the raise it must precede** (`:565-576`):

```python
                response = self.comm.get_response()
                if response.type == "MAIN":
                    break  # Main phase is complete
                if response.type == "ERROR":
                    hint = _boot_block_hint_message(response, protocol, mem_size)
                    msg = response.message
                    if hint:
                        msg = msg + " -- " + hint
                    _raise_for_error_response(response, msg)
                if response.type != "OK":
                    raise EpromOperationError(
                        f"Programmer did not request data chunk, got {response.type}: {response.message}"  # noqa: E501
                    )
```

A mid-block DATA frame hits that `raise` today. The new arm goes **between** the ERROR branch and this
`if response.type != "OK"`.

**(3) `ack_data=False` — analog: `_execute_phase`'s INIT/END progress handling** (`:480-488`). This is
the `#write-empty-input-regression` fix, in prose, at the site that carries it:

```python
            # INIT/END phases: render DATA progress frames but do NOT ack them.
            # #write-empty-input-regression (Option C): a multi-step in-progress
            # INIT/END sub-step (e.g. write-init blank-check) emits one
            # MSG_DATA_PROGRESS per chunk but the firmware consumes a host ack
            # only on the first chunk. Acking every DATA frame here piled up N-1
            # spurious OK acks in the firmware RX buffer, desyncing the MAIN
            # data-pull handshake -> MSG_ERR_EMPTY_INPUT (0xA4). The firmware keeps
            # emitting progress (so the bar still moves); the host just skips the ack.
            self._handle_progress_response(response, progress, ack_data=False)
```

**Do NOT route the write branch through `_handle_progress_response`** (`:492-514`) — its DATA arm calls
`progress.set_progress(current, total)` at `:508`, which is exactly the rebuild path D-04 forbids:

```python
        if response.type == "DATA":
            try:
                if response.message and "/" in response.message:
                    current, total = map(int, response.message.split("/"))
                    if progress:
                        progress.set_progress(current, total)
                elif response.message:
                    progress.update(int(response.message))
            except (ValueError, TypeError):
                pass  # Not a parsable progress update
            if ack_data:
                self.comm.send_ack()
```

Copy its `try/except (ValueError, TypeError): pass` parse-tolerance and its `"/" in response.message`
guard into the new `_apply_write_progress`; do not copy the `set_progress` call or the ack.

**The rebuild hazard, confirmed real** (`ClassProgressHandler`, `:247-277`):

```python
    def start(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0
        if self.progress_callback:
            self.progress_callback(self.current_step, total_steps)
        else:
            if self.pbar:
                self.pbar.close()  # Close old one if any
            logging_redirect_tqdm()
            self.pbar = tqdm.tqdm(total=total_steps, bar_format=bar_format)
...
    def set_progress(self, current, total):
        if self.total_steps != total or (not self.pbar and not self.progress_callback):
            self.start(total)

        self.current_step = current
        if self.progress_callback:
            self.progress_callback(current, total)
        if self.pbar:
            self.pbar.n = current
            self.pbar.refresh()
```

The write bar is started with `file_size` at **`:561`** while `0xE0` carries `handle->mem_size` — a
short input file or `--address` write differs, so every frame would `close()` and re-create the bar.
The last three lines of `set_progress` (`:275-277`) are the exact operations `_apply_write_progress`
should perform directly, bypassing the `start(total)` arm.

**Bar-fight source** (`:591`): `progress.update(len(data_chunk))` on chunk handoff. Latch per RESEARCH
Pitfall 1; do not delete it (that regresses Uno-class boards to a dead bar).

**Offset source** (`:339-343`): `command_dict["address"]` is set **only** when an `--address` was
supplied, so `(eprom_data_dict or {}).get("address", 0)` is correct:

```python
        addr = 0
        if address:
            try:
                addr = parse_address(address) or 0
                command_dict["address"] = addr
```

**(4) The budget-failure hint — analog: `_boot_block_hint_message`** (`:106-170`, **ends at 170**, not
135). Its shape is a module-level pure function returning `Optional[str]`, keyed on `response.id`
first, with a local `from firestarter.messages import …` to avoid an import cycle:

```python
def _boot_block_hint_message(response, protocol: int, mem_size: int) -> Optional[str]:
    """Return a boot-block-locked inference hint string, or None.
    ...
    Wording per A3 / STRIDE T-94-MISLABEL: the hint INFERS the lockout from the
    address range; it does NOT confirm it ...
    """
    from firestarter.messages import MSG_ERR_FL4_VERIFY_TIMEOUT

    if response.id != MSG_ERR_FL4_VERIFY_TIMEOUT:
        return None
    if protocol != _FLASH4_PROTOCOL_ID:
        return None
    ...
    return hint
```

Also copy its module-level constant block (`:94-103`: `_BOOT_BLOCK_SIZE`, `_TIMEOUT_ADDR_RE`,
`_FLASH4_PROTOCOL_ID`) as the home for `_BUDGET_FAILURE_IDS`, and its wiring at `:568-572` (the
`" -- " + hint` composition) for the new hint. Message-id values verified in
`firestarter/messages.py`: `MSG_ERR_PULSE_TOO_WIDE = 0xAE` (`:106`), `MSG_ERR_MAX_PULSES = 0xBD`
(`:121`), `MSG_ERR_ENERGY_CAP = 0xBE` (`:122`), `MSG_DATA_PROGRESS = 0xE0` (`:123`),
`MSG_ERR_WRITE_FAILED = 0xB1` (`:109` — **the dead id, D-20**).

**Typed-exception dispatch is already centralised** (`:75-91`) — the hint needs no new exception type:

```python
def _raise_for_error_response(response, message: str) -> None:
    """Raise ProtocolNotImplementedError for id 0xBB, EpromOperationError otherwise.
    ...
    """
    from firestarter.messages import MSG_ERR_PROTOCOL_NOT_IMPLEMENTED

    if response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED:
        raise ProtocolNotImplementedError(response.message, error_code=response.id)
    raise EpromOperationError(message, error_code=response.id)
```

**(5) `pulse_us` on `write_eprom` — analog: `consistency_check_eprom`'s DB-dict override** (`:766-773`;
CONTEXT's `:765-777` and RESEARCH's `:762-773` both drift by a line):

```python
            # Merge read-timing knobs into eprom_data_dict copy so they ride
            # into _setup_operation via command_dict = eprom_data_dict.copy().
            # Emit each key only when non-zero (firmware defaults apply when absent).
            # Pattern: consistent with how pulse-delay already travels via the DB dict.
            if read_settling_us or read_strobe_us:
                eprom_data_dict = dict(
                    eprom_data_dict
                )  # shallow copy — never mutate caller's dict
                if read_settling_us:
                    eprom_data_dict[JSON_KEY_READ_SETTLING_DELAY] = read_settling_us
                if read_strobe_us:
                    eprom_data_dict[JSON_KEY_READ_STROBE_US] = read_strobe_us
```

Signature-side analog (`:709-710`) — the µs-parameter comment convention:

```python
        read_settling_us: int = 0,  # address-settling delay (µs; 0=firmware default)
        read_strobe_us: int = 0,  # /CE read-strobe pulse width (µs; 0=firmware default)
```

The dict reaches the wire through `_setup_operation`'s copy at **`:335`** (CONTEXT says `:337`):

```python
        command_dict = eprom_data_dict.copy()  # Work with a copy for the command
```

**One verified difference from the analog:** `"pulse-delay"` is emitted **unconditionally** by
`database.py:555` (`"pulse-delay": full_eprom_data.get("pulse-delay", 0),`), so the override
*replaces* an always-present key rather than adding one. Emit-only-when-non-zero still applies to the
*override*, not to the key.

**Read the budget INSIDE the `with`** — analog: `write_eprom`'s own `seen_message_ids` check and its
comment (`:1591`, `:1612-1634`):

```python
        with self._operation_context(
            eprom_name, eprom_data_dict, COMMAND_WRITE, operation_flags, address_str,
        ) as (cmd_data, buf_size, op_name):
...
            # ... This check MUST read self.comm.seen_message_ids
            # here, inside the _operation_context `with` block: that block's
            # `finally` calls _disconnect_programmer(), which sets self.comm to
            # None, so a read after the block exits would raise or silently
            # see nothing.
```

**Absent-advertisement fallback — analog: `_calculate_buffer_size`** (`:300-313`), including the
reversal history D-10 rests on:

```python
    def _calculate_buffer_size(self) -> int:
        # CAP-01 (Phase 55): firmware_max_chunk is now populated by the
        # _decode_id_frame MSG_OK_READY ack override in serial_comm.py ...
        # Phase 54 D-05 is reversed: when the field is absent (old firmware
        # or ack with 0 param bytes), return 512 — the Uno floor, universally
        # safe minimum — instead of raising FirmwareOutdatedError.
        max_chunk = (
            getattr(self.comm, "firmware_max_chunk", None) if self.comm else None
        )
        if max_chunk is not None and max_chunk >= 1:
            return max_chunk
        # CAP-01 safe Uno-floor default: absent advertisement -> 512.
        return 512
```

Copy the `getattr(self.comm, "<attr>", None) if self.comm else None` guard, the `is not None` +
lower-bound test, and the comment naming the default's derivation.

---

### `firestarter_app/firestarter/cli_handlers.py` (MOD — controller, request-response) — PARTIAL ANALOG

**Analog A (the decorator stack `--pulse-us` joins):** `write`'s own options, `:549-589`. Note this is
a **production** command; the nearest µs-option precedent is not.

```python
@cli.command(name="write")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.argument("input_file")
@click.option(
    "-b", "--no-blank-check", "blank_check",
    is_flag=True, flag_value=False, default=True,
    help="Skip the blank check before write (erase still runs if the chip supports it).",
)
...
@click.option("-a", "--address", default=None, help="Write start address in dec/hex")
@click.option("--vpe-as-vpp", "vpe_as_vpp", is_flag=True, help="Use VPE as VPP voltage")
@click.pass_obj
@map_typed_errors
def write(
    app: AppContext,
    eprom: str,
    input_file: str,
    ...
) -> None:
```

Decorator order to preserve: options, then `@click.pass_obj`, then `@map_typed_errors`.

**Analog B (µs-option shape ONLY):** `:1469-1482` — `--read-settling` / `--read-strobe`.

```python
    @click.option(
        "--read-strobe",
        "read_strobe_us",
        type=int,
        default=0,
        help="/CE read-strobe pulse width (µs; 0=firmware default 3µs).",
    )
```

**Two reasons this analog must be copied only partially:**
1. It lives inside the `if _DEV_TOOLS_ENABLED:` block on `dev consistency-check` (`:1485`
   `def dev_consistency_check`) — a **dev-gated** command. `--pulse-us` is on production `write`
   (D-18), so it inherits none of that gating.
2. Its `default=0` is **fatal** when paired with `IntRange(1, 65535)`: Click type-casts the default, so
   `firestarter write` with no flag would exit 2. RESEARCH measured this. Use `default=None`.

**Analog C (the D-17 mandatory report line):** `:666-675` — CONTEXT cites `:616-628` (that is the
docstring reference at `:624-628`); the code is here:

```python
    if is_protocol_0x0d and not allowed and not skip_sdp_unlock:
        skip_sdp_unlock = True
        click.echo(
            f"{eprom.upper()}: auto-setting --skip-sdp-unlock on your behalf "
            f"({sdp_reason}). Firmware's automatic SDP unlock is keyed on "
            "protocol, not on this specific part, so without this the unlock "
            "sequence's command bytes would be stored as data at the "
            "bus-truncated magic addresses on a part with no SDP command "
            "decoder."
        )
```

Copy: `click.echo` (not `logger.info` — this must be default-visible), the `f"{eprom.upper()}: …"`
prefix convention, and the sibling-`if` discipline documented at `:690-699` (a second report block is
a **separate** `if`, never an `elif` chained onto this one, so both can fire on the same chip).

**Call site to thread `pulse_us` through:** `:717-729`

```python
    ok = app.eprom_operator.write_eprom(
        eprom,
        eprom_data,
        input_file,
        address_str=address,
        operation_flags=_build_op_flags(...),
    )
    sys.exit(0 if ok else 1)
```

`eprom_data` here is `resolve_chip(eprom, db=app.db)`'s programmer dict (`:630`) — the same dict the
D-17 line must read the database pulse from.

**Docstring convention:** `write`'s docstring (`:603-629`) records each flag's decision with its
`TRAP #n / D-nn` tag, including the D-17/D-18 "exposed on `write` ONLY" paragraph (`:616-628`) that is
the direct precedent for `--pulse-us`'s own write-only note.

---

### `firestarter_app/firestarter/constants.py` (OPTIONAL MOD — config)

**Analog:** `:139-149`

```python
# Dev sweep knobs — Firmware sync: json_parser.c (key_read_settling, key_read_strobe)
# JSON key name strings for host-tunable read-timing parameters.
# MUST stay in sync with the PROGMEM key strings in firmware json_parser.c.
# Used by consistency_check_eprom() to emit knob values in per-read JSON commands.
JSON_KEY_READ_SETTLING_DELAY = "read-settling-delay"
JSON_KEY_READ_STROBE_US = "read-strobe-us"
# Per-chip page size wire field (PGSZ-03 / CR-01) — Firmware sync: json_parser.c (key_page_size)
# Emitted by eprom_operations.py only when the DB supplies a datasheet-sourced page_size
# (emit-when-present, mirrors read-strobe-us pattern). ...
JSON_KEY_PAGE_SIZE = "page-size"
```

Copy the `# Firmware sync: json_parser.c (key_…)` header line and the "who emits it / when" note. If
`JSON_KEY_PULSE_DELAY` is added, use it at **both** sites (`database.py:555` and the new
`write_eprom` override) so exactly one definition exists — otherwise skip it; it is cosmetic.

---

### `firestarter_app/tests/conftest.py` (MOD — test fixture)

**Analog:** `make_comm`, `:200-231`. Every `SerialCommunicator` attribute must be mirrored here or the
new field becomes an `AttributeError` swallowed by `_probe_port`'s broad `except Exception`.

```python
@pytest.fixture
def make_comm(fake_serial):
    """Factory: build a SerialCommunicator wired to the fake serial port.

    Uses `__new__` to bypass `__init__` (which would try to open a real
    serial.Serial). ...
    """
    from firestarter.serial_comm import SerialCommunicator

    def _factory():
        instance = SerialCommunicator.__new__(SerialCommunicator)
        ...
        # Phase-54 (EVEN-01): firmware-advertised MAIN-path decode capacity (None until probed)
        instance.firmware_max_chunk = None
        # CAP-02: firmware identity + effective HW revision, both carried in the
        # MSG_OK_READY ack. None until probed — and None is a REJECT for the
        # shield-revision gate, so a fixture that forgets these fails closed.
        instance.firmware_identity = None
        instance.hw_revision = None
        # Phase-120 (D-15 / HOST-06): bounded per-connection observed-id record
        instance.seen_message_ids = set()
        return instance

    return _factory
```

Add the CAP-03 attribute in the same commented style, naming CAP-03 and the D-10 fallback semantics.
`build_frame` (`:125-135`) and `_FakeSerial` (`:138-192`, with `feed()` at `:187`) need no change.

---

### `firestarter_app/tests/test_hw_revision_gate.py` (MOD — test, byte layout)

**Analog:** `:162-219` — the ack-fixture builders and the four decode tests.

```python
def _ready_body(params: bytes) -> bytes:
    """Build the `body` _decode_id_frame receives: [id][params][crc]."""
    from tests.conftest import _ref_crc8_ccitt

    payload = bytes([MSG_OK_READY]) + params
    return payload + bytes([_ref_crc8_ccitt(payload)])


def _cap02_params(buffer_size: int, revision: int, identity: str) -> bytes:
    raw = identity.encode("ascii")
    return struct.pack(">H", buffer_size) + bytes([revision, len(raw)]) + raw


def test_decode_extended_ack_populates_all_three_fields(make_comm):
    comm = make_comm()
    body = _ready_body(_cap02_params(1024, REVISION_2_2, "3.0.0:leonardo"))
    comm._decode_id_frame(len(body), body)

    assert comm.firmware_max_chunk == 1024
    assert comm.hw_revision == REVISION_2_2
    assert comm.firmware_identity == "3.0.0:leonardo"
```

Extend `_cap02_params` with an optional budget tail (three lines). The three existing negative tests
are the templates for CAP-03's own: `test_decode_legacy_two_byte_ack_still_yields_buffer_size`
(`:185`), `test_decode_truncated_version_prefix_leaves_identity_none` (`:196`) and
`test_decode_implausible_buffer_size_is_clamped_away` (`:210`) — the last is the exact template for
the budget clamp:

```python
def test_decode_implausible_buffer_size_is_clamped_away(make_comm):
    """The CAP-01 [1, 4096] plausibility clamp survives the widened length
    test -- an absurd advertised size must leave firmware_max_chunk unset so
    the 512 floor applies (T-55-06)."""
    comm = make_comm()
    body = _ready_body(_cap02_params(60000, REVISION_2_2, "3.0.0:uno"))
    comm._decode_id_frame(len(body), body)

    assert comm.firmware_max_chunk is None
```

**D-08's hazard needs ≥2 identity lengths** (e.g. `"3.0.0:uno"` = 9 vs `"3.0.0:leonardo"` = 14): a
fixed-index decode passes for one length and fails for the other, which is the only way to prove
`ver_end` is computed.

---

### `firestarter_app/tests/test_pulse_us_override.py` (NEW — test, CLI + wire capture)

**Analog:** `tests/test_write_skip_sdp_unlock.py:132-195` — a complete hardware-free `write` through
`CliRunner`, with `find_and_connect` patched to capture the composed `command_dict`.

```python
def _drive_write(
    runner: CliRunner, chip: str, tmp_path, make_comm, fake_serial,
    extra_args: list[str] | None = None,
):
    """Invoke `firestarter write <chip> <file> [extra_args]` end to end.

    Drives a full, successful write through a REAL EpromOperator wired to a
    fake serial port -- INIT_DONE -> OK_REQ_DATA (one data block requested) ->
    MAIN_DONE -> END_DONE ... while patching
    `SerialCommunicator.find_and_connect` to capture the composed
    `command_dict` at the exact point it would cross onto the wire.
    """
    input_file = tmp_path / f"{chip}.bin"
    input_file.write_bytes(b"\x01\x02\x03\x04")
    ...
    fake_serial.feed(build_frame(MSG_INIT_DONE, b""))
    fake_serial.feed(build_frame(MSG_OK_REQ_DATA, b""))
    fake_serial.feed(build_frame(MSG_MAIN_DONE, b""))
    fake_serial.feed(build_frame(MSG_END_DONE, b""))

    captured: dict = {}

    def _fake_find_and_connect(command_dict, config, **kwargs):
        captured["command_dict"] = command_dict
        return make_comm()

    app = make_app_context()
    args = ["write", chip, str(input_file), *(extra_args or [])]
    with patch(
        "firestarter.serial_comm.SerialCommunicator.find_and_connect",
        side_effect=_fake_find_and_connect,
    ):
        result = runner.invoke(cli, args, obj=app)
    return result, captured
```

Copy: the frame-feed sequence, the `captured["command_dict"]` closure, `make_app_context()` (a real
`AppContext`, not a `Mock(spec=EpromOperator)` — the module docstring at `:7-11` says why), the
`runner` fixture at `:94-95`, and the import block at `:16-40` including
`from .conftest import _FakeSerial, build_frame` / `make_app_context as _make_app_context`.

**HOST-04's assertion target** is `captured["command_dict"]["pulse-delay"]`; the negative
("no new wire key") is `set(captured["command_dict"]) == <expected key set>`.

**HOST-05 needs one thing this analog does not have:** an exit-code-2 assertion. Click's `IntRange`
refusal is a `UsageError` → `result.exit_code == 2`, and `@map_typed_errors` never sees it (the raise
happens during parameter processing). Also assert `find_and_connect` was **not called** on refusal —
`test_write_skip_sdp_unlock.py`'s `captured` dict staying empty is the ready-made oracle for that.

**Pitfall-3 regression guard:** author `write` with **no** `--pulse-us` and assert exit 0. `firestarter
--help` in CI never invokes `write`, so nothing else catches `default=0`.

---

### `firestarter_app/tests/test_budget_failure_render.py` (NEW — test, transform)

**Analog:** `tests/test_boot_block_hint.py:42-104` — synthesise the decoded `Response` directly, call
the pure hint function, assert on required and forbidden substrings.

```python
def _make_timeout_response(failing_addr: int) -> Response:
    """Build a synthetic MSG_ERR_FL4_VERIFY_TIMEOUT Response.

    Format: "Timeout verifying 0x%02x at 0x%06lx (got 0x%02x)"
    ...
    We synthesise the decoded text directly to match what codec.decode_id_frame
    would produce — avoiding a real wire frame and serial path.
    """
    message = f"Timeout verifying 0x00 at 0x{failing_addr:06x} (got 0x00)"
    return Response(type="ERROR", message=message, payload=None, id=MSG_ERR_FL4_VERIFY_TIMEOUT)


def test_boot_block_hint_first_16k() -> None:
    resp = _make_timeout_response(0x0000FF)
    hint = _boot_block_hint_message(resp, _PROTO_FLASH4, _MEM_SIZE_W29C040)
    assert hint is not None, (
        "FIX-01b: boot-block hint must be returned for first-16K address 0x0000ff"
    )
    # Inference substrings required by the plan (A3 / T-94-MISLABEL)
    assert "may be" in hint, "hint must use inference language 'may be'"
    ...
```

Copy: the synthetic-`Response` builder (id + text, no wire frame), the required-substring assertion
style with a requirement tag in each message, and the `assert hint is None` negative for non-matching
ids. D-21's "no retry advice, no resumption implication" is naturally expressed as **forbidden**
substrings — the mirror of `test_boot_block_hint_non_flash4_protocol_no_hint` (`:136`) and
`test_boot_block_hint_non_timeout_id_no_hint` (`:149`).

**D-20 source-contract leg:** assert no host path keys on `MSG_ERR_WRITE_FAILED` for this family. The
in-repo pattern for a Python-side source scan is the firmware repo's
`tests/test_hv_routing_source_contract_v142.py` (see above) — the same `_strip_comments` +
concatenation-built-needle discipline applies.

---

### `firestarter_app/tests/test_write_response_budget.py` + `test_write_progress.py` (NEW — tests)

**Analog A (the full hardware-free `write_eprom` driver, no CLI):**
`tests/test_eprom_operations.py:1207-1259`

```python
def _drive_write_eprom_for_ack_check(
    tmp_path, make_comm, fake_serial, *, skip_sdp_unlock: bool, ack_present: bool,
):
    """Drive a full, otherwise-successful write_eprom() against a real
    protocol-0x0D chip (at28c256) through a fake serial port.

    Feed sequence ... [WARN] -> INIT_DONE -> OK_REQ_DATA -> MAIN_DONE ->
    END_DONE. The WARN frame MUST land inside the INIT (or END) phase
    window, never inside MAIN: _main_phase_send_data's tight
    request/response loop only tolerates MAIN/ERROR/OK-request-chunk
    responses and raises EpromOperationError on anything else ...
    """
    ...
    def _fake_find_and_connect(command_dict, config, **kwargs):
        return make_comm()

    operator = EpromOperator(ConfigManager())
    with patch(
        "firestarter.serial_comm.SerialCommunicator.find_and_connect",
        side_effect=_fake_find_and_connect,
    ):
        ok = operator.write_eprom("at28c256", _at28c256_programmer_dict(), str(input_file), ...)
    return ok
```

**This docstring is load-bearing for HOST-02's tests:** it states that a non-`MAIN`/`ERROR`/`OK` frame
inside the MAIN window raises today. A DATA frame fed **between** `OK_REQ_DATA` and `MAIN_DONE` is
therefore the RED-first fixture for the new DATA branch, and the same placement note explains why
today's suites feed WARN frames inside INIT instead.

**Analog B (the call-argument oracle idiom):** `tests/test_submit.py:324-330`

```python
    argv = run_fn.call_args[0][0]
    ...
    assert "shell" not in run_fn.call_args.kwargs
```

Apply the same `call_args` / `call_args.kwargs` inspection to a wrapped
`SerialCommunicator.get_response`, asserting the `timeout` it receives. This is Pitfall 6's primary
oracle: it runs in milliseconds where a real-timeout test would run for 120 s (`_FakeSerial.read()`
returns `b''` immediately and `_read_and_parse_lines` sleeps 1 ms per empty read without resetting
`start_time` — `serial_comm.py:426-430`).

**Analog C (the existing DATA-render test):** `tests/test_eprom_operations.py:98`
`test_handle_progress_response_data_path` — the template for a progress-render assertion.

**D-12's negative proof** is the same `call_args` assertion applied to `verify_eprom` (`:1675`),
`read_eprom`, `check_eprom_blank`, `erase_eprom` and the chip-id path: each must still see 10.

---

### `firestarter/CLAUDE.md` (MOD — documentation)

**Analog:** its own §"Algorithm Handlers" 0x07/0x08/0x0B rows. Each row already carries this phase's
precedents in the required voice: the corrected `99998 µs` derivation (0x0B row), the
`command_done()`-is-a-source-contract-not-a-behavioural-claim sentence (all three rows), and the
"proven only in the emitted control-register stream, never on a part" boundary (0x08 row). D-06's
non-claim — *EPROM path only, and delivered on `leonardo` only* — belongs in the same rows, in the same
"**Honest headline:** / **Boundary:**" shape.

---

## Shared Patterns

### S-1: Length-discriminated wire extension (`MSG_OK_READY`)
**Source:** `firestarter_app/firestarter/serial_comm.py:349-377` (CAP-01 `:356-363`, CAP-02 `:364-376`)
**Apply to:** `serial_comm.py`, `src/firestarter.cpp`, `tests/test_hw_revision_gate.py`
**Rule:** length gate → `struct.unpack(">H", …)` → plausibility clamp → assign, else leave `None`.
Never index before gating; never use a fixed offset past CAP-02's variable tail. The catalog entry is
`params=(("bytes","hex"),)` with `param_bytes=-1` (`messages.py:142-150`), so **no `messages.toml`
edit and no codegen run** — `messages.py` is generated and must never be hand-edited.

### S-2: Absent advertisement means safe default, never an error
**Source:** `firestarter_app/firestarter/eprom_operations.py:300-313`
**Apply to:** the D-10 fallback in `eprom_operations.py`, and every CAP-03 test
**Rule:** `getattr(self.comm, "<attr>", None) if self.comm else None`, then a lower-bound test, then a
documented derived default. Phase 54's `FirmwareOutdatedError` was **reversed** into this shape — cite
that reversal, it is the argument against refusing the write.

### S-3: Ack discipline on DATA frames
**Source:** `firestarter_app/firestarter/eprom_operations.py:480-488` (`ack_data=False`, INIT/END) vs
`:534-535` (`ack_data=True`, MAIN flow control)
**Apply to:** the new MAIN-phase DATA branch (`ack_data=False`, D-05)
**Rule:** render always, ack only where the firmware consumes one. The
`#write-empty-input-regression` comment is the required citation.

### S-4: PROGMEM reads and Arduino-header abstinence
**Source:** `firestarter/src/proms/eprom_params.cpp:11-15, 23` + `firestarter/src/proms/eprom.cpp:310-314`
**Apply to:** `eprom_budget.{h,cpp}`
**Rule:** `pgm_read_byte` / `pgm_read_dword` per field into locals; no `Arduino.h`; `#include
<stdint.h>` + `"rurp_platform_compat.h"`. The native watermark is 1166 with **zero** headroom and the
AVR policy in `scripts/baseline/size_baseline.json` is `avr_rule: "== 0"` — any new warning on `uno`,
`uno328pb` or `leonardo` turns `check_build_warnings.py` RED.

### S-5: Source-contract gate construction
**Source:** `firestarter/tests/test_hv_routing_source_contract_v142.py` (whole module), itself
citing `firestarter/tests/test_write_path_source_contract_v131.py:203-235`
**Apply to:** the `#ifndef SERIAL_ON_IO` gate; the D-20 no-`0xB1` leg
**Rule:** stdlib-only module; `_REPO_ROOT` from `_HERE.parent`; import-time env seam per scanned file;
shape-preserving comment stripper; brace-matched body extraction; concatenation-built forbidden
needles + a self-check that they appear nowhere verbatim; a non-vacuity leg that recomputes defaults
**without** reading `os.environ`; explicit no-skip leg. Say honestly which CI legs run it.

### S-6: Mandatory, default-visible provenance line
**Source:** `firestarter_app/firestarter/cli_handlers.py:666-675` (and the sibling-`if` discipline at
`:690-699`)
**Apply to:** the D-17 `--pulse-us` report line
**Rule:** `click.echo` (never `logger.info`), `f"{eprom.upper()}: …"` prefix, name both the value
replaced and the value used, and use a **separate** `if` so it can co-fire with the D-04/D-13 lines.

### S-7: Advancing-clock native mock
**Source:** `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp:141-168`
**Apply to:** `test_loop_eprom_v131.cpp`'s `setUp`
**Rule:** file-static counter, reset in `setUp`, `When(Method(ArduinoFake(Function), millis)).AlwaysDo(
[&]() { counter += N; return counter; })`. Prove non-vacuity in both directions: clock frozen → 0
frames; clock advancing → N ≥ 2 frames with monotonically increasing first params. Filter captured
frames by id — the capture stub records `MSG_DEBUG` entries too.

### S-8: Commit before running the full firmware suite
**Source:** `firestarter/tests/test_flash_path_record_sync.py` (F-141-11, orphaned)
**Apply to:** every firmware plan's verification block
**Rule:** it asserts whole-repo `git status --porcelain`. Sequence commit-then-test, never
test-then-commit, or it goes RED for the wrong reason. D-23's one-commit `eprom.cpp` rule interacts
with this: the golden's working-tree leg goes RED on the first keystroke and its blob-SHA leg only
after commit.

---

## No Analog Found

| File / Mechanism | Role | Data Flow | Reason |
|------------------|------|-----------|--------|
| `cli_handlers.py` — `click.IntRange` bounds enforcement (D-15) | controller | request-response | **Zero** `IntRange` usages anywhere in `firestarter_app/firestarter/` or `tests/` (verified by grep). Every existing numeric option is bare `type=int`. Use RESEARCH §Pattern 7's measured behaviour table as the specification, and treat `--read-strobe`'s `default=0` as an **anti**-pattern, not a template. |
| CAP-03 host↔firmware **byte-layout parity** assertion | test | byte layout | No existing gate compares the two repos' wire layouts. Meta `CLAUDE.md` requires `serial_comm.py` and `firestarter.cpp` to move in lockstep, but nothing enforces it — which is exactly why BF-1 went unnoticed. RESEARCH Open Question 4 hands this to Phase 144/TEST-07; if this phase authors it, the closest shape is `test_hw_revision_gate.py`'s fixture-decoded-by-the-real-decoder tests (`:175-219`). |

Everything else has a concrete in-tree analog.

---

## Corrections to Upstream Citations

Read this before quoting any CONTEXT.md or RESEARCH.md line number into a plan.

| Upstream claim | Corrected fact |
|----------------|----------------|
| RESEARCH: the frame-capture `rurp_log_id` override is at `test/native/avr/_shared/host_stubs_common.inc:268` | **Wrong file.** `host_stubs_common.inc` contains no `rurp_log_id`. The strong override and all six accessors are at `test/native/avr/test_loop_eprom_v131/host_stubs.cpp:230-281`. |
| CONTEXT D-13 / RESEARCH: "the `start_time` resets at `:448` / `:513`" | Neither fires for a binary id frame. The reset a `0xE0` progress frame hits is **`serial_comm.py:502`**. `:448` is the pre-preamble text flush; `:513` is the newline text path. |
| RESEARCH Open Question 1 / A6: unresolved — "confirm the exact ordering at plan time"; a DB-pulse-of-0 chip might advertise a 2 s budget | **RESOLVED YES.** `parse_json` (`src/firestarter.cpp:52`) calls `configure_memory` at `:92`; `init_programmer_framed` (`:115`) calls `parse_json` at `:130` and emits the ack at `:157`. `configure_eprom`'s fallback (`src/proms/eprom.cpp:68-75`) has already run. No spurious-timeout path. Residual: non-memory commands skip `configure_memory`, but `eprom_params_for()` returns NULL there → budget 0 → host clamp → `None` → D-10 fallback. |
| CONTEXT: `_boot_block_hint_message` at `:106-135` | The function is `:106-170` (RESEARCH's `:106-170` is right). |
| CONTEXT: `_setup_operation`'s `command_dict` copy at `:337` | `:335`. |
| CONTEXT: `consistency_check_eprom`'s DB-dict override at `:765-777`; RESEARCH: `:762-773` | `:766-773` (the `if` is at `:766`). |
| CONTEXT: the D-04 report-line precedent at `cli_handlers.py:616-628`; RESEARCH: `:667-677` / `:667-690` | The `click.echo` block is `:666-675`. `:616-628` is the docstring paragraph about it (also worth citing, for the D-18 write-only precedent). |
| CONTEXT: `--read-settling`/`--read-strobe` at `:1470-1484`; RESEARCH: `:1469-1494` | Options at `:1469-1482`; handler `def dev_consistency_check` at `:1485`. **Both live inside `if _DEV_TOOLS_ENABLED:`** — the analog is a dev-gated subcommand, not a production one. |
| CONTEXT: `write_eprom`'s `self.comm`-is-None warning at `:1620-1631` | `:1612-1634`. |
| CONTEXT/RESEARCH: `mem_util_blank_check`'s `0xE0` emit at `memory.cpp:558` | Correct — but it is **conditional**: `if (handle->cmd != CMD_BLANK_CHECK)` at `:466`, with the programmer-mode-drop rationale at `:461-465`. Cite the gate, not just the call. |
| RESEARCH BF-1: firmware emits a 2-byte ack; CAP-02 absent from the v1.31 branch | **Re-verified this session** at `src/firestarter.cpp:157`: `LOG_OK_ID_U16(MSG_OK_READY, (uint16_t)DATA_BUFFER_SIZE);`. BF-1 stands. |
| — (not stated upstream) | `eprom_params_t`'s field order is **largest-first**: `overprogram_cap_us` is the FIRST column, not `max_pulses` (`include/eprom_params.h:52-59`). The row literals at `eprom_params.cpp:45-49` are positional, so a reader assuming `max_pulses` first misreads all three rows. `sizeof == 12` is `static_assert`-pinned. |
| — (not stated upstream) | `include/eprom_params.h` gets PROGMEM via `#include "rurp_platform_compat.h"`, not `<avr/pgmspace.h>` directly. `eprom_budget.h` should do the same. |

---

## Metadata

**Analog search scope:**
- `/workspaces/firestarter_app/firestarter/` (`serial_comm.py`, `eprom_operations.py`,
  `cli_handlers.py`, `constants.py`, `database.py`, `messages.py`)
- `/workspaces/firestarter_app/tests/` (`conftest.py`, `test_hw_revision_gate.py`,
  `test_write_skip_sdp_unlock.py`, `test_eprom_operations.py`, `test_boot_block_hint.py`,
  `test_submit.py`)
- `/workspaces/firestarter/src/` (`firestarter.cpp`, `proms/eprom.cpp`, `proms/eprom_params.cpp`,
  `proms/memory.cpp`, `boards/uno_rurp_shield.cpp`)
- `/workspaces/firestarter/include/` (`eprom_params.h`, `logging_id.h`, `rurp_shield.h`)
- `/workspaces/firestarter/tests/` (19 pytest gate modules; `test_hv_routing_source_contract_v142.py`,
  `test_protocol_branch_inventory.py`, `golden/protocol_branch_inventory.json`)
- `/workspaces/firestarter/test/native/avr/` (`test_loop_eprom_v131/`, `test_cobs_data_frame/`,
  `_shared/host_stubs_common.inc`), `platformio.ini`

**Files read this session:** 26 (13 host, 13 firmware). **Grep sweeps:** 14.

**Branch state:** both submodules on `gsd/v1.31-27c-programming-algorithm-fidelity`.

**Pattern extraction date:** 2026-08-12
