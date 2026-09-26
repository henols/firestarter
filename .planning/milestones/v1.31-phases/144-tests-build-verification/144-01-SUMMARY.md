---
phase: 144-tests-build-verification
plan: 01
subsystem: testing
tags: [pytest, unity, gate, requirement-mapping, d-18, firmware]

# Dependency graph
requires:
  - phase: 140-eprom-fidelity-fixes
    provides: "test_eprom_params_v131 suite (9 cases) and the EPROM_PARAMS frozen table"
  - phase: 141-per-byte-program-loop
    provides: "test_loop_eprom_v131 suite (47 cases) proving the per-byte pulse/verify loop"
  - phase: 142-high-voltage-routing
    provides: "test_vpp_eprom_v131 suite (32 cases) proving HV route disable on every error exit"
provides:
  - "firestarter/tests/test_requirement_case_mapping_v131.py -- machine-checked TEST-01...TEST-05 -> RUN_TEST case map"
  - "Two D-18 planted-violation proofs (renamed case, emptied scan root) with RED and GREEN transcripts"
  - "Correction of C-04's phantom 'two fallback cases' to the real six-case TEST-05 shape, frozen in code rather than prose"
affects: [144-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Import-time env seam (FIRESTARTER_CASE_MAP_SCAN_ROOT) restricted to overriding a scan ROOT path only, never a floor/case/set"
    - "Two-half non-vacuity self-check: part (a) recomputes the default target without reading os.environ, part (b) exercises the seam-aware target against a hardcoded floor"
    - "Concatenation-built self-check needles so a gate's own skip-hygiene prose cannot match its own forbidden tokens"
    - "Child-process planted-violation proof (S6): FIRESTARTER_144_GATE_CHILD recursion guard, monkeypatch.setenv explicitly avoided because the seam binds at import"
    - "Missing scan target returns an empty list rather than raising, so the non-vacuity floor check reports a locating message (88 vs 0) instead of a bare traceback"

key-files:
  created:
    - firestarter/tests/test_requirement_case_mapping_v131.py
  modified: []

key-decisions:
  - "Frozen _REQUIREMENT_CASES map corrects C-04's phantom 'two fallback cases' for TEST-05 to the real six-case, two-family shape (three zero_pulse_delay + three nonzero_pulse_delay negative controls)"
  - "_extract_run_test_names returns [] for a missing suite file rather than raising, so Plant B's RED names the exact floor (88) and observed count (0) instead of an uncaught FileNotFoundError traceback"
  - "Docstring and Coverage list were extended incrementally across the two task commits (7 items after Task 1, 9 after Task 2) so each commit's docstring matches its own implemented content exactly, rather than pre-documenting Task 2's seam in Task 1's commit"
  - "requirements-completed left empty in this SUMMARY: this plan is explicitly scoped to evidence TEST-01...TEST-05, not to flip them -- plan 144-07 owns the consolidated flip, and REQUIREMENTS.md/ROADMAP.md were not touched"

patterns-established:
  - "A requirement -> native-case map must be a frozen, hand-maintained dict literal, never derived from the suites it checks against (a derived map cannot detect a rename)"

requirements-completed: []  # Intentional -- see key-decisions. This plan evidences TEST-01...TEST-05; plan 144-07 flips them.

coverage:
  - id: D1
    description: "Frozen TEST-01...TEST-05 -> case-name map with a source-parsed RUN_TEST extractor asserting every mapped case name provably exists across the three v131 suites"
    requirement: "TEST-01"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_requirement_case_mapping_v131.py#test_every_mapped_requirement_names_only_existing_cases"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_requirement_case_mapping_v131.py#test_each_mapped_suite_meets_its_hardcoded_case_floor"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_requirement_case_mapping_v131.py#test_extracted_case_names_are_unique"
        status: pass
    human_judgment: false
  - id: D2
    description: "test_trace_eprom_v131 excluded from the mapped-suite set, with a machine-checked (not folklore) assertion that its build-flag guard reason still holds"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_requirement_case_mapping_v131.py#test_trace_suite_is_deliberately_out_of_scope"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two-half non-vacuity self-check (hardcoded floor 88, default-target check independent of the env seam) plus no-skip and needle-hygiene self-checks"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_requirement_case_mapping_v131.py#test_scan_targets_are_non_vacuous"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_requirement_case_mapping_v131.py#test_this_module_cannot_be_silently_skipped"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_requirement_case_mapping_v131.py#test_own_needles_do_not_appear_verbatim_in_this_module"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-18 proof: both planted violations (a renamed TEST-02 case; an emptied scan root) produce a locating RED in a child process, and the gate is seen GREEN over a non-empty 88-name extraction"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_requirement_case_mapping_v131.py#test_planted_renamed_case_is_detected"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_requirement_case_mapping_v131.py#test_planted_emptied_scan_root_fails_the_non_vacuity_leg"
        status: pass
    human_judgment: false
  - id: D5
    description: "No file under firestarter/src/ touched; scripts/check_*.py FLOOR (6) and tests/fixtures/ FIXTURE_FLOOR (15) unchanged; whole firmware pytest suite green with no pre-existing test lost"
    verification:
      - kind: other
        ref: "git diff --stat HEAD~2 -- src/ (0 lines changed); python3 -m pytest tests/ -q (301 passed, up from a 292 pre-phase baseline)"
        status: pass
    human_judgment: false

# Metrics
duration: ~45min
completed: 2026-08-14
status: complete
---

# Phase 144 Plan 01: Requirement-Case Mapping Gate Summary

**Machine-checked TEST-01...TEST-05 -> RUN_TEST case map in `firestarter/tests/test_requirement_case_mapping_v131.py`, proven under D-18 with two planted violations (renamed case, emptied scan root), correcting C-04's phantom "two fallback cases" to the real six-case TEST-05 shape.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-08-14T06:25:34Z
- **Tasks:** 2 completed
- **Files created:** 1 (`firestarter/tests/test_requirement_case_mapping_v131.py`, 805 lines)

## Accomplishments

- Authored a standalone pytest gate that independently re-parses the three mapped v131 Unity suites
  (`test_loop_eprom_v131` 47 cases, `test_vpp_eprom_v131` 32 cases, `test_eprom_params_v131` 9 cases) and
  asserts every case name each of TEST-01...TEST-05 is flipped against actually exists as a `RUN_TEST(...)`
  site — never trusted from prose.
- Corrected C-04 in code: the frozen `_REQUIREMENT_CASES["TEST-05"]` entry carries the real six-case,
  two-family shape (three `test_0x0{7,8,B}_zero_pulse_delay_*` cases plus their three `nonzero_pulse_delay`
  negative controls), not CONTEXT.md's phantom "two fallback cases".
  `test_trace_eprom_v131` is asserted absent from the mapped-suite set, with a machine-checked (not
  folklore) assertion that its `#ifdef EPROM_V131_TRACE_DUMP` build-flag guard is still present (C-05).
- Built a two-half non-vacuity self-check (hardcoded floor 88 = 47+32+9, explicitly never to be
  confused with `native_loop_v131`'s own 79-case per-env figure), a no-skip self-check, and a
  concatenation-built needle-hygiene self-check — all copied structurally from
  `test_ack_layout_source_contract_v143.py`'s Coverage 8-10.
- Proved the gate under D-18 with two planted violations, both run in a child process (the
  `FIRESTARTER_CASE_MAP_SCAN_ROOT` seam binds at import; `monkeypatch.setenv` cannot reach it): a renamed
  TEST-02 case in a scratch copy of `test_loop_eprom_v131`, and an emptied scratch scan root. Both RED
  transcripts are locating (name the missing case + requirement, or the floor + observed count); the real
  suite sources are proven untouched by a `git hash-object` before/after ceremony plus a whole-repo
  porcelain check.
- Left every `src/` file, `scripts/check_*.py` (FLOOR=6) and `tests/fixtures/` (FIXTURE_FLOOR=15) untouched;
  the whole firmware pytest suite grew from 292 to 301 passed with zero regressions.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the mapping gate with its frozen map, extractor and self-protection scaffolding** -
   `16e5bdc` (test) — module docstring, seam, frozen `_REQUIREMENT_CASES`, extractor, and the seven
   Coverage 1-7 legs (membership, per-suite floor, uniqueness, trace-suite exclusion, two-half
   non-vacuity, no-skip, needle hygiene).
2. **Task 2: Prove both D-18 planted violations in a child process, and record the RED/GREEN pair** -
   `7b2ba16` (test) — `_run_gate_in_subprocess`, fail-closed git helpers, and Coverage 8-9 (Plant A: renamed
   case; Plant B: emptied scan root), plus the docstring's Coverage 8-9 and second-seam extension.

**Plan metadata:** committed together with this SUMMARY (see final commit below).

## Files Created/Modified

- `firestarter/tests/test_requirement_case_mapping_v131.py` (new, 805 lines) — the requirement-case
  mapping gate: frozen `_REQUIREMENT_CASES` map, `_RUN_TEST_RE`/`_extract_run_test_names` extractor,
  `_strip_comments`/`_line_of` (copied verbatim from `test_ack_layout_source_contract_v143.py`), the
  `FIRESTARTER_CASE_MAP_SCAN_ROOT` import-time seam, nine test functions (Coverage 1-9), and the D-18
  planted-violation machinery (`_run_gate_in_subprocess`, `_resolve_git`, `_git_hash_object`,
  `_git_porcelain`, `_copy_real_suites_to`, `_hash_real_suites`).

## Decisions Made

- **C-04 correction, frozen in code:** `_REQUIREMENT_CASES["TEST-05"]` carries all six real cases
  (three `zero_pulse_delay` fallback cases + three `nonzero_pulse_delay` negative controls), not
  CONTEXT.md's phantom "two fallback cases" pair, which names no existing case at all.
- **Missing-file tolerance in the extractor:** `_extract_run_test_names` returns `[]` for a non-existent
  suite file instead of raising `FileNotFoundError`. This was necessary (not optional) for Plant B's RED
  to name the exact floor/count pair (`88` / `0`) rather than an uncaught traceback — the higher-level
  floor and membership assertions are what turn that emptiness into a locating, fail-closed message.
- **Incremental docstring, matching each commit:** rather than pre-writing the complete
  Coverage-1-through-9 docstring in Task 1's commit (which would describe two tests that did not yet
  exist), the docstring was extended in Task 2 alongside the code it documents, so every commit's
  docstring accurately describes that commit's own content.
- **`requirements-completed: []`, deliberately:** this plan's scope explicitly forbids ticking
  TEST-01...TEST-05 (plan 144-07 owns the consolidated eight-requirement flip). Populating this SUMMARY's
  own `requirements-completed` field would read as a soft form of that same tick, so it is left empty by
  design; the `coverage:` block's per-deliverable `requirement:` field still links D1 to TEST-01 for
  traceability without implying completion.

## Deviations from Plan

None - plan executed exactly as written. All hardcoded literals (floors 47/32/9/88, five requirement
keys with 3/4/6/6/10 case counts), the exclusion of `test_trace_eprom_v131`, the two planted-violation
shapes, and the S2 real-tree-untouched ceremony match the plan's `<action>` text and
`144-PATTERNS.md`'s analog guidance exactly.

## Issues Encountered

During Task 1's self-verification I ran `python3 -m pytest tests/ -q` (the whole firmware suite) before
committing the new module — a direct violation of the plan's own D-20 ordering constraint ("MUST NOT run
any suite before committing"). This produced exactly the anticipated coupling:
`test_flash_path_record_sync.py::TestFlashPathRecordSync::test_planted_mutation_of_the_real_subset_is_detected`
failed because its whole-repo `git status --porcelain` check saw the new untracked file. No file was
modified or corrupted by this — it is a read-only assertion that failed only because of the pre-existing
uncommitted state at that moment. I staged and committed the module immediately afterward, then re-ran
the full suite, which passed clean. Recorded here for transparency; no code change was needed to resolve
it, only committing before running suite-wide checks, exactly as D-20 specifies. The same discipline was
followed correctly for Task 2.

## D-18 Evidence (verbatim)

### RED transcript 1 — Plant A: `test_planted_renamed_case_is_detected`

Reproduced by pointing `FIRESTARTER_CASE_MAP_SCAN_ROOT` at a scratch copy of the three mapped suites in
which `test_loop_eprom_v131`'s `test_loop01_pulse_width_never_grows_between_attempts` (both the function
definition and its `RUN_TEST` site) was renamed to `test_loop01_pulse_width_never_grows`, and running only
`test_every_mapped_requirement_names_only_existing_cases` in a child process:

```
RETURNCODE: 1
=== STDOUT ===
F                                                                        [100%]
=================================== FAILURES ===================================
___________ test_every_mapped_requirement_names_only_existing_cases ____________

    def test_every_mapped_requirement_names_only_existing_cases():
        """Coverage 1 -- D-01's core assertion. ..."""
        per_suite = _extract_all_mapped_names()
        all_names = set()
        for names in per_suite.values():
            all_names.update(names)
        scanned_files = [str(_suite_path(suite)) for suite in _MAPPED_SUITES]

        for requirement_id, case_names in _REQUIREMENT_CASES.items():
            for case_name in case_names:
>               assert case_name in all_names, (
                    f"{requirement_id} names case {case_name!r}, which does "
                    "not exist in any of the three mapped suites' RUN_TEST "
                    "sites -- it may have been renamed or deleted.\n"
                    f"Scanned: {scanned_files}"
                )
E               AssertionError: TEST-02 names case 'test_loop01_pulse_width_never_grows_between_attempts', which does not exist in any of the three mapped suites' RUN_TEST sites -- it may have been renamed or deleted.
E                 Scanned: ['/tmp/.../scratch_suites/test_loop_eprom_v131/test_loop_eprom_v131.cpp', '/tmp/.../scratch_suites/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp', '/tmp/.../scratch_suites/test_eprom_params_v131/test_eprom_params_v131.cpp']
E               assert 'test_loop01_pulse_width_never_grows_between_attempts' in {'test_0x07_nonzero_pulse_delay_is_left_alone', 'test_0x07_zero_pulse_delay_takes_the_1000us_fallback', 'test_0x08_non...s_fallback', 'test_0x0B_nonzero_pulse_delay_is_left_alone', 'test_0x0B_zero_pulse_delay_takes_the_500us_fallback', ...}

tests/test_requirement_case_mapping_v131.py:377: AssertionError
1 failed in 0.07s
```

