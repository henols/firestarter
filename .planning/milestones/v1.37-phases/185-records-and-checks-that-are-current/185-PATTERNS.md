# Phase 185: Records and Checks That Are Current - Pattern Map

**Mapped:** 2026-09-11
**Files analyzed:** 16 (4 created, 11 modified, 7 deleted)
**Analogs found:** 15 / 16

All analog paths below were verified `git ls-files`-tracked in their own repo (meta, `firestarter/`,
`firestarter_app/`). No gitignored mirror is cited. `firestarter_app/build/lib/firestarter/cli_handlers.py`
is explicitly NOT an analog — it is an untracked stale build artifact.

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|---|
| `tests/fixtures/captured_build_v185_{uno,uno328pb,leonardo}.log` | fw | test fixture | file-I/O (captured transcript) | `tests/fixtures/captured_build_v158_{same}.log` | exact |
| `tests/fixtures/planted_size_baseline_flash_regression_v185.log` | fw | test fixture (planted) | file-I/O (derived transcript) | `tests/fixtures/planted_size_baseline_flash_regression_v158.log` | exact |
| `scripts/baseline/size_baseline.json` (M) | fw | config/record | batch record | its own prior generation (git history at 158-04) | exact |
| `tests/test_check_size_baseline.py` (M) | fw | test | request-response (subprocess) | **itself**, lines 523-547 and 610-635 (the v158 severance docstrings) | exact (self) |
| `tests/fixtures/captured_test_native_summary.log` (M, in place) | fw | test fixture | file-I/O | itself, prior 172→184 in-place update | exact (self) |
| 6 orphaned `captured_build_{fullflash,v132,v151}_*.log` (D) | fw | test fixture | — | Phase 184's orphaned `planted_dispatch_*` deletion | role-match |
| `firestarter/cli_handlers.py` (M: delete `_is_interactive`) | app | utility | — (dead symbol) | — | no analog needed (pure deletion) |
| `tests/test_dev_test_cmd.py` (M: 51 unwraps + docstring) | app | test | request-response (CliRunner) | **itself** — the 5 multi-CM shapes + the sole-CM shape below | exact (self) |
| `tools/check_devtest_orchestrator.py` (M: :66 prose, :163 allow-list) | app | gate/utility | transform (AST scan) | itself — the two literals | exact (self) |
| `tests/test_check_devtest_orchestrator.py` (M: :585 docstring) | app | test | transform | itself — the same docstring's own `_default_uv_write_confirm` / `_is_uv_eprom` supersession sentences | exact (self) |
| `tests/test_numeric_schema_source_scan.py` (M: :40) | app | test | transform (AST scan) | **line 127-134 of the same file** | exact (self) |
| `.github/workflows/catalog-sync-check.yml` (D) | meta | CI config | — | — | no analog (unique deletion) |
| `tools/catalog/sync_to_subrepos.sh` (M: :84-86, :97-99) | meta | script | file-I/O | **lines 47-53 and 65-70 of the same file** | exact (self) |
| `.planning/notes/<catalog-sync-check-retirement>.md` (N) | meta | record | — | `.planning/notes/ae29f2008-classification-verdict.md`, `.planning/notes/jumper-display-ground-truth.md` | exact |
| `.planning/REQUIREMENTS.md` § CLAIM-08 (M) | meta | record | — | 183 D-08 / 184 D-03 in-phase amendments | role-match |
| `.planning/ROADMAP.md` § Phase 185 criterion 5 (M) | meta | record | — | same | role-match |

---

## Pattern Assignments

### `firestarter/tests/fixtures/captured_build_v185_*.log` (fixture, file-I/O)

**Analog:** `firestarter/tests/fixtures/captured_build_v158_uno.log` (86 lines; all three v158 captures are 86 lines)

