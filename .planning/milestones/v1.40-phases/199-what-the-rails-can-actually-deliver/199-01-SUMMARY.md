---
phase: 199-what-the-rails-can-actually-deliver
plan: 01
subsystem: database
tags: [firestarter_app, chip-database, datasheet-override, wire-protocol, tdd, gh-71]

# Dependency graph
requires:
  - phase: 198-the-two-voltage-nibbles
    provides: the datasheet-override mechanism, the FUJITSU/MBM27128 override entry (pulse_duration_us, vdd_mv), and the six/seven-layer wire-dict delta composition pattern this plan extends to seven
provides:
  - "FUJITSU/MBM27128 electrical.vpp_mv corrected 18000 -> 21000 in the shipped chip database, per its own vendored datasheet"
  - "the Phase 199 wire delta layer (tests/golden/wire_dict_expected_deltas_199.json), generated not transcribed, proven capable of failing"
  - "a committed one-row regeneration record (199-REGEN-DIFF.md) as RAIL-02 database-half evidence"
affects: [199-02, 199-03, 199-04, 199-05, gh-71-answer]

# Actuals (#2632)
actuals:
  tokens: 7500
  tasks: 3
  commits: 6

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Datasheet-override field addition to an existing entry (no new top-level key), following the FUJITSU/MBM27C1001 sibling's field ordering"
    - "Generated (not hand-transcribed) wire-dict delta layer, seventh in the 149/153/182/194/197/198/199 composition chain"
    - "TDD RED/GREEN split for a fixture-then-wiring change: RED commits the ungwired delta fixture (module stays red), GREEN wires it into the composition test, count test, layer_pairs, and adds the non-vacuity leg"

key-files:
  created:
    - firestarter_app/tests/golden/wire_dict_expected_deltas_199.json
    - .planning/phases/199-what-the-rails-can-actually-deliver/199-REGEN-DIFF.md
  modified:
    - firestarter_app/tools/datasheet_overrides.json
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - firestarter_app/tests/test_wire_dict_equivalence.py

key-decisions:
  - "D-17 executed exactly as scoped: one field (electrical.vpp_mv) added to the existing FUJITSU/MBM27128 override entry, was 18000 / is 21000, citing the same Figure 3 Quick Pro table already cited for pulse_duration_us and vdd_mv."
  - "D-01 verified to survive D-17: the regeneration diff's support_status multiset is byte-identical before and after; 21000 sits strictly below RURP_VPP_CEILING_MV at 25000 and the ceiling comparison is strict '>'."
  - "Deviation: reworded one pre-existing docstring clause and deleted one pre-existing inline comment (both from the 197/198 lineage, neither touched by this plan's own action text) because their prose restated the literal expression 'len(deltas_153) == 84', colliding with this task's own MODULE_SHAPE_OK verify leg (which requires that literal substring to occur exactly once, guarding against an accidentally duplicated assertion). The actual assertion and test_exactly_84's name/literals are byte-unchanged; see Deviations section."

requirements-completed: [RAIL-02]

