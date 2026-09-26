# Phase 131: Gate Hardening & CI Parity — Pattern Map

**Mapped:** 2026-08-03
**Files analyzed:** 7 (3 modified, 4 created/extended)
**Analogs found:** 6 / 7 (one — `tools/ci_parity.sh` — has no true analog in the repo)
**Repo scope:** everything below is inside the `firestarter_app/` submodule (`beta` @ `16a313a`).

> **All line numbers below were re-measured live on 2026-08-03 against the working tree.**
> See §"Line-number re-measurement" for the audit, including the one number CONTEXT.md got wrong.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `tools/check_mypy_watermark.py` (modify) | CI checker / utility | subprocess → parse → exit-code | `tools/check_no_exists_proxy.py` | role-match (only checker that shells out; others AST-scan) |
| `tests/test_check_mypy_watermark.py` (create) | test | subprocess + in-process pure-function | `tests/test_check_no_exists_proxy.py` + `tests/test_check_devtest_orchestrator.py` | exact (house `test_check_*` shape) |
| `pyproject.toml` (modify) | config | declarative | its own `[py32]` pin block `:61-70` (an in-file precedent for a commented upper bound) | exact |
| `tests/test_sdp_db_invariant.py` (extend) | test | data-derived invariant | itself — `test_exactly_84_algorithm_0x0d_entries` `:81-100` | exact (extend in place) |
| `tests/test_sdp_table_parity.py` (extend) | test | derived parity + fail-closed | itself — `test_altered_temp_copy_fails_parity_non_vacuous` `:301`, `test_missing_override_path_fails_closed` `:349` | exact |
| `tests/test_check_devtest_orchestrator.py` (extend, D-15) | test | AST-derived subset | itself — `test_handler_function_names_all_resolve_to_real_callables` `:379-400` | exact (the mirror-direction leg) |
| `tools/ci_parity.sh` (create) | script | batch, 4 legs | **none** — `firestarter_test.sh` is a hardware script; `tools/` contains **zero** `.sh` files | no analog (see §No Analog Found) |

---

## Pattern Assignments

### `tools/check_mypy_watermark.py` (checker; subprocess → parse → exit-code)

**Analog:** `tools/check_no_exists_proxy.py` (373 lines) — the house checker shape.

**Current subject code, verbatim, `check_mypy_watermark.py:55-73`** (this is what D-01 splits):

```python
    result = subprocess.run(
        ["mypy", "firestarter/", "tests/"],          # :56  — bare PATH lookup (GATE-04)
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    output = result.stdout + result.stderr
    m = re.search(r"Found (\d+) errors?", output)     # :62  — regex BEFORE returncode
    if m:
        return int(m.group(1))                        # :64  — returncode never examined
    if result.returncode == 0 or "Success: no issues found" in output:
        return 0
```

**Pattern to copy — path anchoring** (`check_mypy_watermark.py:20-23`, already correct, keep it):

```python
# Resolve the repo root from this file's location so the gate behaves
# identically regardless of the caller's working directory (CR-WR-03).
# Layout: <repo>/tools/check_mypy_watermark.py -> repo root is two parents up.
REPO_ROOT = Path(__file__).resolve().parent.parent
```

The equivalent in the analog is `check_no_exists_proxy.py:115-116`:

```python
_HERE = os.path.dirname(os.path.abspath(__file__))
_APP_ROOT = os.path.dirname(_HERE)
```

> ⚠ **`_HERE` trap.** `check_devtest_orchestrator.py:80` uses `os.path.dirname(__file__)` **without
> `abspath`**, and `check_permitted_claims.py`'s `_HERE` resolved against the wrong dir, scanned
> nothing and exited 0 on v1.23's only outward-facing gate. `check_mypy_watermark.py` already uses
> `.resolve()` — **do not regress it**, and prove `REPO_ROOT` resolves locally from a foreign cwd
> (the end-to-end leg with `cwd=` set elsewhere covers this).

