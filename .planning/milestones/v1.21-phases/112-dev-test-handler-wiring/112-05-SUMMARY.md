---
phase: 112-dev-test-handler-wiring
plan: 05
subsystem: cli
tags: [chip-test-engine, safety-gate, derive_plan, requirements-doc, python]
gap_closure: true

# Dependency graph
requires:
  - phase: 109-destructiveness-gate-safety
    provides: "derive_plan's D-01 destructive-gating pattern for OP_WRITE/OP_ERASE (locked_destructive advisory list, SAFE-01)"
  - phase: 112-04
    provides: "auto-capture-only diagnostic report model (operator-approved provenance descope this plan's RPT-04 doc-sync reflects)"
provides:
  - "derive_plan(chip, db, destructive=False) returns exactly 3 executable steps [id, read, blank-check] with OP_VERIFY structurally absent, recorded on locked_destructive"
  - "derive_plan(chip, db, destructive=True) unchanged: write, verify, erase in that order"
  - "RPT-04 in REQUIREMENTS.md reflects the shipped auto-capture-only submittability model"
affects: [phase-111-sc2-bench-reverify]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "OP_VERIFY gated behind `destructive` in derive_plan, mirroring the existing OP_WRITE/OP_ERASE D-01 pattern exactly -- verify does not mutate the chip so it stays out of _DESTRUCTIVE_OPS (the runtime id-first mutation gate), but its plan-construction-time inclusion now depends on `destructive` for the same reason write/erase do: no meaningful verify without a preceding write."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Fix direction (a) executed as decided (not reconsidered): gate OP_VERIFY behind `destructive` in derive_plan, appending ('verify', 'destructive=False: verify omitted (D-01)') to locked_destructive when non-destructive, exactly mirroring the write/erase branches immediately above/below it in source order. Verify's position in the destructive plan (after write, before erase) is unchanged."
  - "_DESTRUCTIVE_OPS and _MULTI_RUN_OPS were NOT touched, per the plan's explicit prohibition -- verify's gating lives entirely in derive_plan's plan-construction logic, not in the runtime chip-mutation-gate frozenset (verify doesn't mutate the chip) or the N>=2 disagreement-policy frozenset (D-06 still applies to verify on destructive plans where it is present)."
  - "Three additional test breakages beyond the plan's named three (test_count_applicable_uv_counts, test_count_applicable_eeprom_counts, test_count_applicable_bad_counts_as_ran) plus two more (test_derive_plan_advisory_populated_when_non_destructive, test_derive_plan_na_erase_advisory_only_records_write) were repaired as a direct mechanical consequence of the Task 1 fix -- same bug class as the plan's three named tests (they codified the pre-fix 4-step composition / verify-always-runs assumption), not a scope expansion."

patterns-established:
  - "When a `destructive`-gated op moves from Plan.steps to Plan.locked_destructive, every test asserting the op-count invariants (m_applicable/n_ran banner counts, locked_ops sets) for that chip must be re-derived from the new composition -- the plan's named test list is a floor, not a ceiling; run the full targeted suite before declaring Task 2 done."

requirements-completed: [SWEEP-05, RPT-04]

