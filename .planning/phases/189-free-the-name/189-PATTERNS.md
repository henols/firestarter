# Phase 189: Free the Name - Pattern Map

**Mapped:** 2026-09-13
**Files analyzed:** 5 (1 new, 4 modified)
**Analogs found:** 5 / 5

This phase is infrastructure, not application code. "Role" and "data flow" below are read in the
infrastructure sense (evidence script, config file, docs, test-module docstring).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| **NEW** `.planning/phases/189-free-the-name/<name>.sh` (D-06 clone demo) | evidence/verification script | batch, subprocess + file-I/O | `.planning/milestones/v1.4-phases/15-versioning-locked-step-coordination-foundation/lockstep-dryrun-fixture.sh` | exact (phase-dir, self-contained, prints values then PASS/FAIL) |
| ” (temp-dir + cleanup leg only) | — | — | `tools/catalog/sync_to_subrepos.sh` | partial (only in-repo `mktemp` + `trap ... EXIT` precedent) |
| ” (argument handling + fail-closed discovery, if the planner wants args) | — | — | `.planning/v1.34/tools/run_gates.sh` | role-match (richest arg/`SCRIPT_DIR`/exit-code precedent) |
| ” (bail-on-first-assertion style, if preferred) | — | — | `.planning/v1.7/phase-33-baseline-hex/check-migration.sh` | role-match |
| `/workspaces/.gitmodules` (milestone branch) | config | static | — (edited in place, see exact content below) | n/a |
| `/workspaces/.gitmodules` (meta `main`, via PR) | config | static | same file | n/a |
| `firestarter/README.md:47` | docs | static | — (surgical one-line edit) | n/a |
| `firestarter/tests/meta_presence.py:22` | test module docstring | static | — (surgical one-word edit) | n/a |

---

## 1. Pattern assignment — the D-06 clone-demonstration script (NEW)

### Convention survey (what the repo actually does)

There are **four** tracked shell scripts in this repo that do verification work. There is **no
Python precedent** for this kind of job outside the v1.33/v1.34 tool suites (which are `--selftest`
python tools, a heavier convention than this phase needs). **The dominant convention is bash.**

Measured facts across the four:

| Property | Convention | Exceptions |
|---|---|---|
| Shebang | `#!/usr/bin/env bash` | none — all four |
| Strict mode | `set -euo pipefail` | none — all four |
| Header | A long `#`-comment block: what it proves, `Usage:`, `Exit code:` | all four; `run_gates.sh` also documents failure *style* explicitly |
| Path resolution | `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` then derive repo roots relative to it | `check-migration.sh` hardcodes `/workspaces/...` (older, weaker — do not copy this leg) |
| Arguments | env-var override (`BETA_VERSION="${BETA_VERSION:-…}"`) or a `case` loop with a fail-closed `*)` branch | `check-migration.sh`, `sync_to_subrepos.sh` take none |
| Temp dir | `mktemp` + `trap 'rm -f …' EXIT` — **only one precedent, and it is `mktemp` (file), not `mktemp -d`.** `mktemp -d` appears nowhere in `.planning/`. | — |
| Evidence emission | `echo` of a titled header, then each resolved value on its own labelled line, *before* the verdict | all four |
| Verdict | literal `PASS` / `FAIL` / `OK` token + explicit `exit 0` / `exit 1`; usage errors `exit 2` | `run_gates.sh` = accumulate-then-report; `check-migration.sh` = bail-on-first |
| Diagnostics | failure detail to `>&2`, success to stdout | all four |

**Recommendation for the planner:** bash; `set -euo pipefail`; `SCRIPT_DIR`-relative; env-var
override for the scratch dir; `mktemp -d` + `trap` (extending `sync_to_subrepos.sh`'s `mktemp`
precedent — a directory is what a clone needs); **`git clone` appears in no existing script, so
there is no analog for the clone leg itself** — it is new ground.

**Hazard to carry into the script (memory, `git clean -Xdf` destroys GSD state):** clone into a
scratch dir *outside* the repo (`${TMPDIR}`/`mktemp -d`), never into a path under `/workspaces`
that a later `git clean` could be aimed at, and remove it by explicit path in the `trap`.

### Primary analog: `lockstep-dryrun-fixture.sh`

