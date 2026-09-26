---
phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim
plan: "02"
subsystem: firmware-build-gates
tags: [avr-nm, symbol-table, link-time-gate, checker-convention, pytest, dead-code-elimination]

requires:
  - phase: "155-01"
    provides: "Authoritative before-figures record (7 heap matches, 11 sixty-four-bit matches, both anchors, 438 B / 528 B totals, FW_PRE_SHA)"
provides:
  - "firestarter/scripts/check_no_heap_or_64bit_symbols.py — link-time DEAD-01/DEAD-03 gate reading avr-nm's symbol table over all three AVR targets (or committed --nm-output text captures)"
  - "firestarter/tests/test_check_no_heap_or_64bit_symbols.py — 9-leg anti-hollow pairing proving the gate RED against a real pre-change listing and GREEN on a clean one"
  - "firestarter/tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/ — the real, unedited avr-nm stdout for the pre-change uno ELF plus its README"
  - "tests/test_checker_convention.py FLOOR 6->7, FIXTURE_FLOOR 15->16, with the pre-existing Phase 153 drift recorded rather than silently absorbed"
affects: ["155-03", "155-04", "155-05", "155-06"]

tech-stack:
  added: []
  patterns:
    - "avr-nm invoked as a subprocess (list-form, never shell=True) to witness link-time symbol absence — a capability with no precedent in either repo, explicitly not claimed as discharging backlog 999.15 / gh#8"
    - "--nm-output TARGET=PATH seam lets a gate read a committed text capture of toolchain output instead of invoking the toolchain, keeping the paired pytest hermetic in a CI leg with no AVR toolchain"
    - "Never-vacuous non-vacuity anchors (mem_util_blank_check, rurp_read_voltage_mv) checked only on the otherwise-clean path, after violations are reported unconditionally and first"

key-files:
  created:
    - firestarter/scripts/check_no_heap_or_64bit_symbols.py
    - firestarter/tests/test_check_no_heap_or_64bit_symbols.py
    - firestarter/tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/README.md
    - firestarter/tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/avr-nm-uno.txt
  modified:
    - firestarter/tests/test_checker_convention.py

key-decisions:
  - "Asserted all ELEVEN 64-bit symbols (OQ-2, locked), not the eight DEAD-03 names — a gate over only the eight could pass with 90 B (__umulsidi3 2 B, __umulsidi3_helper 84 B, __ashrdi3 4 B) still linked. Both totals recorded in the source comment: 438 B named-subset, 528 B full contiguous blob."
  - "Raised FLOOR 6->7 and FIXTURE_FLOOR 15->16 (not re-anchored to the live 8/30 count) and recorded the pre-existing Phase 153 drift (check_erase_no_vpp.py landed at 5bfae80 without a floor bump) as a named Phase 158 carry-forward, per the plan's explicit instruction not to unilaterally close that gap here."
  - "Manual argv parser (house convention per check_release_assets.py/check_size_baseline.py), not argparse — check_erase_no_vpp.py's argparse precedent noted and deliberately not followed."
  - "avr-nm resolution is lazy: only required when at least one target is NOT covered by --nm-output, so the fully-hermetic pytest path never needs the toolchain present."

requirements-completed: []  # DEAD-01/DEAD-03 NOT marked complete here -- see "Deviations from Plan" #1

