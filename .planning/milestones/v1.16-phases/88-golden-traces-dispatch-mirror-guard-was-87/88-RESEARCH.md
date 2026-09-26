# Phase 88: Golden Traces + Dispatch-Mirror Guard - Research

**Researched:** 2026-06-26
**Domain:** Firmware native-test authoring (PlatformIO Unity `[env:native]`) + cross-repo dispatch-mirror guard (C++ ↔ markdown ↔ Python) + frozen-world regression gates
**Confidence:** HIGH (all claims grounded in read source + executed gates; no external packages)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Golden traces are **byte-exact full ordered `(reg, data)` sequences** — equality-compared against a pinned expected array, asserting both count and every element. Maximum-strength oracle. (Rejected: key-register-subset, behavioral-only.)
- **D-02:** **Re-bless is allowed in Phase 89.** The golden trace is NOT frozen byte-identical forever; when Phase 89 confirms a trace diff is benign, it may regenerate the expected array. **The re-bless commit is the audit checkpoint.** A Phase-89 failure means "inspect this diff," not automatically "regression." (Rejected: frozen-byte-identical; frozen-with-escape-hatch.)
- **D-03:** Each family gets a byte-exact golden trace for the **write/program path (end-to-end)** AND the **chip-id path** where the family has one.
  - Write path inherently exercises **P3** (VPP gate), **P5** (poll + verify-readback), **P7** (SDP unlock) for families that use them.
  - Chip-id path covers **P4** (`CMD_CHECK_CHIP_ID` compare/report) — a separate command path. The four chip-id call sites are **eprom, flash_intel, eeprom28c, and flash4 (`flash_utils`)**.
  - Read / blank-check paths stay covered by existing Phase-87 INV tests — not re-traced.
