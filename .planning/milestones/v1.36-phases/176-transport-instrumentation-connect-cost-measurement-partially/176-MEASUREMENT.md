# Phase 176 Plan 05 — MEAS-01 Per-Connect Cost Measurement

**Written:** 2026-09-04 (Plan 176-05)
**App build measured:** `firestarter_app` HEAD `df2978e` on branch `gsd/v1.36-dev-test-fidelity`

---

## 1. What was measured, and what it is not

This document records the wall-clock duration of one `find_and_connect` → `disconnect` cycle —
`EpromOperator.measure_connect_cost`'s bench harness — captured on two real Arduino-class boards
attached to this container, ten samples per board, each run with the port pinned explicitly
(`restrict_to_port=True`) so port discovery cannot inflate the figure.

**The subject of this measurement is the host's connect sequence and the board's reset or
enumeration behaviour, never the chip.** No chip identification, read, write, verify, erase or
blank-check command was ever sent to either board during this measurement — the harness sends only
the lightweight `{'state': COMMAND_FW_VERSION}` setup/handshake command that `find_and_connect`
always sends to establish a link, exactly as `measure_command_nak_latency` already does. Nothing
below this line is an observation of any chip's electrical state, because no chip needed to be
present and, per the operator's own confirmation (§5), none was.

This measurement does not, and cannot, tell a reader whether an Uno-class board specifically resets
into optiboot on DTR assertion, or whether a Leonardo-class board specifically re-enumerates over
native USB CDC. It can only report the wall-clock time the host actually observed opening each port,
ten times per class, never blended into one board-independent number.

---

## 2. Provenance block

**Port identity, verified by command before driving any port** (two device nodes were present:
`/dev/ttyACM0`, `/dev/ttyACM1`; no `/dev/ttyUSB*` node existed):

```
$ python3 -m firestarter.main -p /dev/ttyACM0 fw
Beta app detected — defaulting to --pre. Use --firmware-version X.Y.Z to pin a stable version.
Reading current firmware version...
Connecting...Connecting... OK
Current firmware version: 3.0.0b22, for controller: leonardo on port /dev/ttyACM0
New firmware 3.0.0b25 available for leonardo (current: 3.0.0b22). Update now?
[y/n] (n):
Aborted!

$ python3 -m firestarter.main -p /dev/ttyACM1 fw
Beta app detected — defaulting to --pre. Use --firmware-version X.Y.Z to pin a stable version.
Reading current firmware version...
Connecting...Connecting... OK
Current firmware version: 3.0.0b22, for controller: uno on port /dev/ttyACM1
New firmware 3.0.0b25 available for uno (current: 3.0.0b22). Update now? [y/n]
(n):
Aborted!
```

`/dev/ttyACM0` is the port whose `controller:` value names `leonardo` — selected for the
Leonardo-class run. `/dev/ttyACM1` (`uno`) is the port whose `controller:` value names `uno` —
selected for the Uno-class run. Both device nodes present were driven; no node was left unqueried.
Both boards offered a firmware update to `3.0.0b25`; the update was **declined on both**, per the
orchestrator's instruction to keep the two classes on the same `3.0.0b22` build for comparability —
`Aborted!` on each transcript confirms the decline, not a failure of the `fw` read itself.

**`firmware_max_chunk`, read from the run rather than assumed.** The connect-cost harness's own log
does not carry this field (it is transient per-instance state on `SerialCommunicator`, discarded on
disconnect before the log is written), so it was read directly, once per port, via the identical
`find_and_connect(..., restrict_to_port=True)` call the harness itself uses — a supplementary
single connect per board, not counted among either board's ten timed samples:

```
$ python3 -c "
from firestarter.config import ConfigManager
from firestarter.serial_comm import SerialCommunicator
from firestarter.constants import COMMAND_FW_VERSION
for port in ['/dev/ttyACM1', '/dev/ttyACM0']:
    cfg = ConfigManager()
    comm = SerialCommunicator.find_and_connect({'state': COMMAND_FW_VERSION}, cfg, preferred_port=port, restrict_to_port=True)
    print(port, 'firmware_max_chunk=', comm.firmware_max_chunk, 'programmer_info=', comm.programmer_info)
    comm.disconnect()
"
/dev/ttyACM1 firmware_max_chunk= 512 programmer_info= Ready
/dev/ttyACM0 firmware_max_chunk= 1024 programmer_info= Ready
```

`/dev/ttyACM1` (uno) reports **512** and `/dev/ttyACM0` (leonardo) reports **1024** —
matching the board classes' expected buffer sizes exactly, and confirming the port-to-class mapping
above a second, independent way.