coverage:
  - id: D1
    description: "Link-time gate asserting zero heap-set and zero 64-bit-set symbols across all AVR targets named in size_baseline.json's avr_targets, fail-closed on five distinct paths"
    requirement: "DEAD-01"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_no_heap_or_64bit_symbols.py (9 legs, all passing)"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_checker_convention.py (7 legs, all passing against FLOOR=7/FIXTURE_FLOOR=16)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Gate asserts all eleven 64-bit runtime symbols (not the eight DEAD-03 names), proven by the planted-negative leg naming __umulsidi3_helper (the 84 B symbol the eight-name list omits) in its FAIL: output"
    requirement: "DEAD-03"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_no_heap_or_64bit_symbols.py::test_planted_prechange_listing_exits_one_and_names_the_symbols"
        status: pass
      - kind: other
        ref: "python3 scripts/check_no_heap_or_64bit_symbols.py --nm-output uno=tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/avr-nm-uno.txt -- exit 1, stdout contains FAIL: and __umulsidi3_helper"
        status: pass
    human_judgment: false
  - id: D3
    description: "Gate reaches exit 0 on a clean listing (not a checker that can only ever fail) and is proven RED end-to-end against the real, live pre-change build root across all three targets"
    requirement: "DEAD-01"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_no_heap_or_64bit_symbols.py::test_derived_clean_listing_exits_zero_and_names_the_target"
        status: pass
      - kind: other
        ref: "python3 scripts/check_no_heap_or_64bit_symbols.py (no args, live pre-change .pio/build) -- exit 1, stdout names uno/uno328pb/leonardo, quoted verbatim below"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-23
status: complete
---

# Phase 155 Plan 02: Symbol-Absence Gate Summary

**Link-time DEAD-01/DEAD-03 gate reading avr-nm's symbol table over all three AVR ELFs, asserting all eleven 64-bit-runtime symbols (not the eight DEAD-03 names) plus the nine-symbol heap set, landed in one commit with its paired pytest, its real pre-change planted fixture, and the two convention-forced floor raises.**

## Performance

- **Duration:** ~35min
- **Completed:** 2026-08-23
- **Tasks:** 1/1 completed
- **Files modified:** 5 (4 created, 1 edited), all in `firestarter`, one commit

## Continuation note

This plan's single commit (`076abc2`) was already present in `firestarter` at the start of this
session — a prior executor run landed Task 1 and was interrupted before writing this SUMMARY.md.
Per house practice ("re-check COMMITS after any interrupt"), this session did not redo the work:
it read the committed script, test module, fixture and convention edit in full, independently
re-ran every verification leg in the plan's `<verify>`/`<acceptance_criteria>` blocks against the
already-landed commit, confirmed all pass, and then produced this record. No code was re-written
and no second commit was made to `firestarter`.

## Accomplishments

- `scripts/check_no_heap_or_64bit_symbols.py` (491 lines): reads `avr-nm --print-size --size-sort -C`
  output (live, via `FIRESTARTER_AVR_NM`, or a committed `--nm-output TARGET=PATH` text capture),
  parses it in Python line-by-line (never a shelled counting grep — the module docstring names the
  zero-match exit-status inversion that would cause), and asserts absence of the 9-symbol heap set
  and the full 11-symbol 64-bit-runtime set across every target in `size_baseline.json`'s
  `avr_targets` keys. Non-vacuity anchors `mem_util_blank_check` and `rurp_read_voltage_mv` are
  checked only on the otherwise-clean path, after violations are reported unconditionally and first.
- `tests/test_check_no_heap_or_64bit_symbols.py` (347 lines, 9 legs, all passing): proves the gate
  RED (exit 1, `FAIL:`, names `__umulsidi3_helper`) against the real committed pre-change listing;
  proves exit 0 reachable on a synthetic clean derivative; covers five distinct exit-2 fail-closed
  paths (missing listing, anchors stripped, malformed argv, empty `avr_targets`, unreadable
  baseline); and carries the two structural legs (`test_scan_targets_are_non_vacuous`,
  `test_this_module_cannot_be_silently_skipped`).
- `tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/avr-nm-uno.txt` — the verbatim
  `avr-nm` stdout for the real, unedited pre-change `uno` ELF, captured at `FW_PRE_SHA`
  `2ad5b322a37ba4a88afd09cc946f5c4114e51483`; independently re-verified this session to contain
  exactly 7 heap-set matches, exactly 11 sixty-four-bit-set matches, and both anchors.
- `tests/test_checker_convention.py`: `FLOOR` 6->7, `FIXTURE_FLOOR` 15->16; docstring updated to
  name the new checker and record the measured actual counts (8 `check_*.py`, 30 `planted_*`) and
  the pre-existing Phase 153 drift (`check_erase_no_vpp.py` landed without a floor bump) as an
  explicitly unremediated Phase 158 carry-forward.