- **D-04:** **Fixture-sizing under the 256-entry recording cap** (`HOST_STUBS_MAX_RECORDING = 256`). Write traces (especially flash4's page write) MUST use a **minimal representative input** sized under the cap while exercising the full algorithm shape. INV-04's 257→65-byte probe is the precedent.
- **D-05:** **Bind all three.** Dispatch-mirror test proves protocol→handler order agrees across (1) `firestarter/doc/PROTOCOLS.md` §0 table, (2) `firestarter_app/tools/check_dispatch.py` `_ALGO_MEM_TYPE`/dispatch-sim, (3) firmware `configure_memory()` dispatch. Drift in ANY trips the test. (Rejected: native-vs-doc only; host-vs-doc only.)
- **D-06:** The dispatch-mirror guards the **full dispatch table** (all protocols incl. SRAM 0x0E/0x27/0x28/0x29 and 0x34→`not_implemented`), not just the five recompose families. **Reuse the existing PROTOCOLS.md §0 table** — do not author a new canonical table.
- **D-07:** `check_dispatch.py` exits **0 violations** and `diff_db.py` is **empty** against the Phase-86-repinned baseline — **no DB record changes this phase** (SAFE-04, ROADMAP SC#3).
- **D-08:** `pio run -e leonardo` shows **near-zero flash delta** — test + doc-parse work, no PROGMEM strings added to firmware. (Tests compile only into `[env:native]`.)
- **D-09:** Firmware over-voltage VPP check and host `chip_resolver.resolve_chip` guard are **verified present and unmodified** (SAFE-04, SC#4); the 2516 stays `UNVERIFIED` — not spent.

### Claude's Discretion

- **Golden-reference representation (Area 2):** form delegated to planner — inline expected-array literal in the `test_val_*.cpp`, a generated `.inc` fixture header, or another committed representation. **Constraint:** (a) committed, (b) equality-compared (count + every element), (c) **cheaply regenerable** so the D-02 re-bless is a one-step rerun producing a clean reviewable git diff. A small recorder/print mode is the implied mechanism.
- Which existing `test_val_*` suite hosts each golden trace + precise assertion-helper mechanics (e.g. a shared `assert_trace_eq(expected, n)`) — planner/executor's call, consistent with the existing recording-bus API.
- Whether the dispatch-mirror test lives native-side, host-side (pytest), or as a small cross-repo parse harness — as long as all three representations (D-05) are bound. Natural split: host-side parser binds PROTOCOLS.md ↔ check_dispatch.py, native `test_dispatch` anchors the firmware leg.

### Deferred Ideas (OUT OF SCOPE)

- **The primitive recompose itself** (P7 SDP-table dedup → P4 chip-id → P3 VPP gate → P5 poll) — Phase 89.
- **Per-protocol bench validation + PROTOCOL-LEDGER** — Phase 90.
- **0x34 X88C64 programming handler** — PCB-blocked (FUT-01); not in v1.16 scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRIM-01 | Golden traces + dispatch-order test exist before any extraction (the recompose oracle) | §"Golden Traces" — recording-bus idiom (`host_stubs_common.inc:54-80`) + per-family `test_val_*` extension points; §"Dispatch-Mirror" — three-way bind shape |
| SAFE-01 | Key on `handle->protocol` never `electrical.type`; WARNING-5 structural guards preserved (recurs in 89) | Dispatch order in `memory.cpp::configure_memory` keys on `handle->protocol` first (firmware CLAUDE.md §Protocol Dispatch); WARNING-5 guard is host-side in `check_dispatch.py` (the `eeprom28c_in_eprom` + `novpp_in_eprom` buckets) — verified present + green |
| SAFE-02 | INV invariants survive each recompose step, asserted under native register tests | Golden traces are a strictly-stronger superset of the INV assertions in `test_val_*`; the existing INV tests stay green (not replaced). §"INV traceability" |
| SAFE-04 | Over-voltage stays blocked; `resolve_chip` host guard never bypassed; 2516 stays UNVERIFIED | §"SC#4 Safety-Posture Verification" — `eprom_check_vpp`/`flash_intel_check_vpp` over-voltage block (`eprom.cpp:282`, `flash_intel.cpp:65`) + `chip_resolver.resolve_chip` (`chip_resolver.py:55-57`) grep-able structural assertions; diff_db empty keeps 2516 unmoved |
</phase_requirements>

## Summary

Phase 88 is a "freeze-the-world-then-prove-nothing-moved" pass identical in posture to Phase 87. It adds **no firmware behavior**, changes **no DB record**, and must show **near-zero Leonardo flash delta** (current baseline `Flash: 25654 bytes, 89.5%`, captured this session). Everything new compiles only into `[env:native]` (verified `build_src_filter = +<proms/> ...` in `platformio.ini:129`, plus `test_build_src = yes`), so production builds never see it.

The work has three buildable deliverables and two verification gates. (1) **Per-family byte-exact golden register traces** extend the five existing `test_val_*` Unity suites using the already-present recording bus (`host_stubs_common.inc:54-80`): capture the full ordered `(reg, data)` array via `bus_recording_count()`/`recorded_reg(i)`/`recorded_data(i)` and equality-compare it against a pinned expected array (count + every element, D-01). (2) **A dispatch-mirror invariant test** binds the protocol→handler order across the PROTOCOLS.md §0 table (lines 22-35), `check_dispatch.py`'s `dispatch()` sim + `_ALGO_MEM_TYPE`, and the firmware `configure_memory()` arms anchored by `test_dispatch/test_configure_memory.cpp`. (3) **Re-bless plumbing** — a one-step regenerate mode so a Phase-89 benign reorder produces a clean reviewable diff. The gates: `check_dispatch.py` (PASS, 0 violations — verified this session) and `diff_db.py` (empty — verified this session, "0 changed chips"), plus the over-voltage / host-guard safety-posture confirmation.

**Primary recommendation:** Author the golden traces as **committed `.inc` fixture headers** (one per traced path, e.g. `golden_eprom_0x07_write.inc`) generated by a compile-time `GOLDEN_BLESS` print mode added to the `test_val_*` suites, and assert via a small shared `assert_trace_eq()` helper. Implement the dispatch-mirror as a **host-side pytest** (`tests/test_dispatch_mirror.py` in `firestarter_app`) that parses the PROTOCOLS.md §0 markdown table and binds it to `check_dispatch.py`'s `dispatch()` sim, while the **existing native `test_dispatch` suite anchors the firmware leg** (no firmware change needed — the firmware leg is pinned by the per-protocol routing tests already present). This split keeps the parse-heavy work in Python (the natural language for markdown parsing) and the firmware-structure anchor in C++ where it already lives.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Golden register traces (P3/P5/P7 write paths + P4 chip-id) | Firmware native test (`[env:native]` Unity) | — | Traces capture `rurp_write_to_register` side effects of the handlers — only observable inside the cross-compiled firmware TUs |
| Recording / re-bless plumbing | Firmware native test harness | — | Recording bus is a host-stub (`host_stubs_common.inc`); bless-mode print is a test-side compile flag |
| Dispatch-mirror: doc ↔ tool bind | Host (Python / pytest) | — | Markdown parsing + the dispatch sim already live in Python (`check_dispatch.py`); pytest is the existing host test framework |
| Dispatch-mirror: firmware leg anchor | Firmware native test (`test_dispatch`) | — | The firmware `configure_memory()` arms are already pinned by `test_configure_memory.cpp` per-protocol tests |
| Frozen-world DB/dispatch gates | Host (Python tools) | CI | `check_dispatch.py` / `diff_db.py` are host tools run in `firestarter_app` CI (py3.11) |
| Flash-delta gate | Firmware build (`[env:leonardo]`) | — | Production size is a firmware-build property |
| SC#4 safety-posture: over-voltage check | Firmware source (grep-able structural assert) | Firmware native test | The check lives in `eprom.cpp`/`flash_intel.cpp`; "present + unmodified" is a source/structural assertion |
| SC#4 safety-posture: resolve_chip guard | Host source (`chip_resolver.py`) | Host pytest | The host guard is the authoritative refusal layer for non-supported chips |

## Standard Stack

This phase uses **no external packages**. It extends in-repo test infrastructure only.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PlatformIO Core | 6.1.19 (verified `pio --version`) | Build + run `[env:native]` Unity suites and `[env:leonardo]` firmware | Already the firmware build system; native env exists |
| Unity (via PlatformIO `test_framework=unity`) | bundled by PIO | C test assertions (`TEST_ASSERT_EQUAL_*`, `TEST_ASSERT_EQUAL_HEX8_MESSAGE`) | Every existing `test_val_*` / `test_dispatch` suite uses it |
| ArduinoFake (`fakeit`) | bundled (`framework-arduino-avr @ 5.3.0`) | Mock `delay`/`delayMicroseconds`/`Serial` so handler paths run on host | Used in all five `test_val_*` setUps |
| pytest | per `firestarter_app` `[test]` extra | Host-side dispatch-mirror test | Existing host test framework; CI runs `pytest --cov-fail-under=70` |
| Python stdlib `json` / `re` | 3.11 (CI) | Parse `chip_database.json`, `check_dispatch.py` constants, PROTOCOLS.md table | No new deps; `check_dispatch.py`/`diff_db.py` already use stdlib only |

### Supporting
| Asset | Purpose | When to Use |
|-------|---------|-------------|
| `host_stubs_common.inc` recording bus (`HOST_STUBS_RECORD_BUS`) | Capture ordered `(reg,data)` writes | Every golden-trace suite (opt-in `#define` before include) |
| `check_dispatch.py` `dispatch()` + `_ALGO_MEM_TYPE` | Python dispatch sim — the tool leg of the mirror | Dispatch-mirror test imports/parses it |
| `test_dispatch/test_configure_memory.cpp` | Firmware per-protocol routing anchor | Stays as-is; the firmware leg of the mirror |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `.inc` fixture header (recommended) | Inline expected-array literal in `.cpp` | Inline is simplest but mixes ~hundreds of `(reg,data)` rows into test logic, and a re-bless diff churns the whole `.cpp` instead of a dedicated fixture file. `.inc` keeps the re-bless diff isolated and reviewable (D-02). |
| `.inc` fixture header | External committed `.txt`/`.json` loaded at runtime | `[env:native]` has no clean file-read seam (it's a statically-linked host binary with no fixture path convention); a compiled-in `.inc` needs no I/O and links deterministically. |
| Host-side pytest mirror (recommended) | Native-side C++ mirror parsing PROTOCOLS.md | C++ markdown parsing is painful and would need a host-stub TU to read the doc file; the doc + tool both live in Python's reach already. |

**Installation:** none — `pip install -e '.[test]'` (already documented) for the host side; `pio` is on PATH.

**Version verification:** Not applicable — no packages installed. PlatformIO Core 6.1.19 and ArduinoFake/Unity bundles confirmed via `pio --version` and existing green suites this session.

## Package Legitimacy Audit

> Not applicable — Phase 88 installs **no external packages**. It extends in-repo test code and reruns existing in-repo Python tools. No npm/PyPI/crates dependency is added.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
                       ┌─────────────────────── DELIVERABLE 1: GOLDEN TRACES ───────────────────────┐
                       │                                                                            │
 firestarter_handle_t  │   configure_memory(&h)        h.firestarter_operation_init(&h)             │
 (protocol, cmd,  ─────┼─▶  (dispatch → handler) ──┬──▶ (write path: P3 VPP gate / P5 poll /        │
  mem_size, data) │    │                           │    P7 SDP unlock)                              │
                  │    │                           └──▶ (chip-id path P4: CMD_CHECK_CHIP_ID) ──┐     │
                  │    │                                                                       │     │
                  │    │   every rurp_write_to_register(reg,data)                              │     │
                  │    │            │                                                          ▼     │
                  │    │            ▼                                          h.firestarter_operation_main(&h)
                  │    │   s_bus_recording[] (cap 256)  ◀── HOST_STUBS_RECORD_BUS               │    │
                  │    │            │                                                           │    │
                  │    │   bus_recording_count()/recorded_reg(i)/recorded_data(i)              │    │
                  │    │            │                                                           │    │
                  │    │            ▼                                                           │    │
                  │    │   assert_trace_eq(golden_xxx, n)  ══ equality (count + every elem) ════╪══▶ PASS/RED
                  │    │            ▲                                                           │    │
                  │    │   golden_xxx.inc (committed) ◀── GOLDEN_BLESS print mode (re-bless) ───┘    │
                  └────┼────────────────────────────────────────────────────────────────────────────┘
                       │
   ┌───────────────────┴─────────────── DELIVERABLE 2: DISPATCH-MIRROR (3-way bind) ──────────────────┐
   │                                                                                                   │
   │   PROTOCOLS.md §0 table  ──parse──▶ {hex → handler}  ═══compare═══  check_dispatch.dispatch()      │
   │   (doc, lines 22-35)                       ▲                          + _ALGO_MEM_TYPE (tool)     │
   │                                            │                                                      │
   │   firmware configure_memory() arms ◀──anchored by── test_dispatch/test_configure_memory.cpp       │
   │   (memory.cpp)                              (native per-protocol routing tests, unchanged)         │
   └───────────────────────────────────────────────────────────────────────────────────────────────────┘

   ┌──────────────── VERIFICATION GATES (frozen-world) ────────────────┐
   │  check_dispatch.py  → "PASS ... 0 dispatch regressions"  (exit 0)  │
   │  diff_db.py         → "0 changed chips ... 0 missing"    (exit 0)  │
   │  pio run -e leonardo→ Flash 25654 B unchanged           (≈0 delta) │
   │  grep over-voltage check + resolve_chip guard           (present)  │
   └───────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| File | Role in Phase 88 |
|------|------------------|
| `firestarter/test/native/avr/_shared/host_stubs_common.inc` | Recording bus (reuse; do NOT modify behavior — opt-in flag only) |
| `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` | Host golden traces for 0x07/0x08/0x0B write + eprom chip-id (P4) |
| `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` | Host golden trace for 0x0D write (SDP/poll) + eeprom28c chip-id (P4) |
| `firestarter/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp` | Host golden trace for 0x10 write (VPP gate P3) + flash_intel chip-id (P4) |
| `firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp` | Host golden trace for 0x06 write (AMD unlock/SDP) |
| `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` | Host golden trace for 0x05 write (256B page) + flash4 chip-id via flash_utils (P4) |
| `firestarter/test/native/avr/.../golden_*.inc` | New committed fixture headers (one per traced path) |
| `firestarter_app/tools/check_dispatch.py` | Tool leg of mirror (rerun gate; import for mirror test) |
| `firestarter_app/tests/test_dispatch_mirror.py` | NEW host pytest binding doc ↔ tool (recommended) |
| `firestarter/doc/PROTOCOLS.md` | §0 table — canonical doc leg (parse only; do not author new table) |
| `firestarter_app/tools/diff_db.py` | DB-frozen gate (rerun) |

### Recommended Project Structure

```
firestarter/test/native/avr/
├── _shared/
│   └── host_stubs_common.inc        # recording bus (reuse, opt-in)
├── test_val_eprom/
│   ├── test_val_eprom.cpp           # extend: golden write 0x07/0x08/0x0B + chip-id
│   ├── golden_eprom_0x07_write.inc  # NEW committed fixtures
│   ├── golden_eprom_0x08_write.inc
│   ├── golden_eprom_0x0B_write.inc
│   └── golden_eprom_chip_id.inc
├── test_val_eeprom28c/  ... golden_eeprom28c_write.inc, golden_eeprom28c_chip_id.inc
├── test_val_flash_intel/... golden_flash_intel_write.inc, golden_flash_intel_chip_id.inc
├── test_val_flash3/     ... golden_flash3_write.inc
├── test_val_flash4/     ... golden_flash4_write.inc, golden_flash4_chip_id.inc
└── _shared/golden_trace.h            # OPTIONAL: shared assert_trace_eq() + bless-print helper

firestarter_app/
└── tests/test_dispatch_mirror.py     # NEW host pytest: doc §0 ↔ check_dispatch.dispatch()
```

### Pattern 1: Recording-bus capture-and-assert (the existing idiom)

**What:** The five `test_val_*` suites already activate `HOST_STUBS_RECORD_BUS` via their `host_stubs.cpp` and read back the captured writes. The golden trace is a thin equality layer on top.

**When to use:** Every golden-trace path.

**Existing recording-bus API (`_shared/host_stubs_common.inc:54-80`):**
```cpp
// Source: firestarter/test/native/avr/_shared/host_stubs_common.inc:54-80
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
    if (s_bus_recording_count < HOST_STUBS_MAX_RECORDING) {       // <-- 256-entry cap (D-04)
        s_bus_recording[s_bus_recording_count].reg  = reg;
        s_bus_recording[s_bus_recording_count].data = (uint8_t)data;  // <-- only low byte (see Pitfall 1)
        s_bus_recording_count++;
    }
}
#endif
```

**Concrete existing assertion excerpt to mirror (INV-04 count assertion, `test_val_flash4.cpp:330-341`):**
```cpp
// Source: firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp:330-341
clear_bus_recording();
h.firestarter_operation_main(&h);
TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code,
    "INV-04: flash4_write_execute must not error on 65-byte zero write");
int sdp_count = count_sdp_occurrences();
TEST_ASSERT_EQUAL_INT_MESSAGE(1, sdp_count, "INV-04: ...");
```

The golden-trace assertion generalizes this from "count the SDP signature" to "every `(reg, data)` matches the pinned array."

### Pattern 2: Re-bless via a compile-time print mode

**What:** A `#ifdef GOLDEN_BLESS` block that, instead of asserting, prints the captured recording in `.inc`-ready form (e.g. `{ CONTROL_REGISTER, 0x80 },`). The operator/executor runs the suite once with `-D GOLDEN_BLESS`, redirects the printed block into the `.inc` file, and reviews the git diff. Normal runs (no flag) assert.

**When to use:** Initial authoring of each fixture and any Phase-89 re-bless.

**Example bless/assert skeleton:**
```cpp
// Source: pattern proposed for Phase 88 (composed from existing recording-bus API)
static const bus_record_entry_t golden_eprom_0x07_write[] = {
#include "golden_eprom_0x07_write.inc"   // committed fixture: { reg, data }, rows
};
static const int golden_eprom_0x07_write_n =
    sizeof(golden_eprom_0x07_write) / sizeof(golden_eprom_0x07_write[0]);

static void assert_trace_eq(const bus_record_entry_t* expected, int n, const char* ctx) {
    TEST_ASSERT_EQUAL_INT_MESSAGE(n, bus_recording_count(), ctx);   // count first (D-01)
    for (int i = 0; i < n; i++) {
        TEST_ASSERT_EQUAL_HEX8_MESSAGE(expected[i].reg,  recorded_reg(i),  ctx);
        TEST_ASSERT_EQUAL_HEX8_MESSAGE(expected[i].data, recorded_data(i), ctx);
    }
}

#ifdef GOLDEN_BLESS   // bless mode: print the .inc body instead of asserting
static void print_trace_inc(void) {
    for (int i = 0; i < bus_recording_count(); i++)
        printf("    { 0x%02X, 0x%02X },\n", recorded_reg(i), recorded_data(i));
}
#endif
```
`pio test` captures stdout, so `print_trace_inc()` output is recoverable from the test log; alternatively run the test binary directly under `.pio/build/native/`. The planner should pick whichever stdout-capture seam is cleanest — both are one-step.

### Pattern 3: Dispatch-mirror three-way bind (host pytest + native anchor)

**What:** A host pytest parses the PROTOCOLS.md §0 markdown table into `{hex: handler}`, derives the same map from `check_dispatch.dispatch()` + `_ALGO_MEM_TYPE`, and asserts they agree. The native `test_dispatch/test_configure_memory.cpp` already pins the firmware arms (one `test_protocol_0xNN_dispatches_*` per protocol), so the firmware leg is anchored without a firmware change.

**When to use:** The single dispatch-mirror deliverable (D-05/D-06).

**Parsing approach for the §0 table (handler column = col 3 of the pipe table at PROTOCOLS.md:22-35):**
```python
# Source: pattern proposed for Phase 88 (parses firestarter/doc/PROTOCOLS.md §0 table)
import re, pathlib
ROW = re.compile(r"^\|\s*0x([0-9A-Fa-f]+)\s*\|[^|]*\|\s*`([a-z0-9_]+\.cpp|not_implemented\.cpp)`\s*\|")
def parse_protocols_md(path):
    table = {}
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m:
            table[int(m.group(1), 16)] = m.group(2)   # {0x05: "flash_type_4.cpp", ...}
    return table
# Map doc handler-file → check_dispatch handler-function name to compare the two legs:
DOC_FILE_TO_FUNC = {
    "flash_type_4.cpp": "configure_flash4",
    "flash_type_3.cpp": "configure_flash3",
    "eprom.cpp":        "configure_eprom",
    "eeprom_28c.cpp":   "configure_eeprom28c",
    "flash_intel.cpp":  "configure_flash_intel",
    "sram.cpp":         "configure_sram",
    "not_implemented.cpp": "not_implemented",
}
```

The §0 table is reliably machine-parseable: 12 rows, fixed 5-column layout, handler in backticks in column 3 (verified by reading lines 22-35). 0x35/0x39 are NOT in §0 (they are documented as phantom non-protocols in §2, lines 327-328) — the mirror should treat them via the `not_implemented` host-routing rule, matching `check_dispatch`'s comment "host excludes both from KNOWN_PROTOCOLS and routes them to not_implemented."

### Anti-Patterns to Avoid
- **Asserting `CTRL_VPP_VPE_DROP_ENABLE` (0x100) bytes:** the recording buffer stores only the low byte (`(uint8_t)data`, `host_stubs_common.inc:73`). On Rev2 `CTRL_VPP_VPE_DROP_ENABLE` is `0x100` and is **invisible** in an 8-bit golden trace. Pin only 8-bit-fit bits, or document that the 0x100 bit is intentionally outside trace scope (the existing INV tests already note this — `test_val_eprom.cpp:108-112`).
- **Authoring a new canonical dispatch table:** D-06 forbids it. Parse the existing §0 table.
- **Adding PROGMEM strings to firmware:** would break D-08 (flash delta). All new code is test-only / host-only.
- **Over-sized write fixtures:** a flash4 256-byte page write would blow the 256-entry cap (each byte is multiple register writes). Use the INV-04 65-byte discipline (D-04).
- **Re-tracing read/blank-check paths:** D-03 scopes traces to write + chip-id only; read paths stay on the existing INV tests.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Capturing register writes | A new mock layer | `HOST_STUBS_RECORD_BUS` in `host_stubs_common.inc` | Already records ordered `(reg,data)` with a clean C API; Phase 71 HARN-01 |
| Dispatch sim in Python | A re-implementation of `configure_memory` | `check_dispatch.dispatch()` | Already mirrors firmware order line-for-line (`check_dispatch.py:133-157`); it IS the tool leg |
| DB freeze gate | A custom JSON differ | `diff_db.py` | Composite-keyed 1:1 diff + cited root-cause rules already exists; rerun it |
| Dispatch freeze gate | A custom scan | `check_dispatch.py` | 746-chip scan + BLOCKER-2/WARNING-5/GATE-03 guards already exist; rerun it |
| Firmware-leg dispatch anchor | A new C++ mirror test | `test_dispatch/test_configure_memory.cpp` | One positive test per KNOWN_PROTOCOLS entry already pins the arms |
| Markdown table parse | A markdown library dependency | stdlib `re` over the fixed pipe table | The §0 table is a fixed 5-column layout; a one-line regex suffices, no new dep (CI gate stays clean) |

**Key insight:** Phase 88 is almost entirely *assembly of existing instrumentation* — the recording bus, the dispatch sim, and the two gates all exist and are green. The only genuinely new artifacts are the committed golden `.inc` fixtures, a tiny `assert_trace_eq`/bless helper, and one host pytest. Building anything heavier signals scope creep.

## Runtime State Inventory

> Phase 88 is a test-authoring + guard phase, not a rename/refactor/migration. This section applies the discipline anyway because the deliverable's *correctness* depends on committed artifacts and pinned baselines being in the expected state.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | The pinned baselines `tools/baseline/chip_database.baseline.json` (746 chips) and `tools/baseline/dispatch_baseline.json` (158744 B) — Phase-86-repinned. `diff_db.py` compares the live DB against the former. | None — must stay UNCHANGED (D-07). diff_db verified empty this session. |
| Live service config | None — no external service, no UI-resident config. | None ("None — verified: this phase touches only repo files + native tests"). |
| OS-registered state | None — no scheduled tasks, daemons, or installed binaries. | None. |
| Secrets/env vars | The gate tools honor `FIRESTARTER_DB_FILE` / `FIRESTARTER_PINOUTS_FILE` / `FIRESTARTER_BASELINE_FILE` env overrides (`check_dispatch.py:26-33`, `diff_db.py:32-39`). Code reads them by exact name. | None — do not rename. If the dispatch-mirror test wants to point at a fixture DB, set these vars (the test seam already exists). |
| Build artifacts | `.pio/build/native/` (per-suite test binaries) and `.pio/build/leonardo/` (the flash-size reference). `dispatch_baseline.json` is committed but currently consumed by **no tool** (grep found 0 references) — it is an inert pinned artifact. | Rebuild `[env:leonardo]` to confirm flash delta (D-08). The mirror test could optionally bind `dispatch_baseline.json` to give it a live consumer, but that is discretionary. |

**The canonical question (adapted):** *After the new tests + fixtures land, what state must remain byte-identical?* Answer: the two committed baselines (DB + dispatch), every existing DB record (diff_db empty), the Leonardo production flash image (≈25654 B), and the firmware source of the two over-voltage checks + the host `resolve_chip` guard.

## Common Pitfalls

### Pitfall 1: 0x100 control bit invisible in the 8-bit recording
**What goes wrong:** A golden trace silently drops `CTRL_VPP_VPE_DROP_ENABLE` (0x100 on Rev2), so a regression that flips that bit would NOT trip the trace.
**Why it happens:** `rurp_write_to_register` casts `data` to `uint8_t` before storing (`host_stubs_common.inc:73`); the recording entry is `uint8_t`.
**How to avoid:** Document in each fixture header that the trace pins low-byte semantics only; keep the existing INV-01/INV-03 bit-level assertions (which already account for this — `test_val_eprom.cpp:108-116`) as the complementary guard. Do NOT widen the recording struct (that would change harness behavior the other suites depend on byte-exactly, per `host_stubs_common.inc:50-53`).

### Pitfall 2: Recording overflow truncates the trace at 256
**What goes wrong:** A write fixture that exceeds 256 register writes is silently truncated (`if (s_bus_recording_count < HOST_STUBS_MAX_RECORDING)`), so the count assertion passes against a too-short golden array authored from the same truncated capture.
**Why it happens:** Each programmed byte emits several register writes (address LSB/MSB + control + data); flash4's 256-byte page write blows the cap.
**How to avoid:** Size every write fixture to a **minimal representative input** under the cap (D-04). INV-04 already demonstrates this with a 65-byte probe (`test_val_flash4.cpp:323`). For each family, pick the smallest input that still exercises every algorithm branch (one SDP unlock, one program pulse, one poll/verify cycle). Add a defensive `TEST_ASSERT_TRUE(bus_recording_count() < HOST_STUBS_MAX_RECORDING)` so an accidentally-oversized capture fails loudly instead of silently truncating.

### Pitfall 3: `configure_memory()` resets handle function pointers
**What goes wrong:** Chip-id traces that inject scripted bytes via `firestarter_get_data` get the pointer clobbered.
**Why it happens:** `configure_memory()` reassigns `firestarter_get_data` to the real `memory_get_data` after dispatch (documented in `test_eeprom28c_chip_id.cpp:95-100`).
**How to avoid:** Re-assign the mock pointer AFTER `configure_memory(&h)` and before `operation_init(&h)` — the established idiom (`test_eeprom28c_chip_id.cpp:107-108`). The chip-id traces must follow this pattern.

### Pitfall 4: Unmocked `delay`/`delayMicroseconds` aborts the suite
**What goes wrong:** ArduinoFake aborts when an un-stubbed virtual is called; `eprom_check_vpp` calls `delay(100)`, `eprom_write_execute` calls `delay(500)`, `memory_set_data` calls `delayMicroseconds`.
**Why it happens:** fakeit requires `When(...)` setup before the virtual fires.
**How to avoid:** The existing `setUp()` in each suite already stubs these (`test_val_eprom.cpp:72-77`). New write/chip-id traces reuse the same setUp — verify the specific delays each new path hits are covered.

### Pitfall 5: CI py3.11 vs devcontainer py3.12 masks host-mirror failures
**What goes wrong:** A host dispatch-mirror test (or a ruff/format nit) passes in the py3.12 devcontainer but fails CI on py3.11.
**Why it happens:** CI pins `python-version: '3.11'` (`.github/workflows/ci.yml:32`); the devcontainer runs 3.12 (documented in MEMORY).
**How to avoid:** Validate the new pytest under `ruff check` + `ruff format --check` (the firestarter_app tooling gate) before claiming green; avoid f-string-backslash constructs. Run the test with the target's behavior in mind. The mirror test is pure stdlib + json/re, so runtime behavior is identical, but the lint gate is the real trap.

### Pitfall 6: 5V-family `vpp_mv=12000` is a WP-pin voltage, not programming VPP
**What goes wrong:** A naive VPP invariant on the golden traces would false-positive on every AMD/SST flash chip (they list `vpp_mv=12000` for the write-protect pin).
**Why it happens:** `chip_database.json` stores WP-pin voltage in `electrical.vpp_mv` for 5V handlers (documented at length in `check_dispatch.py:60-93`).
**How to avoid:** Golden traces assert register-write *sequences*, not derived VPP semantics — this pitfall is mostly a warning not to re-derive VPP logic. The only DB-checked VPP invariant is `configure_flash_intel` (`_DB_CHECKED_VPP_INVARIANTS`, `check_dispatch.py:93`); don't extend it.

## Code Examples

### Capturing a write-path golden trace (P3/P5/P7 shape)
```cpp
// Source: composed from test_val_eprom.cpp:121-160 (write+init idiom) + the assert_trace_eq pattern
void test_golden_eprom_0x07_write(void) {
    firestarter_handle_t h = make_handle(0x07, CMD_WRITE);  // existing helper, FLAG_SKIP_BLANK_CHECK|SKIP_ERASE
    h.data_size = 1;          // minimal representative input (D-04)
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
    clear_bus_recording();    // isolate the init+execute trace from configure-phase address writes
    if (h.firestarter_operation_init) h.firestarter_operation_init(&h);
    if (h.firestarter_operation_main) h.firestarter_operation_main(&h);
    TEST_ASSERT_TRUE(bus_recording_count() < HOST_STUBS_MAX_RECORDING);  // anti-truncation guard
#ifdef GOLDEN_BLESS
    print_trace_inc();        // emit golden_eprom_0x07_write.inc body
#else
    assert_trace_eq(golden_eprom_0x07_write, golden_eprom_0x07_write_n,
                    "golden trace drift: eprom 0x07 write");
#endif
}
```

### Driving the chip-id (P4) path in a native test
```cpp
// Source: test_dispatch/test_configure_memory.cpp:170-177 (CMD_CHECK_CHIP_ID dispatch)
//         + test_eeprom28c_chip_id.cpp:101-110 (scripted-byte injection idiom)
firestarter_handle_t h = make_handle(0x05, CMD_CHECK_CHIP_ID);  // flash4 P4 via flash_utils
h.chip_id = 0xBFB7;            // non-zero enables the compare
configure_memory(&h);
h.firestarter_get_data = mock_get_data_scripted;   // RE-ASSIGN after configure_memory (Pitfall 3)
clear_bus_recording();
if (h.firestarter_operation_main) h.firestarter_operation_main(&h);  // flash_util_check_chip_id_execute
// then assert_trace_eq against golden_flash4_chip_id.inc
```

### Host dispatch-mirror assertion (doc ↔ tool)
```python
# Source: pattern proposed for Phase 88; binds PROTOCOLS.md §0 (firestarter sub-repo) to check_dispatch
def test_dispatch_mirror_doc_matches_tool():
    doc = parse_protocols_md(PROTOCOLS_MD_PATH)            # {hex: "<handler>.cpp"}
    for hex_id, handler_file in doc.items():
        if hex_id in (0x35, 0x39):                          # phantom: host routes to not_implemented
            continue
        expected_func = DOC_FILE_TO_FUNC[handler_file]
        mt = check_dispatch._ALGO_MEM_TYPE.get(hex_id, 0)
        got_func = check_dispatch.dispatch(hex_id, mt)
        assert got_func == expected_func, f"0x{hex_id:02X}: doc={expected_func} tool={got_func}"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No-op register stubs (dispatch tests assert only `response_code`) | Recording-bus stub captures ordered `(reg,data)` | Phase 71 HARN-01 | Enables side-effect-level traces — the foundation Phase 88 builds on |
| INV assertions: targeted single-property checks (count an SDP, check a bit) | Byte-exact full-sequence golden traces (D-01) | Phase 88 (this) | Strictly stronger oracle; INV tests remain as complementary bit-level guards |
| `build_db.py` Rule1/2/3 + WARNING-5 runtime override | Single principled `classify()` (Phase 86 VAR-02); WARNING-5 is decode-time, not runtime | Phase 86 | INV-08 is **dispatch-only** firmware-side; the WARNING-5 retirement is host-side and NOT firmware-testable (`PROTOCOLS.md:383`) |

**Deprecated/outdated:**
- `dispatch_baseline.json` is committed but consumed by **no tool** (grep: 0 references). Treat as inert; the mirror test may optionally bind it for a live consumer, but this is discretionary, not required.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `pio test` captures the `GOLDEN_BLESS` stdout in a recoverable form for one-step re-bless | Pattern 2 | If stdout isn't cleanly captured, the executor runs the native binary directly under `.pio/build/native/` — still one-step, minor workflow change. LOW risk. |
| A2 | The four chip-id call sites each set a non-NULL `operation_main` reachable on host (confirmed for flash4 via `test_configure_memory.cpp:170-195`; eprom via `eprom.cpp:113-115`; eeprom28c via init; flash_intel via `flash_intel.cpp:124-127`) | D-03 trace coverage | If a chip-id path needs hardware-only behavior the host can't reach, that family's chip-id trace may need a scripted-byte mock (idiom exists). LOW risk — all four have host-driven precedents. |
| A3 | A minimal representative write input (1 byte for eprom; 65 for flash4; small for others) exercises the full P3/P5/P7 algorithm shape | D-04 | If a branch only fires on larger inputs (e.g. multi-page), the trace under-covers. MEDIUM — the executor must verify each fixture hits every algorithm branch, not just stay under the cap. |

**Note:** No package/version/compliance assumptions exist (no external deps). The above are workflow/coverage assumptions the planner should surface as verification steps, not user-confirmation decisions.

## Open Questions

1. **Should the mirror test also bind `dispatch_baseline.json`?**
   - What we know: it is committed (158744 B) but currently has zero consumers.
   - What's unclear: whether the operator wants it given a live consumer or left inert.
   - Recommendation: leave inert for Phase 88 (out of the D-05 three-way scope); note it for a future phase. Binding it is harmless but adds surface the operator didn't request.

2. **One mirror test or a pair (host + native)?**
   - What we know: the firmware leg is already anchored by `test_configure_memory.cpp`; a host pytest can bind doc ↔ tool.
   - What's unclear: whether the planner wants an explicit cross-reference (e.g. the host test asserting the native test enumerates the same protocol set).
   - Recommendation: a single host pytest for doc↔tool + reliance on the existing native `test_dispatch` for the firmware leg satisfies D-05's "all three bound." Optionally add a one-line host assertion that the native test file enumerates every §0 protocol (a grep of `test_configure_memory.cpp` for `test_protocol_0xNN`) to make the firmware-leg binding explicit and drift-tripping.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | native tests + leonardo flash gate | ✓ | 6.1.19 | — |
| `[env:leonardo]` build | D-08 flash-delta gate | ✓ | builds clean (25654 B, 89.5%) | — |
| Python 3 (devcontainer) | run check_dispatch/diff_db + mirror test | ✓ | 3.12 (CI uses 3.11) | validate lint against 3.11 target |
| pytest + ruff (firestarter_app `[test]`) | host mirror test + tooling gate | ✓ (per CI) | per `[test]` extra | `pip install -e '.[test]'` |
| `chip_database.json` + baselines | frozen-world gates | ✓ | 746 chips; baseline 746 | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none — all gates ran green this session.

## Validation Architecture

> `workflow.nyquist_validation` is absent from `.planning/config.json` → treated as ENABLED.

### Test Framework
| Property | Value |
|----------|-------|
| Framework (firmware) | Unity via PlatformIO `[env:native]` (`test_framework=unity`) |
| Framework (host) | pytest (firestarter_app `[test]` extra) |
| Config file | `firestarter/platformio.ini` (`[env:native]`); `firestarter_app/pyproject.toml` (pytest/ruff/mypy) |
| Quick run command (firmware) | `pio test -e native -f "*test_val_eprom*"` (single suite) |
| Quick run command (host) | `python3 tools/check_dispatch.py` / `python3 tools/diff_db.py` (sub-30s) |
| Full suite command (firmware) | `pio test -e native` |
| Full suite command (host) | `pytest` (in `firestarter_app`) |
| Flash-delta gate | `pio run -e leonardo` → compare Flash bytes to 25654 baseline |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PRIM-01 | Per-family byte-exact write+chip-id golden traces exist & pass | unit (native) | `pio test -e native -f "*test_val_*"` | Suites ✅; golden `.inc` + asserts ❌ Wave 0 |
| PRIM-01 | Dispatch-order test binds doc↔tool↔firmware | unit (host + native anchor) | `pytest tests/test_dispatch_mirror.py` + `pio test -e native -f "*test_dispatch*"` | native anchor ✅; mirror test ❌ Wave 0 |
| SAFE-02 | INV-01..09 invariants stay green | unit (native) | `pio test -e native` | ✅ (existing) |
| SAFE-04 | check_dispatch 0 violations | gate (host) | `python3 tools/check_dispatch.py` | ✅ green this session |
| SAFE-04 | diff_db empty | gate (host) | `python3 tools/diff_db.py` | ✅ green this session |
| SAFE-04 | Leonardo flash near-zero delta | gate (build) | `pio run -e leonardo` | ✅ baseline 25654 B |
| SAFE-04 | over-voltage check present/unmodified | structural (grep/test) | `grep -n "vpp_mv > (uint32_t)handle->vpp_mv + 500" src/proms/eprom.cpp src/proms/flash_intel.cpp` | ✅ present (`eprom.cpp:282`, `flash_intel.cpp:65`) |
| SAFE-04 | resolve_chip guard never bypassed | structural (grep/test) | `grep -n "support_status != \"supported\"" firestarter/chip_resolver.py` | ✅ present (`chip_resolver.py:55`) |
| SAFE-01 | dispatch keys on `handle->protocol` first | structural | covered by mirror test + WARNING-5 buckets in check_dispatch | ✅ |

### Sampling Rate
- **Per task commit:** the single touched suite — `pio test -e native -f "*test_val_<family>*"` (or `pytest tests/test_dispatch_mirror.py` for the mirror task). Sub-30s.
- **Per wave merge:** full native suite `pio test -e native` + both gates `check_dispatch.py` / `diff_db.py`.
- **Phase gate:** full native suite green + both host gates exit 0 + `pio run -e leonardo` flash unchanged + the two safety-posture greps present, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `golden_<family>_write.inc` × 5 + `golden_<family>_chip_id.inc` × 4 — committed fixtures (PRIM-01)
- [ ] Shared `assert_trace_eq()` + `GOLDEN_BLESS` print helper (in a `_shared/golden_trace.h` or duplicated per suite)
- [ ] Golden-trace test functions wired into each `test_val_*` `main()` RUN_TEST list
- [ ] `firestarter_app/tests/test_dispatch_mirror.py` — doc↔tool bind (PRIM-01/SAFE-02)
- [ ] (optional) explicit host assertion that native `test_dispatch` enumerates every §0 protocol (firmware-leg drift trip)

*Framework install: none — Unity/ArduinoFake bundled by PIO; pytest via existing `[test]` extra.*

## Security Domain

> `security_enforcement` is not set to `false` in config → treated as enabled. This phase's security surface is **electrical safety** (VPP over-voltage / mis-dispatch hazard), not network/auth. The standard ASVS categories below are mostly N/A for an offline firmware-test phase; the project-specific safety model substitutes.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | offline CLI + USB serial; no auth surface |
| V3 Session Management | no | n/a |
| V4 Access Control | no | n/a |
| V5 Input Validation | partial | `json_parser.c` validates wire fields; not touched this phase |
| V6 Cryptography | no | n/a (CRC8 is integrity, not security) |

### Known Threat Patterns for {RURP firmware + host CLI}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Mis-dispatch routes a 5V part to `configure_eprom` → 12V VPP on a 5V pin (hardware damage) | Tampering / DoS (physical) | BLOCKER-2 + WARNING-5 + GATE-03 guards in `check_dispatch.py` (verified green); dispatch keys on `handle->protocol` first (SAFE-01); the dispatch-mirror trips on any drift |
| Over-voltage VPP applied beyond the chip's `vpp_mv` setpoint | Tampering (physical) | `eprom_check_vpp` / `flash_intel_check_vpp` error (unless `FLAG_FORCE`) when `vpp_mv > setpoint + 500` (`eprom.cpp:282`, `flash_intel.cpp:65`); SC#4 verifies present + unmodified |
| Writing an irreplaceable UV part on an unstable read path | DoS (physical) | 2516 stays `support_status`-resolvable but `UNVERIFIED` (not write-graduated); diff_db empty keeps it unmoved (D-09) |
| Non-supported chip reaching a real handler | Elevation (physical) | `chip_resolver.resolve_chip` raises `ChipNotImplementedError` for any `support_status != "supported"` BEFORE any wire byte (`chip_resolver.py:55-57`) — authoritative host guard |

## Sources

### Primary (HIGH confidence — read this session)
- `firestarter/test/native/avr/_shared/host_stubs_common.inc:54-80` — recording-bus API + 256 cap
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` (full) — write+init idiom, INV assertions, 0x100-bit caveat
- `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` (full) — INV-04 65-byte probe, SDP-count idiom
- `firestarter/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp` (full) — P3 VPP-gate trace + custom-voltage stub
- `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` (full) — chip-id (P4) scripted-byte injection + pointer-reassign idiom
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` (full) — firmware-leg dispatch anchor + CMD_CHECK_CHIP_ID
- `firestarter/doc/PROTOCOLS.md:1-40, 325-402` — §0 table layout (lines 22-35), §2 phantom buckets, §3 INV matrix
- `firestarter_app/tools/check_dispatch.py` (full) — `dispatch()` sim, `_ALGO_MEM_TYPE`, `KNOWN_PROTOCOLS`, guard buckets
- `firestarter_app/tools/diff_db.py` (full) — composite-key diff + root-cause rules
- `firestarter_app/firestarter/chip_resolver.py:13-62` — `resolve_chip` host guard
- `firestarter/src/proms/eprom.cpp:262-300` + `flash_intel.cpp:52-90` — over-voltage VPP check bodies
- `firestarter/CLAUDE.md` §Protocol Dispatch + §Native Test Environment — dispatch order, env layout
- Executed gates this session: `check_dispatch.py` → PASS exit 0; `diff_db.py` → 0 changed exit 0; `pio run -e leonardo` → Flash 25654 B SUCCESS

### Secondary (MEDIUM confidence)
- `firestarter_app/.github/workflows/ci.yml:29-32` — CI pins Python 3.11
- Project MEMORY entries — devcontainer py3.12 masks CI; v1.16 seed (P87 INV matrix, INV-08 dispatch-only)

### Tertiary (LOW confidence)
- none — every claim verified against read source or executed command.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no external deps; all tooling confirmed present + green
- Architecture (recording bus / dispatch sim / gates): HIGH — read full source, ran gates
- Golden-reference representation recommendation: MEDIUM-HIGH — `.inc` form is a design recommendation grounded in the re-bless constraint; planner may choose inline
- Dispatch-mirror shape: HIGH — three legs all read; host-pytest split is the natural decomposition
- Pitfalls: HIGH — each grounded in a specific source line or executed result

**Research date:** 2026-06-26
**Valid until:** 2026-07-26 (stable — in-repo test infra; the only volatility is if Phase 89 starts before planning, which would change the "frozen" baselines)
