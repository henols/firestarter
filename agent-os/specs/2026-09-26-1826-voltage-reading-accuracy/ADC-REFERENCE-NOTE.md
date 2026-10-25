# Which reference the ADC actually uses, and the MUX5 hazard

Written 2026-09-26 in answer to "the Leonardo has a different voltage
reference — is that considered?". It is, and checking it surfaced a latent
defect that is now fixed.

## The two parts differ in two ways, only one of which matters

| | ATmega328P/PB (Uno) | ATmega32U4 (Leonardo) |
|---|---|---|
| Bandgap channel | `MUX[3:0] = 1110` → 14 | `MUX[5:0] = 011110` → 30 |
| `REFS[1:0] = 01` | AVCC | AVCC |
| `REFS[1:0] = 11` | internal **1.1 V** | internal **2.56 V** |

The firmware selects `REFS[1:0] = 01`, AVCC, on both, so the disagreement at
`REFS = 11` never arises. **The bandgap channel is 1.1 V nominal on both
parts** — the 32U4's 2.56 V is a separate *reference* option, not a different
bandgap — so one `RURP_BANDGAP_NOMINAL_MV = 1100` is correct for all three
boards. Only the channel NUMBER differs, and that is the only thing the code
branches on.

Confirmed by the bench: the Leonardo's bandgap count was **206** against a
metered 5.09 V, i.e. 1024 mV. Reading the 2.56 V reference would have given a
count near 515.

## Why not use the 32U4's 2.56 V reference

It removes nothing and breaks the top of the range.

- It is untrimmed too, so the unknown stays exactly as unknown.
- The divider puts **3102 mV** on the pin at the measured maximum VPE of
  22140 mV. That saturates a 2.56 V reference just as it saturates a 1.1 V
  one — using either as the ADC *reference* needs a divider gain of 20.1 or
  more, against the 7.14 every shield has.
- It would make the Leonardo behave unlike the Unos for no accuracy gain.

## Why an internal reference cannot replace the meter at all

Both wirings carry the identical error term. With the reference as AVCC and
the bandgap read as a channel (what we do), and with the bandgap as the
reference (the obvious alternative), the reported value is
`Vin x (Vbg_assumed / Vbg_true)` either way — **AVCC cancels exactly in the
first form**. The error is the unknown value of the reference, and no
rewiring of the multiplexer discovers it.

So the 5 V pin is not a reference. It is a transfer standard: the node where
the operator's meter and the chip can look at one voltage at the same time.
**The meter is the reference.** The 5 V pin is chosen over the VPP rail
because it isolates the bandgap — no pot, no high voltage, no divider in the
path — so the number that comes back is the reference alone.

## The defect this check surfaced, now fixed

On the ATmega32U4, **MUX5 lives in `ADCSRB`, not `ADMUX`**. The bandgap read
wrote `ADMUX` only, so MUX5 kept whatever the previous conversion left. The
bandgap is channel 30 and needs it clear.

It was safe by coincidence, not by construction: this firmware reads only A2
and A3, which are ADC5 and ADC4 on a Leonardo, so nothing ever set MUX5. A
future read of a higher channel would silently redirect the next bandgap
conversion — and on a calibrated board that corrupts every voltage reading,
a stored calibration included.

**Fixed** by computing the register values in `include/rurp_adc_mux.h` rather
than hand-assembling them from bit names, and writing MUX5 explicitly. The
computed values are byte-identical to the previous hand-written ones
(`0x4E` and `0x5E`). Cost: **+10 B on the Leonardo, 0 B on the Unos** — the
compiler folds the arithmetic to the same constant.

`test/native/avr/test_adc_mux` now covers the thing that decides which
voltage the firmware calls its reference, which previously had no test at all
because it lived in an AVR-only translation unit. Two planted breaks are
caught: giving the 32U4 the 328P's channel, and hardwiring MUX5 to 0 — which
is precisely the pre-fix behaviour.


## `dev adc` made self-consistent (same session)

The diagnostic contradicted itself by about one count. `dt_sample_adc` called
`rurp_get_bandgap_adc_reading()` for the reported count, then
`rurp_read_vcc_mv()` and `rurp_read_voltage_mv()` — each of which samples the
bandgap **again**. Three bandgap conversions and two divider conversions per
rail state, so the counts printed described a different instant from the
millivolt figures beside them. Visible in the field as a leonardo reporting
`bandgap 206` next to a VCC that implies 205.

It also back-computed the divider count from the already-rounded millivolt
figure, which lost precision for no reason.

Fixed by exposing `rurp_read_divider_adc()` alongside the existing bandgap
accessor on both platforms, so `dev adc` takes **exactly one sample of each
channel** and derives all four numbers from those two. `rurp_read_voltage_mv`
uses the same accessor, so nothing is duplicated.

Not a correctness issue for calibration or for the VPP path — both always used
a matched pair internally — but a diagnostic whose own numbers disagree is
worth nothing when the next reader is trying to decompose a 0.5 % term.

## Supply independence, confirmed on the bench

Asked whether changing the USB port invalidates a calibration. It does not,
and the boards show why: the supply shifts about **0.5 %** the moment the boost
regulator loads it, **within one `dev adc` sweep** — leonardo 5065 → 5090 mV,
uno 4961 → 4940, uno328pb 5120 → 5096. The bandgap count moves with it, the
reported VCC correctly tracks it, and the VPP figure is unaffected.

The algebra behind that: `Vin = adc_div * Vbg_stored * G / adc_bg`, and both
counts are `V/AVCC * 1024`, so the supply scales them together and divides out.
Over 4.80–5.25 V the counts move 9 % and the reported voltage moves not at all.

**This is the reason the stored value is a bandgap and not a gain correction.**
A gain would be tied to the supply it was measured at. A bandgap is a property
of the die.

Only swapping the Arduino requires recalibration. Swapping the shield changes
the divider (~1 %), which calibration does not cover — a larger residual, not a
recalibration. The bandgap has a temperature coefficient, well under the
3–5 % window but real.
