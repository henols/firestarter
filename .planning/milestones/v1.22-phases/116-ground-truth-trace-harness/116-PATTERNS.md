# Phase 116: GROUND TRUTH + TRACE HARNESS - Pattern Map

**Mapped:** 2026-07-27
**Files analyzed:** 19 (14 new, 4 modified, 1 retired)
**Analogs found:** 17 / 19

Scope note: this phase spans three repos — `firestarter/` (firmware native test harness),
`firestarter_app/` (host generator + gates), and the meta repo (`.planning/` docs). Every analog
below is an existing in-tree file; none of them may be modified except where marked MODIFIED.

---

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|---|
| `test/native/avr/_shared/host_stubs_common.inc` **(MODIFIED)** | fw | test-harness / stub layer | event-driven (side-effect recording) | *itself* — the `HOST_STUBS_RECORD_BUS` block at `:54-80` | exact (self-precedent) |
| `test/native/avr/test_sdp_harness/host_stubs.cpp` **(NEW)** | fw | test fixture (stub TU) | config | `test_val_eeprom28c/host_stubs.cpp` | exact |
| `test/native/avr/test_sdp_harness/test_sdp_harness.cpp` **(NEW)** | fw | test (always-green) | request-response + trace assert | `test_val_eeprom28c.cpp` + `test_val_5v_page.cpp` (:199-233) | exact |
| `test/native/avr/test_sdp_harness/sdp_expected.h` **(NEW)** | fw | test data (literal tuple arrays) | transform | `_shared/validation_matrix.h` (static table shape only — hand-authored, not generated) | partial |
| `test/native/avr/test_eeprom28c_sdp/host_stubs.cpp` **(NEW)** | fw | test fixture (stub TU) | config | `test_val_eeprom28c/host_stubs.cpp` | exact |
| `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` **(NEW)** | fw | test (RED, parked) | request-response + trace assert | `test_eeprom28c_chip_id.cpp` (handle+mock idiom) + `test_val_5v_page.cpp` (RED-before-fix idiom) | exact |
| `test/native/avr/test_eeprom28c_sdp/sdp_expected_fixed.h` **(NEW)** | fw | test data | transform | same as `sdp_expected.h` | partial |
| `test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` **(NEW)** | fw | doc/evidence fixture | — | `.planning/notes/dev-test-unknown-chip-fail-fast.md` (prose shape) | partial |
| `test/native/avr/_shared/sdp_bus_config.h` **(NEW, GENERATED)** | fw | generated artifact | transform | `_shared/validation_matrix.h` | exact |
| `platformio.ini` **(MODIFIED)** | fw | config | — | *itself* — `[env:native]` `test_filter` + `build_flags -I` allowlists | exact |
| `test/native/avr/test_eeprom28c_chip_id/` **(RETIRED)** | fw | test | — | — | n/a (delete; assertions migrate per D-12) |
| `tools/gen_sdp_bus_config.py` **(NEW)** | app | generator (tool) | batch transform | `tools/gen_validation_header.py` | exact |
| `tests/test_sdp_bus_config_drift.py` **(NEW)** | app | test (drift gate) | file-I/O + subprocess | `tests/test_gen_validation_header.py` | exact |
| `tests/test_sdp_db_invariant.py` **(NEW)** | app | test (DB invariant) | batch read | `tests/test_check_dispatch_invariants.py` | role-match |
| `tools/check_no_log_in_sdp_window.py` **(NEW)** | app | checker (AST/source scan) | batch transform | `tools/check_devtest_orchestrator.py` | exact |
| `tests/test_check_no_log_in_sdp_window.py` **(NEW)** | app | test (anti-hollow pairing) | subprocess + env override | `tests/test_check_devtest_orchestrator.py` | exact |
| `tests/fixtures/planted_log_in_window.*` **(NEW)** | app | planted-violation fixture | — | the tmp-file "bad source" fixtures in `test_check_devtest_orchestrator.py` | exact |
| `.planning/phases/116-.../116-PREMISE.md` **(NEW)** | meta | doc | — | `.planning/notes/dev-test-unknown-chip-fail-fast.md` | exact (named by CONTEXT §specifics) |
| `.planning/PROJECT.md` **(MODIFIED)** | meta | doc | — | *itself* — the two existing ⚠ correction blocks | exact |

