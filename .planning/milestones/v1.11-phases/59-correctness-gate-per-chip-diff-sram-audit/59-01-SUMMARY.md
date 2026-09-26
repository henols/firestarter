---
phase: 59-correctness-gate-per-chip-diff-sram-audit
plan: 01
subsystem: database
tags: [python, json, diff, regression-gate, determinism, chip-database]

# Dependency graph
requires:
  - phase: 58-pinout-re-derivation-24-pin-eeprom-unblock
    provides: "Regenerated chip_database.json (743 chips); DIP24_2816 pinout; principled resolve_pinout_key"
  - phase: 57-decode-bug-fixes-protocol-map-check-dispatch
    provides: "BUG-2 timing fix, BUG-3 vcc/vdd fix, check_dispatch.py GATE-03 guard"
  - phase: 56-snapshot-field-dictionary-corrected-docs
    provides: "chip_database.baseline.json (immutable anchor, commit f92873d); citation convention (a8efaedc)"
provides:
  - "GATE-02 green: diff_db.py — re-runnable, grouped-by-cause, full-record diff; exits 0 all 371 changed chips explained; exits 1 on unexplained diff (D-03 BLOCK)"
  - "sort_keys=True hardening in build_db.py (SC#4 byte-stable output)"
  - "SC#4 proof: two consecutive build_db.py runs byte-identical (empty diff)"
  - "SC#2 re-confirmed: check_dispatch.py exits 0 across all 743 chips incl. DIP24_2816"
  - "Snapshot test updated to reflect sort_keys=True new ordering"
affects:
  - "59-02-PLAN (GATE-04 SRAM audit)"
  - "v1.11 milestone close"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "diff_db.py mirrors check_dispatch.py structure: stdlib-only, env-overridable path constants, grouped-by-cause report, exit-code contract, if __name__ == '__main__': main() guard"
    - "BUG2_AND_BUG3 combined-case MUST be tested before single-cause buckets (Pitfall 2 guard)"
    - "sort_keys=True on json.dump for byte-stable DB output regardless of Python dict ordering"

key-files:
  created:
    - firestarter_app/tools/diff_db.py
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "sort_keys=True added to build_db.py json.dump — makes output key-order stable; also changes DB file ordering, requiring snapshot refresh"
  - "diff_db.py uses full bl_chip != cu_chip deep-compare (stdlib dict ==) then classifies by cause — no hand-rolled recursion"
  - "Snapshot test_characterization.ambr updated (Rule 1 auto-fix): sort_keys=True moved Standard SRAM manufacturer earlier in list"

patterns-established:
  - "GATE-02 classifier priority order: RULE_ALGO > BUG2_AND_BUG3 > BUG2_TIMING > BUG3_VCC_VDD > SRAM_PINOUT > None (D-03 BLOCK)"
  - "env-overridable BASELINE_FILE + DB_FILE path constants for testability (FIRESTARTER_BASELINE_FILE / FIRESTARTER_DB_FILE)"

requirements-completed: [GATE-02]

# Metrics
duration: 35min
completed: 2026-06-09
---

# Phase 59 Plan 01: Correctness Gate + Per-chip Diff Summary

**GATE-02 green: diff_db.py classifies all 371 changed chips by 5 root-cause rules with embedded minipro a8efaedc citations; SC#4 byte-identity proved; SC#2 (743 chips) re-confirmed**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-06-09T08:45:00Z
- **Completed:** 2026-06-09T09:20:00Z
- **Tasks:** 2
- **Files modified:** 4 (submodule) + 1 (snapshot)

## Accomplishments