**Shape to reproduce — head** (lines 1-12, no ANSI, `pio run` non-TTY framing):
```
Processing uno (platform: atmelavr; board: uno; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
CONFIGURATION: https://docs.platformio.org/page/boards/atmelavr/uno.html
PLATFORM: Atmel AVR (5.2.0) > Arduino Uno
HARDWARE: ATMEGA328P 16MHz, 2KB RAM, 32KB Flash
DEBUG: Current (avr-stub) External (avr-stub, simavr)
PACKAGES:
 - framework-arduino-avr @ 5.3.0
 - toolchain-atmelavr @ 1.70300.191015 (7.3.0)
LDF: Library Dependency Finder -> https://bit.ly/configure-pio-ldf
LDF Modes: Finder ~ chain, Compatibility ~ soft
```

**Shape to reproduce — tail** (the gate-bearing region; `compare_avr` parses only the `RAM:`/`Flash:`
`(used N bytes from M bytes)` tails):
```
Archiving .pio/build/uno/libFrameworkArduino.a
Indexing .pio/build/uno/libFrameworkArduino.a
Linking .pio/build/uno/firestarter_uno.elf
Checking size .pio/build/uno/firestarter_uno.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [=======   ]  70.0% (used 1434 bytes from 2048 bytes)
Flash: [=======   ]  70.0% (used 22952 bytes from 32768 bytes)
Building .pio/build/uno/firestarter_uno.hex
========================= [SUCCESS] Took 1.21 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:01.213
========================= 1 succeeded in 00:00:01.213 =========================
```

**Capture recipe (the six-generation convention, NOT `--rebuild`):**
```bash
rm -rf ".pio/build/$e" && pio run -e "$e" 2>&1 | tee "tests/fixtures/captured_build_v185_$e.log"
```
Diff the new capture's *shape* (line count, section order) against the v158 sibling before committing.

---

### `firestarter/tests/fixtures/planted_size_baseline_flash_regression_v185.log` (fixture, derived)

**Analog:** `planted_size_baseline_flash_regression_v158.log` — derived from `captured_build_v158_leonardo.log`.

**Exact derivation, measured this session** (`diff captured_build_v158_leonardo.log planted_..._v158.log`):
```
79c79
< Flash: [========  ]  76.6% (used 25098 bytes from 32768 bytes)
---
> Flash: [========  ]  78.2% (used 25610 bytes from 32768 bytes)
```
**One changed line, at the same line number, in the whole file.** `RAM:` untouched; the percentage and
bar columns were recomputed by hand in the v158 plant but are never parsed (the parser anchors on the
`(used N bytes from M bytes)` tail). The `+512 B` offset is the standing convention since Phase 123.

---

### `firestarter/tests/test_check_size_baseline.py` (test, request-response)

**Analog: the file itself.** v158 wrote **per-leg docstring paragraphs only** and added no
module-docstring section — copy that.

**Severance paragraph pattern** (lines 523-547, `test_clean_avr_all_three_envs_pass`):
```python
def test_clean_avr_all_three_envs_pass():
    """Coverage 1 — each captured_build_v158_*.log exits 0 against the LIVE
    default baseline, and its PASS: line names the env.

    SEVERED again by Plan 158-04 (LAND-01): Phase 158 re-recorded
    scripts/baseline/size_baseline.json's avr_targets.*.flash_used/.ram_used to the
    cold post-narrowing figures (uno 22952/1434, ...), which the *_v153* family no
    longer matches (it still carries the pre-narrowing, higher figures) -- feeding it
    here would have made this leg permanently RED. The *_v153* family itself is NOT
    touched: it is retired, not repointed. This leg instead reads a new fixture
    family, captured_build_v158_{uno,uno328pb,leonardo}.log, committed byte-for-byte
    from a cold `rm -rf .pio/build/<env>` + single `pio run -e <env>` invocation per
    env, never re-derived warm and never read from `--rebuild`.

    SEVERANCE, this generation: ... the four legs named there (this one, the native
    leg, the planted-regression leg and the default-mode leg below) are the exhaustive
    set that couples to a baseline value move, and no fifth leg was found red at this
    generation's start."""
```
Four required elements per paragraph: (1) `SEVERED ... by Plan NNN-NN`, (2) *why* the prior family
would go red, (3) the explicit "prior family is NOT touched — retired, not repointed", (4) a
`SEVERANCE`/`RECONCILIATION` paragraph reconciling predicted vs observed red-leg count.

