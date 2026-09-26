# Phase 53: Byte-Exact Bench Verification (hardware-gated) — Pattern Map

**Mapped:** 2026-06-02
**Files analyzed:** 5 (3 new functions/classes + 2 new test file sections)
**Analogs found:** 5 / 5

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `eprom_operations.py` — new `write_cycle_eprom()` | service | CRUD (erase→write→read N-cycle) | `consistency_check_eprom()` (same file, lines 497–696) + `write_eprom()` (lines 838–872) + `erase_eprom()` (lines 910–933) | exact |
| `serial_comm.py` — fault-inject hook in `send_json_command()` | service | request-response | `send_json_command()` (same file, lines 156–175) — inserting a hook just before `self.send_bytes(frame)` | exact |
| `serial_comm.py` — `FaultInjectingSerialCommunicator` subclass | utility | request-response | `SerialCommunicator._decode_id_frame()` wrapper (same file, lines 225–227) | exact |
| `cli_handlers.py` — `dev write-cycle` + `dev fault-inject` subcommands | controller | request-response | `dev_consistency_check` handler (same file, lines 1030–1117) | exact |
| `tests/test_eprom_operations.py` + `tests/test_serial_comm.py` + `tests/test_cli_handlers.py` — new test cases | test | — | `test_consistency_check.py` (monkeypatch-of-operator-internals) + `test_serial_comm.py` + `test_cli_handlers.py` dev group tests | exact |

---

## Pattern Assignments

### `eprom_operations.py` — new `write_cycle_eprom()` (service, CRUD)

**Primary analog:** `consistency_check_eprom()` — `eprom_operations.py` lines 497–696
**Secondary analogs:** `write_eprom()` lines 838–872, `erase_eprom()` lines 910–933

#### Imports pattern (lines 1–52)

```python
import hashlib
import logging
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple  # noqa: UP035

from firestarter.constants import (
    COMMAND_ERASE,
    COMMAND_READ,
    COMMAND_WRITE,
)
from firestarter.exceptions import (
    EpromOperationError,
    SerialError,
    SerialTimeoutError,
)
```

#### Signature pattern — mirror `consistency_check_eprom` (lines 497–509)

```python
def consistency_check_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    runs: int = 3,
    output_dir: Optional[str] = None,
    keep_files: bool = True,
    max_diffs: int = 10,
    quiet: bool = False,
    operation_flags: int = 0,
    read_settling_us: int = 0,
    read_strobe_us: int = 0,
) -> int:
    """...
    Returns:
        0 -- all N reads byte-identical (PASS)
        1 -- one or more reads diverge (FAIL)
        2 -- hardware / serial / timeout error
    """
```

`write_cycle_eprom()` uses the same `int` return type and 3-way verdict (0/1/2). Signature:

```python
def write_cycle_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    source_image_path: str,
    runs: int = 5,
    output_dir: Optional[str] = None,
    operation_flags: int = 0,
) -> int:
```

#### Output-dir setup pattern (lines 551–555)

```python
if output_dir is None:
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    output_dir = f"consistency-check-{eprom_name}-unknown-board-{timestamp}"
output_path = Path(output_dir)
output_path.mkdir(parents=True, exist_ok=True)
```

#### Core read-loop reuse pattern (lines 573–638) — THE reuse seam for write-leg read-back

```python
for i in range(1, runs + 1):
    run_path = output_path / f"run_{i:02d}.bin"
    logger.info(f"Run {i}/{runs}: reading {eprom_name} -> {run_path}")
    start_t = time.time()

    try:
        with self._operation_context(
            eprom_name,
            eprom_data_dict,
            COMMAND_READ,
            operation_flags,
        ) as (cmd_data, _, op_name):
            if not cmd_data:
                logger.error(f"Run {i}: failed to set up read operation.")
                return 2
            try:
                with open(run_path, "wb") as fh:

                    def _writer(
                        address,
                        data_chunk,
                        _fh=fh,
                        _start=cmd_data.get("address", 0),
                    ):
                        _fh.seek(address - _start)
                        _fh.write(data_chunk)

                    is_ok, _ = self._run_state_machine(
                        op_name,
                        main_phase_handler=self._main_phase_read_data,
                        start_addr=cmd_data.get("address", 0),
                        end_addr=cmd_data.get("memory-size", 0),
                        process_data_chunk_callback=_writer,
                    )
            except IOError as e:  # noqa: UP024
                logger.error(f"Run {i}: file I/O error on {run_path}: {e}")
                return 2

        if not is_ok:
            logger.error(f"Run {i}: hardware/serial error -- read incomplete.")
            return 2

    except EpromOperationError as e:
        logger.error(f"Run {i}: {e}")
        return 2

    bytes_written = run_path.stat().st_size
    sha = hashlib.sha256(run_path.read_bytes()).hexdigest()
    elapsed = time.time() - start_t
    results.append((i, sha, bytes_written))
```

