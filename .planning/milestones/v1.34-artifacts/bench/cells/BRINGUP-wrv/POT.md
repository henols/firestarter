# BRINGUP-wrv — Pot Record (Task 3)

**Cell:** `BRINGUP-wrv` (Uno + Rev 2.0, provenance/bring-up position — excluded from the
20-position sweep reconciliation per its `BRINGUP-` cell-id prefix)
**Chip about to be seated:** W27C512 (DIP28, 28-pin), `chips.w27c512.vpp_mv = 12000` in
`rig-pins.json`
**Board state entering this task:** Uno (ATmega328P) + Rev 2.0 shield, v1.33 arm flashed and
proven on-device by task 2 (`READBACK-VERDICT.json`: `judged_match=true`,
`judged_span_bytes=22952`), socket empty, port `/dev/ttyACM0`.

## Stated target

**12.0 V (12000 mV)**, stated to the operator before the gate was presented.

- **Source:** `rig-pins.json` `chips.w27c512.vpp_mv` = `12000`. Identical to
  `chips.w29c020.vpp_mv` (also `12000`), so this same setting stands for the whole cell — no
  re-adjustment is needed when the second chip (W29C020) is swapped in later (this cell, plan
  12 / the write-read-verify step).

## Operator's report

**Verbatim:** `"pot set"`

**Interpretation recorded, not overstated:** the operator was asked to (1) seat the W27C512
and (2) set the pot to 12.0 V, and replied with the combined confirmation "pot set". Both
steps are treated as done, since seating the chip is a precondition of a meaningful VPP
reading and the operator answered the combined ask.

**No operator instrument reading was provided.** This is recorded explicitly rather than left
blank or implied — the single confirming reading below is therefore the *only* rail
measurement recorded for this cell.

## Single confirming reading (Claude-taken, exactly one)

**VPP: 12.0 V, Internal VCC: 4.7 V** — in band, matching the 12.0 V target exactly.

- **Source:** one invocation of
  `FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 vpp`,
  captured to `logs/08_vpp_confirming_read.stdout.log` (stderr: `logs/08_vpp_confirming_read.stderr.log`, empty).
- **Value taken:** the *first* `VPP: ...` sample the app printed immediately after
  `Connecting... OK` in that single invocation.
- **No monitor loop was run by this agent.** Exactly one process was launched. No rail was
  polled or sampled repeatedly by choice.
- **Historical high-VPP init guard:** did not fire. No `VPP is high: ... > 12.0V` line appears
  anywhere in the captured output — the guard from Phase 145 D-17 was not triggered, so no
  pot re-adjustment or clean restart was needed.
- **Contact-fault check:** not applicable — the reading is a clean, in-band, non-blank value
  (not `0x303` or similarly nonsensical), so no re-seat was requested and none occurred.
- **Force flag:** never used. No flag from `rig-pins.json`'s `forbidden_flags` appears in the
  recorded invocation.

### Deviation: the `vpp` CLI subcommand has no single-shot exit mode

**[Rule 3 — blocking issue, tooling behaviour only, no product-code change]**

- **Found during:** this task's confirming read.
- **Issue:** `firestarter vpp` (`firestarter_app/firestarter/hardware.py`
  `_read_voltage_loop` / `cli_handlers.py`'s `vpp` command) streams DATA frames continuously,
  re-printing over the same line with `\r`, until either the operator sends Ctrl+C or the
  hidden `-t/--timeout` option elapses — there is no flag that reads once and exits. The
  first invocation of this command (before this session's `-t` was considered) was launched
  without a timeout and was terminated by the surrounding shell's own 120s command timeout
  (SIGTERM, exit 143) rather than by the tool's own clean exit path. The log this produced is
  a single long `\r`-joined line carrying roughly 175 consecutive samples of the SAME
  invocation (all `VPP: 12.0V` except one transient `VPP: 12.1V` reading), not 175 separate
  reads initiated by this agent.
- **Resolution:** no second process was launched. The single confirming reading recorded
  above is the *first* value that single invocation printed, read directly out of the
  already-captured log; the remainder of that log's content is disclosed here for honesty
  (per this project's anti-fabrication convention) but is explicitly NOT used as additional
  "confirming" data points, and no second `vpp` invocation was run to get a cleaner exit
  code. The forced termination is a process-lifecycle artifact of this one launch, not a
  second sampling event.
- **Why no product-code fix:** `firestarter_app/firestarter/hardware.py` already has a
  value-returning, bounded, non-printing single-shot sampler
  (`HardwareManager.sample_vpp_mv()` / `sample_vpe_mv()`, median of `n=3` DATA frames, clean
  disconnect via an explicit `DONE` message) — but it is only wired to `dev test`'s internal
  before/after energize-and-measure step (`_make_sampler` in `cli_handlers.py`), not exposed
  as its own CLI subcommand or flag. Adding such a flag would be a host-app source change,
  outside this phase's D-16 boundary (no firmware or host-app changes). Recorded here as a
  finding for a future phase, not fixed in-milestone.
- **Files touched:** none (tooling-behaviour finding only; no code changed).

## EEPROM calibration values (carried from task 2)

Recorded in `provenance.json`'s `eeprom_calibration` block, repeated here per this task's
"plus the EEPROM calibration values captured in task 2" instruction:

- `hw_revision_bucket`: `"not measured — `hw` command's revision line not found in this
  session's output"` (the same `hw`/FLAG_VERBOSE limitation documented in task 2's
  `controller_string` field).
- `r16_ohms`: `"not measured — no read-back CLI path exists for R16; firestarter config is
  write-only in this app version"`.
- `r14r15_ohms`: `"not measured — no read-back CLI path exists for R14/R15; firestarter
  config is write-only in this app version"`.
- **Cross-check against the operator:** the operator's task 1 answer to "can you read R1/R2
  off the shield?" was `"No / can't read them"`. The firmware/app path above independently
  confirms these values are unavailable from that side too — there is currently no source
  (operator or firmware) that can supply R1/R2/R16/R14R15 numerically on this rig. Both
  non-claims are recorded side by side rather than one silently standing in for the other.

## Rig state leaving this task

Uno (ATmega328P) + Rev 2.0 shield, v1.33 arm flashed and proven, **W27C512 seated**, pot at
12.0 V (confirmed in band by the single reading above), port `/dev/ttyACM0`. No avrdude
firmware operation (upload, read-back, or signature probe) has run, or will run, on this
board while the chip is seated — the Uno-class chip-out window closed at the end of task 2,
before the chip went in. No chip read/write/erase/blank-check operation has been run on the
W27C512; the write-read-verify oracle is plan 12's job, not this plan's.
