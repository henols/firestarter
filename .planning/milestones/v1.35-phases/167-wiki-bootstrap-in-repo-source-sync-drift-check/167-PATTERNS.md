# Phase 167: WIKI — Bootstrap, In-Repo Source, Sync & Drift Check - Pattern Map

**Mapped:** 2026-08-30
**Files analyzed:** 9 (7 created, 2 modified)
**Analogs found:** 7 / 9

> **Two standing corrections that override "copy the closest analog".**
>
> 1. **The closest analog carries a live defect.** `tools/catalog/sync_to_subrepos.sh:84-86` and
>    `:97-99` run `diff -q "$X" "$X"` — the *same path twice* — then print
>    `OK: … regenerated.`. The comparison is tautologically true and asserts nothing.
>    `.github/workflows/catalog-sync-check.yml` is the same defect class at CI level (5 runs,
>    5 failures, never once asserted its property). Both are the *shape* analogs for this
>    phase's publish command and drift-check workflow, and both are simultaneously cautionary
>    records. Extract the structure; do not carry the self-diff.
> 2. **Zero comments in authored source — project hard rule, no plan may override it.** Every
>    analog below is heavily commented, and `.planning/codebase/CONVENTIONS.md` §"Comment style
>    in infrastructure files" even instructs preserving long rationale comments. **The operator's
>    hard rule wins for anything this phase authors.** Existing files keep their existing
>    comments (do not strip them); new files carry zero. Where an analog uses a comment to carry
>    intent, the new code must relocate that intent into an `argparse` `help=`/`description=`
>    string, a function or variable name, or `wiki/How-This-Wiki-Is-Published.md` (D-12).
>    **All code excerpts below are presented comment-stripped for exactly this reason.**

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tools/wiki/wiki.py` (publish/drift path) | utility CLI | file-I/O + subprocess orchestration | `tools/catalog/sync_to_subrepos.sh` | partial (right data flow, wrong language) |
| `tools/wiki/wiki.py` (CLI skeleton, exit codes) | utility CLI | request-response (argv → exit code) | `tools/catalog/codegen.py` | exact |
| `tools/wiki/wiki.py` (`sidebar` generator) | codegen | transform | `tools/catalog/codegen.py` `main()` + determinism contract | exact |
| `tools/wiki/wiki.py` (`links` walker) | validator | transform | `tools/catalog/codegen.py` `validate_catalog` / `--check` | role-match |
| `tools/wiki/selftest.sh` | test driver | batch | *(none — meta repo has no test harness)* | **none** |
| `.planning/v1.35/MIGRATION-TABLE.md` | doc/provenance table | — | *(none — no in-repo provenance table exists)* | **none** |
| `wiki/Home.md`, `wiki/How-This-Wiki-Is-Published.md` | content | — | `CLAUDE.md` (tone/register only) | weak |
| `wiki/_Sidebar.md` | generated, committed artifact | transform output | `firestarter/include/messages.h` (committed generated file) | role-match |
| `.github/workflows/wiki-check.yml` | CI config | event-driven | `.github/workflows/catalog-sync-check.yml` | exact shape / defective content |
| `CLAUDE.md` (modified) | doc of record | — | itself, line 12 | n/a |
| `.planning/codebase/STRUCTURE.md` (modified) | doc of record | — | itself, lines 26-28, 62-63, 70 | n/a |

## Pattern Assignments

### `tools/wiki/wiki.py` — CLI skeleton and exit-code contract

**Analog:** `tools/catalog/codegen.py:671-735` (exact match; same repo, stdlib-only, argparse, `sys.exit(main())`)

**Shebang + import block pattern** (`codegen.py:1`, `:36-40`):

```python
#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path
```

`CONVENTIONS.md:69` additionally requires `from __future__ import annotations` for stdlib-only
scripts in this project. `codegen.py` omits it; the convention doc is the stated rule — include it.

**Module docstring** — `codegen.py:2-33` uses the docstring as usage text *and* as the home for the
determinism contract and historical rationale. This is the sanctioned place for the explanation
that comments may not carry. `wiki.py`'s docstring is where the exit-code table, the
`--wiki-remote`-is-a-parameter rationale, and the link-form allowlist belong.

**Argparse pattern** (`codegen.py:671-688`, comment-free as written):

```python
def _build_argparser():
    p = argparse.ArgumentParser(
        prog="codegen.py",
        description="Generate firmware/host catalog artifacts from the "
                    "canonical messages.toml.",
    )
    p.add_argument("--catalog", required=True, type=Path,
                   help="Path to messages.toml (canonical or vendored copy).")
    p.add_argument("--check", action="store_true",
                   help="Validate the catalog and exit 0/1. No files written.")
    return p
