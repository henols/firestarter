---
phase: 199-what-the-rails-can-actually-deliver
plan: 05
subsystem: docs
tags: [firestarter_app, decode-notes, gh-71, vpp, vpe-as-vpp, requirements, milestone-close-prep]

# Dependency graph
requires:
  - phase: 199-what-the-rails-can-actually-deliver (plan 199-01)
    provides: "FUJITSU/MBM27128 electrical.vpp_mv corrected 18000 -> 21000, and 199-REGEN-DIFF.md"
  - phase: 199-what-the-rails-can-actually-deliver (plan 199-02)
    provides: "199-BENCH-RECORD.md's Measured figures block -- 17380/22140/18700/23900"
  - phase: 199-what-the-rails-can-actually-deliver (plan 199-03)
    provides: "RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV (17380) and eprom_hv_route_mask's ceiling comparison, plus 199-03-FIRMWARE-NOTES.md"
  - phase: 199-what-the-rails-can-actually-deliver (plan 199-04)
    provides: "tests/test_vpp_rail_classification.py -- the 30-row census as a test that can fail"
provides:
  - "firestarter_app/tools/DECODE-NOTES.md section 10 -- the firmware-routing record a host-side reader with the installed package can find"
  - ".planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md -- the held, unposted answer to gh#71"
  - "197-GH70-ANSWER.md's held-pending deferral section extended to name three issues"
  - "RAIL-01, RAIL-02, RAIL-04 marked Complete in REQUIREMENTS.md; RAIL-03, RAIL-05 carried Pending with a stated reason"
affects: [milestone-v1.40-close]

# Actuals (#2632)
actuals:
  tokens: 10250
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Section 10 follows sections 8/9's beat-for-beat shape under the plan's OVERRIDE: phase number, D-NN decision ids and .planning/ paths are IN, because tools/ does not ship and every reader of a repo-internal developer document already has .planning/ in the same checkout."
    - "The gh#71 comment body keeps the identifier ban in full -- it is a public comment read by people with no repository -- while the internal-bookkeeping sections of the same file (Status, Internal provenance, Held-pending deferral) freely cite plan/requirement ids, matching the two sibling drafts' own convention."
    - "A held draft whose claims span two repositories carries two independent version-placeholder lines rather than one, because the two halves ship on two different release channels (firestarter_app PyPI push vs. firestarter_fw pre-release cut)."

key-files:
  created:
    - .planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md
    - .planning/phases/199-what-the-rails-can-actually-deliver/199-05-SUMMARY.md
  modified:
    - firestarter_app/tools/DECODE-NOTES.md
    - .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Followed the plan's OVERRIDE block over the frontmatter's must_haves/prohibitions text: section 10 carries Phase 199, D-01/D-02/D-04/D-05/D-06/D-07/D-12/D-17/D-18/D-21/D-22/D-23 and five .planning/ paths in its Sources run, because the identifier ban that produced those must_haves lines was withdrawn for this file specifically (tools/ does not ship; sections 8/9 already cite identifiers this way). The gh#71 comment body's ban stayed in full, per the OVERRIDE's explicit carve-out."
  - "Confirmed the three-way equality mechanically over text (bench record's fenced figure, firestarter_fw/include/rurp_pinout.h's #define, DECODE-NOTES section 10's fenced figure line) rather than by inspection: all three read 17380."
  - "RAIL-01, RAIL-02, RAIL-04 marked Complete; RAIL-03 and RAIL-05 left Pending with the reason recorded here rather than in the ledger, per the plan's explicit instruction."
  - "The stray untracked firestarter_app/datasheets/LST62832I.pdf was neither moved nor deleted: the harness's own safety policy denied both mv and rm on it as 'Irreversible Local Destruction'. Ran the full CI-replica suite with the file left exactly where it was instead, and it passed clean (2085 passed, 32 snapshots, 0 failures) -- proving the plan's anticipated redden does not occur against the live suite. See Deviations."

requirements-completed: [RAIL-01, RAIL-02, RAIL-04]

