# Phase 71: Validation Harness + Matrix — Research

**Researched:** 2026-06-16
**Domain:** Software-first three-tier validation harness for EPROM programmer firmware dispatch
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Authored validation matrix is a single app-owned JSON file in
  `firestarter_app/` (location e.g. `tools/` or `firestarter/data/` — planner's
  choice). Python reads it directly; C++ native suites consume it via a codegen
  step that generates a C++ header (same pattern family as the existing build_db /
  codegen flow). Test-only — no production flash impact.
- **D-02:** Authored source is **distinct** from the emitted results artifact
  `validation-matrix.{json,md}` required by HARN-02. Keep two files conceptually
  and physically separate: one is hand-authored input, the other is generated output.
- **D-03 (rejected):** Meta-repo JSON + lockstep codegen to both sub-repos. Rejected.
- **D-04:** Add register-write recording to the **existing shared**
  `firestarter/test/native/avr/_shared/host_stubs_common.inc` as a
  **define-guarded opt-in buffer** (`#define HOST_STUBS_RECORD_BUS`). Existing
  suites compile **unchanged** — flag off = today's no-op behavior.
- **D-05:** A **new subcommand under the existing `dev` group** that **composes**
  the existing `write_cycle_eprom`/`consistency_check_eprom` methods — no
  re-implementation of read/write — and **emits the matrix results artifact**.
- **D-06:** When no board/chip is present, runner records a **SKIP-deferred** cell
  rather than hard-failing.
- **D-07:** Phase 71 stands up all 6 families' Tier-1 native + Tier-2 host wire
  cells GREEN (software, ungated, no bench needed). Phase 73 adds Tier-3 HIL
  evidence + resolves SRAM no-op (VAL-06).
- **D-08:** Non-vacuous PASS oracle: post-write full read + SHA compare on
  **Leonardo** (advisory-only on other boards); mandatory passing negative control;
  retry-count capture; per-task live R1/R2 calibration precondition (`r1 ≈ 270000`);
  `uno328pb` hard-coded **N/A** for program/write cells.
- **D-09:** `check_dispatch.py` gains per-family dispatch invariants AND its hollow
  `non_supported_dispatchable` inverse detector is **populated** — a non-supported
  chip routing to a real handler, or a family handler enabling VPP it must not,
  fails the CI gate.
- **D-10:** Reuse, do **not** fork: existing `[env:native]` + Unity + ArduinoFake,
  host `make_comm`/`fake_serial`, `write_cycle_eprom`/`consistency_check_eprom`,
  `check_dispatch.py`, `diff_db.py`.

### Claude's Discretion

- Exact `dev validate-family` verb/flag spelling (per-family arg vs `--all`/`--family`
  filter, command name) — deferred to planner (D-05/D-06 constraints hold).
- Authored-matrix JSON file path within `firestarter_app/`.
- Whether the generated C++ header is committed or built on-the-fly (determinism
  preferred; not a wire contract so no lockstep gate).
- Evidence-SHA capture mechanism for the emitted results artifact.
- Negative-control representation across software tiers.

### Deferred Ideas (OUT OF SCOPE)

- Running the matrix for real / populating PASS-FAIL-SKIP evidence → Phase 73.
- Resolving the SRAM no-op question → Phase 73 (VAL-06).
- Any per-family correctness fix → Phase 74. Erase path → Phase 75.
- Spec-only gaps → Phase 76. Protocol re-research → Phase 72.

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HARN-01 | Three-tier validation harness: Tier-1 native Unity suites with recording bus stub; Tier-2 host pytest wire round-trip via `make_comm`/`fake_serial`; Tier-3 `dev validate-family` composing existing cycle methods; zero production flash. | Recording stub pattern (§Recording Bus Stub); Tier-2 fixture shape (§Tier-2 Host Wire Round-Trip); Tier-3 composition API (§Tier-3 Runner) |
| HARN-02 | Declarative per-family matrix data file drives native suites + bench runner; emits committed `validation-matrix.{json,md}` artifact with PASS/FAIL/SKIP-deferred per cell. | Matrix schema (§Matrix Schema); codegen pattern (§Codegen Pattern); artifact shape (§Results Artifact) |
| HARN-03 | Non-vacuous PASS oracle: post-write SHA on Leonardo; mandatory negative control; retry-count capture; r1 ≈ 270000 precondition; uno328pb=N/A. | Oracle architecture (§PASS Oracle Architecture) |
| HARN-04 | `check_dispatch.py` gains per-family dispatch invariants + populated `non_supported_dispatchable` inverse detector; CI gate fails on violations. | check_dispatch anatomy (§check_dispatch.py Extension) |

</phase_requirements>

---

## Summary

Phase 71 delivers a software-first, flash-free validation spine for v1.13. All work is in test infrastructure and host CLI — `pio run -e uno/leonardo` byte-count stays unchanged. The three tiers are engineered to be independently green: Tier-1 (native Unity) and Tier-2 (pytest wire round-trip) require no bench hardware and must be GREEN by the end of this phase; Tier-3 (`dev validate-family` CLI runner) is scaffolded but its HIL cells remain SKIP-deferred until Phase 73.

The central design insight is that the existing codebase provides nearly every building block already: the shared stub file explicitly anticipates recording extensions (`host_stubs_common.inc` line 38-39: "If a future test starts caring about register writes, the stubs can grow to record calls"), the `make_comm`/`fake_serial` fixtures are already the host test backbone, `write_cycle_eprom` and `consistency_check_eprom` already implement the 3-way PASS/FAIL/hw-error verdict contract, the `dev` CLI group has the exact subcommand slot, and `check_dispatch.py` already has the `non_supported_dispatchable` list and the wiring to emit per-family failure messages.

The codegen pattern for matrix→C++ header follows the established `tools/catalog/codegen.py` shape: a Python script reads a TOML/JSON source, validates it, and emits a deterministic C++ header with a banner warning "DO NOT EDIT". This pattern is well understood by the codebase and avoids cross-repo lockstep (D-03 rejected).

**Primary recommendation:** Stand up all 6 family cells in Tier-1 and Tier-2 first (pure software, no risk), then add the `dev validate-family` scaffold with SKIP-deferred logic, then extend `check_dispatch.py`. The recording stub addition is the highest-novelty item — get it right with the define-guard pattern before building families on top of it.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Recording bus stub | Firmware test infra (`firestarter/test/`) | — | Stub lives adjacent to firmware sources; only compiled in `[env:native]` |
| Tier-1 native Unity suites | Firmware test infra (`firestarter/test/native/avr/`) | — | PIO discovers under `test/`; excluded from production `src_filter` |
| Tier-2 pytest wire round-trip | Host test infra (`firestarter_app/tests/`) | — | Reuses existing `make_comm`/`fake_serial` fixtures |
| Authored matrix JSON | Host app data/tools (`firestarter_app/`) | — | App-owned per D-01; Python reads directly |
| Matrix → C++ header codegen | Host tools (`firestarter_app/tools/`) | — | Follows existing `tools/catalog/codegen.py` shape |
| `dev validate-family` CLI | Host CLI (`firestarter_app/firestarter/cli_handlers.py`) | Host ops (`eprom_operations.py`) | `dev` group is home for diagnostics (D-05); ops layer provides cycle methods |
| Results artifact emission | Host (`dev validate-family`) | — | Runner owns the artifact per D-05 |
| `check_dispatch.py` extension | Host tools (`firestarter_app/tools/check_dispatch.py`) | — | Existing CI gate; D-09 extends it in-place |

