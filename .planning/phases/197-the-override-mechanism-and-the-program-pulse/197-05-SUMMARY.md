---
phase: 197-the-override-mechanism-and-the-program-pulse
plan: 05
subsystem: database-generator
tags: [python, build_db, chip_database, datasheet-override, census, regen-diff, gh-70]

# Dependency graph
requires:
  - phase: 197-04
    provides: "A database whose only diffs from 70c92ce are the 9 unsupported_reason string swaps and FM1608's two fields — nothing else moved; build_db.py with all three legacy part-specific hardcodes (NMOS_TRUE_VPP_MV, _AT28C_DIP24_NAMES, _ETYPE_RELABEL) already gone."
provides:
  - "The last two D-19 pulse corrections landed as override entries (FUJITSU/MBM27128 -> 1000 us, FUJITSU/MBM27C1001 -> 500 us); FUJITSU/MBM27C4001 confirmed getting NO entry, with a synthetic test proving the no-op-refusal rule is itself covered"
  - "tools/datasheet_overrides.json now holds 9 sorted entries (6 UNSOURCED, 3 citing tracked PDFs); tests/test_datasheet_overrides.py grew to 20 tests, entry count pinned at 9"
  - "A frozen, capable-of-failing part-specific-constant census (tests/test_build_db_constant_census.py + tests/golden/build_db_part_specific_constants.json) answers OVR-06: exactly one honest survivor (a DIP28 pinout-family prefix test, not a chip part number), named with a reason"
  - ".planning/phases/197-the-override-mechanism-and-the-program-pulse/197-REGEN-DIFF.md: the measured 746-row regeneration diff against 70c92ce — 13 changed rows, 0 support_status changes, every field attributed to a decode rule or a datasheet-citing override"
affects: [197-06, 197-07, 198, 199, 200]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Multi-repo plan: gsd_run query commit disabled for this project per its standing note
# (has twice self-created a stray gsd/v1.40-... branch); commits measured by hand per
# repo, following the 197-01/02/03/04 precedent.
actuals:
  tokens: 9200
  tasks: 3
  commits: 5
  commits_by_repo:
    firestarter_app: 2
    meta: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Shape-based literal census over parsed AST, not a name-based grep: find_part_specific_constants() ast-walks every ast.Constant string value against a part-number shape (letters, then digits, then a short alphanumeric tail), then subtracts a frozen allow-list by exact equality — fails closed against a rename the way a hardcoded regex on a specific identifier cannot, and is proven capable of firing with a planted-literal test rather than merely claimed to cover."
    - "Report an honest survivor rather than tuning the detector to make it disappear: the census's shape pattern incidentally matched a pinout-family prefix test (\"DIP28\") that is not a part number at all. Per this plan's own instruction, the pattern was left unchanged and the survivor was named in the golden with a reason, instead of narrowing the shape to hide the finding."
    - "Field-path regeneration diff on a (manufacturer, part_number) key, asserting key-set equality BEFORE any field comparison, walking the union of both sides' LEAF field paths in sorted order — so an added/removed row surfaces as a key-set mismatch rather than being silently absorbed, and the artifact is byte-reproducible."

