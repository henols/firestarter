# Phase 186: The Python Floor, Before the EOL - Research

**Researched:** 2026-09-11
**Domain:** Python packaging metadata, type-checker/linter target configuration, fail-closed CI gates (host-only; `firestarter_app/`)
**Confidence:** HIGH — every number below was measured in this session, in the py3.11 CI-replica venv, with the producing command shown.

## Summary

CONTEXT.md settled the design (D-01…D-12). This document supplies the measured numbers and the
mechanical detail the planner would otherwise guess, and it reports **five places where a
CONTEXT.md or D-11 claim is wrong**, all of which change plan scope.

The headline measurement is benign: **the mypy error count does not move.** At the current
`python_version = "3.10"` the count is 35 in 181 checked files; at `3.11` the output is
**byte-identical** — same 35 errors, same 15 files, same 181 checked. The watermark is already 35.
So D-05 resolves to *neither* branch: nothing to lower, nothing to fix. `MIN_CHECKED_SOURCE_FILES
= 120` is satisfied with margin (181).

The two things that *do* move are ordering and one broken gate:

1. **The D-09 ruff sweep is itself a 3.11-only change and must land after (or with) the mypy
   `python_version` bump, never before it.** The 2 UP017 fixes rewrite `datetime.timezone.utc` to
   `datetime.UTC`, which is 3.11+ only. Measured: with the sweep applied but `python_version` still
   `"3.10"`, the watermark gate reports **37 errors and FAILS (exit 1)**. CI runs on every push to
   every branch (`ci.yml:19` — `branches: ['**']`), so a sweep-first commit is a red build, not a
   transient.
2. **The sweep breaks one existing test, loudly.** `tests/test_cap03_ack_layout_parity.py:198-202`
   pins `_decode_id_frame`'s signature text as a regex containing the literal
   `Optional\[LogMessage\]`. The sweep rewrites that signature to `LogMessage | None`, the regex
   matches 0, and `test_planted_literal_index_is_detected` goes red. Reverting
   `firestarter/serial_comm.py` alone makes it pass again — attribution confirmed by bisect.

### Corrections to CONTEXT.md — read these before planning

CONTEXT.md itself says "re-verify before relying on the numbers". Five things did not survive
re-verification. None re-opens a decision; each changes plan scope.

| # | CONTEXT.md / D-11 says | Measured reality | Where |
|---|---|---|---|
| C-1 | D-11: `firestarter/cli_handlers.py:1814`'s `# noqa: UP006 (python3.9 compat)` "is resolved by the D-09 sweep, not preserved." | **False.** It survives the sweep verbatim, same line, same text. UP006 is already active at `py39`; raising the target changes nothing about it. The plan needs an explicit task. | §2 |
| C-2 | D-11 names `firestarter/main.py:33` (the guard string). | Incomplete. `main.py:31` — `if sys.version_info < (3, 9):  # noqa: UP036` — is the **executable** half of the same guard and must move with it. Its `# noqa: UP036` is load-bearing and must be kept. | §4 |
| C-3 | D-11 names two `STACK.md` files. | Two further meta-repo surfaces co-state the floor: `/workspaces/.planning/codebase/STRUCTURE.md:363` and `CONVENTIONS.md:173`. | §4 |
| C-4 | D-09 treats the sweep as lint churn, orderable freely relative to the config change. | The sweep emits **3.11-only code** (`datetime.UTC`). Sweep-before-config makes the watermark gate fail 37 > 35. Order is constrained. And the fix pass alone leaves 4 files failing `ruff format --check`, which CI runs separately. | §1, §2 |
| C-5 | D-12: "pip already refuses on 3.9/3.10". | The quoted error string is real and verbatim-correct, but it only fires on a **pinned/exact** request. An unpinned `pip install firestarter` on 3.10 silently resolves to the last release advertising `>=3.9` and exits 0. | P-3 |

**Primary recommendation:** plan three commits in this order — (1) the four floor statements plus
the classifier list plus the deleted prose and the `main.py` guard; (2) the ruff sweep (autofix +
`ruff format` + the 3 hand fixes + the `test_cap03_ack_layout_parity.py` regex repair); (3) the
four-way agreement gate. Build the gate as a `tests/test_*.py` using stdlib `tomllib` — the repo
already has that exact precedent in `tests/test_runtime_dependencies.py`, added by Phase 181, whose
own docstring says tomllib is used *"deliberately"* because adding `toml`/`tomli` would add a
dependency in the act of asserting none was added.

---

## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `186-CONTEXT.md` `<decisions>`. These are not re-opened by this research; where
a measurement contradicts one, the contradiction is flagged in-line below, not resolved here.

