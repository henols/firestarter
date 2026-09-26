---
phase: quick-260916-tea
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - VALIDATED-EPROMS.md
  - .claude/skills/devtest-triage/SKILL.md
  - .claude/skills/devtest-triage/scripts/devtest_issues.py
  - .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py
  - .claude/skills/devtest-triage/fixtures/dev-test-sst39sf040-log-capture-first.md
autonomous: true
requirements: [260916-tea]

estimate:
  tokens: 45000
  raw_tokens: 90000
  tasks: 2
  confidence: high

must_haves:
  truths:
    - "The four chips validated during triage — TMS27C512 (#72), W27C040 (#87), MX27C4000 (#74, #75) and the re-validated W29C040 (#48, #88) — are recorded in the committed ledger on `beta`'s line of descent, not only in a working tree."
    - "The ledger's `## Notes` section carries no GSD process reference, and SKILL.md states that rule for every future Notes entry."
    - "`devtest_issues.py` finds the embedded report in a body where one or more fenced blocks of another language precede the report block, whatever those blocks contain."
    - "Detection still requires a parsed JSON object carrying `schema_version`; the `json` info string alone never qualifies a block, so a schema bump needs no code change."
    - "Issue #90 renders as a parseable report — `list` prints no `(no JSON report)` note for it and `show 90` prints `schema 2.2` and routes it FAIL on write and verify."
    - "The regression is proven executable, not asserted: a mutant carrying the pre-fix pattern misses the new fixture's report while the intact module finds it."
    - "The three pre-existing fixtures are byte-identical to their pre-task content and appear in no commit this plan makes."
    - "The full skill suite passes on its own exit status with more than the 68 tests measured before this plan."
    - "No new comment line enters either Python file, and no source file gains a phase number, plan id, `.planning/` path or decision id."
    - "The incidental working-tree noise (`.vscode/*`, `.devcontainer/devcontainer.json`, `.planning/graphs/.last-build-status.json`, `anything.txt`, `tmp/`, `firestarter.wiki/`, `setup-claude-pr-policy.sh`) is in no commit, and neither submodule gitlink moves."
  artifacts:
    - VALIDATED-EPROMS.md
    - .claude/skills/devtest-triage/fixtures/dev-test-sst39sf040-log-capture-first.md
    - .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py
  key_links:
    - "`FENCE_RE` -> `extract_report`'s block loop — the single enumerator of candidate blocks; the only thing this fix changes, and the reason every downstream command (`list`, `show`, `fold`, `is_devtest`) recovers at once."
    - "`extract_report` -> `cmd_list`'s `(no JSON report)` note and `cmd_show`'s hard exit 1 — the two places the defect surfaces to a human, both as a misleading claim about the reporter."
    - "new fixture -> `_mutation.load_mutant` anchor on the `FENCE_RE` pattern text — the permanent, runnable RED demonstration."
---

<objective>
Land the stranded dev-test output on this branch, and fix the report-detection defect that
makes every report produced by current builds read as though the reporter omitted the JSON
block.

Purpose: two unrelated halves of the same complaint. Four chips were validated during triage
and the ledger rows never left the working tree, so none of that reached `beta`. Separately,
`dev test` now emits a captured-log fenced block before the report block, and the parser's
fence regex cannot start at a non-`json` info string — it resynchronises on the wrong fence
and finds one empty block, so the report is never seen. The failure is silent and blames the
reporter.

Output: one commit carrying the regenerated ledger plus the SKILL.md Notes rule, and one
commit carrying a line-anchored fence enumerator, a new hand-authored fixture in issue #90's
shape, and a mutation-guarded regression test that fails against the pre-fix pattern.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/workspaces/CLAUDE.md
@/workspaces/.claude/skills/devtest-triage/SKILL.md
@/workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py
@/workspaces/.claude/skills/devtest-triage/scripts/tests/_mutation.py
@/workspaces/.claude/skills/devtest-triage/fixtures/dev-test-error-codes-populated.md
</context>

<design_decisions>

Settled during planning against the real files and the real issue body. Do not re-litigate
them; implement them.

