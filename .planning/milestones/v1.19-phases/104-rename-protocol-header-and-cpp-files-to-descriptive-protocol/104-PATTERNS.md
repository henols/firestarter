# Phase 104: Rename protocol header/.cpp files to descriptive names - Pattern Map

**Mapped:** 2026-07-02
**Files analyzed:** 12 modified (2 renamed FW file-pairs + dispatch/build/doc/host/test references)
**Analogs found:** 12 / 12 (all with exact correctly-named siblings — this is a rename phase)

> **Rename phase, not new-file creation.** No file is authored from scratch. Every "target" is an
> existing file being renamed OR a reference string being rewritten to match an already-descriptive
> sibling. The load-bearing pattern is the **naming + structure convention** the renamed files must
> match. The best analog throughout is `flash_intel` (correctly-named at every layer: FW file-pair,
> dispatch, spec JSON, generated `.h`, `platformio.ini` dir, test suite, PROTOCOLS.md) — with
> `eeprom_28c` as a second FW-file analog.

## Rename Map (LOCKED — from CONTEXT.md §Decisions)

| Old | New | Serves |
|-----|-----|--------|
| `flash_type_3.{cpp,h}` | `flash_nor_unlock.{cpp,h}` | `PROTO_FLASH_NOR_UNLOCK` (0x06) |
| `configure_flash3()` | `configure_flash_nor_unlock()` | 0x06 |
| `flash_type_4.{cpp,h}` | `flash_5v_page.{cpp,h}` | `PROTO_FLASH_5V_PAGE` (0x05) + phantoms 0x35/0x39 |
| `configure_flash4()` | `configure_flash_5v_page()` | 0x05 |
| test-suite dir `test_val_flash3` + family-id `"flash3"` | `test_val_nor_unlock` + `"nor_unlock"` (discretion: follow function stem) | INV-09 |
| test-suite dir `test_val_flash4` + family-id `"flash4"` | `test_val_5v_page` + `"5v_page"` (discretion) | INV-04 |

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---------------|------|-----------|----------------|---------------|
| `firestarter/include/flash_type_3.h` → `flash_nor_unlock.h` | firmware handler (header) | dispatch | `firestarter/include/flash_intel.h`, `eeprom_28c.h` | exact |
| `firestarter/include/flash_type_4.h` → `flash_5v_page.h` | firmware handler (header) | dispatch | `firestarter/include/flash_intel.h` | exact |
| `firestarter/src/proms/flash_type_3.cpp` → `flash_nor_unlock.cpp` | firmware handler (impl) | dispatch | `firestarter/src/proms/eeprom_28c.cpp` | exact |
| `firestarter/src/proms/flash_type_4.cpp` → `flash_5v_page.cpp` | firmware handler (impl) | dispatch | `firestarter/src/proms/eeprom_28c.cpp` | exact |
| `firestarter/src/proms/memory.cpp` | firmware dispatch | dispatch | (self — `flash_intel`/`eeprom_28c` includes+calls in same file) | exact |
| `firestarter/include/flash_utils.h` / `src/proms/flash_utils.cpp` | firmware utility (comments) | — | (self) | trivial |
| `firestarter/platformio.ini` | build config | — | `test_val_flash_intel` entries (lines 93,111) | exact |
| `firestarter/doc/PROTOCOLS.md` | doc | — | `flash_intel` rows (§0 table, §1.x, §3 INV) | exact |
| `firestarter/test/native/avr/test_val_flash3/` (+ `.cpp`) | test suite | dispatch | `test_val_flash_intel/test_val_flash_intel.cpp` | exact |
| `firestarter/test/native/avr/test_val_flash4/` (+ `.cpp`) | test suite | dispatch | `test_val_flash_intel/test_val_flash_intel.cpp` | exact |
| `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | test suite (dispatch) | dispatch | `flash_intel` dispatch test cases | exact |
| `firestarter_app/tests/test_dispatch_mirror.py` | host guard tool | request-response | `flash_intel.cpp`→`configure_flash_intel` row (line 79) | exact |
| `firestarter_app/tools/check_dispatch.py` | host guard tool | dispatch-mirror | `configure_flash_intel` entries | exact |
| `firestarter_app/tools/validation_matrix_spec.json` | generated-artifact source | — | `flash_intel` family object (lines 95-116) | exact |
| `firestarter/test/native/avr/_shared/validation_matrix.h` | GENERATED artifact | — | `flash_intel` row (line 23) — regen, do NOT hand-edit | exact |
| `firestarter_app/tests/test_check_dispatch_invariants.py` | host test | — | `configure_flash_intel` in expected set (line 114) | exact |
| `firestarter_app/doc/protocol-id.md`, `infoic-field-dictionary.md` | host doc | — | `configure_flash_intel` doc rows | exact |

## Pattern Assignments

### `firestarter/include/flash_nor_unlock.h` and `flash_5v_page.h` (firmware header)

**Analog:** `firestarter/include/flash_intel.h` (identical structure, correctly-named).

**Target convention — full file shape** (`flash_intel.h`, 22 lines):
```c
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __FLASH_INTEL_H__
#define __FLASH_INTEL_H__

