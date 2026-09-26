---
status: investigating
trigger: "community dev test issue (offline): w27c512 — FAIL; failing steps: write, verify, erase, blank-check"
created: 2026-08-22T12:08:02Z
updated: 2026-08-22T16:20:00Z
---

## Current Focus

status_in_one_line: The reported #41 failure is NOT REPRODUCIBLE. The static root-cause
  hypothesis was REFUTED at the bench. Two real, independent defects were found on the way and
  are fixed and committed; neither is the cause of #41.

hypothesis: NONE SURVIVING for the #41 symptom itself. On this rig today -- same firmware
  (3.0.0b20), same host code path, same rails (vpp 12000 / vpe 13700 mV, byte-identical to the
  report), same chip (id 0xDA08 confirmed positively and by negative control) -- every operation
  #41 called BAD passes, twice: write 65536/65536 bytes correct, 5/5 full reads byte-identical,
  erase + full-device post-erase blank check OK, blank OK. The remaining best account of #41 is a
  TRANSIENT fault at the time of that run, most consistent with contact/seating: the write
  fingerprint's own classification is literally named "blank/contact", the "read runs diverged"
  symptom is not reproducible (5/5 identical), and this rig has a documented instability history.
  That is an account, not a confirmed cause, and it is stated as such.

unexplained_residual (do not lose this -- it is the one hard number that still does not fit a
  pure contact fault): #41's write step spent 99.474s over 2 cycles. Subtracting one ~10 s
  full-device read-back for the fingerprint leaves ~44 s per write cycle. A COMPLETE write of
  this pattern is MEASURED at 105.9 s, and a write that aborts at write-init's blank check costs
  ~5 s. 44 s is neither. So #41's write ran a long way and then stopped -- and the report dropped
  the error code that would say where and why. That is precisely the hole the committed host fix
  closes.

next_action: none available to this debugger without a NEW failing report. The correct next step
  is operator-side: re-run `firestarter dev test w27c512` on a host built from
  firestarter_app@debug-w27c512-devtest-all-bad (or later) the NEXT time this chip fails. That
  report will name the failing address, the byte read there, and the firmware message id for
  every BAD step, instead of `error_code: null, reason: ""`. Do not close #41 as fixed.

bench_left_in: chip BLANK and healthy; board reflashed back to the PUBLISHED 3.0.0b20 so the rig
  stays attributable (confirmed by timing signature, not by the version string -- see evidence).

## Symptoms

expected: every applicable `dev test` step reports OK for w27c512
actual: write, verify, erase, blank-check reported FAIL (report schema 1.7)
errors: none recorded (failing steps carried no reason string)
reproduction: firestarter dev test w27c512  (ALWAYS WRITES — operator go-ahead required)
started: report generated 2026-08-22T12:02:49Z; host 3.0.0b27, hw Rev 2.0-class, Override HW: Rev 2.0-class

## Context

chip: w27c512
protocol: 7
chip_id expected/actual: 55816 / None
voltage: vpp 12000 -> 12000 mV, vpe 13700 -> 13700 mV
dedup_fingerprint: 137e93501512
issue: https://github.com/henols/firestarter_prom/issues/41 (reporter: henols, opened 2026-08-22)
sibling issue: #22 — the SAME EPROM, opened 2026-08-06 on host 3.0.0b15, and the source of the
  datasheet cross-check carried into Eliminated below. Per the "one EPROM, one issue" rule
  `devtest_issues.py fold` names #22 canonical and #41 a fold-in; the fold is NOT yet applied
  (outward-facing, awaiting operator). #22's report was much milder: write OK, verify OK,
  erase OK, blank-check BAD only.
firmware on the board: 3.0.0b20:leonardo
host: 3.0.0b27 (beta tip is bf1fdc9 -> 3.0.0b28, one merge newer)
bench state at handoff: exactly one board present, /dev/ttyACM0; no process holds the port;
  no other gsd-debugger running (checked `ps aux` + `fuser`). /dev/ttyUSB* absent.

## Eliminated

- hypothesis: Pin map (28-DIP) is wrong
  evidence: datasheet says PIN CONFIGURATIONS, 28-pin DIP, pins 1–28; database has `DIP28_27512` — triage cross-check verdict MATCH — all 28 pins agree (pin 22 is the dual-function OE/VPP; firestarter labels it VPP)
  timestamp: 2026-08-22

