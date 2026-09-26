---
phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim
plan: "04"
subsystem: firmware
tags: [avr-gcc, avr-libc, integer-arithmetic, pytest, source-contract, dead-code-elimination]

requires:
  - phase: 155-01
    provides: authoritative before-figures (uno 26026/1575, uno328pb 26074/1581, leonardo 28170/2016; the 11-symbol 64-bit table; the corrected RAM/split derivations)
  - phase: 155-02
    provides: check_no_heap_or_64bit_symbols.py, the avr-nm gate over all eleven 64-bit symbols
  - phase: 155-03
    provides: .planning/v1.33/tools/check_dead05_phrasing.py, the DEAD-05 phrasing corpus and its mandated/forbidden wording
provides:
  - the 32-bit reformulation of rurp_read_voltage_mv (folded scale factor, two overflow guards, no 64-bit type)
  - a committed host-side numerical oracle (tests/test_voltage_reformulation_oracle.py) bit-identical at the shipped calibration, bounded at exactly 5 mV, guard boundaries and zero sentinels exercised
  - a comment-stripped source-contract scan binding the oracle's model to the shipped C
  - the shipped comment carrying the mandated DEAD-05 coverage-ceiling wording and correcting all four defects in the preserved reference
affects: [155-06 (after-figures, final avr-nm gate, full-corpus DEAD-05 run, requirement close-out)]

tech-stack:
  added: []
  patterns:
    - "Host-side numerical oracle + comment-stripped source-contract scan for a TU with zero native/bench coverage (test_write_path_source_contract_v131.py's idiom, applied to rurp_common.cpp)"
    - "Model constants defined in exactly one place in the Python model, asserted verbatim in the shipped C, so drift on either side reddens the pytest leg"

key-files:
  created:
    - firestarter/tests/test_voltage_reformulation_oracle.py
  modified:
    - firestarter/src/boards/rurp_common.cpp

key-decisions:
  - "OQ-1 locked: shipped guard constant 4194303UL (0x3FFFFF, a shift test), not the preserved reference's 4000000UL. This measures -1366 B (not the ROADMAP header's -1364 B) once this plan and plan 05 have both landed; the 2 B delta and its cause (the guard-constant choice) is plan 06's ledger entry to record against the final combined total -- noted here per the plan's critical constraint so it is not silently absorbed."
  - "All four defects in the preserved reference's (a6b46f8) comment were corrected rather than carried: the false 'bench-verified only' coverage claim (replaced with the mandated DEAD-05 wording), the 4000000UL guard, the symmetric +/-5% tolerance claim (the real window is -5% relative low / +500 mV absolute high -- so the reformulation's under-read-only behaviour can never suppress the high-side error), and the undercounted 438 B symbol figure (528 B is the full eleven-symbol contiguous blob; 438 B is the named-subset figure, stated alongside it, not alone)."
  - "The hollow-gate tension (test_config_storage_dualslot.py's own rejection of 'an independent fake reimplementation living only in this test') is answered in the oracle's module docstring by naming the source-contract scan as what converts 'a copy behaves' into 'the shipped text is the formula the copy models', and by stating why host-compiling rurp_common.cpp is unavailable (the ARDUINO_AVR_* preprocessor gate, the #error fall-through, and the ADC register writes / Arduino calls in the function body)."
  - "Both dedicated guard-boundary pairs were computed and fixed at plan time, not searched at runtime: guard A at r1=3856000/r2=44000 (sum=3900000, passes) vs r1=3856001/r2=44000 (sum=3900001, fails); guard B at r1=3812003/r2=1000 (k=4194303, passes) vs r1=3812004/r2=1000 (k=4194304, fails), with both guard-B sums independently confirmed at or below the guard-A ceiling so guard A is provably not the guard that fires there."

requirements-completed: []

