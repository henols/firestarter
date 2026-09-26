---
phase: quick-260915-idj
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .claude/skills/devtest-rootcause/SKILL.md
autonomous: true
requirements: [260915-idj]

estimate:
  tokens: 43000
  raw_tokens: 86000
  tasks: 3
  confidence: high

must_haves:
  truths:
    - "ste-lint.py on the skill file exits 0 and reports 0 hard violations."
    - "The firmware path variable in the setup block names a directory that exists."
    - "The four-line page-size exception blockquote is byte-identical to its pre-task content."
    - "Every code fence except the one permitted variable assignment is byte-identical to its pre-task content."
    - "The skill's own decode-table drift check still exits 0."
    - "All six prose tables keep their rationale column and their row count."
    - "The frontmatter description keeps every trigger phrase and stays on one line."
  artifacts:
    - .claude/skills/devtest-rootcause/SKILL.md
  key_links:
    - "SKILL.md setup block -> firestarter_fw submodule directory (11 downstream $FW references)"
    - "SKILL.md page-size exception blockquote -> FROZEN, because phase 194 is rewriting the mechanism it describes"
    - "SKILL.md frontmatter description -> skill trigger matching"
---

<objective>
Rewrite `.claude/skills/devtest-rootcause/SKILL.md` prose in Strict ASD-STE100, and repair
the one factual defect that is safe to repair today.

Purpose: This file is an agent-facing instruction document. A downstream agent with Write
access parses it without a person to resolve ambiguity. The firmware path reference in it
is wrong today, and it breaks 11 downstream path references.

Scope decision, made by the operator during planning: the page-size exception blockquote
is OUT OF SCOPE and is FROZEN. An earlier draft of this plan repaired a line number in it.
That repair is now withdrawn. The paragraph is obsolete in a larger way than a line number
(see the facts block), and the phase that made it obsolete is still running. The operator
decided that the paragraph gets struck later, after phase 194 settles, and NOT in this
task. This plan therefore holds those four lines byte-identical and makes no claim about
`build_db.py` at all.

Output: The same file, with 0 hard STE violations, the firmware path repaired, the
page-size blockquote unchanged, and every fact, hedge, rationale column and code fence
preserved.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/workspaces/CLAUDE.md
@/home/vscode/.claude/skills/asd-ste100/SKILL.md
@/workspaces/.claude/skills/devtest-rootcause/SKILL.md

Read the linter's rule tables directly before Task 2. `SYNONYM_GROUPS` is at
`/home/vscode/.claude/skills/asd-ste100/scripts/ste-lint.py` lines 50-61, and the
regex rule table is at lines 26-40. Those lists are the authority on which words clash,
not this plan.

Do NOT read `/workspaces/.planning/STATE.md`. It is 546 KB on one long line and is not
load-bearing for this task.
</context>

<facts_established_during_planning>
Measured, not assumed. Re-measure anything you intend to rely on.

- Baseline: `39 violations (23 hard, baseline 0)`, linter exit code 1.
- The 23 hard violations are 15 `semicolon`, 6 `synonym-rotation`, 2 `long-sentence`.
  There are ZERO `noun-cluster` findings. Passive voice (15) and present perfect (1) are
  advisory and never fail the run.
- "Hard" means `level == "advisory-free"` in the JSON output. `--json` also emits
  `hard_count`. The linter exits 1 when `hard_count > baseline`, so **exit code 0 is the
  gate**, and it carries no literal that a rewrite could self-invalidate.
- The linter skips code fences (source lines 240-244) and strips inline backtick spans
  (line 247). It scans markdown table cells as separate segments.
- The firmware submodule path is `firestarter_fw` per `.gitmodules`.
  `/workspaces/firestarter` does not exist. `/workspaces/firestarter_fw` does. Re-measured
  after the withdrawal below, and still true.
- **WITHDRAWN SCOPE — the page-size exception blockquote.** An earlier draft of this plan
  recorded `_PAGE_SIZE_BY_PART` at `build_db.py` line 102 and told Task 1 to repair the
  document's `build_db.py:114` citation to `:102`. That measurement was accurate when it was
  taken and is false now. Commit `859109d` in `firestarter_app`
  ("feat(194-01): emit the real page size for every upstream-native 0x05 row") REMOVED the
  symbol. `grep -n '_PAGE_SIZE_BY_PART' firestarter_app/tools/build_db.py` now exits 1 and
  prints nothing. Page size now derives from `infoic_page_size_raw` at `build_db.py:666`,
  which is precisely the seam the blockquote itself names as the principled alternative.
  So the paragraph does not carry a stale line number. It describes a mechanism that no
  longer exists. Repairing `:114` to `:102` would write a confidently false citation that
  points at a symbol that is gone, which is worse than the staleness it set out to repair.
