# Phase 168: MIGRATE — The 13 `doc/` Files, Moved Without Upgrading a Claim - Pattern Map

**Mapped:** 2026-08-31
**Files analyzed:** 14 new/modified code-and-config artifacts (plus 30 pure text-repair targets, not pattern-mapped)
**Analogs found:** 12 / 14

> **HARD OPERATOR RULE — carry into every plan.** No comments are written into product source, ever
> — not provenance, not explanatory. The two sub-repos (`firestarter/`, `firestarter_app/`) are
> product source. Where an excerpt below contains comments, it is presented for its **structure**,
> never as a template for comment style. The one stated exception is meta-repo infrastructure
> (`tools/**`, `.github/workflows/**`), where `.planning/codebase/CONVENTIONS.md:79-93` explicitly
> keeps long rationale comments — the analogs `wiki.py`, `selftest.sh` and `catalog-sync-check.yml`
> all live there.

---

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|------|-----------|----------------|---------------|
| `tools/wiki/honest01_claims.py` (new, one-shot) | meta | checker/CLI | batch / transform (git-read → multiset compare) | `tools/wiki/wiki.py` | exact |
| `tools/wiki/honest02_truth.py` (new, standing gate) | meta | checker/CLI | batch (file-I/O + JSON lookup) | `tools/wiki/wiki.py` | exact |
| `tools/wiki/claim-vocabulary.json` (new) | meta | config/data | file-I/O (rules-as-data) | `tools/catalog/messages.toml` (+ `firestarter_app/tools/baseline/chip_database.baseline.json`) | role-match |
| `tools/wiki/wiki.py` (modify: delete 3 subcommands, add `_Sidebar` containment leg, repoint `DEFAULT_SOURCE_DIR`) | meta | checker/CLI | request-response (argparse dispatch) | itself — `cmd_links` / `check_orphans` | exact |
| `tools/wiki/selftest.sh` (modify: −7 cases, +3 cases) | meta | test driver | batch | `case_orphan_exit_1` (`selftest.sh:137-161`) | exact |
| `.github/workflows/wiki-check.yml` (rewrite) | meta | config/CI | event-driven (schedule + dispatch) | `.github/workflows/catalog-sync-check.yml` | exact |
| `.github/workflows/wiki-publish.yml` (delete) | meta | config/CI | — | — (deletion) | n/a |
| `.planning/v1.35/MIGRATION-TABLE.md` (modify: +SHA column, 12 rows, prose repair) | meta | data/record | file-I/O | itself `:9-24` | exact |
| `firestarter_app/tools/build_db.py` (modify `:543`, `:569`) | app | generator | transform (emit) | itself `:543-569` | exact |
| `firestarter_app/firestarter/data/chip_database.json` (regenerate) | app | generated data | batch | `build_db.py` run + `diff_db.py` gate | exact |
| `firestarter_app/tests/test_dispatch_mirror.py` (modify `:5,37,38`) | app | test | file-I/O at module scope | `tests/fw_presence.py:117-140` (`fw_path`) | exact |
| `firestarter_app/tests/scan_paths.py:113` (remove entry) | app | test inventory | data | `test_scan_paths_resolve.py:47` (`_FLOOR = 6`) | exact |
| 5 doc-leg test modules (split doc legs out) | app | test | file-I/O | `test_py32_packaging.py:55` + `:236-258` | exact |
| Relocated `test_dispatch_mirror` doc leg — **destination undecided** | ? | test/checker | ? | **none** — see §No Analog Found | none |
| `firestarter_app/tests/fixtures/fake_firestarter/doc/PROTOCOLS.md` (rekey/delete) | app | fixture | file-I/O | `test_fw_presence.py:218` (`include/firestarter.h` marker) | partial |

---

## Pattern Assignments

### `tools/wiki/honest01_claims.py` and `tools/wiki/honest02_truth.py` (checker/CLI, batch)

**Analog:** `tools/wiki/wiki.py` (542 lines, stdlib-only). D-07 mandates this shape: a `python3`
script with the 0/1/2 exit contract, driven by `selftest.sh`. **No pytest, no `pyproject.toml`, no
`tests/` may be introduced in the meta repo.**

**Exit-code contract — copy verbatim into each new checker's module docstring** (`wiki.py:1-30`,
condensed to the load-bearing part):

