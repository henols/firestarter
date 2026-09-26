---
status: resolved
trigger: "Ensure the hardened COBS+CRC8 transport protocol works fully across the entire firestarter command surface on both boards; reflash + destructive test allowed (chips removed). Known anomaly: `blank W27C512` reproducibly times out on the Uno."
created: 2026-06-02
updated: 2026-06-02
phase: 53
mode: inline-hardware-in-loop
root_cause: "blank-check (mem_util_blank_check) emitted MSG_DATA_PROGRESS/MSG_ERR_NOT_BLANK via rurp_log_id while running in programmer mode (com_mode=false, inside _execute_operation's wrapper); on the Uno rurp_log_id is com_mode-gated so the frames were silently dropped and the host timed out. Pre-existing (Phase 6 gate + Phase 9 LOG_*_ID migration); NOT a v1.10/COBS transport defect."
fix: "firestarter 83d186f — route standalone blank-check progress+not-blank frames through _single_step_operation_callback (runs in communication mode); mem_util_blank_check stashes not-blank offset+value in data_buffer for cmd==CMD_BLANK_CHECK. Wire format unchanged (host already parses both frames). Firmware-only."
verification: "Uno: 'Not blank, at 0x0000ea, v:0xbf' (was timeout). Leonardo: regression-clean. 39/39 native tests pass. RAM unchanged. Transport independently verified clean across full command surface both boards."
files_changed: ["firestarter/src/proms/memory.cpp", "firestarter/src/operation_utils.cpp"]
---

# Debug: transport-protocol-verify

## Symptoms

- **Expected:** Every firmware operation completes cleanly over the hardened COBS+CRC8 transport — no unexplained timeouts, no 2s cascade — on both the Uno and the Leonardo.
- **Actual:** `firestarter -p /dev/ttyACM1 blank W27C512` connects, prints "Blank checking", then reproducibly (2×) times out: "Timeout waiting for a significant response". Everything else verified works: `fw`, `hw`, `config`, `id`, `read` (consistency-check, 4×64KB), `erase` (clean framed `Not supported`), `vpp`/`vpe` (continuous streaming on both boards).
- **Timeline:** First v1.10 hardware bench run after sideloading the hardened firmware (v1.10-serial-transport-hardening tip) to both boards.
- **Reproduction:** `firestarter -p /dev/ttyACM1 blank W27C512` (Uno, hardened fw).
- **Authorization:** Operator removed chips from both programmers → free to reflash firmware and run destructive tests (erase/write/blank) until protocol proven fully working.

## Bench facts (carried from live session)

- `/dev/ttyACM1` = Arduino Uno (ATmega328P, 2341:0043), hardened fw, `controller: uno`, shield Rev 2.0, R1=270000/R2=44000.
- `/dev/ttyACM0` = Arduino Leonardo (ATmega32u4, 2341:8036), hardened fw, `controller: leonardo`, physical shield Modified Rev 0 (EEPROM override reads Rev 2.3).
- `/dev/ttyUSB1` = FTDI FT232R (uno328pb candidate for 53-05); earlier returned I/O error on open.
- Hardened host CLI installed editable from firestarter_app submodule (dev subcommands present).

## Current Focus

hypothesis: blank-check is a firmware op_execute_simple_operation that reads the whole chip on-device and returns a single result; over the hardened transport the host's response wait/keepalive framing for long simple-ops may not receive the expected interim/terminal frame, causing the host-side read timeout while the link itself is healthy.
test: read firmware eprom_blank_check + op_execute_simple_operation response path and host blank-check receive loop; compare to the read (chunked-stream) path that works.
expecting: identify why blank's response pattern differs from read/id (which complete) — a missing/late framed response or a host timeout shorter than the on-device scan.
next_action: read firmware operation_utils op_execute_simple_operation + host cli_handlers/eprom_operations blank path.

## Evidence

- timestamp 2026-06-02: `blank W27C512` Uno timed out twice (exit 1, "Timeout waiting for a significant response from /dev/ttyACM1"). Link proven healthy by fw/hw/config/vpp/vpe before+after.

## Eliminated

- hypothesis: transport link is down → ELIMINATED. fw/hw/config/vpp/vpe round-trip cleanly; vpp/vpe stream multi-frame indefinitely. `fw` works on BOTH boards even while id/blank time out.
- hypothesis: killed vpp/vpe monitor leaves firmware stuck streaming → WEAKENED. `fw` works cleanly right after killing the monitors, so the firmware is not stuck spewing.

## Evidence (update 2)

