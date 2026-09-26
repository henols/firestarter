---
status: resolved
trigger: "the real issue of not being able to measure the voltages is the timeout and that is the blocker"
created: 2026-06-30
updated: 2026-06-30
phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
milestone: v1.18
constraint: "DIAGNOSTIC PHASE — no firmware/host source edits (SAFE-01). Code RCA + non-invasive unblock only; source fix deferred to Phase 98."
resolution: "H1 (DTR-reset-on-close drops the latched rail). Non-invasive unblock: hold_rail.py (port held open). H2 disproven (0x188->physical 0x89 asserts P1). Proper fix deferred to Phase 98 (host --hold-seconds/dtr=False or fw non-blocking hold-mode)."
hardware_isolation: "Debugger has NO bench hardware and NO operator. Live verification is orchestrator-only."
---

# Debug: held-rail `dev reg -f` timeout blocks DMM measurement

## Symptoms

- **Expected:** `firestarter dev reg 0 0 0x188 -f` holds the VPP program-window rail
  (regulator + VPE-drop + P1-route, address 0) steadily at socket pin 1 so the
  operator can DMM pin 1 (VPP) and pin 31 (PGM/A18). Per v1.14 reference, the
  `dev reg … -f` idiom is the held-rail static proxy for DMM reads.
- **Actual:** the command prints `ERROR: Command 8 timed out` (COMMAND_DEV_REGISTERS=8)
  almost immediately, and the operator's DMM reads **nothing (~0V)** at the socket —
  no measurable held voltage. Operator asserts the timeout is the blocker.
- **Error:** `ERROR: Command 8 timed out`
- **Timeline:** Hit during the v1.18 Phase-97 AM27C020 RCA bench session (Leonardo +
  RURP Rev 2.0, fw 3.0.0b10 / bccd995). The irreversible write attempt already
  succeeded (RCA-01 reproduced); only the supplementary held-rail pin-1/pin-31
  measurement is blocked.
- **Reproduction:** `firestarter dev reg 0 0 0x188 -f` on Leonardo /dev/ttyACM0,
  then try to DMM socket pin 1.

## Orchestrator pre-investigation (evidence already gathered)

- **Firmware** `dt_set_registers` ([firestarter/src/dev_tools.cpp:71-127]): reads 4
  bytes, sends `MSG_OK_READY`, calls `rurp_set_programmer_mode()`, writes
  LSB/MSB/CONTROL registers (**rail set here**), sets CE/OE, then
  **`while (!rurp_user_button_pressed()) delay(200)`** — busy-holds the rail until
  the physical user button is pressed, then `rurp_set_communication_mode()` + return.
- **Host** `dev_set_registers` ([firestarter_app/firestarter/eprom_operations.py:1454-1517]):
  `send_ack()` → `send_bytes(4)` → log "Register data sent." → **`expect_ack()`**
  (waits for a post-hold terminal ack the firmware only sends AFTER the button) →
  times out ("Command 8 timed out") → **`finally: _disconnect_programmer()`** closes
  the port.
- **Leading hypothesis (H1):** closing the serial port on disconnect toggles DTR and
  **resets the Leonardo**, rebooting the firmware and dropping the held rail before
  the operator can read. Tried `stty -F /dev/ttyACM0 -hupcl` (prevent reset-on-close);
  operator escalated to /gsd-debug before confirming a reading — result inconclusive.
- **Alternative hypothesis (H2):** the rail IS held but socket pin 1 genuinely reads
  ~0V because VPP is not routed to pin 1 — i.e. the measurement "nothing" is the
  actual RC-2 routing finding, not a tooling artifact. (Discriminator: pin 32 VCC
  should read ~5V if the board is alive while the rail is held.)
- The `vpp`/`vpe` **monitor** commands keep the port open for N seconds (no reset)
  and read fine — but they enable only the regulator for ADC measurement, NOT the
  P1-route (0x188), so they don't drive socket pin 1.

## Current Focus

status: RCA COMPLETE (diagnose-only). Root cause = H1 (tooling/DTR-reset-on-close).
  H2 (P1-route-lost) DISPROVEN by control-register decode. Rail IS held; the
  `_disconnect_programmer()` port-close resets the Leonardo and drops it.
next_action: none — return diagnosis to orchestrator. See Resolution.

## Evidence

- timestamp 2026-06-30: write -b attempt produced `retries: 20, bad bytes: 1` then a
  byte-identical N=3 post-read (chip pristine) — board serial path is otherwise
  healthy; the failure is specific to the held-rail static proxy UX.