- **A second reason not to touch it: another session is executing phase 194 in this same
  working tree right now.** The generator's page-size mechanism is mid-change. Any sentence
  this task writes about that mechanism could be wrong again within minutes. A frozen
  paragraph cannot be wrong in a new way.
- **Freezing lines 63-66 does not block the 0-hard target. Measured, not assumed.** The
  linter reports 39 findings across 34 distinct lines, and NONE of them is in 63-66. A
  separate scan for every `SYNONYM_GROUPS` member inside those four lines, applied to the
  backtick-stripped text and with the linter's own `\b WORD (?:s|es|ed|d|ing)? \b`
  inflection matching, returns NONE. That second scan matters: the synonym rule re-points
  to the next occurrence when an earlier one is removed, so a losing word sitting in the
  frozen paragraph would make 0-hard unreachable. No group member is there, so no Task 2
  rewrite can re-point a finding into the frozen lines. There is also no semicolon there.
- **The frozen-block gate was proven in both directions during planning.** Against the
  current file it prints `frozen block occurrences: 1` and exits 0. Against a copy mutated
  by exactly the withdrawn `:114` to `:102` edit it prints `0` and exits 1. It is a
  positive exact-text assertion with an `== 1` count, so it cannot fail open, and it is
  anchored on content rather than on a line number, so it survives line shifts from
  sentence splitting earlier in the file.
- **`FW=$ROOT/firestarter` (line 27) is INSIDE a ```bash fence.** The rewrite rule and the
  repair rule collide on exactly this line. Task 1 resolves the collision with one
  enumerated exception and no other.
- The file is ALREADY dirty in the working tree: three unrelated
  `henols/firestarter_prom` -> `henols/firestarter` edits, all inside fences. The fence
  baseline must therefore be snapshotted from the **working tree**, never from HEAD.
- Six tables sit outside fences, at lines 40, 149, 246, 318, 363, 415, with 9, 10, 4, 5,
  4 and 16 pipe-prefixed lines each (48 total). Re-measured after commit `859109d`, and
  unchanged. A seventh table at line 348 is inside a fence, so the fence gate already
  protects it.
- `infoic_lookup.py --check` exits 0, and `seed_debug_session.py --help` exits 0. Both were
  re-measured after commit `859109d` changed `build_db.py`, because `--check` reads that
  generator as text. `--check` is the only decode-table self-test the skill owns.
- The setup block holds `ROOT/firestarter` and `ROOT/firestarter_app`, and the document
  holds 11 `$FW` references. Re-measured, and unchanged.
</facts_established_during_planning>

<tasks>

<task type="tracer">
  <name>Task 1: Land the firmware path repair through the full proof loop</name>
  <files>.claude/skills/devtest-rootcause/SKILL.md</files>
  <read_first>
    `/workspaces/.gitmodules`, for the firmware submodule path.

    Do NOT read `/workspaces/firestarter_app/tools/build_db.py`. This plan makes no claim
    about that file. Another session is editing it right now.
  </read_first>
  <action>
This is the thin end-to-end slice. It touches every gate the later tasks rely on
(fence snapshot, frozen-block check, path grep, self-test) while changing only one line, so
a broken harness is found now rather than after a full prose rewrite.

Step 1, BEFORE editing anything: snapshot the fenced blocks from the current working
tree. Write the extractor to a fixed path and keep both for Task 3:

    mkdir -p /tmp/260915-idj
    cat > /tmp/260915-idj/extract.py <<'PY'
    import sys
    inf = False
    for line in open(sys.argv[1]).read().split("\n"):
        if line.strip().startswith("```"):
            inf = not inf
            print("FENCE", line)
            continue
        if inf:
            print("|", line)
    PY
    cd /workspaces && python3 /tmp/260915-idj/extract.py \
      .claude/skills/devtest-rootcause/SKILL.md > /tmp/260915-idj/fences.before.txt

Snapshot from the working tree, NOT from HEAD. Three unrelated repo-rename edits already
sit in those fences in the working tree. They must not show up as a delta.

This snapshot is a precondition for the Task 3 gate. If `fences.before.txt` is written
after any edit, the gate passes while proving nothing.