coverage:
  - id: D1
    description: "FUJITSU/MBM27128 emits electrical.vpp_mv 21000 in the generated database; regeneration diff proves exactly one row and one field changed, 746 rows in/out, support_status multiset unchanged"
    requirement: "RAIL-02"
    verification:
      - kind: unit
        ref: "OVERRIDES_199_OK inline verify leg (Task 1) -- override file shape and field values"
        status: pass
      - kind: unit
        ref: "REGEN_199_OK inline verify leg (Task 1) -- regeneration diff against HEAD f155364"
        status: pass
      - kind: unit
        ref: "tests/test_datasheet_overrides.py, tests/test_chip_database_field_inventory.py -- full suite"
        status: pass
    human_judgment: false
  - id: D2
    description: "The rendered chip list shows 21.0v for MBM27128; snapshot re-record scoped to test_list, numstat exactly 1 insertion / 1 deletion"
    requirement: "RAIL-02"
    verification:
      - kind: unit
        ref: "tests/test_characterization.py::test_list"
        status: pass
    human_judgment: false
  - id: D3
    description: "The Phase 199 wire delta layer holds exactly one record (FUJITSU|MBM27128|2, vpp_mv 21000), generated programmatically, field-disjoint from the 197 layer on the shared key, and proven capable of failing"
    requirement: "RAIL-02"
    verification:
      - kind: unit
        ref: "tests/test_wire_dict_equivalence.py -- full module (11 node ids)"
        status: pass
    human_judgment: false
  - id: D4
    description: "199-REGEN-DIFF.md records the one-row regeneration as reproducible, honest evidence"
    verification:
      - kind: other
        ref: "REGENDOC_HEADINGS_OK / REGENDOC_CONTENT_OK / FUJITSU-row-count inline verify legs (Task 3)"
        status: pass
    human_judgment: false

# Metrics
duration: 55min
completed: 2026-09-19
status: complete
---

# Phase 199 Plan 01: The MBM27128 tracer — override to rendered display, database half of RAIL-02

**FUJITSU/MBM27128's VPP corrected 18.0V to 21.0V per its own vendored datasheet, traced end-to-end from the override file through the regenerated database, the wire-dict delta layer, and the rendered chip list, with a committed one-row regeneration record.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-09-19T00:00:00Z (approx; not machine-recorded for this run)
- **Completed:** 2026-09-19
- **Tasks:** 3
- **Files modified/created:** 6 (2 created, 4 modified) across two repositories

## Accomplishments

- `FUJITSU/MBM27128` gained `electrical.vpp_mv` (`was` 18000 / `is` 21000) inside its existing datasheet-override entry, sourced from the same Figure 3 Quick Pro table (page 4-20 of `datasheets/MBM27128.pdf`) already cited for `pulse_duration_us` and `vdd_mv`. No new override entry, no new top-level key.
- Regenerated `chip_database.json`: 746 rows in, 746 rows out, exactly one changed field (`FUJITSU`/`MBM27128`/`electrical.vpp_mv`, 18000 -> 21000), `support_status` multiset byte-identical (D-01 holds — 21000 < `RURP_VPP_CEILING_MV` 25000, strict `>` comparison).
- Re-recorded `tests/__snapshots__/test_characterization.ambr` scoped to `test_list` only, numstat exactly `1 1`: the rendered chip list now shows `21.0v` for `MBM27128`.
- Generated (not hand-transcribed) `tests/golden/wire_dict_expected_deltas_199.json`: one record, `FUJITSU|MBM27128|2`, carrying `{"vpp_mv": 21000}`, field-disjoint from the 197 layer's `{"pulse-delay": ...}` on the same shared key.
- Wired the 199 layer into `tests/test_wire_dict_equivalence.py` via TDD RED/GREEN: RED committed the fixture alone (module still red, 85 vs 84 changed records); GREEN wired `_DELTAS_199` into the composition test, the six new `layer_pairs` tuples, the `test_exactly_84_records_change_flags_and_no_other_field_moves` count test (byte-unchanged name and literals), and a new `test_the_199_delta_layer_is_capable_of_failing`. Suite: 11 node ids collected (was 10), all pass.
- Wrote `199-REGEN-DIFF.md`, following the 197/198 precedent shape collapsed to a one-row instance: reproducible method, the four-item row-count line, the single changed-field table, the two positive no-drift claims, and a named honesty limit.

## Task Commits

Each task was committed atomically (across two repositories — the app change lives in `firestarter_app`, the plan-level record lives in the meta repo):

