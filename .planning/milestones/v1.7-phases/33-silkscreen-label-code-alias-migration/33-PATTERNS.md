# Phase 33: Silkscreen Label → Code Alias Migration — Pattern Map

**Mapped:** 2026-05-25
**Files analyzed:** 16 (1 NEW header + 12 firmware modifications + 1 firmware test + 2 host modifications + 1 meta-repo doc fill + 1 NEW wave-0 tooling dir)
**Analogs found:** 16 / 16

Phase 33 is structurally a **mechanical macro rename across firmware + Python host + a meta-repo §7 doc fill**, gated by GATE-1.7 `.hex` byte-identical (`cmp` exit 0 on all 3 AVR envs modulo ≤ ~50 B). Every pattern needed has already shipped in the codebase — this map points each planned file at the exact in-tree analog (line ranges + concrete excerpts) to copy from.

The structural precedent for the entire phase is **Phase 9** (`.planning/phases/09-delete-old-log-macros-measure-flash-savings/`) — it proved AVR-flash-byte-identical macro rename + cross-file sweep is mechanically sound on this codebase. Phase 33 reuses Phase 9's pattern: subsystem-split waves, per-wave verifier (build + cmp + native test), pre/post `.hex` measurement artifact.

---

## File Classification

| New/Modified File | Role | Data Flow | Touch Kind | Closest Analog | Match Quality |
|-------------------|------|-----------|------------|----------------|---------------|
| `firestarter/include/rurp_pinout.h` | firmware header (macro substrate) | n/a | CREATE | `firestarter/include/rurp_shield.h:21-89` (hosts the macros today; new header carves them out verbatim into a dedicated TU) | exact — same `#define` style, same `#ifdef HARDWARE_REVISION` gating, same per-rev REV_* variant block |
| `firestarter/include/rurp_shield.h` | firmware header (decls + latch selectors) | n/a | DELETE-LINES + ADD-INCLUDE | Phase 9 `firestarter/include/rurp_shield.h` (Phase 9 also deleted lines from this header while leaving live decls intact) | exact — same surgical-deletion pattern: drop the `#define VPE_TO_VPP …` block at `:25-94`, keep `CONFIG_VERSION`, `LEAST_SIGNIFICANT_BYTE`, function prototypes; add `#include "rurp_pinout.h"` at `:20` |
| `firestarter/include/rurp_hw_rev_utils.h` | firmware header (dispatcher inline) | request-response | MODIFY-IN-PLACE (textual rename only) | Same file: function body at `:13-35` — only macro identifiers change; `switch`/`case`/dispatcher shape preserved verbatim | exact — Pattern 3 from RESEARCH.md |
| `firestarter/include/rurp_register_utils.h` | firmware header (register write) | request-response | MODIFY-IN-PLACE (2-line rename) | Same file: settle-check at `:42` references `P1_VPP_ENABLE`; `case CONTROL_REGISTER` at `:38` | exact — single-symbol rename, no logic change |
| `firestarter/src/proms/eprom.cpp` | firmware service (UV-EPROM handler) | request-response | MODIFY-IN-PLACE (22 lines rename) | Same file: `eprom_write_init` at `:143-149` is the canonical `REGULATOR \| VPE_TO_VPP` pattern (see Pattern Assignment §1) | exact — biggest call-site cluster; same idiom repeats 22 times |
| `firestarter/src/proms/flash_intel.cpp` | firmware service (Intel-flash handler) | request-response | MODIFY-IN-PLACE (7 lines rename) | Same file: `flash_intel_write_init` at `:105-114` — canonical `REGULATOR \| P1_VPP_ENABLE` pattern | exact |
| `firestarter/src/proms/memory.cpp` | firmware service (top-level dispatch) | request-response | MODIFY-IN-PLACE (6 lines rename + comment refresh) | Same file: bit-mask math at `:139-144` (load-bearing `ADDRESS_LINE_16 == VPE_TO_VPP` comment — Pitfall 1) | exact |
| `firestarter/src/proms/flash_type_4.cpp` | firmware service (page-write flash) | request-response | MODIFY-IN-PLACE (3 lines rename) | Same file: `:108, :116, :132` — `REGULATOR \| VPE_TO_VPP \| VPE_ENABLE` triplet pattern | exact |
| `firestarter/src/proms/eeprom_28c.cpp` | firmware service (AT28C handler) | request-response | MODIFY-IN-PLACE (3 lines rename) | Same file: `eeprom28c_*` calls at `:70, :72, :77` — same `REGULATOR \| A9_VPP_ENABLE` pattern as `eprom.cpp:200-204` | exact |
| `firestarter/src/proms/flash_utils.cpp` | firmware utility (R/W toggle) | request-response | MODIFY-IN-PLACE (3 lines rename) | Same file: `READ_WRITE` toggle at `:21, :25, :30` — narrow rename, single bit | exact |
| `firestarter/src/proms/sram.cpp` | firmware service (SRAM handler) | request-response | MODIFY-IN-PLACE (per RESEARCH §1 0-3 lines if any) | `firestarter/src/proms/eeprom_28c.cpp` (same 5V-only handler shape — no VPP regulator engagement) | role-match (sram.cpp grep returned 0 hits in confirmed run; included only if CONTEXT.md handoff list is correct — see Notes) |
| `firestarter/src/hardware_operations.cpp` | firmware service (`hw_read_voltage`) | request-response | MODIFY-IN-PLACE (2 lines rename) | Same file: `:27, :30` — VPP-vs-VPE selection via `REGULATOR \| VPE_TO_VPP` (line :27) and `REGULATOR` alone (line :30) | exact |
| `firestarter/src/boards/uno_rurp_shield.cpp` | firmware board adapter (comment-only) | n/a | MODIFY-IN-PLACE (1 comment line) | Same file: `:29` — historical comment referencing `READ_WRITE` (per RESEARCH Open Question #4, recommended to refresh) | exact |
| `firestarter/src/boards/leonardo_rurp_shield.cpp` | firmware board adapter | n/a | NO-OP for control-reg names; per CONTEXT scope, only `VOLTAGE_MEASURE_PIN`-style if present | `firestarter/src/boards/uno_rurp_shield.cpp` (same role; board-pair) | role-match |
| `firestarter/src/boards/rurp_common.cpp` | firmware board common (ADC read) | request-response | MODIFY-IN-PLACE (1 line rename) | Same file: `:58` — `analogRead(VOLTAGE_MEASURE_PIN)` → `analogRead(PIN_VPP_VOLTAGE_ADC)` | exact |
| `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` | firmware native test | event-driven (test harness) | MODIFY-IN-PLACE (7 lines rename) | Same file: mock + assertions at `:43-48, :172-188` — references `P1_VPP_ENABLE`; rename to `CTRL_VPP_P1_ENABLE` | exact (Pitfall 6 — DO NOT skip this file in the sweep) |
| `firestarter_app/firestarter/constants.py` | host CLI constants (Python mirror) | n/a | ADD-BLOCK (9 new constants) | Same file: existing `# Control Flags` block at `:60-69` (`FLAG_FORCE = 0x01` etc.) is the canonical "Python-mirror-of-C++-#defines" layout | exact — same idiom: section comment header + one constant per bit + hex literals |
| `firestarter_app/firestarter/main.py` | host CLI controller (argparse) | request-response | MODIFY-IN-PLACE (9 docstring lines + 1 link line) | Same file: `:404-416` — current docstring with old names is the analog for the refreshed version | exact — textual refresh inside the `argparse` `help=` string |
| `.planning/v1.7-SHIELD-REVS.md` §7 | meta-repo documentation (canonical table) | n/a | FILL-IN-PLACE (replace `<!-- OWNED BY PHASE 33 — TBD -->` with 16-row table) | Same file: §1 inventory table at `:16-25` (8 rows × 9 columns) AND §6 capability matrix at `:82-91` (8 rows × 9 columns) | exact — both §1 and §6 are 9-column shield-rev tables; §7 reuses the same Markdown column conventions, footnote style, source-citation column pattern |
| `.planning/v1.7/phase-33-baseline-hex/` | meta-repo tooling (gitignored artifact dir) | file-I/O | CREATE-DIR + place 3 `.hex` snapshots | `.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md` precedent for pre/post-firmware measurement capture | role-match — same "snapshot binary artifact before mutating source" wave-0 pattern |
| (NEW Wave 0) `firestarter/tools/check_migration.sh` or `.planning/tools/check_alias_migration.sh` | tooling script | file-I/O | CREATE | `firestarter_app/tools/check_dispatch.py` (existing dispatch-table regression guard) | role-match — same "wrap grep + assertion in a shell/python verifier" idiom |

---

## Pattern Assignments

### 1. `firestarter/include/rurp_pinout.h` (NEW canonical alias header)

**Role:** firmware header (macro substrate) · **Data Flow:** n/a · **Touch:** CREATE

**Analog:** `firestarter/include/rurp_shield.h:21-89` — the existing file IS the macro substrate; Phase 33 carves it out verbatim into a dedicated TU.

**Header guard + extern "C" pattern** (`rurp_shield.h:8-13, 190-194`):
```c
#ifndef __RURP_SHIELD_H__
#define __RURP_SHIELD_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
// … body …

#ifdef __cplusplus
}
#endif

#endif // __RURP_SHIELD_H__
```
Phase 33 copies this exact shape: `#ifndef __RURP_PINOUT_H__` / `#define __RURP_PINOUT_H__` / matching `extern "C"` block / closing `#endif // __RURP_PINOUT_H__`.

**Macro substrate pattern (carved verbatim from `rurp_shield.h:21-53`):**
```c
#define VOLTAGE_MEASURE_PIN A2

    // CONTROL REGISTER
#ifndef HARDWARE_REVISION
#define VPE_TO_VPP      0x01
#define ADDRESS_LINE_16             VPE_TO_VPP
#define A9_VPP_ENABLE   0x02
#define VPE_ENABLE      0x04
#define P1_VPP_ENABLE   0x08
#define ADDRESS_LINE_17             0x10
#define ADDRESS_LINE_18             0x20
#define READ_WRITE      0x40
#define REGULATOR       0x80

#else
#define HARDWARE_REVISION_PIN A3
#define REVISION_0 0
// … REVISION_2_0, REVISION_2_1, REVISION_2_2 …

#define ADDRESS_LINE_16             0x01
// … (per-rev wide layout) …
#define VPE_TO_VPP      0x100
#endif
```

After Phase 33 the SAME shape appears in `rurp_pinout.h` with the new identifier names (`CTRL_VPP_VPE_DROP_ENABLE`, `CTRL_ADDRESS_LINE_16`, `PIN_VPP_VOLTAGE_ADC`, `PIN_HW_REVISION_DETECT_ADC`, …) and the SAME hex values + SAME `#ifndef HARDWARE_REVISION` / `#else` / `#endif` gating + SAME `#define CTRL_ADDRESS_LINE_16 CTRL_VPP_VPE_DROP_ENABLE` aliasing in the legacy branch (Pitfall 1).

**REV_* per-rev variant pattern (carved from `rurp_shield.h:70-89`):**
```c
#ifdef HARDWARE_REVISION
// REV 1
#define REV_1_VPE_TO_VPP      0x01
#define REV_1_A9_VPP_ENABLE   0x02
// …
#define REV_1_ADDRESS_LINE_16             REV_1_VPE_TO_VPP

// REV 2
#define REV_2_VPE_TO_VPP      0x01
// …
#define REV_2_ADDRESS_LINE_16             0x20
#define REV_2_RW              0x40
#define REV_2_ADDRESS_LINE_18             P1_VPP_ENABLE
#endif
```
Renamed verbatim to `CTRL_VPP_VPE_DROP_ENABLE_REV1`, `CTRL_VPP_VPE_DROP_ENABLE_REV2`, `CTRL_ADDRESS_LINE_16_REV1`, `CTRL_ADDRESS_LINE_16_REV2`, etc. (suffix family per RESEARCH "State of the Art" deprecation table).

**Critical preservation (Pitfalls 1 + 2):** the legacy `#define ADDRESS_LINE_16 VPE_TO_VPP` aliasing at `:26` MUST become `#define CTRL_ADDRESS_LINE_16 CTRL_VPP_VPE_DROP_ENABLE` (macro-alias-as-macro, not duplicate hex). The HARDWARE_REVISION-gated value mapping `VPE_TO_VPP 0x100` MUST stay inside the `#else` branch.

---

### 2. `firestarter/include/rurp_shield.h` (DELETE-LINES + ADD-INCLUDE)

**Role:** firmware header · **Data Flow:** n/a · **Touch:** DELETE-LINES (`:21-94`) + ADD-INCLUDE (after `:19`)

**Analog:** Phase 9 `rurp_shield.h` (deleted the two legacy text-prefix log declarations while keeping `rurp_log_id` decls — see `09-PATTERNS.md:19`). Same surgical-deletion pattern.

**Lines to delete** (current state — to be removed entirely after `rurp_pinout.h` exists):
```c
// rurp_shield.h:21-89 — DELETE
#define VOLTAGE_MEASURE_PIN A2

#ifndef HARDWARE_REVISION
#define VPE_TO_VPP      0x01
// … 8 lines …
#define REGULATOR       0x80
#else
#define HARDWARE_REVISION_PIN A3
// … 5 REVISION_* enum lines …
// … 9 bit-position lines …
#endif

#define ADDRESS_LINE_13             0x20
#define VPP_P1_32_DIP               0x15
// … VPP_P1_28_DIP, VPP_P21_24_DIP …

#ifdef HARDWARE_REVISION
// REV_1_* and REV_2_* blocks (lines 72-93)
#endif
```

**Lines to keep** (everything outside `:21-94`):
- `:1-19` — file header, header guard, includes
- `:97-109` — `CONFIG_VERSION "VER06"`, `VALUE_R1`, `VALUE_R2`, `LEAST_SIGNIFICANT_BYTE`, `MOST_SIGNIFICANT_BYTE`, `OUTPUT_ENABLE`, `CONTROL_REGISTER`, `CHIP_ENABLE` (74HC573 latch selectors — different semantic layer, NOT migrated per Anti-Pattern bullet in RESEARCH)
- `:111-194` — all function prototypes, `rurp_chip_enable`/`rurp_chip_output` macro pair, header guard close

**New include line** (insert after `:19` `#include "rurp_types.h"`):
```c
#include "rurp_types.h"
#include "rurp_pinout.h"   // Phase 33 — canonical alias substrate
```

---

### 3. `firestarter/include/rurp_hw_rev_utils.h` (DISPATCHER textual rename only)

**Role:** firmware header (inline dispatcher) · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (10 macro identifier renames inside function body)

**Analog:** Same file — function body at `:13-35` is its own analog. Pattern 3 from RESEARCH: function signature, `switch` shape, case-fallthrough on Rev 2.0/2.1/2.2, `REVISION_*` enum constants, `default: break` — all preserved verbatim.

**Current state** (`rurp_hw_rev_utils.h:13-35`):
```c
uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    uint8_t ctrl_reg = 0;
    uint8_t hw = rurp_get_hardware_revision();
    switch (hw) {
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2:
        ctrl_reg = data & (A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | ADDRESS_LINE_17 | READ_WRITE | REGULATOR);
        ctrl_reg |= data & VPE_TO_VPP ? REV_2_VPE_TO_VPP : 0;
        ctrl_reg |= data & ADDRESS_LINE_16 ? REV_2_ADDRESS_LINE_16 : 0;
        ctrl_reg |= data & ADDRESS_LINE_18 ? REV_2_ADDRESS_LINE_18 : 0;
        break;
    case REVISION_0:
    case REVISION_1:
        ctrl_reg = data;
        ctrl_reg |= data & VPE_TO_VPP ? REV_1_VPE_TO_VPP : 0;
        break;
    default:
        break;
    }
    return ctrl_reg;
}
```

**Target after rename** (textual substitution only):
```c
uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    uint8_t ctrl_reg = 0;
    uint8_t hw = rurp_get_hardware_revision();
    switch (hw) {
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2:
        ctrl_reg = data & (CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_ADDRESS_LINE_17 | CTRL_READ_WRITE | CTRL_VPP_REGULATOR_ENABLE);
        ctrl_reg |= data & CTRL_VPP_VPE_DROP_ENABLE ? CTRL_VPP_VPE_DROP_ENABLE_REV2 : 0;
        ctrl_reg |= data & CTRL_ADDRESS_LINE_16 ? CTRL_ADDRESS_LINE_16_REV2 : 0;
        ctrl_reg |= data & CTRL_ADDRESS_LINE_18 ? CTRL_ADDRESS_LINE_18_REV2 : 0;
        break;
    case REVISION_0:
    case REVISION_1:
        ctrl_reg = data;
        ctrl_reg |= data & CTRL_VPP_VPE_DROP_ENABLE ? CTRL_VPP_VPE_DROP_ENABLE_REV1 : 0;
        break;
    default:
        break;
    }
    return ctrl_reg;
}
```

**Critical (Pitfall 3):** the LHS canonical input mask AND the RHS per-rev output names BOTH rename. `git grep "REV_[12]_" firestarter/` must return 0 hits after the sweep. `REVISION_0` / `REVISION_1` / `REVISION_2_*` enum values stay (D-03 — out of alias-scope).

**Function `rurp_detect_hardware_revision()` at `:41-58`** references `HARDWARE_REVISION_PIN` (line `:42, :45`) + `VOLTAGE_MEASURE_PIN` (line `:43, :48, :57`). Rename to `PIN_HW_REVISION_DETECT_ADC` + `PIN_VPP_VOLTAGE_ADC`. Function body otherwise unchanged.

---

### 4. `firestarter/include/rurp_register_utils.h` (settle-check rename)

**Role:** firmware header (inline register write) · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (2-line rename)

**Analog:** Same file — `case CONTROL_REGISTER` block at `:38-49` is its own analog.

**Current state** (`rurp_register_utils.h:38-49`):
```c
    case CONTROL_REGISTER:
        if (control_register == data) {
            return;
        }
        if ((control_register & P1_VPP_ENABLE) > (data & P1_VPP_ENABLE)) {
            settle = true;
        }
        control_register = data;
#ifdef HARDWARE_REVISION
        data = rurp_map_ctrl_reg_for_hardware_revision(data);
#endif
        break;
```

**Target after rename:**
```c
    case CONTROL_REGISTER:                              // unchanged (latch selector, not a Phase 33 alias)
        if (control_register == data) {
            return;
        }
        if ((control_register & CTRL_VPP_P1_ENABLE) > (data & CTRL_VPP_P1_ENABLE)) {   // P1_VPP_ENABLE → CTRL_VPP_P1_ENABLE
            settle = true;
        }
        control_register = data;
#ifdef HARDWARE_REVISION
        data = rurp_map_ctrl_reg_for_hardware_revision(data);  // unchanged
#endif
        break;
```

**Preservation:** `CONTROL_REGISTER` (74HC573 latch selector at `rurp_shield.h:103`) is NOT renamed — different semantic layer per Anti-Pattern bullet.

---

### 5. `firestarter/src/proms/eprom.cpp` (22-line call-site cluster)

**Role:** firmware service (UV-EPROM handler — algorithms 0x07, 0x08, 0x0B) · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (22 lines rename)

**Analog:** Same file — `eprom_write_init` at `:143-149` is the canonical 6-line `REGULATOR \| VPE_TO_VPP` pattern that repeats throughout the file.

**Current call-site shape** (`eprom.cpp:143-149`):
```cpp
if (handle->firestarter_get_control_register(handle, REGULATOR) == 0) {
    if (handle->protocol == FLASH_LEGACY) {
        // EPROM_LEGACY: direct VPE path — no VPE_TO_VPP dropping resistor
        handle->firestarter_set_control_register(handle, REGULATOR, 1);
    } else {
        // EPROM_STD / EPROM_QUICK: VPE_TO_VPP dropping path for precise VPP
        handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP, 1);
    }
}
```

**Target after rename:**
```cpp
if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0) {
    if (handle->protocol == FLASH_LEGACY) {
        // EPROM_LEGACY: direct VPE path — no CTRL_VPP_VPE_DROP_ENABLE dropping resistor
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
    } else {
        // EPROM_STD / EPROM_QUICK: CTRL_VPP_VPE_DROP_ENABLE dropping path for precise VPP
        handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1);
    }
}
```

**Other call-site clusters in this file (auditied via grep — all share the same idiom):**
| Line | Pattern | Rename |
|------|---------|--------|
| `:114` | `rurp_register_t programming_bits = VPE_ENABLE;` | `… = CTRL_VPE_ENABLE;` |
| `:180` | `… REGULATOR, 0);` | `… CTRL_VPP_REGULATOR_ENABLE, 0);` |
| `:197` | `… REGULATOR, 1);` | same |
| `:200` | `… A9_VPP_ENABLE, 1);` | `… CTRL_VPP_A9_ENABLE, 1);` |
| `:204` | `… REGULATOR \| A9_VPP_ENABLE, 0);` | combined rename |
| `:219, :222` | `REGULATOR` / `REGULATOR \| VPE_TO_VPP` | combined rename |
| `:270` | `… REGULATOR \| VPE_TO_VPP, 0);` | combined rename |
| `:276` | `… REGULATOR, 1);  // Enable regulator without dropping resistor` | rename + comment refresh |
| `:279` | `… A9_VPP_ENABLE \| VPE_ENABLE, 1);  // … assumes VPE_TO_VPP isn't set …` | rename + comment refresh |
| `:286` | `… REGULATOR \| A9_VPP_ENABLE \| VPE_ENABLE, 0);` | combined rename |
| `:317-321` | `using_p1_as_vpp` helper — VPE_ENABLE → P1_VPP_ENABLE redirect | rename both sides; pattern preserved |
| `:327-328` | `REGULATOR` get + set | combined rename |

---

### 6. `firestarter/src/proms/flash_intel.cpp` (7 lines — Intel-flash)

**Role:** firmware service (Intel 28F flash, algorithm 0x10) · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (7 lines rename)

**Analog:** Same file — `flash_intel_write_init` at `:105-114` is the canonical `REGULATOR | P1_VPP_ENABLE` pattern (SAF-04 safety guard) that repeats through the file.

**Canonical call-site pattern** (`flash_intel.cpp:105-114`):
```cpp
void flash_intel_write_init(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 1);
    delay(500);
    flash_intel_check_vpp(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        // Safety: clear VPP regulator before early-return so 12V is not left
        // applied to socket pin 1 after an unsafe-voltage detection.
        handle->firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 0);
        return;
    }
    …
}
```

**Target after rename:** every `REGULATOR | P1_VPP_ENABLE` → `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_P1_ENABLE`. Comments at `:34, :80` ("Caller already asserted REGULATOR | P1_VPP_ENABLE") are refreshed to new names per Open Question #4 recommendation.

**Other lines in this file:** `:106, :114, :120, :145, :157` (all the same pattern).

---

### 7. `firestarter/src/proms/memory.cpp` (top-level dispatch + mask math)

**Role:** firmware service (top-level dispatch + bus_config bit-mask math) · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (6 lines rename + comment refresh)

**Analog:** Same file — bit-mask math at `:139-144` (load-bearing comment about `ADDRESS_LINE_16 == VPE_TO_VPP` aliasing — Pitfall 1).

**Current state** (`memory.cpp:139-144`):
```cpp
rurp_register_t top_address = ((uint32_t)address >> 16) & (ADDRESS_LINE_16 | ADDRESS_LINE_17 | ADDRESS_LINE_18 | READ_WRITE);
rurp_register_t mask = A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | REGULATOR;
// …
    // VPE_TO_VPP and ADDRESS_LINE_16 share the same CONTROL bit — preserving VPE_TO_VPP
    // would corrupt A16 for 32-pin (512KB) chips. DIP32 chips use P1_VPP_ENABLE instead.
    mask |= VPE_TO_VPP;
```

**Target after rename:**
```cpp
rurp_register_t top_address = ((uint32_t)address >> 16) & (CTRL_ADDRESS_LINE_16 | CTRL_ADDRESS_LINE_17 | CTRL_ADDRESS_LINE_18 | CTRL_READ_WRITE);
rurp_register_t mask = CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_VPP_REGULATOR_ENABLE;
// …
    // CTRL_VPP_VPE_DROP_ENABLE and CTRL_ADDRESS_LINE_16 share the same CONTROL bit —
    // preserving CTRL_VPP_VPE_DROP_ENABLE would corrupt A16 for 32-pin (512KB) chips.
    // DIP32 chips use CTRL_VPP_P1_ENABLE instead.
    mask |= CTRL_VPP_VPE_DROP_ENABLE;
```

**Critical:** the comment at `:142-143` is load-bearing documentation of the aliasing semantics — the comment text refresh matters as much as the code rename.

---

### 8. `firestarter/src/proms/flash_type_4.cpp` (3 lines — page-write flash)

**Role:** firmware service (algorithms 0x05, 0x35, 0x39) · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (3 lines)

**Analog:** Same file — `:108, :116, :132` all share the `REGULATOR | VPE_TO_VPP | VPE_ENABLE` triplet idiom.

**Current call-site** (`flash_type_4.cpp:108`):
```cpp
handle->firestarter_set_control_register(handle, REGULATOR | VPE_TO_VPP | VPE_ENABLE, 0);
```

**Target after rename:**
```cpp
handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE, 0);
```

Apply identically to `:116` (state=1) and `:132` (state=0).

---

### 9. `firestarter/src/proms/eeprom_28c.cpp` (3 lines — AT28C handler)

**Role:** firmware service (algorithm 0x0D — AT28C-series 5V EEPROM) · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (3 lines)

**Analog:** Same file — `:70, :72, :77` share the same `REGULATOR` / `A9_VPP_ENABLE` chip-ID-read idiom that also appears in `eprom.cpp:197-204`.

**Current call-sites** (`eeprom_28c.cpp:66, :72, :77`):
```cpp
handle->firestarter_set_control_register(handle, REGULATOR, 1);
handle->firestarter_set_control_register(handle, A9_VPP_ENABLE, 1);
// …
handle->firestarter_set_control_register(handle, REGULATOR | A9_VPP_ENABLE, 0);
```

**Target after rename:**
```cpp
handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
handle->firestarter_set_control_register(handle, CTRL_VPP_A9_ENABLE, 1);
// …
handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE, 0);
```

---

### 10. `firestarter/src/proms/flash_utils.cpp` (3 lines — READ_WRITE toggle)

**Role:** firmware utility (R/W bit toggle) · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (3 lines)

**Analog:** Same file — `:21, :25, :30` all share the bare `READ_WRITE` single-bit toggle pattern.

**Current call-sites:**
```cpp
handle->firestarter_set_control_register(handle, READ_WRITE, 0);   // :21
handle->firestarter_set_control_register(handle, READ_WRITE, 0);   // :25
handle->firestarter_set_control_register(handle, READ_WRITE, 1);   // :30
```

**Target:** `READ_WRITE` → `CTRL_READ_WRITE` everywhere.

---

### 11. `firestarter/src/hardware_operations.cpp` (`hw_read_voltage` VPP/VPE selection)

**Role:** firmware service (`READ_VPP` / `READ_VPE` device commands) · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (2 lines rename)

**Analog:** Same file — `:25-30` is the canonical VPP-vs-VPE branch:

**Current state** (`hardware_operations.cpp:25-30`):
```cpp
if (handle->cmd == CMD_READ_VPP) {
    LOG_DEBUG_ID_SUB(DBG_SETTING_UP_VPP);
    rurp_write_to_register(CONTROL_REGISTER, REGULATOR | VPE_TO_VPP);
} else if (handle->cmd == CMD_READ_VPE) {
    LOG_DEBUG_ID_SUB(DBG_SETTING_UP_VPE);
    rurp_write_to_register(CONTROL_REGISTER, REGULATOR);
```

**Target after rename:**
```cpp
if (handle->cmd == CMD_READ_VPP) {
    LOG_DEBUG_ID_SUB(DBG_SETTING_UP_VPP);
    rurp_write_to_register(CONTROL_REGISTER, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE);
} else if (handle->cmd == CMD_READ_VPE) {
    LOG_DEBUG_ID_SUB(DBG_SETTING_UP_VPE);
    rurp_write_to_register(CONTROL_REGISTER, CTRL_VPP_REGULATOR_ENABLE);
```

`CONTROL_REGISTER` stays (latch selector, not a Phase 33 alias).

---

### 12. `firestarter/src/boards/rurp_common.cpp` (ADC read)

**Role:** firmware board common (analog read of voltage divider) · **Data Flow:** request-response · **Touch:** MODIFY-IN-PLACE (1 line)

**Analog:** Same file — `:58`:

**Current:** `uint32_t voltage_adc_reading = analogRead(VOLTAGE_MEASURE_PIN);`

**Target:** `uint32_t voltage_adc_reading = analogRead(PIN_VPP_VOLTAGE_ADC);`

---

### 13. `firestarter/src/boards/uno_rurp_shield.cpp` (comment refresh)

**Role:** firmware board adapter · **Data Flow:** n/a (comment only) · **Touch:** MODIFY-IN-PLACE (1 comment line — per Open Question #4)

**Analog:** Same file — `:29`:

**Current:** `// NOTE: The original code included \`READ_WRITE\` (0x40), which would attempt to control PB6.`

**Target:** `// NOTE: The original code included \`CTRL_READ_WRITE\` (0x40), which would attempt to control PB6.`

Per Open Question #4 recommendation: refresh comments using old names so future grep for `READ_WRITE` does not surface only historical comments.

---

### 14. `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` (7 lines)

**Role:** firmware native test (Unity) · **Data Flow:** event-driven (test harness) · **Touch:** MODIFY-IN-PLACE (7 lines rename — Pitfall 6, native build path does NOT set `-D HARDWARE_REVISION`)

**Analog:** Same file — `:43-48` is the canonical mock-recorder pattern; `:172-188` is the SAF-04 regression assertion block.

**Current state** (`test_flash_intel_vpp.cpp:43-48`):
```cpp
static void mock_set_ctrl_reg(struct firestarter_handle*, rurp_register_t reg, bool state) {
    s_last_ctrl_reg = reg;
    s_last_ctrl_state = state;
    if ((reg & P1_VPP_ENABLE) && state == false) {
        s_ctrl_writes_with_p1_low++;
    }
}
```

And at `:186-187`:
```cpp
TEST_ASSERT_BITS_HIGH(P1_VPP_ENABLE, s_last_ctrl_reg);
TEST_ASSERT_FALSE_MESSAGE(s_last_ctrl_state,
    "SAF-04: final control-register write must drive regulator low after VPP error");
```

**Target after rename:** `P1_VPP_ENABLE` → `CTRL_VPP_P1_ENABLE` everywhere; `REGULATOR` (if it appears anywhere — check `:170, :184, :186` per RESEARCH inventory) → `CTRL_VPP_REGULATOR_ENABLE`. Comments referencing old names also refreshed.

**Verification:** `cd firestarter && pio test -e native` must pass post-rename. This is the test the legacy-path aliasing (Pitfall 1) most likely surfaces in — the native build does NOT set `-D HARDWARE_REVISION`.

---

### 15. `firestarter_app/firestarter/constants.py` (ADD-BLOCK)

**Role:** host CLI constants module · **Data Flow:** n/a (documentary mirror) · **Touch:** ADD-BLOCK (9 new constants)

**Analog:** Same file — existing `# Control Flags` block at `:60-69` is the canonical "Python-mirror-of-C++-#defines" layout.

**Existing analog pattern** (`constants.py:59-69`):
```python
# Control Flags
FLAG_FORCE = 0x01
FLAG_CAN_ERASE = 0x02
FLAG_SKIP_ERASE = 0x04
FLAG_SKIP_BLANK_CHECK = 0x08
FLAG_VPE_AS_VPP = 0x10

FLAG_OUTPUT_ENABLE = 0x20
FLAG_CHIP_ENABLE = 0x40

FLAG_VERBOSE = 0x80
```

**Target — new block appended after `:69`:**
```python

# RURP Control Register Bits — mirror of firestarter/include/rurp_pinout.h
# Documentary only — Python does not write the control register directly
# (firmware owns that). Used by `firestarter dev registers --firestarter`
# and similar host-side helpers. Keep in sync per CLAUDE.md sync rule.
CTRL_VPP_VPE_DROP_ENABLE     = 0x100   # was VPE_TO_VPP (wide layout)
CTRL_VPP_REGULATOR_ENABLE    = 0x080   # was REGULATOR
CTRL_READ_WRITE              = 0x040   # was READ_WRITE
CTRL_ADDRESS_LINE_18         = 0x020
CTRL_ADDRESS_LINE_17         = 0x010
CTRL_VPP_P1_ENABLE           = 0x008   # was P1_VPP_ENABLE
CTRL_VPE_ENABLE              = 0x004   # was VPE_ENABLE
CTRL_VPP_A9_ENABLE           = 0x002   # was A9_VPP_ENABLE
CTRL_ADDRESS_LINE_16         = 0x001
```

**Pattern conventions copied from FLAG_* block:**
- Section header comment line beginning with `#`
- `UPPER_CASE = 0xNNN` per line
- Bit values in MSB-to-LSB order (matches `FLAG_VERBOSE = 0x80` ordering for FLAG_*)
- Inline `# was OLD_NAME` annotation tracing the rename
- No type annotations (matches FLAG_* convention)

---

### 16. `firestarter_app/firestarter/main.py:404-416` (docstring refresh)

**Role:** host CLI controller (argparse `--firestarter` help text) · **Data Flow:** request-response (argparse) · **Touch:** MODIFY-IN-PLACE (9 docstring lines)

**Analog:** Same file — `:400-416` IS the analog. Phase 33 refreshes the docstring text from old names to new names; the `argparse.add_argument` call structure stays identical.

**Current state** (`main.py:400-417`):
```python
reg_parser.add_argument(
    "-f",
    "--firestarter",
    action="store_true",
    help="""Using Firestarter register definition.
By using the firestarter argumet,
the control register will be remaped to match
the hardware revision of the RURP sheild.
0x100 - VPE_TO_VPP
0x080 - REGULATOR
0x040 - READ_WRITE
0x020 - ADDRESS_LINE_18
0x010 - ADDRESS_LINE_17
0x008 - P1_VPP_ENABLE
0x004 - VPE_ENABLE
0x002 - A9_VPP_ENABLE
0x001 - ADDRESS_LINE_16""",
)
```

**Target after rename:**
```python
reg_parser.add_argument(
    "-f",
    "--firestarter",
    action="store_true",
    help="""Using Firestarter register definition.
By using the firestarter argumet,
the control register will be remaped to match
the hardware revision of the RURP sheild.
See constants.RURP_CONTROL_REGISTER_BITS (mirror of rurp_pinout.h).
0x100 - CTRL_VPP_VPE_DROP_ENABLE
0x080 - CTRL_VPP_REGULATOR_ENABLE
0x040 - CTRL_READ_WRITE
0x020 - CTRL_ADDRESS_LINE_18
0x010 - CTRL_ADDRESS_LINE_17
0x008 - CTRL_VPP_P1_ENABLE
0x004 - CTRL_VPE_ENABLE
0x002 - CTRL_VPP_A9_ENABLE
0x001 - CTRL_ADDRESS_LINE_16""",
)
```

Bit ordering MSB→LSB preserved (matches `constants.py` block ordering). Existing typo `argumet`/`sheild` preserved verbatim (not a Phase 33 fix).

---

### 17. `.planning/v1.7-SHIELD-REVS.md` §7 (FILL-IN-PLACE)

**Role:** meta-repo documentation (canonical alias table) · **Data Flow:** n/a · **Touch:** FILL-IN-PLACE (replace `<!-- OWNED BY PHASE 33 — TBD -->` with 16+ row table + intro paragraph)

**Analog (column shape):** §1 inventory at `:16-25` AND §6 capability matrix at `:82-91` — both are 8-row × 9-column shield-rev tables that establish the Markdown column-style + footnote conventions §7 inherits.

**§1 column-shape excerpt** (`:16`):
```markdown
| silkscreen | provenance | state | introduced_commit | removed_commit | schematic_path | gerber_path | photo_dir | notes |
|------------|------------|-------|-------------------|----------------|----------------|-------------|-----------|-------|
```

**§6 column-shape excerpt** (`:82`):
```markdown
| rev | chip_families_supported | max_vpp_v | max_vcc_v | address_bus_width_bits | supported_protocol_ids | runtime_guard_gaps | source_evidence | notes |
|---|---|---|---|---|---|---|---|---|
```

**Target §7 column shape** (per RESEARCH §7 Column Schema):
```markdown
| silkscreen_label | label_type | canonical_alias | hex_value (legacy / rev2) | rev_0 | rev_1 | rev_2_0 | rev_2_1 | rev_2_2 | rev_2_3 | mod_rev_0 | source_citation |
|------------------|-----------|------------------|----------------------------|-------|-------|---------|---------|---------|---------|-----------|------------------|
| VPE_EN           | N         | CTRL_VPE_ENABLE  | 0x04 / 0x04                | ✓     | ✓     | ✓       | ✓       | ✓       | ✓       | (inherits Rev 0) | mine-notes.md:452 (Rev 2.1 blob f3b7a521 line 18240) |
| R41              | S         | RES_HW_REVISION_DIVIDER | n/a                 | not-present | not-present | ✓ (4k7) | ✓ (4k7) | ✓ (4k7 sch / 10k chat — pending §5) | ✓ (10k) | as-modified — pending Phase 35 | mine-notes.md:429 ("%TO.C,R41*%" in Rev 2.2 gerber) |
| JP4              | S         | JMP_VPP_P1_BYPASS | n/a                       | not-present | not-present | ✓ (1x2) | ✓ (1x2) | ✓ (1x2) | ✓ (2x2) | as-modified — pending Phase 35 | mine-notes.md:430 |
| A3 (Arduino-pin) | N         | PIN_HW_REVISION_DETECT_ADC | A3                | not-present | not-present | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) | rurp_shield.h:36 (current) |
| A2 (Arduino-pin) | N         | PIN_VPP_VOLTAGE_ADC | A2                       | ✓     | ✓     | ✓       | ✓       | ✓       | ✓       | (inherits Rev 0) | rurp_shield.h:21 (current) |
| … (control register bits — 8 rows for canonical CTRL_*) … |
| … (per-rev REV_1_* / REV_2_* variants — 4 rows) … |
```

**Row count target:** ≥ 16 (per RESEARCH "Row count estimate" — 8 control-register bits + 2 Arduino-pin assignments + 2 shield designators + 4 per-rev variant rows). Planner enumerates exactly.

**Cell sentinel conventions copied from §6:**
- `not-present` — rev does not have this designator/bit at all
- `(inherits Rev 0)` — Modified Rev 0 cells unaffected by rework (D-09)
- `as-modified — pending Phase 35` — Modified Rev 0 cells rework-touched (D-09)
- `pending Phase 35` — operator-physical-measurement gates value (Rev 2.2 R41 discrepancy)
- `✓` — applies as documented

**Source-citation column convention copied from §1 + §4:**
- Format: `mine-notes.md:NNN (Rev X.Y blob SHA line NNNN)` for schematic-net rows
- Format: `mine-notes.md:NNN ("%TO.C,DESIGNATOR*%" in Rev X.Y gerber)` for silkscreen-printed rows
- Format: `rurp_shield.h:NN (current)` for code-side anchors

---

### 18. `.planning/v1.7/phase-33-baseline-hex/` (NEW — Wave 0 binary snapshot dir)

**Role:** meta-repo tooling artifact directory · **Data Flow:** file-I/O · **Touch:** CREATE-DIR + 3 `.hex` snapshots

**Analog:** `.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md` — Phase 8 established the "snapshot binary artifact before mutating source" wave-0 pattern (also reused in Phase 9 per `09-PATTERNS.md`).

**Wave 0 capture (single-shot Bash task at start of Wave 1, BEFORE any source edit):**
```bash
mkdir -p .planning/v1.7/phase-33-baseline-hex/
cp firestarter/.pio/build/uno/firestarter_uno.hex             .planning/v1.7/phase-33-baseline-hex/uno.hex
cp firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex   .planning/v1.7/phase-33-baseline-hex/uno328pb.hex
cp firestarter/.pio/build/leonardo/firestarter_leonardo.hex   .planning/v1.7/phase-33-baseline-hex/leonardo.hex
```

**Per-wave verification:**
```bash
cd firestarter && pio run -e uno && pio run -e uno328pb && pio run -e leonardo
cmp .planning/v1.7/phase-33-baseline-hex/uno.hex       firestarter/.pio/build/uno/firestarter_uno.hex
cmp .planning/v1.7/phase-33-baseline-hex/uno328pb.hex  firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex
cmp .planning/v1.7/phase-33-baseline-hex/leonardo.hex  firestarter/.pio/build/leonardo/firestarter_leonardo.hex
```

Path is already covered by Phase 31 D-11 gitignore policy (`.planning/v1.7/`); planner verifies no `.gitignore` edit is needed.

---

### 19. (NEW Wave 0) `check_migration.sh` / `check_alias_migration.sh` (verifier script)

**Role:** meta-repo or `firestarter/tools/` regression-guard script · **Data Flow:** file-I/O · **Touch:** CREATE (single shell or Python file)

**Analog:** `firestarter_app/tools/check_dispatch.py` — existing dispatch-table regression-guard (per `firestarter_app/CLAUDE.md` "Regression guard `tools/check_dispatch.py`").

**Recommended location** (planner picks):
- `firestarter/tools/check_migration.sh` — colocated with `firestarter/name_firmware.py` (sub-repo tooling)
- OR `.planning/tools/check_alias_migration.sh` (meta-repo tooling)

**Pattern to copy from `check_dispatch.py`:** wrap an assertion (grep-zero + `cmp` exit-0) in a single executable; exit non-zero on failure with a clear message. Phase 9 SUMMARY files capture similar measurement-script patterns.

**Functional shape:**
```bash
#!/usr/bin/env bash
set -euo pipefail

# Assertion 1 — zero remaining references to old names in firmware
HITS=$(grep -rn '\b\(VPE_ENABLE\|VPE_TO_VPP\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|READ_WRITE\|REGULATOR\|HARDWARE_REVISION_PIN\|VOLTAGE_MEASURE_PIN\)\b' \
  firestarter/include/ firestarter/src/ firestarter/test/ 2>/dev/null | wc -l)
[ "$HITS" -eq 0 ] || { echo "FAIL: $HITS old-name references remain"; exit 1; }

# Assertion 2 — REV_[12]_* prefix family fully removed
HITS_REV=$(grep -rn 'REV_[12]_' firestarter/include/ firestarter/src/ 2>/dev/null | wc -l)
[ "$HITS_REV" -eq 0 ] || { echo "FAIL: $HITS_REV REV_[12]_* references remain"; exit 1; }

# Assertion 3 — .hex byte-identical for all 3 envs
for env in uno uno328pb leonardo; do
    cmp ".planning/v1.7/phase-33-baseline-hex/${env}.hex" "firestarter/.pio/build/${env}/firestarter_${env}.hex" \
      || { echo "FAIL: ${env}.hex diverged from baseline"; exit 1; }
done

echo "PASS: alias migration verified clean"
```

---

## Shared Patterns

### Pattern A: `#define`-only aliases, never `constexpr` / `enum class`

**Source:** Project convention — every existing alias is a `#define` (see `rurp_shield.h:21-89`, `firestarter.h:53-58` for `FLAG_*`, all of `constants.py:60-69`). `constexpr` is reserved for type-anchored values like `VCC_CALC_CONSTANT` in `rurp_common.cpp:27`.

**Apply to:** New `rurp_pinout.h` header. Per D-07 and Anti-Pattern bullet in RESEARCH, `constexpr` would risk emitting AVR symbol-table metadata that breaks the .hex byte-identical gate (ALIAS-03 / GATE-1.7).

**Excerpt (apply this idiom verbatim):**
```c
#define CTRL_VPP_REGULATOR_ENABLE     0x80
#define CTRL_VPP_VPE_DROP_ENABLE      0x100
```

### Pattern B: `#ifdef HARDWARE_REVISION` compile-flag gating (CRITICAL — Pitfall 2)

**Source:** `rurp_shield.h:24-53` AND `rurp_shield.h:70-89` — set via `-D HARDWARE_REVISION` in `platformio.ini:23` for all 3 AVR envs (uno, uno328pb, leonardo) but NOT set in the `[env:native]` Unity build path.

**Apply to:** `rurp_pinout.h` (mirror the existing structure VERBATIM — same `#ifndef HARDWARE_REVISION` / `#else` / `#endif` shape; same `#ifdef HARDWARE_REVISION` for the REV_* variant block).

**Excerpt (rurp_shield.h:24-53 — exact target structure for rurp_pinout.h):**
```c
#ifndef HARDWARE_REVISION
#define VPE_TO_VPP      0x01           // legacy single-rev — VPE_TO_VPP = 0x01
#define ADDRESS_LINE_16             VPE_TO_VPP   // ← LOAD-BEARING ALIAS (Pitfall 1)
#define A9_VPP_ENABLE   0x02
// …
#define REGULATOR       0x80

#else
// per-rev wide layout — different value mapping
#define ADDRESS_LINE_16             0x01
// …
#define VPE_TO_VPP      0x100          // ← value DIFFERS from legacy
#endif
```

### Pattern C: Header organization — one `.h` per major subsystem

**Source:** `firestarter/include/` directory layout: `rurp_shield.h` (shield interface), `rurp_register_utils.h` (register write inline), `rurp_hw_rev_utils.h` (rev dispatch inline), `firestarter.h` (handle struct + flag bits), `rurp_types.h` (type defs), etc.

**Apply to:** New `rurp_pinout.h` fits cleanly into this layout (between `rurp_types.h` and `rurp_shield.h` in include-order).

### Pattern D: Cross-repo Python↔C++ constants sync rule

**Source:** `firestarter_app/CLAUDE.md:100` — *"`firestarter/constants.py` must stay in sync with `firestarter/include/firestarter.h` in the firmware sub-repo. Both define the same flag bit values and command codes."*

**Apply to:** Per D-08, expand this rule to also cover the new `rurp_pinout.h` ↔ `constants.py::RURP_CONTROL_REGISTER_BITS` block. Recommended: refresh the `firestarter_app/CLAUDE.md` sync rule text in Wave 4 (same commit as the constants.py addition for atomicity).

### Pattern E: `firestarter/CLAUDE.md` §Constants docstring sync

**Source:** `firestarter/CLAUDE.md:86-93` — already documents control-register bits with their OLD names (`REGULATOR (0x80)`, `VPE_TO_VPP (0x01)`, `P1_VPP_ENABLE (0x08)`, `A9_VPP_ENABLE (0x02)`, `VPE_ENABLE (0x04)`).

**Apply to:** Phase 33 MUST refresh this CLAUDE.md docstring to new `CTRL_*` names in Wave 1 (atomicity recommendation A6 from RESEARCH). Concrete refresh target:
```markdown
Control register bits (from `rurp_pinout.h`):
- `CTRL_VPP_REGULATOR_ENABLE (0x80)` — enable VPP boost regulator
- `CTRL_VPP_VPE_DROP_ENABLE (0x01 legacy / 0x100 rev2)` — drop VPE through resistor to VPP level
- `CTRL_VPP_P1_ENABLE (0x08)` — route VPP to socket pin 1
- `CTRL_VPP_A9_ENABLE (0x02)` — route VPP to A9 (for EPROM chip ID read)
- `CTRL_VPE_ENABLE (0x04)` — apply VPE directly to PGM pin
```
Algorithm table at `firestarter/CLAUDE.md:53-65` also references `VPE_TO_VPP` in handler-description column (rows 1, 2) and `P1_VPP` (row Intel) — refresh both.

### Pattern F: Phase-tagged comment-style for refresh

**Source:** `09-PATTERNS.md:30` — Phase 9 norm of `# Phase X (LXXX-NN): ...` voice for comment refresh + memory-pattern matching.

**Apply to:** When refreshing load-bearing comments in `memory.cpp:142-144`, `eprom.cpp:276, :279` and similar, planner may use `// Phase 33 / ALIAS-02: …` annotation or leave clean — planner's discretion. The Phase 9 archive uses both styles.

### Pattern G: Pre/post `.hex` measurement protocol (GATE-1.7)

**Source:** Phase 9 `09-MEASUREMENT.md` — established the bench matrix of per-board `wc -c` + `sha256sum` capture in fix-commit messages.

**Apply to:** Wave 4 wrap-up commit message MUST include:
1. `wc -c` of pre-rename + post-rename `.hex` for each of 3 boards
2. `cmp` exit code per board (expected: 0)
3. `sha256sum` of all 3 post-rename `.hex` (one line per board)
4. Diff vs ALIAS-03 ≤ ~50 B budget (expected: 0 B drift)

### Pattern H: Word-boundary grep for old-name sweep (Pitfall 6)

**Source:** RESEARCH §Exact Call-Site Inventory verification command — use `\b` word boundaries to avoid false positives on comments referencing "CONTROL REGISTER" (which contains `REGULATOR` as a substring).

**Apply to:** All `grep -rn` operations in the verifier script + planner-task verification step. Pattern:
```bash
grep -rn '\b\(VPE_ENABLE\|VPE_TO_VPP\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|READ_WRITE\|REGULATOR\|HARDWARE_REVISION_PIN\|VOLTAGE_MEASURE_PIN\)\b' include/ src/ test/
```

---

## No Analog Found

None. Every file Phase 33 touches has at least one direct in-tree analog. The `rurp_pinout.h` NEW file's body is carved verbatim from `rurp_shield.h:21-89`; §7 reuses §1 + §6 column-shape conventions; the verifier script reuses `check_dispatch.py`'s wrap-an-assertion-in-a-CLI idiom.

---

## Cross-Phase Handoff Pattern Mapping

These four handoffs are explicitly called out in CONTEXT.md and mapped here:

| Handoff | Source Analog | Phase 33 Use |
|---------|---------------|---------------|
| **Phase 9 macro-rename precedent** | `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-PATTERNS.md` (entire file shape) + `09-MEASUREMENT.md` (`.hex` capture protocol) | (a) Wave decomposition (small atomic diffs); (b) per-wave verifier (`pio run` + `pio test -e native` + `cmp`); (c) fix-commit message must include per-board `wc -c` (Pattern G). Confidence HIGH — Phase 9 closed clean. |
| **HARDWARE_REVISION ifdef pattern** | `rurp_shield.h:24-89` (existing) | Pattern B above — `rurp_pinout.h` mirrors the `#ifndef HARDWARE_REVISION` / `#else` / `#endif` shape VERBATIM. Same gate, same hex-value duality (Pitfall 2), same `ADDRESS_LINE_16 == VPE_TO_VPP` aliasing in the legacy branch (Pitfall 1). |
| **`rurp_map_ctrl_reg_for_hardware_revision()` dispatcher** | `rurp_hw_rev_utils.h:13-35` (existing) | Pattern Assignment §3 above — function body is its own analog. Switch shape, case-fallthrough, REVISION_* enum constants ALL preserved verbatim; only the macro identifiers inside the body change (LHS canonical input mask + RHS per-rev output bits BOTH rename — Pitfall 3). |
| **`constants.py` flag-bits block** | `constants.py:59-69` (existing `# Control Flags` block) | Pattern Assignment §15 above — same section-header style, same `NAME = 0xNN` shape, same "no type annotations" convention. New `# RURP Control Register Bits` block appended after the existing FLAG_* block; inline `# was OLD_NAME` annotation traces the rename. |
| **`v1.7-SHIELD-REVS.md` §1-§6 column conventions** | `.planning/v1.7-SHIELD-REVS.md` §1 at `:16-25` (8r × 9c) + §6 at `:82-91` (8r × 9c) | Pattern Assignment §17 above — §7 is a 12-column table (1 silkscreen + 1 type + 1 alias + 1 hex + 7 per-rev + 1 citation) but reuses §1's sentinel-cell vocabulary (`not-present`, `(inherits Rev 0)`, `as-modified — pending Phase 35`) and §1's source-citation column format. |

---

## Notes

1. **`sram.cpp`** — listed in CONTEXT.md's file handoff list, but `grep` against the working tree did not surface old-name references in this file. The planner should sweep `firestarter/src/proms/sram.cpp` and confirm whether the file has 0, 1, or N call-sites. If 0, drop from plan; if N>0, treat with the same `eeprom_28c.cpp` analog (Pattern Assignment §9 — same 5V-only handler shape).
2. **`firestarter/include/firestarter.h:53` `FLAG_VPE_AS_VPP 0x10`** — per RESEARCH Open Question #5, this is a wire-protocol flag (NOT a shield-net name) and is OUT of D-03 alias-scope. Phase 33 does NOT migrate it. Verified in the Anti-Patterns bullet of RESEARCH.
3. **`CONFIG_VERSION "VER06"`** — stays at `"VER06"` per D (Discretion item) + Pitfall 5. `rurp_configuration_t` struct layout is byte-identical pre/post.
4. **Native vs AVR build paths** — Native test build does NOT set `-D HARDWARE_REVISION` → uses legacy `#ifndef HARDWARE_REVISION` path → exercises the `ADDRESS_LINE_16 == VPE_TO_VPP` aliasing (Pitfall 1). All 3 AVR envs set `-D HARDWARE_REVISION` → use the wide layout. The verifier script's `cmp` runs on AVR `.hex`; the Unity native test catches the legacy-path aliasing trap.

---

## Metadata

**Analog search scope:**
- `firestarter/include/` (15 headers)
- `firestarter/src/proms/` (10 .cpp files, 1 .h)
- `firestarter/src/boards/` (3 .cpp files)
- `firestarter/src/` (top-level: hardware_operations.cpp, firestarter.cpp, etc.)
- `firestarter/test/native/avr/` (Unity test suites)
- `firestarter_app/firestarter/` (constants.py, main.py, eprom_operations.py)
- `firestarter_app/tools/` (check_dispatch.py)
- `.planning/v1.7-SHIELD-REVS.md` (§1-§6 column conventions)
- `.planning/phases/09-delete-old-log-macros-measure-flash-savings/` (Phase 9 precedent — 09-PATTERNS.md, 09-MEASUREMENT.md, 09-CONTEXT.md)

**Files scanned (direct Read or Grep):** 14
**Pattern extraction date:** 2026-05-25
