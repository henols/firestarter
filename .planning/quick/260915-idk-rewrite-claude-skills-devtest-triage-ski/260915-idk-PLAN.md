---
phase: quick-260915-idk
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .claude/skills/devtest-triage/SKILL.md
  - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/gates.sh
  - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/skill-before.txt
  - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/fences-baseline.txt
  - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/token-census.txt
  - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/token-census.md
  - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/citations-derived.txt
  - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/citation-remap.md
  - .planning/milestones/v1.37-research/SUMMARY.md
  - .planning/milestones/v1.37-research/PITFALLS.md
  - .planning/milestones/v1.37-phases/187-answered-reports/187-RESEARCH.md
  - .planning/milestones/v1.37-phases/187-answered-reports/187-PATTERNS.md
  - .planning/milestones/v1.37-phases/187-answered-reports/187-CONTEXT.md
  - .planning/milestones/v1.36-phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-09-PLAN.md
  - .planning/milestones/v1.36-phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-07-PLAN.md
autonomous: true
requirements: [260915-idk]

estimate:
  tokens: 62000
  raw_tokens: 124000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "ste-lint.py on the skill file exits 0 and prints a count line ending `0 hard, baseline 0`."
    - "Every code fence in the skill file is byte-identical to its pre-task content."
    - "The skill's own supersede self-test still exits 0 with 6/6 cases."
    - "The six dev-test step tokens appear in prose only as step names, quoted external text, or domain nouns — never as ordinary English verbs."
    - "The frontmatter description keeps all seven trigger phrases, stays one physical line, and no longer garden-paths on the supersede clause."
    - "All six prose tables keep their rationale column, their column count and their row count."
    - "Every .planning/ line citation into the skill file that this edit displaced points at the same content it named before."
    - "The gate derives the citation enumeration itself. It does not read a total from this plan, and it requires one classified row per target it found."
    - "The gate proves the citation round trip mechanically. For a retargeted or an unmoved target, the skill text at the new line is byte-identical to the text that was at the old line."
    - "The round-trip gate leg is proven reachable: it exits non-zero on a deliberately corrupted remap row before the task relies on it."
  artifacts:
    - .claude/skills/devtest-triage/SKILL.md
    - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/gates.sh
    - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/skill-before.txt
    - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/token-census.md
    - .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/citation-remap.md
  key_links:
    - "SKILL.md frontmatter description -> skill trigger matching (the routing text a model reads before it ever opens the file)"
    - "SKILL.md prose step-token vocabulary -> the `steps[]` names an agent parses out of a dev test report JSON"
    - "SKILL.md section 3a three-leg table -> an irreversible outward action (closing a community member's GitHub issue)"
    - "SKILL.md label names -> live GitHub labels and scripts/devtest_issues.py"
    - ".planning/ file:LINE citations -> SKILL.md line numbers"
---

<objective>
Rewrite the prose of `.claude/skills/devtest-triage/SKILL.md` in Strict ASD-STE100, reserve
the six dev-test step tokens for step names only, and rephrase the garden-path clause in the
frontmatter description.

Purpose: this file is an agent-facing instruction document. A downstream agent parses it with
no person present to resolve ambiguity, and then takes an irreversible outward action — it
closes a community member's GitHub issue. Six words in its prose are also exact machine tokens
in the `dev test` report JSON, so a prose reuse of one of them collides with a protocol name.

Output: the same file, with 0 hard STE violations, the six tokens reserved, every code fence
byte-identical, and every fact, hedge, rationale column and label name preserved.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/workspaces/CLAUDE.md
@/home/vscode/.claude/skills/asd-ste100/SKILL.md
@/workspaces/.claude/skills/devtest-triage/SKILL.md

Do NOT read `.planning/STATE.md` in full. It is 546 KB and is not load-bearing here.
</context>

<facts_established_during_planning>

All numbers below were measured against the working tree on 2026-09-15. Use them as the
starting invariants. If any of them does not reproduce, the file changed after planning —
stop and say so instead of adapting.

## Baseline

