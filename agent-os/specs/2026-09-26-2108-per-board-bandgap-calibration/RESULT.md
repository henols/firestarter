# Per-board bandgap calibration — result

**Built and verified on silicon 2026-09-26**, on three boards across three
shield revisions.

## Measured figures

```
LEONARDO_BANDGAP_CALIBRATED_MV  = 1019
UNO_BANDGAP_CALIBRATED_MV       = 1095
UNO328PB_BANDGAP_CALIBRATED_MV  = 1050
LEONARDO_VPP_BEFORE_MV          = 12994
LEONARDO_VPP_AFTER_MV           = 12036
VPP_HIGH_GUARD_AT_12V_MV        = 12500
```

## What the calibration does

One meter reading on the 5 V header pin. The firmware reads its own bandgap
count and back-solves `bandgap_mv = vcc_meter * bandgap_adc / 1024`. No pot,
no high voltage, chip may stay seated, and it works on a stable image because
the arithmetic is in the firmware rather than the host.

```
firestarter cal --vcc 5.09
```

## Verified

**The reported supply now matches the meter.**

| Board | meter | reported before | reported after |
|---|---|---|---|
| leonardo | 5.09 V | 5468 mV | **5090 mV** |
| uno | 4.94 V | 4940 mV | 4961 mV |
| uno328pb | 5.12 V | 5364 mV | **5120 mV** |

**The leonardo can write again.** On an unchanged rail its VPP reading moved
`12994 -> 12036 mV`. The HIGH guard for a 12000 mV target fires above
12500 mV, so before calibration a correctly set rail was refused — the failure
that stopped v1.34 cell A3/B2 — and after calibration it is inside the window.

**The VCC plausibility guard is now silent on all three.** It fired on the
leonardo and uno328pb before calibration and on neither after, with no
knowledge of any figure in this file. Same instrument, opposite verdict,
because the boards changed.

**The operator's shield override survived the CONFIG_VERSION bump.** The
leonardo still reports `Rev 2.2 (override)` after migrating VER06 -> VER07.
The previous version-gated wipe would have reset it to 0xFF.

## The residual, and why it is not chased

One bandgap ADC count, about 0.5 %. The uno reads 4961 against a metered
4940 for exactly that reason.

It is deliberately left there. A 3.5-digit multimeter reading 5.09 V is
itself about +/-0.5 %, so **the calibration is now bounded by the operator's
instrument, not by the firmware**. Recovering sub-count resolution would need
the oversampled sum carried through the arithmetic, and would buy precision
the input cannot support.

Averaging was changed from truncating to rounding, which halves the
quantization error for two tokens and is worth having regardless.

## What this closed

- The per-die bandgap error measured in the previous spec: 7.9 %, 0.5 % and
  4.8 % on the three boards, now corrected per board.
- The stranding defect in
  `.planning/todos/pending/config-version-not-bumped-strands-stale-eeprom-calibration.md`,
  by its own option 2. A stale `r1 = 1000` is now corrected by a range check
  regardless of the version string, which the version gate could never reach.
- The unconditional `hardware_revision` reset on every version bump.

## Still open

- **v1.43 Task 6, the guard window retune,** is now unblocked: the reading is
  trustworthy, so the -5 %/+500 mV window can be judged on its merits rather
  than against instrument error.
- **Stage 2, the divider trim,** is not built. Measured at about 1 %, below
  the one-count resolution of this instrument.
- Rail readings on the leonardo and uno328pb at a known pot setting would
  close their per-board divider terms. The uno's is closed.
