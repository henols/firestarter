---
phase: 198-the-two-voltage-nibbles
plan: 01
subsystem: database
tags: [chip-database, vpp, vdd, datasheet-overrides, wire-protocol, decode-tables]

requires:
  - phase: 197-the-override-mechanism-and-the-program-pulse
    provides: the datasheet_overrides.json loader/apply mechanism, the wire-dict delta-layer pattern, and the DECODE-NOTES.md section-per-finding convention
provides:
  - Corrected FUJITSU/MBM27C1001 and FUJITSU/MBM27C4001 electrical.vpp_mv (12000 -> 12500)
  - Corrected FUJITSU/MBM27128, FUJITSU/MBM27C1001 and FUJITSU/MBM27C4001 electrical.vdd_mv (5500 -> 6000)
  - Phase 198 wire-dict delta layer (tests/golden/wire_dict_expected_deltas_198.json), generated programmatically, closing the known-red window it opened
  - Completed VPP_MV decode table (xg_vpp_voltages[] 0xF1/0xF2) with an exact-match-before-mask decode, byte-identical regeneration
  - DECODE-NOTES.md Section 9 (decode provenance subsection), opened for completion by plan 198-03
affects: [198-02, 198-03, 198-04, "any future phase touching build_db.py's VPP_MV/VCC_VOLTAGES or datasheet_overrides.json"]

actuals:
  tokens: 7858
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Exact-match-before-mask decode: a module-level frozenset derived from the table's own non-zero-low-nibble keys, checked before the & 0xF0 fallback, so a future table addition with option bits extends the exempt set automatically."
    - "Wire-dict delta layers generated programmatically from a live-capture diff script, never hand-transcribed (the |<i> positional-index key suffix rots on row reorder)."

key-files:
  created:
    - firestarter_app/tests/golden/wire_dict_expected_deltas_198.json
    - firestarter_app/tests/test_vpp_decode_table.py
  modified:
    - firestarter_app/tools/datasheet_overrides.json
    - firestarter_app/tools/build_db.py
    - firestarter_app/tools/DECODE-NOTES.md
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tests/test_datasheet_overrides.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - firestarter_app/tests/test_wire_dict_equivalence.py

key-decisions:
  - "D-07: VPP corrected to 12500 (datasheet nominal), not 12200 (the literal floor with no margin)."
  - "D-08: FUJITSU/MBM27C2001 left untouched at 12000 -- no vendored datasheet, and citing a sibling's reading is what 197 D-02 forbids."
  - "D-09: vdd_mv corrected to 6000 in this phase (not deferred to Phase 200) for the three rows whose vendored datasheets state it."
  - "D-02: VPP_MV completed from xg_vpp_voltages[] (0xF1=25000, 0xF2=21000); exact-match-before-mask used instead of a literal full-byte re-key, which measured breakage on 142 rows."
  - "The deleted 5-line VPP_MV comment's facts were relocated to DECODE-NOTES.md Section 9 in the same commit, per CLAUDE.md's comment-deletion discipline; the block is quoted verbatim below."

requirements-completed: [VOLT-01, VOLT-02]

coverage:
  - id: D1
    description: "FUJITSU/MBM27C1001 and FUJITSU/MBM27C4001 emit vpp_mv 12500; FUJITSU/MBM27128, MBM27C1001 and MBM27C4001 emit vdd_mv 6000; FUJITSU/MBM27C2001 stays at (12000, 5500); regeneration diff is exactly 3 rows / 5 electrical fields with an identical row-key set and support_status multiset."
    requirement: "VOLT-02"
    verification:
      - kind: unit
        ref: "tests/test_characterization.py::test_list (snapshot)"
        status: pass
      - kind: unit
        ref: "tests/test_datasheet_overrides.py::TestShippedOverrideFileContract"
        status: pass
      - kind: unit
        ref: "tests/test_chip_database_field_inventory.py"
        status: pass
      - kind: unit
        ref: "tests/test_vcc_margin_rail.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "Phase 198 wire-dict delta layer (2 records, vpp_mv 12500 each), generated programmatically, wired into the composition test and proven capable of failing; golden baseline and all five prior layers stay byte-unchanged; the two tests it reddened in Task 1 are closed by name."
    requirement: "VOLT-02"
    verification:
      - kind: unit
        ref: "tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden_plus_the_149_and_153_and_182_and_194_and_197_and_198_deltas"
        status: pass
      - kind: unit
        ref: "tests/test_wire_dict_equivalence.py::test_exactly_84_records_change_flags_and_no_other_field_moves"
        status: pass
      - kind: unit
        ref: "tests/test_wire_dict_equivalence.py::test_the_198_delta_layer_is_capable_of_failing"
        status: pass
    human_judgment: false
  - id: D3
    description: "VPP_MV completed to 18 entries (0xF1=25000, 0xF2=21000) from xg_vpp_voltages[]; decode exact-matches before masking, derived from the table itself; regeneration after this change is byte-identical to Task 1's committed database; no row emits vpp_mv 0."
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "tests/test_vpp_decode_table.py"
        status: pass
      - kind: unit
        ref: "full suite: 2069 passed, 0 failed (Python 3.11)"
        status: pass
    human_judgment: false

