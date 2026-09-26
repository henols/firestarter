---
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "07"
subsystem: firmware
tags: [phase-landing, size-reduction, dedup, boolean-convention, golden-inventory, requirements-closure]

requires:
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 01
    provides: "156-before-figures.md -- the authoritative before-half baselines this record pairs against (31 __udivmodhi4, 24660/24708/26804 flash, 348/0/0 pytest, seven corrections index)"
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 02
    provides: "the two DEDUP-03 blind-spot oracles (under-voltage severity pairing, chip-ID message id), written and proven RED/GREEN against the PRE-refactor code -- this plan re-proves them against the shipped, post-refactor code"
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 03
    provides: "mem_util_report_voltage, DEDUP-01's own measured -268 B"
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 04
    provides: "mem_util_report_chip_id, DEDUP-02's own measured -158 B, the six-divergence resolution table"
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 05
    provides: "the boolean-convention flip (nine wrappers, six engine returns), measured size-identical with the three .hex SHA pairs"
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 06
    provides: "tests/test_boolean_convention_source_contract_v133.py, proven RED four ways and GREEN on the real tree"
provides:
  - ".planning/v1.33/156-after-figures.md -- the phase's authoritative outcome record: all eight phase-gate legs, the four-probe re-proof against the shipped code, the resolved -268/-158 split, the mechanical __udivmodhi4 and per-symbol ledgers, the six-divergence table, the seven coverage ceilings in final form, and the corrections index closed out"
  - "All four DEDUP-01..04 requirements ticked complete in REQUIREMENTS.md with discharge evidence cited, closing the traceability table's four Pending rows"
  - "REQUIREMENTS.md DEAD-06 corrected in place (C-7): its uniqueness claim about touching a test file is false"
  - "ROADMAP.md Phase 156 marked PHASE CLOSED with a plan-count and done-annotation update"
affects: [157, 158, 159]

tech-stack:
  added: []
  patterns:
    - "Post-refactor probe re-proof: a planted-negative oracle written against the PRE-refactor code is regression evidence for that code, but a claim about the SHIPPED code requires re-planting the same substitution where the mutation point now lives (inside a shared helper) and re-observing the same RED/GREEN pair -- otherwise the claim is about a tree that no longer exists"
    - "Confirm-vs-supersede framing for a split figure: when two independent per-commit measurements land exactly on an inherited, previously-UNVERIFIED split, the honest statement is CONFIRMED (with the measured values cited), not SUPERSEDED and not silently presented as if the inherited figure had always been measured"

key-files:
  created:
    - .planning/v1.33/156-after-figures.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Confirmed C-3 as CONFIRMED, not superseded: plan 03's own -268 B and plan 04's own -158 B sum exactly to the phase's measured -426 B and match the ROADMAP's inherited -268/-158 split precisely. Stated as confirmation of an independently re-measured value, not as inheriting the ROADMAP figure."
  - "Closed DEDUP-03 with a probe-by-probe re-proof against the shipped code rather than citing plan 02's pre-refactor RED/GREEN evidence alone -- two of the four mutation points (B and D) now live inside shared helpers (mem_util_report_voltage, mem_util_report_chip_id) rather than in four separate blocks, so the same substitutions were re-planted at their new location and re-observed flipping from BLIND to RED."
  - "Left the STATE.md frontmatter stopped_at field untouched (still reads Phase 154), matching this milestone's established convention across all six prior 156-0X plans, none of which updated it either -- only the body's Current Position and ## Session Stopped-at fields carry the live narrative. Updated the ## Session block's own Stopped-at line for the first time this phase (it had been stale at Phase 154 since before plan 01), per this plan's explicit instruction that the scraper reads the body, not the frontmatter."
  - "Kept the ## Session Stopped-at narrative as a single unbroken line (not word-wrapped across multiple lines), matching every other Stopped-at entry in this file, after an initial word-wrapped draft was corrected before committing -- consistency with the file's own established single-line convention for scraped fields, not a functional requirement this plan's acceptance criteria enforced."

requirements-completed: [DEDUP-01, DEDUP-02, DEDUP-03, DEDUP-04]