- checked: serial open path `serial_comm.py:132-136`. found: port opened with
  `serial.Serial(port, baudrate, timeout)` and DEFAULT control-line handling — no
  `dsrdtr=`, no `rtscts=`, no explicit `dtr=`/`setDTR()`. implication: pyserial's
  default asserts DTR on open and DE-asserts on close. On the Leonardo (ATmega32u4
  native USB-CDC) a DTR transition triggers the Caterina bootloader/reset. This is
  the textbook "Leonardo resets when the port opens/closes" behavior.

- checked: `disconnect()` `serial_comm.py:473-484`. found: calls
  `self.connection.close()` with no DTR-hold guard. close() releases DTR → Leonardo
  reset. implication: the reset fires at port-close, i.e. exactly at
  `dev_set_registers` `finally: _disconnect_programmer()` (eprom_operations.py:1516-1517).

- checked: `dev_set_registers` `eprom_operations.py:1454-1517`. found: after
  `send_bytes(4)` it calls `expect_ack()` (default `DEFAULT_RESPONSE_TIMEOUT`). The
  firmware does NOT send a terminal ack until the user button is pressed (see fw
  evidence below). So `expect_ack` ALWAYS times out for a held rail → "Command 8
  timed out" → `finally: _disconnect_programmer()` → close() → DTR-reset → rail drops.
  implication: the timeout and the rail-drop are the SAME event chain; the timeout is
  not merely cosmetic — its `finally` is what kills the rail.

- checked: firmware `dt_set_registers` `dev_tools.cpp:71-127`. found: order is
  (1) `LOG_OK_ID_U16(MSG_OK_READY,...)` ack at line 107 — this is the ack the host's
  PRECEDING `expect_ack` would consume, but note the host code path: `send_ack()` →
  `send_bytes()` → `expect_ack()`. The fw sends OK_READY (line 107) BEFORE writing
  registers, but the host's single `expect_ack()` at 1511 is waiting AFTER send_bytes.
  (2) `rurp_set_programmer_mode()` line 108 → `rurp_serial_end()` — the UART is TORN
  DOWN, so any post-button ack cannot even reach the host until comms mode is restored.
  (3) writes LSB/MSB/CONTROL — **rail latched into the 74HC573 control register here**
  (lines 110-116). (4) CE/OE. (5) `while(!rurp_user_button_pressed()) delay(200)` —
  busy-holds, rail stays latched in the '573 (latch holds until rewritten or chip
  reset). (6) on button: `rurp_set_communication_mode()` restores UART, returns true.
  implication: the rail IS physically held for the entire button-wait. The ONLY way
  the host learns the loop ended is the post-button return; the host gives up first
  (expect_ack timeout) and closes the port → reset. RAIL CONFIRMED HELD until reset.

- checked: `rurp_set_programmer_mode` / `rurp_set_communication_mode`
  `uno_rurp_shield.cpp:96-100, 66-97` and the boot init at lines 56-63. found: board
  init writes CONTROL_REGISTER=0x00 (line 61) then enters communication mode. A reset
  therefore zeroes the control latch → rail = 0V. implication: a DTR-reset at port
  close re-runs init, which explicitly clears the rail to 0x00. This is the mechanism
  by which the operator's DMM reads ~0V.

- checked: H2 control-register decode. Host `-f 0x188` → firmware
  `ctrl_reg = (0x188 & 0x01FF) = 0x188`, firestarter_reg=1 (`dev_tools.cpp:83-86`).
  Remap via `rurp_map_ctrl_reg_for_hardware_revision` (rurp_hw_rev_utils.h:15-41,
  REVISION_2_0 arm, compiled with HARDWARE_REVISION so the canonical macros are the
  wide layout: VPE_DROP=0x100, P1=0x08, REG=0x80, A18=0x20, A16=0x01):
    • mask (A9|VPE|P1|A17|RW|REG)=0xDE → 0x188 & 0xDE = 0x88  (P1 0x08 + REG 0x80 survive)
    • 0x188 & VPE_DROP(0x100) = 0x100 → sets VPE_DROP_REV2 (0x01)
    • 0x188 & A16(0x01) = 0 ; 0x188 & A18(0x20) = 0
  → physical CTRL = 0x88 | 0x01 = **0x89 = REGULATOR + P1 + VPE_DROP_REV2**.
  implication: the P1-route bit (0x08) IS correctly asserted on Rev 2.0 — the
  CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2 aliasing (rurp_pinout.h:127) is
  NOT triggered because address-line-18 is only aliased onto P1 when A18(0x20) is set
  in the INPUT, and 0x188 does not set 0x20. So 0x188 does route VPP to socket pin 1.
  H2's "host value fails to assert P1" premise is FALSE.

## Eliminated

