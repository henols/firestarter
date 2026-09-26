---
status: resolved
trigger: "Phase 145 Gate 2, cycle 1, Attempt 1: `firestarter -v -p /dev/ttyACM0 write W27C512 img1.bin` exits 1 with 'Byte at 0x000000 failed to program within 25 pulses' (MSG_ERR_MAX_PULSES, 0xBD) on the very first byte of the very first block. Erase, blank-check, chip-id and idle VPP all pass. Phase 145 HALTED on this; STATE.md hands it to a debug session. Find root cause and fix."
created: 2026-08-16
updated: 2026-08-16
resolved: 2026-08-16
related_phase: 145-bench-validation
milestone: v1.31
sub_repo: firestarter + firestarter_app (lockstep candidate)
goal: find_and_fix
---

# Debug Session: w27c512-program-fail-byte0

## Symptoms

DATA_START

**Expected behavior:** `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img1.bin`
programs all 65536 bytes and passes the firmware-side verify, exit 0. This is Gate 2 cycle 1 of
Phase 145 (three 64 KiB cycles, pass rule = 3/3 byte-exact on both oracles).

**Actual behavior:** exit 1 after 9.4s. The write aborts on the **first byte of the first block**,
offset `0x000000`, on the first pulse attempt of the entire cycle. No block ever completed.

**Error message (verbatim, 2026-08-16):**

```
ERROR  :RURP         : 342: ERROR: Byte at 0x000000 failed to program within 25 pulses
ERROR  :EpromOperator: 622: Programmer error during WRITE: Byte at 0x000000 failed to program
within 25 pulses -- the write aborted at this address: bytes before this block were already
programmed, this block is only partially programmed, and no later block was attempted. The
firmware stops accepting blocks for this write and its address counter does not advance, so
re-running the write repeats the whole file from the start. A byte that will not converge like
this usually means insufficient program voltage or a worn or failing cell, not a timing problem.
ERROR  :EpromOperator:1986: Write to W27C512 failed.
```

Message is `MSG_ERR_MAX_PULSES` = `0xBD`, defined in `firestarter/tools/catalog/messages.toml:682`
(`"Byte at 0x%06x failed to program within %d pulses"`, params u24 addr + u8 pulses).

**Timeline:** First 64 KiB write attempted under the v1.31 programming-algorithm changes.
Phases 138–144 (host/firmware algorithm work, tests, build) all closed green; Phase 144 was
8/8 with both standing REDs retired. Gate 1 of Phase 145 (`erase W27C512 -b`) PASSED on the same
board and the same seated part immediately before this. So the failure appeared on the **first
real programming operation** exercised against the v1.31 algorithm path on hardware.

**Reproduction:** `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img1.bin`
Board: Leonardo, `3.0.0b17`, on `/dev/ttyACM0`. Shield: Rev 2.0. Part: Winbond W27C512, seated,
declared expendable ("you can erase or do anything its a test ic for you").

DATA_END

## Initial Evidence (from 145-BENCH-LOG.md, Gate 2 Cycle 1 Attempt 1)

**What still worked — this bounds the fault to the program step specifically:**
- Port identity re-verified fresh: `firestarter -p /dev/ttyACM0 fw` →
  `Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0`.
  Identical to 145-04's recorded value; no re-enumeration.
- `firestarter -p /dev/ttyACM0 id W27C512` → exit 0, `Chip ID check passed for W27C512`
  (`0xda08`). Rules out chip-id mismatch / wrong part.
- The INIT-phase blank-check streamed cleanly through the **entire** 65536-byte space
  (`DATA: 2048/65536` … `DATA: 65536/65536`, then `INIT: (init done)`). The whole part read as
  blank going in — consistent with 145-04's `erase W27C512 -b` passing its own post-erase blank
  check. **The chip was blank and fully readable. Only the program step failed.**
- `firestarter -p /dev/ttyACM0 vpp -t 5` post-failure → **12.0V, Internal VCC 5.5V**, stable
  across all ten frames, in-band (11400–12500 mV), unchanged from Gate 1.

