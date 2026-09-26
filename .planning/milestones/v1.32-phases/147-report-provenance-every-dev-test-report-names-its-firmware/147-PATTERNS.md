# Phase 147: Report Provenance — every `dev test` report names its firmware - Pattern Map

**Mapped:** 2026-08-18
**Files analyzed:** 11 (5 production + 4 test + 1 skill script + 1 skill doc)
**Analogs found:** 11 / 11 (7 exact, 3 role-match, 1 partial — see §No Analog Found for the one true greenfield surface)

All line coordinates below were opened on disk this session. Drift vs the prompt is
flagged inline as **[DRIFT]**. Repos: meta `/workspaces`, app submodule
`/workspaces/firestarter_app` (currently on `gsd/v1.31-27c-programming-algorithm-fidelity`
— **must be re-based off `origin/beta` before any executor runs**).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/firestarter/hardware.py` | service (hardware layer) | request-response (one serial round trip) | **itself**, `get_hardware_revision()` `:88-113` (the bool sibling) + `firestarter/frame_vectors.py:20` for the NamedTuple | exact |
| `firestarter_app/firestarter/cli_handlers.py` | controller (Click handler) | request-response | **itself**, the current `AutoCapture(...)` block `:2494-2507` | exact |
| `firestarter_app/firestarter/diagnostic_report.py` | model + renderer | transform (dict → rich table / JSON) | **itself**, `NOT_MEASURED` `:85`, `SCHEMA_VERSION` block `:55-84`, `render()` `:505-530` | exact |
| `firestarter_app/tools/parse_devtest_issue.py` | utility (stdlib-only CLI) | transform (issue body → text) | **itself**, `render_diff`'s `n_agreeing` labelled-clause block `:214-218` | exact (sibling-line analog; no test analog exists) |
| `/workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py` | utility (skill script) | transform | **itself**, `cmd_show`'s `host … hw` print `:332-333` and `_summarize`'s `or "?"` at `:185` | exact (but `or` idiom is an ANTI-pattern here — P-8) |
| `/workspaces/.claude/skills/devtest-triage/SKILL.md` | docs | — | **itself**, `:61-67` verbatim `show` transcript | exact |
| `firestarter_app/tests/test_hardware.py` | test (unit, hardware) | request-response | `test_get_hardware_revision_happy_path` `:51-63` + `test_get_hardware_revision_failure_path` `:66-77` | role-match (the *bool* sibling is tested; the value-returning one is not — greenfield assertions) |
| `firestarter_app/tests/test_dev_test_cmd.py` | test (handler, end-to-end) | request-response | `make_hardware_manager` `:372-401`; `test_hw_revision_auto_captured_end_to_end` `:730-743` | exact |
| `firestarter_app/tests/test_diagnostic_report.py` | test (render unit) | transform | `_rendered_text` `:967-969` + `test_hold_state_held_reaches_both_surfaces` `:972-985` + `_minimal_report` `:145-193` | exact |
| `firestarter_app/tests/test_parse_devtest_issue.py` | test (parser unit) | transform | `_B11_BODY` `:361-454` + `test_legacy_vocabulary_b11_body_still_parses` `:456-478`; imports at `:42-56` | role-match (fixture shape exists; `render_diff` has zero tests) |
| `/workspaces/.gitignore` | config | — | already-staged working-tree hunk (verified below) | exact — **precondition, not a design choice** |

---

## Pattern Assignments

### `firestarter/hardware.py` (service, request-response) — the only new logic

**Analog:** the file's own `read_hardware_revision_value()` `:115-147` (the method being
renamed/widened) and its bool sibling `get_hardware_revision()` `:88-113`.
**[DRIFT]** the prompt's `:115-148` is the `def` line through one trailing blank; the body ends `:147`.

**Imports pattern** (`hardware.py:9-28`) — `typing` is imported with a ruff-suppression comment; a
`NamedTuple` addition joins that same line:

```python
import logging
import re
import statistics
import time
from typing import Optional, Tuple  # noqa: UP035

from firestarter.config import ConfigManager
from firestarter.constants import (
    COMMAND_CONFIG,
    COMMAND_HW_VERSION,
    COMMAND_READ_VPE,
    COMMAND_READ_VPP,
)
from firestarter.exceptions import (
    HardwareOperationError,
    ProgrammerNotFoundError,
    SerialError,
    SerialTimeoutError,
)
from firestarter.serial_comm import SerialCommunicator

logger = logging.getLogger("Hardware")
```

Note: `Optional` (not `X | None`) is this module's convention — **P-9**: `diagnostic_report.py`
already breaks the py3.9 floor, do not propagate that here.

**Module-level private-constant precedent** (`hardware.py:32-35`) — where a module-private helper or
regex lives, i.e. where a `_scrub_identity` belongs:

```python
# Tolerant match for the FIRST "%u.%uV" pair in a 0xE4/0xE5 DATA message
# (e.g. "VPP: 20.9V, Internal VCC: 5.0V") -- guards against catalog format
# wording drift (Pitfall 3 / T-111-DRIFT).
_VOLTAGE_RE = re.compile(r"(\d+)\.(\d+)\s*V")
```

**Core pattern to copy — the exact method being widened** (`hardware.py:115-147`, verbatim):

```python
    def read_hardware_revision_value(self, flags: int = 0) -> Optional[str]:
        """Value-returning sibling of get_hardware_revision: returns the
        coarse revision-bucket string (or None on any transport error / a
        non-ready ack) instead of only logging it.

        Mirrors get_hardware_revision's exact find_and_connect -> expect_ack
        -> disconnect handshake but returns data rather than printing (same
        relationship sample_vpp_mv/_sample_one_voltage bears to
        read_vpp_voltage). This is the auto-capture source for
        AutoCapture.hw_revision (Phase 112 Plan 04) -- a coarse bucket or an
        honest None is an accepted outcome, never a fabricated value. Opens
        ONE serial read (energize/query only) -- no VPP-set, no wire-dict,
        no --force (SAFE-02 clean). Does NOT change get_hardware_revision's
        existing bool contract -- the `dev hw` CLI command depends on that.
        """
        command = {"state": COMMAND_HW_VERSION}
        if flags:
            command["flags"] = flags

        comm = None
        try:
            comm = SerialCommunicator.find_and_connect(command, self.config)
            is_ok, msg = comm.expect_ack()
            if is_ok:
                return msg
            logger.error(f"Failed to read hardware revision: {msg}")
            return None
        except (ProgrammerNotFoundError, SerialError, SerialTimeoutError) as e:
            logger.error(f"Failed to read hardware revision: {e}")
            return None
        finally:
            if comm:
                comm.disconnect()