---

## Pattern Assignments

### `firestarter/test/native/avr/_shared/host_stubs_common.inc` (MODIFIED — harness/stub, event-driven)

**Analog:** itself. The `HOST_STUBS_RECORD_BUS` block is the in-tree precedent (Phase 71 HARN-01)
for exactly the second-opt-in-flag shape TRACE-01 needs. Copy its structure, not just its spirit.

**Opt-in-flag documentation-comment pattern** (`:42-54`) — the new flag needs an equivalent block:
```c
/* Recording bus stub — Phase 71 HARN-01 / D-04.
 * Define HOST_STUBS_RECORD_BUS before including this file to activate the
 * recording version. Existing suites (test_dispatch, test_cobs_*,
 * test_read_timing, test_messages, test_data_input, test_not_implemented,
 * test_frame_vectors) MUST NOT define this flag — flag off = today's no-op
 * behavior is preserved byte-exactly. This is an opt-IN guard (inverse of
 * the opt-OUT HOST_STUBS_CUSTOM_VOLTAGE_MV / HOST_STUBS_CUSTOM_HW_REVISION
 * guards above). */
#ifdef HOST_STUBS_RECORD_BUS
#define HOST_STUBS_MAX_RECORDING 256
```

**Recorder body pattern to mirror** (`:57-75`) — buffer + count + `extern "C"` accessor trio +
bounded push. The new strobe recorder keeps this exact accessor shape (`clear_*`, `*_count()`,
per-field indexed getters) so test files read identically:
```c
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
Divergence the plan must add (research §Code Examples, CORRECTION 1 / Pitfall 2): an
`s_strobe_overflow` flag on the `else` branch of the bounds check (the existing recorder silently
drops), and `HOST_STUBS_MAX_STROBES 512`.

**Opt-OUT guard pattern the new flag must reuse verbatim** (`:110-114`, `:125-141`) — the six
redefinition collisions from CORRECTION 1 are resolved by wrapping existing stubs in exactly this
shape:
```c
#ifndef HOST_STUBS_CUSTOM_VOLTAGE_MV
extern "C" uint16_t rurp_read_voltage_mv() { return 0; }
#endif
...
#ifdef HARDWARE_REVISION
extern "C" void rurp_detect_hardware_revision() {}
#ifndef HOST_STUBS_CUSTOM_HW_REVISION
extern "C" uint8_t rurp_get_hardware_revision() { return 0; }
#endif
extern "C" uint8_t rurp_get_physical_hardware_revision() { return 0; }
extern "C" uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    return (uint8_t)data;
}
#endif
```
The stubs to guard are at `:82` (`rurp_read_from_register`), `:90` (`rurp_set_control_pin`),
`:98` (`rurp_write_data_buffer`), and the whole `HARDWARE_REVISION` block opener at `:125`.

---

### `firestarter/test/native/avr/test_sdp_harness/host_stubs.cpp` and `test_eeprom28c_sdp/host_stubs.cpp` (NEW — test fixture, config)

**Analog:** `firestarter/test/native/avr/test_val_eeprom28c/host_stubs.cpp` (full file, 29 lines).

**Copy this entire shape** — banner, the `extern "C"` include block, the flag-BEFORE-include
ordering comment, the relative `.inc` include:
```c
/*
 * Phase 71 Plan 04 — host stub TU for the test_val_eeprom28c Tier-1 suite.
 * Phase 6 WR-06 — shared stub body lives in ../_shared/host_stubs_common.inc.
 *
 * Suite-specific extensions:
 *   - HOST_STUBS_RECORD_BUS: activate the recording buffer ...
 *
 * PITFALL 1 (from 71-PATTERNS.md): HOST_STUBS_RECORD_BUS MUST be defined
 * BEFORE #include of host_stubs_common.inc.
 */
