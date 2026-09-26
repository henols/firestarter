---
phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated
plan: 02
subsystem: dev-test-engine
tags: [uv-eprom, blast-radius-invariance, rekey-ledger, frozen-corpus, firestarter_app]

requires:
  - phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated (plan 01)
    provides: FLAG_SKIP_BLANK_CHECK on a proven monotonic UV masked write, the SKIPPED blank-check verdict adjudication, and WriteInitPreflightChip -- the pieces this plan's frozen shape and re-key declaration are built on
provides:
  - "the frozen corpus's first shape exercising a real UV masked slot write (uv-slot-write-pass), reaching overall_verdict PASS with write/verify run_count == 2 -- the machine-checked host-side form of ROADMAP criteria 1 and 2"
  - "the RK-174-04-p179-uv-blank-check-abort declared re-key, bound across firestarter_app and .planning/MILESTONES.md, closing the one gate 179-01 deliberately left RED"
  - "RESERVED_SHAPE_IDS drawn down to empty, with the reservation namespace's emptiness asserted rather than left to iterate silently over zero rows"
affects: [179-03-committed-uv-slot-write-test, 179-04-bench-wave-and-requirement-marking]

actuals:
  tokens: 8345
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "eight-site frozen-shape registration landed in ONE commit, because SHAPE_IDS = tuple(sorted(_BUILDERS)) makes any partial state red by construction (Phase 174/177/178 precedent, reused verbatim)"
    - "declared re-key as a SEPARATE commit from the behaviour-change/registration commit, per .planning/MILESTONES.md's D-11 protocol -- the re-key is a reviewable unit, not a test repaired inside the commit that broke it"
    - "an emptied reservation frozenset gets an explicit `== frozenset()` assertion plus an unregistered-sentinel probe, rather than leaving a `for x in EMPTY_SET` loop to pass silently over zero iterations"

key-files:
  created: []
  modified:
    - firestarter_app/tests/fixtures/report_shapes.py
    - firestarter_app/tests/fixtures/shape_ids.json
    - firestarter_app/tests/fixtures/reports/uv-slot-write-pass.json (new)
    - firestarter_app/tests/fixtures/reports/m27c512-full-blank-check-bad.json
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/fixtures/rekey_ledger.py
    - .planning/MILESTONES.md
    - .planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-DECISIONS.md (new)

key-decisions:
  - "D-179-1 (operator-answered checkpoint:decision): criterion 4 is satisfied by a SPLIT -- a committed firmware-faithful-double regression (plan 179-03, no skip marker) plus a blocking-human bench wave producing a committed 179-MEASUREMENT.md (plan 179-04), per the Phase 176-05 precedent. Neither artifact alone is criterion 4."
  - "D-179-2 (operator-answered checkpoint:decision): uv-slot-write-pass is built real-path -- _build_real_path_report with a WriteInitPreflightChip seeded outside the top write slot -- so the frozen hash is of what the engine actually produces, accepting the derive_plan/chip_database.json coupling every other real-path shape already has."
  - "The re-baselined m27c512-full-blank-check-bad hash and its LADDER_PINS move are MEASURED this session against the committed builder, never transcribed from 179-RESEARCH.md's MEDIUM-confidence projections or this plan's own earlier monkeypatched pre-measurement."

requirements-completed: []

