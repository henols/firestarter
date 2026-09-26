# Phase 34: Shield-Version-Detect Design + Firmware Plumbing — Pattern Map

**Mapped:** 2026-05-25
**Files analyzed:** 11 (2 meta-repo doc fills + 3 firmware modifications + 3 host modifications + 3 optional Wave 0 artifacts)
**Analogs found:** 11 / 11

Phase 34 is structurally a **3-repo plumbing pass**: meta-repo `<!-- OWNED BY PHASE 34 — TBD -->` fills (§8 + §9), an in-place rework of `rurp_detect_hardware_revision()` + a one-line `case` addition + a `#define` triplet on the firmware side, and a Phase-33-substrate-mirroring Python-parity block + cosmetic `serial_comm.py` extension on the host side. Every pattern needed has already shipped in the codebase — Phase 33 is the structural precedent for the entire phase, including the gitignored baseline-hex + verifier-script wave-0 idiom (which Phase 34 inherits with the assertion swapped from "byte-identical cmp" to "delta-band check"). The Phase 33 §7 fill is the direct analog for the §8 + §9 fills.

This map points each planned file at the exact in-tree analog (line ranges + concrete excerpts) to copy from.

---

## File Classification

| New/Modified File | Role | Data Flow | Touch Kind | Closest Analog | Match Quality |
|-------------------|------|-----------|------------|----------------|---------------|
| `.planning/v1.7-SHIELD-REVS.md` §8 | meta-repo documentation (canonical schematic-delta narrative + per-rev R41 table) | n/a | FILL-IN-PLACE (replace `<!-- OWNED BY PHASE 34 — TBD -->` at line 135) | Same file §7 fill at `:105-131` (Phase 33 substrate — narrative paragraphs + per-rev table with footnote conventions + source-citation column) | exact — same TBD-marker-replacement pattern, same Markdown idioms |
| `.planning/v1.7-SHIELD-REVS.md` §9 | meta-repo documentation (per-rev ADC band table) | n/a | FILL-IN-PLACE (replace `<!-- OWNED BY PHASE 34 — TBD -->` at line 139) | Same file §7 alias table at `:113-131` (16 rows × 11 cols Markdown) + §1 inventory + §6 capability matrix | exact — same multi-column per-rev table convention with `not-present` / `✓` / `pending Phase 35` cell sentinels |
| `firestarter/include/rurp_shield.h` | firmware header (REVISION_* enum) | n/a | ADD-LINES (2 new `#define`s at `:30`) | Same file: existing `REVISION_0..REVISION_2_2` block at `:22-30` (Phase 33-survived enum block per Phase 33 D-03) | exact — same `#define REVISION_X N` shape, same `#ifdef HARDWARE_REVISION` gating |
| `firestarter/include/rurp_hw_rev_utils.h` | firmware header (detect logic + ctrl-reg mapper) | request-response (boot init) | MODIFY-IN-PLACE (rework `rurp_detect_hardware_revision()` body at `:42-59`; add `case REVISION_2_3:` arm to `rurp_map_ctrl_reg_for_hardware_revision()` at `:14-36`; leave `rurp_get_hardware_revision()` at `:61-67` UNCHANGED) | Same file: existing function bodies (the rework copies the digital-A3 + analog-A2 dispatch shape and extends it to a 4-arm if/else-if band-lookup chain) | exact — same `pinMode` + `analogRead` idiom, same `if/else-if/else` AVR-idiom for ADC band-decode (already the canonical shape on `:49` `< 1000` magic-number) |
| `firestarter/include/rurp_pinout.h` | firmware header (alias substrate) | n/a | ADD-LINES (3 new threshold `#define`s after `:47` inside `#ifdef HARDWARE_REVISION` block) | Same file: existing Section 1 PIN_* declarations at `:43-47` (Phase 33 substrate — `#define`-only constants under HARDWARE_REVISION gating) | exact — same `#define NAME VALUE` shape, same `#ifdef HARDWARE_REVISION` gate, Phase 33 D-07 `#define`-NOT-`constexpr` lock |
| `firestarter_app/firestarter/constants.py` | host CLI constants (Python mirror of firmware enum) | n/a | ADD-BLOCK (7 new constants in `# RURP Hardware Revisions` block) | Same file: existing `# RURP Control Register Bits` block at `:71-83` (Phase 33 substrate — section-comment header + `NAME = 0xNN` per line + `# was OLD_NAME` annotation pattern) | exact — same idiom: section header + one constant per byte-value + hex literals + sync-burden comment |
| `firestarter_app/firestarter/serial_comm.py` | host CLI service (`_format_message` MSG_OK_REV path) | request-response | MODIFY-IN-PLACE (extend lines `:336-340` with `_REVISION_SILKSCREEN` dict lookup) | Same file: existing `_format_message` MSG_OK_REV and MSG_OK_CFG sentinel-aware rendering at `:319-346` (Phase 33 P-02/P-03 substrate) | exact — same `if msg_id == MSG_OK_REV and len(params) == 2:` guard pattern, same 0xFF sentinel handling |
| `firestarter_app/CLAUDE.md` | host CLI documentation (sync-rule prose) | n/a | EXTEND-PROSE (one sentence appended to existing "Constants" subsection) | Same file: existing CTRL_* sync-rule sentence at `:100` (Phase 33 substrate added the first cross-repo parity declaration in this exact spot) | exact — same sentence shape, same "mirrors X in firmware sub-repo; keep in sync per CLAUDE.md sync rule" template |
| `.planning/v1.7/baseline-34/{uno,leonardo,uno328pb}.hex` | meta-repo tooling (gitignored Intel-HEX baselines) | file-I/O | CREATE-DIR + place 3 `.hex` snapshots | `.planning/v1.7/phase-33-baseline-hex/{uno,uno328pb,leonardo}.hex` (Phase 33 Plan 00 — captured pre-rename snapshots from `firestarter/.pio/build/<env>/firestarter_<env>.hex` via `cp` after clean rebuild) | exact — Phase 33 Plan 00 capture pattern is verbatim reusable; only the directory name and the post-Wave-2 assertion change |
| `.planning/v1.7/baseline-34/verify-detect-34.sh` | meta-repo tooling (wave-merge regression-guard) | file-I/O | CREATE (executable bash script with `set -euo pipefail` + 3 assertions) | `.planning/v1.7/phase-33-baseline-hex/check-migration.sh` (Phase 33 Plan 00 — grep-zero + REV_*-zero + 3x `cmp` byte-identical) | role-match — same wrapper idiom (assertions, `set -euo pipefail`, gitignored under `.planning/v1.7/`), but the `cmp` assertion swaps to a `[20, 300] B` delta-band `[ -ge ] [ -le ]` check on `wc -c` |
| `firestarter_app/tests/test_revision_constants_parity.py` | host CLI test (pytest parity assertion) | event-driven (test harness) | CREATE (1 test function asserting 7 known byte values) | `firestarter_app/tests/test_decoder.py` (existing pytest module testing wire-frame decode — same `from firestarter.constants import *` import pattern + module-scoped test functions) | role-match — same pytest module layout; new file is a single assertion function with no fixtures |

