# Phase 132: Retire `dev sdp` & Discharge the mypy Debt - Pattern Map

**Mapped:** 2026-08-03
**Files analyzed:** 14 (2 created, 1 moved, 11 modified)
**Analogs found:** 13 / 14
**Sub-repo HEAD verified:** `firestarter_app` @ `8caf77f`, branch `gsd/v1.30-sdp-surface-retirement`

> **Path convention.** Every `firestarter/…`, `tests/…`, `tools/…`, `pyproject.toml`,
> `.github/…` path below is relative to `/workspaces/firestarter_app/`. The one exception is
> `.planning/REQUIREMENTS.md`, which is the meta-repo at `/workspaces/.planning/REQUIREMENTS.md`.
> All line numbers below were **re-measured this session** against `8caf77f` (CONTEXT.md's D-11
> warning honoured); where they differ from CONTEXT.md the measured value is flagged.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/sdp_honesty.py` (new) | utility / pure message-text carrier | transform (pure fn) | `firestarter/sdp_capability.py` | role-match |
| `tools/<ci-replica-venv>.sh` (new) | tooling script | batch | `tools/ci_parity.sh` | role-match (style only — D-07 forbids folding) |
| `tests/test_sdp_honesty.py` (from `tests/test_dev_sdp_cmd.py`) | test | request-response (CliRunner) | itself (git mv) + `tests/test_write_skip_sdp_unlock.py` | exact |
| `tools/check_no_exists_proxy.py` | config (fail-closed target list) | batch | itself, `:125-…` literal list | exact |
| `firestarter/cli_handlers.py` (delete `dev sdp` span) | controller (Click) | request-response | sibling `@dev.command(name="test")` `:2055` | exact |
| `tests/conftest.py` (typed factory + fixture) | test fixture / factory | transform | `tests/test_dev_test_cmd.py:84` + `conftest.py`'s `make_comm` `:171` | exact |
| `firestarter/cli_handlers.py` (D-14 tripwire comments) | controller | request-response | the existing D-04/D-18 comment blocks `:620-645` | exact |
| `firestarter/constants.py` | config / constants | n/a | itself `:67-97`, `:121` | exact |
| `firestarter/eprom_operations.py` (comment text only) | service | request-response | **RING-FENCED** — see §Ring-fence | n/a |
| `tests/test_revision_constants_parity.py` (4 stale refs) | test (parity) | transform | itself | exact |
| `tests/test_write_skip_sdp_unlock.py` (tripwire test + fixture migration) | test | request-response | its own existing tests `:157-274` | exact |
| `tests/__snapshots__/test_characterization.ambr` | test snapshot | n/a | itself `:124-146` | exact |
| `pyproject.toml` | config | n/a | itself `:161-207` | exact |
| `.planning/REQUIREMENTS.md` (RETIRE-08 text) | doc | n/a | — | no analog (prose edit) |

---

## Pattern Assignments

### `firestarter/sdp_honesty.py` — NEW (utility, pure transform)

**Analog:** `firestarter/sdp_capability.py` (281 lines) — the only existing *pure, importless,
strict-island* helper module in `firestarter/`. Copy its **shape**, not its content (D-02 forbids
extending it).

**Import-purity pattern** (`sdp_capability.py:45-52`) — the load-bearing convention: a lettered
provenance docstring, then a comment that states the module's import-set invariant explicitly:

```python
from __future__ import annotations

# D-03 purity (Task 2): the module's top-level import set is a subset of
# {"__future__", "typing"} — no click, no serial, no firestarter.* imports.
from typing import Any, Mapping  # noqa: UP035
```

`sdp_honesty.py` should state the same invariant for itself. Note the forward contract in
CONTEXT.md §Integration points: Phase 134's leg rows and Phase 135's `--sdp-relock` import this, so
it must not import `click` (the caller does the `click.echo`).

**Return-shape pattern** (`sdp_capability.py:201-203`, `:266`) — `-> tuple[bool, str]` message
tuples, and a thin name-keyed wrapper delegating to an entry-keyed pure core:

```python
def sdp_capability_for_entry(
    entry: Mapping[str, Any] | None, display_name: str
) -> tuple[bool, str]:
```

```python
def sdp_capability(chip_name: str, db: Any) -> tuple[bool, str]:
    """..."""
    return sdp_capability_for_entry(db.get_eprom(chip_name), chip_name)
```

**The three honesty strings to relocate** — verbatim from the span being deleted,
`cli_handlers.py:2312-2316` (CONTEXT.md said `:2316-2318`; measured `:2315-2319`):

```python
        click.echo(
            f"SDP {mode} sequence for {chip_upper} was emitted. The "
            "resulting protection state cannot be read back on this chip "
            "family, so this is not a claim about the chip's actual state."
        )
```

The three greppable tokens the four tests key on are `was emitted` (`:2316`),
`cannot be read back` (`:2317`), `not a claim about the chip's actual state` (`:2318`). Keep all
three in the relocated string or the surviving assertions go RED.

