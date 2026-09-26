---
phase: 140-parameter-table
plan: 07
subsystem: firmware
tags: [eprom, parameter-table, phase-close, cold-build, requirements-tracking, baseline-verification, platformio]

# Dependency graph
requires:
  - phase: 140-01
    provides: "eprom_params_t table + eprom_params_for() accessor + 140-PREDICTIONS.md (P1-P5, committed before any measurement)"
  - phase: 140-02
    provides: "TABLE-05 firmware-half gate (protocol_branch_inventory), 3 planted RED runs"
  - phase: 140-03
    provides: "TABLE-05 database-half gate (chip_database_field_inventory), 4 planted RED runs"
  - phase: 140-04
    provides: "native_params_v131 env + 9-case suite proving the pulse_delay==0 fallback and row resolution"
  - phase: 140-05
    provides: "18-cell citation sidecar (eprom_params_citations.json) + 10-test coverage gate, 5 planted RED runs"
  - phase: 140-06
    provides: "doc/PROTOCOLS.md + CLAUDE.md reconciled against the shipped citations"
provides:
  - "140-PARAM-TABLE-RECORD.md: the Phase 140 close record -- 11 sections, both named divergences, prediction-vs-measurement reconciliation, 12-planted-RED gate evidence index, findings register (new F-140-09/F-140-10), hand-offs"
  - "Cold, post-140-PREDICTIONS.md measurement of all 3 AVR + 4 native envs, both check_size_baseline.py runs, both check_build_warnings.py runs, both repos' full pytest suites -- every reconcilable prediction matched exactly"
  - "TABLE-01 through TABLE-05 marked Complete in REQUIREMENTS.md and ROADMAP.md, exactly once, with the rest of both documents provably untouched"
affects: [141-per-byte-program-loop, 142-high-voltage-routing, 144-tests-and-build-verification, 146-close-honesty-ledger]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Snapshot-and-diff discipline for requirement/roadmap bookkeeping edits: cp both files before editing, diff after, assert the change set is exactly the enumerated lines"
    - "Surgical Edit-tool replacement in preference to a write-path that reformats an entire markdown file as a side effect, when the task's own acceptance criteria bound the diff to specific lines"

key-files:
  created:
    - .planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "Used the Edit tool (exact string replacement) instead of the requirements.mark-complete / roadmap.update-plan-progress SDK verbs for Task 3's edits -- both verbs write through a shared platformWriteSync -> _normalizeMd pass that reformats blank-line spacing across the ENTIRE target markdown file on every write, which would have violated Task 3's explicit, enumerated 'nothing else may move' scope"
  - "requirements.mark-complete was still invoked afterward, in the standard state_updates step, as a safe no-op verification: since all 5 requirements were already Complete from the manual edit, its own 'if (updated.length > 0)' guard skips the file write entirely -- confirmed zero diff"
  - "roadmap.update-plan-progress was deliberately NOT invoked at all this plan (neither in Task 3 nor in state_updates) -- ROADMAP.md is large enough that its unconditional whole-file write would reformat blank-line spacing across many unrelated, already-shipped milestones, which the same T-140-30 threat-model concern (an edit clobbering unrelated content) that motivated the snapshot-and-diff requirement in the first place argues against; the plan's own required end-state (Phase 140 checklist [x] + date suffix, Coverage table rows Complete) was already achieved by the manual edit"
  - "P5 (native_params_v131's invisibility to both live gates) was recorded as NOT independently re-triggered this session, rather than silently marked a match -- the plan's own critical hazard #2 forbids invoking either check script with that env name, so re-observing the KeyError/exit-2 behavior would require violating the plan to prove a point F-138-05 (Phase 138) already established"
  - "Minted two new finding IDs in the phase record, both explicitly required by Task 2's own action text: F-140-09 (doc/PROTOCOLS.md contradicted the datasheets it cited, corrected in plan 140-06) and F-140-10 (140-RESEARCH.md's Pitfall 5 undercounted the branch-predicate population at 3 sites; the real, gate-derived count is 21 tier-2 sites)"

patterns-established:
  - "Any future plan whose acceptance criteria bound a markdown-file diff to specific enumerated lines should use direct Edit-tool string replacement rather than a requirements.mark-complete / roadmap.update-plan-progress style SDK verb, because platformWriteSync's _normalizeMd pass reformats blank-line spacing across the whole file on every write, unconditionally, regardless of how small the intended semantic change is"

requirements-completed: [TABLE-01, TABLE-02, TABLE-03, TABLE-04, TABLE-05]

