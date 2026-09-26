# Phase 108: Test-Plan Engine + Address-Derived Pattern + Fingerprint - Context

**Gathered:** 2026-07-02
**Status:** Ready for planning

<domain>
## Phase Boundary

A new `chip_test.py` **test-plan engine** that, given any chip in the database
(including chips the maintainer has never physically touched), can:

1. **Derive** the exact op list that chip's protocol supports — strictly from the
   frozen DB fields `protocol` / `electrical.type` / `FLAG_CAN_ERASE`, never
   re-invoking build-time `classify()`, and bypassing the `resolve_chip`
   support-status guard for **plan derivation only** (via `get_eprom()` /
   `convert_to_programmer()`).
2. Run each op (id, read, write, verify, erase, blank-check) as an **independent,
   non-fatal step** with a `OK`/`BAD`/`NA`/`SKIPPED` verdict; one step's failure
   never aborts the rest (the W29C040 locked-boot-block lesson).
3. Run **id-first**; a chip-ID mismatch **hard-gates** all destructive steps shut
   for that run (chip left pristine) while still recording id/read findings.
4. Run destructive/verify steps **N≥2** and report `marginal` on disagreement.
5. Generate an **address-derived** write/verify pattern (byte = f(address)) preceded
   by a cheap all-0x00/all-0xFF pre-pass, coupled with a **byte-mismatch fingerprint
   classifier** (blank/contact vs address-line vs transport vs indeterminate).
6. Add the `EpromOperationError.error_code` seam preserving the firmware `response.id`.

**Engine-only this phase.** The `@dev.command("test")` CLI handler is **Phase 112**;
the `--destructive` gate / small-region cap / CI orchestrator-only check are **Phase
109**; the report model is **Phase 110**; the voltage sampler is **Phase 111**. This
phase must be fully **unit-testable without a bench** (mock operator + `EpromDatabase(skip_local_override=True)`).
</domain>

<decisions>
## Implementation Decisions

### Address-derived pattern (PATT-01)
- **D-01:** The generator is an **XOR-fold of the address bytes**:
  `byte = (addr ^ (addr >> 8) ^ (addr >> 16) ^ (addr >> 24)) & 0xFF`.
  Every address line contributes to the expected byte, so a stuck/shorted/aliased
  high address line (A8+) produces systematically wrong bytes at the aliased
  addresses — this is the "folding high bits in" the requirement mandates.
  Deterministic and reproducible across runs (no RNG state). Rejected: address
  low-byte only (blind above A7), and an address-keyed LFSR/PRNG (harder to map a
  bit-flip back to an address line during fingerprinting, overkill for line faults).
- **D-02:** The pattern is preceded by a **cheap all-0x00/all-0xFF pre-pass** (PATT-01).
  The pattern generator must be **region-parameterized** (start/length) — it does NOT
  assume a full-chip write — because Phase 109 will cap the UV-EPROM write to a small
  high-address contiguous window. Do not bake full-chip assumptions into the generator.

### Fingerprint classifier (PATT-02)
- **D-03:** The classifier emits **four** outcomes, not three:
  `blank/contact`, `address-line`, `transport`, and an explicit **`indeterminate`**
  bucket that fires when no signature dominates. Never force an ambiguous distribution
  into one of the three confident labels — this project's false-PASS history (Rev-0
  shield Bug A, ST-vs-Winbond chip-ID mixup, AM27C020 write#1 60/64 vs write#2 0/64)
  proves over-confident classification mis-diagnoses.
- **D-04:** Signature direction (from the design note): all/near-all `0xFF` →
  blank/contact; mismatches clustered in high address bits / power-of-two aliasing →
  address-line; scattered/non-repeatable → transport. **Reuse
  `consistency_check_eprom`'s divergence math** (eprom_operations.py:671) for the
  transport/scatter signal — do NOT write a parallel divergence implementation.
  Exact numeric thresholds are a planner/researcher detail; the honest-fallback
  contract (D-03) is the locked part.

### N≥2 / marginal policy (SWEEP-04)
- **D-05:** Default **N=2**, overridable via a `runs` parameter that **mirrors
  `consistency_check_eprom(runs=…)`** (minimum 2, reject `<2` before any state-machine
  call — same guard as the existing method). Keeps the escalate-to-more-runs option for
  flaky boards (uno328pb).
- **D-06:** `marginal` applies to **destructive/verify steps only** (per spec) — not
  every repeated step. Read-step disagreement is measured as **byte-level divergence**
  (reuse the consistency divergence math), not a verdict flip.

### error_code seam (RPT-03)
- **D-07:** Add an **optional `__init__` kwarg** to `EpromOperationError`:
  `EpromOperationError(*args, error_code=None)` storing `self.error_code`. Existing
  `raise EpromOperationError("…")` sites keep working untouched (kwarg defaults `None`);
  new raise sites pass the firmware `response.id` byte. Backward-compatible by
  construction, single obvious access path. Rejected: set-attribute-after-construction
  (every site must remember to set it; readers need `getattr` defaults; easy to miss a site).

