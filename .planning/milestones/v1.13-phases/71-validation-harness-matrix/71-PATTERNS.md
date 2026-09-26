# Phase 71: Validation Harness + Matrix — Pattern Map

**Mapped:** 2026-06-16
**Files analyzed:** 16 new/modified files
**Analogs found:** 16 / 16

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter/test/native/avr/_shared/host_stubs_common.inc` | test-infra (MODIFIED) | request-response | itself (extend in-place) | self |
| `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` | test | event-driven | `test/native/avr/test_dispatch/test_configure_memory.cpp` | exact |
| `firestarter/test/native/avr/test_val_eprom/host_stubs.cpp` | test-infra | — | `test/native/avr/test_flash_intel_vpp/host_stubs.cpp` | exact |
| `firestarter/test/native/avr/test_val_{eeprom28c,flash3,flash4,flash_intel,sram}/` | test × 5 | event-driven | same as eprom pair above | exact |
| `firestarter/platformio.ini` | config (MODIFIED) | — | itself lines 80-100 | self |
| `firestarter/test/native/avr/_shared/validation_matrix.h` | config (GENERATED) | — | `firestarter_app/tools/catalog/codegen.py` emit shape | exact |
| `firestarter_app/tools/validation_matrix_spec.json` | config (NEW) | — | `firestarter_app/tools/catalog/messages.toml` (authored input shape) | role-match |
| `firestarter_app/tools/gen_validation_header.py` | utility/codegen | transform | `firestarter_app/tools/catalog/codegen.py` | exact |
| `firestarter_app/tests/test_val_wire_*.py` (6 files) | test | request-response | `firestarter_app/tests/` wire tests using `make_comm`/`fake_serial` | exact |
| `firestarter_app/tests/test_validate_family_cmd.py` | test | request-response | `firestarter_app/tests/` Click CLI tests using `AppContext` | exact |
| `firestarter_app/tests/test_matrix_schema.py` | test | transform | `firestarter_app/tests/` JSON validation tests | role-match |
| `firestarter_app/tests/test_gen_validation_header.py` | test | transform | `firestarter_app/tests/` codegen drift tests | role-match |
| `firestarter_app/tests/test_matrix_artifact.py` | test | transform | same | role-match |
| `firestarter_app/tests/test_validate_oracle.py` | test | transform | same | role-match |
| `firestarter_app/tests/test_check_dispatch_invariants.py` | test | transform | `firestarter_app/tools/check_dispatch.py` (existing gate structure) | exact |
| `firestarter_app/firestarter/cli_handlers.py` (MODIFIED) | CLI handler | request-response | `cli_handlers.py` lines 1044-1130 (`dev consistency-check`) | exact |
| `firestarter_app/tools/check_dispatch.py` (MODIFIED) | utility/gate | CRUD | itself (extend in-place) | self |

---

## Pattern Assignments

### `firestarter/test/native/avr/_shared/host_stubs_common.inc` (MODIFIED)

**Analog:** itself — extend in-place per D-04. The file already has two define-guarded opt-OUT patterns at lines 78-82 and 93-100.

**Existing opt-OUT guard pattern** (lines 78-82 and 93-100):
```cpp
#ifndef HOST_STUBS_CUSTOM_VOLTAGE_MV
extern "C" uint16_t rurp_read_voltage_mv() {
    return 0;
}
#endif

#ifdef HARDWARE_REVISION
// ...
#ifndef HOST_STUBS_CUSTOM_HW_REVISION
extern "C" uint8_t rurp_get_hardware_revision() {
    return 0;
}
#endif
```

**New recording buffer — opt-IN pattern to add (after line 48, replacing the current no-op `rurp_write_to_register`):**

The current no-op at lines 45-48:
```cpp
extern "C" void rurp_write_to_register(uint8_t reg, rurp_register_t data) {
    (void)reg;
    (void)data;
}
```

Replace with the define-guarded recording version:
```cpp
/* Recording bus stub — Phase 71 HARN-01 / D-04.
 * Define HOST_STUBS_RECORD_BUS before including this file to activate.
 * Existing suites (test_dispatch, test_cobs_*, etc.) must NOT define this
 * flag — flag off = today's no-op behavior unchanged. */
