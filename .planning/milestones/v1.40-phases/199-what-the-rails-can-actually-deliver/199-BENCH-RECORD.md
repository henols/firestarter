# Phase 199 — Bench record: what the rails can actually deliver

**Measured:** 2026-09-19, against meta-repo `90f8812c` on branch `v1.40-program-parameter-fidelity`.

This record holds the figures Phase 199 ships. Per D-07 the figure in Task 2 Window A becomes the
shipped threshold and cannot be re-derived without another attended bench session.

## Measured figures

Plans `199-03` and `199-05` parse these four lines. Each is a bare integer count of millivolts.
Read the integer from here; do not re-transcribe it from prose elsewhere in this file.

```
DELIVERABLE_MAX_DROP_PATH_MV = 17380
DELIVERABLE_MAX_DIRECT_VPE_MV = 22140
ADC_PAIRED_DROP_MV = 18700
ADC_PAIRED_DIRECT_MV = 23900
```

The first two are operator meter readings at socket pin 1. The second two are the firmware's own
monitor readings. They are not the same measurement and must not be substituted for one another —
see "Limits" below.

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

**Window A MEASURED after a firmware fix. Window B pending.** The three attempts below produced no
rail and no reading; they are kept because they are why the method had to change, not as
measurements. Read the "Fault 1"/"Fault 2" subsections before trusting any invocation in this file.

### Window A — drop-resistor path to socket pin 1 (`0x188`) — THE THRESHOLD FIGURE

| Field | Value |
|---|---|
| Operator's meter reading, verbatim | **`17.38v`** |
| Millivolt conversion (exact decimal shift, not rounded) | **`17380`** |
| `DELIVERABLE_MAX_DROP_PATH_MV` | **`17380`** |
| Composite | `0x188` = `0x080` REGULATOR + `0x100` VPE-DROP + `0x008` P1 |
| Measurement point | socket pin 1 against board ground |
| Rig | Rev 2.0 silkscreen (operator), socket empty, pot at maximum and untouched since Task 1 |

**The invocation that produced this figure was NOT `hold_rail.py`.** It was:

```
firestarter -v -p /dev/ttyACM0 dev reg 0 0 0x188 -f
```

with the rail held by the firmware's own `while (!rurp_user_button_pressed()) delay(200);` loop at
the tail of `dt_set_registers()` — the host had already disconnected. The board answers no serial
traffic while in that loop, which is how the hold was confirmed to be real: a probe and a
`hold_rail.py 0x188` invocation both timed out against it, and the operator then reported the
reading off a live rail. **No `firestarter` command ran while the rail was held**; the two timed-out
attempts happened before the reading and could not have opened the port. The pot was not moved.

This differs from the plan's prescribed method, which assumed `hold_rail.py 0x188` would hold the
rail. It does not on this rig — see Fault 1 and Fault 2. A reader must not read the
`hold_rail.py 0x188` string elsewhere in this file as the provenance of `17380`.

### Window B — direct VPE path to socket pin 1 (`0x088`)

| Field | Value |
|---|---|
| Operator's meter reading, verbatim | **`22.14v`** |
| Millivolt conversion (exact decimal shift, not rounded) | **`22140`** |
| Composite | `0x088` = `0x080` REGULATOR + `0x008` P1, drop bit CLEAR |
| Measurement point | socket pin 1 against board ground, same pin as Window A |
| Rig | same session, pot NOT moved between Window A and Window B |

Invocation, held by the same firmware button-wait as Window A:

```
firestarter -v -p /dev/ttyACM0 dev reg 0 0 0x088 -f
```

Firmware answered `OK: Ready` and the host disconnected before the reading. No `firestarter`
command ran while the rail was held.

### The pair

| Path | Composite | Delivered at socket pin 1 |
|---|---|---|
| Drop-resistor (standard VPP) | `0x188` | **17380 mV** |
| Direct VPE (VPE-as-VPP) | `0x088` | **22140 mV** |

Both at one pot setting, pot at maximum, socket empty, Rev 2.0 by operator silkscreen statement.