duration: ~15min
completed: 2026-09-18
status: complete
---

# Phase 198 Plan 01: The Fujitsu VPP/VDD tracer and the completed VPP decode Summary

**Moved MBM27C4001's VPP from 12.0V to 12.5V end-to-end (database, override file, snapshot, wire dict), corrected the sibling MBM27C1001 and MBM27128 program-VDD/VPP figures against their own vendored datasheets, and completed+fixed the `VPP_MV` decode table's 0xF0 mask so 25V/21V no longer collapse onto 18V.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-09-18T18:50Z (approx, first regeneration run)
- **Completed:** 2026-09-18T19:04Z
- **Tasks:** 3
- **Files modified:** 9 (2 newly created)

## Accomplishments

- `FUJITSU/MBM27C1001` and `FUJITSU/MBM27C4001` now emit `electrical.vpp_mv: 12500` (was 12000) — the datasheet nominal (12.5V ± 0.3V), not the literal floor.
- `FUJITSU/MBM27128`, `FUJITSU/MBM27C1001` and `FUJITSU/MBM27C4001` now emit `electrical.vdd_mv: 6000` (was 5500) — all three vendored datasheets state 6.0V ± 0.25V.
- `FUJITSU/MBM27C2001` intentionally left at `(12000, 5500)` — no vendored datasheet for that row (D-08).
- The Phase 198 wire-dict delta layer (`tests/golden/wire_dict_expected_deltas_198.json`) generated programmatically from the live capture, closing the two tests Task 1 reddened.
- `VPP_MV` completed from upstream's `xg_vpp_voltages[]` (0xF1=25000, 0xF2=21000), with an exact-match-before-mask decode replacing the plain `& 0xF0` lookup — proven byte-identical on regeneration.
- `DECODE-NOTES.md` Section 9 opened, carrying the decode-provenance facts the deleted 5-line `VPP_MV` comment held.

## Task Commits

Each task was committed atomically inside `firestarter_app` (all on `v1.40-program-parameter-fidelity`), with the meta-repo gitlink advanced in a following commit:

1. **Task 1: A datasheet voltage reaches the operator** — `961f795` (fix) / meta `6af2e3aa`
2. **Task 2: The Phase 198 wire delta layer, generated not transcribed** — `873bbb5` (test) / meta `c0fcf472`
3. **Task 3: Complete the VPP decode and fix the mask** — `254c4f7` (feat) / meta `6fb90e1f`

**Plan metadata:** this SUMMARY's own commit (below).

_No STATE.md/ROADMAP.md commit — the orchestrator owns those writes for this phase per the execution brief._

## Files Created/Modified

- `firestarter_app/tools/datasheet_overrides.json` — added `FUJITSU/MBM27C4001` (new key), extended `FUJITSU/MBM27C1001` and `FUJITSU/MBM27128` with `electrical.vpp_mv`/`electrical.vdd_mv` fields
- `firestarter_app/tests/test_datasheet_overrides.py` — `_EXPECTED_ENTRY_COUNT` 9 → 10
- `firestarter_app/firestarter/data/chip_database.json` — GENERATED, 3 rows / 5 electrical field values changed
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — targeted 2-line re-record (numstat `2 2`)
- `firestarter_app/tests/golden/wire_dict_expected_deltas_198.json` — new, 2-record delta layer + 5-key `meta` block
- `firestarter_app/tests/test_wire_dict_equivalence.py` — `_DELTAS_198` constant, composition block, 5 new `layer_pairs` tuples, `test_the_198_delta_layer_is_capable_of_failing`, `deltas_198` folded into the 84-count test
- `firestarter_app/tools/build_db.py` — `VPP_MV[0xF1]`/`VPP_MV[0xF2]` added, `_VPP_EXACT_LOW_BYTES` derived constant, exact-match-before-mask decode, 5-line comment deleted
- `firestarter_app/tools/DECODE-NOTES.md` — Section 9 opened (decode-provenance subsection)
- `firestarter_app/tests/test_vpp_decode_table.py` — new, 3 tests pinning the completed table and its derivation

## Decisions Made