**The mechanical-enforcement comment to relocate** (`cli_handlers.py:2301-2311`) — this is the
rationale the no-fabricated-duration test cites; it must travel with the string:

```python
        # D-10 summary line -- honest and symmetric on both directions: the
        # claim is that the sequence was EMITTED, never that the resulting
        # state was verified. No duration figure appears here -- this is
        # mechanically enforced, not merely a discipline: get_response()
        # filters the entire INFO band out at serial_comm.py:424, so the
        # operation layer literally cannot see the firmware's `0x5F`/`0x61`
        # duration frame to plumb one through. No lock/unlock state boolean
        # appears either -- HOST-05's honesty floor.
```

**The D-14 unknown-command mapping to relocate** (`cli_handlers.py:2280-2299`) — comment + arm:

```python
    # Serial call. D-14: an `EpromOperationError` whose `error_code` is
    # `MSG_ERR_UNKNOWN_CMD` means the attached firmware predates
    # CMD_SDP_LOCK/CMD_SDP_UNLOCK (Phase 119) and does not recognise this
    # command at all. ... Keyed on the message **id**, never the message text.
    try:
        ...
    except EpromOperationError as e:
        if e.error_code == MSG_ERR_UNKNOWN_CMD:
            raise FirmwareOutdatedError(
                f"{chip_upper}: attached firmware does not implement SDP "
                f"{mode} (unknown command) -- upgrade with "
                "'firestarter fw --install'."
            ) from e
        raise
```

The surviving test asserts on `"firestarter fw --install"` and
`"outdated" or "does not implement"` — both must remain in the relocated wording. If the helper is
importless-of-`click`, the natural shape is a raiser/mapper the caller wraps, e.g.
`map_unknown_cmd(exc, mode, chip_upper) -> FirmwareOutdatedError | None`, importing only
`firestarter.exceptions` + `firestarter.messages` (both leaf modules).

**pyproject strict-island registration** (`pyproject.toml:175-189`) — the list D-02 extends:

```toml
[[tool.mypy.overrides]]
# Phase 42 D-06: strict-island for the 8 modules touched in v1.8.
# eprom_operations.py DELIBERATELY EXCLUDED per D-07 (GATE-1.8d read-path ring-fence; ...).
module = [
    "firestarter.main",
    "firestarter.cli_handlers",
    ...
    "firestarter.serial_comm",
]
disallow_untyped_defs = true
check_untyped_defs = true
```

⚠ `firestarter.sdp_capability` is **not** in this list today — verify at plan time whether the
existing strict island covers it, because "the strict-island module list" D-02 names is this
Phase-42 block and adding `firestarter.sdp_honesty` here means `disallow_untyped_defs = true`
(every function needs a return annotation).

---

### `tools/<ci-replica-venv>.sh` — NEW (tooling script, batch)

**Analog:** `tools/ci_parity.sh` (162 lines, shipped 9 commits ago as `8caf77f`). Copy structure
only; D-07 forbids folding into it.

**Header pattern** (`ci_parity.sh:1-56`) — a `# tools/<name>.sh -- <purpose> (GATE-id, phase, D-refs).`
first line, then all-caps section headings inside the comment block:
`WHAT THIS IS FOR`, `WHAT THIS DELIBERATELY DOES NOT MIRROR`, `WHY … IS NOT A LEG`,
`LEG 4'S EXPECTED LOCAL EXIT 2`, and finally an explicit `Exit codes:` contract:

```bash
# Exit codes: 0 if every leg passed; non-zero (naming the failing legs) if
# any leg failed. This script never aborts early on a single failing
# command (deliberately not a strict-abort-on-error shell mode) and never
# swallows a leg's exit code -- all four legs always run, and the final
# summary prints each one.
```

**Root anchoring pattern** (`:58-73`) — `set -u` (never `set -e`, deliberately), resolve the repo
root from `BASH_SOURCE`, `mktemp -d` + `trap cleanup EXIT`:

```bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"
cd "${REPO_ROOT}" || { echo "FATAL: cannot cd to repo root ${REPO_ROOT}"; exit 2; }

TMPROOT="$(mktemp -d)"
cleanup() { rm -rf "${TMPROOT}"; }
trap cleanup EXIT
```

**Per-leg banner + non-swallowing exit capture** (`:75-99`):

```bash
banner() {
  echo "---------------------------------"
  echo "Leg ${1}: ${2}"
  echo "Proves: ${3}"
  echo "---------------------------------"
}

banner 1 "FIRESTARTER_FW_ROOT=<empty dir> python3 -m pytest tests/ -q" \
  "the suite passes with the firmware sibling absent -- the standalone-CI condition."
FIRESTARTER_FW_ROOT="${TMPROOT}" python3 -m pytest tests/ -q
LEG1_EXIT=$?
echo "Leg 1 exit code: ${LEG1_EXIT}"
```

