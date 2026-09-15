---
name: devtest-rootcause
description: Investigate the firestarter code behind a triaged `dev test` chip failure and fix the real defect — a decode bug in the database generator, or a genuine bug in the host app or firmware — then report the fix on the issue with the artefact versions carrying it and a fix:committed / fix:released label. Knows that chip_database.json is generated and must never be hand-edited. Use when asked to investigate why an EPROM fails, root-cause a dev test issue, fix a chip's pinout or protocol or VPP, correct the database generator, act on the datasheet findings left on an issue, say which version fixes a chip, or make a chip like at28c256 or w27e257 work.
---

# Root-cause a `dev test` failure in the code

Takes the datasheet findings `devtest-triage` left on an issue and turns them into a
fix in the **right** file, then reports on the issue which artefact versions carry that
fix. The hard part is not the fix, it is knowing which files may be edited at all.

**Self-contained.** `scripts/infoic_lookup.py` is stdlib-only and owns its decode
tables outright — it never imports `build_db.py`, so it works even with
`firestarter_app` absent. `--check` guards against the copy drifting (see §1).

That is distinct from the **regeneration commands** in §4 (`build_db.py`,
`.claude/skills/devtest-rootcause/scripts/diff_db.py`). Those are the project's own build and gate steps —
the thing being fixed — exactly like `pytest` or `pio run`. A skill must not
reimplement or shadow them; regenerating the database means running the real generator.

The meta repository is also named `firestarter`. That name collision is why a
firmware path without the `_fw` suffix looks plausible and is wrong.

```bash
# ROOT works from anywhere in the checkout, including inside either submodule.
ROOT=$(git rev-parse --show-superproject-working-tree 2>/dev/null)
ROOT=${ROOT:-$(git rev-parse --show-toplevel)}

APP=$ROOT/firestarter_app
FW=$ROOT/firestarter_fw
S=$ROOT/.claude/skills/devtest-rootcause/scripts

python3 $S/infoic_lookup.py AT28C256        # what upstream actually says about the chip
python3 $S/infoic_lookup.py --check         # our tables still agree with build_db.py?
python3 $S/seed_debug_session.py 21         # seed a GSD debug session from the issue

grep VERSION $FW/include/version.h          # firmware version, for the §5 fix report
grep __version__ $APP/firestarter/__init__.py   # host version, same
```

## The fix surface — read this before editing anything

| File | Status | May you edit it? |
|---|---|---|
| `$APP/firestarter/data/chip_database.json` | **GENERATED** by `tools/build_db.py` | **NEVER.** Edits are erased on the next regen. Fix the generator, regenerate |
| `$APP/tools/build_db.py` | authored — the decoder | Yes, subject to the proof rule below |
| `$APP/firestarter/data/pinouts.json` | authored — input to the generator, never written by it | Yes. This is where a wrong socket wiring is really fixed |
| `$APP/tools/extra_chips.json` | authored supplement | Only for chips **absent from infoic.xml entirely** (2516, 2532). Not an override for a chip upstream already has |
| `$APP/firestarter/*.py` | authored host app | Yes — real bugs |
| `$FW/src/`, `$FW/include/` | authored firmware | Yes — real bugs. Cannot be verified without bench hardware; say so |
| `$FW/include/messages.h` | **GENERATED** from the meta repo's `messages.toml` | Never hand-edit; regenerate |

### The proof rule

**The generator may not emit a field it cannot prove from `infoic.xml`.**

Every value in a database entry must be *decoded from an attribute upstream actually
carries*. No invented fields, no per-chip lookup table keyed on part number, no
hand-maintained override stack — under any name.

If a chip decodes wrongly, the bug is in **how an existing attribute is interpreted**
— `flags`, `voltages`, `protocol_id`, `variant`, `pin_map`, `type` — and the fix
belongs in the function that interprets it. If the information genuinely is not in
`infoic.xml`, the honest outcome is to report that, not to invent a field.

> One exception exists: `_PAGE_SIZE_BY_PART` (`build_db.py:114`) adds `page_size` from
> `[CITED:]` **datasheets**, not from `infoic.xml` — the exact shape this rule forbids.
> Do not extend it or add siblings to it. Upstream carries `infoic_page_size_raw`, which
> is the principled seam if page size ever needs revisiting.

## 1. See what upstream actually says

```bash
python3 $S/infoic_lookup.py AT28C256
```

Real output:

```
=== AT28C256,AT28C256@SOIC28,AT28C256E,...,AT28HC256L   [ATMEL]   (INFOICT76) ===
  matched           : AT28C256, AT28C256@SOIC28   packages: (unqualified), SOIC28
  flags & 0x10      = SET   -> electrically erasable   (raw flags 0xC010)
  voltages & 0xF0   = 0x00  -> VPP 12V   (option bits 0x0)
  protocol_id       = 0x07  -> programming.algorithm, before any safety flip
  variant           = 0x4126 (lo=0x26, hi=0x41)  -> resolve_pinout_key()
  pin_map           = 0x0C14 (lo=0x14 = pm_idx)  -> resolve_pinout_key()
  type              = 1 (EEPROM)
  code_memory_size  = 32768 (0x8000)  -> electrical.size_bytes
```

The script owns its decode tables rather than importing the generator, so it stays
usable standalone. The cost of a private copy is drift, so verify it after touching
`build_db.py`:

```bash
python3 $S/infoic_lookup.py --check
```

```
ok: MINIPRO_XML_URL matches build_db.py
ok: VPP table matches build_db.py:VPP_MV (16 entries, compared in mV)
```

It reads the generator **as text** (`ast.literal_eval`, never importing or running it —
running it would regenerate the database) and exits 1 naming any key that disagrees.
With `firestarter_app` absent it prints `SKIP` and exits 0; the lookup still works.

**It fails CLOSED on a rename.** A constant the check cannot find is a DRIFT, not a
warning, and the message names every name it tried (`GENERATOR_VPP_NAMES`). The owned
table is held in **millivolts** to match the generator exactly, so the comparison is a
plain dict equality with no string round-trip; `format_vpp()` does the `12000 -> "12V"`
rendering at the print site.

Never "improve" a table value from memory — transcribe it from the generator, then run
`--check`. A misremembered VPP index reads as a decode bug in a chip that has none.

`--raw` dumps every attribute verbatim when you need one the decoder ignores.

Three things this output will trip you on:

- **Package suffixes.** Upstream names are qualified — `W27E257@DIP28`. Some parts
  appear *only* suffixed. DIP is the package this project programs; a PLCC/SOIC row
  legitimately carries a different `protocol_id` and pinout and is not evidence of a bug.
- **A part appears once per upstream database** (`INFOICT76`, `INFOIC2PLUS`, `INFOIC`)
  and the rows can disagree — the legacy `INFOIC` row for AT28C256 says
  `protocol_id=0x31`. Check which database `build_db.py` consumes before treating a
  row as authoritative.
- **Not found means not found.** `infoic_lookup.py 2516` exits 1 — and 2516 is one of
  exactly two chips in `extra_chips.json`. That is the supplement's whole remit.

Compare against what shipped:

```bash
cd $APP && firestarter info -a at28c256
python3 -c "
import json,re
d=json.load(open('firestarter/data/chip_database.json'))
for m,cs in d.items():
    for e in cs:
        if 'AT28C256' in e.get('part_number',''):
            print(m, json.dumps(e, indent=2))"
```

**A difference is not automatically a bug.** `build_db.py` deliberately flips 5V
parallel EEPROMs from upstream's `0x07` to `0x0D` so a 12V rail is never driven into a
5V part — that is why AT28C256 ships as algorithm `13` despite upstream saying `0x07`.
Read the rule and its comment before "correcting" it. Likewise the `vpp: "12V"` on that
part is a faithful decode of VPP index `0x00`; protocol `0x0D` never routes it.

## 2. Decide which layer is at fault

| Evidence from triage | Layer | Where |
|---|---|---|
| Pin map disagrees with the datasheet DIP view | pinout data | `pinouts.json` if the key's wiring is wrong; `resolve_pinout_key()` if the wrong key was chosen |
| Wrong `electrical.type` / erase capability | decode | `classify()` — the `flags & 0x10` axis, not `protocol_id` |
| Wrong VPP | decode | the VPP index table; mask `voltages & 0xF0`, never `& 0xFF` |
| Wrong algorithm/protocol | decode | `classify()` and the safety-flip rules in `main()` |
| Wrong pulse timing | decode | `interpret_timing()` |
| Chip missing from the DB entirely | supplement | `extra_chips.json`, only if absent from `infoic.xml` |
| Right data, wrong behaviour on the wire | host | `$APP/firestarter/eprom_operations.py`, `serial_comm.py`, `chip_resolver.py` |
| Right command, wrong hardware sequence | firmware | `$FW/src/proms/*.cpp` for the protocol, `src/eprom_operations.cpp` |