| Fact | Value |
|---|---|
| `ste-lint.py` on the file | `39 violations (23 hard, baseline 0), 2602 words, 1.5 per 100 words`, exit 1 |
| Hard breakdown | 16 semicolon, 2 long-sentence, 5 synonym-rotation |
| Advisory (never fails the run) | 16 passive-voice |
| Findings inside a code fence | 0 — the linter is fence-aware |
| `scripts/test_supersede.py` | `6/6 cases behaved as specified`, exit 0 |
| File length | 446 lines |
| Fence-only extract | 139 lines, sha256 `385873372be3d9fdf307511869ca494700b194c62d8225913b398c802a496735` |

Hard = linter level `advisory-free`. Passive voice and compound tenses are advisory and do
not fail the run. Strict mode still says fix them where the fix costs nothing, but they are
not the gate.

## The linter's masking rules — this is what makes the job tractable

Read `ste-lint.py` before rewriting. Three behaviours matter:

1. It skips fenced blocks entirely.
2. It **deletes inline code spans** (backtick pairs) before every rule check. A step name
   written as a backticked span is invisible to the linter. This is why backticking a step
   name is both the reader-facing convention and the mechanical fix.
3. It splits a markdown table row into cells and scans **each cell as its own sentence unit**
   for the 25-word cap. A rationale cell is measured on its own.

## Semicolons — 16, all hard

Lines 9, 10, 97, 162, 173, 211, 215, 216, 225, 248, 301, 337, 345, 437, 444, 445.

Nine of them sit in table cells in the rationale columns. Splitting one into two sentences is
the fix. Compressing the rationale away is not.

## Long sentences — 2, both on line 3

The frontmatter description carries a 35-word sentence and a 48-word sentence. The cap is 25.
These are the only two long-sentence findings in the whole file — the body prose already
clears the cap.

## Synonym rotation — 5 hard findings, but more occurrences than findings

The linter records only the FIRST occurrence of each group member, so removing a flagged line
promotes the next occurrence into a new finding. Every occurrence of a losing member must go,
not only the flagged one. Measured occurrence lists, after fence and code-span masking:

| Group | Keeper (first in document order) | Losing member | Every visible occurrence |
|---|---|---|---|
| check / verify / confirm / validate | `check` (9 occurrences) | `verify` | lines 3, 280 |
| check / verify / confirm / validate | `check` | `validate` (as `validated`) | line 241 |
| delete / remove / erase | `erase` (line 114, and it is a step token) | `delete` | lines 288, 435 |
| fix / repair / correct | `fix` (13 occurrences) | `correct` | lines 381, 406 |
| get / retrieve / fetch / obtain | `get` (5 occurrences) | `fetch` | lines 279, 288, 435 |

## TRAP — the two obvious replacement verbs are themselves banned

The item text suggests "confirm" and "remove" as replacements. Both would create a NEW hard
violation, because the linter groups them with words that must stay:

- `confirm` is in the same group as `check`, which is the keeper.
- `remove` is in the same group as `erase`, which is a step token and cannot be dropped.

Locked substitutions, chosen because none of them is in any linter synonym group:

| Prose use to remove | Replacement | Note |
|---|---|---|
| `verify` as an ordinary verb | `check` | the group keeper, already used 9 times |
| `validated` as an ordinary verb | recast the sentence | the backticked label span stays as it is |
| `delete` the bad file | `discard` | not `remove` — same group as a step token |
| `fetch` the datasheet | `get` | the group keeper, and the section heading already says it |
| `correct` as an adjective | `right`, or state what it agrees with | `right` is already used at line 402 |
| `read` as an ordinary verb | `inspect`, or recast | `read` is in no linter group, so only the census catches it |
| `write` as an ordinary verb | `save` | as in saving a comment body to a file |

## The six reserved step tokens

`id`, `read`, `blank-check`, `write`, `verify`, `erase` are the `steps[]` names in the report
JSON. A downstream agent routes on them. There are 37 occurrences outside code fences today.
Each surviving occurrence must fall into exactly one of three allowed classes:

| Class | Meaning | Examples in the current file |
|---|---|---|
| `STEP` | a reference to the dev-test step of that name | `blank-check BAD` (406), `` `erase` reported NA/BAD `` (320), the section 3a table (174) |
| `QUOTED` | verbatim external text: a datasheet term, a `firestarter info` output field, a GitHub issue title, a tool name, a file name, a flag, an identifier | `Can be erased:` (320), `Chip ID:` (321), the `Read` tool (300, 434), the quoted issue title at 408 |
| `NOUN` | a compound technical noun whose head is not the step | `page-write` buffer (323), `write cycle` (325), `write` path (322), write protection (324), `erasable` (320), UV-EPROM erase (114) |

