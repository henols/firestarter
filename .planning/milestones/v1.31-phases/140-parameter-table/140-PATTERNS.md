# Phase 140: Parameter Table - Pattern Map

**Mapped:** 2026-08-09
**Files analyzed:** 11 new + 1 modified (+ 2 doc updates)
**Analogs found:** 11 / 11 (9 exact / 2 role-match)
**Repos:** DUAL — `firestarter/` (9 artifacts) and `firestarter_app/` (2 artifacts)

> RESEARCH.md already located these analogs. This document is the copy-ready extraction:
> the actual bytes an executor pattern-matches against, with file:line anchors.
> Read `140-RESEARCH.md` § Common Pitfalls alongside this — every pattern below has a
> named failure mode attached.

---

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match |
|-------------------|------|------|-----------|----------------|-------|
| `include/eprom_params.h` | fw | model (type + const-data decl) | table lookup (read-only) | `include/rurp_platform_compat.h` (dependency-free header shape) + `src/json_parser.c:91` (struct + PROGMEM table typedef) | role-match |
| `src/proms/eprom_params.cpp` | fw | model (PROGMEM table + accessor) | table lookup (read-only) | `src/proms/not_implemented.cpp` (**include block — the warning-critical one**) + `src/json_parser.c:73-79,113-118` (storage + `pgm_read_ptr` scan) | exact (composite) |
| `test/native/avr/test_eprom_params_v131/host_stubs.cpp` | fw | test harness (link stub TU) | n/a (link-only) | `test/native/avr/test_not_implemented/host_stubs.cpp` | **exact** |
| `test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp` | fw | test (native Unity unit) | request-response (call → assert on handle) | `test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp` | exact role, simpler data flow |
| `platformio.ini` → `[env:native_params_v131]` | fw | config (build env) | n/a | `platformio.ini:293-329` `[env:native_trace_v131]` | **exact** |
| `tests/golden/eprom_params_citations.json` | fw | fixture (committed inventory) | file-I/O | `tests/golden/eprom_v131_trace_inventory.json` | **exact** |
| `tests/test_eprom_params_citations.py` | fw | test (committed gate) | file-I/O + re-parse | `tests/test_golden_trace_identity_eprom_v131.py` | **exact** |
| `tests/golden/protocol_branch_inventory.json` | fw | fixture (committed inventory) | file-I/O | `tests/golden/eprom_v131_trace_inventory.json` | **exact** |
| `tests/test_protocol_branch_inventory.py` | fw | test (committed gate, source scan) | file-I/O + regex scan | `tests/test_golden_trace_identity_eprom_v131.py` | exact role, source-scan locator is new |
| `tests/golden/chip_database_field_inventory.json` | app | fixture (committed inventory) | file-I/O | fw `tests/golden/eprom_v131_trace_inventory.json` (cross-repo shape copy) | role-match |
| `tests/test_chip_database_field_inventory.py` | app | test (committed gate) | file-I/O + aggregate | `tests/test_sdp_db_invariant.py` (DB load + counts + non-vacuity) + fw identity-pin shape | role-match (composite) |
| `doc/PROTOCOLS.md` §1.3-1.5, `CLAUDE.md` § Algorithm Handlers | fw | docs | n/a | — update in place, F-140-09 | n/a |

**Read-only reference (this phase must NOT modify):** `src/proms/eprom.cpp` — byte-unchanged (D-10).

---

## Pattern Assignments

### 1. `firestarter/src/proms/eprom_params.cpp` (model, table lookup)

**Analog A — include block + file skeleton:** `src/proms/not_implemented.cpp` (whole file, 19 lines).
This is the **only** `src/proms/*.cpp` that does not include `<Arduino.h>`, and it is the only one
absent from the 14-warnings-per-TU list in F-140-01. Copy this include discipline verbatim.

```c
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "not_implemented.h"
#include "firestarter.h"
#include "logging_id.h"
#include "messages.h"

void configure_not_implemented(firestarter_handle_t* handle) {
```
*(`src/proms/not_implemented.cpp:1-13` — note: no `#include <Arduino.h>`, no `rurp_shield.h`,
no `rurp_pinout.h`.)*

**Contrast — what NOT to copy** (`src/proms/eprom.cpp:8-17`, the house style that costs +14 warnings):

```c
#include "eprom.h"

#include <Arduino.h>          // ← THIS is the +14-warning line

#include "firestarter.h"
#include "logging_id.h"
#include "memory_utils.h"
#include "rurp_shield.h"
#include "rurp_pinout.h"
#include "operation_utils.h"
```

`eprom_params.cpp` needs **none** of these. Its only include is `"eprom_params.h"`.

**Analog B — PROGMEM const-table storage + access idiom:** `src/json_parser.c:67` and `:113-118`.

```c
const char key_mem_size[] PROGMEM = "memory-size";
/* ... */

typedef struct {
    PGM_P key;
    bool (*parser_func)(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
} key_parser_t;

static const key_parser_t key_parsers[] PROGMEM = {
    {key_mem_size, get_memory_size}, {key_address, get_address},         {key_flags, get_flags},
    {key_chip_id, get_chip_id},      {key_pin_count, get_pin_count},     {key_pulse_delay, get_delay},
    {key_vpp_mv, get_vpp_mv},        {key_algorithm, get_algorithm},
    /* Phase 44 — read-timing sweep knobs (RCA-01 causal proof, D-04) */
    {key_read_settling, get_read_settling},                              {key_read_strobe, get_read_strobe},
};
```
*(`src/json_parser.c:67,91-79`)*

The **scan-not-switch** access idiom — this is exactly the shape the accessor must take, because a
`switch` in the accessor would be the second selector TABLE-05 forbids:

```c
        for (size_t j = 0; j < sizeof(key_parsers) / sizeof(key_parsers[0]); j++) {
            PGM_P key = (PGM_P)pgm_read_ptr(&key_parsers[j].key);
            if (jsoneq_(json, key_token, key) == 0) {
                bool (*parser_func)(const char*, jsmntok_t*, int, firestarter_handle_t*) = (void*)pgm_read_ptr(&key_parsers[j].parser_func);
                parser_func(json, tokens, token_idx, handle);
```
*(`src/json_parser.c:301-305` — a linear `for` over `sizeof(x)/sizeof(x[0])` with `pgm_read_ptr`
on the member address. RESEARCH § Code Examples' `eprom_params_for()` is this shape with
`pgm_read_byte`.)*

