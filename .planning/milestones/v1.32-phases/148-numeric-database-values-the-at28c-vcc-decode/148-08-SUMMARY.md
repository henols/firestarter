---
phase: 148-numeric-database-values-the-at28c-vcc-decode
plan: 08
subsystem: database
tags: [ast-gate, source-scan, non-vacuity, review-artifact, changelog, chip_database]

requires:
  - phase: 148-06
    provides: "build_db.py's _VCC_MARGIN_RAIL_MV substitution and diff_db.py's RULE_VCC_MARGIN_RAIL bucket (56 movers), plus 148-DB-DIFF.md's Before/Wire-equivalence/RED-GREEN sections"
  - phase: 148-07
    provides: "full app suite restored to 1633 passed / 0 failed; frozen field-inventory golden re-derived"
provides:
  - "tests/test_numeric_schema_source_scan.py: whole-file coercion-token scans (database.py, audit_coverage_matrix.py), _PAGE_SIZE_BY_PART==2 import assertion, a tree.body-only AST walk asserting no new module-level part-keyed dict in build_db.py, and two non-vacuity legs proving both scan helpers can fail"
  - "148-DB-DIFF.md completed: full 56-chip mover list by manufacturer+algorithm, the D-03 justification with its minipro citation and the three rejected alternatives' measured blast radii (85/84/225, 167 UV-EPROMs), and the corrected 28-chip (16+12) vcc==5500 non-claim"
  - ".planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md: the deferred group filed with exact counts and full part lists"
  - "README.md's Breaking Changes (v1.32) section: the numeric schema break (D-10, no tolerant reader) and the AT28C VCC correction (5.0v, not a write-path fix)"
  - "REQUIREMENTS.md: DATA-03 and DATA-04 marked Complete -- all five DATA-01..05 requirements now Complete"
affects: []

tech-stack:
  added: []
  patterns:
    - "AST gate scoping via tree.body (not ast.walk) to distinguish module-level constructs from nested locals -- keeps the DATA-04 gate from firing on the pre-existing local _AT28C_DIP24_NAMES (Phase 76 physical-adapter set, nested inside a for loop) while still catching any genuinely new module-level part-keyed dict"
    - "Closed-enumeration exclusion list (_KNOWN_MODULE_LEVEL_DICT_NAMES) rather than a heuristic filter -- a legitimate new module-level dict must be added to the list in an explicit reviewed commit, never silently grandfathered in"

key-files:
  created:
    - firestarter_app/tests/test_numeric_schema_source_scan.py
  modified:
    - .planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md
    - .planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md
    - firestarter_app/README.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The AST gate for DATA-04 walks only tree.body (top-level module statements), never ast.walk -- this is what excludes _AT28C_DIP24_NAMES (a local variable nested several indent levels inside a for loop in main(), addressing an unrelated Phase 76 D-03 physical-adapter classification) while still catching a genuinely new module-level dict, since any real generator lookup table is module-level by construction. Proved both directions: confirmed _AT28C_DIP24_NAMES is NOT in the tree.body scan output today, and planted a scratch-copy _FOO_BY_PART module-level dict which WAS caught as 'unexpected'."
  - "The exclusion set for test 4 is a closed enumeration (_KNOWN_MODULE_LEVEL_DICT_NAMES = {_PAGE_SIZE_BY_PART, PROTOCOL_MAP, VPP_MV, NMOS_TRUE_VPP_MV, VCC_VOLTAGES}), derived by ast-parsing the live tools/build_db.py and listing every top-level Dict-valued Assign/AnnAssign name found today, not guessed. NMOS_TRUE_VPP_MV is itself string-keyed by part number (M2716/M2732/M2732A) but is a small, cited, pre-existing NMOS VPP correction table, not a per-chip guess table -- included in the known set per the plan's explicit instruction, distinguished from _PAGE_SIZE_BY_PART only in that it predates this phase's flagged-exception discipline."
  - "148-DB-DIFF.md's 56-chip mover list, manufacturer breakdown, and 28-chip non-claim lists were all re-derived programmatically this plan (matched on (manufacturer, part_number, index) against the un-re-pinned baseline, since part_number strings are not unique across manufacturers -- M28010 appears under both SGS-THOMSON and ST, each a distinct database row and each independently a mover) rather than copied from prior plans' prose, confirming the manufacturer distribution (ATMEL 20, CATALYST(CSI) 11, XICOR 9, WED 4, NEC 3, SAMSUNG 2, ST 2, AMD 1, CYPRESS 1, HITACHI 1, MAXWELL 1, SGS-THOMSON 1 = 56) matches 148-CONTEXT.md D-03's prediction exactly once manufacturer identity (not just part-number string) is preserved through the match."
  - "The vcc==5500 non-claim's superseded '29 chips' heading (Plan 06's original text) was corrected in-place with an explicit dated correction note pointing to the new, accurate ## Non-claim section, rather than deleted -- preserving the historical record of what was measured when, per this project's established practice of documenting corrections rather than silently overwriting them."

