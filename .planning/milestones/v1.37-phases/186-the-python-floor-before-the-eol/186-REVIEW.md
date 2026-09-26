---
phase: 186-the-python-floor-before-the-eol
reviewed: 2026-09-12T08:35:18Z
depth: standard
files_reviewed: 19
files_reviewed_list:
  - firestarter_app/pyproject.toml
  - firestarter_app/firestarter/main.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/address_parser.py
  - firestarter_app/firestarter/codec.py
  - firestarter_app/firestarter/config.py
  - firestarter_app/firestarter/diagnostic_report.py
  - firestarter_app/firestarter/eprom_info.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/firmware.py
  - firestarter_app/firestarter/hardware.py
  - firestarter_app/firestarter/ic_layout.py
  - firestarter_app/firestarter/jp5_gate.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/tests/test_python_floor_agreement.py
  - firestarter_app/tests/test_cap03_ack_layout_parity.py
  - firestarter_app/tests/test_dev_gate_reads_no_firmware_source.py
  - firestarter_app/tests/test_py32_packaging.py
  - firestarter_app/tests/test_runtime_dependencies.py
  - firestarter_app/.planning/codebase/STACK.md
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 186: Code Review Report

**Reviewed:** 2026-09-12T08:35:18Z
**Depth:** standard
**Files Reviewed:** 19 (submodule `firestarter_app`, diffed `bffbba8..HEAD`)
**Status:** issues_found

## Summary

This phase raises `firestarter_app`'s advertised Python floor from a disagreeing 3.9/3.10/3.11 mix
to a single 3.11 everywhere (`requires-python`, ruff `target-version`, mypy `python_version`, CI
`python-version:` pins), absorbs the resulting `ruff --fix` type-annotation sweep
(`Optional[X]` → `X | None`, `Dict`/`List`/`Tuple` deprecation noqa cleanup, one `UP017`
`datetime.timezone.utc` → `datetime.UTC` rewrite), repairs one regex-based parity test that pinned
the old `Optional[LogMessage]` spelling, and installs a new four-way floor-agreement gate
(`test_python_floor_agreement.py`).

I verified the mechanical claims directly rather than trusting them: `ruff check firestarter/
tests/` is clean, all five touched/added test files pass, the `# noqa: UP036` on `main.py`'s version
guard is genuinely load-bearing (confirmed with `ruff check --fix --unsafe-fixes`: without the
noqa, UP036 deletes the entire guard block as "outdated"), and the new floor-agreement test's three
`.github/workflows/*.yml` pins are exactly the plain-scalar `python-version: '3.11'` shape its regex
expects.

The one substantive finding is that `main.py`'s runtime version guard — the human-facing half of
"raise the floor to 3.11" — does not actually fire in either of the two ways a user reaches this
code: the packaged `firestarter` console-script entry point calls `main()` directly and never
executes the `if __name__ == "__main__":` block the guard lives in, and even a direct `python
main.py` invocation on Python 3.9 crashes with an unrelated `TypeError` while *importing*
`cli_handlers.py` (and its own transitive imports), before ever reaching the guard, because the
sweep this phase absorbed spread runtime-evaluated `X | None` annotations (PEP 604, needs 3.10+)
across every touched module with no `from __future__ import annotations` to defer them. This is
substantially de-risked by the project's own `.planning/notes/python-floor-decision.md` §2, which
already establishes that `pip install firestarter` on 3.9/3.10 mostly never fetches this release at
all — but the guard itself, as written, is dead code for the scenarios it was written to catch, and
nothing in this phase's new test coverage would catch that regressing further.

Two smaller info-level items round this out: the new floor-agreement test's CI-pin regex is a
plain-scalar line match that would silently see zero pins from a future GitHub Actions matrix-style
`python-version: ['3.9', '3.11']`, and `serial_comm.py` retains one quoted-forward-ref
`Optional["SerialCommunicator"]` the sweep didn't touch, leaving one inconsistent spelling next to
177 converted ones in the reviewed file set.

