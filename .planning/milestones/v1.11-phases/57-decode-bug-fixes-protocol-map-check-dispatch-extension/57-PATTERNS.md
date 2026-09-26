# Phase 57: Decode Bug Fixes + PROTOCOL_MAP + check_dispatch Extension — Pattern Map

**Mapped:** 2026-06-08
**Files analyzed:** 2 (both modified in-place, no new files)
**Analogs found:** 2/2 (self-analog — each change copies the in-file idiom)

---

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---------------|------|-----------|----------------|---------------|
| `firestarter_app/tools/build_db.py` | utility (decode pipeline) | transform (XML → JSON) | Self — existing entries in same file | exact |
| `firestarter_app/tools/check_dispatch.py` | utility (safety guard) | batch (DB scan) | Self — existing guard blocks in same file | exact |

No new files are created. All pattern copying is intra-file: each edit must replicate the idiom established by the closest neighbor in the same file.

---

## Pattern Assignments

### `tools/build_db.py` — BUG-1: `VCC_VOLTAGES` dict (line 85)

**Current code (line 85):**
```python
VCC_VOLTAGES = {0x00: "5V", 0x01: "3.3V", 0x04: "5.5V", 0x05: "6.5V"}
```

**Analog for comment + multi-line dict style:** `VPP_VOLTAGES` dict (lines 57–74). Note the block comment above it (lines 46–56) cites the upstream C source with a verified commit hash. The `VPP_MV` parallel dict on lines 76–81 shows the same hex-key / string-value one-entry-per-line style.

**Comment style to copy (from lines 46–56 above `VPP_VOLTAGES`):**
```python
# Upstream infoic.xml caps VPP at 18V (0xF0), but a handful of antique
# Intel NMOS parts physically require higher programming voltages ...
```

**Target form for VCC_VOLTAGES:**
```python
# [VERIFIED: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]]
VCC_VOLTAGES = {
    0x00: "5V",
    0x01: "3.3V",
    0x02: "4V",    # BUG-1 fix: was missing
    0x03: "4.5V",  # BUG-1 fix: was missing
    0x04: "5.5V",
    0x05: "6.5V",
}
```

Key idioms: one-line dict → expand to multi-line; each entry on its own line; inline comment on new entries; citation comment with commit hash above the dict.

---

### `tools/build_db.py` — BUG-3: vcc/vdd label swap (lines 510–511)

**Current code (lines 510–511, inside `chip_entry` dict construction):**
```python
"vdd": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),
"vcc": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),
```

**Analog for inline comment style:** Line 508 (`"vpp"`) and line 509 (`"vpp_mv"`) show the same dict-entry format with no inline comment. The VPP byte access `voltages & 0xFF` is already documented implicitly. For the vcc/vdd fix, add inline bit-range comments matching the style seen in `PIN_MAP_PROTO_TO_PINOUT` comments (e.g., `# one-rom verified for ...` pattern on lines 157, 161, 162).

**Target form:**
```python
# [VERIFIED: minipro database.c#L921-L923 @ a8efaedc]
"vcc": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),    # bits 11-8
"vdd": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),   # bits 15-12
```

Key idiom: labels swap (vcc now on top, vdd below); inline bit-range annotation; citation comment on the line before.

---

### `tools/build_db.py` — BUG-2: `interpret_timing()` function (lines 268–284)

**Current code (lines 268–284):**
```python
def interpret_timing(raw_hex, protocol_id):
    try:
        val = int(raw_hex, 16)
    except:
        val = 0

    # EPROM Legacy (0x0B) is roughly 100us ticks
    if protocol_id == 0x0B:
        return f"{val * 100} us"
    # EPROM Standard (0x07) is roughly 100us ticks
    if protocol_id == 0x07:
        return f"{val * 100} us"
    # Modern (0x08) is often 1us
    if protocol_id == 0x08:
        return f"{val} us"

    return "Algorithm Controlled"
```

