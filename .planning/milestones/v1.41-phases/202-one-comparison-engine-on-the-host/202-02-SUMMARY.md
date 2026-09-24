---
phase: 202-one-comparison-engine-on-the-host
plan: 02
subsystem: verification
tags: [python, tracemalloc, ast, streaming-compare, eprom, performance-testing]

# Dependency graph
requires:
  - phase: 202-01
    provides: "`firestarter/compare.py`'s `CompareAccumulator`, `CompareResult`, `MismatchRange`, `render_compare_lines`, `MAX_RETAINED_RANGES`, which this plan measures and closes coverage gaps on without changing their public shape"
provides:
  - "CMP-03 proven, not merely claimed: peak traced allocation for a 512 KiB-scale compare is bounded (measured under 1 MiB with ~30x margin) and flat in device size across all four fault patterns"
  - "The unflagged runtime trap RESEARCH.md found (a literal per-byte, per-bit D-02 reading costing 19.8-21.4s) is now a failing test if it regresses: two perf_counter timing gates plus a machine-speed-independent AST structural proof"
  - "CMP-05's engine half completed: coalescing/adjacency, ordering determinism, the empty/single-byte edge cases, the MAX_RETAINED_RANGES boundary at N-1/N/N+1, and the alternating-pattern tail-counter exactness at the ~262144-range 512 KiB worst case"
affects: [202-03, 202-04, 202-05, 206]

# Actuals (#2632)
actuals:
  tokens: 5662
  tasks: 3
  commits: 3
  plan_head_before: 676a39d

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "tracemalloc-wrapped synthetic chunk feed against CompareAccumulator, with fixture construction (chunk materialisation) always outside the traced/timed region -- both for accuracy (the traced peak reflects the accumulator's own footprint, not chunk generation) and for the timing tests' 'measure only feed+finalise' requirement."
    - "AST-based structural proof as a companion to a wall-clock timing test: parse the target method's own source with `ast`, assert the performance-critical code shape exists (an early-return equality fast path ahead of any per-offset loop) independent of machine speed. Same idiom precedent as `test_compare.py` module docstring's cited AST import-purity check."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/compare.py
    - firestarter_app/tests/test_compare.py

key-decisions:
  - "Deviation, disclosed plainly: the four-fault-pattern peak-allocation ceiling test traces at 128 KiB, not the plan's literal 512 KiB. Measured reason: tracemalloc's own per-allocation tracing overhead (not the algorithm -- the untraced runtime test proves the algorithm itself takes well under 1s at 512 KiB) pushed the all-differing/alternating cases to 5-12s under trace, intermittently exceeding this file's own 10-second-per-test <verify> gate (observed one run at 12.39s). 128 KiB reproduces the same measured peak (~35KB vs ~37KB at 512 KiB, ~6% difference) in a stable ~1-2s. The existing 128KiB-vs-512KiB flatness test (traces the cheap single-byte pattern directly at 512 KiB) is what actually proves the peak does not grow at the full 512 KiB scale; combined, the two tests still fully cover the CMP-03 claim at 512 KiB with wide margin (128 KiB's peak sits ~30x under the ceiling; doubling it per the flatness bound still leaves ~15x)."
  - "Rejected a 'warm-start' tracing trick (feed most chunks untraced, trace only the tail) that measured as both fast (0.2s) and passing for the current implementation -- discarded after verifying it would NOT catch a device-sized buffer allocated once upfront (e.g. in `__init__`), since tracemalloc only tracks allocations made after `tracemalloc.start()`. Chose the smaller-but-fully-traced-from-chunk-0 approach instead, which preserves the test's actual regression-detection purpose."
  - "Chunk size stays literally 1024 bytes (the real Leonardo board buffer size) and chunk delivery mirrors `_main_phase_read_data`'s monotonically-increasing-address contract exactly -- only total device size was reduced for the two allocation-heavy patterns, not chunking granularity, since RESEARCH.md's own numbers are tied to that exact chunk size."

requirements-completed: [CMP-03, CMP-05]