---

## Standard Stack

### Core (already present — D-10: do not add new dependencies)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Unity (PlatformIO) | bundled | Firmware native test framework | Already in `[env:native]` `test_framework = unity` |
| ArduinoFake | ^0.4.0 | Arduino API mock for native tests | Already in `lib_deps` of `[env:native]` |
| pytest | project standard | Host Python test framework | Already present; used throughout `firestarter_app/tests/` |
| hashlib (stdlib) | Python stdlib | SHA-256 for PASS oracle comparison | Already used in `write_cycle_eprom` and `consistency_check_eprom` |
| json (stdlib) | Python stdlib | Matrix data file parsing | Already used everywhere |
| Click | project standard | CLI framework for `dev` group | Already in use; `dev` group is `@cli.group(name="dev")` |

### No New Dependencies

The requirements spec explicitly prohibits new third-party test dependencies: "New third-party test dependencies — the substrate (PlatformIO native + Unity + ArduinoFake; pytest + syrupy + pyserial) is already present." [VERIFIED: REQUIREMENTS.md §Out of Scope]

---

## Architecture Patterns

### System Architecture Diagram

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  Authored Input (app-owned, hand-maintained)                         │
  │  firestarter_app/tools/validation_matrix_spec.json                   │
  │    { families: [ { id: "eprom", protocols: [0x07,0x08,0x0B],         │
  │                    rep_chip: "W27C512", assertions: {...} } ] }       │
  └────────────────────────┬─────────────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
  ┌──────────────────────┐   ┌──────────────────────────────────────────┐
  │  Python host reads   │   │  tools/gen_validation_header.py (codegen)│
  │  JSON directly       │   │  Emits: firestarter/test/native/avr/     │
  │  (Tier-2, Tier-3)    │   │    _shared/validation_matrix.h           │
  └──────────┬───────────┘   └──────────────┬───────────────────────────┘
             │                               │
             ▼                               ▼
  ┌──────────────────────┐   ┌──────────────────────────────────────────┐
  │  Tier-2: pytest      │   │  Tier-1: native Unity per-family suites  │
  │  firestarter_app/    │   │  firestarter/test/native/avr/            │
  │  tests/test_val_*.py │   │    test_val_eprom/                        │
  │  uses make_comm /    │   │    test_val_eeprom28c/                    │
  │  fake_serial to drive│   │    test_val_flash3/  ... (6 suites)       │
  │  wire round-trips    │   │  host_stubs.cpp: #define HOST_STUBS_RECORD│
  └──────────┬───────────┘   │  _BUS → recording buffer active          │
             │               └──────────────┬───────────────────────────┘
             │                               │
             │               ┌───────────────┘
             │               ▼
             │   ┌──────────────────────────────────────────────────────┐
             │   │  host_stubs_common.inc (define-guarded recording buf) │
             │   │  #ifdef HOST_STUBS_RECORD_BUS                        │
             │   │    static uint8_t _rec_reg[MAX_REC], _rec_data[...];  │
             │   │    static int _rec_count = 0;                         │
             │   │    void clear_recording()  { _rec_count = 0; }        │
             │   │    int  recording_count()  { return _rec_count; }     │
             │   │    uint8_t recorded_reg(i) { return _rec_reg[i]; }    │
             │   │  #else → today's no-op remains (existing suites OK)  │
             │   └──────────────────────────────────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  Tier-3: dev validate-family (CLI runner)                            │
  │  cli_handlers.py §dev group → EpromOperator cycle methods:           │
  │    1. r1_precondition_check() → abort if r1 ≠ 270000                 │
  │    2. negative_control_run()  → wrong-file mismatch, blank chip      │
  │    3. write_cycle_eprom(...)  → erase→write→readback N times         │
  │    4. consistency_check_eprom(...) → N reads, SHA compare            │
  │    5. cell verdict: PASS / FAIL / SKIP-deferred                      │
  └──────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  Emitted Results Artifact (generated output, distinct from input)    │
  │  validation-matrix.json  (family × board × verdict × evidence SHA)   │
  │  validation-matrix.md    (human-readable table)                      │
  └──────────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

```
firestarter/
└── test/
    └── native/
        └── avr/
            ├── _shared/
            │   ├── host_stubs_common.inc      # EXTENDED: add recording buffer
            │   └── validation_matrix.h        # GENERATED by codegen (D-01)
            ├── test_val_eprom/                # NEW: Tier-1 suite for 0x07/0x08/0x0B
            │   ├── test_val_eprom.cpp
            │   └── host_stubs.cpp             # defines HOST_STUBS_RECORD_BUS
            ├── test_val_eeprom28c/            # NEW: Tier-1 suite for 0x0D
            ├── test_val_flash3/               # NEW: Tier-1 suite for 0x06
            ├── test_val_flash4/               # NEW: Tier-1 suite for 0x05/0x35/0x39
            ├── test_val_flash_intel/          # NEW: Tier-1 suite for 0x10
            └── test_val_sram/                 # NEW: Tier-1 suite for 0x0E/0x27/0x28/0x29

firestarter_app/
├── tools/
│   ├── validation_matrix_spec.json            # NEW: authored matrix (D-01)
│   └── gen_validation_header.py               # NEW: codegen entrypoint (D-01)
├── firestarter/
│   └── cli_handlers.py                        # EXTENDED: dev validate-family subcommand
├── tests/
│   └── test_val_wire_*.py                     # NEW: Tier-2 pytest suites (one per family)
└── validation-matrix.json / .md              # EMITTED: results artifact (D-02)
```

---

## Recording Bus Stub (HARN-01 / D-04)

### What the stub file currently contains

`firestarter/test/native/avr/_shared/host_stubs_common.inc` [VERIFIED: file read] provides:

- `rurp_write_to_register(uint8_t reg, rurp_register_t data)` — no-op stub, line 45
- `rurp_read_from_register(uint8_t reg)` — returns 0, line 50
- `rurp_set_control_pin(uint8_t pin, uint8_t state)` — no-op, line 58
- `rurp_set_data_output()`, `rurp_set_data_input()`, `rurp_write_data_buffer()`, `rurp_read_data_buffer()` — no-ops
- Voltage/config/button stubs with `HOST_STUBS_CUSTOM_VOLTAGE_MV` and `HOST_STUBS_CUSTOM_HW_REVISION` opt-out guards

