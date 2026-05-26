# RURP Shield Revision Reference

This is the canonical per-revision reference for RURP shield hardware revisions
used with the Firestarter firmware. It captures what every silkscreen-version
string maps to in code, which chip families and algorithms each revision
supports, the silkscreen → code alias table consumed by
`firestarter/include/rurp_pinout.h`, and the per-revision ADC band lookup the
firmware uses to detect the connected shield at boot.

If you have a shield in hand and want to know "what rev is this and what can
it do", read [§1 (inventory)](#1-inventory) + [§2 (capability matrix)](#2-per-rev-capability-matrix).
If you are reading the firmware source and need to know "what does this
silkscreen label mean in code", read [§3 (alias table)](#3-silkscreen--code-alias-table).
If the firmware reports `rev_unknown` and you want to override detection, set
the EEPROM byte via the host CLI: `firestarter rev <N>` (see the `firestarter_app`
README for the byte values).

Full investigation history (git mine, inter-rev electrical/mechanical deltas,
detect-HW schematic narrative, bench measurement evidence): see
`.planning/v1.7-SHIELD-REVS.md` in the Firestarter meta-repo (sections §2
through §5 and §8 — operator does not need these for normal use).

---

## 1. Inventory

Per-revision inventory of every RURP shield revision recoverable from upstream git history (main branch, tags, rev-named branches, and git-log --diff-filter=D deletions). Revisions whose schematic file is unrecoverable are excluded from this table.

| silkscreen | provenance | state | introduced_commit | removed_commit | schematic_path | gerber_path | photo_dir | notes |
|------------|------------|-------|-------------------|----------------|----------------|-------------|-----------|-------|
| not-recovered | on-main | upstream-only | c2bd111 (Rev 2.3, 2025-06-24) | — | `hardware/RelativelyUniversalROMProgrammer.kicad_sch` (blob fe35bd78) | `hardware/Rev2.3/jlcpcb/production_files/GERBER-RelativelyUniversalROMProgrammer.zip` | — | upstream-c2bd111; R41=10k; JP4 footprint 1x2→2x2 vs Rev2.2; schematic renamed from W27C512Programmer |
| not-recovered | on-main | upstream-only | c2bd111 (Rev 2.3, 2025-06-24) | — | `hardware/W27C512Programmer.kicad_sch` (blob f3b7a521, same as Rev2.1) | `hardware/Rev2.2/Rev2.2-gerbers.zip` (gerber date 2025-04-28) | — | upstream-c2bd111; no standalone Rev2.2 schematic — blob identical to Rev2.1; Phase 35 bench A3↔GND measurement 20 kΩ but NOT R41 in isolation; schematic 4k7 not contradicted (see meta-repo §8 for analysis) |
| not-recovered | on-main | upstream-only | 50a6ea4 (Rev2.1, 2024-12-20) | — | `hardware/W27C512Programmer.kicad_sch` (blob f3b7a521, on origin/Rev2.1) | `hardware/Rev2.1/RURP-Rev2.1.zip` | — | upstream-50a6ea4; R41=4k7; JP4=P1_VPP_JMP (1x2 header) |
| not-recovered | on-main | upstream-only | 28e0239 (Rev2, 2024-10-17) | — | `hardware/rev2/rev2-1316.zip` (gerbers only) | `hardware/rev2/rev2-1316.zip` | — | upstream-28e0239; pre-Rev2.1 "rev2" lowercase deprecated dump |
| not-recovered | on-main | upstream-only | a252e39 (Rev2, 2024-10-08) | — | `hardware/W27C512Programmer.kicad_sch` (blob d2a7f691, on origin/rev2.0) | `hardware/rev2/rev2-1316.zip` (Rev2 era gerbers) | — | upstream-a252e39; Rev2.0 working schematic on origin/rev2.0 branch; R41=4k7 first appears here; ADC pin A3; JP4=P1_VPP_JMP |
| not-recovered | removed-from-main | upstream-only | b84e9e0 (Rev1 PCB, 2024-04-30) | c2bd111 (2025-06-24) | `hardware/UniversalProgrammerRev1b0.zip` (gerbers only — no .kicad_sch in zip) | `hardware/UniversalProgrammerRev1b0.zip` | — | upstream-b84e9e0; voltage divider on A2 (not A3) per commit message; R41 designator NOT present in Rev1 era |
| not-recovered | removed-from-main | upstream-only | 486f3d1 (Hardware release day, 2024-04-18) | c2bd111 (2025-06-24) | `hardware/W27C512Programmer.kicad_sch` (blob d2a7f691 on origin/rev2.0, outside zip) / `hardware/UniversalProgrammerRev0b0.zip` (gerbers only) | `hardware/UniversalProgrammerRev0b0.zip` | — | upstream-486f3d1; gerbers only in zip; schematic accessible via git blob on rev2.0 branch; no R41 in pre-Rev2 schematic era |
| not-recovered | removed-from-main | upstream-only | n/a (operator board derived from Rev 0) | n/a (operator board — parent Rev0 removed at c2bd111) | cross-refs to Rev0 schematic blob d2a7f691 on origin/rev2.0 + UniversalProgrammerRev0b0.zip | n/a (operator modification — no upstream gerbers) | — | parent = Rev 0; operator's third board with hardware-bug-A/B rework (cuts + jumpers); photos + MODIFICATIONS.md rework trace deferred (post-v1.7) |