#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

#define HOST_STUBS_RECORD_BUS
#include "../_shared/host_stubs_common.inc"
```
Divergence (D-05 + research §"The new suite's `host_stubs.cpp`"): substitute the new flag name,
then append `#include "rurp_register_utils.h"` **after** the `.inc`, plus the
`reset_register_cache(lsb, msb, ctrl)` seam. Keep the "MUST be defined BEFORE" comment — it is a
recorded pitfall from the analog's own PATTERNS file.

---

### `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp` (NEW — always-green suite)

**Analog:** `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` (whole file).

**Imports + recording-API extern block** (`:31-47`):
```c
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>

extern "C" {
#include "memory.h"
}
#include "firestarter.h"
#include "rurp_pinout.h"

using namespace fakeit;

/* Recording API — symbols compiled because host_stubs.cpp defines HOST_STUBS_RECORD_BUS. */
extern "C" void clear_bus_recording();
extern "C" int  bus_recording_count();
extern "C" uint8_t recorded_reg(int i);
extern "C" uint8_t recorded_data(int i);
```

**`setUp` pattern** (`:49-55`) — extend, do not replace:
```c
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    clear_bus_recording();
}
void tearDown(void) {}
```
Mandatory additions (Pitfall 3 / CORRECTION 1): `delayMicroseconds`, `delay`, `millis` mocks and
`reset_register_cache(...)`. Comment *why*, or a later editor deletes them as unused.

**`make_handle` factory pattern** (`:59-67`) — one zero-init `firestarter_handle_t h = {};` builder
per case class, protocol/cmd/response_code/chip_id/mem_size only:
```c
static firestarter_handle_t make_handle(uint8_t cmd) {
    firestarter_handle_t h = {};
    h.protocol   = 0x0D;
    h.cmd        = cmd;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id    = 0; /* skip chip-id branch */
    h.mem_size   = 32768; /* 32 KB (AT28C256) */
    return h;
}
```

**Named-message trace assert helper pattern** (`:73-84`) — the shape D-06's element-by-element
comparator replaces, but the `TEST_ASSERT_*_MESSAGE(..., ctx)` + `const char* ctx` context-string
convention carries over verbatim:
```c
static void assert_no_vpp_in_recording(const char* ctx) {
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER) {
            TEST_ASSERT_BITS_LOW_MESSAGE(
                (uint8_t)CTRL_VPP_REGULATOR_ENABLE, recorded_data(i), ctx);
        }
    }
}
```
D-06 upgrade: the new comparator must build the message so it **names the diverging index** — the
analog's `ctx` string is static, which is the weakness D-06 explicitly raises the bar on.

**`main()` pattern** (`:116-126`) — explicit `RUN_TEST` list with section comments, never a
registration macro:
```c
int main(int argc, char** argv) {
    (void)argc; (void)argv;
    UNITY_BEGIN();
    /* 5V-only proof: no VPP-enable CTL bit for any command in the configure phase */
    RUN_TEST(test_eeprom28c_read_configure_no_vpp);
    ...
    return UNITY_END();
}
```

**Secondary analog for the `protocol != 0x0D` → `0xBB` negative (D-04 item 4):**
`test_not_implemented/test_not_implemented.cpp:52-60` — copy this case body wholesale:
```c
void test_protocol_0x11_fwh_not_implemented(void) {
    firestarter_handle_t h = make_handle(0x11, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    TEST_ASSERT_NULL(h.firestarter_operation_init);
    TEST_ASSERT_NULL(h.firestarter_operation_main);
    TEST_ASSERT_NULL(h.firestarter_operation_end);
}
```

---

### `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (NEW — RED, parked)

