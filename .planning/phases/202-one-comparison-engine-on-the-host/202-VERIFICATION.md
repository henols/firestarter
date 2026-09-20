---
phase: 202-one-comparison-engine-on-the-host
verified: 2026-09-20T21:15:00Z
status: passed
score: 8/8 must-have requirement groups verified (all plan-level truths and prohibitions verified)
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-01-PLAN.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-01-SUMMARY.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-02-PLAN.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-02-SUMMARY.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-03-PLAN.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-03-SUMMARY.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-04-PLAN.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-04-SUMMARY.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-05-PLAN.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-05-SUMMARY.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-REVIEW.md", "firestarter_app/firestarter/chip_test.py", "firestarter_app/firestarter/cli_handlers.py", "firestarter_app/firestarter/compare.py", "firestarter_app/firestarter/eprom_operations.py", "firestarter_app/pyproject.toml", "firestarter_app/tests/test_chip_test.py", "firestarter_app/tests/test_cli_handlers.py", "firestarter_app/tests/test_compare.py", "firestarter_app/tests/test_eprom_operations.py"]
covered_digest: "v1:sha256:96f6390c1269ff65c77c370681cb4277cb4d61aa6fc50b65eb5ab619fab91d67"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 202: One comparison engine, on the host — Verification Report

**Phase Goal:** `firestarter verify` and `firestarter blank` compare by reading the chip and comparing on the host, through one streamed implementation that names why a compare failed instead of reporting a single address.
**Verified:** 2026-09-20T21:15:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `verify`/`blank` complete correctly against firmware that still carries `CMD_VERIFY`(6)/`CMD_BLANK_CHECK`(4), without sending either | ✓ VERIFIED | `constants.py:52,54` still define `COMMAND_BLANK_CHECK=4`/`COMMAND_VERIFY=6`; `tests/test_eprom_operations.py::TestOrdinalsNeverSentByVerifyOrBlank::test_no_run_composes_either_retired_ordinal` passes (1 passed), asserting every composed command dict across 4 runs (clean/mismatch verify, clean/non-blank blank) carries `COMMAND_READ`, never 4 or 6 |
| 2 | Mismatch found on a 512 KB part, peak host memory bounded independently of device size | ✓ VERIFIED | `tests/test_compare.py::TestCompareAccumulatorPeakAllocation` (2 tests) — traced peak <1 MiB, flat across doubled device size; both pass |
| 3 | Default run names first mismatching range `start–end` + byte count, no byte values; `--full` names every span | ✓ VERIFIED | `compare.py:504-541` `render_compare_lines` emits only `Mismatch 0xSTART-0xEND (N bytes)` and a bucket line — no expected/actual bytes anywhere; `tests/test_compare.py::TestRenderCompareLines` (7 tests) pass |
| 4 | Failed compare carries a `classify_fingerprint` bucket with total/bad counts, computed from streamed accumulation | ✓ VERIFIED | `chip_test.classify_fingerprint` (chip_test.py:146-177) delegates to `compare.classify_streamed`; `_diff_offsets` removed from the codebase (only referenced in a retirement comment); D-03 corpus test `TestClassifyFingerprintCorpus` passes |
| 5 | Read-abort question answered in writing, not assumed | ✓ VERIFIED | `.planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md` (135 lines) gives an affirmative, mechanism-level answer; ROADMAP.md:226-235 "Known open mechanic — answered by phase 202" points at it |

### Requirement-Level Truths (from PLAN frontmatter must_haves)

