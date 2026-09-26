---
phase: 6
slug: logging-infrastructure
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-18
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Draft skeleton derived from RESEARCH.md `## Validation Architecture`. Planner fills the per-task verification map; reviewer flips `nyquist_compliant: true` when sign-off is met.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (firestarter_app) + PlatformIO `native` env (firestarter) |
| **Config file** | `firestarter_app/pyproject.toml` (Wave 0 creates) + `firestarter/platformio.ini [env:native]` (exists) |
| **Quick run command** | `pytest firestarter_app/tests/ -k <selected>` (host) · `pio test -e native -f <selected>` (firmware) |
| **Full suite command** | `pytest firestarter_app/tests/ && pio test -e native -d firestarter` |
| **Estimated runtime** | ~30s host + ~60s firmware native = ~90s |

---

## Sampling Rate

- **After every task commit:** Run quick run command scoped to the changed module
- **After every plan wave:** Run full suite command
- **Before `/gsd-verify-work`:** Full suite must be green AND `pio run -e leonardo` + `pio run -e uno` build clean AND codegen-drift gate passes (`python tools/catalog/codegen.py … && git diff --exit-code`)
- **Max feedback latency:** 90s

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| _populated by planner_ | | | | | | | | | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/pyproject.toml` — pytest config block (currently absent; sub-repo has no test infra)
- [ ] `firestarter_app/tests/__init__.py` + `firestarter_app/tests/conftest.py` — shared fixtures including a `BytesIO`-style fake serial harness for the decoder (per RESEARCH §LHOST-01 fixture)
- [ ] `firestarter_app/.github/workflows/ci.yml` — host CI workflow with pytest + codegen-drift gate (existing release/publish workflows do NOT run tests)
- [ ] `firestarter/test/native/test_messages/` — native test suite for `rurp_log_id` + CRC8 + frame emit (mirror `test_dispatch/` layout per RESEARCH)
- [ ] `.planning/catalog/` directory in meta-repo (catalog source + codegen + sync script)

*If none of the above need Wave 0 work: "Existing infrastructure covers all phase requirements." — but Phase 6 verifiably DOES need Wave 0 setup; the planner cannot skip this section.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Flash budget check on Leonardo | LFW-01, LFW-02 | Requires physical `pio run -e leonardo` output inspection vs 98.7% baseline | After Phase 6 close, run `pio run -e leonardo`, record `Flash:` line, confirm new helper + table fit (Leonardo headroom ~520 bytes at start, additive code estimated 600–900 bytes — may need conditional-include strategy if it tips over) |
| PORTD ghost-byte robustness in real bench traffic | LHOST-04 (defense-in-depth) | Cannot be simulated — needs real RURP shield exercising address bus during a long read | After Phase 6 close, run `firestarter read -e <chip>` against Uno with the always-on byte-stream reader; confirm no spurious `LogMessage` emissions from ghost bytes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (pytest infra, host CI workflow, native test suite, meta-repo catalog dir)
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