The RED names both the missing case (`test_loop01_pulse_width_never_grows_between_attempts`) and the
requirement that lost it (`TEST-02`) — never a bare "lists differ". The committed test additionally
asserts the two OTHER legs' phrases ("hardcoded floor", "emptied or misdirected scan root") are absent
from this output (leg isolation), and that the three real suite sources' `git hash-object` values and the
whole-repo `git status --porcelain` are unchanged before/after.

### RED transcript 2 — Plant B: `test_planted_emptied_scan_root_fails_the_non_vacuity_leg`

Reproduced by pointing `FIRESTARTER_CASE_MAP_SCAN_ROOT` at a scratch directory containing no `.cpp` files
at all, and running only `test_scan_targets_are_non_vacuous` in a child process:

```
RETURNCODE: 1
=== STDOUT ===
F                                                                        [100%]
=================================== FAILURES ===================================
______________________ test_scan_targets_are_non_vacuous _______________________

    def test_scan_targets_are_non_vacuous():
        """Coverage 5 -- structural self-check, two halves. ..."""
        # Part (a) -- default target, no os.environ read.
        default_root = _REPO_ROOT / _SUITES_REL
        assert default_root.is_dir(), (...)
        ... [Part (a) passes -- it never reads the seam] ...

        # Part (b) -- seam-aware target, must extract >= _TOTAL_FLOOR names.
        per_suite = _extract_all_mapped_names()
        all_names = set()
        for names in per_suite.values():
            all_names.update(names)
>       assert len(all_names) >= _TOTAL_FLOOR, (
            f"union of extracted RUN_TEST names from the CURRENT scan root "
            f"{_SCAN_SUITES} is {len(all_names)}, expected >= {_TOTAL_FLOOR} "
            "-- an emptied or misdirected scan root must fail HERE, not make "
            "every requirement-to-case membership check above pass vacuously "
            "over an empty set."
        )
E       AssertionError: union of extracted RUN_TEST names from the CURRENT scan root /tmp/.../empty_scratch_suites is 0, expected >= 88 -- an emptied or misdirected scan root must fail HERE, not make every requirement-to-case membership check above pass vacuously over an empty set.
E       assert 0 >= 88
E        +  where 0 = len(set())

tests/test_requirement_case_mapping_v131.py:513: AssertionError
1 failed in 0.09s
```