**Analog A (handle + function-pointer mock idiom):**
`firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` — the file being
retired. Its handle builder and the `configure_memory` re-assign hazard migrate; its *scripted*
mock does not.

**Mock function-pointer set + handle builder** (`:39-82`) — keep, with `mock_get_data_scripted`
replaced by an address-keyed `switch (addr)` (research Pattern 3):
```c
static void mock_set_ctrl_reg(struct firestarter_handle*, rurp_register_t, bool) {}
static bool mock_get_ctrl_reg(struct firestarter_handle*, rurp_register_t) { return 0; }
static void mock_set_data(struct firestarter_handle*, uint32_t, uint8_t) {}

static firestarter_handle_t make_28c_handle(uint16_t expected_chip_id, uint32_t ctrl_flags) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.mem_size = 32768;  /* AT28C256 — mfr_addr = mem_size - 64 = 0x7FC0 */
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = expected_chip_id;
    h.ctrl_flags = ctrl_flags | FLAG_SKIP_BLANK_CHECK;
    h.firestarter_set_control_register = mock_set_ctrl_reg;
    h.firestarter_get_control_register = mock_get_ctrl_reg;
    h.firestarter_set_data = mock_set_data;
    h.firestarter_get_data = mock_get_data_scripted;
    return h;
}
```

**The load-bearing re-assign-after-configure step** (`:106-109`) — must survive migration; research
Pattern 3 notes `firestarter_set_data` needs the same treatment, which the analog's comment misses:
```c
    configure_memory(&h);
    /* Re-assign after configure_memory() overwrites the function pointer. */
    h.firestarter_get_data = mock_get_data_scripted;
    h.firestarter_operation_init(&h);
```

**The three fixture sites to retire (TRACE-04 criterion 4, Pitfall 6)** — `:104`, `:140`, `:160`,
all of this exact form:
```c
    s_mock_bytes[2] = 0x20;  /* satisfies eeprom28c_wait_for_write(0x5555, 0x20) */
```

**Analog B (RED-before-fix suite documentation idiom):**
`test_val_5v_page/test_val_5v_page.cpp:150-175` + `:219-233`. Copy the header-comment convention
that states, in the file, what is RED today and why:
```c
/* Test 1 (FIX-02B SDP): flash_5v_page_write_execute must emit FLASH_ENABLE_WRITE
 * SDP 3-byte sequence at the start of each page load.
 * RED before fix (no flash_execute_command(FLASH_ENABLE_WRITE) in write path). */
void test_5v_page_write_execute_emits_sdp(void) {
    firestarter_handle_t h = make_write_handle_with_data();
    configure_memory(&h);
    clear_bus_recording(); /* reset after configure_memory's set_address call */
    h.firestarter_operation_main(&h);
    TEST_ASSERT_TRUE_MESSAGE(recording_contains_sdp_signature(),
        "flash_5v_page_write_execute must emit FLASH_ENABLE_WRITE SDP ... at page start");
}
```
Note the `clear_bus_recording()` **after** `configure_memory` — configure writes address 0, so the
capture must be reset before driving the operation. The new suites need the same.

⚠ Anti-pattern in this analog, do NOT copy: `recording_contains_sdp_signature()` (`:199-217`) is a
*sub-sequence scan*, which research §F5 proves cannot distinguish shipped from fixed (identical
length, identical MSB set on DIP32). D-06 requires ordered element-by-element equality.

---

### `firestarter/test/native/avr/_shared/sdp_bus_config.h` (NEW — generated artifact)

**Analog:** `firestarter/test/native/avr/_shared/validation_matrix.h` (28 lines, whole file).

