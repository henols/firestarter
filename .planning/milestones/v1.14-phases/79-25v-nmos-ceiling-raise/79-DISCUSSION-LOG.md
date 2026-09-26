# Phase 79: 25V NMOS Ceiling Raise - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-23
**Phase:** 79-25v-nmos-ceiling-raise
**Areas discussed:** Discussion intent, Gate methodology re-examination, Reframe sign-off

---

## Discussion intent

| Option | Description | Selected |
|--------|-------------|----------|
| Plan the PCB mod | Capture decisions about the feedback-resistor change | |
| Decide: defer vs proceed | (a)-vs-(b) milestone decision | |
| Re-examine the gate | Question whether NOT CLEARED is the full story (dry-run measured the default ~12V rail) | ✓ |
| Something else | Free-text | |

**User's choice:** Re-examine the gate
**Notes:** Triggered a firmware-level investigation of how VPP is actually generated and measured.

---

## Gate methodology re-examination

| Option | Description | Selected |
|--------|-------------|----------|
| Re-run on direct path | Re-measure on the direct VPE (0x0B) rail; prior verdict measured the wrong (dropped) path | |
| Conclusion stands — defer | Direct path docs ~18V < 25V; accept hardware-change requirement, defer FUT-03 | |
| Re-run + expect hw change | Re-run for a clean number but pre-authorize a PCB change | |

**User's choice:** Free-text correction (superseded the options).
**Notes:** Operator corrected the hardware model: the VPP regulator is controlled by a
**potentiometer on the shield**, not the firmware and not PCB feedback resistors. The host
sends `vpp_mv` to the firmware specifically so the firmware can **block over-voltage and warn
on under-voltage**. For 25V EPROMs the pot must be cranked to max and the direct VPE path used;
if max still isn't enough, the under-voltage path "just hope for the best." Firmware verified:
over-voltage = ERROR/block (unless FLAG_FORCE), under-voltage = WARNING/proceed
(eprom.cpp:229-270); `firestarter vpp` always forces the dropped path (hardware_operations.cpp:28),
confirming the prior ~12V reading was the wrong electrical path for 0x0B.

---

## Reframe sign-off

| Option | Description | Selected |
|--------|-------------|----------|
| Lock it as described | Unblock via pot+FW-protection; graduation proven by Leonardo write+verify; no hard ≥25V pre-gate | |
| Lock, but keep ≥25V gate | Same reframe, but still require corrected dry-run to measure ≥25V (pot@max, direct VPE) before ceiling raise | ✓ |
| Let me adjust | Correct specifics first | |

**User's choice:** Lock, but keep ≥25V gate (conservative)
**Notes:** Corrected hardware model + corrected gate methodology accepted, but the ≥25V
measurement remains a HARD pre-gate before the ceiling change. Do not lean on the firmware's
under-voltage warn-and-proceed to graduate a 25V chip on an inadequate rail.

## Claude's Discretion

- Exact `dev reg` incantation for the direct-VPE (drop-disabled) hold — refine against live
  firmware, provided it measures the 0x0B path and not `firestarter vpp`'s dropped path.

## Deferred Ideas

- Soft/best-effort graduation relying on under-voltage warn-and-proceed — rejected this phase;
  possible future `--force` write mode separate from `supported` graduation.
- Correcting REQUIREMENTS.md FUT-03 root-cause text (PCB-resistor → manual pot) during re-plan.