---

## Pattern Assignments

### 1. `.planning/v1.7-SHIELD-REVS.md` §8 (Detect-HW Schematic Delta — meta-repo doc fill)

**Role:** meta-repo documentation · **Data Flow:** n/a · **Touch:** FILL-IN-PLACE (replace `<!-- OWNED BY PHASE 34 — TBD -->` at line 135)

**Analog:** `.planning/v1.7-SHIELD-REVS.md` §7 fill at `:105-131` — the most recent OWNED-BY-PHASE TBD-marker-replacement (Phase 33 Plan 33-04 ALIAS-01). Established the convention for narrative paragraphs + per-rev tables + footnote citations.

**TBD-marker location** (exact lines to replace):
```markdown
## 8. Detect-HW Schematic Delta (next rev)

<!-- OWNED BY PHASE 34 — TBD -->
```
Lines 133–135. The `<!-- OWNED BY PHASE -->` HTML-comment marker convention is a v1.7-canonical-doc invariant — fill writes BETWEEN the heading line and the next `## ` heading (line 137).

**§7 narrative-paragraph + table pattern** (lines 107–112):
```markdown
Canonical map from every RURP-shield silkscreen / schematic-net label …
[2–3 narrative paragraphs lock the scope, schema, and provenance]

The canonical-alias namespace is split four ways per Open Question Q1 …

Label types: **`S`** = physically silkscreen-printed … **`N`** = schematic-net-only …
[cell-sentinel legend; source-citation format spec]

| col1 | col2 | … | source_citation |
|------|------|---|-----------------|
[N data rows]
```

**Source-evidence citation idiom** (carved from §7 row examples at `:115, :122, :130`):
- Schematic-net rows cite `mine-notes.md:NNN (Rev X.Y blob SHA line NNNN)` — per Phase 31 grep evidence at `mine-notes.md:434-510`.
- Silkscreen-printed rows cite `mine-notes.md:NNN ("%TO.C,DESIGNATOR*%" in Rev X.Y gerber)`.
- Code-side anchors cite `firestarter/include/rurp_pinout.h` (post-Phase-33 substrate).

**RESEARCH-supplied §8 content** (RESEARCH.md §8 Schematic Delta Documentation Surface lines 370–422 carries the exact narrative + ASCII schematic + per-rev R41 value table + JP4 caveat — planner copies that block verbatim into the §8 fill).

**Cell-sentinel conventions to preserve (from §7 row sentinel inventory)**:
- `not-present` — rev has no equivalent designator/bit
- `(inherits Rev 0)` — Modified Rev 0 cell unaffected by hardware-bug-A/B rework
- `as-modified — pending Phase 35` — Modified Rev 0 cell touched by rework
- `pending Phase 35` — operator-physical-measurement gates the value (e.g., Rev 2.2 R41 4k7-vs-10k discrepancy from §3 / §4 row 5)
- `✓` — applies as documented

---

### 2. `.planning/v1.7-SHIELD-REVS.md` §9 (Per-Rev Expected ADC Band Table — meta-repo doc fill)

**Role:** meta-repo documentation · **Data Flow:** n/a · **Touch:** FILL-IN-PLACE (replace `<!-- OWNED BY PHASE 34 — TBD -->` at line 139)

**Analog:** `.planning/v1.7-SHIELD-REVS.md` §7 alias table at `:113-131` (the 16-row × 11-col Phase 33 §7 fill is the direct shape analog) + §1 inventory + §6 capability matrix (both 9-column shield-rev tables).

**TBD-marker location** (exact lines to replace):
```markdown
## 9. Per-Rev Expected ADC Band Table

<!-- OWNED BY PHASE 34 — TBD -->
```
Lines 137–139. Per CONTEXT.md D-11, the 6-column shape is locked:

```markdown
| rev | r41_value | expected_adc_band (10-bit) | reported_enum | reported_silkscreen_string | source_evidence |
|-----|-----------|----------------------------|---------------|----------------------------|-----------------|
```

**§9 table pattern (RESEARCH-supplied)** — RESEARCH.md §9 Schema Refinement lines 426–443 provides the exact 6-row table body with band values derived from D-03 voltage math. Planner copies verbatim. Row sentinel reuse matches §7 conventions.

**Threshold-constant cross-link convention** (RESEARCH §9 lines 440–443):
```markdown
Note: the firmware threshold constants encode the band edges as follows:
- `ADC_BAND_R41_4K7_HIGH = 200` — upper edge of 4k7 bucket …
- `ADC_BAND_R41_10K_LOW = 220` — lower edge of 10k bucket …
- `ADC_BAND_R41_10K_HIGH = 600` — upper edge of 10k bucket …
```
Footnote-style narrative AFTER the table. Mirrors §7's pitfall callouts at `:116` (`Pitfall 1 — aliased to CTRL_ADDRESS_LINE_16 in legacy non-HARDWARE_REVISION branch`).

---

### 3. `firestarter/include/rurp_shield.h` (REVISION_* enum extension)

**Role:** firmware header · **Data Flow:** n/a · **Touch:** ADD-LINES (2 new `#define`s at `:30`, between `REVISION_2_2 = 4` and `#endif`)

**Analog:** Same file `:22-30` — existing `REVISION_0..REVISION_2_2` enum block, Phase 33-survived per D-03 alias-scoping. The block is gated by `#ifdef HARDWARE_REVISION`.

