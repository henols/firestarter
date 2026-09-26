# Phase 58: Pinout Re-derivation + 24-pin EEPROM Unblock — Pattern Map

**Mapped:** 2026-06-08
**Files analyzed:** 5 new/modified files
**Analogs found:** 5 / 5

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/tools/build_db.py` | utility / pipeline | transform (XML → JSON) | itself (current body is the analog — rewrite target) | exact-self |
| `firestarter_app/firestarter/data/pinouts.json` | config/data | static data registry | `DIP24_6116` entry in same file (lines 94-103) | exact |
| `firestarter_app/tests/test_decoder.py` | test | unit + integration | `TestBuildDbDecodeCorrectness` class in same file (lines 691-817) | exact-self |
| `firestarter_app/tools/check_dispatch.py` | utility / gate | batch scan | itself (read-only; auto-covers DIP24_2816 via dynamic load) | exact-self |
| `.planning/phases/58-.../58-SR-1-CHECKLIST.md` | planning artifact | static doc | `.planning/v1.7-SHIELD-REVS.md` checklist pattern (two-layer D-10 precedent) | role-match |

---

## Pattern Assignments

### `firestarter_app/tools/build_db.py` — rewrite `resolve_pinout_key` + delete guess tables

**Analog:** The current `build_db.py` body itself. All excerpts below are the **live code that is being replaced or restructured**; the planner reads them to know exactly what to delete and what to rewrite.

---

#### Tables to DELETE entirely (D-02)

**`DIP28_VARIANT_MAP`** (lines 125–130):
```python
DIP28_VARIANT_MAP = {
    0x10: "DIP28_27512",  # 27C512 — VPP on pin 22 (OE pin), 19 address lines
    0x11: "DIP28_27256",  # 27C256 — VPP on pin 1, 15 address lines
    0x12: "DIP28_2764",  # 27C128
    0x13: "DIP28_2764",  # 27C64/2764A
}
```

**`PIN_MAP_TO_PINOUT`** (lines 149–186) — selected excerpt showing shape:
```python
PIN_MAP_TO_PINOUT = {
    # (pin_count, pm_idx): pinout_key  (None = use sub-discriminator)
    (28, 21,): "DIP28_2764",
    (28, 22): None,  # 27C128/256/512 family — variant_lo discriminates
    (28, 0): None,   # SRAM/FRAM (type=4) handled via override below
    (28, 20,): "DIP28_28C256",
    (28, 19,): "DIP28_28C64",
    (28, 18,): "DIP28_28C64",
    (32, 13): None,
    (32, 12): None,
    (32, 11,): None,
    (32, 10): None,
    (32, 9,): None,
    (32, 7): None,
    (32, 5): "DIP32_STD",
    (32, 0): None,
    (24, 23): None,  # 2716/2732 — variant_lo discriminates
    (24, 0): None,   # 24-pin SRAM (6116) — protocol_id discriminates
}
```

**`PIN_MAP_PROTO_TO_PINOUT`** (lines 198–256) — selected excerpt showing shape:
```python
PIN_MAP_PROTO_TO_PINOUT = {
    # (pin_count, pm_idx, proto_id): pinout_key
    (32, 7, 0x05): "DIP32_SST39SF040",
    (32, 7, 0x06): "DIP32_SST39SF040",
    # ... (58 total entries)
    (32, 0, 0x0E): "DIP32_SST39SF040",
    (32, 0, 0x29): "DIP32_SST39SF040",
    (24, 0, 0x27): "DIP24_6116",
}
```

---

#### Current `resolve_pinout_key` to REWRITE (lines 266–327)

**Current signature** (line 266):
```python
def resolve_pinout_key(pin_count, variant, flags_int, pm_idx=None, proto_id=None):
```

**New signature** (add `type_int` and `mem_size` — both available at the call site):
```python
def resolve_pinout_key(pin_count, variant, flags_int, pm_idx=None, proto_id=None, type_int=1, mem_size=0):
```

**Current body** (lines 282–327 — this is what gets replaced by the principled rule structure):
```python
    key = None

    # Tier 1: (pin_count, pm_idx, proto_id) — most specific
    if pm_idx is not None and proto_id is not None:
        key = PIN_MAP_PROTO_TO_PINOUT.get((pin_count, pm_idx, proto_id))
        if key is not None:
            if key in VALID_PINOUT_KEYS:
                return key
            print(
                f"WARN: PIN_MAP_PROTO_TO_PINOUT[{pin_count},{pm_idx},0x{proto_id:02X}] = '{key}' not in pinouts.json",
                file=sys.stderr,
            )

    # Tier 2: (pin_count, pm_idx)
    if pm_idx is not None and (pin_count, pm_idx) in PIN_MAP_TO_PINOUT:
        key = PIN_MAP_TO_PINOUT[(pin_count, pm_idx)]
        if key is not None:
            if key in VALID_PINOUT_KEYS:
                return key
            print(
                f"WARN: PIN_MAP_TO_PINOUT[{pin_count},{pm_idx}] = '{key}' not in pinouts.json",
                file=sys.stderr,
            )

    # Tier 3: variant-based fall-through
    if pin_count == 24:
        if (variant & 0xFF) == 1:
            key = "DIP24_2732"
        else:
            key = "DIP24_2716"  # Default to 2716
    elif pin_count == 28:
        key = DIP28_VARIANT_MAP.get(variant & 0xFF, "DIP28_2764")
    elif pin_count == 32:
        key = "DIP32_STD"
    else:
        key = None

    if key is not None and key not in VALID_PINOUT_KEYS:
        print(f"WARN: resolved pinout key '{key}' not in pinouts.json", file=sys.stderr)

    return key
