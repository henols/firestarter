---
phase: 139-gh-15-correction-outward
plan: 03
subsystem: docs
tags: [gh15, github-comment, claim-gate, citation-register, pulse-width, correction]

requires:
  - phase: 139-gh-15-correction-outward (plan 01)
    provides: "139-CITATIONS.md (pinned SHAs, content-verified anchors) and 139-GH15-ORIGINAL-CRITERIA.md (the nine verbatim boxes) this comment quotes from"
  - phase: 139-gh-15-correction-outward (plan 02)
    provides: "139-check-claims.py, the Phase-139 forbidden-claim gate this plan's Task 2 runs in argv mode"
provides:
  - "139-GH15-COMMENT.md: the gh#15 correction comment body, byte for byte (blob 635c8ccac8711055db2a317be8f3987559d01f85, 12229 bytes, committed 291efa15) -- C1/C2/C3, the ~6.25V ceiling paragraph, a nine-row acceptance-criteria amendment table quoting every original box verbatim, the proposed design shape, and one community ask -- gate-clean, committed, not yet frozen (139-04 freezes it)"
affects: [139-04, 139-05]

tech-stack:
  added: []
  patterns:
    - "quote the payload inline (three histogram lines), link the full evidence one click away -- a correction that buries its own check in a 200-line dump defeats the point of citing it"
    - "the honest wrong-width-count framing (203/329, 61.7%) survives a skeptical reader's own arithmetic; the false modal-disagreement framing does not, and was rejected by name per the plan's own scope guard"

key-files:
  created:
    - .planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md
  modified: []

key-decisions:
  - "Named the eprom.cpp/memory.cpp pulse_delay double-duty observation (C3) in prose without a line-number link to the erase function at all, rather than citing eprom.cpp:274-283 and relying on the range not matching the forbidden 'eprom.cpp#L283' substring check -- the plan's action text made this citation optional ('may note'), and skipping it entirely removes any risk from that negative assertion rather than merely satisfying it narrowly."
  - "Drafted, then removed, a bare unpinned https://gitlab.com/DavidGriffith/minipro mention -- a link with no commit SHA would have failed the permalink-pinning verify leg. The required literal substring 'gitlab.com/DavidGriffith/minipro' is already supplied by the pinned t48.c/main.c blob links, so the bare mention was redundant as well as unsafe."
  - "Section order (self-correction opener -> C1 -> C2 -> C3 -> 6.25V ceiling -> proposed design shape -> nine-row amendment + two directives -> one ask) follows gh#15's own reading order -- the numeric corrections first, then the architecture criterion they justify amending -- rather than 137-GH12-COMMENT.md's exact four-movement order, since CONTEXT.md leaves section order to Claude's discretion."
  - "The acceptance-criteria table's 'Why' column reasons are scoped tightly to the plan's own named dispositions (action text lines 196-211) rather than embellished, so the table stays a faithful rendering of D-03's item-for-item mapping rather than new editorializing not present in the plan or PROJECT.md's locked record."

requirements-completed: []