**Path:** `/workspaces/.planning/milestones/v1.4-phases/15-versioning-locked-step-coordination-foundation/lockstep-dryrun-fixture.sh`
Closest match because it is a *phase-directory-committed, re-runnable fixture that shells out and
prints the compared values before its verdict* — exactly D-06 plus the `<specifics>` requirement
that the script **print the resolved submodule URLs, not merely exit 0**.

**Header + usage + strict mode + path resolution (lines 1–27):**

```bash
#!/usr/bin/env bash
# lockstep-dryrun-fixture.sh
#
# Proves the VER-03 lockstep contract: invoking both sub-repos' update_version.py
# --beta --dry-run --set-version <X.Y.ZbN> produces byte-identical DRY_RUN output.
#
# Usage:
#   bash lockstep-dryrun-fixture.sh                          # uses default BETA_VERSION=1.2.3b1
#   BETA_VERSION=3.1.0b2 bash lockstep-dryrun-fixture.sh    # override
#
# Exit code: 0 on lockstep match; 1 on any mismatch or script error.
#
# This fixture is callable from Phase 19's E2E-01 smoke test as a pre-flight check.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
APP_REPO="$META_REPO_ROOT/firestarter_app"
FW_REPO="$META_REPO_ROOT/firestarter"
BETA_VERSION="${BETA_VERSION:-1.2.3b1}"
```

Note the "callable from Phase 19's smoke test" line — that is the exact precedent for D-06's
"Phase 193's GATE-03 can extend this rather than reinvent it." Put an equivalent line in the header.

**Precondition check before doing work (lines 38–44)** — copy this shape for "the milestone branch
exists" / "`git` is available" / "the gitlink commits are fetchable":

```bash
for REPO_PATH in "$APP_REPO" "$FW_REPO"; do
    if [[ ! -f "$REPO_PATH/.github/scripts/update_version.py" ]]; then
        echo "ERROR: $REPO_PATH/.github/scripts/update_version.py not found" >&2
        exit 1
    fi
done
```

**Evidence emission — the banner + labelled-value block (lines 29–36):**

```bash
echo "LOCKSTEP DRY-RUN FIXTURE"
echo "========================"
echo "Meta-repo root: $META_REPO_ROOT"
echo "App repo:       $APP_REPO"
echo "Firmware repo:  $FW_REPO"
echo "BETA_VERSION:   $BETA_VERSION"
echo ""
```

**Verdict pattern (lines 52–69)** — print the observed values, then assert, then a single token:

```bash
echo "App emits:       DRY_RUN: $APP_VERSION"
echo "Firmware emits:  DRY_RUN: $FW_VERSION"
echo ""

if [[ "$APP_VERSION" == "$FW_VERSION" ]] && [[ "$APP_VERSION" == "$BETA_VERSION" ]]; then
    echo "LOCKSTEP OK"
    exit 0
else
    echo "LOCKSTEP FAILED: app=$APP_VERSION firmware=$FW_VERSION expected=$BETA_VERSION" >&2
    echo "" >&2
    echo "--- App stdout ---" >&2
    echo "$APP_OUTPUT" >&2
    exit 1
fi
```

For this phase the two observed values are the clone's resolved submodule URLs, read read-only
from inside the scratch clone, e.g. `git -C "$CLONE/firestarter" remote get-url origin` and
`git -C "$CLONE" config --file .gitmodules submodule.firestarter.url` — both printed, then
asserted to contain `firestarter_fw` and **not** the bare slug.

### Temp-dir + cleanup analog: `tools/catalog/sync_to_subrepos.sh`

**Path:** `/workspaces/tools/catalog/sync_to_subrepos.sh`
The only in-repo `mktemp` + `trap` precedent (lines 20–26, 38–39):

```bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
...
tmp_h="$(mktemp)"
trap 'rm -f "$tmp_h" "${tmp_py:-}"' EXIT
```

Its header also documents its dependency list and idempotence — both worth mirroring, since D-06's
script must be re-runnable by a post-claim milestone:

```bash
# Idempotent: re-running with no upstream change is a no-op.
# Requirements: bash, cp, diff, python3, mktemp; ruff for the host artifact.
```

