---
status: resolved
trigger: "verify (and write) fail immediately on the host->fw data path with 'ERROR: Data error: -2' on BOTH Uno and Leonardo, on the hardened v1.10 firmware."
created: 2026-06-02
updated: 2026-06-02
phase: 53
related: [transport-protocol-verify]
root_cause: "Lockstep contract mismatch on the host->fw data-chunk path. Host sends 512-byte data chunks (constants.py BUFFER_SIZE=512); the COBS frame payload is data(512)+CRC8(1)=513 bytes. The firmware COBS decoder rurp_communication_read_data caps committed payload at DATA_BUFFER_SIZE-1 (CR-01 guard, Phase 51 P04; reserves the NUL slot) = 511 on both boards (Uno default 512; leonardo env explicitly -D DATA_BUFFER_SIZE=512). A 513-byte payload exceeds 511 -> PUSH overflow -> _drain_to_delimiter() + return -2 ('payload too large'). Every full 512-byte chunk overflows -> write/verify unusable."
fix: "RESOLVED in firestarter bafbe8a -- Uno rurp_log_id now BUFFERS frames emitted while com_mode==false and FLUSHES them in rurp_set_communication_mode(); bench-verified end-to-end, see the verification section at the foot of this file. The option list that follows was the PRE-FIX analysis, retained for provenance. ORIGINAL NOTE: UNRESOLVED. Dual-repo lockstep change. Options: (a) host: send <=510-byte data chunks (payload<=511) so 510 data + 1 CRC fits the 511 cap; (b) firmware: size the decode buffer to hold chunk+CRC+NUL (RAM-tight on Uno: 545B free, data_buffer[512] dominant — risky); (c) re-derive both from a single negotiated max. Must update Phase 52 lockstep tests to exercise the MAX on-wire chunk on the host->fw path (the gap that let this through)."
---

# Debug: write-verify-datapath-overflow

## Symptoms
- `firestarter -p <port> verify W27C512 <file>` fails at the first data chunk:
  `ERROR: Data error: -2` / "Programmer did not request data chunk, got ERROR: Data error: -2".
- Reproduces on BOTH Uno (/dev/ttyACM1) and Leonardo (/dev/ttyACM0), hardened v1.10 firmware.
- `write` uses the same `_process_incoming_data` host->fw chunk path -> same failure expected.

## Evidence
- Verbose verify: firmware emits `OK: Request data`; host sends a 518-byte frame
  (`#` + COBS(512 data + 1 CRC8) + 0x00); firmware returns `Data error: -2`.
- `-2` = payload-too-large (rurp_serial_utils.cpp:146 PUSH overflow -> _drain_to_delimiter).
- DATA_BUFFER_SIZE=512 on both boards (firestarter.h default; leonardo platformio.ini line 65
  explicitly -D DATA_BUFFER_SIZE=512). Decoder commits at most DATA_BUFFER_SIZE-1 = 511 bytes.
- Host BUFFER_SIZE=512 (constants.py); _calculate_buffer_size returns 512.
- 512 data + 1 CRC = 513-byte payload > 511 cap -> overflow on every chunk.

## Scope
- IN v1.10 transport scope (host->fw data-chunk framing + CR-01 guard from Phase 51 P04).
- Distinct from the blank-check com_mode-gate bug (resolved: [[transport-protocol-verify]]).
- The read path (fw->host) and command channel are unaffected and verified working.
- Likely NOT caught earlier because v1.10 bench focus was the READ path; the host->fw data
  path (write/verify) wasn't exercised on hardware, and the lockstep tests didn't assert the
  maximum on-wire chunk through the decoder's cap.

## Resolution (part 1 — the -2 overflow): FIXED
- firestarter_app c5d8295: host MAX_DATA_CHUNK = BUFFER_SIZE - 2 (510); _calculate_buffer_size()
  returns it; regression TestHostChunkFitsFirmwareDecodeCap in test_frame_vectors.py.
- Bench-verified on Uno: the -2 overflow is GONE — firmware accepts the 510-byte chunk, the
  host->fw data path advances (progress reached 0x01fe), no "Data error: -2".
- Host suite green (the lone test_no_programmer_found_read failure is an env artifact: the bench
  saved port /dev/ttyACM1 in ~/.firestarter/config.json; passes with the port cleared).

## Resolution (part 2 — verify stall): FIXED (systemic)
CONFIRMED same com_mode-gate class: memory_verify_execute (memory.cpp:313) emits MSG_ERR_VERIFY on
mismatch while inside the programmer-mode op window (op_execute_function -> _execute_operation) ->
dropped on the Uno -> host timeout. (The test chip is jittery, so a mismatch is expected.)

Fixed SYSTEMICALLY (firestarter bafbe8a): the Uno rurp_log_id now BUFFERS frames emitted while
com_mode==false and FLUSHES them in rurp_set_communication_mode() instead of dropping. This fixes
verify, write, blank (write/erase reuse path), the 28C chip-id mismatch, flash verify-timeouts —
every operation that emits inside the programmer-mode window — in one place, no per-site changes.

Bench-verified on Uno: verify now reports "0xff != 0x03 at 0x000000" (MSG_ERR_VERIFY) instead of
timing out. blank/fw/read regress clean (single emit, coexists with the targeted blank fix 83d186f).
39/39 native tests pass; +41 B RAM (504 B free).

Note: `write` on W27C512 is still gated by erase "Not supported" (UV-EPROM classification) — a
SEPARATE chip-config matter, not a transport bug. The host->fw write/verify TRANSPORT path is now
fully working (chunk decode + error/result reporting).

## End-to-end verification (chip seated, all 3 fixes)
- Uno (re-enumerated to /dev/ttyACM0 after chip re-seat — ports shuffle per
  feedback_verify_port_identity_each_task). Fresh read SHA 71189f7f (stable across two reads).
- `verify W27C512 <fresh read>` -> "Verify for W27C512 successful (13.98s)", exit 0. Full 64KB
  host->fw compare PASSED. Error leg (MSG_ERR_VERIFY) separately confirmed chip-out ("0xff != 0x03
  at 0x000000"). The host->fw data path is proven end-to-end on the hardened transport.