```

`codegen.py` is flag-only, single-purpose. `wiki.py` needs **subcommands** (`publish`, `sidebar`,
`links`, `check`) — use `p.add_subparsers(dest="command", required=True)`. This is the one place
the analog does not reach; the dispatch-table idiom it *does* supply is directly reusable
(`codegen.py:666-669`):

```python
LANGUAGE_EMITTERS = {
    "cpp":       emit_cpp_header,
    "python":    emit_python,
}
```
→ becomes a `COMMANDS = {"publish": cmd_publish, "sidebar": cmd_sidebar, ...}` map, each returning
an int exit code.

**Exit-code pattern — `main()` returns, `sys.exit` wraps** (`codegen.py:690-735`):

```python
def main():
    args = _build_argparser().parse_args()

    if not args.catalog.is_file():
        print(f"ERROR: catalog file not found: {args.catalog}",
              file=sys.stderr)
        return 2
    ...
    print(f"OK: wrote {args.target} ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**This is a direct hit on RESEARCH § Pattern 3.** The analog already distinguishes **2 = wrong
inputs / precondition not met** from **1 = the asserted property is false**. Carry that split
verbatim: exit 2 = wiki remote absent (must print the operator URL and the literal string
`WIKI-01`), exit 1 = drift / orphan / stale sidebar / illegal name, exit 0 = in sync.
`ERROR:` on stderr and `OK:` on stdout is the established message prefix convention across both
analogs (`codegen.py:696`, `:719`, `:731`; `sync_to_subrepos.sh:44`, `:66`, `:101`).

---

### `tools/wiki/wiki.py` — publish / drift (mirror + commit-only-on-diff)

**Analog:** `tools/catalog/sync_to_subrepos.sh` (partial: correct data flow — authoritative
in-repo source → published target, verify, assert, non-zero on mismatch — but it is bash and its
verification is broken)

**Transferable structure** (`sync_to_subrepos.sh:20-33`, comment-stripped):

```bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_REPO_CATALOG="$SCRIPT_DIR"
FILES=(messages.toml codegen.py)
TARGETS=( "$META_REPO_CATALOG/../../firestarter/tools/catalog" ... )
exit_code=0
```

Four things to carry into `wiki.py`:
1. **Resolve the source directory from the script's own location, not from `cwd`.** In Python:
   `SOURCE_DIR = Path(__file__).resolve().parent.parent.parent / "wiki"`. This is why
   `sync_to_subrepos.sh` runs correctly from anywhere, and `wiki.py` must too.
2. **Missing-source guard before any work** (`:43-46`) — `if [[ ! -f "$src" ]]` → `ERROR:` + exit 1.
   `wiki.py`'s equivalent is the `git ls-remote` probe, but it exits **2**, not 1.
3. **Accumulate then gate** (`exit_code=1` at `:52`, checked at `:57-59`) — report *all* failures
   before exiting, rather than dying on the first. Apply to `links`: report every orphan and every
   broken link in one run, then return 1.
4. **A real cross-copy assertion exists in this file and is worth copying** (`:65-70`) — two
   *distinct* paths compared, error to stderr, `exit 1`:

```bash
if diff -q "$fs_toml" "$fa_toml" >/dev/null; then
    echo "OK: sub-repo catalogs are byte-identical."
else
    echo "ERROR: sub-repo catalogs diverge: $fs_toml vs $fa_toml" >&2
    exit 1
fi
```

**ANTI-PATTERN — do not replicate** (`sync_to_subrepos.sh:84-86`, and identically `:97-99`):

```bash
if diff -q "$FS_ROOT/include/messages.h" "$FS_ROOT/include/messages.h" >/dev/null 2>&1; then
    echo "  OK: firestarter/include/messages.h regenerated."
fi
```

Same operand twice; always true; prints success for a property it never tested; and the failure
branch does not exist, so there is nothing to observe red. **Structural rule this phase must
follow:** for every assertion authored, the two operands must be traceably distinct, *and* the plan
must name the mutation that turns it red and require that red run to be captured. That is precisely
RESEARCH's 11 observed-red cases. Worth filing separately as a live latent defect — it is
out of this phase's scope to fix, but it should not be left undocumented.

**Also do not copy:** the "Idempotent: re-running with no upstream change is a no-op" claim at
`:15`. It is a *docstring assertion with no test*. `wiki.py`'s idempotence must be proven by
`selftest.sh` asserting `git rev-parse master` equality across two `--push` runs.

**Core publish pattern** — RESEARCH § Code Examples supplies the verified mechanism; port it to
`subprocess` list form (Security Domain V5: never `shell=True`):

```python
def _git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True)
```

Sequence: `ls-remote` probe → `clone` (never `init`, per Pitfall 2) → assert
`rev-parse --abbrev-ref HEAD == "master"` → assert worktree `origin` matches the expected remote
*before* any deletion (V12) → wipe worktree except `.git` → copy `wiki/*` → `git add -A` →
`git diff --cached --quiet` → branch on `--push`.

---

### `tools/wiki/wiki.py` — `sidebar` generator

**Analog:** `tools/catalog/codegen.py` — the precedent behind D-10, and per project convention its
emitter is **format-stable**, so byte-stability of `_Sidebar.md` is a pattern *requirement*, not a
nice-to-have.

**Determinism contract** (`codegen.py:24-28`, docstring — reproduce as `wiki.py` docstring text, not
as comments):

```
  - sorting messages by id ascending before emission
  - no timestamps, hostnames, or hashes in the banner
  - LF line endings via Path.write_text(..., newline='\n')
  - explicit dict iteration via sorted(...)
```

**Deterministic emit** (`codegen.py:467`):

```python
return sorted(catalog["messages"], key=lambda m: m["id"])
```

**Emitter shape** (`codegen.py:474-534` pattern, condensed): build a `parts = []` list of strings,
append in sorted order, `return "".join(parts)`. Same for `_Sidebar.md`: `Home` first, then
`sorted()` page stems, `_Sidebar.md` / `_Footer.md` excluded from the list.

**Write pattern** (`codegen.py:725-728`, comment-stripped):

```python
args.target.parent.mkdir(parents=True, exist_ok=True)
args.target.write_text(output, encoding="utf-8", newline="\n")
```

**Freshness-check pattern** — `codegen.py:685-687` + `:711-715` is the exact analog for
`sidebar --check`:

```python
p.add_argument("--check", action="store_true",
               help="Validate the catalog and exit 0/1. No files written.")
...
if args.check:
    print(f"OK: catalog valid ({n} messages, ...).")
    return 0
```

The load-bearing phrase to carry is `help="... No files written."`. `codegen.py`'s `--check` returns
before the `write_text` call, so it structurally cannot rewrite what it checks. Copy that control
flow exactly — RESEARCH § Pattern 5: "a checker that fixes what it is checking reports green
forever."

---

### `tools/wiki/wiki.py` — `links` walker

**Analog:** `codegen.py` `validate_catalog` / `CatalogError` (role-match: a validator that
accumulates rule violations and exits 1).

**Error-class + accumulate pattern** (`codegen.py:254`, `:263`, `:402`, `:412` idiom):

```python
raise CatalogError(
    f"unknown param type {t!r} ({name}). Allowed: {sorted(VALID_PARAM_TYPES)}"
)
```

Note the two reusable habits: an **explicit allowlist constant** named `VALID_*` (`codegen.py:47`,
`:57`, `:75`) whose contents appear `sorted()` in the failure message, and the failure message
naming both the offending value and what was allowed. `wiki.py` gets `ILLEGAL_NAME_CHARS`
(`\ / : * ? " < > |`) and one legal link form, with the same message shape.

**Validate-before-emit ordering** (`codegen.py:29-31` docstring, `:705-709`): "Validation also runs
unconditionally before emission, so an invalid catalog never produces output." Apply: `publish` must
run the offline legs before touching the remote — an orphan or illegal filename must not reach the
wiki.

**Non-tautology rule (no analog — this is new and load-bearing):** reachability evidence comes from
`Home.md` **only**. `_Sidebar.md` is generated to contain every page, so counting sidebar links
makes the orphan check structurally incapable of failing. This is the same defect class as the
`sync_to_subrepos.sh` self-diff above, one abstraction level up — and `sidebar_link_is_not_evidence`
is the negative case that proves it was avoided.

---

### `tools/wiki/selftest.sh`

**No analog. The meta repo has no test harness** (verified: no `pyproject.toml`, no `pytest.ini`,
no `tests/`). The only precedent is `sync_to_subrepos.sh` as a bash driver, and its verification
is the defect above — so the *only* transferable elements are mechanical:

**From `sync_to_subrepos.sh:1`, `:20`:**

```bash
#!/usr/bin/env bash
set -euo pipefail
```

`CONVENTIONS.md:75` records the repo convention as `set -e`; `sync_to_subrepos.sh` uses the
stricter `set -euo pipefail`. Use the stricter form — but note that `set -e` fights exit-code
assertions, so each negative case must capture the code explicitly rather than letting the shell
abort:

```bash
rc=0
python3 "$WIKI_PY" publish --wiki-remote "$FIXTURE" || rc=$?
[[ $rc -eq 1 ]] || { echo "FAIL drift_detected_exit_1: got $rc" >&2; exit 1; }
```

**From `CONVENTIONS.md:76-77`:** progress echoed as `=== Section name ===` banners. Use one banner
per negative case, named exactly as RESEARCH's 11 case ids so plan criteria, selftest output, and
CI log are greppable by the same string.

Fixture setup comes from RESEARCH § Code Examples (verified this session), not from any repo file:
`git init --bare --initial-branch=master`. Per RESEARCH Anti-Patterns, `-b master` is mandatory —
`init.defaultBranch` is unset in this container and a wiki serves only `master`.

**Standing caution attached to this file:** the recorded scar is *"fixture-passing selftests ≠
working tooling"* (~20 v1.34 rig defects, all selftest-green, all failed on first hardware
contact). `selftest.sh` proves the local git mechanism and **nothing** about the service tier.
Whatever the plan writes must not claim otherwise, and the live legs stay gated.