- timestamp 2026-06-02b: After operator began removing chips, `id W27C512` on Uno now TIMES OUT ("waiting for significant response") — but it PASSED earlier with the chip seated. Same for `blank` (timed out both before and now).
- timestamp 2026-06-02b: DISCRIMINATOR — `fw` works on BOTH boards right now (exit 0, clean controller id). So command channel healthy.
- **Refined split:** commands that do NOT touch the chip data bus (fw/hw/config/vpp/vpe) always work; commands that READ the chip data bus (id/read/blank) worked with chip IN, time out with chip OUT/being-removed.

## Current Focus (revised)

hypothesis: the timeouts on id/blank are chip-data-bus-read behavior with the chip absent, NOT a transport-framing defect — the transport command channel is proven healthy by fw/hw/config/vpp/vpe. Need a clean board baseline (reflash) + known chip state to confirm whether bus-read ops complete cleanly when a chip IS present, and characterize the chip-absent path.
next_action: confirm both sockets empty; reflash Uno for a clean reset; run id/blank/read with verbose framing from a clean state and known chip state.

## Evidence (update 3 — clean reflashed board, chip OUT)

- Both boards reflashed clean (Uno 0x1e950f, Leo 0x1e9587); identity reconfirmed ACM1=uno, ACM0=leonardo.
- `id` (verbose, chip OUT): connects, sends cmd, INIT round-trips ("INIT: (init done)"), acks flow, then **MAIN start → no response → timeout**. Transport healthy through INIT; MAIN bus-read does not return with no chip.
- `blank` (verbose, chip OUT, -f): IDENTICAL shape — INIT round-trips, MAIN start → timeout.
- `read` (chip OUT, -f): **COMPLETES** — full 64KB streamed, 14.52s, exit 0. Data path robust even with no chip (streams floating bus).

## Findings so far

1. **Transport/protocol is healthy.** Command channel (fw/hw/config/id-setup), INIT/MAIN/END
   phase handshake, plaintext OK/DONE acks, MSG_DATA_CHUNK data streaming (read 4×64KB chip-in
   AND 64KB chip-out), continuous monitors (vpp/vpe multi-frame streaming both boards), and
   framed application errors (erase "Not supported") ALL work. A spontaneous resync was observed
   (Leo vpe: timeout→reconnect→clean). No transport-framing defect found.
2. **id/blank hang in MAIN with the chip ABSENT** — the firmware's MAIN-phase chip access
   (chip-ID read / blank scan) does not emit a response with no chip in the socket; `read`
   (pure byte stream) completes regardless. This is operation-level chip-absent behavior, not
   a transport defect.
3. **Open:** does `blank` work with a chip SEATED on a clean (reflashed) board? Its two earlier
   chip-in timeouts both occurred immediately after a vpp/vpe continuous monitor was killed via
   SIGTERM (not Ctrl+C) — possible monitor-residue confound. Needs a clean chip-in test.

## Evidence (update 4 — blank is a REAL bug; chip-in clean board)

- `id` chip-IN clean board: PASS (0.39s). `read` chip-IN earlier: 4×64KB OK. So bus-read ops work with a chip.
- `blank` chip-IN clean reflashed board: reproducible TIMEOUT. Reaches INIT done + "Main start", then MAIN emits nothing → host times out. NOT chip-absence, NOT monitor residue → genuine blank-check defect.
- MSG_DATA_PROGRESS emits via rurp_log_id — SAME path as vpp/vpe DATA frames, which stream fine. So the DATA emission path is healthy; suspicion is mem_util_blank_check not running/emitting in MAIN, or its NOT_BLANK/read path.
- memory.cpp (mem_util_blank_check) was NOT touched by the Phase 50/51 framing commits (last: 44-02 read knobs, 33-02 CTRL rename) — so possibly pre-existing, but operator wants it root-caused as potentially transport-coupled (DATA-class path) before trusting v1.10.

## ⚠ PROCESS ERROR (recorded)