```

**Replacement rule structure** (from RESEARCH.md §"Full Principled Rule Structure"):
```python
def resolve_pinout_key(pin_count, variant, flags_int, pm_idx=None, proto_id=None, type_int=1, mem_size=0):
    """Resolve the firestarter pinout key for a chip.

    Principled function: pinout key is a pure function of decoded minipro
    fields (pin_count, pm_idx, variant_lo, type_int, mem_size, proto_id).
    No per-IC names, no per-family lookup tables. pm_idx is the low byte
    of infoic.xml's pin_map attribute — it identifies the chip-family
    layout cluster. variant_lo (variant & 0xFF) sub-discriminates within
    a cluster.

    Returns a pinout key string (e.g., "DIP24_2816") or None if the chip
    cannot be classified; None triggers the D-06 fail-safe skip in main().

    [VERIFIED: exhaustive infoic.xml survey, all 24/28/32-pin DIP chips,
     MINIPRO_XML_URL @ commit a8efaedc — see RESEARCH.md §"Full Principled
     Rule Structure"]
    """
    variant_lo = variant & 0xFF
    key = None

    if pin_count == 24:
        if pm_idx == 23:
            if variant_lo == 0x01:
                key = "DIP24_2732"          # 4KB UV-EPROM
            elif variant_lo == 0x10:
                # 28C-family EEPROM (AT28C04/16, XL2804/2816, AM28C16A, etc.)
                # variant_lo=0x10 is the reliable 28C-EEPROM discriminator —
                # do NOT rely on flags&0x10 here; many 28C parts have flags=0x0000
                # [VERIFIED: infoic.xml — all (pm_idx=23, variant_lo=0x10) chips
                #  are the 28C family sharing the DIP24_2816 layout]
                key = "DIP24_2816"          # 5V EEPROM, rw-pin=21, no vpp-pin
            else:
                key = "DIP24_2716"          # default: 2KB UV-EPROM
        elif pm_idx == 0:
            key = "DIP24_6116"              # SRAM-class (type=4 or proto=0x27)
        else:
            key = None                      # D-06 fail-safe

    elif pin_count == 28:
        if pm_idx == 22:
            if variant_lo == 0x10:
                key = "DIP28_27512"         # VPP on pin 22 (OE/VPP shared)
            elif variant_lo == 0x11:
                key = "DIP28_27256"         # VPP on pin 1
            else:
                key = "DIP28_2764"          # 27C128/27C64 layout
        elif pm_idx == 21:
            key = "DIP28_2764"
        elif pm_idx == 20:
            key = "DIP28_28C256"
        elif pm_idx == 19:
            key = "DIP28_28C64"
        elif pm_idx == 18:
            key = "DIP28_28C64"
        elif pm_idx == 0:
            if type_int == 4 or proto_id in {0x27, 0x28, 0x29}:
                if mem_size <= 8192:
                    key = "DIP28_JEDEC_SRAM_8K"
                else:
                    key = "DIP28_28C256"
            elif proto_id == 0x05:
                key = "DIP28_28C256"        # AT29C256 5V flash
            else:
                key = None
        else:
            key = None                      # D-06 fail-safe

    elif pin_count == 32:
        if pm_idx == 0:
            key = "DIP32_SST39SF040"        # SRAM/NVRAM (type=4; WE=31, no VPP)
        elif pm_idx in {5, 7, 9, 10, 11, 12, 13}:
            if proto_id in {0x05, 0x06}:
                key = "DIP32_SST39SF040"
            elif proto_id == 0x0D:
                key = "DIP32_28C512_EEPROM"
            elif proto_id in {0x07, 0x08, 0x10}:
                key = "DIP32_STD"
            else:
                key = None
        else:
            key = None                      # D-06 fail-safe

    if key is not None and key not in VALID_PINOUT_KEYS:
        print(f"WARN: resolved pinout key '{key}' not in pinouts.json", file=sys.stderr)

    return key
