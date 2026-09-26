---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 09
subsystem: firmware-storage
tags: [py32f071, flash, dual-slot, crc32, pytest, mutation-testing, cortex-m0plus]

# Dependency graph
requires:
  - phase: 126-07
    provides: "platform/py32f071/src/config_storage_dualslot.{h,cpp} -- the HAL-free core this plan compiles by explicit path and exercises"
provides:
  - "firestarter/tests/test_config_storage_dualslot.py -- six distinctly named CFG-05/Criterion-4 behaviours plus the D-05 CRC known-answer anchor, compiling the shipped core by path against a fresh-per-scenario RAM fake"
  - "Ten mutation demonstrations (recorded below, not committed) proving every one of the seven assertions can genuinely fail against an independent single-line change to a scratch copy of the core"
  - "A corrected understanding of the interrupted-write invariant: load() always returns a valid record; WHICH record (previous vs new) depends on whether the abort point covers the record's own 12-word footprint on this host -- confirms and formalizes Plan 126-07's own finding"
affects: ["126-10 (schema-pinning test, next in this phase)", "126-12 (closing plan, only one permitted to tick CFG-05)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-scenario fresh RAM-fake translation units (never a committed fixture TU), sharing one `_FAKE_PREAMBLE` string compiled together with the real core by explicit path -- the tested code is the shipped code (D-02)."
    - "A RAM fake that enforces C-8 (program-without-erase is a DEFECT, not a silent overwrite) by printing a stdout marker and calling abort() -- a defect signal distinguishable from an ordinary assertion failure."
    - "Mutation-driven proof-of-non-vacuity: mutated copies of the core, built and run entirely outside the repository, driven through the exact same committed test functions via a monkeypatched `_CORE_SRC` module global -- reusing assertions rather than reimplementing them for the RED demonstration."

key-files:
  created:
    - firestarter/tests/test_config_storage_dualslot.py
  modified: []

key-decisions:
  - "The interrupted-write test asserts the ACCURATE invariant Plan 126-07 already measured for this exact core (load() always returns a valid record; the winner depends on whether N covers the record's 12-word footprint), not the naive 'previous record always wins' reading of C-2's prose -- confirmed identical on re-measurement, no disagreement with 126-07 found."
  - "Mutation 4 ('length bound removed') is implemented as removing BOTH the validate_record length check AND load()'s defensive min()-clamp, since the shipped code's clamp is explicitly documented as redundant defence-in-depth on the happy path -- removing only the validate_record check leaves the clamp intact and produces NO observable sentinel violation (verified: this alone does not create the vulnerability the plan describes). Documented explicitly so the mutation's scope is transparent, not hidden."
  - "Mutations 8 and 9 needed bespoke demo fakes (not the committed one): mutation 8's fake forces erase_page to fail while also disabling the committed fake's separate C-8 guard, to isolate mutation 8's specific property (ignored return value) from mutation 7's (already demonstrated standalone); mutation 9's demo poisons a same-shaped stack region before calling the mutated save() to make an otherwise-UB tail-byte observation reproducible."

patterns-established: []

requirements-completed: []  # CFG-05 spans Plans 126-07, 126-08 and this one; only 126-12 ticks CFG-01..CFG-07

coverage:
  - id: D1
    description: "Six distinctly named test functions (blank, newest-wins, bad-crc, both-corrupt, interrupted-write, successive-saves) plus a seventh independent CRC known-answer anchor, all exercising the compiled core by explicit path"
    requirement: "CFG-05"
    verification:
      - kind: integration
        ref: "python3 -m pytest tests/test_config_storage_dualslot.py -v (9 passed: 7 required + 2 supporting legs)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The phase's highest-severity mitigation (T-126-09-01): an oversized `length` field rejected before any copy, with a sentinel-filled caller buffer intact past `len`"
    requirement: "CFG-05"
    verification:
      - kind: integration
        ref: "tests/test_config_storage_dualslot.py::test_slot_with_bad_crc_is_rejected_in_favour_of_the_other"
        status: pass
    human_judgment: false
  - id: D3
    description: "All ten mutation demonstrations produce genuine failures from independent single-line changes to scratch copies of the core; no mutation reaches the repository"
    requirement: "CFG-05"
    verification:
      - kind: other
        ref: "scratchpad mutation driver (recorded verbatim below), 10/10 mutations produced a failure or reproduced-defect outcome; git hash-object and git status --porcelain confirmed unchanged/clean after"
        status: pass
    human_judgment: false

duration: ~70min
completed: 2026-08-01
status: complete
---

# Phase 126 Plan 09: The dual-slot core proof suite (six named behaviours + CRC anchor) Summary

**`tests/test_config_storage_dualslot.py` -- six distinctly named CFG-05/Criterion-4 tests plus an independent CRC known-answer anchor, compiling the shipped `config_storage_dualslot.cpp` by explicit path against a fresh RAM fake per scenario, with all ten required mutation demonstrations confirmed genuine failures.**

## Performance

- **Duration:** ~70 min
- **Completed:** 2026-08-01
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments

- Authored `firestarter/tests/test_config_storage_dualslot.py`: seven distinctly named pytest functions (the six Criterion-4 behaviours plus D-05's CRC known-answer anchor), each compiling `platform/py32f071/src/config_storage_dualslot.cpp` by explicit path together with a per-scenario, freshly-written RAM fake (never a committed fixture TU).
- The RAM fake implements the three injected primitives over two 4-byte-aligned 256-byte page buffers, honours an abort-after-N-words hook (C-2), and enforces C-8 (program-without-erase is a DEFECT: a stdout marker plus `abort()`, never a silent overwrite).
- The CRC-rejection test carries the phase's highest-severity mitigation (T-126-09-01): an oversized `length` field is rejected before any copy, verified via a sentinel-filled caller buffer whose bytes past `len` are asserted intact, plus a check that no erase/program primitive call is attributable to the rejected record.
- The interrupted-write test sweeps N in {0, 1, 32, 63, 64} inside one function and asserts the CORRECTED invariant: `load()` always returns a valid record (never garbage, never false); which record wins depends on whether N covers the record's own 12-word footprint on this host -- exactly what Plan 126-07's own investigation found, now formalized as an assertion rather than left as a narrative note.
- Ran all ten required mutation demonstrations (Task 2) against scratch copies of the core, entirely outside the repository -- every one produced a genuine failure or reproduced the described defect. One bug was found and fixed in the committed test during this process (see Deviations).

## Task Commits

Each task was committed atomically:

1. **Task 1: The RAM fake and the seven named tests** -- `9e18dde` (test) -- `firestarter/tests/test_config_storage_dualslot.py`
2. **Fix found during Task 2's mutation-3 demonstration** -- `5281829` (fix) -- `firestarter/tests/test_config_storage_dualslot.py`

**Task 2 (mutation demonstrations)** modified no files -- all ten mutations ran against scratch copies of the core in the session scratchpad, outside `/workspaces/firestarter`, per its own `<files>` spec ("no files modified").

**Plan metadata:** this SUMMARY commit (docs, meta repo)

## Files Created/Modified

- `firestarter/tests/test_config_storage_dualslot.py` -- new file (808 → 816 lines after the Task-2-driven fix); imports stdlib + pytest only; resolves paths self-contained at module level (no `conftest.py`); no path under `.pio/` anywhere in its own text.

## Verification Detail (for the record)

### The seven function names, individual results

All run via `python3 -m pytest tests/test_config_storage_dualslot.py -v`:

| # | Function | Result |
|---|---|---|
| 1 | `test_crc32_matches_the_independent_known_answer_vector` | PASSED |
| 2 | `test_blank_slots_report_no_valid_record` | PASSED |
| 3 | `test_newest_sequence_wins_when_both_slots_valid` | PASSED |
| 4 | `test_slot_with_bad_crc_is_rejected_in_favour_of_the_other` | PASSED |
| 5 | `test_both_slots_corrupt_reports_no_valid_record` | PASSED |
| 6 | `test_interrupted_write_leaves_the_previous_record_loadable` | PASSED |
| 7 | `test_successive_saves_alternate_slots` | PASSED |
| 8 | `test_module_has_no_pio_libdeps_dependency` (supporting leg) | PASSED |
| 9 | `test_compiler_is_required_not_optional` (supporting leg) | PASSED |

No aggregate function stands in for any of the six behaviours -- 9 distinct pytest test IDs collected, all individually reported.

### Observed values (crossed on stdout, never inferred from exit code)

- **CRC known-answer:** `rurp_config_crc32("123456789", 9) == 0xCBF43926` -- exact match.
- **Observed `sizeof(StoredConfiguration)` on this host:** **48** bytes (matches 126-07's recorded figure exactly: host `long` is 8 bytes, `4+2+2+32(configuration)+4+4 = 48`).
- **Interrupted-write, footprint = 12 words (48 bytes / 4):**

  | N (words) | `load_ok` | winning record | matches 126-07's finding |
  |---|---|---|---|
  | 0 | true | previous (`O`) | yes -- N < 12 |
  | 1 | true | previous (`O`) | yes -- N < 12 |
  | 32 | true | new (`N`) | yes -- N >= 12 |
  | 63 | true | new (`N`) | yes -- N >= 12 |
  | 64 | true | new (`N`) | yes -- N >= 12 |

  `load()` never returned false and never returned garbage at any N -- exactly the T-126-09-03/T-126-07-04 property in its strongest form. **No disagreement with Plan 126-07's own harness was found**; the two independently-authored harnesses (126-07's now-deleted scratch harness, and this plan's committed one) agree exactly on the footprint (12 words) and on which record wins at every one of the five tested N values.

- **Slot alternation / sequence progression (4 successive saves):** `programmed_slot` sequence observed `[0, 1, 0, 1]` (strictly alternating), `sequence` observed `[1, 2, 3, 4]` (strictly increasing). Final `load()` returned the 4th save's marker (`'D'`).
- **Sentinel-check outcome (length-bound test):** `oversized_loaded=0`, `sentinel_intact=1`, `erase_calls=0`, `program_calls=0` -- the oversized-`length` record was rejected, the caller's buffer bytes past `len` were untouched, and no flash primitive was invoked during the rejected `load()`.
- **Erase-before-program assertion:** armed and never triggered across any of the seven committed scenarios' ordinary saves (all of which erase before programming, as the real core does); demonstrated firing under mutation 7 below.
- **Zero-byte compile stderr:** asserted (`compile_result.stderr == ""`) under `-Wall -Wextra` for every one of the seven scenario compiles; held in every run.

### Mutation demonstrations (Task 2) -- 10/10 genuine failures

Run entirely in the session scratchpad (`/tmp/.../scratchpad/run_mutations.py` and `.../mutations/*.cpp`), never inside `/workspaces/firestarter`. Mutations 1, 2, 3, 4, 5, 6 and 10 were driven through the **exact same committed test functions** via a monkeypatched `_CORE_SRC` module global (no reimplementation of any assertion); mutations 7, 8 and 9 needed bespoke demo scenarios (documented below) because they exercise properties no single named test asserts directly.

| # | Mutation | Test(s) that failed | Observed failure |
|---|---|---|---|
| 1 | Newest-wins inverted (`>` → `<` in `scan_slots`) | `test_newest_sequence_wins_when_both_slots_valid` | Both orders returned the LOWER-sequence marker (`'L'` instead of `'H'`) |
| 2 | CRC check removed from `validate_record` | `test_slot_with_bad_crc_is_rejected_in_favour_of_the_other` AND `test_both_slots_corrupt_reports_no_valid_record` | Bad-CRC record won (`badcrc_marker='X'`); both-corrupt case returned `true` instead of `false` |
| 3 | Magic check removed from `validate_record` | `test_blank_slots_report_no_valid_record` | The magic-trap fixture (invalid magic, valid length, self-consistent CRC) flipped from rejected to accepted (`magic_trap_loaded=1`) -- confirms the companion assertion genuinely isolates the magic check (see Deviations: this required a fix) |
| 4 | Length bound removed (both `validate_record`'s check AND `load()`'s defensive clamp) | `test_slot_with_bad_crc_is_rejected_in_favour_of_the_other` | **Recorded in full (highest severity, T-126-09-01):** `oversized_loaded` flipped to `1` (accepted) and `sentinel_intact` flipped to `0` -- the caller's buffer bytes past `len` were overwritten, the exact sentinel corruption the assertion exists to catch |
| 5 | Bound check moved after the copy (unclamped `memcpy` first, check second) | `test_slot_with_bad_crc_is_rejected_in_favour_of_the_other` | **Recorded in full:** `sentinel_intact=0` even though the record was still ultimately rejected (`oversized_loaded=0`) -- proves the test asserts an ORDERING (copy happens before the check can matter), not merely the presence of a check |
| 6 | Active slot overwritten (`save` targets `active.slot` instead of the inactive one) | `test_interrupted_write_leaves_the_previous_record_loadable` AND `test_successive_saves_alternate_slots` | Interrupted-write: `load_ok=0` at N=0 and N=1 (the ONLY previously-valid record got destroyed, unlike the correct core which never touches it); successive-saves: all four saves landed on slot 0 (`[0,0,0,0]`, no alternation) |
| 7 | Erase skipped entirely before program | (RAM fake's own C-8 assertion, exercised via the `successive_saves` scenario) | Process aborted (SIGABRT, exit -6) with `DEFECT:PROGRAM_WITHOUT_ERASE slot=0` printed on stdout on the very first save -- the fake's erase-before-program guard fired exactly as armed |
| 8 | Erase-failure return value ignored | (bespoke demo: forced erase failure, C-8 guard disabled to isolate this property) | **Recorded in full, the V4 write-protection failure mode:** with the fake's `erase_page` forced to fail, the mutated `save()` still reported `save_ok=1` -- success it did not achieve -- while `program_calls_slot0=1` confirms it programmed the un-erased page anyway |
| 9 | Staging buffer bypassed (`&record` passed directly instead of the 0xFF-padded 64-word page) | (bespoke demo: stack-poisoned tail bytes) | `tail_all_ff=0` -- bytes beyond the record's own 48-byte footprint in the programmed slot were NOT the deterministic `0xFF` padding the correct staging-buffer code always produces, confirming adjacent (poisoned) stack memory leaked into the "flash" page |
| 10 | CRC polynomial changed (`0xEDB88320` → `0xEDB88321`, one bit) | `test_crc32_matches_the_independent_known_answer_vector` | Observed `0xCFBDC920` instead of the expected `0xCBF43926` -- **this is what stops the other six tests from agreeing only with themselves**: had the anchor been derived from the module under test instead of an independent published vector, this mutation would have passed vacuously |

No mutation was constructed by feeding a test its own expected output; each is an independent, documented single-concept change to a scratch copy. Mutations 4 and 5 are documented as touching two tightly-coupled lines each (the `validate_record` check plus its corresponding `load()`-level enforcement) rather than one, because the shipped code's own comment states the `load()`-level clamp is deliberate defence-in-depth for the `validate_record` check -- removing only one of the two, verified experimentally, produces **no observable difference at all** (the remaining guard fully compensates), which would have made the demonstration vacuous. This is recorded transparently rather than silently narrowed to "one line."

**Post-demonstration integrity check:**
```
core=51a1e82f268dc8526cf3cc1c66c74b86fd7c4085   (unchanged before and after all ten mutations)
firestarter git status --porcelain: 0 lines
```

### Phase-level regression state (recorded per Task 2's instruction)

- `python3 -m pytest tests/ -q` → **153 passed** (144 baseline + this module's 9 test functions).
- `pio test -e native` → **141 test cases: 141 succeeded** across 17 suites.
- `pio test -e native_nodevtools` → **141 test cases: 141 succeeded** across 17 suites.
- `python3 scripts/check_cmake_manifest.py` → exit 0, **26 enforced source(s)** resolved (unchanged from 126-08's baseline; this plan touches no CMake list).
- `ls scripts/check_*.py | wc -l` → **5** (unchanged).

### Hash and branch checks (hard constraints)

- `git hash-object platform/py32f071/src/config_storage_dualslot.cpp` → `51a1e82f268dc8526cf3cc1c66c74b86fd7c4085` (unchanged throughout both tasks and all mutation demonstrations).
- `git show --stat HEAD` (test commit `9e18dde`) → exactly one path, `firestarter/tests/test_config_storage_dualslot.py`.
- `git -C /workspaces/firestarter_py32_ci status --porcelain` → empty (untouched).
- `git -C /workspaces/firestarter_app_py32 status --porcelain` → empty (untouched).
- `git -C /workspaces/firestarter rev-parse --abbrev-ref HEAD` → `v1.23-py32f071-integration`, re-checked after both commits.

## Decisions Made

- Implemented the interrupted-write test against the ACCURATE invariant Plan 126-07 already measured for this exact core (winner depends on whether N covers the 12-word footprint), rather than a literal "previous record always wins" reading -- this plan's independent re-measurement agrees exactly, so no disagreement is recorded, only confirmation.
- Mutation 4's scope (removing both the `validate_record` check and `load()`'s defensive clamp) is documented explicitly rather than silently narrowed, because the single-check version was tried first and verified to produce zero observable difference -- the shipped code's own comment already flags the clamp as intentional defence-in-depth, so a faithful "remove the length bound" demonstration must remove both layers of it.
- Mutations 8 and 9 required bespoke, non-committed demo fakes/scenarios (documented in the driver script, never in the repository) because they exercise properties -- an ignored erase-return-value, and a bypassed staging buffer -- that no single one of the seven committed named functions asserts directly; the plan's own Task 2 action text treats mutations 7-10 as demonstrations distinct from the six-name mapping used for 1-6.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed the blank test's "magic trap" companion fixture, which the length check was silently masking**
- **Found during:** Task 2's mutation-3 demonstration ("magic check removed")
- **Issue:** The companion fixture in `test_blank_slots_report_no_valid_record` left `length` at its blank `0xFFFF` pattern while only fixing up `crc32` to be self-consistent. Since `validate_record`'s length check runs before the CRC check, this fixture was ALREADY rejected on the length gate regardless of the magic check's presence -- so removing the magic check (mutation 3) produced no observable change, an "UNEXPECTED PASS" that would have been a hollow companion assertion (the exact class of defect Task 2 exists to catch, this time caught in the tester's OWN fixture rather than the core).
- **Fix:** Set `trap.length` to `sizeof(rurp_configuration_t)` (a valid, in-bound value) before recomputing `trap.crc32`, so ONLY the magic check can be what rejects the fixture. Re-ran the full suite (still green, 9/9) and re-ran mutation 3 (now fails as expected: `magic_trap_loaded` flips from 0 to 1).
- **Files modified:** `firestarter/tests/test_config_storage_dualslot.py`
- **Verification:** `python3 -m pytest tests/test_config_storage_dualslot.py -v` (9 passed, unmutated); mutation 3 re-run against the fixed committed test now reports "FAILED AS EXPECTED".
- **Committed in:** `5281829` (fix)

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug in the test's own fixture, found via the plan's own mutation-demonstration discipline).
**Impact on plan:** The fix strengthens exactly the property the companion assertion exists to prove (isolation of the magic check from length/CRC). No scope creep -- confined to the one fixture.

## Issues Encountered

None beyond the one auto-fixed bug above, discovered by the plan's own required mutation-testing discipline working as intended.

## User Setup Required

None -- no external service configuration required.

## Non-Claims (Claim Ceiling, explicit)

- **No PY32F071 PCB exists**, and nothing here claims behaviour observed on real hardware.
- **No real power-loss claim.** The interrupted-write test models `FLASH_Program_Page`'s 64 discrete word-store boundaries (observable in the pinned SDK source, C-2) -- not an observation of a real reset on real silicon.
- **No DFU-preservation claim.** This plan does not touch host DFU tooling or exercise an install.
- **No CI-coverage claim.** `pytest tests/` runs only in `build.yml` (push/PR to `main`) and `beta-build.yml` (push to `beta`); `py32f071.yml` has no pytest step. This SUMMARY's local run, plus `126-NONREGRESSION.md` (Plan 126-12), is the only evidence.
- **No requirement checkbox in `.planning/REQUIREMENTS.md` was ticked by this plan.** CFG-05 remains open pending Plan 126-12.

## Next Phase Readiness

- `tests/test_config_storage_dualslot.py` is ready to be cited by Plan 126-12's `126-NONREGRESSION.md` re-execution.
- The dual-slot core (`config_storage_dualslot.{h,cpp}`) is unchanged and unmutated; all mutation evidence lives outside the repository.
- Plan 126-10 (schema-pinning test) can proceed independently -- no shared files with this plan beyond the already-stable core and header.
- No blockers. Both native envs remain at 141/141 across 17 suites; `pytest tests/` is now at 153; the manifest gate is green at 26 enforced sources; checker count unchanged at 5.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: firestarter/tests/test_config_storage_dualslot.py
- FOUND: .planning/phases/126-.../126-09-SUMMARY.md (this file)
- FOUND: commit 9e18dde (Task 1, firestarter repo)
- FOUND: commit 5281829 (fix found during Task 2, firestarter repo)