---

### `.github/workflows/wiki-check.yml`

**Analog:** `.github/workflows/catalog-sync-check.yml` — exact shape analog, and a cautionary record.

**Trigger pattern to copy** (`catalog-sync-check.yml:3-16`), with two substitutions:

```yaml
name: Wiki check
on:
  pull_request:
    branches:
    - beta
    paths:
    - 'wiki/**'
    - 'tools/wiki/**'
    - '.github/workflows/wiki-check.yml'
  workflow_dispatch:
```

Copy: path filters scoped to what the check guards, **the workflow's own file inside its own filter
set** (this is the analog's best idea), `workflow_dispatch`, `actions/checkout@v4` (pin the same
major as the one existing workflow — `STRUCTURE.md:188`: "Check out only what the job reads").

**Do not copy** `branches: [main]` (`:6`, `:11`) — D-06: `origin/beta` is 2,842 commits ahead;
a `main`-keyed workflow in this repo is dormant. Ironically the analog's own comment block records
this same `main`-lags-`beta` mistake as the reason it failed 5/5 — the fix was applied to the
sub-repo refs it resolves, not to its own trigger.

**Job pattern** (`:19-22`, `:27-30`):

```yaml
jobs:
  sync-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check out meta-repo
        uses: actions/checkout@v4
        with:
          path: meta
```

