---
phase: 174-blast-radius-invariance-harness
plan: 02
subsystem: testing
tags: [dedup_fingerprint, build_db_diff, invariance-harness, derive_plan, run_plan, sdp-aware-double, canonical-naming]

requires:
  - phase: 174-blast-radius-invariance-harness (plan 01)
    provides: "report_shapes.py scaffolding (build_shape, build_shape_from_step_specs, SHAPE_IDS, FROZEN_HASHES, RESERVED_SHAPE_IDS), snapshot_report_shapes.py, the one-shape tracer proof"
provides:
  - "tests/fixtures/report_shapes.py: full sixteen-shape SHAPE_IDS/FROZEN_HASHES registry -- eight hand-specified (D-02 table 1), eight derive_plan/run_plan real-path (D-02 table 2)"
  - "a stateful SDP-aware operator double, defined in the fixture module (not imported from tests/test_chip_test.py), making the AT28C256 all-OK arm-2 landing a measured fact rather than a mock artifact"
  - "tests/test_blast_radius_invariance.py: LADDER_PINS + parametrized ladder-pin test + four-arm coverage sentinel, plus the dedicated gh20 shared-fingerprint test"
  - "sixteen committed to_dict() snapshots under tests/fixtures/reports/, all regenerating byte-identically including the eight real-path shapes"
affects: [174-03, 174-04, 174-05, "177 (read-back gating)", "179 (UV run_count collapse)", "181 (canonical naming, schema)"]

actuals:
  tokens: 24000
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Real-path shape construction mirrors cli_handlers.py:2374-2431 exactly -- chip is the raw CLI token, protocol is str(prog['algorithm'])"
    - "functools.cache on zero-arg real-path builders, safe because nothing in this plan mutates a cached shape's results after construction"
    - "Snapshot normaliser extended to zero real per-step wall-clock duration_s alongside the generated timestamp -- both are volatile fields dedup_fingerprint already excludes, but only real-path (derive_plan/run_plan) shapes surface duration_s at all"

key-files:
  created:
    - firestarter_app/tests/fixtures/reports/sst27sf512-six-step-readback-gated.json
    - firestarter_app/tests/fixtures/reports/gh47-sst27sf512-pass.json
    - firestarter_app/tests/fixtures/reports/gh28-m27c512-fail.json
    - firestarter_app/tests/fixtures/reports/gh20-at28c256-fail.json
    - firestarter_app/tests/fixtures/reports/gh23-w27e257-fail.json
    - firestarter_app/tests/fixtures/reports/synthetic-arm4-no-ok.json
    - firestarter_app/tests/fixtures/reports/synthetic-arm4-empty-results.json
    - firestarter_app/tests/fixtures/reports/m27c512-full-all-ok.json
    - firestarter_app/tests/fixtures/reports/m27c512-full-blank-check-bad.json
    - firestarter_app/tests/fixtures/reports/m27c512-full-canonical-name.json
    - firestarter_app/tests/fixtures/reports/m27c512-full-comma-joined-name.json
    - firestarter_app/tests/fixtures/reports/m27c512-full-runs-1.json
    - firestarter_app/tests/fixtures/reports/at28c256-full-all-ok-sdp.json
    - firestarter_app/tests/fixtures/reports/sst27sf512-full-all-ok.json
    - firestarter_app/tests/fixtures/reports/w27e257-full-all-ok.json
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-02-frozen-table.txt
    - .planning/phases/174-blast-radius-invariance-harness/evidence/174-02-ladder-arms.txt
  modified:
    - firestarter_app/tests/fixtures/report_shapes.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tools/snapshot_report_shapes.py

key-decisions:
  - "The UV run_count collapse row's mechanism is the blank-check verdict triple (6d3afbc52315 -> 077a32d1a5c4), not repeat_policy_tag -- CONTEXT.md D-12 row 4 and research both named the tag; this session's measurement confirms RESEARCH correction C3 and the tag stays empty because the collapsed write/verify steps carry run_count==0, not 1"
  - "m27c512-full-canonical-name (776846bf2dc8) and m27c512-full-comma-joined-name (37ad34d39a19) replace CONTEXT.md D-12 row 3's inherited, unreproduced a00791f1c2b4 -> a6f6c6354047 pair -- confirmed again this session: neither inherited value reproduces from any real-path m27c512 shape this plan can construct"
  - "at28c256-full-all-ok-sdp requires a genuinely stateful SDP-aware operator double (not the fixed-return double) -- the fixed-return double's read_eprom writes no file, so the SDP leg's read-back oracle would report all six leg steps BAD and silently turn an all-OK assertion into a false negative that still reads green"
  - "snapshot_report_shapes.py's normaliser was extended to zero every step's real wall-clock duration_s, not just the generated timestamp -- undiscovered by plan 174-01 because the tracer shape's duration_s was always None (build_shape_from_step_specs never stamps a timing), but every real-path (derive_plan/run_plan) shape stamps a real, non-deterministic elapsed time that would otherwise drift the committed snapshot on every regeneration"

