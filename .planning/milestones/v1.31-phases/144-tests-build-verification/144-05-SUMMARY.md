---
phase: 144-tests-build-verification
plan: 05
subsystem: testing
tags: [pio, size-baseline, pytest, merge-05, gate, d-10, d-11, d-13, d-14, d-18, firmware]

# Dependency graph
requires:
  - phase: 138-preconditions-baseline
    provides: "The PREP-03 anchor (23954/24004/26016 flash; 1573/1579/2014 RAM) this plan measures its delta against, and size_baseline_v131.json's original native_trace_v131 record"
  - phase: 140-tests-build-verification
    provides: "eprom_params_for() finally linking (+204 B of this plan's measured flash growth) and the native_params_v131 env (9 cases) this plan's Task 1 runs by name"
  - phase: 141-per-byte-program-loop
    provides: "The per-byte pulse-to-verify loop and the native_loop_v131 env (39 cases pre-Phase-142) this plan's Task 1 runs by name"
  - phase: 142-high-voltage-routing
    provides: "eprom_hv_route_mask() and native_loop_v131's second suite (test_vpp_eprom_v131, 32 cases), bringing that env to 79"
  - phase: 143-host-timeout-progress-pulse-override
    provides: "143-HOST-RECORD.md section 7.1's own cold measurement (24824/24874/26906), independently reproduced by this plan's own Task 1 rebuild, and CAP-02/CAP-03's flash contribution"
provides:
  - "One cold consolidated measurement of the FINAL v1.31 tree: all three AVR targets plus all five native envs (native, native_nodevtools, native_params_v131, native_loop_v131, native_trace_v131), closing D-02's cross-phase-interaction gap"
  - "All three size baselines (size_baseline.json, size_baseline_base01.json, size_baseline_v131.json) re-anchored to the v1.31 tip, with size_baseline_v131.json gaining native_params_v131 and native_loop_v131 records it never held (C-01)"
  - "Seven re-derived fixtures (three re-captured, four re-derived plants) and two updated figure literals in test_check_size_baseline.py, each plant re-proven RED and GREEN at its new figures (D-18)"
  - "Verbatim pre- and post-rewrite verdicts for both check_size_baseline.py modes and check_build_warnings.py, with D-14's anchor-moved disclosure recorded in the file, the test docstring, and this SUMMARY"
