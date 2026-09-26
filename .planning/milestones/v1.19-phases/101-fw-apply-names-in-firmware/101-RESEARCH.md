# Phase 101: FW — Apply Names in Firmware - Research

**Researched:** 2026-07-01
**Domain:** Embedded C/C++ firmware (Arduino/PlatformIO), rename/relabel refactor with strict behavior-preservation gates; dual-repo lockstep (firmware ↔ Python host constants)
**Confidence:** HIGH (all claims verified against the actual repo state this session — files read, guards run, baseline green/red state observed)

## Summary

Phase 101 is a **pure rename/relabel refactor** of firmware C source with zero numeric-value changes. It consumes the operator-approved name set finalized in Phase 100 (recorded verbatim in `firestarter/doc/PROTOCOLS.md`, submodule commit `6e7bd38`). Three mechanical changes: (FW-01) define `PROTO_<NAME>` `#define`s whose numeric value equals the existing protocol hex, (FW-02) relabel the raw-hex `if (handle->protocol == 0x..)` dispatch chain in `src/proms/memory.cpp` to those named constants including honest phantom tokens for the 0x35/0x39 arm, and (FW-03) rename the many-to-one handler files/functions from the approved family-name layer. Every numeric value, dispatch order, and behavior stays identical.

**The single most important finding:** the "approved family-name layer" in PROTOCOLS.md names the handler families using the **already-existing** function/file names — `configure_eprom()`/`eprom.cpp`, `configure_flash3()`/`flash_type_3.cpp`, `configure_flash4()`/`flash_type_4.cpp`, `configure_eeprom28c()`/`eeprom_28c.cpp`, `configure_sram()`/`sram.cpp`, `configure_flash_intel()`/`flash_intel.cpp`, `configure_not_implemented()`/`not_implemented.cpp`. There is **no delta between current names and approved names for the handler layer.** The planner MUST verify this against PROTOCOLS.md §"Handler-family layer" before authoring any file/function rename — FW-03 may be a **no-op (already-conformant)** or require only cosmetic touch-ups, NOT a wholesale rename. Do not invent new handler names.

**Second critical finding:** `firestarter_app/tests/test_dispatch_mirror.py` (the "dispatch-mirror guard" cited in GATE-01) is **already RED on this branch** — Phase 100's restructure of the PROTOCOLS.md bucket table moved the `.cpp` filename out of the table column its regex (`_ROW_RE`) scans, so `parse_protocols_md()` now returns an empty dict and the test fails. This is a pre-existing Phase-100-induced breakage that Phase 101 must reconcile (fix the guard's parser to read the new table structure, or ensure the guard reads the still-intact separate handler-family table at PROTOCOLS.md lines 49–57). The planner must decide the disposition and add a task.

**Primary recommendation:** Create a new header `firestarter/include/proto_constants.h` (or fold into an existing home) with `#define PROTO_<NAME> 0x<hex>` for all 14 tokens, `#include` it in `memory.cpp`, relabel the 6 dispatch `if` blocks, leave handler files/functions as-is unless PROTOCOLS.md's family layer specifies a different name (it does not — they match), decide whether `constants.py` must mirror the new PROTO_ tokens (currently it defines ZERO protocol constants and the parity test asserts none), reconcile the already-red `test_dispatch_mirror.py`, and gate everything on `pio test -e native` (82 cases) + `check_dispatch.py` + `diff_db.py` + the constants-parity pytest, all validated against py3.11 semantics.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `PROTO_<NAME>` constant definitions | Firmware (`firestarter/include/`) | Host (`constants.py`) if lockstep-mirrored | Firmware is where dispatch reads them; label-is-number lives in the C header |
| Raw-hex → named dispatch relabel | Firmware (`src/proms/memory.cpp`) | — | `configure_memory()` is the single dispatch site |
| Handler file/function names | Firmware (`src/proms/*.cpp`, `include/*.h`) | Doc (PROTOCOLS.md family layer is the source-of-truth for the names) | Rename-only; names sourced from Phase-100 doc |
| Dispatch-order integrity guard | Host (`check_dispatch.py`, `test_dispatch_mirror.py`) + Firmware (`test_configure_memory.cpp`) | — | Three-way bind: doc ↔ tool ↔ firmware native test |
| Constants parity | Host (`tests/test_revision_constants_parity.py`) | Firmware header (`firestarter.h`) | Pytest asserts hard-coded literals against header values |
| DB identity | Host (`diff_db.py`) | — | GATE-02: no chip_database.json value change |

## User Constraints (from ROADMAP + REQUIREMENTS — no CONTEXT.md exists for Phase 101)

> **NOTE:** `.planning/phases/101-fw-apply-names-in-firmware/` contains NO `101-CONTEXT.md` (verified: `has_context: false` from init). The binding constraints below are extracted verbatim from `.planning/ROADMAP.md` Phase 101 Success Criteria and `.planning/REQUIREMENTS.md`. If `/gsd-discuss-phase` runs before planning, its CONTEXT.md supersedes this section.

### Locked Decisions (from ROADMAP Phase 101 Success Criteria + REQUIREMENTS FW-01/02/03, GATE-01/02/03)

1. **FW-01:** Firmware defines a `PROTO_<NAME>` constant for every protocol number with its numeric value UNCHANGED (the label IS the number). Dispatch site reads by name (`handle->protocol == PROTO_...`) rather than raw hex.
2. **FW-02:** The raw-hex dispatch chain in `firestarter/src/proms/memory.cpp` is relabeled ENTIRELY to the named constants — including explicitly-non-real phantom tokens for the 0x35/0x39 dispatch arm — dispatch order and behavior preserved.
3. **FW-03:** The many-to-one handler files and functions are renamed FROM THE APPROVED FAMILY-NAME LAYER (`configure_flash3`/`flash_type_3.cpp`, `configure_flash4`/`flash_type_4.cpp`, `configure_eeprom28c`, the SRAM/EPROM family handlers) — a rename ONLY; the groupings are NOT split.
4. **GATE-01:** Protocol numbers remain the dispatch key end to end; no name/token becomes a dispatch or lookup key; algorithm-first dispatch behavior unchanged (golden register traces + dispatch-mirror guard stay green — or re-pin with cited rationale for a purely-cosmetic token change).
5. **GATE-02:** NO `chip_database.json` content change; NO wire / lockstep-constant *value* change — only C-token *names* change, not numeric values. `diff_db.py` shows identity, `check_dispatch.py` passes, constants-parity test holds.
6. **GATE-03:** CLI grammar UNCHANGED — chip selection stays by part number; no protocol name/alias accepted as CLI input (this phase makes NO CLI change). Holds trivially (Phase 101 touches no CLI surface).
7. **Source of truth:** Phase 100's `firestarter/doc/PROTOCOLS.md` (commit `6e7bd38`) is the ONE authoritative name set. No naming is invented in Phase 101 — extract number→PROTO_<NAME> verbatim.
8. **Branch:** firmware sub-repo on `v1.19-protocol-naming-labels` (forked off v1.16 tip `a296195`); gitlinks PINNED (do NOT bump the meta-repo gitlink); lockstep beta cut is operator-gated and OUT OF SCOPE this milestone.
9. **Dual-repo lockstep:** `constants.py` ↔ `firestarter.h` wherever a value crosses the wire. (See Open Question 1 — the PROTO_ tokens may NOT need host mirroring; verify.)