---

## 2. Per-Rev Capability Matrix

Per-rev capability matrix declaring which chip families, voltage ranges, address-bus width, and firmware algorithms (`protocol_id`s) each RURP shield revision physically supports. Cross-checked against firmware source-of-truth `firestarter/src/proms/memory.cpp::configure_memory` dispatch chain.

The canonical `KNOWN_PROTOCOLS` list is documented in `CLAUDE.md` §Protocol Dispatch: `0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39`.

| rev | chip_families_supported | max_vpp_v | max_vcc_v | address_bus_width_bits | supported_protocol_ids | runtime_guard_gaps | notes |
|---|---|---|---|---|---|---|---|
| Rev 0 | UV-EPROM 28-pin DIP, UV-EPROM 32-pin DIP, 24-pin legacy DIP UV-EPROM, 28-pin AT28C EEPROM, AMD-style flash, Intel 28F flash, SRAM/NVRAM | 13 | 5 | 20 | 0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39 | NO_DETECT (R41 designator not yet introduced; falls through to `rev_unknown`) | First public RURP. All KNOWN_PROTOCOLS handlers are firmware-side capability. |
| Rev 1 | UV-EPROM 28-pin DIP, UV-EPROM 32-pin DIP, 24-pin legacy DIP UV-EPROM, 28-pin AT28C EEPROM, AMD-style flash, Intel 28F flash, SRAM/NVRAM | 13 | 5 | 20 | 0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39 | NO_DETECT_VIA_R41 (A2 divider for unrelated purpose; A3 reads floating) | Capability inherited from Rev 0. A2 divider unrelated to R41-on-A3 detect. |
| rev2 (lowercase) | UV-EPROM 28-pin DIP, UV-EPROM 32-pin DIP, 24-pin legacy DIP UV-EPROM, 28-pin AT28C EEPROM, AMD-style flash, Intel 28F flash, SRAM/NVRAM | 13 | 5 | 20 | 0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39 | (none) | "rev2 lowercase" is a deprecated gerber dump electrically equivalent to Rev 2.0 working schematic. |
| Rev 2.0 working | UV-EPROM 28-pin DIP, UV-EPROM 32-pin DIP, 24-pin legacy DIP UV-EPROM, 28-pin AT28C EEPROM, AMD-style flash, Intel 28F flash, SRAM/NVRAM | 13 | 5 | 20 | 0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39 | (none) | First rev with R41=4k7 at A3 in the schematic. |
| Rev 2.1 | UV-EPROM 28-pin DIP, UV-EPROM 32-pin DIP, 24-pin legacy DIP UV-EPROM, 28-pin AT28C EEPROM, AMD-style flash, Intel 28F flash, SRAM/NVRAM | 13 | 5 | 20 | 0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39 | (none) | First formally-released Rev 2.X. R41=4k7. JP4=P1_VPP_JMP (1x2 vertical header). |
| Rev 2.2 | UV-EPROM 28-pin DIP, UV-EPROM 32-pin DIP, 24-pin legacy DIP UV-EPROM, 28-pin AT28C EEPROM, AMD-style flash, Intel 28F flash, SRAM/NVRAM | 13 | 5 | 20 | 0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39 | (none — R41 value uncertainty does NOT affect programming capability; R41 is detect-divider only) | Capability unchanged from Rev 2.1. R41 value per schematic 4k7; bench A3↔GND header reading 20 kΩ inconclusive (includes MCU leakage). |
| Rev 2.3 | UV-EPROM 28-pin DIP, UV-EPROM 32-pin DIP, 24-pin legacy DIP UV-EPROM, 28-pin AT28C EEPROM, AMD-style flash, Intel 28F flash, SRAM/NVRAM | 13 | 5 | 20 | 0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39 | (none) | Current upstream main rev. R41=10k. JP4 footprint = PinHeader_2x02. Capability set unchanged from Rev 2.1/2.2. |
| Modified Rev 0 | as-modified — pending v1.8 | as-modified — pending v1.8 | as-modified — pending v1.8 | 20 (parent Rev 0 baseline) | as-modified — pending v1.8 | UNKNOWN_REWORK; operator-attested via EEPROM byte. Bench detection: ADC mid-band → REVISION_2_3 (operator's mod wired a 10k pull-up on A3). | Items marked `pending v1.8` (Modified Rev 0 row) are deferred to v1.8 — see meta-repo `.planning/todos/pending/` queue. |

---

## 3. Silkscreen → Code Alias Table

Canonical map from every RURP-shield silkscreen / schematic-net label that crosses into firmware into the post-Phase-33 code-side alias namespace.

The canonical-alias namespace is split four ways: **`CTRL_*`** for control-register bit positions written to the 74HC573 latch (`rurp_pinout.h:24-44` legacy / wide-layout pair + `:58-72` REV_1/REV_2 suffix family); **`PIN_*`** for Arduino-pin assignments that map to RURP signals (`PIN_VPP_VOLTAGE_ADC = A2`, `PIN_HW_REVISION_DETECT_ADC = A3`); **`RES_*`** for shield-level resistor designators referenced by firmware logic (today only the detect divider, `RES_HW_REVISION_DIVIDER` = R41); **`JMP_*`** for shield-level jumper designators (today only the VPP-bypass jumper, `JMP_VPP_P1_BYPASS` = JP4). Every row's `canonical_alias` column matches `^(CTRL|PIN|RES|JMP)_[A-Z0-9_]+$`.

Label types: **`S`** = physically silkscreen-printed on the PCB; **`N`** = schematic-net-only (visible only inside `.kicad_sch` source).

| silkscreen_label | label_type | canonical_alias | hex_value (legacy / rev2) | rev_0 | rev_1 | rev_2_0 | rev_2_1 | rev_2_2 | rev_2_3 | mod_rev_0 |
|------------------|-----------|------------------|----------------------------|-------|-------|---------|---------|---------|---------|-----------|
| REGULATOR | N | CTRL_VPP_REGULATOR_ENABLE | 0x80 / 0x80 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| VPE_TO_VPP | N | CTRL_VPP_VPE_DROP_ENABLE | 0x01 / 0x100 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| READ_WRITE | N | CTRL_READ_WRITE | 0x40 / 0x40 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| ADDRESS_LINE_18 | N | CTRL_ADDRESS_LINE_18 | 0x20 / 0x20 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| ADDRESS_LINE_17 | N | CTRL_ADDRESS_LINE_17 | 0x10 / 0x10 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| P1_VPP_ENABLE | N | CTRL_VPP_P1_ENABLE | 0x08 / 0x08 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| VPE_ENABLE | N | CTRL_VPE_ENABLE | 0x04 / 0x04 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| A9_VPP_ENABLE | N | CTRL_VPP_A9_ENABLE | 0x02 / 0x02 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| ADDRESS_LINE_16 | N | CTRL_ADDRESS_LINE_16 | 0x01 / 0x01 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| ADDRESS_LINE_13 | N | CTRL_ADDRESS_LINE_13 | 0x20 / 0x20 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| REV_1_VPE_TO_VPP | N | CTRL_VPP_VPE_DROP_ENABLE_REV1 | 0x01 | ✓ | ✓ | not-present | not-present | not-present | not-present | (inherits Rev 0) |
| REV_2_VPE_TO_VPP | N | CTRL_VPP_VPE_DROP_ENABLE_REV2 | 0x01 | not-present | not-present | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| REV_2_ADDRESS_LINE_18 | N | CTRL_ADDRESS_LINE_18_REV2 | 0x08 | not-present | not-present | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| A2 (Arduino-pin) | N | PIN_VPP_VOLTAGE_ADC | A2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| A3 (Arduino-pin) | N | PIN_HW_REVISION_DETECT_ADC | A3 | not-present | not-present | ✓ | ✓ | ✓ | ✓ | (inherits Rev 0) |
| R41 | S | RES_HW_REVISION_DIVIDER | n/a | not-present | not-present | ✓ (4k7) | ✓ (4k7) | ✓ (4k7 schematic; v1.8 backlog for in-isolation ground truth) | ✓ (10k) | as-modified — pending v1.8 |
| JP4 | S | JMP_VPP_P1_BYPASS | n/a | not-present | not-present | ✓ (1x2) | ✓ (1x2) | ✓ (1x2) | ✓ (2x2) | as-modified — pending v1.8 |

---

## 4. Per-Rev Expected ADC Band Table

Per-rev expected ADC value range + reported firmware enum + reported silkscreen string. The bands were originally derived from voltage-divider math assuming the MCU's internal pull-up acted as R_top. **Phase 35 Plan 01 fix switched `pinMode(PIN_HW_REVISION_DETECT_ADC)` from `INPUT_PULLUP` to `INPUT` (high-Z), disabling the internal pull-up — fundamentally changing the band-math semantics.** Bands are now interpreted as characterizing *A3-net composition*, not R41 value alone.

The firmware threshold constants `ADC_BAND_R41_4K7_HIGH = 200`, `ADC_BAND_R41_10K_LOW = 220`, `ADC_BAND_R41_10K_HIGH = 600` (declared in `firestarter/include/rurp_pinout.h:58-62`) work empirically without modification — Phase 35 Wave 3 bench (2026-05-26): 0/15 reads landed in the `[200, 220)` guard gap across 3 shield revisions.

| Rev | A3-net composition (post-Plan 01) | Expected ADC band (10-bit, 8-sample avg) | Reported enum | Reported silkscreen string |
|-----|-----------------------------------|------------------------------------------|--------------|----------------------------|
| Rev 0 | no R41; A3 floats | 850–1023 (high band; A2 disambig → high → Rev 0) | `REVISION_0` (= 0) | `"Rev 0"` |
| Rev 1 | no R41; A3 floats | 850–1023 (high band; A2 disambig → low → Rev 1) | `REVISION_1` (= 1) | `"Rev 1"` |
| Rev 2.0 / 2.1 / 2.2 (R41 to GND via JP4) | R41 only to GND; A3 pulled low via MCU leakage | 0–199 (low band; empirical Phase 35 Wave 3 — both operator boards land here regardless of R41 value because no R_top is active under INPUT high-Z) | `REVISION_2_0` (= 2) | `"Rev 2.0-class"` |
| Rev 2.3 (R41 = 10k) | per schematic: R41 to GND via JP4 — same low band as Rev 2.0/2.1/2.2 in INPUT high-Z mode | 0–199 (same low band — R41 value alone does not differentiate) | `REVISION_2_0` (broad-bucket) OR `REVISION_2_3` if operator EEPROM-overrides | `"Rev 2.0-class"` OR `"Rev 2.3"` via override |
| Modified Rev 0 (operator-attested rework: 10k pull-up on A3) | external pull-up to +5V via 10k | 220–600 (mid band — Phase 35 bench empirical) | `REVISION_2_3` (= 5) [operator-acceptable per rework intent] | `"Rev 2.3"` (via EEPROM override = 5) |
| (any reading in [200, 220) guard gap OR in [600, 849] dead zone) | inconclusive | (gap reading) | `REVISION_UNKNOWN` (= 0xFE) | `"rev_unknown"` |

**Threshold-constant cross-link (mirror of `rurp_pinout.h:58-62`):**

- `ADC_BAND_R41_4K7_HIGH = 200` — upper edge of "R41-only-to-GND" low band.
- `ADC_BAND_R41_10K_LOW  = 220` — lower edge of "A3-pulled-up" mid band. `[200, 220)` → `REVISION_UNKNOWN` guard gap.
- `ADC_BAND_R41_10K_HIGH = 600` — upper edge of mid band; above signals "A3 floating, no R41".

Items marked `pending v1.8` are operator-deferred and tracked in the meta-repo `.planning/todos/pending/` queue.

---

## Full Investigation History

The complete RURP shield investigation — upstream git archaeology, inter-rev electrical/mechanical deltas, detect-hardware schematic delta narrative, bench measurement evidence — lives in the Firestarter meta-repo at:
`.planning/v1.7-SHIELD-REVS.md`

Sections covered there but not duplicated here:
- §2 Mentioned-but-not-recovered (Anders chat-intel cited revs without surviving schematics)
- §3 Anders R41-on-A3 detect-divider history (per-rev R41 introduction timeline)
- §4 Inter-Rev Electrical Differences (delta table)
- §5 Inter-Rev Mechanical Differences (footprint + jumper-position changes)
- §8 Detect-HW Schematic Delta (next-rev shield narrative + topology + Phase 35 ASCII correction)

Meta-repo is private; the path above is the local-clone reference for operators with meta-repo access.
