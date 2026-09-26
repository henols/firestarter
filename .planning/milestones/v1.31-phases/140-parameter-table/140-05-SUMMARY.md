---
phase: 140-parameter-table
plan: 05
subsystem: firmware
tags: [eprom, citations, datasheet-attribution, table-04, pytest, provenance, gh-15]

# Dependency graph
requires:
  - phase: 140-parameter-table (140-01)
    provides: "eprom_params_t table (include/eprom_params.h) + EPROM_PARAM_KEYS/EPROM_PARAMS + eprom_params_for() (src/proms/eprom_params.cpp) -- the live values this sidecar cites and the gate re-parses"
provides:
  - "tests/golden/eprom_params_citations.json: the D-14 machine-readable citation sidecar -- one entry per (row, column) cell, 18 total, every cell attributed to a datasheet or the literal reasoned-basis form"
  - "tests/test_eprom_params_citations.py: the TABLE-04 bijection/drift/well-formedness gate, plus the TABLE-01 field-freeze and TABLE-02 no-pulse-column structural assertions (10 tests)"
  - "Five planted-violation RED transcripts + one GREEN transcript (D-15), captured verbatim in this file"
affects: [140-06-close-record, 140-07-requirements-flip, 144-close-reconciliation, 146-follow-up-candidates]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Committed-inventory gate (S6): sidecar JSON + an independent regex re-parse of the C struct/array, compared for exact bijection and per-cell value drift -- never trusting the sidecar's own derivation"
    - "Env-seam override triple (FIRESTARTER_PARAMS_HEADER/_SOURCE/_CITATIONS) binding at import, used only for planted-violation runs, with two tests (blob-SHA pin, default-target resolution) deliberately immune to it"

key-files:
  created:
    - firestarter/tests/golden/eprom_params_citations.json
    - firestarter/tests/test_eprom_params_citations.py
  modified: []

key-decisions:
  - "Cells whose evidence spans multiple corroborating datasheets record the D-09 representative part as the primary part/document/revision/section, and fold corroborating vendors plus any 'mandatory note' text into an optional `notes` field -- never a fabricated single quote spanning parts it wasn't drawn from"
  - "0x0B's `max_pulses` is the one max_pulses cell shipped as basis=reasoned, not datasheet -- TI TMS 2516 specifies a single 50ms pulse, not a pulse count, so no citation was invented for a number the primary source never states"
  - "The recovery command in meta.datasheets_not_committed uses a generic `datasheets/<slug>/<file>.pdf` placeholder rather than a concrete example path, so the sidecar itself never contains the `datasheets/0x0...` substring the plan's own gate checks for"

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "TABLE-04 bijection: the sidecar's 18 cells are exactly the cross-product of the live 3 row keys and 6 field names -- no missing cell (unattributed value) and no extra cell (citation for a value that doesn't exist)"
    requirement: "TABLE-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_citations_cover_every_cell_exactly_once"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_inventory_is_non_vacuous"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every basis==datasheet cell carries non-empty family/part/document/revision/section/quote, and scope matches the literal D-09 template with the row's real chip count (170/127/32)"
    requirement: "TABLE-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_every_citation_is_well_formed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every basis==reasoned cell's reasoned_from starts with the exact literal 'no datasheet basis — reasoned from ' (em dash, trailing space)"
    requirement: "TABLE-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_every_citation_is_well_formed"
        status: pass
    human_judgment: false
  - id: D4
    description: "A value cannot change without its citation following -- the sidecar's recorded value is compared against the live table's initialiser at the same (row, column), integers as integers and enum identifiers as strings"
    requirement: "TABLE-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_recorded_values_match_the_live_table"
        status: pass
    human_judgment: false
  - id: D5
    description: "TABLE-01: struct field list is exactly the frozen six in order. TABLE-02: no field matches the pulse-width regex, and the only field containing the substring 'pulse' is exactly max_pulses"
    requirement: "TABLE-01, TABLE-02"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_struct_field_names_are_exactly_the_frozen_six_in_order"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_no_pulse_width_column_exists"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_rows_are_exactly_the_three_27c_protocols"
        status: pass
    human_judgment: false
  - id: D6
    description: "The three named divergences (F-140-05 0x07 Intel-family 3xN split candidate, D-06 0x08 PROJECT.md prose-vs-table contradiction, F-140-07 energy_cap_us=50000's wrong published justification) are recorded in meta.named_divergences, not silently smoothed"
    verification:
      - kind: other
        ref: "python3 -c \"import json; g=json.load(open('tests/golden/eprom_params_citations.json')); assert len(g['meta']['named_divergences'])==3\" -- exit 0 (also embedded in Task 1's committed <automated> verify block)"
        status: pass
    human_judgment: false
  - id: D7
    description: "src/proms/eprom.cpp remains byte-unchanged by this plan (D-10) -- this plan ships DATA + GATES + TEST only"
    verification:
      - kind: other
        ref: "git -C firestarter diff --quiet -- src/proms/eprom.cpp (exit 0)"
        status: pass
    human_judgment: false
  - id: D8
    description: "D-15 non-vacuity: the citation gate has been seen RED on five distinct planted violations (missing cell, extra cell, blanked D-09 scope on exactly one cell, drifted value, injected pulse-width column) before its GREEN was believed, with the RED output captured verbatim"
    verification:
      - kind: other
        ref: "Runs A-F below (this file, ## Planted-Violation Runs) -- each RED names the planted defect, not a decode/import/path error; Run C's transcript opens with exactly one PLANTED_CELL= line"
        status: pass
    human_judgment: false
  - id: D9
    description: "meta.evidence_ceiling records the D-02 constraint that verify_mode encodes WHEN to verify and never at what VCC, because the datasheets' raised-VCC verify passes are unreachable on this shield's ~6.25V ceiling"
    verification:
      - kind: other
        ref: "manual inspection of tests/golden/eprom_params_citations.json meta.evidence_ceiling (this SUMMARY quotes it verbatim below)"
        status: pass
    human_judgment: false
  - id: D10
    description: "A stray FIRESTARTER_PARAMS_* env var cannot silently redirect the blob-SHA pin or the default-target resolution: test 1 always names the fixed repo-relative path as the git argument, and test 9 recomputes its targets from _REPO_ROOT/_HERE without consulting the environment"
    requirement: "TABLE-04"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_blob_shas_match_the_recorded_sources"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_eprom_params_citations.py::test_default_targets_resolve_inside_this_repository"
        status: pass
    human_judgment: false

