---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 03
subsystem: firmware
tags: [config-storage, eeprom, avr, py32f071, cmake, seam, refactor]

# Dependency graph
requires:
  - phase: 126-01
    provides: firestarter/platform/py32f071/CONFIG-STORAGE.md and the vendored design (95 pytest total at that point)
  - phase: 126-02
    provides: "tests/test_config_storage_eeprom_regression.py authored against the pre-refactor src/rurp_config_utils.cpp, with its recorded blob SHA 0ef805ff8e915f9321bda5dc50d61b8a8dd26eaf as the D-04 proof target"
provides:
  - "include/rurp_config_storage.h — the two-function byte-blob storage seam (rurp_config_storage_load/save), included by exactly two TUs today (policy + AVR backend); rurp_shield.h not touched"
  - "src/rurp_config_utils.cpp reduced to a policy-only layer: no EEPROM include, no CONFIG_START, no platform conditional; rurp_validate_config byte-identical to pre-refactor"
  - "src/boards/rurp_config_storage_eeprom.cpp — the AVR EEPROM backend, a pure move of CONFIG_START/EEPROM.get/EEPROM.put, both functions returning true unconditionally"
  - "platform/py32f071/CMakeLists.txt's PY32_EXCLUDED set grows 5 -> 6 lines (only the new backend TU added; the rurp_config_utils.cpp exclusion deliberately NOT retired here)"
  - "D-04 discharged via the documented fallback: one named, justified line change to tests/test_config_storage_eeprom_regression.py, both blob SHAs recorded"
