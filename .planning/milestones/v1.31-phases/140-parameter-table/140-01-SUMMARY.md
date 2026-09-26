---
phase: 140-parameter-table
plan: 01
subsystem: firmware
tags: [eprom, progmem, avr, platformio, cmake, protocol-dispatch, fail-closed]

# Dependency graph
requires:
  - phase: 138-preconditions-baseline
    provides: frozen native_trace_v131 fixture (5 cases/1 suite), size_baseline_v131.json AVR/native figures, F-138-02/F-138-05 findings
provides:
  - "eprom_params_t: const, protocol_id-keyed, six-column parameter type (firestarter/include/eprom_params.h)"
  - "EPROM_PARAM_KEYS[]/EPROM_PARAMS[] PROGMEM tables + eprom_params_for() fail-closed linear-scan accessor (firestarter/src/proms/eprom_params.cpp)"
  - "140-PREDICTIONS.md: pre-measurement P1-P5 predictions, committed before any cold measurement, reconciled against zero-contradiction Observed data"
affects: [140-04-native-params-test, 140-05-citations-sidecar, 141-per-byte-program-loop, 144-close-reconciliation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "PROGMEM protocol_id-keyed const table + linear-scan accessor returning NULL on no match (no switch, no default row)"
    - "Predict-then-commit-then-measure ordering for GC-sensitive flash-delta claims (140-PREDICTIONS.md)"

key-files:
  created:
    - firestarter/include/eprom_params.h
    - firestarter/src/proms/eprom_params.cpp
    - .planning/phases/140-parameter-table/140-PREDICTIONS.md
  modified:
    - firestarter/platform/py32f071/CMakeLists.txt

key-decisions:
  - "0x07 overprogram_factor = 0 (locked, operator-decided 2026-08-09) shipped verbatim, not the RESEARCH.md example's superseded 3"
  - "eprom_params.cpp registered in FIRESTARTER_COMMON_SOURCES (PY32F071 CMake manifest) alongside its sibling eprom.cpp, not PY32_EXCLUDED -- it has no AVR-specific dependency and every existing src/proms/*.cpp is already a common source"

patterns-established:
  - "Pattern 1: dependency-free header (stdint.h + rurp_platform_compat.h only) keeps a new src/proms/*.cpp TU at zero added native-build warnings against a zero-headroom watermark"
  - "Pattern 2: a comment containing a glob like src/proms/*.cpp trips -Wcomment (literal '/*' substring) -- spell it as prose instead"

requirements-completed: []

coverage:
  - id: D1
    description: "Const, protocol_id-keyed PROGMEM table with exactly three rows (0x07/0x08/0x0B) and six columns (no pulse-width column), values matching the plan's locked_values table cell-for-cell, with a NULL-returning fail-closed accessor"
    verification:
      - kind: other
        ref: "cd firestarter && pio run -e uno (SUCCESS, flash 23954/ram 1573 -- byte-identical to size_baseline_v131.json); ad-hoc g++ program linking eprom_params.cpp dumped all three rows and confirmed exact locked values (0x07 overprogram_factor=0, 0x0B max_pulses=255/energy_cap_us=50000) plus eprom_params_for(0x0C)==NULL"
        status: pass
    human_judgment: false
  - id: D2
    description: "The new translation unit adds ZERO build warnings to native and native_nodevtools (cold)"
    verification:
      - kind: other
        ref: "rm -rf .pio/build/native && pio test -e native; rm -rf .pio/build/native_nodevtools && pio test -e native_nodevtools; scripts/check_build_warnings.py --log native=/tmp/140-01-native.log --log native_nodevtools=/tmp/140-01-nodev.log -> PASS total warnings=1166 (== watermark) both envs, exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "140-PREDICTIONS.md (P1-P5) committed to the meta repo before any cold measurement, then reconciled against Observed cold data with zero contradictions"
    verification:
      - kind: other
        ref: "git log -1 --format=%cI a2705cfb -> 2026-08-10T00:13:30Z, precedes native pio test start 00:13:53Z and native_nodevtools start 00:15:54Z; Observed section in .planning/phases/140-parameter-table/140-PREDICTIONS.md names commit a2705cfb and both run timestamps"
        status: pass
    human_judgment: false
  - id: D4
    description: "src/proms/eprom.cpp left byte-unchanged (D-10) and the firmware Python gate suite (227 tests, including the PY32F071 CMake manifest gate this plan's new file tripped and the executor fixed) stays green"
    verification:
      - kind: other
        ref: "git -C firestarter diff --quiet -- src/proms/eprom.cpp (exit 0); pio test -e native_trace_v131 -> 5 test cases: 5 succeeded; python3 -m pytest tests/ -q -> 227 passed; python3 scripts/check_cmake_manifest.py -> PASS exit 0"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-08-10
status: complete
---

# Phase 140 Plan 01: Parameter Table Summary

**PROGMEM `eprom_params_t` table (0x07/0x08/0x0B, six columns, no pulse-width) with a fail-closed linear-scan accessor, plus pre-measurement predictions committed before any cold flash/warning capture -- both landed with zero AVR flash/RAM delta and zero added native warnings.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-08-10T00:03:24Z
- **Completed:** 2026-08-10T00:24:52Z
- **Tasks:** 3 (as planned)
- **Files modified:** 4 (3 planned + 1 deviation fix)

## Accomplishments

- Shipped `firestarter/include/eprom_params.h`: dependency-free (`<stdint.h>` + `rurp_platform_compat.h` only), `eprom_params_t` with the six frozen columns in the required largest-first order (`sizeof == 12`, `static_assert`-checked), `VERIFY_PER_PULSE(_PLUS_FINAL)` / `VPP_PATH_DROP_RESISTOR` / `VPP_PATH_DIRECT_VPE` enums, and the `eprom_params_for()` declaration.
- Shipped `firestarter/src/proms/eprom_params.cpp`: `EPROM_PARAM_KEYS[]` / `EPROM_PARAMS[]` PROGMEM tables and a linear-scan `eprom_params_for()` that returns `NULL` on no match — no `switch`, no default row.
- **Exact row values shipped** (locked_values table, verified cell-for-cell via a standalone compiled dump):

  | protocol | overprogram_cap_us | energy_cap_us | max_pulses | overprogram_factor | verify_mode | vpp_path |
  |---|---|---|---|---|---|---|
  | `0x07` | 75000 | 0 | 25 | **0** | `VERIFY_PER_PULSE_PLUS_FINAL` (1) | `VPP_PATH_DROP_RESISTOR` (0) |
  | `0x08` | 75000 | 0 | 25 | 0 | `VERIFY_PER_PULSE_PLUS_FINAL` (1) | `VPP_PATH_DROP_RESISTOR` (0) |
  | `0x0B` | 75000 | 50000 | 255 | 0 | `VERIFY_PER_PULSE` (0) | `VPP_PATH_DIRECT_VPE` (1) |
  | `0x0C` (unrecognised) | — | — | — | — | — | `eprom_params_for(0x0C) == NULL` |

  `0x07`'s `overprogram_factor = 0` is the locked, operator-decided value — NOT the RESEARCH.md
  example's superseded `3`. The 22-part Intel-family divergence (F-140-05) is named in the TU's
  own comment block, immediately above `EPROM_PARAMS[]`.
- Committed `.planning/phases/140-parameter-table/140-PREDICTIONS.md` (P1-P5, mechanical basis
  for each) to the meta repo at commit `a2705cfb02d848ab1d927da0b784f959300cc4ab`
  (`2026-08-10T00:13:30Z`) **before** running the cold `native`/`native_nodevtools` captures, then
  appended an "Observed (Plan 01, cold)" section naming that commit and recording the results —
  every prediction matched its observation exactly; no contradiction was found or needed recording.
- **Cold measurement results, verbatim:**
  - `native`: 141 test cases: 141 succeeded, 17 suites (summary-table count), warnings
    macro_redefinition=1166 / total=1166.
  - `native_nodevtools`: 141 test cases: 141 succeeded, 17 suites, warnings
    macro_redefinition=1166 / total=1166.
  - `scripts/check_build_warnings.py` PASS line: `native: total warnings=1166 (== watermark
    1166), native_nodevtools: total warnings=1166 (== watermark 1166)`, exit 0.
  - `native_trace_v131` (Task 2): `5 test cases: 5 succeeded`, 1 suite, PASSED.
  - AVR `uno` (Task 2): `pio run -e uno` SUCCESS; flash 23954/32256, RAM 1573/2048 —
    byte-identical to `scripts/baseline/size_baseline_v131.json`'s recorded `uno` figures (0 delta).
- Confirmed `src/proms/eprom.cpp` is byte-unchanged: `git -C firestarter diff --quiet -- src/proms/eprom.cpp` exits 0 (D-10 preserved).

## Task Commits

Each task was committed atomically (Task 3 required two commits by design — the plan's own
gate requires the predictions commit to precede the cold measurement in git history):

1. **Task 1: Author include/eprom_params.h** — `9914c8f` (feat, firestarter)
2. **Task 2: Author src/proms/eprom_params.cpp** — `79b2d8e` (feat, firestarter)
3. **Task 3a: Commit predictions BEFORE measuring** — `a2705cfb` (docs, meta repo)
4. **Task 3b: Append Observed section after cold measurement** — `46a01ce0` (docs, meta repo)
5. **Deviation fix (Rule 3, discovered while completing Task 3's overall verification pass)** — `3207632` (fix, firestarter): register `eprom_params.cpp` in the PY32F071 CMake manifest

**Plan metadata:** this SUMMARY's own commit (docs: complete plan) — see final commit below.

_Note: Task 3 has two commits by the plan's own explicit design (predictions must precede
measurement in git history, provably); this is not a TDD RED/GREEN split._

## Files Created/Modified

- `firestarter/include/eprom_params.h` (new, 84 lines) — `eprom_params_t` type, `VERIFY_*` /
  `VPP_PATH_*` enums, `eprom_params_for()` declaration, `static_assert(sizeof==12)`.
- `firestarter/src/proms/eprom_params.cpp` (new, 62 lines) — `EPROM_PARAM_KEYS[]` /
  `EPROM_PARAMS[]` PROGMEM tables, `eprom_params_for()` linear-scan accessor.
- `.planning/phases/140-parameter-table/140-PREDICTIONS.md` (new, 170 lines) — P1-P5
  pre-measurement predictions + Observed (cold) reconciliation section.
- `firestarter/platform/py32f071/CMakeLists.txt` (modified, +1 line) — registered
  `src/proms/eprom_params.cpp` in `FIRESTARTER_COMMON_SOURCES`, next to `eprom.cpp`.

## Decisions Made

- Followed the plan's locked `<locked_values>` table exactly — did not copy 140-RESEARCH.md's
  superseded `0x07 overprogram_factor = 3` example.
- `vpp_path` and `verify_mode` implemented as plain anonymous enums (values 0/1), not
  `rurp_register_t` masks — keeps the header dependency-free per the plan's explicit instruction
  (Phase 142 owns the mask sets).
- Comment banners describe the no-`<Arduino.h>`/no-`rurp_shield.h` constraint in prose rather than
  spelling those literal filenames, to satisfy the task's own acceptance criteria that the header
  contain zero occurrences of those strings anywhere, including comments.
- **Deviation decision:** registered `eprom_params.cpp` in the PY32F071 ARM manifest
  (`FIRESTARTER_COMMON_SOURCES`) rather than `PY32_EXCLUDED` — every one of the 9 pre-existing
  `src/proms/*.cpp` files is already a common source, none is excluded, and the new file has no
  AVR-specific dependency (its only non-stdlib include, `rurp_platform_compat.h`, already takes
  the generic non-`__AVR__` path that a non-Arduino host build exercises, which this plan directly
  proved compiles clean via a standalone `g++` build).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a `-Wcomment` warning-trap in `eprom_params.cpp`'s own banner text**
- **Found during:** Task 2, immediately after writing the file (pre-commit `g++ -Wall -Wextra` check)
- **Issue:** A banner comment referenced `src/proms/*.cpp` (a glob), and the two characters `/*`
  inside that glob (from `proms/*.cpp`) are a literal "nested comment start" sequence GCC's
  `-Wcomment` flags — which would have been a genuine added warning on the native build against a
  watermark with zero headroom (critical hazard #1), silently invalidating the P3 prediction before
  it was even written.
- **Fix:** Reworded the sentence to "the only other translation unit under src/proms/" (no glob).
- **Files modified:** `firestarter/src/proms/eprom_params.cpp`
- **Verification:** `g++ -std=gnu++17 -Wall -Wextra -I include -c src/proms/eprom_params.cpp`
  produces zero warnings (re-confirmed after the edit, before commit); cold `native` /
  `native_nodevtools` captures later confirmed 1166/1166 (unchanged watermark).
- **Committed in:** `79b2d8e` (fixed pre-commit; never landed in git history as a warning)

**2. [Rule 3 - Blocking] Registered the new TU in the PY32F071 CMake manifest**
- **Found during:** Task 3, while running the plan's own overall `<verification>` step
  (`python3 -m pytest tests/ -q`), which the plan states should report "227 passed (unchanged)"
- **Issue:** `tests/test_check_cmake_manifest.py::test_armed_and_passing_on_the_real_tree` failed:
  `scripts/check_cmake_manifest.py`'s reverse-omission check requires every `.cpp`/`.c` file under
  `src/` to be either named in `platform/py32f071/CMakeLists.txt`'s `FIRESTARTER_COMMON_SOURCES` or
  covered by a reasoned `# PY32_EXCLUDED:` comment. This pre-existing gate (Phase 123/124, BASE-04)
  is not named anywhere in 140-CONTEXT.md / 140-PATTERNS.md / 140-RESEARCH.md / 140-VALIDATION.md —
  the new file was an unnamed omission the moment it landed in `src/proms/`.
- **Fix:** Added `"${REPOSITORY_ROOT}/src/proms/eprom_params.cpp"` to `FIRESTARTER_COMMON_SOURCES`,
  immediately after its sibling `eprom.cpp` line — not `PY32_EXCLUDED`, because every one of the 9
  pre-existing `src/proms/*.cpp` files is already a common source (none is excluded) and the new
  file is architecturally portable (dependency-free; its one include, `rurp_platform_compat.h`,
  already takes the generic non-AVR code path a non-Arduino build needs, proven by this plan's own
  standalone `g++` compile in Task 2).
- **Files modified:** `firestarter/platform/py32f071/CMakeLists.txt`
- **Verification:** `python3 scripts/check_cmake_manifest.py` → `PASS ... 27 enforced source(s)
  resolved ... allow-listed omission(s): [same 5 pre-existing entries, none new]`, exit 0.
  `python3 -m pytest tests/ -q` → `227 passed` (tree clean, matching the plan's own overall
  verification requirement exactly). This is a purely textual gate (`cmake`/`arm-none-eabi-gcc`
  are absent from this devcontainer by the gate's own design) — no ARM compilation was attempted
  or claimed.
- **Committed in:** `3207632` (separate commit, since Tasks 1-2 were already committed when this
  was discovered during Task 3's wrap-up)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Both fixes were required for correctness against pre-existing, unrelated live
gates that the plan text did not anticipate. Neither changes any row value, any AVR/native
size/warning/suite figure already recorded in `140-PREDICTIONS.md`, or any file in this plan's
declared `files_modified` list beyond the one necessary manifest line. No scope creep.

## Issues Encountered

**Ordering nuance, stated rather than smoothed (not treated as a violation, but worth naming
per this project's own "name the divergence" convention):** Task 2's `pio run -e uno` build-success
check (required by the plan's own Task 2 acceptance criteria) unavoidably prints PlatformIO's
standard `RAM:`/`Flash:` usage summary as console output, which happened to read 23954/1573 bytes
— byte-identical to the already-published `size_baseline_v131.json` figures — chronologically
before the Task 3 predictions commit (`a2705cfb`, 00:13:30Z) landed. This is **not** the "AVR delta
measurement" the plan's critical hazard #6 and must-have truth guard against: no formal delta was
computed (`scripts/check_size_baseline.py` was never invoked in this plan, by design — the plan's
own `<verification>` block and Task 3's action text scope the cold-measurement discipline to the
two *native* envs only; the formal AVR `--policy merge05` gate run is Wave 3 / a later plan's
concern per `140-VALIDATION.md`'s Per-Task Verification Map). The P1/P2 prediction *text* itself
was derived purely from the structural gc-sections argument (confirmed in-session by reading
`arduino.py` lines 98/99/111 directly) before any byte count was observed, so no hindsight
adjustment occurred — but the raw byte-count observation's timing relative to the predictions
commit is disclosed here for full transparency rather than left implicit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `eprom_params_t`, `eprom_params_for()`, and the three-row table exist, compile cleanly on `uno`
  and on both pinned native envs, and are ready for Phase 141 to wire into `configure_eprom` — by
  design, nothing in `src/` references them yet (D-10), so they are correctly and expectedly
  invisible to the AVR-compiled surface's flash usage today. This is not a stub: the data and
  accessor are complete and correct; only the caller is deferred, exactly as the phase record
  states.
- `140-PREDICTIONS.md` P1/P2 (AVR flash/RAM delta ≈0) are the pre-committed hypothesis Phase 141's
  own flash-delta measurement should be read against; P5 remains unobserved until plan 140-04
  creates `native_params_v131`.
- This plan marks no requirement checkbox Complete, per its own `<requirement_completion>` scope —
  TABLE-01 spans 140-01/140-04/140-05, TABLE-02 spans 140-01/140-05; only 140-07 may flip either
  checkbox in `.planning/REQUIREMENTS.md`.
- No blockers for plans 140-02 through 140-07.

---
*Phase: 140-parameter-table*
*Completed: 2026-08-10*

## Self-Check: PASSED

Files verified present on disk:
- FOUND: `firestarter/include/eprom_params.h`
- FOUND: `firestarter/src/proms/eprom_params.cpp`
- FOUND: `.planning/phases/140-parameter-table/140-PREDICTIONS.md`
- FOUND: `.planning/phases/140-parameter-table/140-01-SUMMARY.md`
- FOUND: `eprom_params.cpp` registered in `firestarter/platform/py32f071/CMakeLists.txt`

Commits verified present in git history:
- FOUND (firestarter): `9914c8f`, `79b2d8e`, `3207632`
- FOUND (meta): `a2705cfb`, `46a01ce0`, `3467af4a`