**Pattern to copy — exit-code convention** (`check_mypy_watermark.py:8-13`, docstring already
states it; the fix makes it true):

```
  0 — at or below watermark   1 — exceeds watermark   2 — tool/config failure
```

The analog uses the same 0/1/2 split with `2` reserved for "could not parse the target"
(`check_no_exists_proxy.py:343-350`):

```python
        except SyntaxError as e:
            print(f"ERROR: syntax error parsing {t}: {e}", file=sys.stderr)
            return 2
```

**Pattern to copy — the never-vacuous guard, and its ORDERING**
(`check_no_exists_proxy.py:305-334`). This is the direct structural precedent for
`MIN_CHECKED_SOURCE_FILES` (D-05): *assert the coverage of the check, not just its verdict*, and
hoist the coverage guard **above** any guard that an empty/degenerate input satisfies vacuously.

```python
def main(argv: list[str]) -> int:
    """...
    Guard order is load-bearing (never-vacuous BEFORE missing-target -- see
    the module docstring): an explicitly-emptied target list must fail
    before the missing-target guard, which is vacuously satisfied by an
    empty list, gets a chance to silently pass it through.
    """
    targets = resolve_targets(argv)

    if not targets:
        print(
            "FAIL: no scan targets resolved -- the gate cannot vacuously "
            "pass with nothing scanned"
        )
        return 1

    missing = [t for t in targets if not os.path.isfile(t)]
    if missing:
        print(
            "FAIL: scan target(s) not found on disk -- the gate cannot "
            f"vacuously pass with a target silently skipped: {missing}"
        )
        return 1
```

**Apply the same ordering to the hardened classifier:** `returncode not in (0,1)` → then require the
`(checked N source files)` completion clause → then `checked < MIN_CHECKED_SOURCE_FILES` → only then
compare to the watermark. Each earlier guard must be unreachable-by-the-later-one's-vacuity.

**Pattern to copy — the PASS line names what was scanned** (`check_no_exists_proxy.py:363-368`):

```python
    print(
        f"PASS: scanned {len(scanned)} file(s) for the module-level "
        f"absence-proxy idiom: "
        f"{', '.join(os.path.relpath(s, _APP_ROOT) for s in scanned)}"
    )
```

→ the hardened gate's success line should carry `checked N source files` for the same reason: an
outside reader can see the coverage, not just the verdict. The existing
`print(f"mypy errors: {count} (watermark: {watermark})")` at `:80` is the line the end-to-end test
leg asserts on (D-02 layer 3) — **keep that exact prefix** or update the test in the same commit.

**Anti-pattern this phase must NOT copy — the env seam.** All five other checkers expose
`FIRESTARTER_*_SRC`/`_TARGETS`. D-01 explicitly refuses one here, because those seams override
*which files to read* (fail-closed-able), whereas an argv seam would override *which program runs*
(a bypass). Reference for what is being declined, `check_no_exists_proxy.py:211-233`:

```python
# `os.environ.get(...)` with NO default is deliberate -- it must return
# `None` when the variable is absent ... so `resolve_targets` below can tell
# "absent -> use defaults" apart from "present-but-empty -> zero targets,
# never a silent fall-back to defaults".
FIRESTARTER_PROXY_LINT_TARGETS = os.environ.get("FIRESTARTER_PROXY_LINT_TARGETS")

def resolve_targets(argv: list[str]) -> list[str]:
    if argv:
        return list(argv)
    if FIRESTARTER_PROXY_LINT_TARGETS is not None:   # is not None, NOT truthiness
        return [p for p in FIRESTARTER_PROXY_LINT_TARGETS.split(os.pathsep) if p]
    return list(_DEFAULT_TARGETS)
```

Copy this shape **only** if a future scan-target seam is added. Not here.

---

### `tests/test_check_mypy_watermark.py` (test; subprocess + pure-function)

