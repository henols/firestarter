---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 11
subsystem: docs
tags: [honesty-ledger, claim-gate, py32f071, close-02, evidence-tiers, d17-residual]

requires:
  - phase: 130-close-honesty-ledger-claim-gate-release-decision (plan 03)
    provides: "the D-11 USB descriptor swap and the confined ARM delta this ledger's decision-only-unverified tier cites"
  - phase: 130-close-honesty-ledger-claim-gate-release-decision (plans 06-10)
    provides: "all five planning files (PROJECT.md, STATE.md, ROADMAP.md, REQUIREMENTS.md, notes/py32f071-port-branch-state.md) green under check_record_corrections.py, and the mechanism corrections this ledger cites without restating"
  - phase: 124-firmware-integration-merge
    provides: "the AVR flash/RAM deltas and the A-5 discharge citation (124-NONREGRESSION.md §F4d)"
  - phase: 127-host-dfu-installer
    provides: "the HOST-03 mock-only ceiling paragraph and the HOST-06 UM1504 residual (127-NONREGRESSION.md §7, §3/§6)"
  - phase: 128-release-asset-fold
    provides: "the two CI rehearsal dispatches and the REL-03/REL-04 stated seams (128-NONREGRESSION.md §3, §7)"
provides:
  - "130-LEDGER.md — the single source of permitted wording both release-notes bodies (130-12) and the release decision (130-13) must match"
  - "The claim gate (check_permitted_claims.py) armed for the first time in the real Phase 130 directory: default-mode now FAILS as armed-but-incomplete, naming exactly the three still-missing contracted artifacts"
affects: ["130-12", "130-13", "130-16"]

tech-stack:
  added: []
  patterns:
    - "Evidence-tier grouping (D-09): six ### tiers ordered weakest-to-strongest instead of one row per requirement category, so the strength gradient is visible on the page"
    - "Dual-axis claim rows (D-12): every row's Class cell carries both a v1.22-style status token (PERMITTED/CONTEXT-ONLY/FORBIDDEN) and a Phase-129 sourcing tag ([VERIFIED]/[CITED]/[ASSUMED]/[UNVERIFIED-UNTIL-SILICON])"
    - "Self-reference escape (122-LEDGER.md:28 technique): forbidden claims cited by REQUIREMENTS.md file:line, never reproduced, to avoid tripping the ledger's own scanner"

key-files:
  created:
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-LEDGER.md
  modified: []

key-decisions:
  - "D-17's ship-gate tension is recorded as an owned residual, never as resolved, amended, or satisfied — the ledger points at 130-DECISION.md for the argument and states plainly a future reader may decide otherwise."
  - "The real-published-artifact tier's row is marked pending, with the cut tag recorded as an explicit not-yet-observed placeholder (no version string predicted) — the observation is owed to plan 130-15."
  - "PCB-03/FUT-N04's corrected VTOR fact and the toolchain-absence narrowing are cited as mechanism corrections plan 130-10 already made in REQUIREMENTS.md itself; this ledger does not restate REQUIREMENTS.md's wording, only cites it."
  - "F-10 (the QFN56/QFN32 contiguous-bus impossibility) is given top billing in the residuals list, ahead of HOST-01/04/06 and REL-03/04's F-8, per the plan's explicit instruction."
  - "The community inbox is stated as not empty (gh#20, gh#18) rather than silently omitted, per RESEARCH C-18."

requirements-completed: []  # This plan ticks NO requirement ids — CLOSE-02 is discharged only by plan 130-16