affects: [126-04, 126-05, 126-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Storage-seam header pattern (two bool functions over a void*/size_t blob), modelled on include/rurp_vpp.h's extern \"C\" wrapper and include-before-extern-C ordering"
    - "Per-platform backend TU under src/boards/, PY32_EXCLUDED from the ARM manifest, modelled on src/boards/rurp_common.cpp"
    - "Manifest-grouping split: an ARM-manifest edit set can be deliberately spread across multiple plans/commits when landing them together would create an undetectable duplicate-definition window"

key-files:
  created:
    - firestarter/include/rurp_config_storage.h
    - firestarter/src/boards/rurp_config_storage_eeprom.cpp
  modified:
    - firestarter/src/rurp_config_utils.cpp
    - firestarter/platform/py32f071/CMakeLists.txt
    - firestarter/scripts/check_cmake_manifest.py
    - firestarter/tests/test_config_storage_eeprom_regression.py

key-decisions:
  - "D-04's primary proof (recorded blob SHA re-hashes IDENTICAL) did NOT hold unmodified: the plan's own acceptance criteria mandate a three-board #if guard around the new AVR backend TU, and the pre-existing regression test compiles that TU with plain host g++ (no ARDUINO_AVR_* macro defined), which produced an empty translation unit and a link failure. This is exactly the 126-CONTEXT.md Discretion-documented fallback scenario (\"verify this survives contact\"); applied it: one named, justified line change to _compile()'s argv (added -DARDUINO_AVR_UNO), landed in its own separate, clearly-named commit, both blob SHAs recorded below."
  - "The five-edit ARM manifest split is deliberately kept to ONE new exclusion line in this plan; retiring the existing src/rurp_config_utils.cpp exclusion and promoting it into FIRESTARTER_COMMON_SOURCES is deferred to Plan 126-08 (same commit that deletes platform/py32f071/src/config.cpp), because promoting it here while config.cpp still defines the same four functions would give the ARM link two definitions of each — undetectable locally (arm-none-eabi-gcc/cmake/ninja absent; py32f071.yml does not fire on this branch)."
  - "The split commit and the test fallback fix are two separate commits (mirroring Plan 126-02's own ee2fe0d + dd3e4d2 shape): the split lands exactly the five files the acceptance criteria name, and the test fix is its own commit with the fallback's justification and both SHAs in the message."

requirements-completed: []  # CFG-03 completes at Plan 126-05's seam-shape gate; CFG-04 completes at Plan 126-04's measurement. This plan ticks NOTHING (only Plan 126-12 ticks CFG-01..07).

coverage:
  - id: D1
    description: "The storage seam header (include/rurp_config_storage.h) declares exactly two bool functions over a byte blob, included by exactly two TUs today (the policy layer and the AVR backend), with the includes-before-extern-C ordering and D-06/D-07/D-09 rationale recorded in its comment block"
    requirement: "CFG-03"
    verification:
      - kind: unit
        ref: "manual includer census: grep -rln '\"rurp_config_storage.h\"' src include platform test tests -> exactly 2 files"
        status: pass
    human_judgment: false
  - id: D2
    description: "src/rurp_config_utils.cpp is policy-only (no EEPROM include, no CONFIG_START, no platform conditional) and rurp_validate_config is byte-identical to the pre-refactor text"
    requirement: "CFG-03"
    verification:
      - kind: unit
        ref: "git diff src/rurp_config_utils.cpp (no hunk touches rurp_validate_config's body); pytest tests/ -q"
        status: pass
    human_judgment: false
  - id: D3
    description: "src/boards/rurp_config_storage_eeprom.cpp is a pure move of the AVR EEPROM access (CONFIG_START 48, typed EEPROM.get/put), both functions returning true unconditionally, guarded by the three-board #if before its includes"
    requirement: "CFG-04"
    verification:
      - kind: unit
        ref: "tests/test_config_storage_eeprom_regression.py -- all 7 functions"
        status: pass
    human_judgment: false
  - id: D4
    description: "ARM manifest gains exactly one new PY32_EXCLUDED line (5 -> 6), enforced-source count stays 24, and the src/rurp_config_utils.cpp exclusion is deliberately retained (retirement deferred to Plan 126-08)"
    requirement: "CFG-03"
    verification:
      - kind: unit
        ref: "python3 scripts/check_cmake_manifest.py -> PASS, 24 enforced, 6 allow-listed"
        status: pass
    human_judgment: false
  - id: D5
    description: "D-04 discharged via the documented fallback: the recorded pre-refactor blob SHA does not re-hash identical (a known, justified single-line change was required), both SHAs recorded, the test still green, and the observed access pair unchanged from Plan 126-02's pre-refactor values"
    requirement: "CFG-04"
    verification:
      - kind: unit
        ref: "git hash-object tests/test_config_storage_eeprom_regression.py; tests/test_config_storage_eeprom_regression.py -v (7/7 pass); access pair (48, 32) for load/save/validate, matching 126-02"
        status: pass
    human_judgment: false
  - id: D6
    description: "Both pinned native environments still report exactly 141 test cases / 141 succeeded / 17 suites; all three AVR builds exit 0 with the new object file present and identical flash/RAM to the pre-existing baseline"
    requirement: "CFG-04"
    verification:
      - kind: unit
        ref: "pio test -e native; pio test -e native_nodevtools; pio run -e uno/-e uno328pb/-e leonardo"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-07-31
status: complete
---

# Phase 126 Plan 03: Config Persistence Split — Common Policy Layer + Per-Platform Byte-Blob Backend Summary

**Split `src/rurp_config_utils.cpp` into a policy-only layer plus a new two-function storage seam (`include/rurp_config_storage.h`) and a pure-move AVR EEPROM backend (`src/boards/rurp_config_storage_eeprom.cpp`), added the one ARM-manifest exclusion this forces, and discharged D-04's "empty diff" proof via its documented fallback — one named, justified line change to the regression test, both blob SHAs recorded — after the recorded pre-refactor SHA did not re-hash identical against the acceptance-criteria-mandated AVR board guard.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-07-31T22:57:00Z
- **Tasks:** 2
- **Files modified:** 6 (2 created, 4 modified)

## Accomplishments

- `include/rurp_config_storage.h` created: exactly two `bool` declarations (`rurp_config_storage_load(void*, size_t)` / `rurp_config_storage_save(const void*, size_t)`), `<stdbool.h>`/`<stddef.h>` included before the `extern "C"` open, comment block carrying D-06/D-07/D-09/CFG-04 rationale and a FIRE-PROOF section naming both `tests/test_config_storage_seam_shape.py` (Plan 126-05) and `tests/test_config_storage_eeprom_regression.py` (Plan 126-02).
- `src/rurp_config_utils.cpp` reduced to policy-only: `#include <EEPROM.h>` and `#define CONFIG_START 48` removed; `#include "rurp_config_storage.h"` added; the two EEPROM calls replaced with `(void)rurp_config_storage_load/save(...)`. `rurp_validate_config`'s body — including the D-14 write-back — is byte-for-byte unchanged (confirmed by `git diff`: no hunk touches it).
- `src/boards/rurp_config_storage_eeprom.cpp` created: five-line MIT banner (byte-identical to `rurp_common.cpp`'s), three-board `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB) || defined(ARDUINO_AVR_LEONARDO)` guard before the includes with `#endif` at end of file, `CONFIG_START 48` moved verbatim, typed `EEPROM.get`/`EEPROM.put` via a cast to `rurp_configuration_t*` (not a byte loop), both functions returning `true` unconditionally, `len` cast to `void` in both.
- `platform/py32f071/CMakeLists.txt`: exactly one new line — `# PY32_EXCLUDED: src/boards/rurp_config_storage_eeprom.cpp -- AVR EEPROM backend, no ARM analogue` — taking the exclusion set from 5 to 6 lines. The existing `src/rurp_config_utils.cpp` exclusion is untouched; `FIRESTARTER_COMMON_SOURCES` (17 entries), `PY32_PLATFORM_SOURCES` (7 entries) and `PY32_SDK_SOURCES` (14 entries) are untouched.
- `scripts/check_cmake_manifest.py`'s module docstring updated to enumerate the new six-line exclusion set and record the deferred retirement and its duplicate-definition reason — text only; no regex, constant, function body or exit code changed.
- Both atomicity demonstrations run as scratch manipulations (never committed): exclusion line absent -> exit 1 with `"present in tree, not named... and not covered by a reasoned PY32_EXCLUDED entry"`; reason segment removed -> exit 1 with the missing-reason violation plus the same uncovered-tree-source violation. Restored state -> exit 0 both times.
- D-04's fallback applied and both blob SHAs recorded (see the dedicated section below) — the primary re-hash proof did NOT hold unmodified, and this is flagged prominently, not absorbed as routine.
- Both pinned native environments re-measured: `pio test -e native` = 141 cases / 141 succeeded / 17 suites; `pio test -e native_nodevtools` = 141 / 141 / 17. All three AVR builds (`uno`, `uno328pb`, `leonardo`) exit 0 with `src/boards/rurp_config_storage_eeprom.cpp.o` present, and their reported flash/RAM figures are identical to the pre-existing `size_baseline.json` values (23954/1573, 24004/1579, 26016/2014) — no delta observed, though this plan claims no flash/RAM figure (Plan 126-04 owns that measurement officially).

## Task Commits

Each task was committed atomically:

1. **Task 1: The atomic split — seam header, policy-only TU, AVR backend, manifest edit, checker docstring** — `1d1ab28` (refactor) — 5 files: `include/rurp_config_storage.h`, `src/rurp_config_utils.cpp`, `src/boards/rurp_config_storage_eeprom.cpp`, `platform/py32f071/CMakeLists.txt`, `scripts/check_cmake_manifest.py`.
   - Follow-up: `62b1b73` (test) — the D-04 documented fallback, one line in `tests/test_config_storage_eeprom_regression.py`'s `_compile()`. This follow-up is folded into Task 1's scope, mirroring Plan 126-02's own `ee2fe0d` + `dd3e4d2` two-commit shape: the split commit's own `git show --stat` still lists exactly the five files the plan's acceptance criteria name, and the test fix is a separately named, fully-justified commit landed immediately after (both within this task's execution, never left as a paused red state).
2. **Task 2: Discharge D-04 — the recorded blob SHA re-hash and evidence capture** — no file changes (evidence capture only, recorded below).

**Plan metadata:** (this SUMMARY commit, to follow)

## Files Created/Modified

- `firestarter/include/rurp_config_storage.h` (new) — the two-function byte-blob storage seam.
- `firestarter/src/rurp_config_utils.cpp` (modified) — reduced to policy-only.
- `firestarter/src/boards/rurp_config_storage_eeprom.cpp` (new) — AVR backend, pure move.
- `firestarter/platform/py32f071/CMakeLists.txt` (modified) — one new `PY32_EXCLUDED` line.
- `firestarter/scripts/check_cmake_manifest.py` (modified) — docstring only.
- `firestarter/tests/test_config_storage_eeprom_regression.py` (modified) — one line, the D-04 fallback (see Deviations).

## Decisions Made

- **Manifest-grouping correction recorded and applied exactly as the plan specifies:** only the new backend's exclusion line lands here; retiring `src/rurp_config_utils.cpp`'s exclusion and promoting it into `FIRESTARTER_COMMON_SOURCES` is deferred to Plan 126-08, in the same commit that deletes `platform/py32f071/src/config.cpp` — landing the promotion now, while `config.cpp` still defines the same four functions, would give the ARM link two definitions of each, undetectable in this devcontainer (`arm-none-eabi-gcc`/`cmake`/`ninja` absent; `py32f071.yml` does not fire on a push to this branch) and surfacing only in a later gated CI run.
- **D-04's documented fallback invoked, not the primary re-hash proof** — see the dedicated section below for the full reasoning and both SHAs.
- **The fallback fix is its own commit, not folded into the split commit** — this keeps the split commit's `git show --stat` at exactly the five paths the acceptance criteria name, mirroring the precedent Plan 126-02 itself set (`ee2fe0d` + `dd3e4d2`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking, per the plan's own documented fallback] D-04's primary blob-SHA re-hash proof did not hold; the plan's own documented fallback was applied**

