# Phase 118: OBSERVE — auto-unlock visible + opt-out-able (FW half) - Pattern Map

**Mapped:** 2026-07-28
**Files analyzed:** 11 (2 firmware production, 1 firmware config, 2 firmware test suites, 1 shared test header, 3 meta catalog/CI, 3 host gate files, 1 new planning doc)
**Analogs found:** 9 / 11 with a real in-tree analog; **2 have NO analog and that is a finding, not a gap to be papered over** (see §"No Analog Found")

**Repo layout reminder:** meta = `/workspaces/`, firmware = `/workspaces/firestarter/`, host = `/workspaces/firestarter_app/`.
Both sub-repos verified on `v1.22-at28c-software-data-protection-lifecycle`; firmware HEAD `f8d10a5`, host HEAD `9dd11a9`.

---

## Line-drift audit vs 118-CONTEXT.md

**Every line citation in CONTEXT.md `<canonical_refs>` was re-verified against the current tree. ZERO drift.** Planner may trust CONTEXT's line numbers verbatim.

| CONTEXT claim | Verified |
|---|---|
| `eeprom_28c.cpp` `PAGE_SIZE 64` at :33 | ✅ :33 |
| `AT28C_TWC_MAX_MS` at :42, comment :35-42 | ✅ comment :35-41, `#define` :42 |
| `EEPROM_SDP_DISABLE[6]` at :106-114 | ✅ extern decl :106, definition :107-114 |
| emitter comment :190-205, `eeprom28c_emit_command_sequence` :206-222 | ✅ exactly |
| `eeprom28c_wait_for_sdp_completion` :256-269 | ✅ exactly |
| `eeprom28c_write_init` :271-301, emit call :291, wait :297 | ✅ exactly |
| `eeprom28c_write_execute` :303-341, `set_data` loop :317-320 | ✅ exactly |
| `firestarter.h` FLAG block :59-68, `is_flag_set` :70-71, `ctrl_flags` :96 | ✅ exactly |
| `logging_id.h` `LOG_ID`/`LOG_ID_U32` :28-37, `LOG_INFO_ID*` :42-84 | ✅ exactly |
| `check_no_log_in_sdp_window.py` :89-94, :104-107, :119-151, :208-232, :234-236 | ✅ exactly |
| `test_filter` contains `test_eeprom28c_sdp` | ✅ `platformio.ini:119` (and `test_sdp_harness` at :118) |
| `messages.toml` INFO free from `0x5E`, WARN free from `0x86` | ✅ highest INFO `0x5D` (:269), highest WARN `0x85` (:334) |

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter/src/proms/eeprom_28c.cpp` (modify) | protocol handler | request-response + event-driven bus I/O | **itself** (post-117); nearest sibling shape `firestarter/src/proms/flash_5v_page.cpp:61-77` | exact (self) |
| `firestarter/include/firestarter.h` (modify: `FLAG_SKIP_SDP_UNLOCK 0x100`) | config / constants header | n/a | the `FLAG_*` block itself, :59-68 | exact |
| `tools/catalog/messages.toml` (meta, modify: 4 new ids) | data/config (canonical catalog) | transform → codegen | existing INFO `0x58/0x59` and WARN `0x84/0x85` entries | exact |
| `firestarter/include/messages.h` (**GENERATED — never hand-edit**) | generated header | codegen output | — | n/a |
| `firestarter_app/firestarter/messages.py` (**GENERATED — never hand-normalise**) | generated module | codegen output | — | n/a |
| `firestarter_app/tools/check_no_log_in_sdp_window.py` (rewrite window) | source-scan gate (utility) | transform / batch | **itself** — reuse `_strip_comments`/`_find_function_body`/`_find_anchor` | exact (self) |
| `firestarter_app/tests/fixtures/planted_log_in_window.cpp` (re-plant) | test fixture | n/a | **itself** | exact (self) |
| `firestarter_app/tests/test_check_no_log_in_sdp_window.py` (update) | test | subprocess-level gate test | **itself** — 6-case shape is the house triple | exact (self) |
| `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (add cases + `micros` mock) | native Unity test | ordered-stream assertion | `test_sdp_harness/test_sdp_harness.cpp` setUp :70-95 | exact |
| `firestarter/platformio.ini` | config | n/a | `test_filter` at :102-119 — **no change expected**, both suites already listed | exact |
| `.planning/phases/118-…/118-MEASUREMENT.md` (new, D-13) | planning doc | n/a | `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`, `.planning/phases/116-…/116-PREMISE.md` | role-match |

---

## Pattern Assignments

### `firestarter/src/proms/eeprom_28c.cpp` — the sole firmware production file