coverage:
  - id: D1
    description: "130-LEDGER.md written with identity header, ceiling, dual-axis key, and six evidence-tier claim tables (CI-compile-only, AVR-measured, native-simulated, mock-only, real-published-artifact, decision-only-unverified), every row dual-axed, no forbidden wording reproduced, no cut tag predicted"
    verification:
      - kind: other
        ref: "python3 structural-assertion script (caveat present, six tier names present, both key vocabularies present, no '3.0.0b15' literal, F4d/124-NONREGRESSION cited) -- PASS"
        status: pass
      - kind: other
        ref: "FIRESTARTER_CLAIMSCAN_TARGETS=<130-LEDGER.md> python3 check_permitted_claims.py -- PASS, exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "Negative space (eight deferrals, F-10-first residuals, D-17 owned as a tension), the CLOSE-02 four-item minimum coverage, the community-inbox non-claim, and the scanner-status paragraph all written; the claim gate's default-mode run transitions from UNARMED/exit-0 to armed-but-incomplete/exit-1, naming exactly the three not-yet-written artifacts"
    verification:
      - kind: other
        ref: "python3 check_permitted_claims.py (default mode) -- FAIL, exit 1, names 130-DECISION.md/130-RELEASE-NOTES-fw.md/130-RELEASE-NOTES-app.md exactly"
        status: pass
      - kind: unit
        ref: "python3 -m pytest test_check_permitted_claims.py -q -- 11 passed"
        status: pass
    human_judgment: false

duration: 65min
completed: 2026-08-02
status: complete
---

# Phase 130 Plan 11: Honesty Ledger — Evidence Tiers, Negative Space, and the Claim Gate's First Arming Summary

**Wrote `130-LEDGER.md` — the single source of permitted wording both release bodies must match — with six evidence tiers grouped weakest-to-strongest, every claim row dual-axed (status token + sourcing tag), D-17's ship-gate tension carried as an owned residual (never resolved), and observed the claim gate's default-mode run transition for the first time from `UNARMED:`/exit 0 to a named armed-but-incomplete `FAIL:`/exit 1.**

## Performance

- **Duration:** ~65 min
- **Tasks:** 2
- **Files modified:** 1 created (`130-LEDGER.md`) + this SUMMARY

## Accomplishments

- **Task 1** — wrote the identity header (firmware/host/meta branch tips with real HEAD SHAs, an explicit not-yet-observed cut-tag placeholder, the software-only oracle list), the composition note (cross-reference only, citing `v1.23-FLASH-PATH-DECISION.md`'s own line 28), the ceiling quoted verbatim with the forbidden claims cited by `.planning/REQUIREMENTS.md:14` rather than reproduced, both key blocks (the v1.22-style status key and Phase 129's sourcing vocabulary, with the orthogonality sentence stated explicitly), and six `###` evidence-tier tables — CI-compile-only (3 rows, citing two real CI dispatches), AVR-measured (4 rows, including the A-5 discharge citing `124-NONREGRESSION.md` §F4d), native-simulated (1 row, CFG-05's fake-backend coverage), mock-only (3 rows, including HOST-03's mock-only readback ceiling), real-published-artifact (1 row, marked pending, publication-only wording), and decision-only-unverified (2 rows, the provisional pin map and the USB identity decision). Every row's `Class` cell carries both a status token and a sourcing tag.
- **Task 2** — appended the mechanism-corrections section (three items: the PCB-04 reversal recorded as a reversal, the toolchain-absence narrowing plan 130-10 already made in `REQUIREMENTS.md`, and the claim-gate `_DEFAULT_TARGETS` repoint), the three-part negative space (exactly eight deferrals matching `.planning/REQUIREMENTS.md` §"Future Requirements" lines 109–128 identifier-for-identifier; the residuals list with **F-10 given top billing** ahead of HOST-01/04/06 and REL-03/04's F-8; the D-17 residual recorded as a tension, never a resolution, plus the two Phase 129 open hardware questions tagged `[UNVERIFIED-UNTIL-SILICON]`), the "what no test, gate or review can close" section naming all four of CLOSE-02's minimum-coverage items (the provisional pin map, `HOST_STUBS_RECORD_BUS`'s absence on ARM, the 572 µs/600 µs USB-ISR-vs-PROM timing figure cited as a different board's number, and HOST-03's mock-only ceiling), the community-inbox paragraph naming gh#20 and gh#18 explicitly, and the scanner-status paragraph stating the mechanizable-half-only non-claim with D-02's blocking operator wording review named as the non-mechanizable half.
- Observed and recorded the claim gate's arming transition (see below) — the first time `check_permitted_claims.py`'s default-mode run has produced anything other than `UNARMED:`/exit 0 in this milestone.

## Task Commits

1. **Task 1: Identity header, ceiling, dual-axis key, six evidence-tier tables** — `63de93d6` (docs)
2. **Task 2: Mechanism corrections, negative space, D-17 residual, scanner status** — `a4c4a874` (docs)

## Files Created/Modified

- `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-LEDGER.md` — created, 183 lines. The only content file this plan touches, per its own `files_modified` and the orchestrator's held-writes contract.

## Decisions Made

- **D-17's tension recorded, not resolved.** The ledger states the ship gate's binding force is unchanged, that this phase's disclosure of the interim USB pair is a judgment call (recorded as one, not as a settled reading of the registry's terms), and points at `130-DECISION.md` for the full argument rather than reproducing it. `grep -ci 'ship gate.*\(satisfied\|amended\|resolved\)'` returns 0.
- **The real-published-artifact row stays pending.** No cut tag is predicted anywhere in the file (`grep -c '3.0.0b15'` returns 0); the row's permitted wording is scoped to publication only ("a file with a specific name, carrying a specific version string, became a downloadable release asset"), never to the image running or booting.
- **Forbidden claims cited by location, never reproduced.** Per the 122-LEDGER.md:28 technique this plan was instructed to copy, `.planning/REQUIREMENTS.md`'s five forbidden phrasings are cited as `:14` rather than quoted — this is also why the ledger avoids the eight literal forbidden-phrase shapes everywhere else in its own prose (verified by the scanner's PASS below, not merely by inspection).
- **Mechanism corrections cited, not restated.** Plan 130-10's in-place `REQUIREMENTS.md` amendments (PCB-03/FUT-N04's VTOR correction, the toolchain-absence narrowing) are cited as already-made corrections in this ledger's "Mechanism corrections" section rather than re-derived or re-quoted at length, keeping `REQUIREMENTS.md` as the single copy of that wording.
- **F-10 given top billing**, listed before HOST-01/04/06 and REL-03/04's F-8 in the residuals sub-section, exactly as the plan's `must_haves` required.

