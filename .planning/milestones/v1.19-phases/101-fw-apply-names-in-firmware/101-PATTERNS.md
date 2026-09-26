# Phase 101: FW — Apply Names in Firmware - Pattern Map

**Mapped:** 2026-07-01
**Files analyzed:** 4 primary targets (1 new, 3 modified) + 7 conformance-confirm handler pairs + 2 doc/parser edits
**Analogs found:** 4 / 4 (all in-repo, exact-role analogs read this session)

> This is a **rename/relabel-only** phase. There is no new business logic. The
> "patterns to copy" are therefore *existing firmware conventions the new/edited
> files must match exactly* — not new feature scaffolding. Every excerpt below is
> the literal substitution surface or the literal style template.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/include/proto_constants.h` **(NEW)** | config (constant home) | transform (label→number) | `firestarter/include/firestarter.h` (`#define` block + include-guard) | exact (same repo, same header idiom) |
| `firestarter/src/proms/memory.cpp` **(MOD)** | dispatch (router) | request-response (protocol→handler) | *self* — the dispatch chain is its own ground-truth; relabel in place | n/a (edit-in-place) |
| `firestarter/include/{eprom,sram,flash_type_3,flash_type_4,eeprom_28c,flash_intel,not_implemented}.h` + matching `.cpp` **(CONFORMANCE-CONFIRM, D-01)** | handler (family) | request-response | `firestarter/include/eprom.h` (representative `extern "C"` handler header) | exact — approved names == current names (NO rename) |
| `firestarter_app/tests/test_dispatch_mirror.py` **(MOD, Wave 0, D-03)** | test (guard) | transform (doc-table parse) | *self* — `parse_protocols_md()` / `_ROW_RE` parser must be re-pinned to Phase-100 table shape | n/a (fix-in-place) |
| `firestarter/CLAUDE.md` **(MOD, likely)** | doc | — | *self* — "Algorithm Handlers" + dispatch-order tables carry OLD prose names | n/a (doc sync) |

**Not touched (assert by diff-scope, GATE-02/03):** `firestarter_app/firestarter/constants.py` (D-02 — firmware-only, no PROTO_ mirror), `chip_database.json`, `tools/check_dispatch.py` dispatch strings, `tools/diff_db.py`, `test_configure_memory.cpp` (hard-coded hex handles — stays green through a relabel).

---

## Pattern Assignments

### `firestarter/include/proto_constants.h` (NEW — config/constant home, FW-01)

**Analog:** `firestarter/include/firestarter.h` — copy its include-guard, comment, and `#define`-block idioms verbatim.

**Include-guard + license-header pattern** (`firestarter.h` lines 1-14) — copy this exact frame, swapping the guard token:
```c
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#ifndef __FIRESTARTER_H__
#define __FIRESTARTER_H__

#include <stdbool.h>
#include <stdint.h>
```
→ For the new file use `#ifndef __PROTO_CONSTANTS_H__ / #define __PROTO_CONSTANTS_H__ ... #endif // __PROTO_CONSTANTS_H__` (matches `firestarter.h`'s `#endif  // __FIRESTARTER_H__` at line 118 and `eprom.h`'s `#endif // __EPROM_H__`).

**`#define` constant-block pattern** (`firestarter.h` lines 34-68) — the flag/command block is the exact idiom for the PROTO_ block: bare `#define NAME 0xNN`, hex literals, grouped with blank lines and a `// Comment` section header:
```c
#define CMD_IDLE 0
#define CMD_READ 1
...
// Control flags
#define FLAG_FORCE 0x01
#define FLAG_CAN_ERASE 0x02
```
→ Emit `#define PROTO_FLASH_5V_PAGE 0x05` … one per row of the 14-row approved map. Plain integer literals, **no suffix** (RESEARCH §Note: `handle->protocol` is `uint32_t`; `#define` compares fine). Values are the VERBATIM hex from PROTOCOLS.md — the label IS the number.

**Phantom-token caveat** (RESEARCH Pitfall 4 — this is the one non-obvious line):
```c
#define PROTO_PHANTOM_0x35 0x35   // honest non-protocol: IC2_ALG_ITE (ITE EC MCU label), 0 DB chips, dispatch-preserved
#define PROTO_PHANTOM_0x39 0x39   // honest non-protocol: no IC2_ALG constant exists, 0 DB chips, dispatch-preserved
```
`0x35` inside the identifier is literal text, not a hex literal — this is a legal C identifier. **Do NOT "fix" it to `_35`** (operator-approved spelling). Verify by `pio run -e uno` after adding the header.

**Verbatim 14-token map to emit** (from `firestarter/doc/PROTOCOLS.md` bucket table @ `6e7bd38`, lines 30-43):

