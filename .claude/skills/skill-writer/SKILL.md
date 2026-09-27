---
name: skill-writer
description: Write a new skill for the Firestarter repo, or fix one that never triggers. Use when asked to create, author, add or scaffold a skill, to turn a repeated procedure into a skill, to review or rewrite an existing SKILL.md, or to work out why a skill is not being picked up.
---

# Writing a skill

A skill is one directory under `.claude/skills/`, holding one `SKILL.md`. The
frontmatter decides whether the skill is ever reached; the body decides whether it
helps once it is. Both fail silently, so both are checked below.

```bash
mkdir -p /workspaces/.claude/skills/<name>          # directory name IS the skill name
$EDITOR /workspaces/.claude/skills/<name>/SKILL.md  # frontmatter + body
```

Skills live in the **meta repo** (`/workspaces/.claude/skills/`), not in a sub-repo.
It is the only vantage point that sees all three trees — `.planning/`,
`firestarter_app/`, and `firestarter/` — and most skills here touch more than one.

## Frontmatter contract

Two keys, both required, nothing else needed:

| Key | Rule |
|---|---|
| `name` | Lowercase, hyphenated. **Must equal the directory name.** A mismatch is the single most common reason a skill never loads. |
| `description` | One sentence or two. Names the capability *and* the phrasings that should route to it. This is the only part of the skill that is always in context — everything else is loaded on demand. |

`allowed-tools` exists as an optional restriction on what the skill may call. Reach
for it only when a skill must be prevented from writing.

Write the description in the third person, about the task, not about the reader:

```yaml
# Reaches the skill.
description: Triage community `dev test` chip-validation issues against the chip's real
  datasheet. Use when asked to triage dev test issues, check an EPROM against its
  datasheet, verify the pin map or VPP for a chip, or close passing validation issues.

# Never reaches it — no trigger surface, and "helps you" describes the reader.
description: Helps you work with EPROMs.
```

The pattern every working skill here follows: **what it does**, then `Use when
asked to …` followed by the concrete verbs and nouns a request would actually
contain. Include the vocabulary you would not choose yourself — `dev test`, `pinout`,
`VPP`, `blank-check`, `at28c256`, `infoic.xml` — because the request will use it,
often as a bare part number. A skill that only matches its own preferred wording is a
skill that never fires.

## Where files go

| Path | Holds | Notes |
|---|---|---|
| `<skill>/SKILL.md` | The index. Always loaded when the skill triggers. | Keep it to what a reader needs every time. |
| `<skill>/scripts/*.py` | Every executable module. | Python 3 (`/usr/local/bin/python3`, 3.12 here). Node 22 is also on PATH if a skill needs it. |
| `<skill>/<data>.json` | Data and templates. | Skill root, not `scripts/`. |
| `<skill>/references/*.md` | Detail loaded on demand. | Reference by path from SKILL.md so it is fetched only when needed. |

Commit data a skill needs to run offline, and keep scripts runnable from any cwd —
this container resets the working directory between tool calls, so a skill that
depends on an earlier `cd` will break. Use absolute paths or a `$S=` variable.

## Progressive disclosure

`SKILL.md` is an index, not a manual. Everything in it costs context on every
trigger; everything outside it costs nothing until named.

- Put the whole workflow in `SKILL.md` when it fits in roughly a screen or two.
- Move per-format tables, long reference material, and rarely-needed edge cases
  into sibling files, and name the path where the reader would want them.
- Never inline something a script can produce. `python3 … infoic_lookup.py AT28C256`
  beats pasting a decode table into the skill.

## House style

Match the skills already here. They read the same way on purpose:

- **Imperative and terse.** "Read the field, do not assume it." Not "it is
  recommended that you consider…".
- **Commands first.** Open with the fenced block that does the thing, then explain.
  Assign the long path to a variable (`S=/workspaces/.claude/skills/<name>/scripts`)
  and use it throughout.
- **Worked output, not description.** Show what the command actually prints, captured
  from a real run.
- **Tables for contracts** — options, file meanings, troubleshooting. End with a
  `Symptom | Fix` table.
- **Numbered steps for anything ordered**, especially where order is load-bearing
  (fold same-EPROM issues *before* triaging any of them).
- **State the provenance of any claim.** This project grades every fact. Say which
  source a table came from, cite `file:line` where it helps, and mark what is verified
  versus assumed. A firmware claim that has not been on the bench says so.

## Hard rules a new skill must not break

These are project constraints, not preferences. A skill that violates one is wrong
however well it is written.

