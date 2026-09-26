---
status: resolved
trigger: "write fails on Leonardo with \"Empty input\" (MSG_ERR_EMPTY_INPUT 0xA4) — overloaded COBS/CRC bad-frame error on the write-data chunk during MAIN; reproduces on b8/b8 across 100B/37KB/64KB files; regression vs Phase-54 EVEN-01 baseline"
created: 2026-06-17
updated: 2026-06-17
related: [write-verify-datapath-overflow]
root_cause: "NOT a COBS/CRC transport fault. The default (blank-check-enabled) write path runs mem_util_blank_check as a multi-step sub-step of the write's INIT phase (eprom_write_init, eprom.cpp:108-109). For each 2048-byte chunk the firmware emits MSG_DATA_PROGRESS (memory.cpp:457, `DATA: N/65536`). The host (_handle_progress_response, eprom_operations.py:380) ACKs every DATA frame, but the firmware in-progress INIT housekeeping (_execute_operation_house_keeping_func, operation_utils.cpp:230-242) consumes a host ACK only on the FIRST chunk (can_operation_start), not on subsequent in-progress chunks. So N-1 spurious OK acks (N = mem_size/BLANK_CHECK_CHUNK_SIZE = 32 for 64KB) accumulated in the firmware RX buffer, desyncing the MAIN-phase data-pull handshake. The write read a stale OK instead of a data frame, aborted, returned to CMD_IDLE, and decoded the remaining queued junk as an empty command -> MSG_ERR_EMPTY_INPUT (0xA4) at firestarter.cpp:115/194. The bench-reported '2048' was the FIRST blank-check progress frame (DATA: 2048/65536), not a data-transfer position. The bug only reproduced WITHOUT -b (blank-check enabled); -b (SKIP_BLANK_CHECK) writes were always clean."
fix: "OPTION C (host-only; firmware keeps the progress emit so the blank-check bar still moves). Firmware: NO change — the baseline mem_util_blank_check per-chunk emit `if (handle->cmd != CMD_BLANK_CHECK) LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS,...)` (memory.cpp:456-458) is retained; the earlier Option D suppress-the-emit attempt was reverted (git checkout). Host (firestarter_app/firestarter/eprom_operations.py): threaded `ack_data: bool = True` through _handle_progress_response; the DATA-frame send_ack() now fires only when ack_data is True, while progress rendering always runs. _execute_phase (INIT/END) passes ack_data=False — this is the single change that stops the spurious acks. _main_phase_simple (MAIN) passes ack_data=True (unchanged). _main_phase_read_data keeps its own DATA send_ack() and uses default ack_data=True for non-DATA frames. INIT-START / MAIN-START / final acks untouched. No protocol constants touched (constants.py / firestarter.h unchanged)."
verification: "Leonardo /dev/ttyACM0 (controller identity confirmed = leonardo, fw 3.0.0b8) rebuilt+uploaded (pio run/upload -e leonardo, 88.9% flash). Default (blank-check ON, NO -b) writes — the exact failing path — all succeed with NO 0xA4: 100B (5.45s), 37KB (15.49s), 64KB (22.84s). The INIT-phase blank-check progress bar MOVES (Option C goal achieved) — two distinct progress bars observed per 64KB write (0x800-step blank-check during INIT, then 0x400-step write data during MAIN). verify W27C512 against 64KB PASS (5.60s, full host->fw read compare) — proves the MAIN-receive ack path is intact after the host change. 77/77 native firmware tests pass. 640/640 host tests pass after clearing the saved ~/.firestarter/config.json port (the 2 test_no_programmer_found_* env-artifact tests fail only with a saved port; documented, not a regression). ruff check + ruff format clean on eprom_operations.py; mypy error count unchanged vs baseline (9 pre-existing self.comm union-attr, none new)."
files_changed: [firestarter_app/firestarter/eprom_operations.py]
---

# Debug: write-empty-input-regression