**Analogs:** `tests/test_check_no_exists_proxy.py` (237 lines) for the fail-closed legs;
`tests/test_check_devtest_orchestrator.py` (411 lines) for the runner helper and the docstring
"Coverage:" enumeration.

**Runner helper to copy** (`test_check_devtest_orchestrator.py:45-60`) — use this **verbatim in
shape** for D-02 layer 3 (the end-to-end leg):

```python
# Absolute path to the firestarter_app directory (cwd-independent), mirrors
# tests/test_check_dispatch_invariants.py:22.
_FA_DIR = Path(__file__).parent.parent


def _run_checker(
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, "tools/check_devtest_orchestrator.py"],
        cwd=str(_FA_DIR),
        capture_output=True,
        text=True,
        env=env,
    )
```

Note `sys.executable`, not `"python3"` — the same discipline FIX-2(i) applies to the checker itself.

**Module-docstring shape to copy** (`test_check_devtest_orchestrator.py:1-37`): a numbered
`Coverage:` list, one entry per leg, stating what each leg *proves*. `test_sdp_db_invariant.py:6-21`
does the same. The six D-02 legs map 1:1 onto six numbered entries.

**Fail-closed leg shape to copy** (`test_check_no_exists_proxy.py:165-199`) — this is the template
for the truncated-run and coverage-floor legs, including the "and print no PASS:" negative
assertion, which is what makes the leg non-hollow:

```python
def test_never_vacuous_empty_seam_fails_closed() -> None:
    """... must exit non-zero with the never-vacuous message and print no PASS:
    line -- proves the zero-targets guard fires even though it is hoisted
    above (and would otherwise be shadowed by a vacuously-satisfied)
    missing-target guard."""
    result = _run_checker(env_overrides={"FIRESTARTER_PROXY_LINT_TARGETS": ""})
    assert result.returncode != 0, (
        f"checker exited 0 on an explicitly-emptied target seam.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "no scan targets resolved" in result.stdout
    assert "PASS:" not in result.stdout
```

**Two adaptations required, because D-01/D-02 differ from every existing `test_check_*` module:**

1. **Legs 1–4 are in-process, not subprocess.** No existing `test_check_*` module calls a checker
   function directly — they all go through `_run_checker`. The pure-classifier legs therefore have
   **no exact precedent** and must use `pytest.raises(SystemExit)` + `.value.code`:

   ```python
   with pytest.raises(SystemExit) as exc:
       classify_mypy_result(2, TRUNCATED_OUTPUT)
   assert exc.value.code == 2
   ```

   The nearest in-repo precedent for importing a `tools/` module in-process is
   `test_check_devtest_orchestrator.py:387-389`:

   ```python
   check_devtest_orchestrator = importlib.import_module(
       "tools.check_devtest_orchestrator"
   )
   ```

   Use `importlib.import_module("tools.check_mypy_watermark")` — that import path is proven to work
   from `tests/` today.

2. **Leg 5 (argv proof) monkeypatches `subprocess.run` inside the checker's module namespace.** No
   precedent in any `test_check_*` module. The assertion is exactly:

   ```python
   assert captured_argv == [sys.executable, "-m", "mypy", "firestarter/", "tests/"]
   ```

   Assert the **whole list by equality**, not membership — memory
   `reference_gh_label_argv_needs_preexisting_label_and_write_access` records that a membership-only
   argv assertion misses the negative. Patch the name **in the checker module**
   (`monkeypatch.setattr(mod, "subprocess", fake)` or `setattr(mod.subprocess, "run", fake)`), never
   globally.

**Fixture placement.** `tests/fixtures/` is ruff-`extend-exclude`d (`pyproject.toml:113`, comment at
`:110-112` says it exists "for the source-scan gates"). Existing committed fixtures are
`planted_no_exists_proxy.py`, `planted_widenable_allowset.py`, `planted_permit_by_default.py`,
plus `.h`/`.cpp` ones. **Canned mypy output is text, not Python** — the stronger precedent is
`test_check_devtest_orchestrator.py`, which writes fixtures with `tmp_path.write_text(...)` inline
rather than committing them. For canned *strings*, prefer module-level string constants in the test
file (simplest, ruff-clean, no exclusion needed); reserve `tests/fixtures/` for anything a
subprocess must read from disk.

