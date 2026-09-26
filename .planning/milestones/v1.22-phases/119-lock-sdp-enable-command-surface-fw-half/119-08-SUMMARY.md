---
phase: 119-lock-sdp-enable-command-surface-fw-half
plan: "08"
subsystem: firmware-sdp-lock
tags: [firmware, firestarter, sdp, at28c, eeprom28c, native-tests, unity, timing-measurement]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "05"
    provides: "Scripted micros() tick queue (sdp_script_micros/s_micros_script/s_micros_cursor/s_micros_tail) replacing the two-slot parity alternator -- the seam this plan's tracker drives"
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "07"
    provides: "Both native envs' build_src_filter widened with operation_utils.cpp; generic NULL-main refusal; complete cmd x protocol matrix; Leonardo flash at 25972/28672 (2700 B free)"
provides:
  - "eeprom28c_write_execute's worst-per-byte page-load interval tracker, reported ONCE via the unconditional MSG_INFO_PAGE_LOAD_WORST_US (0x62), reachable on both the completing and the aborting exit via a single-exit restructure"
  - "sdp_decode_u32_param_for_id() -- a reusable u32-parameter decoder over captured_frames, using the same documented wire layout sdp_captured_frame_ids walks"
  - "Cases 26-29 in test_eeprom28c_sdp.cpp: decoded-value proof on a completing two-page write (non-monotonic script, mid-write spike), the aborting-exit proof (empty-socket bench condition), the declined-WARN pin, and the response_code-preservation pin"
  - "The full firmware+host regression sweep and flash decomposition for Plan 119-10 to lift: per-plan attribution against the live 2992 B Leonardo headroom, the enumerated real-path diff, and the golden identity story"
affects: [119-09, 119-10, 119-11]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single-exit restructure (flagged break + trailing report) so a report line is reachable on both a function's normal and early-abort exits, without changing the abort's own error/response_code semantics"
    - "Decoding a captured log frame's parameter bytes (not just membership of its id) to prove a tracker reports the correct VALUE, not merely that it fired"
    - "A non-monotonic scripted tick sequence with the spike placed mid-drive (never first/last) as the discriminator between a running-maximum tracker and a first/last-interval bug"

key-files:
  created: []
  modified:
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp

key-decisions:
  - "Verified the structural precondition against live source before editing: eeprom28c_write_execute's per-byte loop's closing brace was immediately followed by the function's closing brace (nothing followed the loop) -- confirmed the single-exit restructure is behaviour-preserving by inspection, not by hope."
  - "Kept the page_load_aborted bool per the plan's explicit instruction even though both exits report identically today (there is no branching behaviour on it) -- marked with (void) for reader clarity, since the plan calls for the flag as the documented single-exit mechanism, not as a currently-branching control value."
  - "Extended the existing gh#11 citation comment (rather than writing a new one) with all five required items: the flash-vs-timing conflation named explicitly, gh#11 restated as a conflation bug in the comment's own prior wording, what the tracked number is and is not (MCU driving its own latches; t_BLC as accepted by the die is not provable), why there is no runtime check here (the max-tracking compare is not the declined budget check), and F-118-01's 572-vs-600us numbers."
  - "Rule 1 auto-fix, out of the plan's stated files_modified: added a micros() mock to test_val_eeprom28c.cpp's setUp(). Task 1's tracker made eeprom28c_write_execute call micros() for the first time, and every case in that suite drives write_execute via h.firestarter_operation_main(&h) -- an unmocked micros() call aborts ArduinoFake (SIGABRT), confirmed by running the suite immediately after Task 1's commit. Fixed with AlwaysReturn(0) since the suite never asserts on timing."
  - "New native cases numbered 26-29, not 24-25 as the plan's read_first assumed -- Plan 119-07 (which landed after this plan's read_first was authored) already claimed cases 24/25 for the NULL-main refusal proofs. Continued the sequence from 26 rather than renumbering 119-07's cases."
  - "Case B's (Case 27's) abort geometry uses a two-page write (72 bytes) so the first page's failure demonstrably leaves the second page's bytes un-loaded (never contributing to the tracked max), rather than a single-page write where 'bytes loaded before the abort' would trivially equal 'all bytes in data_size'."

requirements-completed: []

