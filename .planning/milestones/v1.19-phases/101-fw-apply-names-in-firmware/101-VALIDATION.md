---
phase: 101
slug: fw-apply-names-in-firmware
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-01
---

# Phase 101 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Filled from the `## Validation Architecture` section of `101-RESEARCH.md`. This is a
> rename/relabel-only phase — the validation surface is the existing guard suite, which must
> stay green (with the one pre-existing RED guard, `test_dispatch_mirror.py`, reconciled in Wave 0).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | PlatformIO Unity (firmware, `native` env) + pytest 7.x (host `firestarter_app`) |
| **Config file** | `firestarter/platformio.ini`, `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/test_dispatch_mirror.py -q` |
| **Full suite command** | `cd firestarter && pio test -e native && pio run -e uno` then host guards (below) |
| **Estimated runtime** | ~60–120 seconds (native tests + uno build + host guards) |

**Host guard commands (GATE-01/GATE-02 — see 101-RESEARCH.md for exact green-state):**
- `python firestarter_app/.../check_dispatch.py` → PASS (746 dispatch rows)
- `python firestarter_app/.../diff_db.py` → identity (no chip_database.json change)
- constants-parity pytest (`constants.py` ↔ `firestarter.h`) → 6 pass
- `ruff check firestarter_app/` + `ruff format --check` + `mypy` → clean against **py3.11** CI target
- v1.16 golden register traces → byte-identical (or re-pinned with cited cosmetic rationale)

---

## Sampling Rate

- **After every task commit:** Run the quick run command (`pytest test_dispatch_mirror.py -q`)
- **After every plan wave:** Run the full suite command (native tests + uno build + all host guards)
- **Before `/gsd-verify-work`:** Full suite + all GATE guards must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 101-00-01 | 00 | 0 | GATE-01 | — | dispatch-mirror parser reads Phase-100 PROTOCOLS.md table → non-empty | unit | `pytest tests/test_dispatch_mirror.py -q` | ✅ | ⬜ pending |
| 101-01-01 | 01 | 1 | FW-01 | — | `PROTO_<NAME>` defined for every protocol number, values unchanged | unit/build | `pio run -e uno` + constants-parity pytest | ✅ | ⬜ pending |
| 101-01-02 | 01 | 1 | FW-02 | — | memory.cpp dispatch reads named constants; order/behavior identical | golden trace | `pio test -e native` + golden register traces | ✅ | ⬜ pending |
| 101-02-01 | 02 | 2 | FW-03 | — | family handler files/functions confirmed conformant to approved layer | source assert | grep-assert handler names + `pio run -e uno` | ✅ | ⬜ pending |
| 101-02-02 | 02 | 2 | GATE-01/02 | — | check_dispatch PASS, diff_db identity, parity green, py3.11 ruff/mypy clean | integration | all host guard commands above | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Task IDs are indicative; final IDs assigned by the planner. Wave 0 MUST precede the GATE-green assertions.*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_dispatch_mirror.py` — **fix the parser** so it reads the Phase-100
      PROTOCOLS.md table layout (currently RED: `parse_protocols_md() returned an empty table`).
      This is a pre-existing red guard reconciled in-scope (D-03) — GATE-01 cannot be honestly
      claimed green until this passes.

*All other verification uses existing infrastructure (native tests, uno build, check_dispatch,
diff_db, constants-parity, golden traces) — no new framework install needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| No hardware behavior change (bench) | GATE-01 | Rename-only; dispatch order/values identical → no bench re-validation required | N/A — golden traces + native tests + uno build are the authoritative automated proof; no chip on socket needed |

*Rename/relabel-only phase: all phase behaviors have automated verification. No bench hardware run is required for this phase.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (the red dispatch-mirror guard)
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