## Deviations from Plan

None — plan executed exactly as written. Two small wording fixes were made during self-verification, both before either task's commit, and are recorded here for completeness rather than as deviations from the committed content:

- **[Rule 1 — self-caught, pre-commit] `HOST_STUBS_RECORD_BUS` named explicitly.** The first draft of the "absent ARM bus-trace oracle" bullet paraphrased the harness generically without naming it; the acceptance criteria requires the literal name. Fixed before Task 2's commit (`a4c4a874` already carries the corrected text — no separate commit needed since this was caught before the task's single commit).
- **[Rule 1 — self-caught, pre-commit] gh#20/gh#18 named explicitly.** The first draft of the community-inbox paragraph paraphrased the two issues ("a community-reported... failure" / "a second issue") instead of naming them; the acceptance criteria requires the literal issue numbers. Fixed before Task 2's commit, same commit as above.

## Issues Encountered

None. No auth gates, no checkpoints, no package installs — this plan ran only `python3`, `pytest`, `grep`, and `git` against files already present in the tree.

## The Claim Gate's Arming Transition — recorded verbatim, per this plan's `<gate_behavior_you_must_expect>`

**Before this plan's commits** (recorded by plan 130-06, reproduced for continuity):
```
$ python3 check_permitted_claims.py
UNARMED: none of the 4 named v1.23 closing artifacts for Phase 130 exist yet (130-LEDGER.md, 130-DECISION.md, 130-RELEASE-NOTES-fw.md, 130-RELEASE-NOTES-app.md) -- the close has not started, so the claim gate has nothing to scan yet. This is expected before Phase 130 runs.
exit=0
```

**After this plan's commits** (measured this session, both tasks landed):

Named-target run (the mechanical acceptance criterion for this plan):
```
$ FIRESTARTER_CLAIMSCAN_TARGETS=/workspaces/.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-LEDGER.md python3 check_permitted_claims.py
PASS: scanned ../130-close-honesty-ledger-claim-gate-release-decision/130-LEDGER.md; 1 file(s) carry the required silicon caveat (this PASS is the mechanizable half of the honesty criterion only -- see the module docstring's explicit non-claim)
exit=0
```

