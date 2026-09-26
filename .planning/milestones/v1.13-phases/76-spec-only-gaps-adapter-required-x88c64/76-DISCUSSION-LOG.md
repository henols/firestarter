# Phase 76: Spec-Only Gaps — adapter-required + X88C64 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-18
**Phase:** 76-spec-only-gaps-adapter-required-x88c64
**Areas discussed:** X88C64 handler gate, GAP-01 rule-arm shape, spec doc home/format, X88C64 reason reword

---

## X88C64 handler gate (GAP-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Verdict + protocol spec only | Datasheet verdict + STORE/RECALL + byte/page write protocol; classify as documented feasible-candidate; NO firmware handler this phase | ✓ |
| Attempt handler if research proves it | Commit the 0x34 handler this phase if research shows fully spec'd + RURP-feasible | |

**User's choice:** Verdict + protocol spec only (recommended).
**Notes:** Phase 74 flash ceiling still open (74-03 deferred) + feasibility MEDIUM; honors "do NOT commit a blind handler". Handler stays a deferred future requirement.

---

## GAP-01 resolve_pinout_key rule-arm shape

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit named classification; pin-map in spec doc | build_db.py arm names AT28C04/16, routes to adapter-required (refusal); full remap lives in spec doc | ✓ |
| Encode full DIP24→DIP32 remap in the arm now | Rule arm carries the actual pin-remap for a drop-in future adapter | |

**User's choice:** Explicit named classification; pin-map in the spec doc (recommended).
**Notes:** Avoids "resurrected guess table"; keeps untestable remap data out of code until an adapter exists.

---

## Adapter pin-map spec — doc home & format

| Option | Description | Selected |
|--------|-------------|----------|
| firestarter/doc + meta .planning, lockstep | Operator-facing pin table + socket re-route in firestarter/doc, canonical copy in meta .planning | ✓ |
| meta .planning only (promote later) | Single meta doc now; promote to firestarter/doc when an adapter is built | |

**User's choice:** firestarter/doc + meta .planning, lockstep (recommended).
**Notes:** Matches the existing two-layer SHIELD-REVISIONS pattern; someone physically builds the adapter so it should be GitHub-visible.

---

## X88C64 unsupported_reason reword

| Option | Description | Selected |
|--------|-------------|----------|
| Reword now as part of GAP-02 | Fix the misleading host-visible string to reflect the datasheet verdict; keep check_dispatch/diff_db green | ✓ |
| Leave untouched this phase | Don't touch the DB string; capture as follow-up | |

**User's choice:** Reword now as part of GAP-02 (recommended).
**Notes:** Current string ("XICOR NovRAM serial-parallel hybrid") is misleading — it's a parallel DIP24 chip. 1-chip reason-string delta, no support_status/dispatch change.

---

## Claude's Discretion

- Filename/section layout of the new adapter spec doc (follow SHIELD-REVISIONS precedent).
- Exact wording of the rewritten X88C64 unsupported_reason (datasheet-accurate, gates green).
- Depth/structure of the X88C64 protocol write-up beyond STORE/RECALL + byte/page write + timing.

## Deferred Ideas

- Graduating AT28C04/16 (and X88C64) to `supported` — needs physical adapter + golden round-trip.
- X88C64 0x34 firmware handler — future flash-ceiling-gated milestone if spec proves feasible.
