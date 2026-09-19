# Phase 199 — Bench record: what the rails can actually deliver

**Measured:** 2026-09-19, against meta-repo `90f8812c` on branch `v1.40-program-parameter-fidelity`.

This record holds the figures Phase 199 ships. Per D-07 the figure in Task 2 Window A becomes the
shipped threshold and cannot be re-derived without another attended bench session.

## Session setup

**Serial port identity — probed in this session, not inherited.**
Standing bench rule 1: `/dev/ttyACM*` numbering shuffles across replug, so the port is re-probed
per task rather than carried over from any earlier session or cell.

| Field | Value | How obtained |
|---|---|---|
| Device path | `/dev/ttyACM0` | only `/dev/ttyACM*` present; no `/dev/ttyUSB*` |
| Controller | `leonardo` | `firestarter -p /dev/ttyACM0 fw` |
| Firmware version | `3.0.0b31` | same invocation |
| Firmware-reported hardware | `Rev 2.0-class, Override HW: Rev 2.0-class` | `firestarter -p /dev/ttyACM0 hw` |

**The firmware-reported hardware line above is NOT evidence of the revision** and no fact in this
record is inferred from it. Standing bench rule 6: `hw_revision` cannot distinguish Rev 2.0 from
Rev 2.2 from the modified Rev 0 — they share a resistor band. It is recorded only so that a later
reader can see it agreed with the operator rather than wondering whether it was consulted.

A firmware update to `3.0.0b33` was offered by the `fw` probe and **declined**. Nothing was
flashed in this session. (That release was cut carrying zero assets and the upload cannot be re-run,
so accepting it would not have succeeded in any case.)

### Operator statements

Claude cannot verify any of the three facts below. Each is recorded verbatim as the operator's
statement, not as a measurement.

- **Shield revision (silkscreen):** *Rev 2.0*, with the controller reported as a Leonardo.
  Operator statement, 2026-09-19. D-04 scopes this session to Rev 2.0 only; a different revision
  stops the plan and re-scopes the phase rather than substituting a board.
- **Chip out of socket:** *"chip out"*. Operator statement, 2026-09-19. D-05 requires it: the
  rails are held with nothing in the socket to receive them. It stays out for the whole session.
- **Pot at maximum:** *"pot to max"*. Operator statement, 2026-09-19. Claude stated the target as
  maximum; the operator set it and is the authority on where it landed. Per standing bench rule 4
  Claude took no monitor loop, and per the standing rule recorded at ROADMAP "Phase 999.38" the
  operator's own meter — never the firmware's `vpp` figure — adjudicates the pot. **From this point
  the pot is not touched again for the rest of the session**, because every figure in this plan must
  be at one pot setting or the Task 3 pairing is meaningless.

## Task 2 — The two hold windows

*Pending.*

## Task 3 — Paired ADC reads and the error figures

*Pending.*