#ifdef __cplusplus
extern "C" {
#endif
#include "firestarter.h"

    void configure_flash_intel(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif

#endif // __FLASH_INTEL_H__
```

**What to copy for the renamed headers:**
- Header-guard macro form: `__FLASH_NOR_UNLOCK_H__` / `__FLASH_5V_PAGE_H__` (correct spelling — CONTRAST the current MISSPELLED `__FALSH__TYPE_3_H__` / `__FALSH__TYPE_4_H__`).
- Guard appears in **three** places: `#ifndef` (line 8), `#define` (line 9), and the `#endif //` trailing comment (line 22). The analog keeps all three consistent.
- MIT license block (lines 1-6) — preserve verbatim.
- `extern "C"` wrapper + `#include "firestarter.h"` (analog puts the include INSIDE the `extern "C"` block, line 14).
- Function decl indented 4 spaces: `void configure_flash_nor_unlock(firestarter_handle_t* handle);`

> **Latent bug in the OLD `flash_type_4.h`:** its `#ifndef`/`#define` say `__FALSH__TYPE_4_H__`
> (misspelled) but the trailing `#endif // __FLASH__TYPE_4_H__` differs — three-way inconsistency.
> The `flash_intel.h` analog demonstrates all three must be identical. Rewriting to the correct new
> token fixes both the misspelling AND the mismatch.

---

### `firestarter/src/proms/flash_nor_unlock.cpp` and `flash_5v_page.cpp` (firmware impl)

**Analog:** `firestarter/src/proms/eeprom_28c.cpp` (correctly-named handler, same file-header + include convention).

**Include-block convention** (`eeprom_28c.cpp` lines 1-17):
```c
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "eeprom_28c.h"          // <-- own header FIRST, matching basename

#include <Arduino.h>

#include "firestarter.h"
#include "flash_utils.h"
#include "logging_id.h"
#include "memory_utils.h"
#include "operation_utils.h"
#include "rurp_pinout.h"
```

**What to change in the renamed `.cpp` files:**
- Line 8 self-include: `#include "flash_nor_unlock.h"` / `#include "flash_5v_page.h"` (must match new basename — analog shows the self-include is the first `#include`).
- Rename the public entry point only: `configure_flash3` → `configure_flash_nor_unlock`,
  `configure_flash4` → `configure_flash_5v_page`.
- MIT header block (lines 1-6) preserved.

**Internal static-helper naming (`flash3_*` / `flash4_*`) — DISCRETIONARY per CONTEXT Q2/Research.**
The old files use a `<stem>_*` static-helper convention (`flash_type_3.cpp:17-25` declares
`flash3_erase_execute`, `flash3_write_init`, `flash3_get_chip_id`, etc.; `flash_type_4.cpp:27-39`
declares `flash4_page_size`, `flash4_write_init`, etc.). The `eeprom_28c.cpp` analog shows the
convention IS "helpers share the file stem" (`eeprom28c_write_init`, `eeprom28c_wait_for_write` —
lines 21-23). So a *fully consistent* rename would also rename `flash3_*`→`flash_nor_unlock_*` /
`flash4_*`→`flash_5v_page_*`. These helpers are file-internal (not referenced by host tooling), so
this is cosmetic-only. Planner decides scope; if renamed, no cross-repo impact.

---

### `firestarter/src/proms/memory.cpp` (firmware dispatch)

**Analog:** the `flash_intel` and `eeprom_28c` lines in this SAME file (already correctly named).

**Include pattern** (lines 13-17) — the renamed includes must sit alongside the descriptive ones:
```c
#include "eprom.h"
#include "flash_type_3.h"       // → "flash_nor_unlock.h"
#include "flash_type_4.h"       // → "flash_5v_page.h"
#include "flash_intel.h"        // <-- analog: already descriptive
#include "eeprom_28c.h"         // <-- analog: already descriptive
```

**Call-site pattern** — the descriptive analogs (lines 75-83) show the exact protocol-guard shape the
renamed calls (lines 85-93) must match:
```c
if (handle->protocol == PROTO_FLASH_INTEL) {   // analog
    configure_flash_intel(handle);
    return;
}
...
if (handle->protocol == PROTO_FLASH_NOR_UNLOCK) {
    configure_flash3(handle);          // → configure_flash_nor_unlock(handle);
    return;
}
if (handle->protocol == PROTO_FLASH_5V_PAGE || handle->protocol == PROTO_PHANTOM_0x35 || handle->protocol == PROTO_PHANTOM_0x39) {
    configure_flash4(handle);          // → configure_flash_5v_page(handle);
    return;
}
```

**Second call-site — legacy mem_type fallback (lines 129-134):** ALSO calls `configure_flash3`
(line 130) and `configure_flash4` (line 133). Both must be renamed. The `TYPE_FLASH_TYPE_3`/
`TYPE_FLASH_TYPE_4` `#define`s (lines 28,30) name the legacy mem_type ints, NOT the handlers — those
`#define` names are OUT of scope (they mirror the wire `type` int, no host dependency).

---

### `firestarter/test/native/avr/test_val_nor_unlock/` and `test_val_5v_page/` (test suite)

**Analog:** `firestarter/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp` (correctly-named
suite — dir stem, filename, and test-fn prefix all descriptive).

**Naming convention the analog demonstrates:**
- Directory = suite name = filename: `test_val_flash_intel/test_val_flash_intel.cpp`.
- Test functions are prefixed with the family stem, NOT `configure_`:
  `test_flash_intel_write_enables_vpp_p1`, `test_flash_intel_read_configure_only_does_not_enable_vpp`.
  (For the renames: `test_flash4_*`→`test_5v_page_*`, `test_flash3_*`→`test_nor_unlock_*`.)
- Comments/assertions reference the FUNCTION under test: `"configure_flash_intel write must ..."` — so
  in the renamed suites these become `"configure_flash_5v_page ..."` / `"configure_flash_nor_unlock ..."`.

**CRITICAL scoping fact (verified):** the family-id string (`"flash3"`/`"flash4"`) is **NOT embedded in
the test `.cpp` files.** `grep` of `test_val_flash4.cpp` shows it references only the function name
`configure_flash4` and the phantom protocols via `make_handle(0x35, ...)` / `make_handle(0x39, ...)`
(lines 111,120,131) — the phantom-protocol INTEGERS stay unchanged (GATE-01). So the test-`.cpp` edits
are: (a) function-name substitution `configure_flash4`→`configure_flash_5v_page`, (b) test-fn renames,
(c) comment text. The family-id string lives ONLY in the spec JSON, the generated `.h`, and the
`platformio.ini` dir names (below).

---

### `firestarter/platformio.ini` (build config)

**Analog:** the `test_val_flash_intel` entries (already descriptive) at lines 93 (`test_filter`) and
111 (`-I` build_flags).

**Pattern — each suite dir appears in TWO lists (verified: 6 total refs for flash3+flash4):**
```ini
test_filter =
    ...
    native/avr/test_val_flash3      # line 91 → native/avr/test_val_nor_unlock
    native/avr/test_val_flash4      # line 92 → native/avr/test_val_5v_page
    native/avr/test_val_flash_intel # line 93 (analog — leave)
build_flags =
    ...
    -I test/native/avr/test_val_flash3      # line 109 → test_val_nor_unlock
    -I test/native/avr/test_val_flash4      # line 110 → test_val_5v_page
    -I test/native/avr/test_val_flash_intel # line 111 (analog — leave)
```
If the test dirs are renamed (CONTEXT Q2 = yes), all 4 lines (91,92,109,110) update to match the new
`git mv`'d directory names. `test_val_flash_intel` shows the exact string shape.

---

### `firestarter_app/tests/test_dispatch_mirror.py` (host guard — filename→function map)

**Analog:** the `"flash_intel.cpp": "configure_flash_intel"` entry (line 79) — the one correctly-named
row in `DOC_FILE_TO_FUNC`.

**Target dict shape** (lines 74-82):
```python
DOC_FILE_TO_FUNC: dict[str, str] = {
    "flash_type_4.cpp": "configure_flash4",              # → "flash_5v_page.cpp": "configure_flash_5v_page"
    "flash_type_3.cpp": "configure_flash3",              # → "flash_nor_unlock.cpp": "configure_flash_nor_unlock"
    "eprom.cpp": "configure_eprom",
    "eeprom_28c.cpp": "configure_eeprom28c",
    "flash_intel.cpp": "configure_flash_intel",          # <-- ANALOG: descriptive file + descriptive func
    "sram.cpp": "configure_sram",
    "not_implemented.cpp": "not_implemented",
}
```
Both the KEY (`.cpp` filename, parsed from PROTOCOLS.md §0 handler-family table via `_FAMILY_ROW_RE`)
and the VALUE (function name, matched against `check_dispatch.dispatch()`) change. The `flash_intel`
row proves the descriptive form: filename basename == the PROTOCOLS.md `.cpp` cell, function ==
`check_dispatch` return string. **These must move in the same commit as PROTOCOLS.md §0 (Pitfall 1).**

---

### `firestarter_app/tools/check_dispatch.py` (host guard — function-name-keyed)

**Analog:** `configure_flash_intel` appearances (dispatch return line 136, invariant key line 83).

**Two touch points, both keyed on function name only (verified):**
```python
# dispatch() mirror (lines 135-142) — mirrors memory.cpp order:
    if protocol == 0x10:
        return "configure_flash_intel"     # <-- analog
    if protocol == 0x0D:
        return "configure_eeprom28c"
    if protocol == 0x06:
        return "configure_flash3"          # → "configure_flash_nor_unlock"
    if protocol == 0x05:
        return "configure_flash4"          # → "configure_flash_5v_page"
```
```python
# mem_type fallback map (lines 152-157) — ALSO returns the func strings:
    return {1: "configure_eprom", 4: "configure_sram",
            3: "configure_flash3",   # → "configure_flash_nor_unlock"
            5: "configure_flash4"}.get(mem_type, "ERROR")
```
```python
# _FAMILY_VPP_INVARIANTS keys (lines 78-85):
    "configure_flash3": (0, 6000),     # → "configure_flash_nor_unlock": (0, 6000)
    "configure_flash4": (0, 6000),     # → "configure_flash_5v_page": (0, 6000)
    "configure_flash_intel": (10000, 22000),   # <-- analog, descriptive key
```
Note: the phantom-protocol dispatch (0x35/0x39→flash4) is NOT in `check_dispatch.dispatch()` (host
routes them to `not_implemented` — see spec `protocols_note`), so no phantom edit here.

---

### `firestarter_app/tools/validation_matrix_spec.json` (source for generated `validation_matrix.h`)

**Analog:** the `flash_intel` family object (lines 95-116) — descriptive `id` + descriptive `handler`.

**Target object shape** (the `flash4` block, lines 72-94, is the one to reshape):
```json
{
  "id": "flash_intel",                       ← analog: descriptive family id
  "handler": "configure_flash_intel",        ← analog: descriptive handler
  "tier1": { "suite": "test_val_flash_intel", ... }
}
```
For the renames, edit the `flash3` block (line 51-71) and `flash4` block (line 72-94):
- `"id": "flash3"` → `"nor_unlock"`; `"handler": "configure_flash3"` → `"configure_flash_nor_unlock"`;
  `"suite": "test_val_flash3"` → `"test_val_nor_unlock"`.
- `"id": "flash4"` → `"5v_page"`; `"handler": "configure_flash4"` → `"configure_flash_5v_page"`;
  `"suite": "test_val_flash4"` → `"test_val_5v_page"`.
- The `flash4` block's `protocols_note` prose references `configure_flash4` several times — update.
- `protocols` arrays (`[6]`, `[5]`) are the numeric dispatch keys — UNCHANGED (GATE-01).

---

### `firestarter/test/native/avr/_shared/validation_matrix.h` (GENERATED — do NOT hand-edit)

**Analog:** line 23 `{ 0x10, "flash_intel", "configure_flash_intel" }` (descriptive family+handler).

Rows 21-22 today:
```c
{ 0x06, "flash3", "configure_flash3" },     // → { 0x06, "nor_unlock", "configure_flash_nor_unlock" }
{ 0x05, "flash4", "configure_flash4" },     // → { 0x05, "5v_page",   "configure_flash_5v_page" }
```
**Do NOT edit this file by hand** (header says `DO NOT EDIT -- generated by
tools/gen_validation_header.py`). After editing `validation_matrix_spec.json`, regenerate via
`python firestarter_app/tools/gen_validation_header.py` (Pitfall 2). The numeric protocol column
(0x06/0x05) is unchanged.

---

### `firestarter/doc/PROTOCOLS.md` (doc — §0 table, §1.x, §3 INV matrix)

**Analog:** the `flash_intel` §0 row + `configure_flash_intel` handler references.

**Concrete lines to update (grep-verified):**
- §0 handler-family table lines 66-67:
  `| flash4 | \`configure_flash4()\` | \`flash_type_4.cpp\` | 0x05 (...) |`
  `| flash3 | \`configure_flash3()\` | \`flash_type_3.cpp\` | 0x06 (single-protocol) |`
  Both the func cell AND the `.cpp` cell change (this is exactly what `test_dispatch_mirror.py`'s
  `_FAMILY_ROW_RE` + `DOC_FILE_TO_FUNC` join parses — keep lockstep).
- §0 bucket-table lines 45,46,57,58 use the bare family label `flash4`/`flash3` — update to the chosen
  family stem (`5v_page`/`nor_unlock`) for consistency.
- §1.1 line 84 `**Handler:** \`configure_flash4()\` → \`flash_type_4.cpp\``; §1.2 line 104 same for flash3.
- §1.1 line 113 prose `configure_flash3()`; line 356 `configure_flash4()` dispatch prose.
- §3 INV matrix (SAFE-02 suite-path contract): lines 405,407,414,419 map INV-04 →
  `test/native/avr/test_val_flash4/` and INV-09 → `test/native/avr/test_val_flash3/`, plus the
  `flash_type_4.cpp`/`flash_type_3.cpp` owning-handler column and `test_inv04_flash4_*`/
  `test_inv09_flash3_*` planned-test-fn names. All update to the new suite dirs + function stems
  (CONTEXT Q2 intentionally reopens SAFE-02 for this rename). Keep INV-04/INV-09 grep-intact
  (line 398: "one `grep -rn INV-04` must hit this doc row + the native suite").

---

## Shared Patterns

### Header-guard correct form (fix the misspelling)
**Analog source:** `firestarter/include/flash_intel.h:8-9,22` and `eeprom_28c.h:8-9,22`.
**Apply to:** both renamed headers.
```c
#ifndef __FLASH_NOR_UNLOCK_H__       // (was __FALSH__TYPE_3_H__)
#define __FLASH_NOR_UNLOCK_H__
...
#endif // __FLASH_NOR_UNLOCK_H__     // all three occurrences identical
```
Post-rename smoke: `grep -rn FALSH firestarter/` must return nothing (Pitfall 4).

### MIT license header block (preserve verbatim)
**Analog source:** lines 1-6 of every `firestarter/src/proms/*.cpp` and `include/*.h`.
**Apply to:** both renamed file-pairs. Never drop during `git mv` + edit (Pitfall 6).

### `git mv` first, then edit contents (history preservation)
**Apply to:** all 4 renamed FW files + 2 test-suite dirs. `git mv old new` THEN rewrite guard/include/
symbols so git records a rename, not delete+add (Pitfall 5). Run `pio run -t clean` before the
verification build to drop stale `.pio/*.o` (Pitfall 3).

### Numbers stay the dispatch key (GATE-01 discipline)
**Apply to:** every reference. Protocol INTEGERS (`0x05`, `0x06`, `0x35`, `0x39`) and `protocols`
arrays are NEVER changed — only the human-readable file/function/family strings. The phantom
`make_handle(0x35/0x39)` calls in the test suite and the `PROTO_PHANTOM_0x35/0x39` guards in
`memory.cpp` keep their numeric literals.

### Generated-file discipline
**Apply to:** `validation_matrix.h` only. Edit the spec JSON → run `gen_validation_header.py` → the `.h`
regenerates. The `flash_intel` row is the golden shape of the output.

### Dual-repo lockstep (commit-pair)
Firmware (`firestarter/`) and host (`firestarter_app/`) both commit on their own
`v1.19-protocol-naming-labels` branch. The doc↔tool↔firmware bind (`PROTOCOLS.md` §0 ↔
`DOC_FILE_TO_FUNC` ↔ `check_dispatch.dispatch()`) must be internally consistent within the commit-pair
or `test_dispatch_mirror.py` fails (Pitfall 1). Gitlinks stay PINNED per milestone convention.

## No Analog Found

None. Every target has an exact correctly-named sibling (`flash_intel` at every layer; `eeprom_28c` as
a second FW-file analog). This is a mechanical rename to an established convention — the planner should
copy the `flash_intel` shape, not invent structure.

## Metadata

**Analog search scope:** `firestarter/src/proms/`, `firestarter/include/`, `firestarter/test/native/avr/`,
`firestarter/platformio.ini`, `firestarter/doc/PROTOCOLS.md`; `firestarter_app/tests/`,
`firestarter_app/tools/`.
**Files scanned:** ~14 read + grep inventory across both repos.
**Pattern extraction date:** 2026-07-02
