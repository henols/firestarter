---
phase: 99
slug: bench-ledger-graduation-gate-evidence-ledger-update
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-01
---

# Phase 99 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> **Note:** Phase 99's primary "validation" is an operator-witnessed hardware gate (BENCH-01),
> not an automated suite. The automatable surface is the ledger gate (`check_ledger.py`) + its
> unit tests and the EVIDENCE-cell consistency check.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (host: `firestarter_app`) + standalone gate scripts (`check_ledger.py`, `check_*.py`) |
| **Config file** | `firestarter_app/pyproject.toml` (host); gate scripts are argv-free standalone |
| **Quick run command** | `python3 .planning/v1.16/ledger/tools/check_ledger.py` |
| **Full suite command** | `cd .planning/v1.16/ledger/tools && python3 -m pytest test_check_ledger.py -q` (plus Phase-97 gates) |
| **Estimated runtime** | ~5 seconds (gate scripts); pytest ~seconds |

---

## Sampling Rate

- **After every task commit:** `check_ledger.py` (after any ledger edit); `pytest test_check_ledger.py -q` (after any gate edit).
- **After every plan wave:** full gate-script set (Phase-97 checks + `check_ledger.py`) green.
- **Before `/gsd-verify-work`:** `check_ledger.py` exit 0 + BENCH-01/02 evidence complete + operator sign-off.
- **Max feedback latency:** ~10 seconds (software); hardware gate is operator-paced.

---

## Per-Task Verification Map

*Populated by the planner/executor. Anchor rows:*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 99-XX-XX | XX | 1 | LEDGER (SC#3) | — | ledger self-consistent, 0 contradictions | integration | `python3 .planning/v1.16/ledger/tools/check_ledger.py` | ✅ | ⬜ pending |
| 99-XX-XX | XX | 1 | LEDGER (SC#3) | — | gate extension doesn't regress 11 other rows | unit | `python3 -m pytest test_check_ledger.py -q` | ✅ (extend) | ⬜ pending |
| 99-XX-XX | XX | 2 | BENCH-02 | T-99-fabrication | EVIDENCE cell filled + SHA-self-consistent | integration | Phase-99 EVIDENCE/signature gate | ⚠️ may add sibling | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Extend `check_ledger.py` / `test_check_ledger.py` to admit a v1.18-native `0x08` graduation (written-image SHA == read-back SHA) WITHOUT requiring a v1.15 *write* baseline — while keeping the 11 existing rows green. **(The single required software task.)**
- [ ] (Recommended) A Phase-99 EVIDENCE gate (reuse `check_signature.py` shape or add `check_graduation.py`) asserting the P99 cell fields are filled + SHA-self-consistent (anti-fabrication).
- *No test-framework install needed — pytest + gate scripts already present.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| write→verify byte-exact on seated AM27C020 (SHA match) OR clean deferral | BENCH-01 | Requires physical chip seated on Leonardo + Rev 2.0; operator authorizes each live write | `firestarter write -b <img>` → `verify`/`read` → `sha256sum` compare; operator-witnessed with `controller:` identity + live R1/R2 readback |
| read stability (N≥3, not N=1) | BENCH-01 | Hardware read variance | `firestarter dev consistency-check AM27C020 --runs 3` |
| VPP rail at socket pin 1 during program window | BENCH-02 | DMM at physical socket; pot set by operator (12.75V±0.25, no monitor loops) | Operator sets pot, says "done"; ONE confirmation read via `timeout -s INT <sec> stdbuf -oL firestarter vpp` (ADC monitor) or DMM if held-rail tooling permits |

---

## Validation Sign-Off

- [ ] All software tasks have automated verify or Wave 0 dependencies
- [ ] Hardware tasks documented as Manual-Only with operator-witness protocol
- [ ] Wave 0 covers the ledger-gate extension (the MISSING reference)
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s (software)
- [ ] `nyquist_compliant: true` set in frontmatter (after execution)

**Approval:** pending