coverage:
  - id: D1
    description: "TABLE-01: const protocol_id-keyed table carries rows for 0x07/0x08/0x0B with all five named columns, each protocol resolving to its own distinct row"
    requirement: "TABLE-01"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp#test_each_protocol_resolves_to_its_own_distinct_row (native_params_v131 case 7), #test_row_values_match_the_frozen_table (case 9)"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_struct_field_names_are_exactly_the_frozen_six_in_order, ::test_rows_are_exactly_the_three_27c_protocols"
        status: pass
    human_judgment: false
  - id: D2
    description: "TABLE-02: no pulse-width column anywhere in the table; write path still reads handle->pulse_delay (frozen trace unmoved)"
    requirement: "TABLE-02"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_no_pulse_width_column_exists"
        status: pass
      - kind: other
        ref: "cd firestarter && rm -rf .pio/build/native_trace_v131 && pio test -e native_trace_v131 -> 5 test cases: 5 succeeded (this plan's own cold re-run, D-10 frozen fixture unmoved)"
        status: pass
    human_judgment: false
  - id: D3
    description: "TABLE-03: the pulse_delay==0 fallback is exercised by a running test (1000/100/500us per protocol) with paired non-vacuity negative controls; no bench oracle exists for this branch (F-140-04, stated not implied)"
    requirement: "TABLE-03"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp cases 1-6 (3 positive fallback cases + 3 paired negative controls), re-run cold this plan: 9 test cases: 9 succeeded"
        status: pass
    human_judgment: false
  - id: D4
    description: "TABLE-04: every one of the 18 cells cites a named primary datasheet or the exact 'no datasheet basis -- reasoned from X' form; bijection + drift + well-formedness gate; 5 planted RED runs preceded its GREEN"
    requirement: "TABLE-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py (10 tests) -- re-run cold this plan as part of the full firmware suite (244 passed)"
        status: pass
      - kind: other
        ref: "5 planted-violation RED transcripts in 140-05-SUMMARY.md (missing cell, extra cell, blanked D-09 scope, drifted value, injected pulse-width column), each named for the right reason"
        status: pass
    human_judgment: false
  - id: D5
    description: "TABLE-05: no new chip_database.json field (DB-half gate) and no second firmware algorithm selector (firmware-half gate); protocol_id remains the sole dispatch key; 3+4 planted RED runs preceded the two gates' GREEN"
    requirement: "TABLE-05"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_protocol_branch_inventory.py (7 tests) + firestarter_app/tests/test_chip_database_field_inventory.py (8 tests) -- both re-run cold this plan (244 firmware / 1547 app, both green)"
        status: pass
      - kind: other
        ref: "3 planted-violation RED transcripts (140-02-SUMMARY.md) + 4 planted-violation RED transcripts (140-03-SUMMARY.md) = 7 of the phase's 12 total, each named for the right reason"
        status: pass
    human_judgment: false
  - id: D6
    description: "Phase-close record: cold post-prediction measurement of all 3 AVR + 4 native envs, both baseline gate scripts, both repos' full suites -- every reconcilable prediction (P1-P4) matched exactly; both named divergences (0x07 Intel-family split candidate, 0x08 PROJECT.md contradiction) recorded in 140-PARAM-TABLE-RECORD.md; TABLE-01..05 marked complete exactly once with the surrounding roadmap provably untouched"
    verification:
      - kind: other
        ref: ".planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md (11 numbered sections, 280 lines); this SUMMARY's own Gate Transcripts and Prediction-vs-Measurement sections below"
        status: pass
    human_judgment: false

duration: ~32min
completed: 2026-08-10
status: complete
---

# Phase 140 Plan 07: Close Record, Cold Reconciliation & Requirement Flips Summary

**Cold post-prediction measurement of all 3 AVR + 4 native envs plus both repos' full suites reconciled every one of 140-PREDICTIONS.md's testable claims exactly (0-byte AVR flash/RAM delta, 1166 native warnings, 141/17 pinned suites, 5/1 and 9/1 on the two non-CI envs); the Phase 140 close record names both divergences (the 0x07 Intel-family split candidate and the 0x08 PROJECT.md self-contradiction) without smoothing either, and TABLE-01 through TABLE-05 are now marked Complete exactly once.**

## Performance

