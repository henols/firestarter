# Phase 186: The Python Floor, Before the EOL - Pattern Map

**Mapped:** 2026-09-11
**Files analyzed:** 1 new code file, 1 new note, 10 edited surfaces
**Analogs found:** 2 / 2 new files (both exact)

All analog paths below were checked with `git ls-files` and are **git-tracked source**, not
gitignored mirrors. App-repo paths are relative to `/workspaces/firestarter_app/`; meta-repo paths
are absolute under `/workspaces/`.

---

## HARD RULE — read before copying any excerpt

`/workspaces/CLAUDE.md` § "Source code comments — hard rule" binds this phase and cannot be
overridden by a plan: **no comments may be written into source under `firestarter/` or
`firestarter_app/`, ever.**

Every analog quoted below lives in a heavily-commented file. That commenting is **not** a pattern to
replicate:

| Construct in the analog | Copy it? |
|---|---|
| Module docstring (`"""…"""` at file top) | **Yes** — this is the model. `tests/test_runtime_dependencies.py:1-13` is the exemplar. |
| Function docstring | **Yes** — every helper in the analogs documents itself this way. |
| Attribute docstring (a bare string literal *after* a module constant) | **Yes** — see `test_runtime_dependencies.py:23-26`; it is a docstring, not a comment. |
| Assertion message string (`assert x, "…"`) | **Yes** — it is runtime data, not commentary. |
| `#` comment (e.g. `test_py32_packaging.py:78-81`, `:88-89`, `:99-100`) | **NO. Never.** |
| `# noqa: …` | Mechanical, not commentary — permitted where a lint rule requires it (`main.py:31`'s `# noqa: UP036` is load-bearing and must survive). A *falsified parenthetical* attached to one (`cli_handlers.py:1814`) is prose and is deleted. |

The new gate file must carry **zero `#` comment lines**. Everything it would explain goes in a
module docstring and in function docstrings. This is not a style preference; it is the standing rule,
and D-10's deletions in this same phase exist because the rule was previously broken.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| **NEW** `tests/test_python_floor_agreement.py` (name at planner's discretion) | test (fail-closed config gate) | file-I/O → parse → cross-source agreement assertion | `tests/test_runtime_dependencies.py` | **exact** (tomllib+pyproject half) |
| — its YAML-reading half | test (regex source-scan) | file-I/O → regex extract | `tests/test_py32_packaging.py` `:84-127` | **exact** |
| — its agreement half | test (two-source parity) | transform → compare | `tests/test_revision_constants_parity.py` | **role+flow match** (C header ↔ Python, not TOML ↔ YAML) |
| — its non-vacuity half | test (guard) | assertion | `tests/test_scan_paths_resolve.py:99-110` + `tests/test_runtime_dependencies.py:29-35, 56-62` | **exact** |
| **NEW** `/workspaces/.planning/notes/python-floor-decision.md` | rationale note (non-code) | document | `/workspaces/.planning/notes/catalog-sync-check-retirement.md` | **exact** |
| `pyproject.toml` | config | — | (edited in place, no analog needed) | n/a |
| `firestarter/main.py:31,33` | entrypoint guard | request-response (startup) | (edited in place) | n/a |
| `firestarter/cli_handlers.py:1814` | controller | — | (edited in place) | n/a |
| `firestarter/eprom_info.py:94-109` | service | — | (edited in place; the exact post-fix text is in RESEARCH §2) | n/a |
| `tests/test_py32_packaging.py:43-49, :78-81` | test | — | (prose deletion only — no assertion changes) | n/a |
| `tests/test_cap03_ack_layout_parity.py:200` | test | — | (one regex literal) | n/a |
| meta `.planning/codebase/{STACK,STRUCTURE,CONVENTIONS}.md`, app `.planning/codebase/STACK.md` | docs | — | (edited in place) | n/a |

---

## Pattern Assignments

### `tests/test_python_floor_agreement.py` (NEW — test, cross-source agreement)