#### (a) Where the before-line goes — `eeprom28c_write_init`, lines 271-301 (verbatim)

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
    // Disable SDP (Software Data Protection) before writing. The sequence is
    // emitted through handle->firestarter_set_data (i.e. memory_set_data),
    // ... [comment continues :281-290]
    eeprom28c_emit_command_sequence(handle, EEPROM_SDP_DISABLE, sizeof(EEPROM_SDP_DISABLE) / sizeof(EEPROM_SDP_DISABLE[0]));
    // Wait for the SDP-disable internal write cycle to complete. FIX-02: the
    // ... [comment continues :293-296]
    eeprom28c_wait_for_sdp_completion(handle);
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}
```

Concrete placement facts for the planner:
- **The `if (handle->chip_id > 0) { … }` block ends at :279.** CONTEXT's discretionary "before-line must sit after `eeprom28c_check_chip_id`'s early-return" therefore means: emit at :280 or later, i.e. between the closing `}` of the identity block and the `eeprom28c_emit_command_sequence(...)` call at :291.
- **The `micros()` bracket (D-05) goes at :291** — one `micros()` read immediately before the call on :291, one immediately after. Both are OUTSIDE `eeprom28c_emit_command_sequence`'s body (:206-222), which is what makes D-05's "perturb inter-byte timing not at all" literally true.
- **The skip gate (D-02)** wraps :291 + :297 as a pair. Note that on the skip path the completion wait must also be skipped — there is no internal write cycle to wait for.
- **`FLAG_SKIP_BLANK_CHECK` at :298 is the in-file idiom for a skip gate** — `if (!is_flag_set(FLAG_X)) { do_the_thing(); }`. Copy that shape, inverted, for `FLAG_SKIP_SDP_UNLOCK`.

#### (b) The **accepted** WARN shape (D-02's severity precedent) — `eeprom_28c.cpp:142-151`

```cpp
    if (handle->mem_size < 64) {
        if (is_flag_set(FLAG_FORCE)) {
            LOG_WARN_ID_U32(MSG_WARN_MEM_SIZE_TOO_SMALL, (uint32_t)handle->mem_size);
            handle->response_code = RESPONSE_CODE_WARNING;
        } else {
            LOG_ERROR_ID_U32(MSG_ERR_MEM_SIZE_TOO_SMALL, (uint32_t)handle->mem_size);
            handle->response_code = RESPONSE_CODE_ERROR;
        }
        return;
    }
```

**Copy the `LOG_WARN_ID*` spelling; DO NOT copy the `handle->response_code = RESPONSE_CODE_WARNING;` line** — D-02 and Phase 117 D-05 forbid it in the SDP path, and `test_case8_completion_poll_preserves_prior_severity` enforces it. This is the closest live WARN call site and it is in the same file, 130 lines above the edit site.

#### (c) The **rejected** INFO shape (D-02's rejected precedent) — `flash_5v_page.cpp:61-77`

```cpp
void flash_5v_page_write_init(firestarter_handle_t* handle) {
    if (!is_operation_in_progress(handle)) {
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }

        if (is_flag_set(FLAG_CAN_ERASE)) {
            if (!is_flag_set(FLAG_SKIP_ERASE)) {
                flash_5v_page_erase_execute(handle);
            } else {
                LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);      // <-- flash_5v_page.cpp:70, the REJECTED shape
            }
        }
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}
```

Sibling at `flash_nor_unlock.cpp:85-86` (the D-04 two-separate-ids precedent):
```cpp
                LOG_DEBUG_ID_SUB(DBG_SKIPPING_ERASE_MEMORY);
                LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE_MEM);
```
Note the paired `LOG_DEBUG_ID_SUB` — a discretionary composable idiom (zero flash cost in production builds) if the planner wants a debug breadcrumb alongside the new report lines.

#### (d) D-10's citation site — `eeprom28c_write_execute` per-byte loop, lines 317-320 (verbatim)

```cpp
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, data);
```

The comment naming the shared t_BLC exposure goes immediately above :317 (inside the function, after the `window_start` declaration at :316) or above :320. **No code change here** — D-10 is citation-only, and the framing must aim at gh#11's *conflation*, never at "sampling rate" (Phase 117 correction).

#### (e) The constant block to extend — `eeprom_28c.cpp:35-42` (verbatim)

```cpp
// AT28C datasheet-max write-cycle time (t_WC), in milliseconds -- the
// unconditional wall-clock floor D-04 requires before polling for SDP-disable
// completion [CITED: Microchip DS20006432B section 6.6.2 p.10 / DS20006386B
// p.10, via .planning/research/SUMMARY.md]. Sibling of, not a duplicate of,
// Phase 118's AT28C_TBLC_MAX_US = 100: that constant bounds the *inter-byte*
// window inside the SDP-disable command sequence itself; this one bounds the
// *internal write cycle* that follows the sequence's last byte.
#define AT28C_TWC_MAX_MS 10
```

**This comment already forward-declares `AT28C_TBLC_MAX_US = 100` by name and draws the t_BLC-vs-t_WC distinction (:39-41).** Add the new `#define` adjacent to :42 and *extend* — do not restate the distinction. Verified: `AT28C_TBLC_MAX_US` currently exists **only** in this comment (`eeprom_28c.cpp:39`), nowhere else in the firmware tree.

#### (f) The hard constraint on the emitter body — `eeprom_28c.cpp:196-222` (verbatim, load-bearing)

```cpp
// Hard constraint on this body: nothing bus-visible beyond the explicit
// data-direction call below and the set_data loop. The SDP_FIXED_* goldens
// (test/native/avr/_shared/sdp_expected.h) were recorded from
// drive_reference_emitter's bare set_data loop
// (test_sdp_harness.cpp/test_eeprom28c_sdp.cpp) -- any additional
// bus-visible call (in particular a firestarter_set_control_register
// bracket, the way flash_util_byte_flipping brackets its loop) appends
// recorded strobes and breaks cases 1-3's full-stream equality. No LOG_ call
// belongs here either: report lines are Phase 118's OBS-01 scope and must
// sit before or after the sequence, never inside it.
static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length) {
    // D-12: memory_set_data (memory.cpp) never sets the data-bus direction;
    // ... [comment :207-217]
    rurp_set_data_output();
    for (size_t i = 0; i < length; i++) {
        handle->firestarter_set_data(handle, sequence[i].address, sequence[i].byte);
    }
}
```

Body span for D-06's new gate window: **opening `{` on :206, closing `}` on :222.** The scannable inner span is :207-221.

---

### `firestarter/include/firestarter.h` — one new `FLAG_*` define

**Existing block, lines 59-71 (verbatim):**

```c
// Control flags
#define FLAG_FORCE 0x01
#define FLAG_CAN_ERASE 0x02
#define FLAG_SKIP_ERASE 0x04
#define FLAG_SKIP_BLANK_CHECK 0x08
#define FLAG_VPE_AS_VPP 0x10

#define FLAG_OUTPUT_ENABLE 0x20
#define FLAG_CHIP_ENABLE 0x40

#define FLAG_VERBOSE 0x80

#define is_flag_set(flag) \
    ((handle->ctrl_flags & flag) == flag)
```