Add what the analog lacks and this repo requires: an explicit `permissions:` block. The check job is
`contents: read`; only the later, gated publish workflow gets `contents: write` (repo default
workflow permission is `read`, verified — without the declaration a wiki push 403s).

**Assertion step pattern** (`:88-95`) — comment-free as written, and the shape is right:

```yaml
      - name: Assert vendored catalog matches meta-repo authoritative copy
        run: |
          cmp meta/tools/catalog/messages.toml firestarter/tools/catalog/messages.toml
          diff meta/tools/catalog/messages.toml firestarter/tools/catalog/messages.toml
          echo "OK: meta-repo authority preserved end-to-end"
```

Two distinct operands, relies on the tool's own non-zero exit, `OK:` line last. For
`wiki-check.yml` the whole body reduces to:

```yaml
      - name: Assert wiki source integrity (offline legs)
        run: |
          python3 tools/wiki/wiki.py check
          bash tools/wiki/selftest.sh
```

**Do not copy the comment blocks** (`:1`, `:20-27`, `:32-49`) — project hard rule. Their content is
genuinely valuable, and `CONVENTIONS.md:70-78` explicitly asks for it to be preserved; that
convention is overridden here. Relocate the equivalent rationale to
`wiki/How-This-Wiki-Is-Published.md` (D-12) and the phase record. Leave the existing file's comments
in place — the rule governs what this phase authors.