coverage:
  - id: D1
    description: "Peak traced allocation for a compare is under 1 MiB across all four fault patterns (clean, one bad byte, every byte differing, alternating) and does not grow when the simulated device size doubles"
    requirement: "CMP-03"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorPeakAllocation::test_peak_allocation_under_ceiling"
        status: pass
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorPeakAllocation::test_peak_allocation_flat_in_device_size"
        status: pass
    human_judgment: false
  - id: D2
    description: "A clean 512 KiB-scale compare completes in under 1.0s and the worst-case all-differing compare in under 8.0s; a machine-speed-independent structural test proves the discriminating code shape (equality fast path before any per-offset loop) independently of timing"
    requirement: "CMP-03"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorRuntime::test_all_matching_512kib_runtime_under_one_second"
        status: pass
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorRuntime::test_all_differing_512kib_runtime_under_eight_seconds"
        status: pass
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorFastPathStructure::test_fast_path_precedes_per_offset_loop"
        status: pass
    human_judgment: false
  - id: D3
    description: "A mismatching span straddling a chunk boundary coalesces into one MismatchRange; two spans separated by exactly one matching byte stay two ranges; two touching spans merge into one; no two retained ranges touch or overlap"
    requirement: "CMP-05"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorAdjacencyAndOverlap"
        status: pass
    human_judgment: false
  - id: D4
    description: "ranges is ordered ascending by start, and identical input produces identical output on every run"
    requirement: "CMP-05"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorOrdering"
        status: pass
    human_judgment: false
  - id: D5
    description: "A zero-length region and a single-byte region (matching and differing) both produce a well-formed CompareResult rather than an exception"
    requirement: "CMP-03"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorEmptyAndSingleByte"
        status: pass
    human_judgment: false
  - id: D6
    description: "At exactly MAX_RETAINED_RANGES-1, MAX_RETAINED_RANGES, and MAX_RETAINED_RANGES+1 coalesced ranges, nothing is dropped below the cap and extra_ranges/extra_bytes are exact past it, using the module's real default cap"
    requirement: "CMP-05"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorRangeCapBoundary"
        status: pass
    human_judgment: false
  - id: D7
    description: "extra_ranges and extra_bytes are exact for the alternating 512 KiB worst case (~262144 coalesced ranges): extra_ranges + cap equals the true total, extra_bytes + retained counts equals bad exactly, and bad/count are int not float"
    requirement: "CMP-05"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorAlternatingPrecision::test_extra_ranges_and_extra_bytes_exact_for_512kib_alternating"
        status: pass
    human_judgment: false
  - id: D8
    description: "The standing prohibition holds: a count or classification must never be presented as covering more of the device than was actually compared or counted -- the retained-range cap bounds what is shown, never what is counted"
    verification:
      - kind: unit
        ref: "tests/test_compare.py#TestCompareAccumulatorAlternatingPrecision, TestCompareAccumulatorRangeCapBoundary"
        status: pass
    human_judgment: false

duration: ~65min
completed: 2026-09-20
status: complete
---

# Phase 202 Plan 02: Peak-Allocation and Runtime Proofs, and the Compare Accumulator's Coalescing/Cap-Honesty Summary

**The compare engine's two hardest-to-see properties -- bounded memory and bounded runtime, both independent of device size -- are now failing tests if they regress, plus full CMP-05 engine coverage for coalescing, ordering and the range-cap's exactness.**

## Performance

- **Duration:** ~65 min
- **Completed:** 2026-09-20
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 2 (`firestarter/compare.py`, `tests/test_compare.py`), all in `firestarter_app`

## Accomplishments

