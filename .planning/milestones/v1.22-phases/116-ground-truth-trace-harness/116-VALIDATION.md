---
phase: 116
slug: ground-truth-trace-harness
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-27
---

# Phase 116 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `116-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | Unity 2.6.1 via PlatformIO 6.1.19, `platform = native` |
| **Framework (host)** | pytest 9.1.1 |
| **Config file** | `firestarter/platformio.ini` §`[env:native]` · `firestarter_app/pyproject.toml` |
| **Quick run command (firmware)** | `cd firestarter && pio test -e native -f "*test_sdp_harness*"` |
| **Quick run command (host)** | `cd firestarter_app && python -m pytest tests/test_sdp_db_invariant.py tests/test_sdp_bus_config_drift.py -x` |
| **Full suite command (firmware)** | `cd firestarter && pio test -e native` — **baseline 80/80** |
| **Full suite command (host)** | `cd firestarter_app && python -m pytest -x` |
| **Estimated runtime** | quick ~2–5 s · firmware full ~24–40 s |

No framework install is required — both toolchains are already present.

---

## Sampling Rate

- **After every task commit:** `pio test -e native -f "*test_sdp_harness*"` (firmware tasks) / `python -m pytest tests/test_sdp_*.py -x` (host tasks)
- **After every plan wave:** `cd firestarter && pio test -e native` (must stay **80/80** plus the new always-green suite's cases) **and** `cd firestarter_app && python -m pytest -x`
- **Before `/gsd-verify-work`:** both full suites green, plus `ruff check` / `ruff format --check` against the py3.9/3.11 CI target, plus `diff_db.py` identity proving the chip DB is untouched
- **Max feedback latency:** 40 seconds

---

## Per-Task Verification Map

Task IDs are assigned by the planner; rows below are keyed by requirement and must be
re-keyed to `116-NN-MM` task IDs once PLAN.md files exist.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | TRACE-01a | — | Ordered stream interleaves data bytes, latch strobes and CE/OE | unit | `pio test -e native -f "*test_sdp_harness*"` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | TRACE-01b | — | Flag-off is byte-exact — all pre-existing suites unchanged | regression | `pio test -e native` → 80/80 | ✅ | ⬜ pending |
| TBD | TBD | TBD | TRACE-02 | — | Ordered `(LSB,MSB,data,CE)` stream pinned per pinout, RED today | unit (parked) | `pio test -e native -f "*test_eeprom28c_sdp*"` (parked → Phase 117) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | TRACE-03a | — | Unlock table mutated to `0x10` → different stream | unit | `pio test -e native -f "*test_sdp_harness*"` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | TRACE-03b | — | Lock table swapped for write prefix → different stream | unit | `pio test -e native -f "*test_sdp_harness*"` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | TRACE-03c | — | Planted `LOG_` in timing window → scan fails | unit (host) | `python -m pytest tests/test_no_log_in_sdp_window.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | TRACE-03d | — | `protocol != 0x0D` → `configure_not_implemented()` / `0xBB` | unit | `pio test -e native -f "*test_not_implemented*"` | ✅ extend | ⬜ pending |
| TBD | TBD | TBD | TRACE-04a | — | Address-keyed mock replaces call-ordered mock | unit | `pio test -e native -f "*test_sdp_harness*"` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | TRACE-04b | — | No `s_mock_bytes[n] = 0x20` fixture survives (3 sites) | structural | grep gate / host pytest over migrated suites | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | TRACE-05 | — | 84 × `algorithm==13` all `chip_id_check: false` **and** count == 84 | unit (host) | `python -m pytest tests/test_sdp_db_invariant.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | TRACE-06 | — | INIT-abort premise settled + PROJECT.md corrected | doc + unit | `116-PREMISE.md` reviewed; evidence re-runnable via the RED suite | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | D-10 | — | Generated header drift-gated | unit (host) | `python -m pytest tests/test_sdp_bus_config_drift.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/_shared/host_stubs_common.inc` — extend with the CORRECTION 1 guard set (TRACE-01)
- [ ] `firestarter/test/native/avr/test_sdp_harness/{host_stubs.cpp,test_sdp_harness.cpp,sdp_expected.h}` — always-green suite (TRACE-01, TRACE-03a/b, TRACE-04)
- [ ] `firestarter/test/native/avr/test_eeprom28c_sdp/{host_stubs.cpp,test_eeprom28c_sdp.cpp,sdp_expected_fixed.h,RED-BASELINE.md}` — parked RED suite (TRACE-02, TRACE-06 evidence)
- [ ] `firestarter/test/native/avr/_shared/sdp_bus_config.h` — generated, `DO NOT EDIT` (D-08)
- [ ] `firestarter/platformio.ini` — `test_filter` + `-I` for the always-green suite **only**; `-I` (not `test_filter`) for the parked suite, with the named `TODO(v1.22 Phase 117)`
- [ ] `firestarter_app/tools/gen_sdp_bus_config.py` (D-08/D-11)
- [ ] `firestarter_app/tools/check_no_log_in_sdp_window.py` + planted fixture (TRACE-03c)
- [ ] `firestarter_app/tests/test_sdp_bus_config_drift.py` — `FW_ABSENT` skipif (D-11)
- [ ] `firestarter_app/tests/test_sdp_db_invariant.py` — **no** skipif (TRACE-05, F9)
- [ ] `.planning/phases/116-ground-truth-trace-harness/116-PREMISE.md` (TRACE-06, D-14)
- [ ] `.planning/PROJECT.md` — third ⚠ correction block (D-14), carrying CORRECTION 4's *66 of 84*
- [ ] **Setup task:** create the `v1.22-...` branch off `beta` in **both** sub-repos (F10)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| PROJECT.md correction block wording | TRACE-06 / D-14 | Prose accuracy of a premise correction is a human judgement, not a machine assertion | Operator reads `116-PREMISE.md` + the new PROJECT.md ⚠ block and confirms the finding matches the harness evidence |

No hardware/bench verification is in scope — this phase is software-only (zero production-code risk).

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 40s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
