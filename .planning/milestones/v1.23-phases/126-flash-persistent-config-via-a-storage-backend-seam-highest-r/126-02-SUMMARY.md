---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 02
subsystem: testing
tags: [pytest, g++, eeprom, config-storage, avr, regression-test, py32f071]

# Dependency graph
requires:
  - phase: 126-01
    provides: firestarter/platform/py32f071/CONFIG-STORAGE.md and firestarter/tests/test_config_storage_design_vendored.py (86 -> 95 pytest total)
provides:
  - "firestarter/tests/test_config_storage_eeprom_regression.py, authored and proven green against the untouched pre-refactor src/rurp_config_utils.cpp"
  - "The recorded blob SHA Plan 126-03 must re-hash as D-04's primary proof of ROADMAP Criterion 3"
  - "The observed (offset=48, length=sizeof(rurp_configuration_t)=32-on-this-host) access pair the pre-refactor code emits"
affects: [126-03, 126-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hand-written fake EEPROM.h written fresh into tmp_path per call (C-12), never a committed fixture header, never dependent on the gitignored ArduinoFake libdeps path"
    - "Symbolic size assertions against the compiled binary's own reported sizeof(), never a Python integer literal (C-6)"
    - "Both pre-refactor and post-refactor D-08 source paths named from the start, filtered to existing files at collection time"
    - "Seeding both the fake's backing storage AND the live global config directly (never through EEPROM.get/put) so a deleted access produces a genuinely empty per-phase list rather than being masked by a validate-triggered write-back cascade"

key-files:
  created:
    - firestarter/tests/test_config_storage_eeprom_regression.py
  modified: []

key-decisions:
  - "D-04 discharged as a two-commit proof: this plan authors and proves the test against the untouched pre-refactor file and records its blob SHA; Plan 126-03 re-hashes that exact SHA after the split as primary proof, with a path-scoped git diff --stat as corroboration only"
  - "The committed non-vacuity check is scoped to the load phase's access count alone (not a sum across all three phases), because the save and validate phases run their own independent calls regardless of a load-only mutation -- a sum-based check would not fail on a deleted EEPROM.get call, silently defeating its own purpose"
  - "The driver seeds the live rurp_config global directly (memcpy, never through EEPROM.get/put) in addition to the fake's backing storage, so a mutation that removes the get() call leaves the load phase's access list genuinely empty instead of masked by an indirect validate write-back"

requirements-completed: []  # CFG-04 spans this plan, 126-03 and 126-04; only Plan 126-12 ticks requirement checkboxes

coverage:
  - id: D1
    description: "CFG-04 regression test authored against the pre-refactor src/rurp_config_utils.cpp, asserting the EEPROM get/put access at offset 48 with a length compared against the compiled binary's own reported sizeof(rurp_configuration_t) -- 7 test functions, all green"
    requirement: "CFG-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_config_storage_eeprom_regression.py -- all 7 functions"
        status: pass
    human_judgment: false
  - id: D2
    description: "Four mutation demonstrations (five assertion legs) proving each of the module's assertions able to fail on a mutated copy, with no mutation reaching the repository"
    verification:
      - kind: other
        ref: "scratch harness re-invoking the module's own test functions against mutated copies in tmp_path (see Task 2 evidence below); not committed to the repo"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-07-31
status: complete
---

# Phase 126 Plan 02: CFG-04 Pre-Refactor EEPROM Regression Test Summary

**Authored and proved green a pytest+g++ regression test against the untouched `src/rurp_config_utils.cpp`, asserting the EEPROM get/put access at offset 48 with a symbolic `sizeof(rurp_configuration_t)` length (32 on this host), and recorded its blob SHA as the artefact Plan 126-03's split will be judged against.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-07-31T22:39:30Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments

- `firestarter/tests/test_config_storage_eeprom_regression.py` created: 7 test functions, all green, against the pre-refactor policy layer.
- The pre-refactor `(offset, length)` access pair observed and recorded: `(48, 32)` for both `get` and `put`, with `sizeof(rurp_configuration_t) == 32` on this host (host `g++ 14.2.0`, `long` = 8 bytes, per C-6).
- The D-14 write-back (`rurp_validate_config()` on a version mismatch triggers a `put`) is asserted and observed to fire correctly.
- Each of the module's four load-bearing assertions (offset, length, non-vacuity, missing-header) demonstrated able to FAIL against a mutated copy, entirely in `tmp_path` / a scratch scandir outside the repository -- no mutation reached the repo.
- The test file's full 40-character blob SHA recorded below for Plan 126-03 to re-hash.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the pre-refactor CFG-04 regression test with a hand-written fake EEPROM.h** - `ee2fe0d` (test), refined by `dd3e4d2` (fix) after a self-review found the non-vacuity check would not actually fail on the "no access" mutation (see Deviations below). The refinement is folded into Task 1's scope since Task 2's own mutation demonstrations are what surfaced it, before any file outside this plan's single artifact was touched.
2. **Task 2: Prove each assertion able to fail, then record the D-04 evidence ledger** - no file changes (mutation demonstrations run entirely in scratch directories outside the repo per the plan's own instruction); evidence recorded below.

**Plan metadata:** (this SUMMARY commit, to follow)

## Files Created/Modified

- `firestarter/tests/test_config_storage_eeprom_regression.py` - CFG-04's pre-refactor regression test: hand-written fake `EEPROM.h` (written fresh into `tmp_path` per call), a driver TU exercising `rurp_load_config()` / `rurp_save_config()` / `rurp_validate_config()` in three log-isolated phases, and 7 pytest functions.

## Decisions Made

- **D-04's two-commit proof protocol, written down for Plan 126-03 to execute:** the recorded blob SHA below must re-hash **identical** after the CFG-03/D-07/D-08 split, and this module must still be **green** against the post-refactor tree (with both `src/rurp_config_utils.cpp` and `src/boards/rurp_config_storage_eeprom.cpp` now resolving in `_RESOLVED_SOURCES`). A path-scoped `git diff --stat` on the test file is **corroboration only** -- `.planning/phases/124-firmware-integration-merge/124-VERIFICATION.md` records a live finding where exactly that pipeline reported "(empty)" while a `1 file changed, 25 insertions(+)` trailer survived the grep because the trailer text does not contain the grepped filename. Quote `git diff --stat`'s full output rather than summarizing it as empty.
- **Documented fallback (never invoked in this plan):** if the both-paths-named-from-the-start approach cannot survive the refactor intact, the fallback is **one named, justified line change** to this test file in Plan 126-03, with **both** blob SHAs (before and after that one line change) recorded and the justification stated in that plan's SUMMARY -- never a silent edit, and never a `pytest.skip`.
- **Non-vacuity scoped to the load phase, not summed across all three phases** (see Deviations) -- a design correction found and fixed within this plan's own Task 1/Task 2 boundary, before the commit was finalized as the artefact Plan 126-03 depends on.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Non-vacuity check would not have caught the no-access mutation as designed**
- **Found during:** Task 2's mutation demonstration 3 (deleting the `EEPROM.get` call)
- **Issue:** The first version of the driver seeded only the fake EEPROM's backing storage, not the live `rurp_config` global. Deleting the `EEPROM.get` call left the live global at its zero-initialized state, so `rurp_validate_config()`'s internal mismatch check still fired and produced a `put` — masking the "no access" mutation behind an unrelated cascading write-back. A non-vacuity check summed across all three phases (load + save + validate) would therefore never actually go to zero and would not fail, even though the specific `get`-assertion test correctly caught the mutation via its exact-list comparison. This defeated the acceptance criterion that "the get assertion AND the non-vacuity assertion must both fail" and "the non-vacuity leg is what catches a silently-absent access."
- **Fix:** The driver now seeds BOTH the fake's backing storage AND the live global config directly (via `memcpy`, never through `EEPROM.get`/`put`, so this setup step is not itself a recorded access) with matching data before calling `rurp_load_config()`. This makes an unmutated call record exactly one `get` (redundant but harmless overwrite with identical data), while a mutation that removes the `get` call leaves the load phase's access list genuinely EMPTY (the live global already matches, so `rurp_validate_config()` does not cascade). The committed module's `test_non_vacuity_source_resolved_and_access_recorded` was also rescoped to assert `len(parsed["load"]) > 0` specifically, rather than a sum across all phases.
- **Files modified:** `firestarter/tests/test_config_storage_eeprom_regression.py`
- **Verification:** Re-ran the full module (7/7 pass) and `pytest tests/ -q` (102 pass) after the fix; re-ran all four mutation demonstrations against the corrected module and confirmed the no-access mutation now fails BOTH the get-assertion and the non-vacuity assertion (see the table below).
- **Committed in:** `dd3e4d2` (a follow-up commit to the same file, within Task 1's scope; Task 2 performed no file writes of its own)

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug in the test harness's own non-vacuity check, found via the plan's own mandated mutation-proof step)
**Impact on plan:** Necessary for correctness of the artefact Plan 126-03 depends on. No scope creep — the fix is confined to the single file this plan is scoped to, and the mutation-demonstration step that found it is exactly what Task 2 mandates.

## Issues Encountered

None beyond the deviation above, which was found and resolved via the plan's own required verification step (Task 2's mutation demonstrations), not an external blocker.

## D-04 Evidence Ledger

**This is the single highest-value output of this plan.**

- **Recorded blob SHA of `tests/test_config_storage_eeprom_regression.py`** (the final, committed version — after the `dd3e4d2` fix):
  ```
  0ef805ff8e915f9321bda5dc50d61b8a8dd26eaf
  ```
  **Plan 126-03 MUST compare `git hash-object tests/test_config_storage_eeprom_regression.py` against exactly this 40-character string** after landing the CFG-03/D-07/D-08 split. A match, plus a still-green run of this module, is D-04's primary proof of ROADMAP Criterion 3. (The intermediate commit `ee2fe0d`'s blob, `378ddb5a4fbd290457acb83ac52e50b7923a9efc`, is superseded by the `dd3e4d2` fix and is NOT the SHA to compare against.)

