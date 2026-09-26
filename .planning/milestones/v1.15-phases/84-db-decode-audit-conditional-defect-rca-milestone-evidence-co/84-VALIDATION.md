---
phase: 84
slug: db-decode-audit-conditional-defect-rca-milestone-evidence-co
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-24
---

# Phase 84 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `84-RESEARCH.md` §Validation Architecture. Closing phase of v1.15 — firmware (VPP-skip)
> + host (FM1608 blank-check, DB relabel) + manual bench re-validation.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (host)** | pytest (Py3.11 CI / Py3.12 devcontainer) |
| **Framework (firmware)** | PlatformIO Unity `[env:native]` |
| **Config file** | `firestarter_app/.github/workflows/ci.yml` (ruff/mypy/pytest); `firestarter/platformio.ini` `[env:native]` |
| **Quick run command (host)** | `cd firestarter_app && python -m pytest tests/test_eprom_operations.py -x` |
| **Full suite command (host)** | `cd firestarter_app && python -m pytest` |
| **Firmware native** | `cd firestarter && pio test -e native` |
| **DB gate scripts** | `cd firestarter_app && python tools/check_dispatch.py && python tools/diff_db.py` |
| **Estimated runtime** | host suite ~30–60s; `pio test -e native` ~1–2 min |

---

## Sampling Rate

- **After every task commit:** host quick run (`pytest tests/test_eprom_operations.py -x`) + `pio test -e native` if firmware was touched.
- **After every plan wave:** full host suite + `check_dispatch.py` + `diff_db.py` (all green) + 0xA4 guard (`test_init_phase_data_frames_not_acked`).
- **Before `/gsd-verify-work`:** full host suite green + `pio test -e native` green + Leonardo flash ≤ ~90% (if firmware touched); bench re-validation recorded in EVIDENCE.{md,json}.
- **Max feedback latency:** < 120s (automated tiers); manual bench is operator-gated and out of the latency budget.

---

## Per-Task Verification Map

| Req / Behavior | Wave | Test Type | Automated Command | File Exists | Status |
|----------------|------|-----------|-------------------|-------------|--------|
| FIX-01 (VPP-skip): `read`/`blank-check` init does NOT enable VPP regulator / emit VPP ERROR-WARN; write/erase/chip-id STILL gate VPP | 1 (fw) | firmware native (unit) | `pio test -e native -f "*test_dispatch*"` (extend dispatch suite) | ✅ suite; ❌ W0: add VPP-skip + negative assertion | ⬜ pending |
| FIX-01 (FM1608 blank): `blank` on SRAM/FRAM short-circuits cleanly, no 0xA4 | 1 (host) | host unit | `pytest tests/test_eprom_operations.py::<new_test> -x` | ✅ file; ❌ W0: add test | ⬜ pending |
| D-40 (relabel label-only): `diff_db.py` exits 0 (relabel explained); CAN_ERASE pinning unchanged | 1 (host) | host integration | `python tools/diff_db.py && pytest tests/test_diff_db_gate.py -x` | ✅ `test_diff_db_gate.py`; ❌ W0: add RULE_PHASE84_RELABEL + assertion | ⬜ pending |
| D-40 (CAN_ERASE not flipped): relabel does NOT change SST39SF040/FM1608 `flags`/CAN_ERASE | 1 (host) | host unit | extend Phase-81 81-01 CAN_ERASE re-audit pinning test | ✅ test exists; ❌ W0: add pin | ⬜ pending |
| D-40 (no dispatch regression): full-DB VPP-safety gate green | 1 (host) | host integration | `python tools/check_dispatch.py` | ✅ exists | ⬜ pending |
| SAFE-02 (D-51): 0xA4 ack guard green before bench | 1 (host) | host unit | `pytest tests/test_eprom_operations.py::test_init_phase_data_frames_not_acked -x` | ✅ exists | ⬜ pending |
| FIX-01 re-bench (2516 read N≥3 / 0x08 / flash4) | bench | manual-only (hardware) | operator-gated; `dev consistency-check --runs 3`, `dev write-cycle`/`write -b` | n/a — manual, recorded in EVIDENCE | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Native dispatch assertion that `eprom_generic_init` skips VPP for `CMD_READ`/`CMD_BLANK_CHECK` **and** a negative assertion that write/erase/chip-id STILL gate VPP (extend `test/native/avr/test_dispatch/test_configure_memory.cpp` or a new suite) — covers FIX-01 firmware + the over-broadening hazard.
- [ ] Host test pinning the FM1608/SRAM blank-check short-circuit in `tests/test_eprom_operations.py` — covers FIX-01 host (D-30).
- [ ] `tools/diff_db.py` `RULE_PHASE84_RELABEL` root-cause rule + `tests/test_diff_db_gate.py` assertion — covers D-40 diff-gate BLOCK risk (Pitfall 3).
- [ ] CAN_ERASE pinning assertion that the relabel does NOT change SST39SF040/FM1608 `flags` (reuse/extend the Phase-81 81-01 re-audit test) — proves D-40 label-only-for-CAN_ERASE.
- [ ] *(If FM1608 FRAM label taken)* host test pinning the VPP-display gate + `_ELECTRICAL_TYPE_LABEL` "FRAM" entry.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 2516 read re-validation after VPP-skip fix (read + blank-check + decode, N≥3 byte-identical) — NEVER written | FIX-01 / D-20/D-21 | Single irreplaceable UV part; real silicon on Leonardo + Rev 2.0 | After fw flash: `dev consistency-check 2516 --runs 3`; record SHA stability + VPP rail in EVIDENCE. STOP at read — no write. |
| AM27C020 0x08 write re-bench (RCA-and-defer) | FIX-01 / D-31(a) | Real silicon; 0x08/DIP32 P1-as-VPP write path | Retry write after VPP-skip fix; if still 0-bits-programmed, record disposition + future tracker (do NOT fix unless trivial). |
| W29C040 flash4 256B-page write re-bench (RCA-and-defer) | FIX-01 / D-31(c) | Real silicon; flash4 SDP/poll/VPP behaviour | `write -b` with 256B-page; if FAIL, reopen Phase-74 Wave-2 / CR-01 disposition. |
| Firmware fit/health | D-10 | Physical board program | `pio run -e leonardo` → Leonardo flash ≤ ~90%; verify `controller:` identity + `r1 ≈ 270000`; ASK silkscreen shield rev. |

---

## Validation Sign-Off

- [ ] All automatable tasks have an `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (5 items above)
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s (automated tiers)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