Firmware protocol implementations map to the constants in `$FW/include/proto_constants.h`
(`eprom.cpp`, `eeprom_28c.cpp`, `flash_5v_page.cpp`, `flash_nor_unlock.cpp`,
`flash_intel.cpp`, `sram.cpp`). Constants and flag bits are duplicated between
`$APP/firestarter/constants.py` and `$FW/include/firestarter.h` — change both together.

## 3. Hand the fix to `gsd-debug`

Once §2 says *which layer* is at fault but not *why*, stop reasoning in this context
and run the fix through a GSD debug session. That gets the scientific-method loop,
a persistent session file that survives a context reset, and atomic commits.

Seed the session first — the whole point of the handoff is that the debugger inherits
the datasheet work instead of redoing it:

```bash
python3 $S/seed_debug_session.py 21                    # from the triaged issue
python3 $S/seed_debug_session.py 21 --slug at28c256-sdp-write
```

```
[gsd] Session: <root>/.planning/debug/at28c256-sdp-write.md
[gsd] Status: investigating
[gsd] Carried over 6 eliminated hypotheses from triage
```

It reads the issue and the `devtest-triage` comment, then writes a standard GSD debug
session file with `Symptoms` and `Context` filled from the report, and every **MATCH**
row of the triage table pre-recorded under `Eliminated`:

```
- hypothesis: Pin map (28-DIP) is wrong
  evidence: datasheet says §2.4 pins 1–28; database has `DIP28_28C256` —
            triage cross-check verdict MATCH — all 28 pins agree
```

Rows that were *not* proven dead (a `LOW` or `represented` verdict) are deliberately
left out — only a settled question gets eliminated. A PASS report is refused: that is
`devtest-triage` territory, not a debug session.

The script then prints the spawn prompt. **Spawn `gsd-debugger` directly:**

```
Agent(prompt=<the printed prompt>, subagent_type="gsd-debugger",
      description="Debug at28c256-sdp-write")
```

**Do not spawn `gsd-debug-session-manager`, and do not invoke `/gsd-debug` for this.**
In this devcontainer agents launch in the background and the manager's nested spawn
does not complete: it returns a bogus "waiting…" message with the session file
untouched, while an orphaned debugger keeps running. Two debuggers then race the same
serial port and confound every hardware reading. One level, directly, is the rule here.
Before spawning, check no earlier debugger is still alive on the port.

The printed prompt already carries the §0 fix-surface rules verbatim. That is not
decoration: `gsd-debugger` has Write access and no knowledge that
`chip_database.json` is generated — without those constraints it will "fix" the JSON
and the change will vanish at the next regen. If you write the prompt yourself, carry
them, plus the hardware note that `dev test` always writes and needs operator consent.

**The prompt must also force the resume path.** `gsd-debugger`'s own entry flow reads
*"If active sessions exist AND $ARGUMENTS: start new session → `create_debug_file`"*,
and that step writes a fresh file with `status: gathering` and an **empty Symptoms**.
Since the spawn prompt supplies arguments, a debugger that takes that branch discards
the seeded file — losing the whole Eliminated section, and then skipping symptom
gathering because `symptoms_prefilled: true`. Strictly worse than not seeding. The
generated prompt therefore names the path and status explicitly and tells it to enter
at `resume_from_file`. Do not drop that block.

When the debugger returns, continue at §4 — a debug session does not exempt a database
change from the regen-and-diff proof.

### If GSD is not installed

**GSD is optional.** A contributor who clones this repo without it must still be able
to use the skill, so the seeder detects and degrades:

```bash
python3 $S/seed_debug_session.py 21 --mode standalone   # force it either way
```

```
[standalone] Investigation record: gsdless/devtest-investigations/at28c256-sdp.md
[standalone] Carried over 6 eliminated hypotheses from triage
[standalone] GSD not detected — emitting a plain investigation prompt with no gsd-debugger dependency.
```

| Signal | Effect |
|---|---|
| `gsd-debugger.md` in `<root>/.claude/agents/` or `~/.claude/agents/` | Decides the **prompt**: GSD spawn prompt vs standalone |
| `<root>/.planning/` exists | Decides the **directory**: `.planning/debug/` vs `devtest-investigations/` |

The two signals are independent — `.planning/` is a sensible home for the record even
where the agent is missing. `--mode gsd` on a machine without the agent warns rather
than failing silently, because spawning that subagent type will fail.

