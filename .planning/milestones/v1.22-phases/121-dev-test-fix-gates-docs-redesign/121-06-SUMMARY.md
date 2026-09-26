---
phase: 121-dev-test-fix-gates-docs-redesign
plan: 06
subsystem: testing
tags: [dev-test, chip_test, op-vocabulary, uv-eprom, write-region, fail-closed]

# Dependency graph
requires:
  - phase: 121-dev-test-fix-gates-docs-redesign (plan 02)
    provides: "_dispatch_multi_run/_dispatch_step fail-closed on _MULTI_RUN_OPS; _DESTRUCTIVE_OPS chip-ID gate in run_plan"
  - phase: 121-dev-test-fix-gates-docs-redesign (plan 05)
    provides: "is_uv_eprom, Plan.is_uv, Step.write_region, derive_plan(..., write_scope=...)"
provides:
  - "OP_WRITE_PARTIAL op string, live in both _DESTRUCTIVE_OPS and _MULTI_RUN_OPS"
  - "_write_region_for(step, eprom_data) reads Step.write_region instead of guessing UV-ness from eprom_data"
  - "derive_plan's write_scope=\"partial\" arm emits OP_WRITE_PARTIAL (not OP_WRITE)"
  - "_dispatch_multi_run threads the Step through to _write_region_for; OP_WRITE_PARTIAL fully wired into the write dispatch branch (temp-file build, sampler bracket, fingerprint readback)"
affects: [121-07, 121-09, 121-14]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Op-name-as-distinguisher: when two operations can carry the identical numeric parameters (region), a distinct op string is the thing dedup_fingerprint hashes on, not the parameters."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py

key-decisions:
  - "The seventh op string is OP_WRITE_PARTIAL = \"write-partial\"; D-07 stops the vocabulary there (no verify-partial partner) because a verify's region is definitionally the preceding write's."
  - "_write_region_for's signature changed to (step, eprom_data) -- eprom_data is now unused (kept only for _dispatch_multi_run call-site symmetry); the is_uv guess and _PROTOCOL_UV_EPROM constant are deleted, not bypassed."
  - "Correction (measured, not planned): for a UV part, write_scope=\"full\" and write_scope=\"partial\" produce the IDENTICAL top-anchored region (both are is_uv-gated onto _top_anchored_or_default in 121-05's derive_plan, unchanged by this plan). The op string, not the region, is what makes a UV part's full and partial writes distinguishable -- which is exactly D-06's stated purpose."
  - "Deviation: converted the 3 pre-existing 121-05 tests asserting the partial arm emitted OP_WRITE (now OP_WRITE_PARTIAL) as part of Task 1's own commit, and converted the 8 pre-existing bench-free _write_region_for(full) tests as part of Task 2's own commit -- both were necessary to keep every individual task commit green, rather than deferring the conversion to Task 3 as the plan's task-level text literally described."

requirements-completed: []  # DEVTEST-03/DEVTEST-04 contribute-only per requirement_ownership; closed by plan 121-09. Do NOT mark complete.

coverage:
  - id: D1
    description: "OP_WRITE_PARTIAL added to the op vocabulary and both safety-relevant frozensets (_DESTRUCTIVE_OPS, _MULTI_RUN_OPS)"
    requirement: "DEVTEST-04"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_partial_same_ops_as_full_different_region"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_partial_write_gated_on_id_mismatch"
        status: pass
    human_judgment: false
  - id: D2
    description: "_write_region_for reads Step.write_region and never re-derives UV-ness from eprom_data (guess deleted, not bypassed)"
    requirement: "DEVTEST-03"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_write_region_for_no_carried_region_returns_engine_default_even_for_uv_shaped_data"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_write_region_for_step_region_wins_over_bogus_eprom_data_width_hint"
        status: pass
    human_judgment: false
  - id: D3
    description: "The partial write's production-path region and chip-ID gating are proven through run_plan/resolve_chip (not a bench-free _write_region_for(full) call), including a deliberate-break proof of the frozenset membership"
    requirement: "DEVTEST-04"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_write_region_via_run_plan_uses_the_plan_carried_window"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_verify_region_matches_the_preceding_partial_write_region"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 06: OP_WRITE_PARTIAL and Region-Reading Summary

