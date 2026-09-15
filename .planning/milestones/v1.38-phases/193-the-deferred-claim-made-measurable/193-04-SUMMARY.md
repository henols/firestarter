---
phase: 193-the-deferred-claim-made-measurable
plan: 04
subsystem: docs
tags: [git, submodules, gitmodules, gate-03, archaeology, honesty]

requires:
  - phase: 193-the-deferred-claim-made-measurable
    provides: "193-03's three evidence transcripts — 193-gate-03-fresh-clone.txt, 193-gate-03-existing-clone.txt, 193-gate-03-submodule-sync-hazard.txt. This plan cites them and adds no new reading."
provides:
  - ".planning/notes/gitmodules-archaeology-trap.md — the dedicated GATE-03 note: the trap, both workarounds as ordered procedures, the submodule-sync hazard and its two-command repair, the banked transcripts, and the honest limits"
affects: [193-05]

actuals:
  tokens: 3198
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Sibling-note register from v135-close-procedure-under-protection.md and 999.9-repo-rename-impact-analysis.md. No YAML frontmatter. Bold Date/Raised during/Status/Method key lines. ## headings. Transcript-then-prose."
    - "Every ordered-procedure step states its command and its consequence inline, in the shape 999.9's own 'Ordered procedure' section uses."
    - "A projected, unverifiable claim is explicitly labelled 'projection' in the prose that carries it, rather than stated as a bare fact. That wording is what the D-16 honesty constraint requires."

key-files:
  created:
    - .planning/notes/gitmodules-archaeology-trap.md
  modified: []

key-decisions:
  - "Wrote the note with no YAML frontmatter, matching the two sibling notes (v135-close-procedure-under-protection.md, 999.9-repo-rename-impact-analysis.md). The plan's own environment_notes forbid adding one."
  - "Cited the sync-hazard repair and the fresh/existing-clone workarounds by transcript filename and READING number only. Never by line number. This follows the project's 'cite by content, not line number' idiom and this plan's explicit prohibition."
  - "Kept the fix/repair word contrast in '## The sync hazard' ('This is a repair, not a fix') as one deliberate exception to otherwise-consistent word choice. The plan's own action text requires that exact contrast. 193-03 made the same call in its own transcript prose."
  - "Applied ASD-STE100 sentence-length and semicolon fixes across every paragraph after the lint hook flagged the first drafts of both tasks. Re-verified 0 sentences over 25 words and 0 semicolons before each commit."

requirements-completed: []