#ifdef HOST_STUBS_RECORD_BUS
#define HOST_STUBS_MAX_RECORDING 256
struct bus_record_entry_t { uint8_t reg; uint8_t data; };
static bus_record_entry_t s_bus_recording[HOST_STUBS_MAX_RECORDING];
static int s_bus_recording_count = 0;
extern "C" void clear_bus_recording() { s_bus_recording_count = 0; }
extern "C" int  bus_recording_count() { return s_bus_recording_count; }
extern "C" uint8_t recorded_reg(int i)  { return s_bus_recording[i].reg; }
extern "C" uint8_t recorded_data(int i) { return s_bus_recording[i].data; }
extern "C" void rurp_write_to_register(uint8_t reg, rurp_register_t data) {
    if (s_bus_recording_count < HOST_STUBS_MAX_RECORDING) {
        s_bus_recording[s_bus_recording_count].reg  = reg;
        s_bus_recording[s_bus_recording_count].data = (uint8_t)data;
        s_bus_recording_count++;
    }
}
#else
extern "C" void rurp_write_to_register(uint8_t reg, rurp_register_t data) {
    (void)reg; (void)data;
}
#endif
```

---

### `firestarter/test/native/avr/test_val_eprom/host_stubs.cpp` (NEW, all 6 families)

**Analog:** `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp` lines 1-33.

**Imports pattern** (lines 18-25 of analog):
```cpp
#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}
```

**Core pattern** — opt-IN recording, NO opt-OUT overrides needed for pure recording suites (lines 30-33 of analog show the opt-OUT pattern; for recording suites invert to opt-IN):
```cpp
/* Activate recording bus stub — MUST precede the shared include. */
#define HOST_STUBS_RECORD_BUS
#include "../_shared/host_stubs_common.inc"
/* No further overrides — the recording buffer replaces the no-op. */
```

For `test_val_flash_intel/host_stubs.cpp` only, also add mock voltage (same as analog):
```cpp
#define HOST_STUBS_RECORD_BUS
#define HOST_STUBS_CUSTOM_VOLTAGE_MV
#include "../_shared/host_stubs_common.inc"
static uint16_t s_mock_vpp_mv = 12000;  /* default: valid 12V for flash_intel */
extern "C" void set_mock_vpp_mv(uint16_t mv) { s_mock_vpp_mv = mv; }
extern "C" uint16_t rurp_read_voltage_mv() { return s_mock_vpp_mv; }
```

---

### `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` (NEW, primary Tier-1 analog)

**Analog:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (full file, 191 lines).

**Imports pattern** (lines 31-40 of analog):
```cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"

using namespace fakeit;
```

**Additional declarations needed by recording suites (not in analog — add after imports):**
```cpp
/* Recording API — symbols compiled because host_stubs.cpp defines HOST_STUBS_RECORD_BUS */
extern "C" void clear_bus_recording();
extern "C" int  bus_recording_count();
extern "C" uint8_t recorded_reg(int i);
extern "C" uint8_t recorded_data(int i);
```

**setUp pattern** (lines 42-52 of analog):
```cpp
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    clear_bus_recording();   /* ADD: reset before each test */
}

void tearDown(void) {}
```

**make_handle helper** (lines 57-65 of analog — copy verbatim):
```cpp
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.mem_type = mem_type;
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}
```

**Core recording assertion pattern** (new, based on RESEARCH.md §Recording Bus Stub):
```cpp
/* POSITIVE: write init enables VPP regulator via CTL register */
void test_eprom_write_enables_vpp_regulator_via_ctl(void) {
    firestarter_handle_t h = make_handle(0x07, 0, CMD_WRITE);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    bool vpp_seen = false;
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER &&
            (recorded_data(i) & CTRL_VPP_REGULATOR_ENABLE)) {
            vpp_seen = true; break;
        }
    }
    TEST_ASSERT_TRUE_MESSAGE(vpp_seen, "configure_eprom write must enable VPP regulator");
}