**Summary + board stamp + aggregate exit** (`:124-162`) — copy verbatim in shape, including the
`BOARD-ATTACHED:` and `Python:` stamp lines (this phase's venv script should additionally stamp the
resolved **mypy version** and prove `numpy` is absent from the venv, since that is its whole point):

```bash
echo "BOARD-ATTACHED: ${BOARD_STAMP}"
echo "Python: $(python3 -V 2>&1)"
...
if [ -z "${FAILED_LEGS}" ]; then
  echo "CI-PARITY: PASS"; exit 0
else
  echo "CI-PARITY: FAIL (legs:${FAILED_LEGS})"; exit 1
fi
```

**What the new script must reproduce from CI** (`.github/workflows/ci.yml:33-36`, `:60-70`):
Python **3.11**, `pip install -e .[test]`, then `python tools/check_mypy_watermark.py`. The
watermark gate's pure functions are directly importable (no subprocess needed):
`tools/check_mypy_watermark.py` exposes `get_watermark()` `:91`, `mypy_argv()` `:106`,
`run_mypy()` `:118`, `classify_mypy_result(returncode, output) -> int` `:133`,
`enforce_watermark(count, watermark)` `:211`, `main()` `:229`, with
`MIN_CHECKED_SOURCE_FILES = 120` at `:48` and `REPO_ROOT` at `:41`.

---

### `tests/test_dev_sdp_cmd.py` → `tests/test_sdp_honesty.py` (test, request-response)

**Analog:** itself (`git mv`, 558 lines). The four survivors, re-measured:

| Test | Line | Asserts on |
|------|------|-----------|
| `test_summary_line_carries_the_unreadable_state_caveat_on_both_directions` | **:395** | `"cannot be read back"` in **both** enable and disable output |
| `test_summary_line_carries_no_duration_figure` | **:423** | `not re.search(r"\d+\s*(us\|µs\|ms\|s)\b", summary_line)` |
| `test_no_fabricated_lock_state_boolean_in_the_report` | **:453** | three asserts: `"was emitted"`, `"cannot be read back"`, `"not a claim about the chip's actual state"` |
| `test_firmware_too_old_is_reported_when_unknown_cmd_comes_back` | **:513** | `"firestarter fw --install"` + (`"outdated"` or `"does not implement"`) |

**The line-selection idiom the first three share** (`:445-450`, `:471-473`) — the assertions are
scoped to the host's own summary line, never the whole capture. Any retarget onto the helper must
preserve this scoping (it is why the test survives a firmware INFO frame in the buffer):

```python
    summary_line = next(
        line for line in result.output.splitlines() if "was emitted" in line
    )
    assert "was emitted" in summary_line
    assert "cannot be read back" in summary_line
    assert "not a claim about the chip's actual state" in summary_line
```

**The D-14 test's mock shape** (`:521-536`):

```python
    operator = Mock(spec=EpromOperator)
    operator.sdp_lock.side_effect = EpromOperationError(
        "Unknown command: 9", error_code=MSG_ERR_UNKNOWN_CMD
    )
    app = make_app_context(eprom_operator=operator)
```

**Module-docstring pattern to keep** (`:1-22`) — the FALSE-GREEN TRAP paragraph and the
`_is_interactive`-patching rationale. After the deletion the `_off_tty()` / `_on_tty()` helpers
(`:110-117`) become dead if the new SUT is a pure helper — **prune them with the gate tests**, and
count the pruning per D-04.

**Cases pruned per D-04 (count and name them in the record):** the surface-shape test `:125`, the
gate-ordering cases up to `:388` (absent chip, capability refusal, the nine adapter-required parts,
`Confirm.ask` prompt, `-y` bypass, TTY refusal), `test_tblc_warn_prints_at_warning…` `:479`, and
`test_success_exit_zero_and_failure_exit_one` `:539`. Existing coverage that makes this safe is in
§Shared Patterns → "Coverage that already exists".

**Same-commit gate edit** — `tools/check_no_exists_proxy.py:157` (CONTEXT.md's anchor **confirmed
exact**). The entry shape is a bare relative-path string inside a comprehension over a tuple:

```python
_DEFAULT_TARGETS = [
    os.path.join(_APP_ROOT, rel)
    for rel in (
        "tests/__init__.py",
        "tests/conftest.py",
        ...
        "tests/test_dev_sdp_cmd.py",     # <-- :157, becomes "tests/test_sdp_honesty.py"
        ...
```

The list is kept alphabetically sorted, so `test_sdp_honesty.py` moves position, not just text —
the rename is a delete + insert, not an in-place edit. `_HERE`/`_APP_ROOT` anchoring at `:113-116`
resolves locally (the `check_permitted_claims.py` trap does **not** apply here — verified).

---

### `firestarter/cli_handlers.py` — delete the `dev sdp` span (controller, request-response)

**Deletion boundary, re-measured:** `@dev.command(name="sdp")` at **:2196**,
`def dev_sdp(app: AppContext, eprom: str, mode: str, assume_yes: bool) -> None:` at **:2213**,
body runs to **:2321 = EOF**. It is the last function in the file. All CONTEXT.md anchors confirmed.