**Offline legs only.** RESEARCH Pitfall 6: the live wiki-comparison leg's *code* is written and
fixture-proven now, but its CI trigger is wired in the operator-gated task. No red-by-default check,
and specifically **no warn-and-exit-0 fail-open** — that would make the drift check unable to fail
for the one reason it exists. The `catalog-sync-check.yml` scar is what a red-by-default check
becomes: ignored.

---

### `wiki/_Sidebar.md` (generated, committed)

**Analog:** `firestarter/include/messages.h` / `firestarter_app/firestarter/messages.py` — generated
by `codegen.py`, **committed**, regenerated by `sync_to_subrepos.sh:78-95`, CI-asserted.

This is the precedent D-10 rests on: generated files in this project are committed, not produced at
consumption time. The regeneration call site pattern (`sync_to_subrepos.sh:79-82`) is a plain
invocation of the generator with explicit paths:

```bash
python3 "$META_REPO_CATALOG/codegen.py" \
    --catalog "$META_REPO_CATALOG/messages.toml" \
    --language cpp \
    --target "$FS_ROOT/include/messages.h"
```

`wiki.py publish` calls its own `sidebar` code path the same way — in-process, one function, not a
second subprocess. The `OK:`-printing block that *follows* this call in the analog is the self-diff
anti-pattern; the correct successor is `sidebar --check` comparing generated-in-memory against the
committed file.

---

### `CLAUDE.md` and `.planning/codebase/STRUCTURE.md` (modified)

No pattern to copy — these are targeted factual corrections. Both become false the moment `wiki/`,
`tools/wiki/` and a second workflow exist:

| File | Line | Current text | Why it becomes false |
|------|------|--------------|----------------------|
| `CLAUDE.md` | 12 | "This repo tracks only `.planning/` … and `.claude/`" | `wiki/` and `tools/wiki/` are new tracked top-level paths |
| `STRUCTURE.md` | 26-28 | tracked-root enumeration ending `tools/`, `CLAUDE.md`, `.gitignore`, `.gitmodules` | omits `wiki/` |
| `STRUCTURE.md` | 62-63 | "`catalog-sync-check.yml` # TRACKED — the repo's **ONLY** workflow" | there will be two |
| `STRUCTURE.md` | 70 | `tools/catalog/messages.toml` is the only `tools/` entry shown | `tools/wiki/` missing |

