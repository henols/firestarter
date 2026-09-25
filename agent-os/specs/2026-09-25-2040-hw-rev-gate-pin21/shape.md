# Shield-Revision Gate for VPP-on-Pin-21 Chips — Shaping Notes

## Scope

A 24-pin chip with VPP on chip pin 21 needs a Rev 2.2 or Rev 2.3 shield. The pin maps are
`DIP24_2716` and `DIP24_2532`, for example the TI 2516. When the host sends the chip config, the
firmware replies with `MSG_OK_READY`. That reply carries the hardware-revision byte, and the host
then checks it. On a `write` or `erase` with a shield that is not proven to be Rev 2.2/2.3, the host
stops with an error. `--force` continues with a warning.

The firmware cannot tell Rev 2.2 from Rev 2.0. The operator therefore sets the override one time
with `firestarter config --rev 2.2`, and the firmware stores it in the Arduino EEPROM.

The host check already existed (`serial_comm.py` `_validate_hardware_revision`). This work closes
five gaps in it:

- `--force` had no effect.
- Every command was refused, `read` included.
- The refusal was hidden on a cold connect.
- `--rev 2.2` truncated to `2`, which is Rev 2.0.
- The firmware stored any `rev` value.

## Decisions

- **D-1. Commands checked:** `write` and `erase` only (operator). `read`, `blank` and `verify`
  pass on every shield with no warning. On a 0x0B write, the blank-guard read runs first and passes,
  and then the write's own connect is refused. That extra read of a 2–4 KiB part is accepted.
- **D-2. Chips checked:** `bus-config.vpp-pin == 11`, as before. The revisions that pass are the
  allowlist {Rev 2.2, Rev 2.3}. Every other value is refused, including unknown and absent values
  (fail closed).
- **D-3. `--force`** is read from the wire dict (`FLAG_FORCE`). When it is set, the operation
  continues and a warning prints at default verbosity (`click.echo`, stderr).
- **D-4.** `HardwareRevisionUnsupportedError` moves under `HardwareOperationError`. It renders as
  `Hardware error: …` and exits 1. `_setup_operation` no longer catches it.
- **D-5.** The policy moves to the pure module `hw_revision_gate.py`. It runs after the ack, not
  before the serial port opens. This is a recorded deviation from `host/pre-serial-gates`: the
  revision is only known from the firmware.
- **D-6. `config --rev`** takes silkscreen values only (operator): `0 1 2 2.0 2.1 2.2 2.3`, and
  `-1` to clear the override. The raw bytes `4` and `5` are refused.
- **D-7. Firmware range check (operator):** `rev` must be 0–5 or 0xFF. Any other value gets
  `MSG_ERR_INVALID_REV`, and the RAM and EEPROM config do not change.
- **D-8. Branches:** `v1.42-hw-rev-gate` in both sub-repos, made from `v1.42-jumper-display`.

## Changes from the plan, made during the build

- **D-5 call site.** The gate is called by `EpromOperator._setup_operation`
  (`_check_shield_revision`), on the cold connect and on the leased connect. It is not called by
  `SerialCommunicator.setup_command`. The wire dict carries no chip name, and `host/refusal-text`
  needs the name. Every write and erase connects through `_setup_operation`. The call still comes
  after the setup ack and before the host answers it. A refusal drops the link.
- **D-7 payload.** `MSG_ERR_INVALID_REV` (0xC1) has no params. A value such as `-1` or `"4"` has no
  number to report.
- **D-7 atomicity.** `parse_json` parses a `CMD_CONFIG` into a copy of the config. It commits and
  saves the copy only when every field is valid. So a refused `rev` also leaves an `r1` or `r2` in
  the same command unapplied. `get_rev` accepts only 1–3 decimal digits in a JSON number, so `-1`,
  `2.2` and `"4"` are refused and are not coerced.

## Context

- **Visuals:** none.
- **References:** see `references.md`.
- **Product alignment:** Mission "Fail closed" and "A wrong choice can … damage an irreplaceable
  chip". Mission scope: no shield revision senses JP4. That is why the operator must assert
  Rev 2.2.

## Standards Applied

- host/typed-refusals — re-root under `HardwareOperationError`. No new verbatim arm.
- host/refusal-text — module-level format constants, STE100, chip name in upper case, escapes
  named.
- host/gate-polarity — fail closed. The escapes are the CLI option `--force` and `config --rev`.
- host/echo-vs-logger — the forced warning changes what the operation does, so it uses
  `click.echo`.
- host/help-docstrings, host/command-skeleton — the `--rev` and `--force` help text.
- host/pre-serial-gates — the pure-module shape. See D-5 for the deviation.
- firmware/fail-closed-refusals, firmware/logging-ids, firmware/size-reporting — the `rev` range
  check.
- protocol/message-catalog, protocol/rollout-compatibility — the new error ID. The firmware ships
  first.
- testing/* — non-vacuity, no source scans, standalone checkout, both native envs.
