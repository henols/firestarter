---
phase: 148-numeric-database-values-the-at28c-vcc-decode
plan: 02
subsystem: tooling
tags: [diff_db, gate-02, schema-migration, canonicalizer, regression-gate]

requires: ["148-01"]
provides:
  - "Schema-agnostic diff_db.py comparator (_canonicalize_db) that normalizes both the pinned baseline and the current database to the numeric mv/us schema before classification"
  - "diff_db_gate test fixtures migrated to the numeric schema (vcc_mv/vdd_mv/pulse_duration_us)"
affects: [148-03, 148-04, 148-05, 148-06, 148-07, 148-08]

tech-stack:
  added: []
  patterns:
    - "Load-time canonicalization hook: both DBs normalized to one schema immediately after _load_db, before _make_index, so every downstream comparison (index build, equality check, _classify_diff, _diff_field_paths) sees a single shape regardless of which side of a schema migration either input is on"
    - "Narrow except (TypeError, ValueError) per-field parse helpers with a documented 0 sentinel for unparseable values (mirrors build_db.py's generator behavior for 'Algorithm Controlled')"

key-files:
  created: []
  modified:
    - firestarter_app/tools/diff_db.py
    - firestarter_app/tests/test_diff_db_gate.py

key-decisions:
  - "_canonicalize_db returns a normalized deep copy (never mutates its input) so main()'s bl_db/cu_db rebinding is the only place schema normalization happens, keeping _load_db's exit-code contract untouched"
  - "electrical.vpp is dropped entirely during canonicalization (not renamed) — vpp_mv already carries the value under an unchanged name/type, so BUG_B_VPP and RULE_PHASE66's vpp_mv-only comparison terms are now the sole VPP check"
  - "RULE_VCC_MARGIN_RAIL is explicitly NOT added in this plan — it belongs to 148-06, once the 56-chip mover rule actually exists to explain"

requirements-completed: []

coverage:
  - id: D1
    description: "GATE-02 exits 0 with the identical 744/2/742 bucket distribution recorded pre-change in 148-DB-DIFF.md, proving the canonicalizer is representation-neutral on today's still-string-schema database"
    requirement: "DATA-05"
    verification:
      - kind: unit
        ref: "python3 tools/diff_db.py — EXIT=0, 'CHANGED chips (744 total)', 'PGSZ_PAGE_SIZE] (2 chips)', 'PROV01_PROTECT_METADATA] (742 chips)'"
        status: pass
    human_judgment: false
  - id: D2
    description: "_canonicalize_db is idempotent (applying it twice yields an equal result) and no _RULE_FIELD_PATHS rule still claims the (electrical, vpp) path"
    requirement: "DATA-05"
    verification:
      - kind: unit
        ref: "inline python check importing tools/diff_db.py, asserting a == b after double-canonicalization and stale == {} over _RULE_FIELD_PATHS"
        status: pass
    human_judgment: false
  - id: D3
    description: "The only old-schema test fixture in the tree (tests/test_diff_db_gate.py) migrated to vcc_mv/vdd_mv/pulse_duration_us; gate test and lint both green"
    requirement: "DATA-05"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_diff_db_gate.py -o addopts=\"\" -q — 4 passed; ruff check + ruff format --check on tests/ both pass"
        status: pass
    human_judgment: false
  - id: D4
    description: "Baseline and GATE-03 (check_dispatch.py) byte-unchanged; full app suite still green"
    requirement: "DATA-05"
    verification:
      - kind: unit
        ref: "git diff --quiet on tools/baseline/chip_database.baseline.json and tools/check_dispatch.py (both clean); check_dispatch.py EXIT=0; full pytest suite 1621 passed"
        status: pass
    human_judgment: false

duration: ~15min
completed: 2026-08-19
status: complete
---

# Phase 148 Plan 02: diff_db.py Schema-Normalizing Comparator Summary

**Made GATE-02 (`diff_db.py`) schema-agnostic ahead of the numeric-database migration by adding a load-time `_canonicalize_db` normalizer, renaming every field-name-keyed classification read to the canonical `vcc_mv`/`vdd_mv`/`pulse_duration_us` names, and migrating the gate's own test fixtures — while the pinned pre-136.1 baseline and GATE-03 stay byte-unchanged.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-08-19T10:05:00Z
- **Completed:** 2026-08-19T10:20:00Z
- **Tasks:** 2 completed
- **Files modified:** 2