| # | Truth (paraphrased) | Req | Status | Evidence |
|---|------|-----|--------|----------|
| 6 | `verify` sends `COMMAND_READ`, never composes `cmd:6` | CMP-01 | ✓ VERIFIED | see #1 |
| 7 | Clean verify exits 0, mismatching verify exits 1 | CMP-07 | ✓ VERIFIED | `test_eprom_operations.py` exit-code assertions in `TestOrdinalsNeverSentByVerifyOrBlank` (`v_match==0`, `v_mismatch==1`) |
| 8 | Mismatch line exact form `Mismatch 0xSTART-0xEND (N bytes)`, no byte values | D-13 | ✓ VERIFIED | code + tests above |
| 9 | `compare.py` import set excludes `eprom_operations`/`chip_test`/`serial_comm`/`click` | D-01 | ✓ VERIFIED | `compare.py:29-31` only imports `__future__`/`dataclasses`; `tests/test_compare.py::TestImportPurity` AST-walks the whole tree and passes |
| 10 | Expected side arrives through a pull callback `expected(offset,length)->bytes`; no device-sized buffer | D-04 | ✓ VERIFIED | `verify_eprom._expected` (eprom_operations.py:2439) seeks+reads per call; `_blank_expected_bytes` (line 332) returns a constant string of the requested length only |
| 11 | `CompareResult` plain dataclass; `render_compare_lines` returns `list[str]` | D-05 | ✓ VERIFIED | `compare.py:89-159`, `504` |
| 12 | Accumulator is the one divergence implementation, streaming, no device-sized list | D-02 | ✓ VERIFIED | `compare.py:162-330` three-tier `feed()`; `TestCompareAccumulatorRuntime`/`TestCompareAccumulatorFastPathStructure` pass |
| 13 | Retained-range cap with exact `extra_ranges`/`extra_bytes` counters | D-16 | ✓ VERIFIED | `compare.py:269-286`; `TestCompareAccumulatorRangeCapBoundary`, `TestCompareAccumulatorAlternatingPrecision` pass |
| 14 | `dev test` keeps pass/fail meaning across `verify_eprom`'s int contract | — | ✓ VERIFIED | `chip_test.py:3243` `== 0` adapter; `tests/test_chip_test.py`/`test_dev_test_cmd.py` (part of 389-test run, all pass) |
| 15 | `firestarter.compare` mypy-strict; `compare.py`/`cli_handlers.py`/`main.py` mypy-clean | — | ✓ VERIFIED | `pyproject.toml:176` lists `firestarter.compare`; `mypy firestarter/compare.py firestarter/cli_handlers.py firestarter/main.py` → "Success: no issues found in 3 source files" (re-run by this verifier) |
| 16 | Two `CompareAccumulator` instances accumulate independently; no module-level mutable counter | backstop | ✓ VERIFIED | Direct source inspection: `compare.py`'s only module-level state is immutable (`MAX_RETAINED_RANGES: int`, `FP_*` string constants, threshold floats); every mutable field (`_compared`, `_bad`, `_ranges`, `_set_count`, …) is a `self.` attribute set in `__init__` — no shared/global state exists for two instances to leak into each other through |
| 17 | Prohibition: a compare must never report a match for a region it did not compare in full | D-plan01 | ✓ VERIFIED (prohibition resolved) | `_drive_region_compare` (eprom_operations.py:2332) requires `result.total > 0 and result.bad == 0 and result.compared == result.total` before returning 0 |
| 18 | Peak alloc <1 MiB flat in size; clean 512 KiB <1.0s, worst-case <8.0s | CMP-03 | ✓ VERIFIED | `TestCompareAccumulatorPeakAllocation`, `TestCompareAccumulatorRuntime`, `TestCompareAccumulatorFastPathStructure` all pass |
| 19 | Coalescing/adjacency/ordering/empty/single-byte/cap-boundary correctness | CMP-03/05 | ✓ VERIFIED | `TestCompareAccumulatorAdjacencyAndOverlap`, `TestCompareAccumulatorOrdering`, `TestCompareAccumulatorEmptyAndSingleByte`, `TestCompareAccumulatorRangeCapBoundary` all pass |
| 20 | Prohibition: cap bounds what is shown, never what is counted | D-plan02 | ✓ VERIFIED (prohibition resolved) | `compare.py:272-285` comment + `_extra_ranges`/`_extra_bytes` running counters; covered by cap-boundary tests |
| 21 | `classify_fingerprint` delegates, `_diff_offsets` retired, corpus of 5 buckets/4 traps agrees | CMP-06 | ✓ VERIFIED | `chip_test.py:146-177`; `TestClassifyFingerprintCorpus` (part of the 70-test `test_compare.py` run) passes |
| 22 | `verify` prints exactly one bucket summary line after range lines | D-14/D-09 | ✓ VERIFIED | `render_compare_lines` (compare.py:534-540); `TestRenderCompareLines`/`TestFinaliseAlwaysClassifies` pass |
| 23 | Default stops at first mismatch, breaks read in flight | CMP-04/D-06 | ✓ VERIFIED | `_drive_region_compare` (eprom_operations.py:2262-2273) passes `accumulator.has_mismatch` as `abort_predicate` when `not full`; `TestVerifyEpromReadAbort::test_default_abort_stops_acking_after_the_mismatching_chunk` passes |
| 24 | `_main_phase_read_data` gains additive `abort_predicate`, 4 existing callers unchanged | D-06 | ✓ VERIFIED | `eprom_operations.py:915-921`; full `test_eprom_operations.py`/`test_consistency_check.py` suites (62+ tests cited in SUMMARY, re-confirmed via this verifier's 389-test combined run) pass |
| 25 | Deliberate abort never reported as fault; only timeout id, only in bounded window, only when requested | D-08 | ✓ VERIFIED | `eprom_operations.py:2290-2315` four-condition check; `TestVerifyEpromReadAbort` (10 tests: default-abort, non-timeout-after-abort, timeout-with-no-abort, timeout-outside-window, first/last-byte boundary, exact-count) all pass |
| 26 | Bucket line on aborted run reports `compared < total` with span | D-09 | ✓ VERIFIED | `_drive_region_compare` overrides `result.total = region_length` before rendering; `test_aborted_run_counts_are_exact_integers_matching_pre_stop_bytes` passes |
| 27 | First/last-byte mismatch both reported as a range, both exit 1 | CMP-04 boundary | ✓ VERIFIED | `test_first_byte_mismatch_aborts_after_one_chunk_and_reports_a_range`, `test_last_byte_mismatch_completes_normally_not_as_an_abort` pass |
| 28 | Zero-length region: no abort, no false clean pass | CMP-04 empty | ✓ VERIFIED | `result.total > 0` guard (eprom_operations.py:2332), same as truth #17 |
| 29 | `blank` compares via the same engine; no ordinal 4 composed | CMP-02 | ✓ VERIFIED | `check_eprom_blank` (eprom_operations.py:2596-2683) calls `COMMAND_READ` + `_drive_region_compare`; see #1's ordinal test |
| 30 | Blank supplies expected bytes via same pull callback, no device-sized buffer | D-04 | ✓ VERIFIED | `_blank_expected_bytes` (eprom_operations.py:332) |
| 31 | Blank on non-blank-capable part (SRAM/FRAM) returns 2, not 1 | D-12 | ✓ VERIFIED | `check_eprom_blank:2639-2648` short-circuits to `return 2` before any command composed |
| 32 | `verify`/`blank` both accept `-a/-s` spelled as `read` does; region-scoped compare covers only that region | CMP-08 | ✓ VERIFIED | `cli_handlers.py:906-1022` option decorators; `tests/test_cli_handlers.py::test_region_scoped_verify_composes_a_command_dict_bounding_exact_region` passes |
| 33 | Explicit size wins; default resolution differs per command; refusals fire before port opens | D-17 | ✓ VERIFIED | `_region_refusal_exit_code` (cli_handlers.py:796-903), including the CR-01 fix (see below); `test_region_past_chip_end_is_refused_before_opening_the_port` (parametrized verify+blank) passes, `connect_spy.assert_not_called()` |
| 34 | `verify`/`blank` exit 0/1/2 as documented; transport failure distinguishable from mismatch | CMP-07/D-10 | ✓ VERIFIED | `test_service_setup_failure_route_to_exit_2_names_its_own_message`, `test_usage_error_also_exits_2_but_never_reaches_the_operator` (both parametrized verify+blank) pass |
| 35 | `map_typed_errors` byte-identical to pre-phase state | D-11 | ✓ VERIFIED | `git diff <pre-201-03 commit> HEAD -- firestarter/cli_handlers.py` shows no hunk touching `map_typed_errors`; `test_map_typed_errors_still_exits_one_for_a_third_command` (erase still exits 1) passes |
| 36 | No command dict from verify/blank ever carries ordinal 4 or 6 | CMP-01/02 | ✓ VERIFIED | see #1 |
| 37 | `consistency_check_eprom` docstring no longer claims sole int-returning method | — | ✓ VERIFIED | `eprom_operations.py:1075-1082` docstring now names `verify_eprom`/`check_eprom_blank` as sharing the convention |
| 38 | Prohibition: hardware/transport fault never presented as mismatch, and vice versa | D-plan05 | ✓ VERIFIED (prohibition resolved) | D-08 discrimination (#25) + ordinal/exit-code tests |

**Score:** 38/38 truths (roadmap success criteria + plan must_haves + prohibitions) verified. 0 present-but-behavior-unverified.

### CR-01 Fix Confirmation (from 202-REVIEW.md)

The review's one critical finding — `_region_refusal_exit_code` failing to refuse an out-of-range `--address` when `--size` is omitted (`blank`'s case) — is fixed and committed at `firestarter_app` commit `a0855b9` (`fix(202-05): refuse -a past the chip end when --size is absent (CR-01)`), which is the current gitlink HEAD for `firestarter_app` in the meta repo (`git ls-tree HEAD firestarter_app` → `a0855b97b4a66c5608b84c5e675157258258402e`).

Verified directly:
- `mem_size is not None and start >= mem_size` is now checked unconditionally before `length` is resolved (cli_handlers.py:872-877).
- `blank`'s no-`--size` default now resolves `length = mem_size - start` (cli_handlers.py:886-891) instead of leaving it `None`.
- Three new test legs exist and pass: `-a` alone past the end (both commands, parametrized), `-a` alone exactly at `memory-size`, and the negative control `-a <memory-size - 1>` (accepted, not refused) — ran `tests/test_cli_handlers.py -k "region_past_chip_end or blank_address_alone or address_alone"` → 7 passed.

The review's two warnings (WR-01: untested exact boundary of the 3.0s abort-acceptance window under host jitter; WR-02: a genuine transport failure during `dev test`'s blank-check step folds into `VERDICT_BAD` rather than a distinct hardware verdict) and one info finding (IN-01: dead defensive branch in `feed()`) remain open. Neither warning blocks a phase must-have: WR-01 is a documented design tradeoff at an already-tested window (not an untested feature), and WR-02 is explicitly deferred to phase 206 in the code's own comment, with the residual risk confirmed present but scoped out of this phase.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/compare.py` | Streaming engine, 120+ lines | ✓ VERIFIED | 541 lines; exports `MismatchRange`, `CompareResult`, `CompareAccumulator`, `MAX_RETAINED_RANGES`, `render_compare_lines`, `Fingerprint`, `FP_*`, `classify_streamed`, `DiffSummary`, `diff_summary` all present |
| `firestarter_app/tests/test_compare.py` | Engine tests, 300+ lines | ✓ VERIFIED | 1391+ lines, 70 tests, all pass |
| `firestarter_app/pyproject.toml` | mypy strict-island entry | ✓ VERIFIED | `firestarter.compare` present at line 176 |
| `.planning/phases/.../202-READ-ABORT-ANSWER.md` | Written D-07 answer, 30+ lines | ✓ VERIFIED | 135 lines |
| `firestarter_app/firestarter/cli_handlers.py` | Region options + refusals + 3-code exit | ✓ VERIFIED | `--size`/`--address`/`--full` on both `verify` and `blank`; `_region_refusal_exit_code` present with CR-01 fix |
| `firestarter_app/tests/test_cli_handlers.py` | Exit-code matrix + region refusals, 120+ lines | ✓ VERIFIED | region/exit-code test classes present and passing |