key-files:
  created:
    - firestarter_app/tests/test_build_db_constant_census.py
    - firestarter_app/tests/golden/build_db_part_specific_constants.json
    - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-REGEN-DIFF.md
  modified:
    - firestarter_app/tools/datasheet_overrides.json
    - firestarter_app/tests/test_datasheet_overrides.py
    - firestarter_app/firestarter/data/chip_database.json
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The census's shape pattern found one real survivor, \"DIP28\" (from `pinout_key.startswith(\"DIP28\")` in classify()'s SRAM/FRAM re-route arm), against the <behavior> block's stated expectation of zero. Per this plan's own explicit instruction (\"Do not tune the shape pattern to make an inconvenient survivor disappear\") and per must_haves' own allowance (\"Success criterion 2 is satisfied either by an empty list or by a named list with reasons\"), the finding was recorded honestly in the golden with a reason rather than the pattern narrowed to exclude it. It is a pinout-family prefix test, not a chip part number — it selects every DIP28_* pinout key, not one part."
  - "REQUIREMENTS.md hand-edited for OVR-06 and PULSE-02 only, per this project's standing note that the requirements verb reformats the whole file and per the shared-ID gate (#2388): OVR-06 is also declared by 197-01 (finished) and PULSE-02 by 197-02 (finished), so both are now ready. PULSE-03 is also declared by 197-06 (not yet run) and is deliberately left Pending — marking it here would misrepresent phase-wide progress before its second declaring plan finishes."
  - "gsd_run query commit was not used for any commit in this plan, per this project's standing rule that the verb has twice self-created a stray gsd/v1.40-... branch mid-plan in this repository. All commits were made with plain git commit, with an explicit branch check before and after each one."
  - "The regeneration diff script counts only LEAF field paths (a value that is not itself a dict), not intermediate object-level paths — an initial draft double-counted each changed row (once at the leaf, once at the containing 'programming'/'electrical' object), which would have produced 18 table lines instead of the correct, exactly-attributable 14."

requirements-completed: [OVR-06, PULSE-02]

coverage:
  - id: D1
    description: "Two remaining D-19 pulse corrections landed: FUJITSU/MBM27128 200->1000 us (Quick Pro TPW, datasheets/MBM27128.pdf) and FUJITSU/MBM27C1001 100->500 us (datasheets/MBM27C1001.pdf); FUJITSU/MBM27C4001 confirmed getting no entry, with a synthetic test proving the no-op-refusal rule is covered; datasheet_overrides.json holds 9 sorted entries"
    requirement: PULSE-02
    verification:
      - kind: unit
        ref: "tests/test_datasheet_overrides.py (20 tests: 18 from 197-03 + test_mbm27c4001_noop_entry_raises + test_total_entry_count_is_pinned_exactly)"
        status: pass
      - kind: other
        ref: "python tools/build_db.py -> 'Done! ... = 746 total.'; four Fujitsu rows read pulse_duration_us 1000/500/500/100 with algorithm 7/8/8/8 -> PULSE_OK"
        status: pass
      - kind: other
        ref: "python -c '...' asserting exactly 9 sorted entries, 6 UNSOURCED, 3 citing distinct git-tracked PDF paths -> SORT_OK, CITATIONS_OK"
        status: pass
      - kind: unit
        ref: "pytest tests/ -o addopts='' -q -rf -> 2 failed, 2062 passed; both FAILED lines name tests/test_wire_dict_equivalence.py and no other module"
        status: pass
    human_judgment: false
  - id: D2
    description: "A frozen, capable-of-failing part-specific-constant census answers OVR-06: find_part_specific_constants() ast-walks tools/build_db.py against a part-number shape pattern; golden records exactly one honest survivor (DIP28, a pinout-family prefix, not a part number) with a non-empty reason"
    requirement: OVR-06
    verification:
      - kind: unit
        ref: "tests/test_build_db_constant_census.py (7 tests, all passing): planted-literal-is-reported, allow-list-exact-not-containment, empty-allow-list-still-reports, output-is-sorted, real-source-matches-frozen-golden-exactly, golden-length-is-exact, golden-entries-carry-a-reason"
        status: pass
      - kind: other
        ref: "python -c '...' asserting golden has a meta block, constants is a list, every entry has a non-empty reason -> CENSUS_GOLDEN_OK 1"
        status: pass
      - kind: other
        ref: "ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/ -> clean"
        status: pass
    human_judgment: false
  - id: D3
    description: "197-REGEN-DIFF.md measures and records the 746-row regeneration diff against 70c92ce: 13 changed rows, 0 support_status changes, every one of the 14 changed fields attributed to a decode rule or a datasheet-citing override, both zero-diff claims (six NMOS entries, size-threshold derivation) cited by proving plan/commit"
    requirement: PULSE-03
    verification:
      - kind: other
        ref: "python -c '...' independent measurement: set(fa) == set(fb), len(changed) == 13, no support_status changes -> DIFF_13_0_OK"
        status: pass
      - kind: other
        ref: "grep -c '^|' 197-REGEN-DIFF.md -> 16 (header + separator + 14 changed-field rows)"
        status: pass
      - kind: other
        ref: "grep -qF for 70c92ce, unsupported_reason, pulse_duration_us, electrical.vcc_mv, electrical.type, UNSOURCED -> all found"
        status: pass
    human_judgment: false

duration: ~65min
completed: 2026-09-18
status: complete
---

# Phase 197 Plan 05: The override mechanism and the program pulse Summary

**Landed the final two Fujitsu pulse corrections with the MBM27C4001 no-op explicitly refused, answered OVR-06 with a frozen census that found and named one honest survivor rather than a padded-empty answer, and measured the phase's full 746-row regeneration diff at exactly 13 changed rows and 0 `support_status` changes.**

## Performance

- **Duration:** ~65 min
- **Started:** 2026-09-18
- **Completed:** 2026-09-18T14:09:04Z
- **Tasks:** 3 (two `type="auto" tdd="true"`, one `type="auto"`)
- **Files modified:** 7 (3 new test/golden/artifact files, 3 generator/test/data files, 1 REQUIREMENTS.md), plus 1 gitlink

## Accomplishments

- **Task 1 — the two remaining pulse corrections, and the row that must not get one:**
  - Added `FUJITSU/MBM27128` (`programming.pulse_duration_us` 200 → 1000, citing `datasheets/MBM27128.pdf`, `note` recording both the Quick Pro `TPW = 1 ms ± 50 µs` figure carried and the conventional 50 ms single-shot figure rejected, with the firmware-semantics argument for why) and `FUJITSU/MBM27C1001` (100 → 500, citing `datasheets/MBM27C1001.pdf`) to `tools/datasheet_overrides.json`, keeping all 9 top-level keys in ascending order.
  - Wrote **no** entry for `FUJITSU/MBM27C4001` — its own datasheet confirms the decoded 100 µs is already correct, so an entry would be a no-op D-04 makes a build failure. Added `test_mbm27c4001_noop_entry_raises`, a synthetic no-op entry that asserts `apply_datasheet_override` raises, proving the exclusion rule is itself covered rather than merely obeyed.
  - Added `test_total_entry_count_is_pinned_exactly` (`_EXPECTED_ENTRY_COUNT = 9`) — the plan asked to "update the entry-count assertion... from 7 to 9," but no such assertion existed in the module before this plan (only the `UNSOURCED`-count assertion did); this is a new test, not an edit of an existing one. `_EXPECTED_UNSOURCED_COUNT` stays at 6 — both new entries cite tracked PDFs.
  - Regenerated: `python tools/build_db.py` reports `746 total`. The four Fujitsu rows read `pulse_duration_us` 1000/500/500/100 with `algorithm` 7/8/8/8 — matching D-19 exactly.
  - Full Python 3.11 suite after this task: 2 failed (both `tests/test_wire_dict_equivalence.py`, the known-red window), 2055 passed. No other module regressed.
- **Task 2 — answering OVR-06 with a frozen census that cannot pass vacuously:**
  - `find_part_specific_constants(source_text, allow_list)` in the new `tests/test_build_db_constant_census.py`: `ast.parse`s the given source text, walks every `ast.Constant` string value, keeps those matching the part-number shape (at most 16 characters; up to six ASCII letters, then two to five ASCII digits, then up to eight further ASCII letters or digits), subtracts the allow-list by exact string equality, and returns the ascending-sorted remainder. Takes source text and allow-list as parameters and reads nothing else from disk.
  - Proven capable of failing, not merely claimed to cover: a planted literal (`"AT28C16"`, `"FM1608"`) in synthetic source is reported; a synthetic literal containing an allow-listed string as a prefix (`"AT28C16EXTRA"` against allow-list `{"AT28C16"}`) is still reported, proving exact-equality matching, not containment; an empty allow-list still reports rather than early-returning; multi-value output is proven ascending sorted.
  - Ran the detector against the real, live `tools/build_db.py` with an empty allow-list. **It found one survivor: the literal `"DIP28"`**, from `pinout_key.startswith("DIP28")` inside `classify()`'s SRAM/FRAM 28-pin re-route arm — matching the shape by coincidence (`"DIP"` + `"28"` + zero further characters), not because it names a chip. This is one real survivor, not the empty answer the plan's `<behavior>` block anticipated; per the plan's own explicit instruction not to tune the shape pattern to make an inconvenient survivor disappear, and per the requirement's own stated allowance for a named list with reasons, it was recorded honestly in `tests/golden/build_db_part_specific_constants.json` with a full reason (it is a pinout-*family* selector, not a part number; no alternative representation of "any DIP28-family pinout" avoids the shape match without either abandoning the string-prefix test or building a redundant second family-membership table) rather than narrowed away.
  - `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both clean.
- **Task 3 — measuring and recording the 746-row regeneration diff:**
  - Wrote a throwaway field-path diff script (not committed to `tools/`), full text recorded in the artifact: loads the baseline via `git show 70c92ce:firestarter/data/chip_database.json`, flattens both sides to `(manufacturer, part_number) -> row`, asserts key-set equality before any field comparison, then for each key in `sorted()` order walks the union of both sides' **leaf** dotted field paths (an initial draft counted intermediate object-level paths too, doubling the line count to 18 before this fix — see Deviations) and reports every differing one.
  - **Measured: 746 rows in, 746 rows out, 13 rows changed, 0 `support_status` changes** — confirming D-16 exactly, with no discrepancy to reconcile.
  - All 14 changed fields attributed: 9 `unsupported_reason` string swaps (ATMEL ×4, MICROCHIP memory ×4, NEC ×1) to the hardware-damage guard now being the sole writer since Plan `197-04` deleted the competing name-list arm; `RAMTRON/FM1608`'s `electrical.type` (`FRAM`→`SRAM`) to the same plan's `_ETYPE_RELABEL` deletion letting `classify()`'s natural SRAM arm apply, and its `electrical.vcc_mv` (3300→5000) to the SRAM single-rail rewrite at `build_db.py:773-776` firing as a direct consequence; the 3 `programming.pulse_duration_us` changes to the named override entries and their `datasheet` citations (`FUJITSU/MBM27128`, `FUJITSU/MBM27C1000`, `FUJITSU/MBM27C1001`).
  - Recorded the two zero-diff claims with their proving plan/task/commit: the six NMOS override entries (Plan `197-03` Task 2, `firestarter_app@047a5bd`) and the `_PGM_ON_PIN31_MAX_SIZE` size-threshold derivation (Plan `197-01` Task 3, `firestarter_app@5fec5eb`).
  - Named the honesty limit: the diff proves what moved and why, never that a new value is electrically correct.

## Task Commits

Each task was committed atomically, inside the submodule (except Task 3's artifact and the gitlink advance):

1. **Task 1: Two remaining Fujitsu pulse corrections, MBM27C4001 no-op refused** - `firestarter_app@b864cd7` (feat)
2. **Task 2: Frozen part-specific-constant census answers OVR-06** - `firestarter_app@88d487d` (test)
3. **Task 3: Measure and record the 746-row regeneration diff** - `meta@7bd5790c` (docs)

**Gitlink advance:** `meta@80a5daa5` (chore: advance firestarter_app gitlink)

**Plan metadata:** committed alongside this SUMMARY.md and REQUIREMENTS.md (see final commit in this plan's history)

_Note: Task 1 and Task 2 are `tdd="true"`; correctness was proven via the plan's own `<verify>` automation (regeneration checks, sort/citation checks, the known-red-window full-suite check, ruff, the no-comments check) plus new/updated unit tests, rather than a separate RED→GREEN→REFACTOR commit sequence — as in plans `197-02`/`197-03`/`197-04`, each new leg's correctness gate is its own dedicated, unreachable-against-prior-code assertion, executed and inspected before staging rather than committed as a separate RED commit._

## Files Created/Modified

- `firestarter_app/tools/datasheet_overrides.json` - two entries added (`FUJITSU/MBM27128`, `FUJITSU/MBM27C1001`), 9 sorted keys total
- `firestarter_app/tests/test_datasheet_overrides.py` - `test_mbm27c4001_noop_entry_raises` and `test_total_entry_count_is_pinned_exactly` added; module docstring extended; 20 tests total
- `firestarter_app/firestarter/data/chip_database.json` - regenerated; three `programming.pulse_duration_us` values changed (this plan's two plus 197-02's `MBM27C1000`, already present)
- `firestarter_app/tests/test_build_db_constant_census.py` - new; `find_part_specific_constants()` plus 7 tests across 3 classes
- `firestarter_app/tests/golden/build_db_part_specific_constants.json` - new; `meta` block plus one honest survivor (`DIP28`) with a full reason
- `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-REGEN-DIFF.md` - new; the measured 746-row regeneration diff, reproducible method, full script text, 14-row table, two zero-diff claims, honesty limit
- `.planning/REQUIREMENTS.md` - `OVR-06` and `PULSE-02` checkboxes and traceability-table rows flipped to Complete (both declaring plans now finished); `PULSE-03` deliberately left Pending (197-06 not yet run)
- `firestarter_app` (gitlink in meta repo) - advanced to `88d487d`

## Decisions Made

- **The census's real finding, `"DIP28"`, was recorded rather than engineered away.** The plan's `<behavior>` block anticipated zero survivors against the real source with an empty allow-list; the actual detector found one, a pinout-family prefix test that matches the part-number shape by coincidence. The plan's own instruction — "Do not tune the shape pattern to make an inconvenient survivor disappear; that converts a real finding into a silent exclusion" — and the requirement's own stated tolerance for a named survivor governed this: it went into the golden with a full reason instead of the shape pattern being narrowed to exclude it.
- **A new total-entry-count test was added, not an existing assertion edited**, because `tests/test_datasheet_overrides.py` had no total-count assertion before this plan (only `_EXPECTED_UNSOURCED_COUNT`). The plan's wording ("update the entry-count assertion... from 7 to 9") assumed one already existed; `test_total_entry_count_is_pinned_exactly` with `_EXPECTED_ENTRY_COUNT = 9` was added to satisfy the acceptance criterion's substance.
- **REQUIREMENTS.md hand-edited for OVR-06 and PULSE-02 only**, per this project's standing note that the requirements verb reformats the whole file, and per the shared-ID gate (#2388): both are also declared by an already-finished plan (`197-01`, `197-02` respectively). `PULSE-03` is also declared by `197-06`, not yet run, and is deliberately left Pending.
- **`gsd_run query commit` was not used for any commit in this plan**, per this project's standing rule that the verb has twice self-created a stray `gsd/v1.40-...` branch mid-plan in this repository. All commits were made with plain `git commit`, with an explicit branch check (`git rev-parse --abbrev-ref HEAD` + `git symbolic-ref --quiet HEAD`) before and after each one.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, self-caught] Regeneration-diff script double-counted changed fields at the object level**
- **Found during:** Task 3, before writing the artifact
- **Issue:** The first draft of `field_paths()` recorded both a leaf path (e.g. `programming.pulse_duration_us`) and its containing intermediate object path (`programming`) whenever the object's value differed, producing 18 table lines for what is exactly 14 independently-attributable changed fields — inflating and double-counting the same underlying change.
- **Fix:** `field_paths()` rewritten to collect only leaf paths (a value that is not itself a `dict`), matching the task's own definition of "every changed field."
- **Files modified:** none in either repo — the script is a throwaway, not committed; only its corrected final text is recorded in `197-REGEN-DIFF.md`.
- **Verification:** re-run measured 13 changed rows / 14 changed-field lines / 0 `support_status` changes, matching the independent Python one-liner in the plan's own `<verify>` block exactly.
- **Committed in:** `meta@7bd5790c` (the artifact records only the corrected script)

---

**Total deviations:** 1 auto-fixed (1 self-caught scripting bug in a throwaway, uncommitted tool; no functional or generator-source change)
**Impact on plan:** No scope creep. The corrected script produces exactly the row/field counts D-16 predicted and this plan's own independent verification asserts.

## Issues Encountered

None beyond the self-caught diff-script bug documented above. `gitlab.com` was reachable for the one regeneration this plan ran; the Python 3.11 venv at `/tmp/fs-venv311` was reused without modification; `ruff` 0.16.8 was available in that same venv. The full suite ran to completion in every invocation.

## Known Stubs

None.

## Deleted-comment report (CLAUDE.md "Source code comments — hard rule")

**No comment line was added to any staged `.py` file across all three tasks.** The mandatory check
(`git diff --cached -- '*.py' | grep -E '^\+\s*#' | grep -v '^\+\s*#!'`) printed nothing before every
one of the two `firestarter_app` commits (`b864cd7`, `88d487d`). No existing comment was deleted or
modified in `tools/build_db.py` by this plan — `datasheet_overrides.json` is JSON (no comment syntax),
and the two new test/golden files were both newly created, so there was nothing pre-existing to reflow
or lose an antecedent for.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `tools/datasheet_overrides.json` holds all pulse corrections this phase's in-repo datasheets
  support (3 entries: `FUJITSU/MBM27C1000` from `197-02`, `FUJITSU/MBM27128` and
  `FUJITSU/MBM27C1001` from this plan), plus the 6 `UNSOURCED` NMOS entries from `197-03` — 9 total,
  sorted. `FUJITSU/MBM27C4001` correctly carries no entry.
- OVR-06 is answered: `tests/golden/build_db_part_specific_constants.json` names the one honest
  survivor (`DIP28`) with a reason, under a census proven capable of failing.
- `197-REGEN-DIFF.md` is the measured, reproducible acceptance evidence for the restated OVR-05 and
  for PULSE-03: exactly 13 rows changed, 0 `support_status` changes, 746 in and out, every field
  attributed.
- **The two known-red `tests/test_wire_dict_equivalence.py` tests remain open, to be closed by
  `197-06` by name, exactly as this plan's known-red window specified:**
  - `tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden_plus_the_149_and_153_and_182_and_194_deltas`
  - `tests/test_wire_dict_equivalence.py::test_exactly_84_records_change_flags_and_no_other_field_moves`
- No blockers. `197-06` can measure the real wire-dict delta against a database whose every diff from
  `70c92ce` is now fully accounted for in `197-REGEN-DIFF.md`, and `197-07`'s inventory can cite this
  plan's `FUJITSU/MBM27C4001` datasheet-confirmed-correct finding directly.
- **PULSE-03 stays Pending in `REQUIREMENTS.md`** until `197-06` finishes (shared-ID gate, #2388) —
  not a blocker, just the expected state given `197-06` also declares it.

## Self-Check: PASSED

- FOUND: `firestarter_app/tools/datasheet_overrides.json`
- FOUND: `firestarter_app/tests/test_datasheet_overrides.py`
- FOUND: `firestarter_app/tests/test_build_db_constant_census.py`
- FOUND: `firestarter_app/tests/golden/build_db_part_specific_constants.json`
- FOUND: `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-REGEN-DIFF.md`
- FOUND commit: `firestarter_app@b864cd7`
- FOUND commit: `firestarter_app@88d487d`
- FOUND commit: `meta@7bd5790c`
- FOUND commit: `meta@80a5daa5`
- Both `firestarter_app` and meta repo HEAD confirmed on `v1.40-program-parameter-fidelity`
- Gitlink in meta repo confirmed pointing at `firestarter_app@88d487d`
- Full Python 3.11 suite re-run after all tasks: `2 failed, 2062 passed` — both failures name
  `tests/test_wire_dict_equivalence.py` and no other module
- `.planning/ROADMAP.md` confirmed untouched (`git diff --stat` empty)
- `.planning/STATE.md` confirmed untouched (`git diff --stat` empty)

---
*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Completed: 2026-09-18*