**Fail-closed return (D-05) — copy the *invariant*, not the code:** `src/proms/memory.cpp:126-139`

```c
    // Named infeasibility arms (D-02): FWH and GAL/PLD — infeasible on RURP.
    if (handle->protocol == 0x11 || handle->protocol == 0x2A ||
        handle->protocol == 0x2B || handle->protocol == 0x2C) {
        configure_not_implemented(handle);
        return;
    }

    // Generic fail-closed guard: every remaining protocol value — including
    // protocol == 0 — is unrecognized and reaches not-implemented. Trusts
    // only handle->protocol end to end; no backward-compat fallback axis
    // remains (T-64-01, Phase 105 protocol-only dispatch).
    configure_not_implemented(handle);
}
```
The transferable property: **an unrecognised protocol reaches a terminal refusal, never a default
row.** `eprom_params_for()` returns `NULL`; it never returns `&EPROM_PARAMS[0]`.

**Protocol tokens** (`include/proto_constants.h:18-29`) — use these in comments/keys; the label IS
the number, no new naming layer:

```c
#define PROTO_EPROM_28PIN 0x07
#define PROTO_EPROM_32PIN 0x08
#define PROTO_EPROM_24PIN 0x0B
```

---

### 2. `firestarter/include/eprom_params.h` (model, type + extern decl)

**Analog — dependency-free header + include-guard shape:** `include/rurp_platform_compat.h:8-13,84-86`

```c
#ifndef __RURP_PLATFORM_COMPAT_H__
#define __RURP_PLATFORM_COMPAT_H__

#include <stdint.h>
#include <stddef.h>
#include <string.h>
```
…
```c
#endif /* __AVR__ */

#endif /* __RURP_PLATFORM_COMPAT_H__ */
```

This is also the header that supplies the host-side `PROGMEM` / `pgm_read_*` shims, so including it
is what makes the new header compile identically on AVR and on `platform = native`:

```c
#if defined(__AVR__)
#include <avr/pgmspace.h>
#else

#ifndef PROGMEM
#define PROGMEM
#endif
/* ... */
#ifndef pgm_read_byte
#define pgm_read_byte(address) (*(const uint8_t*)(address))
#endif
```
*(`include/rurp_platform_compat.h:19-37`)*

**`extern "C"` wrapper idiom for a C-callable declaration in a `.h` consumed by C++ TUs:**
`include/memory_utils.h:29-31`

```c
#ifdef __cplusplus
}
#endif
```

**Struct field order is load-bearing** (Pitfall 2): largest-first
(`uint32_t, uint32_t, uint8_t×4`) gives `sizeof == 12` on **both** avr-gcc (1-byte alignment) and
x86-64. The worked header in `140-RESEARCH.md` § Code Examples is the recommended literal starting
point.

---

### 3. `firestarter/test/native/avr/test_eprom_params_v131/host_stubs.cpp` (test harness)

**Analog:** `test/native/avr/test_not_implemented/host_stubs.cpp` — **whole file, exact copy shape.**
Pitfall 6 says the TABLE-03 suite needs *none* of the three opt-in recorder layers, so the pure
pass-through variant is correct.

```c
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase 64 — host stub TU for the test_not_implemented suite.
 * Phase 6 WR-06 — shared stub body lives in ../_shared/host_stubs_common.inc.
 *
 * ...
 * Suite-specific extensions: NONE — test_not_implemented uses the canonical
 * default for every stub, so this TU is a pure pass-through to the shared
 * include.
 *
 * Scope: only compiled into [env:native] via PIO's automatic discovery of
 * files under test/. Production builds (env:uno, env:leonardo) never see
 * this file because their src_filter excludes test/.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

#include "../_shared/host_stubs_common.inc"
```
*(`test/native/avr/test_not_implemented/host_stubs.cpp:1-36`, verbatim.)*

**Do NOT copy** `test_trace_eprom_v131/host_stubs.cpp` (three opt-in guards + a stateful read-back
model) or `test_val_eprom/host_stubs.cpp` (`HOST_STUBS_RECORD_BUS` + `HOST_STUBS_CUSTOM_HW_REVISION`).
For reference, the opt-in guard discipline they demonstrate — **every guard reads at include time,
so it must be `#define`d BEFORE the `#include`**:

```c
/* Activate recording bus stub (opt-IN). */
#define HOST_STUBS_RECORD_BUS
/* Opt out of default hw-revision stub so we can return non-REVISION_0. */
#define HOST_STUBS_CUSTOM_HW_REVISION

#include "../_shared/host_stubs_common.inc"
```
*(`test/native/avr/test_val_eprom/host_stubs.cpp:30-38`. The available guards are documented at
`test/native/avr/_shared/host_stubs_common.inc:22-32` + `:50-60`.)*

---

### 4. `firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp` (native unit test)

**Analog:** `test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp`

**Include block** (`:34-47`):

```cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <string.h>
#include <stdio.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

#include "../_shared/eprom_v131_expected.h"

using namespace fakeit;
```

> `<Arduino.h>` in the **test** TU is fine — Pitfall 1's watermark constraint is about
> `src/proms/*.cpp`, which `build_src_filter = +<proms/>` compiles into `native` and
> `native_nodevtools` too. Test TUs under `test/native/avr/test_eprom_params_v131/` are compiled
> **only** by the env whose `test_filter` names them.

**`setUp` / `tearDown` — the ArduinoFake preamble** (`:72-100`, trimmed to what the params suite needs):

```cpp
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();

    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysDo([](unsigned int us) { /* ... */ });
    When(Method(ArduinoFake(), delay)).AlwaysDo([](unsigned long ms) { /* ... */ });
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    When(Method(ArduinoFake(), micros)).AlwaysReturn(0);
    /* ... recorder resets ... */
}

void tearDown(void) {}
```