The header comment at lines 36-39 explicitly anticipates this extension: "If a future test starts caring about register writes, the stubs can grow to record calls; today they are deliberately minimal." [VERIFIED: file read host_stubs_common.inc:36-39]

### How to add the recording buffer

The define-guard opt-in pattern must mirror the existing `HOST_STUBS_CUSTOM_VOLTAGE_MV` / `HOST_STUBS_CUSTOM_HW_REVISION` opt-OUT pattern — but inverted: opt-IN via `#define HOST_STUBS_RECORD_BUS` BEFORE including the shared file.

**Pattern to follow (verified from test_flash_intel_vpp/host_stubs.cpp:30-31):**
```cpp
#define HOST_STUBS_CUSTOM_VOLTAGE_MV    // opt-OUT of default stub
#define HOST_STUBS_CUSTOM_HW_REVISION   // opt-OUT of default stub
#include "../_shared/host_stubs_common.inc"
// then define the custom versions below
```

**Recording buffer addition to host_stubs_common.inc:**
```cpp
/* Recording bus stub — Phase 71 HARN-01 / D-04.
 * Define HOST_STUBS_RECORD_BUS before including this file to activate.
 * Existing suites (test_dispatch, test_cobs_*, test_read_timing, etc.)
 * MUST NOT define this flag — flag off = today's no-op behavior unchanged. */
#ifdef HOST_STUBS_RECORD_BUS
#define HOST_STUBS_MAX_RECORDING 256

struct bus_record_entry_t {
    uint8_t reg;
    uint8_t data;
};
static bus_record_entry_t s_bus_recording[HOST_STUBS_MAX_RECORDING];
static int s_bus_recording_count = 0;

extern "C" void clear_bus_recording() { s_bus_recording_count = 0; }
extern "C" int  bus_recording_count() { return s_bus_recording_count; }
extern "C" uint8_t recorded_reg(int i) { return s_bus_recording[i].reg; }
extern "C" uint8_t recorded_data(int i) { return s_bus_recording[i].data; }

extern "C" void rurp_write_to_register(uint8_t reg, rurp_register_t data) {
    if (s_bus_recording_count < HOST_STUBS_MAX_RECORDING) {
        s_bus_recording[s_bus_recording_count].reg  = reg;
        s_bus_recording[s_bus_recording_count].data = (uint8_t)data;
        s_bus_recording_count++;
    }
}
#else
// Original no-op (unchanged for existing suites):
extern "C" void rurp_write_to_register(uint8_t reg, rurp_register_t data) {
    (void)reg; (void)data;
}
#endif
```

### Which `rurp_*` functions to intercept

From the dispatch path in `memory.cpp:configure_memory` and `rurp_register_utils.h` (per HARDWARE_SIM_SPEC.md §3.3): the primary signal of handler behavior is the **sequence of `rurp_write_to_register` calls** (which drives LSB, MSB, and CTL latches). The key register values are:
- `LSB_ADDRESS_REGISTER` — captures A0..A7
- `MSB_ADDRESS_REGISTER` — captures A8..A13 + R/W line on bit 6 for SRAM/EEPROM
- `CONTROL_REGISTER` — captures VPP enables (CTRL_VPP_REGULATOR_ENABLE=0x80, CTRL_VPP_P1_ENABLE=0x08, etc.)

**Critical per-family observable assertions:**

| Family | Must be written | Must NOT be written | Proof |
|--------|----------------|---------------------|-------|
| `configure_eprom` | CTL with `CTRL_VPP_REGULATOR_ENABLE (0x80)` set | — | VPP boost must fire |
| `configure_eeprom28c` | MSB with bit 6 HIGH (R/W=1 for reads) | CTL with 0x80 | 5V only |
| `configure_flash3` | CTL without 0x80 | — | No VPP |
| `configure_flash4` | CTL without 0x80 | — | No VPP |
| `configure_flash_intel` | CTL with `CTRL_VPP_P1_ENABLE (0x08)` set | — | P1 VPP |
| `configure_sram` | zero CTL writes (no-op handler) | 0x80, 0x08 | Never VPP |

For `configure_sram`: the current `sram.cpp:15-17` body is `LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM)` with NO function pointer wiring. [VERIFIED: sram.cpp read] The recording test for SRAM therefore asserts `bus_recording_count() == 0` after `configure_memory` runs with `CMD_READ` — proving the SRAM no-op is the current state (this is the evidence Phase 73 will resolve for VAL-06).

**How native suites read the recording:**

Each per-family suite's `host_stubs.cpp` defines `HOST_STUBS_RECORD_BUS` before including the shared file:
```cpp
// test_val_eprom/host_stubs.cpp
#define HOST_STUBS_RECORD_BUS
#include "../_shared/host_stubs_common.inc"
// (no further overrides needed for EPROM suite)
```

Then the test body:
```cpp
// test_val_eprom/test_val_eprom.cpp
extern "C" void clear_bus_recording();
extern "C" int  bus_recording_count();
extern "C" uint8_t recorded_reg(int i);
extern "C" uint8_t recorded_data(int i);

void test_eprom_write_sets_vpp_regulator(void) {
    clear_bus_recording();
    firestarter_handle_t h = make_handle(0x07, 0, CMD_WRITE);
    configure_memory(&h);
    // Find any CTL write with CTRL_VPP_REGULATOR_ENABLE set
    bool vpp_seen = false;
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER &&
            (recorded_data(i) & CTRL_VPP_REGULATOR_ENABLE)) {
            vpp_seen = true; break;
        }
    }
    TEST_ASSERT_TRUE(vpp_seen);
}
```

### platformio.ini changes required

Each new `test_val_*` suite directory must be added to the `test_filter` allowlist in `[env:native]`. [VERIFIED: platformio.ini:80-87]
The `build_flags` must include `-I test/native/avr/test_val_<family>` for each new suite.

**IMPORTANT:** The 6 new suites must be added to `test_filter` and `build_flags` in `platformio.ini`. The current allowlist (lines 80-87) is explicit and a new suite NOT in the list will not run.

---

## Matrix Schema and Codegen Pattern (HARN-02 / D-01 / D-02)

### Authored matrix JSON schema

The authored input lives at e.g. `firestarter_app/tools/validation_matrix_spec.json`. Schema:

```json
{
  "schema_version": 1,
  "families": [
    {
      "id": "eprom",
      "handler": "configure_eprom",
      "protocols": [7, 8, 11],
      "rep_chip": "W27C512",
      "tier1": {
        "suite": "test_val_eprom",
        "assertions": [
          "vpp_regulator_enabled_on_write",
          "vpp_regulator_disabled_on_read",
          "op_pointer_write_set",
          "op_pointer_read_set"
        ]
      },
      "tier2": {
        "test_module": "test_val_wire_eprom",
        "commands": ["write", "read", "verify", "blank_check", "chip_id"]
      },
      "tier3": {
        "test_chip": "W27C512",
        "boards": ["leonardo"],
        "skip_boards": ["uno328pb"]
      }
    }
  ]
}
```

