# Phase 57: Decode Bug Fixes + PROTOCOL_MAP + check_dispatch Extension — Research

**Researched:** 2026-06-08
**Domain:** Python decode pipeline (`tools/build_db.py`, `tools/check_dispatch.py`)
**Confidence:** HIGH

---

## Summary

Phase 57 is a pure-software decode-correctness phase. The authoritative semantics were established in Phase 56 (`infoic-field-dictionary.md`, `protocol-id.md`, `protocol-flags.md`). This phase's job is to make `build_db.py` and `check_dispatch.py` match those documented semantics — no new research is required, only precise mechanical code edits grounded in the Phase 56 dictionary.

Four confirmed decode bugs exist in `build_db.py`. Three affect the generated `chip_database.json` values for all 734 chips; one affects the symbolic names in an in-process map. A fifth item extends `check_dispatch.py`'s VPP-safety guard from a single pinout to a full-class assertion. All five items are locatable to exact line ranges; each fix is a one-to-five-line edit.

The test suite has 470 green tests after Phase 56. This phase will invalidate the `test_info_known_chip` snapshot (which pins the current broken crash output) and the `test_list` snapshot (which pins current pulse_duration values). The planner must include a snapshot-update task. The `check_dispatch.py` extension adds a new assertion but produces 0 violations against the current DB, so no existing tests break on the safety-guard side.

**Primary recommendation:** Fix the four `build_db.py` bugs in the exact order: (1) `VCC_VOLTAGES` table — add two missing nibbles, (2) vcc/vdd labels — swap the two extraction lines, (3) `interpret_timing` — remove the ×100 branch for 0x07/0x0B, (4) `PROTOCOL_MAP` + `KNOWN_PROTOCOLS` cleanup. Then extend `check_dispatch.py`. Then regenerate `chip_database.json` and update snapshots.

---

## Project Constraints (from CLAUDE.md)

- `chip_database.json` — do NOT edit by hand; regenerate from `build_db.py`
- `ruff check` + `ruff format --check` + `mypy` (strict on 8 named modules) + `pytest --cov-fail-under=70` — all enforced by CI and pre-commit
- mypy strict applies to: `main.py`, `cli_handlers.py`, `chip_resolver.py`, `frame_parser.py`, `codec.py`, `address_parser.py`, `exceptions.py`, `serial_comm.py` — `tools/build_db.py` and `tools/check_dispatch.py` are NOT in the strict-mypy set
- `build_db.py` fetches live from upstream master by operator decision (D-01 in Phase 56 CONTEXT.md) — the `MINIPRO_XML_URL` constant is not changed in Phase 57
- Phase 57 is HOST-ONLY; firmware sub-repo untouched
- WARNING-5 safety override and fm1608 override in `build_db.py` must be preserved intact; `_etype` two-pass pattern must survive

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Decode `voltages` field (VCC/VDD nibbles) | `tools/build_db.py` | — | Only the decoder reads raw XML nibbles |
| Decode `pulse_delay` field | `tools/build_db.py` | — | `interpret_timing()` owns this conversion |
| Symbolic protocol naming | `tools/build_db.py` | `tools/check_dispatch.py` | `PROTOCOL_MAP` is build-time; `check_dispatch.py` must stay in sync |
| VPP-safety dispatch guard | `tools/check_dispatch.py` | — | Post-hoc assertion over the already-generated DB |
| `chip_database.json` (output) | `tools/build_db.py` | — | Generated artifact; consumers read it, never write it |

---

## Standard Stack

No new packages. This phase edits existing Python source files only.

| Tool | Version | Purpose | Status |
|------|---------|---------|--------|
| Python | ≥3.9 (CI target) | Build tool runtime | Already installed |
| ruff | pinned in pyproject.toml | Lint + format gate | Already enforced |
| pytest | pinned in pyproject.toml | Test runner | Already enforced |
| syrupy | pinned in pyproject.toml | Snapshot assertions | Snapshot updates needed |

---

## Package Legitimacy Audit

No new packages installed in this phase. Section not applicable.

---

## Architecture Patterns

### Data Flow for This Phase

