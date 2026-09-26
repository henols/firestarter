# Phase 98: FIX — Correct the 0x08 32-Pin Write/VPP Path - Pattern Map

**Mapped:** 2026-06-30
**Files analyzed:** 7 modified + 2 test/fixture (9 total)
**Analogs found:** 9 / 9 (every file has an in-repo analog — this is a re-scope/extend phase, not net-new)

> This is a **firmware + host-data** phase. No frontend, no new service, no migration.
> The fix is mostly *re-scoping and extending existing machinery* (RESEARCH "Key insight").
> Every pattern below cites a live, verified-this-session analog with file:line.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/firestarter/data/pinouts.json` (new `DIP32_27C020` entry) | config (DB/pinout) | transform (pin→bus-line) | `DIP32_SST39SF040` entry (same file, `:74-83`) | exact — scoped DIP32 variant precedent |
| `firestarter_app/tools/build_db.py` (`resolve_pinout_key` 0x08-≤256K branch) | utility (DB pipeline) | transform (size/proto → pinout key) | `resolve_pinout_key` pin_count==32 branch (`:281-296`) | exact — same function, add a size-keyed arm |
| `firestarter_app/firestarter/data/chip_database.json` (AM27C020 row `pinout`) | config (generated artifact) | CRUD (static record) | AM27C040/AM27C080 rows (same file, `:287-323`) | exact — sibling rows on `DIP32_STD` |
| `firestarter_app/firestarter/database.py` (`get_bus_config` consumes new pinout) | service (host bus-config build) | transform | `get_bus_config` static-high / rw-pin handling (`:278-332`) | exact — already parses `static-high-pins`/`rw-pin` |
| `firestarter/src/proms/memory.cpp` (PGM-assert in `memory_set_data` / remap) | service (firmware program pulse) | request-response (CE pulse) | `memory_set_data` (`:274-284`) + `mem_util_remap_address_bus` (`:309-332`) | exact — the CE-only pulse seam + static_high_mask OR |
| `firestarter/src/proms/eprom.cpp` (P1-hold window extension, gate) | service (firmware EPROM handler) | request-response | `program_mismatched_bytes` (`:168-180`) + `eprom_internal_set_control_register` (`:319-326`) | exact — P1-hold already 90% built here |
| `firestarter/include/firestarter.h` + `firestarter_app/firestarter/constants.py` (only if D-03 escalates to a new wire field) | config (wire-struct lockstep) | n/a | `page_size` (`firestarter.h:97`) ↔ `JSON_KEY_PAGE_SIZE` (`constants.py:100`) | role-match — lockstep precedent, last resort |
| `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` (corrected-path test + mismatch test) | test (native Unity) | event-driven (recording assert) | `test_inv03_eprom_0x08_p1_as_vpp` (`:320-354`) + WR-02a (`:615-657`) | exact — INV-03 recording pattern + WR-02 mismatch fork |
| `firestarter/test/native/avr/test_val_eprom/golden_eprom_0x08_write.inc` (re-bless ONLY if changed) | test fixture (golden trace) | transform (pinned (reg,data) rows) | `golden_eprom_0x08_write.inc` (itself) + bless flow | exact — re-pin in place, cite rationale |

---

## Pattern Assignments

### `pinouts.json` — new `DIP32_27C020` entry (host, config / transform)

**Analog:** `DIP32_SST39SF040` (`firestarter_app/firestarter/data/pinouts.json:74-83`) — the proven scoped-DIP32-variant precedent. It moves pin 31 OUT of `address-bus-pins` (into `rw-pin`) and relocates A18; the new entry follows the same structural move for pin 31 but **keeps `vpp-pin: [1]`** (27C020 has VPP on pin 1).

**Live `DIP32_STD` baseline** (`:64-72`) — pin 31 is the 19th `address-bus-pins` entry (= line 22 = A18):
```json
"DIP32_STD": {
  "pins": {
    "vcc-pin": [32], "gnd-pin": [16], "vpp-pin": [1],
    "address-bus-pins": [12,11,10,9,8,7,6,5,27,26,23,25,4,28,29,3,2,30,31],
    "data-bus-pins": [13,14,15,17,18,19,20,21],
    "ce-pin": [22], "oe-pin": [24]
  }
}
```

**Scoped-variant precedent** (`:74-83`) — note pin 31 removed from `address-bus-pins`, expressed as `rw-pin`, and a verbose `comment` citing the datasheet source:
```json
"DIP32_SST39SF040": {
  "comment": "Per piersfinlayson/one-rom (datasheet-verified): ... A18 at pin 1 (NOT VPP) and WE at pin 31 (NOT address bus). ...",
  "pins": {
    "vcc-pin": [32], "gnd-pin": [16],
    "address-bus-pins": [12,11,10,9,8,7,6,5,27,26,23,25,4,28,29,3,2,30,1],
    "data-bus-pins": [13,14,15,17,18,19,20,21],
    "ce-pin": [22], "oe-pin": [24], "rw-pin": [31]
  }
}
```

**Pattern for `DIP32_27C020`:** drop `31` from `address-bus-pins` (so the firmware bus-config no longer drives line 22 from an address bit); keep `vpp-pin: [1]`; express pin 31's PGM role via a pin-function the existing `get_bus_config` already understands. The **preferred no-new-wire-field vehicle** is `static-high-pins: [31]` (RESEARCH Pattern 1 option (a), `database.py:322-332` already plumbs it end-to-end) — **subject to the polarity Open-Question Q1** (PGM is program-active LOW, `static_high_mask` drives HIGH; if HIGH-on-line-22 ≠ PGM=VIL at the socket, the assert must instead be a firmware clear/hold-low of line 22 — see firmware seam below). **Write a verbose `comment`** citing `AM27C020.pdf` (pin 31 = PGM, VPP on pin 1) and the ≤256K-only scope (D-02/D-04), mirroring the `DIP32_SST39SF040` comment style.

---

### `build_db.py` — `resolve_pinout_key` 0x08-≤256K arm (host, utility / transform)

**Analog:** `resolve_pinout_key`, pin_count==32 branch (`firestarter_app/tools/build_db.py:281-296`). A1 is **CONFIRMED**: this is a pure function of decoded fields including `mem_size`, so a ≤256K-keyed arm is expressible here (no post-process override needed).

**Live branch to extend** (`:285-296`):
```python
elif pm_idx in {5, 7, 9, 10, 11, 12, 13}:
    # Mixed flash/EPROM families — proto_id discriminates
    if proto_id in {0x05, 0x06}:
        key = "DIP32_SST39SF040"  # 5V flash; no VPP, WE=31
    elif proto_id == 0x0D:
        key = "DIP32_28C512_EEPROM"  # 5V EEPROM; WE=30, no VPP
    elif proto_id in {0x07, 0x08, 0x10}:
        key = "DIP32_STD"  # UV-EPROM / Intel-flash; VPP=pin 1
    else:
        key = None