The standalone prompt drops every GSD-specific step name and instead states the method
— one hypothesis at a time, name the test that would disprove it, no code changes until
a hypothesis survives — and keeps the same record-file discipline (Symptoms immutable,
Eliminated append-only, Current Focus overwritten before each action). **It carries the
identical fix-surface guardrails**, which is the part that must never be lost: those
protect the generated database regardless of who does the investigating.

Hand it to a general-purpose agent or work it yourself, and commit any fix atomically
on its own branch — the GSD routing in Hard rules below applies only where GSD exists.

## 4. Regenerate and prove the change

Never edit the JSON. After changing the generator:

```bash
cd $APP
python3 tools/build_db.py            # fetches the pinned infoic.xml SHA, rewrites the DB
FIRESTARTER_DB_FILE=$ROOT/firestarter_app/firestarter/data/chip_database.json \
FIRESTARTER_BASELINE_FILE=$ROOT/firestarter_app/tools/baseline/chip_database.baseline.json \
python3 $ROOT/.claude/skills/devtest-rootcause/scripts/diff_db.py  # per-chip diff vs tools/baseline/ — the review artifact
git diff --stat firestarter/data/chip_database.json
```

`build_db.py` takes no arguments and **runs the full regen on any invocation** —
there is no `--help`. It is deterministic against the pinned SHA: on an unmodified
tree it reproduces the shipped file byte for byte, so any diff is *yours*.

Read `.claude/skills/devtest-rootcause/scripts/diff_db.py` output as the evidence for the change. A one-chip fix that moves
hundreds of chips means the decode change was too broad — that is the signal this
pipeline exists to give you.

Then the app's own gates:

```bash
cd $APP && python3 -m pytest -o addopts="" -q
```

Doubling `-q` hides the count line, hence the `-o addopts=""`. If the baseline chip
count changes, `tools/baseline/` must be re-anchored deliberately and explained — not
quietly refreshed to make a test pass.

For firmware:

```bash
cd $FW && pio run -e uno && pio test
```

A firmware protocol change cannot be validated without a chip on the bench. Say that
explicitly rather than implying the fix is confirmed.

## 5. Report the fix on the issue

A code change is not a validation. What closes a `dev test` issue is a fresh PASS
report from the reporter's bench — and only `devtest-triage` closes it, against the
three-leg supersede test in its §3a. Leg 2 of that test compares **artefact versions**,
so a fix comment that does not name them cannot be acted on: the reporter does not know
what to install, and a later PASS cannot be shown to post-date the fix.

So the deliverable here is a comment naming **which artefact versions carry the fix**,
plus the label that says whether anyone can test it yet.

### Read every version, never state one from memory

| Artefact | Version lives in | How it appears in a report |
|---|---|---|
| Firmware | `$FW/include/version.h` → `VERSION` | the `firmware` row, rendered `VERSION:board` by `FW_VERSION` |
| Host app | `$APP/firestarter/__init__.py` → `__version__` | the `host` row |
| Chip database | **no version of its own** | it is regenerated into the host package, so a database fix ships under the host version above |

That third row is the one that catches people. A `build_db.py` or `pinouts.json` fix has
no version of its own to cite — cite the host release that will carry it.

```bash
grep VERSION $FW/include/version.h
grep __version__ $APP/firestarter/__init__.py
git -C $FW log --oneline -3          # the commits carrying the fix
git -C $APP log --oneline -3
```

### Post it

```bash
gh issue comment 45 --repo henols/firestarter --body-file /tmp/fix.md
```

Template — keep the artefact table even when a row is empty, because "the host is not
involved" is itself a finding:

```markdown
### Fix — <one line saying what was wrong>

**Root cause:** <the mechanism, in the code, at file:line>

| Artefact | Commits | Version carrying the fix |
|---|---|---|
| Firmware | `1e8bbae`, `a218b4f` (fw#56 → `beta`) | none yet — later than `3.0.0b22` |
| Host app | — | — (not involved) |
| Chip database | — | — (not involved) |

**Proof:** <the gate output that showed it works — .claude/skills/devtest-rootcause/scripts/diff_db.py, pytest, pio test>
**Unproven:** <what needs a chip on the bench>

**To re-test:** install firmware <version> and host <version>, then
`firestarter dev test <chip>`. A PASS on those versions closes this issue.
```

### Label it

| State | Label | Means |
|---|---|---|
| Commits exist, no release carries them | `fix:committed` | Nobody can test it yet. Say which release will carry it if you know |
| A released version carries the fix | `fix:released` | The reporter can act — re-running `dev test` on that build is what closes this |

