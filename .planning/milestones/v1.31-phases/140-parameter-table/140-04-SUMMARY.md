---
phase: 140-parameter-table
plan: 04
subsystem: firmware
tags: [eprom, progmem, avr, platformio, unity, native-test, fail-closed, table-03]

# Dependency graph
requires:
  - phase: 140-01
    provides: "eprom_params_t, EPROM_PARAM_KEYS[]/EPROM_PARAMS[] PROGMEM tables and the fail-closed eprom_params_for() accessor this suite calls into"
provides:
  - "[env:native_params_v131]: a FIFTH native PlatformIO environment (platformio.ini), naming only native/avr/test_eprom_params_v131 in its test_filter -- both pinned envs' 141-case/17-suite counts left untouched"
  - "test/native/avr/test_eprom_params_v131/host_stubs.cpp: a pure pass-through host stub TU (no opt-in recorder guard needed)"
  - "test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp: 9 Unity cases proving, by a RUNNING TEST, that configure_eprom's pulse_delay == 0 fallback (src/proms/eprom.cpp:69-76) fires only when pulse_delay is genuinely zero, paired 1:1 with negative controls, plus eprom_params_for()'s row-resolution and fail-closed-NULL behaviour"
  - "Proof that native_params_v131's existence moved nothing pinned: native and native_nodevtools both still report 141/141/17 cold, and native_trace_v131 (D-10's frozen fixture) is still 5/5/1 GREEN"
