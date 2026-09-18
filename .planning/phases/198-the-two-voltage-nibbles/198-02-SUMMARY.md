---
phase: 198-the-two-voltage-nibbles
plan: 02
subsystem: database
tags: [chip-database, vcc, vdd, datasheet-overrides, decode-tables]

requires:
  - phase: 198-the-two-voltage-nibbles
    provides: "198-01's completed VPP_MV decode table, exact-match-before-mask pattern, and DECODE-NOTES.md § 9 opened for extension"
provides:
  - Completed VCC_VOLTAGES decode table (xg_vcc_voltages[], 15 entries, 0x00-0x0E)
  - Twelve signed UNSOURCED override entries holding the vdd-index-0x06 carve-out at its pre-completion value
  - Planted-mutation, structural and predicate test coverage proving the carve-out is load-bearing
  - The phase's full regeneration record (198-REGEN-DIFF.md, 15 rows / 17 fields)
affects: [198-03, 198-04, "any future phase touching VCC_VOLTAGES or datasheet_overrides.json"]

actuals:
  tokens: 8563
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Structural override-count assertions derive the held-entry set from the file itself via its field-shape (not a hardcoded key list), so a future datasheet closing one entry does not require editing the test's expected-key list."
    - "A relational predicate (vdd < vcc) is pinned as a test against the emitted database rather than shipped as a build-time assertion, per D-06's discretion clause -- reporting, not correcting."

key-files:
  created:
    - .planning/phases/198-the-two-voltage-nibbles/198-REGEN-DIFF.md
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/tools/datasheet_overrides.json
    - firestarter_app/tools/DECODE-NOTES.md
    - firestarter_app/tests/test_vcc_margin_rail.py
    - firestarter_app/tests/test_datasheet_overrides.py
    - firestarter_app/firestarter/data/chip_database.json

key-decisions:
  - "D-01 applied: VCC_VOLTAGES completed from xg_vcc_voltages[] -- nine more indices (0x06..0x0E), a strict conflict-free superset of the six already shipped."
  - "D-04/D-05 applied: the twelve 0x06 rows keep vdd_mv 5000, held by twelve explicit UNSOURCED override entries rather than by omitting 0x06 from the table."
  - "D-06 applied (as a test, per Claude's discretion, not a build-time assertion): the vdd < vcc predicate is pinned against the emitted database -- exactly 28 rows, exactly matching the vcc_mv == 5500 set."
  - "D-08/D-10 recorded in 198-REGEN-DIFF.md rather than in code -- the FUJITSU/MBM27C2001 family inconsistency and the firmware guard-band consequence of raising VPP to 12500, both per the phase's explicit instruction that these have no other home."
  - "A falsified provenance marker (database.c#L130-L135, actually tl866a_vpp_voltages[] plus the start of tl866a_vcc_voltages[]) was deleted whole, not rewritten, from both its occurrences, per CLAUDE.md's comment-deletion discipline; the corrected citation was relocated to DECODE-NOTES.md § 9."

requirements-completed: [VOLT-01, VOLT-03]