/* NEGATIVE CONTROL: read must NOT enable VPP regulator */
void test_eprom_read_does_not_enable_vpp_regulator(void) {
    firestarter_handle_t h = make_handle(0x07, 0, CMD_READ);
    configure_memory(&h);
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER) {
            TEST_ASSERT_BITS_LOW_MESSAGE(CTRL_VPP_REGULATOR_ENABLE, recorded_data(i),
                "configure_eprom read must NOT enable VPP regulator");
        }
    }
}
```

**SRAM-specific override** — `test_val_sram/test_val_sram.cpp` must assert zero writes (no-op state):
```cpp
/* configure_sram is currently a no-op (sram.cpp:15-17) — assert zero writes.
 * Phase 74 FIX-01 will change this; until then GREEN = confirmed no-op. */
void test_sram_configure_records_zero_bus_writes(void) {
    firestarter_handle_t h = make_handle(0x0E, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_EQUAL_INT_MESSAGE(0, bus_recording_count(),
        "configure_sram must not issue any register writes (no-op state)");
}
```

**main() pattern** (lines 165-190 of analog — copy structure):
```cpp
int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_eprom_write_enables_vpp_regulator_via_ctl);
    RUN_TEST(test_eprom_read_does_not_enable_vpp_regulator);
    /* add protocol 0x08, 0x0B variants */
    return UNITY_END();
}
```

---

### `firestarter/platformio.ini` (MODIFIED)

**Analog:** itself lines 80-100 (the `test_filter` allowlist + `build_flags` `-I` entries).

**Pattern to replicate for each of the 6 new suites** (lines 80-100 of analog):
```ini
test_filter =
    native/avr/test_dispatch
    native/avr/test_not_implemented
    ...
    native/avr/test_val_eprom        ; ADD
    native/avr/test_val_eeprom28c    ; ADD
    native/avr/test_val_flash3       ; ADD
    native/avr/test_val_flash4       ; ADD
    native/avr/test_val_flash_intel  ; ADD
    native/avr/test_val_sram         ; ADD
build_flags =
    ${env.build_flags}
    -std=gnu++17
    -I include
    -I test/native/avr/test_dispatch
    ...
    -I test/native/avr/test_val_eprom        ; ADD
    -I test/native/avr/test_val_eeprom28c    ; ADD
    -I test/native/avr/test_val_flash3       ; ADD
    -I test/native/avr/test_val_flash4       ; ADD
    -I test/native/avr/test_val_flash_intel  ; ADD
    -I test/native/avr/test_val_sram         ; ADD
```

**Critical:** PIO uses a positive allowlist (not `test_ignore`) — a suite not in `test_filter` silently doesn't run. See comment at lines 78-80 of `platformio.ini`.

---

### `firestarter_app/tools/gen_validation_header.py` (NEW)

**Analog:** `firestarter_app/tools/catalog/codegen.py` — full file. Key structural patterns:

**Imports + path constants** (lines 36-40 of analog):
```python
import argparse
import sys
from pathlib import Path
import json
```

**Validation-first pattern** (lines 167-198 of analog — `validate_catalog`):
```python
def validate_spec(spec: dict) -> None:
    """Raise ValueError on schema violation before any emission."""
    if not isinstance(spec.get("schema_version"), int):
        raise ValueError("spec must have integer schema_version")
    families = spec.get("families")
    if not isinstance(families, list) or not families:
        raise ValueError("spec must have non-empty 'families' list")
    # per-family: id, handler, protocols (list of int) required
    for fam in families:
        for key in ("id", "handler", "protocols"):
            if key not in fam:
                raise ValueError(f"family {fam!r} missing required key '{key}'")
```

**Determinism contract** (lines 23-27 of analog docstring):
```python
# Determinism: sorted order, no timestamps, LF endings
# Path.write_text(..., encoding="utf-8", newline="\n")
```

**Banner pattern** (lines 120-125 of analog):
```python
BANNER = (
    "/* DO NOT EDIT -- generated by tools/gen_validation_header.py\n"
    " * Re-run after editing tools/validation_matrix_spec.json */\n"
    "\n"
)
```

**main() pattern** (lines 690-728 of analog):
```python
def main() -> int:
    args = _build_argparser().parse_args()
    if not args.spec.is_file():
        print(f"ERROR: spec not found: {args.spec}", file=sys.stderr)
        return 2
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    try:
        validate_spec(spec)
    except ValueError as e:
        print(f"ERROR: spec validation failed: {e}", file=sys.stderr)
        return 1
    output = emit_cpp_header(spec)
    args.target.parent.mkdir(parents=True, exist_ok=True)
    args.target.write_text(output, encoding="utf-8", newline="\n")
    print(f"OK: wrote {args.target}")
    return 0
