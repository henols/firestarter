# Cell A1 — P-05 / P-06: chip seating and pot confirmation

## P-05 — Seat the W27C512 (2026-08-27, operator)

Operator reply, verbatim: *"Uno on /dev/ttyACM1, rev 2.0 shield and W27C512 seated"* — confirms
board identity (re-confirms serial `55736303739351B040E1`), shield ("rev 2.0" — canonical
`Rev 2.0`, case-only normalization), and the W27C512 (DIP28) seated.

**The pot / VPP setting was NOT separately declared by the operator in this reply. No meter
reading was supplied by the operator.** This is recorded honestly, not inferred or assumed:
`P-06`'s operator half was not answered in words. `P-06` is instead established below by
measurement — Claude's single confirming `vpp` read is the arbiter, per Standing bench rule 4
(the operator adjusts the pot himself; Claude takes exactly one confirming read, never a
monitor loop).

Circumstantial expectation (not a measurement, stated as such): Phase 160 recorded this rig
left at "pot at 12.0V" and the Rev 2.0 shield (which carries the pot) never left this Uno across
the board swaps recorded in Phase 161 Plan 02. The single confirming read below is what actually
settles this, not the expectation.

## P-06 — Single confirming `vpp` read (log `08_vpp_confirming_read`)

Command: `FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config
/workspaces/.v1.34-arms/control/.venv/bin/firestarter -p /dev/ttyACM1 vpp`

**Target:** 12.0 V for the whole cell, sourced from `rig-pins.json`'s `chips.w27c512.vpp_mv` and
`chips.w29c020.vpp_mv` (both `12000`) — this is the single pot setting for the whole cell; it is
never re-adjusted at `P-08`, because both bench chips declare the identical target.

**Tool behaviour note:** `firestarter vpp` has no single-shot flag (confirmed via
`firestarter vpp --help` — only `--help` is listed) and is inherently a continuous monitor
("Reading continuously. Press Ctrl+C to stop."). Per Standing bench rule 4 ("Claude takes
exactly one confirming read, never a live monitor loop"), the invocation was run, the **first**
reported reading was taken as the confirming value, and the process was then interrupted with
`SIGINT` (the tool's own documented stop mechanism — its stdout ends with "VPP reading stopped
by user.", exit code 0) rather than left to poll further. This is not a re-invented tolerance
check; it is the same single-read, then-stop discipline the procedure requires, applied to a
tool whose own design is a loop until interrupted.

**Measured (first reading, confirming value):** `VPP: 12.0V, Internal VCC: 5.1V`

**No numeric tolerance is stated anywhere in `PROCEDURE.md`, `rig-pins.json`, or the phase
research/pattern docs** beyond the "12.0 V" target quoted to one decimal everywhere in this
project and the historical guard-fire prose example (`VPP is high: 13.1V > 12.0V`). The
confirming reading (`12.0V`) matches the declared target **exactly** at the precision this
project records the figure everywhere else — this is not a judgment call on an invented band;
it is the reading agreeing with the target to the only precision either side is ever stated at.
(For completeness: of the readings visible in the log before the interrupt, 282 read `12.0V`
and 8 read `12.1V` — noise inside the same one-decimal bucket, not a trend away from target.)

**`--force used? No`** — no guard fired, no adjustment was needed, no bypass flag was ever
invoked.

**Verdict: `P-06` is satisfied by measurement.** No contact fault (not blank, not `0x303`), no
guard fire, no operator re-prompt needed. Proceeding to Task 5 (`P-07`, position 1).
