---
phase: 207-the-version-and-the-record
reviewed: 2026-09-23T16:10:08Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - firestarter_fw/include/version.h
  - firestarter_app/firestarter/__init__.py
  - firestarter_app/README.md
  - firestarter.wiki/Breaking-Changes.md
  - firestarter.wiki/Writing-and-Verifying.md
  - firestarter.wiki/Home.md
  - firestarter.wiki/_Sidebar.md
  - firestarter.wiki/Install-Beta.md
  - firestarter.wiki/Testing-Chips.md
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 207: Code Review Report

**Reviewed:** 2026-09-23T16:10:08Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Phase 207 bumps `firestarter_fw` and `firestarter_app` to `3.1.0b1` and corrects the app README's
mixed-version upgrade sentence. It also ships five wiki pages (three new, two edited) that document
the `3.1.0b1` host-side verify/blank-check move and the CLI/firmware compatibility break.

I traced every checkable factual claim in the wiki set against the actual CLI source
(`cli_handlers.py`, `compare.py`, `constants.py`), the actual `firestarter_fw` source
(`firestarter.h`, `firestarter.cpp`, `eprom.cpp`) and the pinned `--help` snapshots in
`tests/__snapshots__/test_characterization.ambr`. This includes: exit-code tables for `write`,
`verify`, `blank`, `erase -b`; the verdict-line strings for `--verify`; the compare classification
labels (`blank/contact`, `address-line`, `match`, `indeterminate`) and the "at most 64 / … and N
more ranges" cap (`MAX_RETAINED_RANGES = 64`); command ordinals 4 and 6 and their retirement
(`firestarter.h`, `constants.py`); the `ERROR: Unknown command: %d` and `Not blank, at 0x%06x, v:
0x%02x` message formats; the `FLAG_SKIP_BLANK_CHECK` (`0x08`) retirement and the fact that
`build_flags()` no longer composes any wire bit for `blank_check`, which is what makes the "a
3.1.0b1 CLI's plain `erase` against older firmware still runs the old firmware's automatic
post-erase blank check" claim correct rather than a guess; the board-flag table in `Install-Beta`;
the 746-part/59-manufacturer count in the README; and every internal wiki link. All of it checked
out. No planning identifiers (phase numbers, D-NN ids, `.planning/` paths, `v1.4x` labels) leaked
into the published wiki pages.

One factual error was found and is worth a follow-up wiki commit: `Testing-Chips.md` describes
`dev test`'s repeat cycle as running the write-and-verify block **twice**, in five separate places.
The actual default, `_DEFAULT_RUNS = 3` in `cli_handlers.py`, runs it **three** times — confirmed
independently by `dev_test`'s own docstring ("The write/verify block runs as a CYCLE, three times")
and by `chip_test.py`'s tranche/alternation logic, which is parameterized on `cycles` and visibly
produces 3-way behavior (a UV slot split into 3 tranches, an SRAM pattern sequence of
pattern/complement/pattern rather than a single pair). This predates Phase 207 — the wiki page was
last rewritten 2026-08-31 and the default changed to 3 on 2026-09-17 (`b596249`) without the wiki
being updated — but it is live on the wiki today and squarely in scope as a user-facing factual
error about physical hardware use.

## Warnings

### WR-01: `Testing-Chips.md` says `dev test` runs write-and-verify twice; the code runs it three times

**File:** `firestarter.wiki/Testing-Chips.md:39, 48-50, 51-52, 53-55, 60-62`

**Issue:** The page states, in five places, that the non-`--fast` `dev test` sweep performs the
write-and-verify block **twice**:

- Line 39: "It runs the write-and-verify part **twice**."
- Lines 48-50 (UV-erasable EPROM bullet): "...each run moves down to the next unused slot... The
  bits each run would have used are simply split between the two passes, so the chip ends up in
  the same state and lasts just as long."
- Lines 51-52: "**EEPROMs and page-write chips** — written in full, twice."
- Lines 53-55: "**SRAM and FRAM** — written with a pattern, then its exact opposite."
- Lines 60-62: "`dev test --fast` runs the write-and-verify once instead of twice."

The actual default is three cycles, not two:

- `firestarter_app/firestarter/cli_handlers.py:2845`: `_DEFAULT_RUNS = 3`, passed as
  `runs=1 if fast else _DEFAULT_RUNS` into `run_plan` at `cli_handlers.py:2955`.
- `run_plan`'s own docstring (`chip_test.py`) and the `dev_test` command's docstring
  (`cli_handlers.py:2876` area) both say "three times" / "runs as a CYCLE, three times".
- `chip_test.py`'s `_uv_cycle_targets` splits a UV slot's bits into `cycles` tranches (a "uv-tranche
  recipe: N cumulative images out of ONE slot") — with the real default this is a 3-way split, not
  the 2-way split the wiki describes, so a reader estimating how much of a UV EPROM's limited slot
  budget one `dev test` run actually consumes is working from the wrong arithmetic.
- `chip_test.py`'s `_alternating_cycle_targets` (the SRAM/FRAM recipe) produces
  pattern/complement/pattern for 3 cycles, not the single pattern-then-opposite pair the wiki
  describes.

This is user-facing documentation about a command that "writes to the chip every run (no read-only
mode)" against a UV EPROM's limited number of usable slots — a reader is meant to act on this number
when deciding whether to test a UV part.

This staleness predates Phase 207 (the page's own footer says it was "rewritten 2026-08-31", and the
default changed from a lower value to 3 in `b596249`, "feat(dev-test): default the run count to
three for read and write/verify/erase alike", dated 2026-09-17), but the page is live on the
published wiki today and is in this review's file list.

**Fix:** Replace "twice" / "two passes" with "three times" / "three passes" throughout, and correct
the SRAM/FRAM bullet to describe the actual pattern/complement/pattern sequence, e.g.:

```markdown
It runs the write-and-verify part **three times**. ...

- **UV-erasable EPROMs** — one small slot per run, as described above. The bits
  each run would have used are simply split between the three passes, so the chip
  ends up in the same state and lasts just as long.
- **EEPROMs and page-write chips** — written in full, three times. ...
- **SRAM and FRAM** — written with a pattern, then its exact opposite, then the
  pattern again. ...

`dev test --fast` runs the write-and-verify once instead of three times. ...
```

Consider citing `_DEFAULT_RUNS` (or just "the default repeat count") rather than a bare literal, so
a future change to that constant doesn't silently re-strand the page the way this one did.

---

_Reviewed: 2026-09-23T16:10:08Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