```python
#!/usr/bin/env python3
"""
tools/wiki/<name>.py -- single stdlib-only CLI ...

Exit-code contract:
  0 = the asserted property holds
  1 = the asserted property is false
  2 = a precondition was not met (source directory missing, or wiki
      remote absent)

--source-dir and --wiki-remote are parameters, not module constants,
because that is what makes every offline negative case testable against
a fixture before the operator creates the real GitHub wiki.
"""
```

**Imports pattern** (`wiki.py:32-40`) — stdlib only, `from __future__ import annotations`, `Path`:

```python
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
```

(The new checkers additionally need `json`, `hashlib`, `collections.Counter`, `subprocess` for
`git show`. `difflib`, `shutil`, `tempfile` are the publish-only imports being deleted.)

**Module-constant pattern** (`wiki.py:43-58`) — every path/name/regex is a module constant, never
inlined at a call site:

```python
DEFAULT_SOURCE_DIR = Path(__file__).resolve().parent.parent.parent / "wiki"
HOME_PAGE = "Home.md"
NAV_EXCLUDED_PAGES = ("_Sidebar.md", "_Footer.md")
_LEGAL_TARGET_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*(?:#[A-Za-z0-9_-]*)?")
```

**The three-outcome signalling pattern — a check function returns a list of failure strings; the
`cmd_*` wrapper turns it into 0/1** (`wiki.py:210-249`):

```python
def check_orphans(source_dir: Path) -> list[str]:
    failures: list[str] = []
    home = source_dir / HOME_PAGE
    if not home.is_file():
        failures.append(f"orphan check requires {HOME_PAGE} to exist")
        return failures
    ...
    return failures


def cmd_links(args: argparse.Namespace) -> int:
    source_dir = args.source_dir
    failures = check_page_names(source_dir)
    failures += check_link_forms(source_dir)
    failures += check_orphans(source_dir)
    if failures:
        for message in failures:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    ...
    print(
        f"OK: {len(pages)} pages, all reachable from {HOME_PAGE}, all "
        "internal links resolve, all filenames legal."
    )
    return 0
```

Reporting conventions to copy exactly: failures go to **stderr** prefixed `ERROR: `; the success
line goes to **stdout** prefixed `OK: ` and **carries the count of things actually checked**. That
count is the anti-vacuity surface — HONEST-01's D-04 zero-counts and HONEST-02's per-leg counts
belong in that same line or immediately above it.

**Exit 2 — precondition, at `main()` before dispatch** (`wiki.py:527-540`):

```python
def main() -> int:
    args = _build_argparser().parse_args()

    if not args.source_dir.is_dir():
        print(
            f"ERROR: source directory not found: {args.source_dir}",
            file=sys.stderr,
        )
        return 2

    return COMMANDS[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
```

**Exit-2 on a data-load failure — the sibling precedent** (`firestarter_app/tools/diff_db.py:718-731`).
This is the shape for HONEST-02 loading `chip_database.json` and `claim-vocabulary.json`, and for
HONEST-01 loading the vocabulary and `MIGRATION-TABLE.md`:

```python
def _load_db(path, label):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot load {label} {path}: {e}", file=sys.stderr)
        sys.exit(2)
```

`diff_db.py:1-20` also documents its 0/1/2 contract in the module docstring with a per-code
rationale — the same doc shape, from the app repo, confirming this is a project-wide convention and
not a `wiki.py` local habit.

**Reuse, do not re-implement** (`wiki.py:109-139`): `strip_code_spans` and `extract_internal_links`
are already selftested and are the normalisation step HONEST-01's multiset comparison needs
(RESEARCH §Don't Hand-Roll). Both new checkers may import them from `wiki.py` (same directory,
`sys.path` sibling) or the plan may factor them into a shared module — but they must not be
re-written as fresh regexes.

```python
def strip_code_spans(text: str) -> str:
    def _fence_repl(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    text = _FENCE_RE.sub(_fence_repl, text)
    return _INLINE_CODE_RE.sub(lambda match: " " * len(match.group(0)), text)
```

---

### `tools/wiki/claim-vocabulary.json` (config/data, file-I/O)

**Analogs (two, both role-match — no exact "checker reads its rules from committed JSON" precedent
exists in the meta repo):**