```

**Pattern:** add a size-keyed sub-condition inside the `proto_id in {0x07, 0x08, 0x10}` arm: `proto_id == 0x08 and mem_size <= 262144` → `"DIP32_27C020"`, else stays `"DIP32_STD"`. This **structurally excludes** 512K/1M (AM27C040 524288 / AM27C080 1048576 stay on `DIP32_STD`, A18 on pin 31) — the D-04 host-side guard. Keep the inline `#` rationale comment in the existing style. The `key not in VALID_PINOUT_KEYS` warn at `:298` is the safety net.

---

### `chip_database.json` — AM27C020 row (host, generated config / CRUD)

**Analog:** AM27C040 (`:287-305`) / AM27C080 (`:307-...`) sibling rows — same `algorithm: 8`, `pin_count: 32`, all currently `"pinout": "DIP32_STD"`.

**Live AM27C020 row** (`:277-285`):
```json
"part_number": "AM27C020",
"pinout": "DIP32_STD",
"programming": { "algorithm": 8, "chip_id_check": true,
                 "chip_id_value": "0x00000197", "pulse_duration": "100 us" },
"support_status": "supported"
```
(`electrical.size_bytes` = 262144, `vpp_mv` = 13000.)

**Pattern:** **do NOT hand-edit** (`firestarter_app/CLAUDE.md`: "generated chip database (do NOT edit by hand"; Pitfall 7). Regenerate via `python tools/build_db.py` after the `resolve_pinout_key` change → AM27C020 (256K, 0x08) flips to `"DIP32_27C020"` while AM27C040/AM27C080 (512K/1M) stay `"DIP32_STD"`. Then review with `diff_db.py` (below) and re-pin the baseline with a cited rule. **Verify the diff shows ONLY 256K 0x08/32-pin rows changed** (D-02 review surface, Pitfall 1 warning sign).