- **Found during:** Task 2's D-04 discharge attempt, immediately after Task 1's split commit.
- **Issue:** The plan's own acceptance criteria (Task 1) mandate that `src/boards/rurp_config_storage_eeprom.cpp` wrap its body in the three-board `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB) || defined(ARDUINO_AVR_LEONARDO)` guard, matching the `uno_rurp_shield.cpp`/`leonardo_rurp_shield.cpp` analog. `tests/test_config_storage_eeprom_regression.py`'s `_compile()` (authored pre-split, in Plan 126-02) invokes host `g++` on both candidate sources with no board macro defined at all. Compiling the new backend TU under those conditions collapses the guarded body to an empty translation unit, producing `undefined reference to rurp_config_storage_load` / `rurp_config_storage_save` at link time — a **structural incompatibility** between two of the plan's own acceptance criteria (the mandatory AVR guard vs. the test compiling without any board macro), not a behaviour regression. `126-CONTEXT.md`'s own Discretion section anticipates exactly this: *"Verify this survives contact — if it cannot, the fallback is a single named, justified line change with both blob SHAs recorded, never a silent edit."*
- **Fix:** Applied the documented fallback exactly as specified. One line changed in `_compile()`: `argv = [compiler, "-std=gnu++17", "-Wall", "-Wextra"]` became `argv = [compiler, "-std=gnu++17", "-Wall", "-Wextra", "-DARDUINO_AVR_UNO"]`, with an inline comment stating the reason and that it is behaviourally inert for every *other* resolved source — `include/rurp_platform_compat.h` gates its only AVR-only include (`<avr/pgmspace.h>`) on `__AVR__` (compiler-supplied), never on `ARDUINO_AVR_UNO`, so defining the latter under host g++ changes nothing else about the compile. Verified this manually before committing: a scratch compile with `-DARDUINO_AVR_UNO` produced a clean link and the exact same `(op, idx, length)` access triple — `(G/P, 48, 32)` for load/save/validate — as the pre-fallback pre-refactor run.
- **Files modified:** `tests/test_config_storage_eeprom_regression.py` (one line).
- **Verification:** `python3 -m pytest tests/test_config_storage_eeprom_regression.py -v` — 7/7 pass; `python3 -m pytest tests/ -q` — 102 passed (unchanged total, no test added or removed); the observed access pair matches Plan 126-02's recorded pre-refactor values exactly (see below).
- **Committed in:** `62b1b73` (its own commit, separate from the split commit `1d1ab28`, per the two-commit shape described above).