1. **`tools/catalog/messages.toml` + `tools/catalog/codegen.py`** — the meta repo's only existing
   committed-data-consumed-by-tooling pair. `codegen.py:39` imports `tomllib`; `:463` is the single
   parse point (`return tomllib.loads(text)`); `:675-678` makes the data-file path a CLI flag with a
   default, not a hardcoded constant:

   ```python
   parser.add_argument("--messages", ...,
                       help="Path to messages.toml (canonical or vendored copy).")
   ```

   ```python
   except tomllib.TOMLDecodeError as e:   # codegen.py:700 — parse failure is its own exit path
   ```

   **Copy:** data path is a flag with a module-constant default; one parse point; parse failure is a
   distinct exit path (exit 2 per the contract above).

2. **`firestarter_app/tools/baseline/chip_database.baseline.json` + `diff_db.py:33-40`** — an
   env-overridable path constant pair, the shape to use if the planner wants a fixture override
   without a flag:

   ```python
   DB_FILE = os.environ.get(
       "FIRESTARTER_DB_FILE",
       os.path.join(_DATA_DIR, "chip_database.json"),
   )
   ```

**Divergence to state in the plan:** the vocabulary file is JSON, not TOML — `messages.toml` uses
TOML because `codegen.py` is a code generator with a rich schema, and `tomllib` is 3.11+. The
meta-repo system Python is 3.12 so `tomllib` is available, but `json` is the lower-floor choice and
RESEARCH already specifies a JSON shape (`168-RESEARCH.md` §"Recommended vocabulary data-file shape",
with `schema_version`, `families`, `expected_zero`). Use JSON; state the reason.

---

### `tools/wiki/wiki.py` — surgery (D-20) and the new WIKI-05 leg (D-06)

**Delete — exact current line ranges** (RESEARCH §"Retiring `tools/wiki/`", re-confirmed against the
live file this session):

| Symbol | Lines | Note |
|---|---|---|
| `generate_sidebar` | 72-82 | |
| `cmd_sidebar` | 84-106 | |
| `cmd_check` | 252-274 | |
| `_git` | 276-282 | publish-only helper |
| `safe_remote` | 284-286 | publish-only helper |
| `cmd_publish` | 288-421 | |
| `COMMANDS` entries `"sidebar"`, `"check"`, `"publish"` | 423-428 | keep `"links"` |
| `sidebar_parser` block | 461-471 | |
| `check` subparser | 486-495 | |
| `publish_parser` block | 497-521 | incl. `--push`, `--require-wiki` |
| `DEFAULT_WIKI_REMOTE`, `WIKI_BRANCH` | 43, 44 | publish-only |
| `--wiki-remote` on the common parser | 431-448 | no surviving subcommand consumes it |
| imports `difflib`, `shutil`, `subprocess`, `tempfile` | 35-40 | become unused |
| module docstring `Subcommands:` block, `Determinism contract` paragraph | 12-28 | describe `sidebar`/`check`/`publish` |
| `SIDEBAR_PAGE` | 47 | **keep** — the new D-06 containment leg reuses it |

**The current `COMMANDS` table and the exact post-surgery target:**

```python
COMMANDS = {
    "sidebar": cmd_sidebar,
    "links": cmd_links,
    "check": cmd_check,
    "publish": cmd_publish,
}
```
→
```python
COMMANDS = {
    "links": cmd_links,
}
```

**`DEFAULT_SOURCE_DIR` (`:45`) points at `<repo>/wiki`, the directory this phase deletes.** Left
alone, `main()`'s exit-2 precondition fires on every default invocation. Either make `--source-dir`
required or default it to a conventional clone path — decide and state which.

**The new `_Sidebar.md` containment leg — write it as a new `check_*` function in the
`check_orphans` shape** (`wiki.py:210-228`, quoted above). Semantics: **set containment**
(`{pages} ⊆ {sidebar entries}`), ordering- and wording-tolerant. Do **not** resurrect
`generate_sidebar`'s byte-equality — that is wrong for a hand-maintained file. Add its failures into
`cmd_links`'s `failures` accumulator so it reports through the same 0/1 path, and extend the `OK:`
line's count so the new leg is visible when green.

**Semantics that stay unchanged (D-06):** `HOME_PAGE`/`NAV_EXCLUDED_PAGES` (`:46,48`) — only
`Home.md` counts as reachability evidence, `_Sidebar.md` does not. `check_page_names` (141-166),
`check_link_forms` (169-207), `render_title`/`page_files`/`page_stems` (60-70) are untouched.

---

### `tools/wiki/selftest.sh` — three new cases