```

---

### `firestarter_app/tools/validation_matrix_spec.json` (NEW)

**Analog:** `firestarter_app/tools/catalog/messages.toml` (authored input; JSON analog). Schema from RESEARCH.md §Matrix Schema:
```json
{
  "schema_version": 1,
  "families": [
    {
      "id": "eprom",
      "handler": "configure_eprom",
      "protocols": [7, 8, 11],
      "rep_chip": "W27C512",
      "tier1": { "suite": "test_val_eprom", "assertions": [...] },
      "tier2": { "test_module": "test_val_wire_eprom", "commands": [...] },
      "tier3": { "test_chip": "W27C512", "boards": ["leonardo"], "skip_boards": ["uno328pb"] }
    }
  ]
}
```
Keep protocol IDs as decimal integers (not `0x07` hex — JSON has no hex literal).

---

### `firestarter/test/native/avr/_shared/validation_matrix.h` (GENERATED)

**Analog:** `firestarter/include/messages.h` (committed generated header). The C++ header emitted by `gen_validation_header.py` follows its shape:
```c
/* DO NOT EDIT -- generated by tools/gen_validation_header.py
 * Re-run after editing tools/validation_matrix_spec.json */

#pragma once

#define VAL_FAMILY_COUNT 6

typedef struct {
    uint32_t protocol;
    const char* family_id;
    const char* handler_name;
} val_family_entry_t;

static const val_family_entry_t VAL_FAMILIES[] = {
    { 0x07, "eprom", "configure_eprom" },
    ...
};
```

Commit this file (like `messages.h`). Native suites must compile without running codegen at build time.

---

### `firestarter_app/tests/test_val_wire_eprom.py` (and 5 sibling files) — Tier-2

**Analog:** any existing `firestarter_app/tests/test_*.py` that uses `make_comm`/`fake_serial`. The fixture API from `conftest.py` lines 121-151:

**Imports + fixture pattern:**
```python
import pytest
from firestarter.database import EpromDatabase
from tools.check_dispatch import dispatch, KNOWN_PROTOCOLS

def test_eprom_wire_dict_algorithm_field(make_comm, fake_serial):
    db = EpromDatabase()
    chip = db.get_eprom("W27C512")
    wire = db.convert_to_programmer(chip)
    # Assert the wire dict carries the correct algorithm field
    assert wire.get("algorithm") == 0x07

def test_eprom_wire_dict_dispatches_to_configure_eprom(make_comm, fake_serial):
    db = EpromDatabase()
    chip = db.get_eprom("W27C512")
    wire = db.convert_to_programmer(chip)
    proto = wire.get("algorithm", 0)
    mt = wire.get("type", 1)
    assert dispatch(proto, mt) == "configure_eprom"
```

**Key:** Tier-2 tests do NOT require serial I/O. They validate that the host wire dict for each family's representative chip (from `validation_matrix_spec.json`) routes to the correct handler via the same `dispatch()` already exercised by `check_dispatch.py`.

**`make_comm` factory** (`conftest.py` lines 127-151) — use as-is; the fixture uses `__new__` to bypass `SerialCommunicator.__init__` and injects `fake_serial` as `.connection`.

---

### `firestarter_app/tests/test_validate_family_cmd.py` (Tier-3 scaffold)

**Analog:** existing Click CLI tests in `firestarter_app/tests/` that invoke `cli_handlers.py` subcommands. The `dev consistency-check` handler at `cli_handlers.py:1042` is the direct structural match.

**Core pattern — invoke CLI via Click's test runner:**
```python
from click.testing import CliRunner
from firestarter.main import cli

