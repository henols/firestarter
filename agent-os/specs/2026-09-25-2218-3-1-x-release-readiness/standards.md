# Standards for 3.1.x Release Readiness

The following standards apply to this work. Each is reproduced in full so the spec stands alone.

Applicability in one line each:

| Standard | Why it applies |
|---|---|
| host/pre-serial-gates | `fw_release_gate.py` is a pure gate. One recorded deviation — see shape.md D-8. |
| host/gate-polarity | Fail closed on an unparseable version. D-9 is the one documented fail-open edge. |
| host/typed-refusals | `FirmwareReleaseRefusedError` under `FirmwareOperationError`, no new arm. |
| host/refusal-text | `_REFUSAL_FORMAT` / `_UNREADABLE_FORMAT`, imported by tests, never copied. |
| host/command-skeleton | The `--allow-newer-firmware` option on `fw`. |
| host/help-docstrings | Its `help=` string is user documentation. No `--help` pin test. |
| testing/non-vacuity | Both threshold sides, violating input, absent-evidence cases. |
| testing/standalone-checkout | Verify from a fresh clone on Python 3.11, not the devcontainer. |
| protocol/retired-ordinals | Read, not changed. Its tombstones are the evidence behind D-3. |
| protocol/rollout-compatibility | Firmware ships first — the ordering constraint in the runbook. |

---

## host/pre-serial-gates


Each host safety policy is its own module (`*_gate.py`, `*_guard.py`). It is a pure predicate over the resolved wire dict and the operation name.

```python
DAMAGE_CAPABLE_OPERATIONS = frozenset({"write", "erase"})

def is_affected(bus_config: dict | None) -> bool: ...

def require_acknowledged(chip_name, bus_config, operation, acknowledged) -> None:
    if operation not in DAMAGE_CAPABLE_OPERATIONS:
        return
    if not bus_config or not bus_config.get("bus"):
        raise Pin1HazardRefusedError(...)   # absent evidence = refuse
    ...
```

- No I/O, no environment reads, no serial access.
- `require_*()` raises a typed exception on refusal and returns `None` on pass. `is_*()` / `requires_*()` return a bool.
- Call it from `eprom_operations.py`, not only `cli_handlers.py`. `dev test`, `chip_test` and library callers must reach it too.
- It refuses before the port opens and before the wire dict reaches the transport.
- Never inline the policy in `eprom_operations.py` or `cli_handlers.py`.
- Import protocol IDs (`FLASH4_PROTOCOL_ID`, `SDP_PROTOCOL_ID`). Never retype the literal.
- Ship a test that plants a violation and proves the gate refuses it.

---

## host/gate-polarity


A gate fails closed by default: absent evidence means "not provably safe", never "probably fine".

| Worst case of a wrong guess | Polarity | Example |
|---|---|---|
| Chip damage or data loss | Fail closed | `jp5_gate`, `page_size_gate`, `write_blank_guard` |
| Only an operation becomes unavailable | Fail open allowed | `flash4_erase_gate` |

- A fail-open gate must state why its worst case is only lost availability.
- The module docstring names the polarity, the worst case in each direction, and the operator escape.
- The escape is a documented CLI option (`-b`) or an interactive yes. Never an environment variable: those fail open.
- An invalid recorded value (non-power-of-two page size, out-of-range) refuses exactly like a missing value.

---

## host/typed-refusals


Each refusal has its own exception class in `exceptions.py`, under the root that matches its domain. `@map_typed_errors` turns it into a `click.ClickException` (exit 1).

| Root | Rendered prefix |
|---|---|
| `SerialError` | `Communication error: ` |
| `EpromOperationError` | `Programmer error: ` |
| `HardwareOperationError` | `Hardware error: ` |
| `ChipNotFoundError`, `FirmwareOperationError` | none |

```python
class PageAlignmentError(EpromOperationError):
    """Raised when ... Fired by page_size_gate.require_page_alignment before any serial byte."""
```

- A new class gets its prefix from its root class. Write the message so it reads correctly after that prefix.
- Existing verbatim arms (`ChipNotImplementedError`, `PageSize*`, `PageAlignmentError`, `NegativeStartAddressError`, `Pin1HazardRefusedError`) are exceptions. Do not add more.
- A subclass arm goes above its parent's arm. The first matching `except` wins.
- Gates raise; they never call `sys.exit`. The only exit path is `map_typed_errors` → `ClickException` (exit 1).
- The docstring says which function raises it and that it fires before any serial byte.

---

## host/refusal-text


Keep refusal text in module-level format constants. Tests import the constant; they do not copy the text.

```python
_REFUSAL_FORMAT = (
    "Refusing write to {chip_name}: not blank at 0x{address:06X}, v: 0x{value:02X}."
)
raise SomeRefusalError(_REFUSAL_FORMAT.format(chip_name=chip_name.upper(), ...))
```

