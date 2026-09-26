# Phase 111: Measured-Voltage Sampler (hardware-gated) - Research

**Researched:** 2026-07-02
**Domain:** Host-side serial-frame parsing (Python) — value-returning VPP/VPE mV sampler + wiring into the `dev test` sweep report
**Confidence:** HIGH (all claims grounded in current source at `firestarter_app/...:line` and `firestarter/...:line`; the one design-shaping surprise — see §Make-or-Break — is verified against the live decode path)

## Summary

Phase 111 adds a **value-returning** sibling to the existing print-and-return-`bool`
VPP/VPE monitor in `hardware.py`, and records the parsed rail voltage into the
Phase-110 `DiagnosticReport`. The work is host-only and additive: it reuses the
existing `COMMAND_READ_VPP=11` / `COMMAND_READ_VPE=12` monitor command path
(`constants.py:66-67`), sets no VPP, builds no protocol command, and adds no
firmware dispatch entry.

**One surprise dominates the plan** and overturns a CONTEXT §D-05 assumption:
the raw 4×u16 payload of the `MSG_DATA_VPP_VOLTAGE` (0xE4) / `MSG_DATA_VPE_VOLTAGE`
(0xE5) frames is **decoded and then discarded** — `codec.py` computes the values,
renders the human string, and returns a `LogMessage` whose `payload` is `None` for
everything except `MSG_DATA_CHUNK` (`codec.py:269-282`). By the time a frame
reaches the read loop as a `Response`, only the formatted string
`"VPP: 20.9V, Internal VCC: 5.0V"` survives (`Response.message`); `Response.payload`
is `None`. So "parse the raw payload via `frame_parser._decode_param`" (CONTEXT
§D-05 / Discretion) **is not possible against today's `Response`** — the raw bytes
never arrive. The planner must pick one of two shapes (§Architecture Patterns,
Pattern A vs B).