duration: ~32min
completed: 2026-08-10
status: complete
---

# Phase 140 Plan 05: Citation Sidecar + TABLE-04/01/02 Gate Summary

**Machine-readable D-14 citation sidecar for all 18 `eprom_params_t` cells (one datasheet or reasoned-basis attribution each), gate-enforced by a 10-test pytest module that proved itself on five distinct planted violations before its GREEN was trusted.**

## Performance

- **Duration:** ~32 min (approximate -- this executor continued directly from the shared Wave 2 session; first commit `3672b27` at `2026-08-10T02:10:08Z`, plan complete `2026-08-10T02:20Z`)
- **Started:** ~2026-08-10T01:48:00Z (approximate)
- **Completed:** 2026-08-10T02:20:00Z
- **Tasks:** 3 (as planned)
- **Files modified:** 2 (both new, both planned)

## Accomplishments

- Shipped `firestarter/tests/golden/eprom_params_citations.json`: 18 cells (`0x07`/`0x08`/`0x0B` x the six struct columns), each carrying either a full datasheet citation (family, part, document, revision, section, verbatim quote, D-09 scope clause) or the literal `no datasheet basis — reasoned from ` prefix. `meta` records `blob_shas` pinned to the live `include/eprom_params.h` / `src/proms/eprom_params.cpp`, the D-09 scope template, the reasoned prefix, the per-row chip counts (170/127/32), the D-02 evidence-ceiling paragraph, the self-describing datasheet-recovery command (no repo-path citation), and the three named divergences.
- Shipped `firestarter/tests/test_eprom_params_citations.py`: a standalone pytest module (no `conftest.py`, no `scripts/check_*.py` obligations) that independently re-parses `include/eprom_params.h`'s struct field names and `src/proms/eprom_params.cpp`'s `EPROM_PARAM_KEYS[]`/`EPROM_PARAMS[]` tables, then asserts:
  - TABLE-04's bijection (sidecar cells == live cross-product, exactly 18, no duplicates, missing/extra named separately)
  - TABLE-04's drift check (recorded value == live initialiser, per cell)
  - TABLE-04's well-formedness (datasheet cells non-empty + D-09 scope with the right count; reasoned cells carry the literal prefix)
  - TABLE-01's field-name freeze (exactly the frozen six, in order) and row freeze (exactly `0x07`/`0x08`/`0x0B`)
  - TABLE-02's no-pulse-column guarantee, defeating the `max_pulses` substring trap explicitly
  - Non-vacuity (`cells_scanned == 18`, both files exist/non-empty, 6 fields/3 rows live)
  - Env-seam immunity for the blob-SHA pin and default-target resolution
  - The fail-closed `git`-required self-scan
- Proved the gate fails five different ways before trusting its pass (D-15): a missing cell, an extra cell, a blanked D-09 scope clause on **exactly one** cell (verified via the `next()`-based single-cell selector, never the `[:1]`-after-side-effect trap), a drifted value, and an injected pulse-width column -- each RED captured verbatim below, each failing for the *right* named reason, none for a decode/import/path error.
- Confirmed `src/proms/eprom.cpp`, `include/eprom_params.h` and `src/proms/eprom_params.cpp` are all byte-unchanged by this plan (D-10): `git diff --quiet` exits 0 for all three.
- Full firmware suite: 244 passed (234 baseline + 10 new), 0 failed. `tests/test_checker_convention.py` unaffected (7 passed) -- nothing landed under `scripts/` or `tests/fixtures/`.

## Task Commits

Each task was committed atomically inside `firestarter/` (submodule):

1. **Task 1: Author `tests/golden/eprom_params_citations.json`** — `3672b27` (feat, firestarter)
2. **Task 2: Author `tests/test_eprom_params_citations.py`** — `d9bcf53` (test, firestarter)
3. **Task 3: Plant five violations, see RED, capture verbatim, see GREEN** — no additional commit. All six runs (A-F) succeeded on the first attempt against the Task 1/2 artifacts as already committed; no locator or assertion fix was required (D-15 trap 2 did not fire). Task 3's sole deliverable -- the verbatim transcripts -- is recorded in this SUMMARY, which is committed in the meta repo's final metadata commit.

**Plan metadata:** this SUMMARY's own commit (docs: complete plan) — see final commit below.

## Files Created/Modified

- `firestarter/tests/golden/eprom_params_citations.json` (new, 259 lines) — the D-14 sidecar: `meta` (sources, blob_shas, recorded_at_head, requirement, decision, scope_clause_template, reasoned_prefix, row_chip_counts, datasheets_not_committed, why_two_checks, how_to_update, evidence_ceiling, named_divergences) + `cells` (18 entries).
- `firestarter/tests/test_eprom_params_citations.py` (new, 558 lines) — the 10-test TABLE-04/01/02 gate: independent regex re-parsers (`_struct_field_names`, `_row_keys`, `_row_values`, `_live_table`), fail-closed `git` resolution (`_resolve_git`/`_git`), and the ten `test_*` functions.

## Decisions Made