- **D-07** applied: VPP corrected to 12500, the datasheet nominal, not 12200.
- **D-08** applied: `FUJITSU/MBM27C2001` left unchanged — no vendored datasheet.
- **D-09** applied: `vdd_mv` corrected in this phase rather than deferred to Phase 200, since the evidence (three matching vendored datasheets) is already on disk.
- **D-02** applied: `VPP_MV` completed from `xg_vpp_voltages[]`; exact-match-before-mask chosen over a literal full-byte re-key after confirming the latter would drop 142 rows to a `0` default (RESEARCH Pitfall 1) — measured directly in this session via the byte-identical-regeneration proof, not merely trusted from RESEARCH.
- **D-16** cited: the deleted comment's facts (the `SST27VF512` `voltages=0x0001` witness row, the corrected `xg_vpp_voltages[]` provenance) relocated to `DECODE-NOTES.md` § 9 rather than lost.

## Deviations from Plan

None of Rule 1-4 category. One self-correction during execution, recorded for transparency:

**Self-corrected: an initial VPP_MV comment replacement violated the no-new-comments rule**
- **Found during:** Task 3, immediately after the first edit
- **Issue:** My first edit to `build_db.py` replaced the deleted 5-line comment with a single corrected `# [VERIFIED: ...]` marker line. This is a NEW comment line (191 - 5 + 1 = 187), which both contradicts the task's explicit instruction ("Delete, do not rewrite") and would have failed the acceptance criterion pinning the comment count at exactly 186.
- **Fix:** Removed the replacement line before running any verify legs or staging anything. `VPP_MV` now has zero comment lines above it, matching the plan's literal instruction.
- **Files affected:** `firestarter_app/tools/build_db.py` (caught and corrected before commit; no bad state was ever staged or committed)
- **Verification:** Comment-line count measured at exactly 186 after the fix; staged-comment check prints nothing.

## Measured Values (per plan `<output>` spec)

- **Task 1 regeneration diff:** exactly 3 rows, 5 field values, all under `electrical`, identical row-key set, identical `support_status` multiset (`DIFF_OK 3 5`).
- **Snapshot re-record `--numstat`:** `2	2` (two lines added, two removed).
- **`len(deltas_198)`:** 2 (`FUJITSU|MBM27C1001|7`, `FUJITSU|MBM27C4001|12`, both `{"vpp_mv": 12500}`).
- **`test_exactly_84_records_change_flags_and_no_other_field_moves`:** composing `deltas_198` into its composition list returned the count to exactly 84 with `changed_fields == {"flags"}`, both assertions byte-unchanged, as the plan's superseding instruction predicted (measured, not assumed — the test passed on the first run after the edit).
- **Deleted comment line count:** 5, quoted verbatim:
  ```
  # Key on (voltages & 0xF0), NOT (voltages & 0xFF). The low byte packs two
  # fields: bits 7-4 are the VPP index (these table keys), bits 3-0 are option
  # flags. Masking the full byte yields Unknown/0 mV whenever the option bits are
  # set — e.g. SST27VF512 has voltages=0x0001, and 0x01 is not a key here.
  # [minipro database.c + tl866a.c, tl866ii_vpp_voltages[]]
  ```
  `build_db.py`'s hash-prefixed line count moved from 191 to 186 (measured with the same one-line Python count both before and after).
- **End-state full 3.11 suite:** `2069 passed` (0 failed), run via `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q -p no:randomly -rf`, after all three tasks.

## Issues Encountered

None beyond the self-corrected comment-line deviation documented above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan `198-02` can proceed: `VCC_VOLTAGES` completion (D-01), the 12 held `0x06` override entries (D-05), and the `vdd < vcc` predicate documentation are untouched by this plan and ready to layer on top.
- `DECODE-NOTES.md` § 9 is open with its decode-provenance subsection; plan `198-03` completes it with the general D-15 finding.
- The database, override file, wire-dict layers and snapshot are all internally consistent and fully green (2069 passed) — no residual red state carries forward.
- gh#66's draft answer (D-17) still needs `198-04` or a later plan to compose and hold it; nothing in this plan blocks that.

---
*Phase: 198-the-two-voltage-nibbles*
*Completed: 2026-09-18*

## Self-Check: PASSED

- All created/modified files confirmed present on disk (`tests/golden/wire_dict_expected_deltas_198.json`, `tests/test_vpp_decode_table.py`, `tools/datasheet_overrides.json`, `tools/build_db.py`, `tools/DECODE-NOTES.md`).
- All three task commit hashes (`961f795`, `873bbb5`, `254c4f7`) and all three meta gitlink-advance hashes (`6af2e3aa`, `c0fcf472`, `6fb90e1f`) confirmed present in `git log --oneline --all`.
- Full 3.11 suite re-confirmed green (2069 passed, 0 failed) after all three tasks landed.
- `git diff --quiet` against the regenerated database confirmed byte-identical after Task 3, and `git status --short` in `firestarter_app` shows no uncommitted tracked changes (only the pre-existing untracked `datasheets/LST62832I.pdf`, not part of this plan).
