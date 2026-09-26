---
phase: 194-real-page-size-reaches-the-firmware
plan: 03
subsystem: host-data-gates
tags: [chip-database, page-size, protocol-0x05, test-invariants, golden-fixtures]

requires:
  - phase: 194-01
    provides: "regenerated chip_database.json (746 rows, 45 page_size carriers: 18 native 0x0D + 27 native 0x05), _PAGE_SIZE_BY_PART deleted"
provides:
  - "test_page_size_invariants.py leg 4/6 moved to the 45-carrier / 45-identity shape, by re-derivation against the pinned upstream join, not by hand edit"
  - "A new 27-row two-halves leg (D-08's host half): every algorithm-5 row's page_size equals its own infoic_page_size_raw, and exactly 18 of 27 also equal the old capacity-bracket derivation, with the other 9 differing by exactly 2x"
  - "test_vcc_margin_rail.py's curated-table guard replaced by an absence assertion (hasattr), keeping the guarantee alive after the table's deletion"
  - "tests/golden/chip_database_field_inventory.json re-derived by independent traversal: programming.page_size 20 -> 45, everything else confirmed unchanged"
affects: [194-04, 194-06]

actuals:
  tokens: 5068
  tasks: 3
  commits: 3
  plan_head_before: "firestarter_app@859109d, meta@820142c4"

tech-stack:
  added: []
  patterns:
    - "Import (not relocate) an in-repo frozenset as an identity oracle across test modules -- tests.test_lock_status_class_partition's _ALGORITHM_0X05_KEYS is imported into test_page_size_invariants.py with a small string-to-tuple adapter and its own count guard, rather than re-authored or moved"
    - "Absence assertion (hasattr) replacing a count assertion when the counted object is deleted outright -- keeps the guard's failure mode readable instead of an AttributeError"
    - "A deleted firmware derivation rule, written out as a local test function, becomes the only surviving oracle for a no-regression proof once the code path it audited is gone"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_page_size_invariants.py
    - firestarter_app/tests/test_vcc_margin_rail.py
    - firestarter_app/tests/golden/chip_database_field_inventory.json

key-decisions:
  - "Tasks 1 and 2 committed together (c0289d2), matching the precedent recorded in 194-02-SUMMARY.md: both touch the same file with no clean seam once the 27-row leg is added on top of the widened identity sets."
  - "The 27 0x05 identities were imported from tests/test_lock_status_class_partition.py's _ALGORITHM_0X05_KEYS rather than duplicated, per the plan's stated preference. The frozenset uses a 'MFG/part' string separator there. A one-line adapter (tuple(key.split('/', 1))) converts each entry to this module's (mfr, part) tuple shape. A len()==27 guard makes a partial import fail loudly."
  - "Leg 6's function name (test_every_page_size_carrier_is_curated_or_native_0x0d) was left unchanged, matching the exact name given in the wave-context failing-test list. Only its message text was rewritten to drop 'curated' and add the 0x05 half, since the plan named a rename requirement only for leg 4's function."

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "test_page_size_invariants.py leg 4 (carrier count) and leg 6 (provenance allow-list) move from 20/20-identities to 45/45-identities, re-derived from the upstream provenance join (194-RESEARCH.md R1), not hand-edited. Both synthetic non-vacuity legs (10, 11) verified unchanged and still passing."
    requirement: "PAGE-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_page_size_invariants.py -- 12 tests, 0 failed"
        status: pass
    human_judgment: false
  - id: D2
    description: "New 27-row two-halves leg. Half (a): all 27 algorithm-5 rows carry page_size == infoic_page_size_raw. Half (b): exactly 18 of 27 also equal the old capacity-bracket derivation (64/128/256 by size_bytes). The other 9 differ by exactly 2x, with the emitted value the larger of the pair. Verified against the regenerated database with the independent TABLE-OK script."
    requirement: "PAGE-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_page_size_invariants.py::test_all_27_algorithm_5_rows_carry_their_real_page_and_18_match_the_old_derivation"
        status: pass
    human_judgment: false
  - id: D3
    description: "test_vcc_margin_rail.py's third assertion replaced with an absence assertion (not hasattr(build_db, '_PAGE_SIZE_BY_PART')). The leg is kept, not deleted. Its other two assertions are untouched."
    requirement: "PAGE-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_vcc_margin_rail.py::test_vcc_voltages_table_unedited_and_no_new_part_keyed_dict"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/golden/chip_database_field_inventory.json re-derived by an independent traversal of the regenerated database. programming.page_size moved 20 -> 45. infoic_page_size_raw is confirmed still 744. Every other level (top, electrical, totals) is confirmed unchanged."
    requirement: "PAGE-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_database_field_inventory.py -- 6 tests, 0 failed"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-09-15
status: complete
---

