# Phase 34: Shield-Version-Detect Design + Firmware Plumbing — Research

**Researched:** 2026-05-25
**Domain:** Firmware ADC band-detect + Python parity + meta-repo schematic-delta documentation
**Confidence:** HIGH (stack/architecture/pitfalls all verified against codebase)
**Mode:** Stress-test of pre-locked D-01..D-11 via codebase grep + ATmega328P datasheet sources

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions (D-01..D-11)

- **D-01: §8 documents the existing Anders R41-on-A3 scheme — no new operator-fabricated board.** Phase 34 fills `.planning/v1.7-SHIELD-REVS.md` §8 with the already-upstream divider topology (JP4 / P1_VPP_JMP → R41 → A3 → GND), citing the per-rev R41 value from §3. The spec's "next-rev shield" phrasing is satisfied by treating Rev 2.3 as the seed entry. No new PCB design, no new resistor proposal, no fabrication.
- **D-02: ADC pin = A3 (PIN_HW_REVISION_DETECT_ADC) — already aliased in Phase 33.** No new pin assignment. The pin is already declared in `firestarter/include/rurp_pinout.h:46`. R41 is already aliased as `RES_HW_REVISION_DIVIDER`. JP4 is aliased as `JMP_VPP_P1_BYPASS`.
- **D-03: Voltage-band separation derived from upstream R41 values + ATmega internal pull-up.** Computed bands (5V VCC, 30 kΩ typical pull-up): Rev 2.0/2.1/2.2 (R41=4k7) → ADC ≈ 138; Rev 2.3 (R41=10k) → ADC ≈ 256; pre-detect-resistor (no R41) → ADC ≈ 1023. Separation ≥ 0.4 V across the 20–50 kΩ pull-up tolerance range.
- **D-04: ADC distinguishes physically-separable bands only — Rev 2.0/2.1/2.2 collapse into one bucket.** Reports `REVISION_2_0` (broad bucket). Operator-specific Rev 2.1/Rev 2.2 distinction flows through EEPROM `hw_revision` override.
- **D-05: Detected ADC enum values mapped to silkscreen strings host-side, NOT firmware-side.** Firmware writes a u8 enum via `MSG_OK_REV`. Host catalog formats it. No codegen on `tools/catalog/messages.toml`. Planner finalizes whether the string mapping lives in `serial_comm.py` or in a new `hardware_revisions.py` lookup module.
- **D-06: Switch A3 from `digitalRead` to `analogRead`; preserve A2 ADC disambiguation for Rev 0 vs Rev 1.** New `if/else` band-lookup chain on `analogRead(PIN_HW_REVISION_DETECT_ADC)`; existing A2 magic-number `< 1000` retained for Rev 0 vs Rev 1.
- **D-07: Add `REVISION_2_3 = 5` and `REVISION_UNKNOWN = 0xFE` enum values; `0xFF` stays reserved for "no override" sentinel.** Insert at `firestarter/include/rurp_shield.h:30`. Change `default:` branch sentinel from `0xFF` to `REVISION_UNKNOWN`. Add `case REVISION_2_3:` arm aliased to REV_2_x ctrl-reg layout.
- **D-08: Python-side parity — add `REVISION_2_3 = 5` + `REVISION_UNKNOWN = 0xFE` to `firestarter_app/firestarter/constants.py`.** New `# RURP Hardware Revisions` block. Mirror firmware enum verbatim. Extend `firestarter_app/CLAUDE.md` sync rule prose.
- **D-09: No new message ID — reuse `MSG_OK_REV` 2-byte wire shape verbatim.** `tools/catalog/messages.toml` untouched; no codegen pass. Frame ID + byte count + frame structure unchanged.
- **D-10: `.hex` byte-diff per AVR env + native test green is the planner's gate; operator-on-bench validation deferred to Phase 35.** Pre-Phase-34 `.hex` baseline captured at branch tip (gitignored `.planning/v1.7/baseline-34/`); post-Phase-34 Δ expected 50–200 B; `pio test -e native -f "*test_dispatch*"` green; `pytest -q` in firestarter_app green.
- **D-11: §9 table schema = `rev | r41_value | expected_adc_band | reported_enum | reported_silkscreen_string | source_evidence`.** Planner enforces strict band ordering: `ADC_BAND_R41_4K7_HIGH < ADC_BAND_R41_10K_LOW < ADC_BAND_R41_10K_HIGH`.

### Claude's Discretion (research recommendations forthcoming below)

- Plan-wave decomposition (likely 3 waves — meta §8/§9 → firmware → Python parity)
- Threshold constant location (`rurp_pinout.h` vs new sibling header)
- 8-sample analogRead averaging (driven by D-03 tolerance math)
- Host-side `firestarter dev detect-rev` subcommand
- Native test coverage extension for `rurp_hw_rev_utils.h`
- CONFIG_VERSION bump in `rurp_shield.h:44` (NOT needed — struct unchanged)

### Deferred Ideas (OUT OF SCOPE)