**Analog for `except Exception:` idiom:** Lines 289–294 (`main()` top) use `except Exception as e:` — that is the project's established form. The bare `except:` in `interpret_timing` is a ruff `BLE001` violation that must be changed to `except Exception:`.

**Analog for docstring style:** `resolve_pinout_key()` (lines 210–225) uses a triple-quoted docstring with no blank line before the first sentence. `interpret_timing` has no docstring currently; the fixed version adds a one-liner.

**Target form:**
```python
def interpret_timing(raw_hex, protocol_id):
    # [VERIFIED: minipro database.c#L866 @ a8efaedc]
    # Raw pulse_delay is microseconds for ALL protocols — no multiplier.
    try:
        val = int(raw_hex, 16)
    except Exception:
        val = 0

    if protocol_id in (0x07, 0x08, 0x0B):
        return f"{val} us"

    return "Algorithm Controlled"
```

Key idioms: `except Exception:` (not bare `except:`); citation comment at function top; collapse three separate `if` chains into one `in (...)` membership test; remove the `×100` factor and the wrong comments.

---

### `tools/build_db.py` — BUG-4: `PROTOCOL_MAP` dict (lines 25–44) and `KNOWN_PROTOCOLS` set (line 83)

**Current `PROTOCOL_MAP` (lines 25–44):**
```python
PROTOCOL_MAP = {
    0x05: "FLASH_AMD_STD",
    0x06: "FLASH_AMD_ALT",
    0x07: "EPROM_STD",
    0x08: "EPROM_QUICK",
    0x0B: "EPROM_LEGACY",
    0x0E: "SRAM_32PIN",
    0x0D: "EEPROM_POLL",
    0x10: "FLASH_INTEL",
    0x11: "FLASH_FWH",
    0x27: "SRAM_24PIN",
    0x28: "SRAM_STD",
    0x29: "SRAM_512K_1M",
    0x2A: "NVRAM_32PIN",
    0x2C: "NVRAM_TIMEKEEPER",
    0x2E: "NVRAM_512K",
    0x35: "FLASH_EEPROM_LIKE",
    0x39: "FLASH_INTEL_ALT",
    0x3C: "FLASH_4MB",
}
```

**Analog for comment style for excluded IDs:** The existing codebase uses inline `# comment` after each dict entry (see `_ALGO_MEM_TYPE` in `check_dispatch.py` lines 36–48: `0x05: 5,   # FLASH_AMD_STD     → TYPE_FLASH_TYPE_4`). For the PROTOCOL_MAP, excluded IDs become commented-out entries with rationale. The `PIN_MAP_TO_PINOUT` dict (lines 111–130) and `PIN_MAP_PROTO_TO_PINOUT` (lines 142–200) show the style: a block comment per logical group, then entries with inline `# description` comments.

**Target form for PROTOCOL_MAP (adds inline IC2_ALG_* citations and converts excluded entries to commented lines):**
```python
PROTOCOL_MAP = {
    0x05: "FLASH_AMD_STD",      # IC2_ALG_F29EE
    0x06: "FLASH_AMD_ALT",      # IC2_ALG_W29F32P
    0x07: "EPROM_STD",          # IC2_ALG_ROM28P_1
    0x08: "EPROM_QUICK",        # IC2_ALG_ROM32P
    0x0B: "EPROM_LEGACY",       # IC2_ALG_ROM24P_1
    0x0D: "EEPROM_POLL",        # IC2_ALG_EE28C32P
    0x0E: "SRAM_32PIN",         # IC2_ALG_RAM32_1
    0x10: "FLASH_INTEL",        # IC2_ALG_28F32P
    0x27: "SRAM_24PIN",         # IC2_ALG_ROM24P_2
    0x28: "SRAM_STD",           # IC2_ALG_ROM28P_2
    0x29: "SRAM_512K_1M",       # IC2_ALG_RAM32_2
    # Excluded IDs documented here for traceability:
    # 0x11: IC2_ALG_FWH  — LPC 4-wire serial bus + 3.3V; infeasible on RURP
    # 0x2A: IC2_ALG_GAL16  — GAL16V8 PLD (type=3); no DIP memory chips
    # 0x2C: IC2_ALG_GAL22  — GAL22V10 PLD (type=3); no DIP memory chips
    # 0x2E: IC2_ALG_PIC32X_2 — PIC32 MCU (type=2); no DIP memory chips
    # 0x35: IC2_ALG_ITE  — ITE EC MCU TQFP128 (type=2); no DIP memory chips
    # 0x39: NO IC2_ALG CONSTANT — phantom; INFOIC2PLUS-unreachable
    # 0x3C: NOT IN MINIPRO SOURCE — invented; remove entirely
}
```

