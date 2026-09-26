# Phase 34: Shield-Version-Detect Design + Firmware Plumbing - Context

**Gathered:** 2026-05-25
**Status:** Ready for planning
**Mode:** Auto — decisions made from prior-phase substrate without per-question prompts; redirect via plan-phase edit if any call lands wrong.

<domain>
## Phase Boundary

Fill `.planning/v1.7-SHIELD-REVS.md` §8 (Detect-HW Schematic Delta) + §9 (Per-Rev Expected ADC Band Table) — both currently `<!-- OWNED BY PHASE 34 — TBD -->` — and plumb the firmware-side ADC-band detection. The schematic delta is **not a new operator-fabricated board**; it documents the existing Anders R41-on-A3 divider scheme already shipped in upstream Rev 2.0 / 2.1 / 2.2 / 2.3 (per §3 of v1.7-SHIELD-REVS.md). Firmware extends the existing `rurp_detect_hardware_revision()` (`firestarter/include/rurp_hw_rev_utils.h:42-59`) from its current digital-A3 + analog-A2 dual-pin scheme to an analog-A3 band-lookup substrate that can distinguish Rev 2.0-class (R41=4k7) from Rev 2.3 (R41=10k) from pre-detect-resistor revs (Rev 0 / 1 — no R41 → floating A3 with internal pull-up → high-band → `rev_unknown` fall-through), while preserving the existing A2 Rev 0 vs Rev 1 disambiguation. Extend the `REVISION_*` enum at `firestarter/include/rurp_shield.h:25-29` with `REVISION_2_3 = 5` and `REVISION_UNKNOWN = 0xFE` (`0xFF` already reserved as "no EEPROM override" sentinel per `rurp_hw_rev_utils.h:63` and `hardware_operations.cpp:101`). Reuse the existing `MSG_OK_REV` 2-byte wire shape (`physical_u8, effective_u8`) — new enum values flow through unchanged; no codegen pass on `tools/catalog/messages.toml` needed. Add Python-side `REVISION_2_3` + `REVISION_UNKNOWN` constants to `firestarter_app/firestarter/constants.py` (parity with the firmware enum extension, per the sync rule in `firestarter_app/CLAUDE.md`). GATE-1.7 non-regression: programming + read paths byte-identical on all 3 AVR envs (`uno` / `leonardo` / `uno328pb`); pre-detect-resistor handshake byte-identical modulo the `MSG_OK_REV` physical-u8 value (additive in the sense that new code paths can populate it, but the wire frame ID and byte count are unchanged).

Desk-side waves only for Phase 34 close. Operator-on-bench validation of `rev_unknown` fall-through on an existing pre-detect-resistor board (Rev 0 / Rev 2.0 / Rev 2.2) is recommended but deferred to Phase 35 (the milestone-close human-UAT pass that also gates the sub-repo `beta` → `main` promotion per the v1.7 branch model). Sub-repo `v1.7-shield-investigation` → `beta` promotion happens at Phase 34 close per the v1.7 roadmap §Branch model.

</domain>

<decisions>
## Implementation Decisions

### Detect-HW Schematic Delta (D-01..D-03)