coverage:
  - id: D1
    description: "eeprom28c_write_execute tracks the worst per-byte page-load interval and reports it exactly once via MSG_INFO_PAGE_LOAD_WORST_US (0x62), reachable on both the completing and the aborting exit via a single-exit restructure; no AT28C_TBLC_MAX_US comparison or LOG_WARN_* call added to the loop"
    requirement: LOCK-06
    verification:
      - kind: unit
        ref: "grep -c MSG_INFO_PAGE_LOAD_WORST_US src/proms/eeprom_28c.cpp -- 1; pio run -- 3/3 SUCCESS, flash +100 B all three boards"
        status: pass
      - kind: unit
        ref: "python3 tools/check_no_log_in_sdp_window.py -- PASS, confirmed empirically (eeprom28c_write_execute is not a scanned window)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Case 26: a completing two-page write with a non-monotonic scripted tick sequence (spike at byte index 40, neither first nor last) proves the tracker keeps a running maximum -- the DECODED u32 parameter equals the scripted maximum (77 us), not merely id membership"
    requirement: LOCK-06
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_eeprom28c_sdp*\" test_case26_write_execute_reports_worst_interval_on_completing_write -- PASSED"
        status: pass
    human_judgment: false
  - id: D3
    description: "Case 27: the first page's write poll fails against an always-wrong mock (the empty-socket bench condition); the report still fires via the single-exit break, MSG_ERR_EEPROM_TIMEOUT also appears, and the decoded value (55 us) corresponds only to the 64 bytes loaded before the abort -- a huge installed tail (999999999) is proven never reached"
    requirement: LOCK-06
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_eeprom28c_sdp*\" test_case27_write_execute_reports_worst_interval_on_aborting_write -- PASSED"
        status: pass
    human_judgment: false
  - id: D4
    description: "Case 28: an interval far above AT28C_TBLC_MAX_US (1000 vs 100) still never emits MSG_WARN_SDP_TBLC_EXCEEDED on this path, while MSG_INFO_PAGE_LOAD_WORST_US is present -- pins D-16's declined runtime budget check"
    requirement: LOCK-06
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_eeprom28c_sdp*\" test_case28_write_execute_no_tblc_budget_warn -- PASSED"
        status: pass
    human_judgment: false
  - id: D5
    description: "Case 29: response_code (WARNING) is unchanged across a completing write, mirroring test_case8's invariant onto the new emission"
    requirement: LOCK-06
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_eeprom28c_sdp*\" test_case29_write_execute_report_preserves_response_code -- PASSED"
        status: pass
    human_judgment: false
  - id: D6
    description: "Full regression sweep: both native envs 141/141 across 17 suites (was 137, +4); pio run 3/3 SUCCESS all boards; flash decomposed per-plan against the live 2992 B Leonardo headroom (lands at 2600 B free, no threshold claim beyond 'fits'); all host gates green; firmware diff enumerated by real path, frozen files confirmed absent; golden identity story confirmed"
    verification:
      - kind: unit
        ref: "pio test -e native / -e native_nodevtools -- 141/141 across 17 suites, both envs, identical counts"
        status: pass
      - kind: unit
        ref: "pio run -- 3/3 SUCCESS (Leonardo 26072/28672, Uno 23932/32256, uno328pb 23976/32384)"
        status: pass
      - kind: unit
        ref: "pytest across six named modules (30 passed); check_no_log_in_sdp_window.py / check_is_memory_cmd_no_ifdef.py / check_dispatch.py / check_devtest_orchestrator.py all exit 0; gen_sdp_bus_config.py --check exits 0; ruff (pre-existing 4-file finding, none in Phase 119 diff)"
        status: pass
      - kind: unit
        ref: "git diff --name-only 1880054..HEAD -- confirms include/flash_utils.h, src/proms/flash_5v_page.cpp, src/proms/flash_nor_unlock.cpp all absent"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-07-28
status: complete
---

# Phase 119 Plan 08: Page-Load Worst-Interval Tracker (D-16) + Full Firmware Sweep Summary