```

---

#### Current call site to UPDATE (line 435–437)

```python
# Current:
pinout_key = resolve_pinout_key(
    pin_count, variant, flags, pm_idx=pm_idx, proto_id=proto_id
)

# Updated — add type_int and mem_size:
pinout_key = resolve_pinout_key(
    pin_count, variant, flags, pm_idx=pm_idx, proto_id=proto_id,
    type_int=type_int, mem_size=mem_size
)
```

Both `type_int` and `mem_size` are already decoded before line 435 (lines 372 and 389).

---

#### Safety-skip block to DELETE and REPLACE WITH RULE OUTCOME (lines 419–432)

```python
# DELETE THIS ENTIRE BLOCK:
if (
    pin_count == 24
    and proto_id in (0x07, 0x08, 0x0B)
    and (flags & 0x10)
):
    print(
        f"WARN: skipping {mfg_name}/{name} — 24-pin 5V EEPROM with "
        ...
    )
    continue
```

Replacement: The principled rule `resolve_pinout_key` returns `"DIP24_2816"` for all `(pm_idx=23, variant_lo=0x10)` chips. After `resolve_pinout_key`, add the algorithm-correction Rule 1 (see below).

**D-06 fail-safe** replaces the generic skip: after `resolve_pinout_key` returns `None`, emit a loud WARN and `continue` (no VPP-asserting dispatch). Pattern to copy from the existing `proto_id not in KNOWN_PROTOCOLS` skip at line 397–402:
```python
if proto_id not in KNOWN_PROTOCOLS:
    print(
        f"WARN: skipping {name} — unknown protocol_id 0x{proto_id:02X}",
        file=sys.stderr,
    )
    continue
```

New D-06 analog (same shape, different condition):
```python
if pinout_key is None:
    print(
        f"WARN: skipping {mfg_name}/{name} — unclassifiable pinout "
        f"(pin_count={pin_count}, pm_idx={pm_idx}, variant_lo=0x{variant & 0xFF:02X}); "
        f"add override via ~/.firestarter/database.json",
        file=sys.stderr,
    )
    continue
```

---

#### Algorithm-override blocks — REWRITE AS NAMED RULES (lines 452–555)

The current `_etype` derivation (Pass 1, lines 452–459) is PRESERVED exactly:
```python
# Pass 1: flags-based _etype (BEFORE algorithm overrides)
if type_int == 4:
    _etype = "SRAM"
