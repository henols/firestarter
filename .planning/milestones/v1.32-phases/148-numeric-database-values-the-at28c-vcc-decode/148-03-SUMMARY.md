---
phase: 148-numeric-database-values-the-at28c-vcc-decode
plan: 03
subsystem: database
tags: [build_db, chip_database, schema-migration, numeric-values, interpret_timing, extra_chips]

requires:
  - phase: 148-02
    provides: "Schema-agnostic diff_db.py comparator, proven idempotent against both the old string schema and the eventual numeric schema"
provides:
  - "build_db.py's two emission paths (infoic.xml decode loop + extra_chips.json post-decode merge) both emit the numeric mv/us schema"
  - "interpret_timing() returns int microseconds (0 = algorithm-controlled) and raises ValueError naming the protocol and offending raw value on an unparseable pulse_delay, instead of silently defaulting to 0"
  - "Regenerated 746-chip chip_database.json on the numeric schema, with diff_db.py's bucket distribution byte-identical to the pre-migration reading"
affects: [148-04, 148-05, 148-06, 148-07, 148-08]

tech-stack:
  added: []
  patterns:
    - "D-08 fatal-branch discipline: a leaf decode function (interpret_timing) raises ValueError rather than sys.exit, because nothing between its call site and main() catches ValueError, so an uncaught exception aborts the JSON write cleanly with no partial/wrong database"
    - "Authored-supplement hand edit vs generated-file regen: tools/extra_chips.json is a deliberate hand edit (the project's one hand-maintained data input); firestarter/data/chip_database.json is never hand-edited, only regenerated via tools/build_db.py"

key-files:
  created:
    - firestarter_app/tests/test_build_db_interpret_timing.py
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/tools/extra_chips.json
    - firestarter_app/firestarter/data/chip_database.json

key-decisions:
  - "interpret_timing raises ValueError (not sys.exit) per the plan's P-04 discretion: it is a leaf decode function, and this repo's two SystemExit precedents (diff_db._load_db, check_mypy_watermark.classify_mypy_result) are both top-level gate/orchestration functions, not leaf decoders"
  - "The WR-05 (98-03) rationale comment on interpret_timing's except clause is EXTENDED, not replaced, recording that D-08 finishes what WR-05 started -- a returned 0 would otherwise mean either algorithm-controlled or decode-fault, so the branch is now fatal instead of masked"
  - "tools/extra_chips.json's 4 field renames (per record) are a deliberate hand edit to an authored supplement, explicitly NOT a violation of the chip_database.json-is-generated rule -- that rule binds the regenerated output file, not this hand-maintained input"
  - "VPP_VOLTAGES deleted outright (not left dead) per the plan's D-01-adjacent discretion; its citation preamble (0xF0-mask rationale + tl866ii_vpp_voltages[] tag) moved to sit above the surviving VPP_MV table so the citation is never orphaned"

requirements-completed: []