**Current `KNOWN_PROTOCOLS` (line 83):**
```python
KNOWN_PROTOCOLS = {0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39}
```

**Target form:**
```python
# [VERIFIED: canonical IC2_ALG_* constants from database.h#L24-L77 @ a8efaedc]
# 0x35 (IC2_ALG_ITE) and 0x39 (phantom — no IC2_ALG constant) removed:
# neither produces chips in the INFOIC2PLUS DIP-24..32 filter.
KNOWN_PROTOCOLS = {0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29}
```

Key idioms: inline `# IC2_ALG_*` comment after every live entry; excluded IDs become `# 0xNN: ...` commented lines inside the dict block, not deleted — preserving traceability; citation comment block immediately above `KNOWN_PROTOCOLS`.

---

### `tools/build_db.py` — BUG-4 secondary: `_etype` re-derivation block (line 485)

**Current code (lines 481–489):**
```python
if proto_id in {0x0E, 0x27, 0x28, 0x29}:
    _etype = "SRAM"
elif proto_id in {0x07, 0x08, 0x0B}:
    _etype = "UV-EPROM"
elif proto_id in {0x05, 0x06, 0x0D, 0x10, 0x35, 0x39}:
    _etype = "Flash/EEPROM"
# else: leave _etype at the flags-based value (uncommon path —
# any new proto_id added to KNOWN_PROTOCOLS but not classified
# above falls back to whatever the flags-based block decided).
```

**Also line 473 (the comment block above the re-derivation):**
```python
#   - 0x0D / 0x05 / 0x06 / 0x10 / 0x35 / 0x39 → Flash/EEPROM family
```

**Target:** Remove `0x35` and `0x39` from line 485's set literal; update line 473's comment to remove the `0x35 / 0x39` references. Two-pass `_etype` structure (flags-based first pass, protocol-aware second pass) must survive intact — only the set contents change.

**Target form for line 485:**
```python
elif proto_id in {0x05, 0x06, 0x0D, 0x10}:
    _etype = "Flash/EEPROM"
```

**Target form for line 473 comment:**
```python
#   - 0x0D / 0x05 / 0x06 / 0x10 → Flash/EEPROM family
```

Key idiom: set literal with `{...}` curly braces (not a tuple); the `# else: leave _etype` trailing comment survives unchanged.

---

### `tools/check_dispatch.py` — Remove `0x35`/`0x39` from `_ALGO_MEM_TYPE` (lines 47–48)

**Current code (lines 35–49):**
```python
_ALGO_MEM_TYPE = {
    0x05: 5,   # FLASH_AMD_STD     → TYPE_FLASH_TYPE_4
    0x06: 3,   # FLASH_AMD_ALT     → TYPE_FLASH_TYPE_3
    0x07: 1,   # EPROM_STD         → TYPE_EPROM
    0x08: 1,   # EPROM_QUICK       → TYPE_EPROM
    0x0B: 1,   # EPROM_LEGACY      → TYPE_EPROM
    0x0D: 1,   # EEPROM_POLL       → TYPE_EPROM (firmware dispatches on protocol prefix)
    0x0E: 4,   # SRAM_32PIN        → TYPE_SRAM
    0x10: 1,   # FLASH_INTEL       → TYPE_EPROM (firmware dispatches on protocol prefix)
    0x27: 4,   # SRAM_24PIN        → TYPE_SRAM
    0x28: 4,   # SRAM_STD          → TYPE_SRAM
    0x29: 4,   # SRAM_512K_1M      → TYPE_SRAM
    0x35: 5,   # FLASH_EEPROM_LIKE → TYPE_FLASH_TYPE_4
    0x39: 5,   # FLASH_INTEL_ALT   → TYPE_FLASH_TYPE_4
}
```

