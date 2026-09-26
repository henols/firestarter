# Phase 56: Snapshot + Field Dictionary + Corrected Docs - Pattern Map

**Mapped:** 2026-06-08
**Files analyzed:** 5 (1 snapshot artifact, 1 new doc, 3 doc rewrites)
**Analogs found:** 4 / 5

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/tools/baseline/chip_database.baseline.json` | artifact (regression anchor) | batch / snapshot | `firestarter_app/firestarter/data/chip_database.json` | exact (copy-at-point-in-time) |
| `firestarter_app/doc/infoic-field-dictionary.md` | reference doc (new) | transform (XML field → annotated table) | `firestarter_app/doc/protocol-id.md` + `firestarter_app/doc/protocol-flags.md` | role-match (same doc family, same repo) |
| `firestarter_app/doc/protocol-id.md` | reference doc (rewrite) | transform | `firestarter_app/doc/protocol-flags.md` | exact (same doc family, same H2 + table + section structure) |
| `firestarter_app/doc/protocol-flags.md` | reference doc (rewrite) | transform | `firestarter_app/doc/package-details.md` | exact (same doc family) |
| `firestarter_app/doc/package-details.md` | reference doc (rewrite) | transform | `firestarter_app/doc/protocol-flags.md` | exact (same doc family) |

---

## Pattern Assignments

### `firestarter_app/tools/baseline/chip_database.baseline.json` (artifact, snapshot)

**Analog:** `firestarter_app/firestarter/data/chip_database.json`

**How to create:** Run `python tools/build_db.py` from `firestarter_app/`, then copy the generated output to `tools/baseline/chip_database.baseline.json`. Commit on the beta branch as Wave 0 / Plan 1 — before any other Phase 56 changes.

**JSON structure pattern** (from `chip_database.json` lines 1-30):
```json
{
  "ALI(Acer)": [
    {
      "part_number": "M8720",
      "electrical": {
        "type": "UV-EPROM",
        "size_bytes": 262144,
        "pin_count": 32,
        "vpp": "12V",
        "vpp_mv": 12000,
        "vdd": "5V",
        "vcc": "5V"
      },
      "programming": {
        "algorithm": 8,
        "pulse_duration": "20 us",
        "chip_id_check": false,
        "chip_id_value": "0x00000000"
      },
      "pinout": "DIP32_STD"
    }
  ]
}
```

**Content invariant:** 734 chips, 58 manufacturers, 14063 lines at phase start. No hand-editing; only `build_db.py` output committed.

**Directory note:** `tools/baseline/` does not exist yet — the baseline JSON file creates it. No `.gitkeep` or README needed.

---

### `firestarter_app/doc/infoic-field-dictionary.md` (new reference doc)

**Analog:** `firestarter_app/doc/protocol-id.md` (DOC-03) and `firestarter_app/doc/protocol-flags.md` (DOC-02)

**Logo-header pattern** (line 1 of ALL three existing docs — identical, copy verbatim):
```html
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>
```

**Top-of-file citation block** (unique to this new file, per D-05/D-06):
```markdown
**Citation commit:** `a8efaedc236c1d9718bd28299dfbb99536b010ff` (2026-03-23, "infoic: Correct ATMEGA328PB fuse defaults")
**Permalink base:** `https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc236c1d9718bd28299dfbb99536b010ff/src/`
```

**Per-attribute section structure** (H3 heading per attribute, confirmed in RESEARCH.md §Open Questions #3):
```markdown
### `<attribute_name>` (<type>) — CONFIRMED | INFERRED | UNKNOWN

**Source:** `<file>#L<line>` @ `a8efaedc`

| Bit | Mask | Constant | Meaning |
|-----|------|----------|---------|
| ... | ...  | ...      | ...     |