| `#define` | value |
|-----------|-------|
| `PROTO_FLASH_5V_PAGE` | `0x05` |
| `PROTO_FLASH_NOR_UNLOCK` | `0x06` |
| `PROTO_EPROM_28PIN` | `0x07` |
| `PROTO_EPROM_32PIN` | `0x08` |
| `PROTO_EPROM_24PIN` | `0x0B` |
| `PROTO_EEPROM_PARALLEL` | `0x0D` |
| `PROTO_SRAM_32PIN` | `0x0E` |
| `PROTO_FLASH_INTEL` | `0x10` |
| `PROTO_SRAM_24PIN` | `0x27` |
| `PROTO_SRAM_28PIN` | `0x28` |
| `PROTO_SRAM_32PIN_NVRAM` | `0x29` |
| `PROTO_EEPROM_8051BUS` | `0x34` |
| `PROTO_PHANTOM_0x35` | `0x35` |
| `PROTO_PHANTOM_0x39` | `0x39` |

> Note: `0x34` (`PROTO_EEPROM_8051BUS`) has NO dispatch arm in `memory.cpp` — it falls through the generic `protocol != 0` guard (line 116). Emit the constant for completeness/cross-reference, but the dispatch relabel below does NOT reference it.

---

### `firestarter/src/proms/memory.cpp` (MOD — dispatch/router, FW-02)

**Analog:** *self.* The dispatch chain is the ground truth; relabel token-for-token **in place**, preserving exact line order (Pitfall 5). Add `#include "proto_constants.h"` alongside the existing handler includes (lines 13-24).

**Include-add site** (lines 13-24, current):
```cpp
#include "eprom.h"
#include "flash_type_3.h"
#include "flash_type_4.h"
#include "flash_intel.h"
#include "eeprom_28c.h"
...
#include "sram.h"
```
→ add `#include "proto_constants.h"` in this block.

**Dispatch-arm substitution surface** (lines 74-119, current raw-hex — the exact `if` blocks to relabel). Preserve order and behavior; substitute ONLY the hex literals in the `handle->protocol == …` comparisons:

```cpp
    if (handle->protocol == 0x10) {                 // → PROTO_FLASH_INTEL
        configure_flash_intel(handle);
        return;
    }
    if (handle->protocol == 0x0D) {                 // → PROTO_EEPROM_PARALLEL
        configure_eeprom28c(handle);
        return;
    }
    if (handle->protocol == 0x06) {                 // → PROTO_FLASH_NOR_UNLOCK
        configure_flash3(handle);
        return;
    }
    if (handle->protocol == 0x05 || handle->protocol == 0x35 || handle->protocol == 0x39) {
        configure_flash4(handle);                   // → PROTO_FLASH_5V_PAGE || PROTO_PHANTOM_0x35 || PROTO_PHANTOM_0x39
        return;
    }
    if (handle->protocol == 0x07 || handle->protocol == 0x08 || handle->protocol == 0x0B) {
        configure_eprom(handle);                    // → PROTO_EPROM_28PIN || PROTO_EPROM_32PIN || PROTO_EPROM_24PIN
        return;
    }
    if (handle->protocol == 0x0E || handle->protocol == 0x27 ||
        handle->protocol == 0x28 || handle->protocol == 0x29) {
        configure_sram(handle);                     // → PROTO_SRAM_32PIN || PROTO_SRAM_24PIN || PROTO_SRAM_28PIN || PROTO_SRAM_32PIN_NVRAM
        return;
    }
```

**Explicitly-relabel arm (FW-02 mandate):** the `0x05 || 0x35 || 0x39` arm (lines 89-92) is the ONE arm FW-02 mandates receive the phantom tokens.

**Leave-as-raw-hex arms (D-04):**
- The `0x11 || 0x2A || 0x2B || 0x2C` infeasible arm (lines 107-111) has **NO approved tokens** — leave raw hex; do not invent names. Its existing comment (lines 105-106) already documents the intent.
- The generic `if (handle->protocol != 0)` fail-closed guard (line 116) uses the numeric literal `0` — never named. **Preserve exactly** (this is the BLOCKER-2 / 12V-VPP-hazard mitigation, Security Domain).
- The `mem_type` fallback (`TYPE_EPROM` etc., lines 26-29 / 122-134) is `mem_type`, NOT protocol — out of FW-02 scope, leave as-is.

**Order-preservation invariant (Pitfall 5 / Security):** do NOT reorder arms. First-match semantics + the fail-closed guard position (AFTER all implemented cases, BEFORE `protocol==0` fallback) are load-bearing. `test_configure_memory.cpp` (18-case dispatch suite, hard-coded hex) pins this and must stay green with zero edits.

