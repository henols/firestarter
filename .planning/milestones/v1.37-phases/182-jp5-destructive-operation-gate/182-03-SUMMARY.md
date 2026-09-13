---
phase: 182-jp5-destructive-operation-gate
plan: 03
subsystem: generator
tags: [generated-artefact, diff-gate, golden-delta, regeneration, python]

requires:
  - phase: 182-jp5-destructive-operation-gate (182-02)
    provides: "resolve_pinout_key's 32-pin proto_id==0x08 arm forking on variant_lo, routing 0x03 to DIP32_27C801 — the key this plan's regeneration produces"
provides:
  - "firestarter_app/tools/diff_db.py: RULE_PHASE182_A19_PINOUT root-cause rule (rationale, pinout-only field-path scope, part-number-plus-value-scoped dispatch arm before RC1_DIP32_27C020, priority-docstring line)"
  - "firestarter_app/firestarter/data/chip_database.json: regenerated via build_db.py — 8 rows (AM27C080, AM27LV080, AT27C080, M27C801 x2, MX27C8000, MX27C8000A, UPD27C8001) moved DIP32_STD -> DIP32_27C801, pinout field only"
  - "firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md: regenerated, diff confined to the eight rows' pinout column and its direct downstream effects (per-pinout counts, one variance-defect relocation)"
  - "firestarter_app/tests/golden/wire_dict_expected_deltas_182.json: third field-disjoint delta layer, 8 entries, whole-replacement bus-config objects, programmatically generated"
  - "firestarter_app/tests/test_wire_dict_equivalence.py: _DELTAS_182 constant, renamed composition test with 182 legs, generalised triple field-disjointness, updated 84-record scope-proof baseline, test_the_182_delta_layer_is_capable_of_failing"
affects: []

actuals:
  tokens: 9400
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "diff_db.py root-cause rules land as a coordinated four-place edit (rationale string, field-path scope, dispatch arm, priority docstring line) placed BEFORE the regeneration that would otherwise trip BLOCK: unexplained diff"
    - "Coverage-matrix golden regeneration uses a scratch output + scratch ledger seeded from the committed meta-repo ledger, never writing the meta-repo tracked ledger file directly (precedent: commit 6e4b31a, 148-05)"
    - "A third wire-dict delta layer generalises the existing pair-wise field-disjointness leg to all three pairwise combinations rather than special-casing the new layer"

key-files:
  created:
    - firestarter_app/tests/golden/wire_dict_expected_deltas_182.json
  modified:
    - firestarter_app/tools/diff_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md
    - firestarter_app/tests/test_diff_db_gate.py
    - firestarter_app/tests/test_wire_dict_equivalence.py

key-decisions:
  - "RULE_PHASE182_A19_PINOUT is scoped BOTH by pinout value (DIP32_27C801) AND by a 7-entry part_number frozenset, following the plan's explicit double-scope instruction — a future DIP32_27C801 row that is not one of these eight named parts is a new part, not a Phase 182 relabel, and must escalate to UNEXPLAINED rather than be silently absorbed."
  - "The coverage-matrix golden was regenerated via a scratch output/ledger pair seeded from the committed .planning/v1.3-defect-coverage-ids.json, never writing to that tracked file — same precedent as the 148-05 regeneration (commit 6e4b31a). The committed ledger's own drift relative to the current chip_database.json (it predates several later phases) is pre-existing and out of this plan's scope; the deterministic minting reproduces the same result on any re-run against the same DB state."
  - "The MACRONIX(MXIC) 1048576B coverage-matrix variance finding relocates from DIP32_STD (old DEFECT-COV-77, now zero members) to DIP32_27C801 (new DEFECT-COV-96) as a direct, deterministic consequence of the pinout split. DEFECT-COV-76 (SGS-THOMSON, unrelated) only shifts table position due to the new entry's insertion into the sorted list — same ID, same content."
  - "Deviation: test_diff_db_gate.py's pinned PROV01_PROTECT_METADATA count (682) and test_wire_dict_equivalence.py's 84-record 153-scope-proof baseline both went stale as a direct, mechanical consequence of this regeneration and were updated (see Deviations)."

requirements-completed: [SAFE-01]

