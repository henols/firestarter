---
phase: 57
slug: decode-bug-fixes-protocol-map-check-dispatch-extension
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-08
---

# Phase 57 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `cd firestarter_app && pytest tests/ -q -x` |
| **Full suite command** | `cd firestarter_app && pytest tests/ -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && pytest tests/ -q -x`
- **After every plan wave:** Run `cd firestarter_app && pytest tests/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green (470+ tests) + `ruff check` + `ruff format --check`
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 57-01-* | 01 | 1 | DEC-03 | — | Decode never silently inflates a hardware timing value (×100 removed) | unit | `cd firestarter_app && pytest tests/ -q -k timing` | ❌ W0 (may add) | ⬜ pending |
| 57-01-* | 01 | 1 | DEC-04 | — | VCC/VDD decode never mislabels a voltage rail | unit | `cd firestarter_app && pytest tests/ -q -k voltage` | ❌ W0 (may add) | ⬜ pending |
| 57-02-* | 02 | 1 | DEC-05 | — | PROTOCOL_MAP exposes only canonical/known algorithm IDs | unit | `cd firestarter_app && pytest tests/ -q -k protocol` | ❌ W0 (may add) | ⬜ pending |
| 57-03-* | 03 | 2 | GATE-03 | T-57-01 | No vpp-pin + 5V-EEPROM-handler chip routes to a VPP-asserting path | gate | `cd firestarter_app && python tools/check_dispatch.py` | ✅ exists | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Confirm existing `firestarter_app/tests/` covers `build_db.py` decode (timing, VCC/VDD, PROTOCOL_MAP). If a decode unit test does not exist, add focused regression tests asserting the corrected values (W27C512 `pulse_duration` == 100 µs; nibble 0x02→4V / 0x03→4.5V; vcc=bits11-8 / vdd=bits15-12; PROTOCOL_MAP contains no `0x2A/0x2C/0x2E/0x35/0x3C` non-canonical entries).
- [ ] `firestarter_app/tools/baseline/chip_database.baseline.json` — before/after diff harness already established by Phase 56; reuse it to confirm only intended fields change.

*Existing pytest infrastructure (470+ tests) covers most phase requirements; decode-specific regression assertions may be added in Wave 0.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `firestarter info W27C512` shows `pulse_duration` 100 µs | DEC-03 | End-user CLI surface (DB regenerated) | Regenerate `chip_database.json`, run `firestarter info W27C512`, confirm `pulse_duration`/timing reads 100 µs not 10000 µs |

*All other phase behaviors have automated verification (pytest + `check_dispatch.py` exit code).*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