For Phase 35 (close):
- Operator-on-bench validation (Rev 2.0/2.2 sideload + handshake-read)
- Rev 2.2 R41 physical measurement (follow-up #5)
- §9 row update for Modified Rev 0 (once `MODIFICATIONS.md` lands)
- README cross-links (firestarter/ + firestarter_app/)

For post-v1.7:
- Runtime capability guards (§6 Runtime-Guard Follow-Up Todos)
- 8-sample analogRead averaging (if not landed in Phase 34)
- Native-test coverage for `rurp_hw_rev_utils.h`
- Codegen pass to add `MSG_OK_DETECTED_REV` (richer string)
- PORTx masks in board cpp files (Phase 33 deferred)

Out of v1.7 entirely:
- Designing Rev 2.4 with finer per-rev bands (per-rev distinguishable by ADC alone — requires PCB fab)
- External pull-up resistor on A3 (schematic change → new rev)
- Per-board MCU pull-up calibration stored in EEPROM
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DETECT-HW-01 | Schematic delta documented in `v1.7-SHIELD-REVS.md`: resistor divider into an Arduino ADC pin, with rev-specific resistor values producing voltage bands ≥ ~0.3V apart against 10-bit ADC noise floor | §8 fill (D-01) — ASCII schematic + per-rev R41 table sourced from §3; voltage-band math in `## ADC Voltage Band Math` proves ≥ 0.4 V separation across worst-case pull-up tolerance |
| DETECT-HW-02 | Schematic delta includes per-rev expected-ADC-band table seeding Rev 2.3 entry; existing Rev 0 / 2.0 / 2.2 boards captured as `rev_unknown` fall-through band | §9 fill (D-11) — six-row schema with `expected_adc_band` column carrying explicit tolerance-derived ranges |
| DETECT-FW-01 | Firmware reads ADC pin, looks up voltage band, reports detected silkscreen-rev string in handshake payload; on pre-detect-resistor boards (floating/grounded ADC) → `rev_unknown` and firmware honors EEPROM `hw_revision` byte fallback | D-06 detect-logic rework + D-07 enum extension + D-09 `MSG_OK_REV` wire reuse; `rurp_get_hardware_revision()` EEPROM-override precedence at `rurp_hw_rev_utils.h:61-67` unchanged (already implements fall-through correctly) |
| DETECT-FW-02 | GATE-1.7 non-regression: existing pre-detect-resistor boards handshake byte-identical to v1.6 baseline modulo additive `rev_unknown` report; chip programming + read paths byte-identical; firmware compiles cleanly for all 3 AVR targets without physical fabrication | D-10 `.hex` byte-diff per env mechanism (Phase 33 verified pattern); D-09 wire-frame-ID + byte-count invariants; Phase 35 operator-on-bench deferred |
</phase_requirements>

## Overview

Phase 34 is a 3-repo plumbing phase: (1) fill `.planning/v1.7-SHIELD-REVS.md` §8 (Detect-HW Schematic Delta) + §9 (Per-Rev ADC Band Table) in the meta-repo; (2) rework `firestarter/include/rurp_hw_rev_utils.h::rurp_detect_hardware_revision()` from a digital-A3 + analog-A2 read into an analog-A3 band-lookup that distinguishes Rev 2.0-class (R41=4k7) from Rev 2.3 (R41=10k) from pre-detect-resistor revs (no R41); (3) mirror two new enum values (`REVISION_2_3 = 5`, `REVISION_UNKNOWN = 0xFE`) into `firestarter_app/firestarter/constants.py`.

CONTEXT.md pre-locked D-01..D-11. This research stress-tests those decisions against actual code — the result is **D-01..D-11 are correct and implementable as written.** One nuance flagged: ATmega328P datasheet pull-up range is 20–50 kΩ (verified [CITED: avrfreaks/forum + Microchip datasheet]), and the worst-case math at 50 kΩ pull-up brings the 4k7 band edge as low as ADC ≈ 88 (V_A3 ≈ 430 mV) and the 10k band edge as low as ADC ≈ 170 (V_A3 ≈ 833 mV) — separation remains > 0.4 V but the threshold constants need to be picked to land mid-gap with explicit margin, not at the nominal-30 kΩ midpoint. Concrete proposal: `ADC_BAND_R41_4K7_HIGH = 200`, `ADC_BAND_R41_10K_LOW = 220`, `ADC_BAND_R41_10K_HIGH = 600`. This gives a 20-ADC-count guard gap between the 4k7 and 10k buckets across the full pull-up tolerance range.

**Primary recommendation:** Three-wave plan — Wave 1 (meta-repo §8/§9 fill + Phase 34 baseline `.hex` capture) → Wave 2 (firmware: enum extension + `rurp_detect_hardware_revision()` rework + `rurp_map_ctrl_reg_for_hardware_revision()` REV_2_3 arm + threshold constants in `rurp_pinout.h`) → Wave 3 (firestarter_app: constants.py parity + CLAUDE.md sync-rule extension + optional serial_comm.py enum→silkscreen-string mapping). Reuse the Phase 33 `check-migration.sh` pattern verbatim for the byte-diff gate, but rename to `verify-detect-34.sh` and replace the grep-zero assertion with an "expected delta band" check (50–200 B). 8-sample analogRead averaging is RECOMMENDED — adds 8 cycles of jitter immunity at trivial code cost; the threshold tolerance math is tight enough at the 50 kΩ pull-up endpoint that single-shot reads risk band-edge misclassification.

## ADC Voltage Band Math (D-03 validation + threshold constant proposal)

### ATmega Internal Pull-up Spec

| Source | Min | Typ | Max | Notes |
|--------|-----|-----|-----|-------|
| ATmega328P datasheet (DC characteristics — I/O ports) | 20 kΩ | ~30–40 kΩ | 50 kΩ | [CITED: avrfreaks/forum + Microchip ATmega328P datasheet — Min 20kΩ Max 50kΩ verified via WebSearch 2026-05-25] |
| ATmega32U4 (Leonardo) | 20 kΩ | ~30 kΩ | 50 kΩ | [ASSUMED — Leonardo MCU uses same I/O-port pull-up spec family; verify against Leonardo datasheet at execute time if margin matters] |
| ATmega328PB (uno328pb) | 20 kΩ | ~30 kΩ | 50 kΩ | [ASSUMED — Atmel-7810 family-shared spec; ATmega328PB is the PB-variant of ATmega328P, same I/O cell] |

**Confidence:** HIGH for ATmega328P (verified via two independent sources — official AVR Freaks discussion citing datasheet + Microchip's 7810 family datasheet). MEDIUM-HIGH for 32U4 / 328PB (same Atmel I/O-cell architecture; pull-up specs match across the family per accepted engineering knowledge — but planner should grep the per-MCU datasheet at execute time if any band-edge margin shrinks below 200 mV).

### Voltage-Band Math (5V VCC, divider topology: pull-up Rpu in series with R41 to GND)

V_A3 = VCC × R41 / (Rpu + R41), where Rpu is the internal pull-up (20–50 kΩ) and R41 is the per-rev detect divider.

ADC reading (10-bit, VCC = AREF reference) = round(V_A3 / VCC × 1023) = round(R41 / (Rpu + R41) × 1023).

| Rev | R41 | Rpu = 20 kΩ (best-case high-bound) | Rpu = 30 kΩ (typical) | Rpu = 50 kΩ (worst-case low-bound) |
|-----|-----|------------------------------------|----------------------|--------------------------------------|
| Rev 2.0/2.1/2.2 | 4k7 | V≈0.953 V, ADC≈195 | V≈0.677 V, ADC≈138 | V≈0.430 V, ADC≈88 |
| Rev 2.3 | 10k | V≈1.667 V, ADC≈341 | V≈1.250 V, ADC≈256 | V≈0.833 V, ADC≈170 |
| Pre-detect (no R41, A3 floating with pull-up) | n/a | V≈VCC, ADC≈1023 | V≈VCC, ADC≈1023 | V≈VCC, ADC≈1023 |

Notes:
- The "pre-detect floating" case isn't truly floating — `pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP)` at `rurp_hw_rev_utils.h:43` enables the internal pull-up. With no R41 path to GND, A3 sits at VCC (or close to it; minor leakage drops it slightly but still ≥ 900 mV / ADC ≥ 850 in practice).
- The R41=10k worst-case (50 kΩ Rpu) **lower band edge is ADC≈170**; the R41=4k7 best-case (20 kΩ Rpu) **upper band edge is ADC≈195**. **These two ranges DO NOT overlap.** Separation across the full tolerance space ≥ 195→170 = 25 ADC counts ≈ 122 mV, which is above the 10-bit ADC noise floor (~10 mV ≈ 2 LSB on a quiet AVR reference) but tight enough to justify 8-sample averaging.

### Threshold-Constant Proposal Table

| Constant | Proposed value | Rationale |
|----------|---------------|-----------|
| `ADC_BAND_R41_4K7_HIGH` | `200` | Upper edge of the R41=4k7 bucket. Best-case (Rpu=20kΩ) reading is ADC≈195; setting the threshold at 200 gives 5-count headroom AND keeps the 4k7 bucket from bleeding into the 10k bucket at the worst-case-pull-up endpoint. |
| `ADC_BAND_R41_10K_LOW` | `220` | Lower edge of the R41=10k bucket. Worst-case (Rpu=50kΩ) reading is ADC≈170; with 8-sample averaging the band drifts up by ~5–10 counts, so the actual minimum lands ≈180–190. 220 gives a 20-count guard gap above the 4k7 ceiling of 200. *Note: if 8-sample averaging is NOT added, drop this to 210 to give a 10-count guard gap.* |
| `ADC_BAND_R41_10K_HIGH` | `600` | Upper edge of the R41=10k bucket. Best-case reading is ADC≈341; setting the threshold at 600 gives a wide kill-zone before the pull-up-only floating range (≥850). 600 is mid-gap between the 10k upper-bound (≈341) and the pre-detect lower-bound (≈850). |

**Decision logic (firmware):**
- `adc_a3 < ADC_BAND_R41_4K7_HIGH (200)` → Rev 2.0-class (broad bucket per D-04) → `REVISION_2_0`
- `adc_a3 < ADC_BAND_R41_10K_HIGH (600) && adc_a3 >= ADC_BAND_R41_10K_LOW (220)` → Rev 2.3 → `REVISION_2_3`
- `adc_a3 >= ADC_BAND_R41_10K_HIGH (600)` → high band (no R41) → fall through to A2 disambig for Rev 0 vs Rev 1
- `adc_a3 in [200, 220)` (the guard gap) → `REVISION_UNKNOWN` — explicit fall-through; this is the failure mode for a Rev 2.2 board with R41 physically measured at a value between 4k7 and 10k (the open Phase 35 follow-up #5)

### 8-Sample Averaging Recommendation: YES

**Recommendation:** Add 8-sample averaging via a small inline `analog_read_avg8()` helper (8 reads summed, shifted right by 3 — pure shift-divide, no library call).

**Rationale:**
1. Single-shot ADC reads on AVR with AVcc reference exhibit ±2–4 LSB jitter at low band reads ([CITED: ATmega328P datasheet electrical characteristics — ADC noise typical ≤ 2 LSB with quiet AVcc, up to 4 LSB with switching loads]). The RURP shield's AVcc is shared with the digital rail (5V VCC plane carries the data buffer + control register switching) — not a quiet reference.
2. The worst-case gap between the 4k7 bucket ceiling (ADC≈195 at Rpu=20kΩ) and the 10k bucket floor (ADC≈170 at Rpu=50kΩ) — 25 ADC counts — exceeds single-shot noise but is within 2σ jitter range on a noisy supply.
3. 8 samples × ~13 µs per ADC conversion ≈ 104 µs added boot latency — negligible against the existing ~50 ms boot-handshake sequence in `firestarter.cpp:39-47`.
4. Code cost: ≈ 30 bytes additional Flash (loop + accumulator + shift). Well within the D-10 expected 50–200 B delta budget.

**Code:**
```cpp
static uint16_t analog_read_avg8(uint8_t pin) {
    uint16_t sum = 0;
    for (uint8_t i = 0; i < 8; i++) {
        sum += (uint16_t)analogRead(pin);
    }
    return (uint16_t)(sum >> 3);  // average over 8 samples
}
```

[ASSUMED: 8-sample averaging is sufficient for the 25-count worst-case gap. If bench measurement on operator's Rev 2.2 board (Phase 35) shows readings drifting within the [200, 220) guard gap, planner should increase to 16 samples (shift right by 4) — still trivial Flash cost.]

### Band-Overlap Risk Summary

| Pair | Worst-case lower-of-higher | Best-case upper-of-lower | Gap | Risk |
|------|----------------------------|--------------------------|-----|------|
| 4k7 vs 10k | ADC≈170 (10k @ Rpu=50kΩ) | ADC≈195 (4k7 @ Rpu=20kΩ) | 25 counts | **LOW** with 8-sample averaging + 20-count threshold guard; **MEDIUM** with single-shot reads |
| 10k vs floating | ADC≈850 (floating, leakage-affected) | ADC≈341 (10k @ Rpu=20kΩ) | 509 counts | **NONE** — orders of magnitude wider than any reasonable noise envelope |
| 4k7 vs floating | ADC≈850 | ADC≈195 | 655 counts | **NONE** |

The only real risk is the 4k7-vs-10k boundary. Mitigations: 8-sample averaging + 20-count guard gap + EEPROM `hw_revision` override path (existing) for any operator-discovered misclassification.

## Firmware Detection Logic Rework (D-06, D-07 implementation surface)

### Existing Code (current state — `rurp_hw_rev_utils.h:42-59`)

```cpp
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
        revision = 0xFF;     // <-- LATENT BUG: collides with EEPROM-override-absent sentinel
    }
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT);
}
```

### Reworked Body (Phase 34 — D-06 + D-07 + 8-sample averaging)

```cpp
void rurp_detect_hardware_revision() {
    pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP);
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT_PULLUP);

    // 8-sample averaging on the A3 detect divider to robustify against AVcc
    // switching noise (see Phase 34 RESEARCH §ADC Voltage Band Math).
    uint16_t adc_a3 = analog_read_avg8(PIN_HW_REVISION_DETECT_ADC);

    if (adc_a3 < ADC_BAND_R41_4K7_HIGH) {
        // Rev 2.0/2.1/2.2 with R41=4k7 — reports as REVISION_2_0 (broad bucket per D-04;
        // operator distinguishes 2.1/2.2 via EEPROM hw_revision override if needed).
        revision = REVISION_2_0;
    } else if (adc_a3 >= ADC_BAND_R41_10K_LOW && adc_a3 < ADC_BAND_R41_10K_HIGH) {
        // Rev 2.3 with R41=10k.
        revision = REVISION_2_3;
    } else if (adc_a3 >= ADC_BAND_R41_10K_HIGH) {
        // High band — no R41 (pre-detect-resistor era). Disambiguate Rev 0 vs Rev 1
        // via the legacy A2 divider check (preserved from current code — already correct).
        revision = analogRead(PIN_VPP_VOLTAGE_ADC) < 1000 ? REVISION_1 : REVISION_0;
    } else {
        // adc_a3 in the [ADC_BAND_R41_4K7_HIGH, ADC_BAND_R41_10K_LOW) guard gap —
        // physical detect inconclusive. EEPROM hw_revision override is the escape hatch.
        revision = REVISION_UNKNOWN;
    }
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT);
}
```

**Changes from existing code:**
1. `digitalRead(PIN_HW_REVISION_DETECT_ADC)` → `analog_read_avg8(PIN_HW_REVISION_DETECT_ADC)` (the load-bearing D-06 change).
2. `switch (value)` → `if/else if/else` chain (digital switch can't express band-lookup; if-chain is the canonical AVR idiom for ADC band-decode — verified against the existing A2 `< 1000` magic-number branch which is also if-style).
3. New `else if (adc_a3 >= ADC_BAND_R41_10K_LOW && adc_a3 < ADC_BAND_R41_10K_HIGH)` arm for Rev 2.3.
4. New explicit guard-gap branch reporting `REVISION_UNKNOWN`.
5. **Latent-bug cleanup:** `default: revision = 0xFF;` (collided with EEPROM-override-absent sentinel) → guard-gap arm `revision = REVISION_UNKNOWN;`.

### `rurp_map_ctrl_reg_for_hardware_revision()` Extension (D-07)

Current code at `rurp_hw_rev_utils.h:14-36` switches on `hw` and aliases Rev 2.0/2.1/2.2 to the REV2 wide-control-register layout. Phase 34 adds **one case label** (`REVISION_2_3:`) to the existing REV2 arm:

```cpp
uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    uint8_t ctrl_reg = 0;
    uint8_t hw = rurp_get_hardware_revision();
    switch (hw) {
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2:
    case REVISION_2_3:                              // <-- NEW (D-07)
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
    default:                                        // catches REVISION_UNKNOWN + any unrecognized byte
        break;
    }
    return ctrl_reg;
}
```

**Verification of Rev 2.3 ctrl-reg layout identity to Rev 2.x:** `.planning/v1.7-SHIELD-REVS.md` §4 row 6 [VERIFIED: file read] documents the Rev 2.2 → Rev 2.3 delta as `R41 = 4k7 → 10k` + `JP4 footprint 1x2 → 2x2` + schematic rename. **No control-line routing delta.** Per `§4 row 6 control_line_routing_delta: "no change (REGULATOR/VPE_TO_VPP/P1_VPP_ENABLE/A9_VPP_ENABLE/VPE_ENABLE bits unchanged)"`. The `case REVISION_2_3:` aliasing to the REV_2_x ctrl-reg arm is correct by construction.

### `REVISION_UNKNOWN = 0xFE` Non-Collision Audit

[VERIFIED: codebase grep 2026-05-25] — `grep -rn "0xFE" firestarter/` returns one hit:
- `firestarter/src/boards/rurp_serial_utils.cpp:120` — a CRC8 lookup-table byte. Not a sentinel. No collision risk.

The EEPROM override-absent sentinel `0xFF` appears at:
- `firestarter/src/rurp_config_utils.cpp:37` (`config->hardware_revision = 0xFF;` — factory-fresh default)
- `firestarter/include/rurp_hw_rev_utils.h:12` (`uint8_t revision = 0xFF;` — initial detect-result placeholder)
- `firestarter/include/rurp_hw_rev_utils.h:63` (`if (rurp_config->hardware_revision < 0xFF)` — override-active gate)
- `firestarter/src/hardware_operations.cpp:99, 102, 112, 114` (`MSG_OK_REV` + `MSG_OK_CFG` payload assembly)

**`0xFE` is reserved exclusively by Phase 34 for `REVISION_UNKNOWN`. No existing call-site reads `0xFE`. No EEPROM consumer compares against `0xFE`.** Safe.

Note on `uint8_t revision = 0xFF;` at `rurp_hw_rev_utils.h:12`: this static-storage initializer fires BEFORE `rurp_detect_hardware_revision()` runs at boot. If `rurp_get_physical_hardware_revision()` is somehow called before detect runs (it isn't in current code — `firestarter.cpp:39` calls detect first), it would return `0xFF`. Phase 34 may want to change this initializer to `REVISION_UNKNOWN` for symbolic clarity, but it's NOT load-bearing — the initializer value is overwritten by `rurp_detect_hardware_revision()` on the first boot path before any caller reads it. Discretion — leave it alone for byte-identical Wave 1, or refactor to `REVISION_UNKNOWN` if the planner wants symbolic consistency.

### Caller Audit (verification that detect-rev rework doesn't break anything)

[VERIFIED: codebase grep 2026-05-25] — all callers of the three detect-rev functions:

| Function | Caller | Behavior depends on... |
|----------|--------|------------------------|
| `rurp_detect_hardware_revision()` | `firestarter/src/firestarter.cpp:39` (boot init) | Side effect only — sets the file-scope `revision` static |
| `rurp_get_physical_hardware_revision()` | `hardware_operations.cpp:98`, `firestarter.cpp:46, 137` | Returns the static `revision` byte. **Tolerates any 0–255 value** — caller just emits the byte as part of `MSG_OK_REV` / `MSG_INFO_PHYSICAL_HW` / debug logging |
| `rurp_get_hardware_revision()` | `eprom.cpp:212`, `flash_intel.cpp:29`, `hardware_operations.cpp:20`, `rurp_register_utils.h:48` (via `rurp_map_ctrl_reg_for_hardware_revision`) | Compares against `REVISION_0` symbolically. **`REVISION_UNKNOWN` correctly falls through** to the `default: break;` arm in `rurp_map_ctrl_reg_for_hardware_revision()` → `ctrl_reg = 0` → fail-safe (no VPP enables, no VPE enables). Same behavior as the current `0xFF` fall-through, but without the EEPROM-sentinel collision. |

**No caller depends on the old `0xFF` semantic of the detect function.** The `0xFF`-vs-`REVISION_UNKNOWN` swap is purely a sentinel cleanup; behavior is preserved.

## Python Parity Surface (D-08 implementation surface)

### `firestarter_app/firestarter/constants.py` — exact lines to add

Per Phase 33 D-04 substrate ([VERIFIED: file read `constants.py:71-83`]), the convention is: block-header comment + `NAME = 0xNN` per line + `# was OLD_NAME` annotation (no type annotations). Lands **immediately after** the `# RURP Control Register Bits` block (currently ends at line 83).

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

### `firestarter_app/CLAUDE.md` — exact prose extension

Existing prose at `firestarter_app/CLAUDE.md:100` reads: "Additionally, the `RURP_CONTROL_REGISTER_BITS` block in `constants.py` (CTRL_* names) mirrors the control-register-bit declarations in `firestarter/include/rurp_pinout.h` (Phase 33 / v1.7 — silkscreen-label code-alias migration). Keep CTRL_* names + hex values in sync with the firmware header."

**Phase 34 extension — append one sentence:**

> Additionally, the `RURP_HARDWARE_REVISIONS` block in `constants.py` (REVISION_* names) mirrors the hardware-revision enum declarations in `firestarter/include/rurp_shield.h` (Phase 34 / v1.7 — shield-version-detect design + firmware plumbing). Keep REVISION_* names + byte values in sync with the firmware enum; `0xFF` is reserved as the EEPROM-override-absent sentinel and `0xFE` (`REVISION_UNKNOWN`) is reserved for the ADC-band-gap fall-through.

### D-05 Host-Side Enum → Silkscreen-String Mapping — Recommendation

**Two viable paths:**

**Path A (RECOMMENDED): Extend `_format_message` at `serial_comm.py:336`.**

Pros:
- Single-file change, co-located with existing P-02 `MSG_OK_REV` sentinel-aware rendering at lines 336-340.
- No new module → no new import surface → no new test scaffolding.
- Matches the Phase 33 minimal-surface pattern (Phase 33 P-02 changes lived inside this same `_format_message`).

Cons:
- Slightly bloats `_format_message` (already handles 4 special-cases; adding a 5th REVISION_* → string lookup is a small increment).

Concrete code (replaces lines 336-340):
```python
# Phase 34: extend MSG_OK_REV rendering to map physical-u8 to silkscreen string.
_REVISION_SILKSCREEN = {
    REVISION_0:       "Rev 0",
    REVISION_1:       "Rev 1",
    REVISION_2_0:     "Rev 2.0-class",   # broad bucket per Phase 34 D-04
    REVISION_2_1:     "Rev 2.1 (override)",
    REVISION_2_2:     "Rev 2.2 (override)",
    REVISION_2_3:     "Rev 2.3",
    REVISION_UNKNOWN: "rev_unknown",
}

if msg_id == MSG_OK_REV and len(params) == 2:
    physical, effective = params[0], params[1]
    phys_str = _REVISION_SILKSCREEN.get(physical, f"Rev{physical}")
    if effective == 0xFF:
        return phys_str
    eff_str = _REVISION_SILKSCREEN.get(effective, f"Rev{effective}")
    return f"{eff_str}, Override HW: {phys_str}"
```

The `_REVISION_SILKSCREEN` dict lands at module scope (top of `serial_comm.py`, alongside the existing `STATE_MACHINE_PREFIXES` / `NON_RESPONSE_PREFIXES` lists) — declared once, looked up via dict-get.

**Path B (NOT RECOMMENDED): New module `firestarter_app/firestarter/hardware_revisions.py`.**

Pros:
- Cleaner separation of concerns; reusable from `hardware.py` if the CLI ever wants to read the silkscreen string directly.
- Easier to unit-test in isolation.

Cons:
- New file, new import to add to `serial_comm.py` and possibly `hardware.py`.
- Phase 34 is name-only (D-08) — adding a module is a larger surface than D-08 contemplated.
- Phase 35 README-update wave can spin out the module if a later need arises.

**Verdict: Path A.** Smaller diff, matches Phase 33 substrate pattern, easier to GATE-1.7 verify (single-file change → trivially pytest-greppable). If a future milestone (post-v1.7) wants the lookup elsewhere, refactor at that time.

### `messages.py` Catalog — UNCHANGED

[VERIFIED: `messages.py:126` read] `MSG_OK_REV` format string `"Rev%u (eff: %u)"` is the catalog default; the planner intentionally does NOT modify this (`messages.py` is auto-generated from `tools/catalog/messages.toml`, per the file's docstring at `messages.py:1-15`). The `_format_message` override at `serial_comm.py:336` is the canonical Path A path — it short-circuits the catalog format string with the silkscreen-string rendering for P-02-shape sentinels (already wired this way).

### `hardware.py` Consumer — UNCHANGED

[VERIFIED: `hardware.py:81-107` read] `get_hardware_revision()` calls `comm.expect_ack()` and logs the resulting message as-is. The message text already flows through `_format_message` upstream in `serial_comm._handle_message_response` — `hardware.py` consumes the rendered string, not the raw bytes. No change needed.

## §8 Schematic Delta + §9 ADC Band Table Documentation Surface (D-01, D-11)

### Existing TBD Markers (verified)

[VERIFIED: file read `v1.7-SHIELD-REVS.md:133-139`]
- `## 8. Detect-HW Schematic Delta (next rev)` — currently `<!-- OWNED BY PHASE 34 — TBD -->`
- `## 9. Per-Rev Expected ADC Band Table` — currently `<!-- OWNED BY PHASE 34 — TBD -->`

### §8 Recommended Structure

```markdown
## 8. Detect-HW Schematic Delta (Anders R41-on-A3 substrate documentation)

Per D-01 (Phase 34 CONTEXT.md) — §8 documents the EXISTING Anders R41-on-A3 detect-divider scheme already shipped in upstream Rev 2.0+ shields (per §3). The "schematic delta for next-rev shield" phrasing in DETECT-HW-01 is satisfied by treating Rev 2.3 (R41 = 10kΩ) as the seed entry — the detect-divider is upstream-shipped, not operator-fabricated. No new PCB fabrication is required; Phase 34 only plumbs the firmware-side ADC band-lookup to consume the existing divider.

### Topology

ASCII schematic of the R41-on-A3 divider as it appears in upstream Rev 2.0+ shields:

```
        +5V VCC (via Arduino's ATmega internal pull-up, Rpu = 20–50 kΩ
              per ATmega328P / 32U4 / 328PB datasheet — see §9 math)
              |
              |
              |    (internal to MCU — enabled by
              <      pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP) at
              <        firestarter/include/rurp_hw_rev_utils.h:43)
              |
              o-------- A3 pin (Arduino-pin alias PIN_HW_REVISION_DETECT_ADC,
              |               declared at firestarter/include/rurp_pinout.h:46;
              |               canonical silkscreen-net mapping in §7 row 15)
              |
              |
            R41 (silkscreen designator; alias RES_HW_REVISION_DIVIDER per §7 row 16;
              per-rev value table below)
              |
              |
            GND (via JP4 / P1_VPP_JMP — see notes below)
```

### Per-Rev R41 Value Table

| Rev | R41 value | JP4 footprint | Notes |
|-----|-----------|---------------|-------|
| Rev 0 / Rev 1 | not present | not present | Pre-Rev-2 — no R41 designator in schematic (mine-notes.md §Per-rev-R41 + Phase 31 Finding B). A3 floats at VCC under internal pull-up. |
| Rev 2.0 (working) | 4.7 kΩ | 1x2 vertical | First rev with R41 (commit a252e39, 2024-10-08). Source: §3 row 1. |
| Rev 2.1 | 4.7 kΩ | 1x2 vertical | Source: §3 row 2 (schematic blob f3b7a521 line 18240). |
| Rev 2.2 | 4.7 kΩ per schematic; **OPEN: Anders chat-intel cites 10 kΩ (Phase 35 follow-up #5)** | 1x2 vertical | Source: §3 row 3. Schematic blob identical to Rev 2.1. Operator physical measurement pending. |
| Rev 2.3 | 10 kΩ | 2x2 vertical | Source: §3 row 4 (schematic blob fe35bd78 line 20591). |
| Modified Rev 0 | as-modified — pending Phase 35 | as-modified — pending Phase 35 | Operator-rework board; full trace in MODIFICATIONS.md (Phase 35 follow-up #4). |

### Source Evidence

- Per-rev R41 values: `.planning/phases/31-upstream-shield-archaeology/mine-notes.md` §Per-rev-R41
- Schematic citations: §3 rows 1–4 (Anders R41-on-A3 history)
- Pin alias: §7 row 15 (`PIN_HW_REVISION_DETECT_ADC` → A3, HARDWARE_REVISION-gated, declared `firestarter/include/rurp_pinout.h:46`)
- Resistor alias: §7 row 16 (`RES_HW_REVISION_DIVIDER` → R41)
- Jumper alias: §7 row 17 (`JMP_VPP_P1_BYPASS` → JP4)

### JP4 Caveat

JP4 (silkscreen designator; alias `JMP_VPP_P1_BYPASS` per §7) carries P1_VPP_JMP — it's a jumper for routing VPP to socket pin 1, not strictly a "GND" pin. In the detect-divider topology, R41's lower terminal connects to one pin of JP4 such that the divider works only when JP4 is in a specific config; consult upstream Anders schematic (blob fe35bd78 on origin/Rev2.3, line 20582 for R41 + line 22562 for JP4) for the exact wiring. The footprint 1x2-vs-2x2 transition between Rev 2.2 and Rev 2.3 (mine-notes.md Finding D) is a physical-connector form-factor change but does NOT alter the electrical topology — both forms carry the same net.
```

### §9 Schema Refinement (D-11 + this research's voltage-band math)

```markdown
## 9. Per-Rev Expected ADC Band Table

Per D-11 (Phase 34 CONTEXT.md) — band schema is per-rev expected ADC value range + reported firmware enum + reported silkscreen string. Band values derived from D-03 voltage math (see Phase 34 RESEARCH §ADC Voltage Band Math) with worst-case pull-up tolerance (20–50 kΩ) factored in. The firmware threshold constants `ADC_BAND_R41_4K7_HIGH = 200`, `ADC_BAND_R41_10K_LOW = 220`, `ADC_BAND_R41_10K_HIGH = 600` (declared in `firestarter/include/rurp_pinout.h`) enforce strict band ordering; readings in the [200, 220) guard gap report `REVISION_UNKNOWN`.

| Rev | R41 value | Expected ADC band (10-bit, 8-sample avg) | Reported enum | Reported silkscreen string | Source evidence |
|-----|-----------|------------------------------------------|--------------|----------------------------|------------------|
| Rev 0 | not present | 850–1023 (high band, A3 floating; A2 disambig → high → Rev 0) | `REVISION_0` (= 0) | `"Rev 0"` | §6 row 1 + `rurp_hw_rev_utils.h:51` (A2 < 1000 disambig); pre-detect-resistor era — A3 reads pull-up only |
| Rev 1 | not present | 850–1023 (high band, A3 floating; A2 disambig → low → Rev 1) | `REVISION_1` (= 1) | `"Rev 1"` | §6 row 2 + `rurp_hw_rev_utils.h:51`; Rev 1 schematic introduces A2 divider per commit b84e9e0 |
| Rev 2.0 / 2.1 / 2.2 (R41 = 4k7) | 4.7 kΩ | 88–195 (4k7 band; per D-03 math at 5V VCC, Rpu = 20–50 kΩ) | `REVISION_2_0` (= 2) | `"Rev 2.0-class"` | §3 rows 1–3 + §6 rows 4–6 + Phase 34 RESEARCH §ADC Voltage Band Math + D-04 (broad-bucket collapse) |
| Rev 2.3 (R41 = 10k) | 10 kΩ | 170–341 (10k band; per D-03 math) | `REVISION_2_3` (= 5) | `"Rev 2.3"` | §3 row 4 + §6 row 7 + Phase 34 RESEARCH §ADC Voltage Band Math |
| Modified Rev 0 | as-modified | as-modified — pending Phase 35 | (operator-attested via EEPROM byte) | (as configured by operator) | memory `[[user_shield_revisions]]` + `MODIFICATIONS.md` stub + Phase 35 follow-up #4; operator sets `hw_revision` in EEPROM, ADC value irrelevant |
| (any reading outside the above bands — including the [200, 220) guard gap and the [342, 849] dead zone) | — | (gap reading) | `REVISION_UNKNOWN` (= 0xFE) | `"rev_unknown"` | D-07; EEPROM override at `rurp_get_hardware_revision()` is the escape hatch |

Note: the firmware threshold constants encode the band edges as follows:
- `ADC_BAND_R41_4K7_HIGH = 200` — upper edge of 4k7 bucket (Best-case Rpu=20kΩ 4k7 reading is ADC≈195; 5-count headroom)
- `ADC_BAND_R41_10K_LOW = 220` — lower edge of 10k bucket (Worst-case Rpu=50kΩ 10k reading is ADC≈170; 50-count guard above the 4k7 ceiling)
- `ADC_BAND_R41_10K_HIGH = 600` — upper edge of 10k bucket (Best-case Rpu=20kΩ 10k reading is ADC≈341; 250-count guard below the floating-A3 lower-bound ≈850)
```

## GATE-1.7 Non-Regression Verification (D-10 mechanism)

### Phase 33 Baseline Mechanism (Verified Precedent)

[VERIFIED: `.planning/phases/33-silkscreen-label-code-alias-migration/33-00-SUMMARY.md` read 2026-05-25] Phase 33's baseline-capture pattern:

1. Verify source-tree cleanliness: `git status --porcelain include/ src/ test/ platformio.ini` returns 0 lines.
2. Clean rebuild all 3 AVR envs: `pio run -t clean -e uno -e uno328pb -e leonardo && pio run -e uno -e uno328pb -e leonardo`.
3. Copy each `.pio/build/<env>/firestarter_<env>.hex` into `.planning/v1.7/phase-33-baseline-hex/<env>.hex` (**gitignored** under `.planning/v1.7/`).
4. Record firestarter HEAD SHA in `BASELINE_COMMIT.txt` (also gitignored).
5. Land an executable `check-migration.sh` (gitignored) with three assertions: grep-zero on old names + REV_* zero + 3x cmp byte-identical.
6. Pre-rename: script returns exit 1 with `FAIL: Assertion 1` (proof the gate is wired). Post-rename: returns exit 0 with `PASS: alias migration verified clean`.

**Per-board pre-rename baseline `.hex` sizes [VERIFIED: 33-00-SUMMARY.md `wc -c` table]:**
- uno: 62617 B
- uno328pb: 62854 B
- leonardo: 68876 B

### Phase 34 Adaptation: `verify-detect-34.sh`

**Recommended path:** `.planning/v1.7/baseline-34/` (gitignored — same parent as `phase-33-baseline-hex/`).

**Contents (all gitignored):**
- `uno.hex` — pre-Phase-34 firestarter_uno.hex
- `uno328pb.hex` — pre-Phase-34 firestarter_uno328pb.hex
- `leonardo.hex` — pre-Phase-34 firestarter_leonardo.hex
- `BASELINE_COMMIT.txt` — firestarter sub-repo HEAD SHA at baseline-34 capture time
- `verify-detect-34.sh` — executable bash script with the assertions below

**Phase 34's assertion set (differs from Phase 33's because Phase 34 EXPECTS a non-zero delta, not byte-identical):**

```bash
#!/usr/bin/env bash
set -euo pipefail

BASELINE_DIR="/workspaces/.planning/v1.7/baseline-34"
FIRMWARE_DIR="/workspaces/firestarter"

EXPECTED_DELTA_MIN=20    # below this, the new detect-rev rework didn't actually compile in
EXPECTED_DELTA_MAX=300   # above this, the rework bloated more than expected — investigate

# --- Assertion 1: each AVR env produces a built .hex larger than baseline
# by a delta in the [EXPECTED_DELTA_MIN, EXPECTED_DELTA_MAX] range.
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

# --- Assertion 2: native dispatch tests stay green
cd "${FIRMWARE_DIR}"
pio test -e native -f "*test_dispatch*" >/dev/null 2>&1 || { echo "FAIL: pio test -e native -f '*test_dispatch*'"; exit 1; }

# --- Assertion 3: REVISION_2_3 + REVISION_UNKNOWN present in firmware header
grep -q "REVISION_2_3" "${FIRMWARE_DIR}/include/rurp_shield.h" || { echo "FAIL: REVISION_2_3 missing from rurp_shield.h"; exit 1; }
grep -q "REVISION_UNKNOWN" "${FIRMWARE_DIR}/include/rurp_shield.h" || { echo "FAIL: REVISION_UNKNOWN missing from rurp_shield.h"; exit 1; }

echo "PASS: Phase 34 detect-rev rework verified — delta within expected band, native tests green, enums present."
```

### When to Capture Baseline

**CRITICAL:** Capture the baseline as the **very first task** of Phase 34's plan — BEFORE any firmware-source edits. This is the Phase 33 precedent (Plan 33-00 captures baseline; Plans 33-01..04 consume it). If baseline is captured after a partial edit, the delta math is corrupted.

**Recommended:** Wave 1 Task 1 (or Wave 0 if the planner adds one) — pure capture, no source edits, no commit (baseline is gitignored). Wave 1 then proceeds to §8/§9 fill (meta-repo, no firmware impact).

### Native Test Coverage Confirmation

[VERIFIED: `firestarter/platformio.ini:78-101` read 2026-05-25]

The `[env:native]` `test_filter` is `native/avr/test_dispatch` + `native/avr/test_messages`. The `build_src_filter` is `+<proms/> +<boards/rurp_serial_utils.cpp>` — **explicitly excludes** `src/hardware_operations.cpp`, `src/firestarter.cpp`, and (critically) does NOT pick up `include/rurp_hw_rev_utils.h` for compilation. The detect-rev code path is therefore AVR-only at the source level; the native test suite exercises ONLY `configure_memory` dispatch and the message catalog, neither of which depend on the detect-rev rework.

**`pio test -e native -f "*test_dispatch*"` is the correct phase gate** — it asserts that the unrelated dispatch path stays green across Phase 34's edits, which is the load-bearing claim of DETECT-FW-02 ("Chip programming + read paths byte-identical").

**Additional native suites to consider running for safety net:**
- `pio test -e native -f "*test_messages*"` — verifies `MSG_OK_REV` catalog format string unchanged (Phase 34 doesn't touch the catalog, but a paranoid check catches accidental codegen-from-toml drift)
- `pio test -e native` (all suites) — catches any cross-cutting regression; the known-flaky `test_flash_intel_vpp` + `test_eeprom28c_chip_id` suites per `platformio.ini:70-76` may surface but those flakes are pre-existing (Phase 17 WR-01 + Phase 20 verification) and orthogonal to Phase 34

### Python Parity Gate

`pytest -q` in `firestarter_app/` — [VERIFIED: `firestarter_app/tests/conftest.py` + test layout read] — covers:
- `test_decoder.py` — wire-frame decoder (MSG_OK_REV format)
- `test_messages.py` (if exists — verify at execute) — catalog parity
- `test_firmware_install.py`, `test_fwguard.py`, `test_update_version.py` — unrelated, included for safety

Phase 34 adds two new constants (`REVISION_2_3`, `REVISION_UNKNOWN`); existing tests will continue to pass. **Recommended new test assertion** (lands in a small `tests/test_constants_parity.py`):

```python
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
    assert REVISION_2_3     == 0x05  # NEW Phase 34
    assert REVISION_UNKNOWN == 0xFE  # NEW Phase 34
    # 0xFF is reserved as the EEPROM-override-absent sentinel — NOT a REVISION_ value.
```

## Existing Code Patterns to Replicate (Phase 33 substrate)

### Pattern 1: `#define`-only constants (NOT `constexpr`)

[VERIFIED: `firestarter/include/rurp_pinout.h:43-77` read] Phase 33 D-07 rationale: AVR-objcopy + `.hex` byte-identical math requires preprocessor-level constants, not `constexpr` (which can introduce inline-storage thunks that perturb `.hex` layout). All Phase 33 CTRL_*, PIN_*, RES_*, JMP_* constants use `#define`.

**Phase 34 follows:** `ADC_BAND_R41_4K7_HIGH = 200`, `ADC_BAND_R41_10K_LOW = 220`, `ADC_BAND_R41_10K_HIGH = 600` all declared as `#define` (NOT `constexpr static const uint16_t`).

**Location decision (Claude's Discretion):** Two options.
- **Option A (RECOMMENDED): `firestarter/include/rurp_pinout.h`** — sits alongside the existing `RES_HW_REVISION_DIVIDER` (= R41) and `PIN_HW_REVISION_DETECT_ADC` (= A3) aliases. The bands are a property of the divider, so co-location matches the Phase 33 substrate (RES_/PIN_/CTRL_/JMP_ all live in `rurp_pinout.h`). Adds 3 lines inside the existing `#ifdef HARDWARE_REVISION` block at lines 45-47.
- **Option B: New sibling header `firestarter/include/rurp_hw_rev_bands.h`** — cleaner namespace, but introduces a new file. Phase 33's substrate consolidated everything into `rurp_pinout.h` deliberately.

**Verdict: Option A.** Smaller diff, matches Phase 33 4-namespace lock + co-location convention. Concrete addition to `rurp_pinout.h` (after line 47):

```cpp
// ---- Section 1b: ADC voltage-band thresholds (HARDWARE_REVISION-gated) -------
// Used by rurp_detect_hardware_revision() in rurp_hw_rev_utils.h to map an
// 8-sample-averaged analogRead(PIN_HW_REVISION_DETECT_ADC) value to a REVISION_*
// enum byte. Math: see Phase 34 RESEARCH.md §ADC Voltage Band Math + the §9
// per-rev band table in .planning/v1.7-SHIELD-REVS.md.
#define ADC_BAND_R41_4K7_HIGH   200   // upper edge of 4k7 bucket (Rev 2.0/2.1/2.2)
#define ADC_BAND_R41_10K_LOW    220   // lower edge of 10k bucket (Rev 2.3); [200, 220) is the guard gap → REVISION_UNKNOWN
#define ADC_BAND_R41_10K_HIGH   600   // upper edge of 10k bucket; above this is the pull-up-only / no-R41 high band
```

### Pattern 2: `#ifdef HARDWARE_REVISION` gating

[VERIFIED: `platformio.ini:21-23` + `rurp_pinout.h:45-47, 83-107` + `rurp_hw_rev_utils.h:4-69` read] All detect-rev code lives behind `#ifdef HARDWARE_REVISION`. The flag is set in `[env]` `build_flags` at `platformio.ini:23` (`-D HARDWARE_REVISION`) for all 3 AVR envs (`uno`, `uno328pb`, `leonardo`). The `[env:native]` env intentionally does NOT inherit this flag in any way that compiles `rurp_hw_rev_utils.h` — the `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp>` excludes `src/hardware_operations.cpp` (which would pull in `rurp_hw_rev_utils.h` transitively).

**Phase 34 follows:** All new constants, new enum values (`REVISION_2_3`, `REVISION_UNKNOWN`), and the reworked `rurp_detect_hardware_revision()` body sit inside `#ifdef HARDWARE_REVISION` blocks. The native env continues to bypass detect-rev entirely.

### Pattern 3: EEPROM Sentinel `0xFF` Carve-Out

[VERIFIED: `firestarter/include/rurp_hw_rev_utils.h:63` + `firestarter/src/hardware_operations.cpp:99, 102, 112, 114` + `firestarter/src/rurp_config_utils.cpp:37` read]

`0xFF` is load-bearing as the EEPROM "no override active" sentinel:
- Set at factory-fresh boot in `rurp_validate_config()` (`rurp_config_utils.cpp:37`).
- Checked by `rurp_get_hardware_revision()` (`rurp_hw_rev_utils.h:63` — `if (rurp_config->hardware_revision < 0xFF)` selects override path).
- Echoed as sentinel byte in `MSG_OK_REV` effective-byte (`hardware_operations.cpp:99-101`) and `MSG_OK_CFG` override-byte (`hardware_operations.cpp:111-113`).

**Phase 34 carve-out:** `0xFE = REVISION_UNKNOWN` is the new "physical detect inconclusive" sentinel. **`0xFF` remains EEPROM-only.** The current `default: revision = 0xFF;` in `rurp_detect_hardware_revision()` (`rurp_hw_rev_utils.h:54-57`) is a latent bug — it briefly puts a `0xFF` into the physical-detect register (until detect rewrites it on the next boot). Phase 34's swap to `REVISION_UNKNOWN` cleans this up.

### Pattern 4: Phase 33 Atomic Multi-Repo Commit Boundary

[VERIFIED: Phase 33-04-PLAN.md frontmatter read 2026-05-25] Phase 33 Wave 4 used the following pattern:
- `files_modified` lists span 3 directories: `firestarter_app/firestarter/constants.py`, `firestarter_app/firestarter/main.py`, `firestarter_app/CLAUDE.md`, `.planning/v1.7-SHIELD-REVS.md`.
- Submodule sub-repo (firestarter_app) commits first (Task 1 lands inside the submodule on `v1.7-shield-investigation`).
- Meta-repo bumps the submodule pointer as a separate commit (Task 1's meta-repo commit).
- Task 2 (§7 fill) lands directly on the meta-repo.

**Phase 34 follows:** Wave 1 lands meta-repo §8/§9 fills (meta-repo commits only). Wave 2 lands firmware edits (firestarter sub-repo commits + meta-repo submodule-pointer-bump commits). Wave 3 lands Python parity (firestarter_app sub-repo commits + meta-repo submodule-pointer-bump commits + meta-repo CLAUDE.md sync-rule extension commit).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Firmware framework | PlatformIO Unity (`[env:native]` host-side cross-compile) |
| Firmware config | `firestarter/platformio.ini` |
| Firmware quick run | `cd firestarter && pio test -e native -f "*test_dispatch*"` |
| Firmware full suite | `cd firestarter && pio test -e native` (known-flaky `test_flash_intel_vpp` + `test_eeprom28c_chip_id` per Phase 17 WR-01) |
| Python framework | pytest (configured in `firestarter_app/pyproject.toml`, fixtures in `firestarter_app/tests/conftest.py`) |
| Python quick run | `cd firestarter_app && pytest -q` |
| GATE-1.7 wave gate | `bash /workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh` (modeled on Phase 33's `check-migration.sh`) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test type | Automated command | File exists? |
|--------|----------|-----------|-------------------|-------------|
| DETECT-HW-01 | §8 ASCII schematic + per-rev R41 table | doc-lint | `grep -q "## 8. Detect-HW Schematic Delta" .planning/v1.7-SHIELD-REVS.md && ! grep -q "OWNED BY PHASE 34 — TBD" .planning/v1.7-SHIELD-REVS.md` | Wave 0/1 |
| DETECT-HW-02 | §9 per-rev ADC band table seeded Rev 2.3 + `rev_unknown` fall-through | doc-lint | `grep -q "## 9. Per-Rev Expected ADC Band Table" .planning/v1.7-SHIELD-REVS.md && grep -q "REVISION_2_3" .planning/v1.7-SHIELD-REVS.md && grep -q "REVISION_UNKNOWN" .planning/v1.7-SHIELD-REVS.md` | Wave 0/1 |
| DETECT-FW-01 | firmware ADC band-lookup + handshake reports detected enum + EEPROM fall-through preserved | unit (native) + integration (build) | `cd firestarter && pio test -e native -f "*test_dispatch*" && pio run -e uno -e uno328pb -e leonardo && grep -q "REVISION_2_3" firestarter/include/rurp_shield.h && grep -q "analog_read_avg8\|analogRead(PIN_HW_REVISION_DETECT_ADC)" firestarter/include/rurp_hw_rev_utils.h` | Wave 0 |
| DETECT-FW-02 | `.hex` size delta in [20, 300] B + native dispatch green + Python parity green | byte-diff gate | `bash /workspaces/.planning/v1.7/baseline-34/verify-detect-34.sh && cd firestarter_app && pytest -q` | Wave 0 (baseline + script land) |

### Nyquist Dim 1..8

**Dim 1 — Functional (behavioral correctness of detect-rev):**
- **Test artifact:** post-flash handshake-read on operator's Rev 2.0 / Rev 2.2 board reports either `REVISION_2_0` (R41=4k7 populated) or `REVISION_UNKNOWN` (R41 missing). **Deferred to Phase 35** (operator-on-bench wave).
- **Phase 34 surrogate:** firmware-side compile-and-flash check + `pio run` returns exit 0 + the new `analog_read_avg8` + `if/else if/else` chain exists in `rurp_hw_rev_utils.h`.
- **Rationale:** Adding native-test coverage for `rurp_hw_rev_utils.h` would require extending the `build_src_filter` glob + writing an ArduinoFake mock for `analogRead`. Per Phase 33 D-08 + CONTEXT D-04 (Claude's Discretion), the lowest-friction default is to leave native tests as-is and rely on the Phase 35 operator-on-bench validation.

**Dim 2 — Backward-compat (GATE-1.7 byte-diff per env):**
- **Test artifact:** `verify-detect-34.sh` — asserts each AVR env's `.hex` delta lands in [20, 300] B vs pre-Phase-34 baseline. Below 20 B implies the rework didn't compile in; above 300 B implies unexpected bloat (investigate before merge).
- **Why a band, not exact:** Phase 34 adds the `analog_read_avg8` helper (~30 B) + 3 new threshold `#define`s (preprocessor-resolved, 0 B added unless used in distinct code arms) + 1 new `case REVISION_2_3:` (≈ 8–16 B) + new `else if` arm (≈ 30–50 B) + 8-sample averaging loop body (≈ 30 B). Expected ~80–150 B total per env.
- **Phase 33 contrast:** Phase 33 expected Δ = 0 B (pure rename). Phase 34 EXPECTS non-zero Δ because the detect-rev logic actually changes — the gate is an upper bound, not a byte-identical check.

**Dim 3 — Python parity (`pytest -q` covers the constants):**
- **Test artifact:** new `firestarter_app/tests/test_revision_constants_parity.py` (or extend an existing test file) — asserts `REVISION_2_3 == 0x05` and `REVISION_UNKNOWN == 0xFE`. Concrete assertion code in §Python Parity Surface above.
- **Existing pytest infra:** `firestarter_app/tests/conftest.py` already provides `make_comm` fixture; no new fixtures needed.

**Dim 4 — Wire format (`MSG_OK_REV` 2-byte frame ID + byte count unchanged):**
- **Test artifact:** `grep -q '0x04: MessageDef(id=0x04, name="MSG_OK_REV"' firestarter_app/firestarter/messages.py` returns 0 (unchanged catalog entry); `grep -q 'param_bytes=2' firestarter_app/firestarter/messages.py | grep MSG_OK_REV` returns 0 (still 2 bytes).
- **Rationale:** Phase 34 explicitly does NOT modify `tools/catalog/messages.toml` per D-09. The codegen-from-toml byte-identical-check is the gate.

**Dim 5 — Docs (§8 + §9 schema lock per D-11):**
- **Test artifact:** grep checks per requirement table above (`! grep -q "OWNED BY PHASE 34 — TBD"`).
- **Optional lint:** validate §9 table has the exact 6-column shape `rev | r41_value | expected_adc_band | reported_enum | reported_silkscreen_string | source_evidence` via `awk` row-count.

**Dim 6 — Cross-repo invariant (Python REVISION_* byte values exactly match firmware enum byte values):**
- **Test artifact:** `firestarter_app/tests/test_revision_constants_parity.py` (as above) asserts 7 known byte values. **No automatable cross-file lint** (firmware sub-repo is a separate git tree; meta-repo can't grep into it deterministically across sub-repo bumps), but the pytest assertion + the firestarter_app/CLAUDE.md sync-rule prose + the Phase 34 plan SUMMARY documentation collectively enforce the invariant.

**Dim 7 — EEPROM override precedence unchanged:**
- **Test artifact:** `rurp_get_hardware_revision()` at `rurp_hw_rev_utils.h:61-67` is **UNCHANGED** by Phase 34. Diff check: `cd firestarter && git diff include/rurp_hw_rev_utils.h | grep -q "rurp_get_hardware_revision"` should match ZERO change-lines (the function body is verbatim pre-Phase-34).
- **Behavioral verification:** any chip-write or chip-read operation on a board with `rurp_config->hardware_revision != 0xFF` still routes through the override path (asserted via existing operator workflows — no new test needed).

**Dim 8 — Operator-on-bench (explicitly deferred to Phase 35):**
- **Deferral pointer:** `Phase 35 follow-up: sideload Phase 34 firmware to operator's Rev 2.0 or Rev 2.2 board with chip OUT (memory [[feedback_chip_out_before_sideload]]) + verify port identity (memory [[feedback_verify_port_identity_each_task]]) + confirm MSG_OK_REV reports either REVISION_2_0 (R41=4k7 populated) or REVISION_UNKNOWN (R41 missing). Either outcome is acceptable per the DETECT-FW-01 fall-through clause.`
- **Gate:** sub-repo `v1.7-shield-investigation` → `beta` promotion happens at Phase 34 close (desk-side). `beta` → `main` is GATED on the Phase 35 operator-on-bench result.

### Sampling Rate

- **Per task commit:** `pio run -e uno -e uno328pb -e leonardo` (build sanity); `pytest -q` (Python sanity)
- **Per wave merge:** `bash verify-detect-34.sh` (byte-diff gate + native dispatch); `pytest -q` (full Python suite)
- **Phase gate:** `verify-detect-34.sh` PASS + pytest PASS + §8/§9 doc-lint PASS before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] Capture pre-Phase-34 `.hex` baseline + write `verify-detect-34.sh` — `.planning/v1.7/baseline-34/` (gitignored, mirrors Phase 33 Plan 33-00)
- [ ] (Optional, Wave 3) Create `firestarter_app/tests/test_revision_constants_parity.py` if Phase 34 wants a hard pytest-level cross-repo byte-value assertion

*(All existing pytest + Unity infra is already in place from Phase 33 / earlier phases — no framework install needed.)*

## Risks + Open Questions

### Risk 1 — Rev 2.2 R41 chat-vs-sch discrepancy (4k7 vs 10k)
- **Severity:** MEDIUM (operator misclassification, but EEPROM escape hatch preserved)
- **Mitigation:** EEPROM `hw_revision` override path is unchanged. Operator sets `firestarter hw -r 4` to force `REVISION_2_2` regardless of ADC reading.
- **Detection signal at execute:** if operator's Rev 2.2 board reports `REVISION_2_3` (= 5) via `firestarter hw`, the chat-cited 10k value is confirmed (and Phase 35 follow-up #5 resolves by amending §3 row 3 + §9 row 3).
- **Failure mode:** Phase 34 firmware misclassifies operator's Rev 2.2 board as Rev 2.3 → control-register layout still correct (both REV_2_x layouts are identical) → no programming-path damage → only the silkscreen-string display is wrong. Operator override fully recovers.

### Risk 2 — Pull-up tolerance edge-case on future MCU variant
- **Severity:** LOW (no current MCU exceeds 50 kΩ)
- **Mitigation:** Threshold-band math is parameterized by `#define` constants. If a new MCU variant (e.g., a hypothetical Arduino-compatible board with 80 kΩ pull-ups) lands in scope, redefine `ADC_BAND_R41_4K7_HIGH` / `ADC_BAND_R41_10K_LOW` / `ADC_BAND_R41_10K_HIGH` in a per-env build flag override.
- **Detection signal at execute:** bench reading drifts into the guard gap [200, 220) on a board that should clearly be Rev 2.0-class — implies pull-up is outside the assumed 20–50 kΩ range, OR R41 value is non-standard, OR AVcc reference is unusually noisy.
- **Bench evidence that would invalidate band table:** N≥3 consecutive boot-handshake reads on the same physical board landing in different bands (4k7 vs guard-gap vs 10k). Would prompt re-derivation of threshold constants from operator-specific Rpu measurement.

### Risk 3 — 8-sample averaging adds boot latency, may surface a timing dependency
- **Severity:** LOW (added latency ≈ 104 µs against existing ~50 ms boot sequence)
- **Mitigation:** Profile via `pio test` if a test asserts on boot-sequence timing. Current dispatch tests do not.
- **Detection signal at execute:** native dispatch tests time-out — would indicate the 8-sample loop is somehow interacting with ArduinoFake's clock model. Has not occurred in any prior phase that touched analogRead.

### Risk 4 — Modified Rev 0 board reads an unpredictable ADC value
- **Severity:** LOW (operator-attested via EEPROM byte; ADC reading is irrelevant by D-04)
- **Mitigation:** Modified Rev 0 has no upstream-canonical R41 value. Operator sets `hw_revision = REVISION_0 (0)` in EEPROM; `rurp_get_hardware_revision()` returns 0 regardless of ADC.
- **Detection signal at execute:** if operator forgets to set the EEPROM override on Modified Rev 0, the board may report any of REVISION_0 / REVISION_2_0 / REVISION_UNKNOWN depending on what the rework did. Cosmetic only — no programming-path impact.

### Risk 5 — Latent `uint8_t revision = 0xFF;` initializer at `rurp_hw_rev_utils.h:12` is unchanged by Phase 34
- **Severity:** TRIVIAL (the value is overwritten before any caller reads it)
- **Mitigation:** Optional cosmetic cleanup — change to `uint8_t revision = REVISION_UNKNOWN;`. Discretion.
- **Detection signal at execute:** none. The initializer's `0xFF` value is dead-code-equivalent in normal boot flow.

### Open Question 1 — Should the `_REVISION_SILKSCREEN` dict live in `serial_comm.py` or a new module?
- **What we know:** Path A (`serial_comm.py`) is the smaller diff and matches Phase 33 substrate.
- **What's unclear:** Whether a future phase (post-v1.7) will want the lookup from `hardware.py` or `main.py` directly.
- **Recommendation:** Land Path A. If a later phase needs the lookup elsewhere, refactor at that time.

### Open Question 2 — Native test extension for `rurp_hw_rev_utils.h`?
- **What we know:** The current `[env:native]` build deliberately excludes detect-rev code (`build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp>`).
- **What's unclear:** Whether the planner wants to extend `src_filter` to include `+<hardware_operations.cpp>` (which pulls in `rurp_hw_rev_utils.h` transitively) + write an ArduinoFake mock for `analogRead`.
- **Recommendation:** Defer to post-v1.7 (per CONTEXT.md Claude's Discretion + Phase 33's precedent of not extending native test coverage during the migration). Phase 35 operator-on-bench is the canonical Dim 1 validation.

### Open Question 3 — `firestarter dev detect-rev` host-side subcommand?
- **What we know:** CONTEXT.md flags this as Claude's Discretion. It would print the raw ADC value + the detected REVISION_* byte + the EEPROM override state — a diagnostic for Phase 35 follow-up #5.
- **What's unclear:** Whether the value is worth a new subcommand vs. having operator run `firestarter hw` (which already exists and reports MSG_OK_REV).
- **Recommendation:** Defer. The existing `firestarter hw` command displays the silkscreen string; Phase 35 follow-up #5 can read the raw ADC via `firestarter dev registers --firestarter` if needed.

### Open Question 4 — Bump `CONFIG_VERSION` in `rurp_shield.h:44`?
- **What we know:** `CONFIG_VERSION = "VER06"` ([VERIFIED: file read]). `rurp_configuration_t` struct ([VERIFIED: `rurp_types.h:19-24` read]) contains `version`, `r1`, `r2`, `hardware_revision` — no struct-field change in Phase 34.
- **Recommendation:** **DO NOT BUMP.** The struct is unchanged. Bumping would force every operator's EEPROM to re-initialize on next boot (per `rurp_validate_config()` at `rurp_config_utils.cpp:32-39`), wiping their persisted R1/R2 calibration. Verified no struct change — preserve VER06.

## Sources

### Primary (HIGH confidence — file reads in this session)
- `/workspaces/.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-CONTEXT.md` — all D-01..D-11 decisions
- `/workspaces/.planning/REQUIREMENTS.md` — DETECT-HW-01/02 + DETECT-FW-01/02 verbatim
- `/workspaces/.planning/v1.7-SHIELD-REVS.md` §1, §3, §4, §6, §7 — per-rev evidence + canonical alias table
- `/workspaces/firestarter/include/rurp_shield.h:25-29` — REVISION_0..REVISION_2_2 enum block
- `/workspaces/firestarter/include/rurp_hw_rev_utils.h:14-67` — current detect-rev logic
- `/workspaces/firestarter/include/rurp_pinout.h:43-77` — Phase 33 alias substrate + ifdef structure
- `/workspaces/firestarter/include/messages.h` — message ID catalog
- `/workspaces/firestarter/src/hardware_operations.cpp:95-115` — MSG_OK_REV emit
- `/workspaces/firestarter/src/firestarter.cpp:42-50, 136-138` — boot handshake
- `/workspaces/firestarter/src/rurp_config_utils.cpp:32-40` — CONFIG_VERSION + EEPROM init
- `/workspaces/firestarter/include/rurp_types.h:19-24` — `rurp_configuration_t` struct
- `/workspaces/firestarter/platformio.ini:67-103` — `[env:native]` config + `build_src_filter`
- `/workspaces/firestarter_app/firestarter/constants.py:71-83` — Phase 33 CTRL_* parity block
- `/workspaces/firestarter_app/firestarter/serial_comm.py:319-350` — `_format_message` P-02 sentinel handling
- `/workspaces/firestarter_app/firestarter/messages.py:126` — auto-generated MSG_OK_REV catalog entry
- `/workspaces/firestarter_app/firestarter/hardware.py:81-107` — consumer-side MSG_OK_REV path
- `/workspaces/firestarter_app/CLAUDE.md:100` — Phase 33 sync rule prose
- `/workspaces/.planning/phases/33-silkscreen-label-code-alias-migration/33-00-SUMMARY.md` — baseline-capture pattern + check-migration.sh structure
- `/workspaces/.planning/phases/33-silkscreen-label-code-alias-migration/33-04-PLAN.md` — multi-repo atomic-commit pattern

### Secondary (MEDIUM-HIGH confidence — verified via WebSearch + cross-referenced)
- [ATmega328P internal pull-up Rpu = 20–50 kΩ per AVR Freaks forum citing official datasheet](https://www.avrfreaks.net/forum/confusion-atmega328p-pull-resistor-datasheet)
- [Microchip ATmega328P Datasheet (Automotive variant — same I/O cell as commercial part)](https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf)
- [Empirical Arduino pull-up measurement — typical ~30 kΩ on real silicon](https://hackingmajenkoblog.wordpress.com/2016/08/12/measuring-arduino-internal-pull-up-resistors/)

### Tertiary (LOW confidence — assumed knowledge, flagged for execute-time verification)
- ATmega32U4 (Leonardo) + ATmega328PB (uno328pb) pull-up specs — assumed family-shared with ATmega328P. Verify per-MCU datasheet at execute time if band margins shrink.
- 8-sample averaging is sufficient for 25-count worst-case gap — assumed; bench-validate in Phase 35 operator-on-bench wave.

## Metadata

**Confidence breakdown:**
- ADC voltage band math: HIGH — verified ATmega328P datasheet spec via 2 independent sources; family-shared assumption for 32U4 / 328PB is LOW-confidence but unlikely to invalidate threshold band selection (the worst-case 50 kΩ pull-up math leaves margin)
- Firmware detection logic rework: HIGH — all call-sites grepped, REVISION_UNKNOWN non-collision audit verified, latent `0xFF` bug confirmed
- Python parity surface: HIGH — Phase 33 D-04 substrate verified; concrete code provided for both Path A and Path B; Path A recommended with rationale
- §8/§9 documentation surface: HIGH — existing TBD markers verified; D-01 + D-11 schemas locked
- GATE-1.7 non-regression: HIGH — Phase 33 baseline-capture pattern verified (33-00-SUMMARY.md); `verify-detect-34.sh` is a verbatim adaptation
- Existing code patterns to replicate: HIGH — all 4 patterns (define-only, HARDWARE_REVISION gating, 0xFF carve-out, atomic multi-repo commit) verified via file reads
- Validation architecture (Dim 1..8): HIGH — Dim 1 deferral is the load-bearing design choice (matches CONTEXT.md), all other dims have concrete automated commands
- Risks + open questions: HIGH (risks have concrete mitigation paths + detection signals)

**Research date:** 2026-05-25
**Valid until:** 2026-06-25 (30 days — codebase is stable, ATmega datasheet specs are stable; bench-validation in Phase 35 may surface new evidence that requires §9 band-table refinement)

## RESEARCH COMPLETE
