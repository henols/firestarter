---
phase: 206-dev-test-keeps-its-fidelity-on-one-session
plan: 02
subsystem: testing
tags: [dev-test, chip_test, diagnostic_report, dedup-fingerprint, compare-path, blank-check-evidence]

requires:
  - phase: 206-01
    provides: "check_eprom_blank/verify_eprom verdicts 0/1/2 land on VERDICT_SKIPPED+STATUS_ERROR at both dispatch arms (D-01); the frozen 19-case dedup_fingerprint corpus proven unmoved"
  - phase: 202-verification-engine-moves-to-the-host
    provides: "_drive_region_compare's on_result seam (Phase 203, WRITE-01); check_eprom_blank/verify_eprom's host-side compare engine"
provides:
  - "StepResult.compare_evidence -- the blank-check step's own bad/compared/first_offset/first_actual/ff_count/aborted/classification mapping, additive and outside dedup_fingerprint's allow-list"
  - "StepResult.compare_path and compare_path_tag -- the empty-default 'cmp=host' discriminator distinguishing a Phase-202 host-path comparison from a firmware/unknown/legacy one, appended to dedup_fingerprint only when non-empty"
  - "EpromOperator.verify_eprom gains a keyword-only on_result parameter, forwarded to _drive_region_compare, mirroring check_eprom_blank's Task 1 treatment"
affects: [206-03-lease-gate, 206-04-lease-measurement]

actuals:
  tokens: 12338
  tasks: 2
  commits: 2
  plan_head_before: c22287a

tech-stack:
  added: []
  patterns:
    - "Empty-default discriminator discipline, third application: compare_path_tag joins repeat_policy_tag/coverage_tag as a module-level *_TAG constant + list[StepResult]->str free function, keyed structurally off a falsy-default StepResult field, appended to dedup_fingerprint's pre-image only when non-empty"
    - "on_result capture-list idiom, second application: a local captured list + closure passed as on_result=, checked for non-emptiness to detect whether a compare step's operator call actually reached the host engine (as opposed to a test double that accepts on_result for signature parity but never invokes it)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/fake_chip.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_chip_test_cycle.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/test_write_blank_guard.py
    - firestarter_app/tests/test_dev_test_cmd.py

key-decisions:
  - "D-02 (fork F2, Task 1): the blank-check step's compare evidence lives in a NEW additive StepResult field (compare_evidence), never in the existing fingerprint slot -- a populated fingerprint there would classify blank/contact (not match) on every passing blank check and re-key all 19 frozen literals."
  - "D-03 (fork F4, Task 3): a third empty-default discriminator, COMPARE_PATH_HOST_TAG = \"cmp=host\", keyed on a new falsy-default StepResult.compare_path field, appended to dedup_fingerprint after the coverage tag. Direction fixed by history: every already-filed report was produced by the firmware path, so firmware/unknown/legacy stays untagged."
  - "checkpoint:decision answered land-as-specified (operator, 2026-09-23) -- see 'Checkpoint Decision Record' below."
  - "Deviation (Rule 3, Task 3): EpromOperator.verify_eprom gains its own keyword-only on_result, forwarded to _drive_region_compare, exactly mirroring check_eprom_blank's Task 1 treatment. Required because the 8 frozen fixture shapes built through the REAL derive_plan->run_plan pipeline against a mocked operator (report_shapes.py's own documented design) would otherwise pick up compare_path=\"host\" on every successful verify step regardless of mock-vs-real, re-keying 4 of the 19 frozen literals. Adding the on_result seam and having FakeChip.verify_eprom accept-but-never-invoke it (same treatment FakeChip.check_eprom_blank got in Task 1) makes compare_path structurally correct: only a call that genuinely reaches _drive_region_compare's finalised CompareResult sets it."

patterns-established:
  - "compare_path_tag: third and final member of the empty-default discriminator family in chip_test.py (repeat_policy_tag, coverage_tag, compare_path_tag), all placed contiguously and all following the identical falsy-default / structural-field-key / append-only-when-non-empty shape."

requirements-completed: [DEVTEST-01, DEVTEST-02]