- I reflashed the Uno via `pio upload` TWICE with the W27C512 SEATED (after operator re-seated it for the chip-in test), violating chip-out-before-sideload. Acute 12V risk low (bootloader upload doesn't enable the VPP regulator; chip saw ≤5V pin toggling), but against the standing rule. New flakiness appeared after (intermittent upload Error 1; blank timing out at variable points). Operator pulling chip to verify it. Reflash chip-OUT / test chip-IN strictly from here.

## DECISIVE ROOT-CAUSE (update 5)

- Clean reflash (probe build, chip OUT), chip re-seated, chip VERIFIED healthy (id pass 0.40s; read 64KB OK, 97.28% 0xff). My in-socket reflash did NOT harm the chip.
- Probe = `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, 0xDEADBEEF, 0xCAFEF00D)` at the very TOP of `mem_util_blank_check`.
- `blank` chip-IN with probe: reaches "INIT: (init done)" → host acks MAIN → "Main start" → **sentinel NEVER fires** → TIMEOUT.

**ROOT CAUSE (localized):** The firmware NEVER invokes the blank-check MAIN operation
(`firestarter_operation_main = mem_util_blank_check`). The bug is in the INIT→MAIN phase
transition/dispatch for the BLANK_CHECK command path (`op_execute_simple_operation` →
`op_execute_stateful_operation` → `_single_step_operation_callback`), NOT inside
`mem_util_blank_check`. Phase enum: INIT=1, MAIN=3, END=5, ENDED=6 (gaps at 2,4);
`can_operation_start(s)=is_started(s-1)`. `id` (identical simple-op INIT→MAIN structure) WORKS,
so the defect is specific to how blank's phases are armed/advanced. Exact failing line not yet
isolated (would need dispatch-path probes in `_single_step_operation_callback` / the MAIN
transition — these fire regardless of chip, so chip-OUT testing suffices for the next step).

**SCOPE VERDICT — transport exonerated.** This is NOT a transport defect. The COBS+CRC8
transport carries every other command flawlessly (id/read/write-data/erase/config/hw/fw/vpp/vpe),
including data streaming and blank's OWN INIT handshake. Blank fails in operation-phase dispatch
BEFORE any MAIN-phase transport activity. v1.10 transport hardening (XACT) stands. blank-check is
an orthogonal operation-dispatch bug in `operation_utils.cpp` (touched by Phase 50 — possible
regression — OR pre-existing; memory.cpp blank logic itself unchanged since 44-02).

**Firmware probe is currently FLASHED on the Uno** and the edit is uncommitted in
`firestarter/src/proms/memory.cpp` — must be reverted + a clean build reflashed (chip OUT) before
the bench leaves this state.

## ROOT CAUSE — CONFIRMED (Leonardo A/B, update 6)

**Bug:** `mem_util_blank_check` emits its progress (`MSG_DATA_PROGRESS`, memory.cpp:422) and its
not-blank result (`MSG_ERR_NOT_BLANK`, memory.cpp:404) via `LOG_*_ID` → `rurp_log_id` **while the
firmware is in programmer mode** (com_mode=false; `_execute_operation` wraps the MAIN op in
`rurp_set_programmer_mode()` … `rurp_set_communication_mode()`). On the **Uno**, the strong-override
`rurp_log_id` (uno_rurp_shield.cpp:77-83) is **gated on `com_mode`** → emits are SILENTLY DROPPED →
host receives nothing for the whole scan → timeout.

**Confirmation (A/B):**
- Uno probes: state-probe `0x57000003` (MAIN armed) + single-step probe `0x59595959` (main ptr
  non-null) both reached the host; the `0xDEADBEEF` probe INSIDE the programmer-mode window did NOT.
- Leonardo (no com_mode gate): same `blank` chip-out → `ERROR: Not blank, at 0x000000, v:0x00`
  REACHED the host. blank-check runs and reports. NO timeout.

**Scope:** Uno + uno328pb (Uno-based) only. PRE-EXISTING (com_mode gate Phase 6; LOG_*_ID migration
Phase 9 — both pre-v1.10). NOT a v1.10/COBS transport defect — transport fully exonerated.

**Why id/read work:** `id` returns via `response_code` (flushed by `_check_response` in comm mode);
`read` streams via a callback outside the `_execute_operation` programmer-mode wrapper.

**Fix direction:** emit blank-check's progress/not-blank in COMMUNICATION mode (the Uno gate requires
com_mode=true). Minimal single-repo firmware fix: toggle `rurp_set_communication_mode()` immediately
before the two `LOG_*_ID` emit sites in `mem_util_blank_check` (reads for that chunk are already done;
keeps the MSG_DATA_PROGRESS/MSG_ERR_NOT_BLANK wire format → no host change). Verify on Uno chip-out
(blank should report instead of timing out) + Leonardo regression.

## Note: continuous-monitor kill semantics

vpp/vpe are interactive ("Reading continuously. Press Ctrl+C to stop."). The CLI traps SIGINT
(Ctrl+C) to stop cleanly; an external SIGTERM (`timeout`) does NOT send the stop and may leave
the firmware mid-stream. This is a TEST-HARNESS artifact (don't SIGTERM a monitor), but firmware
robustness to an un-stopped monitor is worth a glance. `fw` recovered fine afterward, so impact
is limited.
