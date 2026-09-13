---
phase: 187-answered-reports
plan: 06
subsystem: infra
tags: [github-api, reply-drafting, dev-test, chip-database, permalinks]

requires:
  - phase: 187-05
    provides: "The shape and hash discipline for evidence/bodies/*.md and 187-UPSTREAM-REPLIES.md (per-issue PENDING OPERATOR REVIEW status lines, the Dispositions table, the REPLY-05-applicability section pattern), and the pinned meta merge SHA / app version / firmware version this plan's bodies also cite"
provides:
  - "evidence/bodies/187-gh23.md, 187-gh28.md, 187-gh31.md — the REPLY-01/REPLY-02 posting payloads, drafted to disk and posted nowhere"
  - "187-UPSTREAM-REPLIES.md extended with ## gh#23, ## gh#28, ## gh#31 sections, each body inline byte-identically to its file; the three stale 'drafted by 187-06' annotations corrected"
  - "evidence/187-06-draft-link-check.txt and evidence/187-06-body-hashes.txt — the link resolution (zero URLs, with the reason recorded) and sha256 hash-binding for the 187-09/187-10/187-11 approval gates"
affects: [187-09, 187-10, 187-11, 187-12]

actuals:
  tokens: 5800
  tasks: 3
  commits: 3
  plan_head_before: 1b9967e7

tech-stack:
  added: []
  patterns:
    - "Verified byte-identity between each inline review-document body and its standalone file with a small python regex extraction (matching 187-05's own precedent) rather than eyeballing a diff"
    - "Documented a zero-URL evidence file with an explicit 'why no link exists' section, rather than inventing a permalink the plan's own read_first/action never asked for"

key-files:
  created:
    - .planning/phases/187-answered-reports/evidence/bodies/187-gh23.md
    - .planning/phases/187-answered-reports/evidence/bodies/187-gh28.md
    - .planning/phases/187-answered-reports/evidence/bodies/187-gh31.md
    - .planning/phases/187-answered-reports/evidence/187-06-draft-link-check.txt
    - .planning/phases/187-answered-reports/evidence/187-06-body-hashes.txt
  modified:
    - .planning/phases/187-answered-reports/187-UPSTREAM-REPLIES.md

key-decisions:
  - "Drafted all three bodies (gh#23, gh#28, gh#31) with zero https:// links. Unlike gh#60/gh#62 (187-05), which each answer against an existing .planning/notes/ verdict document written for that purpose, no such document exists for the three standing datasheet defects or for the D-11 status-axis mechanism, and neither task's read_first/action named one to cite. Recorded the reasoning explicitly in evidence/187-06-draft-link-check.txt rather than inventing a citation the plan never specified."
  - "Removed a cross-chip mention ('same as the M27C512 in the sibling thread') from the first draft of gh#31's body after Task 2's own verify leg caught it grepping for 'm27c512' in 187-gh31.md — replaced with 'unlike the EEPROM case in the sibling thread', which names no chip and keeps each body naming only its own chip."
  - "Left the two pre-existing 'PENDING OPERATOR REVIEW' prose mentions (187-UPSTREAM-REPLIES.md lines 10 and 30, both written by 187-05, both explanatory sentences rather than per-issue status lines) untouched, rather than rewording 187-05's own prose to force Task 3's literal grep -c count to exactly 5. Verified directly that the actual invariant — exactly five '**Status — gh#N:**' lines — holds; documented the raw-count discrepancy below rather than silently editing content this plan does not own."

requirements-completed: [REPLY-01, REPLY-02, REPLY-05, REPLY-06]

