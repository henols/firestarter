# Phase 190: Endpoints That Do Not Depend on a Redirect - Pattern Map

**Mapped:** 2026-09-13
**Files analyzed:** 8 (5 modified in `firestarter_app`, 1 new test module, 2 new evidence artifacts)
**Analogs found:** 7 / 8

All analog paths below were checked with `git ls-files` in their owning repository and are
**git-tracked source**, not gitignored mirrors. Paths inside `firestarter_app/` are tracked in the
`firestarter_app` submodule; paths under `.planning/` are tracked in the meta repository.

> **Binding constraint on every excerpt in this document.** `/workspaces/CLAUDE.md` § "Source code
> comments — hard rule" and `firestarter_app/CLAUDE.md` both forbid **any** comment in
> `firestarter_app/` — product source *and* `tests/`. Several analogs below are heavily commented.
> **Copy the structure, never the comments.** Docstrings are not comments and are the house idiom
> (every analog test carries one); Click docstrings are `--help` text. A plan must not say "add a
> comment citing X" and must not make "a comment exists" an acceptance criterion.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/firestarter/constants.py` (3 URL constants) | config | — | the same file's existing constant block | exact (in-file edit) |
| `firestarter_app/tests/test_endpoint_constants.py` **(new)** | test — invariant pin | transform | `firestarter_app/tests/test_revision_constants_parity.py` | exact |
| `firestarter_app/tests/test_firmware_install.py:383,494` | test — fixture derivation | request-response (mocked) | the same file's `mock_releases_factory` sites | exact (in-file edit) |
| `firestarter_app/firestarter/firmware.py` — `list_releases` → `Optional` | service | request-response | `firmware.py::_pick_asset`, `firmware.py::fetch_latest_release_info` | exact |
| `firestarter_app/firestarter/firmware.py` — `manage_firmware_update` guard before the final `return True` | service | request-response | `firmware.py:910-915` (the `should_install_now` guard) | exact |
| `firestarter_app/firestarter/cli_handlers.py:1206-1226` — `--list` render + exit | controller | request-response | `cli_handlers.py:1196-1204` (the `--dfu-probe` branch) | **exact — this is the key analog** |
| new tests for D-06/D-09/D-11 (stream-sensitive) | test — CLI | request-response | `tests/test_cli_handlers.py:124-125` (no-`obj=` + exit 1) | partial — see Gap 1 |
| `firestarter_app/tests/test_py32_pyusb_absent.py` (adapt the vehicle, Finding 4) | test — subprocess CLI | request-response | the same file's `_CHILD_PROGRAM_TEMPLATE` | exact (in-file edit) |
| `firestarter_app/firestarter/submit.py:59`, `.planning/codebase/INTEGRATIONS.md:8` | doc/comment string edit | — | — | trivial, no analog needed |
| `190-*.sh` evidence script **(new)** | evidence script | batch | `.planning/phases/189-free-the-name/fresh-clone-fixture.sh` | exact |
| evidence transcript **(new)** | evidence | — | `.planning/phases/189-free-the-name/evidence/189-rename-03-fresh-clone.txt` | exact |

---

## Pattern Assignments

### `firestarter_app/firestarter/cli_handlers.py` — the `--list` failure/exit branch (controller)

**Analog: `cli_handlers.py:1196-1204`, the `--dfu-probe` branch, eleven lines above the code being
changed.** It is the same shape the D-09/D-11 change needs — a branch that renders a result, chooses
between two exit codes on an emptiness test, and calls `sys.exit` itself:

```python
    if dfu_probe:
        found = app.firmware_manager.probe_dfu(usb_id=usb_id)
        if not found:
            print("No USB DFU devices found.")
            sys.exit(1)
        print("Attached USB DFU devices:")
        for line in found:
            print(f"  {line}")
        sys.exit(0)
```

**How the new code differs and why:** `probe_dfu` conflates "none found" with "failed"; D-10 is
precisely the decision *not* to repeat that. So the guard is `if releases is None:` (identity, not
truthiness — `[]` is falsy and must still take the exit-0 path per D-13), placed **before** the
`if json_output:` branch so no document is emitted on either rendering path (D-11).