requirements-completed: [DATA-03, DATA-04]

coverage:
  - id: D1
    description: "tests/test_numeric_schema_source_scan.py (8 tests): whole-file scans of database.py (3 forbidden tokens, parametrized) and audit_coverage_matrix.py (parse_pulse_us) for the deleted coercion layer; _PAGE_SIZE_BY_PART pinned at exactly 2 entries via live import; a tree.body-only AST walk of build_db.py asserting the module-level dict-constant name set is exactly the 5 known today (no new part-keyed sibling); two non-vacuity legs proving both scan helpers (_find_forbidden_tokens, _top_level_dict_constant_names) can actually report a violation on synthetic/planted input, not just always pass"
    requirement: "DATA-03"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_numeric_schema_source_scan.py -o addopts=\"\" -v -- 8 passed; ruff check + format --check clean; live scratch-copy plant of _FOO_BY_PART = {\"W29C040\": 1} onto a copy of the real tools/build_db.py, re-run against the real _top_level_dict_constant_names helper -- confirmed RED (unexpected={'_FOO_BY_PART'}), then discarded (scratch dir removed, git diff --quiet tools/build_db.py confirmed clean); confirmed _AT28C_DIP24_NAMES absent from the tree.body scan of the real, unmodified build_db.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "build_db._PAGE_SIZE_BY_PART verified at exactly 2 entries and confirmed to not gain an undeclared sibling -- DATA-04's flagged pre-existing exception stays a singular exception"
    requirement: "DATA-04"
    verification:
      - kind: unit
        ref: "tests/test_numeric_schema_source_scan.py::test_page_size_by_part_has_exactly_two_entries and ::test_build_db_has_no_new_module_level_part_keyed_dict -- both pass"
        status: pass
    human_judgment: false
  - id: D3
    description: "148-DB-DIFF.md completed with all required sections (## Before, ## Wire equivalence, ## The 56 movers, ## Why this condition, ## Non-claim, ## Evidence Ceiling) reviewable as a single whole document: the 56-chip mover list by manufacturer+algorithm, the D-03 justification with its minipro database.c#L130-L135 citation and the three rejected alternatives' measured blast radii (type-keyed 85/16-set-to-3.3V, algorithm-keyed 84/16-set-to-3.3V, relation-keyed 225/167-UV-EPROMs-swept-in), and the corrected 28-chip (16+12, not 29) vcc==5500 non-claim with full part lists and the explicit statement that gh#21/#32/#11/#12 stay open and 0x0D stays unverified"
    requirement: "DATA-05"
    verification:
      - kind: unit
        ref: "grep-based header/content assertions (the plan's own <verify> block) all pass: all 6 required ## headings present, X88C64 and AT28C present, tl866ii_vcc_voltages present, 85/225/167/5500/3300 all present, 'not a real voltage' present as a contiguous phrase, and the negative assertion (no gh# closure claim, no 0x0D-verified claim) holds"
        status: pass
    human_judgment: false
  - id: D4
    description: "Deferred vcc==5500 group filed as .planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md with exact counts (16+12=28), full part lists for both sub-groups, and the reason it is not fixed (algorithm 0x07's vdd is non-uniform -- both 5500 and 6500 across chips in that family -- so the substitution target is unproven, unlike the 56-chip case)"
    requirement: "DATA-05"
    verification:
      - kind: unit
        ref: "test -f + front-matter/content grep assertions from the plan's <verify> block all pass"
        status: pass
    human_judgment: false
  - id: D5
    description: "README.md's new Breaking Changes (v1.32) section, inserted immediately above Breaking Changes (v1.20), states both the breaking numeric schema (vcc_mv/pulse_duration_us, stale ~/.firestarter/database.json overrides no longer load, loud failure not silent mis-resolve) and the AT28C VCC correction (4.0v -> 5.0v), explicitly disclaiming any write-path fix. No CHANGELOG.md created."
    requirement: "DATA-01"
    verification:
      - kind: unit
        ref: "grep-based assertions from the plan's <verify> block: v1.32 heading present and ordered before v1.20; section contains vcc_mv, pulse_duration_us, ~/.firestarter/database.json path, 5.0v, and 'verify' (case-insensitive); no CHANGELOG.md file exists"
        status: pass
    human_judgment: false
  - id: D6
    description: "Full app suite at ZERO failures: 1641 passed (up from Plan 07's 1633 -- +8 net new passing tests, this plan's own test_numeric_schema_source_scan.py module). Database byte-reproducible from the committed generator; GATE-02 (diff_db.py) exit 0 with RULE_VCC_MARGIN_RAIL still 56; GATE-03 (check_dispatch.py) exit 0, 0 violations, byte-unchanged; pinned baseline byte-unchanged; ruff clean on firestarter/ and tests/"
    requirement: "DATA-05"
    verification:
      - kind: unit
        ref: "python3 -m pytest -o addopts=\"\" -q -- 1641 passed, 1 warning, 210.53s (0:03:30), 32 snapshots passed; python3 tools/build_db.py && git diff --quiet firestarter/data/chip_database.json -- clean; python3 tools/diff_db.py -- EXIT=0, RULE_VCC_MARGIN_RAIL (56 chips); python3 tools/check_dispatch.py -- EXIT=0, 0 violations; git diff --quiet tools/check_dispatch.py and tools/baseline/chip_database.baseline.json -- both clean; python3 -m ruff check firestarter/ tests/ and ruff format --check -- both clean; tests/test_chip_database_field_inventory.py -- 8 passed"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-19
