# Phase 88: Golden Traces + Dispatch-Mirror Guard - Pattern Map

**Mapped:** 2026-06-26
**Files analyzed:** 16 (9 `.inc` fixtures + 1 shared helper header + 5 `test_val_*` suite extensions + 1 host pytest)
**Analogs found:** 16 / 16 (every new file has a concrete in-repo analog; no green-field)

> Two-repo system. All firmware-side work lands in `firestarter/` (`[env:native]` Unity tests + committed fixtures — production firmware is NOT modified, D-08). The dispatch-mirror lands host-side in `firestarter_app/` (pytest). NO dual-repo lockstep (no wire/constant change).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `test/native/avr/_shared/golden_trace.h` (NEW) | test-utility (shared C header) | transform (capture→assert / capture→print) | `test_val_flash4.cpp:79-90` `assert_no_vpp_in_recording` + `host_stubs_common.inc:64-67` recording API | role-match (generalizes an existing recording-scan helper) |
| `test_val_eprom/golden_eprom_0x07_write.inc` (NEW) | test-fixture (committed expected array) | batch (static `{reg,data}` rows) | INV-04 count idiom `test_val_flash4.cpp:330-341`; recorded via bless mode | role-match (new artifact form; data shape exists) |
| `test_val_eprom/golden_eprom_0x08_write.inc` (NEW) | test-fixture | batch | same as 0x07 | role-match |
| `test_val_eprom/golden_eprom_0x0B_write.inc` (NEW) | test-fixture | batch | same as 0x07 | role-match |
| `test_val_eprom/golden_eprom_chip_id.inc` (NEW) | test-fixture | batch | chip-id path `test_eeprom28c_chip_id.cpp:101-110` | role-match |
| `test_val_eeprom28c/golden_eeprom28c_write.inc` (NEW) | test-fixture | batch | INV-04 idiom | role-match |
| `test_val_eeprom28c/golden_eeprom28c_chip_id.inc` (NEW) | test-fixture | batch | `test_eeprom28c_chip_id.cpp:101-110` | exact (same family chip-id) |
| `test_val_flash_intel/golden_flash_intel_write.inc` (NEW) | test-fixture | batch | INV-04 idiom | role-match |
| `test_val_flash_intel/golden_flash_intel_chip_id.inc` (NEW) | test-fixture | batch | `test_configure_memory.cpp:170-195` + scripted-byte idiom | role-match |
| `test_val_flash4/golden_flash4_write.inc` (NEW) | test-fixture | batch | INV-04 `test_val_flash4.cpp:310-342` (65-byte probe) | exact (same suite, sizing precedent) |
| `test_val_flash4/golden_flash4_chip_id.inc` (NEW) | test-fixture | batch | `test_configure_memory.cpp:170-195` (flash4 P4 via flash_utils) | role-match |
| `test_val_flash3/golden_flash3_write.inc` (NEW) | test-fixture | batch | INV-04 idiom | role-match |
| `test_val_eprom/test_val_eprom.cpp` golden test fns (MODIFY) | test | request-response (configure→init→main) | own write+init idiom `test_val_eprom.cpp:121-160` | exact (extends itself) |
| `test_val_eeprom28c/test_val_eeprom28c.cpp` golden test fns (MODIFY) | test | request-response | `test_eeprom28c_chip_id.cpp:101-110` | role-match |
| `test_val_flash_intel/`, `test_val_flash3/`, `test_val_flash4/` `*.cpp` golden test fns (MODIFY) | test | request-response | `test_val_flash4.cpp:310-342` | exact (extends itself) |
| `firestarter_app/tests/test_dispatch_mirror.py` (NEW) | test (host pytest) | transform (parse + cross-check) | `tests/test_check_dispatch_invariants.py:1-43` (imports `tools.check_dispatch`) | role-match (same import seam + style) |

---

## Pattern Assignments

### `test/native/avr/_shared/golden_trace.h` — shared assert/bless helper (test-utility, transform)

**Analogs:**
- `firestarter/test/native/avr/_shared/host_stubs_common.inc:64-67` (recording API the helper reads)
- `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp:79-90` (existing scan-helper shape to generalize)

**Recording API to consume** (`host_stubs_common.inc:64-75` — already present, opt-in via `HOST_STUBS_RECORD_BUS`; cap is 256, low-byte only):
```cpp
extern "C" void clear_bus_recording();
extern "C" int  bus_recording_count();
extern "C" uint8_t recorded_reg(int i);
extern "C" uint8_t recorded_data(int i);
// rurp_write_to_register stores (uint8_t)data — 0x100 CTRL_VPP_VPE_DROP_ENABLE is INVISIBLE (Pitfall 1)
```