coverage:
  - id: D1
    description: "tools/diff_db.py carries RULE_PHASE182_A19_PINOUT (rationale + pinout-only field-path scope + value-and-part-number-scoped dispatch arm before RC1_DIP32_27C020 + priority docstring line); pre-regeneration diff still exits 0"
    requirement: SAFE-01
    verification:
      - kind: unit
        ref: "tests/test_diff_db_gate.py (5 tests, full suite)"
        status: pass
      - kind: other
        ref: "tools/diff_db.py exit=0 pre-regeneration (744 changed chips explained against pinned baseline)"
        status: pass
    human_judgment: false
  - id: D2
    description: "chip_database.json regenerated via build_db.py's documented entry point; diff_db.py exits 0 attributing exactly 8 rows to RULE_PHASE182_A19_PINOUT with zero unexplained; 746 rows/59 manufacturers preserved; wire_dict_baseline.json and chip_database_field_inventory.json byte-unchanged"
    requirement: SAFE-01
    verification:
      - kind: other
        ref: "tools/diff_db.py exit=0 post-regeneration, [RULE_PHASE182_A19_PINOUT] (8 chips), 0 unexplained, 0 new, 0 missing"
        status: pass
      - kind: unit
        ref: "tests/test_chip_database_field_inventory.py, tests/test_audit_coverage_matrix.py, tests/test_diff_db_gate.py (23 tests)"
        status: pass
      - kind: other
        ref: "git diff --stat HEAD -- tests/golden/wire_dict_baseline.json (empty output)"
        status: pass
    human_judgment: false
  - id: D3
    description: "wire_dict_expected_deltas_182.json (8 entries, whole bus-config replacement, 20-element bus with line 21 at index 19, no vpp-pin) generated programmatically; equivalence test extended with 182 legs, triple field-disjointness, and a capability-to-fail sibling; golden byte-unchanged"
    requirement: SAFE-01
    verification:
      - kind: unit
        ref: "tests/test_wire_dict_equivalence.py (8 tests, was 7)"
        status: pass
      - kind: other
        ref: "git diff --stat HEAD -- tests/golden/wire_dict_baseline.json (empty output)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full firestarter_app suite green under Python 3.11 after the regeneration"
    requirement: SAFE-01
    verification:
      - kind: integration
        ref: "pytest tests/ -o addopts=\"\" -q: 2337 passed, 1 pre-existing unrelated warning"
        status: pass
    human_judgment: false

duration: 70min
completed: 2026-09-10
status: complete
---

# Phase 182 Plan 03: chip_database.json Regeneration and the Third Wire-Dict Delta Layer Summary

**`chip_database.json` regenerated from the corrected `resolve_pinout_key` rule (8 rows DIP32_STD -> DIP32_27C801), with `diff_db.py`'s new `RULE_PHASE182_A19_PINOUT` rule proving the diff is exactly those 8 rows, and the resulting `bus-config` change recorded as a third named, counted, provenance-carrying delta layer beside the untouched `wire_dict_baseline.json` golden.**

## Performance

- **Duration:** 70 min
- **Started:** 2026-09-10 (sequential inline session)
- **Completed:** 2026-09-10
- **Tasks:** 3
- **Files modified:** 6 (1 created, 5 modified)

## Accomplishments