## Warnings

### WR-01: `main.py`'s runtime version guard cannot fire via the packaged entry point

**File:** `firestarter_app/firestarter/main.py:29-34`
**Issue:** The guard is nested inside `if __name__ == "__main__":`. `pyproject.toml`'s
`[project.scripts]` entry (`firestarter = "firestarter.main:main"`, unchanged by this phase) is
resolved by pip/setuptools into a generated console-script wrapper that imports `firestarter.main`
and calls `main()` (i.e. `cli()`) directly — it never executes `firestarter/main.py` as `__main__`.
Every user who installs via `pip install firestarter` and runs the `firestarter` command — which is
effectively all of them — never reaches this check at all, regardless of their interpreter version.
This predates this phase (the block had the same shape at `< (3, 9)` before), but this phase is
exactly the one that re-asserted the guard's message and number (`176c22d`) without noticing the
guard itself is unreachable from the primary invocation path, and the new `test_python_floor_agreement.py`
gate (which this phase adds specifically to prevent floor-statement drift) does not exercise
`main.py` at all — it only reads `pyproject.toml` and workflow YAML.
**Fix:** Move the check out of the `__name__ == "__main__"` guard so it runs unconditionally when
`main.py` is imported (or call it as the first statement inside `main()`/`cli()`), so the packaged
entry point exercises the same check a direct script invocation does:
```python
if sys.version_info < (3, 11):  # noqa: UP036
    sys.exit(
        "Error: Firestarter requires Python 3.11 or higher. "
        "Please update your Python version."
    )

main = cli


def exit_gracefully(signum: int, frame: FrameType | None) -> None:
    """Signal handler that exits the process with status 1."""
    sys.exit(1)
```

### WR-02: Even by direct script invocation, the guard is preempted by an unrelated `TypeError` on Python 3.9/pre-3.10