**Analog:** `case_orphan_exit_1` (`selftest.sh:137-161`) — the shortest complete case, and the one
whose new siblings most closely resemble it. **Copy this shape exactly:**

```bash
case_orphan_exit_1() {
    local src="$WORK/orphan_exit_1_src"
    new_source_dir "$src"
    local ok=0

    local control_rc
    control_rc=$(rc_of orphan_exit_1_control.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "orphan_exit_1_control" 0 "$control_rc" || ok=1

    printf '%s\n' '# Page Orphan' '' 'Fixture body with no internal links.' > "$src/Page-Orphan.md"
    python3 "$WIKI_PY" sidebar --source-dir "$src" >/dev/null

    local mutated_rc
    mutated_rc=$(rc_of orphan_exit_1_mutated.log python3 "$WIKI_PY" links --source-dir "$src")
    assert_rc "orphan_exit_1" 1 "$mutated_rc" || ok=1

    if ! grep -q 'Page-Orphan' "$WORK/orphan_exit_1_mutated.log"; then
        echo "ERROR: orphan_exit_1: stderr missing Page-Orphan" >&2
        ok=1
    fi

    record "orphan_exit_1" 1 "$mutated_rc" "$control_rc" "orphan absent from Home.md"

    return "$ok"
}
```

Every element is load-bearing and must appear in each new case: a **green control run first**
(proves the fixture is otherwise valid, so the RED is attributable to the mutation), the mutation,
the RED run, a **grep of the captured log for the specific offending name** (an exit-1 for the wrong
reason is not evidence), the `record` row, and `return "$ok"`.

> **Note for the planner:** this case's `python3 "$WIKI_PY" sidebar ...` line invokes a subcommand
> D-20 deletes. It exists only to keep the fixture's `_Sidebar.md` consistent. When adapting this
> case as a template — and when keeping `case_orphan_exit_1` itself — that line must go or be
> replaced by a literal `printf` of the sidebar. Same hazard in `case_sidebar_link_is_not_evidence`
> (`:163-197`), which is a **keeper** case: check it for `sidebar` invocations.

**Fixture helpers — real signatures** (`selftest.sh:17-27`):

```bash
new_source_dir() {
    local dir="$1"
    mkdir -p "$dir"
    printf '%s\n' '# Home' '' '[Page One](Page-One)' > "$dir/Home.md"
    printf '%s\n' '# Page One' '' 'Fixture body with no internal links.' > "$dir/Page-One.md"
    printf '%s\n' '- [Home](Home)' '- [Page One](Page-One)' > "$dir/_Sidebar.md"
}

new_bare_wiki() {
    git init --bare --initial-branch=master -q "$1"
}
```

Both take **one positional argument, a path**, and neither returns anything. Driver helpers:
`rc_of <logname> <cmd...>` (echoes the rc, captures stdout+stderr to `$WORK/<logname>`),
`record <case> <expected> <observed> <control> <note>`, `assert_rc <case> <expected> <observed>`
(`:29-63`).

**The three new cases, against those real signatures:**

| New case | Fixture | Mutation | Expected |
|---|---|---|---|
| `honest01_weakened_claim_exit_1` | `new_source_dir` for the wiki side + a **git repo** for the source side (the D-02 `git show <sha>:doc/<file>` read path needs one — `new_bare_wiki` is bare and cannot serve `show`; a `git init` + commit helper is a **new helper the plan must add**) | soften one `adapter-required` to "may need an adapter" on the wiki side | rc 1, log names the DROPPED token |
| `honest02_absent_part_number_exit_1` | `new_source_dir` + a minimal fixture `chip_database.json` | a stamped page claiming a part number absent from the fixture DB | rc 1, log names the part number |
| `wiki05_unreferenced_page_exit_1` | `new_source_dir` | add a page listed in `_Sidebar.md` but not linked from `Home.md`; **and** a page linked from Home but absent from `_Sidebar.md` (the new containment leg) | rc 1, log names each page |

**Case registration** (`selftest.sh:481`) — a single flat array; the runner and the
`OK: selftest complete (N cases)` count derive from it, so the array is the only place a case is
enabled:

```bash
CASES=(stale_sidebar_exit_1 sidebar_deterministic orphan_exit_1 ... deleted_page_removed)
```

Post-surgery: 12 − 7 + 3 = **8 cases**. The `OK: selftest complete (8 cases)` line is itself a
verifiable phase artifact.