**Existing scan-helper to generalize** (`test_val_flash4.cpp:79-90` iterates the recording — the new helper iterates+equality-compares instead):
```cpp
static void assert_no_vpp_in_recording(const char* ctx) {
    for (int i = 0; i < bus_recording_count(); i++) {
        if (recorded_reg(i) == CONTROL_REGISTER) {
            TEST_ASSERT_BITS_LOW_MESSAGE((uint8_t)CTRL_VPP_REGULATOR_ENABLE, recorded_data(i), ctx);
        }
    }
}
```

**Pattern to author** (the `bus_record_entry_t` type already exists in `host_stubs_common.inc:57-60`; declare a matching plain struct or reuse via `extern "C"` accessors — accessors are the cleaner seam since the struct is `static` in the `.inc`). Equality-compare count first (D-01), then every element via `TEST_ASSERT_EQUAL_HEX8_MESSAGE`; `#ifdef GOLDEN_BLESS` prints `.inc`-ready rows instead of asserting:
```cpp
// _shared/golden_trace.h — included AFTER the extern "C" recording decls
struct golden_entry_t { uint8_t reg; uint8_t data; };

static inline void assert_trace_eq(const golden_entry_t* exp, int n, const char* ctx) {
    TEST_ASSERT_TRUE_MESSAGE(bus_recording_count() < 256, "golden trace truncated at cap (Pitfall 2)");
    TEST_ASSERT_EQUAL_INT_MESSAGE(n, bus_recording_count(), ctx);   // count first (D-01)
    for (int i = 0; i < n; i++) {
        TEST_ASSERT_EQUAL_HEX8_MESSAGE(exp[i].reg,  recorded_reg(i),  ctx);
        TEST_ASSERT_EQUAL_HEX8_MESSAGE(exp[i].data, recorded_data(i), ctx);
    }
}
#ifdef GOLDEN_BLESS
static inline void print_trace_inc(void) {
    for (int i = 0; i < bus_recording_count(); i++)
        printf("    { 0x%02X, 0x%02X },\n", recorded_reg(i), recorded_data(i));
}
#endif
```

---

### `golden_<family>_*.inc` × 9 — committed expected-array fixtures (test-fixture, batch)

**Analog (representation + sizing):** `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp:310-342` — the INV-04 65-byte minimal probe. D-04 sizing discipline: pick the smallest input that still fires every algorithm branch (one SDP unlock, one program pulse, one poll/verify), and stay under the 256-entry cap.

**Form:** each `.inc` is a bare comma-list of `{ reg, data }` rows `#include`d into a `static const golden_entry_t golden_xxx[] = { #include "golden_xxx.inc" };` literal (Pattern 2 / research §"Code Examples"). Generated by running the suite with `-D GOLDEN_BLESS` and redirecting `print_trace_inc()` output. Header comment in each fixture MUST note: low-byte-only semantics (0x100 bit out of scope, Pitfall 1) and the input that produced it (re-bless reproducibility, D-02).

```c
// golden_eprom_0x07_write.inc — pinned (reg,data) for eprom 0x07 write, 1-byte input.
// Low-byte semantics only: CTRL_VPP_VPE_DROP_ENABLE (0x100) not captured (see test_val_eprom.cpp:108-112).
    { 0x00, 0x00 },
    { 0x01, 0x00 },
    // ...
```

**Coverage map (D-03 — write path + chip-id where the family has one; 4 chip-id sites = eprom, eeprom28c, flash_intel, flash4):**
- `eprom`: `golden_eprom_0x07_write.inc`, `_0x08_write.inc`, `_0x0B_write.inc`, `_chip_id.inc`
- `eeprom28c`: `golden_eeprom28c_write.inc`, `_chip_id.inc`
- `flash_intel`: `golden_flash_intel_write.inc`, `_chip_id.inc`
- `flash4`: `golden_flash4_write.inc`, `_chip_id.inc`
- `flash3`: `golden_flash3_write.inc` (NO chip-id — not one of the four P4 sites)

---

### Golden write-test functions in `test_val_*` suites (test, request-response)

**Analog (write+init drive idiom):** `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:121-160`. Each suite already activates the recording bus via its own `host_stubs.cpp` (`#define HOST_STUBS_RECORD_BUS` before include — confirmed `test_val_flash4/host_stubs.cpp:28`), declares the `extern "C"` recording API (`test_val_eprom.cpp:61-65`), and stubs `delay`/`delayMicroseconds` in `setUp()` (`test_val_eprom.cpp:67-78` — Pitfall 4). REUSE that setUp.

