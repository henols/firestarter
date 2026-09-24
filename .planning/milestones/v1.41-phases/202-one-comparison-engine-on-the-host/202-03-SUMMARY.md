---
phase: 202-one-comparison-engine-on-the-host
plan: 03
subsystem: verification
tags: [python, streaming-compare, eprom, fingerprint-classifier, ast-testing]

# Dependency graph
requires:
  - phase: 202-01
    provides: "`firestarter/compare.py`'s `CompareAccumulator`, `CompareResult`, `MismatchRange`, `render_compare_lines`, `MAX_RETAINED_RANGES`, `Fingerprint`/`FP_*` -- this plan adds the classifier that finally populates `CompareResult.fingerprint`"
  - phase: 202-02
    provides: "the accumulator's proven peak-allocation/runtime bounds and per-bit `_set_count` counters this plan exposes on `CompareResult` and consumes in `classify_streamed`"
provides:
  - "`firestarter/compare.py`: `classify_streamed` (the one divergence classifier) and `diff_summary` (the D-02 replacement for `chip_test._diff_offsets`), plus `DiffSummary` and three new `CompareResult` fields (`ff_count`, `first_offset`, `bit_set_counts`)"
  - "`chip_test.classify_fingerprint` delegates to `classify_streamed` via a `CompareAccumulator` -- D-02's single-divergence-primitive rule is enforced by code structure, not just stated in a comment"
  - "`CompareAccumulator.finalise()` always populates `CompareResult.fingerprint`; `render_compare_lines` appends the D-14 bucket summary line (classification, bad count, compared count, region total, compared address span per D-09) whenever a fingerprint is present"
  - "A 12-row D-03 corpus in `tests/test_compare.py` proving the streamed path and an independently transcribed pre-refactor batch reference agree on whole `Fingerprint` objects across all five buckets and four traps"
affects: [202-04, 202-05, 206]

