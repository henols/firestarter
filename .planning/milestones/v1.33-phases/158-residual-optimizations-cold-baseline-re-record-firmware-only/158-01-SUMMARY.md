---
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
plan: "01"
subsystem: infra
tags: [platformio, pytest, jsmn, json-parser, size-baseline, ci-gates, measurement]

requires:
  - phase: 157-command-decode-table-handle-type-narrowing-firmware-only
    provides: "184/184/17 native case count on both native envs at 785e644; the field-table + type-narrowing landing this phase's cold measurement anchors to"
provides:
  - "The COLD pre-phase position of every AVR/native figure Phase 158 moves, with the producing command recorded per figure"
  - "LAND-04 discharged with both clauses proven by command output (no CI workflow invokes check_size_baseline.py as a size gate; the checker's own pytest DOES run in CI at build.yml:161)"
  - "LAND-07 discharged with three re-derived, re-runnable token bounds (50/14, 51/13, 55/9), refuting the criterion's 57/7"
  - "LAND-08 discharged with four new same-tree timed native runs plus the milestone's prior corpus, and the three D-04 prohibitions stated in the record"
  - "The default-mode gate recorded RED with every failing line verbatim, so plan 04's flip to GREEN is falsifiable"
  - "The four legs that will redden on the baseline re-record, named with current line numbers, fixture families and remedies, kept distinct from the four porcelain legs"
affects: [158-02, 158-04, 158-05, 158-07, 159-close]

tech-stack:
  added: []
  patterns:
    - "Cold-measurement recipe: rm -rf .pio/build/<env> + exactly one pio run -e <env>, never pio run -t clean and never check_size_baseline.py --rebuild"
    - "Before-figures record convention (Phase 155/156/157 lineage): every number carries its verbatim producing command; corrections to ROADMAP/REQUIREMENTS prose live in the record's supersedes/corrections-index, never in the source documents"

key-files:
  created:
    - .planning/v1.33/158-before-figures.md
  modified: []

key-decisions:
  - "OD-1 through OD-10 confirmed and restated in the record (no re-litigation): LAND-05 taken, LAND-06 declined, LAND-03 fixed via the axis-split argument, the FLOOR carry-forward closed by plan 05, jsmn.h's dead duplicate left unedited, ARM verified only if the toolchain installs, *_v153* retired-in-place-and-kept, ROADMAP/REQUIREMENTS edited by plan 07 only, neither gitlink re-pinned."
  - "LAND-07's chip-database bound (bound a) required adding ALL of eprom_operations.py's optional runtime keys (address, read-settling-delay, read-strobe-us) to each chip's convert_to_programmer() output, not merely cmd -- this reproduces the research's 50/14 figure exactly; omitting those three keys understates the bound by 6 tokens (44 vs 50), which was caught and corrected during this task."
  - "check_build_warnings.py's bare (no-argument) invocation is NOT a valid gate leg -- its own never-vacuous guard fails it (exit 1, 'no envs examined'). The plan's own acceptance criterion assumed a bare invocation exits 0; the record states the actual observed behavior (bare: exit 1; with --log against the three cold AVR logs: exit 0, all three envs clean) rather than forcing the plan's original expectation."

requirements-completed: [LAND-04, LAND-07, LAND-08]