**Emitted-header shape to match exactly** (`:1-16`):
```c
/* DO NOT EDIT -- generated by tools/gen_validation_header.py
 * Re-run after editing tools/validation_matrix_spec.json */

#pragma once

#include <stdint.h>

#define VAL_FAMILY_COUNT 11

typedef struct {
    uint32_t protocol;
    const char* family_id;
    const char* handler_name;
} val_family_entry_t;

static const val_family_entry_t VAL_FAMILIES[] = {
    { 0x07, "eprom", "configure_eprom" },
```
Banner first line, blank line, `#pragma once`, `#include <stdint.h>`, a `*_COUNT` define, a local
struct typedef, then a `static const` table. Note the header defines its **own** row struct — the
SDP header must NOT re-declare `bus_config_t` (that lives in `include/firestarter.h:75-82`); emit
initialiser literals plus a small wrapper row struct carrying the pinout name.

---

### `firestarter_app/tools/gen_sdp_bus_config.py` (NEW — generator, batch transform)

**Analog:** `firestarter_app/tools/gen_validation_header.py` (190 lines, whole file).

**Module docstring + contract** (`:1-23`) — state the target path, the mirrored precedent, and the
exit codes:
```python
"""
Firestarter v1.13 validation matrix codegen.

Reads tools/validation_matrix_spec.json (authored input, D-01) and emits a
deterministic C++ header for the native Unity test suites:

  firestarter/test/native/avr/_shared/validation_matrix.h

Mirrors the established tools/catalog/codegen.py shape:
  - Validate-first: validate_spec() raises ValueError on any schema violation
    BEFORE emission (T-71-INPUT mitigation).
  - Deterministic: sorted family/protocol order, no timestamps, LF endings.
  - Banner: DO NOT EDIT with re-run instructions.
  - Path.write_text(encoding="utf-8", newline="\\n") for byte-identical output.

Exit codes:
  0 — spec valid, header emitted successfully
  1 — spec validation failed (schema error)
  2 — spec file not found
"""
```

**Path-constant + banner block** (`:34-54`) — copy the sibling-repo path derivation verbatim:
```python
_TOOLS_DIR = Path(__file__).parent
_SPEC_DEFAULT = _TOOLS_DIR / "validation_matrix_spec.json"
_TARGET_DEFAULT = (
    _TOOLS_DIR.parent.parent / "firestarter" / "test" / "native" / "avr"
    / "_shared" / "validation_matrix.h"
)

BANNER = (
    "/* DO NOT EDIT -- generated by tools/gen_validation_header.py\n"
    " * Re-run after editing tools/validation_matrix_spec.json */\n"
    "\n"
)
```

**Validate-before-emit + deterministic write** (`:165-186`) — the load-bearing ordering:
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
**`--spec` / `--target` argparse options are mandatory** (`:142-162`) — the drift gate depends on
`--target` pointing at a temp file. Divergence per D-08: this generator's "spec" is not a JSON file
but the live host derivation — import `EpromDatabase` / `convert_to_programmer` from
`firestarter/database.py:535` and `firestarter/data/pinouts.json`; keep `--target` and keep a
validate-before-emit step over the derived rows.

---

### `firestarter_app/tests/test_sdp_bus_config_drift.py` (NEW — drift gate, FW_ABSENT skipif)

**Analog:** `firestarter_app/tests/test_gen_validation_header.py` (194 lines, whole file).

**Cross-repo path constants + `FW_ABSENT` skipif** (`:18-41`) — copy exactly:
```python
_REPO_ROOT = Path(__file__).parent.parent.parent
_APP_DIR = _REPO_ROOT / "firestarter_app"
_GEN_SCRIPT = _APP_DIR / "tools" / "gen_validation_header.py"
_COMMITTED_HEADER = (
    _REPO_ROOT / "firestarter" / "test" / "native" / "avr" / "_shared" / "validation_matrix.h"
)

# The firmware sub-repo may be absent in standalone CI ... Mirrors the
# FW_ABSENT skip pattern in test_revision_constants_parity.py.
_FW_HEADER_ABSENT = not _COMMITTED_HEADER.exists()
_requires_fw_header = pytest.mark.skipif(
    _FW_HEADER_ABSENT,
    reason="firestarter firmware checkout absent (validation_matrix.h)",
)
```
(Original idiom: `tests/test_revision_constants_parity.py:52-58`, `FIRMWARE_HEADER` / `FW_ABSENT`.)