**Write-leg adaptation:** Replace the per-run body with: (a) call `erase_eprom()`, (b) call `write_eprom()`, (c) run the read-back using the block above, (d) compare `sha` against `source_sha`. The `_operation_context + _run_state_machine + _main_phase_read_data` block is copied verbatim — the reuse-not-duplicate rule is preserved.

#### Write entry point pattern (lines 838–872)

```python
def write_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    input_file_path: str,
    operation_flags: int = 0,
    address_str: Optional[str] = None,
) -> bool:
    with self._operation_context(
        eprom_name,
        eprom_data_dict,
        COMMAND_WRITE,
        operation_flags,
        address_str,
    ) as (cmd_data, buf_size, op_name):
        if not cmd_data:
            return False
        logger.info(f"Writing {input_file_path} to {eprom_name.upper()}")
        is_ok, _ = self._run_state_machine(
            op_name,
            main_phase_handler=self._main_phase_send_data,
            input_file_path=input_file_path,
            buffer_size=buf_size,
        )
        return is_ok
```

#### Erase entry point pattern (lines 910–933)

```python
def erase_eprom(
    self,
    eprom_name: str,
    eprom_data_dict: dict,
    operation_flags: int = 0,
    address_str: Optional[str] = None,
) -> bool:
    with self._operation_context(
        eprom_name,
        eprom_data_dict,
        COMMAND_ERASE,
        operation_flags,
        address_str,
    ) as (cmd_data, _, op_name):
        if not cmd_data:
            return False
        logger.info(f"Erasing EPROM {eprom_name.upper()}")
        is_ok, final_msg = self._run_state_machine(op_name)  # no MAIN handler for erase
        return is_ok
```

#### SHA-256 verdict pattern (lines 640–692)

```python
# Verdict
distinct = sorted({r[1] for r in results})
exit_code = 0 if len(distinct) == 1 else 1
verdict = "PASS" if exit_code == 0 else "FAIL"
print(f"\nConsistency check: {verdict}")
print(f"Chip: {eprom_name}  Board: unknown-board  Port: {port}")
print(f"Runs: N={runs}")
print(f"Distinct SHAs: {len(distinct)}")
print(f"Output dir: {output_dir}/")
```

**Write-leg adaptation:** Replace `distinct` comparison with `source_sha != readback_sha` — compare each readback against the source image SHA, not against each other.

---

### `serial_comm.py` — fault-inject hook in `send_json_command()` (service, request-response)

**Analog:** `send_json_command()` — `serial_comm.py` lines 156–175 (the exact insertion site)

#### Core frame-assembly pattern (lines 156–175) — THE injection point

```python
def send_json_command(self, command_dict: dict) -> int:
    """Serialise command_dict as a COBS+CRC8 framed command and send it.

    Frame layout (ADR §4.3, FRAME-05, CRC-01):
        COBS(json_bytes + CRC8(json_bytes)) + 0x00
    """
    self._log_command_details(command_dict)
    json_bytes = json.dumps(command_dict, separators=(",", ":")).encode("ascii")
    crc = _crc8_ccitt(json_bytes)
    body = cobs_encode(json_bytes + bytes([crc]))
    frame = body + b"\x00"
    return self.send_bytes(frame)  # <-- INSERT HOOK IMMEDIATELY BEFORE THIS LINE
```

**Hook insertion (new code):**

```python
    frame = body + b"\x00"
    # PHASE-53 FAULT INJECTION — only active when _fault_inject_outgoing is set
    # (None by default; set only within dev fault-inject subcommand scope).
    # Production path: this attribute does not exist → getattr returns None → no-op.
    _hook = getattr(self, "_fault_inject_outgoing", None)
    if _hook is not None:
        frame = _hook(frame)
    return self.send_bytes(frame)
```

**Default attribute (new, on `SerialCommunicator.__init__`):**

```python
self._fault_inject_outgoing: Optional[Callable[[bytes], bytes]] = None
```

**Fault forms the hook can implement (D-02):**