Step 2: change the firmware path assignment so it names `firestarter_fw`, matching the
submodule path in `.gitmodules`. This is the ONLY edit permitted inside any fence in this
whole plan. It repairs 11 downstream `$FW` references.

Step 3: add one short sentence to the prose paragraph that sits ABOVE the setup fence,
stating that `firestarter` is now the name of the meta repository itself. That name
collision is why the old path looked plausible. Put this OUTSIDE the fence. Adding a line
inside the fence would break the fence-invariance gate in Task 3. Skip this step if it
does not read naturally there.

Step 4: run the frozen-block gate now, BEFORE any prose rewriting, and see it print
`frozen block occurrences: 1` and exit 0. The gate is the third `automated` leg below. Run
it here so that it is known to be reachable and green from the start. A gate first seen at
the end of a task proves nothing about the state it was supposed to protect.

**The page-size exception blockquote is OUT OF SCOPE and FROZEN.** These four lines, which
sit under the "The proof rule" heading and start with `> One exception exists:`, must be
byte-identical when this plan finishes:

    > One exception exists: `_PAGE_SIZE_BY_PART` (`build_db.py:114`) adds `page_size` from
    > `[CITED:]` **datasheets**, not from `infoic.xml` — the exact shape this rule forbids.
    > Do not extend it or add siblings to it. Upstream carries `infoic_page_size_raw`, which
    > is the principled seam if page size ever needs revisiting.

Do not repair the line number in them. Do not rewrite them for STE. Do not strike them. Do
not annotate them. The reason is in the facts block: the symbol they name no longer exists,
so any repair of that citation would be a confidently false statement, and the phase that
removed the symbol is still running in this working tree. The operator decided that this
paragraph gets struck in separate work, after phase 194 settles.

Note what the gate does and does not assert. It asserts that four lines of SKILL.md keep
their exact bytes. It makes NO claim that the citation inside them is accurate. Holding
known-obsolete text unchanged is the deliberate outcome here.

Change no other command, flag, path, file name, function name or identifier.
  </action>
  <verify>
    <automated>cd /workspaces && test -d /workspaces/firestarter_fw && [ "$(/usr/bin/grep -o 'ROOT/firestarter[a-z_]*' .claude/skills/devtest-rootcause/SKILL.md | sort -u | tr '\n' ' ')" = "ROOT/firestarter_app ROOT/firestarter_fw " ]</automated>
    <automated>cd /workspaces && python3 .claude/skills/devtest-rootcause/scripts/infoic_lookup.py --check</automated>
    <automated>cd /workspaces && python3 - <<'PY'
import sys
F = ".claude/skills/devtest-rootcause/SKILL.md"
FROZEN = (
"> One exception exists: `_PAGE_SIZE_BY_PART` (`build_db.py:114`) adds `page_size` from\n"
"> `[CITED:]` **datasheets**, not from `infoic.xml` \u2014 the exact shape this rule forbids.\n"
"> Do not extend it or add siblings to it. Upstream carries `infoic_page_size_raw`, which\n"
"> is the principled seam if page size ever needs revisiting."
)
n = open(F).read().count(FROZEN)
print("frozen block occurrences:", n)
sys.exit(0 if n == 1 else 1)
PY</automated>
  </verify>
  <done>
The setup block assigns the firmware path to a directory that exists, and no
`ROOT/firestarter` reference without the `_fw` or `_app` suffix remains. The frozen-block
gate was run before any prose edit and printed `frozen block occurrences: 1`. The fence
delta against `fences.before.txt` is exactly one line pair, and that pair is the firmware
path assignment. The drift check exits 0.
  </done>
</task>

<task type="auto">
  <name>Task 2: Rewrite the document body in Strict ASD-STE100</name>
  <files>.claude/skills/devtest-rootcause/SKILL.md</files>
  <read_first>
    `SYNONYM_GROUPS` at `/home/vscode/.claude/skills/asd-ste100/scripts/ste-lint.py`
    lines 50-61. That list is the authority on which words clash. Read it before you
    rewrite. Also read the Strict mode rules in
    `/home/vscode/.claude/skills/asd-ste100/SKILL.md`.
  </read_first>
  <action>
Apply the `asd-ste100` skill in **Strict** mode to the prose body. Leave frontmatter line
3 alone. Task 3 owns it.

Clear the 15 semicolon findings by splitting each into two sentences. Splitting a
semicolon into two sentences is the goal. Compressing a rationale away is not permitted.
Shorter never wins over unambiguous.