Edit in the same phase, per RESEARCH Pitfall 8 — otherwise the next codebase mapper records the
drift as a defect.

## Shared Patterns

### Message prefixes and stream discipline
**Source:** `codegen.py:696`, `:719`, `:731`; `sync_to_subrepos.sh:44`, `:51`, `:66`, `:101`
**Apply to:** `wiki.py`, `selftest.sh`, `wiki-check.yml`

`ERROR: <what> <offending value>` to **stderr**; `OK: <property asserted>` to **stdout**, last.
Both analogs are consistent on this and it is what makes CI logs greppable.

### Non-zero exit is the assertion; the message is for the human
**Source:** `catalog-sync-check.yml:88-95`, `sync_to_subrepos.sh:68-69`
**Apply to:** every leg of `wiki.py`, every case in `selftest.sh`

Never `|| true`, never `--allow-empty`, never swallow a code. RESEARCH names
`git commit --allow-empty` and `git commit || true` as criterion-3 killers specifically.

### Two operands must be traceably distinct, and the red state must have been seen
**Source:** the **inversion** of `sync_to_subrepos.sh:84-86` / `:97-99`
**Apply to:** all 11 negative cases; the `sidebar --check` freshness leg; the CI assertion step

The single most important pattern in this map, and the only one derived by negation. A comparison
whose operands come from one variable, a failure branch with no test, and a green CI leg whose red
state nobody has seen are all the same defect. This repo has shipped all three.

### Stdlib-only, no installs
**Source:** `codegen.py:33` ("Stdlib only"); `CONVENTIONS.md:69`; `CONVENTIONS.md:79-80` (skills own
their scripts, no cross-repo imports)
**Apply to:** `tools/wiki/wiki.py`

No package, no import path, no `sys.path` surgery — `tools/wiki/` is not a package, exactly as
`tools/catalog/` is not. This is also the structural reason pytest was priced and rejected.

### Black formatting, editor-enforced only
**Source:** `CONVENTIONS.md:91-92`
**Apply to:** `wiki.py`

There is no lint or format config in the tracked meta-repo root and no CI formatting leg. Match
`codegen.py`'s hand-aligned style; do not add a formatter config as a side effect of this phase.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tools/wiki/selftest.sh` | test driver | batch | No test harness of any kind exists in the meta repo. Mechanics (`set -euo pipefail`, `=== banner ===`) come from `sync_to_subrepos.sh` + `CONVENTIONS.md:75-77`; the fixture and exit-code-assertion structure comes from RESEARCH § Code Examples and § Validation Architecture. |
| `.planning/v1.35/MIGRATION-TABLE.md` | provenance table | — | No checked-in provenance/mapping table exists in this repo. Shape is defined by D-04 plus Pitfall 4's **rendered-title column** — use RESEARCH, not a codebase analog. |
| `wiki/Home.md`, `wiki/How-This-Wiki-Is-Published.md` | content | — | No published-documentation page exists in the meta repo (`doc/` lives in the sub-repos and is Phase 168's input, not a pattern source). `CLAUDE.md` is the closest register match. Content is fixed by D-09 and D-12 — Home carries the curated list plus the D-06 beta-vs-released caveat; the second page carries the WIKI-02 authority rule and the overwrite warning. |
| `wiki-publish.yml` | CI config | event-driven | Deliberately **not created in this phase** (RESEARCH § Recommended Project Structure: "ADDED IN THE GATED TASK, not before the wiki exists"). Its analog when authored is `wiki-check.yml` plus the mandatory `permissions: contents: write` block. |

## Metadata

**Analog search scope:** `tools/`, `.github/workflows/`, repo root, `.planning/codebase/`
**Files scanned:** 7 read (`sync_to_subrepos.sh`, `codegen.py`, `catalog-sync-check.yml`,
`CLAUDE.md`, `STRUCTURE.md`, `CONVENTIONS.md`, plus directory listings); 4 strong analogs retained
**Pattern extraction date:** 2026-08-30
