---
phase: 79
slug: 25v-nmos-ceiling-raise
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-22
---

# Phase 79 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `79-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.0 |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter_app && python3 -m pytest tests/test_build_db_inclusion.py tests/test_chip_resolver.py tests/test_check_dispatch_invariants.py -v` |
| **Full suite command** | `cd firestarter_app && python3 -m pytest --cov --cov-fail-under=70` |
| **VPP-safety gate** | `cd firestarter_app && python3 tools/check_dispatch.py` |
| **Lint gate** | `cd firestarter_app && ruff check --target-version py39 . && ruff format --check --target-version py39 .` |
| **Estimated runtime** | ~30 seconds (quick), ~90 seconds (full + coverage) |

> Devcontainer runs Python 3.12; CI targets py39/3.11. Always validate ruff with `--target-version py39` before claiming CI-green (3.12-masks-CI trap).

---

## Sampling Rate

- **After every task commit:** Run quick command + `ruff check --target-version py39 .`
- **After every plan wave:** Run full suite + `python3 tools/check_dispatch.py` + `ruff check/format --target-version py39`
- **Before `/gsd-verify-work`:** Full suite green + `check_dispatch.py` PASS
- **Max feedback latency:** ~90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| dry-run | 01 | 1 | NMOS-01 | T-79-VPP | Shield produces ≥25V at socket VPP pin (chip-OUT); measured V + silkscreen rev recorded BEFORE ceiling change | hardware/manual | `firestarter -p <port> vpp` + multimeter | N/A | ⬜ pending |
| ceiling | 02 | 2 | NMOS-02 | T-79-CEIL | `RURP_VPP_CEILING_MV == 25000` | unit | `python3 -c "from tools.build_db import RURP_VPP_CEILING_MV; assert RURP_VPP_CEILING_MV == 25000"` | ✅ after edit | ⬜ pending |
| invariant | 02 | 2 | NMOS-02 | T-79-CEIL | `_FAMILY_VPP_INVARIANTS["configure_eprom"] == (0, 25000)`; 25V vpp not a violation | unit | `pytest tests/test_check_dispatch_invariants.py::test_configure_eprom_with_25v_vpp_is_not_a_violation -x` | ❌ W0 | ⬜ pending |
| reclassify | 02 | 2 | NMOS-02 | — | 4 NMOS chips reclassify `supported` with `vpp_mv=25000`; 0 `vpp-exceeds-max` remain | unit | `pytest tests/test_build_db_inclusion.py::TestNmosVppCorrection -v` | ❌ W0 | ⬜ pending |
| db-gate | 02 | 2 | NMOS-02 / SAFE-02 | T-79-GATE | full-DB VPP-safety gate green at new ceiling | integration | `python3 tools/check_dispatch.py` | ✅ | ⬜ pending |
| exemplar-fix | 02 | 2 | NMOS-02 | — | 7 broken tests updated to X88C64P/AT28C16 exemplar | unit | `pytest tests/test_build_db_inclusion.py tests/test_chip_resolver.py tests/test_cli_handlers.py -v` | ❌ W0 | ⬜ pending |
| resolve | 03 | 3 | NMOS-03 | — | `resolve_chip("M2716")` succeeds (no refusal) post-graduation | unit | `pytest tests/test_chip_resolver.py::test_resolve_chip_nmos_graduated_resolves -x` | ❌ W0 | ⬜ pending |
| parity | 03 | 3 | SAFE-03 | — | firmware↔host parity green (no FLAG_* touched) | unit | `pytest tests/test_revision_constants_parity.py -v` | ✅ | ⬜ pending |
| bench-write | 03 | 3 | NMOS-03 | T-79-BENCH | write+verify on Leonardo, SHA match + non-vacuous negative control, R1/R2 reconcile recorded | hardware/bench | manual — Leonardo + NMOS chip + SHA | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_build_db_inclusion.py` — rewrite `test_nmos_vpp_exceeds_max` → `test_nmos_graduated_to_supported`; add `test_zero_vpp_exceeds_max_chips_remain`; replace M2716 with X88C64P/AT28C16 in `test_vpp_exceeds_max_reason_*`
- [ ] `tests/test_chip_resolver.py` — update two tests using M2716 as `vpp-exceeds-max`; add `test_resolve_chip_nmos_graduated_resolves`
- [ ] `tests/test_cli_handlers.py` — update three tests using M2716 as `vpp-exceeds-max` / refusal exemplar
- [ ] `tests/test_check_dispatch_invariants.py` — add `test_configure_eprom_with_25v_vpp_is_not_a_violation`

*These are test-update gaps caused by the `vpp-exceeds-max` category becoming empty after graduation — they must land in the same wave as the ceiling change so the suite never goes red across a wave boundary.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Shield produces ≥25V at socket VPP pin | NMOS-01 | No runtime VPP enforcement in firmware; only a physical multimeter can confirm the boost converter + R1/R2 calibration actually delivers 25V | Chip OUT. Hold VPP rail (`firestarter -p <port> vpp` / dev-reg hold per bench tooling). Probe socket VPP pin with DMM. Record measured V + silkscreen shield rev. Must read ≥25V before any ceiling change. |
| Write + verify on real NMOS chip | NMOS-03 | Requires Leonardo + physical 25V EPROM + shield Rev 2.0/2.2 (NOT Rev 0) | Insert NMOS chip on Leonardo. Write a known image, independent read-back, SHA-match. Include a non-vacuous negative control. Record live R1/R2 reconcile. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies (2 manual-only, hardware-gated — `autonomous: false`)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter (after planner wires automated verify into every code task)

**Approval:** pending
