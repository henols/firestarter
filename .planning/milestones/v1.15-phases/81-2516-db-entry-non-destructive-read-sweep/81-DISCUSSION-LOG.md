# Phase 81: 2516 DB Entry + Non-Destructive Read Sweep - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-23
**Phase:** 81-2516-db-entry-non-destructive-read-sweep
**Areas discussed:** 2516 manual safety review, DB-02 FLAG_CAN_ERASE rigor, read-sweep anomaly policy, non-UV blank-check semantics

---

## 2516 manual safety review

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated review doc + you gate | Claude proposes a Phase-58 SR-1-style checklist in `81-2516-SAFETY-REVIEW.md`; operator signs off before any bench session. Most auditable. | ✓ |
| Inline in EVIDENCE record | Fold the 5-point checklist into EVIDENCE.{md,json}; one artifact, less ceremony. | |
| Claude reviews, notes in plan | Claude performs+records the checklist in the plan summary; no separate human sign-off. | |

**User's choice:** Dedicated review doc + operator human gate
**Notes:** The override bypasses `check_dispatch.py`/`diff_db.py` and Phase 83 will write the irreplaceable 2516 off this decode — operator wants a personal sign-off, not a self-attestation. → CONTEXT D-01/D-02/D-03.

---

## DB-02 FLAG_CAN_ERASE rigor

| Option | Description | Selected |
|--------|-------------|----------|
| Confirm + ensure Flash/EEPROM test | Read-only confirm Phase 77's wiring; add a Flash/EEPROM pinning test if absent; fix only on a real gap. | |
| Fresh adversarial re-audit | Re-derive the full path from scratch ignoring Phase 77's conclusion, then pin with tests. Heavier. | ✓ |
| Formality only | Trust Phase 77; note "confirmed, no change"; no new test unless CI is red. | |

**User's choice:** Fresh adversarial re-audit
**Notes:** W29C020/W29C040 are `Flash/EEPROM` (not `EEPROM`) and get bench-proven for the first time in Phase 82 — the Flash/EEPROM erase branch must be independently proven, not inherited. → CONTEXT D-04/D-05.

---

## Read-sweep anomaly policy

| Option | Description | Selected |
|--------|-------------|----------|
| Reseat+retry, record, continue | Reseat + retry up to N; if still dirty record verdict=ANOMALY and continue; flag genuine defects for Phase 84 FIX-01. | ✓ |
| Halt on first anomaly | Stop the sweep on the first non-clean read for a decision. | |
| Record-only, no retry | Single read per chip; record whatever comes back; no reseat/retry. | |

**User's choice:** Reseat + retry, record, continue
**Notes:** Sweep is non-destructive → no reason to halt. Aligns with bench memory (retry-on-timeout / never-trust-N=1; all-0xFF = contact fault → reseat). → CONTEXT D-06/D-07.

---

## Non-UV blank-check semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Read + note current state | Non-UV chips get a read + observed-state summary (not a pass/fail blank gate); only the 3 UV-EPROMs get a gating blank-state (SWEEP-02). | ✓ |
| Full blank-check on all 11 | Run blank-check on every chip and record blank/not-blank uniformly. | |
| Skip non-UV blank entirely | Read-only for the 8 non-UV chips; blank-check only the 3 UV-EPROMs. | |

**User's choice:** Read + note current state
**Notes:** EEPROMs aren't factory-blank and FRAM is never blank — a uniform pass/fail blank gate would be misleading. → CONTEXT D-08/D-09.

---

## Claude's Discretion

- Exact EVIDENCE.{md,json} schema shape (must carry the locked columns + extend the v1.13 matrix).
- Reseat/retry count default (D-07: up to 2) and the exact read command/flags.
- Whether the safety-review captures a `firestarter info 2516` transcript as evidence.

## Deferred Ideas

- 2516 write proof on the ~22.4V VPE rail (Phase 83 / GRAD-03; closes FUT-03).
- Promote 2516 user-override → `build_db.py` (FUT-B, only if it appears upstream).
- 8-chip write→verify validation (Phase 82); consolidated decode audit + RCA (Phase 84).
- Carried pending todos (avrdude / cobs-deadline / uno328pb-jitter) — off-scope, not folded.
