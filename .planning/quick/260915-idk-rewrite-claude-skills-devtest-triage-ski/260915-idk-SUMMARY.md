---
quick_id: 260915-idk
status: complete
completed: 2026-09-15
---

# Strict ASD-STE100 rewrite — devtest-triage

## Result

`ste-lint.py` exits 0. **23 hard violations → 0**; 39 → 11 total; density 1.5 → 0.4
per 100 words.

| Invariant | Before | After |
|---|---|---|
| Fenced tool transcripts | 18 blocks | 18 blocks, **byte-identical** |
| `test_supersede.py` | 6/6, exit 0 | 6/6, exit 0 |
| Line count | 447 | 447 |
| Diff shape | — | 33 hunks, **none changing line count** |

## Commits

- `7921e6cb` — rewrite frontmatter description in Strict STE
- `f8b828d5` — rewrite SKILL.md body in Strict ASD-STE100
- `14f7184f` — drop the gate apparatus (see Deviations)
- `ed519fc7` — shift the sibling skill's displaced citations

## What changed

Semicolons split into sentences, passive voice made active, and the six `dev test`
step tokens (`id`, `read`, `blank-check`, `write`, `verify`, `erase`) reserved for step
names only. They are exact machine tokens in the report JSON, so prose reuse of them
was a genuine one-word-two-meanings hazard: `verify it really is a PDF` and the heading
`### 5b. Read it` both bound ordinary English to a token an agent routes on. Both are gone.

The `description:` frontmatter was rewritten because it held the two over-length
sentences, and it garden-pathed on `close failures a later PASS supersedes` — a reduced
relative clause sitting in the string that decides whether the skill is invoked at all.
Every trigger phrase survives.

Replacement words were chosen **outside** `ste-lint.py`'s `SYNONYM_GROUPS`. The obvious
substitutions do not work: `confirm` shares a group with `check`/`verify`, and `remove`
shares one with `delete`/`erase`, so either would have relocated a violation rather than
clearing it.

## Deviations from plan

**The gate apparatus was removed on operator instruction — no gates for skills.**
Task 1 had built `gates.sh` (598 lines) plus `fences-baseline.txt`, `skill-before.txt`,
`token-census.{md,txt}` and `citations-derived.txt`. All were deleted in `14f7184f`.
None ever lived inside `.claude/skills/` — they were in this quick directory.

The verification they performed was re-run directly instead, and all of it passes: the
linter exit code, fence byte-identity against a pre-edit working-tree snapshot,
`test_supersede.py`, and the citation round-trip.

**Task 3 (citation repair) was reduced to almost nothing by measurement.** The plan
assumed the rewrite would displace line-anchored citations. It did not: the triage diff
is 33 hunks with **zero** line-count change, so all 14 citing lines still point at the
same positions. The only repairs needed were for the *sibling* skill, whose rewrite added
3 lines — 4 citations shifted by +3 in `ed519fc7`.

`147-RESEARCH.md:528`'s `:61-67` range was confirmed pre-existing-stale and left alone.

## Concurrency note

Phase 194-01 was executing in this same working tree throughout. Every commit staged
explicit paths only; no `git add -A` was used, and no phase-194 file was ever swept in.