---

### `database.py` — `get_bus_config` (host, service / transform; likely NO edit)

**Analog / live consumer:** `get_bus_config` (`:278-332`). It already parses `address-bus-pins` (`:289-297`), `rw-pin`/`vpp-pin` (`:305-320`), and `static-high-pins` → `map_config["static-high"]` (`:322-332`). `pin_conversions[32][31] = 22` (the host A18 mapping, `database.py:78` block) is what currently routes pin 31 onto bus line 22.

```python
if "static-high-pins" in pin_map_data and pins in pin_conversions:
    static_high = []
    for pin in pin_map_data["static-high-pins"]:
        if pin in pin_conversions[pins]:
            static_high.append(pin_conversions[pins][pin])
        ...
    if static_high:
        map_config["static-high"] = static_high
```

**Pattern:** if `DIP32_27C020` expresses PGM via `static-high-pins: [31]`, **no `database.py` change is needed** — pin 31 (→ line 22) flows into `static-high` → wire `static-high` → firmware `static_high_mask`. Only touch `database.py` if a genuinely new pin-function field is required (D-03 escalation; avoid). The `vpp-pin` ROM_CE/ROM_OE guard at `:314-315` is the precedent for "function present but resolves to a reserved line — skip."

---

### `memory.cpp` — deliberate PGM-assert seam (firmware, service / request-response)

**Analog:** `memory_set_data` (`firestarter/src/proms/memory.cpp:346-356`) — the CE-only program pulse (RC-1 secondary surface), and `mem_util_remap_address_bus` (`:309-332`) — where `static_high_mask` is ORed in.

**Live CE-only pulse** (`:274-284`):
```cpp
void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_chip_input();
    address = mem_util_remap_address_bus(handle, address, WRITE_FLAG);  // pin 31 = line 22 from addr bit
    handle->firestarter_set_address(handle, address);
    rurp_write_data_buffer(data);
    delayMicroseconds(3);
    rurp_chip_enable();                       // CE low
    delayMicroseconds(handle->pulse_delay);   // 100µs for 0x08
    rurp_chip_disable();                       // CE high
}
```

**Live static_high OR** (`:330` inside `mem_util_remap_address_bus`):
```cpp
    reorg_address |= config.static_high_mask;   // lines unconditionally driven HIGH
    return reorg_address;
```

**Pattern (D-01 belt, D-03 preference):** drive pin 31's bus line (now a static_high/PGM line via `DIP32_27C020`) to the program-active level and hold it across the CE-pulse window, **gated** on `handle->protocol == 0x08 && handle->pins == 32 && handle->mem_size <= 262144` (the A18-unused belt — Pattern 2). Prefer composing from `static_high_mask` (already ORed at `:330`) over a new wire field. **Polarity caveat (Q1):** AM27C020 programs with PGM=VIL; if `static_high_mask` (HIGH) cannot express a LOW-hold at the socket, add an explicit firmware clear/hold-low of line 22 inside the gated branch of `memory_set_data`, with a datasheet-cited comment. **Do NOT hardcode "pin 31 = PGM"** — the role flows from the host pinout (CONTEXT Integration Points); the firmware reads `bus_config`/protocol/size.

---

### `eprom.cpp` — P1-hold window + gate (firmware, service / request-response)

**Analog:** `program_mismatched_bytes` (`firestarter/src/proms/eprom.cpp:168-180`) — the P1-hold suspenders are **already in place at the per-buffer level**, and `eprom_internal_set_control_register` (`:319-326`) — the existing `CTRL_VPE_ENABLE → CTRL_VPP_P1_ENABLE` rewrite.

**Live P1-hold across the byte loop** (`:168-180`):
```cpp
static void program_mismatched_bytes(firestarter_handle_t* handle, const uint8_t* mismatch_bitmask) {
    rurp_register_t programming_bits = CTRL_VPE_ENABLE;
    handle->firestarter_set_control_register(handle, programming_bits, 1);   // P1 asserted (after rewrite)
    delay(10);
    for (uint32_t i = 0; i < handle->data_size; i++) {
        if (mismatch_bitmask[i / 8] & (1 << (i % 8))) {
            handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);  // CE pulse
        }
    }
    handle->firestarter_set_control_register(handle, programming_bits, 0);   // P1 cleared after loop
}
```