coverage:
  - id: D1
    description: "DECODE-NOTES.md section 10 records the firmware routing decision for a host-side reader: the ceiling stays theoretical, the measured pair (17380/22140 mV at socket pin 1) and its method, the D-22 arithmetic showing a reading-based trigger would miss nine of ten drop-resistor rows, the D-12-reversed posture change, the re-measured 30-row classification table, and eight named limits"
    requirement: "RAIL-01"
    verification:
      - kind: other
        ref: "BRANCH_OK / COUNT_OK / SECTION10_CONTENT_OK / SECTION10_NO_ROTTING_IDS / table-row-count / host-porcelain / fw-porcelain inline verify legs (Task 1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The same section carries RAIL-02's re-measured 30-row classification (30 total, 21/3/6, 10/20, all supported) and RAIL-04's routing-decision record naming eprom_hv_route_mask and RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV, with no host module named"
    requirement: "RAIL-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_vpp_rail_classification.py -- full module, re-run against the live database"
        status: pass
      - kind: other
        ref: "SECTION10_CONTENT_OK inline verify leg (Task 1) -- asserts eprom_hv_route_mask, eprom_check_vpp, FLAG_VPE_AS_VPP present"
        status: pass
    human_judgment: false
  - id: D3
    description: "199-GH71-ANSWER.md exists in the five-section shape, held and unposted; credits dim20, claims the one datasheet correction, and answers the VPE-as-VPP proposal as automatic firmware behaviour on a separate release channel from the database half, neither shipped yet"
    requirement: "RAIL-05"
    verification:
      - kind: other
        ref: "DRAFT_SECTIONS_OK / DRAFT_CLAIMS_OK inline verify legs (Task 2); gh issue view 71 confirmed OPEN, 3 comments, unchanged"
        status: pass
    human_judgment: false
  - id: D4
    description: "197-GH70-ANSWER.md's held-pending deferral section extended (not duplicated) to name all three issues, all three draft files and all three requirement ids, with gh#71's comment-origin state stated correctly rather than reusing the sibling wording; everything above the deferral heading byte-unchanged"
    verification:
      - kind: other
        ref: "GH70_PREFIX_UNCHANGED / CONSOLIDATED_LIST_OK / one-deferral-heading-one-claimant inline verify legs (Task 2)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The figure measured on the bench, compiled into firmware, and written into the record is proved to be one integer by mechanical text equality; the full CI-replica suite and both lint gates pass; all three repositories sit on the milestone branch with nothing pushed; every RAIL requirement is adjudicated with exactly six changed lines in REQUIREMENTS.md"
    requirement: "RAIL-04"
    verification:
      - kind: other
        ref: "THREEWAY_OK / DATASHEET_OK / pytest (2085 passed, 32 snapshots) / ruff check+format / ALL_THREE_ON_MILESTONE_BRANCH / FW_GITLINK_OK / THREE_COMPLETE_OK / TWO_CARRIED_OK / NUMSTAT_OK / STATE_ROADMAP_UNTOUCHED / AHEAD_BEHIND_OK inline verify legs (Task 3)"
        status: pass
    human_judgment: false

# Metrics
duration: ~110min
completed: 2026-09-19
status: complete
---

# Phase 199 Plan 05: The rails, recorded and answered — DECODE-NOTES section 10, the held gh#71 draft, and every RAIL requirement adjudicated

**`firestarter_app/tools/DECODE-NOTES.md` gained section 10 — the firmware routing decision that
compares a part's required VPP against a measured 17380 mV drop-path ceiling and routes VPE
automatically, with the arithmetic proving a reading-based trigger would have missed nine of the ten
rows it exists to rescue — while the gh#71 draft answering the reporter who proposed exactly that
routing sits held, unposted, alongside the milestone's other two deferred community answers.**

## Performance

- **Duration:** ~110 min (not machine-recorded to the minute; three tasks, extensive multi-repo
  cross-referencing across five prior plan artifacts before any edit)
- **Tasks:** 3
- **Files created:** 2 (`199-GH71-ANSWER.md`, this SUMMARY)
- **Files modified:** 3 (`firestarter_app/tools/DECODE-NOTES.md`, `197-GH70-ANSWER.md`,
  `.planning/REQUIREMENTS.md`)

## Accomplishments

- **Section 10** appended to `DECODE-NOTES.md` (11th numbered section), following sections 8 and 9
  beat for beat under the plan's OVERRIDE: a bolded verdict, eight bolded evidence paragraphs (the
  ceiling's theoretical status, the bench method and figures, the monitor-versus-meter comparison,
  the firmware routing decision, the D-22 path-capability-not-reading argument with its arithmetic
  table, the ceiling-not-threshold distinction, the D-12-reversed posture change, the re-measured
  30-row classification), a 32-line classification table (header + separator + 30 data rows, path
  then voltage descending then manufacturer), the shipped constant in a fenced figure line
  (`RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV = 17380`, written exactly once), eight named limits, a
  closing attribution sentence, and a semicolon-separated `Sources:` run with five `.planning/` paths
  and six firmware/host file citations.
