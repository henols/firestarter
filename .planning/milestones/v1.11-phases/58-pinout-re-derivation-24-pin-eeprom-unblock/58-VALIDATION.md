---
phase: 58
slug: pinout-re-derivation-24-pin-eeprom-unblock
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-08
---

# Phase 58 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from 58-RESEARCH.md § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (installed via `pip install -e '.[test]'` from `firestarter_app/`) |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `python3 -m pytest tests/test_decoder.py -x -q` |
| **Full suite command** | `python3 -m pytest -q` (~480 tests currently) |
| **Estimated runtime** | ~30 seconds full suite; <5s quick |

> Run all commands from `firestarter_app/`. Per memory: use the `/usr/local` python toolchain; restore with `pip install -e '.[test]'` if wiped.

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/test_decoder.py -x -q`
- **After every plan wave:** Run `python3 -m pytest -q && python3 tools/check_dispatch.py`
- **Before `/gsd-verify-work`:** Full suite (480+) green AND GATE-03 (`check_dispatch.py`) returns 0 violations.
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| W0 | 00 | 0 | PIN-01/02/03 | T-58-01 | Tests assert no VPP-on-wrong-pin dispatch for any 24-pin EEPROM | unit | `python3 -m pytest tests/test_decoder.py -x` | ❌ W0 | ⬜ pending |
| — | — | 1 | PIN-01 | — | `resolve_pinout_key` returns correct key per (pin_count, pm_idx, variant_lo) | unit | `pytest tests/test_decoder.py::TestResolvedPinoutKey -x` | ❌ W0 | ⬜ pending |
| — | — | 1 | PIN-01 | — | Guess tables not importable/referenced | unit | `pytest tests/test_decoder.py::TestGuessTablesDeleted -x` | ❌ W0 | ⬜ pending |
| — | — | 1 | PIN-02 | T-58-01 | WARNING-5 fires for 5V erasable + proto=0x07 → 0x0D | unit | `pytest tests/test_decoder.py::TestWarning5Rule -x` | ❌ W0 | ⬜ pending |
| — | — | 2 | PIN-02 | T-58-01 | GATE-03 returns 0 violations after DB regen | integration | `python3 tools/check_dispatch.py` | ✅ exists | ⬜ pending |
| — | — | 2 | PIN-03 | T-58-01 | AT28C16 in DB with algo=0x0D + 24-pin EEPROM pinout | integration | `firestarter info AT28C16` | runs after install | ⬜ pending |
| — | — | 2 | PIN-03 | T-58-01 | The 10 already-dangerous 24-pin EEPROMs (AM28C16A/X2816A/XL2804A …) fixed to algo=0x0D + DIP24_2816 | integration | `pytest tests/test_decoder.py::TestDangerous24pinEEPROMFixed -x` | ❌ W0 | ⬜ pending |
| — | — | 1 | PIN-03 | T-58-01 | DIP24_2816 in pinouts.json, no `vpp-pin`, rw=21/oe=20/ce=18 | unit | `pytest tests/test_decoder.py::TestDIP24_2816Pinout -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_decoder.py::TestResolvedPinoutKey` — unit tests for representative (pin_count, pm_idx, variant_lo) combinations (DIP24_2732/2716/2816/6116, DIP28_27512/27256/2764/28C256/28C64, DIP32 std + EEPROM variants).
- [ ] `tests/test_decoder.py::TestGuessTablesDeleted` — assert `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`, `DIP28_VARIANT_MAP` are absent from `tools.build_db`.
- [ ] `tests/test_decoder.py::TestWarning5Rule` — assert WARNING-5 still fires (5V erasable + proto=0x07 → 0x0D).
- [ ] `tests/test_decoder.py::TestDIP24_2816Pinout` — assert `DIP24_2816` present, no `vpp-pin`, `rw-pin=[21]`, `ce-pin=[18]`, `oe-pin=[20]`.
- [ ] `tests/test_decoder.py::TestDangerous24pinEEPROMFixed` — integration: assert the 10 previously-dangerous 24-pin EEPROMs land on algo=0x0D + DIP24_2816 in the regenerated DB (the RESEARCH scope-expansion finding).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real-hardware write/program of AT28C04/16 EEPROMs | PIN-03 | BENCH-01 deferred to v2 per REQUIREMENTS.md — milestone closes on source-correctness | Out of scope; recorded so the bench gap isn't mistaken for completeness |
| SR-1 datasheet cross-check of DIP24_2816 pin assignment | PIN-03 / SC#4 | Datasheet read is a human judgement against AT28C16/AT28C04 docs | Complete the SR-1 checklist (D-10/D-11): vpp-pin absent, rw=WE pin, oe/ce correct, all 24 pins accounted for |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