---

### `pyproject.toml` (config)

**Analog: itself.** The `[py32]` extra `:61-70` is the in-file precedent for a commented upper
bound — copy its comment discipline for D-14's `mypy>=2.1.0,<3`:

```toml
# Floor raised to 1.3.1 (HOST-07 / D-19): the current pyusb release at plan
# time, Requires-Python >=3.9.0, satisfiable on this project's py39 floor.
# Upper bound <2 refuses a future major that could reorder ctrl_transfer's
# parameters, which Plan 127-06's API-surface test pins against 1.3.1's shape.
py32 = [
    "pyusb>=1.3.1,<2",
]
```

The pattern: *floor + reason*, *ceiling + the named artifact that depends on the shape*. D-14's
ceiling comment must name the `(checked N source files)` regex.

**The line to change (D-13), verbatim `pyproject.toml:130-135`:**

```toml
[tool.mypy]
python_version = "3.9"          # Must be in config file — mypy 2.1.0 rejects --python-version 3.9 via CLI flag
ignore_missing_imports = true   # needed for tqdm, rich (no stubs)
disallow_untyped_defs = false   # gradual adoption — global stays lenient (D-10)
check_untyped_defs = false
# mypy_error_watermark = 35   # Updated Phase 71-07: floor after 71-06 added test_validate_family_cmd.py (6 AppContext mock-type errors). Prior: 29 (Phase 69-03).
```

The `# Updated Phase 71-07: … Prior: 29 (Phase 69-03).` comment at `:135` is the **house watermark
change-protocol shape** — a dated phase reference plus the prior value. Reuse that exact shape for
D-05's `MIN_CHECKED_SOURCE_FILES` comment and for D-06's `43/41/84` constant comment.

**Do not touch:** `requires-python = ">=3.9"` at `:12`; the `Programming Language :: Python :: 3.9`
classifier at `:37`; `# mypy_error_watermark = 35` at `:135`. (D-13; ROADMAP.)

---

### `tests/test_sdp_db_invariant.py` + `tests/test_sdp_table_parity.py` (extend; D-06)

**Analog: `test_sdp_db_invariant.py` itself.** The existing 84-count leg, verbatim `:81-100`:

```python
def test_exactly_84_algorithm_0x0d_entries() -> None:
    """TRACE-05 / CLOSE-01: exactly 84 chip_database.json entries have
    programming.algorithm == 13.
    ...
    """
    db = json.loads(_DB_FILE.read_text(encoding="utf-8"))
    selected = _select_0x0d_chips(db)
    assert len(selected) == 84, (
        "TRACE-05/CLOSE-01: expected exactly 84 chip_database.json entries "
        f"with programming.algorithm == 13, found {len(selected)}. A count "
        "change means a chip was added to or removed from the 0x0D bucket "
        "-- re-check every Phase 116+ trace-coverage assumption before "
        "proceeding."
    )
```

Two structural patterns to copy from this module:

**(a) Shared helper called by BOTH the real leg and the non-vacuity leg** (`:44-75`):

```python
# Shared helpers -- both the real-DB tests and the non-vacuity test call
# these, so the non-vacuity leg exercises the same code the real test does.
def _select_0x0d_chips(db: dict) -> list[tuple[str, dict]]:
    ...
def _assert_chip_id_check_false(selected: list[tuple[str, dict]]) -> None:
    offenders = [...]
    assert not offenders, ("... Offending chips: {offenders}")
```

