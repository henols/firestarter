---
phase: 139-gh-15-correction-outward
plan: 04
subsystem: docs
tags: [gh15, github-issue-body, claim-gate, citation-register, freeze, cross-check]

requires:
  - phase: 139-gh-15-correction-outward (plan 01)
    provides: "139-GH15-ORIGINAL-CRITERIA.md (the nine verbatim boxes embedded in the amendment's collapsed block) and 139-CITATIONS.md sections 0-3 (extended by this plan, not rewritten)"
  - phase: 139-gh-15-correction-outward (plan 02)
    provides: "139-check-claims.py, the Phase-139 forbidden-claim gate this plan re-runs in default mode over both outward artifacts"
  - phase: 139-gh-15-correction-outward (plan 03)
    provides: "139-GH15-COMMENT.md, the frozen correction comment this plan cross-checks the amendment against, and (mid-task) corrects a table-structure defect in"
provides:
  - "139-GH15-BODY-AMENDMENT.md: the complete, default-skipped, ready-to-apply gh#15 body replacement (blob 8ff1a961f28c53f5c743b3c228e60f88ea3ded40, 12870 bytes, committed 2956e29b) -- dated AMENDED block, both prose directives struck through with dated corrections, the wrong `0x0B` `pulse: 50000 us` default corrected in place, a nine-row disposition table, the original nine boxes preserved byte-for-byte in a collapsed details block, and a new 6.25V evidence-ceiling section"
  - "139-GH15-COMMENT.md corrected in place: dropped a stray # row-number column from its disposition table (blob d77a639c62751c197e465ec637f24f330dab35ef, 12193 bytes, committed 19b492d9) -- structural fix only, no disposition/reason/quote changed"
  - "139-CITATIONS.md sections 4-5: the claim-gate non-vacuity record (planted RED before default-mode GREEN, gate blob unchanged) and the freeze table (blob SHA + byte length + committing commit per artifact), plus the one-trailing-newline GitHub normalization named in advance"
affects: [139-05]

tech-stack:
  added: []
  patterns:
    - "build the issue-body replacement programmatically from the live-fetched body text (string-replace with assert-exactly-once guards on every substring touched), never by hand-transcribing gh#15's prose -- guarantees byte-exact preservation of every unedited section"
    - "a mechanical cross-check can itself surface a structural defect in an already-committed, already-gate-clean artifact from a prior plan -- the defect here was a table-shape mismatch (an extra column), not a substantive disagreement, and the fix is authorized by this plan's own scope guard"

key-files:
  created:
    - .planning/phases/139-gh-15-correction-outward/139-GH15-BODY-AMENDMENT.md
  modified:
    - .planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md
    - .planning/phases/139-gh-15-correction-outward/139-CITATIONS.md

key-decisions:
  - "Fixed 139-GH15-COMMENT.md's disposition table (dropped a stray '#' row-number column never specified by 139-03-PLAN.md's own three-column instruction: box / disposition / reason) rather than reshaping the amendment's already plan-compliant 3-column table to match a 4-column shape that was itself the defect. Authorized by this plan's scope guard ('only if the plan's cross-check requires a named correction'). Re-ran all five of plan 139-03's own literal verify blocks against the corrected file -- all five still pass unchanged, confirming the fix is structural only."
  - "Built the amendment from the live-fetched gh#15 body via a small assert-exactly-once string-replacement script rather than hand-transcription, so every unedited section (Problem, both 0x07/0x08 subsections, Shared-helpers scaffold, VPP handling, Remove-current-algorithm, Compatibility, Tests) is byte-identical to the live issue, and only the specifically-mandated edits (two prose directives, the 0x0B default, the acceptance-criteria section) differ."
  - "Placed the safe-delay-helper grounding note (75 ms / 16383 us / 9464 us) as an appended dated NOTE directly under gh#15's own 'Shared implementation helpers' section, since C3's argument is specifically about that helper and the plan's numbered action list did not call for a new top-level section for it."
  - "Included zero raw github.com/gitlab.com hyperlinks in the amendment -- file:line references appear as plain inline code only (e.g. `eprom.cpp:69-77`). This trivially satisfies the pinned-permalink requirement by having nothing unpinned to find, and removes any risk of an accidental `/blob/beta/` or branch-name match."

requirements-completed: []