- hypothesis: H2 — the rail is held but socket pin 1 reads ~0V because the `-f 0x188`
  host value fails to assert the physical P1-route bit (CTRL_VPP_P1 / CTRL_ADDRESS_LINE_18
  aliasing on Rev2).
  evidence: control-register decode (above) — 0x188 remaps to physical 0x89 which
  includes P1 (0x08); the A18↔P1 alias is gated on input bit 0x20 which 0x188 does not
  set. P1-route is correctly asserted. The ~0V reading is fully explained by H1 (the
  port-close DTR-reset zeroes the latch before the operator can measure), so there is
  no residual signal that H2 needs to explain. H2 cannot be FULLY excluded as a
  *secondary* finding without a live measurement (a genuine pin-1 routing fault could
  coexist), hence the discriminating test below — but it is not the cause of the
  reported blocker (the timeout + ~0V), which H1 explains end-to-end.
  timestamp: 2026-06-30

## Resolution

root_cause: |
  H1 (TOOLING). The rail IS correctly set and physically latched in the 74HC573
  control register, but it is dropped before the operator can measure it because
  the host tears the serial port down.

  Mechanism (end-to-end):
  1. `dev_set_registers` (eprom_operations.py:1454-1517) connects, sends the 4
     register bytes, then calls `expect_ack()` (serial_comm.py:1511).
  2. The firmware `dt_set_registers` (dev_tools.cpp:71-127) latches the rail
     (lines 110-116) and then BUSY-WAITS in `while(!rurp_user_button_pressed())
     delay(200)` (line 121). It does NOT emit any post-setup ack until the
     button is pressed — and even then only after `rurp_set_communication_mode()`
     restores the UART (line 124). `rurp_set_programmer_mode()` at line 108 calls
     `rurp_serial_end()`, so the UART is DOWN for the whole hold.
  3. The host's `expect_ack()` therefore always hits `DEFAULT_RESPONSE_TIMEOUT`
     (=10 s, serial_comm.py:63) -> "ERROR: Command 8 timed out".
  4. The `finally:` block runs `_disconnect_programmer()` -> `comm.disconnect()`
     -> `self.connection.close()` (serial_comm.py:478).
  5. The port was opened with `serial.Serial(port, baudrate, timeout)` and NO
     DTR/RTS control (serial_comm.py:132-136). pyserial's default asserts DTR on
     open and de-asserts on close; on the Leonardo (ATmega32u4 native USB-CDC)
     that DTR transition resets the MCU (Caterina bootloader behavior).
  6. The reset re-runs board init, which writes CONTROL_REGISTER = 0x00
     (uno_rurp_shield.cpp:58) -> the latch is zeroed -> socket pin 1 reads ~0V.

  So the "timeout" and the "~0V" are one event chain: the timeout's `finally`
  closes the port, the close resets the Leonardo, and init zeroes the rail. The
  operator's claim ("the timeout is the blocker") is correct — the timeout itself
  is benign, but its `finally: _disconnect_programmer()` is what drops the rail.

  H2 (genuine pin-1 routing fault) is DISPROVEN as the CAUSE: the host `-f 0x188`
  decodes (via rurp_map_ctrl_reg_for_hardware_revision, REVISION_2_0 arm) to
  physical CTRL = 0x89 = REGULATOR(0x80) + P1(0x08) + VPE_DROP_REV2(0x01). The P1
  route IS asserted; the CTRL_VPP_P1 / CTRL_ADDRESS_LINE_18 alias is gated on input
  bit 0x20 (not set by 0x188). H1 fully explains the ~0V, so no residual evidence
  requires H2. (A real routing fault could still coexist — see discriminating test.)

  Why v1.14 `dev reg ... -f` "held an erase rail successfully": that bench session
  (see reference_v114_bench_erase_rail_and_test_artifact) almost certainly used a
  board/path that does NOT reset on port-close in the same way, OR the operator
  measured DURING the button-wait window before the CLI exited. On the Leonardo the
  native-USB DTR-reset on close is unavoidable with the default pyserial open — that
  is the differentiator from the v1.14 success.