**Make-handle + clear-then-drive pattern** (compose `make_handle` `test_val_eprom.cpp:85-95` + INV-04 main-drive `test_val_flash4.cpp:316-331`):
```cpp
void test_golden_eprom_0x07_write(void) {
    firestarter_handle_t h = make_handle(0x07, CMD_WRITE);  // FLAG_SKIP_BLANK_CHECK|FLAG_SKIP_ERASE
    h.data_size = 1;                       // minimal representative input (D-04)
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    clear_bus_recording();                 // isolate init+execute from configure-phase address writes
    if (h.firestarter_operation_init) h.firestarter_operation_init(&h);
    if (h.firestarter_operation_main) h.firestarter_operation_main(&h);
#ifdef GOLDEN_BLESS
    print_trace_inc();
#else
    assert_trace_eq(golden_eprom_0x07_write, golden_eprom_0x07_write_n, "golden drift: eprom 0x07 write");
#endif
}
```

**Wire into `main()` RUN_TEST list** (existing list shape `test_val_flash4.cpp:344-359`):
```cpp
RUN_TEST(test_golden_eprom_0x07_write);   // add alongside existing INV/VPP tests — do NOT replace them (SAFE-02)
```

---

### Golden chip-id (P4) test functions in eprom / eeprom28c / flash_intel / flash4 suites (test, request-response)

**Analog (scripted-byte injection + the function-pointer reassign-after-configure idiom — Pitfall 3):** `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp:32-45, 101-110`.

**Scripted-byte mock + reassign-after-`configure_memory`** (`test_eeprom28c_chip_id.cpp:42-45, 106-109`):
```cpp
static uint8_t s_mock_bytes[16]; static int s_mock_byte_idx;
static uint8_t mock_get_data_scripted(struct firestarter_handle*, uint32_t) {
    if (s_mock_byte_idx < (int)sizeof(s_mock_bytes)) return s_mock_bytes[s_mock_byte_idx++];
    return 0xFF;
}
// ... in the test:
configure_memory(&h);
h.firestarter_get_data = mock_get_data_scripted;  // RE-ASSIGN: configure_memory overwrote it (Pitfall 3)
clear_bus_recording();
if (h.firestarter_operation_main) h.firestarter_operation_main(&h);
// then: assert_trace_eq(golden_<family>_chip_id, ..., "golden drift: <family> chip-id");
```

**flash4 chip-id specifics** (`test_configure_memory.cpp:170-177` confirms `configure_flash4` + `CMD_CHECK_CHIP_ID` sets a non-NULL `operation_main`): build the handle with `CMD_CHECK_CHIP_ID` and a non-zero `h.chip_id` to enable the compare branch.

---

### `firestarter_app/tests/test_dispatch_mirror.py` — host dispatch-mirror (test, transform)

**Analogs:**
- `firestarter_app/tests/test_check_dispatch_invariants.py:1-43` — import seam (`from tools.check_dispatch import ...`), `_FA_DIR = Path(__file__).parent.parent` path discipline, docstring style.
- `firestarter_app/tools/check_dispatch.py:38-50, 117-130, 133-157` — the tool leg: `_ALGO_MEM_TYPE`, `KNOWN_PROTOCOLS`, and `dispatch(protocol, mem_type)` (mirrors firmware order line-for-line — DO NOT re-implement; import it).
- `firestarter/doc/PROTOCOLS.md:22-35` — the §0 pipe table (doc leg): `| hex | DB chip count | handler | datasheets folder | algorithm-axis name |`, handler in backticks col 3 (e.g. `` `flash_type_4.cpp` ``, `` `eprom.cpp` ``, `` `not_implemented.cpp` ``).
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — the firmware leg, already anchored (no firmware change). Optionally grep it for `test_protocol_0x*` / `test_flash4_check_chip_id_*` to make the firmware-leg binding explicit.

