# v1.43 — Bench record: decomposing the voltage-reading error

**Measured:** 2026-09-26, meta `8702f4b9` on branch `v1.43-voltage-reading-accuracy`.

## Measured figures

Later tasks parse the integers from this block. Read them from here; do not
re-transcribe them from prose elsewhere in this file.

```
LEONARDO_BANDGAP_ADC        = 206
LEONARDO_RAILS_OFF_ADC      = 137
UNO_BANDGAP_ADC             = 228
UNO_RAILS_OFF_ADC           = 138
UNO328PB_BANDGAP_ADC        = 210
UNO328PB_RAILS_OFF_ADC      = 136
DIVIDER_R1_IN_USE           = 270000
DIVIDER_R2_IN_USE           = 44000
LEONARDO_VCC_METER_MV       = 5090
UNO_VCC_METER_MV            = 4940
UNO328PB_VCC_METER_MV       = 5120
UNO_VPP_METER_MV            = 11180
UNO_VPP_FIRMWARE_MV         = 11086
```

Meter readings are the operator's, taken 2026-09-26 on the 5 V header pin of
each board, plus one VPP rail reading on the uno. Reported verbatim as
`PB 5.12v / Leonardo 5.09v / Uno 4.94v - 11.18v`. Claude did not take them
and cannot verify them.

## Session setup

Port identity probed in this session per board, not inherited. All three
boards were flashed in this session with a **locally built** `-D DEV_TOOLS=1`
image that self-reports as `3.1.0b3` and is **NOT** the released `3.1.0b3` —
no published image carries `CMD_DEV_ADC`. avrdude verified each write.

| Port | Controller | Shield (firmware-reported) | Flashed | avrdude verify |
|---|---|---|---|---|
| `/dev/ttyACM0` | leonardo | Rev 2.2 (operator override) | 25374 B | verified |
| `/dev/ttyACM1` | uno | Rev 2.0-class | 22964 B | verified |
| `/dev/ttyUSB0` | uno328pb | Rev 1 | 23168 B | verified |

The firmware-reported shield revision is **not** evidence of the physical
revision — Rev 2.0/2.1/2.2 share a resistor band. It is recorded only so a
later reader can see it was consulted.

**Operator statement, 2026-09-26, verbatim: "both sockets are empty"** — the
chip-out precondition for sideloading the two Uno-class boards. Claude cannot
verify this; it is recorded as an operator statement, not a measurement.

## Raw readings — `firestarter dev adc`

One sweep per board. All three rail states in one command, so all three
samples on a board share one pot setting.

| Board | state | divider adc | bandgap adc | V (mV) | VCC (mV) |
|---|---|---|---|---|---|
| leonardo | rails off | 137 | 206 | 5221 | 5468 |
| leonardo | VPP | 341 | 206 | 12994 | 5468 |
| leonardo | VPE | 397 | 205 | 15202 | 5495 |
| uno | rails off | 138 | 228 | 4738 | 4962 |
| uno | VPP | 322 | 228 | 11086 | 4940 |
| uno | VPE | 369 | 228 | 12705 | 4940 |
| uno328pb | rails off | 136 | 210 | 5084 | 5364 |
| uno328pb | VPP | 325 | 210 | 12149 | 5364 |
| uno328pb | VPE | 373 | 210 | 13943 | 5364 |

The VPP and VPE millivolt figures are **not comparable between boards**: each
shield has its own potentiometer at its own setting. Only the rails-off and
bandgap columns are cross-comparable.

## The decomposition

The ADC is ratiometric, so for any channel `reading = V_in / VCC * 1024`.

**The divider term, and why it needs no meter.** With the regulator off, the
divider's top node sits at `VCC - Vf(D1)`, so

```
G_true = (1 - Vf/VCC) * 1024 / rails_off_adc
```

`VCC` very nearly cancels: at Vf = 200 mV, changing VCC from 4.9 V to 5.1 V
moves `G_true` by under 0.1 %. So the rails-off count is a near-pure measure
of the divider ratio, independent of both the supply and the bandgap.

| Board | Shield | rails-off adc | G_true @ Vf=100mV | @ 200mV | @ 300mV |
|---|---|---|---|---|---|
| leonardo | Rev 2.2 | 137 | 7.3250 | 7.1755 | 7.0260 |
| uno | Rev 2.0 | 138 | 7.2719 | 7.1235 | 6.9751 |
| uno328pb | Rev 1 | 136 | 7.3788 | 7.2282 | 7.0776 |

Nominal `G = 314000/44000 = 7.1364`.