**Existing enum block** (lines 22–30, verbatim):
```c
#ifdef HARDWARE_REVISION
// Hardware-revision enum values (out of D-03 alias-scope per Phase 33 RESEARCH —
// these are revision identifiers, not RURP-signal aliases).
#define REVISION_0 0
#define REVISION_1 1
#define REVISION_2_0 2
#define REVISION_2_1 3
#define REVISION_2_2 4
#endif
```

**Phase 34 extension pattern** (insert 2 lines after line 29, before the `#endif` at line 30):
```c
#define REVISION_2_3 5
#define REVISION_UNKNOWN 0xFE   // ADC band-gap fall-through; 0xFF reserved for EEPROM-override-absent sentinel
```

**Critical preservation** (per CONTEXT.md D-07 + RESEARCH.md §REVISION_UNKNOWN Non-Collision Audit):
- `0xFF` stays reserved as the EEPROM-override-absent sentinel (loaded-bearing at `rurp_hw_rev_utils.h:63`, `rurp_config_utils.cpp:37`, `hardware_operations.cpp:99,101,111,113`).
- `0xFE` is grep-clean — only existing occurrence is a CRC8 lookup-table byte at `rurp_serial_utils.cpp:120` (not a sentinel; no collision).
- Block stays under `#ifdef HARDWARE_REVISION` (native env continues to bypass).

---

### 4. `firestarter/include/rurp_hw_rev_utils.h` (detect-rev rework + ctrl-reg `case REVISION_2_3:` arm)

**Role:** firmware header (inlined dispatcher + boot init) · **Data Flow:** request-response (boot init populates static `revision`; called once per boot from `firestarter.cpp:39`) · **Touch:** MODIFY-IN-PLACE — rework function body at `:42-59`; add 1 case label at `:20`; leave `:61-67` UNCHANGED.

**Analog:** Same file — existing function bodies at `:14-36` (mapper) + `:42-59` (detect) + `:61-67` (override-aware getter).

**Existing `rurp_map_ctrl_reg_for_hardware_revision()` switch** (lines 14–36, verbatim):
```c
uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    uint8_t ctrl_reg = 0;
    uint8_t hw = rurp_get_hardware_revision();
    switch (hw) {
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2:
        ctrl_reg = data & (CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_ADDRESS_LINE_17 | CTRL_READ_WRITE | CTRL_VPP_REGULATOR_ENABLE);
        ctrl_reg |= data & CTRL_VPP_VPE_DROP_ENABLE ? CTRL_VPP_VPE_DROP_ENABLE_REV2 : 0;
        ctrl_reg |= data & CTRL_ADDRESS_LINE_16 ? CTRL_ADDRESS_LINE_16_REV2 : 0;
        ctrl_reg |= data & CTRL_ADDRESS_LINE_18 ? CTRL_ADDRESS_LINE_18_REV2 : 0;
        break;
    case REVISION_0:
    case REVISION_1:
        ctrl_reg = data;
        ctrl_reg |= data & CTRL_VPP_VPE_DROP_ENABLE ? CTRL_VPP_VPE_DROP_ENABLE_REV1 : 0;
        break;
    default:
        break;
    }
    return ctrl_reg;
}
```

**Phase 34 case-label extension** (single line insertion after `:20`, before the body at `:21`):
```c
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2:
    case REVISION_2_3:                              // <-- NEW (D-07 — ctrl-reg layout identical to REV_2_x per §4 row 6)
        ctrl_reg = data & (CTRL_VPP_A9_ENABLE | …)
```
`REVISION_UNKNOWN` deliberately NOT added to the switch — it falls through the existing `default: break;` arm → `ctrl_reg = 0` (fail-safe — no VPP enables, no VPE enables; matches current `0xFF` fall-through behavior).

**Existing `rurp_detect_hardware_revision()` body** (lines 42–59, verbatim — the rework rewrites the body but keeps the function signature):
```c
void rurp_detect_hardware_revision() {
    pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP);
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT_PULLUP);

    int value = digitalRead(PIN_HW_REVISION_DETECT_ADC);
    switch (value) {
    case 1:
        revision = analogRead(PIN_VPP_VOLTAGE_ADC) < 1000 ? REVISION_1 : REVISION_0;
        break;
    case 0:
        revision = REVISION_2_0;
        break;
    default:
        // Unknown hardware revision
        revision = 0xFF;     // <-- LATENT BUG: collides with EEPROM-override-absent sentinel
    }
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT);
}
```

**Phase 34 rework body** (RESEARCH §Reworked Body lines 175–202 — verbatim):
```c
void rurp_detect_hardware_revision() {
    pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP);
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT_PULLUP);

    // 8-sample averaging on the A3 detect divider to robustify against AVcc
    // switching noise (see Phase 34 RESEARCH §ADC Voltage Band Math).
    uint16_t adc_a3 = analog_read_avg8(PIN_HW_REVISION_DETECT_ADC);

    if (adc_a3 < ADC_BAND_R41_4K7_HIGH) {
        revision = REVISION_2_0;                // 4k7 bucket — broad Rev 2.0-class per D-04
    } else if (adc_a3 >= ADC_BAND_R41_10K_LOW && adc_a3 < ADC_BAND_R41_10K_HIGH) {
        revision = REVISION_2_3;                // 10k bucket
    } else if (adc_a3 >= ADC_BAND_R41_10K_HIGH) {
        // High band — no R41. Disambiguate Rev 0 vs Rev 1 via the legacy A2 divider check.
        revision = analogRead(PIN_VPP_VOLTAGE_ADC) < 1000 ? REVISION_1 : REVISION_0;
    } else {
        revision = REVISION_UNKNOWN;            // [ADC_BAND_R41_4K7_HIGH, ADC_BAND_R41_10K_LOW) guard gap
    }
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT);
}
```

**`analog_read_avg8()` helper pattern** (RESEARCH §8-Sample Averaging lines 126–135 — landed as a `static` inline above `rurp_detect_hardware_revision()`):
```c
static uint16_t analog_read_avg8(uint8_t pin) {
    uint16_t sum = 0;
    for (uint8_t i = 0; i < 8; i++) {
        sum += (uint16_t)analogRead(pin);
    }
    return (uint16_t)(sum >> 3);
}
```

**`rurp_get_hardware_revision()` UNCHANGED** (lines 61–67, leave verbatim — DETECT-FW-01 fall-through clause is satisfied by construction):
```c
uint8_t rurp_get_hardware_revision() {
    rurp_configuration_t* rurp_config = rurp_get_config();
    if (rurp_config->hardware_revision < 0xFF) {
        return rurp_config->hardware_revision;
    }
    return rurp_get_physical_hardware_revision();
}
```