coverage:
  - id: D1
    description: "gh#23's reply drafted: concedes the rig-fault-reported-as-chip-verdict diagnosis in full, states plainly (separately from the concession) that the tool did not and cannot become able to see an unhooked VPP, quotes the shipped rail_reading_disclosure sentence verbatim, restates the W27E257 vpp_mv=13500 (datasheet 12V) defect as unfixed with the generator's decode function as fix locus, names cause:rig/needs:report with reasons, carries the REPLY-05 sentence with the re-run ask, and does not imply a w27e257 PASS exists"
    requirement: "REPLY-01"
    verification:
      - kind: other
        ref: "head -1 grep '^(---|#)' -> 0; grep -F '3.0.0b39' -> 1; grep -F '3.0.0b27' -> 1; grep '13' | grep -i 'v' -> 1; grep -i schema -> 1; grep -E 'blob/(beta|main)/' -> 0; gh issue list --search w27e257 --json title --jq 'select(title matches PASS)' -> 0"
        status: pass
    human_judgment: true
    rationale: "Whether the concession register and the honest-limit statement read faithfully to the reporter (D-13's register, matching the 152/173 precedent) is a judgment call the plan's own success criteria route to the 187-09 operator gate, not something a grep can certify."
  - id: D2
    description: "gh#28 and gh#31 drafted as two distinct bodies (verified distinct sha256), each naming only its own chip's datasheet defect with its measured value and the generator's decode function as fix locus, each carrying the D-12 write-shortcut caveat before the re-run ask without proposing a new report field, each withholding fix:released with a stated reason and adding needs:report, and each carrying the REPLY-05 sentence with the ask"
    requirement: "REPLY-02"
    verification:
      - kind: other
        ref: "sha256sum both -> 2 distinct; grep -il m27c512/m27c1001 cross-checks -> each body names only its own chip (0 cross-mentions after the gh#31 fix); grep -c fix:released -> 1 each; grep -il schema -> 2; app/fw version presence -> 0 missing; grep -E blob/(beta|main)/ -> 0"
        status: pass
    human_judgment: true
    rationale: "Whether the caveat's placement and register are honest and readable to two different reporters about two different chips is routed to the 187-10/187-11 operator gates, matching D2's own precedent in 187-05-SUMMARY.md."
  - id: D3
    description: "All URLs in the three bodies resolved (zero found, reason recorded); one sha256 line per body written for the 187-09/187-10/187-11 gates; 187-UPSTREAM-REPLIES.md extended with three new ## gh#N sections carrying each body inline byte-identically, the three stale annotations corrected, and the REPLY-05-applicability section extended — with nothing posted, labelled, or closed"
    verification:
      - kind: other
        ref: "grep -o https:// across all three bodies -> 0 matches; grep -c 'sha256(' body-hashes.txt -> 3, all match sha256sum of the files on disk; grep -c '^## gh#' -> 5; grep -c '^**Status — gh#' -> 5 (raw 'PENDING OPERATOR REVIEW' literal count is 7, inflated by two pre-existing 187-05 prose sentences, not per-issue status lines); ls evidence/bodies/ -> 5 files; python3 regex byte-identity check for gh23/gh28/gh31 inline vs file -> MATCH for all three (3675/2821/2775 bytes... see body)"
        status: pass
    human_judgment: false

duration: 16min
completed: 2026-09-12
status: complete
---

# Phase 187 Plan 06: Draft gh#23, gh#28, gh#31 reply bodies Summary

**Drafted the three replies to the disputed `dev test` triage threads — gh#23 (W27E257), gh#28 (M27C512) and gh#31 (M27C1001) — each conceding the reporters' attribution objection in full, keeping the three still-unfixed datasheet defects standing with their measured values, and asking for a re-run with every known caveat (D-11's honest limit on gh#23, D-12's write-shortcut caveat on gh#28/gh#31) attached, without posting, labelling or closing anything.**

## Performance

- **Duration:** 16 min
- **Tasks:** 3
- **Files modified:** 6 (5 created, 1 modified)

## Accomplishments

- Drafted `evidence/bodies/187-gh23.md` (REPLY-01): concedes AndersBNielsen's diagnosis — a rig
  fault reported as a chip verdict — in the first two sentences, then states separately and
  plainly that the tool did not and cannot become able to see an unhooked VPP (the status axis
  only fires on `SerialError`/`HardwareOperationError`; a mis-wired VPP produces bad data instead,
  so a fresh run would still file `FAIL`). Names what actually changed (the misleading
  `vpp_mv`/`vpe_mv` fields removed, the `rail_reading_disclosure` sentence added, quoted verbatim).
  Restates the W27E257 `13.5 V` vs datasheet `12 V` programming-voltage defect as unfixed, with the
  fix locus named as the database generator's decode function. Notes the EEPROM/UV-EPROM split (no
  UV-slot harness work applies to this chip). Is explicit that no w27e257 PASS run exists anywhere
  in the tracker, so the concession is of the general point only. Names `cause:rig` and
  `needs:report` with reasons. Carries the REPLY-05 `schema_version`/`dedup_fingerprint` sentence
  in the same section as the re-run ask, naming both cut versions (`3.0.0b39` app, `3.0.0b27`
  firmware) byte-exactly. States the issue stays open.
