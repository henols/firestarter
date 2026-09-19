# Phase 199 — Bench record: what the rails can actually deliver

**Measured:** 2026-09-19, against meta-repo `90f8812c` on branch `v1.40-program-parameter-fidelity`.

This record holds the figures Phase 199 ships. Per D-07 the figure in Task 2 Window A becomes the
shipped threshold and cannot be re-derived without another attended bench session.

## Session setup

**Serial port identity — probed in this session, not inherited.**
Standing bench rule 1: `/dev/ttyACM*` numbering shuffles across replug, so the port is re-probed
per task rather than carried over from any earlier session or cell.

| Field | Value | How obtained |
|---|---|---|
| Device path | `/dev/ttyACM0` | only `/dev/ttyACM*` present; no `/dev/ttyUSB*` |
| Controller | `leonardo` | `firestarter -p /dev/ttyACM0 fw` |
| Firmware version | `3.0.0b31` | same invocation |
| Firmware-reported hardware | `Rev 2.0-class, Override HW: Rev 2.0-class` | `firestarter -p /dev/ttyACM0 hw` |

**The firmware-reported hardware line above is NOT evidence of the revision** and no fact in this
record is inferred from it. Standing bench rule 6: `hw_revision` cannot distinguish Rev 2.0 from
Rev 2.2 from the modified Rev 0 — they share a resistor band. It is recorded only so that a later
reader can see it agreed with the operator rather than wondering whether it was consulted.

A firmware update to `3.0.0b33` was offered by the `fw` probe and **declined**. Nothing was
flashed in this session. (That release was cut carrying zero assets and the upload cannot be re-run,
so accepting it would not have succeeded in any case.)

### Operator statements

Claude cannot verify any of the three facts below. Each is recorded verbatim as the operator's
statement, not as a measurement.

- **Shield revision (silkscreen):** *Rev 2.0*, with the controller reported as a Leonardo.
  Operator statement, 2026-09-19. D-04 scopes this session to Rev 2.0 only; a different revision
  stops the plan and re-scopes the phase rather than substituting a board.
- **Chip out of socket:** *"chip out"*. Operator statement, 2026-09-19. D-05 requires it: the
  rails are held with nothing in the socket to receive them. It stays out for the whole session.
- **Pot at maximum:** *"pot to max"*. Operator statement, 2026-09-19. Claude stated the target as
  maximum; the operator set it and is the authority on where it landed. Per standing bench rule 4
  Claude took no monitor loop, and per the standing rule recorded at ROADMAP "Phase 999.38" the
  operator's own meter — never the firmware's `vpp` figure — adjudicates the pot. **From this point
  the pot is not touched again for the rest of the session**, because every figure in this plan must
  be at one pot setting or the Task 3 pairing is meaningless.

## Task 2 — The two hold windows

**BLOCKED. No meter reading was taken, and none is recorded. The rails were never energized.**

Nothing in this section is a measurement. It is the record of why the plan's method does not work
on this rig, so that a later attempt does not repeat it.

### What was attempted

| # | Invocation | Hold | Outcome |
|---|---|---|---|
| A1 | `python3 .planning/milestones/v1.18-artifacts/bench/hold_rail.py 0x188 300` | 300 s | Window lapsed before the operator reached it. **No reading taken.** Not a discarded reading — no reading exists. |
| A2 | `python3 .planning/milestones/v1.18-artifacts/bench/hold_rail.py 0x188 1800` | 1800 s | Operator reports no voltage at socket pin 1 and **no LEDs lit**. Rail not energized. |
| A3 | `python3 .planning/milestones/v1.18-artifacts/bench/hold_rail.py 0x188 1800` | 1800 s | Re-run after reflashing with `-D DEV_TOOLS=1`. Operator again reports **no LEDs lit**. Rail not energized. |

Window B (`0x088`) was never opened: Window A never produced a rail, so opening B would have
measured the same nothing. **The D-06 pin-21 configuration was likewise not measured**, which is
the deliberate non-measurement the plan called for — but it is recorded here alongside two further
non-measurements that were NOT deliberate, and plan `199-05` must not conflate them.