**Delete these 7 cases with their `CASES=` entries:** `stale_sidebar_exit_1` (65-96),
`sidebar_deterministic` (97-136), `wiki_absent_exit_2` (277-309), `drift_detected_exit_1` (310-345),
`hand_edit_overwritten` (346-395), `idempotent_head_unchanged` (396-431), `deleted_page_removed`
(432-480).

---

### `.github/workflows/wiki-check.yml` (config/CI, event-driven — rewrite)

**Analog:** `.github/workflows/catalog-sync-check.yml`. **RESEARCH falsified `submodules: recursive`**
(the gitlinks pin `a218b4f5` / `cb189a9b`, both pre-dating this phase). Use the named-checkout +
branch-resolver pattern instead.

**The cautionary comment block — read it, do not copy it into the new file verbatim**
(`catalog-sync-check.yml:22-29`, `:35-52`). It records: no `submodules: recursive`, an accidental
gitlink once killed the checkout before any assertion ran, and **5 runs / 5 failures / 2026-07-11 to
2026-08-18 without ever asserting its property**. The new workflow *should* carry its own rationale
comment naming the failure it prevents (meta-repo infra is exempt from the no-comments rule per
`CONVENTIONS.md:79-85`) — but it must be the new workflow's own reasoning, not a copy.

**Branch resolver — copy this step near-verbatim** (`catalog-sync-check.yml:53-67`):

```yaml
      - name: Resolve sub-repo ref (same branch name, else beta)
        id: subref
        run: |
          CAND="${{ github.head_ref || github.ref_name }}"
          echo "meta ref under test: $CAND"
          for repo in firestarter firestarter_app; do
            if git ls-remote --exit-code --heads \
                 "https://github.com/henols/$repo.git" "$CAND" >/dev/null 2>&1; then
              RESOLVED="$CAND"
            else
              RESOLVED="beta"
            fi
            echo "${repo}_ref=$RESOLVED" >> "$GITHUB_OUTPUT"
            echo "$repo -> $RESOLVED"
          done
```

> Under a `schedule` trigger `github.head_ref` is empty and `github.ref_name` is the default branch,
> so the resolver lands on `beta` for both sub-repos. That is the correct standing-gate behaviour —
> but the plan must **state** it rather than let it be inferred, because the resolver's comment text
> is written for a PR trigger.

**Named checkout** (`catalog-sync-check.yml:30-33`, `:69-81`) — meta at `path: meta`, sub-repo at an
explicit `repository:` + `path:` + resolved `ref:`. This phase needs only meta + `firestarter_app`
(for `chip_database.json`):

```yaml
      - name: Check out meta-repo
        uses: actions/checkout@v4
        with:
          path: meta

      - name: Check out firestarter_app (host sub-repo)
        uses: actions/checkout@v4
        with:
          repository: henols/firestarter_app
          path: firestarter_app
          ref: ${{ steps.subref.outputs.firestarter_app_ref }}
```

**Assertion-step style** (`catalog-sync-check.yml:83-87`) — a plain `run:` block that ends with an
explicit `echo "OK: ..."` naming the property proved:

```yaml
      - name: Assert cross-sub-repo vendored catalog identity
        run: |
          cmp firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
          echo "OK: vendored messages.toml byte-identical across sub-repos"
```

**Trigger and permissions** — take `permissions: contents: read` from the file being replaced
(`wiki-check.yml:15-16`) and the `workflow_dispatch:` key from `catalog-sync-check.yml:16`. The wiki
clone is **anonymous** (RESEARCH: verified, the repo is public); use a plain `git clone`, not
`actions/checkout` (whose `repository:` cannot address a `.wiki.git`):

```yaml
      - name: Clone the published wiki
        run: git clone --depth 1 https://github.com/henols/firestarter_prom.wiki.git wiki-clone
```

**D-05 — two independent checker steps after one shared clone**, so a database failure and a
navigation failure arrive as two attributable REDs. This is the reason the two checkers are separate
steps and not one aggregator; the deleted `cmd_check` (`wiki.py:252-274`) is the anti-pattern —
it collapsed two legs into one verdict.

**Delete:** `.github/workflows/wiki-publish.yml` (34 lines), including its
`secrets.WIKI_PUSH_TOKEN || secrets.GITHUB_TOKEN` env at `:18`. Also delete the now-dead
`wiki-drift-live` job (`wiki-check.yml:26-35`) — it invokes `publish --require-wiki`.