- **Highest bit currently used: `0x80` (`FLAG_VERBOSE`, :68). `0x100` is free.** Confirmed by exhaustive grep — 8 `FLAG_*` defines, no gaps, nothing above `0x80`.
- **`ctrl_flags` is `uint32_t` (`firestarter.h:96`)** so `0x100` needs no widening. `is_flag_set` is a bare mask macro capturing `handle` from caller scope — works unchanged for `0x100`.
- No new field, no parser change: `json_parser.c`'s `get_flags` uses `extract_long`.
- **`FLAG_SKIP_SDP_UNLOCK` currently exists nowhere in either sub-repo except the reservation comment at `eeprom_28c.cpp:191`.** Verified by grep across both trees.

**Assert the negative (D-03 / CONTEXT explicitly demands this):**
`firestarter_app/tests/test_revision_constants_parity.py:121-145` — the host FLAG parity test. Verbatim, the load-bearing part:

```python
@pytest.mark.skipif(FW_ABSENT, reason="firestarter firmware checkout absent")
def test_flag_values_match_firmware():
    from firestarter.constants import (
        FLAG_CAN_ERASE, FLAG_CHIP_ENABLE, FLAG_FORCE, FLAG_OUTPUT_ENABLE,
        FLAG_SKIP_BLANK_CHECK, FLAG_SKIP_ERASE, FLAG_VERBOSE, FLAG_VPE_AS_VPP,
    )

    assert FLAG_FORCE == 0x01  # FLAG_FORCE
    ...
    assert FLAG_VERBOSE == 0x80  # FLAG_VERBOSE
```

**It imports and asserts exactly eight hardcoded literals; it never enumerates `firestarter.h`.** A firmware-only ninth flag does not trip it. CONTEXT's D-03 claim verified TRUE. Do **not** add `FLAG_SKIP_SDP_UNLOCK` to `firestarter_app/firestarter/constants.py` — that is Phase 120 HOST-03.

---

### `tools/catalog/messages.toml` (meta, canonical) + the three-repo codegen ritual (D-03)

#### Entry shapes to copy

INFO band, zero-param (`messages.toml:223-237`):
```toml
[[messages]]
id          = 0x58
name        = "MSG_INFO_SKIPPING_ERASE"
severity    = "INFO"
format      = "Skipping erase"
params      = []
wire_format = "id_frame"

[[messages]]
id          = 0x59
name        = "MSG_INFO_SKIPPING_ERASE_MEM"
severity    = "INFO"
format      = "Skipping erase of memory"
params      = []
wire_format = "id_frame"
```

INFO band with a u8 param + render hint (`messages.toml:268-274`):
```toml
[[messages]]
id          = 0x5D
name        = "MSG_INFO_CMD"
severity    = "INFO"
format      = "Cmd: 0x%02x"
params      = [{ type = "u8", render = "hex_byte" }]
wire_format = "id_frame"
```

WARN band with a u32 `dec` param — **the shape for a duration-carrying line** (`messages.toml:325-331`):
```toml
[[messages]]
id          = 0x84
name        = "MSG_WARN_MEM_SIZE_TOO_SMALL"
severity    = "WARN"
format      = "Memory size %lu too small for chip-id check"
params      = [{ type = "u32", render = "dec" }]
wire_format = "id_frame"
```

WARN band, u24 hex_addr — D-02's cited severity precedent (`messages.toml:333-339`):
```toml
[[messages]]
id          = 0x85
name        = "MSG_WARN_FL4_BOOT_BLOCK_LOCKED"
severity    = "WARN"
format      = "boot block locked -- 0x%06lx not programmable (W29C040 section 6.6 irreversible lockout, write forced)"
params      = [{ type = "u24", render = "hex_addr" }]
wire_format = "id_frame"
```

⚠ **See §"No Analog Found" #2 — `MSG_WARN_FL4_BOOT_BLOCK_LOCKED` has ZERO firmware call site. It is a catalog-*entry* precedent only, not a call-site precedent.**

Band section comments (do not reorder entries — `messages.toml:3-4`: "DO NOT REORDER ENTRIES. Codegen sorts by id ascending"). New INFO ids go after :274; new WARN ids go after :339, before the `# ERROR (0xA0..0xDF)` divider at :341-343.

#### The ritual, end to end (verbatim from `tools/catalog/sync_to_subrepos.sh`)

Header contract (`sync_to_subrepos.sh:1-19`):
```bash
# Authoritative source: tools/catalog/{messages.toml,codegen.py}
# Generated firmware artifact: firestarter/include/messages.h
# Generated host artifact:     firestarter_app/firestarter/messages.py
#
# Idempotent: re-running with no upstream change is a no-op.
# Run after every catalog or codegen edit.
```

Steps the script performs: (1) copy `messages.toml` + `codegen.py` from meta into both sub-repos' `tools/catalog/`; (2) `diff` the two vendored copies for byte-identity; (3) regenerate:
```bash
python3 "$META_REPO_CATALOG/codegen.py" \
    --catalog "$META_REPO_CATALOG/messages.toml" \
    --language cpp \
    --target "$FS_ROOT/include/messages.h"
...
python3 "$META_REPO_CATALOG/codegen.py" \
    --catalog "$META_REPO_CATALOG/messages.toml" \
    --language python \
    --target "$FA_ROOT/firestarter/messages.py"
```

#### The three drift gates that make it mandatory