## Symptoms
- **Expected:** `firestarter write W27C512 <file>` completes the MAIN write phase and verifies clean (the Phase-54 EVEN-01 baseline, proven on Leonardo/ACM0 2026-06-04).
- **Actual:** `write` aborts during the write MAIN phase with `ERROR: Empty input` after the first data block (observed `DATA: 2048/65536`).
- **Error:** `MSG_ERR_EMPTY_INPUT` (0xA4). ⚠ The name is MISLEADING — firmware `firestarter/src/firestarter.cpp:186-189` OVERLOADS 0xA4 for "CRC mismatch, COBS violation, overflow, OR read underrun" (a dedicated `MSG_ERR_BAD_FRAME` was deferred because messages.h is codegen). The real fault is a **write-data-chunk COBS/CRC framing failure**, NOT literally empty input. Do NOT chase "empty input" literally.
- **Timeline:** Discovered at the bench 2026-06-16 (Phase 08 UAT). Regression vs Phase-54 baseline. NOT a version issue — matched host/firmware b8/b8; updating fw b6→b8 did not fix it.
- **Reproduction:** Leonardo /dev/ttyACM0, W27C512 seated, fw b8. Reproduced across 3 file sizes (100 B, 37 KB, 64 KB). Failure occurs after 2048 B = 2× the 1024-byte Leonardo buffer.

## Scope
- Write-path transport regression. Read path completes clean (no literal prefixes), so Phase-08 ID-frame ack rendering is FINE.
- Candidate culprits: v1.11/v1.12/v1.13 host changes to the `write` command or chunked-send path; or a buffer-boundary framing bug (failed after 2048 B = 2× Leonardo 1024 buffer).
- **Related prior bug (resolved):** `write-verify-datapath-overflow` — host→fw data-chunk path returned `-2` (payload-too-large, 512+CRC+NUL > 511 cap), fixed by Phase 55 CAP-01 buffer-size advertisement + host safe-512 default. DISTINCT error code (-2 vs 0xA4) but same host→fw chunked-send path — inspect whether CAP-01 negotiation / safe-512 default interacts with the new failure.

## Evidence
- timestamp: 2026-06-17T01
  checked: Host chunked-send path (eprom_operations.py:403-440 _main_phase_send_data) + buffer-size calc (eprom_operations.py:184-197 _calculate_buffer_size).
  found: Host reads buffer_size bytes/chunk, frames `#` + COBS(data + CRC8) + 0x00. buffer_size = firmware_max_chunk (CAP-01, populated from MSG_OK_READY ack) or 512 floor. On Leonardo, firmware advertises DATA_BUFFER_SIZE=1024 → host sends 1024-byte data chunks.
  implication: Per-chunk on-wire payload is 1024 data + 1 CRC = 1025 bytes.
- timestamp: 2026-06-17T02
  checked: Firmware advertised chunk (firestarter.cpp:138 LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)) + Leonardo DATA_BUFFER_SIZE (platformio.ini:67 -D DATA_BUFFER_SIZE=1024) + MAIN-path decode cap (operation_utils.cpp:173 rurp_communication_read_data(buf, DATA_BUFFER_SIZE)) + decoder semantics (rurp_serial_utils.cpp:138-243).
  found: Decoder `cap` = max PAYLOAD-DATA bytes committed to buffer[]; the CRC byte is held in `last_byte` 1-byte-lookahead and NEVER written (out ≤ cap). MAIN path cap=DATA_BUFFER_SIZE=1024 → a 1024-data-byte chunk fits EXACTLY (out reaches 1024, CRC held separately, no -2 overflow). So per-chunk 1024 does NOT overflow the MAIN decoder.
  implication: A pure per-chunk-size overflow would fail on chunk 1, not after 2048 B. The 2048 B failure (= chunk 3, after 2 clean 1024 chunks) points elsewhere than a fixed-size cap. Need to investigate the chunk-3 boundary: host read() short-read at EOF? CRC8 host-vs-fw mismatch on a specific byte pattern? COBS encoder edge case? Or a chunk-count/state issue.

## Eliminated
- hypothesis: Per-chunk fixed-size overflow (1024 data + CRC exceeds MAIN decoder cap → -2 → 0xA4) — analogous to the resolved -2 datapath bug.
  evidence: MAIN-path decoder cap = DATA_BUFFER_SIZE (1024), CRC held in lookahead not committed; a 1024-byte chunk fits exactly. Would fail on chunk 1, but symptom is failure AFTER 2048 B (chunk 3). Per-chunk size is not the trigger.
  timestamp: 2026-06-17T02