**The second surprise sizes the units contract:** the firmware does NOT put
millivolts on the wire. `hw_read_voltage` reads a real `voltage_mv` from the ADC
but transmits only `v_int` (whole volts) and `v_dec` (a single tenths digit),
rounded to 100 mV (`hardware_operations.cpp:60-73`). A function named
`sample_vpp_mv()` is achievable but its resolution is **100 mV**, and the mV value
must be *reconstructed* as `v_int*1000 + v_dec*100` — it is not a first-class mV
integer read off the frame. Success Criterion 2 ("parsed mV matches the
previously-printed value") is satisfiable because both derive from the same two
integers, but the report must not imply mV precision it does not have.

**Primary recommendation:** Implement the sampler as **Pattern A (string re-parse
of `Response.message`)** — a private `_parse_voltage_frame(message: str) -> int | None`
that regex-extracts the `%u.%uV` pair and returns reconstructed mV, plus a
`_sample_one_voltage(state, flags) -> int | None` that runs the existing
find_and_connect → expect_ack → send_ack handshake, reads N DATA frames, and
returns the **median** of the parsed mV values (D-02). `sample_vpp_mv()` /
`sample_vpe_mv()` are thin wrappers over it (states 11/12). Do **not** touch
`_read_voltage_loop` (SC3). Wire the sampler at the **Phase-112 orchestration
layer around `run_plan`**, not inside `chip_test.run_plan` (§Q4). Test entirely
bench-free with synthetic `build_frame(0xE4, struct.pack(">HHHH", ...))` frames;
defer the live SC2 confirmation to a bench UAT (D-05).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Parse 0xE4/0xE5 frame → mV int | Host — `hardware.py` (new private parse helper) | `frame_parser` / `codec` (only if Pattern B) | VOLT-01 is explicitly host-side; the frame already exists on the wire |
| Sample N frames, take median | Host — `hardware.py` `HardwareManager` | — | Reuses the existing serial handshake; same class that owns `read_vpp_voltage` |
| Record mV into report | Host — `diagnostic_report.py` (new fields) + Phase-112 orchestrator | — | The report model owns the slot; the orchestrator supplies the value |
| Decide *when* to sample (before/after/standalone) | Host — Phase-112 orchestrator around `run_plan` | `chip_test` (only if sampler is threaded in) | Sampling is a self-contained serial op independent of `write_eprom` (D-03) |
| Firmware voltage emit | Firmware (UNCHANGED) | — | `hw_read_voltage` already emits the frame; **no firmware change in this phase** |

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01 (LOCKED): Sample BOTH rails; split the report's one slot into two.** The write
  step captures VPP **and** VPE every destructive run. Expand the Phase-110 single
  combined `vpp_vpe_mv: int | None` slot (`diagnostic_report.py:297`) into separate
  VPP/VPE fields. Rejected: sampling only the protocol-relevant rail; rejected VPP-only.
  Keep the single-source `to_dict()`/`render()` contract (Phase 110 D-01) intact when
  adding fields.
- **D-02 (LOCKED): N samples per rail → report the MEDIAN.** Grab a few frames from the
  read loop and record the median mV. N = **3–5**, exact value planner's discretion.
  Recording the raw sample count/samples is discretionary. Rejected: single reading;
  rejected min.
- **D-03 (LOCKED): Sample BEFORE and AFTER the write step** (two independent regulator
  reads per rail → up to 4 sample points on a destructive run). The VPP/VPE read is a
  self-contained serial command and `write_eprom` is a self-contained INIT→MAIN→END op —
  the rail **cannot** be tapped mid-pulse, so before/after are two *independent*
  energizations bracketing the write. Gives an across-write droop signal. Rejected:
  before-only or after-only.
- **D-04 (LOCKED): Fire the sampler on non-destructive runs too** — take a single
  standalone VPP+VPE read even when there is no write step, as a "can your rig reach
  VPP/VPE?" diagnostic. Safe: the read energizes the regulator and measures only, with
  **no A9/VPE/P1 socket routing** (`reference_vpp_vpe_no_socket_routing`) — safe with a
  chip seated. On a non-destructive run the before/after slots are `NOT_MEASURED`
  (nothing to bracket); the standalone reading fills the plain VPP/VPE field. Any absent
  reading (sampler error/timeout, frame not emitted) → `NOT_MEASURED`, never a false 0.
- **D-05 (LOCKED): Ship software-complete + unit-tested now; DEFER the live SC2 check.**
  Build + unit-test the sampler against **recorded/synthetic 0xE4/0xE5 frames**; defer
  the live "parsed mV == printed monitor value" confirmation on Leonardo + Rev 2.0 to a
  bench session as a **HUMAN-UAT / FUT item**. Phase 112 proceeds on the sampler API
  immediately. When bench-validated later: the non-destructive standalone read is
  checkable against `firestarter vpp`/`vpe` with any chip seated; the before/after write
  path can use an electrically-erasable chip (W27C512 / W29C020). Standing bench
  discipline: live R1/R2 readback + verify `controller:` port identity per task; Leonardo
  is chip-OUT-sideload-exempt.

### Claude's Discretion
- **Exact mV computation from the `%u.%uV` (whole/frac) frame** — CONTEXT prefers parsing
  the raw `param_bytes` via `frame_parser._decode_param`; **RESEARCH finds this path is
  NOT available on today's `Response` (see §Make-or-Break) — the planner must choose
  Pattern A (string re-parse) or Pattern B (extend plumbing).** Confirm fractional-unit
  scaling (RESEARCH: whole volts + single tenths digit; reconstructed mV =
  `v_int*1000 + v_dec*100`, 100 mV resolution).
- **Additive-sibling refactor** — extract a single-frame parse helper that both the new
  sampler and (optionally) the existing `_read_voltage_loop` can call; **do NOT alter
  `_read_voltage_loop`'s printing/loop behavior** (SC3). Exact N (3–5), whether to record
  raw samples, and flat-vs-nested voltage field shape are planner's call within D-01..D-04.
- **`flags` passed to the read command** — default `flags=0` unless research surfaces a
  needed flag. **RESEARCH: no flag is needed** — the firmware read path
  (`hardware_operations.cpp:15-81`) consults no `flags` bit for VPP/VPE reads; `flags=0`
  is correct.

### Deferred Ideas (OUT OF SCOPE)
- **SC2 live hardware validation (Leonardo + Rev 2.0)** — deferred to a bench session as a
  HUMAN-UAT / FUT item per D-05. The software (sampler + wiring + unit tests against
  synthetic frames) closes this phase; the live "parsed mV == printed monitor value"
  confirmation is the deferred hardware gate.
- **Todo matcher's 8 matches** (1 @ 0.9 firmware VPP-check, 7 @ 0.6) — all off-axis for a
  host-only frame-parse phase; none folded (same disposition as Phases 109/110).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VOLT-01 | A value-returning VPP/VPE mV sampler in `hardware.py` (parsing the `MSG_DATA_VPP/VPE_VOLTAGE` frames the current monitor only prints) captures the tester's actual rail voltage during the write step into the report. | §Make-or-Break (where the value lives on the wire + why payload path is unavailable), §Architecture Patterns (Pattern A/B sampler shape), §Q3 (report slot), §Q4 (write-step wiring), §Validation Architecture (bench-free test strategy for the parser). |
</phase_requirements>

## Make-or-Break: Where the millivolt value actually lives on the wire

This is the single feasibility question that reshapes the plan. Answered end-to-end
against live source.

### Firmware emit site (what is actually transmitted)

`firestarter/src/hardware_operations.cpp:60-73`:

```c
uint16_t vcc_mv = rurp_read_vcc_mv();
uint16_t voltage_mv = rurp_read_voltage_mv();          // real mV from ADC
// Compute pre-rounded integer/decimal tenths for each voltage (catalog expects 4 x u16).
uint16_t v_int  = (uint16_t)((voltage_mv + 50) / 1000);      // whole volts
uint16_t v_dec  = (uint16_t)(((voltage_mv + 50) / 100) % 10); // ONE tenths digit
uint16_t vc_int = (uint16_t)((vcc_mv + 50) / 1000);
uint16_t vc_dec = (uint16_t)(((vcc_mv + 50) / 100) % 10);
if (handle->cmd == CMD_READ_VPE)
    LOG_DATA_ID_U16x4(MSG_DATA_VPE_VOLTAGE, v_int, v_dec, vc_int, vc_dec);
else
    LOG_DATA_ID_U16x4(MSG_DATA_VPP_VOLTAGE, v_int, v_dec, vc_int, vc_dec);
```

- `[VERIFIED: firestarter/src/hardware_operations.cpp:60-73]` The firmware **discards
  sub-100 mV precision before transmitting.** The wire carries four u16s:
  `(rail_whole, rail_tenths, vcc_whole, vcc_tenths)`. The true `voltage_mv` never
  leaves the firmware.
- `[VERIFIED: firestarter/include/logging_id.h:194-205]` `LOG_DATA_ID_U16x4` packs each
  u16 **big-endian (MSB first)** into 8 bytes. Matches the host `_decode_param("u16")`
  which uses `struct.unpack_from(">H", ...)` (`frame_parser.py:150-151`). **No endianness
  risk on the payload path.**
- **Reconstructed mV = `v_int*1000 + v_dec*100`** → resolution is 100 mV. A named
  `sample_vpp_mv()` returning an `int` in mV is honest as long as the report/docs do not
  claim finer than 100 mV. `[ASSUMED]` (arithmetic is verified; the *labeling* choice —
  whether to call it mV, or `rail_dV` tenths, is a planner decision flagged in
  §Assumptions Log A1).

### Host receive site (what actually survives to the read loop)

`firestarter/frame_parser.py:17-19` — the `Response` namedtuple:
```python
Response = namedtuple("Response", ["type", "message", "payload", "id"], defaults=[None, None])
```

`firestarter/codec.py:236-282` — the decode path:
1. `_decode_param` decodes the 4 u16 params into `values` (`codec.py:236-247`).
2. `format_message(0xE4, values, entry)` returns `None` (0xE4/0xE5 are not P-02/P-03
   sentinel IDs), so `text` falls through to `entry.format % tuple(fmt_values)` →
   `"VPP: 20.9V, Internal VCC: 5.0V"` (`codec.py:252-267`).
3. **`chunk_payload` is set ONLY for `MSG_DATA_CHUNK` (0xE6)** (`codec.py:269-277`); for
   0xE4/0xE5 it stays `None`.
4. `return LogMessage(severity=..., text=text, id=msg_id, payload=chunk_payload)`
   (`codec.py:280-282`).

`firestarter/serial_comm.py:394-399` builds the `Response` from the `LogMessage`:
`payload=decoded.payload` → **`None` for 0xE4/0xE5.**

- `[VERIFIED: firestarter/codec.py:269-282 + firestarter/serial_comm.py:394-399]` **The
  decoded 4×u16 values are NOT propagated on `Response`.** They exist only transiently
  inside `codec.py`. `Response.payload` is `None` for a voltage frame;
  `Response.message` carries the human string. This directly refutes the CONTEXT §D-05
  premise "parse the raw `param_bytes` via the existing `frame_parser._decode_param` u16
  machinery" — those bytes are not reachable from a `Response`.

### Consequence for the planner (pick one)

- **Pattern A — re-parse `Response.message` (RECOMMENDED, smallest surface):** regex the
  `"VPP: %u.%uV"` / `"VPE: %u.%uV"` string. Zero change to `frame_parser`, `codec`,
  `serial_comm`. Cost: couples the sampler to the catalog **format-string wording**
  (`messages.py:685` / `:694`). Guard by making the parser tolerant (match `r"(\d+)\.(\d+)\s*V"`
  anywhere in the string) and by pinning the format string in a test.
- **Pattern B — extend the plumbing to carry decoded params:** add a `params` field to
  `LogMessage`/`Response` (mirroring how `payload` was added for `MSG_DATA_CHUNK` in
  W-04), populate it in `codec.py`, and have the sampler read the structured values.
  Cleaner value semantics (no string coupling) but touches `frame_parser.Response`
  (`:17`), `codec.py` (`:280-282`), and `serial_comm.py` (`:394-399`) — all in the
  strict-mypy set. Larger blast radius; still host-only/additive.

**Recommendation: Pattern A.** It keeps the change inside `hardware.py` (SC3-safe,
matches the "additive sibling" framing), avoids editing three transport modules, and the
format-string coupling is fully pinned by a one-line regression test on `messages.py`'s
0xE4/0xE5 format. Pattern B is only worth it if a later phase needs structured params
from other DATA frames.

## Standard Stack

No new packages. The phase is pure host-side Python over the existing dependency set.

### Core (already in the project — reuse only)
| Module | Purpose | Why Standard |
|--------|---------|--------------|
| `firestarter/hardware.py` | `HardwareManager` — owns `_read_voltage_loop` + `read_vpp/vpe_voltage`; new sampler lives here | The class already holds the serial handshake the sampler needs (`hardware.py:166-263`) |
| `firestarter/serial_comm.py` `SerialCommunicator` | `find_and_connect` / `expect_ack` / `send_ack` / `get_response` | The existing per-op transient-connection pattern (`hardware.py:188-201`) |
| `firestarter/diagnostic_report.py` `DiagnosticReport` | The report the mV lands in; add VPP/VPE fields to `to_dict()` (`:379-401`) | Phase-110 single-source render contract; `NOT_MEASURED` sentinel (`:43`) |
| `statistics.median` (stdlib) | Median of N samples (D-02) | Stdlib; handles even/odd N; no dep |
| `re` (stdlib) | Regex the `%u.%uV` string (Pattern A) | Stdlib |
| `struct` (stdlib) | Build synthetic test frames (`>HHHH`) | Stdlib; already used in `frame_parser`/tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `statistics.median` | hand-rolled sort+midpoint | median is stdlib, correct for even N (mean of two middle) — but see Pitfall 5 (mV stays a clean multiple of 50 only for odd N; for even N the mean of two 100-mV-grid values can land on a 50-mV value — acceptable, document it) |
| Pattern A string re-parse | Pattern B structured params on `Response` | A = 1 module touched; B = 3 modules (transport core) touched. A recommended. |
| Sampler inside `run_plan` | Sampler at Phase-112 orchestrator | Orchestrator keeps `run_plan`'s operator-only contract clean (§Q4) |

## Architecture Patterns

### System Architecture Diagram

```
                         dev test <chip>  (Phase 112 orchestrator — NOT this phase's CLI)
                                    │
             ┌──────────────────────┼───────────────────────────────┐
             │                      │                                │
   (before write)            run_plan(plan, operator, db)      (after write)
   sample VPP+VPE  ───────►  [chip_test.py: id→read→blank      ◄─── sample VPP+VPE
   (this phase)               →WRITE→verify→erase steps]            (this phase)
        │                            │                                   │
        ▼                            ▼                                   ▼
  HardwareManager.sample_vpp_mv() / sample_vpe_mv()   ← THIS PHASE'S NEW API (hardware.py)
        │
        ▼
  _sample_one_voltage(state=11|12, flags=0)           ← reuses the existing handshake
        │  find_and_connect → expect_ack → send_ack → get_response × N
        ▼
  SerialCommunicator.get_response()  ──►  Response(type="DATA", message="VPP: 20.9V, ...", payload=None, id=0xE4)
        │
        ▼
  _parse_voltage_frame(message) -> int mV | None      ← regex %u.%uV  → v_int*1000 + v_dec*100
        │
        ▼   (median of N parsed mV, per rail)
  DiagnosticReport.vpp_before_mv / vpp_after_mv / vpe_before_mv / vpe_after_mv   (D-01/D-03)
  DiagnosticReport.vpp_mv / vpe_mv  (standalone, D-04)     — None → "not measured" (D-04)
```

Component-to-file mapping:
- New sampler API + parse helper: `firestarter_app/firestarter/hardware.py`
- Report fields (split `vpp_vpe_mv`): `firestarter_app/firestarter/diagnostic_report.py`
- When-to-sample orchestration: Phase-112 layer that calls `chip_test.run_plan`
  (do NOT modify `run_plan`; see §Q4)

### Recommended Project Structure
No new files. Edits confined to:
```
firestarter_app/firestarter/
├── hardware.py              # + _parse_voltage_frame, _sample_one_voltage, sample_vpp_mv, sample_vpe_mv
├── diagnostic_report.py     # split vpp_vpe_mv -> vpp_*/vpe_* fields (keep single-source to_dict/render)
└── (Phase 112 orchestrator) # calls the sampler before/after run_plan — mostly Phase 112, but this
                             #   phase must define the API so 112 can wire it (D-05: "112 needs the code to exist")
firestarter_app/tests/
├── test_hardware.py         # + sampler parse/median/timeout tests (synthetic 0xE4/0xE5 frames)
└── test_diagnostic_report.py# + split-field serialization tests
```

### Pattern 1: The additive sampler (do NOT disturb the print loop)
**What:** New public `sample_vpp_mv()` / `sample_vpe_mv()` beside the bool-returning
`read_vpp_voltage` / `read_vpe_voltage`, sharing the connect/handshake shape of
`_read_voltage_loop` but returning a median mV int instead of printing.
**When to use:** Always for this phase.
**Example (shape, Pattern A):**
```python
# Source: modeled on firestarter_app/firestarter/hardware.py:166-263 (do not modify that method)
import re
import statistics
from typing import Optional

_VOLTAGE_RE = re.compile(r"(\d+)\.(\d+)\s*V")  # tolerant: matches "VPP: 20.9V" / "VPE: 21.0V"

def _parse_voltage_frame(self, message: str) -> Optional[int]:
    """Parse the FIRST %u.%uV pair from a 0xE4/0xE5 DATA message -> mV (100 mV grid).
    Returns None if the string does not match (honest fallback, never a false 0)."""
    m = _VOLTAGE_RE.search(message or "")
    if not m:
        return None
    v_int, v_dec = int(m.group(1)), int(m.group(2))
    return v_int * 1000 + v_dec * 100   # RESEARCH: wire carries whole volts + tenths only

def _sample_one_voltage(self, state: int, n: int = 3, flags: int = 0) -> Optional[int]:
    """Energize the rail regulator, read N DATA frames, return the median mV.
    Self-contained: find_and_connect -> expect_ack(ready) -> send_ack -> N x get_response.
    Returns None on transport error/timeout/no-parse (D-04 NOT_MEASURED upstream)."""
    command = {"state": state}
    if flags:
        command["flags"] = flags
    comm = None
    samples: list[int] = []
    try:
        comm = SerialCommunicator.find_and_connect(command, self.config)
        is_ok, _ = comm.expect_ack()
        if not is_ok:
            return None
        for _ in range(n):
            comm.send_ack()                      # request one reading
            resp = comm.get_response()
            if resp.type != "DATA":
                break
            mv = self._parse_voltage_frame(resp.message)
            if mv is not None:
                samples.append(mv)
    except (ProgrammerNotFoundError, SerialError, SerialTimeoutError, HardwareOperationError):
        return None
    finally:
        if comm:
            comm.disconnect()
    return int(statistics.median(samples)) if samples else None

def sample_vpp_mv(self, n: int = 3) -> Optional[int]:
    return self._sample_one_voltage(COMMAND_READ_VPP, n=n)

def sample_vpe_mv(self, n: int = 3) -> Optional[int]:
    return self._sample_one_voltage(COMMAND_READ_VPE, n=n)
```
Note the handshake mirror: `hardware.py:188-201` does exactly
`find_and_connect → expect_ack → send_ack`, then loops on `get_response` acking each
DATA frame (`:204-219`). The sampler differs only in: (a) it stops after N frames instead
of looping forever, (b) it returns a value instead of printing, (c) it never touches the
`firestarter vpp`/`vpe` CLI path. **SC3 is satisfied structurally: `_read_voltage_loop`
and `read_vpp/vpe_voltage` are not edited.**

### Pattern 2: Split the report slot, keep single-source render (D-01)
**What:** Replace `vpp_vpe_mv: int | None` with separate fields; surface them through the
existing `to_dict()` so both `render()` and `to_json_block()` pick them up automatically.
**Example:**
```python
# Source: firestarter_app/firestarter/diagnostic_report.py:277-395 (extend, keep single-source)
@dataclass
class DiagnosticReport:
    ...
    # D-01: split the single slot; D-03 before/after on destructive; D-04 standalone
    vpp_before_mv: int | None = None
    vpp_after_mv: int | None = None
    vpe_before_mv: int | None = None
    vpe_after_mv: int | None = None
    vpp_mv: int | None = None            # standalone (non-destructive run, D-04)
    vpe_mv: int | None = None

def to_dict(self) -> dict[str, Any]:
    return {
        ...
        "voltage": {                     # substitute NOT_MEASURED for each None (D-04)
            "vpp_before_mv": NOT_MEASURED if self.vpp_before_mv is None else self.vpp_before_mv,
            "vpp_after_mv":  NOT_MEASURED if self.vpp_after_mv  is None else self.vpp_after_mv,
            "vpe_before_mv": NOT_MEASURED if self.vpe_before_mv is None else self.vpe_before_mv,
            "vpe_after_mv":  NOT_MEASURED if self.vpe_after_mv  is None else self.vpe_after_mv,
            "vpp_mv":        NOT_MEASURED if self.vpp_mv        is None else self.vpp_mv,
            "vpe_mv":        NOT_MEASURED if self.vpe_mv        is None else self.vpe_mv,
        },
        ...
    }
```
- `render()` (`:403-468`) currently does **not** render `vpp_vpe_mv` at all — add a
  `table.add_row("voltage", ...)` line so the split values are human-visible. Keep the
  render sourced from `d = self.to_dict()` (never a second field list).
- **The `NOT_MEASURED` substitution must live in `to_dict()`** — that is "the ONE place
  the sentinel string is substituted" per the module's own docstring
  (`diagnostic_report.py:319-330`, 383-384). Do not fabricate a `0` for an absent reading
  (Phase 108/110 honest-fallback pattern).

### Anti-Patterns to Avoid
- **Editing `_read_voltage_loop` to "share" code with the sampler.** It couples the
  monitor's print/loop behavior to the sampler and risks SC3. Prefer a *new* private
  helper; if you must share, share the tiny `_parse_voltage_frame`, never the loop.
- **Threading the sampler into `chip_test.run_plan`.** `run_plan`'s contract is
  operator-method dispatch (`chip_test.py:501-572`); it takes an `operator`
  (`EpromOperator`), not a `HardwareManager`. Injecting voltage sampling there widens its
  surface and would trip the Phase-109 orchestrator AST gate scope. Sample in the
  Phase-112 layer that *calls* `run_plan` (§Q4).
- **Reporting a false `0` mV** for a timeout/no-frame. Use `None` → `NOT_MEASURED`.
- **Claiming mV precision.** The wire is 100 mV-quantized; do not imply finer.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Serial connect + ready handshake | A new connect/ack sequence | `SerialCommunicator.find_and_connect` + `expect_ack` + `send_ack` (already used at `hardware.py:188-201`) | Race-free handshake already solved; re-deriving it re-introduces the race the comment at `:190-191` warns about |
| Median of N | Manual sort + index | `statistics.median` (stdlib) | Correct even/odd handling |
| Frame parse (Pattern B) | New byte-unpacking | `frame_parser._decode_param("u16", ...)` | The canonical u16 (`>H`) decoder; only relevant if Pattern B |
| Synthetic test frame | Hand-assembled bytes with wrong CRC | `tests/conftest.py:52 build_frame(0xE4, params)` | Builds `magic|len|id|params|crc|0x0A` with a correct CRC8 automatically |
| Report serialization | A second field list in `render()` | Extend `to_dict()` only | Single-source contract (Phase 110 D-01) |

**Key insight:** Every primitive this phase needs already exists in the codebase; the work
is *composition + one small parse function + report fields*, not new machinery.

## Runtime State Inventory

Not a rename/refactor/migration phase — greenfield-additive host code. Section omitted per
protocol. (No stored data, live-service config, OS-registered state, secrets, or build
artifacts carry a renamed identifier here.)

## Common Pitfalls

### Pitfall 1: Assuming the raw payload is on `Response` (the CONTEXT §D-05 trap)
**What goes wrong:** Planner tasks the sampler to call `_decode_param` on
`Response.payload` (as CONTEXT §D-05 suggests); `payload` is `None` for 0xE4/0xE5 →
`AttributeError`/`TypeError` or a silent `None`, and the sampler never returns a value.
**Why it happens:** `MSG_DATA_CHUNK` (0xE6) *does* carry raw bytes in `payload`, so the
pattern looks reusable — but voltage frames do not (`codec.py:269-282`).
**How to avoid:** Use Pattern A (parse `Response.message`) or Pattern B (extend plumbing).
Do not read `Response.payload` for a voltage frame.
**Warning signs:** A unit test that feeds a real `build_frame(0xE4, ...)` returns `None`
where a value was expected.

### Pitfall 2: Treating the wire value as millivolts
**What goes wrong:** Reading `v_int` as mV (getting 20 mV) or forgetting the tenths →
20 000× or 10× errors.
**Why it happens:** The function is *named* `..._mv` but the wire carries whole volts +
tenths.
**How to avoid:** Reconstruct `v_int*1000 + v_dec*100`. Pin it with a KAT test:
`build_frame(0xE4, struct.pack(">HHHH", 20, 9, 5, 0))` → `sample` returns `20900`.
**Warning signs:** Sampled value off by exactly 10× or 1000× from the printed monitor.

### Pitfall 3: Format-string coupling (Pattern A only)
**What goes wrong:** A future edit to the `messages.py:685/:694` format string
(`"VPP: %u.%uV, ..."`) silently breaks the regex; the sampler returns `None` and the
report reads `NOT_MEASURED` forever with no error.
**How to avoid:** Keep the regex tolerant (`r"(\d+)\.(\d+)\s*V"`, first match) and add a
regression test asserting the current 0xE4/0xE5 `format` in `CATALOG` still matches the
regex. Both `messages.py` and the firmware `messages.h` are codegen-generated — a format
change is possible but gated.
**Warning signs:** All voltage fields become `NOT_MEASURED` after an unrelated messages
regen.

### Pitfall 4: Sampling latency perturbing the sweep (timing)
**What goes wrong:** Each rail read costs `delay(100)` (stabilize) +
`delay(500)`-per-reading in firmware (`hardware_operations.cpp:37,57`) plus serial
round-trips. N=5 samples × 2 rails × before+after = up to 20 firmware reads ≈ **10+
seconds of pure `delay()`** added per destructive chip. This does NOT corrupt the value
(the reads are independent of the write pulse, D-03) but it slows the sweep.
**Why it happens:** The firmware read loop is designed for a human-watched monitor, not a
tight sampler.
**How to avoid:** Keep N at the low end (D-02 permits 3). The value is unaffected —
this is a UX/runtime note for the planner, not a correctness bug. Do NOT try to reduce
the firmware delay (that is a firmware change, out of scope).
**Warning signs:** `dev test` on a destructive chip feels multi-second-slow per rail read.

### Pitfall 5: Median of an EVEN N lands off the 100-mV grid
**What goes wrong:** `statistics.median([20900, 21000])` = `20950.0` (a float, off-grid),
then `int(...)` truncates to `20950`. Harmless but can surprise a "must be a multiple of
100" assertion.
**How to avoid:** Prefer odd N (3 or 5) so the median is one of the samples; if even N is
used, document that the median may be a 50-mV value. Cast to `int` for the report field
type (`int | None`).

### Pitfall 6: Orchestrator/SAFE-gate scope
**What goes wrong:** Wiring the sampler somewhere the Phase-109
`tools/check_devtest_orchestrator.py` AST gate flags (e.g. next to a VPP-set call, or
inside a raw-wire-dict builder).
**How to avoid:** The sampler sends `{"state": 11|12}` (a monitor command, not a
protocol/write command), sets no `vpp_mv`, passes no `--force`. Keep it in `hardware.py`
+ the Phase-112 orchestrator. Re-run the AST gate after wiring.

## Code Examples

### Building a synthetic voltage frame for tests (bench-free)
```python
# Source: firestarter_app/tests/conftest.py:52 (build_frame) + firestarter/messages.py:681-698
import struct
# VPP = 20.9 V, Internal VCC = 5.0 V  ->  4 x u16, big-endian
params = struct.pack(">HHHH", 20, 9, 5, 0)
frame = build_frame(0xE4, params)   # magic|len|id|params|crc|0x0A, correct CRC8
# Feed via the existing fixture:
fake_serial.feed(b"OK: ready\n")    # the expect_ack() handshake
fake_serial.feed(frame)             # first DATA frame
fake_serial.feed(frame)             # second (for N>=2 median)
fake_serial.feed(frame)             # third
# Then patch find_and_connect -> make_comm() and assert sample_vpp_mv() == 20900
```

### The existing handshake the sampler mirrors (read, don't edit)
```python
# Source: firestarter_app/firestarter/hardware.py:188-219 (read_vpp_voltage's loop — DO NOT MODIFY)
comm = SerialCommunicator.find_and_connect(command_for_connect, self.config)
is_ok, msg = comm.expect_ack()          # firmware "ready" signal (MSG_OK_READY)
if not is_ok: return False
comm.send_ack()                          # start the reading loop
while True:
    response = comm.get_response()
    if response.type == "DATA":
        print(f"\r{response.message}    ", end="", flush=True)   # <-- monitor prints; sampler parses instead
        comm.send_ack()                  # ack -> request next reading
    ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Voltage frames were text lines (`DATA: VPP: ..`) | ID-encoded binary frames (0xE4/0xE5, 4×u16) decoded by `codec.py` | v1.10/v1.11 (COBS + ID-frame era) | The sampler works on the decoded `Response`, not a raw text line |
| Raw params carried nowhere | `MSG_DATA_CHUNK` added `payload` to `LogMessage` (W-04) | Phase 8/W-04 | Precedent for Pattern B, but voltage frames were never given a `params` field |

**Deprecated/outdated:**
- CONTEXT §D-05's "parse the raw `param_bytes` via `_decode_param`" — **superseded by
  §Make-or-Break**: the raw params are not on `Response`. Use Pattern A/B.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Naming the return `..._mv` (100 mV-resolution reconstruction) is acceptable vs. exposing tenths (`_dV`) | §Make-or-Break, Pattern 1 | Low — arithmetic verified; only the *label* is a judgment call. If the report should show "20.9 V" verbatim, store the raw `(int,dec)` instead. Planner/UAT confirms. |
| A2 | The Phase-112 orchestrator (not `run_plan`) is the right place to invoke the sampler | §Q4 | Medium — if the milestone intends `run_plan` to own sampling, the sampler must be threaded in (a HardwareManager/callable param). CONTEXT §D-03's "independent energizations bracketing the write" supports the orchestrator placement. Confirm at plan time. |
| A3 | `flags=0` is correct for the read command | §User Constraints Discretion | Low — verified the firmware read path consults no flag (`hardware_operations.cpp:15-81`). |
| A4 | Pattern A (string re-parse) is preferred over Pattern B | §Make-or-Break | Low — both are correct; A has the smaller surface. If a later phase needs structured params broadly, B becomes attractive. |

## Open Questions

1. **run_plan vs orchestrator placement (couples with A2).**
   - What we know: `run_plan(plan, operator, db, *, runs)` (`chip_test.py:501`) dispatches
     to `EpromOperator` methods; it has no `HardwareManager` handle. Sampling is a
     self-contained serial op (D-03).
   - What's unclear: whether Phase 112 already plans an orchestrator wrapper that owns
     both `run_plan` and the sampler, or whether this phase should add a sampler param to
     `run_plan`.
   - Recommendation: Define the sampler API on `HardwareManager` this phase; leave the
     *call-site* to the Phase-112 orchestrator (D-05 says 112 "needs the code to exist,
     not to be bench-proven"). If the planner wants a wired end-to-end demo this phase,
     add a thin orchestrator function that takes both a `HardwareManager` and calls
     `run_plan`, and populates the report fields around it — without modifying `run_plan`.

2. **Field shape: flat vs nested (`voltage` sub-dict).**
   - What we know: D-01/D-03/D-04 require VPP/VPE × before/after + standalone. The report
     uses flat top-level keys today (`vpp_vpe_mv`).
   - Recommendation: A nested `"voltage": {...}` sub-dict (shown in Pattern 2) keeps
     `to_dict()` readable and groups the six fields; flat is also fine. Planner's call
     (CONTEXT grants this). Either way, keep the `NOT_MEASURED` substitution in `to_dict`.

## Environment Availability

Skipped for the software build itself (host-only Python, stdlib + existing deps — no new
external tool). The **deferred** SC2 bench gate (D-05) does have hardware dependencies,
listed here for the future UAT:

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Leonardo board + RURP Rev 2.0 shield | SC2 live "parsed mV == printed value" check | operator-run (deferred) | — | none — this is the single hardware gate, deferred to bench UAT per D-05 |
| Electrically-erasable chip (W27C512 / W29C020) | Before/after write-path bench check | operator-run (deferred) | — | any seated chip suffices for the *standalone* (non-destructive) read check |

**Missing dependencies with fallback:** the software MVP (sampler + wiring + synthetic-frame
unit tests) is fully buildable and testable with **no hardware** — that is the entire point
of D-05.

## Validation Architecture

nyquist_validation key is absent in `.planning/config.json` → treated as ENABLED.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (+ coverage gate `--cov-fail-under=70`, CI-enforced) |
| Config file | `firestarter_app/pyproject.toml` (pytest + ruff + mypy config); CI `.github/workflows/ci.yml` |
| Quick run command | `cd firestarter_app && python -m pytest tests/test_hardware.py -x -q` |
| Full suite command | `cd firestarter_app && python -m pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VOLT-01 | `_parse_voltage_frame("VPP: 20.9V, ...")` → 20900 mV | unit | `pytest tests/test_hardware.py -k parse_voltage -x` | ❌ Wave 0 (new tests) |
| VOLT-01 | `sample_vpp_mv()` returns median mV from N synthetic 0xE4 frames | unit | `pytest tests/test_hardware.py -k sample_vpp -x` | ❌ Wave 0 |
| VOLT-01 | `sample_vpe_mv()` uses state 12, parses 0xE5 | unit | `pytest tests/test_hardware.py -k sample_vpe -x` | ❌ Wave 0 |
| VOLT-01 | transport error / no DATA frame → returns `None` (not 0) | unit | `pytest tests/test_hardware.py -k sample_none -x` | ❌ Wave 0 |
| VOLT-01 | median of even N + off-grid handling (Pitfall 5) | unit | `pytest tests/test_hardware.py -k median -x` | ❌ Wave 0 |
| VOLT-01 | 0xE4/0xE5 `CATALOG` format still matches the parser regex (Pitfall 3 guard) | unit | `pytest tests/test_hardware.py -k format_pin -x` | ❌ Wave 0 |
| VOLT-01/SC3 | `read_vpp_voltage`/`read_vpe_voltage` unchanged (existing tests still green) | regression | `pytest tests/test_hardware.py -q` | ✅ (`tests/test_hardware.py:74-120`) |
| VOLT-01/D-01 | split report fields serialize; `None` → `NOT_MEASURED` in `to_dict()` | unit | `pytest tests/test_diagnostic_report.py -k voltage -x` | ❌ Wave 0 |
| SC2 | parsed mV == printed monitor value on real hardware | **manual (deferred)** | operator bench UAT, Leonardo + Rev 2.0 (D-05) | manual-only |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_hardware.py tests/test_diagnostic_report.py -x -q`
- **Per wave merge:** `python -m pytest -q` (full suite) + `ruff check` + `ruff format --check` + `mypy` (hardware.py is not in the strict-8 set today; if Pattern B touches `serial_comm.py`/`frame_parser.py`/`codec.py`, those ARE strict-mypy — budget for it)
- **Phase gate:** full suite green + coverage ≥ 70 before `/gsd-verify-work`; SC2 recorded as deferred HUMAN-UAT/FUT.

### Wave 0 Gaps
- [ ] `tests/test_hardware.py` — add sampler parse/median/timeout/format-pin tests using
      `build_frame(0xE4|0xE5, struct.pack(">HHHH", ...))` + `fake_serial.feed` +
      patched `find_and_connect` (harness already exists at `tests/test_hardware.py:44-120`
      and `tests/conftest.py:52`).
- [ ] `tests/test_diagnostic_report.py` — add split-field (VPP/VPE before/after/standalone)
      serialization + `NOT_MEASURED` fallback tests.
- [ ] No framework install needed — pytest + conftest fixtures (`build_frame`, `fake_serial`,
      `make_comm`) already present.

## Security Domain

security_enforcement key absent in `.planning/config.json` → treated as ENABLED.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface (local serial CLI) |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | **yes** | The sampler parses a wire frame from the device. Treat it as untrusted input: tolerant regex, bounded N loop, `None` on any parse failure (never crash the sweep). Malformed/truncated frames are already CRC-guarded in `codec.py` and surface as a dropped/`None` reading — do not `assert` on device-supplied values. |
| V6 Cryptography | no (CRC8 is integrity, not crypto) | Frame integrity handled upstream by `_crc8_ccitt` (`frame_parser.py:52`); the sampler does not touch it |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malicious/garbled device frame yields a bogus voltage | Tampering | Tolerant parse + range-agnostic honesty: return the parsed value or `None`; never fabricate `0`; the report's job is to show the reading, not to trust it. A wildly wrong reading is itself diagnostic signal. |
| Format-string / catalog drift silently disables the sampler | Denial-of-info | Pitfall 3 regression test pins the 0xE4/0xE5 format against the regex |
| Sampler opens a serial connection unexpectedly (SAFE-02 orchestrator-only) | Elevation-of-behavior | Sampler stays in `hardware.py`; report model imports no transport class (`diagnostic_report.py:18-24`); re-run `tools/check_devtest_orchestrator.py` |
| Unbounded read loop hangs the sweep | DoS | Bounded `for _ in range(n)` loop + `get_response` timeout (`SerialTimeoutError`) → `None` |

## Sources

### Primary (HIGH confidence — read this session, cited by file:line)
- `firestarter_app/firestarter/hardware.py:166-263` — `_read_voltage_loop`, `read_vpp/vpe_voltage`
- `firestarter_app/firestarter/frame_parser.py:17-19, 133-184` — `Response`, `_decode_param`
- `firestarter_app/firestarter/codec.py:57-130, 236-282` — `format_message`, decode path, payload only for chunk
- `firestarter_app/firestarter/serial_comm.py:360-432` — frame read → `Response` build (`payload=decoded.payload`), `get_response`
- `firestarter_app/firestarter/messages.py:113-117, 681-698` — 0xE4/0xE5 defs (4×u16, `param_bytes=8`, format)
- `firestarter_app/firestarter/constants.py:66-67` — `COMMAND_READ_VPP=11`, `COMMAND_READ_VPE=12`
- `firestarter_app/firestarter/diagnostic_report.py:42-43, 283-468` — report model, `NOT_MEASURED`, `vpp_vpe_mv` slot, `to_dict`/`render`
- `firestarter_app/firestarter/chip_test.py:501-572, 783-872` — `run_plan`, `_dispatch_multi_run`, `_DESTRUCTIVE_OPS`
- `firestarter_app/firestarter/cli_handlers.py:1474-1593` — `dev_validate_family` compose/mock seam
- `firestarter_app/firestarter/eprom_operations.py:257-296` — `EpromOperator.__init__` (config-manager-based)
- `firestarter_app/tests/test_hardware.py:1-120` — voltage-read test harness pattern
- `firestarter_app/tests/conftest.py:52-124` — `build_frame`, `_FakeSerial`, `fake_serial`, `make_comm`
- `firestarter/src/hardware_operations.cpp:15-81` — `hw_read_voltage` emit (whole+tenths, not mV; delays)
- `firestarter/include/logging_id.h:194-205` — `LOG_DATA_ID_U16x4` (big-endian pack)
- `.planning/REQUIREMENTS.md:42, 89` — VOLT-01, "only near-firmware touch is parsing an existing frame"
- `firestarter_app/CLAUDE.md`, `firestarter/CLAUDE.md` — constants-sync rule, dispatch invariants, mypy gate

### Secondary (MEDIUM confidence)
- Memory `reference_vpp_vpe_no_socket_routing`, `project_phase79_gate_reexamined` (cited in CONTEXT for D-04/D-01 safety grounding)

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new deps; all reuse targets read and cited by line.
- Architecture: HIGH — the make-or-break (payload not on `Response`; wire is whole+tenths)
  is verified against the live decode path and firmware emit; both patterns are concrete.
- Pitfalls: HIGH — each pitfall is tied to a specific verified source line.
- Wiring placement (run_plan vs orchestrator): MEDIUM — depends on Phase-112 intent
  (Open Question 1 / Assumption A2).

**Research date:** 2026-07-02
**Valid until:** 2026-08-01 (stable host code; only risk is a codegen regen changing the
0xE4/0xE5 format string — guarded by the Pitfall 3 test)