The forbidden class is `VERB`: the token used as an ordinary English verb. Confirmed instances
to fix: line 3 (`verify` the pin map), 14 (the skill reads and writes), 149 (read as data),
244 (the person reading), 280 (`verify` it really is a PDF), 288 (`delete` it), 291 (the `5b`
heading), 293 (read the page), 333 (the rig reads a rail), 345 (write the body to a file),
413 (read the field), 424 (write the table), 425 (the script reads it back), 442 (read the
reason).

Line 408 quotes the GitHub issue title "AT28Cxxx Write Protection Enable/Disable missing".
That is external verbatim text. It does not change.

## The frontmatter description

One physical line, line 3, an unquoted YAML scalar. It carries three things that must all
survive:

1. The three outcomes. The second one, `close failures a later PASS supersedes`, is a reduced
   relative clause and garden-paths. Rephrase to the shape `close a failure when a later PASS
   supersedes it`.
2. The sentence `Labels every issue by cause.`
3. Seven trigger phrases, which drive skill selection:
   1. triage dev test issues
   2. go through the chip test reports
   3. check an EPROM against its datasheet
   4. verify the pin map or VPP for a chip
   5. close passing validation issues
   6. defer failures that later passed
   7. work an issue like "[dev test] at28c256 — FAIL"

Trigger 4 is the one collision. It keeps its object noun phrase and changes only its verb, to
`check`. No trigger may be dropped. Triggers are quoted user phrasings, so the phrasal verb in
trigger 2 stays.

YAML safety: keep the value on one physical line, do not let it start with a quote, and do not
introduce a colon-plus-space anywhere inside it. PyYAML is NOT installed in this devcontainer,
so the structural check is positional, not a parse.

## The six prose tables

| Location | Columns | Data rows |
|---|---|---|
| 111-117 Verdicts | 3 | 5 |
| 155-162 Rule / Why | 2 | 6 |
| 170-174 the three legs | 3 | 3 |
| 208-220 Labels | 3 | 11 |
| 314-325 cross-check | 4 | 10 |
| 432-446 Troubleshooting | 2 | 13 |

## TRAP — the fence baseline is the working tree, not HEAD

`.claude/skills/devtest-triage/SKILL.md` already carries an uncommitted change, and that
change edits text INSIDE three code fences (lines 236, 238 and 349, following the
`henols/firestarter_prom` to `henols/firestarter` rename). A fence comparison against HEAD
would therefore report fence changes this task did not make. Baseline the fences from the
working tree at task start. That rename-follow is correct and stays.

## Line citations into this file

A prose rewrite can displace them. The three files under `.planning/graphs/` are generated
artifacts and are never hand-edited.

**TRAP — a citing LINE can carry more than one citation TARGET.** An enumeration of one target
per matching line undercounts. Two shapes appear in this corpus:

1. A full citation: `` `.claude/skills/devtest-triage/SKILL.md:205-225` ``.
2. A backticked shorthand range later on the same line: `` `:340-355` ``, which inherits the
   file named earlier on that line.

Measured on 2026-09-15, excluding `.planning/graphs/` and this task's own directory: **14
matching lines in 8 files, carrying 18 citation targets** — 14 full and 4 shorthand. The
shorthand targets are `:340-355` (187-RESEARCH 1898), `:375` (181-09 109), `:330` (181-09 271)
and `:375` (181-09 272). The one on 181-09 line 109 names the same skill line as the full
citation on that line, and both are separate text tokens that a repair must reach.

**These numbers are the tripwire, not the contract.** The gate derives the target list itself
at run time. Do not hard-code 14 or 18 anywhere. If the derived total differs from 18, a citing
file changed after planning: record the delta in `citation-remap.md` and continue, because a
citing file is free to change and this plan does not own it.

**TRAP — the enumeration must exclude its own output.** `citation-remap.md` lives under
`.planning/` and contains `SKILL.md:NNN` strings by construction. An enumerator that does not
exclude `.planning/quick/260915-idk-*/` counts its own rows and grows on every run.

The target `SKILL.md:61-67` in `147-RESEARCH.md` is already stale before this task starts. It
claims to name the verbatim `show` render, and those lines hold the section 2 heading instead.
It is out of scope: record it, do not retarget it. `147-RESEARCH.md` is therefore the one citing
file this task does not edit, which is why it is absent from `files_modified`.

