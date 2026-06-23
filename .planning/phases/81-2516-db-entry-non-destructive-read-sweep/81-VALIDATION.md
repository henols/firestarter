---
phase: 81
slug: 2516-db-entry-non-destructive-read-sweep
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-23
---

# Phase 81 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (firestarter_app) |
| **Config file** | firestarter_app/pyproject.toml |
| **Quick run command** | `cd firestarter_app && pytest tests/test_database_conversion.py -q` |
| **Full suite command** | `cd firestarter_app && pytest -q` |
| **Estimated runtime** | ~32 seconds (650 tests, per 2026-06-23 research run) |

---

## Sampling Rate

- **After every task commit:** Run the quick run command
- **After every plan wave:** Run the full suite command
- **Before `/gsd-verify-work`:** Full suite must be green (incl. the 0xA4 `test_init_phase_data_frames_not_acked` guard — SAFE-02)
- **Max feedback latency:** ~32 seconds

---

## Per-Task Verification Map

*To be completed by the planner — map each task to its requirement, test type, and automated command. See RESEARCH.md §"Validation Architecture" for the recommended dimension coverage.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 81-01-01 | 01 | 1 | DB-02 | T-81-01 / — | FLAG_CAN_ERASE set for Flash/EEPROM 0x05; NOT set for UV-EPROM | unit | `cd firestarter_app && pytest tests/test_database_conversion.py -q` | ✅ | ⬜ pending |

---

## Wave 0 Requirements

- *Existing infrastructure (pytest, ruff, mypy) covers all software phase requirements — no Wave 0 framework install needed.*
- *Hardware bench requirements (SWEEP-01/02, EVID-*) are manual-only — see below.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 11-chip non-destructive read + blank-check on Leonardo + Rev 2.0 | SWEEP-01, SWEEP-02, EVID-01/02/03 | Requires physical chips + bench hardware (operator-executed) | Read + blank-check each chip; N≥3 byte-identical reads + negative control; record EVIDENCE row |
| 2516 user-override safety review sign-off | GRAD-02 | Human gate — operator personally approves the hand-authored override before bench | Operator signs `81-2516-SAFETY-REVIEW.md` checklist (D-01) |
| `firestarter info 2516` correct decode | GRAD-02 | Requires the user-override entry installed in `~/.firestarter/database.json` | Run `firestarter info 2516`, confirm 0x0B / DIP24_2716 / UV-EPROM / 25000mV / 2048 bytes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 32s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