**Note:** Keep protocol IDs as integers (decimal 7 = 0x07) to avoid JSON hex parsing complexity.

### Codegen entrypoint pattern

The existing `tools/catalog/codegen.py` shows the authoritative pattern for this codebase [VERIFIED: codegen.py read]:
- Input: TOML/JSON source file
- Validation pass (raise on schema violation before emission)
- Deterministic emission: sorted order, no timestamps, LF line endings
- Banner: `/* DO NOT EDIT -- generated by tools/... */`

A new `tools/gen_validation_header.py` follows this exact shape. Emits `firestarter/test/native/avr/_shared/validation_matrix.h`:

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
    { 0x08, "eprom", "configure_eprom" },
    { 0x0B, "eprom", "configure_eprom" },
    { 0x0D, "eeprom28c", "configure_eeprom28c" },
    { 0x06, "flash3", "configure_flash3" },
    { 0x05, "flash4", "configure_flash4" },
    ...
};
```

**Committed vs on-the-fly:** Commit the generated header (like `messages.h` is committed). Native suites must compile without running the codegen script. Add a CI drift check that re-runs codegen and diffs the result (same pattern as the messages drift gate).

### Results artifact (emitted output — D-02)

`validation-matrix.json` is written by `dev validate-family` to the project root or a specified output dir:

```json
{
  "generated": "2026-06-16T12:00:00",
  "harness_version": "71",
  "cells": [
    {
      "family": "eprom",
      "board": "leonardo",
      "tier": 3,
      "verdict": "PASS",
      "evidence_sha": "abc123...",
      "retry_count": 0,
      "r1_mv": 270100
    },
    {
      "family": "sram",
      "board": "uno328pb",
      "tier": 3,
      "verdict": "SKIP-deferred",
      "reason": "uno328pb is N/A for program/write (999.2 brownout)"
    }
  ]
}
```

`validation-matrix.md` is a Markdown table rendered from the same data.

---

## Tier-2 Host Wire Round-Trip (HARN-01)

### make_comm / fake_serial fixture shape

From `firestarter_app/tests/conftest.py` [VERIFIED: file read]:

```python
# conftest.py provides:
# - fake_serial: _FakeSerial instance (BytesIO-backed)
# - make_comm: factory for SerialCommunicator bypassing real serial
```

The `_FakeSerial` implements `read(n)`, `readline()`, `in_waiting`, `write(...)`, `flush()`, `close()`, `is_open`, `port`, `timeout`. [VERIFIED: conftest.py:65-100]

**Tier-2 test pattern:**

```python
# tests/test_val_wire_eprom.py
def test_eprom_write_command_sends_algorithm_field(make_comm, fake_serial):
    comm = make_comm(fake_serial)
    # Inject a simulated OK response
    fake_serial.write(build_frame(MSG_ID_OK, b""))
    # Build chip config for W27C512 (protocol=0x07)
    from firestarter.database import EpromDatabase
    db = EpromDatabase()
    chip = db.get_eprom("W27C512")
    wire = db.convert_to_programmer(chip)
    # Assert the wire dict contains algorithm=0x07
    assert wire.get("algorithm") == 0x07
    # Assert dispatch() maps it to configure_eprom
    from tools.check_dispatch import dispatch
    assert dispatch(0x07, wire.get("type", 1)) == "configure_eprom"
```

The Tier-2 tests do not require real serial I/O — they validate that the host wire dict for each family's representative chip reaches the correct handler via the same `dispatch()` logic already exercised by `check_dispatch.py`.

---

## Tier-3 Runner: `dev validate-family` (HARN-01 / D-05 / D-06)

### Where it lands

`cli_handlers.py` — new `@dev.command(name="validate-family")` alongside the existing four dev subcommands (`dev read`, `dev reg`, `dev addr`, `dev consistency-check`). [VERIFIED: cli_handlers.py:902-1042]

### Composition — reuse not re-implement

`write_cycle_eprom` (eprom_operations.py:747) signature: [VERIFIED: file read]
```python
def write_cycle_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    source_image_path: str,
    runs: int = 5,
    output_dir: Optional[str] = None,
    operation_flags: int = 0,
) -> int:  # 0=PASS, 1=FAIL/mismatch, 2=hw-error
```

`consistency_check_eprom` (eprom_operations.py:546) signature:
```python
def consistency_check_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    runs: int = 3,
    output_dir: Optional[str] = None,
    keep_files: bool = True,
    max_diffs: int = 10,
    quiet: bool = False,
    operation_flags: int = 0,
    read_settling_us: int = 0,
    read_strobe_us: int = 0,
) -> int:  # 0=PASS, 1=FAIL, 2=hw-error
```

The runner composes them without re-implementing the read/write logic.

### SKIP-deferred logic (D-06)

```python
@dev.command(name="validate-family")
@click.argument("family", type=click.Choice(["eprom","eeprom28c","flash3","flash4","flash_intel","sram","all"]))
@click.option("--board", default=None)
@click.option("--chip", default=None)
@click.option("--source", default=None, type=click.Path())
@click.option("--output-dir", default=None)
@click.pass_obj
@map_typed_errors
def dev_validate_family(app, family, board, chip, source, output_dir):
    """Run the validation matrix for one or all families."""
    # If no board/port: record SKIP-deferred for all Tier-3 cells, emit artifact
    if not app.port or not board or not chip or not source:
        _emit_skip_deferred_artifact(family, reason="no board/chip/source provided", output_dir=output_dir)
        return  # exit 0 — milestone remains closeable
    # Otherwise: r1 precondition check → negative control → write_cycle + consistency
    ...
