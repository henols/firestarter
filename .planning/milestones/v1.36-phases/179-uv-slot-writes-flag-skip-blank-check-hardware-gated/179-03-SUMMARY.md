---
phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated
plan: 03
subsystem: dev-test-engine
tags: [uv-eprom, blank-check, chip_test, firestarter_app, regression, criterion-4]

requires:
  - phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated (plan 01)
    provides: FLAG_SKIP_BLANK_CHECK on a proven monotonic UV masked write, the SKIPPED blank-check verdict adjudication, and WriteInitPreflightChip -- the pieces this plan's regression module exercises
  - phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated (plan 02)
    provides: uv-slot-write-pass registered in the frozen corpus, confirming the same builder shape this module's core leg re-derives independently
provides:
  - "ROADMAP criterion 4's host half: tests/test_chip_test_uv_slot_write.py, committed, collected in every CI run, carrying zero skip markers -- the first automated proof that a UV part holding data outside its top slot accepts the slot write and folds to overall_verdict == PASS with run_count == 2"
  - "ROADMAP criterion 3 proved rather than asserted: the monotonicity witness and region_policy constructed in disagreement in BOTH directions via the public WriteContext.cycle_targets seam, with zero probe reads and no monkeypatching"
  - "an anti-vacuity sibling behind every positive claim: the double's refusal, the adjudication's load-bearing role, the flag's non-always-on-ness, the adjudication's non-always-on-ness, and the measured inertness of the research-prescribed probe-read string equality"
affects: [179-04-bench-wave-and-requirement-marking]

actuals:
  tokens: 4690
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "criterion-4 regression module modelled on tests/test_chip_test_sdp_leg.py's docstring-taxonomy shape: module docstring names the full leg inventory and the module's honest scope boundary (host path only, hardware claim named as a sibling plan's)"
    - "every positive claim paired with an anti-vacuity sibling in the SAME commit as the claim it protects, never deferred to a later plan"
    - "WriteContext.cycle_targets as the zero-probe injection seam for constructing two signals in deliberate disagreement, asserting on read_eprom call count to prove the seam bypassed the resolver rather than merely producing the same answer by coincidence"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_chip_test_uv_slot_write.py (new)

key-decisions:
  - "Both tasks landed all twelve legs GREEN on first write -- the described behavior was already fully implemented by plans 179-01/02, so this plan is pure regression authorship, not RED-GREEN-REFACTOR against new production code. No implementation code was touched (asserted in every hygiene gate)."
  - "The evidence-capture script's own full-suite run (325s) exceeded this tool's 120s default Bash timeout on first attempt; re-run with an explicit longer timeout, then the truncated evidence file was hand-repaired by splicing in the completed run rather than re-running the whole capture script a second time."

requirements-completed: []

coverage:
  - id: D1
    description: "Criterion 4's host half: a committed, collected, unskipped regression proving a UV part holding data outside the target slot accepts the slot write and the run folds to PASS with write/verify run_count == 2, with the double's refusal and the adjudication's load-bearing role both asserted"
    requirement: "UV-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_uv_slot_write_on_a_non_blank_part_reaches_pass_with_run_count_two"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_the_double_refuses_a_non_blank_write_without_the_flag"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_the_double_accepts_a_non_blank_write_with_the_flag"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_the_flag_reaches_the_wire_on_every_cycle"
        status: pass
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-03-criterion-four.txt (direct_noflag_return=False, direct_noflag_code=176, direct_flag_return=True, write_verdict=OK, write_run_count=2, verify_verdict=OK, verify_run_count=2, overall=PASS, flags_seen=8,8, title_matches=True)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The adjudication is what lifts the run to PASS (not incidental absence of BAD), and the not-blank finding survives the verdict change: blank-check reads SKIPPED with reason and error_code=176 intact, and forcing the same results' blank-check back to BAD folds to FAIL"
    requirement: "UV-02"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_the_blank_check_adjudication_is_what_lifts_the_run_to_pass"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_uv_slot_write_preserves_the_not_blank_finding"
        status: pass
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-03-criterion-four.txt (forced_bad_folds=FAIL, bc_verdict=SKIPPED, bc_error_code=176, bc_reason_cell_verbatim=True)"
        status: pass
    human_judgment: false
  - id: D3
    description: "ROADMAP criterion 3: the two signals (region_policy string, monotonicity witness) constructed in DISAGREEMENT in both directions via the public WriteContext.cycle_targets seam, with zero probe reads and no monkeypatching -- the witness wins each time"
    requirement: "UV-03"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_uv_slot_policy_without_the_witness_does_not_set_the_flag"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_fixed_policy_with_the_witness_sets_the_flag"
        status: pass
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-03-witness-wins.txt (dirA_flags=0, dirA_reads=0, dirB_flags=8, dirB_reads=0, resolver_patched=0)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The fail-closed empty cases and the falsified prescribed witness form are committed as assertions, not left to one-off evidence: _is_monotonic_masked_target is False for None/unmasked/empty-current and True only when all three conjuncts hold; the SUMMARY.md:89-prescribed current_source == 'probe read' equality never matches a real staged tranche"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_the_witness_is_false_for_absent_empty_and_unmasked_targets"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_the_prescribed_probe_read_string_equality_would_never_match"
        status: pass
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-03-witness-wins.txt (witness_none=False, witness_unmasked=False, witness_empty_current=False, witness_full=True, prescribed_equality_matches=False, staged_prefix_holds=True)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Neither always-on failure mode is possible: a non-UV plan never sets the flag, and a non-UV blank-check failure still reports BAD (the adjudication does not fire outside a UV plan)"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_a_non_uv_plan_never_sets_the_skip_blank_check_flag"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py#test_a_non_uv_blank_check_failure_is_still_bad"
        status: pass
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-03-witness-wins.txt (nonuv_flags_distinct=0, nonuv_blank_check_verdict=BAD)"
        status: pass
    human_judgment: false
  - id: D6
    description: "All twelve legs are proved COLLECTED (no leg_<name>=0), the module carries zero skip markers and zero paren-bearing patching primitives, and the full suite stays green with the new legs added"
    verification:
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-03-witness-wins.txt (12/12 legs collected, skip_markers=0, resolver_patched=0, 2265 passed, 32 snapshots passed, 0 failed)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-06
status: complete
---