</facts_established_during_planning>

<tasks>

<task type="tracer">
  <name>Task 1: Build the invariance harness, then rewrite the frontmatter description end-to-end</name>
  <files>.planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/gates.sh, .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/skill-before.txt, .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/fences-baseline.txt, .claude/skills/devtest-triage/SKILL.md</files>
  <precondition>The fence-only extract of `.claude/skills/devtest-triage/SKILL.md` has sha256 `385873372be3d9fdf307511869ca494700b194c62d8225913b398c802a496735` and `ste-lint.py` reports 23 hard violations. If either differs, the file changed after planning — stop and report instead of adapting.</precondition>
  <action>
First write the harness, because every later task is gated by it.

Copy the skill file, unmodified, to `skill-before.txt` before you edit one character of it.
This is the pre-edit baseline and it is load-bearing twice: the fence baseline derives from it,
and it is the left-hand side of the citation round trip in task 3. Take it from the working
tree, never from HEAD, for the same reason the fence baseline does.

Extract the fence-only baseline to `fences-baseline.txt` with an awk pass that toggles on any
line whose stripped form starts with three backticks or three tildes, printing the delimiter
lines and everything between them. Assert its sha256 equals the pinned constant. That
assertion is the precondition check — it proves the working tree is the one this plan was
written against, and it deliberately baselines the working tree rather than HEAD, because the
already-uncommitted rename-follow edits text inside three fences.

Then write `gates.sh` in the same directory. It runs every invariant and prints one PASS or
FAIL line per leg, exiting non-zero if any leg fails. The legs, in order:

1. Run `ste-lint.py` on the skill file. Require exit 0 and a count line reporting 0 hard.
2. Re-extract the fences and require the sha256 to equal `fences-baseline.txt`.
3. Run `scripts/test_supersede.py` and require exit 0.
4. Count the prose tables outside fences. Require six tables, with column counts 3, 2, 3, 3,
   4, 2 and data-row counts 5, 6, 3, 11, 10, 13, in document order.
5. Emit the reserved-token census: every occurrence of the six tokens and their inflections
   outside code fences, one per line, as line number, token, source line. Write it to
   `token-census.txt`. Then read the executor-written `token-census.md`, ignore lines starting
   with a hash, require one classified entry per census occurrence, and require zero entries
   whose class is the forbidden one.
6. Require all seven trigger phrases in the frontmatter description, matched by their object
   noun phrase so a verb substitution does not hide one.
7. Structural frontmatter check: line 1 and line 4 are the document separator, line 3 starts
   with the description key, the description occupies exactly one physical line, and its value
   contains no colon-plus-space.
8. Require the string `henols/firestarter` present and `henols/firestarter_prom` absent.
9. Derive the citation enumeration. Scan `.planning/` markdown for lines naming the skill file
   by line number, excluding `.planning/graphs/` and this task's own directory. From each such
   line, extract every full citation target AND every backticked shorthand range on that same
   line. Emit one record per target as citing file, citing line, old target, shape. Write it to
   `citations-derived.txt`. Then require `citation-remap.md` to carry exactly one row per
   derived record, keyed on that triple, and no row that the derivation did not produce. Do not
   compare against any number written in the plan.
10. Round-trip every remapped citation against the two files, on exact text. For each
    `citation-remap.md` row, by disposition:
    - `unmoved` and `retargeted`: for each endpoint of the range, require the line at the old
      number in `skill-before.txt` to be byte-identical to the line at the new number in the
      live skill file. An `unmoved` row is checked the same way, with old equal to new, so a
      wrong claim of "it did not move" fails here too.
    - `anchor`: exact text cannot round-trip, because this task rewrote the target line. Require
      a non-empty reason field, require the new line to exist in the file, and require the
      nearest preceding markdown heading above the new line to equal the nearest preceding
      heading above the old line in `skill-before.txt`. That is the mechanical form of "the same
      semantic anchor".
    - `pre-existing-stale`: require the old and new targets to be equal, and require the citing
      file to be unmodified in git.
    Any other disposition string fails the leg. Print the failing citing file, the endpoint, and
    both texts on a mismatch, so a failure is diagnosable without a second run.