| Rule | What it forbids in a skill |
|---|---|
| **A skill owns its scripts** | No importing or shelling out to `firestarter_app/tools/*.py` or firmware scripts — those are submodules that move, get renamed, or are not checked out. Depending on general binaries (`gh`, `curl`, `pdftotext`, `python3`) is fine, and so is *running* the project's own build/gate commands (`build_db.py`, `pytest`, `pio run`) — those are the thing being verified, not a borrowed helper. |
| **Never hand-edit generated files** | `firestarter_app/firestarter/data/chip_database.json` is generated by `tools/build_db.py`; `firestarter/include/messages.h` is codegen'd from the meta repo's `messages.toml`. Edits are erased on the next regen. Fix the generator and regenerate. |
| **The database generator may not invent fields** | Every emitted value must decode from an attribute minipro's `infoic.xml` actually carries (`flags`, `voltages`, `protocol_id`, `variant`, `pin_map`, `type`). No per-chip guess tables keyed on part number — three were deliberately deleted in Phase 70. |
| **Never weaken a hardware-damage guard** | `tools/check_dispatch.py` (GATE-03) stops 12V reaching a 5V part's WE/address pin. A skill never edits a gate to make its own change pass. |
| **Hardware is destructive and operator-gated** | `firestarter dev test <chip>` ALWAYS WRITES to the chip. No skill runs a hardware command, adjusts the VPP pot, or drives a bench board without explicit operator go-ahead in that session — and never while another agent may hold the serial port. |
| **Keep the two-repo constants in sync** | Flag bits and constants are duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h`; the serial protocol between `serial_comm.py` and `firestarter.cpp`. A skill that changes one must change the other. |
| **Never work on `beta` or `main`** | Sub-repo work forks off `beta`, meta work off `main`, onto a `v1.X-slug` branch. Releases are operator-gated: nothing is stable until the operator says so. |
| **File-changing work enters through GSD — where GSD exists** | `/gsd-quick`, a seeded `gsd-debugger` session, or `/gsd-execute-phase`, so it lands with atomic commits and state tracking. A skill routes the reader there rather than editing around the gate. |
| **GSD is optional — degrade, never hard-fail** | A contributor may clone this repo without GSD installed. A skill that leans on `.planning/`, a `gsd-*` subagent, or a slash command must detect its absence and fall back to something self-contained, keeping the safety-critical parts intact. Key the prompt on whether `.claude/agents/gsd-<name>.md` exists (project or `~/`), and the file location on whether `.planning/` exists — they are independent signals. `devtest-rootcause`'s `--mode auto\|gsd\|standalone` is the worked example. |

If a skill hands work to a subagent, it must carry the relevant rules **into the
prompt**. A `gsd-debugger` has Write access and no idea the chip database is
generated; without the constraint it will "fix" the JSON and the change will vanish.

## Registering it — there is nothing to register

Skills in `.claude/skills/` are discovered automatically. This repo's `CLAUDE.md` is
hand-written and has **no `GSD:skills` managed block**, so there is no Project Skills
table to add a row to.

**Do not run `gsd-tools generate-claude-md` to "register" a skill.** It does not touch
the hand-written `/workspaces/CLAUDE.md` at all — it *creates* a second file at
`/workspaces/.claude/CLAUDE.md`, 265 lines regenerated from `.planning/PROJECT.md` and
`.planning/codebase/STACK.md`. Claude Code then loads **both** files as project
instructions every session, and the generated one goes stale the moment those sources
do. Verified 2026-08-08: the file did not exist, one invocation created it.

If you run it by accident, delete the file it created:

```bash
rm /workspaces/.claude/CLAUDE.md      # only if it was absent before
```

## Tracking it

`.gitignore` keeps all of `.claude/` local **except** skills:

```
.claude/*
!.claude/skills/
```

So a new skill is tracked and shared automatically. One exclusion follows it —
`find-skills`, which is marketplace-installed and carries a `source.json` to reinstall
from, so it is not vendored here. Check what you are about to commit:

```bash
git add -An .claude/          # must list only the skills you intend to ship
```

## Validation checklist

Before calling a skill done:

- [ ] `name` matches the directory name exactly.
- [ ] `description` names the capability and the trigger phrasings, in the third
      person, including vocabulary you would not have chosen.
- [ ] Every command in the skill has been run, and the shown output is real.
- [ ] Every path the skill cites resolves to a file that exists.
- [ ] Scripts are under `scripts/`, own their logic, and run from any cwd.
- [ ] Nothing in it breaks a hard rule above.
- [ ] It says how its claims were established, and marks what is unverified.
- [ ] `git add -An .claude/` lists what you expect and nothing else.

The mechanical half of that list is checkable:

```bash
node -e '
const fs=require("fs"),p="/workspaces/.claude/skills";
for (const d of fs.readdirSync(p)) {
  const f=`${p}/${d}/SKILL.md`;
  if (!fs.existsSync(f)) { console.log(`FAIL ${d}: no SKILL.md`); continue; }
  const m=fs.readFileSync(f,"utf8").match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) { console.log(`FAIL ${d}: no frontmatter`); continue; }
  const name=(m[1].match(/^name:\s*(.+)$/m)||[])[1]?.trim();
  const desc=(m[1].match(/^description:\s*([\s\S]+?)(?=\n\S+:|$)/m)||[])[1]?.trim();
  const bad=[];
  if (name!==d) bad.push(`name "${name}" != dir "${d}"`);
  if (!desc) bad.push("no description");
  else if (!/\buse when\b/i.test(desc)) bad.push("description has no \"Use when\" trigger clause");
  console.log(bad.length ? `FAIL ${d}: ${bad.join("; ")}` : `ok   ${d}`);
}'
```

Real output:

```
ok   devtest-rootcause
ok   devtest-triage
ok   find-skills
ok   skill-writer
```

It catches the name/directory mismatch, missing or unparseable frontmatter, and a
description with no trigger surface — the three failures that make a skill invisible
rather than merely unhelpful. Everything else on the list needs reading.

Also check the skill has no borrowed dependencies:

```bash
grep -rn "^import \|^from \|firestarter_app/tools" /workspaces/.claude/skills/<name>/scripts/
```

Anything outside the stdlib, or any path into a sub-repo's `tools/`, breaks the
first hard rule.

## Skeleton

````markdown
---
name: my-skill
description: <What it does, in one clause.> Use when asked to <verb> <noun>,
  <alternate phrasing>, or <the term someone else would use>.
---

# <Imperative title>

<One or two sentences: what goes in, what comes out.>

```bash
S=/workspaces/.claude/skills/my-skill/scripts

python3 $S/driver.py <verb> <arg>      # the common case
```

## <The main operation>

<Command, then real output, then how to read it.>

## Troubleshooting

| Symptom | Fix |
|---|---|
| … | … |
````