**Build identity — before either measured run:**

```
$ cd /workspaces/firestarter_app && git status --short
(clean — no output)
$ git rev-parse --short HEAD
df2978e
$ git rev-parse --abbrev-ref HEAD
gsd/v1.36-dev-test-fidelity
```

`df2978e` is the same commit `176-04-SUMMARY.md` records as landing `measure_connect_cost` itself —
this measurement runs the harness plan `176-04` built, not a drifted tree. The working tree was
still byte-unchanged after both runs (re-checked post-measurement, §7).

**The exact commands issued, verbatim, one per board class, ten samples each:**

```
$ cd /workspaces/firestarter_app
$ python3 -m firestarter.main -p /dev/ttyACM1 dev fault-inject sst27sf512 --mode connect-cost --samples 10 --output-dir <uno-output-dir>
$ python3 -m firestarter.main -p /dev/ttyACM0 dev fault-inject sst27sf512 --mode connect-cost --samples 10 --output-dir <leonardo-output-dir>
```

`sst27sf512` is an arbitrary chip token — connect-cost mode never resolves it (`resolve_chip` is
only reached on the default `cycle` mode branch in `cli_handlers.py`), so no chip database lookup or
bus configuration is built for either run.

---

## 3. Raw captured logs

### 3a. Uno-class run (`/dev/ttyACM1`) — terminal output

```
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
(exit code 0)
```

### 3b. Uno-class run — `connect-cost-log.txt`, verbatim

```
# per-connect cost (one pinned port, restrict_to_port=True)
port: /dev/ttyACM1  controller_identity: Ready
samples_collected: 10
sample_0: 2.518s
sample_1: 2.517s
sample_2: 2.518s
sample_3: 2.519s
sample_4: 2.518s
sample_5: 2.518s
sample_6: 2.517s
sample_7: 2.518s
sample_8: 2.519s
sample_9: 2.519s
min: 2.517s
median: 2.518s
max: 2.519s
structural_floor: 2.500s
remainder: 0.018s
decode_failures: 0
probe_timeouts: 0
resync_body_truncated: 0
resync_length_missing: 0
timeouts: 0
```

### 3c. Leonardo-class run (`/dev/ttyACM0`) — terminal output

```
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
Connecting...Connecting... OK
(exit code 0)
```

### 3d. Leonardo-class run — `connect-cost-log.txt`, verbatim

```
# per-connect cost (one pinned port, restrict_to_port=True)
port: /dev/ttyACM0  controller_identity: Ready
samples_collected: 10
sample_0: 2.676s
sample_1: 2.607s
sample_2: 2.606s
sample_3: 2.606s
sample_4: 2.608s
sample_5: 2.612s
sample_6: 2.611s
sample_7: 2.607s
sample_8: 2.606s
sample_9: 2.607s
min: 2.606s
median: 2.607s
max: 2.676s
structural_floor: 2.500s
remainder: 0.107s
decode_failures: 0
probe_timeouts: 0
resync_body_truncated: 0
resync_length_missing: 0
timeouts: 0
```

`controller_identity` in both logs reads `Ready` — that field is populated from
`comm.programmer_info`, which the setup/handshake ack sets to the RURP's generic `"Ready"` response
string, not a board-class name. It is transcribed here honestly rather than reported as
`leonardo`/`uno`; the board-class identity for each run comes from §2's independent `fw` command
transcriptions and the `firmware_max_chunk` read, not from this field.

---

## 4. The numbers

Both runs collected all 10 requested samples (`samples_collected: 10` in each log, matching
`--samples 10`); neither run reports `unmeasured` for any figure.

### 4a. Uno-class connect cost (512 B `firmware_max_chunk`, port `/dev/ttyACM1`)

| Figure | Value |
|---|---|
| Samples collected | 10 |
| Min | 2.517s |
| Median (`statistics.median_low`) | 2.518s |
| Max | 2.519s |
| Structural floor (board-independent) | 2.500s |
| Remainder (median − floor) | 0.018s |
| `probe_timeouts` observed during run | 0 |

**These two per-board-class figures are never blended, and no single per-connect cost number that
combines both board classes exists or should be quoted anywhere in this document.** Section 4a's
2.518s median describes only the Uno-class board on `/dev/ttyACM1`; it says nothing about the
Leonardo-class board below.

### 4b. Leonardo-class connect cost (1024 B `firmware_max_chunk`, port `/dev/ttyACM0`)

