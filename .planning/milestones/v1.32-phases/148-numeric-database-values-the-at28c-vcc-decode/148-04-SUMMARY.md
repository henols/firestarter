---
phase: 148-numeric-database-values-the-at28c-vcc-decode
plan: 04
subsystem: database
tags: [database, format_mv, ic_layout, eprom_info, schema-migration, numeric-values]

requires:
  - phase: 148-03
    provides: "build_db.py's numeric mv/us schema (vcc_mv/vdd_mv/vpp_mv/pulse_duration_us) emitted and regenerated into chip_database.json"
provides:
  - "database.py's coercion layer (_parse_pulse_duration + .replace(\"V\",\"\")->float() block) deleted; direct-indexed numeric reads in _map_data (D-10 fail-loud)"
  - "One shared format_mv(mv:int)->str render helper in database.py, owning the single millivolt-to-human-string convention"
  - "ic_layout.py's vcc_str/vpp_str and eprom_info.py's list-view vpp_str all render through format_mv, with structural (not hand-mirrored) WR-02 parity"
  - "746-chip wire dict proven byte-identical to the Plan 01 pre-change golden; test_characterization.ambr proven byte-unchanged"
affects: [148-05, 148-06, 148-07, 148-08]

tech-stack:
  added: []
  patterns:
    - "D-16: one public format_mv(mv:int)->str owns the millivolt-render convention; call sites never hand-format volts again"
    - "D-10: _map_data direct-indexes electrical[\"vcc_mv\"]/[\"vpp_mv\"] and programming[\"pulse_duration_us\"] instead of tolerant .get(key, 0) — an absent key raises KeyError rather than silently defaulting pulse-delay to 0 (which now means algorithm-controlled)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/database.py
    - firestarter_app/firestarter/ic_layout.py
    - firestarter_app/firestarter/eprom_info.py
    - firestarter_app/tests/test_sdp_capability.py
    - .planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md

key-decisions:
  - "P-02/P-03/P-07 followed verbatim: format_mv is strict (no 'N/A' fallback), the existing try/except int-coercion + vpp_mv>0 gate at both display sites is left untouched (guards the gate, not the render), and the dead vpp_volts fallback in convert_to_programmer + the vpp_volts mapped-dict key are both deleted outright"
  - "[Rule 1 - Bug] test_sdp_capability.py::test_local_override_0x0d_entry_is_refused_at_runtime's synthetic 0x0D local-override fixture carried no electrical dict at all; Task 1's direct-indexed _map_data now raises KeyError before reaching the SDP-refusal predicate under test. Fixed the test fixture (added electrical.vcc_mv/vpp_mv + programming.pulse_duration_us), not production code — the strict raise is exactly what D-10 mandates"

requirements-completed: []

coverage:
  - id: D1
    description: "database.py's string-coercion layer (_parse_pulse_duration, the .replace(\"V\",\"\")->float() block, vpp_volts key, dead convert_to_programmer fallback) deleted outright; one public format_mv(mv:int)->str added; _map_data direct-indexes vcc_mv/vpp_mv/pulse_duration_us and raises KeyError on a missing key"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "grep assertions (0 _parse_pulse_duration, 0 replace(\"V\", 0 vpp_volts, 1 def format_mv) + inline python format_mv(5000/3300/12500/25000) == '5.0v 3.3v 12.5v 25.0v' + inline python KeyError-on-missing-pulse_duration_us proof -- all pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "746-chip host->wire capture is byte-identical to the Plan 01 pre-change golden after the migration; test_pulse_us_override.py and test_eprom_database.py/test_chip_resolver.py all pass"
    requirement: "DATA-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_wire_dict_equivalence.py -- 5 passed; tests/test_eprom_database.py tests/test_chip_resolver.py tests/test_pulse_us_override.py -- 47 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "ic_layout.py's vcc_str/vpp_str and eprom_info.py's list-view vpp_str all call format_mv; the WR-02 parity comment at both sites rewritten to state structural (not hand-mirrored) parity; tests/__snapshots__/test_characterization.ambr byte-unchanged; firestarter info AT28C256 still reads 4.0v (confirming the margin-rail rule has not leaked into this plan)"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "tests/test_characterization.py -- 35 passed, git diff --quiet on the .ambr clean; tests/test_ic_layout.py tests/test_eprom_info.py -- 19 passed; CLI checks (firestarter info W27C512 VCC:5.0v/VPP:12.0v, AT28C256 VCC:4.0v) pass; ruff check + ruff format --check clean"
        status: pass
    human_judgment: false
  - id: D4
    description: "148-DB-DIFF.md records the measured wire-equivalence proof (D-14/D-06/D-15) and corrects D-15's stated proof mechanism per RESEARCH F-3 (no AT28C VCC line exists in any snapshot; W27C512 is the only info-view snapshot and is not a mover)"
    requirement: "DATA-03"
    verification:
      - kind: other
        ref: "grep assertions over 148-DB-DIFF.md for '## Wire equivalence', test_wire_dict_equivalence, byte-identical/byte-unchanged, D-06, D-15, W27C512 -- all pass; ## Before section confirmed unmodified"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-08-19
