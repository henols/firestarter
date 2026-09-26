---
phase: 90
slug: per-protocol-bench-validation-ledger
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-26
---

# Phase 90 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> This phase's deliverable is a **ledger document + bench evidence**, not source code.
> The planner fills the per-task map; the Validation Architecture section of 90-RESEARCH.md
> is the authoritative source for the observable contract per requirement.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (host gates) + a Wave-0 ledger self-consistency checker (new) + manual bench (hardware) |
| **Config file** | `firestarter_app/pyproject.toml` (validate against CI **py3.11**, NOT devcontainer py3.12) |
| **Quick run command** | `python -m json.tool .planning/v1.16/ledger/PROTOCOL-LEDGER.json >/dev/null` (JSON well-formed) |
| **Full suite command** | ledger self-consistency checker (all 12 buckets present, PASS rows carry `oracle`+evidence refs, cross-refs resolve into EVIDENCE.json/validation_matrix_spec.json) |
| **Estimated runtime** | ~5 s (doc/JSON checks); bench ops are manual + operator-gated |

---

## Sampling Rate

- **After every task commit:** Run the quick JSON well-formedness check on PROTOCOL-LEDGER.json.
- **After every plan wave:** Run the ledger self-consistency checker.
- **Before `/gsd-verify-work`:** Self-consistency checker green; all bench PASS rows have non-empty evidence references and `oracle: leonardo+Rev2.0`.
- **Max feedback latency:** ~5 s for doc/JSON gates (bench latency is operator-paced, out of the automated loop).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 90-01-01 | 01 | 1 | LEDGER-01 | — | PROTOCOL-LEDGER.{md,json} exists with one row per all 12 buckets; cross-refs (chip→EVIDENCE.json, family→validation_matrix_spec.json) resolve; no SHA/verdict data duplicated | unit | ledger self-consistency checker | ❌ W0 | ⬜ pending |
| 90-02-01 | 02 | 2 | LEDGER-02 | — | Each on-hand bucket PASS row carries `oracle: leonardo+Rev2.0` + non-empty evidence refs; regression SHA == v1.15 baseline (read N≥3 + write-cycle A→B) | manual+unit | structural PASS-field assert + bench evidence | ❌ W0 | ⬜ pending |
| 90-03-01 | 03 | 2 | LEDGER-03 | — | 6 no-silicon buckets = `UNVERIFIED` (full rows w/ datasheet-rep cite + primitives); 3 defect rows reproduce documented status verbatim | unit | self-consistency checker enum + defect-row text match | ❌ W0 | ⬜ pending |
| 90-04-01 | 02 | 2 | SAFE-04 | — | firmware over-voltage VPP check present+unmodified (primitives.cpp vpp_check_window); `chip_resolver.resolve_chip` guard never bypassed; 2516 stays UNVERIFIED | unit | grep assertions on primitives.cpp + chip_resolver.py; 2516 status check | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Task IDs are planner-provisional — the planner sets the real wave/plan split.*

---

## Wave 0 Requirements

- [ ] Ledger self-consistency checker (new tool/script) — asserts all 12 buckets present, PASS-field structural constraint (oracle + evidence refs), cross-reference keys resolve into EVIDENCE.json (`cell.chip`) and validation_matrix_spec.json (`family.id` / decimal protocol membership), verification_status enum valid.
- [ ] No new framework install — pytest + json tooling already present (SAFE-05: zero new deps).

*Existing host test infrastructure covers the SAFE-04 grep assertions.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Bench regression-match per on-hand chip (read N≥3 SHA + write-cycle A→B SHA == v1.15 baseline) on recomposed firmware | LEDGER-02 | Requires physical Leonardo + RURP Rev 2.0 + the 4 chips; operator-gated silicon ops | Flash recomposed fw (submodule a296195); per chip run READ first (N≥3) then write-cycle A→B (gen_test_image seeds 1/2; FM1608 via `write -b`); compare SHA-256 to hard-coded v1.15 targets; mismatch = FAIL/INVESTIGATE |
| Over-voltage stays physically blocked during all bench sessions | SAFE-04 | Hardware behavior under live VPP | Operator confirms no over-voltage event; firmware VPP check fires as designed |

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` verify (ledger checker / grep) or a documented Manual-Only entry with operator instructions
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (bench tasks pair with the automated ledger/structural checks)
- [ ] Wave 0 covers the ledger self-consistency checker before any ledger rows are authored
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s for automated gates
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
