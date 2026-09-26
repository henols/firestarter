---
phase: 123-non-regression-baselines-gate-hardening
plan: 03
subsystem: build-warning-gate
tags: [platformio, gcc, warnings, baseline, watermark, firmware-repo]

requires:
  - phase: 123-non-regression-baselines-gate-hardening (plan 01)
    provides: firestarter/scripts/baseline/size_baseline.json's warnings block (avr 0/0/0, native 360/360) + captured fixtures
  - phase: 123-non-regression-baselines-gate-hardening (plan 02)
    provides: check_size_baseline.py's ParseError/PASS/FAIL/exit-taxonomy shape and FIRESTARTER_SIZE_BASELINE seam name, mirrored here
provides:
  - "firestarter/scripts/check_build_warnings.py — BASE-06 gate: AVR exact-zero macro-redefinition rule + native 360-warning watermark, exit 0/1/2"
  - "firestarter/tests/test_check_build_warnings.py — 10-test anti-hollow pairing, proven against a real host g++ compile and real pio test framing"
  - "4 committed fixtures under firestarter/tests/fixtures/: 2 compiled .cpp sources, 2 derived logs"
affects:
  - "123-06 (convention meta-test: check_build_warnings.py joins the firestarter/scripts/check_*.py population)"
  - "123-11 (evidence artifact cites this gate's invocation; also where BASE-06/BASE-08 actually tick)"
  - "Phase 124 (any BASE-06 wiring into CI reads this script)"

tech-stack:
  added: []
  patterns:
    - "Tail-anchored MACRO_REDEF_RE (no :line:col: prefix) so gcc 7.3 vs gcc 14 column-format differences never narrow the match"
    - "AVR exact-zero (==) vs native watermark (<=) as two branches of one check_env() function reading one shared baseline JSON"
    - "Compiler resolved fail-closed via shutil.which(os.environ.get('CXX', 'g++')) — assert, never skip"

key-files:
  created:
    - firestarter/scripts/check_build_warnings.py
    - firestarter/tests/test_check_build_warnings.py
    - firestarter/tests/fixtures/planted_build_warnings_macro_redef.cpp
    - firestarter/tests/fixtures/clean_build_warnings_no_redef.cpp
    - firestarter/tests/fixtures/planted_build_warnings_avr_redef.log
    - firestarter/tests/fixtures/planted_build_warnings_native_excess.log
  modified: []

key-decisions:
  - "AVR FAIL messages name the offending macro(s) (e.g. 'names=PSTR'), not just counts — added during Task 3 (Rule 1) because the end-to-end coverage test needs the macro named in the gate's own output, and it is useful in any real CI failure regardless"
  - "planted_build_warnings_native_excess.log required 361 appended synthetic lines, not 'a small number' as the plan's task text assumed, because captured_test_native_summary.log (123-01's truncated SUMMARY-tail capture) itself carries 0 warning lines, not a near-360 base — documented as a deviation"
  - "PlatformIO-invisibility for the two new .cpp fixtures verified via test_filter entry counts (17 for each native env) and an absence grep for both fixture filenames in platformio.ini, not via 'pio test --list-tests', which was measured this session to enumerate ALL directories under test/native/avr/ (18, including the pre-existing, filter-excluded test_flash_intel_vpp) regardless of test_filter — an unreliable proxy for what pio actually runs"

requirements-completed: []