- `tools/diff_db.py` carries `RULE_PHASE182_A19_PINOUT` in all four required places (rationale in `_RATIONALES` with a `[VERIFIED: ...a8efaedc236c1d9718bd28299dfbb99536b010ff]` citation, `("pinout",)`-only scope in `_RULE_FIELD_PATHS`, a value-AND-part-number-scoped dispatch arm placed before `RC1_DIP32_27C020`, and a numbered line in the priority-order docstring). Landed BEFORE the regeneration, as the plan required — the pre-regeneration diff still exits 0 (744 changed chips explained against the pinned baseline).
- `chip_database.json` regenerated through `tools/build_db.py`'s documented entry point against the pinned `infoic.xml` commit `a8efaedc236c1d9718bd28299dfbb99536b010ff` — never hand-edited. `tools/diff_db.py` on the regenerated database exits 0, attributing **exactly 8 chips** to `RULE_PHASE182_A19_PINOUT` (`AM27C080`, `AM27LV080`, `AT27C080`, `M27C801` x2 — SGS-THOMSON and ST — `MX27C8000`, `MX27C8000A`, `UPD27C8001`), zero unexplained, zero missing. 746 rows across 59 manufacturers preserved; `DIP32_27C801` count is exactly 8, each 1,048,576 bytes and `support_status=supported`.
- `PROV01_PROTECT_METADATA`'s primary bucket dropped from 682 to exactly 674 (742 → 686 → 682 → 674) because the 8 Phase 182 rows now carry pinout as their primary cause with the three PROV01 fields surfacing as a compound secondary delta — a direct, mechanical consequence of the regeneration, not a defect. `test_diff_db_gate.py`'s pinned assertion was updated to match (Deviation 1).
- `tests/golden/v1.3-COVERAGE-MATRIX.md` regenerated via `tools/audit_coverage_matrix.py`, run against scratch output/ledger paths seeded from the committed meta-repo `.planning/v1.3-defect-coverage-ids.json` (never written to directly — same precedent as commit `6e4b31a`, 148-05). The diff is confined to the eight rows' pinout column and its direct downstream effects: the per-pinout summary counts (`DIP32_27C801` +8, `DIP32_STD` −8), the eight rows' enumeration-table pinout cells, and the MACRONIX(MXIC)/1048576B variance-defect finding relocating from `DIP32_STD` (old `DEFECT-COV-77`, now zero members) to `DIP32_27C801` (new `DEFECT-COV-96`) — `DEFECT-COV-76` (SGS-THOMSON, unrelated) only shifts table position due to the new entry's sorted-list insertion, same ID and content.
- `tests/golden/chip_database_field_inventory.json` verified byte-unchanged — no new generated field was emitted by this phase.
- `tests/golden/wire_dict_expected_deltas_182.json` created: 8 delta entries, each a whole-replacement `bus-config` object (20-element `bus` list, bus line 21 at index 19, no `vpp-pin` key), generated **programmatically** from the live capture (`_capture_wire_dicts`) against the committed golden — never transcribed by hand. Five-key `meta` block (`decision`/`honesty`/`how_to_update`/`phase`/`provenance`) mirrors the 149 layer's structure, citing milestone D-17.
- `tests/test_wire_dict_equivalence.py` extended: `_DELTAS_182` path constant; the composition test renamed to `test_live_capture_matches_golden_plus_the_149_and_153_and_182_deltas` with 182 non-vacuity and exact-count (`== 8`, not "at least") legs added; field-disjointness generalised from a pair to all three pairwise combinations (149×153, 149×182, 153×182 — all confirmed disjoint: 149 touches `page-size`, 153 touches `flags`, 182 touches `bus-config`, and 182 shares zero keys with either other layer); the 84-record 153-scope-proof test's baseline now composes golden+149+182 (Deviation 2); `test_the_182_delta_layer_is_capable_of_failing` added, reusing `_describe_record_diff`. `test_wire_key_union_is_exactly_nine_keys` passes unedited — `vpp-pin` is nested inside `bus-config`, not a top-level wire key. Module: 8 tests passing (was 7).
- Full `firestarter_app` suite green under Python 3.11: **2337 passed**, 1 pre-existing unrelated `DeprecationWarning` (Click `MultiCommand`), 0 failures. `ruff check`/`format --check` and the mypy watermark (35, unchanged) both clean on every file this plan touched.

## Wire-level prediction confirmed against the live capture

The predicted wire-level change (bus line 21 at index 19, `vpp-pin` key dropped entirely) held exactly: all 8 rows' regenerated `bus-config` is byte-identical — `{"bus": [0,1,2,...,16,20,22,21]}` (20 elements, index 19 = `21`), and none carries a `vpp-pin` key. `pin_conversions[32][24]` does resolve to the `ROM_OE` sentinel and `get_bus_config` does drop it, exactly as the plan's flagged prediction stated.

## `support_status` / `programming.*` movement (assumption A4)

Confirmed via `diff_db.py`'s per-chip output: none of the 8 rows show `support_status` movement (all remain `supported`), and the only `programming.*` fields appearing on them are the pre-existing `infoic_page_size_raw`/`protect_off_before`/`protect_on_after` compound-secondary fields from `PROV01_PROTECT_METADATA` — already-explained, database-wide fields, not new movement caused by this rule. Assumption A4 holds.

## Task Commits

Each task was committed atomically inside `firestarter_app` (a separate git repository on `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`), followed by a meta-repo commit advancing the gitlink by name:

1. **Task 1: Add the diff_db root-cause rule** — `fb0b516` (feat) in `firestarter_app`; `82b5c5ed` (chore) in meta.
2. **Task 2: Regenerate chip_database.json and the coverage matrix** — `1267b8c` (feat) in `firestarter_app`; `23b03de3` (chore) in meta.
3. **Task 3: Add the 182 wire-dict delta layer** — `4adf719` (test) in `firestarter_app`; `9659f181` (chore) in meta.

## Files Created/Modified

- `firestarter_app/tools/diff_db.py` — `RULE_PHASE182_A19_PINOUT`: rationale, pinout-only field-path scope, part-number-plus-value-scoped dispatch arm before `RC1_DIP32_27C020`, priority-docstring line.
- `firestarter_app/firestarter/data/chip_database.json` — regenerated; 8 rows' `pinout` field only moved `DIP32_STD` → `DIP32_27C801`.
- `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` — regenerated; diff confined to the eight rows and direct downstream defect-finding relocation.
- `firestarter_app/tests/test_diff_db_gate.py` — pinned `PROV01_PROTECT_METADATA` count corrected to 674; `RULE_PHASE182_A19_PINOUT (8 chips)` assertion added.
- `firestarter_app/tests/golden/wire_dict_expected_deltas_182.json` — new; third delta layer, 8 entries.
- `firestarter_app/tests/test_wire_dict_equivalence.py` — `_DELTAS_182`; renamed composition test with 182 legs; triple field-disjointness; corrected 84-record scope-proof baseline; `test_the_182_delta_layer_is_capable_of_failing`; module docstring updated.