## Accomplishments
- Added `_canonicalize_db(db)` to `tools/diff_db.py`, called on both the pinned baseline and the current database immediately after `_load_db` in `main()`, before `_make_index` — the minimal-surface hook point that makes the equality guard, `_classify_diff`, and `_diff_field_paths` all see one normalized schema regardless of which side of the migration either input is actually on.
- Normalized `electrical.vcc`/`vdd` (string, e.g. `"4V"`) to `vcc_mv`/`vdd_mv` (int millivolts) via two narrow-except helpers (`_voltage_str_to_mv`, `_pulse_str_to_us`), dropped `electrical.vpp` entirely (superseded by the already-present `vpp_mv`), and normalized `programming.pulse_duration` to `pulse_duration_us`, with `"Algorithm Controlled"` and any unparseable value mapping to the documented `0` sentinel.
- Renamed the five field-name-keyed classification reads (`:445-459` pre-edit) and the `_RULE_FIELD_PATHS` tuples in `BUG2_AND_BUG3`, `BUG2_TIMING`, `BUG3_VCC_VDD` to the canonical names, and deleted the now-redundant `("electrical","vpp")` entries from `BUG_B_VPP` and `RULE_PHASE66` (the `vpp_mv` term in each already covers the same comparison).
- Migrated the only old-schema chip literals remaining in the tree — `tests/test_diff_db_gate.py`'s `_make_chip` helper and the inline `SST39SF040` fixture — to the numeric schema, with a comment recording that `_canonicalize_db` accepts either schema so these literals prove the new shape deliberately rather than by the compatibility path's side effect.
- Confirmed GATE-02 still exits 0 with the byte-identical 744-chip / `PGSZ_PAGE_SIZE`=2 / `PROV01_PROTECT_METADATA`=742 distribution recorded in `148-DB-DIFF.md`'s `## Before` section, the canonicalizer is idempotent, `tools/baseline/chip_database.baseline.json` and `tools/check_dispatch.py` are byte-unchanged (`git diff --quiet` on both), and the full app test suite is still green (1621 passed — same count as Plan 01's baseline).

## Task Commits

Each task committed atomically inside the `firestarter_app` submodule, on branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`:

1. **Task 1: Add the normalizing comparator and rename every field-name-keyed read** - `b396e26` (feat) — `firestarter_app`
2. **Task 2: Migrate the one test fixture carrying old-schema literals** - `7fb844b` (test) — `firestarter_app`

## Files Created/Modified
- `firestarter_app/tools/diff_db.py` — added `_voltage_str_to_mv`, `_pulse_str_to_us`, `_canonicalize_db`; hooked canonicalization into `main()` right after `_load_db`; renamed the five field-name reads in `_classify_diff` and the corresponding `_RULE_FIELD_PATHS` tuples to `vcc_mv`/`vdd_mv`/`pulse_duration_us`; deleted the `("electrical","vpp")` entries from `BUG_B_VPP` and `RULE_PHASE66`
- `firestarter_app/tests/test_diff_db_gate.py` — migrated `_make_chip` and the inline `SST39SF040` fixture from `vcc`/`vdd`/`vpp`/`pulse_duration` string literals to `vcc_mv`/`vdd_mv`/`pulse_duration_us` numeric literals (dropping the now-redundant `vpp` line since `vpp_mv` already carries the value); added a one-line schema-provenance comment above `_make_chip`

## Decisions Made
- `_canonicalize_db` deep-copies its input (`copy.deepcopy`) and returns a new dict rather than mutating in place, so `main()`'s `bl_db = _canonicalize_db(bl_db)` / `cu_db = _canonicalize_db(cu_db)` rebinding is the only place normalization happens — no hidden aliasing between the loaded JSON and the normalized version.
- Both voltage and pulse-duration parsing use the same narrow `except (TypeError, ValueError)` pattern with a `0` fallback, per the plan's T-148-05 threat-model guidance, even though the plan's prose only explicitly called out the `"Algorithm Controlled"` case for pulse duration — applying the same defensive pattern uniformly keeps the function's failure mode single and documented rather than having one field silently succeed and another silently raise.
- `RULE_VCC_MARGIN_RAIL` was deliberately not added — confirmed absent via `grep -c 'RULE_VCC_MARGIN_RAIL' tools/diff_db.py` returning 0 — since Plan 06 owns it and the 56-chip mover set does not exist until that plan's rule runs.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' automated verify blocks passed on the first attempt with no auto-fixes required.

## Requirements Handling

**DATA-05 is intentionally left `Pending`** in both `REQUIREMENTS.md` and `ROADMAP.md`. Per this plan's explicit instruction, DATA-05 is also claimed by 148-06 (the plan that adds `RULE_VCC_MARGIN_RAIL` and completes the blast-radius proof), so this plan's contribution — making the comparator schema-agnostic — is necessary-but-not-sufficient for DATA-05 and the checkbox is only flipped by that plan's last-contributing-plan status. `roadmap.update-plan-progress` was still run to update the Phase 148 plan-count row (2/8 plans complete); the requirement traceability table itself is unchanged.

## Issues Encountered
None.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness

`tools/diff_db.py` now reads and classifies on the canonical `vcc_mv`/`vdd_mv`/`pulse_duration_us` names and is proven idempotent against both the old string schema (today) and the eventual numeric schema (after Plan 03's generator change), with the pinned pre-136.1 baseline untouched. Plan 03 can now migrate `build_db.py`'s emission to the numeric schema without GATE-02 going spuriously RED for a representation reason. No blockers.

---
*Phase: 148-numeric-database-values-the-at28c-vcc-decode*
*Completed: 2026-08-19*

## Self-Check: PASSED

- FOUND: `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-02-SUMMARY.md`
- FOUND: `firestarter_app/tools/diff_db.py`
- FOUND: `firestarter_app/tests/test_diff_db_gate.py`
- FOUND commit `b396e26` (firestarter_app, Task 1)
- FOUND commit `7fb844b` (firestarter_app, Task 2)