`delay`/`delayMicroseconds` are **defined by ArduinoFake, not stubbed in the shared `.inc`** — every
suite that can reach them mocks them in its own `setUp()` (`:78-85` says so explicitly). The params
suite calls `configure_memory`/`configure_eprom` only, which reaches no `delay()`, but an
`.AlwaysReturn()` stub is cheap insurance.

**Fresh-handle factory (Pitfall 4 — the global handle never resets `pulse_delay`)** (`:215-229`):

```cpp
static firestarter_handle_t make_v131_handle(uint32_t protocol, uint8_t pins, uint32_t mem_size,
                                              uint32_t pulse_delay_us, const bus_config_t& bus_config) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = 0;
    h.vpp_mv = 0;
    h.pins = pins;
    h.mem_size = mem_size;
    h.pulse_delay = pulse_delay_us;
    h.bus_config = bus_config;
    h.ctrl_flags = FLAG_SKIP_BLANK_CHECK | FLAG_SKIP_ERASE;
    return h;
}
```

**Unity `main()` shape** (`:378-395`) — a hand-written `main` with explicit `RUN_TEST` calls, not
auto-discovery:

```cpp
int main(int argc, char** argv) {
    /* ... */
    UNITY_BEGIN();
    RUN_TEST(test_smoke_setup_leaves_both_recorders_clean);
    /* ... */
    RUN_TEST(test_protocol_0x07_am27c512_capture_is_sound_and_deterministic);
    /* ... */
    return UNITY_END();
}
```

Consequence: **a `void test_*(void)` function that is not named in `main()` never runs and never
fails.** The plan's verification must compare the reported case count against the number of
`RUN_TEST` lines.

The full worked suite (6 fallback cases + 2 row-resolution cases) is in `140-RESEARCH.md`
§ Code Examples "The TABLE-03 fallback test".

---

### 5. `firestarter/platformio.ini` — `[env:native_params_v131]` (config)

**Analog:** `platformio.ini:293-329` `[env:native_trace_v131]` — copy wholesale **including the
comment discipline**. The comment block is not decoration; it is what stops a later phase folding
this env into a pinned one.

```ini
[env:native_trace_v131]
; Phase 138 Plan 03 (PREP-03, D-01/D-02/D-04): a FOURTH native environment,
; whose sole purpose is to compile+run test_trace_eprom_v131 -- the suite
; that captures the pre-change 27C write loop's merged strobe+timing stream
; for all three protocols (0x07/0x08/0x0B), before any v1.31 code moves.
;
; HARD CONSTRAINT -- MUST NEVER be folded into [env:native] or
; [env:native_nodevtools]'s test_filter. Both of those are pinned at exactly
; the same 17-entry test_filter list and a live gate (check_size_baseline.py's
; compare_native) asserts 141 cases / 17 suites on BOTH of them by exact
; count. This env's test_filter therefore names ONLY its own new suite (1
; entry, not 18), and this env is NOT added to default_envs (:16) -- pio run
; would try to link a main()-less target ("undefined reference to main").
;
; FURTHER CAVEAT (measured, Phase 138 Plan 03 RESEARCH): do not feed
; "native_trace_v131" to either live gate.
;   - check_size_baseline.py hardcodes NATIVE_ENVS = ("native",
;     "native_nodevtools") and compare_native does a bare
;     baseline["native_envs"][env] lookup -- an unknown env name raises an
;     UNCAUGHT KeyError (exit 1, a false regression signal), not the
;     documented exit-2 "tool/format failure". Recorded as finding F-138-05
;     (owner henols), not fixed here.
;   - check_build_warnings.py handles this correctly (exit 2, clean message)
;     but there is still no baseline entry for this env to compare against.
; This env's own counts and warnings are recorded ONLY in the new
; scripts/baseline/size_baseline_v131.json, never asserted by either gate.
platform = native
test_framework = unity
test_filter =
	native/avr/test_trace_eprom_v131
build_flags =
	${env:native.build_flags}
	-I test/native/avr/test_trace_eprom_v131
lib_deps =
	fabiobatsilva/ArduinoFake@^0.4.0
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>
test_build_src = yes
```
*(`platformio.ini:293-329`, verbatim. Note: **tab**-indented continuation lines, not spaces.)*

`${env:native.build_flags}` inherits `-std=gnu++17`, `-I include`, all 17 existing suite `-I`
entries and `-D RURP_BOARD_NAME=\"native\"` (`platformio.ini:120-141`) — so the new
`include/eprom_params.h` is already on the include path via `-I include`.

**The two lists that must NOT be touched** (`platformio.ini:102-119` and `:120-141`) are
`[env:native]`'s `test_filter` (17 entries) and its `-I` list. `[env:native_nodevtools]` mirrors
them (`:166+`); `CLAUDE.md` § "Reuse pattern for future native tests" says a new suite normally goes
into **both** — D-11 deliberately overrides that here.

**Also do not touch** `platformio.ini:11-16`:

```ini
[platformio]
; Phase 20 E2E-04: `pio run` (the firmware build) MUST NOT attempt to link the
; [env:native] target — it is a test-only environment with no main(), so
; linking fails with "undefined reference to main". Constrain default_envs
; to the AVR targets; `pio test -e native` still picks up native explicitly.
default_envs = uno, uno328pb, leonardo
```

The third-env precedent (`[env:native_pinmap_provisional]`, `:255-291`) is a second worked instance
of the same shape if a tiebreak is needed.

---

### 6. `firestarter/tests/test_eprom_params_citations.py` and `tests/test_protocol_branch_inventory.py` (committed gates)

**Analog:** `tests/test_golden_trace_identity_eprom_v131.py` — the in-milestone standalone-pytest gate.
**Copy the pattern, not the file** (its own docstring, `:10-13`, explains why a shared-helper
refactor disarms the self-scan).

**Why this shape and not `scripts/check_*.py`:** `tests/test_checker_convention.py:129-130` pins

```python
FLOOR = 6
FIXTURE_FLOOR = 15
```