coverage:
  - id: D1
    description: "All eight phase-gate legs run and recorded on the final tree, including the two no CI workflow invokes (native_loop_v131, check_size_baseline.py), with leg 1 run three times and the canonical baseline's pre-existing BASE-01 failure reproduced and attributed to Phase 158"
    requirement: "DEDUP-01"
    verification:
      - kind: unit
        ref: "pio test -e native (172/172 x3), -e native_nodevtools (172/172), -e native_loop_v131 (82/82); pytest tests/ -q (355 passed); pio run all three targets (24234/24282/26378, 1567/1573/2008); check_size_baseline.py --policy merge05 --rebuild (PASS); check_build_warnings.py --rebuild (PASS)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The four DEDUP-03 planted transpositions re-run in a throwaway worktree against the shipped, post-refactor tree at 1151dc4 -- probes B and D flip from BLIND (everywhere) to RED, closing both blind spots against the code that actually shipped"
    requirement: "DEDUP-03"
    verification:
      - kind: other
        ref: "This SUMMARY's Non-Vacuity / Planted-Negative Evidence section below -- probe A RED in native_loop_v131 (3 cases) / BLIND in native; probe B RED in native_loop_v131 (2 cases, was BLIND everywhere); probe C RED in native (2 cases); probe D RED in native (1 case, was BLIND everywhere); GREEN control 172/172 + 82/82 on the real tree after each revert"
        status: pass
    human_judgment: false
  - id: D3
    description: "-268/-158 split confirmed exactly against the phase's measured -426 B total; the branch-inventory golden's two re-derivations (23->22, 22->21) each landed inside their own commit so the gate was never red at a committed state"
    requirement: "DEDUP-01"
    verification:
      - kind: other
        ref: "156-03-SUMMARY.md (-268 B), 156-04-SUMMARY.md (-158 B); tests/golden/protocol_branch_inventory.json counts confirmed 21/1/20 this session"
        status: pass
    human_judgment: false
  - id: D4
    description: "DEDUP-04 closed: size-identical on all three AVR targets (re-confirmed byte-for-byte against plan 04's committed figures), the three .hex SHA pairs recorded as the expected divergence, the 9-to-1 negation reduction and its one surviving negation identified by name and line"
    requirement: "DEDUP-04"
    verification:
      - kind: unit
        ref: "pio run all three targets unchanged from plan 04's figures; grep -c 'return !op_execute_' == 0; grep -cE forwarding calls == 9; grep -n 'return !callback' -> one match at operation_utils.cpp:92"
        status: pass
    human_judgment: false
  - id: D5
    description: "All four requirement checkboxes flipped in REQUIREMENTS.md with discharging plan and artifact cited; traceability table rows updated from Pending; DEAD-06 corrected in place with the C-7 consequence; ROADMAP.md Phase 156 marked closed with no other phase's plans line or Coverage row moved (diff-verified); STATE.md advanced"
    requirement: "DEDUP-02"
    verification:
      - kind: other
        ref: "git diff -- .planning/REQUIREMENTS.md confined to the DEAD-06 append, the four DEDUP entries, and the four traceability rows (18 changed lines); git diff of pre/post ROADMAP.md snapshots confined to Phase 156's own section; git show --stat --name-only HEAD lists exactly 4 paths, all under .planning/"
        status: pass
    human_judgment: false

duration: ~1h
completed: 2026-08-23
status: complete
---

# Phase 156 Plan 07: Landing -- The Measured Ledger, the Gate Results and the Corrections Summary

**Ran all eight phase-gate legs on the final tree, re-proved DEDUP-03's evidence against the shipped code (two probes flipping from BLIND to RED at the code that actually ships), wrote the authoritative `.planning/v1.33/156-after-figures.md` record, and closed all four DEDUP requirements in `REQUIREMENTS.md` with the -426 B total confirming the -268/-158 split exactly.**

## Performance

- **Duration:** ~1h
- **Completed:** 2026-08-23
- **Tasks:** 3
- **Files modified:** 4 (1 created, 3 modified)

## Accomplishments

