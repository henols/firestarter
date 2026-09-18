# Phase 199: What the rails can actually deliver — Research

**Researched:** 2026-09-18
**Domain:** RURP shield high-voltage rail measurement (bench), host-side voltage-shortfall policy, database override + regeneration evidence
**Confidence:** HIGH for everything measured this session against the live repos; the one number this phase needs that does **not** exist yet is the measured drop-path maximum, and that is deliberate (D-07/D-08).

**Shas this research was measured against:** meta `27a33619`, `firestarter_app` `f155364`, `firestarter_fw` `11024ee`, all three on `v1.40-program-parameter-fidelity` [VERIFIED: `git rev-parse --short HEAD` in each repo, this session].

Every claim below is tagged **MEASURED** (I ran the command or read the file this session and the output is reproduced) or **INFERRED** (derived from measured facts but not itself observed).

---

## What this phase actually is

CONTEXT.md states the shape and this research does not enlarge it:

> **a bench session, one JSON field, one new host module, one markdown section, one test, one held draft.**

Concretely, the six deliverables:

| # | Deliverable | Repo / path | Requirement |
|---|---|---|---|
| 1 | **A bench session** on the Rev 2.0 shield: DMM at socket pin 1 on two rail configurations, plus exactly one paired ADC read | evidence file in `.planning/phases/199-.../` | RAIL-01 |
| 2 | **One JSON field**: `electrical.vpp_mv` `18000 → 21000` added to the existing `FUJITSU/MBM27128` entry | `firestarter_app/tools/datasheet_overrides.json` | RAIL-02 |
| 3 | **One new host module**: the shortfall policy, `jp5_gate.py` shape, warns and returns a flag, never refuses | `firestarter_app/firestarter/<name>_gate.py` | RAIL-03, RAIL-04 |
| 4 | **One markdown section**: `## 10.` in `tools/DECODE-NOTES.md` — the theoretical-ceiling status, the measured figures, the ADC error, the 30-row classification table, the named limits | `firestarter_app/tools/DECODE-NOTES.md` | RAIL-01, RAIL-02, RAIL-04 |
| 5 | **One test** that reddens when the 30-row classification stops being true | `firestarter_app/tests/` | RAIL-02 |
| 6 | **One held draft** answering gh#71, joined to the consolidated held-pending list | `.planning/phases/199-.../199-GH71-ANSWER.md` | RAIL-05 |

Plus the unavoidable regeneration consequences of #2, all of which are **measured below, not assumed**: a 1-record wire-delta layer, a 1-line characterization snapshot re-record, and a one-row regeneration diff artifact.

---

## A. The bench session (RAIL-01, D-04…D-08)

### A1. `hold_rail.py` — what it is and how it is invoked

**MEASURED** — read in full at `.planning/milestones/v1.18-artifacts/bench/hold_rail.py` (67 lines).

**What it does.** It reproduces `EpromOperator.dev_set_registers(..., firestarter=True)`'s wire payload by hand, then **holds the serial port open** for a fixed window so the board never resets and the 74HC573 control latch keeps its value. It deliberately never calls `expect_ack()` — the firmware busy-waits on the user button for `dev reg`, so the host's ack times out and the `finally: _disconnect_programmer()` closes the port, which de-asserts DTR, resets the MCU and zeroes the latch before an operator can read the meter. That is the exact failure D-05 warns about.

**Arguments** (both positional, both optional):

```
python3 hold_rail.py [CTRL_HEX] [HOLD_SECONDS]
```

- `CTRL_HEX` — control-register composite in the **host `-f` (firestarter) namespace**, parsed with `int(sys.argv[1], 16)`. **Default `0x188`.**
- `HOLD_SECONDS` — integer, **default `120`**.

**The composite it holds by default**, from its own docstring, verbatim:

> `CTRL defaults to 0x188 (REGULATOR 0x080 + VPE-drop 0x100 + P1-route 0x008, host -f namespace → physical CTRL 0x89 on Rev 2.0).`

**Wire payload**, verbatim from the script:

```python
payload = bytes([0x00, 0x00, 0x80 | ((CTRL >> 8) & 0x01), CTRL & 0xFF])
```

**MEASURED** — this is byte-identical to `EpromOperator.dev_set_registers`'s own packing at `firestarter_app/firestarter/eprom_operations.py` (the `self.comm.send_bytes(bytes([msb, lsb, (0x80 if firestarter else 0x00) | (ctrl_reg >> 8 & 0x01), ctrl_reg & 0xFF]))` call). The script is a faithful mirror, not an approximation.

**Does it stand alone?** Almost. **MEASURED** dependencies:

- It imports `firestarter.serial_comm.SerialCommunicator`, `firestarter.config.ConfigManager`, `firestarter.constants.COMMAND_DEV_REGISTERS` — so **the `firestarter` package must be importable** by whatever interpreter runs it.
- Its shebang is `#!/usr/local/bin/python3.12`, a devcontainer-specific absolute path. **Invoke it as `python3 hold_rail.py …`, never as `./hold_rail.py`** — the shebang is stale relative to the `.venv/ci-replica` (3.11) the rest of this phase uses, and running it under the wrong interpreter is an import failure, not a silent wrong result.
- **Cleanup is automatic and safe**: the `finally:` block calls `comm.disconnect()`, the board resets, and the latch clears to `0x00`. No rail is left energized on Ctrl-C or on kill.
- It prints a banner naming the expected pins to measure, then sleeps. It presses no button and needs none.

**Discretion point (CONTEXT.md allows either):** copy it into this phase's bench directory, or invoke it in place from `.planning/milestones/v1.18-artifacts/bench/`. **Recommendation: invoke in place, and record the invocation verbatim in the bench record.** Copying creates a second file that can drift, and CLAUDE.md's memory already flags "skills must own their scripts" as a rule about *skills*, not about one-shot bench evidence. If it is copied, the copy must be byte-identical and the record must say so.

### A2. The nine standing bench rules

**MEASURED** — read from `.planning/milestones/v1.34-artifacts/PROCEDURE.md` § "Standing bench rules". Reported near-verbatim, with the Claude-vs-operator split flagged.

| # | Rule (near-verbatim) | Binds |
|---|---|---|
| 1 | **Port identity is re-verified for every cell, never inherited.** `/dev/ttyACM*` **and** `/dev/ttyUSB*` numbering shuffles across replug, so the port used by a previous cell or session is never assumed for this one. | **Claude** — must re-probe the port before each bench step. |
| 2 | **Chip-out-before-sideload is Uno-class only.** On `uno`/`uno328pb` the chip is out of its socket before any avrdude invocation touching the bootloader (flash **and** read-back). The **Leonardo is exempt**. | Operator (chip handling); Claude must not trigger a sideload with a chip seated on Uno-class. *Not directly engaged this phase — D-05 has the chip OUT throughout anyway.* |
| 3 | **Photography, multimeter readings, chip handling and pot adjustment are operator-only.** Claude drives serial and CLI only — `fw`, `hw`, `read`, `write`, `vpp`, `dev consistency-check` and the phase's own tools. **Claude never touches the physical rig.** | **Hard split.** Every DMM number in this phase comes from the operator; Claude may not assert one. |
| 4 | **The operator adjusts the pot himself.** Claude states the target, the operator sets it and reports back, and Claude takes **exactly one** confirming read — **never a live monitor loop.** | **Hard split**, and see A4: `firestarter vpp` *is* a monitor loop by default. |
| 5 | **The VPP and VPE monitors do not route to the socket.** A blank or nonsense reading on either means a contact fault, not a rail fault. | **Claude** — and this is the reason the paired read of D-05 measures a *different node* from the DMM. See A5. |
| 6 | **Board identity is by silkscreen and avrdude signature, never by a firmware-reported revision field.** `hw_revision` cannot distinguish Rev 2.0 / Rev 2.2 / Modified Rev 0 (same resistor band), so the operator's silkscreen read is authoritative. | **Hard split.** D-04's "Rev 2.0 only" must be established by an operator silkscreen statement, recorded in the bench record. |
| 7 | **This procedure must not run under `--auto` / `--chain` / any auto-advance mode.** Those modes auto-approve the `human-verify` checkpoints every physical step depends on; **`autonomous: false` on a plan is not self-protecting against that.** | **Orchestration.** The bench plan must carry `autonomous: false` *and* the phase must not be run through `/gsd-execute-phase --auto`. |
| 8 | **A single clean re-seat is allowed per position.** If a failure is attributable to a named physical cause, one re-seat and one re-run are permitted — and **both the discarded attempt and the re-run are recorded**, never just the re-run. | Operator + record. |
| 9 | **`FIRESTARTER_CONFIG_DIR` is set inline on every command that invokes an arm binary** or a tool that shells out to one — never by a session-level `export`. `config.py` computes `HOME_PATH`, `DATABASE_FILE` and `PIN_MAP_FILE` as **import-time** constants from `get_config_dir()`, so a mid-session export fixes only call-time consumers and silently leaves the database and pin-map on `~/.firestarter`. | **Claude.** Engaged this phase only if an arm binary is used; `hold_rail.py` and `firestarter vpp` do not shell out to one, but a config-dir isolation is still cheap insurance. |

**The load-bearing ones for Phase 199, per CONTEXT.md's own reading:** 3, 4, 5, 6, 7.

### A3. The two control-register composites for D-06

**MEASURED** — derived from four files read this session.

**The bits** (`firestarter_fw/include/rurp_pinout.h`, the `#else` / `HARDWARE_REVISION` arm — the one the host mirrors), verbatim:

```c
#define CTRL_ADDRESS_LINE_16          0x01
#define CTRL_VPP_A9_ENABLE            0x02
#define CTRL_VPE_ENABLE               0x04
#define CTRL_VPP_P1_ENABLE            0x08
#define CTRL_ADDRESS_LINE_17          0x10
#define CTRL_ADDRESS_LINE_18          0x20
#define CTRL_READ_WRITE               0x40
#define CTRL_VPP_REGULATOR_ENABLE     0x80
#define CTRL_VPP_VPE_DROP_ENABLE      0x100
```

**The same values are mirrored host-side**, verbatim from `firestarter_app/firestarter/constants.py`:

```python
CTRL_VPP_VPE_DROP_ENABLE = 0x100  # was VPE_TO_VPP (wide layout)
CTRL_VPP_REGULATOR_ENABLE = 0x080  # was REGULATOR
CTRL_VPP_P1_ENABLE = 0x008  # was P1_VPP_ENABLE
```

**What each bit means for this phase:**

- `CTRL_VPP_REGULATOR_ENABLE` (`0x080`) — **turns the boost regulator on.** Nothing reaches any socket pin without it. It is the *source*.
- `CTRL_VPP_VPE_DROP_ENABLE` (`0x100`) — **selects a LEVEL, not a route.** `firestarter_fw/src/proms/memory.cpp`'s own comment says so: *"CTRL_VPP_VPE_DROP_ENABLE selects a VPP LEVEL -- VPE dropped through the [resistor]"*. With the bit set, the rail is passed through the drop resistor (VPP ≈ 13 V nominal / ~17.8 V at pot max on gh#71's board); clear, the undropped VPE rail is used (~22.7 V at the same pot setting).
- `CTRL_VPP_P1_ENABLE` (`0x008`) — **routes the selected rail to socket pin 1** (28-pin VPP destination).
- `CTRL_VPE_ENABLE` (`0x004`) — routes to the **non-P1** destination (pin 21 for 24-pin parts). D-06 declines this configuration.

**Why the substitution matters.** `eprom_internal_set_control_register` (`firestarter_fw/src/proms/eprom.cpp`) is the only writer on the write path, and it swaps the bits:

```c
void eprom_internal_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle)) {
        bit &= ~CTRL_VPE_ENABLE;
        bit |= CTRL_VPP_P1_ENABLE;
    }
    ep_set_control_register(handle, bit, state);
}
```

and `using_p1_as_vpp` (`firestarter_fw/include/memory_utils.h`), verbatim:

```c
static inline bool using_p1_as_vpp(const firestarter_handle_t* handle) {
    return (handle->pins == 32 && handle->bus_config.vpp_line == VPP_P1_32_DIP) ||
           (handle->pins == 28 && handle->bus_config.vpp_line == VPP_P1_28_DIP) ||
           (handle->pins == 24 && handle->bus_config.vpp_line == VPP_P21_24_DIP);
}
```

`VPP_P1_28_DIP` is `0x0F` = **15** (`firestarter_fw/include/rurp_shield.h`). **MEASURED:** `MBM27128`'s live wire dict carries `"bus-config": {"vpp-pin": 15, …}` and `"pin-count": 28`, so `using_p1_as_vpp` is **true** for it — the pulse goes to **socket pin 1**, exactly what D-06 measures. `hold_rail.py` therefore reproduces the real write-path destination, not an approximation of it.

**The two composites, host `-f` namespace:**

