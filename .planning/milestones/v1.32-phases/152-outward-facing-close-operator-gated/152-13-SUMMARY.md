---
phase: 152-outward-facing-close-operator-gated
plan: 13
subsystem: testing
tags: [claim-gate, regex, fail-closed, operator-gate, pytest]

requires:
  - phase: 152-outward-facing-close-operator-gated
    provides: "152-01's claim contract and pre-populated _CAVEAT_RULES map; 152-02's paired suite and 30-leg baseline; 152-08/09/12's authored release-note bodies and comment drafts; 152-12's beta-merge and tag substitution"
provides:
  - "152-check-claims.py armed at seven real outward artifacts (previously one), with the arming leg strengthened to a literal membership assertion"
  - "152-check-not-auto.py, the fail-closed configuration guard the five posting plans run first"
  - "A fixed verified-on-silicon forbidden-pattern row (word-boundary defect found and closed in this plan)"
  - "The extended-target-list transcript section: armed RED against the specified plant, defaults GREEN over all seven, the re-run suite count, and two recorded design decisions"
affects: [152-14, 152-15, 152-16, 152-17, 152-18, 152-19, 152-20]

tech-stack:
  added: []
  patterns:
    - "_DEFAULT_TARGETS ordering trap: an entry may only be added once its artifact exists on disk"
    - "basename-keyed caveat lookup with a fail-closed default to the full caveat set"
    - "fail-closed configuration guard: every uncertain read path (missing file, parse error, absent key) is a non-zero exit, never a silent pass"

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-check-not-auto.py
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/config_auto_active.json
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/config_auto_inactive.json
  modified:
    - .planning/phases/152-outward-facing-close-operator-gated/152-check-claims.py
    - .planning/phases/152-outward-facing-close-operator-gated/test_check_claims_152.py
    - .planning/phases/152-outward-facing-close-operator-gated/152-CLAIM-GATE-TRANSCRIPTS.md

key-decisions:
  - "152-LEDGER.md, named as a candidate target in early research, was never authored as a separate file — its intended content folded into 152-MERGE-RECORD.md — so the armed list has exactly seven entries, not eight, and _CAVEAT_RULES carries no live entry for it."
  - "A fourth required-caveat row to enforce the withdrawn re-lock command's presence half of criterion 4 was considered and rejected: the fail-closed default would force that literal command string into every fixture and every scanned artifact, including the three comment drafts that never mention it. Presence stays a positive grep in the posting plans; word order stays the gate's job."
  - "The verified-on-silicon row's missing word boundary (found empirically, not from the plan's task list) was fixed with a fixed-width negative lookbehind, because the plan's own files_modified already covered both files touched and a paired both-directions test leg closes the risk of the fix becoming a hole."

patterns-established:
  - "Pattern: a configuration guard proves what it reads, not what writes to it — 152-check-not-auto.py's docstring states its own limit explicitly rather than implying a guarantee the write path was never measured to support."

requirements-completed: [OUT-05]

duration: 25min
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 13: Arm the Claim Gate at Real Artifacts, Add the Auto-Chain Guard Summary

**Extended `152-check-claims.py`'s `_DEFAULT_TARGETS` from one entry to seven real outward artifacts, re-proved the gate RED against the specified plant while so armed, closed a live false-positive in an inherited forbidden-pattern row, and shipped `152-check-not-auto.py` as the fail-closed guard the five posting plans run first.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-21T17:37:16Z
- **Tasks:** 3
- **Files:** 3 created (`152-check-not-auto.py` + 2 fixtures), 3 modified

## Accomplishments

- `152-check-claims.py`'s `_DEFAULT_TARGETS` extended from `["152-CLAIM-CLASSES.md"]` to seven
  entries: `152-CLAIM-CLASSES.md`, `152-GH12-COMMENT.md`, `152-GH21-COMMENT.md`,
  `152-GH11-COMMENT.md`, `152-RELEASE-NOTES-app.md`, `152-RELEASE-NOTES-fw.md`,
  `152-MERGE-RECORD.md`. `152-LEDGER.md` is correctly absent — see Decisions.
