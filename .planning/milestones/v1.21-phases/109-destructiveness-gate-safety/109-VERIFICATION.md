---
phase: 109-destructiveness-gate-safety
verified: 2026-07-02T20:21:37Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 109: Destructiveness Gate + Safety Verification Report

**Phase Goal:** A tester can never accidentally run a destructive step — write/erase only exist in the plan when `--destructive` was passed on that exact invocation — and a machine-enforced gate proves `dev test` never grows a new way to touch hardware outside the existing, already-safe command paths.
**Verified:** 2026-07-02T20:21:37Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SAFE-01: non-destructive plan structurally omits write/erase from executable `steps`; `--destructive` read only from the invocation kwarg, never config/env | ✓ VERIFIED | `chip_test.py:318-416` `derive_plan()`: when `destructive` is falsy, `OP_WRITE`/`OP_ERASE` are appended only to a local `locked_destructive` list, never to `steps`; when `destructive=True` they are appended to `steps` exactly as Phase 108. `grep -nE 'os\.environ|getenv'` in chip_test.py returns zero hits — the only source of `destructive` is the `derive_plan(..., destructive=...)` kwarg. Tests `test_derive_plan_destructive_flag_strips_not_annotates`, `test_derive_plan_strip_default_only_destructive_ops_removed`, `test_derive_plan_destructive_keeps_and_empties_advisory` pass and assert exact op-set membership (not tautological) against real DB chip M8720. |
| 2 | SAFE-02: every executed op routes through `resolve_chip`; no VPP-set, no raw wire dict, no `--force`; a VPP-guard refusal is a captured finding, never silently retried | ✓ VERIFIED | `run_plan`/`_resolve_or_none` (`chip_test.py:481-499`) call `resolve_chip(name, db=db)` for every executed step; `derive_plan` never calls it (guard-bypass/guard-honoring split preserved, asserted by pre-existing tests `test_derive_plan_never_calls_resolve_chip` / `test_derive_plan_reads_via_get_eprom_and_convert_to_programmer_only`, both still pass). `grep -niE 'set_vpp\|vpp_enable\|enable_vpp\|write_vpp'` and `grep -nE 'force\s*='` in chip_test.py show zero executable-code hits (only comments). New tests `test_safe02_routes_via_resolve_chip_for_every_executed_step`, `test_safe02_no_vpp_no_wire_no_force_source_scan` (AST-based, docstring-exempt), `test_safe02_vpp_guard_refusal_is_a_finding_not_a_retry_single_run`/`_multi_run` (assert exact operator call-count == 1, no retry-around), and `test_safe02_only_known_operator_methods_no_attribute_error` (Mock(spec=[6 methods]) full run completes without AttributeError) all pass. |
| 3 | SWEEP-05: applicable-only N-of-M banner DATA (M excludes NA slots, derives from the single Plan object; N counts ran-with-any-verdict; no rendering added) | ✓ VERIFIED | `BannerCounts`/`count_applicable(plan, results)` (`chip_test.py:895-951`): `m_applicable = sum(supported steps) + len(plan.locked_destructive)` (single Plan object, never re-derives — proven by `test_count_applicable_m_from_single_plan_never_rederives` which monkeypatches `derive_plan` to raise and asserts it's never called); `n_ran` counts verdicts in `{OK, BAD, marginal}`, excluding NA/SKIPPED. `test_count_applicable_uv_counts` asserts exact numeric M=4/N=3 for AM2716; `test_count_applicable_n_equals_m_when_destructive` asserts N==M==5 for the same chip run destructive. `test_count_applicable_no_print_or_render_introduced` (word-boundary regex) confirms zero print/click/console additions. |
| 4 | PATT-03: UV write region is an engine module constant, top-anchored `[mem_size-256, mem_size)`, UV detected in-engine, no DB field can widen it | ✓ VERIFIED | `_UV_WRITE_REGION_LENGTH = 256` (`chip_test.py:601`, module constant) + `_write_region_for(eprom_data)` (`chip_test.py:615-645`): width always comes from the constant; `mem_size` only bounds placement. UV detected via `electrical-type == "UV-EPROM"` (derivation-time dict) OR `algorithm == _PROTOCOL_UV_EPROM (0x0B)` (execution-time programmer dict — a real gap the plan's literal wording missed and the executor caught/fixed, documented in 109-01-SUMMARY.md). `test_cap_not_widenable_by_injected_db_field` proves an injected oversized DB hint cannot widen the region; `test_uv_window_top_anchored_default_length`/`test_uv_window_scales_with_memory_size`/`test_nonuv_default_region_unchanged` assert exact (start, length) tuples for AM2716/AM2732/M8720. `_dispatch_multi_run` (`chip_test.py:807`) feeds the same `start` into both `generate_pattern` and `classify_fingerprint(addr_base=start)` (Pitfall 3, verified by `test_addr_base_absolute_matches_region_start`). `generate_pattern`/`classify_fingerprint` bodies unchanged (verified by `test_generate_pattern_and_classify_fingerprint_source_unchanged`). |
| 5 | SAFE-03: a genuinely-populated, build-failing AST checker denies VPP-set/raw-wire-dict/--force in `dev test`'s code paths, proven non-hollow by a mandatory paired anti-hollow pytest | ✓ VERIFIED | `tools/check_devtest_orchestrator.py` is a real `ast.parse` + `ast.NodeVisitor` walk (not grep/substring), with 3 deny-list buckets (VPP-set names, wire-dict key threshold ≥2, force=True/`"--force"`), an env-override seam (`FIRESTARTER_DEVTEST_SRC`), and a host-only assertion. Ran directly: `python tools/check_devtest_orchestrator.py` → exit 0, `PASS: ... 0 VPP-set, 0 raw-wire-dict, 0 --force`. Paired pytest `tests/test_check_devtest_orchestrator.py` (6 tests) subprocess-invokes the real checker binary with real on-disk fixture files injected via the env-override for 4 distinct violation classes (VPP-set, raw-wire-dict, force=True, bare `"--force"` string) plus a clean-fixture sanity check — all 6 pass, confirming both the clean-pass AND non-zero-on-violation halves of the anti-hollow contract (D-03). This is NOT the v1.12 hollow-GATE-03 pattern. |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/chip_test.py` | `Plan.locked_destructive`, strip logic, `_UV_WRITE_REGION_LENGTH`/`_write_region_for`, `BannerCounts`/`count_applicable` | ✓ VERIFIED | All symbols present, substantive, wired into `derive_plan`/`_dispatch_multi_run`/reporting path |
| `firestarter_app/tests/test_chip_test.py` | SAFE-01/PATT-03/SWEEP-05/SAFE-02 tests | ✓ VERIFIED | 75 tests in file, all pass; targeted 34-test subset for this phase's new/changed behavior all pass |
| `firestarter_app/tools/check_devtest_orchestrator.py` | AST-based SAFE-03 checker | ✓ VERIFIED | Genuine AST walk, exits 0 on clean source with PASS: line |
| `firestarter_app/tests/test_check_devtest_orchestrator.py` | Anti-hollow paired pytest | ✓ VERIFIED | 6 tests, real subprocess-level fixture injection, all pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `derive_plan(destructive=False)` | `Plan.steps` (omits write/erase) + `Plan.locked_destructive` (records them) | direct construction | WIRED | Confirmed by code read + passing tests |
| `run_plan` | `Plan.steps` only | iteration | WIRED (and confirmed NOT wired to `locked_destructive`) | `grep locked_destructive` shows zero references inside `run_plan`/`_run_step`/`_dispatch_multi_run` — only in `derive_plan` (producer) and `count_applicable` (consumer) |
| `etype/algorithm` (UV signal) | `_write_region_for` → `generate_pattern`/`classify_fingerprint` | `_dispatch_multi_run` | WIRED | Same absolute `start` fed to both calls (Pitfall 3), verified by dedicated test |
| `Plan` + `run_plan` results | `count_applicable` → `BannerCounts` | single-object read, no re-derivation | WIRED | Monkeypatch-raises test proves no second `derive_plan` call |
| checker | `chip_test.py` source | `ast.parse` + env-override | WIRED | Direct execution confirmed exit 0/PASS; pytest subprocess confirms both polarities |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full targeted test_chip_test.py subset (34 tests covering all 5 truths) | `pytest tests/test_chip_test.py -k "..." -v` | 34 passed | ✓ PASS |
| Full test_chip_test.py file | `pytest tests/test_chip_test.py -q` | 75 passed | ✓ PASS |
| SAFE-03 checker direct invocation | `python tools/check_devtest_orchestrator.py` | exit 0, `PASS:` line | ✓ PASS |
| SAFE-03 paired anti-hollow pytest | `pytest tests/test_check_devtest_orchestrator.py -v` | 6 passed (1 clean-pass + 4 planted-violation + 1 seam-sanity) | ✓ PASS |
| Full app suite (baseline check) | `pytest --cov=firestarter --cov-fail-under=70` | 796 passed, 1 failed | ✓ PASS (matches documented pre-existing baseline failure) |
| Lint/format | `ruff check` + `ruff format --check` on all 4 phase files | clean | ✓ PASS |

**Baseline note confirmed:** the single failure (`tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches`) is a coverage-matrix golden-fixture diff unrelated to chip_test.py/check_devtest_orchestrator.py — consistent with the phase's documented pre-existing baseline. No other failures found. Not counted as a Phase-109 gap.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| SAFE-01 | 109-01 | Structural destructiveness gate at plan-construction time, per-invocation only | ✓ SATISFIED | Truth 1 |
| SAFE-02 | 109-02 (+ preserved by 109-01) | Orchestrator-only: resolve_chip routing, no VPP/raw-cmd/--force, refusal-as-finding | ✓ SATISFIED | Truth 2 |
| SAFE-03 | 109-03 | Machine-enforced, non-hollow AST CI gate | ✓ SATISFIED | Truth 5 |
| SWEEP-05 | 109-02 | Applicable-only N-of-M banner data | ✓ SATISFIED | Truth 3 |
| PATT-03 | 109-01 | UV small-region write cap, engine-capped, non-widenable | ✓ SATISFIED | Truth 4 |

All 5 phase requirement IDs (SAFE-01, SAFE-02, SAFE-03, SWEEP-05, PATT-03) are declared in PLAN frontmatter, cross-referenced in REQUIREMENTS.md (all marked `[x]` complete, mapped to Phase 109), and independently verified against the codebase above. No orphaned requirements found for this phase.

### Anti-Patterns Found

None. Scanned `chip_test.py`, `tests/test_chip_test.py`, `tools/check_devtest_orchestrator.py`, `tests/test_check_devtest_orchestrator.py` for TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER markers, empty-implementation patterns, and hardcoded-empty-data patterns — zero hits in all four files.

### Human Verification Required

None. All must-haves are structurally verifiable via code reading + passing automated tests; no visual, real-time, or external-service behavior is in scope for this phase (host-only, bench-free by design).

### Gaps Summary

No gaps. All 5 truths (mapping 1:1 to the 5 ROADMAP success criteria and the 5 requirement IDs SAFE-01/02/03, SWEEP-05, PATT-03) are verified against actual, running code — not SUMMARY.md narrative. The SAFE-03 gate in particular was scrutinized against this project's own hollow-GATE-03 (v1.12) precedent and found to be genuinely populated: a real AST walk with a mandatory, passing, subprocess-level negative-fixture test suite (4 distinct violation classes injected via env-override, each independently proven to flip the exit code).

Two executor-caught-and-fixed deviations (documented in 109-01-SUMMARY.md) were verified as correct engineering, not shortcuts: (1) two pre-existing tests updated to pass explicit `destructive=True` after the strip-by-default behavior change, and (2) UV detection extended to also recognize `algorithm == 0x0B` at execution time, since the real `resolve_chip`-derived programmer dict drops `electrical-type` — both are covered by dedicated regression tests that pass.

---

_Verified: 2026-07-02T20:21:37Z_
_Verifier: Claude (gsd-verifier)_