1. **Task 1: 21V reaches the operator (tracer)** — `firestarter_app@82e2461` (fix) + `meta@35c81625` (gitlink advance)
2. **Task 2: The Phase 199 wire delta layer (TDD)** — `firestarter_app@b26e764` (test, RED) + `firestarter_app@7e02494` (feat, GREEN) + `meta@cee6449c` (gitlink advance)
3. **Task 3: The one-row regeneration record** — `meta@3ab2e8f9` (docs)

**Plan metadata:** this SUMMARY's own commit (below).

_Note: Task 2 is a TDD task and produced two source commits (test -> feat); no REFACTOR commit was needed._

## Files Created/Modified

- `firestarter_app/tools/datasheet_overrides.json` — added `electrical.vpp_mv` to the existing `FUJITSU/MBM27128` entry; extended its `note` by one sentence; entry/UNSOURCED counts (22/18) unchanged.
- `firestarter_app/firestarter/data/chip_database.json` — regenerated; one row, one field changed.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — one line re-recorded inside `# name: test_list`.
- `firestarter_app/tests/golden/wire_dict_expected_deltas_199.json` — new, one-record delta layer with the required five-key `meta` block.
- `firestarter_app/tests/test_wire_dict_equivalence.py` — `_DELTAS_199` constant, non-vacuity + exact-count legs, six new `layer_pairs` tuples, composition into the 84-count test, new `test_the_199_delta_layer_is_capable_of_failing`, extended docstring coverage list.
- `.planning/phases/199-what-the-rails-can-actually-deliver/199-REGEN-DIFF.md` — new, the plan's regeneration evidence record.

## Decisions Made

