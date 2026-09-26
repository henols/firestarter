# Phase 113: Submission Flow - Pattern Map

**Mapped:** 2026-07-03
**Files analyzed:** 5 (1 new module, 3 edits, 1 checker extension) + 3 test files
**Analogs found:** 5 / 5

> All implementation lives in the **`firestarter_app/` submodule** (Python host CLI).
> Paths below are relative to `firestarter_app/` unless absolute. RESEARCH.md §Sources
> carries the exhaustive `file:line` index; this map extracts the load-bearing excerpts.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/submit.py` (NEW) | service/utility (submission) | request-response (shell-out + browser hand-off) | `firestarter/avr_tool.py` (subprocess/which) + `firestarter/firmware.py` (Confirm) | role-match (composite) |
| `firestarter/cli_handlers.py` (EDIT — `--submit` flag + call site in `dev_test`) | controller (Click handler) | request-response | the existing `dev_test` handler + `--destructive`/`-y` flags in the SAME function (`:1753-1905`) | exact (same function) |
| `firestarter/diagnostic_report.py` (EDIT — `dedup_fingerprint` helper + `to_dict()` field) | model (report) | transform | `is_submittable`/`build_db_diff` module-level helpers + `_step_dict`/`to_dict` in the SAME file | exact (same file) |
| `tools/check_devtest_orchestrator.py` (EDIT — add `submit.py` scan leg) | config/tooling (AST gate) | batch scan | the existing dual-target `main()` (`:321-396`) | exact (same file) |
| `tests/test_submit.py` (NEW) | test | request-response | `tests/test_dev_test_cmd.py` (`make_app_context` + `Mock(spec=)` + `_is_interactive` patch) | role-match |
| `tests/test_dev_test_cmd.py` (EDIT — `--submit` end-to-end) | test | request-response | itself | exact |
| `tests/test_diagnostic_report.py` (EDIT — dedup determinism) | test | transform | itself | exact |

## Pattern Assignments

### `firestarter/submit.py` (NEW — service/utility, request-response)

Composite of three analogs. Recommended structure is in RESEARCH.md §Recommended Module
Structure — build small seam-injected functions with real defaults.

**Analog A — `shutil.which` + `subprocess` primitives** (`firestarter/avr_tool.py:9-15`):
```python
import logging
import os
import re
import time
from pathlib import Path
from shutil import which
from subprocess import PIPE, CalledProcessError, Popen, TimeoutExpired  # noqa: F401
```
Copy the `from shutil import which` + `subprocess`-import style. For submit, prefer
`subprocess.run(argv_list, input=body, text=True, capture_output=True, check=False)`
(RESEARCH §Pattern 2) over `Popen`. **argv is a LIST, never `shell=True`, never a dict**
(SAFE-03 + V5 command-injection control).

**Analog B — `Confirm.ask` preview-confirm** (`firestarter/firmware.py:20`):
```python
from rich.prompt import Confirm
```
Same import the `dev_test --destructive` gate already uses (`cli_handlers.py:1817`,
excerpt below). Inject as `confirm_fn=Confirm.ask` with a real default.

**Analog C — hardcoded `henols/...` GitHub owner constant** (`firestarter/constants.py:9-15`):
```python
FIRESTARTER_RELEASES_URL = "https://api.github.com/repos/henols/firestarter/releases"
```
Precedent for a hardcoded owner-repo constant. **D-01 target differs**: submit uses
`henols/firestarter_app` (host repo, NOT the firmware repo `henols/firestarter`).
Declare `SUBMIT_REPO = "henols/firestarter_app"` as a module constant — no cwd/remote
inference (RESEARCH §Anti-Patterns).

**Seam-injection signature** (mirror `_is_interactive` patch-ability + the deleted
`prompt_provenance(ask=, confirm=)` style):
```python
def submit_report(report, chip, saved_json_path, *,
                  which_fn=shutil.which, run_fn=subprocess.run,
                  browser_open=webbrowser.open, isatty_fn=None,
                  confirm_fn=Confirm.ask, console=None): ...
```

**gh tier argv** (RESEARCH §Code Examples — verified against gh manual):
```python
proc = run_fn(["gh", "issue", "create", "--repo", "henols/firestarter_app",
               "--label", "gsd-inbox", "--title", title, "--body-file", "-"],
              input=body, text=True, capture_output=True, check=False)