fix: |
  DIAGNOSE-ONLY — no source edit applied (SAFE-01). Recommendations below.

  --- NON-INVASIVE UNBLOCK (orchestrator can do NOW, no source edit) ---
  Standalone scratchpad pyserial script that opens /dev/ttyACM0 with DTR held
  inactive across open AND keeps the port OPEN for a measurement window, so the
  board never resets and the latch is never re-zeroed.
    1. Open without resetting the Leonardo:
         import serial, time
         s = serial.Serial()
         s.port = "/dev/ttyACM0"; s.baudrate = 250000; s.timeout = 2
         s.dtr = False; s.rtscts = False; s.dsrdtr = False
         s.open(); s.dtr = False     # re-assert inactive post-open (belt+braces)
         time.sleep(2.0)             # CONNECTION_STABILIZE_DELAY equivalent
       (Alternatively pre-arm once: `stty -F /dev/ttyACM0 -hupcl` so close() does
        not drop DTR — but the script avoids the OPEN reset too and is preferred.)
    2. FW-version handshake is OPTIONAL on this manual path; go straight to cmd 8.
    3. Send the dev-register COMMAND frame (COBS+CRC8, baud 250000). There is NO
       frame-start sentinel — the real send path (serial_comm.py:190-191) is
       `cobs_encode(json+crc8) + b"\x00"`. The `#` prefix in the cobs_encode
       docstring (frame_parser.py:67) is STALE/unused.
         json_bytes = b'{"cmd":8,"flags":0}'        # compact ascii, no spaces
         crc = crc8_ccitt(json_bytes)               # poly 0x07, seed 0x00 (frame_parser.py:36-57)
         frame = cobs_encode(json_bytes + bytes([crc])) + b"\x00"
         s.write(frame); s.flush()
    4. Read until firmware OK_READY (emitted at dev_tools.cpp:107 right after parse,
       BEFORE programmer mode). Then send the plaintext ACK and the RAW 4-byte
       register payload (NOT COBS-framed — raw, per send_bytes eprom_operations.py:1500-1509):
         s.write(b"OK"); s.flush()                  # send_ack (plaintext, serial_comm.py:451)
         # payload = [msb, lsb, (0x80 if firestarter else 0)|(ctrl>>8 & 1), ctrl & 0xFF]
         # For `-f 0x188`: msb=0x00, lsb=0x00, byte3=0x80|((0x188>>8)&1)=0x81, byte4=0x88
         s.write(bytes([0x00, 0x00, 0x81, 0x88])); s.flush()
       Firmware now latches physical CTRL=0x89 and busy-waits on the button — rail HELD.
    5. MEASUREMENT WINDOW: do NOT read the terminal ack, do NOT close.
         time.sleep(60)   # or input("Enter when done")
       Port stays open, DTR stays inactive, Leonardo does NOT reset, '573 holds the
       rail. Operator DMMs socket pin 1 (VPP) and pin 31 (PGM/A18) during this window.
    6. Release: press the physical button to end the fw loop, OR run another
       dev-register cycle with CTRL=0x00 then close. (Closing alone resets the board,
       which also zeroes the rail — acceptable teardown.)
    Baud 250000; dtr=False/dsrdtr=False so neither open nor the window resets the board.

  --- PROPER PHASE-98 SOURCE FIX (named, not applied) — recommend BOTH ---
  (a) HOST `--hold-seconds N` on `firestarter dev reg`: when set, after send_bytes
      the host SKIPS the blocking `expect_ack()`, `time.sleep(N)` with the port held
      open, then writes a clean CTRL=0x00 and closes. Pair with opening the
      SerialCommunicator with dtr=False/dsrdtr=False so neither open nor close resets
      the Leonardo. Removes the timeout AND the reset-on-close from the held-rail UX.
      Files: eprom_operations.py:dev_set_registers + serial_comm.py:__init__ (add
      dtr/dsrdtr params) + cli_handlers.py dev reg option.
  (b) FIRMWARE dev "hold mode": a dev sub-op that latches the rail and returns
      immediately (emit MSG_OK_READY) WITHOUT the `while(!button)` busy-wait, plus a
      paired "release" op writing CTRL=0x00. Lets the host hold the rail across
      commands on one open port and removes the un-ackable button-wait/comms-teardown.
      File: dev_tools.cpp (new dt_hold_registers / dt_release variant).
  Host (a) alone unblocks the operator UX with no firmware reflash; (b) is the
  cleaner long-term protocol shape.

verification: |
  Not verified live (diagnose-only; orchestrator owns the bench + operator).

  DISCRIMINATING TEST (H1 vs any residual H2) — run live with the rail HELD via the
  scratchpad script's measurement window (board NOT reset):
    * DMM socket pin 32 (VCC) reads ~5V  -> board ALIVE, latch held => H1 not acting
      in the window. THEN read pin 1:
        - pin 1 ~12-13V (VPP)             => rail held AND routed: pure H1 (the
          original ~0V was the port-close reset; held window reads fine).
        - pin 1 ~0V while pin32 ~5V       => GENUINE pin-1 routing fault (residual
          H2 / RC-2): rail held but not reaching pin 1.
    * DMM pin 32 ~0V during the window    => board reset anyway (DTR not held low);
      pure H1 — fix the open-path DTR handling (post-open re-assert / stty -hupcl).
  Fastest no-script confirmation that close-not-set drops the rail: run
  `firestarter dev reg 0 0 0x188 -f`; the instant it prints the timeout, watch an
  LED/scope on the rail — voltage present for ~10 s (the expect_ack window) then
  collapsing exactly when the CLI process exits confirms H1 (the close, not the set).

files_changed: []
