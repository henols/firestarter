---
phase: 77
slug: erase-write-path-graduation-0x07-ee-eproms
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-21
validated: 2026-06-22
---

# Phase 77 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.0 (confirmed installed) |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter_app && python3 -m pytest tests/test_database_conversion.py tests/test_revision_constants_parity.py -v` |
| **Full suite command** | `cd firestarter_app && python3 -m pytest --cov --cov-fail-under=70` |
| **Estimated runtime** | ~30 seconds (full suite) |

**Lint/type gates:** `ruff check . && ruff format --check .` (validate against py3.9/3.11 target — devcontainer py3.12 masks CI) + `mypy firestarter/database.py` (NOTE: `database.py` is NOT in the strict-8 module list, so strict overrides do not apply to the edit site).

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_database_conversion.py tests/test_revision_constants_parity.py -v`
- **After every plan wave:** Run `pytest --cov --cov-fail-under=70 && python3 tools/check_dispatch.py && ruff check . && ruff format --check .`
- **Before `/gsd-verify-work`:** Full suite green + `check_dispatch.py` PASS
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 77-01-01 | 01 | 1 | ERASE-01 | — | EEPROM (0x07) → FLAG_CAN_ERASE set | unit | `pytest tests/test_database_conversion.py::test_convert_w27c512_flag_can_erase -x` | ✅ | ✅ green |
| 77-01-02 | 01 | 1 | ERASE-01 | — | UV-EPROM → flag clear | unit | `pytest tests/test_database_conversion.py::test_convert_uv_eprom_no_flag_can_erase -x` | ✅ | ✅ green |
| 77-01-03 | 01 | 1 | ERASE-01 | — | Flash/EEPROM (AT28C256) → flag set | unit | `pytest tests/test_database_conversion.py::test_convert_at28c256_flash_eeprom_flag_can_erase -x` | ✅ | ✅ green |
| 77-02-01 | 02 | 1 | ERASE-01/D-07 | T-77-A4 | INIT/END DATA frames NOT acked | unit | `pytest tests/test_eprom_operations.py::test_init_phase_data_frames_not_acked -x` | ✅ | ✅ green |
| 77-03-01 | 03 | 2 | SAFE-02 | T-77-VPP | check_dispatch full-DB VPP gate clean | integration | `python3 tools/check_dispatch.py` | ✅ | ✅ green |
| 77-03-02 | 03 | 2 | SAFE-03 | — | FLAG_CAN_ERASE parity constants.py=firestarter.h | unit (existing) | `pytest tests/test_revision_constants_parity.py -v` | ✅ | ✅ green |
| 77-03-03 | 03 | 2 | SAFE-01 | — | 8 chips supported; resolve_chip no refusal | unit (existing) | `pytest tests/test_chip_resolver.py -v` | ✅ | ✅ green |
| 77-04-01 | 04 | 3 | ERASE-02 | T-77-VPP | write→auto-erase→program→verify clean on Leonardo | hardware/bench | manual — Leonardo W27C512 + SHA match | N/A | ✅ bench-proven (manual) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/test_database_conversion.py` — add 3 `convert_to_programmer` FLAG_CAN_ERASE tests (EEPROM/0x07 set, UV-EPROM clear, Flash/EEPROM set) — **landed (77-01, commit `92898f8`)**
- [x] `tests/test_eprom_operations.py` — add D-07 `ack_data=False` (0xA4) INIT/END-DATA-not-acked regression test — **landed (77-02, commit `5d8a5b1`)**

*Existing infrastructure (`test_chip_resolver.py`, `test_revision_constants_parity.py`, `check_dispatch.py`) covers SAFE-01/02/03 with no new files.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| write→auto-erase→program→verify cycle | ERASE-02 | Requires physical Leonardo + real non-blank W27C512 + bench shield | Standing bench precondition (ASK shield rev, r1≈270000 reconcile, controller port identity); 14V erase-rail chip-OUT VPP multimeter dry-run FIRST (`autonomous: false`); then seated `firestarter write` (no `-b`) + independent post-write read SHA-match + non-vacuous wrong-file negative control |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-06-22

---

## Validation Audit 2026-06-22

All 7 automatable per-task verifications confirmed present and green (live run); the single
ERASE-02 row is genuinely hardware-bound and bench-proven (77-04: clean no-`-b`
write→auto-erase→program→verify on Leonardo W27C512, readback SHA match, non-vacuous wrong-file
negative control). Full suite green, 77.79% coverage (≥70), check_dispatch.py PASS. No gaps to
fill — phase is Nyquist-compliant.

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
| Automated (green) | 7 |
| Manual-only (bench-proven) | 1 |