affects: [144-06, 144-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Re-deriving a planted violation fixture from a moved anchor: preserve the single stated cause and its asserted delta magnitude (never the absolute figure), so the paired test's delta=+N assertion needs no edit even though the anchor under it moved"
    - "A baseline's own meta.supersedes/meta.deltas_vs_base01 fields carry the anti-overclaim disclosure in the data file itself, not only in prose elsewhere: a zero delta after a re-anchor states plainly that the anchor moved, not that growth stayed inside the old band"
    - "Cold warning counts for envs no checker script may ever be invoked against (D-22) are obtained by grep on the cold log directly, using the exact two regexes check_build_warnings.py uses, so the figure is real without ever risking the KeyError/false-regression failure mode"

key-files:
  created: []
  modified:
    - firestarter/scripts/baseline/size_baseline.json
    - firestarter/scripts/baseline/size_baseline_base01.json
    - firestarter/scripts/baseline/size_baseline_v131.json
    - firestarter/tests/fixtures/captured_build_uno.log
    - firestarter/tests/fixtures/captured_build_uno328pb.log
    - firestarter/tests/fixtures/captured_build_leonardo.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved.log
    - firestarter/tests/fixtures/planted_size_baseline_flash_regression.log
    - firestarter/tests/test_check_size_baseline.py

key-decisions:
  - "requirements-completed left empty in this SUMMARY, matching plan 144-01/144-04's precedent: this plan is explicitly FORBIDDEN from ticking TEST-01..05/07/08 -- plan 144-07 owns the consolidated eight-requirement flip. This plan supplies the evidence those flips will cite."
  - "The pre-rewrite --policy merge05 verdict is quoted verbatim against what scripts/baseline/size_baseline_base01.json actually held before this plan's rewrite (the v1.24 figures 23932/23976/26072, giving deltas +892/+898/+834) rather than the plan text's own +870/+890 mention, which describes the delta against the PREP-03 anchor (a different, already-reported comparison earlier in the same task). The measured, verbatim output is authoritative over a paraphrase; both are RED, which is what task 1's acceptance criteria require."
  - "size_baseline_base01.json's original Phase-123 meta (generated/phase/generated_by/tree_shas/note) was left untouched as the historical record of BASE-01's genesis; a new re_anchor_note field states plainly that avr_targets was overwritten in place and why, rather than editing history to look consistent with data it no longer describes."
  - "warnings.native's own note field (previously 'all four native watermarks') was updated to 'all six' when native_params_v131/native_loop_v131 were added to size_baseline_v131.json, so the file's internal self-description stays accurate rather than silently going stale."

patterns-established:
  - "A re-derived planted fixture is a NEW plant (D-18): its RED transcript was captured freshly against the real checker at its new figures before its GREEN (paired test + clean-capture identity leg) was trusted, for all four plants, not assumed transitively from the old fixture having once fired."

requirements-completed: []  # Intentional -- see key-decisions. This plan evidences TEST-01/02/03/04/05/07/08; plan 144-07 flips them.

coverage:
  - id: D1
    description: "One cold consolidated run measuring all three AVR targets (uno 24824/32256 flash, 1573/2048 RAM; uno328pb 24874/32384, 1579/2048; leonardo 26906/28672, 2014/2560 -- 93.8%, 1766 B headroom) and all five native envs (native 141/17, native_nodevtools 141/17, native_params_v131 9/1, native_loop_v131 79/2, native_trace_v131 5/1 all-passing) against the FINAL v1.31 tree in one session"
    requirement: "TEST-08"
    verification:
      - kind: other
        ref: "pio run -t clean -e {uno,uno328pb,leonardo} && pio run -e {uno,uno328pb,leonardo} -- /tmp/gsd-144/build_{uno,uno328pb,leonardo}.log"
        status: pass
      - kind: other
        ref: "rm -rf .pio/build/<env> && pio test -e {native,native_nodevtools,native_params_v131,native_loop_v131,native_trace_v131} -- /tmp/gsd-144/{native,native_nodevtools,native_params_v131,native_loop_v131,native_trace_v131}.log"
        status: pass
    human_judgment: false
  - id: D2
    description: "All three size baselines re-anchored to the v1.31 tip in one commit; size_baseline_v131.json gains native_params_v131 (9/9/1/true) and native_loop_v131 (79/79/2/true) records it never held; seven fixtures re-captured/re-derived; two figure literals updated in test_check_size_baseline.py; no checker script and no src/ file touched"
    requirement: "TEST-08"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py (12/12 passed)"
        status: pass
      - kind: unit
        ref: "firestarter/tests/ (full suite, 312 passed)"
        status: pass
      - kind: other
        ref: "git diff HEAD~1 --name-only (exactly 11 files) && git diff HEAD~1 --stat -- scripts/check_size_baseline.py scripts/check_build_warnings.py src/ (empty)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both TEST-08 gates read PASS post-rewrite at exact zero delta, disclosed as an anchor move (D-14) not growth-inside-band; all four re-derived plants proven RED with verbatim transcripts naming their unique cause, then GREEN via their paired tests"
    requirement: "TEST-08"
    verification:
      - kind: other
        ref: "python3 scripts/check_size_baseline.py --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... (PASS, zero delta)"
        status: pass
      - kind: other
        ref: "python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log ... (PASS, +0<=64/+0<=64/+0<=0)"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py#test_policy_merge05_fires_on_uno_class_over_band, #test_policy_merge05_fires_on_leonardo_growth, #test_policy_merge05_fires_on_ram_move, #test_planted_flash_regression_flips_checker_to_failure"
        status: pass
    human_judgment: false

# Metrics
duration: 30min
completed: 2026-08-14
status: complete
---

# Phase 144 Plan 05: Baseline Re-Anchor & Consolidated Cold Measurement Summary

**One cold consolidated run measured the FINAL v1.31 tree (+870/+870/+890 B flash, RAM unmoved), then re-anchored all three size baselines to that tip and re-derived the seven fixtures the re-anchor moved the ground under — retiring MERGE-05's standing RED as an explicit anchor move, not a band victory.**

## Performance

- **Duration:** ~30 min
- **Tasks:** 3 (1 measurement-only, 1 single mechanical commit, 1 verification-only)
- **Files modified:** 11 (one commit)

## Accomplishments

- Task 1: the phase's ONE cold consolidated run against the final tree (all three AVR targets, all five native envs), with verbatim pre-rewrite verdicts for every gate.
- Task 2: all three baselines re-anchored to the v1.31 tip in a single mechanical commit, with seven fixtures re-derived and two test literals updated as collateral.
- Task 3: post-rewrite verdicts (both TEST-08 gates PASS at exact zero delta) and all four re-derived plants proven RED then GREEN.

## Task Commits

1. **Task 1: The ONE cold consolidated run, and the pre-rewrite gate verdicts** — no commit (measurement-only; `git status --porcelain` confirmed empty at task end, as required)
2. **Task 2: Re-anchor all three baselines, re-capture and re-derive the seven fixtures, update the two literals — one commit** — `a594173` (test) in `firestarter`
3. **Task 3: Post-rewrite gate verdicts and the four re-derived plants' RED/GREEN pairs** — no commit (verification-only, appends to scratch `/tmp/gsd-144/verdicts.txt` only)

**Plan metadata:** this SUMMARY's own commit, in the superproject.

## Cold Consolidated Measurement (Task 1)

### Flash/RAM, all three AVR targets, cold (`pio run -t clean -e <env>` then `pio run -e <env>`)

| Target | Flash used/total | RAM used/total | Delta vs PREP-03 anchor (23954/24004/26016) |
|---|---|---|---|
| `uno` | 24824 / 32256 | 1573 / 2048 | **+870 B flash, +0 RAM** |
| `uno328pb` | 24874 / 32384 | 1579 / 2048 | **+870 B flash, +0 RAM** |
| `leonardo` | 26906 / 28672 | 2014 / 2560 | **+890 B flash, +0 RAM** |

**Leonardo ceiling, computed from the measured figures:** 26906 / 28672 = **93.8%**, leaving **1766 B** headroom (28672 − 26906). Watched explicitly, as TEST-08 requires, not discovered.

**Attribution of the +870/+870/+890 B growth** (against the Phase-138 PREP-03 anchor): the parameter table finally linking, `eprom_params_for()` gaining its first `src/` caller (Phase 140, ~+204 B); the per-byte pulse-to-verify loop rewrite (Phase 141); the shared `eprom_hv_route_mask()` HV-route resolver (Phase 142); and the host-facing `CAP-02`/`CAP-03` identity+budget ack plus the guarded `MSG_DATA_PROGRESS` emission (Phase 143). These figures are byte-identical to `143-HOST-RECORD.md` section 7.1's own cold measurement (24824/24874/26906; 1573/1579/2014) — expected, since Phase 144's own prior plans (144-01, 144-03, 144-04) are test-only and touch no `src/` file, confirming this plan's own independent rebuild rather than merely copying that record forward.

### Native envs, cold (`rm -rf .pio/build/<env>` then `pio test -e <env>`)

| Env | Cases | Suites | All passed | Labelled |
|---|---|---|---|---|
| `native` | 141 | 17 | true | pinned, CI-covered |
| `native_nodevtools` | 141 | 17 | true | pinned, CI-covered |
| `native_params_v131` | 9 | 1 | true | run-by-name only, **no CI leg** |
| `native_loop_v131` | 79 | 2 | true | `test_loop_eprom_v131` (47) + `test_vpp_eprom_v131` (32) = 79 per-env; run-by-name only, **no CI leg** |
| `native_trace_v131` | 5 | 1 | true, 0 failed | run-by-name only, **no CI leg**; retired from RED by plan 144-03's re-freeze |

88 is the three-suite mapping denominator (144-01); 79 is `native_loop_v131`'s own per-env figure. These are never added together — each is labelled with the env/suite that produced it.

**The three `*_v131` envs run in NO CI leg of either repository** — a restated absence, not an implied coverage claim. No invocation in this plan ever passed one of their names to either checker script.

### Cold warning counts, the three `*_v131` envs (grep, never via either checker — D-22)

| Env | `macro_redefinition` | `total` | Note |
|---|---|---|---|
| `native_params_v131` | 140 | 140 | new figure, now recorded in `size_baseline_v131.json` for the first time (C-01) |
| `native_loop_v131` | 154 | 154 | new figure, now recorded for the first time (C-01); higher than the other two because it compiles two suites |
| `native_trace_v131` | 140 | 140 | **unmoved** from the existing record — plan 144-03's fixture re-freeze did not change the compiled-warning surface |

No gap: all three counts were obtained cleanly by grepping the cold logs with the exact two regexes `check_build_warnings.py` uses.

### Pre-rewrite verdicts, verbatim

```
=== PRE-REWRITE: strict identity, default baseline (size_baseline.json) ===
FAIL:
  uno: flash_used baseline=23954 observed=24824
  uno328pb: flash_used baseline=24004 observed=24874
  leonardo: flash_used baseline=26016 observed=26906
exit=1

=== PRE-REWRITE: --policy merge05, --baseline size_baseline_base01.json ===
FAIL:
  uno: flash_used baseline=23932 observed=24824 delta=+892 exceeds MERGE-05 uno-class band of 64 B
  uno328pb: flash_used baseline=23976 observed=24874 delta=+898 exceeds MERGE-05 uno-class band of 64 B
  leonardo: flash_used baseline=26072 observed=26906 delta=+834 exceeds MERGE-05 leonardo band of 0 B
exit=1

=== PRE-REWRITE: native compare, default baseline (size_baseline.json) ===
PASS: native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)
exit=0

=== PRE-REWRITE: check_build_warnings.py, five permitted envs ===
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0), native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166 (== watermark 1166)
exit=0
```

Note on the band-policy verdict: this is quoted exactly as the checker produced it, against what `size_baseline_base01.json` actually held before this plan's rewrite (the v1.24 figures 23932/23976/26072, i.e. deltas +892/+898/+834) — see Decisions for why this differs from a +870/+890 figure mentioned elsewhere in the plan text (that figure describes the delta against the PREP-03 anchor, a different, already-reported comparison). Both pre-rewrite gates are RED, each naming its deltas, as required.

## Re-Anchor (Task 2, one commit `a594173`)

All three baselines rewritten to the v1.31 tip in a single mechanical commit:

- **`size_baseline.json` (D-10)** — the live default baseline. `avr_targets` now 24824/24874/26906 flash, 1573/1579/2014 RAM (unchanged). `native_envs` and the entire `warnings` block preserved byte-identical (verified: `warnings` dict equality check passed). `meta.deltas_vs_base01` recomputed to all-zero, each `merge05_clause` now stating the anchor-moved disclosure. `meta.supersedes` corrected: no longer claims BASE-01 is immutable.
- **`size_baseline_base01.json` (D-11, D-12)** — `avr_targets` overwritten to the same tip figures; `native_envs`/`warnings` preserved verbatim (the 360 watermark is v1.23-era, not this phase's to move). A new `re_anchor_note` meta field records the retirement of v1.24 semantics while the forward MECHANISM (band literals, `--policy merge05` invocation shape) stays untouched. No v1.24 content preserved in-tree — git history is the record (blob `b940c91655600a57ad7ef67cba723943af929daf`).
- **`size_baseline_v131.json` (D-13 + C-01)** — `avr_targets` rewritten to the tip; `native_trace_v131` updated to its now-genuinely-all-passing `5/5/1/true`; **two new env records added that this file never held**: `native_params_v131` (9/9/1/true) and `native_loop_v131` (79/79/2/true), with matching `warnings.native` entries (140/140, 154/154). A `c01_policy_change` meta field records that `141-NEW-TRACE.md` section 6 held these counts in prose only ("never in a baseline JSON") until this plan.

**Fixtures re-captured** (`tests/fixtures/captured_build_{uno,uno328pb,leonardo}.log`): each replaced with the real cold `pio run` output for its env (the post-clean build block only, matching every sibling captured fixture's established shape — the preceding `pio run -t clean` block is not part of the committed capture).

**Four plants re-derived** (D-18, each preserving its single cause and asserted delta):

| Fixture | Old cause (pre-re-anchor) | New cause (this plan) | Delta preserved |
|---|---|---|---|
| `planted_size_baseline_policy_uno_over_band.log` | 23932 → 23997 | 24824 → 24889 | `delta=+65` |
| `planted_size_baseline_policy_leonardo_growth.log` | 26072 → 26073 | 26906 → 26907 | `delta=+1` |
| `planted_size_baseline_policy_ram_moved.log` | 1573 → 1574 (flash 23932) | 1573 → 1574 (flash 24824, zero delta) | `+1 B RAM` |
| `planted_size_baseline_flash_regression.log` | 26016 → 26528 | 26906 → 27418 | `+512 B` |

Two figure literals updated in `test_check_size_baseline.py`'s flash-regression leg (26016→26906, 26528→27418); `delta=+65`/`delta=+1` assertions left untouched, as required. Every docstring naming a moved number was updated (module docstring's coverage items 3 and 8, the derivation section, and the two affected function docstrings).

**Verification:** `git diff HEAD~1 --name-only` lists exactly the 11 declared paths; `git diff HEAD~1 --stat` against the two checker scripts and `src/` is empty. `python3 -m pytest tests/ -q` → **312 passed** (run only after the commit, per D-20/F-09).

## Post-Rewrite Verdicts & The Four Plants (Task 3)

```
=== POST-REWRITE: strict identity, default baseline (size_baseline.json) ===
PASS: uno(flash=24824/32256,ram=1573/2048), uno328pb(flash=24874/32384,ram=1579/2048), leonardo(flash=26906/28672,ram=2014/2560)
exit=0

=== POST-REWRITE: --policy merge05, --baseline size_baseline_base01.json ===
PASS: uno(flash=24824/32256[+0<=64],ram=1573/2048[=]), uno328pb(flash=24874/32384[+0<=64],ram=1579/2048[=]), leonardo(flash=26906/28672[+0<=0],ram=2014/2560[=])
exit=0

=== POST-REWRITE: native compare, default baseline ===
PASS: native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)
exit=0

=== POST-REWRITE: check_build_warnings.py, five permitted envs ===
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0), native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166 (== watermark 1166)
exit=0
```

**MERGE-05 reads green because its anchor moved to v1.31, not because growth stayed inside v1.24's band.** The band-policy verdict's own `[+0<=64]`/`[+0<=0]` annotations make this literal: every delta is exactly zero. This pairs with **F-141-01**'s operator acceptance of the overrun (recorded at Phase 141 close, never remediated) and the **+204 B** parameter-table mechanism (Phase 140's `eprom_params_for()` gaining its first caller) as the substantive reason growth happened in the first place — the anchor move is the bookkeeping event, not the cause.

### The four re-derived plants — RED, verbatim

```
=== PLANT 1 RED: policy_uno_over_band (expect delta=+65, band of 64) ===
FAIL:
  uno: flash_used baseline=24824 observed=24889 delta=+65 exceeds MERGE-05 uno-class band of 64 B
exit=1

=== PLANT 2 RED: policy_leonardo_growth (expect delta=+1, leonardo) ===
FAIL:
  leonardo: flash_used baseline=26906 observed=26907 delta=+1 exceeds MERGE-05 leonardo band of 0 B
exit=1

=== PLANT 3 RED: policy_ram_moved (expect ram_used 1574 vs 1573) ===
FAIL:
  uno: ram_used baseline=1573 observed=1574 delta=+1 (MERGE-05 requires ram_used unchanged)
exit=1

=== PLANT 4 RED: flash_regression (expect 26906 and 27418) ===
FAIL:
  leonardo: flash_used baseline=26906 observed=27418
exit=1
```

Every plant fires, each naming its own unique cause. **GREEN half:** `python3 -m pytest tests/test_check_size_baseline.py -v` → **12/12 passed**, including the four paired tests (`test_policy_merge05_fires_on_uno_class_over_band`, `test_policy_merge05_fires_on_leonardo_growth`, `test_policy_merge05_fires_on_ram_move`, `test_planted_flash_regression_flips_checker_to_failure`) and the clean-capture identity leg (`test_clean_avr_all_three_envs_pass`) — proving each RED is attributable to its own plant, not to the fixture set as a whole. `python3 -m pytest tests/test_check_size_baseline.py tests/test_check_build_warnings.py -q` → **22 passed**. `/tmp/gsd-144/verdicts.txt` contains zero occurrences of `Traceback` and no invocation naming a `*_v131` env.

**The one leg that changes character rather than breaking:** `test_policy_merge05_permits_the_measured_landing_deltas` now asserts **zero-delta identity**, not "growth stayed inside the band" — its docstring says so explicitly (a Phase 144 sentence appended in the same register as the Plan 124-10 precedent it already carried). Stated plainly here rather than silently: a hollowed-out-looking leg that still passes is worse than a RED one if the reason it passes goes unrecorded.

## Standing Non-Claims (restated, not eroded)

- **No bench run happened.** Nothing in this plan is a claim about real silicon — Phase 145 owns that.
- **TEST-04's "disables every high-voltage route"** remains proven only in the emitted control-register stream, never behaviourally — this plan's measurement work does not change that boundary.
- **The three `*_v131` envs (`native_params_v131`, `native_loop_v131`, `native_trace_v131`) are covered by no CI leg in either repository.** Their counts, now recorded in `size_baseline_v131.json` for the first time, remain a local run-by-name obligation, never an implied CI claim.

## Decisions Made

See frontmatter `key-decisions`. In brief: the pre-rewrite band-policy verdict is quoted exactly as measured (against BASE-01's actual pre-rewrite v1.24 content) rather than a +870/+890 paraphrase found elsewhere in the plan text describing a different comparison; BASE-01's historical Phase-123 meta fields were left untouched with a new field added alongside them rather than edited to look retroactively consistent; and `size_baseline_v131.json`'s own internal `warnings.note` was corrected from "four" to "six" watermarks now that two more are recorded there.

## Deviations from Plan

None — plan executed exactly as written. The only interpretive judgment made (quoting the actual measured pre-rewrite band-policy deltas rather than a figure mentioned in the plan's own prose that described a different comparison) is documented above as a Decision, not a deviation: the underlying commands, figures, and acceptance criteria all matched the plan's literal requirements.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All evidence TEST-01 through TEST-05, TEST-07, and TEST-08 need is now recorded: the consolidated cold run, the re-anchored baselines, the re-derived fixtures, and the verbatim gate verdicts (including D-14's anchor-moved disclosure). Plan 144-07 can proceed to the eight-requirement flip.
- `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` coverage tables were NOT edited by this plan, per its explicit scope boundary.
- No blockers. `firestarter` is clean, on `gsd/v1.31-27c-programming-algorithm-fidelity`, one commit ahead (`a594173`) of where this plan started.

## Self-Check: PASSED

All 11 modified `firestarter` paths confirmed present on disk. Commit `a594173` confirmed in `git log`. This SUMMARY confirmed written before commit.

---
*Phase: 144-tests-build-verification*
*Completed: 2026-08-14*