**Critical preservation** (Pitfalls — pull from RESEARCH §Firmware Detection Logic Rework lines 204–211):
1. `analog_read_avg8(PIN_HW_REVISION_DETECT_ADC)` not `digitalRead` — the load-bearing D-06 change.
2. `if/else-if/else` chain not `switch` — digital switch can't express band-lookup (already the codebase idiom at `:49` `< 1000` magic-number).
3. Latent-bug cleanup: `default: revision = 0xFF;` → `else { revision = REVISION_UNKNOWN; }` — removes the `0xFF`-sentinel collision per D-07.
4. The `static uint8_t revision = 0xFF;` initializer at `:12` is dead-code in normal boot flow (overwritten before any caller reads it) — leave alone for byte-identical Wave 2 (or refactor to `REVISION_UNKNOWN` if planner wants symbolic consistency).

---

### 5. `firestarter/include/rurp_pinout.h` (ADC band threshold `#define`s)

**Role:** firmware header (alias substrate) · **Data Flow:** n/a · **Touch:** ADD-LINES (3 new `#define`s inside the `#ifdef HARDWARE_REVISION` block after `:47`)

**Analog:** Same file `:43-47` — existing Section 1 PIN_* declarations (Phase 33 substrate). Same `#define`-only constant idiom under `#ifdef HARDWARE_REVISION` gate.

**Existing Section 1 PIN_* block** (lines 41–47, verbatim):
```c
// ---- Section 1: Arduino-pin assignments (PIN_*) ------------------------

#define PIN_VPP_VOLTAGE_ADC A2

#ifdef HARDWARE_REVISION
#define PIN_HW_REVISION_DETECT_ADC A3
#endif
```

**Phase 34 extension** (RESEARCH §Pattern 1 lines 575–584 — insert AFTER line 47, BEFORE the start of `// ---- Section 2 …` at line 49):
```c
// ---- Section 1b: ADC voltage-band thresholds (HARDWARE_REVISION-gated) -------
// Used by rurp_detect_hardware_revision() in rurp_hw_rev_utils.h to map an
// 8-sample-averaged analogRead(PIN_HW_REVISION_DETECT_ADC) value to a REVISION_*
// enum byte. Math: see Phase 34 RESEARCH.md §ADC Voltage Band Math + the §9
// per-rev band table in .planning/v1.7-SHIELD-REVS.md.
#ifdef HARDWARE_REVISION
#define ADC_BAND_R41_4K7_HIGH   200   // upper edge of 4k7 bucket (Rev 2.0/2.1/2.2)
#define ADC_BAND_R41_10K_LOW    220   // lower edge of 10k bucket (Rev 2.3); [200, 220) → REVISION_UNKNOWN
#define ADC_BAND_R41_10K_HIGH   600   // upper edge of 10k bucket; above → high band / no R41
#endif
```