```
tools/infoic.xml (upstream fetch)
         |
         v
  build_db.py::main()
         |
         +-- DIP filter (package_details, type) -- unchanged
         |
         +-- VCC_VOLTAGES lookup (BUG-1 FIX: add 0x02, 0x03)
         |
         +-- vcc/vdd field assignment (BUG-3 FIX: swap >>8 / >>12)
         |
         +-- interpret_timing() (BUG-2 FIX: remove ×100 branch)
         |
         +-- PROTOCOL_MAP lookup (BUG-4 FIX: canonical IC2_ALG_* names)
         |
         +-- KNOWN_PROTOCOLS gate (BUG-4 FIX: remove 0x35, 0x39)
         |
         +-- WARNING-5 override (UNCHANGED)
         |
         +-- fm1608 override (UNCHANGED)
         |
         v
  chip_database.json (regenerated)
         |
         v
  check_dispatch.py::main()
         |
         +-- existing: SRAM-protocol → configure_eprom guard (UNCHANGED)
         |
         +-- existing: DIP28_2764 + Flash/EEPROM → configure_eprom guard (UNCHANGED)
         |
         +-- NEW: any vpp-pin pinout + {0x05,0x06,0x0D} → configure_eprom guard
         |
         v
  exit 0 (0 violations)
```

### Component Responsibilities

| File | Lines | Purpose |
|------|-------|---------|
| `tools/build_db.py` | 85 | `VCC_VOLTAGES` dict — add missing nibbles |
| `tools/build_db.py` | 83 | `KNOWN_PROTOCOLS` set — remove 0x35, 0x39 |
| `tools/build_db.py` | 25–44 | `PROTOCOL_MAP` — fix wrong names, remove 0x3C |
| `tools/build_db.py` | 268–284 | `interpret_timing()` — remove ×100 branch |
| `tools/build_db.py` | 510–511 | vcc/vdd chip_entry assignment — swap extractions |
| `tools/build_db.py` | 473, 485 | Post-override `_etype` re-derivation — remove 0x35/0x39 |
| `tools/check_dispatch.py` | 47–48 | `_ALGO_MEM_TYPE` — remove/comment 0x35/0x39 entries |
| `tools/check_dispatch.py` | 64–65 | `_28C_EEPROM_HAZARD_PINOUT` constant — generalize to set |
| `tools/check_dispatch.py` | 72 | `dispatch()` — remove 0x35/0x39 from configure_flash4 |
| `tools/check_dispatch.py` | 95–100 | Error lists — add `vpp_eeprom_in_eprom` list |
| `tools/check_dispatch.py` | 119–130 | Violation check — add full-class VPP guard |

---

## Per-Success-Criterion Fix Map

### SC-1: DEC-03 — Remove `interpret_timing` ×100 multiplier

**Location:** `tools/build_db.py` lines 268–284, function `interpret_timing(raw_hex, protocol_id)`

**Current code:**
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

**Correct behavior per infoic-field-dictionary.md (BUG-2):** Raw `pulse_delay` value is microseconds for ALL protocols with no multiplication. Minipro source `database.c#L866` loads the value directly with no post-processing.

**Fix:** Remove the two `val * 100` branches for `0x0B` and `0x07`. Both should return `f"{val} us"`. The `0x08` branch is already correct. The comment about "100us ticks" is wrong and must be removed.

**Resulting correct function:**
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

**Impact:** 252 chips change `pulse_duration` in the regenerated DB (all 0x07 and 0x0B chips with non-zero `pulse_delay`). W27C512 changes from `"10000 us"` to `"100 us"`.

**How to verify:** After regenerating DB: `python -c "import json; db=json.load(open('firestarter/data/chip_database.json')); [print(mfg, c['part_number'], c['programming']['pulse_duration']) for mfg,cs in db.items() for c in cs if 'W27C512' in c.get('part_number','')]"` — expect `100 us`.

**Safe-removal scope:** Only 0x07 and 0x0B are affected. 0x08 already returns `f"{val} us"` and is unchanged. All other protocols return `"Algorithm Controlled"` and are unchanged.

---

### SC-2 + SC-3: DEC-04 — VCC nibbles + vcc/vdd label swap

#### BUG-1: Missing VCC nibbles

**Location:** `tools/build_db.py` line 85

**Current code:**
```python
VCC_VOLTAGES = {0x00: "5V", 0x01: "3.3V", 0x04: "5.5V", 0x05: "6.5V"}
```

**Correct behavior per infoic-field-dictionary.md (BUG-1):** `tl866ii_vcc_voltages[]` at `database.c#L130–L135` defines 6 entries. Missing: `0x02 → "4V"` and `0x03 → "4.5V"`. Chips with nibble `0x02` or `0x03` silently fall back to the `"5V"` default.

**Fix:**
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