elif proto_id in {0x0E, 0x27, 0x28, 0x29}:
    _etype = "SRAM"
elif flags & 0x10:
    _etype = "Flash/EEPROM"
else:
    _etype = "UV-EPROM"
```

**Rule 1: 28C EEPROM Algorithm Correction** — insert AFTER `resolve_pinout_key`, BEFORE `_etype` Pass 1. Replaces the deleted 24-pin safety-skip AND fixes the 10 dangerous chips with `flags=0x0000` that the skip missed:
```python
# Rule 1: 28C EEPROM family — force algorithm 0x0D
# Pinout DIP24_2816 means variant_lo=0x10 (confirmed 28C EEPROM family).
# This replaces the safety-skip at the old lines ~419-432 AND fixes the
# 10 chips that slipped through with flags=0x0000 (AM28C16A, etc.).
# [VERIFIED: RESEARCH.md §"Algorithm Override Rules" + §"Dangerous 24-pin EEPROMs"]
if pinout_key == "DIP24_2816":
    proto_id = 0x0D
    # _etype is set in Pass 1 below — will read "Flash/EEPROM" via proto=0x0D
    print(
        f"INFO: {mfg_name}/{name} algorithm 0x{<original_proto>:02X}->0x0D "
        f"(Rule 1: 28C-EEPROM family; configure_eeprom28c, no VPP)",
        file=sys.stderr,
    )
```

**Rule 2: WARNING-5 Safety Net** — current block (lines 479–489) is kept but the pinout predicate generalizes. Copy exact shape, updating comment to reference Rule 2:
```python
# Rule 2 — WARNING-5 generalized safety net (current lines 479-489, keep shape):
if (
    pinout_key in ("DIP28_2764", "DIP28_28C256")
    and proto_id == 0x07
    and _etype == "Flash/EEPROM"
):
    print(
        f"INFO: {mfg_name}/{name} algorithm override 0x07->0x0D "
        f"(WARNING-5: 5V EEPROM with non-EPROM pinout — route through configure_eeprom28c)",
        file=sys.stderr,
    )
    proto_id = 0x0D
```

**Rule 3: fm1608 SRAM override** — current block (lines 512–534) is kept with minimal changes (the `pinout_key` re-assignment inside the block already uses `mem_size` correctly). Only the comment needs updating to reference "Rule 3":
```python
# Rule 3: fm1608/SRAM — type=4 with EPROM proto (current lines 512-534, keep shape):
if type_int == 4 and proto_id in (0x07, 0x08, 0x0B):
    proto_id = 0x28
    if pin_count == 28:
        if mem_size <= 8192:
            pinout_key = "DIP28_JEDEC_SRAM_8K"
            size_label = "8K"
        else:
            pinout_key = "DIP28_28C256"
            size_label = f"{mem_size // 1024}K"
        print(
            f"INFO: {mfg_name}/{name} type=4 SRAM override ...",
            file=sys.stderr,
        )
```

**Pass 2: protocol-aware `_etype`** (lines 547–555) is PRESERVED exactly:
```python
# Pass 2: protocol-aware _etype AFTER all overrides
if proto_id in {0x0E, 0x27, 0x28, 0x29}:
    _etype = "SRAM"
elif proto_id in {0x07, 0x08, 0x0B}:
    _etype = "UV-EPROM"
elif proto_id in {0x05, 0x06, 0x0D, 0x10}:
    _etype = "Flash/EEPROM"