Clear the synonym-rotation findings. For each group in `SYNONYM_GROUPS`, pick ONE member
and use it everywhere in the file. Recommended survivors, chosen to match the domain and
the flag names already in the document: `check`, `fix`, `start`, `fetch`, `change`, `use`,
`show`, `stop`. Remove every other member of those groups from the prose.

Three mechanics of this rule will cost you passes if you do not know them:

1. The linter records only the FIRST occurrence of each group member. Fixing the line it
   names is often not enough. The finding then re-points to the next occurrence of the
   same word. Remove the losing word file-wide.
2. A rewrite can INTRODUCE a new clash by reaching for a word in another group. Re-run the
   linter after every pass.
3. Inflections count. The matcher is `\bWORD(?:s|es|ed|d|ing)?\b`.

Two traps in this specific file:

- **A verbatim quotation near line 220.** The italic text that quotes `gsd-debugger`'s own
  entry flow is a quotation of another document. It must stay byte-identical, or the
  document starts telling a lie about what that agent does. Its group clash is with the
  word near line 209 that describes how agents behave in this devcontainer. Fix line 209
  instead, and use `run` there.
- **An adjective near line 425.** The one-word cell in the Troubleshooting table uses a
  losing word in its adjective sense, not as a verb. The linter is purely lexical and
  flags it anyway. Use `Right` there.

Preserve modality exactly. A hedge is content. "may have failed" must never become
"failed". "A difference is not automatically a bug" carries the safety margin of the whole
section and keeps its hedge.

Preserve every rationale column, caveat and disclosed limitation in substance. Those
columns are what stop a downstream agent from reasoning its way around a rule.

Passive voice (15) and present perfect (1) are advisory and never fail the run. Fix them
where the fix costs nothing. Keep "have proven" near line 384 if current relevance is the
point there, which is what the STE skill's own exception covers.

**Skip the page-size exception blockquote.** It is the four-line quoted paragraph under
"The proof rule", starting `> One exception exists:`. Task 1 states the rule and the
reason. It applies with equal force here: an STE sweep naturally runs over the whole body,
and this paragraph is carved out of that sweep. Leave its bytes alone.

Skipping it is safe for your target, and this was measured rather than assumed. No linter
finding of any level sits in those four lines, and no `SYNONYM_GROUPS` member appears in
them at all. So no word you retire elsewhere can re-point a synonym finding into the frozen
paragraph. The second `automated` leg below runs the frozen-block gate. Run it after every
pass, together with the linter.

Change no command, flag, path, file name, function name or identifier. Change nothing
inside any fence. Task 1 already made the single permitted fence edit.
  </action>
  <verify>
    <automated>cd /workspaces && python3 - <<'PY'
import json, subprocess, sys
F = ".claude/skills/devtest-rootcause/SKILL.md"
L = "/home/vscode/.claude/skills/asd-ste100/scripts/ste-lint.py"
d = json.loads(subprocess.run(["python3", L, "--json", F], capture_output=True, text=True).stdout)
bad = [v for v in d["violations"] if v["level"] == "advisory-free" and v["line"] != 3]
for v in bad:
    print("BODY HARD:", v["line"], v["rule"], v["match"])
print("body hard count:", len(bad))
sys.exit(1 if bad else 0)
PY</automated>
    <automated>cd /workspaces && python3 - <<'PY'
import sys
F = ".claude/skills/devtest-rootcause/SKILL.md"
FROZEN = (
"> One exception exists: `_PAGE_SIZE_BY_PART` (`build_db.py:114`) adds `page_size` from\n"
"> `[CITED:]` **datasheets**, not from `infoic.xml` — the exact shape this rule forbids.\n"
"> Do not extend it or add siblings to it. Upstream carries `infoic_page_size_raw`, which\n"
"> is the principled seam if page size ever needs revisiting."
)
n = open(F).read().count(FROZEN)
print("frozen block occurrences:", n)
sys.exit(0 if n == 1 else 1)
PY</automated>
  </verify>
  <done>
Zero hard violations remain outside frontmatter line 3. Every rationale column is intact.
Every fence is unchanged since Task 1. The page-size exception blockquote is byte-identical
and the frozen-block gate exits 0.
  </done>
</task>

<task type="auto">
  <name>Task 3: Rewrite the frontmatter description and converge the whole file</name>
  <files>.claude/skills/devtest-rootcause/SKILL.md</files>
  <action>
