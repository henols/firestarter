---
phase: 98
slug: fix-correct-the-0x08-32-pin-write-vpp-path
status: ready
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-30
---

# Phase 98 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Blind/no-bench phase — all verification is native tests + host gate scripts + py3.11 CI.
> The silicon write→verify proof is Phase 99 (not validated here; do NOT over-claim).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Firmware framework** | Unity via PlatformIO `[env:native]` (ArduinoFake/fakeit for delay/Serial) |
| **Firmware config file** | `firestarter/platformio.ini` (`[env:native]`) |
| **Firmware quick run** | `pio test -e native -f "*test_val_eprom*"` |
| **Firmware full suite** | `pio test -e native` |
| **Host framework** | pytest + ruff + mypy + tool scripts (`firestarter_app/`) |
| **Host gate** | `ruff check` · `ruff format --check` · `mypy` · `python tools/diff_db.py` · `python tools/check_dispatch.py` |
| **Estimated runtime** | ~30–60s native; host gate ~20s |

---

## Sampling Rate

- **After every task commit:** firmware → `pio test -e native -f "*test_val_eprom*"`; host → `python tools/check_dispatch.py && python tools/diff_db.py` after any DB/pinout change.
- **After every plan wave:** `pio test -e native` (full native) ; `pytest -q` (full host).
- **Before `/gsd-verify-work`:** full native suite green + host `ruff check` + `ruff format --check` + `mypy` + `diff_db` + `check_dispatch` green **on py3.11**.
- **Max feedback latency:** ~60s.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 98-01-01 | 01 | 1 | FIX-03 | T-98-02 | DIP32_27C020 added; siblings untouched; valid JSON | unit (host) | `python -c "...assert DIP32_27C020 pin31 off bus..."` | ✅ | ⬜ pending |
| 98-01-02 | 01 | 1 | FIX-03 | T-98-01 | size-gated assignment; 512K/1M stay DIP32_STD; diff_db clean | unit (host) | `python tools/build_db.py && python tools/diff_db.py` | ✅ | ⬜ pending |
| 98-01-03 | 01 | 1 | SAFE-02 | T-98-03/04 | ruff+format+mypy+diff_db+check_dispatch green on py3.11; 0 VPP violations | host CI | `ruff check . && ruff format --check . && python tools/check_dispatch.py && python tools/diff_db.py` | ✅ | ⬜ pending |
| 98-02-01 | 02 | 2 | FIX-01/FIX-02 | T-98-05/07 | corrected-path + gate-exclusion + mismatch tests (RED pre-fix) | unit (native) | `pio test -e native -f "*test_val_eprom*"` | ❌ W0 (extend test_val_eprom.cpp) | ⬜ pending |
| 98-02-02 | 02 | 2 | FIX-01/SAFE-02 | T-98-05/06/08 | gated PGM-assert GREEN; size term present; vpp_check_window untouched | unit (native) | `pio test -e native -f "*test_val_eprom*"` | ❌ W0 (Task 1) | ⬜ pending |
| 98-02-03 | 02 | 2 | FIX-02 | T-98-07 | 0x07/0x0B/chip-id byte-identical; 0x08 re-pinned only if changed | unit (native) | `pio test -e native -f "*test_val_eprom*" && git diff --exit-code <non-0x08 .inc>` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` — corrected-0x08-32-pin recording test (PGM line driven program-active), gate-exclusion test (mem_size=524288 → no PGM-assert), and ≥1 failure-case/mismatch test (D-05 / P89 CR-01). Authored as Plan 02 Task 1 (RED first).
- [ ] Provision a python3.11 interpreter for local SAFE-02 validation (no 3.11 binary in devcontainer — Pitfall 5); else run host gate under CI and mark py3.11 sign-off CI-pending.

*All other phase behaviors are covered by existing infrastructure (golden traces, diff_db, check_dispatch, vpp_check_window coverage).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Bits actually flip on seated AM27C020 silicon | (BENCH-01, Phase 99 — NOT this phase) | Blind/no-bench phase; the pin-31-already-VIL caveat (Pitfall 6) means native correctness ≠ silicon success | Deferred to Phase 99 (Leonardo + Rev 2.0, operator-witnessed write→verify SHA) |

*Phase 98 itself has full automated verification for every in-scope behavior (host gate + native tests). The silicon residual is explicitly a Phase-99 gate, not a Phase-98 manual check.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (test_val_eprom.cpp new tests = Plan 02 Task 1)
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-30