coverage:
  - id: D1
    description: "derive_plan(chip, db, destructive=False).steps op-list == [OP_ID, OP_READ, OP_BLANK_CHECK] exactly, OP_VERIFY absent, recorded on locked_destructive"
    requirement: "SWEEP-05"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_derive_plan_verify_gated_behind_destructive, tests/test_chip_test.py::test_derive_plan_strip_default_only_destructive_ops_removed"
        status: pass
      - kind: other
        ref: "inline python composition one-liner (Task 1 verify block) -- no mock"
        status: pass
    human_judgment: false
  - id: D2
    description: "derive_plan(chip, db, destructive=True).steps keeps OP_VERIFY after OP_WRITE and before OP_ERASE -- byte-for-byte the destructive plan shipped today"
    requirement: "SC2"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_derive_plan_verify_gated_behind_destructive, tests/test_chip_test.py::test_derive_plan_destructive_keeps_and_empties_advisory"
        status: pass
    human_judgment: false
  - id: D3
    description: "A non-destructive `dev test` invocation never calls operator.verify_eprom and exits 0 on a healthy chip, proven by a test that removes the verify_eprom.return_value=True masking"
    requirement: "SWEEP-05"
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::TestExitCodeMapping::test_non_destructive_run_never_dispatches_verify"
        status: pass
    human_judgment: false
  - id: D4
    description: "SAFE-01/02/03 non-regression: no new firmware dispatch, no VPP-set, no --force, no raw wire-dict"
    requirement: "SAFE-01/02/03"
    verification:
      - kind: other
        ref: "python tools/check_devtest_orchestrator.py -- exit 0, PASS line names cli_handlers.py/chip_test.py"
        status: pass
    human_judgment: false
  - id: D5
    description: "RPT-04 in REQUIREMENTS.md no longer describes interactive provenance prompts; reflects the 112-04 auto-capture model"
    requirement: "RPT-04"
    verification:
      - kind: other
        ref: "grep -c 'is prompted before the sweep' .planning/REQUIREMENTS.md == 0; grep -q 'Plan 04' .planning/REQUIREMENTS.md; git diff --stat shows only RPT-04's line changed"
        status: pass
    human_judgment: false
  - id: D6
    description: "Lint/format/mypy clean on all touched files; targeted pytest suite green"
    verification:
      - kind: unit
        ref: "cd firestarter_app && ruff check firestarter/chip_test.py tests/test_chip_test.py tests/test_dev_test_cmd.py && ruff format --check (same) && python -m mypy firestarter/chip_test.py && python -m pytest tests/test_chip_test.py tests/test_dev_test_cmd.py -q"
        status: pass
    human_judgment: false

# Metrics
duration: 35min
completed: 2026-07-03
status: complete
---

# Phase 112 Plan 05: Gate OP_VERIFY Behind `destructive` (SC2/SWEEP-05 Gap Closure) Summary

**Fixed `derive_plan`'s unconditional OP_VERIFY append (chip_test.py:387) so a non-destructive `dev test` run is genuinely 3 steps (id, read, blank-check) instead of 4 — restoring the tool's safest default invocation to a trustworthy `exit 0`, matching every locked success criterion and the shipped `--help` text.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-07-03T11:57:00Z
- **Completed:** 2026-07-03T12:04:27Z
- **Tasks:** 3
- **Files modified:** 4 (1 source, 2 test, 1 docs)

## Accomplishments

