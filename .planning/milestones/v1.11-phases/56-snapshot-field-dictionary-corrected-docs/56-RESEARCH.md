# Phase 56: Snapshot + Field Dictionary + Corrected Docs — Research

**Researched:** 2026-06-08
**Domain:** Documentation and regression snapshot — minipro source cross-reference, infoic.xml field semantics, doc rewrite
**Confidence:** HIGH (all field semantics verified against minipro source via direct WebFetch of pinned commit; build_db.py and existing docs read in full)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** No vendored `infoic.xml` in the repo. `build_db.py` keeps fetching live from `MINIPRO_XML_URL` pointing to upstream `master` (line 10 behavior preserved).
- **D-02:** GATE-01 re-derived — the immutable anchor is the OUTPUT (committed snapshot of current generated `chip_database.json`), not the input XML.
- **D-03:** The regression baseline is a committed snapshot of the CURRENT generated `chip_database.json` (pre-milestone baseline). Phase 59's GATE-02 per-chip diff compares against this frozen DB.
- **D-04:** GATE-04 weakened — "deterministic given a stable upstream `master`"; byte-identity only holds if upstream `master` is unchanged between runs. Flag for Phase 59 planner.
- **D-05:** Field-dictionary citations use GitLab commit-permalink URLs to minipro source pinned to ONE recorded SHA documented at top of the dictionary. No minipro source vendored.
- **D-06:** One recorded "minipro citation commit" SHA at the top of `infoic-field-dictionary.md`; all permalinks share it.
- **D-07:** The authoritative field dictionary lives as `firestarter_app/doc/infoic-field-dictionary.md` (companion markdown). `build_db.py` constants stay code-only.
- **D-08:** Rewrite all three docs FRESH, derived from the field dictionary. Build order: dictionary first → docs regenerated from it.
- **D-09:** Preserve the existing logo-header convention: each doc opens with the `firestarter_logo.png` `<p align="left">` block at line 1.
- **D-10:** Specific corrections per doc:
  - `protocol-id.md` (DOC-03): canonical `IC2_ALG_*` names; fix the `0x39` error; feasibility/exclusion notes for non-memory + infeasible IDs.
  - `protocol-flags.md` (DOC-02): canonical protocol names; flag-bit fix — bit 4 = `can_erase`, not "requires write-enable sequence".
  - `package-details.md` (DOC-01): re-titled to describe `flags`; bit meanings source-grounded; inferred bits 3/6/7 explicitly marked not source-confirmed.
- **D-11:** The dictionary MUST state correct decode semantics for BUG-1..4 even though the `build_db.py` code fix is Phase 57. Four OPEN items listed for Phase 56 to resolve (see below — all resolved in this research).

### Claude's Discretion

- Exact path/filename of the baseline DB snapshot (D-03) and the per-attribute table layout of the dictionary are left to the planner/executor.
- Whether the citation-commit SHA (D-06) is also mirrored as a comment in `build_db.py` is discretionary.

### Deferred Ideas (OUT OF SCOPE)

- v1.11 input pinning / true offline-reproducible rebuilds (original GATE-01/04 design) — not pursued.
- `w27c512-eeprom-misclassification` — v1.11-relevant but a Phase 57/58 classification fix, not a snapshot/docs item. Dictionary should document correct erasability semantics.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEC-01 | Authoritative, source-cited field dictionary for all 13 in-scope attributes, each marked CONFIRMED / INFERRED / UNKNOWN | All 13 attributes fully researched in §Standard Stack; D-11 open items resolved |
| DEC-03 | `pulse_delay` is microseconds for all protocols (dictionary side — code fix Phase 57) | BUG-2 CONFIRMED: minipro stores raw µs, no transformation; ×100 multiplier is wrong |
| DEC-04 | VCC/VDD voltage decode correct and complete (dictionary side — code fix Phase 57) | BUG-1 CONFIRMED: nibbles 0x02=4V and 0x03=4.5V missing. BUG-3 CONFIRMED: vcc=(>>8), vdd=(>>12) in minipro source; build_db has them swapped |
| DEC-05 | `PROTOCOL_MAP` uses canonical `IC2_ALG_*` names; exclusion rationale documented (dictionary side — code fix Phase 57) | BUG-4 CONFIRMED: all wrong/phantom/invented entries catalogued against IC2_ALG constants in database.h |
| DOC-01 | `package-details.md` corrected — re-titled to describe `flags`, bit meanings source-grounded, inferred bits (3/6/7) explicitly marked | flags bits from database.c lines 39–50; unknown bits clearly delineated |
| DOC-02 | `protocol-flags.md` corrected — canonical protocol names, flag-bit interpretation fixes (bit 4 = `can_erase`) | MP_ERASE_MASK = 0x00000010 confirmed; current "requires write-enable sequence" is wrong |
| DOC-03 | `protocol-id.md` corrected — `IC2_ALG_*` names, `0x39` error fixed, feasibility/exclusion notes | Full IC2_ALG table verified; 0x39 has no IC2_ALG constant (phantom); all exclusion rationales sourced |
| GATE-01 | Regression baseline committed (re-derived: the OUTPUT DB snapshot, not input XML, per D-02/D-03) | Snapshot mechanics documented: `python tools/build_db.py` → commit `chip_database.json`; 734 chips, 58 manufacturers |
</phase_requirements>

---

## Summary

Phase 56 is a pure documentation and snapshot phase. It produces three artifacts that anchor all downstream v1.11 decode work: a committed regression baseline of the current `chip_database.json`, a new authoritative field dictionary (`firestarter_app/doc/infoic-field-dictionary.md`) with every Firestarter-relevant `infoic.xml` attribute cited against minipro source, and three rewritten decode docs derived from the dictionary.

All four D-11 "OPEN" items from CONTEXT.md have been resolved in this research session against the pinned minipro commit (`a8efaedc236c1d9718bd28299dfbb99536b010ff`, 2026-03-23). BUG-2 (pulse_delay unit confusion) is CONFIRMED — minipro `database.c` loads `pulse_delay` directly into `device->pulse_delay` with no transformation; the raw value IS already microseconds. BUG-1, BUG-3, and BUG-4 are confirmed from prior research sessions and further verified here. The VCC nibble table from minipro (`tl866ii_vcc_voltages[]`) explicitly contains `0x02=4V` and `0x03=4.5V`, missing from `build_db.py`. The voltages field unpacking in `database.c` lines 921–923 confirms `vdd=(voltages>>12)&0x0f` and `vcc=(voltages>>8)&0x0f` — the exact opposite of `build_db.py` lines 510–511.

