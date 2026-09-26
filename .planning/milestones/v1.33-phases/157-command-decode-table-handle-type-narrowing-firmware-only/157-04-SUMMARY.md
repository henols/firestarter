---
phase: 157-command-decode-table-handle-type-narrowing-firmware-only
plan: "04"
subsystem: firmware-decode
tags: [json_parser.c, store_field, unity, native-tests, fail-closed, dispatch, DECODE-05, planted-negative]

# Dependency graph
requires:
  - phase: 157-command-decode-table-handle-type-narrowing-firmware-only
    provides: "the compiler-derived field_desc_t table and store_field's saturate/mask policy split (src/json_parser.c, plan 02)"
  - phase: 157-command-decode-table-handle-type-narrowing-firmware-only
    provides: "firestarter_handle_t.protocol narrowed to uint8_t and .ctrl_flags narrowed to uint16_t (include/firestarter.h, plan 03), which makes the out-of-range hole live"
provides:
  - "Five executing native Unity cases in test_read_timing pinning DECODE-05: S1/S2 (out-of-range algorithm saturates AND dispatch fail-closes), S3 (in-range algorithm still dispatches), S4 (out-of-range flags masks, never sets every flag), S5 (out-of-range page-size saturates, not a plausible valid size)"
  - "Each case's captured RED transcript against the correct planted-negative probe (two distinct probes required, not one), run in a throwaway detached worktree and fully discarded"
  - "C-18 confirmed in practice: S4 passes VACUOUSLY against the saturation-deleted probe and requires its own saturating-bitmask probe"
  - "C-20 confirmed in practice: S5's consumer-side half (eeprom28c_page_mask) is source-level evidence only, recorded as a comment, because the function is static and unreachable from any test"
  - "The native case-count movement (172 -> 177 on both native and native_nodevtools) handed forward to Phase 158 / LAND-01, not absorbed into either baseline file"
