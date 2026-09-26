# Phase 191: The Branch That Reaches Users - Pattern Map

**Mapped:** 2026-09-13
**Files analyzed:** 6 (1 script created, 2 todos created, 3 source files modified)
**Analogs found:** 6 / 6

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.planning/phases/191-the-branch-that-reaches-users/191-stable-install-fixture.sh` (new) | test fixture (bash) | request-response over live HTTP + subprocess | `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/endpoint-contract-fixture.sh` | exact (shape); **API surface diverges — see below** |
| same, secondary | test fixture (bash) | scratch-dir lifecycle | `.planning/phases/189-free-the-name/fresh-clone-fixture.sh` | role-match (temp-tree + exit-code discipline) |
| `.planning/todos/pending/2026-09-13-release-yml-autocommit-vs-ruleset.md` (new) | backlog record | document | `.planning/todos/pending/2026-08-30-sync-to-subrepos-self-diff-asserts-nothing.md` | exact |
| `.planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md` (new) | backlog record | document | same | exact |
| `firestarter_app/firestarter/constants.py` @ `origin/main` (mod) | config constant | n/a | 189-04 `.gitmodules` one-line prepared-branch change | exact (procedure) |
| `firestarter_app/README.md` @ `origin/main` (mod) | docs | n/a | same | exact (procedure) |
| `firestarter_app/firestarter/__init__.py` @ `origin/main` (mod) | version marker | n/a | same | exact (procedure) |

---

## Pattern Assignments

### 1. `191-stable-install-fixture.sh` (test fixture, live HTTP + clean venv)

**Analog:** `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/endpoint-contract-fixture.sh`
(475 lines — read in full). Secondary: `189-free-the-name/fresh-clone-fixture.sh` (its scratch-dir and
exit-code-3 conventions).

#### 1a. Header block — copy the shape verbatim, change the content

190's header (lines 1–72) is the template: script name, what it proves, **why the naive reading proves
nothing**, the enumerated checks, `Usage:`, `Environment:`, `Dependencies:`, `Failure style:`,
`Exit codes:`, `Re-runnable:`. `--help` reprints it by slicing its own source:

```bash
for arg in "$@"; do
    case "$arg" in
        --help)
            sed -n '2,64p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "ERROR: unrecognized argument: $arg" >&2
            echo "Usage: bash $0 [--help]" >&2
            exit 2
            ;;
    esac
done
```
(190 lines 78–90. Note the `sed -n 'A,Bp'` range is hand-tuned to the header length — the new script
must retune it, and a planner should make "`--help` exits 0 and prints the usage" a verify leg so a
mis-tuned range is caught.)

Strict mode is one line, immediately after the header: `set -euo pipefail` (190:73, 189:56).

#### 1b. Exit-code discipline — inherit all four codes

190 lines 55–63:

```
#   0  ENDPOINT CONTRACT OK -- ...
#   1  a check or an assertion failed for any other reason
#   2  bad usage (unrecognized argument)
#   3  the one named, expected non-failure case -- api.github.com is not
#      reachable from this container. This is a network fact, not a URL
#      regression; re-run when connectivity returns.
```

The `3` case is produced by a transport-only probe **before any work** (190:130–136):

```bash
PROBE_CODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 \
    https://api.github.com/repos/henols/firestarter_fw/releases/latest 2>/dev/null || echo "000")"
if [ "$PROBE_CODE" = "000" ]; then
    echo "NETWORK UNAVAILABLE: could not reach api.github.com (transport-level failure)." >&2
    echo "This reports the network, not a URL regression. Re-run when connectivity returns." >&2
    exit 3
fi
```
For 191 this probe is doubly load-bearing: a `pip install` also needs the network, so probing
`pypi.org` as well (same shape, second `PROBE_CODE`) distinguishes "no network" from "package missing".

#### 1c. The per-check idiom — heredoc child, log file, verdict token

Every one of 190's five checks is the same four-part block (190:179–220 is the canonical instance):

```bash
echo "--- Check 1: stable channel ---"
if ! "$PYTHON_BIN" -P <<'PYEOF' >"$CHECK1_LOG" 2>&1
... python ...
print("CHECK1 OK")
PYEOF
then
    echo "FAIL: Check 1 (stable channel) -- python child failed." >&2
    echo "      Expected: <expectation named in words>" >&2
    echo "      Output:" >&2
    cat "$CHECK1_LOG" >&2
    exit 1
