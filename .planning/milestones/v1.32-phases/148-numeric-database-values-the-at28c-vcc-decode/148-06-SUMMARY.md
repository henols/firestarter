---
phase: 148-numeric-database-values-the-at28c-vcc-decode
plan: 06
subsystem: database
tags: [build_db, diff_db, vcc-decode, at28c, margin-rail, chip-database]

requires:
  - phase: 148-03
    provides: "build_db.py's numeric mv/us schema (vcc_mv/vdd_mv/vpp_mv/pulse_duration_us) emitted and regenerated into chip_database.json"
  - phase: 148-05
    provides: "audit_coverage_matrix.py's parse_pulse_us deleted; full suite restored to 1623 passed / 3 failed (148-07-owned)"
provides:
  - "build_db.py's _VCC_MARGIN_RAIL_MV = VCC_VOLTAGES[0x02] constant and its post-construction margin-rail substitution: whenever electrical.vcc_mv == 4000, substitute the chip's own already-decoded vdd_mv"
  - "diff_db.py's RULE_VCC_MARGIN_RAIL rule (in _RATIONALES, _RULE_FIELD_PATHS, a value-scoped _classify_diff branch placed before BUG3_VCC_VDD, and the docstring priority list)"
  - "tests/test_vcc_margin_rail.py: zero-at-rail, exactly-56-movers-onto-their-own-vdd, no-decrease guard, DATA-04 decode-table-unedited assertion, and a non-vacuity leg"
  - "tests/test_characterization.py::test_info_at28c256: criterion 1's only test, pinning firestarter info AT28C256 -> VCC: 5.0v"
  - "tests/test_diff_db_gate.py: bucket-invariance test pinning the measured distribution (744/56/686/2/0/0)"
  - "148-DB-DIFF.md: RED/GREEN transcript, the 56-chip mover list, the D-03 justification, and the explicit vcc=5500 non-claim"
affects: [148-07, 148-08]

tech-stack:
  added: []
  patterns:
    - "Post-construction value-keyed substitution: the margin-rail rule reads chip_entry AFTER construction (mirrors the shipped SRAM vcc=vdd block), keyed on the decoded VALUE alone rather than any part-number/type/algorithm axis -- generalizes the SRAM precedent from a type key to a value key"
    - "diff_db.py rule ordering: a new value-scoped _classify_diff branch must be placed BEFORE any pre-existing rule whose condition is broad enough to also match the new diff shape, or the pre-existing rule silently misattributes it"

key-files:
  created:
    - firestarter_app/tests/test_vcc_margin_rail.py
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tools/diff_db.py
    - firestarter_app/tests/test_diff_db_gate.py
    - firestarter_app/tests/test_characterization.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - .planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md

key-decisions:
  - "Measured correction to the plan's own predicted RED mechanism: Task 1's RED was predicted as diff_db.py exit 1 with 56 UNEXPLAINED chips, on the theory that no existing rule claims the (electrical, vcc_mv) path for these chips. That theory did not hold -- the pre-existing BUG3_VCC_VDD rule's condition (voltage_diff and not timing_diff and not algo_diff) does not check pinout/type/vpp, so it silently matched the 56 movers and misattributed them to the Phase 57/58 vcc/vdd label-swap rationale. The measured RED is exit 0 with all 56 chips wrongly bucketed as BUG3_VCC_VDD -- arguably a stronger proof of D-11's need than the predicted RED, since it shows the movers being silently swallowed by the WRONG rule rather than surfaced as unexplained. Documented verbatim in 148-DB-DIFF.md; Task 2's new RULE_VCC_MARGIN_RAIL branch (placed before BUG3_VCC_VDD) is what fixes this, and the measured GREEN matches every other plan prediction exactly (744/56/686/2/0/0)."
  - "RULE_VCC_MARGIN_RAIL's _classify_diff condition hardcodes the literal 4000 (mirroring RC1_DIP32_27C020's hardcoded pinout-string-literal style) rather than importing build_db.py's _VCC_MARGIN_RAIL_MV constant into diff_db.py -- diff_db.py imports nothing from tools.build_db anywhere today, and the value is cited in the rule's own rationale comment (which names build_db.py::_VCC_MARGIN_RAIL_MV explicitly) so the linkage is documented, not silently duplicated."
  - "tests/test_vcc_margin_rail.py's _mv() helper duplicates diff_db.py's voltage-string parsing (3 lines) rather than importing diff_db.py into a test -- explicit per-plan instruction, matching the existing repo convention of not importing a gate tool into a test module."