and globs `scripts/check_*.py` non-recursively, requiring per checker: a paired
`tests/test_check_<X>.py`, ≥1 `tests/fixtures/planted_<X>*`, the checker's exact filename inside the
test module, a `returncode != 0` assertion, **and** both floors raised in the same commit. A pytest
module under `tests/` is outside that glob and incurs none of it.

**Path resolution — self-contained, no `conftest.py`** (`:64-82`):

```python
"""
Self-contained path resolution below -- NOT in conftest.py (firestarter/
tests/ has no conftest.py anywhere in the repo; a recorded house-rule
pattern decision, not an omission). Stdlib and pytest only.
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_FIXTURE_PATH = "test/native/avr/_shared/eprom_v131_expected.h"
_INVENTORY_JSON = _HERE / "golden" / "eprom_v131_trace_inventory.json"
_CONSUMERS = (
    _REPO_ROOT / "test" / "native" / "avr" / "test_trace_eprom_v131" / "test_trace_eprom_v131.cpp",
)
```

> Contrast with the D-15 trap: `check_permitted_claims.py`'s `_HERE` resolved to the *checker's own*
> phase directory. Here `_HERE` is `firestarter/tests/` and `_REPO_ROOT` is the firmware repo root —
> correct **because the module lives beside what it checks**. Confirmed there is still no
> `conftest.py` anywhere under `firestarter/tests/`.

**Fail-closed `git` resolution — no skip path, ever** (`:91-128`):

```python
def _resolve_git():
    git_bin = shutil.which(os.environ.get("GIT", "git"))
    assert git_bin is not None, (
        "git not found on PATH (checked $GIT, falling back to 'git'). This "
        "must FAIL the suite, never be silently skipped ..."
    )
    return git_bin


def _git(*args):
    git_bin = _resolve_git()
    result = subprocess.run(
        [git_bin, *args],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"git {' '.join(args)} failed (exit {result.returncode}).\n"
        f"stderr:\n{result.stderr}"
    )
    return result.stdout.strip()
```