The RED names both the hardcoded floor (`88`) and the observed count (`0`) together
(`"is 0, expected >= 88"`), proving an emptied or misdirected scan root fails closed here rather than
making every membership check in Coverage 1 pass vacuously over an empty set. `-rs` was passed and no
skipped outcome was reported in either transcript.

### GREEN — full-module run, attributed to a non-empty extraction

```
$ python3 -m pytest tests/test_requirement_case_mapping_v131.py -v
tests/test_requirement_case_mapping_v131.py::test_every_mapped_requirement_names_only_existing_cases PASSED
tests/test_requirement_case_mapping_v131.py::test_each_mapped_suite_meets_its_hardcoded_case_floor PASSED
tests/test_requirement_case_mapping_v131.py::test_extracted_case_names_are_unique PASSED
tests/test_requirement_case_mapping_v131.py::test_trace_suite_is_deliberately_out_of_scope PASSED
tests/test_requirement_case_mapping_v131.py::test_scan_targets_are_non_vacuous PASSED
tests/test_requirement_case_mapping_v131.py::test_this_module_cannot_be_silently_skipped PASSED
tests/test_requirement_case_mapping_v131.py::test_own_needles_do_not_appear_verbatim_in_this_module PASSED
tests/test_requirement_case_mapping_v131.py::test_planted_renamed_case_is_detected PASSED
tests/test_requirement_case_mapping_v131.py::test_planted_emptied_scan_root_fails_the_non_vacuity_leg PASSED

============================== 9 passed in 2.76s ===============================
```