coverage:
  - id: D1
    description: "VCC_VOLTAGES equals upstream's 15-index xg_vcc_voltages[] map exactly (0x00-0x0E), no 0x0F entry, _VCC_MARGIN_RAIL_MV unchanged at 4000; the falsified database.c#L130-L135 citation is deleted from both occurrences and relocated to DECODE-NOTES.md § 9 with the corrected L182-L190 citation."
    requirement: "VOLT-01"
    verification:
      - kind: command
        ref: "python -c VCC_TABLE_OK assertion (15-entry map identity + margin-rail check)"
        status: pass
      - kind: unit
        ref: "full suite: 2069 passed, 0 failed (Python 3.11), after Task 1"
        status: pass
    human_judgment: false
  - id: D2
    description: "tools/datasheet_overrides.json holds 22 sorted keys, 18 UNSOURCED, 4 tracked-PDF citations; exactly twelve entries carry the single field pair electrical.vdd_mv was 1800/is 5000, all UNSOURCED, all ending in a Closed by: sentence; the regeneration diff for this plan's Task 1 is exactly 12 rows / 12 electrical.vdd_mv values (the 0x0D/0x0E movers), zero vcc_mv movement, identical row-key set and support_status multiset; exactly 12 EXEL/ST/SGS-THOMSON rows still emit vdd_mv 5000 / vcc_mv 5500."
    requirement: "VOLT-03"
    verification:
      - kind: command
        ref: "python -c HELD_OK 12 assertion (override file structure)"
        status: pass
      - kind: command
        ref: "python -c DIFF_OK 12 12 assertion (regeneration diff vs prior HEAD)"
        status: pass
      - kind: command
        ref: "python -c CARVEOUT_OK 12 assertion (emitted database carve-out census)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The twelve held entries are proven load-bearing by a planted-mutation test (applying the entry writes its is value; mutating is changes the emitted value; a stale was against a non-matching decode raises); a structural assertion derives the twelve from the shipped file itself; the vdd<vcc predicate is pinned against the emitted database at exactly 28 rows, matching the vcc_mv==5500 set, with the three below/equal/above buckets (28/433/285) summing to 746."
    requirement: "VOLT-01"
    verification:
      - kind: unit
        ref: "tests/test_datasheet_overrides.py::TestHeldEntryIsLoadBearing"
        status: pass
      - kind: unit
        ref: "tests/test_datasheet_overrides.py::TestVddBelowVccPredicate"
        status: pass
      - kind: unit
        ref: "tests/test_datasheet_overrides.py::TestShippedOverrideFileContract::test_exactly_twelve_held_0x06_carveout_entries"
        status: pass
      - kind: unit
        ref: "full suite: 2075 passed, 0 failed (Python 3.11), after Task 2"
        status: pass
    human_judgment: false
  - id: D4
    description: "198-REGEN-DIFF.md carries all five required sections (reproducible method, row-count line, changed-fields table, zero-diff-claims, honesty limit), the 746/15/17/0372cc6/MBM27C2001 tokens, at least 19 table lines, and leaves .planning/milestones/ untouched. Records D-10's firmware guard-band consequence and D-08's Fujitsu family inconsistency, both stated as having no other home."
    requirement: "VOLT-03"
    verification:
      - kind: command
        ref: "SECTIONS_OK / TOKENS_OK / TABLE_OK / MILESTONES_UNTOUCHED shell assertions"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-09-18
status: complete
---

# Phase 198 Plan 02: The completed VCC decode table and the signed 0x06 carve-out Summary

**Completed `VCC_VOLTAGES` from upstream's `xg_vcc_voltages[]` (nine more indices), signed the twelve
rows whose completed decode is not credible for their part class with explicit `UNSOURCED` override
entries, proved those entries load-bearing with a planted-mutation test, pinned the `vdd < vcc`
predicate against the emitted database, and wrote the phase's full regeneration record.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-09-18
- **Tasks:** 3
- **Files modified:** 6 (1 newly created)

## Accomplishments

- `VCC_VOLTAGES` completed to upstream's 15-entry `xg_vcc_voltages[]` map (`0x06`=1800, `0x07`=2500,
  `0x08`=3000, `0x09`=1200, `0x0A`=4750, `0x0B`=5250, `0x0C`=5750, `0x0D`=6000, `0x0E`=6250), with the
  six existing entries unchanged and no `0x0F` entry (genuinely absent upstream). `VCC_VOLTAGES[0x02]`
  and `_VCC_MARGIN_RAIL_MV` are unchanged (still 4000).
- Twelve rows at vdd index `0x06` (7 EXEL, 3 ST, 2 SGS-THOMSON, 28C-class 5V EEPROMs) decode to a
  1.8V figure not credible as their program rail; held at the previously-emitted 5000 mV by twelve
  explicit `UNSOURCED` entries in `tools/datasheet_overrides.json`, each naming what would close it.