| D-06 configuration | Composite | Bits | `hold_rail.py` invocation |
|---|---|---|---|
| **(a) drop-resistor → socket pin 1** — *this is the threshold figure* | **`0x188`** | `0x080` REGULATOR + `0x100` VPE-DROP + `0x008` P1 | `python3 hold_rail.py 0x188 180` (this is also the script's default) |
| **(b) direct VPE → socket pin 1** — what VPE-as-VPP delivers to the 10 stranded 28-pin rows | **`0x088`** | `0x080` REGULATOR + `0x008` P1, **drop bit clear** | `python3 hold_rail.py 0x088 180` |

**Why this routes to pin 1, stated plainly:** `0x080` turns the regulator on; `0x100` (present in (a), absent in (b)) chooses whether the resistor drops it; `0x008` closes the path from the selected rail to socket pin 1. No other bit in either composite touches a route.

**Payload check (INFERRED from the measured packing, arithmetic only):** `0x188` → `[0x00, 0x00, 0x81, 0x88]`; `0x088` → `[0x00, 0x00, 0x80, 0x88]`. The 9th bit rides in byte 2's LSB; the `0x80` in byte 2 is the `firestarter=True` namespace marker.

**Guard to be aware of:** `dev_set_registers` rejects `ctrl_reg > 0x1FF` when `firestarter=True` and `> 0xFF` when not. `hold_rail.py` always sets the `0x80` namespace marker, so `0x188` passes. A plan that instead used `firestarter dev reg 0 0 0x188` **without `-f`** would be refused by the host before the wire.

**Cross-check against the firmware's own route resolver.** `eprom_hv_route_mask()` (`firestarter_fw/src/proms/eprom.cpp`) returns only the *level* bits, never the route bit:

```c
rurp_register_t eprom_hv_route_mask(firestarter_handle_t* handle) {
    if (is_flag_set(FLAG_VPE_AS_VPP)) {
        return CTRL_VPP_REGULATOR_ENABLE;
    }
    const eprom_params_t* row = eprom_params_for(handle->protocol);
    if (row == NULL) {
        return EPROM_HV_ROUTE_MASK;
    }
    if (pgm_read_byte(&row->vpp_path) == VPP_PATH_DIRECT_VPE) {
        return CTRL_VPP_REGULATOR_ENABLE;
    }
    return EPROM_HV_ROUTE_MASK;
}
```

with `#define EPROM_HV_ROUTE_MASK (CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE)` = `0x180`. So on a real write of `MBM27128`: `0x180` is asserted once per block (configuration (a) minus P1), then P1 (`0x008`, substituted for `CTRL_VPE_ENABLE`) is asserted per pulse → **`0x188` total**, which is exactly configuration (a). **With `FLAG_VPE_AS_VPP` set, the mask becomes `0x080`, and with P1 that is `0x088` — configuration (b).** The two composites are not a bench abstraction; they are the two states the write path actually produces.

### A4. The paired ADC read — exact command line

**MEASURED** — `firestarter_app/firestarter/cli_handlers.py`:

```python
@cli.command(name="vpp")
@click.option("-t", "--timeout", type=int, default=None, hidden=True)
def vpp(app: AppContext, timeout: int | None) -> None:
    """VPP voltage."""
```

and the identical `vpe` command immediately below it. So the two subcommands are exactly:

```bash
firestarter vpp
firestarter vpe
```

**What they print.** `HardwareManager._read_voltage_loop` (`firestarter/hardware.py`) prints each DATA frame with `print(f"\r{message}    ", end="", flush=True)` — carriage-return overwrite, i.e. a **live monitor**. The frame text is firmware-formatted, e.g. `VPP: 20.9V, Internal VCC: 5.0V` (the shape `_parse_voltage_frame`'s regex expects). The wire carries **whole volts plus one tenths digit only**, so every figure sits on a **100 mV grid and is never finer** — that alone is a resolution limit § 10 must name, independent of the ADC's accuracy.

**⚠️ Rule-4 hazard, MEASURED:** `_read_voltage_loop` is `while True:` and returns only on an `OK`/`ERROR` response, on `KeyboardInterrupt`, or when `timeout_seconds` is set *and* elapsed. With no `-t`, it is an **unbounded live monitor loop — which standing bench rule 4 forbids.**

**Therefore the bench plan must use the hidden `-t` option:**

```bash
firestarter vpp -t 1
firestarter vpe -t 1
```

`-t 1` still emits several frames inside that second (the timeout is checked *after* each DATA frame), so the honest description in the bench record is **"one bounded sampling window, last frame recorded"**, not "one read". If a literally-single sample is wanted, the value-returning sibling `HardwareManager._sample_one_voltage(state, n=3)` takes a **median of 3** — but it is **not exposed on the CLI** and would need a throwaway script. **Recommendation: `-t 1`, record the settled value, and state the sampling in § 10.**

**What the ADC read physically measures** — `hw_read_voltage` (`firestarter_fw/src/hardware_operations.cpp`), verbatim:

```c
if (handle->cmd == CMD_READ_VPP) {
    rurp_write_to_register(CONTROL_REGISTER, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE);
} else if (handle->cmd == CMD_READ_VPE) {
    rurp_write_to_register(CONTROL_REGISTER, CTRL_VPP_REGULATOR_ENABLE);
}
```

**`CMD_READ_VPP` = `0x180` (= composite (a) without P1). `CMD_READ_VPE` = `0x080` (= composite (b) without P1). Neither asserts any socket-routing bit.** That is standing bench rule 5 in code, and it is the single most important honesty limit of the whole session — see A5.

**Rev 0 refusal, MEASURED:** the same function returns `MSG_ERR_REV0_VPP_RD` before either branch when `rurp_get_hardware_revision() == REVISION_0`. This is D-04's stated reason Modified Rev 0 could contribute no ADC figure.

### A5. The ordering hazard (D-05) — mechanism and required step order

**The mechanism, MEASURED.** `SerialCommunicator._connect` (`firestarter/serial_comm.py`) opens the port with:

```python
self.connection = serial.Serial(
    port=self.port_name,
    baudrate=self.baud_rate,
    timeout=self.timeout,
)
```

No `exclusive=`, no `dsrdtr=`, no `dtr=False`. Consequences, both load-bearing:

1. **pyserial asserts DTR on open and de-asserts it on close.** On the ATmega32u4 / ATmega16U2 the DTR transition resets the MCU, the 74HC573 control latch zeroes, and **any held rail collapses to 0 V**. This is the documented root cause in `hold_rail.py`'s own docstring and the reason `firestarter dev reg 0 0 <CTRL> -f` does not work: it sets the rail correctly, then its own `finally: _disconnect_programmer()` destroys it.
2. **No `exclusive=True` means a second process is not blocked from opening the same tty.** This is *worse* than being blocked: on Linux, `firestarter vpp` launched while `hold_rail.py` holds the port will (a) reset the board, killing the held rail mid-DMM-read, and (b) interleave two framing state machines on one tty, producing garbage rather than a clean failure.

**Therefore no `firestarter` command may run inside a hold window — this is not a preference, it is a correctness requirement.**

**The required step ordering.** The two nodes are also different (A4), so the DMM step and the ADC step are inherently sequential, not concurrent:

```
0.  Operator confirms shield identity by SILKSCREEN (rule 6) → "Rev 2.0". Recorded.
0b. Operator confirms chip is OUT of the socket. Recorded.
0c. Claude verifies the port identity for this session (rule 1). Recorded.

1.  Claude states the pot target: MAXIMUM. Operator sets the pot (rule 4). Operator confirms.
    >>> POT IS NOT TOUCHED AGAIN FOR THE REST OF THE SESSION. <<<
    Every figure below must be at ONE pot setting or the pairing in step 5 is meaningless.

2.  HOLD WINDOW A — configuration (a), drop path:
      python3 .planning/milestones/v1.18-artifacts/bench/hold_rail.py 0x188 180
    Claude starts it, prints the banner, and RUNS NOTHING ELSE.
    Operator reads the DMM at socket pin 1. Operator reports the number.
    Window closes (script exits or Ctrl-C). Rail clears.

3.  HOLD WINDOW B — configuration (b), direct VPE path:
      python3 .planning/milestones/v1.18-artifacts/bench/hold_rail.py 0x088 180
    Same discipline. Operator reads DMM at socket pin 1. Reports. Window closes.

4.  >>> BOTH HOLD WINDOWS ARE CLOSED. No hold_rail.py process is running. <<<
    (Verify: no python process holding the tty.)

5.  Claude takes the paired ADC reads, one bounded window each:
      firestarter vpp -t 1     ->  the ADC's view of the DROP rail (CTRL 0x180)
      firestarter vpe -t 1     ->  the ADC's view of the DIRECT rail (CTRL 0x080)

6.  The error figures:
      error_drop   = (firestarter vpp reading)  vs  (step 2 DMM reading)
      error_direct = (firestarter vpe reading)  vs  (step 3 DMM reading)
```

**The honesty limit this ordering creates, and § 10 must state it.** Step 5 reads with **no socket-routing bit asserted** (A4), while steps 2 and 3 read **at socket pin 1 through `CTRL_VPP_P1_ENABLE`**. The two figures therefore differ by *(ADC error) + (whatever the P1 switch path drops)*, and this session **cannot separate the two terms**. The pair is an honest bound on the combined discrepancy; it is **not** a pure ADC calibration, and it must not be written up as one. 999.38's ~+7.5 % (6.8–8.3 %) ratiometric figure remains the only ADC-only number, and it stays a citation, not a replacement.

**Which figure becomes the threshold.** D-06 is explicit: **configuration (a)'s DMM reading at socket pin 1 IS the threshold figure.** It is a meter reading at the real destination, so it is the number RAIL-01 asks for and the number the host module compares against. The ADC pair exists to give RAIL-01's "known error", not to produce the threshold.

**One further operational note, deferred in CONTEXT.md but worth surfacing to the bench plan:** the pot is left at maximum at the end of this session. Phase 201 is also bench-gated. Either restore the pot to a working setting as a final recorded step, or record explicitly that it was left at maximum so Phase 201 does not inherit a surprise.

### A6. Bench-artifact directory convention

**MEASURED.**

- `.planning/phases/` currently holds 28 directories, including `197-…`, `198-…` and `199-what-the-rails-can-actually-deliver` — **active-milestone phase evidence lives in the phase directory.** Phases 197 and 198 wrote `197-PULSE-INVENTORY.md`, `197-REGEN-DIFF.md`, `198-REGEN-DIFF.md`, `198-VOLT03-DISPOSITION.md` there.
- `.planning/milestones/` holds `v1.15-artifacts/bench`, `v1.16-artifacts/ledger/bench`, `v1.18-artifacts/bench`, `v1.34-artifacts/bench` — **these are post-close locations**, populated when a milestone is hand-archived. `.planning/archive/` does not exist.

**The convention, stated:** write this phase's bench evidence to the **phase directory** as `.planning/phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md` (name at the planner's discretion, matching the `199-<TOPIC>.md` pattern of 197/198). The v1.40 close will move it under `.planning/milestones/v1.40-artifacts/bench/` by hand, like every prior milestone. **Do not create `.planning/milestones/v1.40-artifacts/` during the phase** — that directory is the close's to make.

---

## B. The database change (RAIL-02, D-17)

### B7. The existing `FUJITSU/MBM27128` entry, verbatim

**MEASURED** — `firestarter_app/tools/datasheet_overrides.json`, lines 51–58:

```json
  "FUJITSU/MBM27128": {
    "datasheet": "datasheets/MBM27128.pdf",
    "note": "Figure 3, the Quick Pro flow chart on page 4-20, specifies TPW = 1 ms +/- 50 us with VCC = 6V +/- 0.25V, VPP = 21V +/- 0.5V and an X = 20 pulse ceiling. Page 4-19's conventional procedure specifies a 50 ms pulse and is the wrong reading here: the firmware consumes this field as the initial pulse width of a verify-per-pulse loop capped at 25 pulses with overprogram_factor = 0 on protocols 0x07 and 0x08, which is the fast Quick Pro algorithm's shape and not the conventional single-shot one. Note also that the corrected value still yields an incomplete Quick Pro, because the firmware never emits the datasheet's tOPW over-program pulse. This entry's electrical.vdd_mv field also comes from that same Figure 3 table's VCC = 6V +/- 0.25V figure.",
    "fields": {
      "programming.pulse_duration_us": { "was": 200, "is": 1000 },
      "electrical.vdd_mv": { "was": 5500, "is": 6000 }
    }
  },
```

**The existing `note` already states the VPP figure**: *"VPP = 21V +/- 0.5V"*. The datasheet citation is already correct and already git-tracked. D-17 adds a field to an entry that exists, and the note needs at most a sentence extension naming that the `electrical.vpp_mv` field now also comes from that same Figure 3 table.

### B8. Exactly what must be added

**MEASURED** against `_validate_datasheet_overrides_shape` and `apply_datasheet_override` in `firestarter_app/tools/build_db.py`. The addition is one line inside the existing `fields` map:

```json
      "electrical.vpp_mv": { "was": 18000, "is": 21000 }
```

**Schema facts, all MEASURED:**

- **Field-path allowlist.** `_OVERRIDABLE_DECODED_FIELDS` is a tuple, verbatim:
  ```python
  _OVERRIDABLE_DECODED_FIELDS = (
      "electrical.size_bytes",
      "electrical.pin_count",
      "electrical.vpp_mv",
      "electrical.vcc_mv",
      "electrical.vdd_mv",
      "programming.pulse_duration_us",
  )
  ```
  **`electrical.vpp_mv` is already in it.** No allowlist edit is needed — and two sibling entries (`FUJITSU/MBM27C1001`, `FUJITSU/MBM27C4001`) already use this exact field path, so there is a working precedent in the same file.
- **`was`/`is` shape is mandatory**: `set(pair) != {"was", "is"}` raises. No third key, no bare value.
- **Top-level keys must be in strict ascending order.** **MEASURED:** `list(d) == sorted(d)` is `True` today across all 22 keys. Adding a field to an existing key does not disturb this.
- **`fields` maps are NOT required to be sorted** — `MBM27C1001` carries `pulse_duration_us`, `vpp_mv`, `vdd_mv` in that non-alphabetical order and the validator does not look. **Follow the sibling entries' order — `programming.*` first, then `electrical.vpp_mv`, then `electrical.vdd_mv`** — for readability, not for the validator.
- **Entry count and UNSOURCED count do NOT move.** **MEASURED:** the file has **22** entries, **18** `UNSOURCED`. `tests/test_datasheet_overrides.py` carries `_EXPECTED_ENTRY_COUNT = 22` and `_EXPECTED_UNSOURCED_COUNT = 18`. Because D-17 adds a *field* to an *existing* entry, **neither literal moves.** This is a real difference from Plan 198-01, which had to bump them.

**Every fail-closed check this new field can trip** — all five, MEASURED from `apply_datasheet_override`, with the exact refusal text each produces:

| Failure mode | Raises |
|---|---|
| Field path not in the allowlist (typo, e.g. `electrical.vpp`) | `…override names field path 'electrical.vpp', which is not one of the overridable decoded fields […] — refusing to apply an unknown field path` |
| A second entry also targets `electrical.vpp_mv` on the same row | `…both target 'electrical.vpp_mv' on the same row — refusing to apply two overrides to one field` |
| `was` is not the same Python type as the live decode (e.g. `"18000"` as a string) | `…recorded prior '18000' (str) does not match the live decode's type int (18000) — refusing to coerce` |
| `is` is not the same type | `…override value '21000' (str) does not match the live decode's type int (18000) — refusing to coerce` |
| **`was` does not match the live decode** (e.g. writing `was: 12000`) | `…recorded prior 12000 for 'electrical.vpp_mv' does not match the live decode 18000 — refusing to apply a stale override` |
| `was == is` | `…override value 21000 equals the recorded prior 18000 — refusing a no-op override` |

**MEASURED: the live decode for `MBM27128`'s `electrical.vpp_mv` is `18000`.** So `"was": 18000` is the only value that passes. The gh#71 maintainer comment explains where the 18000 comes from: `voltages="0x40f0"` → VPP low byte `0xF0` → `VPP_MV[0xF0] = 18000`, upstream's own ceiling.

### B9. Regeneration — invocation, output, row count

**MEASURED.** The invocation, exactly as Plan 198-01 used it:

```bash
cd /workspaces/firestarter_app && python tools/build_db.py
```

**Its success line** is built at `tools/build_db.py`:

```python
f"= {total_chips + supplement_count} total. Saved to {OUTPUT_FILE}"
```

so the last stdout line ends `= 746 total. Saved to …/chip_database.json`. Plan 198-01's proven assertion idiom is:

```bash
python tools/build_db.py 2>&1 | tail -1 | /usr/bin/grep -q '= 746 total\.'
```

**Row count stays 746.** **INFERRED but tightly:** an override substitutes a decoded value before `classify()`'s downstream derivations; it adds and removes no rows. The count assertion above is the check that proves it rather than assuming it.

**Network dependency — flag this to the planner.** **MEASURED:** `build_db.py` fetches `MINIPRO_XML_URL` over the network with `requests.get(..., timeout=30)` and `sys.exit(1)` on any exception. The URL is SHA-pinned:

```python
MINIPRO_XML_URL = (
    "https://gitlab.com/DavidGriffith/minipro/-/raw/"
    "a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml"
)
```

**MEASURED this session:** `requests.head(...)` returned **`status 200`, `content-length 17861009`** — reachable now, ~17 MB. There is **no offline cache path**. A bench-day network outage blocks the regeneration task. This is not new to this phase, but a plan should not assume it silently.

**Byte-stability.** The `is` value is substituted into `_decoded_view` before `classify()` runs, and `21000 < RURP_VPP_CEILING_MV (25000)` under the **strict** `>` compare, so **no `support_status` moves** — D-01 holds with D-17 applied. The regeneration should therefore produce exactly one changed row and exactly one changed field.

### B10. The wire-delta layer — **a 199 layer IS needed. Measured, not assumed.**

**MEASURED, three ways:**

1. **`vpp_mv` crosses the wire.** `resolve_chip('MBM27128', db=EpromDatabase())` returns keys `['algorithm', 'bus-config', 'chip-id', 'flags', 'memory-size', 'pin-count', 'pulse-delay', 'vpp_mv']` with `vpp_mv == 18000`.
2. **`MBM27128` is in the golden baseline.** `tests/golden/wire_dict_baseline.json` → `records["FUJITSU|MBM27128|2"]` exists, **746 records total**, and its record reads:
   ```json
   {"algorithm": 7, "bus-config": {"bus": [0,…,13], "vpp-pin": 15}, "chip-id": 0,
    "flags": 0, "memory-size": 16384, "pin-count": 28, "pulse-delay": 200, "vpp_mv": 18000}
   ```
3. **That exact key already appears in the 197 layer** carrying `{"pulse-delay": 1000}` — so the 199 layer shares a key with the 197 layer and must be **field-disjoint** from it (`vpp_mv` vs `pulse-delay`: disjoint ✅). This is precisely the situation the 198 layer already handled with `FUJITSU|MBM27C1001|7`, and the module's docstring names field-disjointness as what makes `dict.update` composition order-independent.

**Conclusion: yes, `tests/golden/wire_dict_expected_deltas_199.json` is required, and it holds exactly ONE delta.**

**Exact key format.** `MANUFACTURER|part_number|<positional index within that manufacturer's list>` — e.g. `FUJITSU|MBM27128|2`. The 197 layer's own `meta.provenance` states why it is generated and never hand-transcribed:

> *"the `|<i>` record-key suffix is a positional index within each manufacturer's list and would silently rot if any row is ever added or reordered."*

**Exact file shape** — two top-level keys, `deltas` and `meta`; `meta` carries **exactly five** required keys, alphabetically `decision`, `honesty`, `how_to_update`, `phase`, `provenance`, each a non-empty string. Plan 198-01's verify leg asserts exactly that:

```python
assert set(d) == {'deltas', 'meta'}
assert set(d['meta']) == {'decision', 'honesty', 'how_to_update', 'phase', 'provenance'}
assert all(isinstance(v, str) and v.strip() for v in d['meta'].values())
```

**The 199 layer's content, fully determined:**

```json
{
  "deltas": { "FUJITSU|MBM27128|2": { "vpp_mv": 21000 } },
  "meta": { "decision": "…", "honesty": "…", "how_to_update": "…",
            "phase": "199-what-the-rails-can-actually-deliver", "provenance": "…" }
}
```

**How the test loads the layers** — `tests/test_wire_dict_equivalence.py` (705 lines) composes the golden with **six ORDERED, FIELD-DISJOINT delta layers** (149, 153, 182, 194, 197, 198) via `dict.update`, and per its own docstring:

> *"A future phase adding a SEVENTH layer should add a seventh delta file and a seventh set of legs here, rather than editing any existing delta file or folding a seventh layer's entries into one of these six."*

**What a 199 layer obliges the planner to touch in that module — four things, each named by the module's own docstring:**

1. Rename/extend the composition test `test_live_capture_matches_golden_plus_the_149_and_153_and_182_and_194_and_197_and_198_deltas` to include 199, and add the 199 non-vacuity + exact-count legs (`len(deltas_199) == 1`, not "at least").
2. Add the pairwise field-disjointness check for the new layer — **the 199-with-197 pair is the one that matters**, sharing key `FUJITSU|MBM27128|2` and kept passing only by `vpp_mv` ≠ `pulse-delay`.
3. **Compose the 199 layer into `test_exactly_84_records_change_flags_and_no_other_field_moves`.** If it is not composed, `MBM27128` surfaces there as an unexplained change and the count floats from 84 to 85. This is the leg 198-01 had to handle identically ("composing the 198 layer keeps the count at 84 rather than letting it float to 86").
4. Add `test_the_199_delta_layer_is_capable_of_failing`, mirroring tests 8/9/10.

**The anti-laundering rule stands: `wire_dict_baseline.json` and all six prior delta files must be byte-unchanged.** Plan 198-01's proven guard:

```bash
git diff --quiet <pre-phase-sha> -- tests/golden/wire_dict_baseline.json \
  tests/golden/wire_dict_expected_deltas_149.json tests/golden/wire_dict_expected_deltas_153.json \
  tests/golden/wire_dict_expected_deltas_182.json tests/golden/wire_dict_expected_deltas_194.json \
  tests/golden/wire_dict_expected_deltas_197.json tests/golden/wire_dict_expected_deltas_198.json
```

### B11. The characterization snapshot — **exactly one line. Measured.**

**MEASURED:** `/usr/bin/grep -c "MBM27128" tests/__snapshots__/test_characterization.ambr` → **`1`**. The single occurrence is line 757:

```
  | MBM27128            | FUJITSU          |   28 |            | UV-EPROM    | 18.0v|
```

**MEASURED:** the enclosing snapshot block is `# name: test_list` (the `# name:` markers immediately preceding line 757 are `test_info_known_chip[test_info_known_chip_stderr]` at 498 and `test_list` at 501). So **exactly one test** — `tests/test_characterization.py::test_list` — and **exactly one line** moves, `18.0v` → `21.0v`.

**The expected `--numstat` is `1  1`** (one insertion, one deletion), not 198's `2 2`. The proven re-record idiom, adapted from Plan 198-01 verbatim except the count:

```bash
cd /workspaces/firestarter_app && \
.venv/ci-replica/bin/python -m pytest "tests/test_characterization.py::test_list" \
  -o addopts="" -q -p no:randomly --snapshot-update >/dev/null 2>&1; \
NS=$(git diff --numstat -- tests/__snapshots__/test_characterization.ambr) && \
printf '%s\n' "$NS" && printf '%s\n' "$NS" | /usr/bin/grep -qP '^1\t1\t'
```

**Failing direction:** zero lines means the rendered voltage never moved (the override did not apply); more than one line-pair means a blanket update swept in unrelated drift.

**MEASURED cross-check on the render path:** `print_eprom_list_table` in `firestarter/eprom_info.py` renders the VPP column only when `_etype not in {"SRAM", "FRAM"} and _vpp_mv > 0`, via `format_mv(_vpp_mv)`. `MBM27128` is `UV-EPROM`, so the column is live and `21000 → "21.0v"` is deterministic.

### B12. `197-REGEN-DIFF.md`'s shape, for reuse

**MEASURED** — read in full. Its structure, in order:

1. **`# Phase NNN — The 746-Row Regeneration Diff`** with a `**Measured:**` line naming the date, the sub-repo sha, the branch, and *which plans are committed at that point* ("the database diffed here is the phase's final generated state").
2. **A one-paragraph claim** stating exactly what the artifact is evidence for, in requirement terms, with the headline numbers.
3. **`## Reproducible method`** — the baseline ref (`git show <sha>:firestarter/data/chip_database.json`), the live path, **and a paragraph naming the two wrong methods and why** (`tools/baseline/chip_database.baseline.json` is stale; `tools/diff_db.py` does not exist).
4. **The full diff script text, inline, in a fenced block**, explicitly labelled *"a throwaway, run from `firestarter_app`'s repository root and NOT committed under `tools/`"* — because `tools/` sits outside every CI gate.
5. **A paragraph explaining what the script guarantees**: key-set equality asserted *before* any field comparison (`KEY SET MISMATCH` + exit 1), union of leaf dotted paths with `<absent>` for one-sided paths, sorted emission so re-running is byte-identical.
6. **`## Row-count line`** — a four-item list: Rows in / Rows out / Rows changed / `support_status` values changed, and a sentence reconciling it against the phase's own prediction (or recording the discrepancy).
7. **`## The N changed fields, one line per field`** — a table `| Manufacturer | Part number | Field path | Before | After | Cause |`, where **Cause** is either "Decode rule: …" or "Override: entry `KEY` in `tools/datasheet_overrides.json`, `datasheet: …` (plan `NNN-NN`)". Then a closing sentence asserting every changed field fits one of the two kinds and none fits neither.
8. **`## The two zero-diff claims`** — explicit claims about what did **not** move, each with the commit that proved it. *"These are load-bearing and a table of CHANGES cannot show them."*
9. **`## Honesty limit`** — what the diff proves and, sharply, what it does not (*"It does NOT prove any new value is electrically correct"*).
10. Footer: `*Phase: …*` / `*Measured: …*`.

**For Phase 199 this collapses to a one-row instance:** rows in 746 / out 746 / changed **1** / `support_status` changed **0**; one table row (`FUJITSU | MBM27128 | electrical.vpp_mv | 18000 | 21000 | Override: entry FUJITSU/MBM27128 …`); and the zero-diff section becomes the **positive claim that no other row moved**, which for this phase is the whole point. **Yes, reuse the shape** — CONTEXT.md's discretion note says it almost certainly should be, and nothing measured here argues otherwise. Suggested path: `.planning/phases/199-what-the-rails-can-actually-deliver/199-REGEN-DIFF.md`.

---

## C. The 30-row classification test (RAIL-02, D-18)

### C13. The 30-row measurement, reproduced

**MEASURED this session** against the live `firestarter_app/firestarter/data/chip_database.json`.

**The reproducing one-liner** (safe, read-only):

```bash
cd /workspaces/firestarter_app && python3 -c "
import json, collections
db = json.load(open('firestarter/data/chip_database.json'))
rows = [(m, r) for m, rs in db.items() for r in rs if r.get('electrical', {}).get('vpp_mv', 0) >= 18000]
PATH = {0x07: 'DROP_RESISTOR', 0x08: 'DROP_RESISTOR', 0x0B: 'DIRECT_VPE'}
print('count', len(rows))
print('by mv  ', dict(collections.Counter(r['electrical']['vpp_mv'] for _, r in rows)))
print('by path', dict(collections.Counter(PATH.get(r['programming']['algorithm'], '?') for _, r in rows)))
print('status ', dict(collections.Counter(r.get('support_status') for _, r in rows)))
for m, r in sorted(rows, key=lambda x: (-x[1]['electrical']['vpp_mv'], x[0], x[1]['part_number'])):
    a = r['programming']['algorithm']
    print(f\"{r['electrical']['vpp_mv']:6d} | 0x{a:02X} | {PATH.get(a,'?'):13s} | {r['electrical']['pin_count']:2d} | {m} | {r['part_number']}\")
"
```

**Output, verbatim:**

```
count 30
by mv   {18000: 22, 25000: 6, 21000: 2}
by path {'DIRECT_VPE': 20, 'DROP_RESISTOR': 10}
status  {'supported': 30}
```

| vpp_mv | algo | vpp_path | pins | Manufacturer | part_number |
|---|---|---|---|---|---|
| 25000 | 0x0B | DIRECT_VPE | 24 | INTEL | `2732,2732A,M2732,M2732A` |
| 25000 | 0x0B | DIRECT_VPE | 24 | INTEL | `M2716,M2716M` |
| 25000 | 0x0B | DIRECT_VPE | 24 | SGS-THOMSON | `ETC2716,M2716` |
| 25000 | 0x0B | DIRECT_VPE | 24 | ST | `ETC2716,M2716` |
| 25000 | 0x0B | DIRECT_VPE | 24 | TEXAS INSTRUMENTS | `2516` |
| 25000 | 0x0B | DIRECT_VPE | 24 | TEXAS INSTRUMENTS | `2532` |
| 21000 | 0x0B | DIRECT_VPE | 24 | SGS-THOMSON | `M2732A` |
| 21000 | 0x0B | DIRECT_VPE | 24 | ST | `M2732A` |
| 18000 | 0x0B | DIRECT_VPE | 24 | AMD | `AM2716` |
| 18000 | 0x0B | DIRECT_VPE | 24 | AMD | `AM2732,AM2732A` |
| 18000 | 0x0B | DIRECT_VPE | 24 | FAIRCHILD | `NMC27C16` |
| 18000 | 0x0B | DIRECT_VPE | 24 | FAIRCHILD | `NMC27C16Q` |
| 18000 | 0x0B | DIRECT_VPE | 24 | FAIRCHILD | `NMC27C32,NMC27C32E,NMC27C32EH,NMC27C32H,NMC27C32Q` |
| **18000** | **0x07** | **DROP_RESISTOR** | **28** | **FUJITSU** | **`MBM27128`** ← gh#71 |
| 18000 | 0x0B | DIRECT_VPE | 24 | FUJITSU | `MBM2732,MBM2732A,MBM27C32,MBM27C32A` |
| 18000 | 0x07 | DROP_RESISTOR | 28 | FUJITSU | `MBM27C128P` |
| 18000 | 0x07 | DROP_RESISTOR | 28 | FUJITSU | `MBM27C64` |
| 18000 | 0x07 | DROP_RESISTOR | 28 | HITACHI | `HN27C64FP` |
| 18000 | 0x07 | DROP_RESISTOR | 28 | HITACHI | `HN27C64G` |
| 18000 | 0x07 | DROP_RESISTOR | 28 | INTEL | `27128,D27128` |
| 18000 | 0x07 | DROP_RESISTOR | 28 | INTEL | `2764` |
| 18000 | 0x07 | DROP_RESISTOR | 28 | MITSUBISHI | `M5M27C128` |
| 18000 | 0x07 | DROP_RESISTOR | 28 | NEC | `UPD2764,UPD2764C,UPD2764D` |
| 18000 | 0x0B | DIRECT_VPE | 24 | NSC | `NMC27C16` |
| 18000 | 0x0B | DIRECT_VPE | 24 | NSC | `NMC27C16Q` |
| 18000 | 0x0B | DIRECT_VPE | 24 | SGS-THOMSON | `ETC2732` |
| 18000 | 0x0B | DIRECT_VPE | 24 | ST | `ETC2732` |
| 18000 | 0x0B | DIRECT_VPE | 24 | TI | `TMS2716` |
| 18000 | 0x0B | DIRECT_VPE | 24 | TI | `TMS2732A` |
| 18000 | 0x07 | DROP_RESISTOR | 28 | TI | `TMS2764` |

**Every CONTEXT.md count confirms:** 30 rows; 22/2/6 at 18000/21000/25000; 10 DROP_RESISTOR / 20 DIRECT_VPE; all 30 `supported`; the 10 drop-path rows are **all algorithm `0x07`, all 28-pin, all at exactly 18000**, and the 20 direct-VPE rows are all `0x0B`, all 24-pin, and **hold all eight of the 21000/25000 rows**. The named 10 match CONTEXT.md's list exactly.

**One useful addition CONTEXT.md does not state:** **no row in the 30 carries algorithm `0x08`.** So a test keyed on the firmware's three-key table only ever exercises two of its three rows. Worth naming in the test docstring so a later reader does not read `0x08`'s absence as an omission.

### C14. **The single most important question for the test's design: is `vpp_path` available to the host?**

**MEASURED, and the answer is plainly NO.**

```bash
cd /workspaces/firestarter_app && /usr/bin/grep -rn "vpp_path\|VPP_PATH\|DROP_RESISTOR\|DIRECT_VPE" firestarter/ tests/ tools/
```

→ **zero matches.** The concept does not exist anywhere on the host side: not in the emitted database (a row's emitted keys are `electrical.{pin_count,size_bytes,type,vcc_mv,vdd_mv,vpp_mv}`, `part_number`, `pinout`, `programming.{algorithm,chip_id_check,chip_id_value,infoic_page_size_raw,protect_off_before,protect_on_after,pulse_duration_us}`, `support_status` — **14 emitted fields**, guarded at 14 by `tests/test_chip_database_field_inventory.py`), not in the wire dict, not in `constants.py`, not in any test.

The mapping lives **only** in the firmware, in `firestarter_fw/src/proms/eprom_params.cpp`, verbatim:

```c
static const uint8_t EPROM_PARAM_KEYS[] PROGMEM = { 0x07, 0x08, 0x0B };
...
    /* 0x07 PROTO_EPROM_28PIN */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x08 PROTO_EPROM_32PIN */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x0B PROTO_EPROM_24PIN */ { 75000UL, 50000UL, 255, 0, VERIFY_PER_PULSE,            VPP_PATH_DIRECT_VPE    },
```

**So the test must encode the algorithm → path mapping itself. There is no honest alternative.**

**And it must NOT scan the firmware source to derive it.** Three measured reasons:

1. `firestarter_app`'s CI uses `actions/checkout@v4` with **no `submodules:` key** — `firestarter_fw` is **not present** in the app's CI checkout. A firmware-scanning test would either error or skip in CI.
2. Project memory records the exact failure mode: *"App gates scan FIRMWARE source — renames break them; they fail OPEN"*, and *"Devcontainer sibling layout masks CI-only defects."* The devcontainer has `firestarter_fw/` as a sibling, so such a test would pass locally and be vacuous in CI — the worst outcome.
3. D-18's whole point is a test that **fails** when the answer changes. A gate that fails open fails that requirement by construction.

**The honest way to write it, stated plainly:**

- Put the mapping in the test module as a **named module constant**, e.g. `_ALGORITHM_TO_VPP_PATH = {0x07: "drop-resistor", 0x08: "drop-resistor", 0x0B: "direct-vpe"}`.
- State in the **module docstring** (not a comment — CLAUDE.md hard rule) that this is a **deliberate mirror** of `firestarter_fw/src/proms/eprom_params.cpp`'s `EPROM_PARAMS` table, that the host has no access to that table, and — this is the part that makes it honest — **that this test therefore cannot detect a firmware-side change to the table. It detects a database-side change only.** That limit also belongs in § 10.
- Derive **everything else** from the live database: the row set, the voltages, the counts. No hand-kept part-number list. `tests/test_flash4_erase_gate.py` establishes exactly this discipline and even asserts it (*"NO PART-NUMBER LITERAL IN THE MODULE"*).
- Assert the **exact** counts, never "at least": `len(rows) == 30`, `Counter(mv) == {18000: 22, 21000: 2, 25000: 6}`, `Counter(path) == {"drop-resistor": 10, "direct-vpe": 20}`, and `all(support_status == "supported")`. A 31st row arriving upstream, or a row changing algorithm, then reddens.

**Interaction with D-17 — important, and easy to get wrong.** The 30-row measurement above was taken **before** the `MBM27128` override lands. After D-17, `MBM27128` moves 18000 → 21000, so the counts become **`{18000: 21, 21000: 3, 25000: 6}`** — the total stays 30 and the path split stays 10/20 (algorithm is unchanged), but **two of the three voltage counts move.** The test must be written against whichever state its own plan commits, and the plan must sequence the test task **after** the override task or state the pre/post counts explicitly. **INFERRED from the measured override semantics; the regeneration will confirm it.**

### C15. Where the test lives, and `tests/` conventions

**MEASURED.**

- **Naming:** `tests/test_<subject>.py`, one module per subject. Precedents in this family: `test_flash4_erase_gate.py`, `test_jp5_gate.py`, `test_build_db_inclusion.py`, `test_b15_page_size_corroboration.py`, `test_chip_database_field_inventory.py`.
- **Module docstring convention:** every one of these opens with the four-line MIT header, then a one-line subject statement, then a numbered **`Coverage:`** list naming each test and *what defect class it closes*. `test_flash4_erase_gate.py`'s six-item list and `test_wire_dict_equivalence.py`'s ten-item list are the models. **This is where the honesty limits go** — it is a docstring, not a comment, and is explicitly permitted.
- **Two database-loading conventions, both live:**
  - `EpromDatabase(skip_local_override=True)` — used by `test_flash4_erase_gate.py`, `test_characterization.py`, `test_chip_resolver.py`, `test_chip_test.py` and others. `skip_local_override=True` is load-bearing: it ignores a developer's `~/.firestarter` overrides so the test reads the shipped database.
  - Direct `json.load` via a path constant — `test_b15_page_size_corroboration.py` does `_DB_FILE = _FA_DIR / "firestarter" / "data" / "chip_database.json"`, and `test_build_db_inclusion.py` states it *"load[s] chip_database.json directly (not via EpromDatabase)"*.
  - **Recommendation for this test: the direct `json.load` path.** The claim is about the *generated artifact* (the 30 rows the generator emits), not about what `EpromDatabase` resolves, and `test_build_db_inclusion.py` is the exact precedent for that framing.
- **Ordering:** `pytest-randomly` is installed (`.venv/ci-replica/bin/python -m pytest … -p no:randomly` runs clean — **MEASURED**, 21 passed in 0.85 s on `test_flash4_erase_gate.py`). The 197/198 plans pass `-p no:randomly` in every verify leg. **Order must not matter** for a pure database-reading test; use `-p no:randomly` in verify legs for determinism, not because the test depends on order.
- **`addopts`:** `pyproject.toml` sets `addopts = "-ra -q"`. Project memory records that doubling `-q` hides the count line, which is why the 198 legs all pass `-o addopts=""`. Copy that.

**Home:** a **new file** is right. `tests/test_vpp_rail_classification.py` (name at the planner's discretion). No existing module owns "which rows ask more than a rail can give", and folding it into `test_build_db_inclusion.py` would bury a phase-defining claim inside an unrelated module's coverage list. **Discretion, per CONTEXT.md:** one test over all 30 rows, or split by `vpp_path`. **Recommendation: one module, several tests** — one for the total/voltage census, one for the path split, one for the all-`supported` claim, and one non-vacuity test proving the gate can fail (the discipline `test_wire_dict_equivalence.py` applies to every layer).

### C16. CI gates this test must pass

**MEASURED** from `firestarter_app/.github/workflows/ci.yml` — the `ci` job, in order:

| Step | Exact command | Scope |
|---|---|---|
| Python | `actions/setup-python@v5` with `python-version: '3.11'` | — |
| Install | `pip install -e .[test]` | — |
| ruff lint | `ruff check firestarter/ tests/` | `firestarter/` + `tests/` |
| ruff format | `ruff format --check firestarter/ tests/` | `firestarter/` + `tests/` |
| pytest | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | `tests/`, **coverage floor 70 %** |
| smoke | `pip install -e . && firestarter --help` | — |

**mypy is NOT a CI step. MEASURED:** `grep -rn mypy .github/workflows/` returns nothing; mypy appears only as a dev dependency (`"mypy>=2.1.0,<3"`) and a `[tool.mypy]` config block in `pyproject.toml`. Project memory independently records that *"the pre-release ships even when Host CI fails"* and that the mypy watermark gate is scoped `firestarter/ tests/` on py3.11. **So mypy is a local discipline, not a merge gate.** Run it, but a plan must not claim CI enforces it.

**If the new policy module is added to a mypy strict island** (`[[tool.mypy.overrides]]` with `disallow_untyped_defs = true`), note the measured membership: `firestarter.main`, `cli_handlers`, `chip_resolver`, `frame_parser`, `codec`, `address_parser`, `exceptions`, `serial_comm`, `sdp_honesty`, `log_capture`. **The three existing gate modules are NOT in it.** Adding the new module would be a deliberate strengthening (as `sdp_honesty` was); not adding it matches the three precedents. Either is defensible — **recommendation: match the three precedents and stay out, and instead type the module fully anyway**, as `flash4_erase_gate.py` already does (`from __future__ import annotations`, full annotations, `Mapping[str, Any] | None`).

**The devcontainer-vs-CI Python hazard, MEASURED and real.** The devcontainer default `python3` is **3.12**; CI is **3.11**. Project memory records this as *"PROVEN to have broken beta CI"*. A 3.11 replica already exists and works:

```bash
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -V
# -> Python 3.11.16   [MEASURED this session]
```

**Every pytest/mypy verify leg in this phase must invoke `.venv/ci-replica/bin/python`, never bare `python`/`python3`.** Plans 198-01 and 198-04 already do this throughout; copy the idiom verbatim.

**Two further CI-visible invariants this phase must not move**, both MEASURED as existing guards:

- `tests/test_chip_database_field_inventory.py` pins the emitted field set at **14 fields** — this is why D-09 refuses a per-part routing field.
- `tests/test_build_db_inclusion.py` asserts against `build_db.RURP_VPP_CEILING_MV` in three places, including a synthetic row proving the ceiling reason string. **D-01 leaves all three green** — nothing in this phase touches the constant.

---

## D. The warning policy module (RAIL-03, D-13…D-16)

### D17. The shared shape of the three precedent modules

**MEASURED** — all three read in full: `jp5_gate.py` (155 lines), `page_size_gate.py` (182), `flash4_erase_gate.py` (79).

**What they share:**

| Aspect | Observed shape |
|---|---|
| **Header** | The four-line MIT block (`Project Name: Firestarter` / `Copyright (c) 2024 Henrik Olsson` / blank / `Permission is hereby granted under MIT license.`), then a blank line, then a one-line subject with its requirement ids in parentheses where they exist (`(SAFE-01/02/04)`). |
| **Docstring body** | Several paragraphs of *policy prose*: what the hardware actually does, why a wrong answer is harmful, and — every time — an explicit **polarity paragraph** saying whether the gate fails open or closed **and arguing against the opposite choice**, naming the sibling modules by filename. |
| **The purity claim, stated almost identically in all three** | `jp5_gate`: *"No I/O, no environment reads, no serial access -- the wire dict and the operation name are the whole input, which is what makes the policy testable without a board and keeps eprom_operations.py and cli_handlers.py free of the reasoning."* `flash4_erase_gate` and `page_size_gate` repeat it nearly verbatim. **D-13 is quoting this sentence.** |
| **Inputs** | The **wire dict** (`Mapping[str, Any] \| None`, or a narrowed slice like `bus_config: dict \| None`), the **operation name** (`str`), plus the **chip name** as a separate argument — *the wire dict carries no name*, MEASURED: its keys are `algorithm, bus-config, chip-id, flags, memory-size, pin-count, pulse-delay, vpp_mv`. |
| **Operation scoping** | A module-level `frozenset` naming the operations the policy applies to: `DAMAGE_CAPABLE_OPERATIONS = frozenset({"write", "erase"})`, `_WRITE_OPERATIONS = frozenset({"write"})`. A non-matching operation returns early, unconditionally. |
| **Message construction** | A module-level `_..._FORMAT` string plus a small `def <x>_text(...) -> str` builder, *"built from `_REFUSAL_FORMAT` rather than assembled inline, so a test can assert the exact shape instead of a whole sentence."* |
| **Typing** | `from __future__ import annotations` (the two newer ones), full annotations, `Mapping[str, Any] \| None`. |
| **Single-sourcing** | Shared values are imported, never re-declared: `page_size_gate` imports `FLASH4_PROTOCOL_ID` from `flash4_erase_gate`; `jp5_gate` derives `SOCKET_PIN_1_BUS_LINE` from `database.pin_conversions[32][1]`. |

**How each expresses its refusal — the part this phase inverts:**

| Module | Refusal mechanism |
|---|---|
| `jp5_gate` | **Two layers.** `require_acknowledged(...) -> None` **raises `Pin1HazardRefusedError`** (defence in depth, called from `eprom_operations.write_eprom` and `erase_eprom`); `confirm_or_refuse(...) -> bool` prints the hazard text, refuses off-TTY, and otherwise prompts with `default=False`, **returning `bool`** (called from `cli_handlers`). |
| `page_size_gate` | `require_page_size` / `require_page_alignment` **raise** `PageSizeUnavailableError` / `PageAlignmentError`. |
| `flash4_erase_gate` | A pure predicate `is_flash4(...) -> bool` plus `refusal_text(name) -> str`; **the caller** does `click.echo(refusal_text(eprom)); sys.exit(1)`. The module itself raises nothing. |

**D-13's "this module never refuses" maps cleanly onto the `flash4_erase_gate` split**, which is the newest and simplest of the three: **a pure predicate + a pure text builder, with the caller deciding what to do.** Except here the caller does not exit — it emits and continues.

**Recommended surface for the new module** (shape only; names are the planner's discretion per CONTEXT.md):

```python
_SHORTFALL_OPERATIONS = frozenset({"write", "info"})

def vpp_shortfall(programmer_data: Mapping[str, Any] | None,
                  deliverable_mv: int) -> int | None:
    """The required vpp_mv when it exceeds what the shield can deliver, else None."""

def should_route_vpe(programmer_data: Mapping[str, Any] | None,
                     operation: str,
                     deliverable_mv: int) -> bool:
    """True when this operation on this part must set FLAG_VPE_AS_VPP."""

def shortfall_text(chip_name: str, required_mv: int, deliverable_mv: int) -> str:
    """The single operator-facing wording (D-16). Names both voltages."""
```

Note `should_route_vpe` and `vpp_shortfall` are the **same predicate** (D-09: the flag is set exactly when the required voltage exceeds the deliverable maximum) — keep one predicate and derive both, so the warned condition and the routed condition **cannot drift apart**. That is the same single-sourcing argument `flash4_erase_gate`'s docstring makes about `FLASH4_PROTOCOL_ID`.

**Polarity — state it explicitly in the docstring, as all three precedents do.** This gate should **fail OPEN** on absent evidence (no `vpp_mv` key, `None`/empty dict → no warning, no routing), for `flash4_erase_gate`'s exact reason: guessing wrong in the closed direction would route VPE — *raising* a rail — on every part this predicate cannot classify, which is a hardware risk, not merely an availability one. **Absent evidence must never cause a rail to be raised.**

**The threshold's provenance — D-08's hard constraint made concrete.** The `deliverable_mv` value **does not exist until the bench session produces it.** Two mechanisms are available (CONTEXT.md leaves the choice to the planner):

- **A module constant** in the new gate, e.g. `RURP_REV20_DROP_PATH_DELIVERABLE_MV = <measured>`, with the module docstring naming the bench record and the § 10 section it comes from. Simpler; matches `page_size_gate`'s `_ACCEPTED_PAGE_SIZES` precedent of naming a hardware-derived set explicitly.
- **A parameter** threaded from the call sites. More testable, but there is then no single place a reader finds the number.

**Recommendation: a module constant, plus every function taking `deliverable_mv` as a parameter that defaults to it.** That gives the test a way to drive the predicate at arbitrary thresholds (so the *test* never hardcodes the measured figure either) while giving a reader one place to find the shipped number. **Until the bench runs, the number is a placeholder and the plan must say so** — write the host plan with the constant's value as an explicit `<bench-measured>` blank the bench plan fills, and make the host plan `depends_on` the bench plan. **Nothing in this phase may write `18000` as the threshold before the DMM reading exists** (D-07/D-08).

### D18. The tests for the three gates — style, and what makes them board-free

**MEASURED** from `tests/test_flash4_erase_gate.py` (the cleanest instance).

**Style:**
- A numbered `Coverage:` list in the module docstring, each item naming the defect class it closes.
- **The pure predicate is parametrized over values derived from the live database**, never a hand-picked subset:
  ```python
  _SHIPPED_ALGORITHM_VALUES = sorted(_shipped_algorithm_values(EpromDatabase(skip_local_override=True)))

  @pytest.mark.parametrize("algorithm", _SHIPPED_ALGORITHM_VALUES)
  def test_is_flash4_true_only_for_algorithm_5_over_shipped_values(algorithm):
      assert is_flash4({"algorithm": algorithm}) == (algorithm == FLASH4_PROTOCOL_ID)
  ```
- **A dedicated polarity test whose docstring argues with a future reader**: *"This is the single most likely thing a later reader will 'fix' back to fail-closed; this test is the place that survives to argue with them."* Copy this device — the new gate's fail-open polarity has the same exposure.
- **A "no part-number literal in the module" test**, using `inspect`/`pathlib` to read the module's own source and assert no shipped `part_number` string occurs in it, docstrings included. Directly applicable here.
- **A message-shape test** asserting exact line count and a forbidden-substring list. For this phase the forbidden list should include any mention of the pot (**D-15**) and any wording that distinguishes "VPE rescues this" from "nothing rescues this" (**D-16**).

**What makes them board-free — three measured devices:**
1. `CliRunner()` from `click.testing` drives the real CLI in-process.
2. `patch.object(cli_handlers, "resolve_chip", return_value={...})` injects a synthetic wire dict, so no database lookup and no chip need exist.
3. An `AppContext` built entirely from `Mock(spec=...)` objects — `eprom_operator=Mock(spec=EpromOperator)`, `hardware_manager=Mock(spec=HardwareManager)`, etc. — so **no serial port is ever opened**, and `eprom_operator.write_eprom.assert_not_called()` / `.assert_called_once()` proves whether the operation proceeded.

**That third device is exactly what proves RAIL-03's "and the operation still proceeds":** assert the warning text is in `result.output` **and** `eprom_operator.write_eprom.assert_called_once()`, in the same test. There is also a shared `make_app_context` / `app_context` factory in `tests/conftest.py` (Phase 132, RETIRE-05) that supersedes the per-module copies — **prefer it** over hand-rolling a fourth `_cli_app_context`.

### D19. The `write` call site — exactly where the derived flag must land

**MEASURED**, the full chain:

```
cli_handlers.py  @click.option("--vpe-as-vpp", "vpe_as_vpp", is_flag=True, help="Use VPE as VPP voltage")   [line ~588, `write` ONLY]
      ↓  vpe_as_vpp: bool  (write handler parameter)
cli_handlers.py  eprom_data = resolve_chip(eprom, db=app.db)          ← the wire dict, carries vpp_mv
      ↓
cli_handlers.py  jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "write")   ← gate call site
                 page_size_gate.require_page_size(eprom, eprom_data, "write")
                 page_size_gate.require_page_alignment(eprom, eprom_data, "write", address, input_file)
      ↓
cli_handlers.py  app.eprom_operator.write_eprom(..., operation_flags=_build_op_flags(
                     blank_check=..., force=..., vpe_as_vpp=vpe_as_vpp, ...), ...)          ← **THE INJECTION POINT**
      ↓
cli_handlers._build_op_flags(*, vpe_as_vpp: bool = False, ...)  → build_flags(blank_check, force, vpe_as_vpp, verbose, ...)
      ↓
eprom_operations.build_flags:   if vpe_as_vpp: flags |= FLAG_VPE_AS_VPP
      ↓
constants.FLAG_VPE_AS_VPP = 0x10   ==   firestarter_fw/include/firestarter.h FLAG_VPE_AS_VPP 0x10
      ↓  wire
eprom_hv_route_mask():  is_flag_set(FLAG_VPE_AS_VPP) → return CTRL_VPP_REGULATOR_ENABLE   (undropped rail)
      ↓  and eprom_check_vpp() calls the SAME eprom_hv_route_mask() before reading, so the ±window follows the routed rail.
```

**The precise call site:** the `vpe_as_vpp=vpe_as_vpp` keyword inside the `_build_op_flags(...)` call in the `write` handler's `app.eprom_operator.write_eprom(...)` invocation. **This is the only place `vpe_as_vpp` reaches `_build_op_flags` on any command — MEASURED:** `grep -n "vpe.as.vpp" firestarter/cli_handlers.py` returns exactly one `@click.option` (on `write`), one handler parameter, and one `vpe_as_vpp=vpe_as_vpp` keyword. **D-11's "`write` only" is forced by the code, confirmed.**

**The recommended shape**, mirroring how the three gates are wired in (a call in `cli_handlers`, reasoning in the module), placed immediately after the existing gate calls and before `write_eprom`:

```python
shortfall_mv = rail_gate.vpp_shortfall(eprom_data)          # None when no shortfall
if shortfall_mv is not None:
    click.echo(rail_gate.shortfall_text(eprom, shortfall_mv, rail_gate.DELIVERABLE_MV))
    vpe_as_vpp = True
```

then leave the existing `vpe_as_vpp=vpe_as_vpp` keyword untouched. Two properties this gives for free:
- **`--vpe-as-vpp` survives as a manual override** (D-11) — an operator-supplied `True` is never turned off, because the assignment only ever raises the flag.
- **Nothing else in the chain changes**, so `build_flags`'s signature — which `tests/test_bug_characterization.py`'s BUG-1 contract pins — is untouched.

**One caution, MEASURED:** `eprom_operations.write_eprom` already calls `jp5_gate.require_acknowledged(...)` as a second, defence-in-depth layer. **Do not mirror that here.** A second call would emit the warning twice on the same write. D-13's module never refuses, so there is nothing for a second layer to guarantee.

### D20. The `info` call site

**MEASURED.** The `info` handler (`cli_handlers.py`, `@cli.command(name="info")`):

```python
eprom_details = app.db.get_eprom(eprom)
if not eprom_details: ...
eprom_data_for_programmer = app.db.convert_to_programmer(eprom_details)      ← THE WIRE DICT, in scope
raw_config_data, manufacturer = app.db.get_eprom_config(eprom)
structured_details = app.eprom_presenter.prepare_detailed_eprom_data(
    eprom, eprom_details, eprom_data_for_programmer, raw_config_data, manufacturer, ...)
if structured_details:
    app.eprom_presenter.present_eprom_details(structured_details, ...)
```

The `Support status:` / `Reason:` block D-14 names is in `eprom_info.py::present_eprom_details`:

```python
if chip_data.get("support_status"):
    support_status = chip_data["support_status"]
    logger.warning("Support status:      " + support_status)
    unsupported_reason = chip_data.get("unsupported_reason", "")
    if unsupported_reason:
        logger.warning("Reason:              " + unsupported_reason)
```

**Two viable insertion points, and they differ in an important way:**

| Option | Where | Trade-off |
|---|---|---|
| **(A) CLI handler** — recommended | in `cli_handlers.info`, immediately after `eprom_data_for_programmer = app.db.convert_to_programmer(...)` | Matches the three-gate convention (gates are called from `cli_handlers`). The wire dict is already in a local. `eprom_info.py` is untouched, so **no snapshot in `test_characterization.ambr` moves**. Emits before the details block rather than inside it. |
| **(B) presenter** | inject `combined_data["vpp_shortfall"]` inside `prepare_detailed_eprom_data` (which already receives `eprom_data_for_programmer`), then emit in `present_eprom_details` beside the `Support status:` block | Puts the line in the visually right place, exactly mirroring how `support_status` is injected. **But** it changes `eprom_info.py` output and risks moving `test_info_known_chip[test_info_known_chip_stderr]` snapshots for any affected part. |

**Recommendation: (A).** It keeps the phase's blast radius at the size CONTEXT.md describes, and D-14's requirement is that `info` emits the warning — not that it appears at a particular line of the block. If the planner prefers (B), the plan must budget a snapshot check for `test_info_known_chip` as well as `test_list`.

**MEASURED, important:** `info` does **not** go through `resolve_chip`, so it never raises `ChipNotImplementedError`. It works for every row, including non-`supported` ones. That is a feature here — the warning surfaces on parts `write` would refuse.

### D21. Does the wire dict at each site carry `vpp_mv`? **Yes — and the two dicts are identical.**

**MEASURED this session:**

```python
d1 = resolve_chip('MBM27128', db=EpromDatabase())              # the `write` path's dict
d2 = EpromDatabase().convert_to_programmer(db.get_eprom('MBM27128'))   # the `info` path's dict
sorted(d1) == sorted(d2) == ['algorithm','bus-config','chip-id','flags','memory-size','pin-count','pulse-delay','vpp_mv']
d1 == d2   ->  True
d2['vpp_mv'] -> 18000
```

**So D-13's premise holds at both sites with no special-casing: the wire dict is one shape, it carries `vpp_mv`, and the module's whole input is that dict plus the operation name plus the chip name.** The only difference between the two sites is the *route to* the dict (`resolve_chip` vs `convert_to_programmer`), not its contents — and `resolve_chip` is a thin wrapper that additionally enforces `support_status`.

Spot-checked on two of the eight high rows: `M2716` and `2532` both return `vpp_mv: 25000`, `algorithm: 11 (0x0B)`, `pin-count: 24` through `convert_to_programmer`.

### D22. Logger, level, and the house voice

**MEASURED.** Three distinct loggers, one per module:

```python
firestarter/cli_handlers.py:     logger = logging.getLogger("Firestarter")
firestarter/eprom_info.py:       logger = logging.getLogger("EpromConsolePresenter")
firestarter/eprom_operations.py: logger = logging.getLogger("EpromOperator")
```

**Level: `logger.warning`** for the `info` surface (that is literally what D-14 points at). For the `write` surface, the measured house practice for a **warn-and-proceed** message is **`click.echo`**, not the logger — and the reason is stated in the source at the `--skip-erase` block and again at the `--pulse-us` block:

> *"click.echo (never logger.info): this must be visible at DEFAULT verbosity, with no -v needed. Reason: a bench artifact or log captured without the command line beside it cannot otherwise tell you the pulse was not the database's -- and this evidence will be read by strangers."*

That argument applies with full force here: a shortfall warning that a `-v`-less run swallows is exactly the silent attempt RAIL-03 forbids. **Recommendation: `click.echo` on `write` (matching `flash4_erase_gate`'s caller and the two warn-and-proceed blocks), `logger.warning` on `info` (matching the `Support status:` block D-14 names).** Both are visible at default verbosity; state the split in the module docstring so it does not read as an accident.

**Three verbatim examples of the house voice, for D-16's one wording:**

1. From `cli_handlers.py`'s warn-and-proceed `--skip-erase` block:
   > `MBM27128: --skip-erase has nothing to skip on this chip's protocol — the 28C family's write path (protocol 0x0D) performs no erase step, so there is nothing here for this flag to skip; each page write applies directly. The family does have a standalone erase, reachable as `firestarter erase`, which this flag does not affect. Proceeding with a normal write.`

2. From `eprom_operations.py`'s blank-check warning:
   > `Blank check is not applicable to {NAME} (electrical type: {etype}, protocol: 0x{proto:02X}). SRAM/FRAM are volatile or byte-rewritable — they have no factory-blank state and the firmware has no blank-check op for them.`

3. From `flash4_erase_gate.refusal_text` — the minimal end of the register:
   > `Erase not supported for {NAME}`

**The pattern, extracted:** `{CHIP NAME UPPERCASED}: <the measured fact>. <what the tool is doing about it>. <what happens next>.` Em dashes for parenthetical cause; no exclamation; no advice the tool cannot back. **Note how example 1 ends: "Proceeding with a normal write."** — that closing clause is exactly RAIL-03's "and the operation still proceeds", already in the house voice.

**And what D-15/D-16 forbid in that sentence:** no pot target, no mention of which rail is being used beyond "routing VPE", no "this will/will not work", no distinction between the rescuable ten and the unreachable eight. The `diagnostic_report.py` disclosure is the honesty model:

> `vpp/vpe readings measure the regulator rail only -- they do not show whether the eprom socket is connected`

---

## E. gh#71 (RAIL-05, D-19/D-20)

### E23. `197-GH70-ANSWER.md` — structure, and the exact held-pending list

**MEASURED** — read in full. **Five sections**, in order:

1. **`# gh#70 Answer — Draft`**, immediately followed by a bold standing warning: *"This is an internal draft-tracking file. Only the "Comment Body" section below is the text intended for posting to the public GitHub issue. The header above it and the notes below it are internal project bookkeeping and must never be pasted onto the issue."*
2. **`## Status`** — `**DRAFT — APPROVED, HELD PENDING THE BETA CUT. NOT POSTED.**`, then the dated operator decision as a numbered list (publication route + any approved text amendments, each with the reason), then `**Nothing has been posted.**` pointing at the deferral section.
3. **`## Internal provenance (project bookkeeping only — do not post)`** — bulleted: which phase/plan produced it and which requirement it answers; where internal backlog numbers live **and an explicit statement that they are kept out of the public body** (*"meaningless to a reader without this project's planning directory"*); which internal phase owns each "worked separately" claim; technical cross-checks for whoever resolves the version placeholder.
4. **`## Comment Body`** — preceded by `*(Post this section verbatim once the version line is resolved. Do not include this file's header or footnotes.)*`, then **delimited top and bottom by a bare `---`**. Inside, bolded lead-ins: `**What changed.**`, `**Version:** held pending the v1.40 beta cut; …`, `**What this correction does not do.**`, **`**This correction does not close this report.**`** ← *the heading convention CONTEXT.md D-19 refers to*, `**A second finding, measured but not yet tested on real hardware.**`, `**Two more things worth recording here.**`
5. **`## Held-pending deferral (internal — do not post)`** — the consolidated list. Its **exact current contents and format**:
   - An opening bold pair: *"This comment is held, not posted, by explicit operator decision dated 2026-09-18 (`hold`)."* / *"**This is now the consolidated list for every held answer in this milestone.**"*, plus a sentence naming the sibling file (`198-GH66-ANSWER.md`) and stating both files carry the same five-section shape and the same four steps, *"so a reader who finds either file reaches complete instructions for both."*
   - Then four labelled bullets, each a bold lead-in:
     - **`What is held:`** — names the exact section of each file, what it claims, and the issue's current comment state (*"gh#70 remains OPEN with 3 comments, none from this project; gh#66 remains OPEN with 6 comments, none from this project."*)
     - **`Why:`** — the no-upstream argument, with the measured commit counts (41 meta / 14 app ahead of `origin/beta`, `git branch -r --contains` returning nothing), and the statement that the reasoning is not per-issue.
     - **`What releases the hold:`** — the v1.40 beta cut; *"The same beta cut releases both held drafts; there is no separate trigger for gh#66."*
     - **`Exactly what to do at that point — the following four steps apply once per issue, run separately for gh#70 and for gh#66:`** — a numbered 1–4 list: (1) replace the `**Version:**` line; (2) re-run the no-over-claim and no-attribution checks against the final body only; (3) post ONLY the `## Comment Body` section verbatim, *"starting after the opening `---` and ending before the closing `---`"*, with `gh issue comment <N> --repo henols/firestarter --body-file`; (4) record the returned comment URL back into that draft and mark the requirement complete in `.planning/REQUIREMENTS.md`.
     - **`Requirement status:`** — PULSE-04 (gh#70) and VOLT-04 (gh#66) NOT satisfied by their plans, carried to milestone close, with the artifact paths that carry them.

**What D-20 requires this phase to do to that section, concretely:**
- Add gh#71 / `199-GH71-ANSWER.md` to the sibling-file sentence in the opening paragraph (currently names only one sibling).
- Extend **What is held** with gh#71's line and its measured current comment state (see E25: **OPEN, 3 comments, one from `dim20` and two from `henols` — so "none from this project" is FALSE for gh#71 and must not be copied**).
- Extend **What releases the hold** to say the same cut releases all three.
- Change *"apply once per issue, run separately for gh#70 and for gh#66"* to name all three, and add `71` to step 3's command list and RAIL-05 to step 4's requirement list.
- Extend **Requirement status** to `PULSE-04`, `VOLT-04` **and `RAIL-05`**.

### E24. The 198 equivalent

**MEASURED** — `.planning/phases/198-the-two-voltage-nibbles/198-GH66-ANSWER.md`, **119 lines**, the same five-section shape:

```
1:   # gh#66 Answer — Draft
3:   **This is an internal draft-tracking file. Only the "Comment Body" section below is the text …
7:   ## Status
9:   **DRAFT — APPROVED, HELD PENDING THE BETA CUT. NOT POSTED.**
24:  **Nothing has been posted.** See "Held-pending deferral" near the end of this file …
27:  ## Internal provenance (project bookkeeping only — do not post)
57:  ## Comment Body
67:  **What changed — corrections only. This does not close the report.**
76:  **Version:** held pending the v1.40 beta cut; this line will be updated …
86:  ## Held-pending deferral (internal — do not post)
88:  **This comment is held, not posted, by the same operator decision that holds gh#70, dated …
```

**Two things to copy for 199:**
- The 198 body folds the "does not close" clause **into the "What changed" heading itself** (`**What changed — corrections only. This does not close the report.**`) rather than giving it a separate section. Both forms exist in the precedent set; either satisfies D-19's *"everything sits under an explicit 'this does not close this report' heading."*
- 198's deferral section **defers to gh#70's as the canonical list** (*"by the same operator decision that holds gh#70"*) rather than duplicating the reasoning. **199 should do the same**: carry the four steps and the pointer, and let `197-GH70-ANSWER.md` remain the single consolidated list D-20 names.

### E25. gh#71 — current state, read-only

**MEASURED** via `gh issue view 71 --repo henols/firestarter` (read-only; **nothing was posted**).

| Field | Value |
|---|---|
| Title | `[dev test] MBM27128 — FAIL (1fa5c59c68b8)` |
| State | **OPEN** |
| Labels | **`dev-test`, `cause:firmware`, `cause:database`** |
| Author | `dim20` (Dimitris Roumeliotis) |
| Created | 2026-09-12T19:20:24Z |
| Comments | **3** — one from `dim20` (2026-09-12), **two from `henols` (2026-09-16)** |

**The report body** is an auto-generated `dev test` schema 2.0 report. Key measured values:
- `auto_capture`: `host_version: 3.0.0b39`, `fw_board_identity: 3.0.0b27:uno`, **`hw_revision: "Rev 2.0-class"`**, `protocol: "7"`, `chip_id_expected: null` (the `id` step is correctly NA).
- `write-partial` **BAD**, error 189: *"Byte at 0x003f01 failed to program within 25 pulses"*, `write_region_start: 16128`, `write_region_length: 256`, `write_bits_cleared: 128`, `write_bits_retained: 384`, `write_coverage: "slot 0x3F00 (256 bytes), 128 bits cleared this cycle; 63 of 64 slots left on this part"`.
- `verify` **BAD**, error 175: `0x02 != 0x03 at 0x003f01`.
- **`voltage`: `vpp_before_mv: 17800`, `vpp_after_mv: 17700`, `vpe_before_mv: 22700`, `vpe_after_mv: 22700`.**
- `rail_reading_disclosure`: *"vpp/vpe readings measure the regulator rail only -- they do not show whether the eprom socket is connected (advisory)"*.
- `db_diff.ladder_state: "community-fail"`, `dedup_fingerprint: "1fa5c59c68b8"`.

**`dim20`'s proposal (2026-09-12T21:35:59Z), the operative sentences verbatim:**

> *"**Programming Voltage (VPP):** The chip strictly requires 21.0V ± 0.5V to successfully program."*
> *"The test log shows the standard VPP rail only reached 17.8V (vpp_before_mv: 17800), which falls short of the 21.0V requirement. Since the board's standard VPP maxes out at ~18V, this can possibly be resolved by using the vpe as vpp option. The log shows the VPE rail has plenty of headroom (vpe_before_mv: 22700), so routing VPE to act as VPP should allow the hardware to hit the 21.0V target and program the chip."*

He also attached `Fujitsu-MBM27128-25-datasheet.pdf` and reported VCC 5.0 V ± 5 % conventional / **6.0 V ± 0.25 V Quick Pro**, pulse 50 ms conventional / **1 ms Quick Pro**, standard 28-pin DIP.

**Maintainer comment 1 (`henols`, 2026-09-16T12:08:29Z)** — a full datasheet cross-check table. Already published on the issue, so the draft must **not** re-announce any of it:
- The pin map, size, erase mode, chip-ID absence, algorithm, page size and write protection **all MATCH**.
- **`VPP (program)`: datasheet 21 V ± 0.5 V (20.5–21.5 V), abs max +22 V; database `vpp_mv: 18000` → "MISMATCH — 2.7 V below the datasheet minimum".**
- **`Pulse width`: 0.95/1.00/1.05 ms Quick Pro; database `pulse_duration_us: 200` → "MISMATCH — 5× short of even the Quick Pro minimum".**
- `VCC (program)`: 6 V ± 0.25 V Quick Pro; `vdd_mv: 5500` *"and never applied; the shield holds 5.0 V"* → MISMATCH.
- **The `0xF0`-is-a-cap explanation is already public**, including the quoted `build_db.py` comment, the `NMOS_TRUE_VPP_MV` gap, and the `AM27128A`/`0x5070` contrast.
- **On the VPE suggestion, already said:** *"The rail readings support it — 17.8 V on VPP against 22.7 V on VPE — and the datasheet's +22 V absolute maximum leaves room for a 21 V target."* With two cautions: the rail readings are **regulator** readings, not socket readings; and the firmware's VPP acceptance test *"only rejects a rail that is too high (`eprom.cpp`: `vpp_mv > handle->vpp_mv + 500`); the low side is a warning only, which is why an under-target rail programmed nothing and reported no voltage error."*
- Closing: *"Correcting `vpp_mv` to 21000 and `pulse_duration_us` to 1000 is a database change; being able to deliver 21 V to socket pin 1 is a firmware and hardware question that needs a bench answer, and is the reason this issue stays open rather than closing on the analysis."*

**Maintainer comment 2 (`henols`, 2026-09-16T20:41:12Z)** — the boundary hypothesis:
- *"**Not asking for a re-test here either**, for the same reason as #66 and #70."*
- The VCC gap is real and worth fixing, **but** *"this report's stop address argues it is not the cause here."* `0x003f01` is 255 bytes from the end of a 16 KB part; the two sibling Fujitsu reports stop **exactly 256 bytes from the end of their parts, which are 128 KB and 512 KB**. *"Three different sizes, the same position relative to the end."*
- *"In #66 the reporter also raised VPP into the datasheet window and reproduced the identical address across multiple physical chips, and six firmware versions changed nothing. Insufficient programming voltage does not fail that deterministically; a final-block handling defect does."*
- *"This stays open tracking that boundary alongside the VCC gap."*

**What D-19 therefore leaves the draft, and what it forbids — stated sharply:**

| The draft MAY claim | The draft MUST NOT claim |
|---|---|
| `MBM27128`'s `electrical.vpp_mv` is corrected 18000 → 21000, from the vendored `datasheets/MBM27128.pdf`, crediting `dim20` | Anything new about causation. The boundary hypothesis is the maintainer's standing position and this phase does not advance it. |
| **A direct answer to `dim20`'s VPE-as-VPP proposal: it is now automatic above the measured threshold** — the phase's one genuinely new fact | That the fix makes the part program. Nothing in this phase is bench-proven against a real `MBM27128`. |
| The measured deliverable maximum at socket pin 1 on both paths, Rev 2.0, with the method and the error, **once the bench has produced it** | Any figure the bench did not produce; and no re-announcement of the 21 V / 1 ms mismatches or the `0xF0` explanation — the maintainer published both on 2026-09-16. |
| That the issue stays open | That the issue can close. RAIL-05 is left **Pending**, exactly as PULSE-04 and VOLT-04 are. |

**The `**Version:**` line must carry the same held-pending placeholder the two sibling drafts use.** `firestarter_app` is still on `v1.40-program-parameter-fidelity` with a single untracked file and no upstream; nothing has been pushed.

---

## F. Cross-cutting

### F26. `tools/DECODE-NOTES.md` — the § 10 template

**MEASURED.** The file is **525 lines**; its top-level outline:

```
##  0. Pinned upstream reproducibility (the SHA this regen is grounded on)
##  1. LOW byte — `variant & 0xFF` (pinout-family sub-discriminator)
##  2. HIGH byte — `variant >> 8` … — NOT a classifier      (### 2.1, 2.2, 2.3)
##  3. build_db.py provenance decision (records, does not apply)
##  4. X88C64 fix rationale (`proto_id == 0x34` → `electrical.type = EEPROM`)
##  5. FM1608 identity (Phase 197 D-08 deleted the relabel — the row now reads SRAM)
##  6. Honest gaps (documented, never guessed — D-05)
##  7. Sources
##  8. `pulse_delay` unit finding (PULSE-01, Phase 197 — the decode rule survives)
##  9. The voltage word's two nibbles and VPP byte (VOLT-01, Phase 198 — …)
```

**So § 10 appends at the end of the file, after § 9.**

**The heading format**, from §§ 8 and 9 — a numbered `##`, the subject, then in parentheses the **requirement id, the phase number, and a one-clause verdict**:

```
## 9. The voltage word's two nibbles and VPP byte (VOLT-01, Phase 198 — the two nibbles and the VPP byte select a programmer rail index, not a chip requirement)
```

For 199 the parenthetical is `(RAIL-01/RAIL-02/RAIL-04, Phase 199 — …)`.

**The sub-structure of § 9, which § 10 should follow beat for beat:**

1. **`**Verdict: …**`** — an opening bolded sentence stating the finding, then a short paragraph saying which plans produced which piece of it.
2. **A sequence of bolded lead-in paragraphs**, each carrying one kind of evidence, each with a provenance marker. The measured set in § 9: `**What the decode does today**`, `**A falsified citation, found and corrected.**`, `**The twelve-row carve-out …**`, `**The positive confirmation.**`, `**The falsification of the rival reading …**`, `**The arithmetic argument — the sharpest single piece of evidence …**`, `**A second instance of the same pattern …**`, `**The edge case and dead branch (D-16).**`, `**The surviving silent fallback (D-03).**`
3. **`**The limits, named rather than hedged:**`** — a bulleted list. § 9's four bullets are the model: *"The datasheet corroboration is n = 3, and all three are Fujitsu"*; *"No claim is made about the 167 rows … this phase does not reach"* with a **Cross-reference:** to the owning phase; *"The finding does not assert that any particular row's emitted value is correct"*; and one naming a reading as *"this generator's own working reading, not upstream-attested."*
4. **A closing sentence naming which plans established which part.**
5. **`Sources: …`** — a semicolon-separated run of paths and `<file>#<lines> @ <sha>` citations.

**Provenance markers, exact form (MEASURED, verbatim from § 9):**

```
[VERIFIED: build_db.py, the `_d_vpp_mv` / `_d_vcc_mv` / `_d_vdd_mv` assignment immediately after `classify()` runs]
[VERIFIED: database.c#L161-L170 @ a8efaedc]
[VERIFIED: minipro <file>#<lines> @ a8efaedc — <array>[]]
[VERIFIED: minipro.h#L84-L85 @ a8efaedc]
```

Two forms: `<file>#<Lstart>-<Lend> @ <sha>` for a pinned external file, and a **content-addressed prose locator** for in-repo files that move (*"the assignment immediately after `classify()` runs"*). **Use the prose form for `build_db.py` and the firmware**, matching CONTEXT.md's "cited by content, not line number" instruction and the repository's line-citation-repair rule.

**§ 6 "Honest gaps" — the template for § 10's named limits.** Its two bullets are the shape: a bolded claim-sentence, then the evidence, then an explicit **"Cross-reference:"** naming whatever owns the gap. It also demonstrates the device of an `**[Plan NN-NN IMPLEMENTED]**` inline marker updating an older bullet in place rather than rewriting it — useful if § 10's Rev 2.2 / Modified Rev 0 gap is ever closed.

**What § 10 must contain, assembled from the D-decisions:**

- **The verdict:** `RURP_VPP_CEILING_MV = 25000` is a **regulator's theoretical figure**, kept as the refusal gate (D-01), and the deliverable maximum at the socket is a separate, measured, host-side number (D-02).
- **The measured figures**: DMM at socket pin 1, drop path and direct-VPE path, Rev 2.0, pot at maximum, chip out, with the `hold_rail.py` composites (`0x188` / `0x088`) named, and **the ADC pair with the discrepancy figure** — described as a *combined* ADC-plus-P1-path discrepancy, not a pure ADC calibration (see A5).
- **The 30-row classification table** (C13, re-measured post-D-17), with a reason per row and the 10/20 path split.
- **The D-06 approximation, stated as an approximation**: the 20 algorithm-`0x0B` rows are classified against a **pin-1** VPE figure taken through `CTRL_VPP_P1_ENABLE`, while they actually receive VPE through `CTRL_VPE_ENABLE` to pin 21 — **different physical destinations.**
- **The D-12 posture change**: `eprom_hv_route_mask`'s own documentation calls `FLAG_VPE_AS_VPP` *"a pure human override (25V NMOS parts, the manual-pot workflow) set by no database entry"*. After D-09 it is **also set by a host rule**. The flag's resolution order is unchanged — it still wins over the table with no table read — but that comment no longer describes the only caller. **Do not edit the comment** (no-comments rule); record the change here. **This is the reason D-03 exists**: `build_db.py` carries a `# RURP boost regulator theoretical ceiling…` comment directly above the constant, and editing it would emit a `+`-prefixed `#` line that trips the pre-commit check.
- **The named limits** (§ 6/§ 9 style): Rev 2.2 and Modified Rev 0 unmeasured (overlaps backlog **999.42**); Modified Rev 0 *cannot* contribute an ADC figure at all (`MSG_ERR_REV0_VPP_RD`, `MSG_WARN_REV0_VPP_UNSUPPORTED`); the pin-21 configuration not measured; the ADC/DMM pair is a combined discrepancy; the `firestarter vpp/vpe` wire resolution is a **100 mV grid**; 999.38's ~+7.5 % (6.8–8.3 %) is cited, not replaced, and its standing rule stands — **set any pot target from a multimeter reading, never from the firmware's own `vpp` figure**; the D-18 test mirrors a firmware table the host cannot read and therefore **detects database-side change only**; and the two `TEXAS INSTRUMENTS` rows carry a hardcoded `vpp_mv: 25000` from `extra_chips.json`, `UNVERIFIED` and not write-graduated.

### F27. Commit unit and branch state

**MEASURED this session:**

| Repo | Branch | Working tree |
|---|---|---|
| meta (`/workspaces`) | `v1.40-program-parameter-fidelity` | modified: `.devcontainer/devcontainer.json`, `.planning/graphs/*`, `.vscode/*`; untracked: `anything.txt`, `firestarter.wiki/`, `setup-claude-pr-policy.sh`, `tmp/` |
| `firestarter_app` | `v1.40-program-parameter-fidelity` | one untracked file: `datasheets/LST62832I.pdf` |
| `firestarter_fw` | `v1.40-program-parameter-fidelity` | **clean** |

**Both sub-repos are on the milestone branch, confirmed.**

**The commit unit is `firestarter_app`.** Every code, test, fixture and `tools/` change in this phase lands there. `firestarter_fw` is **read-only for this phase** — D-10 establishes the mechanism already ships; Phase 201 is the milestone's only firmware change. The meta repo carries `.planning/` (the bench record, the regen diff, the gh#71 draft, ROADMAP/REQUIREMENTS/STATE updates), and the **gitlink advances per phase** (v1.36 convention) so the meta-repo commit that closes the phase also bumps the `firestarter_app` submodule pointer.

**Two standing hazards the plan must respect:**
- **A push to `beta` in `firestarter_app` publishes to PyPI**, with no path filter — even a docs-only push. This phase's work stays on `v1.40-program-parameter-fidelity` and pushes nothing.
- **`tests/test_flash_path_record_sync` asserts repo porcelain** (project memory) — commit before running the full suite, or that leg reddens on unrelated dirt. The untracked `datasheets/LST62832I.pdf` in `firestarter_app` is exactly the kind of dirt that trips it; the plan should dispose of it (commit it or stash it) before a full-suite run rather than discovering it mid-verify.

### F28. The pre-commit comment check — and its one weakness

**The command, verbatim from CLAUDE.md** (`firestarter_app` is the Python side):

```bash
git -C firestarter_app diff --cached -- '*.py' | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!'
```

**MEASURED this session, on the current (empty) index:** zero staged files, no output, and the `test -z` form of the check **exits 0**.

**⚠️ This is the weakness the planner must design around: the check passes vacuously when nothing is staged.** A verify leg that runs it against an unstaged working tree proves nothing at all. Two fixes, both cheap:

1. **Stage first, then check.** The leg must run *after* `git add`, and should assert the staged set is non-empty in the same breath:
   ```bash
   cd /workspaces/firestarter_app && \
   N=$(git diff --cached --name-only -- '*.py' | wc -l) && test "$N" -gt 0 && \
   D=$(git diff --cached -- '*.py') && \
   OFFENDERS=$(printf '%s\n' "$D" | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!'); \
   printf '%s' "$OFFENDERS"; test -z "$OFFENDERS"
   ```
   **Failing direction:** non-zero exit either because no Python file is staged (the check would have been vacuous) **or** because offending lines were printed immediately above.
2. **Prove the check can fail** once, in the plan, with a positive control — pipe a synthetic `+# planted` line through the same two greps and confirm it is caught — rather than trusting a silent pass.

**The pathspec `-- '*.py'` is load-bearing** (CLAUDE.md says so explicitly): without it, each pattern also matches markdown, and the check reports a file it does not govern. Since this phase writes a large markdown section (§ 10) and three or four `.md` artifacts, dropping the pathspec would produce a flood of false positives.

**Devcontainer `grep` hazard, MEASURED as a project rule:** bare `grep` in this devcontainer is **ugrep**, and it **honours `.gitignore`** — it silently under-scans. **Use `/usr/bin/grep` everywhere**, in verify legs and in ad-hoc checks. Two related project-memory traps worth carrying into the plan: `grep -qF` with a dash-leading pattern exits 2 and the gate fails **open** (use `-qFe`), and `grep -c` in a gate is an open-failure idiom.

**Two further no-comment specifics for this phase:**
- `page_size_gate.py` **already contains** `#` comments (e.g. above `_ACCEPTED_PAGE_SIZES`). Those are pre-existing and untouched; the rule governs **added** lines (`^\+\s*#`). The new module must carry **zero** `#` lines — everything explanatory goes in the module docstring, which is permitted and is what all three precedents use.
- Click docstrings and module docstrings are **user-facing text / module documentation, not comments** (CLAUDE.md and project memory both say so). The new module's docstring, the new test module's `Coverage:` list, and any `"""..."""` on a function are all fine.

### F29. Proven verify-command idioms

**MEASURED** from `.planning/phases/198-the-two-voltage-nibbles/198-01-PLAN.md`'s `<automated>` blocks. Copy these verbatim — they are already known to run in this environment.

| Idiom | Form | Why it is used |
|---|---|---|
| **CI-replica interpreter** | `.venv/ci-replica/bin/python …` | Python **3.11.16** (MEASURED), matching CI. Bare `python3` is 3.12 in this devcontainer and has broken beta CI before. |
| **Sentinel assertion** | `… -c "…; print('FUJITSU_OK')" \| /usr/bin/grep -qx 'FUJITSU_OK'` | `-qx` requires the **whole line** to match, so partial output or a traceback cannot pass. The `assert` inside prints the offending values in the AssertionError, so a failure is self-describing. |
| **Branch guard** | `B=$(git rev-parse --abbrev-ref HEAD) && printf '%s\n' "$B" && test "$B" = 'v1.40-program-parameter-fidelity'` | Prints the branch **and** asserts it. `beta` in particular means the next push publishes to PyPI. |
| **Generator success** | `python tools/build_db.py 2>&1 \| tail -1 \| /usr/bin/grep -q '= 746 total\.'` | Asserts both a clean exit and the row count in one leg. |
| **Numstat** | `NS=$(git diff --numstat -- <path>) && printf '%s\n' "$NS" && printf '%s\n' "$NS" \| /usr/bin/grep -qP '^1\t1\t'` | The **single-line re-record** discipline (197-04 precedent). Prints the numstat before asserting, so a failure shows the real number. **`-P` for the literal tab.** For this phase the expected pattern is `^1\t1\t` (MEASURED, B11), not 198's `^2\t2\t`. |
| **Pytest, count-line visible** | `.venv/ci-replica/bin/python -m pytest <paths> -o addopts="" -q -p no:randomly 2>&1 \| tail -3 \| /usr/bin/grep -qE '^[0-9]+ passed'` | `-o addopts=""` defeats the `-ra -q` in `pyproject.toml` (a doubled `-q` hides the count line). `-p no:randomly` makes the run deterministic. |
| **Collection-count floor** | `test "$(… --collect-only 2>/dev/null \| /usr/bin/grep -c '::')" -ge N` | Proves a **new test was actually added**, not just that the module still passes. |
| **Fixture anti-laundering** | `git diff --quiet <sha> -- tests/golden/wire_dict_baseline.json tests/golden/wire_dict_expected_deltas_*.json` | Proves no prior golden or delta layer was re-captured to make this phase's change disappear. |
| **Source-shape assertion** | read the module with `pathlib.Path(...).read_text()`, assert named tests exist, assert exact `s.count(...)` for load-bearing assertion strings, and assert weakening idioms are **absent**: `for w in ('xfail', 'pytest.mark.skip', 'issubset'): assert w not in s` | Catches a later reader silently weakening the gate. Directly applicable to the D-18 test. |
| **Lint** | `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` | The exact CI scope. **`tools/` is deliberately excluded** — it sits outside every CI gate, which is D-18's stated reason the coverage must live in `tests/`. |

**One idiom to add that 198 did not have** — arming the comment check (F28).

---

## Sequencing constraints

**D-08 makes one edge a hard predecessor, and it changes the plan graph.**

```
                 ┌──────────────────────────────────────────────────┐
  PLAN A  ───►   │  BENCH SESSION (RAIL-01)                          │
  bench-gated    │  Rev 2.0, pot max, chip out                       │
  autonomous:    │  hold_rail.py 0x188 → DMM @ pin 1  = THRESHOLD    │
  false          │  hold_rail.py 0x088 → DMM @ pin 1  = VPE figure   │
                 │  firestarter vpp -t 1 / vpe -t 1   = ADC pair     │
                 │  → 199-BENCH-RECORD.md  (the number now EXISTS)   │
                 └────────────────┬─────────────────────────────────┘
                                  │  HARD PREDECESSOR (D-07, D-08)
                                  │  no plan may hardcode 18000 before this
                 ┌────────────────▼─────────────────────────────────┐
  PLAN C  ───►   │  HOST POLICY MODULE (RAIL-03, RAIL-04)            │
                 │  the gate module + its threshold constant         │
                 │  + write call site + info call site + its tests   │
                 └────────────────┬─────────────────────────────────┘
                                  │
  PLAN B  ───►   ┌────────────────┴─────────────────────────────────┐
  INDEPENDENT    │  DATABASE (RAIL-02 part 1)                        │
  of the bench   │  datasheet_overrides.json + regen + wire-delta     │
                 │  layer 199 + snapshot re-record + 199-REGEN-DIFF   │
                 └────────────────┬─────────────────────────────────┘
                                  │  (30-row counts move after this)
                 ┌────────────────▼─────────────────────────────────┐
  PLAN D  ───►   │  30-ROW CLASSIFICATION TEST (RAIL-02 part 2)      │
                 │  needs B's post-override counts                    │
                 └────────────────┬─────────────────────────────────┘
                                  │
                 ┌────────────────▼─────────────────────────────────┐
  PLAN E  ───►   │  § 10 in DECODE-NOTES.md  (needs A, B, C, D)      │
                 │  + 199-GH71-ANSWER.md + D-20 list update (RAIL-05)│
                 └──────────────────────────────────────────────────┘
```

**Stated as rules the planner must honour:**

1. **A → C is a hard edge.** The threshold constant cannot be written before the DMM reading exists. A host plan authored against `18000` up front makes **D-07 unobservable** — the whole point of D-07 is that the measurement wins outright if it disagrees with the operator's provisional 18 V. Where the host plan must refer to the number before it exists, it refers to it as **a placeholder the bench plan fills**, and the plan text must say so in those words.
2. **B is independent of A.** The `MBM27128` override rests on the vendored datasheet, not on any rail measurement. B can run first, in parallel, or on a non-bench day. Running B first is the better schedule: it de-risks the regeneration/wire-delta/snapshot work away from bench time.
3. **B → D is a hard edge.** The override moves `MBM27128` from the 18000 bucket to the 21000 bucket, so the exact voltage counts the test asserts differ before and after. Either sequence D after B, or have D assert the post-override counts and let it be red until B lands — the first is cleaner.
4. **A, B, C, D → E.** § 10 is the record of everything, and the gh#71 draft's one new claim ("automatic above the measured threshold") needs both the measured threshold **and** the shipped rule.
5. **The bench plan carries `autonomous: false`, and the phase must not be executed under `--auto` / `--chain`** — standing bench rule 7, and project memory records that `--auto` **auto-approves human-verify gates** and that `autonomous: false` is **not self-protecting** against it. This must be stated in the phase's execution note, not only in the plan frontmatter.
6. **Within the bench plan, the step order in A5 is itself a constraint**, not a suggestion: both hold windows close before any `firestarter` command runs, and the pot is set once and never touched again.

---

## Open questions for the planner

| # | Question | What would resolve it |
|---|---|---|
| 1 | **What is the measured drop-path maximum at socket pin 1?** Everything about the host threshold depends on it, and it does not exist. | The bench session (Plan A). **This is D-08 working as designed, not a research gap.** |
| 2 | **Is the operator's provisional 18 V within reach of the measurement?** If the DMM reads, say, 16.6 V, then even after D-17 the 10 drop-path rows at 18000 also fall short and all 30 rows warn — a wider blast radius for the § 10 table and for the warning's frequency than if the figure lands at ~18 V. | The bench session. The § 10 table should be authored **after** the number is known so its "reason" column is written once. |
| 3 | **Does `firestarter vpp -t 1` produce a stable enough figure to pair with the DMM?** The loop emits several frames per second on a 100 mV grid; if the last frame jitters, the pairing needs a stated rule (last frame? modal frame?). | One bench observation. Decide and record the rule in § 10's method, whichever it is. |
| 4 | **`logger.warning` vs `click.echo` on the `write` path.** Both are defensible; I recommend `click.echo` (D22) on the default-verbosity argument the source itself makes, but this is the planner's call and it affects which tests assert `result.output` vs `caplog`. | A one-line decision in the plan. |
| 5 | **Does the `info` warning move any `test_characterization.ambr` snapshot?** Insertion option (A) (CLI handler) should not, since `eprom_info.py` is untouched; option (B) (presenter) very likely does. I did not run a snapshot diff because doing so would write to the working tree. | Run `pytest tests/test_characterization.py -o addopts="" -q -p no:randomly` after the change and read `git diff --numstat`. Budget a snapshot leg if (B) is chosen. |
| 6 | **Should the new gate module join a mypy strict island?** The three precedents are not in one; `sdp_honesty` joined "from birth" as a deliberate strengthening. mypy is not a CI gate either way (C16). | A one-line decision. Note that if it joins, `pyproject.toml` moves, which is outside the six-deliverable shape. |
| 7 | **Does the 199 delta layer need `test_exactly_84_records_change_flags_and_no_other_field_moves` renamed?** The count stays 84 if 199 is composed in, but the test's name enumerates layers only implicitly. The module docstring's layer enumeration definitely moves. | Reading the test body when the task is written; the docstring's ten-item `Coverage:` list is the checklist. |
| 8 | **Disposition of `firestarter_app`'s untracked `datasheets/LST62832I.pdf`.** It predates this phase and is unrelated, but `test_flash_path_record_sync` asserts repo porcelain, so it can redden an unrelated verify leg. | Ask the operator, or stash it for the duration. Do not commit someone else's stray file as part of this phase. |
| 9 | **Is the pot restored before Phase 201?** CONTEXT.md defers this as operational. Phase 201 is also bench-gated and would inherit a pot at maximum. | A closing step in the bench plan, or an explicit recorded statement that it was left at maximum. |

---

## Verify command inventory

Every command below is copy-pasteable and was either run this session (marked **✅ run**) or is a direct adaptation of a proven Plan 198-01 leg (marked **↺ adapted**). **`/usr/bin/grep` throughout** — bare `grep` is ugrep here and honours `.gitignore`.

### Branch and repo state

```bash
# ✅ run — expect: v1.40-program-parameter-fidelity   (three times)
cd /workspaces && for R in . firestarter_app firestarter_fw; do git -C "$R" rev-parse --abbrev-ref HEAD; done
```
**Failure:** any line other than `v1.40-program-parameter-fidelity`. **`beta` is the dangerous one** — the next push there publishes to PyPI.

```bash
# ↺ adapted — the single-repo guard, prints then asserts
cd /workspaces/firestarter_app && B=$(git rev-parse --abbrev-ref HEAD) && printf '%s\n' "$B" && test "$B" = 'v1.40-program-parameter-fidelity'
```
**Failure:** non-zero exit.

### The override entry

```bash
# ↺ adapted — expect: OVERRIDES_199_OK
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -c "
import json
d = json.load(open('tools/datasheet_overrides.json'))
assert len(d) == 22, len(d)
assert list(d) == sorted(d), 'unsorted'
assert sum(1 for v in d.values() if v['datasheet'] == 'UNSOURCED') == 18
e = d['FUJITSU/MBM27128']
assert e['datasheet'] == 'datasheets/MBM27128.pdf', e['datasheet']
assert set(e['fields']) == {'programming.pulse_duration_us', 'electrical.vdd_mv', 'electrical.vpp_mv'}, sorted(e['fields'])
assert e['fields']['electrical.vpp_mv'] == {'was': 18000, 'is': 21000}, e['fields']['electrical.vpp_mv']
assert all(isinstance(p['was'], int) and isinstance(p['is'], int) for x in d.values() for p in x['fields'].values())
print('OVERRIDES_199_OK')" | /usr/bin/grep -qx 'OVERRIDES_199_OK'
```
**Failure:** output is not `OVERRIDES_199_OK`. The AssertionError names the leg — an entry count other than 22 means an entry was **added** when D-17 says a field was added to an existing one; an `UNSOURCED` count other than 18 means the same; a `fields` set with two or four keys means the new field was misplaced; a `was` other than 18000 means a stale override that `build_db.py` would refuse anyway.

```bash
# ✅ run form (datasheet existence) — expect: the file, non-zero size
cd /workspaces/firestarter_app && git ls-files --error-unmatch datasheets/MBM27128.pdf
```
**Failure:** non-zero exit — the citation names a path that is not git-tracked, which `_validate_datasheet_overrides_shape` also refuses.

### Regeneration

```bash
# ↺ adapted — expect: silent success
cd /workspaces/firestarter_app && python tools/build_db.py 2>&1 | tail -1 | /usr/bin/grep -q '= 746 total\.'
```
**Failure:** non-zero exit — either the generator raised (a stale `was`, a no-op pair, an unsorted file, an untracked datasheet path, or a network failure fetching the SHA-pinned `infoic.xml` all abort it), or its last stdout line does not report 746 total.

```bash
# ↺ adapted — expect: REGEN_199_OK
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -c "
import json, subprocess
base = json.loads(subprocess.run(['git','show','HEAD:firestarter/data/chip_database.json'],capture_output=True,text=True).stdout)
live = json.load(open('firestarter/data/chip_database.json'))
fb = {(m, r['part_number']): r for m, rs in base.items() for r in rs}
fa = {(m, r['part_number']): r for m, rs in live.items() for r in rs}
assert set(fa) == set(fb), sorted(set(fa) ^ set(fb))
assert len(fa) == 746, len(fa)
changed = [(k, sec, f, fb[k].get(sec,{}).get(f), fa[k].get(sec,{}).get(f))
           for k in fb for sec in set(fb[k]) | set(fa[k])
           if isinstance(fb[k].get(sec), dict) or isinstance(fa[k].get(sec), dict)
           for f in set(fb[k].get(sec,{})) | set(fa[k].get(sec,{}))
           if fb[k].get(sec,{}).get(f) != fa[k].get(sec,{}).get(f)]
assert changed == [(('FUJITSU','MBM27128'), 'electrical', 'vpp_mv', 18000, 21000)], changed
assert sorted(r.get('support_status') for r in fb.values()) == sorted(r.get('support_status') for r in fa.values())
print('REGEN_199_OK')" | /usr/bin/grep -qx 'REGEN_199_OK'
```
**Failure:** output is not `REGEN_199_OK` — a differing row-key set (a row added or removed), a row count other than 746, **any** changed field other than the single `MBM27128` `vpp_mv` move, or a changed `support_status` multiset (which would break D-01).

### The 30-row classification (post-override state)

```bash
# ✅ run (pre-override form) — post-override expect: {18000: 21, 21000: 3, 25000: 6}
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -c "
import json, collections
db = json.load(open('firestarter/data/chip_database.json'))
rows = [(m, r) for m, rs in db.items() for r in rs if r.get('electrical', {}).get('vpp_mv', 0) >= 18000]
PATH = {0x07: 'drop-resistor', 0x08: 'drop-resistor', 0x0B: 'direct-vpe'}
print('count', len(rows))
print('mv  ', dict(sorted(collections.Counter(r['electrical']['vpp_mv'] for _, r in rows).items())))
print('path', dict(sorted(collections.Counter(PATH.get(r['programming']['algorithm'],'?') for _, r in rows).items())))
print('stat', dict(collections.Counter(r.get('support_status') for _, r in rows)))"
```
**Pre-override MEASURED output:** `count 30` / `mv {18000: 22, 21000: 2, 25000: 6}` / `path {'direct-vpe': 20, 'drop-resistor': 10}` / `stat {'supported': 30}`.
**Failure:** any count other than 30, any `?` in the path histogram (an algorithm outside `{0x07, 0x08, 0x0B}` reached the ≥18000 set), or any `support_status` other than `supported` — the last would mean D-01 was violated somewhere.

### The wire-delta layer

```bash
# ↺ adapted — expect: LAYER_199_OK
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -c "
import json
d = json.load(open('tests/golden/wire_dict_expected_deltas_199.json'))
assert set(d) == {'deltas', 'meta'}, sorted(d)
assert set(d['meta']) == {'decision', 'honesty', 'how_to_update', 'phase', 'provenance'}, sorted(d['meta'])
assert all(isinstance(v, str) and v.strip() for v in d['meta'].values())
assert d['meta']['phase'] == '199-what-the-rails-can-actually-deliver', d['meta']['phase']
assert set(d['deltas']) == {'FUJITSU|MBM27128|2'}, sorted(d['deltas'])
assert d['deltas']['FUJITSU|MBM27128|2'] == {'vpp_mv': 21000}, d['deltas']
g = json.load(open('tests/golden/wire_dict_baseline.json'))['records']
assert g['FUJITSU|MBM27128|2']['vpp_mv'] == 18000, g['FUJITSU|MBM27128|2']['vpp_mv']
d197 = json.load(open('tests/golden/wire_dict_expected_deltas_197.json'))['deltas']
assert set(d197['FUJITSU|MBM27128|2']) & set(d['deltas']['FUJITSU|MBM27128|2']) == set(), 'layer 197/199 field collision'
print('LAYER_199_OK')" | /usr/bin/grep -qx 'LAYER_199_OK'
```
**Failure:** output is not `LAYER_199_OK` — a top-level key set other than the two, a `meta` block missing one of the five anti-laundering keys or carrying an empty string, a delta key set other than the one measured record, a payload field other than `vpp_mv`, a golden value other than the measured pre-phase 18000 (meaning the golden moved, or the layer records something the golden already carries and therefore proves nothing), or a **field collision with the 197 layer on the shared key**, which would break `dict.update` order-independence.

```bash
# ↺ adapted — replace <PRE-PHASE-SHA> with the firestarter_app sha at phase start (f155364 today)
cd /workspaces/firestarter_app && git diff --quiet <PRE-PHASE-SHA> -- \
  tests/golden/wire_dict_baseline.json \
  tests/golden/wire_dict_expected_deltas_149.json tests/golden/wire_dict_expected_deltas_153.json \
  tests/golden/wire_dict_expected_deltas_182.json tests/golden/wire_dict_expected_deltas_194.json \
  tests/golden/wire_dict_expected_deltas_197.json tests/golden/wire_dict_expected_deltas_198.json
```
**Failure:** non-zero exit — the golden baseline or one of the six prior delta layers moved, meaning a fixture was re-captured to make this phase's change disappear.

```bash
# ↺ adapted
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/test_wire_dict_equivalence.py -o addopts="" -q -p no:randomly -rf 2>&1 | tail -3 | /usr/bin/grep -qE '^[0-9]+ passed'
```
**Failure:** any failure reported, or no `N passed` line — the composition test failing means the live capture and the composed expectation still disagree; the count test failing means composing the 199 layer did not return the changed-record count to 84.

```bash
# ↺ adapted — MEASURED this session: the module collects exactly 10 node ids today, so 11 is the post-task floor
cd /workspaces/firestarter_app && test "$(.venv/ci-replica/bin/python -m pytest tests/test_wire_dict_equivalence.py -o addopts="" -q -p no:randomly --collect-only 2>/dev/null | /usr/bin/grep -c '::')" -ge 11
```
**Failure:** fewer than 11 node ids — the new `test_the_199_delta_layer_is_capable_of_failing` was not added.

### The characterization snapshot

```bash
# ↺ adapted from the 197-04 single-line precedent — expect `1  1`
cd /workspaces/firestarter_app && \
.venv/ci-replica/bin/python -m pytest "tests/test_characterization.py::test_list" -o addopts="" -q -p no:randomly --snapshot-update >/dev/null 2>&1; \
NS=$(git diff --numstat -- tests/__snapshots__/test_characterization.ambr) && printf '%s\n' "$NS" && printf '%s\n' "$NS" | /usr/bin/grep -qP '^1\t1\t'
```
**Failure:** `--numstat` reports anything other than exactly 1 insertion and 1 deletion. **Zero lines** means the snapshot did not need re-recording, i.e. the rendered voltage never moved and the override did not reach the display path. **More than one line-pair** means a blanket update swept in unrelated drift.

```bash
# ✅ run — the pre-change ground truth this expectation rests on: exactly one occurrence
cd /workspaces/firestarter_app && test "$(/usr/bin/grep -c 'MBM27128' tests/__snapshots__/test_characterization.ambr)" -eq 1 && /usr/bin/grep -n 'MBM27128' tests/__snapshots__/test_characterization.ambr
```
**MEASURED output:** `757:  | MBM27128            | FUJITSU          |   28 |            | UV-EPROM    | 18.0v|`
**Failure:** a count other than 1 — the single-line assumption no longer holds and the numstat expectation must be re-derived.

### The policy module and its call sites

```bash
# the module carries ZERO shipped part numbers (the flash4_erase_gate discipline)
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -c "
import json, pathlib
src = pathlib.Path('firestarter/<MODULE>.py').read_text(encoding='utf-8')
db = json.load(open('firestarter/data/chip_database.json'))
names = {a.strip() for m, rs in db.items() for r in rs for a in r['part_number'].split(',') if len(a.strip()) >= 4}
hits = sorted(n for n in names if n in src)
assert not hits, hits
print('NO_PART_LITERALS')" | /usr/bin/grep -qx 'NO_PART_LITERALS'
```
**Failure:** output is not `NO_PART_LITERALS` — the AssertionError lists every shipped part number occurring in the module source, docstrings included; the policy must be database-derived, never a hand-kept list.

```bash
# the module contains NO '#' comment lines at all (CLAUDE.md hard rule, checked on the file not the diff)
cd /workspaces/firestarter_app && ! /usr/bin/grep -nE '^\s*#' firestarter/<MODULE>.py
```
**Failure:** non-zero exit with the offending lines printed — a `#` line exists anywhere in the new module. (A shebang would also trip this; the module must not have one.)

```bash
# the derived flag genuinely reaches build_flags — proves FLAG_VPE_AS_VPP (0x10) is set
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -c "
from firestarter.eprom_operations import build_flags
from firestarter.constants import FLAG_VPE_AS_VPP
assert FLAG_VPE_AS_VPP == 0x10, hex(FLAG_VPE_AS_VPP)
assert build_flags(vpe_as_vpp=True) & FLAG_VPE_AS_VPP
assert not (build_flags(vpe_as_vpp=False) & FLAG_VPE_AS_VPP)
print('FLAG_OK')" | /usr/bin/grep -qx 'FLAG_OK'
```
**Failure:** output is not `FLAG_OK` — the flag constant moved off `0x10` (host/firmware parity break) or `build_flags` stopped mapping it.

```bash
# --vpe-as-vpp still exists on write and on no other command (D-11)
cd /workspaces/firestarter_app && test "$(/usr/bin/grep -c -- '--vpe-as-vpp' firestarter/cli_handlers.py)" -eq 1
```
**Failure:** a count other than 1 — the option was added to a second command, or removed. (**MEASURED today: exactly 1**, at the `write` command's `@click.option`.)

### The 30-row classification test

```bash
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/<NEW_TEST>.py -o addopts="" -q -p no:randomly 2>&1 | tail -3 | /usr/bin/grep -qE '^[0-9]+ passed'
```
**Failure:** any failure reported, or no `N passed` line.

```bash
# the test does not weaken itself, and does not scan firmware source
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -c "
import pathlib
s = pathlib.Path('tests/<NEW_TEST>.py').read_text(encoding='utf-8')
for w in ('xfail', 'pytest.mark.skip', 'issubset', '>=', 'firestarter_fw'):
    assert w not in s, w
print('TEST_SHAPE_OK')" | /usr/bin/grep -qx 'TEST_SHAPE_OK'
```
**Failure:** output is not `TEST_SHAPE_OK` — the AssertionError names the weakening idiom found (`>=` would turn an exact count into a floor) or, critically, `firestarter_fw`, which would mean the test reaches into a repo that is **not present in app CI** and would fail open there.

### CI gates

```bash
# ↺ adapted — the exact CI lint scope
cd /workspaces/firestarter_app && ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/
```
**Failure:** non-zero exit — a lint error or an unformatted file under the two directories CI actually gates. `tools/` is deliberately out of scope (it is outside every CI gate, which is why D-18 puts the coverage in `tests/`).

```bash
# ↺ adapted — the CI pytest step, on the CI interpreter
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70 -o addopts="" -q 2>&1 | tail -5
```
**Failure:** any failure, or a coverage line below 70 %. Run this on a **clean** working tree — `tests/test_flash_path_record_sync` asserts repo porcelain and reddens on unrelated untracked files.

```bash
# ✅ run — the CI interpreter is 3.11, the devcontainer default is 3.12
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -V | /usr/bin/grep -q '^Python 3\.11\.'
```
**MEASURED:** `Python 3.11.16`. **Failure:** non-zero exit — the replica venv drifted off the CI floor, and every other leg's result becomes untrustworthy.

### The no-comments rule (armed, per F28)

```bash
# RUN THIS AFTER `git add`, NOT BEFORE — the unarmed form passes vacuously (MEASURED: rc=0 on an empty index)
cd /workspaces/firestarter_app && \
N=$(git diff --cached --name-only -- '*.py' | wc -l) && test "$N" -gt 0 && \
D=$(git diff --cached -- '*.py') && \
OFFENDERS=$(printf '%s\n' "$D" | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!'); \
printf '%s' "$OFFENDERS"; test -z "$OFFENDERS"
```
**Failure, two distinct directions:** (a) non-zero from `test "$N" -gt 0` — **no Python file is staged, so the check would have proved nothing**; (b) non-zero from `test -z "$OFFENDERS"`, with the offending lines printed immediately above — a comment line was added to a staged Python file. **The `-- '*.py'` pathspec is load-bearing**: without it the pattern also matches this phase's markdown artifacts and reports files the rule does not govern.

```bash
# positive control — prove the check can fail. expect: PLANTED CAUGHT
printf '%s\n' '+# planted comment' '+#!/usr/bin/env python' '+code = 1' | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!' | /usr/bin/grep -q 'planted comment' && echo 'PLANTED CAUGHT'
```
**Failure:** no `PLANTED CAUGHT` — the grep pair itself is broken and every green run of the real check is meaningless.

### gh#71 (read-only)

```bash
# ✅ run — expect: OPEN, 3 comments, labels dev-test / cause:firmware / cause:database
cd /workspaces && XDG_CACHE_HOME="${TMPDIR:-/tmp}/ghcache" gh issue view 71 --repo henols/firestarter \
  --json state,labels,comments --jq '{state, labels: [.labels[].name], comments: (.comments|length), authors: [.comments[].author.login]}'
```
**MEASURED:** `state: OPEN`, `labels: [dev-test, cause:firmware, cause:database]`, `comments: 3`, `authors: [dim20, henols, henols]`.
**Failure:** a different state (someone closed it), a different comment count (**something was posted** — the draft's "what is held" claim would be stale), or different labels.
**`XDG_CACHE_HOME` is required** — `~/.cache/gh` is unwritable in this devcontainer and `gh` fails without it.
**⚠️ Read-only. Nothing in this phase posts to GitHub; the draft is held per D-19.**

---

## Assumptions log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The post-D-17 voltage histogram becomes `{18000: 21, 21000: 3, 25000: 6}` | C14 | INFERRED from the measured override semantics (one row moves buckets). If the regeneration disagrees, the D-18 test's literals are wrong and it goes red — a loud, cheap failure, not a silent one. The regen verify leg catches it first. |
| A2 | Configuration (b) (`0x088`) is what VPE-as-VPP actually delivers to a 28-pin part | A3 | INFERRED by composing two measured facts: `eprom_hv_route_mask` returns `CTRL_VPP_REGULATOR_ENABLE` alone under `FLAG_VPE_AS_VPP`, and `eprom_internal_set_control_register` substitutes P1 for VPE when `using_p1_as_vpp` holds. Not observed on a scope. If wrong, the bench measures a rail the write path does not produce. A native trace or an operator continuity check on pin 1 would confirm. |
| A3 | `firestarter vpp -t 1` yields a usable settled figure | A4 | The `-t` option is `hidden=True` and the timeout is checked only after a DATA frame, so a very short window could return after one frame or several. Bench-observable in seconds; open question 3. |
| A4 | The `info` insertion at option (A) moves no snapshot | D20 | Not measured — measuring it would have written to the working tree. Open question 5; a `--numstat` check after the change settles it. |
| A5 | `-p no:randomly` is available in the CI environment as well as the replica | C15 | Verified in `.venv/ci-replica` this session; CI's own pytest step does **not** pass it, so this only affects local verify legs, not CI. |

---

## Sources

**Primary (HIGH confidence — read or executed this session):**
- `.planning/phases/199-what-the-rails-can-actually-deliver/199-CONTEXT.md` (full)
- `.planning/REQUIREMENTS.md` RAIL-01…05; `.planning/ROADMAP.md` v1.40 block + Phase 199 block
- `.planning/milestones/v1.18-artifacts/bench/hold_rail.py` (full)
- `.planning/milestones/v1.34-artifacts/PROCEDURE.md` § "Standing bench rules" (full)
- `.planning/phases/197-…/197-REGEN-DIFF.md`, `197-GH70-ANSWER.md` (both full); `.planning/phases/198-…/198-GH66-ANSWER.md` (outline), `198-01-PLAN.md` `<automated>` blocks
- `firestarter_fw`: `include/rurp_pinout.h`, `include/memory_utils.h`, `include/rurp_shield.h` (VPP_* constants), `src/proms/eprom.cpp` (`eprom_hv_route_mask`, `eprom_internal_set_control_register`, `eprom_check_vpp`, `eprom_internal_erase`), `src/proms/eprom_params.cpp`, `src/hardware_operations.cpp` (`hw_read_voltage`)
- `firestarter_app`: `tools/build_db.py`, `tools/datasheet_overrides.json`, `tools/DECODE-NOTES.md`, `firestarter/{jp5_gate,page_size_gate,flash4_erase_gate,cli_handlers,eprom_operations,eprom_info,hardware,serial_comm,constants}.py`, `tests/{test_flash4_erase_gate,test_wire_dict_equivalence,conftest}.py`, `tests/golden/{wire_dict_baseline,wire_dict_expected_deltas_197,wire_dict_expected_deltas_198}.json`, `tests/__snapshots__/test_characterization.ambr`, `pyproject.toml`, `.github/workflows/ci.yml`
- Live `firestarter/data/chip_database.json` via `python3 -c` (30-row census, wire-dict shapes)
- gh#71 via `gh issue view 71 --repo henols/firestarter` (read-only)
- `/workspaces/CLAUDE.md`

**Secondary (MEDIUM):**
- Project memory (`~/.claude/projects/-workspaces/memory/MEMORY.md`) for the ugrep, py3.12-masks-CI, `--auto`-auto-approves, porcelain-assertion and firmware-source-scanning hazards — each corroborated against a measured file where it mattered.

**Not consulted:** `STATE.md` (size guardrail), the full `ROADMAP.md` (size guardrail), `.planning/notes/197-at28c-guard-evidence-for-phase-199.md` beyond confirming its existence (its subject is **ruled out** of this phase).

---

## Metadata

**Confidence breakdown:**
- **Bench mechanics (A):** HIGH — `hold_rail.py`, the CTRL bits, the route resolver and the DTR mechanism were all read in source this session, and the `0x188`/`0x088` composites reconcile independently against `eprom_hv_route_mask` + `using_p1_as_vpp`.
- **Database change (B):** HIGH — every schema constraint, the allowlist membership, the live `was` value, the wire-delta key and the snapshot line count were measured, not assumed.
- **Classification test (C):** HIGH for the 30-row census and for the decisive negative finding (no `vpp_path` on the host, zero matches). MEDIUM for the post-override counts, which are inferred and will be confirmed by the regeneration.
- **Policy module (D):** HIGH — all three precedents read in full, both call sites traced end to end, both wire dicts measured identical.
- **gh#71 (E):** HIGH — fetched read-only this session; the full comment thread is reproduced above.
- **Cross-cutting (F):** HIGH — the CI file, the interpreter versions, the branch state and the comment check's vacuous-pass behaviour were all executed.

**The one thing this research deliberately does not provide:** the measured deliverable maximum. D-07/D-08 make that the bench session's output, and providing a placeholder value here would be the exact failure those decisions exist to prevent.

**Research date:** 2026-09-18
**Valid until:** ~2026-10-18 for the repository facts (stable, internal); **immediately invalidated** for gh#71's comment state by any new comment on the issue, and for the branch facts by any push.

---
*Phase: 199-what-the-rails-can-actually-deliver*
*Researched: 2026-09-18*
