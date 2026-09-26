---
phase: 175-structural-sentinel-over-derive-plan
plan: 02
subsystem: testing
tags: [derive_plan, chip_test, cli_handlers, structural-sentinel, anti-vacuity, prune-06, uv-write-scope]

requires:
  - phase: 175-structural-sentinel-over-derive-plan
    plan: 01
    provides: "tests/plan_corpus.py shared corpus surface, tests/test_derive_plan_structural_sentinel.py with the fail-closed op partition and write-to-verify predicate this plan extends"
provides:
  - "erase_blank_check_violations(plan) -- D-05's separately-named erase-to-blank-check pairing leg, anchored to the production cycle_block_bounds helper"
  - "uv_policy_violations(plan) and uv_blank_check_order_violations(plan) -- D-12's UV write-scope ceiling pins at the derive_plan level, both directions"
  - "test_resolve_write_scope_returns_partial_for_every_uv_row -- the handler-level leg sweeping the real _resolve_write_scope over all 677 part numbers, both interactive values"
affects: [175-03, 175-04, 175-05, 177]

actuals:
  tokens: 5106
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Erase-to-blank-check and write-to-verify kept as separately-named predicates over the same corpus rather than folded into one oracle predicate, so a later phase can cite either by name"
    - "A UV ceiling pinned at BOTH the derive_plan level (structural, easy) and the handler level (decisive, over the real cli_handlers._resolve_write_scope through make_app_context) -- the derive_plan pins alone would stay green even if the handler regressed"
    - "A negative gate (grep for a forbidden assertion pattern) used to keep a known-false invariant (full_device_permitted on a UV write) out of the suite permanently, rather than relying on reviewer memory"

key-files:
  created:
    - .planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-02-erase-and-uv-pins.txt
  modified:
    - firestarter_app/tests/test_derive_plan_structural_sentinel.py

key-decisions:
  - "The plan's two named erase hand-built fixtures (`id, read, erase, verify` and `id, read, blank-check, erase, verify`) both carry no write step, so cycle_block_bounds always returns None for them and neither ever reaches the bounds[1] half of the outside-the-block check. Added a seventh test, test_a_second_erase_outside_the_block_is_a_violation_not_a_skip (the erase-leg analog to 175-01's write-leg precedent), specifically to make weakening E2 observably RED -- without it, dropping the upper-bound check is invisible to this module."
  - "The 28C-family carve-out reason literal is kept as ONE unbroken string rather than an implicitly-concatenated two-line literal, because the plan's own acceptance gate does a single-line grep -F match -- the wrapped form is semantically identical at runtime but invisible to that grep."
  - "Measured, not copied, and all measurements matched the plan's pinned must_haves exactly: erase_violations=0, live_erase_plans=608, blank_check_removed_unflagged=0, carveout_plans=162, carveout_chips=81, carveout_reasons=1, uv_plans=540, uv_policy_violations=0, uv_slot_steps=1080, uv_slot_on_non_uv=0, uv_blank_check_order_violations=0, scope_partial=270, scope_full=407, scope_disagreements=0. No disagreement to report against the plan's own text this time (unlike 175-01's 373-vs-540 UV plan-count correction)."

requirements-completed: [PRUNE-06]

coverage:
  - id: D1
    description: "erase_blank_check_violations: every executable OP_ERASE step in all 1,354 shipped plans has an OP_BLANK_CHECK step present at a higher index inside the same production cycle_block_bounds block; the 81-chip/162-plan 28C-family NA carve-out is pinned by both absolute count and its single reason string"
    requirement: PRUNE-06
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_every_executable_erase_has_a_blank_check_behind_it_in_the_block"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_the_28c_family_na_blank_check_carve_out_is_pinned"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_removing_the_blank_check_flags_every_live_erase_plan"
        status: pass
    human_judgment: false
  - id: D2
    description: "Anti-vacuity for the erase leg: three hand-built counter-plans (no blank-check at all, blank-check ahead of the erase with no cycle at all, a second erase past a real block) plus the 608-of-608 mutated-corpus sensitivity leg, plus three deliberate weakenings (E1-E3) each observed RED and transcribed"
    requirement: PRUNE-06
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py (31 tests, full module)"
        status: pass
      - kind: other
        ref: ".planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-02-erase-and-uv-pins.txt"
        status: pass
    human_judgment: false
  - id: D3
    description: "The UV write-scope ceiling (aq6) pinned at the derive_plan level in both directions (no UV plan claims full-device policy; the uv-slot policy is claimed only by UV plans) and at the blank-check ordering level (a UV write always has a blank-check ahead of it)"
    requirement: PRUNE-06
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_no_uv_plan_claims_the_full_device_region_policy"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_the_uv_slot_policy_is_claimed_only_by_uv_plans"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_a_uv_write_has_a_blank_check_ahead_of_it"
        status: pass
    human_judgment: false
  - id: D4
    description: "The decisive handler-level leg: _resolve_write_scope over all 677 part numbers, both interactive values, cross-checked against Plan.is_uv through the real cli_handlers module and make_app_context(db=REAL_DB, config_manager=Mock()); plus two negative gates keeping a false full_device_permitted invariant and a real ConfigManager() construction out of the suite"
    requirement: PRUNE-06
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_resolve_write_scope_returns_partial_for_every_uv_row"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_derive_plan_structural_sentinel.py#test_uv_policy_violations_flags_both_directions"
        status: pass
      - kind: other
        ref: ".planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-02-erase-and-uv-pins.txt (U1-U3 weakenings, each observed RED)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-04