# Phase 179 Plan 03: Criterion-4 Regression Module Summary

**`tests/test_chip_test_uv_slot_write.py` lands twelve named legs, none skipped, proving a UV part outside its top slot reaches `overall_verdict == PASS` with `run_count == 2`, that the monotonicity witness -- not `region_policy` -- decides the flag in both disagreement directions, and that every one of those positive claims has an anti-vacuity sibling asserting the double actually refuses, the adjudication actually decides, and neither is always-on.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-09-06 (continuation dispatch, resuming after plan 179-02's completion)
- **Completed:** 2026-09-06
- **Tasks:** 2
- **Files modified:** 1 (`firestarter_app`), plus 2 new evidence files (meta repo)

## Accomplishments

- `tests/test_chip_test_uv_slot_write.py` (new, 435 lines, twelve test functions) closes ROADMAP criterion 4's host half: no test in the suite exercised UV-01 before this plan (`FakeChip.write_eprom` models UV AND-physics but not the firmware write-init pre-flight refusal), and now one does, committed and unskipped.
- Legs 1-2 prove `WriteInitPreflightChip` genuinely refuses a non-blank write without the flag (`False`, `last_firmware_error_code == 0xB0`) and genuinely accepts it with the flag (`True`, `None`) -- so legs 3-6 cannot be theatre against a double that refuses nothing.
- Leg 3 is the criterion-4 core: a two-cycle `run_plan` on `m27c512` against a double seeded outside the top slot yields `write`/`verify` verdict `OK` at `run_count == 2` and `submit.overall_verdict(results) == "PASS"`, with `submit.build_title(...)` matching `^\[dev test\] m27c512 — PASS \([0-9a-f]{12}\)$`.
- Leg 4 pins `chip.write_flags_seen == [8, 8]` -- the flag survives onto the SECOND cycle via the staged-tranche carry-through, not just the first.
- Legs 5-6 prove the `PASS` is produced BY the adjudication (forcing the same results' blank-check verdict back to `BAD` folds to `FAIL`) and that the not-blank finding survives verbatim (`SKIPPED`, non-empty `reason`, `error_code == 176`, `submit._reason_text(...)` returns the reason unsuppressed).
- Legs 7-8 prove ROADMAP criterion 3 in both directions via the public `WriteContext.cycle_targets` injection seam (never a monkeypatch of `_resolve_write_target`): policy `uv-slot` + witness absent → flag `[0]`; policy `fixed` + witness present → flag `[8]`; both assert zero `read_eprom` calls, so the leg is proven to test the witness rather than the resolver.
- Legs 9-12 are the anti-vacuity closet: the fail-closed empty/unmasked/absent cases for `_is_monotonic_masked_target`, the measured falsification of `.planning/research/SUMMARY.md:89`'s prescribed `current_source == "probe read"` equality (never matches; the `.startswith("probe read ")` prefix always does), a non-UV plan recording only `0` in `write_flags_seen`, and a non-UV blank-check failure still reporting `BAD`.
- All twelve legs passed on first write against the existing implementation (plans 179-01/02 had already landed the production behavior) -- this plan is pure regression authorship, touching zero production code, asserted by `git diff HEAD~1 --quiet -- firestarter/` on both commits.
- Full suite: **2265 passed, 0 failed, 32 snapshots passed** (was 2253 before this plan; +12 for the new legs, no regressions).

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule (branch `gsd/v1.36-dev-test-fidelity`), with the meta repo's gitlink advanced in the same logical step:

1. **Task 1: Criterion 4's committed core -- the UV slot write reaches PASS, and the double really refuses** - `60e35e3` (test, firestarter_app) / `3b38733a` (test, meta gitlink + evidence)
2. **Task 2: The witness wins -- both disagreement directions, every empty case, and the falsified string form pinned red** - `9f39853` (test, firestarter_app) / `038b6145` (test, meta gitlink + evidence)

**Plan metadata:** committed separately (this SUMMARY.md + STATE.md).

## Files Created/Modified

- `firestarter_app/tests/test_chip_test_uv_slot_write.py` - new module, twelve test functions across two commits: legs 1-6 (Task 1, criterion-4 core) and legs 7-12 (Task 2, witness-wins + anti-vacuity)
- `.planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-03-criterion-four.txt` - measured Task 1 evidence (new)
- `.planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-03-witness-wins.txt` - measured Task 2 evidence (new)

## Decisions Made

See `key-decisions` in frontmatter. In brief: no RED-GREEN cycle was needed because the behavior under test was already fully implemented by plans 179-01/179-02 -- every one of the twelve legs passed on first write, so this plan's two `tdd="true"` tasks each produced exactly one tests-only commit, matching the plan's own explicit "Commit once, tests only" instruction rather than a literal RED/GREEN/REFACTOR split. The evidence-capture script's own full-suite run needed a longer timeout than this tool's 120s default; the truncated first attempt's evidence file was hand-repaired by splicing in a completed re-run rather than re-running the entire capture script (which would have re-executed the already-measured sections redundantly).

## Deviations from Plan

None - plan executed exactly as written. One self-correction during authorship: a `#` comment was drafted for the `_OPERATOR_METHODS` module-level list, caught immediately by re-reading the file before it was ever committed, and replaced with equivalent prose in the module docstring's existing "Operator-double harness" paragraph. No commit ever carried the comment; `git diff HEAD~1` on both commits confirms zero added `^\+[[:space:]]*#` lines.

## Issues Encountered

- The Task 2 evidence-capture script's `pytest tests/ -o addopts=""` full-suite run took ~326s, exceeding the 120s default Bash tool timeout on the first combined-script attempt. Resolved by re-running the full-suite command alone with an explicit 480s timeout, then splicing its output into the evidence file in place of the truncated tail -- all measured values (leg collection, skip/resolver-pattern counts, the independent witness measurements) from the first attempt were already complete and correct, so only the final full-suite section needed replacement.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter_app/tests/test_chip_test_uv_slot_write.py` is committed, collected, and green: 12/12 legs, zero skip markers, zero paren-bearing patching primitives (`setattr(`, `mock.patch(`, `@patch(` all absent).
- ROADMAP criterion 4's host half and criterion 3 are both closed by this plan. Per `D-179-1`, criterion 4's HARDWARE half -- the committed `179-MEASUREMENT.md` bench artifact -- is still owed by plan `179-04`.
- Per the shared-ID gate, `UV-01`/`UV-02`/`UV-03` are correctly NOT marked complete in `REQUIREMENTS.md` here -- this plan's frontmatter declares all three, but plan `179-04` owns the marking (it branches on a `BENCH RESULT:` sentinel and may only be entitled to mark some of them). `ROADMAP.md` and `REQUIREMENTS.md` were not touched by this plan.
- No blockers for `179-04`. The bench wave still needs the operator's ST M27C512 confirmed on hand and not saturated, per `179-RESEARCH.md`'s Q6/A1 (unchanged since 179-01/179-02).

## Self-Check: PASSED

- `firestarter_app/tests/test_chip_test_uv_slot_write.py` exists and contains all twelve test function names: confirmed via `pytest --collect-only`.
- Commits `60e35e3`, `9f39853` (firestarter_app) and `3b38733a`, `038b6145` (meta) all found in `git log --oneline --all`.
- All `<acceptance_criteria>` for both tasks re-verified against fresh evidence files this session; all pass.
- Plan-level `<verification>` items 1-6 re-run this session: 12/12 legs collected and unskipped; `pytest tests/ -o addopts=""` reports `2265 passed, 32 snapshots passed, 0 failed`; ruff check/format, mypy watermark (35/35), `check_devtest_orchestrator.py`, `check_diagnostic_report_claims.py`, `snapshot_report_shapes.py --check` (19 snapshots) and `check_rekey_ledger.py` (from `/workspaces`) all exit clean; `git diff --quiet -- firestarter/` holds across both `firestarter_app` commits; zero added `#` comment lines; both submodules and `chip_database.json` porcelain-clean.

---
*Phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated*
*Completed: 2026-09-06*