coverage:
  - id: D1
    description: "The .gitmodules history trap is explained (per-commit URL pinning, why archaeology re-triggers it), and the note states plainly that a plain submodule update at a pre-rename ref succeeds today because the old slug still redirects"
    requirement: GATE-03
    verification:
      - kind: other
        ref: "grep -c over the four ## headings in Task 1 returns 4. Grep for the redirect claim and the evidence/193-gate-03-fresh-clone.txt citation both return non-zero."
        status: pass
    human_judgment: false
  - id: D2
    description: "Workaround A (existing clone) is written as an ordered procedure of literal commands. It states both halves of the .git/config-vs-.gitmodules precedence rule. It cites evidence/193-gate-03-existing-clone.txt by filename and reading."
    requirement: GATE-03
    verification:
      - kind: other
        ref: "grep for the literal git config/checkout/submodule-update commands and the transcript filename in the Workaround A section. All present."
        status: pass
    human_judgment: false
  - id: D3
    description: "Workaround B (fresh clone at v1.35) is written as an ordered procedure. It states the override-before-update ordering is load-bearing. It explains why v1.35, not a milestone-branch commit, is the demonstration ref. It cites evidence/193-gate-03-fresh-clone.txt."
    requirement: GATE-03
    verification:
      - kind: other
        ref: "grep for 'git clone --no-recurse-submodules', the load-bearing-order sentence, and the transcript filename in the Workaround B section. All present."
        status: pass
    human_judgment: false
  - id: D4
    description: "The one-shot git -c idiom is present. It is labelled explicitly as a convenience beside the two prescribed workarounds, not a replacement for either."
    requirement: GATE-03
    verification:
      - kind: other
        ref: "'## A one-shot variant, supplementary' section text names it a convenience beside Workaround A and Workaround B, not a replacement for either."
        status: pass
    human_judgment: false
  - id: D5
    description: "The git submodule sync hazard is a first-class warning. Both clobbered locations are named — the .git/config override and the child's own origin. The two-command repair is given literally. The durability check (a second sync re-clobbers both) is stated. The neighbouring 999.9 procedure step that makes the hazard reachable is named."
    requirement: GATE-03
    verification:
      - kind: other
        ref: "grep for both repair commands, 'git submodule sync --recursive', and the durability-check sentence in '## The sync hazard'. All present."
        status: pass
    human_judgment: false
  - id: D6
    description: "The projected post-claim failure is labelled a projection, never an observation. No section anywhere in the note describes it as observed or measured."
    requirement: GATE-03
    verification:
      - kind: other
        ref: "awk-scoped grep over '## Honest limits' onward. 'projection'/'projected' count 1. 'observed (breakage|failure)' and 'we measured the post-claim' count 0."
        status: pass
    human_judgment: true
    rationale: "Whether the surrounding prose genuinely reads as a labelled projection, rather than a hedged observation, is a judgment call about tone. The plan itself routes this to human review rather than to a keyword grep alone."
  - id: D7
    description: "Every citation in the note is by path/section-heading or by filename, never by line number. The note carries no YAML frontmatter block."
    requirement: GATE-03
    verification:
      - kind: other
        ref: "grep for '\\.(md|py|sh|cpp|h):[0-9]+' returns 0. Grep for '^---$' returns 0."
        status: pass
    human_judgment: false

duration: 14min
completed: 2026-09-14
status: complete
---

# Phase 193 Plan 04: The `.gitmodules` Archaeology Note Summary

**A new dedicated note (`.planning/notes/gitmodules-archaeology-trap.md`) carries the `.gitmodules` history trap and both GATE-03 workarounds as ordered literal-command procedures citing plan 193-03's executed transcripts. It also carries the undocumented `git submodule sync` hazard with its two-command repair. A final honest-limits section labels the post-claim failure a projection, not an observation.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-09-14 (session start)
- **Completed:** 2026-09-14
- **Tasks:** 2
- **Files modified:** 1 (new)

## Accomplishments
- Wrote `## The trap`. States the per-commit URL-pinning mechanism. Names `v1.35` as the concrete ref a reader will hit. States plainly, and boldly per the plan's house style for a load-bearing negative, that the trap does not bite today. The old slug still redirects.
- Wrote `## Workaround A — an existing clone` and `## Workaround B — a fresh clone at a pre-rename ref`. Both are numbered, literal-command ordered procedures. Each states the consequence of every step inline. Each cites its 193-03 transcript by filename and READING number. Each explains a mechanism 193-RESEARCH.md verified directly. `.git/config` wins on disagreement and is invisible on agreement. The override-before-update ordering is load-bearing because `submodule init` preserves an existing override rather than re-copying it.
- Wrote `## A one-shot variant, supplementary`, carrying the non-persisting `git -c submodule.firestarter.url=… submodule update --init` idiom. Labelled explicitly as a convenience beside the two prescribed workarounds, not a replacement for either.
- Wrote `## The sync hazard`. Names `git submodule sync` as the command that silently clobbers both the `.git/config` override and the child's own `origin` remote. This happens when the command runs at a pre-rename ref. Embeds the captured before/after readings. Gives the two-command repair literally. States the durability check that proves a second `sync` re-clobbers both — a repair, not a fix. Names the neighbouring `.planning/notes/999.9-repo-rename-impact-analysis.md` § "Ordered procedure" Phase A step 2 as the routine-hygiene step that makes the hazard reachable.
- Wrote `## Banked evidence — the executed transcripts`. Names all three plan 193-03 transcripts and what each proves.
- Wrote `## Honest limits` in three labelled points. The trap does not bite today. The post-claim failure shape is a projection rather than an observation, and is unverifiable while the redirect is live. History cannot be repaired — only documented and worked around.

