---
phase: 153-write-path-erase-policy
plan: 10
subsystem: testing
tags: [python, pytest, erase-policy, dev-test, chip_test, sdp]

# Dependency graph
requires:
  - phase: 153-07
    provides: "FLAG_CAN_ERASE restored on the wire for all 84 algorithm-13 rows at the source (database.py's exclusion tuple)"
provides:
  - "Two corrected `chip_test.py` reason texts (constant comment + arm reason string) that no longer claim the 28C family has no erase operation"
  - "The `_PROTOCOL_EEPROM_28C` arm kept as a documented, tested defensive fallthrough for a user-override non-qualifying-electrical-type row, rather than deleted"
  - "The `dev test` sweep leg inverted to a positive `erase_eprom` call assertion, with the multi-run call-count (2, not 1) recorded as a MEASURED DISCREPANCY against the plan's own prescribed assertion"
  - "Third-generation M/N accountings (m_applicable=10, n_ran=6) for the count/banner/baseline-gate legs, all live-derived in this session"
  - "The AT28C256 blank-check placement case moved to the exact measured index (5, after erase at 4) with ordering assertions, sharing case 1's placement while keeping case 3's verdict"
  - "Full host suite (1811 tests) confirmed green"
affects: [153-11, 153-12, 153-13, 153-16]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "MEASURED DISCREPANCY convention extended to a plan's own prescribed assertion, not just prior generations' figures -- when live measurement contradicts a specific plan instruction, the honest resolution is the accurate assertion plus a recorded divergence, never a forced-to-pass literal"
    - "Third-generation accounting docstrings carry all three generations' figures visibly, plus an explicit integer-coincidence caveat when a later generation's numbers happen to match an earlier one for unrelated reasons"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py
    - firestarter_app/tests/test_chip_test_blank_check_order.py

key-decisions:
  - "The plan's own text prescribed `erase_eprom.assert_called_once()` for the inverted sweep leg. Live-measured against `run_plan`'s actual dispatch, `OP_ERASE` is a member of `_MULTI_RUN_OPS` (the write/erase/verify N=2 disagreement-policy set) and is genuinely called twice under `run_plan`'s default `runs=2` -- exactly like write and verify already are. Asserting `assert_called_once()` would be false on this codebase; used `assert_called()` plus an explicit `call_count == 2` instead, and recorded the divergence in the docstring rather than forcing the plan's literal text to pass."
  - "The `_PROTOCOL_EEPROM_28C` constant and its arm are kept, not deleted, per the plan's disposition -- reachable only for a `0x0D` row whose `electrical-type` falls outside {\"EEPROM\", \"Flash/EEPROM\"}. A reachability leg (`test_protocol_eeprom_28c_arm_reachable_for_non_qualifying_etype`) proves this using a database-double subclass mirroring `tests/fixtures/synthetic_nonzero_chip_id.py`'s shape, rather than leaving the arm as untested dead code."
  - "Ruff's `select` list (E/F/I/UP) was checked, not assumed, to confirm it does not flag an unused module-level constant (F401 is unused-import-only) -- recorded in the kept constant's own comment."

requirements-completed: []
# ERASE-03 is NOT flipped here -- plans 11, 12, 13 also claim it and have not yet run.

coverage:
  - id: D1
    description: "Correct the two chip_test.py reason texts (constant comment + arm reason string) and keep the _PROTOCOL_EEPROM_28C arm as a documented defensive fallthrough, with no logic change to the three coupled expressions"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/firestarter/chip_test.py -- grep -c 'has no erase operation' returns 0; ruff check/format + mypy watermark (35==35) pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "Invert the dev-test sweep leg to a positive erase_eprom call assertion, re-measure the two count_applicable/banner legs to m_applicable=10/n_ran=6 with third-generation accountings, and add a reachability leg for the defensive fallthrough arm"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py -o addopts=\"\" -q -- 110 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Re-measure the SDP-leg baseline-gate accounting (n_ran=6, m_applicable=10, third generation) and move the AT28C256 blank-check placement assertion to the exact measured index with ordering relations, leaving the two negative controls untouched"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test_sdp_leg.py tests/test_chip_test_blank_check_order.py -o addopts=\"\" -q -- 80 + 5 passed; combined 4-module run + test_database_conversion.py -- 215 passed; full host suite -- 1811 passed"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 10: Absorb the `dev test` Erase Plan-Shape Change and Correct Reason Texts Summary

**Corrected the two `chip_test.py` reason texts that falsely claimed the 28C family has no erase operation, kept the now-unreachable `_PROTOCOL_EEPROM_28C` arm as a tested defensive fallthrough, and re-measured all four downstream `dev test` legs (sweep, two count/banner legs, SDP-leg baseline gate, blank-check placement) to the live post-restoration plan shape -- taking the host suite from 5 failing to fully green (1811 passed).**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-21
- **Tasks:** 3/3 completed
- **Files modified:** 4