**Banner assertion** (`:53-59`):
```python
@_requires_fw_header
def test_committed_header_has_do_not_edit_banner() -> None:
    content = _COMMITTED_HEADER.read_text(encoding="utf-8")
    assert content.startswith(
        "/* DO NOT EDIT -- generated by tools/gen_validation_header.py"
    ), "Header is missing the DO NOT EDIT banner"
```

**The drift gate itself** (`:89-130`) — regenerate to a temp target, byte-compare, remediation
message in the assert:
```python
@_requires_fw_header
def test_codegen_produces_byte_identical_output() -> None:
    with tempfile.NamedTemporaryFile(suffix=".h", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        result = subprocess.run(
            [sys.executable, str(_GEN_SCRIPT), "--spec", str(_SPEC), "--target", str(tmp_path)],
            capture_output=True, text=True, cwd=str(_APP_DIR),
        )
        assert result.returncode == 0, (
            f"gen_validation_header.py failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert tmp_path.read_bytes() == _COMMITTED_HEADER.read_bytes(), (
            "validation_matrix.h is STALE — re-run to update:\n"
            "  cd firestarter_app && python tools/gen_validation_header.py\n"
        )
    finally:
        tmp_path.unlink(missing_ok=True)
```

**Non-vacuity companion** (`:133-174`) — `test_validate_spec_called_before_emission` proves the
generator refuses bad input and writes nothing. Carry an equivalent.

---

### `firestarter_app/tests/test_sdp_db_invariant.py` (NEW — DB invariant, TRACE-05)

**Analog:** `firestarter_app/tests/test_check_dispatch_invariants.py`.

**Docstring-as-coverage-map convention** (`:1-11`) — enumerate what each test proves, including the
non-vacuity leg:
```python
"""
Tests for check_dispatch.py per-family VPP invariants (Phase 71 HARN-04 / D-09).

Coverage:
  1. Real-DB baseline: subprocess gate exits 0 on the current clean chip_database.json.
  2. Invariant shape: _FAMILY_VPP_INVARIANTS has correct ranges for flash_intel and sram.
  3. Non-vacuous proof: synthetic configure_sram chip with vpp_mv=12000 IS flagged as a
     violation — proves the gate CAN fail (not a vacuous always-pass check).
"""
```

**cwd-independent app-dir constant** (`:24`):
```python
_FA_DIR = Path(__file__).parent.parent
```

**Assertion-with-diagnostic convention** (`:56-68`):
```python
    assert result.returncode == 0, (
        f"check_dispatch.py exited {result.returncode} on clean DB.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
```

Divergence (research §F9): this test reads `chip_database.json` directly — nested access
`c["programming"]["algorithm"] == 13` — and must assert **both** `len(rows) == 84` and per-element
`chip_id_check is False`. It must **NOT** carry the `FW_ABSENT` skipif even if it shares a file
with the drift gate; keep the two concerns in separate functions.

---

### `firestarter_app/tools/check_no_log_in_sdp_window.py` (NEW — source-scan checker)

**Analog:** `firestarter_app/tools/check_devtest_orchestrator.py` (431 lines; read `:1-110`).

**Anti-hollow docstring + exit-code contract** (`:33-44`, `:70-77`):
```python
This is a genuinely-populated AST walk (`ast.parse` + a fresh
`ast.NodeVisitor`), NOT a hollow declared-empty detector -- the exact
tech-debt fate this project incurred with v1.12's GATE-03 (a checker that
could never fail because it asserted nothing concrete). The paired pytest
(`tests/test_check_devtest_orchestrator.py`) proves this checker actually
flips to non-zero on a planted violation, injected via the
`FIRESTARTER_DEVTEST_SRC` / `FIRESTARTER_DEVTEST_HANDLER` env-overrides below
(mirrors `tools/check_dispatch.py`'s `FIRESTARTER_DB_FILE` seam) -- D-03's
anti-hollow contract.

Exit codes:
  0 -- ... (PASS: line printed)
  1 -- at least one deny-list violation was found (FAIL: per-bucket summary
       printed, per-bucket capped at the first 20 entries).
```