## Evidence (continued)
- timestamp: 2026-06-17T03
  checked: Bench repro on Leonardo /dev/ttyACM0 fw 3.0.0b8. (a) write -b (SKIP_BLANK_CHECK) 4KB 0xFF + 4KB random → BOTH SUCCEED (clean 1024-byte chunks, "Sent 1032/1030 bytes", buffer_size=1024). (b) write WITHOUT -b (default, blank-check ON) 64KB to a freshly-ERASED blank W27C512 → FAILS with `ERROR: Empty input` (0xA4) right at "Main start".
  found: The 0xA4 reproduces ONLY on the default (blank-check-enabled) write path, NOT with -b. The transport (COBS/CRC chunk framing) is HEALTHY — 1024-byte chunks transfer fine with -b.
  implication: The bug is NOT a COBS/CRC/buffer-boundary transport fault. It is a host↔fw HANDSHAKE DESYNC introduced by the write-init blank-check progress emission.
- timestamp: 2026-06-17T04
  checked: Full unfiltered write trace (/tmp/write_trace.log). Firmware emits 32× `DATA: N/65536` (N=2048,4096,...,65536) during INIT, host replies `OK` (2 bytes) to each, then `INIT: (init done)`, host ack, `Main start`, then immediately `ERROR: Empty input`. Confirmed BLANK_CHECK_CHUNK_SIZE=2048 (memory.cpp:383) → 65536/2048 = 32 progress frames. First frame is exactly `DATA: 2048/65536` = the bench-reported "2048" (misread as data position; it is blank-check progress).
  found: mem_util_blank_check (memory.cpp:391-460), when called as the write's firestarter_operation_init (handle->cmd==CMD_WRITE, NOT CMD_BLANK_CHECK), emits LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS,...) once per 2048-byte chunk (line 384-386). This runs as a multi-step in-progress INIT op: _execute_operation_house_keeping_func (operation_utils.cpp:238) calls op_wait_for_ack ONLY on the FIRST entry (can_operation_start true); subsequent in-progress iterations do NOT consume an ack. So the firmware emits 32 ack-expecting-looking DATA frames but consumes only 1 ack. Meanwhile the host's _handle_progress_response (eprom_operations.py:368-380) calls send_ack() for EVERY DATA frame during _execute_phase("INIT"). Result: ~31 spurious OK acks pile up in the fw RX buffer.
  implication: At MAIN start the fw's op_get_message reads the stale queued OK acks (not the expected data frame) → write aborts → command_done → CMD_IDLE → the remaining queued junk is COBS-decoded as a command → empty/garbage decode → MSG_ERR_EMPTY_INPUT (0xA4) at firestarter.cpp:115/194. Matches trace exactly ("Main start" → immediate 0xA4).
- timestamp: 2026-06-17T05
  checked: Asymmetry vs the working READ path. _process_outgoing_data (eprom_operations.cpp:113-120) emits MSG_DATA_CHUNK then ALWAYS op_wait_for_ack — one ack consumed per DATA frame. The host acks DATA frames the same way for both. So the read DATA-ack handshake is balanced; the write-init blank-check progress DATA emit is UNBALANCED (emits without consuming).
  found: Standalone `blank` command (CMD_BLANK_CHECK) SUPPRESSES the per-chunk DATA emit (memory.cpp:456 guard `if (handle->cmd != CMD_BLANK_CHECK)`) and works cleanly (4.73s, no desync). Only the write-init caller (cmd==CMD_WRITE) still emits the unbalanced progress.
  implication: Root cause = unbalanced DATA-progress emit during write-init blank-check. Fix options: (A) firmware: suppress the MSG_DATA_PROGRESS emit during write-init blank-check (the host renders its own progress bar; the standalone-blank path already proves suppression is safe); (B) firmware: op_wait_for_ack after each progress emit (matches read path, but adds a round-trip per chunk); (C) host: do NOT send_ack on DATA frames during INIT/END phases. Option A is the minimal, lowest-risk fix and removes a contract that the host cannot satisfy without desync.