```

Three structural facts a planner must preserve: the `{"state": COMMAND_HW_VERSION}` dict shape
(outside the AST gate's denied wire-key vocabulary AND in an unscanned file), the three-exception
tuple (F-17: `FirmwareOutdatedError` / `HardwareRevisionUnsupportedError` are `SerialError`
subclasses and land here), and `finally: if comm: comm.disconnect()` (SAFE-02 teardown, unchanged).

**NamedTuple pattern** (`firestarter/frame_vectors.py:17-22`) — the in-repo precedent RESEARCH cites,
verified:

```python
from typing import NamedTuple


class FrameVector(NamedTuple):
    id: int
    name: str
    payload: bytes
    frame: bytes
```

Plain `class X(NamedTuple)` with annotated fields; no `total=`, no defaults, no `dataclasses`.

**Sanitising precedent for D-07** (`cli_handlers.py:2159-2173`) — copy the *shape*
(char-by-char allow-list loop), **never the character class** (it maps `:` → `_`, which would mangle
`"3.0.0b19:leonardo"`):

```python
def _sanitize_chip_token(chip: str) -> str:
    """Filesystem-safe token for the dev-test-<chip>.{json,md} artifact names.
    ...
    Deterministic: the same chip name always sanitizes to the same token.
    """
    safe_chars = []
    for ch in chip:
        if ch.isalnum() or ch in ("-", "_", "."):
            safe_chars.append(ch)
        else:
            safe_chars.append("_")
```

⚠ **Do not place the scrubber in `cli_handlers.py`** — see §Shared Patterns / Trap 1. It belongs in
`hardware.py` beside `_VOLTAGE_RE`.

---

### `firestarter/cli_handlers.py` (controller, request-response) — one unpack, zero new callables

**Analog:** the construction site itself. Verified verbatim at `:2493-2507`:

```python
    # fw_board_identity stays None: EpromOperator.comm is a transient
    # per-operation connection torn down after every operator call (see
    # 112-02-SUMMARY.md) -- there is no live comm to read programmer_info
    # off of after run_plan returns without opening a new, extraneous
    # connection, which would violate the orchestrator-only contract
    # (SAFE-02). hw_revision IS reachable via a dedicated, orchestrator-safe
    # energize/query read (Part A, hardware.py) and is populated below.
    auto_capture = AutoCapture(
        host_version=version,
        fw_board_identity=None,
        hw_revision=app.hardware_manager.read_hardware_revision_value(),
        chip=chip,
        protocol=None,
    )
```

**[DRIFT, cosmetic]** the comment runs `:2493-2499` (not `:2494-2500`); `auto_capture = AutoCapture(`
is `:2500`, `fw_board_identity=None` `:2502`, the `read_hardware_revision_value()` call `:2503`,
closing `)` `:2506`. The prompt/RESEARCH coordinates are each one line high. Anchor the edit on the
literal `fw_board_identity=None`, not on a line number.

The comment is **replaced, not deleted** (CONTEXT §Specific Ideas): the old text says why
`EpromOperator.comm` cannot serve; the replacement says why the hw-revision connection can.

**The keyword-construction style to preserve** — every field passed by keyword, one per line. The
change is `identity = app.hardware_manager.read_programmer_identity()` on the line above, then
`fw_board_identity=identity.fw_board_identity` / `hw_revision=identity.hw_revision`. **Named field
access, never `a, b = ...`** (D-03).

---

### `firestarter/diagnostic_report.py` (model + renderer, transform)

**Analog:** the file itself, three sites.

**Constant + per-bump rationale block** (`:55-85`, the format D-09's note extends). The 1.3 note is
the closest analog in tone — it records a measured discrepancy rather than reconciling it, and
explicitly rejects a bump-less field change:

```python
SCHEMA_VERSION = "1.3"  # D-02: single-sourced, baked into to_dict() output
# 1.1 (Phase 114, GRAD-01): additive db_diff.ladder_state key -- backward
# compatible, existing consumers reading current_support_status/
# proposed_disposition are unaffected.
# 1.2 (Phase 121 Plan 06/07, D-06): the bump marks the seventh op string
# ... `tools/parse_devtest_issue.py` accepts
# `schema_version` by PRESENCE ONLY (see `_extract_fenced_report`), never an
# exact-value match, so this bump is invisible to that parser. ...
# 1.3 (v1.30 Phase 134 plan 134-06, D-10/LEG-12): additive `sdp_hold_state`
# key ... REJECTED: a field-plus-JSON change
# with no version bump -- the artifact shape would change while its own
# version claimed it had not, in the milestone whose close phase (Phase 137)
# arms a claim gate over exactly that kind of statement.
NOT_MEASURED = "not measured"  # D-03: honest fallback, never a false 0
```

The 1.4 note copies this shape: `# 1.4 (v1.32 Phase 147, D-09): …` — and must state the
**value-population vs key-addition** distinction (a key that was unconditionally `null` now carries
data). The new marker constant sits on the line beside `NOT_MEASURED` with the same
trailing-comment-carries-the-rationale style.