- **D-01:** **The floor is raised to 3.11.** `requires-python = ">=3.11"`, `[tool.ruff] target-version =
  "py311"`, `[tool.mypy] python_version = "3.11"` — all three move together. This resolves FLOOR-01 in the
  raise direction and closes the question Phase 131 D-13 explicitly deferred to the operator ("dropping it
  is a published-metadata breaking change on a live PyPI package, an operator decision, not this phase's to
  make"). — **Reversibility:** one-way.

- **D-02:** **3.11 was chosen against three alternatives, each rejected on a measured ground** (3.10 — EOL
  on the day it lands; hold 3.9 — `mypy.defaults.PYTHON3_VERSION_MIN` is `(3, 10)`; 3.12 — CI runs 3.11).

- **D-03:** **The classifier list becomes 3.11 and 3.12 only.** 3.9 and 3.10 removed; 3.13 **not** added.

- **D-04:** **A fail-closed check asserts all four floor statements name the same version** —
  `requires-python`, `[tool.ruff] target-version`, `[tool.mypy] python_version`, and the `python-version`
  pinned in `firestarter_app/.github/workflows/ci.yml`.

- **D-05:** **Watermark policy: ratchet down, fix a rise.** If the count drops below `# mypy_error_watermark
  = 35`, lower it. If it rises, **fix the new errors; do not raise the watermark.**

- **D-06:** **999.27's instruction to re-verify `_FOUND_RE` / `_CLEAN_RE` does not apply here.**

- **D-07:** **Rationale lives in `.planning/notes/python-floor-decision.md`** (meta repo), plus a corrected
  3.11 claim and a one-line pointer in `firestarter_app/.planning/codebase/STACK.md`.

- **D-08:** **The note carries decision + evidence + a standing rule + a successor backlog item** carrying
  **2027-10-31** (3.11 EOL). Standing rule: *the floor tracks the version CI runs; when mypy's minimum
  supported target rises above it, move all four statements together.*

- **D-09:** **The full ruff autofix is absorbed, as its own commit, separate from the config change.** The 3
  non-auto-fixable findings must be named and handled individually, not swept. — **Reversibility:** costly.

- **D-10:** **Falsified prose comments are deleted, never rewritten.** `# mypy_error_watermark = 35` is NOT
  a comment for this purpose — `check_mypy_watermark.py:96` parses it as configuration.

- **D-11:** **Mechanical surfaces decided here so no plan asks** — the `main.py` guard string, the
  `cli_handlers.py:1814` noqa, both `STACK.md` files, the two mypy-fixture sites left unchanged, and the
  gate reading every `python-version:` in the app's workflows.

- **D-12:** **`requires-python` is the user-facing notice; the release wording is recorded for ship, not
  written now.** A one-line release-note fragment goes in the phase SUMMARY.

### Claude's Discretion

- Plan decomposition and commit boundaries, subject to D-09's separate-commit constraint.
- The agreement gate's implementation shape (a `tests/` test vs a `tools/check_*.py` invoked from CI) and
  how it reads `ci.yml` — a regex or a minimal parse; `pyyaml` is **not** a dependency this project carries
  and must not become one for this.
- The note's internal structure and prose.
- Exact wording of the `main.py` guard string beyond the version number.

### Deferred Ideas (OUT OF SCOPE)

- **Broadening ruff's `select` beyond `["E","F","I","UP"]`** — its own phase, not this one.
- **Every `# noqa: BLE001` in `firestarter_app` is inert** — adjacent to D-09's sweep and deliberately
  untouched by it.
- **Adding a `CHANGELOG.md`** — rejected in D-12 as a new capability.
- **A 3.13 CI leg / claiming 3.13 support** — rejected in D-03 for lack of any test.

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **FLOOR-01** | The advertised Python floor and the type-checker agree. Either mypy enforces the advertised `>=3.9` floor, or the floor is raised deliberately and `requires-python`, `target-version` and `python_version` all move together. | §4 gives the verified current text and line number of all four statements; §1 proves mypy accepts `3.11` with zero config-rejection diagnostic and no count change; §2 gives the full lint consequence of moving `target-version`. |
| **FLOOR-02** | The choice is made and applied **before 2026-10-31**; the milestone does not close with the pair still divergent. | §3 gives the no-pyyaml gate shapes and the exact four values the gate must normalise; §6 gives the commands that prove agreement. |
| **FLOOR-03** | The reasoning is recorded where the next person finds it, not only in a commit message. | §4 confirms the two `STACK.md` edit sites and finds two additional meta-repo surfaces D-11 missed; the `.planning/notes/` precedent shape is measured below. |

---

## Project Constraints (from CLAUDE.md)

| Directive | Effect on this phase |
|---|---|
| **No comments in product source, ever; a plan cannot override it.** Covers everything under `firestarter/` and `firestarter_app/`. Deleting comments is permitted; writing them is not. | D-10's deletions are compliant. **Any new gate file must carry zero explanatory comments** — note that every existing `tools/check_*.py` and `tests/test_*.py` in this repo is heavily commented, so the planner must NOT copy their commenting style. Module/function **docstrings are not comments** for this rule, and are how the existing gates would be documented under it. |
| Click docstrings are user-facing `--help` text, not commentary. | Not touched by this phase. |
| `main` is protected in all three repos; this project's close targets `beta`. | No push/PR work in this phase. |
| Constants/flag bits duplicated between Python and C++ must change together. | Not applicable — this phase touches no protocol constant. |
| Serial protocol changes must be kept in sync. | Not applicable — host-only, no protocol change. |

`.claude/skills/` holds four skills (`devtest-rootcause`, `devtest-triage`, `find-skills`,
`skill-creator`). None is topical to this phase; no `rules/*.md` directory exists.
`.planning/config.json` sets `workflow.nyquist_validation: false`, so **no Validation Architecture
section is included** in this document.

---

## Architectural Responsibility Map

Single-tier phase — everything lives in the host CLI repo's build/CI configuration. Recorded so the
planner can sanity-check that no task drifts into the firmware or the wheel's runtime code.

| Capability | Primary owner | Secondary | Rationale |
|---|---|---|---|
| Advertised install floor (`requires-python`, classifiers) | `firestarter_app/pyproject.toml` `[project]` | PyPI published metadata | setuptools reads it; pip enforces it at resolve time |
| Lint target | `firestarter_app/pyproject.toml` `[tool.ruff]` | `ci.yml:80-84` | ruff's `target-version` is the only thing that decides which UP rules fire |
| Type-check target | `firestarter_app/pyproject.toml` `[tool.mypy]` | `tools/check_mypy_watermark.py` (`ci.yml:87`) | mypy clamps to its own minimum; the gate is what makes the value observable |
| Proven runtime | `.github/workflows/{ci,beta-release}.yml` `python-version` | GitHub runner | the only one of the four that is *executed* rather than declared |
| Runtime refusal for an under-floor interpreter | `firestarter_app/firestarter/main.py:30-35` | — | user-facing behaviour inside the wheel, not metadata |
| Agreement between the four | **new** (D-04) | — | nothing owns it today; that is the defect |
| Rationale durability | `.planning/notes/python-floor-decision.md` (meta) + `firestarter_app/.planning/codebase/STACK.md` | — | D-07: the meta note is invisible to the app-repo editor, hence the pointer |

**Not in any tier for this phase:** the firmware repo (`/workspaces/firestarter/`), which pins
`python-version: '3.11'` in two of its own workflows and is untouched.

## Measurement environment

Everything below was measured with the already-built CI-replica venv. It was **reused, not
rebuilt** — see the `--refresh` hazard in Pitfalls.

```bash
cd /workspaces/firestarter_app
.venv/ci-replica/bin/python -V          # Python 3.11.16
.venv/ci-replica/bin/python -c "import importlib.util;print(importlib.util.find_spec('numpy'))"   # None
.venv/ci-replica/bin/python -m mypy --version   # mypy 2.3.1 (compiled: yes)
.venv/ci-replica/bin/ruff --version             # ruff 0.16.4
.venv/ci-replica/bin/python -c "import firestarter;print(firestarter.__file__)"
# /workspaces/firestarter_app/firestarter/__init__.py   <- editable install resolves to the real tree
```

`[VERIFIED: measured 2026-09-11 in /workspaces/firestarter_app/.venv/ci-replica]`

Re-verified CONTEXT.md's load-bearing D-02 fact:

```bash
.venv/ci-replica/bin/python -c "import mypy.defaults as d; print(d.PYTHON3_VERSION_MIN)"
# (3, 10)
```

`[VERIFIED: mypy 2.3.1 runtime introspection]` — `PYTHON3_VERSION_MIN == (3, 10)`, exactly as
CONTEXT.md states. Holding 3.9 remains unreachable under `mypy>=2.1.0,<3`.

**Destructive-edit disclosure.** Every experiment that required editing tracked files was run in a
throwaway git worktree at `/tmp/.../scratchpad/wt186`, created with `git worktree add --detach`.
**No file in `/workspaces/firestarter_app` or `/workspaces` was modified at any point.** Verified:

```bash
cd /workspaces/firestarter_app && git status --porcelain
# ?? datasheets/MBM27C1001.pdf
# ?? datasheets/MX27C4000.pdf     <- both pre-existed this session

cd /workspaces && git status --porcelain --ignore-submodules=untracked
#  M .planning/VALIDATED-EPROMS.md
#  M .planning/config.json
# ?? anything.txt
# ?? tmp/                          <- all four pre-existed this session
cd /workspaces && git ls-tree HEAD firestarter_app
# 160000 commit bffbba8e6179a181f9ac381d11a2d86d6204ec37   firestarter_app   <- unchanged gitlink
```

---

## 1. The mypy count at the new floor (D-05)

### The measurement

```bash
cd /workspaces/firestarter_app
# current config (python_version = "3.10"):
.venv/ci-replica/bin/python -m mypy firestarter/ tests/ | tail -1
# Found 35 errors in 15 files (checked 181 source files)

# at the new floor, without editing pyproject.toml:
.venv/ci-replica/bin/python -m mypy --python-version 3.11 firestarter/ tests/ | tail -1
# Found 35 errors in 15 files (checked 181 source files)
```

The two runs are **byte-identical**, not merely equal in count:

```bash
diff mypy310.txt mypy311.txt && echo IDENTICAL
# IDENTICAL
```

| Quantity | Value | Provenance |
|---|---|---|
| mypy errors at current `python_version = "3.10"` | **35** in 15 files, 181 checked | `[VERIFIED: measured 2026-09-11]` |
| mypy errors at `python_version = "3.11"` | **35** in 15 files, 181 checked (identical output) | `[VERIFIED: measured 2026-09-11]` |
| Current `# mypy_error_watermark` | **35** | `[VERIFIED: firestarter_app/pyproject.toml:174]` — verbatim: `# mypy_error_watermark = 35   # Updated Phase 71-07: floor after 71-06 added test_validate_family_cmd.py (6 AppContext mock-type errors). Prior: 29 (Phase 69-03).` |
| `MIN_CHECKED_SOURCE_FILES` | **120**, satisfied at 181 | `[VERIFIED: firestarter_app/tools/check_mypy_watermark.py:48]` — verbatim: `MIN_CHECKED_SOURCE_FILES = 120` |

**D-05 verdict: the count neither falls nor rises. The watermark stays at 35, unchanged.** Neither
branch of D-05 fires. The plan needs no watermark edit and no error-fixing task — and it should say
so explicitly rather than leaving a reader to wonder whether the measurement was skipped.

Error-code distribution at 3.11, for the record:

```bash
grep -oE '\[[a-z-]+\]$' mypy311.txt | sort | uniq -c | sort -rn
#  31 [annotation-unchecked]   <- notes, not counted errors
#  10 [union-attr]
#  10 [arg-type]
#   6 [assignment]
#   5 [attr-defined]
#   3 [func-returns-value]
#   1 [return-value]
```

### The authoritative gate-path measurement

`check_mypy_watermark.py:106-115` hard-codes `mypy_argv()` as
`[sys.executable, "-m", "mypy", "firestarter/", "tests/"]` with **no `--python-version` flag**, so
the gate's number comes from the config file. Measured on the worktree with all four floor
statements set to 3.11 and the full ruff sweep applied:

```bash
cd <worktree>
.venv/ci-replica/bin/python tools/check_mypy_watermark.py
# checked 181 source files
# mypy errors: 35 (watermark: 35)
# OK: error count at watermark.
# exit 0
```

`[VERIFIED: measured 2026-09-11, gate script's own code path]`

Two things this proves beyond the count. First, the completeness clause is satisfied: `checked 181`
≥ `MIN_CHECKED_SOURCE_FILES = 120`, which is what `_INFO_TEMPLATE` names as the evidence that
licenses lowering (`check_mypy_watermark.py:81-88`). Second, **mypy emits no config-rejection
diagnostic for `python_version = "3.11"`** — `classify_mypy_result` exits 2 on any line matching
`^.*: \[mypy[^\]]*\]: .*$` (`:73-76`, `:161-171`), and the run reached the watermark comparison, so
no such line was printed.

### The ordering constraint this measurement exposed

Running the same gate with the sweep applied but `python_version` still `"3.10"`:

```bash
cd <worktree-with-sweep-only>
.venv/ci-replica/bin/python tools/check_mypy_watermark.py
# checked 181 source files
# mypy errors: 37 (watermark: 35)
# FAIL: 37 errors exceeds watermark 35. New errors introduced.
# exit 1
```

The two extra errors, isolated by diff:

```
firestarter/diagnostic_report.py:735: error: Module has no attribute "UTC"  [attr-defined]
firestarter/cli_handlers.py:1888:    error: Module has no attribute "UTC"  [attr-defined]
```

(post-sweep line numbers). Cause: ruff's 2 **UP017** fixes rewrite `datetime.timezone.utc` to
`datetime.UTC`, and `datetime.UTC` is a Python 3.11 addition. `[VERIFIED: measured 2026-09-11]`

**Consequence for the plan:** the ruff sweep commit is not floor-neutral. It emits 3.11-only code.
It must land **after** `python_version = "3.11"`, or in the same commit. Landing it first produces a
red push. `ci.yml:16-19` triggers on `push: branches: ['**']`, and `ci.yml:1-13`'s own header says
"CI runs on EVERY branch", so every intermediate commit on the milestone branch is gated.

The reverse ordering is also not free but is harmless: with `target-version = "py311"` set and the
sweep not yet applied, `ruff check firestarter/ tests/` reports 182 errors (exit 1) while the
watermark gate passes at 35. **Whichever order is chosen, one intermediate commit is red.** That is
inherent to D-09's separate-commit requirement and should be stated in the plan rather than
discovered in CI. If the planner wants zero red commits it must fold D-09's sweep into the config
commit, which D-09 forbids — so the honest choice is config-first, sweep-second, with the red
intermediate acknowledged.

---

## 2. The three non-auto-fixable ruff findings (D-09)

### Re-measured split — CONTEXT.md's figures are correct

```bash
cd /workspaces/firestarter_app
.venv/ci-replica/bin/ruff check firestarter/ tests/                       # target py39 from config
# All checks passed!   (exit 0)

.venv/ci-replica/bin/ruff check --target-version py311 firestarter/ tests/ --statistics
# 177  UP045  [-] non-pep604-annotation-optional
#   2  UP017  [*] datetime-timezone-utc
#   2  UP035  [*] deprecated-import
#   1  I001   [*] unsorted-imports
# Found 182 errors.
# [*] 179 fixable with the `--fix` option (3 hidden fixes can be enabled with the `--unsafe-fixes` option).
```

**No drift from CONTEXT.md: 182 / 177 UP045 / 2 UP017 / 2 UP035 / 1 I001 / 179 fixable / 3 hidden.**
`[VERIFIED: measured 2026-09-11, ruff 0.16.4]`

One figure CONTEXT.md does not have: the **actual fix pass is 190 fixes, not 179**, because ruff
iterates and the first pass unmasks more:

```bash
ruff check --target-version py311 --fix firestarter/ tests/ | tail -2
# Found 193 errors (190 fixed, 3 remaining).
# No fixes available (3 hidden fixes can be enabled with the `--unsafe-fixes` option).
```

### The 3, named individually

All three are **UP045**, all in **`firestarter_app/firestarter/eprom_info.py`**, all in the
signature of `prepare_detailed_eprom_data`. Pristine-tree locations:

```bash
.venv/ci-replica/bin/ruff check --target-version py311 --output-format=concise firestarter/eprom_info.py
# firestarter/eprom_info.py:97:24:  UP045 Use `X | None` for type annotations
# firestarter/eprom_info.py:100:36: UP045 Use `X | None` for type annotations
# firestarter/eprom_info.py:103:26: UP045 Use `X | None` for type annotations
#   (the file's other 6 UP045 findings all carry [*] and are auto-fixed)
```

The exact source construct, `firestarter/eprom_info.py:94-109` verbatim:

```python
    def prepare_detailed_eprom_data(
        self,
        eprom_name: str,  # For logging and titles
        eprom_details: Optional[
            Dict  # noqa: UP006
        ],  # Pre-fetched from db.get_eprom(name)  # noqa: UP006
        eprom_data_for_programmer: Optional[
            Dict  # noqa: UP006
        ],  # Pre-fetched from db.get_eprom(name)
        raw_config_data: Optional[
            Dict  # noqa: UP006
        ],  # Pre-fetched from db.get_eprom_config()  # noqa: UP006
        manufacturer: Optional[str],  # Pre-fetched from db.get_eprom_config()
        include_export_config: bool = False,
        include_adapter: bool = False,
    ) -> Optional[Dict]:  # noqa: UP006
```

| # | Rule | File:line:col | Construct | Why ruff will not auto-fix it |
|---|---|---|---|---|
| 1 | UP045 | `firestarter/eprom_info.py:97:24` | `eprom_details: Optional[\n Dict # noqa: UP006\n ],` | The `Optional[...]` subscript spans lines and **encloses a comment**. Collapsing it to `X \| None` would delete that comment, so ruff classifies the fix unsafe. |
| 2 | UP045 | `firestarter/eprom_info.py:100:36` | `eprom_data_for_programmer: Optional[\n Dict # noqa: UP006\n ],` | Same. |
| 3 | UP045 | `firestarter/eprom_info.py:103:26` | `raw_config_data: Optional[\n Dict # noqa: UP006\n ],` | Same. |

`[VERIFIED: firestarter_app/firestarter/eprom_info.py:94-109, read this session; ruff 0.16.4 output]`

### What the correct hand fix is — measured, not proposed

**`--unsafe-fixes` is the wrong instrument here.** Measured, it resolves all three but produces an
unreadable and format-unstable result:

```bash
ruff check --target-version py311 --fix --unsafe-fixes firestarter/eprom_info.py
# Found 5 errors (5 fixed, 0 remaining).
ruff format --check firestarter/eprom_info.py
# unformatted: File would be reformatted     <- ruff format then splits `Dict | None` across two
#                                               lines to make room for the trailing comments
```

It also produces an inconsistent result: one of the three parameters lost its `# noqa: UP006` (and
became `dict | None`) while the other two kept theirs (`Dict | None  # noqa: UP006`).

**The hand fix that works** — collapse all three to `dict | None` and drop the now-orphaned inner
comments (deletion, which the hard rule permits):

```python
        eprom_details: dict | None,
        eprom_data_for_programmer: dict | None,
        raw_config_data: dict | None,
```

Measured outcome of that hand fix plus the autofix:

```bash
ruff check --target-version py311 --output-format=concise firestarter/ tests/
# firestarter/eprom_info.py:13:26: F401 [*] `typing.Optional` imported but unused
ruff check --target-version py311 --fix firestarter/ tests/ | tail -1
# Found 1 error (1 fixed, 0 remaining).
ruff format --check firestarter/ tests/ | tail -1
# 179 files already formatted
.venv/ci-replica/bin/python -m mypy --python-version 3.11 firestarter/ tests/ | tail -1
# Found 35 errors in 15 files (checked 181 source files)
```

`[VERIFIED: measured 2026-09-11 in a throwaway worktree]` — note the second-order **F401** on the
now-unused `typing.Optional` import at `firestarter/eprom_info.py:13`; it is auto-fixable, but only
a second `--fix` pass catches it.

### `ruff format --check` after `ruff check --fix` — NOT clean

This is a fact CONTEXT.md does not carry and CI enforces (`ci.yml:83-84`).

```bash
ruff check --target-version py311 --fix firestarter/ tests/     # 190 fixed
ruff format --check firestarter/ tests/
# 4 files would be reformatted, 175 files already formatted
```

The four: `firestarter/address_parser.py`, `firestarter/cli_handlers.py`,
`firestarter/diagnostic_report.py`, `firestarter/hardware.py`. All four are the same shape —
shortening `Optional[X]` to `X | None` (or `datetime.timezone.utc` to `datetime.UTC`) makes a
previously-wrapped line fit on one, and the formatter wants to unwrap it. Running `ruff format`
resolves all four and does **not** reintroduce any lint finding:

```bash
ruff format firestarter/ tests/        # 4 files reformatted, 175 files left unchanged
ruff check --target-version py311 firestarter/ tests/ | tail -1   # Found 3 errors.  (the 3 unsafe UP045)
ruff format --check firestarter/ tests/ | tail -1                 # 179 files already formatted
```

`[VERIFIED: measured 2026-09-11]` — **the sweep commit must run `ruff format` after `ruff check
--fix`, not just the fix.**

### Blast radius of the sweep

```bash
git diff --stat     # after --fix + format, in the worktree
# 15 files changed, 175 insertions(+), 183 deletions(-)
```

The 15: `firestarter/{address_parser,cli_handlers,codec,config,diagnostic_report,eprom_info,
eprom_operations,firmware,hardware,ic_layout,jp5_gate,main,serial_comm}.py` plus
`tests/test_dev_gate_reads_no_firmware_source.py` and `tests/test_runtime_dependencies.py`.

- **`firestarter/messages.py` and `firestarter/frame_vectors.py` are NOT touched.** Confirmed
  independently: `ruff check --target-version py311 firestarter/messages.py
  firestarter/frame_vectors.py` → `All checks passed!`. The codegen drift gates (`ci.yml:58-64`,
  `:69-75`) and `beta-release.yml:60-73`'s `ruff format` + `ruff check --add-noqa` normalisation
  therefore cannot drift from this change. `[VERIFIED: measured 2026-09-11]`
- **The sweep does NOT touch `firestarter_app/tools/`**, because CI's ruff scope is
  `firestarter/ tests/` only (`ci.yml:81`, `ci.yml:84`). Independent proof that `tools/` is outside
  every gate: it is dirty at both targets — `ruff check --target-version py39 tools/` → `Found 8
  errors`; `--target-version py311 tools/` → `Found 6 errors` (3 E402, 2 I001, 1 UP031).
  `[VERIFIED: measured 2026-09-11]`

### Two findings adjacent to D-09 the planner should decide about

1. **`# noqa: UP006 (python3.9 compat)` at `firestarter/cli_handlers.py:1814` SURVIVES the sweep,
   verbatim, at the same line number.** D-11 says it "is resolved by the D-09 sweep, not
   preserved." **That is false.** UP006 (`typing.Dict` → `dict`) is gated at py39 and is already
   active under the current `target-version = "py39"`; raising the target to py311 changes nothing
   about it. Measured: 62 `# noqa: UP006` lines in `firestarter/*.py` before the sweep, 57 after
   (the 5 that vanish were on inner-bracket lines the UP045 fix collapsed away, all in
   `eprom_info.py`), and `cli_handlers.py:1814` is not among them:

   ```bash
   awk 'NR==1814' <worktree>/firestarter/cli_handlers.py
   # def _load_validation_spec() -> Dict[str, Any]:  # noqa: UP006 (python3.9 compat)
   ```

   `[VERIFIED: measured 2026-09-11 pre- and post-sweep]` The planner must handle this explicitly.
   Two options, both compliant with the hard rule (neither writes a new comment):
   - delete the falsified parenthetical, leaving `# noqa: UP006`; or
   - resolve the finding at the site — `-> dict[str, Any]:` — and delete the whole noqa.

2. **`firestarter/py32_dfu.py` keeps 14 `Optional[...]` annotations, all explicitly
   UP045-suppressed** (`# noqa: UP045` or `# noqa: UP006,UP045`, at `:282, 366, 407, 430, 431, 567,
   576, 579, 580, 820, 923, 953, 962, 994`). They pre-date this phase and the autofix does not reach
   them, so they are not D-09's to sweep — but they mean `target-version = "py311"` has its UP045
   consequence switched off in one whole file, which is the shape D-09 rejected in the abstract.
   Worth a line in the SUMMARY or a backlog note; not obviously worth a task. `[VERIFIED: measured
   2026-09-11]`

### The sweep breaks one existing test — plan for it

```bash
cd <worktree with full change>
pytest tests/test_cap03_ack_layout_parity.py::test_planted_literal_index_is_detected -q
# FAILED  ... AssertionError: assert '13' in 'expected at least 1 definition of
#   `_decode_id_frame` in .../firestarter/serial_comm.py, found 0 -- the CAP-03 decode facts
#   can only be extracted if there is a body to extract them from.'
```

Bisected to the source change, then to one file:

| Tree state | Result |
|---|---|
| full change | `1 failed` (deterministic, 2 runs, caches cleared) |
| pristine | `1 passed` (deterministic, 2 runs) |
| `pyproject.toml` reverted, source swept | `1 failed` |
| source reverted, `pyproject.toml` changed (all four edits, and each of the four alone) | `1 passed` |
| `firestarter/serial_comm.py` reverted, everything else swept | `1 passed` |

`[VERIFIED: measured 2026-09-11, bisect]`

Root cause, `tests/test_cap03_ack_layout_parity.py:198-202` verbatim:

```python
_DECODE_ID_FRAME_DEF_RE = re.compile(
    r"^([ \t]*)def _decode_id_frame\(\s*self\s*,\s*frame_len:\s*int\s*,\s*"
    r"body:\s*bytes\s*\)\s*->\s*Optional\[LogMessage\]\s*:\s*$",
    re.MULTILINE,
)
```

The sweep rewrites both definitions in `firestarter/serial_comm.py` (`:335` and `:1112`):

```
-    def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]:
+    def _decode_id_frame(self, frame_len: int, body: bytes) -> LogMessage | None:
```

so the regex matches 0 and `_extract_decode_id_frame_body` (`:274-298`) raises its non-vacuity
assertion. Reproduced in-process:

```python
print(len(m._DECODE_ID_FRAME_DEF_RE.findall(txt)))   # 0
```

**Fix belongs in the sweep commit:** update the `Optional\[LogMessage\]` alternative at
`tests/test_cap03_ack_layout_parity.py:200` to match `LogMessage \| None` (or to accept either).
The gate fails **loud**, not open, which is the good outcome.

**It takes down six test legs, not one.** The full suite run below, with both sibling repos present
so nothing is skipped for layout reasons, gives:

```
FAILED tests/test_cap03_ack_layout_parity.py::test_firmware_and_host_agree_on_indices_zero_through_three
FAILED tests/test_cap03_ack_layout_parity.py::test_budget_is_written_and_read_at_the_computed_offset
FAILED tests/test_cap03_ack_layout_parity.py::test_both_sides_use_big_endian_for_both_u16_fields
FAILED tests/test_cap03_ack_layout_parity.py::test_host_uses_no_bare_integer_index_above_three_to_reach_the_budget
FAILED tests/test_cap03_ack_layout_parity.py::test_scan_targets_are_non_vacuous
FAILED tests/test_cap03_ack_layout_parity.py::test_planted_literal_index_is_detected
6 failed, 2349 passed, 4 skipped, 1 warning in 468.19s
```

All six share the single root cause above, and **all six are in that one file** — no other module
fails. Five of the six are `requires_fw`-gated and so would show as skips in GitHub CI (no sibling
firmware repo there); `test_planted_literal_index_is_detected` is **not** gated and goes red in CI
regardless. One regex edit fixes all six. `[VERIFIED: measured 2026-09-11, full suite, 3.11 replica
venv, both siblings present]`

This is also the **only** test of its kind. A scan of every source-text pattern in `tests/` and
`tools/` that pins a `typing` construct found exactly one:

```bash
/usr/bin/grep -rn "Optional\\\\\[\|Optional\[\|-> Optional\|Tuple\\\\\[\|Dict\\\\\[" tests/*.py tools/*.py \
  | grep -viE "^\S+: *(from|import)"
# tests/test_cap03_ack_layout_parity.py:200:    r"body:\s*bytes\s*\)\s*->\s*Optional\[LogMessage\]\s*:\s*$",
```

`[VERIFIED: measured 2026-09-11 with /usr/bin/grep, not the ambient ugrep]`

---

## 3. A no-pyyaml shape for the four-way agreement gate (D-04 + D-11)

### Every `python-version:` in the app's workflows — complete inventory

```bash
cd /workspaces/firestarter_app
/usr/bin/grep -rn "python-version" .github/workflows/
# .github/workflows/beta-release.yml:52:          python-version: '3.11'
# .github/workflows/ci.yml:53:          python-version: '3.11'
# .github/workflows/ci.yml:112:          python-version: '3.11'
```

**Exactly three, all `'3.11'`, at exactly the lines CONTEXT.md names.** The discussion missed
nothing. `[VERIFIED: firestarter_app/.github/workflows/, /usr/bin/grep, 2026-09-11]`

The other two workflow files carry no Python pin at all:
`publish.yml` has no `setup-python` step (its only Python reference is
`publish.yml:56: - run: python3 -m pip install --upgrade build && python3 -m build`, on the runner
default), and `release.yml` has no Python reference whatsoever. A gate that globs
`.github/workflows/*.yml` and asserts on every `python-version:` it finds therefore finds 3 and must
not require that every file contain one.

The meta repo has **no `.github/workflows/` directory at all** (`/workspaces/.github/` contains only
`CONTRIBUTING.md` and `ISSUE_TEMPLATE/`), so the gate's scope is entirely inside the app repo.
For completeness, the *firmware* repo pins `python-version: '3.11'` twice
(`/workspaces/firestarter/.github/workflows/build.yml:109`, `beta-build.yml:88`) — out of this
phase's scope and not reachable from a fresh app-repo clone; the gate must not try to read it.

### The `ci-py32` question — settled

`ci.yml:104-128` is the `ci-py32` job. Its setup step:

```yaml
109	      - name: Set up Python 3.11
110	        uses: actions/setup-python@v5
111	        with:
112	          python-version: '3.11'
```

**`ci-py32` runs the SAME interpreter as `ci`.** It is isolated in what it *installs*
(`.[test,py32]` vs `.[test]`, per `ci.yml:98-103`), not in what Python it runs. A gate asserting all
three pins equal the floor is therefore correct today, and there is no legitimate-divergence
exception to carve out. `[VERIFIED: firestarter_app/.github/workflows/ci.yml:104-128, read this
session]`

### The four spellings, and the normalisation the gate needs

| Statement | Current text | Location | Post-change text | Normalised |
|---|---|---|---|---|
| `requires-python` | `requires-python = ">=3.9"` | `pyproject.toml:12` | `">=3.11"` | strip a leading `>=` → `3.11` |
| ruff `target-version` | `target-version = "py39"` | `pyproject.toml:110` | `"py311"` | `py` + major + minor, no dot: `py311` → `3.11` |
| mypy `python_version` | `python_version = "3.10"` | `pyproject.toml:155` | `"3.11"` | already `3.11` |
| CI pin (×3) | `python-version: '3.11'` | `ci.yml:53`, `ci.yml:112`, `beta-release.yml:52` | unchanged | strip single quotes → `3.11` |

`[VERIFIED: all four read from source this session; texts quoted verbatim above]`

Two normalisation notes the planner should not have to rediscover:

- **ruff's token set is a closed enum**, confirmed from the tool: `ruff check --target-version` with
  no value prints `[possible values: py37, py38, py39, py310, py311, py312, py313, py314, py315]`.
  `py3` + minor-with-no-separator. Parsing `py311` requires splitting after the first digit
  (`py` → drop, `3` → major, `11` → minor), **not** a fixed 2-character minor: `py39` is 3.9 and
  `py311` is 3.11. `[VERIFIED: ruff 0.16.4 --help output]`
- **`requires-python` is a specifier, not a version.** `">=3.11"` normalises to `3.11` only under
  the assumption that the project states a bare lower bound. A gate should assert the *shape*
  (`^>=\d+\.\d+$`) and fail closed on anything else, rather than silently stripping whatever
  non-digits precede the number — otherwise `">=3.11,<4"` or `"~=3.11"` would pass a naive strip.

### `tomllib` — available, and already used in this repo

```bash
.venv/ci-replica/bin/python -c "import tomllib,sys; print('OK on',sys.version.split()[0]); \
  d=tomllib.load(open('pyproject.toml','rb')); \
  print(d['project']['requires-python'], d['tool']['ruff']['target-version'], d['tool']['mypy']['python_version'])"
# OK on 3.11.16
# >=3.9 py39 3.10
```

`[VERIFIED: measured 2026-09-11]` — `tomllib` is 3.11+ stdlib, present in the CI interpreter, and
reads all three pyproject values with no dependency. The devcontainer's 3.12 has it too, so the gate
runs locally as well as in CI. **Nothing about the gate needs `tomli` or `pyyaml`.**

There is a repo precedent that settles this decisively — `tests/test_runtime_dependencies.py:1-18`,
verbatim:

```python
"""HYG-02, asserted by test rather than by a sentence: the runtime
`dependencies` list in `pyproject.toml` is pinned to exactly six shipped
distributions, by exact set equality.

This module uses stdlib `tomllib` (available on Python 3.11+, matching the
app CI floor) deliberately: reaching for `toml` or `tomli` to parse
`pyproject.toml` would add a dependency in the very act of asserting that
no dependency was added, which is HYG-02's own claim.

`181-PATTERNS.md` (Phase 181's pattern map) found no precedent in this tree
for a test that parses `pyproject.toml` -- the shape here is an original
decision, not a copied one.
"""
```

`[VERIFIED: firestarter_app/tests/test_runtime_dependencies.py:1-18, read this session]`

This file already does, for `project.dependencies`, exactly what D-04's gate must do for the four
floor values: `tomllib` parse, path resolved from `Path(__file__).resolve().parent.parent` (with an
explicit `check_permitted_claims.py`-inspired justification at `:29-35`), and a non-vacuity guard
(`assert path.is_file()`, `assert dependencies`) before any comparison.

**Note the contradiction this creates with D-10's other deletion target.**
`tests/test_py32_packaging.py:43-49` argues the opposite in prose — *"Why a regex scan, not a TOML
parse. tomllib is py3.11+ and this project's declared floor is py3.9 …"*. Both idioms exist in
`tests/` today; the tomllib one is newer (Phase 181) and matches CI. After this phase the regex
rationale is falsified twice over (the floor becomes 3.11, and the mypy figure in that sentence was
already wrong). See §5.

### The YAML half, without pyyaml

The three pins are textually uniform — `          python-version: '3.11'` — and the repo's
established idiom for reading a non-Python file by regex is
`tests/test_revision_constants_parity.py` (a `#define` extractor over a C header) and
`tests/test_py32_packaging.py:84-86` (a regex over a `pyproject.toml` block). A line regex such as
`^\s*python-version:\s*['"]?([0-9]+\.[0-9]+)['"]?\s*$` over
`sorted(Path(".github/workflows").glob("*.yml"))` is idiomatic here and adds nothing.

**The non-vacuity clause is the load-bearing part.** This repo has a recorded case of a checker that
resolved to the wrong directory, scanned nothing and exited 0 (`check_permitted_claims.py`, cited in
`test_runtime_dependencies.py:31-34`), and `tests/scan_paths.py`'s own
`test_inventory_is_non_vacuous` exists for the same reason. The gate must assert it found **at
least 3** `python-version:` pins (a floor, raised deliberately when a fourth workflow is added,
never lowered) and that the workflows directory exists, before asserting agreement.

### Placement: the two shapes, and what each costs

There are three precedents in this repo, not two:

| Shape | Real example | Runs under | Lint/type coverage | Cost |
|---|---|---|---|---|
| **A. `tests/test_*.py` only** | `tests/test_runtime_dependencies.py` (Phase 181, HYG-02); `tests/test_py32_packaging.py`; `tests/test_revision_constants_parity.py` | `pytest` step, `ci.yml:89-90` | **Full** — inside `ruff check`, `ruff format --check` and the mypy watermark scope (`firestarter/ tests/`) | The gate's own code is subject to the D-09 sweep and to the watermark. If it ever throws a mypy error, that error counts against the 35. |
| **B. `tools/check_*.py` + a `tests/test_check_*.py` driver (subprocess)** | 12 of the 13 `tools/check_*.py` files — e.g. `tools/check_no_exists_proxy.py` driven by `tests/test_check_no_exists_proxy.py` via `subprocess`, never an import (its `:11-13` explains why) | `pytest` step | **None for the tool** — `tools/` is in no CI scope; the driver test is covered | Two files instead of one; the checker itself is unlinted, unformatted and untyped. |
| **C. `tools/check_*.py` + an explicit CI step** | exactly one: `tools/check_mypy_watermark.py`, run at `ci.yml:87` (`run: python tools/check_mypy_watermark.py`) — and it *also* has a `tests/test_check_mypy_watermark.py` driver | its own CI step **and** `pytest` | None for the tool | A workflow edit (which the new gate would then have to keep in agreement with itself), plus the same unlinted-tool cost. |

`[VERIFIED: firestarter_app/tools/ listing + /usr/bin/grep over .github/workflows/ + tests/, 2026-09-11]`

Concrete tradeoff, stated without choosing:

- **A** is the smallest change and the only shape that puts the new gate inside every quality gate
  this milestone is about. Its one real cost is self-reference: a test living in `tests/` is swept
  by D-09 and counted by the watermark, so the gate must be written 3.11-clean from the start. It
  also cannot run before `pip install -e .[test]` in CI (it runs at `ci.yml:89-90`, after the
  install at `:77-78`) — irrelevant here, since the gate needs no installed package.
- **B** matches the numerical majority of this repo's gates and keeps the checker importable by a
  future tool, at the cost of writing the logic in a directory with **no mypy, no `ruff check` and
  no `ruff format`** — measured above as 6 live ruff findings sitting in `tools/` right now,
  unnoticed.
- **C** is the only shape that produces a *named* CI step ("four-way floor agreement") in the
  Actions UI, which has diagnostic value; it is also the only shape that requires editing `ci.yml`,
  the very file the gate reads — a small but real circularity the planner should weigh.

One placement detail that applies to all three: the app's wheel ships `packages = ["firestarter"]`
(`pyproject.toml:94`), so neither `tests/` nor `tools/` is distributed. A gate reading
`.github/workflows/` can never be executed from an installed package and needs no guard for that.

---

## 4. The exact edit sites, verified live

Every line number CONTEXT.md cites was re-read this session. `/usr/bin/grep` was used throughout,
never the ambient ugrep.

### Verified — CONTEXT.md is correct

| Cited | Verified | Exact current text |
|---|---|---|
| `pyproject.toml:12` | ✅ `:12` | `requires-python = ">=3.9"` |
| `pyproject.toml:37` | ✅ `:37` | `    "Programming Language :: Python :: 3.9",` (and `:38` `    "Programming Language :: Python :: 3.10",` — the second classifier D-03 removes, which CONTEXT.md names in prose but not by line) |
| `pyproject.toml:63-66`, falsifying sentence `:65` | ⚠ block is actually **`:61-67`**; falsifying sentence at **`:65`** ✅ | `:65` — `# time, Requires-Python >=3.9.0, satisfiable on this project's py39 floor.` The full comment block runs `:61-67`, starting `# USB DFU firmware install for the PY32F071 board target. Optional because it is`. |
| `pyproject.toml:110` | ✅ `:110` | `target-version = "py39"` |
| `pyproject.toml:127` | ✅ `:127` | `# UP: pyupgrade (modernise syntax within py39 bounds — UP007/UP045 no-ops on py39)` |
| `pyproject.toml:139-154` | ✅ `:139-154` | 16-line `[tool.mypy]` comment block, opening `# Phase 131 D-13/GATE-05: 3.10 is mypy's true` and closing `# (backlog 999.27).` |
| `pyproject.toml:155` | ✅ `:155` | `python_version = "3.10"` |
| `tests/test_py32_packaging.py:44-45` | ✅ `:44-45` | `project's declared floor is py3.9 (ruff target-version = "py39", mypy` / `python_version = "3.9"); tomli is not a dependency this project carries and` — **already false today** (mypy is `"3.10"`), exactly as D-10 says. Part of the module docstring block `:43-49`. |
| `tests/test_py32_packaging.py:79` | ✅ `:79` | `# >=3.9.0, satisfiable on this project's py39 floor); <2 refuses a future` (comment block `:78-81`) |
| `firestarter/main.py:33` | ✅ `:33` | `            "Error: Firestarter requires Python 3.9 or higher. "` (the sentence continues at `:34`: `            "Please update your Python version."`) |
| `firestarter/cli_handlers.py:1814` | ✅ `:1814` | `def _load_validation_spec() -> Dict[str, Any]:  # noqa: UP006 (python3.9 compat)` |
| meta `.planning/codebase/STACK.md` `~:193, :203, :256` | ✅ exactly `:193`, `:203`, `:256` | `:193` `- Python 3.9+ - Host application (CLI tool, \`firestarter_app/\`)` · `:203` `- Python 3.9+ (tested through 3.12; system Python 3.13 present in dev)` · `:256` `- Python 3.9+ with pip` |
| app `.planning/codebase/STACK.md` `~:7, :12, :57` | ✅ exactly `:7`, `:12`, `:57` | `:7` ``- Python 3.9+ - All application logic (enforced via `requires-python = ">=3.9"` in `pyproject.toml`)`` · `:12` `- Python 3.13.5 (current dev machine runtime; min supported is 3.9)` · `:57` `- Python 3.9+` |
| `tools/check_mypy_watermark.py:68` | ✅ `:68` | `# "pyproject.toml: [mypy]: python_version: 3.9 is not supported (must be` — part of the `:67-72` comment documenting `_CONFIG_REJECTION_RE`. This is a quoted example of **mypy's own output**, illustrating the regex at `:73-76`. **D-11 is right: leave it.** |
| `tests/test_check_mypy_watermark.py:106` | ✅ `:106` | `    "pyproject.toml: [mypy]: python_version: 3.9 is not supported "` — line 2 of the `CONFIG_REJECTION_OUTPUT` fixture constant at `:105-109`, whose header (`:100-104`) states its purpose: *"A well-formed, COMPLETE completion clause … carrying mypy's own config-diagnostic prefix."* A synthetic fixture of a real mypy message, not a claim about this project's floor. **D-11 is right: leave it.** |

### `# mypy_error_watermark = 35` is configuration, not a comment — confirmed

`firestarter_app/pyproject.toml:174` verbatim:

```
# mypy_error_watermark = 35   # Updated Phase 71-07: floor after 71-06 added test_validate_family_cmd.py (6 AppContext mock-type errors). Prior: 29 (Phase 69-03).
```

`firestarter_app/tools/check_mypy_watermark.py:91-103` reads it as configuration; `:96` verbatim:

```python
    m = re.search(r"^\s*#\s*mypy_error_watermark\s*=\s*(\d+)", text, flags=re.MULTILINE)
```

and `:97-102` `sys.exit(2)` if absent. **D-10 is right: the line stays.** Its value stays at 35
(§1). Note the *trailing* half of that same line (`# Updated Phase 71-07: …`) is ordinary comment
prose with no floor claim in it, so D-10 does not reach it either.

### Surfaces the discussion MISSED

Exhaustive sweep over **tracked** files only (so no `.venv*`, no `__pycache__`, no generated data):

```bash
cd /workspaces/firestarter_app
git ls-files -z | /usr/bin/grep -zvE '^(tests/golden/|firestarter/data/|datasheets/|images/)' \
  | xargs -0 /usr/bin/grep -nIE '3\.9|py39|python3\.9|\(3, 9\)'
```

and in the meta repo:

```bash
cd /workspaces && /usr/bin/grep -rnIE '3\.9|py39|python3\.9' .planning/codebase/
```

Everything D-10/D-11 names was found. **Three additional surfaces were not in D-10/D-11's list:**

| # | Location | Exact current text | Why it matters |
|---|---|---|---|
| M-1 | `firestarter_app/firestarter/main.py:31` | `    if sys.version_info < (3, 9):  # noqa: UP036` | **The version tuple itself**, one line above the guard string D-11 names at `:33`. It is executable behaviour, not prose — leaving it at `(3, 9)` while the message says 3.11 would make the guard a lie in the opposite direction. |
| M-2 | `/workspaces/.planning/codebase/STRUCTURE.md:363` | `- **Python:** 3.9+` (under `### Python Application`, in a `## Build Environments` section whose `:360` carries `*[unverified in 2026-08-26 scoped remap — submodule contents, out of scope]*`) | A fourth co-statement of the floor in the meta repo, in a different file from `STACK.md`. |
| M-3 | `/workspaces/.planning/codebase/CONVENTIONS.md:173` | ``Union types use the Python 3.10+ `X \| Y` syntax in some places despite the `>=3.9` requirement:`` | Doubly falsified by this phase: the floor moves, **and** the D-09 sweep makes `X \| None` the norm rather than an exception. The `:166-177` block it heads shows `Optional[str]` / `Tuple[bool, Optional[int]]` as the house style, which the sweep reverses. |

`[VERIFIED: /usr/bin/grep over tracked files + meta .planning/codebase/, 2026-09-11]`

Nothing else co-states the floor. Specifically checked and **clean**: `firestarter_app/README.md`
(no Python version mentioned at all), `firestarter_app/.planning/codebase/*` other than `STACK.md`,
`.github/scripts/`, and the meta repo's `.github/` (which has no workflows).

### The `# noqa: UP036` at `main.py:31` must be preserved

A small mechanical trap, measured. With the guard raised to `(3, 11)` and `target-version = "py311"`:

```bash
ruff check --target-version py311 firestarter/main.py     # with the noqa: only the unrelated UP045
ruff check --target-version py311 firestarter/main.py     # with the noqa REMOVED:
# UP036 Version block is outdated for minimum Python version
#   --> firestarter/main.py:31:8
# help: Remove outdated version block
```

`[VERIFIED: measured 2026-09-11]` — UP036's fix is an **unsafe fix that deletes the entire runtime
guard**. The `# noqa: UP036` at `:31` is load-bearing and must survive; and nobody should run
`ruff check --fix --unsafe-fixes` on this tree.

Separately, the sweep deletes `main.py:17`'s `from typing import Optional  # noqa: UP035` outright
(the import becomes unused once `Optional[FrameType]` → `FrameType | None` at `:25`). That is the
autofix doing its job, not something the plan must arrange.

---

## 5. What `tests/test_py32_packaging.py` asserts — and what goes red

**The floor raise breaks nothing in this file.** Read in full this session
(`firestarter_app/tests/test_py32_packaging.py`, 300 lines). It contains **no assertion about
`requires-python`, `target-version`, `python_version`, or any CI pin.** Its seven tests assert:

| Test | Line | Asserts |
|---|---|---|
| `test_py32_block_is_non_vacuous` | `:171` | the `py32 = [` block parses non-empty |
| `test_py32_floor_is_exactly_the_expected_spec` | `:179` | `py32` requirements `== ["pyusb>=1.3.1,<2"]` — a **pyusb** floor, not a Python floor |
| `test_pyusb_absent_from_the_test_extra` | `:188` | no `pyusb` in the `test` extra |
| `test_py32_gate_fails_closed_…` | `:203` | fail-closed on a planted file |
| `test_d17_record_phrases_present_…` | `:217` | D-17 phrases near `def flash_method(` in `firmware.py` |
| `test_d17_gate_fails_closed_…` | `:225` | fail-closed on a planted file |
| `test_install_doc_address_parity_fails_closed_…` | `:287` | fail-closed on a planted doc |

The two floor mentions are **prose only**: the module docstring at `:43-49` and the
`_EXPECTED_PYUSB_SPEC` comment at `:78-81`. D-10's deletions of `:44-45` and `:79` touch neither an
assertion nor a constant.

Two secondary observations for the planner:

1. **Deleting only `:44-45` leaves a falsified argument standing.** The full `:43-49` paragraph is
   *"Why a regex scan, not a TOML parse"*, and its entire justification is the 3.9 floor. After this
   phase, `tomllib` is available by the project's own declared floor, so the paragraph's conclusion
   no longer follows from its premise even with the two named lines removed. Deleting the whole
   `:43-49` paragraph is the honest application of D-10; deleting two lines out of the middle leaves
   a non-sequitur. (The *code* stays a regex scan — that is not this phase's to change.)
2. **The pyusb comment at `:78-81` and `pyproject.toml:61-67` say the same falsified thing** and
   should be deleted together: `pyusb>=1.3.1`'s own `Requires-Python >=3.9.0` remains a true fact
   about pyusb, but "satisfiable on this project's py39 floor" stops being a reason for anything.

### Every assertion in the app's test suite that reads any of the four floor values

```bash
cd /workspaces/firestarter_app
/usr/bin/grep -rn "requires-python\|requires_python\|target-version\|target_version\|python_version\|python-version" tests/*.py
# tests/test_check_mypy_watermark.py:106:    "pyproject.toml: [mypy]: python_version: 3.9 is not supported "
# tests/test_check_mypy_watermark.py:186:    assert "python_version" in captured.err, (
# tests/test_runtime_dependencies.py:42:    `pyserial>=3.5 ; python_version<"3.12"` both reduce to `pyserial`.
# tests/test_py32_packaging.py:44:project's declared floor is py3.9 (ruff target-version = "py39", mypy
# tests/test_py32_packaging.py:45:python_version = "3.9"); tomli is not a dependency this project carries and
```

**Not one of these reads a live floor value.** `test_check_mypy_watermark.py:106` and `:186` operate
on the synthetic `CONFIG_REJECTION_OUTPUT` fixture, never on `pyproject.toml`.
`test_runtime_dependencies.py:42` is a docstring illustrating an *environment-marker* example
(`python_version<"3.12"` as a dependency marker), unrelated to the floor. The remaining two are the
prose lines D-10 deletes.

**Therefore: after this phase, nothing in `tests/` asserts the four floor values at all — which is
precisely the gap D-04 exists to close.**

---

## 6. Verification commands that will actually run

All commands assume `cwd = /workspaces/firestarter_app` unless stated. **Do not use the
devcontainer's ambient `python3`/`pytest`/`mypy`** — it is 3.12 and app CI is 3.11-only, a
divergence that has broken beta CI before.

| # | What it proves | Command (cwd `/workspaces/firestarter_app`) | FAILURE looks like |
|---|---|---|---|
| V1 | The replica interpreter is the right one and honest | `.venv/ci-replica/bin/python -V` → `Python 3.11.16`; `.venv/ci-replica/bin/python -c "import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('numpy') is None else 1)"` | version line is not `3.11.*`, or exit 1 from the numpy probe (a numpy-present venv truncates mypy at exit 2) |
| V2 | The four floor statements read as expected | `.venv/ci-replica/bin/python -c "import tomllib;d=tomllib.load(open('pyproject.toml','rb'));print(d['project']['requires-python'],d['tool']['ruff']['target-version'],d['tool']['mypy']['python_version'])"` then `/usr/bin/grep -rn "python-version" .github/workflows/` | printed triple is not `>=3.11 py311 3.11`; or the grep prints fewer than 3 lines, or any line is not `'3.11'` |
| V3 | ruff lint clean at the new target | `.venv/ci-replica/bin/ruff check firestarter/ tests/` | any line other than `All checks passed!`; exit ≠ 0 |
| V4 | ruff format clean (CI runs this separately — §2 shows the fix pass alone is not enough) | `.venv/ci-replica/bin/ruff format --check firestarter/ tests/` | `N files would be reformatted`; exit ≠ 0 |
| V5 | The mypy watermark gate, by its own code path | `.venv/ci-replica/bin/python tools/check_mypy_watermark.py` | absence of the literal line `OK: error count at watermark.`; or any `FAIL:`/`ERROR:` line; or `checked N` with N < 120; exit ≠ 0. **Exit 2 means the run could not be trusted, not that the tree is clean.** |
| V6 | The full suite, with a visible count | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` | the tail line is not of the form `N passed …`; any `FAILED` line. `-o addopts=""` is required — `[tool.pytest.ini_options] addopts = "-ra -q"` (`pyproject.toml:107`) plus a command-line `-q` doubles to `-qq` and **suppresses the count line entirely** |
| V7 | CI's exact pytest invocation, incl. the coverage floor | `.venv/ci-replica/bin/python -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | absence of `Required test coverage of 70% reached.`; any `FAILED` line |
| V8 | The standalone-CI shape (no sibling firmware repo, as in GitHub Actions) | `FIRESTARTER_FW_ROOT="$(mktemp -d)" .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` | any `FAILED`. This is `tools/ci_parity.sh` leg 1's own shape (`ci_parity.sh:85-89`) and is what catches a gate that only passes because the sibling repo happens to be present locally |
| V9 | All five legs at once | `bash tools/ci_replica_venv.sh` (**without** `--refresh` — see Pitfalls) | the final line is not `CI-REPLICA: PASS`; any `Leg N exit code: <non-zero>` |
| V10 | The phase left the shipped guard honest | `/usr/bin/grep -n "version_info\|requires Python" firestarter/main.py` | any `3, 9` or `Python 3.9` still present |
| V11 | No floor claim survives anywhere | `git ls-files -z \| /usr/bin/grep -zvE '^(tests/golden/\|firestarter/data/\|datasheets/\|images/)' \| xargs -0 /usr/bin/grep -nIE '3\.9\|py39\|python3\.9\|\(3, 9\)'` | any hit other than the two deliberate fixture sites (`tools/check_mypy_watermark.py:68`, `tests/test_check_mypy_watermark.py:106`) |
| V12 | Meta-repo docs corrected | (cwd `/workspaces`) `/usr/bin/grep -rnIE '3\.9\|py39' .planning/codebase/` | any hit at all — §4 lists all five current ones |

Two environment notes that belong in the plan's own setup step:

- **Test-env install** is `pip install -e '.[test]'` (`ci.yml:77-78` is `pip install -e .[test]`).
  Inside the replica venv this is already done; a fresh venv needs it.
- **`/usr/bin/grep`, never bare `grep`.** The devcontainer's `grep` is ugrep and honours
  `.gitignore`, so it silently under-scans. Every scan above whose completeness is load-bearing uses
  the absolute path.

---

## 7. Pitfalls specific to this change

### P-1. `ci_replica_venv.sh --refresh` would silently build a **3.12** venv today

`tools/ci_replica_venv.sh:111-121`'s `resolve_base_python` probes, in order: `python3.11` on `PATH`,
then `/home/vscode/.local/bin/python3.11`, then bare `python3`. Measured, right now:

```bash
command -v python3.11                        # (nothing — not on PATH)
[ -x /home/vscode/.local/bin/python3.11 ]    # false — absent
command -v python3 && python3 -V             # /usr/local/bin/python3 → Python 3.12.14
```

The existing `.venv/ci-replica` **is** 3.11.16 (`pyvenv.cfg` names
`/home/vscode/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin`, a **uv**-managed
interpreter on neither probed path). So: **reuse the venv; do not pass `--refresh`.** If a rebuild
is genuinely needed, prepend the uv bin dir first:

```bash
PATH="/home/vscode/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin:$PATH" bash tools/ci_replica_venv.sh --refresh
```

The script does not fail on a 3.12 base — it prints `INTERPRETER-DIVERGENCE: using 3.12.14, CI uses
3.11` and carries on. That stamp is easy to scroll past, and success criterion 2 forbids measuring
in 3.12. Check the `INTERPRETER:` line in the summary block every time. `[VERIFIED: measured
2026-09-11]`

Also note `uv python list` itself is broken in this container (`Failed to initialize cache at
/home/vscode/.cache/uv: Permission denied`) — set `UV_CACHE_DIR` to a writable path if uv is needed.

### P-2. Commit order is constrained (see §1)

Sweep-before-config → watermark gate fails 37 > 35 on push. Config-before-sweep → `ruff check` fails
182 on push. One intermediate commit is red either way; config-first is the one whose redness is
cosmetic (a lint backlog) rather than a false "new type errors introduced" signal.

### P-3. What a 3.9/3.10 consumer actually sees — D-12's premise is only half right

CONTEXT.md D-12 says *"pip already refuses on 3.9/3.10"* and quotes *"requires a different Python:
3.10.x not in '>=3.11'"*. **The quoted wording is correct; the word "refuses" is not, for the
default case.** Measured with a two-wheel local experiment (a dummy package published at 1.0.0 with
`requires-python = ">=3.9"` and 2.0.0 with `">=3.11"`), resolved for a 3.10 target:

```bash
python3 -m pip install --dry-run --no-index --find-links ./wheels \
  --python-version 3.10 --only-binary=:all: --target ./t310 fsfloordemo
# Processing ./wheels/fsfloordemo-2.0.0-py3-none-any.whl
# INFO: pip is looking at multiple versions of fsfloordemo to determine which version is compatible …
# Processing ./wheels/fsfloordemo-1.0.0-py3-none-any.whl
# Would install fsfloordemo-1.0.0          <-- SILENT DOWNGRADE, no error, exit 0

python3 -m pip install --dry-run --no-index --find-links ./wheels \
  --python-version 3.10 --only-binary=:all: --target ./t310b "fsfloordemo==2.0.0"
# ERROR: Package 'fsfloordemo' requires a different Python: 3.10.0 not in '>=3.11'
```

`[VERIFIED: measured 2026-09-11, pip 25.0.1, local wheel index]` The error string is also present
verbatim in pip's own source at
`/usr/local/lib/python3.12/site-packages/pip/_internal/resolution/legacy/resolver.py:103-106`.

So the real consumer experience after this lands:

- `pip install firestarter` on 3.9/3.10 → **no error**. pip silently selects the newest release that
  still advertises a compatible floor. (Today that is `firestarter 2.0.7`, since the 3.x line is all
  pre-releases; with `--pre` it would be the last `3.0.0bNN` that carried `>=3.9`.)
- `pip install firestarter==<new version>` or an upgrade to a pinned new version → the quoted error.

**Implication for D-12's release-note fragment:** "pip will refuse" is inaccurate and would mislead
a 3.10 user who sees an apparently-successful install of an old version. The honest one-liner is
that 3.9/3.10 users are **pinned to the last release advertising `>=3.9`** and will stop receiving
updates silently. This is a wording correction to make in the SUMMARY, not a re-opening of D-12.

Confirmed the published metadata shape from a locally-installed wheel of the current release
(`.venv311/…/firestarter-3.0.0b36.dist-info/METADATA`): `Requires-Python: >=3.9`, plus
`Classifier: Programming Language :: Python :: 3.9` and `:: 3.10`. `[VERIFIED: measured 2026-09-11]`

### P-4. Nothing in packaging needs re-baselining

- No test in `tests/` reads `requires-python`, and no test builds or inspects an sdist or wheel
  (`/usr/bin/grep -rln "sdist\|git archive\|MANIFEST" tests/*.py tools/*.py` → no matches).
- `publish.yml:56` builds with `python3 -m build` on the runner default interpreter and never
  asserts a floor.
- `beta-release.yml` runs `pytest tests/ -v` (`:75-76`) and the codegen drift gate, both covered by
  V6/V3 above, then `.github/scripts/update_version.py` — which carries no Python-version claim.
- Standing caution from prior work: a working-tree sdist is a false positive (220 vs 173 entries);
  only a clean `git archive` build is honest. Not needed here, since nothing in this phase changes
  what is packaged — only the metadata value.

### P-5. `ci-py32` and the PY32F071 DFU tooling are undisturbed

`ci-py32` runs the same `'3.11'` (§3). Its only content assertion is
`pytest tests/test_pyusb_api_surface.py -q` (`ci.yml:127-128`). The `[py32]` extra pins
`pyusb>=1.3.1,<2`, whose own `Requires-Python` is `>=3.9.0` — a *lower* bound than 3.11, so the
raise cannot make it unresolvable. `firestarter/py32_dfu.py` uses no 3.10/3.11-only syntax and is
left untouched by the sweep (its 14 UP045 sites are pre-suppressed, §2). **The only py32 surface
this phase touches is prose** — `pyproject.toml:61-67` and `tests/test_py32_packaging.py:78-81`.

### P-6. `tools/catalog/`'s `tomllib` use becomes consistent, and the drift gates run pre-install

`tools/catalog/codegen.py` and `codegen_vectors.py` already `import tomllib`, and `ci.yml:55-75`
runs them with `python3` **before** `pip install -e .[test]` (`:77-78`). That works only because the
CI interpreter is 3.11. Raising the floor does not change the mechanics; it makes the existing
dependency on 3.11-stdlib honest rather than incidental. No action — recorded so the planner does
not treat it as a change site.

### P-6b. Full-suite result on the complete change — one file red, nothing else

Measured end to end, in the 3.11 replica venv, on a worktree carrying **all four floor statements at
3.11, the classifier list trimmed, the `main.py` guard raised, the full ruff sweep plus `ruff format`
plus the 3 hand fixes**, with both sibling repos present so nothing skips for layout reasons:

| Tree | Result | Command |
|---|---|---|
| pristine, main tree | `2359 passed, 1 warning in 451.75s` | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` |
| **pristine, same worktree + symlinked siblings** (the control) | `2355 passed, 4 skipped, 1 warning in 447.33s` | same, `PYTHONPATH=<worktree>` |
| full change, same worktree + symlinked siblings | `6 failed, 2349 passed, 4 skipped, 1 warning in 468.19s` | same, `PYTHONPATH=<worktree>` |

**The delta between control and change is exactly the 6 `test_cap03_ack_layout_parity.py` failures**
— 2355 = 2349 + 6, with the same 4 skips in both. The 4 skips are meta-repo-artifact skips
(`test_audit_coverage_matrix.py:615`, `test_blast_radius_invariance.py:595`,
`test_variant_decode_evidence_stability.py:147` ×2) present in the control too, and are a scratch-
layout artifact, not a phase effect.

All 6 failures are `tests/test_cap03_ack_layout_parity.py`, one root cause, one regex edit (§2).
The three CI gates on the same tree: `ruff check` → `All checks passed!`;
`ruff format --check` → `179 files already formatted`; `check_mypy_watermark.py` → `checked 181
source files / mypy errors: 35 (watermark: 35) / OK: error count at watermark.` (exit 0);
`pytest --cov-fail-under=70` → `Required test coverage of 70% reached. Total coverage: 84.76%`.

`[VERIFIED: measured 2026-09-11]`

### P-7. Worktree/sibling-layout hazards, if the planner measures the way this research did

The app's test suite resolves a sibling firmware repo at `<app repo>/../firestarter` and, in a
couple of places, `<app repo>/../firestarter_app`. Measured in a scratch worktree without those
siblings, the pristine tree yields **2 spurious failures**
(`test_gen_validation_header.py::test_validate_spec_called_before_emission`,
`test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing`) and ~65 skips that
are 0 in the real tree. Both are layout artifacts, proven by running them on the *pristine*
worktree. Use `FIRESTARTER_FW_ROOT` (V8) or symlink the siblings, and never attribute a failure to
the change without re-running it on an unmodified tree in the same layout.

Also, an editable install does **not** follow a worktree — set `PYTHONPATH` to the worktree root and
print `firestarter.__file__` before trusting any number taken there.

### P-8. Do not run `ruff check --fix --unsafe-fixes` on this tree

Two separate reasons, both measured: it produces a format-unstable, inconsistently-noqa'd result at
`eprom_info.py:94-109` (§2), and UP036's unsafe fix **deletes the runtime version guard** at
`main.py:31-35` (§4).

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Reading `pyproject.toml` in the new gate | a regex over TOML text | stdlib `tomllib` | 3.11 stdlib by the project's own new floor; `tests/test_runtime_dependencies.py:1-18` is the in-repo precedent and explains the reasoning; a regex over TOML re-creates the exact stale-rationale defect this milestone is removing |
| Reading `python-version:` from workflow YAML | adding `pyyaml` | a line regex over `.github/workflows/*.yml` | `pyyaml` is not a project dependency and CONTEXT.md forbids making it one; the three pins are textually uniform; `tests/test_revision_constants_parity.py` is the in-repo precedent for a regex source-scan |
| Getting a trustworthy local mypy count | a hand-rolled `uv venv` | `tools/ci_replica_venv.sh` (reuse, no `--refresh`) | the ambient numpy PEP-695 stub truncates mypy at exit 2; raising the target to 3.11 does **not** lift that wall (`type` statements are 3.12 syntax) |
| Measuring the watermark | a hand-rolled `mypy` argv | `tools/check_mypy_watermark.py` | it binds mypy to `sys.executable` (`:106-115`) and applies all four GATE guards; a hand argv can report a number from a truncated run |
| Proving the sweep is complete | eyeballing the diff | `ruff check` **and** `ruff format --check`, both, after the fix pass | measured: the fix pass alone leaves 4 files unformatted, and CI runs both (`ci.yml:80-84`) |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The pip downgrade behaviour measured against a local `--find-links` wheel directory also holds against the real PyPI index. | P-3 | The release-note wording would over- or under-state what a 3.9/3.10 user sees. Mitigation: the mechanism (candidate filtering by `Requires-Python` in `package_finder.py:74-90`) is index-agnostic, but this was not measured against PyPI. `[ASSUMED]` |
| A2 | GitHub's `ubuntu-latest` runner behaves the same as the local replica venv for these gates. | §6 | A gate that passes locally could differ in CI. The replica venv is the project's own designated instrument for exactly this, and `ci_parity.sh`'s header documents the known gaps (interpreter minor version, ambient packages). `[ASSUMED]` |
| ~~A3~~ | ~~No `requires_fw`-gated test pins a `typing` construct the sweep changes beyond the one in §2.~~ **RESOLVED by measurement** — the full suite was run with both siblings present: 6 failures, all in `test_cap03_ack_layout_parity.py`, all one root cause. Not an assumption. | §2 | — |
| A4 | The successor backlog date 2027-10-31 is Python 3.11's end-of-life. | D-08 | The successor item would carry a wrong deadline. Carried from CONTEXT.md D-08; not independently verified against python.org this session. `[ASSUMED]` |

---

## Open Questions

1. **Where the four-way gate lives (A / B / C in §3).**
   - What we know: all three shapes have live precedents; `tools/` is outside mypy, `ruff check`
     and `ruff format`; only `check_mypy_watermark.py` has a named CI step.
   - What's unclear: whether the project wants a named CI step for this gate.
   - Recommendation: CONTEXT.md places this in Claude's Discretion. The planner picks; §3's table has
     the cost of each. Note shape A is the only one that puts the gate inside the quality gates the
     milestone is about, and it is the only one that needs no `ci.yml` edit.

2. **How much of `test_py32_packaging.py:43-49` to delete.**
   - What we know: D-10 names `:44-45`; the surrounding paragraph's whole argument rests on the 3.9
     floor and on `tomllib` being unavailable, both of which this phase falsifies.
   - Recommendation: delete the paragraph, not two lines out of its middle. Flagged here rather than
     decided, because D-10 named specific lines.

3. **`cli_handlers.py:1814` — delete the parenthetical, or resolve UP006 at the site.**
   - What we know: D-11's stated resolution (the sweep handles it) is measurably false (§2).
   - Recommendation: the planner must choose one of the two compliant options in §2; either is a
     one-line change.

---

## Sources

### Primary (HIGH confidence — read or executed this session)

- `firestarter_app/pyproject.toml` — all four floor statements, classifier list, prose blocks, watermark line
- `firestarter_app/tools/check_mypy_watermark.py` (full) and `tools/ci_replica_venv.sh` (full)
- `firestarter_app/.github/workflows/{ci.yml,beta-release.yml,publish.yml,release.yml}`
- `firestarter_app/tests/{test_py32_packaging.py,test_runtime_dependencies.py,test_check_mypy_watermark.py,test_cap03_ack_layout_parity.py,scan_paths.py}`
- `firestarter_app/firestarter/{main.py,cli_handlers.py,eprom_info.py,serial_comm.py}` (relevant regions)
- `/workspaces/.planning/codebase/{STACK.md,STRUCTURE.md,CONVENTIONS.md,TESTING.md,CONCERNS.md}`
- `firestarter_app/.planning/codebase/STACK.md`
- `/workspaces/.planning/{REQUIREMENTS.md § FLOOR, ROADMAP.md:5605-5640, config.json}`
- `/workspaces/.planning/notes/catalog-sync-check-retirement.md` (note shape; 230 lines, YAML frontmatter + `## VERDICT` + numbered sections); 27 `.md` notes exist in `.planning/notes/` (29 files total, incl. one `.py` and one `.patch`)
- Tool output: mypy 2.3.1, ruff 0.16.4, pip 25.0.1, `tomllib`, `pytest` — all commands shown inline

### Secondary (MEDIUM confidence)

- pip's own source for the incompatible-Python messages:
  `pip/_internal/resolution/legacy/resolver.py:103-106` and `pip/_internal/index/package_finder.py:74-90`
- `firestarter-3.0.0b36.dist-info/METADATA` in a local venv (current published metadata shape)

### Tertiary (LOW confidence)

- 3.11's 2027-10-31 EOL date — carried from CONTEXT.md D-08, not re-verified against python.org.

---

## Metadata

**Confidence breakdown:**

- Measured numbers (mypy counts, ruff splits, gate exits, line numbers): **HIGH** — every figure
  re-measured this session with the producing command recorded; no CONTEXT.md figure carried forward
  unverified.
- Gate-placement precedents: **HIGH** — enumerated from the live tree, not recalled.
- pip consumer behaviour: **MEDIUM** — mechanism measured against a local index, not PyPI (A1).
- 3.11 EOL date: **LOW** — inherited, unverified (A4).

**Research date:** 2026-09-11
**Valid until:** ~2026-10-11 (30 days). The measured counts are pinned to mypy 2.3.1 / ruff 0.16.4;
a version bump in either invalidates §1 and §2 and requires re-measurement. FLOOR-02's own deadline
is 2026-10-31.

*No `## Validation Architecture` section: `.planning/config.json` sets
`workflow.nyquist_validation: false`.*
*No `## Package Legitimacy Audit` section: this phase installs no external package. The only
dependency-adjacent decision is the explicit refusal to add `pyyaml` or `tomli` (§3), and `tomllib`
is stdlib.*
*No `## Environment Availability` section beyond the Measurement environment block above: the phase's
only external dependencies are the Python 3.11 replica venv (present, verified) and the already-installed
mypy/ruff/pytest toolchain.*