**Primary analog:** `firestarter_app/tests/test_runtime_dependencies.py` (119 lines, Phase 181,
tracked). Read in full this session. It is the *only* file in this tree that parses
`pyproject.toml` with `tomllib`, and it was written for exactly the adjacent problem (pinning
`project.dependencies`). Copy its skeleton wholesale; swap the subject.

#### 1. The module-docstring idiom (`:1-13`, verbatim)

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

Three things to carry over, and one to change:
- Opening line names the **requirement ID** and says *"asserted by test rather than by a sentence"* —
  the new gate's opener should name **FLOOR-01/FLOOR-02** the same way.
- A paragraph justifying the `tomllib` choice over `toml`/`tomli`. For this phase the justification
  is stronger, not weaker: after D-01, 3.11 is the project's own declared floor, so `tomllib` is
  stdlib by the project's own metadata. Say that.
- A provenance paragraph naming the pattern map. **Change it:** Phase 181 honestly recorded "no
  precedent … an original decision". Phase 186 *does* have a precedent — this file. The new
  docstring should say so, citing `tests/test_runtime_dependencies.py` and `186-PATTERNS.md`.
- ASCII `--` is used for em-dashes throughout this file. Match it.

#### 2. Repo-root resolution + the recorded wrong-directory defect (`:29-35`, verbatim)

```python
def _pyproject_path() -> Path:
    """Resolve `pyproject.toml` from this test file's own parents, never a
    directory-relative path. This project has a recorded checker
    (`check_permitted_claims.py`) whose directory-relative `_HERE` resolved
    to the wrong directory, scanned nothing, and exited 0 -- the same
    failure mode a fragile relative resolution here would invite."""
    return Path(__file__).resolve().parent.parent / "pyproject.toml"
```

`Path(__file__).resolve().parent.parent` is the app-repo root from `tests/`. The new gate needs the
same anchor for **two** targets — `pyproject.toml` and `.github/workflows/`. Factor one
`_app_root()` helper rather than repeating the chain.

Note the weaker sibling idiom at `tests/test_py32_packaging.py:73-76`:

```python
_APP_DIR = Path(__file__).parent.parent
_PYPROJECT = _APP_DIR / "pyproject.toml"
```

It omits `.resolve()`. **Prefer the `test_runtime_dependencies.py` form** (with `.resolve()`), which
is newer and carries the stated reason. `test_py32_packaging.py`'s *virtue* is that its paths are
module globals, which is what makes the fail-closed legs monkeypatchable — combine both: module-level
globals, resolved with `.resolve()`.

#### 3. Non-vacuity guards before any comparison (`:51-62`, verbatim)

```python
def _parsed_runtime_dependencies() -> list[str]:
    """Parse `pyproject.toml` with stdlib `tomllib` and return the raw
    `project.dependencies` list, guarded against a mis-resolved path: the
    file must exist and the list must be non-empty before anything else is
    asserted about its contents."""
    path = _pyproject_path()
    assert path.is_file(), path
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    dependencies = data["project"]["dependencies"]
    assert dependencies, "project.dependencies parsed empty"
    return dependencies
```

And the dedicated vacuity **leg** kept separate from the drift legs (`:112-119`, verbatim):

```python
def test_an_empty_expected_set_fails_rather_than_passing_vacuously():
    """The separate, explicitly-named vacuity leg (never folded into the
    RED-drift tests above): comparing the real parsed set against an empty
    expected set must fail, not pass by coincidence."""
    dependencies = _parsed_runtime_dependencies()
    names = {_distribution_name(dep) for dep in dependencies}
    with pytest.raises(AssertionError):
        assert names == set()
```

Third instance of the same idiom, `tests/test_scan_paths_resolve.py:99-110` verbatim — the
**count-floor** shape, which is what RESEARCH §3 says the YAML half needs ("at least 3 pins"):