coverage:
  - id: D1
    description: "The comment carries every C1/C2/C3 evidentiary token with permalinks pinned to commit SHAs (never branch names), plus every required negative assertion: no false modal-disagreement sentence, no eprom.cpp:283 program-pulse misattribution, no PROJECT.md/138-BASELINE.md citation, no branch-name permalink"
    requirement: "ISSUE-01"
    verification:
      - kind: unit
        ref: "two literal <verify><automated> blocks from 139-03-PLAN.md Task 1, run verbatim -> CONTENT-OK, NEGATIVE-OK; plus PERMALINKS-PINNED-OK (every github.com/gitlab.com link other than the issue URL embeds a 7-40 hex commit SHA)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The ~6.25V program-VCC ceiling is stated in its own paragraph (not a footnote), and a nine-row acceptance-criteria amendment table maps item-for-item onto all nine of gh#15's original boxes (quoted verbatim from 139-GH15-ORIGINAL-CRITERIA.md), plus both non-checkbox prose directives quoted verbatim"
    requirement: "ISSUE-02"
    verification:
      - kind: unit
        ref: "DIRECTIVES-OK (both prose directives quoted verbatim) and ORIGINAL-BOXES-QUOTED-OK (all nine original boxes found verbatim via the plan's own sed/grep loop against 139-GH15-ORIGINAL-CRITERIA.md)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The comment passes the phase's own claim gate in argv mode on the first attempt (no wording fix needed), the gate's own blob SHA is unchanged from plan 139-02's commit, and gh#15 (OPEN, 0 comments, no labels) plus eprom.cpp's three-ref blob equality are both re-confirmed unchanged"
    requirement: "ISSUE-01 (mechanizable half), ISSUE-02 (mechanizable half)"
    verification:
      - kind: unit
        ref: "GATE-GREEN-OK (python3 139-check-claims.py 139-GH15-COMMENT.md exits 0) + GATE-UNMODIFIED-OK (git status clean on the gate script; blob SHA c7ccf421bc30904983cb8b64acbc25c6bfde565c identical at HEAD and at commit 49881518) + PRECONDITIONS-STILL-OK"
        status: pass
    human_judgment: false

duration: ~23min
completed: 2026-08-09
status: complete
---

# Phase 139 Plan 03: gh#15 Correction Comment Summary

**Drafted `139-GH15-COMMENT.md` -- the byte-for-byte gh#15 correction comment carrying C1/C2/C3, the ~6.25V ceiling as its own paragraph, and a nine-row acceptance-criteria amendment quoting every original box verbatim -- and it passed the phase's own claim gate clean on the first attempt.**

## Performance