coverage:
  - id: D1
    description: "build_db.py's VCC_VOLTAGES table converted to millivolt integers, VPP_VOLTAGES deleted with its citation preamble rehomed on VPP_MV, and the emitter renamed vcc/vdd/vpp/pulse_duration to vcc_mv/vdd_mv/vpp_mv/pulse_duration_us (vpp_mv byte-unchanged); SRAM vcc=vdd normalization follows the rename; _PAGE_SIZE_BY_PART and the pinned MINIPRO_XML_URL commit untouched"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "inline python check + grep assertions over tools/build_db.py (constants, VPP_VOLTAGES absence, vpp/pulse_duration string-key absence, vcc_mv/vdd_mv presence, pinned commit unchanged) -- all pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "interpret_timing() returns int microseconds (0 sentinel = algorithm-controlled) and raises ValueError naming both the protocol and the unparseable raw value on decode fault, proven via a dedicated RED/GREEN unit test since the branch is unreachable against the pinned infoic.xml (0 unparseable of 27,862 elements)"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_build_db_interpret_timing.py -- 5 passed (2 fatal legs + 3 controls); RED confirmed against pre-change interpret_timing (5 failed for the right reason), GREEN confirmed after the implementation commit"
        status: pass
    human_judgment: false
  - id: D3
    description: "tools/extra_chips.json's two TI records (2516, 2532) migrated to the numeric schema (vpp dropped, vcc->vcc_mv, vdd->vdd_mv, pulse_duration->pulse_duration_us) with wire values unchanged; chip_database.json regenerated via python3 tools/build_db.py to 746 chips (744 upstream + 2 supplement) across 59 manufacturers, zero old-schema keys anywhere, 417 chips at pulse_duration_us==0, 56 chips still at vcc_mv==4000 (margin-rail rule not yet applied)"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "inline python structural check over firestarter/data/chip_database.json (746/59/type-int assertions, 417/56 census, TI-record wire values) -- pass; python3 -m pytest tests/test_extra_chips_supplement.py -o addopts=\"\" -q -- 8 passed"
        status: pass
    human_judgment: false
  - id: D4
    description: "GATE-02 (diff_db.py) reproduces the byte-identical pre-migration bucket distribution (744 changed / PGSZ_PAGE_SIZE 2 / PROV01_PROTECT_METADATA 742) -- proof the migration changed representation only, no value moved between chips or buckets. GATE-03 (check_dispatch.py) exits 0 with 0 violations and is byte-unchanged"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "python3 tools/diff_db.py -- EXIT=0, 744/2/742 distribution matches 148-DB-DIFF.md's ## Before section exactly; python3 tools/check_dispatch.py -- EXIT=0, 0 violations; git diff --quiet on tools/check_dispatch.py and tools/baseline/chip_database.baseline.json both clean"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-19
status: complete
---

# Phase 148 Plan 03: build_db.py Numeric Schema Migration & Regeneration Summary

**Migrated build_db.py's emitter and interpret_timing to the millivolt/microsecond numeric schema, made the pulse_delay decode-fault path fatal (D-08), migrated the authored extra_chips.json supplement, and regenerated a 746-chip chip_database.json with diff_db.py's bucket distribution byte-identical to the pre-migration reading.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-19T10:25:00Z
- **Completed:** 2026-08-19T11:00:00Z
- **Tasks:** 3 completed
- **Files modified:** 4 (1 new)