status: complete
---

# Phase 148 Plan 08: Permanence Gates, Review Artifact Closure & Breaking-Change Changelog Summary

**Closed DATA-03 and DATA-04 with assertions rather than assurances (a tree.body-scoped AST gate that catches a new part-keyed dict without firing on the pre-existing local `_AT28C_DIP24_NAMES`, plus two proven-capable-of-failing token scans), completed `148-DB-DIFF.md` into a single reviewable document with the corrected 28-chip (not 29) deferred non-claim, and stated the breaking numeric schema and AT28C VCC correction in README's changelog surface — full suite now 1641 passed, 0 failed, all five DATA-01..05 requirements Complete.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-08-19T13:20:00Z (approx)
- **Completed:** 2026-08-19T14:10:00Z (approx)
- **Tasks:** 3 completed
- **Files modified:** 4 (1 new)

## Accomplishments

- Wrote `tests/test_numeric_schema_source_scan.py` (8 tests, all passing): whole-file token scans of `database.py` (`_parse_pulse_duration`, `.replace("V"`, `vpp_volts`, parametrized so a failure names the exact token) and `audit_coverage_matrix.py` (`parse_pulse_us`); a live-import assertion that `_PAGE_SIZE_BY_PART` still has exactly 2 entries; a `tree.body`-only AST walk of `build_db.py` asserting the module-level dict-constant name set is exactly the 5 known today (`_PAGE_SIZE_BY_PART`, `PROTOCOL_MAP`, `VPP_MV`, `NMOS_TRUE_VPP_MV`, `VCC_VOLTAGES`); and two non-vacuity legs proving both scan helpers can actually detect a planted violation.
- Confirmed the scoping line directly, both ways: ran the real AST-walk helper against the unmodified `tools/build_db.py` and verified `_AT28C_DIP24_NAMES` (a Phase 76 D-03 local variable, nested inside a `for` loop deep in `main()`, addressing an unrelated physical-DIP24-adapter classification) is **absent** from the top-level scan output — then, separately, copied `tools/build_db.py` to a scratch dir, appended `_FOO_BY_PART = {"W29C040": 1}` at module level, re-ran the same helper against the planted copy, and confirmed it **is** caught (`unexpected={'_FOO_BY_PART'}`) — RED confirmed, then the scratch copy was discarded and `git diff --quiet tools/build_db.py` reconfirmed the real file untouched.
- Completed `148-DB-DIFF.md` with all six required `##` sections reviewable as one document: `## The 56 movers` (full per-chip list re-derived programmatically from the live database against the un-re-pinned baseline, matched on `(manufacturer, part_number, index)` since part numbers collide across manufacturers — `M28010` appears as two distinct rows under `SGS-THOMSON` and `ST`; this match discipline is what reproduces 148-CONTEXT.md D-03's exact manufacturer breakdown: ATMEL 20, CATALYST(CSI) 11, XICOR 9, WED 4, NEC 3, SAMSUNG 2, ST 2, AMD 1, CYPRESS 1, HITACHI 1, MAXWELL 1, SGS-THOMSON 1); `## Why this condition` (the D-03 justification, its `minipro database.c#L130-L135` citation, and the three rejected alternatives' measured blast radii: type-keyed 85 movers/16 set to 3.3V, algorithm-keyed 84/16, relation-keyed 225/167 UV-EPROMs swept in); and `## Non-claim`, restating the deferred `vcc==5500` group at the corrected **28** chips (16+12, not 29) with full part lists for both sub-groups, the inverted-category-error framing, and the explicit reason it is not fixed (algorithm `0x07`'s `vdd` is non-uniform — both 5500 and 6500 — so the substitution target this group would need is unproven, unlike the 56-chip case). Added a dated correction note above the plan-06-era "29 chips" heading rather than deleting it, preserving the record of what was measured when.
- Filed `.planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md` with the exact 16+12=28 counts, full part lists, the inverted-category-error explanation, and the `0x07` non-uniformity reason it is deferred, cross-referencing `148-DB-DIFF.md`'s `## Non-claim` section.
- Inserted a new `## Breaking Changes (v1.32)` section into `firestarter_app/README.md`, immediately above `## Breaking Changes (v1.20)`, following that section's established shape. Covers two things in one section: the breaking numeric schema (unit-suffixed strings → `vcc_mv`/`vdd_mv`/`vpp_mv`/`pulse_duration_us` integers; a stale `~/.firestarter/database.json` override written against the old schema no longer loads — no tolerant reader, per D-10 — with the upgrade path stated), and the AT28C-family VCC correction (`4.0v` → `5.0v`, framed as a verify-rail-vs-operating-supply data correction, explicitly **not** claiming any write-path fix since `vcc` never crosses the wire). No `CHANGELOG.md` created; no CLI output changed (D-17).
- Full app suite: **1641 passed, 0 failed**, 210.53s — up from Plan 07's 1633/0 baseline (+8 net new passing tests, exactly this plan's own new test module). `tools/build_db.py` regeneration confirmed byte-reproducible (`git diff --quiet firestarter/data/chip_database.json`); `tools/diff_db.py` (GATE-02) exit 0 with `RULE_VCC_MARGIN_RAIL` still 56; `tools/check_dispatch.py` (GATE-03) exit 0, 0 violations, byte-unchanged (`git diff --quiet tools/check_dispatch.py`); the pinned baseline byte-unchanged (`git diff --quiet tools/baseline/chip_database.baseline.json`); ruff check + format clean on `firestarter/` and `tests/`.
- Marked **DATA-03** and **DATA-04** `Complete` in `REQUIREMENTS.md` (both the checkbox list and the traceability table) — hand-edited (not via the `gsd-tools requirements` verb) to avoid the known whole-file-reformat blast radius of that verb, diff confirmed scoped to exactly the 4 intended lines. **All five DATA-01..05 requirements for Phase 148 are now Complete.**

