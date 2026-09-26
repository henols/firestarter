# Phase 126: Flash-Persistent Config via a Storage-Backend Seam - Pattern Map

**Mapped:** 2026-07-31
**Files analyzed:** 11 (5 new firmware sources/headers, 3 new pytest modules, 3 changed, 1 deleted)
**Analogs found:** 10 / 11 (one has a recorded absence, not a wrong analog)
**Codebase:** `/workspaces/firestarter` @ `2b5e8c8`, branch `v1.23-py32f071-integration` (verified at map time)

> **Every line number below was re-confirmed against the live tree this session.** Where the
> research's line numbers were off, the correction is flagged inline with **[LINE-CORRECTION]**.
> Where a file the research or the orchestrator names does not exist, it is recorded in
> §"No Analog Found" / §"Recorded Absences" rather than substituted.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `include/rurp_config_storage.h` | **NEW** — seam header | contract only | `include/rurp_vpp.h` (Phase 125 seam header) | **exact** — same role (capability/seam header), same `extern "C"` idiom, same "fire-proof by a `tests/` harness" convention |
| `src/rurp_config_utils.cpp` | **CHANGED** — policy/service | file-I/O (delegated) | itself, pre-refactor (the only policy TU of its kind) | **self** — a pure split; the pre-refactor shape below IS the reference |
| `src/boards/rurp_config_storage_eeprom.cpp` | **NEW** — per-platform backend | file-I/O (EEPROM byte blob) | `src/boards/rurp_common.cpp` | **exact** — AVR-only TU in `src/boards/`, `# PY32_EXCLUDED:` manifest line, board-macro `#if` guard |
| `platform/py32f071/src/config_storage_dualslot.cpp` (+ local `.h`) | **NEW** — HAL-free algorithm core | transform + file-I/O via injected primitives | `platform/py32f071/src/timing.cpp` (shape/linkage) — **no HAL-free-injected-primitive core exists in the tree** | **role-match only** (see §"No Analog Found" row 1) |
| `platform/py32f071/src/config_storage_flash.cpp` | **NEW** — HAL glue | file-I/O | `platform/py32f071/src/timing.cpp` | **exact** — narrow ARM-only HAL wrapper TU, `extern "C"` definitions, anonymous-namespace state |
| `platform/py32f071/src/config.cpp` | **DELETED** | — | n/a | n/a — read verbatim below so the four drift points are on the record before deletion |
| `platform/py32f071/linker/PY32F071xB_FLASH.ld` | **CHANGED** — config/linker script | address map | itself (only `.ld` in the tree) | **self** — current `MEMORY` block quoted verbatim below |
| `platform/py32f071/CMakeLists.txt` | **CHANGED** — build manifest | — | itself (the 5 existing `PY32_EXCLUDED` lines) | **self** |
| `platform/py32f071/CONFIG-STORAGE.md` | **NEW** — design doc | — | `platform/py32f071/README.md` | weak — no in-tree vendored-design doc exists; format is fully specified by CONTEXT Discretion + RESEARCH §Code Examples |
| `tests/test_config_storage_eeprom_regression.py` | **NEW** — test (compile+run) | request-response over subprocess | `tests/test_vpp_seam_manual_on_every_board.py` | **exact** |
| `tests/test_config_storage_dualslot.py` | **NEW** — test (compile+run, 6 fns) | request-response over subprocess | `tests/test_vpp_seam_manual_on_every_board.py` | **exact** |
| `tests/test_py32_flash_map.py` | **NEW** — test (textual gate) | transform (parse text, assert) | `tests/test_vpp_seam_manual_on_every_board.py::test_board_macro_sets_match_the_real_build_config` | **exact** — substring/regex presence over a plain file read, "deliberately explicit, never derived" |

---

## Pattern Assignments

### `include/rurp_config_storage.h` (NEW — seam header, contract only)

**Analog:** `include/rurp_vpp.h` (89 lines, entire file read).

This is the closest analog in the tree by a wide margin: it is the *other* seam header authored
one phase earlier, under the same D-09-ancestor constraint (do not touch `rurp_shield.h`).

**Header-open pattern** — `rurp_vpp.h:1`, then a long rationale comment block, then the include:
```c
#pragma once

/*
 * Phase 125 (VPP-01, VPP-02, decisions D-06/D-07/D-09/D-10/D-11) -- the VPP
 * control capability seam. ...
 *
 * WHY THIS IS DEPENDENCY-FREE:
 *   The only include below is <stdint.h>, which a plain host preprocessor
 *   resolves standalone -- no rurp_shield.h, no <Arduino.h>, no
 *   rurp_platform.h, no PY32 HAL. This is a standing constraint (D-02), not a
 *   local convenience: ...
 *
 * FIRE-PROOF:
 *   tests/test_vpp_seam_manual_on_every_board.py compiles this header (and
 *   src/rurp_vpp.cpp) with a host compiler across every board macro-set ...
 */

#include <stdint.h>
```

**Note the guard idiom divergence.** `rurp_vpp.h` uses `#pragma once`; the older headers use
include guards — `include/rurp_types.h:8-9`:
```c
#ifndef __RURP_TYPES_H__
#define __RURP_TYPES_H__
```
RESEARCH §Pattern 1 prescribes `#ifndef __RURP_CONFIG_STORAGE_H__`. **Both idioms are live in
`include/`.** Either is defensible; the `__RURP_*_H__` form matches `rurp_types.h` /
`rurp_shield.h`, the `#pragma once` form matches the immediate seam-header analog.