- **Multi-source cells keep one D-09 representative part as primary attribution.** Several cells (e.g. `0x07 overprogram_factor`, `0x08 verify_mode`) are corroborated by two or three vendor datasheets in the plan's own `<citation_content>`. Rather than inventing a single quote spanning parts it wasn't drawn from, each such cell's `part`/`document`/`revision`/`section` name the row's D-09 representative part (Winbond W27C512 / AMD Am27C020 / TI TMS 2516), `quote` carries the most literal verbatim text available (preferring an actual quoted sentence over a flowchart-absence paraphrase where both exist), and corroborating vendors plus any "mandatory note" text land in the optional `notes` field. This keeps every field honestly sourced (critical hazard #8) without narrowing the schema to lose the corroboration the research actually found.
- **`0x0B`'s `max_pulses` ships as `basis: "reasoned"`, the one `max_pulses` cell with no datasheet basis at all.** TI TMS 2516 specifies a single 50ms pulse per location, not a pulse count -- there is nothing in the primary source to cite for a termination-bound number, so the citation says so rather than dressing up the F-140-06 floor-derivation as a datasheet fact.
- **The datasheet-recovery command in `meta.datasheets_not_committed` uses a generic `<slug>` placeholder, never a concrete example path.** The plan's own automated check (`! grep -q 'datasheets/0x0'`) would otherwise be tripped by illustrative examples like `datasheets/0x08-EPROM-QUICK/...` -- the generic form documents the recovery procedure without reintroducing the repo-path citation the sidecar is required to avoid (F-140-08).
- **Task 3 required no code changes.** All six runs (A-F) produced the exact expected RED/GREEN outcomes on the first attempt against the already-committed Task 1/2 artifacts, so nothing in `test_eprom_params_citations.py` needed a locator or assertion fix (D-15 trap 2 never fired).

## Deviations from Plan

None - plan executed exactly as written. (One self-caught authoring mistake during Task 1 -- see Issues Encountered -- was corrected before the first commit and is not a deviation from the plan itself.)

## Issues Encountered

**Self-caught authoring mistake, fixed before the first commit (not a Rule 1-4 deviation -- this was a typo in content being actively authored, caught by the plan's own Task 1 `<automated>` verify block, not a pre-existing bug in the codebase):** the first draft of five `reasoned_from` strings read `"no datasheet basis — reasoned from: ..."` (a stray colon after "from"), which does not `.startswith()` the required literal prefix `"no datasheet basis — reasoned from "` (space, no colon). Task 1's own verification script caught this immediately (`AssertionError: no datasheet basis — reasoned from: no 28-pin datasheet read`) before anything was committed. Fixed by rewording each of the five affected cells (`0x07/overprogram_cap_us`, `0x07/energy_cap_us`, `0x08/overprogram_cap_us`, `0x08/energy_cap_us`, `0x0B/overprogram_cap_us`, `0x0B/max_pulses`) to read naturally without the colon (e.g. "reasoned from a uniform ceiling with..." / "reasoned from no 28-pin datasheet read..."). Re-ran Task 1's verification script clean before committing -- no partial or broken state ever reached git history.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The TABLE-04 sidecar and gate are complete and green; plan 140-06 (per Task list ordering in `140-VALIDATION.md`'s Wave 0) can build on a fully-cited, drift-proof parameter table.
- The three named divergences (F-140-05, D-06, F-140-07) are now on record in a gate-enforced file, not just in planning prose -- Phase 146 / CLOSE-04 has a concrete artifact to reconcile against.
- This plan marks no requirement checkbox Complete, per its own `<requirement_completion_rule>` -- TABLE-01 spans 140-01/140-04/140-05, TABLE-02 spans 140-01/140-05, TABLE-04 spans 140-05/140-06; only plan 140-07 may flip any TABLE-* checkbox in `.planning/REQUIREMENTS.md` or `.planning/ROADMAP.md`.
- No blockers for the remaining Wave 2/3 plans. `src/proms/eprom.cpp`, `include/eprom_params.h` and `src/proms/eprom_params.cpp` are all confirmed byte-unchanged, so Phase 141's baseline (`native_trace_v131`, still GREEN per 140-01/140-04) is undisturbed.

---

## meta.evidence_ceiling (quoted verbatim from the shipped sidecar)

> verify_mode encodes WHEN to verify and never at what VCC. Every datasheet read for this table specifies its final verification pass at a raised VCC for threshold margin (ST M27C512/M27C1001: 1st VCC=6V, 2nd VCC=4.2V; Microchip 27C512A: VCC=VPP=4.5V/5.5V for the Express final check; AMD Am27C020: VCC=VPP=5.25V after programming at 6.25V). The RURP shield has no VCC-raise path -- the ~6.25V program-VCC ceiling this milestone measured is the practical ceiling for this hardware -- so a verify-VCC column could only ever record a value the firmware has no way to act on. D-02 forbids that column outright; this paragraph is the place that constraint is recorded in the same file as the numbers, not only in Phase 146's ledger.

## meta.named_divergences (quoted verbatim from the shipped sidecar)

1. **F-140-05** (`0x07`/`overprogram_factor`): "PROJECT.md's throughput table implies 3 for 0x07, but the shipped value is 0; the 22 Intel-family 1ms parts on this row (Intel 2764 / 2764A / 27128 / 27128A / 27512, TI TMS2764, NEC UPD2764, ST M2764A and the rest of the 1000 microsecond sub-population) genuinely want a 3xN margin pulse, which the 0x07 datasheets cited for the shipped value of 0 do not apply." Phase 146 hand-off: splitting `0x07` is forbidden by TABLE-05 this milestone; recorded as a follow-up candidate.
2. **D-06** (`0x08`/`overprogram_factor`): "PROJECT.md's own throughput table gives 0x08 a 3 x N x pulse overpulse, contradicting PROJECT.md's own prose ('not for Quick-Pulse / Flashrite / PRESTO, so it is gated per row') -- the two halves of the same document disagree with each other." Resolved in favour of the prose and the primary datasheets; Phase 146 / CLOSE-04 reconciles the table text.
3. **F-140-07** (`0x0B`/`energy_cap_us`): "The justification sentence published on gh#15 and carried in PROJECT.md -- that 50ms 'is exactly the classic 2716 total programming time', derived as 100 x 500us -- is factually wrong. The TI TMS 2516 datasheet states its own total programming time for all bits is 100 seconds; 50ms is the per-location pulse width (t_w(PR) TYP), not a total." The value is correct; only the published reason is wrong. Phase 146 / CLOSE-04 reconciles the posted text.

---

## Planted-Violation Runs (D-15)

All six runs below were executed against the real, committed `tests/golden/eprom_params_citations.json` and `tests/test_eprom_params_citations.py` from Tasks 1-2. Every planted mutation lived in a `mktemp -d` scratch directory outside both repositories and was deleted immediately after its run (`rm -rf "$T"`); `include/eprom_params.h`, `src/proms/eprom_params.cpp` and the sidecar were never edited in place.

### Run A — a value with no citation

**Command:**
```bash
cd /workspaces/firestarter && T=$(mktemp -d) && \
python3 -c "import json,sys; g=json.load(open('tests/golden/eprom_params_citations.json')); g['cells']=g['cells'][1:]; json.dump(g, open(sys.argv[1],'w'))" "$T/c.json" && \
FIRESTARTER_PARAMS_CITATIONS="$T/c.json" python3 -m pytest tests/test_eprom_params_citations.py -q
```

**Verbatim stdout:**
```
....F..F..                                                               [100%]
=================================== FAILURES ===================================
_________________ test_citations_cover_every_cell_exactly_once _________________

    def test_citations_cover_every_cell_exactly_once():
        """TABLE-04's bijection: the set of (row, column) in the sidecar's
        cells equals the cross-product of the live row keys and the live field
        names; no duplicates; and len(cells) == 18. Missing cells (a value with
        no citation) and extra cells (a citation for a value that does not
        exist) are named separately in the failure message."""
        _table, field_names, row_keys = _live_table()
        expected = {(row, col) for row in row_keys for col in field_names}
    
        citations = _load_citations()
        cells = citations["cells"]
        seen = [(c["row"], c["column"]) for c in cells]
        seen_set = set(seen)
    
        duplicates = sorted({item for item in seen if seen.count(item) > 1})
        assert not duplicates, f"duplicate (row, column) citations: {duplicates!r}"
    
        missing = sorted(expected - seen_set)
        extra = sorted(seen_set - expected)
>       assert not missing and not extra, (
            "citation coverage is not a bijection.\n"
            f"missing cells (a live value with no citation): {missing!r}\n"
            f"extra cells (a citation for a value that does not exist): {extra!r}"
        )
E       AssertionError: citation coverage is not a bijection.
E         missing cells (a live value with no citation): [('0x07', 'overprogram_cap_us')]
E         extra cells (a citation for a value that does not exist): []
E       assert (not [('0x07', 'overprogram_cap_us')])

tests/test_eprom_params_citations.py:397: AssertionError
________________________ test_inventory_is_non_vacuous _________________________

    def test_inventory_is_non_vacuous():
        """D-15: cells_scanned == 18 and > 0; both source files resolve, exist
        and are non-empty; the live parse returned 6 field names and 3 rows;
        every cell object is non-empty. A zero-scan must never read as a
        pass."""
        for path in (_HEADER_PATH, _SOURCE_PATH, _CITATIONS_PATH):
            assert path.exists(), f"{path} does not exist"
            assert path.stat().st_size > 0, f"{path} exists but is empty"
    
        _table, field_names, row_keys = _live_table()
        assert len(field_names) == 6, (
            "non-vacuous guard: expected exactly 6 live field names, got "
            f"{len(field_names)}: {field_names!r}"
        )
        assert len(row_keys) == 3, (
            "non-vacuous guard: expected exactly 3 live rows, got "
            f"{len(row_keys)}: {row_keys!r}"
        )
    
        citations = _load_citations()
        cells = citations["cells"]
        cells_scanned = len(cells)
>       assert cells_scanned == 18 and cells_scanned > 0, (
            f"non-vacuous guard: cells_scanned={cells_scanned}, expected "
            "exactly 18 and > 0 -- a zero-scan or truncated sidecar must FAIL, "
            "never silently pass."
        )
E       AssertionError: non-vacuous guard: cells_scanned=17, expected exactly 18 and > 0 -- a zero-scan or truncated sidecar must FAIL, never silently pass.
E       assert (17 == 18)

tests/test_eprom_params_citations.py:504: AssertionError
=========================== short test summary info ============================
FAILED tests/test_eprom_params_citations.py::test_citations_cover_every_cell_exactly_once
FAILED tests/test_eprom_params_citations.py::test_inventory_is_non_vacuous - ...
2 failed, 8 passed in 0.08s
```
**Exit code: 1.** Named the missing `(row, column)` exactly (`('0x07', 'overprogram_cap_us')`) and `cells_scanned=17, not 18` -- matches plan expectation exactly.

### Run B — a citation for a value that does not exist

**Command:**
```bash
cd /workspaces/firestarter && T=$(mktemp -d) && \
python3 -c "import json,sys; g=json.load(open('tests/golden/eprom_params_citations.json')); e=dict(g['cells'][0]); e['column']='fallback_pulse_us'; g['cells'].append(e); json.dump(g, open(sys.argv[1],'w'))" "$T/c.json" && \
FIRESTARTER_PARAMS_CITATIONS="$T/c.json" python3 -m pytest tests/test_eprom_params_citations.py -q
```

**Verbatim stdout:**
```
....F.FF..                                                               [100%]
=================================== FAILURES ===================================
_________________ test_citations_cover_every_cell_exactly_once _________________

    def test_citations_cover_every_cell_exactly_once():
        """TABLE-04's bijection: the set of (row, column) in the sidecar's
        cells equals the cross-product of the live row keys and the live field
        names; no duplicates; and len(cells) == 18. Missing cells (a value with
        no citation) and extra cells (a citation for a value that does not
        exist) are named separately in the failure message."""
        _table, field_names, row_keys = _live_table()
        expected = {(row, col) for row in row_keys for col in field_names}
    
        citations = _load_citations()
        cells = citations["cells"]
        seen = [(c["row"], c["column"]) for c in cells]
        seen_set = set(seen)
    
        duplicates = sorted({item for item in seen if seen.count(item) > 1})
        assert not duplicates, f"duplicate (row, column) citations: {duplicates!r}"
    
        missing = sorted(expected - seen_set)
        extra = sorted(seen_set - expected)
>       assert not missing and not extra, (
            "citation coverage is not a bijection.\n"
            f"missing cells (a live value with no citation): {missing!r}\n"
            f"extra cells (a citation for a value that does not exist): {extra!r}"
        )
E       AssertionError: citation coverage is not a bijection.
E         missing cells (a live value with no citation): []
E         extra cells (a citation for a value that does not exist): [('0x07', 'fallback_pulse_us')]
E       assert (not [] and not [('0x07', 'fallback_pulse_us')])

tests/test_eprom_params_citations.py:397: AssertionError
__________________ test_recorded_values_match_the_live_table ___________________

    def test_recorded_values_match_the_live_table():
        """TABLE-04's drift check: for each cell, the recorded value equals the
        live initialiser at that row and column position -- integers compared
        as integers, enum identifiers compared as strings. Reports the first
        mismatch naming row, column, recorded and live value. This is what
        stops a value drifting away from its citation."""
        table, _field_names, _row_keys_live = _live_table()
        citations = _load_citations()
        for cell in citations["cells"]:
            row, col, recorded = cell["row"], cell["column"], cell["value"]
            assert row in table, (
                f"cell ({row}, {col}): row {row!r} does not exist in the live "
                f"table (live rows: {sorted(table)!r})"
            )
>           assert col in table[row], (
                f"cell ({row}, {col}): column {col!r} does not exist in the "
                f"live row (live columns: {sorted(table[row])!r})"
            )
E           AssertionError: cell (0x07, fallback_pulse_us): column 'fallback_pulse_us' does not exist in the live row (live columns: ['energy_cap_us', 'max_pulses', 'overprogram_cap_us', 'overprogram_factor', 'verify_mode', 'vpp_path'])
E           assert 'fallback_pulse_us' in {'overprogram_cap_us': 75000, 'energy_cap_us': 0, 'max_pulses': 25, 'overprogram_factor': 0, ...}

tests/test_eprom_params_citations.py:471: AssertionError
________________________ test_inventory_is_non_vacuous _________________________

    def test_inventory_is_non_vacuous():
        """D-15: cells_scanned == 18 and > 0; both source files resolve, exist
        and are non-empty; the live parse returned 6 field names and 3 rows;
        every cell object is non-empty. A zero-scan must never read as a
        pass."""
        for path in (_HEADER_PATH, _SOURCE_PATH, _CITATIONS_PATH):
            assert path.exists(), f"{path} does not exist"
            assert path.stat().st_size > 0, f"{path} exists but is empty"
    
        _table, field_names, row_keys = _live_table()
        assert len(field_names) == 6, (
            "non-vacuous guard: expected exactly 6 live field names, got "
            f"{len(field_names)}: {field_names!r}"
        )
        assert len(row_keys) == 3, (
            "non-vacuous guard: expected exactly 3 live rows, got "
            f"{len(row_keys)}: {row_keys!r}"
        )
    
        citations = _load_citations()
        cells = citations["cells"]
        cells_scanned = len(cells)
>       assert cells_scanned == 18 and cells_scanned > 0, (
            f"non-vacuous guard: cells_scanned={cells_scanned}, expected "
            "exactly 18 and > 0 -- a zero-scan or truncated sidecar must FAIL, "
            "never silently pass."
        )
E       AssertionError: non-vacuous guard: cells_scanned=19, expected exactly 18 and > 0 -- a zero-scan or truncated sidecar must FAIL, never silently pass.
E       assert (19 == 18)

tests/test_eprom_params_citations.py:504: AssertionError
=========================== short test summary info ============================
FAILED tests/test_eprom_params_citations.py::test_citations_cover_every_cell_exactly_once
FAILED tests/test_eprom_params_citations.py::test_recorded_values_match_the_live_table
FAILED tests/test_eprom_params_citations.py::test_inventory_is_non_vacuous - ...
3 failed, 7 passed in 0.11s
```
**Exit code: 1.** Named the extra cell exactly (`('0x07', 'fallback_pulse_us')`) on test 5, with a correct bonus RED on test 7 (the appended cell's column doesn't exist in the live row either) -- matches plan expectation.

### Run C — a datasheet citation with the D-09 scope clause removed (exactly one cell)

**Command:**
```bash
cd /workspaces/firestarter && T=$(mktemp -d) && \
python3 -c "import json,sys; g=json.load(open('tests/golden/eprom_params_citations.json')); t=next(c for c in g['cells'] if c['basis']=='datasheet'); t['scope']=''; print('PLANTED_CELL=%s/%s' % (t['row'], t['column'])); json.dump(g, open(sys.argv[1],'w'))" "$T/c.json" && \
FIRESTARTER_PARAMS_CITATIONS="$T/c.json" python3 -m pytest tests/test_eprom_params_citations.py -q
```

**Verbatim stdout:**
```
PLANTED_CELL=0x07/max_pulses
.....F....                                                               [100%]
=================================== FAILURES ===================================
______________________ test_every_citation_is_well_formed ______________________

    def test_every_citation_is_well_formed():
        """TABLE-04: for basis == 'datasheet', family/part/document/revision/
        section/quote/scope all non-empty, and scope matches the D-09 template
        with the row's real chip count. For basis == 'reasoned', reasoned_from
        starts with meta.reasoned_prefix, and that prefix is itself asserted to
        be the literal 'no datasheet basis — reasoned from '. Any other basis
        value fails."""
        citations = _load_citations()
        meta = citations["meta"]
        prefix = meta["reasoned_prefix"]
        assert prefix == "no datasheet basis — reasoned from ", (
            "meta.reasoned_prefix must be the exact literal "
            f"'no datasheet basis — reasoned from ' (em dash, trailing "
            f"space), found {prefix!r}"
        )
        counts = meta["row_chip_counts"]
        scope_re = re.compile(
            r"^representative of this row; not asserted true of all (\d+) "
            r"chips carrying this protocol_id\.$"
        )
        for cell in citations["cells"]:
            row, col, basis = cell["row"], cell["column"], cell.get("basis")
            if basis == "datasheet":
                for key in ("family", "part", "document", "revision", "section", "quote", "scope"):
>                   assert cell.get(key), (
                        f"cell ({row}, {col}): datasheet citation missing or "
                        f"empty required field {key!r}"
                    )
E                   AssertionError: cell (0x07, max_pulses): datasheet citation missing or empty required field 'scope'
E                   assert ''
E                    +  where '' = <built-in method get of dict object at 0x7f5e10a5fa00>('scope')
E                    +    where <built-in method get of dict object at 0x7f5e10a5fa00> = {'row': '0x07', 'column': 'max_pulses', 'value': 25, 'basis': 'datasheet', ...}.get

tests/test_eprom_params_citations.py:429: AssertionError
=========================== short test summary info ============================
FAILED tests/test_eprom_params_citations.py::test_every_citation_is_well_formed
1 failed, 9 passed in 0.09s
```
**Exit code: 1.** Transcript opens with exactly one `PLANTED_CELL=0x07/max_pulses` line, and the RED names that one cell (`(0x07, max_pulses)`) and no other -- confirms the `next()`-based single-cell selector was used, never the `[:1]`-after-side-effect trap that would have blanked all 12 datasheet cells.

### Run D — a value that drifted from its citation

**Command:**
```bash
cd /workspaces/firestarter && T=$(mktemp -d) && \
python3 -c "import json,sys; g=json.load(open('tests/golden/eprom_params_citations.json')); [c.update(value=100) for c in g['cells'] if c['row']=='0x0B' and c['column']=='max_pulses']; json.dump(g, open(sys.argv[1],'w'))" "$T/c.json" && \
FIRESTARTER_PARAMS_CITATIONS="$T/c.json" python3 -m pytest tests/test_eprom_params_citations.py -q
```

**Verbatim stdout:**
```
......F...                                                               [100%]
=================================== FAILURES ===================================
__________________ test_recorded_values_match_the_live_table ___________________

    def test_recorded_values_match_the_live_table():
        """TABLE-04's drift check: for each cell, the recorded value equals the
        live initialiser at that row and column position -- integers compared
        as integers, enum identifiers compared as strings. Reports the first
        mismatch naming row, column, recorded and live value. This is what
        stops a value drifting away from its citation."""
        table, _field_names, _row_keys_live = _live_table()
        citations = _load_citations()
        for cell in citations["cells"]:
            row, col, recorded = cell["row"], cell["column"], cell["value"]
            assert row in table, (
                f"cell ({row}, {col}): row {row!r} does not exist in the live "
                f"table (live rows: {sorted(table)!r})"
            )
            assert col in table[row], (
                f"cell ({row}, {col}): column {col!r} does not exist in the "
                f"live row (live columns: {sorted(table[row])!r})"
            )
            live_value = table[row][col]
>           assert recorded == live_value, (
                "value drifted from its citation -- "
                f"row={row} column={col} recorded={recorded!r} live={live_value!r}"
            )
E           AssertionError: value drifted from its citation -- row=0x0B column=max_pulses recorded=100 live=255
E           assert 100 == 255

tests/test_eprom_params_citations.py:476: AssertionError
=========================== short test summary info ============================
FAILED tests/test_eprom_params_citations.py::test_recorded_values_match_the_live_table
1 failed, 9 passed in 0.08s
```
**Exit code: 1.** Names row (`0x0B`), column (`max_pulses`), recorded (`100`) and live (`255`) exactly -- matches plan expectation.

### Run E — a pulse-width column added to the header

**Command:**
```bash
cd /workspaces/firestarter && T=$(mktemp -d) && \
sed 's/^\( *\)uint8_t  *vpp_path;/\1uint32_t fallback_pulse_us;\n\1uint8_t vpp_path;/' include/eprom_params.h > "$T/eprom_params.h" && \
FIRESTARTER_PARAMS_HEADER="$T/eprom_params.h" python3 -m pytest tests/test_eprom_params_citations.py -q
```

**Planted diff** (scratch copy vs. the real, untouched header):
```diff
57c57,58
<     uint8_t  vpp_path;            /* VPP_PATH_DROP_RESISTOR / VPP_PATH_DIRECT_VPE */
---
>     uint32_t fallback_pulse_us;
>     uint8_t vpp_path;            /* VPP_PATH_DROP_RESISTOR / VPP_PATH_DIRECT_VPE */
```

**Verbatim stdout:**
```
.FF.F.FF..                                                               [100%]
=================================== FAILURES ===================================
_________ test_struct_field_names_are_exactly_the_frozen_six_in_order __________

    def test_struct_field_names_are_exactly_the_frozen_six_in_order():
        """TABLE-01: the live struct's ordered field-name list equals the
        frozen six, in order. Reports the first divergence by index rather
        than a bare 'lists differ'."""
        live = _struct_field_names(_HEADER_PATH.read_text())
        n = min(len(live), len(_FROZEN_FIELD_NAMES))
        for i in range(n):
>           assert live[i] == _FROZEN_FIELD_NAMES[i], (
                f"first divergence at field index {i} -- "
                f"expected={_FROZEN_FIELD_NAMES[i]!r} live={live[i]!r} "
                f"(expected={_FROZEN_FIELD_NAMES!r}, live={live!r})"
            )
E           AssertionError: first divergence at field index 5 -- expected='vpp_path' live='fallback_pulse_us' (expected=['overprogram_cap_us', 'energy_cap_us', 'max_pulses', 'overprogram_factor', 'verify_mode', 'vpp_path'], live=['overprogram_cap_us', 'energy_cap_us', 'max_pulses', 'overprogram_factor', 'verify_mode', 'fallback_pulse_us', 'vpp_path'])
E           assert 'fallback_pulse_us' == 'vpp_path'
E             
E             - vpp_path
E             + fallback_pulse_us

tests/test_eprom_params_citations.py:319: AssertionError
______________________ test_no_pulse_width_column_exists _______________________

    def test_no_pulse_width_column_exists():
        """TABLE-02. Two independent assertions, because a naive 'no field name
        contains pulse' substring test is fooled by the legitimate field
        max_pulses -- that is the trap this test exists to catch:
          (a) no field name matches (?i)(pulse_(width|delay|us)|fallback_pulse)
          (b) the ONLY field name containing the substring 'pulse' is exactly
              max_pulses
        """
        live = _struct_field_names(_HEADER_PATH.read_text())
        for name in live:
>           assert not _PULSE_WIDTH_RE.search(name), (
                f"field {name!r} matches the pulse-width pattern "
                f"{_PULSE_WIDTH_RE.pattern!r} -- TABLE-02 forbids any "
                "pulse-width column in this table; pulse width stays "
                "handle->pulse_delay."
            )
E           AssertionError: field 'fallback_pulse_us' matches the pulse-width pattern '(?i)(pulse_(width|delay|us)|fallback_pulse)' -- TABLE-02 forbids any pulse-width column in this table; pulse width stays handle->pulse_delay.
E           assert not <re.Match object; span=(0, 14), match='fallback_pulse'>
E            +  where <re.Match object; span=(0, 14), match='fallback_pulse'> = <built-in method search of re.Pattern object at 0x55f5b3efec60>('fallback_pulse_us')
E            +    where <built-in method search of re.Pattern object at 0x55f5b3efec60> = re.compile('(?i)(pulse_(width|delay|us)|fallback_pulse)', re.IGNORECASE).search

tests/test_eprom_params_citations.py:341: AssertionError
_________________ test_citations_cover_every_cell_exactly_once _________________

    def test_citations_cover_every_cell_exactly_once():
        """TABLE-04's bijection: the set of (row, column) in the sidecar's
        cells equals the cross-product of the live row keys and the live field
        names; no duplicates; and len(cells) == 18. Missing cells (a value with
        no citation) and extra cells (a citation for a value that does not
        exist) are named separately in the failure message."""
>       _table, field_names, row_keys = _live_table()
                                        ^^^^^^^^^^^^^

tests/test_eprom_params_citations.py:384: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def _live_table():
        """Build {row_key: {field_name: value}} from a live, independent
        re-parse of the header and source -- never trusting the sidecar's own
        recorded values. Returns (table, field_names, row_keys)."""
        header_text = _HEADER_PATH.read_text()
        source_text = _SOURCE_PATH.read_text()
        field_names = _struct_field_names(header_text)
        row_keys = _row_keys(source_text)
        row_values = _row_values(source_text)
        assert len(row_keys) == len(row_values), (
            f"EPROM_PARAM_KEYS has {len(row_keys)} entries but EPROM_PARAMS has "
            f"{len(row_values)} rows -- the two arrays are supposed to be "
            "positionally parallel."
        )
        table = {}
        for key, values in zip(row_keys, row_values):
>           assert len(values) == len(field_names), (
                f"row {key} has {len(values)} initialiser tokens but the "
                f"struct has {len(field_names)} fields: {field_names!r} "
                f"(row tokens: {values!r})"
            )
E           AssertionError: row 0x07 has 6 initialiser tokens but the struct has 7 fields: ['overprogram_cap_us', 'energy_cap_us', 'max_pulses', 'overprogram_factor', 'verify_mode', 'fallback_pulse_us', 'vpp_path'] (row tokens: [75000, 0, 25, 0, 'VERIFY_PER_PULSE_PLUS_FINAL', 'VPP_PATH_DROP_RESISTOR'])
E           assert 6 == 7
E            +  where 6 = len([75000, 0, 25, 0, 'VERIFY_PER_PULSE_PLUS_FINAL', 'VPP_PATH_DROP_RESISTOR'])
E            +  and   7 = len(['overprogram_cap_us', 'energy_cap_us', 'max_pulses', 'overprogram_factor', 'verify_mode', 'fallback_pulse_us', ...])

tests/test_eprom_params_citations.py:243: AssertionError
__________________ test_recorded_values_match_the_live_table ___________________

    def test_recorded_values_match_the_live_table():
        """TABLE-04's drift check: for each cell, the recorded value equals the
        live initialiser at that row and column position -- integers compared
        as integers, enum identifiers compared as strings. Reports the first
        mismatch naming row, column, recorded and live value. This is what
        stops a value drifting away from its citation."""
>       table, _field_names, _row_keys_live = _live_table()
                                              ^^^^^^^^^^^^^

tests/test_eprom_params_citations.py:463: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def _live_table():
        """Build {row_key: {field_name: value}} from a live, independent
        re-parse of the header and source -- never trusting the sidecar's own
        recorded values. Returns (table, field_names, row_keys)."""
        header_text = _HEADER_PATH.read_text()
        source_text = _SOURCE_PATH.read_text()
        field_names = _struct_field_names(header_text)
        row_keys = _row_keys(source_text)
        row_values = _row_values(source_text)
        assert len(row_keys) == len(row_values), (
            f"EPROM_PARAM_KEYS has {len(row_keys)} entries but EPROM_PARAMS has "
            f"{len(row_values)} rows -- the two arrays are supposed to be "
            "positionally parallel."
        )
        table = {}
        for key, values in zip(row_keys, row_values):
>           assert len(values) == len(field_names), (
                f"row {key} has {len(values)} initialiser tokens but the "
                f"struct has {len(field_names)} fields: {field_names!r} "
                f"(row tokens: {values!r})"
            )
E           AssertionError: row 0x07 has 6 initialiser tokens but the struct has 7 fields: ['overprogram_cap_us', 'energy_cap_us', 'max_pulses', 'overprogram_factor', 'verify_mode', 'fallback_pulse_us', 'vpp_path'] (row tokens: [75000, 0, 25, 0, 'VERIFY_PER_PULSE_PLUS_FINAL', 'VPP_PATH_DROP_RESISTOR'])
E           assert 6 == 7
E            +  where 6 = len([75000, 0, 25, 0, 'VERIFY_PER_PULSE_PLUS_FINAL', 'VPP_PATH_DROP_RESISTOR'])
E            +  and   7 = len(['overprogram_cap_us', 'energy_cap_us', 'max_pulses', 'overprogram_factor', 'verify_mode', 'fallback_pulse_us', ...])

tests/test_eprom_params_citations.py:243: AssertionError
________________________ test_inventory_is_non_vacuous _________________________

    def test_inventory_is_non_vacuous():
        """D-15: cells_scanned == 18 and > 0; both source files resolve, exist
        and are non-empty; the live parse returned 6 field names and 3 rows;
        every cell object is non-empty. A zero-scan must never read as a
        pass."""
        for path in (_HEADER_PATH, _SOURCE_PATH, _CITATIONS_PATH):
            assert path.exists(), f"{path} does not exist"
            assert path.stat().st_size > 0, f"{path} exists but is empty"
    
>       _table, field_names, row_keys = _live_table()
                                        ^^^^^^^^^^^^^

tests/test_eprom_params_citations.py:491: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def _live_table():
        """Build {row_key: {field_name: value}} from a live, independent
        re-parse of the header and source -- never trusting the sidecar's own
        recorded values. Returns (table, field_names, row_keys)."""
        header_text = _HEADER_PATH.read_text()
        source_text = _SOURCE_PATH.read_text()
        field_names = _struct_field_names(header_text)
        row_keys = _row_keys(source_text)
        row_values = _row_values(source_text)
        assert len(row_keys) == len(row_values), (
            f"EPROM_PARAM_KEYS has {len(row_keys)} entries but EPROM_PARAMS has "
            f"{len(row_values)} rows -- the two arrays are supposed to be "
            "positionally parallel."
        )
        table = {}
        for key, values in zip(row_keys, row_values):
>           assert len(values) == len(field_names), (
                f"row {key} has {len(values)} initialiser tokens but the "
                f"struct has {len(field_names)} fields: {field_names!r} "
                f"(row tokens: {values!r})"
            )
E           AssertionError: row 0x07 has 6 initialiser tokens but the struct has 7 fields: ['overprogram_cap_us', 'energy_cap_us', 'max_pulses', 'overprogram_factor', 'verify_mode', 'fallback_pulse_us', 'vpp_path'] (row tokens: [75000, 0, 25, 0, 'VERIFY_PER_PULSE_PLUS_FINAL', 'VPP_PATH_DROP_RESISTOR'])
E           assert 6 == 7
E            +  where 6 = len([75000, 0, 25, 0, 'VERIFY_PER_PULSE_PLUS_FINAL', 'VPP_PATH_DROP_RESISTOR'])
E            +  and   7 = len(['overprogram_cap_us', 'energy_cap_us', 'max_pulses', 'overprogram_factor', 'verify_mode', 'fallback_pulse_us', ...])

tests/test_eprom_params_citations.py:243: AssertionError
=========================== short test summary info ============================
FAILED tests/test_eprom_params_citations.py::test_struct_field_names_are_exactly_the_frozen_six_in_order
FAILED tests/test_eprom_params_citations.py::test_no_pulse_width_column_exists
FAILED tests/test_eprom_params_citations.py::test_citations_cover_every_cell_exactly_once
FAILED tests/test_eprom_params_citations.py::test_recorded_values_match_the_live_table
FAILED tests/test_eprom_params_citations.py::test_inventory_is_non_vacuous - ...
5 failed, 5 passed in 0.11s
```
**Exit code: 1.** Fails on both test 2 (`test_struct_field_names_are_exactly_the_frozen_six_in_order`, first divergence at index 5) and test 3 (`test_no_pulse_width_column_exists`, `fallback_pulse_us` matches the pulse-width pattern) as required, with three additional correctly-diagnosed knock-on failures (tests 5/7/8, all via the same `_live_table()` field/token-count mismatch) -- none of the five is a decode/import/path error.

### Run F — the real tree, no env seams set

**Command:**
```bash
cd /workspaces/firestarter && python3 -m pytest tests/test_eprom_params_citations.py -q
```

**Verbatim stdout:**
```
..........                                                               [100%]
10 passed in 0.05s
```

**Sources-unchanged check:**
```bash
git diff --quiet -- include/eprom_params.h src/proms/eprom_params.cpp && echo "RUN_F_GREEN_AND_SOURCES_UNCHANGED"
```
```
RUN_F_GREEN_AND_SOURCES_UNCHANGED
```
**Exit code: 0.** All 10 tests pass on the real, unmodified tree.

### Final tree-cleanliness check (post Task 1+2 commits)

```bash
git status --porcelain            # (empty -- both files already committed atomically)
git diff --quiet -- include/eprom_params.h src/proms/eprom_params.cpp tests/golden/eprom_params_citations.json && echo "DIFF_QUIET_OK exit=0"
```
```
DIFF_QUIET_OK exit=0
```

---

*Phase: 140-parameter-table*
*Completed: 2026-08-10*

## Self-Check: PASSED

Files verified present on disk:
- FOUND: `firestarter/tests/golden/eprom_params_citations.json`
- FOUND: `firestarter/tests/test_eprom_params_citations.py`
- FOUND: `.planning/phases/140-parameter-table/140-05-SUMMARY.md`

Commits verified present in git history (firestarter):
- FOUND: `3672b27` (feat: citation sidecar)
- FOUND: `d9bcf53` (test: TABLE-04/01/02 gate)
