---
phase: 153-write-path-erase-policy
plan: 07
subsystem: database
tags: [python, database.py, flag-derivation, erase-policy, host]

# Dependency graph
requires:
  - phase: 153-03
    provides: "CMD_ERASE dispatch arm in configure_eeprom28c (firmware), AN-0544B software six-byte erase"
  - phase: 153-06
    provides: "algorithm-5 pre-write blank check deleted from flash_5v_page_write_init"
provides:
  - "FLAG_CAN_ERASE restored on the wire for all 84 algorithm-13 rows"
  - "Corrected Phase 121 D-12 comment block (fourth recorded reversal in the 119/120/121/153 chain)"
  - "Exact 8-test inherited-red set, each assigned to its owning plan (08/09/10)"
  - "Measured post-change count_applicable figures (m_applicable=10, n_ran=6) for plan 10"
  - "Measured wire-dict delta shape (84 rows, flags-only, 0->2) for plan 08"
affects: [153-08, 153-09, 153-10, 153-11, 153-12, 153-13]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Reversal-record voice: mechanism-corrected / intent-satisfied, never framed as failure"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/database.py

key-decisions:
  - "Algorithm 5 stays excluded from FLAG_CAN_ERASE (live hardware-hazard reason, unrelated to algorithm 13's now-retired reason); only 13 is dropped from the tuple."
  - "chip_database.json is not touched -- flag is derived at conversion time, confirmed byte-unchanged."
  - "Both false claims in the Phase 121 D-12 comment (no erase operation at all; firmware never reads the flag) are corrected in place, in the project's reversal-record voice, citing D-153-05, ERASE-03, eprom_operations.cpp."

requirements-completed: [ERASE-07]
# ERASE-03 is NOT flipped here -- plans 08, 09, 10, 11, 12, 13 also claim it and have not yet run.

coverage:
  - id: D1
    description: "Drop algorithm 13 from the FLAG_CAN_ERASE exclusion tuple at database.py:617; algorithm 5 stays excluded"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "python3 -c \"AT28C256 flags=0x2, W29C040 flags=0x0, M27C512 flags=0x0\""
        status: pass
      - kind: unit
        ref: "tests/ full suite -o addopts=\"\" -- exactly 8 named failures, 1798 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "Rewrite the Phase 121 D-12 comment block correcting both now-false claims (ERASE-07)"
    requirement: "ERASE-07"
    verification:
      - kind: unit
        ref: "grep -c 'has no erase operation at' database.py == 0"
        status: pass
      - kind: unit
        ref: "grep -c 'never reads FLAG_CAN_ERASE' database.py == 0"
        status: pass
      - kind: unit
        ref: "grep -c 'hardware-damage hazard' database.py >= 1 (algorithm-5 rationale preserved)"
        status: pass
      - kind: unit
        ref: "tests/test_database_conversion.py -o addopts=\"\" -- exactly the one expected pre-existing failure, no new failures from the comment edit"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 07: Restore FLAG_CAN_ERASE for Algorithm 13 and Correct the D-12 Comment Summary

**One-line, one-character-class change (`algo not in (5, 13)` -> `(5,)`) that flips the wire capability flag on all 84 algorithm-13 rows, plus a full rewrite of the Phase 121 D-12 comment block recording this as the fourth reversal in the 119/120/121/153 chain.**

## Performance

- **Duration:** ~40 min
- **Completed:** 2026-08-21T08:38:08Z
- **Tasks:** 2/2 completed
- **Files modified:** 1 (`firestarter_app/firestarter/database.py`)

## Accomplishments

- **Task 1 — Dropped algorithm 13 from the exclusion tuple** (`database.py:617`, confirmed
  correct line by direct grep — the ROADMAP/REQUIREMENTS' cited `:621` is the `simple_flags |=`
  body, not the edit site). `algo not in (5, 13)` became `algo not in (5,)`. Algorithm 5 remains
  excluded for its own, unrelated, still-valid hardware-hazard reason (setting the flag for 0x05
  would route `flash4_write_init` into `flash4_erase_execute`, asserting `CTRL_VPP_REGULATOR_ENABLE`
  — 12 V — on a 5 V-only part).
- **Measured the exact wire effect:** `AT28C256` (algorithm 13) now converts with `flags=0x2`
  (`FLAG_CAN_ERASE` set); `W29C040` (algorithm 5) and `M27C512` (UV-EPROM, non-EEPROM
  electrical-type) both still convert with `flags=0x0`. `chip_database.json` is byte-unchanged
  (`git diff --stat` empty) — no entry carries a `flags` key, so nothing there needed touching.
