---
phase: 157-command-decode-table-handle-type-narrowing-firmware-only
plan: "07"
subsystem: firmware-decode
tags: [json_parser.c, firestarter.h, avr-nm, strings, size-baseline, cold-build, phase-closeout]

# Dependency graph
requires:
  - phase: 157-command-decode-table-handle-type-narrowing-firmware-only
    provides: "all six prior plans' measured figures and probe transcripts (157-01 through 157-06 SUMMARYs), which this plan re-measures at the final committed position and assembles into the phase outcome record"
provides:
  - ".planning/v1.33/157-after-figures.md -- the phase's authoritative outcome record: all eight gate legs run on the final tree, cold-to-cold headline delta (-1144 B flash / -5 B RAM), DECODE-01's symbol ledger and DECODE-02's block dump re-measured at the final position, DECODE-07 discharged by record, all 22 corrections closed out"
  - "ROADMAP.md Phase 157 and REQUIREMENTS.md DECODE-01..07 closed against the after-record, with per-criterion correction sentences replacing stale figures"
  - "Phase 158/159 handoffs: native case-count trajectory 172->177->184, size_baseline.json's stale 172, BASE-01's frozen 141, cold-vs-warm figure status"
affects: ["158-LAND-01", "158-LAND-03", "159-REMAP-01"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Cold-both-sides delta: rebuild the pre-phase position in a throwaway detached worktree (rm -rf .pio/build + one pio run) alongside the post-phase cold rebuild, so a phase's headline size delta is never a warm-before-against-cold-after mixture"

key-files:
  created:
    - .planning/v1.33/157-after-figures.md
  modified:
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Cold-rebuilt the pre-phase position (1151dc4) in a throwaway worktree rather than trusting the before-record's WARM figures -- both turned out byte-identical to WARM at that position, but the comparison is now provably cold-to-cold rather than assumed equivalent"
  - "Re-captured plan 02's two _Static_assert planted-negative diagnostics verbatim in a fresh throwaway probe this session, since neither prior SUMMARY preserved the compiler's exact error text -- the after-record's DECODE-03 evidence quotes real, re-derived output rather than a paraphrase"
  - "Composed cold-to-cold delta (-1144 B / -5 B) matches plan 03's own WARM composed total exactly, confirming the WARM/COLD convention makes no observable difference at this position -- stated as an observation in the handoff section, not generalized into a guarantee for Phase 158"
  - "REQUIREMENTS.md section 4's header line was corrected in place (measured -1144 B, not -1148 B) following the precedent DEAD-03's phase-155 section header already set, even though the plan's action text named only the checkbox/traceability edits explicitly"

patterns-established: []

requirements-completed: [DECODE-01, DECODE-02, DECODE-03, DECODE-04, DECODE-05, DECODE-06, DECODE-07]

coverage:
  - id: D1
    description: "All eight phase-gate legs run on the final committed tree (785e644) with verbatim command and result, including the four that run in no CI workflow"
    verification:
      - kind: integration
        ref: "pio test -e native/-e native_nodevtools => 184/184 each; check_build_warnings.py --rebuild, check_no_heap_or_64bit_symbols.py, check_size_baseline.py (merge05 and default) all run and recorded; firestarter_app pytest tests/ => 1976 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "Headline size delta is cold on both sides: pre-phase position cold-rebuilt in a throwaway detached worktree at 1151dc4, post-phase cold-rebuilt on the committed tree, composed delta -1144 B flash / -5 B RAM per target"
    verification:
      - kind: other
        ref: "rm -rf .pio/build/<env> + pio run -e uno -e uno328pb -e leonardo on both sides this session; uno 24234->23090, uno328pb 24282->23138, leonardo 26378->25234, RAM 1567/1573/2008 -> 1562/1568/2003"
        status: pass
    human_judgment: false
  - id: D3
    description: "DECODE-01's symbol ledger and DECODE-02's offset-resolved block dump re-measured at the final position on all three AVR targets, with no automated gate claimed"
    verification:
      - kind: other
        ref: "avr-nm shows all ten stubs + store_field + five siblings ABSENT; key_parsers 44B->66B; get_flags.constprop.33 82B; strings block dump shows exactly one key-string block per target, all eleven keys at count 1"
        status: pass
    human_judgment: false
  - id: D4
    description: "DECODE-07 discharged by the after-record's own section, no code changed; ROADMAP and REQUIREMENTS DECODE-01..07 closed against it with per-criterion corrections, diff confined to Phase 157 / section 4"
    verification:
      - kind: other
        ref: "grep -cE '^\\| DECODE-0[1-7] \\| Phase 157 \\| Complete' REQUIREMENTS.md => 7; grep -c '^### Phase ' ROADMAP.md unchanged at 100 before/after; git show --stat on both commits lists only the intended paths"
        status: pass
    human_judgment: false
  - id: D5
    description: "firestarter submodule left byte-unchanged by this plan: porcelain empty, HEAD still 785e644, no throwaway worktree or probe branch left behind"
    verification:
      - kind: other
        ref: "git -C firestarter status --porcelain empty; git -C firestarter rev-parse HEAD == 785e644; git -C firestarter worktree list matches pre-plan output (firestarter + firestarter_py32_ci only)"
        status: pass
    human_judgment: false

duration: 100min
completed: 2026-08-23
status: complete
---

# Phase 157 Plan 07: Landing -- All Gate Legs, After-Figures Record, ROADMAP/REQUIREMENTS Closure Summary

**Ran all eight phase-gate legs on the final committed firmware tree (785e644), cold-rebuilt both sides of the phase's headline size delta in a throwaway detached worktree to prove a cold-to-cold -1144 B flash / -5 B RAM measurement, wrote the 16-section `157-after-figures.md` outcome record with all 22 corrections closed out, and flipped all seven DECODE requirements to Complete against it with scoped ROADMAP/REQUIREMENTS edits confined to Phase 157 and section 4.**

## Performance

- **Duration:** ~100 min
- **Tasks:** 3 (run every gate leg cold on both sides; write and commit the after-figures record; close out ROADMAP/REQUIREMENTS)
- **Files modified:** 3 (`.planning/v1.33/157-after-figures.md` created; `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` scoped-edited)

## Accomplishments

- Cold-rebuilt the pre-phase position (`1151dc4`) in a throwaway `git worktree add --detach /tmp/157-cold-probe/firestarter` and measured all three AVR targets: `uno` 24234/1567, `uno328pb` 24282/1573, `leonardo` 26378/2008 -- byte-identical to `157-before-figures.md`'s own WARM figures, confirming (not assuming) the convention makes no difference here. Worktree removed and pruned; `git worktree list` matched its pre-probe output.
- Cold-rebuilt the post-phase position on the committed tree at `785e644`: `uno` 23090/1562, `uno328pb` 23138/1568, `leonardo` 25234/2003 -- zero `warning:` lines, byte-identical to plans 03/04/05's own WARM figures. Composed the delta **cold to cold**: `−1144 B` flash / `−5 B` RAM on all three targets, matching plan 03's own WARM composed total exactly.
- Re-measured DECODE-01's symbol ledger at the final position: all ten deleted stubs, `store_field`, and the five zero-cost siblings confirmed ABSENT; `key_parsers` grew from `44 B` to `66 B` (each row now carries a full `field_desc_t` instead of one function pointer); `get_flags.constprop.33` at `82 B`, suffix unpinned; `jsoneq_`/`simple_strtoul` unchanged. Recorded that the ledger does not close arithmetically against the image delta, and why (LTO redistribution).
- Re-measured DECODE-02's evidence on all three targets: exactly ONE key-string block survives per target (not two), all eleven keys at count one, `flags` no longer mangled to `Uflags` because there is only one copy. Confirmed `get_flags`'s two call sites are in two different functions (`json_parse_config:348`, `json_get_cmd:379`), correcting the "two sites" misreading (C-1).
- Re-captured plan 02's two `_Static_assert` planted-negative diagnostics **verbatim** in a fresh throwaway probe this session (`/tmp/157-07-probe/firestarter`), since neither prior SUMMARY preserved the compiler's exact error text: a struct reorder (`mem_size` moved after `data_buffer`) and a planted twelfth `key_parsers[]` row each produce the assertion's own authored message on `pio run -e uno`. Probe reverted and discarded.
- Ran all eight phase-gate legs on the final tree with their verbatim command, exit status and salient output: cold AVR build (zero warnings), `pio test -e native`/`-e native_nodevtools` (184/184 each, 17 suites), `check_build_warnings.py --rebuild` (PASS), `check_no_heap_or_64bit_symbols.py` (PASS), `check_size_baseline.py --policy merge05` (exits 1, exactly two native case-count lines, no AVR leg fails), `check_size_baseline.py` default mode (exits 1, pre-existing `flash_used`/`ram_used` byte-identity failures Phases 155/156 already caused, plus the native case-count growth), and the host suite (`pytest tests/` => `1976 passed`). Legs 4/5/6/7 marked as running in NO CI workflow.
- Quoted `scripts/check_size_baseline.py:697` and `:709` verbatim, confirming both are strict-inequality growth-only comparisons, and recorded the MERGE-05 pass as ONE-SIDED.
- Re-derived `sizeof(firestarter_handle_t)` on both architectures with the OD-7 method: AVR `596 B` (eleven table members at offsets 3-32, `data_buffer` at 33), native `656 B` unchanged -- both matching plan 03's own figures exactly, confirming no further struct change occurred since.
- Wrote `.planning/v1.33/157-after-figures.md`, sixteen sections, all 22 corrections (C-1 through C-22) closed out with source-said / measured / outcome, all seven OD decisions with their declined alternative's cost, DECODE-07 discharged by its own §9 (no code change), the 999.35 non-additivity warning, and explicit numbered handoffs to Phases 158 and 159. Committed as `ca144570` (`docs(157-07): record the phase outcome, the gate ledger and the twenty-two corrections`).
- Closed out ROADMAP.md §Phase 157 (Measured line and all seven success criteria, each gaining a closure sentence naming its discharging plan, the after-record section, and its correction) and REQUIREMENTS.md §4 (all seven DECODE bullets ticked with discharge sentences and corrections; all seven traceability rows flipped to `Complete`; section header corrected in place, following the DEAD-03 precedent), via scoped `Edit` replacements only. Diff confirmed confined to Phase 157 / section 4 -- `^### Phase ` heading count unchanged at 100, both files' line counts unchanged (4544, 158). Committed as `2a2fda22` (`docs(157-07): close out DECODE-01..07 and supersede the stale ROADMAP figures`).

## Task Commits

1. **Task 1: Run every phase-gate leg on the final tree, cold on both sides** -- no commit (measurement-only task; the cold-before probe worktree and the `_Static_assert` diagnostic-capture probe were both throwaway, fully discarded before this task ended).
2. **Task 2: Write and commit the after-figures record** -- `ca144570` (`docs(157-07): record the phase outcome, the gate ledger and the twenty-two corrections`).
3. **Task 3: Close out the ROADMAP and REQUIREMENTS prose this phase supersedes** -- `2a2fda22` (`docs(157-07): close out DECODE-01..07 and supersede the stale ROADMAP figures`).

## Files Created/Modified

- `.planning/v1.33/157-after-figures.md` -- the phase's authoritative outcome record: git anchors, the phase ledger (cold both sides), DECODE-01 through DECODE-07's evidence sections, the eight-leg gate ledger, the one-sidedness quote, thirteen coverage ceilings, the 22-row corrections ledger, all seven OD decisions, the 999.35 warning, and Phase 158/159 handoffs.
- `.planning/ROADMAP.md` -- Phase 157's `**Measured**` line and all seven success criteria gained closure sentences naming the discharging plan and after-record section; plan 07's checkbox flipped to `[x]`.
- `.planning/REQUIREMENTS.md` -- all seven `DECODE-0N` bullets ticked with discharge sentences and corrections; section 4's header corrected in place; all seven traceability rows flipped from `Pending` to `Complete`.

## Decisions Made

- **Cold-rebuilt the pre-phase position rather than trusting the before-record's WARM figures.** Both turned out byte-identical at `1151dc4`, but the composed delta is now provably cold-to-cold, not assumed equivalent from a different plan's session.
- **Re-captured plan 02's two `_Static_assert` diagnostics verbatim this session**, since the plan-02 SUMMARY described the outcome ("FAIL with the assertion's own message text") without preserving the exact compiler output -- the after-record quotes real, freshly re-derived text.
- **Corrected REQUIREMENTS.md §4's header line in place** (`-1144 B`, not `-1148 B`), following the precedent DEAD-03's phase-155 section header already established (`## 2. Dead-Weight Removal (DEAD) — Phase 155, measured −1366 B flash / −8 B RAM (corrected from −1364 B...`), even though the plan's action text named only the DECODE-0N bullets and traceability rows explicitly. This closes the same stale-figure hazard the plan's own objective names, applied one line higher than literally instructed.
- **Did not restate the ROADMAP's `86-110 B` per-stub range or `3-37`/`38` offset figures anywhere as current** -- every criterion's closure sentence names the correction (`84-110 B`, `3-32`/`33`) explicitly.

## Deviations from Plan

None -- plan executed exactly as written. The REQUIREMENTS.md §4 header correction (above) is an extension of the plan's own stated intent (supersede every stale figure in scope) rather than a deviation from it, applied by the same DEAD-03 precedent the plan's own read_first list points at.

## Issues Encountered

None. All eight gate legs ran clean on the first attempt; both throwaway probe worktrees (`157-cold-probe`, `157-07-probe`) built and were discarded without incident; `git -C firestarter worktree list` matched its pre-plan output after each.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- `firestarter` HEAD remains `785e644` on `gsd/v1.33-source-hygiene-firmware-size-reduction`; `git -C firestarter status --porcelain` is empty; no `.rej`/`.orig` file exists anywhere; no throwaway worktree or probe branch left behind.
- Phase 158 (LAND-01/LAND-02/LAND-03) can proceed directly from `.planning/v1.33/157-after-figures.md` §16's handoffs: the native case-count trajectory `172 -> 177 -> 184` on both `native` and `native_nodevtools` (17 suites unchanged), `scripts/baseline/size_baseline.json`'s stale `172`, `size_baseline_base01.json`'s frozen `141`, and the fact that every headline figure in this record is COLD.
- Phase 159 (REMAP-01..05) can cite this record's own `file:LINE` citations as measured against the current, post-Phase-154 tree, to be remapped once over the composite diff, per the before-record's own D-01/D-05 statement.
- All seven DECODE requirements are `Complete` in `.planning/REQUIREMENTS.md`, each with a named discharging plan and after-record section. Phase 157 is fully closed.
- No blockers.

---
*Phase: 157-command-decode-table-handle-type-narrowing-firmware-only*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: `.planning/v1.33/157-after-figures.md`
- FOUND: `.planning/phases/157-command-decode-table-handle-type-narrowing-firmware-only/157-07-SUMMARY.md`
- FOUND: meta commit `ca144570` (`git log --oneline --all`)
- FOUND: meta commit `2a2fda22` (`git log --oneline --all`)
- FOUND: `firestarter` HEAD unchanged at `785e644`, `git -C firestarter status --porcelain` empty