**Live VPE→P1 rewrite** (`:319-326`):
```cpp
void eprom_internal_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle)) {
        bit &= ~CTRL_VPE_ENABLE;
        bit |= CTRL_VPP_P1_ENABLE;     // 0x08 — held across program_mismatched_bytes
    }
    ep_set_control_register(handle, bit, state);
}
```

**Pattern:** the "hold P1 across the full program window" half of D-01 already exists at the per-buffer level; the residual is per-*byte*-CE-pulse coverage (do that in `memory.cpp`, above). Any gate that asserts a control bit here MUST honor the **D-04 alias** (`CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2 == 0x08`, `rurp_pinout.h:121,127`) — size-gate so it never reaches a 512K/1M A18 user. Model the gate on the v1.17 T-93-CANERASE protocol-keyed defense-in-depth and the `eprom_write_execute` protocol branch at `eprom.cpp:198-199` (`handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)`).

---

### `firestarter.h` ↔ `constants.py` — wire-field lockstep (LAST RESORT, only if D-03 escalates)

**Analog:** `page_size` (`firestarter/include/firestarter.h:97`) ↔ `JSON_KEY_PAGE_SIZE = "page-size"` (`firestarter_app/firestarter/constants.py:100`) — the v1.17 per-chip wire-field precedent.

```c
// firestarter.h:97
uint32_t page_size;          /* PGSZ-02/03: per-chip page size from DB (bytes; 0 = ... heuristic) */
```
```python
# constants.py:100
JSON_KEY_PAGE_SIZE = "page-size"
```
Existing wire-struct fields the fix should reuse FIRST (no new field): `static_high_mask` (`firestarter.h:81`), `protocol` (`:89`), `pins` (`:90`), `mem_size` (`:91`).

**Pattern:** D-03 forbids a new wire field unless the PGM-assert genuinely cannot be expressed via the new pinout's `static_high_mask` + a protocol/size firmware gate. If escalation is unavoidable: add the field to `firestarter.h`, mirror the JSON key in `constants.py`, plumb host emit, and pay the **full lockstep + parity cost** — `diff_db.py`, `check_dispatch.py`, and the constants-parity pytest all green. The `RURP_CONTROL_REGISTER_BITS` block (`constants.py:106-114`) mirroring `rurp_pinout.h` CTRL_* is the established sync discipline.

---

### `test_val_eprom.cpp` — corrected-path test + mandatory mismatch test (firmware, test / event-driven)

**Analog 1 (corrected-path recording assert):** `test_inv03_eprom_0x08_p1_as_vpp` (`firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:320-354`):
```cpp
void test_inv03_eprom_0x08_p1_as_vpp(void) {
    firestarter_handle_t h = make_handle(0x08, CMD_WRITE);
    h.pins = 32;
    h.bus_config.vpp_line = VPP_P1_32_DIP; /* 0x15 */
    h.data_size = 1;
    configure_memory(&h);
    if (h.firestarter_operation_init) h.firestarter_operation_init(&h);
    clear_bus_recording();                 // isolate execute-phase
    if (h.firestarter_operation_main) h.firestarter_operation_main(&h);
    TEST_ASSERT_TRUE_MESSAGE(
        recording_has_vpp_enable(CTRL_VPP_P1_ENABLE),
        "INV-03: 0x08 execute ... must record CTRL_VPP_P1_ENABLE ...");
}
```
Recording helpers live at `:131-148` (`recording_has_vpp_enable`, `recording_has_any_vpp_enable`); `clear_bus_recording()` / `bus_recording_count()` / `recorded_reg()` / `recorded_data()` are the assertion surface. **Pattern:** add a corrected-0x08-32-pin test (≤256K bus_config = the new `DIP32_27C020` shape) asserting the pin-31/PGM line was driven program-active in the recording (a CONTROL-register / line-22 bit assertion, NOT just `recording_has_vpp_enable`). Watch **Pitfall 4** — re-assign any scripted `firestarter_get_data` mock AFTER `configure_memory()` (it clobbers it at `memory.cpp:91`).