status: complete
---

# Phase 148 Plan 04: database.py Coercion-Layer Deletion & format_mv Summary

**Deleted database.py's string-coercion layer entirely, replaced it with one shared `format_mv` render helper, moved all three display call sites onto it, and proved the 746-chip wire dict and the pinned CLI snapshot both stayed byte-unchanged through the migration.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-19T10:50:00Z
- **Completed:** 2026-08-19T11:15:00Z
- **Tasks:** 3 completed
- **Files modified:** 5 (4 firestarter_app, 1 meta)

## Accomplishments
- Deleted `_parse_pulse_duration` and the `.replace("V","")` -> `float()` coercion block (both `try/except` bodies, the commented-out `logger.warning` lines, the `vpp = 0`/`vcc = 0` initializers) from `database.py::_map_data`, and added `format_mv(mv: int) -> str` (`return f"{mv / 1000:.1f}v"`) at module level in the vacated band — the single definition of the millivolt-to-human render (**D-16**).
- Rewrote `_map_data`'s mapped dict to direct-index `electrical["vcc_mv"]`, `electrical["vpp_mv"]`, and `programming["pulse_duration_us"]` instead of tolerant `.get(key, 0)` reads (**D-10**) — a stale string-schema `~/.firestarter/database.json` override missing a numeric key now raises `KeyError` loudly rather than silently resolving `pulse-delay` to `0` (which now means "algorithm-controlled" and would otherwise program a 0x07 chip with no pulse). Verified with an inline synthetic-record probe.
- Deleted the dead `vpp_volts` mapped-dict key and `convert_to_programmer`'s dead `or int(full_eprom_data.get("vpp_volts",0)*1000)` fallback, replacing it with a direct `full_eprom_data["vpp_mv"]` read — `vpp_mv` is the sole VPP source on the wire (**D-06**).
- Moved `ic_layout.py`'s `vcc_str` and `vpp_str`, and `eprom_info.py`'s list-view `vpp_str`, onto the shared `format_mv` helper, leaving the existing `try/except` int-coercion + `vpp_mv > 0` gate at both sites untouched (P-03: it guards the gate, not the render). Rewrote the WR-02 parity comment at both sites to state the new **structural** guarantee — both views call the same `format_mv` on the same already-coerced `_vpp_mv`, so they cannot diverge, rather than being kept in step by two hand-mirrored `'N/A'` fallbacks.
- Proved the phase's central safety claim: the live 746-chip `EpromDatabase(skip_local_override=True) -> get_eprom -> convert_to_programmer` capture is **byte-identical** to the Plan 01 pre-change golden (`test_wire_dict_equivalence.py`, 5/5 passing), and `tests/__snapshots__/test_characterization.ambr` is **byte-unchanged** (`git diff --quiet` clean) — confirmed `firestarter info AT28C256` still reads `4.0v` (the margin-rail rule is Plan 06's, not leaked here).
- Recorded the measured proof in `148-DB-DIFF.md`'s new `## Wire equivalence (D-14 / D-06)` section, and corrected the record where CONTEXT.md's D-15 supporting prose was wrong per RESEARCH F-3: no AT28C VCC line exists in any pinned snapshot; the only info-view snapshot (`firestarter info W27C512`) is not a mover. The criterion actually held is the stronger one — the `.ambr` is byte-unchanged in its entirety.
- **[Rule 1 - Bug, out-of-plan discovery]** Fixed a regression Task 1's strict indexing caused in `tests/test_sdp_capability.py::test_local_override_0x0d_entry_is_refused_at_runtime`: its synthetic 0x0D local-override fixture carried no `electrical` dict at all, so `_map_data` now raised `KeyError` before ever reaching the SDP-refusal predicate the test actually exercises. Fixed the test fixture (added minimal `electrical.vcc_mv`/`vpp_mv` and `programming.pulse_duration_us`), not production code — the strict raise on a genuinely stale record is exactly what this plan's D-10 acceptance criterion mandates.