**The branch being replaced** (`cli_handlers.py:1206-1226`, verbatim; note `import json as _json` is
a function-local import — keep that idiom, and note D-10 forbids adding a `requests` import here):

```python
        releases = app.firmware_manager.list_releases(
            channel_filter=channel_filter, board=board
        )
        if json_output:
            import json as _json

            print(_json.dumps(releases, indent=2))
        else:
            print(f"{'Version':<12} {'Channel':<14} {'Published':<22} Asset URL")
            for r in releases:
                print(
                    f"{r['version']:<12} {r['channel']:<14} {r['published']:<22} {r['asset_url']}"  # noqa: E501
                )
        sys.exit(0)
```

**Stderr write — no in-repo precedent exists.** `git grep` finds no production module in
`firestarter/` writing to `sys.stderr` (only `avr_tool.py` and `submit.py` *reading* subprocess
stderr). Per RESEARCH § Alternatives, `click.echo(..., err=True)` is the smaller conceptual jump
inside a Click handler; `print(..., file=sys.stderr)` is equivalent. Either is new surface — the
planner picks one and states it. `sys` and `click` are both already imported in this module.

**Exit wiring to preserve:** `sys.exit(0 if ok else 1)` at `cli_handlers.py:1266` is the update
path's exit; the `--list` and `--dfu-probe` branches exit earlier and independently.

---

### `firestarter_app/firestarter/firmware.py` — `list_releases` returning `Optional` (service)

**Analog for the signature: `firmware.py:140`,** the file's own `str | None` idiom, and
`firmware.py:241`'s `Tuple[str | None, str | None]  # noqa: UP006`. The file deliberately keeps
`List`/`Tuple` with `# noqa: UP006`; **match that, do not "modernise"**, or ruff's `UP` rules churn
the diff.

```python
def _pick_asset(assets: object, board: str) -> str | None:
    """Resolve the download URL of the first matching asset, else None."""
    if not isinstance(assets, list):
        return None
```

Target form (per RESEARCH, probed green under ruff): `-> List[ReleaseInfo] | None:  # noqa: UP006`.

**Analog for the failure arm — the only line that changes in the body, at `firmware.py:421-423`:**

```python
        try:
            all_releases = self._fetch_all_releases()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch releases for list: {e}")
            return []
```

`return []` becomes `return None`. **The `logger.error` stays** (D-07), and per Finding 5 it goes to
**stdout** in production — which is why a D-11 test must assert "no JSON document on stdout", never
`result.stdout == ""`.

**Error-message house style to copy** (`firmware.py:258-260`) — an f-string naming the board, with
`# noqa: E501` when the line is long. Per RESEARCH § Measured Live Behaviour, the existing messages
name the **board but not the endpoint URL**, so the new D-06/D-09 messages must carry the URL
themselves; they cannot lean on the pre-existing line:

```python
                logger.error(
                    f"Could not find firmware version or URL for board '{board}' in the latest release."  # noqa: E501
                )
                return None, None
```

---

### `firestarter_app/firestarter/firmware.py` — the D-06 guard (service)

**Analog: `firmware.py:910-915`,** the guard D-08 warns about double-emitting. The new guard is the
same shape, one nesting level out, immediately before the file's final `return True`:

```python
        if should_install_now:
            if not download_url or not latest_version:
                logger.error(
                    f"Cannot install: latest firmware URL or version for {board_to_use} is not available."  # noqa: E501
                )
                return False
```

```python
        return True  # No installation performed, but process completed as expected
```

**Two things the planner must carry from RESEARCH Finding 3:** (a) that trailing line is the file's
**last** line — cite it by content (`return True  # No installation performed...`), not by number;
(b) every branch inside `if should_install_now:` returns, so a guard placed just above it is
**structurally** unreachable when `should_install_now` is `True` — no `force_install` / `install_flag`
condition is needed or wanted. The condition to use is `not latest_version or not download_url`,
mirroring line 911.

**The pre-existing comment on that `return True` line is not this phase's to add or extend.** If the
line is rewritten, do not re-author a comment on it.

---

### `firestarter_app/tests/test_endpoint_constants.py` (new — test, invariant pin)

**Analog: `firestarter_app/tests/test_revision_constants_parity.py`** — the repository's established
standalone-constants-invariant module. Its shape:

**Imports pattern** (top of the file, by-name import from `firestarter.constants`):

```python
from firestarter import constants
from firestarter.constants import (
    REVISION_0,
    REVISION_1,
    REVISION_2_0,
)
```

**Core assertion leg** (`tests/test_revision_constants_parity.py:151-160`) — a docstring stating the
invariant and what drift it catches, then flat positive asserts:

```python
def test_revision_byte_values_match_firmware_enum():
    """Assert each REVISION_* byte value matches the firmware enum at
    `firestarter/include/rurp_shield.h:25-31` (post-Plan-02 HEAD). This is
    the Phase 34 D-08 cross-repo parity invariant — drift on either side
    fails the gate at pytest time."""
    assert REVISION_0 == 0x00
    assert REVISION_1 == 0x01
```

Copy the docstring-carries-the-rationale discipline (the "why" belongs there, and in `SUMMARY.md`);
the file's inline `#` comments must **not** be reproduced.

**Planted-violation / reachability pattern** (`tests/test_revision_constants_parity.py:706-720`) —
the repository's precedent for criterion 2's "prove the pin actually fails". Note it uses a
**committed fixture** plus `monkeypatch` and `pytest.raises(AssertionError)`:

```python
def test_planted_value_drift_is_detected(monkeypatch: pytest.MonkeyPatch) -> None:
    """..."""
    assert _FIXTURE_VALUE_DRIFT.is_file(), (
        f"committed fixture missing: {_FIXTURE_VALUE_DRIFT}"
    )
    monkeypatch.setattr(sys.modules[__name__], "FIRMWARE_HEADER", _FIXTURE_VALUE_DRIFT)
    with pytest.raises(AssertionError) as excinfo:
        _check_cmd_two_way()
    message = str(excinfo.value)
    assert "CMD_VERIFY = 106" in message
```

**How the pin differs:** it asserts module-level string constants, so there is no header-parsing
helper to re-enter. RESEARCH's chosen falsification proof is therefore the out-of-band `sed`/revert
transcript (RESEARCH § Code Examples), **not** an in-suite planted-violation test. The planner should
pick one and say which; the transcript route is cheaper and matches D-16's evidence-under-the-phase-
directory habit.

**Assertion content is fixed by decision, not discretion:** positive-only, on the slug
(`"henols/firestarter_fw/" in url`) — D-02 forbids a negative assertion (`henols/firestarter` is a
substring of `henols/firestarter_fw`) and D-03 forbids pinning the full URL.

---

### `firestarter_app/tests/test_firmware_install.py:381-384, 492-495` (test — fixture derivation)

**Analog: the sites themselves.** Verbatim, and note `:494` already carries `# noqa: E501` — an
f-string over the constant will still need it:

```python
        page1_mock = mock_releases_factory(
            releases_page1,
            next_url="https://api.github.com/repos/henols/firestarter/releases?page=2",
        )
```

```python
            mock_releases_factory(
                release_on_page(i),
                next_url=f"https://api.github.com/repos/henols/firestarter/releases?page={i + 1}",  # noqa: E501
            )
```

The module has **no** `from firestarter.constants import ...` today, so URL-03 adds one. Per
RESEARCH Pitfall 7, `firmware.py` imports the constants **by name**, so any test that *monkeypatches*
a constant must patch `firestarter.firmware.FIRESTARTER_*`; a test that merely *reads* the value for
an f-string may import from either module — importing from `firestarter.constants` is the honest
source for URL-03.

**D-01 is explicit that this half is a tautology on its own.** Neither `next_url` is ever asserted;
the pin is the guard.

---

### CLI tests for D-06 / D-09 / D-11 (test — stream-sensitive) — **Gap 1**

**The three analogs the orchestrator asked for, measured:**