**Render rows** (`:505-520`, verbatim — the `str(None)` defect):

```python
    def render(self, console: Any = None) -> Any:
        """Human `rich` table built from the SAME dict `to_dict()` produces
        (RPT-01, D-01) -- never a second hand-maintained field list, never a
        re-parse of the JSON string produced by `to_json_block()`."""
        from rich.table import Table

        d = self.to_dict()
        ac = d["auto_capture"]
        table = Table(title=f"dev test -- {ac['chip']}")
        table.add_column("Field")
        table.add_column("Value")

        table.add_row("host_version", str(ac["host_version"]))
        table.add_row("fw_board_identity", str(ac["fw_board_identity"]))
        table.add_row("hw_revision", str(ac["hw_revision"]))
        table.add_row("protocol", str(ac["protocol"]))
        table.add_row(
            "chip_id (expected/actual)",
            f"{ac['chip_id_expected']} / {ac['chip_id_actual']}",
        )
```

**[DRIFT, cosmetic]** the two rows to fix are `:517` (`fw_board_identity`) and `:518`
(`hw_revision`) — the prompt says `:518-519`. `host_version` at `:516` is always populated and
needs no marker; `protocol` at `:519` and the `chip_id` pair at `:520-523` are **deliberately left
alone** (D-12).

Note the `render()` docstring's own contract: the table sources from `to_dict()`, never a second
field list. A marker helper must therefore branch on the **dict value**, not on the dataclass field.

---

### `tools/parse_devtest_issue.py` (utility, transform) — stdlib-only

**Analog:** `render_diff`'s own `n_agreeing` block — the labelled-clause style D-14 says to mirror.
Verified verbatim at `:192-216`:

```python
def render_diff(
    report_obj: dict[str, Any],
    diff: dict[str, Any],
    *,
    n_agreeing: int | None = None,
) -> str:
    """Plain-text current-vs-proposed DB-diff render (D-04, no third-party
    import). Explicitly labels any `n_agreeing` value a maintainer decision
    input, never an auto-promotion trigger (D-01)."""
    auto_capture = report_obj.get("auto_capture") or {}
    chip = auto_capture.get("chip", "?")
    lines = [
        f"dev test triage -- {chip}",
        f"  schema_version:          {report_obj.get('schema_version', '?')}",
        f"  dedup_fingerprint:       {diff.get('dedup_fingerprint', '')}",
        f"  current_support_status: {diff.get('current_support_status', '')}",
        f"  proposed_disposition:   {diff.get('proposed_disposition', '')}",
        f"  ladder_state:           {diff.get('ladder_state') or '(none)'}",
    ]
    if n_agreeing is not None:
        lines.append(
            f"  N agreeing inputs:     {n_agreeing} "
            "(maintainer decision input -- NEVER an auto-promotion trigger)"
        )
    return "\n".join(lines)
```

Patterns to copy: two-space-indented `f"  label:{padding}{value}"` rows appended to a `lines` list;
`.get(...)` with an inline fallback; a conditional row appended via `lines.append(...)` with the
qualifying clause as an adjacent string literal on its own line. `--` (double hyphen), never an
em dash, inside these literals.

**The stdlib-only contract, quoted** (`tools/parse_devtest_issue.py:9-14`) — this is the reason D-11
cannot be single-sourced:

```
INBOX-01 Community `dev test` Issue Triage Parser (v1.21 Phase 114)

Stdlib-only CLI a maintainer runs during `gsd-inbox` triage against a
community `dev test` GitHub issue.
```

and `:20-27`, the presence-only detection contract D-17 must not disturb:

```
Detection (D-04) requires BOTH markers ... AND a fenced ```json block whose parsed object
carries a `schema_version` key (`diagnostic_report.py:to_json_block`).
`schema_version` is accepted by PRESENCE (any value), not an exact
string match, so this parser survives a future schema bump ... without a code change.
```

**Call site** (`:251`, unchanged): `print(render_diff(report_obj, diff))` inside
`_run_single_mode` — the render is print-only; no return-value consumer to break.

---

### `.claude/skills/devtest-triage/scripts/devtest_issues.py` (utility, transform) — skill-owned

**Analog:** `cmd_show`'s own print block. Verified at `:324-341`:

```python
    auto = report.get("auto_capture") or {}
    steps = report.get("steps") or []
    volt = report.get("voltage") or {}
    dbd = report.get("db_diff") or {}

    print(f"#{args.number if args.number is not None else '?'}  "
          f"{t['chip']}  —  {t['verdict'].upper()}")
    print(f"  schema      {report.get('schema_version')}   "
          f"generated {report.get('generated')}")
    print(f"  host        {auto.get('host_version')}   "
          f"hw {auto.get('hw_revision')}")
    print(f"  protocol    {auto.get('protocol')}   chip {auto.get('chip')}")
    cid_e, cid_a = auto.get("chip_id_expected"), auto.get("chip_id_actual")
    if cid_e is not None or cid_a is not None:
        exp = f"0x{cid_e:X}" if isinstance(cid_e, int) else str(cid_e)
        act = f"0x{cid_a:X}" if isinstance(cid_a, int) else str(cid_a)
        print(f"  chip id     expected {exp}  actual {act}")
    print(f"  fingerprint {fingerprint(report, body)}")
