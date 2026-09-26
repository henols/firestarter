---
phase: 197-the-override-mechanism-and-the-program-pulse
plan: 03
subsystem: database-generator
tags: [python, build_db, chip_database, datasheet-override, fail-closed, gh-70]

# Dependency graph
requires:
  - phase: 197-02
    provides: "tools/datasheet_overrides.json's D-20 public shape; load_datasheet_overrides / apply_datasheet_override wired into the decode loop between classify() and the VPP ceiling check; the six-path overridable decoded view"
provides:
  - "Five OVR-04 fail-closed legs on the override loader/applier: unmatched override key (checked after the whole decode loop via check_all_override_keys_consumed), two keys resolving to the same row+field, an unsorted top-level key order, a per-field type mismatch (bool excluded from the int check), and full structural validation (entry shape, required datasheet/fields, non-empty fields, {was, is} shape, UNSOURCED requires a note) inside load_datasheet_overrides"
  - "NMOS_TRUE_VPP_MV and its 'highest VPP wins' tie-break deleted from tools/build_db.py; six one-row override entries (INTEL/M2716, INTEL/M2732, SGS-THOMSON/M2716, SGS-THOMSON/M2732A, ST/M2716, ST/M2732A) replace it, each on electrical.vpp_mv, each datasheet: UNSOURCED"
  - "tools/datasheet_overrides.json now holds 7 sorted keys, 6 UNSOURCED, none INTEL/M2732A"
  - "18 tests in tests/test_datasheet_overrides.py (10 from 197-02 + 8 new), all passing"