# Actuals (#2632)
actuals:
  tokens: 15760
  tasks: 3
  commits: 3
  plan_head_before: 614989b9b50b19077816c66118226e5440f240d3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Online-then-filter classification: the accumulator counts every CANDIDATE bit it could ever need during feed() (bounded by each chunk's own absolute top address), and the classifier filters that superset down to the batch-equivalent candidate range (keyed on compared LENGTH, not absolute address) only at finalisation, since the correct upper bound is unknowable until the compare ends."
    - "Corpus equality against an independently transcribed reference, not a golden file: the D-03 test holds a hand-copied pre-refactor implementation in the test module itself, so the corpus proves two independent computations agree rather than one computation agreeing with itself."
    - "AST-based whole-tree import-purity scan (mirrors the Phase-109 SAFE-02 lesson already used for `diagnostic_report.py`): a substring grep false-positives on this module's own docstring prose describing the safety property it enforces."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/compare.py
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_compare.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_cli_handlers.py

key-decisions:
  - "D-14's bucket line stays inside eprom_operations.verify_eprom's existing logger.info call (202-01's shape), not moved to a click.echo in cli_handlers.verify as CONTEXT.md/RESEARCH.md's architecture sketch implied -- the current shape already satisfies D-05 (compare.py returns strings, the service layer echoes) and moving the echo would be an unrequested refactor beyond this plan's scope."
  - "The Task 3 CliRunner acceptance test asserts against caplog.text, not result.output -- a pre-built obj=app skips cli()'s _setup_logging test-mode short-circuit, so result.output is always empty for logger.info output under pytest regardless of behavior (the same measured fact tests/test_cli_handlers.py's test_info_elevated_programming_vcc_warns already documented)."
  - "FP_ADDRESS_LINE/FP_BLANK_CONTACT/FP_INDETERMINATE/FP_TRANSPORT/_FF_RATIO_THRESHOLD stay imported into chip_test.py with # noqa: F401 for backward-compatible re-export -- tests/test_chip_test_sdp_leg.py and tests/test_diagnostic_report.py import them FROM firestarter.chip_test, not firestarter.compare, continuing 202-01's zero-test-churn contract for Fingerprint/FP_MATCH."
  - "classify_fingerprint's own explicit classify_streamed call (Task 2) and finalise()'s new auto-classification (Task 3) both run on every classify_fingerprint call, computing the Fingerprint twice. Not optimized away: Task 2 was implemented and verified before Task 3 wired finalise()'s auto-population, so classify_fingerprint could not yet rely on result.fingerprint when its own <verify> ran. Cheap (one compare's evidence dict, not a device-sized structure); documented rather than silently left for a future reader to \"simplify\" without understanding why."

requirements-completed: [CMP-06]

coverage:
  - id: D1
    description: "chip_test.classify_fingerprint keeps its exact signature and returns a Fingerprint equal, field for field including the evidence dict, to the one the pre-refactor batch implementation returns, across a corpus spanning all five buckets"
    requirement: "CMP-06"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestClassifyFingerprintCorpus::test_streamed_and_batch_reference_agree"
        status: pass
      - kind: unit
        ref: "tests/test_compare.py#TestClassifyFingerprintCorpus::test_corpus_covers_all_five_buckets"
        status: pass
    human_judgment: false
  - id: D2
    description: "chip_test._diff_offsets no longer exists, its one in-module caller consumes compare.diff_summary, and no materialised list of every mismatching offset is built anywhere on the classification path"
    requirement: "CMP-06"
    verification:
      - kind: unit
        ref: "chip_test module attribute check (verify block): assert not hasattr(c, '_diff_offsets')"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_the_agreeing_branch_never_calls_the_per_byte_diff_primitive"
        status: pass
    human_judgment: false
  - id: D3
    description: "A failed comparison carries a classify_fingerprint bucket computed from the streamed accumulator's counters, and CompareResult.fingerprint is populated for every finalise() call, clean or mismatching"
    requirement: "CMP-06"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestFinaliseAlwaysClassifies"
        status: pass
    human_judgment: false
  - id: D4
    description: "verify prints exactly one bucket summary line after the range lines, carrying the classification, the bad count, the compared count, the region total and the compared address span"
    requirement: "CMP-06"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestRenderCompareLines::test_bucket_summary_line_exact_text"
        status: pass
      - kind: unit
        ref: "tests/test_compare.py#TestRenderCompareLines::test_bucket_summary_line_is_last_and_exactly_one"
        status: pass
      - kind: integration
        ref: "tests/test_cli_handlers.py#test_verify_cli_prints_range_line_and_bucket_summary_line"
        status: pass
    human_judgment: false
  - id: D5
    description: "The corpus pins the four traps: bit-clustering keys only for the finalisation range, a suspected-line tie resolves to the lowest bit, a 256-byte region produces empty bit-clustering while 257 does not, and zero-/unequal-length inputs return zero totals without raising"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestClassifyStreamed (256/257 boundary, tie, zero-length tests)"
        status: pass
      - kind: unit
        ref: "tests/test_compare.py#TestDiffSummary"
        status: pass
    human_judgment: false
  - id: D6
    description: "test_generate_pattern_and_classify_fingerprint_source_unchanged follows the moved logic into compare.py, so the guard it was written for is still enforced"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_generate_pattern_and_classify_fingerprint_source_unchanged"
        status: pass
    human_judgment: false
  - id: D7
    description: "compare.py's whole-tree import set names none of firestarter.eprom_operations, firestarter.chip_test, firestarter.serial_comm or click"
    requirement: "CMP-06 (D-01)"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestImportPurity::test_no_forbidden_import_anywhere_in_compare_py"
        status: pass
    human_judgment: false

duration: ~110min
completed: 2026-09-20
status: complete
---

# Phase 202 Plan 03: One Divergence Implementation and the Diagnosis Line Summary

**`chip_test.classify_fingerprint` now delegates to a new `compare.classify_streamed`, `_diff_offsets` is deleted outright, and every compare carries a D-14 bucket-summary line -- proven bit-for-bit equal to the retired batch implementation by a 12-row corpus.**

## Performance

- **Duration:** ~110 min
- **Completed:** 2026-09-20
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 5, all in `firestarter_app` (2 production, 3 test), across 3 app commits + 3 meta gitlink-advance commits

## Accomplishments

- `firestarter/compare.py` gained `classify_streamed` (the one divergence classifier, reproducing `chip_test.classify_fingerprint`'s pre-refactor bucket order, evidence-key set, clustering-range filter, tie-breaking and empty-input behaviour bit for bit) and `diff_summary`/`DiffSummary` (the D-02 replacement for `chip_test._diff_offsets`, returning a bad count instead of a materialised offset list). `CompareResult` gained `ff_count`, `first_offset` and `bit_set_counts` so the classifier has the counters it needs.
- `chip_test.classify_fingerprint`'s body is now a thin delegating wrapper: it builds a `CompareAccumulator` over the common prefix, feeds it once, finalises, and returns `classify_streamed`'s verdict. `_diff_offsets` is deleted; its one remaining in-module caller (`_dispatch_read`'s multi-run divergence block) is re-pointed at `compare.diff_summary`.
- `CompareAccumulator.finalise()` now calls `classify_streamed` unconditionally, so `CompareResult.fingerprint` is populated for every compare -- clean or mismatching -- without any caller asking separately. `render_compare_lines` appends exactly one D-14 bucket summary line after any range/tail lines, in the form `{classification}, {bad} bad of {compared} compared of {total} (0xSTART-0xEND)`.
- A 12-row D-03 corpus in `tests/test_compare.py` asserts whole-`Fingerprint` equality between the delegating `classify_fingerprint` and an independently transcribed pre-refactor batch reference, spanning all five buckets and the four measured traps (a compared length of exactly 256 vs. 257, a bit-index tie, and zero-/unequal-length inputs).
- `test_generate_pattern_and_classify_fingerprint_source_unchanged` (the source-pin guard RESEARCH.md flagged as about to become vacuous) now also inspects `classify_streamed` and `CompareAccumulator.feed`, so it still enforces the region-constant leak-out guard after the logic moved. A new AST-based whole-tree import-purity scan pins D-01 for `compare.py`. A new `CliRunner`-driven integration test in `tests/test_cli_handlers.py` proves a real `verify` invocation (not a mocked operator) logs both a range line and the bucket line through production code.

## Task Commits

1. **Task 1: Streamed fingerprint finalisation that reproduces the batch shape exactly** — app `d6a35df`, meta `42bf7bbc`
2. **Task 2: Delegate the classifier and delete the materialised offset list** — app `3b12b9a`, meta `6ddf4424`
3. **Task 3: The diagnosis line, and two guards that must not become theatre** — app `6eed1ed`, meta `baa66e88`

**Plan metadata:** *(this commit, immediately following)*

## Files Created/Modified

- `firestarter_app/firestarter/compare.py` — `classify_streamed`, `diff_summary`, `DiffSummary` added; `CompareResult` gains `ff_count`/`first_offset`/`bit_set_counts`; `CompareAccumulator.finalise()` always classifies; `render_compare_lines` gains the D-14 bucket line
- `firestarter_app/firestarter/chip_test.py` — `classify_fingerprint` delegates; `_diff_offsets` and its preceding rule comment deleted (comment moved to `compare.py`); `_dispatch_read`'s divergence block re-pointed at `diff_summary`; `FP_*`/`_FF_RATIO_THRESHOLD` re-export preserved with `# noqa: F401`
- `firestarter_app/tests/test_compare.py` — 16 direct `classify_streamed`/`diff_summary` unit tests (Task 1), the 12-row D-03 corpus + 2 coverage-shape tests (Task 2), 2 `render_compare_lines` bucket-line tests + 1 no-fingerprint test + `TestFinaliseAlwaysClassifies` (3 tests) + `TestImportPurity` (Task 3). Test count in this file: 33 → 70.
- `firestarter_app/tests/test_chip_test.py` — `test_diff_offsets_equal_arrays`/`test_diff_offsets_known_positions` retired (superseded by `test_compare.py`'s direct `diff_summary` tests); `test_diff_offsets_unequal_length` re-pointed at `diff_summary`; `test_the_agreeing_branch_never_calls_the_per_byte_diff_primitive` monkeypatches `diff_summary` instead of `_diff_offsets`; `test_generate_pattern_and_classify_fingerprint_source_unchanged` extended to inspect `classify_streamed`/`CompareAccumulator.feed`
- `firestarter_app/tests/test_cli_handlers.py` — new `test_verify_cli_prints_range_line_and_bucket_summary_line`, driving a real `EpromOperator` through the fake-serial harness

## Decisions Made

- **D-14's echo stays where 202-01 put it** (inside `eprom_operations.verify_eprom`'s `logger.info` loop), not moved into `cli_handlers.verify` as an echo — the existing shape already satisfies D-05, and relocating it would be an unrequested architectural change.
- **The CLI acceptance test uses `caplog.text`, not `result.output`** — a pre-built `obj=app` skips `cli()`'s `_setup_logging`, so `result.output` is always empty for logged output under pytest (measured, matching this file's own documented precedent).
- **`FP_*`/`_FF_RATIO_THRESHOLD` stay re-exported from `chip_test.py`** with `# noqa: F401`, for two sibling test modules that import them from there.
- **`classify_fingerprint` computes its `Fingerprint` twice per call** (once inside `finalise()`, discarded; once via its own explicit `classify_streamed` call) — a consequence of implementing Task 2 before Task 3 wired `finalise()`'s auto-population. Cheap and correct; documented rather than silently optimized without explanation.

## Deviations from Plan

None — plan executed exactly as written. `ruff check --fix` initially removed the `FP_*`/`_FF_RATIO_THRESHOLD` imports from `chip_test.py` as "unused" after the delegation landed; caught immediately (would have broken two sibling test modules' imports) and restored by hand with `# noqa: F401` and an explanatory comment before any commit landed — not a deviation from the plan's own scope, just a mechanical correction to an auto-fix tool's blind spot.

## Issues Encountered

None beyond what is documented above under Decisions.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Exactly one divergence implementation exists (`compare.classify_streamed`), and `chip_test.classify_fingerprint` delegates to it — D-02 is now enforced by code structure.
- `CompareResult.fingerprint` is populated for every compare; `render_compare_lines`'s output now always ends with the D-14 bucket line when a fingerprint is present. `verify_eprom` (the only current caller) surfaces both automatically.
- `classify_streamed`/`diff_summary` are ready for phase 203's write guard and phase 206's `dev test` migration to consume directly.
- 202-04 (abort mechanism, `abort_predicate`) and 202-05 (`blank` joining the engine, `--size`/`-a` options, exit-code closure) remain unimplemented.
- Both `firestarter_app` and the meta repo remain on `v1.41-verification-to-host`; no stray branch. `firestarter_app` HEAD before this plan: `614989b`; meta HEAD before this plan: `fb14baa2`.
- Full suite: 2180 tests collected (up from 2144), full run green (coverage 85.76%, `Required test coverage of 70% reached`, 36/36 snapshots). `ruff check`/`ruff format --check` clean over `firestarter/ tests/`. `mypy firestarter/compare.py firestarter/cli_handlers.py firestarter/main.py`: no issues. `mypy firestarter/ tests/` (full CI scope): 32 errors in 12 files, unchanged from the pre-phase baseline.

---
*Phase: 202-one-comparison-engine-on-the-host*
*Completed: 2026-09-20*

## Self-Check: PASSED

- `firestarter_app/firestarter/compare.py` — FOUND, modified (classify_streamed/diff_summary/DiffSummary added, finalise() wired)
- `firestarter_app/firestarter/chip_test.py` — FOUND, modified (classify_fingerprint delegates, _diff_offsets deleted)
- `firestarter_app/tests/test_compare.py` — FOUND, modified (33 → 70 tests)
- `firestarter_app/tests/test_chip_test.py` — FOUND, modified
- `firestarter_app/tests/test_cli_handlers.py` — FOUND, modified
- App commits `d6a35df`, `3b12b9a`, `6eed1ed` — FOUND in `git log --oneline --all`
- Meta commits `42bf7bbc`, `6ddf4424`, `baa66e88` — FOUND in `git log --oneline --all`
- Both repos on `v1.41-verification-to-host`, no stray branch
- `firestarter.chip_test` no longer has `_diff_offsets`: confirmed (`primitive retired`)
- `tests/test_compare.py tests/test_chip_test.py tests/test_cli_handlers.py`: 300/300 passed
- Full suite (`pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70 -q`): green, `Required test coverage of 70% reached. Total coverage: 85.76%`, 36/36 snapshots, no FAILED/ERROR lines (note: the plan's literal `-q` doubles pyproject's own `-q` addopts, which suppresses the final count line per a known project quirk — dot output reaching `[100%]` with zero F/E markers and the coverage gate passing is the available proof)
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`: clean
- `mypy firestarter/compare.py firestarter/cli_handlers.py firestarter/main.py`: no issues
- `mypy firestarter/ tests/` (full CI scope): 32 errors in 12 files — unchanged from the 202-01/202-02 baseline