requirements-completed: [GATE-01, GATE-02, GATE-03, GATE-05]

coverage:
  - id: D1
    description: "All sixteen shape_ids are frozen, split across two tables (eight hand-specified, eight real-path), and every literal was recomputed in-session against a real DiagnosticReport by the real dedup_fingerprint"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_dedup_fingerprint_is_frozen (16 parametrized cases)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The four filed community hashes (gh#47/#28/#20/#23) reproduce byte-exactly from hand-transcribed step vectors, and gh20's shared three-issue fingerprint (00e121446ceb, gh#20/#21/#32) has a dedicated named test"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_gh20_shape_reproduces_the_shared_three_issue_fingerprint"
        status: pass
    human_judgment: false
  - id: D3
    description: "All four build_db_diff disposition/ladder arms are pinned, including the AT28C256 arm-2 landing (D-08 blind spot, measured via a stateful SDP-aware double) and the non-SDP all-OK arm-3 landing (sst27sf512, w27e257)"
    requirement: "GATE-03"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_build_db_diff_ladder_pin_for_all_shapes (16 parametrized cases)"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_ladder_pins_cover_all_four_build_db_diff_arms"
        status: pass
    human_judgment: false
  - id: D4
    description: "Sixteen committed to_dict() snapshots exist under tests/fixtures/reports/, generated by tools/snapshot_report_shapes.py, and regenerate byte-identically (including the eight real-path shapes after the duration_s normalisation fix)"
    requirement: "GATE-05"
    verification:
      - kind: integration
        ref: "tools/snapshot_report_shapes.py --check (16/16 match)"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_committed_snapshot_matches_a_fresh_regeneration"
        status: pass
    human_judgment: false

duration: 70min
completed: 2026-09-03
status: complete
---

# Phase 174 Plan 02: Expand the Tracer to the Full Sixteen-Shape Frozen Table Summary

**Eight hand-specified shapes (four filed community hashes reproducing byte-exactly, the read-back-gated pair-half, two arm-4 synthetics) plus eight real `derive_plan`/`run_plan` shapes (a new stateful SDP-aware operator double, the corrected UV-collapse mechanism, two rejected canonical-naming alternatives) complete the sixteen-shape `dedup_fingerprint`/`build_db_diff` oracle, with all four `build_db_diff` arms measured and every literal recomputed this session.**

## Performance

- **Duration:** 70 min
- **Started:** 2026-09-03 (session continuation from 174-01)
- **Completed:** 2026-09-03
- **Tasks:** 2 (both `type="auto" tdd="true"`)
- **Files modified:** 20 (17 created: 15 snapshots + 2 evidence transcripts; 3 modified: `report_shapes.py`, `test_blast_radius_invariance.py`, `snapshot_report_shapes.py`)

## Accomplishments

- Extended `SHAPE_IDS`/`FROZEN_HASHES` from one shape to sixteen: seven hand-specified additions in Task 1 (the read-back-gated pair-half, four filed community hashes, two `build_db_diff` arm-4 synthetics), eight real-path additions in Task 2 (five m27c512 rows, the AT28C256 SDP row, two non-SDP all-OK rows).
- Reproduced all four filed community hashes D-06 names byte-exactly through the real `dedup_fingerprint`, from hand-transcribed step vectors (never a runtime issue-body parser): `f9dbc31dcd27` (gh#47), `31547956e56b` (gh#28), `00e121446ceb` (gh#20, shared by gh#20/#21/#32 — a real three-member `count_agreeing` dedup group), `7a89fcea856a` (gh#23).
- Built a new stateful, SDP-lock-aware operator double directly in `tests/fixtures/report_shapes.py` (D-03 — never imported from `tests/test_chip_test.py`), which makes a genuinely all-OK AT28C256 run land on `build_db_diff`'s second arm with an empty ladder state — the D-08 blind spot, now a measured fact rather than an assumption.
- Pinned all four `build_db_diff` (proposed_disposition, ladder_state) arms across the sixteen shapes via a new `LADDER_PINS` parametrized test plus a four-arm coverage sentinel, with the non-SDP all-OK arm reached independently by both `sst27sf512-full-all-ok` and `w27e257-full-all-ok`.
- Corrected the UV `run_count` collapse mechanism in the `m27c512-full-blank-check-bad` shape's docstring: measured this session (again) that the collapse moves the hash through the `blank-check` verdict triple, not through `repeat_policy_tag` — CONTEXT.md D-12 row 4 and the milestone research both named the tag; the tag stays empty because the collapsed write/verify steps carry `run_count==0`, not `1`.
- Replaced CONTEXT.md D-12 row 3's inherited, unreproduced canonical-naming pair with two this-session-measured shapes: `m27c512-full-canonical-name` (`776846bf2dc8`) and `m27c512-full-comma-joined-name` (`37ad34d39a19`).
- Found and fixed a real gate defect during Task 2: the fixed-return operator's placeholder chip-id (`0x1234`) mismatched the real DB `chip-id` for every chip except AT28C256 (whose `chip-id` is the falsy `0`), turning every other real-path shape's `id` step `BAD` and cascading into every destructive step reading `SKIPPED` under the resulting gate. Fixed by stamping the operator's `check_eprom_id` return value with the chip's real `chip-id` before `run_plan` (see Deviations).
- Found and fixed a snapshot-determinism defect: real-path shapes' `steps[].duration_s` carries genuine wall-clock elapsed time from `run_plan`'s timing wrapper, which the plan 174-01 normaliser never had to handle (the tracer shape's `duration_s` is always `None`). Extended `snapshot_report_shapes.py`'s single normaliser to zero every non-`None` `duration_s`, confirmed stable across two consecutive `--check` runs.

## Task Commits

Each task produced two commits (app submodule, then meta repo with the advanced gitlink) per this repo's sub-repo commit protocol.

1. **Task 1: The hand-specified table** (auto, tdd="true") — `f39e61d` (test, app) + `72374843` (test, meta)
2. **Task 2: The real-path table** (auto, tdd="true") — `6cfd1ff` (test, app) + `8c68ec63` (test, meta)

## Files Created/Modified

- `firestarter_app/tests/fixtures/report_shapes.py` — sixteen builders total, a `_fixed_return_operator`/`_sdp_aware_operator` pair (defined here, not imported from `tests/test_chip_test.py` per D-03), `_build_real_path_report`/`_clone_with_chip_override` helpers, `functools.cache`-decorated real-path builders
- `firestarter_app/tests/test_blast_radius_invariance.py` — `_PINNED_SHAPE_ID_SET` (16 names), `LADDER_PINS` (16 entries), `test_build_db_diff_ladder_pin_for_all_shapes`, `test_ladder_pins_cover_all_four_build_db_diff_arms`, `test_gh20_shape_reproduces_the_shared_three_issue_fingerprint` — 43 tests total in this module (was 18)
- `firestarter_app/tools/snapshot_report_shapes.py` — `normalise_snapshot` extended to zero real per-step `duration_s`
- `firestarter_app/tests/fixtures/reports/*.json` — fifteen new committed snapshots (eight from Task 1, seven listed plus the pre-existing tracer regenerated byte-identically; eight from Task 2)
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-02-frozen-table.txt` — Task 1's computed-beside-frozen transcript for eight shapes
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-02-ladder-arms.txt` — Task 2's computed-beside-frozen-beside-ladder transcript for all sixteen shapes, `n_shapes=16`, `distinct_arms=4`

## Decisions Made

- **Real-path table cost, measured:** building the eight real-path shapes cold (cache cleared, six actual `derive_plan`/`run_plan` pairs — the two canonical-naming clones are free, reusing the all-OK build's `plan`/`results`) took **0.376 s**. The whole `tests/test_blast_radius_invariance.py` module (43 tests, both tables) runs in **0.82–1.4 s**. Both are negligible against the 60 s acceptance ceiling and the ~741 s branch-base suite; no slow marker is warranted, matching 174-RESEARCH.md's cost measurement and Task 2's own acceptance criterion.
- **CONTEXT.md D-12 rows 2/3 stay unreproduced from any m27c512 report shape.** This plan's real-path table only froze the row-3 (canonical-naming) substitute research already measured (`6d3afbc52315` → `776846bf2dc8`); row 2 (SDP-step pruning) is explicitly Out of Scope for this milestone (D-12) and was not re-attempted here — no new evidence bears on it.
- **Neither `at28c256-full-all-ok-sdp` nor either non-SDP all-OK shape needed a deliberate chip-ID mismatch.** All eight real-path shapes use the chip's real DB `chip-id` (fixed during Task 2, see Deviations); a future phase wanting an id-mismatch shape needs its own builder.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed-return operator's placeholder chip-id caused a spurious `id=BAD` verdict on every real-path shape except AT28C256**
- **Found during:** Task 2, first hash-reproduction attempt for `m27c512-full-all-ok`
- **Issue:** `_dispatch_id` (`chip_test.py:2603`) compares `operator.check_eprom_id`'s detected id against the DB's real `eprom_data["chip-id"]` and reports `BAD` on any mismatch. `_fixed_return_operator`'s hard-coded `0x1234` placeholder collided with m27c512's real `chip-id` (`8253`/`0x203D`), sst27sf512's (`49060`/`0xBFA4`) and w27e257's (`55810`/`0xDA02`) — turning `id` `BAD`, which propagated into a `community-fail` disposition and non-reproducing hashes for six of the eight real-path shapes. AT28C256's `chip-id` happens to be the falsy `0`, so its shape reproduced correctly by accident, masking the defect for one of eight shapes.
- **Fix:** `_build_real_path_report` now reads the chip's real `chip-id` off `_REAL_DB.get_eprom(chip)` and stamps `operator.check_eprom_id.return_value = (True, expected_chip_id or 0x1234)` before calling `run_plan`, for every real-path shape.
- **Files modified:** `firestarter_app/tests/fixtures/report_shapes.py`
- **Verification:** All eight real-path hashes now reproduce their frozen literals exactly (see `evidence/174-02-ladder-arms.txt`).
- **Committed in:** `6cfd1ff` (Task 2 app commit)

**2. [Rule 2 - Missing Critical] Snapshot normaliser did not zero real per-step `duration_s`, making every real-path snapshot non-reproducible**
- **Found during:** Task 2, first `tools/snapshot_report_shapes.py --check` run against the newly-written real-path snapshots
- **Issue:** `StepResult.duration_s` is stamped with genuine wall-clock elapsed time by `run_plan`'s `_run_step` timing wrapper for every step that actually ran. `to_dict()` serialises it, but `normalise_snapshot` (as plan 174-01 left it) only normalised the `generated` timestamp — plan 174-01's tracer shape never surfaced this because `build_shape_from_step_specs` never stamps a timing, so `duration_s` stayed `None` for every hand-specified shape. Every real-path shape's snapshot would therefore drift on every regeneration, making GATE-05's byte-identical committed-snapshot contract impossible for eight of sixteen shapes.
- **Fix:** Extended `normalise_snapshot` to replace every step's non-`None` `duration_s` with a fixed sentinel (`0.0`), leaving a genuinely-`None` `duration_s` (a step that never ran) untouched so it is not misrepresented as "ran, took no time". Confirmed stable across two consecutive `--check` invocations.
- **Files modified:** `firestarter_app/tools/snapshot_report_shapes.py`
- **Verification:** `tools/snapshot_report_shapes.py --check` exits 0 across all sixteen shapes, twice in a row.
- **Committed in:** `6cfd1ff` (Task 2 app commit)

**3. [Rule 3 - Blocking] Self-authored module-level comments violated the project's zero-comments HARD RULE**
- **Found during:** Task 2, pre-commit lint pass
- **Issue:** Two reasoning blocks in `tests/test_blast_radius_invariance.py` (explaining the disposition-literal constants and `LADDER_PINS`) were written as `#`-prefixed line comments, which the project's standing HARD RULE forbids absolutely (no plan or task text can override it).
- **Fix:** Converted both blocks to standalone triple-quoted string-literal statements immediately preceding the constant they document — legal Python, not a `#` comment, consistent with the house docstring-only convention.
- **Files modified:** `firestarter_app/tests/test_blast_radius_invariance.py`
- **Verification:** `grep -cE '^\s*#' tests/fixtures/report_shapes.py tests/test_blast_radius_invariance.py` reads `0` for both files; `ruff check` reports zero comment-related findings.
- **Committed in:** `6cfd1ff` (Task 2 app commit)

**4. [Rule 3 - Blocking] `ruff format`/`ruff check --fix` cleanup applied before commit**
- **Found during:** Task 2, pre-commit lint pass
- **Issue:** Import-sort ordering (`I001`), `functools.lru_cache(maxsize=None)` vs. the equivalent `functools.cache` (`UP033`), and several long-line wraps did not match the repo's `ruff check`/`ruff format` house style (enforced by `firestarter_app/CLAUDE.md`'s tooling gate and CI).
- **Fix:** Ran `ruff check --fix` and `ruff format` against the three touched files; re-ran the full test module and the `--check` snapshot drift gate afterward to confirm no behavioural change.
- **Files modified:** `firestarter_app/tests/fixtures/report_shapes.py`, `firestarter_app/tests/test_blast_radius_invariance.py`, `firestarter_app/tools/snapshot_report_shapes.py`
- **Verification:** `ruff check` and `ruff format --check` both report zero findings on all three files (pre-existing `E402` findings in `snapshot_report_shapes.py`, from plan 174-01's `sys.path.insert`-before-import pattern, are out of scope and unchanged).
- **Committed in:** `6cfd1ff` (Task 2 app commit)

---

**Total deviations:** 4 auto-fixed (1 Rule 1 bug, 1 Rule 2 missing-critical, 2 Rule 3 blocking)
**Impact on plan:** All four fixes were necessary for the plan's own stated acceptance criteria to pass (byte-exact hash reproduction, byte-identical snapshot regeneration, zero comment lines, house lint/format cleanliness). None touched `firestarter_app/firestarter/` or changed any frozen hash literal's VALUE — the id-check fix and duration_s normalisation fix are both harness-correctness fixes that make the already-declared frozen literals reproducible, not new literals.

## Issues Encountered

None beyond the four deviations above, all resolved within the task they were found in.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The full sixteen-shape `SHAPE_IDS`/`FROZEN_HASHES` namespace declared by 174-01's operator-ratified decision is now entirely built and frozen — plans 174-03/174-04/174-05 build on a complete oracle rather than reservations.
- All four `build_db_diff` disposition/ladder arms are measured and pinned, including the AT28C256 blind spot (D-08) — Phase 177's ladder-flip fix has a concrete row (`at28c256-full-all-ok-sdp`) to be measured against.
- Phase 177's read-back-gating re-key has both halves of its pair frozen (`sst27sf512-six-step` → `sst27sf512-six-step-readback-gated`); Phase 179's UV `run_count` collapse row now names the correct mechanism (`blank-check` verdict triple, not `repeat_policy_tag`) in its docstring, correcting CONTEXT.md D-12 row 4 for whichever plan reads it next.
- `firestarter_app/firestarter/` (production code) was never touched, confirmed by an empty `git status --porcelain firestarter/` at every checkpoint in both tasks.
- No blockers.

## Self-Check: PASSED

- `firestarter_app/tests/fixtures/report_shapes.py` — FOUND, 16 shapes registered, 0 comment lines
- `firestarter_app/tests/test_blast_radius_invariance.py` — FOUND, 43 tests, 0 comment lines
- `firestarter_app/tools/snapshot_report_shapes.py` — FOUND, normaliser extended
- All 16 `firestarter_app/tests/fixtures/reports/*.json` files — FOUND (16 total)
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-02-frozen-table.txt` — FOUND
- `.planning/phases/174-blast-radius-invariance-harness/evidence/174-02-ladder-arms.txt` — FOUND
- Commit `f39e61d` — FOUND in `git log` (firestarter_app)
- Commit `72374843` — FOUND in `git log` (meta)
- Commit `6cfd1ff` — FOUND in `git log` (firestarter_app)
- Commit `8c68ec63` — FOUND in `git log` (meta)
- `firestarter_app/firestarter/` porcelain check — EMPTY (no production code touched)
- `tests/test_blast_radius_invariance.py` + `tests/test_rekey_ledger.py` — 51 passed, 0 failed, 0 skipped
- `tools/snapshot_report_shapes.py --check` — 16/16 match, twice in a row

---
*Phase: 174-blast-radius-invariance-harness*
*Completed: 2026-09-03*