**Three-way bind (D-05/D-06)** — parse §0 table, derive the same map from the tool sim, assert agreement across the FULL table (incl. SRAM 0x0E/0x27/0x28/0x29 and 0x34→`not_implemented`). 0x35/0x39 are NOT in §0 (phantom, §2 lines 327-328) → route to `not_implemented`:
```python
import re, pathlib
from tools import check_dispatch   # tool leg — import, never re-implement dispatch()

_FA_DIR = pathlib.Path(__file__).parent.parent
PROTOCOLS_MD = _FA_DIR.parent / "firestarter" / "doc" / "PROTOCOLS.md"  # sub-repo doc leg
ROW = re.compile(r"^\|\s*0x([0-9A-Fa-f]+)\s*\|[^|]*\|\s*`([a-z0-9_]+\.cpp)`\s*\|")
DOC_FILE_TO_FUNC = {
    "flash_type_4.cpp": "configure_flash4", "flash_type_3.cpp": "configure_flash3",
    "eprom.cpp": "configure_eprom", "eeprom_28c.cpp": "configure_eeprom28c",
    "flash_intel.cpp": "configure_flash_intel", "sram.cpp": "configure_sram",
    "not_implemented.cpp": "not_implemented",
}

def parse_protocols_md():
    return {int(m.group(1), 16): m.group(2)
            for line in PROTOCOLS_MD.read_text(encoding="utf-8").splitlines()
            if (m := ROW.match(line))}

def test_dispatch_mirror_doc_matches_tool():
    for hex_id, handler_file in parse_protocols_md().items():
        mt = check_dispatch._ALGO_MEM_TYPE.get(hex_id, 0)
        got = check_dispatch.dispatch(hex_id, mt)
        assert got == DOC_FILE_TO_FUNC[handler_file], f"0x{hex_id:02X}: doc={DOC_FILE_TO_FUNC[handler_file]} tool={got}"
```

**CI discipline (Pitfall 5):** validate under py3.11 target — run `ruff check` + `ruff format --check`; pure stdlib `re`/`pathlib`, no markdown lib (Don't-Hand-Roll). Avoid f-string-backslash constructs.

---

## Shared Patterns

### Recording bus (opt-in, do NOT modify behavior)
**Source:** `firestarter/test/native/avr/_shared/host_stubs_common.inc:54-80`
**Apply to:** all 5 `test_val_*` suites (each already opts in via its `host_stubs.cpp:28` `#define HOST_STUBS_RECORD_BUS`).
The 256 cap and `(uint8_t)data` low-byte store are load-bearing — widening the struct would break the byte-exact behavior other suites depend on (`host_stubs_common.inc:50-53`). Add `assert_trace_eq`'s `bus_recording_count() < 256` guard so an oversized capture fails loudly (Pitfall 2).

### setUp() delay/Serial stubs (ArduinoFake)
**Source:** `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:67-78`
**Apply to:** every new write/chip-id test — reuse the suite's existing `setUp()`. Unmocked `delay`/`delayMicroseconds` aborts the suite (Pitfall 4). Confirm each new path's specific delays are covered.

### 0x100 control-bit caveat
**Source:** `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:108-116`
**Apply to:** every `.inc` fixture (document it) — the existing INV-01/INV-03 bit-level assertions stay as the complementary guard for the 0x100 bit (Pitfall 1).

### Re-bless workflow (D-02)
**Source:** Pattern proposed in `88-RESEARCH.md` §Pattern 2, built on the recording API.
**Apply to:** all golden suites — `-D GOLDEN_BLESS` prints `.inc` rows; redirect into the fixture; the re-bless commit is the audit checkpoint.

### Frozen-world gates (rerun, expect unchanged — D-07/D-08/D-09)
**Sources:** `firestarter_app/tools/check_dispatch.py` (0 violations), `firestarter_app/tools/diff_db.py` (empty), `pio run -e leonardo` (Flash ≈25654 B). Safety-posture greps confirmed present this session: over-voltage at `firestarter/src/proms/eprom.cpp:282` (`vpp_mv > (uint32_t)handle->vpp_mv + 500`) and `flash_intel.cpp:65`; host guard at `firestarter_app/firestarter/chip_resolver.py:55` (`support_status != "supported"`). These are verify-present-and-unmodified — no edits.

## No Analog Found

None. Every new file maps to an existing in-repo analog (recording API, INV/scan helpers, scripted-byte chip-id idiom, dispatch sim import seam, §0 doc table). The only genuinely new artifact *forms* are the committed `.inc` fixtures and the `golden_trace.h` helper, both of which generalize existing recording-scan code rather than introducing a new mechanism.

## Metadata

**Analog search scope:** `firestarter/test/native/avr/{_shared,test_val_*,test_eeprom28c_chip_id,test_dispatch}`, `firestarter/doc/PROTOCOLS.md`, `firestarter/src/proms/{eprom,flash_intel}.cpp`, `firestarter_app/tools/{check_dispatch,diff_db}.py`, `firestarter_app/firestarter/chip_resolver.py`, `firestarter_app/tests/{conftest,test_check_dispatch_invariants}.py`
**Files scanned:** ~12 (all read this session; no re-reads)
**Pattern extraction date:** 2026-06-26
