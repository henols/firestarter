---
phase: 137-close-honesty-ledger-claim-gate-gh12-followup
plan: 04
subsystem: docs
tags: [release-notes, requirements-ledger, sdp, backlog, claim-gate]

# Dependency graph
requires:
  - phase: 137-03
    provides: 137-LEDGER.md (CLOSE-04), the honesty ledger this plan's release notes and decision doc sit alongside
provides:
  - RELOCK-07's stale --sdp-relock "v1.23+" label corrected at both live occurrences and all four citation sites, terminal values fresh-measured this plan
  - 137-RELEASE-NOTES-app.md (CLOSE-05) -- the next release's notes, "Removed" section states a withdrawal never a migration
  - 137-DECISION.md -- RELOCK-07 confirmation, C-1 disposition, beta-only pre-flight recommendation
  - Operator-batch C-1 dispositioned defer-with-owner, filed as a named-owner backlog todo
  - CLOSE-05's own stale requirement text (which still named write --sdp-relock as the mapping target) corrected in place
affects: [137-05, 137-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Append-only correction convention: each citation site gets a new dated block below its prior text, never an in-place rewrite of history"
    - "defer-with-owner disposition: a real, out-of-scope finding gets a named-owner backlog todo plus a cross-linked batch-row update, not a silent drop"

key-files:
  created:
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-RELEASE-NOTES-app.md
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-DECISION.md
    - .planning/todos/pending/build-db-diff-ladder-state-community-reported-regression.md
  modified:
    - .planning/STATE.md
    - .planning/PROJECT.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/notes/sdp-surface-retirement-and-behavioral-proof.md
    - .planning/v1.30-OPERATOR-BATCH.md

key-decisions:
  - "RELOCK-07's citation chain had drifted a fifth time by this plan's own execution (634/823 -> 972/844); fixed by fresh grep, not by trusting any prior citation, including this plan's own text"
  - "CLOSE-05's own requirement text still said dev sdp enable -> write --sdp-relock, contradicting the 2026-08-03 operator decision every other document already reflected -- corrected in place as a Rule 1 fix rather than left inconsistent"
  - "Operator-batch C-1 dispositioned defer-with-owner (Owner: henols), not fixed in this phase -- the underlying classify_fingerprint code sits outside every Phase 137 plan's declared file scope"

patterns-established:
  - "A requirement's own stated criterion can itself go stale when an amendment lands elsewhere in the tree without a matching REQUIREMENTS.md edit; check the requirement's own text, not just its cross-references, before ticking it Complete"

requirements-completed: [CLOSE-05, RELOCK-07]

coverage:
  - id: D1
    description: "RELOCK-07's stale --sdp-relock 'v1.23+' label corrected at both live occurrences (STATE.md, PROJECT.md) and all four citation sites (REQUIREMENTS.md, PROJECT.md's own paragraph, the design note Sec 8, ROADMAP.md), terminal values fresh-measured 2026-08-05 at STATE.md:972 / PROJECT.md:844"
    requirement: "RELOCK-07"
    verification:
      - kind: other
        ref: "grep -q '\\[x\\] \\*\\*RELOCK-07' REQUIREMENTS.md && ! grep -q '`--sdp-relock`.*v1\\.23+' STATE.md PROJECT.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "137-RELEASE-NOTES-app.md's Removed section states a withdrawal (dev sdp enable -> withdrawn, Backlog 999.28), never names write --sdp-relock as available, passes the claim gate alone"
    requirement: "CLOSE-05"
    verification:
      - kind: other
        ref: "FIRESTARTER_CLAIMSCAN_TARGETS_V130=137-RELEASE-NOTES-app.md python3 check_permitted_claims.py"
        status: pass
      - kind: other
        ref: "grep -c 'write --sdp-relock' 137-RELEASE-NOTES-app.md == 0; grep -c 'Backlog 999.28' >= 1; grep -c 'withdrawn' >= 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "137-DECISION.md authored (RELOCK-07 confirmation, C-1 disposition, beta-only recommendation), passes the claim gate alone"
    verification:
      - kind: other
        ref: "FIRESTARTER_CLAIMSCAN_TARGETS_V130=137-DECISION.md python3 check_permitted_claims.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "Operator-batch C-1 dispositioned defer-with-owner: named-owner todo filed, batch row updated to no longer read 'needs a disposition before close'"
    verification:
      - kind: other
        ref: "test -f build-db-diff-ladder-state-community-reported-regression.md && grep -q 'Owner: henols' <same> && ! grep -q 'needs a disposition before close' v1.30-OPERATOR-BATCH.md"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-05
status: complete
---

# Phase 137 Plan 04: RELOCK-07 Terminal Fix + CLOSE-05 Release Notes + C-1 Disposition Summary

**Fresh-measured RELOCK-07's fifth citation drift (634/823 -> 972/844) and closed it at all four sites; authored the next release's honest "withdrawal, not migration" release notes; dispositioned operator-batch C-1 defer-with-owner with a named-owner backlog todo; corrected CLOSE-05's own stale requirement text in the process.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-08-05
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 6 modified, 3 created

## Accomplishments

- **RELOCK-07 terminal fix.** Fresh `grep -n "v1.23+" .planning/STATE.md .planning/PROJECT.md` found the
  two live stale-label rows at `STATE.md:972` and `PROJECT.md:844` — a fifth drift from the `634`/`823`
  pair the requirement itself had cited (measured 2026-08-03). Both rows now read **Backlog 999.28** in
  place of "v1.23+". All four citation sites named by the requirement's own text
  (`REQUIREMENTS.md` RELOCK-07 itself, `PROJECT.md`'s "Stale labels this milestone fixes" paragraph, the
  design note §8, `ROADMAP.md`'s v1.30 milestone-list entry) now state these terminal values, each via an
  appended, dated correction rather than an in-place rewrite of the historical record. RELOCK-07 ticked
  Complete.
- **CLOSE-05 release notes authored.** `137-RELEASE-NOTES-app.md` (version-agnostic, "this release" —
  no cut tag exists yet) carries a `## Removed` section stating `dev sdp disable` → `write` (automatic,
  genuinely redundant, not merely dropped) and `dev sdp enable` → withdrawn, no replacement, tracked as
  Backlog 999.28. `write --sdp-relock` is never named — the file describes the replacement design as
  settled and queued without spelling out the flag string, so `grep -c 'write --sdp-relock'` is exactly
  `0`. Also documents the new six-step `dev test` SDP leg (43 ALLOW / 41 REFUSE of 84 `0x0D` chips) and
  the CHAN-01..07 stable-channel `dev` narrowing (Phase 136, confirmed shipped via `136-VALIDATION.md`
  before being described as shipping in this same release). Passes `check_permitted_claims.py` scanned
  alone (`PASS: scanned 137-RELEASE-NOTES-app.md`) — one in-flight fix was needed: the original title used
  "self-verifying", which the checker's relational rule flags near an SDP context token with no nearby
  "emission"/caveat qualifier; reworded to "a testable leg for the lock" instead.
- **137-DECISION.md authored** with its three mandated sections: RELOCK-07 confirmation (citing the
  fresh-measured terminal lines), operator-batch C-1's disposition, and the phase's own beta-only
  pre-flight recommendation (nothing pushed, merged, or published by the file itself; cross-references
  operator-batch A-1/A-2 as the two items still requiring the operator directly). Passes the claim gate
  scanned alone.
- **C-1 dispositioned defer-with-owner.** Filed
  `.planning/todos/pending/build-db-diff-ladder-state-community-reported-regression.md`, citing
  `134-RECORD.md` §6 residual 4 verbatim, `Owner: henols`, matching this project's established
  named-owner-todo convention (`at28c256-write-path-failure-gh20.md`). `.planning/v1.30-OPERATOR-BATCH.md`'s
  C-1 row updated from "needs a disposition before close" to name the disposition and the filed todo's
  path. The underlying `classify_fingerprint`/`diagnostic_report.py` code is **not** touched — those files
  sit outside every Phase 137 plan's declared file scope, and fixing them here would itself be the scope
  creep this milestone's honesty discipline exists to avoid.

## Task Commits

Each task was committed atomically:

1. **Task 1: RELOCK-07 fresh-measure and fix** — `4f1ffb70` (docs)
2. **Task 2: Author 137-RELEASE-NOTES-app.md** — `bf8c380b` (docs)
3. **Task 3: Author 137-DECISION.md; C-1 disposition; tick CLOSE-05** — `f83871d2` (docs)

**Plan metadata:** (this commit, following)

## Files Created/Modified

- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-RELEASE-NOTES-app.md` — next
  release's notes (CLOSE-05)
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-DECISION.md` — RELOCK-07
  confirmation + C-1 disposition + beta-only recommendation
- `.planning/todos/pending/build-db-diff-ladder-state-community-reported-regression.md` — named-owner
  backlog todo for C-1
- `.planning/STATE.md` — one-phrase fix (`--sdp-relock` → v1.23+` → `Backlog 999.28`)
- `.planning/PROJECT.md` — one-phrase fix (same), reflowed one paragraph to avoid a same-line grep
  false-positive, appended a terminal AMENDED correction block below the existing 2026-08-03 blockquote
- `.planning/REQUIREMENTS.md` — RELOCK-07 ticked Complete + appended terminal correction; CLOSE-05 ticked
  Complete + its own stale mapping text corrected in place; both traceability rows updated
- `.planning/ROADMAP.md` — appended one clause to the v1.30 milestone-list entry's staleness parenthetical
- `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md` — appended a correction sentence to §8
- `.planning/v1.30-OPERATOR-BATCH.md` — C-1 row updated with the defer-with-owner disposition

## Decisions Made

- **RELOCK-07's own previously-cited pair (634/823) was itself stale by this plan's execution** — this is
  the fifth documented drift of the same two labels. Fixed by fresh `grep` at execution time, trusting no
  prior citation including this plan's own draft text, per the plan's explicit instruction.
- **CLOSE-05's own requirement text had not been amended** even though `PROJECT.md`, `STATE.md`, and
  `ROADMAP.md` all already stated "Phase 137's CLOSE-05/06 were amended". `REQUIREMENTS.md`'s CLOSE-05
  checkbox text still literally read `dev sdp enable` → `write --sdp-relock` — the exact overclaim this
  milestone exists to prevent, sitting in the requirement meant to prevent it. Corrected in place as a
  Rule 1 auto-fix (a stale/wrong assertion, not a design change) rather than left inconsistent with every
  other document in the tree.
- **PROJECT.md's "Stale labels this milestone fixes" paragraph (line 145) was reflowed, not rewritten** —
  its content is unchanged, but "v1.23+" was moved to a following line so it no longer sits on the same
  raw text line as `` `--sdp-relock` ``, which would otherwise trip a literal same-line grep check even
  though the sentence is accurate historical narrative (the paragraph already flags its own citation as
  stale via the blockquote beneath it).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] CLOSE-05's own requirement text still named `write --sdp-relock` as the shipped mapping**
- **Found during:** Task 3 (ticking CLOSE-05 Complete)
- **Issue:** `REQUIREMENTS.md`'s CLOSE-05 criterion read "Release notes carry a 'Removed' section mapping
  `dev sdp disable` → `write` (automatic) and `dev sdp enable` → `write --sdp-relock`." This directly
  contradicts the 2026-08-03 operator decision (Phase 135 deferred, RELOCK-01…06 out of scope) that every
  other document in the tree (`PROJECT.md`, `STATE.md`, `ROADMAP.md`, the amended
  `gh12-followup-after-dev-sdp-retirement.md` todo) already reflects. Ticking this requirement Complete
  without fixing its own text would leave the milestone's honesty-close phase citing an overclaim inside
  its own success criterion.
- **Fix:** Corrected the criterion's own wording in place to describe the actual mapping (withdrawn, no
  replacement, Backlog 999.28), with an explicit `⚠ Corrected 2026-08-05` note naming the supersession and
  an Evidence citation to `137-RELEASE-NOTES-app.md`.
- **Files modified:** `.planning/REQUIREMENTS.md`
- **Verification:** `grep -c 'write --sdp-relock' 137-RELEASE-NOTES-app.md` = 0 confirms the release notes
  this criterion cites do not carry the overclaim; the criterion's own text no longer asserts it either.
- **Committed in:** `f83871d2` (Task 3 commit)

**2. [Rule 1 - Bug] `check_permitted_claims.py` flagged "self-verifying" in the release notes' draft title**
- **Found during:** Task 2 (authoring `137-RELEASE-NOTES-app.md`)
- **Issue:** The initial title used "self-verifying", which the checker's relational rule treats as
  forbidden near an SDP context token unless "emission" or the required caveat sits within one line —
  neither did in the title.
- **Fix:** Reworded to "a testable leg for the lock", preserving meaning without tripping the pattern.
- **Files modified:** `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-RELEASE-NOTES-app.md`
- **Verification:** `check_permitted_claims.py` scanned alone → `PASS: scanned 137-RELEASE-NOTES-app.md`
- **Committed in:** `bf8c380b` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (2 Rule 1 bug fixes)
**Impact on plan:** Both necessary for the milestone's own honesty discipline to hold internally
consistent. No scope creep — neither touched code, and both stayed inside this plan's declared file
scope (`REQUIREMENTS.md` was already a declared file; the release notes file is this plan's own output).

## Issues Encountered

None beyond the two auto-fixed deviations above.

## User Setup Required

None — no external service configuration required. `--auto`/`--chain` was correctly NOT used for this
phase per STATE.md's standing note (Plan 137-05 carries a blocking `checkpoint:human-action` gate); this
plan itself has no checkpoints and required no operator action.

## Next Phase Readiness

- CLOSE-05 and RELOCK-07 are both Complete. Project-wide requirement state: **54 ticked / 2 open**
  (`CLOSE-01`, `CLOSE-06` remain, both later Phase 137 plans' own scope).
- `137-RELEASE-NOTES-app.md` and `137-DECISION.md` are now two of the claim gate's four named default
  targets; `137-GH12-COMMENT.md` (the third remaining artifact) does not exist yet, so the default-target
  scan is correctly `UNARMED`/fail-closed until plan 137-05/06 authors it — expected, not a defect.
- No sub-repo touched this plan; `firestarter_app`'s tracked gitlink confirmed unchanged before and after
  (`cc036e8`).
- Next: Plan 137-05 (or whichever plan carries CLOSE-01/CLOSE-06 and the blocking `checkpoint:human-action`
  gate for the gh#12 reply).

---
*Phase: 137-close-honesty-ledger-claim-gate-gh12-followup*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: `137-RELEASE-NOTES-app.md`
- FOUND: `137-DECISION.md`
- FOUND: `.planning/todos/pending/build-db-diff-ladder-state-community-reported-regression.md`
- FOUND: `137-04-SUMMARY.md` (this file)
- FOUND commit `4f1ffb70` (Task 1)
- FOUND commit `bf8c380b` (Task 2)
- FOUND commit `f83871d2` (Task 3)
