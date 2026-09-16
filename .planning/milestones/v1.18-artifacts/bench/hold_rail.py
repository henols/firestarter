#!/usr/local/bin/python3.12
"""Phase-97 held-rail static proxy — keeps the serial port OPEN so the Leonardo
does NOT reset, holding a control-register rail steady for operator DMM reads.

Root cause this works around (debug session held-rail-dev-reg-timeout):
`firestarter dev reg … -f` sets the rail correctly, but the host's
`expect_ack()` times out (firmware busy-waits on the user button) and the
`finally: _disconnect_programmer()` CLOSES the port. pyserial de-asserts DTR on
close → resets the ATmega32u4 → the 74HC573 control latch zeroes → pin 1 ≈ 0V
before the operator can measure. By holding the port open for the whole window
(and never pressing the button), the rail stays latched and measurable.

NOT a source edit: this is a .planning/ bench diagnostic, reusing the installed
firestarter framing. The proper fix (host --hold-seconds / dtr=False, or a
firewmare non-blocking dev hold-mode) is deferred to Phase 98.

Usage:  python3 hold_rail.py [CTRL_HEX] [HOLD_SECONDS]
        CTRL defaults to 0x188 (REGULATOR 0x080 + VPE-drop 0x100 + P1-route 0x008,
        host -f namespace → physical CTRL 0x89 on Rev 2.0). HOLD defaults to 120s.
Cleanup: on exit (normal, Ctrl-C, or kill) the port closes → board resets →
        rail clears to 0x00. No rail is left energized.
"""
import sys
import time
import logging

from firestarter.serial_comm import SerialCommunicator
from firestarter.config import ConfigManager
from firestarter.constants import COMMAND_DEV_REGISTERS

logging.basicConfig(level=logging.INFO, format="%(message)s")

CTRL = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x188
HOLD = int(sys.argv[2]) if len(sys.argv) > 2 else 120

# Mirror dev_set_registers firestarter=True payload:
#   [msb, lsb, (0x80 | (ctrl>>8 & 0x01)), ctrl & 0xFF]
payload = bytes([0x00, 0x00, 0x80 | ((CTRL >> 8) & 0x01), CTRL & 0xFF])

comm = None
try:
    config = ConfigManager()
    comm = SerialCommunicator.find_and_connect(
        {"cmd": COMMAND_DEV_REGISTERS, "flags": 0}, config
    )
    comm.send_ack()
    n = comm.send_bytes(payload)
    print(
        f"\n>>> RAIL HELD: CTRL=0x{CTRL:03X}  payload={payload.hex()}  ({n} bytes sent)\n"
        f">>> Port stays OPEN for {HOLD}s — board will NOT reset. MEASURE NOW:\n"
        f">>>   pin 32 (VCC)  expect ~5V  (alive => no reset)\n"
        f">>>   pin 1  (VPP)  expect ~13V (P1 route asserted)\n"
        f">>>   pin 31 (PGM/A18) expect ~0V\n"
        f">>> (no button press needed; rail clears on exit)\n",
        flush=True,
    )
    time.sleep(HOLD)
finally:
    if comm is not None:
        print(">>> releasing rail (closing port → board resets → CTRL=0x00)", flush=True)
        comm.disconnect()