## Decisions Made

See `key-decisions` in frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected `test_diff_db_gate.py`'s stale `PROV01_PROTECT_METADATA` pinned count**
- **Found during:** Task 2 (regenerating `chip_database.json`), running the plan's own `<verification>` full-suite check.
- **Issue:** `tests/test_diff_db_gate.py::test_vcc_margin_rail_bucket_distribution` asserts `[PROV01_PROTECT_METADATA] (682 chips)` in `diff_db.py`'s output. Task 2's own regeneration moves 8 rows off the `PROV01_PROTECT_METADATA` primary bucket (they now carry pinout as primary cause, PROV01 fields as compound secondary), dropping the count to 674 — a direct, mechanical consequence of the authorized DB change, not a bug in the change itself.
- **Fix:** Updated the assertion to `674` and its docstring math to `742 -> 686 -> 682 -> 674`; added a companion `[RULE_PHASE182_A19_PINOUT] (8 chips)` assertion, mirroring the existing `RULE_PHASE66` pattern.
- **Files modified:** `firestarter_app/tests/test_diff_db_gate.py`
- **Verification:** `pytest tests/test_diff_db_gate.py -o addopts="" -q` — 5 passed.
- **Committed in:** `1267b8c` (Task 2 commit)

**2. [Rule 1 - Bug] Corrected `test_exactly_84_records_change_flags_and_no_other_field_moves`'s baseline composition**
- **Found during:** Task 3, running `test_wire_dict_equivalence.py` before adding the 182 layer (pre-fix, to confirm the expected failure shape).
- **Issue:** This Phase-153-scope-proof test composes `golden + deltas_149` as its baseline and compares against the live capture, asserting exactly 84 changed records with only `flags` differing. Once `chip_database.json` carried the 8 Phase 182 `bus-config` changes (Task 2), the same test measured 92 changed records (84 + 8), because the 8 Phase 182 rows were present in `live` but absent from the test's own baseline.
- **Fix:** The baseline now composes `golden + deltas_149 + deltas_182` (182 doesn't touch `flags`, so the 153-scope proof — exactly 84 records, only `flags` moves — is restored exactly).
- **Files modified:** `firestarter_app/tests/test_wire_dict_equivalence.py`
- **Verification:** `pytest tests/test_wire_dict_equivalence.py -o addopts="" -q` — 8 passed.
- **Committed in:** `4adf719` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — pre-existing pinned test expectations went stale as a direct, mechanical consequence of the plan's own authorized database regeneration). **Impact on plan:** Both fixes are required for the full app suite to stay green after this plan's authorized changes; neither introduces scope beyond what the plan's own `<verification>` block (`pytest tests/ ... whole app suite green`) demands. No scope creep.

## Issues Encountered

None beyond the deviations above. One pre-existing, out-of-scope item logged to `.planning/phases/182-jp5-destructive-operation-gate/deferred-items.md`: `ruff check firestarter/ tools/ tests/` reports 8 errors (import-sort / percent-format / import-position) in five files this plan did not touch (`tools/audit_coverage_matrix.py`, `tools/build_devtest_issue_corpus.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`, `tools/snapshot_report_shapes.py`). `ruff check` on every file this plan actually modified exits 0.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `chip_database.json` now reflects the corrected `DIP32_27C801` pinout for the eight 1 MB proto-0x08 chips, with `diff_db.py`, the coverage-matrix golden, and the wire-dict delta layer all proving the change is confined to exactly those eight rows.
- No blockers for the remaining phase plans (182-04 through 182-07 per the roadmap dependency chain; 182-04, 06 and 07 already complete per phase directory).
- The duplicate `M27C801` across SGS-THOMSON and ST is upstream's own manufacturer duplication (RESEARCH.md, 182-02 SUMMARY) — regeneration preserves both rows, confirmed unaffected by this plan.

## Self-Check: PASSED

- `firestarter_app/tests/golden/wire_dict_expected_deltas_182.json` — FOUND on disk.
- Commits `fb0b516`, `1267b8c`, `4adf719` (firestarter_app) and `82b5c5ed`, `23b03de3`, `9659f181` (meta) — all FOUND via `git log --oneline --all`.
- All plan-level `<verification>` commands re-run: `diff_db.py` exit=0 with `RULE_PHASE182_A19_PINOUT (8 chips)`; full `firestarter_app` suite 2337 passed; `ruff check`/`format --check` clean on every file this plan touched; mypy watermark unchanged at 35.
- `tests/golden/wire_dict_baseline.json` confirmed byte-unchanged (`git diff --stat HEAD` empty).

---
*Phase: 182-jp5-destructive-operation-gate*
*Completed: 2026-09-10*
