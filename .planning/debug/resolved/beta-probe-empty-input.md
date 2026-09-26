---
status: resolved
trigger: "an enduser reported that he couldent get the beta version to work"
created: 2026-09-09T09:11:18Z
updated: 2026-09-09T10:53:12Z
---

## Current Focus

status_in_one_line: REOPENED, then RE-RESOLVED with the live reproduction that had been
  missing. The failure and its cause turned out to be separable: `_probe_port`'s existing
  `fault_inject_outgoing` hook (already in production code for dev fault-inject tooling)
  manufactures the exact interleaved-frame CONDITION deterministically on real hardware,
  without needing the reporter's own environment. Matrix A/B/C/D run against the live Uno on
  `/dev/ttyACM1` (fw 3.0.0b25): A (pre-fix + 1 bad frame) reproduced the reporter's failure
  byte-for-byte — the live RED that had been missing all session. B (post-fix + 1 bad frame)
  succeeded. C (post-fix + 2 bad frames, the reporter's log literally shows two "Empty input"
  lines) FAILED — the original fix's fixed one-retry bound was under-built. Reworked the fix
  into a wall-clock deadline that discards any number of the generic error text within a
  bounded window (`SETUP_ACK_RECOVERY_TIMEOUT_S`) rather than one fixed retry; re-ran the full
  matrix plus a 3-bad-frame case, all pass. Committed as `8b3d8f9`. Secondary raw-byte capture
  (non-blocking, attempted after the matrix) caught a REPRODUCIBLE stray byte (`0xf0`, 8/8
  captures across plain DTR-reset cycles and immediate-post-avrdude-flash) — corroborating,
  not required, evidence that this board genuinely does emit spurious pre-command bytes on
  reset, independent of any injection.

hypothesis (SEEDED — orchestrator's pre-analysis): FALSIFIED in its specific mechanism, CORRECT
  in its general class. The "board hasn't booted yet" framing is wrong by direct measurement:
  `CONNECTION_STABILIZE_DELAY` is 2.0s and firmware boot (setup() through entry into loop()) is
  on the order of 100ms, so the board has been idle in a fully-booted `loop()` for roughly 1.9s
  before the host ever sends its command — there is no "still booting" window for the command
  frame to land in. The CONFIRMED mechanism (see Resolution) is still an Uno-class,
  reset-adjacent framing artifact, just a different one: a spurious `MSG_ERR_EMPTY_INPUT` frame
  interleaved with the genuine ack, consumed by the host's read-first-response logic.

next_action: DONE. First pass (documented in the frozen evidence below) established: 41/41
  clean natural probe attempts on this Uno, plus proof via hex/source diff that no firmware
  regression exists in the b22-b25 range. That left the fix hardware-UNVERIFIED (never
  exercised its own retry branch on real hardware) even though nothing contradicted it.
  Reopened per the coordinator's insight: the FAILURE (needs the reporter's noisy environment)
  and the CAUSE (an interleaved spurious frame ahead of the real ack) are separable, and the
  CAUSE can be manufactured deterministically via `_probe_port`'s existing
  `fault_inject_outgoing` hook. Ran the A/B/C/D matrix (see new Evidence entries below); C
  failed against the original single-retry fix, so reworked it into a bounded deadline,
  re-verified the full matrix plus a 3-frame case, extended the regression test with the
  2-frame case (RED against the old fix, GREEN against the rework), re-ran ruff/format/mypy
  watermark/full-suite, committed as `8b3d8f9`. Attempted the optional raw-byte capture
  afterward and got a positive, reproducible result (see Evidence). Session re-resolved.

