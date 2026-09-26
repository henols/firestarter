---
phase: 153-write-path-erase-policy
plan: 08
subsystem: testing
tags: [python, pytest, golden-fixture, wire-protocol, erase-policy, host]

# Dependency graph
requires:
  - phase: 153-07
    provides: "FLAG_CAN_ERASE restored on the wire for all 84 algorithm-13 rows; measured 84-row/flags-only/0->2 delta shape"
  - phase: 149-01
    provides: "wire_dict_baseline.json golden, wire_dict_expected_deltas_149.json (18 entries), _describe_record_diff helper, D-17 never-re-capture rule"
provides:
  - "wire_dict_expected_deltas_153.json: 84 non-vacuous flags-only delta entries + meta decision block"
  - "test_wire_dict_equivalence.py extended to compose two ordered, field-disjoint delta layers (149 page-size, 153 flags)"
  - "Exhaustive 746-row scope proof that exactly 84 records changed and only the flags field moved"
  - "Reachability proof that the new delta layer's gate can fail"
  - "Host suite reduced from the inherited 8 failures to exactly 7 (plans 09/10's remaining set), 1801 passed"
affects: [153-09, 153-10, 153-11, 153-12, 153-13, 153-16]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-layer delta composition over one preserved golden, asserted field-disjoint rather than assumed"
    - "Exhaustive-count leg re-asserts the total row count in the same test as the subset count (from test_page_size_invariants.py)"

key-files:
  created:
    - firestarter_app/tests/golden/wire_dict_expected_deltas_153.json
  modified:
    - firestarter_app/tests/test_wire_dict_equivalence.py

key-decisions:
  - "D-153-05 (restated in the new file's meta block): the Phase 148 golden stays byte-unchanged; this delta file is the committed, reviewable list Phase 153's FLAG_CAN_ERASE restoration produces on top of it."
  - "84 delta keys generated programmatically from golden+149-layer vs. live capture, never typed by hand -- avoids the |<i> positional-suffix rot risk the 149 file's own meta block already warns about."
  - "Kept the 149 layer's own exact-count assertion (== 18) as a true equality, not weakened into a floor, even though a second layer now exists alongside it."

requirements-completed: []
# ERASE-03 is NOT flipped here -- plans 09, 10, 11, 12, 13 also claim it and have not yet run.

coverage:
  - id: D1
    description: "Commit an 84-entry, non-vacuous, flags-only wire-value delta list for the FLAG_CAN_ERASE restoration, field-disjoint from the 18 Phase 149 deltas"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "generation-time asserts: 84 entries, single field {flags}, all keys present in golden with OLD value, 0 field collisions with the 149 layer, wire_dict_baseline.json/wire_dict_expected_deltas_149.json git-diff empty"
        status: pass
    human_judgment: false
  - id: D2
    description: "Extend the 746-chip wire-value equivalence gate to compose both delta layers, with new non-vacuity/exact-count/disjointness/failure-capability legs"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "tests/test_wire_dict_equivalence.py -o addopts=\"\" -q -- 7 passed"
        status: pass
      - kind: unit
        ref: "tests/ full suite -o addopts=\"\" -- 7 failed (owned by plans 09/10), 1801 passed"
        status: pass
    human_judgment: false
---

# Phase 153 Plan 08: Commit the 84-Record Wire-Value Delta and Extend the Equivalence Gate Summary

**Committed `wire_dict_expected_deltas_153.json` (84 flags-only, non-vacuous entries generated programmatically) and extended `test_wire_dict_equivalence.py` to compose it with the existing Phase 149 layer over the untouched Phase 148 golden, adding an exhaustive 746-row scope proof and a reachability proof.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-21T08:55:00Z
- **Tasks:** 2/2 completed
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

- **Task 1 — Generated and committed `wire_dict_expected_deltas_153.json`.** Derived programmatically:
  loaded the golden's `records`, applied the 149 delta layer to a deep copy, captured live wire dicts
  through the same `_capture_wire_dicts` shape the test module uses, and diffed. Confirmed exactly the
  measured shape from plan 07: **84 records changed, single field `flags`, old value `0` -> new value
  `2`** in every one. Wrote the file with sorted keys (stable diff) and a `meta` block naming `84`,
  `746`, `ERASE-03`, `flags`, the `convert_to_programmer` exclusion-tuple cause, and the algorithm-5/
  UV-EPROM absence as a scope proof. `wire_dict_baseline.json` and `wire_dict_expected_deltas_149.json`
  confirmed byte-unchanged (`git diff --stat` empty on both).
- **Task 2 — Extended the equivalence gate.** Renamed
  `test_live_capture_matches_golden_plus_the_149_deltas` to
  `test_live_capture_matches_golden_plus_the_149_and_153_deltas`, kept all four original assertions in
  place and in order (anti-laundering, 149 non-vacuity, 149 exact-count `== 18`, golden-plus-deltas
  equality — now composing both layers), and added three new assertions inline: 153 non-vacuity, 153
  exact-count `== 84`, and field-disjointness over the 18 shared keys (measured: `0` collisions).
  Added `test_exactly_84_records_change_flags_and_no_other_field_moves` (asserts the `746` total in
  the same test as the `84` subset, and that the changed-field union is exactly `{flags}`) and
  `test_the_153_delta_layer_is_capable_of_failing` (mutates one of the 84 records, reuses
  `_describe_record_diff`, asserts it names exactly that one record). Updated the module docstring's
  coverage list to describe all seven tests and record the never-re-capture / add-a-third-file
  guidance.
- **Full module result:** `pytest tests/test_wire_dict_equivalence.py -o addopts="" -q` — **7 passed**,
  verified on both the devcontainer's Python 3.12 and a `uv`-managed Python 3.11 (the app's actual CI
  target interpreter).