The 43/41/84 element-wise leg (D-06 leg 1) should follow this exactly: a
`_partition_0x0d(db) -> tuple[list[str], list[str]]` helper, called by the count leg, the
element-wise leg, and a non-vacuity leg over a synthetic dict.

**(b) The assertion names every offender**, not just a count. Element-wise means the failure message
must name *which chip moved*.

**Fail-closed / non-vacuity precedents in `test_sdp_table_parity.py`:**
`test_altered_temp_copy_fails_parity_non_vacuous` (`:301`) and
`test_missing_override_path_fails_closed` (`:349`). Copy the naming convention
(`*_non_vacuous`, `*_fails_closed`) — `tests/test_skip_census.py`'s allow-list and the house
readers both key on these names.

> ⚠ **`test_sdp_table_parity.py` imports `fw_path`/`requires_fw` from `tests.fw_presence`
> (`:55`) and resolves firmware paths at module scope (`:62-63`).** Under recipe leg 1
> (`FIRESTARTER_FW_ROOT=$(mktemp -d)`) the whole module is `requires_fw`-skipped. **Any new
> 43/41/84 leg placed in this module is therefore invisible under leg 1 and in standalone CI.**
> Put the DB-only legs in `test_sdp_db_invariant.py`, whose docstring `:23-28` explicitly says it
> carries no FW skip marker for exactly this reason. This is also how D-18's negative criterion is
> satisfied.

> ⚠⚠ **MEASURED BLOCKER for D-06 leg 1 as written.** D-06 says "recompute the partition from
> `chip_database.json` + the committed `flags` bit-15 decode". **That is not implementable today:**
> - `chip_database.json` per-chip keys are `['electrical','part_number','pinout','programming','support_status']`
>   and `programming` keys are `['algorithm','chip_id_check','chip_id_value','pulse_duration']`.
>   **There is no `flags` field in the shipped DB** (measured: all 84 `0x0D` chips → `flags` absent).
> - `tools/infoic.xml` is **gitignored** (`.gitignore:29 — tools/infoic*.xml`) and **not present**
>   in the working tree. The bit-15 source is not committed.
> - Therefore the only DB-side derivation available is `sdp_capability_for_entry()` itself, which
>   makes "derived parity" self-parity — vacuous, and exactly P-10's hole.
>
> **Measured live, 2026-08-03:** feeding each of the 84 `0x0D` chips as
> `{"protocol-id": 13, "name": part_number}` through `sdp_capability_for_entry` yields
> **ALLOW 43 / REFUSE 41 / total 84**. The triple is real; only its *independent* derivation is
> unavailable.
>
> **Recommended shape for the planner:** make the independent side a **committed sorted list of the
> 43 ALLOW part numbers** (a hand-checked snapshot with the change-protocol comment), assert
> element-wise equality against `sdp_capability_for_entry`'s answer for all 84, and assert the
> literal triple separately. That preserves D-06's purpose — *a chip moving ALLOW→REFUSE produces a
> visible edit to a named constant* — without pretending to a derivation the repo cannot perform.
> Record the substitution and its reason; do not silently downgrade to parity-only.

**Entry-point line resolved:** `sdp_capability()` is at `firestarter/sdp_capability.py:266`
(research's two readings were 266 and 272 — **266 is correct**; `sdp_capability_for_entry`, the pure
one the tests should call, is at `:201`). `SDP_CAPABLE_TOKENS` is at `:70`.

---

### `tests/test_check_devtest_orchestrator.py` — the derived-subset leg (D-15)

**Analog: the mirror leg in the same file, `:379-400`, verbatim:**

```python
def test_handler_function_names_all_resolve_to_real_callables() -> None:
    """Every name in `_HANDLER_FUNCTION_NAMES` MUST resolve to a real
    callable in `firestarter.cli_handlers` -- turns the pre-Plan-121-09
    `_is_uv_eprom` dangling entry ... into a permanently-enforced invariant
    rather than a one-off fix. ..."""
    check_devtest_orchestrator = importlib.import_module(
        "tools.check_devtest_orchestrator"
    )
    from firestarter import cli_handlers

    missing = [
        name
        for name in check_devtest_orchestrator._HANDLER_FUNCTION_NAMES
        if not callable(getattr(cli_handlers, name, None))
    ]
    assert missing == [], (
        f"_HANDLER_FUNCTION_NAMES contains name(s) with no matching callable "
        f"in cli_handlers: {missing}"
    )
```