## Task Commits

Each task committed atomically, Tasks 1 and 3 inside the `firestarter_app` submodule on branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`, Task 2 in the meta repo:

1. **Task 1: Assert the deletions and the no-lookup-table rule permanently** — `903d6cc` (test) — `firestarter_app`
2. **Task 2: Complete the D-12 review artifact and file the deferred group** — `80664c9d` (docs) — meta repo
3. **Task 3: State the breaking change to the user and run the phase gate** — `862628f` (docs) — `firestarter_app`

_No REFACTOR commit was needed._

## Files Created/Modified

- `firestarter_app/tests/test_numeric_schema_source_scan.py` — new file, 8 tests: coercion-layer token scans, `_PAGE_SIZE_BY_PART` count assertion, tree.body-scoped AST no-new-part-keyed-dict assertion, two non-vacuity legs
- `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md` — completed with `## The 56 movers`, `## Why this condition`, `## Non-claim` (corrected 28-chip count) sections; superseded "29 chips" heading corrected in place with a dated note, not deleted
- `.planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md` — new file: deferred 28-chip group, exact counts, full part lists
- `firestarter_app/README.md` — new `## Breaking Changes (v1.32)` section (numeric schema break + AT28C VCC correction)
- `.planning/REQUIREMENTS.md` — DATA-03 and DATA-04 flipped to `[x]`/Complete (checkbox list + traceability table)