**`eeprom28c_write_execute`'s per-byte page-load loop now tracks its worst inter-byte `micros()` interval and reports it exactly once via `MSG_INFO_PAGE_LOAD_WORST_US` (0x62), reachable on both the completing and the aborting exit through a single-exit restructure — with the flash-vs-timing conflation in the directive named explicitly in source, no runtime budget check added to the hot path, and a full 17-suite/two-env/three-board regression sweep confirming the flash delta (+100 B, landing at 2600 B free against the live 2992 B headroom) and every host gate green.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-07-28
- **Tasks:** 3/3
- **Files modified:** 3 (2 firmware source/test files touched by the plan's own scope, 1 additional test file fixed under Rule 1)

## Accomplishments

- **Task 1 (the tracker):** Verified the structural precondition against live source first — `eeprom28c_write_execute`'s per-byte loop's closing brace was immediately followed by the function's closing brace, confirming nothing followed the loop and the single-exit restructure is behaviour-preserving by inspection. Added a worst-interval `uint32_t` and a previous-reading `uint32_t`, seeded from `micros()` immediately before the loop, updated via unsigned subtraction after every `firestarter_set_data` call. Converted the two early `return;` statements (after `eeprom28c_wait_for_page_write` / `eeprom28c_verify_page_readback`) into a flagged `break;`, so the single `LOG_ID_U32(MSG_INFO_PAGE_LOAD_WORST_US, worst)` call after the loop is reachable on both exits — the empty-socket bench condition takes the abort path on the very first page, exactly the case Plan 119-11 will bench. No `AT28C_TBLC_MAX_US` comparison and no `LOG_WARN_*` call anywhere in the loop (D-16 declines the runtime check, preserving 118's D-10). Extended the existing gh#11 citation comment with all five required items (see Deviations/Decisions). Flash delta: **+100 B on all three boards** (Leonardo 25972→26072, Uno 23832→23932, uno328pb 23876→23976).
- **Task 2 (the proofs):** Added `sdp_decode_u32_param_for_id()`, a reusable decoder over `captured_frames` using the same wire layout `sdp_captured_frame_ids` already walks. Added Cases 26-29 (see Deviations for the renumbering from the plan's stated 24-25): Case 26 proves the tracker's decoded value equals a scripted non-monotonic maximum on a completing two-page write; Case 27 proves the report fires on the aborting exit with the value corresponding only to the bytes loaded before the abort; Case 28 pins the declined runtime WARN even at a 10x-over-budget scripted interval; Case 29 mirrors Case 8's `response_code`-preservation invariant onto the new emission. All four passed on the first attempt. Re-checked Plan 119-05's frame-count inventory: it already recorded that zero existing frame-count assertions drive `eeprom28c_write_execute`, confirmed still true — nothing needed widening. `pio test -e native`/`-e native_nodevtools`: **141/141 across 17 suites, both envs** (was 137, +4). `pio run`: unchanged at 26072/23932/23976 (test-only task).
- **Task 3 (the sweep):** Ran the full firmware and host regression set (see below for the complete decomposition, enumeration, and gate table). No code changes in this task.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Mocked `micros()` in `test_val_eeprom28c.cpp`'s `setUp()`**
- **Found during:** Task 1 (immediately after committing the tracker)
- **Issue:** `eeprom28c_write_execute` now calls `micros()` for the first time. Every case in `test_val_eeprom28c.cpp` drives `write_execute` via `h.firestarter_operation_main(&h)` for `CMD_WRITE`, and that suite's `setUp()` never mocked `micros()` (it only mocked `delay`/`delayMicroseconds`/`millis`). Running `pio test -e native -f "*test_val_eeprom28c*"` right after Task 1's commit reproduced a `SIGABRT` (ArduinoFake aborts on any unmocked virtual).
- **Fix:** Added `When(Method(ArduinoFake(), micros)).AlwaysReturn(0);` to `setUp()`, with a comment explaining why. The suite never asserts on timing, so a fixed 0 is behaviourally inert to every existing case.
- **Files modified:** `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp`
- **Verification:** Re-ran the suite: 6/6 passed (was SIGABRT). Full `pio test -e native`/`-e native_nodevtools` both green afterward.
- **Committed in:** `30b1c40` (separate fix commit, before Task 2's new cases)

**2. [Not a Rule violation — plan read_first was stale] Cases numbered 26-29 instead of 24-25**
- **Found during:** Task 2 planning
- **Issue:** The plan's `read_first` describes "the main() RUN_TEST list as Plan 119-06 left it" and instructs "Add cases to test_eeprom28c_sdp.cpp, numbered from 24" — but Plan 119-07 (which executed after this plan's context was authored) already added cases 24 and 25 (the NULL-main refusal proofs).
- **Fix:** Continued the sequence from 26 rather than renumbering 119-07's already-committed cases.
- **Files modified:** `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- **Verification:** `grep -n "test_case2[4-9]"` confirms cases 24-29 are all present, uniquely named, and registered exactly once each in `main()`.
- **Committed in:** `0048b3d` (Task 2 commit)

---

**Total deviations:** 2 (1 Rule-1 auto-fix, 1 case-numbering continuation)
**Impact on plan:** Both were necessary corrections to keep the test suite green and consistent with prior-plan state; no scope creep, no plan intent altered.

## Task Commits

Each task was committed atomically inside the `firestarter/` submodule:

1. **Task 1: Track the worst per-byte page-load interval and report it once, on both exits** — `4d76c32` (feat)
   - Rule-1 fix (test_val_eeprom28c.cpp micros() mock) — `30b1c40` (fix, landed immediately after Task 1, before Task 2's new cases)
2. **Task 2: Prove the report line fires with the right value, on both the completing and the aborting exit** — `0048b3d` (test)
3. **Task 3: Full firmware and host regression sweep, with the flash increment attributed** — no code changes; recorded below

**Plan metadata:** committed alongside this SUMMARY (docs, meta commit staging the gitlink + SUMMARY.md + STATE.md + ROADMAP.md).

## Files Created/Modified

- `firestarter/src/proms/eeprom_28c.cpp` — the worst-interval tracker, the single-exit restructure, the `MSG_INFO_PAGE_LOAD_WORST_US` report call, and the extended gh#11/D-16 comment
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — `sdp_decode_u32_param_for_id()` and Cases 26-29
- `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — Rule-1 `micros()` mock fix (out-of-plan-scope, necessary regression fix)

## Decisions Made

See `key-decisions` in frontmatter for the six load-bearing ones (structural-precondition verification, the retained-but-unused abort flag, the extended comment's five required items, the Rule-1 fix, the case renumbering, and Case 27's two-page abort geometry).

## Task 3 — Full Regression Sweep (records for Plan 119-10)

### Firmware native suites

Both envs: **141/141 across 17 suites** (was 137/137 through Plan 119-07; +4 for this plan's Cases 26-29). Zero divergence between `[env:native]` and `[env:native_nodevtools]` — the same source, compiled and run twice, both green, confirming this plan's tracker is `DEV_TOOLS`-invariant like everything else on the LOCK-03 chain.

### `pio run` — all three AVR envs, 3/3 SUCCESS

| Board | Flash (before Task 1 → after) | Delta this plan | Free flash after |
|---|---|---|---|
| Leonardo | 25972 → 26072 / 28672 | **+100 B** | **2600 B** |
| Uno | 23832 → 23932 / 32256 | +100 B | 8324 B |
| uno328pb | 23876 → 23976 / 32384 | +100 B | 8408 B |

RAM unchanged on all three boards (Leonardo 2014/2560, Uno 1573/2048, uno328pb 1579/2048) — every new local is stack-scoped, not global.

### Flash decomposition — per-plan attribution against the live 2992 B Leonardo headroom (LOCK-06's own arithmetic is Plan 119-10's task; this plan's contribution and the running total are recorded here for that plan to lift)

Base (Phase 118 close, commit `1880054`): Leonardo **25680**/28672 (2992 B free), Uno 23542/32256, uno328pb 23592/32384.

| Plan | What it added | Leonardo Δ | Uno Δ | uno328pb Δ | Leonardo running total |
|---|---|---|---|---|---|
| 119-01 | Three catalog ids (numeric `#define`s only, no PROGMEM string table on firmware side) | +0 B | +0 B | +0 B | 25680 |
| 119-02 | `is_memory_cmd()` + `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` defines + second native env (no prod cost) | +12 B | +12 B | +12 B | 25692 |
| 119-04 | `EEPROM_SDP_ENABLE[3]`, shared timed-emit helper, both SDP ops, entry points, switch arms | +262 B | +260 B | +254 B | 25954 |
| 119-05 | Test-only (goldens, scripted `micros()` queue) | +0 B | +0 B | +0 B | 25954 |
| 119-06 | Test-only (three-way identity/distinctness guard) | +0 B | +0 B | +0 B | 25954 |
| 119-07 | Generic NULL-`main` refusal at the op layer | +18 B | +18 B | +18 B | 25972 |
| **119-08 (this plan)** | **Worst-per-byte page-load tracker + single-exit restructure + report call** | **+100 B** | **+100 B** | **+100 B** | **26072** |
| **Total phase delta** | | **+392 B** | **+390 B** | **+384 B** | |

**Arithmetic against the live 2992 B headroom (Leonardo):** 2992 B − 392 B = **2600 B free**. **No threshold claim beyond "fits"** (D-15's instruction, matching how Phases 117 and 118 recorded their deltas as measured facts with provenance) — this plan makes no claim about how close to any limit the phase landed, only that the measured delta fits inside the measured headroom.

**`-D DEV_TOOLS` remains the tighter, binding configuration.** RESEARCH's temporary `[env:leonardo_nodevtools]` measurement at the phase base (`1880054`, before any Phase 119 change) recorded **24388/28672** for a release-config build — i.e. a **1292 B** cost for the `-D DEV_TOOLS` flag (25680 − 24388). Since `-D DEV_TOOLS` costs flash rather than saving it, the `DEV_TOOLS` build has the SMALLER headroom of the two configurations (2600 B today, vs. an inferred ~3892 B for a release-config build carrying this phase's same +392 B delta) — it remains the binding constraint for LOCK-06's judgement. This plan did not re-run a release-config build; the figure is restated from RESEARCH's own measurement, consistent with 119-09/119-10's plan text.

### Host gate set — all green

- `python3 -m pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py tests/test_check_is_memory_cmd_no_ifdef.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py tests/test_dispatch_mirror.py -q` → **30 passed** (matches Plan 119-07's baseline exactly — no test in these six modules exercises `eeprom28c_write_execute`).
- `python3 tools/check_no_log_in_sdp_window.py` → PASS, exit 0. Confirmed empirically (not assumed): `eeprom28c_write_execute` is not one of its three scanned windows (emitter lines 298-314, completion-poll lines 348-361 — unchanged anchors), so this plan's new `LOG_ID_U32` call is legitimate and outside the gate's scope.
- `python3 tools/check_is_memory_cmd_no_ifdef.py` → PASS, exit 0.
- `python3 tools/check_dispatch.py` → PASS, exit 0 (746 chips scanned, 0 regressions, 0 consistency violations — unaffected by this plan's `eeprom_28c.cpp` edit, which touches no dispatch logic).
- `python3 tools/check_devtest_orchestrator.py` → PASS, exit 0 (host-only files, untouched by this firmware-only plan).
- `python3 tools/gen_sdp_bus_config.py --check` → exit 0, `_shared/sdp_bus_config.h` regenerates blob-identically.
- `ruff check .` / `ruff format --check .` (target-version `py39` per `pyproject.toml`, Python 3.12.13 runtime): **4 pre-existing violations** in `.github/scripts/update_version.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`, `tools/check_mypy_watermark.py` — confirmed via `git status --short` in `firestarter_app/` that this plan touched **zero** files in that submodule, and `118-NONREGRESSION.md` §"Sweep summary" already recorded these identical 4 pre-existing findings at Phase 118's close. Not this phase's regression; not chased.

### Firmware diff, enumerated by real path (not the ROADMAP's non-existent `flash_utils.{h,cpp}` shorthand)

`git -C /workspaces/firestarter diff --name-only 1880054..HEAD` (full Phase 119 diff, 17 commits, all seven firmware plans):

```
.github/workflows/build.yml
CLAUDE.md
include/eprom_operations.h
include/firestarter.h
include/messages.h
platformio.ini
src/eprom_operations.cpp
src/firestarter.cpp
src/operation_utils.cpp
src/proms/eeprom_28c.cpp
test/native/avr/_shared/host_stubs_common.inc
test/native/avr/_shared/sdp_expected.h
test/native/avr/test_cmd_admission/avr/pgmspace.h
test/native/avr/test_cmd_admission/host_stubs.cpp
test/native/avr/test_cmd_admission/test_cmd_admission.cpp
test/native/avr/test_data_input/host_stubs.cpp
test/native/avr/test_dispatch/test_configure_memory.cpp
test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
test/native/avr/test_sdp_harness/test_sdp_harness.cpp
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp
tools/catalog/messages.toml
```

**`include/flash_utils.h`, `src/proms/flash_5v_page.cpp`, and `src/proms/flash_nor_unlock.cpp` (the real paths — never the ROADMAP's `flash_utils.{h,cpp}` shorthand, which is not a real path in this tree) are all absent from that listing.** Confirmed by enumeration, not by a `git diff -- src/flash_utils.h` check against a path that does not exist (which would pass vacuously).

### Golden identity story (for Plan 119-10 to lift)

- **`_shared/sdp_bus_config.h`** — blob-SHA identical to the phase base (`e0111e6...` both sides). Confirmed via `git diff 1880054..HEAD -- test/native/avr/_shared/sdp_bus_config.h` (empty) and matching `git hash-object` output.
- **`_shared/host_stubs_common.inc`** — **CORRECTION to the plan's stated acceptance criterion:** this file is **NOT** blob-identical to the phase base. Plan 119-07 Task 1 added one no-op `extern "C" void op_reset_timeout() {}` stub (additions-only, confirmed via `git diff` — zero pre-existing lines touched) when widening both native envs' `build_src_filter` with `operation_utils.cpp`. This plan (119-08) did not touch the file further. The plan's Task 3 acceptance criterion (inherited from 118-NONREGRESSION.md's shape, which predates 119-07's change) is stale on this one point; recorded as a correction here per project convention (D-05/D-15's class of correction), not silently passed over.
- **`_shared/sdp_expected.h`** — its whole-file blob SHA **necessarily changed** (Plan 119-05 added four `SDP_FIXED_LOCK_*` arrays). Its identity proof is Plan 119-05's per-array byte-identity check: `diff` against `git show 1880054:test/native/avr/_shared/sdp_expected.h` shows **additions only** (re-confirmed here: `git diff 1880054..HEAD -- test/native/avr/_shared/sdp_expected.h | grep '^-' | grep -v '^---'` → 0 lines removed). That method and result are restated here, not re-derived, per Plan 119-05's own instruction.

### Two known-RED host modules — pre-existing, not chased

- **`tests/test_audit_coverage_matrix.py`** — stale golden, pre-existing (`.planning` memory `reference_audit_coverage_matrix_golden_stale.md`). Not run as part of this plan's gate set (not one of the six named modules); not this phase's regression.
- **`tests/test_no_programmer_found_*`** — go RED with a live board attached (`.planning` memory `reference_characterization_no_programmer_tests_fail_with_live_board.md`), an environment artifact. Not run as part of this plan's gate set.

Neither module is in Task 3's named six-module pytest command; both are named here per Task 3's explicit instruction to record and not chase them.

## Issues Encountered

None beyond the Rule-1 fix and the case-renumbering documented above under Deviations.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None. This plan modifies production firmware (`eeprom_28c.cpp`) and native test suites only; no UI or data-rendering path is affected.

## Requirement Status

**No requirement marked Complete by this plan**, per the plan's explicit instruction. `REQUIREMENTS.md` is byte-unchanged by this plan (confirmed: this plan made zero edits to that file). **LOCK-06 remains Pending** — it is closed by Plan 119-10 (the flash-half judgement against the live 2992 B headroom, using this plan's per-plan decomposition above) and Plan 119-11 (the three-board bench measurement). LOCK-01 through LOCK-05 remain Complete, untouched. DEVTEST-01 remains Pending (Phase 121's host half).

## Next Phase Readiness

- The page-load worst-interval tracker is landed, tested on both exits, and its comment names the flash-vs-timing conflation explicitly — Plan 119-11 can now run `firestarter write at28c256 -b --force` on all three boards and expect `MSG_INFO_PAGE_LOAD_WORST_US` to appear exactly once per write, on either exit.
- The full per-plan flash decomposition above is ready for Plan 119-10 to lift verbatim into its non-regression sweep and LOCK-06 closure arithmetic.
- The `_shared/host_stubs_common.inc` non-identity correction is recorded here so Plan 119-10 does not inherit a stale "blob-identical" claim for that file.
- This is the **last firmware code plan** in Phase 119 — Plan 119-09 (meta, the Phase 121 amendment) and Plan 119-10/119-11 (meta, non-regression + bench) proceed without further `firestarter/` submodule edits from this plan set.
- No blockers for Plan 119-09.

---
*Phase: 119-lock-sdp-enable-command-surface-fw-half*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/src/proms/eeprom_28c.cpp`
- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- FOUND: `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp`
- FOUND: `4d76c32` (Task 1 commit, firestarter submodule)
- FOUND: `30b1c40` (Rule-1 fix commit, firestarter submodule)
- FOUND: `0048b3d` (Task 2 commit, firestarter submodule)
