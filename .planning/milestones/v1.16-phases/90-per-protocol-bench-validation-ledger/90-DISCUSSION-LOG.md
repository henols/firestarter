# Phase 90: Per-Protocol Bench Validation + Ledger - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-26
**Phase:** 90-per-protocol-bench-validation-ledger
**Areas discussed:** PASS bar / regression, Ledger composition, Firmware + bench mechanics, UNVERIFIED + defect rows

---

## PASS bar / regression (Area A)

| Option | Description | Selected |
|--------|-------------|----------|
| Regression-match v1.15 SHA | Re-run each chip's v1.15 op on rebuilt fw; PASS = byte-identical result (same read SHA / write verdict) as v1.15 baseline | ✓ |
| Standalone clean op | PASS = op completes cleanly under rebuilt fw, no SHA comparison | |
| Match-where-stable | Regression-match where clean baseline exists; standalone where v1.15 was anomalous | |

**User's choice:** Regression-match v1.15 SHA
**Notes:** Grounded in EVIDENCE.json — all 4 on-hand chips (W29C020, SST39SF040, W27C512, FM1608) have clean v1.15 PASS baselines, so no match-where-stable fallback needed.

### Op scope follow-up

| Option | Description | Selected |
|--------|-------------|----------|
| Write-cycle + read, both | Re-run BOTH non-destructive read (SHA) AND write-cycle A→B per chip; write-cycle exercises the recomposed VPP/chip-id/poll primitives | ✓ |
| Write-cycle only | Just A→B per chip | |
| Read only | Read-SHA regression only; does not exercise recomposed write primitives | |

**User's choice:** Write-cycle + read, both
**Notes:** The Phase-89 recompose changed the write-path primitives; a read-only test would not touch the changed code.

### N + mismatch follow-up

| Option | Description | Selected |
|--------|-------------|----------|
| N≥3; mismatch = investigate, not PASS | ≥3 byte-identical reads; any SHA diff vs v1.15 = FAIL/INVESTIGATE, never auto-passed; reseat+retry first | ✓ |
| N≥2; mismatch = investigate | Two identical reads suffice; same mismatch rule | |
| You decide | Planner picks N | |

**User's choice:** N≥3; mismatch = investigate, not PASS

---

## Ledger composition (Area B)

| Option | Description | Selected |
|--------|-------------|----------|
| Cross-reference by ID | Ledger rows reference EVIDENCE cells (by chip) + v1.13 matrix (by family id); no data copied; upstream stays source of truth | ✓ |
| Embed snapshot subset | Copy SHA/verdict/flash fields into ledger; self-contained but drift risk | |
| You decide schema | Lock only the compose principle; planner proposes JSON shape | |

**User's choice:** Cross-reference by ID
**Notes:** Exact JSON field names/ordering left to planner within the compose-don't-replace principle.

---

## Firmware + bench mechanics (Area C)

| Option | Description | Selected |
|--------|-------------|----------|
| Claude drives, operator gates | Claude flashes final recomposed fw + runs ops over USB passthrough; operator confirms Rev 2.0 + port identity + authorizes each silicon op; gitlinks PINNED b10, no lockstep | ✓ |
| Hybrid: reads auto, writes gated | Reads Claude-driven unattended; writes operator-confirmed live | |
| Operator runs all ops | Operator executes everything; Claude only authors ledger from pasted results | |

**User's choice:** Claude drives, operator gates
**Notes:** Matches the v1.15 bench workflow. Leonardo is exempt from chip-out-before-sideload (Uno-class only), but operator still authorizes each flash.

---

## UNVERIFIED + defect rows (Area D)

| Option | Description | Selected |
|--------|-------------|----------|
| Full rows; defects status-only | UNVERIFIED buckets get complete rows (name, datasheet-rep cite, primitives, flash delta) + reason='no on-hand silicon'; 3 defect rows reproduce documented status verbatim + source link | ✓ |
| Minimal UNVERIFIED rows | hex + name + status + reason only; defect rows = pointer to deferred table | |
| You decide | Full where useful, minimal where redundant | |

**User's choice:** Full rows; defects status-only
**Notes:** Keeps the ledger a standalone 12-bucket v1.16 picture; no re-litigation of CR-01 / FUT-06 / FUT-03.

---

## Claude's Discretion

- Exact `PROTOCOL-LEDGER.json` field names, row ordering, and `.md` table layout (within D-04).
- Bench evidence artifact storage layout/paths (consistent with `.planning/v1.15/bench/`).
- Exact read-harness invocation for the N≥3 cells (e.g. `firestarter dev consistency-check`).

## Deferred Ideas

- Fixing the 3 open defects (W29C040/CR-01, AM27C020/FUT-06, 2516/FUT-03) — carried status-only.
- 0x34 X88C64 programming handler — PCB-blocked (FUT-01).
- Acquiring silicon for the 6 no-silicon buckets — future milestone.
- Lockstep beta cut `3.0.0b11` + gitlink bump — operator-gated, not this phase.