```python
# Corrupt CRC8 byte: frame[-2] is the byte immediately before the 0x00 delimiter
def corrupt_crc8(frame: bytes) -> bytes:
    return frame[:-2] + bytes([frame[-2] ^ 0x01]) + b"\x00"

# Drop 0x00 delimiter: firmware waits for delimiter until inter-byte timeout fires
def drop_delimiter(frame: bytes) -> bytes:
    return frame[:-1]
```

---

### `serial_comm.py` — `FaultInjectingSerialCommunicator` subclass (utility, request-response)

**Analog:** `_decode_id_frame()` wrapper — `serial_comm.py` lines 225–227 (the override point)

#### The override point pattern (lines 225–227)

```python
def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]:
    """Compatibility wrapper — see codec.decode_id_frame."""
    return codec.decode_id_frame(frame_len, body)
```

#### Ring-fence guard (lines 229–238) — MUST NOT be touched

```python
# =================================================================
# DO NOT MODIFY — v1.9 RCA territory (GATE-1.8d)
# The body of this generator is the host-side baseline for v1.9's
# read-bug RCA. Phase 26 baseline binaries (.planning/v1.6/
# consistency-check-runs/W27C512-leonardo-20260526-*-v2*/) were
# captured against this exact body. Structural-only changes here
# (e.g. type hints on the signature) are OK; any change to the
# byte-by-byte read loop, the magic-preamble dispatch, the
# frame-length read, or the timeout reset semantics MUST be
# flagged and deferred to v1.9 alongside binary re-validation.
# =================================================================
```

#### FaultInjectingSerialCommunicator subclass (new code, NOT in production imports)

```python
class FaultInjectingSerialCommunicator(SerialCommunicator):
    """Test-only subclass for fw→host fault injection.

    NOT imported in production code. Used only within the dev fault-inject
    subcommand scope. Overrides _decode_id_frame to corrupt the body
    bytes before COBS+CRC8 decode — exercising the host decoder's resync
    path (bounded-desync + fail-fast per Phase 50 D-01).

    The body of _read_and_parse_lines() is UNCHANGED (ring-fence preserved).
    """

    def __init__(
        self,
        *args: Any,
        corrupt_incoming_once: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._corrupt_incoming_once = corrupt_incoming_once
        self._fault_fired = False

    def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]:
        if self._corrupt_incoming_once and not self._fault_fired:
            self._fault_fired = True
            # Flip last byte (CRC8 position in the body) before decode.
            # This causes codec.decode_id_frame's CRC8 check to fail,
            # which surfaces as None → _read_and_parse_lines re-syncs.
            body = body[:-1] + bytes([body[-1] ^ 0x01])
        return super()._decode_id_frame(frame_len, body)
```

**Placement:** This class lives in `serial_comm.py` below `SerialCommunicator`, or in a new `firestarter/fault_inject.py` dev-only module. If placed in `serial_comm.py` it must carry full type annotations (mypy strict on this module per CLAUDE.md).

---

### `cli_handlers.py` — `dev write-cycle` + `dev fault-inject` subcommands (controller, request-response)

**Analog:** `dev_consistency_check` handler — `cli_handlers.py` lines 1030–1117

#### Imports already present (lines 1–44)

```python
import sys
from typing import Any, Callable, List, Literal, Optional  # noqa: UP035

import click

from firestarter.chip_resolver import resolve_chip
from firestarter.eprom_operations import EpromOperator, build_flags
from firestarter.exceptions import (
    ChipNotFoundError,
    EpromOperationError,
    FirmwareOutdatedError,
    HardwareOperationError,
    SerialError,
    SerialTimeoutError,
)
```

#### Click option pattern — copy from `dev_consistency_check` (lines 1030–1082)

```python
@dev.command(name="consistency-check")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.option(
    "--runs",
    type=int,
    default=3,
    help="Number of consecutive reads (default 3; minimum 2).",
)
@click.option(
    "--output-dir",
    "output_dir",
    type=str,
    default=None,
    help="Output dir for per-run binaries (default consistency-check-<chip>-<board>-<TS>/).",
)
@click.option(
    "-q", "--quiet", is_flag=True, help="Suppress per-run tqdm progress bars (D-11)."
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force read, even if the chip id doesn't match.",
)
@click.pass_obj
@map_typed_errors
def dev_consistency_check(
    app: AppContext,
    eprom: str,
    runs: int,
    output_dir: Optional[str],
    ...
) -> None:
```