1. Meta `.github/workflows/catalog-sync-check.yml:42-53`:
```yaml
      - name: Assert cross-sub-repo vendored catalog identity
        run: |
          cmp firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
          ...
      - name: Assert vendored catalog matches meta-repo authoritative copy
        run: |
          cmp meta/tools/catalog/messages.toml firestarter/tools/catalog/messages.toml
          cmp meta/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
```
⚠ **Both sub-repo checkouts in that workflow use `ref: main` (`catalog-sync-check.yml:27,38`).** This gate compares meta's branch copy against the sub-repos' **`main`**, so it will not go green for v1.22 catalog work until the milestone merges. Plan for a *local* `cmp` of all three copies as the in-phase proof; do not treat a red `catalog-sync-check` on the milestone branch as a phase defect.

2. Firmware `firestarter/.github/workflows/build.yml:60-66`:
```yaml
      - name: Catalog validity check
        run: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check

      - name: Codegen drift gate (messages.h)
        run: |
          python3 tools/catalog/codegen.py \
            --catalog tools/catalog/messages.toml \
            --target include/messages.h \
            --language cpp
          git diff --exit-code include/messages.h
```

3. Host `firestarter_app/.github/workflows/ci.yml:35-44` — the identical `--check` + regenerate + `git diff --exit-code` pair for `firestarter/messages.py`.

#### The precedent commit pair (the exact ritual to replicate)

`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED 0xBB` was added end to end in Phase 63 Plan 01:

- firmware `5b0c053` — `feat(63-01): add MSG_ERR_PROTOCOL_NOT_IMPLEMENTED 0xBB catalog constant (WIRE-01)`; touched exactly `tools/catalog/messages.toml` (+8) and `include/messages.h` (131 changed lines)
- host `b958700` — same subject; touched exactly `tools/catalog/messages.toml` (+8) and `firestarter/messages.py`
- meta side: `d7d0a7e` / `e0bdea4` / `0e9137f` are the meta `tools/catalog/messages.toml` precedents for the same class of edit.

Both commit bodies state *"Regenerate … under Python 3.11 (CI-matching version)"*. **Use python3.11 for codegen; the devcontainer default is 3.12** (`.planning` memory `reference_devcontainer_py312_masks_ci_py39.md`).