- **Anchored the phase.** `git rev-list --count adf1a31..HEAD` = **6** commits, listed by subject and reconciled against the per-plan record (plan 02 contributed 2, plans 03/04/05/06 one each). `git -C firestarter status --porcelain` empty and `git -C firestarter worktree list` showing only the primary tree plus the untouched `firestarter_py32_ci` sibling, both before and after this plan's own measurement work.
- **Ran the eight-leg phase gate on the real, committed tree at `1151dc4`:** `pio test -e native` **172/172** over 17 suites, run three separate times (21.6 s, 31.6 s, 32.6 s) with no variance; `-e native_nodevtools` **172/172**; `-e native_loop_v131` **82/82** over 2 suites (no CI workflow invokes this env); `pytest tests/ -q` **355 passed, 0 failed** (348 canonical baseline + plan 06's 7 new legs, clearing both this plan's own stated ≥314 floor and the original ≥313 phase-gate floor); `pio run` all three targets **24234/24282/26378** flash, **1567/1573/2008** RAM, matching `-426`/`0` against the before-figures exactly, Leonardo Caterina headroom **2294 B** (up from 1868 B); `check_size_baseline.py --policy merge05 --rebuild` **PASS**, one-sidedness quoted directly from `:697`/`:709` (both strict growth-only comparisons), baseline byte-unchanged; the canonical `--baseline size_baseline_base01.json` form reproduced the **pre-existing** `native: cases baseline=141 observed=172` failure verbatim, attributed to Phase 158 / LAND-03, not this phase; `check_build_warnings.py --rebuild` **PASS**, zero macro-redefinition on all three AVR targets, no new warning on any of the seven edited source files.
- **Re-proved DEDUP-03's four planted transpositions against the SHIPPED code**, not the pre-refactor code plan 02 wrote them against. In a single throwaway worktree (`/tmp/probe156g/firestarter`, `git worktree add ... 1151dc4`), each substitution planted, run, reverted with `git checkout --`, before the next:
  - **Probe A** (over-voltage severity ternary, `eprom.cpp`): RED in `native_loop_v131` (3 failed, including `test_vpp02_e1_...`), BLIND in `native` (172/172 unchanged) -- unchanged from research, attributed to coverage ceiling 2, not a regression.
  - **Probe B** (under-voltage pairing, `eprom.cpp` + `flash_intel.cpp`): **RED** in `native_loop_v131` (2 failed -- `test_vpp04_e_...` and `test_vpp04_f_...`, both "Expected 2 Was 0"), unaffected in `native`. Research measured this **BLIND EVERYWHERE** pre-plan-02 -- **this is blind spot 1's closure, re-proven against the shipped code**, where the mutation point now lives inside the shared `mem_util_report_voltage` helper and reaches both call sites from one edit.
  - **Probe C** (chip-ID `response_code`, `memory.cpp`): RED in `native` (`174 test cases: 2 failed, 170 succeeded` -- `test_migrated_mismatching_chip_id_errors` and `test_case7_...`), matching research. The mutation point has moved from four separate blocks into one shared helper, now reaching all four former call sites from a single edit.
  - **Probe D** (chip-ID message id, `memory.cpp`): **RED** in `native` (`173 test cases: 1 failed, 171 succeeded` -- `test_case7_mismatching_chip_id_with_force_warns`, the WARN-direction id assertion). Research measured this **BLIND EVERYWHERE** pre-plan-02 -- **this is blind spot 2's closure, in CI, re-proven against the shipped code**.
  - **GREEN control**, the real unedited tree at `1151dc4`, re-confirmed after each revert and after the worktree's removal and pruning: `native` 172/172, `native_loop_v131` 82/82.
