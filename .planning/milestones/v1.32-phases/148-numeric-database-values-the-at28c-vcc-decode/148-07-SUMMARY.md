---
phase: 148-numeric-database-values-the-at28c-vcc-decode
plan: 07
subsystem: database
tags: [chip_database, schema-migration, golden-inventory, ast-walk, gate-proof, extra_chips]

requires:
  - phase: 148-03
    provides: "build_db.py's numeric mv/us schema (vcc_mv/vdd_mv/vpp_mv/pulse_duration_us) emitted and regenerated into chip_database.json"
  - phase: 148-06
    provides: "VCC margin-rail substitution landed; full suite at 1630 passed / 3 failed, all 3 failures being this plan's own frozen-golden mismatch"
provides:
  - "tests/golden/chip_database_field_inventory.json re-derived by independent traversal + AST walk for the numeric mv/us schema (D-13): 6 electrical keys (vcc_mv/vdd_mv/vpp_mv replacing vcc/vdd/vpp), programming.pulse_duration_us (replacing pulse_duration), 25 generator_emitted_chip_entry_keys (down from 26)"
  - "148-GOLDEN-TRANSCRIPTS.md: six seen-to-fail transcripts (legs A-F) proving the gate can still fail before being trusted green, including a new Phase-148-specific leg (E) planted inside tools/extra_chips.json itself"
  - "Full app suite restored to 1633 passed, 0 failed -- the last transient from the numeric schema migration retired"
affects: [148-08]

tech-stack:
  added: []
  patterns:
    - "Golden re-derivation discipline (D-13): every number in a frozen schema-freeze golden is computed by a throwaway script that imports the test module's own _walk/_generator_chip_entry_keys/_extra_chips_entry_keys helpers against the live tree, never by copying numbers out of a failing test's error message or hand-editing a count"
    - "Gate seen-to-fail proof before trust (D-15): a frozen-golden gate is not trusted green until proven capable of failing on planted violations, each run in a child process (env var on the command line, never monkeypatch, since _DB_PATH/_GEN_PATH resolve at import time)"

key-files:
  created: []
  modified:
    - firestarter_app/tests/golden/chip_database_field_inventory.json
    - .planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-GOLDEN-TRANSCRIPTS.md

key-decisions:
  - "Re-derived every number via a throwaway script (not committed) that imports tests/test_chip_database_field_inventory.py's own _walk, _generator_chip_entry_keys, and _extra_chips_entry_keys helpers directly against the live tree, rather than reimplementing the traversal/AST-walk logic a second time -- guarantees the derivation used the exact same code path the gate itself uses, with zero risk of a second, subtly-different implementation silently diverging from the gate's own semantics"
  - "meta.recorded_by/requirement/decision header fields updated to '148-07'/'DATA-02'/'D-13' (the plan's own provenance) while the five prose fields the plan requires byte-identical (why_counts_not_names, why_not_diff_db, how_to_update, db_is_generated, generator_scan_scope) were left untouched, verified programmatically against git show HEAD's pre-change copy"
  - "Leg E (Phase-148-specific, absent from the Phase 140 Plan 03 precedent) plants a key inside the REAL tools/extra_chips.json record rather than a scratch copy, because _EXTRA_CHIPS_PATH is deliberately not environment-overridable -- run last, immediately before Leg F, with a pre-plant byte-exact backup restored and git-diff-verified before Leg F ran, so a failed restore could not contaminate the clean-tree GREEN leg"

requirements-completed: [DATA-02]