## DD-1. Why the current pattern fails, measured

The live pattern is `FENCE_RE` on line 74 of `devtest_issues.py`. Walk it over issue #90's
real body, which is `...captured log lines (captured=6, dropped=0, truncated=0):` then a
fenced `text` block of six log lines, then the fenced `json` report block:

At the `text` opener the optional `json` alternative matches empty, then `\s*` matches empty
because `t` is not whitespace, then the required newline cannot match `t` — so no match
starts there. The engine advances and next succeeds at the **closing** fence of the `text`
block, where the following blank line satisfies the newline requirement; the lazy body then
captures the empty span up to the `json` block's **opening** fence. Scanning resumes past
that opener, so the report block is consumed as a delimiter and never offered to
`json.loads`.

Measured during planning on the live body of issue #90: `findall` returns exactly one block,
of length 0. `extract_report` therefore returns `None`, `cmd_list` prints `(no JSON report)`
and `cmd_show` exits 1 with `JSON report: no`. Every report from current builds parses this
way.

## DD-2. The fix is the enumerator, and only the enumerator

Replace the pattern with a line-anchored one that accepts any info string. The compiled
pattern becomes ````r"^```[^\n]*\n(.*?)^```"```` and the flags become
`re.DOTALL | re.MULTILINE`.

Both fences must sit at the start of a line, and everything up to the first newline after the
opening fence is discarded as the info string. `extract_report`'s loop is otherwise
**unchanged**: every block is still tried in document order, and a block still qualifies only
when `json.loads` yields a dict carrying `schema_version`. The `json` info string is never
required and never sufficient, so a schema bump still needs no code change.

Measured during planning with that pattern: on issue #90's real body, two blocks (356 and
10443 characters) and the second parses to the schema `2.2` report; `show` then prints the
full step table and routes it `FAIL — write, verify`. On all three committed fixtures the
extracted report is identical to what the old pattern produced (schema `1.2`, `1.4`, `2.0`).
The three synthetic bodies the existing suite builds — the `not json at all` block followed
by a `json` block, the `foo: bar` block, and the 1.05 MB body of `x` — all keep their current
answers.

Do not add a comment above the line. Update `extract_report`'s existing docstring instead, so
it says the enumerator accepts any info string and that unrelated blocks may precede the
report. That docstring is an existing docstring being corrected, not new commentary.

## DD-3. The RED demonstration is a mutation guard, not a claim

This suite already proves each guard can fail by loading a mutated copy of the module
(`tests/_mutation.py`, four existing call sites in `test_devtest_issues.py`). Use the same
idiom: `load_mutant(MODULE_PATH, <the new pattern argument text>, <the pre-fix pattern
argument text>)`, then assert the mutant returns `None` for the new fixture while the intact
module returns the schema `2.2` report.

`load_mutant` asserts its anchor occurs exactly once in the source, so the anchor must be the
full argument text of the `re.compile` call on the `FENCE_RE` line — pattern literal and
flags — which is unique. Write both strings as raw Python literals so the backslash-n
sequences match the module source character for character.

## DD-4. The new fixture is hand-authored in #90's shape, and the three old ones stay frozen

