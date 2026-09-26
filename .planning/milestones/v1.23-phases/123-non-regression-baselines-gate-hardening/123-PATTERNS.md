# Phase 123: Non-Regression Baselines & Gate Hardening - Pattern Map

**Mapped:** 2026-07-30
**Files analyzed:** 24 new/modified files across 3 repos
**Analogs found:** 19 / 24 (5 genuinely new — see §No Analog Found)

Authoritative file list derived from `123-RESEARCH.md` §"Component responsibilities",
§"Architectural Responsibility Map" and §"The Seven Proxy-Carrying Modules".

---

## File Classification

### Firmware repo (`/workspaces/firestarter/`) — milestone branch off `beta`

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/check_size_baseline.py` (BASE-01 comparator) | checker/CLI | file-I/O + transform (parse pio stdout → compare JSON) | `/workspaces/firestarter/scripts/check_uno_ram.sh` (parser + exit taxonomy) **and** `/workspaces/firestarter_app/tools/check_mypy_watermark.py` (Python shape) | role-match (composite) |
| baseline JSON (e.g. `scripts/size_baseline.json`) | config/data | batch (read-only record) | `/workspaces/firestarter_app/tools/baseline/dispatch_baseline.json` | exact |
| `scripts/check_cmake_manifest.py` (BASE-04) | checker/CLI | file-I/O + transform | `/workspaces/firestarter_app/tools/check_no_log_in_sdp_window.py` | exact |
| `scripts/check_orphan_provisional.py` (BASE-05) | checker/CLI | file-I/O (tree grep) | `/workspaces/firestarter_app/tools/check_no_log_in_sdp_window.py` | exact |
| `scripts/check_build_warnings.py` (BASE-06) | checker/CLI | transform (parse build log) + watermark | `check_uno_ram.sh` (parse) + `check_mypy_watermark.py` (watermark + exit 2) | role-match |
| `tests/test_check_*.py` × 4 | test | request-response (subprocess) | `/workspaces/firestarter_app/tests/test_check_no_log_in_sdp_window.py` + meta `test_check_permitted_claims.py` | exact (test shape) / partial (repo conventions differ — see §Shared Patterns "Firmware-repo test constraints") |
| `tests/test_checker_convention.py` (BASE-08 meta-test) | test | file-I/O (glob + floor) | **none** | no analog |
| `tests/fixtures/planted_*` (new directory) | fixture | — | `/workspaces/firestarter_app/tests/fixtures/planted_log_in_window.cpp` | exact |
| `tests/fixtures/planted_macro_redef.cpp` (D-14) | fixture (compiled by host `g++`) | — | **none** (no compiled fixture exists in either repo) | no analog |
| `tests/fixtures/*.log` (captured pio output) | fixture | — | `/workspaces/firestarter/tests/golden/stable-baseline.h` (committed byte-exact input) | partial |

### Host repo (`/workspaces/firestarter_app/`) — milestone branch off `beta`

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tests/fw_presence.py` (shared helper, D-09) | test utility | file-I/O probe | `tests/test_check_no_log_in_sdp_window.py:61-77` (the `_requires_fw` marker block being centralised) | role-match |
| 7 modules rekeyed (`test_revision_constants_parity.py`, `test_dispatch_mirror.py`, `test_sdp_bus_config_drift.py`, `test_check_no_log_in_sdp_window.py`, `test_sdp_table_parity.py`, `test_check_is_memory_cmd_no_ifdef.py`, `test_gen_validation_header.py`) | test (modified) | — | each other (see §Pattern Assignments) | exact |
| `tests/scan_paths.py` + `tests/test_scan_paths_resolve.py` (D-11) | config + test | file-I/O batch | `check_permitted_claims.py`'s `_DEFAULT_TARGETS` (explicit non-pattern list) + fail-closed missing-target guard | role-match |
| `tests/test_skip_census.py` (BASE-03/D-10) | test | event-driven (pytest report hook / subprocess run) | **none** | no analog |
| recurrence lint (`tools/check_no_exists_proxy.py` + `tests/test_check_no_exists_proxy.py`) (D-09) | checker + test | file-I/O AST/regex scan | `tools/check_is_memory_cmd_no_ifdef.py` + its paired test; `tests/fixtures/planted_permit_by_default.py` (planted **Python** fixture already exists) | exact |
| `tests/fixtures/fake_firestarter/` (D-12) | fixture (committed tree) | — | **none** (no committed fake-sibling tree exists) | no analog |

### Meta repo (`/workspaces/.planning/phases/123-…/`)

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `check_permitted_claims.py` (v1.23) | checker/CLI | file-I/O scan | `.planning/phases/122-…/check_permitted_claims.py` | exact (near-verbatim copy) |
| `test_check_permitted_claims.py` | test | request-response (subprocess) | `.planning/phases/122-…/test_check_permitted_claims.py` | exact |
| `fixtures/{clean_control.md, clean_control_second.md, planted_py32_overclaim.md, planted_missing_caveat.md, clean_avr_bench_control.md}` | fixture | — | `.planning/phases/122-…/fixtures/` (4 files) | exact + 1 new (`clean_avr_bench_control.md`, D-16 negative direction) |
| `123-NONREGRESSION.md` (D-05 evidence artifact) | doc | — | `.planning/phases/122-…/122-NONREGRESSION.md` | exact |

---

## Pattern Assignments

### `scripts/check_*.py` (firmware repo, checker, file-I/O)

**Primary analog:** `/workspaces/firestarter_app/tools/check_no_log_in_sdp_window.py`
**Secondary analog:** `.planning/phases/122-…/check_permitted_claims.py`

**Module-top path constant + env seam WITH a default** (`check_no_log_in_sdp_window.py:92-103`) —
use this shape when there is exactly one scan target:

```python
# Module-top path constant (mirrors tools/check_dispatch.py:24-33's
# env-overridable path-constant idiom, and tools/check_devtest_orchestrator.py's
# FIRESTARTER_DEVTEST_SRC seam).
_HERE = os.path.dirname(__file__)
_DEFAULT_SDP_SRC = os.path.join(
    _HERE, "..", "..", "firestarter", "src", "proms", "eeprom_28c.cpp"
)

# Env-override seam: lets the paired pytest point this checker at a
# deliberately-violating fixture file (tests/fixtures/planted_log_in_window.cpp)
# without editing the real, clean eeprom_28c.cpp (anti-hollow contract, D-04).
FIRESTARTER_SDP_SRC = os.environ.get("FIRESTARTER_SDP_SRC", _DEFAULT_SDP_SRC)
```

**Env seam WITHOUT a default** (`check_permitted_claims.py:58-68`) — use this shape when the
checker has a *list* of targets, because absent-vs-present-but-empty must stay distinguishable
(BASE-07 criterion 5, and BASE-04's two-fixture arming cases):

```python
# Env-override seam (mirrors check_no_community_support_status_write.py's
# FIRESTARTER_DISP01_REPORT and check_devtest_orchestrator.py's
# FIRESTARTER_DEVTEST_SRC): lets the paired pytest point this checker at
# deliberately-violating fixtures under fixtures/ without editing a real
# closing artifact. `os.environ.get(...)` with NO default is deliberate --
# it must return None when FIRESTARTER_CLAIMSCAN_TARGETS is absent from the
# environment, and the (possibly empty) raw string when present, so
# resolve_targets() below can tell "absent -> use defaults" apart from
# "present-but-empty -> zero targets, never a silent fall-back to
# defaults". Values are split on os.pathsep; empty segments are dropped.
FIRESTARTER_CLAIMSCAN_TARGETS = os.environ.get("FIRESTARTER_CLAIMSCAN_TARGETS")
```

**Explicit non-pattern default target list** (`check_permitted_claims.py:41-56`) — copy the
comment, not just the list; it is the rationale for the fixture-placement discipline:

```python
# Explicit five-element default target list -- NEVER pattern-based and
# NEVER discovered by walking a directory tree. The `fixtures/`
# subdirectory deliberately contains violating text
# (planted_forbidden_claim.md, planted_missing_caveat.md) and must never be
# reachable from this default set, the same discipline
# `firestarter_app/tests/fixtures/planted_log_in_window.cpp` observes
# relative to its own checker's scan targets. If a future edit turns this
# into a wildcard-expanded or tree-walked set, the fixtures directory would
# poison every default-mode run.
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "122-LEDGER.md"),
    ...
]
```

**Three-level precedence resolver** (`check_permitted_claims.py:136-149`) — the `is not None`
line is load-bearing:

```python
def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    FIRESTARTER_CLAIMSCAN_TARGETS env seam if the variable is present in
    os.environ (checked via `is not None`, not truthiness -- an explicitly
    empty value must resolve to zero targets, never a silent fall-back to
    defaults); else `_DEFAULT_TARGETS`.
    """
    if argv:
        return list(argv)
    if FIRESTARTER_CLAIMSCAN_TARGETS is not None:
        return [p for p in FIRESTARTER_CLAIMSCAN_TARGETS.split(os.pathsep) if p]
    return list(_DEFAULT_TARGETS)
```

**Fail-closed + never-vacuous guards** (`check_permitted_claims.py:164-181`). RESEARCH
recommends **hoisting the `if not targets` block above the `missing` block** in the v1.23 copy;
the observable behaviour is unchanged:

```python
    missing = [t for t in targets if not os.path.isfile(t)]
    if missing:
        print(
            "FAIL: scan target(s) not found on disk -- the gate cannot "
            f"vacuously pass with a target silently skipped: {missing}"
        )
        return 1

    if not targets:
        # Defense in depth: reached only when the env seam is explicitly set
        # to the empty string (or argv resolves to an empty list some other
        # way) -- the missing-target guard above is vacuously satisfied by
        # an empty list, so this is the real never-vacuous guard.
        print(
            "FAIL: no scan targets resolved -- the gate cannot vacuously "
            "pass with nothing scanned"
        )
        return 1
```

**Bucketed FAIL printer with a 20-row cap** (`check_permitted_claims.py:152-157`):

```python
def _print_bucket(label, violations):
    print(f"FAIL: {len(violations)} {label}:")
    for v in violations[:20]:
        print(f"  {v}")
    if len(violations) > 20:
        print(f"  ... and {len(violations) - 20} more")
```

**Anti-skip PASS line naming every scanned file** (`check_permitted_claims.py:212-217`,
and `check_no_log_in_sdp_window.py:434`):

```python
    print(
        f"PASS: scanned {', '.join(os.path.relpath(s, _HERE) for s in scanned)}; "
        f"{caveat_present_count} file(s) carry the required silicon caveat "
        "(this PASS is the mechanizable half of criterion 4 only -- see the "
        "module docstring's explicit non-claim)"
    )
    return 0
```

```python
    print(f"PASS: no logging call in SDP timing window ({path}, {range_desc})")
```

**Fail-closed on unresolvable structure — `ValueError` naming the fix, never a silent pass**
(`check_no_log_in_sdp_window.py:308-315`). This is the exact shape D-07's "armed but target
unresolvable ⇒ hard failure" needs:

```python
    emitter_body = _find_function_body(cleaned_text, _EMITTER_FUNC_NAME)
    if emitter_body is None:
        raise ValueError(
            f"{_EMITTER_FUNC_NAME}() not found (or not brace-balanced) in "
            "source -- if the emitter was renamed or replaced, add the new "
            "anchor/name for _EMITTER_FUNC_NAME in "
            "check_no_log_in_sdp_window.py rather than deleting this gate"
        )
```

caught in `main()` and converted to an exit code (`:412-416`):

```python
    try:
        violations, emitter_range, poll_range = scan(source_text)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
```

**Docstring convention** — `check_no_log_in_sdp_window.py:1-86` and
`check_permitted_claims.py:1-31`. Both end with an explicit `Exit codes:` block. The
**"explicit non-claim"** paragraph (`check_permitted_claims.py:25-30`) is the load-bearing
convention BASE-07 must carry forward:

```
**Explicit non-claim (load-bearing):** a green run of this gate is the
mechanizable half of ROADMAP criterion 4 ONLY. It cannot detect an implied
overclaim, a misleading omission, or wrong tone -- criterion 4 is closed by
this gate PLUS the D-16 blocking operator wording review (plan 122-11). A
green run of this gate must never be reported, in any SUMMARY or ledger
entry, as by itself satisfying criterion 4.
```

`check_no_log_in_sdp_window.py:45-55` carries the paired **anti-hollow contract** paragraph
naming the v1.12 GATE-03 failure mode, the paired pytest, the fixture, and the env seam by
name. Every new checker docstring should carry an equivalent.

**Entry point** (both files): `if __name__ == "__main__": sys.exit(main())`.

---

### `scripts/check_size_baseline.py` (BASE-01 comparator, checker, transform)

**Analog A — parser + exit taxonomy:** `/workspaces/firestarter/scripts/check_uno_ram.sh`
(the only file in `firestarter/scripts/`; this comparator supersedes it).

Header + exit contract (lines 1-26) — carry the `Exit codes:` block and the
"change only when the accepted baseline changes" comment into the JSON's meta block:

```bash
# Runs `pio run -e uno`, parses the linker RAM report line:
#   RAM:   [=======   ]  73.4% (used N bytes from M bytes)
# computes free RAM = M - N, and fails (exit 1) if free RAM < RAM_FLOOR.
#
# Exit codes:
#   0  — free RAM >= RAM_FLOOR (baseline passes)
#   1  — free RAM < RAM_FLOOR (regression detected)
#   2  — could not parse the RAM line from build output

set -euo pipefail

# Baseline floor (Phase-49 / 2026-06-01 measurement: 1503 B used / 2048 B total)
# Change only when the accepted baseline changes after a deliberate Plan 04
# post-change measurement confirms the new floor is still safe.
RAM_FLOOR=545   # minimum acceptable free RAM in bytes (Phase-49 baseline ceiling)
```

Parse + fail-closed-on-unparseable (lines 39-58) — this is the `exit 2` arm the Python
comparator inherits:

```bash
RAM_LINE="$(echo "$BUILD_OUTPUT" | grep -E '^RAM:')"

if [ -z "$RAM_LINE" ]; then
    echo "[check_uno_ram] ERROR: could not find 'RAM:' line in pio output."
    echo "$BUILD_OUTPUT" | tail -20
    exit 2
fi

USED_BYTES="$(echo "$RAM_LINE" | grep -o 'used [0-9]* bytes' | grep -o '[0-9]*')"
TOTAL_BYTES="$(echo "$RAM_LINE" | grep -o 'from [0-9]* bytes' | grep -o '[0-9]*')"

if [ -z "$USED_BYTES" ] || [ -z "$TOTAL_BYTES" ]; then
    echo "[check_uno_ram] ERROR: could not parse used/total bytes from RAM line."
    echo "  RAM line was: $RAM_LINE"
    exit 2
fi
```

PASS/FAIL output shape (lines 65-73) — `FAIL:` names both numbers and points at the
investigation:

```bash
if [ "$FREE_BYTES" -lt "$RAM_FLOOR" ]; then
    echo "[check_uno_ram] FAIL: free RAM ${FREE_BYTES} B < floor ${RAM_FLOOR} B"
    ...
    exit 1
fi

echo "[check_uno_ram] PASS: free RAM ${FREE_BYTES} B >= floor ${RAM_FLOOR} B"
exit 0
```

> **RESEARCH note to carry into the plan:** `RAM_FLOOR=545` currently **FAILS** — measured Uno
> free RAM is 475 B. Do not port the 545 constant; the baseline JSON replaces it. Whether the
> superseded shell script is deleted or left in place is a plan decision, but it must not be
> left silently red.

**Analog B — Python watermark + three-way exit:** `/workspaces/firestarter_app/tools/check_mypy_watermark.py`.

Repo-root resolution independent of cwd (`:20-23`):

```python
# Resolve the repo root from this file's location so the gate behaves
# identically regardless of the caller's working directory (CR-WR-03).
# Layout: <repo>/tools/check_mypy_watermark.py -> repo root is two parents up.
REPO_ROOT = Path(__file__).resolve().parent.parent
```

Three-outcome discrimination — the gate-bypass guard the warning-count parser must copy
(`:43-73`):

```python
def count_mypy_errors() -> int:
    """Run mypy and return the error count.

    Distinguishes three outcomes so a broken type checker can never be mistaken
    for a clean tree (gate-bypass guard, CR-01):
      - a 'Found N errors' line     -> N  (mypy's errors-found path, exit 1)
      - exit 0 / 'Success'          -> 0  (genuinely clean tree)
      - anything else               -> mypy ran but crashed or changed its
                                       output; sys.exit(2) (tool/config error)
                                       rather than silently reporting 0 errors
                                       and passing the gate.
    """
    ...
    print(
        "ERROR: mypy did not report a parseable error count "
        f"(exit {result.returncode}). Treating as a tool/config failure, "
        "not a clean tree.\n" + output.strip(),
        file=sys.stderr,
    )
    sys.exit(2)
```

Watermark comparison with a three-way message (`:76-92`) — note the `INFO:` arm telling the
reader to lower the watermark. The BASE-06 native-env watermark (360) should mirror this:

```python
    watermark = get_watermark()
    count = count_mypy_errors()
    print(f"mypy errors: {count} (watermark: {watermark})")
    if count > watermark:
        print(
            f"FAIL: {count} errors exceeds watermark {watermark}. New errors introduced."
        )
        sys.exit(1)
    elif count < watermark:
        print(
            f"INFO: {count} errors — {watermark - count} below watermark. "
            "Lower watermark in pyproject.toml."
        )
    else:
        print("OK: error count at watermark.")
```

**Analog C — baseline JSON layout:** `/workspaces/firestarter_app/tools/baseline/dispatch_baseline.json:1-8`.
`{"meta": {...}, "<data>": [...]}`; the `note` field carries full provenance prose including
pinned upstream SHAs and what supersedes what:

```json
{
  "meta": {
    "generated_by": "check_dispatch.py inline capture",
    "chip_count": 746,
    "note": "Re-pinned Phase 86 ... Minipro infoic.xml pinned at SHA a8efaedc... Supersedes the Phase 66 Plan 04 capture (744 chips). ... Provenance-only capture (no test consumes this file); chip_database.baseline.json is the load-bearing diff_db gate."
  },
  "chips": [ ... ]
}
```

Note the last clause: the `note` states explicitly **whether anything consumes the file**.
D-03's meta block (tree SHA, pio 6.1.19, atmelavr 5.2.0, avr-gcc 7.3.0, ROADMAP cross-check
5/5) goes here, and the BASE-01 JSON is load-bearing — say so.

---

### `tests/test_check_*.py` (paired planted-fixture tests, all three repos)

**Analog:** `.planning/phases/122-…/test_check_permitted_claims.py` (204 lines, 7 tests) —
the canonical shape. Secondary: `firestarter_app/tests/test_check_no_log_in_sdp_window.py`.

**Module docstring: coverage enumeration + the never-import contract** (`:1-27`):

```
This is the MANDATORY anti-hollow pairing for the claim gate (GATE-01): a
checker with no negative-fixture test is exactly this project's v1.12
hollow-GATE-03 failure mode -- a declared-empty detector that could never
fail because nothing concrete was asserted against it. Every planted-
violation test below invokes the checker as a real subprocess against a
committed fixture file via the FIRESTARTER_CLAIMSCAN_TARGETS env seam --
never an in-process import -- so a passing test suite proves the checker
itself (not the test) fails the build on a real violation. The scanner is
never imported directly in this module.

Coverage:
  1. Clean-pass baseline via the seam ...
  2. Planted forbidden-phrase violation ...
  ...
  7. Positional argv overrides the env seam (documented precedence, pinned
     against a future silent inversion).
```

**The subprocess runner — a LIST, never `shell=True`** (`:34-57`). Copy verbatim; the
`targets is None` branch is what reaches the "variable genuinely absent" path:

```python
_HERE = Path(__file__).parent
_SCANNER = _HERE / "check_permitted_claims.py"


def _run_scanner(targets=None, argv=None):
    """Invoke the scanner as a real subprocess.

    `targets`, when not None, sets FIRESTARTER_CLAIMSCAN_TARGETS to that
    exact string (so the empty string is reachable, per test 5) -- when
    None, the env var is left absent from the child's environment entirely,
    reaching the "variable absent -> use real defaults" path.
    """
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )
```

Host-repo variant, for a checker invoked by relative path from the app root
(`test_check_no_log_in_sdp_window.py:80-91`):

```python
_FA_DIR = Path(__file__).parent.parent

def _run_checker(
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, "tools/check_no_log_in_sdp_window.py"],
        cwd=str(_FA_DIR),
        capture_output=True,
        text=True,
        env=env,
    )
```

**Assert BOTH a non-zero exit AND a distinctive failure substring** (`:83-97`) — the exit
code alone is the false-green trap:

```python
def test_planted_forbidden_phrase_flips_checker_to_failure():
    """The committed planted_forbidden_claim.md fixture MUST fail the gate,
    attributed to the should-now-work label -- the real C-5/D-14 near-miss
    wording ('AT28C parts should now work')."""
    result = _run_scanner(targets="fixtures/planted_forbidden_claim.md")
    assert result.returncode != 0, (
        f"scanner exited 0 on a planted forbidden-phrase violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, (
        f"Expected 'FAIL:' in output but got:\n{result.stdout}"
    )
    assert "should-now-work" in result.stdout, (
        f"Expected the should-now-work label in output but got:\n{result.stdout}"
    )
```

**Never-vacuous test — asserts the specific message, not just non-zero** (`:143-158`). The
docstring explains why a coincidental-failure mode is isolated; BASE-07's v1.23 copy is in
exactly the same position (default targets do not exist yet):

```python
def test_never_vacuous_on_explicitly_empty_target_list():
    """FIRESTARTER_CLAIMSCAN_TARGETS explicitly set to the empty string MUST
    resolve to zero targets and exit non-zero -- and must NOT silently fall
    back to the real default targets (which do not exist yet at this wave,
    so a fall-back would ALSO exit 1, but for the wrong reason and without
    a PASS:; this test asserts the never-vacuous message specifically,
    isolating the correct failure mode from that coincidental one)."""
    result = _run_scanner(targets="")
    assert result.returncode != 0, (...)
    assert "PASS:" not in result.stdout
    assert "no scan targets resolved" in result.stdout, (...)
```

**Anti-skip test — PASS line names every file** (`:166-182`) and **precedence pin**
(`:190-203`) — both are directly reusable for BASE-04's multi-target list and BASE-07.

**Derive expected line numbers from the fixture at test time, never hardcode**
(`test_check_no_log_in_sdp_window.py:93-103`) — relevant to the BASE-06 warning fixture:

```python
def _line_number_of_marker(text: str, marker: str) -> int:
    """Return the 1-indexed line number of the first line containing
    `marker` in `text`, or raise if not found. Used to derive the expected
    planted-violation line number directly from a fixture/temp source at
    test time, rather than hardcoding a second literal that a future
    re-plant could silently desync from."""
    for i, line in enumerate(text.splitlines(), start=1):
        if marker in line:
            return i
    raise AssertionError(f"marker {marker!r} not found in source text")
```

---

### Firmware-repo test modules — `firestarter/tests/test_*.py`

**Analog:** `/workspaces/firestarter/tests/test_update_version.py` — the **only** existing
pytest in the firmware repo. Every new firmware-repo test module mirrors it.

**Licence/provenance header + requirement/decision trace** (`:1-21`):

```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 15 Plan 01 — Wave 0 RED-gate scaffold for firestarter/update_version.py.

Requirements: VER-02
Decisions covered: D-04, D-05, D-06, D-07, D-08, D-09, D-12, D-13, D-17, D-21, D-24, D-25
...
"""
```

**Self-contained `sys.path` injection — the no-conftest house rule** (`:23-32`). This is the
single most important line for the planner; it is a *recorded pattern decision*, not an
omission:

```python
import sys
import subprocess
from pathlib import Path

# Self-contained sys.path injection — NOT in conftest.py per 15-PATTERNS.md Critical Note 4.
# Firmware sub-repo has the script at .github/scripts/update_version.py — same layout as app.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".github" / "scripts"))
import update_version  # noqa: E402

import pytest
```

New firmware-repo tests invoke `scripts/check_*.py` as a **subprocess** (per the v1.22 shape),
so most will not need the `sys.path` injection at all — but if any helper is imported, it must
do its own resolution here and **must not** add a `conftest.py`.

**Committed golden inputs resolved relative to the test file** (`:68-73`):

```python
        golden_dir = Path(__file__).resolve().parent / "golden"
        baseline = golden_dir / "stable-baseline.h"
        expected = golden_dir / "stable-expected.h"

        version_file = tmp_path / "version.h"
        version_file.write_bytes(baseline.read_bytes())
```

`firestarter/tests/fixtures/` should sit beside the existing `golden/` using this same
`Path(__file__).resolve().parent / "<dir>"` idiom.

**Assertion message style** (`:85-89`) — every assert carries a message printing got-vs-expected:

```python
        assert version_file.read_bytes() == expected.read_bytes(), (
            f"Stable path output did not match golden expected file.\n"
            f"Got:      {version_file.read_text()!r}\n"
            f"Expected: {expected.read_text()!r}"
        )
```

Also present and reusable: `@pytest.fixture(autouse=True) def _isolate_env(self, monkeypatch)`
clearing CI env vars (`:46-56`), and class-grouped tests (`class TestUpdateVersionStable:`).

> **⚠ Cross-repo copy hazard (name each in the plan).** `firestarter/tests/` has **no**
> `conftest.py`, `pytest.ini`, `pyproject.toml` or `setup.cfg` anywhere in the repo, and CI
> installs **bare `pytest` only** — no ruff, no mypy, no `pytest-mock`, no `syrupy`.
> `firestarter_app/tests/conftest.py` exists (153 lines) and that repo runs
> `ruff check` + `ruff format --check` + a mypy watermark. A host test module copied into
> `firestarter/tests/` unmodified will break on a missing fixture or a non-stdlib import; a
> firmware test copied into `firestarter_app/tests/` will fail the lint gate. Do **not**
> cross-copy blindly.

---

### The 7 proxy-carrying host modules — exact current code to replace (D-09, BASE-02)

Verbatim per-module absence proxies and one representative `skipif` each. Each of these is a
**module-level** constant evaluated at import time — `monkeypatch.setenv` cannot affect it
(RESEARCH Correction C-15), which is why the replacement's paired tests must run pytest or the
checker as a subprocess.

**1. `tests/test_revision_constants_parity.py`** (8 decorator legs)
```python
:135  FIRMWARE_HEADER = (
:138  FW_ABSENT = not FIRMWARE_HEADER.exists()
...
:551  @pytest.mark.skipif(FW_ABSENT, reason="firestarter firmware checkout absent")
```
Also carries a docstring block at `:90-95` naming the "known, explained, residual gap (D-13)"
of the host-only-CI skip — this prose is what BASE-02 supersedes and should be updated, not
just deleted.

**2. `tests/test_dispatch_mirror.py`** (2 legs) — **compound, two scan paths behind one flag**:
```python
:31  _FA_DIR = pathlib.Path(__file__).parent.parent
:34  _PROTOCOLS_MD = _FA_DIR.parent / "firestarter" / "doc" / "PROTOCOLS.md"
:37  _FW_DISPATCH_TEST = (
:50  # Mirrors the FW_ABSENT idiom in test_revision_constants_parity.py and the
:52  FW_ABSENT = not (_PROTOCOLS_MD.exists() and _FW_DISPATCH_TEST.exists())
...
:156 @pytest.mark.skipif(FW_ABSENT, reason="firestarter firmware checkout absent")
```
Rekeying this module moves **two** paths into the D-11 inventory.

**3. `tests/test_sdp_bus_config_drift.py`** (3 legs) — the `_requires_fw_header` alias form:
```python
:22  _APP_DIR = _REPO_ROOT / "firestarter_app"
:24  _REAL_PINOUTS = _APP_DIR / "firestarter" / "data" / "pinouts.json"   # NOT cross-repo
:25  _COMMITTED_HEADER = (
:42  _FW_HEADER_ABSENT = not _COMMITTED_HEADER.exists()
:43  _requires_fw_header = pytest.mark.skipif(
:44      _FW_HEADER_ABSENT,
:45      reason=...,
:46  )
:49  @_requires_fw_header
```
⚠ `_REAL_PINOUTS` (:24) is **same-repo** — the Python package dir shares the name with the
sibling repo. It must not be pulled into the cross-repo inventory. `_FA_DIR.parent / "firestarter"`
= the sibling **repo**; `_APP_DIR / "firestarter"` = the **package**. Both appear here, 4 lines apart.

**4. `tests/test_check_no_log_in_sdp_window.py`** (1 leg) — the fullest comment block, and the
best template for the shared helper's docstring:
```python
:61  _FA_DIR = Path(__file__).parent.parent
:62  _FIXTURE = _FA_DIR / "tests" / "fixtures" / "planted_log_in_window.cpp"
:63  _EEPROM_28C_CPP = _FA_DIR.parent / "firestarter" / "src" / "proms" / "eeprom_28c.cpp"

# The firmware sub-repo may be absent in standalone CI (firestarter_app
# checked out alone -- beta-release.yml has no sibling firestarter checkout).
# Mirrors the FW_ABSENT skip pattern in test_sdp_table_parity.py /
# test_revision_constants_parity.py / test_gen_validation_header.py. Only
# the clean-source control below touches the real firmware file; every
# other case in this module drives a fixture or temp file via
# FIRESTARTER_SDP_SRC and needs no firmware checkout.
:72  _FW_ABSENT = not _EEPROM_28C_CPP.exists()
:73  _requires_fw = pytest.mark.skipif(
:74      _FW_ABSENT,
:75      reason="firestarter firmware checkout absent (eeprom_28c.cpp)",
:76  )
:109 @_requires_fw
```

**5. `tests/test_sdp_table_parity.py`** (3 legs **+ 1 inline guard**):
```python
:49  _FLASH_UTILS_H = _REPO_ROOT / "firestarter" / "include" / "flash_utils.h"
:54  _FW_ABSENT = not _EEPROM_28C_CPP.exists()
:55  _requires_fw = pytest.mark.skipif(
:171 @_requires_fw
...
:299     if _FW_ABSENT:            # <-- BARE INLINE GUARD, invisible to a decorator grep
```
A rekey pass that only rewrites decorators leaves `:299` behind. This is also precisely the
shape D-09's recurrence lint must catch.

**6. `tests/test_check_is_memory_cmd_no_ifdef.py`** (1 leg):
```python
:55  _FIXTURE = _FA_DIR / "tests" / "fixtures" / "planted_ifdef_in_predicate.h"
:56  _FIRESTARTER_H = _FA_DIR.parent / "firestarter" / "include" / "firestarter.h"
:65  _FW_ABSENT = not _FIRESTARTER_H.exists()
:66  _requires_fw = pytest.mark.skipif(
:102 @_requires_fw
```

**7. `tests/test_gen_validation_header.py`** (6 legs — the module absent from v1.22's
eleven-row gate table):
```python
:22  _COMMITTED_HEADER = (
:37  _FW_HEADER_ABSENT = not _COMMITTED_HEADER.exists()
:38  _requires_fw_header = pytest.mark.skipif(
:44 / :53 / :62 / :70 / :89 / :177   @_requires_fw_header
```

**Measured totals:** 24 decorator legs + 1 inline guard, 49 collected tests, 0 skipped with the
sibling present. Three distinct constant names (`FW_ABSENT`, `_FW_ABSENT`, `_FW_HEADER_ABSENT`)
and at least three distinct reason strings — RESEARCH recommends normalising all seven to one
shared marker so D-10's allow-list has one firmware-absent entry, not five near-duplicates.

---

### Meta-repo `check_permitted_claims.py` (v1.23)

**Analog:** `.planning/phases/122-…/check_permitted_claims.py` — copy near-verbatim. Only these
change per RESEARCH: `_DEFAULT_TARGETS` (v1.23 closing artifacts, all-or-nothing arming per
D-15), `FORBIDDEN_PATTERNS` (the 8-row v1.23 table), `REQUIRED_CAVEAT_*`
(`"no PY32F071 hardware exists"`), and D-16 proximity scoping.

Phrase-table shape to preserve (`:70-103`) — labelled tuples, all `re.IGNORECASE`, with a
comment recording which entries are deliberately **narrowed** and which are deliberately
**broad**, and why:

```python
# Eight forbidden-phrase labels/patterns, all case-insensitive.
# ... this table is a closed set distilled from it, not a verbatim copy. Two entries
# (`works-on-silicon`, `proven-on-silicon`) are deliberately NARROWED to a
# silicon/AT28C object so the gate stays a real signal instead of firing on
# unrelated prose such as "works on the merged tree"; `now-works` is kept
# broad on purpose because C-5's actual near-miss ("AT28C parts should now
# work") had no object qualifier to anchor on.
FORBIDDEN_PATTERNS = [
    ("verified-fixed", re.compile(r"verified\s+fixed", re.IGNORECASE)),
    ("silicon-verified", re.compile(r"silicon[-\s]verified", re.IGNORECASE)),
    ...
]
```

Required-caveat block **plus the recorded interaction comment** (`:105-115`) — D-16 sharpens
this, but the comment must survive:

```python
# Canonical required-caveat sentence fragment, and its whitespace-tolerant
# regex. Deliberate interaction, recorded here rather than "fixed" by
# weakening the pattern set above: an honest negated phrasing such as
# "nothing is silicon-verified here" WILL trip the `silicon-verified`
# forbidden pattern. The correct response when that happens is to reword the
# artifact to use the canonical caveat sentence below, not to narrow
# FORBIDDEN_PATTERNS to dodge the false alarm.
REQUIRED_CAVEAT_PROSE = "no AT28C silicon was tested"
REQUIRED_CAVEAT_PATTERN = re.compile(
    r"no\s+AT28C\s+silicon\s+was\s+tested", re.IGNORECASE
)
```

Pure scan function returning a tuple, separate from I/O (`:118-133`) — keep this split; D-16's
proximity window is a change to `scan_text` only, and it is the unit the fixtures exercise:

```python
def scan_text(text):
    """Scan `text` for forbidden-phrase matches and required-caveat presence.
    Returns (forbidden_hits, caveat_present): ...
    """
    forbidden_hits = []
    for label, pattern in FORBIDDEN_PATTERNS:
        for m in pattern.finditer(text):
            forbidden_hits.append((label, m.group(0)))
    caveat_present = bool(REQUIRED_CAVEAT_PATTERN.search(text))
    return forbidden_hits, caveat_present
```

---

## Shared Patterns

### Coarse-key arming (D-07, D-15)
**Source:** the idiom exists only as prose + the 7 modules' `.git`-adjacent proxies; RESEARCH
supplies the generalised shape (§Architecture Patterns, Pattern 3).
**Apply to:** BASE-04, BASE-05 (`platform/py32f071/` dir), BASE-07 (all-or-nothing over named
targets), the shared FW-presence helper (`../firestarter/.git`).

```python
ARMED = (FW_ROOT / "platform" / "py32f071").is_dir()
if not ARMED:
    print("UNARMED: platform/py32f071/ absent -- this gate arms when Phase 124 lands the port.")
    return 0
missing = [p for p in fine_grained_targets if not p.exists()]
if missing:
    print(f"FAIL: armed but {len(missing)} target(s) unresolvable: {missing}")
    return 1          # a rename inside the port CANNOT disarm this gate
```

The closest *committed* precedent for the "missing fine-grained target ⇒ hard failure, naming
the fix" half is `check_no_log_in_sdp_window.py:308-315` (quoted above).

### Three-way exit taxonomy
**Source:** `firestarter/scripts/check_uno_ram.sh:14-17`; `firestarter_app/tools/check_mypy_watermark.py:8-13`.
**Apply to:** every new checker.
```
  0 — pass
  1 — real violation
  2 — tool/config/parse error (a broken tool must never look like a clean tree)
```
Note `check_no_log_in_sdp_window.py` and `check_permitted_claims.py` use a **two-way** taxonomy
(0/1) with `ERROR:`-to-stderr folded into exit 1. Both are house idioms; RESEARCH recommends the
three-way form for the parsing gates (BASE-01, BASE-06) and either for the text scanners.

### Fixture placement discipline
**Source:** `check_permitted_claims.py:41-49` (the comment quoted above) and the observed layout.
**Apply to:** all three new fixture directories.

| Checker | Fixture location | Reachable from default targets? |
|---------|------------------|---------------------------------|
| `.planning/phases/122-…/check_permitted_claims.py` | `.planning/phases/122-…/fixtures/` (sibling dir, `_HERE/fixtures/`) | **No** — `_DEFAULT_TARGETS` is 5 explicit `_HERE/122-*.md` paths, never a glob |
| `firestarter_app/tools/check_no_log_in_sdp_window.py` | `firestarter_app/tests/fixtures/planted_log_in_window.cpp` | **No** — the default is a single hardcoded `../firestarter/src/proms/eeprom_28c.cpp` |
| `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` | `firestarter_app/tests/fixtures/planted_ifdef_in_predicate.h` | **No** — same shape |

Existing planted fixtures (7, all in `firestarter_app/tests/fixtures/`):
`planted_constants_fw_missing.h`, `planted_constants_host_missing.h`,
`planted_constants_value_drift.h`, `planted_ifdef_in_predicate.h`, `planted_log_in_window.cpp`,
`planted_permit_by_default.py`, `planted_widenable_allowset.py`. The last two are **Python**
fixtures — the closest precedent for D-09's recurrence-lint fixture.

Naming convention actually observed: `planted_<what-is-wrong>.<ext>`, and clean controls are
named `clean_*` (meta repo: `clean_control.md`, `clean_control_second.md`).

### Firmware-repo test constraints (apply to every new `firestarter/tests/*.py`)
- No `conftest.py` / `pytest.ini` / `pyproject.toml` — **house rule**, recorded at
  `firestarter/tests/test_update_version.py:27`.
- Stdlib + `pytest` only (CI runs bare `pip install pytest`).
- No lint/format/type gate in the firmware repo — match `test_update_version.py`'s style by hand.
- `firestarter/tests/` is PIO-invisible (PlatformIO globs `test/`, not `tests/`), so a `.cpp`
  fixture under `tests/fixtures/` cannot reach any build.
- Current contents: `__init__.py` (the dir **is** a package), `golden/`, `test_update_version.py`.
  `firestarter/scripts/` contains exactly one file, `check_uno_ram.sh`.

---

## No Analog Found

Files with no close match in either sub-repo or the meta repo. Use RESEARCH.md's prescribed
mechanism rather than inventing an analog.

| File | Role | Data Flow | Reason / where to get the mechanism |
|------|------|-----------|--------------------------------------|
| `firestarter_app/tests/fixtures/fake_firestarter/` (D-12) | fixture (committed tree) | file-I/O | No committed fake-sibling tree exists anywhere in the project. Every existing fixture is a single file. RESEARCH §D-12 "Mechanism 1" supplies the working shape (commit the tree **without** the marker; `shutil.copytree` into `tmp_path` and `(fake / ".git").write_text("gitdir: /nonexistent\n")` at test time). **Do not** follow CONTEXT D-12's suggested `.git` gitfile — measured: `git add` exits 0 and stages nothing. |
| `firestarter/tests/fixtures/planted_macro_redef.cpp` (D-14) | fixture compiled at test time | transform | No test in either repo shells out to a compiler. Mechanism per RESEARCH: `shutil.which(os.environ.get("CXX", "g++"))`, assert not None (**fail, never skip**), compile, feed stdout to the gate's own parser. Anchor the parser on the diagnostic tail `warning:\s*"(?P<macro>[^"]+)"\s+redefined` — never on `:line:col:` (gcc 7.3 emits `:2:0:`, gcc 14 emits `:2:9:`). |
| `firestarter/tests/test_checker_convention.py` (BASE-08 meta-test) | test | file-I/O glob + floor | No meta-test over the checker set exists. Nearest conceptual kin is `tools/audit_coverage_matrix.py` (a coverage ledger), but its shape does not transfer. Note RESEARCH C-6: the convention holds for only **4 of 7** host checkers, so this must be scoped to `firestarter/scripts/check_*.py` (today: zero Python checkers) with a hardcoded floor. |
| `firestarter_app/tests/test_skip_census.py` (BASE-03/D-10) | test | event-driven | Nothing in either suite inspects pytest's own skip report. Needs a subprocess `pytest -rs` run (or a report hook) plus a committed allow-list of reason strings. Note D-10 explicitly forbids a pinned skip count. |
| `firestarter_app/tests/scan_paths.py` (D-11 inventory) | config | batch | No central path inventory exists — the current state is exactly the seven-way duplication D-11 removes. The nearest shape is `check_permitted_claims.py`'s `_DEFAULT_TARGETS` (explicit, non-pattern) + its missing-target fail-closed guard, applied to a union of population A (6 test-module paths) and population B (11 `tools/*.py` resolvers listed in RESEARCH §"The complete cross-repo scan-path inventory"). |

---

## Metadata

**Analog search scope:**
`/workspaces/firestarter/{scripts,tests}/`,
`/workspaces/firestarter_app/{tools,tests,tests/fixtures}/`,
`/workspaces/.planning/phases/122-close-honesty-ledger-community-ask-release-decision/`

**Files scanned:** 8 read in full, ~25 enumerated/grepped
**Pattern extraction date:** 2026-07-30