coverage:
  - id: D1
    description: "Committed host-side numerical oracle proving the 32-bit form bit-identical to the 64-bit form at the shipped calibration (k=7850 exact, ADC 1023/bandgap 225 -> 35691 both ways), bit-identical over the full bandgap range (0 mismatches / 1,046,529 evals), and bounded at exactly 5 mV worst deviation over the stated grid with a proven one-directional (under-read-only) property"
    requirement: "DEAD-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_voltage_reformulation_oracle.py::test_scale_factor_is_exact_at_the_shipped_calibration, ::test_named_single_reading_agrees_in_both_forms, ::test_bit_identity_at_the_shipped_calibration_over_the_stated_bandgap_range, ::test_bit_identity_at_the_shipped_calibration_over_the_full_bandgap_range, ::test_worst_deviation_over_the_stated_grid_is_exactly_five_and_never_over_reads (all pass)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both uint32 overflow guards exercised by dedicated cases on each side of their exact boundary (the nominal grid reaches neither), plus both pre-existing zero sentinels (r2==0, bandgap==0) preserved unchanged"
    requirement: "DEAD-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_voltage_reformulation_oracle.py::test_guard_a_boundary_pair, ::test_guard_b_boundary_pair, ::test_guard_b_bound_keeps_the_product_inside_thirty_two_bits, ::test_zero_sentinels_still_return_zero (all pass)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Comment-stripped source-contract scan binding the oracle's transcribed formula (5 constructs) and its 3 model constants verbatim to the shipped rurp_read_voltage_mv body, plus a standalone no-uint64_t source-level check for DEAD-03; all three legs RED against the pre-change 64-bit implementation (task 1) and GREEN after the 32-bit reformulation lands (task 2)"
    requirement: "DEAD-03, DEAD-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_voltage_reformulation_oracle.py::test_shipped_c_matches_the_transcribed_formula, ::test_no_sixty_four_bit_type_remains_in_the_function_body, ::test_model_constants_appear_verbatim_in_the_shipped_body (RED at commit e26e9ab, GREEN at commit 46dd574)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The 32-bit reformulation shipped in src/boards/rurp_common.cpp -- no uint64_t in the function, avr-nm confirms all eleven 64-bit symbols absent from all three ELFs, and pio test -e native stays 172/172 across 17 suites (this TU compiles in no native environment)"
    requirement: "DEAD-03"
    verification:
      - kind: other
        ref: "avr-nm 64-bit regex count == 0 on uno/uno328pb/leonardo; pio test -e native == 172/172, 17 suites, unchanged"
        status: pass
    human_judgment: false
  - id: D5
    description: "The shipped comment and the oracle's module docstring both carry the mandated DEAD-05 coverage-ceiling wording verbatim and none of the six forbidden phrasings; the named avr-gcc residual risk is stated as unmitigated in both"
    requirement: "DEAD-05"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_voltage_reformulation_oracle.py::test_module_docstring_states_the_coverage_ceiling (pass); manual normalised-substring check confirms the mandated phrase present verbatim in both required-positive targets this plan produces"
        status: pass
    human_judgment: false

tech-stack-note: |
  No new dependency. stdlib + pytest only, matching the CI leg 3 contract.

# Metrics
duration: 45min
completed: 2026-08-23
status: complete
---

# Phase 155 Plan 04: Voltage Reformulation Oracle and 32-bit Reformulation Summary

**Folded `rurp_read_voltage_mv`'s resistor divider into a single 32-bit scale factor, deleting the function's only call site into the soft 64-bit runtime, proven equivalent by a committed host-side numerical oracle bound to the shipped C by a comment-stripped source-contract scan.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-23T09:55:00Z (approx.)
- **Completed:** 2026-08-23T10:40:00Z (approx.)
- **Tasks:** 2 (TDD: RED then GREEN)
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

