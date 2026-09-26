---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 07
subsystem: docs
tags: [honesty-ledger, planning-record, gate-hardening, project-md]

requires:
  - phase: 130-close-honesty-ledger-claim-gate-release-decision
    provides: "check_record_corrections.py (plan 130-02) — the label-aware checker this plan's edits are measured against"
provides:
  - "PROJECT.md carries all six research corrections named in scope (R-2, R-11, R-15, R-10, A-5, retired py32 slots) as a labeled ⚠ CORRECTION block"
  - "PROJECT.md is green under check_record_corrections.py when scanned alone (0 unlabeled hits, down from 5)"
  - "The two historically-correct 2992 B statements (v1.22 archive + decision register) are preserved byte-unchanged apart from a stated-reason recordscan:history marker"
  - "The PROJECT.md:836 start-here-next footer is disarmed additively, without deleting the dated record"
affects: [130-16]

tech-stack:
  added: []
  patterns:
    - "Labeled ⚠ CORRECTION block for the v1.23-close research corrections, matching the v1.22 eight-block register shape (D-05)"
    - "recordscan:history / recordscan:allow inline markers with stated reasons, per plan 130-02's exemption grammar"

key-files:
  modified:
    - .planning/PROJECT.md

key-decisions:
  - "PROJECT.md:59's stale DATA_BUFFER_SIZE figure was corrected in prose (not exempted), per the plan's explicit prohibition against adding a marker there — it is a false current fact, not a preserved historical one"
  - "PROJECT.md:774's portability-macros/capability-macros collocation got a recordscan:allow marker naming it coincidental, mirroring the wording pattern plan 130-04 used for the analogous ROADMAP.md:28 case, per the critical_context instruction"
  - "Two needle hits (PROJECT.md:45 porting-md-dual-slot, PROJECT.md:97 part-with-no-vtor) were in the plan's own reconciliation-table scope for 130-07 but were not named in either task's <action> text. Both were addressed anyway (Rule 2/3: the plan's own stated verification -- a full-file checker PASS -- could not otherwise be satisfied), each with the marker mechanism the reconciliation table assigned (LABEL-HISTORY for :45, LABEL-ALLOW for :97)"

requirements-completed: []

coverage:
  - id: T1
    description: "PROJECT.md:59 corrected in prose (512, not 1024); a new labeled ⚠ CORRECTION block records R-2/R-11/R-15/R-10/A-5/retired-slots"
    verification:
      - kind: manual
        ref: "grep -c 'DATA_BUFFER_SIZE = 1024' .planning/PROJECT.md -- 0"
        status: pass
      - kind: manual
        ref: "check_record_corrections.py --explain restricted to PROJECT.md -- new block's needles all verdict 'block'"
        status: pass
    human_judgment: false
  - id: T2
    description: "PROJECT.md:836 footer disarmed additively; :32/:172 (orig :163) history-marked; check_record_corrections.py exits 0 for PROJECT.md alone"
    verification:
      - kind: manual
        ref: "FIRESTARTER_RECORDSCAN_TARGETS=.../PROJECT.md python3 check_record_corrections.py -- PASS, exit 0"
        status: pass
      - kind: manual
        ref: "marker-strip demonstration on a /tmp copy of PROJECT.md -- non-zero exit, label named, copy discarded"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-02
status: complete
---

# Phase 130 Plan 07: PROJECT.md Honesty-Ledger Corrections Summary

**Corrected PROJECT.md's one false current fact (stale py32 buffer size), disarmed its highest-risk stale footer (the v1.29 next-milestone pointer carrying a superseded SHA) without deleting the dated record, added a six-item labeled `⚠ CORRECTION` block for the v1.23 close, and marked the historically-correct `2992 B` statements as preserved history — `check_record_corrections.py` goes from 5 unlabeled hits to 0 when scanned against PROJECT.md alone.**

## Performance

- **Duration:** 55 min
- **Tasks:** 2
- **Files modified:** 1 (`.planning/PROJECT.md`)

## Checker Delta (the load-bearing metric)

Scanning `PROJECT.md` alone with plan 130-02's checker:

| | Before this plan | After this plan |
|---|---|---|
| Total needle hits | 11 | 15 (+4: the new block's own needle mentions, all exempt) |
| `unlabeled` | **5** (`:836`, `:32`, `:45`, `:774`, `:97`) | **0** |
| `block` | 6 | 9 |
| `line-label` | 0 | 1 (the footer's new `⚠ SUPERSEDED` note) |
| `inline-history` | 0 | 3 (`:32`, `:172`/orig `:163`, `:45`) |
| `inline-allow` | 0 | 2 (`:783`/orig `:774`, `:97`) |

`FIRESTARTER_RECORDSCAN_TARGETS=/workspaces/.planning/PROJECT.md python3 check_record_corrections.py` now exits **0** with `PASS: scanned .planning/PROJECT.md; exempt hits by verdict: {'block': 9, 'line-label': 1, 'inline-history': 3, 'inline-allow': 2}`. The project-wide default-mode run (all five files) is still RED — `STATE.md`, `ROADMAP.md`, `REQUIREMENTS.md` and the notes file remain plans 130-06/130-08/130-09/130-10's open scope, unaffected by this plan.

## Accomplishments

**Task 1 — corrected `:59`, added the labeled correction block.**
- `PROJECT.md:59`'s `DATA_BUFFER_SIZE = 1024` claim (a false current fact sitting inside the unrelated `⚠` block opened at `:55` about the stale ROADMAP prior-art paragraph) is now corrected in prose to `512`, citing R-2 and `REQUIREMENTS.md` §"Out of Scope"'s row explaining why the value is deliberately not bumped to Leonardo's 1024. The literal string `DATA_BUFFER_SIZE = 1024` no longer appears anywhere in the file (`grep -c` returns 0).
- A new `**⚠ CORRECTION (2026-08-02) — Phase 130 close**` block was appended to the end of the "Phase progress" list, inside the `## Current Milestone: v1.23` region, carrying six numbered items: R-2 (buffer size), R-11 (branch head SHA), R-15 (both CI-trigger/toolchain halves), R-10 (no substantive correction needed, arithmetic cited), A-5 (discharged at Phase 124, with citations), and the two retired py32 ROADMAP slots. Every needle mention inside this new block (`1024`, `311eacf`, `2992`, `arm-none-eabi-gcc`+`absent`) resolves to verdict `block`, confirmed by `--explain`, proving the block model recognises it rather than merely looking labeled to a human.

**Task 2 — disarmed the `:836` footer, marked the historically-correct statements.**
- The `:836` footer (now `:845` after Task 1's insertions) keeps its full 2026-07-30 v1.22-close text unchanged and gains an appended `**⚠ SUPERSEDED (2026-08-02 — Phase 130 close):**` note: the next-milestone claim is superseded (v1.23 became PY32F071 Integration, both py32 slots retired by CLOSE-03), `311eacf` is superseded by `4ee64a1` (R-11), the release-asset-naming blocker is closed (REL-01/REL-02, cited), and the actual next milestone is the `v1.30` ROADMAP entry. The dated footer itself is preserved verbatim; nothing was deleted.
- `PROJECT.md:32` (v1.22 archive line) and `:172` (orig `:163`, v1.22 decision-register line) each gained an inline `recordscan:history` marker with a stated reason (2992 B was the pre-Phase-119 headroom, 28672 − 25680, exactly what Phase 119's own +392 B was judged against). Both lines are byte-unchanged apart from the appended comment — confirmed by `git diff` showing only the marker text added.
- `PROJECT.md:783` (orig `:774`, the v1.23-STARTED footer) gained an inline `recordscan:allow` marker naming the `agent/portability-macros`/"capability macros" collocation coincidental — the branch name and the unrelated VPP capability-macro seam mention land in one long paragraph by chance; R-1's actual finding (no pin-map work, zero timing consumers) is neither asserted nor contradicted there.
- Two needles the plan's task text did not explicitly name but which the reconciliation table assigned to this plan (`:45` porting-md-dual-slot, `:97` part-with-no-vtor) were also resolved during Task 1 — see Deviations below.
- The suppression-is-real proof: `exempt_regions()`'s marker on line 32 was stripped on a `/tmp` copy, the checker was re-run against that copy, observed `FAIL: 1 leonardo-headroom-2992` at the stripped line with exit 1, and the copy was discarded.

## Task Commits

1. **Task 1: Correct `:59` + add the labeled `⚠ CORRECTION` block** — `a44dd62` (docs)
2. **Task 2: Disarm the `:836` footer + mark history-exempt statements** — `f701dd7` (docs)

## Files Created/Modified

- `.planning/PROJECT.md` — the only file touched by this plan (confirmed: `git diff --stat` across both commits shows exactly one file changed, 16 insertions / 7 deletions)

## Decisions Made

- **`:59` corrected in prose, never exempted.** Per the plan's explicit prohibition — it is a false current fact, not a preserved historical one, and label-awareness would otherwise skip it silently (it sits inside the block opened at `:55` about a different subject, the stale ROADMAP prior-art paragraph).
- **`:774`/`:783`'s collocation marked `recordscan:allow`, not corrected.** The `agent/portability-macros`/"capability macros" co-occurrence is coincidental — neither token asserts or contradicts R-1's actual finding — mirroring the wording pattern plan 130-04 used for the analogous `ROADMAP.md:28` case, per the critical_context instruction to mirror it for consistency.
- **`:45` and `:97` addressed even though absent from either task's `<action>` text.** The plan's own reconciliation table (from `130-02-SUMMARY.md`) assigned both to plan 130-07's scope, and Task 2's stated verification (`check_record_corrections.py` exits 0 for `PROJECT.md` alone) could not otherwise pass — these two needle hits are genuinely unlabeled hits inside `PROJECT.md`, independent of the tasks' narrower prose. Resolved each per the disposition the reconciliation table assigned: `:45` (porting-md-dual-slot) got `recordscan:history` (accurate at kickoff, superseded by Phase 126's actual shipped design); `:97` (part-with-no-vtor) got `recordscan:allow` (the line names the "no VTOR" correction as an open item for other plans to close, it does not itself assert the false claim). Documented here as a Rule 2/3 auto-fix — the plan's own acceptance criteria could not be met otherwise, and neither needle was weakened to reach green.

## Deviations from Plan

**1. [Rule 2/3 — missing scope in plan's `<action>` text] Addressed two additional unlabeled needle hits inside `PROJECT.md` that the plan's reconciliation table assigned to this plan but that neither task's `<action>` text named.**
- **Found during:** Task 1 (discovered while confirming Task 2's stated verification would pass against the full file)
- **Issue:** `130-02-SUMMARY.md`'s reconciliation table assigns five `PROJECT.md` rows to plan 130-07 (`:836`, `:32`, `:45`, `:774`, `:97`), but the plan's own task `<action>` text only discusses `:59`/`:836`/`:32`/`:163`/`:774` explicitly — `:45` and `:97` are absent from both tasks' prose, even though Task 2's acceptance criterion ("the checker exits 0 restricted to this file") requires them resolved.
- **Fix:** Added a `recordscan:history` marker to `:45` (PORTING.md/dual-slot claim, superseded by Phase 126's shipped design) and a `recordscan:allow` marker to `:97` (self-referential "no VTOR" correction pointer), each using the marker mechanism the reconciliation table itself assigned.
- **Files modified:** `.planning/PROJECT.md`
- **Commit:** `a44dd62`

No other deviations. No architectural changes, no auth gates, no package installs.

## PROJECT.md:59 vs PROJECT.md:774 — the two upstream-flagged dispositions

Per the plan's `<upstream_results>` instructions, both findings were resolved deliberately:

- **`PROJECT.md:59`** was a genuinely stale current fact (`DATA_BUFFER_SIZE = 1024`) hidden inside an unrelated `⚠` block's region-wide exemption. It was corrected in prose to `512`, cross-referencing the already-correct figure at `:75`/item-7 of the research-corrections block and citing `REQUIREMENTS.md`'s "Out of Scope" row. This closes the exact fail-open gap RESEARCH C-7's note about `PROJECT.md:59` was warning about — the checker's block exemption is region-wide, not needle-specific, so leaving this uncorrected would have silently carried a wrong number into the next milestone despite a green gate.
- **`PROJECT.md:774`** (now `:783`) was confirmed a coincidental collocation, not a stale claim: `agent/portability-macros` (the branch name) and "capability macros" (the unrelated VPP seam) land in one long footer paragraph purely by chance. A `recordscan:allow` marker names this explicitly rather than rewording the paragraph to hide the collocation or weakening the needle — the needle stays exactly as strict as plan 130-02 defined it.

## Known Stubs

None — this is a documentation-only plan; no code or UI was touched.

## Threat Flags

None. This plan edits only `.planning/PROJECT.md` prose and inline HTML comments; it introduces no new network endpoints, auth paths, file-access patterns, or schema changes at a trust boundary. The threat register in `130-07-PLAN.md` (T-130-28…32, T-130-SC) is fully discharged by the acceptance criteria verified above; no new surface was found beyond what that register already names.

## User Setup Required

None.

## Next Phase Readiness

- `PROJECT.md` is green under `check_record_corrections.py` when scanned alone; plan 130-16 (the only plan permitted to tick CLOSE-01/02/03/04) can rely on this file's contribution to the eventual full-project-green state without further edits here.
- No requirement id was ticked by this plan, per its own frontmatter (`requirements: [CLOSE-01]`, ticked only by plan 130-16) and the orchestrator-held-writes instruction.
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md` were not touched, and no `roadmap update-plan-progress` or state-advancing verb was run, per the orchestrator's explicit restriction for this plan.
- `git -C /workspaces rev-parse --abbrev-ref HEAD` confirmed `gsd/v1.23-py32f071-integration` after both task commits — the known `gsd-tools query commit` branch-switch hazard (plan 130-05) did not recur, because no `gsd-tools query commit` verb was used for the content commits (plain `git commit`, per the sequential-executor instructions for this run).

---
*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Completed: 2026-08-02*

## Self-Check: PASSED

`.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-07-SUMMARY.md` found on disk; both task commit hashes (`a44dd62`, `f701dd7`) found in `git log --oneline --all`.