---

**Total deviations:** 1, and it is the plan's own pre-authorized fallback path, not an ad hoc deviation-rule fix. **This is flagged prominently, not treated as routine**, per the plan's explicit instruction: D-04's primary proof (an unmodified blob-SHA re-hash) did **not** hold; the fallback (one named, justified line, both SHAs recorded) is what discharges the proof instead.
**Impact on plan:** Necessary — the AVR guard is a hard acceptance criterion for Task 1, and the test's compile invocation cannot exercise the guarded backend without some means of opening it under host g++. No scope creep: the fix is confined to one line of one file, landed as its own named commit.

## Issues Encountered

None beyond the D-04 fallback documented above, which was anticipated by the plan itself and resolved via the plan's own documented protocol — not an external blocker.

## D-04 Evidence Ledger

**This is the load-bearing output of this plan.**

### Primary proof attempt: blob-SHA re-hash — DID NOT hold unmodified

- **Recorded pre-refactor SHA (126-02):** `0ef805ff8e915f9321bda5dc50d61b8a8dd26eaf`
- **Post-split re-hash, before the fallback (confirmed identical to the recorded SHA — the split commit `1d1ab28` alone did NOT change the test file):** `0ef805ff8e915f9321bda5dc50d61b8a8dd26eaf` (matched, as expected — the split commit touched only `src/`, `include/`, `platform/` and the checker script, never the test).
- **Post-fallback SHA (after the one-line `_compile()` change, commit `62b1b73`):** `12bd237a7aeec174d2eaf5c99f206737255388f3`.
- **Verdict:** The recorded SHA re-hashes IDENTICAL only up to (and not including) the fallback commit. Because Task 1's own acceptance criteria mandate the AVR board guard, and the test as authored in Plan 126-02 cannot exercise a guarded backend TU under host g++ without a board macro, the fallback documented in `126-CONTEXT.md`'s Discretion section was invoked exactly as written: one named, justified line change, with both SHAs recorded here. **This is the finding this plan's dispatch prompt asked to be flagged prominently — the "empty diff on the test file" premise does not survive the AVR-guard acceptance criterion unmodified, and the fallback protocol is what makes the split's behaviour-preservation still provable.**