**Target:** Remove lines 47–48 entirely (the `0x35` and `0x39` entries). No replacement comment needed since they are phantom IDs with no matching KNOWN_PROTOCOLS entry after the build_db.py fix.

**Also line 72 in `dispatch()`:**
```python
if protocol in (0x05, 0x35, 0x39):                     return "configure_flash4"
```

**Target form for line 72:**
```python
if protocol == 0x05:                                    return "configure_flash4"
```

Key idiom: the trailing-space alignment padding on the right-hand side of `dispatch()` return statements must be preserved. The existing style right-aligns all `return` keywords on the same column — adjust spacing to keep the column alignment after changing `(0x05, 0x35, 0x39)` to `0x05`.

---

### `tools/check_dispatch.py` — GATE-03: full-class VPP safety guard (new block)

**Analog for the error list + violation check pattern:** The existing `eeprom28c_in_eprom` guard (lines 57–65, 95–100, 119–130) is the direct template. Copy it verbatim, changing only the list name, the predicate, and the FAIL message.

**Existing eeprom28c_in_eprom pattern (lines 95–100 init + 119–130 check):**

Error list init (line 97, inside `main()` before the chip loop):
```python
eeprom28c_in_eprom = []
```

Violation check (lines 119–130, inside the chip loop after `sram_in_eprom` check):
```python
# WARNING-5 safety: DIP28_2764 + Flash/EEPROM chips must NOT route to
# configure_eprom (12V P1_VPP_ENABLE would hit A14 on the 5V part).
pinout = chip.get("pinout", "")
etype = chip.get("electrical", {}).get("type", "")
if (
    pinout == _28C_EEPROM_HAZARD_PINOUT
    and etype == "Flash/EEPROM"
    and handler == "configure_eprom"
):
    eeprom28c_in_eprom.append(
        f"{mfg}/{part} proto=0x{proto:02X} pinout={pinout}"
    )
```

Failure reporting (lines 165–174, inside the `if errors or sram_in_eprom or ...` block):
```python
if eeprom28c_in_eprom:
    print(
        f"FAIL: {len(eeprom28c_in_eprom)} DIP28_2764 Flash/EEPROM chips "
        f"route to configure_eprom (WARNING-5: 12V on A14 hazard):"
    )
    for e in eeprom28c_in_eprom[:20]:
        print(f"  {e}")
    if len(eeprom28c_in_eprom) > 20:
        print(f"  ... and {len(eeprom28c_in_eprom) - 20} more")
```

Exit gate check (line 148):
```python
if errors or sram_in_eprom or eeprom28c_in_eprom or wire_regressions:
```

PASS message (lines 185–190):
```python
print(
    f"PASS: all {total} chips have a valid dispatch path; "
    f"0 SRAM chips route to configure_eprom; "
    f"0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; "
    f"0 wire-key regressions"
)
```

**For the GATE-03 addition, add:**

1. `import json as _json` at module top if not already present (check: current imports are `json`, `os`, `sys`, `from firestarter.database import EpromDatabase` — `json` is already imported at line 17; `_json` alias is not needed, use `json` directly).

2. After `DB_FILE` constant (line 30), add:
```python
_PINOUT_FILE = os.path.join(_DATA_DIR, "pinouts.json")
```