## Task Commits

Each task was committed atomically:

1. **Task 1: The trap and both workarounds, as ordered procedures** - `1d296c4c` (docs)
2. **Task 2: The hazard, the banked evidence, and what is projection** - `16ac3cf2` (docs)

**Plan metadata:** (this commit)

## Files Created/Modified
- `.planning/notes/gitmodules-archaeology-trap.md` - the new GATE-03 note: the trap, both workarounds, the sync hazard, banked evidence, and honest limits

## Decisions Made
- No YAML frontmatter in the note. This matches both sibling notes this plan's `read_first` named.
- Citations by filename/READING or by section heading throughout. No `path:NN` citations anywhere. This follows the project's own "cite by content, not line number" convention and this plan's explicit prohibition.
- Kept the deliberate "repair, not fix" word contrast in the sync-hazard section, because the plan's action text requires that exact contrast. Otherwise normalized word choice to satisfy the ASD-STE100 synonym-rotation check.

## Deviations from Plan

None — plan executed exactly as written. The ASD-STE100 structural-lint corrections applied after each `Write`/`Edit` split long sentences, removed semicolons, and resolved one word-choice rotation. These are style corrections under the operator's globally-installed `asd-ste100` skill instruction. They are not deviations from the plan's content requirements — no fact, citation, command, or claim changed as a result. Every acceptance criterion and `<verify>` command in both tasks was re-run against the final text before each commit, and passed.

## Issues Encountered
- The ASD-STE100 lint hook flagged several long sentences and one semicolon after the first `Write` of Task 1's content. It flagged more after the first `Edit` extending the note with Task 2's content. Each flagged sentence was split into shorter sentences, all now 25 words or fewer. Semicolons were removed. Every fact, command, and citation was preserved. A word-count scan before each commit checked for 0 sentences over 25 words and 0 semicolons in the final file. Both checks passed before every commit.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
The note exists. It carries all seven required headings. It cites all three plan 193-03 transcripts by filename. It states both halves of the `.git/config`-vs-`.gitmodules` precedence rule. It documents the `git submodule sync` hazard with its two-command repair. It separates execution from projection under `## Honest limits`. Plan 193-05 can now add `CLAUDE.md`'s GATE-03 pointer into the repository-structure section, citing this note by path and section heading. GATE-03 stays `Pending` in `REQUIREMENTS.md` — correctly, because 193-05 also declares GATE-03 and has not yet produced a SUMMARY. The shared-ID gate defers marking it complete until every declaring plan finishes. No blockers.

---
*Phase: 193-the-deferred-claim-made-measurable*
*Completed: 2026-09-14*

## Self-Check: PASSED

- `.planning/notes/gitmodules-archaeology-trap.md` exists on disk (verified with `[ -f ]`).
- Both task commits (`1d296c4c`, `16ac3cf2`) are present in `git log --oneline --all`.
- All Task 1 and Task 2 `<verify>` grep commands re-ran against the final committed file. Every one returned the required count. Task 1: 4 headings, 4 bold keys, 0 frontmatter markers, 8 transcript-filename hits, 9 literal-command hits, 0 line-numbered citations. Task 2: 3 more headings, 11 transcript-filename hits, 4 repair-command hits, 1 hazard-procedure hit. Also 1 projection-word hit in Honest limits, 0 observation-phrasing hits, 6 fenced-code-block delimiters. The branch check returned the expected name.
- No credential material, secrets, or destructive commands against `/workspaces` appear anywhere in the note. It only cites transcripts plan 193-03 already committed, captured in disposable clones.
- ASD-STE100 structural lint re-checked clean on the note (0 sentences over 25 words, 0 semicolons) before both commits.
