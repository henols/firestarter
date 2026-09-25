---
phase: "202"
slug: "one-comparison-engine-on-the-host"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-09-24"
---

# Phase 202 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Reconstructed retroactively (State B) on 2026-09-24 from the five PLAN/SUMMARY pairs, `202-VERIFICATION.md` and `202-SECURITY.md`. Every command below was re-run against the live `firestarter_app` tree at `5302f63`, 54 commits after the phase-202 verification anchor `a0855b9`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Python 3.11, `firestarter_app/.venv311`), plus mypy and ruff |
| **Config file** | `firestarter_app/pyproject.toml` (addopts `-ra -q`, so pass `-o addopts=""` to get the count line) |
| **Quick run command** | `cd firestarter_app && .venv311/bin/python -m pytest tests/test_compare.py tests/test_eprom_operations.py tests/test_cli_handlers.py -o addopts="" -q` |
| **Full suite command** | `cd firestarter_app && .venv311/bin/python -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70 -q` |
| **Estimated runtime** | ~130 s for the phase-scoped set (718 tests), ~190 s for the full suite |

---

## Sampling Rate

- **After every task commit:** Run the quick run command
- **After every plan wave:** Run the full suite command
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 190 seconds

---

## Per-Task Verification Map

All paths are relative to `firestarter_app/`. `pytest` stands for `.venv311/bin/python -m pytest -o addopts="" -q`.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 202-01-01 | 01 | 1 | CMP-07 | — | D-10 exit contract confirmed by the operator (`confirm-d10`) | checkpoint:decision | — (decision gate, no code) | n/a | ✅ green |
| 202-01-02 | 01 | 1 | CMP-01, CMP-05 | T-202-01 | `verify` sends `COMMAND_READ`, compares on host; `compare.py` import-pure (D-01) | unit + AST | `pytest tests/test_compare.py tests/test_eprom_operations.py` · `pytest tests/test_compare.py::TestImportPurity` · `TestVerifyEpromHostSideRead` | ✅ | ✅ green |
| 202-01-03 | 01 | 1 | CMP-07 | — | `dev test` OP_VERIFY keeps pass/fail meaning across the bool→int change | unit | `pytest tests/test_chip_test.py tests/test_chip_test_cycle.py tests/test_dev_test_cmd.py tests/test_devtest_firmware_error_propagation.py` | ✅ | ✅ green |
| 202-02-01 | 02 | 2 | CMP-03 | T-202-01 | Peak traced allocation < 1 MiB, flat in device size | unit (tracemalloc) | `pytest tests/test_compare.py::TestCompareAccumulatorPeakAllocation` | ✅ | ✅ green |
| 202-02-02 | 02 | 2 | CMP-03 | T-202-05 | Clean compare < 1 s, all-differing < 8 s; fast path precedes per-offset loop | unit + AST | `pytest tests/test_compare.py::TestCompareAccumulatorRuntime tests/test_compare.py::TestCompareAccumulatorFastPathStructure` | ✅ | ✅ green |
| 202-02-03 | 02 | 2 | CMP-03, CMP-05 | T-202-02 | Coalescing, ordering, empty/single-byte, cap boundary, exact `extra_*` counters | unit | `pytest tests/test_compare.py -k "Adjacency or Ordering or EmptyAndSingleByte or RangeCapBoundary or AlternatingPrecision"` | ✅ | ✅ green |
| 202-03-01 | 03 | 3 | CMP-06 | T-202-06 | Streamed finalisation reproduces the batch `Fingerprint` shape | unit | `pytest tests/test_compare.py::TestClassifyStreamed tests/test_compare.py::TestDiffSummary` | ✅ | ✅ green |
| 202-03-02 | 03 | 3 | CMP-06 | T-202-06 | `classify_fingerprint` delegates; `_diff_offsets` retired | unit + corpus | `pytest tests/test_compare.py::TestClassifyFingerprintCorpus` · `python -c "import firestarter.chip_test as c; assert not hasattr(c, '_diff_offsets')"` | ✅ | ✅ green |
| 202-03-03 | 03 | 3 | CMP-06 | T-202-07 | Exactly one D-14 bucket line after the range lines | unit + CLI | `pytest tests/test_compare.py::TestRenderCompareLines tests/test_compare.py::TestFinaliseAlwaysClassifies tests/test_cli_handlers.py::test_verify_cli_prints_range_line_and_bucket_summary_line` | ✅ | ✅ green |
| 202-04-01 | 04 | 4 | CMP-04 | — | Additive `abort_predicate=None` seam; existing callers unchanged | unit + signature | `pytest tests/test_eprom_operations.py tests/test_consistency_check.py` · signature check on `_main_phase_read_data` | ✅ | ✅ green |
| 202-04-02 | 04 | 4 | CMP-04 | T-202-04, T-202-08, T-202-09 | Stop at first mismatch; abort never read as a fault (4-condition acceptance, window edges pinned); port clean after abort | unit | `pytest tests/test_eprom_operations.py::TestVerifyEpromReadAbort` | ✅ | ✅ green |
| 202-04-03 | 04 | 4 | CMP-04 | T-202-08 | First/last-byte, zero-length, coalesced-run boundaries; written answer recorded | unit + doc grep | `pytest tests/test_eprom_operations.py::TestVerifyEpromReadAbort` · `grep -q temporal 202-READ-ABORT-ANSWER.md && grep -q 202-READ-ABORT-ANSWER.md .planning/ROADMAP.md` | ✅ | ✅ green |
| 202-05-01 | 05 | 5 | CMP-02 | T-202-01 | `blank` runs through the one engine; expected side is a chunk-sized pull callback | unit | `pytest tests/test_eprom_operations.py::TestCheckEpromBlankHostSideRead tests/test_eprom_operations.py::TestCheckEpromBlankSharesTheOneCompareDrive tests/test_eprom_operations.py::TestBlankExpectedBytesPullCallback tests/test_chip_test_blank_check_order.py tests/test_erase_blank_step_nonregression.py` | ✅ | ✅ green |
| 202-05-02 | 05 | 5 | CMP-08, CMP-07 | T-202-11, T-202-12 | `-a/--address` and `-s/--size`; refusals fire before the port opens; wire bounds exact region | CLI | `pytest tests/test_cli_handlers.py -k "refus or region or chip_end"` | ✅ | ✅ green |
| 202-05-03 | 05 | 5 | CMP-01, CMP-02, CMP-07 | T-202-10 | Ordinals 4/6 never composed; 0/1/2 matrix; `map_typed_errors` unchanged | unit + CLI | `pytest tests/test_eprom_operations.py::TestOrdinalsNeverSentByVerifyOrBlank tests/test_cli_handlers.py -k "happy_path or mismatch or setup_failure or map_typed_errors or exit"` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Requirement coverage