```

Style: bare `print(f"  label{spaces}{value}")`, hanging-indent continuation strings, `auto.get(...)`
raw. Note the `cid_e is not None` guard — **this file already has the correct `is not None` idiom**
to copy for the identity, two lines below the `hw None` defect.

**Anti-pattern in the same file — do NOT copy** (`:185`, inside `_summarize`):

```python
        "host": auto.get("host_version") or "?",
```

`or` also fires on `""`, hiding the empty-string transport fault D-07 exists to keep visible (P-8).
Use `is None`.

**Contract:** no `from firestarter…` import may appear in this file (skills own their scripts). It
owns its own marker literal.

### `.claude/skills/devtest-triage/SKILL.md` (docs)

**Analog:** its own fenced transcript at `:59-76`, which reproduces the `show` output verbatim
including the exact line the script changes:

```
#32  at28c256  —  FAIL
  schema      1.2   generated 2026-08-07T12:07:39Z
  host        3.0.0b15   hw Rev 2.0-class, Override HW: Rev 2.3
  protocol    13   chip at28c256
  fingerprint 00e121446ceb
```

That `host … hw …` line must be regenerated from the new script output in the **same commit**. Note
the transcript's `host 3.0.0b15` with no firmware line is literally the gh#21/#32 half-answer D-15
names — the updated transcript is itself the evidence PROV-06 is satisfied.

---

### `tests/test_hardware.py` (test unit) — the largest greenfield surface (W-1)

**Analog:** the two `get_hardware_revision` legs in the same file. **Verified: 13 tests in the file,
zero of them touch `read_hardware_revision_value`.**

**File-header + import pattern** (`:1-28`), including the safety-boundary docstring convention and
the *stated test pattern* this phase reuses:

```python
"""Phase 42 / ERR-03 coverage lift for ``HardwareManager`` READ-SIDE voltage
methods (D-14.5).

SAFETY BOUNDARY: this file does NOT exercise ``set_vpp_voltage`` or
``set_vpe_voltage`` ...

Test pattern: patch ``SerialCommunicator.find_and_connect`` to return a
``make_comm()``-built communicator wired to ``fake_serial``; feed the wire
frames the firmware would emit.
"""

import re
import struct
from typing import Iterator  # noqa: UP035
from unittest.mock import Mock, patch

import pytest

from firestarter.config import ConfigManager
from firestarter.constants import COMMAND_READ_VPE
from firestarter.hardware import HardwareManager
from firestarter.messages import MSG_END_DONE

from .conftest import build_frame
```

**Local frame helpers + the `hw_config` fixture** (`:31-48`) — `hw_config` is local to this file,
NOT in conftest:

```python
def _ok_frame_bytes() -> bytes:
    """A text-line 'OK: ...' frame the SerialCommunicator parser will see."""
    return b"OK: ready\n"


def _error_frame_bytes() -> bytes:
    """A text-line 'ERROR: ...' frame the parser will surface as a failure path."""
    return b"ERROR: simulated\n"


@pytest.fixture
def hw_config(tmp_path, monkeypatch) -> Iterator[ConfigManager]:
    """Fresh ConfigManager rooted in tmp_path (no ~/.firestarter pollution)."""
    monkeypatch.setattr("firestarter.config.HOME_PATH", str(tmp_path))
    ConfigManager._instances.clear()
    ConfigManager._initialized_configs.clear()
    yield ConfigManager(config_filename="t_hw.json")
```

**Happy-path leg to mirror** (`:51-63`) — the exact three-fixture signature, feed-then-build-then-patch
order:

```python
def test_get_hardware_revision_happy_path(hw_config, make_comm, fake_serial) -> None:
    """get_hardware_revision succeeds when find_and_connect returns a comm
    that yields an OK ack frame."""
    fake_serial.feed(_ok_frame_bytes())  # The expect_ack() inside picks this up
    fake_serial.feed(MSG_END_DONE.to_bytes(1, "big"))  # any trailing byte is fine
    comm = make_comm()

    hw = HardwareManager(hw_config)
    with patch(
        "firestarter.serial_comm.SerialCommunicator.find_and_connect",
        return_value=comm,
    ):
        ok = hw.get_hardware_revision()
    assert ok is True
```

For PROV-02's one-connection assertion, bind the patch (`as mock_fac`) and assert
`mock_fac.call_count == 1`; `comm` here is a real `SerialCommunicator` instance built via `__new__`,
so `disconnect()` cannot be `assert_called_once()` directly — wrap it
(`comm.disconnect = Mock(wraps=comm.disconnect)`) or assert on the mocked-factory call count plus a
`patch.object(comm, "disconnect")`. `Mock` and `patch` are already imported at `:18`.

**Transport-error leg to mirror** (`:66-77`) — note the function-local exception import, the
established idiom for D-04 leg 2 / F-17:

```python
def test_get_hardware_revision_failure_path(hw_config, make_comm, fake_serial) -> None:
    """get_hardware_revision returns False when find_and_connect raises
    a transport-level error."""
    from firestarter.exceptions import ProgrammerNotFoundError

    hw = HardwareManager(hw_config)
    with patch(
        "firestarter.serial_comm.SerialCommunicator.find_and_connect",
        side_effect=ProgrammerNotFoundError("no port"),
    ):
        ok = hw.get_hardware_revision()
    assert ok is False
