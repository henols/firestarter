---
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "01"
subsystem: firmware-measurement
tags: [avr-nm, avr-objdump, pio, platformio, size-baseline, protocol_branch_inventory, git-worktree]

requires: []
provides:
  - .planning/v1.33/156-before-figures.md -- the authoritative before-half measurement record for Phase 156
affects: [156-02, 156-03, 156-04, 156-05, 156-06, 156-07]

tech-stack:
  added: []
  patterns:
    - "Before-figures record convention (established Phase 155, followed here): frontmatter status/supersedes fields naming exactly what stale ROADMAP/REQUIREMENTS prose is corrected, every figure carrying its verbatim producing command"

key-files:
  created:
    - .planning/v1.33/156-before-figures.md
  modified: []

key-decisions:
  - "Recorded the pytest tests/ baseline as measured in the canonical /workspaces/firestarter checkout (348 passed/0 failed/0 skipped) rather than silently substituting research's isolated-worktree figure (313/0/32), and explained + reproduced the divergence via tests/meta_presence.py's META_PRESENT seam, since Task 1's own action text instructs running everything from /workspaces/firestarter"
  - "Recorded the constprop.42 clone's measured byte size (214 B / 0xd6) as distinct from 156-RESEARCH.md's own C-5 figure (216 B / 0xd8) rather than quoting the unverified research figure, per the plan's own 'measure, never assume' ethos"
  - "Measured A1's inferred cause for the 31st __udivmodhi4 call site directly (built uno at e26e9ab and at 46dd574 in throwaway worktrees) rather than leaving it merely unclaimed -- the count is 31 at both, so A1's inference is measured FALSE at that specific commit"

requirements-completed: []

coverage:
  - id: D1
    description: "Every pre-change figure Phase 156's four requirements are measured against is captured in one committed file, on a tree proven unchanged, before any source edit"
    requirement: "DEDUP-01"
    verification:
      - kind: other
        ref: ".planning/v1.33/156-before-figures.md committed at 97703379; git -C firestarter status --porcelain empty before and after (see §1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The record carries the seven ROADMAP/REQUIREMENTS corrections plus the planner-found eighth, each with its measured replacement value"
    requirement: "DEDUP-01"
    verification:
      - kind: other
        ref: ".planning/v1.33/156-before-figures.md §10 corrections index (C-1..C-7 + planner-found eighth)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The reference carrier is named correctly (a6b46f8, not size-reduction-survey) with sha and measured applicability"
    requirement: "DEDUP-04"
    verification:
      - kind: other
        ref: ".planning/v1.33/156-before-figures.md §7; git merge-base independently re-verified this session"
        status: pass
    human_judgment: false
  - id: D4
    description: "The eprom.cpp blob SHA proving the golden gate is GREEN on arrival is recorded"
    requirement: "DEDUP-01"
    verification:
      - kind: other
        ref: ".planning/v1.33/156-before-figures.md §6 -- git hash-object src/proms/eprom.cpp == recorded blob_shas"
        status: pass
    human_judgment: false
  - id: D5
    description: "The __udivmodhi4 count of 31 (not the stale ROADMAP figure of 30) is recorded as DEDUP-01's mechanical denominator"
    requirement: "DEDUP-01"
    verification:
      - kind: other
        ref: ".planning/v1.33/156-before-figures.md §4 -- avr-objdump count == 31, cross-checked at two adjacent commits"
        status: pass
    human_judgment: false
  - id: D6
    description: "The three flash/RAM pairs are recorded as DEDUP-04's only size-identity before side"
    requirement: "DEDUP-04"
    verification:
      - kind: other
        ref: ".planning/v1.33/156-before-figures.md §2 -- pio run -e uno/uno328pb/leonardo, all three match exactly"
        status: pass
    human_judgment: false

duration: ~15min
completed: 2026-08-23
status: complete
---

# Phase 156 Plan 01: Before-Figures Capture Summary

**Independently re-measured every irrecoverable pre-change figure for Phase 156 (three AVR flash/RAM pairs, the per-symbol ledger, 31 `__udivmodhi4` call sites, the golden's GREEN-on-arrival blob SHA, and the reference-carrier's `-C1` applicability), on a tree proven unchanged, and committed the result — finding two additional measured discrepancies beyond the seven ROADMAP corrections along the way.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-23
- **Tasks:** 2 (Task 1 measurement-only, no commit; Task 2 wrote and committed the record)
- **Files modified:** 1 (`.planning/v1.33/156-before-figures.md`, new)

## Accomplishments

