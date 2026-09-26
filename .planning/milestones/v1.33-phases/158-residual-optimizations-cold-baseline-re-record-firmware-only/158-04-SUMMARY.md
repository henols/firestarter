---
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
plan: "04"
subsystem: firmware
tags: [size-baseline, ci-gate, merge05, fixture-severance, pytest, jsmn]

# Dependency graph
requires:
  - phase: 158-01
    provides: "158-before-figures.md — the cold pre-phase AVR/native ledger, the recorded RED shape of default mode (8 verbatim FAIL lines), and the four legs + remedies this plan executes"
  - phase: 158-02
    provides: "jsmntok_t narrowing — the only src/ change landed this phase (RAM -128 B, flash a reduction on all three AVR targets); this plan's cold figures reproduce it exactly"
  - phase: 158-03
    provides: "LAND-06 declined, zero source change — confirms this plan's tree position (HEAD unchanged since 158-02) needed no additional re-measurement"
provides:
  - "scripts/baseline/size_baseline.json re-recorded from cold builds: avr_targets (uno 22952/1434, uno328pb 23000/1440, leonardo 25098/1875) and native_envs (native/native_nodevtools both 184/184/17)"
  - "*_v158* fixture family: 4 new files (three cold captures + one derived plant) plus 2 native summaries updated in place; *_v153* family retired in place and kept"
  - "Default mode flipped RED -> GREEN (LAND-01 discharge evidence): exit 0, verbatim PASS: line, against plan 01's own recorded RED shape"
  - "Canonical --policy merge05 verbatim PASS: line with three negative flash deltas (-1872/-1874/-1808) against positive allowances (788/788/724) and three negative RAM deltas (-139 each) against a 2 B tolerance (LAND-02 one-sidedness evidence)"
  - "meta.consumed_by and envs_agree_note stale-prose repairs (C-7, C-8)"
