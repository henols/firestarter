---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 09
subsystem: testing
tags: [python, regex, gate-hardening, honesty-ledger, ci-tooling, markdown]

requires:
  - phase: 130-close-honesty-ledger-claim-gate-release-decision (plan 02)
    provides: "check_record_corrections.py — the twelve-needle staleness checker, its two exemption mechanisms, and the machine-derived CLOSE-01 worklist (including the load-bearing mechanical finding written specifically for this plan)"
provides:
  - "A third exemption mechanism in check_record_corrections.py — `recordscan:supersedes needle=<label> lines=<n,n,...> reason: <text>` — that retroactively covers specific (needle label, line number) pairs elsewhere in the same file without editing those lines"
  - "notes/py32f071-port-branch-state.md's dated body (lines 1-134) preserved byte-for-byte, with an append-only SUPERSEDED section (lines 135-179) covering all twelve checker-flagged sites plus the closeable-scope paragraph the checker misses due to a line-wrap split"
  - "check_record_corrections.py exits 0 for notes/py32f071-port-branch-state.md alone (0 unlabeled, 12 superseded, 13 block)"
affects: [130-16]

tech-stack:
  added: []
  patterns:
    - "Mechanism 3: a machine-readable inline marker placed anywhere in a file (in practice inside an already-open labeled block) that names a needle label and an explicit line-number list elsewhere in the SAME file as retroactively exempt — narrowly scoped by requiring a real needle label, an enumerated (not ranged) line list, and a mandatory stated reason"

key-files:
  created:
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/fixtures/superseded_section_control.md
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/fixtures/superseded_section_full_control.md
  modified:
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/test_check_record_corrections.py
    - .planning/notes/py32f071-port-branch-state.md

key-decisions:
  - "Resolution 2 chosen (extend the checker with a third exemption mechanism), not Resolution 1 (per-line inline markers on the original body) — see 'The 130-02 Decision Point' below for full reasoning"
  - "The new marker keyword is `supersedes`, distinct from `history`/`allow`, so a grep for the mechanism-2 keywords never accidentally matches it"
  - "The marker requires an explicit, enumerated line-number list (not a range, not 'rest of file') plus a needle label that must exist in `_NEEDLE_LABELS` plus a mandatory non-blank reason — three independent narrow-scoping guards, each proven by its own negative test"
  - "The closeable-scope paragraph (lines 131-134) is documented in the appended section even though the checker does not flag it (a markdown line-wrap splits '27 commits' / 'behind' across two physical lines) — honored because this plan's own truths bullet names it, not because the gate requires it"

requirements-completed: []

coverage:
  - id: D1
    description: "check_record_corrections.py gains a narrowly-scoped third exemption mechanism (recordscan:supersedes) enabling retroactive, byte-unchanged supersession of a dated capture's stale lines"
    verification:
      - kind: unit
        ref: "test_check_record_corrections.py::test_superseded_section_control_fails_on_the_uncovered_line_only"
        status: pass
      - kind: unit
        ref: "test_check_record_corrections.py::test_superseded_section_full_control_exits_zero"
        status: pass
      - kind: unit
        ref: "test_check_record_corrections.py::test_supersedes_marker_suppression_is_real_not_accidental"
        status: pass
      - kind: unit
        ref: "test_check_record_corrections.py::test_supersedes_marker_with_unknown_needle_label_does_not_exempt"
        status: pass
      - kind: unit
        ref: "test_check_record_corrections.py::test_supersedes_marker_with_no_reason_does_not_exempt"
        status: pass
      - kind: unit
        ref: "test_check_record_corrections.py (full module, 20 tests, all pre-existing 15 unaffected)"
        status: pass
    human_judgment: false
  - id: D2
    description: "notes/py32f071-port-branch-state.md's original body (lines 1-134) is byte-unchanged; an append-only SUPERSEDED section covers all twelve checker-flagged sites plus the closeable-scope paragraph; check_record_corrections.py exits 0 for this file"
    verification:
      - kind: unit
        ref: "head -134 notes/py32f071-port-branch-state.md | sha256sum == 39cfc9094fc923f1bda5a98f0b5c6a8a494076bbd7265e5845c8dd4ffbd6c43e (measured before and after the edit)"
        status: pass
      - kind: unit
        ref: "git diff -- .planning/notes/py32f071-port-branch-state.md shows zero removed lines"
        status: pass
      - kind: automated_ui
        ref: "FIRESTARTER_RECORDSCAN_TARGETS=.../notes/py32f071-port-branch-state.md python3 check_record_corrections.py --explain (0 unlabeled, 12 superseded, 13 block)"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-08-02