coverage:
  - id: D1
    description: "The blank-check step carries its own compare evidence (bad, compared, first_offset, first_actual, ff_count, aborted, classification) outside dedup_fingerprint's hash, recovered through the existing on_result seam at zero extra device I/O"
    requirement: "DEVTEST-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_blank_check_carries_compare_evidence_without_a_fingerprint"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_blank_check_compare_evidence_is_absent_when_the_step_never_ran"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_step_dict_emits_compare_evidence_and_compare_path_keys"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_compare_evidence_does_not_move_any_frozen_hash"
        status: pass
    human_judgment: false
  - id: D2
    description: "A host-path comparison report is distinguishable from a firmware-path one via compare_path_tag's empty-default 'cmp=host' append to dedup_fingerprint, with all 19 frozen literals provably unmoved and the tag proven capable of moving the hash"
    requirement: "DEVTEST-02"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_dedup_fingerprint_is_frozen[all 19 parametrized cases]"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_planted_compare_path_host_reddens_the_gate"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_default_step_result_is_untagged_by_compare_path_tag"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_empty_results_list_is_untagged_by_compare_path_tag"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_two_runs_differing_only_in_compare_path_do_not_merge"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_two_runs_identical_in_every_hashed_component_do_not_separate"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_compare_path_tag_is_appended_after_the_coverage_tag"
        status: pass
    human_judgment: true
    rationale: "The re-key itself -- the second restart of the 43 measured ALLOW chips' count_agreeing promotion ladder in two milestones -- is a policy/business consequence a human confirmed at the checkpoint, not something a test asserts pass/fail on. The affected-population disclosure is recorded below rather than machine-verified."

duration: 28min (this session; Task 1 was executed and committed in a prior session before this continuation agent was spawned)
completed: 2026-09-23
status: complete
---

# Phase 206 Plan 02: The blank-check step recovers its own evidence, and a host-path report gets its own identity Summary

**`check_eprom_blank` now hands back the address-and-value evidence a blank-check failure used to discard, and `dedup_fingerprint` can tell a Phase-202 host-path comparison apart from a firmware-path one — without moving any of the 19 frozen literals thousands of filed community reports are keyed on.**

## Performance

- **Duration:** 28 min (this continuation session, Task 3 + SUMMARY; Task 1 ran in a prior session)
- **Started (this session):** 2026-09-23T09:00:00Z (approximate — continuation spawn)
- **Completed:** 2026-09-23T09:28:12Z
- **Tasks:** 2 code tasks (Task 1, Task 3) + 1 `checkpoint:decision` (Task 2, answered `land-as-specified`)
- **Files modified:** 10 (across both task commits)

## Accomplishments
- `check_eprom_blank`'s dispatch arm captures the finalised `CompareResult` through the already-shipped `on_result` seam and attaches it to the blank-check step as a new additive `StepResult.compare_evidence` field — `bad`, `compared`, `first_offset`, `first_actual`, `ff_count`, `aborted` and the classification string, all outside `dedup_fingerprint`'s five-entry allow-list.
- `compare_path_tag` joins `repeat_policy_tag`/`coverage_tag` as the third empty-default discriminator: `""` for the firmware/unknown/legacy default, `"cmp=host"` when a step's comparison actually ran through the Phase-202 host engine. `dedup_fingerprint` appends it after the coverage tag, only when non-empty.
- All 19 frozen `dedup_fingerprint` literals are provably unmoved (`test_dedup_fingerprint_is_frozen`, 19/19 green), and the tag is proven CAPABLE of moving the hash by a planted-mutation leg — an inert tag would have left the gate green while DEVTEST-02 went unmet.
- The empty, adjacency and ordering edge cases are each pinned by a dedicated test.
- `EpromOperator.verify_eprom` gained its own `on_result` forwarding (mirroring `check_eprom_blank`), which is what makes `compare_path` structurally correct for the 8 frozen fixture shapes that run through the real `derive_plan`→`run_plan` pipeline against a mocked operator.
- The one-way re-key was confirmed by a human at the `checkpoint:decision` before Task 3 landed; the affected population is named below.

## Task Commits

Each task was committed atomically:

1. **Task 1: the blank-check step carries its own compare evidence, outside the hash** - `555c69d` (feat, tdd) — completed in a prior session, verified by the orchestrator before this continuation began.
2. **Task 2: checkpoint:decision** — no commit (interactive gate). Answered `land-as-specified`.
3. **Task 3: the empty-default host-path discriminator** - `81ff585` (feat, tdd)

**Plan metadata:** (this commit, following)

_Both code tasks carried `tdd="true"`; RED transcripts are recorded below._

## Files Created/Modified
- `firestarter_app/firestarter/chip_test.py` - `StepResult.compare_evidence`/`compare_path`; `COMPARE_PATH_HOST`/`COMPARE_PATH_HOST_TAG`/`compare_path_tag`; `_dispatch_step`'s `OP_BLANK_CHECK` arm captures compare evidence and sets `compare_path`; `_dispatch_multi_run`'s `OP_VERIFY` branch captures `compare_path` via a new `on_result` callback; `_aggregate_cycle_results` propagates both new fields through the fold
- `firestarter_app/firestarter/diagnostic_report.py` - `_step_dict` emits `compare_evidence`/`compare_path` unconditionally; `dedup_fingerprint` appends `compare_path_tag`'s output after the coverage tag, only when non-empty
- `firestarter_app/firestarter/eprom_operations.py` - `check_eprom_blank` (Task 1) and `verify_eprom` (Task 3) both gain a keyword-only `on_result` parameter, forwarded to `_drive_region_compare`
- `firestarter_app/tests/fake_chip.py` - `FakeChip.check_eprom_blank` (Task 1) and `FakeChip.verify_eprom` (Task 3) accept `on_result` for signature parity, never invoke it
- `firestarter_app/tests/test_chip_test.py`, `test_chip_test_cycle.py`, `test_diagnostic_report.py`, `test_blast_radius_invariance.py`, `test_write_blank_guard.py`, `test_dev_test_cmd.py` - new and updated regression tests for both tasks

## Decisions Made
- D-02, D-03 as recorded in the PLAN's Decisions section — no new architectural decisions introduced during execution.
- **Checkpoint Decision Record (Task 2):** the operator was shown all three options (`land-as-specified`, `defer-the-tag`, `invert-the-direction`) with their trade-offs, including that landing the tag restarts the `count_agreeing` promotion ladder for the 43 measured ALLOW chips a second time in two milestones (after the v1.30 SDP leg), that filed issues keep their ids forever, and that a later code revert cannot rejoin groups filed in between. The operator answered **`land-as-specified`** through the orchestrator's interactive gate. Task 3 was implemented exactly as specified, with no re-ask and no reopening of the trade-off.
  - **Affected population, named per the plan's own prohibition:** the 43 measured ALLOW chips whose `count_agreeing` promotion counts restart for host-path reports, starting from the first post-206 `dev test --submit`.