---

### `firestarter_app/tools/build_db.py` (generator, transform) — D-14

**Analog:** itself. Both sites are inside one `if _chip_aliases & _AT28C_DIP24_NAMES:` arm.

**`:543` — a `#` comment. Under the operator rule this is a DELETION, not a repoint.** Its
surrounding block (`:535-545`) is comment-only; the whole run of comment lines naming the doc path
goes:

```python
                # The DIP24→DIP32 remap lives in firestarter/doc/AT28C04-ADAPTER.md.
```

**`:565-569` — the emitted, operator-visible string. This one is EDITED, not deleted** (it is
`unsupported_reason`, surfaced by `firestarter info`):

```python
                if _chip_aliases & _AT28C_DIP24_NAMES:
                    _support_status = "adapter-required"
                    _unsupported_reason = (
                        "adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical "
                        "DIP24-to-DIP32 adapter; see firestarter/doc/AT28C04-ADAPTER.md"
                    )
```

Under D-13 the replacement names the **wiki page title**, not a URL and not a path. The
`"adapter required:"` prefix is pinned by
`tests/test_build_db_inclusion.py:539` (`test_adapter_required_reason_starts_with_adapter_required`)
— it must survive the edit.

**Regeneration + verification commands** (RESEARCH-verified this session):

```bash
cd firestarter_app && python tools/build_db.py     # no CLI args; fetches infoic.xml from a pinned
                                                   # gitlab commit a8efaedc; REQUIRES gitlab.com
python tools/diff_db.py                            # expect RC=0
```

Round trip is byte-identical against `HEAD` today, so any diff after the edit is exactly the 9
`unsupported_reason` rows.

**Do NOT re-baseline `tools/baseline/chip_database.baseline.json`.** Measured: `diff_db.py` returns
RC=0 with all 9 reason strings mutated — it is indifferent to the text. The baseline is a pinned
historical snapshot (last re-anchored Phase 98, `362bfa0`) consumed by six modules; re-anchoring is
the move this project has learned reddens unrelated legs. Its 9 copies of the path are historical
evidence, which is D-18's own reasoning. **State the exclusion with its reason.**

---

### `firestarter_app/tests/test_dispatch_mirror.py` and the four sibling doc modules (test, file-I/O)

**Two different path-resolution patterns exist, and only one raises. This is H-1 and it is the
phase's single hardest ordering constraint.**

**Pattern A — the raiser. `test_dispatch_mirror.py:38` only** (via `fw_path`):

```python
from tests.fw_presence import FW_ROOT, fw_path, requires_fw

_FA_DIR = pathlib.Path(__file__).parent.parent

_PROTOCOLS_MD = fw_path("doc", "PROTOCOLS.md")
```

`fw_path` (`tests/fw_presence.py:117-140`) — the raise, verbatim:

```python
def fw_path(*parts: str) -> Path:
    resolved = FW_ROOT.joinpath(*parts)
    if FW_REPO_PRESENT and not resolved.exists():
        raise MissingScanTargetError(
            f"{resolved} does not exist, but the firmware repo IS present "
            f"(marker found at {FW_REPO_MARKER}). This scan target was "
            "renamed or moved -- update this path (or the cross-repo "
            "scan-path inventory) rather than removing or bypassing this "
            "gate."
        )
    return resolved
```

Called at **module scope**, this aborts pytest **collection** — 0 tests run, not 1 module red.
Its error text names the fix; follow it (update the path or the inventory), do not bypass the gate.

**Pattern B — the five safe modules.** Pure `pathlib.Path` construction, no filesystem access at
import; `read_text()` happens inside test bodies. The canonical instance is
`test_py32_packaging.py:52-55`:

```python
_APP_DIR = Path(__file__).parent.parent
_PYPROJECT = _APP_DIR / "pyproject.toml"
_FIRMWARE_PY = _APP_DIR / "firestarter" / "firmware.py"
_INSTALL_DOC = _APP_DIR / "doc" / "PY32F071-FIRMWARE-INSTALL.md"
```

Same shape at `test_lockable_proms_doc_claims.py:48`, `test_protection_table_citations.py:33`,
`test_lock_status_class_partition.py:81`, `test_protect_flags_doc_measurements.py:47-49`.