# else: leave _etype at the flags-based value
```

**Critical execution order** (planner must enforce):
1. `resolve_pinout_key(...)` call → sets `pinout_key`
2. D-06 fail-safe: if `pinout_key is None` → skip + `continue`
3. Pass 1 flags-based `_etype` (needs pre-override proto)
4. Rule 1 (DIP24_2816 → proto=0x0D) — note: store original proto before overwriting if logging it
5. Rule 2 (WARNING-5 — uses flags-based `_etype` from Pass 1)
6. Rule 3 (fm1608 — uses flags-based `_etype` and `type_int`)
7. Pass 2 protocol-aware `_etype`
8. `chip_entry` construction

---

### `firestarter_app/firestarter/data/pinouts.json` — add `DIP24_2816`

**Analog:** `DIP24_6116` entry (lines 94–103) — electrically identical layout, different name/comment.

**`DIP24_6116` (the electrical template)** — copy this structure, rename to `DIP24_2816`, change `name`/`comment`, change `rw-pin` to confirm pin 21 is WE (already identical), remove `vpp-pin` (absent in 6116 — that's exactly the safety property):
```json
"DIP24_6116": {
    "name": "JEDEC 24-pin 5V SRAM (6116/6264-style)",
    "comment": "Per piersfinlayson/one-rom (datasheet-verified): 6116 SRAM has 11 address pins (A0-A10) with A10=pin 19, CE=18, OE=20, WE=21. 5V single-supply, no programming voltage. Used by 6116-class 2KB SRAM chips. Covers the (pin_count=24, pm_idx=0, protocol_id=0x27) group + any other JEDEC 24-pin SRAM/FRAM with 6116-compatible pinout.",
    "pins": {
        "vcc-pin": [24], "gnd-pin": [12],
        "address-bus-pins": [8, 7, 6, 5, 4, 3, 2, 1, 23, 22, 19],
        "data-bus-pins": [9, 10, 11, 13, 14, 15, 16, 17],
        "ce-pin": [18], "oe-pin": [20], "rw-pin": [21]
    }
}
```

**New `DIP24_2816` entry** (from RESEARCH.md §"DIP24_2816 Pinout Definition"):
```json
"DIP24_2816": {
    "name": "JEDEC 24-pin 5V parallel EEPROM (AT28C16/AT28C04 family)",
    "comment": "AT28C16/AT28C04/28C16A-class 24-pin 5V single-supply parallel EEPROMs. Same physical layout as DIP24_6116 SRAM (WE=pin 21, OE=pin 20, CE=pin 18, VCC=pin 24, GND=pin 12). NO vpp-pin — configure_eeprom28c is 5V-only (SDP-disable + DQ7 page-write polling; VPP regulator is never asserted). Over-allocated to A0-A10 (11 address bits = AT28C16 maximum); AT28C04 has 9 address lines and firmware restricts driving via mem_size. Source: Atmel AT28C16 datasheet Table 1 (pin description). Pin 21=WE, NOT VPP — the DIP24_2716 (UV-EPROM) layout has VPP=pin 21; this layout does NOT.",
    "pins": {
        "vcc-pin": [24], "gnd-pin": [12],
        "address-bus-pins": [8, 7, 6, 5, 4, 3, 2, 1, 23, 22, 19],
        "data-bus-pins": [9, 10, 11, 13, 14, 15, 16, 17],
        "ce-pin": [18], "oe-pin": [20], "rw-pin": [21]
    }
}
```

**SR-1 critical invariant:** `DIP24_2816` must NOT contain a `"vpp-pin"` key. Compare with `DIP24_2716` (line 6 of pinouts.json) which DOES have `"vpp-pin": [21]` — that is the exact hazard the new entry avoids. Pin 21 appears as `"rw-pin"` (WE) in `DIP24_2816`, never as `"vpp-pin"`.

**Insertion point:** Add `DIP24_2816` immediately after `DIP24_6116` (after line 103) — keeps the DIP24 family entries grouped together.

---

### `firestarter_app/tests/test_decoder.py` — add `resolve_pinout_key` regression suite

**Analog:** `TestBuildDbDecodeCorrectness` class (lines 691–817) — same file, same import pattern (`from tools.build_db import <name>`), same `class TestXxx:` + `def test_<behavior>(self):` shape, no fixtures needed (pure unit tests).

**Import pattern to copy** (lines 703–706, 773–776 in existing class):
```python
from tools.build_db import VCC_VOLTAGES   # current pattern
from tools.build_db import interpret_timing  # current pattern