affects: [157-05-PLAN, 157-06-PLAN, 157-07-PLAN, "158-LAND-01"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-probe RED capture for a safety-case suite: a saturation-deleted probe (reddens the ordinal-saturation cases) and a saturating-bitmask probe (reddens the bitmask-masking case) are NOT interchangeable -- a single probe leaves one case's RED unproven"
    - "Throwaway git worktree add --detach probe, leaf-named exactly `firestarter` (test_scope_is_firmware_only's hard-coded expectation), used to author and destructively test cases against a planted-negative tree without ever touching the real checkout"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp

key-decisions:
  - "S2 (dispatch fail-closes), not S1 (stored byte correct), is the load-bearing case: a correct stored 0xFF is a different claim from configure_memory actually refusing the command, and S2 is the only thing in the repository that pins the second, contingent claim (ceiling 6)"
  - "S2's assertions are RESPONSE_CODE_ERROR plus all three operation pointers NULL -- test_not_implemented.cpp's local idiom -- rather than comparing against a named handler's function pointer, which is not exported to tests and no suite in the tree does"
  - "S3 asserts only response_code != RESPONSE_CODE_ERROR after configure_memory, with no operation-pointer assertion, because configure_sram is a stub leaving firestarter_operation_init NULL on a genuine success path (test_configure_memory.cpp precedent)"
  - "S4 asserts the ctrl_flags == 0 equality PLUS three separate per-bit assertions (FLAG_FORCE, FLAG_SKIP_ERASE, FLAG_SKIP_BLANK_CHECK all clear), so the case reads as what it prevents rather than as a bare equality"
  - "S5 asserts the parse-level 0xFFFF saturation only; the consumer-side half (eeprom28c_page_mask rejecting 0xFFFF via both its range and power-of-two guards, returning AT28C_PAGE_SIZE_FALLBACK - 1, a mask not a size) is recorded as an in-file comment, not an assertion, because the function is `static` and unreachable from any test (C-20)"
  - "Two probes, not one, were required to capture every case's RED: probe A (store_field's width < sizeof(uint32_t) saturation branch deleted) reddens S1/S2/S5 but S4 passes VACUOUSLY there (a truncating store reduces wire flags 65536 to 0 before any policy runs); probe B (the key_flags row switched from FIELD_MASK to FIELD) reddens only S4, observed ctrl_flags == 0xFFFF. This corrects 157-VALIDATION.md's Wave-0 row (C-18), which claimed a single saturation-deleted probe reddens S1, S2 AND S4."
  - "The native case-count movement (172 -> 177, both envs) is recorded as a handoff to Phase 158 / LAND-01 and neither baseline file (size_baseline.json, size_baseline_base01.json) was edited"

patterns-established:
  - "A safety-case suite with a saturate-vs-mask policy split needs one probe per policy branch, not one probe for the whole suite -- documented here as the reusable shape for any future per-field policy audit"

requirements-completed: []

coverage:
  - id: D1
    description: "S1/S2: an out-of-range wire algorithm saturates to 0xFF (not truncating to a real handler's protocol value) AND configure_memory's dispatch fail-closes with RESPONSE_CODE_ERROR and all three operation pointers NULL"
    requirement: "DECODE-05"
    verification:
      - kind: integration
        ref: "pio test -e native -f \"*test_read_timing*\" => test_out_of_range_algorithm_saturates_not_truncates PASS, test_out_of_range_algorithm_dispatch_fail_closes PASS; both seen RED against the saturation-deleted probe (Expected 255 Was 5 / Expected 0 Was 1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "S3: a valid in-range algorithm still dispatches (non-regression guard -- S1/S2 cannot be satisfied by breaking every algorithm)"
    requirement: "DECODE-05"
    verification:
      - kind: integration
        ref: "pio test -e native -f \"*test_read_timing*\" => test_in_range_algorithm_still_dispatches PASS on both the real tree and probe A"
        status: pass
    human_judgment: false
  - id: D3
    description: "S4: an out-of-range wire flags value masks to 0 (never saturates to 0xFFFF), with the three dangerous flags (FLAG_FORCE, FLAG_SKIP_ERASE, FLAG_SKIP_BLANK_CHECK) individually asserted clear"
    requirement: "DECODE-05"
    verification:
      - kind: integration
        ref: "pio test -e native -f \"*test_read_timing*\" => test_out_of_range_flags_masks_never_sets_every_flag PASS on the real tree; seen RED against the saturating-bitmask probe B (Expected 0 Was 65535)"
        status: pass
    human_judgment: false
  - id: D4
    description: "S5: an out-of-range wire page-size saturates to 0xFFFF, not a plausible valid power-of-two size (65600 would otherwise truncate to 64); consumer-side rejection recorded as source-level evidence (C-20)"
    requirement: "DECODE-05"
    verification:
      - kind: integration
        ref: "pio test -e native -f \"*test_read_timing*\" => test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size PASS; seen RED against the saturation-deleted probe A (Expected 65535 Was 64)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Both native environments land at 177/177 in lockstep, the AVR uno image is byte-identical to plan 03's figures (proving no production code was added), both local check scripts pass, and the host wire-key parity gates still report 24 passed"
    verification:
      - kind: integration
        ref: "pio test -e native and pio test -e native_nodevtools => 177 test cases: 177 succeeded each; pio run -e uno => 23090 flash / 1562 RAM, zero warnings; check_build_warnings.py --rebuild and check_no_heap_or_64bit_symbols.py both exit 0; firestarter_app pytest tests/test_json_key_parity.py tests/test_revision_constants_parity.py => 24 passed"
        status: pass
    human_judgment: false

duration: 70min
completed: 2026-08-23
status: complete
---

# Phase 157 Plan 04: DECODE-05 Safety Cases Summary

**Authored and landed five native Unity cases pinning DECODE-05's fail-closed guarantee for out-of-range `algorithm`/`flags`/`page-size`, each proven RED against the correct one of two distinct planted-negative probes before being landed green, with the native case-count movement (172 -> 177) handed to Phase 158 rather than absorbed.**

## Performance

- **Duration:** ~70 min
- **Tasks:** 2 (author + RED-capture in a throwaway probe worktree; land green + commit + host gate)
- **Files modified:** 1 (`firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp`)

## Accomplishments

- Authored five new Unity cases in the existing `test_read_timing` suite:
  `test_out_of_range_algorithm_saturates_not_truncates` (S1),
  `test_out_of_range_algorithm_dispatch_fail_closes` (S2, the load-bearing case),
  `test_in_range_algorithm_still_dispatches` (S3, non-regression guard),
  `test_out_of_range_flags_masks_never_sets_every_flag` (S4),
  `test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size` (S5). Added
  `extern "C" { #include "memory.h" }` to reach `configure_memory` directly, following
  `test_not_implemented.cpp`'s include form -- no `platformio.ini` change needed since
  every native env's `build_src_filter` already carries `+<proms/>`.
- Ran the whole authoring-and-probing cycle in a throwaway `git worktree add --detach`
  probe at `/tmp/157-s-probe/firestarter` (leaf named exactly `firestarter` per
  `test_scope_is_firmware_only`'s hard-coded expectation), so nothing in
  `/workspaces/firestarter` was touched until the cases were proven.
- **Probe A** (saturation branch deleted from `store_field`): S1, S2 and S5 went RED
  exactly as required; S3 and S4 passed, with S4 passing **vacuously** because a
  truncating (non-saturating) store reduces a wire `flags` of 65536 to 0 before any
  policy check runs. This is the direct extension of the research's F-4 result --
  9 pre-existing cases + S3 + S4 pass, S1/S2/S5 fail.
- **Probe B** (the `key_flags` table row switched from `FIELD_MASK` to `FIELD` --
  the reference implementation's own verbatim behaviour): S4 went RED with `ctrl_flags`
  observed as `0xFFFF`, exactly the fail-open OD-1 exists to reject. S1, S2, S3 and S5
  passed on this probe, and all nine pre-existing cases passed on both probes.
- **C-18 confirmed in practice, not merely cited**: `157-VALIDATION.md`'s Wave-0 row
  claims a single saturation-deleted probe reddens S1, S2 AND S4 -- this session's
  own Probe A run demonstrates that claim is false for S4 (it passes vacuously there).
  Two distinct probes are required and are not interchangeable.
- **C-20 confirmed**: S5 asserts only the parse-level `0xFFFF` saturation. The
  consumer-side half is recorded as an in-file comment: `eeprom28c_page_mask` is
  `static` in `src/proms/eeprom_28c.cpp` and unreachable from any test; `0xFFFF`
  fails both its guards (exceeds `AT28C_PAGE_SIZE_MAX` 512, and fails the
  power-of-two test), so the function returns `AT28C_PAGE_SIZE_FALLBACK - 1` (63),
  a mask, not the size (64).
- Discarded the probe worktree completely (`git checkout -- .`, `git worktree remove
  --force`, `git worktree prune`) and reproduced the identical five cases by hand in
  the real tree, confirmed `git worktree list`, `git branch --list`, and
  `git rev-list --count HEAD` (850, unchanged) all matched the pre-task state.
- Landed the five cases in `/workspaces/firestarter`: `pio test -e native -f
  "*test_read_timing*"` reports `14 test cases: 14 succeeded`; `pio test -e native`
  and `pio test -e native_nodevtools` each report `177 test cases: 177 succeeded`
  over 17 suites, in lockstep.
- Confirmed `pio run -e uno` is byte-identical to plan 03's figures (`23090` flash /
  `1562` RAM, zero `warning:` lines) -- the cheapest available proof that this plan
  added no production code, since a native test case cannot change an AVR image.
- Ran `check_build_warnings.py --rebuild` (PASS, `macro_redefinition=0` on all three
  AVR targets, native watermark unmoved) and `check_no_heap_or_64bit_symbols.py`
  (PASS, `heap=0,64bit=0` on all three AVR targets) -- both exit 0 (OD-6).
- Ran `check_size_baseline.py --policy merge05 --baseline
  scripts/baseline/size_baseline_base01.json --rebuild`: the two native `cases`
  lines now read `observed=177` (moved from `172`) against the frozen `baseline=141`;
  no AVR flash or RAM leg failed. Neither baseline file was edited.
- Committed inside the submodule as `8edfd6e`
  (`test(157-04): prove an out-of-range algorithm and flags fail closed`); ran the
  host wire-key parity gates in `firestarter_app` afterward (`24 passed`), with zero
  `firestarter_app` files changed.

## Captured RED Transcripts (verbatim)

### Probe A -- saturation branch deleted from `store_field`

Command: direct execution of the compiled native test binary
(`.pio/build/native/firestarter_native`) after `pio test -e native -f
"*test_read_timing*"` built it; the direct-binary invocation is quoted here as the
authoritative oracle because `pio test`'s own process wrapper printed a
`SIGQUIT`/off-by-one artifact on this errored run (`15 test cases: 3 failed, 11
succeeded` instead of the true `14 Tests 3 Failures`) -- the same class of runner
artifact the phase's own `157-before-figures.md` §5 documents for `RUN_TEST` lexical
counts ("trust the runner, never the grep"; here neither the wrapper's own summary
line nor a naive grep was trustworthy, only the underlying Unity binary's own report):

```
test/native/avr/test_read_timing/test_read_timing_params.cpp:298:test_read_settling_us_parsed_from_json:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:299:test_read_strobe_us_parsed_from_json:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:300:test_read_timing_fields_default_zero_when_absent:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:301:test_read_settling_us_capped_at_max:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:302:test_page_size_parsed_from_json:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:303:test_page_size_defaults_zero_when_absent:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:304:test_page_size_resets_between_two_parses_on_the_same_handle:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:305:test_unknown_key_before_a_known_key_does_not_desync_the_token_walk:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:306:test_unknown_key_before_page_size_does_not_desync_the_token_walk:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:552:test_out_of_range_algorithm_saturates_not_truncates:FAIL: Expected 255 Was 5. 261 must saturate to 0xFF, not truncate to 0x05 -- 0x05 is PROTO_FLASH_5V_PAGE, a real handler configure_memory would dispatch into
test/native/avr/test_read_timing/test_read_timing_params.cpp:213:test_out_of_range_algorithm_dispatch_fail_closes:FAIL: Expected 0 Was 1. this is the case that would have caught the defect: the stored byte being right (S1) is not the same claim as the dispatch fail-closing -- a saturated 0xFF must reach configure_memory's generic fail-closed tail
test/native/avr/test_read_timing/test_read_timing_params.cpp:309:test_in_range_algorithm_still_dispatches:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:310:test_out_of_range_flags_masks_never_sets_every_flag:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:289:test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size:FAIL: Expected 65535 Was 64. 65600 must saturate to 0xFFFF, not truncate to 64 -- 64 is a perfectly valid page size, which is what makes the hole silent

-----------------------
14 Tests 3 Failures 0 Ignored 
FAIL
```

Result: **S1, S2 and S5 FAIL; S3, S4 and all nine pre-existing cases PASS** -- exactly
the required outcome. The full `pio test -e native` run on this probe reported
`178 test cases: 3 failed, 174 succeeded` via its own wrapper (the same +1 artifact:
9 pre-existing test_read_timing cases + S3 + S4 = 11 pass in that suite, plus 163
pass across the other 16 suites = 174 total pass, matching the wrapper's own
"174 succeeded" figure exactly even though its total-cases line is off by one), which
is the direct extension of the research's own F-4 result (that tree was 172 of 172
green before these cases existed; here it is 174 pass / 3 fail = 177 true total).

### Probe B -- `key_flags` row switched from `FIELD_MASK` to `FIELD` (saturate)

Command: same direct-binary invocation, after `git checkout -- src/json_parser.c`
restored Probe A's edit and the `key_flags` row was changed to
`FIELD(key_flags, ctrl_flags, 0)`:

```
test/native/avr/test_read_timing/test_read_timing_params.cpp:298:test_read_settling_us_parsed_from_json:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:299:test_read_strobe_us_parsed_from_json:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:300:test_read_timing_fields_default_zero_when_absent:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:301:test_read_settling_us_capped_at_max:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:302:test_page_size_parsed_from_json:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:303:test_page_size_defaults_zero_when_absent:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:304:test_page_size_resets_between_two_parses_on_the_same_handle:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:305:test_unknown_key_before_a_known_key_does_not_desync_the_token_walk:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:306:test_unknown_key_before_page_size_does_not_desync_the_token_walk:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:307:test_out_of_range_algorithm_saturates_not_truncates:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:308:test_out_of_range_algorithm_dispatch_fail_closes:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:309:test_in_range_algorithm_still_dispatches:PASS
test/native/avr/test_read_timing/test_read_timing_params.cpp:260:test_out_of_range_flags_masks_never_sets_every_flag:FAIL: Expected 0 Was 65535. an out-of-range wire flags value must mask to the width-limited truncation, never saturate to 0xFFFF -- saturating a bitmask turns on every flag at once, a fail-open in a fail-closed phase
test/native/avr/test_read_timing/test_read_timing_params.cpp:311:test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size:PASS

-----------------------
14 Tests 1 Failures 0 Ignored 
FAIL
```

Result: **S4 FAILS with `h.ctrl_flags` observed as `65535` (0xFFFF); S1, S2, S3, S5
and all nine pre-existing cases PASS** -- exactly the required outcome, and the
observed value is precisely the fail-open OD-1 exists to reject.

**Why two probes were needed, restated:** with the saturation branch deleted (Probe
A), a wire `flags` of `65536` is truncated to `0` by the width-limited `memcpy`
before any policy check runs, so S4's `ctrl_flags == 0` equality holds and the case
passes VACUOUSLY. `157-VALIDATION.md`'s Wave-0 row claims a single saturation-deleted
probe reddens S1, S2 and S4; that is wrong for S4 and is correction **C-18** --
verified here, not merely repeated from the plan. The second RED direction is also
recorded: on the pre-phase tree at `1151dc4`, `ctrl_flags` was 32 bits wide and would
have stored `0x10000` for a wire `flags` of `65536` (no defined bit set, still a
non-zero, non-matching value), so S4 was RED there too, independent of this phase's
policy split.

## Task Commits

1. **Task 1: Author the five safety cases in a probe tree and capture each RED** --
   no commit (all work happened in a throwaway `git worktree` at
   `/tmp/157-s-probe/firestarter`, fully discarded before the task ended; no tracked
   file in `/workspaces/firestarter` changed; `git rev-list --count HEAD` was 850
   before and after).
2. **Task 2: Land the five cases green, and hand the case-count movement to Phase
   158** -- `8edfd6e`
   (`test(157-04): prove an out-of-range algorithm and flags fail closed`).

## Files Created/Modified

- `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` -- added
  `extern "C" { #include "memory.h" }` and five new cases (S1-S5) plus their
  `RUN_TEST` entries; `setUp`, `tearDown`, `make_handle`, `parse_json`, the local
  `#define READ_TIMING_MAX_US`, and all nine pre-existing case bodies are
  byte-identical to their pre-plan state (confirmed: `git diff HEAD~1` shows zero
  deletion lines, only additions plus the one include line).

## Decisions Made

- **S2, not S1, is the load-bearing case.** A correct stored `0xFF` is a different
  claim from `configure_memory` actually refusing the command; S2 is the only thing
  in the repository that pins the second, dispatch-table-contingent claim (ceiling
  6: saturation-as-fail-closed is contingent on `0xFF` being unmapped in
  `configure_memory`'s chain today).
- **S2's shape copies `test_not_implemented.cpp`'s idiom** (`RESPONSE_CODE_ERROR`
  plus all three operation pointers NULL) rather than comparing against a named
  handler's function pointer, which is not exported to tests.
- **S3 asserts no operation pointer**, per `test_configure_memory.cpp`'s own
  documented reason (`configure_sram` is a stub leaving
  `firestarter_operation_init` NULL on a genuine success path).
- **S4 asserts three per-bit clauses in addition to the equality**, so the case
  reads as what it prevents (all nine flags being set at once by a saturating
  bitmask) rather than as a bare equality that could pass for the wrong reason.
- **S5 asserts the parse-level saturation only**; the consumer-side half
  (`eeprom28c_page_mask`) is recorded as an in-file comment, per C-20, because the
  function is `static` and unreachable from any test.
- **Two probes, confirmed non-interchangeable in practice.** Probe A (saturation
  deleted) reddens S1/S2/S5 but S4 passes vacuously there; Probe B (saturating
  bitmask) reddens only S4. This is C-18, verified by this session's own two runs,
  not merely cited from the plan.
- **The direct compiled test binary was used as the authoritative RED/GREEN oracle**
  for both probes, because `pio test`'s own process wrapper printed an internally
  inconsistent total-case count (`15`/`178` instead of the true `14`/`177`) on both
  errored runs -- a `SIGQUIT`(Probe A)/`SIGHUP`(Probe B) artifact of the wrapper's
  process supervision on a non-zero Unity exit code, not a defect in the test
  content. The wrapper's own per-suite pass/fail breakdown matched the direct
  binary exactly in both cases; only its printed *total* case count was
  self-inconsistent (`failed + succeeded` did not sum to the stated total).
- **The native case-count movement (172 -> 177, both `native` and
  `native_nodevtools`) is handed to Phase 158 / LAND-01, not absorbed.** Neither
  `scripts/baseline/size_baseline.json` nor `size_baseline_base01.json` was edited.
  Plan 05 will move the count again.

## Deviations from Plan

None -- plan executed exactly as written. The `pio test` wrapper's total-case-count
artifact on both errored probe runs (noted above) is a pre-existing tooling quirk
triggered by the RED-capture requirement itself, not a plan deviation; it was
resolved by falling back to the directly-compiled test binary's own report, which is
consistent with the phase's own established "trust the runner, never a naive count"
discipline (`157-before-figures.md` §5), applied here one level deeper than the
`grep -c RUN_TEST` case that discipline was originally written for.

## Issues Encountered

- **`pio test`'s process-wrapper reported an internally inconsistent total-case
  count on both errored probe runs** (`15 test cases: 3 failed, 11 succeeded` on
  Probe A, `15 test cases: 1 failed, 13 succeeded` on Probe B -- neither sums to
  its own stated total, and both were one higher than the true `14`). Resolved by
  running the compiled native test binary directly
  (`.pio/build/native/firestarter_native`), whose own Unity summary (`14 Tests N
  Failures`) matched the per-case PASS/FAIL lines exactly and cross-checked against
  the full-suite `pio test -e native` pass-count arithmetic (163 unrelated-suite
  passes + per-suite pass count == the wrapper's own "succeeded" figure in both
  cases). This did not affect the landed, real-tree result: `pio test -e native -f
  "*test_read_timing*"` on the finished tree cleanly reports `14 test cases: 14
  succeeded` with no wrapper artifact, because that run has no failing case.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter` HEAD is now `8edfd6e` on `gsd/v1.33-source-hygiene-firmware-size-reduction`;
  `git -C firestarter status --porcelain` is empty; no `.rej`/`.orig` file exists
  anywhere; the probe worktree and its branch left no trace
  (`git worktree list`, `git branch --list`, `git rev-list --count HEAD` all matched
  their pre-task values before this plan's own commit).
- Plan 05 (the six round-trip cases OD-5 takes, plus the read-strobe cap test) can
  land in the same suite; it will move the native case count again from 177.
- Plan 06/07 should read this SUMMARY when composing the after-figures record and
  the final requirement closure: the case-count handoff is `172 -> 177` on BOTH
  native envs at THIS plan's position (before plan 05's own further movement), the
  AVR `uno` image is unchanged from plan 03 (`23090`/`1562`), and
  `scripts/baseline/size_baseline.json` still records `172` today (not re-anchored
  by this plan, per its own prohibition).
- **DECODE-05's requirement status is intentionally NOT flipped in
  `.planning/REQUIREMENTS.md` by this plan.** Per this plan's own instructions,
  Plan 07 (this phase's closeout) owns the final status flip for all seven DECODE
  requirements. DECODE-05's evidence is fully recorded above (the five cases, their
  captured REDs, the two-probe distinction, ceilings 6 and C-20) for Plan 07 to
  cite directly.
- No blockers.

---
*Phase: 157-command-decode-table-handle-type-narrowing-firmware-only*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp`
- FOUND: `.planning/phases/157-command-decode-table-handle-type-narrowing-firmware-only/157-04-SUMMARY.md`
- FOUND: firmware commit `8edfd6e` (`git -C firestarter log --oneline --all`)
- FOUND: meta commit `53c20523` (`git log --oneline --all`)