**Planted-leg paragraph pattern** (lines 610-635) additionally states the false-cause argument and the
diff shape:
```python
    """... would make the checker fail for TWO reasons (flash_used has already
    diverged before the plant is even applied) instead of the one this leg names --
    exactly the false-green/false-cause pattern this project's own fixture-severance
    precedent exists to avoid. ... with the same +512 B offset every prior version of
    this fixture has used since Phase 123 (25098 + 512 = 25610) ... Diffed against its
    own capture: exactly one changed line, the Flash: line, with the RAM: line and
    every other byte identical.

    RECONCILIATION: this leg was correctly anticipated in `158-before-figures.md`
    §6 as one of the four legs coupled to the live baseline's value; no
    false-cause surprise was observed at this generation ..."""
```

**In-place update pattern for the native pair** (lines 565-575) — note the wording that makes the
in-place choice read as a decision, and that the fixtures were *genuinely re-captured*:
```python
    """Coverage 2 — both captured_test_native*.log files exit 0 with 184 and 17 in PASS:.

    Plan 158-04 (LAND-01) updated captured_test_native_summary.log and
    captured_test_native_nodevtools_summary.log IN PLACE again, 172 -> 184
    cases/succeeded (suites unchanged at 17) -- both were genuinely RE-CAPTURED
    from real `pio test -e native` / `-e native_nodevtools` runs at this phase's
    final tree position, following the same in-place convention Phase 149 Plan 07,
    Plan 151-10 and Plan 153-15 all used."""
```

**Body edits are mechanical** — the fixture name literal in the tuple, and the two numeric assertions:
```python
    for env_name, fixture in (
        ("uno", "captured_build_v158_uno.log"),        # -> v185
        ("uno328pb", "captured_build_v158_uno328pb.log"),
        ("leonardo", "captured_build_v158_leonardo.log"),
    ):
    ...
    assert "25098" in result.stdout   # -> new leonardo baseline
    assert "25610" in result.stdout   # -> new baseline + 512
```

---

### `firestarter_app/tests/test_dev_test_cmd.py` (test, request-response)

**Analog: the file itself.** Four DISTINCT call-site shapes exist. Excerpted once each.

**Shape A — sole context manager, 46 sites.** Delete the `with` line and dedent the body 4 spaces:
```python
        with _off_tty():
            result = runner.invoke(cli, ["dev", "test", _CHIP_UV], obj=app)
        assert result.exit_code in (0, 1, 2), result.output
```
becomes
```python
        result = runner.invoke(cli, ["dev", "test", _CHIP_UV], obj=app)
        assert result.exit_code in (0, 1, 2), result.output
```

**Shape B — first in a parenthesized multi-CM, 1 sibling → collapses** (lines 949-953, 1275-1278,
i.e. the `patch.dict(os.environ, ...)` and `patch("firestarter.submit.submit_report")` sites):
```python
        with (
            _off_tty(),
            patch.dict(os.environ, {"FIRESTARTER_CONFIG_DIR": str(custom_dir)}),
        ):
            result = runner.invoke(cli, ["dev", "test", _CHIP_NO_ID], obj=app)
```
becomes a single-CM `with` (NOT `with (X,):` — `ruff format --check` reds on that):
```python
        with patch.dict(os.environ, {"FIRESTARTER_CONFIG_DIR": str(custom_dir)}):
            result = runner.invoke(cli, ["dev", "test", _CHIP_NO_ID], obj=app)
```