**Copy exactly, inverting the direction.** D-15's leg AST-parses `firestarter/cli_handlers.py`,
collects every module-level `_`-prefixed function name referenced from `dev_test`'s body, and
asserts `referenced <= _HANDLER_FUNCTION_NAMES`, with the failure message naming the omissions —
same `missing == []` + f-string-naming shape.

**The target set, verbatim `tools/check_devtest_orchestrator.py:138-150`** (9 names, and the
comment above it at `:130-137` already states the obligation this leg enforces):

```python
_HANDLER_FUNCTION_NAMES = frozenset(
    {
        "dev_test",
        "_verdict_code",
        "_sanitize_chip_token",
        "_is_uv_eprom",
        "_resolve_write_scope",
        "_default_uv_write_confirm",
        "_chip_id_fields",
        "_is_interactive",
        "_make_sampler",
    }
)
```

The comment above it (`:134-137`): *"Every future helper added to the `dev test` surface MUST be
listed here, or this gate silently under-covers exactly that new code"* — D-15 converts that prose
obligation into a mechanical one. Quote it in the new leg's docstring.

AST-walk precedent for "find functions referenced inside one function's body":
`check_devtest_orchestrator.py:226` (`if callee is not None and callee in _VPP_SET_NAMES:`) and
`check_no_exists_proxy.py:280-290` (module-level-assignment walk with `is not None` guards).

---

### `tools/ci_parity.sh` (script; batch)

**No analog.** `tools/` contains **zero** `.sh` files (verified). The only shell scripts in the repo
are `firestarter_test.sh` (171 lines), `write_test.sh` (126), `write_test_port.sh` (57) — all
**hardware** integration drivers, none with `set -e`, a leg-summary, or an aggregate exit code.

**The one reusable convention, `firestarter_test.sh:90-113`** — the banner + per-leg exit check:

```bash
exec_firestarter() {
    TEST_NAME=$1
    ...
    echo "---------------------------------"
    echo "Test: $TEST_NAME"
    echo "Cmd: $firestarter_cmd"
    echo "---------------------------------"
    echo
    $firestarter_cmd
    if test $? -gt 0; then
```

and the terminal `echo "All tests passed"` (`:171`). Copy the `---------------------------------`
banner and the trailing summary line; **do not** copy its structure otherwise — it `exit 1`s on the
first failure, which violates D-08's *"must not swallow leg failures"* + *"prints a final summary"*
(you need all four legs to run and a per-leg status).

**The four legs must mirror `ci.yml` exactly. Verbatim `ci.yml:60-73`:**

```yaml
      - name: Install package + test deps
        run: pip install -e .[test]

      - name: ruff lint
        run: ruff check firestarter/ tests/

      - name: ruff format check
        run: ruff format --check firestarter/ tests/

      - name: mypy type check (watermark gate)
        run: python tools/check_mypy_watermark.py

      - name: Run pytest with coverage
        run: pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```

- Leg 3's path set is **`firestarter/ tests/`** — neither wider nor narrower (`ci.yml:64`, `:67`).
- The gate step is `ci.yml:69-70`; `workflow_dispatch:` is `ci.yml:25`; `push: branches: [main]`
  is `ci.yml:9-11`; `Set up Python 3.11` is `ci.yml:33-36`. **All confirmed.**
- CI does **not** run `check_no_exists_proxy.py` — which is D-10's whole justification for keeping
  it out of the recipe. Confirmed: it appears nowhere in `ci.yml`.