**Independent re-parse (never trust the JSON's own derivation)** (`:131-152`):

```python
def _parse_arrays(text):
    """Re-derive the ordered (name, entries) pairs from ... raw text,
    independently of the committed inventory JSON. Strips C-style
    comments first so a commented-out entry -- or a provenance banner's prose
    -- can never inflate a count."""
    arrays = []
    for m in _ARRAY_DECL_RE.finditer(text):
        name = m.group(1)
        body = m.group(2)
        body_nc = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
        body_nc = re.sub(r"//[^\n]*", "", body_nc)
        entries = _ENTRY_RE.findall(body_nc)
        arrays.append((name, len(entries)))
    return arrays
```

with the locator regexes at `:84-88`:

```python
_ARRAY_DECL_RE = re.compile(
    r"static const v131_trace_entry_t\s+(\w+)\[\]\s*=\s*\{(.*?)\};",
    re.DOTALL,
)
_ENTRY_RE = re.compile(r"\{[^{}]*\}")
```

**The six-test shape** — map 1:1 onto both new gates:

| # | Test (`:155-244`) | For `test_eprom_params_citations.py` | For `test_protocol_branch_inventory.py` |
|---|---|---|---|
| 1 | `test_blob_sha_matches_the_recorded_inventory` — `git rev-parse HEAD:<path>` vs `meta.blob_sha` | pin `src/proms/eprom_params.cpp` | pin `src/proms/eprom.cpp` (**doubles as the D-10 byte-unchanged proof**) |
| 2 | `test_array_names_match_the_recorded_inventory` — ordered names, live parse vs JSON | struct field names == the frozen six, in order | branch-site list == the pinned 4 sites |
| 3 | `test_array_entry_counts_match_the_recorded_inventory` — positional, **names the FIRST divergence** | per-row cell count (3 rows × 6 = 18) | per-site keyed-on class + allowlist reason |
| 4 | `test_inventory_is_non_vacuous` — `>= 3` items, every count `>= 1` | `cells_scanned == 18` and `> 0` | `sites_scanned >= 4`, files scanned `> 0` |
| 5 | `test_consuming_suites_still_include_the_fixture` — the artifact stays load-bearing | the citation JSON is referenced by the `.cpp`'s header comment | the `.cpp` path resolves and is non-empty |
| 6 | `test_git_is_required_not_optional` — **self-scan for skip bypasses** | copy verbatim | copy verbatim |

Test 3's "first divergence" discipline, verbatim (`:177-195`):

```python
    n = min(len(recorded), len(live))
    for i in range(n):
        rec_name, rec_entries = recorded[i]
        live_name, live_entries = live[i]
        if rec_name != live_name or rec_entries != live_entries:
            raise AssertionError(
                f"first divergence at index {i} -- "
                f"recorded={{'name': {rec_name!r}, 'entries': {rec_entries}}}, "
                f"live={{'name': {live_name!r}, 'entries': {live_entries}}}"
            )
    assert len(recorded) == len(live), (
        f"array count diverged after {n} matching entries -- "
        f"recorded_count={len(recorded)} live_count={len(live)}"
    )
```

Test 6's self-scan, verbatim (`:222-244`) — this is the D-15 non-vacuity mechanism and it is
**startswith()-based specifically so its own prose never self-matches**:

```python
def test_git_is_required_not_optional():
    this_source = Path(__file__).read_text()
    for line in this_source.splitlines():
        stripped = line.strip()
        assert not stripped.startswith("pytest.skip"), (
            f"found a skip-bypass call at: {line!r} -- git absence must "
            "FAIL this suite, never take this bypass."
        )
        assert not stripped.startswith("@pytest.mark.skipif"), (
            f"found a skip-marker decorator at: {line!r} -- git "
            "absence must FAIL this suite, never skip it."
        )
```

**D-13 locator warning (Pitfall 5) — this is the one place the analog does NOT transfer.**
`eprom.cpp` does **not** include `proto_constants.h` (verified: its include block is
`eprom.h`, `<Arduino.h>`, `firestarter.h`, `logging_id.h`, `memory_utils.h`, `rurp_shield.h`,
`rurp_pinout.h`, `operation_utils.h` — `eprom.cpp:8-17`). The three protocol comparisons spell the
value as **raw hex**. A locator matching only `PROTO_EPROM_24PIN` finds nothing today; one matching
only `0x0B` breaks when Phase 142 adopts the token. Match **both**.

---

### 7. `firestarter/tests/golden/*.json` (committed inventory fixtures)

**Analog:** `tests/golden/eprom_v131_trace_inventory.json` — whole file, 23 lines. The `meta` block's
key set is the pattern: provenance + *why two independent checks exist* + *how to update* + *what it
is frozen for*.

```json
{
  "meta": {
    "source": "test/native/avr/_shared/eprom_v131_expected.h",
    "recorded_by": "Phase 138 Plan 05",
    "requirement": "PREP-03",
    "blob_sha": "ca3e09f164e6e1c541ecb63d15bbebf5bce41d70",
    "recorded_at_head": "3dad6450e277692eb4374de1512d69eaa17709de",
    "why_two_checks": "A whole-file blob match alone cannot distinguish 'unchanged' from 'an array deleted together with the assertions that consumed it' ...",
    "how_to_update": "If this file legitimately changes, re-derive this inventory from the file with an independent parse (never hand-edit the numbers) AND state in the commit message which array changed and why -- never edit this JSON merely to make a surprise disappear.",
    "frozen_for": "Phase 144 / TEST-06 -- ...",
    "measured_entry_counts": { "0x07": { "strobes": 142, "timings": 56, "merged": 198 } },
    "overflow_observed": "false for both recorders on every one of the three captures ..."
  },
  "arrays": [
    { "name": "EPROM_V131_TRACE_PROTO_07", "entries": 198 },
    { "name": "EPROM_V131_TRACE_PROTO_08", "entries": 221 },
    { "name": "EPROM_V131_TRACE_PROTO_0B", "entries": 201 }
  ]
}
```
*(`tests/golden/eprom_v131_trace_inventory.json:1-23`, abridged at the long strings.)*

For `eprom_params_citations.json`, `meta` additionally carries the datasheet-recovery command
(Open Question 3 / F-140-08: **no datasheet corpus resolves on this branch**, so citations are
self-describing and `meta` records how to obtain the PDFs):

```bash
git -C firestarter show \
  v1.16-protocol-first-architecture-rebuild:datasheets/0x08-EPROM-QUICK/AM27C020.pdf > AM27C020.pdf
```
*(`140-RESEARCH.md` § Code Examples.)*

---

### 8. `firestarter_app/tests/test_chip_database_field_inventory.py` (committed gate, DB half)

**Analog A — DB path resolution + shape traversal + non-vacuity:** `tests/test_sdp_db_invariant.py:68-99`

```python
import json
from pathlib import Path

from firestarter.sdp_capability import sdp_capability_for_entry

# Absolute path to the firestarter_app directory (independent of cwd)
_FA_DIR = Path(__file__).parent.parent
_DB_FILE = _FA_DIR / "firestarter" / "data" / "chip_database.json"

# Upstream protocol_id / firmware dispatch key for configure_eeprom28c (0x0D).
_ALGORITHM_0X0D = 13


def _select_0x0d_chips(db: dict) -> list[tuple[str, dict]]:
    """Select every (manufacturer, chip) pair with programming.algorithm == 13.

    The DB shape is {manufacturer: [chip, ...]}, and the fields live in a
    nested "programming" object. A top-level scan on db (rather than this
    nested per-chip access) finds nothing and would make every downstream
    assertion pass vacuously.
    """
    selected = []
    for _mfr, chips in db.items():
        for chip in chips:
            if chip["programming"]["algorithm"] == _ALGORITHM_0X0D:
                selected.append((_mfr, chip))
    return selected
```

**The DB shape is `{manufacturer: [chip, ...]}`** — verified in-session: 59 top-level manufacturer
keys, each a **list** of chip objects. A chip object:

```json
{
 "electrical": { "pin_count": 32, "size_bytes": 262144, "type": "EEPROM",
                 "vcc": "5V", "vdd": "5V", "vpp": "12V", "vpp_mv": 12000 },
 "part_number": "M8720",
 "pinout": "DIP32_27C020",
 "programming": { "algorithm": 8, "chip_id_check": false,
                  "chip_id_value": "0x00000000", "infoic_page_size_raw": 0,
                  "protect_off_before": false, "protect_on_after": false,
                  "pulse_duration": "20 us" },
 "support_status": "supported"
}
```

A `for key in db:` loop over the top level enumerates **manufacturers**, not chips — the
field-inventory gate must descend two levels, exactly as `_select_0x0d_chips` does, or it counts
zero fields and passes vacuously.

**Count-assertion + explain-the-consequence message shape** (`:267-284`):

```python
def test_exactly_84_algorithm_0x0d_entries() -> None:
    """TRACE-05 / CLOSE-01: exactly 84 chip_database.json entries have
    programming.algorithm == 13.

    A count change means a chip was added to or removed from the 0x0D
    bucket and every trace-coverage assumption in this milestone needs
    re-checking. ...
    """
    db = json.loads(_DB_FILE.read_text(encoding="utf-8"))
    selected = _select_0x0d_chips(db)
    assert len(selected) == 84, (
        "TRACE-05/CLOSE-01: expected exactly 84 chip_database.json entries "
        f"with programming.algorithm == 13, found {len(selected)}. A count "
        "change means a chip was added to or removed from the 0x0D bucket "
        "-- re-check every Phase 116+ trace-coverage assumption before "
        "proceeding."
    )
```

This is the direct model for the "27C protocol counts: `algorithm` 7 → 170, 8 → 127, 11 → 32" row of
the frozen inventory.

**Analog B — the committed-inventory bijection** has no app-side precedent: `firestarter_app/tests/golden/`
holds only `stable-baseline.py`, `stable-expected.py` and `v1.3-COVERAGE-MATRIX.md` (no JSON). Copy
the firmware's `tests/golden/*.json` + six-test shape across the repo boundary (§6 and §7 above).
The nearest app-side golden idiom is `tests/test_audit_coverage_matrix.py:600-643` (regenerate →
byte-compare against `tests/golden/`), which is the *generator* variant, not the *inventory* variant.

**Corroboration, NOT the gate:** `tests/test_diff_db_gate.py:50-68` drives `tools/diff_db.py` by
subprocess:

```python
        firestarter_app_dir = Path(__file__).resolve().parent.parent

        result = subprocess.run(
            [sys.executable, "tools/diff_db.py"],
            cwd=str(firestarter_app_dir),
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, (
            f"diff_db.py exit code {result.returncode} (expected 0); "
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
```

F-140-10: `diff_db.py`'s `_diff_field_paths` already unions both key sets and would see a new
field — but it compares against `tools/baseline/chip_database.baseline.json`, which regenerating
silences. The TABLE-05 gate must be the **non-silenceable** half; do not delegate to `diff_db.py`.

**App-repo constraints the new module must satisfy** (verified this session):

| Constraint | Source | Consequence |
|---|---|---|
| `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` in CI | `.github/workflows/ci.yml:81,84` | the new module **is** linted and formatted-checked (unlike anything in `tools/`, F-140-12) |
| `target-version = "py39"`, `line-length = 88` | `pyproject.toml:110-111` | py3.9-compatible syntax; 88-col |
| `addopts = "-ra -q"`, `testpaths = ["tests"]` | `pyproject.toml:105-107` | run the baseline with `-o addopts=""` to see the count line |
| `pytest tests/ --cov=firestarter --cov-fail-under=70` | `ci.yml:90` | coverage measures `firestarter/` only; a `tests/`-only addition cannot move it |
| `collect_ignore` **is armed** in `tests/conftest.py:76-102` | conftest | it only ignores `test_pyusb_api_surface.py` — but Assumption A6 still applies: assert the new module appears in `pytest --collect-only` |

---

## Shared Patterns

### S1 — File header block (both repos, C/C++ and Python)

```c
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * Phase <N> Plan <NN> (<REQ-IDs>, <D-NN>) — <one-line purpose>
 * ...
 */
```
```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase <N> Plan <NN> -- <requirement> ...

Requirements: <IDs>

Defect class this closes: <the specific thing a count/status assertion cannot see>

Coverage:
  1. <test name> -- <what it asserts>
  ...
"""
```
**Apply to:** every new file. The Python variant's `Defect class this closes:` +
numbered `Coverage:` list (`tests/test_golden_trace_identity_eprom_v131.py:1-67`) is the house shape
for a gate module and is what makes the planted-failure obligation legible.

### S2 — PROGMEM const table + `pgm_read_*` access
**Source:** `src/json_parser.c:67`, `:113-118`
**Apply to:** `src/proms/eprom_params.cpp`
The array is `static const … PROGMEM`; every field read goes through `pgm_read_byte` /
`pgm_read_word` / `pgm_read_dword` / `pgm_read_ptr` on `&array[i].member`. Never dereference
directly — it compiles and silently reads RAM garbage on AVR.

### S3 — Fail-closed on an unrecognised value, zero hardware side effects
**Source:** `src/proms/memory.cpp:126-139`; codified in `firestarter/CLAUDE.md` § "Fail-closed invariant"
**Apply to:** `eprom_params_for()` (returns `NULL`, D-05)
Never a default row. `configure_not_implemented` (`src/proms/not_implemented.cpp:13-19`) shows the
terminal form: NULL out all three operation pointers, log an ID-only error, set
`RESPONSE_CODE_ERROR`.

### S4 — `messages.h` is codegen-generated and ID-only
**Source:** memory note + `firestarter/src/proms/not_implemented.cpp:11,17` (`LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, …)`)
**Apply to:** any new error message this phase might want for the NULL row.
Authored in the **meta** repo's `messages.toml` and regenerated — never hand-edited in
`firestarter/include/messages.h`. Phase 140 most likely needs **no** new message (nothing in `src/`
calls the accessor yet, D-10).

### S5 — Positive-allowlist test plumbing
**Source:** `platformio.ini:102-141` (`[env:native]`), `:293-329` (`[env:native_trace_v131]`);
`firestarter/CLAUDE.md` § "Reuse pattern for future native tests" (v1.22 Phase 119 D-04 correction)
**Apply to:** the fifth env.
A suite directory is invisible to `pio test` until its path is in `test_filter`, and its headers are
unreachable until `-I test/native/avr/<dirname>` is in `build_flags`. **Both** lists. In the new
env only — never in `[env:native]` / `[env:native_nodevtools]`.

### S6 — Committed-inventory gate (two independent readings)
**Source:** `tests/test_golden_trace_identity_eprom_v131.py` + `tests/golden/eprom_v131_trace_inventory.json`
**Apply to:** all three new gates.
The invariant: the artifact and the recorded expectation are read by **two separate mechanisms** and
compared, so a change to either alone is visible. Blob SHA (via `git`) + independent re-parse +
non-vacuity floor + consumer-still-references + skip-bypass self-scan.

### S7 — CI legs that will actually run the new gates
**Source:** `firestarter/.github/workflows/build.yml:161`, `beta-build.yml:134` (`pytest tests/ -v`);
`firestarter_app/.github/workflows/ci.yml:90` (`pytest tests/ …`)
**Apply to:** gate placement (confirms D-12/OQ4).
**`fetch-depth: 0` is already set and is load-bearing** for any gate that shells out to `git`
(`build.yml:70-86` documents why: the history gates fail with "does not resolve to a commit" under a
depth-1 clone). A blob-SHA pin only needs HEAD's tree, but stay inside the existing contract.
**Neither firmware workflow runs any `pio test` env beyond `native` and `native_nodevtools`**
(F-140-11) — `native_params_v131` is a local, run-by-name obligation.

### S8 — Native-suite handle hygiene
**Source:** `test_trace_eprom_v131.cpp:215-229`; root cause at `src/json_parser.c:164-278`
**Apply to:** the TABLE-03 suite.
`json_parse` resets `address`, `ctrl_flags`, four `bus_config` fields and `chip_id` — **not**
`pulse_delay`, `protocol`, `mem_size`, `vpp_mv` or `pins`:

```c
int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle) {
    handle->address = 0;
    handle->ctrl_flags = 0;
    handle->bus_config.rw_line = 0xFF;
    handle->bus_config.vpp_line = 0xFF;
    handle->bus_config.address_lines[0] = 0xFF;
    handle->bus_config.address_mask = 0;
    handle->bus_config.static_high_mask = 0;
    handle->chip_id = 0;
```
So every case builds `firestarter_handle_t h = {};` fresh, and every positive fallback case is
paired with a `pulse_delay = 777` negative control.

---

## Read-Only Reference — `src/proms/eprom.cpp` (byte-unchanged, D-10)

These excerpts are what the new table **describes without duplicating**, and what the D-13 gate must
pin. Do not edit them in this phase.

**The `pulse_delay == 0` fallback (D-03: STAYS here; TABLE-03's test target)** — `eprom.cpp:69-76`:

```c
    // Set default pulse_delay from protocol when Python doesn't supply one
    if (handle->pulse_delay == 0) {
        switch (handle->protocol) {
            case 0x08: handle->pulse_delay = 100;  break;  // EPROM_QUICK: 100µs
            case 0x0B: handle->pulse_delay = 500;  break;  // EPROM_LEGACY: 500µs
            default:   handle->pulse_delay = 1000; break;  // EPROM_STD: 1ms
        }
    }
}
```
Note `default:` — `0x07` reaches 1000 µs through the default arm, **not** a `case 0x07:`. A gate
locator that requires three `case` labels finds two.

**The retry-escalation loop — NOT an overprogram pulse** (Phase 141's, LOOP-02) — `eprom.cpp:159-179`:

```c
    int mismatch = 0;
    int retries = 0;
    uint32_t org_delay = handle->pulse_delay;

    for (int w = 0; w < NUMBER_OF_RETRIES; w++) {
        program_mismatched_bytes(handle, mismatch_bitmask);

        mismatch = verify_and_update_mask(handle, mismatch_bitmask);

        if (!mismatch) {
            if (retries > 0) {
                LOG_INFO_ID_U8(MSG_INFO_RETRIES, (uint8_t)retries);
            }
            handle->pulse_delay = org_delay;
            return;
        }

        retries = w + 1;
        handle->pulse_delay = org_delay + (org_delay * retries / NUMBER_OF_RETRIES);
        LOG_DEBUG_ID_SUB_U16_U16(DBG_PULSE_DELAY_MISMATCH, (uint16_t)org_delay, (uint16_t)handle->pulse_delay);
    }
```
with `#define NUMBER_OF_RETRIES 20` at `:20`. This is *adaptive pulse-width growth on retry*, not an
Intel 3N margin pulse — the basis for the locked `0x07 overprogram_factor = 0` decision. Note the
asymmetry the D-13/Phase-141 record should carry: `org_delay` is restored on the success path
(`:172`) but **not** on the retry-exhausted failure path (`:181-192`).

**The four protocol/handle branch sites the D-13 inventory must pin** (measured, Pitfall 5):

| Site | Predicate (verbatim) | Keyed on | Class |
|---|---|---|---|
| `eprom.cpp:71` | `switch (handle->protocol)` | `protocol` | **algorithm selector** (stays, D-03) |
| `eprom.cpp:145` | `if (handle->protocol == 0x0B \|\| is_flag_set(FLAG_VPE_AS_VPP))` | `protocol` **+ `ctrl_flags`** | VPP route — **allowlist** (Phase 142) |
| `eprom.cpp:218` | `if (handle->protocol == 0x0B \|\| is_flag_set(FLAG_VPE_AS_VPP))` | `protocol` **+ `ctrl_flags`** | VPP route — **allowlist** (Phase 142) |
| `eprom.cpp:320` | `if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle))` | `pins` **+ `bus_config.vpp_line`** | pin routing — **allowlist** (pre-existing) |

The `:145` site in full (`eprom.cpp:143-153`), showing the two VPP routes the table's `vpp_path`
column names abstractly:

```c
void eprom_write_execute(firestarter_handle_t* handle) {
    if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0) {
        if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {
            // EPROM_LEGACY: direct VPE path — no CTRL_VPP_VPE_DROP_ENABLE dropping resistor
            handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
        } else {
            // EPROM_STD / EPROM_QUICK: CTRL_VPP_VPE_DROP_ENABLE dropping path for precise VPP
            handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1);
        }
        delay(500);
    }
```

and the `:320` site with its predicate's definition (`include/memory_utils.h:24-28`):

```c
static inline bool using_p1_as_vpp(const firestarter_handle_t* handle) {
    return (handle->pins == 32 && handle->bus_config.vpp_line == VPP_P1_32_DIP) ||
           (handle->pins == 28 && handle->bus_config.vpp_line == VPP_P1_28_DIP) ||
           (handle->pins == 24 && handle->bus_config.vpp_line == VPP_P21_24_DIP);
}
```
```c
void eprom_internal_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle)) {
        bit &= ~CTRL_VPE_ENABLE;
        bit |= CTRL_VPP_P1_ENABLE;
    }
    ep_set_control_register(handle, bit, state);
}
```
*(`src/proms/eprom.cpp:318-325`)*

D-13's stated rule ("a branch keyed on **any other** handle field fails the gate") hits the last
three. **Without a reasoned allowlist naming all three, the gate is RED on arrival and can never be
seen to pass** — which triggers D-15 trap (2), "a pre-authored gate leg can be unreachable".

---

## No Analog Found

| File / Element | Role | Why no analog |
|---|---|---|
| `firestarter_app/tests/golden/chip_database_field_inventory.json` | fixture | `firestarter_app/tests/golden/` contains **no JSON** today (only `stable-baseline.py`, `stable-expected.py`, `v1.3-COVERAGE-MATRIX.md`). Copy the firmware's `tests/golden/*.json` `meta`-block shape across the repo boundary. |
| The D-13 branch-site **locator** (regex over `src/proms/eprom.cpp`) | gate internals | No existing firmware gate parses C control flow. The nearest in-repo idiom is `_parse_arrays`'s comment-stripping declaration regex (`test_golden_trace_identity_eprom_v131.py:131-144`) — reuse the comment-stripping discipline; the pattern itself is new. |
| The TABLE-04 citation **schema** (family + part + doc number + revision + section + scope clause) | data format | No in-tree precedent. Format is Claude's discretion; the gate's bijection assertion is what makes it load-bearing. |
| `eprom_params_t` struct itself | model | No `src/proms/` TU currently declares a protocol-keyed const data table — this is a genuinely new TU (§ State of the Art: the v1.16 `primitives.{h,cpp}` layer was never merged and does not exist on this branch). |

---

## Anti-Patterns — flag if any analog seems to encourage them

| Anti-pattern | Why it is wrong here | Where the temptation comes from |
|---|---|---|
| `#include <Arduino.h>` in `src/proms/eprom_params.cpp` | +14 macro-redefinition warnings × 2 pinned envs against a watermark at **exactly 1166 with zero headroom** → live gate RED (F-140-01) | **Every other** `src/proms/*.cpp` does it. `not_implemented.cpp` is the exception to copy. |
| Adding the new suite to `[env:native]` / `[env:native_nodevtools]` `test_filter` | breaks the pinned 141 cases / 17 suites on both (D-11) | `firestarter/CLAUDE.md` § "Reuse pattern for future native tests" explicitly instructs adding to both envs — **D-11 overrides it** |
| `scripts/check_eprom_params.py` | drags in `test_checker_convention.py`'s five obligations + `FLOOR` 6→7 + `FIXTURE_FLOOR` 15→16 in the same commit (Pitfall 8) | it is the house convention for *executable checkers* |
| A `switch (protocol)` inside `eprom_params_for()` | that IS the second selector TABLE-05 forbids | `eprom.cpp:71` is a switch, and it stays |
| A `fallback_pulse_us` (or any pulse-width) column | TABLE-02 violation, and gh#15's posted correction just told the world the table has no pulse column (D-03) | the fallback constants sit visibly at `eprom.cpp:71-76` |
| A second dispatch key / a second row keyed on anything but `protocol_id` | TABLE-05 violation; F-140-05's `0x07` family split is a **Phase 146 finding**, never a second row | F-140-05 makes the split look necessary |
| Any new `chip_database.json` field | TABLE-05 violation; the file is **GENERATED**, never hand-edited | the DB-half gate reads the file, which invites "just add a column" |
| An app-side gate that scans firmware source | failed open **4×** in Phase 117; the app's own `tests/test_dev_gate_reads_no_firmware_source.py` codifies the lesson (D-12) | one meta-repo script would "cover both halves" |
| A meta-repo script reading both working trees | runs in **no** CI leg of either sub-repo → a local-run obligation, not a gate (D-12 rejected option) | same |
| `__attribute__((used))` / `static_assert` to force the table into the image | explicitly rejected by D-10; burns scarce Uno-class headroom on code nothing calls. **Expect AVR flash delta ≈ 0** and say so before measuring | a ~0 delta looks like "we forgot the table" |
| Re-baselining `scripts/baseline/size_baseline.json` | Phase 138 created the `_v131` sibling precisely so nothing moves the live baseline before Phase 144 | the counts will not match the new env |
| Passing `native_params_v131` to `check_size_baseline.py` / `check_build_warnings.py` | uncaught `KeyError` → exit 1 (F-138-05) / exit 2, no baseline entry | both scripts look env-generic |
| Editing `src/proms/eprom.cpp` at all | `native_trace_v131` asserts **full ordered positional equality**; D-10 keeps it GREEN through this phase | the VPP duplication at `:145`/`:218` is obviously wrong and Phase 142 fixes it |
| Warm `pio run` for the size/warning capture | warm under-counts badly (native warm 998 vs cold 1166) → false pass | speed |
| Citing a datasheet by repo path | F-140-08: no `datasheets/` tree resolves on this branch; `doc/PROTOCOLS.md` already cites paths that 404 | `doc/PROTOCOLS.md` does it |

---

## Metadata

**Analog search scope:**
`firestarter/{src/proms,src,include,test/native/avr,tests,tests/golden,scripts,.github/workflows}`,
`firestarter/platformio.ini`;
`firestarter_app/{tests,tests/golden,firestarter/data,.github/workflows}`, `firestarter_app/pyproject.toml`

**Files read for extraction (15):**
`src/proms/not_implemented.cpp`, `src/proms/eprom.cpp` (4 targeted ranges), `src/proms/memory.cpp:108-142`,
`src/json_parser.c:42-312`, `include/rurp_platform_compat.h`, `include/proto_constants.h:14-33`,
`include/memory_utils.h:18-31`, `platformio.ini` (4 ranges), `test/native/avr/_shared/host_stubs_common.inc:1-60`,
`test/native/avr/test_not_implemented/host_stubs.cpp`, `test/native/avr/test_val_eprom/host_stubs.cpp`,
`test/native/avr/test_trace_eprom_v131/host_stubs.cpp`, `test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp` (2 ranges),
`tests/test_golden_trace_identity_eprom_v131.py`, `tests/golden/eprom_v131_trace_inventory.json`,
`firestarter_app/tests/test_sdp_db_invariant.py` (2 ranges), `firestarter_app/tests/test_diff_db_gate.py`

**Verified in-session (not recalled):** DB shape `{manufacturer: [chip,…]}` with 59 top-level keys;
`FLOOR = 6` / `FIXTURE_FLOOR = 15` at `tests/test_checker_convention.py:129-130`;
no `conftest.py` anywhere under `firestarter/tests/`; `collect_ignore` armed (pyusb only) at
`firestarter_app/tests/conftest.py:100-102`; both firmware workflows run `pytest tests/ -v` with
`fetch-depth: 0`; app CI lints `firestarter/ tests/` with ruff.

**Pattern extraction date:** 2026-08-09
