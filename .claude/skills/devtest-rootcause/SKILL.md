---
name: devtest-rootcause
description: Investigate the firestarter code behind a triaged `dev test` chip failure and fix the real defect. The defect is a decode bug in the database generator, or a genuine bug in the host app or firmware. Then report the fix on the issue with the artefact versions carrying it and a fix:committed / fix:released label. Knows that chip_database.json is generated and must never be hand-edited. Use when asked to investigate why an EPROM fails, root-cause a dev test issue, or fix a chip's pinout or protocol or VPP. Use it also to fix the database generator, or to act on the datasheet findings left on an issue. Use it to say which version fixes a chip, or to make a chip like at28c256 or w27e257 work.
---

# Root-cause a `dev test` failure in the code

Takes the datasheet findings `devtest-triage` left on an issue and turns them into a
fix in the **right** file, then reports on the issue which artefact versions carry that
fix. The hard part is not the fix, it is knowing which files may be edited at all.

**Self-contained.** `scripts/infoic_lookup.py` is stdlib-only and owns its decode
tables outright — it never imports `build_db.py`, so it works even with
`firestarter_app` absent. The private copy can drift from the generator, so
transcribe any table value from `build_db.py` rather than from memory (see §1).

That is distinct from the **regeneration commands** in §3 (`build_db.py`,
`.claude/skills/devtest-rootcause/scripts/diff_db.py`). Those are the project's own build and gate steps —
the thing being fixed — exactly like `pytest` or `pio run`. A skill must not
reimplement or shadow them. Regenerating the database means running the real generator.

```bash
# ROOT works from anywhere in the checkout, including inside either submodule.
ROOT=$(git rev-parse --show-superproject-working-tree 2>/dev/null)
ROOT=${ROOT:-$(git rev-parse --show-toplevel)}

APP=$ROOT/firestarter_app
FW=$ROOT/firestarter_fw
S=$ROOT/.claude/skills/devtest-rootcause/scripts

python3 $S/infoic_lookup.py AT28C256        # what upstream actually says about the chip

grep VERSION $FW/include/version.h          # firmware version, for the §3 fix report
grep __version__ $APP/firestarter/__init__.py   # host version, same

# Tests for this skill's scripts. stdlib unittest, no pytest, no network, no submodule.
for d in $ROOT/.claude/skills/*/scripts/tests; do
  python3 -m unittest discover -s "$d" -t "$d" || break
done
```

Run them by hand after editing a script — nothing runs those tests
automatically, since this repository has no CI workflow.

## The fix surface — read this before editing anything

| File | Status | May you edit it? |
|---|---|---|
| `$APP/firestarter/data/chip_database.json` | **GENERATED** by `tools/build_db.py` | **NEVER.** Edits are erased on the next regen. Fix the generator, regenerate |
| `$APP/tools/build_db.py` | authored — the decoder | Yes, subject to the proof rule below |
| `$APP/firestarter/data/pinouts.json` | authored — input to the generator, never written by it | Yes. This is where a wrong socket wiring is really fixed |
| `$APP/tools/extra_chips.json` | authored supplement | Only for chips **absent from infoic.xml entirely** (2516, 2532). Not an override for a chip upstream already has |
| `$APP/firestarter/*.py` | authored host app | Yes — real bugs |
| `$FW/src/`, `$FW/include/` | authored firmware | Yes — real bugs. Cannot be verified without bench hardware. Say so |
| `$FW/include/messages.h` | **GENERATED** from the meta repo's `messages.toml` | Never hand-edit. Regenerate instead |

### The proof rule

**The generator may not emit a field it cannot prove from `infoic.xml`.**

Every value in a database entry must be *decoded from an attribute upstream actually
carries*. No invented fields, no per-chip lookup table keyed on part number, no
hand-maintained override stack — under any name.

If a chip decodes wrongly, the bug is in **how an existing attribute is interpreted**
— `flags`, `voltages`, `protocol_id`, `variant`, `pin_map`, `type` — and the fix
belongs in the function that interprets it. If the information genuinely is not in
`infoic.xml`, the honest outcome is to report that, not to invent a field.

The rule has no exceptions. Page size was the last one: it came from a per-part table
keyed on datasheets until phase 194 moved it onto `infoic_page_size_raw`, the upstream
attribute. Do not reintroduce a per-part table under any name.

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
usable standalone. The cost of a private copy is drift. Nothing detects that drift for
you, so after touching `build_db.py` compare the two tables by eye.

The owned table is held in **millivolts** to match the generator's own unit, so the two
can be read side by side with no string round-trip in the middle. `format_vpp()` does
the `12000 -> "12V"` rendering at the print site.

Never "improve" a table value from memory — transcribe it from the generator. A
misremembered VPP index reads as a decode bug in a chip that has none.

`--raw` dumps every attribute verbatim when you need one the decoder ignores.

Three things this output will trip you on:

- **Package suffixes.** Upstream names are qualified — `W27E257@DIP28`. Some parts
  appear *only* suffixed. DIP is the package this project programs. A PLCC/SOIC row
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
Read the rule and its comment before "fixing" it. Likewise the `vpp: "12V"` on that
part is a faithful decode of VPP index `0x00`. Protocol `0x0D` never routes it.

## 2. Decide which layer is at fault

**Start by asking whether this programming path has ever worked.** `devtest-triage`
records every chip that passed on real hardware, grouped into families — parts sharing
`programming.algorithm`, `pinout` and `electrical.vpp_mv`, the three fields that decide
the programming path, the wiring and the rail:

```bash
python3 $ROOT/.claude/skills/devtest-triage/scripts/eprom_ledger.py family --chip w27e257
```

| It reports | Read it as |
|---|---|
| one or more passing members | The path is proven on hardware. Suspect **this chip's data** — pinout key, VPP, chip id, size — before the protocol implementation |
| no passing member | The protocol implementation is **in scope**, not just the data. Nothing has ever passed down this path |

Do not infer the family from the algorithm alone. `w27e257` is algorithm `0x07` like the
passing `w27c512`, but sits on a different pinout and a 13.5 V rail, so it is a
different family with nothing recorded in it.

This is a subprocess call into the sibling skill, not an import — both skills stay
stdlib-only and self-contained. Where `devtest-triage` is not installed, skip the step
and say the family is unknown rather than guessing.

| Evidence from triage | Layer | Where |
|---|---|---|
| Pin map disagrees with the datasheet DIP view | pinout data | `pinouts.json` if the key's wiring is wrong. `resolve_pinout_key()` if the wrong key was chosen |
| Wrong `electrical.type` / erase capability | decode | `classify()` — the `flags & 0x10` axis, not `protocol_id` |
| Wrong VPP | decode | the VPP index table. Mask `voltages & 0xF0`, never `& 0xFF` |
| Wrong algorithm/protocol | decode | `classify()` and the safety-flip rules in `main()` |
| Wrong pulse timing | decode | `interpret_timing()` |
| Chip missing from the DB entirely | supplement | `extra_chips.json`, only if absent from `infoic.xml` |
| Right data, wrong behaviour on the wire | host | `$APP/firestarter/eprom_operations.py`, `serial_comm.py`, `chip_resolver.py` |
| Right command, wrong hardware sequence | firmware | `$FW/src/proms/*.cpp` for the protocol, `src/eprom_operations.cpp` |

Firmware protocol implementations map to the constants in `$FW/include/proto_constants.h`
(`eprom.cpp`, `eeprom_28c.cpp`, `flash_5v_page.cpp`, `flash_nor_unlock.cpp`,
`flash_intel.cpp`, `sram.cpp`). Constants and flag bits are duplicated between
`$APP/firestarter/constants.py` and `$FW/include/firestarter.h` — change both together.

## 3. Regenerate and prove the change

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

A firmware protocol change cannot be checked without a chip on the bench. Say that
explicitly rather than implying the fix is checked.

## 4. Report the fix on the issue

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

Both labels come from the shared taxonomy.
`python3 $ROOT/.claude/skills/devtest-triage/scripts/devtest_issues.py labels`
creates it if the tracker does not have it yet.

Leave the issue **open** either way. A fix you have proven in CI is still unproven on
the reporter's hardware, and that gap is exactly what the label and the version
references exist to close.

## Hard rules

- `chip_database.json` is generated. Editing it is always wrong.
- No generator field without proof in `infoic.xml`. No per-chip guess tables.
- `extra_chips.json` adds chips upstream lacks. It does not override chips upstream has.
- Do not "fix" `PROTO_PHANTOM_0x35` / `0x39` spelling in `proto_constants.h`. Those
  substrings are deliberate.
- Commit any fix atomically, on its own branch.
- **If you hand this investigation to another agent, carry the fix surface with it.**
  An agent with write access does not otherwise know `chip_database.json` is generated,
  and will "fix" the JSON — the change then vanishes at the next regen. Copy the fix
  surface table and the proof rule into whatever prompt you write.
- `dev test` always WRITES to the chip. Never run it, or any other hardware command,
  without the operator's explicit go-ahead.
- **A fix is not reported until the artefact versions are on the issue** (§4). Name the
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
| Fetch of infoic.xml is slow | 17.8 MB. It caches to `$TMPDIR/infoic-<sha>.xml`. Reuse it |
| `gh: 'fix:committed' not found` | The shared taxonomy is not created on this tracker — run `devtest_issues.py labels` from `devtest-triage/scripts` |
| A fix landed but the issue still says `fix:committed` | The release shipped and nobody moved the label. Swap it to `fix:released` and post the version that carries it (§4) |
| Reporter asks "which version has the fix?" | §3's comment was skipped or omitted the artefact table. Read the versions from `version.h` and `__init__.py` — never from memory — and post it |
| A decode looks wrong and `build_db.py` changed recently | The owned table in `infoic_lookup.py` drifted. Update it to match the generator — the generator is authoritative, not this script |
| The generator renamed its VPP table | Find the new name and **re-read every value** — a rename and a value change can arrive in the same commit |