**Added the seventh op string `OP_WRITE_PARTIAL`, wired it into both safety frozensets, and converted `_write_region_for` from an execution-time UV-ness guess into a pure reader of `derive_plan`'s already-decided `Step.write_region`.**

## Performance

- **Duration:** ~15 min (18:21-18:36 UTC)
- **Started:** 2026-07-29T18:21:16Z
- **Completed:** 2026-07-29T18:35:47Z
- **Tasks:** 3
- **Files modified:** 2 (`firestarter/chip_test.py`, `tests/test_chip_test.py`)

## Accomplishments

- `OP_WRITE_PARTIAL = "write-partial"` joins the ordered op vocabulary (now seven strings), is a member of the live `_DESTRUCTIVE_OPS` (chip-ID gate) and `_MULTI_RUN_OPS` (dispatch allow-list) frozensets, and is emitted by `derive_plan`'s `write_scope="partial"` arm instead of `OP_WRITE`. `derive_plan`'s verify step stays the plain `OP_VERIFY` string with the identical `write_region` (D-07 -- no `verify-partial` partner).
- `_write_region_for` no longer guesses UV-ness. Its signature is now `_write_region_for(step, eprom_data)`: it returns `step.write_region` when carried, else the engine default `(0, 256)`. The `electrical-type`/`algorithm == 0x0B` guess and the `_PROTOCOL_UV_EPROM` constant are deleted (not bypassed) -- proven by a test that feeds a UV-shaped `eprom_data` dict alongside a region-less `Step` and asserts the engine default is returned, not the old guess's `(65280, 256)`.
- `_dispatch_step` now passes `step` through to `_dispatch_multi_run`, which accepts it as a keyword-only `step` parameter and threads it into `_write_region_for`. `_dispatch_multi_run`'s op-dispatch ladder (temp-file creation, the write branch, the fingerprint readback branch) was widened to treat `OP_WRITE_PARTIAL` identically to `OP_WRITE` -- a partial write is still a write for pattern generation and sampler bracketing.
- Four new tests drive the partial write and its chip-ID gating through the **production** `run_plan`/`resolve_chip` path (RESEARCH Pitfall 4), asserting on the bytes `operator.write_eprom` actually received rather than calling `_write_region_for` with a bench-only `full`-shaped dict.
- A deliberate-break proof was executed: temporarily removing `OP_WRITE_PARTIAL` from `_DESTRUCTIVE_OPS` turned `test_partial_write_gated_on_id_mismatch` RED (`AssertionError: assert 'OK' == 'SKIPPED'`), confirming the frozenset membership is load-bearing, not merely asserted by construction. The frozenset was restored and the test re-confirmed GREEN before committing.

## Task Commits

Each task was committed atomically in `firestarter_app` on branch `v1.22-at28c-software-data-protection-lifecycle`:

1. **Task 1: Add OP_WRITE_PARTIAL and put it in both frozensets** - `ce63514` (feat)
2. **Task 2: Convert _write_region_for from guessing to reading, and stop discarding the Step** - `927de2c` (refactor)
3. **Task 3: Prove the partial write through the production path and through the chip-ID gate** - `cd7f56b` (test)

