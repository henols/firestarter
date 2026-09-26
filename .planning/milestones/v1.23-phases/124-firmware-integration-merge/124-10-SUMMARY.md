---
phase: 124-firmware-integration-merge
plan: "10"
subsystem: firmware-ci
tags: [firestarter, size-baseline, build-warnings, cold-vs-warm, merge05, merge06, gate-hardening]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    plan: "02"
    provides: "check_size_baseline.py --policy merge05 + the frozen scripts/baseline/size_baseline_base01.json this plan's MERGE-05 assertion runs against (never rewritten)."
  - phase: 124-firmware-integration-merge
    plan: "04"
    provides: "The landed tree (e2c422d) and its post-landing AVR/native figures this plan's re-baseline records as the new live default."
  - phase: 124-firmware-integration-merge
    plan: "08"
    provides: "[env:native_pinmap_provisional] -- the third native env this plan adds to native_envs + warnings.native so it stops being a KeyError/exit-2 blind spot."
  - phase: 124-firmware-integration-merge
    plan: "09"
    provides: "The final code-bearing tree (2bd7187) this plan measures -- no plan after 124-09 touches compiled firmware surface."
provides:
  - "scripts/baseline/size_baseline.json rewritten to the post-landing tree: new meta.warm_vs_cold_correction (corrects BASE-01's false clean-build claim -- 360 was warm, the same pre-landing tree measures 456 cold), new meta.deltas_vs_base01 (leonardo -56, uno +22, uno328pb +28, RAM unchanged, each labelled with its MERGE-05 clause), native watermarks re-baselined to each env's COLD figure (native/native_nodevtools 1166, native_pinmap_provisional 138)"
  - "The third native env present in BOTH native_envs and warnings.native (same key set, mechanically verified) so check_size_baseline.py's compare_native and check_build_warnings.py's check_env never KeyError/exit-2 on it"
  - "scripts/baseline/size_baseline_base01.json re-confirmed byte-identical (blob SHA b940c91655600a57ad7ef67cba723943af929daf) before and after this plan -- MERGE-05's frozen reference point was never touched"
  - "MERGE-05 discharged as an exit code on the final tree: --policy merge05 vs the frozen BASE-01 exits 0 with the exact RESEARCH-predicted deltas; default mode vs the NEW live baseline also exits 0"
  - "MERGE-06 discharged as an exit code on the final tree: --native-log for both pinned envs exits 0 at cases=141,suites=17; test_golden_trace_identity.py 6 passed"
  - "Every Phase-123 fixture/literal the re-baseline invalidated is repaired: 5 re-captured captured_* fixtures, 2 re-derived planted_* fixtures, 2 test modules' literals and provenance docstrings updated -- full firmware suite stays at 72 passed, 0 failed, no test arm added or removed"