```

### SKIP-deferred makes milestone closeable

When `dev validate-family` is invoked with no hardware, it emits a `validation-matrix.json` with all Tier-3 cells as `SKIP-deferred`. Phase 71's success criterion only requires Tier-1 + Tier-2 cells GREEN. The SKIP-deferred scaffold means Phase 73 can fill in real results by re-running the same command with hardware attached.

---

## PASS Oracle Architecture (HARN-03 / D-08)

### Leonardo-only non-advisory PASS

The post-write SHA comparison in `write_cycle_eprom` [VERIFIED: eprom_operations.py:846-852] already implements this for all boards. The Phase 73 PASS oracle upgrades this to be strict (non-advisory) on Leonardo by:
- Running `write_cycle_eprom` with runs≥1 on Leonardo
- Comparing `readback_sha == source_sha` as the **authoritative** PASS signal
- Marking the same result as `advisory` (not FAIL) on other boards

**Board detection:** Use the board name from `app.eprom_operator.config` or the firmware identity string (already captured by the handshake in `serial_comm.py`).

### uno328pb = N/A for write cells

Hard-coded in the runner: if `board == "uno328pb"`, skip all Tier-3 program/write cells and record verdict=`N/A (brownout 999.2)`. [ASSUMED — from MEMORY.md `project_uno328pb_vpp_recal_and_program_brownout`; the brownout fact is in project memory, not code]

### Mandatory negative control

The negative control proves verify **can** fail. Two sub-tests:
1. **Wrong-file mismatch:** Run `consistency_check_eprom` with a source file containing a single-byte flip — expect return code 1 (FAIL).
2. **Blank/chip-out:** Run read on an empty socket — expect hw-error return code 2, OR a blank read that mismatches a non-blank source.

For Tier-1 (native Unity), the negative control is representable as an assertion test where the recording buffer confirms the VPP regulator was NOT enabled when a read-only handler ran:

```cpp
void test_eprom_read_does_not_enable_vpp_regulator(void) {
    clear_bus_recording();
    firestarter_handle_t h = make_handle(0x07, 0, CMD_READ);
    configure_memory(&h);
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER) {
            TEST_ASSERT_BITS_LOW(CTRL_VPP_REGULATOR_ENABLE, recorded_data(i));
        }
    }
}
```

### r1 ≈ 270000 calibration precondition

The Tier-3 runner reads the board's R1 value via `app.eprom_operator.hardware.get_config()` or equivalent. If `r1 < 200000` or `r1 > 340000` (±25% tolerance band around 270000), abort with `sys.exit(2)` before issuing any write command. [ASSUMED — the exact calibration field names in config need verification against `rurp_configuration_t` fields in firmware; planner should verify `r1` field path]

### Retry count capture

`write_cycle_eprom` already captures cycle count as `runs` parameter. The runner emits this as `retry_count` in the results artifact cell.

---

## check_dispatch.py Extension (HARN-04 / D-09)

### Current hollow `non_supported_dispatchable`

The `non_supported_dispatchable` list is declared at line 167, populated at lines 244-246 (counter only, never appended), and checked at lines 319, 387-396, 411-412. [VERIFIED: check_dispatch.py read]

The current logic (lines 239-246) explains why it's hollow: every non-supported chip is covered by the D-12 host guard (chip_resolver.resolve_chip raises before any wire dict is built), so the comment at line 244 says "non_supported_dispatchable remains empty — it exists as a future-regression detector."

**To populate it non-vacuously for HARN-04**, the invariant must become active for the newly-checkable case: a **family handler enabling VPP it must not**. This is a different axis from `support_status`.

### Per-family dispatch invariants to add

These are checkable purely from the chip data and the `dispatch()` result:

| Invariant | Failure Condition | Family |
|-----------|-------------------|--------|
| VPP invariant: flash3 never VPP | `dispatch(proto, mt) == "configure_flash3"` AND `vpp_mv > 6000` | 0x06 |
| VPP invariant: flash4 never VPP | `dispatch(proto, mt) == "configure_flash4"` AND `vpp_mv > 6000` | 0x05/0x35/0x39 |
| VPP invariant: sram never VPP | `dispatch(proto, mt) == "configure_sram"` AND `vpp_mv > 6000` | 0x0E/0x27/0x28/0x29 |
| VPP invariant: eeprom28c never VPP | `dispatch(proto, mt) == "configure_eeprom28c"` AND `vpp_mv > 6000` | 0x0D |
| SRAM protocols → configure_sram | `proto in SRAM_PROTOCOLS` AND `handler != "configure_sram"` | already exists as `sram_in_eprom` |
| flash_intel always 12V VPP | `dispatch(proto, mt) == "configure_flash_intel"` AND `vpp_mv < 10000` | 0x10 |

For `non_supported_dispatchable` to become non-hollow, the condition should be: a non-supported chip that `dispatch()` maps to a real handler (not `ERROR` or `not_implemented`) AND whose handler enables a VPP rail inconsistent with its `electrical.type`. Example: a chip tagged `support_status="vpp-exceeds-max"` that somehow still has `vpp_mv ≤ 22000` (contradicting the tag reason) and dispatches to `configure_eprom` — this is the VPP-exceeds-max tagging being wrong.

**Concrete implementation plan for check_dispatch.py:**

1. Add a `_FAMILY_VPP_INVARIANTS` dict mapping handler name → `(min_vpp_mv, max_vpp_mv)`:
   ```python
   _FAMILY_VPP_INVARIANTS = {
       "configure_eprom":       (0, 22000),     # up to RURP ceiling
       "configure_eeprom28c":   (0, 6000),      # 5V only — no VPP
       "configure_flash3":      (0, 6000),      # 5V only
       "configure_flash4":      (0, 6000),      # 5V only
       "configure_flash_intel": (10000, 22000), # requires 12V VPP
       "configure_sram":        (0, 6000),      # 5V only — never VPP
   }
   ```

2. For each chip where `handler` is in `_FAMILY_VPP_INVARIANTS`, assert `vpp_mv` falls in the range. Violations go into a new `family_vpp_violations` list that fails the gate.

3. **Populate `non_supported_dispatchable`** with chips that have `chip_ss != "supported"` AND `handler` is a real handler AND the VPP invariant is violated — meaning the chip has both a classification problem (non-supported) AND a VPP mismatch. This is the condition that was previously hollowed out by the "D-12 host guard covers all" logic but now has a concrete test signal.

4. The existing `WR-03` assertion (`non_dispatchable_count == non_supported_count`) must still hold — no chip falls through both the handler check and the VPP check without being counted.

---

## Common Pitfalls

### Pitfall 1: Define-guard ordering in new per-family host_stubs.cpp

**What goes wrong:** The recording buffer's `rurp_write_to_register` and the original no-op in the `#else` branch are both defined in the same `.inc` file. If a new suite includes `host_stubs_common.inc` WITHOUT defining `HOST_STUBS_RECORD_BUS`, the no-op applies and no recording happens — but the test tries to assert on `bus_recording_count()` which doesn't exist as a symbol.
**Why it happens:** The recording API functions (`clear_bus_recording`, `bus_recording_count`, etc.) are only compiled when `HOST_STUBS_RECORD_BUS` is defined.
**How to avoid:** Every per-family validation suite's `host_stubs.cpp` must `#define HOST_STUBS_RECORD_BUS` BEFORE the `#include "../_shared/host_stubs_common.inc"` line. The existing dispatch suite's `host_stubs.cpp` (which must remain unchanged) must NOT define the flag.
**Warning signs:** Linker error "undefined reference to `clear_bus_recording`" or "undefined reference to `bus_recording_count`" when compiling an existing suite.

### Pitfall 2: configure_sram no-op records zero writes — test must not assert non-zero

**What goes wrong:** `configure_sram` is currently a one-liner that only logs. [VERIFIED: sram.cpp:15-17] If a Tier-1 test for the SRAM family asserts that the handler writes specific CTL register values, it will fail immediately — because the handler does nothing.
**Why it happens:** SRAM is deliberately a no-op today; the SRAM no-op question is intentionally deferred to Phase 73 (VAL-06, D-07).
**How to avoid:** The SRAM Tier-1 suite (test_val_sram) must assert `bus_recording_count() == 0` after configure_memory runs — confirming the no-op state. This is a GREEN test that documents current behavior, NOT a test that requires the handler to do something.
**Warning signs:** Test author writes `TEST_ASSERT_NOT_EQUAL(0, bus_recording_count())` for SRAM — this will be RED and must not be committed.