**Plan metadata:** this commit (docs: complete plan), in the meta repo only.

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` - `OP_WRITE_PARTIAL` constant; `_DESTRUCTIVE_OPS`/`_MULTI_RUN_OPS` frozenset membership; `derive_plan`'s partial-arm op emission; `_write_region_for` signature/body rewrite; `_PROTOCOL_UV_EPROM` constant removed; `_dispatch_step`/`_dispatch_multi_run` widened to thread `step` and to treat `OP_WRITE_PARTIAL` like `OP_WRITE` in the run loop, temp-file, and fingerprint-readback branches.
- `firestarter_app/tests/test_chip_test.py` - 3 pre-existing `derive_plan` partial-scope tests updated for the `OP_WRITE_PARTIAL` op string (Task 1); 8 pre-existing bench-free `_write_region_for(full)` tests converted to the new `(step, eprom_data)` contract, preserving the SC4 not-widenable and addr_base proofs (Task 2); 4 new production-path tests added for the partial write's region, the full-scope UV correction, the chip-ID gate, and the verify-region equality (Task 3).

## Decisions Made

- Kept `eprom_data` as a parameter of `_write_region_for` (unused in the body) purely for call-site symmetry with `_dispatch_multi_run`'s existing signature, rather than dropping it and reshuffling every call site.
- **Correction to this plan's own Task 3 framing:** the plan's `<behavior>` spec for `test_write_region_via_run_plan_uv_part_full_scope_uses_full_window` states that a UV part's `write_scope="full"` "gets the engine default region, distinguishable from the partial one." Measured against the actual (unchanged-by-this-plan) `derive_plan` logic from plan 121-05, this is not what happens: `write_scope="full"` for a UV part is `is_uv`-gated onto `_top_anchored_or_default`, exactly like `"partial"` -- both produce the identical `(65280, 256)` window for `M27C512`. The test was written to assert the measured behavior (both scopes thread the same region to `operator.write_eprom`) and documents that the op string (`OP_WRITE` vs `OP_WRITE_PARTIAL`), not the region, is the actual distinguisher for a UV part -- which is precisely D-06's stated purpose (the op name enters `dedup_fingerprint`'s hash so the two runs cannot cross-agree, per T-121-24). Region-level divergence between "full" and "partial" only exists for non-UV chips, which was already covered by 121-05's `test_derive_plan_partial_same_ops_as_full_different_region` (using `M8720`).
- Per Task 1's instruction, `diagnostic_report.py` and `tools/parse_devtest_issue.py` were left untouched -- confirmed op-string-agnostic (`diagnostic_report.py` imports only `BannerCounts`/`Plan`/`StepResult` and passes `result.op` straight through; `parse_devtest_issue.py` keys on the `[dev test]` title marker and `dedup_fingerprint` grouping, not any op vocabulary). `git status --porcelain` for both files is empty.
- No live reference to `_PROTOCOL_UV_EPROM` existed anywhere in the tree before deletion (`grep -rn "_PROTOCOL_UV_EPROM" firestarter/ tests/ tools/` was empty even before this plan's changes) -- it was deleted outright, no Task-3 conversion needed for it specifically.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated the 3 pre-existing 121-05 tests asserting the partial arm still emitted "write"**
- **Found during:** Task 1 verification (`pytest tests/test_chip_test.py`)
- **Issue:** `test_derive_plan_partial_same_ops_as_full_different_region`, `test_derive_plan_partial_write_region_uv_memory_size`, and `test_derive_plan_partial_write_region_missing_memory_size_falls_back` (written by plan 121-05, whose own docstring said "Plan 121-06 will swap this scope's emitted write op to OP_WRITE_PARTIAL; here it is still OP_WRITE") asserted the write step's op was `"write"` for `write_scope="partial"`.
- **Fix:** Updated the three tests to look up the write step by `"write-partial"` and assert the op sequence differs from the full-scope plan by exactly that one op string.
- **Files modified:** `tests/test_chip_test.py`
- **Verification:** `pytest tests/test_chip_test.py` green (99 passed) before commit.
- **Committed in:** `ce63514` (Task 1 commit)

**2. [Rule 3 - Blocking] Converted 8 pre-existing bench-free `_write_region_for(full)` tests to the new `(step, eprom_data)` signature**
- **Found during:** Task 2 verification -- changing `_write_region_for`'s signature from `(eprom_data)` to `(step, eprom_data)` broke all 8 tests in the "UV small-region top-anchored write cap" section with `TypeError: _write_region_for() missing 1 required positional argument`.
- **Issue:** The plan's Task 3 text says these tests should be "converted... in this task" (i.e., Task 3), but Task 2's own acceptance criteria require `pytest tests/ -p no:cacheprovider -q` to report 0 failures. Deferring the fix to Task 3 would have left Task 2's commit in a broken state.
- **Fix:** Converted all 8 tests in the same commit as the signature change: 4 tests now construct an explicit `Step` carrying `write_region` and assert `_write_region_for` returns it unchanged regardless of `eprom_data` (including the SC4 not-widenable-by-bogus-eprom_data proof); 1 test (`test_write_region_for_no_carried_region_returns_engine_default_even_for_uv_shaped_data`) is new, proving the deleted guess does NOT fire even against a UV-shaped `eprom_data`; the integration test (`test_dispatch_multi_run_uses_selector_for_uv_chip`) now builds its `Step` with an explicit `write_region=(1792, 256)` (AM2716's UV window) instead of relying on auto-detection.
- **Files modified:** `tests/test_chip_test.py`
- **Verification:** `pytest tests/test_chip_test.py` green (97 passed); full suite `pytest tests/ -p no:cacheprovider` green (1078 passed) before commit.
- **Committed in:** `927de2c` (Task 2 commit)

**3. [Rule 1 - Bug] `_dispatch_multi_run`'s op-dispatch ladder did not originally recognise `OP_WRITE_PARTIAL`**
- **Found during:** Task 2, while widening `_dispatch_multi_run` to accept `step` -- tracing the run loop showed `if op == OP_WRITE:` / `if op in (OP_WRITE, OP_VERIFY):` checks that would route `OP_WRITE_PARTIAL` (now a `_MULTI_RUN_OPS` member per Task 1) into the "unreachable" `AssertionError` branch, since it passes the allow-list guard but matches none of the specific op branches.
- **Fix:** Extended the temp-file-creation condition, the run-loop write branch (including the `sampler` bracket), and the fingerprint-readback condition to treat `OP_WRITE_PARTIAL` identically to `OP_WRITE`.
- **Files modified:** `firestarter/chip_test.py`
- **Verification:** Task 3's `test_write_region_via_run_plan_uses_the_plan_carried_window` and `test_partial_write_gated_on_id_mismatch` exercise this path end to end and pass.
- **Committed in:** `927de2c` (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (1 bug/test-correction, 1 blocking signature-change conversion, 1 missing-dispatch bug). All three were necessary to make the feature actually work and to keep every task's commit individually green; no scope creep beyond `chip_test.py`/`test_chip_test.py`.

## Issues Encountered

- `ruff check` initially flagged an import-ordering (isort) violation after adding `_DESTRUCTIVE_GATE_REASON`/`OP_WRITE_PARTIAL` to the test file's import block; fixed with `ruff check --fix tests/test_chip_test.py` before the Task 3 commit.
- `ruff format` reformatted `chip_test.py`'s new `_write_region_for` signature line (over 88 chars when written across two lines) into a single line; applied via `ruff format` and reconfirmed the full suite green before the Task 2 commit.
- `/tmp/venv311` (the CI-matching ruff venv referenced by this plan's acceptance criteria) does not exist in this devcontainer; used the devcontainer's own `ruff` (0.16.0, same as the project's declared `ruff>=0.15.14` floor) with the project's `pyproject.toml` `target-version = "py39"` config instead. `ruff check`/`format --check` both pass.
- `git -C /workspaces/firestarter status --porcelain` (a verification bullet copied into this plan's Task 3 acceptance criteria) shows an untracked `firestarter/` subdirectory inside the firmware repo. This is a pre-existing environment artifact unrelated to this plan -- this plan touches only `firestarter_app/` and made zero changes to the `firestarter` (firmware) sub-repo. Not fixed (out of scope; logged here rather than in the firmware tree).

## Next Phase Readiness

- `OP_WRITE_PARTIAL` is live and fully wired (vocabulary, both frozensets, `derive_plan` emission, `_dispatch_multi_run` dispatch) -- ready for plan 121-07's `dedup_fingerprint`/`diagnostic_report.py` op-vocabulary work (`_LEGACY_OP_VOCABULARY`, schema version bump) to build on.
- `_write_region_for`'s pure Step-reading contract is stable; plan 121-09 (which owns closing DEVTEST-03/DEVTEST-04) can wire `cli_handlers.py`'s `write_scope` resolution against `derive_plan` without any further changes to the region-selection primitive.
- No blockers. `REQUIREMENTS.md` untouched, as required by this plan's `<requirement_ownership>` lock.

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/chip_test.py`, `firestarter_app/tests/test_chip_test.py`
- FOUND: commit `ce63514` (feat, Task 1)
- FOUND: commit `927de2c` (refactor, Task 2)
- FOUND: commit `cd7f56b` (test, Task 3)
- FOUND: `.planning/phases/121-dev-test-fix-gates-docs-redesign/121-06-SUMMARY.md`
- FOUND: commit `fdb06a2` (docs, meta-repo SUMMARY commit)