fi
cat "$CHECK1_LOG"
/usr/bin/grep -qFe "CHECK1 OK" "$CHECK1_LOG" || {
    echo "FAIL: Check 1 completed without printing its verdict token." >&2
    exit 1
}
```

Three details a planner must preserve, each of which was a real bug elsewhere in this project:
- `/usr/bin/grep`, never bare `grep` — the devcontainer's `grep` is ugrep and honors `.gitignore`.
- `-qFe` with the `e`, not `-qF` — a dash-leading pattern makes `-qF` exit 2 and the gate fails open.
- The verdict token check is **separate** from the child's exit status: a child that dies mid-print
  can still exit 0 under some interpreters.

`"$PYTHON_BIN" -P` (PYTHONSAFEPATH) is used on every child, for the reason 190 records at lines
162–171: without it Python prepends the caller's cwd, and `/workspaces`'s sibling `firestarter/`
**firmware** submodule forms a namespace package that shadows the host package. **This applies
unchanged in 191** — the venv interpreter is still invoked from a cwd that may be `/workspaces`.

#### 1d. Scratch bookkeeping and cleanup

```bash
CHECK1_LOG="$(mktemp)"
...
cleanup() {
    rm -f "$CHECK1_LOG" "$CHECK2_LOG" ...
}
trap cleanup EXIT
```
(190:144–153.) 189's fixture adds the convention 191's venv needs: the scratch parent is
`mktemp -d`, **resolved outside `/workspaces` so a later `git clean -Xdf` cannot take it**, with a
`KEEP_*=1` escape hatch (189 header lines 19–30). D-08's venv should be created inside exactly such a
`mktemp -d` and removed in the same `trap cleanup EXIT`.

The downloaded `.hex` is removed **by explicit path, never by directory** (190:310–320):

```bash
HEX_PATH="$(/usr/bin/grep '^hex_path: ' "$CHECK3_LOG" | sed 's/^hex_path: //')"
if [ "$KEEP_DOWNLOAD" != "1" ]; then
    if [ -n "$HEX_PATH" ] && [ -f "$HEX_PATH" ]; then
        rm -f -- "$HEX_PATH"
        echo "removed_download: $HEX_PATH"
    fi
fi
```
The comment above it names why: the directory it sits in also holds the app's own `config.json` and
`reports/`. On `origin/main` that directory is `HOME_PATH`, defined in **`firmware.py`, not
`constants.py`**:

```python
HOME_PATH = os.path.join(os.path.expanduser("~"), ".firestarter")
```
(`origin/main:firestarter/firmware.py:33`.) `constants.py` on `main` has no `HOME_PATH` at all.

#### 1e. The `redirects == 0` assertion — the one thing that must survive intact

190:194–204, the substance of D-07:

```python
for label, url in (
    ("FIRESTARTER_RELEASE_URL", FIRESTARTER_RELEASE_URL),
    ("FIRESTARTER_RELEASES_URL", FIRESTARTER_RELEASES_URL),
):
    r = requests.get(url, timeout=10)
    print(f"requested: {url}")
    print(f"resolved: {r.url}")
    print(f"status: {r.status_code}")
    print(f"redirects: {len(r.history)}")
    assert len(r.history) == 0, f"{label} followed {len(r.history)} redirect(s) -> {r.url}"
    assert r.url == url, f"{label} resolved to a different URL than requested: {r.url}"