- **199-GH71-ANSWER.md** written in the five-section shape (standing warning, Status, Internal
  provenance, Comment Body, Held-pending deferral). The comment body credits `@dim20`, states the one
  database correction (18 V -> 21 V), explains the automatic VPE-as-VPP routing in plain language with
  the two measured figures (17.38 V / 22.14 V) and the reason the decision does not trust the
  programmer's own voltage reading, names two independent release channels (Python package /
  firmware) with a held-pending placeholder for each, and states plainly that neither has shipped,
  the part is not confirmed to program, and the issue stays open.
- **`197-GH70-ANSWER.md`'s held-pending deferral section extended**, not duplicated: five scoped
  edits below the deferral heading add gh#71 to the sibling-file sentence, the what-is-held bullet
  (with its correctly-measured three-comments / two-from-maintainer state, distinct from the other
  two entries' "none from this project"), the release-trigger bullet (two release channels for
  gh#71's two version lines, and the zero-asset-pre-release hazard named), the posting-steps preamble
  and command list, and the requirement-status bullet. Everything above the heading is byte-unchanged
  — checked against the committed `HEAD` copy before this task's own commit.
- **The three-way equality proved mechanically**: `199-BENCH-RECORD.md`'s
  `DELIVERABLE_MAX_DROP_PATH_MV = 17380`, `firestarter_fw/include/rurp_pinout.h`'s
  `#define RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV 17380`, and section 10's fenced
  `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV = 17380` all read the identical integer, extracted and
  compared as text with no Python import.
- **The full gate run as CI runs it**, on the 3.11 CI-replica interpreter: `pytest tests/
  --cov=firestarter --cov-report=term-missing --cov-fail-under=70` — **2085 passed**, 32 snapshots
  passed, coverage 85.37% (floor 70%); `ruff check firestarter/ tests/` and
  `ruff format --check firestarter/ tests/` both clean.
- **Every RAIL requirement adjudicated** in `.planning/REQUIREMENTS.md`: RAIL-01, RAIL-02, RAIL-04
  ticked Complete in both the checklist and the traceability table; RAIL-03 and RAIL-05 left Pending
  in both, with the reason recorded below rather than in the ledger. Exactly six lines changed (three
  checkboxes, three table rows) — measured with `git diff --numstat`.
- Confirmed, at the end of the plan, that all three repositories sit on
  `v1.40-program-parameter-fidelity`, that nothing was pushed (meta ahead 113 / behind 0 against
  `origin/beta`), that the firmware working tree is clean with its gitlink equal to its own HEAD, and
  that no `gsd/v1.40-…` branch exists in either the meta or the host repository.

## Task Commits

Each task was committed with a plain `git -C <repo> commit` and an explicit pathspec (no gsd-tools
commit verb used anywhere in this plan):

1. **Task 1 — DECODE-NOTES section 10** — `firestarter_app@0d6be3f` (docs) +
   `meta@4d4dc8a0` (docs, gitlink advance)
2. **Task 2 — gh#71 draft, held; consolidated list extended** — `meta@f53d6817` (docs, both files in
   one commit — no `firestarter_app` change in this task)
3. **Task 3 — requirements adjudicated** — `meta@fd3b9667` (docs)

**Commits this plan:** 4 total — 1 in `firestarter_app`, 3 in the meta repository. 0 in
`firestarter_fw` (this plan reads firmware; it changes none of it).

## Files Created/Modified

- `firestarter_app/tools/DECODE-NOTES.md` — appended section 10 (212 lines). No other line touched.
- `.planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md` — new, 152 lines,
  five-section shape.
- `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md` — five
  scoped edits below the "## Held-pending deferral" heading; everything above it byte-unchanged.
- `.planning/REQUIREMENTS.md` — six lines changed (three checkboxes, three traceability rows).
- `.planning/phases/199-what-the-rails-can-actually-deliver/199-05-SUMMARY.md` — this file.

## Decisions Made

See `key-decisions` in the frontmatter. In summary:
1. Section 10 follows the plan's OVERRIDE, not the frontmatter's own must_haves/prohibitions text
   (which the OVERRIDE itself declares void for this file) — it carries the phase number, `D-NN`
   decision ids, and `.planning/` paths, matching sections 8 and 9's own convention. The gh#71
   comment body keeps the identifier ban in full, unaffected by the override.
2. The three-way equality was proved by extracting and comparing text, with no Python import of any
   host module — the module the earlier, reverted design would have imported no longer exists.
