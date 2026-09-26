---
phase: 153-write-path-erase-policy
plan: 15
subsystem: infra
tags: [platformio, avr, size-gate, merge-05, check_size_baseline, fixture-severance, erase-08]

# Dependency graph
requires:
  - phase: 153-write-path-erase-policy (plan 14)
    provides: "MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130, the fourth named flash
      exemption, and 3 test legs deliberately left red for this plan's fixture severance"
  - phase: 151-protection-readability-lock-status
    provides: "the *_v151* fixture-severance precedent and the module-docstring
      severance-record pattern this plan's fourth generation follows"
provides:
  - a new *_v153* fixture family (13 files, 4 groups), each Group-4 plant re-derived
    from `_merge05_flash_allowance()`/`_merge05_ram_allowance()` plus one and OBSERVED
    to flip the checker to failure before any leg was written against it
  - 8 repointed legs + 1 new admission arm + 1 strengthened anti-laundering leg in
    tests/test_check_size_baseline.py, all 14 legs green
  - a reconciliation record: 4 legs were red at task start that 153-14-SUMMARY.md's
    hand-off did not enumerate (one a genuinely new coupling -- native case counts)
  - ERASE-08 flipped to Complete -- the last of its three owning plans
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fourth-generation fixture severance: sever onto a NEW *_v153* family, never
      repoint or re-anchor the *_v151* family it retires in place"
    - "Widened-not-repointed leg treatment (Arm 1 and Arm 3 of the admission test):
      fixture stays fixed at its own sub-allowance delta, only the decomposition-
      string assertion widens to the current allowance's full term count"

key-files:
  created:
    - firestarter/tests/fixtures/captured_build_v153_uno.log
    - firestarter/tests/fixtures/captured_build_v153_uno328pb.log
    - firestarter/tests/fixtures/captured_build_v153_leonardo.log
    - firestarter/tests/fixtures/merge05_base01_anchor_v153_uno.log
    - firestarter/tests/fixtures/merge05_base01_anchor_v153_uno328pb.log
    - firestarter/tests/fixtures/merge05_base01_anchor_v153_leonardo.log
    - firestarter/tests/fixtures/merge05_erase_standalone_v153_uno.log
    - firestarter/tests/fixtures/merge05_erase_standalone_v153_uno328pb.log
    - firestarter/tests/fixtures/merge05_erase_standalone_v153_leonardo.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth_v153.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band_v153.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved_v153.log
    - firestarter/tests/fixtures/planted_size_baseline_flash_regression_v153.log
  modified:
    - firestarter/tests/test_check_size_baseline.py
    - firestarter/tests/fixtures/captured_test_native_summary.log
    - firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log