#### Dispatch + 3-way verdict pattern (lines 1104–1117)

```python
eprom_data = resolve_chip(eprom, db=app.db)
verdict_int = app.eprom_operator.consistency_check_eprom(
    eprom,
    eprom_data,
    runs=runs,
    output_dir=output_dir,
    keep_files=keep_files,
    max_diffs=max_diffs,
    quiet=quiet,
    operation_flags=_build_op_flags(force=force),
    read_settling_us=read_settling_us,
    read_strobe_us=read_strobe_us,
)
sys.exit(verdict_int)  # NOT bool-to-int wrap — preserves 0/1/2 verdict
```

**`dev write-cycle` adaptation:**

```python
@dev.command(name="write-cycle")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.argument("source_image", type=click.Path(exists=True))
@click.option("--runs", type=int, default=5, help="Number of write→read-back cycles (default 5).")
@click.option("--output-dir", "output_dir", type=str, default=None)
@click.option("-f", "--force", is_flag=True)
@click.pass_obj
@map_typed_errors
def dev_write_cycle(
    app: AppContext,
    eprom: str,
    source_image: str,
    runs: int,
    output_dir: Optional[str],
    force: bool,
) -> None:
    """Erase → write source image → read-back N times; assert SHA-256 == source SHA."""
    eprom_data = resolve_chip(eprom, db=app.db)
    verdict_int = app.eprom_operator.write_cycle_eprom(
        eprom,
        eprom_data,
        source_image_path=source_image,
        runs=runs,
        output_dir=output_dir,
        operation_flags=_build_op_flags(force=force),
    )
    sys.exit(verdict_int)
```

**`dev fault-inject` adaptation:**

```python
@dev.command(name="fault-inject")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.option(
    "--direction",
    type=click.Choice(["outgoing", "incoming"]),
    default="outgoing",
    help="outgoing = corrupt host→fw frame; incoming = mutate fw→host frame.",
)
@click.option(
    "--fault-form",
    "fault_form",
    type=click.Choice(["corrupt-crc8", "drop-delimiter"]),
    default="corrupt-crc8",
)
@click.option("--output-dir", "output_dir", type=str, default=None)
@click.pass_obj
@map_typed_errors
def dev_fault_inject(
    app: AppContext,
    eprom: str,
    direction: str,
    fault_form: str,
    output_dir: Optional[str],
) -> None:
    """Demonstrate COBS resync: inject a corrupted frame and assert recovery on the next."""
    eprom_data = resolve_chip(eprom, db=app.db)
    ok = app.eprom_operator.fault_inject_cycle(
        eprom,
        eprom_data,
        direction=direction,
        fault_form=fault_form,
        output_dir=output_dir,
    )
    sys.exit(0 if ok else 1)
```

---

### Tests — new test cases in existing test files (test)

**Analogs:**
- `tests/test_consistency_check.py` — monkeypatch-of-operator-internals pattern
- `tests/test_serial_comm.py` — `SerialCommunicator` unit test pattern
- `tests/test_cli_handlers.py` — `dev` group CliRunner pattern

#### Monkeypatch-of-operator-internals pattern (from `test_consistency_check.py` lines 76–110)

```python
def _make_fake_ctx(memory_size: int = _PAYLOAD_SIZE):
    """Return a @contextmanager-decorated fake _operation_context."""
    @contextmanager
    def fake_ctx(self, eprom_name, eprom_data_dict, cmd, *a, **kw):
        yield {"address": 0, "memory-size": memory_size}, 512, "READ"
    return fake_ctx

def _make_fake_state_machine_with_payloads(payloads):
    """Fake _run_state_machine that feeds successive payloads to the callback."""
    counter = {"i": 0}
    def fake_state_machine(self, op_name, **kwargs):
        cb = kwargs["process_data_chunk_callback"]
        payload = payloads[counter["i"]]
        counter["i"] += 1
        cb(0, payload)
        return (True, None)
    return fake_state_machine, counter
```

**Usage pattern (lines 121–147):**

```python
def test_all_runs_identical_pass_exit_0(self, tmp_path, monkeypatch):
    identical = _identical_payload()
    fake_sm, counter = _make_fake_state_machine_with_payloads(
        [identical, identical, identical]
    )
    monkeypatch.setattr(EpromOperator, "_operation_context", _make_fake_ctx())
    monkeypatch.setattr(EpromOperator, "_run_state_machine", fake_sm)

    op = EpromOperator(ConfigManager())
    rc = op.consistency_check_eprom(
        "TEST_CHIP",
        eprom_data_dict={"memory-size": _PAYLOAD_SIZE},
        runs=3,
        output_dir=str(tmp_path / "out"),
        keep_files=True,
        quiet=True,
    )
    assert rc == 0
```