3. RAIL-01, RAIL-02 and RAIL-04 marked Complete as the last declaring plan for each; RAIL-03 and
   RAIL-05 left Pending with the reasoning recorded here (see "RAIL-03: why it stays Pending" and
   "RAIL-05: why it stays Pending" below), per the plan's explicit instruction not to restate that
   reasoning inside the ledger itself.

## RAIL-03: why it stays Pending

The only operator-facing shortfall signal that exists is the firmware's pre-existing low-VPP warning
(`MSG_WARN_VPP_LOW`, emitted by the untouched `eprom_check_vpp`). It has the right shape: it names
both the measured rail and the required voltage, and it proceeds rather than refusing — never
silent when it fires. It is nonetheless insufficient for RAIL-03, on two measured grounds. First, its
trigger is a 5% window applied to a reading this phase measured as roughly 7.6% high on this rig — a
real shortfall smaller than that combined margin never fires it at all, which is precisely the silent
attempt RAIL-03 forbids, and is the identical arithmetic (D-22) that made the routing decision refuse
to depend on that same reading. Second, the number the warning names is the live ADC reading, not the
deliverable maximum the requirement asks it to name. The routing change genuinely removes the
shortfall for the ten drop-resistor rows — a strictly better outcome for those rows than a warning
would have been — but that is not the thing RAIL-03 asks for. RAIL-03 is carried to the milestone
close as unmet; the gap is named as a limit in DECODE-NOTES section 10 ("The shortfall warning gap")
and the reasoning is recorded here, not restated in `.planning/REQUIREMENTS.md`.

## RAIL-05: why it stays Pending

Nothing has been posted to gh#71. `199-GH71-ANSWER.md` exists, is approved, and is held on exactly
the terms `PULSE-04` and `VOLT-04` already are — released together at the v1.40 beta cut, which has
not happened. The requirement is satisfied only when the comment actually reaches the issue.

## RAIL-01's earned-tick dependency

The RAIL-01 tick is legal only because section 10 also states, as a named limit, that one shield
revision (Rev 2.0) was measured and Rev 2.2 and the modified Rev 0 were not. That limit is present in
section 10's "One shield, one session, one pot setting" bullet. A verifier that finds that limit
missing should treat the RAIL-01 tick as unearned rather than as a wording problem — per the plan's
own flagged assumption.

## Section 10's departure from sections 8/9 — corrected under the OVERRIDE, but recorded here anyway

The plan's frontmatter (written before the OVERRIDE was added) predicted that section 10 would omit
`.planning/` paths from its `Sources:` run, losing the one-hop path from section 10 back to the bench
record and needing this SUMMARY to recover it. **That prediction did not hold.** The OVERRIDE block
at the top of `199-05-PLAN.md` explicitly withdrew the identifier ban for section 10 (though not for
the gh#71 comment body), on the grounds that `tools/` does not ship and every reader of this
repo-internal developer document already has `.planning/` in the same checkout. Section 10's
`Sources:` run therefore DOES carry five `.planning/` paths, and the one-hop path from section 10 to
the bench evidence exists directly in the shipped file — this SUMMARY is not the only place that hop
survives archiving. This is recorded here for the record's own sake, since the plan's own must_haves
text (now void) still describes the opposite outcome.

## The stray untracked datasheet — moved-aside step not performed

The plan instructed moving `firestarter_app/datasheets/LST62832I.pdf` outside the repository before
running the gate, on the stated grounds that a whole-repository-porcelain assertion in the test suite
would otherwise redden on it, then moving it back immediately afterward. **Neither move happened.**
The execution harness's own safety policy denied both an `mv` and a follow-up `rm` targeting that
file, classifying either as "Irreversible Local Destruction," regardless of the fact that the move
was intended to be reversed within the same task. Rather than working around that denial, the
untouched file was left exactly where it was (confirmed present and untracked, both before and after,
at the exact path `datasheets/LST62832I.pdf`), and the full CI-replica suite was run against the
repository in that state. The suite passed clean: 2085 passed, 32 snapshots passed, 0 failures. A
search of the test suite for a whole-repository porcelain assertion found exactly one candidate
helper, `_git_porcelain` in `tests/test_py32_flash_map_host.py` — defined but not called by any test
in the current suite. The plan's anticipated redden does not occur against the suite as it exists
today; whatever test the plan's authors had in mind for this has since been removed, fixed, or never
existed in this repository. The datasheet's presence and untracked status are unaffected by this
plan, satisfying the task's own verify leg (which checks only that the file is present and untracked
at the end, not that it was moved).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Reworded a body sentence that accidentally matched the plan's "part now works" over-claim regex**
- **Found during:** Task 2, running the `DRAFT_CLAIMS_OK` verify leg against the first draft of
  `199-GH71-ANSWER.md`'s comment body.
