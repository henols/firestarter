---
phase: 94
slug: fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-page-size
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-27
---

# Phase 94 — Validation Strategy

> Per-phase validation contract. Phase 94 ships real firmware + host code (T-93-CANERASE fix, boot-block detection, per-chip page_size). FIX-01's original "program page 0" claim is hardware-blocked (Phase 93 — locked boot block); validation here proves the *software* corrections are right + the writable region works. See `94-RESEARCH.md` § "Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Firmware framework** | PlatformIO native (`pio test -e native` from `/workspaces/firestarter`); flash4 suite `test_val_flash4` + golden traces + dispatch-mirror guard |
| **Host framework** | pytest (`pip install -e '.[test]'` from `/workspaces/firestarter_app`); diff_db + check_dispatch run as pytest gates (`test_diff_db_gate.py`, `test_check_dispatch_invariants.py`) |
| **Lint/type gates** | ruff check + ruff format --check + mypy — validate against **py3.11** (devcontainer 3.12 MASKS py3.11 failures) |
| **Quick run command** | `pio test -e native -f "*test_val_flash4*"` (firmware) / `pytest -q` (host) |
| **Full suite command** | `pio test -e native` + `pytest` + `ruff check` + `ruff format --check` + `mypy` |
| **Bench proof** | writable-region (0x4000+) write→read→verify byte-exact on the seated W29C040 (Leonardo + Rev 2.0, /dev/ttyACM0) |

---

## Sampling Rate

- **After every task commit:** Run the relevant quick suite (`pio test -e native -f "*flash4*"` for firmware tasks; `pytest -q` for host tasks).
- **After every wave:** Full firmware + host suite + ruff/mypy (py3.11) green.
- **Before phase verification:** diff_db shows only intended `page_size` additions; check_dispatch passes; constants parity (constants.py ↔ firestarter.h) green.
- **Max feedback latency:** native tests ~1s; pytest seconds; bench proof one cycle.

---

## Per-Task Verification Map

| Task area | Requirement | Test / Evidence | Test Type | Pass Condition | Status |
|-----------|-------------|-----------------|-----------|----------------|--------|
| T-93-CANERASE host fix | FIX-01 / SAFE-02 | host test: `convert_to_programmer` does NOT set FLAG_CAN_ERASE for algorithm==5 (5V flash4) | pytest | flags for W29C040 = 0x00 (no 0x02); existing 0x07/EEPROM unchanged | ⬜ pending |
| T-93-CANERASE fw guard | FIX-01 | native: flash4 write/erase path asserts NO CTRL_VPP_* bits for protocol 0x05 | pio native | `test_flash4_*_no_vpp` green incl. erase path | ⬜ pending |
| Boot-block detection | FIX-01 | native: ID-mode detect read of 0x00002 returns lock verdict; host surfaces clear "boot block locked" error instead of cryptic timeout | pio native + pytest | locked-region write-timeout yields boot-block-locked diagnostic | ⬜ pending |
| Golden traces / guard | FIX-02 | flash4 golden register traces + dispatch-mirror guard | pio native | green (or re-pinned with cited rationale) | ⬜ pending |
| Native write-path tests | FIX-03 | page-0 + page-boundary native coverage of corrected paths | pio native | green; lockstep where it crosses the wire | ⬜ pending |
| Per-chip page_size DB | PGSZ-01 | `build_db.py` / chip DB carries datasheet-sourced `page_size` (W29C040=256, W29C020=128 cited; heuristic fallback for unconfirmed) | pytest + diff_db | diff_db shows only intended page_size additions | ⬜ pending |
| Firmware consumes page_size | PGSZ-02 | firmware uses `handle->page_size ? : flash4_page_size(mem_size)` | pio native | per-chip value consumed; heuristic = fallback | ⬜ pending |
| page_size over the wire | PGSZ-03 | lockstep field constants.py ↔ firestarter.h ↔ json_parser; safe default when absent | pytest + native | constants parity green; check_dispatch passes | ⬜ pending |
| CI py3.11 + safety | SAFE-02 | ruff/format/mypy/diff_db/check_dispatch green on py3.11; over-voltage blocked; host guard not bypassed | CI gates | all green against py3.11 target | ⬜ pending |
| Writable-region proof | FIX-01 (demo) | bench write→read→verify byte-exact on 0x4000+ | manual (bench) | SHA match on the writable region | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red*

---

## Wave 0 Requirements

- [ ] Confirm `test_val_flash4` native suite builds + runs (`pio test -e native -f "*test_val_flash4*"`) as the baseline.
- [ ] Confirm host test env restored (`pip install -e '.[test]'`) and `pytest -q` green pre-change.
- [ ] Establish the py3.11 validation recipe (don't trust devcontainer 3.12 for ruff/codegen).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Writable-region write→verify byte-exact | FIX-01 (demonstration) | Requires seated W29C040 on Leonardo + Rev 2.0 | `firestarter write` a fixed image into 0x4000+, read back, SHA-compare |
| Boot-block-locked diagnostic on real chip | FIX-01 | Requires the locked chip | write into 0x0–0x3FFF → expect clear boot-block-locked message (post-fix) |

*BENCH-01 full-image graduation is NOT validatable on this chip (locked boot block) — deferred to a different W29C040 sample (Phase 95, operator-gated).*

---

## Validation Sign-Off

- [ ] Every requirement (FIX-01/02/03, PGSZ-01/02/03, SAFE-02) maps to an automated test or a documented hardware-blocked deferral
- [ ] T-93-CANERASE fix proven: W29C040 wire flags carry no FLAG_CAN_ERASE; firmware asserts no 12V on 0x05
- [ ] page_size: diff_db shows only intended additions; constants parity green; heuristic fallback preserved
- [ ] CI green on py3.11 (not just devcontainer 3.12)
- [ ] FIX-01 page-0 limitation documented as hardware-blocked (not faked)
- [ ] `nyquist_compliant: true` set once the map is green

**Approval:** pending
