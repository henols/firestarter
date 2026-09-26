---
phase: 177-evidence-gated-read-back
plan: 01
subsystem: testing
tags: [chip_test, dev-test, fingerprint, dedup_fingerprint, blast-radius, rekey-ledger]

requires:
  - phase: 174-blast-radius-invariance-harness
    provides: "The frozen-hash gate (FROZEN_HASHES, LADDER_PINS, the rekey ledger and its D-11 declare-in-a-separate-commit protocol) this plan is required to turn RED and measure against."
provides:
  - "FP_MATCH + _synthesized_match_fingerprint: a zero-device-I/O fingerprint for a passing write/verify step"
  - "prior_cycles_failed threaded keyword-only through the four _run_step/_dispatch hops, computed by _run_cycle_block from per_step[i]"
  - "The evidence-gated read-back: a step's own read-back now runs only when that step or an earlier cycle in its block failed"
  - "A bad==0 match bucket inside classify_fingerprint, placed after ff_ratio/address-line so blank/contact stays unmoved"
  - "The measured (not projected) Phase 174 blast-radius impact: exactly which of the 16 frozen shapes moved, the ladder-arm count, and the 18-row filed-corpus re-key mapping"
affects: [177-02-declare-the-rekey, 177-03-close-prune-04-and-seal-phase]

actuals:
  tokens: 11162
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Evidence-gated diagnostic read-back: a diagnostic device read only runs when a cheaper signal (the step's own outcomes, or a prior cycle's verdict) says something needs diagnosing -- verify decides, read-back diagnoses."
    - "Keyword-only, explicitly-forwarded, False-defaulted flag threaded through an existing four-hop dispatch chain (mirrors collect_fingerprint's own shape)."
    - "Measure-never-transcribe: every hash/count in this plan's evidence was produced by running real code against the committed corpus/fixtures this session, never copied from a planning document."

key-files:
  created:
    - .planning/phases/177-evidence-gated-read-back/177-DECISIONS.md
    - .planning/phases/177-evidence-gated-read-back/evidence/177-01-tracer-end-to-end.txt
    - .planning/phases/177-evidence-gated-read-back/evidence/177-01-red-capture.txt
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_chip_test_cycle.py

key-decisions:
  - "D-177-1: PRUNE-04 closes measured-empty within the dev test engine; eprom_operations.write_cycle_eprom is named-and-excluded (it is the uno328pb read-repeatability oracle, not the engine)."
  - "D-177-2: classify_fingerprint gains a bad==0 -> match bucket, placed after the ff_ratio and address-line tests, in addition to the zero-I/O _synthesized_match_fingerprint constructor."
  - "D-177-3: sst27sf512-six-step and sst27sf512-six-step-readback-gated both stay registered; the tracer's step_specs move to match (RK-174-01) and the gated shape is re-pointed to the gate's failing branch (verdict marginal) in plan 177-02, since a naive fingerprint-dropped projection measurably collapses it onto the tracer."
  - "D-177-4: the filed-corpus re-key is published as a full old-to-new mapping (this plan's Task 3 evidence file), with the measured count recorded rather than the projected 18 transcribed -- they happened to agree exactly."

requirements-completed: [PRUNE-01, PRUNE-02, PRUNE-03]

coverage:
  - id: D1
    description: "A passing write+verify plan run performs zero operator.read_eprom calls and both steps still report a match fingerprint (PRUNE-01)"
    requirement: PRUNE-01
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_a_passing_run_performs_zero_fingerprint_read_backs"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_a_passing_write_reports_a_synthesized_match_fingerprint"
        status: pass
    human_judgment: false
  - id: D2
    description: "The read-back gate is per-step and reads across all prior cycles, not just the final cycle's own outcomes (PRUNE-02 adjacency/empty/ordering edges)"
    requirement: PRUNE-02
    verification:
      - kind: unit
        ref: "tests/test_chip_test_cycle.py#test_a_failing_first_cycle_keeps_the_fingerprint_read_back"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_cycle.py#test_an_all_passing_two_cycle_run_performs_zero_fingerprint_read_backs"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_a_bad_blank_check_does_not_force_a_read_back_on_a_passing_write"
        status: pass
    human_judgment: false
  - id: D3
    description: "The synthesized fingerprint is honest (ff_ratio=None, never a fabricated 0.0) and shares its evidence key set with a real measured fingerprint (PRUNE-03)"
    requirement: PRUNE-03
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_synthesized_and_measured_fingerprints_share_one_evidence_key_set"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_a_zero_length_write_region_synthesizes_a_match_with_no_read"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_classify_fingerprint_still_returns_blank_contact_for_an_all_ff_perfect_compare"
        status: pass
    human_judgment: false
  - id: D4
    description: "The Phase 174 frozen-hash gate is deliberately RED after the behaviour commit, and the exact moved set (shapes, ladder arms, filed-corpus re-key mapping) is measured and committed as evidence, with nothing repaired"
    verification:
      - kind: other
        ref: ".planning/phases/177-evidence-gated-read-back/evidence/177-01-red-capture.txt"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-05