**Analog 2 (mandatory failure-case / mismatch fork — D-05, P89 CR-01 lesson):** WR-02a (`:615-657`):
```cpp
static uint8_t mock_mismatch_get_data(struct firestarter_handle*, uint32_t) {
    if (s_mismatch_mock_idx < (int)sizeof(s_mismatch_mock_bytes))
        return s_mismatch_mock_bytes[s_mismatch_mock_idx++];
    ...
}
void test_wr_02a_...(void) {
    s_mismatch_mock_bytes[0] = 0xDE; s_mismatch_mock_bytes[1] = 0xAD;  // forced mismatch
    h.firestarter_get_data = mock_mismatch_get_data;   // assigned AFTER configure_memory
    ...
    TEST_ASSERT_..._MESSAGE(RESPONSE_CODE_ERROR, ..., "... mismatch ... must yield ERROR");
}
```
**Pattern:** a 0x08-32-pin write where verify never matches must (a) still ERROR after the retry budget AND (b) the corrected-path test must assert pin-31/PGM was driven program-active in the *recording* — not just happy-path (the CR-01 lesson: a matching-id golden trace misses the correct-vs-incorrect fork). Register the new tests with `RUN_TEST(...)` in the runner (existing `RUN_TEST` calls in the same file).

**Pitfall 3:** `CTRL_VPP_VPE_DROP_ENABLE` (0x100) is invisible in the 8-bit trace — use the bit-level INV-01/INV-03 assertions for that bit, not the golden trace.

---

### `golden_eprom_0x08_write.inc` — re-bless ONLY if changed (firmware, test fixture / transform)

**Analog:** the file itself + the bless flow. Header documents the bless command and the low-byte-only caveat (`:1-13`):
```
// golden_eprom_0x08_write.inc — pinned (reg,data) trace for eprom 0x08 (EPROM_QUICK) write.
// Re-bless: pio test -e native -f "*test_val_eprom*" with -DGOLDEN_BLESS; redirect rows here.
// low-byte-only semantics (Pitfall 1): CTRL_VPP_VPE_DROP_ENABLE is 0x100 ... NOT captured ...
```
`#ifdef GOLDEN_BLESS print_trace_inc();` fires per golden test (`:514,536,558,595`).

**Pattern:** re-bless ONLY if the corrected 0x08 path legitimately changes the low-byte trace; cite the rationale in this `.inc` header comment. **Pitfall 2 (BLOCKING):** `-DGOLDEN_BLESS` re-pins ALL four traces — after blessing, `git diff` and **revert** any change to `golden_eprom_0x07_write.inc`, `golden_eprom_0x0B_write.inc`, `golden_eprom_chip_id.inc`. Only the 0x08 `.inc` may change (D-05 byte-identity tripwire). A5: the trace may not change at all if the fix is fully data-driven through bus-config bits the trace captures — check the actual diff before re-pinning.

---

## Shared Patterns

### Protocol+size-keyed defense-in-depth gate (the D-04 BLOCKING guard)
**Source model:** v1.17 T-93-CANERASE (firmware protocol gate + host mirror); `eprom_write_execute` protocol branch `eprom.cpp:198-199`; host structural scoping in `build_db.py:resolve_pinout_key`.
**Apply to:** every PGM/P1-hold surface (`memory.cpp`, `eprom.cpp`) AND the host pinout assignment (`build_db.py`).
**The alias being guarded** (`firestarter/include/rurp_pinout.h:121,127`):
```c
#define CTRL_VPP_P1_ENABLE_REV2            0x08
#define CTRL_ADDRESS_LINE_18_REV2          CTRL_VPP_P1_ENABLE_REV2   // SAME physical bit
```
**Gate predicate (concrete):**
- Host: only `proto_id == 0x08 && mem_size <= 262144` chips get `DIP32_27C020` (structural exclusion of 512K/1M A18 users).
- Firmware: `handle->protocol == 0x08 && handle->pins == 32 && handle->mem_size <= 262144` (A18 = bit 18 = mask 0x40000; "A18 unused" ⟺ mem_size ≤ 262144). Belt that catches a mis-built DB row.
**Anti-pattern (DO NOT):** gate on "0x08 + 32-pin" alone — 127 chips share 0x08/DIP32_STD across 128K/256K/512K/1M; the missing size term corrupts A18 on the 512K+ parts.

