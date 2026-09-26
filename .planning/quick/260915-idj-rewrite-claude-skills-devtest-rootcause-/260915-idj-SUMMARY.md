---
status: complete
quick_id: 260915-idj
files_modified:
  - .claude/skills/devtest-rootcause/SKILL.md
commits:
  - 100538e3
  - 0331957a
  - faf7e055
---

# 260915-idj: Rewrite `.claude/skills/devtest-rootcause/SKILL.md` in Strict ASD-STE100

## One-liner

Rewrote the skill's prose to 0 hard STE violations, repaired the firmware submodule path
(`firestarter` → `firestarter_fw`), and left the obsolete page-size exception blockquote
byte-identical and explicitly not reviewed.

## Staged files (self-check per task, `git status --short` after each `git add`)

Each of the three commits staged exactly one file: `.claude/skills/devtest-rootcause/SKILL.md`.
No other path was ever in the staged set. Confirmed before each commit against the
concurrently-running phase-194 session's untracked/modified files, which stayed untouched.

## Linter counts

- **Before (baseline):** `39 violations (23 hard, baseline 0)` — 15 semicolon, 6
  synonym-rotation, 2 long-sentence.
- **After Task 1** (firmware path repair only, one new sentence added): hard count
  unchanged at this point except the new sentence itself never introduced a violation
  (checked incidentally by the PostToolUse STE hook, which flagged only a pre-existing
  semicolon at the line below — not part of Task 1's edit).
- **After Task 2** (body rewrite): `python3 ste-lint.py --json` body-only count (excluding
  frontmatter line 3) = **0 hard violations**. All 15 semicolons split into separate
  sentences. Five synonym-rotation groups (`check`/`verify`/`confirm`/`validate`,
  `start`/`launch`, `fix`/`repair`/`correct`, `get`/`fetch`) collapsed to one survivor
  word each in the body: `check`, `start`, `fix`, `fetch`.
- **After Task 3** (frontmatter rewrite): **`17 violations (0 hard, baseline 0)`, 2589
  words, 0.7 per 100 words.** All 17 remaining findings are advisory (passive voice,
  present perfect) and never fail the run. `ste-lint.py` exits 0.

## Fence delta (Task 1 pre-edit snapshot vs. final state)

Exactly one line pair, the single permitted edit:

```
7c7
< | FW=$ROOT/firestarter
---
> | FW=$ROOT/firestarter_fw
```

Verified by diffing a fenced-block extractor's output taken from the working tree
*before* any edit (`/tmp/260915-idj/fences.before.txt`) against the same extractor run
on the final file. No other fenced block changed, including the three unrelated
`henols/firestarter_prom` → `henols/firestarter` edits that were already dirty in the
working tree before this plan started.

## Frozen-block gate (page-size exception blockquote)

Ran before any edit (Task 1, precondition proof), after Task 2, and after Task 3. All
three runs printed `frozen block occurrences: 1` and exited 0. The four lines under
"The proof rule" heading, starting `> One exception exists: `_PAGE_SIZE_BY_PART`...`,
are byte-identical to their pre-task content in every commit.

**This paragraph was left unchanged on purpose, not because it was reviewed and found
accurate.** It is now known to describe a mechanism that no longer exists: commit
`859109d` in `firestarter_app` ("feat(194-01): emit the real page size for every
upstream-native 0x05 row") removed `_PAGE_SIZE_BY_PART` from `build_db.py` while phase
194 was executing concurrently in this same working tree. Repairing the stale
`build_db.py:114` citation would have written a confidently false statement pointing at
a symbol that no longer exists. The operator decided this paragraph gets struck in
separate work, after phase 194 settles — not in this task. Do not read this SUMMARY as
confirmation that the blockquote's content is correct; it is confirmation only that its
*bytes* did not change.

## Deviations from plan

None. All three tasks executed as written, including the withdrawn-scope handling for
the page-size blockquote (already reflected in the plan itself, not a deviation
discovered during execution).

## Phrasing kept long on purpose

None required — every hard-violation sentence split cleanly into shorter sentences
without losing a fact, hedge, or rationale. Two places got extra care to avoid dropping
precision:

- The frontmatter's original single 52-word sentence ("Investigate the firestarter code
  behind a triaged `dev test` chip failure and fix the real defect — a decode bug in the
  database generator, or a genuine bug in the host app or firmware — then report the fix
  on the issue with the artefact versions carrying it and a fix:committed / fix:released
  label.") became three sentences that preserve every clause, including the "or" between
  the two defect types and the exact `fix:committed` / `fix:released` label spelling.
- The 50-word trigger-phrase sentence became three "Use ... " sentences, each keeping
  every literal trigger token asserted by the plan's gate (`dev test`, `EPROM`,
  `root-cause`, `pinout`, `protocol`, `VPP`, `database generator`, `datasheet`,
  `firmware`, `host app`, `at28c256`, `w27e257`).

## Word substitutions for synonym-rotation cleanup

- `verify` → `check` (2 sites: "so check it after touching `build_db.py`", "then
  **re-check every value**"). Kept "check" throughout since it matches the `--check`
  flag already prominent in the document.
- `validated` → `checked`, `confirmed` → `checked` (firmware-bench-proof sentence).
- `launch` → `run` (the one prose site that clashed with a byte-frozen verbatim
  quotation of `gsd-debugger`'s own entry-flow text, which contains the word `start` and
  could not be touched).
- `correcting` → `fixing`, `Correct` → `Right` (troubleshooting-table interjection sense,
  not the verb sense — the plan flagged this specific cell as a false-positive lexical
  match).
- `gets` → `gives` / rewrote "gets eliminated" to "is eliminated" (two sites where `get`
  was being used as an auxiliary/copula, not in its acquire-something sense, and would
  otherwise have clashed with the surviving `fetch` in the Troubleshooting table).
- Frontmatter: `correct the database generator` → `fix the database generator` (kept the
  token `database generator` intact for trigger matching, per plan instruction).

## Verification (plan's 8-item list, all passed)

1. `ste-lint.py` exits 0: `17 violations (0 hard, baseline 0)`.
2. Fence delta is exactly the two lines of the firmware path repair.
3. `infoic_lookup.py --check` exits 0 (`ok: MINIPRO_XML_URL...`, `ok: VPP table...`).
4. `/workspaces/firestarter_fw` exists; no bare `ROOT/firestarter` reference remains.
5. Frozen-block gate: `frozen block occurrences: 1`, exit 0.
6. Six prose tables report row counts `[9, 10, 4, 5, 4, 16]`.
7. `git diff` shows no command/flag/path/filename/function-name/identifier change other
   than the one firmware path repair — the only new backtick spans introduced anywhere
   in the diff are `` `firestarter` `` and `` `_fw` ``, both from the one explanatory
   sentence Task 1 was instructed to add, not new code identifiers.
8. `git diff` touches zero lines of the page-size exception blockquote.

## Self-Check

- `.claude/skills/devtest-rootcause/SKILL.md`: FOUND, modified as described.
- Commit `100538e3`: FOUND in `git log --oneline`.
- Commit `0331957a`: FOUND in `git log --oneline`.
- Commit `faf7e055`: FOUND in `git log --oneline`.

## Self-Check: PASSED