**Sequencing consequence for the planner:** the five Pattern-B modules can have their doc legs
removed/relocated *after* the delete — only their assertions go red. `test_dispatch_mirror.py:38`
and `tests/scan_paths.py:113` must be repaired **in the same commit as, or before,** the firmware
`doc/` deletion. Warning sign: `Interrupted: N error during collection` with a non-zero collected
count.

`tests/scan_paths.py:113` — remove the entry; the floor at `test_scan_paths_resolve.py:47` is
`_FLOOR = 6`, so 8 → 7 entries stays legal.

---

### Non-vacuity assertion — **the project standard, applies to every new checker**

**Source:** `firestarter_app/tests/test_py32_packaging.py`. The stated rule
(`:31-40`, module docstring):

> **Non-vacuity (research finding A-7).** A scan that finds nothing must never read as a pass. Every
> gate below asserts its scan target was located at all — the `py32 = [` block, `def flash_method(`,
> and the install doc's §3 heading — before comparing anything the scan found. Each gate's assertion
> body is factored into a helper the real leg and a fail-closed planted-file leg both call.

**The implementation, verbatim** (`:236-258`) — the shape every new checker's read path must follow:

```python
def _read_install_doc() -> str:
    assert _INSTALL_DOC.exists(), (
        f"{_INSTALL_DOC} does not exist -- every downstream assertion about "
        "its contents would be vacuously true (research finding A-7)"
    )
    text = _INSTALL_DOC.read_text(encoding="utf-8")
    assert text, f"{_INSTALL_DOC} is empty"
    assert _INSTALL_DOC_SECTION_3_HEADING in text, (
        f"{_INSTALL_DOC_SECTION_3_HEADING!r} not found in {_INSTALL_DOC} -- "
        "the address/outcome assertions below would be vacuously true "
        "against a doc section that was never actually located "
        "(research finding A-7)"
    )
    return text
```

**Three legs, in order: exists → non-empty → the document's own anchor is present.** Translated to
the 0/1/2 contract (the meta repo has no `assert`-based harness), each of these becomes an early
`return 2` (precondition) or an appended failure string, never a silent pass:

- HONEST-01: each `git show <sha>:doc/<file>` must produce non-empty text **and** the mapped wiki
  page must exist — before any Counter is compared. A page that failed to resolve must not compare
  as "0 dropped".
- HONEST-02: the database must load and yield >0 rows; the delimited claim region must be **found**
  on a stamped page before any token is resolved against it. RESEARCH Pitfall 3 is the concrete
  failure this prevents (`SHIELD-REVISIONS.md` — zero database chips — reports 11 of 20 `0xNN`
  tokens "resolving" by numeric coincidence).
- D-04's zero counts (`vpp-exceeds-max`, `UNVERIFIED`, `PROTOCOL-LEDGER`) must print as an explicit
  **"0 of 0 — VACUOUS, not checked"** line, never folded into the `OK:` line.

The companion pattern is the **fail-closed planted-file leg** (`test_py32_packaging.py:340-348`):
monkeypatch the module's path constant at a planted file that passes non-vacuity but lacks the
asserted content, proving the gate can genuinely fail. In `selftest.sh` terms that is exactly the
`control_rc` (green) + `mutated_rc` (red) pair of `case_orphan_exit_1`.

---

### `.planning/v1.35/MIGRATION-TABLE.md` (data/record, file-I/O)

**Analog:** itself, `:9-24`. Pipe table, one row per file, `TBD` as the explicit unfilled marker
(which makes `! grep -q TBD .planning/v1.35/MIGRATION-TABLE.md` a one-line completeness gate):

```markdown
| Source repo | Source path | Wiki page | Rendered title | Moved in |
|---|---|---|---|---|
| firestarter_prom | — | Home | Home | 167 |
| firestarter | firestarter/doc/PROTOCOLS.md | TBD | TBD | TBD |
```

D-02 adds a **pre-deletion SHA column**. **H-2: the SHAs must be recorded before the delete commits,
or the HONEST-01 oracle is gone.** Read path, verified this session:

```bash
git -C firestarter show <sha>:doc/PROTOCOLS.md
```

**Prose repair required:** `:3-7` states "`wiki.py publish` does not read this table, and never will"
and describes a mechanical publish path — false once D-20 deletes `publish`. Keep the table, repair
the prose.

---

## Shared Patterns