requirements-completed: [DATA-01, DATA-05]

coverage:
  - id: D1
    description: "build_db.py's _VCC_MARGIN_RAIL_MV = VCC_VOLTAGES[0x02] constant (a lookup, not a re-typed literal) added immediately after VCC_VOLTAGES; a post-construction mutation (after the SRAM block, before chips.append) substitutes vdd_mv for vcc_mv wherever vcc_mv == _VCC_MARGIN_RAIL_MV; VCC_VOLTAGES[0x02] itself remains 4000 (D-01, table unedited); chip_database.json regenerated to 746 chips, 0 at vcc_mv==4000, no chip's vcc_mv lowered"
    requirement: "DATA-01"
    verification:
      - kind: unit
        ref: "python3 -c \"from tools import build_db as b; print(b._VCC_MARGIN_RAIL_MV, b.VCC_VOLTAGES[2])\" -- prints '4000 4000'; grep -c constant definition == 1; rule-use line > SRAM-line; len(_PAGE_SIZE_BY_PART) == 2; regenerated-DB structural check (746 chips, 0 at 4000mV) -- all pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "firestarter info AT28C256 now reports VCC: 5.0v (was 4.0v), VPP: 12.0v unaffected; W27C512 (a non-mover) still reports VCC: 5.0v -- criterion 1 satisfied and pinned by the new test_info_at28c256 snapshot (insertions-only .ambr diff, 0 deletions)"
    requirement: "DATA-01"
    verification:
      - kind: unit
        ref: "tests/test_characterization.py::test_info_at28c256 -- 1 passed; live CLI check FIRESTARTER_CONFIG_DIR=<scratch> firestarter info AT28C256 | grep 'VCC:.*5.0v' and 'VPP:.*12.0v'; W27C512 VCC unchanged; git diff --numstat .ambr shows 52 insertions, 0 deletions"
        status: pass
    human_judgment: false
  - id: D3
    description: "diff_db.py's RULE_VCC_MARGIN_RAIL added to _RATIONALES (cited), _RULE_FIELD_PATHS ({(electrical,vcc_mv)} only), a value-scoped _classify_diff branch placed BEFORE BUG3_VCC_VDD (baseline vcc_mv==4000 AND current vcc_mv==current vdd_mv AND current vcc_mv!=4000, with algo/timing/pinout/type exclusivity), and the docstring priority list (renumbered). diff_db.py now exits 0 with the measured distribution: 744 total changed, RULE_VCC_MARGIN_RAIL 56, PROV01_PROTECT_METADATA 686 (dropped from 742 by exactly the 56 movers), PGSZ_PAGE_SIZE 2, 0 NEW, 0 MISSING. Baseline NOT re-pinned; check_dispatch.py (GATE-03) byte-unchanged, exits 0 with 0 violations"
    requirement: "DATA-05"
    verification:
      - kind: unit
        ref: "python3 tools/diff_db.py ; echo EXIT=$? -- EXIT=0, all six count assertions match; tests/test_diff_db_gate.py::TestDiffDbVccMarginRailBucketInvariance::test_vcc_margin_rail_bucket_distribution -- 1 passed; git diff --quiet on baseline and check_dispatch.py both clean; python3 tools/check_dispatch.py -- EXIT=0, 0 violations"
        status: pass
    human_judgment: false
  - id: D4
    description: "Exactly 56 chips moved vcc_mv 4000 -> 5000, every one landing on its OWN vdd_mv (not a fixed literal); no chip's vcc_mv is ever lower than its baseline value (the property the rejected type-keyed/algorithm-keyed alternatives, measured at 85/84 movers each setting 16 genuinely-5V EEPROMs to 3.3V, would have violated); a non-vacuity leg proves the zero-at-rail gate is capable of failing"
    requirement: "DATA-05"
    verification:
      - kind: unit
        ref: "tests/test_vcc_margin_rail.py -- 5 passed (zero-at-rail, exactly-56-movers, no-decrease guard, DATA-04 table-unedited + _PAGE_SIZE_BY_PART==2, non-vacuity leg)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Full suite restored: 1630 passed, 3 failed (up from Plan 05's 1623 passed / 3 failed -- +7 net new passing tests from this plan's 5 new test_vcc_margin_rail.py tests + 1 new test_characterization.py test + 1 new test_diff_db_gate.py test, 0 net new failures). The 3 remaining failures are exclusively the 148-07-owned test_chip_database_field_inventory.py frozen-golden mismatches, confirmed untouched. Wire-dict equivalence (D-06/D-14) still byte-identical; ruff check + format clean on all touched files"
    requirement: "DATA-05"
    verification:
      - kind: unit
        ref: "python3 -m pytest -o addopts=\"\" -q -- 1630 passed, 3 failed, 212.17s (count line visible); the 3 failures are exclusively test_chip_database_field_inventory.py's three tests; python3 -m pytest tests/test_wire_dict_equivalence.py -o addopts=\"\" -q -- 5 passed; ruff check + format --check clean on tools/build_db.py, tools/diff_db.py, tests/test_diff_db_gate.py, tests/test_vcc_margin_rail.py, tests/test_characterization.py, and (per acceptance scope) firestarter/ + tests/"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-19