- **Gated `OP_VERIFY` behind `destructive` in `derive_plan`**, mirroring the existing `OP_WRITE`/`OP_ERASE` D-01 pattern exactly: when `destructive=True`, verify stays in `steps` positioned after write and before erase (byte-for-byte unchanged from today's shipped behavior); when `destructive=False`, verify is omitted from the executable `steps` list and instead recorded on the advisory `locked_destructive` list as `("verify", "destructive=False: verify omitted (D-01)")`. `_DESTRUCTIVE_OPS` and `_MULTI_RUN_OPS` were left untouched per the plan's explicit prohibitions — verify's gating lives entirely at plan-construction time in `derive_plan`, not in either runtime frozenset.
- **Net effect:** `derive_plan(chip, db, destructive=False).steps` op-list is now exactly `[id, read, blank-check]` — 3 steps, matching the phase's locked success criteria (Phase 109 SC1/SWEEP-05, Phase 112 SC2, `112-02-PLAN.md`'s own `must_haves.truths`) and the shipped `--help` text ("Without --destructive: id + read + blank-check only"), which was already accurate and required no edit.
- **Added `test_derive_plan_verify_gated_behind_destructive`** (non-mocked composition assertion) proving both the 3-step non-destructive op-list + `locked_destructive` entry, and the unchanged destructive ordering (verify after write, before erase).
- **Added `test_non_destructive_run_never_dispatches_verify`** (behavioral CliRunner regression) that removes `make_clean_operator()`'s usual `verify_eprom.return_value = True` masking, replacing it with a `side_effect=AssertionError(...)` that would fail loudly if verify were ever dispatched on a non-destructive run. Under the pre-fix (4-step) plan this test fails (verify runs → AssertionError → BAD → exit 1); under the fix it passes (verify structurally absent → unreachable → exit 0).
- **Repaired 8 existing tests** that codified the pre-fix 4-step composition or the always-runs-verify assumption: the 5 the plan named (`test_derive_plan_read_and_verify_always_present`, `test_derive_plan_destructive_flag_strips_not_annotates`, `test_derive_plan_strip_default_only_destructive_ops_removed`, plus two `locked_destructive`-set assertions the plan's own read-through surfaced: `test_derive_plan_advisory_populated_when_non_destructive`, `test_derive_plan_na_erase_advisory_only_records_write`) and 3 more discovered only by running the full targeted suite (`test_count_applicable_uv_counts`, `test_count_applicable_eeprom_counts`, `test_count_applicable_bad_counts_as_ran` — the `BannerCounts.n_ran` banner-count tests, which naturally drop by 1 once verify no longer executes non-destructively, and gain `"verify"` in their `locked_steps` assertions).
- **Reworded RPT-04 in `REQUIREMENTS.md`** to drop the stale "provenance is prompted before the sweep" language (a model deleted outright in Phase 112 Plan 04, operator-approved) and instead document the shipped auto-capture-only model: `hw_revision`/host version/protocol path auto-captured, honest `None` where unavailable, zero interactive prompts, `is_submittable` derived from auto-capture completeness only.

## Task Commits

Each task committed atomically; source/test commits inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`), the REQUIREMENTS.md doc commit in the meta-repo:

1. **Task 1: Gate OP_VERIFY behind `destructive` in derive_plan** — `7a74fcc` (fix, firestarter_app submodule)
2. **Task 2: Non-mocked composition + non-masking behavioral regression tests; repair the 8 affected tests** — `b88649f` (test, firestarter_app submodule)
3. **Task 3: Reword RPT-04 in REQUIREMENTS.md to the auto-capture model** — `ba02e1b` (docs, meta-repo)

**Plan metadata:** (this commit, meta-repo) — docs: complete plan

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` — `derive_plan`'s `OP_VERIFY` append moved from unconditional to a `destructive`-gated branch (mirrors the `OP_WRITE` block immediately above it); non-destructive omission recorded on `locked_destructive`.
- `firestarter_app/tests/test_chip_test.py` — new `test_derive_plan_verify_gated_behind_destructive`; 7 existing tests repaired for the corrected 3-step non-destructive composition (`test_derive_plan_read_and_verify_always_present`, `test_derive_plan_destructive_flag_strips_not_annotates`, `test_derive_plan_strip_default_only_destructive_ops_removed`, `test_derive_plan_advisory_populated_when_non_destructive`, `test_derive_plan_na_erase_advisory_only_records_write`, `test_count_applicable_uv_counts`, `test_count_applicable_eeprom_counts`, `test_count_applicable_bad_counts_as_ran`).
- `firestarter_app/tests/test_dev_test_cmd.py` — new `test_non_destructive_run_never_dispatches_verify` in `TestExitCodeMapping`.
- `.planning/REQUIREMENTS.md` — RPT-04 body reworded to the auto-capture model, citing Phase 112 Plan 04; `- [x] **RPT-04**:` bullet prefix and single-line bold label preserved; no other row touched.

## Decisions Made

See `key-decisions` in frontmatter for the full list. Highlights:

- Fix direction (a) — gate `OP_VERIFY` behind `destructive`, mirroring `OP_WRITE`/`OP_ERASE` — executed exactly as decided in the plan objective; not reopened for reconsideration.
- `_DESTRUCTIVE_OPS`/`_MULTI_RUN_OPS` left untouched per explicit prohibition: verify's gating is a plan-construction-time decision in `derive_plan`, not a runtime-mutation-gate or disagreement-policy concern.
- The plan named 3 tests as needing repair; the full targeted suite run surfaced 5 more (2 `locked_destructive`-set assertions the plan's own `<action>` prose implied but didn't enumerate by name, and 3 `count_applicable` banner-count tests). All 8 are the same bug class — tests that encoded the pre-fix composition — and were repaired as part of Task 2's stated intent ("repair the three existing tests that currently codify the buggy 4-step composition" — the actual blast radius was 8, discovered via the plan's own required verification step, not a scope expansion).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Repaired 5 additional tests beyond the plan's named 3, broken by the same fix**
- **Found during:** Task 2 verification (`pytest tests/test_chip_test.py tests/test_dev_test_cmd.py -q`)
- **Issue:** The plan explicitly named 3 tests to repair (`test_derive_plan_read_and_verify_always_present`, `test_derive_plan_destructive_flag_strips_not_annotates`, `test_derive_plan_strip_default_only_destructive_ops_removed`). Running the plan's own required verification command surfaced 5 more failures caused by the identical Task 1 fix: `test_derive_plan_advisory_populated_when_non_destructive` and `test_derive_plan_na_erase_advisory_only_records_write` asserted `locked_destructive` op-sets that didn't yet include `"verify"`; `test_count_applicable_uv_counts`, `test_count_applicable_eeprom_counts`, and `test_count_applicable_bad_counts_as_ran` asserted `BannerCounts.n_ran` values that assumed verify still executed on a non-destructive run.
- **Fix:** Updated each assertion to reflect the corrected composition (`locked_destructive` op-sets now include `"verify"`; `n_ran` values reduced by 1 for the non-destructive cases; `locked_steps` set assertions include `"verify"`). No test was weakened — each still asserts the same invariant class, just with the corrected expected values.
- **Files modified:** `firestarter_app/tests/test_chip_test.py`
- **Verification:** Full targeted suite (`test_chip_test.py` + `test_dev_test_cmd.py`, 98 tests) green.
- **Committed in:** `b88649f` (Task 2)