| Asked for | Found? |
|---|---|
| a `CliRunner` test with **no `obj=`** | **yes — 11 sites.** `tests/test_cli_handlers.py:84,95,103,124,205,215`; `tests/test_dev_test_cmd.py:547`; `tests/test_erase_blank_step_nonregression.py:80`; plus three inside subprocess child-program templates (`test_dev_group_channel_gating.py:104`, `test_py32_channel_gating.py:97`, `test_py32_pyusb_absent.py:202`). |
| a test asserting **`result.stderr` separately from stdout** | **NO — none exists.** Every `result.stderr` hit in `tests/` is a `subprocess.CompletedProcess`, not a `click.testing.Result`: `test_characterization.py:159` (`subprocess.run`), `test_fw_presence.py:123,144,146,169`, `test_gen_validation_header.py:106`, `test_sdp_bus_config_drift.py:85,156`, `test_dev_group_channel_gating.py:170`, `test_py32_channel_gating.py:139`, `test_py32_pyusb_absent.py:252`. **A CliRunner stream-split assertion is new surface in this repository.** |
| a test asserting a **non-zero exit code** | **yes — dozens.** `tests/test_cli_handlers.py` alone has ~24 `assert result.exit_code == 1`. |

**The one analog that is all three things the D-11 test needs at once — no `obj=`, real exit-code
assertion** (`tests/test_cli_handlers.py:123-125`):

```python
def test_info_unknown_chip_error_path(runner: CliRunner) -> None:
    """`firestarter info NOPE_NOT_A_CHIP` exits 1 with chip-not-found error."""
    result = runner.invoke(cli, ["info", "NOPE_NOT_A_CHIP"])
    assert result.exit_code == 1
```

**The `runner` fixture** (`tests/test_cli_handlers.py:78-81`) is reusable as-is, **but its docstring
is stale and must not be trusted or copied**:

```python
@pytest.fixture
def runner() -> CliRunner:
    """Fresh CliRunner per test — mix_stderr=True so stderr+stdout flow into result.output."""
    return CliRunner()
```

`mix_stderr` was removed in Click 8.2 and the installed Click is **8.5.0**; `result.stdout` and
`result.stderr` are always separate and `result.output` is their concatenation. A new test module
should define its own fixture with an accurate docstring rather than inherit this one.

**The dominant house style is the anti-pattern here.** `runner.invoke(cli, argv, obj=app)` is used at
126 of 137 sites (e.g. `test_fw_list_plain`, `test_fw_list_with_json` at `tests/test_cli_handlers.py:647-663`):

```python
def test_fw_list_plain(runner: CliRunner) -> None:
    """`firestarter fw --list` exits 0 with mocked list_releases returning []."""
    fw_mgr = Mock(spec=FirmwareManager)
    fw_mgr.list_releases.return_value = []
    app = make_app_context(firmware_manager=fw_mgr)
    result = runner.invoke(cli, ["fw", "--list"], obj=app)
    assert result.exit_code == 0
```

Per `cli_handlers.py:427-430`, `obj=` short-circuits the group callback **before** `_setup_logging`
runs, so `logger.error` falls through to `logging.lastResort` (stderr) instead of
`SingleLineStatusHandler` (stdout). A D-11 stderr assertion written this way passes for the wrong
reason. **Use `obj=` for the exit-code-only tests (matching the file), and no-`obj=` for anything
asserting a stream.** These two tests must also stay green (D-13) — both stub `[]`, which remains
exit 0.

---

### `firestarter_app/tests/test_py32_pyusb_absent.py` (test — adapt the vehicle, Finding 4)

The one test the D-09 change breaks. The seam to edit is in the child-program template at
`tests/test_py32_pyusb_absent.py:186-197` — **the comment quoted there encodes the old contract
verbatim and will be false after this phase**, so it goes with the change (removal, not rewriting
into a new comment):

```python
def _raise_request_exception(*_args, **_kwargs):
    raise requests.RequestException(
        "blocked: no network access in this subprocess test"
    )


# Stub the HTTP seam so `fw --list` needs no network: list_releases() already
# catches requests.RequestException and returns an empty list (the real code
# path, not a bypass of it).
_firmware_module.requests.get = _raise_request_exception
```

The assertions it feeds (`:274-283`) expect exit 0 plus four header-row labels. Per RESEARCH the fix
is to make the child stub return a **successful empty release list** instead of raising — preserving
the module's stated intent ("`fw --list` exits 0 offline", header row present, `usb*` never imported)
rather than re-purposing a pyusb-absence test into an endpoint test. Note the child reports only
`result.output`, so it cannot make a stream claim — another reason not to relocate D-11 here.

---