---

### `firestarter/include/*.h` + `src/proms/*.cpp` handler families (CONFORMANCE-CONFIRM — FW-03 / D-01)

**Analog:** `firestarter/include/eprom.h` (representative `extern "C"` handler-header idiom).

**CRITICAL — this is a no-op rename (D-01, RESEARCH Handler Inventory):** Phase 100's approved family names ARE the already-existing function/file names. FW-03 is satisfied by **confirming conformance**, NOT renaming. A wholesale rename would touch 100+ refs (`configure_sram` 30, `configure_eprom` 18, `configure_flash4` 15, `configure_flash3` 14, `configure_flash_intel` 13, `configure_eeprom28c` 13, `configure_not_implemented` 5) across both repos and re-open Phase 100.

**Conformance table to assert** (approved name == current name for all 7):

| Family | Approved `configure_*` | Approved file | Current (verified) | Delta |
|--------|------------------------|---------------|--------------------|-------|
| eprom | `configure_eprom()` | `eprom.cpp` | `configure_eprom` / `eprom.cpp` | NONE |
| sram | `configure_sram()` | `sram.cpp` | `configure_sram` / `sram.cpp` | NONE |
| flash4 | `configure_flash4()` | `flash_type_4.cpp` | `configure_flash4` / `flash_type_4.cpp` | NONE |
| flash3 | `configure_flash3()` | `flash_type_3.cpp` | `configure_flash3` / `flash_type_3.cpp` | NONE |
| eeprom28c | `configure_eeprom28c()` | `eeprom_28c.cpp` | `configure_eeprom28c` / `eeprom_28c.cpp` | NONE |
| flash_intel | `configure_flash_intel()` | `flash_intel.cpp` | `configure_flash_intel` / `flash_intel.cpp` | NONE |
| not-implemented | `configure_not_implemented()` | `not_implemented.cpp` | `configure_not_implemented` / `not_implemented.cpp` | NONE |