- Wrote `firestarter/tests/test_voltage_reformulation_oracle.py`: 15 tests -- 9 numeric/guard/sentinel legs, 3 source-contract legs, 3 structural/docstring legs -- proving the 32-bit reformulation bit-identical to the 64-bit form at the shipped calibration, bounded at exactly 5 mV worst-case and one-directional (under-read only) across the stated grid, with both overflow guards exercised at their exact boundary using plan-computed `(r1, r2)` pairs.
- Committed the oracle first with its three source-contract legs deliberately RED against the pre-change 64-bit implementation (proving they are reachable, not pre-satisfied), then landed the 32-bit reformulation in `src/boards/rurp_common.cpp` and turned all three GREEN.
- The shipped comment corrects all four defects PATTERNS.md identified in the preserved reference (`a6b46f8`): the false "bench-verified only" claim, the wrong guard constant (`4000000UL` vs the locked `4194303UL`), the symmetric `+/-5%` tolerance claim (the real window is asymmetric), and the undercounted 438 B symbol figure (528 B is the true eleven-symbol total).
- Confirmed the image-level effect: `avr-nm`'s 64-bit regex is 0 on all three ELFs; `check_no_heap_or_64bit_symbols.py` still exits 1 with FAIL naming only heap symbols (plan 05's half), proving the gate discriminates the two symbol families.
- `pio test -e native` and `-e native_nodevtools` both stayed 172/172 across 17 suites; `pytest tests/` grew from a pre-existing 332 to 347 (332 + this plan's 15 new legs), 0 failed.

## Task Commits

Each task was committed atomically inside the `firestarter` submodule, on branch `gsd/v1.33-source-hygiene-firmware-size-reduction`:

1. **Task 1: RED -- author the numerical oracle and its source-contract scan** - `e26e9ab` (test) -- 12/15 legs green, 3 source-contract legs RED by construction against the pre-change 64-bit implementation.
2. **Task 2: GREEN -- ship the 32-bit reformulation** - `46dd574` (refactor) -- 15/15 legs green.

No plan-metadata commit lands in the `firestarter` submodule (task commits are the plan's only firmware-repo output); this SUMMARY, STATE.md and ROADMAP.md are committed separately in the meta repo per the standard protocol.

## TDD Gate Compliance

- RED gate: `e26e9ab` (`test(155-04): ...`) -- 3 source-contract legs failing by construction, quoted verbatim below.
- GREEN gate: `46dd574` (`refactor(155-04): ...`) -- all 15 legs passing.
- No REFACTOR-gate commit was needed (no cleanup pass required after GREEN).

### RED failure messages (verbatim, task 1)

```
test_shipped_c_matches_the_transcribed_formula:
AssertionError: expected at least one occurrence of the summed-divider assignment
in the comment-stripped body of rurp_read_voltage_mv, found 0.

test_no_sixty_four_bit_type_remains_in_the_function_body:
AssertionError: expected zero uint64_t occurrences in the comment-stripped body
of rurp_read_voltage_mv, found 4.

test_model_constants_appear_verbatim_in_the_shipped_body:
AssertionError: expected the literal '3900000' (_GUARD_SUM_MAX) to appear
verbatim in the comment-stripped body of rurp_read_voltage_mv.
```

## Files Created/Modified

- `firestarter/tests/test_voltage_reformulation_oracle.py` -- new. 15 tests: numeric bit-identity/deviation/direction legs, 4 guard-boundary/sentinel legs, 3 source-contract legs, 3 structural/docstring legs. Calibration read from `include/rurp_shield.h` (never hardcoded); `_strip_comments`/`_line_of` copied verbatim from `test_write_path_source_contract_v131.py`.
- `firestarter/src/boards/rurp_common.cpp` -- `rurp_read_voltage_mv` reformulated: `uint32_t sum = r1 + r2;` / guard A / `uint32_t k = (1100UL * sum) / r2;` / guard B / `uint32_t bg = ...;` / narrowed return, replacing the `uint64_t numerator`/`denominator` form. Comment rewritten to correct all four preserved-reference defects and carry the mandated DEAD-05 wording. No planning-provenance token added (confirmed: `grep -cE 'DEAD-0[0-9]|Phase 155|OQ-[0-9]|D-0[0-9]'` returns 0). Trailing-newline state (file already lacked one) preserved unchanged.

## Decisions Made

See `key-decisions` in the frontmatter for the full detail. In brief: `4194303UL` (OQ-1) shipped over `4000000UL`; both guard-boundary pairs computed at plan time per the plan's exact spec; the hollow-gate tension answered by name in the oracle's docstring; all four preserved-reference comment defects corrected.

## Deviations from Plan

None that changed a deliverable or a mandated name -- plan executed as specified, including the exact test names, the exact guard constants, and the exact `(r1, r2)` boundary pairs.

## Issues Encountered

**The plan's own `<verify><automated>` `-k` filter for task 1 collides with two mandated test names.** `-k "not shipped_c and not sixty_four_bit and not model_constants"` is meant to isolate the 12 non-source-contract legs, but `shipped_c` is also a substring of the mandated names `test_scale_factor_is_exact_at_the_shipped_calibration` and both `test_bit_identity_..._shipped_calibration_...` legs (via "shipped_c" inside "shipped_calibration"), so pytest's substring `-k` matching deselects those three numeric legs too -- the literal command collects 9, not the "at least 12" the acceptance criteria expects, and the source-contract-only run collects 6 (3 fail + 3 unrelated passes), not "exactly 3 failed, 0 passed." This is a pre-existing ambiguity in the plan's verify command, not a defect in the oracle: I did not rename the mandated test names (Rule 4 territory -- renaming a plan-mandated identifier is out of scope for an auto-fix). Instead I verified the RED/GREEN split precisely via explicit pytest node-id `--deselect`/selection (`test_shipped_c_matches_the_transcribed_formula`, `test_no_sixty_four_bit_type_remains_in_the_function_body`, `test_model_constants_appear_verbatim_in_the_shipped_body` as the exact 3-leg set), confirming 12 passed / 3 deselected at RED and 3 failed / 0 passed when isolated to exactly those three node IDs -- the same proof the plan's `-k` command intended, reached by a collision-free selector. No commit was affected; this is a verification-methodology note for plan 06 or any future re-run of this plan's verify block.

**Pre-existing DEAD-05 phrasing-gate violation, out of scope.** Running `.planning/v1.33/tools/check_dead05_phrasing.py` with default arguments after landing both of this plan's files reports `FAIL: 4 forbidden-phrasing violation(s)` -- all four are in `155-03-SUMMARY.md` (plan 03's own artifact), which quotes the first forbidden phrasing (enumerated in `155-VALIDATION.md` item 5) three times inside prose that also names `rurp_read_voltage_mv` (documenting its own gate's needle-matching example, not making a coverage claim about the firmware function). Neither of this plan's two files (`rurp_common.cpp`, `test_voltage_reformulation_oracle.py`) contributes any violation -- confirmed by inspecting the tool's full output, and independently by a targeted normalised-substring check confirming both files carry the mandated phrasing and none of the six forbidden ones. Per the scope boundary (only auto-fix issues directly caused by this plan's own file changes), `155-03-SUMMARY.md` was left untouched and this is logged here for whoever runs the phase-wide DEAD-05 check in plan 06.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Plan 05 (`include/firestarter.h`'s `progress_data` removal, `src/proms/memory.cpp`'s file-scope static, the two native test edits) can land independently; this plan touched neither file.
- Plan 06's after-figures record should quote this plan's measured flash deltas as its 64-bit-runtime half: `uno` 26026->25310 (-716), `uno328pb` 26074->25358 (-716), `leonardo` 28170->27454 (-716), RAM unchanged on all three (heap removal is plan 05's half). Once plan 05 lands, the combined total is expected to reconcile to -1366 B flash / -8 B RAM per 155-RESEARCH.md's `k > 4194303UL` measurement -- record the 2 B delta against the ROADMAP's `-1364 B` header (the `4000000UL` figure) with its cause (the guard-constant choice, OQ-1) in that record.
- `check_no_heap_or_64bit_symbols.py` still exits 1 (heap symbols only) until plan 05 lands; do not treat this as a regression.
- DEAD-03, DEAD-04 and DEAD-05 remain `Pending` in REQUIREMENTS.md by design -- plan 06 closes them once the phase's full corpus (including plan 05's and plan 06's own artefacts) is in place and the `check_dead05_phrasing.py` full-corpus run is clean.

---
*Phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: firestarter/tests/test_voltage_reformulation_oracle.py
- FOUND: firestarter/src/boards/rurp_common.cpp
- FOUND: commit e26e9ab (test(155-04): voltage reformulation oracle)
- FOUND: commit 46dd574 (refactor(155-04): 32-bit reformulation)