coverage:
  - id: D1
    description: "Cold pre-phase AVR ledger (uno/uno328pb/leonardo flash+RAM, zero warnings) and native ledger (184/184/17 x4 runs) captured and recorded"
    verification:
      - kind: other
        ref: "manual rm -rf + pio run / pio test invocations, teed to /tmp/gsd-158/pre-*.log, transcribed into .planning/v1.33/158-before-figures.md sections 2-3"
        status: pass
    human_judgment: false
  - id: D2
    description: "LAND-04 discharged: both clauses proven by grep/ls command output against .github/ in all three repos"
    requirement: LAND-04
    verification:
      - kind: other
        ref: "grep -rn check_size_baseline .github/ (exit 1, all three repos); ls scripts/check_*.py | wc -l (=8); grep -n 'pytest tests/' build.yml (:161)"
        status: pass
    human_judgment: false
  - id: D3
    description: "LAND-07 discharged: three token bounds re-derived by a kept, re-runnable script against real pinouts.json/chip_database.json"
    requirement: LAND-07
    verification:
      - kind: other
        ref: "/tmp/gsd-158/land07_tokens.py output: 50/14, 51/13, 55/9 -- matches 158-RESEARCH.md F-7 exactly"
        status: pass
    human_judgment: false
  - id: D4
    description: "LAND-08 discharged: four new same-tree timed native runs (3x native, 1x native_nodevtools), all 184/184/17, plus the three D-04 prohibitions stated in the record"
    requirement: LAND-08
    verification:
      - kind: other
        ref: "pio test -e native (x3), pio test -e native_nodevtools (x1); durations 55.035s/40.820s/38.763s/50.987s, no case-count mismatch"
        status: pass
    human_judgment: false
  - id: D5
    description: "Default-mode gate recorded RED (8 verbatim failing lines) against the live size_baseline.json, establishing the falsifiable pre-state for plan 04's GREEN flip"
    verification:
      - kind: other
        ref: "python3 scripts/check_size_baseline.py --avr-log ... --native-log ... (exit 1, 8 FAIL: lines, recorded verbatim in section 4)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The four reddening legs (test_clean_avr_all_three_envs_pass, test_clean_native_both_envs_pass, test_planted_flash_regression_flips_checker_to_failure, test_default_mode_is_unchanged_by_the_new_flag) located by reading current source, distinguished from the four porcelain legs"
    verification:
      - kind: other
        ref: "grep -n 'def test_...' tests/test_check_size_baseline.py; grep -n porcelain tests/test_requirement_case_mapping_v131.py tests/test_trace_segment_exhaustiveness_v131.py"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-08-24
status: complete
---

# Phase 158 Plan 01: Cold Pre-Phase Baseline + LAND-04/07/08 Record Summary

**Cold-measured the pre-phase AVR/native position on all three targets and both native envs, re-derived LAND-07's token arithmetic to 50/14 - 51/13 - 55/9 (refuting the criterion's 57/7), and recorded the default-mode gate RED verbatim so plan 04's flip to GREEN is falsifiable.**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-08-24T09:16:34Z
- **Completed:** 2026-08-24T09:37:46Z
- **Tasks:** 3
- **Files modified:** 1 (`.planning/v1.33/158-before-figures.md`, net-new)

## Accomplishments
- Captured a genuinely COLD position on all three AVR targets (`uno` 23090/1562, `uno328pb`
  23138/1568, `leonardo` 25234/2003, zero warnings each) via `rm -rf .pio/build/<env>` + exactly
  one `pio run -e <env>` per env — never `pio run -t clean`, never `check_size_baseline.py
  --rebuild`.
- Ran `pio test -e native` three times and `pio test -e native_nodevtools` once: all four runs
  184/184 cases, 17 suites, no case-count flake this session; duration still spread 1.42x
  (38.763s–55.035s) across three identical-tree `native` runs — the D-04 evidence LAND-08 needed.
- Ran the full `pytest tests/ -q -o addopts=""` suite from the canonical checkout: 355 passed, 0
  skipped, proving the 32 cross-repo `test_flash_path_record_sync.py` legs ran (F-12).
- Proved LAND-04's two clauses by command output: zero `.github/` workflow references
  `check_size_baseline` in any of the three repos (of 8 `scripts/check_*.py`, only
  `check_release_assets.py` is CI-invoked); `build.yml:161`'s `pytest tests/ -v` DOES run this
  checker's own gate suite in CI, on `push: branches: ['**','!beta']`.