- **Peak-allocation ceiling proven** (CMP-03, T-202-01 mitigation): a 1 MiB traced-peak ceiling, with its derivation recorded as a comment, asserted across all four RESEARCH.md fault patterns (all-match, single-byte, all-differ, alternating), plus a flatness assertion (128 KiB vs 512 KiB peaks within 2x) that turns "bounded independently of device size" into a measured property.
- **The unflagged runtime trap is now a gate, not a claim** (T-202-05 mitigation): two `perf_counter` timing tests (clean under 1.0s, worst-case all-differing under 8.0s) plus an `ast`-based structural test proving the equality fast path precedes any per-offset loop in `feed()` -- the structural test is what actually catches a regression reliably on fast hardware, where the timing bounds alone (measured 0.0005s clean / 0.63s worst-case on this devcontainer, vs the plan's 1.0s/8.0s bounds) carry far more margin than RESEARCH.md's cited machine implied.
- **CMP-05's engine half completed**: chunk-boundary-straddling coalescing, one-byte-gap vs touching-span adjacency, the no-touch/no-overlap invariant, ordering determinism, the empty/single-byte edge cases, the `MAX_RETAINED_RANGES` boundary at N-1/N/N+1 with the real default cap, and the alternating-pattern's ~262144-range 512 KiB worst case proving `extra_ranges`/`extra_bytes` stay exact past the cap.
- Two comments added at load-bearing sites in `compare.py`: the per-chunk offset-list construction (naming the rejected counter-only alternative and its measured 21.4s/1.9s, ~79KB cost difference) and the range-cap check in `_close_open_range` (naming the standing prohibition: the cap bounds what is shown, never what is counted).

## Task Commits

1. **Task 1: Peak allocation stays under 1 MiB and flat in device size** - `b849c5f` (test)
2. **Task 2: The compare is not slower than the firmware path it replaces** - `cd0b6ff` (test)
3. **Task 3: Coalescing, ordering and the honesty of the capped range list** - `614989b` (test)

Meta-repo gitlink advances: `13de087e`, `d501e772`, `6fa9190b` (one per task).

**Plan metadata:** *(this commit, immediately following)*

## Files Created/Modified

- `firestarter_app/tests/test_compare.py` — 21 new tests across 8 new test classes: `TestCompareAccumulatorPeakAllocation`, `TestCompareAccumulatorRuntime`, `TestCompareAccumulatorFastPathStructure`, `TestCompareAccumulatorAdjacencyAndOverlap`, `TestCompareAccumulatorOrdering`, `TestCompareAccumulatorEmptyAndSingleByte`, `TestCompareAccumulatorRangeCapBoundary`, `TestCompareAccumulatorAlternatingPrecision`; plus a new `_iter_chunks` synthetic chunk-generator helper and a `PEAK_ALLOCATION_CEILING_BYTES` module constant. Test count: 12 → 33.
- `firestarter_app/firestarter/compare.py` — two comments added (no behavior change): at the per-chunk offset-list construction in `feed()`, and at the cap check in `_close_open_range()`.

## Decisions Made

- **Peak-allocation ceiling test traces at 128 KiB, not the plan's literal 512 KiB** — see key-decisions above and Deviations below for the full measured rationale. This is the plan's one substantive deviation.
- **The `MAX_RETAINED_RANGES` boundary tests use the module's real default cap** rather than an overridden small `max_ranges` (unlike 202-01's `TestCompareAccumulatorRangeCap`, which uses `max_ranges=2` for a cheap smoke test) — Task 3 explicitly wanted the boundary proven at the shipped constant's actual value.
- **Chunks are always pre-materialised into a list before `tracemalloc.start()` or `time.perf_counter()` begins**, in every new test — both for the timing tests' explicit "measure only feed+finalise" requirement and, for the peak tests, so the traced peak reflects the accumulator's own footprint rather than the synthetic generator's chunk construction.

## Deviations from Plan

### Auto-fixed issues

**1. [Rule 3 - Blocking] The plan's literal "512 KiB, all four patterns" peak-allocation test intermittently exceeded the plan's own 10-second-per-test `<verify>` gate**