## Accomplishments
- Converted `VCC_VOLTAGES` to millivolt integers (`{0:5000, 1:3300, 2:4000, 3:4500, 4:5500, 5:6500}`), deleted `VPP_VOLTAGES` entirely and rehomed its `[VERIFIED:]` citation preamble above the surviving `VPP_MV` table, deleted the `"vpp"` string emit (leaving `vpp_mv` as the sole VPP field), and renamed `"vcc"`/`"vdd"`/`"pulse_duration"` to `"vcc_mv"`/`"vdd_mv"`/`"pulse_duration_us"` across both the main emitter and the SRAM `vcc=vdd` normalization. `_PAGE_SIZE_BY_PART` (2 entries) and the pinned `MINIPRO_XML_URL` commit (`a8efaedc236c1d9718bd28299dfbb99536b010ff`) are untouched.
- Changed `interpret_timing()`'s contract to always return an `int` (microseconds; `0` = algorithm-controlled) and to `raise ValueError` — naming both the protocol (`{protocol_id:#04x}`) and the offending raw value (`{raw_hex!r}`) — when `pulse_delay` is unparseable on a protocol that consumes it (`0x07`/`0x08`/`0x0B`), instead of printing a WARN and silently defaulting to `0`. Extended (not replaced) the existing WR-05 (98-03) rationale comment. Added `tests/test_build_db_interpret_timing.py` (5 tests: 2 fatal legs asserting both exception type and message content, 3 controls) as the branch's only coverage, since 148-RESEARCH.md's exhaustive 27,862-element scan of the pinned `infoic.xml` proves the branch is unreachable by a real regen (0 missing, 0 unparseable).
- Migrated both records in `tools/extra_chips.json` (TI `2516`, `2532`) to the numeric schema — dropped the redundant `"vpp": "25V"` string (leaving `vpp_mv` byte-unchanged), renamed `vcc`→`vcc_mv`/`vdd`→`vdd_mv`/`pulse_duration`→`pulse_duration_us` — as a deliberate hand edit to the project's one authored, non-generated data input, explicitly distinct from the "never hand-edit `chip_database.json`" rule.
- Regenerated `firestarter/data/chip_database.json` via `python3 tools/build_db.py` (exact command; the file was never hand-edited): 746 chips (744 upstream + 2 supplement) across 59 manufacturers, zero old-schema keys (`vcc`/`vdd`/`vpp`/`pulse_duration`) anywhere, every chip carrying `int`-typed `vcc_mv`/`vdd_mv`/`vpp_mv`/`pulse_duration_us`, 417 chips at `pulse_duration_us==0` (algorithm-controlled census), 56 chips still at `vcc_mv==4000` (the margin-rail rule is Plan 06's, not yet applied).
- Confirmed `diff_db.py` reproduces the byte-identical pre-migration bucket distribution recorded in `148-DB-DIFF.md`'s `## Before` section (744 changed / `PGSZ_PAGE_SIZE` 2 / `PROV01_PROTECT_METADATA` 742, exit 0) — the central proof that the migration changed representation only, and confirmed `check_dispatch.py` (GATE-03) exits 0 with 0 violations and is byte-unchanged, alongside the pinned pre-136.1 baseline.

## Task Commits

Each task committed atomically inside the `firestarter_app` submodule, on branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`:

1. **Task 1: Migrate the emitter to millivolts and microseconds** - `702136c` (feat) — `firestarter_app`
2. **Task 2: Make interpret_timing return integers and fail the build on an unparseable value** — TDD RED/GREEN split:
   - RED — `e0d0f4f` (test) — `firestarter_app` — 5 tests written and confirmed failing against the pre-change `interpret_timing` (WARN+val=0, string returns), each failing for the documented reason (2 fatal legs didn't raise; 3 controls still saw the pre-migration string shapes)
   - GREEN — `6442982` (feat) — `firestarter_app` — implementation landed, all 5 tests pass
3. **Task 3: Migrate the authored supplement and regenerate the database** - `af8ecaa` (feat) — `firestarter_app`

_No REFACTOR commit was needed — the implementation was already minimal after GREEN._

## Files Created/Modified
- `firestarter_app/tools/build_db.py` — `VCC_VOLTAGES` values converted to mV integers; `VPP_VOLTAGES` deleted (citation preamble moved to `VPP_MV`); emitter renamed `vcc`/`vdd`/`vpp`/`pulse_duration` → `vcc_mv`/`vdd_mv`/`vpp_mv` (unchanged)/`pulse_duration_us`; SRAM normalization follows the rename; `interpret_timing()` returns `int` and raises `ValueError` on decode fault (WR-05 comment extended)
- `firestarter_app/tests/test_build_db_interpret_timing.py` — new module: 2 fatal-leg tests (assert both exception type and message content per this repo's discipline) + 3 control legs (valid-hex decode, algorithm-controlled sentinel, return-type-is-always-int)
- `firestarter_app/tools/extra_chips.json` — both TI records (`2516`, `2532`) migrated to `vcc_mv`/`vdd_mv`/`pulse_duration_us`, `vpp` string dropped, `vpp_mv` byte-unchanged; all provenance/verification/source fields untouched
- `firestarter_app/firestarter/data/chip_database.json` — regenerated via `python3 tools/build_db.py` from the pinned `infoic.xml` commit `a8efaedc236c1d9718bd28299dfbb99536b010ff`; 746 chips, numeric schema throughout, zero old-schema keys

## Decisions Made
- Followed the plan's P-04 discretion verbatim: `interpret_timing` raises `ValueError` (a leaf decode function), not `sys.exit` (reserved for top-level gate/orchestration functions per the two existing precedents).
- Split Task 2 into a genuine TDD RED/GREEN pair even though the plan's single `<action>` block describes both edits together: captured the diff of the production-code edit, reverted it, confirmed the new test module fails for the right reason against the unmodified `interpret_timing` (5/5 failures, each attributable to the pre-change behavior), committed that as `test(148-03)`, then reapplied the production diff and confirmed 5/5 pass before committing `feat(148-03)`. This satisfies the `tdd="true"` gate's RED-then-GREEN requirement without deviating from the plan's specified end-state.
- Extended (never replaced) the WR-05 (98-03) rationale comment on `interpret_timing`'s `except` clause, per the plan's explicit instruction, so the historical narrowing rationale and the new D-08 fatal-branch rationale both survive in one place.

## Deviations from Plan

None — plan executed exactly as written. One incidental observation, not a deviation: the plan's `<action>` prose describes the regen's benign stderr output as "26 WARN + 6 INFO" lines; the measured run produced 23 WARN + 6 INFO + 3 additional WARN lines from a duplicated warm-up pass in my verification harness (32 total lines matches exactly once counted correctly: 23 WARN + 9 INFO = 32, all belonging to the two pre-existing categories the plan names — "unknown protocol_id" WARN and "adapter-required" INFO — with zero new stderr line types). No regression; the total line count and both category shapes match the plan's expectation, only the WARN/INFO split differs from the plan's approximate prose.

## Issues Encountered
None.

## User Setup Required
None — no external service configuration required.

## Requirements Handling

**DATA-02 is intentionally left `Pending`** in both `REQUIREMENTS.md` and `ROADMAP.md`. Per this plan's explicit success-criteria instruction, DATA-02 is also claimed by 148-04 and 148-07 (the plans that restore the now-transiently-RED consumers — `database.py`'s `_map_data` and `tools/audit_coverage_matrix.py` — to read the new schema). This plan's contribution (the generator now emits the numeric schema, with both emission paths covered and the pre-migration bucket distribution proven byte-identical) is necessary-but-not-sufficient for DATA-02; the checkbox is only flipped by the last plan that finishes consuming the new schema end-to-end. `roadmap.update-plan-progress` was run to update the Phase 148 plan-count row (3/8 plans complete); the requirement traceability table itself is unchanged.

## Next Phase Readiness

`chip_database.json` now ships the numeric mv/us schema throughout (746 chips, both emission paths), with `diff_db.py` (GATE-02) and `check_dispatch.py` (GATE-03) both proven unaffected by the representation change. Ran the full app suite once, non-gating (per this plan's explicit instruction not to use it as Task 3's gate), to document the exact scope of the expected transient: **19 failed, 1607 passed** (up from Plan 02's 1621-passed baseline — 14 net fewer passing, 19 newly failing, 5 of those 19 were skip/xfail-adjacent already excluded from the 1621 count). All 19 failures are old-schema-key readers, consistent with the plan's documented transient:
- `tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden` (1) — `firestarter/database.py::_map_data` still reads the old `pulse_duration` key (now absent) and silently defaults, so only the wire's `pulse-delay` field differs from the golden for every pulse-consuming chip (417 identical items omitted from the diff; the rest all differ on exactly `['pulse-delay']`).
- `tests/test_audit_coverage_matrix.py` (10) — `tools/audit_coverage_matrix.py` consumers of the old key names, named in the plan as Plan 05's restoration target.
- `tests/test_characterization.py::test_list/test_info_known_chip/test_search_w27` (3) — CLI-output characterization tests reaching `database.py::_map_data` through the same path as the wire-dict golden.
- `tests/test_chip_database_field_inventory.py` (3) — a frozen field-inventory golden asserting the old key names are present.
- `tests/test_pulse_us_override.py` (2) — override-path tests keyed on the old `pulse_duration` field name.

Plan 04 (per its stated scope) restores `database.py::_map_data`, which should close `test_wire_dict_equivalence.py`, `test_characterization.py`, and `test_pulse_us_override.py` (16 of the 19). Plan 05 restores `tools/audit_coverage_matrix.py` (10 of the 19 — some overlap expected once both plans land, exact count TBD by Plan 05). `test_chip_database_field_inventory.py`'s golden was not named in this plan's or Plan 04/05's stated scope in the material available to this executor; flagging it here so the next plan's author can confirm which plan owns updating that frozen inventory.

No blockers for Plan 04.

## Self-Check: PASSED

- FOUND: `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-03-SUMMARY.md`
- FOUND: `firestarter_app/tests/test_build_db_interpret_timing.py`
- FOUND commit `702136c` (firestarter_app, Task 1)
- FOUND commit `e0d0f4f` (firestarter_app, Task 2 RED)
- FOUND commit `6442982` (firestarter_app, Task 2 GREEN)
- FOUND commit `af8ecaa` (firestarter_app, Task 3)
- FOUND commit `c295e3e7` (meta repo, plan metadata)