### Pitfall 3: test_filter allowlist not updated in platformio.ini

**What goes wrong:** New `test_val_*` suites are discovered by PlatformIO under `test/native/avr/` but NOT listed in the `test_filter` allowlist in `platformio.ini`. PIO's comment explains: "Using positive test_filter allowlist (test_ignore was being honored inconsistently — likely PIO version quirk)." [VERIFIED: platformio.ini:78-80]
**Why it happens:** The allowlist was established because `test_ignore` was unreliable. Adding a new suite directory without updating `test_filter` means it silently doesn't run.
**How to avoid:** For each new `test_val_*` suite: add `native/avr/test_val_<family>` to `test_filter` AND `-I test/native/avr/test_val_<family>` to `build_flags` in `[env:native]`.

### Pitfall 4: Authored JSON and emitted results artifact filenames must be unambiguous

**What goes wrong:** The planner names both files with "validation-matrix" and they get confused. A CI script regenerates the authored input from the emitted output (backwards).
**Why it happens:** D-02 locks them as separate files but doesn't specify names.
**How to avoid:** Use clearly distinct names: `validation_matrix_spec.json` (authored, underscore, singular, in `tools/`) vs `validation-matrix.json` (emitted, hyphen, in root or output dir). Never write the authored spec from the runner.

### Pitfall 5: mypy strict scope on cli_handlers.py

**What goes wrong:** `cli_handlers.py` is in the mypy strict island (Phase 42 D-06). A new `dev validate-family` subcommand that uses untyped intermediate values fails the mypy gate.
**Why it happens:** The CI gate runs `mypy` strict on 8 modules including `cli_handlers.py`. [VERIFIED: firestarter_app/CLAUDE.md]
**How to avoid:** Type-annotate the new handler fully. The `@map_typed_errors` decorator is already present on other dev subcommands and must be applied here too (pattern: `cli_handlers.py:923-924`).

### Pitfall 6: VPP-invariant threshold for "no VPP" families

**What goes wrong:** Some flash4 chips list `vpp_mv = 12000` in the DB as a write-protect input (not a programming VPP). Setting the invariant threshold at `vpp_mv > 0` would flag all of them as violations.
**Why it happens:** The DB's `vpp_mv` field encodes both programming VPP and write-protect-input VPP. For AMD/SST flash, 12V is on the WP pin, not needed for programming.
**How to avoid:** Use `vpp_mv > 6000` as the threshold for "claims elevated VPP for flash3/flash4/sram/eeprom28c" (the programming range). Cross-check against CHIP_FAMILIES.md §2.1: "VPP: 12 V (SST39SF, AT29Cxxx) — can be pulled HIGH to enable write, or tied to VCC; not required for programming itself." [VERIFIED: CHIP_FAMILIES.md:189]

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Register-write recording in tests | A custom recording framework | `#define HOST_STUBS_RECORD_BUS` guard in the existing shared stub | WR-06 consolidation; adding a second stub file re-introduces the ~120-line drift WR-06 removed |
| Write+readback SHA comparison | A re-implementation of the read path | `write_cycle_eprom` return code 0/1/2 | The method already does erase→write→N readbacks; implementing it again risks diverging from the production code path |
| Consistency check logic | A re-implementation of N-read + SHA compare | `consistency_check_eprom` return code 0/1/2 | The method is already proven and has existing pytest coverage |
| Dispatch simulation | A re-implementation of `configure_memory` logic | `check_dispatch.dispatch()` function | Already mirrors firmware dispatch order exactly; adding another mirror creates drift risk |
| Wire dict construction | Constructing JSON commands manually in tests | `EpromDatabase.convert_to_programmer()` | The production converter already handles address-bus remapping, vpp_mv encoding, bus-config construction |
| Results artifact rendering | A custom markdown templating engine | Python f-strings / simple table formatting | The artifact is a simple 2D table; over-engineering introduces dependencies |

**Key insight:** Every "new" capability in Phase 71 has an existing primitive in the codebase. The work is composition and wiring, not invention.

---

## Code Examples

### Example 1: Per-family native suite structure (Tier-1)

Based on `test_dispatch/test_configure_memory.cpp` pattern [VERIFIED: file read]:

```cpp
// test_val_eprom/test_val_eprom.cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
extern "C" {
#include "memory.h"
}
#include "firestarter.h"
// Recording API — symbols exist because host_stubs.cpp defines HOST_STUBS_RECORD_BUS
extern "C" void clear_bus_recording();
extern "C" int  bus_recording_count();
extern "C" uint8_t recorded_reg(int i);
extern "C" uint8_t recorded_data(int i);

using namespace fakeit;

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    clear_bus_recording();
}

void tearDown(void) {}

static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol = protocol; h.mem_type = mem_type; h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

/* PROVABLE BY SIDE-EFFECT: write init sets VPP regulator via CTL register */
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
    TEST_ASSERT_TRUE_MESSAGE(vpp_seen, "configure_eprom write must enable VPP regulator via CTL");
}

/* NEGATIVE CONTROL: read does NOT enable VPP regulator */
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

int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();
    RUN_TEST(test_eprom_write_enables_vpp_regulator_via_ctl);
    RUN_TEST(test_eprom_read_does_not_enable_vpp_regulator);
    // ... (protocol 0x08, 0x0B variants)
    return UNITY_END();
}
```

### Example 2: check_dispatch.py per-family VPP invariant addition

```python
# Addition to check_dispatch.py (after existing _SRAM_PROTOCOLS definition)

# Per-family VPP range invariants (Phase 71 HARN-04).
# Maps handler name → (min_vpp_mv, max_vpp_mv) that a chip using this handler
# must declare in chip_database.json.
# 6000 mV threshold: chips listing 12V on their WP pin (AMD/SST flash) are
# not "programming VPP" — the 12V is just write-protect, not asserted by firmware.
_FAMILY_VPP_INVARIANTS = {
    "configure_eprom":       (0, 22000),     # RURP ceiling 22V; any VPP up to that
    "configure_eeprom28c":   (0, 6000),      # 5V-only EEPROM — no elevated VPP
    "configure_flash3":      (0, 6000),      # AMD unlock flash — 5V only
    "configure_flash4":      (0, 6000),      # page-write flash — 5V only
    "configure_flash_intel": (10000, 22000), # Intel 28F — requires 12V
    "configure_sram":        (0, 6000),      # SRAM — never VPP (BLOCKER-2)
}

# Activation in main() scan loop (after existing handler determination):
family_vpp_violations = []
# ...
vpp_mv = chip.get("programming", {}).get("vpp_mv", 0)
if handler in _FAMILY_VPP_INVARIANTS:
    lo, hi = _FAMILY_VPP_INVARIANTS[handler]
    if not (lo <= vpp_mv <= hi):
        family_vpp_violations.append(
            f"{mfg}/{part} proto=0x{proto:02X} handler={handler} "
            f"vpp_mv={vpp_mv} outside [{lo},{hi}]"
        )
```

