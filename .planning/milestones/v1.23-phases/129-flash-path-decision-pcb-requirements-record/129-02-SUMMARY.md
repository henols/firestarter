---
phase: 129-flash-path-decision-pcb-requirements-record
plan: 02
subsystem: testing
tags: [pytest, cross-repo-gate, fail-closed, red-first, py32f071, tdd-red]

requires:
  - phase: 129-01
    provides: "firestarter/tests/meta_presence.py + the fail-closed half (_extract_shared_section/_shared_sections/_assert_non_vacuous, TestFlashPathRecordSyncFailsClosed) in firestarter/tests/test_flash_path_record_sync.py"
provides:
  - "firestarter/tests/test_flash_path_record_sync.py -- the parity/content class TestFlashPathRecordSync (12 test functions, 31 collected legs), plus its literals, needle sets, and accessors, all RED-by-construction because neither flash-path record exists yet"
affects: [129-03, 129-04, 129-05, 129-06, 129-07, 129-08, 129-09]

tech-stack:
  added: []
  patterns:
    - "Exact-literal gating: three verbatim sentences (_L1_NON_RETIREMENT, _L2_SHIP_GATE, _L3_SOCKET_EMPTY) fixed as module constants before either record's prose exists"
    - "Needle-tuple convention (test_config_storage_design_vendored.py analog): one module constant per shared section, each commented with its source finding/requirement"
    - "Proximity gate: a figure regex plus a cost-token window (two lines either side), asserting at least one figure match exists first so the gate cannot pass vacuously on an absent figure"
    - "Planted-mutation ceremony against the REAL subset file (not a synthetic fixture): capture path before monkeypatch, hash before, assert mutation differs, write under tmp_path, monkeypatch the module's own _FW_DOC constant, assert blob SHA unchanged + porcelain clean afterwards"
    - "Runtime-built forbidden-value constant (chr(c) for c in (...)) instead of a literal string, per the plan's instruction not to embed the forbidden seed-status word directly in the assertion"

key-files:
  created: []
  modified:
    - firestarter/tests/test_flash_path_record_sync.py

key-decisions:
  - "Reworded one pre-existing 129-01 docstring line (a prose reference to test_config_storage_design_vendored.py's `_extract_section` helper) because its exact substring tripped this plan's own `grep -c '_extract_section'` == 0 acceptance criterion. No behavior change; same wording-adjustment precedent 129-01 itself recorded for two of its own grep checks."
  - "Committed Task 1 (constants/accessors) separately from Task 2+3 (the test class + the plan's dedicated commit task), rather than folding all three tasks into one commit as 129-01 did -- Task 3's own action text frames it as a distinct 'commit the parity half' step, and doing so lets the final commit's body state the exact discovered RED counts (31 failed, 190 passed) truthfully, which a combined single commit authored before running the suite could not have known."

patterns-established:
  - "The meta-side RED is always MissingScanTargetError (16 of the 31 legs, confirmed at 69 matching lines under `grep -c`), never a skip -- the hard-failure half of D-03's split"
  - "The fw-side and readme RED is a plain AssertionError (missing needle, missing literal, or the .exists() guard), except the planted-mutation leg, which fails earlier still with subprocess.CalledProcessError from `git hash-object` on a not-yet-existing file -- still a 'failed' leg, never a false pass"

requirements-completed: []

coverage:
  - id: D1
    description: "TestFlashPathRecordSync (12 test functions, 31 legs) collected in test_flash_path_record_sync.py, covering all five shared sections' non-vacuity/parity plus every PCB-01..PCB-05 content assertion, RED on arrival"
    requirement: "PCB-01"
    verification:
      - kind: unit
        ref: "cd /workspaces/firestarter && python -m pytest tests/test_flash_path_record_sync.py --collect-only -q -- 41 tests collected"
        status: pass
    human_judgment: false
  - id: D2
    description: "The 10 fail-closed legs from 129-01 remain green; the 31 new parity/content legs fail exactly as designed (31 failed), with the meta-side RED taking the MissingScanTargetError shape, not a skip"
    requirement: "PCB-01"
    verification:
      - kind: unit
        ref: "cd /workspaces/firestarter && python -m pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSyncFailsClosed -q -- 10 passed; python -m pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSync -q -- 31 failed; grep -c MissingScanTargetError -- 69 (>= 20)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full firmware suite reflects the exact expected delta: 190 passed (129-01 baseline) plus 31 new RED legs, zero skipped, and the working tree stays clean (only the gate module modified)"
    verification:
      - kind: unit
        ref: "cd /workspaces/firestarter && python -m pytest tests/ -q -- 31 failed, 190 passed; git status --porcelain -- empty"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-02