**Shape C — first in a multi-CM with 2 siblings → keep the parenthesized form** (lines 1301-1306):
```python
        with (
            _off_tty(),
            patch("firestarter.submit.webbrowser.open", mock_browser_open),
            patch("firestarter.submit.subprocess.run", mock_run_fn),
        ):
```
→ delete only the `_off_tty(),` line; indentation unchanged.

**Shape D — `_off_tty()` is NOT first** (line 1964-1967 second position; line 2183 last position after
a multi-line `patch(...)` call). Delete that one line; the survivor collapses to a single-CM `with`:
```python
        with (
            patch("firestarter.cli_handlers.run_plan", side_effect=KeyboardInterrupt),
            _off_tty(),
        ):
```

**The helper to delete** (lines 518-520):
```python
def _off_tty():
    """Context manager forcing the off-TTY branch (D-03)."""
    return patch("firestarter.cli_handlers._is_interactive", return_value=False)
```

**The direct-patch sites (D-06 / research §B.3) — three, not two.** Shape:
```python
        with patch("firestarter.cli_handlers._is_interactive", return_value=True):
            result = runner.invoke(cli, ["dev", "test", _CHIP_UV], obj=app)
```
- `test_uv_part_writes_one_slot_on_a_tty` (:836) — MERGE away; its assertion
  `assert "write-partial" in {s["op"] for s in data["steps"]}` is byte-identical to its sibling's.
- `test_uv_part_writes_one_slot_off_a_tty_too` (:850) — SURVIVOR, renamed to carry no TTY claim.
- `test_non_uv_part_is_still_written_in_full_without_a_prompt` (:864) — drop the patch AND the
  docstring's *"TTY or not"* clause; the name needs no rename.

**Module docstring, the false clause to DELETE** (lines 8-14) — under the no-comments rule the
permitted operation is deletion, not replacement prose:
```
TTY-gating is controlled by patching the module-level `firestarter.cli_handlers.
_is_interactive` function directly (NOT `sys.stdin.isatty`) because
`click.testing.CliRunner.invoke` replaces `sys.stdin` with its own stream
for the duration of the call, so a `patch("sys.stdin.isatty", ...)` applied
before `invoke()` silently does not survive (documented in cli_handlers.py's
`_is_interactive` docstring and 112-02-SUMMARY.md's Issues Encountered).
```

---

### `firestarter_app/tests/test_numeric_schema_source_scan.py:40` (test, transform)

**Analog: line 127-134 of the same file** — the symbol-and-scope form, already correct:
```python
    """ast-parse `source_text` and collect the name of every top-level
    (`tree.body`-only, NOT `ast.walk`) `Assign`/`AnnAssign` whose value is a
    dict literal. Deliberately does NOT recurse into function bodies,
    `for`/`if`/`with` blocks, etc. -- that scoping is exactly what keeps
    this helper from firing on `_AT28C_DIP24_NAMES`, a local variable
    nested inside a `for` loop deep in `main()`, addressing an unrelated
    pre-existing Phase 76/D-03 physical-adapter classification."""
```

**The defect to repair** (lines 40-43), whose surrounding sentence already carries the scope prose:
```
     on `_AT28C_DIP24_NAMES` (build_db.py:594) -- that set literal (not
     even a Dict) is a LOCAL variable nested inside a `for` loop several
     indent levels deep, addressing a pre-existing, unrelated Phase 76/D-03
     physical-adapter classification, not a module-level construct at all.
```
Replace the `(build_db.py:594)` parenthetical with the line-129 scope form (`a local variable nested
inside a `for` loop deep in `main()`` — or simply drop the parenthetical, since the scope is already
stated in the next clause). Do NOT write `538`, `545` or `594`.

---

### `firestarter_app/tests/test_check_devtest_orchestrator.py:585` (test, transform)