**Sibling registration pattern that bounds the deletion** — the preceding subcommand ends at
`:2193` (`sys.exit(code)`) inside `dev_test`, registered at:

```python
2055: @dev.command(name="test")
2059: def dev_test(app: "AppContext", chip: str) -> None:
```

Full `dev` subcommand roster (post-deletion must be 8, was 9):
`:1180 read`, `:1211 reg`, `:1273 addr`, `:1310 consistency-check`, `:1400 write-cycle`,
`:1453 fault-inject`, `:1680 validate-family`, `:2055 test`, ~~`:2196 sdp`~~.

**The four gates deleted with the command** — quote these in the record per D-04:

```python
2235:    if not app.db.get_eprom(eprom):          # Gate 1 -- absent chip
2244:    allowed, reason = sdp_capability(eprom, app.db)   # Gate 2 -- capability
2250:    eprom_data = resolve_chip(eprom, db=app.db)       # Gate 3 -- support status
2261:    interactive = _is_interactive()                   # Gate 4 -- consent
2262:    if interactive and not assume_yes:
2273:        proceed = Confirm.ask(prompt, default=False)
2277:    elif not interactive and not assume_yes:
2278:        raise click.ClickException(
2279:            f"{chip_upper}: refusing to run off a TTY without -y/--yes -- "
2280:            "pass -y to proceed unattended."
2281:        )
```

`-y/--yes` option decorator at `:2199-2210`. `Confirm.ask` at **:2273** (CONTEXT.md cited `:2267`,
which is inside the prompt *string*; the call is at **:2273**).

**Import-cleanup obligation:** after the deletion, check whether `Confirm`, `MSG_ERR_UNKNOWN_CMD`,
`FirmwareOutdatedError`, `sdp_capability`, `EpromOperationError` still have other users in
`cli_handlers.py` — `sdp_capability` **does** (`:625`, the auto-unlock block). `ruff check` select
`F` catches any that become unused, so leg 3 of `ci_parity.sh` is the proof.

---

### `firestarter/cli_handlers.py` — D-14 tripwire comment sites (controller)

**Anchors re-measured — all three confirmed:**

`:302` inside `_build_op_flags` (which starts at `:295`):

```python
def _build_op_flags(
    *,
    blank_check: bool = True,
    force: bool = False,
    verbose: bool = False,
    vpe_as_vpp: bool = False,
    skip_erase: bool = False,
    skip_sdp_unlock: bool = False,        # <-- :302
```

`:579` inside `def write(...)`:

```python
def write(
    app: AppContext,
    ...
    skip_sdp_unlock: bool,               # <-- :579  (a required param, not a default)
) -> None:
```

⚠ Correction to CONTEXT.md: `:579` is a **non-defaulted parameter** on `write`'s signature; only
`:302` is a `= False` default. The Click default lives on the option decorator above `write` —
locate it and consider it the third comment site.

**The auto-set / flag-independence block, `:622-645`** — this is the *decision* site D-14 names,
and the existing comment style to mirror (rationale-in-prose, decision-ID-tagged):

```python
    sdp_entry = app.db.get_eprom(eprom)
    is_protocol_0x0d = (
        bool(sdp_entry) and sdp_entry.get("protocol-id") == SDP_PROTOCOL_ID
    )
    allowed, sdp_reason = sdp_capability(eprom, app.db)
    if is_protocol_0x0d and not allowed and not skip_sdp_unlock:
        skip_sdp_unlock = True
        click.echo(
            f"{eprom.upper()}: auto-setting --skip-sdp-unlock on your behalf "
            ...
        )
    elif skip_sdp_unlock and not is_protocol_0x0d:
        # D-18 warn-and-proceed: the user asked for something vacuous on this
        # protocol. Do NOT refuse, do NOT abort, do NOT suppress the bit —
        # firmware never reads FLAG_SKIP_SDP_UNLOCK outside protocol 0x0D, so
        # nothing unsafe happens either way, ...
```

The tripwire comment goes adjacent to the `if is_protocol_0x0d and not allowed and not
skip_sdp_unlock:` decision, phrased as the criterion (D-14): *a developer changing the auto-unlock
default must read it by construction.*

---

### `tests/conftest.py` — typed `make_app_context` factory + `app_context` fixture

**Analog A — the factory body to type** (`tests/test_dev_test_cmd.py:84-107`, the canonical of the
five `**overrides: object` copies; `test_dev_sdp_cmd.py:80` and `test_write_skip_sdp_unlock.py:55`
are near-identical):