affects: [140-05-citations-sidecar, 140-06-claude-md-exception, 140-07-close-reconciliation, 144-close-reconciliation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fifth native env (D-11): a suite that must run but must never move a pinned case/suite count gets its own dedicated PlatformIO env, positive-test_filter-allowlisted, excluded from default_envs and from both size/warning baseline scripts by name -- same shape as native_trace_v131 (Phase 138), now proven twice"
    - "pulse_delay == 0 fallback proof requires a PAIRED negative control (pulse_delay = 777) for every positive case, or the positive assertion can pass on a handle the fallback switch never actually touched (T-140-13)"

key-files:
  created:
    - firestarter/test/native/avr/test_eprom_params_v131/host_stubs.cpp
    - firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp
  modified:
    - firestarter/platformio.ini

key-decisions:
  - "Host stub TU's own banner text avoids the literal substring 'HOST_STUBS_' and the 'src/proms/*.cpp' glob pattern (both from the copied test_not_implemented precedent) -- the former to keep this plan's own negative-grep verification meaningful, the latter following the 140-01 precedent that /* inside prose trips -Wcomment"
  - "delay()/delayMicroseconds() mocked with plain .AlwaysReturn() (test_cmd_admission's idiom), not test_trace_eprom_v131's .AlwaysDo(...) recorder lambda -- this suite's code path (configure_memory -> configure_eprom's pulse_delay fallback) never calls either function, so no recorder is needed"
  - "make_handle() sets mem_size=2048 and FLAG_SKIP_BLANK_CHECK|FLAG_SKIP_ERASE on every case (mirrors the trace suite's handle-construction convention) even though this suite never invokes firestarter_operation_main/_init -- configure_eprom only wires function pointers and resolves the pulse_delay fallback for CMD_WRITE, so no operation ever actually runs"

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "pulse_delay == 0 fallback EXERCISED by a running test (not asserted in prose): 0x07/0x08/0x0B resolve to 1000/100/500 us respectively"
    verification:
      - kind: unit
        ref: "test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp#test_0x07_zero_pulse_delay_takes_the_1000us_fallback, #test_0x08_zero_pulse_delay_takes_the_100us_fallback, #test_0x0B_zero_pulse_delay_takes_the_500us_fallback"
        status: pass
    human_judgment: false
  - id: D2
    description: "Non-vacuity: a nonzero pulse_delay (777) on each of 0x07/0x08/0x0B survives configure_memory untouched -- the paired negative control that stops D1 passing vacuously (T-140-13)"
    verification:
      - kind: unit
        ref: "test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp#test_0x07_nonzero_pulse_delay_is_left_alone, #test_0x08_nonzero_pulse_delay_is_left_alone, #test_0x0B_nonzero_pulse_delay_is_left_alone"
        status: pass
    human_judgment: false
  - id: D3
    description: "Each of 0x07/0x08/0x0B resolves to its own distinct eprom_params_for() row; an unrecognised protocol (0x0C, and 0) resolves to NULL, never a default row (D-05 fail-closed, T-140-17)"
    verification:
      - kind: unit
        ref: "test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp#test_each_protocol_resolves_to_its_own_distinct_row, #test_unknown_protocol_returns_null"
        status: pass
    human_judgment: false
  - id: D4
    description: "All 18 cell values of the frozen plan-140-01 table are read back through pgm_read_byte/pgm_read_dword (never a direct PROGMEM dereference) and match exactly"
    verification:
      - kind: unit
        ref: "test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp#test_row_values_match_the_frozen_table"
        status: pass
    human_judgment: false
  - id: D5
    description: "Neither pinned native env moved: native and native_nodevtools both still report 141 test cases / 141 succeeded / 17 suites cold, and check_build_warnings.py still reports exactly 1166 total warnings on both"
    verification:
      - kind: other
        ref: "rm -rf .pio/build/native && pio test -e native; rm -rf .pio/build/native_nodevtools && pio test -e native_nodevtools; scripts/check_build_warnings.py --log native=... --log native_nodevtools=... -> PASS total warnings=1166 (== watermark) both envs, exit 0"
        status: pass
    human_judgment: false
  - id: D6
    description: "native_trace_v131 (D-10's frozen pre-change trace fixture) is still GREEN, and src/proms/eprom.cpp remains byte-unchanged"
    verification:
      - kind: other
        ref: "rm -rf .pio/build/native_trace_v131 && pio test -e native_trace_v131 -> 5 test cases: 5 succeeded, 1 suite; git -C firestarter diff --quiet -- src/proms/eprom.cpp (exit 0)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-08-10
status: complete
---

# Phase 140 Plan 04: Native Parameter-Table Test Suite Summary

**Fifth PlatformIO native env (`native_params_v131`) plus a 9-case Unity suite that exercises `configure_eprom`'s `pulse_delay == 0` fallback and `eprom_params_for()`'s row resolution by running code — the only possible oracle for TABLE-03, since 0 of 329 shipped 27C chips ever hit that branch on the bench.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-10T01:34:54Z
- **Completed:** 2026-08-10T01:54:15Z
- **Tasks:** 3 (Task 3 was verification-only — see Issues Encountered)
- **Files modified:** 3 (1 modified: `platformio.ini`; 2 created)

## Accomplishments

- Appended `[env:native_params_v131]` to `firestarter/platformio.ini`, a structural copy of
  `[env:native_trace_v131]` (D-11): `test_filter` names exactly one entry
  (`native/avr/test_eprom_params_v131`), `build_flags` inherits `${env:native.build_flags}` plus its
  own `-I`, `lib_deps`/`build_src_filter`/`test_build_src` copied unchanged. The HARD CONSTRAINT
  comment block states all five guardrails: never folded into either pinned env's `test_filter`,
  never added to `default_envs`, never fed to `check_size_baseline.py` (F-138-05 uncaught `KeyError`)
  or `check_build_warnings.py`, and runs in **no CI leg of either repository** (F-140-11).
- Created `test/native/avr/test_eprom_params_v131/host_stubs.cpp`: a pure pass-through copy of
  `test_not_implemented/host_stubs.cpp`'s shape (no `HOST_STUBS_*` opt-in guard) — this suite calls
  `configure_memory`/`configure_eprom` only, which perform no hardware I/O beyond
  `mem_util_set_address(handle, 0)`.
- Created `test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp` — 9 hand-listed
  `RUN_TEST` cases (verified: `grep -c 'RUN_TEST('` = 9, matching the reported case count exactly):
  1. `test_0x07_zero_pulse_delay_takes_the_1000us_fallback`
  2. `test_0x08_zero_pulse_delay_takes_the_100us_fallback`
  3. `test_0x0B_zero_pulse_delay_takes_the_500us_fallback`
  4. `test_0x07_nonzero_pulse_delay_is_left_alone` (negative control, pulse_delay=777)
  5. `test_0x08_nonzero_pulse_delay_is_left_alone`
  6. `test_0x0B_nonzero_pulse_delay_is_left_alone`
  7. `test_each_protocol_resolves_to_its_own_distinct_row`
  8. `test_unknown_protocol_returns_null` (0x0C and 0, both NULL — D-05)
  9. `test_row_values_match_the_frozen_table` (18 cells, all three rows, via `pgm_read_byte`/`pgm_read_dword`)
- **Cold run, verbatim (`rm -rf .pio/build/native_params_v131 && pio test -e native_params_v131`):**
  `9 test cases: 9 succeeded`, 1 suite, exit 0. A subsequent invocation confirmed exit code 0
  explicitly.
- **Proved the pinned envs did not move (all four cold, `rm -rf .pio/build/<env>` then a single
  `pio test -e <env>`):**

  | Env | Cases | Succeeded | Suites | Status | CI coverage |
  |---|---|---|---|---|---|
  | `native` | 141 | 141 | 17 | PASSED, exit 0 | build.yml / beta-build.yml |
  | `native_nodevtools` | 141 | 141 | 17 | PASSED, exit 0 | build.yml / beta-build.yml |
  | `native_trace_v131` | 5 | 5 | 1 | PASSED, exit 0 (D-10 frozen fixture, still GREEN) | **none** — local run-by-name only |
  | `native_params_v131` | 9 | 9 | 1 | PASSED, exit 0 | **none** — local run-by-name only |

  `native_params_v131` and `native_trace_v131` run in **no CI leg of either repository**
  (`build.yml:142,155` / `beta-build.yml:122,128` invoke only `native` and `native_nodevtools`,
  F-140-11) — their counts above are a **local, run-by-name obligation**, recorded here and to be
  re-recorded in the phase-close record (D-11), never implied to be CI-covered.
- **`check_build_warnings.py` on the two pinned envs only, verbatim:**
  `PASS: native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166
  (== watermark 1166)`, exit 0. `native_params_v131`/`native_trace_v131` were never passed to this
  script or to `check_size_baseline.py` (both would misbehave on an unrecognised env name, F-138-05).
- `git -C firestarter diff --quiet -- src/proms/eprom.cpp` exits 0 — **byte-unchanged** (D-10): this
  suite calls into `configure_eprom` but never edits it.
- `git -C firestarter diff --quiet -- scripts/baseline/` exits 0 — `size_baseline.json` and
  `size_baseline_v131.json` both byte-unchanged; `check_size_baseline.py` was not invoked at all in
  this plan.
- `cd firestarter && python3 -m pytest tests/ -q` → **234 passed** — unchanged from the pre-existing
  baseline (critical hazard #9); no regression from this plan's changes.

## Task Commits

1. **Task 1: Add `[env:native_params_v131]` and the pass-through host stub** — `f405922` (feat, firestarter)
2. **Task 2: Author the 9-case Unity suite** — `3c165d5` (test, firestarter)
3. **Task 3: Prove the pinned envs did not move, and record the run-by-name counts** — no new commit
   (verification-only; see Issues Encountered)

**Plan metadata:** this SUMMARY's own commit (docs: complete plan) — see final commit below.

## Files Created/Modified

- `firestarter/platformio.ini` (+42 lines) — new `[env:native_params_v131]` section, appended
  immediately after `[env:native_trace_v131]`; every pre-existing line left byte-for-byte untouched
  (`git diff --stat` shows insertions only).
- `firestarter/test/native/avr/test_eprom_params_v131/host_stubs.cpp` (new, 37 lines) — pure
  pass-through stub TU, no suite-specific opt-in guard.
- `firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp` (new, 220 lines) —
  the 9-case suite described above.

## Decisions Made

- Followed the plan's exact instruction to structurally copy `[env:native_trace_v131]` for the new
  env, including its HARD CONSTRAINT comment block (restated with this plan's own requirement IDs
  and an added explicit "no CI leg" line, F-140-11).
- Reworded two phrases in the new `host_stubs.cpp` banner relative to the literal copied precedent
  text (see `key-decisions` in frontmatter) — functionally identical file, wording chosen to avoid a
  self-defeating verification (the literal substring `HOST_STUBS_` inside a sentence *saying* "no
  guard is defined" would trip this plan's own negative-grep check) and to avoid the `-Wcomment`
  `/*`-inside-a-glob trap 140-01 already found and fixed once.
- Mocked `delay()`/`delayMicroseconds()` with `.AlwaysReturn()` rather than the trace suite's
  `.AlwaysDo(...)` recorder lambda, since this suite's code path never calls either function — the
  simpler idiom (also used by `test_cmd_admission`, `test_flash_intel_vpp`, and others) is correct
  and sufficient here.

## Deviations from Plan

None — plan executed exactly as written. The only adjustment was wording-only (see Decisions Made
above), caught and fixed before the first commit; it never landed as a defect in git history.

## Issues Encountered

**Task 3 produced no additional file changes, and therefore no additional commit.** The plan's Task
3 `<files>` tag names `firestarter/platformio.ini`, but Task 3's own `<action>` text describes a
pure verification-and-recording exercise (run all four native envs cold, run the warnings gate on
the two pinned envs, confirm the baseline files and `eprom.cpp` are untouched) — it contains no
further edit instruction, and none of `platformio.ini`'s content changed between Task 1's commit and
the end of Task 3. This mirrors 140-01 Plan Task 3's own precedent (that task, too, was primarily an
observe-and-record step, though it happened to also produce the `140-PREDICTIONS.md` file). Named
here per this project's "name the divergence" convention rather than silently treating the `<files>`
tag as satisfied by Task 1's earlier edit.

**Verification note (not a defect):** the local PlatformIO version (Core 6.1.19) does not print a
literal `"N test suites"` string in `pio test` summary output for any of the four envs measured in
this plan — the suite counts in the table above (17 / 17 / 1 / 1) are counted from the summary
table's row count per environment, exactly as 140-01-SUMMARY.md's own cold-measurement table already
did ("17 suites (summary-table count)"). The plan's own Task 3 verification commands anticipate this:
they grep for `'[0-9]+ test cases: [0-9]+ succeeded'` (which is present, verbatim, in every log) and
separately for `'[0-9]+ test suites'` (which this PlatformIO version does not emit) — the acceptance
criteria were satisfied via the case-count grep and the summary-table row count, not the absent
literal string.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- TABLE-03 (the `pulse_delay == 0` fallback) is now proven by a running, committed test — the only
  oracle that can ever prove it, since no bench run in Phase 145 reaches this branch (F-140-04).
  TABLE-01's row-resolution behaviour is also proven behaviourally here, alongside 140-01's
  compile-time proof and 140-05's forthcoming citation-sidecar half.
- Per this plan's own `<requirement_completion>` scope, **no requirement checkbox is flipped by this
  plan** — TABLE-01 spans 140-01/140-04/140-05, and TABLE-03's completion is recorded together with
  the phase-wide regression evidence in plan 140-07 only. `.planning/REQUIREMENTS.md` and
  `.planning/ROADMAP.md` are untouched by this plan (no checkbox edits made).
- `native_params_v131`'s 9/9 pass and the confirmed-unmoved 141/141/17 pinned counts are ready
  inputs for 140-07's phase-wide regression record and for 144's close reconciliation — both should
  cite this SUMMARY's table rather than re-deriving the counts.
- No blockers for plans 140-05, 140-06 or 140-07.

---
*Phase: 140-parameter-table*
*Completed: 2026-08-10*

## Self-Check: PASSED

Files verified present on disk:
- FOUND: `firestarter/platformio.ini`
- FOUND: `firestarter/test/native/avr/test_eprom_params_v131/host_stubs.cpp`
- FOUND: `firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp`
- FOUND: `.planning/phases/140-parameter-table/140-04-SUMMARY.md`

Commits verified present in git history (firestarter):
- FOUND: `f405922`
- FOUND: `3c165d5`