```python
def test_inventory_is_non_vacuous() -> None:
    """The union must be at least `_FLOOR` entries long -- an emptied or
    mis-globbed inventory fails here rather than passing silently, since
    test 1 above would otherwise vacuously pass over zero paths."""
    assert len(ALL_CROSS_REPO_PATHS) >= _FLOOR, (
        f"ALL_CROSS_REPO_PATHS has only {len(ALL_CROSS_REPO_PATHS)} entries, "
        f"expected at least {_FLOOR} -- the inventory may have been emptied "
        "or mis-derived."
    )
```

**This is the load-bearing part of the new gate.** Copy all three shapes: (a) `assert path.is_file()`
per target, (b) `assert <parsed> ` non-empty before comparing, (c) a named `>= _FLOOR` count leg for
the workflow glob, with `_FLOOR = 3` as a module constant that is *raised* when a fourth workflow
gains a pin, never lowered.

#### 4. The regex-over-a-non-Python-file idiom

Two candidates; **`tests/test_py32_packaging.py` is the closer analog** and is what the new gate
should follow, because (i) its subject is the same file family (config text, not C), (ii) its path
constants are module globals designed for monkeypatch fail-closed legs, and (iii) it pairs each
regex with a non-vacuity assert in a shared helper. `test_revision_constants_parity.py` is a
line-by-line state-machine extractor over a C header — heavier machinery than three uniform YAML
lines need.

Module-global compiled regex + reader helper, `tests/test_py32_packaging.py:84-86` and `:114-131`
(verbatim, `#` comments in the surrounding file deliberately not quoted):

```python
_PY32_BLOCK_RE = re.compile(r"^py32\s*=\s*\[(.*?)\]", re.DOTALL | re.MULTILINE)
_TEST_BLOCK_RE = re.compile(r"^test\s*=\s*\[(.*?)\]", re.DOTALL | re.MULTILINE)
_REQUIREMENT_RE = re.compile(r'"([^"]*)"')
```

