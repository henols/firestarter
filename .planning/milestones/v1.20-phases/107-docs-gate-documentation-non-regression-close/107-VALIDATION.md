---
phase: 107
slug: docs-gate-documentation-non-regression-close
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-02
---

# Phase 107 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> This is a DOCS + GATE close phase: nearly all "validation" is re-running the
> existing non-regression gate suite (GATE-01/02, SAFE-01). The only code/codegen
> change is the D-06 0xAE removal, verified by the codegen drift gate + suites.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | firmware: PlatformIO/Unity native; host: pytest 7.x + ruff + mypy |
| **Config file** | `firestarter/platformio.ini`; `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter && pio test -e native` |
| **Full suite command** | `cd firestarter && pio test -e native` && `cd firestarter_app && pytest` |
| **Estimated runtime** | ~60–120 seconds |

---

## Sampling Rate

- **After every task commit:** Run the gate touched by that task (e.g. `check_dispatch.py`, or `pio test -e native` after the 0xAE regen).
- **After every plan wave:** Run the full gate sweep.
- **Before close:** Full gate sweep must be green *modulo the documented pre-existing baseline* (D-07).
- **Max feedback latency:** ~120 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 107-01-xx | 01 | 1 | DOC-01 | — | Docs carry no `type`/`mem_type` wire refs; v1.20 Breaking Changes recorded | grep/source assertion | `grep -rIn "mem_type\|\"type\"" firestarter/CLAUDE.md firestarter/doc/PROTOCOLS.md firestarter_app/CLAUDE.md` returns only preserved `electrical.type` | ✅ | ⬜ pending |
| 107-02-xx | 02 | 1 | DOC-01 (D-06) | — | 0xAE removed from canonical toml; codegen regen clean | codegen drift gate | `cd firestarter_app && python tools/catalog/codegen.py --check` (0 drift) + `pytest` messages tests | ✅ | ⬜ pending |
| 107-03-xx | 03 | 2 | GATE-01, GATE-02, SAFE-01 | over-voltage VPP | All gates green; no NEW regression vs beta; over-voltage stays blocked; every DB chip routes via protocol | integration/gate sweep | `pio test -e native` (native+golden+dispatch-mirror), `check_dispatch.py` (0), `diff_db.py` (no real-chip change), host `pytest`+ruff+mypy scoped to `git diff beta..HEAD` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Plan/task IDs above are indicative — final IDs set by the planner.*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. No new test framework or fixtures needed — this phase re-runs the established native + host + codegen gates.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| None | — | All close-gate behaviors have automated verification (native suite, check_dispatch, diff_db, codegen drift, host pytest). No hardware/bench needed for this phase. | — |

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (none)
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