### SAFE-02 over-voltage invariant (must stay intact)
**Source:** `vpp_check_window` (`firestarter/src/proms/primitives.cpp:93`, HIGH→ERROR `:106`, FLAG_FORCE→WARN `:121`); host `chip_resolver.resolve_chip` guard.
**Apply to:** all firmware VPP touches in this phase.
**Rule (D-06):** over-voltage stays ERROR-blocked, no `FLAG_FORCE` relaxation in the path, no test-only escape hatch, AM27C020 flows through normal 0x08 dispatch. (Pitfall 6: low VPP is only a WARNING — a blind fix can look correct in the trace yet flip 0 bits on silicon; that residual is the Phase-99 gate, do NOT over-claim.)

### Host CI gate on py3.11 (SAFE-02)
**Source:** `firestarter_app/.github/workflows/ci.yml:29-32` (py3.11); `pyproject.toml:111` (mypy `python_version="3.9"`); `tools/check_dispatch.py`; `tools/diff_db.py` (baseline `tools/baseline/chip_database.baseline.json`).
**Apply to:** every host change.
**Commands:** `ruff check` + `ruff format --check` + `mypy` + `python tools/diff_db.py` + `python tools/check_dispatch.py`.
**Pitfall 5 (BLOCKING):** devcontainer default python is 3.12; CI is 3.11; **no 3.11 binary present** — provision a 3.11 venv (uv/pyenv) or treat local 3.12 as advisory and rely on CI. f-string backslash + ruff-pin differences are the traps.

### Constants/wire lockstep discipline (only if D-03 escalates)
**Source:** `firestarter_app/firestarter/constants.py:106-114` (`RURP_CONTROL_REGISTER_BITS`) mirrors `firestarter/include/rurp_pinout.h`; `page_size` (`firestarter.h:97`) ↔ `JSON_KEY_PAGE_SIZE` (`constants.py:100`).
**Apply to:** any new wire field.
**Rule:** change firmware header + Python constants together; constants-parity pytest must pass.

---

## No Analog Found

None. Every file in scope has a verified in-repo analog. The only **uncertainty** is design-level, not analog-level:

| Open question | Where it lands | Resolution path |
|---------------|----------------|-----------------|
| PGM polarity (program-active LOW vs `static_high_mask` HIGH-drive) — Q1 | `pinouts.json` vehicle choice + `memory.cpp` seam | Planner resolves against AM27C020.pdf; if HIGH≠VIL at socket, use a firmware clear/hold-low branch instead of `static-high-pins` |
| Static `static_high_mask` vs CE-timed assert — Q2 | `memory.cpp` vs new wire field | Try `static_high_mask` first; escalate to a minimal new wire field only if the assert must be timed to the CE pulse (D-03 last resort) |
| Claude's-discretion Phase-99 diagnostic hook | optional `eprom.cpp`/dev-reg surface | Add only if worth the surface; held-rail `dev reg -f` proxy is the cheap static-inspection route |

---

## Metadata

**Analog search scope:**
- `firestarter_app/firestarter/data/{pinouts,chip_database}.json`
- `firestarter_app/firestarter/{database.py,constants.py}`
- `firestarter_app/tools/{build_db.py,diff_db.py,check_dispatch.py}`
- `firestarter/src/proms/{memory.cpp,eprom.cpp}`
- `firestarter/include/{rurp_pinout.h,firestarter.h,memory_utils.h,rurp_shield.h}`
- `firestarter/test/native/avr/test_val_eprom/{test_val_eprom.cpp,golden_eprom_0x08_write.inc}`

**Files scanned:** 14 (all read direct this session; line numbers verified against live tip, not RESEARCH-cited).
**Verified deltas vs RESEARCH:** A1 (`build_db.py` can assign `DIP32_27C020` for ≤256K 0x08 at `resolve_pinout_key:291`) is **CONFIRMED — no override needed**. `eprom_internal_set_control_register` is at `:319-326` (RESEARCH said :320-326 — off by one on the comment line). WR-02a is at `:615-657` (RESEARCH said :621-703 spanning a/b/c). All other RESEARCH file:line citations confirmed accurate.
**Pattern extraction date:** 2026-06-30