- **Duration:** ~32 min
- **Started:** ~2026-08-10T02:43:00Z (approximate; continued directly from the 140-06 session, whose completion STATE.md recorded at `2026-08-10T02:43:01.407Z`)
- **Completed:** 2026-08-10T03:15:00Z (approximate)
- **Tasks:** 3 (Task 1 was measurement-only -- see Task Commits)
- **Files modified:** 3 (1 new: `140-PARAM-TABLE-RECORD.md`; 2 modified: `REQUIREMENTS.md`, `ROADMAP.md`)

## Accomplishments

- **Cold capture, Task 1** -- for each of `uno`/`uno328pb`/`leonardo`/`native`/`native_nodevtools`/`native_trace_v131`/`native_params_v131`: `rm -rf .pio/build/<env>` then a single uninterrupted invocation. Every AVR target came back byte-identical to `size_baseline_v131.json` (0 delta, flash and RAM, on all three); every native env's case/suite count matched its pin exactly. See "Gate Transcripts" and "Prediction vs. Measurement" below for full verbatim output.
- **Both baseline gate scripts, cold, verbatim PASS on both invocations** -- `check_size_baseline.py` default seam (exit 0) and `--policy merge05 --baseline size_baseline_base01.json` (exit 0, RAM delta `[=]` on all three AVR targets); `check_build_warnings.py` on the two pinned native envs (1166/1166) and on the three AVR envs (`macro_redefinition=0` each).
- **Both repositories' full suites green, cold** -- firmware `pytest tests/ -q` -> 244 passed (227 baseline + 7 from 140-02 + 10 from 140-05); app `pytest tests/ -o addopts="" -q` -> 1547 passed (1539 baseline + 8 from 140-03).
- **`140-PARAM-TABLE-RECORD.md` (Task 2)** -- 280 lines, 11 numbered sections exactly as the plan specifies: what shipped, the row grid (pointing at, not restating, `eprom_params_citations.json`), Named Divergence 1 (`0x07`'s Intel-family split candidate, F-140-05), the Named Contradiction (`0x08`, D-06), the inert `overprogram_cap_us` column, prediction-vs-measurement (quoting P1-P5, naming `140-PREDICTIONS.md`'s commit SHA `a2705cfb02d848ab1d927da0b784f959300cc4ab`, explaining the ~0 AVR flash delta mechanically via `-Wl,--gc-sections`/F-140-02), the suite/env count table with the explicit no-CI-leg statement (F-140-11), the 12-planted-RED gate evidence index, what this phase does not verify (four items, including "no bench oracle exists for TABLE-03"), a findings register (new F-140-09 and F-140-10, inherited F-138-05), and Phase 141/142/144/146 hand-offs.
- **TABLE-01 through TABLE-05 marked Complete exactly once (Task 3)** -- five checkbox flips and five traceability-row flips in `REQUIREMENTS.md`, five traceability-row flips plus one dated checklist-checkbox flip in `ROADMAP.md`. Snapshot-and-diff verified: the combined diff touches exactly the 16 enumerated lines, nothing else -- confirmed by full-diff review, not merely by the plan's own (repo-convention-mismatched) `**Plans:**` grep probe (see Deviations).
- `src/proms/eprom.cpp` confirmed byte-unchanged across the whole phase: `git -C firestarter diff --quiet -- src/proms/eprom.cpp` exits 0 (re-checked this plan); `native_trace_v131` (D-10's frozen pre-change fixture) still 5/5 PASSED, cold, this session.
- `.planning/PROJECT.md` confirmed byte-unchanged (`git diff --quiet` exits 0); both submodules' `git status --porcelain` confirmed empty/pre-existing-only -- no commit landed in either submodule from this plan.

## Task Commits

1. **Task 1: Cold AVR + native capture, both gate scripts, both suites** -- no commit (measurement-only; produces no tracked file change of its own -- see Issues Encountered). Evidence captured verbatim in this SUMMARY and folded into Task 2's record.
2. **Task 2: Write `140-PARAM-TABLE-RECORD.md`** -- `c78cbb77` (docs, meta repo)
3. **Task 3: Mark TABLE-01..05 complete** -- `bf52f47b` (docs, meta repo)

**Plan metadata:** this SUMMARY's own commit (docs: complete plan) -- see final commit below.

## Files Created/Modified

- `.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md` (new, 280 lines) -- the Phase 140 close record.
- `.planning/REQUIREMENTS.md` (10 lines changed) -- TABLE-01..05 checkboxes (`### Parameter Table`) and traceability-table rows flipped to Complete.
- `.planning/ROADMAP.md` (6 lines changed) -- TABLE-01..05 traceability-table rows flipped to Complete; Phase 140 checklist entry flipped to `[x]` with `(completed 2026-08-10)`.
- `firestarter/`, `firestarter_app/` -- **read-only this plan.** `git status --porcelain` empty (firestarter) / pre-existing-untracked-only (firestarter_app) at every checkpoint. No commit landed in either submodule.

## Decisions Made

See frontmatter `key-decisions` for full rationale. Summary:
- Used the Edit tool for Task 3's REQUIREMENTS.md/ROADMAP.md changes instead of the `requirements.mark-complete`/`roadmap.update-plan-progress` SDK verbs, because both route through `platformWriteSync` -> `_normalizeMd`, which reformats blank-line spacing across the **entire** target markdown file on every write -- directly incompatible with Task 3's explicit, enumerated "nothing else may move" scope. Discovered by running `requirements.mark-complete` once, observing a ~40-line spurious diff scattered across unrelated sections of `REQUIREMENTS.md`, reverting from the pre-edit snapshot, and redoing the edit surgically.
- Still invoked `requirements.mark-complete` afterward (state_updates step) as a verification-only, zero-write no-op (all 5 already Complete).
- Did **not** invoke `roadmap.update-plan-progress` at all this plan -- the same whole-file-reformat risk applies to `ROADMAP.md`, which is far larger and spans many already-shipped milestones; the plan's own required end state was already achieved manually.
- Recorded P5 as **not independently re-triggered** this session (the plan's critical hazard #2 forbids invoking either check script with `native_params_v131`), rather than silently presenting it as a confirmed match.
- Minted F-140-09 and F-140-10 in the phase record, both named explicitly in Task 2's own action text.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Avoided the SDK write-path's whole-file markdown reformat side effect**
- **Found during:** Task 3, immediately after the first `requirements.mark-complete` invocation
- **Issue:** `requirements.mark-complete TABLE-01 TABLE-02 TABLE-03 TABLE-04 TABLE-05` correctly flipped the 5 intended checkboxes and table rows, but the underlying `platformWriteSync` write path applies `_normalizeMd` (`shell-command-projection.cjs`) to the **entire** file content on every `.md` write -- inserting a blank line before/after list items throughout the whole document. The resulting diff touched ~40 unrelated lines scattered across `PREP-*`, other bullets, and general prose -- directly violating this task's own explicit acceptance criterion that "the combined diff of the two files touches only the changed checkbox/status lines and the Phase 140 checklist line."
- **Fix:** Reverted `REQUIREMENTS.md` to its pre-edit snapshot (`cp` restore) and re-applied the identical 5+5 flips via the Edit tool (exact string replacement, no markdown normalization pass). Applied the same surgical approach to `ROADMAP.md` from the start, and skipped `roadmap.update-plan-progress` entirely for the same reason.
- **Files modified:** `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`
- **Verification:** Snapshot-diff after the surgical edit shows exactly 10 changed lines in `REQUIREMENTS.md` and exactly 6 in `ROADMAP.md` (16 total), matching Task 3's own enumerated change set precisely; `git diff | grep -Ec '^[-+]'` = 36 (16 replaced lines x 2 + 4 diff-header lines across 2 files), confirmed against the plan's own verify block.
- **Committed in:** `bf52f47b` (the corrected edit was what actually landed; the reverted, over-broad version was never committed)

---

**Total deviations:** 1 auto-fixed (1 bug -- an SDK-tool side effect, not a plan defect)
**Impact on plan:** No content change to any requirement, decision, or unrelated phase's line. Zero scope creep -- the fix is strictly a *mechanism* substitution (Edit tool vs. SDK verb) that produces the identical intended end state without the collateral formatting churn.

## Issues Encountered

**Task 1 produced no additional file changes, and therefore no additional commit** -- mirroring the identical, already-established pattern in 140-01/140-04/140-05/140-06's own Task 3 precedents. Task 1's `<files>` tag names `140-PARAM-TABLE-RECORD.md`, but Task 1's own `<action>` text is a pure cold-measurement-and-recording exercise; the plan's own instruction is to "record every command line and its verbatim output in a scratch note for Task 2 to fold into the record" -- a scratch note, not a committed artifact. Named here per this project's "name the divergence" convention.

**P5 (native_params_v131's invisibility to both live gates) was not independently re-triggered this session** -- disclosed above under Decisions Made and in `140-PARAM-TABLE-RECORD.md` §6, rather than silently presented as a re-confirmed match. This is a deliberate non-test, not a miss: re-observing the `KeyError`/exit-2 behavior would require calling one of the two check scripts on an env name both are documented (F-138-05) to mishandle, which this plan's own critical hazard #2 explicitly forbids.

**The plan's own `**Plans:**` grep verify probe (Task 3) produces empty output, by repo convention, not by omission.** `.planning/ROADMAP.md` consistently spells this line `**Plans**:` (colon outside the bold run) for every phase in the active v1.31 milestone section -- never `**Plans:**` (colon inside), which is the literal substring the plan's verify command greps for. That exact literal form does appear elsewhere in this same file, in several already-shipped, older milestones (`v1.13`/`v1.19`/`v1.20`), confirming it is a real, pre-existing style variant this tooling has previously produced -- just not the one live in the v1.31 section today. Since this plan did not call `roadmap.update-plan-progress` (see Deviations), no `**Plans**:`-style line was touched at all in this plan's diff, so the probe's empty result is consistent with, not contrary to, "no other phase's Plans line moved." Verified by full manual diff review instead (see Task 3 commit message and this SUMMARY's Deviations section).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 140 (Parameter Table) is structurally complete: all 7 plans executed, all 5 TABLE-* requirements marked Complete exactly once, `src/proms/eprom.cpp` byte-unchanged throughout, both named divergences (F-140-05, D-06/0x08 contradiction) and the wrong published `energy_cap_us` justification (F-140-07) recorded for Phase 146 to reconcile.
- Phase 141 (Per-Byte Program Loop) can now wire `eprom_params_for()` into `configure_eprom` -- the table, the accessor, all 18 cited cells, and the fail-closed NULL-row contract are complete and proven; the real AVR flash cost this phase's ~0 delta deferred (mechanically, via `-Wl,--gc-sections`) lands in Phase 141's own measurement.
- Phase 142 (High-Voltage Routing) has a pinned, reasoned inventory of the two `0x0B || FLAG_VPE_AS_VPP` branch sites (`eprom.cpp:145`/`:218`) it will legitimately move -- the D-13 gate is expected to go RED when it does, and must be re-derived (never hand-edited) at that time.
- Phase 144 (`TEST-08`) has this plan's prediction-vs-measurement table as its own reconciliation's input; `TEST-06` has the still-GREEN `native_trace_v131` frozen fixture to diff the new post-loop trace against.
- Phase 146 (`CLOSE-04`) inherits three named items to reconcile against published text this phase did not edit: F-140-05 (a possible `0x07` family split), the `0x08` prose-vs-table contradiction (D-06), and F-140-07 (the wrong "100 x 500 us" gh#15 justification for `0x0B`'s `energy_cap_us`).
- No blockers for Phase 141.

---

## Gate Transcripts (verbatim, this plan's own cold Task 1 run)

```
$ python3 scripts/check_size_baseline.py --avr-log uno=/tmp/140-07-uno.log \
    --avr-log uno328pb=/tmp/140-07-uno328pb.log --avr-log leonardo=/tmp/140-07-leonardo.log \
    --native-log native=/tmp/140-07-native.log --native-log native_nodevtools=/tmp/140-07-native_nodevtools.log

PASS: uno(flash=23954/32256,ram=1573/2048), uno328pb(flash=24004/32384,ram=1579/2048),
leonardo(flash=26016/28672,ram=2014/2560), native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)
default_seam_exit=0
```

```
$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json \
    --avr-log uno=/tmp/140-07-uno.log --avr-log uno328pb=/tmp/140-07-uno328pb.log --avr-log leonardo=/tmp/140-07-leonardo.log

PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]),
leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=])
merge05_exit=0
```

```
$ python3 scripts/check_build_warnings.py --log native=/tmp/140-07-native.log --log native_nodevtools=/tmp/140-07-native_nodevtools.log

PASS: native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166 (== watermark 1166)
warn_native_exit=0
```

```
$ python3 scripts/check_build_warnings.py --log uno=/tmp/140-07-uno.log --log uno328pb=/tmp/140-07-uno328pb.log --log leonardo=/tmp/140-07-leonardo.log

PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0)
warn_avr_exit=0
```

```
$ cd /workspaces/firestarter && python3 -m pytest tests/ -q
244 passed in 11.36s

$ cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts="" -q
1547 passed, 1 warning in 196.51s (0:03:16)
```

Neither check script was invoked with `native_params_v131` or `native_trace_v131` at any point (both would misbehave on an unrecognized env name, F-138-05). Both submodules confirmed clean after every command: `git -C firestarter status --porcelain` empty; `git -C firestarter_app status --porcelain` shows only pre-existing, plan-unrelated untracked files present before this plan started.

## Suite / Env Counts (six figures, this plan's own cold measurement)

| Env / suite | Cold measurement | CI coverage |
|---|---|---|
| `native` | 141 cases / 141 succeeded / 17 suites | `build.yml` / `beta-build.yml` |
| `native_nodevtools` | 141 cases / 141 succeeded / 17 suites | `build.yml` / `beta-build.yml` |
| `native_trace_v131` | 5 cases / 5 succeeded / 1 suite | **none** -- local run-by-name only (F-140-11) |
| `native_params_v131` | 9 cases / 9 succeeded / 1 suite | **none** -- local run-by-name only (F-140-11) |
| firmware `pytest tests/ -q` | 244 passed (227 + 7 + 10) | `build.yml` |
| app `pytest tests/ -o addopts="" -q` | 1547 passed (1539 + 8) | `ci.yml` |

## Prediction vs. Measurement (140-PREDICTIONS.md, committed `a2705cfb02d848ab1d927da0b784f959300cc4ab`)

| # | Predicted | Measured (this plan, cold) | Match |
|---|---|---|---|
| P1 | AVR flash delta ~=0 on `uno`/`uno328pb`/`leonardo` | 0 / 0 / 0 (23954/24004/26016, byte-identical to `size_baseline_v131.json`) | Yes -- exact |
| P2 | AVR RAM delta = exactly 0 on all three | 0 / 0 / 0 (1573/1579/2014) | Yes -- exact |
| P3 | `native`/`native_nodevtools` warnings exactly 1166 each | 1166 / 1166 | Yes -- exact |
| P4 | `native`/`native_nodevtools` 141/17; `native_trace_v131` 5/1 GREEN | 141/17, 141/17, 5/1 -- all PASSED | Yes -- exact |
| P5 | `native_params_v131` raises uncaught `KeyError` on `check_size_baseline.py`, exit 2 on `check_build_warnings.py` | **Not independently re-triggered** this session (plan's critical hazard #2 forbids it); basis unchanged since F-138-05 | Not re-tested -- deliberate abstention, not a miss |

**No contradiction found.** Full mechanical explanation for the ~0 AVR flash delta, and both named divergences (F-140-05, D-06), are recorded in `140-PARAM-TABLE-RECORD.md` §§3-4, 6.

## Five Requirement Evidence Pointers

- **TABLE-01** -- `eprom_params.h`/`eprom_params.cpp` (140-01) + `native_params_v131` cases 7 and 9 (140-04) + the citation gate's field-name freeze (`test_struct_field_names_are_exactly_the_frozen_six_in_order`, 140-05).
- **TABLE-02** -- the citation gate's no-pulse-column test (`test_no_pulse_width_column_exists`, 140-05) + `native_trace_v131` still GREEN (5/5, this plan's own cold re-run).
- **TABLE-03** -- `native_params_v131` cases 1-6 (140-04), with the explicit note (§9 of the record) that no bench oracle exists for this branch (F-140-04).
- **TABLE-04** -- the 18-cell sidecar (`eprom_params_citations.json`) and its coverage/drift/well-formedness gate (140-05), with 5 planted RED runs.
- **TABLE-05** -- the two split gates, firmware half (140-02, 3 planted RED runs) and database half (140-03, 4 planted RED runs).

---
*Phase: 140-parameter-table*
*Completed: 2026-08-10*

## Self-Check: PASSED

Files verified present on disk:
- FOUND: `.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md`
- FOUND: `.planning/phases/140-parameter-table/140-07-SUMMARY.md`

Commits verified present in git history (meta repo):
- FOUND: `c78cbb77` (docs: write the Phase 140 close record)
- FOUND: `bf52f47b` (docs: mark TABLE-01..05 complete)

Re-confirmed invariants immediately before finalizing this SUMMARY:
- `grep -c '^- \[x\] \*\*TABLE-0' .planning/REQUIREMENTS.md` -> `5`
- `grep -Ec '\| TABLE-0[1-5] \| Phase 140 \| Complete \|'` -> `5` in both `REQUIREMENTS.md` and `ROADMAP.md`
- `git diff --quiet -- .planning/PROJECT.md` -> exit 0 (byte-unchanged)
- `git -C firestarter diff --quiet -- src/proms/eprom.cpp` -> exit 0 (byte-unchanged, D-10 preserved)
- Both submodules' `git status --porcelain` -> empty (firestarter) / pre-existing-untracked-only (firestarter_app) -- no commit landed in either from this plan