status: complete
---

# Phase 148 Plan 06: VCC Margin-Rail Substitution & diff_db.py Blast-Radius Proof Summary

**Corrected `firestarter info AT28C256`'s `VCC:` line from `4.0v` to `5.0v` via a value-keyed post-construction substitution in `build_db.py` (never touching the faithfully-decoded `VCC_VOLTAGES` table), and proved the exact 56-chip blast radius in `diff_db.py` with a dedicated `RULE_VCC_MARGIN_RAIL` bucket — discovering along the way that the plan's own predicted RED mechanism was wrong, and documenting the corrected, stronger measurement.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-08-19T11:40:00Z (approx)
- **Completed:** 2026-08-19T12:30:00Z (approx)
- **Tasks:** 3 completed
- **Files modified:** 7 (1 new)

## Accomplishments

- Added `build_db.py::_VCC_MARGIN_RAIL_MV = VCC_VOLTAGES[0x02]` — a **lookup** into the existing decode table (never a re-typed literal), placed immediately after `VCC_VOLTAGES` with a comment stating the claim about the decode table itself ("4 V is a real number that is not a real operating voltage"). `VCC_VOLTAGES[0x02]` itself is byte-unchanged at `4000` — the table is never edited (D-01).
- Added the post-construction margin-rail substitution immediately after the shipped SRAM `vcc=vdd` block and before `chips.append(chip_entry)`: whenever `chip_entry["electrical"]["vcc_mv"] == _VCC_MARGIN_RAIL_MV`, substitute the chip's own already-decoded `vdd_mv`. Keyed on the **decoded value alone** — no part number, no type, no algorithm — with a code comment naming the measured 85/84/225-mover rejected alternatives and the sixteen 5V EEPROMs they would have set to 3.3V (DATA-05's "too broad" guard, stated where the next reader will see it).
- Regenerated `firestarter/data/chip_database.json` via `python3 tools/build_db.py`: 746 chips, **0** remaining at `vcc_mv == 4000`, no chip's `vcc_mv` lower than its pre-rule value.
- Added `diff_db.py`'s `RULE_VCC_MARGIN_RAIL` in all three required places (`_RATIONALES` with its `tl866ii_vcc_voltages[]` citation, `_RULE_FIELD_PATHS` scoped to exactly `{("electrical","vcc_mv")}`, and a value-scoped `_classify_diff` branch placed **before** `BUG3_VCC_VDD`) plus the docstring priority list (renumbered). `diff_db.py` now exits 0 with the measured distribution: **744** total changed, `RULE_VCC_MARGIN_RAIL` **56**, `PROV01_PROTECT_METADATA` **686** (dropped from 742 by exactly the 56 movers), `PGSZ_PAGE_SIZE` **2**, **0** NEW, **0** MISSING.
- Added a bucket-invariance test to `tests/test_diff_db_gate.py` pinning that exact six-number distribution via the real `diff_db.py` subprocess.
- Wrote `tests/test_vcc_margin_rail.py` (new module, 5 tests): zero-chips-at-margin-rail, exactly-56-movers-each-landing-on-their-own-`vdd_mv` (matched by `(manufacturer, part_number, index)` composite key against the un-re-pinned baseline, since part numbers are not unique), a no-decrease guard against the baseline, the DATA-04 decode-table-unedited + `_PAGE_SIZE_BY_PART == 2` assertion, and a non-vacuity leg driving the same offender-collecting helper the real-DB test calls.
- Added `tests/test_characterization.py::test_info_at28c256` — criterion 1's only test, since no AT28C VCC line existed in any prior pinned snapshot. Generated with a scoped `--snapshot-update` and confirmed the `.ambr` diff is **insertions-only** (52 insertions, 0 deletions via `git diff --numstat`).
- Live-verified: `firestarter info AT28C256` now prints `VCC:                5.0v` (`VPP:` unaffected at `12.0v`); `firestarter info W27C512` (a non-mover) still prints `VCC:                5.0v`, confirming the rule did not touch chips it shouldn't.
- Full suite restored to **1630 passed, 3 failed** (up from Plan 05's 1623/3 baseline — 0 net new failures, +7 net new passing tests from this plan's own additions). The 3 remaining failures are exclusively the 148-07-owned `test_chip_database_field_inventory.py` frozen-golden mismatches, confirmed untouched.