- **Duration:** ~23 min
- **Started:** approx. 2026-08-09T12:32Z (immediately after plan 139-02's completion commit `179364d7`)
- **Completed:** 2026-08-09T12:55:07Z
- **Tasks:** 2 of 2
- **Files created:** 1

## Task 1 -- Draft 139-GH15-COMMENT.md

Wrote `.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md` (67 lines, 12229 bytes) as
the literal comment body -- no YAML frontmatter, no title heading, no footer, bold-paragraph headings
only (`**...**`, never `##`), voice carried forward from `137-GH12-COMMENT.md` per D-02 (first person,
plain-spoken, framed explicitly as self-correction: "I filed this issue, and on a closer look, two of
its numbers are wrong and one of its premises is inverted").

Content, in the order it appears:

- **C1** -- states `0x0B`'s pulse is 500 microseconds, not `50000 us`; names the ×100
  `interpret_timing()` multiplier as the fingerprint (`50000 = 500 × 100`), cites both removal commits
  by SHA (`8de307f`, `12286df`) and the adjudication at `doc/infoic-field-dictionary.md#L210-L217`;
  carries both cross-checks (`AT28C64B` 10000 us / `DS1225` 1 us) and the firmware-already-defaults-to-500
  corroboration at `eprom.cpp:69-77`.
- **C2** -- states pulse width is a database datum, not a per-protocol constant; quotes all three
  histogram lines inline verbatim (`n = 170`/`127`/`32`) with the honest **203/329 (61.7%)**
  wrong-width framing -- explicitly NOT the false "all three constants disagree with the modal value"
  sentence the plan's own scope guard forbids (verified absent by the NEGATIVE-OK grep leg below).
  Links the full distribution and the runnable script as meta permalinks; cites `_parse_pulse_duration`
  and minipro's two-orthogonal-wire-fields precedent on GitLab (`t48.c:255`, `t48.c:266-267`,
  `main.c:698`), all pinned to `cae74c0607077d6260b24995f5e4c0d0b66a6a2e`.
- **C3** -- states the 32-bit-safe delay helper is for the 75 ms overprogram pulse
  (`3 × 25 × 1000 us`, built from gh#15's own defaults), gives the AVR truncation argument in its strong
  form (`75000 - 65536 = 9464 us`, a silent 12.5% pulse), and cites the program pulse at
  `memory.cpp:321-330` inside `memory_set_data()` -- never `eprom.cpp:283`. One sentence notes
  `handle->pulse_delay`'s double duty as both program and erase pulse, without a line-number citation to
  the erase function at all (see Decisions Made).
- **The ~6.25V ceiling** -- its own paragraph, framed as a limit on any implementation of gh#15 on this
  shield, naming boxes 3/4/5 as the ones it makes datasheet-algorithm fidelity unreachable for.
- **The proposed design shape** -- the five-column table shape (`max_pulses`, `overprogram_factor`,
  `overprogram_cap_us`, `verify_mode`, `vpp_path`), the no-pulse-column rule, `pulse_delay == 0`
  fallbacks, the `0x0B` 50 ms accumulated-energy cap with no overpulse, and hard-fail-on-max-pulses --
  every numeric row marked **proposed**.
- **The nine-row amendment table** -- one row per original gh#15 box, quoted verbatim in column 1,
  disposition (kept/corrected/replaced) in column 2, reason in column 3, followed by both non-checkbox
  prose directives quoted verbatim with their own dispositions (replaced; reversed).
- **The ask** -- names the `0x0B` one-shot-vs-looped question as reasoned, not derived (minipro packs
  `pulse_delay` into a `BEGIN_TRANS` message for closed firmware and never runs the algorithm), names
  `M2716`/`M2732`/`AM27C020` as the bench-coverage gap, and mentions the proposed (not yet built)
  `--pulse-us` override.

**Verify blocks run (all five from the plan's literal `<verify>` section, executed verbatim):**

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && F=139-GH15-COMMENT.md && test -f "$F" && test "$(head -1 "$F")" != "---" && test "$(grep -c '^#' "$F")" = "0" && for p in "500" "50000" "8de307f" "12286df" "infoic-field-dictionary.md" "#L210-L217" "n = 170" "n = 127" "n = 32" "203" "329" "61.7" "138-02-PULSE-DISTRIBUTION.md" "138-pulse-distribution.py" "_parse_pulse_duration" "gitlab.com/DavidGriffith/minipro" "memory.cpp" "memory_set_data" "75 ms" "16383" "9464" "6.25" "silicon-margin" "max_pulses" "overprogram_factor" "overprogram_cap_us" "verify_mode" "vpp_path" "pulse_delay == 0" "50 ms" "proposed" "M2716" "M2732" "AM27C020"; do grep -qF -- "$p" "$F" || { echo "MISSING: $p"; exit 1; }; done && echo CONTENT-OK
CONTENT-OK
```

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && F=139-GH15-COMMENT.md && ! grep -qiE 'all three.*disagree.*modal' "$F" && ! grep -qF 'eprom.cpp#L283' "$F" && ! grep -qF 'PROJECT.md' "$F" && ! grep -qF '138-BASELINE.md' "$F" && ! grep -qE '/blob/(beta|main|gsd)' "$F" && test "$(grep -oiE '\b(kept|corrected|replaced)\b' "$F" | wc -l)" -ge 9 && echo NEGATIVE-OK
NEGATIVE-OK
```

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && grep -qF 'each protocol must own its programming state machine and timing constants' 139-GH15-COMMENT.md && grep -qF 'Do not retain the current generic 500 us legacy default' 139-GH15-COMMENT.md && echo DIRECTIVES-OK
DIRECTIVES-OK
```

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && MISS=$(sed -n 's/^- \[ \] //p' 139-GH15-ORIGINAL-CRITERIA.md | while IFS= read -r b; do grep -qF -- "${b%.}" 139-GH15-COMMENT.md || printf '%s\n' "$b"; done) && test -z "$MISS" && echo ORIGINAL-BOXES-QUOTED-OK || { echo "NOT QUOTED VERBATIM:"; printf '%s\n' "$MISS"; exit 1; }
ORIGINAL-BOXES-QUOTED-OK
```

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && BAD=$(grep -oE 'https://(github|gitlab)\.com/[^ )>"]+' 139-GH15-COMMENT.md | grep -v '/issues/' | grep -vE '/(blob|raw|commit|commits)/[0-9a-f]{7,40}' || true) && test -z "$BAD" && echo PERMALINKS-PINNED-OK || { echo "UNPINNED LINKS:"; printf '%s\n' "$BAD"; exit 1; }
PERMALINKS-PINNED-OK
```

Plus the sub-repo discipline check: `git status --porcelain -- firestarter firestarter_app` showed only
the two pre-existing stale-gitlink ` M ` entries (unchanged from every prior plan in this phase).

## Task 2 -- Run the claim gate against the comment and record the result

## Claim gate

Ran the gate in argv mode, exactly as the plan's `<action>` specifies (default mode is not used here,
since `139-GH15-BODY-AMENDMENT.md` does not exist yet and would correctly fail closed on a missing
target):

**Literal command:**
```
cd /workspaces/.planning/phases/139-gh-15-correction-outward && python3 139-check-claims.py 139-GH15-COMMENT.md
```

**Literal stdout:**
```
PASS: scanned 139-GH15-COMMENT.md; 1 file(s) carry both required caveats (this PASS is the mechanizable half of the ISSUE-02 / D-05 discipline only -- see the module docstring's explicit non-claim)
```

**Exit code: 0.**

**No wording change was needed.** The gate passed on the first attempt against the comment as drafted
in Task 1 -- no forbidden phrase, both required caveats (`6.25 V`, `silicon-margin`) present. There is
therefore no before/after wording pair to record.

**This green is licensed by plan 139-02's recorded Run 1 red.** `139-02-SUMMARY.md` §"Claim gate --
non-vacuity record" shows this identical gate script observed **FAIL** (exit 1, four named forbidden-phrase
matches) against a planted violation, before any pass was relied on. That non-vacuity proof precedes and
licenses this plan's pass; a gate that had only ever passed would not be trusted here.

**The gate's own blob is unmodified**, confirmed two ways:
```
$ test -z "$(git status --porcelain -- .planning/phases/139-gh-15-correction-outward/139-check-claims.py)" && echo GATE-UNMODIFIED-OK
GATE-UNMODIFIED-OK
$ git rev-parse HEAD:.planning/phases/139-gh-15-correction-outward/139-check-claims.py
c7ccf421bc30904983cb8b64acbc25c6bfde565c
$ git rev-parse 49881518:.planning/phases/139-gh-15-correction-outward/139-check-claims.py
c7ccf421bc30904983cb8b64acbc25c6bfde565c
```
Identical blob SHA (`c7ccf421bc30904983cb8b64acbc25c6bfde565c`) at `HEAD` and at plan 139-02's own
commit `49881518` -- this green cannot have been bought by weakening the gate.

**Preconditions re-asserted, both still holding:**
```
$ gh issue view 15 --repo henols/firestarter_prom --json state,comments,labels -q '{state:.state,n:(.comments|length),labels:.labels}'
{"labels":[],"n":0,"state":"OPEN"}
```
gh#15 is still `OPEN`, still zero comments, still no labels -- unchanged from plan 139-01's §0
measurement.
```
$ for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/eprom.cpp; done | sort -u | wc -l
1
```
`eprom.cpp` is still exactly one unique blob SHA across all three refs -- unchanged from plan 139-01's
D-10 baseline. No implementation has moved underneath this draft.

All Task 1 content assertions were re-confirmed passing (they were not re-run after Task 2, since no
wording changed -- the same five verify blocks recorded under Task 1 above are the current, final
state of the file).

## Task Commits

1. **Task 1: Draft 139-GH15-COMMENT.md** -- `291efa15` (feat) -- adds the 67-line, 12229-byte comment
   body, staged individually (`git add .planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md`),
   no other file touched.
2. **Task 2: Run the claim gate** -- no additional commit. The gate passed on the first attempt against
   the file committed in Task 1; nothing about `139-GH15-COMMENT.md` or `139-check-claims.py` changed,
   so there was nothing beyond this SUMMARY to commit.

## Files Created/Modified

- `.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md` -- the gh#15 correction comment
  body, byte for byte. Blob SHA `635c8ccac8711055db2a317be8f3987559d01f85`, 12229 bytes, 67 lines.
  Committed, gate-clean, **not yet frozen** -- plan 139-04 freezes it alongside the body amendment.

## Decisions Made

See `key-decisions` in the frontmatter above. In summary: the erase-pulse double-duty observation is
named in prose with no line-number citation at all, rather than citing a range engineered to dodge the
forbidden `eprom.cpp#L283` substring; a bare unpinned minipro repo URL was drafted then removed since it
would have failed the permalink-pinning verify leg and was redundant with the already-pinned `t48.c`/
`main.c` links; section order follows gh#15's own reading order rather than 137-GH12-COMMENT.md's exact
shape, per CONTEXT's explicit discretion grant; and the amendment table's reasons are scoped to the
plan's own named dispositions, not embellished.

## Deviations from Plan

None -- plan executed exactly as written. Both tasks completed on the first attempt: Task 1's comment
passed every one of its five literal verify blocks without a second draft, and Task 2's gate run passed
clean on the first attempt with zero wording changes required, so no "fix and re-verify" cycle was
triggered anywhere in this plan.

## Issues Encountered

None. One thing worth naming as a near-miss rather than an issue: an early draft of the C2 section
included a bare `https://gitlab.com/DavidGriffith/minipro` mention for readability; this was caught and
removed before the file was written, because the permalink-pinning verify leg (`PERMALINKS-PINNED-OK`)
requires every `github.com`/`gitlab.com` link to embed a commit SHA, and a bare repository root URL
does not. The required literal-string token (`gitlab.com/DavidGriffith/minipro`) is still satisfied
because it is a substring of the pinned `t48.c`/`main.c` blob URLs used elsewhere in the same section.

## User Setup Required

None -- no external service configuration required. This plan makes no state-changing `gh` call (only
read-only `gh issue view`) and no `git push` of any kind.

## Next Phase Readiness

- **139-04 is unblocked**: `139-GH15-COMMENT.md` exists, is committed (`291efa15`), and passes the claim
  gate clean. Plan 139-04 freezes it (blob SHA + byte length, already recorded above:
  `635c8ccac8711055db2a317be8f3987559d01f85`, 12229 bytes) alongside authoring and freezing
  `139-GH15-BODY-AMENDMENT.md`.
- **139-05's operator gate has real content to review**: the comment is drafted, gate-clean, and
  citation-complete -- nothing about its substance is a placeholder.
- **No requirement ticked by this plan** (`requirements-completed: []`), matching the plan's own scope
  guard exactly. ISSUE-01 and ISSUE-02 tick only in 139-05 on the operator's wording approval; ISSUE-03
  only on a verified post. Project-wide requirement state is unchanged by this plan.
- No sub-repo commit was made by this plan (pure meta-repo documentation; `firestarter` and
  `firestarter_app` working trees confirmed to show only the two pre-existing stale-gitlink entries,
  unchanged before and after both tasks).
- **Nothing has been posted to GitHub. Nothing has been pushed.** gh#15 remains `OPEN` with zero
  comments and no labels, confirmed by a fresh live read at the end of Task 2.

---
*Phase: 139-gh-15-correction-outward*
*Completed: 2026-08-09*

## Self-Check: PASSED

- FOUND: `139-GH15-COMMENT.md`
- FOUND: `139-03-SUMMARY.md`
- FOUND commit: `291efa15` (Task 1: draft 139-GH15-COMMENT.md)
- FOUND commit: `a128480d` (this SUMMARY)