### The 0/1/2 exit contract
**Source:** `tools/wiki/wiki.py:6-10` (contract), `:527-540` (exit 2 at `main()`),
`firestarter_app/tools/diff_db.py:11-19` + `:718-731` (exit 2 on a data-load failure).
**Apply to:** both new checkers, and the modified `wiki.py`.
2 means *the check could not run*; 1 means *the property is false*. A CI consumer keying on the exit
status must never confuse a missing input with a real gate failure.

### `ERROR:` to stderr, `OK: <count> ...` to stdout
**Source:** `wiki.py:231-249`.
**Apply to:** both new checkers, every new `selftest.sh` case's grep assertion, every workflow
assertion step (`catalog-sync-check.yml:87`).
The `OK:` line **must carry the count of things actually checked** — that count is what makes a
vacuous pass visible.

### Green control before RED mutation
**Source:** `selftest.sh:137-161` (`control_rc` then `mutated_rc`, both `record`ed);
`test_py32_packaging.py:340-348` (planted-file fail-closed leg).
**Apply to:** all three new selftest cases, and to the phase's criteria 4/5/8 evidence.
An exit-1 without a green control is not attributable to the mutation. Additionally grep the
captured log for the **specific** offending name — an exit-1 for the wrong reason is not evidence.

### Rules as committed data, path as a flag
**Source:** `tools/catalog/codegen.py:675-678` + `:463`; `diff_db.py:33-40`.
**Apply to:** `claim-vocabulary.json` and HONEST-02's database path.
One parse point; a module-constant default; a flag (or env var) override so every fixture case is
testable offline. This is the same reasoning `wiki.py:20-22` gives for `--source-dir`.

### Named checkout, never `submodules: recursive`
**Source:** `.github/workflows/catalog-sync-check.yml:22-29` (the record), `:53-81` (the pattern).
**Apply to:** the rewritten `wiki-check.yml`.
Gitlinks pin stale SHAs (`a218b4f5`, `cb189a9b`); `.gitmodules` uses SSH URLs; and an accidental
gitlink once killed the checkout before any assertion ran.

### No comments in product source
**Source:** operator hard rule; RESEARCH §Project Constraints.
**Apply to:** every repair site in `firestarter/` and `firestarter_app/`.
A `#` or `//` reference to a `doc/` path is **deleted**, not repointed:
`proto_constants.h:11-16`, `build_db.py:543`, `diagnostic_report.py:256`, `ic_layout.py:461`,
`test_diagnostic_report.py:844`, `test_loop_eprom_v131.cpp:1755`.
**Docstrings are not comments** and are repointed, not deleted: `protection_readability.py:11`,
`py32_dfu.py:27`, `check_protection_readability_invariants.py:21`, `diff_db.py`.
**Click docstrings are user-facing `--help` text** — a comment sweep must not touch them.
Meta-repo infrastructure (`tools/**`, `.github/workflows/**`) keeps rationale comments per
`.planning/codebase/CONVENTIONS.md:79-85`.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| The relocated `test_dispatch_mirror.py` doc leg | test/checker | file-I/O | **RESEARCH Open Question 1 — the single largest unresolved design question in the phase.** There is no precedent for a firmware-dispatch gate reading its canonical leg from a public wiki clone, and none for a pytest module in the meta repo (D-07 forbids adding a harness). Whichever destination is chosen (wiki clone vs. the frozen D-02 SHA), it must preserve `_BUCKET_ROW_RE`'s 7-column and `_FAMILY_ROW_RE`'s 4-column shapes (`test_dispatch_mirror.py:72-80`) — RESEARCH Pitfall 6 — which is the strongest argument for migrating `PROTOCOLS.md` §0's two tables **byte-for-byte**. |
| `honest01`'s non-bare git source fixture | test fixture | file-I/O | `new_bare_wiki` (`selftest.sh:25-27`) is `git init --bare` and cannot serve `git show <sha>:doc/<file>`. A new `new_source_repo` helper (non-bare `git init` + a commit) has no existing analog in this driver. |

---

## Metadata

**Analog search scope:** `/workspaces/tools/`, `/workspaces/.github/workflows/`,
`/workspaces/firestarter_app/tools/`, `/workspaces/firestarter_app/tests/`,
`/workspaces/firestarter/include/`
**Files scanned:** 11 read in the cited ranges; 4 strong analogs selected
(`wiki.py`, `selftest.sh`, `catalog-sync-check.yml`, `test_py32_packaging.py`) plus 2 supporting
(`diff_db.py`, `codegen.py`)
**Pattern extraction date:** 2026-08-31
