---
phase: 157-command-decode-table-handle-type-narrowing-firmware-only
plan: "05"
subsystem: firmware-decode
tags: [json_parser.c, store_field, unity, native-tests, offsetof, round-trip, DECODE-06, DECODE-03, planted-negative]

# Dependency graph
requires:
  - phase: 157-command-decode-table-handle-type-narrowing-firmware-only
    provides: "the compiler-derived field_desc_t table, store_field's clamp/saturate/mask steps, and READ_TIMING_MAX_US hoisted above the table (src/json_parser.c, plan 02)"
  - phase: 157-command-decode-table-handle-type-narrowing-firmware-only
    provides: "the five DECODE-05 safety cases and the two-probe RED-capture pattern in test_read_timing_params.cpp (plan 04), which this plan extends rather than replaces"
provides:
  - "An executing read-strobe-us cap case (did not exist before this plan, C-8) and an equality-tightened read-settling-delay cap case, both proven RED against a removed clamp column AND against a clamp-to-zero regression, with the equality-RED / upper-bound-GREEN contrast measured on the same broken tree"
  - "Six store-round-trip cases (mem_size, address, pulse_delay, chip_id, vpp_mv, pins) closing the last six of the eleven field-table rows -- every row now has an executing test proving it writes the member its offsetof names (ceiling 7 CLOSED)"
  - "Two planted wrong-member-row probes (key_vpp_mv -> chip_id, key_pin_count -> page_size), each localising to exactly its own affected case"
  - "The final native case-count handoff to Phase 158 / LAND-01: 172 -> 177 -> 184 on both native and native_nodevtools, 17 suites unchanged"
