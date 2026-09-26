# Phase 111: Measured-Voltage Sampler (hardware-gated) - Pattern Map

**Mapped:** 2026-07-03
**Files analyzed:** 4 (all MODIFY; no new files)
**Analogs found:** 4 / 4 (all in-repo, same modules)

> All paths below are in the `firestarter_app/` git submodule. The firmware
> submodule (`firestarter/`) is NOT touched (host-only, additive). RESEARCH
> Pattern A (string re-parse of `Response.message`) is the recommended shape —
> `Response.payload` is `None` for 0xE4/0xE5 (RESEARCH §Make-or-Break), so the
> raw-payload approach from CONTEXT §D-05 is superseded.

## File Classification

| File (MODIFY) | Role | Data Flow | Closest Analog | Match Quality |
|---------------|------|-----------|----------------|---------------|
| `firestarter/hardware.py` | service (HardwareManager method) | request-response (serial DATA-frame stream, bounded) | same file `_read_voltage_loop` + `read_vpp/vpe_voltage` (`hardware.py:166-263`) | exact (sibling method, same class, same handshake) |
| `firestarter/diagnostic_report.py` | model (dataclass + serialization) | transform (fields → `to_dict()` → `render()`) | same file existing `TransportHealth` `_transport_dict()` NOT_MEASURED substitution (`:324-336`, `:379-401`) | exact (same module, established sub-dict pattern) |
| `tests/test_hardware.py` | test | request-response (synthetic wire frames) | same file voltage-read harness (`test_hardware.py:44-120`) + `conftest.py:52 build_frame` | exact |
| `tests/test_diagnostic_report.py` | test | transform (serialization assertions) | same file `test_transport_not_measured` (`:219`) + `test_dual_render_single_source` (`:144`) | exact |

## Pattern Assignments

### `firestarter/hardware.py` (service, bounded request-response)

**Analog:** `_read_voltage_loop` + `read_vpp_voltage`/`read_vpe_voltage` (same file, DO NOT MODIFY these — SC3).

**Add:** `_parse_voltage_frame`, `_sample_one_voltage`, `sample_vpp_mv`, `sample_vpe_mv` as additive siblings.

**Imports pattern** (`hardware.py:9-26`) — extend, do not restructure:
```python
import logging
import time
from typing import Optional, Tuple  # noqa: UP035

from firestarter.config import ConfigManager
from firestarter.constants import (
    COMMAND_CONFIG,
    COMMAND_HW_VERSION,
    COMMAND_READ_VPE,      # =12  (already imported — reuse, no new command)
    COMMAND_READ_VPP,      # =11  (already imported — reuse, no new command)
)
from firestarter.exceptions import (
    HardwareOperationError,
    ProgrammerNotFoundError,
    SerialError,
    SerialTimeoutError,
)
from firestarter.serial_comm import SerialCommunicator
```
New stdlib imports needed for the sampler: `import re`, `import statistics` (add alongside `time`).

**Core handshake pattern to MIRROR** (`hardware.py:182-251`) — the connect → ack → send_ack → get_response loop. The sampler differs only in: (a) stops after N frames (`for _ in range(n)`) instead of `while True`, (b) parses+returns instead of `print(...)`, (c) never touches the CLI path:
```python
command_for_connect = {"state": state_to_set}
if flags:
    command_for_connect["flags"] = flags
comm = None
try:
    comm = SerialCommunicator.find_and_connect(command_for_connect, self.config)
    # Wait for the firmware to signal ready (handshake, prevents race).
    is_ok, msg = comm.expect_ack()
    if not is_ok:
        return False          # sampler: return None
    comm.send_ack()            # start the reading loop on the firmware
    while True:                # sampler: for _ in range(n):
        response = comm.get_response()
        if response.type == "DATA":
            print(f"\r{message}    ", end="", flush=True)   # sampler: parse response.message
            comm.send_ack()    # ack -> request next reading
        ...
finally:
    if comm:
        comm.disconnect()
```