**build_db.py usage:** `<relevant line(s)>`
**BUG note (if applicable):** BUG-N — `<what is wrong>` vs `<what is correct>`
```

**Thirteen attributes to cover** (from CONTEXT.md §domain):
`package_details`, `type`, `variant`, `protocol_id`, `flags`, `voltages`, `pin_map`, `pulse_delay`, `chip_id`, `code_memory_size`, `page_size`, `chip_info`, `blank_value`

**CONFIRMED/INFERRED/UNKNOWN labelling rule** (from RESEARCH.md pitfall 2):
- CONFIRMED: bit has a corresponding `MP_*` constant in `database.c` lines 39-50
- UNKNOWN: bits 3, 6, 7 of `flags` — no `MP_*` constant; must be labelled UNKNOWN, not INFERRED

**Key build_db.py constant blocks the dictionary annotates:**

PROTOCOL_MAP (`build_db.py` lines 25-44):
```python
PROTOCOL_MAP = {
    0x05: "FLASH_AMD_STD",   # IC2_ALG_F29EE — correct functional name
    0x06: "FLASH_AMD_ALT",   # IC2_ALG_W29F32P — correct functional name
    0x07: "EPROM_STD",       # IC2_ALG_ROM28P_1 — correct functional name
    0x08: "EPROM_QUICK",     # IC2_ALG_ROM32P — correct functional name
    0x0B: "EPROM_LEGACY",    # IC2_ALG_ROM24P_1 — correct functional name
    0x0E: "SRAM_32PIN",      # IC2_ALG_RAM32_1 — correct functional name
    0x0D: "EEPROM_POLL",     # IC2_ALG_EE28C32P — correct functional name
    0x10: "FLASH_INTEL",     # IC2_ALG_28F32P — correct functional name
    0x11: "FLASH_FWH",       # IC2_ALG_FWH — infeasible on RURP (LPC serial, 3.3V)
    0x27: "SRAM_24PIN",      # IC2_ALG_ROM24P_2 — mislabeled (ROM algo), fm1608 override
    0x28: "SRAM_STD",        # IC2_ALG_ROM28P_2 — mislabeled (ROM algo), fm1608 override
    0x29: "SRAM_512K_1M",    # IC2_ALG_RAM32_2 — correct functional name
    0x2A: "NVRAM_32PIN",     # BUG-4: IC2_ALG_GAL16 — GAL16V8 PLD, type=3, WRONG
    0x2C: "NVRAM_TIMEKEEPER",# BUG-4: IC2_ALG_GAL22 — GAL22V10 PLD, type=3, WRONG
    0x2E: "NVRAM_512K",      # BUG-4: IC2_ALG_PIC32X_2 — PIC32 MCU, type=2, WRONG
    0x35: "FLASH_EEPROM_LIKE",# BUG-4: IC2_ALG_ITE — ITE IT8xxx MCU, TQFP128, WRONG
    0x39: "FLASH_INTEL_ALT", # BUG-4: NO IC2_ALG CONSTANT — phantom, INFOIC2PLUS-unreachable
    0x3C: "FLASH_4MB",       # BUG-4: NOT IN MINIPRO SOURCE — invented, remove entirely
}
```

VCC_VOLTAGES (`build_db.py` line 85) — current (BUG-1, missing 0x02 and 0x03):
```python
VCC_VOLTAGES = {0x00: "5V", 0x01: "3.3V", 0x04: "5.5V", 0x05: "6.5V"}
# MISSING: 0x02: "4V", 0x03: "4.5V"  (source: tl866ii_vcc_voltages[] database.c#L130)
```

voltages unpacking (`build_db.py` lines 510-511) — current (BUG-3, labels swapped):
```python
"vdd": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),   # WRONG: reads vcc position
"vcc": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),  # WRONG: reads vdd position
# Correct (minipro database.c#L921): vcc=(>>8), vdd=(>>12)
```

interpret_timing (`build_db.py` lines 268-284) — current (BUG-2, x100 multiplier wrong):
```python
if protocol_id == 0x0B:
    return f"{val * 100} us"   # WRONG: raw value is already µs
if protocol_id == 0x07:
    return f"{val * 100} us"   # WRONG: raw value is already µs
```

---

### `firestarter_app/doc/protocol-id.md` (DOC-03, rewrite)

**Analog:** `firestarter_app/doc/protocol-flags.md` (most similar: summary table first, details section, no ASCII box art)

**Logo-header** (line 1, from existing `protocol-id.md` line 1):
```html
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>
```

**Document structure pattern** (from existing `protocol-flags.md` lines 1-17):
```markdown
<p align="left">...</p>

---

## <Title>