## Accomplishments

- **Task 1 -- Corrected `chip_test.py`'s two false reason texts.** The `_PROTOCOL_EEPROM_28C`
  constant's comment no longer claims the 28C family has no erase operation; it now states
  the Phase 153 mechanism (AN-0544B software chip erase in `configure_eeprom28c`, restored
  wire flag) and records the arm as a deliberately-kept defensive fallthrough for a
  non-qualifying-electrical-type user-override row, with the delete-versus-keep disposition
  and a checked (not assumed) confirmation that ruff's `select` list does not flag an unused
  module-level constant. The arm's own reason string was rewritten to state only what is
  true of a row that reaches it (non-qualifying electrical type), naming no wire flag. The
  three coupled expressions (`can_erase` read, `erase_is_executable` computation, erase arm's
  condition) are byte-unchanged, confirmed by `git diff`.
- **Task 2 -- Inverted and re-measured `test_chip_test.py`'s four legs.** Renamed and inverted
  the sweep leg (`test_devtest01_0x0d_sweep_erase_is_supported_and_erase_eprom_is_called`):
  erase is now `supported=True`/`destructive=True` and `operator.erase_eprom` is genuinely
  called. **MEASURED DISCREPANCY against the plan's own text:** live measurement showed
  `erase_eprom` is called **twice**, not once (`OP_ERASE` is in `_MULTI_RUN_OPS`, the
  write/erase/verify N=2 disagreement-policy set, and `run_plan`'s default `runs=2` applies
  uniformly) -- `assert_called_once()` would have been false, so `assert_called()` plus an
  explicit `call_count == 2` were used instead, with the divergence recorded in the docstring.
  Both count/banner legs re-measured live to `m_applicable=10, n_ran=6`, each carrying a
  third-generation accounting (pre-260807-kaq 10/6 -> post-260807-kaq 9/5 -> Phase 153 10/6
  again) with an explicit note that the integer coincidence with generation 1 is a composition
  coincidence (erase joining the sets, not blank-check returning), not a restoration. Added
  `test_protocol_eeprom_28c_arm_reachable_for_non_qualifying_etype`, a reachability leg using a
  `_NonQualifyingEtype28CDatabase` subclass (mirroring `tests/fixtures/synthetic_nonzero_chip_id.py`'s
  shape) that overrides AT28C256's `electrical-type` to `"OTP"`, proving the kept arm still
  fires and produces the corrected reason (never the generic flag-keyed wording). Module:
  **110 passed**.
- **Task 3 -- Re-measured `test_chip_test_sdp_leg.py` and moved the blank-check placement
  assertion in `test_chip_test_blank_check_order.py`.** The baseline-gate test's docstring
  gained a third generation (erase now runs regardless of the SDP baseline gate, since it
  precedes the SDP leg entirely, raising `n_ran` 5->6 and `m_applicable` 9->10), plus a direct
  erase-verdict assertion. The AT28C256 placement case was renamed
  (`test_at28c256_blank_check_moves_after_erase_but_stays_na`), its index assertion corrected
  from the stale index 2 to the exact measured index 5, and ordering assertions added (after
  erase at index 4, before every SDP-leg op) so the leg stays a contiguous terminal block. The
  module docstring's four-case enumeration and the `_CHIP_AUTO_ERASE_28C` constant's comment
  were both updated to state the new mechanism. Cases 2 and 4 (negative controls) confirmed
  byte-unchanged via `git diff` (no hunk inside either function). Combined run of all four
  `chip_test`-family modules plus `test_database_conversion.py`: **215 passed**.