```

**`make_comm` fixture — the identity default that gives the absent case for free**
(`tests/conftest.py:200-235`). **[DRIFT]** the prompt says `conftest.py:225`; the
`firmware_identity = None` assignment is at **`:225`** — confirmed exact, and it carries a
fail-closed rationale comment:

```python
@pytest.fixture
def make_comm(fake_serial):
    """Factory: build a SerialCommunicator wired to the fake serial port.

    Uses `__new__` to bypass `__init__` (which would try to open a real
    serial.Serial). Per PATTERNS §"firestarter_app/tests/test_decoder.py".
    """
    from firestarter.serial_comm import SerialCommunicator

    def _factory():
        instance = SerialCommunicator.__new__(SerialCommunicator)
        instance.connection = fake_serial
        instance.port_name = "/dev/null"
        ...
        # CAP-02: firmware identity + effective HW revision, both carried in the
        # MSG_OK_READY ack. None until probed — and None is a REJECT for the
        # shield-revision gate, so a fixture that forgets these fails closed.
        instance.firmware_identity = None
        instance.hw_revision = None
```

Consequences for the five W-1 legs: the **default `make_comm()` already yields the identity-absent
case**; a populated-identity leg sets `comm.firmware_identity = "3.0.0b19:leonardo"` after building;
the D-07 scrub leg sets it to a U+FFFD-bearing string. `instance.hw_revision = None` on the next line
is the CAP-02 **u8**, not the revision string — P-7's confusable pair, visible right here.

---

### `tests/test_dev_test_cmd.py` (test handler, end-to-end) — W-5, 41 dependents

**Analog:** its own `make_hardware_manager`, verified at `:372-401`:

```python
def make_hardware_manager(
    vpp_values: object = 12000,
    vpe_values: object = 5000,
    hw_revision: object = "Rev 2.0-class",
) -> Mock:
    """A Mock(spec=HardwareManager) with canned sample_vpp_mv/sample_vpe_mv/
    read_hardware_revision_value.

    D-10: this builder's `Mock` return type is deliberate too -- see
    `make_clean_operator` above and tests/conftest.py's `make_app_context`
    docstring for the reasoning.

    A plain int makes every call return the same value (return_value); a
    list makes each successive call return the next value (side_effect) ...
    """
    hw = Mock(spec=HardwareManager)
    if isinstance(vpp_values, list):
        hw.sample_vpp_mv.side_effect = vpp_values
    else:
        hw.sample_vpp_mv.return_value = vpp_values
    if isinstance(vpe_values, list):
        hw.sample_vpe_mv.side_effect = vpe_values
    else:
        hw.sample_vpe_mv.return_value = vpe_values
    hw.read_hardware_revision_value.return_value = hw_revision
    return hw
```

W-5's change: a sibling `fw_board_identity: object = "3.0.0b19:leonardo"` parameter, and the last
wiring line becomes
`hw.read_programmer_identity.return_value = ProgrammerIdentity(hw_revision=hw_revision, fw_board_identity=fw_board_identity)`
— a **real NamedTuple**, never a bare `Mock` (RESEARCH: the NamedTuple's field names are not
spec-protected, so a `MagicMock` return leaks a child mock into the report). Default-argument
signature preserved so all 41 `runner.invoke(cli, ["dev", "test", …])` sites keep working; D-08 and
D-13(b) vary exactly one field. The docstring prose at `:378` is reworded.

**End-to-end leg to mirror** (`:730-743`, verbatim — this is the analog for both D-08 and D-13(b),
because it already asserts the rendered output AND the saved artifact):

```python
    def test_hw_revision_auto_captured_end_to_end(self, runner: CliRunner) -> None:
        """The mocked hardware manager's read_hardware_revision_value() flows
        through to the rendered report and the .json artifact (Phase 112
        Plan 04 auto-capture wiring, end-to-end)."""
        app = make_app_context(
            eprom_operator=make_clean_operator(),
            hardware_manager=make_hardware_manager(hw_revision="Rev 2.0-class"),
        )
        with _off_tty():
            result = runner.invoke(cli, ["dev", "test", _CHIP_NO_ID], obj=app)
        assert result.exit_code == 0, result.output
        assert "Rev 2.0-class" in result.output
        data = _load_report(_CHIP_NO_ID)
        assert data["auto_capture"]["hw_revision"] == "Rev 2.0-class"
```

Supporting helpers in the same file: `_off_tty()` `:409-411`
(`patch("firestarter.cli_handlers._is_interactive", return_value=False)`), `runner` fixture
`:404-406`, `_load_report(chip) -> dict` `:418`.

**The load-bearing negative assertion that must follow the rename** (`:825-846`) — with its
docstring, which names the assertion as load-bearing and explains why an exit-code check would not do:

```python
        """`NO_SUCH_CHIP_XYZ` is absent from the DB (get_eprom is falsy).
        `dev test` must exit 1 with the bare `Error: ... not found in
        database` message and short-circuit BEFORE any hardware read /
        operator call -- proven by
        read_hardware_revision_value.assert_not_called() (the load-bearing
        assertion: the always-writes notice still prints first, per
        test_always_writes_notice_is_the_first_line_unconditionally, so a
        bare "no output before the error" check would no longer prove
        anything)."""
        chip = "NO_SUCH_CHIP_XYZ"
        app = make_app_context(
            eprom_operator=Mock(spec=EpromOperator),
            hardware_manager=Mock(spec=HardwareManager),
        )
        with _off_tty():
            result = runner.invoke(cli, ["dev", "test", chip], obj=app)
        assert result.exit_code == 1, result.output
        assert f"{chip}: not found in database" in result.output
        app.hardware_manager.read_hardware_revision_value.assert_not_called()
        app.eprom_operator.read_eprom.assert_not_called()