- Five rows at vdd index `0x0D` now emit `vdd_mv` 6000 (was 5000); seven rows at vdd index `0x0E` now
  emit `vdd_mv` 6250 (was 5000) — the completed table reaching what used to be a fabricated fallback.
- A falsified provenance marker (`database.c#L130-L135`, actually `tl866a_vpp_voltages[]` plus the
  start of `tl866a_vcc_voltages[]`) was found duplicated on both `VCC_VOLTAGES` and
  `_VCC_MARGIN_RAIL_MV`, deleted whole from both occurrences, and its corrected provenance
  (`database.c#L182-L190`, `xg_vcc_voltages[]`) relocated to `DECODE-NOTES.md` § 9.
- The same falsified citation, surviving as a module docstring in `tests/test_vcc_margin_rail.py`,
  was corrected in place (a docstring is not a comment under the project rule).
- A planted-mutation test (`TestHeldEntryIsLoadBearing`) proves the twelve held entries actually do
  the work: applying a synthetic held entry to a matching decoded view yields 5000; mutating its
  `is` value yields the mutated value instead; applying it to a non-matching decoded view raises.
- A structural test derives the twelve held entries from the shipped file itself (no hardcoded key
  list) and asserts the exact count, the `UNSOURCED` token and the closure sentence on each.
- `TestVddBelowVccPredicate` pins D-06's relational key against the emitted database: exactly 28
  rows have `vdd_mv` below `vcc_mv`, that set equals the `vcc_mv == 5500` set, and the three buckets
  (28 below / 433 equal / 285 above) partition all 746 rows. This is a test, not a build-time
  assertion — nothing in `build_db.py` hangs off the predicate, per D-06's discretion clause.
- `.planning/phases/198-the-two-voltage-nibbles/198-REGEN-DIFF.md` written: the phase's full
  regeneration diff against the pre-phase commit `0372cc6` is exactly 15 rows / 17 field values, all
  `electrical`, zero `support_status` changes, 746 in / 746 out — reconciling exactly against
  198-01's measured 3-row/5-field diff plus this plan's measured 12-row/12-field diff. Records D-10's
  firmware guard-band consequence and D-08's `FUJITSU/MBM27C2001` family inconsistency, both stated
  as having no other home.

## Task Commits

Each task was committed atomically inside `firestarter_app` (Tasks 1-2) or the meta repo (Task 3),
all on `v1.40-program-parameter-fidelity`, with the meta-repo gitlink advanced in a following commit
for each `firestarter_app` task:

1. **Task 1: Complete the VCC table and sign the 0x06 carve-out, in one commit** —
   `firestarter_app@0849135` (feat) / meta `872b4f2e`
2. **Task 2: Prove the twelve held entries are load-bearing, and pin the group's key predicate** —
   `firestarter_app@80735b2` (test) / meta `33c8ceb9`
3. **Task 3: The phase's regeneration record** — meta `0ec4591d` (docs, no `firestarter_app` commit
   — this task touches only `.planning/`)

**Plan metadata:** this SUMMARY's own commit (below).

_No STATE.md/ROADMAP.md commit — the orchestrator owns those writes for this phase per the execution
brief._

## Files Created/Modified

- `firestarter_app/tools/build_db.py` — `VCC_VOLTAGES` gains 9 keys (`0x06`-`0x0E`); the two
  duplicated falsified provenance markers deleted (2 comment lines, quoted below); comment-line count
  moved from 186 to 184.
- `firestarter_app/tools/datasheet_overrides.json` — 12 new `UNSOURCED` entries (10 → 22 keys, 6 → 18
  `UNSOURCED`), each holding `electrical.vdd_mv` `was: 1800, is: 5000` for one EXEL/ST/SGS-THOMSON row.
- `firestarter_app/tools/DECODE-NOTES.md` — § 9 extended with the completed `VCC_VOLTAGES`
  provenance, the falsified-citation finding, and the twelve-row carve-out rationale.