```python
def make_app_context(**overrides: object) -> AppContext:
    """Construct a minimal, hardware-free AppContext for `dev test` tests.

    Mirrors test_validate_family_cmd.py's make_app_context: EpromDatabase
    uses skip_local_override=True and every manager is Mock(spec=...) unless
    the caller overrides it. No real serial port or bench access is ever
    opened (SC4).
    """
    db = overrides.pop("db", None)
    if db is None:
        db = EpromDatabase(skip_local_override=True)
    config_manager = overrides.pop("config_manager", None)
    if config_manager is None:
        config_manager = ConfigManager()
    return AppContext(
        db=db,
        config_manager=config_manager,
        eprom_operator=overrides.pop("eprom_operator", Mock(spec=EpromOperator)),
        hardware_manager=overrides.pop("hardware_manager", Mock(spec=HardwareManager)),
        firmware_manager=overrides.pop("firmware_manager", Mock(spec=FirmwareManager)),
        eprom_presenter=overrides.pop(
            "eprom_presenter", Mock(spec=EpromConsolePresenter)
        ),
    )
```

**This is the 30-error mechanism.** `**overrides: object` types every `.pop(...)` result as
`object`, so each of the six `AppContext(...)` keyword arguments raises
`Argument "<name>" to "AppContext" has incompatible type "object"; expected "<Type>"` — six errors
per copy × five copies = 30. The fix is to replace `**overrides` with explicit typed keywords, which
is why D-10's factory must come **before** the bulk fixes.

**Analog B — the untyped shape that contributes zero errors** (`tests/test_cli_handlers.py:40-66`)
— do **not** touch these three (out of scope per CONTEXT.md §Deferred):

```python
def make_app_context(**manager_overrides) -> AppContext:
    """Construct an AppContext for in-process CliRunner tests.
    ...
    """
    db = manager_overrides.pop("db", None)
    if db is None:
        db = EpromDatabase(skip_local_override=True)
    config_manager = manager_overrides.pop("config_manager", None)
    if config_manager is None:
        config_manager = ConfigManager()
    return AppContext(
        db=db,
        config_manager=config_manager,
        eprom_operator=manager_overrides.pop(
            "eprom_operator", Mock(spec=EpromOperator)
        ),
        ...
```

(No annotation on `**manager_overrides` ⇒ the def is untyped ⇒ `check_untyped_defs = false` skips
the body entirely. That asymmetry is the whole reason five copies cost 30 errors and three cost 0.)

**The real `AppContext` — the exact field names and types the typed keywords must match**
(`firestarter/cli_handlers.py:104-116`):

```python
class AppContext:
    """Typed DI container threaded through every Click handler via ctx.obj (D-05, D-07).

    Constructed once at group entry; pulled by handlers via @click.pass_obj.
    CliRunner tests construct a fresh AppContext per test (mock managers OK).
    """

    db: EpromDatabase
    config_manager: ConfigManager
    eprom_operator: EpromOperator
    hardware_manager: HardwareManager
    firmware_manager: FirmwareManager
    eprom_presenter: EpromConsolePresenter
```

Six fields, all required, all non-`Optional`. The typed factory signature therefore wants
`Optional[X] = None` per keyword with a `None`-means-default body, e.g.:

```python
def make_app_context(
    *,
    db: EpromDatabase | None = None,
    config_manager: ConfigManager | None = None,
    eprom_operator: EpromOperator | None = None,
    hardware_manager: HardwareManager | None = None,
    firmware_manager: FirmwareManager | None = None,
    eprom_presenter: EpromConsolePresenter | None = None,
) -> AppContext:
```

⚠ Type-compat note the planner must resolve: callers pass `Mock(spec=EpromOperator)`, whose static
type is `Mock`, **not** `EpromOperator`. Annotating the parameter as `EpromOperator | None` moves
the 30 errors from the factory to its 4×N call sites unless the mock arguments are cast or the
parameters widened. The two idiomatic escapes already in the tree are `Mock(spec=...)` plus a
`cast(...)`, or annotating as a protocol. **Decide this in the plan, and measure the resulting count
in the numpy-free venv — do not assume it lands at ≤35.**

**Fixture-wrapping pattern** (`conftest.py:165-197`) — the house style for both a plain fixture and
a factory fixture; D-10's thin `app_context` fixture copies the former:

```python
@pytest.fixture
def fake_serial() -> _FakeSerial:
    """Return a fresh BytesIO-backed fake serial port."""
    return _FakeSerial()


@pytest.fixture
def make_comm(fake_serial):
    """Factory: build a SerialCommunicator wired to the fake serial port.
    ...
    """
    def _factory():
        ...
    return _factory
```

**conftest import-set today** (`:30-34`): `importlib.util`, `io`, `struct`, `pytest`. Adding the
factory pulls in `unittest.mock.Mock` plus six `firestarter.*` imports at conftest module scope —
which changes suite-wide import timing. `conftest.py`'s own docstring `:9-21` enumerates its exports
(`MAGIC_PREAMBLE_REF`, `_ref_crc8_ccitt`, `build_frame`, `fake_serial`, `make_comm`,
`collect_ignore`); **add the two new names to that list** or the docstring goes stale. Also note
`conftest.py` is itself a `check_no_exists_proxy` target (`:129`) and is **not** in any mypy
strict-island list — verify whether the new typed factory is actually type-checked, or the "typed
fixture" is unverified by the gate it exists to defend.