- Wrote and ran `/tmp/gsd-158/land07_tokens.py`, re-deriving LAND-07's three token bounds from
  `pinouts.json` and `chip_database.json`: **50/14** (real chip-database max, `W29C020` family),
  **51/13** (real pin-map max, `DIP32_27C020`), **55/9** (field-wise-maximum synthetic, no real
  record). All three match `158-RESEARCH.md` F-7 exactly, refuting the criterion's `57`/`7`.
- Ran the canonical MERGE-05 `--avr-log` invocation (exit 0, three negative flash deltas) and
  `--rebuild` invocation (exit 1, exactly two `cases baseline=141 observed=184` lines, zero AVR
  lines — LAND-03's pre-fix mechanism, C-12) against `size_baseline_base01.json`.
- Ran default mode against the live `size_baseline.json`: RED, 8 failing lines captured verbatim
  (3 AVR flash/RAM pairs + 2 native case-count lines).
- Located, by reading current source, the four `tests/test_check_size_baseline.py` legs that will
  redden on plan 04's re-record (with line numbers, fixture families, and remedies), and the four
  `_git_porcelain`-asserting legs in `test_requirement_case_mapping_v131.py` /
  `test_trace_segment_exhaustiveness_v131.py` that redden for any dirty file — kept as two
  distinct sets per Pitfall 4.
- Wrote and committed `.planning/v1.33/158-before-figures.md` (14 sections, 13 correction rows
  C-1..C-13, 10 OD decision bullets, 12 coverage ceilings) as a single-path commit.

## Task Commits

1. **Task 1: Capture the pre-phase position** (measurement only, no file changes) — folded into
   the record committed in Task 3.
2. **Task 2: Re-derive LAND-07's token arithmetic and prove LAND-04's two clauses** (derivation
   only, no tracked file changes) — folded into the record committed in Task 3.
3. **Task 3: Write and commit the before-figures record** — `d78f9354` (docs)

**Plan metadata:** (this document + STATE.md/ROADMAP.md updates, committed separately per the
final-commit step)

_Note: Tasks 1 and 2 of this plan are measurement/derivation-only per the plan's own file-scope
(`files_modified: [.planning/v1.33/158-before-figures.md]`); no tracked file exists to commit
until Task 3 writes the record itself, so all three tasks' work lands in the single Task 3 commit._

## Files Created/Modified
- `.planning/v1.33/158-before-figures.md` — the authoritative pre-phase record: cold AVR/native
  ledgers, the gate ledger with every leg's exit status and verbatim output, the one-sidedness
  quotes, the four reddening legs vs. four porcelain legs, the severance plan, LAND-04's two
  clauses, LAND-07's three token bounds, all twelve coverage ceilings, all ten OD decisions, and
  the thirteen-row corrections index (C-2/C-3/C-13 left open for `158-after-figures.md`).

## Decisions Made
- LAND-07's chip-database bound required merging ALL of `eprom_operations.py`'s optional runtime
  keys (`address`, `read-settling-delay`, `read-strobe-us`) into each chip's wire dict, not just
  `cmd` — this was discovered by comparing an initial 44-token result against research's stated
  50, and confirmed correct once fixed (exact match).
- `check_build_warnings.py`'s bare invocation exits 1 via its own never-vacuous guard rather than
  the plan's assumed exit 0; recorded both the bare-invocation behavior and the correct
  `--log`-qualified invocation (exit 0) rather than silently forcing the plan's original
  expectation to appear true.
- Leonardo's Caterina headroom (`28672 − 25234 = 3438 B`) is recorded as confirming, not
  superseding, `157-after-figures.md`'s own `3438 B` figure at the same commit — C-13 stays open
  pending LAND-05/06 landing in later plans of this phase.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] LAND-07's chip-database token-count script initially undercounted by omitting optional runtime keys**