**Error-handling pattern to COPY VERBATIM** (`hardware.py:236-251`) — same except-tuple; sampler returns `None` (never a false 0, honest-fallback):
```python
except (
    ProgrammerNotFoundError,
    SerialError,
    SerialTimeoutError,
    HardwareOperationError,
) as e:
    return None      # (loop variant logs + returns False; sampler is silent -> None)
finally:
    if comm:
        comm.disconnect()
```

**Parse + median pattern** (RESEARCH Pattern 1, §Architecture) — reconstruct mV as `v_int*1000 + v_dec*100` (wire carries whole volts + one tenths digit only, 100 mV resolution — Pitfall 2); tolerant regex (Pitfall 3); `statistics.median` (Pitfall 5, cast `int`); thin `sample_vpp_mv`/`sample_vpe_mv` wrappers over `_sample_one_voltage(COMMAND_READ_VPP|COMMAND_READ_VPE)`, `flags=0` (verified, RESEARCH A3). See RESEARCH lines 296-341 for the full code shape.

---

### `firestarter/diagnostic_report.py` (model, transform)

**Analog:** `TransportHealth`'s `_transport_dict()` NOT_MEASURED substitution (`:324-336`) + `to_dict()` (`:379-401`) + `render()` (`:403-469`).

**Slot to split** (`:303`): `vpp_vpe_mv: int | None = None` → separate VPP/VPE before/after + standalone fields (D-01/D-03/D-04). RESEARCH lines 355-378 give the exact field list and nested `"voltage": {...}` sub-dict shape (flat also acceptable — Open Q2).

**NOT_MEASURED substitution pattern to COPY** (`_transport_dict`, `:324-336`) — this is the module's canonical "ONE place the sentinel is substituted" pattern. Apply identically per voltage field:
```python
def _transport_dict(self) -> dict[str, Any]:
    """Substitute NOT_MEASURED for any None counter -- the ONE place in
    this module that knows the sentinel string (Pitfall 3)."""
    th = self.transport
    return {
        "cobs_errors": NOT_MEASURED if th.cobs_errors is None else th.cobs_errors,
        ...
    }
```
New `_voltage_dict()` helper mirrors this: `NOT_MEASURED if self.vpp_before_mv is None else self.vpp_before_mv`, etc. Sentinel constant at `:42-43`.

**Single-source contract to PRESERVE** (D-01, `to_dict`/`render` docstrings `:379-406`): add the voltage block to `to_dict()` (`:386-401`) ONLY; `render()` must source from `d = self.to_dict()` (`:409`) — add one `table.add_row("voltage", ...)` line (the current slot renders nothing today). Never a second field list. Do NOT switch `to_dict` to `dataclasses.asdict()`.

---

### `tests/test_hardware.py` (test)

**Analog:** voltage-read harness (`:44-120`) — `hw_config` fixture, `make_comm`/`fake_serial`, patch `find_and_connect`, `fake_serial.feed(...)`.

**Harness pattern to COPY** (`:74-88`):
```python
def test_read_vpp_voltage_finish_on_ok(hw_config, make_comm, fake_serial) -> None:
    fake_serial.feed(_ok_frame_bytes())        # ready handshake ("OK: ready\n")
    fake_serial.feed(b"OK: finished\n")        # loop-end signal
    comm = make_comm()
    hw = HardwareManager(hw_config)
    with patch(
        "firestarter.serial_comm.SerialCommunicator.find_and_connect",
        return_value=comm,
    ):
        ok = hw.read_vpp_voltage()
    assert ok is True
```

**Synthetic frame pattern** (`conftest.py:52` `build_frame` — correct CRC8 auto-computed; RESEARCH §Code Examples lines 484-496):
```python
import struct
params = struct.pack(">HHHH", 20, 9, 5, 0)   # VPP 20.9V, VCC 5.0V (big-endian 4xu16)
frame = build_frame(0xE4, params)            # magic|len|id|params|crc|0x0A
fake_serial.feed(b"OK: ready\n")             # expect_ack() handshake
fake_serial.feed(frame); fake_serial.feed(frame); fake_serial.feed(frame)  # N>=3 for median
# patch find_and_connect -> make_comm(); assert hw.sample_vpp_mv() == 20900
```