Create `.claude/skills/devtest-triage/fixtures/dev-test-sst39sf040-log-capture-first.md`
modelled on the real body of issue #90 — not copied wholesale from it, matching the
hand-authored precedent of `dev-test-error-codes-populated.md`. It must carry, in this order:
the reporter's step table as prose, a `captured log lines (captured=N, dropped=0,
truncated=0):` line, a fenced `text` block of a few `[step] source LEVEL: message` lines, then
the fenced `json` report block. The report carries `schema_version` `2.2`, `generated`,
`dedup_fingerprint`, an `auto_capture` with `host_version` `3.0.0b44` and `fw_board_identity`
`3.0.0b31:leonardo`, `steps` with real `error_code` integers on the failing rows, and a
`log_capture` object whose entries mirror the text block.

Its leading header states it is hand-authored test data modelled on the shape of issue #90,
that it is not a real community report and is not evidence about SST39SF040, and that it must
not be regenerated from a live `to_dict()`. The header names the issue number and the
structural facts only — no phase number, no task or plan id, no `.planning/` path.

The three existing fixtures are inputs to other tests and two of them are deliberately pre-2.0
bodies whose own headers forbid regeneration. Do not open them for editing and do not let them
appear in any commit this plan makes.

## DD-5. Test wiring

`test_devtest_issues.py` has no fixture loader yet. Build the path from `__file__`, never the
cwd: `_SCRIPTS_DIR` is already the `scripts/` directory, so the fixtures live at
`os.path.join(os.path.dirname(_SCRIPTS_DIR), "fixtures", ...)`. Read with
`encoding="utf-8"`.

Add three cases to `TestUntrustedBodyParser`:

| Case | Asserts |
|---|---|
| report found behind a preceding `text` block | `extract_report` on the new fixture returns a dict whose `schema_version` is `2.2` and whose `dedup_fingerprint` matches the fixture |
| mutation guard | intact module finds that report; the mutant carrying the pre-fix pattern returns `None` for the same body |
| unclosed fence | a body with an opening fence and no closing fence returns `None`, promptly and without raising |

No new `#` comment line in either Python file — docstrings only, matching the surrounding
style.

</design_decisions>

<tasks>