# New tests import:
from tools.build_db import resolve_pinout_key
from firestarter.data import pinouts  # or json.load(open(PINOUT_FILE))
```

**Class structure to copy** (lines 691–698):
```python
class TestBuildDbDecodeCorrectness:
    """Regression tests for the four decode bugs fixed in Phase 57 Plan 01.

    DEC-04 (BUG-1): VCC_VOLTAGES must include nibbles 0x02 (4V) and 0x03 (4.5V).
    ...
    """
```

New class follows the same shape:
```python
class TestResolvedPinoutKey:
    """Unit tests for the Phase 58 principled resolve_pinout_key rewrite.

    PIN-01: resolve_pinout_key returns the correct pinout key for each
    (pin_count, pm_idx, variant_lo) combination. Covers all documented
    rule branches from RESEARCH.md §"Full Principled Rule Structure".

    Each test passes hard-coded field values matching real infoic.xml chips,
    verifying the general rules without importing chip_database.json.
    """
```

**Individual test shape to copy** (lines 701–709):
```python
def test_vcc_voltages_includes_nibble_0x02_as_4v(self):
    """DEC-04 BUG-1: VCC_VOLTAGES[0x02] must equal '4V' (was missing)."""
    from tools.build_db import VCC_VOLTAGES

    assert VCC_VOLTAGES[0x02] == "4V", (
        f"VCC_VOLTAGES[0x02] expected '4V', got {VCC_VOLTAGES.get(0x02)!r}"
    )
```

**Minimum test cases for Wave 0 (from RESEARCH.md §"Wave 0 Gaps"):**

```python
class TestResolvedPinoutKey:
    # 24-pin branch tests:
    def test_24pin_pm23_variant_lo_01_returns_dip24_2732(self):
        # variant_lo=0x01, pm_idx=23 → DIP24_2732 (4KB UV-EPROM)
    def test_24pin_pm23_variant_lo_00_returns_dip24_2716(self):
        # variant_lo=0x00, pm_idx=23 → DIP24_2716 (2KB UV-EPROM)
    def test_24pin_pm23_variant_lo_10_returns_dip24_2816(self):
        # variant_lo=0x10, pm_idx=23 → DIP24_2816 (28C EEPROM family) ← KEY TEST
    def test_24pin_pm0_returns_dip24_6116(self):
        # pm_idx=0 → DIP24_6116 (SRAM)
    def test_24pin_unknown_pm_idx_returns_none(self):
        # pm_idx=99 → None (D-06 fail-safe)

    # 28-pin branch tests:
    def test_28pin_pm22_variant_lo_10_returns_dip28_27512(self):
    def test_28pin_pm22_variant_lo_11_returns_dip28_27256(self):
    def test_28pin_pm22_variant_lo_00_returns_dip28_2764(self):
    def test_28pin_pm20_returns_dip28_28c256(self):
    def test_28pin_pm19_returns_dip28_28c64(self):
    def test_28pin_pm18_returns_dip28_28c64(self):
    def test_28pin_pm21_returns_dip28_2764(self):

    # 32-pin branch tests:
    def test_32pin_pm5_proto_06_returns_dip32_sst39sf040(self):
    def test_32pin_pm9_proto_0d_returns_dip32_28c512_eeprom(self):
    def test_32pin_pm13_proto_07_returns_dip32_std(self):
    def test_32pin_pm0_returns_dip32_sst39sf040(self):


class TestGuessTablesDeleted:
    """Assert the three survey-built guess tables no longer exist (D-02)."""

    def test_pin_map_to_pinout_not_in_build_db(self):
        import tools.build_db as bdb
        assert not hasattr(bdb, "PIN_MAP_TO_PINOUT"), "PIN_MAP_TO_PINOUT must be deleted (D-02)"

    def test_pin_map_proto_to_pinout_not_in_build_db(self):
        import tools.build_db as bdb
        assert not hasattr(bdb, "PIN_MAP_PROTO_TO_PINOUT"), "PIN_MAP_PROTO_TO_PINOUT must be deleted (D-02)"

    def test_dip28_variant_map_not_in_build_db(self):
        import tools.build_db as bdb
        assert not hasattr(bdb, "DIP28_VARIANT_MAP"), "DIP28_VARIANT_MAP must be deleted (D-02)"