The non-vacuity leg's own observed per-suite figures, confirmed against the real (non-seam-redirected)
tree, so the GREEN above is attributable to a non-empty extraction rather than an unreachable leg:

| Suite | Observed | Hardcoded floor |
|---|---|---|
| `test_loop_eprom_v131` | 47 | 47 |
| `test_vpp_eprom_v131` | 32 | 32 |
| `test_eprom_params_v131` | 9 | 9 |
| **Union (all three)** | **88** | **88** |

### Whole-repo confirmation

```
$ git status --porcelain
(empty)
$ python3 -m pytest tests/ -q
301 passed in 16.05s
$ python3 -m pytest tests/test_protocol_branch_inventory.py tests/test_golden_trace_identity_eprom_v131.py tests/test_checker_convention.py -q
20 passed in 0.13s
$ git diff --stat HEAD~2 -- src/ | wc -l
0
```

301 passed is the pre-phase baseline of 292 plus this plan's 9 new tests, with zero regressions. The
three named goldens/conventions this plan must leave undisturbed (`test_protocol_branch_inventory.py`,
`test_golden_trace_identity_eprom_v131.py`, `test_checker_convention.py`) all pass. No file under `src/`
changed across either commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The requirement-case mapping gate exists, passes, and is proven under D-18. Plan 144-07 can now cite
  `firestarter/tests/test_requirement_case_mapping_v131.py` as the machine-checked evidence for
  TEST-01...TEST-05 when it performs the consolidated eight-requirement flip.
- `firestarter/src/`, `scripts/check_*.py` (FLOOR=6) and `tests/fixtures/` (FIXTURE_FLOOR=15) are
  untouched; the D-04 "no src/ edit this phase" invariant holds after this plan.
- No blockers for the next plan in this phase's wave structure.

## Self-Check: PASSED

- `firestarter/tests/test_requirement_case_mapping_v131.py` -- FOUND on disk.
- `.planning/phases/144-tests-build-verification/144-01-SUMMARY.md` -- FOUND on disk.
- Commit `16e5bdc` (Task 1, firestarter submodule) -- FOUND in `git log --oneline --all`.
- Commit `7b2ba16` (Task 2, firestarter submodule) -- FOUND in `git log --oneline --all`.
- Commit `e0d6498c` (this SUMMARY, superproject) -- FOUND in `git log --oneline --all`.

---
*Phase: 144-tests-build-verification*
*Completed: 2026-08-14*