- Put the chip name in upper case, near the start: `W27C512: ...` or `Refusing write to W27C512: ...`.
- Say what can go wrong, and how the operator can continue (`-b`, cut JP5 and answer yes).
- For jumpers and pins, quote the board silkscreen exactly (`"Cut for ROMs with A19 on P1"`), so the operator can check it on the board.
- Write in ASD-STE100: short sentences, one instruction per sentence, no hedging.

---

## host/command-skeleton


```python
@cli.command(name="read")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.option("-a", "--address", default=None, help="Read start address in dec/hex")
@click.pass_obj
@map_typed_errors                      # innermost
def read(app: AppContext, eprom: str, address: str | None) -> None:
    """Reads an EPROM into a file."""
    ok = app.eprom_operator.read_eprom(...)
    sys.exit(0 if ok else 1)
```

- Decorator order: `@cli.command` → arguments/options → `@click.pass_obj` → `@map_typed_errors`.
- Handlers take `app: AppContext`. Never build managers inside a handler. Tests pass `obj=AppContext(...)` to `CliRunner.invoke`.
- Check invalid option combinations first and raise `click.UsageError` (e.g. `--full` without `--verify`), before `resolve_chip`.
- Plain commands end with `sys.exit(0 if ok else 1)`.
- Verdict commands (`verify`, `write --verify`, `blank -b`): `0` = proven good, `1` = proven bad, `2` = could not decide (read failed, refused before compare).

---

## host/help-docstrings


A command docstring and every `help=` string are user documentation. Click prints them as `--help`.

- No internal references: no phase or plan IDs, requirement tags (`WRITE-01`), `file:line`, or maintainer notes.
- Put implementation reasoning in a `#` comment in the function body, not in the docstring.
- Write in ASD-STE100 (same as refusal text).
- Do not add tests that pin `--help` text.

---

## testing/non-vacuity


Every new check (gate, guard, refusal) ships with committed tests that feed it violating input and assert that it refuses.

```python
def test_is_affected_true_at_bit_19(): ...                   # refuses
def test_is_affected_false_at_bit_18(): ...                  # boundary: passes
def test_require_acknowledged_no_bus_key_raises_fail_closed(): ...  # absent evidence
```

- Test both sides of each threshold.
- For a fail-closed check, test `None` / empty / missing input.
- The violation is in the input data (synthetic pin map, bad page size). Never mutate source to plant it.
- A test written before the fix must fail on its own assertion. If it fails on setup or lookup, the test is broken, not the code. Read the failure message.
- Assertions on shipped data use exact counts (`== 746`), never floors (`>=`). A change updates the number on purpose.

---

## testing/standalone-checkout


CI checks out each repo alone (`work/<repo>/<repo>`). The devcontainer's sibling layout (`/workspaces/firestarter_fw` next to `firestarter_app`) hides cross-repo dependencies.

```python
_APP_ROOT = Path(__file__).resolve().parent.parent   # never cwd, never an env var
_DB_FILE = _APP_ROOT / "firestarter" / "data" / "chip_database.json"
```

- A test reads only files inside its own repo. Never a sibling repo, the meta repo or `.planning/`.
- Resolve paths from `Path(__file__)`.
- To check "inside repo X", use `Path.is_relative_to()`, never a name substring.
- Never write a test that skips when a sibling is absent. In CI it never runs.

Before you trust a new test, run it in a fresh clone of that repo only. The clone sees committed files only.

```bash
git clone /workspaces/firestarter_app "$SCRATCH/app" && cd "$SCRATCH/app"
export UV_CACHE_DIR="$SCRATCH/uv-cache"          # default cache is not writable
uv venv --python 3.11 .venv                      # CI runs 3.11; devcontainer has 3.12
VIRTUAL_ENV=.venv uv pip install -e '.[test]' && .venv/bin/pytest tests/
```

Use a new venv. The devcontainer's editable install still points at `/workspaces`.

---

## protocol/retired-ordinals


Never reuse a retired wire ordinal. Shipped hosts still send them, so a new meaning would make an old host drive a different operation.

| Kind | Retired |
|---|---|
| Command | `4` (blank check), `6` (verify) |
| Flag | `0x08` (skip blank check) |

When you retire one, leave a tombstone comment at the old slot on both sides (`constants.py` and `firestarter.h`):

```python
# Ordinal 6 -- the verify command -- retired in 3.1.0. This ordinal must
# NEVER be reused for any new command, flag or reserved meaning.
```

- Keep the slot empty. Do not delete the tombstone.
- Give a new command or flag the next unused value.

---

## protocol/rollout-compatibility


Firmware ships first. The host may require the latest firmware.

- Release the firmware before the host that depends on it.
- If the firmware is too old, the host raises `FirmwareOutdatedError`, and the message tells the user to run `firestarter fw --install`. The host has no fallback paths for old firmware.
- New ack and blob fields go at the end. The host finds them by frame length, never by version string. Compute offsets from the length bytes (`ver_len`), never from a literal index.
- A numeric field has a plausibility range, and `0` means "not sent" (e.g. `write_budget_s` accepts `[1, 14400]`). Never read `0` as a real value.

---