3. Inside `main()`, after `with open(DB_FILE ...) as f: db_raw = json.load(f)` (line 87), add:
```python
with open(_PINOUT_FILE, encoding="utf-8") as _pf:
    _pinouts_raw = json.load(_pf)
# Dynamically build the set of pinouts that have a vpp-pin field.
# Using pinouts.json avoids hardcoding — Phase 58 may add new pinouts.
_vpp_pinouts = frozenset(
    k for k, v in _pinouts_raw.items() if "vpp-pin" in v.get("pins", {})
)
_5v_eeprom_algos = frozenset({0x05, 0x06, 0x0D})
```

4. After `eeprom28c_in_eprom = []` (line 97), add:
```python
vpp_eeprom_in_eprom = []
```

5. After the `eeprom28c_in_eprom.append(...)` block (after line 130), add:
```python
# GATE-03: full-class VPP-safety guard — any chip with a vpp-pin pinout AND
# a 5V-EEPROM-family algorithm (0x05/0x06/0x0D) must not route to configure_eprom.
if (
    pinout in _vpp_pinouts
    and proto in _5v_eeprom_algos
    and handler == "configure_eprom"
):
    vpp_eeprom_in_eprom.append(
        f"{mfg}/{part} proto=0x{proto:02X} pinout={pinout}"
    )
```

6. Add `vpp_eeprom_in_eprom` to the exit gate (line 148):
```python
if errors or sram_in_eprom or eeprom28c_in_eprom or vpp_eeprom_in_eprom or wire_regressions:
```

7. Add a `if vpp_eeprom_in_eprom:` reporting block inside the error section, matching the `eeprom28c_in_eprom` block verbatim but with the new list name and message:
```python
if vpp_eeprom_in_eprom:
    print(
        f"FAIL: {len(vpp_eeprom_in_eprom)} vpp-pin Flash/EEPROM chips "
        f"route to configure_eprom (GATE-03: VPP-class hazard):"
    )
    for e in vpp_eeprom_in_eprom[:20]:
        print(f"  {e}")
    if len(vpp_eeprom_in_eprom) > 20:
        print(f"  ... and {len(vpp_eeprom_in_eprom) - 20} more")
```

8. Update the PASS message to include the new counter line, matching the existing multi-line f-string style:
```python
print(
    f"PASS: all {total} chips have a valid dispatch path; "
    f"0 SRAM chips route to configure_eprom; "
    f"0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; "
    f"0 vpp-pin Flash/EEPROM chips route to configure_eprom; "
    f"0 wire-key regressions"
)
```

Note: `pinout` and `etype` are already extracted earlier in the loop for the `eeprom28c_in_eprom` check (lines 121–122), so the GATE-03 block does NOT re-extract them — it reuses the already-extracted `pinout` variable. The `etype` variable is NOT needed for GATE-03 (the predicate uses `proto in _5v_eeprom_algos`, not `etype`).

---

## Shared Patterns

### Exception Handling Idiom

**Source:** `tools/build_db.py` line 292 and throughout `main()`
**Apply to:** The `interpret_timing()` fix only

The project uses `except Exception:` (or `except Exception as e:`) uniformly — never a bare `except:`. The `interpret_timing` function currently has a bare `except:` at line 271 which is a ruff `BLE001` violation. Fix must change it to `except Exception:` as part of the BUG-2 edit.

```python
# CORRECT — matches project idiom:
except Exception:
    val = 0

# WRONG — ruff BLE001 violation (current code):
except:
    val = 0
```

### Lookup Table Comment / Citation Style

**Source:** `build_db.py` lines 46–56, 93–130, 133–200
**Apply to:** All edited lookup tables (`VCC_VOLTAGES`, `PROTOCOL_MAP`, `KNOWN_PROTOCOLS`)

All lookup tables in the file use one of two annotation patterns:
- Block comment above the dict/set citing the upstream source with commit hash: `# [VERIFIED: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]]`
- Inline trailing comment per entry: `0x05: "FLASH_AMD_STD",      # IC2_ALG_F29EE`

