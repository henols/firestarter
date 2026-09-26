# Voltage-Reading Accuracy — Shaping Notes

## Scope

Decompose the firmware's measured **+6.8 % to +8.3 % high** VPP/VPE reading error (backlog 999.38,
undetermined since 2026-08-29) into its two possible terms by bench measurement, then apply the part
of the fix that is firmware-only, then retune the VPP guard window against the corrected reading.

The measurement chain is `Vin = adc × 1100 × (R1+R2) / (bandgap_adc × R2)`. It is ratiometric, so
VCC cancels exactly and is **not** an error source. Only two terms can be wrong:

1. the assumed bandgap `1100` (ATmega spread 1.0–1.2 V per chip, no factory trim word on AVR), and
2. the assumed divider `R1=270000 / R2=44000`.

**In scope:** the bench decomposition; making the conversion math natively testable; instrument
fixes (averaging, mux settling, fail-closed on implausible calibration, full-mV on the wire, a VCC
plausibility guard); corrected compiled divider defaults if the measurement selects that arm; the
guard-window retune; disposition of 999.38 and v1.40 RAIL-03.

**Out of scope:** building the per-board calibration wizard. The dormant seed's two-stage design
stands; this spec supplies the numbers that size it (D-D). Also out: any change to high-voltage
**routing** — `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV` stays ADC-independent (v1.40 D-22/D-23).

## Decisions

- **D-A. Diagnose, then fix.** Operator choice. Instrument fixes that are correct either way ship
  first, so the bench session measures a clean instrument.
- **D-B. Probe point = the VPP/VPE net the ADC senses.** Operator choice. Evidence says the drop bit
  switches the MIC2288 *feedback* network — VPP and VPE are two regulated setpoints of one physical
  net, not a series drop. The VPE−VPP difference is neither constant nor a constant ratio across pot
  settings (1.7 V, 2.2 V, 4.76 V across the v1.2 and Phase 199 records), which no fixed series
  resistor and no fixed divider can produce, but two affine setpoint curves with different slopes
  can. **Confirm in Task 4, do not assume.** Consequences: the net is probeable anywhere, and one
  divider calibration serves both rails (seed D4). If no test point is accessible, substitute socket
  pin 1 with P1 asserted (the Phase 199 method) and record the substitution explicitly.
- **D-C. Guard window in scope, retuned AFTER the fix.** Operator choice. New bounds come from the
  measured residual, not a guess.
- **D-D. No per-board calibration built here.** The follow-up may shrink to nothing if the divider
  term dominates.
- **D-E. The error model is gain-only.** Phase 199's two paired ratios agree to 0.3 % across a 5 V
  span. This retires the seed's D1 hedge ("let the procedure discover the model") — the data is in.
  Do not build offset fitting.
- **D-F. Predictions written before the measurement.** Task 4 records falsifiable predictions per
  hypothesis first. Without that, a second board tells us nothing.
- **D-G. Mechanical decisions (taken, not asked):**
  - Pure conversion math is extracted from AVR register access so it can be natively tested.
  - Raw ADC counts reach the host via a **new dev-gated command**, never by widening the
    fixed-length `MSG_DATA_VPP_VOLTAGE` (4×u16, `param_bytes=8`) — that would break older hosts.
  - The stale `MSG_DATA_VPP_VOLTAGE` catalog comment ("raw millivolt integers"; the firmware sends
    pre-split tenths) is corrected in the same catalog edit.
  - A `CONFIG_VERSION` bump resets `r1`/`r2` on every board. Accepted — it resolves the long-live
    stranding todo, and the operator's boards are re-measured in this spec anyway.

## What made this shapeable — three findings from existing evidence

1. **`Internal VCC: 5.5 V` in every Leonardo bench log since v1.2.** An ATmega32U4 cannot run at
   5.5 V. It back-solves to a real bandgap near 1.00–1.01 V, which alone gives +9 to +10 % on VPP —
   *more* than observed, so the divider term partly cancels it. Uno logs report 5.0 V. This is a
   free, no-hardware measurement of error term 1 that has been on screen for two years unread.
2. **Phase 199's paired ratios: 18700/17380 = 1.0759 and 23900/22140 = 1.0795.** Within 0.3 % across
   a 5 V span ⇒ pure gain, no offset (D-E). Also rules out a series drop in the P1 routing, which
   would have appeared as a constant offset (1320 vs 1760 mV), not a constant ratio.
3. **The Rev 1 schematic contradicts the ADC.** Its own boost math gives `VPE-Max = 21.92 V`; the
   meter read 22.14 V at max pot (+1.0 %); the firmware read 23900 mV — 9 % above a voltage the
   MIC2288 feedback network physically cannot produce. The meter agrees with the hardware.

**And the honest limit:** on AVR there is no absolute voltage reference in the chain. AVCC is
USB-derived and unspecified better than ±5 %; the bandgap is a ±9 % per-chip part with no factory
trim. No firmware change can make the reading absolutely accurate — one external measurement per
board is unavoidable for term 1, though it can be one number typed once. What *is* firmware-only:
corrected divider defaults (shield-wide), the instrument fixes, and the stranding fix.

## Context

- **Visuals:** `visuals/rev1-schematic-extract.md` — the boost feedback math and the resistor-value
  census pulled from `firestarter_fw/document/rurp_schematics_rev1.pdf`. No mockups; this is
  hardware work. Bench photographs of the probe points are added when Task 4 runs.
- **References:** see `references.md`.
- **Product alignment:**
  - *Honest claims* (mission): a chip counts as validated only after real silicon, and a report
    states the **measured** voltages. That rule is load-bearing here — the reported voltage has been
    wrong by ~8 % for the whole life of the project, so every "measured VPP" claim on file carries
    that error. Task 7 must say so rather than quietly correcting forward.
  - *Evidence ceiling* (tech-stack): VPE tops out near 22.5 V and no shield reaches the ~6.25 V
    program VCC. Nothing in this spec changes what the hardware can deliver — it changes what the
    firmware honestly reports about it.
  - *VPP is set by hand on every board, permanently on AVR* (tech-stack). So the operator's meter,
    never the firmware's figure, adjudicates the pot — and that standing rule is the workaround this
    spec is trying to retire.
  - *Compare and blank-check run on the host; the firmware only reads and writes* — the guard window
    is a firmware-side safety gate and stays there (v1.40 D-21: the host-side shortfall gate was
    built and fully reverted).

## Standards Applied

Full text in `standards.md`. Summary of why each is here:

- `testing/no-source-introspection` — the only proof of the shipped formula is a source scan; it is
  replaced and deleted.
- `testing/native-firmware-tests` — the new conversion suite registers in both `platformio.ini`
  lists and runs in both native environments.
- `testing/non-vacuity` — a guard that cannot fire is the exact failure v1.40 RAIL-03 recorded.
- `firmware/size-reporting` — Leonardo has 4856 B of margin; averaging and a dev command cost flash.
- `firmware/fail-closed-refusals` — the `return 0` on implausible calibration is fail-open on a
  high-voltage path.
- `firmware/timing` — the settling delay carries a cited datasheet figure.
- `protocol/message-catalog` — the new message ID comes from `messages.toml` in the meta repo only.
- `protocol/duplicated-constants` — the new command ordinal moves in `firestarter.h` and
  `constants.py` together.
- `protocol/rollout-compatibility` — firmware before host; no widening of a fixed-length DATA frame.
- `host/help-docstrings`, `host/echo-vs-logger` — the new host command's surface.