- D-17 executed exactly as scoped (see frontmatter `key-decisions`).
- D-01 verified, not merely assumed, to survive D-17.
- The tracer feedback gate (Task 1, `type="tracer"`) was evaluated per the precedence chain: `AUTO_CHAIN`/`AUTO_CFG` both `false`, `human_verify_mode` unset (defaults `end-of-phase`), and Task 1's `<verify>` block carries only `<automated>` entries (no `<human-check>`) — so the gate re-ran the tracer's verify end-to-end, confirmed all legs pass, logged the auto-continue, and proceeded directly to Task 2 without synthesizing a checkpoint.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 2's `MODULE_SHAPE_OK` verify leg collided with pre-existing prose duplicating a literal expression**
- **Found during:** Task 2 (wiring the 199 delta layer into `test_wire_dict_equivalence.py`)
- **Issue:** The plan's own verify leg asserts `s.count('len(deltas_153) == 84') == 1` over the whole module source. Measured (before any of this plan's edits, i.e. inherited unchanged from Plan 198-01): the literal substring `len(deltas_153) == 84` already occurred **three** times — once in the module docstring's coverage-item-1 prose (bullet (e)), once in an inline `# (e) 153-layer exact count: ...` comment immediately above the real assertion, and once in the real `assert len(deltas_153) == 84,` statement itself. The check's own stated purpose (`fails_when`: "a count other than 1 ... means an existing assertion was edited or duplicated") is a guard against accidental code duplication; the two extra matches are narrative restatements, not code duplicates, and neither was touched or introduced by this plan's own edits.
- **Fix:** Reworded the docstring clause (permitted — docstrings are documentation, not comments under CLAUDE.md's hard rule) from `"(e) 153-layer exact count -- len(deltas_153) == 84, not "at least""` to `"(e) 153-layer exact count -- \`deltas_153\` pinned at 84 records, not a floor"`, preserving the same information without the literal expression. Deleted the redundant inline `# (e) 153-layer exact count: ... mirrors (c) for the new layer.` comment whole — a legal move under the plan's own prohibition ("the only legal moves on a comment are leave-it-byte-unchanged or delete-it-whole"; deletion is always permitted, only addition/rewriting is forbidden). The actual assertion (`assert len(deltas_153) == 84,`), `test_exactly_84_records_change_flags_and_no_other_field_moves`'s two literal assertions, and its name are all byte-unchanged — verified separately by diffing the function body against the pre-edit git blob.
- **Files modified:** `firestarter_app/tests/test_wire_dict_equivalence.py`
- **Verification:** Re-ran `MODULE_SHAPE_OK` (now passes, count == 1 for both `len(deltas_153) == 84` and `len(changed_keys) == 84`), the full `tests/test_wire_dict_equivalence.py` suite (11 passed), `ruff check`/`ruff format --check` (both clean), and confirmed the count test's body is byte-identical to its pre-edit state.
- **Committed in:** `firestarter_app@7e02494` (Task 2 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 blocking — a plan-authoring inconsistency in a verify leg's literal-count assumption, not a defect in the delivered override/database/wire-dict/snapshot changes).
**Impact on plan:** No scope creep. No test assertion, test name, or delivered behavior changed; only pre-existing narrative text (docstring prose and one redundant inline comment) was adjusted to make the module's own literal-count self-check consistent with itself.

## Issues Encountered

None beyond the deviation above. The `type="tracer"` feedback gate and the TDD RED/GREEN cycle both proceeded without incident; no auth gates were hit; no architectural questions arose.

## Numeric Results (per plan's `<output>` requirements)

- **Changed-row / changed-field counts (Task 1):** 746 rows in, 746 rows out, 1 row changed, 1 field changed (`electrical.vpp_mv`, 18000 -> 21000), 0 `support_status` changes.
- **Snapshot numstat (Task 1):** `1	1	tests/__snapshots__/test_characterization.ambr` (one insertion, one deletion), rendered row: `| MBM27128            | FUJITSU          |   28 |            | UV-EPROM    | 21.0v|`.
- **`len(deltas_199)` (Task 2):** 1 (`{"FUJITSU|MBM27128|2": {"vpp_mv": 21000}}`).
- **84-count test after composing the 199 layer (Task 2):** stayed at exactly 84 (not 85), with both literal assertions (`len(deltas_153) == 84`, `len(changed_keys) == 84`) and the test's name byte-unchanged.
- **Collected node-id count for `tests/test_wire_dict_equivalence.py`:** 10 before this plan, 11 after (the new `test_the_199_delta_layer_is_capable_of_failing`).
- **Row-count line as written into `199-REGEN-DIFF.md`:** Rows in 746, rows out 746, rows changed 1, `support_status` values changed 0.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The database half of RAIL-02 is complete and evidenced. `MBM27128` moved from the 18000 voltage bucket to the 21000 bucket, which Plan `199-04`'s census literals must be written against (per the plan's own `key_links`).
- The 199 delta layer, override entry, and regeneration record are all committed on `v1.40-program-parameter-fidelity` in both repositories, gitlink advanced. No blockers for `199-02` (the bench session) or `199-03`/`199-04`/`199-05`.
- No firmware file was touched, consistent with this phase being host-only.

## Self-Check: PASSED

- Branch identity: both `firestarter_app` and the meta repo confirmed on `v1.40-program-parameter-fidelity` after every commit.
- Created files exist on disk: `firestarter_app/tests/golden/wire_dict_expected_deltas_199.json`, `.planning/phases/199-what-the-rails-can-actually-deliver/199-REGEN-DIFF.md`, `.planning/phases/199-what-the-rails-can-actually-deliver/199-01-SUMMARY.md` — all FOUND.
- Commits exist in `git log --oneline --all`: `firestarter_app@82e2461`, `firestarter_app@b26e764`, `firestarter_app@7e02494`, `meta@3ab2e8f9`, `meta@ac85d4a9` — all FOUND.
- Meta gitlink for `firestarter_app` matches its live HEAD (`7e02494`).
- RAIL-02 correctly left unmarked in REQUIREMENTS.md pending sibling plans 199-04/199-05 (shared-ID gate, `requirements.ready-ids` reported 0/1 ready).

---
*Phase: 199-what-the-rails-can-actually-deliver*
*Completed: 2026-09-19*