- hypothesis: Pin count / size is wrong
  evidence: datasheet says 65,536 × 8, 28-pin 600 mil DIP; database has `pin_count: 28`, `0x10000` — triage cross-check verdict MATCH
  timestamp: 2026-08-22

- hypothesis: VPP (program) is wrong
  evidence: datasheet says Program mode: OE/VPP raised to VPP = **12V**, VCC = VCP = 5V, CE pulsed low; database has `vpp: 12V`, `vpp_mv: 12000` — triage cross-check verdict MATCH
  timestamp: 2026-08-22

- hypothesis: VCC is wrong
  evidence: datasheet says single 5V supply; VCP = 5V for programming; database has `vcc: 5V` — triage cross-check verdict MATCH
  timestamp: 2026-08-22

- hypothesis: Chip ID is wrong
  evidence: datasheet says Product Identifier with A9 = VHH (12V): manufacturer DAh, device 08h; database has `chip_id_value: 0xda08` — triage cross-check verdict MATCH
  timestamp: 2026-08-22

- hypothesis: Erase is wrong
  evidence: datasheet says electrically erasable; OE/VPP = VPE (14V), A9 = VPE (14V), A0 low, other addresses low, data inputs high, CE pulsed low; database has flags: electrically erasable — triage cross-check verdict MATCH — and the firmware does drive A9 high via `CTRL_VPP_A9_ENABLE` in `eprom_internal_erase`
  timestamp: 2026-08-22

- hypothesis: Pulse timing is wrong
  evidence: datasheet says erase within 100 mS; program pulse via CE; database has `pulse_duration: 100 us` — triage cross-check verdict MATCH
  timestamp: 2026-08-22

- hypothesis: Algorithm is wrong
  evidence: datasheet says byte program with OE/VPP at VPP, program verify with OE/VPP = VIL, CE = VIL; database has `0x07` (28-pin UV/EE, 13V VPP) — triage cross-check verdict MATCH for this part — see the note below on the shared protocol
  timestamp: 2026-08-22

- hypothesis: (Current Focus, pre-handoff) The `dev test` write step builds an UNMASKED
    address-derived payload, so on a non-blank W27C512 every byte needs an impossible 0->1 flip
  evidence: DISPROVEN by static trace. Masking is applied only for `region_policy == uv-slot`
    (chip_test.py:3079). W27C512 is electrically erasable, so `is_uv_eprom` is False and
    derive_plan gives it `full-device` policy -- and the write does not NEED a mask, because
    firmware `eprom_write_init` (eprom.cpp:145-157) calls `eprom_internal_erase` before writing
    whenever FLAG_CAN_ERASE is set and FLAG_SKIP_ERASE is not. "address-derived pattern
    (unmasked)" is a CORRECT, deliberate label for this family, not the symptom. Evidence item 5
    is a red herring.
  timestamp: 2026-08-22

- hypothesis: (Evidence item 3, pre-handoff) `write_bits_cleared: 0` / `write_bits_retained: 0`
    prove the write cleared no bit anywhere in the 65536-byte region
  evidence: DISPROVEN -- those two fields are HARDCODED literals on the unmasked path, not
    measurements. `_resolve_write_target` constructs `WriteTarget(..., masked=False,
    bits_cleared=0, bits_retained=0, ...)` (chip_test.py:3080-3088) and diagnostic_report.py:800-801
    copies them straight off the target. Only the `uv-slot` branch ever computes real counts. The
    zeros carry NO information about this run.
  timestamp: 2026-08-22

- hypothesis: (Evidence item 4a, pre-handoff) The write fingerprint (>=98% 0xFF) and the
    blank-check BAD verdict cannot both describe the same chip, so one must be failing at the
    command level
  evidence: DISPROVEN -- not a contradiction. `classify_fingerprint` returns blank/contact at
    `ff_ratio >= 0.98`, which permits up to 1310 non-0xFF bytes in 65536. "nearly blank" and "not
    blank" are simultaneously true, and that band is exactly what a partial erase produces.
  timestamp: 2026-08-22