- All five files landed in one commit (`076abc2`), leaving `git -C firestarter status --porcelain`
  empty; no file under `src/`, `include/`, `test/`, `platformio.ini` or `scripts/baseline/` touched.

## Verification performed this session (against the already-landed commit)

- `python3 -m pytest tests/test_check_no_heap_or_64bit_symbols.py tests/test_checker_convention.py -q`
  → **16 passed** (9 new + 7 convention).
- `python3 -m pytest tests/ -q` → **332 passed** (323 baseline + 9 new legs), run after confirming
  the commit was already landed and the tree porcelain (this module's own
  `test_flash_path_record_sync.py` asserts whole-repo git porcelain).
- `pio test -e native` → **172 test cases: 172 succeeded, 17 suites** (unchanged from 155-01 baseline).
- `pio test -e native_nodevtools` → **172 test cases: 172 succeeded, 17 suites** (unchanged).
- Five exit-code paths demonstrated explicitly:
  - `--nm-output uno=<planted fixture>` → exit **1**, stdout: `FAIL: 18 forbidden symbol(s) found:` naming all 7 heap + 11 sixty-four-bit symbols including `__umulsidi3_helper`.
  - `--nm-output uno=/nonexistent/path.txt` → exit **2** (`ERROR: uno: --nm-output listing not found: ...`).
  - `--definitely-not-a-flag` → exit **2** (`ERROR: unrecognized argument: --definitely-not-a-flag`).
  - `test_clean_listing_without_anchors_exits_two` and `test_unreadable_baseline_exits_two` (pytest legs) → both exit 2, independently confirmed passing.
  - `test_derived_clean_listing_exits_zero_and_names_the_target` (pytest leg) → exit 0, `PASS:` reachable, confirmed passing.
- **End-to-end RED against the live pre-change build root** (no args; `.pio/build/{uno,uno328pb,leonardo}` all present and warm from 155-01):
  ```
  FAIL: 54 forbidden symbol(s) found:
    leonardo: __brkval (heap, type B, 2 B)
    ... [18 lines per target, identical symbol set] ...
    uno: __brkval (heap, type B, 2 B)
    ... [18 lines] ...
    uno328pb: __brkval (heap, type B, 2 B)
    ... [18 lines] ...
  exit=1
  ```
  All three env keys derived from `size_baseline.json`'s `avr_targets` (`uno`, `uno328pb`,
  `leonardo`) are named, 18 violations per target (7 heap + 11 sixty-four-bit), 54 total — matching
  155-01's before-figures record exactly.
- Source assertions: `grep -c 'shell=True'` finds exactly one hit, and it is the docstring's own
  prose stating the invariant ("never `shell=True`"), not an actual `subprocess` call — every real
  `subprocess.run` call in the file is list-form. The 11-symbol `DI64_SYMBOLS` frozenset and the
  438 B/528 B/90 B comment naming `__umulsidi3`, `__umulsidi3_helper`, `__ashrdi3` are both present.
- `git -C firestarter log -1 --name-only` for `076abc2` lists exactly the five `files_modified`
  paths and nothing else; `git -C firestarter diff --name-only 2ad5b32 076abc2 -- scripts/baseline/
  src/ include/ test/ platformio.ini` is empty.

## Task Commits

1. **Task 1: Land the symbol-absence gate and all four convention-forced companions in ONE commit** — `076abc2` (test) — landed by a prior, interrupted executor session; contents independently verified in full by this session (see Continuation note above).

**Plan metadata:** committed together with this SUMMARY per the final-commit step (see STATE.md/ROADMAP.md update below).

## Files Created/Modified

- `firestarter/scripts/check_no_heap_or_64bit_symbols.py` — the link-time symbol-absence gate.
- `firestarter/tests/test_check_no_heap_or_64bit_symbols.py` — its 9-leg paired pytest.
- `firestarter/tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/README.md` — fixture provenance.
- `firestarter/tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/avr-nm-uno.txt` — the real pre-change `uno` avr-nm listing.
- `firestarter/tests/test_checker_convention.py` — `FLOOR`/`FIXTURE_FLOOR` raised, docstring updated.

## Decisions Made

- All decisions were made by the plan itself (locked OQ-2, the floor-raise-not-re-anchor rule, the
  manual-argv-parser house convention); this session made no new architectural decisions, only
  verified the already-landed implementation matches every one of them.

## Deviations from Plan

**1. [Rule 4-adjacent — requirements bookkeeping] DEAD-01/DEAD-03 deliberately NOT marked
complete in REQUIREMENTS.md, despite appearing in this plan's `requirements` frontmatter.**
- **Found during:** state-update step (`requirements.mark-complete`).
- **Issue:** REQUIREMENTS.md's own checkbox text for DEAD-01 and DEAD-03 asserts "the image
  contains no `malloc`/`free`/.../`__brkval` symbol" and "the image contains no 64-bit runtime
  helper" respectively. This session's own live end-to-end gate run against the unedited tree
  (see Verification above) shows **54 forbidden-symbol violations across all three targets** —
  the source removals that would make those symbols vanish are plans 04/05's job, not this
  plan's. The plan's Multi-Source Coverage Audit itself frames this plan as covering only
  "REQ DEAD-01 and DEAD-03's link-time halves" (i.e., the gate that will later prove the
  requirement, not the requirement's discharge).
- **Fix:** Ran `requirements mark-complete DEAD-01 DEAD-03`, observed it flip both checkboxes to
  `[x]` and both traceability rows to "Complete", recognised this as premature (a documented
  house pitfall — "Executors prematurely mark multi-plan reqs Complete"), and reverted
  `REQUIREMENTS.md` via `git checkout --` before it was committed. Left both requirements
  `Pending` for plan 05 (source removal) and/or plan 06 (post-change proof) to close honestly.
- **Files affected:** `.planning/REQUIREMENTS.md` (reverted, no net change).
- **Verification:** `git diff .planning/REQUIREMENTS.md` empty after the revert.

---

**Total deviations:** 1 (requirements-bookkeeping correction, no code/gate impact).
**Impact on plan:** None on the shipped artifact — the gate, its tests, its fixture and the
convention floor raise are exactly as the plan specified. The only correction was to this
session's own over-eager state-update step.

## Issues Encountered

**Discovered a pre-landed commit at session start.** `git -C firestarter log --oneline -3` showed
commit `076abc2` (`test(155-02): ...`) already sitting on top of `2ad5b32` (155-01's `FW_PRE_SHA`),
with a clean working tree. This is consistent with a prior executor session having completed
Task 1 and been interrupted before the SUMMARY/STATE/final-commit steps. Resolution: verified the
commit's content matches the plan's `files_modified` list exactly (five files, `git diff` against
`src/`, `include/`, `test/`, `platformio.ini`, `scripts/baseline/` empty), re-ran every automated
verification and acceptance-criteria command from the plan against the live commit, and confirmed
all pass before writing this record — no rework, no second commit.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

The link-time oracle for DEAD-01 and DEAD-03 exists, is fail-closed on five distinct paths, is
proven RED against both a committed real pre-change listing and the live pre-change build root
(54 violations across three targets), and is proven to reach exit 0 on a clean listing. Plan 03
(the DEAD-05 phrasing gate) and plans 04/05 (the actual source removals that must turn this gate
GREEN) can proceed without further gate-authoring work. `firestarter/tests/test_checker_convention.py`
still carries a named, unremediated Phase 153 floor-drift note for Phase 158 to close. No blockers.

---
*Phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: `firestarter/scripts/check_no_heap_or_64bit_symbols.py`
- FOUND: `firestarter/tests/test_check_no_heap_or_64bit_symbols.py`
- FOUND: `firestarter/tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/README.md`
- FOUND: `firestarter/tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/avr-nm-uno.txt`
- FOUND: commit `076abc2` (`git -C firestarter log --oneline --all | grep 076abc2`)
