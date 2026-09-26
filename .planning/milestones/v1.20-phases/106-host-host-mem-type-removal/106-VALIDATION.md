---
phase: 106
slug: host-host-mem-type-removal
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-02
---

# Phase 106 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/test_chip_resolver.py tests/test_val_wire_*.py -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command
- **After every plan wave:** Run full suite command
- **Before `/gsd-verify-work`:** Full suite must be green (plus py3.11-target `ruff check` + `ruff format --check` + `mypy`)
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | — | — | HOST-01..04 | — | N/A | unit | `cd firestarter_app && python -m pytest -q` | ✅ | ⬜ pending |

*Per-task rows populated by the planner. Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements — `test_chip_resolver.py`, `test_val_wire_*.py`, `test_eprom_database.py`, `test_ic_layout.py` already exist; this phase edit-and-inverts them plus adds one D-06 test.*

---

## Manual-Only Verifications

*All phase behaviors have automated verification (pure host-side cleanup; no hardware dependency — SC#1–#4 all map to pytest assertions).*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