**Leg 1's env var, why it must be process-level — `tests/fw_presence.py:77-88`, verbatim:**

```python
_APP_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_FW_ROOT = _APP_REPO_ROOT.parent / "firestarter"

FW_ROOT: Path = Path(os.environ.get("FIRESTARTER_FW_ROOT", str(_DEFAULT_FW_ROOT)))

FW_REPO_MARKER: Path = FW_ROOT / ".git"

FW_REPO_PRESENT: bool = FW_REPO_MARKER.exists()
```

`FIRESTARTER_FW_ROOT` is at **`:80`** (CONTEXT.md correct). `MissingScanTargetError` is at **`:105`**
(correct). The import-time-binding warning is at **`:35-45`** — CONTEXT.md says `:37-42`; the block
runs `:35-45`. Verbatim:

```
**Import-time binding -- read this before writing a test against this
module.** `FW_ROOT`, `FW_REPO_MARKER`, `FW_REPO_PRESENT`, `FW_ABSENT_REASON`
and `requires_fw` are all evaluated once, at import ... `monkeypatch.setenv`
runs *after* import and collection have already happened, so it has **no
effect** on any of these names. A test that needs a different `FW_ROOT` must
invoke pytest (or a checker script) in a **subprocess**, with
`FIRESTARTER_FW_ROOT` set in the child process's environment -- never an
in-process monkeypatch ... (RESEARCH Correction C-15).
```

Note `fw_presence.py:80` is the **deliberate exception** to the no-default env-seam rule (a root
path needs a default). Do not "fix" it.

**D-09's board stamp** — enumerate `/dev/ttyACM* /dev/ttyUSB*` and emit
`BOARD-ATTACHED: <list>` or `BOARD-ATTACHED: none` into the summary. No in-repo precedent; the
closest project convention is `dev test`'s port enumeration. Keep it a pure `ls`/glob, no serial
open.

---

## Shared Patterns

### Anti-hollow contract (applies to every test file this phase touches)

**Source:** `tests/test_check_devtest_orchestrator.py:1-11`

```
This is the mandatory anti-hollow pairing for the SAFE-03 gate: a checker
tool with no negative-fixture test is exactly the failure mode this project
incurred with v1.12's GATE-03 (a declared-empty detector that could never
fail because nothing concrete was asserted). Every planted-violation test
below injects a REAL subprocess-level violation ... -- never an in-process
synthetic -- so a passing test suite proves the checker itself (not the
test) fails the build on a real violation.
```

**Apply to:** `test_check_mypy_watermark.py`, both `sdp_*` extensions, the D-15 leg. Every new leg
needs a stated *what it proves* and a paired demonstration that it *can* fail.

### Assertion-failure messages name the offender AND the fix

**Source:** `tests/fw_presence.py:133-139`, `tools/check_no_exists_proxy.py:337-345`

```python
        raise MissingScanTargetError(
            f"{resolved} does not exist, but the firmware repo IS present "
            f"(marker found at {FW_REPO_MARKER}). This scan target was "
            "renamed or moved -- update this path (or the cross-repo "
            "scan-path inventory) rather than removing or bypassing this "
            "gate."
        )
```

**Apply to:** every message this phase writes — including the reworded `INFO:` line. The current
`INFO: … Lower watermark in pyproject.toml.` (`check_mypy_watermark.py:87-90`) is the exact
opposite: it names a *bypass* as the fix. The rewrite must make the suggestion conditional on a
verified-complete run and say so.

### Explicit non-glob target lists

**Source:** `tools/check_no_exists_proxy.py:118-207` (an 80-entry literal enumeration, never a
tree-walk), documented at `:49`.
**Apply to:** anything this phase adds that enumerates files. `MIN_CHECKED_SOURCE_FILES` is the
deliberate inversion of this (D-05: literal, *not* derived — because there the derivation *is* the
measurement).

### Subprocess, never monkeypatch, for environment simulation

