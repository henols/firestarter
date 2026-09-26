---
phase: 108
slug: test-plan-engine-address-derived-pattern-fingerprint
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-02
---

# Phase 108 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (firestarter_app) |
| **Config file** | firestarter_app/pyproject.toml (`[tool.pytest.ini_options]`) |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/test_chip_test.py -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run the task's quick command (`tests/test_chip_test.py` or `tests/test_error_code_seam.py`)
- **After every plan wave:** Run `cd firestarter_app && python -m pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green + `ruff check` / `ruff format --check` clean
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 108-01-01 | 01 | 1 | RPT-03 | T-108-01 | Optional `error_code` kwarg, backward-compatible | unit | `cd firestarter_app && python -c "from firestarter.exceptions import EpromOperationError as E; assert E('x', error_code=164).error_code==164; assert E('x').error_code is None"` | ❌ W1 (108-01 T3) | ⬜ pending |
| 108-01-02 | 01 | 1 | RPT-03 | T-108-02 | `_raise_for_error_response` threads `response.id` | unit | `cd firestarter_app && python -m pytest tests/test_error_code_seam.py -q` | ❌ W1 (108-01 T3) | ⬜ pending |
| 108-01-03 | 01 | 1 | RPT-03 | T-108-03 | N/A | unit | `cd firestarter_app && python -m pytest tests/test_error_code_seam.py -q` | ❌ W1 (this task) | ⬜ pending |
| 108-02-01 | 02 | 1 | PATT-01 | T-108-04 | Region-parameterized XOR-fold pattern + pre-pass | unit | `cd firestarter_app && python -c "from firestarter.chip_test import generate_pattern as g; assert g(0x8000,16)!=g(0,16); assert len(g(0,16))==16"` | ❌ W1 (108-02 T3) | ⬜ pending |
| 108-02-02 | 02 | 1 | PATT-02 | T-108-05 | Shared byte-diff helper (reuse consistency divergence math) | unit | `cd firestarter_app && python -m pytest tests/test_chip_test.py -q` | ❌ W1 (108-02 T3) | ⬜ pending |
| 108-02-03 | 02 | 1 | PATT-02 | T-108-06 | 4-bucket classifier incl. honest `indeterminate` fallback | unit | `cd firestarter_app && python -m pytest tests/test_chip_test.py -q` | ❌ W1 (this task) | ⬜ pending |
| 108-03-01 | 03 | 2 | SWEEP-01 | T-108-07 | Derivation reads DB via guard-bypassing `get_eprom`/`convert_to_programmer` | unit | `cd firestarter_app && python -m pytest tests/test_chip_test.py -q` | ✅ | ⬜ pending |
| 108-03-02 | 03 | 2 | SWEEP-01 | T-108-08 | Protocol-driven op inclusion (id-first, NA rules) | unit | `cd firestarter_app && python -m pytest tests/test_chip_test.py -q` | ✅ | ⬜ pending |
| 108-04-01 | 04 | 3 | SWEEP-02, RPT-03 | T-108-09/10 | Non-fatal per-step executor + `error_code` capture | unit | `cd firestarter_app && python -m pytest tests/test_chip_test.py -q` | ✅ | ⬜ pending |
| 108-04-02 | 04 | 3 | SWEEP-03 | T-108-11/12 | id-first chip-ID mismatch hard-gates destructive steps (chip pristine) | unit | `cd firestarter_app && python -m pytest tests/test_chip_test.py -q` | ✅ | ⬜ pending |
| 108-04-03 | 04 | 3 | SWEEP-04 | T-108-13/SC | N≥2 `marginal` on disagreement + write-step fingerprint wiring | unit | `cd firestarter_app && python -m pytest tests/test_chip_test.py -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*File Exists: ✅ = analog/target already on disk · ❌ W1 = test file created during Wave 1 execution (noted plan/task that creates it)*

---

## Wave 0 Requirements

No separate Wave 0 is required — the pytest framework and fixtures already exist in `firestarter_app/tests/` (`make_app_context()` / `Mock(spec=EpromOperator)` in `test_validate_family_cmd.py`; the `_operation_context`/`_run_state_machine` monkeypatch in `test_consistency_check.py`). The two new test files are created co-located with their code inside Wave 1:

- [x] `firestarter_app/tests/test_error_code_seam.py` — created by **108-01 Task 3** (covers RPT-03)
- [x] `firestarter_app/tests/test_chip_test.py` — created by **108-02 Task 3** (covers PATT-01/02; extended by 108-03 and 108-04 for SWEEP-01/02/03/04)

*Existing infrastructure covers all phase requirements; no framework install or shared-fixture stubs are outstanding.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | Engine is fully bench-free this phase (mock operator + `EpromDatabase(skip_local_override=True)`) | All phase behaviors have automated verification. |

*All phase behaviors have automated verification. (Live-bench validation against physical chips is a downstream concern — this phase's engine is unit-tested only.)*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none outstanding — test files created in-plan during Wave 1)
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-07-02
