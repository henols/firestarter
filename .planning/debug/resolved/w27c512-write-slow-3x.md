---
status: resolved
trigger: "W27C512 write is ~3-4x slower on v3.x than v2.x. gh#36 (29.71s -> 108.74s regression) + gh#42 (dev test PASS, write step 139.2s vs read 10.6s). Operator hypothesis: the HOST is chunking data too small during programming, from a misunderstanding of page writing; page programming belongs in the FIRMWARE, not the app."
created: 2026-08-22
updated: 2026-08-22
resolved: 2026-08-22
shipped_as: firmware 3.0.0b22 (PR henols/firestarter#55, merged to beta)
goal: find_and_fix
sub_repo: firestarter_app (+ firestarter if the seam is on the wire)
issues: [36, 42]
bench: /dev/ttyACM0 = leonardo, fw 3.0.0b20, Rev 2.0-class, W27C512 seated
---

# Debug Session: w27c512-write-slow-3x

## Symptoms

DATA_START

**Operator's verbatim description:**

> the w27c512 is written verry slow https://github.com/henols/firestarter_prom/issues/36 prof
> https://github.com/henols/firestarter_prom/issues/42
>
> I thint the issue is that the app is deciding to send small shunks of data while progamming and
> that is some missunderstandig about page writing.
> Several eproms whant page programming and that shall be handeled inside the FW and not by the
> app. The full buffer shall be sent over and if the eprom is requirning page writing the buffer
> data shall be sent in chunks while programming.

DATA_END

**Expected behavior:** A full 64 KiB W27C512 write completes in roughly the v2.x time (~30s), and
the host streams **full buffers** to the firmware. Any page-granular sequencing a chip needs is the
**firmware's** responsibility, applied to data already resident in its buffer.

**Actual behavior:** The write step takes 108.7s (gh#36, v3.x) to 139.2s (gh#42, this rig's
configuration) for the same 64 KiB part. v2.x did the same write in 29.71s.

**Error messages:** NONE. Both operations report success. gh#42 is a **PASS** report — every step
OK. This is a pure performance regression, not a functional failure. That matters for the fix: no
error path is involved, so the cause is in the normal, happy-path write loop.

**Timeline:** Worked at v2.x speed. Regressed somewhere in the 2.x -> 3.x line. Operator's decision
this session: pin it by **git archaeology** over the write path, NOT by installing an old host.

**Reproduction:** `firestarter -p /dev/ttyACM0 write W27C512 <64KiB image>` on the attached rig,
or the `write` step of `firestarter dev test w27c512`.

## Evidence

- timestamp: 2026-08-22 (orchestrator, pre-seed)
  source: gh#36 body
  fact: v2.x "Write to W27C512 successful (29.71s)." -> v3.x "Write to W27C512 successful (108.74s)."
    Same chip, same operation. 3.66x slower. Reporter's own A/B, so host+firmware both moved.

- timestamp: 2026-08-22 (orchestrator, pre-seed)
  source: gh#42 JSON, schema_version 1.7, generated 2026-08-22T15:15:10Z
  fact: Per-step durations on host 3.0.0b28 / fw 3.0.0b20:leonardo, chip w27c512, protocol **7**:
    id 3.47s | read 10.618s | write **139.172s** | verify 19.58s | erase 8.256s | blank-check 8.066s.
    write_region_start 0, write_region_length 65536 -> the write covered the FULL device.
    transport_health all "not measured", transport_suspect false.
    vpp 12000 mV / vpe 13700 mV before and after, unchanged.

- timestamp: 2026-08-22 (orchestrator, pre-seed)
  source: live probe of this rig
  fact: `/dev/ttyACM0` reports "Current firmware version: 3.0.0b20, for controller: leonardo".
    `hw` reports "Rev 2.0-class, Override HW: Rev 2.0-class". Both **byte-identical** to gh#42's
    `fw_board_identity` and `hw_revision`. This rig is the same configuration as the proof report.
    No other process holds the port. Editable install resolves to /workspaces/firestarter_app.

- timestamp: 2026-08-22 (orchestrator, pre-seed)
  source: arithmetic on the numbers above -- ORIENTATION ONLY, each term must be re-derived
  fact: A budget that shows the overhead is NOT in the silicon:
    - Pure pulse time: 65536 bytes x 100 us (W27C512 protocol 0x07 nominal) = **6.55s**.
    - Transport floor: the `read` step moved the same 65536 bytes in **10.6s**, so a full-device
      payload traverses the wire in ~10s.
    - 6.55 + 10.6 = ~17s of irreducible work. v2.x's 29.7s is plausibly close to that.
    - gh#42's 139.2s therefore carries roughly **120s of overhead that is neither pulse nor payload.**
    - Leonardo's data buffer is 1024 B -> 64 blocks for 64 KiB. 120s / 64 = **~1.9s per block**,
      which is implausibly large for one round trip -> suspect the real chunk count is much
      HIGHER than 64, i.e. the transfer granularity is far below the 1024 B buffer.
    Treat every number here as a hypothesis to confirm, not a finding. In particular the 100 us
    pulse must be read from the actual database row, not assumed.

- timestamp: 2026-08-22 (debugger, static)
  checked: host transfer granularity, end to end.
  found: `_main_phase_send_data` (firestarter_app/firestarter/eprom_operations.py:908) reads
    `file_handle.read(buffer_size)`; `buffer_size` comes from `_calculate_buffer_size`
    (:480-493) which returns `comm.firmware_max_chunk` VERBATIM; that is set in
    `serial_comm.py:395-401` from the MSG_OK_READY u16 param, clamp [1,4096]; the firmware
    advertises `DATA_BUFFER_SIZE` there (firestarter/src/firestarter.cpp:233-234), and
    platformio.ini:87 sets `-D DATA_BUFFER_SIZE=1024` for leonardo. So the host chunk is 1024 B
    and a 64 KiB write is 64 chunks. There is NO page-size or chip-derived value anywhere on the
    0x07 write path's wire granularity.
  implication: **The operator's hypothesis (host chunking too small) is REFUTED.** The host already
    sends full buffers. 120 s / 64 chunks would be 1.9 s per chunk, which is not round-trip
    latency -- it is time the firmware spends inside the block.

- timestamp: 2026-08-22 (debugger, static)
  checked: firmware 0x07 write inner loop, current beta (1e1f989).
  found: `eprom_internal_write_execute_body` (src/proms/eprom.cpp:306-521) loops PER BYTE. For each
    byte needing a pulse it calls `eprom_internal_program_pulse` (:247-253), which is:
      set_control_register(CTRL_VPE_ENABLE, 1); delayMicroseconds(EPROM_VPP_SETUP_US);
      set_data(addr, expected);                 delayMicroseconds(EPROM_VPP_HOLD_US);
      set_control_register(CTRL_VPE_ENABLE, 0);
    `EPROM_VPP_SETUP_US`=1000 and `EPROM_VPP_HOLD_US`=100 (include/eprom.h:166-167).
    `set_data` -> `memory_set_data` (src/proms/memory.cpp:401-409) spends `pulse_delay` = the DB's
    `pulse_duration_us` = **100 us** for W27C512.
  implication: cost per programmed byte = 1000 + 100 + 100 = **1200 us**, of which **1100 us is
    pure route-settle delay, not program energy**. 65536 bytes -> **72.1 s of dead delay** +
    6.55 s of actual pulse. That is the missing ~120 s, near enough.

- timestamp: 2026-08-22 (debugger, git archaeology across the 2.x->3.x boundary)
  checked: `git show 2.0.6:src/proms/eprom.cpp` (firmware tag 2.0.6, the v2.x line).
  found: v2.x used a PASS-BATCHED algorithm. `program_mismatched_bytes()` asserted `VPE_ENABLE`
    once, paid `delay(10)` ONCE PER PASS, then pulsed every mismatched byte in the block with the
    rail already up; `verify_and_update_mask()` then read the whole block with the rail down and
    rebuilt a 128-byte mismatch bitmask; up to NUMBER_OF_RETRIES=20 passes.
  implication: v2.x per-64-KiB settle cost = 64 blocks x 10 ms = **0.64 s**. v3.x = **72.1 s**.
    Same 6.55 s of pulse in both. The regression is a factor-112 amplification of the settle,
    caused by moving the pulse/verify granularity from PER PASS to PER BYTE (v1.31 Phase 141
    LOOP-01) while leaving the route assert inside the per-byte step (debug session
    w27c512-program-fail-byte0, which added the per-pulse assert to fix a real correctness bug).

- timestamp: 2026-08-22 (debugger, static)
  checked: whether this cost was already known.
  found: include/eprom.h:145-148 states it outright: "The COST, so nobody has to re-measure it:
    ~110 s per 64 KiB write, up from ~40 s at 100 us." gh#36 measured 108.74 s.
  implication: the regression is a DOCUMENTED, ACCEPTED cost of a correctness fix -- not an unknown
    defect. Nobody compared it to the v2.x 29.71 s baseline at the time. The 40 s figure quoted for
    100/10 us is ALSO above v2.x, which independently confirms the per-byte structure (not just the
    settle magnitude) carries cost v2.x did not pay.

- timestamp: 2026-08-22 (debugger, BENCH, /dev/ttyACM0, fw 3.0.0b20 as-found)
  checked: instrumented full 64 KiB write of a deterministic pseudorandom image (238 bytes of 0xFF,
    so 65298 bytes need a pulse). Harness patched `SerialCommunicator.send_bytes` to timestamp
    every '#'-framed data chunk.
  found: **chunk_count = 64. Framed chunk size 1028-1031 B (= 1024 payload + CRC8 + COBS +
    delimiter).** Inter-chunk wall time: min 1.560 s, p50 **1.568 s**, max 2.063 s, sum 99.27 s.
    `Write to W27C512 successful (105.89s)`, harness wall total 109.29 s.
  implication: (1) **The host chunking hypothesis is REFUTED by direct measurement** -- 64 chunks of
    a full 1024-byte buffer is exactly the negotiated buffer size; nothing is fragmented.
    (2) 99.3 of the 105.9 s is spent BETWEEN chunk pushes, i.e. inside the firmware's per-block
    program loop -- 1.568 s per 1024-byte block = **1531 us per byte**. The predicted per-byte
    delay cost (1000 us setup + 100 us pulse + 100 us hold = 1200 us) accounts for 78 % of it; the
    remaining ~331 us/byte is the 2-3 register-latched reads plus set_data's own register writes.
    (3) 105.89 s independently reproduces the 105.9 s "unexplained residual" recorded in
    `.planning/debug/w27c512-devtest-all-bad.md` and gh#36's 108.74 s.

- timestamp: 2026-08-22 (debugger, static, design point)
  checked: where page programming actually lives, independently of the bug.
  found: the host transports a per-chip `page-size` DATUM over the wire
    (firestarter_app/firestarter/database.py:558-567, constants.py:167) and nothing more; the wire
    CHUNK size is `_calculate_buffer_size()` = `comm.firmware_max_chunk` = the firmware's own
    `DATA_BUFFER_SIZE`, with no chip input at all. Page SEQUENCING is entirely firmware-side:
    `eeprom28c_page_mask(handle->page_size)` at src/proms/eeprom_28c.cpp:673 (algorithm 0x0D) and
    `flash_5v_page_page_size(handle->mem_size)` at src/proms/flash_5v_page.cpp:27,106-125
    (algorithm 0x05, which derives its own page size and ignores the wire field).
  implication: the operator's DESIGN INTENT is already satisfied architecturally -- full buffers on
    the wire, page sequencing inside the firmware. Nothing needs to move. The only host
    involvement is passing a database VALUE, not making a chunking decision.

- timestamp: 2026-08-22 (debugger, BENCH, after the fix, fw built from debug-w27c512-write-slow)
  checked: same rig, same deterministic image, same harness as the before-run.
  found: `Write to W27C512 successful (33.51s)`; chunk_count 64 (unchanged); inter-chunk p50
    **0.436 s** (was 1.568 s), min 0.432, max 0.936, sum 27.92 s. A second cycle on a DIFFERENT
    random image: 33.50 s, p50 0.435 s. Both cycles verified byte-exact by an independent full
    read-back: 0 mismatching bytes, sha256 equal. `verify` step: 5.69 s.
  implication: **105.89 s -> 33.51 s, 3.16x.** The falsification threshold set in the reasoning
    checkpoint (p50 must fall below 0.6 s) is met with margin. v2.x's 29.71 s is now within 13 %,
    and the remaining gap is explained: this loop still does a per-pulse verify read and a final
    full-block verify pass that v2.x did not do.

## Eliminated

- hypothesis: "The v1.32 Phase 149 wire `page-size` seam is what's mis-driving W27C512."
  why_eliminated: That seam reaches only the **0x0D** parallel-EEPROM handler, and only 18 DB rows
    gained `programming.page_size`. gh#42 records W27C512 as **protocol 7**, not 0x0D. So the
    shipped page-size code is not on this chip's code path.
  caveat: This eliminates the Phase-149 seam as the CAUSE. It does NOT eliminate the operator's
    broader design claim -- that page handling belongs in firmware -- which remains the frame for
    the fix, and it does NOT rule out some OTHER host-side chunking decision. Confirm what
    actually governs the host's transfer granularity on the 0x07 write path.

- hypothesis: "This is the same defect as the gh#41 / w27c512-devtest-all-bad session."
  why_eliminated: That session chases a FAILURE (write/verify/erase reported BAD) and concluded the
    symptom was not reproducible. gh#42 is a **PASS** with every step OK. Different symptom class.
  caveat: That session recorded an "unexplained_residual" that is a TIMING number -- it measured a
    complete write of this pattern at **105.9s** and could not account for a 44s partial. That
    105.9s measurement CORROBORATES the slowness reported here as normal-for-v3.x, and is a
    cross-check worth reusing. See `.planning/debug/w27c512-devtest-all-bad.md`.

## Current Focus

hypothesis: **REVISED (static analysis complete).** The operator's host-chunking hypothesis is
  REFUTED on the static evidence. The overhead is inside the FIRMWARE's per-byte program loop:
  `eprom_internal_program_pulse` (src/proms/eprom.cpp:247) pays `EPROM_VPP_SETUP_US`=1000 us +
  `EPROM_VPP_HOLD_US`=100 us of dead `delayMicroseconds` on EVERY BYTE that needs a pulse, because
  v1.31's LOOP-01 rewrite made the pulse->verify granularity PER BYTE while the route assert/settle
  stayed inside that per-byte step. v2.x asserted the route ONCE PER PASS (delay(10) amortised over
  1024 bytes) and verified in a separate pass. 65536 x 1100 us = 72.1 s of pure settle.

test: (1) confirm chunk size/count on the wire = 1024 B x 64 by live instrumentation (refute the
  host hypothesis with a printed number, not an inference); (2) measure per-chunk wall time to show
  the time is spent INSIDE the firmware block, not in transport; (3) A/B a firmware build that
  restores per-pass amortisation.

expecting: 64 chunks of 1024 B; per-chunk wall time ~1.2-1.7 s for a fully-programmed block.

next_action: bench-instrument a full 64 KiB write on /dev/ttyACM0 and print chunk count + per-chunk
  wall time.

reasoning_checkpoint:
  hypothesis: "A 64 KiB W27C512 (protocol 0x07) write spends 1100 us of pure route-settle delay per
    programmed byte because v1.31's per-byte pulse->verify loop calls
    `eprom_internal_program_pulse` (which asserts CTRL_VPE_ENABLE, waits EPROM_VPP_SETUP_US=1000 us,
    strobes, waits EPROM_VPP_HOLD_US=100 us, de-asserts) once PER BYTE, where v2.x asserted the
    route once PER PASS and paid delay(10) amortised over a whole 1024-byte block."
  confirming_evidence:
    - "Measured: p50 1.568 s per 1024-byte block on the bench = 1531 us/byte; 1200 us of that is
       accounted for by named delayMicroseconds calls read off the source."
    - "Measured: 64 chunks x 1024 B on the wire -- transport is NOT the cost, and the host is
       already sending full buffers."
    - "git show 2.0.6:src/proms/eprom.cpp: program_mismatched_bytes() asserts VPE_ENABLE once and
       pays delay(10) once, then pulses every flagged byte in the block."
    - "include/eprom.h:145-148 already states the cost as ~110 s/64 KiB, and gh#36 measured
       108.74 s. The two agree."
  falsification_test: "If restoring per-pass route amortisation does NOT reduce the measured
    write time, the settle is not the cost and the hypothesis is wrong. Threshold: p50 inter-chunk
    time must fall from 1.568 s to under 0.6 s."
  fix_rationale: "Restore v2.x's pass-batched structure -- assert the route once per pass, pulse
    every byte still needing a pulse, de-assert, then verify that pass's bytes -- while KEEPING
    every v1.31 semantic (LOOP-06 skips, per-byte pulse counting, max_pulses, energy cap,
    per-pulse verify, LOOP-03 overprogram at the byte's own pulse count, the final full-block
    verify pass). This addresses the root cause (settle paid per byte instead of per pass) rather
    than the symptom, and it gives BETTER program margin than either settle value ever tried,
    because every pulse after the first in a pass sees a rail that has been up for milliseconds."
  blind_spots:
    - "Holding VPE asserted across ~1000 consecutive pulses is what v2.x did for years, but this
       session has no instrument on the rail; a VPP droop over a long assert would show up as a
       final-verify failure, which the bench A/B will detect but cannot attribute."
    - "128 B of stack for the pending bitmask on leonardo (2016/2560 B static RAM used). v2.x used
       the same 128 B array on the same board, so the precedent is direct, but stack depth is not
       measured here."
    - "The native trace goldens and one loop test encode the interleaved per-byte pulse/verify
       order; a restructure moves them and they must be re-adjudicated, not silently regenerated."

## Resolution

root_cause: |
  Firmware, not host. `eprom_internal_program_pulse` (firestarter/src/proms/eprom.cpp:247-253)
  asserts the program-voltage route, waits `EPROM_VPP_SETUP_US` = 1000 us, strobes, waits
  `EPROM_VPP_HOLD_US` = 100 us and de-asserts -- and v1.31's LOOP-01 rewrite calls it once PER
  BYTE. So a 64 KiB write pays 65536 x 1100 us = 72.1 s of route settle that is neither program
  energy nor payload. v2.0.6's `program_mismatched_bytes()` asserted the route once per PASS and
  paid its settle once per pass: 64 blocks x 10 ms = 0.64 s. Constants at include/eprom.h:166-167;
  that header's own comment (lines 145-148) already predicted "~110 s per 64 KiB write" and gh#36
  measured 108.74 s -- it was simply never compared against the 29.71 s v2.x baseline.
  The operator's hypothesis (host chunking too small) is REFUTED: measured 64 chunks x 1024 B.

fix: |
  firestarter @ debug-w27c512-write-slow, commits 071d505 + 5882548 -- pass-batch the 0x07/0x08/0x0B program
  loop: a scan pass (route down, flag every byte short of target) alternating with a pulse pass
  (route asserted once, strobe every flagged byte). After the first pass the scan re-reads only the
  bytes the previous pulse pass strobed, so per-byte read counts are unchanged. Also folds
  eprom.cpp's inline copy of the final full-block verify into a call to `memory_verify_execute`
  (declared in include/memory_utils.h), buying back 262 B of AVR flash.
  NO host change: the host was already correct.

verification: |
  Bench: 105.89 s -> 33.51 s (3.16x); p50 per-block 1.568 s -> 0.436 s. Two consecutive 64 KiB
  cycles on two different random images, both byte-exact against an independent read-back
  (0 mismatches, sha256 equal). Firmware native suites (at 273eedb): native 172/172,
  native_nodevtools 172/172, native_trace_v131 5/5, native_loop_v131 80/80,
  native_params_v131 9/9, native_pinmap_provisional 11/11. AVR builds: 0 warnings on all three
  targets. Host app suite: 1970 passed.
  Size gate `check_size_baseline.py --policy merge05 --rebuild`: PASS, exit 0.

files_changed:
  - firestarter/src/proms/eprom.cpp
  - firestarter/include/memory_utils.h
  - firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
  - firestarter/include/eprom.h (5882548 -- EPROM_OVERPROGRAM_SUPPORTED)
  - firestarter/platformio.ini (5882548 -- leonardo -D EPROM_OVERPROGRAM_SUPPORTED=0)

CI GATE THIS SESSION INITIALLY MISSED -- READ THIS BEFORE PUSHING FIRMWARE WORK:
  `.github/workflows/build.yml:161` runs **`pytest tests/ -v`** in the FIRMWARE repo -- 322 (now
  323) Python gate tests -- as a hard CI step, alongside `pio test -e native`,
  `-e native_nodevtools`, `pio run` and `check_release_assets.py`. This session verified the pio
  envs and `check_size_baseline.py` but NEVER ran `pytest tests/`, and pushed; PR #55 went RED with
  11 failures while both native pio steps passed. A CI-scope grep that matches only `pio test`
  lines misses it. **Run `python -m pytest tests/ -q` in /workspaces/firestarter before any push.**
  The 11 failures were all "recorded inventory" gates -- blob SHAs, per-array entry counts, native
  case counts and literal fixture positions -- pinning exactly the two artifacts this session
  changed on purpose (`src/proms/eprom.cpp` and the re-frozen trace golden). Re-anchored at
  firmware commit 6d4d6bc; every number re-derived with each gate's own parser, never hand-edited.
  Two assertions changed in MEANING rather than anchor and are named in that commit message:
  `test_protocol_branch_inventory.py`'s non-vacuity floor (24 -> 23, because the fix legitimately
  removed 3 branch sites) and a NEW leg in `test_progress_emission_is_leonardo_only.py` that pins
  the first-pass progress-emission gate instead of letting a widened locator tolerate it.