**Tests to add** (RESEARCH Test Map lines 585-592): `parse_voltage` (→20900), `sample_vpp`/`sample_vpe` (median, states 11/12), `sample_none` (transport error/no-DATA → `None` not 0), `median` (even-N off-grid), `format_pin` (0xE4/0xE5 `CATALOG` format still matches regex — Pitfall 3 guard). Keep existing `:74-120` tests green (SC3 regression).

---

### `tests/test_diagnostic_report.py` (test)

**Analog:** `test_transport_not_measured` (`:219`) + `test_dual_render_single_source` (`:144`).

**NOT_MEASURED assertion pattern to COPY** (`test_transport_not_measured`, `:219`): build a report with `None` voltage fields, assert each serializes to `NOT_MEASURED` in `to_dict()["voltage"]` (never `0`). **Single-source pattern** (`test_dual_render_single_source`, `:144`): assert the split fields surface consistently through both `to_dict()` and `render()`. Bench-free seam: real `EpromDatabase(skip_local_override=True)` + `Mock(spec=[...])` operator (file docstring lines 8-13).

**Tests to add** (RESEARCH line 592): split-field serialization (VPP/VPE before/after/standalone) + `None → NOT_MEASURED` fallback.

## Shared Patterns

### Honest-fallback (NOT_MEASURED / None, never a false 0)
**Source:** `diagnostic_report.py:318-330` (`_transport_dict`) + `hardware.py:236-251` (except → False).
**Apply to:** the sampler (return `None` on error/timeout/no-parse) AND every new voltage report field (`None → NOT_MEASURED` in `to_dict()`). Phase 108/110 precedent. Sentinel at `diagnostic_report.py:42-43`.

### Serial handshake (find_and_connect → expect_ack → send_ack → get_response)
**Source:** `hardware.py:182-251` (`_read_voltage_loop`).
**Apply to:** `_sample_one_voltage`. Do NOT re-derive the ack sequence (the `:190-191` comment warns of a race). Bounded `for _ in range(n)` loop, not `while True`.

### Single-source render (to_dict is canonical, render consumes it)
**Source:** `diagnostic_report.py:373-395` (`to_dict`) + `:403-409` (`render` reads `d = self.to_dict()`).
**Apply to:** all new voltage fields — extend `to_dict()` only; add render rows sourced from the dict. Phase 110 D-01.

### Bench-free synthetic-frame test seam
**Source:** `conftest.py:52` (`build_frame`), `:65-124` (`_FakeSerial`, `fake_serial`, `make_comm`) + `test_hardware.py:44-120` (patch `find_and_connect`).
**Apply to:** all sampler unit tests (D-05 — no hardware). CRC8 auto-computed by `build_frame`; do not hand-assemble frames.

### Orchestrator-only / SAFE-02 (no new dispatch, no VPP-set)
**Source:** `test_diagnostic_report.py:238` (`test_report_module_is_orchestrator_only`).
**Apply to:** the sampler sends `{"state": 11|12}` only — no `vpp_mv`, no raw-wire-dict, no `--force`. Report model imports no transport class. Re-run `tools/check_devtest_orchestrator.py` (Phase 109 AST gate) after wiring.

## No Analog Found

None. Every file in scope is a MODIFY of an existing module with a same-file (or
same-repo) analog. The one CONTEXT-suggested approach without a working analog is
`_decode_param` on `Response.payload` — **superseded** (payload is `None` for
0xE4/0xE5; use Pattern A string re-parse, RESEARCH §Make-or-Break).

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (hardware.py, diagnostic_report.py), `firestarter_app/tests/` (test_hardware.py, test_diagnostic_report.py, conftest.py). Firmware submodule out of scope (host-only).
**Files scanned:** 5 (all cited by RESEARCH; read this session to extract concrete excerpts).
**Pattern extraction date:** 2026-07-03