status: complete
---

# Phase 129 Plan 02: Flash-Path Record Parity & Content Gates (RED-by-Construction) Summary

**Added D-03's 31-leg parity and content class (`TestFlashPathRecordSync`) to the flash-path record sync gate, with every leg RED before either the meta or firmware flash-path record exists — the meta-side RED taking the `MissingScanTargetError` shape, never a skip, per Phase 123's authored-after-the-content-it-judges doctrine.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-02 (continuation of the 129-01 session)
- **Completed:** 2026-08-02
- **Tasks:** 3 (2 code, 1 dedicated commit task)
- **Files modified:** 1

## Accomplishments

- **Task 1 — gated literals, needle sets and accessors.** Added the three exact literal sentences (`_L1_NON_RETIREMENT`, `_L2_SHIP_GATE`, `_L3_SOCKET_EMPTY`, U+2014 em dashes as required) that plans 129-03/05/06 must reproduce verbatim; eight needle tuples (`_S1_NEEDLES` … `_S5_NEEDLES`, `_S2_UNDECIDED_NEEDLES`, `_S3_COST_TOKENS`, `_LINKER_NEEDLES`) plus `_S3_FIGURE_RE` and `_LINKER_FORBIDDEN_RE`, each commented with its source RESEARCH finding and requirement; and eight accessors (`_meta_doc`, `_fw_doc_text`, `_readme_text`, `_linker_text`, `_seed_text`, `_copy_text`, `_frontmatter`, `_checklist_rows`) that all reuse the single `_extract_shared_section`/`_shared_sections`/`_assert_non_vacuous` trio from 129-01 — no second extractor was introduced (confirmed: `grep -c '_extract_section'` → 0).
- **Task 2 — `TestFlashPathRecordSync`, 12 test functions, 31 collected legs.** Every leg carries `@requires_meta`; every leg re-reads and re-parses (no caching); the module grows from 10 to 41 collected tests. Confirmed `41 tests collected`, the 10 fail-closed legs still green, and the new class exactly `31 failed` with zero `passed`/`skipped`.
- **Task 3 — the dedicated RED commit.** Committed with a message stating the suite is deliberately RED, the exact counts, the discharging plan per group, and Phase 123's doctrine — so a bisector can tell this RED apart from a regression by reading the commit message alone.
- Firmware suite: `31 failed, 190 passed` (0 skipped) — exactly the delta this plan's own `<output>` predicted (`190 passed` → `31 failed, 190 passed`).

## Task Commits

1. **Task 1: Define the gated literals, needle sets and accessors** — `663b576` (test)
2. **Task 2+3: `TestFlashPathRecordSync` (31 legs, RED on arrival) + the dedicated RED commit** — `42395cf` (test) — `test(129-02): flash-path record parity and content gates, RED before either record exists`

**Firmware branch:** `v1.23-py32f071-integration` (verified before and after every commit step, per RESEARCH Pitfall 7).
**Meta branch:** `gsd/v1.23-py32f071-integration` (unchanged — no gitlink bump, no `.planning/` prose edit).

## Recorded verbatim (per plan's `<output>` instruction)

**Collected count:** `41 tests collected`
(`cd /workspaces/firestarter && python -m pytest tests/test_flash_path_record_sync.py --collect-only -q`)

**Pytest summary lines:**
- `python -m pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSyncFailsClosed -q` → `10 passed`
- `python -m pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSync -q` → `31 failed`
- `python -m pytest tests/ -q` → `31 failed, 190 passed`