---

**Total deviations:** 1 auto-fixed (Rule 1 — mechanical test repair, same root cause as the plan's own named fixes; no behavior or scope change beyond what Task 1's fix necessitated).
**Impact on plan:** None beyond completing the plan's own stated intent more thoroughly than its example list enumerated. All `must_haves.truths` and `success_criteria` are met without deviation.

## Issues Encountered

None beyond the test-repair blast-radius noted above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 112's single remaining gap (SC2/SWEEP-05) is closed. `firestarter dev test <chip>` on its safest, most casual invocation path (no `--destructive`) now genuinely runs exactly 3 non-fatal steps and exits 0 on a healthy chip, matching the shipped `--help` text and every locked success criterion.
- The Phase-111 SC2 hardware bench re-verify (before/after voltage-capture on a real electrically-erasable chip via `--destructive`) remains the sole outstanding human-verification item, carried forward unchanged from `112-02-SUMMARY.md`/`112-03-SUMMARY.md`/`112-04-SUMMARY.md`/`112-UAT.md` — this plan does not attempt it (cannot be closed by software) but the fixed non-destructive default means an operator can now trust `exit 0` before proceeding to `--destructive` with confidence.
- RPT-04's documentation debt (identified in `112-VERIFICATION.md`'s Gaps Summary) is closed — REQUIREMENTS.md no longer promises a deleted interactive-prompt model.

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/chip_test.py
- FOUND: firestarter_app/tests/test_chip_test.py
- FOUND: firestarter_app/tests/test_dev_test_cmd.py
- FOUND: .planning/REQUIREMENTS.md
- FOUND: .planning/phases/112-dev-test-handler-wiring/112-05-SUMMARY.md
- FOUND: commit 7a74fcc (Task 1, firestarter_app submodule)
- FOUND: commit b88649f (Task 2, firestarter_app submodule)
- FOUND: commit ba02e1b (Task 3, meta-repo)

---
*Phase: 112-dev-test-handler-wiring*
*Completed: 2026-07-03*