adjudicated (operator decisions, 2026-08-22):

  - DECISION 1 -- FLASH: RESOLVED at commit 5882548. My checkpoint figures were WRONG by ~2x and
    are corrected here: the change cost leonardo +772 B, uno +476 B, uno328pb +474 B against the
    LIVE baseline (scripts/baseline/size_baseline.json), i.e. leonardo overran MERGE-05's 724 B
    allowance by **48 B only**, and uno/uno328pb both PASSED and needed nothing. My earlier
    "+1496 / needs 772 B" restated the gate's CUMULATIVE delta against BASE-01 as if it were the
    change delta. Do not reuse those numbers.
    Operator ruled: compile out the LOOP-03 overprogram path on the **leonardo target only**, no
    new exemption constant. Implemented as `EPROM_OVERPROGRAM_SUPPORTED` (default 1,
    include/eprom.h) with `-D EPROM_OVERPROGRAM_SUPPORTED=0` in platformio.ini's leonardo env; the
    switch also gates the now-single-caller static `eprom_internal_program_pulse` and the two
    locals only that site reads, because an unreferenced static/local is a warning and the AVR
    policy is zero.
    Post-guard, cold rebuild, against the live baseline:
      uno       25548 -> 26026  +478  (allowance 788)  PASS
      uno328pb  25598 -> 26074  +476  (allowance 788)  PASS
      leonardo  27630 -> 28170  +540  (allowance 724)  PASS, 184 B spare
    RAM +0 on all three; 0 warnings on all three.
    **Leonardo Caterina margin: 28672 - 28170 = 502 B** (was 270 B at 071d505; 1042 B pre-session).
    Honest correction: the guard saved 232 B, not the ~422 B I estimated at 071d505 (that estimate
    came from an earlier code variant), so leonardo landed at +540 rather than the ~+350 predicted.
    It still passes with 184 B spare, so no exemption was invented.
    Per-target behavioural divergence, stated not buried: uno/uno328pb can still emit an
    overprogram margin pulse, leonardo cannot. Unobservable today because `overprogram_factor` is
    ABSENT from all 746 chip_database.json rows (the field would sit under `programming`), so
    eprom_overprogram_us returns 0 on every target. It becomes observable the moment a row gains
    one -- whoever adds such a row must revisit the define and re-measure the Caterina margin.
    Residual on the gate itself, unclosed and NOT caused by this change: the canonical
    `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json`
    invocation still exits 1, because it measures CUMULATIVE growth against BASE-01 and the live
    position was already at +724 = exactly leonardo's whole 724 B allowance, i.e. 0 B of room. By
    the gate's own printed arithmetic it would fail for a +1 B leonardo change too. Closing it
    needs either a re-record of size_baseline.json (its documented role as the LIVE baseline) or a
    fifth exemption, and the operator has ruled the exemption out. Left for whoever lands this.
    Also pre-existing and unrelated: that invocation reports `native: cases baseline=141
    observed=170` from a stale count inside size_baseline_base01.json.

  - DECISION 2 -- TRACE GOLDEN: **REVERSED BY THE OPERATOR ON 2026-08-22. The golden IS now
    regenerated, and a CI-enforced invariant sits behind it.** Commits 453a188 + 273eedb.

    ORIGINAL RULING, kept visible so the record shows why it changed: "leave
    test/native/avr/_shared/eprom_v131_expected.h RED as a visible flag that the write cadence
    changed; a later agent MUST NOT re-freeze it; anyone shipping this branch has to consciously
    adjudicate the cadence change." That instruction is now SUPERSEDED -- do not follow it.

    WHY IT WAS REVERSED: CI does not run that suite, so the red was invisible to automation and
    the branch would have merged green with it. `.github/workflows/build.yml:142,155` and
    `beta-build.yml:122,128` run ONLY `pio test -e native` and `-e native_nodevtools`, plus the
    AVR/ARM builds and `check_release_assets.py`. They run NONE of native_trace_v131,
    native_loop_v131, native_params_v131, native_pinmap_provisional, and they do NOT run
    `check_size_baseline.py` at all. Worse, the frozen arrays encoded the PER-BYTE cadence, which
    IS the defect -- the fixture was asserting the bug we had just fixed, exactly the failure mode
    that file's own header already documents for the Phase 145 regression.

    WHAT WAS DONE (453a188): re-captured by the procedure the golden's own header documents
    (`PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP" pio test -e native_trace_v131
    --without-testing`, then run the built binary directly). Totals read verbatim from the dump
    banners, all three with strobe_overflow=0 timing_overflow=0: 0x07 121->131, 0x08 148->149,
    0x0B 92->101. Totals GREW because a pass-batched loop re-reads the block to decide the next
    pass where the per-byte loop interleaved its verify read with each pulse. The header now states
    that the arrays encode ONE route assert and ONE settle PER PASS, and that a future capture
    dropping back toward the old totals -- or showing CTRL_VPE_ENABLE (0x04) / CTRL_VPP_P1_ENABLE
    (0x08) rising once per PROGRAMMED BYTE instead of once per PASS -- means the ~3.7x regression
    has returned and must not be re-frozen without re-measuring a real 64 KiB write.
    `pio test -e native_trace_v131` is now 5/5. (5, not 6: the 6th RUN_TEST in that file is the
    dump case behind `#ifdef EPROM_V131_TRACE_DUMP`, not compiled by default. PlatformIO's own
    count line inflates by one when a case fails -- it reported "6 test cases: 3 failed, 2
    succeeded" -- which is a pre-existing reporting quirk, not a missing case.)

    THE GUARD THAT REPLACES THE RED (273eedb), and this is the substantive half: two cases added
    to `test/native/avr/test_val_eprom/test_val_eprom.cpp`, a suite in BOTH pinned envs'
    test_filter and therefore actually run by CI. They pin that the count of program-voltage route
    ASSERTS over a block scales with the PASS count, never the programmed-byte count:
      test_writeperf_route_is_asserted_once_per_pass_not_once_per_byte  -> EXACTLY 1
      test_writeperf_route_assert_count_tracks_passes_not_pulses        -> EXACTLY 2
    NON-VACUITY DEMONSTRATED, not asserted: both were run against the pre-fix per-byte loop
    planted verbatim from `git show 1e1f989:src/proms/eprom.cpp` and OBSERVED RED at
    **Expected 1 Was 8** and **Expected 2 Was 9** -- the numbers the mechanism predicts (8 bytes ->
    8 asserts; 9 pulses -> 9 asserts) -- then GREEN at 1 and 2 against the fix. Each case also
    carries its own floors so it cannot pass vacuously: response_code OK, asserts >= 1, and a
    recorder-saturation check (the shared 256-entry recorder drops its tail SILENTLY with no
    overflow flag of its own).
    Mechanism: HOST_STUBS_RECORD_BUS records `rurp_write_to_register` only, which is exactly
    enough -- each settle follows a route assert immediately, so counting RISING EDGES of the route
    bit counts settles one-for-one. Rising edges, not values-with-the-bit-set: mem_util_set_address
    writes CONTROL_REGISTER once per byte, so bit-carrying values are plentiful in BOTH cadences
    and would not discriminate.
    `scripts/baseline/size_baseline.json` native/native_nodevtools counts moved 170 -> 172 in the
    same commit (suites stay 17 -- the cases joined an existing suite), because
    check_size_baseline.py records those counts and would otherwise fail on a mismatch. The AVR
    flash/RAM figures in that file were deliberately NOT touched: no src/ file changed, and the
    AVR figures are byte-identical to 5882548's.
    `check_size_baseline.py --policy merge05 --rebuild` now **PASSES, exit 0**:
      uno 26026 [+478<=788] / uno328pb 26074 [+476<=788] / leonardo 28170 [+540<=724], RAM +0 all.

  - DECISION 3 -- 0x08 / 0x0B BENCH PROOF: **PENDING, UNCLOSED RESIDUAL. Do not attempt on this
    rig.** The fix is on the shared `eprom_write_execute` path, so it moves 0x08 and 0x0B as well
    as the reported 0x07. Bench proof exists for **0x07 only** (W27C512, three clean 64 KiB
    cycles, byte-exact); 0x08 and 0x0B rest on the native suites alone. Why it cannot be closed
    here: both erasable proxies the operator owns (W27C512, W27E257) are 0x07. The 0x08 erasable
    proxies are MX26C / PT28C / LG28C / SST27 010-040, none of which are on this bench. The only
    0x08 part known on the bench is a UV AM27C020 previously recorded MARGINAL (write#1 60/64,
    write#2 0/64, suspected VPP droop), so a failure there would be ambiguous between this new
    loop and a known-bad part -- it would prove nothing either way. Chip choice is with the
    operator. Nothing was seated or requested.
    **OPERATOR RULING (2026-08-22): DEFER 0x08 -- ship on native evidence.** The 0x08/0x0B bench
    gap is accepted and stays an explicitly stated, unclosed residual rather than a blocker. It
    must be disclosed in the PR body, not just here. Revisit if an 0x08 erasable part
    (MX26C / PT28C / LG28C / SST27 010-040) ever reaches the bench. Do NOT close this residual by
    substituting the marginal AM27C020, and do NOT quietly drop the caveat when landing.


## Resolution

root_cause: Firmware, not host. `eprom_internal_program_pulse` (firestarter/src/proms/eprom.cpp:247)
  asserted the VPE route and paid EPROM_VPP_SETUP_US=1000 + EPROM_VPP_HOLD_US=100
  (include/eprom.h:166-167) PER BYTE. 65536 x 1100 us = 72.1 s of pure settle against only 6.55 s of
  actual program pulse. v2.0.6's program_mismatched_bytes() asserted the route once PER PASS with a
  single delay(10) = 0.64 s per device. A factor-112 amplification of the same settle, introduced by
  v1.31 Phase 141 LOOP-01 (per-byte granularity) plus the w27c512-program-fail-byte0 fix, which
  correctly moved the route assert inside the per-byte step to cure a real correctness bug.
  The operator's stated hypothesis (host chunking too small) was MEASURED and REFUTED: the host
  sends 64 chunks of a full 1024 B buffer for a 64 KiB write, using comm.firmware_max_chunk
  verbatim. Page programming is ALREADY firmware-side; nothing needed moving.

fix: firestarter branch `debug-w27c512-write-slow`, two commits off beta 1e1f989:
  - 071d505 perf(eprom): amortise the VPE settle over a pass, not every byte
  - 5882548 build(leonardo): compile out the LOOP-03 overprogram site on this target only
  Host UNCHANGED (firestarter_app still on beta 3d43bf5, zero tracked changes).

verification:
  - Bench, on the ACTUAL BRANCH TIP 5882548 (leonardo re-flashed; avrdude verified 28170 bytes
    on-chip, matching the size gate's leonardo figure exactly): fresh random 64 KiB image,
    write **33.35 s**, independent full read-back **sha256 identical, 0 mismatching bytes**.
    The image was deliberately DIFFERENT from the resident one -- reusing it would let LOOP-06
    skip every already-correct byte and fake a fast result.
  - Four clean byte-exact 64 KiB cycles total: two by the debugger and one orchestrator-verified
    at 071d505 (33.51 / 33.50 / 33.49 s), plus this one at 5882548 (33.35 s).
  - Before/after: **105.89 s -> 33.35 s** on this rig (3.2x). gh#36 reported 108.74 s; v2.x 29.71 s.
  - Size gate `check_size_baseline.py --policy merge05 --rebuild` **PASSES all three, exit 0**:
    uno 26026 (+478<=788), uno328pb 26074 (+476<=788), leonardo 28170 (+540<=724, 184 B spare).
    RAM +0 everywhere. Leonardo Caterina margin 502 B against the unguarded 28672 B cliff.
  - Native suites at 273eedb: native **172/172**, native_nodevtools **172/172**,
    native_trace_v131 **5/5**, native_loop_v131 80/80, native_params_v131 9/9,
    native_pinmap_provisional 11/11. Nothing is red anywhere.
    (The +2 cases in both pinned envs are the CI-enforced cadence invariant; native_trace_v131 went
    green when its golden was re-frozen. Both are Decision 2's reversal -- see it for the
    red/green non-vacuity evidence.)

files_changed: firestarter/src/proms/eprom.cpp, firestarter/include/eprom.h,
  firestarter/include/memory_utils.h, firestarter/platformio.ini,
  firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp,
  firestarter/test/native/avr/_shared/eprom_v131_expected.h (re-frozen, 453a188),
  firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp (invariant, 273eedb),
  firestarter/test/native/avr/test_val_eprom/host_stubs.cpp (read-back model, 273eedb),
  firestarter/scripts/baseline/size_baseline.json (native counts 170->172, 273eedb)

commits: 071d505 (fix) -> 5882548 (leonardo overprogram guard)
  -> 453a188 (re-freeze golden) -> 273eedb (CI-enforced cadence invariant + baseline counts)
  all on firestarter branch debug-w27c512-write-slow. Host untouched throughout.

residuals_not_closed:
  1. 33.35 s vs v2.x's 29.71 s. Explained, not hidden: this loop keeps a per-pulse verify read AND
     a final full-block verify that v2.x did not do -- roughly 20 s of reads. A read costs ~100 us
     for a 3 us strobe, so the register-write path is a separate unexplored optimisation (~10 s).
  2. 0x08 / 0x0B have NO bench proof (Decision 3, operator-deferred). Shared code path, 0x07 only
     on silicon. Must be disclosed in the PR body.
  3. native_trace_v131 left RED by instruction (Decision 2). Must be adjudicated before beta.
  4. The BASE-01 cumulative gate invocation still exits 1 -- pre-existing, 0 B of room before this
     change, not caused by it. Needs a size_baseline.json re-record or a fifth exemption.
  5. No DMM on the VPE rail. The rail now stays asserted for a whole pass rather than per byte;
     a droop would surface as a final-verify failure, and four clean cycles is suggestive, not
     proof. The 1000/100 us settle constants were left untouched.
  6. Bench state: leonardo flashed with 5882548; the W27C512 holds tip_img.bin
     (sha256 d30ef8f1...). gh#36 and gh#42 are still OPEN and unanswered.

## Post-ship verification (orchestrator, 2026-08-22)

The PUBLISHED release artifact was verified end-to-end, not just the local build:
`firestarter fw --install --firmware-version 3.0.0b22` onto the leonardo bench board (downloaded
`firestarter_leonardo.hex` from the 3.0.0b22 release), then a full 64 KiB write of a FRESH random
image (`sha256 20ae29dd...`) -> **33.35 s**, followed by an independent full read-back that is
**byte-exact, sha256 identical, 0 mismatching bytes**.

The fresh image matters: LOOP-06 skips already-correct bytes, so re-writing the resident contents
emits zero pulses and would have faked a fast result. Every timing figure in this record used an
image the chip did not already hold.

Both community issues answered on 2026-08-22 (comment ids 5382664757 on gh#36, 5382665259 on
gh#42), each naming 3.0.0b22 and each stating plainly that only 28-pin (0x07) was verified on
silicon while the fix also moves 32-pin (0x08) and 24-pin (0x0B). Both issues deliberately LEFT
OPEN: the replies ask the reporters to confirm, so closing them would contradict the ask.

**Deliberately NOT done, with reasoning:** `firestarter/CLAUDE.md:295` still states the pinned
native envs are "asserted at exactly 141 cases / 17 suites". The real number is 172 (it was already
stale at 170 before this session). It was left alone because `beta-build.yml` intentionally carries
NO `paths-ignore`, so a docs-only merge to firmware `beta` would bump the version and publish an
entire new pre-release for a comment fix. Correct move is to let this ride along with the next real
firmware change. Same reasoning applies to any other prose-only correction in that repo.