```python
def _read_py32_requirements() -> list[str]:
    """Read `_PYPROJECT` (a module global, monkeypatchable) and return the
    non-vacuity-checked list of py32 extra requirement strings.

    Raises `AssertionError` if the `py32 = [` block is absent or empty --
    the fail-closed planted-file leg below exercises exactly this raise by
    monkeypatching `_PYPROJECT` before calling this same helper, so the
    real gate leg and the fail-closed leg share one code path."""
    text = _PYPROJECT.read_text(encoding="utf-8")
    requirements = _py32_extra_requirements(text)
    assert requirements, (
        f"'py32 = [' block not found (or found empty) in {_PYPROJECT} -- "
        "every downstream assertion about its contents would be vacuously "
        "true (research finding A-7)"
    )
    return requirements
```

The **one helper called by both the real leg and the planted-file fail-closed leg** is the
structural pattern to copy. Its fail-closed partner (`:203-210`) monkeypatches the module global:

```python
def test_py32_gate_fails_closed_on_a_planted_file_with_no_py32_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fail-closed RED demonstration: point `_PYPROJECT` at a planted file
    containing no `py32 = [` block and assert the shared helper raises
    rather than silently passing on an empty match set (research finding
    A-7)."""
```

The regex itself for the YAML half is given ready-made by RESEARCH §3:
`^\s*python-version:\s*['"]?([0-9]+\.[0-9]+)['"]?\s*$` over
`sorted(Path(".github/workflows").glob("*.yml"))` — note RESEARCH's warning that `publish.yml` and
`release.yml` carry **no** pin, so the gate must not require one per file; only the ≥3 total floor.

**Secondary analog (fail-closed on a missing file), `tests/test_revision_constants_parity.py:342-357`
verbatim** — use this shape for the workflows *directory* guard, since an absent directory is the
`check_permitted_claims.py` failure mode:

```python
def _read_header_text() -> str:
    """Read `FIRMWARE_HEADER`'s text, failing closed.

    An absent or unreadable header path is an ERROR, never a silent pass:
    returning an empty define set would make every downstream two-way
    assertion vacuously true (T-120-23). This is also the seam the planted-
    violation legs (below) exercise by `monkeypatch.setattr`-ing
    `FIRMWARE_HEADER` at module scope before calling any `_check_*` helper.
    """
    if not FIRMWARE_HEADER.is_file():
        raise AssertionError(
            f"firmware header not found at {FIRMWARE_HEADER} -- an absent "
            "or unreadable header must be a hard failure, never a silent "
            "pass with an empty define set"
        )
    return FIRMWARE_HEADER.read_text(encoding="utf-8")
```

#### 5. Failure-reporting style — the house convention

Measured convention across all three analogs: **`assert <cond>, "<message>"` with a parenthesised
multi-line message; the message names the offending file (by interpolating the path constant) and
the offending value (`!r`), and states what would otherwise have been vacuously true.** There is no
custom exception class and no `pytest.fail()` in this family.

Two real examples, verbatim.

`tests/test_py32_packaging.py:186-188` — names the value, uses `!r`, states the expectation:

```python
    assert requirements == [_EXPECTED_PYUSB_SPEC], (
        f"py32 extra requirements {requirements!r} != [{_EXPECTED_PYUSB_SPEC!r}]"
    )
```

`tests/test_scan_paths_resolve.py:90-95` — names the class of cause, and tells the reader exactly
which file to edit:

```python
    assert not missing, (
        "The following cross-repo scan path(s) do not resolve -- the "
        "firmware repo IS present, so this is a rename or move, not an "
        "absence. Update the path in tests/scan_paths.py (or the resolving "
        "module/tool) to match:\n" + "\n".join(f"  - {m}" for m in missing)
    )
```

For the four-way gate, the disagreement message should therefore name **all four values with their
source file** (not just report "mismatch"), e.g. a `{statement: (value, source)}` mapping rendered
one per line, so a reader sees which of the four drifted without opening anything. That is the
direct application of the second example.

Two further conventions visible across the family and worth matching:
- Multi-item failures are **collected into a list and reported together** (`missing`, `errors`), not
  short-circuited on the first — see `test_revision_constants_parity.py:446, :520, :558`
  (`assert not errors, "CMD_* two-way parity failures:\n" + "\n".join(...)`).
- Newer files (`test_runtime_dependencies.py`) carry **no return-type annotations on test
  functions**; older ones (`test_py32_packaging.py`, `test_scan_paths_resolve.py`) annotate `-> None`.
  Both pass the current gates. Prefer `-> None`, the majority.

#### 6. Multi-source agreement — the precedent DOES exist

Unlike Phase 181 (which recorded "no precedent"), this phase has one, and the planner should not
invent a shape:

**`firestarter_app/tests/test_revision_constants_parity.py` is a genuine multi-source agreement
gate** — it asserts that constants in the firmware's C header (`firestarter.h`) and the host's
`constants.py` name the same values, in **both directions**, and separately that
`COMMAND_NAMES` covers them. Its structure maps one-to-one onto the four-way floor gate:

| `test_revision_constants_parity.py` | New floor gate |
|---|---|
| `_read_header_text()` — fail-closed read of source 1 | `_parsed_pyproject()` — fail-closed tomllib read |
| `_extract_defines(text)` — regex extract + normalise | `_workflow_python_versions()` — regex extract + normalise |
| `_host_name(fw_name)` — **normalise across the two spellings** (`:329`) | the four normalisations in RESEARCH §3's table (`>=3.11` → `3.11`, `py311` → `3.11`, `'3.11'` → `3.11`) |
| `_check_cmd_two_way()` — collects `errors`, asserts both directions (`:378-449`) | `_check_four_way()` — collects disagreements, asserts all four equal |
| planted-violation legs via `monkeypatch.setattr` on the path global | planted-file legs via monkeypatched path globals |

The normalisation helper is the part most worth isolating into its own testable function, exactly as
`_host_name()` is: RESEARCH §3 records that `py39` → 3.9 but `py311` → 3.11, i.e. **the minor is not
a fixed width** — split after the first digit. A unit leg over that helper alone (`py39`, `py311`,
`py310`) costs three lines and catches the only genuinely subtle bug in the gate. Likewise, RESEARCH
warns `requires-python` is a *specifier*: assert the shape `^>=\d+\.\d+$` and fail closed on
anything else rather than stripping non-digits blindly.

**Honest caveat, in the Phase 181 spirit:** no existing test in this tree compares a value between
`pyproject.toml` and a GitHub workflow, and none compares TOML against YAML. The *structure* above is
copied; the TOML↔YAML pairing is new to this phase and should be recorded as such in the new file's
docstring.

#### 7. Two things NOT to copy from the analogs

- **`from __future__ import annotations`** (`test_py32_packaging.py:63`). Unnecessary at a 3.11
  floor. `test_runtime_dependencies.py` omits it and uses `list[str]` directly (`:51`). Follow the
  newer file.
- **`typing.Optional` / `typing.Dict`** anywhere. The new file is written after (or into) the D-09
  sweep and must be 3.11-clean from the first line, or it becomes its own UP045 finding. Use
  `X | None` and builtin generics.

---

### `/workspaces/.planning/notes/python-floor-decision.md` (NEW — rationale note, meta repo)

**Analog:** `/workspaces/.planning/notes/catalog-sync-check-retirement.md` (230 lines, tracked,
written 2026-09-11 for Phase 185 of this same milestone — the freshest instance of the shape).

**Measured shape of the analog:**

1. **YAML frontmatter**, three keys, closed by `---`:

```markdown
---
title: Catalog sync check retirement — why it never asserted what it claimed, and what is lost with it
date: 2026-09-11
context: v1.37 Phase 185, CLAIM-08 (D-01, D-02, D-03) — read from the live workflow file before deletion
---
```

Note `title` is a *sentence with a subordinate clause*, not a label; `context` names milestone,
phase, requirement ID, decision IDs, and how the evidence was obtained.

2. An `# H1` repeating the subject with its requirement ID in parentheses —
   `# Catalog sync check retirement (CLAIM-08)`.
3. **`## VERDICT` first**, before any evidence: the decision in bold in its first sentence, then the
   grounds, then an explicit paragraph enumerating what the note is required to carry.
4. **Numbered `## N. …` sections** thereafter — `## 1. The cause`, `## 2. Why the 2026-08-18 fix did
   not fix it`, `## 3. That the workflow's own comment is now false`, `## 4. That a naive beta
   fallback would not have worked either`, `## 5. The residual gap, named explicitly`. Each maps to
   one thing the requirement obliged the note to record.
5. **Verbatim quoted evidence in fenced blocks**, introduced as *"quoted verbatim from the file
   before its deletion"*.

**Do the 27 `.md` notes share a shape?** Partly — the consistency is real but not total, measured
across all 27:

| Property | Consistency |
|---|---|
| YAML frontmatter (`title`/`date`/`context`) | **25 of 27** carry it. Two do not (`disposable-artifact-inventory.md`, `gsd-installation-topology-and-1.1.0-removal.md`). |
| `## ` section headings | **27 of 27**. Universal. |
| A verdict/headline section first | Strong majority — `## VERDICT`, `## THE VERDICT`, `## Headline`, `## Decision`, `## Summary`, or a `## The load-bearing finding: …` opener. |
| Numbered sections (`## 1.`, `## 2.`) | Minority (~4). Prose headings are the norm. |
| Section headings as **sentences/claims**, not nouns | Consistent — e.g. *"Key insight — generality and speed are NOT opposed here"*, *"Negative result — pin this so nobody chases it"*. |
| Length | 54–546 lines; median ~130. |
| A closing `## Source references` / `## Related` | Common, not universal. |

`.planning/notes/` also contains one `.py` and one `.patch` (29 files total, 27 `.md`).

**Recommended shape for `python-floor-decision.md`**, following the analog and D-08's four required
contents:

```markdown
---
title: The Python floor raised to 3.11 — why, what it breaks, and the rule for the next move
date: 2026-09-11
context: v1.37 Phase 186, FLOOR-01/02/03 (D-01…D-12) — measured in the py3.11 CI-replica venv
---

# The Python floor (FLOOR-01)

## VERDICT
## 1. The decision, and the three rejected alternatives
## 2. The evidence
## 3. The standing rule
## 4. The successor: 3.11 EOLs 2027-10-31
```

Quote RESEARCH's measured figures verbatim in §2 (mypy 35/35 byte-identical at 3.10 and 3.11;
`PYTHON3_VERSION_MIN == (3, 10)`; 182 ruff findings, 190 fixes, 3 hand-fixed). Do **not** re-measure.
The analog's `## 5. The residual gap, named explicitly` has a direct counterpart worth carrying:
`py32_dfu.py`'s 14 pre-suppressed UP045 sites mean `target-version = "py311"` has its main consequence
switched off in one whole file (RESEARCH §2).

---

## Shared Patterns

### Path resolution (applies to the new gate only)
**Source:** `tests/test_runtime_dependencies.py:29-35`
`Path(__file__).resolve().parent.parent` from `tests/`, with the `check_permitted_claims.py`
wrong-directory defect cited in the docstring as the reason. Never a cwd-relative path.

### Non-vacuity before comparison (applies to every leg of the new gate)
**Sources:** `tests/test_runtime_dependencies.py:57, :61, :112-119`;
`tests/test_py32_packaging.py:124-129`; `tests/test_scan_paths_resolve.py:99-110`;
`tests/test_revision_constants_parity.py:342-357`
Three tiers, all three expected: file/dir exists → parsed result non-empty → a named
`test_*_is_non_vacuous` leg with a `>= _FLOOR` count.

### Fail-closed demonstration via monkeypatched module-global path
**Sources:** `tests/test_py32_packaging.py:203-210`; `tests/test_revision_constants_parity.py:342-357`
The real leg and the planted-file leg call **one shared helper**; the planted leg monkeypatches the
module-level path constant. This requires the new gate's paths to be module globals, not locals.

### Assertion messages
**Sources:** `tests/test_py32_packaging.py:186-188`; `tests/test_scan_paths_resolve.py:90-95`
`assert cond, (f"…{value!r}… {path} …")`; name the file, name the value, say what would otherwise be
vacuously true or what the reader should edit. Collect multiple failures and report together.

### Docstrings, never comments
**Source:** `tests/test_runtime_dependencies.py` in its entirety — 119 lines, **zero `#` comments**,
every explanation in a module/function/attribute docstring. It is the only analog here that already
complies with the standing hard rule, which is a second reason to treat it as the primary template.

---

## Edited Files — compact table (no excerpts; RESEARCH §4 carries the verbatim text)

| File | Site | Change | Source of truth |
|---|---|---|---|
| `pyproject.toml` | `:12` | `requires-python = ">=3.9"` → `">=3.11"` | D-01 |
| `pyproject.toml` | `:37`, `:38` | delete the 3.9 and 3.10 classifiers | D-03 |
| `pyproject.toml` | `:110` | `target-version = "py39"` → `"py311"` | D-01 |
| `pyproject.toml` | `:155` | `python_version = "3.10"` → `"3.11"` | D-01 |
| `pyproject.toml` | `:61-67` (falsifying sentence `:65`) | delete the falsified py39-floor prose block | D-10; RESEARCH corrects the range from `:63-66` |
| `pyproject.toml` | `:127` | delete the "py39 bounds" lint note | D-10 |
| `pyproject.toml` | `:139-154` | delete the 16-line `[tool.mypy]` rationale block | D-10 |
| `pyproject.toml` | `:174` | **unchanged** — `# mypy_error_watermark = 35` is parsed configuration, and the count does not move (RESEARCH §1) | D-10, D-05 |
| `firestarter/main.py` | `:31` | `sys.version_info < (3, 9)` → `(3, 11)`; **keep `# noqa: UP036`** — its removal lets an unsafe fix delete the guard | C-2, RESEARCH §4 |
| `firestarter/main.py` | `:33` | guard message 3.9 → 3.11 | D-11 |
| `firestarter/cli_handlers.py` | `:1814` | **survives the sweep** (C-1 falsifies D-11). Either delete the `(python3.9 compat)` parenthetical, or resolve to `-> dict[str, Any]:` and drop the noqa. Planner must choose. | C-1 |
| `firestarter/eprom_info.py` | `:94-109` | 3 hand UP045 fixes → `dict \| None` ×3, orphaned inner comments deleted; then a second `--fix` pass for the F401 on `:13` | D-09, RESEARCH §2 |
| `tests/test_py32_packaging.py` | `:43-49` | delete the whole "Why a regex scan, not a TOML parse" paragraph, not just `:44-45` — the argument's premise is falsified | D-10 + RESEARCH Open Q2 |
| `tests/test_py32_packaging.py` | `:78-81` | delete the falsified py39-floor half of the pyusb comment | D-10 |
| `tests/test_cap03_ack_layout_parity.py` | `:200` | `Optional\[LogMessage\]` → accept `LogMessage \| None`; fixes all 6 red legs | RESEARCH §2 |
| meta `/workspaces/.planning/codebase/STACK.md` | `:193`, `:203`, `:256` | 3.9+ → 3.11+ | D-11 |
| meta `/workspaces/.planning/codebase/STRUCTURE.md` | `:363` | `- **Python:** 3.9+` → 3.11+ | C-3 (missed by D-11) |
| meta `/workspaces/.planning/codebase/CONVENTIONS.md` | `:173` (block `:166-177`) | doubly falsified — floor moves AND the sweep makes `X \| None` the norm | C-3 (missed by D-11) |
| app `firestarter_app/.planning/codebase/STACK.md` | `:7`, `:12`, `:57` | 3.9+ → 3.11+, plus the one-line pointer to the meta note | D-07, D-11 |
| `tools/check_mypy_watermark.py:68`, `tests/test_check_mypy_watermark.py:106` | — | **LEAVE UNCHANGED** — mypy's own output as fixture text | D-11 (confirmed correct) |

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| — | — | — | None. Both new files have a direct in-tree analog. |

The nearest thing to a gap: **no existing test compares a value between `pyproject.toml` and a
GitHub workflow file**, and none compares TOML against YAML. The *structure* (fail-closed read →
normalise → collect disagreements → assert, with non-vacuity legs and a planted fail-closed leg) is
fully precedented by `test_revision_constants_parity.py`; only the two source formats are new. Record
that distinction in the new file's docstring rather than claiming either "copied" or "original"
wholesale.

---

## Metadata

**Analog search scope:** `/workspaces/firestarter_app/{tests,tools,firestarter}/`,
`/workspaces/firestarter_app/.github/workflows/`, `/workspaces/.planning/notes/`,
`/workspaces/.planning/codebase/`
**Files read this session:** `tests/test_runtime_dependencies.py` (full),
`tests/test_py32_packaging.py:1-210`, `tests/test_revision_constants_parity.py` (targeted ranges),
`tests/test_scan_paths_resolve.py:90-125`, `tests/scan_paths.py:33-58`,
`.planning/notes/catalog-sync-check-retirement.md:1-40` + heading sweep over all 27 notes
**Tracked-source verification:** `git ls-files` confirmed every analog path above
**Not re-measured:** every mypy/ruff/pytest figure is quoted from `186-RESEARCH.md`, per scope
**Pattern extraction date:** 2026-09-11