**Env-override seam** (`:80-90`) — the exact mechanism D-04 calls for:
```python
_HERE = os.path.dirname(__file__)
_DEFAULT_CHIP_TEST = os.path.join(_HERE, "..", "firestarter", "chip_test.py")

# Env-override seam (mirrors check_dispatch.py's FIRESTARTER_DB_FILE): lets
# the paired pytest point this checker at a deliberately-violating fixture
# file without editing the real, clean chip_test.py source (D-03).
FIRESTARTER_DEVTEST_SRC = os.environ.get("FIRESTARTER_DEVTEST_SRC", _DEFAULT_CHIP_TEST)
```
Divergence: the target here is a **C++** file (`firestarter/src/proms/eeprom_28c.cpp`), so `ast`
does not apply. Use a structural scan (brace-matched function-body extraction) rather than a bare
substring grep — the analog's docstring records why greps false-positive on this project's prose
comments. Fail closed if the path is missing (the analog tolerates a missing path only for the
test-fixture leg; note that carve-out and do not generalise it).

**Paired anti-hollow pytest:** `firestarter_app/tests/test_check_devtest_orchestrator.py` — the
`_run_checker({"FIRESTARTER_DEVTEST_SRC": str(bad)})` helper (used at `:101`, `:121`, `:141`,
`:159`) plus the clean-source control at `:186`. Copy the helper + one-violation-per-test layout.

Research §F6 recommends an additional cheap gate in this same shape: assert the test-local
`byte_flip_t` copy matches the six literal `{address, byte}` pairs at `eeprom_28c.cpp:26-33`.
Same checker, second deny/parity bucket.

---

### `firestarter/platformio.ini` (MODIFIED — config)

**Analog:** itself, `[env:native]`. Two parallel allowlists must be edited **together** for the
always-green suite, and **neither** for the parked RED suite (D-01):
```ini
test_filter =
	native/avr/test_dispatch
	...
	native/avr/test_val_sram

build_flags =
	${env.build_flags}
	-std=gnu++17
	-I include
	-I test/native/avr/test_dispatch
	...
	-I test/native/avr/test_val_sram
```
The existing KNOWN-FLAKY comment block above `test_filter` is the precedent for D-01's
`TODO(v1.22 Phase 117)` parking note — write the new note in that same style, directly above the
`test_filter` list, naming the parked directory:
```ini
; KNOWN-FLAKY: test_flash_intel_vpp + test_eeprom28c_chip_id suites ...
; TODO(v1.5): root-cause the SIGABRT in Unity teardown and re-enable.
; Using positive test_filter allowlist (test_ignore was being honored
; inconsistently — likely PIO version quirk).
```
Also: `test_eeprom28c_chip_id` is named in that comment; retiring the directory (D-12) means the
comment must be updated in the same commit or it references a nonexistent suite.

---

### `.planning/.../116-PREMISE.md` and `.planning/PROJECT.md` (docs)

**Analog for `116-PREMISE.md`:** `.planning/notes/dev-test-unknown-chip-fail-fast.md` — named by
CONTEXT §specifics as the target shape: state the finding, the evidence, and *why the distinction
is load-bearing*, so a later editor does not undo it. Use the verbatim permitted wording from
RESEARCH §F1 and carry CORRECTION 4 (66 of 84, per-pinout).

**Analog for the PROJECT.md edit:** the two existing ⚠ correction blocks under
`## Current Milestone: v1.22`. Match their heading level, ⚠ prefix, and dated-attribution form.

---

## Shared Patterns