- **Pre-refactor anchor SHA of `src/rurp_config_utils.cpp`:** `6705fd46e07a2d359d161dc2e7728cb4e45f89c7` — confirmed unchanged by both `git hash-object` and by this plan's post-mutation integrity check.

- **Task 1 commits and their single changed path:**
  - `ee2fe0d9d595ba56f7727fd4abf052f2c5647dc1` — `tests/test_config_storage_eeprom_regression.py` (489 insertions, new file)
  - `dd3e4d2c894152dfb94c769ecc46f3e04d5766d8` — `tests/test_config_storage_eeprom_regression.py` (33 insertions, 17 deletions; the non-vacuity fix above)
  - Both commits' `git show --stat` list exactly one path.

- **Observed `(operation, index, length)` access list** (host `g++ 14.2.0`, unmutated code):
  ```
  ACCESS load G 48 32
  ACCESS save P 48 32
  ACCESS validate P 48 32
  SIZEOF 32
  ```
  i.e., `rurp_load_config()` → one `get` at index 48, length 32; `rurp_save_config()` → one `put` at index 48, length 32; `rurp_validate_config()` on a version mismatch → one `put` at index 48, length 32 (the D-14 write-back). `sizeof(rurp_configuration_t) == 32` on this host.

- **Pre-refactor pytest result for this module:** all 7 functions passed —
  `test_pre_refactor_tu_compiles_and_runs_with_zero_warnings`,
  `test_load_config_get_access_at_config_start_with_sizeof_length`,
  `test_save_config_put_access_at_config_start_with_sizeof_length`,
  `test_validate_config_write_back_produces_put_on_version_mismatch`,
  `test_non_vacuity_source_resolved_and_access_recorded`,
  `test_module_references_no_pio_build_artifact_path`,
  `test_compiler_is_required_not_optional`.