```
In 191 the loop has **exactly one** entry — `FIRESTARTER_RELEASE_URL` — because that is the only
release constant on `main` (D-01). Keep both assertions: `len(r.history) == 0` and `r.url == url`.

**Positive control (189-04 precedent, and required here):** a zero-redirect reading is only meaningful
next to a reading that *does* redirect. The fixture should also `requests.get` the bare-slug URL
`https://api.github.com/repos/henols/firestarter/releases/latest` and assert `len(r.history) == 1`,
proving the probe can see a redirect when one exists. Without it, `redirects: 0` is indistinguishable
from a broken measurement.

#### 1f. CRITICAL DIVERGENCE — 190's fixture cannot be re-run against the stable

190's fixture imports, on every check, surface that **does not exist in `origin/main`'s argparse-based
2.0.x code**:

| 190 fixture uses | exists on `origin/main`? |
|---|---|
| `FirmwareManager.fetch_release_info(channel=…, board=…)` | **no** |
| `FIRESTARTER_RELEASES_URL` | **no** |
| `click` / `click.testing.CliRunner` | **no** (argparse) |
| `firestarter.cli_handlers.cli` | **no** (module absent) |
| `fw --list`, `fw --stable`, `fw --pre`, `--json` | **no** |
| `FirmwareManager(config_manager=None)` | signature is `__init__(self, config_manager: ConfigManager)` — positional works, but there is no `channel` anywhere |

The new fixture must drive `main`'s **own** API. These are the real signatures on
`origin/main:firestarter/firmware.py` — quoted so the planner does not invent them:

```python
# firestarter/firmware.py:52
    def __init__(self, config_manager: ConfigManager):

# firestarter/firmware.py:98
    def fetch_latest_release_info(
        self, board: str = "uno"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetches the latest firmware version and download URL for the specified board.
        Returns: (latest_version_str, download_url_str) or (None, None) on failure.
        """
```

```python
# firestarter/firmware.py:107 -- the ONLY consumer of the constant
            response = requests.get(FIRESTARTER_RELEASE_URL, timeout=10)
            response.raise_for_status()
            release_data = response.json()
            latest_version = release_data.get("tag_name")
            firmware_asset_name = f"firestarter_{board}.hex"
            download_url = None
            for asset in release_data.get("assets", []):
                if asset.get("name") == firmware_asset_name:
                    download_url = asset.get("browser_download_url")
                    break
```

```python
# firestarter/firmware.py:148
    def _download_firmware_file(self, url: str) -> Optional[str]:
        """Downloads firmware from the URL and saves it to a temporary local path."""
```
It returns a path under `HOME_PATH` (see 1d) or `None` on failure — it does **not** raise.