## Decisions Made

- The DATA-04 AST gate scopes to `tree.body` only (never `ast.walk`), which is what excludes the pre-existing local `_AT28C_DIP24_NAMES` while still catching any genuinely new module-level part-keyed dict; proved both directions (see Accomplishments).
- The known-dict exclusion set for that gate is a closed enumeration derived from the live source, not a heuristic — `NMOS_TRUE_VPP_MV` is included despite being string-keyed by part number because it is a small, cited, pre-existing NMOS VPP correction table (not a per-chip guess table), distinguishing it from the kind of table DATA-04 forbids.
- The mover list and both non-claim sub-group lists were re-derived programmatically against the un-re-pinned baseline this plan, matched on `(manufacturer, part_number, index)` rather than part_number alone — part numbers are not unique across manufacturers (`M28010` under both `SGS-THOMSON` and `ST`), and a naive part_number-only match silently collapses duplicate manufacturer identities, which is exactly the kind of measurement error this project's "measure it, don't argue it" discipline exists to catch.
- The superseded "29 chips" heading in `148-DB-DIFF.md` (written during Plan 06, before RESEARCH F-6's correction was available) was corrected in place with a dated note rather than deleted, preserving the historical record.

## Deviations from Plan

None — plan executed exactly as written. The plan's own acceptance criteria and `<verify>` blocks were satisfied on the measurements taken; no locator fix, no re-scoping, and no auto-fix beyond what the plan's `<action>` blocks already specified was required.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Requirements Handling

**DATA-03 and DATA-04 are marked `Complete`** in both `REQUIREMENTS.md`'s checkbox list and its traceability table, per this plan's explicit closing instruction — this is the last plan claiming both requirements. **All five Phase 148 requirements (DATA-01, DATA-02, DATA-03, DATA-04, DATA-05) are now `Complete`.** `roadmap.update-plan-progress` was run to update the Phase 148 plan-count row.

## Next Phase Readiness

Phase 148 (Numeric Database Values & the AT28C VCC Decode) is complete: 8/8 plans, all 5 requirements Complete, full suite at 1641 passed / 0 failed, all four gates (GATE-02, GATE-03, the frozen field-inventory golden, and this plan's own two new source-scan/AST gates) green with non-vacuity proofs on file. The deferred `vcc==5500` high-margin-verify-rail group (28 chips) is filed as a pending todo, not fixed, with the reason (algorithm `0x07`'s non-uniform `vdd`) stated for whichever future phase picks it up. No blockers for phase close.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter_app/tests/test_numeric_schema_source_scan.py` (8 tests, all pass)
- FOUND: `/workspaces/.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md` (all 6 required `##` headings present)
- FOUND: `/workspaces/.planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md`
- FOUND: `## Breaking Changes (v1.32)` in `/workspaces/firestarter_app/README.md`, ordered before `## Breaking Changes (v1.20)`
- FOUND commit `903d6cc` (firestarter_app, Task 1)
- FOUND commit `80664c9d` (meta repo, Task 2)
- FOUND commit `862628f` (firestarter_app, Task 3)
- FOUND: `.planning/REQUIREMENTS.md` DATA-03/DATA-04 both `[x]`/Complete

All items verified present on disk and in git history. No missing items.

---
*Phase: 148-numeric-database-values-the-at28c-vcc-decode*
*Completed: 2026-08-19*
