---
status: resolved
trigger: "the progress bar are not growing during blank check until it kind of ends and then it grows up to 98% ( 0x7d800/0x80000 bytes ) and reports an error 'Programmer error during BLANK_CHECK: Empty input'. I dont think the blank check is bad i think its returning the wrong answer, mybe times oy in some way or the app ist reading the final messages from the programmer"
created: 2026-08-29
updated: 2026-08-29
related: [write-empty-input-regression, transport-protocol-verify]
root_cause: "Standalone blank-check's MAIN-phase per-chunk loop (_single_step_operation_callback, operation_utils.cpp, reached via op_execute_simple_operation for CMD_BLANK_CHECK) emits one MSG_DATA_PROGRESS frame per 2048B chunk but NEVER consumed the host's per-frame ack -- unlike every other flow-controlled data path in the firmware (e.g. eprom_read's _process_outgoing_data ALWAYS op_wait_for_ack()s after each DATA emit). The host's _main_phase_simple acks every DATA frame unconditionally, so this ran fully unthrottled -- writing for the entire ~60-70s / 256-chunk duration of a 512KB chip's blank check without ever touching the incoming byte stream. Byte-level wire capture (5 live reproductions) proved the eventual failure is NOT a corrupted/misframed byte stream -- it is a clean, CRC-valid, zero-param id=0xA4 (MSG_ERR_EMPTY_INPUT) frame, appearing after exactly 1.000-1.001s of total wire silence following the last successful chunk (1000ms = TIMEOUT_MS). MSG_ERR_EMPTY_INPUT has only 2 call sites, both gated on handle.cmd==CMD_IDLE, so handle.cmd silently reverted to CMD_IDLE mid-operation. Instrumentation (temporary probes in command_done() and in the res==ERROR branch) proved command_done() was NEVER invoked before the failure in 2 separate instrumented runs -- the CMD_IDLE transition happened via direct state desync, not a controlled completion path. The failure point was NOT a fixed chunk count or fixed wall-clock time -- it scaled inversely with per-chunk instrumentation byte volume across 3 different loads (251 chunks @ 17B/chunk = 4267B; 176 chunks @ ~25B/chunk = 4400B; 92 chunks @ ~57B/chunk = 5244B), consistent with a roughly fixed ~4-5KB cumulative-TX-volume resource being exhausted by the unthrottled emit loop (the exact low-level AVR/USB-CDC mechanism was not conclusively isolated, but the STRUCTURAL cause -- missing flow control -- was)."
fix: "firestarter/src/operation_utils.cpp, _single_step_operation_callback: after LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS,...) for CMD_BLANK_CHECK (the branch that fires once per 2048B chunk while still in progress), added a call to op_wait_for_ack(handle) to consume the ack the host already sends unconditionally for every DATA frame during MAIN. On ack timeout, treat it as an error (return false), matching the existing res==ERROR handling. This restores the same 1:1 flow control every other data-emitting path in the firmware already has (e.g. the read path). No host-side change needed -- the host already acks every DATA frame in _main_phase_simple. No change to write-init or erase-end's blank-check call (they run through a different engine, _execute_operation_house_keeping_func's in-progress branch, which was never affected)."
verification: "Firmware rebuilt+reflashed to the bench Leonardo (fw checked via `fw` -> controller: leonardo). Native gates: native (184/184) and native_nodevtools (184/184) both pass unmodified. uno env also builds clean (unaffected). Hardware: standalone `firestarter blank W27C040` on /dev/ttyACM0 -- 4 consecutive clean PASSES post-fix (RC=0, progress bar advances smoothly 0%->100% throughout, no batching-at-the-end), each completing in ~61.66s (vs the pre-fix deterministic 0xA4 failure at 251/256 chunks on every one of 3 baseline runs). Regression checks on the SAME chip: `erase -f` (plain, no blank-check) succeeds; `erase -f -b` (blank-check as erase's END-phase step -- the operator's already-working path) succeeds (59.36s, full progress bar); `write -f` with default blank-check-enabled INIT step succeeds (60.01s). All four command shapes that touch mem_util_blank_check now complete cleanly on the same hardware in the same session."
files_changed: [firestarter/src/operation_utils.cpp, firestarter/src/proms/memory.cpp]
---