class TestWarning5Rule:
    """Assert WARNING-5 still fires as Rule 2 (PIN-02 regression guard)."""

    def test_warning5_fires_for_dip28_28c256_proto_07_flash_eeprom(self):
        # Simulate a chip that has pm_idx=20 → DIP28_28C256, flags=0x10 → Flash/EEPROM,
        # proto_id=0x07. After WARNING-5 the algorithm must be 0x0D.
        # This tests Rule 2 directly.


class TestDIP24_2816Pinout:
    """Assert DIP24_2816 is in pinouts.json with correct SR-1-safe pin assignments."""

    def test_dip24_2816_present_in_pinouts_json(self):
    def test_dip24_2816_has_no_vpp_pin_field(self):   # ← CRITICAL SR-1 gate
    def test_dip24_2816_rw_pin_is_21(self):
    def test_dip24_2816_ce_pin_is_18(self):
    def test_dip24_2816_oe_pin_is_20(self):
    def test_dip24_2816_vcc_is_24_gnd_is_12(self):
```

**Integration test class** (loads the regenerated `chip_database.json`):
```python
class TestDangerous24pinEEPROMFixed:
    """Integration tests: assert the 10 dangerous 24-pin EEPROMs + 9 blocked
    chips are correctly re-classified in the regenerated chip_database.json."""

    def _load_db(self):
        import json, os
        db_path = os.path.join(
            os.path.dirname(__file__), "..", "firestarter", "data", "chip_database.json"
        )
        with open(db_path) as f:
            return json.load(f)

    def test_am28c16a_has_algo_0x0D_and_dip24_2816(self):
        db = self._load_db()
        # find AMD/AM28C16A ...
        # assert chip["programming"]["algorithm"] == 0x0D
        # assert chip["pinout"] == "DIP24_2816"

    def test_at28c16_has_algo_0x0D_and_dip24_2816(self):
        # same shape for ATMEL/AT28C16
```

**`EpromDatabase(skip_local_override=True)` pattern** (from `test_eprom_database.py` lines 35–36) — use this instead of raw JSON load when testing via the DB API:
```python
from firestarter.database import EpromDatabase

db = EpromDatabase(skip_local_override=True)
eprom = db.get_eprom("AT28C16")
assert eprom is not None
assert eprom["algorithm"] == 0x0D   # after Phase 58 regen
```

---

### `firestarter_app/tools/check_dispatch.py` — READ-ONLY (auto-covers DIP24_2816)

**No changes required.** Excerpting the GATE-03 predicate (lines 140–143) to confirm auto-coverage:

```python
# GATE-03: full-class VPP-safety guard — any chip whose electrical type
# is Flash/EEPROM (a 5V part) must NOT route to configure_eprom, which
# asserts 12V P1_VPP_ENABLE. This is pinout-agnostic (so it auto-covers
# any pinout Phase 58 adds) and is a true superset of the WARNING-5
# DIP28_2764 check above.
if etype == "Flash/EEPROM" and handler == "configure_eprom":
    vpp_eeprom_in_eprom.append(
        f"{mfg}/{part} proto=0x{proto:02X} pinout={pinout}"
    )