⚠ **Column-reflow hazard (this is why 8 catalog lines became a 131-line diff).** `messages.h` pads the `#define` name column to the longest name:
```c
#define MSG_WARN_MEM_SIZE_TOO_SMALL       0x84
#define MSG_WARN_FL4_BOOT_BLOCK_LOCKED    0x85
```
Longest existing name is **`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (32 chars)**. Any new name **≤ 32 chars** leaves the padding untouched and yields a small, reviewable diff; a 33+-char name reflows the whole header. Budget the four new names accordingly (e.g. `MSG_INFO_SDP_UNLOCK` 19, `MSG_INFO_SDP_UNLOCK_DONE_US` 27, `MSG_WARN_SDP_UNLOCK_SKIPPED` 27, `MSG_WARN_SDP_TBLC_EXCEEDED` 26 — all safe). Do **not** hand-normalise `messages.py` (`.planning` memory `reference_codegen_ruff_clean_emitter.md`).

**Graceful degradation confirmed:** `firestarter_app/firestarter/codec.py:206-209` logs `"Unknown message ID 0x.. — catalog out of date?"` and drops the frame, so a released b11 host neither crashes nor garbles the four new ids.

---

### `firestarter_app/tools/check_no_log_in_sdp_window.py` — D-06's window rewrite

#### Machinery to REUSE unchanged

- `_strip_comments` :119-151 (length- and newline-preserving comment blanking; the anti-substring-grep guarantee)
- `_line_of` :154-155
- `_find_function_body` :158-183 — brace-matcher; **currently hard-wired to `_FUNC_DEF_PATTERN` (:78) which is `\bvoid\s+eeprom28c_write_init\s*\([^)]*\)\s*\{`.** D-06 needs *two* bodies (`eeprom28c_emit_command_sequence`, `eeprom28c_wait_for_sdp_completion`), and **both are `static` and one takes a multi-arg signature**:
  - `static void eeprom28c_emit_command_sequence(firestarter_handle_t* handle, const byte_flip_t* sequence, size_t length) {` (`eeprom_28c.cpp:206`)
  - `static void eeprom28c_wait_for_sdp_completion(firestarter_handle_t* handle) {` (`eeprom_28c.cpp:244`)
  ⚠ The existing `_FUNC_DEF_PATTERN` starts at `\bvoid\s+`, which **would still match** `static void foo(` (the `\b` sits before `void`), and `[^)]*` handles the 3-arg signature. But the pattern must be parameterised by function name rather than a module constant. Generalise `_find_function_body(cleaned_text, func_name)`.
  ⚠ **Forward-declaration trap:** both functions have prototypes at `eeprom_28c.cpp:87-88` ending in `;` — the trailing `\{` in the pattern is what excludes them. Preserve it.
- `_find_anchor` :186-194
- `_LOG_CALL_PATTERN` :116 — `\bLOG_[A-Z][A-Z0-9_]*\s*\(` — matches every macro family in `logging_id.h` including the new bare `LOG_ID(`/`LOG_ID_U32(` forms. No change needed.

#### The code being REPLACED — :216-236 (verbatim)

```python
    emit_match = _find_anchor(_EMIT_ANCHOR_PATTERNS, body_text, 0)
    if emit_match is None:
        raise ValueError(
            f"no command-emit anchor found inside {_FUNC_NAME}() -- if the "
            "emitter was renamed or replaced, add the new anchor to "
            "_EMIT_ANCHOR_PATTERNS in check_no_log_in_sdp_window.py rather "
            "than deleting this gate"
        )

    wait_match = _find_anchor(_WAIT_ANCHOR_PATTERNS, body_text, emit_match.end())
    if wait_match is None:
        raise ValueError(
            f"no completion-wait anchor found after the command-emit anchor "
            f"inside {_FUNC_NAME}() -- if the wait call was renamed or "
            "replaced, add the new anchor to _WAIT_ANCHOR_PATTERNS in "
            "check_no_log_in_sdp_window.py rather than deleting this gate"
        )

    window_start = body_start + emit_match.start()
    window_end = body_start + wait_match.start()
    window_text = cleaned[window_start:window_end]
```

The `ValueError` fail-closed idiom (**every message names the fix rather than suggesting deletion**) is the pattern to preserve verbatim in the rewritten resolver. `scan()`'s return contract is `(violations, window_start_line, window_end_line)`; a two-window rewrite must decide whether to keep that 3-tuple (and what the line range means) — the pytest at Test 1 asserts only `"PASS:" in stdout`, so the `main()` print format at :285-288 has latitude.

**Append-only contract (:85-88, :102-103):** `_EMIT_ANCHOR_PATTERNS` (:89-94) and `_WAIT_ANCHOR_PATTERNS` (:104-107) each still carry their pre-Phase-117 predecessors. **If the rewrite stops using them for window resolution, do not delete them** — D-06's rewrite replaces the *call-site span*, and the anchors are the file's documented rename tripwire. Prefer keeping them as function-name anchors for the two new bodies.

---

### `firestarter_app/tests/fixtures/planted_log_in_window.cpp` — the load-bearing re-plant

Current fixture, verbatim (full file, 37 lines):

```cpp
/*
 * DELIBERATELY-VIOLATING fixture for
 * tests/test_check_no_log_in_sdp_window.py (Phase 116 Plan 04, TRACE-03c).
 *
 * This file is a minimal, standalone, never-compiled C++ source. It is not
 * built by platformio.ini and is not part of any firmware target. It exists
 * ONLY so the paired pytest can point tools/check_no_log_in_sdp_window.py's
 * FIRESTARTER_SDP_SRC env-override seam at it and prove the checker actually
 * exits non-zero on a real logging call planted inside the SDP timing
 * window.
 *
 * "Fixing" this file (i.e. removing the planted LOG_INFO_ID(...) call below)
 * would silently hollow TRACE-03's third negative -- the anti-hollow gate
 * this project has required since the v1.12 hollow-GATE-03 tech debt. Do
 * NOT "fix" this file. If the checker's anchors ever change shape, update
 * this fixture to match the new shape (keeping the planted violation
 * between the anchors), do not delete the violation.
 */

void eeprom28c_write_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        eeprom28c_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
    // Disable SDP (Software Data Protection) before writing.
    flash_execute_command(EEPROM_SDP_DISABLE);
    LOG_INFO_ID(MSG_DEBUG);  // PLANTED VIOLATION -- inside the SDP timing window
    // Wait for SDP disable internal write cycle to complete
    if (!eeprom28c_wait_for_write(handle, 0x5555, 0x20)) {
        return;
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
}
```

**CONTEXT's D-06 hazard confirmed against the tree.** The planted `LOG_INFO_ID(MSG_DEBUG);` is on line **29**, sitting **between** `flash_execute_command(EEPROM_SDP_DISABLE);` (:28) and `eeprom28c_wait_for_write(...)` (:31). Under D-06's new window definition (emitter body + completion-poll body) that placement is legal → checker returns 0 → the pytest's `assert result.returncode == 1` goes RED **and** the gate goes hollow. The fixture must gain a `static void eeprom28c_emit_command_sequence(...) { … LOG_… … }` body with the violation **inside** it, in the same commit.

⚠ **Second-order hazard the planner must own:** the pytest hardcodes the violation's line number:
```python
    assert "line 29" in result.stdout, (
        f"Expected the FAIL: output to name the planted line (29) but got:\n"
        f"{result.stdout}"
    )
```
(`tests/test_check_no_log_in_sdp_window.py:99-103`). **Any re-plant shifts that line and breaks this assertion even if the gate works.** Update the literal in the same commit.

---

### `firestarter_app/tests/test_check_no_log_in_sdp_window.py` — the complete gate+fixture+test triple to copy

This file **is** the in-tree canonical triple. Its six-case structure (docstring :20-30):

| # | Case | Function |
|---|---|---|
| 1 | clean-source control → exit 0 + `"PASS:"` | `test_checker_exits_zero_on_clean_source` :62-73 |
| 2 | **committed planted violation → exit 1 + names the line + names the macro** (the anti-hollow proof) | `test_checker_exits_nonzero_on_committed_planted_violation` :81-105 |
| 3 | out-of-window control → exit 0 (discriminates by position, not presence) | :113-135 |
| 4 | comment-not-a-call control → exit 0 (proves `_strip_comments`, not a grep) | :143-171 |
| 5 | fail-closed: missing source path → non-zero + `"ERROR:"` on stderr | :179-190 |
| 6 | fail-closed: emit anchor absent → non-zero + `"add the new anchor"` | :198-217 |

The subprocess harness (:45-53) — copy verbatim:
```python
def _run_checker(
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, "tools/check_no_log_in_sdp_window.py"],
        cwd=str(_FA_DIR),
        capture_output=True,
        text=True,
        env=env,
    )
```

Test 2's docstring states the project's anti-hollow rule explicitly and is worth quoting into the plan:
> *"An exit-code-only assertion would not be enough on its own -- pairing it with the output-content assertion below is what makes this a genuine anti-hollow proof rather than a coincidence (e.g. the checker crashing for an unrelated reason)."*

**D-06 needs cases 3 and 4 rewritten too**, not just 2: their temp-file sources use the *old* call-site shape (`flash_execute_command` + `eeprom28c_wait_for_write` inside `eeprom28c_write_init`) and contain no emitter/poll body at all, so under the new resolver they will hit the fail-closed `ValueError` path and exit non-zero — flipping two currently-green tests RED. **Four of the six cases are affected; the planner should name all four.**

**Other planted-fixture precedents in the host tree (for the anti-hollow shape):**
- `tests/test_sdp_table_parity.py:223-263` — `test_altered_temp_copy_fails_parity_non_vacuous` (temp-copy planted violation, no committed fixture) and `:266+` `test_missing_override_path_fails_closed`. Uses the same env-override seam idiom.
- Other env-override-seam gates worth reading for idiom consistency: `tools/check_dispatch.py` (`FIRESTARTER_DB_FILE`), `tools/check_devtest_orchestrator.py` (`FIRESTARTER_DEVTEST_SRC`), `tools/check_no_community_support_status_write.py` (Phase 114 DISP-01 AST lock).
- ⚠ `tests/fixtures/` contains **exactly one** file: `planted_log_in_window.cpp`. The "multiple committed planted fixtures" precedent CONTEXT gestures at is realised as *temp-file* plants in the other gates' pytests, not as committed fixtures. This is the only committed one.

---

### Firmware native test suites — `micros()` mocking + stream assertions

#### The `millis()` mock to copy, and where `micros` goes — `test_eeprom28c_sdp.cpp:94-118` (verbatim)

```cpp
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    /* REQUIRED (mirrors test_sdp_harness.cpp / D-05): the real
     * rurp_register_utils.h calls delayMicroseconds, and
     * eeprom28c_check_chip_id / eeprom28c_wait_for_write call delay() /
     * delayMicroseconds() too. ArduinoFake ABORTS (SIGABRT) on any unmocked
     * virtual. Do not remove these as "unused" -- they are load-bearing. */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();
    When(Method(ArduinoFake(), delay)).AlwaysReturn();
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);

    clear_strobes();
    reset_register_cache(0x00, 0x00, 0x00);

    s_mfr_addr_keyed = 0;
    s_mfr_hi_keyed = 0xFF;
    s_mfr_lo_keyed = 0xFF;
    s_reads_at_mfr_addr = 0;
    s_reads_at_poll_addr = 0;
    s_poll_addr_toggles = false;
}
```

`test_sdp_harness.cpp:70-95` is **byte-identical for the mock block** (lines 71-84), minus `s_poll_addr_toggles`. So the `micros` mock is a one-line insertion after `millis` in **both** suites:
- fixed-value variant: `When(Method(ArduinoFake(), micros)).AlwaysReturn(0);` → duration 0, budget never exceeded
- controllable-counter variant (needed for a budget-exceeded case, CONTEXT-recommended): `Return(a, b)` / `AlwaysDo(...)` over a file-static counter. Note the two `micros()` reads bracket the emit call, so exactly **two** returns per drive.

⚠ **`micros()` appears nowhere in the firmware today** (verified: zero hits in `src/` and `include/` excluding `delayMicroseconds`). Any suite that drives `eeprom28c_write_init` and lacks the mock will SIGABRT, which reads exactly like the deferred D-13 Unity-teardown flake. The full set of suites that call `eeprom28c_write_init`/`configure_eeprom28c` must be swept, not just the two named: check `test_val_eeprom28c` as well.

#### Handle factory + flag injection — `test_eeprom28c_sdp.cpp:126-137`

```cpp
static firestarter_handle_t make_sdp_handle(const sdp_bus_config_row_t& row) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = 0; /* skip chip-id branch for cases 1-5 */
    h.mem_size = row.mem_size;
    h.bus_config = row.bus_config;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK;
    return h;
}
```

D-08's skip case sets `h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_SDP_UNLOCK;`. The sibling `make_identity_handle(expected_chip_id, ctrl_flags)` (:139-155) already takes `ctrl_flags` as a parameter and ORs `FLAG_SKIP_BLANK_CHECK` in — the cleaner analog if `make_sdp_handle` needs a flags argument.

**Note the D-01 mock comment (:147-155):** the suite deliberately does **not** stub `firestarter_set_data`, because FIX-01's emitter is built on that pointer. Only `get_data` is mocked. Do not reintroduce a `set_data` no-op.

#### The stream-equality helper — `_shared/sdp_expected.h:86-107` (verbatim)

```cpp
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
                ctx, div,
                (unsigned)expected[div].kind, (unsigned)expected[div].pin, (unsigned)expected[div].value,
                (unsigned)strobe_kind(div), (unsigned)strobe_pin(div), (unsigned)strobe_value(div));
        } else { ... }
        TEST_FAIL_MESSAGE(msg);
    }
}
```

`SDP_FIXED_*` goldens (D-07's byte-identity subject — **no regeneration expected**):

| Array | Line | `_LEN` macro |
|---|---|---|
| `SDP_FIXED_DIP28_28C256` | :195-224 | :225 |
| `SDP_FIXED_DIP28_28C64` | :227-250 | :251 |
| `SDP_FIXED_DIP24_2816` | :253-276 | :277 |
| `SDP_FIXED_DIP32_28C512_EEPROM` | :286-309 | :310 |
| (`SDP_SHIPPED_DIP28_28C256`, pre-117 reference) | :144-172 | :173 |

First rows of `SDP_FIXED_DIP28_28C256` (:195-204), showing the per-write 10-entry shape:
```cpp
static const sdp_strobe_t SDP_FIXED_DIP28_28C256[] = {
    /* write #1  remap(0x5555)=0x9555  (LSB,MSB)=(0x55,0x95)  payload 0xAA */
    {2, 4, 1},
    {1, 0, 0x55}, {2, 1, 1}, {2, 1, 0},
    {1, 0, 0x95}, {2, 2, 1}, {2, 2, 0},
    {1, 0, 0xAA}, {2, 0x20, 0}, {2, 0x20, 1},
```

**D-07's "report lines are recorder-invisible" claim verified structurally:** `sdp_strobe_t` records only `{kind, pin, value}` with `STROBE_KIND_DATA = 1` / `STROBE_KIND_PIN = 2` (`sdp_expected.h:57-58`) — i.e. `rurp_write_to_register` / `rurp_write_data_buffer` / `rurp_set_control_pin`. `rurp_log_id` → Serial is not a recorded kind, and `Serial.write` is mocked `AlwaysReturn(1)` in both suites' setUp. So a `LOG_*` before/after the emit call cannot append a strobe.

**D-08's "assert on content, never a count" constraint:** the skip-proof case must assert `strobe_count() == 0` **plus** that no `{1, 0, 0x55}`/`{1, 0, 0xAA}` sequence appears — or, cleanest and fully positional, drive with the flag set and assert `sdp_assert_stream_equals(nothing, 0, ...)` is unnecessary because `strobe_count()` is 0. ⚠ Careful: a bare `strobe_count() == 0` **is** a count assertion. The compliant shape is to assert the recorded stream is not equal to `SDP_FIXED_*` at index 0 *and* that the emitter's first strobe `{2, 4, 1}` (the `rurp_set_data_output()`… actually a no-op in stubs) never appears. Simplest content-positional form: `TEST_ASSERT_EQUAL(-1, sdp_first_divergence(SDP_FIXED_DIP28_28C256, SDP_FIXED_DIP28_28C256_LEN))` must be **false** for the skip case, with the assertion phrased as "the recorded stream diverges from the full unlock stream at index 0".

#### `platformio.ini` — no change needed

`test_filter` at :102-119 already contains both:
```ini
	native/avr/test_sdp_harness
	native/avr/test_eeprom28c_sdp
```
(:118, :119). Both also have `-I` entries in `build_flags`. **CONTEXT's claim verified.** The long provenance comment at :85-101 is where any new suite-status note belongs.

---

### `118-MEASUREMENT.md` (new, D-13)

**Analogs:** `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` (verbatim-capture-with-provenance discipline, including its `## Post-suite-edit RED baseline (Phase 117 commit 1 — D-03)` appended-heading convention) and `.planning/phases/116-ground-truth-trace-harness/116-PREMISE.md`.

Required contents per D-13: exact command, the `controller:` identity line, board + firmware build identity, raw captured log. Per CONTEXT `<specifics>`: **no wording that could read as bench-validating `0x0D`.**

---

## Shared Patterns

### Unconditional emission (the D-01 crux)

**Source:** `firestarter/include/logging_id.h`
**Apply to:** the two new INFO-band report lines and the two new WARN lines

```c
// --- Unconditional ID-frame emit ---              // :25
#define LOG_ID(id) rurp_log_id((id), NULL, 0)       // :28
#define LOG_ID_U8(id, p1)     rurp_log_id_u8((id), (uint8_t)(p1))    // :33
#define LOG_ID_U16(id, p1)    rurp_log_id_u16((id), (uint16_t)(p1))  // :34
#define LOG_ID_U24(id, p1)    rurp_log_id_u24((id), (uint32_t)(p1))  // :35
#define LOG_ID_U32(id, p1)    rurp_log_id_u32((id), (uint32_t)(p1))  // :36
```

versus the gated family (:42-49, representative):

```c
// --- FLAG_VERBOSE-gated variants (INFO severity equivalent) ---     // :42
#define LOG_INFO_ID(id)                                                \
    do {                                                               \
        if (is_flag_set(FLAG_VERBOSE)) {                               \
            LOG_ID(id);                                                \
        }                                                              \
    } while (0)
```

**Critical nuance the planner must not miss:** `LOG_WARN_ID*` (:114-119), `LOG_ERROR_ID*` (:105-110), `LOG_OK_ID*`, `LOG_INIT_ID*`, `LOG_MAIN_ID*`, `LOG_END_ID*`, `LOG_DATA_ID*` are **literal `#define` aliases of `LOG_ID*`** — i.e. unconditional. So:
- **D-02's WARN lines have a perfect house-style analog: use `LOG_WARN_ID` / `LOG_WARN_ID_U32`.** No convention is broken there; `eeprom_28c.cpp:138` is a live sibling call site 130 lines up.
- **Only the two INFO-band lines break convention**, because the INFO band's *only* macro family is the gated one. D-01 therefore requires either bare `LOG_ID` / `LOG_ID_U32` with an INFO-band id, or a new unconditional `LOG_INFO_ID*_ALWAYS`-style alias. **Bare `LOG_ID` on an INFO-band id has zero precedent (see below); the pattern-consistent alternative is to add an alias block mirroring :114-119's shape.** That is a planner-level design call this map surfaces rather than settles.

### Deny-list coverage note for the gate

`_LOG_CALL_PATTERN` = `\bLOG_[A-Z][A-Z0-9_]*\s*\(` — matches bare `LOG_ID(` and `LOG_ID_U32(` too. So D-01's chosen spelling stays inside the rewritten gate's coverage without any pattern change.

### `eeprom_28c.cpp` cross-repo source-scan checklist (CORRECTION 4 item 4 — mandatory)

Host gates that read firmware source. **All five re-verified as present on `9dd11a9`:**

| Gate | Scans | Risk from this phase's edits |
|---|---|---|
| `tools/check_no_log_in_sdp_window.py` + `tests/test_check_no_log_in_sdp_window.py` | `eeprom_28c.cpp` window | **HIGH — D-06 deliberately rewrites it; 4 of 6 pytest cases affected** |
| `tests/test_sdp_table_parity.py` | `eeprom_28c.cpp` source text; `_PAIR_RE` :115, `decl_pattern` :134 = `\b{decl_name}\s*\[\s*\d*\s*\]\s*=\s*` matching `EEPROM_SDP_DISABLE` | **MEDIUM — broken 3× by Phase 117. This phase does not touch the table or its declaration syntax, so it should stay green. Re-run explicitly.** |
| `tests/test_dispatch_mirror.py` | `eeprom_28c.cpp` | LOW — dispatch unchanged |
| `tests/test_sdp_db_invariant.py` | `eeprom_28c.cpp` | LOW |
| `tools/gen_sdp_bus_config.py` + `tests/test_sdp_bus_config_drift.py` | generates `_shared/sdp_bus_config.h` | LOW — bus configs untouched |
| `tests/test_revision_constants_parity.py:121-145` | 8 hardcoded `FLAG_*` literals under `FW_ABSENT` skipif | **NONE — verified non-exhaustive; a 9th firmware flag does not trip it** |
| `tools/check_dispatch.py`, `tools/build_db.py` | firmware paths / DB | expected untouched; confirm |

⚠ **The vacuous-path trap:** a `git diff -- <path>` check only proves anything if `<path>` is real. `src/flash_utils.h` does not exist (the ROADMAP shorthand). Any new path-based check written in this phase must be self-proving (e.g. assert the file exists first).

---

## No Analog Found

| # | Claimed pattern | Reality | Consequence for the plan |
|---|---|---|---|
| 1 | **A non-verbose-gated INFO-band call site** (D-01's precedent) | **ZERO exist.** Exhaustive grep of `firestarter/src/`: there are **no** bare `LOG_ID(`, `LOG_ID_U8(`, `LOG_ID_U16(`, `LOG_ID_U24(`, `LOG_ID_U32(`, `LOG_ID_BYTES(` call sites at all — every use of those macros is via a severity-named alias. All **19** `MSG_INFO_*` emissions go through `LOG_INFO_ID*` (`flash_5v_page.cpp:70`, `eprom.cpp:104,170`, `dev_tools.cpp:30,40,67,93,135,137,139`, `operation_utils.cpp:189,216,245,247`, `firestarter.cpp:132,134,135,137`, `flash_nor_unlock.cpp:86`). **CONTEXT's D-01 claim is confirmed exactly: this phase creates the tree's first non-verbose-gated INFO-band emission.** The plan must state this in the source comment (CONTEXT `<specifics>`: "the break must be argued in the source comment, not just done") and cannot cite an analog because there is none. |
| 2 | **`MSG_WARN_FL4_BOOT_BLOCK_LOCKED` as a WARN *call-site* precedent** (D-02) | **It has ZERO firmware call sites.** `grep -rn BOOT_BLOCK_LOCKED src/ include/ test/` returns only the generated `include/messages.h:69` and `:97`. The host references are catalog-presence assertions only (`firestarter_app/tests/test_val_wire_5v_page.py:283-301`). It is a **catalog-entry-shape** precedent, not a call-site one. **The live WARN-at-a-decision-point call sites are `eeprom_28c.cpp:138` (`LOG_WARN_ID_U32(MSG_WARN_MEM_SIZE_TOO_SMALL, …)`) and `:168` (`LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, …)`) — use those.** Both are in the file being edited. Note both set `response_code`, which D-02 forbids; copy the macro, not the severity write. |
| 3 | `micros()` anywhere in firmware | **Zero occurrences** (excluding `delayMicroseconds`). No mocking analog exists; the `millis()` `AlwaysReturn(0)` line is the shape to clone. |
| 4 | `AT28C_TBLC_MAX_US` | Exists **only** as prose in `eeprom_28c.cpp:39`. No `#define` anywhere. |
| 5 | `FLAG_SKIP_SDP_UNLOCK` | Exists **only** as prose in `eeprom_28c.cpp:191`. Nowhere in either sub-repo's code. |
| 6 | A serial-frame baseline recorder (for OBS-05's "exactly two new frames") | **None exists** — CONTEXT D-07 already declined building one. Do not invent an analog. |
| 7 | Multiple *committed* planted-violation fixtures | `firestarter_app/tests/fixtures/` contains exactly **one** file. Other gates plant into `tmp_path` temp files instead. The "multiple precedents" are the *pattern*, realised as temp plants in `test_sdp_table_parity.py:223-263` etc. |

---

## Metadata

**Analog search scope:**
`/workspaces/firestarter/{src,include,test/native/avr,tools/catalog,.github/workflows,platformio.ini}`,
`/workspaces/firestarter_app/{firestarter,tools,tests,.github/workflows}`,
`/workspaces/{tools/catalog,.github/workflows}`

**Read in full:** `firestarter/src/proms/eeprom_28c.cpp` (427 lines), `firestarter/include/logging_id.h` (329), `firestarter_app/tools/check_no_log_in_sdp_window.py` (294), `firestarter_app/tests/fixtures/planted_log_in_window.cpp` (37), `firestarter_app/tests/test_check_no_log_in_sdp_window.py` (217).
**Read targeted (non-overlapping):** `firestarter/include/firestarter.h:50-110`, `firestarter/include/messages.h:1-20,55-72`, `firestarter/src/proms/flash_5v_page.cpp:55-79`, `firestarter/src/proms/flash_nor_unlock.cpp:79-94`, `firestarter/platformio.ini:85-130`, `firestarter/test/native/avr/_shared/sdp_expected.h:1-204`, `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:60-175`, `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp:60-110`, `tools/catalog/messages.toml` (band map + entries :220-341), `tools/catalog/sync_to_subrepos.sh` (full), `.github/workflows/catalog-sync-check.yml:30-60`, `firestarter/.github/workflows/build.yml:55-70`, `firestarter_app/tests/test_revision_constants_parity.py:118-148`.

**Pattern extraction date:** 2026-07-28
**Sub-repo HEADs at extraction:** firmware `f8d10a5`, host `9dd11a9`, both on `v1.22-at28c-software-data-protection-lifecycle`