# returncode 0 -> proc.stdout.strip() is the created issue URL
```

**Oversize URL guard** (RESEARCH §Oversize Handling / §Code Examples): build encoded URL
via `urllib.parse.urlencode(params, quote_via=quote)`, measure `len(url.encode("utf-8"))`,
drop the fenced JSON past 7500 bytes, hard-stop before ~8000. Measure the ENCODED bytes,
not the raw body (Pitfall 3).

---

### `firestarter/cli_handlers.py` (EDIT — controller; wire `--submit` into `dev_test`)

**Analog: the SAME function.** Copy the flag + gate patterns already present.

**Flag pattern to copy** (`cli_handlers.py:1774-1780`, the `-y/--yes` option):
```python
@click.option(
    "-y", "--yes", "assume_yes",
    is_flag=True, default=False,
    help="Bypass the --destructive confirm prompt on a TTY.",
)
```
Add `--submit` as a sibling `is_flag=True, default=False` option; add `submit: bool` to
the `def dev_test(...)` signature (`:1786-1792`). Do NOT reuse `-y/--yes` for submission
(RESEARCH §Guardrails — `--yes` is scoped to the destructive chip-sacrifice prompt only).

**TTY-gated Confirm pattern to mirror** (`cli_handlers.py:1809-1822`):
```python
interactive = _is_interactive()
if interactive and destructive and not assume_yes:
    proceed = Confirm.ask(
        "--destructive will sacrifice the chip. Continue?", default=False
    )
    if not proceed:
        click.echo("Aborted -- chip left untouched.")
        sys.exit(0)
```
The `--submit` flow is the same shape (D-04): on TTY, preview → `Confirm.ask` → send;
off-TTY, print body + URL and return WITHOUT sending.

**Call site** (after persist `:1900`, before `sys.exit(code)` `:1902-1905`):
```python
console.print(f"[dim]Report written to {json_file}[/dim]")

if submit:
    from firestarter import submit as submit_mod
    submit_mod.submit_report(report, chip, json_file, console=console)
```
Pass the in-memory `report`, `chip`, and the already-resolved `json_file` path
(`:1884`). Do NOT re-run the sweep (RESEARCH §Anti-Patterns #1).

**`_is_interactive` seam to reuse** (`cli_handlers.py:1717-1724`) — tests patch this
function directly, NOT `sys.stdin.isatty`, because `CliRunner.invoke` swaps `sys.stdin`.

---

### `firestarter/diagnostic_report.py` (EDIT — model; add `dedup_fingerprint`)

**Analog: the SAME file's module-level helpers + `to_dict`.**

**Module-level helper pattern to copy** (`is_submittable`, `diagnostic_report.py:150-162`):
```python
def is_submittable(ac: AutoCapture) -> bool:
    return bool(ac.chip) and bool(ac.protocol) and bool(ac.host_version)
```
Add `dedup_fingerprint(report) -> str` as a sibling module-level function (RESEARCH
§Dedup Fingerprint impl — sha256 over `chip | protocol | ordered (op=verdict:cls)`,
`[:12]`). Inputs read from `AutoCapture` (`:92-93`) and `_step_dict` fields
(`op`/`verdict`/`fingerprint.classification`, `:323-332`). EXCLUDE volatile fields
(`generated` `:361`, `host_version`, `vpp_*/vpe_*` voltages).

**`to_dict()` single-source field-add** (`diagnostic_report.py:346-363`):
```python
return {
    "schema_version": SCHEMA_VERSION,
    "generated": self._utc_now(),
    "auto_capture": self._auto_capture_dict(),
    ...
    "is_submittable": is_submittable(self.auto_capture),
    "db_diff": self._db_diff_dict(),
}
```
Add `"dedup_fingerprint": dedup_fingerprint(self)` here so it lands in the JSON
automatically (single-source invariant — `render()` `:377` and `to_json_block()` `:443`
both consume `to_dict()`, so no second field list). `submit.py` reads it back via
`report.to_dict()["dedup_fingerprint"]` for the issue title.

---

### `tools/check_devtest_orchestrator.py` (EDIT — add `submit.py` full-scan leg)

**Analog: the SAME file's dual-target `main()` (`:321-396`) + env-override constants
(`:84-97`).**

**Env-override constant pattern to copy** (`:84`, `:96-97`):
```python
FIRESTARTER_DEVTEST_SRC = os.environ.get("FIRESTARTER_DEVTEST_SRC", _DEFAULT_CHIP_TEST)
FIRESTARTER_DEVTEST_HANDLER = os.environ.get(
    "FIRESTARTER_DEVTEST_HANDLER", _DEFAULT_DEVTEST_HANDLER
)
```
Add a third `FIRESTARTER_DEVTEST_SUBMIT` (default `firestarter/submit.py`).

**Full-scan aggregation to copy** (`main()`, `:337`, `:350-355`):
```python
targets = [FIRESTARTER_DEVTEST_SRC, FIRESTARTER_DEVTEST_HANDLER]
...
full_scan_visitor = _scan_file(FIRESTARTER_DEVTEST_SRC)
if full_scan_visitor is not None:
    scanned.append(FIRESTARTER_DEVTEST_SRC)
    vpp_set_violations.extend(full_scan_visitor.vpp_set_violations)
    raw_wire_dict_violations.extend(full_scan_visitor.raw_wire_dict_violations)
    force_violations.extend(full_scan_visitor.force_violations)