**What failed:** bit-programming under load, first byte, first pulse attempt, `MAIN` phase
(not `INIT`).

**Explicitly NOT ruled out — the idle VPP reading does not close this:**
12.0V/5.5V is an *idle* sample with no pulse in flight. Program-window voltage at the socket
under load was **never measured** — the held-rail DMM proxy is defeated by DTR-reset-on-close
(standing Phase-97 tooling gap). An in-band idle reading and a droop-under-load failure are not
in tension; the tooling on hand cannot distinguish them.

**Observation handed over WITHOUT a claim (bench log's words):** `vpp -t 5` also reports
`Internal VCC: 5.5V`, and v1.31 carries a known **6.25V program-VCC evidence ceiling**
(unreachable on this shield) as standing context. The bench log names the two figures side by
side for debug's benefit but makes **no claim either way** — no measurement taken distinguishes a
program-VCC explanation from a marginal/worn part from an unmeasured VPP droop.

## Prime suspects to discriminate (not yet tested)

1. **v1.31 algorithm-fidelity regression** — the pulse/verify loop, pulse_duration sourcing
   (DB data, not a constant), or the max-pulse budget introduced in phases 138–144. This is the
   only thing that changed since W27C512 last wrote successfully. Strongest a-priori candidate
   and the only one testable purely in software.
2. **Pulse duration / DB value wrong for W27C512** — v1.31 made pulse a database field. Check the
   value actually reaching the firmware for W27C512 versus what previously worked (100 µs was the
   Phase-57 figure) and versus the datasheet at `firestarter_app/datasheets/W27C512.pdf`.
3. **Verify-after-pulse readback path** — if the post-pulse readback is wrong (bus timing, OE/CE
   sequencing, reading before the cell settles), a byte that *did* program reads back unprogrammed
   and the loop burns all 25 pulses. Note the plain read path is proven good by the blank check.
4. **VPP droop under program load** — physically plausible, but see constraints: not measurable
   this session.
5. **Worn/failing part** — cannot be discriminated by swapping this session (no chip handling).

## Constraints for this session (operator-set)

- **ALLOWED:** drive `/dev/ttyACM0` live — `firestarter` read / id / vpp / vpe / erase / write /
  dev commands, firmware rebuild + flash to the attached Leonardo.
- **NOT AVAILABLE:** chip handling. No re-seat, no swapping in a second W27C512, no moving to a
  different shield or board. D-09's re-seat allowance stays unconsumed.
- **NOT AVAILABLE:** DMM readings. Program-window VPP droop cannot be measured this session.
- Therefore: **prioritise causes that are discriminable in software and over the wire.** If the
  investigation converges on a cause that needs a DMM or a second part, say so plainly and stop
  there rather than guessing — that is a legitimate terminal state for this session.
- Part is expendable; erases and write attempts on it are authorized.

## Environment

- Meta repo `/workspaces`, branch `gsd/v1.31-27c-programming-algorithm-fidelity`.
- `firestarter/` and `firestarter_app/` both on `gsd/v1.31-27c-programming-algorithm-fidelity`.
- Board: Leonardo, fw `3.0.0b17`, `/dev/ttyACM0`. Port free — no process holds it.
- Test image: `.planning/phases/145-bench-validation/images/img1.bin` (64 KiB).
- Prior logs: `.planning/phases/145-bench-validation/logs/write_cycle1_attempt1.stdout.log`
  and `.stderr.raw` (preserved off the canonical names; do not overwrite).
- Full narrative: `.planning/phases/145-bench-validation/145-BENCH-LOG.md`, Gate 2 section.

## Current Focus

status: RESOLVED — root cause confirmed, fix applied, verified on hardware, committed.

root cause: v1.31 Phase 141 deleted the only code that asserted the program-voltage route
(`CTRL_VPE_ENABLE`) around a program pulse, so every 27C program strobe went out with the 12 V
rail generated but never switched onto the socket. See the Resolution block at the bottom.

fix: `firestarter` commits `eb563d2` + `ebe9cb3` on
`gsd/v1.31-27c-programming-algorithm-fidelity`.

verified: 12/12 byte-exact 64 KiB write+read-back cycles at the shipped settle values, on the
same board and the same seated part that failed Gate 2; final run made from the exact committed
tree. Full software gate results in Resolution.verification.

next_action: none for this session. Four items are handed back to Phase 145 / the operator —
see "Open items handed back" at the bottom, of which the MERGE-05 band breach (+96 B against a
0 B leonardo band, deliberately not laundered) is the one needing a decision.

## Evidence

- (see Initial Evidence above — carried from the bench log)

- timestamp: 2026-08-16
  checked: `firestarter/data/chip_database.json` (generated) for W27C512, and
    `.planning/phases/145-bench-validation/images/img1.bin` byte 0.
  found: W27C512 = WINBOND row, `algorithm 7` (0x07), 28 pins, `pulse_duration "100 us"`,
    `pinout DIP28_27512`, `vpp_mv 12000`, `chip_id_value 0x0000da08` — matches the bench-observed
    id exactly. img1.bin is 65536 B, byte 0 = 0x00, 65408 of 65536 bytes are non-0xFF.
  implication: SUSPECT 2 (wrong pulse/DB value) is ELIMINATED — 100 µs is the historical
    Phase-57 figure and is what the DB carries. Byte 0 being 0x00 (not 0xFF) explains why the
    LOOP-06 `expected == 0xFF` skip does not fire and the very first byte is the one that fails.

- timestamp: 2026-08-16
  checked: `eprom_params.cpp` row for 0x07 and `configure_eprom`'s pulse fallback.
  found: 0x07 row = `{ overprogram_cap_us 75000, energy_cap_us 0, max_pulses 25,
    overprogram_factor 0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR }`. energy_cap_us 0
    means UNCAPPED, so the pre-flight `MSG_ERR_PULSE_TOO_WIDE` refusal and `MSG_ERR_ENERGY_CAP`
    are both structurally unreachable on this row; `max_pulses` 25 is the only live budget, which
    is exactly the number the error reported.
  implication: the budget values are internally consistent. The 25-pulse exhaustion is a real
    non-convergence, not a mis-set budget.

- timestamp: 2026-08-16
  checked: `git show 30850845:src/proms/eprom.cpp` (the v1.31 branch point = last known-good
    write path) vs `HEAD:src/proms/eprom.cpp`; every `set_control_register` call site in each.
  found: the old path had FOUR control-register writes per block —
    (1) `REGULATOR|DROP` once per block + `delay(500)`,
    (2) `CTRL_VPE_ENABLE = 1` + `delay(10)` at the top of `program_mismatched_bytes()`,
    (3) `CTRL_VPE_ENABLE = 0` at the bottom of it, before `verify_and_update_mask()`,
    (4) `REGULATOR = 0` on failure.
    The new path has only (1) `eprom_hv_route_mask(handle) = 1` + `delay(500)`, and
    `EPROM_HV_ALL_OFF_MASK = 0` on error. `CTRL_VPE_ENABLE` is set to 1 NOWHERE in the v1.31
    write path. `eprom_hv_route_mask()` returns only `CTRL_VPP_REGULATOR_ENABLE` or
    `EPROM_HV_ROUTE_MASK` (= REGULATOR|DROP) — neither contains 0x04.
  implication: ROOT CAUSE CANDIDATE, from source alone.

- timestamp: 2026-08-16
  checked: `src/proms/memory.cpp::memory_set_data` — the function the per-byte loop calls to
    emit a pulse.
  found: `rurp_chip_input(); remap_address(WRITE_FLAG); set_address(); write_data_buffer();
    delayMicroseconds(3); rurp_chip_enable(); mem_util_delay_us(pulse_delay); rurp_chip_disable();`
    It touches NO control register. Also `mem_util_remap_address_bus` only raises a `vpp_line`
    bit for chips that have one, and DIP28_27512's vpp-pin is 22 which `database.py:295` maps to
    ROM_OE and then deliberately DROPS (`vpp_line` stays the 0xFF sentinel).
  implication: the program-voltage route is 100% the caller's responsibility, and for W27C512
    there is no shift-register vpp_line to carry it either. Nothing else can be supplying it.

- timestamp: 2026-08-16
  checked: the project's own two empirically-captured golden strobe traces —
    `test/native/avr/_shared/eprom_v131_expected_prechange.h` (frozen PRE-v1.31 capture) vs
    `test/native/avr/_shared/eprom_v131_expected.h` (Phase 144 POST-v1.31 capture). Extracted
    every value latched into CONTROL_REGISTER in each.
  found:
    PRE  0x07: {0x81, 0x85, 0x91, 0x95}  -> 0x04 (CTRL_VPE_ENABLE) SET during the program pass
    PRE  0x08: {0x80, 0x81, 0x88, 0x89, 0xc0, 0xc8} -> 0x08 (CTRL_VPP_P1_ENABLE, the remapped
               form for a using_p1_as_vpp handle) SET during the program pass
    PRE  0x0B: {0x80, 0x88}              -> 0x08 SET during the program pass
    POST 0x07: {0x81, 0x91}              -> NEITHER 0x04 NOR 0x08 EVER SET
    POST 0x08: {0x80, 0x81, 0xc0}        -> NEITHER EVER SET
    POST 0x0B: {0x80}                    -> NEITHER EVER SET
    Decoded PRE 0x07 sequence: ctrl<-0x81, delay 500 ms, ctrl<-0x85, delay 10 ms, then OE=1 /
    data / CE-low-100us program strobes. Decoded POST 0x07 sequence: ctrl<-0x81, delay 500 ms,
    then straight into OE=1 / data / CE-low-100us strobes with ctrl still 0x81.
  implication: ROOT CAUSE CONFIRMED from the repo's own captured hardware-intent traces, on all
    three EPROM protocols, not just 0x07. The v1.31 firmware pulses the chip with the high-voltage
    rail generated but never switched onto the socket. Phase 144 froze this trace as the new
    baseline and read its 198 -> 91 entry shrink as expected cadence simplification; the shrink
    actually swallowed the loss of the program-voltage assert.

- timestamp: 2026-08-16
  checked: DECISIVE EXPERIMENT. Restored the per-pulse program-voltage assert in
    `src/proms/eprom.cpp`, built leonardo (flash 26906 -> 27002 B, +96; RAM 2014 B unchanged),
    flashed `/dev/ttyACM0`, re-verified identity (`3.0.0b17, for controller: leonardo`) and
    `id W27C512` (pass), then ran the byte-identical command that produced the Gate 2 failure:
    `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img1.bin`
  found: **EXIT 0.** `Write to W27C512 successful (40.35s)`, wall clock 44 s. All 64 blocks
    completed; no MSG_ERR_MAX_PULSES, no MSG_ERR_VERIFY, and the firmware's own
    VERIFY_PER_PULSE_PLUS_FINAL full-array pass ran clean. Independent read-back oracle:
    `firestarter -p /dev/ttyACM0 read W27C512 <out>` (7.40 s) then a byte compare against the
    source image — 65536/65536 BYTE-EXACT, sha256
    `f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a` on both sides.
  implication: ROOT CAUSE CONFIRMED AND FIX VERIFIED ON HARDWARE. One code change flipped a
    100%-reproducible first-byte failure into a byte-exact 64 KiB write on the same board, the same
    shield and the same seated part, with no chip handling and no voltage adjustment. This also
    retroactively eliminates suspects 4 and 5 FOR THIS PART: a part that programs 65408 bytes
    byte-exact is not worn out, and a rail that cannot hold program voltage under load does not
    produce a byte-exact 64 KiB write. Neither was measured — both are excluded by outcome.

- timestamp: 2026-08-16
  checked: STABILITY. Committed the fix (`eb563d2`), rebuilt leonardo from the committed tree,
    re-flashed, and ran two further independent cycles with different 64 KiB images.
  found: **Cycle 2 (img2.bin) FAILED — but with a DIFFERENT symptom.** exit 1 after 26 s, at
    ~48% through: `ERROR: 0x85 != 0xc5 at 0x007acf` (MSG_ERR_VERIFY, 0xAF), not
    MSG_ERR_MAX_PULSES and not at byte 0. Cycle 3 (img3.bin) then PASSED: exit 0,
    `successful (40.31s)`, read-back BYTE-EXACT over all 65536 bytes.
    Tally on the fixed firmware: cycle 1 PASS byte-exact, cycle 2 FAIL, cycle 3 PASS byte-exact.
  implication: the original defect is gone — 2 of 3 cycles now write and verify all 65536 bytes
    byte-exact where the pre-fix firmware could not program a single byte, and the one failure is
    a different message at a different address at a different stage. What remains is a separate,
    intermittent, single-byte defect. Its signature: expected 0x85, read 0xc5, so exactly bit 6
    stayed at 1 when it should have been programmed to 0 — an under-programmed cell. Note the
    per-pulse verify inside the loop had already MATCHED for that byte (otherwise the loop would
    have kept pulsing to max_pulses); it is the later full-array VERIFY_PER_PULSE_PLUS_FINAL pass
    that disagreed. So the cell took enough charge to read correctly immediately after its pulse
    and not enough to hold — a program-MARGIN failure, not a program-failure.

- timestamp: 2026-08-16
  checked: whether the residual is plausibly an under-settle of EPROM_VPP_SETUP_US (100 us,
    against the deleted code's 10 ms), using write time as a proxy for pulses-per-byte since no
    pulse counter is reported on success.
  found: a full 64 KiB read takes 7.40 s, i.e. ~113 us per byte including all register latching.
    A write at ~1 pulse per byte predicts roughly 3 reads/byte (LOOP-06 pre-read, per-pulse
    verify, final-pass verify) = ~22 s, plus 65408 x (100 setup + 100 pulse + 10 hold) = ~13.7 s,
    plus the per-pulse control-register writes -- about 36-40 s. Measured: 40.35 s and 40.31 s.
  implication: at 100 us setup the pulses are ALREADY EFFECTIVE — essentially every byte
    converges on its first pulse, which a grossly under-settled rail could not produce (bytes
    would need several pulses each and the write would be markedly slower). This weakens, without
    eliminating, "the settle is too short" as the residual's cause: more setup time would still
    raise per-pulse energy at the margin. It is the one remaining knob discriminable in software,
    so it is worth one experiment — but the honest reading of the timing is that the residual
    looks like a program-MARGIN limit (marginal cell, or program-window VPP droop) rather than a
    firmware sequencing error, and neither of those is measurable without a DMM or a second part.

- timestamp: 2026-08-16
  checked: SETTLE EXPERIMENT. Raised `EPROM_VPP_SETUP_US` 100 -> 1000 and `EPROM_VPP_HOLD_US`
    10 -> 100, rebuilt, flashed, and ran 11 consecutive 64 KiB cycles across all three images
    (img1/img2/img3), each write followed by an independent full read-back and byte compare.
  found: **11/11 byte-exact. Zero failures of either kind.** 719 424 programmed bytes. Write time
    ~110 s per cycle, up from ~40 s — an increase of 65408 x 900 us = 58.9 s, which matches the
    added settle almost exactly and therefore independently re-confirms ~1 pulse per byte at both
    settings (the extra time is settle, not extra pulses).
  implication: the residual margin failure did not recur. Stated with its real strength: 11/11
    against the earlier 2/3 gives p ~ 0.025 under the null of an unchanged per-byte failure rate
    (expected 3.67 failures in 719 424 bytes at the observed 1-in-196 224 rate, P(0) = 0.025).
    That is suggestive, NOT proof, and it does not identify WHICH mechanism the extra settle
    relieved. Flash is byte-identical on all three AVR targets at the new values (compile-time
    constants), so the settle change costs nothing but write time.

- timestamp: 2026-08-16
  checked: FINAL CONFIRMATION on the exact committed tree. Rebuilt leonardo from `ebe9cb3`
    (27002 B flash), re-flashed `/dev/ttyACM0`, re-verified identity, ran img1.bin.
  found: exit 0, `Write to W27C512 successful (106.02s)`, read-back BYTE-EXACT, sha256
    `f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a` — identical to the source
    image and to cycle 1's hash.
  implication: the binary built from the committed source is the binary that was verified.

- timestamp: 2026-08-16
  checked: `.planning/phases/141-per-byte-program-loop/141-PATTERNS.md:158` and `141-CONTEXT.md:220`.
  found: the pattern record instructed the executor to DELETE `program_mismatched_bytes()`
    "outright" and enumerated only its loop/bitmask mechanics. Neither it, nor 141-VERIFICATION.md,
    nor the LOOP-02 absence gate ever names the `CTRL_VPE_ENABLE` assert/release that function
    also carried. Phase 142 then rewrote HV *routing* (`eprom_hv_route_mask`) and Phase 144
    re-froze the trace, so three phases passed over the gap without any gate that asserts the
    program-voltage bit is ever high.
  implication: mechanism for how a purely-structural refactor silently dropped an electrical
    requirement. There is no regression test for "the program pulse happens with VPP routed".

## Eliminated

- hypothesis: Wrong board / wrong port — RULED OUT. `fw` re-verified `leonardo on /dev/ttyACM0`,
  identical to 145-04's value.
- hypothesis: Chip-id mismatch / wrong part in the socket — RULED OUT. `id W27C512` exit 0,
  `0xda08`.
- hypothesis: Part not erased / not blank going in — RULED OUT. Full-space blank check streamed
  clean over all 65536 bytes immediately before the failure.
- hypothesis: Read path broken — RULED OUT for the plain read path. The blank check read the
  entire part successfully. (Does NOT rule out the post-pulse verify readback, which is a
  different code path under different bus conditions — see suspect 3.)
- hypothesis: VPP rail dead or grossly out of band at idle — RULED OUT. 12.0V stable across ten
  frames, in-band. (Does NOT rule out droop under program load — never measured.)
- hypothesis: SUSPECT 2, pulse duration / DB value wrong for W27C512 — RULED OUT. DB carries
  `pulse_duration "100 us"`, which is the historical Phase-57 figure, and `max_pulses` 25 with
  `energy_cap_us` 0 (uncapped) on the 0x07 row. Nothing about the timing values is anomalous.
- hypothesis: SUSPECT 3, post-pulse verify readback is untrustworthy (bus timing / OE-CE
  sequencing) — RULED OUT as a *primary* cause. The POST-change golden trace shows the verify read
  is byte-identical in shape to the plain read the blank check already proves good (OE=0, address
  latch, CE strobe, `read_settling_us`), and it runs with the identical control-register value
  0x81. The readback is fine; there is simply nothing to read back, because the pulse before it was
  applied with no program voltage on the part.

## Resolution

root_cause: |
  Phase 141 (plan 141-04) rewrote `eprom_write_execute` as a per-byte pulse-to-verify loop and
  deleted `program_mismatched_bytes()` "outright" per 141-PATTERNS.md:158. That helper was the
  ONLY place the EPROM write path ever asserted the program-voltage route — it wrapped each
  program pass in `set_control_register(CTRL_VPE_ENABLE, 1) / delay(10) / ... /
  set_control_register(CTRL_VPE_ENABLE, 0)`. The replacement loop calls `firestarter_set_data()`
  bare, and `memory_set_data()` writes no control register of its own, so from Phase 141 until
  this fix every CE program strobe on protocols 0x07, 0x08 and 0x0B was emitted with the boost
  regulator on and dropped to 12 V but that rail never switched onto the socket's VPP node. Per
  the W27C512 datasheet's TABLE OF OPERATING MODES, Program requires CE = VIL *and* OE/VPP = VPP
  (12 V); with OE/VPP at logic level the part is simply in Output Disable. No cell could change,
  the per-pulse verify never matched, and the first byte needing a pulse — offset 0x000000, since
  img1.bin byte 0 is 0x00 and so escapes LOOP-06's 0xFF skip — exhausted `max_pulses` 25 and
  raised MSG_ERR_MAX_PULSES (0xBD).

  Why three phases passed over it: the deletion was specified structurally (remove the retry
  loop, the bitmask, the two helpers) and no record — 141-PATTERNS.md, 141-VERIFICATION.md, the
  LOOP-02 absence gate — ever named the electrical assert those helpers also carried. Phase 142
  then rewrote HV *routing* around `eprom_hv_route_mask()` and even left a comment in
  memory.cpp:165 reasoning about "why VPE survives a per-byte verify read", a belief with no code
  behind it. Phase 144 re-captured the golden strobe trace and read its 198 -> 91 entry shrink as
  expected cadence simplification. The regression was visible the whole time as a diff between
  two committed fixtures — pre-change latches 0x85/0x95 on 0x07 and 0x88/0x89/0xc8 on 0x08/0x0B,
  post-change latches neither 0x04 nor 0x08 anywhere — because no gate asserted that the
  program-voltage bit is ever high.

fix: |
  `firestarter/src/proms/eprom.cpp` — new file-static `eprom_internal_program_pulse()` asserts
  `CTRL_VPE_ENABLE` (substituted to `CTRL_VPP_P1_ENABLE` by the pre-existing
  `eprom_internal_set_control_register` on a `using_p1_as_vpp` handle, which is what restores
  0x08/0x0B's 0x88), settles `EPROM_VPP_SETUP_US`, emits the pulse, holds `EPROM_VPP_HOLD_US`,
  and releases. Both the convergence pulses and the (currently unreachable) overprogram pulse go
  through it. Per pulse rather than per block because the datasheet requires OE/VPP LOW for
  Program Verify and this loop verifies after every pulse.

  Settle values are 1000 us / 100 us, set on bench evidence rather than from the datasheet floors
  (TOES/TVS are 2.0 us MIN each). The first attempt at 100 us / 10 us fixed the headline defect
  but left an intermittent single-byte margin failure (1 of 3 cycles); 1000 us / 100 us did not
  reproduce it in 11 cycles. Cost is ~110 s per 64 KiB instead of ~40 s, against an 8 s per-block
  CAP-03 budget that leaves ample room. Flash +96 B on all three AVR targets (from the helper;
  the constants themselves are free), RAM unchanged, native warning watermark still exactly 1166.

verification: |
  HARDWARE (Leonardo 3.0.0b17, /dev/ttyACM0, Rev 2.0 shield, the same seated Winbond W27C512 that
  failed Gate 2 — no re-seat, no swap, no voltage adjustment at any point):
  - The byte-identical failing command now exits 0. 13 full 64 KiB write cycles across three
    different images, each followed by an independent `firestarter read` and byte compare:
    12 byte-exact, 1 failure. The single failure was at the FIRST settle values (100/10) and was
    a different defect (MSG_ERR_VERIFY on one under-programmed byte at 0x007acf, not
    MSG_ERR_MAX_PULSES at 0x000000). At the shipped values: 12/12 byte-exact.
  - Final run made from the exact committed tree (rebuilt, re-flashed): exit 0, byte-exact,
    sha256 f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a.
  SOFTWARE:
  - firmware pytest 314/314 (was 312/312 before; +2 legs added by this session)
  - native envs: native 141/141, native_nodevtools 141/141, native_params_v131 9/9,
    native_loop_v131 79/79, native_trace_v131 5/5
  - host app pytest 1590/1590, 30 snapshots — no app change was needed
  - `check_build_warnings.py` PASS: AVR 0 warnings, native watermark exactly 1166 (no headroom
    consumed); `check_size_baseline.py` default mode PASS against the re-anchored baseline
  - Both new/rewritten gate legs proven RED against planted violations before being trusted:
    three plants for the macro-resolution leg, one +5 us growth plant for the rewritten
    pulse-width leg.

files_changed:
  - firestarter/src/proms/eprom.cpp (the fix)
  - firestarter/include/eprom.h (EPROM_VPP_SETUP_US / EPROM_VPP_HOLD_US + full rationale)
  - firestarter/test/native/avr/_shared/eprom_v131_expected.h (re-captured, 91/115/59 -> 121/148/92)
  - firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp (value-keyed pulse-width leg rewritten structurally)
  - firestarter/tests/test_write_path_source_contract_v131.py (macro allowlist + new resolving leg)
  - firestarter/tests/test_trace_segment_exhaustiveness_v131.py (leading-settle shape; floor 885 -> 981; plants re-pointed)
  - firestarter/tests/test_check_size_baseline.py (merge05 legs re-pointed; new breach-recording leg)
  - firestarter/tests/golden/protocol_branch_inventory.json (line numbers + blob sha re-derived; 26 sites, tiers unchanged)
  - firestarter/tests/golden/eprom_v131_trace_inventory.json (counts + blob sha)
  - firestarter/scripts/baseline/size_baseline.json (+96 B flash re-anchor; BASE-01 deliberately untouched)
  - firestarter/tests/fixtures/{captured_build_*,planted_size_baseline_flash_regression,merge05_base01_anchor_*}.log, README.md
  commits:
  - firestarter eb563d2 "fix(eprom): assert the program-voltage route around every program pulse"
  - firestarter ebe9cb3 "fix(eprom): raise the VPP settles to 1000us/100us on bench evidence"
  branch: gsd/v1.31-27c-programming-algorithm-fidelity

## Open items handed back (NOT resolved by this session)

1. **MERGE-05 band breach, deliberately not laundered.** The fix is +96 B of flash on all three
   AVR targets. MERGE-05's bands are 0 B (leonardo) and 64 B (uno-class), so
   `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json`
   is RED. BASE-01 was NOT re-anchored — Phase 144 / D-11 moved that anchor once already and the
   green it produced was the anchor moving, not growth staying inside a band; doing it again from
   a debug session would hide a breach behind the same mechanism twice. The breach is recorded as
   a live assertion (`test_policy_merge05_fires_on_the_current_tree`) so it cannot rot. Whether
   the band admits a defect fix is a milestone requirements judgement for the operator.
2. **The intermittent margin failure is mitigated, not explained.** 1000 us / 100 us made it stop
   recurring across 11 cycles (p ~ 0.025), but no measurement identified whether the cause was an
   under-settled VPE route, a marginal cell, or program-window VPP droop. Discriminating those
   needs a DMM on the rail during a pulse, or a second W27C512 sample — neither available this
   session. If it ever returns, raise these two constants BEFORE concluding the part is worn.
3. **Phase 145 Gate 2 itself is not closed by this session.** Gate 2's rule is 3/3 byte-exact
   cycles; this session ran 12/12 byte-exact at the shipped values, which should satisfy it, but
   the gate is Phase 145's to run and record in 145-BENCH-LOG.md.
4. **0x08 and 0x0B were fixed but only proven in the trace, never on a part.** The same missing
   assert affected all three EPROM protocols and the golden trace now shows the route asserted on
   each. Only 0x07 (W27C512) was exercised on hardware. AM27C020 (0x08) and any 24-pin 0x0B part
   remain unverified on the bench.
5. **There is still no gate asserting that a program pulse carries program voltage.** The
   rewritten pulse-width leg and the trace fixture would now both change if the assert were
   removed again, but neither says so in those words. A direct leg — "every CE-gated,
   OE-high timing entry sits inside a control-register window with the route bit set" — would
   name the invariant this session had to rediscover from a fixture diff.