**Analog: the same docstring.** It already contains the exact pattern for retiring a named example —
two prior supersessions written in place:
```python
    The assertion here is a SUBSET, never an equality, because
    `_is_interactive` is legitimately listed but not referenced from
    `dev_test`'s body -- an equality assertion would be red for the opposite
    reason on day one. `_default_uv_write_confirm` used to be the other such
    entry; it went when the UV write prompt was retired (quick task
    260822-aq6). `_is_uv_eprom` used to be the third such entry; Phase 181
    plan 04 made it body-referenced by inlining the deleted write-scope
    helper's rule at `dev_test`'s own `derive_plan` call site.
```
**The repair is a name substitution inside existing prose** — swap `_is_interactive` for a still-live
listed-but-not-body-referenced example (`_verdict_code` or `_overall_exit_code`, both called only
indirectly via `_dev_test_exit_code`). Authoring no new paragraph keeps the edit inside what the
no-comments rule permits.

---

### `tools/catalog/sync_to_subrepos.sh` (script, file-I/O) — D-14

**Analog: lines 47-53 and 65-70 of the same file.**

**Idiom 1 — two-operand `cp` + `diff -q "$src" "$dst"`, with an `else`** (lines 47-53):
```bash
        cp "$src" "$dst"
        if diff -q "$src" "$dst" >/dev/null; then
            echo "  copied: $f -> $target"
        else
            echo "ERROR: copy mismatch: $src vs $dst" >&2
            exit_code=1
        fi
```

**Idiom 2 — the one correct cross-sub-repo assertion, with `>&2` + `exit 1`** (lines 65-70):
```bash
if diff -q "$fs_toml" "$fa_toml" >/dev/null; then
    echo "OK: sub-repo catalogs are byte-identical."
else
    echo "ERROR: sub-repo catalogs diverge: $fs_toml vs $fa_toml" >&2
    exit 1
fi
```

**The two tautologies to replace** (lines 84-86 and 97-99) — same path twice, no `else`:
```bash
if diff -q "$FS_ROOT/include/messages.h" "$FS_ROOT/include/messages.h" >/dev/null 2>&1; then
    echo "  OK: firestarter/include/messages.h regenerated."
fi
```
```bash
if diff -q "$FA_ROOT/firestarter/messages.py" "$FA_ROOT/firestarter/messages.py" >/dev/null 2>&1; then
    echo "  OK: firestarter_app/firestarter/messages.py regenerated."
fi
```
Note the existing generation step writes `--target` **directly onto the committed path** (lines 79-82 /
92-95); the repair must generate to a `mktemp` path, `cp` it into place, then `diff` tmp-vs-installed —
two traceably distinct operands (research §E.3). Keep plain `cp` (not `cp -f`) so the RED proof is
reachable. This file is in the **meta** repo, so the no-comments rule does not bind it — but the
existing style carries no per-assertion commentary anyway; match it.

---

### `.planning/notes/<catalog-sync-check-retirement>.md` (record) — D-03

**Analogs:** `.planning/notes/ae29f2008-classification-verdict.md` (183) and
`.planning/notes/jumper-display-ground-truth.md` (182).

**Frontmatter + verdict-first structure** (from `ae29f2008-classification-verdict.md:1-14`):
```markdown
---
title: AE29F2008 classification verdict — algorithm 5 is correct, and gh#62 is correct too
date: 2026-09-11
context: v1.37 Phase 183, SAFE-09 — re-verified in this session against 183-RESEARCH.md §B
---

# AE29F2008 classification verdict (SAFE-09)

## THE VERDICT

**AE29F2008 is classified `algorithm 5` CORRECTLY. ...**

**This verdict is equivalence-based, not a direct datasheet reading.** ...
```

**Evidence-chain section with executed commands quoted verbatim** (same file):
```markdown
## THE EVIDENCE CHAIN

Three legs, each re-verified in this session (commands and outputs below) ...

**Leg (a) — the classification is an upstream transcription, not a generator decision.** ...

```
$ cd /workspaces/firestarter_app && /usr/bin/grep -n '0x05, 0x06, 0x0D, 0x10' tools/build_db.py
356:    if proto_id in {0x05, 0x06, 0x0D, 0x10}:
```
```