- **Full host suite confirmed fully green.** `pytest -o addopts="" -q` over the entire
  `firestarter_app` test tree: **1811 passed, 0 failed** (227s). This closes the remaining
  5-failure set this plan inherited (`153-09-SUMMARY.md`'s "Next Phase Readiness").
- **`ruff check` / `ruff format --check`** pass on all four touched files. A pre-existing,
  out-of-scope ruff finding in three untouched `tools/` files (unrelated I001/UP031 issues,
  not in this plan's `files_modified`) is logged in `deferred-items.md` rather than fixed.
- **mypy watermark:** `35 == 35`, verified on a `uv venv --python 3.11` (the app's actual CI
  interpreter, built fresh this session with `UV_CACHE_DIR` set) -- the devcontainer's native
  Python 3.12 fails open on the same pre-existing numpy-stub syntax error noted in
  `153-09-SUMMARY.md`.
- `firestarter/` sub-repo confirmed clean of tracked modifications (`git status --short`
  empty); `tools/check_dispatch.py` confirmed untouched (`git diff --quiet` holds).

## Task Commits

1. **Task 1: Correct the two `chip_test.py` reason texts and keep the 0x0D arm as a defensive fallthrough** - `95041ba` (fix, firestarter_app)
2. **Task 2: Re-measure and invert the four `test_chip_test.py` legs, and prove the fallthrough arm is reachable** - `e53e095` (test, firestarter_app)
3. **Task 3: Re-measure the SDP-leg baseline accounting and move the blank-check placement assertion** - `3edabf2` (test, firestarter_app)

**Plan metadata:** pending (this commit)

## Files Created/Modified
- `firestarter_app/firestarter/chip_test.py` - corrected `_PROTOCOL_EEPROM_28C` constant comment + arm reason string; arm kept as documented defensive fallthrough; no logic change
- `firestarter_app/tests/test_chip_test.py` - sweep leg inverted (positive `erase_eprom` call, call_count==2 measured discrepancy); two count/banner legs re-measured to 10/6 with third-generation accounting; new reachability leg for the defensive fallthrough arm
- `firestarter_app/tests/test_chip_test_sdp_leg.py` - baseline-gate leg re-measured to n_ran=6/m_applicable=10 with third-generation accounting; added erase-verdict assertion
- `firestarter_app/tests/test_chip_test_blank_check_order.py` - AT28C256 case renamed, index corrected to the exact measured 5, ordering assertions added; module docstring and `_CHIP_AUTO_ERASE_28C` comment updated

## Decisions Made
- Used `assert_called()` + explicit `call_count == 2` for the sweep leg's positive erase-dispatch proof instead of the plan-prescribed `assert_called_once()`, after live measurement showed the multi-run disagreement policy (`_MULTI_RUN_OPS`, `runs=2`) calls `erase_eprom` twice -- recorded as a MEASURED DISCREPANCY in the docstring rather than forcing a false assertion to pass.
- Built the reachability leg's database double as an `EpromDatabase` subclass overriding `get_eprom` for one chip name (mirroring `tests/fixtures/synthetic_nonzero_chip_id.py`'s established pattern) rather than a bare `Mock`, so `convert_to_programmer`'s real flag-derivation logic runs unmodified against the overridden field.
- Chose `electrical-type="OTP"` as the synthetic non-qualifying value for the reachability fixture: outside {"EEPROM", "Flash/EEPROM"}, not "UV-EPROM" (which would route to a different arm first), and not in `_SRAM_FRAM_ETYPES`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in plan text] Corrected the sweep leg's call-count assertion from "exactly once" to "exactly twice"**
- **Found during:** Task 2
- **Issue:** The plan's own `<action>` text prescribed `erase_eprom.assert_called_once()`. Live-measured against this commit's `run_plan`, `OP_ERASE` is a member of `_MULTI_RUN_OPS` (the write/erase/verify N=2 disagreement-policy set) and `run_plan`'s default `runs=2` genuinely dispatches `erase_eprom` twice -- `assert_called_once()` fails with `Called 2 times`.
- **Fix:** Used `operator.erase_eprom.assert_called()` plus an explicit `assert operator.erase_eprom.call_count == 2`, and documented the divergence as a MEASURED DISCREPANCY in the test's docstring, per the project's established convention for reporting live measurements that contradict planning-time prose rather than silently reconciling them.
- **Files modified:** `firestarter_app/tests/test_chip_test.py`
- **Verification:** `pytest tests/test_chip_test.py::test_devtest01_0x0d_sweep_erase_is_supported_and_erase_eprom_is_called -o addopts="" -q` passes.
- **Committed in:** `e53e095` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - plan-text correctness).
**Impact on plan:** The corrected assertion is strictly more accurate than the plan's prescribed one and does not weaken the proof (it still positively proves dispatch occurred); no scope creep.

## Issues Encountered

None beyond the sweep-leg call-count discrepancy documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ERASE-03's `dev test` half is now fully funded: two corrected reason texts, a documented and
  tested defensive fallthrough arm, an inverted sweep leg, and third-generation M/N accountings
  across all three affected test modules.
- The full host suite (1811 tests) is confirmed green, closing out the plan-shape absorption
  work this milestone's plans 07-10 were staged across.
- No blockers for plans 11, 12, 13, or 16, which also claim ERASE-03 and have not yet run.
- `write_scope="none"`'s AT28C256 step-list shrink (4 -> 3, `locked_destructive` gaining
  `erase`) remains unasserted by any test this plan touches, as the plan's own inherited-state
  notes -- plan 12 owns pinning it.
- A pre-existing, out-of-scope ruff finding in three untouched `tools/` files is logged in
  `153-write-path-erase-policy/deferred-items.md`.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED
