# Standards for the Shield-Revision Gate

The following standards apply to this work.

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

## host/echo-vs-logger

`logger.*` is for diagnostics that show only with `-v`. A fact the operator needs uses `click.echo`, so it shows at default verbosity.

```python
# operator must see this without -v
click.echo(f"{eprom.upper()}: pulse override {pulse_us} us (database: {db_pulse} us)")

# diagnostic detail
logger.debug("resolved bus config: %s", bus_config)
```

- Use `click.echo` for: refusals that exit without an exception, verdict lines, and notices that change what the operation does.
- Use `logger` for: trace detail, timings, raw frames.

---

## host/help-docstrings

A command docstring and every `help=` string are user documentation. Click prints them as `--help`.

- No internal references: no phase or plan IDs, requirement tags (`WRITE-01`), `file:line`, or maintainer notes.
- Put implementation reasoning in a `#` comment in the function body, not in the docstring.
- Write in ASD-STE100 (same as refusal text).
- Do not add tests that pin `--help` text.

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

## firmware/fail-closed-refusals

Unknown or out-of-range input is refused with an error ID. Never clamp, never pick a default row.

```cpp
const eprom_params_t* row = eprom_params_for(handle->protocol);
if (row == NULL) {                       // never &EPROM_PARAMS[0]
    LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}
if (energy_cap_us > 0 && handle->pulse_delay > energy_cap_us) {  // 0 = uncapped
    LOG_ERROR_ID_U32(MSG_ERR_PULSE_TOO_WIDE, handle->pulse_delay);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}
```

Why: a fallback can put HV on a part that cannot take it. A silent clamp gives a verify failure that looks like bad silicon. The host needs an explicit error ID as evidence.

- Refuse pre-flight, before any HV bit is set.
- Every refusal = `LOG_ERROR_ID_*` + `RESPONSE_CODE_ERROR` + `return`. Change no hardware state.
- Lookups return NULL on no match; callers check it.
- Unknown protocol values end in `configure_not_implemented()` (`0xBB`). No other path.
- Only exception: a `0` on the wire means "use the handler default" (`pulse_delay`, AT28C `page_size`). Resolve the default first, then run the refusal checks.
- Guard sentinels: `0` in a cap field means "uncapped", not "cap at zero".

---

## firmware/logging-ids

Emit only catalog IDs through the `LOG_<SEV>_ID_*` macros in `logging_id.h`. Severity is in the ID; every macro calls `rurp_log_id`.

```cpp
bool force = is_flag_set(FLAG_FORCE);
mem_util_report_voltage(handle, vpp_mv, handle->vpp_mv,
                        force ? MSG_WARN_VPP_HIGH : MSG_ERR_VPP_HIGH,
                        force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR);

uint8_t _b[4] = { addr >> 16, addr >> 8, addr, pulse_count };  // big-endian
LOG_ERROR_ID_BYTES(MSG_ERR_MAX_PULSES, _b, 4);
```

- A new message goes in the meta repo `tools/catalog/messages.toml`, then run codegen there. Never hand-edit `messages.h`.
- The payload matches the catalog shape: big-endian, exact byte count. Use `LOG_ID_U*` or the composites, or pack `_b[]` by hand.
- A `--force` downgrade forks the ID and the response code together. Both IDs must be in the catalog.
- An unrecognised raw chip value: send the raw byte + `0xFF` decode + `RESPONSE_CODE_WARNING`. Never coerce it to a known value.
- `LOG_INFO_ID_*` emits only with `FLAG_VERBOSE`. Data the host needs uses DATA/WARN/ERROR.
- Uno-class (`SERIAL_ON_IO`): frames sent in programmer mode go to a 4-slot buffer, and extra frames drop silently. Keep frames per operation to a minimum there. Guard periodic emits with `#ifndef SERIAL_ON_IO`.

---

## firmware/size-reporting

Every firmware change reports flash and RAM, before and after, for `leonardo` and `uno`.

```bash
pio run -e leonardo                                       # stable image
PLATFORMIO_BUILD_FLAGS="-D DEV_TOOLS=1" pio run -e leonardo   # beta image (larger)
pio run -e uno
```

- Take the numbers from the `RAM:` / `Flash:` lines of the build output.
- Leonardo is the tightest target: 28672 B Caterina ceiling, not 32768.
- Report the beta (`DEV_TOOLS=1`) image too. It ships and it is larger.
- Always report RAM next to flash. A PROGMEM move trades one for the other.

---

## protocol/message-catalog

Message IDs have one source: `tools/catalog/messages.toml` in the meta repo. Generate the artifacts only there.

```bash
# edit tools/catalog/messages.toml, then:
tools/catalog/sync_to_subrepos.sh   # writes firestarter_fw/include/messages.h
                                    #    and firestarter_app/firestarter/messages.py
```

- Never hand-edit `messages.h` or `messages.py`. The next sync overwrites them without warning.
- Never regenerate in a sub-repo. The sub-repos hold generated artifacts only.
- Commit in all three repos on the same milestone branch: catalog (meta), `messages.h` (fw), `messages.py` (app).
- A new ID needs host rendering in the same change (format string, render hints, decoder handling).
- Never reorder entries.
- The ERROR band `0xA0–0xBF` is full. New ERROR IDs start at `0xC0`. Severity comes from the `severity` field, never from the ID range.
- Params: at most 24 wire bytes. `wire_format = "text"` entries have `params = []`.

---

## protocol/rollout-compatibility

Firmware ships first. The host may require the latest firmware.

- Release the firmware before the host that depends on it.
- If the firmware is too old, the host raises `FirmwareOutdatedError`, and the message tells the user to run `firestarter fw --install`. The host has no fallback paths for old firmware.
- New ack and blob fields go at the end. The host finds them by frame length, never by version string. Compute offsets from the length bytes (`ver_len`), never from a literal index.
- A numeric field has a plausibility range, and `0` means "not sent" (e.g. `write_budget_s` accepts `[1, 14400]`). Never read `0` as a real value.

---

## testing/native-firmware-tests

Unity suites live in `test/native/avr/<suite>/` and run on the host with `platform = native`.

To add a suite, update both lists in `[native_base]` in `platformio.ini`:

```ini
test_filter = ... native/avr/<suite>
shared_build_flags = ... -I test/native/avr/<suite>
```

A suite that is not in `test_filter` never runs.

```bash
pio test -e native && pio test -e native_nodevtools   # run both; CI runs `native` on PRs only
```

Harness blind spots:
- The recording stubs (`test/native/avr/_shared/host_stubs_common.inc`) log every register write. Real `rurp_write_to_register` skips unchanged values. Do not count register writes.
- Time is fake. Most suites mock `millis()` through ArduinoFake to always return 0, and `delay()` records nothing. Do not assert timing.

Golden traces run the happy path (matching chip ID, VPP in window). For every branch, add explicit tests: chip-ID mismatch, each WARNING/ERROR fork, VPP out of window, poll timeout.

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

## testing/no-source-introspection

A test exercises production code with data. It never reads source text and asserts on its contents, whether by regex, substring or `ast`. This applies in all repos.

| Allowed | Forbidden |
|---|---|
| Call production functions; assert on results | Read `.py` `.c` `.h` `.cpp` `.md` `.yml` `.toml` and assert on the text |
| Read shipped data (`firestarter/data/*.json`, `pinouts.json`) | `ast` walks of production modules |
| Native Unity tests that run firmware code | Tests that parse another repo's source |

Why: source scanners fail open. A rename makes them skip or match zero times, and nothing goes red.

- If a hazard cannot be observed by a test, make it true by construction: codegen from one source (like `tools/catalog/`), a single shared definition, `static_assert` / `#error`.
- Host/firmware parity comes from codegen, not from a parity test.
- The source contracts in `firestarter_fw/tests/` are legacy, pending removal. Add none, do not extend them, and remove one when you touch it.

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