affects: ["158-05 (BASE-01/checker-convention close-out)", "158-06 (after-figures)", "158-07 (ROADMAP/REQUIREMENTS correction)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One-commit re-record + severance discipline: a baseline value move and its dependent fixture family land atomically because the checker's own pytest runs in CI on every branch except beta"
    - "Fixture severance onto a new *_vNNN* family rather than repointing/deleting the retired one, preserving byte-level measurement history in git-tracked files"

key-files:
  created:
    - firestarter/tests/fixtures/captured_build_v158_uno.log
    - firestarter/tests/fixtures/captured_build_v158_uno328pb.log
    - firestarter/tests/fixtures/captured_build_v158_leonardo.log
    - firestarter/tests/fixtures/planted_size_baseline_flash_regression_v158.log
  modified:
    - firestarter/scripts/baseline/size_baseline.json
    - firestarter/tests/fixtures/captured_test_native_summary.log
    - firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log
    - firestarter/tests/test_check_size_baseline.py

key-decisions:
  - "OD-8 executed: the *_v153* family is retired in place and KEPT, never repointed or deleted. Severance is 4 new files plus 2 updated in place (not the 13-file, 4-group docket every prior generation used), because no MERGE-05 exemption is authored for a reduction (D-03) -- Groups 2 and 3 are explicitly not needed and not authored this generation."
  - "The re-record and the severance land in ONE commit (S-4): build.yml:161's pytest tests/ -v fires on push to every branch except beta, so a split commit would leave a CI-red intermediate commit on this branch."
  - "The two native summary fixtures are updated IN PLACE, not severed -- test_clean_native_both_envs_pass is the sole reader of either, matching the established convention since Phase 149 Plan 07."
  - "meta.consumed_by and envs_agree_note's stale prose (C-7, C-8) are repaired in the same commit rather than deferred, since both are on this plan's own subject (the file this plan re-records)."

requirements-completed: [LAND-01, LAND-02]

# Coverage metadata
coverage:
  - id: D1
    description: "size_baseline.json re-recorded from cold builds with every figure mechanically equal to a figure parsed from a committed capture (never computed)"
    requirement: "LAND-01"
    verification:
      - kind: unit
        ref: "tests/test_check_size_baseline.py::test_clean_avr_all_three_envs_pass, ::test_clean_native_both_envs_pass"
        status: pass
      - kind: other
        ref: "python3 -c baseline-fixture mechanical consistency check (parses captured_build_v158_*.log + native summaries, asserts equality with size_baseline.json) -> BASELINE-FIXTURE-CONSISTENT"
        status: pass
    human_judgment: false
  - id: D2
    description: "Default mode (no --policy) flips from the RED shape plan 01 recorded to a PASS: line -- LAND-01's own discharge evidence"
    requirement: "LAND-01"
    verification:
      - kind: other
        ref: "python3 scripts/check_size_baseline.py --avr-log ... --native-log ... -> exit 0, PASS: uno(flash=22952/32768,ram=1434/2048), uno328pb(flash=23000/32768,ram=1440/2048), leonardo(flash=25098/32768,ram=1875/2560), native(cases=184,suites=17), native_nodevtools(cases=184,suites=17)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Canonical --policy merge05 invocation exits 0 with three negative flash deltas against positive allowances -- LAND-02's one-sidedness evidence, no exemption authored"
    requirement: "LAND-02"
    verification:
      - kind: other
        ref: "python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log ... -> exit 0, PASS: uno(flash=22952/32768[-1872<=788=...]), uno328pb(...[-1874<=788=...]), leonardo(...[-1808<=724=...])"
        status: pass
      - kind: unit
        ref: "tests/test_check_size_baseline.py::test_policy_merge05_fires_on_uno_class_over_band, ::test_policy_merge05_fires_on_leonardo_growth, ::test_policy_merge05_fires_on_ram_move (three surviving plants, unmoved allowance)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Fixture severance: *_v158* family (4 new) plus 2 native summaries updated in place; *_v153* retired in place and kept; BASE-01 and checker source byte-unchanged"
    verification:
      - kind: unit
        ref: "tests/test_check_size_baseline.py -q -o addopts=\"\" (14 passed) and combined with tests/test_check_build_warnings.py (24 passed)"
        status: pass
      - kind: other
        ref: "git diff HEAD~1 HEAD -- scripts/baseline/size_baseline_base01.json scripts/check_size_baseline.py -> both empty"
        status: pass
    human_judgment: false

# Metrics
duration: ~40min
completed: 2026-08-24
status: complete
---

# Phase 158 Plan 04: Cold baseline re-record + fixture severance onto v158 Summary

**`size_baseline.json` re-recorded from three cold `pio run` builds and two genuine `pio test` native captures at the phase's final tree position (8e126f2), landed in one commit with a new `*_v158*` fixture family, flipping the default-mode gate from RED to GREEN and producing a verbatim one-sided `PASS:` line for LAND-02.**

## Performance

- **Duration:** ~40 min
- **Completed:** 2026-08-24
- **Tasks:** 3 (2 produced state -- captures and the commit; task 3 recorded gate output with no tracked-file change)
- **Files modified:** 8 (4 created, 4 modified) in the one commit; ROADMAP.md checkbox in the meta repo

## Accomplishments

- **Task 1 (capture):** Three cold `rm -rf .pio/build/<env>` + single `pio run -e <env>` builds reproduced plan 158-02's own post-narrowing figures exactly: uno 22952/1434, uno328pb 23000/1440, leonardo 25098/1875 (all zero `warning:` lines). Structural comparison against the `*_v153*` analogs found only benign differences: smaller progress-bar fill counts (expected, from the smaller byte counts) and non-deterministic parallel-build step ordering (a known PlatformIO characteristic, not a regression) -- same 86-line count, same banner, same trailing environment-status block on all three.
- Two genuine `pio test -e native` / `-e native_nodevtools` runs both reported 184/184 cases, 17 suites -- unchanged from plan 158-01's and plan 158-02's own measurements at this and the immediately-prior tree position. No D-04 re-run was needed (no count mismatch observed). The final recorded count (184) is this session's own measurement, per Pitfall 9, not a figure copied from the research document.
- The v153 plant's derivation rule was established by observing `diff tests/fixtures/captured_build_v153_leonardo.log tests/fixtures/planted_size_baseline_flash_regression_v153.log`: exactly one changed line, the `Flash:` line, at `27630 + 512 = 28142`, percentage and bar re-derived. This plan's new plant replicates the rule exactly: `25098 + 512 = 25610`, computed via the same `%5.1f%%` / `bar_chars = round(pct/10)` rendering rule, verified byte-identical to the real `pio` output format.
- **Task 2 (one commit, `e730068`):** Installed 4 new fixtures (`captured_build_v158_{uno,uno328pb,leonardo}.log`, `planted_size_baseline_flash_regression_v158.log`), updated the 2 native summary fixtures in place (172 -> 184 cases/succeeded, suites unchanged at 17), re-recorded all 16 moving fields in `size_baseline.json` (12 AVR + 4 native), repaired `meta.consumed_by` (now names 3 consumers including `check_release_assets.py`) and `envs_agree_note` (no longer quotes the stale 151-case figure), and appended a new `meta.cold_rerecord_phase158` dated note key following the established precedent. Repointed the four reddening legs in `tests/test_check_size_baseline.py` (`test_clean_avr_all_three_envs_pass`, `test_clean_native_both_envs_pass`, `test_planted_flash_regression_flips_checker_to_failure`, `test_default_mode_is_unchanged_by_the_new_flag`), changing only fixture names, figures, and each leg's own severance docstring paragraph -- no assertion's meaning changed. `scripts/baseline/size_baseline_base01.json` and `scripts/check_size_baseline.py` are byte-unchanged (all six MERGE-05 literals untouched). `git diff --name-only HEAD~1 HEAD` lists exactly the eight owned paths.
- Mechanical consistency proven by direct parse: every `avr_targets` `flash_used`/`ram_used`/`flash_free`/`ram_free` equals a figure parsed from its committed capture (free = untouched total minus used); every `native_envs` `cases`/`succeeded` equals the figure parsed from its committed native summary. `flash_total` (32768 x3), `ram_total` (2048/2048/2560), `suites` (17), `native_pinmap_provisional`, `envs_agree` and the whole `warnings` block are byte-unchanged; no `*_v131` env was added.
- `python3 -m pytest tests/test_check_size_baseline.py tests/test_check_build_warnings.py -q -o addopts=""`: **24 passed** (the severance-detection pair). `python3 -m pytest tests/ -q -o addopts=""` from `/workspaces/firestarter` on the committed tree: **360 passed**, zero `skipped` -- identical to plan 158-02's own post-Task-2 count (355+5 module legs), confirming plan 158-03 added no case and this plan changed fixture content only, not test inventory.
- **Task 3 (gate ledger, no commit):** LEG 1 (default mode against the just-recorded baseline, using the committed v158 fixtures): exit 0, `PASS: uno(flash=22952/32768,ram=1434/2048), uno328pb(flash=23000/32768,ram=1440/2048), leonardo(flash=25098/32768,ram=1875/2560), native(cases=184,suites=17), native_nodevtools(cases=184,suites=17)` -- the RED-to-GREEN flip against plan 01's own recorded 8-line RED shape (baseline=25548/25598/27630/1575/1581/2016, native baseline=172 both envs, all now observed strictly lower/equal). This is LAND-01's discharge evidence.
- LEG 3 (canonical `--policy merge05 --baseline scripts/baseline/size_baseline_base01.json`, fed the v158 AVR captures): exit 0, verbatim `PASS: uno(flash=22952/32768[-1872<=788=band64+exempt96+seam210+lock288+erase130],ram=1434/2048[-139<=2=seam2]), uno328pb(flash=23000/32768[-1874<=788=...],ram=1440/2048[-139<=2=seam2]), leonardo(flash=25098/32768[-1808<=724=...],ram=1875/2560[-139<=2=seam2])` -- three negative flash deltas against positive allowances and three negative RAM deltas against a 2 B tolerance. LAND-02's one-sidedness evidence, captured exactly.
- LEG 4: `sed -n '697p;709p' scripts/check_size_baseline.py` -> `if flash_delta > allowance:` / `if ram_delta > ram_tolerance:`, both growth-only. `grep -n "MERGE05_"` confirms all six literals (band 64, defect-fix 96, seam 210, lock-status 288, erase-standalone 130, seam-RAM 2) present and, per the empty `git diff HEAD~1 HEAD -- scripts/check_size_baseline.py`, byte-unchanged.
- LEG 5: `test_base01_is_not_re_anchored_by_the_new_exemption` green; `git diff 785e644 HEAD -- scripts/baseline/size_baseline_base01.json` (785e644 = the phase's own pre-phase SHA) is empty -- BASE-01 is byte-unchanged across the WHOLE phase, not merely this plan.
- LEG 6: the three surviving `*_v153*` policy plants (`test_policy_merge05_fires_on_uno_class_over_band`, `_on_leonardo_growth`, `_on_ram_move`) all green, asserted rather than re-planted -- their derivation basis (the unmoved allowance functions) never changed this phase, confirming the 4-plus-2 severance rather than the historical 13-file docket (C-11).
- LEG 7: `check_build_warnings.py --log uno=... --log uno328pb=... --log leonardo=...` -> exit 0, `PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0)` (the `warnings` block is byte-unchanged by this plan, hence expected clean). `check_no_heap_or_64bit_symbols.py` -> exit 0, `PASS: leonardo(heap=0,64bit=0,anchors=2/2,...), uno(...), uno328pb(...)`.
- LEG 8: `python3 -m pytest tests/ -q -o addopts=""` from `/workspaces/firestarter` on the committed tree: **360 passed**, zero `skipped` -- reconciled against plan 158-02's own post-commit count (also 360; unchanged, since neither plan 158-03 nor this plan added a test case).

## Task Commits

Each task was committed atomically:

1. **Task 1: Capture the final position once** — no commit (capture-only task; logs land under `/tmp/gsd-158/final/`, no tracked file touched)
2. **Task 2: One commit — re-record, sever, repoint** — `e730068` (test)
3. **Task 3: Discharge LAND-01/LAND-02 through the gate ledger** — no commit (gate-run task; HEAD stays at `e730068`)

## Files Created/Modified

- `firestarter/scripts/baseline/size_baseline.json` — 16 moving figures re-recorded from cold captures; `meta.consumed_by` and `envs_agree_note` prose repaired; new `meta.cold_rerecord_phase158` note key appended.
- `firestarter/tests/fixtures/captured_build_v158_{uno,uno328pb,leonardo}.log` — new, cold `pio run` captures, byte-for-byte.
- `firestarter/tests/fixtures/planted_size_baseline_flash_regression_v158.log` — new, derived from the leonardo capture with the standing +512 B offset.
- `firestarter/tests/fixtures/captured_test_native{,_nodevtools}_summary.log` — updated in place from real `pio test` runs.
- `firestarter/tests/test_check_size_baseline.py` — four legs repointed onto the v158 family with new severance docstring paragraphs; every other leg byte-unchanged.

## Decisions Made

- OD-8 executed: 4 new files plus 2 updated in place, not the 13-file 4-group docket. Groups 2 (synthetic BASE-01 anchor trio) and 3 (exemption-admission trio) are explicitly NOT authored this generation, stated in both the commit body and the module docstring's disposition table, because no MERGE-05 exemption is needed for a reduction (D-03).
- The one-commit rule (S-4) executed exactly as mandated: staged nothing until every edit was done and both required pytest runs (`test_check_size_baseline.py` alone, then combined with `test_check_build_warnings.py`) were green, then committed once.
- The two stale `meta` prose fields (C-7, C-8) were repaired in this same commit rather than deferred, since they are on this plan's own subject file.

## Deviations from Plan

### Auto-fixed Issues

None in the Rule 1-3 sense — no bug, missing functionality, or blocker was found in the source tree; this plan only re-records data and reorganizes test fixtures.

### Recorded discrepancy (honesty convention, not a deviation)

**LEG 2's actual observed shape differs from the plan's stated expectation.** The plan's action text predicted that `check_size_baseline.py --rebuild` in bare default mode (no `--policy`, no `--baseline`) would pass the AVR comparison but still fail the two native `cases` lines "because BASE-01 is not the baseline here." Observed: `python3 scripts/check_size_baseline.py --rebuild` exits **0** with a full `PASS:` line covering all three AVR targets AND both native envs (`PASS: uno(flash=22952/32768,ram=1434/2048), uno328pb(flash=23000/32768,ram=1440/2048), leonardo(flash=25098/32768,ram=1875/2560), native(cases=184,suites=17), native_nodevtools(cases=184,suites=17)`).

Root cause: a bare `--rebuild` invocation with no `--baseline` flag resolves `baseline_path = baseline_arg or FIRESTARTER_SIZE_BASELINE`, i.e. the *default* `scripts/baseline/size_baseline.json` — the file this plan just re-recorded — never `size_baseline_base01.json`. `main()`'s `--rebuild` branch (`check_size_baseline.py:879-883`) rebuilds AND re-tests **both** the three AVR envs and both `NATIVE_ENVS` (`native`, `native_nodevtools`), so a bare `--rebuild` genuinely re-executes `pio test` for both native envs against the live tree and compares against the live (now-current) baseline — which agrees, since nothing moved since the commit. BASE-01 only enters the picture when `--baseline scripts/baseline/size_baseline_base01.json` is passed explicitly (as LEG 3's canonical `--policy merge05` invocation does), which the plan's LEG 2 text does not specify. Recorded honestly per this phase's own convention (matching `158-before-figures.md`'s treatment of `check_build_warnings.py`'s bare-invocation discrepancy) rather than forcing the plan's original guess to appear true. This does not affect LAND-01 or LAND-02's discharge (LEG 1 and LEG 3 are the load-bearing evidence for each) — LEG 2 is explicitly a **check**, per Pitfall 6, never a transcription source, and its actual (stronger) result — full agreement between a fresh live rebuild and the just-committed baseline — is itself a valid confirmation that the re-record is internally consistent.

---

**Total deviations:** 0 auto-fixed; 1 honesty-convention discrepancy recorded (no code or test change required).
**Impact on plan:** None on LAND-01/LAND-02 discharge; LEG 2's actual result is a stronger confirmation than the one predicted.

## Issues Encountered

None. All three cold AVR builds and both native test runs reproduced plan 158-02's own figures exactly on the first attempt; no D-04 re-run was needed.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 05 (BASE-01/checker-convention close-out) can now cite this plan's mechanically-verified figures and the confirmed byte-unchanged status of `size_baseline_base01.json` and `scripts/check_size_baseline.py`.
- Plan 06 (after-figures) can cite: LEG 1's verbatim PASS line (the RED-to-GREEN flip), LEG 3's verbatim PASS line (LAND-02's one-sided evidence), the four unmoved MERGE-05 literals, the severance inventory (4 new + 2 in place, Groups 2/3 explicitly not needed), and BASE-01 confirmed byte-unchanged across the whole phase (785e644 -> HEAD).
- Plan 07 (ROADMAP/REQUIREMENTS correction) can cite this plan's own commit `e730068` and its native-count correction (172 stale -> 184 true) as further confirmation of C-1's `172 -> 184` correction already recorded in `158-before-figures.md`.
- No blockers.

---
*Phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only*
*Completed: 2026-08-24*

## Self-Check: PASSED

- FOUND: firestarter/scripts/baseline/size_baseline.json
- FOUND: firestarter/tests/fixtures/captured_build_v158_uno.log
- FOUND: firestarter/tests/fixtures/captured_build_v158_uno328pb.log
- FOUND: firestarter/tests/fixtures/captured_build_v158_leonardo.log
- FOUND: firestarter/tests/fixtures/planted_size_baseline_flash_regression_v158.log
- FOUND: firestarter/tests/fixtures/captured_test_native_summary.log
- FOUND: firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log
- FOUND: firestarter/tests/test_check_size_baseline.py
- FOUND commit (firestarter): e730068 (test(158-04): re-record size_baseline.json from cold builds and sever fixtures onto v158)