affects: [197-04, 197-05, 197-06]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Multi-repo plan: gsd_run query commit is disabled for this project (it has twice
# self-created a stray gsd/v1.40-... branch), so commits below are measured by hand
# per repo rather than via the SDK ledger, following the 197-01/197-02 precedent.
actuals:
  tokens: 5491
  tasks: 2
  commits: 3
  commits_by_repo:
    firestarter_app: 2
    meta: 1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Whole-file fail-closed validation: legs that need knowledge no single per-field comparison has (an override key that matched nothing across the whole decode loop; two keys racing on one row's field) are checked with a small, independently-testable function (check_all_override_keys_consumed) rather than folded into the per-chip applier, so they stay unit-testable without a network fetch or a full regeneration."
    - "Exact-type comparison (`type(x) is not type(y)`) as the coercion guard: catches both a JSON float against a decoded int and a JSON bool against a decoded int in one check, since Python's `isinstance(True, int)` would silently pass the second case."

key-files:
  created: []
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/tools/datasheet_overrides.json
    - firestarter_app/tests/test_datasheet_overrides.py

key-decisions:
  - "OVR-02 edge probe (plan's flagged_assumption, category unclassified): the per-field no-op check fires on the first redundant field it encounters, so a wholly-redundant entry and a single redundant field inside an otherwise-useful entry are both refused identically — the plan's own text says this ambiguity is carried forward rather than silently decided, and this plan does not resolve it further."
  - "requirements-completed lists only OVR-02 and OVR-04, not OVR-05, despite OVR-05 being in this plan's frontmatter requirements field. OVR-05 is also declared by 197-04's frontmatter (still unexecuted), so the shared-ID gate (#2388) means marking it Complete here would be premature — 197-04 must finish first. REQUIREMENTS.md was hand-edited (OVR-02 and OVR-04 only) rather than via gsd_run query requirements.mark-complete, per this project's standing note that the requirements verb reformats the whole file."
  - "Mid-execution self-correction: an initial edit collapsed a two-line comment ('These defaults are overridden at the two inclusion gates below / and at the NMOS VPP override block...') into one rewritten line, which is a REWRITE (an added '+' comment line), not a pure deletion of the orphaned clause — a violation of the project's absolute no-new-comments rule even though the rewritten text was shorter and factually unchanged. Caught before committing by re-running the staged-comment check; fixed by deleting only the orphaned second line and leaving the first line's text and lack of trailing punctuation exactly as it was. See Deviations below."
  - "gsd_run query commit was not used for any commit in this plan, per this project's standing rule that the verb has twice self-created a stray gsd/v1.40-... branch mid-plan in this repository. All commits were made with plain git commit, with an explicit branch check before and after each one."

patterns-established:
  - "check_all_override_keys_consumed(overrides, consumed_keys) as the reusable shape for a whole-run fail-closed check: pure function, no I/O, called once after the decode loop and before json.dump, independently unit-testable by constructing the two sets by hand."

requirements-completed: [OVR-02, OVR-04]

coverage:
  - id: D1
    description: "Five OVR-04 fail-closed legs added to the override loader/applier: unmatched override key (whole-run, checked after the decode loop), duplicate row+field target (two keys resolving to one row), unsorted top-level key order, per-field type mismatch (float vs int, bool vs int), and full structural validation of the file shape (entry object, required datasheet/fields keys, non-empty fields, {was, is} shape, UNSOURCED requires a non-empty note)"
    requirement: OVR-04
    verification:
      - kind: unit
        ref: "tests/test_datasheet_overrides.py (18 tests, 10 from 197-02 unchanged + 8 new: unmatched key, duplicate target, unsorted file, float-vs-int, bool-vs-int, missing datasheet, missing/empty fields, well-formed multi-entry control)"
        status: pass
      - kind: other
        ref: "cd firestarter_app && python tools/build_db.py, twice in succession — 'git diff --quiet -- firestarter/data/chip_database.json' exits 0 both times (idempotency)"
        status: pass
      - kind: other
        ref: "ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/ — clean; git diff --cached -- '*.py' | grep '^\\+\\s*#' — prints nothing"
        status: pass
    human_judgment: false
  - id: D2
    description: "NMOS_TRUE_VPP_MV moved out of tools/build_db.py as six one-row override entries in tools/datasheet_overrides.json (INTEL/M2716, INTEL/M2732, SGS-THOMSON/M2716, SGS-THOMSON/M2732A, ST/M2716, ST/M2732A), each on electrical.vpp_mv, each datasheet: UNSOURCED with a note naming the inheritance and the cross-application; the 'highest VPP wins' tie-break dissolves entirely under D-01's one-row-per-key shape; regeneration is byte-identical to the database plan 197-02 committed"
    requirement: OVR-05
    verification:
      - kind: other
        ref: "grep -c NMOS_TRUE_VPP_MV tools/build_db.py == 0; python -c \"...len(datasheet_overrides.json)...\" == 7; UNSOURCED count == 6; no INTEL/M2732A key"
        status: pass
      - kind: other
        ref: "the six named rows verified against firestarter/data/chip_database.json: vpp_mv 25000/25000/25000/25000/21000/21000, all support_status supported, all algorithm 11"
        status: pass
      - kind: other
        ref: "python tools/build_db.py; git diff --quiet -- firestarter/data/chip_database.json — exits 0 (byte-identical to 197-02's commit)"
        status: pass
      - kind: unit
        ref: "full 3.11 suite: 'python -m pytest tests/ -o addopts=\"\" -q -rf' -> '2 failed, 2053 passed', both failures in tests/test_wire_dict_equivalence.py and no other module"
        status: pass
    human_judgment: false

duration: ~1h
completed: 2026-09-18
status: complete
---

# Phase 197 Plan 03: The override mechanism and the program pulse Summary

**Hardened the datasheet-override loader with five whole-file/type fail-closed legs under 18 unit tests, then moved `NMOS_TRUE_VPP_MV` out of `tools/build_db.py` as six one-row `UNSOURCED` override entries — a byte-identical regeneration proving the move changed nothing.**

## Performance

- **Duration:** ~1h
- **Started:** 2026-09-18
- **Completed:** 2026-09-18
- **Tasks:** 2 (both `type="auto" tdd="true"`)
- **Files modified:** 3 (1 generator file, 1 override data file, 1 test module) plus 1 gitlink, plus `REQUIREMENTS.md`

## Accomplishments

- **Task 1 — five whole-file/type fail-closed legs, all under unit test:**
  - `check_all_override_keys_consumed(overrides, consumed_keys)`, a new pure function called once after the whole decode loop and before `json.dump`, raises `ValueError` naming every override key that matched no row's `MANUFACTURER/ALIAS` across the run. `apply_datasheet_override` now accepts an optional `consumed_keys` set it adds every matched key to; `main()` threads one shared set through every call.
  - `apply_datasheet_override` now keeps a per-row `written_by` map of `field_path -> entry_key` and raises `ValueError` naming both keys when a second override targets a field a prior key in the same row's alias set already wrote — the `INTEL/M2732` / `INTEL/M2732A` scenario the plan calls out by name.
  - Before comparing `was`/`is` against the live decode, `apply_datasheet_override` now checks `type(was) is not type(live)` and `type(is_) is not type(live)`, raising and naming the row, the field, both types and both values on a mismatch. Exact-type comparison (not `isinstance`) means a JSON `true` against a decoded `int` is caught even though `True == 1` in Python — proven by a test that would otherwise silently corrupt a field via Python's bool/int equality.
  - `load_datasheet_overrides` now runs `_validate_datasheet_overrides_shape` on every load: top-level must be an object; every entry must be an object with `datasheet` and `fields` present; `fields` must be a non-empty object whose every value is a `{was, is}` pair; `datasheet` must be either a repository-relative path that exists under the app root or the exact token `UNSOURCED`; an `UNSOURCED` entry must carry a non-empty `note`; and the top-level key order must equal its own ascending sort, with the raise naming the first position where found and expected diverge.
  - All five raisers match the project's house style: `ValueError`, an implicitly-concatenated f-string, the row/entry identity first, the offending value(s) with `!r`, closing with an em-dash `— refusing to …` clause.
  - `tests/test_datasheet_overrides.py` grew from 10 to 18 tests (all passing): the 10 from plan `197-02` are byte-unchanged and still pass, plus 8 new — unmatched key (proving the raise happens after the loop, not inside `apply_datasheet_override`), duplicate target naming both keys, unsorted file naming the first out-of-order key, float-vs-int type mismatch, bool-vs-int type mismatch, missing `datasheet`, missing/empty `fields`, and a well-formed multi-entry control proving the five legs are not unconditional.
  - Two successive `python tools/build_db.py` runs leave `git diff --quiet -- firestarter/data/chip_database.json` exiting 0 (OVR-04 idempotency).
- **Task 2 — `NMOS_TRUE_VPP_MV` evacuated as six one-row entries:**
  - Regenerating with the hardcode deleted (before writing any override entry) showed all six rows decode to `18000` mV without correction — confirming the source comment's own claim that upstream aliases these NMOS parts under generic 2716/2732 entries and caps them at 18 V. These six `18000` values are the measured `was` figures, not carried over from any document.
  - Six entries added to `tools/datasheet_overrides.json`, sorted ascending alongside the existing `FUJITSU/MBM27C1000` entry (7 keys total): `INTEL/M2716` → 25000, `INTEL/M2732` → 25000, `SGS-THOMSON/M2716` → 25000, `SGS-THOMSON/M2732A` → 21000, `ST/M2716` → 25000, `ST/M2732A` → 21000. No `INTEL/M2732A` entry exists — that alias resolves to the same row as `INTEL/M2732`, and a second entry there is exactly the duplicate-target case Task 1 makes fail closed.
  - Every one of the six carries `"datasheet": "UNSOURCED"`. Each `note` states plainly: the value is inherited verbatim from the deleted `NMOS_TRUE_VPP_MV` hardcode, whose own comment cited an Intel datasheet not vendored in this repository; for the four SGS-THOMSON/ST rows, the note additionally states that an Intel-sourced reading is being applied to a different vendor's part with no vendor-specific datasheet backing it — the exact silent cross-application D-02 exists to expose; and each names what would close it (that vendor's own datasheet, vendored and git-tracked).
  - `_EXPECTED_UNSOURCED_COUNT` in `tests/test_datasheet_overrides.py` moved from 0 to 6.
  - Regenerating with the six entries in place reproduced `firestarter/data/chip_database.json` **byte-identical** to the database plan `197-02` committed (`git diff --quiet` exits 0) — the move contributes zero diff, exactly as D-06 claims.
  - The six named rows verified directly against the regenerated database: all emit the expected `vpp_mv` (25000/25000/25000/25000/21000/21000), all `support_status: supported`, all `programming.algorithm: 11` — none crossed into `vpp-exceeds-max`, confirming the ceiling comparison stayed `>` and not `>=`.
  - Full Python 3.11 suite: **2 failed, 2053 passed** (2045 + 8 new tests from Task 1). Both failures are the same known-red `tests/test_wire_dict_equivalence.py` tests plan `197-02` documented; no other module regressed.

## Task Commits

Each task was committed atomically, inside the submodule (except the gitlink advance):

1. **Task 1: Whole-file fail-closed legs, sort gate, type check, 8 new tests** - `firestarter_app@77c109f` (test)
2. **Task 2: Move `NMOS_TRUE_VPP_MV` into six one-row override entries** - `firestarter_app@047a5bd` (feat)

**Gitlink advance:** `meta@934ee443` (chore: advance firestarter_app gitlink)

**Plan metadata:** committed alongside this SUMMARY.md (see final commit in this plan's history)

_Note: both tasks are `tdd="true"`; correctness was proven via the plan's own `<verify>` automation (regeneration diffs, byte-identity, idempotency, the known-red-window full-suite check, ruff, the no-comments check) plus the new unit tests in `tests/test_datasheet_overrides.py`, rather than a separate RED→GREEN→REFACTOR commit sequence — as in plan `197-02`, the loader/applier functions already existed and the correctness gate for each new leg is its own dedicated unit test (each leg is unreachable against a correct file, so the test IS the RED-then-GREEN proof, executed and inspected before staging rather than committed as a separate RED commit)._

## Files Created/Modified

- `firestarter_app/tools/build_db.py` - deleted `NMOS_TRUE_VPP_MV`, its comment paragraph, the `_nmos_vpp_mv` accumulator and the "highest VPP wins" matching loop; added `_validate_datasheet_overrides_shape`, `check_all_override_keys_consumed`, and extended `apply_datasheet_override` with duplicate-target tracking and exact-type checks; `main()` now threads a shared `_consumed_override_keys` set and calls the whole-run check before the `extra_chips` merge
- `firestarter_app/tools/datasheet_overrides.json` - 6 new entries (`INTEL/M2716`, `INTEL/M2732`, `SGS-THOMSON/M2716`, `SGS-THOMSON/M2732A`, `ST/M2716`, `ST/M2732A`), all `datasheet: UNSOURCED`, sorted ascending alongside the existing `FUJITSU/MBM27C1000` entry (7 keys total)
- `firestarter_app/tests/test_datasheet_overrides.py` - 8 new tests plus updated module docstring; `_EXPECTED_UNSOURCED_COUNT` moved from 0 to 6
- `firestarter_app/firestarter/data/chip_database.json` - regenerated; **byte-identical** to plan `197-02`'s commit (git reports zero diff)
- `firestarter_app` (gitlink in meta repo) - advanced to `047a5bd`
- `.planning/REQUIREMENTS.md` - `OVR-02` and `OVR-04` checked off and marked Complete in the traceability table; `OVR-05` deliberately left Pending (see Decisions Made)

## Decisions Made

- **OVR-02 edge probe left unresolved, as the plan's own `flagged_assumptions` instructs.** The per-field no-op check (`was == is_` inside `apply_datasheet_override`) fires on the first redundant field it reaches within an entry, so a wholly-redundant entry and a single redundant field inside an otherwise-useful entry both abort the build identically. The plan explicitly carries this ambiguity forward rather than deciding it; this plan does not resolve it further.
- **`requirements-completed` lists only `OVR-02` and `OVR-04`**, despite `OVR-05` also appearing in this plan's frontmatter `requirements` field. `OVR-05` is a multi-plan requirement — it also appears in `197-04`'s frontmatter, which has not yet run. Per the shared-ID gate (#2388), marking `OVR-05` Complete here, before `197-04` finishes, would misrepresent phase-wide progress. `REQUIREMENTS.md` was hand-edited rather than via `gsd_run query requirements.mark-complete`, per this project's standing note that the requirements/roadmap verbs reformat the whole file.
- **Mid-execution self-correction on the no-comments rule.** An initial edit to the "Initialize support classification fields" comment block collapsed two lines ("These defaults are overridden at the two inclusion gates below" + "and at the NMOS VPP override block before chip_entry construction.") into a single rewritten line ending in a period. Re-running the staged-comment check (`git diff --cached -- '*.py' | grep '^\+\s*#'`) before committing caught this: the rewritten line is a `+` comment line, which the project's absolute no-new-comments rule forbids even when the content is shorter and factually unchanged. Fixed by deleting only the second (orphaned) line and leaving the first line byte-for-byte as it was, producing a pure deletion with zero `+` comment lines. This is exactly the "delete a clause, do not rewrite" instruction CLAUDE.md gives, applied to a case the plan's own read_first citations did not enumerate line-by-line.
- **`gsd_run query commit` was not used for any commit in this plan**, per this project's standing rule that the verb has twice self-created a stray `gsd/v1.40-...` branch mid-plan in this repository. All commits were made with plain `git commit`, with an explicit branch check (`git rev-parse --abbrev-ref HEAD` + `git symbolic-ref --quiet HEAD`) before and after each one.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, self-caught] Comment rewrite reverted to a pure deletion**
- **Found during:** Task 2, before committing
- **Issue:** An edit collapsing a two-line orphaned comment into one rewritten line added a new `+` comment line to the staged diff, violating the project's absolute no-new-comments rule (a rewrite is not a deletion, even when shorter).
- **Fix:** Reverted to deleting only the orphaned second line, leaving the first line's text and punctuation exactly as it was in the original file.
- **Files modified:** `firestarter_app/tools/build_db.py`
- **Verification:** `git diff -- tools/build_db.py | grep -E '^\+\s*#' | grep -v '^\+\s*#!'` printed nothing before staging; the same check re-run against the staged diff before commit also printed nothing.
- **Committed in:** `047a5bd` (the fix landed before the task's only commit — no separate commit was needed since the error was caught pre-stage)

---

**Total deviations:** 1 auto-fixed (1 self-caught rule-compliance fix, no functional change)
**Impact on plan:** No scope creep; the fix is required for CLAUDE.md compliance and was caught before any commit landed with the violation.

## Issues Encountered

None beyond the self-caught comment-rewrite issue documented above. `gitlab.com` was reachable for every regeneration; the Python 3.11 venv at `/tmp/fs-venv311` (created in plan `197-02`) was reused without modification. The full suite ran to completion in every invocation, each time reporting the known-red window unchanged in shape (only the passed-count grew, from 2045 to 2053, matching the 8 new tests).

## Known Stubs

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `tools/datasheet_overrides.json` now holds 7 entries and the loader/applier enforces all five OVR-04 fail-closed legs plus the sort gate and the type check, all under unit test. `197-04` (also declaring `OVR-05`) and `197-05` build directly on this hardened mechanism without further architectural change.
- `NMOS_TRUE_VPP_MV` is fully evacuated from `tools/build_db.py`; the "highest VPP wins" tie-break no longer exists anywhere in the generator. Two remaining part-specific hardcodes (`_AT28C_DIP24_NAMES`, `_ETYPE_RELABEL`) are explicitly out of scope for this plan per D-07/D-08 (deletions, not moves) and belong to other plans in this phase.
- **The two known-red `tests/test_wire_dict_equivalence.py` tests remain exactly as plan `197-02` left them, still to be closed by `197-06` by name:**
  - `tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden_plus_the_149_and_153_and_182_and_194_deltas`
  - `tests/test_wire_dict_equivalence.py::test_exactly_84_records_change_flags_and_no_other_field_moves` (now reports 85, not 84 — unchanged from plan `197-02`'s one-row/one-field delta, since this plan's regeneration is byte-identical)
- No blockers. `197-04` can proceed against a database whose only diff from `70c92ce` is the single row/field plan `197-02` named, and an override mechanism whose fail-closed behavior is fully under CI.

## Self-Check: PASSED

- FOUND: `firestarter_app/tools/datasheet_overrides.json`
- FOUND: `firestarter_app/tests/test_datasheet_overrides.py`
- FOUND: `firestarter_app/tools/build_db.py`
- FOUND commit: `firestarter_app@77c109f`
- FOUND commit: `firestarter_app@047a5bd`
- FOUND commit: `meta@934ee443`
- Both `firestarter_app` and meta repo HEAD confirmed on `v1.40-program-parameter-fidelity`
- Gitlink in meta repo confirmed pointing at `firestarter_app@047a5bd`

---
*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Completed: 2026-09-18*