**Impact:** Any chip in infoic.xml with VCC nibble `0x02` or `0x03` will now decode correctly instead of silently showing `"5V"`. The AT28C256/AT28C64-class chips mentioned in the success criterion are the expected beneficiaries — need to verify by regenerating and diffing against baseline.

#### BUG-3: vcc/vdd label swap

**Location:** `tools/build_db.py` lines 510–511 (inside `chip_entry` dict construction)

**Current code:**
```python
"vdd": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),
"vcc": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),
```

**Correct behavior per infoic-field-dictionary.md (BUG-3):** Per `database.c#L921–L923`:
- `vcc = (voltages >> 8) & 0x0F` — bits 11-8
- `vdd = (voltages >> 12) & 0x0F` — bits 15-12

The current code has the labels swapped: `vdd` reads bits 11-8 (the VCC position) and `vcc` reads bits 15-12 (the VDD position).

**Fix:**
```python
# [VERIFIED: minipro database.c#L921-L923 @ a8efaedc]
"vcc": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),   # bits 11-8
"vdd": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),  # bits 15-12
```

**Impact:** All 734 chips will have their `vcc`/`vdd` labels corrected. This is a systematic swap — any chip where VCC ≠ VDD will have those two values transposed in the output. Most chips have VCC=VDD=5V so no visible change; chips with differing VCC/VDD (3.3V logic / 5V programming, for example) will show the correct assignment.