- **Found during:** Task 2 (writing `/tmp/gsd-158/land07_tokens.py`)
- **Issue:** The first version of the script added only `cmd` to each chip's `convert_to_programmer()` output before counting tokens, producing 44 tokens for the `W29C020` family — 6 tokens short of research's stated 50.
- **Fix:** Added the remaining optional runtime keys `eprom_operations.py` can merge (`address`, `read-settling-delay`, `read-strobe-us`) to reproduce the maximal real command for each chip.
- **Files modified:** `/tmp/gsd-158/land07_tokens.py` (scratch script, not committed — this plan writes only `.planning/v1.33/158-before-figures.md`)
- **Verification:** Re-run script now prints 50/14, 51/13, 55/9 — exact match to `158-RESEARCH.md` F-7's independently-derived figures.
- **Committed in:** N/A (scratch file under `/tmp/`, not a tracked artifact of this plan)

**2. [Rule 1 - Bug] Corrected a first draft of the same script's pinouts.json field access**
- **Found during:** Task 2
- **Issue:** The script initially read `address-bus-pins`/`static-high-pins`/`rw-pin`/`vpp-pin` directly off each `pinouts.json` top-level record, but those fields are actually nested under a `pins` sub-key — the initial run reported `max_bus=0`, `max_static_high=0`.
- **Fix:** Changed field access to `rec.get("pins", rec)` before reading the four sub-fields.
- **Files modified:** `/tmp/gsd-158/land07_tokens.py`
- **Verification:** Re-run reports `max_bus=19`, `max_static_high=1`, matching the DIP32_STD/24-pin records' known shapes.
- **Committed in:** N/A (scratch file)

---

**Total deviations:** 2 auto-fixed (both Rule 1, both confined to a scratch derivation script
under `/tmp/`, neither touching any tracked file). **Impact on plan:** Both fixes were necessary
to make LAND-07's re-derivation match the phase's own research and produce a reproducible,
correct record. No scope creep — the committed record (`158-before-figures.md`) reflects only the
corrected, final script output.

## Issues Encountered
- The plan's task 1 acceptance criterion for `check_build_warnings.py` (leg (a)) assumed a bare,
  no-argument invocation exits 0. The checker's own documented never-vacuous guard makes this
  false (exit 1, "no envs examined"). Resolved by recording the actual observed behavior for both
  the bare invocation and the correct `--log`-qualified invocation, rather than treating the
  plan's literal text as ground truth. This is a plan-authoring gap, not a firmware or checker
  defect — no code was changed.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 02 (`jsmntok_t` narrowing) can proceed against the confirmed 184/184/17 native baseline
  recorded here.
- Plan 04 (baseline re-record + severance) has the cold recipe, the default-mode RED shape to
  flip, the four reddening legs with remedies, and the `*_v158*` fixture membership (4 new files
  plus 2 updated in place) all handed forward in `158-before-figures.md` §6-7 and §16.
- Plan 05 (checker-convention close-out) has BASE-01's four `141` integers, the two false
  CI-coverage paragraphs, and the current `FLOOR`/`FIXTURE_FLOOR` values against the shipped
  counts (8 checkers, 30 planted fixtures).
- Plan 07 (ROADMAP/REQUIREMENTS scope-correction) has the exact figures and correction IDs to
  apply (C-1, C-4/C-5, C-6) named in the record's §16 handoff.
- No blockers. `git -C firestarter status --porcelain` is empty; the `firestarter`/`firestarter_app`
  gitlink drift is pre-existing (OD-10) and unaffected by this plan.

---
*Phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only*
*Completed: 2026-08-24*

## Self-Check: PASSED

- FOUND: `.planning/v1.33/158-before-figures.md`
- FOUND: commit `d78f9354` (`git log --oneline --all | grep d78f9354`)
- FOUND: `/tmp/gsd-158/land07_tokens.py` (scratch, not a tracked artifact)
- FOUND: `/tmp/gsd-158/pre-cold-{uno,uno328pb,leonardo}.log` (scratch, not tracked)
- FOUND: `.planning/phases/158-residual-optimizations-cold-baseline-re-record-firmware-only/158-01-SUMMARY.md` (this file)