### Anti-hollow: every gate ships a planted-violation proof
**Sources:** `firestarter_app/tools/check_devtest_orchestrator.py:33-44` (contract prose) +
`tests/test_check_devtest_orchestrator.py` (`_run_checker` env-override harness) +
`tests/test_gen_validation_header.py:133-174` (bad-spec → exit 1, no output written) +
`tests/test_check_dispatch_invariants.py:1-11` ("Non-vacuous proof" coverage line).
**Apply to:** `check_no_log_in_sdp_window.py`, `gen_sdp_bus_config.py`, `test_sdp_db_invariant.py`,
and the two in-suite `byte_flip_t` negatives.

### Generated artifact = DO NOT EDIT banner + regenerate-and-diff pytest
**Sources:** `gen_validation_header.py:50-54` (banner constant) + `:184`
(`write_text(encoding="utf-8", newline="\n")`) + `test_gen_validation_header.py:89-130` (gate).
**Apply to:** `_shared/sdp_bus_config.h`, `tools/gen_sdp_bus_config.py`,
`tests/test_sdp_bus_config_drift.py`.

### Cross-repo test skipping
**Source:** `firestarter_app/tests/test_revision_constants_parity.py:52-58`; second instance
`test_gen_validation_header.py:32-41`.
```python
FIRMWARE_HEADER = (
    Path(__file__).parent.parent.parent / "firestarter" / "include" / "firestarter.h"
)
FW_ABSENT = not FIRMWARE_HEADER.exists()
```
**Apply to:** `test_sdp_bus_config_drift.py` only. **Never** to `test_sdp_db_invariant.py`.

### Native suite composition (three files per suite dir)
**Source:** `test_val_eeprom28c/` — `host_stubs.cpp` (flag + `.inc` include),
`test_val_eeprom28c.cpp` (`setUp`/`tearDown`/`make_handle`/cases/`main`), and two
`platformio.ini` lines. Directory name **must** start with `test` (research: silently uncollected
otherwise).
**Apply to:** both new firmware suites.

### Unity assertion style
**Source:** `test_val_eeprom28c.cpp:76-81`, `:90-91`; `test_val_5v_page.cpp:229-232`.
Always the `_MESSAGE` variant, message written as an imperative contract sentence naming the
function under test. **Apply to:** every new firmware assertion; D-06 additionally requires the
diverging index in the message.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `test_sdp_harness/sdp_expected.h`, `test_eeprom28c_sdp/sdp_expected_fixed.h` | test data | transform | No hand-authored ordered-stream golden exists in the tree. `validation_matrix.h` supplies the static-table *shape* only; the closest behavioural precedent, `recording_contains_sdp_signature()` (`test_val_5v_page.cpp:199-217`), is a sub-sequence scan D-06 explicitly rejects. Build from RESEARCH §F4/§F5's literal 54-entry streams. |
| `test_eeprom28c_sdp/RED-BASELINE.md` | evidence fixture | — | No committed expected-vs-actual divergence fixture exists inside either sub-repo (all prior RED evidence lived in `.planning/`). Prose shape from `.planning/notes/dev-test-unknown-chip-fail-fast.md`; content from RESEARCH §F4/§F5 + CORRECTION 2/3. |

---

## Metadata

**Analog search scope:** `firestarter/test/native/avr/**`, `firestarter/platformio.ini`,
`firestarter_app/tools/**`, `firestarter_app/tests/**`, `firestarter_app/firestarter/database.py`,
`.planning/notes/`.
**Files read for extraction:** 12 (`host_stubs_common.inc`, `test_val_eeprom28c.cpp`,
`test_val_eeprom28c/host_stubs.cpp`, `test_val_5v_page.cpp`, `test_eeprom28c_chip_id.cpp`,
`test_not_implemented.cpp`, `validation_matrix.h`, `platformio.ini`, `gen_validation_header.py`,
`test_gen_validation_header.py`, `test_check_dispatch_invariants.py`,
`check_devtest_orchestrator.py`; plus `test_revision_constants_parity.py` and `database.py`
excerpts).
**Pattern extraction date:** 2026-07-27
