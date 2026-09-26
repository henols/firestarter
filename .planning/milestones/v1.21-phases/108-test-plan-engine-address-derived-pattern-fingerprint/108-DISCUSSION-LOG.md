# Phase 108: Test-Plan Engine + Address-Derived Pattern + Fingerprint - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-02
**Phase:** 108-test-plan-engine-address-derived-pattern-fingerprint
**Areas discussed:** Address-pattern formula, Fingerprint thresholds, N≥2 / marginal policy, error_code seam shape

---

## Address-pattern formula (PATT-01)

| Option | Description | Selected |
|--------|-------------|----------|
| XOR-fold of address bytes | `byte = (addr ^ (addr>>8) ^ (addr>>16) ^ (addr>>24)) & 0xFF`. Every address line contributes; stuck/aliased high line → systematically wrong bytes. Deterministic, reproducible. | ✓ |
| LFSR/PRNG keyed on address | Higher entropy but harder to map bit-flip → address line during fingerprinting; overkill for line faults. | |
| Address low-byte | `byte = addr & 0xFF`. Blind above A7 — the very lines the tool exists to catch. | |

**User's choice:** XOR-fold of address bytes.
**Notes:** Literally the "folding high bits in" behavior PATT-01 mandates; chosen for reproducibility and clean bit-flip→line mapping.

---

## Fingerprint thresholds / classifier honesty (PATT-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit `indeterminate` bucket + reuse consistency math | Four outcomes (blank/contact, address-line, transport, indeterminate); reuse `consistency_check_eprom` divergence math for the transport signal. | ✓ |
| Force-classify into the three | Always pick closest signature, no fallback. Cleaner report, risks over-confident mislabels. | |

**User's choice:** Explicit `indeterminate` bucket + reuse consistency math.
**Notes:** Grounded in the project's false-PASS history (Bug A, ST-vs-Winbond, AM27C020). Exact numeric thresholds left to planner/researcher; the honest-fallback contract is the locked part.

---

## N≥2 / marginal policy (SWEEP-04)

| Option | Description | Selected |
|--------|-------------|----------|
| N=2 default, configurable ≥2; marginal on destructive/verify only | Mirror `consistency_check_eprom(runs=, min 2)`; read disagreement = byte-level divergence. | ✓ |
| Hard-fixed N=2, marginal on any repeated step | No runs knob; simpler surface, loses escalate-to-N-runs on flaky boards. | |

**User's choice:** N=2 default, configurable ≥2; marginal on destructive/verify only.
**Notes:** Preserves the escalate-runs option for uno328pb-class instability.

---

## error_code seam shape (RPT-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Optional `__init__` kwarg storing `self.error_code` | `EpromOperationError(*args, error_code=None)`; existing raise sites untouched, new sites pass `response.id`. | ✓ |
| Settable attribute after construction | `e.error_code = response.id` at raise sites; every site must remember, readers need getattr defaults. | |

**User's choice:** Optional `__init__` kwarg storing `self.error_code`.
**Notes:** Backward-compatible by construction; single obvious access path.

---

## Claude's Discretion

- `derive_plan()` return type and per-step result record shapes (constrained by the locked verdict vocabulary + fingerprint outcomes).
- Exact numeric thresholds inside the fingerprint classifier.
- Internal module/helper decomposition within `chip_test.py`.

## Deferred Ideas

None — discussion stayed within phase scope. Adjacent concerns are owned by Phases 109–114.