```
`submit.py` is a fresh orchestrator module (like `chip_test.py`) → add it as a THIRD
FULL-scan target: append to `targets`, add a `_scan_file(FIRESTARTER_DEVTEST_SUBMIT)`
leg, include it in `_assert_host_only`. `submit.py` passes all three deny buckets by
construction (gh argv is a list not a dict; no VPP-set; no `--force`) — RESEARCH §SAFE-03.
The `scanned`-empty fail-closed guard (`:366-372`) already protects the new leg.

---

### `tests/test_submit.py` (NEW) + edits to `test_dev_test_cmd.py` / `test_diagnostic_report.py`

**Analog: `tests/test_dev_test_cmd.py:1-75`.**

**Seam pattern to copy** (`test_dev_test_cmd.py:30-41`, `:54-75`):
```python
from unittest.mock import Mock, patch
from click.testing import CliRunner
from firestarter.cli_handlers import AppContext, cli
from firestarter.database import EpromDatabase
# ...
def make_app_context(**overrides):
    """EpromDatabase(skip_local_override=True) + every manager Mock(spec=...)."""
```
Plus the autouse `FIRESTARTER_CONFIG_DIR` isolation fixture (`:54-65`) and the
`patch("firestarter.cli_handlers._is_interactive", ...)` idiom (NOT `sys.stdin.isatty`).

For `test_submit.py`: call `submit_report(...)` directly with mock
`which_fn`/`run_fn`/`browser_open`/`isatty_fn`/`confirm_fn` — never touch PATH, network,
or a browser. Assert tier selection, exact `gh` argv, sanitized stdin body, encoded-URL
byte measure + JSON-drop threshold, off-TTY no-send, D-03 refusal messaging, and that
each PII vector is scrubbed (A3 fails OPEN — one test per vector). See RESEARCH
§Phase Requirements → Test Map for the `-k` selectors.

## Shared Patterns

### Seam-injected callables with real defaults
**Source:** `cli_handlers.py:1717-1724` (`_is_interactive`) + the deleted
`prompt_provenance(ask=, confirm=)` style (documented `diagnostic_report.py:139-147`).
**Apply to:** every side-effecting boundary in `submit.py` (`which`, `subprocess.run`,
`webbrowser.open`, TTY check, `Confirm.ask`). Keyword arg + real default → monkeypatch
in tests.

### subprocess as an argv LIST (never shell, never dict)
**Source:** `avr_tool.py:15` + the SAFE-03 checker's `_WIRE_DICT_KEYS`/`--force` deny
buckets (`check_devtest_orchestrator.py`).
**Apply to:** the `gh` shell-out. A list argv avoids both command-injection (V5) and a
false-positive on the `visit_Dict` wire-dict check.

### to_dict() single-source serialization
**Source:** `diagnostic_report.py:346-363` (`to_dict`), consumed by `render()` (`:371`)
and `to_json_block()` (`:441`).
**Apply to:** the dedup fingerprint (add to `to_dict`, do not fork a field list) and
sanitization (scrub the DICT recursively, then build both the human table and fenced
JSON from the scrubbed dict — RESEARCH §Sanitization).

### D-03 refuse-gate predicate
**Source:** `diagnostic_report.py:150-162` (`is_submittable`).
**Apply to:** `submit_report` entry — refuse when `is_submittable(report.auto_capture)`
is `False`; re-derive the missing field names locally (`is_submittable` returns only a
bool) per RESEARCH §Guardrails.

### Filesystem-safe token (adjacent, do NOT reuse for body content)
**Source:** `cli_handlers.py:1668-1683` (`_sanitize_chip_token`).
Note: this sanitizes FILENAMES. The SUB-02 body sanitizer is a sibling concern (content
PII scrub) — a NEW regex set in `submit.py`, not this helper.

## No Analog Found

None. Every file has an exact or role-match analog. The two genuinely new capabilities —
URL-encoding/byte-measuring (`urllib.parse`) and the recursive PII string-scrub (`re` +
`getpass.getuser()`) — have no in-repo precedent but are fully specified in RESEARCH
§Browser URL Facts, §Oversize Handling, and §Sanitization (concrete regex set at
lines 285-303). Planner should follow those, not hunt for a codebase analog.

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tools/`,
`firestarter_app/tests/`
**Files read:** `avr_tool.py`, `diagnostic_report.py`, `cli_handlers.py` (dev_test +
helpers), `firmware.py` (import head), `constants.py` (owner-URL head),
`check_devtest_orchestrator.py` (main + constants), `test_dev_test_cmd.py` (seam head)
**Pattern extraction date:** 2026-07-03