### Claude's Discretion
- The exact filename/location of the new `PROTO_<NAME>` constant home in `firestarter/include/` (new header vs. fold into `firestarter.h`).
- Whether to keep `#define` or use an `enum`/`constexpr` (subject to C-linkage constraints — handlers are `extern "C"`; `memory.cpp` is C++).
- How to phrase the "honest non-real" phantom-token comment in `memory.cpp`.
- The disposition of the already-red `test_dispatch_mirror.py` (fix parser vs. re-pin) — but it MUST end green.

### Deferred Ideas (OUT OF SCOPE)
- **NAME-F1:** Renaming `datasheets/<hex>-<NAME>/` folder slugs (Phase 103 records the divergence; slugs NOT renamed).
- **NAME-F2:** Accepting a protocol name/alias as CLI input (GATE-03 keeps part-number selection).
- Splitting the many-to-one handlers into one-handler-per-protocol (architectural restructure, explicitly out of scope).
- Any `chip_database.json` value change or new chip graduation.
- Host CLI display names (Phase 102) and doc prose/INV-matrix reconciliation (Phase 103).

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FW-01 | Define `PROTO_<NAME>` constants, values unchanged; dispatch reads by name | Verbatim name→hex map extracted below (§Approved Name Set); no PROTO_ constants exist in firmware yet (`grep -rln PROTO_ include/ src/` → none); constant home options in §Constant Home |
| FW-02 | Relabel raw-hex dispatch chain in `memory.cpp`; phantom tokens for 0x35/0x39 | Full verbatim dispatch chain quoted below (§Ground-Truth Dispatch Chain); phantom decision from Phase 100 (`PROTO_PHANTOM_0x35`/`PROTO_PHANTOM_0x39`) |
| FW-03 | Rename handler files/functions from approved family-name layer | Handler-family layer table extracted; **CRITICAL: approved names == current names** (§Handler Inventory) — likely no-op |
| GATE-01 | Numbers stay dispatch key; golden traces + dispatch-mirror guard green | Guard machinery + commands documented (§Guard Machinery); dispatch-mirror guard is **already RED** (pre-existing) — must reconcile |
| GATE-02 | No DB/wire/lockstep-value change; diff_db + check_dispatch + parity green | All three guards run green at baseline this session (§Guard Machinery); parity test asserts NO protocol constants currently |
| GATE-03 | CLI grammar unchanged | Holds trivially — Phase 101 touches no CLI file |

## Approved Name Set (VERBATIM from PROTOCOLS.md @ 6e7bd38 — do NOT paraphrase)

`[VERIFIED: firestarter/doc/PROTOCOLS.md lines 30–45, read this session]`

Every token below has its numeric value = the hex ID (the label IS the number, per FW-01):

| hex | PROTO_ token | display name | handler-family | phantom? |
|-----|--------------|--------------|----------------|----------|
| 0x05 | `PROTO_FLASH_5V_PAGE` | Flash — 5V page-write (EEPROM-like) | flash4 (0x05 + phantoms 0x35/0x39) | no |
| 0x06 | `PROTO_FLASH_NOR_UNLOCK` | Flash — AMD/SST unlock-sequence NOR | flash3 (single-protocol) | no |
| 0x07 | `PROTO_EPROM_28PIN` | EPROM — 28-pin UV/EE, 13V VPP | eprom (0x07/0x08/0x0B) | no |
| 0x08 | `PROTO_EPROM_32PIN` | EPROM — 32-pin UV/EE, 13V VPP | eprom (0x07/0x08/0x0B) | no |
| 0x0B | `PROTO_EPROM_24PIN` | EPROM — 24-pin legacy, 12–25V direct-VPE | eprom (0x07/0x08/0x0B) | no |
| 0x0D | `PROTO_EEPROM_PARALLEL` | EEPROM — 5V parallel, SDP + DQ7 poll | eeprom28c (single-protocol) | no |
| 0x0E | `PROTO_SRAM_32PIN` | SRAM — 32-pin battery-backed NVRAM | sram (0x0E/0x27/0x28/0x29) | no |
| 0x10 | `PROTO_FLASH_INTEL` | Flash — Intel 28F command-register, 12V VPP mandatory | flash_intel (single-protocol) | no |
| 0x27 | `PROTO_SRAM_24PIN` | SRAM — 24-pin async, 5V | sram (0x0E/0x27/0x28/0x29) | no |
| 0x28 | `PROTO_SRAM_28PIN` | SRAM/FRAM — 28-pin (FM1608) | sram (0x0E/0x27/0x28/0x29) | no |
| 0x29 | `PROTO_SRAM_32PIN_NVRAM` | SRAM — 32-pin large battery-backed NVRAM, 512K–1M | sram (0x0E/0x27/0x28/0x29) | no |
| 0x34 | `PROTO_EEPROM_8051BUS` | EEPROM — XICOR 8051-bus, PCB-blocked (FUT-01) | not-implemented (PCB-blocked) | no |
| 0x35 | `PROTO_PHANTOM_0x35` | (phantom — 0 DB chips, dispatch-preserved) | flash4 dispatch arm | **YES** |
| 0x39 | `PROTO_PHANTOM_0x39` | (phantom — 0 DB chips, dispatch-preserved) | flash4 dispatch arm | **YES** |

