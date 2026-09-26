# Phase 49: Framing Mechanism Decision (COBS `0x00` vs SLIP `0xC0`) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-01
**Phase:** 49-framing-mechanism-decision-cobs-0x00-vs-slip-0xc0
**Areas discussed:** Mechanism posture, SAFE-01 proof rigor, Decision artifact, Contract depth

---

## Mechanism Posture

| Option | Description | Selected |
|--------|-------------|----------|
| Lean SLIP, confirm with evidence | Treat SLIP `0xC0` as presumptive winner (safety-first), record justifies it against COBS | |
| Neutral evidence-driven | No thumb on the scale — research builds full comparison, record picks on weighted criteria | ✓ |
| Lean COBS, confirm with evidence | Treat streaming COBS `0x00` as presumptive (embedded convention, lower overhead) | |

**User's choice:** Neutral evidence-driven
**Notes:** COBS stays genuinely in contention; the decision is made on merit.

### Follow-up: Criteria weighting

| Option | Description | Selected |
|--------|-------------|----------|
| Safety / fewest moving parts | Prioritize ruling out the bus-aliasing risk class | |
| Provable byte-exactness | Prioritize whichever is easiest to prove correct end-to-end | |
| Implementation simplicity | Prioritize smallest auditable dual-repo diff | |
| Let the evidence rank them | Score all criteria; aggregate ranking decides; present the matrix | ✓ |

**User's choice:** Let the evidence rank them
**Notes:** No single pre-weighted criterion. Score safety, provability, simplicity, and
overhead; the aggregate ranking picks the winner.

---

## SAFE-01 Proof Rigor

| Option | Description | Selected |
|--------|-------------|----------|
| Code/architectural proof | Static proof from `serial_comm.py` + `com_mode` gate + transition sequence; non-hardware Phase 49 | ✓ |
| Code proof + Phase 53 bench confirm | Static proof binding now; bench-confirmation obligation handed to Phase 53 | |
| Bench proof required in Phase 49 | Phase 49 itself includes an operator-authorized bench test (hardware-gated) | |

**User's choice:** Code/architectural proof
**Notes:** SAFE-01 resolved entirely within Phase 49, no hardware step.

### Follow-up: Inconclusive proof outcome

| Option | Description | Selected |
|--------|-------------|----------|
| Inconclusive → SLIP wins | Unprovable COBS guarantee is decisive evidence; SLIP selected (per §5 Q2); decision stays in Phase 49 | ✓ |
| Inconclusive → escalate to bench | Escalate that one question to an operator bench test rather than defaulting to SLIP | |
| Proof is just one input | Lowers COBS's provability score but doesn't auto-decide; matrix still picks | |

**User's choice:** Inconclusive → SLIP wins
**Notes:** Decisive fallback rule consistent with COBS-DECISION §5 Q2 ("if the proof is
unavailable, SLIP is the safer choice"). No escalation, no blocking.

---

## Decision Artifact

| Option | Description | Selected |
|--------|-------------|----------|
| New v1.10 ADR, cross-linked | New standalone `.planning/v1.10-FRAMING-DECISION.md`; cross-refs v1.9 doc; v1.9 survey stays immutable | ✓ |
| Extend the existing doc | Append v1.10 section to `v1.9-COBS-DECISION.md` in place | |
| Phase CONTEXT/PLAN only | No separate ADR; decision lives in phase artifacts | |

**User's choice:** New v1.10 ADR, cross-linked
**Notes:** Clean milestone separation. Proposed filename `.planning/v1.10-FRAMING-DECISION.md`
(planner may finalize). Supersedes the v1.9 doc's DEFER line for the mechanism question.

---

## Contract Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Full frame contract | Lock delimiter, escape/run-length scheme, exact frame layout, CRC8 placement, + per-file change map | ✓ |
| Mechanism + delimiter + CRC placement | Lock mechanism/delimiter/CRC placement; finer encoding to Phase 50 | |
| Mechanism + delimiter only | Lock just mechanism + delimiter; rest is Phase 50 research | |

**User's choice:** Full frame contract
**Notes:** Phases 50–52 implement against a frozen spec. Per-file map covers
`rurp_serial_utils.cpp`, `serial_comm.py`, `frame_parser.py`, `test_messages`.

---

## Claude's Discretion

- Exact ADR filename and section structure (within the cross-link + immutability constraints).
- The specific scoring scale / matrix presentation format (as long as all four criteria are
  scored and the aggregate ranking is shown).

## Deferred Ideas

- Hardware/bench confirmation of the SAFE-01 timing guarantee — not in Phase 49 (rides Phase 53 if wanted).
- Implementing the chosen framing — Phases 50 (data path) / 51 (command channel).
- `serial-cobs-resync-data-path.md` todo — reviewed, not folded; re-pointed to Phase 50 (commit `70fc917`).
