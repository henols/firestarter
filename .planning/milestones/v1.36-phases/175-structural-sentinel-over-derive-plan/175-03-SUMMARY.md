---
phase: 175-structural-sentinel-over-derive-plan
plan: 03
subsystem: testing
tags: [derive_plan, chip_test, structural-sentinel, prune-05, prune-06, committed-artifact, drift-gate]

requires:
  - phase: 175-structural-sentinel-over-derive-plan
    plan: 01
    provides: "tests/plan_corpus.py shared REAL_DB / PART_NUMBERS / all_rows / plan_corpus() surface this plan's generator imports rather than rebuilding"
provides:
  - "tests/fixtures/plan_shapes.json -- the frozen half of D-10's no-drop proof: 8 shape families at the (op, supported) grain over all 677 shipped part numbers, six absolutely-asserted aggregates"
  - "tools/measure_plan_shapes.py -- validate-before-emit generator with --check and a --planted-fault seam (chip-count-skew, orphan-family, empty-chips), exit codes 0/1/2"
  - "tests/test_plan_shapes_drift.py -- six-leg drift gate, no skip marker, byte-identical regeneration proof"
affects: [175-04, 175-05, 177]

actuals:
  tokens: 14964
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Committed-artifact + generator + drift-test trio (Phase 174's D-16 precedent), generator imports the shared test-side corpus instead of building a second EpromDatabase"
    - "A generator whose only external input is the shipped database plants its own validate-before-emit faults through a --planted-fault seam rather than an external file argument, since the database must never be mutated"
    - "validate(payload) recomputes from the corpus rather than only checking internal payload self-consistency -- total_steps, unsupported_steps, and family-token bijection are all re-derived independently and compared"

key-files:
  created:
    - firestarter_app/tools/measure_plan_shapes.py
    - firestarter_app/tests/fixtures/plan_shapes.json
    - firestarter_app/tests/test_plan_shapes_drift.py
    - .planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-03-plan-shapes-drift.txt
  modified: []

key-decisions:
  - "The (op, supported) grain (8 families over 16 distinct (op, supported) sequences) is a deliberate STRENGTHENING of CONTEXT's D-10, not a departure from it. D-10's '4 distinct op-sequences' correctly measures the op-only grain; the finer grain costs nothing in artifact size while catching an SDP supported flip on 40 chips that leaves the op-only sequence byte-identical -- exactly PRUNE-05's concern, and exactly what an alignment-only no-drop proof (175-04's execution half) structurally cannot see, since a prune shrinks Plan.steps and the results list together and alignment still holds."
  - "Family identity is a pure function of a chip's full-scope plan (id-check presence, blank-check position relative to the write step, erase presence, SDP-leg presence), and this scheme is bijective with the actual (op, supported) sequence by construction, because derive_plan's own op ORDER is itself a function of exactly these same facts. validate() proves the bijection empirically (recomputing every chip's shape and comparing same-family members) rather than assuming it holds."
  - "Keyed by part_number, not by database row -- 746 rows collapse to 677 unique names via derive_plan's own resolution, so a row-keyed artifact would carry 69 duplicate values that can never diverge."
  - "The three planted faults (chip-count-skew, orphan-family, empty-chips) are injected through the generator's own --planted-fault seam applied to the already-derived payload, immediately before validate() -- the generator's only external input is the shipped database, which must not be mutated, so there is no --issues-style file argument to corrupt as the analog does."
  - "Measured, not assumed, and every pinned number matched on first measurement: rows=746, distinct_part_numbers=677, plans=1354, distinct_shape_families=8, total_steps=16248, unsupported_steps=9304, and all 8 family chip counts (197, 180, 90, 76, 41, 40, 27, 26) exactly matching 175-RESEARCH.md section F. No disagreement to report against the plan's own text this time."

requirements-completed: [PRUNE-05, PRUNE-06]

coverage:
  - id: D1
    description: "The committed plan-shape pin: 8 shape families over the 16 distinct (op, supported) sequences, keyed by part_number over all 677 unique names, with six absolutely-asserted aggregates (rows 746, distinct_part_numbers 677, plans 1354, distinct_shape_families 8, total_steps 16248, unsupported_steps 9304)"
    requirement: PRUNE-05
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_plan_shapes_drift.py#test_committed_artifact_exists_and_carries_the_generated_by_banner"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_plan_shapes_drift.py#test_aggregate_numbers_are_asserted_absolutely_not_only_for_drift"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_plan_shapes_drift.py#test_family_and_chip_maps_are_closed_and_internally_consistent"
        status: pass
    human_judgment: false
  - id: D2
    description: "The generator validates before it emits and is proven able to fail: three planted faults through --planted-fault, plus --check against a nonexistent target and against a one-byte-altered copy, all five observed to exit non-zero while leaving the committed artifact byte-unchanged"
    requirement: PRUNE-05
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_plan_shapes_drift.py#test_planted_faults_exit_non_zero_and_write_nothing"
        status: pass
      - kind: other
        ref: ".planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-03-plan-shapes-drift.txt (five observed non-zero exits, plus the one-byte-altered-copy leg run directly against the generator)"
        status: pass
    human_judgment: false
  - id: D3
    description: "A fresh regeneration is byte-identical to the committed artifact (subprocess drift gate), and the artifact's output order (sort_keys=True, part_number-sorted chips, family-id-sorted shape_families) is specified and stable so a regeneration diff names the chips that moved"
    requirement: PRUNE-05
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_plan_shapes_drift.py#test_codegen_produces_byte_identical_output"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_plan_shapes_drift.py#test_output_order_is_specified_and_stable"
        status: pass
    human_judgment: false
  - id: D4
    description: "The drift test carries no skip marker of any kind (the artifact is in-repo, unlike the sibling-repo test_sdp_bus_config_drift.py it deliberately does not copy the skip idiom from), and the generator carries exactly one comment line, its shebang"
    requirement: PRUNE-06
    verification:
      - kind: other
        ref: "grep -cE '^\\s*#' over both new source files: 1 (shebang only) in the generator, 0 in the drift test; grep for pytest.mark.skip/skipif/pytest.skip in the drift test: 0 matches"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-04
status: complete
---

# Phase 175 Plan 03: Frozen Plan-Shape Pin over `derive_plan` Summary

**The frozen half of D-10's no-drop proof: a committed pin of all 8 `(op, supported)`-grain plan shapes the shipped database produces over 677 chips, its validate-before-emit generator with a `--planted-fault` seam, and a six-leg drift test with no skip marker -- proven able to fail on five independently-observed non-zero exits.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-09-04
- **Tasks:** 2 (Task 1 generator + committed artifact, Task 2 drift test)
- **Files modified:** 4 (2 new `firestarter_app` source files, 1 new committed artifact, 1 committed evidence transcript)

## Accomplishments

- `firestarter_app/tools/measure_plan_shapes.py` -- imports the shared `tests/plan_corpus.py` surface (`REAL_DB`, `PART_NUMBERS`, `all_rows`, `plan_corpus`) rather than building a second `EpromDatabase`; derives each chip's family token from four hyphen-joined facts about its `full`-scope plan (id-check presence, blank-check position, erase presence, SDP-leg presence); validates strictly before emitting (chip-count closure, family-to-shape bijection recomputed independently, all six aggregates recomputed from the corpus); renders with `json.dumps(indent=2, sort_keys=True) + "\n"`.
- `firestarter_app/tests/fixtures/plan_shapes.json` -- the committed pin: `_generated_by` banner, six absolute aggregates, 8 `shape_families` keyed by family id in sorted order, 677 `chips` keyed by `part_number` in sorted order. 38,646 bytes / 940 lines, matching `175-RESEARCH.md` section F's third prototype exactly.
- `firestarter_app/tests/test_plan_shapes_drift.py` -- six legs: the `_generated_by` banner, the six-aggregate absolute check, byte-identical subprocess regeneration, the three planted faults plus a missing-target `--check` (all through the generator's own `--planted-fault` seam, since its only external input is the shipped database and must not be mutated), family/chip closure, and output-order/trailing-newline stability. Carries no skip marker of any kind.
- Measured, not copied, and every one of the plan's pinned numbers matched on first measurement: `rows=746`, `distinct_part_numbers=677`, `plans=1354`, `distinct_shape_families=8`, `total_steps=16248`, `unsupported_steps=9304`, and all 8 family chip counts (`id-bcpost-erase-sdpNA`=197, `id-bcpre-eraseNA-sdpNA`=180, `noid-bcpre-eraseNA-sdpNA`=90, `noid-bcpreNA-eraseNA-sdpNA`=76, `noid-bcpostNA-erase-sdpNA`=41, `noid-bcpostNA-erase-sdp`=40, `id-bcpreNA-eraseNA-sdpNA`=27, `noid-bcpost-erase-sdpNA`=26), summing to 677. The whole app suite reports **2,145 passed, 0 failed** (2,139 baseline from 175-02 plus these 6 new tests). Phase 174's frozen hashes (`test_blast_radius_invariance.py` + `test_rekey_ledger.py`) still report 114 passed. `ruff check`/`ruff format --check` exit 0. mypy watermark unmoved at 35/35. `firestarter_app/firestarter/` and the firmware repo both report a clean `git status --porcelain`.

## Task Commits

Each task was committed atomically, in `firestarter_app`:

1. **Task 1: generator + committed artifact** - `051aa6f` (test) -- `tools/measure_plan_shapes.py` and `tests/fixtures/plan_shapes.json`.
2. **Task 2: drift test** - `27f8208` (test) -- `tests/test_plan_shapes_drift.py`, six legs, 6/6 passed.

**Plan metadata:** this SUMMARY's own commit follows, in the meta repo, alongside the evidence transcript and the `firestarter_app` gitlink advance.

## Files Created/Modified

- `firestarter_app/tools/measure_plan_shapes.py` -- the generator (new)
- `firestarter_app/tests/fixtures/plan_shapes.json` -- the committed pin (new)
- `firestarter_app/tests/test_plan_shapes_drift.py` -- the drift gate, 6 tests (new)
- `.planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-03-plan-shapes-drift.txt` -- census plus all five observed fail-closed non-zero exits, plus the drift module's own green run (new)

## Decisions Made

- The `(op, supported)` grain is a deliberate STRENGTHENING of D-10, not a departure from it. Both the generator's module docstring and the drift test's module docstring state this explicitly, in the same words this SUMMARY uses, so a later reader cannot delete either module without reading why the frozen half is at this grain and not the coarser op-only one D-10's own prose names.
- Family identity is a pure four-fact function of a chip's `full`-scope plan. This is bijective with the actual `(op, supported)` sequence by construction (`derive_plan`'s op order is itself a function of exactly these same four facts), and `validate()` proves the bijection empirically rather than assuming it -- it recomputes every chip's own shape and asserts every member of a family agrees, so a database change that made two structurally different shapes collide onto one token would fail loudly.
- The three planted faults are injected through the generator's own `--planted-fault` seam, applied to the already-derived payload immediately before `validate()` -- this is the one leg with no 1:1 analog in `measure_part_number_delta.py`, which plants its fault through an external `--issues` file argument. This generator's only external input is the shipped database, which must never be mutated, so an override seam had to be designed rather than reused.
- `validate(payload)` recomputes `total_steps`, `unsupported_steps`, and the family-shape bijection from the corpus itself (importing `plan_corpus()` a second time, cheaply, since it is cached), rather than checking only the payload's own internal self-consistency -- matching the plan's anti-vacuity discipline that a drift-only gate would let a silently-changed measurement through as long as it stayed internally consistent.
- No disagreement to report against the plan's own text this time (unlike 175-01's 373-vs-540 UV plan-count correction) -- every pinned number, every family token string, and every family chip count matched the plan's `must_haves` and `175-RESEARCH.md` section F exactly on first measurement.