Note also `firestarter/firmware.py:19`: `from firestarter.constants import *`. So the constant is
re-exported as `firestarter.firmware.FIRESTARTER_RELEASE_URL` and is importable from either module —
but it is bound **by value at module scope**, so rebinding `firestarter.constants.FIRESTARTER_RELEASE_URL`
at runtime has no effect on `firmware.py` (190-RESEARCH Pitfall 7). 191 needs no rebinding (there is no
"unreachable" check in D-07's chain), but a planner must not reintroduce one naively.

The bench leg's entry point, for D-09's transcript (not fixture content):

```python
# firestarter/firmware.py:291
    def manage_firmware_update(
        self,
        install_flag: bool = False,
        avrdude_path_override: Optional[str] = None,
        avrdude_config_override: Optional[str] = None,
        port_override: Optional[str] = None,
        board_override: Optional[str] = "uno",
        flags: int = 0,
        ) -> bool:
```
and the version-comparison defect D-09 predicts (`firmware.py:132–146`):

```python
    def _compare_versions(
        self, current_version_str: str | None, latest_version_str: str | None
    ) -> bool:
        ...
        try:
            current = tuple(map(int, current_version_str.split(".")))
            latest = tuple(map(int, latest_version_str.split(".")))
            return current >= latest
        except ValueError:
            logger.warning(
                f"Could not parse version strings for comparison: '{current_version_str}', '{latest_version_str}'"
            )
            return False
```
`int("0b22")` raises `ValueError` → warning → `False` → downgrade offered. Exactly as D-09 measured.

#### 1g. Provenance-first printing (D-08's shadowing trap)

190 prints its environment before any check (190:155–160):

```bash
echo "ENDPOINT CONTRACT FIXTURE (URL-01 / URL-03 / URL-04)"
echo "====================================================="
echo "python_bin: $PYTHON_BIN"
echo "app_root: $APP_ROOT"
echo "nope_slug: $NOPE_SLUG"
echo ""
```
191 must go further and print, **as check 0, before anything else**, out of the freshly created venv:
`firestarter.__file__`, `firestarter.__version__`, and the `FIRESTARTER_RELEASE_URL` value read out of
the **installed** package. That is what makes the transcript prove which artefact was exercised.

**Do NOT copy 190's `PYTHON_BIN` default** (190:100):
```bash
PYTHON_BIN="${PYTHON_BIN:-$APP_ROOT/.venv311/bin/python}"
```
D-08 explicitly retires the 3.11 pin. 191 creates its own venv with `python3 -m venv` on the
devcontainer default interpreter, inside its `mktemp -d`, and sets `PYTHON_BIN` to that venv's
`bin/python`. 190's preconditions block (190:107–122) is still the right shape — check the interpreter
is executable, check the imports resolve — but the import probe drops `click`:
`"$PYTHON_BIN" -P -c "import firestarter, requests"`.

Likewise 190's derived roots (190:96–98) are still correct and should be copied literally, since the
phase directory sits at the same depth:
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
APP_ROOT="$META_ROOT/firestarter_app"
```
…but 191 does **not** need `APP_ROOT` for the install (the point is that no local path is used).
190's closing porcelain assertion (190:464–470) is still worth keeping as an "I touched nothing"
guard:
```bash
APP_STATUS="$(git -C "$APP_ROOT" status --porcelain)"
if [ -n "$APP_STATUS" ]; then
    echo "FAIL: firestarter_app working tree is dirty after the checks ran." >&2
    echo "$APP_STATUS" >&2
    exit 1
fi
echo "app_repo_porcelain: clean"
```

---

### 2. The two backlog items (`.planning/todos/pending/*.md`)

**Analog:** `.planning/todos/pending/2026-08-30-sync-to-subrepos-self-diff-asserts-nothing.md`
(short, recent, defect-shaped — the right template; the `write-sdp-relock-deferred.md` style is a
multi-page deferral record and is *not* the shape to copy).

**Filename convention:** `YYYY-MM-DD-kebab-summary.md`, in `pending/`. Both recent items follow it
(`2026-09-13-close-six-stale-claims-wr01-wr06.md`, `2026-09-08-reclaim-local-scratch-artifacts.md`).
`resolves_phase: unassigned` is used for freshly filed defects; `none` is reserved for deliberately
unassignable ones.

**Frontmatter, verbatim template:**

```markdown
---
created: 2026-08-30T11:20:00Z
title: sync_to_subrepos.sh runs `diff -q $X $X` twice — two verifications that assert nothing
area: tooling
found_in_phase: 167
files:
  - tools/catalog/sync_to_subrepos.sh (lines 84-86 and 97-99 — the two self-comparisons)
  - tools/catalog/sync_to_subrepos.sh (lines 65-70 — the one CORRECT two-distinct-operand assertion, for reference)
---

## Problem
```

The `files:` list carries a `path (line range — what it is)` string per entry, and the newer
`2026-09-13-…` item shows the same with a trailing `(WR-01)`-style tag. Note the second entry in the
example: **the correct instance is cited alongside the defect as a reference**. Both 191 items should
do the same — cite `origin/main:.github/workflows/release.yml` (or `publish.yml`) as the defect **and**
`origin/beta:.github/workflows/beta-release.yml`'s `pypi` job as the proven pattern, which D-05
requires each item to name.

The `2026-09-13-…` item adds a `source:` key pointing at the artefact that raised it; 191's items
should use `source: .planning/phases/191-the-branch-that-reaches-users/191-CONTEXT.md (D-04 / D-05)`.

Body shape: `## Problem` → what is measured → why it matters → the known-good fix → disposition.

---

### 3–5. The three `origin/main` source edits (config constant, docs, version)

**Analog:** `.planning/phases/189-free-the-name/189-04-PLAN.md` Task 1 + `189-04-SUMMARY.md`. This is the
**binding procedural precedent** and matters more than any code excerpt.

#### The exact current lines on `origin/main` — quote these for exact-match edits

`firestarter/constants.py`, lines 8–10 (the constant is **wrapped in parentheses across three lines**,
not a single line — an exact-match edit must account for that):

```python
FIRESTARTER_RELEASE_URL = (
    "https://api.github.com/repos/henols/firestarter/releases/latest"
)
```

`README.md:17`:

```markdown
The Firestarter Firmware can be found here [Firestarter](https://github.com/henols/firestarter).
```
(D-03 allows rewording beyond the slug; the minimal change is `henols/firestarter` →
`henols/firestarter_fw`. Note `README.md:11` also contains
`raw.githubusercontent.com/henols/firestarter_app/...` — that is the **app** repo, correctly named, and
is the positive control proving a boundary-aware sweep is not returning an empty file.)

`firestarter/__init__.py` — the whole file is one line:

```python
__version__ = "2.0.8"
```
→ `2.0.9`.

**CLAUDE.md hard rule applies:** no comments added to any of these three files. Rationale goes in
`SUMMARY.md` or the commit message.

#### The procedure — 189-04 Task 1, quoted

> Fetch `main` from `origin` — a fetch, never a push — then create a scratch worktree outside
> `/workspaces` with `git worktree add`, branching `v1.38-gitmodules-main` from `origin/main`. Do not
> check out `main` in the primary working tree. … Commit in the worktree with plain `git commit`, then
> remove the worktree with `git worktree remove`. The branch survives the worktree's removal, which is
> the point: the commit is prepared locally and waits for the operator. Do not push it, do not open a
> pull request, and do not merge anything. That is Task 2, and it is the operator's.

Its rationale, also from the plan: the primary tree stays on the milestone branch; the worktree is kept
**outside `/workspaces`** so `git clean -Xdf` cannot take it; submodules are left uninitialised in the
worktree deliberately.

For 191 the same shape applies, one level down: the worktree is of the **`firestarter_app` submodule's**
repository (`git -C /workspaces/firestarter_app fetch origin main`, then
`git -C /workspaces/firestarter_app worktree add <outside-/workspaces> -b <branch> origin/main`), and
the prepared branch carries **one commit touching three files** (D-03).

#### 189-04's verify legs — reuse the counting idiom

From `189-04-PLAN.md` lines 137–151 (adapt paths; note every one uses `/usr/bin/grep`):

```bash
git -C <repo> rev-parse --verify <branch>
git -C <repo> diff --numstat origin/main <branch>
git -C <repo> show <branch>:<file> | awk '/<new-line-regex>/ {n++} END {print n+0}'
git -C <repo> show <branch>:<file> | /usr/bin/grep -lE 'henols/firestarter([^_a-zA-Z0-9]|$)' | wc -l
git -C <repo> show <branch>:<file> | /usr/bin/grep -lE 'henols/firestarter_app' | wc -l   # positive control
git -C /workspaces branch --show-current      # must still be the milestone branch
git -C <repo> worktree list | wc -l           # must be back to 1
```
The boundary-aware pattern `henols/firestarter([^_a-zA-Z0-9]|$)` is the exact regex D-03's sweep uses,
and it exists because `henols/firestarter` is a substring of `henols/firestarter_fw`.

#### Post-merge verification — live API, never the local clone

From `189-04-SUMMARY.md` (`tech-stack.patterns`, verbatim):

> "The merged state of a protected branch is verified by reading the file back from the GitHub contents
> API at the target ref, never from the local clone, since a local branch proves only what was prepared,
> not what landed."

The concrete commands 189-04 used:

```bash
gh api "repos/henols/firestarter_prom/contents/.gitmodules?ref=main" -H "Accept: application/vnd.github.raw"
gh api repos/henols/firestarter_prom/pulls/79   # asserted merged: true, read merge_commit_sha
```
…asserted against **three** greps: new-URL count 1, bare-slug count 0, and a `firestarter_app`
positive control count 1 — the control being what proves the zero is a real absence rather than an
empty response.

For 191 the equivalents are:
```bash
gh api "repos/henols/firestarter_app/contents/firestarter/constants.py?ref=main" -H "Accept: application/vnd.github.raw"
gh api "repos/henols/firestarter_app/contents/README.md?ref=main"                 -H "Accept: application/vnd.github.raw"
gh api "repos/henols/firestarter_app/contents/firestarter/__init__.py?ref=main"   -H "Accept: application/vnd.github.raw"
gh api repos/henols/firestarter_app/pulls/<n>
gh run list -R henols/firestarter_app --workflow release.yml --limit 5   # D-06's live branch decision
```
Plus PyPI read back independently (`https://pypi.org/pypi/firestarter/json` → `info.version`), which
D-06 requires after Gate 2. Note `gh run view --log` needs `XDG_CACHE_HOME` set in this container;
`gh run list` and `gh api` are unaffected.

Also from 189-04, and binding here: the agent **never pushes, opens a PR, or merges**; the operator's
report is never the verification source; the prepared branch is left un-deleted after the merge.

---

## Shared Patterns

### Evidence and transcript capture
**Source:** `189-04-SUMMARY.md` key-files + `.planning/phases/189-free-the-name/evidence/`
**Apply to:** the fixture transcript and D-09's bench transcript
Evidence files live under `<phase-dir>/evidence/` with names of the form
`<phase>-<req>-<slug>.md|.txt` (e.g. `189-rename-02-branch-disposition.md`,
`189-rename-02-observables.txt`). The fixture script itself lives at the **phase-directory root**, not
under `evidence/` — that is where both `fresh-clone-fixture.sh` and `endpoint-contract-fixture.sh` sit.

### Positive control accompanies every zero
**Source:** `189-04-SUMMARY.md` coverage D1
**Apply to:** the `redirects == 0` assertion, the boundary-aware slug sweep, and the post-merge read-back
A count of zero is only evidence if a sibling count that should be non-zero is taken in the same run.

### `/usr/bin/grep` and `-qFe`
**Apply to:** every grep in the fixture and in every plan `<automated>` verify leg
Bare `grep` is ugrep here and honors `.gitignore`; `-qF` with a dash-leading pattern exits 2 and the
gate fails open.

### `.planning/config.json` prune guard
**Source:** `191-CONTEXT.md` § "One housekeeping hazard"
**Apply to:** every plan that calls a `gsd-tools` state-writing verb
`git status -- .planning/config.json` after each such call; restore `planning.sub_repos`
(`firestarter`, `firestarter_app`, `firestarter_app_py32`, `firestarter_py32_ci`) rather than
committing the prune. Expect `STATE.md`'s `progress.completed_phases` / `progress.percent` to need the
same hand repair (precedent: commit `b019c706`).

### No comments in product source
**Source:** `CLAUDE.md` § "Source code comments — hard rule"
**Apply to:** `constants.py`, `__init__.py` on `main`. Not overridable by a plan. The fixture script and
the todos are `.planning/` artefacts, not product source, and their header comments are required.

---

## No Analog Found

None. Every file in this phase has a close in-repo precedent.

The one **near-miss worth stating explicitly**: `endpoint-contract-fixture.sh` is an exact *structural*
analog and a **non**-analog at the API level. Phase 190's D-16 asserted 191 would re-run it; D-07
corrects that. A planner that copies 190's python bodies unchanged will produce a fixture that
`ImportError`s on the very first check.

---

## Metadata

**Analog search scope:** `.planning/phases/189-free-the-name/`,
`.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/`, `.planning/todos/pending/`,
`firestarter_app` at `origin/main` (via `git show`, never a checkout)
**Files scanned:** 12 read; 36 todo filenames enumerated
**Pattern extraction date:** 2026-09-13