```

**[VERIFIED]** `:845` is the `assert_not_called()` line, as RESEARCH F-11 states. Rename it AND keep
the docstring naming it. Also `:863` `hw.read_hardware_revision_value.assert_called()` in
`test_dev_test_present_but_unsupported_still_sweeps`.

Why a miss cannot go silently green: every double is `Mock(spec=HardwareManager)` (here `:391`,
conftest `:314`, and 20+ further sites), which raises `AttributeError` on a name the spec lost.
**Do not weaken any of those to a bare `Mock()`** (P-2).

---

### `tests/test_diagnostic_report.py` (test render, transform) — D-13(a)

**Analog:** the `sdp_hold_state` both-surfaces pair — the established non-vacuous console oracle.

**The helper** (`:967-969`, verbatim):

```python
def _rendered_text(table) -> str:
    cells = [str(cell) for column in table.columns for cell in column.cells]
    return " ".join(cells)
```

**[DRIFT]** the prompt/RESEARCH say `:965`; the `def` is at **`:967`** (`:955-965` is the
Evidence-Ceiling comment block that precedes it — itself a pattern worth copying for any new test
block in this file).

**The both-surfaces leg to mirror** (`:972-985`):

```python
def test_hold_state_held_reaches_both_surfaces():
    """`SDP_HOLD_HELD` (the inhibited write was correctly refused) appears
    verbatim in to_dict()["sdp_hold_state"] AND in render()'s output text --
    LEG-12 requires both surfaces, and D-07 is why: render()'s per-step row
    never shows `reason`, so the hold state needs its own row to be visible
    to a terminal reader at all."""
    report = _minimal_report()
    report.sdp_hold_state = SDP_HOLD_HELD

    d = report.to_dict()
    assert d["sdp_hold_state"] == SDP_HOLD_HELD

    table = report.render()
    assert SDP_HOLD_HELD in _rendered_text(table)
```

Shape to copy: build via `_minimal_report()`, mutate one field, assert on `to_dict()` **and** on
`_rendered_text(report.render())`. For D-10 the JSON assertion inverts —
`assert report.to_dict()["auto_capture"]["fw_board_identity"] is None` while the marker appears in
the table.

**`_minimal_report` — and the reason a null-identity fixture needs no new parameter**
(`:145-193`): its `AutoCapture(...)` passes only `host_version`, `chip`, `protocol`:

```python
def _minimal_report(
    *,
    chip: str = "M8720",
    protocol: str = "0x08",
    host_version: str = "3.0.0b10",
    step_specs: list[tuple[str, str, str | None, str]] | None = None,
    vpp_before_mv: int | None = None,
    vpe_before_mv: int | None = None,
):
    """Directly-constructed DiagnosticReport (no derive_plan/run_plan) for
    precise dedup_fingerprint test control over step shape. ..."""
    from firestarter.diagnostic_report import (
        AutoCapture,
        DiagnosticReport,
        TransportHealth,
    )
    ...
    auto_capture = AutoCapture(
        host_version=host_version,
        chip=chip,
        protocol=protocol,
    )
    return DiagnosticReport(
        auto_capture=auto_capture,
        transport=TransportHealth(),
        plan=Plan(name=chip),
        results=results,
        vpp_before_mv=vpp_before_mv,
        vpe_before_mv=vpe_before_mv,
    )
```

So `_minimal_report()` **already yields `fw_board_identity=None` and `hw_revision=None`** — D-13(a)
needs no fixture change at all, only a new test. Note the keyword-only signature and the
function-local `from firestarter.diagnostic_report import …`.

---

### `tests/test_parse_devtest_issue.py` (test parser) — W-2, W-3, and the marker-parity assert

**Analog A — the import block that makes the parity assert legal** (`:37-56`, verbatim). This is the
one place in the repo that legitimately imports **both** worlds:

```python
from __future__ import annotations

import json

from firestarter.chip_test import VERDICT_OK, Plan, StepResult
from firestarter.database import EpromDatabase
from firestarter.diagnostic_report import (
    SCHEMA_VERSION,
    AutoCapture,
    DiagnosticReport,
    TransportHealth,
    build_db_diff,
)
from firestarter.submit import build_body, build_title, sanitize_dict
from tools.parse_devtest_issue import (
    _MAX_BODY_BYTES,
    count_agreeing,
    extract_db_diff,
    parse_devtest_body,
)
```

W-2 adds `render_diff` to the `tools.parse_devtest_issue` group (alphabetical: after
`parse_devtest_body`). The parity assert imports the app-side marker from the
`firestarter.diagnostic_report` group and the parser-side marker from the `tools` group. The skill
script's third literal is **not** importable — its parity is covered by the W-4 human-verify, not by
this test.

**Analog B — the frozen fixture shape for W-3** (`:355-374`, head of a `:361-454` literal). Note the
explicit never-regenerate instruction:

```python
_B11_TITLE = "[dev test] M8720 — PASS (b11deadbeef)"