---

## Chip Family Dispatch Inventory (verified)

The 6 families and their algorithm IDs, per `memory.cpp:configure_memory` [VERIFIED: file read] and `firestarter/CLAUDE.md` [VERIFIED: system-reminder]:

| Family | Handler | Protocols | VPP | Notes |
|--------|---------|-----------|-----|-------|
| UV-EPROM | `configure_eprom` | 0x07, 0x08, 0x0B | 13-18V | VPP via CTRL_VPP_REGULATOR_ENABLE + drop resistor |
| 5V EEPROM | `configure_eeprom28c` | 0x0D | none (5V) | SDP-disable + DQ7 page poll |
| Flash AMD (sector) | `configure_flash3` | 0x06 | none (5V) | AMD unlock, sector erase |
| Flash AMD/SST (page) | `configure_flash4` | 0x05, 0x35, 0x39 | none (5V) | Page write + DQ7 |
| Flash Intel | `configure_flash_intel` | 0x10 | 12V (P1) | Command register, SR polling |
| SRAM/NVRAM | `configure_sram` | 0x0E, 0x27, 0x28, 0x29 | none (5V) | Currently no-op (sram.cpp:15-17) |

Note: `configure_flash4` includes 0x39 which is "future-proofed" (0 chips in current DB) per firmware CLAUDE.md. The SRAM handler currently has NO function pointer wiring — it only calls `LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM)`.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Test dispatch by op-pointer presence only | Test dispatch by side-effect (CTL register sequence) | Phase 71 (this phase) | Handler provable even if partially wired |
| `non_supported_dispatchable` always empty (hollow gate) | Populate with VPP-invariant violations | Phase 71 | Closes v1.12 CR-01 tech debt |
| No family-level Tier-2 wire tests | Per-family Tier-2 pytest round-trips via fake_serial | Phase 71 | Validates host wire dict without hardware |
| No results artifact | `validation-matrix.{json,md}` emitted by runner | Phase 71 | Explicit partial coverage vs silent |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `uno328pb` is N/A for program/write cells (999.2 brownout) — from project MEMORY.md | PASS Oracle | Low — multiple memory entries confirm; would only affect which cells are N/A not the architecture |
| A2 | r1 calibration precondition should use r1 ≈ 270000 with ±25% tolerance band | PASS Oracle | Low — exact tolerance band is a planner/implementation detail, not a blocker |
| A3 | r1 value is accessible via `app.eprom_operator.hardware.get_config()` or similar | PASS Oracle | Medium — exact field path in `rurp_configuration_t` needs verification against firmware struct; planner should grep `rurp_get_config()` return fields |
| A4 | The 6000 mV threshold correctly separates WP-pin VPP (12V, not needed for programming) from true programming VPP violations in flash3/flash4 | check_dispatch | Medium — verify against CHIP_FAMILIES.md and chip_database.json vpp_mv values before setting; if any flash3/flash4 chips legitimately need >6V programming, threshold must be raised |
| A5 | Generated C++ header should be committed (not on-the-fly) to avoid build-time Python dependency in firmware native tests | Matrix Codegen | Low — the alternative (on-the-fly) also works; determinism contract is the requirement |

---

## Open Questions

1. **SRAM function pointer wiring for VAL-06 (Phase 73)**
   - What we know: `configure_sram` is currently a one-liner (sram.cpp:15-17). Recording test will assert zero CTL writes.
   - What's unclear: Will the Tier-1 SRAM test be GREEN (assert no-op) or RED (assert function pointers wired)? Phase 71's test should assert the CURRENT state (no-op = GREEN), not the desired Phase 74 FIX-01 state.
   - Recommendation: Write the SRAM Tier-1 test to assert `bus_recording_count() == 0` for the current no-op. Phase 74 (FIX-01) will update it to RED→GREEN after the fix.

2. **0x35 and 0x39 in KNOWN_PROTOCOLS mismatch**
   - What we know: `check_dispatch.py:KNOWN_PROTOCOLS` does NOT include 0x35 and 0x39 (intentionally, per comment at line 79-92). But firmware dispatches both to `configure_flash4`.
   - What's unclear: Should the per-family dispatch invariants for flash4 include 0x35 and 0x39 in their scope?
   - Recommendation: Yes — the FAMILY_VPP_INVARIANTS covers the handler name, not protocol IDs. `dispatch(0x35, ...)` returns `"configure_flash4"` and would be covered by the flash4 VPP invariant automatically.

3. **Evidence SHA in the results artifact**
   - What we know: The artifact cell needs `evidence_sha` (HARN-02).
   - What's unclear: Which file to SHA-hash for Tier-1 and Tier-2 cells (no readback file for software tests).
   - Recommendation: For Tier-1/Tier-2 cells, use `hashlib.sha256(b"tier1-pass-no-file").hexdigest()` as a sentinel — or emit `evidence_sha: null` with `tier: 1` to signal software-only. Reserve the actual SHA for Tier-3 readback files.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `pio test -e native` | Tier-1 native suites | ✓ (PlatformIO) | Already in CI | — |
| pytest | Tier-2 host tests | ✓ | Already in dev env | — |
| Python 3.x | Matrix codegen | ✓ | 3.12 in devcontainer | — |
| Arduino board (Leonardo) | Tier-3 HIL | Not required for Phase 71 | — | SKIP-deferred cells |

---

## Validation Architecture