status: complete
---

# Phase 175 Plan 02: Erase Pairing and UV Write-Scope Ceiling Summary

**Two new sentinel legs over `derive_plan`'s output -- the erase-to-blank-check pairing (D-05) and the `aq6` UV write-scope ceiling (D-12) -- plus the decisive handler-level sweep of `cli_handlers._resolve_write_scope` over all 677 shipped part numbers, twelve new test functions total, each of six deliberate weakenings observed RED and restored GREEN.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-09-04
- **Tasks:** 2 (Task 1 erase-to-blank-check leg, Task 2 UV write-scope ceiling)
- **Files modified:** 2 (1 test module extended across 4 commits, 1 evidence transcript committed)

## Accomplishments

- `erase_blank_check_violations(plan)` -- D-05's separately-named leg, anchored to the production `chip_test.cycle_block_bounds` helper exactly as the write leg is, asserting PRESENCE of an `OP_BLANK_CHECK` step behind a live `OP_ERASE`, never supportedness. Swept clean across all 608 of the corpus's live-erase plans.
- The 81-chip, 162-plan 28C-family NA blank-check carve-out (Phase 153's `FLAG_CAN_ERASE` restoration on all 84 algorithm-13 rows) is pinned by absolute count AND its single reason string, asserted as three separate assertions so each names its own drift.
- `uv_policy_violations(plan)` and `uv_blank_check_order_violations(plan)` -- D-12's UV write-scope ceiling pinned at the `derive_plan` level in both directions (a UV plan never claims the full-device policy; the uv-slot policy is claimed only by UV plans) and the pre-write blank-check ordering.
- `test_resolve_write_scope_returns_partial_for_every_uv_row` -- the leg D-12 says matters most: sweeps the real `cli_handlers._resolve_write_scope` over all 677 part numbers at both `interactive` values through `make_app_context(db=REAL_DB, config_manager=Mock())`, cross-checked against `Plan.is_uv` with zero disagreements.
- Twelve new test functions (7 for the erase leg, including one Rule 2 deviation test; 5 for the UV ceiling), taking the module from 19 to 31 tests. Six deliberate weakenings (E1-E3, U1-U3) each applied, observed to turn the module RED with the exact expected failure, and reverted -- transcribed verbatim into `evidence/175-02-erase-and-uv-pins.txt`.
- Measured, not copied, and every number matched the plan's pinned constants exactly: `erase_violations=0`, `live_erase_plans=608`, `blank_check_removed_unflagged=0`, `carveout_plans=162`, `carveout_chips=81`, `carveout_reasons=1`, `uv_plans=540`, `uv_policy_violations=0`, `uv_slot_steps=1080`, `uv_slot_on_non_uv=0`, `uv_blank_check_order_violations=0`, `scope_partial=270`, `scope_full=407`, `scope_disagreements=0`. The whole app suite reports 2,139 passed, 0 failed (2,127 baseline from 175-01 plus these 12 new tests). Every Phase 174 frozen hash (`test_blast_radius_invariance.py` + `test_rekey_ledger.py`) still reports 114 passed. mypy watermark unmoved at 35/35. `firestarter_app/firestarter/` and the firmware repo both report a clean `git status --porcelain`.

## Task Commits

Each task was committed atomically, in `firestarter_app` (test code); the meta commit (evidence + gitlink + this SUMMARY) follows this SUMMARY's own creation:

1. **Task 1: erase-to-blank-check pairing leg and 28C carve-out** - `9902263` (test) -- `erase_blank_check_violations`, the 28C-family carve-out constant and pin, six of the plan's seven named erase-leg test functions (25 tests total in the module at this point).
2. **Task 2: UV write-scope ceiling and the handler leg** - `9eecfc1` (test) -- `uv_policy_violations`, `uv_blank_check_order_violations`, and all five UV-leg tests including the handler-level sweep (30 tests total).
3. **Fix: the E2 coverage-gap counter-plan** - `5755718` (fix) -- a Rule 2 deviation adding `test_a_second_erase_outside_the_block_is_a_violation_not_a_skip`, the only fixture in the module that exercises the outside-the-block check against a REAL (non-`None`) bounds tuple (31 tests total).
4. **Fix: single-line carve-out reason literal** - `c87eb15` (fix) -- a Rule 1 deviation keeping the pinned 28C reason string on one unbroken line so the plan's own single-line `grep -F` gate can see it.

**Plan metadata:** this SUMMARY's own commit follows, in the meta repo.

## Files Created/Modified

- `firestarter_app/tests/test_derive_plan_structural_sentinel.py` -- extended from 19 to 31 tests (modified, across 4 commits)
- `.planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-02-erase-and-uv-pins.txt` -- census measurements plus all six weakenings' observed RED output and the restored clean run (new)

## Decisions Made

- `erase_blank_check_violations` calls `chip_test.cycle_block_bounds` exactly once, mirroring `write_verify_violations`'s own call, so the two legs cannot drift on what a cycle block is (D-02's discipline, reapplied to D-05).
- The erase leg asserts PRESENCE of a blank-check behind a live erase, never supportedness -- the refined D-05 form. A naive "supported blank-check" reading is RED on the 162-plan 28C-family carve-out and unfixable without a production change this phase forbids; that reading appears nowhere in this module.
- No leg asserts `full_device_permitted is False` on a UV write step -- D-12 forbids it, and it would be a false invariant (`full_device_permitted` is `write_scope == "full"` verbatim, independent of UV-ness). A negative gate (`grep -qE '^\s*assert.*full_device_permitted'` returning nothing) keeps this out of the suite permanently rather than relying on reviewer memory.
- `make_app_context(db=REAL_DB, config_manager=Mock())` builds the handler-leg context exactly once for all 677 x 2 sweep calls, reusing the corpus module's single database instance (D-07) and avoiding a real `ConfigManager()` construction (the documented `~/.firestarter/config.json` write leak). A second negative gate (`grep -n 'ConfigManager()'` returning nothing) keeps a real construction out of the module permanently.
- **Rule 2 deviation, reported rather than silently patched around:** the plan's two named erase hand-built fixtures both omit a write step, so `cycle_block_bounds` always returns `None` for them and neither ever reaches the `bounds[1]` half of the outside-the-block check -- meaning weakening E2 (dropping that half) would have been genuinely vacuous against the module as literally specified. Added a seventh test, `test_a_second_erase_outside_the_block_is_a_violation_not_a_skip` (the erase-leg's own analog to 175-01's `test_a_second_write_outside_the_block_is_a_violation_not_a_skip`), specifically to close this gap. Verified empirically: applying E2 without this test left the module fully green; with it, E2 reddens exactly this one test (the violation's reason string changes from `"erase sits outside the cycle block"` to `"no blank-check behind the erase in the block"` -- the erase is still flagged either way, just via a different, wrong arm, which the exact-tuple assertion catches).
- **Rule 1 deviation, self-caught:** the 28C carve-out reason literal was first written as an implicitly-concatenated two-line string (`"protocol 0x0D (28C family) auto-erases per page during write; no " "step in this plan can ever leave the device blank"`), which is semantically identical to the single-line form at runtime but is invisible to a single-line `grep -qF` -- exactly the gate the plan's own Task 1 `<verify>` block uses. Rewritten as one unbroken line; re-verified the exact literal now matches via `grep -qF`, and that `ruff format --check` and all 31 tests still pass unchanged.
- No measurement disagreement to report against the plan's own text this time (unlike 175-01's 373-vs-540 UV plan-count correction) -- every one of the fourteen pinned numbers (`erase_violations` through `scope_disagreements`) matched the plan's `must_haves` on first measurement.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added the outside-the-block erase counter-plan the E2 weakening needs**
- **Found during:** Task 1, while designing and applying the E1-E3 weakening transcripts (the plan's own "see the RED" step).
- **Issue:** The plan's two named hand-built erase fixtures (`id, read, erase, verify` and `id, read, blank-check, erase, verify`) both carry no write step. `cycle_block_bounds` can only open a block at a write step, so both fixtures always get `bounds is None` and short-circuit through the `bounds is None` half of the outside-the-block check -- neither ever reaches the `bounds[1]` comparison the E2 weakening (drop the upper-bound half) targets. Applying E2 as specified, without an additional test, left the whole module green -- a vacuous weakening, which the plan's own acceptance criteria (`rc_e2=1`, a `[0-9]+ failed` line) explicitly forbid.
- **Fix:** Added `test_a_second_erase_outside_the_block_is_a_violation_not_a_skip`, a hand-built `write, verify, sdp-lock, erase` plan whose `cycle_block_bounds` is a REAL `(0, 2)` tuple and whose erase sits at index 3, past the block. Confirmed the original code flags it via the `bounds[1]` comparison; confirmed E2 flags it too but with a different (wrong) reason string, which the exact-tuple assertion catches.
- **Files modified:** `firestarter_app/tests/test_derive_plan_structural_sentinel.py`
- **Verification:** With the fix in place, E2 reddens exactly `test_a_second_erase_outside_the_block_is_a_violation_not_a_skip` (1 failed, 30 passed); reverted, the module returns to 31 passed.
- **Committed in:** `5755718`

**2. [Rule 1 - Bug] Kept the 28C carve-out reason literal on one line**
- **Found during:** Task 1's own acceptance-criteria self-check (`grep -qF` for the exact pinned literal).
- **Issue:** `_28C_CARVE_OUT_REASON` was first written as two adjacent string literals (implicit concatenation) split across two source lines. The value is identical at runtime, but the plan's own gate does a single-line `grep -qF` match against the exact literal, which cannot see a value split across lines -- the gate would have silently passed the wrong condition.
- **Fix:** Rewrote the constant as one unbroken string on a single line.
- **Files modified:** `firestarter_app/tests/test_derive_plan_structural_sentinel.py`
- **Verification:** `grep -qF` now matches; `ruff format --check` and `ruff check` still exit 0 (E501 is excluded from this project's ruff select set, so the long line is not flagged); all 31 tests still pass unchanged.
- **Committed in:** `c87eb15`

---

**Total deviations:** 2 auto-fixed (1 missing critical anti-vacuity coverage, 1 self-caught gate-visibility bug).
**Impact on plan:** Both fixes are test-side only, strengthen rather than weaken the sentinel's guarantees, and neither touches any production file. No scope creep.

## Issues Encountered

None beyond the two deviations above, both self-detected and self-corrected within this plan's own gates before the final commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The erase-to-blank-check pairing and the UV write-scope ceiling are both committed, green, and proven non-vacuous at both the `derive_plan` and (for the UV ceiling) the handler level. Phase 177 can cite either leg by name, as D-05 requires.
- The module now stands at 31 tests total (19 from 175-01, 12 from this plan), all reusing `plan_corpus()` and `REAL_DB` from `tests/plan_corpus.py` without rebuilding either.
- No disagreement to carry forward this time -- all fourteen pinned counts matched on first measurement.

## Self-Check: PASSED

All key files confirmed present on disk (`test_derive_plan_structural_sentinel.py`, `evidence/175-02-erase-and-uv-pins.txt`). All four `firestarter_app` commit hashes (`9902263`, `9eecfc1`, `5755718`, `c87eb15`) confirmed present via `git log --oneline`. All plan-level `<verification>` commands re-run clean: 31/31 sentinel tests pass, 215/215 precedent-module tests pass (`test_chip_test_blank_check_order.py` + `test_dev_test_cmd.py` + `test_chip_test.py`), 114/114 Phase 174 frozen-hash tests pass, `ruff check`/`ruff format --check` exit 0, mypy watermark reports 35 (watermark: 35), both `git status --porcelain` checks against production code report empty, and the full app suite reports 2,139 passed, 0 failed.

---
*Phase: 175-structural-sentinel-over-derive-plan*
*Completed: 2026-09-04*