affects: [124-11, 124-12, 124-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Cold-then-warm pio test pairing (rm -rf .pio/build/<env> + a single extended-timeout invocation, then an immediate second invocation with no clean) applied to THREE native envs this time, not two -- the third env's ratio (cold=138/warm=0) differs qualitatively from the two pinned envs' (cold=1166/warm=998), because it compiles only 1 suite instead of 17 and its warm re-run's auto-regenerated Unity runner recompile happens not to touch any redefinition-prone shim file. Recorded as a genuine measurement finding, not normalized to match the other two envs."
    - "Watermark-set-to-COLD-not-WARM is mechanical, not a judgment call: check_build_warnings.py's below-watermark arm returns INFO (not FAIL), so a COLD watermark stays green on both a cold CI run (OK) and a warm local re-run (INFO); a WARM watermark would instead go FAIL on the next cold CI run -- CI always builds cold."
    - "A re-baseline that changes the DEFAULT baseline's own figures downstream-invalidates any planted-violation fixture and any test literal that assumed the old default -- both the failure-figure literals (baseline/observed pair) and, less obviously, any test that synthesizes 'the post-landing figure' by rewriting an OLD default-baseline capture (test_policy_merge05_permits_the_measured_landing_deltas) must be re-derived, because the capture the synthesis started from no longer carries the old figure to rewrite FROM."

key-files:
  created: []
  modified:
    - firestarter/scripts/baseline/size_baseline.json
    - firestarter/tests/fixtures/captured_build_uno.log
    - firestarter/tests/fixtures/captured_build_uno328pb.log
    - firestarter/tests/fixtures/captured_build_leonardo.log
    - firestarter/tests/fixtures/captured_test_native_summary.log
    - firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log
    - firestarter/tests/fixtures/planted_size_baseline_flash_regression.log
    - firestarter/tests/fixtures/planted_build_warnings_avr_redef.log
    - firestarter/tests/fixtures/planted_build_warnings_native_excess.log
    - firestarter/tests/test_check_size_baseline.py
    - firestarter/tests/test_check_build_warnings.py

key-decisions:
  - "The three MERGE-05 `policy_*` planted fixtures (uno_over_band, leonardo_growth, ram_moved) were deliberately NOT re-derived -- they are asserted exclusively against the FROZEN size_baseline_base01.json (pre-landing figures), which this plan never modifies, so their pre-landing numbers (23932/23997, 26072/26073, 1573/1574) remain correct and unchanged. Re-deriving them would have been busywork against a target that stays fixed."
  - "test_policy_merge05_permits_the_measured_landing_deltas was rewritten, not merely re-pointed: before this plan it synthesized RESEARCH's PREDICTED post-landing deltas onto tmp_path copies of the then-still-pre-landing captured_build_*.log fixtures (because the real landing hadn't happened at authoring time). Since captured_build_*.log now literally carries the post-landing figures (re-captured by this plan's Task 1), the synthesis step was removed entirely -- the test now feeds the committed fixtures straight to the checker, turning a pre-landing PREDICTION into a direct post-landing MEASUREMENT. The now-unused `_rewrite_flash_used` helper and the `import re` it required were both removed rather than left as dead code."
  - "planted_build_warnings_native_excess.log's synthetic count was raised from 363 to 1206 (1200 macro-shaped + 6 non-macro), not to some smaller number just above 1166 -- keeping the same shape (macro-heavy, small non-macro tail) and a comfortable margin (40 lines) rather than a minimal one-line-over-the-line fixture, consistent with the original Phase-123 fixture's own margin ratio (363 vs 360 watermark = 3 lines over; this plan's margin is proportionally similar once the raised baseline is accounted for)."
  - "The re-derived native-excess fixture's header comment was worded to avoid the literal substring 'warning:' (no colon-adjacent 'warning' token) in its own prose, after discovering during derivation that WARNING_LINE_RE's coarse `warning:`-anywhere-on-a-line match counts comment lines too -- the same self-tripping-grep class Plan 124-09 documented for its own fixture. Verified: `grep -cE 'warning:'` on the finished file returns exactly 1206 (1200 macro-shaped + 6 non-macro), matching the intended synthetic count with zero header-comment inflation."

requirements-completed: []
# Per this plan's dispatch <requirement_ticking_scope>: .planning/REQUIREMENTS.md is
# NOT touched. Plan 124-12 is the sole owner of every MERGE-01..MERGE-08 tick. What
# is proved here, for 124-12 to cite: MERGE-05 discharged by --policy merge05 against
# the FROZEN size_baseline_base01.json (exit 0, deltas -56/+22/+28 matching RESEARCH
# exactly) AND by the default-mode gate against the newly re-baselined live default
# (exit 0); MERGE-06 discharged by --native-log for both pinned envs (exit 0,
# cases=141,suites=17) and by the golden-trace pin (6 passed).

coverage:
  - id: D1
    description: "Final tree measured with the build state pinned: three AVR clean rebuilds (byte-identical to Plans 124-04/06/08/09's recorded landing figures, 0 delta across five intervening code-bearing plans) and cold+warm pio test for all three native envs (native/native_nodevtools cold=1166/warm=998; native_pinmap_provisional cold=138/warm=0), with the exact rm -rf + single-invocation sequence stated"
    requirement: "MERGE-05"
    verification:
      - kind: unit
        ref: "pio run -t clean -e {uno,uno328pb,leonardo} then pio run -e <env> -- uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014, all three logs 0 total warnings"
        status: pass
      - kind: unit
        ref: "rm -rf .pio/build/<env> + pio test -e <env> (540000ms timeout) then a second pio test -e <env> with no clean, for native/native_nodevtools/native_pinmap_provisional -- 141/141/10 cases, 17/17/1 suites, all PASSED in every run"
        status: pass
    human_judgment: false
  - id: D2
    description: "Live scripts/baseline/size_baseline.json rewritten to the post-landing tree: meta.warm_vs_cold_correction corrects BASE-01's false clean-build claim, meta.deltas_vs_base01 records the three signed AVR deltas with their MERGE-05 clause, native watermarks set to each env's COLD figure, third env present in both native_envs and warnings.native with the same key set, frozen BASE-01 blob SHA re-confirmed unchanged"
    requirement: "MERGE-05"
    verification:
      - kind: unit
        ref: "python3 -c \"import json;d=json.load(open('scripts/baseline/size_baseline.json'));print(sorted(d['native_envs']), sorted(d['warnings']['native']))\" -- both sorted lists equal ['native','native_nodevtools','native_pinmap_provisional']"
        status: pass
      - kind: unit
        ref: "git hash-object scripts/baseline/size_baseline_base01.json -- b940c91655600a57ad7ef67cba723943af929daf, unchanged before and after this plan's three commits"
        status: pass
      - kind: unit
        ref: "python3 scripts/check_build_warnings.py --log <env>=<cold log>, all three native envs -- PASS with '== watermark' text (not INFO) for native (1166), native_nodevtools (1166), native_pinmap_provisional (138)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every Phase-123 fixture/literal the re-baseline invalidated is repaired: 5 captured_* fixtures re-captured, 2 planted_* fixtures re-derived (flash_regression, avr_redef), 1 planted_* fixture's synthetic count raised above the new watermark (native_excess, 363->1206), test literals + provenance docstrings updated in both modules; the 3 MERGE-05 policy_* fixtures deliberately left untouched (frozen-baseline-only); full firmware suite unchanged in size (72 passed, 0 failed, same as Plan 124-09's recorded total) -- no test arm added or removed"
    requirement: "MERGE-05"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/ -q -- 72 passed, 0 failed"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/test_check_size_baseline.py tests/test_check_build_warnings.py -q -- 12 passed + 10 passed, both unchanged collected counts from Plan 124-02's recorded values"
        status: pass
      - kind: unit
        ref: "test_native_watermark_fires_on_planted_excess -- planted_build_warnings_native_excess.log's 1206 synthetic lines still exceed the new 1166 watermark; confirmed non-vacuous (1206 > 1166, margin 40)"
        status: pass
    human_judgment: false
  - id: D4
    description: "MERGE-05 and MERGE-06 both discharged as exit codes on the final tree: --policy merge05 vs the frozen BASE-01 exits 0 naming the exact RESEARCH-predicted deltas (leonardo -56, uno +22, uno328pb +28); the same three logs in default mode against the NEW live baseline also exit 0; --native-log for both pinned envs exits 0 at cases=141,suites=17; the golden-trace identity pin passes unchanged"
    requirement: "MERGE-06"
    verification:
      - kind: unit
        ref: "python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log leonardo=... --avr-log uno=... --avr-log uno328pb=... -- PASS: leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=]), uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]) -- exit 0"
        status: pass
      - kind: unit
        ref: "python3 scripts/check_size_baseline.py --avr-log ... (default mode, NEW live baseline) -- PASS, exit 0"
        status: pass
      - kind: unit
        ref: "python3 scripts/check_size_baseline.py --native-log native=... --native-log native_nodevtools=... -- PASS: native(cases=141,suites=17), native_nodevtools(cases=141,suites=17) -- exit 0"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/test_golden_trace_identity.py -q -- 6 passed, 0 failed"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 10: Post-Landing Re-Baseline + MERGE-05/MERGE-06 Discharge Summary

**Re-baselined `scripts/baseline/size_baseline.json` to the post-landing tree with both build states recorded (native watermarks set to the COLD figure -- 1166 for the two pinned envs, 138 for the new third env -- with BASE-01's own 360-was-warm falsehood corrected in place), repaired every fixture/literal the re-baseline invalidated, and discharged MERGE-05 (`--policy merge05` vs the frozen BASE-01: -56/+22/+28, exactly RESEARCH's predicted deltas) and MERGE-06 (`--native-log` both pinned envs: 141/17; golden traces: 6 passed) as exit codes on the final tree.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-07-31T10:2x:xxZ (approx, first AVR clean build)
- **Completed:** 2026-07-31T10:44:27Z (Task 3 commit)
- **Tasks:** 3 completed
- **Files modified:** 11 (5 re-captured fixtures, 2 re-derived planted fixtures, 1 rewritten JSON baseline, 2 test modules updated)

## Accomplishments

- **Task 1:** Measured the final tree (`2bd7187`, after Plans 124-01..09) with the build state pinned. Three AVR clean rebuilds (uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014, all 0 warnings) matched Plans 124-04/06/08/09's recorded landing figures byte-for-byte -- confirming zero drift across five intervening code-bearing plans. Cold+warm `pio test` for all three native envs, each via `rm -rf .pio/build/<env>` + one extended-timeout (540000ms) invocation then an immediate warm re-run: native/native_nodevtools cold=1166/warm=998 (matching Plan 124-04's recorded post-landing figures exactly); the new third env `native_pinmap_provisional` cold=138/warm=0 -- a different cold/warm ratio, recorded as a genuine finding (it compiles only 1 suite vs the pinned envs' 17, so its warm re-run's auto-regenerated Unity runner recompile happens not to touch any redefinition-prone shim file). Re-captured the five committed `captured_*` fixtures from these runs (three AVR build logs verbatim; the two native SUMMARY-tail captures preserving the existing truncation convention -- header + 17 suite rows + the N-cases footer, no compiler-diagnostic content, exactly as before).
- **Task 2:** Rewrote `scripts/baseline/size_baseline.json` in place as the Phase-124 recorded truth, keeping the same schema. `meta.warm_vs_cold_correction` states, with all labelled integers: BASE-01's recorded native watermark of 360 was a warm-cache figure; the identical pre-landing tree measures 456 cold; the landed tree measures native/native_nodevtools cold=1166/warm=998, native_pinmap_provisional cold=138/warm=0. `meta.deltas_vs_base01` records the three signed AVR flash deltas (leonardo -56, uno +22, uno328pb +28, RAM unchanged on all three) each labelled with the exact MERGE-05 clause it satisfies. `meta.supersedes` names the frozen `size_baseline_base01.json` and its blob SHA. `native_envs` and `warnings.native` both gained the third env with the identical key set (mechanically verified via a sorted-list comparison). Every native watermark was set to the COLD figure, per `check_build_warnings.py`'s below-watermark-is-INFO-not-FAIL asymmetry (a COLD watermark stays green on both a cold CI run and a warm local re-run; a WARM watermark would go red on the next cold CI run). The frozen BASE-01 file's blob SHA was re-confirmed unchanged before and after this task.
- **Task 3:** Repaired every fixture and literal the re-baseline invalidated. Re-derived `planted_size_baseline_flash_regression.log` from the new leonardo capture (26016 -> 26528, same +512 B offset) and updated both literals in its paired test. Re-derived `planted_build_warnings_avr_redef.log` from the new uno capture (same single PSTR-redefined insertion point). Re-derived `planted_build_warnings_native_excess.log`'s synthetic count from 363 to 1206 (1200 macro-shaped + 6 non-macro) so it still exceeds the new 1166 watermark by a real margin, and updated both literals in its paired test. Discovered and rewrote `test_policy_merge05_permits_the_measured_landing_deltas`: it previously synthesized RESEARCH's predicted post-landing deltas onto tmp_path copies of the (then still pre-landing) captured logs; since Task 1's re-capture means the committed captures now literally ARE the post-landing figures, the synthesis step became not just unnecessary but broken (the old-figure substring it rewrote FROM no longer exists in the file) -- removed the synthesis, the now-unused helper, and the now-unused `import re`. Updated both modules' provenance docstrings to record every re-derivation and note that pre-landing captures/fixtures are preserved in git history and in `size_baseline_base01.json`. Ran the full firmware suite (72 passed, 0 failed, unchanged total) and discharged both requirement-level exit codes on the final tree.