- The gate, invoked with no argv and no env seam, exits 0 over all seven:
  ```
  PASS: scanned 152-CLAIM-CLASSES.md, 152-GH12-COMMENT.md, 152-GH21-COMMENT.md, 152-GH11-COMMENT.md, 152-RELEASE-NOTES-app.md, 152-RELEASE-NOTES-fw.md, 152-MERGE-RECORD.md; 6 of 6 caveat-required file(s) carry every caveat their own rule demands; 1 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
  ```
- The arming leg (`test_armed_against_the_real_152_artifacts`) is strengthened with a literal
  membership assertion over all seven expected basenames, plus an explicit `len(...) == 7` check —
  a silent omission now fails the suite instead of passing on a shorter list.
- The gate was re-demonstrated RED while armed at the real seven-target list, with the roadmap's
  pre-amendment criterion-1 plant (`fixtures/planted_sdp_relock_as_shipped.md`) appended via the env
  seam. It failed for exactly one reason — the appended plant, attributed to its own
  `sdp-relock-as-shipped` label alone — while the six real artifacts scanned clean. The literal
  pasted command and output are recorded in `152-CLAIM-GATE-TRANSCRIPTS.md`'s "Extended target list
  (Plan 152-13)" section, not reproduced here, since that transcript file is the one place in this
  phase permitted to quote the plant's forbidden text as evidence and this SUMMARY is not.
- `152-check-not-auto.py` built and demonstrated in all four directions with real subprocess exit
  codes: truthy fixture → non-zero, naming the key; falsy fixture → zero; nonexistent config path →
  non-zero; the live repository configuration → zero (the key currently reads `False`). The guard's
  own docstring states plainly what it does not establish: it is a real control over a real read, not
  proof that an auto or chained run cannot reach a public post through some other path this project
  has not measured.
- A live false-positive was found and closed: the inherited `verified-on-silicon` forbidden-pattern
  row had no leading word boundary, so it rejected the non-claim that a protocol *remains*
  UNVERIFIED on silicon — the exact opposite of the claim the row exists to catch. Fixed with a
  fixed-width negative lookbehind ahead of the word the row is built on, paired with a new
  both-directions test leg proving the non-claim is now permitted while the actual forbidden
  phrasing is still rejected. Nothing shipped in this phase before the fix ever hit this pattern —
  this milestone's canonical caveat wording always phrases the non-claim as staying unverified *in
  PROTOCOL-LEDGER*, never *on silicon* — so this closes a latent trap rather than an active break.
- The paired suite grew from 30 to 34 legs (3 new guard legs selectable by `-k not_auto`, 1 new leg
  for the word-boundary fix) and is fully green:
  ```
  34 passed in 1.15s
  ```
- The transcript's "Extended target list (Plan 152-13)" section records the armed RED, the defaults
  GREEN with all seven artifacts named, the re-run suite count, the false-positive reproduction and
  fix, a "withdrawal-presence check" subsection recording why a fourth required-caveat row was
  considered and rejected, and a "Posted mode" subsection recording the basename rule the five
  posting plans depend on. The "Final target list" section is untouched, still a stub for Plan
  152-20.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend `_DEFAULT_TARGETS` to the seven real artifacts and strengthen the arming leg** —
   `973eeb2b` (feat) — also includes the `verified-on-silicon` fix and its paired test leg, since
   both touched the same two files this task already had open.
2. **Task 2: Build `152-check-not-auto.py`** — `bfee443c` (feat)
3. **Task 3: Extend the transcript** — `c1cc6ed4` (docs)

No separate plan-metadata commit — this plan's orchestrator owns STATE.md/ROADMAP.md writes after
the wave completes, per this plan's own instructions.

## Files Created/Modified

- `.planning/phases/152-outward-facing-close-operator-gated/152-check-claims.py` — `_DEFAULT_TARGETS`
  extended to seven entries; posted-mode basename rule recorded as a comment; `verified-on-silicon`
  row's word-boundary fix
- `.planning/phases/152-outward-facing-close-operator-gated/test_check_claims_152.py` — arming leg
  strengthened with a membership assertion; three new guard legs (`-k not_auto`); one new leg for the
  word-boundary fix (34 legs total, up from 30)
- `.planning/phases/152-outward-facing-close-operator-gated/152-check-not-auto.py` — new, the
  fail-closed configuration guard