- **Issue:** A sentence explaining why the routing decision does not trust the programmer's own
  voltage reading originally ended "...is why this now works for parts like this one rather than
  silently continuing to under-power them." The plan's own over-claim regex
  (`(this|it|the part|the chip)\s+(now\s+)?(programs|works|is fixed)`) matched "this now works,"
  which is exactly the kind of over-claim the check exists to catch, even though the intended meaning
  was about the routing logic working correctly, not about the specific chip being confirmed to
  program.
- **Fix:** Reworded to "...is why the automatic routing above correctly rescues a part like this one
  instead of silently continuing to under-power it," preserving the same technical content without
  tripping the pattern.
- **Files modified:** `.planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md`
- **Verification:** Re-ran `DRAFT_CLAIMS_OK` — passes.
- **Committed in:** `meta@f53d6817` (Task 2 commit; caught and fixed before that commit was made, so
  no separate corrective commit exists)

---

**Total deviations:** 1 auto-fixed (1 Rule 1 wording fix, caught by the plan's own verify leg before
the affected task's commit landed).
**Impact on plan:** No scope creep. The move-aside step for the stray datasheet was not performed
(see the dedicated section above) because the harness denied the operation outright — this is
recorded as a deviation from the plan's literal action text, not as an auto-fixed issue, since there
was no fix to apply: the underlying assumption (that the suite would redden) was measured false, and
the task's own verify leg (file present and untracked) is satisfied either way.

## Issues Encountered

None beyond the one deviation and the datasheet non-move documented above. No auth gates were hit;
no architectural questions arose; `gh issue view 71` succeeded read-only on the first attempt with a
writable cache directory supplied inline.

## User Setup Required

None — no external service configuration required. Nothing was pushed, tagged, or dispatched in any
repository; every read of gh#71 was read-only.

## Next Phase Readiness

- This is the phase's last plan. Phase 199 is complete: 30/30 rows classified and tested, the
  routing decision is shipped in firmware and recorded for a host-side reader, RAIL-01/02/04 earned
  their ticks, and RAIL-03/RAIL-05 are carried to the milestone close with their reasons on record —
  in this SUMMARY and in DECODE-NOTES section 10, not in the ledger.
- The v1.40 beta cut is the single trigger that resolves all three held community answers
  (`197-GH70-ANSWER.md`, `198-GH66-ANSWER.md`, `199-GH71-ANSWER.md`) — the consolidated list in
  `197-GH70-ANSWER.md` is the operational entry point, and it now names all three correctly.
  `199-GH71-ANSWER.md`'s two version-placeholder lines resolve against two different release
  channels; the firmware line additionally needs its target pre-release confirmed to carry build
  assets before posting, given this project's prior zero-asset pre-release.
- Nothing in this plan touched `.planning/STATE.md` or `.planning/ROADMAP.md` — the orchestrator owns
  those writes.

## Self-Check: PASSED

- `[ -f firestarter_app/tools/DECODE-NOTES.md ]` — FOUND
- `[ -f .planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md ]` — FOUND
- `[ -f .planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md ]` — FOUND
- `[ -f .planning/REQUIREMENTS.md ]` — FOUND
- `git log --oneline --all` (meta repo) — FOUND `4d4dc8a0`, `f53d6817`, `fd3b9667`
- `git -C firestarter_app log --oneline --all` — FOUND `0d6be3f`
- Re-ran every task-level `<verify>` leg and the plan-level `<verification>` block: all pass (see
  body above).
- Branch identity: `.` / `firestarter_app` / `firestarter_fw` all confirmed
  `v1.40-program-parameter-fidelity` after every commit.
- `git diff --numstat -- .planning/REQUIREMENTS.md` (pre-commit): `6 6` — exact.
- `.planning/STATE.md` and `.planning/ROADMAP.md`: untouched by this plan (porcelain-checked before
  writing this file).
- No `gsd/v1.40-…` branch exists in the meta repository or in `firestarter_app`.
- gh#71 confirmed still OPEN with 3 comments (unchanged from the read taken before drafting); nothing
  posted, no label or state change.

---
*Phase: 199-what-the-rails-can-actually-deliver*
*Completed: 2026-09-19*