No `firestarter` command ran inside any window. The pot was not moved at any point after Task 1.

### Fault 1 — `hold_rail.py` reports success against a command the firmware does not have

`hold_rail.py` prints `>>> RAIL HELD: CTRL=0x188 payload=00008188 (4 bytes sent)` **whether or not
the firmware accepted the command.** It calls `comm.send_bytes()` and never calls `expect_ack()`, so
it cannot observe a refusal. Traced with `firestarter -v dev reg 0 0 0x188 -f` against the shipped
firmware `3.0.0b31`:

```
INFO :EpromOperator: Setting registers: MSB: 0x00, LSB: 0x00, CTRL: 0x188
DEBUG:SerialComm   : Sent 2 bytes   (the "OK" ack)
DEBUG:SerialComm   : Sent 4 bytes   (the payload)
ERROR:RURP         : ERROR: Unknown command: 8
```

`CMD_DEV_REGISTER` is `8`, and `firestarter_fw/include/firestarter.h` defines it inside
`#if DEV_TOOLS`. `-D DEV_TOOLS=1` appears in `platformio.ini` **only under `[env:native]`** — not
under `[env:leonardo]`, `[env:uno]` or `[env:uno328pb]`. **No shipped AVR firmware implements
command 8**, so `firestarter dev reg`, `firestarter dev addr` and `hold_rail.py` cannot work on any
released build. Historically `-D DEV_TOOLS` sat in the shared `[env]` block (firmware commit
`2678306`), which is why this method worked at the v1.14 and v1.18 benches and silently stopped.

`firestarter dev reg` **exits 0** on this path despite printing `ERROR: Unknown command: 8`.

### Fault 2 — `dt_set_registers` cannot complete, even under `-D DEV_TOOLS=1`

`[env:leonardo]` was rebuilt with `-D DEV_TOOLS=1` and flashed to the attached board (24898 B of the
28672 B safe ceiling, 86.8 %, bootloader-guard passed, avrdude verified). The firmware error then
changed from `Unknown command: 8` to `Command 8 timed out` — the command is now dispatched, but it
never completes, and **no `MSB`/`LSB`/`CTRL` decode line is ever returned**, so the handler never
reaches its register writes.

`firestarter_fw/src/dev_tools.cpp` `dt_set_registers()` opens:

```c
if (op_get_message(handle) != OP_MSG_ACK) { return false; }
if (rurp_communication_available() < 4)   { return false; }
```

The host sends the ack and the payload as **two separate writes**. `op_get_message()` returns
`OP_MSG_ACK` the moment it consumes `OK`; if the 4 payload bytes have not yet arrived, the second
guard returns `false`. The dispatcher re-enters the handler — but the ack has already been consumed,
so `op_get_message()` now runs over the payload `00 00 81 88`, and **every one of those bytes falls
to the `default:` arm of its switch and is read and discarded as junk**
(`firestarter_fw/src/operation_utils.cpp`). The payload is destroyed, the handler spins, and the
firmware's own timeout fires. The handler is not re-entrant across its own early return.

This is a latent defect in code that **no CI leg exercises on hardware and no release ships**:
`dev_tools.cpp` compiles only under `DEV_TOOLS`, which only `[env:native]` sets.

### Rig state left by this session

The attached board no longer runs shipped firmware. It carries a **locally built `[env:leonardo]`
image with `-D DEV_TOOLS=1`, which self-reports as `3.0.0b33` and is NOT the released `3.0.0b33`.**
The port re-enumerated from `/dev/ttyACM0` to `/dev/ttyACM1` during the session; identity was
re-probed on the new node (`leonardo`, `3.0.0b33`) per standing bench rule 1.

### Consequence for this phase

D-07 makes the Window A figure load-bearing: it is the shipped threshold and cannot be derived
without an attended bench session. No figure exists. **`199-03` cannot fill
`DELIVERABLE_MAX_DROP_PATH_MV` from this record**, and `199-05` cannot claim a measured threshold.

## Task 3 — Paired ADC reads and the error figures

**Not started.** Its precondition is that both Task 2 hold windows closed with readings recorded.
Neither window produced a rail, so the pairing Task 3 exists to compute has nothing to pair.