Frontmatter line 3 carries 2 of the 2 long-sentence findings, at 53 and 50 words against
a 25-word cap, plus one synonym-rotation finding. Split both sentences.

This line is the skill's trigger surface. A downstream agent matches a user request
against it to decide whether to load this skill at all. Losing a trigger phrase silently
disables the skill for that phrasing, so treat trigger coverage as a fact to preserve,
exactly like a hedge.

Three mechanical constraints on this line:

1. It must stay ONE line. The file must keep the shape: line 1 `---`, line 2
   `name: devtest-rootcause`, line 3 starting `description: `, line 4 `---`. More
   sentences are fine. More lines are not.
2. `name: devtest-rootcause` must not change at all. It is the skill's identity.
3. The value is an unquoted YAML scalar today. A colon followed by a space would break
   it. `fix:committed` is safe because it has no space. If you need a colon and a space,
   wrap the whole value in double quotes, as the `asd-ste100` skill's own frontmatter
   does.

The losing word in the `fix` group appears on this line. Removing it costs the literal
phrase about correcting the generator. Keep the token `database generator` in the line so
that trigger still matches.

Then run the linter over the whole file and drive it to exit 0. Iterate. Every pass can
introduce a new synonym clash, so re-run after each edit until the run is clean.

The page-size exception blockquote stays frozen through every convergence pass. Task 1
states the rule and the reason. The fourth `automated` leg below is the final assertion on
it.
  </action>
  <verify>
    <automated>cd /workspaces && python3 - <<'PY'
import json, subprocess, sys
F = ".claude/skills/devtest-rootcause/SKILL.md"
L = "/home/vscode/.claude/skills/asd-ste100/scripts/ste-lint.py"
fail = []
r = subprocess.run(["python3", L, F], capture_output=True, text=True)
if r.returncode != 0:
    fail.append("linter exit %d, not 0" % r.returncode)
print(r.stdout.strip().split("\n")[-2] if r.stdout else "")
lines = open(F).read().split("\n")
if lines[0] != "---" or lines[1] != "name: devtest-rootcause" or not lines[2].startswith("description: ") or lines[3] != "---":
    fail.append("frontmatter shape broken")
TRIGGERS = ["dev test", "chip_database.json", "EPROM", "root-cause", "pinout",
            "protocol", "VPP", "database generator", "datasheet", "firmware",
            "host app", "at28c256", "w27e257", "fix:committed", "fix:released"]
missing = [t for t in TRIGGERS if t.lower() not in lines[2].lower()]
if missing:
    fail.append("lost triggers: %s" % missing)
inf, tables, cur = False, [], None
for line in lines:
    if line.strip().startswith("```"):
        inf = not inf
        continue
    if inf:
        continue
    if line.startswith("|"):
        cur = (cur or 0) + 1
    elif cur:
        tables.append(cur)
        cur = None
if cur:
    tables.append(cur)
if tables != [9, 10, 4, 5, 4, 16]:
    fail.append("table rows changed: %s, expected [9, 10, 4, 5, 4, 16]" % tables)
for f in fail:
    print("FAIL:", f)
sys.exit(1 if fail else 0)
PY</automated>
    <automated>cd /workspaces && S=/tmp/260915-idj && test -s $S/fences.before.txt && python3 $S/extract.py .claude/skills/devtest-rootcause/SKILL.md > $S/fences.after.txt && (diff $S/fences.before.txt $S/fences.after.txt > $S/fences.delta || true) && cat $S/fences.delta && [ "$(/usr/bin/grep -c '^[<>]' $S/fences.delta)" = "2" ] && /usr/bin/grep -qxF '< | FW=$ROOT/firestarter' $S/fences.delta && /usr/bin/grep -qxF '> | FW=$ROOT/firestarter_fw' $S/fences.delta</automated>
    <automated>cd /workspaces && python3 .claude/skills/devtest-rootcause/scripts/infoic_lookup.py --check && python3 .claude/skills/devtest-rootcause/scripts/seed_debug_session.py --help > /dev/null</automated>
    <automated>cd /workspaces && python3 - <<'PY'