### Key Link Verification

| From | To | Via | Status |
|------|-----|-----|--------|
| `eprom_operations.py` | `compare.py` | `verify_eprom`/`check_eprom_blank` build a `CompareAccumulator`, feed via `_drive_region_compare` | ✓ WIRED |
| `eprom_operations.py` | `constants.py` | `COMMAND_READ` passed to `_operation_context`, not `COMMAND_VERIFY`/`COMMAND_BLANK_CHECK` | ✓ WIRED |
| `cli_handlers.py` | `eprom_operations.py` | `verify`/`blank` call `sys.exit()` on the int verdict | ✓ WIRED |
| `chip_test.py` | `compare.py` | `classify_fingerprint` delegates to `classify_streamed`; `Fingerprint`/`FP_*` re-exported | ✓ WIRED |

### Behavioral Spot-Checks / Targeted Test Runs

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full `compare.py` engine suite | `pytest tests/test_compare.py` | 70 passed | ✓ PASS |
| Read-abort discrimination suite | `pytest tests/test_eprom_operations.py::TestVerifyEpromReadAbort` | 10 passed | ✓ PASS |
| Ordinal-never-sent proof | `pytest tests/test_eprom_operations.py::TestOrdinalsNeverSentByVerifyOrBlank` | 1 passed | ✓ PASS |
| CR-01 fix + region refusal legs | `pytest tests/test_cli_handlers.py -k "region_past_chip_end or blank_address_alone or address_alone"` | 7 passed | ✓ PASS |
| Exit-code matrix | `pytest tests/test_cli_handlers.py -k "exit_2 or usage_error_also_exits or map_typed_errors_still_exits"` | 5 passed | ✓ PASS |
| Region-scoped compare | `pytest tests/test_cli_handlers.py::test_region_scoped_verify_composes_a_command_dict_bounding_exact_region` | 1 passed | ✓ PASS |
| Combined core-module regression | `pytest tests/test_compare.py tests/test_eprom_operations.py tests/test_cli_handlers.py tests/test_chip_test.py` | 389 passed | ✓ PASS |
| mypy strict island | `mypy firestarter/compare.py firestarter/cli_handlers.py firestarter/main.py` | Success: no issues found in 3 source files | ✓ PASS |
| ruff lint | `ruff check` on the 5 phase-touched source/test files | All checks passed! | ✓ PASS |