**`extern "C"` wrapper pattern** — `rurp_vpp.h:70-72` and `:88-90` (this is C-11's requirement,
and the analog does it exactly):
```c
#ifdef __cplusplus
extern "C" {
#endif

/* ... declarations ... */

#ifdef __cplusplus
}
#endif
```
Corroborated at the other end of the seam: `include/rurp_shield.h:12` opens `extern "C" {`
(inside `#ifdef __cplusplus`) and `:162` closes it — **verified**, which is why the four config
declarations at `rurp_shield.h:61` (`void rurp_load_config();`) and `:150-152`
(`rurp_get_config` / `rurp_save_config` / `rurp_validate_config`) already have C linkage.
**All four line numbers verified exact.**

**Declaration-style pattern** — `rurp_vpp.h:84-86`, bare prototypes, no bodies, `(void)` on
no-arg functions:
```c
rurp_vpp_control_mode_t rurp_vpp_control_mode(void);
rurp_vpp_result_t rurp_set_vpp_target_mv(uint16_t target_mv, uint16_t tolerance_mv, uint16_t timeout_ms);
void rurp_disable_vpp_control(void);
```
**Caution for the planner:** D-06's declarations return `bool` and take `size_t`. `rurp_vpp.h`
includes only `<stdint.h>`. A `bool` in a header that may be preprocessed as C needs
`<stdbool.h>`, and `size_t` needs `<stddef.h>`. RESEARCH §Pattern 1's sketch includes
`<stddef.h>` **inside** the `extern "C" {` block and never includes `<stdbool.h>` — copy the
analog's ordering (includes *before* the `extern "C"` open, per `rurp_vpp.h:58` vs `:70`), not
the sketch's.