**Ground-truth source table** (from `jumper-display-ground-truth.md`):
```markdown
| Revision family | Source | Status |
|---|---|---|
| Rev 0 / Rev 1 (identical, per operator) | `firestarter/document/rurp_schematics_rev1.pdf` | Read 2026-07-10 |
```

**Explicit self-correction of a prior claim** (same file) — the shape D-03 bullet 3 needs:
```markdown
Note: an earlier research pass claimed Rev 0/1 routing was undocumented
(gerbers-only upstream). Wrong — the rev1 PDF ships in the firmware sub-repo
itself.
```
and the in-table supersession form: *"**corrected 2026-09-10 (Phase 182):** ... Superseded the prior
single-destination claim"*.

The note must carry all five D-03 contents. Both analogs put the *verdict* first and the evidence
second, quote primary sources verbatim, and name what the evidence does **not** establish.

---

## Shared Patterns

### Evidence-gathering commands (apply to every file in this phase)
**Source:** research §B.4, CONTEXT.md § Measurement traps
```bash
git grep -n "_is_interactive"      # tracked-only: immune to ugrep's .gitignore under-scan
                                   # AND to build/lib/'s untracked false positive
/usr/bin/grep -nE "\.py:[0-9]+" <file>   # only when a gitignored path is irrelevant
```
Never plain `grep` for gate evidence — the devcontainer's `grep` is ugrep and honors `.gitignore`.

### No comments in sub-repo source
**Source:** `/workspaces/CLAUDE.md` § "Source code comments — hard rule"
**Apply to:** every edit under `firestarter/` and `firestarter_app/`.
Permitted operations for a stale record: **delete the false clause**, or **substitute a name inside an
existing docstring**. Not permitted: authoring a replacement explanatory paragraph. Docstrings are in
scope (not comments); `tools/catalog/sync_to_subrepos.sh` is meta-repo and unbound.

### In-phase requirement amendment
**Source:** 183 D-08, 184 D-03
**Apply to:** `.planning/REQUIREMENTS.md` CLAIM-08, `.planning/ROADMAP.md` § Phase 185 criterion 5.
State the conflict first, then the amended wording, then the precedent, inline. **Hand edits only** —
`gsd-tools query requirements/roadmap` verbs reformat the whole file and this ROADMAP is hand-authored.

### RED-first proof
**Source:** 183-04, 184 D-13
**Apply to:** D-14's sync-script repair.
Plant the break, observe and **transcribe the verbatim error line and `rc`**, then restore by explicit
path (`git -C <repo> checkout -- <path>`). Never `git clean`.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `.github/workflows/catalog-sync-check.yml` (deletion) | CI config | — | It is the meta repo's **only** workflow; no sibling exists and no prior workflow retirement happened in this repo. The nearest precedent is the `tools/wiki/` + `wiki-check.yml` retirement (2026-09-02, `5426d7ef`) — that is a precedent for *recording an absence*, not a code pattern to copy. |

`firestarter/cli_handlers.py`'s `_is_interactive` removal is a pure deletion with zero call sites and
needs no analog.

## Metadata

**Analog search scope:** `/workspaces/tools/catalog/`, `/workspaces/.planning/notes/`,
`/workspaces/.github/workflows/`, `firestarter/tests/{fixtures,}`, `firestarter/scripts/baseline/`,
`firestarter_app/{tests,tools,firestarter}/`
**Files scanned:** 14 read (5 fixture logs, 4 test modules, 1 shell script, 2 notes, 2 workflow/JSON)
**Tracked-source gate:** `git ls-files` run per-repo over all 11 cited analog paths — all tracked
**Pattern extraction date:** 2026-09-11
