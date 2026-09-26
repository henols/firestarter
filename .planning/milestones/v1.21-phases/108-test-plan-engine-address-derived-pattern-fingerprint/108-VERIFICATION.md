---
phase: 108-test-plan-engine-address-derived-pattern-fingerprint
verified: 2026-07-02T00:00:00Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 108: Test-Plan Engine + Address-Derived Pattern + Fingerprint Verification Report

**Phase Goal:** Given any chip in the database — including ones the maintainer has never touched — `dev test` can derive exactly the operations that chip's protocol supports, run each as an independent non-fatal step, and (for write/verify) use a pattern that actually exposes address-line and stuck-bit faults rather than hiding them.

**Verified:** 2026-07-02
**Status:** passed
**Re-verification:** No — initial verification

**Scope note:** Per project instructions, code changes for this phase live in the `firestarter_app/` git submodule on branch `v1.21-community-chip-validation-command`. All file paths below are relative to that submodule root unless prefixed `firestarter_app/`. `@dev.command("test")` CLI wiring (Phase 112), the `--destructive` gate/CI orchestrator-only check (Phase 109), the report model (Phase 110), and the voltage sampler (Phase 111) are explicitly out of scope for Phase 108 and were not expected or checked here.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, 108, items 1–6)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `dev test <chip>` derives a plan strictly from `protocol`/`electrical-type`/`FLAG_CAN_ERASE`, never re-invoking `classify()`, and works even for `support_status`-refused chips because derivation bypasses `resolve_chip` | ✓ VERIFIED | `derive_plan()` (`chip_test.py:307-383`) calls only `db.get_eprom` + `db.convert_to_programmer`; `grep -c 'classify('` → 0. Live-executed against `AT28C04,AT28HC04` (real DB entry, `support_status` causes `resolve_chip` to raise `ChipNotImplementedError` — confirmed live) — `derive_plan` still returned a full 6-step plan. |
| 2 | Each operation executes independently with an explicit `OK`/`BAD`/`NA`/`SKIPPED` verdict; a `BAD`/exception on one step never prevents remaining steps from running | ✓ VERIFIED | `run_plan`/`_run_step` (`chip_test.py:468-596`) wrap every step body in its own try/except; `test_run_plan_non_fatal_raising_step_does_not_abort_later_steps` and `test_run_plan_verdict_vocabulary_and_na_not_executed` pass. Verdict constants are exactly `OK/BAD/NA/SKIPPED` (+`marginal`, scoped to destructive/verify per D-06). |
| 3 | The sweep always runs id-check first; a chip-ID mismatch gates all destructive steps shut (chip untouched) while id/read findings are still recorded | ✓ VERIFIED | `derive_plan` always places `id` at `steps[0]`; `run_plan` sets `destructive_gate_closed` from the id-step result before iterating further. Live-executed with a mocked `check_eprom_id` returning `(False, 0x9999)`: `write`/`erase` verdicts were `SKIPPED` with `operator.write_eprom.called == False` and `operator.erase_eprom.called == False`, while `id`/`read`/`blank-check`/`verify` were still recorded (`id`→BAD, others→OK). Also covered by `test_id_mismatch_gate_skips_destructive_steps_without_calling_operator`, `test_id_detected_mismatch_gate_skips_destructive_steps`, `test_id_match_leaves_destructive_steps_ungated`, `test_id_mismatch_does_not_gate_non_destructive_steps` (all pass). |
| 4 | Destructive/verify steps execute at least twice per run; disagreement across runs reports `marginal` (never coerced PASS/FAIL); `runs<2` rejected before any operator call | ✓ VERIFIED | `run_plan(..., runs=1)` returns a single sentinel `BAD` `StepResult` before any resolve/operator call — live-confirmed (`operator.method_calls == []`). Live-executed disagreement scenario (`write_eprom.side_effect=[True, False]`) produced verdict `marginal` with reason citing "2 runs disagreed on outcome (D-06 marginal policy)". `test_runs_boundary_rejects_below_2_before_any_operator_call`, `test_marginal_on_disagreeing_write_runs`, `test_marginal_on_disagreeing_verify_runs`, `test_agreeing_destructive_runs_report_confident_ok/bad` all pass. |
| 5 | The write/verify pattern generator derives each byte from its address (folding high address bits), preceded by a cheap all-0x00/all-0xFF pre-pass; a byte-mismatch fingerprint classifier categorizes verify failures as blank/contact, address-line, or transport | ✓ VERIFIED | `address_fold_byte`/`generate_pattern`/`prepass_images` (`chip_test.py:48-77`) implement the exact XOR-fold, region-parameterized on absolute address. `classify_fingerprint` (`chip_test.py:138-236`) implements the locked 4-bucket order. Live-executed: an A8-fault byte array classified `address-line` naming `suspected_line=8`, `cluster_score=1.0`. All 4 bucket tests (`fp_blank`, `fp_address_line` ×2, `fp_transport`, `fp_indeterminate`) pass; `test_fingerprint_evidence_fields` confirms the evidence dict shape. |
| 6 | `EpromOperationError` carries the firmware `response.id` byte through a new backward-compatible `error_code` attribute; every per-step result has access to the exact firmware error code | ✓ VERIFIED | `exceptions.py:37-42` — `EpromOperationError.__init__(self, *args, error_code=None)`. `eprom_operations.py:84-86` — `_raise_for_error_response` passes `error_code=response.id` on both the `ProtocolNotImplementedError` and generic `EpromOperationError` branches. `StepResult.error_code` populated from `exc.error_code` in `_run_step` (`chip_test.py:584-591`). `test_error_code_seam.py` (5 tests) + `test_run_plan_non_fatal_raising_step_does_not_abort_later_steps` (captures `error_code` on the raising step) all pass. |