| Figure | Value |
|---|---|
| Samples collected | 10 |
| Min | 2.606s |
| Median (`statistics.median_low`) | 2.607s |
| Max | 2.676s |
| Structural floor (board-independent) | 2.500s |
| Remainder (median − floor) | 0.107s |
| `probe_timeouts` observed during run | 0 |

The Leonardo-class max (2.676s, sample_0) is noticeably higher than its own other nine samples
(2.606s–2.612s) — a first-sample effect this measurement did not investigate further; it is reported
as observed, not smoothed over or excluded.

---

## 5. Socket state, stated plainly

The operator confirmed, in this plan's checkpoint response, that both sockets were **empty** —
"attached" was the verbatim answer, and the checkpoint's own text records the operator having
confirmed "the socket is EMPTY on both boards." No `id`, `read`, `write`, `verify`, `erase` or
`blank` command was issued against either board during this measurement — only the connect-cost
harness's own setup/handshake command and the two supplementary `fw` reads, none of which engage
the chip-select or address bus. This is consistent with §1: the socket's contents are not a variable
this measurement depends on, and no chip needed to be inserted or removed for any part of this run.

---

## 6. Validation ceiling — hypotheses tested, and what the data does and does not support

RESEARCH §6 named two mechanisms as **hypotheses**, explicitly not findings, because this
repository contained no prior measurement of either:

- **Uno-class hypothesis (DTR/optiboot):** opening the port asserts DTR, resetting the ATmega328P
  into the optiboot bootloader, which waits before handing off to the sketch — expected to be the
  *dominant term* on Uno-class boards, possibly larger than the 2.5s structural floor.
- **Leonardo-class hypothesis (native USB CDC):** opening the port does not reset the MCU, so no
  bootloader wait is expected, but USB re-enumeration may substitute some smaller overhead.

**What §4's data actually shows: the opposite of the stated Uno-dominance hypothesis.** The
Uno-class remainder (0.018s) is smaller than the Leonardo-class remainder (0.107s), not larger. This
measurement does **not** support the claim that the Uno-class DTR/bootloader wait is the dominant
term beyond the shared 2.5s floor — on this build (`3.0.0b22`) and this specific board, whatever
bootloader wait occurs appears to fit entirely inside the existing `CONNECTION_STABILIZE_DELAY`
sleep, exactly the "invisible" possibility RESEARCH §6 already flagged rather than ruled out. This
measurement cannot distinguish "no bootloader wait occurred" from "a bootloader wait occurred and
was fully absorbed by the floor" — it has no instrumentation inside that 2.0s window, only the
outside wall-clock total. Neither hypothesis's underlying *mechanism* (DTR assertion, optiboot entry,
USB re-enumeration) is directly observed anywhere in this document; only the aggregate wall-clock
duration is. The Leonardo-class board's own larger remainder is recorded as an observation, not
attributed to any confirmed cause — a native-USB re-enumeration cost is a plausible candidate the
data is at least directionally consistent with, but this measurement provides no direct evidence of
that mechanism either.

No support status changes as a result of this document — this document introduces no
`support_status` field and touches no chip database entry. It records a host-and-board timing
figure only.

---

## 7. Downstream consumers

- **PRUNE-08 (Phase 180)** consumes MEAS-01's number. This phase records the measurement; it does
  not spend it — no scoping decision for PRUNE-08 is made here.
- **The R4-01 deferral** ("`EpromOperator` leasing one validated link per plan... MEAS-01 gates
  whether it is worth scoping") is not acted on here either. Both remainders (0.018s and 0.107s) are
  small relative to the 2.5s floor, which is itself unchanged by this measurement — that observation
  is left for PRUNE-08/R4-01 to weigh, not decided in this document.

**Post-measurement integrity check**, confirming this measurement did not modify what it measured:

```
$ git -C firestarter_app status --porcelain firestarter/
(clean — no output)
$ git -C firestarter status --porcelain
(clean — no output)
```

---

## Disposition

**MEAS-01: measured, for both board classes, from two real boards attached to this container.**
Uno-class (512 B, `/dev/ttyACM1`): median 2.518s, remainder 0.018s over the 2.500s floor, 0
`probe_timeouts`. Leonardo-class (1024 B, `/dev/ttyACM0`): median 2.607s, remainder 0.107s over the
same 2.500s floor, 0 `probe_timeouts`. The two figures are never blended and no averaged
single-number per-connect cost is quoted anywhere in this document. Port identity was verified by
command both via `fw` and via a direct `firmware_max_chunk` read before either board was driven
further, both boards stayed on firmware `3.0.0b22` (an offered `3.0.0b25` update was declined on
both), the socket was empty for every run, and the working tree of both `firestarter_app` and
`firestarter` remained byte-unchanged throughout.