<task type="auto">
  <name>Task 1: Commit the stranded ledger rows and the Notes rule</name>
  <files>VALIDATED-EPROMS.md, .claude/skills/devtest-triage/SKILL.md</files>
  <precondition>`git status --porcelain -- VALIDATED-EPROMS.md .claude/skills/devtest-triage/SKILL.md` prints two modified entries. If it prints nothing, the work is already committed — record that in the SUMMARY and skip to Task 2 rather than inventing a change.</precondition>
  <action>Commit the two tracked files that already hold this work, unedited. `VALIDATED-EPROMS.md` is a GENERATED file: do not hand-edit it, do not re-render it, and do not reorder its rows — the working-tree copy already passes `eprom_ledger.py check`, which is what makes it a valid fresh render. It adds the TMS27C512 (#72), W27C040 (#87) and MX27C4000 (#74, #75) rows, re-stamps W29C040 to host 3.0.0b44 / firmware 3.0.0b31 with issues #48 and #88, regenerates the three derived family tables, and strips a GSD process citation out of `## Notes`. `SKILL.md` already carries the matching +7-line rule under the ledger section forbidding GSD process references in Notes. Stage by explicit path only — `git add -- VALIDATED-EPROMS.md .claude/skills/devtest-triage/SKILL.md` — never `git add -A`, `git add .` or `git commit -a`, and never a path inside `firestarter_app/` or `firestarter_fw/`. The incidental noise in this tree stays untouched and uncommitted: the three `.vscode/*.json` files, `.devcontainer/devcontainer.json`, `.planning/graphs/.last-build-status.json`, and the untracked `anything.txt`, `tmp/`, `firestarter.wiki/` and `setup-claude-pr-policy.sh`. Neither submodule gitlink moves. Commit message: `docs(260916-tea): log four validated chips and ban process refs from ledger notes`. No AI attribution and no `Co-Authored-By` trailer.</action>
  <verify>
    <automated>python3 .claude/skills/devtest-triage/scripts/eprom_ledger.py check</automated>
    <automated>test "$(git show --format= --name-only HEAD | LC_ALL=C sort | tr '\n' ' ')" = ".claude/skills/devtest-triage/SKILL.md VALIDATED-EPROMS.md "</automated>
    <automated>FILES=$(git show --format= --name-only HEAD) && test -n "$FILES" && test "$(printf '%s\n' "$FILES" | /usr/bin/grep -c -e '\.vscode' -e 'devcontainer' -e 'last-build-status' -e 'firestarter_app' -e 'firestarter_fw' || true)" = "0"</automated>
    <automated>test "$(/usr/bin/grep -c -e '\.planning/' -e 'Phase [0-9]' VALIDATED-EPROMS.md || true)" = "0"</automated>
    <automated>test "$(git status --porcelain -- .vscode .devcontainer .planning/graphs/.last-build-status.json | wc -l)" -ge 1</automated>
  </verify>
  <done>One commit exists whose file list is exactly `VALIDATED-EPROMS.md` and `.claude/skills/devtest-triage/SKILL.md`. `eprom_ledger.py check` still reports the file matches a fresh render. The ledger's Notes carry no `.planning/` path and no phase citation. The five noise files are still dirty in the working tree, unstaged and uncommitted, and both submodule gitlinks are where they were.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Find the report block behind a preceding log-capture block</name>
  <files>.claude/skills/devtest-triage/fixtures/dev-test-sst39sf040-log-capture-first.md, .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py, .claude/skills/devtest-triage/scripts/devtest_issues.py, .claude/skills/devtest-triage/SKILL.md</files>
  <behavior>
    - A body whose report block is preceded by a fenced `text` block of captured log lines parses: `extract_report` returns the dict, `schema_version` is `2.2`, and the fingerprint matches the fixture.
    - The same body under the pre-fix pattern returns `None` — the mutant proves the test is load-bearing.
    - A body with an opening fence and no closing fence returns `None` without raising and without hanging.
    - The three existing parser tests keep their current answers: `not json at all` then a `json` block still yields the report; a block carrying only `foo` still yields `None`; a 1.05 MB body of `x` still yields `None` promptly.
    - `show --body-file` on the new fixture exits 0 and prints the schema, the host, the firmware identity and the resolved error names for the failing steps.
  </behavior>
  <action>Write the fixture and the three test cases FIRST, per DD-4 and DD-5, run the suite against the unmodified script, and record the observed failure text in the SUMMARY — then apply the fix. The fix is one line: replace `FENCE_RE`'s pattern and flags per DD-2 so both fences are line-anchored and any info string is accepted, and correct `extract_report`'s existing docstring to say so. Change nothing else in that function — the `schema_version`-presence test, the `body[:MAX_BODY]` bound, the fail-soft `except` and the document-order first-match-wins rule all stay exactly as they are. Keep the file stdlib-only, keep every `gh` call a fixed argv list, and interpolate no body text into any command. Add no `#` comment line to either Python file, and put no phase number, plan id, `.planning/` path or decision id anywhere in the fixture, the tests or the script. In `SKILL.md` section 2, next to the sentence stating detection needs both markers, add one short paragraph recording that current `dev test` builds emit a captured-log fenced block ahead of the report block, that detection scans every fenced block regardless of its info string, and naming the new fixture as the committed case for that shape. Then commit all four paths in one commit: `fix(260916-tea): find the report block when other fenced blocks precede it`. No AI attribution and no `Co-Authored-By` trailer. Do not touch the three pre-existing fixtures, the noise files listed in Task 1, or either submodule.</action>
  <verify>
    <automated>python3 -m unittest discover -s .claude/skills/devtest-triage/scripts/tests -t .claude/skills/devtest-triage/scripts/tests</automated>
    <automated>python3 -m unittest discover -s .claude/skills/devtest-triage/scripts/tests -t .claude/skills/devtest-triage/scripts/tests 2>&1 | /usr/bin/grep -qE '^Ran (69|[7-9][0-9]|[1-9][0-9][0-9]) tests'</automated>
    <automated>python3 .claude/skills/devtest-triage/scripts/devtest_issues.py show --body-file .claude/skills/devtest-triage/fixtures/dev-test-sst39sf040-log-capture-first.md --title '[dev test] SST39SF040 — FAIL' | /usr/bin/grep -q 'schema      2.2'</automated>
    <automated>FILES=$(git show --format= --name-only HEAD) && test -n "$FILES" && test "$(printf '%s\n' "$FILES" | /usr/bin/grep -c -e 'at28c256' -e 'error-codes-populated' -e '\.vscode' -e 'devcontainer' -e 'firestarter_app' -e 'firestarter_fw' || true)" = "0"</automated>
    <automated>PYDIFF=$(git show --format= HEAD -- '*.py') && test -n "$PYDIFF" && test "$(printf '%s\n' "$PYDIFF" | /usr/bin/grep -c '^+[[:space:]]*#' || true)" = "0"</automated>
    <automated>ALLDIFF=$(git show --format= HEAD) && test -n "$ALLDIFF" && test "$(printf '%s\n' "$ALLDIFF" | /usr/bin/grep -c -e '^+.*\.planning/' -e '^+.*[Pp]hase [0-9]' || true)" = "0"</automated>
  </verify>
  <human-check>With `gh` authenticated: `python3 .claude/skills/devtest-triage/scripts/devtest_issues.py show 90` exits 0 and prints `schema 2.2`, host `3.0.0b44`, firmware `3.0.0b31:leonardo` and `ROUTE: FAIL ... write, verify`; `... list` prints no `(no JSON report)` note on any open issue. If `gh` is unavailable, say so in the SUMMARY rather than claiming the check passed.</human-check>
  <done>The suite is green on its own exit status with more than 68 tests. The new fixture parses through `show` end to end. The mutation guard fails the suite if the pre-fix pattern is restored. The three pre-existing fixtures are byte-identical and absent from the commit. No added comment line and no process citation in the diff. Issue #90 renders as a parseable report.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| GitHub issue body -> `FENCE_RE` -> `extract_report` | Community-authored and wholly untrusted. This task widens what the enumerator will hand to `json.loads`: previously only blocks opened by a bare or `json` fence, now any info string. |
| `extract_report` -> `list` / `show` / `fold` verdicts | A wrong or forged report drives a triage decision, including an outward-facing issue close through `fold --apply`. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-tea-01 | Spoofing | a decoy fenced block placed before the real report | medium | mitigate | Qualification is unchanged and stays on content: a block wins only when `json.loads` yields a dict carrying `schema_version`, in document order. A decoy without that key is skipped; a decoy with it was already able to win under the old pattern, so this fix adds no new precedence (DD-2). |
| T-tea-02 | Denial of Service | lazy body match over a 1 MB body | medium | mitigate | `body[:MAX_BODY]` stays in force ahead of the match. Both fences are line-anchored, so a body with no line-initial fence fails at each line start rather than backtracking; pinned by the existing over-`MAX_BODY` test plus the new unclosed-fence case (DD-5). |
| T-tea-03 | Tampering | hostile block content reaching a shell or the interpreter | high | mitigate | No `eval`, no `exec`, no `subprocess` added; every `gh` call keeps its fixed argv list and no body text is interpolated into any command. The change is confined to one compiled pattern (DD-2). |
| T-tea-04 | Repudiation | the defect itself — a real report silently read as absent | high | mitigate | This is the bug being closed. The mutation guard makes the regression permanently detectable rather than resting on a commit-message claim (DD-3). |
| T-tea-SC | Tampering | npm/pip/cargo installs | high | accept | No package-manager install task exists in this plan; both files stay stdlib-only and no manifest changes, so the package-legitimacy gate has no surface here. |
</threat_model>

<verification>
- The skill suite exits 0 ON ITS OWN STATUS — not laundered through a pipe — with more than the 68 tests measured before this plan.
- `git log --oneline` shows exactly two new commits, one per task, neither carrying an AI attribution line or a `Co-Authored-By` trailer.
- The union of both commits' file lists is exactly the five paths in `files_modified`. Nothing under `.vscode/`, `.devcontainer/`, `.planning/`, `firestarter_app/` or `firestarter_fw/` appears, and `git diff --submodule=short beta...HEAD` reports no gitlink movement.
- `eprom_ledger.py check` still reports the ledger matches a fresh render after the commit.
- The three pre-existing fixtures are byte-identical to their pre-task content.
- Issue #90 parses end to end through the real `gh` path — a human-verify leg, since it needs network and an authenticated CLI.
</verification>

<success_criteria>
The four chips validated during triage are on this branch and ready to reach `beta`, and a
`dev test` report produced by a current build — which now leads with a captured-log block — is
read correctly by `list`, `show` and `fold`, with a mutation-guarded test that goes red the day
the fence enumerator regresses.
</success_criteria>

<output>
Create `.planning/quick/260916-tea-correct-the-dev-test-so-all-relevant-wor/260916-tea-SUMMARY.md` when done.
</output>