coverage:
  - id: D1
    description: "check_build_warnings.py holds AVR at exact-zero macro-redefinition warnings and native at the recorded 360 watermark, reading one shared baseline JSON via FIRESTARTER_SIZE_BASELINE"
    requirement: "BASE-06"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_build_warnings.py#test_avr_clean_controls_pass_all_three_envs"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_build_warnings.py#test_avr_exact_zero_fires_on_planted_redefinition"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_build_warnings.py#test_native_watermark_fires_on_planted_excess"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_build_warnings.py#test_native_clean_control_passes_at_its_actual_watermark"
        status: pass
    human_judgment: false
  - id: D2
    description: "The gate's parser is proven against a real host g++ compile (never avr-g++) and against real pio test framing, closing D-14's recorded gap; a missing compiler fails the suite rather than skipping it"
    requirement: "BASE-08"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_build_warnings.py#test_real_compiler_emits_the_planted_diagnostic"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_build_warnings.py#test_parser_consumes_real_compiler_output_end_to_end"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_build_warnings.py#test_parser_survives_pio_test_framing"
        status: pass
      - kind: other
        ref: "CXX=definitely-not-a-compiler python3 -m pytest tests/test_check_build_warnings.py -q (3 failed, 7 passed — failures, never skips)"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-07-30
status: complete
---

# Phase 123 Plan 03: BASE-06 Build Warning Gate + Anti-Hollow Pytest Summary

**`check_build_warnings.py` holds the three AVR envs at exact-zero macro-redefinition warnings and both native envs at the recorded 360-warning watermark, proven against a real host `g++` compile and real `pio test` framing via a 10-test pytest suite — firmware repo now at 25 passed, 0 skipped.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-07-30T23:25:00Z (approx.)
- **Completed:** 2026-07-30T23:56:19Z
- **Tasks:** 3 completed
- **Files modified:** 6 (1 script, 1 test module, 4 fixtures)

## Accomplishments
- `firestarter/scripts/check_build_warnings.py`: stdlib-only checker, AVR envs held at `macro_redefinition == 0` (exact equality, measured genuinely clean), native envs held at `total_watermark == 360` (`<=`), unknown env and baseline-load failure are configuration errors (exit 2), never-vacuous guard placed before the per-env loop
- Docstring states the 360's cause (8 pgmspace.h macros × 45 native translation units), its pre-existing-not-regression status, and the rejected 17-suite-directory remediation, in prose that survives isolation from the JSON
- `MACRO_REDEF_RE` anchored on the diagnostic tail only (`warning:\s*"(?P<macro>[^"]+)"\s+redefined`), containing no `:line:col:` construct, so gcc 7.3's `:2:0:` and gcc 14's `:2:9:` forms both match
- 4 committed fixtures: `planted_build_warnings_macro_redef.cpp` (compiled, distinctive macro name), `clean_build_warnings_no_redef.cpp` (paired control), `planted_build_warnings_avr_redef.log` (one genuine redefinition inserted into a real uno build log), `planted_build_warnings_native_excess.log` (361 synthetic warning lines over the 360 watermark, 17 SUMMARY rows and the `141 test cases` line intact)
- `tests/test_check_build_warnings.py`: 10 tests covering both halves of D-14 (compiler → parser via a real host `g++` compile; parser → CLI exit code) plus the pio-framing survival test against `captured_native_warnings_excerpt.log`
- Firmware pytest suite: **25 passed, 0 skipped** (8 pre-existing + 7 from 123-02 + 10 here)

## Task Commits

Each task was committed atomically (in the `firestarter` submodule, branch `v1.23-py32f071-integration`):

1. **Task 1: check_build_warnings.py — AVR exact-zero + native watermark** - `7fc07d5` (feat)
2. **Task 2: four warning fixtures — two compiled sources, two derived logs** - `a564a15` (test)
3. **Task 3: anti-hollow pytest, 25 passed** - `2804105` (test) — includes a folded-in Rule 1 fix to `check_build_warnings.py`'s AVR FAIL message

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md update (meta repo commit follows)

## Files Created/Modified
- `firestarter/scripts/check_build_warnings.py` - BASE-06 gate: `MACRO_REDEF_RE`, `WARNING_LINE_RE`, `ParseError`, `check_env`, `main`
- `firestarter/tests/test_check_build_warnings.py` - 10-test anti-hollow pairing
- `firestarter/tests/fixtures/planted_build_warnings_macro_redef.cpp` - compiled fixture, distinctive macro `FIRESTARTER_FIXTURE_MACRO_REDEF_123_03`
- `firestarter/tests/fixtures/clean_build_warnings_no_redef.cpp` - paired clean control
- `firestarter/tests/fixtures/planted_build_warnings_avr_redef.log` - `captured_build_uno.log` + one genuine `PSTR` redefinition line
- `firestarter/tests/fixtures/planted_build_warnings_native_excess.log` - `captured_test_native_summary.log` + 361 synthetic warning lines (363 total)