- **`pytest tests/ -q` total:** 95 (Plan 126-01's total, current-state note) → **102** (+7, this module's function count). Full run: `102 passed in ~5-8s`.

- **Resolved candidate-path count:** 1 today (`src/rurp_config_utils.cpp` only; `src/boards/rurp_config_storage_eeprom.cpp` does not yet exist). Both paths are named in `_CANDIDATE_SOURCES` from the start (D-08).

- **Zero-byte warning observation:** `compile_result.stderr == ""` confirmed for the unmutated pre-refactor TU under `-Wall -Wextra`.

- **The D-04 proof protocol Plan 126-03 must execute** (written out in one place, per the plan's instruction):
  1. Re-hash `tests/test_config_storage_eeprom_regression.py` and confirm it equals `0ef805ff8e915f9321bda5dc50d61b8a8dd26eaf` exactly.
  2. Re-run `python3 -m pytest tests/test_config_storage_eeprom_regression.py -v` against the post-split tree (now with both `src/rurp_config_utils.cpp` and `src/boards/rurp_config_storage_eeprom.cpp` resolving) and confirm all 7 functions still pass.
  3. Treat a path-scoped `git diff --stat` on the test file as **corroboration only**, and quote its full output rather than summarizing it as "(empty)" — `124-VERIFICATION.md` documents a live case where that exact shortcut hid a real change.
  4. **Documented fallback**, only if step 1 or 2 cannot be satisfied unmodified: make **one named, justified line change** to this test file, and record **both** blob SHAs (this plan's `0ef805ff8e915f9321bda5dc50d61b8a8dd26eaf` and the new one) plus the justification in Plan 126-03's SUMMARY — never a silent edit, and never a `pytest.skip`.

## Mutation Demonstration Table (Task 2)

All four mutations ran against copies in a scratch directory outside the repository (`/tmp/claude-1000/.../scratchpad/126-02-mutations/`), reusing this module's own committed helper functions (`_resolve_compiler`, `_write_fake_eeprom_header`, `_write_driver_tu`, `_compile`, `_run_binary`) via a dynamic import, with `_RESOLVED_SOURCES` monkeypatched to point at the mutated copy. No mutation ever touched a tracked file.

| # | Mutation | Expected outcome | Observed outcome | Assertion that fired |
|---|---|---|---|---|
| 1 | `CONFIG_START` changed from 48 to 100 | offset assertions fail, naming both 48 and the observed value | Compile clean; `load` phase recorded `[('G', 100, 32), ('P', 100, 32)]` (the wrong-address `get` itself broke the config's version match, cascading into a `put`) | `test_load_config_get_access_at_config_start_with_sizeof_length`: `AssertionError: expected exactly one get access at index 48 ... got [('G', 100, 32), ('P', 100, 32)]` |
| 2 | `EEPROM.get(CONFIG_START, *config)` replaced with a narrower-type (`uint8_t`) call at the same index | length assertion fails | Compile clean; `load` phase recorded `[('G', 48, 1)]` (index correct, length wrong) | `test_load_config_get_access_at_config_start_with_sizeof_length`: `AssertionError: ... got [('G', 48, 1)]` |
| 3 | The `EEPROM.get` call deleted entirely from `rurp_load_config()` | both the get assertion AND the non-vacuity assertion fail; the non-vacuity leg is what catches the silently-absent access | Compile clean; `load` phase recorded `[]` (genuinely empty — the live global was pre-seeded matching, so no cascading write-back masked the absence) | (a) `test_load_config_get_access_at_config_start_with_sizeof_length`: `AssertionError: ... got []`; (b) `test_non_vacuity_source_resolved_and_access_recorded`: `AssertionError: expected rurp_load_config() to record at least one EEPROM access; recorded none -- a test that passed here would be exactly the silently-absent-access shape this leg exists to catch.` **This is the load-bearing leg**: it is the one written specifically to catch an absent access, independent of the exact-list comparison in (a). |
| 4 | Compiled without `-I tmp_path` (fake `EEPROM.h` unreachable) | compile fails, reported via the compiler's stderr — never a skip, never a pass | `compile_result.returncode == 1`; stderr: `fatal error: EEPROM.h: No such file or directory` (in both the mutated source TU and the driver TU) | `test_pre_refactor_tu_compiles_and_runs_with_zero_warnings`: `AssertionError: expected a clean compile of (...)` |

**Post-mutation integrity check:** `git hash-object src/rurp_config_utils.cpp` = `6705fd46e07a2d359d161dc2e7728cb4e45f89c7` (unchanged); `git status --porcelain` in `/workspaces/firestarter` = 0 lines after the mutation script completed (the only tracked-tree change during this plan was the deliberate `dd3e4d2` fix, committed before the mutation-demonstration pass ran). The unmutated module was re-run after all four demonstrations and reported green (7/7), confirmed again immediately before writing this SUMMARY.

## Branch Re-Check

- `firestarter` (submodule): `git rev-parse --abbrev-ref HEAD` → `v1.23-py32f071-integration` (confirmed after every commit and after the mutation-demonstration script).
- Meta repo (`/workspaces`): `gsd/v1.23-py32f071-integration` (unchanged by this plan; only this SUMMARY and STATE/ROADMAP updates land there).
- `include/rurp_shield.h` → `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` (unchanged, D-09/CFG-07 prohibition honored).
- `include/rurp_types.h` → `d3fe5203a91527bdb7b20a33843c81065e21c613` (unchanged, CFG-07 prohibition honored).
- `ls scripts/check_*.py | wc -l` → `5` (unchanged; no new checker script created).
- No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked by this plan (confirmed via `git status --porcelain -- .planning/REQUIREMENTS.md` in the meta repo → 0 lines).
- The two gitignored py32 worktrees (`firestarter_py32_ci`, `firestarter_app_py32`) were not written to (both `git status --porcelain` → 0 lines).

## Claim Ceiling

No PY32F071 PCB exists. This plan makes no ARM claim at all: every measurement above (the `sizeof` value, the access list, the warning count) is host-`g++`-compiled AVR-side policy-layer behaviour, per `.planning/REQUIREMENTS.md` §"Validation Ceiling".

## Next Phase Readiness

- The pre-refactor evidence this phase's D-04 proof depends on is captured and green. Plan 126-03 can now perform the CFG-03/D-07/D-08 split (moving the two-function EEPROM backend into `src/boards/rurp_config_storage_eeprom.cpp`) and re-hash the recorded SHA above as its primary proof of behavioural equivalence.
- No blockers. `src/rurp_config_utils.cpp`, `include/rurp_shield.h` and `include/rurp_types.h` are all confirmed untouched and ready for Plan 126-03 to modify.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `.planning/phases/126-flash-persistent-config-via-a-storage-backend-seam-highest-r/126-02-SUMMARY.md`
- FOUND: `firestarter/tests/test_config_storage_eeprom_regression.py`
- FOUND: commit `ee2fe0d` in `firestarter` repo history
- FOUND: commit `dd3e4d2` in `firestarter` repo history