**Score:** 6/6 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/exceptions.py` | `EpromOperationError.error_code` optional kwarg | ✓ VERIFIED | Present, substantive, backward-compatible; `mypy --strict` clean (file is in the strict-8 set). |
| `firestarter/eprom_operations.py` | `_raise_for_error_response` chokepoint pass-through | ✓ VERIFIED | Single chokepoint edit at lines 84-86; both dispatch branches carry `error_code=response.id`. |
| `tests/test_error_code_seam.py` | Dedicated bench-free test file | ✓ VERIFIED | 87 lines, 5 tests, all pass; ruff-clean. |
| `firestarter/chip_test.py` | New module: pattern generator, classifier, `derive_plan`, `run_plan` | ✓ VERIFIED | 791 lines; contains all claimed symbols (`address_fold_byte`, `generate_pattern`, `prepass_images`, `_diff_offsets`, `Fingerprint`, `classify_fingerprint`, `Step`, `Plan`, `derive_plan`, `StepResult`, `run_plan`, dispatch helpers). No stub markers, no `classify(` calls, no VPP/`--force` call sites (only descriptive comments). |
| `tests/test_chip_test.py` | Bench-free unit tests for PATT-01/02, SWEEP-01..04 | ✓ VERIFIED | 900 lines, 50 tests, all pass (`python -m pytest tests/test_chip_test.py -q` → 50 passed). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `_raise_for_error_response` (`eprom_operations.py:70`) | `EpromOperationError(error_code=response.id)` | Direct call | ✓ WIRED | Confirmed at lines 84-86; grep + read match plan spec exactly. |
| `Response.id` (`frame_parser.py`) | `error_code` attribute | Pass-through kwarg | ✓ WIRED | `response.id` flows unmodified into `error_code`. |
| `generate_pattern`/`classify_fingerprint` | write/verify step | `_dispatch_multi_run` (`chip_test.py:700-791`) | ✓ WIRED | Builds `expected = generate_pattern(...)`, computes `Fingerprint` via `classify_fingerprint(expected, actual, repeat_divergent=..., addr_base=_WRITE_REGION_START)`; live-verified via `test_write_step_attaches_fingerprint_with_region_start_addr_base` and `test_write_step_fingerprint_addr_base_matches_region_start` (both pass). |
| `db.get_eprom` → `db.convert_to_programmer` | `derive_plan` op list | Guard-bypassing read path | ✓ WIRED | Live-executed against a real DB entry with `support_status="adapter-required"` (`AT28C04,AT28HC04`) — `resolve_chip` raised `ChipNotImplementedError`, but `derive_plan` returned a full plan. No `resolve_chip(` call exists anywhere inside `derive_plan`'s body (confirmed by source inspection: the only `resolve_chip(` call sites in the file are inside `_resolve_or_none`, used exclusively by `run_plan`). |
| `resolve_chip(name, db)` | per executed op → operator method | Guard-honoring execution | ✓ WIRED | `_resolve_or_none` (`chip_test.py:448-465`) calls `resolve_chip(name, db=db)` for every executed step; a refusal maps to `SKIPPED` with reason (never bypassed). Covered by `test_run_plan_resolver_refusal_maps_to_skipped` and `test_run_plan_routes_through_resolve_chip_not_derivation_dict` (both pass). |
| `EpromOperationError.error_code` (108-01) | per-step `StepResult.error_code` (108-04) | Exception capture in `_run_step` | ✓ WIRED | `except EpromOperationError as exc: ... error_code=exc.error_code` (`chip_test.py:584-591`). |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Guard-bypass on a real `support_status`-refused chip | Manual script: `derive_plan('AT28C04,AT28HC04', db)` vs `resolve_chip(...)` | `resolve_chip` raised `ChipNotImplementedError: adapter required...`; `derive_plan` returned 6 steps | ✓ PASS |
| id-first destructive gate closes on mismatch | Manual script: mocked `check_eprom_id` → `(False, 0x9999)`, `run_plan(...)` | `write`/`erase` verdict `SKIPPED`; `operator.write_eprom.called`/`erase_eprom.called` both `False`; `read`/`blank-check`/`verify` still recorded | ✓ PASS |
| `runs<2` rejected before any operator call | Manual script: `run_plan(plan, operator, db, runs=1)` | Single `BAD` sentinel `StepResult`; `operator.method_calls == []` | ✓ PASS |
| Marginal on disagreeing destructive-run outcomes | Manual script: `write_eprom.side_effect=[True, False]`, `run_plan(..., runs=2)` | `write` verdict `marginal`, reason cites D-06 policy | ✓ PASS |
| Address-line fingerprint names the suspected bit | Manual script: `classify_fingerprint` on an A8-corrupted byte array | `classification == "address-line"`, `evidence["suspected_line"] == 8`, `cluster_score == 1.0` | ✓ PASS |
| flash4 erase NA against real DB chip | Manual script: `derive_plan('AE29F1008', db)` (protocol 0x05, real DB entry) | `erase` step `supported=False`, reason "flash4 (0x05) auto-erases per page..." | ✓ PASS |
| SRAM blank-check NA against real DB chip | Manual script: `derive_plan('DS1220(RW)', db)` (electrical-type SRAM, real DB entry) | `blank-check` step `supported=False`, reason "blank-check not applicable to SRAM..." | ✓ PASS |
| Full `chip_test.py` + `test_error_code_seam.py` suite | `python -m pytest tests/test_chip_test.py tests/test_error_code_seam.py -q` | `55 passed` (50 + 5) | ✓ PASS |
| Full app test suite (regression) | `python -m pytest -q` | All pass except one pre-existing, out-of-scope failure (see below) | ✓ PASS (with documented exception) |
| Lint/format/type gates | `ruff check` / `ruff format --check` / `mypy firestarter/exceptions.py` | All clean, no new errors | ✓ PASS |

### Probe Execution

No probe scripts (`scripts/*/tests/probe-*.sh`) apply to this phase — the phase's own PLAN/SUMMARY verification criteria are pytest-based, not probe-based. Skipped as not applicable.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| RPT-03 | 108-01, 108-04 | `EpromOperationError` preserves firmware `response.id` via `error_code` seam | ✓ SATISFIED | `exceptions.py:37-42`, `eprom_operations.py:84-86`, `chip_test.py:584-591`, `test_error_code_seam.py` (5/5 pass) |
| PATT-01 | 108-02 | Address-derived write/verify pattern, region-parameterized, pre-pass images | ✓ SATISFIED | `chip_test.py:48-77`; 5 dedicated unit tests pass |
| PATT-02 | 108-02 | 4-bucket byte-mismatch fingerprint classifier, honest indeterminate fallback | ✓ SATISFIED | `chip_test.py:138-236`; 6 dedicated unit tests pass; live address-line naming confirmed |
| SWEEP-01 | 108-03 | `derive_plan` reads DB fields only, bypasses `resolve_chip` guard | ✓ SATISFIED | `chip_test.py:307-383`; 18 dedicated unit tests pass; live-confirmed against real adapter-required/flash4/SRAM DB entries |
| SWEEP-02 | 108-04 | Independent non-fatal per-op steps with OK/BAD/NA/SKIPPED verdicts | ✓ SATISFIED | `chip_test.py:468-627`; non-fatal + verdict-vocab tests pass |
| SWEEP-03 | 108-04 | id-first ordering; chip-ID mismatch hard-gates destructive steps | ✓ SATISFIED | `chip_test.py:524-554`; 4 dedicated unit tests pass; live-confirmed gate closure |
| SWEEP-04 | 108-04 | N≥2 execution on destructive/verify; disagreement → `marginal` | ✓ SATISFIED | `chip_test.py:508-519, 700-791`; 9 dedicated unit tests pass; live-confirmed `runs<2` rejection and marginal verdict |

No orphaned requirements: all 7 IDs assigned to Phase 108 in REQUIREMENTS.md (lines 97-110) are declared in exactly one plan's frontmatter (`requirements:` field), and the union of all 4 plans' declared requirements equals the full Phase 108 requirement set with no gaps or extras.

### Anti-Patterns Found

None. Scanned `firestarter/chip_test.py`, `firestarter/exceptions.py`, `firestarter/eprom_operations.py` (modified region), `tests/test_chip_test.py`, `tests/test_error_code_seam.py` for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers, placeholder/"not yet implemented" text, and empty-return stubs — zero matches. `grep -c 'classify('` on `chip_test.py` → 0 (no runtime re-invocation of the build-time classifier, per D-04/SWEEP-01 mandate). `grep` for `vpp`/`force` in `chip_test.py` shows only descriptive comments explaining the engine sets no VPP and passes no `--force` — no actual VPP-set or `--force` call sites.

### Out-of-Scope Item (documented, not a gap)

`tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` fails on this branch. Independently confirmed: this test's assertion compares a regenerated coverage-matrix markdown file against a committed golden fixture; the drift is unrelated to any file this phase touched (`chip_test.py`, `exceptions.py`, `eprom_operations.py`, the two new test files) — the coverage matrix generator does not read `chip_database.json` or any file this phase modified. This matches the pre-existing ledger-drift issue tracked from Phase 106-01 per the SUMMARYs and the task brief's stated out-of-scope carve-out. Not counted as a phase gap.

### Human Verification Required

None. This phase is entirely bench-free pure-compute/unit-testable engine work (explicitly scoped that way — hardware wiring is Phase 111, CLI wiring is Phase 112). All must-haves are either directly observable via source inspection or behaviorally exercised via passing automated tests plus live manual script execution against the real chip database in this session.

### Gaps Summary

No gaps found. All 6 ROADMAP success criteria for Phase 108 are verified with both passing automated tests (55 dedicated tests across `test_chip_test.py` + `test_error_code_seam.py`, all green) and live manual execution against the real chip database and mocked operator in this verification session (not merely reading the SUMMARY's claims). All 7 requirement IDs (SWEEP-01..04, PATT-01/02, RPT-03) are satisfied and correctly traced. Code is ruff-clean, mypy-clean on the strict-8 file touched, and the only test failure in the full suite is a documented, independently-confirmed pre-existing/out-of-scope golden-fixture drift unrelated to this phase's changes.

---

_Verified: 2026-07-02_
_Verifier: Claude (gsd-verifier)_