**Primary recommendation:** Sequence within this phase must be: (1) commit chip_database.json as baseline, (2) write infoic-field-dictionary.md with all 13 attributes cited and D-11 resolved, (3) rewrite the three docs from the dictionary. Do not change any `build_db.py` decode logic — that is Phase 57.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Regression baseline snapshot | Host — `firestarter_app` repo | None (commit artifact) | `chip_database.json` is a generated host artifact; committed to `firestarter_app` sub-repo |
| Field dictionary authoring | Host — `firestarter_app/doc/` | None | Markdown documentation; no firmware touch |
| Doc rewrite (3 files) | Host — `firestarter_app/doc/` | None | Same doc family, same repo |
| D-11 source verification | Research (this phase) | None | Verify against minipro source before writing; no code changes |
| Firmware sub-repo | Not touched | — | Confirmed HOST-ONLY milestone |

---

## Standard Stack

### This Phase Has No Package Installs

Phase 56 is documentation-only + a git commit of an existing generated file. No new Python packages are installed. The only tooling required is already present:

| Tool | Already Available | Purpose |
|------|-----------------|---------|
| Python 3.12 | Yes (`/usr/local/bin/python3`) | Run `build_db.py` to regenerate baseline |
| `requests` library | Yes (confirmed in environment) | Used by `build_db.py` to fetch XML |
| `git` | Yes (2.54.0) | Commit baseline and new doc files |

**Regeneration command:** `python tools/build_db.py` (from `firestarter_app/` directory; fetches from `MINIPRO_XML_URL` live).

**Current DB state:** 734 chips, 58 manufacturers, 14063 lines (`firestarter_app/firestarter/data/chip_database.json`).

---

## Package Legitimacy Audit

> SKIPPED — Phase 56 installs no external packages.

---

## Architecture Patterns

### System Architecture Diagram

```
[Phase 56 artifact flow]

STEP 1: Baseline Snapshot
  chip_database.json (current, 734 chips)
      |-- git commit (no code change) -->  tools/baseline/chip_database.baseline.json
                                           (or .planning/v1.11/ artifact — planner decides path)

STEP 2: Field Dictionary (NEW FILE)
  minipro src/database.c + database.h
  (GitLab permalink @ a8efaedc...)
      |-- research citations -->  firestarter_app/doc/infoic-field-dictionary.md
                                  [13 attributes × CONFIRMED/INFERRED/UNKNOWN]
                                  [one citation-commit SHA at top]
                                  [D-11 resolved: BUG-1..4 correct semantics documented]

STEP 3: Doc Rewrites (3 existing files)
  infoic-field-dictionary.md (authority)
      |-- derive -->  firestarter_app/doc/protocol-id.md       (DOC-03: IC2_ALG_* names, exclusions)
      |-- derive -->  firestarter_app/doc/protocol-flags.md    (DOC-02: bit meanings, bit 4 fix)
      |-- derive -->  firestarter_app/doc/package-details.md   (DOC-01: retitle to flags, UNKNOWN bits)

  Each doc preserves logo-header block at line 1 (D-09).
  No build_db.py decode behavior changed.

[Downstream consumption]
  tools/baseline/chip_database.baseline.json  -->  Phase 59 GATE-02 (per-chip diff)
  infoic-field-dictionary.md                 -->  Phase 57 (bug-fix code cites dictionary as authority)
```

### Recommended Project Structure

```
firestarter_app/
├── doc/
│   ├── infoic-field-dictionary.md   # NEW — authoritative attribute reference
│   ├── protocol-id.md               # REWRITTEN from dictionary (DOC-03)
│   ├── protocol-flags.md            # REWRITTEN from dictionary (DOC-02)
│   └── package-details.md           # REWRITTEN from dictionary (DOC-01)
├── firestarter/
│   └── data/
│       └── chip_database.json       # COMMITTED as baseline (no content change)
└── tools/
    └── baseline/                    # NEW directory (or .planning/v1.11/ — planner decides)
        └── chip_database.baseline.json  # Copy of chip_database.json at phase start
```

**Baseline location decision (D-03 leaves to planner):** Two options — `firestarter_app/tools/baseline/chip_database.baseline.json` (inside the sub-repo, co-located with the tool) or `.planning/v1.11/chip_database.baseline.json` (inside meta-repo, planning artifact). The `firestarter_app/tools/baseline/` path is slightly preferable because it keeps the baseline next to the generator tool and can be referenced via a relative path in Phase 59's diff script. Either is valid.

---

## D-11 Open Items — FULLY RESOLVED

All four items listed as OPEN in CONTEXT.md D-11 are now CONFIRMED against minipro source commit `a8efaedc236c1d9718bd28299dfbb99536b010ff` (2026-03-23). The dictionary must state these as CONFIRMED.

### BUG-2 / DEC-03: pulse_delay unit — CONFIRMED µs, no transformation

**Status:** CONFIRMED [VERIFIED: gitlab.com/DavidGriffith/minipro database.c]

`pulse_delay` in `infoic.xml` is already in microseconds for ALL protocols. Minipro `database.c` loads the field at line 866:
```c
err += get_attr_value(xml_device, size, "pulse_delay", &device->pulse_delay);
```
No transformation follows. The value is stored directly. The `interpret_timing` ×100 multiplier for `0x07` and `0x0B` in `build_db.py` (lines 275–279) is categorically wrong — it is NOT an intentional per-protocol unit conversion.

**Evidence from current DB (confirms the bug is live):**
- `W27C512`: `pulse_duration = "10000 us"` (should be `"100 us"` — raw XML value 0x64 = 100)
- `AM2716`: `pulse_duration = "50000 us"` (should be `"500 us"` — raw XML value 0x1F4 = 500)
- `CAT28C256` (algo 0x07, WARNING-5 flipped post-override): `pulse_duration = "1000000 us"` (should be `"10000 us"` — raw XML value 0x2710 = 10000)