coverage:
  - id: D1
    description: "The frozen corpus gains uv-slot-write-pass -- the first shape exercising a real UV masked slot write, reaching overall_verdict PASS with write/verify run_count == 2 and a masked, probe-read write_target"
    requirement: "UV-02"
    verification:
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-02-shape-registration.txt (new_bc_verdict=SKIPPED, new_write_verdict=OK, new_write_run_count=2, new_verify_run_count=2, new_overall=PASS, new_target_masked=True, new_target_probe=True, new_hash_frozen_matches=True)"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py -- 100 passed (full module) after registration"
        status: pass
    human_judgment: false
  - id: D2
    description: "uv-slot-write-pass registered across all eight gate-enforced sites in one commit; the corpus carries 19 frozen shapes and 19 matching generated snapshots; all 17 other FROZEN_HASHES entries reproduce byte-unmoved"
    verification:
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-02-shape-registration.txt (shape_count=19, pinned_set_matches=True, anchor_matches=True, inherited_drifted=, OK: 19 snapshot(s) match)"
        status: pass
    human_judgment: false
  - id: D3
    description: "RESERVED_SHAPE_IDS drawn down to empty, with the emptiness explicitly asserted and build_shape's KeyError property kept alive by an unregistered sentinel probe -- no read site silently vacuous"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_build_shape_raises_for_every_reserved_shape_id"
        status: pass
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-02-shape-registration.txt (reserved_left=)"
        status: pass
    human_judgment: false
  - id: D4
    description: "m27c512-full-blank-check-bad re-baselined to its measured post-179-01 value; its LADDER_PINS pair moves community-fail -> community-reported, verified against a live build_db_diff; all four build_db_diff arms stay populated"
    verification:
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-02-shape-registration.txt (rebaselined_frozen_matches=True, rebaselined_moved_off_before=True, ladder_mismatches=, ladder_distinct=4)"
        status: pass
    human_judgment: false
  - id: D5
    description: "RK-174-04-p179-uv-blank-check-abort declared in a SEPARATE commit from the registration -- after_hash filled with the measured value, before_hash untouched, no other row declared, bound to .planning/MILESTONES.md in the same logical step"
    requirement: "UV-01"
    verification:
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-02-rekey-declaration.txt (rk04_after_matches_frozen=True, rk04_before_untouched=True, other_declared names only the four pre-existing declared rows, OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The tree is green again: full suite >= 2242 tests, 0 failures, 32 snapshots passed"
    verification:
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-02-rekey-declaration.txt (2253 passed, 32 snapshots passed, 0 failed)"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-09-06
status: complete
---

# Phase 179 Plan 02: Re-Key Declaration and Frozen-Shape Registration Summary

**The blast-radius invariance harness's tree is green again: `uv-slot-write-pass` is registered as the corpus's first real UV masked-slot-write shape (measured hash `927571e5110f`, `overall_verdict == PASS`, `run_count == 2`), `m27c512-full-blank-check-bad` is re-baselined to its measured post-179-01 value (`e42f1567967a`), and `RK-174-04-p179-uv-blank-check-abort` is declared in a separate commit bound across both repositories.**

## Performance

- **Duration:** 40 min (approx; continuation executor resuming a mid-flight checkpoint, exact wall-clock not independently tracked)
- **Started:** 2026-09-06 (continuation dispatch, resuming after the operator's checkpoint:decision answer)
- **Completed:** 2026-09-06T21:03:26Z
- **Tasks:** 3
- **Files modified:** 8 (5 in `firestarter_app`, 3 in the meta repo, one new each)

## Accomplishments

- `D-179-1` and `D-179-2` recorded in `179-DECISIONS.md`, resolving Task 1's `checkpoint:decision` per the operator's answer relayed in this continuation's dispatch: both take this plan's recommended Option A.
- `_build_uv_slot_write_pass()` (new): a `WriteInitPreflightChip` at the `m27c512` memory size read off `_REAL_DB`, seeded with content at `[0x0000:0x0100]` -- outside `uv_slot_starts`' top-down first slot -- run through `_build_real_path_report(chip="m27c512", write_scope="full", runs=2)`. Measured: `blank-check` verdict `SKIPPED`, `write`/`verify` verdict `OK` with `run_count == 2`, `overall_verdict == PASS`, `write_target.masked == True` with `current_source` starting `"probe read (tranche"`.
- All eight gate-enforced sites updated in one commit: `_BUILDERS`, `FROZEN_HASHES` (new entry `927571e5110f`, re-baselined `m27c512-full-blank-check-bad` to `e42f1567967a`), `RESERVED_SHAPE_IDS` (now empty), `LADDER_PINS` (new entry plus the forced `m27c512-full-blank-check-bad` move to `community-reported`), `_PINNED_SHAPE_ID_SET`, `tests/fixtures/shape_ids.json`, and the two generated snapshots (`uv-slot-write-pass.json` new, `m27c512-full-blank-check-bad.json` regenerated). All 17 other `FROZEN_HASHES` entries reproduce byte-unmoved.
- `test_build_shape_raises_for_every_reserved_shape_id` repaired to assert `RESERVED_SHAPE_IDS == frozenset()` explicitly and probe an unregistered sentinel string, so the now-empty-set loop no longer silently passes over zero iterations.
- `RK-174-04-p179-uv-blank-check-abort` declared in a **separate** commit (per the D-11 protocol): `after_hash` filled with the measured `e42f1567967a`, `before_hash` untouched at `077a32d1a5c4`, the provenance note corrected to record the actual mechanism (`BAD -> SKIPPED`, not the seeded `OK -> BAD`) and the falsification of `PITFALLS.md:186-188`'s claimed abort mechanism. `.planning/MILESTONES.md`'s bound row updated in the same logical step; `tools/rekey/check_rekey_ledger.py` prints `OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound`.
- Full suite green again: **2253 passed, 0 failed, 32 snapshots passed** (was 5 failed at the end of 179-01's deliberate red).

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule (branch `gsd/v1.36-dev-test-fidelity`), with the meta repo's gitlink advanced in the same logical step:

1. **Task 1: The two calls no CONTEXT.md makes** - decisions recorded in `179-DECISIONS.md`, committed as part of Task 2's meta commit (no code change of its own).
2. **Task 2: Re-baseline the one moved shape and register the last reserved id** - `b35481c` (feat, firestarter_app) / `3d8bfd73` (feat, meta gitlink + decisions + evidence)
3. **Task 3: Declare RK-174-04** - `c090ce9` (test, firestarter_app) / `7232aacb` (test, meta gitlink + MILESTONES.md + evidence)

**Plan metadata:** committed separately (this SUMMARY.md + STATE.md).

## Files Created/Modified

- `firestarter_app/tests/fixtures/report_shapes.py` - `_build_uv_slot_write_pass`, its `_BUILDERS`/`FROZEN_HASHES`/`RESERVED_SHAPE_IDS` entries, the module docstring repair
- `firestarter_app/tests/fixtures/shape_ids.json` - committed sorted anchor, 18 -> 19 entries
- `firestarter_app/tests/fixtures/reports/uv-slot-write-pass.json` - generated snapshot (new)
- `firestarter_app/tests/fixtures/reports/m27c512-full-blank-check-bad.json` - regenerated snapshot
- `firestarter_app/tests/test_blast_radius_invariance.py` - `LADDER_PINS`/`_PINNED_SHAPE_ID_SET` at 19 entries, the re-pinned `m27c512-full-blank-check-bad` ladder pair, the de-vacuumed reserved-name test
- `firestarter_app/tests/fixtures/rekey_ledger.py` - `RK-174-04-p179-uv-blank-check-abort` declared, provenance note corrected
- `.planning/MILESTONES.md` - `RK-174-04-p179-uv-blank-check-abort` row's `after`/`declared`/`change` cells updated (scoped edit)
- `.planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-DECISIONS.md` - `D-179-1`, `D-179-2` (new)
- `.planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-02-shape-registration.txt`, `179-02-rekey-declaration.txt` - measured evidence (new)

## Decisions Made

See `key-decisions` in frontmatter. Both `D-179-1` and `D-179-2` were the operator's answer to Task 1's `checkpoint:decision`, relayed via this continuation dispatch rather than an interactive prompt in this session -- both took the plan's own recommended Option A, so Tasks 2/3 and plan `179-03` follow their default branches; the plan's inline Option B/C alternate edits were not taken.

## Deviations from Plan

None - plan executed exactly as written. The plan's own construction for `_build_uv_slot_write_pass` (`_REAL_DB.get_eprom("m27c512")` memory size, seeding `[0x0000:0x0100]`, `_build_real_path_report(..., runs=2)`) measured to the exact acceptance criteria on the first attempt: `blank-check=SKIPPED`, `write`/`verify=OK` at `run_count=2`, `overall=PASS`, `masked=True`, `current_source` starting `"probe read (tranche"`.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `RESERVED_SHAPE_IDS` is empty; the corpus carries 19 frozen shapes and 19 matching snapshots; `uv-slot-write-pass`'s builder, hash and step shape are available for plan `179-03`'s committed regression module (`tests/test_chip_test_uv_slot_write.py`) to build on directly.
- `RK-174-04` is declared and bound; the blast-radius invariance harness and the rekey ledger tests are both fully green.
- `D-179-1`'s split is now the record: plan `179-03` still owes the committed firmware-faithful-double regression test (no skip marker), and plan `179-04` still owes the `blocking-human` bench wave and the committed `179-MEASUREMENT.md`. Per the shared-ID gate, `UV-01` and `UV-02` are correctly NOT yet marked complete in `REQUIREMENTS.md` -- `requirements.ready-ids` reports `0/2 requirement(s) ready to mark complete` because sibling plans `179-03`/`179-04` (which also declare them) have not yet produced a SUMMARY.
- No blockers for `179-03`. The bench wave (`179-04`) still needs the operator's ST M27C512 confirmed on hand, per `179-RESEARCH.md`'s Q6/A1 (unchanged from `179-01`'s note).

## Self-Check: PASSED

- `firestarter_app/tests/fixtures/report_shapes.py` exists and contains `_build_uv_slot_write_pass`: confirmed.
- `firestarter_app/tests/fixtures/rekey_ledger.py` contains `"e42f1567967a"` in the `RK-174-04` row: confirmed.
- `.planning/MILESTONES.md`'s `RK-174-04-p179-uv-blank-check-abort` row carries `e42f1567967a` / `2026-09-06`: confirmed.
- Commits `b35481c`, `c090ce9` (firestarter_app) and `3d8bfd73`, `7232aacb` (meta) all found in `git log --oneline --all`.
- All `<acceptance_criteria>` for Tasks 1-3 re-verified against fresh evidence files this session; all pass.
- Plan-level `<verification>` items 1-6 re-run this session: full suite `2253 passed, 32 snapshots passed`; `snapshot_report_shapes.py --check` reports `OK: 19 snapshot(s)`; `check_rekey_ledger.py` reports `OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound`; ruff/mypy/`check_devtest_orchestrator.py`/`check_diagnostic_report_claims.py` all exit 0; `git diff --quiet -- firestarter/` holds across both `firestarter_app` commits; zero added `#` comment lines; both submodules porcelain-clean.

---
*Phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated*
*Completed: 2026-09-06*