status: complete
---

# Phase 177 Plan 01: End-to-End Tracer -- Evidence-Gated Fingerprint Read-Back Summary

**A passing `dev test` write/verify step now costs zero device read-backs and still reports a `match` fingerprint, gated on `prior_cycles_failed` threaded through the existing four-hop dispatch chain; the Phase 174 frozen-hash gate is deliberately RED with the exact moved set measured and committed.**

## Performance

- **Duration:** 55 min (continuation from the Task 1 checkpoint; the prior executor made zero commits before pausing)
- **Completed:** 2026-09-05
- **Tasks:** 3 (all completed this session)
- **Files modified:** 6 (3 in `firestarter_app`, 3 in the meta repo)

## Accomplishments

- Recorded all four operator scope decisions (`D-177-1` through `D-177-4`) in `177-DECISIONS.md`, each the plan's recommended option.
- Landed the whole evidence-gated read-back vertical slice as one commit in `firestarter_app`: `FP_MATCH`, `_synthesized_match_fingerprint` (zero device I/O, honest `ff_ratio=None`), a `bad==0 -> match` bucket inside `classify_fingerprint` placed after the `ff_ratio`/address-line tests, and `prior_cycles_failed` threaded keyword-only through `_run_step` -> `_run_step_untimed` -> `_dispatch_step` -> `_dispatch_multi_run`, computed by `_run_cycle_block` from `per_step[i]` filtered on `_RAN_VERDICTS`.
- Measured the exact blast radius of that change against the Phase 174 harness and committed it as evidence: 3 of 16 frozen shapes moved automatically (the two hand-specified shapes and the filed `gh47` shape do not move until 177-02 edits their literal data), the ladder-arm count is measured at 4 (not the projected 3, because two of the three INCONCLUSIVE members are hand-specified), the 26-row filed corpus re-keys 18 rows matching RESEARCH.md's projected issue list exactly, and the inherited `sst27sf512-six-step-readback-gated` projection is confirmed falsified (it collapses onto the tracer's own after-value).

## Task Commits

1. **Task 1: The four scope calls this phase cannot make for the operator** - `34374d93` (docs)
2. **Task 2: End to end -- one passing write, zero read-backs, a `match` that reaches the hash** - `3f01714` (feat, in `firestarter_app`)
3. **Task 3: Capture the RED -- measure exactly which frozen shapes moved, and repair nothing** - `0fdbf148` (docs)