- **D-01: §8 documents the existing Anders R41-on-A3 scheme — no new operator-fabricated board.** Phase 34 fills `.planning/v1.7-SHIELD-REVS.md` §8 with the already-upstream divider topology (JP4 / P1_VPP_JMP → R41 → A3 → GND), citing the per-rev R41 value from §3 (Rev 2.0 / 2.1 / 2.2 = 4k7 per schematic; Rev 2.2 chat-vs-sch 10k discrepancy still pending Phase 35 follow-up #5 physical measurement; Rev 2.3 = 10k). The spec's "next-rev shield" phrasing is satisfied by treating Rev 2.3 as the seed entry per `REQUIREMENTS.md` DETECT-HW-02 ("Initial table seeds the next-rev (Rev 2.3) entry"). No new PCB design, no new resistor proposal, no fabrication. Rationale: operator does not currently own a Rev 2.3 board (per memory [[user_shield_revisions]] — owns Rev 2.2, Rev 2.0, Modified Rev 0); designing a Rev 2.4 with a fresh detect divider would require fabrication + bench cycle outside v1.7 scope. Rev 2.3 already has a divider — Phase 34 just plumbs firmware to read it.
- **D-02: ADC pin = A3 (PIN_HW_REVISION_DETECT_ADC) — already aliased in Phase 33.** No new pin assignment. The pin is already declared in `firestarter/include/rurp_pinout.h:46` as `PIN_HW_REVISION_DETECT_ADC A3` (HARDWARE_REVISION-gated). §7 row 15 confirms applicability across Rev 2.0+. R41 is already aliased as `RES_HW_REVISION_DIVIDER` (§7 row 16, declared in Phase 33 substrate). JP4 is aliased as `JMP_VPP_P1_BYPASS` (§7 row 17). No new aliases needed.
- **D-03: Voltage-band separation derived from upstream R41 values + ATmega internal pull-up.** Internal pull-up on A3 (ATmega328P: 20–50 kΩ typical; ATmega32U4 / 328PB: similar wide spec). With R41 to GND, A3 reads V_A3 = VCC × R41 / (R_pullup + R41). Computed bands (5V VCC, 30 kΩ typical pull-up):
  - **Rev 2.0/2.1/2.2 (R41 = 4k7):** V_A3 ≈ 0.677 V → ADC ≈ 138 (10-bit)
  - **Rev 2.3 (R41 = 10k):** V_A3 ≈ 1.25 V → ADC ≈ 256
  - **Pre-detect-resistor (Rev 0 / Rev 1 — no R41):** A3 floats with internal pull-up → V_A3 ≈ VCC → ADC ≈ 1023
  - Separation between the 4k7 and 10k bands ≈ 0.57 V (well above the ≥ ~0.3 V noise-floor spec in DETECT-HW-01). Pull-up tolerance widens the bands but does not collapse the separation (worst-case 20 kΩ pull-up: 4k7 → ≈ 950 mV, 10k → ≈ 1.67 V; 50 kΩ pull-up: 4k7 → ≈ 430 mV, 10k → ≈ 833 mV — bands still separated by > 0.4 V across the full tolerance range). Planner verifies the threshold math in the §9 band-table fill commit + adds a fix-commit note if any per-board MCU pull-up tolerance falls outside the 20–50 kΩ assumption.

### Per-Rev Granularity (D-04..D-05)

- **D-04: ADC distinguishes physically-separable bands only — Rev 2.0 / 2.1 / 2.2 collapse into one bucket.** §6 of v1.7-SHIELD-REVS.md confirms Rev 2.0, 2.1, 2.2 are electrically identical (no schematic delta — R41 = 4k7 across all three; Rev 2.2 R41-value-chat-vs-sch discrepancy is the open Phase 35 follow-up #5). They CANNOT be distinguished by ADC band alone. `rurp_detect_hardware_revision()` will report the broad bucket: ADC band → `REVISION_2_0` (the canonical "Rev 2.0-class with R41=4k7" enum value already declared at `rurp_shield.h:27`). Operator-specific Rev 2.1 / Rev 2.2 distinction (if needed) flows through the EEPROM `hw_revision` override path — `rurp_get_hardware_revision()` at `rurp_hw_rev_utils.h:61-67` already implements override precedence (EEPROM byte beats physical detection when `rurp_config->hardware_revision < 0xFF`). This honors REQUIREMENTS.md DETECT-FW-01 verbatim: "firmware ... reports the detected silkscreen-rev string in the handshake payload ... falls through to honoring the operator-configured `hw_revision` byte in EEPROM (existing behavior preserved)."
- **D-05: Detected ADC enum values mapped to silkscreen strings host-side, NOT firmware-side.** Firmware writes a u8 enum value via `MSG_OK_REV` (existing wire shape `LOG_OK_ID_U8_U8(MSG_OK_REV, physical, effective)` at `hardware_operations.cpp:102`). Host catalog (`firestarter_app/firestarter/messages.py:126`) currently formats this as `"Rev%u (eff: %u)"`. Phase 34 keeps the wire shape (no codegen pass on `tools/catalog/messages.toml`); host-side cosmetic improvement to map enum byte → silkscreen string ("Rev 2.0-class", "Rev 2.3", "Rev 0", "Rev 1", "rev_unknown") happens in `firestarter_app/firestarter/serial_comm.py:325-340` (P-02 `MSG_OK_REV` formatting path — `_format_message` or sibling). Planner finalizes whether the string mapping lives in `serial_comm.py` or in a new `firestarter_app/firestarter/hardware_revisions.py` lookup module.

### Firmware Detection Logic Rework (D-06..D-08)

- **D-06: Switch A3 from `digitalRead` to `analogRead`; preserve A2 ADC disambiguation for Rev 0 vs Rev 1.** Current code at `rurp_hw_rev_utils.h:42-59` does `digitalRead(A3)` + `analogRead(A2)` (Rev 1 has divider on A2 → low value; Rev 0 has no A2 divider → high value). Phase 34 changes A3 to `analogRead(PIN_HW_REVISION_DETECT_ADC)`, branches on the band:
  ```
  adc_a3 = analogRead(PIN_HW_REVISION_DETECT_ADC);
  if (adc_a3 < ADC_BAND_R41_4K7_HIGH) {
      // Rev 2.0/2.1/2.2 with R41=4k7 — reports as REVISION_2_0 (broad bucket per D-04)
      revision = REVISION_2_0;
  } else if (adc_a3 < ADC_BAND_R41_10K_HIGH) {
      // Rev 2.3 with R41=10k
      revision = REVISION_2_3;
  } else {
      // No R41 → high band (pull-up dominant). Disambiguate Rev 0 vs Rev 1 via A2.
      adc_a2 = analogRead(PIN_VPP_VOLTAGE_ADC);
      revision = (adc_a2 < 1000) ? REVISION_1 : REVISION_0;
  }
  ```
  Threshold constants (`ADC_BAND_R41_4K7_HIGH`, `ADC_BAND_R41_10K_HIGH`) land in `rurp_pinout.h` (or sibling `rurp_hw_rev_bands.h` — planner picks) with values derived from D-03 plus generous tolerance margins. Existing A2 magic-number `< 1000` retained for Rev 0 vs Rev 1 (already shipped, already correct).
- **D-07: Add `REVISION_2_3 = 5` and `REVISION_UNKNOWN = 0xFE` enum values; `0xFF` stays reserved for "no override" sentinel.** Insert at `firestarter/include/rurp_shield.h:30` (immediately after `REVISION_2_2 = 4`). `REVISION_UNKNOWN` is the explicit fall-through for ADC reads that don't match any band (defensive — current `default` branch at `rurp_hw_rev_utils.h:54-57` sets `revision = 0xFF` which collides semantically with the EEPROM-override-absent sentinel). Phase 34 changes the default-branch sentinel to `REVISION_UNKNOWN` (`0xFE`); `0xFF` remains EEPROM-byte-only. `rurp_map_ctrl_reg_for_hardware_revision()` at `rurp_hw_rev_utils.h:14-36` adds a `case REVISION_2_3:` branch that aliases to the `REVISION_2_0` / `REVISION_2_1` / `REVISION_2_2` arm (identical control-register bit layout per §4 row 6 — Rev 2.3 only changed R41 value + JP4 footprint, not control-line routing). `REVISION_UNKNOWN` falls through to the existing `default: break;` arm (ctrl_reg = 0 — fail-safe, matches existing behavior).
- **D-08: Python-side parity — add `REVISION_2_3 = 5` + `REVISION_UNKNOWN = 0xFE` to `firestarter_app/firestarter/constants.py`.** Sits in a new `# RURP Hardware Revisions` block (alongside the existing `# RURP Control Register Bits` block from Phase 33). Mirrors the firmware enum verbatim. `serial_comm.py` MSG_OK_REV format path (line 336) consumes these symbolically when mapping the wire u8 to a silkscreen string per D-05. `firestarter_app/CLAUDE.md` sync rule already covers cross-repo constant parity — extend the "Constants" subsection prose to mention the new REVISION_* block.

### Handshake Wire Format (D-09)

- **D-09: No new message ID — reuse `MSG_OK_REV` 2-byte wire shape verbatim.** `tools/catalog/messages.toml` stays untouched; no codegen pass. The "additive `rev_unknown` report" phrasing in DETECT-FW-02 is interpreted as **the existing `MSG_OK_REV` physical-u8 byte can now take a new enum value (`REVISION_2_3 = 5` or `REVISION_UNKNOWN = 0xFE`) in addition to the existing values 0–4** — message ID unchanged, byte count unchanged, frame structure unchanged. Pre-detect-resistor boards (Rev 0 / Rev 1) that previously reported `physical = 0` or `1` continue to report `0` or `1` (no behavior change). Boards on which the new ADC logic detects `REVISION_UNKNOWN` (`0xFE`) report that value instead of an undefined / 0xFF read — this is the only host-observable wire-payload-VALUE change, and it preserves the wire-FRAME shape. The `MSG_INFO_HW` (0x5B) + `MSG_INFO_PHYSICAL_HW` (0x5C) handshake emits at `firestarter.cpp:133-134` similarly pass the new enum values through unchanged.

### GATE-1.7 Non-Regression Verification (D-10)

- **D-10: `.hex` byte-diff per AVR env + native test green is the planner's gate; operator-on-bench validation deferred to Phase 35.** Per Phase 33's verified pattern (the migration shipped Δ = 0 B across uno / uno328pb / leonardo per STATE.md last-activity line), Phase 34's verification mechanism is:
  1. Pre-Phase-34 `.hex` baseline captured at branch tip (one-time, gitignored under `.planning/v1.7/baseline-34/`) — `wc -c firestarter/.pio/build/<env>/firmware.hex` per env.
  2. Post-Phase-34 `.hex` size compared to baseline; expected Δ ≈ 50–200 B (new `analogRead` call site, new threshold constants, new switch arm, new enum value branch). Planner records actual deltas in the fix-commit message.
  3. `pio test -e native -f "*test_dispatch*"` stays green (configure_memory dispatch unaffected by the rev-detect path).
  4. `pytest -q` in firestarter_app stays green (Python parity is additive constants only).
  5. **Operator-on-bench validation explicitly deferred to Phase 35:** the milestone-close human-UAT pass sideloads Phase 34 firmware to operator's Rev 2.0 or Rev 2.2 board (chip OUT per memory [[feedback_chip_out_before_sideload]]; verify port identity per memory [[feedback_verify_port_identity_each_task]]) and confirms `MSG_OK_REV` reports either `REVISION_2_0` (if operator's board has R41 populated) or `REVISION_UNKNOWN` (if not) — either way is acceptable per the backward-compat fall-through clause. The sub-repo `v1.7-shield-investigation` → `beta` promotion happens at Phase 34 close (desk-side); `beta` → `main` is gated on operator-on-bench at Phase 35 per the v1.7 branch model.

### §9 ADC Band Table Schema (D-11)

- **D-11: §9 table is per-rev expected ADC value range + map to enum value.** Schema lock for the §9 fill:
  ```
  | rev | r41_value | expected_adc_band (10-bit) | reported_enum | reported_silkscreen_string | source_evidence |
  | Rev 0           | not-present | 850–1023 (high band, A3 floating; A2 disambig: high → Rev 0) | REVISION_0   | "Rev 0"           | §6 + rurp_hw_rev_utils.h:49 |
  | Rev 1           | not-present | 850–1023 (high band; A2 disambig: low → Rev 1)              | REVISION_1   | "Rev 1"           | §6 + rurp_hw_rev_utils.h:49 |
  | Rev 2.0 / 2.1 / 2.2 (R41 = 4k7) | 4k7  | 80–220 (4k7 band, see D-03 math) | REVISION_2_0 | "Rev 2.0-class" | §3 + §6 + D-03 + D-04 |
  | Rev 2.3         | 10k         | 200–320 (10k band, see D-03 math)                         | REVISION_2_3 | "Rev 2.3"         | §3 + §6 + D-03         |
  | Modified Rev 0  | as-modified | as-modified — pending Phase 35                            | (operator-attested via EEPROM byte) | (as configured) | memory [[user_shield_revisions]] + Phase 35 follow-up #4 |
  | (any reading outside the above bands) | — | (gap reading)                                | REVISION_UNKNOWN | "rev_unknown"  | D-07                  |
  ```
  Band gaps (220–200 overlap risk between R41=4k7 and R41=10k) — planner verifies threshold constants enforce strict ordering (`ADC_BAND_R41_4K7_HIGH < ADC_BAND_R41_10K_LOW < ADC_BAND_R41_10K_HIGH`) with explicit numeric values chosen to land mid-gap. Planner can replace exact band-edge numbers with tolerance-derived values per D-03 worst-case math; the schema above is illustrative.

### Claude's Discretion

- **Plan-wave decomposition:** likely 3 waves — Wave 1: §8 (Detect-HW schematic delta documentation) + §9 (band table) fill on meta-repo; Wave 2: firmware enum + detection-logic rework + threshold constants on `firestarter` sub-repo; Wave 3: Python-side constants parity + serial_comm.py string-mapping cosmetics on `firestarter_app` sub-repo. Planner picks final wave count.
- **Threshold constant location** — `rurp_pinout.h` (sits with the PIN_ / RES_ aliases) vs new `rurp_hw_rev_bands.h` (sibling header). Planner picks; the `RES_HW_REVISION_DIVIDER` already lives in `rurp_pinout.h` so co-locating bands there has precedent. (Wave 2 owner.)
- **Whether to wrap the new `analogRead(A3)` in a calibration window** (e.g., 8-sample averaging to reduce noise) — internal pull-up + low-Z divider should be stable, but the planner may add averaging if the threshold tolerance math from D-03 leaves insufficient margin against ADC noise.
- **Whether to add a host-side `firestarter dev detect-rev` subcommand** that prints the detected rev string + raw ADC value (operator diagnostic for the open Phase 35 follow-up #5 — R41 = 4k7 vs 10k measurement). Could be cheap to add; planner decides.
- **Native test coverage for the new detection logic** — `rurp_hw_rev_utils.h` is currently NOT under the `[env:native]` `src_filter = +<proms/>` glob; Unity host tests don't exercise it. Planner can either (a) extend `src_filter` to include the new band-lookup logic (with ArduinoFake mocks for `analogRead`), or (b) leave it as an AVR-only path and rely on the §11 firmware-flash-bytes-identical regression check + Phase 35 operator-on-bench validation. Option (b) is the lowest-friction default given Phase 33's precedent.
- **Whether to bump `CONFIG_VERSION` in `rurp_shield.h:93`** — no, the EEPROM-persisted `rurp_configuration_t` struct does NOT change (we add an enum value, not a struct field). Planner verifies.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project planning
- `.planning/ROADMAP.md` §v1.7 / Phase 34 — milestone goal, Phase 34 success criteria, DETECT-HW-01..02 + DETECT-FW-01..02 acceptance
- `.planning/REQUIREMENTS.md` — DETECT-HW-01 (resistor divider + voltage bands), DETECT-HW-02 (per-rev band table), DETECT-FW-01 (firmware ADC read + handshake report + EEPROM fall-through), DETECT-FW-02 (GATE-1.7 non-regression)
- `.planning/STATE.md` — current milestone state (Phase 33 closed; Phase 34 next)
- `.planning/PROJECT.md` — project overview
- `.planning/codebase/STRUCTURE.md` — repo layout (meta-repo + 2 sub-repos)
- `.planning/codebase/CONVENTIONS.md` — coding conventions
- `.planning/codebase/CONCERNS.md` — known concerns / patterns

### v1.7 canonical document — Phase 34 fills §8 + §9
- `.planning/v1.7-SHIELD-REVS.md` §1 — per-rev inventory (rev existence + state)
- `.planning/v1.7-SHIELD-REVS.md` §3 — existing R41-on-A3 detect-HW scheme (Phase 34 §8 fill extends this; R41 values per rev, JP4 topology, schematic citations all already documented here)
- `.planning/v1.7-SHIELD-REVS.md` §4 — inter-rev electrical deltas (Phase 34 reads to confirm Rev 2.3 R41=10k delta and Rev 2.0–2.2 electrical identity)
- `.planning/v1.7-SHIELD-REVS.md` §6 — per-rev capability matrix (Phase 34 confirms ADC detect substrate availability per rev)
- `.planning/v1.7-SHIELD-REVS.md` §7 — silkscreen → code alias table (Phase 34 consumes `PIN_HW_REVISION_DETECT_ADC` row 15, `RES_HW_REVISION_DIVIDER` row 16, `JMP_VPP_P1_BYPASS` row 17)
- `.planning/v1.7-SHIELD-REVS.md` §8 — `<!-- OWNED BY PHASE 34 — TBD -->` — Phase 34 fills (Detect-HW schematic delta documentation)
- `.planning/v1.7-SHIELD-REVS.md` §9 — `<!-- OWNED BY PHASE 34 — TBD -->` — Phase 34 fills (per-rev expected ADC band table per D-11 schema)

### Prior phase context (load-bearing for D-01..D-11)
- `.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md` — schema for §1/§3 source-citation patterns; mine-notes.md grep references for R41 per-rev evidence
- `.planning/phases/32-inter-rev-difference-capability-matrix/` — §4 / §6 fill (no per-phase CONTEXT.md was produced; SUMMARY artifacts present)
- `.planning/phases/33-silkscreen-label-code-alias-migration/33-CONTEXT.md` — D-06 hard-rename policy, D-07 `#define` byte-identical math, D-08 minimal Python parity pattern (Phase 34 D-08 follows the same shape), 4-namespace CTRL_/PIN_/RES_/JMP_ lock

### Firmware source-of-truth files (Phase 34 modifies these)
- `firestarter/include/rurp_shield.h:25-29` — `REVISION_0..REVISION_2_2` enum; Phase 34 adds `REVISION_2_3 = 5` + `REVISION_UNKNOWN = 0xFE`
- `firestarter/include/rurp_hw_rev_utils.h:42-59` — `rurp_detect_hardware_revision()` body; Phase 34 reworks per D-06 (analog A3 + band lookup)
- `firestarter/include/rurp_hw_rev_utils.h:14-36` — `rurp_map_ctrl_reg_for_hardware_revision()`; Phase 34 adds `case REVISION_2_3:` arm aliased to REV_2_x bit layout (per D-07)
- `firestarter/include/rurp_hw_rev_utils.h:61-67` — `rurp_get_hardware_revision()` EEPROM-override path; **unchanged** by Phase 34 (already implements override-precedence correctly)
- `firestarter/include/rurp_pinout.h:46` — `PIN_HW_REVISION_DETECT_ADC A3`; Phase 34 may add `ADC_BAND_*` threshold constants here (D-03 + Discretion)
- `firestarter/include/messages.h` — `MSG_OK_REV` / `MSG_INFO_HW` / `MSG_INFO_PHYSICAL_HW` IDs **unchanged** (D-09 reuses wire shape)
- `firestarter/src/firestarter.cpp:132-134` — boot handshake emits MSG_INFO_FW / MSG_INFO_PHYSICAL_HW / MSG_INFO_HW; **unchanged** code path, new enum values flow through
- `firestarter/src/hardware_operations.cpp:96-105` — `hw_get_version()` emits `MSG_OK_REV` with (physical, effective) u8 pair; **unchanged** code path, new enum values flow through
- `firestarter/platformio.ini` — `-D HARDWARE_REVISION` already set for all 3 AVR envs; no new build flags expected

### Host CLI source-of-truth files (Phase 34 modifies these)
- `firestarter_app/firestarter/constants.py` — add `# RURP Hardware Revisions` block with `REVISION_0..REVISION_2_3 + REVISION_UNKNOWN` per D-08
- `firestarter_app/firestarter/serial_comm.py:325-340` — P-02 `MSG_OK_REV` format path; Phase 34 may extend the enum → silkscreen-string mapping per D-05 (cosmetic, not wire-shape)
- `firestarter_app/firestarter/messages.py:126` — `MSG_OK_REV` MessageDef format string; **unchanged** by Phase 34 (auto-regenerated from `tools/catalog/messages.toml` which is not modified)
- `firestarter_app/firestarter/hardware.py:81-107` — `get_hardware_revision()` consumer of MSG_OK_REV; **unchanged** unless D-05 string mapping lands here
- `firestarter_app/CLAUDE.md` — Constants subsection mentions `RURP_CONTROL_REGISTER_BITS` parity; Phase 34 extends the prose to mention the new `RURP_HARDWARE_REVISIONS` parity (per D-08)

### Memory (auto-recalled, persistent)
- `[[user_shield_revisions]]` — operator owns Rev 2.2 / Rev 2.0 / Modified Rev 0; NO Rev 2.3 on hand; ALWAYS ASK which rev when "swap the shield" comes up
- `[[project_v17_shield_investigation]]` — v1.7 milestone state (Phases 31-35; documentation-first + detect-resistor design + ADC plumbing); resumes v1.6 after v1.7 close
- `[[feedback_branching]]` — milestone branches in all 3 repos; Phase 34 touches meta-repo + both sub-repos; `v1.7-shield-investigation` → `beta` promotion happens at Phase 34 close (sub-repos)
- `[[user_firestarter_repo_layout]]` — meta + 2 sub-repos; sub-repos branched off `beta`, meta off `main`
- `[[feedback_chip_out_before_sideload]]` — chip OUT of socket before any firmware sideload (applies to optional Phase 34 operator-on-bench wave + Phase 35 operator validation)
- `[[feedback_verify_port_identity_each_task]]` — `controller:` identity per port at every task start (Phase 35 multi-board validation will exercise this)

### Sub-repo CLAUDE.md (must respect)
- `firestarter/CLAUDE.md` — protocol dispatch invariants (Phase 34 detect-rev rework MUST NOT perturb `configure_memory` dispatch order; rurp_hw_rev_utils.h is OUT of the proms/ dispatch chain — confirmed by `[env:native] src_filter = +<proms/>` exclusion); CONTROL register bit names verbatim (CTRL_VPP_REGULATOR_ENABLE etc. — Phase 33 substrate)
- `firestarter_app/CLAUDE.md` — Python sync-with-firmware rule (Phase 34 extends to cover the new `RURP_HARDWARE_REVISIONS` block); `MSG_OK_REV` wire format invariant (Phase 34 honors per D-09)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`rurp_detect_hardware_revision()`** (`rurp_hw_rev_utils.h:42-59`) — already does the digital A3 + analog A2 dance for Rev 0/1/2.0 detection. Phase 34 extends the body (analog A3 + band switch) but keeps the signature + the A2-disambig branch for Rev 0 vs Rev 1. No new function. No call-site changes elsewhere in the codebase (only the function body grows).
- **`rurp_get_hardware_revision()`** (`rurp_hw_rev_utils.h:61-67`) — EEPROM-override precedence already correct. Phase 34 leaves this entirely alone. The DETECT-FW-01 fall-through clause ("falls through to honoring the operator-configured `hw_revision` byte in EEPROM (existing behavior preserved)") is satisfied by construction — this function is unchanged.
- **`rurp_map_ctrl_reg_for_hardware_revision()`** (`rurp_hw_rev_utils.h:14-36`) — already dispatches per-rev control-register bit layout via switch. Phase 34 adds one case arm (`REVISION_2_3` aliased to the REV_2_x layout); no signature change.
- **`MSG_OK_REV` 2-byte wire shape** (`hardware_operations.cpp:102` + `serial_comm.py:336`) — already a stable, documented frame. Phase 34 reuses verbatim; the new enum values flow through the existing `u8, u8` payload positions.
- **`firestarter_app/firestarter/messages.py` catalog** — auto-generated from `tools/catalog/messages.toml`. Phase 34 does NOT modify the toml or run codegen — keeps the host catalog stable. (If a future phase needs new MSG_OK_DETECTED_REV codes, that's a codegen-pass commit, deliberately out of v1.7 scope.)
- **Phase 33 `#define`-only alias pattern** — proved Δ = 0 B across all 3 AVR envs. Phase 34 follows the same `#define ADC_BAND_R41_4K7_HIGH 220` pattern for the new threshold constants — no symbol-table pollution, no `.hex` bloat beyond the new analogRead call site and switch logic.

### Established Patterns
- **`#ifdef HARDWARE_REVISION` compile-flag gating** — all detect-rev code paths sit under this ifdef (set in `platformio.ini:23` for all 3 AVR envs; native env intentionally excludes). Phase 34 stays inside the ifdef boundary. Native tests continue to bypass the detect-rev logic entirely.
- **EEPROM-override-byte sentinel = `0xFF`** (`hardware_operations.cpp:101` + `rurp_hw_rev_utils.h:63`) — load-bearing across the codebase. Phase 34 explicitly carves out `0xFE` for `REVISION_UNKNOWN` to avoid collision (per D-07).
- **`#define`-based threshold constants** — not `constexpr` (Phase 33 D-07 rationale: AVR-objcopy + .hex byte-identical math). Phase 34 follows the same convention for `ADC_BAND_*_HIGH` constants.
- **Phase 33 atomic D-06-style delete** — when the old `rurp_shield.h:25-89` block was deleted (Phase 33 Wave 3 Task 4), the delete + dependent edits landed in one atomic commit. Phase 34 has nothing analogous to delete (the existing `rurp_detect_hardware_revision()` body is rewritten in-place, not deleted+rewritten).

### Integration Points
- **Phase 34 → Phase 35 (close)**: §8 + §9 fills close the last `<!-- OWNED BY PHASE -->` markers in `v1.7-SHIELD-REVS.md`; Phase 35 then runs the milestone-close paperwork (README cross-links, MILESTONES.md entry, PROJECT.md "Validated" update, archive). Operator-on-bench validation of the new firmware on Rev 2.0 / Rev 2.2 also gates Phase 35 (sub-repo `beta` → `main` promotion per the v1.7 branch model).
- **Phase 34 → v1.6 resume**: Phase 34's `REVISION_2_3` + `REVISION_UNKNOWN` enum additions become available substrate for v1.6 Phase 27 RCA re-open. The instrumented A/B builds can cite the detected rev string in their RCA logs — useful for ruling out "operator forgot to set hw_revision byte" as a confound when reproducing the read-bug across boards. Not a hard dependency; just self-documenting clarity.
- **Phase 34 → future runtime-guard milestone**: Per §6 Runtime-Guard Follow-Up Todos, future capability-vs-rev guards will read `rurp_get_hardware_revision()` and refuse the requested protocol_id if the rev's capability matrix forbids it. Phase 34 makes `REVISION_2_3` a first-class detectable value (where previously only EEPROM-byte override could surface it) — the guard substrate now sees a richer set of revs at boot.

</code_context>

<specifics>
## Specific Ideas

- **The "schematic delta for next-rev shield" phrasing is satisfied by documenting Anders's already-upstream Rev 2.3 R41=10k change** (per D-01). The roadmap and REQUIREMENTS text doesn't demand a fresh PCB design; it demands the firmware know how to detect Rev 2.3 + future divider-equipped boards. Operator does not own Rev 2.3 — but the firmware needs to be ready for when they (or a future user) get one.
- **Internal pull-up tolerance is the dominant noise term** (D-03). The 20–50 kΩ ATmega328 internal pull-up range moves the band edges substantially. Threshold constants must enforce strict ordering and include guard bands; if real-world readings cluster near a band edge, the operator override via EEPROM `hw_revision` byte is the escape hatch (existing behavior — D-04).
- **`MSG_OK_REV` already reports (physical, effective) — Phase 34 just gives the physical byte more values it can take.** No new wire shape, no codegen, no host-side struct change. Cleanest possible implementation of DETECT-FW-01.
- **The current `default: revision = 0xFF;` at `rurp_hw_rev_utils.h:54-57` is a latent bug** — it conflicts with the EEPROM-override-absent sentinel (`0xFF` also means "no operator override"). Phase 34 carves `0xFE` = `REVISION_UNKNOWN` as the physical-detect-unknown sentinel; `0xFF` remains EEPROM-only (per D-07). This is an intentional minor cleanup; the planner should not feel the need to gate it.
- **Rev 2.2 R41 value discrepancy** (4k7 schematic vs 10k chat — open Phase 35 follow-up #5) does NOT block Phase 34. If operator's Rev 2.2 board has R41 = 10k physically, Phase 34's firmware will misclassify it as Rev 2.3. That's covered by the EEPROM-override path: operator sets `hw_revision = REVISION_2_2 (4)` in EEPROM, and `rurp_get_hardware_revision()` reports the override regardless of the ADC band. Phase 35 follow-up #5 measures actual R41 on operator's board and (if needed) updates §3 + §9 — not §8 schematic.
- **Modified Rev 0 stays operator-attested via EEPROM byte** — Phase 34 firmware reads A3 ADC; Modified Rev 0 may have R41 added or removed by the operator's rework, so ADC reading is unpredictable. Operator sets `hw_revision = REVISION_0 (0)` in EEPROM; that always wins. No firmware-side Modified Rev 0 handling needed.

</specifics>

<deferred>
## Deferred Ideas

### For Phase 35 (close)
- **Operator-on-bench validation** — sideload Phase 34 firmware to Rev 2.0 or Rev 2.2 board, confirm `MSG_OK_REV` reports either `REVISION_2_0` (R41 populated) or `REVISION_UNKNOWN` (R41 not populated). Chip OUT per memory [[feedback_chip_out_before_sideload]]. Verify port identity per memory [[feedback_verify_port_identity_each_task]]. Sub-repo `beta` → `main` promotion gated on this.
- **Rev 2.2 R41 physical measurement** (Phase 35 follow-up #5 already on the books) — if the Rev 2.2 board reports `REVISION_2_3` instead of `REVISION_2_0`, that's data toward resolving the 4k7-vs-10k Anders-chat-vs-schematic discrepancy.
- **§9 row update for Modified Rev 0** — once `MODIFICATIONS.md` lands (Phase 35 follow-up #4), if the rework adds an R41 on A3, §9 gets a row with the band the operator's board actually reads.
- **README cross-links** — `firestarter/README.md` + `firestarter_app/README.md` link to `v1.7-SHIELD-REVS.md` §3 / §8 / §9 ("how the programmer detects which RURP shield revision it's bolted to"). Phase 35 owns.

### For post-v1.7 milestones
- **Runtime capability guards** — per §6 Runtime-Guard Follow-Up Todos, firmware refuses a protocol_id if the detected rev's capability matrix forbids it. Phase 34's `REVISION_2_3` + `REVISION_UNKNOWN` substrate enables this; implementation is post-v1.7 per CAPS-02 deferral.
- **`firestarter dev detect-rev` host subcommand** — operator-facing diagnostic that prints detected rev + raw ADC + override-state. Phase 34 may land this opportunistically (Claude's Discretion); if not, it's a small post-v1.7 follow-up.
- **8-sample analogRead averaging** for noise robustness — Phase 34 may add it if D-03 tolerance math requires; otherwise post-v1.7.
- **Native-test coverage for `rurp_hw_rev_utils.h`** — extend `[env:native] src_filter` to include the new band-lookup logic with ArduinoFake mocks. Not blocking; post-v1.7 cleanup.
- **Codegen pass to add MSG_OK_DETECTED_REV** (separate from MSG_OK_REV) if host wants the detected band as a richer string than just a u8. Phase 34 explicitly avoids this per D-09; if needed later, drop a row into `tools/catalog/messages.toml` and regenerate.
- **Migrating PORTx masks in board cpp files** (Phase 33 deferred item — still out of scope here).

### Out of v1.7 entirely
- **Designing a Rev 2.4 detect divider with finer per-rev bands** (e.g., 4k7 → 6k8 → 10k → 15k progression so each individual rev gets its own band) — would let firmware distinguish Rev 2.1 from Rev 2.2 from Rev 2.3 by ADC alone. Out of v1.7; would need new PCB fabrication + operator validation.
- **External pull-up resistor on A3** (instead of internal) — schematic change requiring new rev. Operator override + EEPROM byte already handles edge cases. Out of v1.7.
- **Per-board MCU pull-up calibration stored in EEPROM** — would let firmware self-calibrate to its specific ATmega328 / ATmega32U4 pull-up resistance. Out of v1.7; complexity-vs-payoff is poor for a 3-band lookup.

### Reviewed Todos (not folded)
- `avrdude-mcu-detection-fallback.md` — v1.5 carryover, not Phase 34 scope (host install concern).
- `large-read-data-jitter-uno328pb.md` — v1.6 milestone scope; v1.6 resumes after v1.7 ships per memory [[project_v17_shield_investigation]].
- `w27c512-eeprom-misclassification.md` — separate HIGH-priority backlog; chip-database routing bug.

(None folded — Phase 34's domain is detect-rev plumbing; the open todos are orthogonal concerns.)

</deferred>

---

*Phase: 34-Shield-Version-Detect-Design-Firmware-Plumbing*
*Context gathered: 2026-05-25 (auto mode — decisions auto-resolved from prior-phase substrate; planner may edit before `/gsd-plan-phase 34`)*