---

### `firestarter/constants.py` (config)

**The stale comment (RETIRE-08 reference 1 of 5), `:67-72`** — measured; CONTEXT.md said `:69-70`,
the actual stale tokens are on **`:69`** and **`:70`**, inside a block starting `:67`:

```python
# Both SDP commands are unconditional in firmware (firestarter.h:61-62) — never
# DEV_TOOLS-gated, because they are real user-facing operations in every build.
# Their COMMAND_NAMES entries below are load-bearing, not cosmetic:
# COMMAND_NAMES[cmd] is dereferenced at eprom_operations.py:301 and again at
# :377 (_setup_operation / _operation_context) — a missing entry is a KeyError
# at operation setup, not a cosmetic display gap.
COMMAND_SDP_UNLOCK = 9      # :73  (CONTEXT.md said :72)
COMMAND_SDP_LOCK = 10       # :74  (CONTEXT.md said :73)
```

Corrected form per D-11 (names first, numbers alongside): `_setup_operation` (`:329`) /
`_operation_context` (`:405`).

**The `COMMAND_NAMES` entries RETIRE-04's test must dereference, `:90-91`** (confirmed exact):

```python
COMMAND_NAMES = {
    COMMAND_READ: "READ",
    ...
    COMMAND_SDP_UNLOCK: "SDP_UNLOCK",    # :90
    COMMAND_SDP_LOCK: "SDP_LOCK",        # :91
    ...
}
```

**`FLAG_SKIP_SDP_UNLOCK`, `:110-121`** (confirmed at `:121`) — the tripwire's second comment site;
note the existing comment block already carries a firmware-sync caveat, so append rather than
displace:

```python
# Ninth and highest wire flag. Firmware's ctrl_flags is uint32_t, so 0x100 is
# in range, and firmware's flag block ENDS here (firestarter.h:148) — ...
FLAG_SKIP_SDP_UNLOCK = 0x100
```

---

### `firestarter/eprom_operations.py` — comment-reference corrections ONLY

> ## ⚠ RING-FENCE — DO NOT TYPE-FIX THIS MODULE
> `firestarter.eprom_operations` sits in `pyproject.toml:191-207`'s `follow_imports = "silent"`
> non-strict block. Its `[union-attr]` cluster (10 errors, one root cause) is dispositioned to
> **`FUT-MYPY-02`** by operator decision of 2026-08-03 (`.planning/REQUIREMENTS.md` §Out-of-Scope).
> This phase reads and references this file. It changes **no code** here and **no annotation** here.
> If a plan's diff of this file contains anything but comment text, the plan is out of scope.

**Correct anchors, re-measured and confirmed:**

```
315:    def _setup_operation(  # Remains largely the same, ...
329:        operation = COMMAND_NAMES[cmd]  # Get command name
376:    def _operation_context(
405:        operation_name = COMMAND_NAMES[cmd]
```

**No stale `301`/`377` tokens exist inside `eprom_operations.py` itself** — grep confirms zero hits.
All five stale references live in the *other* two files:

| # | File | Line | Verbatim stale text |
|---|------|------|---------------------|
| 1 | `firestarter/constants.py` | `:69-70` | ``# COMMAND_NAMES[cmd] is dereferenced at eprom_operations.py:301 and again at`` / ``# :377 (_setup_operation / _operation_context) — …`` |
| 2 | `tests/test_revision_constants_parity.py` | `:71-72` | ``` `COMMAND_NAMES[cmd]` is dereferenced at `eprom_operations.py:301` and ``` / ``` `:377` — a missing entry is a `KeyError` at operation setup, not a ``` |
| 3 | `tests/test_revision_constants_parity.py` | `:527` | ``` `eprom_operations.py:301` and again at `:377` ``` |
| 4 | `tests/test_revision_constants_parity.py` | `:549` | ``` "at eprom_operations.py:301 and :377, so this is a " ``` |
| 5 | `tests/test_revision_constants_parity.py` | `:585-586` | ``` `COMMAND_NAMES[cmd]` is dereferenced at `eprom_operations.py:301` and ``` / ``` again at `:377` (`_setup_operation` / `_operation_context`), so a ``` |

Reference 4 (`:549`) is inside an **assertion message string** — correcting it changes a test's
failure text, not its pass/fail behaviour. `tests.test_revision_constants_parity` is in the
Phase-36 strict island (`pyproject.toml:170`), so edits there are `check_untyped_defs`-checked.

---

### `tests/test_write_skip_sdp_unlock.py` (test) — D-14 named test + fixture migration

**Analog:** its own existing tests. Names are long and criterion-shaped — copy that convention for
D-14's tripwire test, whose *name and docstring are the record*:

```
157: def test_explicit_flag_sets_bit_0x100_on_the_wire(
179: def test_no_flag_on_an_allowed_0x0d_part_emits_no_skip_bit_and_no_auto_set_line(
198: @pytest.mark.parametrize("chip", [_FRAM_CHIP, _PRESDP_DIP2816_CHIP])
199: def test_refused_0x0d_part_gets_the_bit_auto_set_with_an_unconditional_report_line(
218: def test_auto_set_line_is_not_duplicated_when_the_user_passed_the_flag(
243: def test_non_0x0d_chip_with_the_flag_warns_and_proceeds(
263: def test_non_0x0d_chip_without_the_flag_is_unchanged(
```

Local `make_app_context` at `:55` (one of the four survivors) with a **real** `EpromOperator`
default — this variance is why D-10 keeps per-test parameters and does not force the fixture:

```python
def make_app_context(**overrides: object) -> AppContext:
    """...
    Mirrors test_dev_sdp_cmd.py's make_app_context shape, but defaults
    eprom_operator to a real `EpromOperator` (not a Mock) because this suite
    proves the flags bit reaches the composed wire command_dict, which only
    a real EpromOperator composes.
    """
    ...
        eprom_operator=overrides.pop("eprom_operator", EpromOperator(config_manager)),
```

⚠ Its docstring cites `test_dev_sdp_cmd.py` by name at `:42` and `:58` — the `git mv` stales both.
Update them in the same commit.

**Driver helper** `_drive_write(...)` at `:86` — the tripwire test should reuse it rather than
re-author a CliRunner invocation.

---

### `tests/__snapshots__/test_characterization.ambr` (snapshot)

**The `test_help_dev` block, `:124-146`** — measured; the `sdp` line is at **:141** (confirmed):

```
# name: test_help_dev
  '''
  Usage: firestarter dev [OPTIONS] COMMAND [ARGS]...
  ...
  Commands:
    addr               Direct access to address lines and control register.
    consistency-check  Read EPROM N consecutive times and report SHA-256...
    fault-inject       Demonstrate COBS resync: inject a corrupted frame...
    read               Reads the content from an EPROM and prints data to...
    reg                Direct access to registers: MSB, LSB and control...
    sdp                Enable or disable Software Data Protection (SDP) on...    <-- :141, deleted
    test               Run the community chip-validation sweep for CHIP...
    validate-family    Run the per-family validation matrix Tier-3 runner...
    write-cycle        Erase → write source image → read-back N times;...
  
  '''
# ---
```

**Expected diff shape (D-13's named criterion):** exactly one deleted line, `git diff --stat`
showing `1 deletion(-)` in this file and nothing else. Update **node-id-scoped**
(`--snapshot-update` restricted to `test_help_dev`), never a broad regeneration. `addopts` is
`"-ra -q"` (`pyproject.toml:107`) with no `--snapshot-warn-unused`, and the entry stays *used*, so
syrupy's unused-snapshot session failure does not fire (Phase 136's hazard, not this one).

**Width trap** (CONTEXT.md §Established patterns): the snapshot is generated via a real subprocess
at unforced width 78, not `CliRunner` (which forces 80). `tests/test_characterization.py`'s
`_run_fw_help_at_version` (~`:242-286`) is the existing solution — do not reinvent it.

---

### `pyproject.toml` (config)

**Watermark line, `:159`** (confirmed) — read by regex from a *comment*; **not touched** (D-09):

```toml
# mypy_error_watermark = 35   # Updated Phase 71-07: floor after 71-06 added test_validate_family_cmd.py (6 AppContext mock-type errors). Prior: 29 (Phase 69-03).
```

Note the comment itself names the 30-error mechanism this phase discharges — when the watermark is
eventually ratcheted, this trailing rationale is what must be rewritten.