| Requirement | Covering tasks | Status |
|---|---|---|
| CMP-01 | 202-01-02, 202-05-03 | COVERED |
| CMP-02 | 202-05-01, 202-05-03 | COVERED |
| CMP-03 | 202-02-01, 202-02-02, 202-02-03 | COVERED |
| CMP-04 | 202-04-01, 202-04-02, 202-04-03 | COVERED |
| CMP-05 | 202-01-02, 202-02-03 | COVERED |
| CMP-06 | 202-03-01, 202-03-02, 202-03-03 | COVERED |
| CMP-07 | 202-01-01, 202-01-03, 202-05-02, 202-05-03 | COVERED |
| CMP-08 | 202-05-02 | COVERED |

### Superseded verify legs (a later phase changed the code, no Phase 202 gap)

- **202-05-03 "ordinals still defined" leg.** It imports `COMMAND_BLANK_CHECK` and `COMMAND_VERIFY` from `firestarter.constants`. That import now fails with `ImportError`, because Phase 204 removed both constants on purpose. The requirement this leg protected is that neither ordinal ever reaches the wire. `TestOrdinalsNeverSentByVerifyOrBlank` still proves that, and it now asserts the integer literals 4 and 6 directly, so no constant is needed. Do not restore this leg.
- **WR-01 (the abort-window boundary was untested at verification time).** This is now closed. `TestVerifyEpromReadAbort` holds three tests that fake `time.monotonic`: `test_timeout_just_inside_the_acceptance_window_is_the_intended_abort`, `test_timeout_exactly_at_the_acceptance_window_is_the_intended_abort` and `test_timeout_outside_the_acceptance_window_returns_two`.
- **WR-02 (`OP_BLANK_CHECK` treated verdict 2 as BAD).** Phase 206 changed this. `tests/test_chip_test.py::test_blank_check_verdict_2_is_skipped_with_status_error` and `test_verify_verdict_2_is_skipped_with_status_error` now pin verdict 2 as skipped with status error.

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

Phase 202 is host-only, and a fake serial port drives every wire-level claim. No bench run is part of this phase's contract.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (202-01-01 is a decision checkpoint with no code)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (none were MISSING)
- [x] No watch-mode flags
- [x] Feedback latency < 190s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-09-24

---

## Validation Audit 2026-09-24

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

Evidence, re-run on 2026-09-24 against `firestarter_app` `5302f63`:

- The 12 test files named in the Phase 202 `<verify>` blocks ran together: **718 passed**, 129.76 s.
- The import-purity AST check, the `abort_predicate` seam signature check, the `_diff_offsets` retirement check and the `consistency_check_eprom` docstring check all passed.
- `mypy firestarter/compare.py firestarter/cli_handlers.py firestarter/main.py` reported no issues.
- `ruff check` and `ruff format --check` over `firestarter/ tests/` were clean.
- `pyproject.toml:176` still lists `firestarter.compare` in the strict-typing module list.