**Fire-proof convention (mandatory, per the analog's own comment):** the header must name the
`tests/` module that proves its guards can fire. `rurp_vpp.h:51-55` does this, and
`tests/test_vpp_seam_manual_on_every_board.py::test_seam_source_is_dependency_free`
(lines 424-444) enforces the reciprocal constraint on the `.cpp`.

---

### `src/rurp_config_utils.cpp` (CHANGED — policy layer; the split's source)

**Analog:** itself, pre-refactor. **Full current file (40 lines), read verbatim this session** —
this is the byte-for-byte reference CFG-04's regression test is written against, and every line
number the research cites is **verified**:

```cpp
/*
 * Project Name: Firestarter
 * Copyright (c) 2025 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "rurp_shield.h" // For CONFIG_VERSION, VALUE_R1, VALUE_R2
#include <EEPROM.h>

#define CONFIG_START 48                      // <-- :11  moves to the AVR backend TU (D-07)

// Define the global configuration variable here.
// This is the single definition that the linker will use.
rurp_configuration_t rurp_config;             // <-- :15  the global, STAYS (D-07)

// Define the functions here. Their declarations are in rurp_shield.h
rurp_configuration_t* rurp_get_config() {     // <-- :18  STAYS
    return &rurp_config;
}

void rurp_load_config() {                     // <-- :22  STAYS, EEPROM.get -> seam call
    rurp_configuration_t* config = rurp_get_config();
    EEPROM.get(CONFIG_START, *config);        // <-- :24  MOVES below the seam
    rurp_validate_config(config);
}

void rurp_save_config(rurp_configuration_t* config) {  // <-- :28 STAYS
    EEPROM.put(CONFIG_START, *config);        // <-- :29  MOVES below the seam
}

void rurp_validate_config(rurp_configuration_t* config) {  // <-- :32 STAYS, UNCHANGED
    if (strcmp(config->version, CONFIG_VERSION) != 0) {
        strcpy(config->version, CONFIG_VERSION);
        config->r1 = VALUE_R1;
        config->r2 = VALUE_R2;
        config->hardware_revision = 0xFF;
        rurp_save_config(config);             // <-- :38  the D-14 write-back
    }
}
```

**Facts a plan must not re-derive:**
- No `extern "C"` markers in this file — it gets C linkage transitively from
  `#include "rurp_shield.h"` (C-11, verified).
- `strcmp`/`strcpy` come from `rurp_shield.h:17` (`#include <string.h>`) — **verified**; the
  policy TU needs no new include after the split.
- The two lines that cross the seam are exactly `:24` and `:29`. Nothing else in this file is
  EEPROM-aware.

**Schema pin (CFG-07)** — `include/rurp_types.h:19-24`, verified byte-for-byte:
```c
typedef struct rurp_configuration {
    char version[6];
    long r1;
    long r2;
    uint8_t hardware_revision;
} rurp_configuration_t;
```
`CONFIG_VERSION "VER06"` at `rurp_shield.h:46`; `VALUE_R1 270000` at `:49`, `VALUE_R2 44000` at
`:50`. **All verified.**

---

### `src/boards/rurp_config_storage_eeprom.cpp` (NEW — AVR backend, pure move)

**Analog:** `src/boards/rurp_common.cpp` — the precedent CONTEXT D-08 cites by name ("AVR-only
common code in `src/boards/`, excluded from the ARM manifest").

**File-header + board-guard pattern** (`rurp_common.cpp:1-12`, verified):
```cpp
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include <Arduino.h>
#include "rurp_shield.h"
#include "rurp_pinout.h"

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB) || defined(ARDUINO_AVR_LEONARDO)
```

The two sibling board TUs use a *narrower* guard, placed **before** the includes:
- `src/boards/uno_rurp_shield.cpp:8` — `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)`, then `#include "rurp_shield.h"` / `<Arduino.h>` / `"rurp_register_utils.h"`.
- `src/boards/leonardo_rurp_shield.cpp:9` — `#ifdef ARDUINO_AVR_LEONARDO`, same include order.

**Which to copy:** `rurp_common.cpp`'s three-board `#if defined(...) || ... || ...` form, since
the EEPROM backend must compile on all three AVR targets. Note `rurp_common.cpp` puts the guard
*after* the includes; the other two put it *before*. For an `#include <EEPROM.h>` TU the
before-includes placement (uno/leonardo shape) is the safer copy.

**Body pattern:** lift `:11` (`#define CONFIG_START 48`), `:24` (`EEPROM.get`) and `:29`
(`EEPROM.put`) from `rurp_config_utils.cpp` above, wrapped in the two D-06 functions returning
`true` unconditionally. `EEPROM.get`/`put` are the real Arduino templates
(`framework-arduino-avr/libraries/EEPROM/src/EEPROM.h:130-142`) — `put` has per-byte
`update()` semantics (RESEARCH C-12).

**Manifest exclusion pattern** — `platform/py32f071/CMakeLists.txt:30-34`, verified verbatim,
and note the reason-segment format `-- <reason>` is **mandatory** (see the checker below):
```cmake
# PY32_EXCLUDED: src/boards/uno_rurp_shield.cpp -- AVR board impl, no ARM analogue
# PY32_EXCLUDED: src/boards/leonardo_rurp_shield.cpp -- AVR board impl, no ARM analogue
# PY32_EXCLUDED: src/boards/rurp_common.cpp -- AVR-specific common
# PY32_EXCLUDED: src/dev_tools.cpp -- no ARM dev-tools TU; DEV_TOOLS resolves to 0 by the shared default (MERGE-08, D-02)
# PY32_EXCLUDED: src/rurp_config_utils.cpp -- Phase 126 per-platform config backend split; THIS EXCLUSION WILL NEED REVISITING in Phase 126, it is not a permanent exclusion.
```
`grep -rn PY32_EXCLUDED` across the whole tree returns these five lines plus the checker, its
paired pytest and two fixture trees — **nowhere else**. Confirmed: the `:34` line does carry its
own "WILL NEED REVISITING in Phase 126" note, exactly as CONTEXT states.

**No AVR-side `platformio.ini` edit is needed.** `[env:uno]` (`:31`), `[env:uno328pb]` (`:40`)
and `[env:leonardo]` (`:57`) carry **no** `build_src_filter` — the only three
`build_src_filter` lines in the file are at `:163`, `:252`, `:290` (the three native envs).
**Verified**; `src/` is compiled wholesale on AVR, so the new TU is picked up automatically.

---

### `platform/py32f071/src/config_storage_flash.cpp` (NEW — HAL glue)

**Analog:** `platform/py32f071/src/timing.cpp` — the narrowest ARM-only HAL-wrapper TU in the port.

**Imports + anonymous-namespace state + `extern "C"` definition pattern** (`timing.cpp:1-20`,
verified):
```cpp
#include "boards/py32f071_rurp_shield.h"

namespace
{
TIM_HandleTypeDef microsecond_timer;
}

extern "C" void rurp_timing_init(void)
{
    __HAL_RCC_TIM3_CLK_ENABLE();

    const uint32_t pclk = HAL_RCC_GetPCLK1Freq();
    if (pclk < 1000000U || (pclk % 1000000U) != 0U)
    {
        for (;;)
        {
        }
    }
```
Take from this: (a) a single board-header include pulls the whole HAL in; (b) file-local state
in an unnamed `namespace { }`, never `static` at file scope; (c) Allman braces — the ARM
platform sources use Allman, the `src/` firmware uses K&R. Match the directory you are in.

**Platform-guard `#error` pattern** — `platform/py32f071/src/py32f071_rurp_shield.cpp:1-10`
(verified):
```cpp
#include <Arduino.h>

#include "boards/py32f071_rurp_shield.h"
#include "rurp_register_utils.h"
#include "rurp_serial_utils.h"
#include "rurp_shield.h"

#if !defined(RURP_PLATFORM_PY32F071)
#error "py32f071_rurp_shield.cpp compiled for the wrong platform"
#endif
```
Worth copying into `config_storage_flash.cpp` (the HAL half must never be compiled by the host
test — D-02/D-03 compile only the *dualslot* TU by path). **Do NOT put this guard in
`config_storage_dualslot.cpp`**, which the host `g++` harness must compile.

---

### `platform/py32f071/src/config.cpp` (DELETED — the drift, on the record)

**Full current file (47 lines), read verbatim this session.** Recorded here so CFG-07's four
drift points are provable after deletion. **All research line numbers verified exact.**

```cpp
#include <string.h>

#include "rurp_shield.h"

namespace
{
rurp_configuration_t configuration;          // <-- private static, NOT the shared `rurp_config` global
}

extern "C" rurp_configuration_t *rurp_get_config(void)
{
    return &configuration;
}

extern "C" void rurp_validate_config(rurp_configuration_t *value)   // <-- :15-:30 DRIFTED COPY
{
    if (value == nullptr)
    {
        return;
    }

    if (strcmp(value->version, CONFIG_VERSION) != 0 || value->r2 == 0)  // <-- `|| r2 == 0` is drift
    {
        memset(value, 0, sizeof(*value));                                // <-- memset is drift
        strcpy(value->version, CONFIG_VERSION);
        value->r1 = VALUE_R1;
        value->r2 = VALUE_R2;
        value->hardware_revision = 0xFFU;
        /* NOTE: no rurp_save_config() call -- the AVR write-back at
           rurp_config_utils.cpp:38 has NO counterpart here. Drift point 3. */
    }
}

extern "C" void rurp_load_config(void)
{
    memset(&configuration, 0, sizeof(configuration));                    // <-- never reads storage
    rurp_validate_config(&configuration);
}

extern "C" void rurp_save_config(rurp_configuration_t *value)            // <-- :38-:47 PERSISTS NOTHING
{
    if (value == nullptr)
    {
        return;
    }

    rurp_validate_config(value);
    configuration = *value;                                              // <-- assigns to a static
}
```

**Deleting this file also requires removing `src/config.cpp` from `PY32_PLATFORM_SOURCES`**
(`CMakeLists.txt:62`) — `PY32_PLATFORM_SOURCES` is an **ENFORCED** list in
`check_cmake_manifest.py`, so a dangling entry is exit 1, and a missing entry for a new TU is
*not* caught (the reverse check only walks `src/`).

---

### `platform/py32f071/linker/PY32F071xB_FLASH.ld` (CHANGED)

> **[PATH CORRECTION]** The orchestrator prompt names
> `firestarter/platform/py32f071/PY32F071xB_FLASH.ld`. **That path does not exist.** The real
> path is `platform/py32f071/linker/PY32F071xB_FLASH.ld` (as CONTEXT §canonical_refs states,
> and as `CMakeLists.txt:28` sets: `set(LINKER_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/linker/PY32F071xB_FLASH.ld")`).

**Current `MEMORY` block, verbatim, lines 1-11** (the file is 115 lines; `MEMORY` is at `:3-7`
as the research states — **verified**):
```ld
ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 128K
    RAM   (xrw) : ORIGIN = 0x20000000, LENGTH = 16K
}

_estack = ORIGIN(RAM) + LENGTH(RAM);
_Min_Heap_Size = 0x000;
_Min_Stack_Size = 0x400;
```

**In-file `PROVIDE` precedent for D-11** — the script already uses both `PROVIDE_HIDDEN` and
`PROVIDE`, so D-11's symbols follow an existing idiom rather than inventing one:
```ld
    .init_array :
    {
        PROVIDE_HIDDEN(__init_array_start = .);          /* :65 */
        KEEP(*(SORT(.init_array.*)))
        KEEP(*(.init_array*))
        PROVIDE_HIDDEN(__init_array_end = .);            /* :68 */
    } > FLASH
```
```ld
    ._user_heap_stack (NOLOAD) :
    {
        . = ALIGN(8);
        PROVIDE(end = .);                                /* :107 */
        PROVIDE(_end = .);                               /* :108 */
```
**Also note:** there is currently **no bare `__symbol = value;` assignment outside a section**
except `_estack` / `_Min_Heap_Size` / `_Min_Stack_Size` at `:9-11`. D-11's
`__config_slot_a_start` / `__config_slot_b_start` / `__config_page_size` `PROVIDE`s should sit
in that same top-of-file region (after `MEMORY`, before `SECTIONS`), matching `_estack`'s
placement. Every `> FLASH` output section (`:20, 34, 42, 47, 54, 61, 69, 77, 89`) is unaffected
by shrinking `LENGTH`; nothing in `SECTIONS` names a literal address.

This is the only `.ld` file in the tree — no second linker script exists to cross-check against.

---

### `platform/py32f071/CMakeLists.txt` (CHANGED — four edits per C-3)

**Verified structure** (research said `FIRESTARTER_COMMON_SOURCES` at `:35–52`;
**[LINE-CORRECTION]** the `set()` block is `:35-53`, closing paren on `:53`):

| Block | Lines | Enforced by the gate? |
|---|---|---|
| `PY32_EXCLUDED` comments | `:30-34` | yes — reason segment mandatory |
| `FIRESTARTER_COMMON_SOURCES` | `:35-53` (18 entries) | **ENFORCED** |
| `PY32_PLATFORM_SOURCES` | `:55-63` (7 entries, bare relative paths) | **ENFORCED** |
| `PY32_SDK_SOURCES` | `:65-80` (14 entries, `${PY32_SDK_ROOT}/...`) | **STRUCTURALLY EXEMPT** |

**C-3 confirmed independently:** `grep -c hal_flash platform/py32f071/CMakeLists.txt` → **`0`**.
`PY32_SDK_SOURCES` names `py32f071_hal.c`, `_rcc.c`, `_rcc_ex.c`, `_gpio.c`, `_cortex.c`,
`_pwr.c`, `_dma.c`, `_adc.c`, `_adc_ex.c`, `_tim.c` and three CherryUSB files. **No flash
driver.** Edit 4 is real.

**Path-idiom pattern to copy** (three incompatible idioms in one file — do not mix them):
```cmake
set(FIRESTARTER_COMMON_SOURCES
    "${REPOSITORY_ROOT}/src/firestarter.cpp"          # quoted, ${REPOSITORY_ROOT}-rooted
    ...
)
set(PY32_PLATFORM_SOURCES
    src/main.cpp                                       # bare, relative to platform/py32f071/
    src/config.cpp                                     # <-- :62, DELETE
)
set(PY32_SDK_SOURCES
    "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_gpio.c"   # quoted, ${PY32_SDK_ROOT}
)
```

---

### `tests/test_config_storage_*.py` (NEW — the pytest + g++ harness)

**Analog:** `tests/test_vpp_seam_manual_on_every_board.py` (469 lines, read in full).
Second analog for the compile-must-fail leg: `tests/test_pinmap_guard_fires.py`.

**There is no `conftest.py` anywhere in the repo**, and no `pytest.ini` / `pyproject.toml` /
`setup.cfg` / `tox.ini`. **Verified** — `tests/` contains only `__init__.py`, `fixtures/`,
`golden/` and 12 `test_*.py` modules. Path resolution is therefore **self-contained per module**,
and the analog says so explicitly in its docstring (`:36-39`). Copy that.

**Exact self-contained path-resolution idiom** (`:78-93`):
```python
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_INCLUDE = _REPO_ROOT / "include"
_SEAM_HEADER = _INCLUDE / "rurp_vpp.h"
_SEAM_SRC = _REPO_ROOT / "src" / "rurp_vpp.cpp"
_PLATFORMIO_INI = _REPO_ROOT / "platformio.ini"
_PY32_CMAKE = _REPO_ROOT / "platform" / "py32f071" / "CMakeLists.txt"
_PY32_BOARD_HEADER = _INCLUDE / "boards" / "py32f071_rurp_shield.h"
```
Stdlib + pytest only. No third-party import, no PlatformIO import, nothing under `.pio/`.

**Exact fail-closed compiler resolution** (`:136-155`) — copy verbatim, adjusting only the
docstring:
```python
def _resolve_compiler():
    """Resolve the host C++ compiler, fail-closed. ..."""
    compiler = shutil.which(os.environ.get("CXX", "g++"))
    assert compiler is not None, (
        "host C++ compiler not found on PATH (checked $CXX, falling back to "
        "'g++'). This must FAIL the suite, never be silently skipped -- no "
        "embedded toolchain is invoked here."
    )
    return compiler
```

**Exact g++ subprocess-compile idiom** (`:179-191`) — list argv, never a shell, always
`-std=gnu++17 -Wall -Wextra` plus `-I include`:
```python
def _compile(compiler, defines, sources, output_path):
    """Compile (and, when a real main is present, link) the given source
    files with the given macro definitions into a real binary at
    output_path. List argv only, never a shell; ..."""
    argv = [compiler, "-std=gnu++17", "-Wall", "-Wextra", "-I", str(_INCLUDE)]
    argv += [f"-D{define}" for define in defines]
    argv += [str(source) for source in sources]
    argv += ["-o", str(output_path)]
    return subprocess.run(argv, capture_output=True, text=True)
```
For a *preprocess-only* leg the second analog uses `-E` and `os.devnull`
(`test_pinmap_guard_fires.py:103-108`):
```python
    argv = [compiler, "-E", "-I", str(_INCLUDE_BOARDS)]
    argv += [f"-D{_MACRO_NAME}={define}"]
    argv += [str(tu_path), os.devnull]   # actual: ... "-o", os.devnull
    return subprocess.run(argv, capture_output=True, text=True)
```

**Exact run-the-binary idiom, and *why* the result crosses on stdout not the exit code**
(`:194-201`) — this is load-bearing for the six dual-slot tests:
```python
def _run_binary(binary_path):
    """Execute the compiled binary as a second subprocess, list argv,
    capturing output. The seam's result value crosses this process boundary
    on stdout, never this run's exit code (Trap 2): 1 is also the exit code
    of a compile failure, a link failure and a crash, so returning it from
    main would make the correct answer indistinguishable from every
    failure mode."""
    return subprocess.run([str(binary_path)], capture_output=True, text=True)
```

**Exact throwaway-shim-TU idiom — written fresh into `tmp_path` every call, never a committed
fixture TU** (`:158-176`). This is the pattern the RAM-fake main and the fake `EEPROM.h` must
follow:
```python
def _write_shim_tu(tmp_path):
    """Write the measured RESEARCH shim into tmp_path, fresh every call --
    never a committed fixture translation unit (D-03 declined one). ..."""
    tu_path = tmp_path / "vpp_seam_main.cpp"
    tu_path.write_text(
        '#include "rurp_vpp.h"\n'
        "#include <cstdio>\n"
        "int main(void) {\n"
        '    printf("mode=%d result=%d\\n", (int)rurp_vpp_control_mode(),\n'
        "           (int)rurp_set_vpp_target_mv(12000, 200, 50));\n"
        "    rurp_disable_vpp_control();\n"
        "    return 0;\n"
        "}\n"
    )
    return tu_path
```
`test_pinmap_guard_fires.py:94-95` is the one-liner variant:
```python
    tu_path = tmp_path / "pinmap_guard_tu.cpp"
    tu_path.write_text('#include "py32f071_pinmap_guard.h"\n')
```

**Result-parsing idiom — regex over stdout with a full-context failure message** (`:263-280`):
```python
    match = re.match(r"mode=(\d+) result=(\d+)\s*$", run_result.stdout)
    assert match, (
        f"expected stdout of the form 'mode=<int> result=<int>' for board "
        f"macro-set {defines!r}.\n"
        f"stdout:\n{run_result.stdout!r}\nstderr:\n{run_result.stderr!r}"
    )
```

**Zero-warning assertion** (`:250-254`) — the analog demands `stderr == ""` under
`-Wall -Wextra`, not merely exit 0:
```python
    assert compile_result.stderr == "", (
        f"expected zero bytes of -Wall -Wextra warning output for board "
        f"macro-set {defines!r}.\n"
        f"stdout:\n{compile_result.stdout}\nstderr:\n{compile_result.stderr}"
    )
```

**Compile-must-FAIL leg + read-the-`#error`-text-at-test-time idiom** (`:204-217`, `:283-305`) —
the non-vacuity pattern, if a fail-closed guard here needs one:
```python
def _expected_header_error_text():
    """Read the #error message out of include/rurp_vpp.h at test time,
    rather than hardcoding it a second time here ..."""
    text = _SEAM_HEADER.read_text()
    m = re.search(r'#\s*error\s+"([^"]*)"', text)
    assert m, (...)
    return m.group(1)
```
```python
    result = _compile(compiler, ("__AVR__", "RURP_HAS_VPP_DAC=1"), (_SEAM_SRC,), binary_path)
    assert result.returncode != 0, (...)
    assert expected_text in result.stderr, (...)
```

**Textual drift-gate idiom — the analog for `tests/test_py32_flash_map.py`** (`:333-386`).
Plain `read_text()` + substring/regex presence, deliberately **not** parsed into a structure:
```python
    platformio_text = _PLATFORMIO_INI.read_text()
    cmake_text = _PY32_CMAKE.read_text()

    avr_anchors = (
        ("[env:uno]", "board = uno"),
        ("[env:uno328pb]", "board = ATmega328PB"),
        ("[env:leonardo]", "board = leonardo"),
    )
    for env_header, board_line in avr_anchors:
        assert env_header in platformio_text, (
            f"drift detected: expected {env_header!r} in {_PLATFORMIO_INI} -- ..."
        )
```
and the negative form (`:412`), for asserting an absence:
```python
    assert not re.search(r"^\s*#\s*define\s+RURP_HAS_VPP_DAC\b", board_header_text, re.MULTILINE), (...)
```
Use this shape for the D-12(b) linker-map gate (parse `CONFIG`'s `ORIGIN`/`LENGTH` out of the
`.ld` text, assert the region lies inside `0x08000000 + 128 KiB`, assert `__config_page_size`
is 256) and for C-3's edit-4 check (`"py32f071_hal_flash.c" in cmake_text`).

**Self-enforcing no-skip leg** (`:447-468`) — copy this into every new module, including the
concatenation trick that keeps the test from tripping its own check:
```python
def test_compiler_is_required_not_optional():
    """... The two needle strings below are built via concatenation (not written
    verbatim) so this test's own assertion text does not trip its own check ..."""
    own_text = Path(__file__).read_text()
    skip_call = "pytest" + ".skip"
    skipif_marker = "mark" + ".skipif"
    assert skip_call not in own_text, (...)
    assert skipif_marker not in own_text, (...)
```

**Module-docstring convention** (`:1-76`) — every `tests/` module opens with the MIT header,
then `Phase NN Plan NN -- <what>`, `Requirements: <IDs>`, `Decisions covered: <IDs>`, a rationale
block, an explicit **"executes in NO CI leg on this branch"** statement, the "self-contained path
resolution, NOT in conftest.py" note, and a numbered `Coverage:` list mapping each test function
to its decision/requirement. This convention is uniform across `tests/` and the planner should
budget for it.

---

## Shared Patterns

### The `# PY32_EXCLUDED:` contract and its reverse check
**Source:** `scripts/check_cmake_manifest.py` (module docstring `:2-100`, machinery `:110-270`).
**Apply to:** the AVR backend TU, the deleted `config.cpp`, the `rurp_config_utils.cpp` promotion.

Mandatory format, from the docstring `:43-62`:
```
    # PY32_EXCLUDED: <path> -- <reason>
```
> "The reason segment is MANDATORY -- an entry with a path but no stated reason is itself a
> violation, because an allow-list without required reasons degrades into a silencer."

The docstring at `:59-62` already names `src/rurp_config_utils.cpp` as *"Phase 126 per-platform
config backend split; THIS EXCLUSION WILL NEED REVISITING in Phase 126, it is not a permanent
exclusion."* — **the checker's own documentation must be updated alongside the manifest**, or the
docstring will describe a five-line set that no longer exists.

The regexes the plan must satisfy (`:164`, `:171`, `:161` region — verified):
```python
EXCLUDED_LINE_RE = re.compile(r"^\s*#\s*PY32_EXCLUDED:\s*(?P<rest>.*)$", re.MULTILINE)
EXCLUDED_RE      = re.compile(r"^(?P<path>\S+)\s*--\s*(?P<reason>.+?)\s*$")
SET_BLOCK_RE     = re.compile(r"set\(\s*(?P<name>\w+)\s+(?P<body>[^)]*)\)", re.DOTALL)
PATH_RE          = re.compile(r'"?(?P<path>[$\w{}/.\-]+\.(?:cpp|c|s|S))(?!\w)"?')
ENFORCED_LISTS   = {"FIRESTARTER_COMMON_SOURCES", "PY32_PLATFORM_SOURCES"}
EXEMPT_LISTS     = {"PY32_SDK_SOURCES"}
_SOURCE_EXTS     = (".cpp", ".c")
```

The reverse check, verbatim (`enumerate_tree_sources`) — **this is why the new AVR TU under
`src/boards/` is mandatorily covered and why a py32-only TU under `platform/` is invisible to
it (D-03's stated reason)**:
```python
def enumerate_tree_sources():
    """Return every .cpp/.c file under <root>/src, as repo-relative POSIX
    strings, for the reverse-omission check. Empty list if src/ is absent.
    """
    src_dir = _ROOT / "src"
    if not src_dir.is_dir():
        return []
    return sorted(
        str(p.relative_to(_ROOT)).replace(os.sep, "/")
        for p in src_dir.rglob("*")
        if p.is_file() and p.suffix in _SOURCE_EXTS
    )
```

Arming and exit taxonomy (`:126-141` + docstring `:64-78`): `ARMED = _PLATFORM_DIR.is_dir()`;
exit 0 = unarmed **or** clean; exit 1 = unresolvable source / unreasoned exclusion / uncovered
tree source / zero enforced sources resolved; exit 2 = manifest missing-or-unparseable, or an
unknown `set()` source-list name. The env seam is `FIRESTARTER_MANIFEST_ROOT`, read **once at
module import** — the paired pytest must invoke the script as a **real subprocess**, never an
in-process import with `monkeypatch.setenv`.

### AVR size measurement (strict equality, armed)
**Source:** `scripts/check_size_baseline.py::compare_avr` (`:183-211`).
**Apply to:** the measurement plan immediately after the AVR move, before any ARM work.
```python
def compare_avr(env, parsed, baseline):
    """... Asserts flash_used and ram_used equal the recorded values, and that
    flash_total/ram_total are unchanged (a changed total means the board or
    framework moved -- a finding, not a pass). ..."""
    rec = baseline["avr_targets"][env]
    ram_used, ram_total = parsed["RAM"]
    flash_used, flash_total = parsed["Flash"]
    failures = []
    if flash_used != rec["flash_used"]:
        failures.append(
            f"{env}: flash_used baseline={rec['flash_used']} observed={flash_used}"
        )
    ...
```
There is a **second** comparator, `compare_avr_policy_merge05` (`:214-266`), which implements the
A-5 *band* rule (`band = 0 if env == "leonardo" else MERGE05_UNO_CLASS_FLASH_BAND`, RAM strict on
all three). Selected by `--policy merge05` and canonically invoked with
`--baseline scripts/baseline/size_baseline_base01.json`. **A plan must name which comparator and
which baseline file it is invoking** — the default mode (strict equality against the live
`size_baseline.json`) and the MERGE-05 band mode against the frozen BASE-01 file are different
gates with different pass sets.

**Live figures, read from `scripts/baseline/size_baseline.json` this session** — these confirm
RESEARCH's numbers and correct CONTEXT's "2600 B":

| env | flash_used | flash_total | flash_free | ram_used | ram_total |
|---|---|---|---|---|---|
| uno | 23954 | 32256 | **8302** | 1573 | 2048 |
| uno328pb | 24004 | 32384 | **8380** | 1579 | 2048 |
| leonardo | 26016 | 28672 | **2656** | 2014 | 2560 |

The JSON's `meta.note` also carries the measurement procedure and its recorded trap verbatim:
`pio run -t clean -e <env>` then `pio run -e <env>`, one uninterrupted invocation per env,
extended timeout — *"a default 2-minute Bash timeout truncates the toolchain build mid-compile
and silently contaminates the measurement."* `meta.supersedes` states `size_baseline_base01.json`
(blob `b940c91655600a57ad7ef67cba723943af929daf`) is immutable.

### Native env pinning (nothing this phase does can move 141/17)
**Source:** `platformio.ini:163`, `:252`, `:290` — **all three verified identical**:
```ini
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>
```
Neither `src/rurp_config_utils.cpp` nor the new `src/boards/rurp_config_storage_eeprom.cpp`
matches this filter (the filter names `boards/rurp_serial_utils.cpp` by exact path, not
`boards/`). C-13 confirmed structurally. Env headers: `[env:native]` `:69`,
`[env:native_nodevtools]` `:166`, `[env:native_pinmap_provisional]` `:255`.

### Golden-trace and header-blast-radius discipline
**Source:** `include/rurp_shield.h` — 46 TUs including 14 native `host_stubs.cpp` files reach it.
**Apply to:** D-09. The new seam header must be included by exactly three TUs and must not be
reachable from `rurp_shield.h`. Enforceable with the negative-regex idiom above
(`test_vpp_seam_manual_on_every_board.py:412`) plus a `grep`-shaped includer census.

---

## No Analog Found

Files with no close match in the codebase — the planner should use RESEARCH.md's patterns
(§Pattern 2, §Code Examples) rather than substituting a wrong analog.

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `platform/py32f071/src/config_storage_dualslot.cpp` + local header | HAL-free algorithm core | transform + injected-primitive I/O | **No dependency-injected function-pointer-table pattern exists anywhere in this firmware.** `grep` finds no `typedef struct { bool (*...)(...); }` primitive-table idiom in `src/` or `platform/`. `src/rurp_vpp.cpp` is the closest *philosophical* precedent (dependency-free, compiled by both the host harness and the real build) but it has no injected dependencies at all — it is a refusal stub. RESEARCH §Pattern 2's `rurp_flash_primitives_t` sketch is the specification; there is nothing in-tree to copy its shape from. |
| CRC32 | transform | — | **No CRC32 exists in the tree.** The only checksum is the CRC8-CCITT `PROGMEM` table accessor in `src/boards/rurp_serial_utils.cpp` — wrong algorithm, AVR-shaped (`PROGMEM`), and inside a TU that IS compiled by the native envs. Confirmed not reusable, as CONTEXT Discretion states. |
| Hand-written fake `EEPROM.h` for the pytest harness | test shim | — | **No hand-written compile-shim header exists under `tests/`.** `find tests -name '*.h'` returns exactly four files, none of them a fake: `tests/golden/stable-expected.h` and `tests/golden/stable-baseline.h` (golden *comparison* artifacts for `test_golden_trace_identity.py`), and `tests/fixtures/{clean_orphan_provisional_consumed,planted_orphan_provisional_macro}/include/fixture_provisional.h` — which are inputs to a **textual** gate, not compiled by anything. The nearest transferable pattern is `_write_shim_tu`'s "write it fresh into `tmp_path` every call, never a committed fixture TU" (`test_vpp_seam_manual_on_every_board.py:158-176`), which is what the fake `EEPROM.h` should follow. C-12's conclusion holds and is now positively confirmed. |
| `platform/py32f071/CONFIG-STORAGE.md` | design doc | — | No vendored-design document exists under `platform/`. Only `platform/py32f071/README.md`. Format is fully specified by CONTEXT §Discretion + RESEARCH §Code Examples; no in-tree shape to copy. |

### Recorded Absences (things named upstream that are NOT in the live tree)

| Named as | Reality |
|---|---|
| `firestarter/platform/py32f071/PY32F071xB_FLASH.ld` (orchestrator prompt) | **Does not exist.** Real path: `platform/py32f071/linker/PY32F071xB_FLASH.ld`. |
| `platform/py32f071/PORTING.md` | **Absent from the live branch** (confirms A-6). Blob `4b1a441` only. |
| `py32f071_hal_flash.c` in `CMakeLists.txt` | **Absent.** `grep -c hal_flash` → `0`. Confirms C-3; D-08's "three edits" is four. |
| `tests/conftest.py` (or any pytest config file) | **Absent.** Per-module self-contained path resolution is the house rule, and the analog's docstring records it as a decision, not an omission. |
| Native Unity suites / `host_stubs.cpp` | **Present** under `test/native/avr/<suite>/` — noted only for the 141-cases / 17-suites pin. **This phase adds no Unity suite** (D-01), and `test/` is globbed into builds while `tests/` is PIO-invisible. Do not put a new `.py` under `test/`. |
| `firestarter_app/tests/scan_paths.py` `CROSS_REPO_TEST_PATHS` | Out of scope here (D-12); recorded only as Phase 127's obligation. **Not read this session** — no host-repo file is an analog for any file this phase creates. |

---

## Metadata

**Analog search scope:** `/workspaces/firestarter/{include,src,src/boards,platform/py32f071,platform/py32f071/{src,linker},scripts,tests,test}`, plus `platformio.ini` and `scripts/baseline/size_baseline.json`.
**Files read in full:** `tests/test_vpp_seam_manual_on_every_board.py`, `src/rurp_config_utils.cpp`, `platform/py32f071/src/config.cpp`, `platform/py32f071/linker/PY32F071xB_FLASH.ld`, `include/rurp_vpp.h`.
**Files read in targeted ranges:** `platform/py32f071/CMakeLists.txt:1-100`, `scripts/check_cmake_manifest.py:1-110` + `:110-270`, `scripts/check_size_baseline.py:183-280`, `include/rurp_shield.h` (3 ranges), `include/rurp_types.h:1-30`, `src/boards/{rurp_common,uno_rurp_shield,leonardo_rurp_shield}.cpp` heads, `platform/py32f071/src/{py32f071_rurp_shield,timing}.cpp` heads, `tests/test_pinmap_guard_fires.py` (grep-targeted).
**Read-only:** no source file was modified. This document is the only file written.
**Pattern extraction date:** 2026-07-31