key-decisions:
  - "Group 2 (merge05_base01_anchor_v153_*.log) sets BOTH the RAM: and Flash: `used`
    figures to BASE-01's anchor, matching the *_v151* precedent's actual on-disk
    shape (not just the flash figure the plan's own prose literally names) -- this is
    what makes the anchor a genuine zero-delta reference on both dimensions"
  - "Reconciled 4 legs that were red at task start against 153-14-SUMMARY.md's
    3-item hand-off: test_clean_avr_all_three_envs_pass and
    test_default_mode_is_unchanged_by_the_new_flag (omitted from the hand-off, not a
    new coupling), test_planted_flash_regression_flips_checker_to_failure (red for
    the WRONG reason), and test_clean_native_both_envs_pass (a genuinely NEW coupling
    -- native case counts moved 163->170 in the same plan-14 revision, never
    mentioned in that plan's hand-off)"
  - "Arm 1 and Arm 3 of test_policy_merge05_admits_the_documented_defect_fix are
    WIDENED, not repointed: their fixtures stay fixed at +96/+594 respectively, but
    their decomposition-string assertions extend to the current five-term
    allowance, since Arm 3 no longer sits at zero headroom once this plan's own
    exemption widened the ceiling further"
  - "ERASE-08 flipped to Complete in REQUIREMENTS.md -- all four clauses of its full
    text are satisfied across the three owning plans (constants lockstep and
    cold measurement: plan 01/14; leonardo's own named exemption: plan 14; the
    tripwire re-armed and proven above the new ceiling: this plan)"

requirements-completed: [ERASE-08]

coverage:
  - id: D1
    description: "Thirteen-file *_v153* fixture family planted in four groups; all
      four Group-4 plants OBSERVED to flip the checker to failure before any leg
      was written against them"
    requirement: "ERASE-08"
    verification:
      - kind: unit
        ref: "firestarter/tests/fixtures/*_v153*.log + manual checker invocations (transcribed below)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Eight legs repointed onto *_v153*, one new admission arm added, one
      leg strengthened (not repointed) with a fifth source pin plus two new checks;
      all 14 legs in tests/test_check_size_baseline.py pass together"
    requirement: "ERASE-08"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py (pytest -o addopts=\"\" -q, 14 passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Severance record written in the module docstring after Plan
      151-10's own record (not replacing it); all four required grep substrings
      present"
    requirement: "ERASE-08"
    verification:
      - kind: unit
        ref: "grep -c 'software-proven and unvalidated on silicon'/'retired in place'/'ERASE-08'/'no CI leg' tests/test_check_size_baseline.py (all >= 1)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full phase gate re-run from a committed tree: both native envs,
      three cold AVR builds against the revised baseline in both gate modes, the
      build-warnings checker, the erase-body checker, the checker-convention
      meta-test, host lint/format/type gates, and the host dispatch/SDP-window gates"
    requirement: "ERASE-08"
    verification:
      - kind: other
        ref: "pio test -e native / -e native_nodevtools (170/17 both); check_build_warnings.py, check_erase_no_vpp.py, check_dispatch.py, check_no_log_in_sdp_window.py (all exit 0); ruff check/format, check_mypy_watermark.py (all pass)"
        status: pass
    human_judgment: false

# Metrics
duration: 28min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 15: Size Tripwire Severance Onto `*_v153*` Summary

**Re-planted the size tripwire on a new `*_v153*` fixture family (13 files, 4 groups) so the +130 B erase exemption's widened MERGE-05 allowance is still a ceiling — all 4 plants observed flipping the checker to failure — repointed 8 legs plus a new admission arm, strengthened the anti-laundering leg, and flipped ERASE-08 to Complete.**

## Performance

- **Duration:** 28 min
- **Started:** 2026-08-21T10:48:00Z
- **Completed:** 2026-08-21T11:16:00Z
- **Tasks:** 3
- **Files modified:** 16 (13 new fixtures, 1 test module, 2 native summary fixtures updated in place)

## Accomplishments

- Planted a new 13-file `*_v153*` fixture family in the four established groups: three
  real cold `rm -rf .pio/build/<env>` + `pio run -e <env>` captures (byte-identical to
  the live `size_baseline.json`: uno 25548/1575, uno328pb 25598/1581, leonardo
  27630/2016); three synthetic BASE-01 zero-delta anchors; three exemption-admission
  logs (numerically identical to the captures, by design); and four plants, each
  computed by importing `check_size_baseline` and reading
  `_merge05_flash_allowance()`/`_merge05_ram_allowance()`'s own returned values — never
  a hand-added number.
- **Observed all four plants flip the checker to failure** before writing any leg
  against them: leonardo-growth (delta=+725 > 724 B allowance), uno-class over-band
  (delta=+789 > 788 B), RAM-moved (delta=+3 > 2 B), and the default-mode flash
  regression (28142 vs baseline 27630). Verbatim transcripts below.
- Repointed 8 legs onto `*_v153*`, added a new Arm 4 to
  `test_policy_merge05_admits_the_documented_defect_fix` reading the three
  `merge05_erase_standalone_v153_*.log` admission logs (PASSES at exactly the new
  leonardo ceiling — zero headroom), and widened Arm 1/Arm 3's decomposition-string
  assertions to the current five-term allowance without touching either fixture.
- Strengthened (never repointed) `test_base01_is_not_re_anchored_by_the_new_exemption`:
  added the fifth source pin (`MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130`), a check
  that the constant is actually consumed inside `_merge05_flash_allowance()`'s own body,
  and a check that the constant's name never leaks into BASE-01's raw JSON text.
- **Found and fixed a reconciliation gap**: the full suite showed 7 red legs at task
  start, not the 3 named in `153-14-SUMMARY.md`'s hand-off. Fixed all 7 (4 not on the
  historical list, one — `test_clean_native_both_envs_pass` — a genuinely new coupling
  since native case counts moved 163→170 in the same plan-14 revision that moved
  `size_baseline.json`, never mentioned in that plan's hand-off).
- Wrote the Plan 153-15 severance record in the module docstring, appended after Plan
  151-10's own record (never replacing it), carrying the four-group inventory, the
  reconciliation, the retired-in-place statement, the never-reads-a-fixture reason, the
  no-CI-leg sentence, and the Evidence-Ceiling sentence.
- Re-ran the full phase gate from a committed tree: both native envs (170 cases/17
  suites, all passed, both agree), `check_build_warnings.py` (PASS — AVR envs
  macro_redefinition=0, native/native_nodevtools observed 998, watermark 1166 held),
  `check_erase_no_vpp.py` (PASS), `check_dispatch.py` (exit 0, un-diffed source), the
  SDP-window checker (PASS), host `ruff check`/`ruff format --check` (pass), and
  `check_mypy_watermark.py` via a real Python 3.11 venv (35/35, at watermark — the
  devcontainer's default 3.12 interpreter fails this gate on an unrelated numpy stub
  syntax error, a known environment gap, not a regression).
- Flipped ERASE-08 to Complete — the last of its three owning plans (01, 14, 15).

## Task Commits

Each task was committed atomically in `firestarter/`:

1. **Task 1: Plant the thirteen-file `*_v153*` fixture family, each plant observed failing** — `e3593ad` (test)
2. **Task 2: Repoint the eight legs onto the new family and strengthen the not-re-anchored leg** — `aee1e95` (test)
3. **Task 3: Write the severance record and re-run the full phase gate** — `ce5cebd` (docs)

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md/REQUIREMENTS.md updates, committed separately per the `sub_repos` config (meta-repo `.planning/` commit).

## Files Created/Modified

- `firestarter/tests/fixtures/captured_build_v153_{uno,uno328pb,leonardo}.log` — cold clean-control captures
- `firestarter/tests/fixtures/merge05_base01_anchor_v153_{uno,uno328pb,leonardo}.log` — synthetic zero-delta anchors (derivation source for the plants)
- `firestarter/tests/fixtures/merge05_erase_standalone_v153_{uno,uno328pb,leonardo}.log` — this exemption's own admission proof
- `firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth_v153.log` — one byte past the new 724 B leonardo allowance
- `firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band_v153.log` — one byte past the new 788 B uno-class allowance
- `firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved_v153.log` — one byte past the unchanged 2 B RAM tolerance
- `firestarter/tests/fixtures/planted_size_baseline_flash_regression_v153.log` — default-mode regression plant (+512 B standing offset)
- `firestarter/tests/test_check_size_baseline.py` — 8 legs repointed, 1 new admission arm, 1 strengthened leg, severance record appended to the module docstring
- `firestarter/tests/fixtures/captured_test_native_{summary,nodevtools_summary}.log` — updated in place, 163→170 cases (deviation, see below)

## Decisions Made

- Group 2 anchors set BOTH `used` figures (RAM and Flash) to BASE-01's anchor, matching
  the `*_v151*` precedent's actual on-disk shape — the plan's own prose names only
  "the used flash figure," but the read-first precedent file it points to sets both,
  and only setting both achieves the "EXACT ZERO delta on all three targets" property
  the docstring for `test_policy_merge05_permits_the_measured_landing_deltas` requires
  of this fixture shape. Decided per "decide mechanical gray areas, do not ask."
- Arm 1 and Arm 3 of the admission test are widened, not repointed — their fixtures
  stay byte-identical to their prior generation, only the decomposition-string
  assertion grows a fifth term, mirroring exactly the treatment Plan 151-10 gave
  Arm 1 one generation earlier.
- Left the `*_v151*` family (and the two `_fullflash`-generation-and-earlier retired
  families) completely untouched — `git status --porcelain tests/fixtures/` shows zero
  modified `*_v151*` entries throughout.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed 4 additional red legs not named in plan 14's hand-off**
- **Found during:** Task 2, before making any edits (ran the full suite to establish
  the true baseline)
- **Issue:** `153-14-SUMMARY.md` named only 3 red legs. The actual suite showed 7 red:
  `test_clean_avr_all_three_envs_pass`, `test_clean_native_both_envs_pass`,
  `test_planted_flash_regression_flips_checker_to_failure`, and
  `test_default_mode_is_unchanged_by_the_new_flag` were also broken by Plan 153-14's
  own `size_baseline.json` re-record (avr_targets AND native_envs both moved, but the
  hand-off only flagged the avr_targets-coupled legs plan 14 itself had authored
  assertions against).
- **Fix:** Repointed the three AVR-coupled legs onto the new `*_v153*` family (same task
  as the originally-scoped repointing) and updated the two native summary fixtures in
  place (163→170 cases, following the established in-place convention for that pair,
  via real `pio test -e native`/`-e native_nodevtools` runs).
- **Files modified:** `tests/test_check_size_baseline.py`, `tests/fixtures/captured_test_native_summary.log`, `tests/fixtures/captured_test_native_nodevtools_summary.log`
- **Verification:** Full suite green (14/14) after the fix.
- **Committed in:** `aee1e95` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug/reconciliation gap)
**Impact on plan:** Necessary to meet the plan's own acceptance criterion ("full `test_check_size_baseline.py` green") and its own reconciliation instruction ("a leg that failed but is not on the historical list is a new coupling worth naming"). No scope creep — the fix stayed inside `tests/` and this plan's own fixture-family boundary.

## Issues Encountered

- The devcontainer's default Python (3.12) fails `check_mypy_watermark.py` with a
  tool/config error (`numpy/__init__.pyi:737: error: Type statement is only supported
  in Python 3.12 and greater`) — a known pre-existing environment gap (app CI runs
  Python 3.11 only), not a regression introduced by this plan. Worked around by
  creating a throwaway `uv venv --python 3.11` in the scratchpad, installing `.[test]`
  into it, and running the gate through that interpreter — 35/35, at watermark, exit 0.
  No repository file was changed to work around this; the venv lives entirely outside
  the repo.

## Requirement Flip Note

**ERASE-08 flipped to Complete.** All four clauses of its full text are now satisfied,
jointly across the three owning plans:
- "Constants stay in lockstep across `firestarter.h` and `constants.py`" — measured and
  confirmed by plan 14 (14/14 `test_revision_constants_parity.py` passed; both files
  read side by side, no value differs).
- "the flash/RAM delta is measured against a pre-change baseline on all three AVR
  targets" — plan 14's cold `rm -rf` + `pio run` measurement, transcribed in
  `153-DECISIONS.md`'s "Post-change measured position (cold)" section.
- "leonardo... needs its own named exemption" — plan 14 funded
  `MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130`, sized exactly from the measured
  delta, never rounded.
- "a regression is a blocker rather than a note" — this plan re-armed and PROVED the
  tripwire above the new ceiling: all four Group-4 plants were observed flipping the
  checker to failure, and the full `test_check_size_baseline.py` suite (14/14) plus the
  checker-convention meta-test and the erase-body checker all pass together from a
  committed tree.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 153 (Write-Path Erase Policy) has no further plans after this one — this was
  the phase's final tripwire-severance plan, closing ERASE-08.
- The size gate is armed above the new 724 B (leonardo) / 788 B (uno-class) MERGE-05
  allowance and both gate modes are green on all three AVR targets.
- The Caterina cliff headroom is 1042 B on leonardo (down from 1172 B pre-phase),
  UNGUARDED — no gate catches a future overrun past 28672 B; recorded, not mitigated,
  per the phase's own decisions (unchanged by this plan).
- `firestarter_app/` carries no tracked-file diff from this plan — its untracked files
  (`SECURITY.md`, `datasheets/*.pdf`, `write_test_port.sh`, `.planning/config.json`)
  predate this plan and are not touched by it.

## Verbatim Plant-Failure Transcripts (Group 4, Task 1)

```
$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log leonardo=tests/fixtures/planted_size_baseline_policy_leonardo_growth_v153.log
FAIL:
  leonardo: flash_used baseline=26906 observed=27631 delta=+725 exceeds MERGE-05 leonardo allowance of 724 B (band 0 B + defect-fix exemption 96 B + page-size-seam exemption 210 B + lock-status-read exemption 288 B + erase-standalone exemption 130 B)
exit=1

$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=tests/fixtures/planted_size_baseline_policy_uno_over_band_v153.log
FAIL:
  uno: flash_used baseline=24824 observed=25613 delta=+789 exceeds MERGE-05 uno-class allowance of 788 B (band 64 B + defect-fix exemption 96 B + page-size-seam exemption 210 B + lock-status-read exemption 288 B + erase-standalone exemption 130 B)
exit=1

$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=tests/fixtures/planted_size_baseline_policy_ram_moved_v153.log
FAIL:
  uno: ram_used baseline=1573 observed=1576 delta=+3 exceeds MERGE-05 ram allowance of 2 B (page-size-seam exemption 2 B) (MERGE-05 requires ram_used within the admitted allowance)
exit=1

$ python3 scripts/check_size_baseline.py --avr-log leonardo=tests/fixtures/planted_size_baseline_flash_regression_v153.log
FAIL:
  leonardo: flash_used baseline=27630 observed=28142
exit=1
```

## Known Stubs

None.

## Threat Flags

None — no new network endpoint, auth path, file access pattern, or schema change at a
trust boundary was introduced; this plan only re-plants a test fixture family and its
associated legs.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: all 13 `tests/fixtures/*_v153*.log` files
- FOUND commit `e3593ad` (Task 1)
- FOUND commit `aee1e95` (Task 2)
- FOUND commit `ce5cebd` (Task 3)
- FOUND: `.planning/phases/153-write-path-erase-policy/153-15-SUMMARY.md`
