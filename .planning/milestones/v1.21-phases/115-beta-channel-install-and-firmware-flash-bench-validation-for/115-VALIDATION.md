---
phase: 115
slug: beta-channel-install-and-firmware-flash-bench-validation-for
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-10
---

# Phase 115 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> **Note:** This is a VALIDATION + DOCS close phase. Most of its acceptance is
> hardware-witnessed (per-board flash + smoke) and release-engineering
> (CI dispatch / channel-reachability), not unit tests. The automated surface is
> limited to any doc/link lint + not regressing the existing `firestarter_app`
> suite; the load-bearing verifications are manual/hardware. The planner refines
> the per-task map below.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (firestarter_app) |
| **Config file** | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `cd firestarter_app && python -m pytest -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest` |
| **Estimated runtime** | ~30–60 seconds |

*Toolchain caveat (memory `reference_firestarter_app_python_test_env`): use `/usr/local` python; restore via `pip install -e '.[test]'`; ignore foreign `.venv/`. Known pre-existing REDs on a bench session: `test_audit_coverage_matrix` golden + the two `no_programmer_found` characterization tests when a live board is attached — NOT this phase's regressions.*

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && python -m pytest -q` (only where the task touches Python; doc/CI/bench tasks have no unit surface)
- **After every plan wave:** Run the full suite
- **Before `/gsd-verify-work`:** Full suite green (modulo the documented pre-existing REDs)
- **Max feedback latency:** ~60 seconds (software); hardware/CI verifications are witnessed, not sampled

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| {N}-01-01 | 01 | 1 | ONBOARD-0X | — | {expected behavior or "N/A"} | {unit / manual-hw / manual-ci} | `{command or "manual"}` | ✅ / ❌ W0 | ⬜ pending |

*Planner expands this map from the authored plans. Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers the (limited) automated surface. No new test framework needed — the phase's verifications are predominantly manual/hardware + CI-reachability. Any doc-link or command-block lint the planner adds is captured per-task.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Both channels publicly reachable (PyPI `--pre` + GitHub prerelease `.hex` per board) | ONBOARD-01/02 (Step 0) | Requires live external services (PyPI index + GitHub releases API) + irreversible operator-authorized publish | `pip index versions firestarter --pre` shows `3.0.0b11`; the firmware GitHub prerelease exposes `firestarter_{uno,uno328pb,leonardo}.hex` |
| Fresh-venv `--pre` install reports `3.0.0b11` per board | ONBOARD-01 | Needs a throwaway venv + real network install | See RESEARCH.md fresh-venv recipe; `firestarter --version` == `3.0.0b11` |
| Bare `fw -i` auto-routes to `--pre`, downloads board `.hex`, avrdude flash+verify | ONBOARD-02 | Requires the physical board over USB passthrough | Per-board; avrdude reports flash + verify OK |
| Post-flash smoke: `fw` reports beta version+board + one live `hw`/identify op | ONBOARD-03 | Requires the flashed physical board (no chip seated) | `firestarter fw`; `firestarter hw` |
| Community onboarding doc is complete + accurate for a stranger | ONBOARD-04 | Prose/UX quality is human-judged | Review `firestarter_app/doc/beta-testing-install.md` against the ONBOARD-04 checklist |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify OR are explicitly classified manual-hw / manual-ci with instructions
- [ ] Sampling continuity: software tasks sampled after commit; hardware/CI tasks witnessed
- [ ] Wave 0 covers all MISSING references (none expected)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s (software)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