# Debug: blank-check-empty-input-98pct

## Symptoms

- **Expected:** `firestarter blank-check` on a W27C040 (0x80000 = 524288 B) renders a
  progress bar that advances smoothly to 100% and returns a clean blank/not-blank verdict.
- **Actual:** The progress bar does **not** advance during the blank check. Near the end it
  suddenly jumps to ~98% — **`0x7d800/0x80000`** = 514048/524288 B — and the command aborts with
  `Programmer error during BLANK_CHECK: Empty input`.
- **Error:** `MSG_ERR_EMPTY_INPUT`, error_code 164 (`0xA4`).
  ⚠ **The name is MISLEADING.** `0xA4` is OVERLOADED in `firestarter/src/firestarter.cpp` —
  two emit sites: a genuine empty-buffer check, and the frame-integrity path (CRC mismatch,
  COBS violation, overflow, or read underrun) which REUSES `MSG_ERR_EMPTY_INPUT` because a
  distinct `MSG_ERR_BAD_FRAME` was deliberately deferred (messages.h is codegen-generated from
  meta's `messages.toml`). Do NOT chase "empty input" literally.
- **Timeline:** Observed 2026-08-29 on the v1.34 bench rig. The same `ERROR: Empty input` text
  was recorded across the Phase 162 sweep on BOTH arms at differing steps.
- **Reproduction:** Standalone `blank-check`, W27C040, Leonardo `/dev/ttyACM0`, v1.33 arm.

## Operator-supplied discriminator (HIGH VALUE — read before hypothesising)

> "This is happening for the w27c040, the erase and blank check is working when you do a write"

The blank check run as the **write's INIT sub-step** works. Only the **standalone**
`blank-check` command fails. This **inverts** the 2026-06-17 `write-empty-input-regression`
(there, write-path blank-check failed and standalone `blank` was clean at 4.73 s). Any
hypothesis must explain the inversion, not just the 0xA4.

## Arithmetic (do not re-derive, but DO verify against the live trace)

- `0x80000` = 524288 B; `0x7d800` = 514048 B; shortfall = **10240 B = exactly 5 × 2048**.
- `BLANK_CHECK_CHUNK_SIZE` = 2048 (`firestarter/src/proms/memory.cpp:439`).
- 524288 / 2048 = **256 chunks**; 514048 / 2048 = **251**. It dies **5 chunks short**, i.e. it
  completes 251 of 256 progress steps. Establish whether "5 short" is stable across runs — a
  fixed shortfall implicates a buffer/queue depth; a varying one implicates timing.

## Rig state (verified 2026-08-29, before spawning)

- Port `/dev/ttyACM0` present; **no process holding it** (checked `/proc/*/fd`) — port free.
- meta `HEAD` = `gsd/v1.34-pre-merge-hardware-regression-validation`.
- Submodules: `firestarter` @ `5759dc8` (detached HEAD), `firestarter_app` @ `cb189a9` on
  `gsd/v1.33-source-hygiene-firmware-size-reduction`.
- `firestarter` CLI resolves to `/home/vscode/.local/bin/firestarter`; **`firestarter.__file__`
  printed `None`** — confirm which package the CLI actually imports before trusting any host-side
  edit to take effect (known worktree/editable-install trap).
- Operator granted live bench access for this session (chip handling / photos / DMM remain
  operator-only). Board identity must still be confirmed per-port (`ttyACM*` numbers shuffle).

## Scope

Standalone blank-check MAIN-phase path, host↔firmware handshake. Two symptoms that may or may
not share a cause, and should be treated as **separate** until evidence joins them:
1. **Progress bar does not advance, then batches at the end.** Pre-existing backlog item
   `999.3-blank-check-progress-bar-batches-at-end` (directory is EMPTY — title only, no content).
2. **The 0xA4 abort at 251/256 chunks.**

## Prior art (already read — do not re-read from scratch)

- `.planning/debug/resolved/write-empty-input-regression.md` — RESOLVED 2026-06-17. Root cause was
  an **unbalanced DATA-progress emit**: firmware emitted one `MSG_DATA_PROGRESS` per 2048 B chunk
  during write-INIT but consumed a host ACK only on the FIRST chunk, so N-1 spurious OK acks piled
  in the fw RX buffer and desynced the MAIN pull → junk decoded as an empty command → 0xA4.
  Fix was host-only: `ack_data=False` on INIT/END, `ack_data=True` on MAIN.
  **That session explicitly recorded: standalone `blank` SUPPRESSED the per-chunk DATA emit
  (`if (handle->cmd != CMD_BLANK_CHECK)`) and ran cleanly.** That suppression is the likely
  origin of symptom 1 (bar never moves). Verify whether the guard still exists and in what form.
- `firestarter/src/proms/memory.cpp:477-490` — `mem_util_blank_check` now has a **`CMD_BLANK_CHECK`
  special case** that stashes offset+value into `handle->data_buffer` (`data_size = 4`) and sets
  `RESPONSE_CODE_ERROR`, instead of the direct `LOG_ERROR_ID_BYTES(MSG_ERR_NOT_BLANK, ...)` other
  callers use — because on the Uno `rurp_log_id` is com_mode-gated in programmer mode. Tagged
  `(#transport-protocol-verify)`. **This is a standalone-blank-check-ONLY divergence and is the
  prime suspect for the inversion.**
- `firestarter/src/proms/memory.cpp:500-507` — the progress emit sits behind a `RAW_DATA_PROGRESS`
  `#ifdef` (currently OFF), with an `if (handle->address > handle->mem_size) handle->address =
  handle->mem_size;` clamp immediately before `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, ...)`.
- `firestarter_app/firestarter/eprom_operations.py:2098-2125` — host already carries comments
  naming this exact failure: "firestarter_operation_main for CMD_BLANK_CHECK, causing 0xA4" and
  "CMD_BLANK_CHECK, so the firmware emits 0xA4 MSG_ERR_EMPTY_INPUT". An existing workaround lives
  here. Read it and establish whether it is incomplete rather than assuming it is correct.
- `.planning/v1.34/bench/cells/CHIP/human-inputs/anomalies_CHIP__v133__w27e040.txt` — Phase 162-07
  reproduced a blank-check `Empty input` (error_code 164) on the sibling W27E040 **twice**,
  deterministically, inside `dev test`. Concluded "intermittent, arm-independent frame corruption",
  and explicitly filed the overloaded-error-identity problem to Phase 165/166. **Note the tension:
  that file calls it intermittent; the operator's report here is a clean standalone-vs-write
  split. Reconcile, do not inherit the earlier conclusion.**

## Current Focus

status_note: "Fix applied and self-verified (4x clean standalone blank-check + erase/erase-b/write regression checks, all on the same W27C040, same bench session). Committed firestarter@1e8bbae on gsd/v1.33-source-hygiene-firmware-size-reduction. Awaiting operator confirmation before archiving."
next_action: "Operator re-runs `firestarter blank <chip>` (or their normal workflow) once and confirms the progress bar advances smoothly and the command completes without the 'Empty input' error."

reasoning_checkpoint (historical, from fix-confirmation phase):
  hypothesis: "Standalone blank-check's MAIN-phase per-chunk loop (_single_step_operation_callback, driven by op_execute_simple_operation for CMD_BLANK_CHECK) emits one MSG_DATA_PROGRESS frame per 2048B chunk but NEVER calls op_wait_for_ack / op_get_message to consume the host's per-frame ack, unlike every other flow-controlled data path (read's _process_outgoing_data ALWAYS op_wait_for_ack's after each DATA emit). Running unthrottled for 50-70s straight without ever touching the incoming byte stream lets some finite host-ack-side or firmware transport resource accumulate past capacity; once it does, handle.cmd reverts to CMD_IDLE WITHOUT going through command_done() (confirmed by instrumentation — see evidence), and the very next loop() CMD_IDLE decode attempt on stray/leftover bytes fails and emits the reused MSG_ERR_EMPTY_INPUT (0xA4), exactly 1000ms (TIMEOUT_MS) after the last successful chunk."
  confirming_evidence:
    - "Byte-perfect wire capture (3 clean baseline runs + 2 instrumented runs, 5 total) shows the failure is NOT a corrupted/misframed byte stream: each failure ends with a well-formed, CRC-valid, zero-param id=0xA4 frame, preceded by exactly 1.000-1.001s of total wire silence after the last successful DATA-frame+ack exchange -- 1000ms is TIMEOUT_MS, the exact constant op_wait_for_ack uses."
    - "Deterministic across all 3 unmodified-firmware runs: fails at EXACTLY 0x7d800/0x80000 (251/256 chunks) every time on this W27C040."
    - "Instrumentation (Serial.print probes added to command_done() and to the res==ERROR branch of _single_step_operation_callback) NEVER fired before the 0xA4, across 2 separate instrumented reproductions -- proving handle.cmd reached CMD_IDLE WITHOUT going through command_done()'s only 2 call sites, i.e. via direct state corruption/desync rather than a controlled, logged completion path."
    - "Failure point is NOT a fixed chunk count or fixed wall-clock time: adding more per-chunk Serial.print overhead (instrumentation) moved the failure EARLIER in chunk-count terms (176/256 and 92/256 instead of 251/256) roughly in proportion to the extra bytes emitted per chunk -- consistent with a roughly fixed TOTAL TX BYTE BUDGET (~4300-5200B) rather than a chunk-count or absolute-time trigger."
    - "A stack-pointer proxy sampled once per chunk at the top of mem_util_blank_check was IDENTICAL (2694) on every single call across an entire run -- ruling out cumulative/growing stack usage as the mechanism."
    - "Prior art (write-empty-input-regression, 2026-06-17) established the working reference pattern: the read path's _process_outgoing_data ALWAYS op_wait_for_ack()s after each DATA emit, one ack consumed per frame -- this is the balanced pattern standalone blank-check's MAIN loop is missing."
  falsification_test: "Add op_wait_for_ack() immediately after the CMD_BLANK_CHECK progress emit in _single_step_operation_callback (only when a frame was actually just sent) and re-run the identical standalone blank-check on the same W27C040. If the 0xA4 still occurs at any point, the ack-starvation hypothesis is wrong and the true resource being exhausted lies elsewhere (e.g. genuinely in USB/ISR territory beyond firmware source)."
  fix_rationale: "This is the same bug CLASS as the resolved write-empty-input-regression -- an unthrottled, un-acked progress-frame emission loop -- just on a different call path (op_execute_simple_operation's per-chunk MAIN callback, not the INIT housekeeping loop). The host already sends a per-DATA ack unconditionally in _main_phase_simple (ack_data=True), so consuming it firmware-side costs nothing new on the host and restores the same 1:1 flow-control contract every OTHER data-emitting path in this firmware already honors (see read's _process_outgoing_data)."
  blind_spots: "The exact low-level AVR/USB-CDC resource that exhausts (RX ring buffer of unread host acks vs TX buffer/endpoint state vs an ISR/stack collision window) was not conclusively isolated -- only its rough order of magnitude (~4-5KB cumulative TX volume) and its behavioral signature (silent, uncommanded handle.cmd->CMD_IDLE transition) were pinned down. The fix targets the STRUCTURAL cause (no flow control) rather than the specific hardware exhaustion mechanism; if op_wait_for_ack() does not fully resolve it, the mechanism needs deeper AVR-USB-stack investigation (out of firmware-source scope)."

## Evidence

- timestamp: 2026-08-29T00
  checked: Rig preflight — `/dev/ttyACM0` present, no process holding any tty; submodule SHAs; firmware guard sites in `firestarter/src/proms/memory.cpp`; `MSG_DATA_PROGRESS` emit sites across the firmware.
  found: Four `MSG_DATA_PROGRESS` emit sites (`operation_utils.cpp:235`, `proms/memory.cpp:507`, `proms/eprom.cpp:388`) plus a comment at `eprom_operations.cpp:102` reading "On leonardo the firmware emits MSG_DATA_PROGRESS from inside the...". `mem_util_blank_check` carries a `CMD_BLANK_CHECK`-only branch absent from the 2026-06-17 baseline.
  implication: The standalone path is materially different from the write-init path in current firmware, consistent with the operator's standalone-fails/write-works split. Port is free — no risk of a second process confounding live runs.

- timestamp: 2026-08-29T01
  checked: Static trace of op_execute_simple_operation -> op_execute_stateful_operation -> _execute_operation_house_keeping -> _single_step_operation_callback (operation_utils.cpp) for CMD_BLANK_CHECK, vs eprom_read's _process_outgoing_data.
  found: Once state==MAIN, _execute_operation_house_keeping short-circuits immediately (`if (is_operation_started(MAIN)) return CONTINUE;`) and _single_step_operation_callback runs every loop() iteration with NO op_wait_for_ack/op_get_message call anywhere in its 256-chunk path — it only ever WRITES (the progress emit), never READS the incoming byte stream, for the entire duration of a standalone blank check. Contrast: eprom_read's _process_outgoing_data ALWAYS op_wait_for_ack()s after each MSG_DATA_CHUNK emit.
  implication: Every one of the host's per-DATA acks sent during _main_phase_simple's ack_data=True loop goes completely unread by the firmware for the full duration of the operation — an unbounded, un-acked emission loop, structurally identical in kind to the resolved write-empty-input-regression's root cause (unbalanced DATA-progress emit), but on a different call path.

- timestamp: 2026-08-29T02
  checked: Live bench repro, standalone `firestarter blank W27C040` on Leonardo /dev/ttyACM0 (controller identity confirmed via `fw`: leonardo, fw 3.0.0b22), 3 independent unmodified-firmware runs (1 verbose+timestamped, 2 non-verbose) plus a raw pyserial byte-level capture (sitecustomize.py wrapping serial.Serial.read/write) for one of them.
  found: ALL THREE runs fail at EXACTLY 0x7d800/0x80000 (514048/524288 bytes = 251/256 chunks, matching the debug file's pre-recorded arithmetic exactly). Raw byte capture shows the last successful frame is a clean, CRC-valid MSG_DATA_PROGRESS(514048,524288) frame; host acks it (2-byte "OK", no other framing); then EXACTLY 1.000-1.001s of total wire silence; then a clean, CRC-valid, ZERO-PARAM id=0xA4 frame (length field = 2 = id+crc only) appears, decoded by the host as "ERROR: Empty input". One non-verbose run instead showed a CRC-mismatch warning on a DATA frame at the same position before timing out — a variant surface of the same underlying desync.
  implication: The shortfall is a FIXED byte/chunk-count phenomenon on unmodified firmware, not a random transport glitch. The 1.000s silence-then-clean-0xA4 pattern is the signature of op_wait_for_ack's TIMEOUT_MS constant, but 0xA4 (MSG_ERR_EMPTY_INPUT) has only 2 call sites in firestarter.cpp, both gated on handle.cmd==CMD_IDLE — meaning handle.cmd silently reverted to CMD_IDLE sometime in the preceding second.

- timestamp: 2026-08-29T03
  checked: Instrumented firmware (temporary Serial.print probes in command_done(), in _single_step_operation_callback's res==ERROR branch for CMD_BLANK_CHECK, and in loop()'s CMD_IDLE decode-attempt branch), rebuilt+reflashed to the SAME Leonardo, 2 independent reproductions.
  found: NONE of the 3 probes ever printed before the 0xA4 appeared, in either instrumented run — yet the 0xA4 still occurred, at EARLIER chunk counts (176/256 and 92/256) proportional to the extra per-chunk Serial.print byte volume added. A separate stack-pointer proxy (local variable address, sampled once per chunk at the top of mem_util_blank_check) was IDENTICAL (2694) on every single sampled call across a full run.
  implication: command_done() is NEVER invoked before the failure — handle.cmd reaches CMD_IDLE via direct state corruption/desync, not a controlled completion path. Stack usage at the sampled point does not grow over time (rules out a stack leak at that specific call depth, though a transient ISR-driven spike at a DEEPER point cannot be excluded). The chunk-count-at-failure scaling inversely with per-chunk TX byte volume (roughly constant ~4300-5200 cumulative TX bytes across 3 different instrumentation loads: 17B/chunk->251 chunks=4267B baseline; ~25B/chunk->176 chunks=4400B; ~57B/chunk->92 chunks=5244B) points to a roughly fixed cumulative-TX-volume resource, not a fixed time or fixed chunk count, being exhausted by the unthrottled emit loop.

## Eliminated

- hypothesis: The CMD_BLANK_CHECK-only data_buffer-stash/RESPONSE_CODE_ERROR divergence in mem_util_blank_check (memory.cpp:477-490) is the direct cause of the 0xA4.
  evidence: That branch only executes when a not-blank byte is actually found (which would emit MSG_ERR_NOT_BLANK, 0xB0, with a 4-byte payload) — the observed failure is a clean, unrelated 0xA4 zero-param frame appearing after 251/256 (or fewer, when instrumented) chunks all cleanly reported blank. The not-blank branch never fires in any reproduction.
  timestamp: 2026-08-29T02
- hypothesis: Corruption/timing is verbose-logging-induced (Python console overhead) rather than a real firmware/transport issue.
  evidence: A non-verbose run (no -v, no extra console rendering) reproduced the identical failure at the identical 0x7d800 boundary with a similar total elapsed time; ruled out as a host-side console artifact.
  timestamp: 2026-08-29T02
- hypothesis: Fixed elapsed wall-clock time (a firmware- or host-side timer unrelated to chunk count) triggers the failure.
  evidence: Instrumented runs failed at markedly different elapsed times (51s, 37s) and markedly different chunk counts (176, 92) that scale with added per-chunk instrumentation overhead, not with a fixed clock. A pure time-based trigger would produce failures near a constant elapsed time regardless of chunk count, which was not observed.
  timestamp: 2026-08-29T03
- hypothesis: Cumulative/growing stack depth (a stack leak across chunk iterations) is the corruption mechanism.
  evidence: Stack-pointer proxy sampled once per chunk at a fixed call depth was bit-for-bit IDENTICAL (2694) on every call across an entire run — no growth over time at that depth.
  timestamp: 2026-08-29T03

## Post-fix orchestrator audit (2026-08-29, after gsd-debugger returned)

- timestamp: 2026-08-29T04
  checked: Flash/RAM cost of the fix against the LIVE `firestarter/scripts/baseline/size_baseline.json`, via cold rebuilds (`rm -rf .pio/build/<env>` then one `pio run -e <env>`) on all three AVR targets. Also checked which gates CI actually arms.
  found: **+16 B flash on every target, +0 B RAM on every target.** uno 22952 -> 22968; uno328pb 23000 -> 23016; leonardo 25098 -> 25114 (RAM 1434/1440/1875, all byte-unchanged). The default-mode `check_size_baseline.py` gate is a BYTE-IDENTITY comparator, so the recorded live figures are now stale by exactly 16 B on each target. The `--policy merge05` growth axis against BASE-01 is NOT breached and needs no new exemption: BASE-01 leonardo is 26906 and the post-fix figure is 25114, i.e. still well BELOW the reference point (Phase 158's jsmntok_t narrowing bought far more than this fix spends). CI arms only `pio test -e native`, `pio test -e native_nodevtools` and `pio run` (build.yml:142/155/193, beta-build.yml:122/128/145) — it does NOT invoke check_size_baseline.py, so this staleness fails no automated leg today.
  implication: The baseline re-record is a DOCUMENTATION debt, not a broken gate, and not a blocker for the fix. Per this file's own convention it is an adjudicated act requiring a cold-log-sourced, SHA-attributed `meta` prose entry — deliberately NOT performed unilaterally here. Left open for the operator.

- timestamp: 2026-08-29T05
  checked: Whether the host-side `_SRAM_PROTO_IDS` short-circuit in `firestarter_app/firestarter/eprom_operations.py:2097-2120` is a workaround for THIS bug that the firmware fix now makes redundant.
  found: It is NOT. That guard covers SRAM/FRAM families whose `configure_sram()` handler leaves a genuinely NULL `firestarter_operation_main` for `CMD_BLANK_CHECK` — a capability gap, not a transport desync. Those parts have no factory-blank state and no firmware blank-check op at all.
  implication: It stays. It is orthogonal to the operator's "must work the same for any chip you CAN blank-check" constraint — SRAM/FRAM are precisely the parts you cannot blank-check.

## Open items (operator decisions, NOT decided here)

1. **Baseline re-record.** +16 B flash on all three targets makes the live `size_baseline.json`
   figures stale. Not CI-blocking (see 2026-08-29T04). Needs an adjudicated cold re-record with
   SHA-attributed `meta` prose, or an explicit decision to defer.
2. **Branch placement.** Commit `1e8bbae` landed on `gsd/v1.33-source-hygiene-firmware-size-reduction`
   — the branch of the OPEN, UNMERGED firmware PR (#56) that v1.34 exists to bench-gate. The
   submodule was at detached HEAD sitting exactly on that branch's tip (`5759dc8`), so this was the
   mechanically natural landing spot, but it widens that PR's scope with a fix for a PRE-EXISTING
   defect (Phase 162-07 already established this fault is NOT v1.33-attributable).
   **NOT pushed** — local tip `1e8bbae`, `origin` still at `5759dc8`. Meta gitlink deliberately NOT
   bumped, per the `write-empty-input-regression` precedent (gitlinks stay pinned until the beta cut).
3. **Second-chip confirmation.** Verified on W27C040 only. The fix is chip-agnostic by construction
   (it sits in the generic `_single_step_operation_callback` blank-check branch, gated on nothing
   chip-specific), and small parts never reproduced the fault because they never reach the
   ~4-5 KB cumulative-TX threshold — a 64 KB part is 32 chunks (~544 B), an order of magnitude
   under it. Confirming on a second part requires a chip swap, which is OPERATOR-ONLY.

## Follow-up fix — progress-frame chattiness (2026-08-29, operator-directed)

The ack fix made a 512 KB blank check cost 256 progress frames AND 256 ack round-trips. The
operator's direction: a progress frame relays no real data, so cap the pings and keep the byte
count down with the simplest possible algorithm.

Two throttles were tried and REJECTED on measured flash cost, both against the ack-only tree
(uno 22968):
- percent-crossing (`(address * 100) / mem_size`, static `last_pct`): a 32-bit divide, **+18 B**
  and +1 B RAM.
- address bitmask `(address & 0x1FFF) == 0`: **+18 B** as a 32-bit AND, **+8 B** narrowed to
  `(uint16_t)`, **+14 B** as a single-byte `(address >> 8) & 0x1F`.

ACCEPTED instead: widen `BLANK_CHECK_CHUNK_SIZE` 2048 -> 8192 (`firestarter/src/proms/memory.cpp`).
The emit is already one-per-chunk, so the constant alone bounds both the frame count and the
round-trip count — **zero added instructions**. A 512 KB part drops 256 -> 64 of each. Flash is
byte-identical to the ack-only tree on all three targets. Commit `a218b4f`.

Bench-verified (Leonardo /dev/ttyACM0, identity confirmed via `fw` = leonardo 3.0.0b22, W27C040):
blank 4/4 clean at 59.66-59.68s (was 61.66s at 2048), bar stepping 0x2000 and landing exactly on
0x80000/0x80000; **not-blank correctly reported** as `Not blank, at 0x000000, v: 0x92` (the real
`MSG_ERR_NOT_BLANK` payload, not the overloaded 0xA4); `write` with default blank-check INIT
79.18s; `verify` PASS 4.40s; `erase` 0.58s; chip left blank. native + native_nodevtools 184/184.

Recorded honestly: the FIRST blank check after the reflash-reset failed on a chip-ID mismatch
(0x401 vs 0xda86), then 4/4 clean with no intervention. First-read-after-reset blip, not the
transport fault.

## Open-item decisions (operator delegated the call, 2026-08-29)

1. **Baseline re-record — DECIDED: do NOT re-record here. It is a LAND-time act.**
   Measured cold (`rm -rf .pio/build/<env>` then one `pio run -e <env>`; logs captured):
   uno 22952->22968, uno328pb 23000->23016, leonardo 25098->25114, i.e. **+16 B flash on each,
   RAM byte-unchanged (1434/1440/1875)**.
   - The **growth** guard is GREEN with large margin: `--policy merge05 --baseline
     size_baseline_base01.json` exits 0, printing leonardo `-1792<=724`, uno `-1856<=788`,
     uno328pb `-1858<=788`. v1.33's own reductions dwarf this fix; no new exemption is needed.
   - The **default byte-identity** mode reports exactly `flash_used baseline=X observed=X+16` on
     all three. That is the tripwire working as designed on a changed tree, not a defect this fix
     introduced — it goes red for ANY firmware change until someone re-records at land time
     (Phase 158 Plan 04 did precisely that, as LAND-01).
   - Re-recording is not a one-line edit: `tests/test_check_size_baseline.py` hard-codes 22952 /
     23000 / 25098 in at least six places and feeds frozen `captured_build_v158_*.log` fixtures to
     the default gate, so a re-record demands the fixture-SEVERANCE pattern (a NEW version-named
     fixture family, re-point only the live-tracking legs, leave frozen families byte-unchanged) —
     see [[reference_baseline_reanchor_needs_fixture_severance]]. That is phase work, not a debug tail.
   - CI does not arm this gate at all (build.yml:142/155/193, beta-build.yml:122/128/145 run only
     `pio test -e native`, `native_nodevtools`, `pio run`), so nothing automated is left red.
   **Action for whoever lands the v1.33 PR:** re-record the live baseline with the severance
   pattern, attributing +16 B to commits `1e8bbae` + `a218b4f`.

2. **Branch placement — DECIDED: keep both commits on
   `gsd/v1.33-source-hygiene-firmware-size-reduction`** (the open fw PR #56 branch).
   v1.34 exists to bench-gate v1.33's three unmerged PRs; this defect is exactly what that gate
   was built to catch. Landing the fix inside the PR under gate is the point of the exercise. The
   alternative — merge v1.33 carrying a known standalone-blank-check failure, then fix it in a
   follow-up PR — is strictly worse. Both commits remain **UNPUSHED**; the operator pushes.
   Meta gitlink deliberately NOT bumped, per the `write-empty-input-regression` precedent.

3. **Second-chip confirmation — DECIDED: non-blocking, left as an operator ask.**
   A chip swap is operator-only, so this cannot be closed from here. The fix is chip-agnostic by
   construction (generic `_single_step_operation_callback` blank-check branch plus a constant in
   `mem_util_blank_check`; nothing keys on part identity), and small parts never reproduced the
   original fault because they never reach the ~4-5 KB cumulative-TX threshold. **One-line ask:**
   next time any smaller part is seated, run `firestarter blank <part>` once and confirm the bar
   advances and the verdict returns.
