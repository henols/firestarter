---
phase: 102
slug: host-apply-names-in-the-host-cli-display
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-01
---

# Phase 102 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (with syrupy snapshot plugin) |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter_app && pytest tests/test_ic_layout.py -q` |
| **Full suite command** | `cd firestarter_app && pytest -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && pytest tests/test_ic_layout.py -q`
- **After every plan wave:** Run `cd firestarter_app && pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 102-01-01 | 01 | 1 | HOST-01 | — | N/A (display-only) | unit | `cd firestarter_app && pytest tests/test_ic_layout.py -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky — the planner refines this map when plans are written.*

---

## Wave 0 Requirements

- [ ] Single-source invariant test — assert the consolidated canonical map is the one source both `proto_display` and `protocol_info_data` draw from (RESEARCH.md recommendation; guards against IN-01 re-divergence).
- [ ] Regenerate the syrupy snapshot `test_info_known_chip` (`tests/__snapshots__/test_characterization.ambr`) for the new `Protocol:` line.

*Gate re-runs (GATE-01 `tools/check_dispatch.py` + `tests/test_dispatch_mirror.py`, GATE-02 `tools/diff_db.py`) are numeric/DB-level and structurally unaffected by this display-only change — re-run to confirm green.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| py3.11 CI green (ruff/mypy/pytest) | GATE-03 | Devcontainer has only python3.12; CI target is py3.11 | Apply Phase-98 CI-PENDING/structurally-green sign-off; validate `ruff check` + `ruff format --check` + `mypy` structurally, defer live py3.11 run to CI |

*All in-repo behaviors have automated verification; only the py3.11 CI target is environment-gated.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (3/3 tasks in PLAN 102-01)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (invariant + coverage tests in Task 2)
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-07-01