Legs 9 and 10 need `citation-remap.md`, which task 3 writes. When that file is absent, print
SKIP for both legs. Accept `--final` as an argument: in `--final` mode a SKIP is a FAIL. Task 3
runs the gate with `--final`, so absence cannot pass as silence.

Keep the banned-word list inside `gates.sh`, read from a small array, so the plan itself never
has to carry a grep literal.

Then do the one prose rewrite this task owns: the frontmatter description on line 3. Split it
so every sentence is at most 25 words after inline code spans are stripped. Rephrase the
reduced relative clause about supersession into an explicit `when` clause. Change only the
verb of the pin-map trigger, to the group keeper, and leave its object noun phrase intact.
Keep all seven triggers, keep the cause-labelling sentence, keep `henols/firestarter`, and
keep the whole value on one physical line.

This task is the tracer: it touches the frontmatter layer, the linter gate, the fence gate,
the census gate, the trigger gate and the self-test in one pass, and proves the pipeline
before the bulk rewrite starts.
  </action>
  <verify>
    <automated>bash /workspaces/.planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/gates.sh</automated>
    <automated>python3 /home/vscode/.claude/skills/asd-ste100/scripts/ste-lint.py /workspaces/.claude/skills/devtest-triage/SKILL.md | tail -3</automated>
    <automated>python3 /workspaces/.claude/skills/devtest-triage/scripts/test_supersede.py</automated>
  </verify>
  <done>
`gates.sh` exists and runs. `skill-before.txt` holds the pre-edit skill file and the fence
baseline matches the pinned sha256. The linter's hard count has dropped from 23 to 20 (the two
long-sentence findings and one synonym-rotation finding on line 3 are gone) and no new hard
finding has appeared. The self-test still exits 0 with 6/6. The description holds all seven
triggers, states the supersede outcome as an explicit `when` clause, and is still one physical
line. Legs 9 and 10 print SKIP, and `gates.sh --final` exits non-zero on that SKIP — which is
how this task proves the two citation legs are wired and can fail.
  </done>
</task>

<task type="auto">
  <name>Task 2: Rewrite the body prose and reserve the six step tokens</name>
  <files>.claude/skills/devtest-triage/SKILL.md, .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/token-census.md</files>
  <action>
Work the body of the file. Nothing inside a code fence changes.

Split all sixteen semicolons into separate sentences. Nine sit in rationale cells. In a table
cell, two sentences in one cell is the correct shape — the cell keeps every clause it carried.
Never drop a clause to shorten a cell.

Remove every occurrence of each losing synonym, not only the flagged one, using the locked
substitution table in the planning facts. The counts to clear are two for the check-group verb,
one for the validate form, two for the delete verb, two for the correct adjective and three for
the fetch verb. Do not substitute the two verbs the item text suggested — both sit in a linter
group with a word that must stay, and either one creates a new hard violation.

Reserve the six step tokens. Rewrite every instance where one of them acts as an ordinary
English verb, using the substitution table. Where a sentence names an actual dev-test step,
write the step name as a backticked span — that is both the reader-facing convention and the
mechanical reason the linter stops seeing it. Do not rename a step token anywhere: not in a
table, not in a transcript, not in the routing rules, not in the section 3a legs. Leave the
quoted GitHub issue title alone. Leave the tool name alone. Leave the datasheet terms and the
`firestarter info` field names alone.

Fix the advisory passive-voice findings where naming the actor costs nothing and does not
change the claim. Leave a passive where the actor is genuinely unknown or irrelevant, and
leave every hedge exactly as strong as it is. The sentence about a chip working once on the
same build not undoing a failure carries the document's safety margin — rephrase it only if
the rewrite says exactly the same thing.

Change no command, flag, path, file name, label name or code identifier. The label names are
live GitHub labels that `scripts/devtest_issues.py` also uses.

Then write `token-census.md`. Generate the raw census with the harness, then annotate every
occurrence with one of the three allowed classes and a short reason. An occurrence that cannot
be classified is a defect, not a judgement call — go back and rewrite it.
  </action>
  <verify>
    <automated>bash /workspaces/.planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/gates.sh</automated>
    <automated>python3 /home/vscode/.claude/skills/asd-ste100/scripts/ste-lint.py /workspaces/.claude/skills/devtest-triage/SKILL.md; echo "lint exit=$?"</automated>
    <automated>python3 /workspaces/.claude/skills/devtest-triage/scripts/test_supersede.py; echo "selftest exit=$?"</automated>
  </verify>
  <done>