## Task Commits

Each task committed atomically inside the `firestarter_app` submodule, on branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`:

1. **Task 1: Add the margin-rail rule, regenerate, and capture the RED transcript** - `b5416e0` (feat) — `firestarter_app`
2. **Task 2: Add RULE_VCC_MARGIN_RAIL in all three places and capture the GREEN** - `c06709c` (feat) — `firestarter_app`
3. **Task 3: Pin the invariant and give criterion 1 its only test** - `14b62d8` (test) — `firestarter_app`

**Meta-repo docs commit:** `e317092d` (docs, `148-DB-DIFF.md` RED/GREEN transcript + mover list + non-claim) — `/workspaces`

_No REFACTOR commit was needed._

## Files Created/Modified

- `firestarter_app/tools/build_db.py` — `_VCC_MARGIN_RAIL_MV` constant + post-construction margin-rail substitution added; `VCC_VOLTAGES` unedited
- `firestarter_app/firestarter/data/chip_database.json` — regenerated via `python3 tools/build_db.py`; 746 chips, 0 at `vcc_mv==4000`
- `firestarter_app/tools/diff_db.py` — `RULE_VCC_MARGIN_RAIL` added to `_RATIONALES`, `_RULE_FIELD_PATHS`, `_classify_diff` (before `BUG3_VCC_VDD`), and the docstring priority list
- `firestarter_app/tests/test_diff_db_gate.py` — new `TestDiffDbVccMarginRailBucketInvariance` bucket-distribution test
- `firestarter_app/tests/test_vcc_margin_rail.py` — new module, 5 tests
- `firestarter_app/tests/test_characterization.py` — new `test_info_at28c256`
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — 2 new snapshot entries (insertions-only)
- `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md` — RED/GREEN transcript, mover list, justification, non-claim appended

## Decisions Made

- Documented the measured correction to the plan's own predicted RED mechanism (see `key-decisions` in frontmatter and the "Deviations" section below) directly in both the code comments and `148-DB-DIFF.md`, rather than silently matching the plan's literal acceptance-criteria text.
- `RULE_VCC_MARGIN_RAIL`'s `_classify_diff` condition hardcodes the literal `4000` rather than importing `build_db.py`'s `_VCC_MARGIN_RAIL_MV` — matches the existing `RC1_DIP32_27C020` precedent (hardcoded pinout-string literal), and `diff_db.py` imports nothing from `tools.build_db` anywhere today.
- `test_vcc_margin_rail.py`'s `_mv()` helper duplicates 3 lines of `diff_db.py`'s voltage-string parsing rather than importing `diff_db.py` into a test, per the plan's explicit instruction and the repo's established "don't import a gate tool into a test" convention.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in the plan's own predicted mechanism, not in delivered code] Task 1's predicted RED ("exit 1, 56 UNEXPLAINED") did not occur — measured RED was exit 0 with the 56 movers misattributed to the pre-existing `BUG3_VCC_VDD` rule**
- **Found during:** Task 1 verification (running `python3 tools/diff_db.py` immediately after landing the `build_db.py` substitution, before Task 2's `diff_db.py` changes)
- **Issue:** `148-06-PLAN.md`'s Task 1 predicted that `_classify_diff`'s `bl_elec.get("vcc_mv") != cu_elec.get("vcc_mv")` check would see the change but no rule would claim the `("electrical","vcc_mv")` path, escalating the 56 movers to `UNEXPLAINED` (exit 1). Measured behavior: the pre-existing `BUG3_VCC_VDD` rule's condition (`voltage_diff and not timing_diff and not algo_diff`) does not check `pinout_diff`/`type_diff`/`vpp_diff`, so it matched the 56 movers anyway and silently classified them under the Phase 57/58 vcc/vdd label-swap rationale — which is not what happened (D-01: the vcc/vdd field labels are correct; only the margin-rail value is substituted). The measured RED was therefore `EXIT=0` with `[BUG3_VCC_VDD] (56 chips)`, not `EXIT=1` with `UNEXPLAINED`.
- **Fix:** Documented the measured (not predicted) RED verbatim in `148-DB-DIFF.md`, noting it is arguably a *stronger* proof of D-11's need than the predicted RED — the movers were being silently swallowed by the wrong rule rather than surfaced as unexplained. Proceeded with Task 2 exactly as specified (new `RULE_VCC_MARGIN_RAIL` branch placed before `BUG3_VCC_VDD`), which produces the measured GREEN that matches every one of the plan's OTHER predictions exactly (744/56/686/2/0/0). No code change was needed beyond what Task 2 already specified — this was a documentation correction to the RED transcript, not a fix to delivered code.
- **Files modified:** `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md` (RED section text corrected to match measurement)
- **Verification:** `python3 tools/diff_db.py` before Task 2's changes landed showed `EXIT=0` with `[BUG3_VCC_VDD] (56 chips)`, confirmed against the actual `/tmp/dd6red.txt` capture; after Task 2, the same command shows `EXIT=0` with `[RULE_VCC_MARGIN_RAIL] (56 chips)` and `[PROV01_PROTECT_METADATA] (686 chips)`, matching every plan-predicted count exactly.
- **Committed in:** documented in `e317092d` (meta-repo docs commit); no `firestarter_app` code was affected by this correction — Tasks 1/2 landed exactly as the plan's `<action>` blocks specified.

---

**Total deviations:** 1 (a documentation/measurement correction to the plan's own predicted RED transcript; zero impact on delivered code, which matches the plan's `<action>` blocks verbatim).
**Impact on plan:** None on the final implementation — Tasks 1, 2, and 3 all landed exactly as specified in the plan's `<action>` sections. The only correction was to the RED transcript's narrative in the D-12 review artifact, which now records what was actually measured instead of what was predicted (following the same "measure it, don't argue it" discipline the plan itself establishes for the mover count).

## Issues Encountered

None beyond the one documented deviation above.

## User Setup Required

None — no external service configuration required.

## Requirements Handling

**DATA-01 and DATA-05 are marked `Complete`** in both `REQUIREMENTS.md` and its traceability table, per this plan's explicit success-criteria instruction: DATA-01's premise-corrected criterion (5V, not 4.5V, via a margin-rail substitution, never a decode-table edit) is fully satisfied and pinned by `test_info_at28c256` + the live CLI check; DATA-05's blast-radius-proof requirement (diff_db.py as the review artifact, GATE-03 never weakened) is fully satisfied by the `RULE_VCC_MARGIN_RAIL` bucket, the bucket-invariance test, and `check_dispatch.py`'s unchanged 0-violations pass.

**DATA-04 is intentionally left `Pending`** — per this plan's explicit instruction, it is also claimed by Plan 148-08, which is the last plan claiming this requirement and the one that flips its checkbox. This plan's contribution to DATA-04 (no new part-number-keyed dict; `_PAGE_SIZE_BY_PART` still exactly 2 entries; `VCC_VOLTAGES[0x02]` unedited) is asserted directly in `tests/test_vcc_margin_rail.py::test_vcc_voltages_table_unedited_and_no_new_part_keyed_dict` but does not by itself close the requirement.

`roadmap.update-plan-progress` was run to update the Phase 148 plan-count row (6/8 plans complete).

## Next Phase Readiness

Full suite state after this plan: **1630 passed, 3 failed** (up from Plan 05's baseline of 1623 passed / 3 failed — this plan's 7 new tests all pass, 0 net new failures). The 3 remaining failures are exclusively:

- `tests/test_chip_database_field_inventory.py::test_programming_field_inventory_matches`
- `tests/test_chip_database_field_inventory.py::test_electrical_field_inventory_matches`
- `tests/test_chip_database_field_inventory.py::test_generator_emits_no_key_outside_the_frozen_inventory`

All three are the 148-07-owned frozen-inventory golden mismatch from Plan 03's schema migration, confirmed unchanged in cause and unregressed by this plan. Plan 148-07 is the named owner and should update `tests/golden/chip_database_field_inventory.json` to reflect the new numeric field set (and separately account for this plan's `_VCC_MARGIN_RAIL_MV` constant addition, which does not add or remove any per-chip JSON key, so should not itself change the field-inventory golden).

No blockers for Plan 148-07 or 148-08. The `vcc=5500` EEPROM-class group (29 chips) remains an explicit, documented non-claim in `148-DB-DIFF.md` — deferred, not fixed.

## Self-Check: PASSED

- FOUND: `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-06-SUMMARY.md`
- FOUND: `firestarter_app/tests/test_vcc_margin_rail.py` (new, 5 tests, all pass)
- FOUND: `firestarter_app/tools/build_db.py` (modified, contains `_VCC_MARGIN_RAIL_MV`)
- FOUND: `firestarter_app/tools/diff_db.py` (modified, contains `RULE_VCC_MARGIN_RAIL`)
- FOUND commit `b5416e0` (firestarter_app, Task 1)
- FOUND commit `c06709c` (firestarter_app, Task 2)
- FOUND commit `14b62d8` (firestarter_app, Task 3)
- FOUND commit `e317092d` (meta repo, 148-DB-DIFF.md update)

All items verified present on disk and in git history. No missing items.

---
*Phase: 148-numeric-database-values-the-at28c-vcc-decode*
*Completed: 2026-08-19*
