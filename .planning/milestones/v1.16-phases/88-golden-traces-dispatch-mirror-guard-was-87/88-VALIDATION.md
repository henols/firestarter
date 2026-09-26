---
phase: 88
slug: golden-traces-dispatch-mirror-guard-was-87
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-26
---

# Phase 88 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Detail source: `88-RESEARCH.md` → ## Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | Unity via PlatformIO `[env:native]` (`test_framework=unity`) |
| **Framework (host)** | pytest (`firestarter_app` `[test]` extra) |
| **Config file** | `firestarter/platformio.ini` (`[env:native]`); `firestarter_app/pyproject.toml` |
| **Quick run command** | `pio test -e native -f "*test_val_<family>*"` · `pytest tests/test_dispatch_mirror.py` |
| **Full suite command** | `pio test -e native` · (host) `pytest` + `tools/check_dispatch.py` + `tools/diff_db.py` |
| **Estimated runtime** | native suite <60s; host gates <30s |

---

## Sampling Rate

- **After every task commit:** Run the single touched suite — `pio test -e native -f "*test_val_<family>*"` (or `pytest tests/test_dispatch_mirror.py` for the mirror task). Sub-30s.
- **After every plan wave:** Full native suite `pio test -e native` + both gates `check_dispatch.py` / `diff_db.py`.
- **Before `/gsd-verify-work`:** Full native suite green + both host gates exit 0 + `pio run -e leonardo` flash unchanged (≈25654 B baseline) + the two safety-posture greps present.
- **Max feedback latency:** ~60 seconds

---

## Per-Task Verification Map

> Authoritative requirement→test map: `88-RESEARCH.md` → ### Phase Requirements → Test Map. Bound to the as-planned task IDs during planning.

| Requirement | Behavior | Test Type | Automated Command | File Exists |
|-------------|----------|-----------|-------------------|-------------|
| PRIM-01 | Per-family byte-exact write+chip-id golden traces pass | unit (native) | `pio test -e native -f "*test_val_*"` | suites ✅ / golden `.inc`+asserts ❌ W0 |
| PRIM-01 / SAFE-02 | Dispatch-order binds doc↔tool↔firmware | unit (host + native anchor) | `pytest tests/test_dispatch_mirror.py` + `pio test -e native -f "*test_dispatch*"` | native anchor ✅ / mirror ❌ W0 |
| SAFE-02 | INV-01..09 invariants stay green | unit (native) | `pio test -e native` | ✅ existing |
| SAFE-04 | check_dispatch 0 violations | gate (host) | `python3 tools/check_dispatch.py` | ✅ green this session |
| SAFE-04 | diff_db empty | gate (host) | `python3 tools/diff_db.py` | ✅ green this session |
| SAFE-04 | Leonardo flash near-zero delta | gate (build) | `pio run -e leonardo` | ✅ baseline 25654 B |
| SAFE-04 | over-voltage check present/unmodified | structural (grep/test) | `grep -n "vpp_mv > (uint32_t)handle->vpp_mv + 500" src/proms/eprom.cpp src/proms/flash_intel.cpp` | ✅ `eprom.cpp:282`, `flash_intel.cpp:65` |
| SAFE-04 / SAFE-01 | resolve_chip guard never bypassed | structural (grep/test) | `grep -n 'support_status != "supported"' firestarter/chip_resolver.py` | ✅ `chip_resolver.py:55` |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `golden_<family>_write.inc` × 5 + `golden_<family>_chip_id.inc` × 4 — committed fixtures (PRIM-01)
- [ ] Shared `assert_trace_eq()` + `GOLDEN_BLESS` print helper (`_shared/golden_trace.h` or per-suite)
- [ ] Golden-trace test functions wired into each `test_val_*` `main()` RUN_TEST list
- [ ] `firestarter_app/tests/test_dispatch_mirror.py` — doc↔tool bind (PRIM-01/SAFE-02)
- [ ] (optional) explicit host assertion that native `test_dispatch` enumerates every §0 protocol

*Framework install: none — Unity/ArduinoFake bundled by PIO; pytest via existing `[test]` extra.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| (none) | — | This is a freeze-the-world test+gate phase; no bench/hardware step | All phase behaviors have automated or grep-structural verification |

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