## Task Commits

Each task committed atomically inside the `firestarter_app` submodule, on branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance` (Tasks 1-2, plus the Rule-1 fix), and the meta repo (Task 3):

1. **Task 1: Delete the coercion layer and add the shared render helper** - `9ea8ace` (feat) — `firestarter_app`
2. **Task 2: Move the three display call sites onto the shared helper, in parity** - `f52a14e` (feat) — `firestarter_app`
   - **[Rule 1 fix]** `8c5aa8d` (fix) — `firestarter_app` — repaired the synthetic 0x0D local-override test fixture broken by Task 1's strict indexing
3. **Task 3: Prove D-14, D-06 and D-15 together and record the result** - `f189e77b` (docs) — meta repo

_No TDD RED/GREEN split was needed for Task 1 — the plan's `tdd="true"` attribute targets behavior already RED on disk (see below), so the existing failing tests served as RED and this commit is the GREEN._

## Files Created/Modified
- `firestarter_app/firestarter/database.py` — `_parse_pulse_duration` and the string-coercion block deleted; `format_mv(mv:int)->str` added; `_map_data` direct-indexes `vcc_mv`/`vpp_mv`/`pulse_duration_us`; `convert_to_programmer`'s dead `vpp_volts` fallback replaced with a direct `vpp_mv` read
- `firestarter_app/firestarter/ic_layout.py` — `vcc_str`/`vpp_str` now call `format_mv`; WR-02 comment rewritten (structural parity)
- `firestarter_app/firestarter/eprom_info.py` — list-view `vpp_str` now calls `format_mv`; WR-02 comment rewritten (structural parity)
- `firestarter_app/tests/test_sdp_capability.py` — synthetic 0x0D local-override fixture given minimal numeric `electrical`/`programming` keys so `_map_data` can succeed (Rule 1 fix, not a plan task)
- `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md` — new `## Wire equivalence (D-14 / D-06)` section with measured proof and the D-15/RESEARCH-F-3 correction