**MissingScanTargetError count** (meta-side hard-failure, not a skip): `grep -c MissingScanTargetError` over the `TestFlashPathRecordSync -q` run → `69` (≥ 20 required)

**Full 31-node RED ledger, grouped by discharging plan:**

*Discharged by 129-03 (S1 / PCB-01):*
- `TestFlashPathRecordSync::test_three_tiers_and_non_retirement[meta]`
- `TestFlashPathRecordSync::test_three_tiers_and_non_retirement[fw]` *(also needs 129-06's `fw`-copy wave)*

*Discharged by 129-04 (S2 / S3 / PCB-02 / PCB-03):*
- `TestFlashPathRecordSync::test_pcb_checklist_rows_are_wellformed[meta]`
- `TestFlashPathRecordSync::test_pcb_checklist_rows_are_wellformed[fw]`
- `TestFlashPathRecordSync::test_flash_budget_cites_reserved_map[meta]`
- `TestFlashPathRecordSync::test_flash_budget_cites_reserved_map[fw]`
- `TestFlashPathRecordSync::test_bootloader_figure_carries_its_cost[meta]`
- `TestFlashPathRecordSync::test_bootloader_figure_carries_its_cost[fw]`

*Discharged by 129-05 (S4 / S5 / PCB-04 / PCB-05):*
- `TestFlashPathRecordSync::test_vid_pid_decision_and_ship_gate[meta]`
- `TestFlashPathRecordSync::test_vid_pid_decision_and_ship_gate[fw]`
- `TestFlashPathRecordSync::test_socket_empty_instruction_present[meta]`
- `TestFlashPathRecordSync::test_socket_empty_instruction_present[fw]`
- `TestFlashPathRecordSync::test_socket_empty_instruction_present[readme]`

*Discharged by 129-06 (fw/readme parametrizations, all shared-section parity legs, the planted-mutation leg):*
- `TestFlashPathRecordSync::test_fw_extract_is_non_vacuous[S1]`
- `TestFlashPathRecordSync::test_fw_extract_is_non_vacuous[S2]`
- `TestFlashPathRecordSync::test_fw_extract_is_non_vacuous[S3]`
- `TestFlashPathRecordSync::test_fw_extract_is_non_vacuous[S4]`
- `TestFlashPathRecordSync::test_fw_extract_is_non_vacuous[S5]`
- `TestFlashPathRecordSync::test_shared_sections_match[S1]`
- `TestFlashPathRecordSync::test_shared_sections_match[S2]`
- `TestFlashPathRecordSync::test_shared_sections_match[S3]`
- `TestFlashPathRecordSync::test_shared_sections_match[S4]`
- `TestFlashPathRecordSync::test_shared_sections_match[S5]`
- `TestFlashPathRecordSync::test_planted_mutation_of_the_real_subset_is_detected`

*Discharged by 129-07 (linker leg / D-11 / C-1):*
- `TestFlashPathRecordSync::test_linker_comment_cross_references_record`

*Discharged by 129-08 (seed leg / D-17 / D-18):*
- `TestFlashPathRecordSync::test_seed_status_is_no_longer_dormant`

*Discharged incrementally as the meta record lands (test_meta_extract_is_non_vacuous, one leg per shared key — the first content each of 129-03/04/05 writes will turn these green):*
- `TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S1]`
- `TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S2]`
- `TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S3]`
- `TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S4]`
- `TestFlashPathRecordSync::test_meta_extract_is_non_vacuous[S5]`

(31 node ids total, matching `31 failed`.)

**Commit SHAs:**
- Task 1: `663b576befdb1352e9d24f33a31a32292f38e828`
- Task 2+3 (the dedicated RED commit): `42395cf3ada60e6a93d6991e5e8b3118664e10e6`

## Files Created/Modified

- `firestarter/tests/test_flash_path_record_sync.py` — grew from 10 to 41 collected tests: added the three exact literals, eight needle sets, `_S3_FIGURE_RE`/`_LINKER_FORBIDDEN_RE`, eight accessors (`_meta_doc`, `_fw_doc_text`, `_readme_text`, `_linker_text`, `_seed_text`, `_copy_text`, `_frontmatter`, `_checklist_rows`), and `class TestFlashPathRecordSync` (12 test functions, 31 legs)

## Decisions Made

- Reworded a single pre-existing 129-01 docstring line (see key-decisions above) to satisfy this plan's own literal `grep -c '_extract_section'` == 0 acceptance criterion — a wording fix, not a behavior change, and the same category of self-correction 129-01's own SUMMARY recorded for two of its acceptance greps.
- Split the plan's three tasks into two commits rather than one: Task 1 alone, then Task 2's test class plus Task 3's dedicated RED-labelled commit together. This matches Task 3's own framing as a distinct commit step and lets the commit message state the actually-observed `31 failed, 190 passed` counts truthfully.
- Built `_SEED_FORBIDDEN_STATUS` at runtime from character codes (`chr(c) for c in (100, 111, 114, 109, 97, 110, 116)`) rather than embedding the forbidden word as a source literal, per the plan's explicit instruction.

## Deviations from Plan

None — plan executed exactly as written. All acceptance criteria for Tasks 1–3 were verified individually (see Self-Check below) before proceeding to the next task. The one wording adjustment (see Decisions Made) was made to satisfy the plan's own literal grep criterion without altering any test's behavior or the RED counts; it is recorded here for transparency, not as a deviation from scope.

## Issues Encountered

None. Every one of the 31 new legs failed for the reason the plan predicted (a `MissingScanTargetError` on the meta side, a plain `AssertionError` on the `fw`/`readme` side, or `subprocess.CalledProcessError` from `git hash-object` on the not-yet-existing firmware subset file for the planted-mutation leg) — spot-checked the actual failure text for `test_socket_empty_instruction_present[readme]`, `test_linker_comment_cross_references_record`, `test_seed_status_is_no_longer_dormant` and `test_planted_mutation_of_the_real_subset_is_detected` to confirm no accidental logic bug was masquerading as an expected RED.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The full gated-literal, needle-set and accessor surface (`_L1_NON_RETIREMENT`, `_L2_SHIP_GATE`, `_L3_SOCKET_EMPTY`, `_S1_NEEDLES`…`_S5_NEEDLES`, `_S2_UNDECIDED_NEEDLES`, `_S3_FIGURE_RE`, `_S3_COST_TOKENS`, `_S4_NEEDLES`, `_LINKER_NEEDLES`, `_LINKER_FORBIDDEN_RE`) is committed and importable — plans 129-03 through 129-08 write prose against these exact constants rather than re-deriving wording.
- `_checklist_rows()` and `_frontmatter()` are ready for 129-04 (PCB-02 checklist) and 129-08 (seed frontmatter) respectively, both already exercised (as RED) against the real target files.
- The planted-mutation leg (`test_planted_mutation_of_the_real_subset_is_detected`) is wired against the REAL `_FW_DOC` path (not a synthetic fixture) and will need `platform/py32f071/FLASH-PATH-AND-PCB.md`'s S3 body to actually contain the literal string `24 KiB` once 129-04/129-06 write it, or the replacement-target assertion inside this leg will itself need revisiting at that point (flagged for 129-06, since RESEARCH F-3's own wording already fixes `24 KiB` as the sector-quantised figure, so no drift is expected).
- No blockers. Firmware tree is clean at commit `42395cf` on `v1.23-py32f071-integration`. Meta repo untouched apart from this SUMMARY (no `.planning/` prose changed, no gitlink committed — `firestarter` and `firestarter_app` both show as dirty gitlinks in `git status` at the meta level, both expected and deliberately left for `129-09`).

---
*Phase: 129-flash-path-decision-pcb-requirements-record*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: `firestarter/tests/test_flash_path_record_sync.py`
- FOUND: commit `663b576` in `firestarter` git log
- FOUND: commit `42395cf` in `firestarter` git log
- FOUND: `.planning/phases/129-flash-path-decision-pcb-requirements-record/129-02-SUMMARY.md`