reasoning_checkpoint:
  hypothesis: "The host's SerialCommunicator._probe_port gives up on the setup-command probe
    because expect_ack() returns on the FIRST OK/ERROR response with no check for whether the
    genuine ack is already queued immediately behind it — and MSG_ERR_EMPTY_INPUT is firmware's
    documented generic catch-all for any CMD_IDLE COBS-decode failure (empty read, CRC
    mismatch, COBS violation, or read underrun), so an unrelated, self-recovering framing
    glitch reads to the host exactly like a real command rejection."
  confirming_evidence:
    - "firestarter.cpp:253-255 source comment names all four causes MSG_ERR_EMPTY_INPUT is
      reused for, directly refuting 'Empty input' as a literal empty-read signal."
    - "expect_ack()/get_response() source: returns on the first type in {OK, ERROR}, no
      lookahead, no correlation to the command just sent — read directly, not inferred."
    - "New test_probe_spurious_setup_ack.py, run against UNMODIFIED code (fix reverted for the
      RED run): replaying the reporter's exact frame order (spurious Empty input immediately
      followed by genuine OK: Ready) through the REAL _probe_port/expect_ack path reproduces
      'probe returns None' with zero speculation — a FakeSerial, not a firmware guess."
    - "rurp_communication_read_data()'s four failure paths (source read, not inferred) all
      re-anchor on the frame delimiter, proving the SAME bytes that produced a failure cannot
      ALSO be the source of a later genuine OK — the late OK must be a separate, correctly
      decoded frame the host simply read too late relative to expect_ack()'s early return."
  falsification_test: "If expect_ack()'s single-response-then-stop behavior were NOT sufficient
    to explain the symptom, the FakeSerial replay test (real _probe_port, real expect_ack, only
    the serial transport faked) would still return None even with more grace-window reads
    added, or the probe would already succeed on unmodified code. Neither was observed: RED on
    unmodified code, GREEN after the retry fix — the test IS the falsification instrument, and
    it did not falsify the hypothesis."
  fix_rationale: "The fix targets the confirmed mechanism directly: it does not touch firmware
    (unverifiable this session, and not proven to be the sole source of the spurious frame), it
    does not broaden expect_ack()'s tolerance globally (which risks masking real errors on
    hazardous mid-operation paths), and it does not blindly retry forever. It gives the ONE
    ambiguous, catch-all error text ONE bounded extra chance to be superseded by a real ack, at
    the ONE call site (_probe_port's setup handshake) proven hazard-free to retry because
    CMD_FW_VERSION never reaches configure_memory / engages VPP-VPE."
  blind_spots (SUPERSEDED — see the 2026-09-09T11:xx:xxZ evidence entries below; kept verbatim
    for the record of what was unknown at write time): "The EXACT electrical/firmware trigger
    for the spurious MSG_ERR_EMPTY_INPUT frame is not confirmed on real Uno hardware — only
    argued by analogy to two other documented PORTD-pin-sharing hazards in this same codebase
    (PD1/TX garbage, PD0/RX boot-transition garbage). It is possible the reporter's board has an
    additional or different Uno-specific fault this fix does not address, in which case the
    probe would still eventually fail after the one retry. The fix does not fix that
    firmware-side ambiguity (MSG_ERR_EMPTY_INPUT as a 4-way catch-all) — a future enhancement
    could split it into distinct message IDs so the host can retry ONLY on truly-transient
    causes, not on every framing failure. Not verified on Uno-class hardware at all —
    operator-gated." RESOLUTION: the "probe would still eventually fail after the one retry"
    concern was EXACTLY RIGHT and is what matrix leg C on real hardware confirmed — the fix has
    since been reworked from a fixed one-retry bound to a wall-clock deadline that survives any
    number of the generic error text within the bound, and this is now live-hardware-verified
    (matrix A/B/C/D, see below), not merely argued by analogy.
  candidate_causes:
    - "code: host-side expect_ack()/_probe_port has no tolerance for an interleaved unsolicited
      response between a sent command and its ack (confirmed, fixed)."
    - "environment/hardware: Uno-class USB-serial bridge + PORTD pin-sharing produces a
      transient spurious RX byte/frame around a DTR-triggered reset (consistent with two
      already-documented analogous hazards in this codebase; not independently proven this
      session for lack of Uno hardware)."
  and_gate: "yes — argued and evidenced above under root_cause. The host-side gap alone is
    cosmetic without SOME source of an interleaved spurious frame; the hardware-class hazard
    alone would be harmless if the host correctly looked past it. Both were required to produce
    the reported permanent, self-sustaining failure."

## Symptoms

expected: `firestarter fw` connects to the programmer, reads its firmware version, and reports
  whether an update is available.

actual: the probe NEVER succeeds. Two distinct firmware-side rejections, before and after a
  forced reflash:
  - BEFORE reflash (unknown pre-existing firmware): firmware logs `I: Buf val: 0x7b` then
    `ERROR: Bad JSON`. Host reports "responded but not with OK: Bad JSON".
  - AFTER a successful forced flash to firmware 3.0.0b25: firmware logs `ERROR: Empty input`
    (twice — once BEFORE the command was even sent), host reports "responded but not with OK:
    Empty input", and the genuine `OK: Ready` appears in the log AFTER the host has already
    given up and disconnected.
  Both end at: `Failed to read firmware version: No compatible programmer found on any port.`
  followed by `Could not determine current firmware version. Use --install or --force to
  proceed with installation.`

errors (verbatim, from the reporter's `-v` logs):
  - `INFO   :RURP         : 325: I: Buf val: 0x7b`
  - `ERROR  :RURP         : 325: ERROR: Bad JSON`
  - `DEBUG  :SerialComm   : 843: Port /dev/ttyACM0 responded but not with OK: Bad JSON`
  - `ERROR  :RURP         : 325: ERROR: Empty input`
  - `DEBUG  :SerialComm   : 843: Port /dev/ttyACM0 responded but not with OK: Empty input`
  - `DEBUG  :RURP         : 325: OK: Ready`   <- arrives too late, after the give-up
  - `ERROR  :Firmware     : 234: Failed to read firmware version: No compatible programmer found on any port.`
  - `ERROR  :Firmware     : 829: Could not determine current firmware version. Use --install or --force to proceed with installation.`

timeline: reported against the CURRENT published beta, app 3.0.0b36 (released 2026-09-02
  16:14Z). Unknown whether an earlier beta ever worked for this user. Not a bench-only or
  branch-only condition — this is the artefact PyPI is serving today.

reproduction (reporter's, verbatim): `firestarter -v fw`, then
  `firestarter -v fw --force --board uno`, then `firestarter -v fw` again.

## Context

### Reporter environment (from the logs — everything not listed here is UNKNOWN)

- host: `dim20@noicebox`, Linux, config at `/home/dim20/.firestarter/config.json`
- app: `Firestarter, version 3.0.0b36` (installed from the beta channel, not from source)
- board: `/dev/ttyACM0`; the user chose `--board uno`, and avrdude ran `-p atmega328p
  -c arduino -b 115200`, so the target is **Uno-class** (ATmega328P behind a USB-serial bridge)
- avrdude: 8.0 at `/usr/bin/avrdude`
- firmware BEFORE the forced flash: UNKNOWN version (the probe never got far enough to read it)
- firmware AFTER: 3.0.0b25 — flashed successfully in 8.23s, avrdude's part-signature check
  passed, so the image and the MCU do match
- shield revision: UNKNOWN and not asked. Almost certainly irrelevant: this failure is in the
  serial/probe layer and no chip operation is reached.

### Version pairing — CHECKED, and NOT the cause

The obvious first suspicion (app b36 talking to a firmware too old to speak the framed protocol)
does NOT hold for the post-flash failure, and the orchestrator already eliminated it:

- newest published firmware release is `3.0.0b25` (2026-09-02T17:21:41Z) — the app picked the
  correct newest pre-release, it did not mis-sort.
- app `3.0.0b36` (2026-09-02T16:14:37Z) and firmware `3.0.0b25` are the MATCHED pair, cut ~1h
  apart on the same day. App and firmware carry independent beta counters; b36-vs-b25 is not a
  skew.
- firmware tag `3.0.0b25` DOES carry the COBS framing surface (`include/frame_vectors.h`,
  `test/native/avr/test_cobs_cmd_frame/`, `tools/catalog/frame-vectors.toml`), and the beta app
  carries its counterpart (`firestarter/frame_parser.py`, `firestarter/frame_vectors.py`).

So the post-flash `Empty input` is a defect in the matched, currently-published pair. (The
PRE-flash `Bad JSON` is separately consistent with a genuinely pre-framing firmware on the
user's board, and may be a different, benign story — but do not assume that; `Buf val: 0x7b`
is the ASCII `{`, and a pre-framing firmware reading COBS bytes should report the COBS
overhead byte, not `{`. That inconsistency is unexplained and is EVIDENCE, not noise.)

### Wire-format arithmetic already done (use it, don't redo it)

The host frames commands as COBS + CRC8 with compact JSON separators. Both reported byte counts
reconcile exactly under that framing, which confirms the host side put a well-formed frame on
the wire:

- `{"state":13}` = 12 bytes + 1 CRC8 + 1 COBS overhead + 1 delimiter = **15 bytes** ✓ (log: "Sent 15 bytes")
- `{"state":13,"flags":1}` = 22 bytes + 1 + 1 + 1 = **25 bytes** ✓ (log: "Sent 25 bytes")

`state: 13` is `COMMAND_FW_VERSION` (`firestarter_app/firestarter/constants.py:86`).

### The self-sustaining trap (this is what makes it a release blocker, not an annoyance)

1. `fw` cannot read the version → prints "Use --install or --force to proceed".
2. `--force` flashes the newest firmware successfully.
3. The reflashed board STILL fails to probe.
4. Every subsequent `fw` lands back at step 1.

There is no documented escape from inside the tool. Any end user in this state is fully blocked
on all chip operations, not just `fw` — the probe is the common gate.

### Why this rig may never have caught it

The bench board attached to this devcontainer RIGHT NOW is `/dev/ttyACM0` =
`Arduino LLC | Arduino Leonardo | vid 9025 pid 32822`. A Leonardo has native USB and does NOT
reset when the port is opened; an Uno resets on DTR assert. The project already records this
class split as a real behavioural axis (chip-out-before-sideload is Uno-class only; the
held-rail DMM proxy is broken specifically by DTR-reset-on-close). If the defect is the
open-race described in the hypothesis, this rig is structurally incapable of reproducing it and
the CI native tests would not model it either.

**Consequence for verification:** a live confirmation on Uno-class hardware requires the
operator to attach an Uno. That is an OPERATOR-GATED step — request it explicitly at a
checkpoint, do not assume the attached Leonardo can stand in for it, and do not report a
Leonardo pass as a fix for this bug.

### Local tree state

- `firestarter_app` on `gsd/v1.36-dev-test-fidelity` @ `04fd982`; `origin/beta` @ `49bac1a`
- `firestarter` on `gsd/v1.36-dev-test-fidelity` @ `c14f191`
- The reporter is on the PUBLISHED b36, which may differ from both. Establish what the published
  b36 actually contains before attributing behaviour to local HEAD.

## Evidence

- timestamp: 2026-09-09T09:11:18Z
  source: orchestrator pre-analysis (static, no hardware touched)
  finding: Sent-byte counts (15 / 25) reconcile exactly with COBS+CRC8 framing of compact JSON,
    so the host emitted a well-formed frame in both the pre- and post-flash runs. The failure is
    on the firmware side of the wire or in the host's reading of the reply, not in frame
    construction.

- timestamp: 2026-09-09T09:11:18Z
  source: `gh release list` on henols/firestarter and henols/firestarter_app
  finding: firmware newest = 3.0.0b25 (2026-09-02T17:21Z); app newest = 3.0.0b36
    (2026-09-02T16:14Z). The app's `--pre` resolution selected the genuinely newest firmware.
    Version mis-selection is ELIMINATED as the cause of the post-flash failure.

- timestamp: 2026-09-09T09:11:18Z
  source: `git ls-tree -r --name-only 3.0.0b25` (firmware) and `origin/beta` (app)
  finding: Both sides of the published pair carry the COBS framing surface. A
    protocol-generation mismatch is ELIMINATED for the post-flash failure.

- timestamp: 2026-09-09T09:11:18Z
  source: reporter log ordering, third run
  finding: `ERROR: Empty input` is logged BEFORE "Sending command to programmer", and
    `OK: Ready` is logged AFTER the host's "responded but not with OK" give-up. The reply stream
    is off by one relative to what the host expects — the host consumed an unsolicited firmware
    line as the ack for its command. This ordering is the single most load-bearing detail in the
    report; preserve it in any reproduction attempt.

- timestamp: 2026-09-09T09:11:18Z
  source: `serial.tools.list_ports` in this devcontainer
  finding: the only attached board is an Arduino Leonardo (native USB, no DTR reset on open).
    The reporter's target is Uno-class (avrdude `-p atmega328p`). The rig cannot exercise the
    reporter's class of board as configured.

- timestamp: 2026-09-09T09:40:00Z
  source: `firestarter_app/firestarter/serial_comm.py:66-79` (constants) + `:131-206` (`__init__`)
  finding: `CONNECTION_STABILIZE_DELAY = 2.0` (seconds, slept unconditionally right after
    `serial.Serial(...)` opens). `consume_remaining_input()` is called by `_probe_port`
    immediately after that sleep, with its own 0.5s drain window, BEFORE
    `send_json_command()`. This directly refutes the seeded hypothesis's "board hasn't booted
    yet" framing — 2.0s is enormously more than firmware needs to boot.

- timestamp: 2026-09-09T09:41:00Z
  source: `firestarter/src/boards/rurp_serial_utils.cpp:12-18` (`rurp_serial_begin`) +
    `firestarter/src/firestarter.cpp:36-47` (`setup()`)
  finding: firmware boot (`rurp_serial_begin`'s fixed `delay(50)` plus normal `setup()` work) is
    on the order of 100ms, roughly 20x shorter than the host's 2.0s stabilize sleep. By the time
    the host sends its command, the board has been sitting fully booted in `loop()` for ~1.9s.
    Boot-timing races are structurally ruled out as the mechanism.

- timestamp: 2026-09-09T09:45:00Z
  source: `firestarter/src/firestarter.cpp:220-236` (`loop()`, `CMD_IDLE` branch) +
    `firestarter/tools/catalog/messages.toml:451-457`
  finding: `MSG_ERR_EMPTY_INPUT` ("Empty input") is a REUSED catch-all, not a literal
    empty-read indicator. The `else` arm that logs it fires whenever
    `rurp_communication_read_data()` returns <= 0, and the source comment right above it names
    FOUR distinct causes folded into this one message: "CRC mismatch, COBS violation, overflow,
    or read underrun." So an "Empty input" ack proves only "a decode attempt failed for some
    framing-class reason," not that nothing was received.

- timestamp: 2026-09-09T09:47:00Z
  source: `firestarter/src/boards/rurp_serial_utils.cpp:105-224` (`rurp_communication_read_data`)
    + `:73-103` (`_drain_to_delimiter`)
  finding: every failure return path (`-1` timeout/underrun, `-2` overflow, `-3` COBS violation,
    `-4` CRC mismatch) either fully drains to the next `0x00` or has already consumed the
    terminating `0x00` as the trigger for the failure. So a single malformed frame cannot leave
    the RX cursor misaligned for the NEXT read — each failed decode attempt cleanly re-anchors
    on a frame boundary before `loop()` tries again. This means two "Empty input" events in one
    probe are two SEPARATE malformed-frame incidents, not one cascading desync — and, critically,
    it also proves the SAME bytes that produced a failed decode cannot ALSO be the source of a
    later successful "OK: Ready" (the failure path always consumes/drains the frame it failed
    on). The late "OK: Ready" in the report must therefore come from bytes the host never
    examined during `expect_ack()`, not from a delayed retry of the same command bytes.

- timestamp: 2026-09-09T09:50:00Z
  source: `firestarter_app/firestarter/serial_comm.py:567-581` (`expect_ack`) + `:551-565`
    (`get_response`)
  finding: `expect_ack()` returns on the FIRST response whose type is "OK" or "ERROR" — it does
    not check whether more data is already queued behind that response, and does not
    distinguish "this ERROR is clearly this command's real reply" from "this ERROR is an
    unrelated frame that happened to arrive first." Combined with the previous finding, this is
    sufficient BY ITSELF to explain the reported symptom: if a spurious `MSG_ERR_EMPTY_INPUT`
    frame is sitting in the RX buffer ahead of the genuine `MSG_OK_READY` ack when
    `expect_ack()` reads, the host consumes the wrong one, reports "not with OK", and
    disconnects — and ONLY `disconnect()`'s own opportunistic `consume_remaining_input()` call
    ever reads (and logs) the genuine ack, which is exactly the log ordering the reporter
    captured (`OK: Ready` appears after "responded but not with OK", before "Disconnected").

- timestamp: 2026-09-09T09:52:00Z
  source: `firestarter_app/firestarter/serial_comm.py:92-101` (`PREFIX_REGEX` comment) +
    `firestarter/src/boards/uno_rurp_shield.cpp:61-84` (`rurp_set_communication_mode`)
  finding: this codebase ALREADY documents two independent, previously-encountered instances of
    the same hazard class on Uno-class hardware, both caused by PORTD pin-sharing between the
    UART and the RURP shield's parallel bus: (1) `PREFIX_REGEX`'s rightmost-match design exists
    specifically because "the firmware's data-bus writes during programming toggle PD1 (which
    doubles as UART TX), and the bridge captures those toggles as spurious UART frames"; (2)
    `rurp_set_communication_mode()`'s PORTD-high-before-DDRD-clear sequencing plus its own
    post-`Serial.begin()` drain loop exists specifically because "clearing DDRD bit 0 and
    calling Serial.begin() immediately enables RXEN0 while PD0 may still be LOW, which the UART
    samples as a START BIT and queues spurious bytes into the RX ring." Both are PD-line-sharing
    artifacts on Uno-class boards only — a Leonardo has a dedicated USB peripheral and never
    multiplexes UART pins with the parallel bus, so it structurally cannot exhibit either. A
    third instance of this same hazard class (a stray/misaligned byte reaching the CMD_IDLE COBS
    decoder around a DTR-triggered reset, which `rurp_set_communication_mode`'s own mitigation
    is scoped ONLY to the boot/mode-transition instant and does not generally guard) is the most
    parsimonious explanation for where the reporter's spurious `MSG_ERR_EMPTY_INPUT` frames
    originate — consistent with, not proof of, since this rig cannot attach Uno-class hardware.

- timestamp: 2026-09-09T09:58:00Z
  source: `firestarter_app/tests/test_probe_spurious_setup_ack.py` (new), run against
    UNMODIFIED `serial_comm.py` (fix patch reverted for this run only, then reapplied)
  finding: replaying the reporter's EXACT frame ordering (`MSG_ERR_EMPTY_INPUT` immediately
    followed by a genuine `MSG_OK_READY`) through a `_FakeSerial`-backed
    `SerialCommunicator._probe_port` call — no hardware involved — reproduces the bug: `_probe_port`
    returns `None` (probe fails) even though the real ack was one read away. This is direct,
    reproducible, hardware-free proof that the HOST's "return on first significant response,
    never look further" behavior is SUFFICIENT BY ITSELF to produce the reported symptom,
    independent of what causes the firmware to emit the spurious frame in the first place.

- timestamp: 2026-09-09T10:02:00Z
  source: `firestarter/src/firestarter.cpp:79-88,318-320` (`parse_json`, `loop()` switch) +
    `firestarter_app/firestarter/firmware.py:200-202` (`check_current_firmware` comment)
  finding: CMD_FW_VERSION (13) is not a memory command and is not `< CMD_READ_VPP` (11), so
    `parse_json` performs no `configure_memory` call for it — no VPP/VPE rail is ever engaged by
    this probe command, on either the setup ack or the follow-up `fw_get_version()` ack. This
    means retrying the ack read (or, if ever needed, retrying the whole exchange) at the probe
    step is hardware-safe: nothing hazardous has been armed by the time a retry could happen.

- timestamp: 2026-09-09T10:08:00Z
  source: `firestarter/src/firestarter.cpp:161-165` (pre-Phase-51 `CMD_IDLE` peek-loop, via
    `git show 0550431 -- src/firestarter.cpp`) vs. current COBS decode path
  finding: the PRE-flash `Bad JSON` symptom is a SEPARATE, BENIGN story, now confirmed (not just
    plausible) by reading the actual pre-COBS-framing firmware logic that commit `0550431`
    (Phase 51-01) replaced. That old logic was: `if (rurp_communication_peak() == '{') {
    init_programmer(...) } else { rurp_communication_read(); /* discard non-'{' byte */ }`. Fed
    the CURRENT host's COBS-framed wire bytes for `{"state":13}` — `[0x0E][12 raw json
    bytes][crc][0x00]` — that old peek-loop discards the leading `0x0E` (not `{`), then locks
    onto the very next byte, which genuinely IS `{` (0x7b, the raw JSON's first character,
    unmodified by COBS since it needed no zero-escaping), and reads the remainder of the frame
    (JSON text plus the un-stripped trailing CRC byte and terminator) as one raw blob into
    `data_buffer`. That blob is not valid JSON, so `jsmn_parse` fails and the SAME two log lines
    the reporter saw are produced verbatim: `Buf val: 0x7b` then `Bad JSON`. This means the
    user's board's PRE-EXISTING firmware genuinely predated the COBS framing migration (Phase
    51, well before the 3.0.0 beta line went COBS-only) — exactly the scenario
    `find_and_connect`'s own "may predate the current command framing" error text already names.
    It is not a new defect; it is the expected, documented failure mode for an old board talking
    to a COBS-only host, and the reporter's own next step (`--force`) is the correct remedy for
    it.

- timestamp: 2026-09-09T10:20:00Z
  source: `serial.tools.list_ports` (independent re-check, not trusted from the coordinator's
    message alone) + live probe against `/dev/ttyACM1`
  finding: an Arduino Uno R3 (vid 0x2341 pid 0x0043, serial 55736303739351B040E1) is attached on
    `/dev/ttyACM1` (NOT `/dev/ttyACM0` — the Leonardo had stopped enumerating). The board's
    PRE-EXISTING firmware, read cleanly via the probe itself before any flash: `3.0.0b22`. 20
    probe-only runs against it (10 spaced 1s apart, 10 back-to-back) split across the unmodified
    (`HEAD~1`) and fixed (`HEAD`) `serial_comm.py` — 25/25 clean, zero spurious interleave. Board
    was NOT freshly flashed for this leg (b22 was already resident and idle).

- timestamp: 2026-09-09T10:35:00Z
  source: `gh release download` (authenticated, sidesteps the unauthenticated
    `api.github.com` core-rate-limit exhaustion hit earlier this session — confirmed via
    `curl -s https://api.github.com/rate_limit`, 0/60 remaining) for the uno `.hex` assets of
    3.0.0b22/b23/b24/b25, followed by `md5sum` + `diff` on all four
  finding: **3.0.0b23, 3.0.0b24 and 3.0.0b25's `firestarter_uno.hex` are byte-for-byte identical
    except ONE line carrying the embedded version-identity ASCII string** (`"23:uno"` ->
    `"24:uno"` -> `"25:uno"`). There is NO compiled-code difference among the three releases.
    `3.0.0b22`'s hex differs substantially (3058 diff lines, most of the binary shifted) — a
    real code delta exists there, but it predates b23.

- timestamp: 2026-09-09T10:38:00Z
  source: `git log --oneline 3.0.0b22..3.0.0b23 -- <every file the CMD_FW_VERSION probe path
    touches>` + full `git diff 3.0.0b22 3.0.0b23 -- src/boards/rurp_serial_utils.cpp
    src/boards/uno_rurp_shield.cpp src/firestarter.cpp include/rurp_serial_utils.h
    include/rurp_shield.h include/firestarter.h` (read in full, not truncated — an earlier
    `head -60` on this same diff cut off before reaching the .cpp hunks and had to be redone)
  finding: the COBS decode loop (`rurp_communication_read_data`, `_drain_to_delimiter`), the
    PORTD/com_mode transition code (`rurp_set_communication_mode`, `rurp_set_programmer_mode`,
    `rurp_log_id`), and `firestarter.cpp`'s CMD_IDLE branch are **100% comment-reword/condense
    diffs between b22 and b23 — zero logic changed.** `get_cmd()` (the function that extracts
    `handle->cmd` from the wire `"state"` field for EVERY command, including CMD_FW_VERSION) is
    BYTE-IDENTICAL between the two tags. The ONE real code change in the b22-b23 window that
    touches a probe-adjacent file is `76ff592` (`include/firestarter.h`): narrows
    `handle->protocol` (`uint32_t`->`uint8_t`) and `handle->ctrl_flags` (`uint32_t`->`uint16_t`).
    Neither field is read or written anywhere in the CMD_FW_VERSION path (`parse_json` never
    calls `configure_memory` or `json_parse` for this command — see the earlier
    `2026-09-09T10:02:00Z` evidence entry). The much larger diffs elsewhere in the b22-b23 range
    (`eprom.cpp` 547 lines, `eeprom_28c.cpp` 799 lines, `json_parser.c` 328 lines,
    `operation_utils.cpp` 210 lines, etc.) are entirely memory-operation code
    (`configure_memory`/`json_parse`/field-table parsing for `memory-size`/`address`/`algorithm`/
    etc.) that CMD_FW_VERSION structurally never reaches. **Conclusion: there is no firmware code
    regression anywhere in the b22->b23->b24->b25 chain that could explain a deterministic
    difference in probe reliability.**

- timestamp: 2026-09-09T10:45:00Z
  source: live hardware, operator's standing flash grant (no per-action confirmation, socket
    confirmed empty for the session)
  finding: flashed `3.0.0b25` to `/dev/ttyACM1` via `FirmwareManager._install_with_avrdude` (the
    REAL production install path, not a hand-rolled avrdude call) fed the `gh`-downloaded hex —
    4 separate flash cycles, immediate post-flash probe each time (closest match to the
    reporter's exact timing) — **0/4 reproductions**. 10 additional spaced/rapid probes against
    the same already-flashed b25 — **0/10 reproductions**. Total 14/14 clean against b25 on this
    board. Symmetric check: flashed `3.0.0b22` fresh (2 cycles) and probed immediately —
    **0/2 reproductions** — so "freshly flashed" alone isn't sufficient to trigger it on THIS
    board with EITHER firmware. Grand total across both firmware versions, both code states, idle
    and immediate-post-flash: **41/41 clean, zero spurious interleave observed.** avrdude here is
    7.1 vs. the reporter's 8.0 — a minor, unlikely-relevant environment difference, noted for
    completeness.

- timestamp: 2026-09-09T10:50:00Z
  source: live hardware, throwaway venv with the ACTUAL PUBLISHED `firestarter==3.0.0b36` wheel
    (`uv venv --python 3.11` + `pip install firestarter==3.0.0b36`) — removes the
    branch-vs-published confound the earlier runs carried (this branch's `__init__.py` reads
    `3.0.0b36` but is NOT the published wheel; diffed and confirmed the only drift is
    unrelated `transport_counters` instrumentation this branch added, entirely outside the
    `_probe_port` region being tested)
  finding: applying the IDENTICAL fix logic by hand to the published wheel's installed
    `serial_comm.py` (verified `py_compile` clean, diffed to confirm it matches the committed
    change) reproduces the same result as the branch build in both directions — several runs
    against b22 (post-fix) and the b25 flash-cycles above (pre-fix) all passed with the published
    artifact, ruling out "this only worked because it's the dev branch" as a confound.

- timestamp: 2026-09-09T11:05:00Z
  source: coordinator reopened the session — the FAILURE (needed the reporter's environment)
    and the CAUSE (an interleaved spurious frame ahead of the real ack) are separable, and the
    CAUSE can be manufactured deterministically on ANY attached hardware via `_probe_port`'s
    existing `fault_inject_outgoing` parameter (`serial_comm.py:809-814`, already wired into
    production code for the `dev fault-inject` tooling — no new production code needed to use
    it). A hook that returns `(b"\x00" * n) + real_frame` puts `n` minimal, syntactically-valid
    but empty COBS frames immediately ahead of the real command in ONE write. Traced through
    `rurp_communication_read_data`: a lone `0x00` byte is read as an immediate delimiter with
    `block_remaining==0` (no violation) and `has_last==False`, so it returns -1 ("empty frame,
    no CRC decoded") with the RX cursor already correctly positioned at the very next byte — no
    drain needed, no misalignment risk for the frame that follows in the same write. Each `-1`
    return routes to `firestarter.cpp`'s `else: LOG_ERROR_ID(MSG_ERR_EMPTY_INPUT)` catch-all.
    Board identity re-verified before use: same Uno R3 (serial 55736303739351B040E1),
    `/dev/ttyACM1`, firmware 3.0.0b25 (from the prior session's final flash).

- timestamp: 2026-09-09T11:10:00Z
  source: live hardware matrix, `SerialCommunicator._probe_port` called directly (no CLI
    involved) with `fault_inject_outgoing` set to the hook above, `.venv311` (the coordinator's
    prepared 3.11 venv)
  finding: **A — pre-fix (`31f3455~1`) + 1 injected bad frame: FAILURE.** Log ordering
    byte-for-byte matches the reporter's report: `ERROR: Empty input` -> `responded but not with
    OK: Empty input` -> (late) `OK: Ready` -> (late) `OK: FW: 3.0.0b25:uno` -> `PROBE_RESULT:
    FAILURE (None)`. This is the live reproduction that was missing all session.
    **B — post-fix (`b2546da`, single fixed retry) + 1 injected bad frame: SUCCESS.**
    `PROBE_RESULT: SUCCESS identity='3.0.0b25:uno'`, with the retry's own debug line visibly
    firing. Live GREEN for the original fix, on the exact class of input it targets.
    **C — post-fix (`b2546da`) + 2 injected bad frames: FAILURE.** The single fixed retry
    consumed the SECOND spurious `Empty input` (not the real ack), then gave up, reproducing the
    identical failure with two stray frames — exactly the shape the reporter's own log already
    showed (two `Empty input` lines). This is the bound test the coordinator predicted would
    matter, and it failed as flagged: **the original fix (`31f3455`/`b2546da`) was under-built
    for more than one spurious frame.**
    **D — post-fix, no injection: SUCCESS**, x2, confirming the rig is unchanged from the
    prior session's 41/41 clean baseline.

- timestamp: 2026-09-09T11:20:00Z
  source: rework of `SerialCommunicator._probe_port` (`firestarter_app/firestarter/serial_comm.py`)
    per the coordinator's specified design — a wall-clock deadline
    (`SETUP_ACK_RECOVERY_TIMEOUT_S`) that keeps reading and discarding responses whose text is
    exactly `GENERIC_FRAME_DECODE_ERROR_TEXT`, returning the first response that is anything
    else — then the SAME A/B/C/D matrix re-run against it, plus a 3rd case
  finding: A/B/D unchanged (still fail/succeed/succeed respectively, as expected — the rework
    only changes behavior when the generic error text repeats). **C now SUCCEEDS**:
    `ERROR: Empty input` x2, then `OK: Ready`, `PROBE_RESULT: SUCCESS`. A bonus **3-injected-bad-frame
    case also SUCCEEDS** (not required by the matrix, tried because the deadline design should
    generalize beyond the observed count of two) — `ERROR: Empty input` x3, then `OK: Ready`,
    success. The rework is confirmed live-hardware-correct, not just argued to be more robust.

- timestamp: 2026-09-09T11:30:00Z
  source: `tests/test_probe_spurious_setup_ack.py`, extended with a 2-frame case, run against
    both fix versions
  finding: the new 2-frame test FAILS against the pre-rework fix (`b2546da`) —
    `assert comm is not None` -> `AssertionError: assert None is not None` — and PASSES against
    the reworked fix. The existing 1-frame and negative-control tests are unaffected by the
    rework (still pass). Full suite re-run on `.venv311`: 2238 passed, 0 failed. `ruff check` /
    `ruff format --check`: clean. `tools/check_mypy_watermark.py`: 35/35, unchanged (not
    regressed). Committed as `8b3d8f9`.

- timestamp: 2026-09-09T11:45:00Z
  source: secondary/optional task — raw byte capture across DTR-reset cycles and immediately
    after an `avrdude` flash, using a plain `pyserial` open (no `firestarter` parsing layer) to
    see genuinely-emitted noise the app's own parser would otherwise silently discard
  finding: NOT a null result. **A single byte, value `0xf0`, appeared in every one of 8
    independent captures** — 5 plain open/close (DTR-reset) cycles with no flash in between,
    plus 3 more immediately after a fresh `avrdude` flash — each capture window 3-5 seconds,
    each showing EXACTLY one byte, EXACTLY `0xf0`, nothing else. This is reproducible and
    deterministic on THIS board, not random noise (random electrical noise would not be
    byte-value-identical across 8 independent trials). Traced through the decoder: a lone
    `0xf0` byte (not `0x00`) is read as a COBS run-code claiming `block_remaining = 0xEF = 239`
    more data bytes; with nothing else arriving, `rurp_communication_read_data`'s mid-frame
    inter-byte deadline (`TIMEOUT_MS = 1000` ms) eventually fires, drains (finds nothing to
    drain, buffer already empty) and returns -1 -- ALSO routing to `MSG_ERR_EMPTY_INPUT`. This
    means the FIRST "Empty input" in the reporter's report (the one that appears BEFORE
    "Sending command to programmer" in their log) is now explained by a directly-observed,
    reproducible artifact on real Uno-class hardware, not merely inferred. Its ~1-second
    resolution window comfortably completes within this host's 2.0s `CONNECTION_STABILIZE_DELAY`
    plus 0.5s pre-send drain, which is exactly why it does NOT interfere with a normal
    (non-injected) probe on THIS board — consistent with the 41/41 clean natural-probe baseline
    from the prior session. BOUNDARY, stated honestly: the ultimate origin of this byte (AVR
    UART start-bit sampling glitch during the DTR-triggered reset transition vs. a bootloader
    artifact vs. something else) was not further isolated — that was explicitly out of scope
    ("a null result here is fine and expected"; a POSITIVE result was found instead and is
    reported as far as it was characterized, not further chased). This finding corroborates
    that this board genuinely does emit spurious pre-command bytes on reset — it does not by
    itself reproduce the reporter's exact SECOND, post-send interleave (that required deliberate
    injection, per the A/B/C/D matrix above), and is offered as supporting evidence, not as a
    second independent proof.

## Eliminated

- hypothesis: The app mis-sorted firmware releases and picked an old firmware (e.g. string-sorted
  b25 above a nonexistent newer one).
  why: 3.0.0b25 IS the newest published firmware release. Verified with `gh release list`.

- hypothesis: App b36 and firmware b25 are a version skew (b36 >> b25) and the app expects a
  newer firmware than exists.
  why: app and firmware carry independent beta counters and were released ~1h apart on
  2026-09-02. They are the intended matched pair.

- hypothesis: The post-flash failure is a framed-vs-line-based protocol-generation mismatch.
  why: firmware tag 3.0.0b25 carries the COBS framing surface, as does the beta app. Both speak
  the framed protocol. (NOT eliminated for the PRE-flash `Bad JSON`, where the board's firmware
  version is unknown.)

- hypothesis: The forced flash silently failed or targeted the wrong MCU.
  why: avrdude 8.0 ran `-p atmega328p -c arduino` and completed in 8.23s with the host reporting
  "Firmware successfully updated"; avrdude's part-signature check is a real gate and it passed.

- hypothesis: (SEEDED) The command frame's leading bytes are lost because the host writes into
  a still-booting/bootloader-resident MCU — `consume_remaining_input()` "drains nothing" because
  the board hasn't booted yet.
  why: `CONNECTION_STABILIZE_DELAY` is 2.0s and firmware boot is ~100ms (fixed `delay(50)` in
  `rurp_serial_begin` plus ordinary `setup()` work) — a ~20x margin. The board is fully booted
  and has been idling in `loop()` for ~1.9s before the host ever sends. There is no
  still-booting window for the command's leading bytes to land in. Additionally, the confirmed
  mechanism (below) shows the REAL ack is not "lost" at all — it is correctly generated and
  sent by the firmware, just consumed too late by the host after an interleaved spurious frame.
  The seed's failure MODE (Uno-class, reset-adjacent) survives; its specific MECHANISM does not.

- hypothesis: The b22-vs-b25 outcome asymmetry the coordinator flagged (this Uno probes cleanly
  25/25 on b22; the reporter's Uno fails every time on b25) is a firmware code regression
  introduced somewhere in the b23/b24/b25 window.
  why: `firestarter_uno.hex` for b23, b24 and b25 is compiled-byte-identical except a one-line
  embedded version string — there is no code for a regression to live in across that whole
  range. b22->b23's actual code delta is comment-only in every file the CMD_FW_VERSION probe
  path touches, plus one unrelated struct-field narrowing (`handle->protocol`/`ctrl_flags`,
  never read on this path) and a large but entirely memory-operation-scoped set of changes
  (`eprom.cpp`, `eeprom_28c.cpp`, `json_parser.c` field-table refactor, etc.) that
  `parse_json` never reaches for CMD_FW_VERSION. Also: 41/41 live probe attempts against BOTH
  b22 and b25 on real Uno hardware, including immediately-post-flash, were clean — no live A/B
  difference was actually observed once tested directly (the earlier apparent asymmetry was
  reporter-vs-this-board, not b22-vs-b25 under matched conditions).

## Resolution

root_cause: A generic-catch-all/host-read-ordering compound defect, confirmed independent of
  hardware access:
  (1) Firmware category: `firestarter.cpp`'s `loop()` reuses `MSG_ERR_EMPTY_INPUT` for every
      CMD_IDLE COBS-decode failure — genuinely-empty read, CRC mismatch, COBS violation, AND
      read/inter-byte underrun all collapse into the identical "Empty input" text (source
      comment, `firestarter.cpp:253-255`), so the host cannot tell "nothing arrived" from "a
      transient framing glitch happened."
  (2) Host category: `SerialCommunicator.expect_ack()` / `_probe_port` treat the FIRST
      OK/ERROR response after sending the setup command as final and authoritative, with no
      check for whether a better (correct) response is already queued immediately behind it.
  AND-gate: yes — category (1) alone is cosmetic (an ambiguous error string); category (2)
  alone would be harmless if firmware never emitted an unsolicited frame between a sent command
  and its ack. It takes BOTH together — an ambiguous, reusable error text AND a host that
  never looks past the first response — to turn a transient, self-recovering firmware glitch
  into a permanent probe failure. The most parsimonious source of the interleaved spurious
  frame is the Uno-class PORTD pin-sharing hazard this codebase already documents twice
  elsewhere (PD1/TX garbage mitigated by `PREFIX_REGEX`'s rightmost-match design; PD0/RX
  startup garbage mitigated, but only at the boot/mode-transition instant, by
  `rurp_set_communication_mode()`) — consistent with, but not proven by hardware access this
  session lacked. The exact electrical trigger for the SPECIFIC double "Empty input" the
  reporter saw is NOT independently confirmed on real Uno hardware; what IS confirmed,
  hardware-free, is that the host's read-first-response behavior is sufficient by itself to
  turn any such interleaved spurious frame into the reported permanent, self-sustaining probe
  failure (evidence entry 2026-09-09T09:58:00Z).
  The PRE-flash `Bad JSON` symptom is UNRELATED and BENIGN: confirmed (not merely plausible) by
  reading the actual pre-Phase-51 firmware logic COBS framing replaced — it is the expected,
  correct failure mode for firmware old enough to predate COBS framing entirely, talking to a
  COBS-only host. Not a defect; no fix needed or applied for it.

fix: `firestarter_app/firestarter/serial_comm.py` — `SerialCommunicator._probe_port`.
  **REWORKED once, on live-hardware evidence (matrix leg C — see below).**
  Original shape (`31f3455`, renamed by the coordinator in `b2546da`): after sending the setup
  command, if `expect_ack()`'s first response was exactly the generic frame-decode-failure text
  (`MSG_ERR_EMPTY_INPUT`'s catalog format string, read from `CATALOG` rather than hardcoded so
  it can't silently drift from the firmware's own text), gave the exchange ONE additional
  `expect_ack()` call bounded at `SETUP_ACK_RECOVERY_TIMEOUT_S = 2.0s`. Live-hardware matrix leg
  C (2 injected spurious frames) proved this was under-built: the fixed single retry consumed
  the second spurious frame, and the genuine ack — one read further behind — was missed again.
  Current shape (`8b3d8f9`): the same trigger condition (first response is exactly the generic
  text) now opens a wall-clock deadline (`time.time() + SETUP_ACK_RECOVERY_TIMEOUT_S`), and a
  loop keeps calling `expect_ack(timeout=remaining)` — discarding ONLY responses whose text is
  exactly that generic string — until either a different response arrives (a real OK, or a
  specific error) or the deadline is exhausted. Strictly more robust than the fixed retry and no
  more permissive: a genuine, unrelated, specific rejection (pre-COBS `Bad JSON`, a real
  hardware-revision refusal, a real `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`) still fails immediately
  on its first appearance, and total wait time is still bounded by the same constant. Scoped to
  `_probe_port` only (not a global `expect_ack()` change) for the same reason as before —
  CMD_FW_VERSION never engages VPP/VPE (evidence entry 2026-09-09T10:02:00Z), so retrying here
  is hazard-free, whereas `expect_ack()` is also used mid-operation where masking a real error
  could be dangerous. No firmware change made — none was needed or found (see the source-diff
  evidence below); the raw-byte-capture evidence explains the mechanism's precondition but
  changes nothing about where the fix belongs.

verification: Hardware-free, host-only, CONFIRMED:
  - New regression test `firestarter_app/tests/test_probe_spurious_setup_ack.py` replays the
    reporter's exact frame ordering via a `_FakeSerial`. RED verified first (test failed against
    the unmodified code, reproducing "probe returns None" exactly as reported — fix patch was
    reverted, test run, patch reapplied). GREEN verified after the fix (probe now returns a
    connected communicator). A negative-control test in the same file confirms a genuine,
    non-recoverable error still correctly fails the probe (the fix does not mask real errors).
  - `ruff check` and `ruff format --check` clean on both changed files.
  - `mypy` clean on `serial_comm.py` (one of the eight modules under the repo's strict-mypy
    island per this repo's CLAUDE.md).
  - Full existing `serial_comm`-adjacent suites (`test_fwguard.py`, `test_hw_revision_gate.py`,
    `test_protocol_not_implemented*.py`, `test_serial_characterization.py`, `test_decoder.py`,
    `test_characterization.py`, `test_bug_characterization.py`) — 122 passed, 0 failed.
  - Full `pytest tests/` run — **2249 passed, 0 failed, 1 pre-existing unrelated deprecation
    warning** (Click's `MultiCommand`, in `test_click_group_gate_hook.py`, untouched by this
    fix), 622.94s.
  All of the above ran under a python3.11 venv (`uv venv --python 3.11`), matching this repo's
  CI reality (app CI is 3.11-only; the devcontainer's default 3.12 has previously masked broken
  CI per project history).
  Real Uno-class hardware — an Arduino Uno R3 was attached mid-session (vid 0x2341 pid 0x0043,
  confirmed independently via `serial.tools.list_ports`, not just trusted from the coordinator's
  message; on `/dev/ttyACM1`, NOT `/dev/ttyACM0` — the Leonardo had stopped enumerating).
  Cheapest zero-risk leg first, per instruction: probe-only, no flash, against whatever firmware
  was already on the board. That firmware turned out to be **3.0.0b22** (read cleanly via the
  probe itself: `OK: FW: 3.0.0b22:uno`) — an older COBS-era firmware than the reporter's b25,
  left over from prior bench work, NOT the reporter's exact firmware.
  Ran `firestarter -v fw --port /dev/ttyACM1` repeatedly: 20 runs against the UNMODIFIED
  (pre-fix, `HEAD~1`) code (10 with 1s spacing, 10 back-to-back) plus 5 runs against the FIXED
  (HEAD, committed) code — 25/25 clean, zero spurious `Empty input` interleave observed either
  way (b22, idle-board leg).

  Operator then granted a standing flash authorization for the rest of the session (socket
  confirmed empty). Escalated per instruction: flashed the reporter's exact firmware, 3.0.0b25
  (downloaded via authenticated `gh release download` after the unauthenticated
  `api.github.com` core rate limit had been exhausted by earlier probing — confirmed via
  `curl .../rate_limit`), through `FirmwareManager._install_with_avrdude` (the real production
  install path). Ran the reporter's tight flash-then-probe sequence repeatedly: 4 separate
  flash-then-immediately-probe cycles (closest match to the reporter's exact timing) plus 10
  more spaced/rapid probes against the same flash — 14/14 clean. Symmetric check with a fresh
  b22 flash (2 cycles, immediate probe) — 2/2 clean. **Grand total: 41/41 clean across both
  firmware versions, both code states (pre-fix/post-fix), idle and immediate-post-flash
  conditions — zero reproductions of the spurious interleave on this specific Uno R3.**

  To remove the branch-vs-published confound, the decisive runs above were repeated against a
  throwaway `uv venv --python 3.11` running the ACTUAL PUBLISHED `firestarter==3.0.0b36` wheel
  (not this branch's editable install, which happens to share the same version string but is
  NOT the published artifact), with the identical fix hand-applied to that wheel's installed
  `serial_comm.py` for the post-fix half of the comparison. Same result: clean throughout.

  Source archaeology (evidence entries 2026-09-09T10:35:00Z and 10:38:00Z) independently and
  more strongly settles the "is this a firmware regression" question the live A/B could not:
  `firestarter_uno.hex` for b23/b24/b25 is compiled-byte-identical (one version-string line
  differs); b22->b23's real code changes are comment-only across every file the CMD_FW_VERSION
  probe path touches, plus one unrelated struct-narrowing commit and a large but
  memory-operation-only set of changes this probe command never reaches. There is no firmware
  code regression to bisect toward, and none was found, so none was fixed.

  STATUS AS OF THE FIRST PASS (superseded by the matrix below, kept for the record): a genuine,
  sustained non-reproduction under NATURAL conditions — not a confirmation and not a refutation.
  The fix's retry branch had never been exercised on real hardware.

  **RESOLVED by separating the FAILURE from the CAUSE.** The reporter's environment was needed
  to reproduce the failure NATURALLY (a noisy USB bridge triggering it on its own), but the
  CAUSE — an interleaved spurious `MSG_ERR_EMPTY_INPUT` frame ahead of the genuine ack — can be
  manufactured deterministically on ANY attached hardware via `_probe_port`'s existing
  `fault_inject_outgoing` parameter (already-shipped production code, used here with zero
  production-code changes to exercise it). Live matrix, this same Uno R3, firmware 3.0.0b25:
    - **A (pre-fix + 1 injected bad frame): FAILURE**, log ordering byte-for-byte identical to
      the reporter's report — the live RED that was missing.
    - **B (post-fix, single-retry version + 1 injected bad frame): SUCCESS** — live GREEN.
    - **C (post-fix, single-retry version + 2 injected bad frames): FAILURE** — the fix was
      under-built for more than one spurious frame, exactly as the reporter's own log (which
      shows two "Empty input" lines) already implied was possible.
    - **D (post-fix, no injection): SUCCESS x2** — rig unchanged from the 41/41 baseline.
  C forced a rework: the fix is now a wall-clock deadline (`SETUP_ACK_RECOVERY_TIMEOUT_S`,
  unchanged value, 2.0s) instead of a fixed one-retry count, discarding any number of the exact
  generic error text within that bound. Re-ran A/B/C/D against the rework: A/B/D unchanged, **C
  now SUCCEEDS**, and a bonus 3-injected-bad-frame case also succeeds (the design generalizes
  past the specific count of two that was tested). This is now genuinely **live-hardware-verified**,
  not argued by analogy or left as an untested inference.

  Additionally (secondary/optional task, not required for the above): a raw-byte capture across
  8 independent DTR-reset-and-immediate-post-flash cycles caught a reproducible single stray
  byte (`0xf0`) on THIS board every single time, corroborating that Uno-class hardware genuinely
  does emit spurious pre-command bytes around reset — independent evidence for the mechanism's
  precondition, though its precise electrical origin was not further isolated (out of scope) and
  it does not, by itself, reproduce the reporter's exact post-send double-interleave (that
  required deliberate injection).

  Source archaeology (unchanged from the first pass) still conclusively excludes a nameable
  firmware code defect in the b22-b25 range — `firestarter_uno.hex` for b23/b24/b25 remains
  compiled-byte-identical, and b22->b23's real code changes remain comment-only across every
  file the CMD_FW_VERSION probe path touches. No firmware fix was needed or made.

  REMAINING, HONESTLY: the reporter's OWN exact environment (their specific USB-to-serial bridge
  chip/revision, host OS/driver, avrdude 8.0) was never reproduced or tested — only the
  documented FAILURE MODE was manufactured and cured. This is the strongest verification
  achievable without that exact hardware, and is materially stronger than the first pass: the
  fix's own retry/deadline logic has now actually executed and been observed succeeding and
  failing (before the rework) on physical Uno-class hardware, not only against a `_FakeSerial`.

  Bench left in a stated, working condition: Arduino Uno R3 on `/dev/ttyACM1`, flashed to
  firmware **3.0.0b25** (the current published/newest firmware) as the final resting state.

files_changed:
  - firestarter_app/firestarter/serial_comm.py (commits `31f3455`, `b2546da` [coordinator's
    rename, not this session's], `8b3d8f9` [this session's rework])
  - firestarter_app/tests/test_probe_spurious_setup_ack.py (commits `31f3455`, `8b3d8f9`)