```

After Phase 58:
- All 9 previously-blocked chips → `etype="Flash/EEPROM"`, `algorithm=0x0D` → `dispatch(0x0D, ...)` → `"configure_eeprom28c"` → GATE-03 does not fire.
- All 10 previously-dangerous chips → `etype="Flash/EEPROM"`, `algorithm=0x0D` → same → GATE-03 does not fire.
- GATE-03 fires only if any chip slips through with `etype="Flash/EEPROM"` AND reaches `configure_eprom`. 0 violations = correctness proof for PIN-02.

The `dispatch()` function (lines 64–84) also needs no change — `0x0D` already maps to `"configure_eeprom28c"` at line 69.

The DB load pattern (lines 89–96) already uses `json.load(f)` on `DB_FILE` — no pinouts.json key needed; the GATE-03 check reads `chip.get("pinout", "")` and `chip.get("electrical", {}).get("type", "")` directly from the regenerated DB.

---

## Shared Patterns

### Pattern: `print(..., file=sys.stderr)` for build-time diagnostics

**Source:** `build_db.py` lines 399–402 (proto skip), 425–431 (safety skip), 484–488 (WARNING-5 INFO), 526–531 (fm1608 INFO)
**Apply to:** All new diagnostic messages in the rewritten `resolve_pinout_key` caller loop and the D-06 fail-safe
```python
# WARN/INFO/ERROR — consistent pattern across build_db.py:
print(
    f"WARN: skipping {mfg_name}/{name} — <reason>",
    file=sys.stderr,
)
print(
    f"INFO: {mfg_name}/{name} <override description>",
    file=sys.stderr,
)
```

### Pattern: `from tools.build_db import <name>` — test import convention

**Source:** `test_decoder.py` lines 703, 716, 773 (existing `TestBuildDbDecodeCorrectness`)
**Apply to:** All new unit test methods in `TestResolvedPinoutKey`, `TestGuessTablesDeleted`, `TestWarning5Rule`, `TestDIP24_2816Pinout`

Import is done INSIDE each test method body (not at module top), matching the established pattern in the existing `TestBuildDbDecodeCorrectness` class.

### Pattern: `EpromDatabase(skip_local_override=True)` — integration test DB access

**Source:** `test_eprom_database.py` lines 35, 44, 50, 56, 62, 68 (every data-asserting test)
**Apply to:** `TestDangerous24pinEEPROMFixed` integration tests that verify specific chip entries by name

The mandatory pattern per the `test_eprom_database.py` docstring: "every data-asserting test constructs `EpromDatabase(skip_local_override=True)`. Bare `EpromDatabase()` in tests that assert specific chip data is forbidden."

### Pattern: `VALID_PINOUT_KEYS` validation sentinel

**Source:** `build_db.py` lines 258–259 (module-level, loaded once at import)
```python
with open(PINOUT_FILE) as _f:
    VALID_PINOUT_KEYS = set(json.load(_f).keys())
```
**Apply to:** The rewritten `resolve_pinout_key` tail (line 324–326 in current code) — preserve this validation guard unchanged. After adding `DIP24_2816` to `pinouts.json`, `VALID_PINOUT_KEYS` will contain it automatically; no code change to the guard needed.

### Pattern: Two-pass `_etype` — MANDATORY execution order

**Source:** `build_db.py` lines 452–459 (Pass 1) and 547–555 (Pass 2), with algorithm overrides between them.
**Apply to:** The entire algorithm-override section in `main()`. The two-pass pattern is a load-bearing invariant (RESEARCH.md Pitfall 2); collapsing it into one pass breaks WARNING-5 and fm1608.

---

## No Analog Found

All files have close analogs in the codebase. The only new-from-scratch artifact is the SR-1 planning document:

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `.planning/phases/58-.../58-SR-1-CHECKLIST.md` | planning artifact | static doc | No existing per-phase SR checklist in this repo; the `.planning/v1.7-SHIELD-REVS.md` two-layer pattern (meta + sub-repo) is the closest structural precedent. Planner authors this as a new markdown checklist keyed on the SR-1 items from RESEARCH.md §"SR-1 Checklist (pre-verified for DIP24_2816)". |
| `firestarter_app/doc/pinout-safety-review.md` | sub-repo operator doc | static doc | No existing `doc/pinout-safety-review.md`; follows the shield-revisions two-layer pattern (D-10). Planner creates it as the GitHub-visible operator-facing subset of the planning artifact. |

---

## Metadata

**Analog search scope:** `firestarter_app/tools/`, `firestarter_app/tests/`, `firestarter_app/firestarter/data/`
**Files scanned:** 6 (build_db.py, check_dispatch.py, pinouts.json, test_decoder.py, test_eprom_database.py, conftest.py)
**Pattern extraction date:** 2026-06-08
