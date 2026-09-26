# Phase 83: UV-EPROM Write Proof (gated on Phase 81 blank-state) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-24
**Phase:** 83-uv-eprom-write-proof-gated-on-phase-81-blank-state
**Areas discussed:** 2516 read-stability gate, Spend-vs-preserve lean, Write-proof method, 2516 VPE-rail PASS bar

---

## 2516 read-stability gate (the blocking conflict)

| Option | Description | Selected |
|--------|-------------|----------|
| Bench-attempt stabilize, then branch | Attempt to stabilize the 2516 read at the bench (reseat + reset + VPP correction); proceed if N≥3 byte-identical, else defer GRAD-03 to Phase 84 | |
| Defer 2516 entirely to Phase 84 | Keep Phase 83 to the 2 stable UV chips; leave GRAD-03/FUT-03 open until Phase 84 FIX-01 fixes the 0x0B VPP instability | ✓ |
| Blank-check-only write attempt | Trust the deterministic NOT-BLANK blank-check, write anyway, accept unverifiable read-back | |

**User's choice:** Defer 2516 entirely to Phase 84
**Notes:** Protects the irreplaceable 2516; avoids a vacuous PASS on an untrusted read path. GRAD-03 / SC#4 / FUT-03 move to Phase 84 (still within v1.15, as Phase 84 is the last phase).

---

## Spend-vs-preserve lean

| Option | Description | Selected |
|--------|-------------|----------|
| Spend to prove, preserve 2516 | Lean toward spending the 2 commodity UV parts for real write proofs; preserve/defer the irreplaceable 2516 | ✓ |
| Preserve all unless operator says spend | Default preserve; record read+decode only; write conditional/may be empty | |
| Operator decides each, no default | Lock only the decision protocol, no planner pre-bias | |

**User's choice:** Spend to prove, preserve 2516
**Notes:** ST M27C512 (blank) → full image; AM27C020 (not-blank) → all-0x00. Operator keeps the explicit per-chip spend call live at the bench (UV-02); the lean is a planner pre-bias.

---

## Write-proof method per blank-state

| Option | Description | Selected |
|--------|-------------|----------|
| All-0x00 full wipe + read-back SHA | Write all-0x00 over the chip (every 1→0), verify SHA == SHA(all-0x00) | ✓ |
| AND-mask subset + masked-image verify | Partial AND-mask preserving some bits, verify against computed masked image | |
| Planner's discretion per chip | Lock the 1→0 + read-back-SHA principle, let planner pick per chip | |

**User's choice:** All-0x00 full wipe + read-back SHA (for the not-blank AM27C020)
**Notes:** Simplest, exercises every cell, unambiguous; read path trusted so verify is valid. ST M27C512 (blank) uses a full deterministic image per UV-03 (not all-0x00).

---

## 2516 VPE-rail write-proof PASS bar (Phase 84 inherits)

| Option | Description | Selected |
|--------|-------------|----------|
| Read-back SHA match = PASS, warn documented | Clean read-back SHA match counts as PASS; under-voltage warning captured verbatim; best-effort; over-voltage stays blocked | ✓ |
| SHA match + explicit best-effort caveat | Same bar, FUT-03 marked "closed best-effort (under 25V)" | |
| Defer PASS-bar definition to bench reality | Record whatever the bench produces, operator judges | |

**User's choice:** Read-back SHA match = PASS, warn documented
**Notes:** Recorded as the PASS bar Phase 84 will apply when it picks up the 2516 (since the 2516 is deferred per the gate decision). Best-effort per v1.14 D-07 (~22.4V VPE vs 25V spec). Closes FUT-03 if achieved in Phase 84.

---

## Claude's Discretion

- Exact pseudo-random image seed for ST M27C512 + storage (carry Phase 82 D-04; `gen_test_image.py`).
- `dev write-cycle` vs `write_test.sh` as the proof driver.
- Per-chip vs single shared negative control.
- Whether to re-confirm Phase 81 blank-state with a fresh read before the spend.

## Deferred Ideas

- The entire 2516 write proof (GRAD-03), VPE-rail bench proof (SC#4), FUT-03 close → Phase 84.
- 0x0B read-path VPP-instability RCA → Phase 84 FIX-01.
- Consolidated decode audit + defect RCA + evidence consolidation → Phase 84.
- Reviewed-not-folded todos: skip-vpp-on-reads (Phase 84 FIX-01), flash4-page-size (Phase 84), avrdude-fallback, cobs-deadline (unrelated).