### Regression test result (post-fallback, post-split tree)

`python3 -m pytest tests/test_config_storage_eeprom_regression.py -v` — all 7 functions passed:
`test_pre_refactor_tu_compiles_and_runs_with_zero_warnings`,
`test_load_config_get_access_at_config_start_with_sizeof_length`,
`test_save_config_put_access_at_config_start_with_sizeof_length`,
`test_validate_config_write_back_produces_put_on_version_mismatch`,
`test_non_vacuity_source_resolved_and_access_recorded`,
`test_module_references_no_pio_build_artifact_path`,
`test_compiler_is_required_not_optional`.

- **Resolved candidate-path count:** **2** — `src/rurp_config_utils.cpp` and `src/boards/rurp_config_storage_eeprom.cpp` both resolve now (only the first resolved pre-split).
- **Observed `(operation, index, length)` access list, post-split, post-fallback** (host `g++ 14.2.0`, `-DARDUINO_AVR_UNO`):
  ```
  ACCESS load G 48 32
  ACCESS save P 48 32
  ACCESS validate P 48 32
  SIZEOF 32
  ```
  Identical to Plan 126-02's recorded pre-refactor access pair `(48, 32)` for load/save/validate, and `sizeof(rurp_configuration_t) == 32` on this host — **no change in the observed access pair**, which is the CFG-04 claim that actually matters (a change here would have been reported as a STOP finding; none occurred).
- **`pytest tests/ -q` total:** **102 passed** — unchanged from Plan 126-02's end state (this plan added no test module and removed none).

### Corroboration only (never primary — 124-VERIFICATION.md's surviving-trailer finding)