# Phase 194 Plan 03: Real Page Size Reaches the Firmware (Host Data Gates) Summary

**The three host gates plan 01 left RED by design (the 20->45 carrier count, the curated-table guard, and the field-inventory golden) all moved by re-derivation. A new 27-row leg makes D-08's no-regression proof a measurement instead of an assertion: all 27 protocol-0x05 parts now carry their real page, and exactly the 18 whose old derivation was already right did not move.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-09-15T17:40:00Z
- **Tasks:** 3/3
- **Files modified:** 3

## Accomplishments

- **Leg 4** (`test_page_size_invariants.py`) renamed and re-asserted: `test_exactly_20_page_size_carriers_across_all_746_rows` -> `test_exactly_45_page_size_carriers_across_all_746_rows`, asserting exactly 45 carriers across 746 total rows (18 upstream-native 0x0D + 27 upstream-native 0x05, no curated carrier remains). The 45 is the re-derived figure from 194-RESEARCH.md's independent join against pinned minipro `a8efaedc`, not a transcription of the database's current output.
- **Leg 6** widened to a 45-identity provenance allow-list: `_NATIVE_0X0D_PAGE_SIZE_IDENTITIES (18) | _NATIVE_0X05_PAGE_SIZE_IDENTITIES (27)`. The 27 identities are imported from `tests/test_lock_status_class_partition.py::_ALGORITHM_0X05_KEYS` (not duplicated, not relocated), adapted from that module's `"MFG/part"` string shape to this module's `(mfr, part)` tuple shape, with its own `len() == 27` guard. `_CURATED_PAGE_SIZE_IDENTITIES` is deleted -- both its members are 0x05-native and arrive in the new set.
- **New leg 12**, the host half of D-08. For all 27 algorithm-5 rows, `programming.page_size == programming.infoic_page_size_raw` (the part's real page). The test also re-implements the old, now-firmware-deleted capacity-bracket derivation locally (`64` up to 65536 bytes, `128` up to 262144, else `256`). Exactly 18 of the 27 rows match that derivation's output. The other 9 differ, each by exactly a factor of 2, with the emitted (real) value the larger of the pair. The old derivation function is written out inside the test. Per D-06 it no longer exists anywhere else.
- **`test_vcc_margin_rail.py`**'s third assertion (`len(build_db._PAGE_SIZE_BY_PART) == 2`) is replaced with `assert not hasattr(build_db, "_PAGE_SIZE_BY_PART")`. The leg survives, strengthened rather than weakened. An `AttributeError` would have been an opaque test error, not a readable assertion failure. The guarantee ("no part-number-keyed page-size table exists") is now confirmed by absence rather than by count.
- **`tests/golden/chip_database_field_inventory.json`** is re-derived by running the file's own prescribed independent traversal against the regenerated database (see Traversal Output below). Only `programming.page_size` moved (20 -> 45). Every other number was re-derived and confirmed unchanged, not merely assumed. That includes `infoic_page_size_raw`, which stays at 744.
- Both synthetic non-vacuity legs (10, 11) in `test_page_size_invariants.py` re-run and confirmed unchanged and still passing, so the widened 45-identity allow-list cannot pass vacuously.
- `firestarter_app`'s planning-citation gate re-run after fixing two comments that initially cited "Phase 194" and "D-08" directly in `#` comments (caught by the gate itself before commit; see Deviations).

## Traversal Output (golden re-derivation, verbatim)

```
manufacturers 59 chips 746
top {'electrical': 746, 'part_number': 746, 'pinout': 746, 'programming': 746, 'support_status': 746, 'unsupported_reason': 10, 'datasheet': 2, 'provenance': 2, 'source': 2, 'verification_note': 2, 'verification_status': 2}
programming {'algorithm': 746, 'chip_id_check': 746, 'chip_id_value': 746, 'infoic_page_size_raw': 744, 'protect_off_before': 744, 'protect_on_after': 744, 'pulse_duration_us': 746, 'page_size': 45}
electrical {'pin_count': 746, 'size_bytes': 746, 'type': 746, 'vcc_mv': 746, 'vdd_mv': 746, 'vpp_mv': 746}
```

Compared field-by-field against the committed golden: only `programming.page_size` (20 -> 45) differs. `totals.manufacturers` (59) and `totals.chips` (746) are unchanged.

## Docstring Rewordings

- `test_page_size_invariants.py` module docstring. The coverage list widened from 11 to 12 legs. Leg 4's description used to read "(18 native + 2 curated)". It now reads "(18 upstream-native 0x0D rows + 27 upstream-native 0x05 rows -- no curated carrier remains, per Phase 194 D-01/D-02)". Leg 6's description dropped "curated" and named the 27-identity native-0x05 set. Leg 12's description was added, describing the new two-halves table.
- `_provenance_offenders()` docstring: "neither one of the 2 curated rows nor one of the 18 named upstream-native 0x0D rows" became "neither one of the 18 named upstream-native 0x0D rows nor one of the 27 named upstream-native 0x05 rows".
- `test_vcc_margin_rail.py` module docstring (coverage item 4) and the target function's docstring. Old wording: "`_PAGE_SIZE_BY_PART` still has exactly 2 entries". New wording: "the generator carries no `_PAGE_SIZE_BY_PART` attribute at all". Both versions add the same closing clause: no part-number-keyed page-size table exists, curated or otherwise.
- `tests/golden/chip_database_field_inventory.json`'s `meta.why_counts_not_names` prose. The count moved from "page_size (2 of 746)" to "page_size (45 of 746)". The "SIXTH chip" phrasing was generalized to "a further chip". The illustration no longer involves a two-entry curated set. A new `meta.phase_194_update` key was added alongside the existing `meta.phase_149_update` key. It records this plan's re-derivation the same way Phase 149's own entry recorded its own. The existing `phase_149_update` text is untouched.

All of the above are docstring/JSON-string rewordings, not `#` comments, and none introduce new explanatory prose beyond restating the changed count -- consistent with the plan's own instruction and this project's no-comments rule.

## Task Commits

Each task landed in `firestarter_app`, per `commits_land_in`:

1. **Task 1 + Task 2: widen the carrier count to 45, widen the allow-list to 45 identities, add the 27-row D-08 leg** -- `firestarter_app@c0289d2` (test). Committed together: both touch the same file with no clean seam, matching the precedent in 194-02-SUMMARY.md.
2. **Task 3: absence-assert the deleted curated table, re-derive the field-inventory golden** -- `firestarter_app@33e7ea2` (test)
3. **Gitlink advance** -- meta `43bfe126` (test)

**Plan metadata:** committed below (this SUMMARY only -- STATE.md/ROADMAP.md are owned by the orchestrator in this repo, per the shared_artifact_rule override)

## Files Created/Modified

- `firestarter_app/tests/test_page_size_invariants.py` - leg 4 renamed/re-asserted to 45; leg 6's allow-list widened to the imported 27-identity 0x05 set; new leg 12 (27-row two-halves table); module docstring and `_provenance_offenders()` docstring reworded.
- `firestarter_app/tests/test_vcc_margin_rail.py` - third assertion in the target function replaced with a `hasattr` absence check; module docstring item 4 and the function's own docstring reworded.
- `firestarter_app/tests/golden/chip_database_field_inventory.json` - `levels.programming.page_size` 20 -> 45; `meta.why_counts_not_names` reworded; new `meta.phase_194_update` key added.

## Decisions Made

- **Tasks 1 and 2 committed together**, as `firestarter_app@c0289d2`. Both target `test_page_size_invariants.py` with no clean textual seam. The 27-row leg (task 2) is additive and independent of the identity-set changes (task 1). Splitting the diff after drafting and verifying both together would have meant reverting and reapplying half of an already-green change. That would add no verification value. Both tasks' acceptance criteria were independently re-confirmed against the single resulting commit. This mirrors the identical call made in 194-02, for the same reason.
- **Leg 6's function name was left unchanged** (`test_every_page_size_carrier_is_curated_or_native_0x0d`), matching the exact failing-test name given in this plan's wave-context. Only its message text changed. The plan's own instructions named a rename requirement explicitly for leg 4's function only ("the current name encodes 20"). Leg 6's name does not encode a count, so it was left as-is rather than renamed speculatively.
- **The 27 `0x05` identities were imported, not duplicated by hand**, from `tests/test_lock_status_class_partition.py::_ALGORITHM_0X05_KEYS`, per the plan's instruction to source rather than re-author. A one-line adapter converts that module's `"MFG/part"` string separator to this module's `(mfr, part)` tuple shape. A `len() == 27` assertion guards against a silently partial import.
- No architectural deviations (Rule 4) were needed. D-01, D-02, D-04 and D-08's host half were followed as specified.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - blocking issue] Two new comments in `test_page_size_invariants.py` cited "Phase 194" and "D-08" directly, tripping the planning-citation gate**
- **Found during:** Task 3's citation-gate verification step, run against the tree after Tasks 1-3's edits.
- **Issue:** while drafting Task 1's import-adapter comment and Task 2's leg-12 section header, two `#` comments were written. They cited `Phase 194 D-02` and `D-08` directly. `tools/planning_citation_gate.py` flagged both: `tests/test_page_size_invariants.py:77: [phase-or-plan-ref: Phase 194]` and `:440: [decision-id: D-08]`. This is exactly the class of comment `CLAUDE.md` and this plan's own prohibitions forbid in product/test source. Plan, task and decision citations belong in the commit message or SUMMARY.md, never in a comment.
- **Fix:** reworded both comments to describe the mechanism instead. The first now describes an imported frozenset with an adapter. The second now names a leg number and its two-halves description. Neither names the phase or decision ID. A second citation-gate run confirmed the fix: `OK: 140 files scanned, no planning citations.`
- **Files modified:** `firestarter_app/tests/test_page_size_invariants.py`
- **Committed in:** `firestarter_app@c0289d2` (caught and fixed before this commit was made). The committed content carries no citation.

**Total deviations:** 1 auto-fixed (comment citation caught by the project's own gate before commit). No scope creep, no behavioral change.

## Issues Encountered

- **`tests/test_chip_database_field_inventory.py`'s own module docstring names 8 coverage legs**, including `test_generator_emits_no_key_outside_the_frozen_inventory` and `test_this_module_is_collected_and_never_skipped`. The file currently defines only 6 top-level `def test_` functions. This is pre-existing drift, unrelated to this plan. The file is not in this plan's `files_modified` list, and the plan's own prohibitions do not name it as touchable. The module's actual 6 tests all pass, including the ast-walk machinery this plan's Step 3 needed to confirm. `pytest tests/test_chip_database_field_inventory.py -o addopts="" -q` reports `6 passed`. The ast leg's underlying helpers (`_generator_chip_entry_keys`, `_collect_dict_keys` with its `IfExp` branch handling) are present. They are exercised via `test_top_level_field_inventory_matches`, which passed against the regenerated database. `build_db.py`'s emit arm is still shaped as an `IfExp` inside the same `**{...}` unpacking, per plan 01's preserved constraint. This is not itemized as a Rule-1 fix, because it sits entirely outside this plan's file scope. It is flagged here so a future audit of that module's own docstring is not surprised by the count.

## App-Suite Pass/Fail Counts

**Before** (measured at plan start, before any edit in this plan): `4 failed` in the four host-gate legs named in the wave-context (`test_page_size_invariants.py` x2, `test_vcc_margin_rail.py` x1, `test_chip_database_field_inventory.py` x1) when scoped to those four modules. Full-suite run: **1879 passed, 7 failed** (the 4 above, plus the 2 wire-dict failures and the 1 error-band-guard failure, none of which belong to this plan).

**After** (measured on the final committed tree): full-suite run: **1884 passed, 3 failed**. The 3 remaining failures are exactly `tests/test_wire_dict_equivalence.py` (2, plan 194-04's) and `tests/test_protection_status_catalog.py::test_error_band_last_free_id_unspent` (1, plan 194-06's). Both are unchanged from before this plan ran, confirmed by re-running each in isolation and comparing failure text. All 4 gates named as this plan's responsibility are green.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All three host data gates named in this plan's wave-context are green. Each moved by re-derivation, against the pinned upstream join or the golden's own re-derivation instruction, never by pasting a literal.
- The 27-row two-halves leg gives D-08's host half a measured proof, not an assertion. All 27 protocol-0x05 parts carry their real page. The 18 already-correct parts did not move. The 9 corrected parts moved by exactly 2x.
- The 2 wire-dict failures (`tests/test_wire_dict_equivalence.py`) remain RED, untouched, for plan 194-04.
- The 1 error-band-guard failure (`tests/test_protection_status_catalog.py::test_error_band_last_free_id_unspent`) remains RED, untouched, for plan 194-06.
- `.planning/REQUIREMENTS.md` is untouched by design. PAGE-01/PAGE-02 stay open until plan 06 flips them, after all software evidence exists.
- No stubs, skipped tests, or unrun `<verify>` blocks exist in this plan's own deliverables. The pre-existing docstring/function-count drift in `test_chip_database_field_inventory.py` (see Issues Encountered) is out of this plan's scope. It is not itemized as a stub of this plan's making, and it is not appended to `.planning/WINDOWS.md` for that reason.

## Self-Check: PASSED

All 3 modified files confirmed present on disk: `[ -f firestarter_app/tests/test_page_size_invariants.py ]`, `[ -f firestarter_app/tests/test_vcc_margin_rail.py ]`, `[ -f firestarter_app/tests/golden/chip_database_field_inventory.json ]` all succeed. All 3 commit hashes confirmed present: `git -C firestarter_app log --oneline --all | grep -q c0289d2`, `git -C firestarter_app log --oneline --all | grep -q 33e7ea2`, and `git log --oneline --all | grep -q 43bfe126` (meta) all succeed. `git -C firestarter_app status --porcelain` is empty. Meta HEAD is confirmed on `v1.39-protocol-0x05-write-correctness`. No stray `gsd/...-activated-...` branch was created, because plain `git commit` was used throughout, not `gsd-tools query commit`.

---
*Phase: 194-real-page-size-reaches-the-firmware*
*Completed: 2026-09-15*