- Implementation choice (Task 3, not in the plan's own action text): `EpromOperator.verify_eprom` needed the same `on_result` seam `check_eprom_blank` got in Task 1 — see Deviations below.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `verify_eprom` gained a keyword-only `on_result` parameter, mirroring `check_eprom_blank`**
- **Found during:** Task 3, authoring the RED legs and running the full frozen-hash gate
- **Issue:** The plan's action text scopes Task 3's file list to `chip_test.py`/`diagnostic_report.py` (plus test files) and says compare_path should be set "when the operator method actually reached the device," without naming a mechanism for `OP_VERIFY`. A naive implementation — setting `compare_path=COMPARE_PATH_HOST` whenever the `_dispatch_multi_run` loop called `operator.verify_eprom` at least once (`verify_verdicts` non-empty) — re-keyed 4 of the 19 frozen literals (`at28c256-full-all-ok-sdp`, `sst27sf512-full-all-ok`, `uv-slot-write-pass`, `w27e257-full-all-ok`). These 4 shapes are built through the REAL `derive_plan`→`run_plan` pipeline against a `FakeChip`/`Mock` operator (`tests/fixtures/report_shapes.py`'s own documented design, `:56-57`), and since Phase 202 retired the firmware compare path from production code entirely, the naive criterion could not distinguish "a mocked test double's `verify_eprom` returned an int" from "the real host compare engine actually ran" — both looked identical from `_dispatch_multi_run`'s perspective.
- **Fix:** Added `on_result: Callable[[CompareResult], None] | None = None` to `verify_eprom`'s signature, forwarded to its own `_drive_region_compare` call (previously it passed none — `test_verify_never_passes_on_result` pinned that as an explicit invariant). `_dispatch_multi_run`'s `OP_VERIFY` branch now captures via the identical `on_result` callback pattern the blank-check arm uses in Task 1, and sets `compare_path=COMPARE_PATH_HOST` only when the callback actually fired (`captured_compare_verify` non-empty) — structurally correct because `FakeChip.verify_eprom` (updated to accept `on_result` for signature parity, same treatment `FakeChip.check_eprom_blank` got in Task 1) never invokes it, while the real `EpromOperator.verify_eprom` always does when it reaches `_drive_region_compare`.
- **Files modified:** `firestarter_app/firestarter/eprom_operations.py`, `firestarter_app/tests/fake_chip.py`, `firestarter_app/firestarter/chip_test.py`
- **Verification:** All 19 `test_dedup_fingerprint_is_frozen` parametrized cases pass; full host suite (2354 passed) is a superset of the plan 01 baseline (empty failing-id set).
- **Committed in:** `81ff585` (Task 3 commit)

**2. [Rule 3 - Blocking] Rewrote a superseded pinned invariant test**
- **Found during:** Task 3, same investigation as deviation 1
- **Issue:** `tests/test_write_blank_guard.py::test_verify_never_passes_on_result` structurally pinned (via AST walk) that `verify_eprom`'s call to `_drive_region_compare` never carries an `on_result` keyword. Its own docstring scoped that claim to "Task 1" ("`verify_eprom` is untouched by THAT task"), but Task 3's fix above deliberately changes it.
- **Fix:** Renamed and rewrote the test to `test_verify_eprom_forwards_on_result_structurally`, asserting the OPPOSITE (that `on_result` IS forwarded), mirroring `test_check_eprom_blank_forwards_on_result_structurally` immediately below it. The new docstring records the superseded invariant and the reason it changed, rather than silently deleting the history.
- **Files modified:** `firestarter_app/tests/test_write_blank_guard.py`
- **Verification:** `pytest tests/test_write_blank_guard.py -o addopts="" -q` — 1 passed (renamed test), no other test in the module affected.
- **Committed in:** `81ff585` (Task 3 commit)

**3. [Rule 1 - stale pin] Two structural pin tests needed updating for the new field/append**
- **Found during:** Task 3, running the full `test_blast_radius_invariance.py`/`test_diagnostic_report.py` suite after adding `compare_path`
- **Issue:** `_STEPS_ELEMENT_0_KEYS` (D-07's key-list pin) did not yet include `compare_path`, and `test_status_axis_does_not_reorder_the_fingerprint_pre_image`'s structural proof asserted exactly 3 `parts.append` call sites in `dedup_fingerprint` (now 4, with the new `compare_path_tag` append).
- **Fix:** Added `compare_path` to `_STEPS_ELEMENT_0_KEYS` (now 23 keys) with an updated docstring; updated the `parts.append` count assertion and its docstring from 3 to 4.
- **Files modified:** `firestarter_app/tests/test_blast_radius_invariance.py`, `firestarter_app/tests/test_diagnostic_report.py`
- **Verification:** Both tests pass; `test_steps_element_0_key_pin_is_sensitive_to_the_error_name_key` (the anti-vacuity sibling) still passes unchanged.
- **Committed in:** `81ff585` (Task 3 commit)

---

**Total deviations:** 3 auto-fixed (2 Rule 3 - blocking, 1 Rule 1 - stale structural pin).
**Impact on plan:** Deviation 1 is the load-bearing fix that makes DEVTEST-02's own acceptance criterion (all 19 frozen literals unmoved) achievable at all, given the fixture architecture; deviations 2 and 3 are its necessary, narrowly-scoped follow-on test updates. No scope creep — `compare.py` and `tests/fixtures/report_shapes.py` remain untouched, both committed and in the working tree, verified after every task.

## Issues Encountered
None beyond the deviations above.

## Task 1 RED transcript

Recorded by the prior-session executor (orchestrator-verified before this continuation began); not reproduced here — see the Task 1 commit `555c69d` and its acceptance-criteria verification, already confirmed by the orchestrator's Completed Tasks table.

## Task 3 RED transcript

Before the Task 3 implementation edit, the six new/rewritten legs (`test_default_step_result_is_untagged_by_compare_path_tag`, `test_empty_results_list_is_untagged_by_compare_path_tag`, `test_planted_compare_path_host_reddens_the_gate`, `test_two_runs_differing_only_in_compare_path_do_not_merge`, `test_two_runs_identical_in_every_hashed_component_do_not_separate`, `test_compare_path_tag_is_appended_after_the_coverage_tag`) were authored against source carrying only Task 1's changes. `compare_path_tag` and `COMPARE_PATH_HOST` did not exist, so every leg failed on import/attribute error (`ImportError: cannot import name 'compare_path_tag'` / `'COMPARE_PATH_HOST'` from `firestarter.chip_test`) — the intended RED reason: the discriminator function and field genuinely did not exist yet, not a fixture or collection defect. After implementing the field, constants and function, all six passed. The frozen-hash gate (`test_dedup_fingerprint_is_frozen`, all 19 cases) was then run and observed to RED for the reason described in Deviation 1 above (4 shapes re-keyed) before the `on_result`-forwarding fix; after the fix, all 19 passed.

## Baseline comparison (against plan 01's recorded empty baseline)

Full host suite, run through `/workspaces/firestarter_app/.venv311/bin/python`, `-o addopts="" -p no:cacheprovider -q`, after Task 3:

```
2354 passed in 196.34s (0:03:16)
--------------------------- snapshot report summary ----------------------------
36 snapshots passed.
```

Failing-node-id set: **empty** — a superset of plan 01's recorded empty baseline (2333 passed, `206-01-SUMMARY.md`). The net +21 over that baseline (2354 − 2333) accounts for Task 1's and Task 3's new/split test functions combined.

## Threat Flags

None beyond what the PLAN's `<threat_model>` already declared and this plan's tasks mitigated (T-206-08, T-206-09, T-206-01, T-206-10, T-206-11, T-206-SC) — no new report field escapes `submit.sanitize_dict`'s scrubbing (Task 1 confirmed this for `compare_evidence`; `compare_path` is a plain bounded string from a two-value enum, `""`/`"host"`), and `firestarter/compare.py` is untouched, verified after every task.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 03 (lease gate) can proceed: this plan's `dedup_fingerprint` schema work is complete, both DEVTEST-01 and DEVTEST-02 are satisfied, and the frozen 19-case corpus is proven unmoved by either of this plan's task commits.
- No blockers. Both dispatch arms tested end-to-end (blank-check evidence recovery; verify-step host-path detection), the full host suite is a superset of the recorded empty baseline, and `ruff check`/`ruff format --check` are both clean over `firestarter/ tests/`.
- **Carried forward for a future phase (not filed as a new issue — informational only):** the `count_agreeing` ladder restart for the 43 measured ALLOW chips takes effect from the first post-206 `dev test --submit`. No action is required by this phase; noted here so the next `/gsd-extract-learnings` pass has the pointer.

## Self-Check: PASSED

- `firestarter_app/firestarter/chip_test.py` — FOUND (modified, both commits present)
- `firestarter_app/firestarter/diagnostic_report.py` — FOUND (modified, both commits present)
- `firestarter_app/firestarter/eprom_operations.py` — FOUND (modified, both commits present)
- `firestarter_app/tests/fake_chip.py` — FOUND
- `firestarter_app/tests/test_blast_radius_invariance.py` — FOUND
- `firestarter_app/tests/test_chip_test_cycle.py` — FOUND
- `firestarter_app/tests/test_diagnostic_report.py` — FOUND
- `firestarter_app/tests/test_write_blank_guard.py` — FOUND
- Commit `555c69d` — FOUND in `git log --oneline --all`
- Commit `81ff585` — FOUND in `git log --oneline --all`
- All 19 `test_dedup_fingerprint_is_frozen` parametrized cases — PASSED
- `tests/fixtures/report_shapes.py` and `firestarter/compare.py` — untouched, committed and working tree, verified after HEAD

---
*Phase: 206-dev-test-keeps-its-fidelity-on-one-session*
*Completed: 2026-09-23*
