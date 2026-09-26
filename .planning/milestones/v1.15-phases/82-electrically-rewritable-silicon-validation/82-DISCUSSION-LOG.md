# Phase 82: Electrically-Rewritable Silicon Validation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-24
**Phase:** 82-electrically-rewritable-silicon-validation
**Areas discussed:** W29C020 flash4 page-size risk (CR-01), Write payload / test image, Auto-erase confirmation method (REWR-04), Write-failure disposition

---

## W29C020 flash4 page-size risk (CR-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Attempt as-is → P84 if it fails | Run W29C020 write→verify on current firmware; a mid-page-poll failure is recorded FAIL with CR-01 root-cause and handed to Phase 84. Host-only, no firmware scope. | ✓ |
| Pre-fix CR-01 firmware now | Fold the datasheet-sourced page_size fix into Phase 82 before benching. Expands into dual-repo firmware change + reflash. | |
| Bench W29C040 only, flag W29C020 | Validate only the heuristic-correct W29C040, record W29C020 as expected-risk/not-exercised. | |

**User's choice:** Attempt as-is → P84 if it fails
**Notes:** Keeps Phase 82 host-only and matches the milestone ordering (validate on silicon first, RCA/fix in Phase 84). Claude surfaced the CR-01 todo as the most relevant pre-write risk: W29C020 (256KB) is under-sized by `flash4_page_size` (128 vs real 256B) — the same bug Phase 74 fixed for W29C040 (which is correct at 512KB). Plan must pre-record the risk so a failure is pre-attributed.

---

## Write payload / test image

| Option | Description | Selected |
|--------|-------------|----------|
| Full-size deterministic pseudo-random | Full-chip-size pseudo-random image (fixed seed) per chip; max address/paging coverage, non-trivial SHA, real bit transitions over non-blank contents. | ✓ |
| Bit-coverage pattern (0xAA/0x55/walking) | Structured pattern exercising each data line; easier to eyeball, less paging/address coverage. | |
| Real ROM image where available | Actual ROM dump per chip where one exists, random otherwise; realistic but inconsistent. | |

**User's choice:** Full-size deterministic pseudo-random
**Notes:** `dev write-cycle` requires an explicit SOURCE_IMAGE, so the image is a concrete per-chip artifact. Generator/seed/storage left to planner's discretion (must be full-size, reproducible, non-trivial).

---

## Auto-erase confirmation method (REWR-04 SC#3)

| Option | Description | Selected |
|--------|-------------|----------|
| SHA over non-blank; A→B for flash4 | SHA-match over non-blank P81 contents proves erase; explicit A→B only for the 2 flash4 chips. | |
| Explicit A→B rewrite for all 8 | Two-image A→B rewrite proof on every chip (write A/verify, write B no-erase/verify B). Most rigorous, ~2× write cycles, safe (rewritable). | ✓ |
| SHA over non-blank for all, no A→B | Clean write→verify SHA over non-blank contents treated as sufficient for every chip. | |

**User's choice:** Explicit A→B rewrite for all 8
**Notes:** Operator chose the most rigorous uniform protocol. For erasable chips A→B proves auto-erase; for FM1608 (FRAM, no erase) the same A→B proves clean overwrite (REWR-05's intent). Extra cycles cost nothing since all 8 are freely rewritable.

---

## Write-failure disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Reseat+retry, record, continue → P84 | Extend Phase 81 D-06/D-07: reseat+retry N=2, record FAIL/ANOMALY, continue the sweep; genuine defects flagged for Phase 84 FIX-01. | ✓ |
| Halt sweep on first FAIL | Stop the phase on the first failing chip and root-cause inline before continuing. | |

**User's choice:** Reseat+retry, record, continue → P84
**Notes:** Rewritable chips are safe to retry/re-write. Full coverage beats inline RCA; an expected W29C020 CR-01 failure (per the first decision) flows into Phase 84 via this disposition.

---

## Claude's Discretion

- Exact pseudo-random image generator, seed scheme, and storage location.
- Reseat/retry count default (N=2 baseline from Phase 81) and FAIL-vs-ANOMALY column wording.
- Driver choice: `dev write-cycle` (per-chip, explicit source — natural fit for A→B) vs `dev validate-family --source` (matrix-oriented).
- Per-chip vs single shared negative control (Phase 81 fired one; either satisfies EVID-03).
- Write/verify order across the 8 chips (all rewritable → low-stakes).

## Deferred Ideas

- CR-01 proper fix (datasheet-sourced flash4 page_size) → Phase 84 FIX-01 if the W29C020 bench failure fires.
- 3 UV-EPROM write proofs (Phase 83; 2516 read currently unstable per Phase 81).
- Consolidated decode-correctness audit + conditional defect RCA → Phase 84.
- skip-vpp-error/warning-on-reads todo (`resolves_phase: 84`) — not folded; verify-read VPP-refusal gotcha handled operationally.
- Reviewed-not-folded: `avrdude-mcu-detection-fallback`, `cobs-decoder-framelevel-deadline-wr01` (unrelated to Phase 82).