- **Found during:** Task 1's own acceptance-criteria verification loop, then re-confirmed while verifying Task 2's `<verify>` block (which runs `--durations=5` over the whole file and is the actual enforcement point).
- **Issue:** `tracemalloc`'s own per-allocation tracing overhead — not the algorithm itself — made a full-trace of the all-differing and alternating fault patterns at 512 KiB take 5-12s across repeated runs on this shared devcontainer (one observed run: 12.39s), intermittently exceeding Task 2's `<verify>` block's stated failure condition ("any single test in tests/test_compare.py at or above 10 seconds"). Root-caused via targeted micro-benchmarks: removing the untested, not-yet-consumed per-bit clustering evidence loop (built in 202-01 for 202-03's future `classify_streamed`, but not exposed on `CompareResult` yet) dropped the traced time from ~8s to ~2.5s, confirming that loop's generator-based `sum(1 for o in offs if ...)` calls are what tracemalloc's tracing overhead disproportionately penalises — not the per-chunk offset list itself.
- **Fix considered and rejected:** a "warm-start" trick (feed most of the device untraced, then trace only the last few chunks) measured as fast (0.2s) and passing for the current implementation, but was proven — by constructing a hypothetical device-sized-buffer regression allocated once in `__init__` — to be blind to exactly the class of regression this test exists to catch (tracemalloc only tracks allocations made after `tracemalloc.start()`; a pre-existing buffer is invisible). Discarded before it was ever committed.
- **Fix applied:** the four-pattern ceiling test now traces a 128 KiB device (chunk size, delivery order, and all four fault-pattern shapes unchanged) instead of 512 KiB. Measured peak at 128 KiB (~35KB) is within ~6% of the peak at 512 KiB (~37KB) for the worst-case all-differing pattern, confirming the reduction does not weaken the assertion. The pre-existing `test_peak_allocation_flat_in_device_size` test (added in Task 1, using the cheap single-byte pattern, unaffected by this timing pressure) is what directly exercises 512 KiB and proves the peak does not grow between 128 KiB and 512 KiB — so the two tests together still fully cover the plan's CMP-03 claim at the full 512 KiB scale, with substantial margin (128 KiB's peak sits ~30x under the 1 MiB ceiling; even doubled per the flatness bound, ~15x remains).
- **Files modified:** `tests/test_compare.py` (the fix; comment/docstring disclosure at the test class itself, not just here).
- **Verification:** re-ran the full `tests/test_compare.py` suite with `--durations` 6 times after the fix; slowest observed run was 2.93s for the all-differing case (previously 5-12s), all 33 tests passing every time.
- **Committed in:** `cd0b6ff` (Task 2's commit — the fix landed alongside Task 2's own new tests since it was discovered while verifying Task 2's `<verify>` block, which is the gate the regression actually tripped).

### Process note (disclosed, not softened)

The per-bit clustering evidence computation in `CompareAccumulator.feed()` (202-01 code, unmodified by this plan) is currently computed on a per-chunk-local address basis (`top_addr = address + chunk_len - 1`, i.e. relative to each 1024-byte chunk, not the whole device), and its output (`self._set_count`) is not yet exposed on `CompareResult` at all — it exists solely for 202-03's future `classify_streamed`. This plan did not touch or fix that shape, since it is out of this plan's stated scope (Tasks 1-3 cover peak/runtime/coalescing, not classification), but it is worth flagging for 202-03: a device-wide bit range (not a per-chunk one) is very likely what `classify_streamed`'s address-line clustering will actually need, and the current per-chunk range looks incidental to the streaming refactor rather than deliberate. Not filed to WINDOWS.md since nothing here is untested or broken today — it is a forward-looking implementation note for whoever picks up 202-03.

---

**Total deviations:** 1 auto-fixed (Rule 3, test-methodology-only, fully disclosed) + 1 forward-looking process note (no action taken, no defect).
**Impact on plan:** The deviation only changes the SIZE of one synthetic test fixture; it does not weaken CMP-03's coverage (proven via the combination of the 128 KiB ceiling test and the existing 128-vs-512 KiB flatness test) and does not touch production code beyond two explanatory comments. No scope creep.

## Issues Encountered

None beyond what is documented above under Deviations.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- CMP-03 (peak memory, runtime) and CMP-05's engine half (coalescing, ordering, cap exactness) are now both proven by failing-if-broken tests, not just implemented.
- `classify_streamed`/`DiffSummary`/`diff_summary` (202-03) and the abort mechanism (`abort_predicate`, 202-04) remain unimplemented; `CompareResult.fingerprint` still defaults to `None` from this plan.
- **Flag for 202-03:** the per-bit clustering evidence in `feed()` computes its bit range from each chunk's own local top address, not the whole device's — see the Deviations "Process note" above. Worth reviewing when `classify_streamed` starts consuming `_set_count`.
- Both `firestarter_app` and the meta repo remain on `v1.41-verification-to-host`; no stray branch. `firestarter_app` HEAD before this plan: `676a39d`; meta HEAD before this plan: `173546d2`.
- Full suite: 2144 passed, 0 failed, 85.70% coverage (was 2123/85.70% before this plan — net +21 tests, all in `test_compare.py`). `ruff check`/`ruff format --check` clean. `mypy firestarter/compare.py firestarter/cli_handlers.py firestarter/main.py`: no issues. `mypy firestarter/ tests/` (full CI scope): 32 errors in 12 files, unchanged from the pre-phase baseline.

---
*Phase: 202-one-comparison-engine-on-the-host*
*Completed: 2026-09-20*

## Self-Check: PASSED

- `firestarter_app/firestarter/compare.py` — FOUND, modified (2 comments added)
- `firestarter_app/tests/test_compare.py` — FOUND, modified (21 tests added, 12 → 33)
- App commits `b849c5f`, `cd0b6ff`, `614989b` — FOUND in `git log --oneline --all`
- Meta commits `13de087e`, `d501e772`, `6fa9190b` — FOUND in `git log --oneline --all`
- Both repos on `v1.41-verification-to-host`, no stray branch
- `tests/test_compare.py`: 33/33 passed, slowest test 2.93s (well under the 10s `<verify>` ceiling), repeated 6+ times for stability
- Full suite (`pytest tests/ --cov=firestarter --cov-fail-under=70`): 2144 passed, 0 failed, 85.70% coverage, 36/36 snapshots
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`: clean
- `mypy firestarter/compare.py firestarter/cli_handlers.py firestarter/main.py`: no issues
- `mypy firestarter/ tests/` (full CI scope): 32 errors in 12 files — unchanged from the 202-01 baseline (operator-verified there as matching the pre-phase count)