- **Full host suite result:** dropped from the inherited **8 failed, 1798 passed** to **7 failed, 1801
  passed** (1806 total) — the one test this plan owns is now green, no new failures introduced, and
  all three new/renamed tests count toward the `+3` passed delta. The remaining 7 failures are exactly
  the set plans 09 and 10 own (verified by name against plan 07's inherited-red-set table).
- **`ruff check`, `ruff format --check`** both pass on `firestarter/` and `tests/`.
- **mypy watermark:** `35 == 35` (unchanged) — verified on a `uv venv --python 3.11` per the
  documented devcontainer-3.12-fails-open workaround; the raw devcontainer 3.12 invocation fails with
  an unrelated numpy-stub syntax error (`Type statement is only supported in Python 3.12`), a
  pre-existing environment mismatch, not this plan's change.
- `firestarter/` sub-repo confirmed clean of tracked modifications (`git status --short` empty);
  `tools/check_dispatch.py` confirmed untouched (`git diff --quiet` holds).

## Task Commits

1. **Task 1: Generate and commit `wire_dict_expected_deltas_153.json`** - `efffc48` (feat, firestarter_app)
2. **Task 2: Extend the equivalence gate to compose both delta layers** - `abed8bd` (test, firestarter_app)

**Plan metadata:** pending (this commit)

## Files Created/Modified

- `firestarter_app/tests/golden/wire_dict_expected_deltas_153.json` — new: 84 non-vacuous `flags`-only
  delta entries (sorted keys) plus a `meta` decision block.
- `firestarter_app/tests/test_wire_dict_equivalence.py` — extended: `_DELTAS_153` path constant;
  renamed/extended the composed comparison test with three new assertions; two new tests (exhaustive
  scope proof, failure-capability proof); docstring coverage list updated to seven entries.

## Decisions Made

- Generated the 84 delta keys programmatically rather than transcribing them — same rationale the 149
  file's own `meta.provenance` already states (the `|<i>` positional suffix would silently rot under
  hand-transcription if any row is ever added or reordered).
- Kept the 149 layer's `== 18` assertion as a true equality (not widened to "at least 18") even after
  adding the second layer alongside it, per the plan's explicit instruction that it must not become a
  floor.
- Reused `_describe_record_diff` for the new failure-capability test rather than writing a parallel
  comparison, so no second implementation can mask a real regression in the production helper.

## Deviations from Plan

None - plan executed exactly as written. All measured figures (84 records, single field `flags`,
`0 -> 2`, 18-key overlap with 0 field collisions) matched plan 07's pre-measured shape exactly.

## Issues Encountered

- **Devcontainer Python is 3.12; `check_mypy_watermark.py` fails open under it** with the same
  pre-existing numpy-stub syntax error plan 07 documented (unrelated to this plan's diff — no source
  file this plan touches is in the mypy-strict scope, only test files). Worked around with the
  documented `uv venv --python 3.11` recipe (`UV_CACHE_DIR` set, `.[test]` installed) — confirmed
  `mypy errors: 35 (watermark: 35), OK` on the CI-target interpreter.
- No other issues.

## Known Stubs

None - this plan touches only a test fixture and a test module; no UI-facing or data-flow stubs.

## Threat Flags

None - no new network endpoint, auth path, file-access pattern, or schema change at a trust boundary.
All five threats in this plan's own register (T-153-40 through T-153-44) were addressed by the
assertions run above: T-153-40 by the exhaustive 746/84/`{flags}` scope proof; T-153-41 by the
preserved anti-laundering assertion plus the empty `git diff --stat` on both golden files; T-153-42 by
per-delta non-vacuity (asserted twice — at generation time and in the gate); T-153-43 by the observed-
discriminating failure-capability test; T-153-44 by the measured `0`-collision field-disjointness
assertion. T-153-45 (package installs) not applicable — no package was added.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The wire-value change ERASE-03 produces is now enumerated, reviewable, and provably scoped to
  exactly 84 records and one field; the Phase 148 golden survives a third phase without being
  re-captured.
- **Remaining inherited red set for plans 09 and 10** (7 tests, confirmed by a fresh full-suite run
  after this plan's commits):
  - `tests/test_chip_test.py::test_devtest01_0x0d_sweep_erase_is_na_and_erase_eprom_never_called` (10)
  - `tests/test_chip_test.py::test_count_applicable_sdp_gated_allow_chip_ratio_drops` (10)
  - `tests/test_chip_test.py::test_count_applicable_sdp_banner_row_renders_the_dropped_ratio` (10)
  - `tests/test_chip_test_blank_check_order.py::test_at28c256_blank_check_is_na_with_family_fact_reason` (10)
  - `tests/test_chip_test_sdp_leg.py::test_baseline_gate_closes_dead_write_path_allow_chip_full_leg` (10)
  - `tests/test_database_conversion.py::test_convert_at28c256_flash_eeprom_flag_can_erase_cleared` (09)
  - `tests/test_eprom_operations.py::TestSdpOperationsWireShape::test_sdp_command_flags_do_not_carry_the_db_can_erase_bit` (09)
- **ERASE-03 stays "In Progress"** in REQUIREMENTS.md/ROADMAP.md — plans 09, 10, 11, 12, 13 also claim
  it and have not yet run.
- No plan in waves 7-9 may cite a full green host suite; the host suite is intentionally red (7 tests
  now) until plan 16's sweep.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `efffc48` (Task 1 commit)
- FOUND: `abed8bd` (Task 2 commit)
- FOUND: `firestarter_app/tests/golden/wire_dict_expected_deltas_153.json`
- FOUND: `firestarter_app/tests/test_wire_dict_equivalence.py`
- FOUND: `.planning/phases/153-write-path-erase-policy/153-08-SUMMARY.md`