`git diff --stat dd3e4d2 HEAD -- tests/test_config_storage_eeprom_regression.py` (`dd3e4d2` = the commit immediately preceding this plan's work), quoted in full:
```
 tests/test_config_storage_eeprom_regression.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```
This one-line change IS the fallback described above, not a surprise — the corroboration confirms exactly one line changed in exactly one file, nothing more. `git status --porcelain` for `/workspaces/firestarter` (named explicitly): **0 lines** after all commits landed.

### Behaviour-preservation corroboration (C-14) — all seven config-API consumers verified unchanged

| Site | Line read | In Task 1's commit's changed-path list? |
|---|---|---|
| `src/firestarter.cpp:40` | `rurp_load_config();` | No |
| `src/firestarter.cpp:99` | `rurp_configuration_t* config = rurp_get_config();` | No |
| `src/firestarter.cpp:105` | `rurp_save_config(config);` | No |
| `src/boards/rurp_common.cpp:53` | `rurp_configuration_t* rurp_config = rurp_get_config();` | No |
| `include/rurp_hw_rev_utils.h:95` | `if (revision == REVISION_UNKNOWN && rurp_get_config()->hardware_revision == 0xFF) {` | No |
| `include/rurp_hw_rev_utils.h:101` | `rurp_configuration_t* rurp_config = rurp_get_config();` | No |
| `src/hardware_operations.cpp:106` | `rurp_configuration_t* rurp_config = rurp_get_config();` | No |
| `src/hardware_operations.cpp:118` | `rurp_configuration_t* rurp_config = rurp_get_config();` | No |
| `platform/py32f071/src/py32f071_rurp_shield.cpp:297` | `const rurp_configuration_t *const configuration = rurp_get_config();` | No |

(Nine call sites across seven source locations, matching C-14's "seven consumers" grouping — `firestarter.cpp` and `hardware_operations.cpp` each have two call sites within one file.) None appears in `git show --stat 1d1ab28` or `git show --stat 62b1b73`. This is the structural argument that CFG-04's byte-identical-behaviour claim is achievable: every consumer sits above the seam and calls only the four public functions, none of which changed shape.

### Golden traces and native counts

- `python3 -m pytest tests/test_golden_trace_identity.py -q` — **6 passed**. Golden register traces are compared per-array for `_shared/sdp_expected.h` (unchanged basis since Phase 119); no golden trace moved.
- `pio test -e native` — **141 test cases: 141 succeeded** across **17 suites**, `00:01:42`.
- `pio test -e native_nodevtools` — **141 test cases: 141 succeeded** across **17 suites**, `00:01:44`.
- Both runs used PlatformIO's own build timeout headroom (no truncation observed); both exit 0.

### Must-not-touch invariants, re-asserted after all commits

| File | Expected SHA | Observed SHA | Match |
|---|---|---|---|
| `include/rurp_shield.h` | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` | ✓ |
| `include/rurp_types.h` | `d3fe5203a91527bdb7b20a33843c81065e21c613` | `d3fe5203a91527bdb7b20a33843c81065e21c613` | ✓ |
| `platformio.ini` | `f4e720ba75a8c618cc23bac045ab65084d41a0a4` | `f4e720ba75a8c618cc23bac045ab65084d41a0a4` | ✓ |
| `platform/py32f071/linker/PY32F071xB_FLASH.ld` | `b32b5824c8e27492551db5c2b1d413f74f05b6f3` | `b32b5824c8e27492551db5c2b1d413f74f05b6f3` | ✓ |
| `scripts/baseline/size_baseline.json` | `9cc5204bb437735d77523e62512c1d2cadfc668f` | `9cc5204bb437735d77523e62512c1d2cadfc668f` | ✓ |
| `scripts/baseline/size_baseline_base01.json` | `b940c91655600a57ad7ef67cba723943af929daf` | `b940c91655600a57ad7ef67cba723943af929daf` | ✓ |

`CONFIG_VERSION` line at `include/rurp_shield.h:46` still reads the literal `"VER06"`. No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked (confirmed via `git status --porcelain -- .planning/REQUIREMENTS.md` in the meta repo — 0 lines expected, checked as part of this SUMMARY's own commit below).

### Includer census (D-09)

`grep -rln '"rurp_config_storage.h"' src include platform test tests` → exactly **2** files: `src/boards/rurp_config_storage_eeprom.cpp`, `src/rurp_config_utils.cpp`. `include/rurp_shield.h` is not among them (confirmed both by the census and by its unchanged blob SHA above).

### Manifest gate

`python3 scripts/check_cmake_manifest.py` → `PASS`, **24 enforced sources**, **14** `PY32_SDK_SOURCES` structurally exempt, **6** allow-listed omissions: `src/boards/leonardo_rurp_shield.cpp`, `src/boards/rurp_common.cpp`, `src/boards/rurp_config_storage_eeprom.cpp`, `src/boards/uno_rurp_shield.cpp`, `src/dev_tools.cpp`, `src/rurp_config_utils.cpp`.

### Atomicity demonstrations (scratch, never committed)

| # | Manipulation | Exit code | Violation reported |
|---|---|---|---|
| 1 | Backend TU present, its exclusion line removed | **1** | `src/boards/rurp_config_storage_eeprom.cpp: present in tree, not named in FIRESTARTER_COMMON_SOURCES, and not covered by a reasoned PY32_EXCLUDED entry` |
| 2 | Exclusion line present, its `-- <reason>` segment removed | **1** | `PY32_EXCLUDED entry missing its mandatory reason segment: 'src/boards/rurp_config_storage_eeprom.cpp' ...` (plus the same uncovered-tree-source violation, since an unreasoned entry does not count as valid coverage) |
| — | Restored to the correct committed state | **0** | `PASS: ... 24 enforced source(s) ... 6 allow-listed` |

Both were `sed`-based scratch edits to the working tree, reverted immediately after observing the exit code; `git diff platform/py32f071/CMakeLists.txt` after restoration showed only the one intended line, confirming no residue.

### AVR builds (no size figure claimed)

| env | Exit | Object file | Flash used | RAM used |
|---|---|---|---|---|
| `uno` | 0 | `.pio/build/uno/src/boards/rurp_config_storage_eeprom.cpp.o` present | 23954/32256 (unchanged vs. baseline) | 1573/2048 (unchanged) |
| `uno328pb` | 0 | `.pio/build/uno328pb/src/boards/rurp_config_storage_eeprom.cpp.o` present | 24004/32384 (unchanged) | 1579/2048 (unchanged) |
| `leonardo` | 0 | `.pio/build/leonardo/src/boards/rurp_config_storage_eeprom.cpp.o` present | 26016/28672 (unchanged) | 2014/2560 (unchanged) |

No flash or RAM figure is claimed by this plan — the identical-to-baseline figures above are recorded only as evidence the object file exists and the three builds succeed; Plan 126-04 owns the official measurement and any re-baseline decision.

## Branch Re-Check

- `firestarter` (submodule): `git rev-parse --abbrev-ref HEAD` → `v1.23-py32f071-integration` (checked after each commit and after this SUMMARY was written).
- Meta repo (`/workspaces`): `gsd/v1.23-py32f071-integration` (unchanged by this plan's firmware work; only this SUMMARY/STATE/ROADMAP land here).
- The two gitignored py32 worktrees (`firestarter_py32_ci`, `firestarter_app_py32`) were not written to.

## Claim Ceiling

No PY32F071 PCB exists. This plan makes no ARM claim at all: every measurement above (the AVR access pair, the sizeof, the native/AVR counts) is host-`g++`- or `avr-g++`-compiled AVR-side/policy-layer behaviour, per `.planning/REQUIREMENTS.md` §"Validation Ceiling". No flash or RAM figure is claimed for AVR either — that is Plan 126-04's job.

## Next Phase Readiness

- The storage seam exists and is proven behaviour-preserving on the AVR side (via the fallback-adjusted D-04 proof). Plan 126-04 can now measure the AVR flash/RAM delta immediately, before any ARM work — the pre-existing baseline figures observed unchanged in this plan's own build runs are a strong prior that the delta will be zero, but that measurement and any re-baseline decision belong to 126-04, not here.
- Plan 126-05's seam-shape gate (`tests/test_config_storage_seam_shape.py`) can now be written against a real, committed `include/rurp_config_storage.h`.
- Plan 126-08 has a clean, explicit deferred-work item recorded both in the CMakeLists.txt docstring and here: retire the `src/rurp_config_utils.cpp` exclusion, promote it into `FIRESTARTER_COMMON_SOURCES`, add C-3's `py32f071_hal_flash.c` entry to `PY32_SDK_SOURCES`, and delete `platform/py32f071/src/config.cpp` — all in one commit.
- No blockers.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `firestarter/include/rurp_config_storage.h`
- FOUND: `firestarter/src/boards/rurp_config_storage_eeprom.cpp`
- FOUND: commit `1d1ab28` in `firestarter` repo history
- FOUND: commit `62b1b73` in `firestarter` repo history
- FOUND: `.planning/phases/126-flash-persistent-config-via-a-storage-backend-seam-highest-r/126-03-SUMMARY.md`
- FOUND: commit `d7198fc` in meta repo history