Adapt to `CLONE_DIR="$(mktemp -d)"` / `trap 'rm -rf "$CLONE_DIR"' EXIT`, and expose a
`KEEP_CLONE=1` escape hatch if the planner wants the tree inspectable after a failure (no in-repo
precedent for that — planner's discretion under CONTEXT's "temp-dir strategy" freedom).

### Argument handling + exit-code analog: `.planning/v1.34/tools/run_gates.sh`

**Path:** `/workspaces/.planning/v1.34/tools/run_gates.sh`

**Documented exit codes in the header (lines 58–62)** — copy this contract verbatim in shape:

```
# Exit codes
# ----------
#   0  all gates passed (or were skipped under --quick)
#   1  one or more gates failed
#   2  bad usage, or discovery found zero tools / the tools directory does not exist
```

**Fail-closed argument loop (lines 63–78):**

```bash
set -euo pipefail

QUICK=0
for arg in "$@"; do
    case "$arg" in
        --quick) QUICK=1 ;;
        *)
            echo "ERROR: unrecognized argument: $arg" >&2
            echo "Usage: bash $0 [--quick]" >&2
            exit 2
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

**Header note worth imitating (lines 22–31)** — it names its failure style *and* names the other
in-repo precedent it deliberately does not follow, so a reader need not infer:

```
# FAILURE STYLE
# --------------
# Accumulate-then-report: every gate runs regardless of an earlier gate's failure, a
# summary lists every failed gate by name at the end, and the script exits 1 if one or
# more failed. This differs from .planning/v1.7/phase-33-baseline-hex/check-migration.sh's
# bail-on-first-assertion style ...
```

For a three-assertion clone demo, **bail-on-first** (the `check-migration.sh` style) is the better
fit — a failed clone makes later assertions meaningless. State the choice in the header anyway.

### Bail-on-first analog: `.planning/v1.7/phase-33-baseline-hex/check-migration.sh`

**Path:** `/workspaces/.planning/v1.7/phase-33-baseline-hex/check-migration.sh`

**Numbered-assertion header + per-assertion failure block (lines 1–24, 42–48):**

```bash
if [ "${OLD_NAMES_HITS}" -ne 0 ]; then
    echo "FAIL: Assertion 1 — found ${OLD_NAMES_HITS} non-comment references to the 8 old shield-net names in firmware source."
    echo "      Expected 0 post-rename. Pre-rename this is the baseline (≥86 hits per RESEARCH.md)."
    echo "      Re-run after Wave 3 lands the call-site sweep."
    exit 1
fi
```

Each failure prints **what was expected, what the pre-state looks like, and what to do next** —
three lines, not one. Mirror that for "submodule not initialised" and "URL still carries the bare
slug".

**Anti-pattern in this file — do NOT copy:** hardcoded absolute roots (lines 27–32,
`BASELINE_DIR="/workspaces/.planning/..."`). Use `SCRIPT_DIR` derivation instead. D-04's clone
source is `file:///workspaces`, which *is* absolute by nature — derive it from `SCRIPT_DIR` too
(`$(cd "$SCRIPT_DIR/../../.." && pwd)`) so the script survives a worktree or a relocated checkout.

---

## 2. The two firmware-repo edits

Both files are git-tracked in the `firestarter` submodule (`git -C firestarter ls-files` confirms).

### `firestarter/README.md` line 47 — CHANGE

Current text, lines 41–49 (surrounding context for a surgical edit):

```markdown
firestarter fw -i              # stable
firestarter fw -i --pre        # pre-release
```