**Critical preservation** (per Phase 33 D-07 + RESEARCH.md §Pattern 1):
- `#define` NOT `constexpr` (AVR-objcopy `.hex` byte-identical math depends on preprocessor-level constants).
- Inside `#ifdef HARDWARE_REVISION` block (native env continues to bypass).
- Strict band ordering enforced numerically: `200 < 220 < 600` (per D-11).
- Co-located with `RES_HW_REVISION_DIVIDER` / `PIN_HW_REVISION_DETECT_ADC` aliases (per Claude's Discretion Option A; matches Phase 33 4-namespace lock).

---

### 6. `firestarter_app/firestarter/constants.py` (Python REVISION_* parity block)

**Role:** host CLI constants · **Data Flow:** n/a · **Touch:** ADD-BLOCK (7 new constants in a new `# RURP Hardware Revisions` section appended after `:83`)

**Analog:** Same file `:71-83` — the `# RURP Control Register Bits` block (Phase 33 D-08 substrate). Established the canonical "Python-mirror-of-C++-`#define`s" idiom for this codebase: section comment header + sync-burden prose + `NAME = 0xNN  # was OLD_NAME` annotation.

**Existing CTRL_* block** (lines 71–83, verbatim):
```python
# RURP Control Register Bits — mirror of firestarter/include/rurp_pinout.h
# Documentary only — Python does not write the control register directly
# (firmware owns that). Used by `firestarter dev registers --firestarter`
# and similar host-side helpers. Keep in sync per CLAUDE.md sync rule.
CTRL_VPP_VPE_DROP_ENABLE     = 0x100   # was VPE_TO_VPP (wide layout)
CTRL_VPP_REGULATOR_ENABLE    = 0x080   # was REGULATOR
CTRL_READ_WRITE              = 0x040   # was READ_WRITE
CTRL_ADDRESS_LINE_18         = 0x020
CTRL_ADDRESS_LINE_17         = 0x010
CTRL_VPP_P1_ENABLE           = 0x008   # was P1_VPP_ENABLE
CTRL_VPE_ENABLE              = 0x004   # was VPE_ENABLE
CTRL_VPP_A9_ENABLE           = 0x002   # was A9_VPP_ENABLE
CTRL_ADDRESS_LINE_16         = 0x001
```

**Phase 34 mirror block** (RESEARCH §Python Parity Surface lines 276–290 — append to the file after `:83`):
```python
# RURP Hardware Revisions — mirror of firestarter/include/rurp_shield.h
# REVISION_* enum. Documentary only — Python does not perform the ADC
# band-detect (firmware owns that). Used by host-side mapping of the
# MSG_OK_REV physical-u8 byte to a silkscreen-version string for log /
# CLI output. Keep in sync per CLAUDE.md sync rule.
# 0xFF is reserved as the EEPROM-override-absent sentinel (see
# rurp_config_utils.cpp:37 + serial_comm.py _format_message).
REVISION_0          = 0x00
REVISION_1          = 0x01
REVISION_2_0        = 0x02  # broad bucket: covers Rev 2.0 / 2.1 / 2.2 (R41=4k7)
REVISION_2_1        = 0x03  # via EEPROM override only — ADC cannot distinguish
REVISION_2_2        = 0x04  # via EEPROM override only — ADC cannot distinguish
REVISION_2_3        = 0x05  # R41=10k physical detect
REVISION_UNKNOWN    = 0xFE  # ADC band-gap or pre-detect-resistor + A2 indeterminate
```

**Critical preservation**:
- Same column-aligned `NAME = 0xNN  # comment` shape as CTRL_* block (per project CONVENTIONS.md — `UPPER_SNAKE_CASE` constants module-level).
- No type annotations (constants module is bare `name = value` per Phase 33 substrate).
- Section-header docstring carries the cross-repo sync-rule reminder.

---

### 7. `firestarter_app/firestarter/serial_comm.py` (MSG_OK_REV enum → silkscreen-string mapping)

**Role:** host CLI service · **Data Flow:** request-response (renders wire-payload bytes into log strings) · **Touch:** MODIFY-IN-PLACE — extend `_format_message` at `:319-346` with module-scope `_REVISION_SILKSCREEN` dict + lookup branch

**Analog:** Same file `:336-340` — the existing MSG_OK_REV sentinel-aware rendering (Phase 33 substrate established the P-02 `if msg_id == MSG_OK_REV and len(params) == 2:` guard idiom). Path A per RESEARCH §D-05 Open Question 1 recommendation.

**Existing MSG_OK_REV rendering** (lines 336–340, verbatim):
```python
if msg_id == MSG_OK_REV and len(params) == 2:
    physical, effective = params[0], params[1]
    if effective == 0xFF:
        return f"Rev{physical}"
    return f"Rev{effective}, Override HW: Rev{physical}"
```

**Module-scope dict** (RESEARCH §Path A lines 318–326 — lands at module scope, alongside the existing `MAGIC_PREAMBLE` / `STATE_MACHINE_PREFIXES` declarations near the top of the file):
```python
# Phase 34: REVISION_* byte → silkscreen-string mapping for MSG_OK_REV rendering.
# Mirrors firmware enum at firestarter/include/rurp_shield.h. Lookup-via-dict.get()
# so unknown bytes fall back to "Rev{n}" instead of raising.
_REVISION_SILKSCREEN = {
    REVISION_0:       "Rev 0",
    REVISION_1:       "Rev 1",
    REVISION_2_0:     "Rev 2.0-class",   # broad bucket per Phase 34 D-04
    REVISION_2_1:     "Rev 2.1 (override)",
    REVISION_2_2:     "Rev 2.2 (override)",
    REVISION_2_3:     "Rev 2.3",
    REVISION_UNKNOWN: "rev_unknown",
}
```

**Phase 34 `_format_message` extension** (REPLACES lines 336–340 verbatim — RESEARCH §Path A lines 328–334):
```python
if msg_id == MSG_OK_REV and len(params) == 2:
    physical, effective = params[0], params[1]
    phys_str = _REVISION_SILKSCREEN.get(physical, f"Rev{physical}")
    if effective == 0xFF:
        return phys_str
    eff_str = _REVISION_SILKSCREEN.get(effective, f"Rev{effective}")
    return f"{eff_str}, Override HW: {phys_str}"
```

**Critical preservation**:
- Path A chosen over Path B (new `hardware_revisions.py` module) per Phase 33 minimal-surface precedent — smaller diff, single-file change.
- Import `REVISION_*` constants via existing `from firestarter.constants import *` at `:24` (already wildcard-imported per project CONVENTIONS.md Wildcard Constants pattern).
- `0xFF`-effective-sentinel branch preserved verbatim (still means "no override active").
- `dict.get(byte, fallback)` keeps unknown future enum values from raising `KeyError` — same defensive idiom Phase 33 used for `COMMAND_NAMES.get(cmd)` at `:350`.

---

### 8. `firestarter_app/CLAUDE.md` (sync-rule prose extension)

**Role:** host CLI documentation · **Data Flow:** n/a · **Touch:** EXTEND-PROSE (append one sentence to "Constants" subsection at `:100`)

**Analog:** Same file — the existing Phase 33 CTRL_* sync-rule sentence at the end of the "Constants" subsection.

**Existing Constants subsection** (verbatim, ending at line 100):
```markdown
### Constants

`firestarter/constants.py` must stay in sync with `firestarter/include/firestarter.h` in the firmware sub-repo. Both define the same flag bit values and command codes. Additionally, the `RURP_CONTROL_REGISTER_BITS` block in `constants.py` (CTRL_* names) mirrors the control-register-bit declarations in `firestarter/include/rurp_pinout.h` (Phase 33 / v1.7 — silkscreen-label code-alias migration). Keep CTRL_* names + hex values in sync with the firmware header.
```

**Phase 34 sentence extension** (RESEARCH §Python Parity Surface lines 295–299 — append after the existing CTRL_* sentence):
```markdown
Additionally, the `RURP_HARDWARE_REVISIONS` block in `constants.py` (REVISION_* names) mirrors the hardware-revision enum declarations in `firestarter/include/rurp_shield.h` (Phase 34 / v1.7 — shield-version-detect design + firmware plumbing). Keep REVISION_* names + byte values in sync with the firmware enum; `0xFF` is reserved as the EEPROM-override-absent sentinel and `0xFE` (`REVISION_UNKNOWN`) is reserved for the ADC-band-gap fall-through.
```

**Critical preservation**:
- Same sentence template ("Additionally, the `X_BLOCK` block in `constants.py` (Y_* names) mirrors … in `firestarter/include/Z.h` (Phase N / v1.7 — …). Keep Y_* names + values in sync with the firmware header.").
- Append, do NOT replace — Phase 33's CTRL_* sentence stays intact.
- The `0xFF` / `0xFE` sentinel-carve-out clause is novel to Phase 34 — adds the load-bearing detail that Phase 33's sentence didn't need.

---

### 9. `.planning/v1.7/baseline-34/{uno,leonardo,uno328pb}.hex` (gitignored .hex baselines)

**Role:** meta-repo tooling · **Data Flow:** file-I/O · **Touch:** CREATE-DIR + place 3 `.hex` snapshots

**Analog:** `.planning/v1.7/phase-33-baseline-hex/{uno,uno328pb,leonardo}.hex` — Phase 33 Plan 00 Task 1 captured these via `cp` from `.pio/build/<env>/firestarter_<env>.hex` after a verified-clean source-tree rebuild.

**Phase 33 Plan 00 capture pattern** (33-00-PLAN.md Task 1 `<action>` block lines 95–101 — verbatim reusable, only the destination directory changes):

```bash
# 1. Verify clean source tree
cd /workspaces/firestarter && git status --porcelain include/ src/ test/ platformio.ini  # must return 0 lines
cd /workspaces/firestarter && git rev-parse --abbrev-ref HEAD  # must return v1.7-shield-investigation

# 2. Clean rebuild all 3 AVR envs
cd /workspaces/firestarter && pio run -t clean -e uno -e uno328pb -e leonardo
cd /workspaces/firestarter && pio run -e uno -e uno328pb -e leonardo

# 3. Verify build artifacts exist
test -f /workspaces/firestarter/.pio/build/uno/firestarter_uno.hex
test -f /workspaces/firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex
test -f /workspaces/firestarter/.pio/build/leonardo/firestarter_leonardo.hex

# 4. Create gitignored snapshot dir + copy
mkdir -p /workspaces/.planning/v1.7/baseline-34/
cp /workspaces/firestarter/.pio/build/uno/firestarter_uno.hex /workspaces/.planning/v1.7/baseline-34/uno.hex
cp /workspaces/firestarter/.pio/build/uno328pb/firestarter_uno328pb.hex /workspaces/.planning/v1.7/baseline-34/uno328pb.hex
cp /workspaces/firestarter/.pio/build/leonardo/firestarter_leonardo.hex /workspaces/.planning/v1.7/baseline-34/leonardo.hex

# 5. Record baseline commit SHA
cd /workspaces/firestarter && git rev-parse HEAD > /workspaces/.planning/v1.7/baseline-34/BASELINE_COMMIT.txt
```

**Per-board Phase 33 baseline sizes** (from 33-00-SUMMARY.md Per-board baseline `wc -c` table — provided as a cross-reference for what the Phase 34 baseline should look like, modulo whatever Phase 33's Wave 3 rename added in `.hex` bytes):

| Env       | Phase 33 baseline .hex size | Path                                                |
|-----------|----------------------------|-----------------------------------------------------|
| uno       | 62617 B                    | `.planning/v1.7/phase-33-baseline-hex/uno.hex`      |
| uno328pb  | 62854 B                    | `.planning/v1.7/phase-33-baseline-hex/uno328pb.hex` |
| leonardo  | 68876 B                    | `.planning/v1.7/phase-33-baseline-hex/leonardo.hex` |

**Critical preservation**:
- `.planning/v1.7/` is gitignored per Phase 31 D-11; baseline-34/ inherits that gitignore (verified: `git check-ignore` would match line 13 of root `.gitignore`).
- Capture happens BEFORE any firmware-source edit — this is the load-bearing Wave 0 invariant per RESEARCH §When to Capture Baseline.
- `cp` from build output is the ONLY legitimate source — NEVER fabricate `.hex` content via heredoc/echo (per Phase 33 Plan 00 critical-rule annotation).
- `BASELINE_COMMIT.txt` records the firestarter sub-repo HEAD SHA at capture time (per 33-00 Task 1 traceability anchor).

---

### 10. `.planning/v1.7/baseline-34/verify-detect-34.sh` (delta-band regression-guard)

**Role:** meta-repo tooling · **Data Flow:** file-I/O · **Touch:** CREATE (executable bash script)

**Analog:** `.planning/v1.7/phase-33-baseline-hex/check-migration.sh` — Phase 33 Plan 00 wave-merge regression-guard. Phase 34's script is a near-verbatim adaptation; ONLY the `cmp` byte-identical assertion swaps to a `wc -c` delta-band check (Phase 34 EXPECTS non-zero `.hex` delta because the detect-rev logic actually changes; Phase 33's rename was byte-identical).

**Phase 33 `check-migration.sh` shell skeleton** (existing file at `.planning/v1.7/phase-33-baseline-hex/check-migration.sh`, lines 1–88 — full text quoted as the structural analog):

```bash
#!/usr/bin/env bash
#
# Phase 33 wave-merge regression-guard for the silkscreen-label → code-alias
# migration. Wraps three assertions:
#   Assertion 1: grep-zero for old shield-net names …
#   Assertion 2: REV_[12]_* prefix family fully removed …
#   Assertion 3: post-rename .hex byte-identical (cmp) against the captured
#                pre-rename baseline for all three AVR envs.

set -euo pipefail

BASELINE_DIR="/workspaces/.planning/v1.7/phase-33-baseline-hex"
FIRMWARE_DIR="/workspaces/firestarter"
# … assertions …

for env in uno uno328pb leonardo; do
    BASELINE_HEX="${BASELINE_DIR}/${env}.hex"
    BUILT_HEX="${FIRMWARE_DIR}/.pio/build/${env}/firestarter_${env}.hex"
    if ! cmp -s "${BASELINE_HEX}" "${BUILT_HEX}"; then
        echo "FAIL: ${env}.hex diverged from baseline"
        exit 1
    fi
done

echo "PASS: alias migration verified clean"
```

**Phase 34 `verify-detect-34.sh` body** (RESEARCH §Phase 34 Adaptation lines 477–513 — adapted from Phase 33's skeleton; swaps the `cmp` byte-identical assertion to a `wc -c` `[20, 300] B` delta-band check):

```bash
#!/usr/bin/env bash
#
# Phase 34 wave-merge regression-guard for the shield-version-detect firmware
# plumbing. Wraps three assertions:
#   Assertion 1: each AVR env's .hex delta vs pre-Phase-34 baseline lands in
#                [EXPECTED_DELTA_MIN, EXPECTED_DELTA_MAX]. Below MIN: rework
#                didn't compile in. Above MAX: unexpected bloat — investigate.
#   Assertion 2: native dispatch tests stay green (configure_memory unaffected).
#   Assertion 3: REVISION_2_3 + REVISION_UNKNOWN both present in rurp_shield.h.

set -euo pipefail

BASELINE_DIR="/workspaces/.planning/v1.7/baseline-34"
FIRMWARE_DIR="/workspaces/firestarter"

EXPECTED_DELTA_MIN=20    # below this, the detect-rev rework didn't actually compile in
EXPECTED_DELTA_MAX=300   # above this, the rework bloated more than expected

# Assertion 1: per-env .hex delta in expected band
for env in uno uno328pb leonardo; do
    BASELINE_HEX="${BASELINE_DIR}/${env}.hex"
    BUILT_HEX="${FIRMWARE_DIR}/.pio/build/${env}/firestarter_${env}.hex"
    [ -f "${BASELINE_HEX}" ] || { echo "FAIL: baseline ${BASELINE_HEX} missing"; exit 1; }
    [ -f "${BUILT_HEX}" ] || { echo "FAIL: built ${BUILT_HEX} missing — run 'pio run -e ${env}' first"; exit 1; }
    BASELINE_BYTES=$(wc -c < "${BASELINE_HEX}")
    BUILT_BYTES=$(wc -c < "${BUILT_HEX}")
    DELTA=$((BUILT_BYTES - BASELINE_BYTES))
    echo "${env}: baseline=${BASELINE_BYTES} B, built=${BUILT_BYTES} B, delta=${DELTA} B"
    if [ ${DELTA} -lt ${EXPECTED_DELTA_MIN} ] || [ ${DELTA} -gt ${EXPECTED_DELTA_MAX} ]; then
        echo "FAIL: ${env}.hex delta ${DELTA} B outside expected [${EXPECTED_DELTA_MIN}, ${EXPECTED_DELTA_MAX}] range"
        exit 1
    fi
done

# Assertion 2: native dispatch tests stay green
cd "${FIRMWARE_DIR}"
pio test -e native -f "*test_dispatch*" >/dev/null 2>&1 || { echo "FAIL: pio test -e native -f '*test_dispatch*'"; exit 1; }

# Assertion 3: enums present
grep -q "REVISION_2_3" "${FIRMWARE_DIR}/include/rurp_shield.h" || { echo "FAIL: REVISION_2_3 missing"; exit 1; }
grep -q "REVISION_UNKNOWN" "${FIRMWARE_DIR}/include/rurp_shield.h" || { echo "FAIL: REVISION_UNKNOWN missing"; exit 1; }

echo "PASS: Phase 34 detect-rev rework verified — delta within band, native tests green, enums present."
```

**Critical preservation** (from Phase 33 check-migration.sh post-mortem 33-00-SUMMARY.md `Decisions Made` lines 144–148):
- `set -euo pipefail` at top — safe execution.
- Absolute paths via `/workspaces/.planning/v1.7/…` — no relative-path footguns.
- Gitignored under `.planning/v1.7/` (Phase 31 D-11 / inherits parent gitignore line).
- Both pre-Wave-2 (assertion 1 will fail — built `.hex` matches baseline → delta = 0 < 20) AND post-Wave-2 (delta ~80–150 B → PASS) invocations are documented; the script is a meaningful gate at both points.
- `chmod +x` after write (Phase 33 made this implicit by including it in the planner's verify step).

---

### 11. `firestarter_app/tests/test_revision_constants_parity.py` (optional Wave 3 parity assertion)

**Role:** host CLI test · **Data Flow:** event-driven (pytest test harness) · **Touch:** CREATE (single test function)

**Analog:** `firestarter_app/tests/test_decoder.py` (existing wire-frame decoder test module — same project conventions: top-level docstring, `from firestarter.constants import …`, module-scoped test functions, no fixtures needed). Phase 34's parity assertion is a single test function with no fixtures — the smallest possible pytest module.

**RESEARCH-supplied test body** (RESEARCH §Python Parity Gate lines 543–559 — verbatim):

```python
"""
Project Name: Firestarter
Copyright (c) 2026 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 34 parity test: REVISION_* byte values must match the firmware enum
declared at firestarter/include/rurp_shield.h:25-30. Cross-repo invariant
enforced by D-08 + firestarter_app/CLAUDE.md sync rule.
"""

from firestarter.constants import (
    REVISION_0, REVISION_1, REVISION_2_0, REVISION_2_1, REVISION_2_2,
    REVISION_2_3, REVISION_UNKNOWN,
)


def test_revision_byte_values_match_firmware_enum():
    """Phase 34 D-08 parity: REVISION_* byte values must match the firmware
    enum at firestarter/include/rurp_shield.h:25-30."""
    assert REVISION_0       == 0x00
    assert REVISION_1       == 0x01
    assert REVISION_2_0     == 0x02
    assert REVISION_2_1     == 0x03
    assert REVISION_2_2     == 0x04
    assert REVISION_2_3     == 0x05   # NEW Phase 34
    assert REVISION_UNKNOWN == 0xFE   # NEW Phase 34
    # 0xFF is reserved as the EEPROM-override-absent sentinel — NOT a REVISION_ value.
```

**Critical preservation** (from `firestarter_app/tests/test_decoder.py` + project CONVENTIONS.md):
- Module-level docstring with copyright header (project file-header template per CONVENTIONS.md "Module Header Pattern").
- `from firestarter.constants import …` named imports (NOT wildcard — explicit names make the parity assertion self-documenting per the docstring).
- No fixtures, no `conftest.py` dependency — single function with `assert` chain.
- Lives at `firestarter_app/tests/test_revision_constants_parity.py` — picked up automatically by pytest's default test discovery (no pyproject.toml or conftest.py edit needed).

---

## Shared Patterns

### Shared Pattern 1: `#define` (not `constexpr`) for AVR-byte-identical compile

**Source:** `firestarter/include/rurp_pinout.h:43-106` (Phase 33 entire substrate) + 33-CONTEXT.md D-07
**Apply to:** all new firmware `#define`s in Phase 34 — `REVISION_2_3`, `REVISION_UNKNOWN`, `ADC_BAND_R41_4K7_HIGH`, `ADC_BAND_R41_10K_LOW`, `ADC_BAND_R41_10K_HIGH`

```c
#define NAME VALUE   // ← preprocessor-only substitution; emits literally byte-identical token stream
```
Phase 33 D-07 proved this produces AVR-objcopy `.hex` byte-identical output (Δ = 0 B per env). Phase 34 expects Δ > 0 B per env because the underlying detect-rev logic changes — but the threshold-constant additions themselves contribute 0 B until consumed in the rework code (preprocessor-resolved at compile time). `constexpr static const uint16_t` would add a symbol-table thunk that perturbs `.hex` layout — strictly forbidden by Phase 33 D-07.

### Shared Pattern 2: `#ifdef HARDWARE_REVISION` compile-flag gating

**Source:** `firestarter/platformio.ini:23` (`-D HARDWARE_REVISION` for all 3 AVR envs) + `firestarter/include/rurp_pinout.h:45-47, 83-107` + `firestarter/include/rurp_hw_rev_utils.h:4-69`
**Apply to:** all new Phase 34 enum values + threshold constants + reworked detect-rev body

```c
#ifdef HARDWARE_REVISION
// … detect-rev code paths, REVISION_* enum, ADC_BAND_* constants …
#endif
```
The `[env:native]` `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp>` deliberately excludes `src/hardware_operations.cpp` (and transitively `rurp_hw_rev_utils.h`) from the native test build. Phase 34 preserves this asymmetry — native tests continue to bypass detect-rev entirely (per CONTEXT.md Claude's Discretion + RESEARCH §Native Test Coverage Confirmation).

### Shared Pattern 3: EEPROM Sentinel `0xFF` Reserve

**Source:** `firestarter/include/rurp_hw_rev_utils.h:63` (override-active gate) + `firestarter/src/rurp_config_utils.cpp:37` (factory-fresh default) + `firestarter/src/hardware_operations.cpp:99, 102, 112, 114` (`MSG_OK_REV` / `MSG_OK_CFG` sentinel byte emit) + `firestarter_app/firestarter/serial_comm.py:338, 344` (`effective == 0xFF` host-side branch)
**Apply to:** `REVISION_UNKNOWN = 0xFE` carve-out (NOT `0xFF`)

```c
if (rurp_config->hardware_revision < 0xFF) {
    return rurp_config->hardware_revision;   // override active
}
return rurp_get_physical_hardware_revision();  // no override — physical detect wins
```
`0xFF` is load-bearing as the "no EEPROM override" sentinel. Phase 34 MUST NOT alias `REVISION_UNKNOWN` to `0xFF` (would collide); MUST use `0xFE` (grep-clean per RESEARCH §REVISION_UNKNOWN Non-Collision Audit). The existing latent-bug `default: revision = 0xFF;` at `rurp_hw_rev_utils.h:54-57` is cleaned up by Phase 34 (replaced with `REVISION_UNKNOWN` per D-07).

### Shared Pattern 4: Phase 33 Atomic Multi-Repo Commit Boundary

**Source:** `.planning/phases/33-silkscreen-label-code-alias-migration/33-04-PLAN.md` frontmatter `files_modified` lists (cross-3-directory: `firestarter_app/firestarter/constants.py`, `firestarter_app/firestarter/main.py`, `firestarter_app/CLAUDE.md`, `.planning/v1.7-SHIELD-REVS.md`) + 33-00-SUMMARY.md `Files Created/Modified` section
**Apply to:** Phase 34 wave-decomposition pattern

```
Wave 1: meta-repo §8/§9 fills → meta-repo commits only (no submodule pointer bump)
Wave 2: firmware sub-repo edits → firestarter sub-repo commits + meta-repo submodule-pointer-bump commit
Wave 3: host sub-repo edits → firestarter_app sub-repo commits + meta-repo submodule-pointer-bump commit + meta-repo CLAUDE.md sync-rule extension commit
```
Sub-repo commits land first (inside the submodule on `v1.7-shield-investigation` branch); the meta-repo bumps the submodule pointer as a separate commit on the meta-repo's `v1.7-shield-investigation` branch. Phase 33 Wave 4 proved this pattern at scale (lines 605–611 of RESEARCH.md).

### Shared Pattern 5: Gitignored `.planning/v1.7/` baseline-and-tooling area

**Source:** Phase 31 D-11 (`.planning/v1.7/` gitignore policy) + `.planning/v1.7/phase-33-baseline-hex/` (Phase 33 Plan 00 — 5 gitignored files: 3 `.hex` + `BASELINE_COMMIT.txt` + `check-migration.sh`)
**Apply to:** all Phase 34 baseline-34/ artifacts

```
.planning/v1.7/baseline-34/uno.hex             (gitignored — pre-Phase-34 Intel-HEX snapshot)
.planning/v1.7/baseline-34/uno328pb.hex        (gitignored)
.planning/v1.7/baseline-34/leonardo.hex        (gitignored)
.planning/v1.7/baseline-34/BASELINE_COMMIT.txt (gitignored — firestarter HEAD SHA at capture)
.planning/v1.7/baseline-34/verify-detect-34.sh (gitignored, executable)
```
Verify with `cd /workspaces && git status --porcelain .planning/v1.7/baseline-34/ | wc -l` → must return 0 (all artifacts excluded by the root `.gitignore`'s `.planning/v1.7/` rule).

---

## No Analog Found

None. All 11 Phase 34 deliverables have direct in-tree analogs:
- §8 + §9 fills → §7 fill substrate (Phase 33 Plan 33-04 ALIAS-01)
- REVISION_2_3 + REVISION_UNKNOWN → existing REVISION_0..REVISION_2_2 block
- detect-rev rework → existing detect function body + ctrl-reg mapper switch
- ADC_BAND_* → existing PIN_* / RES_* `#define`-only constants
- Python REVISION_* block → existing CTRL_* block (Phase 33 D-08 substrate)
- serial_comm.py mapping → existing MSG_OK_REV P-02 sentinel path
- CLAUDE.md prose extension → existing Phase 33 CTRL_* sync-rule sentence
- baseline-34/ hex + verify-detect-34.sh → Phase 33 Plan 00 baseline-capture pattern
- test_revision_constants_parity.py → existing pytest module shape (test_decoder.py)

---

## Metadata

**Analog search scope:**
- `/workspaces/firestarter/include/` (firmware headers — primary source-of-truth for detect-rev, REVISION_* enum, ADC band constants)
- `/workspaces/firestarter/src/hardware_operations.cpp` (MSG_OK_REV emit site)
- `/workspaces/firestarter_app/firestarter/` (constants.py, serial_comm.py, messages.py, hardware.py)
- `/workspaces/firestarter_app/tests/` (pytest module conventions)
- `/workspaces/firestarter_app/CLAUDE.md` (sync-rule prose location)
- `/workspaces/.planning/v1.7-SHIELD-REVS.md` (§7 fill analog; §8 + §9 TBD markers)
- `/workspaces/.planning/v1.7/phase-33-baseline-hex/` (gitignored baseline + verifier-script analog)
- `/workspaces/.planning/phases/33-silkscreen-label-code-alias-migration/` (33-CONTEXT.md, 33-00-PLAN.md, 33-00-SUMMARY.md, 33-PATTERNS.md — Phase 33 substrate documentation)

**Files scanned:** 17

**Pattern extraction date:** 2026-05-25