### The D-16 evidence script (new — evidence script, batch)

**Analog: `/workspaces/.planning/phases/189-free-the-name/fresh-clone-fixture.sh`** (tracked, 220
lines, executable). Copy its skeleton wholesale. Concrete excerpts:

**Header + strict mode + self-documenting `--help`** (lines 1-55, 62-70):

```bash
#!/usr/bin/env bash
#
# fresh-clone-fixture.sh
#
# Proves RENAME-03: ...
#
# Usage:
#   bash fresh-clone-fixture.sh                  # clone $META_REF (default below)
#   KEEP_CLONE=1 bash fresh-clone-fixture.sh      # leave the scratch tree for inspection
#   bash fresh-clone-fixture.sh --help            # print this usage and exit 0
#
# Environment: ... Dependencies: ... Failure style: ... Exit codes: ... Re-runnable: ...

set -euo pipefail

for arg in "$@"; do
    case "$arg" in
        --help)
            sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
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

(`#` comments are fine here — a shell script under `.planning/` is **not** `firestarter_app/` source
and the hard rule does not reach it.)

**Path resolution and env overrides** (lines 79-82) — never hardcode `/workspaces`:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
META_REF="${META_REF:-v1.38-repository-rename}"
KEEP_CLONE="${KEEP_CLONE:-0}"
```

**Scratch + trap** (lines 103-118) — `mktemp -d` **outside** `/workspaces`, because `git clean -Xdf`
destroys GSD state:

```bash
SCRATCH_PARENT="${SCRATCH_DIR:-$(mktemp -d)}"
CLONE_DIR="$SCRATCH_PARENT/meta-clone"
cleanup() {
    rm -f "$CLONE_LOG"
    if [ "$KEEP_CLONE" != "1" ]; then
        rm -rf "$SCRATCH_PARENT"
    fi
}
trap cleanup EXIT
```

**Labelled-value emission before the verdict** (lines 155-174) — this is the `<specifics>` "must
print what it resolved" requirement, already implemented:

```bash
echo "meta_commit: $META_COMMIT"
echo "gitmodules_url(firestarter): $GITMODULES_URL_FW"
echo "remote_origin(firestarter): $REMOTE_ORIGIN_FW"
```

For Phase 190 the labelled lines are `requested:` / `resolved:` / `status:` / `redirects:` /
`version:` / `asset_url:` per RESEARCH's D-16 instrument.

**Assertion style — bail on first failure, each naming expectation, pre-state and next action, with
the boundary-aware discriminator already written** (lines 196-212; reuse the pattern literally,
do not re-derive it):

```bash
BARE_SLUG_PATTERN='henols/firestarter([^_a-zA-Z0-9]|$)'
if echo "$REMOTE_ORIGIN_FW" | /usr/bin/grep -qE "$BARE_SLUG_PATTERN"; then
    echo "FAIL: Assertion 3 -- remote_origin(firestarter) matches the bare-slug discriminator: $REMOTE_ORIGIN_FW" >&2
    echo "      Expected the URL to name firestarter_fw only, not the bare 'firestarter' slug." >&2
    exit 1
fi
```

**Verdict token + exit-code contract** (lines 216-219): a literal all-caps `... OK` token, `exit 0`;
1 = failure, 2 = bad usage, **3 = one named, expected non-failure case**. Phase 190's natural exit-3
candidate is "network unavailable" — a live-network script that cannot reach `api.github.com` should
say so distinctly rather than read as a URL regression.

**Note `/usr/bin/grep` is spelled explicitly throughout** — the devcontainer `grep` is ugrep and
honours `.gitignore`, so a gate built on bare `grep` fails **open**.

---

### The evidence transcripts (new)

**Analog: `/workspaces/.planning/phases/189-free-the-name/evidence/189-rename-03-fresh-clone.txt`**
(tracked). Shape: a titled header, `capture_date:` (ISO-8601 Z) and `capture_commit:`, the exact
command in a block, then numbered `READING N` sections each with its raw captured output and a prose
paragraph explaining what the reading proves and what it does **not**. `189-firmware-slug-sweep.txt`
adds the `command:` / `matching files:` / `result:` triple plus a **non-vacuity positive control**
(`henols/firestarter_prom` → 8 files) — reproduce that control in the D-05 sweep transcript, because
Pitfall 1 shows the naive sweep returns 6 of 7 sites and reads falsely clean.

Two transcripts are needed: the D-16 live-endpoint one and D-17's five-step CI-equivalent run inside
`/workspaces/firestarter_app/.venv311` (Python 3.11.16, already present).

---

## Shared Patterns

### Logging and operator-visible errors
**Source:** `firestarter/firmware.py:258-260`, `:421`, `:911-915`
**Apply to:** every message this phase adds in `firmware.py`
Module-level `logger`, f-string message, `# noqa: E501` on long lines, `logger.error` for the
operator-visible failure. In production `logger.error` reaches **stdout** via
`SingleLineStatusHandler` (`logging_utils.py:27`) at default level INFO (`cli_handlers.py:103`) —
so "make it visible" needs no new plumbing, but "put it on stderr" (D-11) does.