- Drafted `evidence/bodies/187-gh28.md` (REPLY-02, M27C512) and `evidence/bodies/187-gh31.md`
  (REPLY-02, M27C1001) as two distinct bodies — verified distinct sha256, each naming only its own
  chip and its own datasheet defect (M27C512's `6.5 V` programming supply against its `5 V`
  operating supply with nothing applying it; M27C1001's pin 30 mapped as an address line where the
  datasheet gives no connection, still on the 32-pin 27C020 pin map). Both name the generator's
  decode function as the fix locus and state the UV-EPROM/UV-slot-work split explicitly. Both
  carry the D-12 write-shortcut caveat (the harness now passes a non-blank UV part via a blank-check
  skip that `firestarter write` itself does not take, so a re-run PASS does not mean `write` works)
  in a section that comes before the re-run ask, without proposing any new report field for it.
  Both explicitly withhold `fix:released` (only the harness attribution fix shipped; the chip
  defect did not) and add `needs:report` instead. Both carry the REPLY-05 sentence with the ask and
  both cut versions byte-exactly. Both state the issue stays open.
- Caught and fixed a cross-chip contamination during Task 2's own verification: an early draft of
  gh#31's body referenced "the M27C512 in the sibling thread"; Task 2's own `<verify>` leg
  (`grep -il m27c512 187-gh31.md`) caught it before the commit, and the sentence was reworded to
  "the EEPROM case in the sibling thread" (naming no chip), re-verified, then committed.
- Extracted every URL from the three new bodies (zero found) and recorded the result, with the
  reason no link exists, in `evidence/187-06-draft-link-check.txt`: unlike gh#60/gh#62 (187-05),
  which each answer against an existing `.planning/notes/` verdict document, no such document
  exists for these three chip defects or for the D-11 mechanism, and neither task's own
  `read_first`/`action` named one to cite.
- Wrote `evidence/187-06-body-hashes.txt` with one `sha256(<path>) = <hash>` line per body, for the
  187-09/187-10/187-11 approval gates to bind against.
- Extended `187-UPSTREAM-REPLIES.md`: corrected the three stale "drafted by 187-06, not yet
  drafted"/"drafted by 187-06" annotations (in the header status lines and the Dispositions table)
  to "drafted below" without altering any Dispositions table row's substance; extended the
  REPLY-05-applicability section to record that all three new bodies carry a re-run ask and the
  REPLY-05 sentence in the same section as that ask; appended `## gh#23`, `## gh#28`, `## gh#31`
  sections, each carrying its body inline, confirmed byte-identical to its standalone file by a
  python regex extraction (3675 / 2821 / 2775 bytes respectively, matching exactly).
- Confirmed after all three tasks that nothing was posted, labelled, or closed: no `gh issue
  comment`, `gh issue edit`, or `gh issue close` command was run against gh#23, gh#28, or gh#31 in
  this plan; the only live-tracker call made was the read-only `gh issue list --search w27e257`
  leg Task 1's own `<verify>` required.

## Task Commits

Each task was committed atomically:

1. **Task 1: Draft gh#23** - `8ab7d268` (docs)
2. **Task 2: Draft gh#28 and gh#31** - `2fda6d28` (docs)
3. **Task 3: Resolve links, hash-bind, extend the review document** - `083f93f9` (docs)

**Plan metadata:** committed alongside this SUMMARY (see final commit below).

## Files Created/Modified

- `.planning/phases/187-answered-reports/evidence/bodies/187-gh23.md` - REPLY-01 posting payload
- `.planning/phases/187-answered-reports/evidence/bodies/187-gh28.md` - REPLY-02 posting payload (M27C512)
- `.planning/phases/187-answered-reports/evidence/bodies/187-gh31.md` - REPLY-02 posting payload (M27C1001)
- `.planning/phases/187-answered-reports/evidence/187-06-draft-link-check.txt` - zero-URL result and the reason recorded
- `.planning/phases/187-answered-reports/evidence/187-06-body-hashes.txt` - sha256 for all three bodies
- `.planning/phases/187-answered-reports/187-UPSTREAM-REPLIES.md` - extended with the three new sections, corrected annotations, extended REPLY-05-applicability section

## Decisions Made

- No links in any of the three bodies — no existing `.planning/notes/` document covers these three
  defects, and neither task instructed one to be constructed; recorded the reasoning in the
  link-check evidence file rather than inventing a citation.
