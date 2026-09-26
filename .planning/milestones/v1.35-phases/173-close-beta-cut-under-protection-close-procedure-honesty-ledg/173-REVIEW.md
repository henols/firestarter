---
phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg
reviewed: 2026-09-02T18:02:08Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - tools/wiki/provenance_footers.py
  - .github/workflows/wiki-check.yml
  - .planning/v1.35/MIGRATION-TABLE.md
  - CLAUDE.md
findings:
  critical: 2
  warning: 2
  info: 2
  total: 6
status: issues_found
---

# Phase 173: Code Review Report

**Reviewed:** 2026-09-02T18:02:08Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

`provenance_footers.py` is a new bidirectional guard: it verifies a migrated wiki page carries
the footer its `MIGRATION-TABLE.md` row states (row → wiki direction) and that every live wiki
page has a row (wiki → row direction). The row → wiki direction is well built: `_resolve_row_page`
correctly resolves symlinks before the containment check, so a table row naming a page outside
`--wiki-dir` is reported as `UNSAFE ROW` and never opened — verified this holds even when the
row's target is itself a symlink escaping the directory.

The wiki → row direction (`load_pages` / `check_page_accounting`'s live-page enumeration) does
not get the same treatment. It has no containment check and no error handling at all, even
though it walks a fresh clone of a wiki the tool explicitly does not control. Two problems follow
directly from that gap and are demonstrated below: an unhandled crash on any unreadable/broken
file among the live pages, and a silent symlink escape that the row-driven direction would have
caught and reported. Both sit on the path `check_page_accounting` runs on every non-`--emit`
invocation, i.e. every real CI run of the `Provenance footer check` leg.

There is also a real, demonstrated parsing gap: `parse_tables` never validates that a row's cell
count matches the header's, so a stray unescaped `|` inside any cell (a plausible slip in a
Markdown table, e.g. a source path or an edits note) silently shifts every subsequent column and
drops the last one, rather than failing the row loudly.

`wiki-check.yml` and `MIGRATION-TABLE.md` (as parser input) were reviewed and are sound; findings
below are confined to `provenance_footers.py`. `CLAUDE.md`'s two verifiable factual claims
(`git.base_branch: beta` in `.planning/config.json`, and the `ship.md` merge-base anchor at the
cited line) both check out against the actual files.

## Critical Issues

### CR-01: `load_pages()` crashes the whole checker on any unreadable file in the untrusted wiki clone

**File:** `tools/wiki/provenance_footers.py:119-125` (invoked at `tools/wiki/provenance_footers.py:179`)
**Issue:** `check_page_accounting` (run on every non-`--emit` invocation, before any output is
produced) calls `load_pages(wiki_dir)`, which globs every `*.md` file in the wiki clone and calls
`path.read_text(...)` on each with no error handling. The wiki clone is explicitly the untrusted
input this tool exists to check ("a wiki whose contents it does not control" — module docstring).
A single broken symlink, permission-denied file, or unreadable device-like target among the live
pages takes the whole process down with an unhandled Python traceback instead of the tool's own
designed failure vocabulary (`PAGE MISSING` / `UNRECORDED PAGE` / exit 1) or its degenerate-input
contract (exit 2). Verified directly:

```
$ ln -sf /nonexistent/target wiki/Broken-Symlink.md
$ python3 -c "...pf.load_pages(Path('wiki'))..."
CRASH: FileNotFoundError [Errno 2] No such file or directory: 'wiki/Broken-Symlink.md'
```

This also means a symlink to something that blocks on read (e.g. a FIFO with no writer) would
hang the job rather than fail fast — worse than a crash, since it burns the runner's timeout
instead of reporting anything.

**Fix:** Guard the read and turn any failure into the tool's own vocabulary instead of letting it
propagate:
```python
def load_pages(wiki_dir: Path) -> dict[str, str]:
    pages: dict[str, str] = {}
    for path in sorted(wiki_dir.glob("*.md")):
        if path.name in NAV_EXCLUDED_PAGES:
            continue
        if not path.is_file():
            continue
        try:
            pages[path.name] = path.read_text(encoding="utf-8")
        except OSError as exc:
            pages[path.name] = ""  # or: raise a dedicated failure the caller reports
    return pages
```
and have `check_page_accounting` surface unreadable pages as a named failure (e.g.
`UNREADABLE PAGE: {name} — {exc}`) rather than letting the caller's exception escape `main()`.

### CR-02: Live-page enumeration has no path-containment check — a symlink escaping `--wiki-dir` is silently followed and read

**File:** `tools/wiki/provenance_footers.py:119-125`
**Issue:** The row-driven direction (`_resolve_row_page`, lines 128-135) deliberately resolves the
candidate path and rejects anything outside `--wiki-dir` before it is opened — this is the
documented, tested safety property ("must be reported, not opened"). `load_pages()` has no
equivalent check: it reads whatever `wiki_dir.glob("*.md")` yields, following symlinks with no
containment test. Verified: a symlink placed inside the wiki clone that points to a file outside
it is read without any complaint, and — because its filename happens to line up with a real table
row — the run reports clean:

```
$ ln -sf ../outside/secret.md wiki/Escape-Row.md   # outside/secret.md exists, is a real file
$ python3 -c "...pf.check_page_accounting([row_naming_Escape-Row], Path('wiki'))..."
[]   # no failure reported — the escape is invisible to this direction of the check
```
(The `check_footers`/`_resolve_row_page` direction *does* catch the identical scenario when the
table row is the thing under test — see the module's own `UNSAFE ROW` handling — but nothing
protects the reverse direction, where the live file itself is the symlink.)
**Fix:** Apply the same resolve-and-contain pattern used by `_resolve_row_page` to the glob
results before reading them:
```python
def load_pages(wiki_dir: Path) -> dict[str, str]:
    base = wiki_dir.resolve()
    pages: dict[str, str] = {}
    for path in sorted(wiki_dir.glob("*.md")):
        if path.name in NAV_EXCLUDED_PAGES:
            continue
        resolved = path.resolve()
        try:
            resolved.relative_to(base)
        except ValueError:
            continue  # or report as its own failure kind
        pages[path.name] = resolved.read_text(encoding="utf-8")
    return pages
```

## Warnings

### WR-01: `parse_tables` silently misaligns columns on any row with more cells than the header

**File:** `tools/wiki/provenance_footers.py:95`
**Issue:** `tables[key].append(dict(zip(header, cells)))` never checks `len(cells) ==
len(header)`. A row with an unescaped `|` inside any cell (a source path, a repo name, an edits
note — any of these are free text in `MIGRATION-TABLE.md` today) produces one extra cell, which
`zip` silently truncates at the header's length — shifting every subsequent column by one and
discarding the true last value entirely, with no error. Verified against a synthetic row with a
stray `|` in `Source path`:
```
input row:  | firestarter | firestarter/doc/A|B.md | Foo | Foo | aaaa...(40) | 168 | — |
parsed as:  {'Source repo': 'firestarter', 'Source path': 'firestarter/doc/A',
             'Wiki page': 'B.md', 'Rendered title': 'Foo',
             'Pre-deletion SHA': 'Foo', 'Moved in': 'aaaa...(40)',
             'Post-move edits': '168'}   # true "—" value silently dropped
```
This particular shift happens to produce values that would very likely fail loudly downstream
(a garbage `Wiki page` or non-hex `Pre-deletion SHA`), so it is unlikely to create a silent pass
today — but the parser gives no guarantee of that, and a differently-shaped malformation could
land on values that still validate. This is exactly the "malformed row" class the parser should
detect explicitly rather than rely on incidental downstream failures to catch.
**Fix:** Validate cell count immediately after computing `cells`, and treat a mismatch as a named
parse failure rather than a silent `zip` truncation:
```python
if len(cells) != len(header):
    raise SystemExit(
        f"ERROR: row has {len(cells)} cell(s), header has {len(header)}: {line!r}"
    )
```
(or accumulate it as a failure and exit 2, consistent with the module's other precondition checks).

### WR-02: `check_footers` never verifies the `---` rule that `emit_footers` always writes

**File:** `tools/wiki/provenance_footers.py:151-161` (contrast with the block `emit_footers`
produces at `tools/wiki/provenance_footers.py:196-198`)
**Issue:** `emit_footers` always writes `\n\n---\n\n<footer line>\n` — a horizontal rule
separating the footer from the page body. `check_footers` only inspects `lines[-1]` (the last
non-blank line) against `FOOTER_RE`; it never checks that a `---` rule (or even a blank-line gap)
precedes it. Verified: a page whose footer line is glued directly onto the last paragraph, with no
rule and no blank line, passes with zero failures:
```
# Title

some content

*Relocated from `...` in `...` at `...`. Moved intact and not edited since; not re-verified against the code.*
```
```
check_footers([...]) -> []   # passes; no rule was ever required
```
This also means a page with a stray duplicate footer block sitting above the real trailing one
(e.g. from a `--emit` run whose earlier-footer-stripping regex failed to match, see below) would
never be flagged, since only the final line is examined.
**Fix:** Require the trailing block to match the same shape `emit_footers` writes — reuse
`_TRAILING_FOOTER_BLOCK_RE` (already defined) to assert the footer is preceded by the rule, instead
of independently re-deriving "last non-blank line":
```python
if _TRAILING_FOOTER_BLOCK_RE.search(text) is None:
    failures.append(f"FOOTER MISSING: {page}")
    continue
```

## Info

### IN-01: Dead branch in `check_page_accounting`'s live-page stem computation

**File:** `tools/wiki/provenance_footers.py:181`
**Issue:** `stem = name[:-3] if name.endswith(".md") else name` — `name` always comes from
`load_pages(wiki_dir)`, whose keys are drawn from `wiki_dir.glob("*.md")` (line 121), so
`name.endswith(".md")` is always `True` and the `else name` branch is unreachable.
**Fix:** `stem = name[:-3]` (drop the dead branch), or add a comment-free assertion if defensive
coding against a future `load_pages` signature change is wanted.

### IN-02: `check_footers`'s own safety branches are unreachable through `main()`

**File:** `tools/wiki/provenance_footers.py:142-150`
**Issue:** `check_footers` re-implements the `UNSAFE ROW` / `PAGE MISSING` checks that
`check_page_accounting` already performs over the superset `main_rows`. Since `main()` calls
`check_page_accounting` first and returns 1 immediately on any failure (line 249-253), by the time
`check_footers` runs, every row in `eligible_rows` has already passed those same checks — so lines
142-150 are dead code on the only path that actually invokes `check_footers` (`main()`). Harmless
today, but it is duplicated logic that will drift silently if one copy is fixed and the other is
not.
**Fix:** Either drop the duplicate checks from `check_footers` (since `main()` already guarantees
the precondition) and rely on `main()`'s ordering, or make the duplication intentional and testable
by having `check_footers` also be reachable standalone with its own test coverage — pick one and
document the choice in the exit-code contract's ordering guarantee already stated in the module
docstring.

---

_Reviewed: 2026-09-02T18:02:08Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
