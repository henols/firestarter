---
phase: 60
slug: display-layer-decode-correctness
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-10
---

# Phase 60 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> All validation is board-independent — `firestarter info` is pure host-side code (confirmed
> running in the devcontainer with no Arduino attached).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x + syrupy (snapshots) |
| **Config file** | `firestarter_app/pyproject.toml` (pytest section) |
| **Quick run command** | `pytest tests/test_eprom_info.py -x -q` |
| **Full suite command** | `pytest --cov=firestarter --cov-fail-under=70 -q` |
| **Estimated runtime** | ~10–20 seconds |

> Run all commands from `firestarter_app/`. If the toolchain is wiped, restore with
> `pip install -e '.[test]'` (use the `/usr/local` python, not the foreign `.venv/`).

---

## Sampling Rate

- **After every task commit:** `pytest tests/test_eprom_info.py tests/test_characterization.py -q`
- **After every plan wave:** `ruff check firestarter/ && ruff format --check firestarter/ && pytest --cov-fail-under=70 -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** ~20 seconds

---

## Per-Task Verification Map

| Item | Decision | Behavior to prove | Test Type | Automated Command | File Exists | Status |
|------|----------|-------------------|-----------|-------------------|-------------|--------|
| Erasable bit fires for EEPROM | D-03 | `_map_data("W27C512")` → `info-flags & 0x10 != 0` | unit | `pytest tests/test_eprom_database.py -k erasable -x` | ❌ W0 | ⬜ pending |
| Type label from electrical.type | D-01 | synthetic EEPROM (proto=0x07) → Type shows EEPROM, not UV-EPROM | unit (synthetic) | `pytest tests/test_eprom_info.py -k synthetic -x` | ❌ W0 | ⬜ pending |
| Can-erase from electrical.type | D-02 | EEPROM → electrically-erasable msg; UV-EPROM → UV-only; SRAM → row omitted | unit (synthetic) | `pytest tests/test_eprom_info.py -k synthetic -x` | ❌ W0 | ⬜ pending |
| 0x10 flags_info label | D-07 | `_interpret_flags(0x10)` → electrically-erasable text (not "needs SWE") | unit | `pytest tests/test_eprom_info.py -k interpret_flags -x` | ❌ W0 | ⬜ pending |
| VPP shown for 12V chips | D-07 | W27C512 `output_data` contains a VPP value (sourced from `vpp_mv`/`vpp_volts`) | unit/smoke | in smoke assertions | ❌ W0 | ⬜ pending |
| verified_str removed | D-05 | `output_data` / rendered output never contains `-- NOT VERIFIED --` | unit | in synthetic test | ❌ W0 | ⬜ pending |
| EEPROM display set | SC-1 | W27C512 / SST27VF512 / SST27SF512 / W27C257 → EEPROM + electrically erasable | parametrized real-DB smoke | `pytest tests/test_eprom_info.py -k type_label_and_erase_smoke -x` | ❌ W0 | ⬜ pending |
| UV-EPROM control set | SC-2/SC-3 | M27C512 / 27C256 / 2764 → UV-EPROM + UV-only (no regression) | parametrized real-DB smoke | same as above | ❌ W0 | ⬜ pending |
| info never crashes | D-06 | full `prepare_detailed_eprom_data` happy-path runs for all smoke chips | smoke (no-crash) | covered by smoke set | ❌ W0 | ⬜ pending |
| Snapshot non-regression | D-01/02/05/07 | `firestarter info W27C512` matches the UPDATED snapshot (correct EEPROM output) | subprocess snapshot | `pytest tests/test_characterization.py::test_info_known_chip` | ✅ (must UPDATE) | ⬜ pending |
| Existing tests green | — | 534+ existing tests pass | suite | `pytest -q` | ✅ | ⬜ pending |
| Ruff clean | — | no lint/format issues | lint | `ruff check firestarter/ && ruff format --check firestarter/` | ✅ | ⬜ pending |
| Coverage floor | — | total coverage ≥ 70% (baseline 75.65%) | coverage | `pytest --cov-fail-under=70` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

No new test *files* are strictly required — the `db` and `presenter` fixtures
(`EpromDatabase(skip_local_override=True)`) already exist at module scope in
`tests/test_eprom_info.py` and should be reused.

- [ ] Synthetic fixtures (one per `electrical.type`: EEPROM, UV-EPROM, Flash/EEPROM, SRAM) in `tests/test_eprom_info.py` — minimal raw-config + mapped-data dicts (designs in RESEARCH.md §Synthetic Fixture Design)
- [ ] Parametrized real-DB smoke test `test_type_label_and_erase_smoke` in `tests/test_eprom_info.py` (EEPROM set + UV-EPROM control set)
- [ ] D-03 erasable-bit unit assertion in `tests/test_eprom_database.py`
- [ ] (Optional) thin `tests/test_ic_layout.py` for `_interpret_flags` — or fold into `test_eprom_info.py` (planner's call)

---

## Manual-Only Verifications

| Behavior | Why Manual | Test Instructions |
|----------|------------|-------------------|
| (none) | — | All Phase 60 behaviors have automated host-side verification — no hardware required |

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (synthetic fixtures + smoke set + erasable-bit unit)
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `test_info_known_chip` snapshot updated to corrected EEPROM output (regression canary, not a constraint)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