```bash
gh issue edit 45 --repo henols/firestarter --add-label fix:committed
```

Move the label from `fix:committed` to `fix:released` when the release lands — that
transition is the signal to the reporter, so do not leave it stale:

```bash
gh issue edit 45 --repo henols/firestarter \
  --remove-label fix:committed --add-label fix:released
```

Both labels come from the shared taxonomy;
`python3 $ROOT/.claude/skills/devtest-triage/scripts/devtest_issues.py labels`
creates it if the tracker does not have it yet.

Leave the issue **open** either way. A fix you have proven in CI is still unproven on
the reporter's hardware, and that gap is exactly what the label and the version
references exist to close.

## Hard rules

- `chip_database.json` is generated. Editing it is always wrong.
- No generator field without proof in `infoic.xml`. No per-chip guess tables.
- `extra_chips.json` adds chips upstream lacks; it does not override chips upstream has.
- Do not "fix" `PROTO_PHANTOM_0x35` / `0x39` spelling in `proto_constants.h`; those
  substrings are deliberate.
- **Where GSD is installed**, file-changing work goes through it so it lands with atomic
  commits and state tracking: an unexplained failure to a seeded debug session (§3), an
  already-diagnosed one-line fix to `/gsd-quick`. Route there rather than committing
  around the gate. Where it is not installed, that rule cannot apply — use the
  standalone prompt and commit atomically on a branch. GSD is a convenience here; the
  fix-surface rules are not, and hold either way.
- Spawn `gsd-debugger` **directly**, one level. Never `gsd-debug-session-manager`, and
  never two debuggers at once — they race the serial port and confound the readings.
- Any prompt handed to a debugger must carry the fix-surface rules. It has Write access
  and does not otherwise know the database is generated. `seed_debug_session.py`
  includes them; if you hand-write a prompt, include them yourself.
- **A fix is not reported until the artefact versions are on the issue** (§5). Name the
  firmware and host versions read from `version.h` and `__init__.py`, and label
  `fix:committed` or `fix:released`. Without them the reporter cannot know what to
  install, and `devtest-triage` cannot show a later PASS post-dates the fix.
- Never close a `dev test` issue from this skill. A code change is not a validation —
  only a PASS report closes one, via `devtest-triage`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Database edit vanished | You edited the generated JSON. Fix `build_db.py` or `pinouts.json`, regenerate |
| `build_db.py` prints many `WARN: skipping … unknown protocol_id` | Normal. Upstream carries families firestarter has no handler for |
| `.claude/skills/devtest-rootcause/scripts/diff_db.py` shows hundreds of changed chips | Decode change too broad. Narrow the condition |
| `WARN: resolved pinout key 'X' not in pinouts.json` | `resolve_pinout_key()` returned a key with no definition — add the wiring or fix the resolution |
| Chip not found by `infoic_lookup.py` | Check the part really is absent, not just package-suffixed — the script already splits on `@`. If genuinely absent → `extra_chips.json` territory |
| Fetch of infoic.xml is slow | 17.8 MB. It caches to `$TMPDIR/infoic-<sha>.xml`; reuse it |
| Debugger edited `chip_database.json` | Its prompt lacked the fix-surface rules. Revert, reseed with `seed_debug_session.py`, respawn |
| Session manager returns "waiting…" and nothing changed | Known devcontainer failure. Spawn `gsd-debugger` directly instead (§3) |
| `seed_debug_session.py` refuses a PASS issue | Correct — a PASS goes to `devtest-triage` to be closed and logged |
| `gh: 'fix:committed' not found` | The shared taxonomy is not created on this tracker — run `devtest_issues.py labels` from `devtest-triage/scripts` |
| A fix landed but the issue still says `fix:committed` | The release shipped and nobody moved the label. Swap it to `fix:released` and post the version that carries it (§5) |
| Reporter asks "which version has the fix?" | §5's comment was skipped or omitted the artefact table. Read the versions from `version.h` and `__init__.py` — never from memory — and post it |
| `--check` reports DRIFT | `build_db.py` changed. Update the table in `infoic_lookup.py` to match the generator — the generator is authoritative, not this script |
| `--check` says "no VPP table found under any known name" | The generator renamed the table again. Find the new name, prepend it to `GENERATOR_VPP_NAMES`, then **re-verify every value** — a rename and a value change can arrive in the same commit |