- Confirmed the `firestarter` tree clean and at `adf1a31` before and after every measurement step; no source file was edited.
- Reproduced all three AVR flash/RAM figures exactly (`uno` 24660/1567, `uno328pb` 24708/1573, `leonardo` 26804/2008) and the Leonardo Caterina headroom (1868 B).
- Measured the per-symbol ledger on `uno` via `avr-nm`, confirming C-1 directly (`flash_intel_check_vpp` absent from the symbol table — `grep` exits 1) and C-5 (exactly one `constprop` clone, suffix `.42` not `.44`).
- Measured `__udivmodhi4` call sites at **31** (not the ROADMAP's stale 30 — C-2), then went further than the plan required as "acceptable but optional": built `uno` at both `e26e9ab` and `46dd574` in throwaway worktrees and found the count is 31 at both — a **measured negative result** on research assumption A1's inferred cause, rather than merely leaving the cause unclaimed.
- Confirmed the golden (`tests/golden/protocol_branch_inventory.json`) is GREEN on arrival: live `git hash-object` matches the recorded blob SHA, and an independent live re-extraction using the golden module's own `_extract_predicates` yields the identical 23 sites, each line and predicate recorded.
- Independently re-verified the reference-carrier claims: `size-reduction-survey` carries an empty diff on the three relevant files; `wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8` does carry the work; both fork `8695ee5` (re-derived via `git merge-base`, not merely quoted); the rebuilt six-file subset patch fails `--check` on exactly `eeprom_28c.cpp:292` and applies cleanly with `-C1` — neither `--check` invocation mutated the tree.
- Found and recorded two measured discrepancies beyond the seven ROADMAP corrections: the `constprop.42` clone's byte size (214 B / `0xd6` measured, vs. 216 B / `0xd8` `156-RESEARCH.md`'s own C-5 states), and the pytest `tests/` baseline's dependency on meta-repo presence (348 passed/0 failed/0 skipped in the canonical `/workspaces/firestarter` checkout vs. the 313/0/32 `156-RESEARCH.md`/`156-VALIDATION.md` quote from an isolated worktree) — both explained with root cause, not just flagged.
- Wrote and committed `.planning/v1.33/156-before-figures.md`, superseding ROADMAP §Phase 156 criteria 1/4 and REQUIREMENTS DEDUP-01/DEDUP-04 prose per its frontmatter `supersedes` field.

## Task Commits

1. **Task 1: Assert the tree is unchanged, then measure every irrecoverable pre-change figure** — no commit (measurement only; no tracked file was edited, per the task's own contract)
2. **Task 2: Write and commit the before-figures record** — `9770337` (docs)

**Plan metadata:** (this SUMMARY's own commit, made immediately after this file)

## Files Created/Modified

- `.planning/v1.33/156-before-figures.md` — the authoritative before-half measurement record for Phase 156: git anchors, three AVR flash/RAM pairs, the per-symbol ledger, `__udivmodhi4` call-site count, test/gate baselines, the golden's arrival state, reference-carrier applicability, the one-sided size gate note, the seven coverage ceilings, and a ten-row corrections index (C-1 through C-7, the planner-found eighth comment location, and two further measured discrepancies found this session)

## Decisions Made

- Ran the pytest `tests/` baseline in the canonical `/workspaces/firestarter` checkout (not an isolated throwaway worktree), per Task 1's own instruction to "run everything in `/workspaces/firestarter` unless a step says otherwise" — this produced a different (and, for this canonical position, more correct) result than `156-RESEARCH.md`'s isolated-worktree figure, which is recorded as an explained divergence rather than silently overwritten or silently deferred to.
- Measured A1's inferred cause for the 31st `__udivmodhi4` site directly, rather than choosing the plan's other acceptable option (record with no cause claimed) — since the measurement was cheap (two throwaway `pio run` builds) and yields a strictly more informative, still-honest result (a measured negative, not an absence of information).
- Recorded the `constprop.42` clone's actual measured byte size (214 B) rather than quoting `156-RESEARCH.md`'s stated 216 B, since the two toolchain commands (`avr-nm` and `avr-objdump -t`) agree with each other and disagree with the research figure — the suffix identity (`.42`, not `.44`) is what C-5 is actually about, and that part is unaffected.

## Deviations from Plan

None from the plan's own instructions — Task 1 and Task 2 were executed exactly as specified, including the optional-but-encouraged deeper measurement of A1's cause and the honest recording of two additional discrepancies found along the way. These are not Rule 1/2/3 auto-fixes (nothing was broken or missing that needed fixing) — they are measurements the plan's own philosophy ("measure, don't assume; correct stale figures rather than repeat them") calls for, made explicit here as they were made in the file itself. No architectural decision (Rule 4) was required.

## Issues Encountered

None. All eight `<verify><automated>` legs from Task 1 passed on first run; the Task 2 automated verify (grep-based literal checks against the written file, commit-count and porcelain assertions) passed on first run.

## User Setup Required

None — no external service configuration required. This plan performs measurement and documentation only.

## Next Phase Readiness

- `.planning/v1.33/156-before-figures.md` is committed and ready for plans 03, 04, 05, 06 and 07 to cite as the authoritative before-position.
- The golden's GREEN-on-arrival state (blob SHA `838aca47986103969be4caca3cef71a033bac069`) is now on record, so plans 03/04's expected RED legs against it are unambiguously attributable to their own edits.
- The reference carrier (`wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8`, applicable via `git apply -C1`) is confirmed usable as a semantic reference for plans 03/04/05.
- No DEDUP-0X requirement was marked Complete in `.planning/REQUIREMENTS.md` — all four remain `Pending`, correctly, since plan 07 is the landing plan that closes them. This plan's contribution toward each: DEDUP-01 (the corrected 31-site denominator and the `eprom_check_vpp`/`flash_intel_write_init`/helper before-sizes), DEDUP-02 (the before-state four chip-ID block sizes implicit in the per-symbol ledger, ready for plan 04's divergence enumeration), DEDUP-03 (no direct contribution — plan 02's blind-spot closure is unaffected by this measurement-only plan), DEDUP-04 (the three before flash/RAM pairs that are the flip's only before-side, and the reference-carrier proof that DEDUP-04 exists in neither carrier).
- No firmware file was touched; `firestarter` remains at `adf1a31` on `gsd/v1.33-source-hygiene-firmware-size-reduction`, ready for plan 02 (wave 2) to begin.

---
*Phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw*
*Completed: 2026-08-23*

## Self-Check: PASSED

- `.planning/v1.33/156-before-figures.md` exists on disk — FOUND
- Commit `9770337` (docs(156-01): capture the pre-change before-figures and the seven ROADMAP corrections) exists in `git log --oneline --all` — FOUND

No missing items.