## Task Commits

Each task was committed atomically, inside the `firestarter` submodule (`/workspaces/firestarter`) on branch `v1.23-py32f071-integration`:

1. **Task 1: Measure the final tree with the build state pinned, cold and warm** - `b43ed22` (test)
2. **Task 2: Write the post-landing baseline, correcting the record rather than overwriting it** - `72a6844` (feat)
3. **Task 3: Repair every fixture and literal the re-baseline invalidated, then assert MERGE-05 and MERGE-06** - `a145081` (test)

_No plan-metadata commit is made inside the submodule -- the meta-repo's own SUMMARY.md commit (below) is this plan's final commit._

## Observed Verification Values

### Task 1 -- measurement

- AVR (clean builds, one env at a time), compared to Plans 124-04/06/08/09's recorded figures:

  | Env | Flash used | RAM used | Prior recorded | Match |
  |---|---|---|---|---|
  | uno | 23954/32256 | 1573/2048 | 23954/1573 | exact, 0 delta |
  | uno328pb | 24004/32384 | 1579/2048 | 24004/1579 | exact, 0 delta |
  | leonardo | 26016/28672 | 2014/2560 | 26016/2014 | exact, 0 delta |

  All three logs: 0 total warnings.

- Native (cold = `rm -rf .pio/build/<env>` then one `pio test -e <env>` invocation, 540000ms timeout; warm = an immediate second `pio test -e <env>` invocation, no clean):

  | Env | Cases | Suites | Cold total/macro-redef | Warm total/macro-redef |
  |---|---|---|---|---|
  | native | 141 | 17 | 1166/1166 | 998/998 |
  | native_nodevtools | 141 | 17 | 1166/1166 | 998/998 |
  | native_pinmap_provisional | 10 | 1 | 138/138 | 0/0 |