- hypothesis: The full-device write-region widening (quick 260821-wna) caused the regression
  evidence: DISPROVEN as the cause of the erase failure. The standalone `erase` step takes no
    region and calls `erase_eprom(name, eprom_data)` with no address; `mem_util_blank_check`
    sweeps 0..mem_size for every caller regardless of the write region. The widening changed the
    write step's coverage only. It does explain why #41's write is now also gated on a
    FULL-device blank check, i.e. why the widening makes the pre-existing erase defect
    unmissable -- but it did not introduce it.
  timestamp: 2026-08-22

## Evidence

- timestamp: 2026-08-22 (orchestrator pre-handoff, code/repo inspection only — no hardware touched)
  finding: **The Phase-145 CTRL_VPE_ENABLE regression is NOT the cause.** The board runs firmware
  3.0.0b20, and `git merge-base --is-ancestor eb563d2 3.0.0b20` is TRUE — tag 3.0.0b20 is the
  current `origin/beta` tip (0 commits ahead) and contains both `eb563d2` ("assert the
  program-voltage route around every program pulse") and `ebe9cb3` (1000us/100us settles).
  So the fix that made W27C512 programmable in Phase 145 IS on this board.

- timestamp: 2026-08-22 (orchestrator pre-handoff)
  finding: **The database entry is right, and right for the right reason.** Shipped entry is
  `WINBOND / W27C512,W27E512`: algorithm 7, vpp_mv 12000, type EEPROM, size 65536,
  chip_id 0xda08, pulse_duration_us 100, pinout `DIP28_27512`, protect_off_before/on_after false,
  infoic_page_size_raw 0. `infoic_lookup.py W27C512` shows the upstream DIP28 row
  (INFOICT76 and INFOIC2PLUS agree): protocol_id 0x07, `voltages & 0xF0 = 0x00` -> VPP 12V,
  `flags & 0x10` SET -> electrically erasable, type 1 (EEPROM), size 65536. Decode is faithful;
  this is not a generator fault. Do not go looking for one.

- timestamp: 2026-08-22 (orchestrator pre-handoff)
  finding: **What `fingerprint: "blank/contact"` actually asserts.** `classify_fingerprint`
  (firestarter_app/firestarter/chip_test.py) checks blank/contact FIRST and returns it when
  `ff_ratio >= 0.98` — i.e. at least 98% of the READ-BACK bytes were 0xFF. Combined with the
  report's `write_bits_cleared: 0` / `write_bits_retained: 0`, the write step cleared no bit
  anywhere in the 65536-byte region it claimed (`write_region_start: 0`,
  `write_region_length: 65536`).

- timestamp: 2026-08-22 (orchestrator pre-handoff)
  finding: **Two internal contradictions in the report that any real root cause must explain.**
  (a) The `write` step's fingerprint says the part read back >=98% 0xFF (blank), yet the
  `blank-check` step — which runs AFTER write and erase — reports BAD (not blank). Both cannot
  describe the same chip contents, so at least one of them is failing at the command level
  rather than on data. Note every step carries `error_code: null`, so no message code was
  captured for any of the four BADs — worth asking why the code is being dropped.
  (b) `read` reports verdict OK with `reason: "read runs diverged"` — the two read runs returned
  different bytes. A solidly-blank, solidly-seated part does not produce divergent reads. Note
  `transport_health` is entirely "not measured" and `transport_suspect: false` is therefore an
  unearned reassurance, not evidence.

- timestamp: 2026-08-22 (orchestrator pre-handoff)
  finding: **`write_current_source: "address-derived pattern (unmasked)"` is the sharpest lead.**
  W27C512 is a 12V EE part on the 0x07 path: programming only clears bits (1 -> 0). Writing an
  arbitrary address-derived pattern over existing content requires 0 -> 1 flips that are
  impossible without an erase, so an UNMASKED payload fails at the cell level on a non-blank
  part while the transport looks perfectly healthy. A recently-merged quick (260821-wna, on both
  betas 2026-08-22) exists precisely to mask the dev-test payload as `P = C & D` (clear-only)
  and to introduce two thresholds — and that work has NEVER been run against real hardware.
  Establish from the code whether the mask is applied on this family/host build at all, and
  whether "(unmasked)" is a correct label for a deliberate choice or the symptom itself.

- timestamp: 2026-08-22 (orchestrator pre-handoff)
  finding: **`run_count: 2` is a CYCLE, not a retry, and the second write is normally a no-op.**
  The dev-test repeat was reworked into a cycle with per-family payloads (quick 260822-aq6,
  merged to beta today as bf1fdc9 -> 3.0.0b28). Separately, firmware LOOP-06 skips bytes that
  already read correct, so on 27C-family parts the second write emits ZERO program pulses and is
  effectively a verify. The host build in this report (b27) is one merge behind that beta tip, so
  the cycle path exercised here is very fresh code. Check whether re-running on the current tree
  reproduces at all before attributing anything to hardware.

- timestamp: 2026-08-22 (debugger, static trace -- no hardware touched)
  checked: firestarter/src/proms/eprom.cpp::eprom_internal_erase, and every
    `mem_util_delay_us(handle->pulse_delay)` call site in the firmware
  found: **THE ERASE PULSE IS THE BYTE-PROGRAM PULSE.** eprom.cpp:640 emits
    `mem_util_delay_us(handle->pulse_delay)` with CE low. `handle->pulse_delay` comes from the
    wire key `pulse-delay`, filled by database.py:401 from `programming.pulse_duration_us` = 100
    for W27C512, in MICROSECONDS. The W27C512 datasheet's CE erase pulse width T_PWE is
    95 ms min / 100 ms typ / 105 ms max. The firmware emits 100 us -- ~950x below the datasheet
    MINIMUM. The only other use of that value, `memory_set_data` (memory.cpp:409), is the
    byte-program pulse, where it is correct.
  implication: The erase is under-pulsed by three orders of magnitude, so it only PARTIALLY
    erases. CMD_ERASE installs `mem_util_blank_check` as its END phase (eprom.cpp:52) and
    `eprom_write_init` runs erase-then-blank-check (eprom.cpp:145-157), so a partial erase fails
    BOTH the erase step and the write step; verify then fails because nothing was programmed, and
    blank-check fails because the part is not blank. One cause, four BAD verdicts. This is the
    root cause.

- timestamp: 2026-08-22 (debugger)
  checked: git history of eprom_internal_erase (`git log` over the function body, 20 revisions)
  found: The erase pulse has ALWAYS been `handle->pulse_delay`; the only change in range was
    `delayMicroseconds(...)` -> `mem_util_delay_us(...)` at aeac4e7 (Phase 141 Plan 04), which
    preserved the value. Not a regression -- a long-standing latent defect.
  implication: The #22-passed / #41-failed differential is not a code change. An under-spec erase
    pulse is MARGINAL: it sometimes just manages to blank the part and sometimes does not. The
    measured VPE differs between the two reports (14600 mV in #22 vs 13700 mV in #41 -- these are
    LIVE sampler readings, cli_handlers.py:2386, not config values) and tunnel-erase rate is
    exponential in field strength. Under-spec pulse + lower rail = the flip. Both reports are the
    same defect at two points on its margin.

- timestamp: 2026-08-22 (debugger)
  checked: the host error-reporting chain -- eprom_operations.py::_run_state_machine ->
    write_eprom / verify_eprom / erase_eprom / check_eprom_blank -> chip_test.py::_dispatch_*
    -> _run_step -> diagnostic_report.py
  found: **THE FIRMWARE'S EXPLANATION IS STRUCTURALLY DISCARDED.** `_execute_phase` raises
    `EpromOperationError(message, error_code=response.id)` on an ERROR frame, but
    `_run_state_machine` CATCHES it (eprom_operations.py:631) and returns `(False, str(e))`.
    write_eprom / verify_eprom then do `is_ok, _ = self._run_state_machine(...)` -- discarding the
    text -- and return a bare bool; erase_eprom / check_eprom_blank keep `final_msg` but only log
    it on SUCCESS. `_dispatch_multi_run` therefore only ever sees `False`, and
    `_run_step`'s `except EpromOperationError: ... error_code=exc.error_code` handler
    (chip_test.py:2785-2791) is UNREACHABLE for write/verify/erase/blank-check.
  implication: `error_code: null` and `reason: ""` on all four BAD steps are produced BY
    CONSTRUCTION, not by the firmware being silent. `mem_util_blank_check` emits
    MSG_ERR_NOT_BLANK carrying the offending 3-byte address AND the byte value it read
    (memory.cpp, LOG_ERROR_ID_BYTES(MSG_ERR_NOT_BLANK, _b, 4)). That is exactly the datum that
    would have made this issue triageable in one pass -- and the report throws it away. This is a
    second, independent host defect.

- timestamp: 2026-08-22 (debugger)
  checked: StepResult.divergence vs the schema-1.7 serialiser
  found: `_dispatch_read` computes a full divergence record (cmp_len, bad-byte count, pct,
    first_offset) and `_aggregate_cycles` propagates it, but diagnostic_report.py never serialises
    it -- `divergence` appears in that file only inside a comment. The report can say "read runs
    diverged" and nothing more.
  implication: A third diagnostic-fidelity gap. Noted, not fixed here (out of this bug's scope).

- timestamp: 2026-08-22 (debugger)
  checked: which DB rows can reach eprom_internal_erase
  found: 28 rows -- algorithm 0x07/0x08/0x0B with electrical type EEPROM/Flash-EEPROM. 7 on 0x07
    (SST27SF256/512, SST27VF256/512 at 50 us; W27C257, W27C512/W27E512, W27E257 at 100 us) and
    21 on 0x08 (Winbond W27C010/020/040 and LG/MX/PT clones at 100 us; SST27SF/VF at 50 us;
    SST37VF at 10 us; M8720 at 20 us). 0x0B has none.
  implication: Blast radius of an erase-pulse fix is those 28 rows. Their current erase pulses are
    10-100 us; all are far below any electrical-erase spec. The SST parts are already being driven
    with the Winbond erase ALGORITHM (this function is the only erase the EPROM family has), so
    the pulse-width fix does not introduce a family mismatch that was not already there.

- timestamp: 2026-08-22 (debugger)
  checked: eprom_internal_erase's bus state against the datasheet erase conditions
  found: The datasheet requires the DATA INPUT pins HIGH during erase. eprom_internal_erase calls
    `rurp_chip_input()` (which only deasserts OE), sets address 0x0000, asserts
    CTRL_VPP_A9_ENABLE|CTRL_VPE_ENABLE, and pulses CE -- it never calls `rurp_write_data_buffer`
    and never sets the data-bus direction, so the bus is left in whatever state the preceding
    chip-ID read left it (input / Hi-Z).
  implication: A second, independent deviation from the datasheet erase conditions, and a possible
    co-contributor. Recorded, NOT fixed -- unlike the pulse width it cannot be settled statically.

- timestamp: 2026-08-22 (debugger)
  checked: test/native/avr/_shared/host_stubs_common.inc and test_vpp_eprom_v131
  found: A timing recorder DOES exist (HOST_STUBS_RECORD_TIMING, TIMING_KIND_DELAY_US/MS,
    timing_push) -- added in Phase 138 -- and test_vpp_eprom_v131 already installs the hooks AND
    already drives a full CMD_ERASE through configure_memory
    (test_vpp03_case_e_cmd_erase_control_stream_is_pinned_pre_rewrite).
  implication: The erase pulse width IS unit-testable in the native env. Any earlier note that
    native trace stubs cannot see time is stale.

- timestamp: 2026-08-22 (debugger -- PRIMARY SOURCE, local PDF at
    firestarter_app/datasheets/W27C512.pdf, not a web summary)
  checked: the Winbond W27C512 AC PROGRAMMING/ERASE CHARACTERISTICS and DC Erase
    Characteristics tables, and the Erase Mode prose
  found: (a) "CE Erase Pulse Width TPWE  95  100  105  mS" -- min/typ/max. The firmware emitted
    100 us. Confirms the root cause against the primary source and fixes the constant at 100 ms,
    dead centre.
    (b) "A9 Erase Voltage VID 13.75 / 14 / 14.25 V" and "VPP Erase Voltage VPE 13.75 / 14 /
    14.25 V".
    (c) Erase Mode prose and the mode table row `Erase  VIL  VPE  VIL  VPE  VCE  DIH`: CE low,
    OE/VPP at VPE, A0 low, A9 at VPE, and DATA INPUTS HIGH (DIH).
  implication: **A SECOND, INDEPENDENT out-of-spec condition on this board.** The #41 report's
    LIVE VPE reading is 13700 mV -- 50 mV BELOW the 13.75 V datasheet erase MINIMUM. The #22
    report's was 14600 mV -- 350 mV ABOVE the 14.25 V MAXIMUM, and it erased. So the rail has
    never been inside the erase window in either report; it was over on the high side when the
    erase worked and is under on the low side now. Even with the pulse-width fix, a confirming
    bench run should first have VPE trimmed to ~14.0 V. This is operator-actionable and is NOT
    something the code can fix. It also independently corroborates the marginality argument for
    why #22 passed and #41 failed.
    Point (c) is the datasheet basis for the un-driven-data-bus finding recorded above.

- timestamp: 2026-08-22 (debugger, BENCH -- operator-authorized, /dev/ttyACM0)
  checked: rig identity and part identity before any write
  found: `fw` -> "Current firmware version: 3.0.0b20, for controller: leonardo on port
    /dev/ttyACM0". Only /dev/ttyACM0 present, /dev/ttyUSB* absent, no other holder.
    `id w27c512` PASSED twice. Negative control `id m27c512` (ST, expects 0x203d) MISMATCHED and
    the host reported "Programmer reported chip ID: 0xDA08 ... matches W27C512,W27E512 WINBOND".
  implication: The seated part is definitively the Winbond W27C512 (0xDA08), not the ST M27C512.
    Rig identity matches the #41 report exactly.

- timestamp: 2026-08-22 (debugger, BENCH)
  checked: single-shot vpp/vpe sampling via HardwareManager.sample_vpp_mv/sample_vpe_mv -- the
    SAME seam `dev test`'s own sampler uses (cli_handlers.py:2386). Not the looping `vpe` CLI
    monitor, which holds the port until killed.
  found: 3 consecutive samples, all identical: vpp = 12000 mV, vpe = 13700 mV.
  implication: The rails are BYTE-IDENTICAL to the #41 report (vpp 12000, vpe 13700). VPE is
    therefore still 50 mV below the datasheet's 13.75 V erase minimum -- and, as the runs below
    show, the erase works anyway. **So the rail is NOT the #41 differential either.** The earlier
    "#22 at 14.6 V erased, #41 at 13.7 V did not" reasoning is disproven as a causal account.

- timestamp: 2026-08-22 (debugger, BENCH -- THE DECISIVE RUN)
  checked: whether a 100 us erase pulse can blank a fully-programmed W27C512, on the UNFIXED
    firmware 3.0.0b20 the #41 report was made with
  found: Sequence, all on unfixed firmware:
    1. `blank w27c512` -> BLANK, twice (the part was already blank at session start).
    2. `write w27c512 pattern.bin`, the exact 65536-byte `generate_pattern(0, 65536)` image
       `dev test` uses (ff_ratio 0.0039) -> **"Write to W27C512 successful (105.86s)"**.
    3. `blank w27c512` -> correctly FAILS: **"ERROR: Not blank, at 0x000000, v: 0x00"**.
    4. `erase w27c512` -> success in 0.48s.
    5. `blank w27c512` -> **BLANK. The whole 64 KB.**
    Repeated end to end a second time (write #2 also 105.86s, erase -b, blank) with the same
    outcome, plus 3 full reads in between: all three reads byte-IDENTICAL to each other AND
    ZERO differing bytes against the written pattern (65536/65536 correct).
    `erase -b w27c512` (which is `dev test`'s own erase shape -- the firmware installs
    mem_util_blank_check as the CMD_ERASE END phase unless FLAG_SKIP_BLANK_CHECK is set, and
    `dev test` passes flags=0) -> success in 5.06s, i.e. the post-erase full-device blank check
    RAN and PASSED.
  implication: **THE ERASE-PULSE-WIDTH HYPOTHESIS IS REFUTED AS THE CAUSE OF #41.** A single
    100 us pulse fully blanks this part at this rail voltage. The pulse width is still a real
    950x spec violation (datasheet T_PWE min 95 ms) and is still marginal by construction -- but
    it is NOT what failed in #41, and it must not be reported as the fix for it.
    Everything #41 reported as BAD passes on this rig today, on the same firmware, the same host
    code path, the same rails and the same chip. The "read runs diverged" symptom is likewise not
    reproducible: 3/3 reads byte-identical.

- timestamp: 2026-08-22 (debugger, BENCH -- host fix confirmed on real hardware)
  checked: whether the committed host error-propagation fix surfaces a real firmware error
  found: step 3 above printed **"ERROR: Not blank, at 0x000000, v: 0x00"** and "Programmer error
    during BLANK_CHECK: Not blank, at 0x000000, v: 0x00" -- the firmware's MSG_ERR_NOT_BLANK
    (0xB0) rendered with the offending address AND the byte value, off real silicon.
  implication: This is exactly the string that `dev test`'s report was discarding. The host fix
    is confirmed against hardware, and its value is now concrete: had #41 carried this, the
    triage would have had the failing address and byte for each of the four BAD steps instead of
    `error_code: null, reason: ""`.

- timestamp: 2026-08-22 (debugger, BENCH -- incidental finding, not this bug)
  checked: `erase` vs `erase -b` wall-clock
  found: plain `erase w27c512` returns "successful" in 0.48s; `erase -b` takes 5.06s. The
    difference is the full-device post-erase blank check. So the DEFAULT `firestarter erase`
    reports success having verified nothing at all.
  implication: Separate, pre-existing disclosure gap in the CLI (not in `dev test`, which passes
    flags=0 and so always gets the check). Recorded for the backlog, not fixed here.

- timestamp: 2026-08-22 (debugger, BENCH -- the FIXED firmware, flashed via
    `pio run -t upload -e leonardo --upload-port /dev/ttyACM0`)
  checked: whether the committed 100 ms erase-pulse fix breaks the working path, and whether the
    new pulse is actually emitted on silicon
  found: TWO full cycles, both clean: write 105.95 s / 105.96 s -> 0 differing bytes against the
    pattern on read-back (and 2/2 reads byte-identical); blank correctly reports "Not blank, at
    0x000000, v: 0x00"; `erase -b` 5.16 s -> success; blank -> BLANK.
    **The timing signature is the on-silicon proof of the pulse width.** `erase -b` goes
    5.06 s (published, 100 us pulse) -> 5.16 s (fixed, 100 ms pulse): +0.10 s, exactly the extra
    99.9 ms. `write` goes 105.86 s -> 105.95 s: +0.09 s, exactly write-init's own internal erase
    pulse. Both reproduced twice, stable to 10 ms.
  implication: The fix emits the datasheet pulse on real hardware and does not regress write,
    read, erase or blank-check on a real W27C512. It is a spec-compliance fix, NOT the fix for
    #41. Still unverified: that it rescues a part the 100 us pulse cannot erase -- no such part
    was available, because the one on the bench erases fine at 100 us.

- timestamp: 2026-08-22 (debugger, BENCH)
  checked: `verify` failure reporting, to complete the six-op replay
  found: `verify w27c512 pattern.bin` against the (blank) part failed with
    **"ERROR: 0x00 != 0xff at 0x000000"** -- MSG_ERR_VERIFY with expected byte, actual byte and
    address.
  implication: The verify path also has a fully-populated firmware error that the report was
    discarding. All four of #41's BAD steps have a named, address-bearing firmware error
    available; the host fix routes all four.

- timestamp: 2026-08-22 (debugger, BENCH -- rig hygiene)
  checked: restoring the board to the published firmware
  found: Rebuilt from the parent commit (88d204a == tag 3.0.0b20) and reflashed. `fw` reports
    "3.0.0b20" for BOTH builds -- the version string cannot distinguish them, the known
    host-cannot-see-prerelease-suffix limitation. Identity was instead confirmed by the timing
    signature: `erase -b` back to 5.06 s.
  implication: The bench is left on genuine published 3.0.0b20 with a BLANK, healthy chip, so any
    future report from it is attributable. To re-flash the fix:
    `cd /workspaces/firestarter && git checkout debug-w27c512-erase-pulse && pio run -t upload
    -e leonardo --upload-port /dev/ttyACM0`. NOTE the trap: a board running the fix still reports
    3.0.0b20.

## Resolution

root_cause: **#41's reported symptom: UNDETERMINED and not reproducible.** The static hypothesis
  (erase pulse width) was falsified at the bench: a 100 us pulse fully blanks this part at
  vpe 13700 mV, twice. The rival rail hypothesis was falsified the same way (identical rails,
  works). Best surviving account is a transient contact/seating fault, unconfirmed.
  TWO REAL DEFECTS were found and are fixed, neither of them the cause of #41:
  (1) FIRMWARE -- eprom_internal_erase spent `handle->pulse_delay` (the per-BYTE PROGRAM width,
      from the DB's pulse_duration_us: 100 us for W27C512, 10 us for SST37VF) as the CE ERASE
      pulse. Datasheet T_PWE is 95/100/105 ms. ~950x below the MINIMUM, marginal by construction,
      affecting 28 DB rows. Long-standing, not a regression.
  (2) HOST -- the firmware's error id and message could not reach the diagnostic report for
      write/verify/erase/blank-check, because `_run_state_machine` swallows the
      EpromOperationError that carries them and the four operator methods return a bare bool.
      Every BAD step in every such report has therefore always carried
      `error_code: null, reason: ""`. This is why #41 read as four independent faults with no
      evidence, and it is why the ~44 s-per-write-cycle residual above cannot be resolved.

fix: (1) firestarter @ debug-w27c512-erase-pulse, e58b2e3 -- EPROM_ERASE_PULSE_US = 100000UL
      (100 ms, datasheet-centred, both bounds test-asserted), plus a native timing test measuring
      the CE-low interval, plus an amended (not weakened) source-contract gate and a re-derived
      branch-inventory golden. All three AVR images byte-identical in size to the baseline.
    (2) firestarter_app @ debug-w27c512-devtest-all-bad, f39c125 -- EpromOperator records
      last_firmware_error_code / last_firmware_error_message; chip_test attaches them to non-OK
      write/verify/erase/blank-check steps. dedup_fingerprint provably unchanged.

verification: FIRMWARE fix -- native suite RED then GREEN, all 6 native envs pass (native 170, native_nodevtools 170, native_loop_v131 80,
  native_pinmap_provisional 11, native_params_v131 9, native_trace_v131 5 -- zero failures),
  322 firmware pytest gates pass, 3 AVR builds size-identical, and on-silicon N=2 with a measured
  +0.10 s pulse signature and no regression. NOT verified to rescue an under-erasing part; none
  was available.
  HOST fix -- 10 new tests, 7 of which go RED against origin/beta; full host suite 1953 pass;
  ruff clean; the only mypy error (submit.py:721) is pre-existing on pristine origin/beta.
  Confirmed on real hardware: it surfaces "Not blank, at 0x000000, v: 0x00" and
  "0x00 != 0xff at 0x000000".
  #41 ITSELF IS NOT VERIFIED FIXED, because it could not be reproduced. Do not close it.

files_changed:
  - firestarter/include/eprom.h
  - firestarter/src/proms/eprom.cpp
  - firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp
  - firestarter/tests/test_write_path_source_contract_v131.py
  - firestarter/tests/golden/protocol_branch_inventory.json
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/tests/test_devtest_firmware_error_propagation.py

open_items_for_backlog:
  - `firestarter erase` without `-b` reports "successful" in 0.48 s having verified nothing. The
    post-erase blank check is opt-in on the CLI while `dev test` always gets it.
  - StepResult.divergence (cmp_len, bad-byte count, pct, first_offset) is computed by
    _dispatch_read and propagated by _aggregate_cycles but NEVER serialised -- the report can only
    say "read runs diverged".
  - eprom_internal_erase does not drive the data bus high, which the W27C512 datasheet erase mode
    requires (mode table row: Erase = VIL / VPE / VIL / VPE / VCE / DIH). Left as-is: it is a
    bus-state claim only a bench case with an actually-under-erasing part can arbitrate.
  - VPE measures 13700 mV, 50 mV below the datasheet 13.75 V erase minimum. It erases fine, so
    this is not urgent, but the rail is out of spec on the low side and only the operator can trim
    it.