def test_validate_family_skip_deferred_when_no_hardware():
    runner = CliRunner()
    result = runner.invoke(cli, ["dev", "validate-family", "eprom"])
    # Without --port/--board, all Tier-3 cells are SKIP-deferred; exit 0
    assert result.exit_code == 0
    # Artifact should be emitted with SKIP-deferred verdict
    import json, os
    artifact_path = "validation-matrix.json"
    if os.path.exists(artifact_path):
        data = json.loads(open(artifact_path).read())
        assert all(c["verdict"] == "SKIP-deferred" for c in data["cells"]
                   if c.get("tier") == 3)
```

---

### `firestarter_app/firestarter/cli_handlers.py` (MODIFIED — new `dev validate-family` subcommand)

**Analog:** `cli_handlers.py` lines 1044-1130 (`dev consistency-check` handler) — the direct model.

**Decorator stack pattern** (lines 1044-1096 of analog):
```python
@dev.command(name="validate-family")
@click.argument("family", type=click.Choice(
    ["eprom", "eeprom28c", "flash3", "flash4", "flash_intel", "sram", "all"]
))
@click.option("--board", default=None, help="Board name (e.g. leonardo, uno328pb)")
@click.option("--chip", default=None, help="Representative chip name override")
@click.option("--source", default=None, type=click.Path(),
              help="Source image path for write+verify oracle")
@click.option("--output-dir", "output_dir", type=str, default=None,
              help="Output directory for results artifact")
@click.pass_obj
@map_typed_errors          # REQUIRED — cli_handlers.py is in the mypy strict island
def dev_validate_family(
    app: AppContext,
    family: str,
    board: Optional[str],
    chip: Optional[str],
    source: Optional[str],
    output_dir: Optional[str],
) -> None:
    """Run the per-family validation matrix (Tier-1/Tier-2 are software-only)."""
```

**SKIP-deferred exit pattern** (D-06 — analogous to `sys.exit(verdict_int)` at line 1113 of analog):
```python
    if not app.port or not board or not chip or not source:
        _emit_skip_deferred_artifact(family, output_dir=output_dir)
        sys.exit(0)   # milestone remains closeable
    # ... composition of write_cycle_eprom + consistency_check_eprom
```

**3-way verdict exit** (lines 1112-1114 of analog — copy exactly):
```python
    sys.exit(verdict_int)   # NOT bool-to-int wrap; 0=PASS, 1=FAIL, 2=hw-error
```

**Type annotation requirement** (mypy strict island — Pitfall 5 in RESEARCH.md): all parameters must be fully annotated; `Optional[str]` requires `from __future__ import annotations` or explicit import of `Optional` from `typing`.

---

### `firestarter_app/tools/check_dispatch.py` (MODIFIED — per-family VPP invariants + populate `non_supported_dispatchable`)

**Analog:** itself. Key extension points identified by reading the file:

**Where to add the `_FAMILY_VPP_INVARIANTS` dict** — after `_SRAM_PROTOCOLS` at line 55:
```python
# Per-family VPP range invariants (Phase 71 HARN-04).
# Maps handler name → (min_vpp_mv, max_vpp_mv).
# 6000 mV threshold: separates WP-pin 12V (not a programming VPP)
# from true programming VPP. See RESEARCH.md §Pitfall 6.
_FAMILY_VPP_INVARIANTS: dict[str, tuple[int, int]] = {
    "configure_eprom":       (0, 22000),
    "configure_eeprom28c":   (0, 6000),
    "configure_flash3":      (0, 6000),
    "configure_flash4":      (0, 6000),
    "configure_flash_intel": (10000, 22000),
    "configure_sram":        (0, 6000),
}
```

**Where to add the scan loop extension** — after `handler = dispatch(proto, mt)` at line 197, inside the existing `for chip in chips:` loop (lines 174+):
```python
            # Phase 71 HARN-04: per-family VPP invariant check
            vpp_mv = chip.get("programming", {}).get("vpp_mv", 0) or 0
            if handler in _FAMILY_VPP_INVARIANTS:
                lo, hi = _FAMILY_VPP_INVARIANTS[handler]
                if not (lo <= vpp_mv <= hi):
                    family_vpp_violations.append(
                        f"{mfg}/{part} proto=0x{proto:02X} handler={handler} "
                        f"vpp_mv={vpp_mv} outside [{lo},{hi}]"
                    )
                    # Populate non_supported_dispatchable when non-supported chip
                    # ALSO has a VPP mismatch — the dangerous dual-violation case.
                    if chip_ss != "supported":
                        non_supported_dispatchable.append(
                            f"{mfg}/{part} proto=0x{proto:02X} ss={chip_ss} "
                            f"handler={handler} vpp_mv={vpp_mv} outside [{lo},{hi}]"
                        )