| Protocol ID | ... | ... | ... |
|-------------|-----|-----|-----|
| `0x05`      | ... | ... | ... |
```

**Rewrite structure for DOC-03:**
1. Logo-header (line 1, exact copy)
2. `---` separator
3. `## Protocol-ID Reference` (H2 title)
4. Intro sentence: source of truth = minipro `IC2_ALG_*` constants @ `a8efaedc`
5. **Summary table** — columns: Protocol-ID | IC2_ALG Constant | Firestarter Label | Firmware Handler | Notes
6. **Excluded / Infeasible IDs** subsection — table with rationale column for 0x11, 0x2A, 0x2C, 0x2E, 0x35, 0x39 (phantom), 0x3C (invented)
7. **Per-ID Detail** sections (H3 per protocol), for in-scope IDs only
8. Brief usage note at end

**Critical corrections required** (D-10, RESEARCH.md):
- 0x2A: label as IC2_ALG_GAL16 (GAL PLD), exclude with rationale
- 0x2C: label as IC2_ALG_GAL22 (GAL PLD), exclude with rationale
- 0x2E: label as IC2_ALG_PIC32X_2 (PIC MCU), exclude with rationale
- 0x35: label as IC2_ALG_ITE (ITE EC MCU, TQFP128), exclude; remove from KNOWN_PROTOCOLS note
- 0x39: label as PHANTOM — no IC2_ALG constant in database.h; INFOIC2PLUS-unreachable; remove from KNOWN_PROTOCOLS note
- 0x3C: label as INVENTED — not in minipro source; remove from PROTOCOL_MAP note

---

### `firestarter_app/doc/protocol-flags.md` (DOC-02, rewrite)

**Analog:** `firestarter_app/doc/package-details.md` (both are flag-bit tables with hex mask + meaning columns)

**Logo-header** (line 1, from existing `protocol-flags.md` line 1):
```html
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>
```

**Current incorrect flag table pattern** (existing `protocol-flags.md` lines 20-32) — shows the format to keep but fix the contents:
```markdown
## Flag Bits (single-bit meaning)

| Bit | Mask        | Meaning (most consistent interpretation)                                 |
|-----|-------------|---------------------------------------------------------------------------|
| 3   | `0x00000008`| Requires elevated VPP for programming (typical EPROM behavior).           |
| 4   | `0x00000010`| Requires explicit write-enable or software unlock sequence.              |
```

**Rewrite structure for DOC-02:**
1. Logo-header (line 1, exact copy)
2. `---` separator
3. `## Protocol Flags Reference` (H2 title)
4. Source attribution line: `MP_*` constants from `database.c` lines 39-50 @ `a8efaedc`
5. **Source-confirmed bits table** — columns: Bit | Mask | MP_* Constant | Meaning (CONFIRMED) — covering bits 1, 4, 5, 12, 13, 14, 15, 18, 19, 20-21
6. **UNKNOWN bits table** — columns: Bit | Mask | Current Docs Claim | Correct Statement (UNKNOWN) — covering bits 3, 6, 7
7. **Combined mask patterns** section (retained from current doc, corrected)
8. WARNING-5 note: bit 4 (`MP_ERASE_MASK`) is the discriminator in `build_db.py`'s WARNING-5 predicate (`flags & 0x10`)

**Critical correction required** (D-10, RESEARCH.md):
- Bit 4 (`0x00000010`): current label "Requires explicit write-enable or software unlock sequence" is WRONG. Correct: `MP_ERASE_MASK` = "can be electrically erased" (the WARNING-5 discriminator)
- Bits 3/6/7: currently stated as confirmed meanings; rewrite must mark them UNKNOWN

---

### `firestarter_app/doc/package-details.md` (DOC-01, rewrite)

**Analog:** `firestarter_app/doc/protocol-flags.md` (closest: both are bit-field tables)

**Logo-header** (line 1, from existing `package-details.md` line 1):
```html
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>
```

**Current bit table pattern** (existing `package-details.md` lines 4-22) — shows the table structure to preserve:
```markdown
### **Updated Flag Bits and Inferred Meanings**

| Hex Value   | Bit Position(s)  | Inferred Meaning                                                                  |
|-------------|------------------|-----------------------------------------------------------------------------------|
| 0x00000008  | Bit 3            | Requires VPP (High Programming Voltage)                                           |
| 0x00000010  | Bit 4            | Requires Write Enable Sequence                                                    |
```