Default-mode run (no argv, no env seam — the real, unqualified invocation a human or CI would run):
```
$ python3 check_permitted_claims.py
FAIL: armed (at least one of the 4 named v1.23 closing artifacts exists) but not all 4 exist -- a half-written close is a hard failure (D-15). Missing: ['/workspaces/.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-DECISION.md', '/workspaces/.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-fw.md', '/workspaces/.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-app.md']
exit=1
```

Fixture suite, re-run to confirm the checker's own test coverage is unaffected by a real contracted artifact now existing:
```
$ python3 -m pytest test_check_permitted_claims.py -q
...........                                                              [100%]
11 passed in 0.35s
```

**This transition — `UNARMED:`/exit 0 → a named, itemised `FAIL:`/exit 1 — is expected and correct, not a regression.** It is D-15's all-or-nothing arming working for the first time in the real Phase 130 directory: the failure names **exactly** the three artifacts plans 130-12 (`130-RELEASE-NOTES-fw.md`, `130-RELEASE-NOTES-app.md`) and 130-13 (`130-DECISION.md`) have not yet written — nothing inside `130-LEDGER.md` itself is named as a problem. This is the positive, first-time evidence that plan 130-01's repoint of `_DEFAULT_TARGETS` (RESEARCH C-2, away from this checker's own Phase 123 directory to the sibling Phase 130 directory) took effect in the real tree, not merely in a test fixture.

## Self-Check Data (informational; formal Self-Check section follows)

- `FIRESTARTER_CLAIMSCAN_TARGETS=<130-LEDGER.md> python3 check_permitted_claims.py` → exit 0, `PASS:` naming the ledger.
- `python3 check_permitted_claims.py` (default) → exit 1, `FAIL:`, names exactly the three missing artifacts, none inside `130-LEDGER.md`.
- `python3 -m pytest test_check_permitted_claims.py -q` → 11 passed.
- `grep -c '3.0.0b15' 130-LEDGER.md` → 0.
- `grep -c 'required by pid.codes' 130-LEDGER.md` → 0.
- `grep -ci 'ship gate.*\(satisfied\|amended\|resolved\)' 130-LEDGER.md` → 0.
- Deferral count: 8 (`FUT-N02, FUT-N04, FUT-N05, FUT-N06, FUT-VPP, FUT-CAL, FUT-ORACLE, FUT-ARMSIZE`).
- `git status --short .planning/REQUIREMENTS.md .planning/ROADMAP.md .planning/STATE.md .planning/PROJECT.md` → empty (all four untouched).
- `git rev-parse --abbrev-ref HEAD` → `gsd/v1.23-py32f071-integration` (confirmed after every commit).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 130-12** (both release-notes bodies) and **plan 130-13** (`130-DECISION.md`) can now cite `130-LEDGER.md` as the single source of permitted wording; the claim gate is armed and will hold both of those plans to the same eight-forbidden-phrase / required-caveat standard this ledger already passes.
- **Plan 130-16** (the closing plan) can lift this plan's arming-transition transcript directly into `130-NONREGRESSION.md`, and confirm the claim gate reaches a full `PASS:` across all four contracted artifacts once 130-12/130-13 land.
- No requirement id was ticked by this plan, per its own frontmatter (`requirements: [CLOSE-02]`, ticked only by plan 130-16) and the orchestrator's held-writes instruction. `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, and `.planning/PROJECT.md` are all confirmed untouched.
- `git -C /workspaces rev-parse --abbrev-ref HEAD` confirmed `gsd/v1.23-py32f071-integration` after both task commits — plain `git commit` was used throughout, per this plan's sequential-executor instructions, avoiding the known `gsd-tools query commit` branch-switch hazard.

---
*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-LEDGER.md`
- FOUND: `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-11-SUMMARY.md`
- FOUND: commit `63de93d6` (Task 1)
- FOUND: commit `a4c4a874` (Task 2)
- FOUND: commit `84c5041` (this SUMMARY)
- `git status --short .planning/REQUIREMENTS.md .planning/ROADMAP.md .planning/STATE.md .planning/PROJECT.md` → empty (all four untouched)
- `git rev-parse --abbrev-ref HEAD` → `gsd/v1.23-py32f071-integration` (confirmed)
