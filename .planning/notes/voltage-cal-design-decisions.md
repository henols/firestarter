---
title: Voltage-reading calibration — design decisions
date: 2026-07-03
context: Captured during /gsd-explore 2026-07-03. Records the reasoning behind the white-box, two-stage calibration design so a future planner doesn't re-litigate it. Companion to seed voltage-reading-whitebox-calibration.md and the v1.25 QUEUED milestone.
---

# Voltage-reading calibration — why the design is what it is

> **D1 IS RETIRED (2026-09-26).** It said "we do not assume the error model, the
> procedure discovers it". The model is now measured: pure gain, no offset —
> Phase 199's two paired ratios agree to 0.3 % across a 5 V span. A one-point
> correction through the origin is sufficient and offset fitting must not be
> built. Every other decision here (D2-D7) survived implementation unchanged.

The idea: let the end-user measure real voltages with a DMM, guided by a
calibration step, and correct the firmware's voltage-divider reading math.
These are the forks we resolved during the explore session and the reasoning.

## D1 — Error-model discovery, not assumption

We do **not** assume up front whether the error is pure gain, gain+offset, or
nonlinear. The procedure captures several `(firmware-reading, DMM-actual)` pairs
and fits; if the offset comes out ≈0 it collapses to a gain correction for free.
This defends the user's "measure at different levels" instinct without
over-committing to a model. (Decided after the operator flagged the error shape
as "not something we must investigate up front" — so the *procedure* investigates
it.)

## D2 — White-box over black-box  → **white-box**

Two ways to "adjust the calculation":
- **Black box:** fit `actual = gain × reading (+ offset)` on the final mV, store
  gain/offset, apply at the end. Simple and model-agnostic, but the stored numbers
  are physically meaningless and it does **not** fix VCC reads.
- **White box (chosen):** solve for the physically-real parameters — the true
  per-board bandgap voltage (replacing the hardcoded `1100`) and, optionally, the
  divider ratio.

Chosen because: the bandgap is the *dominant* error (±10 % vs the divider's
±1–2 %), it is pure gain (matching the "constant percentage" error you'd expect),
it is physically honest, and correcting it fixes **VCC and VPP/VPE together** —
`rurp_read_vcc_mv` hardcodes `1126400 = 1100 × 1024`, so the same calibrated
bandgap flows into both formulas.

## D3 — Two stages, measured at two different nodes → **both**

- **Stage 1 (bandgap):** measured off the **fixed 5 V VCC line, no pot.**
  `V_bg = VCC_dmm × bandgap_adc / 1024`. This is where nearly all the accuracy
  comes from, and it's the easiest measurement. Isolating the bandgap *requires*
  measuring at VCC — a VPP-only measurement can't separate bandgap error from
  divider error, and folding a divider error into the stored bandgap would then
  mis-correct VCC.
- **Stage 2 (divider trim):** the pot-and-DMM procedure on VPP, trimming
  `(r1+r2)/r2` for the residual. Optional polish; Stage 1 alone is already useful.

Bonus: this cleanly separates **MCU-specific** cal (bandgap → follows the Arduino)
from **shield-specific** cal (divider → follows the shield), which matters because
shields get swapped between boards.

## D4 — One sense node covers VPP and VPE

Firmware reads only `PIN_VPP_VOLTAGE_ADC`; VPE is VPP dropped through
`CTRL_VPP_VPE_DROP_ENABLE`. So one divider calibration serves both rails — no
separate VPE calibration path needed.

## D5 — UX: no live monitor loop

Tool states the target level → user adjusts the pot and reports the DMM value →
firmware takes **one** confirmation read. No turn-based polling while the operator
turns the pot (that races the adjustment). Consistent with the operator's standing
bench rule.

## D6 — Storage & migration

The calibrated bandgap is a new field in `rurp_configuration_t` → `CONFIG_VERSION`
bump + EEPROM migration. Existing configs default the field to 1100 mV, i.e.
identity, so upgrading changes no behavior until the user calibrates. This retires
the practice of abusing `r1` as the correction knob.

## D7 — Safety is load-bearing, not optional

Calibration writes the numbers the firmware *trusts* to decide programming
voltages, so a bad cal can over/under-volt a chip. The design mandates:
plausibility bounds (reject implausible `V_bg`/divider values), explicit
confirm-before-write (old→new), and a reset-to-defaults escape hatch. This
graduates from "nice to have" to a hard requirement for the milestone.