- Fixed the cross-chip mention caught by Task 2's own verify leg (see Deviations below).
- Left 187-05's own pre-existing prose (two non-status-line mentions of the literal
  `PENDING OPERATOR REVIEW` phrase) untouched rather than reworded to force an unrelated grep count
  to exactly 5; verified the actual per-issue status-line invariant directly instead.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] gh#31's first draft named the sibling chip, violating its own "only its own chip" acceptance criterion**
- **Found during:** Task 2 (re-running the task's own `<verify>` legs before committing)
- **Issue:** The first draft of `evidence/bodies/187-gh31.md` included the sentence "...does apply to it, same as the M27C512 in the sibling thread," which named gh#28's chip inside gh#31's body — caught by `grep -il 'm27c512' 187-gh31.md` returning 1 instead of the required 0.
- **Fix:** Reworded to "...does apply to it — unlike the EEPROM case in the sibling thread," which conveys the same UV-EPROM/EEPROM split without naming either sibling chip by part number.
- **Files modified:** `.planning/phases/187-answered-reports/evidence/bodies/187-gh31.md`
- **Verification:** Re-ran all of Task 2's `<verify>` legs after the fix; `grep -il 'm27c512' 187-gh31.md` now returns 0, and all other legs (distinct sha256, own-chip presence, `fix:released` count, schema mention, version presence, no branch links) pass.
- **Committed in:** `2fda6d28` (the fix was applied before the task's only commit — no separate fix commit exists)

---

**Total deviations:** 1 auto-fixed (1 bug, caught by the plan's own verify leg before commit).
**Impact on plan:** The fix was caught and corrected within the same task, before any commit; no scope creep, no separate remediation commit needed.

## Issues Encountered

- Task 3's literal `grep -c 'PENDING OPERATOR REVIEW'` leg reads 7, not the 5 the plan's own
  `<verify>` and acceptance criteria expect. This is not something this plan introduced: two of the
  seven occurrences (lines 10 and 30 of `187-UPSTREAM-REPLIES.md`) are pre-existing explanatory
  prose written by Plan 187-05 ("...starting at the literal `PENDING OPERATOR REVIEW`..." and
  "...both wait at `PENDING OPERATOR REVIEW`.") rather than per-issue status lines. Plan 187-05's
  own SUMMARY documented the identical discrepancy for the same reason (its D3 verification records
  "`grep -c 'PENDING OPERATOR REVIEW'` -> 7 (>=5)"). The actual invariant the acceptance criterion
  cares about — exactly five `**Status — gh#N:**` per-issue status lines — was verified directly
  (`grep -c '^\*\*Status — gh#'` returns 5) and holds. No pre-existing 187-05 prose was reworded to
  force the raw literal-phrase count to exactly 5, since that prose is not owned by this plan and
  rewording it to satisfy an over-broad grep would risk altering content this plan has no
  instruction to touch.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `187-07` through `187-11` have everything they need to run the five per-issue operator gates:
  all five bodies now exist (gh#60/gh#62 from 187-05; gh#23/gh#28/gh#31 from this plan), all five
  are hash-bound (`evidence/187-05-body-hashes.txt` and `evidence/187-06-body-hashes.txt`), and
  `187-UPSTREAM-REPLIES.md` carries all five sections with all five status lines still reading
  `PENDING OPERATOR REVIEW`.
- `187-12`'s closeout will need to reconcile the raw `PENDING OPERATOR REVIEW` literal count
  (currently 7, not 5) if any future gate re-checks that exact figure — the discrepancy is
  documented above and is unrelated to any issue's actual approval state.
- No blockers. Nothing public changed; gh#23, gh#28, and gh#31 remain exactly as Task 1's live
  tracker check found them (all three OPEN, unmodified labels, last reporter comment still
  2026-08-09).

## Self-Check: PASSED

- `.planning/phases/187-answered-reports/evidence/bodies/187-gh23.md` — FOUND
- `.planning/phases/187-answered-reports/evidence/bodies/187-gh28.md` — FOUND
- `.planning/phases/187-answered-reports/evidence/bodies/187-gh31.md` — FOUND
- `.planning/phases/187-answered-reports/evidence/187-06-draft-link-check.txt` — FOUND
- `.planning/phases/187-answered-reports/evidence/187-06-body-hashes.txt` — FOUND
- Commit `8ab7d268` — FOUND
- Commit `2fda6d28` — FOUND
- Commit `083f93f9` — FOUND
- All Task 1-3 `<verify>` legs and acceptance criteria re-run and passed after the gh#31 fix (see
  body above); no issue posted to, labelled, or closed on the live tracker.

---
*Phase: 187-answered-reports*
*Completed: 2026-09-12*
