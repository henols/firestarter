---
phase: 139-gh-15-correction-outward
plan: 01
subsystem: docs
tags: [github-evidence, citation-register, pulse-width, eprom-cpp, memory-cpp, gh15]

requires:
  - phase: 138-preconditions-baseline
    provides: "the live pulse-width distribution (138-02-PULSE-DISTRIBUTION.md, n=170/127/32) and the runnable 138-pulse-distribution.py this register cites as C2's evidence"
provides:
  - "139-GH15-ORIGINAL-CRITERIA.md: gh#15's nine acceptance-criteria boxes captured verbatim, mechanically, from the live issue body"
  - "139-CITATIONS.md: the evidence register -- gh#15 before-state, three pinned commit SHAs, 15 content-verified citation rows, and the D-10 three-ref blob-equality baseline"
  - "the corrected program-pulse anchor (memory.cpp:321-330, memory_set_data()) replacing 139-CONTEXT.md D-06's eprom.cpp:283 erase-pulse mis-citation"
affects: [139-02, 139-03, 139-04, 139-05]

tech-stack:
  added: []
  patterns:
    - "verify by content at a pinned SHA, never by HTTP status code alone -- fetch raw, slice the line range, grep an expected substring"
    - "three-ref blob equality (HEAD / origin/beta / frozen base) proves a submodule file untouched; a meta-repo git status on a gitlink is not evidence either way"

key-files:
  created:
    - .planning/phases/139-gh-15-correction-outward/139-GH15-ORIGINAL-CRITERIA.md
    - .planning/phases/139-gh-15-correction-outward/139-CITATIONS.md
  modified: []

key-decisions:
  - "gh#15 carries NINE acceptance-criteria boxes, not the seven both 139-CONTEXT.md and ROADMAP.md state -- confirmed by mechanical capture and grep -c, matching 139-RESEARCH.md F-01 exactly; recorded, not reconciled by editing either document."
  - "memory.cpp:321-330 (memory_set_data()) is cited as the PROGRAM pulse; eprom.cpp:274-283 (eprom_internal_erase()) is kept in the register but explicitly relabelled the ERASE pulse, correcting 139-CONTEXT.md D-06's unqualified 'the pulse' attribution to eprom.cpp:283."
  - "138-BASELINE.md dropped from the citation set (404s at the pushed tip; not in D-06's binding list) -- this plan and this phase need no git push."
  - ".planning/PROJECT.md withheld from public citation -- its C1/C2/C3 table is at a different line number locally (71) than at the pushed tip (61); a permalink from local numbers would 200 and point at the wrong ten lines."

requirements-completed: []

coverage:
  - id: D1
    description: "gh#15's nine acceptance-criteria boxes captured verbatim by mechanical gh CLI capture (not hand transcription), proven to carry exactly 9 `- [ ] ` boxes, and proven byte-identical to 139-RESEARCH.md's independently-read copy"
    requirement: "ISSUE-01"
    verification:
      - kind: unit
        ref: "grep -c '^- \\[ \\]' 139-GH15-ORIGINAL-CRITERIA.md -> 9; diff against 139-RESEARCH.md's fenced copy -> empty (RESEARCH-DIFF-EMPTY-OK)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every citation the gh#15 comment will carry (9 raw file anchors, 2 GitHub commits, 4 minipro/GitLab lines) verified by CONTENT at a pinned commit SHA, with the enclosing function/section recorded for every source anchor"
    requirement: "ISSUE-01"
    verification:
      - kind: unit
        ref: "verify_anchor loop over all nine raw anchors -> 9x OK, zero FAIL, transcript in 139-CITATIONS.md section 2"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-10 baseline: eprom.cpp and memory.cpp blob-identical across HEAD, origin/beta, and the Phase 138 frozen base (3085084) -- the 'before implementation' claim is measured, not inferred from git status on a gitlink"
    requirement: "ISSUE-02"
    verification:
      - kind: unit
        ref: "for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/{eprom,memory}.cpp; done | sort -u | wc -l -> 1 (both files)"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-08-09
status: complete
---

# Phase 139 Plan 01: gh#15 Evidence Floor Summary

**Captured gh#15's nine acceptance-criteria boxes verbatim and built a 15-row, content-verified citation register at three pinned commit SHAs — correcting a mis-cited erase-pulse anchor and confirming the program-pulse file untouched by three-ref blob equality.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-08-09T11:50:42Z
- **Completed:** 2026-08-09T12:02:41Z
- **Tasks:** 2 of 2
- **Files created:** 2

## Task 1 — Capture gh#15's nine acceptance boxes verbatim from the live body

Mechanically captured (no hand transcription) via `gh issue view 15 --repo henols/firestarter_prom
--json body -q .body | awk '/^## Acceptance criteria/,0'`, written to
`139-GH15-ORIGINAL-CRITERIA.md`. Verification:

- `grep -c '^- \[ \]'` on the capture prints **9** — confirms `139-RESEARCH.md` F-01: gh#15 carries
  NINE acceptance boxes, not the seven both `139-CONTEXT.md` §canonical_refs and `.planning/ROADMAP.md`
  state. This divergence is recorded here and in the Task 1 commit message, and is deliberately **not**
  reconciled by editing either `139-CONTEXT.md` or `139-RESEARCH.md` (the plan's own prohibition).
- `diff <(grep '^- \[ \]' 139-GH15-ORIGINAL-CRITERIA.md) <(sed -n 's/^> \(- \[ \] .*\)$/\1/p' 139-RESEARCH.md)`
  is empty (`RESEARCH-DIFF-EMPTY-OK`) — the live capture is byte-identical to RESEARCH's own
  independently-read copy, an independent corroboration that gh#15's body has not changed since
  research ran (its `updatedAt == createdAt`, confirmed again below).
- `gh issue view 15 --repo henols/firestarter_prom --json comments -q '.comments | length'` printed
  **0**, both in this task and again, independently, at the start of Task 2 — nothing has been posted.
- File shape confirmed: first line is `## Acceptance criteria`, no YAML delimiter, `grep -c '^# '`
  is `0` (no H1).
- Sub-repo discipline: `git status --porcelain -- firestarter firestarter_app` showed only the two
  pre-existing stale-gitlink ` M ` entries; no file inside either was written.

## Task 2 — Resolve every citation by content at a pinned SHA and write the evidence register

Built `139-CITATIONS.md`, structured in four numbered sections (`## 0.` through `## 3.`), per
`139-PATTERNS.md` §5's evidence-register shape.

**§0 gh#15 before-state** (freshly re-measured, independent of Task 1's own check): `state=OPEN`,
comment count `0`, `labels=[]`, `updatedAt == createdAt` = `2026-07-12T09:15:27Z`, body **5964 bytes**
(via `wc -c`; a `jq .body|length` codepoint count of 5950 was noted and explained as a units artifact,
not a body change — the body contains multi-byte UTF-8 `µ` characters).

**§1 pinning strategy**: re-derived, not copied — meta `b6aa1dcb23ef9931105752ed6dd6badccf6719de`
(pushed tip), firmware `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` (`origin/beta`), host
`4d18b645ab18a2d2465f0f623062e9249eb24132` (`origin/beta`, same as branch tip). All three repos
confirmed `PUBLIC`. Both firmware anchor files confirmed blob-identical at `HEAD` and `origin/beta`.
Two divergences from `139-CONTEXT.md` recorded with reasons: `138-BASELINE.md` dropped (re-confirmed
404 at the pushed tip this session); `.planning/PROJECT.md` withheld from public citation (its
C1/C2/C3 table re-confirmed at line 71 locally vs. line 61 at the pushed tip — a 10-line shift).

**§2 anchor verification table**: all nine raw-file anchors verified by content via the `verify_anchor`
function (fetch raw at the pinned SHA, slice the line range, `grep -qF` an expected substring) — seven
via the plan's own literal `<verify><automated>` block (exited `OK-T2-ANCHORS`), the remaining two
(the erase-pulse anchor and the pulse-distribution script) via the identical function run immediately
after, since the plan's `<action>` text names nine anchors but its literal verify block reproduces
seven. All nine printed `OK`, zero `FAIL`. Plus: two GitHub commits (`8de307f`, `12286df`) resolved via
`gh api .../commits/<sha>`, both reachable from `origin/beta` per `branch -r --contains`; and four
minipro/GitLab lines (`t48.c:246,255,266-267`, `main.c:698`) — **gitlab.com was reachable this
session**, so these are fully re-verified by content rather than the `[CITED, not re-verified]`
fallback RESEARCH's own session had to use (minipro was not local to that session and GitLab was
unreachable from it).

**The C3 anchor correction, stated explicitly in the register:** `memory.cpp:321-330`
(`memory_set_data()`) is cited as **the PROGRAM pulse**. `eprom.cpp:274-283`
(`eprom_internal_erase()`) is kept in the register — relabelled explicitly as **the ERASE pulse** —
because `139-CONTEXT.md` D-06 lists `eprom.cpp:283` as C3's "the pulse" anchor with no qualifier, and
that citation resolves but is checkably the erase pulse; a reader following it would land in the wrong
function. The register states this correction in words at the `eprom.cpp:274-283` row.

**§3 D-10 baseline**: three-ref blob equality (`HEAD`, `origin/beta`, `3085084` — the Phase 138 frozen
firmware base) for both `eprom.cpp` and `memory.cpp`, each producing exactly one unique blob SHA across
all three refs (`8dfa4cced4...` and `478fa1d35f...` respectively). RESEARCH's own F-09 only measured
`memory.cpp` at `HEAD`/`origin/beta`; this plan extended the check to `3085084` per F-09's own
suggestion, and it agrees. Prose explains why the meta repo's ` M firestarter` / ` M firestarter_app`
lines are stale gitlink pointers (tracked SHA behind the checked-out commit), not source edits, and
states that `git submodule status` is never used as a verification mechanism here (confirmed, once,
to still fail unconditionally on an unrelated `.planning/v1.7/upstream-rurp` mapping gap).

**Verify blocks run:** `OK-T2-STRUCT`, `OK-T2-BLOB`, `OK-T2-ANCHORS` — all three of the plan's literal
`<verify><automated>` commands executed and printed their expected sentinel.