## Evidence (continued)
- timestamp: 2026-06-17T06
  checked: OPTION C pivot bench verification on Leonardo /dev/ttyACM0 (controller=leonardo confirmed via `fw`, fw 3.0.0b8). Reverted the Option D firmware suppress (git checkout memory.cpp -> baseline emit guard restored). Applied host ack_data=False on INIT/END. Rebuilt+uploaded leonardo fw. Ran erase->write WITHOUT -b at 100B/37KB/64KB, verify, and both test suites.
  found: All 3 default (blank-check ON) writes SUCCEED with NO 0xA4 — 100B (5.45s), 37KB (15.49s), 64KB (22.84s). The blank-check progress bar MOVES during INIT (two progress bars per 64KB write: blank-check INIT 0x800-step + write MAIN 0x400-step), confirming Option C preserves the progress feedback the operator wanted. verify W27C512 vs 64KB PASS (5.60s) -> MAIN-receive ack path intact. 77/77 firmware native tests pass; 640/640 host tests pass (saved-port env-artifact tests pass once config.json port cleared); ruff clean; mypy unchanged.
  implication: Option C resolves the regression without removing the blank-check progress feedback. Root cause confirmed by the asymmetric fix: stopping ONLY the INIT/END DATA acks (ack_data=False) — while keeping the firmware emit and MAIN acks — eliminates the spurious-ack pileup and the 0xA4. Committed: host firestarter_app fcf7974 (v1.13-algo-validation); firmware NO commit (baseline 8d378b0 already carries the Option C emit; Option D was uncommitted and reverted). Meta gitlinks intentionally NOT bumped (pinned until beta cut).

## Eliminated (continued)
- hypothesis: Data-dependent COBS encoder / CRC8 edge case on large chunks (>254-byte runs, zero handling).
  evidence: Both all-0xFF and random 4KB writes (with -b) transferred 1024-byte chunks cleanly with no 0xA4. COBS/CRC is fine.
  timestamp: 2026-06-17T03
- hypothesis: Buffer-boundary / firmware_max_chunk negotiation (1024 vs cap) regression from CAP-01.
  evidence: buffer_size negotiated to 1024 correctly; -b writes at 1024-byte chunks succeed. The 2048 figure is blank-check progress granularity (BLANK_CHECK_CHUNK_SIZE), not a transport chunk boundary.
  timestamp: 2026-06-17T04

## Current Focus
- hypothesis: CONFIRMED. Write-init blank-check (mem_util_blank_check with cmd==CMD_WRITE) emits 32 MSG_DATA_PROGRESS frames during the multi-step in-progress INIT phase without consuming the host's per-frame OK acks. The host acks every DATA frame, so ~31 spurious acks accumulate and desync the MAIN handshake → fw returns to CMD_IDLE and decodes queued junk as an empty command → MSG_ERR_EMPTY_INPUT (0xA4).
- test: Apply Option A (firmware: suppress the write-init blank-check MSG_DATA_PROGRESS emit), rebuild+upload Leonardo, re-run the default (no -b) 64KB write to a blank chip.
- expecting: With no per-chunk progress DATA emitted during INIT, the host sends no spurious acks, MAIN handshake stays in sync, write completes without 0xA4.
- next_action: Edit memory.cpp:456 guard to also exclude CMD_WRITE (and any non-standalone caller) from the per-chunk progress emit; rebuild leonardo; upload; bench-verify default 64KB write.
- reasoning_checkpoint:
    hypothesis: "The default write path's blank-check INIT phase emits N=32 MSG_DATA_PROGRESS DATA frames that the firmware does not ack-consume, while the host acks each, desyncing the MAIN handshake and producing MSG_ERR_EMPTY_INPUT (0xA4)."
    confirming_evidence:
      - "Bench: -b (blank-check OFF) write succeeds; default (blank-check ON) write fails with 0xA4 at Main start."
      - "Trace shows exactly 32 DATA: N/65536 frames (=BLANK_CHECK_CHUNK_SIZE 2048 granularity), each host-acked, then immediate 0xA4 at Main start."
      - "Firmware in-progress INIT (operation_utils.cpp:238) consumes only the first ack; host acks every DATA (eprom_operations.py:380). Standalone blank suppresses the emit and works."
    falsification_test: "If suppressing the write-init progress emit does NOT fix the 0xA4, the desync is elsewhere (e.g. INIT->MAIN ack count) and the hypothesis is wrong."
    fix_rationale: "Removing the unbalanced DATA-progress emit eliminates the spurious-ack accumulation at the source. The host already renders its own progress bar, and the standalone blank-check path proves suppression is safe and desync-free."
    blind_spots: "Uno path (com_mode-gated emit already dropped on Uno, so Uno may already be unaffected — verify no Uno regression). Other multi-step INIT/END ops (e.g. erase-end) may emit progress the same way and need the same treatment. Verify a verify-op (also _process_incoming_data) is unaffected."