# Frozen `3.0.0b11` artifact shape -- schema_version "1.1", the six original
# op strings only (id/read/blank-check/write/verify/erase), NO
# "write-partial". Must never be regenerated from live `to_dict()` output --
# the whole point is pinning a shape this codebase can no longer produce.
_B11_BODY = (
    "| Step | Verdict | Reason |\n"
    "| ---- | ------- | ------ |\n"
    "| id | OK | chip id matched |\n"
    "| write | OK |  |\n"
    "| verify | OK |  |\n"
    "\n```json\n"
    + json.dumps(
        {
            "schema_version": "1.1",
            "generated": "2026-05-01T12:00:00Z",
            "auto_capture": {
                "host_version": "3.0.0b11",
                "fw_board_identity": "3.0.0b11:leonardo",
                "hw_revision": "Rev 2.0-class",
                "chip": "M8720",
                "protocol": "0x08",
                "chip_id_expected": 4660,
                "chip_id_actual": 4660,
                "chip_id_mismatch_reason": None,
```

**[VERIFIED]** `fw_board_identity` here is **populated** (`"3.0.0b11:leonardo"`), which is why W-3
needs a *second* frozen fixture carrying `fw_board_identity: null`. Copy the construction idiom
exactly: markdown table string `+ json.dumps({...}, indent=2) + "\n```"`, module-level `_`-prefixed
constant, a comment stating why it must never be regenerated.

**Analog C — the assertion style for a frozen-fixture back-compat leg** (`:456-478`):

```python
def test_legacy_vocabulary_b11_body_still_parses():
    """A literal, hand-written `3.0.0b11` body -- schema_version "1.1", six
    original op strings, a dedup_fingerprint -- is accepted by
    parse_devtest_body with the `[dev test]` title marker, and its fields
    are readable (D-06 back-compat)."""
    obj = parse_devtest_body(_B11_TITLE, _B11_BODY)

    assert obj is not None
    assert obj["schema_version"] == "1.1"
    assert obj["auto_capture"]["chip"] == "M8720"
    ...
    assert obj["dedup_fingerprint"] == "b11deadbeef"

    diff = extract_db_diff(obj)
    assert diff["ladder_state"] == "community-reported"
```

The W-3 leg adds `assert obj["auto_capture"]["fw_board_identity"] is None` and (for PROV-06) feeds
the same object to `render_diff` asserting the marker + not-attributable clause.

**Analog D — presence-only forward compat, the fixture D-17 must survive** (`:134-143`):

```python
def test_detect_schema_version_matched_by_presence_not_exact_value():
    """A future schema bump (e.g. 1.0 -> 1.1 -> 1.2) must not break
    detection -- only PRESENCE of the key is checked (D-04)."""
    title, _body = _build_realistic_title_body()
    body = '```json\n{"schema_version": "9.9-future", "auto_capture": {}}\n```'
    obj = parse_devtest_body(title, body)

    assert obj is not None
    assert obj["schema_version"] == "9.9-future"
```

**[DRIFT]** the prompt/RESEARCH cite `"9.9-future"` at `:138`; it is at **`:138`** — confirmed.
Any schema-version *ordering* logic would have to survive this string. Don't add any (D-17).

---

## Shared Patterns

### The three marker literals — why D-11 resolves to three insertion sites, side by side

D-11 asks for a single-sourced constant. Architecture forbids it. The three sites, with the barrier
between each:

| # | File | Insertion site (verified) | Why it cannot import the others |
|---|------|---------------------------|---------------------------------|
| 1 | `firestarter/diagnostic_report.py` | beside `NOT_MEASURED = "not measured"` at **`:85`**, consumed by `render()`'s rows at `:517-518` | canonical home — but `diagnostic_report.py` is orchestrator-only by contract and imports no transport class |
| 2 | `tools/parse_devtest_issue.py` | module-level, above `render_diff` (`:192`), consumed inside it | **"Stdlib-only CLI"** — stated in the module docstring at `:9-11`. Any `from firestarter …` line breaks the contract. Also outside ruff/mypy scope, so nothing would catch a drifted literal |
| 3 | `/workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py` | module-level, consumed in `cmd_show`'s print block (`:332-333`) | **"Skills own their scripts"** — and it lives in a *different repo* (meta), not importable from the app package at all |

Enforcement substitute (Pattern 3, RESEARCH): a one-line equality `assert` in
`tests/test_parse_devtest_issue.py`, the only file already importing both #1 and #2 (see Analog A
above). Site #3's parity is covered by the W-4 `checkpoint:human-verify` — an app-repo test reaching
into `/workspaces/.claude/` would fail **open** in standalone CI.

### Trap 1 (HIGH) — a new `_`-helper in `cli_handlers.py` turns three files RED

**Source:** `tests/test_check_devtest_orchestrator.py:550-611`. The expected set, verified verbatim
at `:550-558`:

```python
_EXPECTED_DEV_TEST_REFERENCED_HELPERS = {
    "_chip_id_fields",
    "_dev_test_exit_code",
    "_is_interactive",
    "_make_sampler",
    "_resolve_write_scope",
    "_sanitize_chip_token",
    "_sdp_recovery_line",
}
```

and the **hard-equality** assertion at `:607-611`:

```python
    assert derived == _EXPECTED_DEV_TEST_REFERENCED_HELPERS, (
        f"the body-only derivation returned {sorted(derived)}, expected "
        f"exactly {sorted(_EXPECTED_DEV_TEST_REFERENCED_HELPERS)}. If this "
        f"is a legitimate new dev_test helper, list it in "
```

⚠ Note the *docstring* of this same test (`:576-581`) claims the assertion "is a SUBSET, never an
equality". **The docstring is stale — the code asserts equality.** A planner reading only the
docstring would mis-scope the trap.

Two guards precede it and are also worth copying wherever a derived set is asserted (`:590-605`):
a non-vacuity `assert derived, …` and a `assert len(derived) >= 6, …` floor.

**Consequence:** adding any `_`-prefixed module-level callable in `cli_handlers.py` referenced from
`dev_test`'s body requires three files in one commit (`cli_handlers.py`,
`tools/check_devtest_orchestrator.py::_HANDLER_FUNCTION_NAMES`, and this expected set).
**Apply to:** the `cli_handlers.py` plan — its diff must add **zero** `def` lines. All new callables
go in `hardware.py` (scrub) and `diagnostic_report.py` (marker cell).

### Trap 2 — the meta-repo `.gitignore` precondition (F-14, verified)

`git ls-files .claude` returns **empty** (nothing tracked), and the un-ignore is **uncommitted** —
present only in the working tree:

```diff
-.claude/
+# Everything under .claude/ is local runtime state (settings, gsd-core, channels,
+# worktrees) EXCEPT hand-authored skills, which are project tooling and are shared.
+.claude/*
+!.claude/skills/
+.claude/skills/*/scripts/__pycache__/
+# find-skills is marketplace-installed (carries source.json — reinstall, don't vendor).
+.claude/skills/find-skills/
```

**Apply to:** any plan touching the skill script or SKILL.md. That hunk must land (or `git add -f`)
or the files cannot be committed. The meta tree is dirty (`.gitignore`, both submodule gitlinks,
untracked `.claude/`, `package*.json`) — **stage named paths, never `git add -A`**.

### Error handling / honest-fallback convention

**Source:** `hardware.py:107-113` and `:141-147` — one `except (ProgrammerNotFoundError, SerialError,
SerialTimeoutError) as e:` clause, `logger.error(f"Failed to read hardware revision: {e}")`, then an
honest sentinel return, with teardown in `finally`. **Apply to:** the widened
`read_programmer_identity`. Keep the tuple exactly (F-17), and return
`ProgrammerIdentity(None, None)` — never a bare `None`, which every caller and the `Mock(spec=…)`
doubles would silently accept.

### Null-rendering convention

**Source:** `diagnostic_report.py:85` (`NOT_MEASURED = "not measured"  # D-03: honest fallback,
never a false 0`) and the correct `is not None` guard already in the skill script at `:340`.
**Anti-source:** `str(ac[...])` at `diagnostic_report.py:511-512` and
`auto.get("host_version") or "?"` at the skill script `:185`.
**Apply to:** all three render surfaces. Branch on `is None`; never `str()`, never `or`.

### Test-run commands (from RESEARCH §Validation Architecture — copy verbatim into verify blocks)

- Quick: `cd /workspaces/firestarter_app && python3 -m pytest tests/test_dev_test_cmd.py tests/test_diagnostic_report.py tests/test_parse_devtest_issue.py tests/test_hardware.py tests/test_provenance.py tests/test_submit.py tests/test_check_devtest_orchestrator.py tests/test_check_diagnostic_report_claims.py -o addopts="" -q`
- Full: `cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts="" -q`
- Gates: `python3 tools/check_devtest_orchestrator.py` and `python3 tools/check_diagnostic_report_claims.py` (both measured `EXIT=0` today)
- CI-scoped lint: `ruff check firestarter/ tests/` && `ruff format --check firestarter/ tests/` — **`tools/` and `.claude/skills/` are NOT linted or type-checked**

`-o addopts=""` is mandatory: the project sets `addopts = "-ra -q"`, and a second `-q` suppresses the
count line. Write `&&` as literal ASCII in `<automated>` blocks — never `&amp;&amp;`.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tests/test_parse_devtest_issue.py::render_diff` tests (W-2) | test (render) | transform | **`render_diff` has zero tests anywhere in the repo** — verified: `grep -rn render_diff` returns only the def (`tools/parse_devtest_issue.py:192`) and its one call site (`:251`). No plain-text-render test exists for this module. **Nearest usable analog:** `tests/test_diagnostic_report.py`'s `_rendered_text` + both-surfaces pair (§`test_diagnostic_report.py` above) — but `render_diff` returns a `str`, so the assertion is a direct substring check on the return value, with no `_rendered_text` indirection. Assert on **behaviour, not types** (`tools/` is outside mypy scope). |
| Skill-script render harness (W-4) | test | transform | No test harness of any kind exists for `.claude/skills/**/scripts/`. Building one in the app repo would reach across repos and **fail open** in standalone CI. Use a `checkpoint:human-verify` with two committed fixture bodies (populated + null) and the offline `show --body-file` commands, plus a diff of `SKILL.md:61-67` against the new output. Do not claim it as automated. |

---

## Metadata

**Analog search scope:** `/workspaces/firestarter_app/firestarter/`, `/workspaces/firestarter_app/tools/`,
`/workspaces/firestarter_app/tests/`, `/workspaces/.claude/skills/devtest-triage/`, `/workspaces/.gitignore`.
`firestarter/` (firmware) treated as read-only reference and **not** searched for analogs — no firmware
file is modified by this phase.
**Files opened this session:** 12 (`hardware.py`, `cli_handlers.py`, `diagnostic_report.py`,
`frame_vectors.py`, `tools/parse_devtest_issue.py`, `tests/conftest.py`, `tests/test_hardware.py`,
`tests/test_dev_test_cmd.py`, `tests/test_diagnostic_report.py`, `tests/test_parse_devtest_issue.py`,
`tests/test_check_devtest_orchestrator.py`, skill `devtest_issues.py` + `SKILL.md`).
**Pattern extraction date:** 2026-08-18
**Read-only:** no source file was modified; this file is the only write.