## Host Compiler Details (for the anti-hollow contract)

- **Observed host `g++` version:** `g++ (Debian 14.2.0-19) 14.2.0`
- **Exact diagnostic text the fixture compile produced:**
  ```
  planted_build_warnings_macro_redef.cpp:14:9: warning: "FIRESTARTER_FIXTURE_MACRO_REDEF_123_03" redefined
     14 | #define FIRESTARTER_FIXTURE_MACRO_REDEF_123_03 2
        |         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  planted_build_warnings_macro_redef.cpp:13:9: note: this is the location of the previous definition
     13 | #define FIRESTARTER_FIXTURE_MACRO_REDEF_123_03 1
        |         ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  ```
- **`MACRO_REDEF_RE` match:** `macro` group == `FIRESTARTER_FIXTURE_MACRO_REDEF_123_03`, matching the fixture's own `#define` name (derived at test time, not hardcoded).

## Observed Exit Codes and Distinctive Substrings Per Planted Case

| Case | Exit code | Distinctive substring |
|---|---:|---|
| 3 clean AVR captures (`uno`/`uno328pb`/`leonardo`) | 0 | `PASS:` + env name + `macro_redefinition=0 (== 0)` |
| `planted_build_warnings_avr_redef.log` (uno) | 1 | `observed=1 rule==(0) names=PSTR` |
| Real-compiler stderr fed through `--log uno=...` (Task 3 coverage 3) | 1 (non-zero) | `FIRESTARTER_FIXTURE_MACRO_REDEF_123_03` named in output |
| `planted_build_warnings_native_excess.log` (native) | 1 | `363` (observed) and `360` (watermark) both present |
| `captured_native_warnings_excerpt.log` at the real 360 watermark | 0 | `INFO: native: total warnings observed=8 is 352 below watermark 360 ...` |
| `captured_test_native_summary.log` against a temp baseline pinned to watermark 0 | 0 | `PASS:` |
| No `--log` / no `--rebuild` | 1 | `no envs examined` |
| `--log nosuchenv=...` | 2 | (no `PASS:`; env name reported via `ERROR:` on stderr) |
| `CXX=definitely-not-a-compiler` forced-missing-compiler run | non-zero (pytest: 3 failed, 7 passed) | `AssertionError: host C++ compiler not found on PATH` — a FAILURE, never a skip |

**Total warning count of `planted_build_warnings_native_excess.log`:** **363** (`grep -c 'warning:'`), against the recorded 360 watermark — 3 over, deliberately small enough to be an unambiguous new-warning signal rather than a coincidental match.