coverage:
  - id: D1
    description: "tests/golden/chip_database_field_inventory.json re-derived by independent traversal of the live 746-chip chip_database.json plus an AST walk of build_db.py's chip_entry construction unioned with a key scan of tools/extra_chips.json: levels.electrical now has exactly 6 keys (pin_count/size_bytes/type/vcc_mv/vdd_mv/vpp_mv, each 746, no vcc/vdd/vpp); levels.programming carries pulse_duration_us:746 (no pulse_duration); generator_emitted_chip_entry_keys has exactly 25 names (vcc_mv/vdd_mv/pulse_duration_us present, vcc/vdd/vpp/pulse_duration absent); totals (59/746), protocol_chip_counts ({7:170,8:127,11:32}), and levels.top (11 keys) all unchanged and asserted so; meta prose byte-identical apart from recorded_at_head (advanced to 14b62d8) and the recorded_by/requirement/decision header"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts=\"\" -v -- 8 passed; inline python assertion script confirming every golden number, totals, protocol counts, levels.top count, recorded_at_head format/change, and meta prose byte-identity against git show HEAD's pre-change copy -- all pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "Six seen-to-fail transcripts captured verbatim in 148-GOLDEN-TRANSCRIPTS.md: Leg A (new field on one chip, FIRESTARTER_CHIP_DB_JSON) RED on test 2 with added={'foo':1}; Leg B (delete a chip, no new name) RED on tests 1/2/3/4/5 all count_changed, zero added/removed, proving counts-not-names; Leg C (vacuous {} target) RED on test 5's explicit non-vacuity guard; Leg D (new key in generator only, FIRESTARTER_BUILD_DB_SOURCE) RED on test 6 with added=['foo']; Leg E (Phase-148-specific: new key inside the real tools/extra_chips.json, no env seam, restored byte-exact) RED on test 6 via the supplement half of the union that RESEARCH F-1 made load-bearing; Leg F (clean tree) GREEN at 8 passed"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "148-GOLDEN-TRANSCRIPTS.md contains headings for legs A-F; legs A-E each record a non-zero exit code (1) and name the numbered test that went RED; leg D's transcript contains FIRESTARTER_BUILD_DB_SOURCE, legs A/B/C contain FIRESTARTER_CHIP_DB_JSON, leg E contains extra_chips.json; leg F records '8 passed' and exit code 0; git -C firestarter_app diff --quiet succeeds and git status --porcelain tools/extra_chips.json is empty after all legs; python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts=\"\" -q passes 8/8 on the restored tree -- all pass"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full app suite at ZERO failures: 1633 passed, 0 failed (up from Plan 06's 1630 passed/3 failed baseline -- the 3 previously-failing test_chip_database_field_inventory.py tests now pass, 0 net new failures). GATE-02 (diff_db.py) and GATE-03 (check_dispatch.py) both still exit 0 with their expected distributions after the golden update, confirming the re-derivation touched only the frozen-inventory artifact, not the database or generator themselves"
    requirement: "DATA-02"
    verification:
      - kind: unit
        ref: "python3 -m pytest -o addopts=\"\" -q -- 1633 passed, 1 warning, 212.27s (0:03:32), 32 snapshots passed; python3 tools/diff_db.py; echo EXIT=$? -- EXIT=0, 744 changed (56 RULE_VCC_MARGIN_RAIL + 686 PROV01_PROTECT_METADATA + 2 PGSZ_PAGE_SIZE), 0 NEW, 0 MISSING; python3 tools/check_dispatch.py; echo EXIT=$? -- EXIT=0, 0 dispatch regressions, 0 consistency violations"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-08-19
status: complete
---

# Phase 148 Plan 07: Golden Field-Inventory Re-Derivation & Six-Leg Gate Proof Summary

**Re-derived `tests/golden/chip_database_field_inventory.json` by independent traversal + AST walk for the numeric mv/us schema (6 electrical keys, `pulse_duration_us`, 25 generator keys), then proved the gate can still fail on six planted legs (five RED, one new to this milestone against `tools/extra_chips.json` itself) before trusting it green — retiring the last transient of Phase 148's schema migration, full suite now 1633 passed / 0 failed.**

## Performance

- **Duration:** ~40 min
- **Started:** 2026-08-19T12:35:00Z (approx)
- **Completed:** 2026-08-19T13:15:00Z (approx)
- **Tasks:** 2 completed
- **Files modified:** 2 (both in-place updates, no new files)

## Accomplishments

- Re-derived every number in `tests/golden/chip_database_field_inventory.json` by writing a throwaway script (not committed) that imports `tests/test_chip_database_field_inventory.py`'s own `_walk`, `_generator_chip_entry_keys`, and `_extra_chips_entry_keys` helpers and runs them directly against the live 746-chip `chip_database.json`, the live `tools/build_db.py`, and the live `tools/extra_chips.json` — never copying numbers out of the failing test's error message and never hand-editing a count.
- Confirmed every expected delta landed exactly as the plan predicted: `levels.electrical` shrank from 7 to 6 keys (`vcc`/`vdd`/`vpp` removed; `vcc_mv`/`vdd_mv` added at 746 each; `vpp_mv` stays at 746); `levels.programming`'s `pulse_duration` (746) became `pulse_duration_us` (746); `generator_emitted_chip_entry_keys` shrank from 26 to exactly 25 names (`vcc`→`vcc_mv`, `vdd`→`vdd_mv`, `pulse_duration`→`pulse_duration_us`, `vpp` dropped with no replacement). `totals` (59 manufacturers / 746 chips), `protocol_chip_counts` (`{7:170, 8:127, 11:32}`), and `levels.top` (11 keys) all confirmed unchanged by explicit assertion, not assumption.
- `meta`'s five prose fields (`why_counts_not_names`, `why_not_diff_db`, `how_to_update`, `db_is_generated`, `generator_scan_scope`) verified byte-identical to the pre-change golden via `git show HEAD:...` diff — only `recorded_at_head` (advanced to the current `firestarter_app` HEAD, `14b62d8`) and the header provenance fields (`recorded_by`/`requirement`/`decision` → `148-07`/`DATA-02`/`D-13`) changed.
- All 8 field-inventory tests pass on the real tree.
- Proved the gate is still capable of failing: six legs captured verbatim in `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-GOLDEN-TRANSCRIPTS.md`. Legs A-D reuse the Phase 140 Plan 03 precedent shape exactly (a new field on one chip; a chip deletion with no new name, proving counts-not-names; a vacuous `{}` target; a new key in the generator's `chip_entry` construction only) — all via `mktemp -d` scratch copies outside both repos, `FIRESTARTER_CHIP_DB_JSON`/`FIRESTARTER_BUILD_DB_SOURCE` set on the child-process command line (never `monkeypatch`, since `_DB_PATH`/`_GEN_PATH` resolve at import time). Leg E is new to this milestone: a key planted directly inside the real `tools/extra_chips.json` record (which has no environment seam by design), run, observed RED on test 6 via the supplement half of the generator-key union, then restored byte-exact and `git diff --quiet`-verified before Leg F ran. Leg F (clean tree) confirmed GREEN at 8 passed, exit 0.
- Confirmed `firestarter/data/chip_database.json`, `tools/build_db.py`, and `tools/extra_chips.json` are all byte-unchanged after all six legs (`git diff --quiet` clean before, between, and after every leg).
- Re-ran `tools/diff_db.py` (GATE-02) and `tools/check_dispatch.py` (GATE-03) after the golden update: both still exit 0 with their expected distributions (744 changed / 56 `RULE_VCC_MARGIN_RAIL` / 686 `PROV01_PROTECT_METADATA` / 2 `PGSZ_PAGE_SIZE`; 0 dispatch regressions) — confirming the golden re-derivation touched only the frozen-inventory artifact itself, nothing downstream.
- Full app suite: **1633 passed, 0 failed** (up from Plan 06's 1630 passed / 3 failed baseline — the 3 previously-failing `test_chip_database_field_inventory.py` tests now pass, 0 net new failures). This retires the last transient from Phase 148's numeric mv/us schema migration (introduced in 148-03).

## Task Commits

Task 1 committed inside the `firestarter_app` submodule, on branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`; Task 2 committed in the meta repo (no `firestarter_app` code change — pure verification/proof work):

1. **Task 1: Re-derive the frozen inventory by independent traversal** — `7efe504` (docs) — `firestarter_app`
2. **Task 2: Prove the gate still fails — six planted legs, captured verbatim** — no `firestarter_app` commit (pure verification against the already-committed golden; all six legs left the tree byte-unchanged) — `1aa58397` (docs, `148-GOLDEN-TRANSCRIPTS.md`) — meta repo

_No REFACTOR commit was needed._

## Files Created/Modified

- `firestarter_app/tests/golden/chip_database_field_inventory.json` — re-derived: `levels.electrical` (6 keys), `levels.programming.pulse_duration_us`, `generator_emitted_chip_entry_keys` (25 names), `meta.recorded_at_head` advanced; `totals`/`protocol_chip_counts`/`levels.top` unchanged; other `meta` prose byte-identical
- `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-GOLDEN-TRANSCRIPTS.md` — new file: six verbatim leg transcripts (A-F), seam-mechanics explanation, and the post-run integrity check

## Decisions Made

- Derived every golden number by importing the test module's own helper functions (`_walk`, `_generator_chip_entry_keys`, `_extra_chips_entry_keys`) against the live tree, rather than reimplementing the traversal/AST-walk logic a second time in the throwaway script — this guarantees the derivation exercises the exact same code path the gate itself uses when it runs, eliminating any risk of a second, subtly different implementation silently diverging from the gate's real semantics.
- Updated `meta.recorded_by`/`requirement`/`decision` to this plan's own provenance (`148-07`/`DATA-02`/`D-13`) while leaving the five `how_to_update`-mandated prose fields untouched — verified programmatically against `git show HEAD`'s pre-change copy rather than by eye.
- Ran Leg E (the new, Phase-148-specific planted violation) last, immediately before the clean-tree Leg F, exactly as the plan requires — a `mktemp`-backed byte-exact copy of `tools/extra_chips.json` was taken before the plant and restored immediately after observing RED, with `git diff --quiet tools/extra_chips.json` confirmed clean before Leg F ran, so a failed restore could never contaminate the GREEN leg.

## Deviations from Plan

None — plan executed exactly as written. Every predicted delta in Task 1's `<action>` block (electrical 7→6 keys, programming pulse_duration→pulse_duration_us, generator keys 26→25, totals/protocol_chip_counts/levels.top unchanged) matched the measured re-derivation exactly on the first attempt; no surprise required stopping to investigate. All six legs in Task 2 produced the exact RED/GREEN outcomes the plan's table specified, on the first attempt, with no locator fix needed.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Requirements Handling

**DATA-02 is marked `Complete`** in both `REQUIREMENTS.md` and its traceability table. Per this plan's explicit instruction, DATA-02 was claimed by 148-03 (generator emits the numeric schema, both emission paths), 148-04 (`database.py`'s `_map_data` restored to read the new schema), and this plan, 148-07, which is the **last** of DATA-02's claimants — it re-derives the frozen schema-freeze golden that the migration moved, closing the requirement end-to-end. `roadmap.update-plan-progress` was run to update the Phase 148 plan-count row (7/8 plans complete).

DATA-03 and DATA-04 are left `Pending` per this plan's explicit scope — 148-08 is the last plan claiming both and is the one that flips their checkboxes. This plan touched neither.

## Next Phase Readiness

Full suite state after this plan: **1633 passed, 0 failed** — zero outstanding test failures anywhere in `firestarter_app`. The frozen schema-inventory gate (TABLE-05/D-12, re-derived this plan under DATA-02/D-13) is proven both correct (8/8 passing on the real tree) and still capable of failing (six seen-to-fail legs, five RED + one GREEN, captured verbatim). GATE-02 (`diff_db.py`) and GATE-03 (`check_dispatch.py`) both confirmed still green with their expected distributions.

No blockers for Plan 148-08, the phase's final plan (DATA-03/DATA-04 closure).

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-07-SUMMARY.md`
- FOUND: `/workspaces/.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-GOLDEN-TRANSCRIPTS.md`
- FOUND: `/workspaces/firestarter_app/tests/golden/chip_database_field_inventory.json` (modified, contains `vcc_mv`, 25 `generator_emitted_chip_entry_keys`)
- FOUND commit `7efe504` (firestarter_app, Task 1)
- FOUND commit `1aa58397` (meta repo, Task 2 transcripts)

All items verified present on disk and in git history. No missing items.

---
*Phase: 148-numeric-database-values-the-at28c-vcc-decode*
*Completed: 2026-08-19*