- `firestarter_app/tests/test_vcc_margin_rail.py` — module docstring's falsified citation corrected
  (`L130-L135`/`tl866ii_vcc_voltages[]` → `L182-L190`/`xg_vcc_voltages[]`).
- `firestarter_app/tests/test_datasheet_overrides.py` — `_EXPECTED_ENTRY_COUNT` 10 → 22,
  `_EXPECTED_UNSOURCED_COUNT` 6 → 18; added `test_exactly_twelve_held_0x06_carveout_entries`,
  `TestHeldEntryIsLoadBearing` (3 tests) and `TestVddBelowVccPredicate` (2 tests) — 5 new tests,
  module collects 26.
- `firestarter_app/firestarter/data/chip_database.json` — GENERATED; this plan's Task 1 diff is 12
  rows / 12 `electrical.vdd_mv` values (the `0x0D`/`0x0E` movers); the phase's cumulative diff
  (Task 1 of `198-01` + Task 1 of `198-02`) is 15 rows / 17 field values.
- `.planning/phases/198-the-two-voltage-nibbles/198-REGEN-DIFF.md` — new, the phase's regeneration
  record.

## Decisions Made

- **D-01** applied: `VCC_VOLTAGES` completed from `xg_vcc_voltages[]`, confirmed a strict
  conflict-free superset of the six already-shipped indices (measured, not merely trusted from
  RESEARCH — the `VCC_TABLE_OK` assertion compared the live table against the transcribed upstream
  map field-by-field).
- **D-04/D-05** applied: the twelve `0x06` rows held at 5000 via explicit override entries rather
  than by omitting `0x06` from the table — each entry states plainly that 1800 is not credible for
  the part class and that the 5000 it holds is itself an unmapped-index fallback, not a datasheet
  figure.
- **D-06** applied as a test (Claude's discretion, per plan): the `vdd < vcc` predicate is pinned in
  `tests/test_datasheet_overrides.py` against the live database, not shipped as a build-time
  assertion in `build_db.py`.
- **D-08/D-10** recorded in `198-REGEN-DIFF.md` only, per the plan's explicit instruction that this
  record is their only home — no code encodes either.
- **D-16 cited**: the deleted falsified marker's corrected content relocated to `DECODE-NOTES.md` §
  9 rather than lost, following the same discipline `198-01` used for the VPP mask comment.
- **Claude's discretion (198-CONTEXT.md)** exercised: coverage for the twelve held entries used one
  planted-mutation test plus a structural count (the 197-06 shape), not twelve near-duplicate
  per-entry assertions — the plan's own reasoning (no additional failure-detection power) was
  followed as written.

## Deviations from Plan

**1. [Rule 1 - Bug] The plan's own `DIFF_OK` verify script raised `AttributeError` on scalar fields**
- **Found during:** Task 1, running the regeneration-diff verify leg before committing
- **Issue:** The plan's inline verify script iterates `sec in set(fb[k]) | set(fa[k])` over every
  top-level key of a row, including scalar fields (`part_number`, `pinout`, `support_status`). For
  those, `fb[k].get(sec, {})` returns a string, not a dict; `set(string)` enumerates characters, and
  the subsequent `.get(f)` call on that string raises `AttributeError: 'str' object has no attribute
  'get'`.
- **Fix:** Ran a corrected version of the same script (used only as an ad-hoc diagnostic to satisfy
  the verify leg's intent, not committed to the repo) that only descends into a `sec` when either
  side's value is a `dict`, and otherwise compares the scalar values directly. This is exactly the
  semantic the script's surrounding assertions already assumed (it separately checks
  `support_status` via `.values()`, confirming scalar fields were never meant to be walked this way).
- **Files affected:** none — this is a diagnostic-only fix to an inline verify command, not a
  change to any committed file.
- **Verification:** The corrected script produced `DIFF_OK 12 12`, matching the plan's required
  output exactly, and confirmed via the independent `CARVEOUT_OK 12` and `VCC_TABLE_OK` legs that the
  underlying database state is correct.
- **Commit:** N/A (diagnostic-only; no file changed).

**Total deviations:** 1 auto-fixed (Rule 1, diagnostic script bug, no committed-file impact).
**Impact:** None on shipped artifacts — the fix was to the executor's own verification tooling, not
to any file this plan modifies or ships.

## Measured Values (per plan `<output>` spec)

- **Task 1 regeneration diff:** exactly 12 rows, 12 field values, all `electrical.vdd_mv` (the
  `0x0D`/`0x0E` movers), identical row-key set, identical `support_status` multiset (`DIFF_OK 12
  12`).
- **`vcc_mv` movement count:** 0 (measured directly in the same diff leg).
- **Deleted comment line count:** 2, both identical, quoted verbatim:
  ```
  # [VERIFIED: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]]
  ```
  (One copy sat immediately above `VCC_VOLTAGES`; the second, identical copy sat immediately above
  the `_VCC_MARGIN_RAIL_MV` comment block.) `build_db.py`'s hash-prefixed line count moved from 186
  to 184 (measured with the same one-line Python count both before and after).
- **`tests/test_datasheet_overrides.py` collected test count:** 26 (was 21 before this plan; +5 new
  tests: 1 structural + 3 planted-mutation + 2 predicate).
- **End-state full 3.11 suite, after Task 1:** `2069 passed` (0 failed).
- **End-state full 3.11 suite, after Task 2 (final):** `2075 passed` (0 failed), run via
  `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q -p no:randomly -rf`.
- **`vdd`-vs-`vcc` predicate, three bucket counts against the final database:** 28 below (`vdd_mv <
  vcc_mv`), 433 equal, 285 above; 28 + 433 + 285 = 746 (`PREDICATE_OK 28 718` for the below/not-below
  split; 433/285 measured separately for the full three-way breakdown).

## Issues Encountered

None beyond the diagnostic-script deviation documented above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan `198-03` can proceed: `DECODE-NOTES.md` § 9 now carries both the VPP and VCC decode
  completions and the falsified-citation corrections; § 9's closing paragraph still defers the
  general D-15 finding (the voltage word's nibbles select a programmer rail index, not a chip
  requirement) to `198-03` as planned.
- `198-04` inherits: the held gh#66 draft (D-17) still needs composing; sub-group 1's sixteen-row
  per-row disposition (D-13) is untouched by this plan; the todo close (D-12) and the consolidated
  held-pending list (D-18) are both still open.
- The database, override file and test suite are all internally consistent and fully green (2075
  passed) — no residual red state carries forward.
- `198-REGEN-DIFF.md` is the phase's complete regeneration record to date; any further phase-198
  plan that changes `electrical.*` fields should extend it rather than write a second one.

---
*Phase: 198-the-two-voltage-nibbles*
*Completed: 2026-09-18*

## Self-Check: PASSED

- All created/modified files confirmed present on disk (`tools/build_db.py`, `tools/datasheet_overrides.json`,
  `tools/DECODE-NOTES.md`, `tests/test_vcc_margin_rail.py`, `tests/test_datasheet_overrides.py`,
  `firestarter/data/chip_database.json`, `.planning/phases/198-the-two-voltage-nibbles/198-REGEN-DIFF.md`).
- All task commit hashes (`firestarter_app@0849135`, `firestarter_app@80735b2`) and all meta commit
  hashes (`872b4f2e`, `33c8ceb9`, `0ec4591d`) confirmed present in `git log --oneline --all` in their
  respective repositories.
- Full 3.11 suite re-confirmed green (2075 passed, 0 failed) after both `firestarter_app` tasks
  landed.
- Both repositories confirmed on branch `v1.40-program-parameter-fidelity` after every commit.
- `git status --porcelain -- .planning/milestones/` confirmed empty — nothing under the archived
  milestones directory was touched.