Other relevant blocks: `[tool.mypy]` `:138-158` (`python_version = "3.10"`,
`disallow_untyped_defs = false`, `check_untyped_defs = false`); Phase-36 test strict island
`:161-173`; Phase-42 production strict island `:175-189` (D-02's insertion point); ring-fence
`follow_imports = "silent"` block `:191-207`.

**`[var-annotated]` targets from the ordering plan** (verified live):

```python
firestarter/database.py:173:        self.proms = {}       # needs Dict[str, Any] (CONTEXT said 174)
firestarter/database.py:174:        self.pin_maps = {}    # (CONTEXT said 175)
firestarter/database.py:325:        pin_signals = {}      # (confirmed)
firestarter/ic_layout.py:233:        properties = []       # the only bare-collection candidate in the file
```

⚠ All four live in the `follow_imports = "silent"` block — verify these actually surface in the
watermark count before planning them as fixes.

---

## Shared Patterns

### Fail-closed explicit target list (all `tools/check_*.py`)
**Source:** `tools/check_no_exists_proxy.py:49-62` (docstring rationale) + `:113-157` (the list)
**Apply to:** any new gate-adjacent tooling this phase writes

```python
_HERE = os.path.dirname(os.path.abspath(__file__))
_APP_ROOT = os.path.dirname(_HERE)

_DEFAULT_TARGETS = [
    os.path.join(_APP_ROOT, rel)
    for rel in (
        "tests/__init__.py",
        ...
    )
]
```

Never a glob, never a tree walk. Precedence is argv > env seam (`is not None`, never truthiness) >
the literal list. Zero-targets guard is placed **above** the missing-target guard, because the
latter is vacuously satisfied by an empty list.

### Watermark-gate pure-function seam
**Source:** `tools/check_mypy_watermark.py:41`, `:48`, `:91-229`
**Apply to:** the CI-replica venv script, and any new test asserting on gate behaviour

`classify_mypy_result(returncode, output) -> int` and `enforce_watermark(count, watermark) -> None`
are pure and directly importable — call them, do not shell out. `MIN_CHECKED_SOURCE_FILES = 120`
(`:48`) is a hard floor: this phase **adds** two files (`firestarter/sdp_honesty.py`,
`tests/test_sdp_honesty.py`) and net-removes none, so the checked count rises. **Verify, don't
assume** (CONTEXT.md §Integration points).

Do **not** switch to `mypy --output json` (STACK §1): JSON mode emits no summary line, which
destroys the `Found N errors in M files (checked K source files)` clause D-08's evidence depends on.

### `test_check_*` house shape, including fail-closed legs
**Source:** `tests/test_check_sdp_capability.py:76-248`, `tests/test_check_mypy_watermark.py:152-363`
**Apply to:** any test authored for the new venv script or a rename-proofing gate

```
test_checker_exits_zero_on_clean_source
test_default_target_resolves_to_an_existing_file
test_pass_line_names_the_scanned_file
test_checker_exits_nonzero_on_planted_...
test_fail_closed_on_missing_target(tmp_path)
test_fail_closed_on_zero_symbol_scan(tmp_path)
```

`test_default_target_resolves_to_an_existing_file` is the leg that would have caught the
`check_permitted_claims.py` `_HERE` trap; `test_fail_closed_on_zero_symbol_scan` is the
non-vacuity leg. `check_mypy_watermark`'s pure-function legs (`:352`, `:363`) show the
no-subprocess style.

### Coverage that already exists (do NOT re-author it — D-04)
**Sources:**
- `tests/test_sdp_db_invariant.py` — Phase 131's 43/41/84 gate:
  `test_exactly_84_algorithm_0x0d_entries` `:248`,
  `test_all_0x0d_chips_have_chip_id_check_false` `:273`,
  `test_all_0x0d_chips_have_chip_id_value_zero_sentinel` `:289`,
  `test_synthetic_chip_id_check_true_is_flagged_non_vacuous` `:318`,
  `test_sdp_partition_matches_committed_allow_list_element_wise` `:359`,
  `test_sdp_partition_counts_are_43_41_84` `:380`,
  `test_partition_flags_a_moved_chip_non_vacuous` `:420`.
- `tests/test_check_sdp_capability.py` — the capability-predicate gate tests listed above.

Between them, the capability partition and its non-vacuity are already fully covered. Retargeting
`test_dev_sdp_cmd.py`'s chip-resolution / capability-refusal cases onto `sdp_capability()` would be
duplicate coverage dressed as preservation. Prune them and account for the prune.

### Import-time binding (why some proofs need a subprocess)
**Source:** CONTEXT.md §Established patterns; `firestarter/channel.py` + `_BOARD_CHOICES`
**Apply to:** any test wanting a different environment

`FW_ROOT`, `FW_REPO_PRESENT`, `requires_fw`, `_BOARD_CHOICES` and
`channel.is_prerelease_build()`'s effect on option construction are frozen at import/collection.
`monkeypatch.setenv` runs after and has no effect. Use a subprocess.

### No new skip reasons
**Source:** `tests/test_skip_census.py` — `ALLOWED_SKIP_REASONS` fails **closed**.
This phase should need zero new entries. A fix that wants one is a signal to re-examine the fix.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `.planning/REQUIREMENTS.md` (RETIRE-08 "three" → "five") | doc | n/a | Prose edit in the meta-repo; the pattern is D-12's *evidence clause* requirement (five references, two files, enumerated), not a code analog. Use the §"eprom_operations.py — comment-reference corrections" table above as the evidence clause verbatim. |

---

## Metadata

**Analog search scope:** `/workspaces/firestarter_app/{firestarter,tests,tools,.github/workflows}`,
`pyproject.toml`; `/workspaces/.planning/{ROADMAP.md,phases/132-*}`
**Files read this session:** 22
**Anchors re-measured:** 31 (4 diverge from CONTEXT.md — `Confirm.ask` `:2273` not `:2267`;
honesty `click.echo` `:2315-2319` not `:2316-2318`; `COMMAND_SDP_*` `:73/:74` not `:72/:73`;
`database.py` `:173/:174` not `:174/:175`)
**Pattern extraction date:** 2026-08-03