The linter exits 0 and its count line reports `0 hard, baseline 0`. The fence extract still
matches the baseline sha256 byte for byte. The self-test exits 0 with 6/6. All six prose
tables keep their column count and their row count, and every rationale cell still carries
every clause it carried before. `token-census.md` classifies every surviving step-token
occurrence, and none of them is classified as an ordinary verb.
  </done>
</task>

<task type="auto">
  <name>Task 3: Repair the line citations this edit displaced</name>
  <files>.planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/citation-remap.md, .planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/citations-derived.txt, .planning/milestones/v1.37-research/SUMMARY.md, .planning/milestones/v1.37-research/PITFALLS.md, .planning/milestones/v1.37-phases/187-answered-reports/187-RESEARCH.md, .planning/milestones/v1.37-phases/187-answered-reports/187-PATTERNS.md, .planning/milestones/v1.37-phases/187-answered-reports/187-CONTEXT.md, .planning/milestones/v1.36-phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-09-PLAN.md, .planning/milestones/v1.36-phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-07-PLAN.md</files>
  <reversibility rating="reversible">Edits archived milestone records, but every change is a line number inside a citation and is git-revertible in one commit.</reversibility>
  <action>
Build an old-to-new line map for the skill file by diffing `skill-before.txt` against the live
file. A range needs both endpoints mapped, and a constant offset is wrong wherever the rewrite
changed a paragraph's line count.

Enumerate the citations by running the gate's own leg 9, then work from `citations-derived.txt`.
Do not enumerate by hand and do not carry a total from this plan into the work. One citing line
can hold more than one target: a full citation and a backticked shorthand range that inherits
the file named earlier on the line. The planning-time measurement was 18 targets on 14 lines in
8 files, and it is a tripwire only — if the derivation disagrees, the derivation wins, and the
delta goes in `citation-remap.md`.

Write `citation-remap.md` as one machine-readable markdown table so the gate can parse it. The
columns, in this order: citing file, citing line, old target, shape, new target, disposition,
evidence. `shape` is full or shorthand. `disposition` is exactly one of `unmoved`, `retargeted`,
`anchor`, `pre-existing-stale`. Any other string fails the gate, so an unsure row cannot be
parked in a free-text value.

Round-trip oracle, and the gate enforces it rather than trusting the row: the skill text at the
old line in `skill-before.txt` must be byte-identical to the text at the new line in the live
file, at both endpoints of a range. Rewrite a citing file only for a row whose round trip
passes.

Two dispositions cannot round-trip on exact text. `anchor` is a citation whose target line this
task rewrote: retarget it by hand to the same semantic anchor, record which anchor and why, and
expect the gate to check that the nearest preceding heading is the same one on both sides.
`pre-existing-stale` is a citation already stale before this task began, which is out of scope:
the range `61-67` in `147-RESEARCH.md` is the known case, its old and new targets stay equal,
and `147-RESEARCH.md` stays unmodified.

**Prove leg 10 is reachable before you rely on it.** Copy `citation-remap.md` to a scratch
path outside the repository, add 1 to one `retargeted` row's new target, point the gate at the
corrupted copy, and record that it exited non-zero and named that row. A leg that has never
been seen to fail has proven nothing. Put that transcript in `citation-remap.md` under a
heading that says it is the reachability proof, and restore the real file afterwards.

If the rewrite displaced nothing, every row is `unmoved`, the gate still round-trips every one
of them, and no citing file changes.

Commit the skill-file rewrite and the citation rewrite in the same commit, so no intermediate
tree carries wrong citations.
  </action>
  <verify>
    <automated>bash /workspaces/.planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/gates.sh --final</automated>
    <automated>git -C /workspaces diff --quiet -- .planning/milestones/v1.32-phases/147-report-provenance-every-dev-test-report-names-its-firmware/147-RESEARCH.md; echo "147-RESEARCH untouched exit=$?"</automated>
    <automated>git -C /workspaces status --porcelain .planning/graphs/ | grep -c 'graph.json\|GRAPH_REPORT' || true</automated>
  </verify>
  <done>