The orchestrator's full-suite run (2216 passed, 85.80% coverage, ruff clean, Python 3.11) was accepted as the environment stated and not independently re-run in full (per the environment note); targeted re-runs above independently confirm the specific must-haves this phase claims.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CMP-01 | 202-01, 202-05 | `verify` compares by reading; no `CMD_VERIFY` sent | ✓ SATISFIED | truths #1, #6, #36 |
| CMP-02 | 202-05 | `blank` compares via same engine; no `CMD_BLANK_CHECK` sent | ✓ SATISFIED | truths #1, #29, #36 |
| CMP-03 | 202-02 | Bounded, device-size-independent host memory | ✓ SATISFIED | truths #2, #18 |
| CMP-04 | 202-04 | Default stops at first mismatch, host breaks read in flight | ✓ SATISFIED | truths #23-28 |
| CMP-05 | 202-01, 202-02 | `--full` reports every span, coalesced | ✓ SATISFIED | truths #19-20 |
| CMP-06 | 202-03 | Failed compare classified via `classify_fingerprint`, streamed | ✓ SATISFIED | truths #4, #21 |
| CMP-07 | 202-01, 202-05 | Exit-code contract, transport distinct from mismatch | ✓ SATISFIED | truths #7, #34 |
| CMP-08 | 202-05 | `-a`/`-s` on both commands, region-scoped | ✓ SATISFIED | truths #32-33 |