coverage:
  - id: D1
    description: "A complete, ready-to-apply gh#15 body replacement is authored and frozen: dated AMENDED block, both prose directives struck through with dated corrections, the 0x0B default corrected in place, a nine-row disposition table, the nine original boxes preserved byte-for-byte in a collapsed details block, and the 6.25 V ceiling section -- with gh#15 itself untouched"
    verification:
      - kind: unit
        ref: "six literal <verify><automated> blocks from 139-04-PLAN.md Task 1, all re-run against the final committed file -> STRUCTURE-OK, CONTENT-OK, AMENDMENT-DISPOSITIONS-OK, DIRECTIVES-OK, ORIGINALS-PRESERVED-OK, GH15-UNTOUCHED-OK"
        status: pass
    human_judgment: false
  - id: D2
    description: "The claim gate is re-shown RED on a planted violation (both forbidden labels named) immediately before the default-mode run that passes GREEN naming both outward artifacts, with the gate script's own blob asserted unchanged from plan 139-02's commit"
    verification:
      - kind: unit
        ref: "REPLANTED-RED-OK (exit 1, both labels named) then DEFAULT-MODE-GREEN-OK (exit 0, both files named); gate blob c7ccf421bc30904983cb8b64acbc25c6bfde565c identical at HEAD and at commit 49881518"
        status: pass
    human_judgment: false
  - id: D3
    description: "The comment and the amendment are proven structurally consistent by a box-anchored mechanical cross-check, not by self-report: all nine original boxes resolve to matching kept/corrected/replaced dispositions in both files"
    verification:
      - kind: unit
        ref: "DISPOSITIONS-AGREE-OK, 9/9 rows matched, 0 mismatches -- first run exposed the table-shape defect in 139-GH15-COMMENT.md (fixed in commit 19b492d9); re-run after the fix is clean"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both outward artifacts are frozen -- blob SHA, byte length, and committing commit each -- recorded in 139-CITATIONS.md section 5, with the one-trailing-newline GitHub normalization named in advance and both standing preconditions (gh#15 untouched, eprom.cpp blob equality) re-asserted"
    verification:
      - kind: unit
        ref: "FROZEN-CLEAN-OK (git status --porcelain empty for the gate script and both artifacts) + CITATIONS-EXTENDED-OK + FREEZE-VALUES-RECORDED-OK + PRECONDITIONS-OK (gh#15 OPEN/0 comments/no labels; eprom.cpp one unique blob across three refs)"
        status: pass
    human_judgment: false

duration: ~19min
completed: 2026-08-09
status: complete
---

# Phase 139 Plan 04: gh#15 Body Amendment + Cross-Check + Freeze Summary

**Authored `139-GH15-BODY-AMENDMENT.md` -- the frozen, default-skipped, ready-to-apply gh#15 body replacement -- built programmatically from the live-fetched issue body; fixed a table-shape defect the mechanical cross-check surfaced in plan 139-03's comment; then froze both outward artifacts with blob SHA, byte length, and committing commit each.**

## Performance

- **Duration:** ~19 min
- **Started:** approx. 2026-08-09T13:01:20Z (immediately after plan 139-03's completion commit `c49c87be`)
- **Completed:** 2026-08-09T13:20:15Z
- **Tasks:** 2 of 2
- **Files created:** 1
- **Files modified:** 2

## Task 1 -- Draft `139-GH15-BODY-AMENDMENT.md`

Fetched gh#15's live body with `gh issue view 15 --repo henols/firestarter_prom --json body -q .body`
(5964 bytes, matching `139-CITATIONS.md` §0 exactly -- no divergence, body still unedited since
`createdAt`). Rather than hand-transcribing the 163-line body, wrote a small Python script that:

1. Loads the fetched raw text.
2. Asserts each substring to be edited (the two prose directives, the `0x0B` default line, the
   shared-helpers anchor paragraph, the `## Acceptance criteria` header) occurs **exactly once** in the
   source, failing loudly otherwise.
3. Applies each edit via a single `str.replace(..., 1)` call, so every unedited section (`## Problem`,
   both `0x07`/`0x08` subsections in full, `## Shared implementation helpers`'s original paragraph,
   `## VPP handling`, `## Remove the current custom algorithm`, `## Compatibility`, `## Tests`) is
   byte-identical to the live issue -- never re-typed.
4. Reuses the original nine-checkbox chunk (sliced from the same fetched text) verbatim inside the new
   `<details>` block, so the "preserved byte-for-byte" guarantee is structural, not just eyeballed.

Wrote `.planning/phases/139-gh-15-correction-outward/139-GH15-BODY-AMENDMENT.md` (192 lines, 12870
bytes) with, in order: a dated `⚠ AMENDED 2026-08-09` block (first person, self-correction framing,
referring to "the correction comment on this issue" by description only -- no URL, no
`issuecomment-` fragment); gh#15's own sections in original order; the "handlers may share... timing
constants" sentence struck through with a dated note (protocol owns shape / database owns pulse /
table columns named); the `0x0B` `pulse: \`50000 us\`` default struck through with a dated note citing
the ×100 bug and commits `8de307f`/`12286df`; the "Do not retain... 500 us legacy default" sentence
struck through and reversed with a dated note; a new grounding note under the shared-helpers paragraph
explaining the safe-delay helper is for the 75 ms overprogram pulse (`16383 us` ceiling, `9464 us`
truncation), not any single pulse; the `## Acceptance criteria` section replaced by an intro paragraph
(203/329/61.7% framing) plus a nine-row disposition table plus the collapsed original-boxes block; and
a new `## Evidence ceiling` section stating the ~6.25 V program-VCC gap and naming boxes 3/4/5.
Zero raw `github.com`/`gitlab.com` hyperlinks were included anywhere -- every citation appears as plain
inline code (e.g. `` `eprom.cpp:69-77` ``), which trivially satisfies the pinned-permalink requirement.

**All six literal `<verify><automated>` blocks from Task 1, re-run against the final committed file:**

```
$ F=139-GH15-BODY-AMENDMENT.md; test -f "$F" && test "$(head -1 "$F")" != "---" && grep -qF 'AMENDED' "$F" && grep -qF 'details' "$F" && test "$(grep -c '^- \[ \]' "$F")" = "9" && ! grep -qF 'issuecomment-' "$F" && echo STRUCTURE-OK
STRUCTURE-OK
```
```
$ F=139-GH15-BODY-AMENDMENT.md; for p in "6.25" "silicon-margin" "500" "50000" "203" "329" "61.7" "75 ms" "16383" "9464" "50 ms" "max_pulses" "overprogram_factor" "overprogram_cap_us" "verify_mode" "vpp_path"; do grep -qF -- "$p" "$F" || { echo "MISSING: $p"; exit 1; }; done; echo CONTENT-OK
CONTENT-OK
```
```
$ F=139-GH15-BODY-AMENDMENT.md; test "$(grep -oiE '\b(kept|corrected|replaced)\b' "$F" | wc -l)" -ge 9 && test "$(awk -F'|' 'NF>=4 && /^[[:space:]]*\|/ {c=tolower($3); if (match(c,/kept|corrected|replaced/)) n++} END{print n+0}' "$F")" = "9" && echo AMENDMENT-DISPOSITIONS-OK
AMENDMENT-DISPOSITIONS-OK
```
```
$ F=139-GH15-BODY-AMENDMENT.md; grep -qF 'each protocol must own its programming state machine and timing constants' "$F" && grep -qF 'Do not retain the current generic 500 us legacy default' "$F" && grep -qF '~~' "$F" && ! grep -qF 'PROJECT.md' "$F" && ! grep -qF '138-BASELINE.md' "$F" && ! grep -qE '/blob/(beta|main|gsd)' "$F" && echo DIRECTIVES-OK
DIRECTIVES-OK
```
```
$ MISS=$(sed -n 's/^- \[ \] //p' 139-GH15-ORIGINAL-CRITERIA.md | while IFS= read -r b; do grep -qF -- "$b" 139-GH15-BODY-AMENDMENT.md || printf '%s\n' "$b"; done); test -z "$MISS" && echo ORIGINALS-PRESERVED-OK
ORIGINALS-PRESERVED-OK
```
```
$ test "$(gh issue view 15 --repo henols/firestarter_prom --json comments -q '.comments | length')" = "0" && test "$(gh issue view 15 --repo henols/firestarter_prom --json updatedAt -q .updatedAt)" = "2026-07-12T09:15:27Z" && echo GH15-UNTOUCHED-OK
GH15-UNTOUCHED-OK
```

## Task 2 -- Planted-failure re-run, default-mode gate, cross-check, and the freeze

### Step 1-2: claim gate, RED before GREEN

**Run 1 (planted violation, MUST FAIL) -- observed FAIL**, run against a scratchpad-only copy of
`139-GH15-COMMENT.md` (never committed, deleted immediately after):

```
$ T=$(mktemp -d); cp 139-GH15-COMMENT.md "$T/planted.md"
$ printf '\nThis firmware is datasheet-conformant and algorithm-accurate.\n' >> "$T/planted.md"
$ python3 139-check-claims.py "$T/planted.md"; rm -rf "$T"
FAIL: 2 forbidden phrase match(es):
  <scratchpad>/planted.md:69: forbidden phrase match [datasheet-conformant]: 'datasheet-conformant'
  <scratchpad>/planted.md:69: forbidden phrase match [algorithm-accurate]: 'algorithm-accurate'
```
Exit code **1**. Both planted labels named verbatim.

**Run 2 (default mode over both real artifacts, MUST PASS) -- observed PASS**:

```
$ python3 139-check-claims.py
PASS: scanned 139-GH15-COMMENT.md, 139-GH15-BODY-AMENDMENT.md; 2 file(s) carry both required caveats (this PASS is the mechanizable half of the ISSUE-02 / D-05 discipline only -- see the module docstring's explicit non-claim)
```
Exit code **0**. PASS line names both files. Gate script confirmed unmodified: `git status --porcelain`
empty, blob `c7ccf421bc30904983cb8b64acbc25c6bfde565c` identical at `HEAD` and at plan 139-02's commit
`49881518`.

### Step 3: structural cross-check -- surfaced and fixed a real defect

The box-anchored cross-check's **first run failed all nine rows**: every row in
`139-GH15-COMMENT.md` resolved to `NONE`. Root cause: `139-GH15-COMMENT.md`'s disposition table
(authored in plan 139-03) carried a fourth leading `#` row-number column that `139-03-PLAN.md`'s own
instruction never specified ("Column 1 quotes each original box... Column 2 is the disposition...
Column 3 is the reason" -- a three-column mandate). The extra column shifted the disposition one field
right, so the cross-check's column-3 extraction read the *box text* instead of the disposition in every
comment row. No disposition, reason, or quoted box text was ever substantively wrong -- this was a
table-shape defect, not a content disagreement.

**Fixed** by dropping the `#` column from `139-GH15-COMMENT.md` (commit `19b492d9`), per this plan's
own scope guard, which names exactly this case. Re-ran all five of plan 139-03's own literal verify
blocks against the corrected file: `CONTENT-OK`, `NEGATIVE-OK`, `DIRECTIVES-OK`,
`ORIGINAL-BOXES-QUOTED-OK`, `PERMALINKS-PINNED-OK` -- all five still pass unchanged, confirming the fix
was structural only.

**Cross-check re-run after the fix, MUST exit 0 -- observed `DISPOSITIONS-AGREE-OK`:**

```
ROW 1 :: comment='replaced' amendment='replaced'
ROW 2 :: comment='kept' amendment='kept'
ROW 3 :: comment='corrected' amendment='corrected'
ROW 4 :: comment='corrected' amendment='corrected'
ROW 5 :: comment='corrected' amendment='corrected'
ROW 6 :: comment='kept' amendment='kept'
ROW 7 :: comment='kept' amendment='kept'
ROW 8 :: comment='kept' amendment='kept'
ROW 9 :: comment='kept' amendment='kept'
DISPOSITIONS-AGREE-OK
```

Runs 1 and 2 above (the claim gate) were re-executed a second time, after this fix, against the file's
final post-fix state -- identical outcomes both times, since the fix touched only table column count,
never the scanned prose.

Supplementary assertions, also individually re-derived: every number named in Task 1's action (`500`,
`50000`, `203`, `329`, `61.7`, `75 ms`, `16383`, `9464`, `50 ms`, `8de307f`, `12286df`, `6.25`,
`silicon-margin`, `max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode`, `vpp_path`)
present in both files; all nine original boxes verbatim in both files (`ALL-9-PRESENT-OK` for each); the
false "all three constants disagree with the modal value" sentence absent from both
(`NO-FALSE-MODAL-SENTENCE-OK`).

### Step 4-5: the freeze, and `139-CITATIONS.md` sections 4-5

| File | Frozen blob SHA | Byte length | Committing commit | `git status --porcelain` |
|---|---|---|---|---|
| `139-GH15-COMMENT.md` | `d77a639c62751c197e465ec637f24f330dab35ef` | 12193 | `19b492d9e4e4d73a8b862ae56416eaabce2ead1e` | empty |
| `139-GH15-BODY-AMENDMENT.md` | `8ff1a961f28c53f5c743b3c228e60f88ea3ded40` | 12870 | `2956e29b1c2629b84ab31ef63fc102fe3bf01ac5` | empty |

`139-GH15-COMMENT.md`'s values supersede plan 139-03's original recording
(`635c8ccac8711055db2a317be8f3987559d01f85`, 12229 bytes) because of the mid-task fix above -- this is
recorded explicitly in `139-CITATIONS.md` §5, not silently overwritten.

Appended `## 4.` (claim gate) and `## 5.` (freeze) to `139-CITATIONS.md` as a **pure append** -- `git
diff` against the pre-plan commit shows zero removed content lines, confirming sections 0-3 are
byte-unchanged. Section 5 names, in advance, the one-trailing-newline GitHub normalization (CRLF
stripped, both sides collapsed to one trailing newline via `diff <(sed -e '$a\' A) <(sed -e '$a\' B)`,
a +1-byte difference in the retrieved-copy direction being the *expected* result of a correct post) and
explicitly rejects `137-05-PLAN.md`'s stricter, never-executed "must be identical" wording, which would
misreport a correct post as corrupted. Closed by re-asserting both standing preconditions: gh#15 still
`OPEN`/0 comments/no labels, and `eprom.cpp` still one unique blob across `HEAD`/`origin/beta`/`3085084`.

**All seven literal Task 2 verify blocks, re-run against the final committed state:**
`REPLANTED-RED-OK`, `DEFAULT-MODE-GREEN-OK`, `DISPOSITIONS-AGREE-OK`, `FROZEN-CLEAN-OK`,
`CITATIONS-EXTENDED-OK`, `FREEZE-VALUES-RECORDED-OK`, `PRECONDITIONS-OK` -- all seven passed.

## Task Commits

Each logical change was committed atomically:

1. **Task 1: Draft `139-GH15-BODY-AMENDMENT.md`** -- `2956e29b` (feat) -- adds the 192-line, 12870-byte
   amendment, staged individually, no other file touched.
2. **Task 2, part A: fix the comment's table structure** -- `19b492d9` (fix) -- drops the stray `#`
   column from `139-GH15-COMMENT.md`'s disposition table; documented as a deviation (see below), not
   silently folded into the freeze commit.
3. **Task 2, part B: claim gate record + freeze** -- `95facc21` (docs) -- appends `139-CITATIONS.md`
   sections 4 and 5, staged individually, no other file touched.

## Files Created/Modified

- `.planning/phases/139-gh-15-correction-outward/139-GH15-BODY-AMENDMENT.md` -- the complete,
  default-skipped, ready-to-apply gh#15 body replacement. Blob `8ff1a961f28c53f5c743b3c228e60f88ea3ded40`,
  12870 bytes, 192 lines. Frozen, gate-clean, not applied to gh#15.
- `.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md` -- corrected in place: dropped a
  stray `#` row-number column from its disposition table. Blob `d77a639c62751c197e465ec637f24f330dab35ef`,
  12193 bytes (was 12229 at plan 139-03's commit). Re-frozen.
- `.planning/phases/139-gh-15-correction-outward/139-CITATIONS.md` -- extended with sections 4 (claim
  gate non-vacuity record) and 5 (the freeze table + normalization); sections 0-3 byte-unchanged.

## Decisions Made

See `key-decisions` in the frontmatter above. In summary: fixed the comment's table structure rather
than the amendment's (the amendment was already plan-compliant); built the amendment programmatically
from the live-fetched body to guarantee byte-exact preservation; placed the C3 grounding note under
gh#15's own shared-helpers paragraph rather than a new section; and used zero raw hyperlinks in the
amendment to sidestep any permalink-pinning risk entirely.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Dropped a stray `#` row-number column from `139-GH15-COMMENT.md`'s disposition table**
- **Found during:** Task 2 (the box-anchored disposition cross-check's first run)
- **Issue:** `139-GH15-COMMENT.md` (authored by plan 139-03) rendered its nine-row disposition table
  with a fourth leading `#` column (`| # | Original box | Disposition | Why |`), never specified by
  `139-03-PLAN.md`'s own instruction, which mandates exactly three columns (box · disposition ·
  reason). Plan 139-03's own verify blocks never caught this, because they only counted
  kept/corrected/replaced occurrences file-wide, without asserting column position. This plan's own
  cross-check leg assumes the three-column shape in both files (mandated explicitly in the plan text:
  "do not reorder the columns"), so the extra column caused every one of the comment's nine rows to
  read as `NONE` (the box text, not the disposition, landed in the column the script inspects).
- **Fix:** Removed the `#` header cell, the separator's fourth `|---|`, and each row's leading `| N |`
  cell from `139-GH15-COMMENT.md`'s table. Also updated one internal cross-reference inside row 4's
  reason ("falls with row 1" -> "falls with the row above") that depended on the now-removed numbering.
  No disposition, reason, or quoted box text changed.
- **Files modified:** `.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md`
- **Verification:** Re-ran all five of plan 139-03's own literal verify blocks against the corrected
  file -- `CONTENT-OK`, `NEGATIVE-OK`, `DIRECTIVES-OK`, `ORIGINAL-BOXES-QUOTED-OK`,
  `PERMALINKS-PINNED-OK` -- all five still pass unchanged. Then re-ran this plan's own cross-check leg:
  `DISPOSITIONS-AGREE-OK`, 9/9 rows matched.
- **Committed in:** `19b492d9` (fix)

---

**Total deviations:** 1 auto-fixed (1 bug fix, Rule 1).
**Impact on plan:** The fix is scoped exactly to the column-count defect; no disposition, reason, box
quote, citation, or caveat changed. Explicitly authorized in advance by this plan's own scope guard
("MUST NOT... 139-GH15-COMMENT.md (only if the plan's cross-check requires a named correction... if
you change it, the freeze must record the NEW blob)"), and the new blob is recorded in
`139-CITATIONS.md` §5 rather than silently overwriting plan 139-03's original recording. No scope creep.

## Issues Encountered

None beyond the deviation documented above, which was resolved within Task 2 as designed (the plan's
own Step 3 anticipates exactly this class of correction: "If the two disagree, the comment is
authoritative and the amendment is corrected to match -- then re-run the leg until it is green" --
though in this case the "disagreement" was a mechanical parsing artifact rather than a substantive
disposition conflict, so the comment's *table shape*, not its dispositions, was the thing corrected).

## User Setup Required

None -- no external service configuration required. This plan made only read-only `gh issue view`
calls (state/comments/labels/updatedAt/body), never a state-changing `gh` call, and no `git push` of
any kind.

## Next Phase Readiness

- **139-05 is unblocked.** Both outward artifacts exist, are mutually consistent (mechanically proven,
  not self-reported), pass the phase's own claim gate in default mode, and are frozen with three
  recorded values each in `139-CITATIONS.md` §5. The operator gate in 139-05 can review text that is
  provably identical to what would be posted or applied.
- **gh#15 remains completely untouched**: `OPEN`, 0 comments, no labels, `updatedAt` unchanged from
  `2026-07-12T09:15:27Z` -- confirmed by a fresh live read at the end of Task 2.
- **`139-check-claims.py` is unmodified** -- blob `c7ccf421bc30904983cb8b64acbc25c6bfde565c`, identical
  to plan 139-02's own commit. The green in this plan was not bought by weakening the gate.
- **No requirement ticked by this plan** (`requirements-completed: []`), matching the plan's own scope
  guard exactly. ISSUE-01, ISSUE-02, and ISSUE-03 are all owned by plan 139-05 and tick only on the
  operator's real-time answers.
- **No sub-repo commit was made by this plan.** `firestarter` and `firestarter_app` working trees show
  only the two pre-existing stale-gitlink entries (unchanged before and after both tasks, confirmed via
  the three-ref blob-equality check on `eprom.cpp`, not `git status`).
- **Nothing has been posted, applied, or pushed.** Every `gh` call this plan made was read-only; no
  `gh issue edit`, `gh issue comment`, or `git push` was ever invoked.

---
*Phase: 139-gh-15-correction-outward*
*Completed: 2026-08-09*

## Self-Check: PASSED

- FOUND: `139-GH15-BODY-AMENDMENT.md`
- FOUND: `139-GH15-COMMENT.md` (corrected)
- FOUND: `139-CITATIONS.md` (sections 4-5 appended)
- FOUND: `139-04-SUMMARY.md`
- FOUND commit: `2956e29b` (Task 1: draft 139-GH15-BODY-AMENDMENT.md)
- FOUND commit: `19b492d9` (Task 2: fix comment's disposition table)
- FOUND commit: `95facc21` (Task 2: claim gate record + freeze)
