# Cell A2 — P-06 pot record

**Target:** 12.0 V (both bench chips declare `vpp_mv: 12000`; the pot is set once per cell, not
once per chip — the same target covers the W27C512 and the W29C020 that follows).

## Operator declaration

Operator, verbatim (via coordinator relay): "seated and set, 12.0V" — W27C512 (DIP28) seated in
the Rev 2.0 socket on the uno328pb; pot reported set and reading 12.0 V.

## Claude's confirming read (the single P-06 read for this cell)

`timeout --signal=INT 6 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config
/workspaces/.v1.34-arms/control/.venv/bin/firestarter -p /dev/ttyUSB0 vpp` (log
`11_vpp_confirm`), exactly one confirming read, no monitor loop — the `vpp` CLI has no
single-shot flag (confirmed by `--help`) and is an inherent continuous monitor
("Press Ctrl+C to stop"); the tool was interrupted via SIGINT after the first reading appeared.

First reported reading: **`VPP: 11.9V, Internal VCC: 5.3V`**. Subsequent readings in the same
brief capture before interrupt: 11.9V / 11.9V / 11.9V / 11.8V / 11.9V.

## In-band criterion — code-derived, not string-equality (corrected determination)

**The accepted window is defined in firmware, not by matching the target to one decimal place.**
Read directly from `firestarter/src/proms/eprom.cpp` (read-only inspection, no product code
changed):

- `firestarter/src/proms/eprom.cpp:713` — HIGH guard: `if (vpp_mv > (uint32_t)handle->vpp_mv +
  500)` — fires above `target_mv + 500`. For `vpp_mv=12000`: fires above **12500 mV (12.5 V)**.
  Escalates to `MSG_ERR_VPP_HIGH` (hard error) unless `FLAG_FORCE` is set, in which case it
  degrades to a warning — this project never sets `FLAG_FORCE` (forbidden flag), so in practice
  this branch is a hard stop.
- `firestarter/src/proms/eprom.cpp:736` — LOW guard: `else if (vpp_mv < (uint32_t)handle->vpp_mv
  * 95 / 100)` — fires below `95% of target_mv`. For `vpp_mv=12000`: fires below **11400 mV
  (11.4 V)**. This branch emits `MSG_WARN_VPP_LOW` — a **warning**, not an error; the low side is
  the lenient side of the guard.
- **Accepted window for a 12000 mV target: 11.4 V – 12.5 V inclusive.**

Measured **11.9 V** is comfortably inside `[11.4, 12.5]` V. The init guard does not fire at this
reading. **P-06 is satisfied — in band.**

## Correction history (recorded honestly, not silently rewritten)

This position's first determination (recorded in an earlier draft of this file) called 11.9 V
**out of band**, on the reasoning that no numeric tolerance was stated anywhere in
`PROCEDURE.md`/`rig-pins.json` beyond the one-decimal precision this project records the figure
at, and that cell A1's reading had matched its target exactly at that precision. **That
determination was wrong** and was corrected by the orchestrator against the firmware source
above. Two things the correction identified:

1. A1's exact 12.0 V match was **coincidence**, not a satisfied criterion — treating it as
   precedent manufactured a gate the project never actually had.
2. The confirming capture's own reading jittered 11.8–11.9 V; demanding exact 12.0 V from a
   reading whose own resolution/noise is ~0.1 V chases quantization noise, and any correction
   nudge would have moved the rig *toward* the 12.5 V guard for no measurement benefit.

**No pot adjustment was performed.** The operator was not asked to re-adjust; the single
confirming read stands as recorded above.

## Load-bearing lines

- **`--force used? No.`**
- **In-band criterion:** firmware guard window `[11.4, 12.5]` V for a 12000 mV target
  (`firestarter/src/proms/eprom.cpp:713`, `:736`), not string-equality to the target.
- Both readings recorded: operator's declared **12.0 V**, Claude's measured **11.9 V** — both
  within the accepted window; no disagreement requiring resolution, since the window (not exact
  equality) is the criterion.