- **Ran the full host suite** (`python3 -m pytest tests/ -o addopts="" -q`) twice — once
  immediately after Task 1's tuple edit, and once again after Task 2's comment rewrite — and got
  the **identical eight named failures** both times, with `1798 passed` and no others. This
  matches the planner's pre-measured set exactly; no ninth failure, no missing failure.
- **Task 2 — Rewrote the Phase 121 D-12 comment block.** Split into a clean two-commit sequence
  (tuple-only, then comment-only) by temporarily reverting the comment text before the first
  commit and reapplying it before the second, so each commit's diff is scoped to exactly one
  task. The rewrite:
  - Removes both now-false claims (verified by negative grep, both `0`): that
    `configure_eeprom28c` "has no erase operation at all," and that the `0x0D` firmware path
    "never reads FLAG_CAN_ERASE."
  - States the corrected facts with citations: Phase 153 (ERASE-03/ERASE-04) added a real
    `CMD_ERASE` dispatch arm implementing the AN-0544B software six-byte erase; `eprom_operations.cpp`'s
    `eprom_erase()` precondition does read `FLAG_CAN_ERASE` (the standalone `erase` command's own
    refusal gate).
  - Restates D-153-05 at the host site: no `FLAG_CAN_ERASE`-gated erase block was added to
    `eeprom28c_write_init`, and `erase` was not added to `write`'s `FLAG_SKIP_SDP_UNLOCK` auto-set
    path — restoring the flag does not make `write` erase implicitly.
  - Preserves the algorithm-5 hardware-hazard rationale verbatim in substance (`hardware-damage
    hazard` grep count 1) — a live, unrelated argument, not touched by this reversal.
  - Frames the correction as the **fourth recorded reversal** in the chain (119 D-18, 120 D-20,
    121 D-12, now 153), in the project's mechanism-corrected / intent-satisfied voice, matching
    `configure_eeprom28c`'s own LOCK-04 precedent comment and `eeprom28c_write_execute`'s D-06 comment
    in `firestarter/src/proms/eeprom_28c.cpp`.
  - Carries forward D-12's blast-radius note in corrected form (no `chip_database.json` `flags`
    key at risk; the only other host reader is `serial_comm.py`'s DEBUG-only logging) and records
    the one benign behavioural delta (`firestarter erase` on a `0x0D` part now performs a real
    erase instead of being refused one layer earlier).
  - Records the plan-shape consequence (erase becomes a supported destructive step on all 84
    rows; blank-check moves to sit after it) so it is not later mistaken for a surprise.

## Task Commits

1. **Task 1: Drop 13 from the exclusion tuple** - `403dc74` (feat)
2. **Task 2: Rewrite the Phase 121 D-12 comment block (ERASE-07)** - `6c9b91e` (docs)

**Plan metadata:** pending (this commit)

## Files Created/Modified

- `firestarter_app/firestarter/database.py` — `convert_to_programmer`'s `FLAG_CAN_ERASE`
  exclusion tuple (`(5, 13)` -> `(5,)`) and the surrounding Phase 121 D-12 comment block rewritten
  as the fourth recorded reversal.

## Decisions Made

- Algorithm 5 stays excluded; only algorithm 13 is dropped. The two exclusions were always for
  unrelated reasons (hardware-hazard vs. now-corrected false-capability), and the code comment now
  says so explicitly.
- `chip_database.json` was not touched — confirmed unnecessary and confirmed untouched
  (`git diff --stat` empty). No generator/decode-function change was needed for this plan.
- Split the single logical diff into two commits (tuple, then comment) by staging the file in two
  passes, so the task-commit granularity in the plan is honored even though both tasks touch the
  same file region.

## Inherited Red Set (for plans 08, 09, 10)

Exactly these eight tests are RED as of this plan's final commit, measured twice (after Task 1 and
again after Task 2, identical both times). **No ninth failure occurred; none of the eight were
absent.** This is the deliberate observed-RED baseline plans 08–10 invert; per this plan's
`<verification>` note, no plan in waves 7–9 may cite a full green host suite.