import sys
F = ".claude/skills/devtest-rootcause/SKILL.md"
FROZEN = (
"> One exception exists: `_PAGE_SIZE_BY_PART` (`build_db.py:114`) adds `page_size` from\n"
"> `[CITED:]` **datasheets**, not from `infoic.xml` — the exact shape this rule forbids.\n"
"> Do not extend it or add siblings to it. Upstream carries `infoic_page_size_raw`, which\n"
"> is the principled seam if page size ever needs revisiting."
)
n = open(F).read().count(FROZEN)
print("frozen block occurrences:", n)
sys.exit(0 if n == 1 else 1)
PY</automated>
  </verify>
  <done>
The linter exits 0 and reports 0 hard violations. The frontmatter keeps its shape, its
name and all 15 trigger tokens. The six tables keep their row counts. The fence delta
against the Task 1 snapshot is exactly the two lines of the firmware path repair. The
page-size exception blockquote is byte-identical to its pre-task content. The drift check
exits 0.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| SKILL.md -> `gsd-debugger` | This document supplies the guardrails for an agent that HAS Write access and does not otherwise know `chip_database.json` is generated |
| SKILL.md -> skill loader | The frontmatter description decides whether the skill loads for a request |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-idj-01 | Tampering | fix-surface rules and rationale columns | high | mitigate | Task 2 forbids compressing a rationale away. Task 3 asserts all six tables keep their exact row counts |
| T-idj-02 | Tampering | code fences holding real tool transcripts | high | mitigate | Task 1 snapshots fences before editing. Task 3 asserts the delta is exactly the two lines of the one permitted repair |
| T-idj-03 | Denial of Service | frontmatter description | medium | mitigate | Task 3 asserts the frontmatter shape and greps for all 15 trigger tokens, so the skill cannot silently stop loading |
| T-idj-04 | Information Disclosure | modality and hedges | medium | mitigate | Task 2 names hedge preservation as a hard rule. The linter never flags hedges, so this one needs the human-readable rule |
| T-idj-05 | Tampering | the one repaired reference | medium | mitigate | Task 1 reads the firmware path from `.gitmodules` rather than from this plan, and asserts it by grep against the real tree |
| T-idj-06 | Tampering | the page-size exception blockquote | high | mitigate | Another session removed the symbol it names, mid-plan. A repair here would write a false citation into a document that a Write-capable agent obeys. All three tasks carve the paragraph out. An exact-text gate with an `== 1` count asserts it in each of them |

No package manager install runs in this plan, so no supply-chain gate applies.
</threat_model>

<verification>
Run from `/workspaces`.

1. `python3 /home/vscode/.claude/skills/asd-ste100/scripts/ste-lint.py .claude/skills/devtest-rootcause/SKILL.md` exits 0. Paste the count line. Baseline was `39 violations (23 hard, baseline 0)`.
2. The fence delta against the Task 1 snapshot is exactly two lines, and both are the firmware path repair.
3. `python3 .claude/skills/devtest-rootcause/scripts/infoic_lookup.py --check` exits 0.
4. `/workspaces/firestarter_fw` exists, and no bare `ROOT/firestarter` reference remains in the document.
5. The frozen-block gate prints `frozen block occurrences: 1` and exits 0. Run nothing against `build_db.py` for this leg. The gate asserts the bytes of SKILL.md only, and this plan makes no claim about the generator.
6. The six prose tables report row counts `[9, 10, 4, 5, 4, 16]`.
7. `git diff .claude/skills/devtest-rootcause/SKILL.md` shows no change to any command, flag, path, file name, function name or identifier other than the one firmware path repair.
8. `git diff` shows no change at all inside the page-size exception blockquote.
</verification>

<success_criteria>
- The linter reports 0 hard violations and exits 0.
- The repaired firmware path resolves against the real tree.
- The page-size exception blockquote is byte-identical to its pre-task content.
- Every code fence is byte-identical to its pre-task content, except the one firmware path assignment.
- Every rationale column survives with the same number of rows.
- Every hedge and scope qualifier survives.
- The frontmatter keeps its name, its one-line description and all 15 trigger tokens.
- The skill's drift check still exits 0.
</success_criteria>

<output>
Create `/workspaces/.planning/quick/260915-idj-rewrite-claude-skills-devtest-rootcause-/260915-idj-SUMMARY.md` when done.

Record in it: the before and after linter count lines, the fence delta, the frozen-block
gate output, and any phrasing kept long on purpose to protect a hedge or a rationale.

Record also that the page-size exception blockquote was left unchanged on purpose, and
that it is now known to describe a mechanism that no longer exists. That paragraph is
scheduled for separate work after phase 194 settles. Do not let a reader of this SUMMARY
conclude that the paragraph was reviewed and found accurate.
</output>