**New test adaptations for `write_cycle_eprom`:**

```python
# test_write_cycle_eprom_pass: mock erase_eprom→True, write_eprom→True,
# _run_state_machine feeds identical payload, assert rc == 0
# test_write_cycle_eprom_mismatch: feed payload != source_image bytes, assert rc == 1
# test_write_cycle_eprom_hw_error: _run_state_machine returns (False, "timeout"), assert rc == 2
```

#### SerialCommunicator unit test pattern (from `test_serial_comm.py` lines 1–80)

```python
# Constructor bypass via __new__ (from conftest.py lines 127–145):
instance = SerialCommunicator.__new__(SerialCommunicator)
instance.connection = fake_serial
instance.port_name = "/dev/null"
instance.baud_rate = 250000
instance.timeout = 0.1
instance.programmer_info = None

# CRC8 + COBS decode for verifying frame mutation:
from firestarter.frame_parser import _crc8_ccitt, cobs_decode
```

**New tests for fault-inject hook in `send_json_command`:**

```python
def test_fault_inject_outgoing_none(make_comm, monkeypatch):
    """When _fault_inject_outgoing is None, frame is sent unmodified."""
    comm = make_comm()
    comm._fault_inject_outgoing = None
    sent = []
    monkeypatch.setattr(comm, "send_bytes", lambda b: sent.append(b) or len(b))
    comm.send_json_command({"cmd": 1})
    assert sent[0][-1] == 0x00  # delimiter present
    body = cobs_decode(sent[0][:-1])
    crc = body[-1]
    payload = body[:-1]
    assert crc == _crc8_ccitt(payload)  # CRC intact

def test_fault_inject_outgoing_corrupt_crc8(make_comm, monkeypatch):
    """When _fault_inject_outgoing flips frame[-2], CRC8 is corrupted."""
    comm = make_comm()
    comm._fault_inject_outgoing = lambda f: f[:-2] + bytes([f[-2] ^ 0x01]) + b"\x00"
    sent = []
    monkeypatch.setattr(comm, "send_bytes", lambda b: sent.append(b) or len(b))
    comm.send_json_command({"cmd": 1})
    body = cobs_decode(sent[0][:-1])
    crc = body[-1]
    payload = body[:-1]
    assert crc != _crc8_ccitt(payload)  # CRC is now wrong
```

#### CliRunner dev-group pattern (from `test_cli_handlers.py` lines 566–595)

```python
def test_dev_consistency_check_pass_verdict(runner: CliRunner) -> None:
    operator = Mock(spec=EpromOperator)
    operator.consistency_check_eprom.return_value = 0
    app = make_app_context(eprom_operator=operator)
    result = runner.invoke(cli, ["dev", "consistency-check", "W27C512"], obj=app)
    assert result.exit_code == 0

def test_dev_consistency_check_hardware_error_verdict(runner: CliRunner) -> None:
    operator = Mock(spec=EpromOperator)
    operator.consistency_check_eprom.return_value = 2
    app = make_app_context(eprom_operator=operator)
    result = runner.invoke(cli, ["dev", "consistency-check", "W27C512"], obj=app)
    assert result.exit_code == 2  # NOT bool-to-int wrap
```

**New test adaptations for `dev write-cycle` + `dev fault-inject`:**

```python
def test_dev_write_cycle_pass(runner: CliRunner, tmp_path) -> None:
    operator = Mock(spec=EpromOperator)
    operator.write_cycle_eprom.return_value = 0
    app = make_app_context(eprom_operator=operator)
    source = tmp_path / "source.bin"
    source.write_bytes(b"\xaa" * 65536)
    result = runner.invoke(cli, ["dev", "write-cycle", "W27C512", str(source)], obj=app)
    assert result.exit_code == 0

def test_dev_fault_inject_pass(runner: CliRunner) -> None:
    operator = Mock(spec=EpromOperator)
    operator.fault_inject_cycle.return_value = True
    app = make_app_context(eprom_operator=operator)
    result = runner.invoke(cli, ["dev", "fault-inject", "W27C512"], obj=app)
    assert result.exit_code == 0
```