affects: ["158-LAND-01", "158-LAND-03", "157-06-PLAN", "157-07-PLAN"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Offset-oracle round-trip case: assert the target member equals the parsed value AND every other table-written member is still 0 (make_handle's zero-init makes this well-founded) -- this is what actually distinguishes 'the row fits the column' (_Static_assert) from 'the row names the right member' (only an executing test)"
    - "Unity aborts a test function on its first failing assertion (longjmp-based TEST_ASSERT) -- to observe BOTH halves of an offset-oracle failure (target wrong AND neighbour carrying the value) against one planted negative, temporarily reorder the assertions in the probe, capture the second failure, then restore the landed order before discarding the probe"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp

key-decisions:
  - "Both cap assertions tightened from '<=' to an exact equality against READ_TIMING_MAX_US: zero passes an upper bound and zero is the loaded value for BOTH knobs (read_settling_us == 0 means no settling delay; read_strobe_us == 0 means use the firmware default of 3 microseconds), so the weaker form was dangerous, not merely loose"
  - "The equality-RED / upper-bound-GREEN contrast is the measured (not asserted) justification for the tightening: on the identical clamp-to-zero-broken tree, the equality form fails (Expected 1000 Was 0) while the old upper-bound form passes"
  - "Six round-trip cases assert ALL ten other table-written members stay 0, not just the target -- a wrong offsetof writes into a neighbour, which only the neighbour assertions catch; asserting the target alone would pass on a row that overwrites a different field with the same wire value by coincidence of type width"
  - "CMD_READ used uniformly for all six round-trip cases (arbitrary but consistent -- none of the six target fields are cmd-gated in json_parse or store_field)"
  - "The vpp_mv wire key is spelled with an UNDERSCORE, matching the declared PROGMEM string exactly; verified no hyphenated spelling exists anywhere in the file"
  - "Two READ_TIMING_MAX_US definitions (production, test-local) are an unremovable duplicate (C-21): the production constant is a file-scope #define in a .c translation unit, not a header export, so the test cannot reference it -- recorded in a comment above the test-local #define rather than fixed"
  - "The native case-count movement (172 -> 177 -> 184, both envs) is handed to Phase 158 / LAND-01; BASE-01's frozen 141 is LAND-03's. Neither baseline file was edited."

patterns-established:
  - "For a safety-case or offset-oracle suite, when Unity's abort-on-first-failure would hide a needed second observation, use a throwaway probe-local assertion reorder (never landed) to surface it independently, then restore the landed order before the probe is discarded -- this keeps the landed test's assertion order 'most important check first' while still letting the executor prove the full failure mode occurred"

requirements-completed: []

coverage:
  - id: D1
    description: "read-strobe-us cap: an out-of-range wire value clamps to EXACTLY READ_TIMING_MAX_US (1000), proven by an executing equality assertion where none existed before (C-8)"
    requirement: "DECODE-06"
    verification:
      - kind: integration
        ref: "pio test -e native -f \"*test_read_timing*\" => test_read_strobe_us_capped_at_max PASS; seen RED against both the removed-clamp probe (Expected 1000 Was 9999) and the clamp-to-zero probe (Expected 1000 Was 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "read-settling-delay cap tightened from an upper bound to an equality against READ_TIMING_MAX_US, with the measured equality-RED / upper-bound-GREEN contrast on the same clamp-to-zero-broken tree as evidence the tightening added coverage"
    requirement: "DECODE-06"
    verification:
      - kind: integration
        ref: "pio test -e native -f \"*test_read_timing*\" => test_read_settling_us_capped_at_max PASS on the real tree; on the clamp-to-zero probe tree, equality form FAILS (Expected 1000 Was 0) while the temporarily-restored upper-bound form PASSES"
        status: pass
    human_judgment: false
  - id: D3
    description: "All eleven field-table rows have an executing round-trip test proving they write the member their offsetof names -- closing ceiling 7 (the _Static_assert guards prove an offset fits the column, never that it names the right member)"
    requirement: "DECODE-03"
    verification:
      - kind: integration
        ref: "pio test -e native -f \"*test_read_timing*\" => the six new round-trip cases (mem_size, address, pulse_delay, chip_id, vpp_mv, pins) PASS; a planted wrong-member row (key_vpp_mv -> chip_id) reddens exactly test_vpp_mv_round_trips_through_the_field_table on both halves (target Expected 12000 Was 0; neighbour chip_id Expected 0 Was 12000 via a temporary probe-only reorder), and a second planted swap (key_pin_count -> page_size) reddens exactly test_pin_count_round_trips_through_the_field_table"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both native environments land at 184/184 in lockstep (172 -> 177 -> 184), 17 suites unchanged; the AVR uno/uno328pb/leonardo images are byte-identical to plan 03's figures; both local check scripts pass; the host wire-key parity gates still report 24 passed"
    verification:
      - kind: integration
        ref: "pio test -e native and pio test -e native_nodevtools => 184 test cases: 184 succeeded each, 17 suites; pio run -e uno -e uno328pb -e leonardo => RAM 1562/1568/2003, zero warnings; check_build_warnings.py --rebuild and check_no_heap_or_64bit_symbols.py both exit 0; firestarter_app pytest tests/test_json_key_parity.py tests/test_revision_constants_parity.py => 24 passed"
        status: pass
    human_judgment: false

duration: 90min
completed: 2026-08-23
status: complete
---

# Phase 157 Plan 05: Read-Timing Cap Equality + Full Field-Table Round-Trip Coverage Summary

**Added the missing `read-strobe-us` cap case, tightened both read-timing cap assertions from an upper bound to an exact equality (with a measured equality-RED / upper-bound-GREEN contrast on a planted clamp-to-zero regression), and added six store-round-trip cases closing all eleven `key_parsers[]` rows to executing offset-oracle coverage -- each with its RED captured against a planted negative in a throwaway, fully-discarded probe worktree, landing the native case count at 184 on both environments.**

## Performance

- **Duration:** ~90 min
- **Tasks:** 3 (strobe cap + tightening + RED capture in probe A; round-trip cases + localisation RED capture in probe B; land green + commit + host gate)
- **Files modified:** 1 (`firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp`)

## Accomplishments

- **Task 1 (probe `/tmp/157-c-probe/firestarter`):** Authored `test_read_strobe_us_capped_at_max` -- parses `{"cmd":1,"read-strobe-us":9999}` and asserts an equality against `READ_TIMING_MAX_US` -- and tightened the pre-existing `test_read_settling_us_capped_at_max`'s assertion from `TEST_ASSERT_TRUE(<=)` to `TEST_ASSERT_EQUAL_UINT32`, both with message-bearing forms stating the zero-is-loaded-value reasoning. Added a drift-risk comment above the test-local `#define READ_TIMING_MAX_US 1000UL` recording C-8/C-21 (the production constant is hoisted in `src/json_parser.c` but is a file-scope `.c`-TU `#define`, not a header export, so the two copies can drift silently and nothing gates it).
- **Probe C1** (both read-timing rows' `clamp` argument set to 0, meaning "no clamp"): both cap cases FAILED, each reporting the observed value `9999` -- proving both cases actually see the clamp column.
- **Probe C2** (`store_field`'s clamp step changed to store `0` instead of the clamp value on an over-limit input): both cap cases FAILED reporting observed value `0`. On the SAME broken tree, the settling case's assertion was temporarily reverted to its old upper-bound form and re-run: it PASSED. This equality-RED / upper-bound-GREEN contrast on one broken tree is the measured evidence that the tightening added real coverage, not cosmetic restyling. The equality form was restored before discarding the probe.
- Discarded probe A completely: `git checkout -- .`, `git worktree remove --force`, `git worktree prune`; confirmed `git worktree list`, `git branch --list` (34, unchanged), and `git rev-list --count HEAD` (851, unchanged) all matched the pre-task state.
- **Task 2 (probe `/tmp/157-d-probe/firestarter`):** Authored six round-trip cases -- `test_memory_size_round_trips_through_the_field_table` (`memory-size`:65536 -> `mem_size`), `test_address_round_trips_through_the_field_table` (`address`:4096 -> `address`), `test_pulse_delay_round_trips_through_the_field_table` (`pulse-delay`:1000 -> `pulse_delay`), `test_chip_id_round_trips_through_the_field_table` (`chip-id`:4660 -> `chip_id`), `test_vpp_mv_round_trips_through_the_field_table` (`vpp_mv`:12000, UNDERSCORE key, matching the declared PROGMEM string exactly, -> `vpp_mv`), `test_pin_count_round_trips_through_the_field_table` (`pin-count`:28 -> `pins`). Each case asserts the target member's value AND that all ten other table-written members are still 0, using the Unity assertion width matching each member's declared type.
- **Probe D** (`key_vpp_mv` row's member argument changed to `chip_id`): `test_vpp_mv_round_trips_through_the_field_table` FAILED with the target assertion `Expected 12000 Was 0`; all other cases (five other round-trip cases, both cap cases, all five plan-04 DECODE-05 cases, all nine pre-existing cases) stayed green. Because Unity aborts a test function on its first failing assertion, the neighbour half of the same failure was captured by a temporary, probe-only reorder that checked `chip_id` BEFORE the target: this produced `Expected 0 Was 12000` on the `chip_id` neighbour assertion, in the same case, on the same planted probe. The reorder was reverted to the landed order (target first) before the row was restored.
- **Probe D confirmation #2** (`key_pin_count` row's member argument changed to `page_size`): `test_pin_count_round_trips_through_the_field_table` FAILED (`Expected 28 Was 0`); recorded as observed -- no other case moved, including plan 04's own page-size saturation case, which stayed green because it parses a different JSON payload against its own, unaffected `key_page_size` row.
- Discarded probe B completely: `git checkout -- .`, `git worktree remove --force`, `git worktree prune`; confirmed `git worktree list`, `git branch --list` (34, unchanged), and `git rev-list --count HEAD` (851, unchanged) all matched the pre-task state.
- **Task 3:** Landed all seven cases and the one tightened assertion in `/workspaces/firestarter` by hand (matching the probe-proven bodies exactly), appended their seven `RUN_TEST` entries in declaration order. `pio test -e native -f "*test_read_timing*"` reports `21 test cases: 21 succeeded`; `pio test -e native` and `pio test -e native_nodevtools` each report `184 test cases: 184 succeeded` over 17 suites, in lockstep.
- Confirmed `pio run -e uno -e uno328pb -e leonardo` reports the SAME RAM figures as plan 03 (`1562` / `1568` / `2003`), zero `warning:` lines -- the cheapest available proof this plan added no production code, since a native test case cannot change an AVR image.
- Ran `check_build_warnings.py --rebuild` (PASS, `macro_redefinition=0` on all three AVR targets; native watermark unmoved at 998, 168 below the 1166 watermark) and `check_no_heap_or_64bit_symbols.py` (PASS, `heap=0,64bit=0` on all three AVR targets) -- both exit 0 (OD-6).
- Ran `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild`: the two native `cases` lines now read `observed=184` (moved from 177) against the frozen `baseline=141`; no AVR flash or RAM leg failed. Neither baseline file was edited.
- Committed inside the submodule as `785e644` (`test(157-05): cap read-strobe-us, tighten both cap assertions, round-trip every table row`); ran the host wire-key parity gates in `firestarter_app` afterward (`24 passed`), with zero `firestarter_app` files changed.

## Captured RED Transcripts (verbatim)

### Probe C1 -- both read-timing `clamp` arguments set to 0 ("no clamp")

Command: `pio test -e native -f "*test_read_timing*"` in `/tmp/157-c-probe/firestarter` after `sed`-ing both `FIELD(key_read_settling, read_settling_us, READ_TIMING_MAX_US)` and `FIELD(key_read_strobe, read_strobe_us, READ_TIMING_MAX_US)` to `..., 0)`:

```
test/native/avr/test_read_timing/test_read_timing_params.cpp:331: test_read_settling_us_parsed_from_json	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:332: test_read_strobe_us_parsed_from_json	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:333: test_read_timing_fields_default_zero_when_absent	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:161: test_read_settling_us_capped_at_max: Expected 1000 Was 9999. read_settling_us must clamp to EXACTLY READ_TIMING_MAX_US -- T-44-01's mitigation for an absurd JSON value reaching delayMicroseconds() in the read loop; an equality, not an upper bound, because 0 passes an upper bound and 0 is this knob's own loaded value ("no settling delay")	[FAILED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:178: test_read_strobe_us_capped_at_max: Expected 1000 Was 9999. read_strobe_us must clamp to EXACTLY READ_TIMING_MAX_US -- T-44-01's mitigation for an absurd JSON value reaching delayMicroseconds() in the read loop; an equality, not an upper bound, because 0 passes an upper bound and 0 is this knob's own loaded value ("use the firmware default of 3 microseconds")	[FAILED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:336: test_page_size_parsed_from_json	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:337: test_page_size_defaults_zero_when_absent	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:338: test_page_size_resets_between_two_parses_on_the_same_handle	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:339: test_unknown_key_before_a_known_key_does_not_desync_the_token_walk	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:340: test_unknown_key_before_page_size_does_not_desync_the_token_walk	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:341: test_out_of_range_algorithm_saturates_not_truncates	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:342: test_out_of_range_algorithm_dispatch_fail_closes	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:343: test_in_range_algorithm_still_dispatches	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:344: test_out_of_range_flags_masks_never_sets_every_flag	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:345: test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size	[PASSED]
Program received signal SIGINT (Interrupt)
-------- native:native/avr/test_read_timing [ERRORED] Took 0.61 seconds --------
============ 16 test cases: 2 failed, 13 succeeded in 00:00:00.614 ============
```

Result: **both cap cases FAIL, each reporting observed value `9999`**, exactly the required outcome. (The wrapper's own total-case-count line, `16`, is one higher than the true `15` -- the same runner artifact plan 04's SUMMARY documents for errored runs; the per-case PASS/FAIL lines above are the authoritative record and were cross-checked line-by-line.)

### Probe C2 -- `store_field`'s clamp step changed to store 0 instead of the clamp value

Command: same suite, after reverting Probe C1's row edit (`git checkout -- src/json_parser.c`) and changing `store_field`'s clamp branch from `value = clamp;` to `value = 0;`:

```
test/native/avr/test_read_timing/test_read_timing_params.cpp:331: test_read_settling_us_parsed_from_json	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:332: test_read_strobe_us_parsed_from_json	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:333: test_read_timing_fields_default_zero_when_absent	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:161: test_read_settling_us_capped_at_max: Expected 1000 Was 0. read_settling_us must clamp to EXACTLY READ_TIMING_MAX_US -- ... ("no settling delay")	[FAILED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:178: test_read_strobe_us_capped_at_max: Expected 1000 Was 0. read_strobe_us must clamp to EXACTLY READ_TIMING_MAX_US -- ... ("use the firmware default of 3 microseconds")	[FAILED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:336: test_page_size_parsed_from_json	[PASSED]
... (remaining nine pre-existing/plan-04 cases all PASSED) ...
============ 16 test cases: 2 failed, 13 succeeded in 00:00:00.572 ============
```

Result: **both cap cases FAIL with observed value `0`**, exactly the required outcome.

**Contrast run**, same broken tree, `test_read_settling_us_capped_at_max`'s assertion temporarily reverted to `TEST_ASSERT_TRUE(h.read_settling_us <= READ_TIMING_MAX_US)`:

```
test/native/avr/test_read_timing/test_read_timing_params.cpp:331: test_read_settling_us_capped_at_max	[PASSED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:175: test_read_strobe_us_capped_at_max: Expected 1000 Was 0. ...	[FAILED]
============ 16 test cases: 1 failed, 14 succeeded in 00:00:02.056 ============
```

Result: **the upper-bound form PASSES on the identical clamp-to-zero-broken tree that reddens the equality form.** This equality-RED / upper-bound-GREEN contrast on one broken tree is the measured justification that the tightening added coverage rather than restyling an assertion. The equality form was restored (`TEST_ASSERT_EQUAL_UINT32_MESSAGE`) before the probe was discarded.

### Probe D -- `key_vpp_mv` row's member argument changed to `chip_id`

Command: `pio test -e native -f "*test_read_timing*"` in `/tmp/157-d-probe/firestarter` after `sed -i 's/FIELD(key_vpp_mv, vpp_mv, 0)/FIELD(key_vpp_mv, chip_id, 0)/' src/json_parser.c`, on the tree with all 20 cases (14 pre-existing/plan-04 + 6 new round-trip cases) landed:

```
... (all 18 other cases PASSED) ...
test/native/avr/test_read_timing/test_read_timing_params.cpp:449: test_vpp_mv_round_trips_through_the_field_table: Expected 12000 Was 0. a wrong offsetof in the vpp_mv row would write into a neighbouring member instead -- the compile-time guards cannot see that, only this executing round-trip can	[FAILED]
test/native/avr/test_read_timing/test_read_timing_params.cpp:530: test_pin_count_round_trips_through_the_field_table	[PASSED]
Program received signal SIGHUP (Hangup)
-------- native:native/avr/test_read_timing [ERRORED] Took 0.69 seconds --------
============ 21 test cases: 1 failed, 19 succeeded in 00:00:00.687 ============
```

Result: **only `test_vpp_mv_round_trips_through_the_field_table` FAILS** (target half: `Expected 12000 Was 0`); every other case -- the five other round-trip cases, both cap cases, all five plan-04 DECODE-05 cases, and all nine pre-existing cases -- stayed green. Localisation confirmed: a wrong row reddens exactly its own case.

**Neighbour-half confirmation**, same planted probe, with the `chip_id` neighbour assertion temporarily moved to run BEFORE the target assertion (Unity aborts a test on its first failing assertion, so with the landed order the target failure masks the neighbour observation):

```
test/native/avr/test_read_timing/test_read_timing_params.cpp:454: test_vpp_mv_round_trips_through_the_field_table: Expected 0 Was 12000. vpp_mv's row must not write into chip_id	[FAILED]
============ 21 test cases: 1 failed, 19 succeeded in 00:00:02.074 ============
```

Result: **the neighbour `chip_id` carries the wire value `12000`** -- confirming the second half of the offset-oracle claim (target left at 0, neighbour carrying the value) on the same planted row. The reorder was reverted to the landed order (target first) before the row was restored.

### Probe D confirmation #2 -- `key_pin_count` row's member argument changed to `page_size`

Command: same suite, after `sed -i 's/FIELD(key_pin_count, pins, 0)/FIELD(key_pin_count, page_size, 0)/' src/json_parser.c` (with `key_vpp_mv` restored to its correct row first):

```
... (all 19 other cases, including test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size, PASSED) ...
test/native/avr/test_read_timing/test_read_timing_params.cpp:481: test_pin_count_round_trips_through_the_field_table: Expected 28 Was 0. a wrong offsetof in the pin-count row would write into a neighbouring member instead -- the compile-time guards cannot see that, only this executing round-trip can	[FAILED]
Program received signal SIGHUP (Hangup)
============ 21 test cases: 1 failed, 19 succeeded in 00:00:00.570 ============
```

Result, recorded exactly as observed: **only `test_pin_count_round_trips_through_the_field_table` FAILS.** No other case moved -- notably, plan 04's own `test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size` stayed green, because it parses a wholly different JSON payload (`"page-size":65600`) through the unaffected `key_page_size` row on its own, independent handle.

## Task Commits

1. **Task 1: Author the strobe cap case, tighten both cap assertions, and prove both against a planted clamp break** -- no commit (all work happened in a throwaway `git worktree` at `/tmp/157-c-probe/firestarter`, fully discarded before the task ended; no tracked file in `/workspaces/firestarter` changed; `git rev-list --count HEAD` was 851 before and after).
2. **Task 2: Author the six store-round-trip cases and prove a planted row-member swap localises to one case** -- no commit (throwaway `git worktree` at `/tmp/157-d-probe/firestarter`, fully discarded; `git rev-list --count HEAD` was 851 before and after).
3. **Task 3: Land the seven cases and the tightening green, and hand the final case count to Phase 158** -- `785e644` (`test(157-05): cap read-strobe-us, tighten both cap assertions, round-trip every table row`).

## Files Created/Modified

- `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` -- added `test_read_strobe_us_capped_at_max` and six round-trip cases plus their seven `RUN_TEST` entries; tightened `test_read_settling_us_capped_at_max`'s assertion from an upper bound to an equality; added a drift-risk comment above the test-local `#define READ_TIMING_MAX_US`. `setUp`, `tearDown`, `make_handle`, `parse_json`, plan 04's five cases, and the eight untouched pre-existing cases are byte-identical to their pre-plan state (confirmed: `git diff HEAD~1` shows deletions only inside the settling cap case's assertion and the drift-comment expansion).

## Decisions Made

- **Both cap assertions tightened to equality**, per the plan's own requirement, with the equality-RED / upper-bound-GREEN contrast on Probe C2's broken tree as the measured justification (not merely asserted).
- **Six round-trip cases assert all ten neighbours, not just the target** -- this is the actual offset oracle; a target-only assertion would not catch a wrong `offsetof` that happens to write a plausible-looking value into a neighbour.
- **CMD_READ used uniformly** for all six round-trip cases; none of the six target members are cmd-gated in `json_parse` or `store_field`, so the choice is arbitrary but kept consistent for readability.
- **A temporary, probe-only assertion reorder** was used twice (in Probe C2's contrast run and in Probe D's neighbour-half confirmation) to work around Unity's abort-on-first-failure behaviour, always reverted to the landed order before the probe's row/assertion was itself restored and before the probe was discarded. Neither reorder was ever landed in `/workspaces/firestarter`.
- **The two `READ_TIMING_MAX_US` definitions are recorded, not fixed** (C-21): the production `#define` is a file-scope constant in a `.c` translation unit and has no header export to reference from the test.
- **The native case-count movement (172 -> 177 -> 184, both `native` and `native_nodevtools`) is handed to Phase 158 / LAND-01, not absorbed.** Neither `scripts/baseline/size_baseline.json` nor `size_baseline_base01.json` was edited.

## Deviations from Plan

None -- plan executed exactly as written. The Unity abort-on-first-failure limitation encountered while trying to observe both halves of Probe D's localisation failure in one run is a pre-existing property of the Unity framework, not a plan deviation; it was resolved by a temporary, probe-only assertion reorder (documented above), consistent with the phase's established probe-and-discard discipline. `pio test`'s own process-wrapper total-case-count artifact on errored runs (`16`/`21` instead of the true `15`/`20`) is the same pre-existing tooling quirk plan 04's SUMMARY documents; the per-case PASS/FAIL lines, which matched expectations exactly in every probe, were used as the authoritative record rather than the wrapper's summary line.

## Issues Encountered

- **Unity's `TEST_ASSERT_*` macros abort the current test function on the first failing assertion** (longjmp-based), which meant Probe D's planted `key_vpp_mv -> chip_id` swap only surfaced the target-half failure (`Expected 12000 Was 0`) in the landed assertion order, never the neighbour-half (`chip_id` carrying `12000`) in the same run. Resolved by a temporary, probe-only reorder that checked the `chip_id` neighbour assertion first, captured `Expected 0 Was 12000`, then reverted the reorder before the probe's planted row was itself restored. This did not affect the landed test, whose assertion order (target first, then all ten neighbours) is unchanged from the original authoring and reads as "check what this case is actually testing before checking what it must not have broken."
- **`pio test`'s process-wrapper reported an internally inconsistent total-case count on every errored probe run** (one higher than the true count in each case, e.g. `16 test cases: 2 failed, 13 succeeded` when the true total was `15`), matching the artifact plan 04's SUMMARY documents. The per-case PASS/FAIL lines matched expectations exactly in every probe and were used as the authoritative record. The landed, real-tree runs (`pio test -e native -f "*test_read_timing*"` => `21 test cases: 21 succeeded`; `pio test -e native` / `-e native_nodevtools` => `184 test cases: 184 succeeded`) show no wrapper artifact, because none of those runs contain a failing case.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter` HEAD is now `785e644` on `gsd/v1.33-source-hygiene-firmware-size-reduction`; `git -C firestarter status --porcelain` is empty; no `.rej`/`.orig` file exists anywhere; both probe worktrees and their working trees left no trace (`git worktree list`, `git branch --list` (34), `git rev-list --count HEAD` (851 before this plan's own commit, 852 after) all matched their pre-task values).
- **Final native case-count handoff to Phase 158 / LAND-01:** the count moved `172` (plan 02) `->` `177` (plan 04) `->` **`184`** (this plan) on BOTH `native` and `native_nodevtools`, in lockstep; the suite count is unchanged at `17`. `scripts/baseline/size_baseline.json` still records `172` today -- LAND-01 owns the re-record. BASE-01's frozen `141` is LAND-03's, from Phase 124.
- **Ceiling 7 is now CLOSED, stated explicitly as this plan's own headline claim:** all eleven `key_parsers[]` rows -- `mem_size`, `address`, `ctrl_flags`, `chip_id`, `pins`, `pulse_delay`, `vpp_mv`, `protocol`, `read_settling_us`, `read_strobe_us`, `page_size` -- now have an executing native test proving they write the member their `offsetof` names, by execution, not by assertion. (`protocol`/`ctrl_flags` from plan 04's DECODE-05 cases; `read_settling_us`/`read_strobe_us`/`page_size` from the pre-existing parse cases; the remaining six from this plan.)
- **DECODE-06's and DECODE-03's requirement status is intentionally NOT flipped in `.planning/REQUIREMENTS.md` by this plan.** Per this plan's own instructions, Plan 07 (this phase's closeout) owns the final status flip for all seven DECODE requirements. Their evidence is fully recorded above (the equality-RED / upper-bound-GREEN contrast for DECODE-06; the eleven-row round-trip closure and both localisation probes for DECODE-03) for Plan 07 to cite directly.
- Plan 06/07 should read this SUMMARY's `172 -> 177 -> 184` figure and the unchanged-17-suites figure when composing the after-figures record and the final requirement closure.
- No blockers.

---
*Phase: 157-command-decode-table-handle-type-narrowing-firmware-only*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp`
- FOUND: `.planning/phases/157-command-decode-table-handle-type-narrowing-firmware-only/157-05-SUMMARY.md`
- FOUND: firmware commit `785e644` (`git -C firestarter log --oneline --all`)
