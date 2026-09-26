# Task 6 — the VPP acceptance window, retuned

Done 2026-09-26, after calibration made the reading trustworthy (D-C: retune
after the fix, never before).

## Measured figures

```
RURP_VPP_HIGH_HEADROOM_PCT       = 3
RURP_VPP_HIGH_HEADROOM_FLOOR_MV  = 500
RURP_VPP_LOW_TOLERANCE_PCT       = 5
INSTRUMENT_RESIDUAL_RSS_PCT_X100 = 142
INSTRUMENT_RESIDUAL_WORST_PCT_X100 = 330
ROWS_WITH_THRESHOLD_CHANGED      = 30
ROWS_WITH_THRESHOLD_UNCHANGED    = 716
```

## The uncertainty budget the bounds are sized against

| term | % |
|---|---|
| divider assumed nominal; measured `G_true` 7.1974 vs 7.1364 | 0.85 |
| divider spread across boards (rails-off counts 136–138) | 0.73 |
| calibration quantisation, one bandgap count | 0.48 |
| operator meter accuracy, 3½-digit DMM | 0.50 |
| bandgap read jitter, ±1 count | 0.45 |
| divider read quantisation, 1 count of ~341 at 12 V | 0.29 |
| **RSS (typical)** | **1.42** |
| **linear sum (worst case)** | **3.30** |

## What changed, and what deliberately did not

**HIGH was a flat +500 mV.** That is +4.2 % at a 12000 mV target but only
+2.0 % at 25000 — tighter than the worst case above, so it could refuse a
correctly set rail on measurement error alone. It is now a **3 % headroom with
a 500 mV floor**.

| target | rows | old ceiling | new ceiling |
|---|---|---|---|
| 9000–13500 | 716 | +500 | **+500 (unchanged)** |
| 18000 | 21 | +500 | +540 |
| 21000 | 3 | +500 | +630 |
| 25000 | 6 | +500 | +750 |

The 30 rows that move are exactly the census Phase 199 was about. Every row
below 18000 mV — 716 of 746 — keeps the identical threshold it had.

**LOW stays at 5 %**, now justified rather than inherited: comfortably outside
the worst case, so it raises no false warning, and it can finally see a real
shortfall, which before calibration it could not because the reading itself was
inflated by more than the window.

**Routing is untouched.** `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV` still decides
the route from path capability and never from a reading (v1.40 D-22/D-23).
This is the verification leg only.

**New: `MSG_WARN_NOT_CALIBRATED` (0x89).** A retuned window is meaningless on a
board that has never been calibrated — the reading there carries the full
per-die bandgap spread, up to 10 %, against a 3–5 % window. The operation now
says so once per voltage-gated operation, and does not refuse.

## v1.40 RAIL-03 — adjudicated, and it still cannot close

> **RAIL-03:** When a part's required VPP exceeds what the shield can deliver,
> the operation proceeds with a warning that names the required voltage **and
> the deliverable one**. It does not refuse silently, and it does not attempt
> silently.

v1.40 recorded two defects. **One is now fixed, one is not, and the unfixed one
is the substance of the requirement.**

- **Fixed.** "Its 5 % trigger window is narrower than the measured +7.59 %
  discrepancy, so it cannot see the shortfalls that exist." Calibration removed
  the discrepancy: the residual is now 1.42 % typical, 3.30 % worst case, so a
  5 % window sits outside it and a reading that trips it is a real shortfall.
- **NOT fixed.** "It names the live reading rather than the deliverable
  figure." `MSG_WARN_VPP_LOW` still reports measured-versus-target. Nothing
  compares a row's requirement against what the selected path can physically
  deliver, which is what RAIL-03 actually asks for.

**Why the unfixed half was not built here.** It needs a deliverable figure per
route. Two exist and are measured — drop path 17380 mV, direct VPE 22140 mV at
socket pin 1. The third does not: the six rows at 25000 mV take VPE to **pin
21** through `CTRL_VPE_ENABLE`, and v1.40 D-06 deliberately did not measure
that path. Those six rows are precisely the ones most likely to exceed what the
shield delivers, so building the warning against a pin-1 figure would give them
a number that is not about their path — the exact substitution D-06 forbids.

**What would close it:** one attended bench session measuring the pin-21 VPE
path, then a pre-flight capability comparison naming both figures. That is a
feature of its own, not a retune, and it stays ADC-independent like the routing
decision it sits beside.

RAIL-03 therefore stays **Pending**, now blocked on one measurement rather than
on an untrustworthy instrument.