- `.planning/phases/152-outward-facing-close-operator-gated/fixtures/config_auto_active.json` — new,
  truthy fixture
- `.planning/phases/152-outward-facing-close-operator-gated/fixtures/config_auto_inactive.json` —
  new, falsy fixture
- `.planning/phases/152-outward-facing-close-operator-gated/152-CLAIM-GATE-TRANSCRIPTS.md` — extended
  target list section filled in; two new design-decision subsections; final target list section
  untouched

## Decisions Made

- **`152-LEDGER.md` stays absent.** Early research named it as target #6, but this phase's actual
  execution folded its intended content into `152-MERGE-RECORD.md` and never authored it as a
  separate file. The armed list has exactly the seven artifacts that exist on disk today, matching
  this plan's own prohibition against adding any entry absent from disk.
- **The withdrawal-presence half of criterion 4 stays outside the gate.** A fourth required-caveat
  row was considered, to enforce that both release-note bodies name the withdrawn command, the same
  way the three existing rows enforce the ledger qualifiers. Rejected because the fail-closed default
  in `_required_caveats_for()` would then demand that exact command string from every scanned
  artifact with no rule of its own — including the three comment drafts, which never discuss SDP
  relock. The presence half is enforced by a positive grep in the posting plans instead (152-08,
  152-09, 152-12 already; 152-17/18 re-verify against the posted bodies); the word-order half stays
  the gate's job everywhere. Recorded in the transcript's new "withdrawal-presence check" subsection.
- **The `verified-on-silicon` fix was made in-plan rather than deferred.** The files it touches
  (`152-check-claims.py`, `test_check_claims_152.py`) were already open for Task 1's own edits, the
  fix is a single fixed-width lookbehind with a clear, testable specification, and a paired
  both-directions leg closes the risk of the fix silently widening into a hole. Deferring it would
  have left a live trap for any future outward text stating the honest non-claim in ordinary English.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed the `verified-on-silicon` row's missing word boundary**
- **Found during:** Task 1, while considering the candidate strengthening flagged ahead of execution
- **Issue:** The row's regex had no leading word boundary, so it matched the non-claim that a
  protocol remains unverified on silicon — the opposite of the claim the row exists to reject.
  Reproduced against a throwaway probe file before the fix.
- **Fix:** Added a fixed-width negative lookbehind immediately ahead of the row's key word (Python's
  `re` requires fixed-width lookbehinds), so the row no longer fires when that word is immediately
  preceded by its own two-letter negating prefix.
- **Files modified:** `152-check-claims.py` (the row's pattern and its explanatory comment),
  `test_check_claims_152.py` (one new both-directions leg)
- **Verification:** New leg passes; full suite green at 34/34; the gate still exits 0 over the real
  default targets after the change.
- **Committed in:** `973eeb2b` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** The fix closes a latent trap for future outward text without touching any of the
plan's three stated tasks' own deliverables; no scope creep into files this plan did not already own.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The gate is armed at every real outward artifact this phase has written so far and has been seen
  to reject the specified plant while so armed. `152-check-not-auto.py` exists and is demonstrated in
  all four directions.
- Plans 152-14 through 152-18 (the five public posts) can now run `152-check-not-auto.py` first, and
  should write any posted-mode re-verification temp file under the same basename as the draft it
  verifies, per the rule recorded in this plan's transcript section.
- Plan 152-20 still owns adding the phase's own `152-NN-SUMMARY.md` files to `_DEFAULT_TARGETS`, plus
  filling in the transcript's "Final target list" section — both untouched by this plan, as required.
- This SUMMARY was written to satisfy `152-check-claims.py`'s own scan when it becomes a target in
  Plan 152-20: it carries the mandated software-proven/unvalidated-on-silicon qualifier verbatim and
  avoids every forbidden pattern's vocabulary, citing labels only where citing them does not itself
  trip the row it names.

This ships software-proven and unvalidated on silicon.

---
*Phase: 152-outward-facing-close-operator-gated*
*Completed: 2026-08-21*

## Self-Check: PASSED

All six files created/modified by this plan confirmed present on disk; all three task commit hashes
(`973eeb2b`, `bfee443c`, `c1cc6ed4`) confirmed present in git log. The gate's own scan of this
SUMMARY, run via the env seam before this note was appended, exited 0.