## Task Commits

1. **Task 1: Capture gh#15's nine acceptance boxes verbatim** — `52ef0ef2` (docs)
2. **Task 2: Resolve every citation by content at a pinned SHA** — `3b23f327` (docs)

## Files Created/Modified

- `.planning/phases/139-gh-15-correction-outward/139-GH15-ORIGINAL-CRITERIA.md` — gh#15's nine
  acceptance-criteria boxes, captured verbatim; no frontmatter, no title, no footer (a raw capture —
  any added byte would be corruption, since D-01's `<details>` block and D-10's read-back assertion
  both consume this file directly).
- `.planning/phases/139-gh-15-correction-outward/139-CITATIONS.md` — the evidence register: gh#15
  before-state, pinning strategy (three fresh-derived SHAs), 15 content-verified citation rows, and
  the D-10 three-ref blob-equality baseline. 278 lines (well above the 60-line floor).

## Decisions Made

- Recorded the nine-vs-seven acceptance-box divergence (RESEARCH F-01) as a finding in both the Task 1
  commit message and this SUMMARY, rather than editing `139-CONTEXT.md` or `.planning/ROADMAP.md` to
  reconcile it — per the plan's explicit prohibition and this project's standing
  append-a-correction-in-a-later-document convention.
- Extended the `verify_anchor` transcript to cover all nine raw anchors named in Task 2's `<action>`
  text, not only the seven reproduced in its literal `<verify>` block, since the acceptance criteria
  explicitly requires "the verify_anchor loop over all nine raw anchors."
- Re-verified minipro's GitLab citations live (gitlab.com was reachable this session) rather than
  falling back to the plan's authorized `[CITED, not re-verified this session]` escape hatch, since a
  live, content-verified citation is strictly stronger evidence than a cited-but-unconfirmed one.
- Kept (rather than dropped) the `eprom.cpp:274-283` anchor in the register despite it not being the
  program pulse, per the plan's own instruction — `handle->pulse_delay` doing double duty as both
  program and erase pulse is a real design observation worth citing, now correctly labelled.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' full `<action>` text and every `<verify>` block
were carried out; the only extensions beyond the plan's literal text (the two extra `verify_anchor`
calls, the live minipro re-verification, extending the D-10 blob check to `3085084` for `memory.cpp`)
were explicitly invited by the plan's own `<action>`/`<acceptance_criteria>` text or by RESEARCH's own
"consider extending" suggestion — not unplanned scope.

## Issues Encountered

None. Every measured figure matched `139-RESEARCH.md`'s recorded values exactly, with two exceptions
already noted as findings rather than problems: the byte-vs-codepoint body-length unit clarification
(§0), and the pleasant surprise that gitlab.com was reachable this session when it was not in
RESEARCH's own session (§2).

## User Setup Required

None — no external service configuration required. This plan is fully autonomous (`type="auto"` on
both tasks); the phase's one `checkpoint:human-action` gate belongs to plan 139-05, not this plan.

## Next Phase Readiness

- **139-02, 139-03, 139-04 and 139-05 are unblocked**: `139-CITATIONS.md` is the evidence register
  those later plans append to (§4/§5 by 139-04, §6 by 139-05) and cite from when drafting
  `139-GH15-COMMENT.md`; `139-GH15-ORIGINAL-CRITERIA.md` is the verbatim source both the `<details>`
  block (D-01, if the body amendment is authorized) and the D-10 post-edit read-back assertion consume.
- **The corrected C3 anchor set is now on record**: `139-GH15-COMMENT.md`'s drafting task (139-03)
  should cite `memory.cpp:321-330` for the program pulse and, if `eprom.cpp:283` is mentioned at all,
  label it explicitly as the erase pulse — never as an unqualified "the pulse."
- **No push is required anywhere in this phase**: `138-BASELINE.md` was dropped from the citation set
  specifically so the phase's only outward act stays the post itself (139-05), per D-08's shape.
- **Project-wide requirement state unchanged by this plan**: ISSUE-01, ISSUE-02, ISSUE-03 all remain
  open. This plan ticks nothing (`requirements-completed: []`), matching the ROADMAP's own
  per-plan requirement-ticking discipline (S-6): ISSUE-01/ISSUE-02 tick only in 139-05 on the
  operator's wording approval; ISSUE-03 only on a verified post.
- No sub-repo commit was made by this plan (pure meta-repo documentation; `firestarter` and
  `firestarter_app` working trees confirmed clean/untouched by every check in this plan — only
  pre-existing, unrelated dirt was observed in `firestarter_app`'s untracked files, none of it caused
  by this session).

---
*Phase: 139-gh-15-correction-outward*
*Completed: 2026-08-09*

## Self-Check: PASSED

- FOUND: `139-GH15-ORIGINAL-CRITERIA.md`
- FOUND: `139-CITATIONS.md`
- FOUND: `139-01-SUMMARY.md`
- FOUND commit: `52ef0ef2` (Task 1)
- FOUND commit: `3b23f327` (Task 2)
- FOUND commit: `9bc24a6b` (this SUMMARY)