#### `fake_serial` + `make_comm` fixtures pattern (from `conftest.py` lines 65–145)

```python
# _FakeSerial: BytesIO-backed stand-in for serial.Serial.
# Key interface: read(n), write(data), flush(), feed(data) [test-side injection].
# feed() appends to the readable buffer from the test side.
fake_serial.feed(build_frame(MSG_INIT_DONE, b""))
fake_serial.feed(build_frame(MSG_MAIN_DONE, b""))
fake_serial.feed(build_frame(MSG_END_DONE, b""))

# make_comm: factory using __new__ to bypass __init__ (no real serial.Serial).
instance = SerialCommunicator.__new__(SerialCommunicator)
instance.connection = fake_serial
```

---

## Shared Patterns

### 3-way verdict contract (0=PASS / 1=FAIL / 2=hw-error)
**Source:** `consistency_check_eprom()` — `eprom_operations.py` lines 513–515, 620–624, 641–642
**Apply to:** `write_cycle_eprom()` and the `dev write-cycle` CLI handler

```python
# Map state machine failure to verdict 2 (NOT 1):
if not is_ok:
    logger.error(f"Run {i}: hardware/serial error -- read incomplete.")
    return 2

# Verdict logic:
distinct = sorted({r[1] for r in results})
exit_code = 0 if len(distinct) == 1 else 1

# CLI handler: direct sys.exit — do NOT bool-to-int wrap:
sys.exit(verdict_int)  # sys.exit(0 if ok else 1) would collapse 2→1
```

### `_operation_context` + `_run_state_machine` pair
**Source:** `consistency_check_eprom()` read loop — `eprom_operations.py` lines 580–624
**Apply to:** `write_cycle_eprom()` read-back step (copied verbatim per reuse-not-duplicate rule)

```python
with self._operation_context(
    eprom_name, eprom_data_dict, COMMAND_READ, operation_flags,
) as (cmd_data, _, op_name):
    if not cmd_data:
        return 2
    with open(run_path, "wb") as fh:
        def _writer(address, data_chunk, _fh=fh, _start=cmd_data.get("address", 0)):
            _fh.seek(address - _start)
            _fh.write(data_chunk)
        is_ok, _ = self._run_state_machine(
            op_name,
            main_phase_handler=self._main_phase_read_data,
            start_addr=cmd_data.get("address", 0),
            end_addr=cmd_data.get("memory-size", 0),
            process_data_chunk_callback=_writer,
        )
```

### Error handling: `EpromOperationError` catch at run boundary
**Source:** `consistency_check_eprom()` — `eprom_operations.py` lines 626–628
**Apply to:** `write_cycle_eprom()` per-cycle loop

```python
except EpromOperationError as e:
    logger.error(f"Run {i}: {e}")
    return 2
```

### `@map_typed_errors` + `@click.pass_obj` decorator stack
**Source:** `dev_consistency_check` handler — `cli_handlers.py` lines 1081–1082
**Apply to:** All new `dev` subcommand handlers

```python
@click.pass_obj
@map_typed_errors
def dev_write_cycle(app: AppContext, eprom: str, ...) -> None:
```

### `resolve_chip(eprom, db=app.db)` chip-resolution call
**Source:** `cli_handlers.py` line 1104
**Apply to:** All new `dev` subcommand handlers that need chip config

```python
eprom_data = resolve_chip(eprom, db=app.db)
```

### Ring-fence constraint on `_read_and_parse_lines`
**Source:** `serial_comm.py` lines 229–238 (GATE-1.8d comment block)
**Apply to:** `FaultInjectingSerialCommunicator` — the subclass overrides only `_decode_id_frame` (lines 225–227); the generator body (lines 240–365) is BYTE-IDENTICAL in the production class.

### mypy strict + type annotation requirement
**Source:** CLAUDE.md — mypy strict applies to `serial_comm.py`, `cli_handlers.py`
**Apply to:** `FaultInjectingSerialCommunicator` and all new Click handlers

```python
# All new methods must carry full type annotations:
def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]: ...
def write_cycle_eprom(self, ...) -> int: ...
```

---

## No Analog Found

All new files have direct analogs in the existing codebase. No entries in this section.

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (eprom_operations.py, serial_comm.py, cli_handlers.py, frame_parser.py), `firestarter_app/tests/` (test_consistency_check.py, test_serial_comm.py, test_cli_handlers.py, conftest.py)
**Files read:** 10 source and test files
**Pattern extraction date:** 2026-06-02