- **Confirmed the `__udivmodhi4` and per-symbol ledgers.** `31 -> 13` (measured this session via `avr-objdump`), the "24 of them" derived claim restated and unaffected; `__udivmodsi4` holds at the pre-existing, unrelated 12 sites. Per-symbol sum: **-624 B** against the measured **-426 B** image delta -- does NOT close, LTO redistribution into `main` named as the cause; DEDUP-01's own symbol sum (-268) closes exactly against its own -268 B image delta, while the entire -198 B non-closure is attributable to DEDUP-02's half (-356 symbol sum vs. -158 B image delta).
- **Confirmed C-3: the -268/-158 split is CONFIRMED, not merely inherited.** Plan 03's own measured -268 B and plan 04's own measured -158 B sum exactly to the phase's -426 B total and match the ROADMAP's carried split precisely -- stated as an independently re-measured confirmation, with both values cited, not as presenting the inherited ROADMAP figure as measured on its own.
- **Wrote `.planning/v1.33/156-after-figures.md`** (10 sections: git anchors, phase ledger, DEDUP-04 size-identity, mechanical criteria, gate ledger, DEDUP-03 evidence, DEDUP-02 six-divergence table, seven coverage ceilings in final form, corrections index, handoffs). Every figure carries its verbatim command. Ceiling 2 stated in its final, narrowed form (the `flash_intel.cpp` under-voltage arm now has one executing case in `native_loop_v131`, still not CI-visible). Ceiling 7 carries plan 05's own three `.hex` SHA pairs, not research's. All forbidden phrasings avoided and verified absent by grep (`byte-for-byte identical image`: 0 occurrences; `the payload bytes were compared`: 0 occurrences; no "tested"/"verified on hardware"/"bench-verified" applied to the nine wrapper call sites).
- **Closed all four DEDUP requirements in `REQUIREMENTS.md` §3**, each ticked with its discharging plan and the after-figures artifact cited, plus the C-1/C-2/C-3/C-4/C-5/C-6 corrections and the ceiling-4/divergence-1 no-oracle statements appended in place. Traceability table's four `Pending` rows replaced with `Complete (plan, closed 156-07)` forms. Appended the **C-7 correction** to DEAD-06's own §2 entry: its claim to be "the only requirement in Phases 155-158 that touches a test file" is now stated as FALSE, since DEDUP-04 touches `test_eeprom28c_sdp.cpp`. `git diff` on `REQUIREMENTS.md` confined to exactly these lines (18 changed lines total: the DEAD-06 append, the 4 DEDUP entries, the 4 traceability rows).
- **Marked ROADMAP.md's Phase 156 entry PHASE CLOSED**, ticked the 156-07 plan checkbox, changed `**Plans**: 7 plans` to `**Plans:** 7/7 plans complete`, and added a closing paragraph naming the eight-leg gate, the two blind-to-red flips, and the confirmed split. A pre-edit vs. post-edit diff of the whole file confirmed no other phase's `**Plans:**` line, plan list, or Coverage row moved -- the diff is confined entirely to Phase 156's own section (two hunks: the Plans line, and the 156-07 checkbox plus the new closing paragraph). No `v1.33 Coverage` section exists in ROADMAP.md to sync (checked; none found), so that sub-step of the task action was a no-op by measurement, not an omission.
- **Advanced `STATE.md`.** Frontmatter: `current_phase` 156 -> 157, `current_phase_name` -> "Command-Decode Table & Type Narrowing", `status` -> `completed`, `completed_phases` 2 -> 3, `completed_plans` 24 -> 25, `percent` 33 -> 50. Body: `Current Position` updated to Phase 157 / "Not started", its `Stopped at:` line rewritten as a single unbroken line summarising this plan's full landing (measured -426 B, both DEDUP-03 flips, DEDUP-04 size-identity, Case 25's de-vacuuming, the new source-contract gate, and the three phase handoffs). The `## Session` block's own `Stopped at:` narrative -- stale at Phase 154 since before plan 01 and left untouched by all six prior 156-0X plans -- was updated for the first time this phase, per this plan's own explicit instruction that the scraper reads the body, not the frontmatter; the frontmatter's `stopped_at` field itself was deliberately left untouched, matching the established convention this milestone has followed since Phase 154 closed. A new Performance Metrics row (`Phase 156 P07`) appended.
- **Committed once**, staging exactly the four intended `.planning/` paths (`156-after-figures.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`) -- never `git add -A`. `git show --stat --name-only --format= HEAD` confirms exactly 4 paths, all under `.planning/`. Neither the `firestarter` nor `firestarter_app` gitlink was staged; `firestarter` remains at `1151dc4` and `git -C firestarter status --porcelain` is empty after the commit -- this plan moved the firmware repo not at all.

## Task Commits

1. **Task 1 (measure, no commit) + Task 2 (write the after-figures record, no commit) + Task 3 (hand-edit REQUIREMENTS/ROADMAP/STATE, then commit all four files together)** -- meta commit `0d70af9d`: `docs(156-07): close out Phase 156 -- the measured ledger, the gate results and the corrections`.

## Files Created/Modified