Or download `firestarter_{board}.hex` from
[Releases](https://github.com/henols/firestarter/releases) and flash it with `avrdude`.

Pre-release builds are tagged `X.Y.ZbN` or `X.Y.ZrcN` and marked "Pre-release", never "Latest",
```

The single edit: `henols/firestarter/releases` → `henols/firestarter_fw/releases` on line 47.
(CONTEXT gives the planner freedom on the link *wording* beyond the slug.)

### `firestarter/README.md` — the five lines that must NOT change

Measured with `/usr/bin/grep -n 'henols/' firestarter/README.md` (devcontainer `grep` is ugrep and
honours `.gitignore` — use `/usr/bin/grep` for gate evidence):

| Line | Slug | Verdict |
|---|---|---|
| 1 | `henols/firestarter_app` (logo raw URL) | **unchanged** — app keeps its name |
| 7 | `henols/firestarter_prom` | **unchanged** — D-1 |
| **47** | `henols/firestarter` | **CHANGE → `firestarter_fw`** |
| 75 | `henols/firestarter_prom/wiki/Contributing` | **unchanged** |
| 80 | `henols/firestarter_prom/wiki` | **unchanged** |
| 81 | `henols/firestarter_prom/wiki/Breaking-Changes` | **unchanged** |

**Concrete discriminator for the executor and for the verification grep** — the bare slug is
`henols/firestarter` followed by a **non-word character or end of string**:

```bash
/usr/bin/grep -InE 'henols/firestarter([^_a-zA-Z0-9]|$)' README.md
```

A plain `grep -n 'henols/firestarter'` matches all six lines and is **wrong**. The `[^_a-zA-Z0-9]`
class is what excludes `_app`, `_prom` and `_fw`. Post-edit this grep must return **zero** lines in
the firmware repo (D-10: verified by grep at verification time, no committed guard).

### `firestarter/tests/meta_presence.py` line 22 — CHANGE

Current docstring, lines 15–27 (the change is one token on line 22):

```python
**Direction warning, unique to this module.** The relationship here is
*parent*, not sibling: `firestarter` is a **submodule of** the meta repo, so
the meta root is `Path(__file__).resolve().parent.parent.parent` -- one
level further up than `firestarter_app/tests/fw_presence.py`'s sibling
arithmetic (that module's app repo and the firmware repo are siblings under
a common parent; this repo's meta root IS that common parent). Under
`actions/checkout` of `henols/firestarter` in isolation, that parent
directory is simply the runner's work directory and `.planning/` does not
exist there at all (RESEARCH F-14) -- an entirely ordinary absent-repo case,
not an error.
```

Line 22 is `` `actions/checkout` of `henols/firestarter` in isolation, that parent ``.
**Edit: `henols/firestarter` → `henols/firestarter_fw`. Nothing else on any other line.**

Note the backtick-quoted `` `firestarter` `` on line 16 — that is the **submodule path/directory
name**, which D-01 explicitly keeps. It must not be touched, and it does not match the bare-slug
regex anyway (no `henols/` prefix).

### HARD CONSTRAINT — no comments in product source

`/workspaces/CLAUDE.md` § "Source code comments — hard rule" applies to everything under
`firestarter/` and `firestarter_app/` and is **not overridable by a plan**:

- **Do not** add any comment, note, phase reference or `# RENAME-01`-style annotation to
  `firestarter/tests/meta_presence.py` or `firestarter/README.md`. The edits are a slug swap and
  nothing more.
- **Do not** write "add a comment citing X" into a plan, and do not make a comment's existence an
  acceptance criterion.
- The existing docstring in `meta_presence.py` already carries GSD provenance
  (`Requirements: PCB-01 …`, `Decisions covered: D-03, D-04`). CONTEXT's `<deferred>` block is
  explicit: **this phase changes the slug inside that docstring and nothing else.** Stripping the
  provenance belongs to todo `2026-08-27-strip-gsd-provenance-comments-from-source.md`.
- The four analog scripts above are **thick with comments — correctly so.** They live under
  `.planning/`, which is *not* product source. The D-06 script may and should carry a full header
  block. Only the `firestarter/` edits are comment-free.

---

## 3. `.gitmodules` and the local clone state (read-only inspection, 2026-09-13)

### `/workspaces/.gitmodules` — exact current content, verbatim (4 lines of body, tab-indented)

```
[submodule "firestarter"]
	path = firestarter
	url = git@github.com:henols/firestarter.git
[submodule "firestarter_app"]
	path = firestarter_app
	url = git@github.com:henols/firestarter_app.git
```

Indentation is a **TAB**, which is what `git submodule set-url` writes — D-03's mechanism therefore
produces no whitespace drift. The only line that changes is
`	url = git@github.com:henols/firestarter.git` → `	url = git@github.com:henols/firestarter_fw.git`.
Section name `[submodule "firestarter"]` and `path = firestarter` stay (D-01); SSH transport stays
(D-02).

### The D-03 observables — both currently carry the OLD slug

`git -C /workspaces config --local -l` (read-only):

```
submodule.firestarter.url=git@github.com:henols/firestarter.git      <-- MUST CHANGE via `sync`
submodule.firestarter.active=true
submodule.firestarter_app.url=git@github.com:henols/firestarter_app.git
submodule.firestarter_app.active=true
remote.origin.url=https://github.com/henols/firestarter_prom.git
```

`git -C /workspaces/firestarter remote -v` (read-only):

```
origin	git@github.com:henols/firestarter.git (fetch)
origin	git@github.com:henols/firestarter.git (push)      <-- MUST CHANGE via `sync --recursive`
```

`git -C /workspaces/firestarter_app remote -v` — already `git@github.com:henols/firestarter_app.git`,
unaffected.

Three observables, three assertions for the verification leg (CONTEXT D-03: "**Both of those are
the observable** … verify them, not just the file"):

| # | Command (read-only) | Expected after |
|---|---|---|
| 1 | `git -C /workspaces config --file .gitmodules submodule.firestarter.url` | `git@github.com:henols/firestarter_fw.git` |
| 2 | `git -C /workspaces config --local submodule.firestarter.url` | `git@github.com:henols/firestarter_fw.git` |
| 3 | `git -C /workspaces/firestarter remote get-url origin` | `git@github.com:henols/firestarter_fw.git` |

**Nothing was modified during this mapping pass.** No `set-url`, no `sync`, no `clone`, no network
or GitHub call was run. The meta repo's own `remote.origin.url` is HTTPS while the submodules are
SSH — a pre-existing asymmetry, out of scope, do not "fix" it.

---

## Shared Patterns

### Evidence-script skeleton (applies to the one new file)
**Sources:** `lockstep-dryrun-fixture.sh` (shape), `sync_to_subrepos.sh` (temp/trap),
`run_gates.sh` (args/exit codes), `check-migration.sh` (assertion messages).

```bash
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```
Header documents: what it proves, `Usage:`, `Exit code:`, dependency list, failure style,
re-runnability. Values printed before verdict. `FAIL:`/`OK` token + explicit exit. Detail to stderr.

### Bare-slug discriminator (applies to every verification grep in this phase)
**Source:** CONTEXT measured facts, confirmed against `firestarter/README.md`.

```bash
/usr/bin/grep -InE 'henols/firestarter([^_a-zA-Z0-9]|$)' <paths>
```
Use `/usr/bin/grep`, not bare `grep` — the devcontainer's `grep` is ugrep and honours
`.gitignore`, silently under-scanning. For a tracked-file-only sweep prefer
`git grep -InE 'henols/firestarter([^_a-zA-Z0-9]|$)'`, which is what CONTEXT's measurement used.

### No comments in product source (applies to both `firestarter/` edits)
**Source:** `/workspaces/CLAUDE.md` § "Source code comments — hard rule". Not overridable. Rationale
goes in the phase `SUMMARY.md` or the commit message, never in the file.

## No Analog Found

| File / leg | Role | Reason |
|---|---|---|
| The `git clone --recurse-submodules` leg of the D-06 script | evidence script | **No tracked script in any of the three repos runs `git clone`** (`grep -rl 'git clone' .planning` → zero hits). The surrounding skeleton has strong analogs; the clone invocation itself is new ground — take it verbatim from CONTEXT D-04. |
| `mktemp -d` | temp-dir strategy | `mktemp -d` appears nowhere under `.planning/` or `tools/`. Only `mktemp` (file) in `sync_to_subrepos.sh`. Extend that precedent. |
| The meta-`main` PR leg (D-07) | process, not a file pattern | No script precedent; the procedure is prose in `.planning/notes/v135-close-procedure-under-protection.md`. |

## Metadata

**Analog search scope:** `/workspaces/.planning/**` (all milestones + archives), `/workspaces/tools/`,
`/workspaces/firestarter/{README.md,tests/}`
**Scripts found and ranked:** 4 tracked bash verification scripts; 4 read in full or in the
relevant ranges. Tracked-source gate applied — all four verified via `git ls-files`; no gitignored
mirror paths are cited.
**Pattern extraction date:** 2026-09-13
