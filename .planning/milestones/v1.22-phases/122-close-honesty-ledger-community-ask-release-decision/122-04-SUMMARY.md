---
phase: 122-close-honesty-ledger-community-ask-release-decision
plan: 04
subsystem: infra
tags: [non-regression, sdp-capability, ci-gates, pytest, pio-run, claim-scanner]

# Dependency graph
requires:
  - phase: 122-03
    provides: "The two inbound merge commits (firestarter_app@4001396, firestarter@953f748) this plan tests — the tree that will actually be published"
provides:
  - "122-NONREGRESSION.md — the CLOSE-01 gate-result artifact for the merged tree: four existing mechanisms, an independent second measurement path, the measured 43/41 SDP split, the eleven-row cross-repo gate, both full suites, both beta workflows' local gate sets, and the validation-ceiling statement"
  - "A recorded, investigated app-pytest count delta (1134 observed vs a stated-but-unreproducible 1150 baseline in prior phase artifacts), traced to git history rather than accepted or silently corrected"
affects: ["122-05", "122-06", "122-07", "122-13"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Independent second measurement path (raw JSON load + manual aggregation) run alongside a test suite's own assertion, so a claim never rests solely on the test's self-check"
    - "Claim-scanner tension resolved by citing the forbidden claim's location rather than reproducing its trigger phrase verbatim, since the scanner matches phrase shape regardless of quotation context — recorded as the gate working as intended, not routed around"

key-files:
  created:
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-NONREGRESSION.md
  modified: []

key-decisions:
  - "Investigated the 1134-vs-1150 app pytest delta via git log (confirmed zero firestarter_app commits between Phase 121's c3c9424 and 122-03's merge) rather than either silently reporting 1150 or accepting 1134 unexplained; recorded the 1150 figure in 122-RESEARCH.md/122-VALIDATION.md/122-04-PLAN.md as an unreproducible documentation inconsistency, since the true pre-merge baseline (independently on record in 121-NONREGRESSION.md) is 1134"
  - "Did not literally quote REQUIREMENTS.md's forbidden claim inside 122-NONREGRESSION.md, because its exact wording is the claim-scanner's own trigger phrase and would fail Task 3's own scanner-clean acceptance criterion regardless of quotation context; cited it by file:line instead and explained why, preserving both the scanner's fail-closed design and the artifact's honesty obligation"
  - "Did not run check_ledger.py at any point, per explicit plan mandate (C-4) — its RED is pre-existing from v1.19 Phase 104's flash3/flash4 rename and is recorded with that cause, never chased"

requirements-completed: []  # This plan ticks nothing — CLOSE-01 closes only in 122-13 per plan scope

coverage:
  - id: D1
    description: "CLOSE-01's four existing mechanisms (0x0D UNVERIFIED grep, DB invariant test, diff_db.py identity, support_status write-scan) all green on the merged tree, plus an independent second measurement path and the measured 43/41 SDP ALLOW/REFUSE split reproducing every recorded figure exactly"
    requirement: "CLOSE-01"
    verification:
      - kind: other
        ref: "grep -c UNVERIFIED PROTOCOL-LEDGER.md == 1; pytest tests/test_sdp_db_invariant.py -q == 4 passed; diff_db.py exit 0; check_no_community_support_status_write.py exit 0; sdp_capability_for_entry over 84 entries == 43/41 total, DIP24_2816 0/19"
        status: pass
    human_judgment: false
  - id: D2
    description: "The eleven nine-row cross-repo non-regression commands all PASS on the merged tree, with row 5 confirmed idempotent against the pre-existing baseline and row 9b's file list (naming the merge-conflicted submit.py) confirmed unchanged from Phase 121's record"
    requirement: "CLOSE-01"
    verification:
      - kind: other
        ref: "check_no_log_in_sdp_window.py, check_is_memory_cmd_no_ifdef.py, gen_sdp_bus_config.py, check_dispatch.py, check_devtest_orchestrator.py all PASS; combined pytest runs 18 passed + 19 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both full suites and both beta workflows' local gate sets pre-validated on the merged tree: app pytest, firmware native, firmware script tests, pio run across three envs, both codegen drift gates, catalog validity, three-way cmp identity"
    requirement: "CLOSE-01"
    verification:
      - kind: other
        ref: "pytest -v (app) == 1134 passed (delta investigated, see key-decisions); pio test -e native == 141/141; pytest tests/ -v (firmware) == 8 passed; pio run == 3/3 SUCCESS, unchanged flash/RAM; both codegen drift gates NO DRIFT"
        status: pass
    human_judgment: false
  - id: D4
    description: "122-NONREGRESSION.md written in the established shape (8 sections, >=90 lines), quotes the permitted claim verbatim, cites the forbidden claim by location, states the criterion-4 non-claim explicitly, and passes its own courtesy claim-scan run"
    requirement: "CLOSE-01"
    verification:
      - kind: other
        ref: "wc -l == 346 (>=90); grep -c 'all 84' == 0; FIRESTARTER_CLAIMSCAN_TARGETS=<path> python3 check_permitted_claims.py exits 0"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-30
status: complete
---

# Phase 122 Plan 04: Merged-Tree Non-Regression Sweep — CLOSE-01's Four Mechanisms + Eleven-Row Gate + Both Full Suites + Both Beta Workflows' Gate Sets Summary

**Re-ran every CLOSE-01 mechanism, the eleven nine-row cross-repo commands, both full suites, and both beta workflows' local gate sets against the actual merged tree (`firestarter_app@4001396`, `firestarter@953f748`) — all green, with one investigated and explained pytest-count discrepancy (1134 vs a stated-but-unreproducible 1150 baseline) and one deliberate claim-scanner workaround (citing the forbidden claim by location instead of quoting its trigger phrase verbatim) recorded in `122-NONREGRESSION.md`.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-07-30 (session start)
- **Completed:** 2026-07-30
- **Tasks:** 3 completed
- **Files modified:** 1 (`122-NONREGRESSION.md`, created)

## Accomplishments

- Ran all four of CLOSE-01's existing mechanisms on the merged tree: `0x0D` `UNVERIFIED` grep count 1 (ledger provably read, not written); `test_sdp_db_invariant.py` 4 passed; `diff_db.py` exit 0 (identity = 2 explained/0 new/0 removed); `check_no_community_support_status_write.py` exit 0.
- Computed an independent second measurement path directly from `chip_database.json` (never trusting the test's own assertion): 746 total chips, 84 at `algorithm == 13`, `chip_id_check` set `{False}`, `support_status` 75 supported / 9 adapter-required, pinout counts 35/19/18/12 — every figure reproduced exactly.
- Measured the per-pinout SDP ALLOW/REFUSE split live via `sdp_capability.sdp_capability_for_entry` over all 84 entries: 43 ALLOW / 41 REFUSE total, with `DIP24_2816` at 0/19 — reproducing STATE.md's derived partition exactly, and recorded the "emission-traced byte-exact" vs "operation-permitted" distinction as a named finding.
- Ran all eleven nine-row cross-repo commands on the merged tree, all PASS, with row 5's idempotence confirmed against the pre-existing `?? firestarter/` baseline and row 9b's PASS line (naming `submit.py` explicitly, one of the two merge-conflicted files) confirmed unchanged from Phase 121's record.
- Ran both full suites: app pytest 1134 passed (29 snapshots) — investigated a discrepancy against a stated 1150 pre-merge baseline appearing in `122-RESEARCH.md`/`122-VALIDATION.md`/this plan's own text, traced via `git log` to a documentation inconsistency rather than a regression (see Deviations); firmware native 141/141 across 17 suites; firmware script tests 8 passed — both matching baseline exactly.
- Pre-validated both beta workflows' local gate sets: catalog validity, both codegen drift gates (`messages.h`, `messages.py`) clean by `git diff --exit-code`, `pio run` 3/3 SUCCESS with flash/RAM figures unchanged from Phase 121 (Leonardo 26072/28672, Uno 23932/32256, uno328pb 23976/32384).
- Confirmed the four pre-existing `ruff check`/`ruff format` findings and the mypy watermark are unchanged and outside v1.22's own diff; confirmed `catalog-sync-check.yml` and firmware `build.yml`'s `native_nodevtools` step remain red-until-`main`-merge by design.
- Never ran `check_ledger.py` — recorded its pre-existing RED with the v1.19 Phase 104 cause per explicit plan mandate (C-4).
- Wrote `122-NONREGRESSION.md` (346 lines, 8 sections) and ran the Wave 0 claim scanner over it as a courtesy check — passed after two rewording rounds (see Deviations).
- Confirmed all three working trees show only the named pre-existing dirt after every gate ran, and the meta gitlinks stayed pinned at `0048b3d`/`96e0622`.

## Task Commits

1. **Tasks 1-3: Run all mechanisms/gates/suites and write `122-NONREGRESSION.md`** — `14e6b06` (docs; the plan's only `files_modified` target is this single artifact, so all three tasks land in one commit)

**Plan metadata:** captured in the final phase-level commit alongside STATE.md/ROADMAP.md updates.

_Note: no TDD tasks in this plan; all three are `type="auto"` verification/documentation tasks writing to the same single file._

## Files Created/Modified

- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-NONREGRESSION.md` — the merged-tree gate-result artifact: CLOSE-01's four mechanisms + independent measurement + SDP split, the eleven-row cross-repo gate table, full-suite results with the delta investigation, both beta workflows' pre-validated gate sets, known-and-explained conditions, the validation-ceiling statement, and deliberately-not-taken actions.

## Decisions Made

- Investigated (rather than silently reported or silently corrected) the 1134-vs-1150 app pytest discrepancy: `git log` confirmed the app repo's pre-merge branch HEAD (`c3c9424`) is Phase 121's own final commit, whose independently-recorded count (`121-NONREGRESSION.md`) is 1134 — meaning the true pre-merge baseline is 1134, and the "1150" figure in `122-RESEARCH.md`/`122-VALIDATION.md`/`122-04-PLAN.md` is not reproducible against the actual git history. Recorded as a documentation inconsistency in those artifacts, not a regression in the merged tree.
- Did not literally quote the forbidden claim from `REQUIREMENTS.md:152` inside `122-NONREGRESSION.md`, because its exact wording is precisely the claim-scanner's trigger phrase and any verbatim reproduction fails the scanner regardless of quotation context (confirmed live: the first draft's verbatim quote produced two `works-on-silicon` false-triggers and a missing-caveat failure). Cited the forbidden claim by file:line instead, added the required caveat sentence verbatim (`no AT28C silicon was tested`), and recorded the reasoning in the artifact itself — per the plan's own instruction to reword rather than weaken the pattern set.
- Reworded two literal "all 84" occurrences (one describing the SDP-split measurement's own scope, one inside a hedge about the honest 66-of-84 figure) to eliminate the exact substring, since `grep -c 'all 84'` is a hard acceptance gate independent of context.
- Did not run `check_ledger.py` at any point (C-4); did not edit `.github/`, `messages.h`, or `PROTOCOL-LEDGER.*`; did not push anything.

## Deviations from Plan

### Auto-fixed Issues

None — no code defect was found or fixed. This plan runs read-only gates and writes one documentation artifact.

### Documented Findings (not auto-fixed, recorded per plan instruction)

**1. [Rule 1 - investigated discrepancy, not a code/git defect] App pytest count 1134 observed vs 1150 stated pre-merge baseline**
- **Found during:** Task 2 (full-suite run)
- **Issue:** `122-RESEARCH.md`, `122-VALIDATION.md`, and `122-04-PLAN.md` all state the app pytest pre-merge baseline as "1150 passed", but this session's live run on the merged tree measured 1134 passed.
- **Investigation:** `git -C firestarter_app log --oneline` confirms zero `firestarter_app` commits landed between Phase 121's final commit (`c3c9424`) and 122-03's merge — meaning the true pre-merge branch HEAD is `c3c9424` itself. `121-NONREGRESSION.md`'s own independently-recorded final sweep at that exact commit states **1134 passed**, not 1150. The 84-count / SDP-split / DB-identity checks all independently confirm the merged tree's data is unchanged, so this is not a test-suite regression — it is a stale or miscomputed figure in three phase-122 planning artifacts that this plan does not have write access to correct (they belong to prior plans/RESEARCH, out of this plan's `files_modified` scope).
- **Resolution:** Recorded the observed 1134, the investigation, and the conclusion ("no regression vs the true pre-merge count") verbatim in `122-NONREGRESSION.md` §4, per the plan's explicit instruction: "If it differs, state the delta and its cause; do not round or paraphrase."
- **Files modified:** none beyond the plan's own artifact (`122-NONREGRESSION.md`).
- **Committed in:** `14e6b06`.

**2. [Rule 1 - claim-scanner interaction, not a defect] Verbatim forbidden-claim quote and two prose phrases tripped the courtesy claim scanner**
- **Found during:** Task 3 (writing and self-testing `122-NONREGRESSION.md`)
- **Issue:** The plan's action text calls for quoting REQUIREMENTS.md's forbidden claim verbatim; doing so literally (`"SDP lock/unlock works on an AT28C256."`) matches the scanner's `works-on-silicon` pattern by construction — the scanner is designed to catch exactly that phrase shape, regardless of quotation context. A first draft also used the phrases "works on real AT28C silicon" and "all 84" in unrelated prose, both of which independently tripped forbidden-pattern / literal-count checks.
- **Fix:** Reworded §7 to cite the forbidden claim by its `REQUIREMENTS.md:152` location instead of reproducing its exact wording, added an explicit note explaining why (the scanner's own module docstring predicts and endorses this outcome for negated/quoted reproductions), added the required caveat sentence verbatim, and reworded the two "all 84" occurrences and the "works on real AT28C silicon" phrase to remove the trigger substrings while preserving meaning.
- **Verification:** Re-ran `FIRESTARTER_CLAIMSCAN_TARGETS=<path> python3 check_permitted_claims.py` — exit 0, `PASS: scanned 122-NONREGRESSION.md; 1 file(s) carry the required silicon caveat`.
- **Files modified:** `122-NONREGRESSION.md` (§7, and two other line edits).
- **Committed in:** `14e6b06`.

---

**Total deviations:** 0 auto-fixed; 2 documented findings (one investigated discrepancy, one claim-scanner interaction), both resolved within this plan's own artifact.
**Impact on plan:** None on correctness — the merged tree's CLOSE-01 surface is genuinely green; both findings are documentation/tooling-interaction discoveries, fully recorded rather than smoothed over.

## Issues Encountered

None beyond the two documented findings above — every gate executed on first attempt and passed; the only iteration required was rewording `122-NONREGRESSION.md`'s own prose to satisfy its own courtesy claim scanner.

## User Setup Required

None — no external service configuration required. Nothing was pushed; no GitHub Actions workflow fired.

## Next Phase Readiness

- `122-NONREGRESSION.md` is the committed, load-bearing gate-result artifact CONTEXT constraint 6 requires: CLOSE-01's entire verification surface is proven green on the exact tree (`firestarter_app@4001396`, `firestarter@953f748`) that wave 6 will push, not an earlier commit.
- Plans 122-05 (`122-LEDGER.md`), 122-06 (PROJECT.md EIGHTH CORRECTION), and 122-13 (requirement ticking) can cite this artifact's measured figures directly: 43/41 SDP split with `DIP24_2816` 0/19, 66-of-84 trace coverage, the app-pytest delta investigation, and the criterion-4 non-claim statement.
- No blockers. No requirement checkbox was ticked (CLOSE-01 closes only in 122-13, per this plan's scope).
- Meta gitlinks remain correctly unchanged (`0048b3d`/`96e0622`); no gitlink work needed until `/gsd-complete-milestone`.

---
*Phase: 122-close-honesty-ledger-community-ask-release-decision*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-NONREGRESSION.md`
- FOUND: `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-04-SUMMARY.md`
- FOUND: `14e6b06` (122-NONREGRESSION.md commit)
- FOUND: `2ce567a` (initial SUMMARY commit)