- `.planning/v1.33/156-after-figures.md` -- new, the phase's authoritative outcome record
- `.planning/REQUIREMENTS.md` -- all four DEDUP entries ticked with discharge evidence; traceability table rows updated; DEAD-06's C-7 correction appended
- `.planning/ROADMAP.md` -- Phase 156 marked PHASE CLOSED, plan count and 156-07 checkbox updated
- `.planning/STATE.md` -- frontmatter and body advanced to Phase 157 (unplanned)

## Decisions Made

- Stated C-3 as **CONFIRMED**, not superseded -- the two independent per-commit measurements (plan 03's -268 B, plan 04's -158 B) land exactly on the ROADMAP's carried split, so the honest framing is confirmation of a value that had been UNVERIFIED, with both figures cited as independently measured, not as accepting the inherited number on faith.
- Re-planted all four DEDUP-03 probes against the post-refactor tree rather than citing plan 02's pre-refactor RED/GREEN evidence as sufficient on its own -- two of the four mutation points (B and D) now live inside shared helpers, so a claim about the shipped code requires observing the same substitution flip BLIND to RED at its new location.
- Left `STATE.md`'s frontmatter `stopped_at` field untouched, matching the established convention every prior 156-0X plan followed (none of them updated it either, since Phase 154 closed) -- only updated the body's `Current Position` and, for the first time this phase, the `## Session` block's own `Stopped at:` line, per this plan's explicit instruction that the scraper reads the body.
- Collapsed the `## Session` Stopped-at narrative to a single unbroken line before committing (an initial word-wrapped draft was corrected), matching the file's own established single-line convention for every other Stopped-at entry.

## Deviations from Plan

None -- plan executed exactly as written. The one sub-step given as conditional ("sync the ROADMAP v1.33 Coverage rows... if that section carries per-requirement status") was checked and found not to apply: no `v1.33 Coverage` section exists in `ROADMAP.md`, so nothing was synced, which is the plan's own stated fallback, not a deviation.

## Issues Encountered

None.

## User Setup Required

None -- no external service configuration required. This plan measures the committed firmware tree and writes only into `.planning/`.

## Next Phase Readiness

- Phase 156 is fully closed: all four DEDUP requirements complete in `REQUIREMENTS.md`, ROADMAP.md's Phase 156 entry marked PHASE CLOSED, `.planning/v1.33/156-after-figures.md` is the authoritative record Phases 157-159 will read.
- `firestarter` is at `1151dc4` on `gsd/v1.33-source-hygiene-firmware-size-reduction`, tree clean, untouched by this plan. `git -C firestarter worktree list` shows only the primary tree and the untouched `firestarter_py32_ci` sibling.
- Handoffs named with owning phase and requirement ids: Phase 157 / DECODE-05 owns `json_parser.c`'s missing `algorithm` range check; Phase 158 / LAND-01 and LAND-03 own the `size_baseline.json` cold re-anchor and the pre-existing BASE-01 case-count mismatch (both confirmed byte-unchanged / reproduced-as-is this session); Phase 159 / REMAP-01 through REMAP-05, close-blocked by REMAP-04, owns the citation staleness this phase's `#include` additions and new functions created. `.planning/v1.33/CITATIONS-STALE.md` was not touched.
- Nothing pushed. `STATE.md`'s Current Position now points at Phase 157, unplanned -- `/gsd-plan-phase 157` is the next actionable step.

---
*Phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw*
*Completed: 2026-08-23*

## Self-Check: PASSED

- `.planning/v1.33/156-after-figures.md` exists on disk -- FOUND
- `.planning/phases/156-duplicated-report-extraction-boolean-convention-repair-firmw/156-07-SUMMARY.md` exists on disk -- FOUND
- meta repo commit `0d70af9d` (docs(156-07): close out Phase 156 -- the measured ledger, the gate results and the corrections) exists in `git log --oneline --all` -- FOUND
- `firestarter` HEAD `1151dc4` unchanged from `FW_POST_SHA`, `git -C firestarter status --porcelain` empty -- FOUND
- `git -C firestarter worktree list` shows exactly two entries (`/workspaces/firestarter`, `/workspaces/firestarter_py32_ci`) -- FOUND, matches pre-plan state

No missing items.