`gates.sh --final` exits 0, so legs 9 and 10 ran rather than skipped. Leg 9 derived the citation
targets itself and found one `citation-remap.md` row per target, with no extra row. Leg 10
round-tripped every `unmoved` and `retargeted` row on exact text at both endpoints, and matched
the enclosing heading for every `anchor` row. The recorded reachability transcript shows leg 10
exiting non-zero on one corrupted row. The pre-existing stale range is recorded, and
`147-RESEARCH.md` is unmodified in git. No generated graph artifact was hand-edited.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| SKILL.md prose to a downstream agent | The rewritten instructions are executed by an agent with `gh` write access |
| SKILL.md to the public tracker | That agent closes and labels issues in a community repository |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-idk-01 | Tampering | The section 3a three-leg supersede rule and the do-not-close-a-FAIL paragraph | high | mitigate | Rationale columns and hedges are preserved verbatim in substance. A semicolon split is allowed; compressing a rationale is not. `test_supersede.py` pins the three legs and must stay green. |
| T-idk-02 | Tampering | Label names, commands, flags and paths | medium | mitigate | No command, flag, path, file name, label name or identifier changes. `gates.sh` asserts the repository slug is the current one and the pre-rename slug is absent. |
| T-idk-03 | Repudiation | Code fences that are verbatim tool transcripts, including two frozen fixtures | high | mitigate | Fence-only sha256 pinned from the working tree at task start and re-checked by every task's verify leg. |
| T-idk-04 | Information disclosure | The step tokens an agent routes on | medium | mitigate | The six tokens are reserved for step names. `token-census.md` classifies every surviving occurrence and the gate rejects any classified as an ordinary verb. |
| T-idk-05 | Tampering | `citation-remap.md` and the archived milestone records it rewrites | medium | mitigate | A wrong remap silently points an archived record at unrelated text. Leg 10 re-derives the round trip from `skill-before.txt` and the live file on exact text, so the row is checked rather than believed. The leg is proven to fail on a corrupted row before the task relies on it. |
| T-idk-06 | Repudiation | The citation enumeration itself | medium | mitigate | A hard-coded total hides a target the enumeration missed, and one citing line can carry several targets. Leg 9 derives the target list at run time and requires one row per derived target. No total is read from the plan. The enumerator excludes this task's own directory, so it cannot count its own output. |
</threat_model>

<verification>
Run `gates.sh --final`. It is the single objective gate and it wraps all ten legs. Without
`--final` the two citation legs may print SKIP, which is correct only while task 3 is unstarted.

Read `token-census.md` and `citation-remap.md` before declaring done — both are acceptance
artifacts, not notes. `citation-remap.md` must carry the leg 10 reachability transcript.

Read the final `git diff` of the skill file end to end. The rewrite is the deliverable and the
diff is the only place to see that a rationale survived rather than being compressed.
</verification>

<success_criteria>
- `ste-lint.py` on the skill file exits 0 and its count line reports `0 hard, baseline 0`.
- The fence-only extract still has sha256 `385873372be3d9fdf307511869ca494700b194c62d8225913b398c802a496735`.
- `scripts/test_supersede.py` exits 0 with 6/6.
- `token-census.md` classifies every step-token occurrence outside fences, and none is an ordinary verb.
- The frontmatter description holds all seven trigger phrases, is one physical line, and states the supersede outcome as an explicit `when` clause.
- Six prose tables, with column counts 3, 2, 3, 3, 4, 2 and row counts 5, 6, 3, 11, 10, 13.
- `gates.sh --final` exits 0, so the two citation legs ran and did not skip.
- `citation-remap.md` carries exactly one row per citation target that gate leg 9 derived at run
  time. No step of this work reads a citation total from this plan.
- Gate leg 10 round-tripped every `unmoved` and `retargeted` row on exact text at both endpoints,
  and the recorded transcript shows that leg exiting non-zero on a corrupted row.
</success_criteria>

<output>
Create `.planning/quick/260915-idk-rewrite-claude-skills-devtest-triage-ski/260915-idk-SUMMARY.md` when done.
Record in it: the before and after linter counts, the fence sha on both sides, the substitution
table as actually applied, any sentence kept long on purpose and the precision that would have
been lost, and the citation displacement measurement. Record the citation-target total that leg 9
derived, next to the planning-time tripwire of 18, and explain any delta. Record the leg 10
reachability transcript, or point at it in `citation-remap.md`.
</output>