_Note: Task 2 carries no separate RED/GREEN split -- the plan's tracer task requires the whole vertical slice (tests + implementation) in one reviewable commit; the "RED" this phase captures is the Phase 174 blast-radius gate, not a TDD cycle on the new code itself._

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` - `FP_MATCH`, `_synthesized_match_fingerprint`, the classifier's `match` bucket, `prior_cycles_failed` threaded through 4 hops, the rewritten gate in `_dispatch_multi_run`
- `firestarter_app/tests/test_chip_test.py` - inverted the read-back count test (`==2` to `==0`), 6 new tests for the synthesized contract/evidence-key-set/per-step gating/non-regression, and 2 pre-existing tests updated for the classifier's now-measurably-different behaviour (see Deviations)
- `firestarter_app/tests/test_chip_test_cycle.py` - the cycle-1-fail/cycle-2-pass adjacency pair, isolating the fingerprint gate's contribution from the plan's always-present `read` step baseline
- `.planning/phases/177-evidence-gated-read-back/177-DECISIONS.md` - the four recorded scope decisions
- `.planning/phases/177-evidence-gated-read-back/evidence/177-01-tracer-end-to-end.txt` - Task 2's automated verify output
- `.planning/phases/177-evidence-gated-read-back/evidence/177-01-red-capture.txt` - Task 3's measured blast-radius evidence

## Decisions Made

See `key-decisions` in the frontmatter for the four operator scope decisions (D-177-1..4). One additional in-session decision: `_cycle_operator`-based cycle tests measure the fingerprint gate's contribution as a delta above the plan's own unconditional `read` step baseline (`operator.read_eprom.call_count == runs` for the passing case, `> runs` for the failing case) rather than an absolute `==0`/`>0` count -- `derive_plan("M8720", write_scope="full")` always includes a `read` step that calls `read_eprom` `runs` times regardless of the fingerprint gate, so an absolute-zero assertion would be structurally false rather than measuring the gate.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Two pre-existing test cycle assertions in `tests/test_chip_test_cycle.py` corrected from an impossible absolute count to the correct delta-above-baseline count**
- **Found during:** Task 2
- **Issue:** The plan's literal guidance for the two new cycle tests specifies asserting `operator.read_eprom.call_count > 0` / `== 0` using `ct.derive_plan("M8720", ..., write_scope="full")`. That plan always includes an unconditional `read` step (`chip_test.py:676`) that calls `read_eprom` exactly `runs` times regardless of the fingerprint gate -- so the `==0` assertion is structurally unsatisfiable (measured: baseline is always 2 at `runs=2`) and the `>0` assertion is trivially true regardless of whether the gate works correctly.
- **Fix:** Asserted against the known fixed baseline instead: `== runs` for the all-passing case (zero calls ADDED by the gate) and `> runs` for the failing-cycle case (extra calls added by the gate). Both isolate the gate's own contribution correctly; verified the failing case measures exactly 1 additional call (only the write step's own cycle failed; the verify step's own cycle passed every time and stayed synthesized, per PRUNE-02's per-step contract).
- **Files modified:** `firestarter_app/tests/test_chip_test_cycle.py`
- **Verification:** `pytest tests/test_chip_test_cycle.py` passes; measured directly via an inline script showing baseline=2, failing-leg=3, passing-leg=2.
- **Committed in:** `3f01714` (Task 2 commit)

**2. [Rule 1 - Bug] `test_allow_single_run_admits_runs_1_and_reports_run_count_1` asserted a stale `read_eprom.call_count == 2`**
- **Found during:** Task 2
- **Issue:** This pre-existing test (unrelated to the plan's named files but inside `tests/test_chip_test.py`, one of the plan's declared `files_modified`) asserted a passing single-run (`--fast`-equivalent) write always cost 2 `read_eprom` calls -- one for the plan's `read` step, one for the write step's own fingerprint read-back. With the gate landed, a passing single-run write's own cycle has nothing to disagree with and no prior cycle to have failed, so its fingerprint is synthesized: the correct count is 1, not 2.
- **Fix:** Updated the assertion to `== 1`, added assertions that the write step's fingerprint is `match`, and rewrote the docstring/comment to state the new, more general claim: `--fast` no longer forfeits the read-back only for a step that FAILS; a passing `--fast` write now costs exactly what a passing full-repeat write costs.
- **Files modified:** `firestarter_app/tests/test_chip_test.py`
- **Verification:** `pytest tests/test_chip_test.py::test_allow_single_run_admits_runs_1_and_reports_run_count_1` passes.
- **Committed in:** `3f01714` (Task 2 commit)

**3. [Rule 1 - Bug] `test_devtest01_0x0d_all_ok_sweep_no_longer_tags_community_fail` asserted the pre-Phase-177 `ladder_state == ""`**
- **Found during:** Task 2
- **Issue:** This test's own docstring already documented (from v1.30 Phase 134) that a genuinely-equal SDP-leg read-back fell through `classify_fingerprint`'s four then-existing buckets to `indeterminate`, which tripped `build_db_diff`'s `has_indeterminate_fingerprint` check and routed `ladder_state` to `_LADDER_NONE`. This is exactly `RK-174-05-p177-match-bucket-d4d6`'s declared mechanism: with the new `match` bucket, a genuinely-equal read-back now classifies `match`, the check no longer trips, and `ladder_state` correctly returns to `_LADDER_COMMUNITY_REPORTED` -- the value this test asserted before 134-03's finding.
- **Fix:** Updated the assertion to `ladder_state == "community-reported"` and rewrote the docstring to record this Phase-177 measurement as superseding the intervening 134-03 MEASURED-SUPERSEDED note, naming `RK-174-05` and pointing at this SUMMARY and `MILESTONES.md`.
- **Files modified:** `firestarter_app/tests/test_chip_test.py`
- **Verification:** `pytest tests/test_chip_test.py::test_devtest01_0x0d_all_ok_sweep_no_longer_tags_community_fail` passes.
- **Committed in:** `3f01714` (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (all Rule 1 -- pre-existing test assertions made factually incorrect by this plan's own declared behaviour change, all within `tests/test_chip_test.py`/`tests/test_chip_test_cycle.py`, both already in this plan's `files_modified`).
**Impact on plan:** All three are necessary consequences of the change this plan exists to make, not scope creep. None touches the Phase 174 frozen-hash gate (`test_blast_radius_invariance.py`) or any fixture -- that gate is confirmed RED per Task 3's evidence and is untouched by this plan, as required by the D-11 protocol.

## Issues Encountered

None beyond the deviations above.

**Sanity check confirmed (per the plan's action):** `tests/test_devtest_firmware_error_propagation.py:211` (`ct._dispatch_step(..., runs=1, collect_fingerprint=False)`) still means what it says after the signature grew a fifth keyword-only parameter -- `collect_fingerprint=False` short-circuits the entire gate at `_dispatch_multi_run`'s `if collect_fingerprint and op in (...)` regardless of `prior_cycles_failed`'s (default `False`) value, so this call site's behaviour is unchanged.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for `177-02` (declare the re-key: edit `tests/fixtures/rekey_ledger.py`'s `after_hash` values and `.planning/MILESTONES.md`'s ledger table in a separate commit from any behaviour change, re-point the two hand-specified `sst27sf512-six-step*` shapes per D-177-3, and publish the filed-corpus old-to-new mapping per D-177-4) and `177-03` (close PRUNE-04 measured-empty per D-177-1, and PRUNE-07's seed amendment). The Phase 174 blast-radius gate is confirmed RED with the exact moved set (`at28c256-full-all-ok-sdp`, `sst27sf512-full-all-ok`, `w27e257-full-all-ok`) measured and recorded in `evidence/177-01-red-capture.txt`; no fixture, frozen hash, snapshot, or ledger row was touched in this plan. One open finding for `177-02` to reconcile in `MILESTONES.md`'s corrections table: `distinct_arms` measures at 4, not the projected 3, until the two hand-specified INCONCLUSIVE-arm shapes are also edited.

---
*Phase: 177-evidence-gated-read-back*
*Completed: 2026-09-05*

## Self-Check: PASSED

- `firestarter_app/firestarter/chip_test.py`, `firestarter_app/tests/test_chip_test.py`, `firestarter_app/tests/test_chip_test_cycle.py` all exist and contain the new symbols (`FP_MATCH`, `_synthesized_match_fingerprint`, `prior_cycles_failed`) -- confirmed via `pytest` collection and inline inspection during Task 2.
- `.planning/phases/177-evidence-gated-read-back/177-DECISIONS.md`, `evidence/177-01-tracer-end-to-end.txt`, `evidence/177-01-red-capture.txt` all exist on disk.
- Commits confirmed present: `34374d93` (meta), `3f01714` (firestarter_app), `0fdbf148` (meta) -- `git log --oneline --all` in each repo shows all three.
- All plan-level `<verification>` items re-run and passing: `177-DECISIONS.md` carries 4 answered decisions; the tracer evidence file shows `passing_readbacks=0`, `write_cls=match`, `verify_cls=match`, 4 `hop_*=True` lines, `all_ff_perfect=blank/contact`, `key_sets_agree=True`; `pytest tests/test_chip_test.py tests/test_chip_test_cycle.py tests/test_devtest_firmware_error_propagation.py` -- 191 passed, 0 failed, 0 skipped; the behaviour commit's diff adds zero comment-opening lines and touches no `tests/fixtures/` path; `ruff check`/`ruff format --check` pass and `tools/check_mypy_watermark.py` prints `mypy errors: 35 (watermark: 35)`; the Phase 174 gate is RED (7 failures in `test_blast_radius_invariance.py`, matching the measured moved set) and is written down as data with nothing repaired; `git -C /workspaces/firestarter status --porcelain` is empty.