New and modified entries must follow both forms: citation comment above the dict, inline IC2_ALG_* comment per entry. This is what makes the PROTOCOL_MAP correction "self-documenting" without requiring a separate doc update.

### `frozenset` for Immutable Sets

**Source:** `build_db.py` lines 390–395 (SRAM protocol sets in `_etype` block use `{...}` set literals inline); `check_dispatch.py` line 54 uses `_SRAM_PROTOCOLS = {0x0E, 0x27, 0x28, 0x29}` (a plain set at module top)

The GATE-03 addition uses `frozenset(...)` for dynamically built sets (since they are constructed at runtime from pinouts.json, not literals) and `frozenset({...})` for small static protocol sets. This matches the RESEARCH.md recommendation. Module-top constants that are static use plain `{...}` set literals; runtime-built sets use `frozenset(...)`.

### ruff Format Alignment

**Source:** `check_dispatch.py` lines 69–74 (the `dispatch()` function body)
**Apply to:** Line 72 edit only

The `dispatch()` function uses trailing-space alignment to right-align all `return` keywords to column ~56. After narrowing `(0x05, 0x35, 0x39)` to `0x05`, the padding must be adjusted to maintain column alignment:

```python
# Current (line 72):
if protocol in (0x05, 0x35, 0x39):                     return "configure_flash4"
# Target:
if protocol == 0x05:                                    return "configure_flash4"
```

Count: `if protocol == 0x05:` is 20 chars; needs 36 spaces to reach column 56 before `return`.

---

## Test / Regression Analogs

### Snapshot Tests (syrupy)

**File:** `firestarter_app/tests/__snapshots__/test_characterization.ambr`
**Affected tests:** `test_list` (line 239), `test_search_w27` (line 261)
**Action:** After DB regeneration, run `cd firestarter_app && python -m pytest tests/test_characterization.py --snapshot-update` to refresh. Inspect the diff — only `pulse_duration` values should change for 0x07/0x0B chips; any other change is unexpected.

`test_info_known_chip` (line 246) pins a crash traceback and does NOT need snapshot update — the vpp-pin TypeError in `ic_layout.py` is not fixed in Phase 57.

### Unaffected Test

**File:** `firestarter_app/tests/test_eprom_info.py` lines 52–65 (`test_clean_config_for_export_strips_vdd`)
This test uses a hand-crafted dict with `"vdd"` and `"vcc"` keys — it does NOT call `build_db.py` or the DB parsing path. The BUG-3 vcc/vdd swap only changes which field gets which nibble value in the DB; the key names are not renamed. This test passes unchanged.

### check_dispatch.py Manual Invocation

**No automated test currently exists for check_dispatch.py** (only a comment reference in `test_audit_coverage_matrix.py`). The regression verification is manual:

```bash
cd firestarter_app && python tools/check_dispatch.py
```

Expected exit code 0 with PASS message that now includes the `vpp-pin Flash/EEPROM` counter line.

### Full Regression Suite

```bash
cd firestarter_app && python -m pytest tests/ --cov-fail-under=70
```

Expected: 470+ tests green (some snapshot tests may require update), coverage ≥ 70%.

---

## No Analog Found

Not applicable — all changes are surgical edits to two existing files. The RESEARCH.md provides verified correct target code for all five fixes. No invented patterns required.

---

## Metadata

**Analog search scope:** `firestarter_app/tools/` (build_db.py, check_dispatch.py read in full)
**Files scanned:** 2 source files + 1 test snapshot file + test_characterization.py + test_eprom_info.py + test_decoder.py
**Pattern extraction date:** 2026-06-08
**Key constraint:** `tools/build_db.py` and `tools/check_dispatch.py` are NOT in the mypy strict-check set — no type annotation changes required. `ruff check` + `ruff format --check` still apply.