- `python3 scripts/check_size_baseline.py --avr-log uno=tests/fixtures/captured_build_uno.log --baseline scripts/baseline/size_baseline_base01.json` -- `FAIL: uno: flash_used baseline=23932 observed=23954` -- exit 1 (proving the re-captured fixture carries post-landing numbers).
- The same command with `--policy merge05` -- `PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=])` -- exit 0.

### Task 2 -- the rewritten baseline

- `python3 -c "import json;d=json.load(open('scripts/baseline/size_baseline.json'));print(sorted(d['native_envs']), sorted(d['warnings']['native']), d['warnings']['policy'])"` -> `['native', 'native_nodevtools', 'native_pinmap_provisional'] ['native', 'native_nodevtools', 'native_pinmap_provisional'] {'avr_rule': '== 0', 'native_rule': '<= total_watermark'}`.
- `git hash-object scripts/baseline/size_baseline_base01.json` -> `b940c91655600a57ad7ef67cba723943af929daf`, both before and after this task (frozen, unchanged).
- `python3 scripts/check_build_warnings.py --log <env>=<cold log>` for all three native envs: `PASS: native: total warnings=1166 (== watermark 1166)`, `PASS: native_nodevtools: total warnings=1166 (== watermark 1166)`, `PASS: native_pinmap_provisional: total warnings=138 (== watermark 138)` -- all exit 0, all `== watermark`, none `INFO`.
- `python3 scripts/check_build_warnings.py --log native=<warm log>` -- `INFO: native: total warnings observed=998 is 168 below watermark 1166 ... ; PASS: ...` -- exit 0, confirming the asymmetry works as designed (INFO, not FAIL, on the warm re-run).
- `python3 scripts/check_size_baseline.py` default mode, all three AVR logs, new live baseline -- `PASS: uno(flash=23954/32256,ram=1573/2048), uno328pb(flash=24004/32384,ram=1579/2048), leonardo(flash=26016/28672,ram=2014/2560)` -- exit 0.
- `python3 scripts/check_size_baseline.py --native-log native=... --native-log native_nodevtools=...` -- `PASS: native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)` -- exit 0.

