---
phase: 110
slug: diagnostic-report-model-dual-output-provenance-prompts
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-02
---

# Phase 110 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (firestarter_app/) |
| **Config file** | firestarter_app/pyproject.toml (`[tool.pytest]`) |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/ -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest tests/ --cov=firestarter` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -q`
- **After every plan wave:** Run the full suite command
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 110-01-01 | 01 | 1 | RPT-01 | — | one source object → rich table + fenced JSON w/ schema_version, no dup logic | unit | `python -m pytest tests/ -q` | ❌ W0 | ⬜ pending |
| 110-01-02 | 01 | 1 | RPT-02 | — | auto-capture fields present from composed Phase-108/109 objects + injected identity | unit | `python -m pytest tests/ -q` | ❌ W0 | ⬜ pending |
| 110-02-01 | 02 | 1 | RPT-04 | — | provenance prompted via injectable seam; "not sure" submittable; blank ⇒ not submittable | unit | `python -m pytest tests/ -q` | ❌ W0 | ⬜ pending |
| 110-02-02 | 02 | 1 | RPT-05 | — | DB-diff shows current support_status + advisory proposal; NO support_status write | unit + grep/AST | `python -m pytest tests/ -q` | ❌ W0 | ⬜ pending |
| 110-01-03 | 01 | 1 | XPORT-01 | — | transport-health renders "not measured" (never 0); transport-suspect never trips on absent counters | unit | `python -m pytest tests/ -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_diagnostic_report.py` — stubs for RPT-01/02/05, XPORT-01 (dual-render, auto-capture, DB-diff, transport "not measured")
- [ ] `tests/test_provenance.py` — stubs for RPT-04 (injectable prompt seam, `is_submittable`, "not sure" = filled)
- [ ] Existing `tests/` fixtures cover `EpromDatabase(skip_local_override=True)` + mock-operator seam (from `dev validate-family`) — reuse, do not re-create

*Existing pytest infrastructure covers the framework; only the two new test files are needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| (none) | — | This phase is host-only + bench-free; all behaviors are unit-testable via the mock-operator seam | — |

*All phase behaviors have automated verification. (Real transport-counter capture is deferred — research confirmed no counters exist today, so XPORT-01's "not measured" path is the tested behavior, not a live-bench measurement.)*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