## Decisions Made
- Followed P-02 (helper name/location), P-03 (strict `format_mv`, no `'N/A'` fallback inside it — the tolerant coercion stays at the display-site gate, per D-07's no-tolerant-reader rule), and P-07 (delete the dead `vpp_volts` fallback and mapped-dict key outright) exactly as specified.
- **[Rule 1 - Bug]** `test_sdp_capability.py`'s synthetic local-override fixture predates the numeric schema and had no `electrical` dict; fixed by adding the minimal numeric keys `_map_data` now requires, rather than loosening production code's strict-raise contract (which is this plan's own explicit D-10 acceptance criterion).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_sdp_capability.py`'s synthetic 0x0D local-override fixture broke under Task 1's strict indexing**
- **Found during:** Full-suite run after Task 2 (not part of this plan's declared 6-test scope)
- **Issue:** `test_local_override_0x0d_entry_is_refused_at_runtime` builds a synthetic local-override DB entry with only `part_number` and `programming.algorithm` — no `electrical` dict at all. Under the pre-migration tolerant `.get(key, 0)` reads this silently resolved to `vpp_mv=0`/`vcc=0`/`pulse-delay=0` and reached the intended SDP-refusal assertion. Under Task 1's direct-indexed `_map_data` (D-10) it now raised `KeyError: 'vpp_mv'` before ever reaching the predicate under test.
- **Fix:** Added `"electrical": {"vcc_mv": 5000, "vpp_mv": 0}` and `"pulse_duration_us": 0` to the fixture's `programming` block, with a comment naming the D-10 cause. This is a fix to the test fixture, not production code — the strict raise is exactly what this plan's D-10 acceptance criterion mandates.
- **Files modified:** `firestarter_app/tests/test_sdp_capability.py`
- **Verification:** `python3 -m pytest tests/test_sdp_capability.py -o addopts="" -q` — 12 passed (was 11 passed / 1 failed before the fix).
- **Committed in:** `8c5aa8d`

---

**Total deviations:** 1 auto-fixed (Rule 1)
**Impact on plan:** The regression was directly caused by this plan's Task 1 change (a stricter, more-correct contract per D-10) surfacing a pre-existing gap in an unrelated test's synthetic fixture. No scope creep — the fix is a one-fixture, minimal-key addition; production code is unchanged from what the plan specified.

## Issues Encountered
None beyond the one deviation above.

## User Setup Required
None — no external service configuration required.

## Requirements Handling

Both requirements this plan is tagged with (`DATA-02`, `DATA-03`) are claimed by multiple plans per the success-criteria instruction, so checkboxes are **not** flipped from this plan alone:

- **DATA-02** is also claimed by 148-07 (restores `tools/audit_coverage_matrix.py`, the other transiently-RED numeric-schema consumer). Left `Pending` in `REQUIREMENTS.md`/`ROADMAP.md`. This plan's contribution (the last host consumer, `database.py`, now reads the numeric schema end-to-end, proven byte-identical on the wire) is necessary but the checkbox is only flipped by 148-07, the last plan to finish.
- **DATA-03** is also claimed by 148-05 and 148-08. Left `Pending`. This plan's contribution (the D-14/D-06 wire-equivalence proof, recorded in `148-DB-DIFF.md`) is one of several DATA-03 deliverables; 148-05 and 148-08 own the remainder.

`roadmap.update-plan-progress` was run to update the Phase 148 plan-count row (4/8 plans complete); the requirement traceability table itself is unchanged per the instruction above.

## Next Phase Readiness

**Measured final suite state after this plan: 13 failed, 1613 passed** (from Plan 03's post-migration baseline of 19 failed, 1607 passed — 6 net retirements, exactly the 6 this plan owned, plus 1 net additional pass from the Rule-1 fix's own new-green test). The exact 13 remaining failures, confirmed to be exclusively the ones later plans own:

- `tests/test_audit_coverage_matrix.py` (10 failures) — owned by 148-05, untouched by this plan.
- `tests/test_chip_database_field_inventory.py` (3 failures) — owned by 148-07, untouched by this plan.

The 6 tests this plan was the named owner for are all green:
- `tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden`
- `tests/test_pulse_us_override.py::test_write_without_pulse_us_still_works`
- `tests/test_pulse_us_override.py::test_override_does_not_mutate_the_caller_dict`
- `tests/test_characterization.py::test_list`
- `tests/test_characterization.py::test_info_known_chip`
- `tests/test_characterization.py::test_search_w27`

`tools/audit_coverage_matrix.py` and `tests/golden/chip_database_field_inventory.json` were not touched, per this plan's explicit instruction. No blockers for Plan 05.

## Self-Check: PASSED

- FOUND: `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-04-SUMMARY.md`
- FOUND: `firestarter_app/firestarter/database.py` (modified, contains `def format_mv`)
- FOUND: `firestarter_app/firestarter/ic_layout.py` (modified, contains `format_mv`)
- FOUND: `firestarter_app/firestarter/eprom_info.py` (modified, contains `format_mv`)
- FOUND: `firestarter_app/tests/test_sdp_capability.py` (modified)
- FOUND commit `9ea8ace` (firestarter_app, Task 1)
- FOUND commit `f52a14e` (firestarter_app, Task 2)
- FOUND commit `8c5aa8d` (firestarter_app, Rule 1 fix)
- FOUND commit `f189e77b` (meta repo, Task 3)

---
*Phase: 148-numeric-database-values-the-at28c-vcc-decode*
*Completed: 2026-08-19*