| # | Test | Owning plan |
|---|------|-------------|
| 1 | `tests/test_chip_test.py::test_devtest01_0x0d_sweep_erase_is_na_and_erase_eprom_never_called` | 10 |
| 2 | `tests/test_chip_test.py::test_count_applicable_sdp_gated_allow_chip_ratio_drops` | 10 |
| 3 | `tests/test_chip_test.py::test_count_applicable_sdp_banner_row_renders_the_dropped_ratio` | 10 |
| 4 | `tests/test_chip_test_blank_check_order.py::test_at28c256_blank_check_is_na_with_family_fact_reason` | 10 |
| 5 | `tests/test_chip_test_sdp_leg.py::test_baseline_gate_closes_dead_write_path_allow_chip_full_leg` | 10 |
| 6 | `tests/test_database_conversion.py::test_convert_at28c256_flash_eeprom_flag_can_erase_cleared` | 09 |
| 7 | `tests/test_eprom_operations.py::TestSdpOperationsWireShape::test_sdp_command_flags_do_not_carry_the_db_can_erase_bit` | 09 |
| 8 | `tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden_plus_the_149_deltas` | 08 |

Full suite result both runs: **8 failed, 1798 passed** (1806 total).

## Measured Figures for Later Plans

- **AT28C256 gated-allow leg** (`write_scope="full"`, `_gated_allow_operator()`): pre-change
  `m_applicable=9, n_ran=5` (measured/pinned in `tests/test_chip_test.py`'s
  `test_count_applicable_sdp_gated_allow_chip_ratio_drops` docstring); **post-change
  `m_applicable=10, n_ran=6`** — this is the same pair the docstring records as the pre-260807-kaq
  historical value, now restored because algorithm 13's blank-check is once again a real (not
  NA-by-family-fact) step ahead of a real erase.
- **Wire-dict delta shape** (`tests/test_wire_dict_equivalence.py`'s golden-vs-live diff): **exactly
  84 records changed**, the changed field is **`flags` only**, and the value moves from **`0` to
  `2`** in every one of them. No other field on any of the 746 rows changed.

## Deviations from Plan

None - plan executed exactly as written. All eight measured downstream failures matched the
planner's pre-computed list exactly, in both count and identity, across two independent full-suite
runs (once after Task 1, once after Task 2).

## Issues Encountered

- **Devcontainer Python is 3.12; `check_mypy_watermark.py` fails open under it** with a numpy stub
  syntax error (`Type statement is only supported in Python 3.12 and greater`) unrelated to this
  plan's change (a pre-existing environment mismatch, per project memory:
  `reference_devcontainer_py312_masks_ci_py39`). Worked around per the documented recipe: created a
  `uv venv --python 3.11` (with `UV_CACHE_DIR` set), installed `.[test]` into it, and re-ran the
  gate there — **`mypy errors: 35 (watermark: 35)` — OK, exit 0**. The single mypy error present
  (`database.py:291`, an unrelated pre-existing `list[int]`/`int` assignment issue far from this
  plan's edit site at lines 578-622) predates this plan's diff, confirmed by `git diff -U0` showing
  no touch to line 291. This run used **Python 3.11**, matching the app's CI target; the raw
  devcontainer 3.12 `mypy` invocation is a different, known-unreliable scope and was not used to
  gate this plan.
- No other issues. `ruff check` and `ruff format --check` passed cleanly on the devcontainer's
  default interpreter both times.

## Known Stubs

None - no new UI-facing or data-flow stubs introduced. This plan touches only a flag-derivation
tuple and its surrounding comment.

## Threat Flags

None - no new network endpoint, auth path, file-access pattern, or schema change at a trust
boundary was introduced. The change stays inside the plan's declared threat register (T-153-34
through T-153-39), all of which were addressed by the criteria already run above (algorithm-5
non-regression confirmed by direct conversion check; both negative greps at 0; `chip_database.json`
byte-unchanged; the eight-failure set confirmed exact; no package installed).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `FLAG_CAN_ERASE` is restored on the wire for all 84 algorithm-13 rows; the Phase 121 D-12 comment
  no longer makes either false claim.
- Plans 08, 09, and 10 have their exact inherited-red set, each test's owning plan named, and the
  two measured figures (`m_applicable=10`/`n_ran=6`; 84-row wire-dict delta) they need without
  re-deriving them.
- **ERASE-03 stays "Pending"** in REQUIREMENTS.md/ROADMAP.md — it is claimed by six plans in this
  phase and only flips once the exhaustive assertion (plan 12) and the downstream inversions
  (08/09/10) land. **ERASE-07 is flipped to complete** by this plan, since it is the sole owner.
- The host suite is intentionally RED (8 tests) until plan 16's sweep; this is expected and
  documented, not a regression to chase.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `403dc74` (Task 1 commit)
- FOUND: `6c9b91e` (Task 2 commit)
- FOUND: `firestarter_app/firestarter/database.py`
- FOUND: `.planning/phases/153-write-path-erase-policy/153-07-SUMMARY.md`
