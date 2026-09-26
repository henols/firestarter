---
phase: 104
slug: rename-protocol-header-and-cpp-files-to-descriptive-protocol
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-02
---

# Phase 104 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Sourced from 104-RESEARCH.md § Validation Architecture. Behavior-preserving rename — existing infrastructure covers all requirements; no Wave 0 test authoring needed (existing tests are UPDATED via string substitution when functions rename).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity (PlatformIO `[env:native]`) + pytest (host `firestarter_app`) |
| **Config file** | `firestarter/platformio.ini` (`[env:native]`, `test_framework=unity`); `firestarter_app` pytest |
| **Quick run command** | `pio test -e native -f "*test_dispatch*"` |
| **Full suite command** | `pio test -e native` + `pytest firestarter_app/tests/test_dispatch_mirror.py firestarter_app/tests/test_check_dispatch_invariants.py` |
| **Estimated runtime** | ~60–120 seconds (native build + host pytest) |

---

## Sampling Rate

- **After every task commit:** `pio test -e native -f "*test_dispatch*"` (fast dispatch sanity)
- **After every plan wave:** `pio test -e native` full + host `pytest` dispatch-mirror suites
- **Before `/gsd-verify-work`:** `pio run -e uno` + `pio run -e leonardo` compile green + full native + host mirror green
- **Max feedback latency:** ~120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | 01 | 1 | RENAME-01/02 | — | dispatch + VPP-safety unchanged | build + native | `pio run -e uno && pio run -e leonardo && pio test -e native` | ✅ | ⬜ pending |
| TBD | 01 | 1 | RENAME-03 | — | no surviving misspelled/old guard | grep smoke | `! grep -rn "FALSH\|flash_type_3\|flash_type_4" firestarter/src firestarter/include` | ✅ | ⬜ pending |
| TBD | 02 | 2 | RENAME-04 | — | dispatch-mirror + invariants hold | host pytest | `pytest firestarter_app/tests/test_dispatch_mirror.py firestarter_app/tests/test_check_dispatch_invariants.py` | ✅ | ⬜ pending |
| TBD | 02 | 2 | RENAME-05 / GATE-01 | — | doc↔tool↔firmware bind intact | host pytest | `pytest firestarter_app/tests/test_dispatch_mirror.py` | ✅ | ⬜ pending |
| TBD | 02 | 2 | GATE-02 | — | DB identity | host | `python firestarter_app/tools/diff_db.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky. Task IDs finalized by the planner.*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* Native dispatch/val suites + host dispatch-mirror + `validation_matrix.h` generator already exist. When functions rename (Q1=files+functions), existing tests are UPDATED (string substitution + regenerate `validation_matrix.h` from `validation_matrix_spec.json`), not newly authored.

---

## Manual-Only Verifications

*All phase behaviors have automated verification.* (`pio run -e uno`/`-e leonardo` compile is the closest-to-manual step and is scriptable.)

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (N/A — none)
- [x] No watch-mode flags
- [x] Feedback latency < 120s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-07-02 (plan-checker VERIFICATION PASSED, dimension-8 checks 8a–8d green)
