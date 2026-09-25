# Spec: shield-revision gate for VPP-on-pin-21 chips (write/erase, `--force`, `config --rev 2.2`)

## Context

A 24-pin chip with VPP on chip pin 21 (pin maps `DIP24_2716` and `DIP24_2532`, for example the TI
2516) needs the three-position JP4 of a Rev 2.2 or Rev 2.3 shield. An earlier shield cannot route
VPP to that pin.

The host already has a check: `SerialCommunicator._validate_hardware_revision`
(`firestarter_app/firestarter/serial_comm.py:749-803`). It runs in `setup_command` after the
firmware's `MSG_OK_READY` ack, which carries the effective hardware-revision byte.
`serial_comm.py:386` reads that byte into `hw_revision`. The check has these gaps:

1. **`--force` does not override it.** The operator wants the refusal to stop the operation, and
   `--force` to continue with a warning.
2. **It refuses every command.** `read`, `blank`, `verify` and the write's own blank-guard read are
   refused too. The operator wants only `write` and `erase` checked.
3. **The refusal is hidden on a cold connect.** `HardwareRevisionUnsupportedError` is a
   `SerialError`. So `_setup_operation` (`eprom_operations.py:740-743`) catches it, logs "Failed to
   setup operation …" and returns `(None, 0)`. It never reaches `map_typed_errors`. If it did, it
   would get the wrong prefix, `Communication error:`.
4. **You cannot assert Rev 2.2.** The firmware ADC puts Rev 2.0, 2.1 and 2.2 in one bucket
   (`REVISION_2_0`). Rev 2.2 (`0x04`) comes only from the EEPROM override. `config --rev` is
   `type=float` followed by `int()`, so `--rev 2.2` becomes `2`, which is Rev 2.0. Today the
   refusal text tells you to type `--rev 4`.
5. **The firmware accepts any `rev` value.** `get_rev` (`firestarter_fw/src/json_parser.c:556`)
   writes `strtoul` into a `uint8_t` with no range check (260 becomes 4), and then saves it to
   EEPROM.

Intended outcome:
- `write` or `erase` of such a chip on a shield that does not report Rev 2.2/2.3 stops with a clear
  `Hardware error:`, exit 1.
- `--force` continues and shows a warning at default verbosity.
- `firestarter config --rev 2.2` stores the Rev 2.2 override in the Arduino EEPROM.
- The firmware refuses an out-of-range `rev` and does not change its config.

## Task 1: Save spec documentation

Create `agent-os/specs/2026-09-25-2040-hw-rev-gate-pin21/` in the meta repo with:
- **plan.md** — this plan.
- **shape.md** — scope, the decisions below, and the context.
- **standards.md** — the full text of: host/typed-refusals, host/refusal-text, host/gate-polarity,
  host/echo-vs-logger, host/help-docstrings, host/command-skeleton, host/pre-serial-gates,
  firmware/fail-closed-refusals, firmware/logging-ids, firmware/size-reporting,
  protocol/message-catalog, protocol/rollout-compatibility, testing/native-firmware-tests,
  testing/non-vacuity, testing/no-source-introspection, testing/standalone-checkout.
- **references.md** — `serial_comm.py` `_validate_hardware_revision` and `setup_command`,
  `jp5_gate.py` (the pure-gate shape), `jumper_table.py` (`VPP_UNREACHABLE_TEXT`,
  `JP4_SILKSCREEN_RULE`), `codec.py` `_REVISION_SILKSCREEN`, `tests/test_hw_revision_gate.py`,
  and the firmware files `json_parser.c` and `firestarter.cpp` (the `CMD_CONFIG` arm).
- No `visuals/` (none were provided).

### Decisions to record in shape.md
- **D-1. Commands checked:** `COMMAND_WRITE` and `COMMAND_ERASE` only. `read`, `blank` and `verify`
  pass on every shield with no warning. On a 0x0B write, the blank-guard read (a `COMMAND_READ`)
  runs first and passes, and the write's own connect is then refused. That extra read of a
  2–4 KiB part is accepted. The alternative, telling the guard read that it belongs to a write,
  needs a new parameter through four call levels and was not chosen.
- **D-2. Chips checked:** the same as today: `bus-config.vpp-pin == 11`, which covers exactly
  `DIP24_2716` and `DIP24_2532`. The revisions that pass are the allowlist `{REVISION_2_2,
  REVISION_2_3}`. `0xFE`, `0xFF`, `REVISION_2_0` and `None` are refused (fail closed).
- **D-3. `--force`** comes from the wire dict (`flags & FLAG_FORCE`), so the gate stays pure. When
  forced, the operation continues and a warning prints with `click.echo(..., err=True)` at default
  verbosity. `--force` already exists on `write` and `erase`. Its help text gains the revision
  case.
- **D-4. Exception root:** `HardwareRevisionUnsupportedError` moves from `SerialError` to
  `HardwareOperationError`. It then renders as `Hardware error: …` and exits 1. The
  `except SerialError` in `_setup_operation` no longer catches it, so no new re-raise is needed.
  No new verbatim arm, as `host/typed-refusals` requires.
- **D-5. Policy module:** the policy moves out of `serial_comm.py` into a pure
  `firestarter/hw_revision_gate.py`, following the `host/pre-serial-gates` shape. It is a recorded
  deviation from that standard: this gate must run after the ack, because the revision comes from
  the firmware. `setup_command` calls it.
- **D-6. `config --rev`** takes silkscreen values only: `0`, `1`, `2`, `2.0`, `2.1`, `2.2`, `2.3`,
  plus `-1` to clear the override. It uses `click.Choice`, so any other value (including the old
  raw bytes `4` and `5`) is a `UsageError` that lists the valid values. The host maps the value to
  the byte (`2.2` → `0x04`).
- **D-7. Firmware range check:** `rev` must be one of `0x00–0x05` or `0xFF`. Other values are
  refused with a new catalog error ID. RAM and EEPROM config do not change. No new ack field, and
  no host version gate is needed: the host also validates `--rev`. The firmware ships first, as
  usual.
- **D-8. Branches:** `v1.42-hw-rev-gate` in `firestarter_app` and `firestarter_fw`, from their
  current `v1.42-jumper-display` HEADs. The meta repo commits the spec, the catalog change and the
  gitlink advance on its current branch.

## Task 2: Firmware — refuse an out-of-range `rev` (firestarter_fw, then catalog in meta)

1. Meta repo `tools/catalog/messages.toml`: add `MSG_ERR_INVALID_REV` at the next free ERROR ID at
   or above `0xC0` (`0xC0` is taken by `MSG_ERR_FL4_PAGE_ALIGN`). Severity ERROR, one `u32` param
   (the raw requested value). Example format: `"Invalid hardware revision: %lu"`. Run
   `tools/catalog/sync_to_subrepos.sh`. Commit the catalog (meta), `messages.h` (fw) and
   `messages.py` (app). Never hand-edit the generated files.
2. `src/json_parser.c` `get_rev`: parse into a local `unsigned long` first. Assign
   `config->hardware_revision` only when the value is 0–5 or `0xFF`. For any other value, report
   an invalid-rev result to `json_parse_config` (for example a distinct negative return that
   carries the value). `config` points at the live RAM config, so assigning before the check
   changes the effective revision even without a save.
3. `src/firestarter.cpp` `CMD_CONFIG` arm (about line 100): on the invalid-rev result, emit
   `LOG_ERROR_ID_U32(MSG_ERR_INVALID_REV, value)` exactly once, not also `MSG_ERR_PARSE_CFG`. Set
   the error response the same way the existing `MSG_ERR_PARSE_CFG` path does, return, and do not
   call `rurp_save_config`.
4. New native Unity suite `test/native/avr/test_config_rev/`, registered in both lists in
   `[native_base]` of `platformio.ini`. Test cases:
   - 0, 5 and 255 are accepted and stored.
   - 6, 254, 256, 260 and `-1` are refused, and `hardware_revision` does not change.
   - Boundaries: 5 against 6, and 254 against 255.

   Check that `HARDWARE_REVISION` is defined in the native envs. If it is not, define it for this
   suite.
5. Run `pio test -e native && pio test -e native_nodevtools`. Report flash and RAM before and after
   for leonardo stable, leonardo `DEV_TOOLS=1` and uno.

## Task 3: Host — pure gate module `firestarter/hw_revision_gate.py`

- Module docstring: the polarity is fail closed. The worst case of a false pass is VPP on the wrong
  pin and chip damage. The worst case of a false refusal is an operation that is not available.
  The escapes are `firestarter config --rev 2.2` and `--force`.
- Constants:
  - `VPP_LINE_REQUIRING_REV_2_2 = 11`.
  - `REVISIONS_WITH_3_POSITION_JP4 = (REVISION_2_2, REVISION_2_3)`. Keep the allowlist comment.
  - `GATED_COMMANDS = frozenset({COMMAND_WRITE, COMMAND_ERASE})`, imported from `constants.py`.
- `is_refused(command_to_send, detected) -> bool`: true when `cmd` is in `GATED_COMMANDS`,
  `bus-config.vpp-pin == 11`, and `detected` is not in the allowlist.
- `require_supported_revision(command_to_send, detected) -> None`: when `is_refused` is true and
  `FLAG_FORCE` is not set, raise `HardwareRevisionUnsupportedError` with `_REFUSAL_FORMAT`.
- `forced_warning(command_to_send, detected) -> str | None`: the `_FORCED_WARNING_FORMAT` text
  when the check is refused and forced. Otherwise `None`.
- Show the revision as silkscreen text with `codec._REVISION_SILKSCREEN`, falling back to the hex
  byte. For `None`, say the firmware does not report a revision.
- `_REFUSAL_FORMAT` (STE100, chip name upper case, reads correctly after `Hardware error: `). It
  says:
  - the chip needs VPP on chip pin 21;
  - only a Rev 2.2 or Rev 2.3 shield can supply it (the Rev 2.2 JP4 pole toward the board edge);
  - the programmer reports `{reported}`;
  - VPP on an incorrect pin can damage the chip;
  - if the shield is Rev 2.2, run `firestarter config --rev 2.2` one time, because the firmware
    cannot detect Rev 2.2;
  - to continue at your own risk, use `--force`.
- `_FORCED_WARNING_FORMAT`: for example `"WARNING: {chip}: the programmer reports {reported}, not
  Rev 2.2 or 2.3. --force is set. The {operation} continues. VPP on an incorrect pin can damage the
  chip."`

## Task 4: Host — wire the gate and the exception

- `serial_comm.py`:
  - Delete `_validate_hardware_revision` and its two class constants.
  - In `setup_command`, at the same place (after the version gate), call
    `hw_revision_gate.require_supported_revision(command_to_send, self.hw_revision)`.
  - Then, if `forced_warning(...)` returns text, `click.echo(text, err=True)`.
  - Keep the comment that says why validating after the ack is safe (VPP waits for the next host
    ack).
  - Check that `_probe_port` (`:1013`) and `find_and_connect` (`:1121-1135`) still re-raise the
    class after the root change. Their `except SerialError` arms no longer match it, so confirm that
    no broad `except Exception` swallows it.
- `exceptions.py`: re-root `HardwareRevisionUnsupportedError(HardwareOperationError)`. Keep the
  `detected=` attribute. Update the docstring: it is raised by `hw_revision_gate`, after the setup
  ack and before the operation ack. Update the comment at `exceptions.py:149`.
- `eprom_operations.py` `_setup_operation`, lease path (`:705-714`): the class is no longer a
  `SerialError`, so the lease link is not dropped on this refusal. Check that `chip_test.py:2592`
  (which treats the error as fatal) still tears down the lease. `cli_handlers.map_typed_errors`
  needs no new arm, because the `HardwareOperationError` arm renders it. Check that no arm above
  that one catches it first.
- `cli_handlers.py`: the `--force` help on `write` (`:632`) and `erase` (`:1401`, confirm the
  line) says it also continues on a shield revision that is not proven, with a warning.
  STE100, no internal refs.

## Task 5: Host — `config --rev` takes silkscreen values

- `cli_handlers.py:1481-1520`:
  - Change `--rev` to `type=click.Choice(["-1", "0", "1", "2", "2.0", "2.1", "2.2", "2.3"])`.
  - Map the value through one table, `REVISION_BY_SILKSCREEN` in `constants.py`, next to the
    `REVISION_*` bytes: `"2.2"` → `REVISION_2_2`, and `"-1"` → the existing `-1` sentinel for
    `set_hardware_config`.
  - Remove the float/int cast comment.
  - Help text (STE100): "Set the shield revision override. Use 2.2 or 2.3 for a shield that has the
    three-position JP4. -1 removes the override."
- No change to `hardware.set_hardware_config`. It already sends `rev` and maps `-1` to `0xFF`.
- When the firmware refuses a value (`MSG_ERR_INVALID_REV`), `config` exits 1 with the rendered
  error. Check that `messages.py` from the sync renders it.

## Task 6: Tests (firestarter_app)

- Rewrite `tests/test_hw_revision_gate.py` against `hw_revision_gate` (production calls with data,
  no source scans):
  - `write` or `erase` with vpp-pin 11 is refused for `REVISION_2_0`, `0xFE`, `0xFF`, `None`, 0
    and 1. It passes for 4 and 5.
  - `read`, `blank` and `verify` with vpp-pin 11 pass for every revision (D-1, both sides).
  - A chip whose vpp-pin is not 11 passes. A `bus-config` that is missing or empty passes, because
    the gated chips always carry vpp-pin 11. Assert this on the real database: exactly the
    `DIP24_2716` and `DIP24_2532` rows get vpp-pin 11, with an exact count.
  - `FLAG_FORCE` set: no raise, and `forced_warning` returns text that contains the upper-case chip
    name. Not refused: `forced_warning` returns `None`.
  - Keep the existing ack-decoding tests and the `_probe_port` integration tests, and update them
    for the new root. The `_probe_port` refusal still propagates. A forced probe returns True and
    the warning goes to stderr.
- `_setup_operation` cold path: the refusal propagates as `HardwareRevisionUnsupportedError`. It is
  not `(None, 0)`. Update `test_setup_operation_has_exactly_three_none_zero_returns` if its count
  changes (read the RED reason first).
- CLI: `write` of `2516` with a mocked ack at `REVISION_2_0` exits 1 with `Hardware error:` and the
  `_REFUSAL_FORMAT` text (import the constant). With `--force` it continues, and stderr has the
  warning.
- `config --rev`: `2.2` sends `rev: 4`, `2.3` sends 5, `2` and `2.0` send 2, `-1` sends `0xFF`.
  `4`, `2.4` and `abc` give a `UsageError` (exit 2) and send no serial bytes.
- `test_fw_update_path_gate.py:123` and `test_chip_test_sdp_leg.py:578-605`: update them for the
  new root and the new command scope.

## Verification

1. Firmware: `cd firestarter_fw && pio test -e native && pio test -e native_nodevtools`. Then build
   leonardo (stable and `DEV_TOOLS=1`) and uno, and report flash and RAM.
2. Host: `cd firestarter_app && pytest tests/ -q` and `ruff check`. Then run the suite in a fresh
   clone with a uv Python 3.11 venv (`testing/standalone-checkout`).
3. Bench (Leonardo on `/dev/ttyACM0`, Rev 2.0 shield; confirm port identity first):
   - Flash the new firmware.
   - `firestarter config --rev 6` is refused by the host (usage error).
   - A raw firmware check of an out-of-range `rev` is refused with `MSG_ERR_INVALID_REV`, and `hw`
     still shows the old value.
   - With no chip in the socket, `firestarter write 2516 <file>` stops with `Hardware error:`,
     exit 1, before any VPP.
   - `firestarter read 2516` is not refused by the gate.
   - `firestarter config --rev 2.2`, then `firestarter hw`, shows Rev 2.2 (override). The write is
     no longer refused by the gate.
   - `firestarter config --rev -1` clears the override.
   - The operator confirms which shield is fitted before the run.