**Finding D-1: the divider is nominal, on all three shield revisions.** The
three counts span 136–138, a 1.5 % spread across Rev 1, Rev 2.0 and Rev 2.2
hardware, and at any plausible Schottky Vf they bracket the nominal 7.1364.
`VALUE_R2 = 44000` is therefore correct — the shaping note's worry that the
Rev 1 schematic carries no 44k part is resolved in favour of 22k + 22k.
**The divider contributes about ±1 %, not ±8 %.**

*Caveat, stated not hidden:* Vf of D1 at the ~16 µA the divider draws is
assumed, not measured. It shifts every G_true in the table by the same
amount, so it cannot explain the boards **agreeing** — which is the load-
bearing observation.

**The bandgap term, measured.** `Vbg_true = bandgap_adc * VCC_meter / 1024`.

| Board | bandgap adc | VCC (meter) | **Vbg_true** | VPP error from the bandgap alone |
|---|---|---|---|---|
| leonardo | 206 | 5090 mV | **1024.0 mV** | **+7.43 %** |
| uno | 228 | 4940 mV | **1099.9 mV** | **+0.01 %** |
| uno328pb | 210 | 5120 mV | **1050.0 mV** | **+4.76 %** |

**Finding D-2: the bandgap varies per MCU, and that variation is the error.**
Three ATmega parts, three different references, all inside the datasheet's
1.0-1.2 V window. The uno's is 1099.9 mV -- within 0.1 mV of the 1100 the
firmware assumes -- and the leonardo's is 76 mV below it.

**Finding D-3, CONFIRMED end to end: D-4's falsifiable prediction held.**
The prediction written before the meter reading was that the uno, alone of
the three, should agree with a meter to about 1 %. Measured:

| | firmware | meter | error |
|---|---|---|---|
| uno VPP rail | 11086 mV | 11180 mV | **-0.84 %** |

Predicted from the bandgap term alone: +0.01 %. The residual is **-0.85 %**,
which is the divider term, and it gives `G_true = 7.1974` against the nominal
7.1364. Back-solving the rails-off count for that ratio implies a Schottky
forward drop of **148 mV** at the ~16 uA the divider draws -- squarely where a
1N5819 sits at that current.

So the two independent routes agree: the rails-off ADC count and the
meter-vs-firmware rail pair both put the divider within about 1 % of nominal.
**D-1 and D-2 are confirmed, and the model closes.**

*What is NOT claimed:* carrying the uno's 148 mV Vf across to the other two
boards predicts +5.65 % for the leonardo, while Phase 199 measured +7.59 % on
a Leonardo. The bandgap term alone predicts +7.43 %, which matches Phase 199
closely. One ADC count is 0.7 % here, so the per-board divider term is at the
edge of this instrument's resolution and must be measured per board, not
inferred from another board. Do not treat the -0.85 % as a global constant.

## Consequence for the fix

**The error is per-MCU, so no firmware-only change can remove it.** This is
the plan's D-A question answered, and it answers against the operator's stated
preference. Three boards carrying three different shield revisions produce
errors of +7.4 %, +4.8 % and +0.0 % from the bandgap term alone. No single
compiled constant can be right for all three, because the quantity that
differs is a property of each ATmega die and the part carries no factory trim
word.

The plan's Task 5 "divider term confirmed wrong" arm therefore **does not
apply**: `VALUE_R1`/`VALUE_R2` are correct and changing them would move every
reading by about 1 % while leaving 7 % on the leonardo.

What applies is the dormant seed's **Stage 1**: store a per-board measured
bandgap and use it in place of the literal 1100. Everything needed to do that
is now in this file -- `Vbg_true = bandgap_adc * VCC_meter / 1024`, one meter
reading on the 5 V pin, no pot and no high voltage. The seed's **Stage 2**
(divider trim) is worth about 1 % on this evidence and is optional.

## The guard, validated on hardware

`MSG_WARN_VCC_IMPLAUSIBLE` (band 4400-5250 mV) was run against all three
boards. The result is non-vacuous rather than uniformly quiet:

| Board | reported VCC | warns? | measured Vbg |
|---|---|---|---|
| leonardo | 5468 mV | yes | 1024.0 mV |
| uno328pb | 5364 mV | yes | 1050.0 mV |
| uno | 4940 mV | **no** | 1099.9 mV |

The silent board is the one whose real bandgap is what the firmware assumes.
The guard separates the two miscalibrated boards from the good one, with no
knowledge of any of the numbers in this record.

## Still owed

- Meter on a rail at a known pot setting for the **leonardo** and
  **uno328pb**, to close their per-board divider terms the way the uno's is
  closed. Until then their divider term is inferred, not measured.
- The in-circuit divider resistance check (plan Task 4 Stage 3). D-1 answers
  what it was for, so it is now corroboration rather than a discriminator.