**Rewrite structure for DOC-01:**
1. Logo-header (line 1, exact copy)
2. `---` separator
3. **Retitle** to `## package_details Field Reference` (D-10: "re-titled to describe `flags`" — the current title is misleading; the `package_details` attribute governs the DIP filter, not the bit flags table)
4. `package_details` uint32 layout section: bit 31 (SMD), bits 29-24 (pin count), bits 15-8 (ICSP serial index), bits 7-0 (adapter type)
5. **Source-cited `flags` bits table** — columns: Bit | Hex Mask | MP_* Constant | Meaning | Status (CONFIRMED/UNKNOWN)
6. Explicitly mark bits 3, 6, 7 as UNKNOWN with note "not a defined MP_* constant in database.c lines 39-50"
7. Build_db.py filter note: `24 <= pin_count <= 32`, `is_smd == 0`, `is_serial == 0`, `type_int in [1, 4]`

---

## Shared Patterns

### Logo-Header Block (apply to ALL doc files, including new dictionary)

**Source:** All three existing docs (`protocol-id.md` line 1, `protocol-flags.md` line 1, `package-details.md` line 1) — identical across all three.

**Copy this verbatim as line 1 of every doc (including new `infoic-field-dictionary.md`):**
```html
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>
```

**Apply to:** `infoic-field-dictionary.md`, `protocol-id.md`, `protocol-flags.md`, `package-details.md`

---

### Doc Separator Convention

**Source:** All three existing docs — each uses `---` on line 3 (after blank line 2).

**Pattern:**
```markdown
<p align="left">...</p>

---

## Title Here
```

**Apply to:** All four doc files.

---

### CONFIRMED / INFERRED / UNKNOWN Labelling

**Source:** RESEARCH.md §"Field Dictionary — Authoritative Attribute Reference" — each attribute opens with the status marker.

**Pattern:**
```markdown
### `attribute_name` (type) — CONFIRMED
```
or
```markdown
### `attribute_name` (type) — UNKNOWN
```

**Rule:** Only bits with a corresponding `MP_*` constant in `database.c` lines 39-50 are CONFIRMED. Bits 3, 6, 7 of `flags` have no `MP_*` constant → UNKNOWN, not INFERRED.

**Apply to:** `infoic-field-dictionary.md` (all 13 attributes); `protocol-flags.md` (UNKNOWN marker on bits 3/6/7 rows); `package-details.md` (Status column in bit table).

---

### Citation Permalink Format

**Source:** RESEARCH.md §D-11 — single recorded SHA, one permalink pattern.

**Pattern:**
```markdown
**Source:** `database.c#L<line>` @ [`a8efaedc`](https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc236c1d9718bd28299dfbb99536b010ff/src/database.c#L<line>)
```

**Apply to:** `infoic-field-dictionary.md` (all citations); referenced in preamble of `protocol-id.md`, `protocol-flags.md`, `package-details.md`.

---

### WARNING-5 Safety Consistency

**Source:** `firestarter_app/CLAUDE.md` — WARNING-5 override logic is load-bearing safety.

**Constraint:** Any doc text about bit 4 (`MP_ERASE_MASK`) must be consistent with WARNING-5's `flags & 0x10` predicate. Bit 4 = "can be electrically erased" — this is the discriminator `build_db.py` uses to flip `DIP28_2764 + 0x07 + Flash/EEPROM` chips to `0x0D`. Documents must not describe bit 4 in a way that contradicts this use.

**Apply to:** `infoic-field-dictionary.md` (`flags` entry), `protocol-flags.md` (bit 4 row), `package-details.md` (bit 4 row).

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `firestarter_app/tools/baseline/chip_database.baseline.json` | regression anchor | snapshot | Baseline snapshot directory (`tools/baseline/`) does not exist yet; the file is a point-in-time copy of `chip_database.json`, created by running `build_db.py` then copying the output — no analog for this specific artifact pattern, but the JSON structure is identical to the source file |

---

## Metadata

**Analog search scope:** `firestarter_app/doc/`, `firestarter_app/tools/`, `firestarter_app/firestarter/data/`
**Files scanned:** 6 (`protocol-id.md`, `protocol-flags.md`, `package-details.md`, `build_db.py` lines 1-180 + 260-285 + 505-515, `chip_database.json` lines 1-30)
**Pattern extraction date:** 2026-06-08
**minipro citation commit:** `a8efaedc236c1d9718bd28299dfbb99536b010ff`