### Exit-code selection lives only in the CLI layer
**Source:** `cli_handlers.py:1196-1204` and `:1266`
**Apply to:** all of URL-04
`sys.exit` appears only in `cli_handlers.py`; `firmware.py` never exits. D-06 is therefore a
`return False` in the service layer, and D-09/D-11 are a `sys.exit(1)` in the handler.

### Typing idiom
**Source:** `firmware.py:140`, `:241`, `:406`, `:428`
**Apply to:** the `list_releases` annotation
`X | None` for scalars; `List[...]`/`Tuple[...]` retained with `# noqa: UP006` where already present.
Do not modernise. mypy is a local pre-commit hook, **not** a CI gate (`firestarter_app/CLAUDE.md`),
so a mypy finding is a quality signal, not a blocker.

### Test-module docstring carries the rationale
**Source:** `tests/test_revision_constants_parity.py:1-50`, `tests/test_erase_flag_invariants.py:1-55`
**Apply to:** the new pin module and every new test
Long module and function docstrings stating the invariant, the anti-vacuity trap, and the
reachability evidence are the house style and are **not** comments. This is where D-01/D-02/D-03
rationale goes — never in an inline `#`.

### Sweep hygiene
**Source:** `fresh-clone-fixture.sh:204`, `189-02-PLAN.md:218`
**Apply to:** every `<automated>` block and the D-05 verification sweep
`git grep -nE 'henols/firestarter([^_a-zA-Z0-9]|$)'` for tracked files, `/usr/bin/grep` spelled in
full for filesystem sweeps, always paired with the `henols/firestarter_prom` positive control.

---

## No Analog Found

| File / concern | Role | Data Flow | Reason |
|---|---|---|---|
| the stderr write in `cli_handlers.py` (D-11/D-12) | controller | request-response | **No production module in `firestarter/` writes to `sys.stderr` or uses `click.echo(err=True)`.** `git grep` finds only subprocess-stderr *reads* in `avr_tool.py` and `submit.py`. Either `click.echo(..., err=True)` or `print(..., file=sys.stderr)` is new surface; RESEARCH § Alternatives prefers the former inside a Click handler. |
| a CliRunner test asserting `result.stderr` | test | request-response | **None exists** (see Gap 1). Every `result.stderr` in `tests/` is a `subprocess.CompletedProcess`. The planner must specify the harness explicitly — `CliRunner().invoke(cli, argv)` with **no `obj=`**, asserting `result.stdout` and `result.stderr` separately and never `result.output`. |
| Intel HEX validation in the D-16 script | evidence script | file-I/O | `firestarter_app` has no HEX parser. Use the cheap format assertion RESEARCH measured (every non-empty line starts `:`, final record `:00000001FF`); do not add an `intelhex` dependency for one evidence script. |

---

## Metadata

**Analog search scope:** `/workspaces/firestarter_app/firestarter/`, `/workspaces/firestarter_app/tests/`,
`/workspaces/.planning/phases/189-free-the-name/`
**Files scanned:** ~150 (`tests/` listing + `git grep` sweeps for `CliRunner`, `result.stderr`,
`exit_code`, `Optional`, `from firestarter.constants`); 9 read in depth
**Tracked-source gate:** every analog path confirmed via `git ls-files` in its owning repository
**Pattern extraction date:** 2026-09-13