**Protocol impact:** 212 chips at 0x07 + 40 chips at 0x0B = 252 chips currently have ×100 inflated `pulse_duration` values. [VERIFIED: gitlab.com/DavidGriffith/minipro database.c#L866]

### BUG-1 / DEC-04: VCC_VOLTAGES missing nibbles 0x02 and 0x03 — CONFIRMED

**Status:** CONFIRMED [VERIFIED: gitlab.com/DavidGriffith/minipro database.c]

`tl866ii_vcc_voltages[]` in minipro `database.c` lines 130–135:
```c
static const parameters_t tl866ii_vcc_voltages[] =
{
    { "3.3", 0x01 }, { "4", 0x02 }, { "4.5", 0x03 },
    { "5", 0x00 },   { "5.5", 0x04 }, { "6.5", 0x05 },
    { NULL, 0x00 }
};
```

Complete mapping: `0x00=5V, 0x01=3.3V, 0x02=4V, 0x03=4.5V, 0x04=5.5V, 0x05=6.5V`

`build_db.py` `VCC_VOLTAGES` (line 85): `{0x00: "5V", 0x01: "3.3V", 0x04: "5.5V", 0x05: "6.5V"}` — missing `0x02` and `0x03`. Any chip with VCC nibble `0x02` or `0x03` silently falls through to the dict's default `"5V"` (Python `.get(key, "5V")`), misreporting voltage. [VERIFIED: gitlab.com/DavidGriffith/minipro database.c#L130]

### BUG-3 / DEC-04: vcc/vdd field labels swapped — CONFIRMED

**Status:** CONFIRMED [VERIFIED: gitlab.com/DavidGriffith/minipro database.c]

Minipro `database.c` voltages unpacking (lines 921–923):
```c
device->voltages.vdd = (voltages >> 12) & 0x0f;   // bits 15-12 = VDD
device->voltages.vcc = (voltages >> 8) & 0x0f;    // bits 11-8  = VCC
device->voltages.vpp = voltages & 0xff;            // bits 7-0   = VPP
```

`build_db.py` lines 510–511:
```python
"vdd": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),    # WRONG: reads VCC position
"vcc": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),   # WRONG: reads VDD position
```

The labels are inverted. Correct: `vdd` uses `>>12`, `vcc` uses `>>8`. This matches `pack_voltages()` at lines 680–685:
```c
voltages->raw_voltages = (voltages->raw_voltages & MP_VOLTAGE_MASK) |
    (voltages->vdd << 12) | (voltages->vcc << 8) | voltages->vpp;
```

**Functional impact in current DB:** `DS1225(RW)` stored as `vdd=3.3V, vcc=5V` — correct labels would be `vdd=5V, vcc=3.3V`. `AM28C16A` stored as `vdd=5.5V, vcc=3.3V` — correct labels would be `vdd=3.3V, vcc=5.5V`. Low runtime impact today (most chips are 5V/5V and both labels happen to be correct), but wrong for anything with differing VCC/VDD. [VERIFIED: gitlab.com/DavidGriffith/minipro database.c#L921]

### BUG-4 / DEC-05: PROTOCOL_MAP wrong names — CONFIRMED

**Status:** CONFIRMED [VERIFIED: gitlab.com/DavidGriffith/minipro database.h]

Complete IC2_ALG table from `database.h` lines 24–77 (commit `a8efaedc`):

| protocol_id | IC2_ALG Constant | build_db.py PROTOCOL_MAP Label | Status |
|-------------|-----------------|-------------------------------|--------|
| 0x05 | IC2_ALG_F29EE | FLASH_AMD_STD | Correct (functional name) |
| 0x06 | IC2_ALG_W29F32P | FLASH_AMD_ALT | Correct (functional name) |
| 0x07 | IC2_ALG_ROM28P_1 | EPROM_STD | Correct (functional name) |
| 0x08 | IC2_ALG_ROM32P | EPROM_QUICK | Correct (functional name) |
| 0x0B | IC2_ALG_ROM24P_1 | EPROM_LEGACY | Correct (functional name) |
| 0x0D | IC2_ALG_EE28C32P | EEPROM_POLL | Correct (functional name) |
| 0x0E | IC2_ALG_RAM32_1 | SRAM_32PIN | Correct (functional name) |
| 0x10 | IC2_ALG_28F32P | FLASH_INTEL | Correct (functional name) |
| 0x11 | IC2_ALG_FWH | FLASH_FWH | Correct label; wrong exclusion (not in KNOWN_PROTOCOLS — correct; but should have exclusion comment) |
| 0x27 | IC2_ALG_ROM24P_2 | SRAM_24PIN | Mislabeled (it's ROM24P_2 but routes to SRAM via fm1608 override — label is functional, not canonical) |
| 0x28 | IC2_ALG_ROM28P_2 | SRAM_STD | Mislabeled (same: ROM28P_2, functional SRAM after fm1608 override) |
| 0x29 | IC2_ALG_RAM32_2 | SRAM_512K_1M | Correct (functional name) |
| **0x2A** | **IC2_ALG_GAL16** | **NVRAM_32PIN (WRONG)** | GAL16V8 PLD algorithm — zero DIP memory chips |
| **0x2B** | IC2_ALG_GAL20 | (not in PROTOCOL_MAP) | GAL20V8 PLD — not relevant |
| **0x2C** | **IC2_ALG_GAL22** | **NVRAM_TIMEKEEPER (WRONG)** | GAL22V10 PLD algorithm — zero DIP memory chips |
| 0x2D | IC2_ALG_NAND | (not in PROTOCOL_MAP) | NAND flash — not relevant |
| **0x2E** | **IC2_ALG_PIC32X_2** | **NVRAM_512K (WRONG)** | PIC32 MCU algorithm — zero DIP memory chips |
| **0x35** | **IC2_ALG_ITE** | **FLASH_EEPROM_LIKE (WRONG)** | ITE IT8xxx EC MCU — TQFP128, zero DIP memory chips; in KNOWN_PROTOCOLS (wrong) |
| **0x39** | **(NO IC2_ALG CONSTANT)** | **FLASH_INTEL_ALT (PHANTOM)** | 0x39 has no IC2_ALG define in database.h; unreachable from INFOIC2PLUS; in KNOWN_PROTOCOLS (wrong) |
| **0x3C** | **(NO IC2_ALG CONSTANT)** | **FLASH_4MB (INVENTED)** | Not in IC2_ALG table; not in KNOWN_PROTOCOLS; no chips |

**Correction required for dictionary (DEC-05):**
- 0x2A: canonical name = `IC2_ALG_GAL16` — GAL16V8 PLD algorithm; no DIP memory chips; exclude
- 0x2C: canonical name = `IC2_ALG_GAL22` — GAL22V10 PLD algorithm; no DIP memory chips; exclude
- 0x2E: canonical name = `IC2_ALG_PIC32X_2` — PIC32 MCU algorithm; no DIP memory chips; exclude
- 0x35: canonical name = `IC2_ALG_ITE` — ITE IT8xxx MCU; TQFP128; no DIP memory chips; remove from KNOWN_PROTOCOLS
- 0x39: no IC2_ALG constant; INFOIC2PLUS-unreachable phantom (appears only in legacy INFOIC for DIP40 27C1024); remove from KNOWN_PROTOCOLS
- 0x3C: invented; no IC2_ALG constant; no chips; not in KNOWN_PROTOCOLS; remove from PROTOCOL_MAP entirely

---

## Field Dictionary — Authoritative Attribute Reference

This section is the pre-cursor content the dictionary file will contain. Each attribute is marked CONFIRMED / INFERRED / UNKNOWN against minipro source.

**Citation commit:** `a8efaedc236c1d9718bd28299dfbb99536b010ff` (2026-03-23, "infoic: Correct ATMEGA328PB fuse defaults")
**Permalink base:** `https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc236c1d9718bd28299dfbb99536b010ff/`

### `package_details` (uint32 hex) — CONFIRMED

Source: `database.c` lines 618–703 [VERIFIED: gitlab.com/DavidGriffith/minipro database.c]

```
Bit  31     0x80000000   SMD flag (surface-mount) — is_smd
Bits 29-24  0x3F000000   Raw pin count (6-bit field; build_db uses 0x7F000000 which is harmless for DIP)
Bits 15-8   0x0000FF00   ICSP serial-interface index — is_serial (non-zero = exclude)
Bits 7-0    0x000000FF   Adapter type (0x00 = DIP native)
```

PLCC adapters remap pin count: ADAPTER 0x38→20, 0x3E→28, 0x3F→32, 0x3D→44.
`build_db.py` usage: filter `24 <= pin_count <= 32`, `is_smd == 0`, `is_serial == 0`, `type_int in [1, 4]` — correct.

### `type` (uint32 hex) — CONFIRMED

Source: `database.c` line 583; constants in `minipro.h` [VERIFIED: gitlab.com/DavidGriffith/minipro database.c]

| Value | Constant | Meaning |
|-------|----------|---------|
| 0x01 | MP_MEMORY | ROM/EPROM/Flash/EEPROM (parallel memory) |
| 0x02 | MP_MCU | Microcontroller |
| 0x03 | MP_PLD | Programmable logic device (GAL, CPLD) |
| 0x04 | MP_SRAM | SRAM / NVRAM / FRAM |
| 0x05 | MP_LOGIC | Logic IC (logicic.xml, not infoic.xml) |

`build_db.py` filters `type_int in [1, 4]` — correct for Firestarter scope.
Safety guard: `type_int == 4` with EPROM-family `protocol_id` → `fm1608` override; `type_int == 3` (PLDs) are filtered before reaching KNOWN_PROTOCOLS check.

### `protocol_id` (uint8 hex) — CONFIRMED

Source: `database.c` line 685; IC2_ALG_* constants in `database.h` lines 24–77 [VERIFIED: gitlab.com/DavidGriffith/minipro database.h]

The full IC2_ALG table is documented in the D-11 BUG-4 section above. Firestarter-relevant subset reaching INFOIC2PLUS DIP-24..32 filter:

| protocol_id | IC2_ALG Constant | Firestarter Handler | Notes |
|-------------|-----------------|---------------------|-------|
| 0x05 | IC2_ALG_F29EE | configure_flash4 | AMD/Fujitsu 5V page-write flash |
| 0x06 | IC2_ALG_W29F32P | configure_flash3 | Winbond/SST AMD-unlock 5V flash |
| 0x07 | IC2_ALG_ROM28P_1 | configure_eprom | 28-pin UV-EPROM primary; some EEPROMs mistagged here |
| 0x08 | IC2_ALG_ROM32P | configure_eprom | 32-pin UV-EPROM (27C010/020/040) |
| 0x0B | IC2_ALG_ROM24P_1 | configure_eprom | 24-pin legacy EPROM (2716/2732) |
| 0x0D | IC2_ALG_EE28C32P | configure_eeprom28c | 28/32-pin 5V EEPROM (28C-series, DQ7 poll) |
| 0x0E | IC2_ALG_RAM32_1 | configure_sram | 32-pin SRAM type 1 |
| 0x10 | IC2_ALG_28F32P | configure_flash_intel | Intel 28F parallel flash (12V VPP, cmd register) |
| 0x27 | IC2_ALG_ROM24P_2 | configure_sram | 24-pin SRAM (6116 family); fm1608 override in effect |
| 0x28 | IC2_ALG_ROM28P_2 | configure_sram | 28-pin SRAM; also target of fm1608/WARNING-5 overrides |
| 0x29 | IC2_ALG_RAM32_2 | configure_sram | 32-pin SRAM 512K/1M |

**Out-of-scope / excluded IDs (with rationale):**
- 0x11 (IC2_ALG_FWH): Intel LPC 4-wire serial bus + 3.3V VCC — not parallel, not 5V; infeasible on RURP
- 0x2A (IC2_ALG_GAL16): GAL16V8 PLD algorithm — `type=3`, zero DIP memory chips
- 0x2C (IC2_ALG_GAL22): GAL22V10 PLD algorithm — `type=3`, zero DIP memory chips
- 0x2E (IC2_ALG_PIC32X_2): PIC32 MCU algorithm — `type=2`, zero DIP memory chips
- 0x35 (IC2_ALG_ITE): ITE IT8xxx EC MCU — TQFP128, `type=2`, zero DIP memory chips
- 0x39 (no IC2_ALG): phantom — no constant in database.h; INFOIC2PLUS-unreachable
- 0x3C (no IC2_ALG): invented — not in minipro source at all

### `flags` (uint32 hex) — CONFIRMED for decoded bits; UNKNOWN for bits 3/6/7

Source: `database.c` lines 39–50 [VERIFIED: gitlab.com/DavidGriffith/minipro database.c#L39]

**Source-confirmed bits (CONFIRMED):**

| Bit | Mask | MP_* Constant | Meaning |
|-----|------|---------------|---------|
| 1 | 0x00000002 | MP_REVERSED_PACKAGE | Package pin numbering is reversed |
| 4 | 0x00000010 | MP_ERASE_MASK | **Can be electrically erased** (the "electrically erasable" discriminator; build_db correctly uses `flags & 0x10` for `_etype`) |
| 5 | 0x00000020 | MP_ID_MASK | Has readable manufacturer/device chip ID |
| 12 | 0x00001000 | MP_DATA_MEMORY_ADDRESS | Has data memory offset |
| 13 | 0x00002000 | MP_DATA_BUS_WIDTH (alias MP_DATA_ORG) | Data bus width: 0=8-bit, 1=16-bit |
| 14 | 0x00004000 | MP_OFF_PROTECT_BEFORE | Off-protection before operation |
| 15 | 0x00008000 | MP_PROTECT_AFTER | Protect after operation |
| 18 | 0x00040000 | MP_LOCK_BIT_WRITE_ONLY | Lock-bit is write-only |
| 19 | 0x00080000 | MP_CALIBRATION | Has calibration data |
| 20-21 | 0x00300000 | MP_SUPPORTED_PROGRAMMING | Programming support level |

**NOT decoded in database.c — meaning UNKNOWN:**

| Bit | Mask | Current docs claim | Correct statement |
|-----|------|--------------------|-------------------|
| 3 | 0x00000008 | "Requires VPP (High Programming Voltage)" | UNKNOWN — not a defined MP_* constant in database.c |
| 6 | 0x00000040 | "Is UV-erasable EPROM" | UNKNOWN — not a defined MP_* constant in database.c |
| 7 | 0x00000080 | "Is Electrically Erasable or Writable" | UNKNOWN — not a defined MP_* constant in database.c; this is likely a TL866II+ firmware-internal bit forwarded raw |

The full 32-bit `flags` value is forwarded to TL866II+ firmware. Bits 3/6/7 may have meaning to the closed-source TL866II+ firmware but are NOT documented in the open minipro source. The existing docs' meanings for these bits are INFERRED from observed chip patterns, not source-confirmed.

**Critical correction for DOC-02/DOC-01:** Bit 4 (`MP_ERASE_MASK = 0x00000010`) means "can be electrically erased." The current docs label it "Requires Write Enable Sequence" — this is wrong. It is the discriminator used by WARNING-5 in `build_db.py` (`flags & 0x10`) to distinguish 5V EEPROMs from UV-EPROMs when both share `protocol_id=0x07`.

### `voltages` (uint32 hex) — CONFIRMED

Source: `database.c` lines 921–923 and 680–685 [VERIFIED: gitlab.com/DavidGriffith/minipro database.c#L921]

```
Bits 7-0   VPP byte     device->voltages.vpp = voltages & 0xff
Bits 11-8  VCC nibble   device->voltages.vcc = (voltages >> 8) & 0x0f
Bits 15-12 VDD nibble   device->voltages.vdd = (voltages >> 12) & 0x0f
```

**VPP byte → millivolts** (VPP_MV in build_db.py — CONFIRMED correct):
0x00=12V, 0x10=9V, 0x20=9.5V, 0x30=10V, 0x40=11V, 0x50=11.5V, 0x60=12.5V, 0x70=13V, 0x80=13.5V, 0x90=14V, 0xA0=14.5V, 0xB0=15.5V, 0xC0=16V, 0xD0=16.5V, 0xE0=17V, 0xF0=18V

**VCC/VDD nibble → voltage** (from `tl866ii_vcc_voltages[]` — CONFIRMED):
0x00=5V, 0x01=3.3V, **0x02=4V (MISSING from build_db.py)**, **0x03=4.5V (MISSING from build_db.py)**, 0x04=5.5V, 0x05=6.5V

**BUG-3 note:** `build_db.py` has the nibble positions swapped. Correct: `vcc=(voltages>>8)&0x0F`, `vdd=(voltages>>12)&0x0F`. This is the Phase 57 code fix; the dictionary states the CORRECT semantics.

### `variant` (uint32 hex) — CONFIRMED

Source: `database.c` line 585 [VERIFIED: gitlab.com/DavidGriffith/minipro database.c]

Low byte = sub-algorithm/variant index sent to programmer; bits 15-8 = T56/T76 name index (irrelevant on RURP). `build_db.py` correctly uses `variant & 0xFF`.

DIP28 UV-EPROM `variant_lo` sub-discriminator (CONFIRMED from chip survey):
- 0x10 → DIP28_27512 (27C512, VPP on pin 22)
- 0x11 → DIP28_27256 (27C256, VPP on pin 1)
- 0x12 → DIP28_2764 (27C128)
- 0x13 → DIP28_2764 (27C64/2764A)
- else → DIP28_2764 (default)

DIP24 `variant_lo`: 0x00=DIP24_2716, 0x01=DIP24_2732.

### `pin_map` (uint32 hex) — CONFIRMED

Source: `database.c` lines 608–617 [VERIFIED: gitlab.com/DavidGriffith/minipro database.c]

Low byte (`pm_idx`) = pin-test map index; clusters chips by physical layout family. Upper bits:
- 0x10000000 = T56_FLAG
- 0x20000000 = TL866II_FLAG (note: TL866II_FLAG=0 does NOT mean unprogrammable on TL866II+)
- 0x40000000 = T48_FLAG

`build_db.py` `pm_idx = pin_map_raw & 0xFF` — correct.

### `pulse_delay` (uint32 hex) — CONFIRMED

Source: `database.c` line 866 [VERIFIED: gitlab.com/DavidGriffith/minipro database.c#L866]

**Raw value is microseconds for ALL protocols, no transformation.** Minipro loads the field directly into `device->pulse_delay` with no multiplication or protocol-conditional conversion.

Verified values:
- AM27C64: 0x64 = 100µs
- W27C512: 0x64 = 100µs
- AM2716: 0x1F4 = 500µs
- AT28C256: 0x2710 = 10000µs = 10ms

**BUG-2:** `build_db.py` `interpret_timing()` applies ×100 for `0x07` and `0x0B` — WRONG. The dictionary states: raw value = µs directly. Phase 57 removes the multiplier.

### `chip_id` (uint32 hex) — CONFIRMED

Source: `database.c` lines 600, 561 [CITED: gitlab.com/DavidGriffith/minipro database.c]

Raw silicon manufacturer/device ID. `0` = no ID. ID check gated by `flags & MP_ID_MASK (0x20)`. `build_db.py` usage: `chip_id_check = True if (flags & 0x20) else False` — correct.

### `code_memory_size` (uint32 hex) — CONFIRMED

Source: `database.c` line 592 [CITED: gitlab.com/DavidGriffith/minipro database.c]

Total addressable bytes. 27C512 = 0x10000 = 65536. Used as firmware `memory-size`. `build_db.py` usage: `mem_size = int(ic.get("code_memory_size"), 16)` — correct.

### `page_size` (uint32 hex) — CONFIRMED

Source: `database.c` line 598 [CITED: gitlab.com/DavidGriffith/minipro database.c]

Page-write size for EEPROM/Flash. Typically 64 or 128 for 28C-family; 0 or 1 if not applicable. Not currently stored by `build_db.py`.

### `chip_info` (uint32 hex) — CONFIRMED

Source: `database.c` line 605 [CITED: gitlab.com/DavidGriffith/minipro database.c]

Opaque discriminator: 0x0006=`MP_VOLTAGES1` (adjustable VCC), 0x0007=`MP_VOLTAGES2` (adjustable VPP), else MCU-specific. ~0x0000 for standard parallel memory. Not stored by `build_db.py` today.

### `blank_value` (uint8 hex, optional) — CONFIRMED

Source: `database.c` lines 627–631 [CITED: gitlab.com/DavidGriffith/minipro database.c]

Erased-read byte; default 0xFF when absent. Not stored by `build_db.py` today.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Minipro source lookups | Re-derive from memory or web search | Direct WebFetch from pinned GitLab permalink | Source can be fetched in seconds; memory has 6-18 month lag |
| Baseline snapshot | Custom snapshot tooling | `git diff` of committed `chip_database.json` | Git already provides line-level diff for JSON |
| Per-chip diff for GATE-02 | ad-hoc JSON compare | `git diff` on `chip_database.baseline.json` vs regenerated DB | Phase 59 can use standard JSON diff tooling |
| Doc table formatting | Custom markdown generator | Write markdown tables directly | Docs are static reference tables; no code generation needed |

---

## Common Pitfalls

### Pitfall 1: Overstepping into Phase 57

**What goes wrong:** The executor, while writing the dictionary's "correct semantics" section for BUG-1..4, also edits `build_db.py` to fix the bugs.
**Why it happens:** It feels natural to fix a bug while documenting it.
**How to avoid:** Phase 56 scope is explicitly DOC-only. `build_db.py` must have zero decode-behavior changes. The dictionary is the authority Phase 57 cites — if Phase 56 changes the code, Phase 57 has nothing to fix and GATE-02 regression baseline is corrupted.
**Warning signs:** Any edit to `build_db.py` lines 75–92 (VCC_VOLTAGES, VPP tables) or 268–284 (interpret_timing) during Phase 56 execution.

### Pitfall 2: Stating Inferred Bits as Confirmed in the Dictionary

**What goes wrong:** Bits 3/6/7 of `flags` are documented with confident "Means X" statements because that's what the existing docs say.
**Why it happens:** The existing `package-details.md` and `protocol-flags.md` present these as known facts.
**How to avoid:** Only bits with a corresponding `MP_*` constant in `database.c` lines 39–50 are CONFIRMED. Bits 3, 6, 7 have no MP_* constant and must be labelled UNKNOWN. The TL866II+ firmware uses them internally but the minipro open-source code does not decode them.
**Warning signs:** Dictionary entries for bits 3/6/7 without "UNKNOWN" marker.

### Pitfall 3: vcc/vdd swap in the dictionary itself

**What goes wrong:** The dictionary states the WRONG (current build_db.py) semantics instead of the correct minipro semantics.
**Why it happens:** Copying from `build_db.py` rather than from minipro source.
**How to avoid:** Dictionary states the CORRECT decode: `vcc` at bits 11-8 (`>>8`), `vdd` at bits 15-12 (`>>12`). The code is wrong; the dictionary documents what it SHOULD be. Phase 57 then fixes the code to match.

### Pitfall 4: Incorrect logo-header format (D-09)

**What goes wrong:** Rewritten doc uses a different image path, alt text, or wrapper tag format than the original.
**Why it happens:** Free-form rewrite forgets to preserve the exact HTML block.
**How to avoid:** Copy the exact logo block from each existing doc as line 1 of the rewrite:
```html
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>
```

### Pitfall 5: Baseline committed after code edits begin

**What goes wrong:** Phase 56 commits the baseline AFTER some test code changes have already been made.
**Why it happens:** Order inversion — coding first, then "snapshotting."
**How to avoid:** Snapshot must be the FIRST commit of Phase 56, on the beta branch, with no intermediate changes. The planner should place the baseline commit as Wave 0 / Plan 1.

### Pitfall 6: Using a stale minipro master SHA for citations

**What goes wrong:** The dictionary cites a SHA that predates key source details that were verified in this research.
**Why it happens:** The research used SHA `a8efaedc236c1d9718bd28299dfbb99536b010ff` (2026-03-23); the executor might use a different or older SHA.
**How to avoid:** The planner should record SHA `a8efaedc236c1d9718bd28299dfbb99536b010ff` as the citation SHA in the plan. All permalink URLs must use this SHA. The executor verifies lines against this exact commit, not master.

### Pitfall 7: 0x39 described as a valid protocol

**What goes wrong:** The rewritten `protocol-id.md` still lists 0x39 as "FLASH_INTEL_ALT" for AT49F040.
**Why it happens:** The existing doc is wrong; copying it perpetuates the error.
**How to avoid:** 0x39 has no IC2_ALG constant in `database.h`. It appears in the legacy INFOIC (not INFOIC2PLUS) for DIP40 chips. The rewrite must label it PHANTOM/UNREACHABLE with an explicit exclusion note.

---

## Code Examples

### Correct voltages decode (what the dictionary documents; what Phase 57 implements)

```python
# Source: minipro/src/database.c lines 921-923 @ a8efaedc
# device->voltages.vdd = (voltages >> 12) & 0x0f;   // bits 15-12
# device->voltages.vcc = (voltages >> 8) & 0x0f;    // bits 11-8
# device->voltages.vpp = voltages & 0xff;            // bits 7-0

# Correct Python (Phase 57 fix target):
"vdd": VCC_VOLTAGES.get((voltages >> 12) & 0x0F, "5V"),  # bits 15-12
"vcc": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, "5V"),   # bits 11-8
```

### Correct VCC_VOLTAGES table (what the dictionary documents; what Phase 57 adds)

```python
# Source: minipro/src/database.c tl866ii_vcc_voltages[] lines 130-135 @ a8efaedc
VCC_VOLTAGES = {
    0x00: "5V",
    0x01: "3.3V",
    0x02: "4V",    # MISSING from current build_db.py
    0x03: "4.5V",  # MISSING from current build_db.py
    0x04: "5.5V",
    0x05: "6.5V",
}
```

### Correct pulse_delay (what the dictionary documents; what Phase 57 implements)

```python
# Source: minipro/src/database.c line 866 @ a8efaedc
# pulse_delay stored directly in device->pulse_delay without transformation
# Raw value IS microseconds for ALL protocols

# Correct Python (Phase 57 fix target — removes x100 multiplier):
def interpret_timing(raw_hex, protocol_id):
    try:
        val = int(raw_hex, 16)
    except:
        val = 0
    if protocol_id in (0x07, 0x08, 0x0B):
        return f"{val} us"   # NOT val * 100
    return "Algorithm Controlled"
```

### Logo-header block to preserve (D-09)

```html
<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>
```

---

## State of the Art

| Old Approach (current docs) | Correct Approach (dictionary + rewrites) | When Changed | Impact |
|----------------------------|------------------------------------------|--------------|--------|
| 0x2A/0x2C/0x2E labeled NVRAM | IC2_ALG_GAL16/GAL22/PIC32X_2 — PLDs/MCUs | Phase 56 dict | Prevents future confusion; removes phantom NVRAM expansion work |
| 0x39 described as AT49F040 "advanced flash" | PHANTOM — no IC2_ALG constant; INFOIC2PLUS-unreachable | Phase 56 dict | Eliminates critical error in existing doc |
| 0x3C listed as FLASH_4MB protocol | INVENTED — remove from PROTOCOL_MAP | Phase 56 dict | Removes non-existent entry |
| Bit 4 = "Requires Write Enable Sequence" | MP_ERASE_MASK = "can be electrically erased" | Phase 56 doc rewrite | Correctly names the WARNING-5 discriminator |
| Bits 3/6/7 stated as confirmed meanings | UNKNOWN — no MP_* constant in database.c | Phase 56 dict | Honest uncertainty; prevents future misuse |
| VCC_VOLTAGES missing 0x02/0x03 | Correct table with all 6 nibbles | Phase 57 code (Phase 56 documents) | AT28C256 and 4V/4.5V chips decoded correctly |
| vdd/vcc label swap | Correct: vcc=bits 11-8, vdd=bits 15-12 | Phase 57 code (Phase 56 documents) | NVRAM/low-voltage chips get correct voltage labels |
| pulse_duration ×100 for 0x07/0x0B | Raw µs, no multiplier | Phase 57 code (Phase 56 documents) | W27C512 shows 100µs not 10000µs |

---

## Project Constraints (from CLAUDE.md)

Per `firestarter_app/CLAUDE.md`:

- **WARNING-5 override** (`DIP28_2764` + `0x07` + Flash/EEPROM → `0x0D`): This load-bearing safety logic must NOT be touched. The dictionary's `flags` entry documents that bit 4 (`MP_ERASE_MASK`) is the discriminator — this is CONSISTENT with WARNING-5's `flags & 0x10` predicate. No conflict.
- **`chip_database.json` — do NOT edit by hand**: The baseline snapshot is created by running `python tools/build_db.py` (live fetch from upstream master), then committing the output. The executor must NOT hand-edit the JSON.
- **Constants sync**: `firestarter/constants.py` ↔ `firestarter/include/firestarter.h` — not applicable to Phase 56 (no constant changes).
- **CI gates**: `ruff check`, `ruff format --check`, `mypy`, `pytest --cov-fail-under=70` — Phase 56 adds only `.md` files and commits an existing `.json`. The CI gate should not be affected. Verify before closing.

Per `/workspaces/CLAUDE.md` (meta-repo):
- Phase 56 is HOST-ONLY (`firestarter_app/` sub-repo). Firmware sub-repo (`firestarter/`) is untouched.
- The sub-repo works on the `beta` branch (confirmed: `cd firestarter_app && git branch --show-current` = `beta`).

---

## Runtime State Inventory

> Phase 56 is a documentation + snapshot phase with no rename/refactor/migration. This section is included to explicitly state: no runtime state is modified.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — chip_database.json is regenerated from scratch; no user data store involved | None |
| Live service config | None — no external service configuration | None |
| OS-registered state | None | None |
| Secrets/env vars | None — no new secrets; MINIPRO_XML_URL is a public GitLab URL already in code | None |
| Build artifacts | `chip_database.json` — re-committed as baseline, content unchanged | Commit as-is; do not regenerate unless verifying freshness |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.x | `build_db.py` regeneration | Yes | 3.12.13 | — |
| `requests` library | `build_db.py` XML fetch | Yes | confirmed | — |
| `git` | Committing baseline + docs | Yes | 2.54.0 | — |
| Network (gitlab.com) | `build_db.py` live fetch | Expected | — | Use existing `chip_database.json` without re-run if offline |
| minipro GitLab (for citations) | infoic-field-dictionary.md authoring | Yes (WebFetch verified) | Commit `a8efaedc` | — |

**Missing dependencies:** None blocking.

---

## Validation Architecture

> `workflow.nyquist_validation` is absent from `.planning/config.json` — treating as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | `firestarter_app/pytest.ini` or project-level (uses pytest discovery) |
| Quick run command | `cd firestarter_app && python -m pytest tests/ -x -q` |
| Full suite command | `cd firestarter_app && python -m pytest tests/ --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GATE-01 | Baseline file exists at committed path | smoke | `test -f firestarter_app/tools/baseline/chip_database.baseline.json` (shell check) | No — new file |
| DEC-01 | Dictionary file exists with all 13 attributes | smoke | `test -f firestarter_app/doc/infoic-field-dictionary.md` | No — new file |
| DOC-01 | `package-details.md` is rewritten | smoke | `grep -q "UNKNOWN" firestarter_app/doc/package-details.md` | Existing file |
| DOC-02 | `protocol-flags.md` is rewritten | smoke | `grep -q "MP_ERASE_MASK\|can_erase" firestarter_app/doc/protocol-flags.md` | Existing file |
| DOC-03 | `protocol-id.md` is rewritten | smoke | `grep -q "IC2_ALG\|phantom\|PHANTOM" firestarter_app/doc/protocol-id.md` | Existing file |
| DEC-03/04/05 | Dictionary contains correct semantics (code unchanged) | manual-review | Review against §D-11 in this research doc | N/A |
| CI gate | All existing tests still pass | regression | `cd firestarter_app && python -m pytest tests/ --cov-fail-under=70` | ✅ Existing |

**Note on automated coverage:** Phase 56 produces only `.md` and `.json` files — no Python code changes. Existing test suite (734-chip characterization, WARNING-5 regression, check_dispatch) should remain green without modification. The planner should include a CI green check as a wave-close verification step, not a new test file.

### Wave 0 Gaps

- No test file gaps — Phase 56 has no new Python code to unit test.
- Shell smoke checks for new file existence can be added inline in plan tasks (no separate test file needed).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | minipro commit `a8efaedc236c1d9718bd28299dfbb99536b010ff` (2026-03-23) is an appropriate citation anchor for all cited source lines | D-11, Field Dictionary | If the line numbers have drifted in this commit vs an older one the permalinks might point to wrong lines — LOW risk since we verified the content matches expected |
| A2 | The `firestarter_app` sub-repo beta branch will remain at its current state until Phase 56 execution begins | Baseline snapshot | If unexpected commits land before Phase 56 starts, the baseline may not reflect the exact pre-milestone state |
| A3 | `build_db.py` `python tools/build_db.py` regeneration produces the same 734-chip DB given unchanged upstream master (no upstream drift) | Baseline snapshot | Upstream master could add/change chips; if the live run produces a different count, the baseline snapshot plan should note the actual count at commit time |

---

## Open Questions (RESOLVED)

1. **Baseline snapshot path — `tools/baseline/` vs `.planning/v1.11/`**
   - What we know: Both paths are technically valid; D-03 leaves the exact path to the planner/executor.
   - What's unclear: Whether the baseline should be inside the `firestarter_app` sub-repo (closer to the generator) or in the meta-repo `.planning/` artifacts.
   - Recommendation: Use `firestarter_app/tools/baseline/chip_database.baseline.json`. The directory is co-located with the generator tool; Phase 59's diff script can reference it with a relative path; it stays in the sub-repo git history where it's most useful.

2. **Whether to add a `.gitkeep` or README to `tools/baseline/`**
   - What we know: The directory does not currently exist.
   - Recommendation: No extra file needed. The baseline JSON itself creates the directory, and its purpose is self-evident from the filename.

3. **Dictionary attribute table layout (discretionary per D-03)**
   - Recommendation: One H3 section per attribute with: source citation, bit layout table, CONFIRMED/INFERRED/UNKNOWN status, `build_db.py` usage note, and BUG note if applicable. This mirrors the structure already proven in `.planning/research/STACK.md` and makes Phase 57 citable by attribute name.

---

## Security Domain

> Phase 56 is documentation-only. No new code paths, no authentication, no input validation, no cryptography. Security domain is not applicable.

---

## Sources

### Primary (HIGH confidence)

- `gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc.../src/database.c` — tl866ii_vcc_voltages[], voltages unpacking (lines 921-923), pack_voltages() (lines 680-685), pulse_delay loading (line 866), type constants (line 583), flags constants (lines 39-50)
- `gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc.../src/database.h` — IC2_ALG_* constants (lines 24-77), T56_FLAG / TL866II_FLAG / T48_FLAG
- `/workspaces/firestarter_app/tools/build_db.py` — current PROTOCOL_MAP (lines 25-44), VCC_VOLTAGES (line 85), VPP_MV (lines 76-81), KNOWN_PROTOCOLS (line 83), interpret_timing (lines 268-284), voltages extraction (lines 510-511)
- `/workspaces/firestarter_app/firestarter/data/chip_database.json` — 734 chips, 58 manufacturers; pulse_duration values confirming BUG-2 live; vdd/vcc values confirming BUG-3 live
- `.planning/research/STACK.md` — per-attribute analysis from prior minipro clone reads (HIGH confidence; source-grounded)
- `.planning/research/FEATURES.md` — IC2_ALG protocol catalog and feasibility analysis (HIGH confidence; source-grounded)
- `.planning/phases/56-snapshot-field-dictionary-corrected-docs/56-CONTEXT.md` — locked decisions D-01 through D-11

### Secondary (MEDIUM confidence)

- `.planning/research/PITFALLS.md` — hazard model; SR-1..SR-6 checklist; WARNING-5 predicate analysis
- `.planning/research/ARCHITECTURE.md` — integration map; phase decomposition
- `/workspaces/firestarter_app/doc/protocol-id.md`, `protocol-flags.md`, `package-details.md` — current (incorrect) state of rewrite targets; confirmed errors catalogued

### Tertiary (LOW confidence)

- None — all D-11 OPEN items resolved from authoritative sources.

---

## Metadata

**Confidence breakdown:**
- D-11 open item resolutions: HIGH — all verified against WebFetch of pinned minipro commit `a8efaedc`
- Field dictionary attribute coverage: HIGH — 13 in-scope attributes sourced from database.c/database.h
- IC2_ALG canonical names: HIGH — verified from database.h complete constant table
- Baseline snapshot mechanics: HIGH — `build_db.py` well-understood; Python + requests present; 734 chips confirmed
- Doc rewrite corrections: HIGH — current errors confirmed from reading existing docs; corrections verified from source

**Research date:** 2026-06-08
**Valid until:** 2026-07-08 (minipro source permalinks are immutable; build_db.py stable; docs stable)

**minipro citation commit:** `a8efaedc236c1d9718bd28299dfbb99536b010ff` (2026-03-23)
**Permalink pattern:** `https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc236c1d9718bd28299dfbb99536b010ff/src/database.c#L{line}`
