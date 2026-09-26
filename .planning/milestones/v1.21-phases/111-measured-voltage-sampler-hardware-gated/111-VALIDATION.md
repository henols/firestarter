---
phase: 111
slug: measured-voltage-sampler-hardware-gated
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-03
---

# Phase 111 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: 111-RESEARCH.md § Validation Architecture (HIGH confidence).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (+ coverage gate `--cov-fail-under=70`, CI-enforced) |
| **Config file** | `firestarter_app/pyproject.toml` (pytest + ruff + mypy); CI `.github/workflows/ci.yml` |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/test_hardware.py -x -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest -q` |
| **Estimated runtime** | ~10 seconds (host-only unit tests; synthetic frames, no hardware) |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && python -m pytest tests/test_hardware.py tests/test_diagnostic_report.py -x -q`
- **After every plan wave:** Run `cd firestarter_app && python -m pytest -q` (full suite) + `ruff check` + `ruff format --check` + `mypy` (note: `hardware.py` is not in the strict-8 mypy set today; **if the planner chooses Pattern B**, `serial_comm.py`/`frame_parser.py`/`codec.py` ARE strict-mypy — budget for it)
- **Before `/gsd-verify-work`:** Full suite green + coverage ≥ 70; SC2 recorded as deferred HUMAN-UAT/FUT (D-05)
- **Max feedback latency:** ~10 seconds

---

## Per-Task Verification Map

> Task/Plan IDs are assigned by the planner; the nyquist-auditor fills them and the Status column during execution. Rows below are the required verifications derived from RESEARCH § Phase Requirements → Test Map (all VOLT-01, all bench-free with synthetic `build_frame(0xE4|0xE5, struct.pack(">HHHH", ...))` frames).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (planner) | (planner) | 0 | VOLT-01 | T-111-INPUT (V5) | `_parse_voltage_frame("VPP: 20.9V, ...")` → `20900` (v_int*1000 + v_dec*100) | unit | `pytest tests/test_hardware.py -k parse_voltage -x` | ❌ W0 | ⬜ pending |
| (planner) | (planner) | 0 | VOLT-01 | — | `sample_vpp_mv()` returns median mV from N synthetic 0xE4 frames (state 11) | unit | `pytest tests/test_hardware.py -k sample_vpp -x` | ❌ W0 | ⬜ pending |
| (planner) | (planner) | 0 | VOLT-01 | — | `sample_vpe_mv()` uses state 12, parses 0xE5 | unit | `pytest tests/test_hardware.py -k sample_vpe -x` | ❌ W0 | ⬜ pending |
| (planner) | (planner) | 0 | VOLT-01 | T-111-INPUT (V5) | transport error / no DATA frame / no-parse → returns `None` (never a false `0`) | unit | `pytest tests/test_hardware.py -k sample_none -x` | ❌ W0 | ⬜ pending |
| (planner) | (planner) | 0 | VOLT-01 | — | median of even N + off-grid handling (Pitfall 5); `int` cast | unit | `pytest tests/test_hardware.py -k median -x` | ❌ W0 | ⬜ pending |
| (planner) | (planner) | 0 | VOLT-01 | T-111-DRIFT | 0xE4/0xE5 `CATALOG` format still matches the parser regex (Pitfall 3 guard) | unit | `pytest tests/test_hardware.py -k format_pin -x` | ❌ W0 | ⬜ pending |
| (planner) | (planner) | 1 | VOLT-01 / SC3 | — | `read_vpp_voltage`/`read_vpe_voltage`/`_read_voltage_loop` UNCHANGED (existing tests still green) | regression | `pytest tests/test_hardware.py -q` | ✅ `tests/test_hardware.py:74-120` | ⬜ pending |
| (planner) | (planner) | 1 | VOLT-01 / D-01 | — | split report fields serialize; `None` → `NOT_MEASURED` in single-source `to_dict()` | unit | `pytest tests/test_diagnostic_report.py -k voltage -x` | ❌ W0 | ⬜ pending |
| — | — | — | SC2 | — | parsed mV == printed monitor value on real hardware | **manual (deferred)** | operator bench UAT — Leonardo + RURP Rev 2.0 (D-05) | manual-only | 🔒 deferred FUT |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky · 🔒 deferred*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_hardware.py` — add sampler parse / median / timeout / format-pin tests using `build_frame(0xE4|0xE5, struct.pack(">HHHH", ...))` + `fake_serial.feed` + patched `find_and_connect` (harness already exists at `tests/test_hardware.py:44-120` and `tests/conftest.py:52`).
- [ ] `firestarter_app/tests/test_diagnostic_report.py` — add split-field (VPP/VPE before/after/standalone) serialization + `NOT_MEASURED` fallback tests.
- [ ] No framework install needed — pytest + conftest fixtures (`build_frame`, `fake_serial`, `make_comm`) already present.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Parsed mV == printed `firestarter vpp`/`vpe` monitor value on real silicon | SC2 (VOLT-01) | Requires energizing the real VPP/VPE regulator and reading the ADC — cannot be exercised without hardware (D-05 single hardware gate, deferred to a bench session as HUMAN-UAT/FUT) | Leonardo + RURP Rev 2.0 (standing bench oracle). Standalone read: compare `sample_vpp_mv()`/`sample_vpe_mv()` against the live `firestarter vpp`/`vpe` monitor with any chip seated (no write, no consumption). Before/after write path: use an electrically-erasable chip (W27C512 / W29C020). Standing bench discipline: live R1/R2 readback + verify `controller:` port identity per task; Leonardo is chip-OUT-sideload-exempt. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