**Note:** The `VCC_VOLTAGES` dict is used for BOTH `vcc` and `vdd` (there is no separate `VDD_VOLTAGES`). The fix applies to both lines simultaneously since the nibble→voltage table is the same. [VERIFIED: database.c#L921-L923 uses the same `tl866ii_vcc_voltages[]` for both].

---

### SC-4: DEC-05 — PROTOCOL_MAP canonical IC2_ALG_* names

**Location:** `tools/build_db.py` lines 25–44 (`PROTOCOL_MAP` dict) and line 83 (`KNOWN_PROTOCOLS` set)

**Current PROTOCOL_MAP entries to fix:**

| Key | Current (wrong) | Correct | Reason |
|-----|-----------------|---------|--------|
| `0x11` | `"FLASH_FWH"` | Remove or comment as excluded | `IC2_ALG_FWH` — LPC serial bus, infeasible on RURP |
| `0x2A` | `"NVRAM_32PIN"` | `"IC2_ALG_GAL16"` + exclusion comment | GAL16V8 PLD algorithm, not memory |
| `0x2C` | `"NVRAM_TIMEKEEPER"` | `"IC2_ALG_GAL22"` + exclusion comment | GAL22V10 PLD algorithm, not memory |
| `0x2E` | `"NVRAM_512K"` | `"IC2_ALG_PIC32X_2"` + exclusion comment | PIC32 MCU algorithm, not memory |
| `0x35` | `"FLASH_EEPROM_LIKE"` | `"IC2_ALG_ITE"` + exclusion comment | ITE IT8xxx EC MCU, TQFP128 — not DIP memory |
| `0x39` | `"FLASH_INTEL_ALT"` | Remove entirely | No IC2_ALG constant in database.h — phantom |
| `0x3C` | `"FLASH_4MB"` | Remove entirely | Not in minipro source at all — invented |

**`KNOWN_PROTOCOLS` set — current:**
```python
KNOWN_PROTOCOLS = {0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39}
```

**Fix:** Remove `0x35` and `0x39` from `KNOWN_PROTOCOLS`. These IDs never appear in the INFOIC2PLUS DIP 24–32 filter scope — no chip currently in the DB uses them (verified: `algos_in_db` does not include 0x35 or 0x39 after the db was last regenerated). Removing them from `KNOWN_PROTOCOLS` changes which `protocol_id` values trigger the "unknown protocol" warning during future regenerations; currently they silently pass through to produce no chips anyway.

**`KNOWN_PROTOCOLS` fixed:**
```python
# [VERIFIED: canonical IC2_ALG_* constants from database.h#L24-L77 @ a8efaedc]
# 0x35 (IC2_ALG_ITE) and 0x39 (phantom — no IC2_ALG constant) removed:
# neither produces chips in the INFOIC2PLUS DIP-24..32 filter.
KNOWN_PROTOCOLS = {0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29}
```

**Secondary fix — post-override `_etype` re-derivation:** Lines 473 and 485 reference `0x35` and `0x39` in the protocol-aware `_etype` re-derivation. After removing them from `KNOWN_PROTOCOLS`, they will never reach that block (chips with unknown proto_id are skipped earlier at line 340). Remove `0x35` and `0x39` from the set on line 485:

```python
# Before (line 485):
elif proto_id in {0x05, 0x06, 0x0D, 0x10, 0x35, 0x39}:
    _etype = "Flash/EEPROM"

# After:
elif proto_id in {0x05, 0x06, 0x0D, 0x10}:
    _etype = "Flash/EEPROM"
```

Also remove the corresponding comment on line 473 that mentions `0x35`/`0x39`.

**Secondary fix — `check_dispatch.py` _ALGO_MEM_TYPE:** Lines 47–48 map `0x35` and `0x39` to mem_type 5. After build_db.py no longer emits chips with these algorithms, check_dispatch.py should remove (or comment) these entries to stay in sync. The `dispatch()` function on line 72 also routes `0x35`/`0x39` to `configure_flash4` — this becomes dead code.

**Impact on DB:** No chip currently in the DB uses `0x35` or `0x39` algorithms (verified against current `chip_database.json`). Removing them from `KNOWN_PROTOCOLS` produces no change in the regenerated DB chipset. The change is semantic correctness of the map and the guard.

---

### SC-5: GATE-03 — check_dispatch.py full-class VPP-safety guard

**Location:** `tools/check_dispatch.py` — new assertion block added to `main()`

**Current behavior:** Lines 119–130 assert that `pinout == "DIP28_2764"` AND `etype == "Flash/EEPROM"` chips do not route to `configure_eprom`. This is the WARNING-5 guard for a single pinout.

**GATE-03 requirement:** Assert that no chip with a `vpp-pin` pinout AND a 5V-EEPROM-family handler (`algorithm in {0x05, 0x06, 0x0D}`) routes to `configure_eprom`. This covers the full set of pinouts that have a `vpp-pin` field.

**Pinouts with `vpp-pin` in `pinouts.json` (verified):**
- `DIP24_2716` — vpp-pin: [21]
- `DIP24_2732` — vpp-pin: [20] (shared with oe-pin)
- `DIP28_2764` — vpp-pin: [1]
- `DIP28_27256` — vpp-pin: [1]
- `DIP28_27512` — vpp-pin: [22] (shared with oe-pin)
- `DIP32_STD` — vpp-pin: [1]

**5V EEPROM family handlers:** `{0x05, 0x06, 0x0D}` — these are `configure_flash4`, `configure_flash3`, and `configure_eeprom28c` respectively. None of these assert VPP. But if a chip with these algorithms happened to be on a vpp-pin pinout AND there was a dispatch path to `configure_eprom`, that would be a hardware damage path.

**Current DB state:** Only 2 chips have a vpp-pin pinout + 5V EEPROM algo — AT29C256 and AT29LV256, both with `algorithm=0x05` (AMD flash) on `DIP28_2764`. Both dispatch to `configure_flash4` (not `configure_eprom`). So the new assertion will immediately produce 0 violations.

**Implementation approach:** Load `pinouts.json` inside `check_dispatch.py` to dynamically determine which pinouts have a `vpp-pin` field. This avoids hardcoding the set and ensures the guard auto-updates if a new vpp-pin pinout is added in Phase 58.

```python
# Near top of check_dispatch.py, after DB_FILE definition:
import json as _json
_PINOUT_FILE = os.path.join(_DATA_DIR, "pinouts.json")

# Inside main(), before the chip loop:
with open(_PINOUT_FILE, encoding="utf-8") as _pf:
    _pinouts_raw = _json.load(_pf)
_VPP_PINOUTS = frozenset(
    k for k, v in _pinouts_raw.items() if "vpp-pin" in v.get("pins", {})
)
_5V_EEPROM_ALGOS = frozenset({0x05, 0x06, 0x0D})

# New error list alongside sram_in_eprom, eeprom28c_in_eprom:
vpp_eeprom_in_eprom = []

# Inside the chip loop, after the existing eeprom28c_in_eprom check:
if (
    pinout in _VPP_PINOUTS
    and proto in _5V_EEPROM_ALGOS
    and handler == "configure_eprom"
):
    vpp_eeprom_in_eprom.append(
        f"{mfg}/{part} proto=0x{proto:02X} pinout={pinout}"
    )
```

**Why use pinouts.json for the set:** Phase 58 will add `DIP24_6116` as a 24-pin pinout, and it does NOT have a `vpp-pin` (it's a 5V SRAM pinout). The dynamic load ensures no maintenance burden when new pinouts are added — only pinouts that actually have `vpp-pin` in their definition are checked.

**Exit code:** The new `vpp_eeprom_in_eprom` list is included in the `if errors or sram_in_eprom or eeprom28c_in_eprom or wire_regressions` check to trigger `sys.exit(1)` on violations.

**Current violation count against the live DB:** 0 (verified by ad-hoc analysis — AT29C256/AT29LV256 route to `configure_flash4`, not `configure_eprom`).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pinout presence check | Don't hardcode `_VPP_PINOUTS = {"DIP28_2764", ...}` as a literal | Load from `pinouts.json` | Phase 58 adds new pinouts; dynamic load ensures auto-coverage |
| Nibble-to-voltage mapping | Don't add a separate VDD_VOLTAGES dict | Reuse `VCC_VOLTAGES` for both vcc and vdd lookups | minipro uses the same `tl866ii_vcc_voltages[]` table for both |
| Protocol name validation | Don't write a custom check | Remove from KNOWN_PROTOCOLS — the existing WARN gate already handles unknown IDs | The gate already prints warnings for unknown proto_id |

---

## Common Pitfalls

### Pitfall 1: Removing 0x35/0x39 from KNOWN_PROTOCOLS while leaving them in downstream code
**What goes wrong:** `check_dispatch.py` still maps `0x35: 5` and `0x39: 5` in `_ALGO_MEM_TYPE` and routes them in `dispatch()`. If a chip with one of these IDs somehow appeared in the DB (upstream drift), the dispatch map would give it a wrong handler silently.
**Why it happens:** KNOWN_PROTOCOLS change in build_db.py is not reflected in check_dispatch.py.
**How to avoid:** Remove both entries from `_ALGO_MEM_TYPE` and the `dispatch()` function in `check_dispatch.py` in the same commit.
**Warning signs:** `check_dispatch.py` has `0x35` or `0x39` in any literal — grep check before committing.

### Pitfall 2: Snapshot suite not updated after pulse_duration fix
**What goes wrong:** 252 chips change `pulse_duration`. The `test_info_known_chip_stderr` snapshot pins the current crash traceback for `firestarter info W27C512`. After the `vpp-pin` bug is separately fixed (Phase 58), that test will show new output. But even now, the `test_list` snapshot pins the current output which may include pulse_duration in some form.
**Why it happens:** Syrupy snapshot files in `tests/__snapshots__/test_characterization.ambr` record exact output.
**How to avoid:** After regenerating `chip_database.json`, run `pytest --snapshot-update` to refresh snapshots. Then review the diff to confirm only expected values changed.
**Warning signs:** Snapshot test failures for `test_info_known_chip`, `test_list`, or `test_search_w27` after DB regeneration.

### Pitfall 3: interpret_timing bare `except:` clause
**What goes wrong:** Current code has bare `except:` which ruff will flag as `BLE001` (blind exception).
**Why it happens:** The original code was written before ruff was enforced.
**How to avoid:** Change `except:` to `except Exception:` in the fixed `interpret_timing`. This is already shown in the fix above.
**Warning signs:** `ruff check` reports `BLE001` on the function.

### Pitfall 4: vcc/vdd swap creating false positives in test_eprom_info.py
**What goes wrong:** `test_eprom_info.py` line 52–64 (`test_clean_config_for_export_strips_vdd`) asserts that `_clean_config_for_export` drops the `vdd` key but keeps `vcc`. This test uses a hand-crafted dict, not the DB, so the key names it checks (`"vdd"`, `"vcc"`) are unaffected by the BUG-3 fix. However, review it to confirm.
**How to avoid:** Check test_eprom_info.py after applying the vcc/vdd swap — those tests operate on already-structured dicts, not on raw XML parsing. They should pass unchanged.

### Pitfall 5: Two-pass `_etype` pattern must survive
**What goes wrong:** The WARNING-5 and fm1608 overrides depend on the first pass `_etype` (flags-based). If a coder mistakenly merges the two `_etype` derivations into one, the safety overrides break.
**Why it happens:** The post-override re-derivation at lines 481-488 looks redundant to a casual reader.
**How to avoid:** The two-pass pattern is load-bearing. Touch only the `{0x35, 0x39}` removal from line 485's set. Leave the structure intact.

### Pitfall 6: Regenerating chip_database.json with live infoic.xml drift
**What goes wrong:** `build_db.py` fetches live from upstream master (D-01 operator decision). If upstream has changed since Phase 56 baseline, the diff may include non-Phase-57 changes.
**How to avoid:** The Phase 59 GATE-02 task owns the per-chip diff review. Phase 57's job is to make the code correct; Phase 59 will diff the output. Still, the Phase 57 plan should include a step to verify that `python tools/build_db.py` completes without errors and that `check_dispatch.py` exits 0.

---

## Code Examples

### BUG-2 Fix: interpret_timing (SC-1)

```python
# Source: infoic-field-dictionary.md BUG-2; minipro database.c#L866 @ a8efaedc
def interpret_timing(raw_hex, protocol_id):
    """Return pulse delay string. Raw pulse_delay is microseconds for all protocols."""
    try:
        val = int(raw_hex, 16)
    except Exception:
        val = 0

    if protocol_id in (0x07, 0x08, 0x0B):
        return f"{val} us"

    return "Algorithm Controlled"
```

### BUG-1 Fix: VCC_VOLTAGES (SC-2)

```python
# Source: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]
VCC_VOLTAGES = {
    0x00: "5V",
    0x01: "3.3V",
    0x02: "4V",    # was missing — AT28C256/AT28C64-class chips use this
    0x03: "4.5V",  # was missing
    0x04: "5.5V",
    0x05: "6.5V",
}
```

### BUG-3 Fix: vcc/vdd swap (SC-3)

```python
# Source: minipro database.c#L921-L923 @ a8efaedc
# vcc = (voltages >> 8) & 0x0F  (bits 11-8)
# vdd = (voltages >> 12) & 0x0F (bits 15-12)
"vcc": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),    # bits 11-8
"vdd": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),   # bits 15-12
```

### BUG-4 Fix: PROTOCOL_MAP excerpt (SC-4)

```python
# Source: minipro database.h#L24-L77 @ a8efaedc — IC2_ALG_* constants
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

### GATE-03 Fix: check_dispatch.py VPP-safety guard extension (SC-5)

```python
# Near top, after existing constants:
import json as _json  # if not already imported
_PINOUT_FILE = os.path.join(_DATA_DIR, "pinouts.json")

# Inside main(), after loading DB:
with open(_PINOUT_FILE, encoding="utf-8") as _pf:
    _pinouts_raw = _json.load(_pf)
# Dynamically build the set of pinouts that have a vpp-pin field.
# Using pinouts.json avoids hardcoding — Phase 58 may add new pinouts.
_vpp_pinouts = frozenset(
    k for k, v in _pinouts_raw.items() if "vpp-pin" in v.get("pins", {})
)
_5v_eeprom_algos = frozenset({0x05, 0x06, 0x0D})

# New error list:
vpp_eeprom_in_eprom = []

# Inside the chip loop, after existing eeprom28c_in_eprom check:
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

---

## DEC-02 Completeness Assessment

DEC-02 requires `build_db.py` field decode to be re-derived to match minipro source semantics for `voltages`, `flags`, `protocol_id`, `type`, and `package_details`.

**Assessment per field:**

| Field | Sub-requirement | Phase 56 status | Phase 57 fix | After Phase 57 |
|-------|-----------------|-----------------|--------------|----------------|
| `voltages` VCC nibbles | BUG-1 | Documented | Add `0x02`/`0x03` | CORRECT |
| `voltages` field labels | BUG-3 | Documented | Swap vcc/vdd | CORRECT |
| `voltages` VPP byte | Already correct | N/A | No change | CORRECT |
| `pulse_delay` | BUG-2 | Documented | Remove ×100 | CORRECT |
| `flags` — _etype | Already correct (`& 0x10`) | N/A | No change | CORRECT |
| `flags` — chip_id_check | Already correct (`& 0x20`) | N/A | No change | CORRECT |
| `protocol_id` | BUG-4 | Documented | Fix PROTOCOL_MAP | CORRECT |
| `type` | Already correct (`in [1,4]`) | N/A | No change | CORRECT |
| `package_details` | Already correct (DIP filter) | N/A | No change | CORRECT |

**Conclusion:** Criteria 1–4 together with the Phase 56 dictionary fully satisfy DEC-02. No additional field-decode corrections are needed beyond what the 4 bugs specify. [ASSUMED] (based on reading all fields in build_db.py against the field dictionary — no additional decode discrepancies found)

---

## Test Suite Architecture

**Current state (Phase 56 verified):** 470 tests green, 72% coverage.

**Tests directly affected by Phase 57 changes:**

| Test | File | Impact | Action Required |
|------|------|--------|-----------------|
| `test_info_known_chip` | `test_characterization.py:248` | Pins current crash; will still crash post-57 (vpp-pin TypeError in ic_layout.py is NOT fixed here) | No snapshot update needed for this one |
| `test_list` | `test_characterization.py:239` | Pins the list output which includes pulse_duration indirectly? The list table does NOT show pulse_duration — likely unchanged | Verify after DB regeneration |
| `test_search_w27` | `test_characterization.py:261` | Pins W27 search results — if any W27 chip `pulse_duration` appears, needs update | Verify after DB regeneration |
| `test_clean_config_for_export_strips_vdd` | `test_eprom_info.py:52` | Uses a hand-crafted dict; unaffected by BUG-3 fix | No action |

**Snapshot update command:**
```bash
cd firestarter_app && python -m pytest tests/test_characterization.py --snapshot-update
```

**Test for check_dispatch changes:** `check_dispatch.py` is not currently invoked by the automated test suite (only referenced indirectly in `test_audit_coverage_matrix.py:403` as a comment). The plan should include a manual invocation check:
```bash
cd firestarter_app && python tools/check_dispatch.py
```
Expected: `PASS: all 734 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions`

After the GATE-03 extension, the pass message should also include: `0 vpp-pin Flash/EEPROM chips route to configure_eprom` (or equivalent phrasing in the new check's print statement).

**Coverage floor:** The test suite is at 72% coverage with a 70% floor. Phase 57 edits `tools/build_db.py` and `tools/check_dispatch.py` — these are `tools/` scripts, not `firestarter/` library modules. If they are included in coverage measurement, the added lines may affect the floor. Verify coverage does not drop below 70% after changes.

**Regression command:**
```bash
cd firestarter_app && python -m pytest tests/ --cov-fail-under=70
```

---

## Runtime State Inventory

This phase is NOT a rename/refactor. Omitted.

---

## Environment Availability

No external dependencies beyond the existing Python toolchain.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python ≥3.9 | build_db.py, check_dispatch.py | Yes | 3.12 (devcontainer) | — |
| requests | build_db.py live-fetch | Yes | pinned in pyproject.toml | — |
| pytest + syrupy | test runner + snapshots | Yes | pinned | — |
| internet (gitlab.com) | DB regeneration | Assumed Yes | — | Use cached infoic.xml from tools/ |

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (pinned in pyproject.toml) |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `cd firestarter_app && python -m pytest tests/ -x -q` |
| Full suite command | `cd firestarter_app && python -m pytest tests/ --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Notes |
|--------|----------|-----------|-------------------|-------|
| DEC-03 | W27C512 pulse_duration = "100 us" | unit (inline assertion) | `python -c "import json; db=json.load(open('firestarter/data/chip_database.json')); ..."` | Manual spot-check or dedicated test |
| DEC-04 | VCC_VOLTAGES includes 0x02/0x03 | unit | Add test to test_eprom_database.py or test_decoder.py | New test needed |
| DEC-04 | vcc=bits-11-8, vdd=bits-15-12 | unit | Same new test | New test needed |
| DEC-05 | PROTOCOL_MAP uses IC2_ALG names | unit (grep/import check) | `python -c "from tools.build_db import PROTOCOL_MAP; assert 'NVRAM' not in str(PROTOCOL_MAP)"` | Or new test |
| GATE-03 | check_dispatch exits 0 after extension | integration | `python tools/check_dispatch.py` (exit code 0) | Existing script; add to CI |

### Wave 0 Gaps

- [ ] No dedicated unit tests for `interpret_timing()` or `VCC_VOLTAGES` currently exist — consider adding to `tests/test_decoder.py` (if it exists) or a new `tests/test_build_db.py`
- [ ] No automated test invokes `check_dispatch.py` as a subprocess (only referenced in comments) — consider adding to `test_audit_coverage_matrix.py` or a new `tests/test_check_dispatch.py`
- [ ] Snapshot updates for `test_characterization.py` after DB regeneration

---

## Security Domain

This phase edits Python decode tables and a safety-guard script. No authentication, session management, cryptography, or user-facing input parsing changes. ASVS categories V2/V3/V4/V6 are not applicable. V5 (input validation) is marginally relevant only in the sense that the protocol ID gate (`KNOWN_PROTOCOLS`) is a form of allowlisting — the fix tightens it (removes 0x35/0x39) rather than loosening it.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | DEC-02 is fully satisfied by the 4 bug fixes — no additional field decode corrections exist | DEC-02 Completeness Assessment | If a 5th decode bug exists, DEC-02 would not be closed. Risk is LOW — all 13 fields in the dictionary were individually reviewed against build_db.py. |
| A2 | `tl866ii_vcc_voltages[]` is the same lookup for both VCC and VDD nibbles | BUG-1/BUG-3 fix | If VDD uses a different table, adding 0x02/0x03 to VCC_VOLTAGES may be incomplete. Risk is LOW — `database.c#L921-L923` shows the same `voltages.vcc`/`voltages.vdd` access pattern using the same array. |
| A3 | The `test_list` snapshot does not pin pulse_duration values | Test suite section | If snapshot update is required but not flagged in the plan, tests will fail. Risk is LOW — the list output shows type/VPP/size, not pulse_duration. |

---

## Open Questions (RESOLVED)

> All three are factual lookups, not blocking unknowns. Each is resolved in a plan action: Q1 → 57-03 Task 1 baseline-diff spot-check; Q2 → 57-01 Task 3 keeps `0x11` as a commented exclusion entry (per 57-PATTERNS.md); Q3 → 57-03 Task 2 confirms the `test_info_known_chip` snapshot is unchanged.

1. **Does AT28C256 have nibble 0x02 or 0x03 in its voltages field?** *(resolved → 57-03 Task 1)*
   - What we know: The success criterion says "AT28C256/AT28C64-class chips that previously defaulted to 5V now decode correct VCC."
   - What's unclear: We cannot verify the raw nibble from the generated DB (it was already decoded to "5V"). The raw value is in `infoic.xml` which requires a live fetch to inspect.
   - Recommendation: After applying BUG-1 fix and regenerating, diff the AT28C256 VCC field in the new vs baseline JSON. If it changes from "5V" to "4V" or "4.5V", the fix is confirmed. If it stays "5V", that chip happens to have nibble 0x00 and the fix corrects other chips.

2. **Should `PROTOCOL_MAP` retain `0x11` (IC2_ALG_FWH) as a comment or be removed entirely?**
   - What we know: The current code has `0x11: "FLASH_FWH"`. It is excluded from `KNOWN_PROTOCOLS` so it can never produce a chip.
   - Recommendation: Keep it as a commented-out entry with the exclusion rationale (matching the pattern for 0x2A/0x2C/etc.), since it IS a real IC2_ALG constant — it just refers to infeasible-on-RURP hardware.

3. **Will the snapshot for `test_info_known_chip` need updating?**
   - What we know: `firestarter info W27C512` currently crashes with a `TypeError: '<=' not supported between instances of 'list' and 'int'` in `ic_layout.py`. This crash is not fixed in Phase 57.
   - Recommendation: The snapshot pins this crash and should remain unchanged after Phase 57. Confirm by running `firestarter info W27C512` after applying fixes.

---

## Sources

### Primary (HIGH confidence — VERIFIED against minipro source commit a8efaedc)
- `firestarter_app/doc/infoic-field-dictionary.md` — Phase 56 authoritative source; all 4 bugs documented with minipro source citations
- `firestarter_app/doc/protocol-id.md` — canonical IC2_ALG_* names, exclusion rationales
- `firestarter_app/doc/protocol-flags.md` — MP_* constants, UNKNOWN bits

### Secondary (HIGH confidence — direct code read)
- `firestarter_app/tools/build_db.py` — read in full; all bug locations confirmed
- `firestarter_app/tools/check_dispatch.py` — read in full; current guard scope confirmed
- `firestarter_app/firestarter/data/pinouts.json` — vpp-pin presence per pinout confirmed
- `firestarter_app/firestarter/data/chip_database.json` — algorithm distribution and AT29C256/AT29LV256 confirmed via ad-hoc Python analysis

### Tertiary (MEDIUM confidence — runtime verification)
- Ad-hoc Python analysis of chip_database.json: 252 BUG-2 chips, 2 GATE-03 near-violations (AT29C256/AT29LV256 on configure_flash4, not configure_eprom), vcc/vdd distribution

---

## Metadata

**Confidence breakdown:**
- Bug locations: HIGH — exact line numbers confirmed by reading source
- Fix correctness: HIGH — cross-referenced against Phase 56 field dictionary (minipro-source-grounded)
- Test impact: MEDIUM — snapshot content requires running after DB regeneration to confirm
- GATE-03 violation count: HIGH — verified by Python analysis

**Research date:** 2026-06-08
**Valid until:** 2026-07-08 (stable domain — only changes if upstream infoic.xml semantics change)