**Source:** `tests/fw_presence.py:35-45`; every `_run_checker` in every `test_check_*` module.
**Apply to:** recipe leg 1, and any leg simulating a different tree/interpreter/channel.
**Exception carved out by D-02 layer 2:** monkeypatching `subprocess.run` *inside the module under
test* is not environment simulation — it is a call-argument probe, and adds no production seam.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `tools/ci_parity.sh` | script | batch, 4 legs | `tools/` has zero `.sh` files. The three repo-root scripts are hardware drivers with no `set -e`, no per-leg status, no aggregate exit code. Take the banner + summary convention from `firestarter_test.sh:106-110,171`; author the leg-aggregation logic fresh per D-08. |
| Pure-classifier in-process test legs | test | in-process | No existing `test_check_*` module calls a checker function directly — all six go through a subprocess `_run_checker`. `pytest.raises(SystemExit)` + `.value.code` has no in-repo precedent against a `tools/` module. Nearest: the `importlib.import_module("tools.…")` line at `test_check_devtest_orchestrator.py:387`. |
| An independent 43/41/84 derivation | data | derived | The `flags` bit-15 source (`tools/infoic*.xml`) is gitignored and absent; `chip_database.json` carries no `flags` field. See the blocker box under D-06. |

---

## Line-number re-measurement

Every number in the dispatch brief, checked against the live tree (`firestarter_app` @ `16a313a`):

| Claim | Verdict |
|---|---|
| `check_mypy_watermark.py` 96 lines; `count_mypy_errors()` `:43-73`; argv `:56`; regex-before-returncode `:62-65` | ✅ all correct |
| `pyproject.toml` `requires-python` `:12`; mypy pin `:76`; ruff target `:101-102`; `extend-exclude` `:113`; `[tool.mypy]` `:130`; `python_version` `:131`; watermark `:135`; `follow_imports` block "near `:170`" | ✅ all correct (`follow_imports = "silent"` block is `:167-183`) |
| `ci.yml` ruff paths `:63-67`; gate `:69-70`; `workflow_dispatch:` `:25`; `push: branches` `:9-11`; Python 3.11 `:33-36` | ✅ all correct |
| `fw_presence.py` `FIRESTARTER_FW_ROOT` `:80`; `MissingScanTargetError` `:105` | ✅ correct |
| `fw_presence.py` import-time-binding warning `:37-42` | ⚠ **MOVED/IMPRECISE** — the block spans **`:35-45`** |
| `test_sdp_db_invariant.py` 84-count assertion `:81-93` | ⚠ **IMPRECISE** — `def` at `:81`, the `assert len(selected) == 84` runs **`:91-98`**; the test ends at `:100` |
| `sdp_capability.py` entry point "266 or 272" | ✅ resolved: **`sdp_capability` at `:266`**; `sdp_capability_for_entry` at `:201`; `SDP_CAPABLE_TOKENS` at `:70`; file is 281 lines |
| `check_sdp_capability_invariants.py` 43/41/84 provenance at `:12` | ✅ correct (`:11-13`) |
| `check_devtest_orchestrator.py` `_HANDLER_FUNCTION_NAMES` `:138-150`, 9 names | ✅ correct |
| `firestarter/tests/test_flash_path_record_sync.py:694` | not re-read — read-only, firmware repo, out of scope (D-17) |

**Environment caveat:** measured in the devcontainer (Python 3.12.13); CI runs 3.11. Line numbers
are environment-independent, but any *mypy behaviour* observed here is not (P-18(a)).

---

## Metadata

**Analog search scope:** `firestarter_app/tools/`, `firestarter_app/tests/`,
`firestarter_app/.github/workflows/`, `firestarter_app/*.sh`, `firestarter_app/pyproject.toml`
**Files read in full or targeted:** 14
**Firmware repo (`firestarter/`):** not searched — out of scope (D-17, ROADMAP)
**Pattern extraction date:** 2026-08-03