- `build_db.py` hardened with `sort_keys=True` on `json.dump` (SC#4 determinism); DB regenerated to 743 chips with stable key ordering
- `diff_db.py` created as a re-runnable GATE-02 gate: grouped-by-cause, full-record, D-03 BLOCK on unexplained diffs
- SC#4 proved: two consecutive `build_db.py` runs produce byte-identical `chip_database.json` (empty diff)
- SC#2 re-confirmed: `check_dispatch.py` exits 0 across all 743 chips including DIP24_2816

## GATE-02 Diff Report Summary

All 371 changed chips are explained by cited root-cause rules. 9 new chips confirmed. 0 chips missing.

| Root Cause | Count | Fields Changed | Citation |
|------------|-------|----------------|----------|
| RULE_ALGO | 17 | `programming.algorithm` | minipro database.c @ a8efaedc; WARNING-5 |
| BUG2_AND_BUG3 | 188 | `pulse_duration` + `vcc`/`vdd` | database.c#L866 + #L921-L923 @ a8efaedc |
| BUG2_TIMING | 19 | `pulse_duration` only | database.c#L866 @ a8efaedc |
| BUG3_VCC_VDD | 135 | `vcc`, `vdd` only | database.c#L921-L923 @ a8efaedc |
| SRAM_PINOUT | 12 | `pinout` | Phase 58 principled resolve_pinout_key |
| NEW chips | 9 | N/A (new records) | Rule 1: DIP24_2816 + algo=0x0D |
| MISSING | 0 | — | — |
| **Total changed** | **371** | | |

## SC#4 Proof (byte-identity)

```
Run 1: python3 tools/build_db.py  ->  chip_database.json saved to /tmp/chip_database_run1.json
Run 2: python3 tools/build_db.py  ->  chip_database.json saved to /tmp/chip_database_run2.json
diff /tmp/chip_database_run1.json /tmp/chip_database_run2.json
SC#4 PASS: byte-identical  (empty diff output)
```

Both runs fetched the same upstream `infoic.xml` state (back-to-back), producing byte-identical output. `sort_keys=True` ensures stability regardless of Python dict insertion order.

## SC#2 Re-confirmation

```
cd firestarter_app && python tools/check_dispatch.py
PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom;
0 DIP28_2764 Flash/EEPROM chips route to configure_eprom;
0 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions
```

GATE-03 guard auto-covers DIP24_2816 because it keys on `electrical.type` (pinout-agnostic, Phase 57 CR-01).

## D-03 BLOCK Exit-1 Demonstration

The `diff_db.py` D-03 BLOCK path was demonstrated with a probe file:

```bash
# Inject unknown field into one chip (M8720) in a probe copy of current DB
# Use probe as "current" with real DB as "baseline" (so chip is present in both but differs)
FIRESTARTER_BASELINE_FILE=firestarter/data/chip_database.json \
FIRESTARTER_DB_FILE=/tmp/probe_db.json \
python tools/diff_db.py
# Output: FAIL: 1 chips with unexplained diffs:
#           M8720
# Exit code: 1  <-- D-03 BLOCK
```

The `baseline==current` edge case also verified:
```bash
FIRESTARTER_BASELINE_FILE=firestarter/data/chip_database.json python tools/diff_db.py
# Output: PASS: all 0 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
# Exit code: 0
```

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule:

1. **Task 1: sort_keys=True hardening + DB regen + SC#4/SC#2** - `3dc11c3` (feat)
2. **Task 2: diff_db.py + snapshot update** - `fc62a27` (feat)

## Files Created/Modified

- `firestarter_app/tools/build_db.py` — added `sort_keys=True` to `json.dump` call (line 517)
- `firestarter_app/firestarter/data/chip_database.json` — regenerated (743 chips, sort-stable key ordering)
- `firestarter_app/tools/diff_db.py` — new GATE-02 diff script (stdlib-only, grouped-by-cause, D-03 BLOCK)
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — snapshot updated (sort order change)

## Decisions Made

- `sort_keys=True` added first, then DB regenerated, then SC#4 two-run compare (Pitfall 3 avoided: no build_db.py change between runs)
- `diff_db.py` uses Python dict `==` for full-record comparison; only runs `_classify_diff` on differing records
- `BUG2_AND_BUG3` classifier tested BEFORE single-cause buckets to handle 188 combined-fix chips correctly (Pitfall 2)
- Snapshot `test_characterization.ambr` refreshed via `--snapshot-update` — legitimate because sort_keys=True changes manufacturer key order which changes list output ordering

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Snapshot test failure after sort_keys=True**
- **Found during:** Task 1 verification (after DB regeneration, running full test suite)
- **Issue:** `tests/test_characterization.py::test_list` snapshot failed because `sort_keys=True` changed the output order of manufacturers in `firestarter list` (Standard SRAM manufacturer "61xx" chips now appear earlier in alphabetical order)
- **Fix:** Updated snapshot via `pytest --snapshot-update tests/test_characterization.py::test_list`; verified all 516 tests pass and coverage floor maintained
- **Files modified:** `tests/__snapshots__/test_characterization.ambr`
- **Verification:** `pytest --cov-fail-under=70` passed with 516 tests (0 failed)
- **Committed in:** `fc62a27` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - snapshot update for legitimate ordering change)
**Impact on plan:** Required snapshot refresh is a correctness fix, not scope creep. The new ordering is the correct alphabetical-sort output.

## Issues Encountered

None beyond the snapshot auto-fix above.

## Next Phase Readiness

- GATE-02 is green: `diff_db.py` committed and exits 0 across the full 371 changed + 9 new chips
- SC#2 and SC#4 green
- Ready for Phase 59 Plan 02: GATE-04 SRAM audit + two-layer documentation

## Self-Check

---
*Phase: 59-correctness-gate-per-chip-diff-sram-audit*
*Completed: 2026-06-09*
