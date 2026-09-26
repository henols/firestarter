---
phase: 131-gate-hardening-ci-parity
plan: 03
subsystem: testing
tags: [sdp_capability, chip_database, pytest, ruff, gate-hardening, anti-narrowing]

# Dependency graph
requires:
  - phase: 131-01
    provides: fail-closed mypy watermark gate baseline; no interaction with this plan's SDP work
provides:
  - "A committed, sorted, manufacturer-qualified 43-entry SDP ALLOW snapshot (`_COMMITTED_SDP_ALLOW_ENTRIES`)"
  - "An element-wise parity leg that names any chip moving ALLOW<->REFUSE in either direction"
  - "The literal 43/41/84 triple, asserted separately, both counts derived (never hardcoded twice)"
  - "A change-protocol comment on the constant: decode reason only, never a test-outcome reason"
  - "A non-vacuity proof that a synthetic moved chip reddens the same helper the real legs call, naming it"
affects: [132-mypy-watermark-and-error-fixes, 137-close-honesty-ledger]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Committed data snapshot + element-wise comparison helper as the independent side of a gate, when the true independent derivation source (infoic.xml) is gitignored and absent -- comparing a predicate to itself is self-parity, not a gate"
    - "Non-vacuity legs assert on the raised message content, not only on the fact of a raise, and assert a control item is NOT named to prove specificity"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_sdp_db_invariant.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Correction F-01 applied: D-06 leg 1's independently-derived partition is not implementable in this repo (chip_database.json carries zero `flags` fields; tools/infoic*.xml is gitignored and absent) -- replaced with a committed 43-entry ALLOW snapshot, generated once from _partition_0x0d and hand-verified against 5 spot-check anchors before being pasted in"
  - "Correction F-02 applied: test_sdp_table_parity.py is requires_fw-skipped whole-module under CI-parity recipe leg 1, so all DB-only legs (both new ones, plus the non-vacuity proof) live in test_sdp_db_invariant.py, which carries no FW skip marker"
  - "Committed ALLOW list is keyed manufacturer/part_number, not part_number alone -- SGS-THOMSON and ST both list M28010, M28C64,M28C64A, and M28C64-xxW as second sources; a part-number-only key would collide and silently drop entries"

requirements-completed: [GATE-08]

coverage:
  - id: D1
    description: "Committed 43-name ALLOW snapshot with change-protocol comment, compared element-wise against sdp_capability_for_entry's answer for all 84 algorithm-13 chips, naming any chip that moved in either direction"
    requirement: "GATE-08"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_sdp_db_invariant.py#test_sdp_partition_matches_committed_allow_list_element_wise"
        status: pass
    human_judgment: false
  - id: D2
    description: "The literal 43 ALLOW / 41 REFUSE / 84 total triple, asserted separately with both counts derived from the shared partition helper, never hardcoded a second time"
    requirement: "GATE-08"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_sdp_db_invariant.py#test_sdp_partition_counts_are_43_41_84"
        status: pass
    human_judgment: false
  - id: D3
    description: "Non-vacuity proof: a synthetic chip moved out of ALLOW reddens the same _assert_partition_matches_committed helper the real legs call, naming the moved chip and not an untouched control chip"
    requirement: "GATE-08"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_sdp_db_invariant.py#test_partition_flags_a_moved_chip_non_vacuous"
        status: pass
    human_judgment: false

# Metrics
duration: ~30min
completed: 2026-08-03
status: complete
---

# Phase 131 Plan 03: Anti-Narrowing SDP Partition Gate Summary

**Closed P-10's hole with a committed 43-entry ALLOW snapshot compared element-wise against `sdp_capability_for_entry`, plus a synthetic non-vacuity proof that a moved chip is caught by name.**

## Performance

- **Duration:** ~30 min
- **Completed:** 2026-08-03T12:53:23Z
- **Tasks:** 2 (Task 1 as RED/GREEN TDD pair; Task 2 as one commit)
- **Files modified:** 2 (`firestarter_app/tests/test_sdp_db_invariant.py`, `.planning/REQUIREMENTS.md`)

## Accomplishments

- Extended `tests/test_sdp_db_invariant.py` in place (no third module) with:
  - `_partition_0x0d(db)`: partitions every algorithm==13 chip into sorted, manufacturer-qualified `MANUFACTURER/PART_NUMBER` ALLOW/REFUSE keys by calling the production `sdp_capability_for_entry` predicate — never a reimplementation.
  - `_assert_partition_matches_committed(measured_allow, committed_allow)`: raises naming both the narrowing direction (left ALLOW) and the widening direction (entered ALLOW) separately.
  - `_COMMITTED_SDP_ALLOW_ENTRIES`: a sorted, 43-entry, manufacturer-qualified tuple, generated once from the real DB and hand-verified against all five plan-specified spot-check anchors, carrying a change-protocol comment (decode reason only, never a test-outcome reason).
  - `test_sdp_partition_matches_committed_allow_list_element_wise` — Leg A, element-wise parity.
  - `test_sdp_partition_counts_are_43_41_84` — Leg B, the literal triple, both counts derived.
  - `test_partition_flags_a_moved_chip_non_vacuous` — a synthetic in-memory DB with an ALLOW chip and a REFUSE control chip; the ALLOW chip is renamed to an unrecognised token (simulating a real narrowing move) and the same helpers the real legs use are proven to raise, naming the moved chip and *not* the untouched control chip.
- Measured live 2026-08-03: 43 ALLOW / 41 REFUSE / 84 total (unchanged from the plan's stated figures).
- Whole suite (`tests/`) passes both with `FIRESTARTER_FW_ROOT` pointed at an empty directory (zero unexpected failures — only the pre-existing fw-absent `SKIPPED` entries from unrelated modules) and with the sibling present.
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both clean.
- `git -C /workspaces/firestarter status --short` is empty — firmware untouched, as required.
- Ticked `GATE-08` (only this ID) in `.planning/REQUIREMENTS.md`, with an evidence clause naming both real legs, and updated its Traceability row to Complete.

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule, on its existing milestone branch (`gsd/v1.30-sdp-surface-retirement`):

1. **Task 1 (RED):** `68447a4` — `test(131-03): RED - anti-narrowing SDP partition legs (GATE-08)`. `_COMMITTED_SDP_ALLOW_ENTRIES` intentionally set to an empty tuple; the element-wise leg was confirmed to fail for the right reason (naming all 43 real ALLOW entries as "entered", none as "left"), while the count leg — which doesn't depend on the constant — already passed. Failure reason read before proceeding.
2. **Task 1 (GREEN):** `9ee7573` — `feat(131-03): GREEN - committed 43-name SDP ALLOW snapshot (GATE-08)`. Replaced the placeholder with the generated, hand-verified 43-entry list. Both new legs pass; zero skips under both a present and an empty `FIRESTARTER_FW_ROOT`.
3. **Task 2:** `f862f97` — `test(131-03): non-vacuity proof for the narrowing gate (GATE-08)`. Added the synthetic-moved-chip non-vacuity leg; whole-suite pass confirmed both ways.

**Meta-repo commit (this plan's docs):** pending final metadata commit (see below).

_Note: Task 1 is a genuine TDD RED→GREEN pair per its `tdd="true"` frontmatter flag; Task 2 is a single `test(...)` commit since it adds a new test rather than modifying production behavior._

## Files Created/Modified

- `firestarter_app/tests/test_sdp_db_invariant.py` — extended in place: 3 new shared/module-level items (`_partition_0x0d`, `_assert_partition_matches_committed`, `_COMMITTED_SDP_ALLOW_ENTRIES`) and 3 new test functions (`test_sdp_partition_matches_committed_allow_list_element_wise`, `test_sdp_partition_counts_are_43_41_84`, `test_partition_flags_a_moved_chip_non_vacuous`). Module docstring's `Coverage:` list gained entries 5–7.
- `.planning/REQUIREMENTS.md` — ticked `GATE-08`'s checkbox with an evidence clause naming the two real test functions; updated its Traceability row from `Pending` to `Complete`.

## Decisions Made

- **Correction F-01 (recorded per plan instruction).** D-06 leg 1 asked for the partition to be independently recomputed from `chip_database.json` plus the committed `flags` bit-15 decode and compared against `sdp_capability()`. Measured 2026-08-03: `chip_database.json` contains **zero** occurrences of the string `"flags"` (no per-chip protection metadata is shipped in this repo), and `tools/infoic.xml` — the bit-15 source — is gitignored (`.gitignore:29`, pattern `tools/infoic*.xml`) and absent from the working tree. Implementing leg 1 literally would recompute the partition using the very function under test (`sdp_capability_for_entry`) — self-parity, which passes whenever both sides drift together and is precisely the hole this gate exists to close. **Replacement:** a committed, sorted, 43-entry ALLOW list checked into the test module as `_COMMITTED_SDP_ALLOW_ENTRIES`. The measured side comes from `_partition_0x0d`, which calls the real predicate. A chip moving ALLOW→REFUSE reddens the element-wise leg, and the only diff that greens it is a visible edit to the named committed constant — governed by its change-protocol comment. This preserves exactly what D-06 leg 1 was built to protect, without the self-parity failure mode. D-06 legs 2 (the literal triple) and 3 (change protocol) survive unchanged.
- **Correction F-02 (recorded per plan instruction).** D-06 said to extend both `tests/test_sdp_db_invariant.py` and `tests/test_sdp_table_parity.py`. Measured: `test_sdp_table_parity.py` imports the sibling-repo presence marker from `tests.fw_presence` at module scope and resolves firmware paths at import time, so the whole module is skipped under the CI-parity recipe's empty-sibling leg (recipe leg 1) and in standalone CI. Any 43/41/84 leg placed there would be invisible exactly where it matters most. **All DB-only legs (the two new ones plus the non-vacuity proof) went into `test_sdp_db_invariant.py` instead**, which the module's own docstring already states carries no FW-absent skip marker for exactly this reason. `test_sdp_table_parity.py` was not touched. This also mechanically discharges D-18's negative criterion (any test this phase adds must pass under recipe leg 1).
- **Manufacturer-qualified keying.** `_partition_0x0d` keys entries as `MANUFACTURER/PART_NUMBER`, not `PART_NUMBER` alone, because three ALLOW part numbers (`M28010`, `M28C64,M28C64A`, `M28C64-xxW`) are duplicated across `SGS-THOMSON` and `ST` as second-source listings; a part-number-only key would collide and silently lose entries. Verified: both `SGS-THOMSON/M28010` and `ST/M28010` are present in the committed list.

**Flagged for Phase 137's ledger:** corrections F-01 and F-02, per the plan's `<output>` instruction.

## Deviations from Plan

None beyond the two plan-anticipated corrections (F-01, F-02) documented above, which the plan itself directed this executor to apply and record — not discretionary deviations.

One minor authoring correction not called out by the plan: the module docstring's correction-F-02 explanation initially used the literal substring `requires_fw` in prose, which tripped the acceptance criterion's `grep -c 'requires_fw\|pytest.skip\|skipif'` check (a literal string match, not marker detection). Reworded to describe the mechanism ("imports the sibling-repo presence marker from `tests.fw_presence`") without using the literal token. No functional change; caught before the GREEN commit landed. **[Rule 3 - Blocking]** — a mechanical false-positive against the plan's own acceptance gate, fixed inline before proceeding.

## Issues Encountered

None. This plan makes zero deletions, sets no mypy watermark, fixes no mypy errors, and does not touch `tools/check_sdp_capability_invariants.py` or `firestarter/sdp_capability.py`, per the plan's scope. `firestarter_app`'s primary `ci` job is left RED by design (Phase 132's responsibility, unaffected by this plan).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- GATE-08 is complete; the anti-narrowing SDP partition gate is live in `firestarter_app/tests/test_sdp_db_invariant.py`, runs under both recipe leg 1 (empty `FIRESTARTER_FW_ROOT`) and standalone CI, and carries no skip marker.
- Corrections F-01 and F-02 are recorded here for Phase 137's negative-space ledger, alongside the other four corrections from `131-01`/`131-02`.
- No blockers for `131-04` (GATE-10) or the remaining phase 131 plans; this plan's file (`tests/test_sdp_db_invariant.py`) is not touched by any other plan in this phase.

---
*Phase: 131-gate-hardening-ci-parity*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/131-gate-hardening-ci-parity/131-03-SUMMARY.md`
- FOUND: `/workspaces/firestarter_app/tests/test_sdp_db_invariant.py`
- FOUND commit: `68447a4` (RED)
- FOUND commit: `9ee7573` (GREEN)
- FOUND commit: `f862f97` (non-vacuity proof)