**What the pair supports, stated no further than it goes.** Against the 30-row census measured in
plan `199-04` (30 rows at or above 18000 mV; 10 on algorithm `0x07`, 20 on `0x0B`):

- The drop-resistor path at 17380 mV reaches **none** of the 30. The nine `0x07` rows at 18000 miss
  by 620 mV; the one `0x07` row at 21000 (`FUJITSU/MBM27128`, the gh#71 part) misses by 3620 mV.
- The direct-VPE path at 22140 mV covers **all ten** `0x07` rows, the worst by 1140 mV of margin.

**What the pair does NOT support.** The 20 algorithm `0x0B` rows — which include all six rows at
25000 mV — receive VPE through `CTRL_VPE_ENABLE` to **pin 21**, and per D-06 that configuration was
deliberately NOT measured in this session. Neither figure above is evidence about those rows. In
particular, nothing here licenses the inference that the six 25000 mV rows are out of reach: 22140
is a pin-1 figure on a path those rows do not use. Plan `199-05` owes its reader that approximation
disclosure explicitly.

### Attempts that produced no rail and no reading


Nothing in this subsection is a measurement.

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
under `[env:leonardo]`, `[env:uno]` or `[env:uno328pb]`. This session concluded from that reading
alone that **no shipped AVR firmware implements command 8**.

**Correction, 2026-09-19 (quick task `260919-cli`): that conclusion is false, and the falsification
is the finding.** `.github/workflows/beta-build.yml`'s "Build PlatformIO Project" step sets
`PLATFORMIO_BUILD_FLAGS: -D DEV_TOOLS=1` for its `pio run` — a per-channel injection added in
firmware commit `e6888a9` ("build: make dev tools a per-channel decision, off by default") and
invisible to a reading of `platformio.ini` alone. The three published `3.0.0b31` AVR release
assets were downloaded, decoded from Intel HEX, and searched for `CTRL remapped` (a string literal
that exists only in `dev_tools.cpp`) on 2026-09-19: `firestarter_uno.hex`, `firestarter_uno328pb.hex`
and `firestarter_leonardo.hex` all contain it. **The published beta channel does implement command
8.** Historically `-D DEV_TOOLS` sat in the shared `[env]` block (firmware commit `2678306`), which
is why this method worked at the v1.14 and v1.18 benches — it did not silently stop working, as
this record originally concluded; `e6888a9` moved the flag from the shared block to the beta
publisher alone, and the shipped beta artifact still carries it.

These two facts do not reconcile on their own: the board in this session, reporting itself as
`3.0.0b31`, refused command 8 with `ERROR: Unknown command: 8` below; the published `3.0.0b31`
release assets implement that command. The most likely explanation is that the attached board was
running a locally built image rather than the actual published `3.0.0b31` asset — but that
explanation is an **inference, not a measurement**: no image was pulled off the board and compared
byte-for-byte against the release asset. The "Rig state left by this session" paragraph below
records exactly that hazard for the image this session left behind (a locally built
`-D DEV_TOOLS=1` image that self-reports as `3.0.0b33` and is not the released `3.0.0b33`), which
is consistent with the same hazard having already been present, unnoticed, at the session's start.
Full evidence: `.planning/quick/260919-cli-beta-build-ships-dev-tools-so-dev-reg-an/260919-cli-EVIDENCE.md`.

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

This is a latent defect in code that **no CI leg exercises on hardware**. It does ship: per the
correction above, the published beta channel builds `dev_tools.cpp` under `-D DEV_TOOLS=1`
(`beta-build.yml`'s `PLATFORMIO_BUILD_FLAGS` injection), so every published pre-release through
`3.0.0b33` carries this re-entrancy defect uncorrected, and `firestarter dev reg` against any of
them dispatches command 8 and then times out. It is fixed on this milestone branch (firmware commit
`7eed3af`) but that fix has not yet reached `beta`.

### Rig state left by this session

The attached board no longer runs shipped firmware. It carries a **locally built `[env:leonardo]`
image with `-D DEV_TOOLS=1`, which self-reports as `3.0.0b33` and is NOT the released `3.0.0b33`.**
The port re-enumerated from `/dev/ttyACM0` to `/dev/ttyACM1` during the session; identity was
re-probed on the new node (`leonardo`, `3.0.0b33`) per standing bench rule 1.

### Consequence for this phase

**Superseded by the measurement, 2026-09-19.** The paragraph below was written while the session was
blocked and before the `dt_set_registers` fix unblocked it. It is kept because the blocked state was
real, but it is **no longer true** and must not be acted on:

> D-07 makes the Window A figure load-bearing: it is the shipped threshold and cannot be derived
> without an attended bench session. No figure exists. **`199-03` cannot fill
> `DELIVERABLE_MAX_DROP_PATH_MV` from this record**, and `199-05` cannot claim a measured threshold.

Both windows were subsequently measured. `DELIVERABLE_MAX_DROP_PATH_MV = 17380` and
`DELIVERABLE_MAX_DIRECT_VPE_MV = 22140` are recorded in § "Measured figures" above, and that fenced
block is the only place any consumer should read them from. D-07's substance still stands: the figure
is load-bearing and cannot be re-derived without another attended bench session.

**Where the figure is consumed changed too.** Under D-21 (2026-09-19) the VPE-routing decision moved
from the host to the firmware, so `17380` becomes a firmware constant in `include/rurp_pinout.h`
rather than a host-side threshold. It is a **ceiling** — the most the drop-resistor path can deliver
at any pot setting — not a threshold for one pot position. See `199-CONTEXT.md` § D-21/D-22/D-23.

## Task 3 — Paired ADC reads and the error figures

### Method

- Shield revision **Rev 2.0**, operator silkscreen statement (standing bench rule 6; `hw_revision`
  cannot distinguish Rev 2.0 / Rev 2.2 / modified Rev 0 and was not used to establish it).
- Socket **empty** for the whole session, operator statement (D-05).
- Pot at **maximum**, operator statement, set against the operator's own meter and **not touched at
  any point** after Task 1 — so all four figures above share one pot setting.
- Composites, host `-f` namespace: `0x188` = `0x080` REGULATOR + `0x100` VPE-DROP + `0x008` P1;
  `0x088` = `0x080` REGULATOR + `0x008` P1 with the drop bit clear. Wire payloads `00008188` and
  `00008088`, the `0x80` in byte 2 being the firestarter-namespace marker.
- Meter at **socket pin 1 against board ground** for both windows. `pinouts.json`'s `DIP28_2764`
  entry puts `vpp-pin` at 1, which is why both configurations are measured there.
- Monitor commands, each a **bounded one-second sampling window**:
  `firestarter -p /dev/ttyACM0 vpp -t 1` and `firestarter -p /dev/ttyACM0 vpe -t 1`.
  The `-t` option is mandatory, not stylistic: without it the read loop is an unbounded
  `while True:` live monitor, which standing bench rule 4 forbids outright.
- **Sampling rule, fixed before the reads were taken:** the value recorded is the last frame emitted
  inside the window; if the last three frames disagreed by more than one 100 mV step, every frame
  would be recorded with its spread instead of a single figure. In the event each window emitted two
  frames and **both frames were identical** on both rails (`VPP: 18.7V` twice; `VPE: 23.9V` twice),
  so the rule resolved without a spread. Internal VCC reported 5.5 V in both windows.

### The two error figures

| Rail | Monitor reading | Meter at pin 1 | Signed difference | As a share of the meter figure |
|---|---|---|---|---|
| Drop-resistor / VPP | 18700 mV | 17380 mV | **+1320 mV** | **+7.59 %** |
| Direct VPE | 23900 mV | 22140 mV | **+1760 mV** | **+7.95 %** |

Both derived by integer arithmetic from the four integers in "Measured figures". The firmware reads
**high** against the meter on both rails.

## Provisional versus measured

The operator named **18 V** as the provisional drop-path figure during discussion, and it was not an
arbitrary guess: 18 V is the top of upstream's own VPP scale, and every capped row in the database is
capped at exactly it. The measured drop-path figure at socket pin 1 is **17380 mV**.

**17380 ships.** D-07 makes this session load-bearing rather than confirmatory, and the measurement
wins over the provisional figure regardless of how well-motivated that figure was. The difference is
not cosmetic: at 18000 the nine algorithm `0x07` rows sitting at exactly 18000 would have been
judged reachable, and at 17380 they are not.

## Limits

Stated in the voice `firestarter_app/firestarter/diagnostic_report.py`'s rail-reading disclosure
establishes, and section 6 of `tools/DECODE-NOTES.md` templates.

- **The ADC/meter difference is a combined discrepancy and this session cannot separate its terms.**
  The monitor reads assert no socket-routing bit, while the meter reads at pin 1 *through the P1
  route*. The +7.59 % and +7.95 % figures are therefore an ADC error **plus** a P1-switch-path drop,
  summed. Nothing here attributes any portion of either figure to one term or the other.
- **Backlog 999.38's figure is cited, not replaced.** Its roughly 7.5 % ratiometric figure, range
  6.8 % to 8.3 %, remains the only ADC-only number this project has. Both figures above fall inside
  that range, which corroborates it from an independent measurement but does not supersede it.
  **999.38's standing operational rule stands unchanged: any pot target is set from a meter reading,
  never from the firmware's own figure.**
- **The monitor's wire format carries whole volts plus one tenths digit**, so every firmware figure
  here is quantised to 100 mV. `18700` and `23900` carry two significant decimal places at most and
  must not be treated as millivolt-precise.
- **The pin-21 direct-VPE configuration was deliberately not measured** (D-06). The 20 algorithm
  `0x0B` rows, including all six rows at 25000 mV, receive VPE through `CTRL_VPE_ENABLE` to pin 21.
  No figure in this record is evidence about those rows.
- **One shield, one session, one pot setting.** These are figures for *this* Rev 2.0 board at
  maximum pot. They are not a specification, not a fleet figure, and not a tolerance band. A second
  board could differ, and this session measured no second board.
- **The bench method in the plan does not work on this rig and was replaced mid-session.** The
  figures came from `dev reg` invocations held by the firmware's own button-wait loop, after a
  firmware fix to `dt_set_registers`. See Fault 1 and Fault 2. Any future session that copies the
  plan's `hold_rail.py` recipe will measure nothing and, worse, be told it succeeded.

## Disposition of this plan's Task 2 verify legs

Recorded because two of the four do not pass, and neither failure is a defect in the measurement.

| Leg | Result | Disposition |
|---|---|---|
| `grep -qF 'hold_rail.py 0x188'` | PASS | The string is present, but as a **failed attempt**, not as the provenance of `17380`. The leg cannot tell those apart. |
| `grep -qF 'hold_rail.py 0x088'` | **FAIL** | **True negative, left failing.** Window B was measured with `dev reg 0 0 0x088 -f`, not `hold_rail.py`, because `hold_rail.py` holds no rail on this rig. Inserting the string to make the leg pass would make the record lie about how the figure was obtained. |
| `git ls-files --error-unmatch …/hold_rail.py` | PASS | The script is git-tracked. It is also non-functional here; tracked and working are different claims. |
| `test -z "$(pgrep -af hold_rail.py)"` | **FAIL, then PASS** | **False positive.** The leg's pattern matches the verify script's OWN command line, because the preceding leg contains the literal `hold_rail.py` and both run in one shell. Re-run alone it returns empty, and a direct scan of every `/proc/<pid>/fd` for a `ttyACM` handle found no holder. The idiom needs `pgrep -af 'hold_rail[.]py'` **and** to not share a shell with a line containing the bare string. It fails closed, so it blocks rather than passing a live rail — the safe direction. |

Both windows were confirmed closed by the `/proc` fd scan, not by the `pgrep` leg.
