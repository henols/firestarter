---
title: White-box voltage-reading calibration (per-board bandgap + divider trim)
trigger_condition: An accuracy/hardware-focused milestone opens, or a user reports inaccurate VPP/VPE readings that today's hand-tuned r1 hack can't fix
planted_date: 2026-07-03
status: implemented
implemented: 2026-09-26
---

# White-box voltage-reading calibration

> **IMPLEMENTED 2026-09-26 (v1.43). Stage 1 only; Stage 2 deliberately not built.**
>
> The design below held up. Three corrections from measurement, recorded so a
> later reader does not re-derive them:
>
> 1. **D1 is retired.** This seed hedged on the error model and had the
>    procedure discover it. It is measured: **pure gain, no offset** (two paired
>    ratios agreeing to 0.3 % across a 5 V span). Do not build offset fitting.
> 2. **Stage 2 is worth about 1 %, not 1-2 %, and was not built.** The divider
>    is nominal on all three shield revisions — rails-off ADC counts 137/138/136
>    — so `VALUE_R2 = 44000` is confirmed and the residual is below this
>    instrument's one-count resolution of 0.7 %.
> 3. **Two things this seed did not anticipate.** The calibration must sample in
>    PROGRAMMER mode, because that is the mode every real measurement is taken
>    in and the I/O state moves the bandgap by a whole count on a SERIAL_ON_IO
>    board. And D6's "existing configs default to 1100 = identity, no behaviour
>    change" understated the migration: the old version-gated wipe also reset
>    `hardware_revision`, destroying the operator's shield override, so the
>    migration had to become a per-field range check rather than a wipe.
>
> Results: `agent-os/specs/2026-09-26-2108-per-board-bandgap-calibration/RESULT.md`.
> The measurement that selected this arm:
> `agent-os/specs/2026-09-26-1826-voltage-reading-accuracy/BENCH-RECORD.md`.

A guided, two-stage calibration procedure that makes the firmware's VPP/VPE (and
VCC) voltage readings accurate per physical board, by replacing today's
hand-tuned-`r1` hack with a **physically-meaningful, white-box** correction:
calibrate the true per-board internal bandgap voltage, then optionally trim the
resistor-divider ratio.

Rationale trail: `.planning/notes/voltage-cal-design-decisions.md`.

## The problem

`rurp_read_voltage_mv` ([firestarter/src/boards/rurp_common.cpp:52-71](../../firestarter/src/boards/rurp_common.cpp#L52-L71)) computes:

```
Vin_mV = (voltage_adc × 1100 × (r1 + r2)) / (bandgap_adc × r2)
```

and `rurp_read_vcc_mv` (same file, :42-50) uses `1126400 = 1100 × 1024`.

Three error sources are baked in:

1. **The `1100` — the internal bandgap, assumed *exact*, really ±10%** (a real
   ATmega bandgap is ~1.0–1.2 V). This is multiplicative on *every* reading and
   is almost certainly the dominant error. It also corrupts VCC reads.
2. **The divider ratio `(r1+r2)/r2`** (`r1`/`r2` in EEPROM config, defaults
   270000/44000) — only resistor tolerance, ±1–2 %.
3. **The ADC** (assumed linear, offset-free).

Today's only "calibration" is hand-editing `r1` (e.g. the uno328pb
1000→270000 fix). That's a single **gain** knob through the origin — it cannot
separate the bandgap error from divider error, and it doesn't fix VCC. The
error model isn't assumed up front: the procedure *measures* several
`(firmware-reading, DMM-actual)` pairs and lets the data decide (collapses to
pure gain if no offset shows up).

## Design (locked in the explore session)

**White-box, two-stage.** One sense node — `PIN_VPP_VOLTAGE_ADC` — covers both
VPP and VPE (VPE is VPP dropped through `CTRL_VPP_VPE_DROP_ENABLE`), so a single
divider calibration serves both.

### Stage 1 — bandgap (the big ±10 % win; MCU-specific, travels with the Arduino)
- Measured off the **fixed 5 V VCC line — no pot involved.** Easiest possible
  measurement; 5 V is always present.
- User puts DMM on the Arduino 5 V pin and enters the reading. Firmware reads the
  bandgap ADC and back-solves the true bandgap:
  `V_bg = VCC_dmm × bandgap_adc / 1024`.
- `V_bg` is a stable physical constant of *that* chip. Store it in config and use
  it in place of the hardcoded `1100` (and `1024 × V_bg` in place of `1126400`),
  so **both** VCC and VPP/VPE reads improve. Doing Stage 1 alone already fixes the
  dominant error.

### Stage 2 — divider trim (the ±1–2 % residual; shield-specific, travels with the shield)
- The pot procedure: tool names a target level, user adjusts the pot, measures
  VPP with the DMM, and reports back. Firmware takes **one** confirmation ADC read
  at that instant (no live monitor loop — see
  [[feedback_operator_adjusts_pot_solo]]).
- With `V_bg` already known, trim `(r1+r2)/r2` to kill the leftover
  resistor-tolerance error. Optional polish on top of Stage 1.

The MCU-vs-shield split matters because shields get swapped between boards
([[user_shield_revisions]]): bandgap cal follows the Arduino, divider cal follows
the shield.

## Scope / shape (rough)

- **Firmware (dual-repo lockstep, firmware-touching):**
  - New calibrated-bandgap field in `rurp_configuration_t`
    ([firestarter/include/rurp_types.h](../../firestarter/include/rurp_types.h)) →
    `CONFIG_VERSION` bump + EEPROM migration (existing configs default the field
    to 1100 mV = identity → no behavior change on upgrade).
  - `rurp_read_voltage_mv` / `rurp_read_vcc_mv` read the calibrated bandgap instead
    of the literal `1100` / `1126400`.
  - A way to expose one raw confirmation read (bandgap ADC + voltage ADC) on demand
    — likely a `dev`-level command or an extension of the existing config path.
- **Host (guided wizard, e.g. `firestarter dev calibrate`):** drives the two
  stages, computes `V_bg` and the divider trim, shows before/after, writes config.
- **Safety (non-negotiable — a bad cal makes the firmware *trust* wrong
  voltages → can over/under-volt a chip):**
  - Plausibility bounds (reject `V_bg` outside ~[1000, 1200] mV; reject implausible
    divider trims).
  - Explicit confirm-before-write showing old→new.
  - A `--reset`/restore-defaults escape hatch (1100 / 270000 / 44000).

## Open questions (before planning)

See `.planning/research/questions.md` — "White-box voltage calibration".

## Relation to other work

- Supersedes the recurring hand-tuned-`r1` workaround
  ([[project_uno328pb_vpp_recal_and_program_brownout]]).
- Complements the `vpp`/`vpe` monitors + held-rail bench tooling
  ([[reference_v114_bench_erase_rail_and_test_artifact]],
  [[reference_held_rail_dtr_reset_hold_script]]).
