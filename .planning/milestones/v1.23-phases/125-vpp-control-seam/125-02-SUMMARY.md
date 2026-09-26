---
phase: 125-vpp-control-seam
plan: 02
subsystem: firmware
tags: [pytest, host-gcc, preprocessor, capability-macro, avr, arm, py32f071, testing]

# Dependency graph
requires:
  - phase: 125-vpp-control-seam
    provides: "125-01's hand-authored include/rurp_vpp.h + src/rurp_vpp.cpp seam, landed in the ARM manifest at 24 enforced sources, with the C-1 native tripwire fired clean (141/17 unchanged)"
provides:
  - "firestarter/tests/test_vpp_seam_manual_on_every_board.py -- 7 functions / 10 collected cases proving VPP-02: one parametrized compile-and-run test across all four board macro-sets, plus the forced-capability non-vacuity leg, the unset-and-non-AVR leg, a drift leg anchored on values literally present in platformio.ini/CMakeLists.txt, the build-supplies-the-macro leg in both directions, the dependency-freedom leg, and the self-enforcing no-skip meta leg"
  - "pytest tests/ moved 72 -> 78 (Task 1) -> 82 (Task 2), verified at each step, never asserted from memory"
affects: [125-04, 125-05, 125-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Compile-and-run subprocess harness (extends the pinmap precedent's preprocess-only shape): a fresh tmp_path shim TU is compiled together with the production src/rurp_vpp.cpp in one host g++ invocation per board macro-set, then the resulting binary is run as a SECOND subprocess, and the seam's return value is parsed from stdout -- never the run subprocess's exit code, because the required value (1) is indistinguishable from a compile failure, link failure or crash if carried as an exit code."
    - "Two independently-scoped '#error' message readers (_expected_header_error_text / _expected_source_error_text), each asserting exactly one directive in its own file -- never one shared 'exactly one' assertion across both files, because the header and the .cpp carry two different messages."

key-files:
  created:
    - firestarter/tests/test_vpp_seam_manual_on_every_board.py
  modified: []

key-decisions:
  - "Regex for reading the #error message had to tolerate an indented directive: include/rurp_vpp.h's guard is written as '#    error \"...\"' (nested inside #if/#if), not the pinmap precedent's flush '#error \"...\"'. Fixed the pattern to '#\\s*error\\s+\"([^\"]*)\"' in both message-reader helpers before the first task commit -- caught by the task's own automated verify, not left for a later plan."
  - "Requirement ticking scope: NONE. VPP-02 appears in this plan's frontmatter as the requirement this plan's proof discharges evidence toward, but per the phase's explicit guard (against the Phase-116 4x premature-tick pattern) no requirement checkbox in .planning/REQUIREMENTS.md was ticked by this plan. Only Plan 125-06 may tick VPP-01/02/03."
  - "Two distinct expected-message helper functions (not one parameterized function) per the plan's literal instruction, so the 'exactly one directive' assertion is never reused across the header and the .cpp -- each file carries a genuinely different message."

requirements-completed: []  # Deliberately empty -- this plan authors VPP-02's proof harness but does not discharge the requirement checkbox; only 125-06 ticks it (phase-specific guard against premature multi-plan ticking, Phase 116 precedent).

coverage:
  - id: D1
    description: "One parametrized pytest function compiles AND runs the VPP seam across all four board macro-sets (uno, leonardo, uno328pb, py32f071) in a single run, asserting compile exit 0, zero -Wall -Wextra stderr bytes, run exit 0, and mode=0/result=1 parsed from stdout (never the run exit code)"
    requirement: "VPP-02"
    verification:
      - kind: integration
        ref: "firestarter/tests/test_vpp_seam_manual_on_every_board.py::test_manual_control_on_every_board_macro_set[uno|leonardo|uno328pb|py32f071]"
        status: pass
    human_judgment: false
  - id: D2
    description: "Forced-capability leg (D-03/C-4): compiling src/rurp_vpp.cpp with RURP_HAS_VPP_DAC forced to 1 fails with that file's own #error text, proving the harness is non-vacuous (the header alone cannot reject this value)"
    requirement: "VPP-02"
    verification:
      - kind: integration
        ref: "firestarter/tests/test_vpp_seam_manual_on_every_board.py::test_forced_capability_macro_fails_closed_in_the_source"
        status: pass
    human_judgment: false
  - id: D3
    description: "Unset-and-non-AVR leg (D-08): compiling with neither __AVR__ nor RURP_HAS_VPP_DAC defined fails with the header's own #error text"
    requirement: "VPP-02"
    verification:
      - kind: integration
        ref: "firestarter/tests/test_vpp_seam_manual_on_every_board.py::test_unset_and_non_avr_fails_closed_in_the_header"
        status: pass
    human_judgment: false
  - id: D4
    description: "Drift leg (D-04/C-6): the four hardcoded board macro-sets are kept honest by asserting their real anchors ([env:uno]+board=uno, [env:uno328pb]+board=ATmega328PB, [env:leonardo]+board=leonardo, RURP_PLATFORM_PY32F071=1, RURP_BOARD_NAME=\"py32f071\") are literally present in platformio.ini / CMakeLists.txt -- never anchored on the framework-supplied ARDUINO_AVR_* macros, absent from platformio.ini"
    requirement: "VPP-02"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_vpp_seam_manual_on_every_board.py::test_board_macro_sets_match_the_real_build_config"
        status: pass
    human_judgment: false
  - id: D5
    description: "Build-supplies leg (D-07): platform/py32f071/CMakeLists.txt declares RURP_HAS_VPP_DAC=0, and include/boards/py32f071_rurp_shield.h defines no top-level RURP_HAS_VPP_DAC (regression guard against the Phase 124 hollow-guard shape)"
    requirement: "VPP-02"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_vpp_seam_manual_on_every_board.py::test_build_supplies_the_capability_macro_the_header_only_tests"
        status: pass
    human_judgment: false
  - id: D6
    description: "Dependency-freedom leg (D-02): src/rurp_vpp.cpp's only #include names rurp_vpp.h, turning the standing constraint into something a future edit cannot quietly break"
    requirement: "VPP-02"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_vpp_seam_manual_on_every_board.py::test_seam_source_is_dependency_free"
        status: pass
    human_judgment: false
  - id: D7
    description: "Self-enforcement meta leg: this module's own source contains no pytest.skip call and no @pytest.mark.skipif decorator, keeping the fail-closed compiler resolver from being edited away"
    requirement: "VPP-02"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_vpp_seam_manual_on_every_board.py::test_compiler_is_required_not_optional"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-07-31
status: complete
---

# Phase 125 Plan 02: VPP Seam Manual-Control Harness Summary

**One parametrized pytest module (7 functions / 10 collected cases) proves the VPP seam refuses on all four board macro-sets by compiling-and-running host g++ binaries, non-vacuously via a forced-capability leg that fails only against `src/rurp_vpp.cpp`'s own `#error`, plus a drift leg anchored on values measured to be literally present in `platformio.ini`/`CMakeLists.txt`.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-07-31
- **Tasks:** 2 (Task 1: four board legs + two guard legs, 6 cases; Task 2: drift + build-supplies + dependency-freedom + no-skip legs, +4 cases)
- **Files modified:** 1 new file in the firmware submodule (`firestarter/tests/test_vpp_seam_manual_on_every_board.py`); 1 new SUMMARY in the meta repo

## Accomplishments

- Authored `firestarter/tests/test_vpp_seam_manual_on_every_board.py`: 7 test functions collecting **10 cases**, verified via `--collect-only -q`.
- Parametrize ids for the single board-legs function: `uno`, `leonardo`, `uno328pb`, `py32f071` — all four in one function, matching ROADMAP Criterion 2's "single parametrized test... in one run".
- Non-vacuity proven the way D-03/C-4 requires: the forced-capability leg compiles `src/rurp_vpp.cpp` itself (not the header alone) with `RURP_HAS_VPP_DAC` forced to 1, and fails with that file's own `#error` text.
- Fixed a regex mismatch discovered while running Task 1's own verify: `include/rurp_vpp.h`'s `#error` directive is written as `#    error "..."` (indented inside nested `#if` arms), not the pinmap precedent's flush `#error "..."`. The pattern `r'#\s*error\s+"([^"]*)"'` (tolerating the whitespace) was applied in both message-reader helpers before the task's commit — caught by the task's own `<verify>` step, not deferred.
- `pytest tests/ -q` moved **72 → 78** after Task 1 and **78 → 82** after Task 2, both re-measured (never assumed) immediately before each commit.
- `tests/test_checker_convention.py` re-confirmed unchanged at `FLOOR = 5` / `FIXTURE_FLOOR = 10` (7 passed) — this module lives under `tests/`, invisible to the checker-convention glob, per RESEARCH C-11.
- The dependency-freedom leg was confirmed to be a real (non-vacuous) assertion by manually pointing its extraction logic at `src/proms/not_implemented.cpp` instead of the seam source: it found 4 `#include` directives (`not_implemented.h`, `firestarter.h`, `logging_id.h`, `messages.h`) against the expected 1, producing the failure `expected exactly one #include directive, got 4: [...]` — proving the leg can fail, not just pass.
- The self-enforcement leg's needle strings (`"pytest" + ".skip"`, `"mark" + ".skipif"`) were independently re-searched against the committed file with a standalone script (not the leg's own code path): zero hits for either concatenated string, confirming the leg is not passing vacuously against its own text.

## Task Commits

1. **Task 1: The four board legs plus the two guard legs** — `93e62fa` (test, firmware repo `/workspaces/firestarter`)
2. **Task 2: The drift, build-supplies, dependency-freedom and no-skip legs** — `9c11f63` (test, firmware repo `/workspaces/firestarter`)

**Plan metadata:** meta-repo commit for this SUMMARY + STATE.md + ROADMAP.md (see final commit below).

## Files Created/Modified

- `firestarter/tests/test_vpp_seam_manual_on_every_board.py` — new, 7 functions / 10 collected cases (322 lines after both tasks)

## The Six Compile/Run Legs, Verbatim (independently re-run outside pytest to record exact figures)

| Leg | Defines | Compile exit | stderr bytes | Run exit | stdout |
|---|---|---:|---:|---:|---|
| uno | `-D__AVR__ -DARDUINO_AVR_UNO -DRURP_BOARD_NAME="uno" -DSERIAL_ON_IO` | 0 | 0 | 0 | `mode=0 result=1` |
| leonardo | `-D__AVR__ -DARDUINO_AVR_LEONARDO -DRURP_BOARD_NAME="leonardo" -DDATA_BUFFER_SIZE=1024` | 0 | 0 | 0 | `mode=0 result=1` |
| uno328pb | `-D__AVR__ -DARDUINO_AVR_ATmega328PB -DRURP_BOARD_NAME="uno328pb" -DSERIAL_ON_IO` | 0 | 0 | 0 | `mode=0 result=1` |
| py32f071 | `-DRURP_PLATFORM_PY32F071=1 -DRURP_HAS_VPP_DAC=0 -DRURP_BOARD_NAME="py32f071"` | 0 | 0 | 0 | `mode=0 result=1` |
| forced-DAC (compiling `src/rurp_vpp.cpp`) | `-D__AVR__ -DRURP_HAS_VPP_DAC=1` | **1** | n/a | n/a | stderr: `src/rurp_vpp.cpp:21:2: error: #error "RURP_HAS_VPP_DAC=1 selects a closed-loop VPP DAC implementation that this branch does not provide"` |
| unset-and-non-AVR | (none) | **1** | n/a | n/a | stderr: `include/rurp_vpp.h:66:6: error: #error "RURP_HAS_VPP_DAC must be supplied by the board/platform build (for py32f071: platform/py32f071/CMakeLists.txt's target_compile_definitions), not by this header."` |

All four board legs produced **zero** bytes of `-Wall -Wextra` compiler warning output. mode=0 is `RURP_VPP_CONTROL_MANUAL`; result=1 is `RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED`.

## The Two `#error` Messages, As Read Out Of Their Files At Test Time

- `include/rurp_vpp.h:66` — `"RURP_HAS_VPP_DAC must be supplied by the board/platform build (for py32f071: platform/py32f071/CMakeLists.txt's target_compile_definitions), not by this header."`
- `src/rurp_vpp.cpp:21` — `"RURP_HAS_VPP_DAC=1 selects a closed-loop VPP DAC implementation that this branch does not provide"`

Neither message is hardcoded as a literal anywhere in the test module — both are read back via `_expected_header_error_text()` / `_expected_source_error_text()`, each scoped to its own file with its own "exactly one directive" assertion.

## The Exact Anchor Set The Drift Leg Asserts

Three AVR anchors (in `platformio.ini`): `[env:uno]` + `board = uno`; `[env:uno328pb]` + `board = ATmega328PB`; `[env:leonardo]` + `board = leonardo`. Two ARM anchors (in `platform/py32f071/CMakeLists.txt`'s `target_compile_definitions`): `RURP_PLATFORM_PY32F071=1`; `RURP_BOARD_NAME="py32f071"`. All five confirmed present by the passing leg; none is `ARDUINO_AVR_UNO`/`_LEONARDO`/`_ATmega328PB` (RESEARCH C-6 — those come from the framework/board JSON and appear nowhere in `platformio.ini`).

## Dependency-Freedom Leg Failure Confirmation

File used to confirm the leg can genuinely fail: `src/proms/not_implemented.cpp` (4 `#include` directives: `not_implemented.h`, `firestarter.h`, `logging_id.h`, `messages.h`). Observed failure message when the leg's extraction regex was pointed at that file instead of `src/rurp_vpp.cpp`: `expected exactly one #include directive, got 4: ['not_implemented.h', 'firestarter.h', 'logging_id.h', 'messages.h']`. This confirms the assertion is load-bearing, not vacuously true for any input.

## `FLOOR` / `FIXTURE_FLOOR` — Confirmed Unchanged

`tests/test_checker_convention.py`: `FLOOR = 5` (line 123), `FIXTURE_FLOOR = 10` (line 124) — both unchanged, 7 passed. This module lives under `tests/`, never `scripts/check_*.py`, so BASE-08's convention glob (scoped to `scripts/` only) never sees it (RESEARCH C-11).

## `pytest tests/` Before / After

- Before this plan (post-125-01): **72 passed**.
- After Task 1 (6 new cases): **78 passed**, re-measured immediately before the Task 1 commit.
- After Task 2 (4 more new cases): **82 passed**, re-measured immediately before the Task 2 commit and again as a final check after both commits.

## Module Totals (from `--collect-only -q`)

- **10 collected cases** from **7 test functions**: `test_manual_control_on_every_board_macro_set` (parametrized ×4: `uno`, `leonardo`, `uno328pb`, `py32f071`), `test_forced_capability_macro_fails_closed_in_the_source`, `test_unset_and_non_avr_fails_closed_in_the_header`, `test_board_macro_sets_match_the_real_build_config`, `test_build_supplies_the_capability_macro_the_header_only_tests`, `test_seam_source_is_dependency_free`, `test_compiler_is_required_not_optional`.

## Decisions Made

- **Regex fix for the indented `#error` directive.** `include/rurp_vpp.h`'s guard is nested two levels deep (`#if !defined(...)` → `#if defined(__AVR__)` → `#else` → `#error`), so the preprocessor line is `#    error "..."`, not a flush `#error "..."` like the pinmap precedent's fragment header. The pinmap-copied regex `r'#error\s+"([^"]*)"'` missed this on first run; fixed to `r'#\s*error\s+"([^"]*)"'` in both message-reader helpers, caught by Task 1's own automated `<verify>` before the commit (not a deviation carried past a task boundary).
- **Two distinct message-reader helpers, not one parameterized function.** Per the plan's literal instruction, `_expected_header_error_text()` and `_expected_source_error_text()` are separate functions, each scoped to its own file's "exactly one directive" assertion — the header and the `.cpp` carry two genuinely different messages, and a shared helper risked the wrong file's text silently satisfying the wrong assertion.
- **No requirement ticked.** Per the phase's explicit scope guard, this plan does not tick VPP-01, VPP-02, or VPP-03 in `.planning/REQUIREMENTS.md` — only Plan 125-06 may do that.

## Deviations from Plan

**1. [Rule 1 - Bug] Fixed the `#error` message regex to tolerate the header's indented directive**
- **Found during:** Task 1, running the task's own `<verify>` command for the first time.
- **Issue:** The regex copied from the pinmap precedent (`r'#error\s+"([^"]*)"'`) assumed a flush `#error "..."` directive. `include/rurp_vpp.h`'s directive is written as `#    error "..."` inside nested preprocessor arms, so the pattern found zero matches and `test_unset_and_non_avr_fails_closed_in_the_header` failed at the `_expected_header_error_text()` call (an `assert m` failure, not a false pass).
- **Fix:** Changed the pattern in both `_expected_header_error_text()` and `_expected_source_error_text()` to `r'#\s*error\s+"([^"]*)"'`, which tolerates arbitrary whitespace between `#` and `error` without weakening the "exactly one directive" check.
- **Files modified:** `firestarter/tests/test_vpp_seam_manual_on_every_board.py`.
- **Verification:** `python3 -m pytest tests/test_vpp_seam_manual_on_every_board.py -q` went from `1 failed, 5 passed` to `6 passed`.
- **Committed in:** `93e62fa` (fix applied before the Task 1 commit, not a separate commit).

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug, caught by the task's own automated verify before committing).
**Impact on plan:** No scope creep; the fix is scoped entirely to the test module's own regex and does not touch the seam files landed by 125-01.

## Known Stubs

None. This plan authors test code only; there is no UI or downstream consumer, and no hardcoded empty value flows to any rendering layer.

## Threat Flags

None. This plan's threat model (see `125-02-PLAN.md` `<threat_model>`) is fully addressed: T-125-08 (result-as-exit-code) is mitigated by parsing from stdout with an explicit acceptance criterion forbidding any run-returncode-vs-result comparison (confirmed by code inspection: no such comparison exists anywhere in the module); T-125-09 (vacuous forced-capability leg) is mitigated by compiling `src/rurp_vpp.cpp` itself and asserting that file's own message; T-125-10 (silent skip) is mitigated by the fail-closed `_resolve_compiler()` plus the self-enforcement leg (independently re-confirmed via a standalone needle search); T-125-11 (drift) is mitigated by the drift leg anchored on RESEARCH-measured-present values; T-125-12 (board-header regression) is mitigated by Leg 5's second half; T-125-13 (overclaiming four independent per-board facts) is mitigated by the module docstring's explicit bound; T-125-14 (landing as `scripts/check_*.py`) is avoided by construction (the module lives under `tests/`, confirmed against `FLOOR`/`FIXTURE_FLOOR` staying unchanged). No new security-relevant surface was introduced — this plan adds test code only, exercising the already-landed 125-01 seam.

## Issues Encountered

None beyond the regex fix documented above under Deviations, which was caught and resolved within Task 1 before its commit.

## User Setup Required

None — no external service configuration required.

## Claim Ceiling Compliance

This SUMMARY makes no claim that the firmware runs on a PY32F071, that closed-loop VPP works, that the pin map is correct/verified/validated, or an unqualified bench-validated/hardware-validated/silicon-verified claim. AVR manual VPP control is not described as provisional or "for now" anywhere in this document or the module it describes. No PY32F071 hardware exists; the py32f071 leg in this module proves a host-compiled macro-set resolves to manual control at compile-and-run time on the host, nothing about silicon. Per the module's own docstring, the four board legs prove uniformity across one compiler-supplied AVR fact plus one explicit ARM declaration, not four independent per-board facts — this document does not imply more than that.

## Next Phase Readiness

- VPP-02's proof harness is committed and green (10/10 passing, 82/82 in the full `tests/` suite). Plan 125-03 (PR #45 non-ancestry gate) can proceed in parallel (Wave 2, same firmware repo, disjoint file).
- Plan 125-04 (three cold AVR builds + non-vacuity measurement) is unaffected by this plan — no production file was touched, only a new test module was added.
- No blockers. `check_cmake_manifest.py` remains at 24 enforced sources (unaffected, sanity-checked); `tests/test_checker_convention.py` remains green at `FLOOR=5`/`FIXTURE_FLOOR=10`.
- Requirement VPP-02 remains unticked in `.planning/REQUIREMENTS.md`, as required — reserved for Plan 125-06's closing sweep.

---
*Phase: 125-vpp-control-seam*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `firestarter/tests/test_vpp_seam_manual_on_every_board.py`
- FOUND: firmware commit `93e62fa` (`git log --oneline --all` in `/workspaces/firestarter`)
- FOUND: firmware commit `9c11f63` (`git log --oneline --all` in `/workspaces/firestarter`)
- FOUND: `/workspaces/.planning/phases/125-vpp-control-seam/125-02-SUMMARY.md`