status: complete
---

# Phase 130 Plan 09: Branch-State Note Supersession Summary

**Extended `check_record_corrections.py` with a third, narrowly-scoped exemption mechanism (`recordscan:supersedes`) so `notes/py32f071-port-branch-state.md`'s dated 2026-07-28 body stays byte-unchanged AND the checker exits 0 for it — resolving the tension 130-02 flagged rather than picking a side.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 2 (plus the decision point both tasks turned on)
- **Files modified:** 3 modified (checker, test module, the note), 2 created (fixtures), plus this SUMMARY

## Accomplishments

- Diagnosed and confirmed, by direct measurement (not by trusting 130-02's cached numbers), that `notes/py32f071-port-branch-state.md` carries exactly 12 `unlabeled` checker hits across 7 needle labels, all on lines 1-134
- Extended `check_record_corrections.py` with exemption mechanism 3 (`recordscan:supersedes`), narrowly scoped by needle-label validity, explicit line enumeration, and a mandatory reason — 10 new tests (2 positive/negative direction, 1 mutation/reachability proof, 2 narrow-scoping negatives, plus supporting assertions), all 15 pre-existing tests unaffected
- Appended a single SUPERSEDED section (45 lines) to the note, covering all 12 checker-flagged sites plus the closeable-scope paragraph (a checker miss due to markdown line-wrap, documented anyway per this plan's truths)
- Verified by hash: `head -134` of the note is byte-identical before and after (`39cfc909...`), `git diff` shows zero removed lines, and `check_record_corrections.py` now exits **0** for this file alone (0 unlabeled, 12 `superseded`, 13 `block`)

## Task Commits

1. **Task 1 (measurement, folded into this SUMMARY — no separate commit; see "Task 1: Measurements" below):** no code changed, verified via `git diff --stat` empty at the time
2. **Checker extension (Resolution 2, the decision this plan had to make):** `3fb6a04` (feat)
3. **Task 2 (append the SUPERSEDED section):** `f33e787` (docs)
4. **This SUMMARY.md:** (commit below)

## Files Created/Modified

- `check_record_corrections.py` — new `_SUPERSEDE_MARKER_RE`, `_collect_superseded_targets()`, `superseded` verdict wired into `_verdict_for_line`/`scan_text`; module docstring gained a "Why a fourth mechanism exists" paragraph
- `test_check_record_corrections.py` — 5 new test functions (10 assertions across positive/negative/mutation/narrow-scoping directions) plus updated module docstring coverage list
- `fixtures/superseded_section_control.md` — plants the needle twice, covers only one occurrence; proves narrow scoping (must FAIL)
- `fixtures/superseded_section_full_control.md` — plants the needle twice, covers both; proves the positive direction (must PASS)
- `.planning/notes/py32f071-port-branch-state.md` — appended SUPERSEDED section (lines 135-179); lines 1-134 byte-unchanged

## Task 1: Measurements (before any edit to the note)

**Full-file SHA-256 (before edit):** `39cfc9094fc923f1bda5a98f0b5c6a8a494076bbd7265e5845c8dd4ffbd6c43e`
**First-134-lines SHA-256 (before edit):** `39cfc9094fc923f1bda5a98f0b5c6a8a494076bbd7265e5845c8dd4ffbd6c43e` (identical to the full-file hash because the file was exactly 134 lines before this plan touched it)
**`wc -l` (before edit):** `134`

**Verbatim `--explain` output for this file alone, before any edit:**

```
/workspaces/.planning/notes/py32f071-port-branch-state.md:53  py32-buffer-1024  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:20  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:21  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:22  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:23  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:24  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:29  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:107  host-head-311eacf  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:61  porting-md-dual-slot  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:96  cli-handlers-821  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:94  hex-extension-hardcoded  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:12  third-stack-2c2ed10  unlabeled
Tally: {'unlabeled': 12}
```

This reproduces 130-02's own capture of this file's slice exactly (12 unlabeled, same 7 labels, same 12 line numbers) — re-measured independently rather than trusted, per this task's own instruction not to act from memory.

### One row per `unlabeled` record (12 rows, matching the tally exactly)

| file:line | needle | superseded claim | corrected value |
|---|---|---|---|
| :12 | third-stack-2c2ed10 | Cites `2c2ed10`/"603 additions across 8 files" as the surviving prior art (quoting the ROADMAP's own since-corrected claim) | The real inventory is five branches; `2c2ed10` (PR #46) is the smallest, not the sole survivor — the live attempt is PR #48 |
| :20 | branches-27-behind | Table row: `agent/py32f071-toolchain` "27 behind" | 0 behind `origin/beta` (Phase 124 merged) |
| :21 | branches-27-behind | Table row: `feature/py32f071-full-support` "27 behind" | Same correction |
| :22 | branches-27-behind | Table row: `feature/py32f071-toolchain` "27 behind" | Same correction |
| :23 | branches-27-behind | Table row: `agent/portability-macros` "27 behind" | Same correction |
| :24 | branches-27-behind | Table row: `feature/common-vpp-calibration` "27 behind" | Same correction |
| :29 | branches-27-behind | Prose: "Every branch is 27 commits behind `beta`" | Same correction |
| :53 | py32-buffer-1024 | `DATA_BUFFER_SIZE = 1024` | 512, deliberately not bumped (v1.10 CAP-01) |
| :61 | porting-md-dual-slot | "the CRC-validated dual-slot flash scheme `PORTING.md` specifies is still unwritten" | `PORTING.md` exists only on two closed PRs; the dual-slot design landed in-milestone (Phase 126) instead |
| :94 | hex-extension-hardcoded | "the extension is baked into the pattern too" | Already fixed on the branch (`asset_candidates()`/`_pick_asset()`) |
| :96 | cli-handlers-821 | `cli_handlers.py:819` | Moved to `cli_handlers.py:930` |
| :107 | host-head-311eacf | `feature/py32f071-fw-install` @ `311eacf`, "queued as milestone v1.29" | Landed at `4ee64a1` as a real merge commit; v1.29 retired into v1.23 |

Row count: **12**, matching the `unlabeled` tally exactly.

### Divergence check against research's/the plan's per-hit list (both directions)

The plan's own `<objective>` names "**Seven** stale sites": (1) the 27-behind figure in the branch table *and* prose (one conceptual site spanning lines 20-24+29), (2) `DATA_BUFFER_SIZE = 1024`, (3) `PORTING.md` dual-slot spec, (4) `cli_handlers.py:819`, (5) hardcoded `.hex` extension, (6) `311eacf` host branch head, (7) the closeable-scope paragraph.

- **Site the checker flagged that the plan's own "seven" count does not separately enumerate:** the opening paragraph's `2c2ed10`/"603 additions" citation (line 12, needle `third-stack-2c2ed10`). This IS named individually in `130-RESEARCH.md` R-14 and IS assigned to this plan by 130-02's reconciliation table (`notes/...:12 | third-stack-2c2ed10 | SUPERSEDED-SECTION | 130-09`) — so it was never actually missed by research, only undercounted by the plan's own summary sentence ("seven" vs. the eight distinct conceptual sites the reconciliation table actually assigns here). Addressed anyway (see the appended section's first table row); recorded here so the "seven" figure in `130-09-PLAN.md`'s objective is not mistaken for a complete count.
- **Site the plan's own truths named that the checker did NOT flag:** the closeable-scope paragraph (lines 131-134, "27 commits behind"). Confirmed by direct inspection: the sentence wraps across two physical markdown lines (`...(27 commits` on line 132, `behind), the host...` on line 133), and the `branches-27-behind` needle's regex requires both tokens on the SAME physical line (per the checker's own documented design choice for long single-line bullets — this file's prose is NOT single-line at this point, which is the gap). This is the same class of miss the project's own memory records elsewhere (wrapped labels breaking a line-scoped gate). Addressed in the appended section anyway, per this plan's own truths bullet, not because the gate requires it — and flagged here as a real, if narrow, checker limitation for whoever next edits this needle.
- No other divergence in either direction: all six remaining checker-flagged labels (`branches-27-behind` ×6 lines, `py32-buffer-1024`, `porting-md-dual-slot`, `hex-extension-hardcoded`, `cli-handlers-821`, `host-head-311eacf`) map exactly onto the plan's remaining six named sites, one-to-one.

### Sites that are NOT stale (no row needed)

- The frontmatter (`date: 2026-07-28`) — correct and must stay unchanged (verified unchanged after the edit).
- The opening paragraph's own framing (lines 7-15, aside from the `2c2ed10` citation already covered) — this paragraph already correctly identifies the ROADMAP's claims as "out of date" as of 2026-07-28; it is itself a correction, not a fresh stale claim.
- `## PR #48 is much further along...` section's CI/SDK/build-detail bullets (lines 36-50) — unaffected by any research correction; still accurate.
- `## What is NOT done` section's other bullets (pin map, closed-loop DAC VPP, zero hardware validation, lines 57-65) — still accurate; only the `PORTING.md` sentence (line 61) is stale.
- `## Trap: PR #47 looks complete and is not` (lines 67-83) — still accurate; no research correction touches it.
- Host-side FW-install seams table's seam 1 ("Board identity") and seam 3 ("Flasher") rows, and the "Reusable shape already present" / "Two safety defects surfaced" paragraphs (lines 92-93, 98-126 minus line 107) — still accurate; only seam 2's extension-hardcoding phrase (line 94) and seam 4's line number (line 96) and the branch-head/milestone-slot sentence (line 107) are stale.
- `## Sizing` section's first two sentences (lines 129-131, "Host-side is one phase..." through "...ROADMAP already flags") — still accurate; only the closeable-scope sentence that follows (lines 131-134) is stale.
- The `PR #48` branch/PR-state columns in the Real Inventory table (OPEN/CLOSED, ahead-counts) other than the "27 behind" figure — no needle names them, and this plan does not independently re-verify live upstream GitHub PR state (out of scope; the "27 behind" correction is the only figure this checker's needle table and 130-RESEARCH.md's work list assign to this table).

`git -C /workspaces diff --stat -- .planning/notes/py32f071-port-branch-state.md` was empty at the end of Task 1 (confirmed before any edit).

## The 130-02 Decision Point

130-02's SUMMARY flagged, specifically for this plan, that a literal reading of this plan's own scope bullet ("an append-only SUPERSEDED section, with the dated body proven byte-unchanged by hash") is in tension with the checker's exemption mechanisms, which are both forward-block-scoped (mechanism 1) or same-line-scoped (mechanism 2) — neither can retroactively cover a line that sits *above* an appended section without editing that line. Two resolutions were offered:

1. Add an inline `recordscan:history` marker to each of the twelve original lines.
2. Extend `check_record_corrections.py` with a third exemption mechanism recognizing a trailing SUPERSEDED section as retroactively covering specific lines.

**Chosen: Resolution 2.** Reasoning:

- **Resolution 1 is not actually available under this plan's own constraints.** This plan's frontmatter `must_haves.prohibitions` explicitly states: *"Do NOT add inline recordscan markers to individual body lines here. The SUPERSEDED section is the mechanism for this file; scattering markers through a dated capture defeats the append-only intent."* Taking Resolution 1 would violate this plan's own prohibition, not merely create tension with a "spirit" reading — it is foreclosed by the letter of the frontmatter I am executing.
- **Resolution 2 was explicitly authorized as in-scope** by both 130-02's SUMMARY ("arguably in scope for `130-09` itself since that plan owns `notes/py32f071-port-branch-state.md`'s CLOSE-01 discharge") and this plan's own dispatch prompt ("one of your two available resolutions legitimately edits `check_record_corrections.py`... this plan is entitled to extend").
- **Both of this plan's own criteria are satisfied simultaneously, not traded off.** The dated body's byte-unchanged property (`head -134 | sha256sum` identical before/after, `git diff` showing zero removed lines) AND the checker's zero-unlabeled-hits requirement are both true at the same time — there is no unresolved conflict to record as "which one I honored instead of the other." Building the missing capability into the checker, rather than accepting a forced choice between the two, was the whole point of treating this as a real decision rather than a shortcut.
- **What I gave up:** nothing structural for the other four scanned files — mechanisms 1 and 2 are completely untouched, all 15 of 130-02's pre-existing tests pass unchanged, and the needle table (12 labels, same regexes) was not weakened, narrowed, or reworded anywhere. What I did accept is a genuine, permanent widening of the checker's vocabulary: a fourth planning record could in principle invoke `recordscan:supersedes` in the future. I judged this an acceptable, narrowly-fenced widening (see "How narrowly this is scoped" below) rather than a loophole, because it requires machine-checkable specificity (a real needle label, explicit line numbers, a stated reason) that "just add a SUPERSEDED heading" cannot satisfy by itself.

### How narrowly mechanism 3 is scoped (proven, not merely asserted)

- **The trigger is exact marker syntax**, `<!-- recordscan:supersedes needle=<label> lines=<n,n,...> reason: <text> -->` — never the English word "superseded" in a heading or prose. A file titled `## SUPERSEDED` with no marker exempts nothing new under this mechanism (mechanism 1's existing block behaviour is unchanged and orthogonal).
- **The needle label must be one of the twelve real labels in `_NEEDLE_LABELS`.** `test_supersedes_marker_with_unknown_needle_label_does_not_exempt` mutates a working marker's label to a one-character typo (`branches-27-behnid`) and proves both previously-covered lines revert to `unlabeled` — a misspelled or fabricated label exempts nothing, it does not raise or warn, it silently fails closed.
- **The line-number list is an explicit enumeration, never a range or "the rest of the file."** `test_superseded_section_control_fails_on_the_uncovered_line_only` plants the identical needle on two lines, covers only one by number, and proves the SECOND stays `unlabeled` — naming one line does not exempt a sibling occurrence of the same label elsewhere in the same file.
- **A reason is mandatory**, exactly mirroring mechanism 2's `_marker_has_reason` requirement. `test_supersedes_marker_with_no_reason_does_not_exempt` proves a marker with `needle=`/`lines=` present but no reason text exempts nothing.
- **Reachability was proven by mutation**, not merely asserted: `_collect_superseded_targets` was temporarily replaced with a body that returns an empty dict unconditionally, and the two positive-direction tests (`test_superseded_section_control_fails_on_the_uncovered_line_only`, `test_superseded_section_full_control_exits_zero`) both flipped to failure, confirming the real green result depends on the new function actually doing something. The file was restored and diffed byte-identical against the pre-mutation copy, and the full 20-test suite was re-run green before proceeding.

## Decisions Made

- **Resolution 2 over Resolution 1** — see "The 130-02 Decision Point" above.
- **One `recordscan:supersedes` marker per row** (7 markers total, one per distinct needle label, each naming its own line or line-set) rather than one giant marker for the whole section — keeps each marker's reason text specific to what it covers and keeps the mutation/removal tests targeted.
- **The closeable-scope paragraph got a row despite the checker not flagging it** — honored because this plan's `must_haves.truths` explicitly names it as a stale site to cover, independent of what the machine gate catches. Recorded as a checker limitation (line-wrap gap) rather than silently omitted.
- **Did not attempt to fix the checker's line-wrap miss for `branches-27-behind`** — that would be a change to needle-matching behavior across all five scanned files, out of this plan's scope (which owns the notes file and, by extension only, mechanism 3). Flagged in the divergence section above for whoever next touches that needle.

## Deviations from Plan

**1. [Rule 4 — architectural change, pre-authorized] Extended `check_record_corrections.py` with a third exemption mechanism.**
- **Found during:** Task 2, at the decision point 130-02 flagged in advance.
- **Issue:** The plan's own prohibitions forbid the only alternative (per-line markers on the original body), and the two existing exemption mechanisms cannot retroactively cover a line above an appended section.
- **Fix:** Added `recordscan:supersedes` (mechanism 3) — see "The 130-02 Decision Point" above for full reasoning and scoping proof.
- **Files modified:** `check_record_corrections.py`, `test_check_record_corrections.py`, two new fixtures.
- **Verification:** 20/20 tests pass (15 pre-existing unaffected + 5 new covering positive/negative/mutation/narrow-scoping directions); reachability proven by temporarily neutering the new function and confirming both positive tests flip to failure, then restoring byte-identically.
- **Committed in:** `3fb6a04` (feat, separate from the note-append commit).

This was not a silent scope expansion — it was explicitly flagged as an open decision by 130-02, explicitly authorized as in-scope by both 130-02's SUMMARY and this plan's own dispatch instructions, and is fully documented here including what was and was not given up.

**Total deviations:** 1, pre-authorized architectural extension (Rule 4, explicitly sanctioned in advance).
**Impact on plan:** Resolves the tension 130-02 flagged without weakening any needle, without touching the note's dated body, and without creating a blanket "any file can escape by writing the word superseded" loophole — proven by 5 new negative/mutation tests.

## Issues Encountered

None beyond the anticipated 130-02 decision point, which is documented above as the plan's central deviation rather than as an "issue."

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `notes/py32f071-port-branch-state.md` is green under `check_record_corrections.py` in isolation (0 unlabeled, 12 superseded, 13 block) and contributes zero `unlabeled` hits to the default five-target run going forward.
- The default five-target run still exits 1 (2 `arm-toolchain-absent`, 1 `branches-27-behind`, 2 `leonardo-headroom-2992`, 3 `part-with-no-vtor`, 1 `third-stack-2c2ed10`, all in `ROADMAP.md`/`REQUIREMENTS.md`) — owned by plans `130-06`/`130-10`, unaffected by this plan's changes, confirmed by direct measurement after this plan's commits landed.
- `check_record_corrections.py`'s new mechanism 3 is available to any later plan (in this milestone or a future one) that needs to retroactively supersede a dated capture without editing it — the module docstring's "Why a fourth mechanism exists" paragraph and this SUMMARY's scoping proof are the reference for that decision.
- No requirement id was ticked by this plan, per its own frontmatter (`requirements: [CLOSE-01]`, ticked only by `130-16`).
- `git -C /workspaces rev-parse --abbrev-ref HEAD` confirmed `gsd/v1.23-py32f071-integration` after every commit in this plan (checked 3 times: after the checker-extension commit, after the note-append commit, and immediately before writing this SUMMARY).

---
*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Completed: 2026-08-02*

## Self-Check: PASSED

All created/modified files found on disk (`check_record_corrections.py`, `test_check_record_corrections.py`,
both new fixtures, `notes/py32f071-port-branch-state.md`, this SUMMARY). All three task commit hashes
(`3fb6a04`, `f33e787`, `f70ac72`) found in `git log --oneline --all`. `REQUIREMENTS.md`/`ROADMAP.md`/
`STATE.md`/`PROJECT.md` confirmed untouched (`git status --short` empty for all four). Full 20-test suite
re-run green. `check_record_corrections.py` re-run against the note alone: exit 0, 0 unlabeled, 12
superseded, 13 block. `git rev-parse --abbrev-ref HEAD` confirmed `gsd/v1.23-py32f071-integration`.