```

**New `family_vpp_violations` list** — declare alongside existing error lists at lines 151-167:
```python
    family_vpp_violations = []
```

**Gate failure injection** — add to the existing `errors` aggregation block (after `sram_in_eprom`, `eeprom28c_in_eprom` checks, around line 319+):
```python
    if family_vpp_violations:
        errors.extend(family_vpp_violations)
        print(f"FAIL: {len(family_vpp_violations)} per-family VPP invariant violation(s):")
        for v in family_vpp_violations:
            print(f"  {v}")
```

---

### `firestarter_app/tests/test_check_dispatch_invariants.py` (NEW)

**Analog:** any existing test that invokes `check_dispatch.main()` or `dispatch()` directly (the existing `test_dispatch_*` tests if present, otherwise the gate tests).

**Core pattern:**
```python
import subprocess, sys

def test_check_dispatch_exits_zero():
    """Existing gate must pass before extensions."""
    result = subprocess.run(
        [sys.executable, "tools/check_dispatch.py"],
        cwd="<firestarter_app_dir>",
        capture_output=True,
    )
    assert result.returncode == 0

def test_family_vpp_invariants_direct():
    """Import and call directly to cover the new invariant dict."""
    from tools.check_dispatch import dispatch, _FAMILY_VPP_INVARIANTS
    # flash_intel must always require elevated VPP
    lo, hi = _FAMILY_VPP_INVARIANTS["configure_flash_intel"]
    assert lo >= 10000
    # sram must never get VPP
    lo2, hi2 = _FAMILY_VPP_INVARIANTS["configure_sram"]
    assert hi2 <= 6000
```

---

## Shared Patterns

### ArduinoFake Serial stub (all Tier-1 native suites)

**Source:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` lines 42-52

**Apply to:** all 6 `test_val_*/test_val_*.cpp` files — copy `setUp()` verbatim, add `clear_bus_recording()` call.

```cpp
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    clear_bus_recording();
}
```

### `@map_typed_errors` decorator (all new CLI handlers)

**Source:** `firestarter_app/firestarter/cli_handlers.py` line 925-926 (on `dev_read`), line 1095-1096 (on `dev_consistency_check`)

**Apply to:** `dev_validate_family` — both the `@dev.command` and the function body must be decorated.

```python
@click.pass_obj
@map_typed_errors
def dev_validate_family(app: AppContext, ...) -> None:
```

### `sys.exit(verdict_int)` — NOT bool-to-int wrap

**Source:** `cli_handlers.py` line 1113 comment: "D-12 step 5 / 3-way verdict contract: verdict_int = consistency_check_eprom(...) # 0=PASS, 1=FAIL, 2=hw-error"

**Apply to:** `dev_validate_family` Tier-3 result emission.

### Deterministic codegen emission (gen_validation_header.py)

**Source:** `firestarter_app/tools/catalog/codegen.py` lines 23-27 (docstring) and line 728

**Apply to:** `gen_validation_header.py` — `Path.write_text(..., encoding="utf-8", newline="\n")`, sorted family entries, no timestamps in banner.

### `make_comm` / `fake_serial` fixture usage (all Tier-2 tests)

**Source:** `firestarter_app/tests/conftest.py` lines 121-151

**Apply to:** all `test_val_wire_*.py` — these fixtures are auto-discovered; no import needed in test files, just accept as function parameters.

```python
def test_something(make_comm, fake_serial):
    comm = make_comm()   # Note: factory call, not fixture value directly
```

---

## No Analog Found

All files have close analogs in the codebase. No entries in this section.

---

## Metadata

**Analog search scope:** `firestarter/test/native/avr/`, `firestarter_app/tests/`, `firestarter_app/tools/`, `firestarter_app/firestarter/cli_handlers.py`
**Files scanned:** 9 source files read in full
**Pattern extraction date:** 2026-06-16