**File:** `firestarter_app/firestarter/main.py:14, 29-34` (root cause spans every file in this
phase's sweep: `cli_handlers.py`, `serial_comm.py`, `hardware.py`, `firmware.py`,
`eprom_operations.py`, `ic_layout.py`, `eprom_info.py`, `codec.py`, `config.py`,
`address_parser.py`, `jp5_gate.py`)
**Issue:** `main.py` does `from firestarter.cli_handlers import cli` at module scope, before the
`if __name__ == "__main__":` block runs. This phase's absorbed sweep (`1ebc548`) rewrote
`Optional[X]` to the PEP 604 `X | None` spelling throughout these modules, none of which declare
`from __future__ import annotations`. Function/method parameter and return annotations (and
class-body / local variable annotations, e.g. `cli_handlers.py:1814`'s
`_load_validation_spec() -> dict[str, Any]`, or `hardware.py`'s `NamedTuple` fields) are evaluated
eagerly at class/def time without that future import. `X | None` requires `type.__or__`, added in
Python 3.10 — on Python 3.9 the mere `import firestarter.cli_handlers` (transitively pulled in by
`main.py`'s own top-level import, ahead of the guard) raises `TypeError: unsupported operand
type(s) for |: 'type' and 'NoneType'` before the guard code ever executes. The one intended
consumer of this guard (`python main.py` run directly) therefore only actually works on exactly
Python 3.10 (where `X | None` evaluates fine and `sys.version_info < (3, 11)` still correctly
refuses) — not on 3.9, which is the version the friendly message exists to catch gracefully.
Real-world exposure is narrowed by `.planning/notes/python-floor-decision.md` §2 (a bare `pip
install firestarter` on 3.9/3.10 mostly never resolves to this release at all), but any git-checkout
or vendored-source user on 3.9 gets a confusing internal traceback instead of the intended message,
and this is a direct, demonstrable consequence of this phase's own sweep spreading unguarded PEP 604
syntax into every reviewed module.
**Fix:** Either add `from __future__ import annotations` to the affected modules (making the
annotations lazy strings, sidestepping the eager-evaluation crash and letting the guard in main.py
actually be the first thing to fail loudly), or accept that the guard is now purely a courtesy for
interpreters that manage to import the package at all (3.10) and document that scope explicitly
rather than leaving it implied. Combining this with WR-01's fix is the more complete remedy.

### WR-03: New floor-agreement test's CI-pin scan is a plain-scalar line match, not a YAML parse — a future matrix-style pin is silently invisible

**File:** `firestarter_app/tests/test_python_floor_agreement.py:41-43, 131-164`
**Issue:** `_PYTHON_VERSION_RE` only matches a bare `python-version: 'X.Y'` (or unquoted) scalar
occupying the whole line. This is a deliberate, documented trade-off (avoiding a YAML dependency),
and today's three pins (`ci.yml` x2, `beta-release.yml` x1) are all in exactly that shape, so the
test is not currently vacuous. But if a future workflow change switches to GitHub Actions' matrix
form (`python-version: ['3.9', '3.11']`) to test multiple interpreters, that line contributes zero
matches to `pins`, silently understating the inventory rather than failing — and because
`_WORKFLOW_PIN_FLOOR` is a floor (`>= 3`), not an exact count, the existing three plain-scalar pins
are enough to keep the assertion passing even while a brand-new matrix-based pin drifts off the
floor completely unchecked. This is exactly the "claim-shaped defect" pattern the test's own
docstrings warn about elsewhere (`check_permitted_claims.py`-style silent under-scan), just at one
remove: the directory-non-vacuity check passes, but a specific *line's* format silently produces no
signal.
**Fix:** At minimum, add a second regex (or a lightweight scan) that also matches a
`python-version:` line followed by a bracketed list, and either parse each element or fail loudly
with an actionable message ("matrix-style python-version pin not understood by this gate") rather
than silently contributing zero pins.

## Info

### IN-01: One quoted forward-reference `Optional[...]` left inconsistent with the rest of the sweep

**File:** `firestarter_app/firestarter/serial_comm.py:816`
**Issue:** `_probe_port(...) -> Optional["SerialCommunicator"]:` was not rewritten to
`"SerialCommunicator" | None` by the sweep (ruff's `UP007`/`UP045` genuinely do not flag this quoted
forward-reference form — confirmed with `ruff check --select UP006,UP007,UP035,UP045`), so
`typing.Optional` remains imported and used at exactly one site in an otherwise fully-converted
file. Harmless at runtime, but it is the one remaining spelling inconsistency in the reviewed set
after a phase whose stated purpose was spelling uniformity.
**Fix:** `-> "SerialCommunicator | None":` (or drop the quotes if `SerialCommunicator` is already
defined above this point in the file) for consistency; low priority, no functional effect.

### IN-02: `datetime.UTC` sweep is correctly gated by the new floor, but only because the crash happens earlier

**File:** `firestarter_app/firestarter/cli_handlers.py:1888`, `firestarter_app/firestarter/diagnostic_report.py:735`
**Issue:** Both `datetime.now(datetime.UTC)` call sites are 3.11+-only (added in 3.11; `diagnostic_report.py`
does declare `from __future__ import annotations`, so its own annotations are safe, but that doesn't
protect the `datetime.UTC` *expression*, which is evaluated at call time regardless). On an
interpreter that manages to import the package at all (i.e., exactly 3.10, per WR-02), reaching
either call site — `dev validate-family`'s artifact writer or `DiagnosticReport._utc_now()` — would
raise `AttributeError: module 'datetime' has no attribute 'UTC'` at runtime. This is not a new
defect distinct from WR-02 (the same 3.10 window is already exposed by `X | None` syntax working
while the floor is nominally 3.11), but it's worth naming as a second, independent way the same
narrow 3.10 gap surfaces, since it strikes at runtime in a command handler rather than at import
time.
**Fix:** Covered by the same fix as WR-01/WR-02 (make the guard actually reachable); no separate
action needed if those are addressed.

---

_Reviewed: 2026-09-12T08:35:18Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
