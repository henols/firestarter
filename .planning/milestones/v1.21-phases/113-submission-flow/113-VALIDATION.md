---
phase: 113
slug: submission-flow
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-07-03
---

# Phase 113 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `113-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` + `click.testing.CliRunner` + `unittest.mock` (all present in `.[test]`) |
| **Config file** | `firestarter_app/pyproject.toml` (`.[test]` extra); CI at `firestarter_app/.github/workflows/ci.yml` |
| **Quick run command** | `pytest tests/test_submit.py -x` |
| **Full suite command** | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |
| **Estimated runtime** | ~30 seconds (full suite, estimate — unit-heavy; executor should record the observed number) |

**CI target caveat:** CI runs Python 3.11; the devcontainer runs 3.12, which masks py3.11 ruff/codegen differences. Validate `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` before claiming CI green.

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_submit.py -x` + `ruff check firestarter/ tests/`
- **After every plan wave:** Run full suite + `ruff format --check firestarter/ tests/` + `python tools/check_devtest_orchestrator.py`
- **Before `/gsd-verify-work`:** Full suite green + orchestrator gate green
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

Task/Plan/Wave IDs are assigned by the planner; rows below are the requirement→test contract lifted from RESEARCH.md and MUST each land in a plan's `<automated>` verify.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | (planner) | (planner) | SUB-01 | — | gh tier chosen when `which_fn` finds gh AND `gh auth status` exit 0; correct argv + stdin body | unit | `pytest tests/test_submit.py -k gh_tier -x` | ❌ W0 | ⬜ pending |
| TBD | (planner) | (planner) | SUB-01 | T-113-05 | browser tier when no gh / not authed; URL params correct; routes to hardcoded `henols/firestarter_app` (no remote inference) | unit | `pytest tests/test_submit.py -k browser_tier -x` | ❌ W0 | ⬜ pending |
| TBD | (planner) | (planner) | SUB-01 | T-113-03 | encoded-URL byte measure + JSON drop past ~7.5 KB, hard-stop before ~8 KB; `urllib.parse.quote` encodes all body/title | unit | `pytest tests/test_submit.py -k oversize -x` | ❌ W0 | ⬜ pending |
| TBD | (planner) | (planner) | SUB-02 | T-113-02 | each PII vector (home path, `/dev/tty*`, `COM*`, username, temp) scrubbed from free-text reason fields | unit | `pytest tests/test_submit.py -k sanitize -x` | ❌ W0 | ⬜ pending |
| TBD | (planner) | (planner) | SUB-02 | T-113-04 | off-TTY prints body + URL but does NOT open browser / run gh; on-TTY `Confirm.ask` gate before send | unit | `pytest tests/test_submit.py -k tty -x` | ❌ W0 | ⬜ pending |
| TBD | (planner) | (planner) | SUB-02 | — | D-03 refusal prints missing field(s) when `is_submittable` is False | unit | `pytest tests/test_submit.py -k refuse -x` | ❌ W0 | ⬜ pending |
| TBD | (planner) | (planner) | SUB-03 | — | dedup hash deterministic; identical outcome → same id; excludes volatile fields (timestamp, host version, measured mV) | unit | `pytest tests/test_diagnostic_report.py -k dedup -x` | ❌ W0 (extend) | ⬜ pending |
| TBD | (planner) | (planner) | SUB-03 | — | fingerprint appears in `to_dict()` JSON AND is used in the issue title | unit | `pytest tests/test_submit.py -k title -x` | ❌ W0 | ⬜ pending |
| TBD | (planner) | (planner) | SAFE-03 | T-113-01 | `submit.py` sets no VPP, builds no wire dict, adds no dispatch entry; passes orchestrator checker | unit | `python tools/check_devtest_orchestrator.py` | ✅ (extend) | ⬜ pending |
| TBD | (planner) | (planner) | SUB-01/02 | — | `--submit` flag wired end-to-end via `CliRunner` with injected mock seams | integration | `pytest tests/test_dev_test_cmd.py -k submit -x` | ✅ (extend) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Threat refs map to RESEARCH.md § Known Threat Patterns: T-113-01 command injection (argv list, no `shell=True`) · T-113-02 PII/path leak · T-113-03 URL/param injection · T-113-04 unintended/silent send · T-113-05 report routed to attacker fork.*

---

## Wave 0 Requirements

- [ ] `tests/test_submit.py` — new file covering SUB-01/02/03 (tier selection, sanitize, oversize, TTY gate, refusal, title)
- [ ] Extend `tests/test_dev_test_cmd.py` — `--submit` flag end-to-end via mock seams
- [ ] Extend `tests/test_diagnostic_report.py` — dedup fingerprint determinism + volatile-field exclusion
- [ ] Extend `tests/test_check_devtest_orchestrator.py` — prove the new `submit.py` scan leg flips red on a planted violation (if `submit.py` is added to the scan set)
- [ ] No framework install needed — `pytest` / `CliRunner` / `mock` already in `.[test]`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real submission smoke (browser actually opens / `gh issue create` actually files) | SUB-01 | Filing a live GitHub issue and launching a real browser cannot run in CI; the logic is unit-tested behind injectable seams (`browser_open`, `run_fn`), so only the real-world open/create is manual | One-time: run `dev test <chip> --submit` on a real terminal against a throwaway/test issue; confirm the prefilled URL opens and (with `gh` authed) an issue lands in `henols/firestarter_app` |

*All other phase behaviors have automated verification via injected seams.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (all 10 per-task rows map 1:1 to a plan task `<automated>` command — plan-checker confirmed)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (`tests/test_submit.py` + extensions above)
- [x] No watch-mode flags (`pytest -x`, not `--watch`)
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

*`wave_0_complete` stays `false` until execution actually writes the Wave 0 test files.*

**Approval:** approved 2026-07-03