### Task 3 -- fixture repair and requirement discharge

- `python3 -m pytest tests/ -q` -> **72 passed, 0 failed** (unchanged from Plan 124-09's recorded total -- no test arm added or removed).
- `python3 -m pytest tests/test_check_size_baseline.py tests/test_check_build_warnings.py -q` -> **12 passed + 10 passed**, both unchanged collected counts from Plan 124-02's recorded values.
- `planted_build_warnings_native_excess.log`: old synthetic count 363 (vs the old 360 watermark), new synthetic count **1206** (1200 macro-shaped + 6 non-macro, vs the new **1166** watermark) -- 1206 > 1166 confirmed, margin 40 lines; `test_native_watermark_fires_on_planted_excess` still fires, naming both `1206` and `1166`.
- **MERGE-05 (`--policy merge05` vs frozen BASE-01):** `PASS: leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=]), uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=])` -- exit 0. Deltas -56/+22/+28 match RESEARCH's measured -56/+22/+28 exactly.
- **MERGE-05 (default mode vs NEW live baseline):** `PASS: leonardo(flash=26016/28672,ram=2014/2560), uno(flash=23954/32256,ram=1573/2048), uno328pb(flash=24004/32384,ram=1579/2048)` -- exit 0.
- **MERGE-06 (`--native-log`, both pinned envs):** `PASS: native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)` -- exit 0.
- **MERGE-06 (golden traces):** `python3 -m pytest tests/test_golden_trace_identity.py -q` -> **6 passed, 0 failed**.
- `python3 scripts/check_build_warnings.py --log native_pinmap_provisional=<cold log>` -> `PASS: native_pinmap_provisional: total warnings=138 (== watermark 138)` -- exit 0, proving the third env is no longer a blind spot.
- `git status --porcelain` -> empty after each commit.
- `git hash-object scripts/baseline/size_baseline_base01.json` -> `b940c91655600a57ad7ef67cba723943af929daf`, unchanged at the end of the plan.
- `python3 scripts/check_cmake_manifest.py` and `python3 scripts/check_orphan_provisional.py` re-confirmed PASS (unregressed, sanity check beyond this plan's explicit scope).

## Files Created/Modified

- `firestarter/scripts/baseline/size_baseline.json` -- rewritten: post-landing figures, `warm_vs_cold_correction`, `deltas_vs_base01`, `supersedes`, three-env `native_envs`/`warnings.native`
- `firestarter/tests/fixtures/captured_build_uno.log` -- re-captured (clean build, post-landing)
- `firestarter/tests/fixtures/captured_build_uno328pb.log` -- re-captured
- `firestarter/tests/fixtures/captured_build_leonardo.log` -- re-captured
- `firestarter/tests/fixtures/captured_test_native_summary.log` -- re-captured (warm SUMMARY tail)
- `firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log` -- re-captured
- `firestarter/tests/fixtures/planted_size_baseline_flash_regression.log` -- re-derived (26016 -> 26528)
- `firestarter/tests/fixtures/planted_build_warnings_avr_redef.log` -- re-derived (same PSTR insertion, new base)
- `firestarter/tests/fixtures/planted_build_warnings_native_excess.log` -- re-derived (363 -> 1206 synthetic lines)
- `firestarter/tests/test_check_size_baseline.py` -- literals updated, `test_policy_merge05_permits_the_measured_landing_deltas` simplified to a direct measurement, provenance docstring updated, unused `_rewrite_flash_used`/`import re` removed
- `firestarter/tests/test_check_build_warnings.py` -- literals updated (363->1206, 360->1166), provenance docstring updated

## Decisions Made

See `key-decisions` in frontmatter for the full list. Highlights: the three MERGE-05 `policy_*` fixtures deliberately left untouched (frozen-baseline-only, never invalidated by the live re-baseline); `test_policy_merge05_permits_the_measured_landing_deltas` rewritten from a synthesized pre-landing prediction into a direct post-landing measurement, once the re-capture made the synthesis both unnecessary and broken; the native-excess fixture's new synthetic count (1206) chosen with a real margin over the new watermark, not a minimal one-line-over value; its header comment reworded to avoid self-tripping the coarse `warning:`-line count, the same class of issue Plan 124-09 documented for its own fixture.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1/3 - Bug/Blocking] `test_policy_merge05_permits_the_measured_landing_deltas` broke as a direct consequence of Task 1's re-capture**
- **Found during:** Task 3 (running the full suite after Task 1/2's changes)
- **Issue:** This test previously synthesized RESEARCH's predicted post-landing AVR figures by rewriting an old-baseline substring (e.g. `26072`) in a tmp_path copy of `captured_build_leonardo.log`. Once Task 1 re-captured that fixture from the real post-landing tree, the file already contains `26016`, so the old substring `26072` no longer exists anywhere in it -- the rewrite's `assert count == 1` would fail with `count == 0`.
- **Fix:** Removed the synthesis step entirely. The test now feeds the committed `captured_build_*.log` fixtures straight to `--policy merge05 --baseline size_baseline_base01.json`, since they already carry the exact figures the old test synthesized -- turning what was a pre-landing prediction into a direct post-landing measurement, which is strictly stronger evidence for the same assertion. Removed the now-dead `_rewrite_flash_used` helper and the `import re` it required.
- **Files modified:** `firestarter/tests/test_check_size_baseline.py`
- **Verification:** `python3 -m pytest tests/test_check_size_baseline.py -q` -- 12 passed (unchanged count), including this test.
- **Committed in:** `a145081` (Task 3 commit)

### Documented Findings (not defects)

**1. The native-excess fixture's original header comment inflated its own synthetic-line count by 4 via self-matching `warning:` substrings in comment prose.** Discovered while re-deriving the fixture at the new (higher) count: `grep -cE 'warning:'` initially returned 1210 instead of the intended 1206 because four header-comment lines happened to contain the literal `warning:` token in explanatory prose (the same class of issue Plan 124-09 documented for its own guard-header/CMakeLists.txt comments). Reworded the header to avoid the literal substring (no colon immediately after "warning" anywhere in the comment block); re-verified the count lands exactly on 1206. Not a functional defect -- caught and corrected before commit, no behavioral impact on the finished fixture.
- **Committed in:** `a145081` (Task 3 commit; corrected before commit, not a separate fix commit)

**2. The third native env's warm-vs-cold ratio is qualitatively different from the two pinned envs, not just numerically smaller.** `native`/`native_nodevtools` warm re-runs still show 998 warnings (down from 1166 cold, a partial drop); `native_pinmap_provisional`'s warm re-run shows 0 (down from 138 cold, a complete drop). This is a genuine measurement finding, not normalized or explained away: the third env compiles only 1 suite (vs 17), so its warm re-run's auto-regenerated Unity test-runner recompile apparently touches none of the redefinition-prone shim files the larger envs' warm re-runs still touch. Recorded honestly in `size_baseline.json`'s `meta.warm_vs_cold_correction` rather than assumed to match the other two envs' ratio.
- **No fix needed** -- both figures were used exactly as measured (cold=138 as the watermark, warm=0 recorded alongside for the record).

**3. Cosmetic: Task 3's commit message lost a backtick-quoted `` `import re` `` phrase to unintended shell command substitution** (the phrase was inside a double-quoted `-m` heredoc-free string containing literal backticks, which bash evaluated as `` `import re` `` -> attempted to run `import` as a command, printing `import: command not found` to stderr and substituting empty output). The commit itself succeeded with the correct file changes; only that one clause of prose in the commit body reads "helper +" instead of "helper + `import re`". Not re-committed (never amend per policy) -- noted here for the record since the commit message is otherwise complete and accurate.

---

**Total deviations:** 1 auto-fixed (Rule 1/3, a test broken by this plan's own Task 1 re-capture, fixed in the same commit that discovered it), 2 documented findings (a self-tripping-grep header wording issue caught before commit; a genuine cold/warm asymmetry difference on the third env), 1 cosmetic commit-message artifact (shell backtick substitution, no functional impact).
**Impact on plan:** None on scope or correctness. The one auto-fix was necessary for the test suite to pass and produced strictly stronger evidence (measurement over synthesis) for the same assertion. Both documented findings were caught and either corrected (header wording) or recorded honestly (the third env's ratio) rather than normalized away.

## Issues Encountered

None beyond the documented deviations above.

## User Setup Required

None -- no external service configuration required.

## Requirement Ticking Scope

Per this plan's dispatch `<requirement_ticking_scope>`, `.planning/REQUIREMENTS.md` was **not** touched. Evidence for Plan 124-12 to cite when it ticks MERGE-05/MERGE-06:

- **MERGE-05:** `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log leonardo=<log> --avr-log uno=<log> --avr-log uno328pb=<log>` exits 0 with deltas leonardo -56, uno +22, uno328pb +28 (all RAM unchanged) -- exactly RESEARCH's measured deltas. The same three logs in default mode against the newly re-baselined live default also exit 0.
- **MERGE-06:** `python3 scripts/check_size_baseline.py --native-log native=<log> --native-log native_nodevtools=<log>` exits 0 at `cases=141,suites=17` for both. `python3 -m pytest tests/test_golden_trace_identity.py -q` -- 6 passed, 0 failed.
- Both were run on the final tree (`2bd7187` compiled state, this plan's own three commits on top touch only baseline JSON, test fixtures, and test modules -- no firmware source).

## Next Phase Readiness

- The live `scripts/baseline/size_baseline.json` now matches the tree as it stands -- a bare run of either gate is correct without any flag, so Phase 125's VPP-03 (which expects a Phase-124 baseline to measure against) has one.
- The frozen `scripts/baseline/size_baseline_base01.json` (blob SHA `b940c91655600a57ad7ef67cba723943af929daf`) remains untouched and is MERGE-05's permanent judged reference.
- Full firmware suite: **72 passed, 0 failed** -- unchanged in size from Plan 124-09, every arm still discriminating.
- Both pinned native envs remain at exactly 141 cases / 17 suites; the third env (`native_pinmap_provisional`) is fully wired into both baseline blocks and no longer a blind spot for `check_build_warnings.py`.
- No blockers for Plan 124-11 or 124-12.

## Self-Check: PASSED

- FOUND: `firestarter/scripts/baseline/size_baseline.json` (modified)
- FOUND: `firestarter/tests/fixtures/captured_build_uno.log` (modified)
- FOUND: `firestarter/tests/fixtures/captured_build_uno328pb.log` (modified)
- FOUND: `firestarter/tests/fixtures/captured_build_leonardo.log` (modified)
- FOUND: `firestarter/tests/fixtures/captured_test_native_summary.log` (modified)
- FOUND: `firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log` (modified)
- FOUND: `firestarter/tests/fixtures/planted_size_baseline_flash_regression.log` (modified)
- FOUND: `firestarter/tests/fixtures/planted_build_warnings_avr_redef.log` (modified)
- FOUND: `firestarter/tests/fixtures/planted_build_warnings_native_excess.log` (modified)
- FOUND: `firestarter/tests/test_check_size_baseline.py` (modified)
- FOUND: `firestarter/tests/test_check_build_warnings.py` (modified)
- FOUND commit `b43ed22` (firestarter submodule)
- FOUND commit `72a6844` (firestarter submodule)
- FOUND commit `a145081` (firestarter submodule)

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