**Phantom-token honesty decision (Phase 100, operator-approved, changed-from-draft):** `[VERIFIED: 100-01-SUMMARY.md lines 125–126 + PROTOCOLS.md §2.1 lines 347–350]` The two dead-dispatch arms use **hex-in-name spelling** — `PROTO_PHANTOM_0x35` and `PROTO_PHANTOM_0x39` (operator changed these from the draft's numeric `PROTO_PHANTOM_35`/`_39`). Rationale recorded in PROTOCOLS.md §2.1: `0x35` = `IC2_ALG_ITE` (an ITE EC microcontroller label in minipro, NOT a memory algorithm), `0x39` = no `IC2_ALG` constant exists. Both have zero DB chips; firmware dispatch is preserved only for forward-compat. These are honest non-protocols, not FLASH variants — the token name must not imply a real algorithm.

**0x34 note:** token is `PROTO_EEPROM_8051BUS` (operator changed from draft `PROTO_EEPROM_X88C64`). The frozen slug `0x34-EEPROM-X88C64` diverges intentionally (DOC-02 anchor). 0x34 routes to `configure_not_implemented()` — Phase 101 only needs a `PROTO_` constant if the dispatch/comment references it; the current `memory.cpp` does NOT special-case 0x34 (it falls through the generic `protocol != 0` guard). See §Ground-Truth Dispatch Chain.

**Infeasible-bucket note (0x11/0x2A/0x2B/0x2C):** These are named as honest non-protocols in PROTOCOLS.md §2.2 but have NO approved `PROTO_` tokens (out of NAME-01 scope). `memory.cpp` currently dispatches them as raw hex in the "named infeasibility arms" `if` (lines 107–108). REQUIREMENTS.md "Out of Scope" says: *"Phase 101 may reuse the §2.2 'honest non-protocols' labels if it needs constants for that dispatch arm."* → **Discretion:** the planner may leave 0x11/0x2A/0x2B/0x2C as raw hex OR introduce honest tokens; there is no operator-approved token set for them, so any token introduced here is `[ASSUMED]` and should be flagged. Recommended: leave them raw-hex with an explanatory comment to avoid inventing un-approved names (FW-02 only mandates relabeling for the 0x35/0x39 arm explicitly).

## Ground-Truth Dispatch Chain (VERBATIM from memory.cpp)

`[VERIFIED: firestarter/src/proms/memory.cpp lines 74–137, read this session]`

`configure_memory(firestarter_handle_t* handle)` dispatches on `handle->protocol` (a `uint32_t`) in this exact order. Every arm ends with `return;`. This is the ground truth FW-02 relabels:

```cpp
// line 74
if (handle->protocol == 0x10) { configure_flash_intel(handle); return; }
// line 79
if (handle->protocol == 0x0D) { configure_eeprom28c(handle); return; }
// line 84
if (handle->protocol == 0x06) { configure_flash3(handle); return; }
// line 89
if (handle->protocol == 0x05 || handle->protocol == 0x35 || handle->protocol == 0x39) {
    configure_flash4(handle); return;           // ← phantom arm: 0x35/0x39 honest tokens go HERE
}
// line 94
if (handle->protocol == 0x07 || handle->protocol == 0x08 || handle->protocol == 0x0B) {
    configure_eprom(handle); return;
}
// line 99
if (handle->protocol == 0x0E || handle->protocol == 0x27 ||
    handle->protocol == 0x28 || handle->protocol == 0x29) {
    configure_sram(handle); return;
}
// line 107 — named infeasibility arms (0x11/0x2A/0x2B/0x2C) — NO approved PROTO_ tokens
if (handle->protocol == 0x11 || handle->protocol == 0x2A ||
    handle->protocol == 0x2B || handle->protocol == 0x2C) {
    configure_not_implemented(handle); return;
}
// line 116 — generic fail-closed guard (catches 0x34 and all unknown non-zero)
if (handle->protocol != 0) { configure_not_implemented(handle); return; }
// lines 122–134 — legacy mem_type fallback (reachable ONLY when protocol == 0)
//   TYPE_EPROM(1)→configure_eprom, TYPE_SRAM(4)→configure_sram,
//   TYPE_FLASH_TYPE_3(3)→configure_flash3, TYPE_FLASH_TYPE_4(5)→configure_flash4
// line 135 — error: LOG_ERROR_ID_U8(MSG_ERR_MEM_TYPE_UNSUPPORTED, handle->mem_type)
```

**Every protocol dispatched and its handler (the ground-truth table):**

| protocol arm | line | handler | approved PROTO_ tokens to substitute |
|--------------|------|---------|--------------------------------------|
| `== 0x10` | 74 | `configure_flash_intel` | `PROTO_FLASH_INTEL` |
| `== 0x0D` | 79 | `configure_eeprom28c` | `PROTO_EEPROM_PARALLEL` |
| `== 0x06` | 84 | `configure_flash3` | `PROTO_FLASH_NOR_UNLOCK` |
| `== 0x05 \|\| 0x35 \|\| 0x39` | 89 | `configure_flash4` | `PROTO_FLASH_5V_PAGE`, `PROTO_PHANTOM_0x35`, `PROTO_PHANTOM_0x39` |
| `== 0x07 \|\| 0x08 \|\| 0x0B` | 94 | `configure_eprom` | `PROTO_EPROM_28PIN`, `PROTO_EPROM_32PIN`, `PROTO_EPROM_24PIN` |
| `== 0x0E \|\| 0x27 \|\| 0x28 \|\| 0x29` | 99 | `configure_sram` | `PROTO_SRAM_32PIN`, `PROTO_SRAM_24PIN`, `PROTO_SRAM_28PIN`, `PROTO_SRAM_32PIN_NVRAM` |
| `== 0x11 \|\| 0x2A \|\| 0x2B \|\| 0x2C` | 107 | `configure_not_implemented` | (no approved tokens — discretion; see note above) |
| `!= 0` (catches 0x34) | 116 | `configure_not_implemented` | (numeric literal `0`; 0x34 never named here) |

**Note:** `handle->protocol` is `uint32_t` (firestarter.h line 89). `PROTO_` defines should be plain integer literals (`0x10`, etc.) — no suffix needed; the comparison is against a `uint32_t`. The mem_type fallback (`TYPE_EPROM 1` etc., defined at memory.cpp lines 26–29) is separate and NOT part of the protocol-name relabel (those are `mem_type` values, not protocol IDs — leave as-is unless the planner chooses to name them too, which is out of FW scope).

## Handler Inventory (FW-03 rename scope) — CRITICAL: approved names == current names

`[VERIFIED: src/proms/*.cpp, include/*.h, PROTOCOLS.md handler-family table lines 49–57]`

The approved family-name layer (PROTOCOLS.md lines 49–57) names each family using the **existing** function/file names:

| Handler-family | Approved `configure_*` function | Approved file | Current function (verified) | Current file (verified) | Delta? |
|----------------|-------------------------------|---------------|----------------------------|-------------------------|--------|
| eprom | `configure_eprom()` | `eprom.cpp` | `configure_eprom` | `src/proms/eprom.cpp` + `include/eprom.h` | **NONE** |
| sram | `configure_sram()` | `sram.cpp` | `configure_sram` | `src/proms/sram.cpp` + `include/sram.h` | **NONE** |
| flash4 | `configure_flash4()` | `flash_type_4.cpp` | `configure_flash4` | `src/proms/flash_type_4.cpp` + `include/flash_type_4.h` | **NONE** |
| flash3 | `configure_flash3()` | `flash_type_3.cpp` | `configure_flash3` | `src/proms/flash_type_3.cpp` + `include/flash_type_3.h` | **NONE** |
| eeprom28c | `configure_eeprom28c()` | `eeprom_28c.cpp` | `configure_eeprom28c` | `src/proms/eeprom_28c.cpp` + `include/eeprom_28c.h` | **NONE** |
| flash_intel | `configure_flash_intel()` | `flash_intel.cpp` | `configure_flash_intel` | `src/proms/flash_intel.cpp` + `include/flash_intel.h` | **NONE** |
| not-implemented | `configure_not_implemented()` | `not_implemented.cpp` | `configure_not_implemented` | `src/proms/not_implemented.cpp` + `include/not_implemented.h` | **NONE** |

**Implication for the planner:** FW-03 as literally worded ("renamed from the approved family-name layer") produces **NO file renames and NO function renames**, because Phase 100 chose the family names to MATCH the existing code (this was deliberate — see 100-VERIFICATION.md Key-Link row: "7 groupings named ... matches the `configure_*` chain described in firestarter/CLAUDE.md"). The planner should:
1. **Verify** the current names against PROTOCOLS.md §"Handler-family layer" (confirmed identical this session).
2. If identical (they are), FW-03 is satisfied by **documenting that the handler layer already conforms** to the approved names — possibly adding a header-comment cross-reference to the `PROTO_` tokens each handler serves. Do NOT rename to something not in the approved layer.
3. If the operator/discuss-phase wants actual renames, that would REQUIRE re-opening Phase 100's approved layer — out of scope; flag it.

**Rename blast radius IF any rename is pursued** (reference counts, `grep -rn <fn> src/ include/ test/`): `configure_sram` 30 refs, `configure_eprom` 18, `configure_flash4` 15, `configure_flash3` 14, `configure_flash_intel` 13, `configure_eeprom28c` 13, `configure_not_implemented` 5. Refs span `src/proms/*.cpp`, `include/*.h`, and 7 native test files (`test/native/avr/test_val_*`, `test_dispatch`, `test_not_implemented`, `_shared/validation_matrix.h`). Plus the host-side `test_dispatch_mirror.py::DOC_FILE_TO_FUNC` map and `check_dispatch.py::dispatch()` return strings. A rename would be a large cross-repo change — another reason to confirm it is a no-op first.

## Constant Home (FW-01)

`[VERIFIED: no PROTO_ constants exist anywhere in firmware — grep -rln "PROTO_" include/ src/ returns nothing]`

**Current state:** `firestarter/include/firestarter.h` holds `CMD_*`, `RESPONSE_CODE_*`, `FLAG_*` `#define`s and the `firestarter_handle_t` struct. It has NO protocol constants — protocol values live only as raw hex literals in `memory.cpp`.

**Options:**
| Option | Pro | Con |
|--------|-----|-----|
| New header `include/proto_constants.h` | Clean separation; single grep target; matches "new constant home in `firestarter/include/`" wording in ROADMAP | One more file to `#include` in `memory.cpp` |
| Fold into `firestarter.h` | Fewer files; already included transitively everywhere | Bloats the core struct header; wider recompile |

**Recommendation:** New header `firestarter/include/proto_constants.h` (ROADMAP Depends-on line explicitly says "a new `PROTO_<NAME>` constant home in `firestarter/include/`"). Include it from `memory.cpp`. Use plain `#define PROTO_<NAME> 0x<hex>` (integer literals) so it works in both C++ (`memory.cpp`) and any `extern "C"` handler that might reference it. Guard with an include-once `#ifndef`.

**Naming caveat for the C compiler:** The phantom tokens `PROTO_PHANTOM_0x35` / `PROTO_PHANTOM_0x39` contain `0x` in the identifier — this is a **valid C identifier** (letters, digits, underscores; `0x35` here is literal text `0`,`x`,`3`,`5`, not a hex literal since it's inside an identifier that starts with `PROTO_`). `#define PROTO_PHANTOM_0x35 0x35` is legal. Verify with a trial compile — this is the one non-obvious token that could surprise. `[VERIFIED: C identifier grammar — identifier chars are [A-Za-z0-9_], leading non-digit; PROTO_PHANTOM_0x35 qualifies]`

## Guard Machinery (exact commands + green-state)

All commands verified run this session. Baseline state captured.

### 1. Firmware native test suite ("golden register traces" + dispatch tests)
`[VERIFIED: ran `pio test -e native` this session — 82 test cases, 82 succeeded in ~61s]`
```bash
cd /workspaces/firestarter
pio test -e native                          # all 14 native suites (82 cases)
pio test -e native -f "*test_dispatch*"     # just the configure_memory dispatch suite (18 cases)
```
- **Green looks like:** `================= 82 test cases: 82 succeeded ... =================`
- The "golden register traces" referenced in requirements = the **COBS frame-vector golden suite** (`test_frame_vectors`, pinned to `include/frame_vectors.h`) + the per-family validation suites (`test_val_eprom/flash3/flash4/flash_intel/sram/eeprom28c`) + the dispatch suite. **None of these assert on protocol NAMES** — they use raw hex handle values and assert `response_code`/register behavior. A pure relabel therefore should leave all 82 green with zero test edits. `[VERIFIED: read test_configure_memory.cpp — asserts make_handle(0x05,...) etc., hard-coded hex]`
- **pio available:** `/usr/local/bin/pio` v6.1.19. `[VERIFIED]`

### 2. Firmware compile (both boards)
`[VERIFIED: ran `pio run -e uno` — SUCCESS, Flash 23516 B / 72.9% of 32256]`
```bash
pio run -e uno          # Uno (512B buffer)
pio run -e leonardo     # Leonardo (1024B buffer)
```
- **Green looks like:** `[SUCCESS]`. A relabel must NOT change the flash byte count meaningfully (`#define` is compile-time; expect byte-identical or trivially different `.hex`).

### 3. check_dispatch.py (dispatch-path + safety guard, GATE-02)
`[VERIFIED: ran this session — PASS: all 746 chips scanned; 736 supported; 0 dispatch regressions]`
```bash
cd /workspaces/firestarter_app
pip install -e '.[test]'                    # once, to make `firestarter` importable
python3 tools/check_dispatch.py
```
- **Green looks like:** `PASS: all 746 chips scanned; 736 supported; ... 0 dispatch regressions; 0 consistency violations`, exit 0.
- **Note:** `check_dispatch.py::dispatch()` (lines 133–157) is a **Python mirror of the memory.cpp dispatch order** using raw hex. It is NOT auto-derived from the firmware — it is a hand-maintained twin. A pure firmware relabel does NOT require editing this file (it keeps hex), UNLESS a handler function is actually renamed (then the return strings + `test_dispatch_mirror.DOC_FILE_TO_FUNC` must change too).

### 4. diff_db.py (DB identity, GATE-02)
`[VERIFIED: ran this session — PASS: all 2 changed chips explained (0 new; 0 removed)]`
```bash
cd /workspaces/firestarter_app
python3 tools/diff_db.py
```
- **Green looks like:** `PASS: all N changed chips explained (0 new chips confirmed; 0 chips removed from baseline)`, exit 0.
- Phase 101 touches NO Python DB pipeline → this MUST stay identical (it's a firmware-only relabel + optional constants.py mirror). If diff_db drifts, something wrong happened.

### 5. Constants-parity pytest (GATE-02, `constants.py` ↔ `firestarter.h`)
`[VERIFIED: ran `pytest tests/test_revision_constants_parity.py -q` — 6 passed]`
```bash
cd /workspaces/firestarter_app
python3 -m pytest tests/test_revision_constants_parity.py -q
```
- **Green looks like:** `6 passed`.
- **CRITICAL SCOPE FINDING:** This test asserts `REVISION_*`, `COMMAND_*`, `FLAG_*`, `CTRL_*`, `CMD_FRAME_MAX`, `MAX_27C020_SIZE` against **hard-coded literals**. It does **NOT** currently assert any `PROTO_*` constants, and `constants.py` defines **ZERO** protocol constants (`grep -cn "PROTO_" firestarter/constants.py` → 0). `[VERIFIED]`
- **Implication:** If Phase 101 does NOT mirror `PROTO_` tokens into `constants.py`, the existing parity test stays green with no edit (the PROTO_ tokens are firmware-internal, never crossing the wire — the wire uses the integer `algorithm` field, not the token name). If the planner DECIDES to mirror them (for symmetry/lockstep), it must ADD a new `test_proto_values_match_firmware()` parity function + `PROTO_*` block in `constants.py`. See Open Question 1 — this is a genuine design decision, not a forced change.

### 6. Dispatch-mirror guard — ⚠ ALREADY RED ON THIS BRANCH
`[VERIFIED: ran `pytest tests/test_dispatch_mirror.py` — FAILED: parse_protocols_md() returned an empty table]`
```bash
cd /workspaces/firestarter_app
python3 -m pytest tests/test_dispatch_mirror.py -q
```
- **Current state:** **RED (pre-existing, caused by Phase 100).** `test_dispatch_mirror_doc_matches_tool` fails with `AssertionError: parse_protocols_md() returned an empty table`.
- **Root cause:** The guard's regex `_ROW_RE = r"^\|\s*0x([0-9A-Fa-f]+)\s*\|[^|]*\|\s*`([a-z0-9_]+\.cpp)`\s*\|"` expects the `.cpp` filename in **column 3** of the bucket table. Phase 100 restructured that table so column 3 is now the **frozen slug** (e.g. `0x05-FLASH-AMD-STD`), not a `.cpp` file. The `.cpp` filenames now live in a **separate** "Handler-family layer" table at PROTOCOLS.md lines 49–57 (which the regex doesn't scan because those rows start with a family name like `| eprom |`, not `| 0xNN |`). So `parse_protocols_md()` returns `{}` and the guard fails.
- **Disposition (planner MUST decide + add a task):** GATE-01 requires the dispatch-mirror guard GREEN. Options: (a) **fix the guard parser** to read the new handler-family table (map family→file→func) or the §1.x per-bucket `**Handler:**` lines; (b) re-pin the guard against the new structure with cited rationale. This is IN SCOPE for Phase 101 because GATE-01 names this guard explicitly and it cannot be left red. Recommend option (a).
- **Also failing pre-existing (UNRELATED to naming):** `test_audit_coverage_matrix.py::test_golden_file_matches` — a v1.3 coverage-matrix golden snapshot, not a naming/dispatch guard. Confirm out-of-scope; do NOT try to fix it in Phase 101 unless it blocks the pytest run (it's an independent test, so it does not block others).

### 7. Host CI gate (py3.11 target) — ruff / format / mypy / pytest
`[VERIFIED: ran ruff/format/pytest this session]`
```bash
cd /workspaces/firestarter_app
ruff check firestarter/ tests/          # CI target — VERIFIED "All checks passed!" at baseline
ruff format --check firestarter/ tests/ # VERIFIED "77 files already formatted"
python tools/check_mypy_watermark.py    # mypy gate
pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```
- **CI runs on Python 3.11** (`.github/workflows/ci.yml` line 29–32: `python-version: '3.11'`). `[VERIFIED]`
- **CI ruff target is `firestarter/ tests/`** — NOT `tools/`. `[VERIFIED: ci.yml lines 60, 63]`. The `tools/` dir has 4 pre-existing ruff errors + 3 format-dirty files (`tools/catalog/codegen_vectors.py`, `tools/check_mypy_watermark.py`), but these are **NOT in the CI target** and do not affect the gate. Phase 101 touches neither `firestarter/` nor `tests/` on the host side UNLESS it mirrors PROTO_ into `constants.py` (then `firestarter/constants.py` IS in the CI target — keep it ruff/format-clean).

## The py3.12-masks-CI-3.11 Trap (critical for host-side changes)

`[VERIFIED: local python is 3.12.13 (/usr/local/bin/python3) and 3.13; NO python3.11 on PATH; CI pins 3.11]` + `[CITED: MEMORY reference_devcontainer_py312_masks_ci_py39]`

- **The trap:** the devcontainer runs Python **3.12/3.13**; CI runs **3.11**. Validating locally can pass while CI fails, because ruff/format/mypy behavior and f-string/codegen output can differ across Python versions. Historically the traps were: f-string backslashes, non-ruff-clean codegen output, and codegen drift gates.
- **Phase 101 exposure:** LOW if firmware-only (no Python touched). MEDIUM if `constants.py` is edited (mirroring PROTO_). If host files change, the plan MUST:
  1. Run `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` — must be clean (they are at baseline; keep them so).
  2. Run the mypy watermark gate.
  3. There is **no python3.11 binary in this devcontainer** — so exact 3.11 reproduction requires either installing 3.11 (`uv`/`pyenv`) or accepting that ruff/mypy are version-stable for simple constant additions. For a plain integer-constant block in `constants.py`, cross-version risk is minimal; the real risk is only if codegen-emitted files (`messages.py`, `frame_vectors.py`) are touched — **they are NOT in Phase 101 scope.** Document this and prefer firmware-only to sidestep the trap entirely.
- **Firmware codegen drift gates** (`build.yml`): the firmware CI has drift gates for `include/messages.h` and `include/frame_vectors.h` (both codegen-emitted). Phase 101 must NOT touch these — a new `proto_constants.h` is hand-authored, not codegen-emitted, so it has no drift gate. Confirm `proto_constants.h` is added to the repo but not wired into any `--check` codegen gate.

## Project Constraints (from CLAUDE.md files)

`[VERIFIED: read /workspaces/CLAUDE.md, firestarter/CLAUDE.md, firestarter_app/CLAUDE.md]`

- **Meta-repo tracks only `.planning/`.** The firmware/host changes land INSIDE the submodules on branch `v1.19-protocol-naming-labels`; the meta-repo orchestrator owns STATE.md/ROADMAP.md + the gitlink bump separately. Do NOT bump the gitlink (PINNED). `[CITED: /workspaces/CLAUDE.md + 100-01-SUMMARY.md line 112]`
- **Serial protocol changes sync between `serial_comm.py` and `firestarter.cpp`.** Phase 101 makes NO wire change (label-is-number; the `algorithm` integer field is unchanged), so this rule is satisfied trivially — but do NOT alter the wire `algorithm` field. `[CITED: /workspaces/CLAUDE.md]`
- **Constants/flag bits duplicated between `constants.py` and `firestarter.h` — change both together.** This rule applies to values that cross the wire (FLAG_*, CMD_*, CTRL_*). The `PROTO_` tokens are firmware-internal labels for an already-existing integer; they are NOT new wire values. Whether to mirror is Open Question 1. `[CITED: /workspaces/CLAUDE.md + firestarter_app/CLAUDE.md §Constants]`
- **firmware dispatch order in `memory.cpp` is the source-of-truth; `firestarter/CLAUDE.md`'s dispatch table must match line-for-line.** `firestarter/CLAUDE.md` also has an "Algorithm Handlers" table using OLD names (`EPROM_STD`, `FLASH_AMD_STD`, etc.). 100-VERIFICATION.md line 96 explicitly notes this is deferred to Phases 101/102/103. **Phase 101 should update `firestarter/CLAUDE.md`'s dispatch/handler tables to the new PROTO_ tokens** to keep the "must match line-for-line" invariant true. Flag this as a likely in-scope doc edit. `[CITED: firestarter/CLAUDE.md]`
- **`chip_database.json` is generated — do NOT edit by hand** (GATE-02 forbids any change anyway). `[CITED: firestarter_app/CLAUDE.md]`

## Runtime State Inventory (rename/relabel phase)

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | **None.** The wire uses the integer `algorithm` field (`handle->protocol`), never a token name. No datastore keys on protocol NAMES. The `chip_database.json` stores integer `algorithm` values, unchanged by this phase. | none (GATE-02) |
| Live service config | **None.** No external service embeds protocol token names. | none |
| OS-registered state | **None.** No task-scheduler/pm2/systemd entries reference protocol names. | none |
| Secrets/env vars | **None.** No env var references a protocol token. (`FIRESTARTER_DB_FILE`, `FIRESTARTER_PINOUTS_FILE`, `FIRESTARTER_CONFIG_DIR` are paths, not names.) | none |
| Build artifacts | Firmware `.hex` (`.pio/build/uno/`, `leonardo/`) is regenerated on `pio run` — a `#define` relabel produces a byte-identical or trivially-different binary. Python `firestarter.egg-info/` regenerates on `pip install -e`. No stale artifact carries a protocol token name. | rebuild on `pio run` / reinstall — automatic, no migration |

**The canonical question — after every firmware file is relabeled, what still holds the old raw hex?** Answer: the **Python twin** (`check_dispatch.py::dispatch()`, `test_dispatch_mirror.DOC_FILE_TO_FUNC`) uses raw hex + handler-function strings; and `firestarter/CLAUDE.md`'s dispatch/handler tables use old prose names. The relabel keeps the SAME integer values, so the Python hex twins remain correct WITHOUT edit; only `firestarter/CLAUDE.md`'s prose names and the (already-red) `test_dispatch_mirror.py` parser need attention. No data migration exists — this is a code-label-only change (no code EDIT to how values are written; the values are identical).

## Common Pitfalls

### Pitfall 1: Treating FW-03 as a wholesale rename
**What goes wrong:** Planner renames `configure_eprom`→`configure_eprom_family` (or similar) across 100+ references and both repos, breaking the dispatch-mirror map and native tests.
**Why it happens:** The requirement says "renamed from the approved family-name layer," which sounds like a rename.
**How to avoid:** The approved family names ARE the current names (verified table above). FW-03 is satisfied by conformance confirmation + optional header cross-reference comments. Only rename if PROTOCOLS.md's family layer specifies a DIFFERENT name than the current code — it does not.
**Warning signs:** Any diff touching `include/*.h` function signatures, or `check_dispatch.py::dispatch()` return strings, or `test_dispatch_mirror.DOC_FILE_TO_FUNC` values.

### Pitfall 2: Forgetting the already-red dispatch-mirror guard
**What goes wrong:** Plan asserts "all guards green" but `test_dispatch_mirror.py` was already failing before Phase 101 started (Phase 100 broke its parser). GATE-01 verification fails.
**Why it happens:** Assuming a clean baseline.
**How to avoid:** Add an explicit task to reconcile `test_dispatch_mirror.py` against the new PROTOCOLS.md structure (fix `_ROW_RE`/`parse_protocols_md()` to read the handler-family table at lines 49–57 or the §1.x `**Handler:**` lines). Confirm it ends GREEN.
**Warning signs:** `parse_protocols_md() returned an empty table` in pytest output.

### Pitfall 3: Mirroring PROTO_ into constants.py without a parity test (or vice versa)
**What goes wrong:** Adding `PROTO_*` to `constants.py` but no `test_proto_values_match_firmware()` → silent drift risk; OR adding a parity test that reads the firmware header but the header path is absent in CI (`FW_ABSENT` skip).
**Why it happens:** Over-applying the "change both together" rule to a firmware-internal label.
**How to avoid:** DECIDE Open Question 1 first. If mirroring, add the `PROTO_*` block AND a `@pytest.mark.skipif(FW_ABSENT)` parity function following the existing `test_flag_values_match_firmware` pattern (hard-coded literal assertions). If NOT mirroring, document that PROTO_ tokens are firmware-internal (the wire carries the integer, not the name) and no host change is needed.
**Warning signs:** `constants.py` gains `PROTO_*` but `test_revision_constants_parity.py` count stays at 6.

### Pitfall 4: The phantom identifier `PROTO_PHANTOM_0x35` failing to compile
**What goes wrong:** Assuming `0x35` inside the identifier is parsed as a hex literal → compile error.
**Why it happens:** Visual pattern-match to hex.
**How to avoid:** It's a valid C identifier (chars `[A-Za-z0-9_]`, non-digit start). `#define PROTO_PHANTOM_0x35 0x35` compiles fine. Confirm with `pio run -e uno` after adding the header. This is the operator-approved spelling (do not "fix" it to `_35`).
**Warning signs:** N/A — verify by compiling; expected to pass.

### Pitfall 5: Changing dispatch ORDER while relabeling
**What goes wrong:** Reordering the `if` arms (e.g. alphabetizing tokens) changes first-match semantics for overlapping cases and can flip behavior.
**Why it happens:** Tidiness urge during relabel.
**How to avoid:** Preserve the EXACT line order (0x10, 0x0D, 0x06, {0x05/0x35/0x39}, {0x07/0x08/0x0B}, {0x0E/0x27/0x28/0x29}, {0x11/0x2A/0x2B/0x2C}, `!=0`, mem_type fallback). Relabel token-for-token in place. The dispatch tests + dispatch-mirror guard pin this order.

### Pitfall 6: `firestarter/CLAUDE.md` dispatch table drifting from memory.cpp
**What goes wrong:** After relabeling `memory.cpp`, the CLAUDE.md "must match line-for-line" dispatch documentation still shows raw hex / old handler-table names → doc drift.
**How to avoid:** Update `firestarter/CLAUDE.md`'s dispatch-order list and "Algorithm Handlers" table to the new tokens in the same commit (100-VERIFICATION.md flagged this as deferred to 101/102/103).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Raw hex `handle->protocol == 0x05` in dispatch | Named `handle->protocol == PROTO_FLASH_5V_PAGE` (label is the number) | Phase 101 (this phase) | Legibility only; numeric values + dispatch identical |
| Old prose handler names in CLAUDE.md (`FLASH_AMD_STD`, `EPROM_STD`) | Canonical `PROTO_` tokens + display names | Phase 100 (doc) → 101 (firmware) → 102 (host) → 103 (prose) | Vocabulary unification across firmware/host/docs |
| `.planning/research/PROTOCOLS.md` speculating 0x35="AT29C", 0x39="AT49F" | Honest phantom non-protocols (`IC2_ALG_ITE`, no constant) | Phase 86 DB regen confirmed 0 chips | Phantom tokens are honest, not real algorithms |

**Deprecated/outdated:**
- `firestarter/CLAUDE.md` "Algorithm Handlers" table names (`EPROM_STD`, `FLASH_AMD_ALT`, `FLASH_EEPROM`, etc.) — superseded by the PROTO_ tokens; update in Phase 101.
- `test_dispatch_mirror.py::_ROW_RE` regex assumes the pre-Phase-100 PROTOCOLS.md table shape — now stale/broken; fix in Phase 101.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The planner should leave 0x11/0x2A/0x2B/0x2C as raw hex (no approved tokens exist for them; introducing tokens is un-approved naming) | Approved Name Set / Dispatch Chain | LOW — REQUIREMENTS.md permits reusing §2.2 labels if needed; either way behavior is identical. Confirm with operator if tokens are desired. |
| A2 | New header `include/proto_constants.h` is the preferred constant home (vs folding into firestarter.h) | Constant Home | LOW — cosmetic; ROADMAP wording favors a new home in include/ |
| A3 | PROTO_ tokens do NOT need mirroring into `constants.py` (they're firmware-internal; the wire carries the integer `algorithm`, not the name) | Guard Machinery §5 / Open Q1 | MEDIUM — if the operator wants symmetry/lockstep, a constants.py block + new parity test is needed. This is a genuine design decision → Open Question 1. |
| A4 | `test_audit_coverage_matrix.py` failure is unrelated to naming and out of Phase 101 scope | Guard Machinery §6 | LOW — it's a v1.3 coverage-matrix golden snapshot; verify it doesn't block the pytest run (it's an independent test). |
| A5 | Reconciling the already-red `test_dispatch_mirror.py` is IN SCOPE for Phase 101 (GATE-01 names it explicitly and requires it green) | Guard Machinery §6 | MEDIUM — if treated as pre-existing-and-ignore, GATE-01 verification could be argued either way; recommend fixing it. Confirm in discuss-phase. |

## Open Questions (RESOLVED)

> All three resolved by operator decisions captured in `101-CONTEXT.md` during /gsd-plan-phase (2026-07-01). Q1→D-02, Q2→D-03, Q3→D-01.

1. **RESOLVED (→ D-02, firmware-only): Should the `PROTO_<NAME>` tokens be mirrored into `firestarter_app/firestarter/constants.py` for lockstep parity?**
   - What we know: `constants.py` currently defines ZERO protocol constants; the parity test asserts only `FLAG_*`/`CMD_*`/`CTRL_*`/`REVISION_*` (values that cross the wire). The wire carries the integer `algorithm` field, not the token name — so PROTO_ tokens are firmware-internal and do NOT strictly need a host twin. ROADMAP §Depends-on says "`constants.py` for lockstep parity" but also frames the phase as firmware-primary.
   - What's unclear: Whether the operator wants host-side PROTO_ constants for symmetry (would require a new `test_proto_values_match_firmware()` parity function), or whether host stays name-free (PROTO_ tokens are a firmware legibility layer only). Note Phase 102 will add DISPLAY names to the host (`ic_layout.py`), which is a separate concern from the C `PROTO_` tokens.
   - Recommendation: Default to **firmware-only** (no constants.py PROTO_ block) to keep the phase minimal and sidestep the py3.11 CI trap; the parity test stays green unchanged. Surface this in `/gsd-discuss-phase` for an explicit operator decision. If mirrored, follow the existing `@skipif(FW_ABSENT)` hard-literal parity pattern.

2. **RESOLVED (→ D-03, fix parser in Wave 0): Disposition of the already-red `test_dispatch_mirror.py`.**
   - What we know: It is RED at baseline due to Phase 100's PROTOCOLS.md table restructure (parser returns empty). GATE-01 requires this guard green.
   - What's unclear: Fix the parser to read the new table shape (recommended) vs. broader re-pin.
   - Recommendation: Add a task to update `parse_protocols_md()`/`_ROW_RE` to parse the handler-family table (lines 49–57) or the §1.x `**Handler:**` lines, and confirm green. Cite the Phase-100 restructure as the rationale.

3. **RESOLVED (→ D-01, conformance-confirm, no rename): Does FW-03 require ANY actual rename?**
   - What we know: Approved family names == current function/file names (verified identical).
   - What's unclear: Whether the operator intended a cosmetic conformance-confirmation or expected visible renames.
   - Recommendation: Treat FW-03 as "confirm conformance + add PROTO_-token cross-reference header comments"; do NOT rename. Confirm in discuss-phase (this materially changes the plan's task count).

## Environment Availability

`[VERIFIED: all probed this session]`

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO (`pio`) | native tests + firmware compile | ✓ | 6.1.19 (`/usr/local/bin/pio`) | — |
| Python 3 | host guards (check_dispatch, diff_db, pytest) | ✓ | 3.12.13 (`/usr/local/bin/python3`); 3.13 also present | — |
| Python 3.11 (CI target) | exact CI-parity ruff/mypy/pytest reproduction | ✗ | — | ruff/mypy are version-stable for constant additions; install via uv/pyenv only if host codegen is touched (it is not in scope) |
| ruff | host lint gate | ✓ | 0.15.20 (`~/.local/bin/ruff`) | — |
| mypy | host type gate | ✓ | 2.1.0 | — |
| `firestarter` pkg (editable) | check_dispatch/diff_db import | ✓ (after `pip install -e '.[test]'`) | v1.18 HEAD `51621bc` | — |

**Missing dependencies with no fallback:** none (firmware-only phase is fully executable here).
**Missing dependencies with fallback:** python3.11 — only matters if host codegen files change (out of scope); the constant-only host changes (if any) are cross-version-stable.

## Validation Architecture

> nyquist_validation is not explicitly false in config.json → included.

### Test Framework
| Property | Value |
|----------|-------|
| Framework (firmware) | Unity via PlatformIO `[env:native]` (`platform=native`, `test_framework=unity`) |
| Framework (host) | pytest + ruff + mypy (CI py3.11) |
| Config file | `firestarter/platformio.ini` `[env:native]` (lines 69+); `firestarter_app/pyproject.toml` + `.github/workflows/ci.yml` |
| Quick run command | `pio test -e native -f "*test_dispatch*"` (firmware) / `python3 tools/check_dispatch.py` (host) |
| Full suite command | `pio test -e native` (82 cases) + `pytest tests/ --cov-fail-under=70` (host) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FW-01 | PROTO_ constants defined, values == hex | compile + dispatch | `pio run -e uno` + `pio test -e native -f "*test_dispatch*"` | ✅ (test_configure_memory.cpp) |
| FW-02 | dispatch relabeled, order/behavior preserved | unit | `pio test -e native -f "*test_dispatch*"` (18 cases incl. phantom 0x35/0x39) | ✅ |
| FW-03 | handler families conform to approved names | grep/assert | `pytest tests/test_dispatch_mirror.py` (after parser fix) | ⚠️ exists but RED — Wave 0 fix |
| GATE-01 | dispatch key = number; guards green | integration | `pio test -e native` + `pytest tests/test_dispatch_mirror.py` | ⚠️ dispatch-mirror RED |
| GATE-02 | no DB/wire/value change | regression | `python3 tools/diff_db.py` + `python3 tools/check_dispatch.py` + `pytest tests/test_revision_constants_parity.py` | ✅ all green baseline |
| GATE-03 | CLI unchanged | n/a | (no CLI file touched — assert by diff scope) | ✅ trivial |

### Sampling Rate
- **Per task commit:** `pio test -e native -f "*test_dispatch*"` (fast, ~3s) + `pio run -e uno` (~2s).
- **Per wave merge:** `pio test -e native` (full 82, ~61s) + `python3 tools/check_dispatch.py` + `python3 tools/diff_db.py` + `pytest tests/test_dispatch_mirror.py tests/test_revision_constants_parity.py`.
- **Phase gate:** full firmware native suite green + all host guards green (including the newly-fixed dispatch-mirror) + `pio run -e uno && pio run -e leonardo` + host CI clean (`ruff check firestarter/ tests/`, `ruff format --check`, mypy, pytest --cov-fail-under=70).

### Wave 0 Gaps
- [ ] Fix `firestarter_app/tests/test_dispatch_mirror.py` parser (`_ROW_RE`/`parse_protocols_md`) to read the post-Phase-100 PROTOCOLS.md table structure — it is RED at baseline and blocks GATE-01. This is the ONE test-infra gap that must be closed before/within the phase.
- No new test files required for FW-01/FW-02 — the existing `test_configure_memory.cpp` (hard-coded hex handles) already pins dispatch and stays green through a relabel.

*(Framework install: none needed — pio + pytest + ruff + mypy all present.)*

## Security Domain

> `security_enforcement` not set false in config → included, scoped to this phase.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | firmware relabel; no auth surface |
| V3 Session Management | no | n/a |
| V4 Access Control | no | n/a |
| V5 Input Validation | no (unchanged) | wire `algorithm` integer parsing in `json_parser.c` is untouched; no new input path |
| V6 Cryptography | no | CRC8 frame integrity (`test_messages`) is untouched by a relabel |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Dispatch-order regression enabling 12V VPP on a 5V SRAM part (BLOCKER-2) | Tampering/Denial | `check_dispatch.py` SRAM-never-eprom guard + native `test_val_sram` — MUST stay green; relabel must not reorder arms |
| Fail-closed dispatch bypass (unknown protocol reaching mem_type 12V fallback) | Elevation | `protocol != 0 → configure_not_implemented` guard (memory.cpp line 116) — preserve exactly; `test_not_implemented` pins it |
| Silent behavior change hidden behind a "cosmetic" relabel | Tampering | golden frame-vectors + 82-case native suite + byte-count check on `pio run` |

**Phase-101-specific security note:** The ONLY security-relevant risk is a dispatch-order or value change masquerading as a relabel. The `PROTO_<NAME>` value MUST equal the hex it replaces (compile-time enforced by the tests that use hex handle values). No new attack surface is introduced.

## Sources

### Primary (HIGH confidence — read/run this session)
- `firestarter/doc/PROTOCOLS.md` @ `6e7bd38` — the operator-approved name set (§bucket table lines 30–45, handler-family lines 49–57, phantom §2.1)
- `firestarter/src/proms/memory.cpp` lines 46–137 — ground-truth dispatch chain
- `firestarter/include/firestarter.h` — current constants home (no PROTO_ present)
- `firestarter/include/{eprom,sram,flash_type_3,flash_type_4,eeprom_28c,flash_intel,not_implemented,memory}.h` — handler function signatures
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — dispatch tests (hard-coded hex)
- `firestarter_app/tools/check_dispatch.py`, `tools/diff_db.py` — GATE-02 guards (ran green)
- `firestarter_app/tests/test_dispatch_mirror.py` — dispatch-mirror guard (ran RED — baseline breakage identified)
- `firestarter_app/tests/test_revision_constants_parity.py` — constants-parity gate (ran 6-passed; no PROTO_ coverage)
- `.planning/phases/100-*/100-01-SUMMARY.md`, `100-VERIFICATION.md` — Phase 100 contract + phantom/0x34/0x29 decisions
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` Phase 101 — locked constraints
- `/workspaces/CLAUDE.md`, `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md` — project rules
- Ran: `pio test -e native` (82/82), `pio run -e uno` (SUCCESS), `check_dispatch.py` (PASS 746), `diff_db.py` (PASS), `ruff check firestarter/ tests/` (clean), parity pytest (6 passed)

### Secondary (MEDIUM confidence)
- `firestarter/.github/workflows/build.yml`, `firestarter_app/.github/workflows/ci.yml` — CI gate composition + py3.11 pin (read, not executed in CI)

### Tertiary (LOW confidence)
- MEMORY `reference_devcontainer_py312_masks_ci_py39` — the py3.12-masks-CI trap (project memory, corroborated by observed 3.12/3.13-only environment)

## Metadata

**Confidence breakdown:**
- Approved name set: HIGH — extracted verbatim from committed PROTOCOLS.md
- Dispatch chain: HIGH — quoted directly from memory.cpp
- Handler inventory / FW-03 no-op finding: HIGH — cross-checked doc family layer against actual file/function names
- Guard machinery + baseline state: HIGH — every command run this session, green/red observed
- constants.py mirroring decision: MEDIUM — a genuine open design question (Open Q1)
- dispatch-mirror reconciliation scope: MEDIUM — GATE-01 implies in-scope; confirm in discuss-phase

**Research date:** 2026-07-01
**Valid until:** 2026-07-31 (stable domain; the only volatility is if PROTOCOLS.md or memory.cpp changes before planning — re-verify the two tables if either commit moves)