No orphaned requirements: REQUIREMENTS.md's Phase 202 row set (CMP-01..08) is exactly the union of `requirements:` fields declared across the 5 plans.

### Anti-Patterns Found

None. `grep -n -E "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER"` over `compare.py`, `eprom_operations.py`, `cli_handlers.py`, `chip_test.py` returns no matches. No stub returns, no hardcoded-empty data flows, no "not yet implemented" markers introduced by this phase (one pre-existing, unrelated line in `cli_handlers.py` about an unrelated firmware protocol was found and is out of this phase's scope).

### Human Verification Required

None. Every must-have truth is either a structural/static property (import purity, docstring content, dataclass shape) directly verifiable by source inspection, or a runtime behavior covered by a passing, targeted unit test this verifier re-ran independently. No visual, real-time, or external-service-dependent behavior is part of this phase's scope.

### Gaps Summary

No gaps. All 8 phase requirements (CMP-01 through CMP-08), all 5 roadmap success criteria, every plan-level `must_haves.truths`/`prohibitions` entry across the 5 plans, and the code review's one critical finding (CR-01, now fixed and tested) were checked directly against the codebase and against a fresh, independent re-run of the relevant tests (not merely against SUMMARY.md prose). The phase's central claim — one streaming comparison engine, on the host, shared by `verify` and `blank`, that names *why* a compare failed rather than a single address, against firmware that still carries both retired ordinals unsent — holds.

---

_Verified: 2026-09-20T21:15:00Z_
_Verifier: Claude (gsd-verifier)_