## Deviations from Plan

None - plan executed exactly as written. The generator's imports of `tests.plan_corpus` and `firestarter.chip_test` were deferred into function bodies (matching `measure_part_number_delta.py`'s own precedent of deferring `firestarter.*` imports into `derive()`) rather than placed at module top level, purely to avoid an unnecessary import-order wrinkle -- `tools/` is unchecked by CI either way, so this had no gate consequence and is not a deviation from any acceptance criterion.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The frozen half of D-10's no-drop proof is committed, green, and proven non-vacuous on five independently-observed fail-closed exits. Plan 175-04 can now build the execution half (the `run_plan`-side alignment proof) with confidence that a future prune of unsupported steps inside `derive_plan` will be caught by this pin even if the alignment check itself stays green.
- The generator's `--planted-fault` seam (`chip-count-skew`, `orphan-family`, `empty-chips`) is available for any later plan in this phase that needs to re-prove the validator can fail, without designing a new override mechanism.
- No disagreement to carry forward -- all pinned numbers matched on first measurement, matching 175-02's clean run rather than 175-01's corrected one.

## Self-Check: PASSED

All key files confirmed present on disk (`measure_plan_shapes.py`, `plan_shapes.json`, `test_plan_shapes_drift.py`, `evidence/175-03-plan-shapes-drift.txt`). Both `firestarter_app` commit hashes (`051aa6f`, `27f8208`) confirmed present via `git log --oneline`. All plan-level `<verification>` commands re-run clean: `--check` exits 0 with an `OK:` line, 6/6 drift tests pass with no skipped/error count, 114/114 Phase 174 frozen-hash tests pass, `ruff check`/`ruff format --check` exit 0, mypy watermark reports 35 (watermark: 35), both `git status --porcelain` checks against production code report empty, and the full app suite reports 2,145 passed, 0 failed.

---
*Phase: 175-structural-sentinel-over-derive-plan*
*Completed: 2026-09-04*