**Firmware suite count:** `python3 -m pytest tests/ -q` → **25 passed, 0 skipped** (matches the plan's expected count: 8 pre-existing + 7 from 123-02 + 10 from this plan).

## D-14 Pio-Framing Gap — Explicitly Closed

**D-14 recorded that the fixture-compile test proves the warning-LINE is parsed correctly, but does not prove the parser survives `pio`'s surrounding framing.** This gap is now closed by `test_parser_survives_pio_test_framing`, which asserts `MACRO_REDEF_RE` finds all 8 real macro-redefinition diagnostics (`PSTR`, `memcpy_P`, `strcpy_P`, `strlen_P`, `pgm_read_byte`, `pgm_read_word`, `pgm_read_dword`, `pgm_read_ptr`) inside the committed `captured_native_warnings_excerpt.log` — real `pio test -e native` output, including its `Processing`/`Building...` preamble, the compiler's own `In file included from ...` chain, and the interleaved `note:` lines that follow every diagnostic — and that `WARNING_LINE_RE` counts exactly 8 lines, undisturbed by that framing.

**Residual limitation, stated explicitly:** `captured_native_warnings_excerpt.log` is a partial capture (8 of the real 360 native warnings, one occurrence per macro), not a full `pio test` run's complete output — 123-01 never committed a full, untruncated native build log carrying all 360 real warnings inline (its `captured_test_native_summary.log` is the SUMMARY-tail only, deliberately truncated). The parser is therefore proven against genuine `pio` framing surrounding real diagnostics, but not against a single real log containing the full 360-warning volume. `planted_build_warnings_native_excess.log` fills the volume-realism gap structurally (17 intact SUMMARY rows, the `141 test cases` line, over-360 total) but its warning content is synthetic, not real compiler output. No further fixture was created to close this residual gap — doing so would require a full clean native rebuild capture, which is out of this plan's scope (the plan's `files_modified` list is fixed to the checker, its test, and 4 named fixtures).

## Decisions Made

1. **AVR FAIL messages name the offending macro(s)** (Rule 1 fix, folded into Task 3's commit). Discovered while writing `test_parser_consumes_real_compiler_output_end_to_end`: the plan's acceptance criteria for that test require "the output names the macro," but the AVR branch of `check_env()` as first written (Task 1) reported only observed/rule counts. Fixed by collecting the distinct matched macro names (capped at 20) into the FAIL message. Verified: `python3 scripts/check_build_warnings.py --log uno=tests/fixtures/planted_build_warnings_avr_redef.log` now prints `names=PSTR`. All of Task 1's original acceptance criteria re-verified passing after the change.
2. **`planted_build_warnings_native_excess.log` needed 361 appended lines, not "a small number."** The plan's Task 2 action text assumed appending "a small number of clearly-synthetic additional warning: lines" to `captured_test_native_summary.log` would suffice to cross the 360 watermark — but that captured file (123-01's SUMMARY-tail-only truncation) carries **0** real warning lines, not a near-360 base. Reaching >360 total therefore required appending the full excess. Documented in both the fixture's own header comment and the test module's docstring, rather than silently padding the file without comment — the same house convention 123-01-SUMMARY.md used for its own truncation-framing correction.
3. **PlatformIO-invisibility verified via `test_filter` entry counts, not `pio test --list-tests`.** Measured this session: `pio test -e native --list-tests` enumerates 18 directories under `test/native/avr/` (all `_shared`-excluded subdirs, including the pre-existing `test_flash_intel_vpp`, which is present on disk but excluded from both native envs' `test_filter` and therefore never actually executed). This is NOT filtered by `test_filter` at listing time, so it is an unreliable proxy for "did the fixture reach a build." Verified instead: both native envs' `test_filter` blocks in `platformio.ini` still list exactly 17 entries each, and neither new `.cpp` fixture's filename appears anywhere in `platformio.ini`. The real `captured_test_native_summary.log` (a genuine prior `pio test` run) independently confirms 17 suites, all PASSED — consistent with the 17-entry `test_filter`, not the 18-directory `--list-tests` enumeration.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug/gap] AVR FAIL message did not name the offending macro**
- **Found during:** Task 3, writing `test_parser_consumes_real_compiler_output_end_to_end`
- **Issue:** Task 1's `check_env()` AVR branch reported only `observed=N rule==(M)` on failure, but the plan's Task 3 acceptance criteria for that test explicitly require "the output names the macro" — a gap between what the checker emitted and what the anti-hollow contract needed to prove.
- **Fix:** Added collection of distinct `MACRO_REDEF_RE` matches (capped at 20, sorted) into the FAIL message, appended as `names=...`.
- **Files modified:** `firestarter/scripts/check_build_warnings.py`
- **Verification:** All of Task 1's original automated acceptance criteria re-run and confirmed still passing; the new coverage-3 test in Task 3 passes against the enhanced message.
- **Committed in:** `2804105` (folded into Task 3's commit, since the fix surfaced while writing that task's pytest)

**2. [Rule 1 - factual premise correction, D-03 spirit] "Small number" of appended lines was not achievable given the real truncated base**
- **Found during:** Task 2, assembling `planted_build_warnings_native_excess.log`
- **Issue:** The plan's action text describes appending "a small number of clearly-synthetic additional warning: lines" to cross the 360 watermark, implicitly assuming the base file already carried a near-360 count. Measured: `captured_test_native_summary.log` (123-01's committed capture) carries exactly 0 `warning:` lines — it is the SUMMARY-table tail only, truncated well after the compile-time warning output per 123-01-SUMMARY.md's own "Native capture truncation point" section.
- **Fix:** Appended 361 synthetic lines (355 macro-redefinition-shaped with distinctive `SYNTHETIC_MACRO_NNNN` names, 6 non-macro unused-variable-shaped) instead of "a small number," documented in both the fixture's header comment and the test module's docstring so the discrepancy is visible to any future reader rather than silently absorbed.
- **Files affected:** `firestarter/tests/fixtures/planted_build_warnings_native_excess.log`, `firestarter/tests/test_check_build_warnings.py` (docstring)
- **Verification:** `grep -c 'warning:' planted_build_warnings_native_excess.log` == 363 (> 360); 17 SUMMARY rows and the `141 test cases` line independently confirmed intact.
- **Committed in:** `a564a15` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 Rule 1 bug/gap, 1 Rule 1 factual-premise correction). Both necessary for the anti-hollow contract to hold as specified; neither is scope creep.
**Impact on plan:** No architectural change; both fixes stay inside this plan's already-declared `files_modified` list.

## Issues Encountered

- Initial draft of the test docstring/comments literally contained the substrings `pytest.mark.skipif`, `pytest.skip`, and `avr-g++` in PROSE explaining why those mechanisms are absent — which broke the plan's own `grep -c` acceptance checks (they count literal substring occurrences, not code usage). Resolved by rephrasing the prose to describe the same intent without using those exact literal tokens (e.g., "any decorator or runtime call that would mark this outcome as skipped" instead of naming `pytest.skip` directly). Re-verified: all four `grep -c` checks (`pytest.mark.skipif`, `pytest.skip`, `platformio/packages`, `avr-g++`) now return 0.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `check_build_warnings.py` and its fixtures are ready to be cited by 123-06's convention meta-test (the `firestarter/scripts/check_*.py` population) and by 123-11's evidence artifact.
- **This plan ticks nothing.** BASE-06 and BASE-08 remain open per the plan's explicit `requirement_closure` — they close only in 123-11, per this plan's own frontmatter instruction.
- No blockers. Firmware repo (`v1.23-py32f071-integration`) is at 25 passed / 0 skipped, working tree clean outside this plan's own commits, `src`/`include`/`platformio.ini`/`.github`/`test` untouched since the recorded fork point.

---
*Phase: 123-non-regression-baselines-gate-hardening*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/scripts/check_build_warnings.py`
- FOUND: `/workspaces/firestarter/tests/test_check_build_warnings.py`
- FOUND: `/workspaces/firestarter/tests/fixtures/planted_build_warnings_macro_redef.cpp`
- FOUND: `/workspaces/firestarter/tests/fixtures/clean_build_warnings_no_redef.cpp`
- FOUND: `/workspaces/firestarter/tests/fixtures/planted_build_warnings_avr_redef.log`
- FOUND: `/workspaces/firestarter/tests/fixtures/planted_build_warnings_native_excess.log`
- FOUND commit `7fc07d5` (feat: check_build_warnings.py)
- FOUND commit `a564a15` (test: four warning fixtures)
- FOUND commit `2804105` (test: anti-hollow pytest, 25 passed)
- Verified: `firestarter` on `v1.23-py32f071-integration`; meta on `gsd/v1.23-py32f071-integration`
- Verified: `python3 -m pytest tests/ -q` → 25 passed, 0 skipped
- Verified: `git status --porcelain` clean in `firestarter` after all three commits