**Representative handler-header idiom** (`eprom.h`, full file — the template if any *optional* PROTO_-token cross-reference comment is added):
```c
#ifndef __EPROM_H__
#define __EPROM_H__

#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif

    void configure_eprom(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif
#endif // __EPROM_H__
```
→ If the planner elects the optional cross-reference (RESEARCH rec #2), add ONLY a `// serves PROTO_EPROM_28PIN / _32PIN / _24PIN` comment above the declaration. Do NOT change the signature, the `extern "C"` block, or the guard. **Warning sign the planner has over-reached (Pitfall 1):** any diff touching a function signature, `check_dispatch.py::dispatch()` return string, or `DOC_FILE_TO_FUNC` value.

---

### `firestarter_app/tests/test_dispatch_mirror.py` (MOD — Wave 0 guard fix, D-03 / FW-03)

**Analog:** *self.* The parser is RED at baseline — Phase 100 restructured the PROTOCOLS.md bucket table so the `.cpp` filename left the column `_ROW_RE` scans.

**The exact broken parser site** (lines 52 + 67-80) — this is the fix surface:
```python
_ROW_RE = re.compile(r"^\|\s*0x([0-9A-Fa-f]+)\s*\|[^|]*\|\s*`([a-z0-9_]+\.cpp)`\s*\|")
...
def parse_protocols_md() -> dict[int, str]:
    result: dict[int, str] = {}
    text = _PROTOCOLS_MD.read_text(encoding="utf-8")
    for line in text.splitlines():
        m = _ROW_RE.match(line)
        if m:
            result[int(m.group(1), 16)] = m.group(2)
    return result
```

**Root cause (VERIFIED against live PROTOCOLS.md):** `_ROW_RE` expects `` `<file>.cpp` `` in **column 3**. The current bucket table (PROTOCOLS.md lines 30-43) is 7 columns wide and column 3 is now the **frozen slug** (`` `0x05-FLASH-AMD-STD` ``); the `handler-family` column holds a bare family name (`flash4 (0x05 + phantoms 0x35/0x39)`), NOT a `.cpp`. The `.cpp` filenames now live ONLY in the separate **Handler-family layer** table (PROTOCOLS.md lines 49-57), whose rows start with `| eprom |` / `| flash4 |` etc. → `_ROW_RE.match()` never fires → `parse_protocols_md()` returns `{}` → the guard's `assert doc_table` (line 101) fails.

**Recommended fix (RESEARCH Open Q2 option a):** re-point the parser to derive `{hex_int → handler_file}` by joining the two current tables:
1. Parse the bucket table (lines 30-43) for `hex → handler-family` (the family word is the first token of the `handler-family` column, e.g. `flash4`, `eprom`, `sram`, `not-implemented`).
2. Parse the Handler-family layer table (lines 49-57) for `family → file` (`| flash4 | ` + backtick-`configure_flash4()` + backtick-`` `flash_type_4.cpp` ``).
3. Compose to `hex → .cpp`, then the existing `DOC_FILE_TO_FUNC` map (lines 56-64, unchanged) resolves to the check_dispatch function name.

Keep `DOC_FILE_TO_FUNC` (lines 56-64) as-is — the 7 file→func mappings are still correct (no handler rename per D-01). Only the *doc-side extraction regex/logic* changes. The `not-implemented` family maps `.cpp` → `"not_implemented"` (note: no `configure_` prefix on the func string, matching `check_dispatch.dispatch()`).

**Must end GREEN** — GATE-01 names this guard explicitly; the baseline is NOT clean (D-03). Wave 0 must land this before any GATE-01 "green" assertion.

> Also-failing-but-out-of-scope (RESEARCH A4): `test_audit_coverage_matrix.py::test_golden_file_matches` (v1.3 coverage snapshot, unrelated to naming). Independent test; does not block the pytest run. Do NOT fix in Phase 101.

---

### `firestarter/CLAUDE.md` (MOD — doc sync, likely in-scope)

**Analog:** *self.* The "Algorithm Handlers" table and the dispatch-order list carry OLD prose names (`EPROM_STD`, `FLASH_AMD_STD`, `FLASH_EEPROM`, `FLASH_AMD_ALT`, etc.). `firestarter/CLAUDE.md` states its dispatch table "must match `memory.cpp` line-for-line"; after relabeling `memory.cpp`, update the CLAUDE.md dispatch list + Algorithm-Handlers "Name" column to the new PROTO_ tokens (100-VERIFICATION.md flagged this deferred to 101/102/103). Pitfall 6.

---

## Shared Patterns

### Constant-definition idiom (firmware)
**Source:** `firestarter/include/firestarter.h` lines 34-68 (`#define NAME 0xNN` blocks with `// Section` comment headers) + lines 8-9/118 (include-guard).
**Apply to:** `proto_constants.h` (the only new file). Plain `#define`, hex literals, no suffix, `__PROTO_CONSTANTS_H__` guard.

### `extern "C"` handler-header idiom
**Source:** `firestarter/include/eprom.h` (full file).
**Apply to:** any handler header IF an optional PROTO_ cross-reference comment is added — comment only, never touch the signature/guard/`extern "C"` frame.

### Dispatch-order + fail-closed invariant (behavior-preservation)
**Source:** `firestarter/src/proms/memory.cpp` lines 74-137.
**Apply to:** the FW-02 relabel. Substitute hex→token in place; NEVER reorder arms; preserve the `protocol != 0` guard at line 116 (BLOCKER-2 / 12V-VPP hazard, Security Domain). Pinned by `test_configure_memory.cpp` (unchanged) — a relabel that keeps 82/82 native cases green + byte-stable `pio run -e uno` proves behavior-identity.

### Doc↔code table sync
**Source:** `firestarter/doc/PROTOCOLS.md` @ `6e7bd38` is the ONE authoritative name set (no naming invented here).
**Apply to:** `test_dispatch_mirror.py` parser (read the new 2-table structure) and `firestarter/CLAUDE.md` (update prose names). Both must reflect the PROTOCOLS.md tables verbatim.

### GATE-02 no-change guards (assert identity, not edit)
**Source:** `tools/check_dispatch.py` (hex-based Python twin), `tools/diff_db.py`, `test_revision_constants_parity.py` (6 hard-literal cases, ZERO PROTO_ coverage).
**Apply to:** all plans — these must stay green with NO edit. `constants.py` gets NO PROTO_ block (D-02) → parity test count stays 6 (Pitfall 3 warning sign: count changes).

---

## No Analog Found

None. Every file has an in-repo analog (the constant home mirrors `firestarter.h`; the dispatch, guard, and handler files are edited/confirmed in place). This is a relabel phase — there is no novel role requiring a RESEARCH.md fallback pattern.

## Metadata

**Analog search scope:** `firestarter/include/`, `firestarter/src/proms/`, `firestarter/doc/PROTOCOLS.md`, `firestarter_app/tests/`, `firestarter/CLAUDE.md`
**Files scanned/read this session:** `memory.cpp`, `firestarter.h`, `eprom.h`, `test_dispatch_mirror.py`, `PROTOCOLS.md` (bucket + handler-family tables), plus both CLAUDE.md files (provided as context)
**Pattern extraction date:** 2026-07-01
**Source-of-truth commit:** PROTOCOLS.md @ `6e7bd38`; dispatch chain @ `memory.cpp` lines 74-137 (v1.16 tip a296195 lineage)