### Claude's Discretion
- Result/plan object shapes (`derive_plan()` return type, per-step result records) —
  planner's call, constrained by the verdict vocabulary (`OK`/`BAD`/`NA`/`SKIPPED`,
  plus `marginal`) and the fingerprint outcomes above.
- Exact numeric thresholds inside the fingerprint classifier (D-04).
- Module layout / helper decomposition within `chip_test.py`.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & scope (this phase)
- `.planning/ROADMAP.md` — Phase 108 section (goal, depends-on, 6 success criteria) + dependency spine
- `.planning/REQUIREMENTS.md` — SWEEP-01/02/03/04, PATT-01/02, RPT-03

### Design intent (the "why" — decisive, read before planning)
- `.planning/notes/dev-test-design-decisions.md` — test-plan model, technology-aware
  destructiveness, two-tier diagnostic contract (auto-captured vs must-ask), the
  fingerprint field semantics this phase's classifier feeds
- `.planning/seeds/community-chip-validation-command.md` — original `/gsd-explore` seed
- `.planning/research/SUMMARY.md` — HIGH-confidence 4-stream research; the two resolved
  open questions (address-derived-not-fixed pattern; FLAG-only/no-auto-graduate)

### Reusable code (firestarter_app/)
- `firestarter/eprom_operations.py:671` — `consistency_check_eprom` (divergence math to
  reuse for the fingerprint + the `runs` param / `runs<2` guard to mirror for SWEEP-04)
- `firestarter/eprom_operations.py:1555/1592/1695` — `write_eprom` / `verify_eprom` /
  `check_eprom_id` service methods the steps call
- `firestarter/exceptions.py:37` — `EpromOperationError` (the `error_code` seam target)
- `firestarter/chip_resolver.py:16` — `resolve_chip` (support-status guard the plan
  derivation bypasses; execution steps still route through it)
- `firestarter/database.py:506/535` — `get_eprom` / `convert_to_programmer` (plan-derivation
  path that bypasses the support-status guard)
- `firestarter/cli_handlers.py:1474` — `dev_validate_family` (sibling handler + the
  `EpromDatabase(skip_local_override=True)` + mock-operator unit-test seam to copy)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `consistency_check_eprom` (eprom_operations.py:671): 3-way int verdict
  (0 PASS / 1 diverge / 2 hw-error), N-run divergence via SHA-256, `runs<2` reject
  guard, quiet-mode callback swap. Directly reused for the fingerprint transport signal
  and the N≥2 marginal policy — do not duplicate the read path.
- `EpromOperator` service methods (`check_eprom_id`, `read_eprom`, `write_eprom`,
  `verify_eprom`, `erase_eprom`, `check_eprom_blank`) — the per-op steps call these; the
  engine adds no new firmware dispatch and sets no VPP itself.
- `EpromDatabase(skip_local_override=True)` + mock operator — the `validate-family` test
  seam; keeps this engine fully unit-testable without a bench.

### Established Patterns
- `EpromOperationError` is today a bare `pass` subclass of `Exception` — adding an
  optional `error_code` kwarg is non-breaking.
- Sibling `@dev.command` handlers already exist (read/reg/addr/consistency-check/
  write-cycle/validate-family @ cli_handlers.py) — Phase 112 will add `test` alongside them.
- `check_eprom_id` already returns `Tuple[bool, Optional[int]]`, precedent for
  non-bool verdicts.

### Integration Points
- Plan **derivation** reads DB via `get_eprom`/`convert_to_programmer` (bypasses
  `resolve_chip` support-status guard); plan **execution** routes every op through
  `resolve_chip` + the existing serial/operator path (Phase 109 CI-enforces this).
- `error_code` seam is consumed by the Phase 110 report (per-step exact firmware code).
- The address-derived pattern generator must accept a region (start/length) so Phase 109
  can cap the UV write window without touching this generator.
</code_context>

<specifics>
## Specific Ideas

- Fault-detection framing is grounded in this project's real RCAs: Bug A (Rev-0 shield
  address/read-path), ST-vs-Winbond 512 chip-ID mixup, AM27C020 VPP-droop write
  non-repeatability, uno328pb transport instability. The pattern (D-01) and the
  honest-`indeterminate` classifier (D-03) exist specifically to surface those classes
  of fault rather than hide them.
</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (Downstream phases already own the adjacent
concerns: `--destructive` gate + UV small-region cap + orchestrator-only CI = Phase 109;
report model + provenance prompts = Phase 110; measured-voltage sampler = Phase 111;
CLI handler = Phase 112; submission = Phase 113; disposition/no-auto-graduate lock = Phase 114.)

</deferred>

---

*Phase: 108-Test-Plan Engine + Address-Derived Pattern + Fingerprint*
*Context gathered: 2026-07-02*