> Note: `workflow.nyquist_validation` key is absent from `.planning/config.json` — treat as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Firmware framework | Unity (PlatformIO `[env:native]`) |
| Host framework | pytest |
| Native run command | `pio test -e native` |
| Host run command | `cd firestarter_app && pytest tests/ -x` |
| Combined CI command | `pio test -e native && cd firestarter_app && pytest tests/ --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HARN-01 (Tier-1) | Recording bus stub captures CTL register writes per family | Unit (native Unity) | `pio test -e native -f "*test_val_*"` | ❌ Wave 0 |
| HARN-01 (Tier-2) | Host wire dict for each family dispatches to correct handler | Unit (pytest) | `pytest tests/test_val_wire_*.py -x` | ❌ Wave 0 |
| HARN-01 (Tier-3) | `dev validate-family` composes cycle methods without re-impl | Integration (pytest) | `pytest tests/test_validate_family_cmd.py -x` | ❌ Wave 0 |
| HARN-02 | Authored matrix JSON distinct from emitted results artifact | Unit (pytest) | `pytest tests/test_matrix_schema.py -x` | ❌ Wave 0 |
| HARN-02 | Codegen produces deterministic C++ header | Unit (pytest) | `pytest tests/test_gen_validation_header.py -x` | ❌ Wave 0 |
| HARN-02 | Emitted `validation-matrix.json` has correct schema | Unit (pytest) | `pytest tests/test_matrix_artifact.py -x` | ❌ Wave 0 |
| HARN-03 | Negative control (wrong file) returns FAIL not PASS | Unit (pytest) | `pytest tests/test_validate_oracle.py::test_negative_control -x` | ❌ Wave 0 |
| HARN-03 | uno328pb cells are N/A for write | Unit (pytest) | `pytest tests/test_validate_oracle.py::test_uno328pb_na -x` | ❌ Wave 0 |
| HARN-04 | check_dispatch.py per-family VPP invariants pass | Integration (pytest/script) | `python tools/check_dispatch.py` | ✅ (script exists; extension needed) |
| HARN-04 | `non_supported_dispatchable` populated and gate fails on violation | Unit (pytest) | `pytest tests/test_check_dispatch_invariants.py -x` | ❌ Wave 0 |
| HARN-01 existing | Existing suites compile unchanged (no recording when flag off) | Regression (native Unity) | `pio test -e native -f "*test_dispatch*"` | ✅ |

### Sampling Rate

- **Per task commit (firmware):** `pio test -e native -f "*test_dispatch*"` (existing regression baseline)
- **Per task commit (host):** `cd firestarter_app && pytest tests/ -x --cov-fail-under=70 && python tools/check_dispatch.py`
- **Per wave merge:** full `pio test -e native && cd firestarter_app && pytest tests/ --cov-fail-under=70`
- **Phase gate:** All Tier-1 and Tier-2 test cells GREEN; Tier-3 SKIP-deferred scaffold in place; `check_dispatch.py` exits 0 before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `firestarter/test/native/avr/test_val_eprom/` — covers HARN-01 Tier-1 eprom
- [ ] `firestarter/test/native/avr/test_val_eeprom28c/` — covers HARN-01 Tier-1 eeprom28c
- [ ] `firestarter/test/native/avr/test_val_flash3/` — covers HARN-01 Tier-1 flash3
- [ ] `firestarter/test/native/avr/test_val_flash4/` — covers HARN-01 Tier-1 flash4
- [ ] `firestarter/test/native/avr/test_val_flash_intel/` — covers HARN-01 Tier-1 flash_intel
- [ ] `firestarter/test/native/avr/test_val_sram/` — covers HARN-01 Tier-1 sram
- [ ] `firestarter_app/tests/test_val_wire_*.py` — 6 files, covers HARN-01 Tier-2
- [ ] `firestarter_app/tests/test_validate_family_cmd.py` — covers HARN-01 Tier-3 scaffold
- [ ] `firestarter_app/tests/test_matrix_schema.py` — covers HARN-02
- [ ] `firestarter_app/tests/test_validate_oracle.py` — covers HARN-03
- [ ] `firestarter_app/tests/test_check_dispatch_invariants.py` — covers HARN-04
- [ ] `firestarter_app/tools/gen_validation_header.py` — codegen entrypoint (D-01)
- [ ] `firestarter_app/tools/validation_matrix_spec.json` — authored matrix (D-01)
- [ ] `firestarter/test/native/avr/_shared/validation_matrix.h` — GENERATED header

---

## Security Domain

> `security_enforcement` is absent from `.planning/config.json` — treat as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Not applicable — no user-facing auth |
| V3 Session Management | no | Not applicable — no sessions |
| V4 Access Control | no | Not applicable — local CLI tool |
| V5 Input Validation | yes | Authored matrix JSON validated before codegen emission; TOML catalog validator pattern (codegen.py:167-198) |
| V6 Cryptography | no | SHA-256 used for verification comparison only (stdlib hashlib), not security-critical |

### Known Threat Patterns for this Phase

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Forged `validation-matrix.json` claiming PASS for a cell that wasn't tested | Tampering | Artifact is EMITTED by the runner, not accepted as input; codegen only reads authored spec; runner only writes results |
| Recording buffer overflow in native tests (>256 entries) | Denial of service | Cap buffer at `HOST_STUBS_MAX_RECORDING = 256`; no overflow is possible (firmware configure_* functions make <20 register writes per initialization) |

---

## Sources

### Primary (HIGH confidence — VERIFIED from codebase)

- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — recording stub extension point, existing opt-out guard pattern
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — authoritative native suite pattern
- `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` — single-include pattern
- `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp` — opt-out guard pattern
- `firestarter/platformio.ini` §`[env:native]` — test_filter allowlist, build_flags, lib_deps
- `firestarter/src/proms/memory.cpp` — configure_memory dispatch order (verified: lines 74-136)
- `firestarter/src/proms/sram.cpp` — configure_sram no-op (verified: lines 15-17)
- `firestarter/src/proms/eprom.cpp` — function pointer wiring pattern (verified: lines 44-62)
- `firestarter_app/tests/conftest.py` — make_comm / fake_serial fixture API
- `firestarter_app/firestarter/eprom_operations.py` — write_cycle_eprom (line 747), consistency_check_eprom (line 546), 3-way verdict
- `firestarter_app/firestarter/cli_handlers.py` — dev group structure (line 905), consistency-check subcommand (line 1044)
- `firestarter_app/tools/check_dispatch.py` — existing gate structure, non_supported_dispatchable hollow detector (lines 167, 244-246)
- `firestarter_app/tools/catalog/codegen.py` — codegen pattern (TOML→C++/Python, determinism contract)
- `.planning/phases/71-validation-harness-matrix/71-CONTEXT.md` — 10 locked decisions D-01..D-10
- `.planning/REQUIREMENTS.md` — HARN-01..HARN-04 requirement text

### Secondary (MEDIUM confidence)

- `.planning/research/HARDWARE_SIM_SPEC.md` — register write sequence semantics, CTL bit definitions
- `.planning/research/CHIP_FAMILIES.md` — per-family VPP requirements, algorithm details
- `.planning/research/ARCHITECTURE_PATTERNS.md` — dispatch pattern, function pointer handle struct
- `firestarter/CLAUDE.md` — confirmed dispatch order, handler→protocol mapping table
- `firestarter_app/CLAUDE.md` — mypy strict scope (cli_handlers.py is in the strict island), CI gate commands

---

## Metadata

**Confidence breakdown:**
- Recording stub pattern: HIGH — exact extension point identified in existing code with anticipatory comment
- Tier-1 native suite pattern: HIGH — verified from working examples in test_dispatch
- Tier-2 fixture pattern: HIGH — verified from conftest.py
- Tier-3 composition API: HIGH — write_cycle_eprom and consistency_check_eprom signatures and return codes verified
- check_dispatch.py anatomy: HIGH — full file read, hollow detector mechanism understood
- Matrix codegen pattern: HIGH — codegen.py shape verified
- PASS oracle (D-08): MEDIUM — oracle mechanics verified, but exact r1 config field path is ASSUMED (A3)
- SRAM no-op state: HIGH — sram.cpp:15-17 is definitively a no-op

**Research date:** 2026-06-16
**Valid until:** 2026-07-16 (stable firmware architecture; unlikely to change)
