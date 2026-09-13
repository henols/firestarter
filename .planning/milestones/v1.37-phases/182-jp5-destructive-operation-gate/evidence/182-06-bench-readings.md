# Phase 182 Plan 06 — bench readings

Operator-taken readings. Every value here is recorded verbatim as reported. Claude took no
multimeter reading; the USB-side reads are Claude's and are marked as such.

**Session:** 2026-09-10
**Rig:** Arduino Leonardo + RURP **Rev 2.2** shield, board identity stated by the operator on sight
(`hw_revision` cannot distinguish Rev 2.2 from Rev 2.0 from a modified Rev 0).
**Port identity, verified this session:** `/dev/ttyACM0`, `controller: leonardo`, firmware
`3.0.0b22`.

## Task 1 — assumption A1: the VPE rail with the boost regulator disabled

| Field | Value |
|---|---|
| Probe point | **`J6` pin 4** (`J6` = the 4-pin "VP" socket; pin 4 is the `VPE` rail) |
| Reference point | **`J5` pin 1 (`GND`)** — the OLED header, stated by the operator. `J5`'s pinout is `1=GND, 2=+5V, 3=SCL, 4=SDA`; pin 1 is a hard board ground. Needed because `J6` carries no GND pin of its own |
| Reading | **4.9 V DC** |
| Board state | Powered, idle, no operation running, no chip seated |
| Board identity | Rev 2.2, stated by the operator on sight |
| Date | 2026-09-10 |
| Taken by | Operator (multimeter readings are operator-only in this project) |

**Verdict: A1 is CONFIRMED.** Decision threshold: a reading at or below ~6 V is a logic-level rail
and confirms the assumption; a reading at or above ~11 V is a programming rail and falsifies it.
4.9 V sits decisively in the confirming band.

### Why `J6` has no ground pin, and what its other three pins are

`J6` ("VP") is a 4-pin probe header exposing the shield's four high-voltage nodes and nothing else —
no ground, which is why an external reference was required:

| `J6` pin | Net | Node |
|---|---|---|
| 1 | `D12` cathode | the socket pin 24 (`/OE`) VPP-injection path |
| 2 | `D10` cathode | the socket pin 26 (`A9`) VPP path — the one `id` uses |
| 3 | `D31` anode = `Q8` collector | **the pin-1 VPP node — JP5's A side** |
| 4 | `VPE` | the rail measured above |

Recorded because pin 3 is the probe point for the socket-pin-1 hazard this phase gates: it is the
same copper as JP5's A-side pad and, through the bridged JP5, socket pin 1 — reachable without
going near the socket. Source: the committed `RelativelyUniversalROMProgrammer.kicad_pcb`, whose
JP4 placement matches Rev 2.2's own drill file hole-for-hole.

**Why 4.9 V is the expected confirming value, not merely "low".** The boost input is `/5V_REG`, the
fused 5 V rail, feeding both `L1` pin 1 and the `MIC2288`'s VIN (`U1` pin 5). With the switch held
off, the conducting path is `L1` → `D1` (1N5819 Schottky) → `VPE`. At no load the Schottky's forward
drop collapses toward zero, so the rail settles just under VIN. 4.9 V is that value.

**Consequence for the gate's scope (D-06).** The premise the desk trace could not measure now holds:
with `CTRL_VPP_REGULATOR_ENABLE` clear the rail is at logic level, so a `read` on an affected part
drives socket pin 1 with a logic level, not a programming voltage. `DAMAGE_CAPABLE_OPERATIONS`
stays `{write, erase}`. Task 3's conditional widening to `read`/`verify`/`blank` does **not** fire.

## Task 2a — JP4 continuity, Rev 2.2

Operator continuity probes, board unpowered, no chip seated, JP4 jumper removed for the test
(its starting position noted for restoration). Readings reported by the operator; Claude took none.

**Result — every prediction held, and the orientation is now measured rather than inferred:**

| JP4 pad | Operator's description | Board coord (PCB, +Y down) | Continuous to | Predicted? |
|---|---|---|---|---|
| Common | the pad with a neighbour on two sides at right angles | `(91.44, 81.79)` | socket pin **1** | yes |
| Pole toward the ZIF socket | "the pole facing the zif socket" | `(93.98, 81.79)` — board **+X** | socket pin **3** | **orientation newly measured** |
| Pole toward the board periphery | "the pole facing to the edge" | `(91.44, 84.33)` — board **+Y** | socket pin **25** | **orientation newly measured** |
| — | unpopulated position | `(93.98, 84.33)` — diagonal from common | — | yes, not drilled |

Negative legs, all as predicted: the two poles are **not** continuous to each other, and neither pole
is continuous to socket pin 1.

**This closes the Rev 2.2 PROBE-PENDING cell** in the VPP-destination table
(`.planning/notes/jumper-display-ground-truth.md`), which read: *"SETTLED electrically.
PROBE-PENDING residual: which physical direction is '+X' as the operator sees the silkscreen."*
It is now answered without reference to the silkscreen at all: **board +X is the direction of the
ZIF socket**, and that pole is the 28-pin destination (socket pin 3). The perpendicular pole, which
points away from the socket toward the board periphery, is the 24-pin destination (socket pin 25).

Consistency check against the layout: the socket `U5` sits at X 100.71 and beyond, JP4's common at
X 91.44 — so board +X is unambiguously socket-ward, and the operator's sighting and the netlist
agree with no residual ambiguity. `U5` pin 1 is at `(100.71, 76.33)`, pin 3 at `(105.79, 76.33)`,
pin 25 at `(118.49, 61.09)`.

**Why the fourth position is not drilled, now confirmed from both ends.** The common occupies one
corner with a selectable pole along each axis. The diagonal position could only bridge the two
poles to each other — connecting a 28-pin part's pin 1 to a 24-pin part's pin 21 with neither
carrying VPP — so it has no function and was never drilled. That is the whole mechanical content
of the Rev 2.1 → Rev 2.2 change: one added hole, 109 → 110 board-wide.

## Task 2b — JP5 is intact on this board

Operator continuity probes, same unpowered session.

| Check | Result | What it establishes |
|---|---|---|
| JP5 pad A ↔ pad B | **continuous** | JP5 is still factory-bridged on this Rev 2.2 — not cut |
| `J6` pin 3 → socket pin 1 | **continuous** | the same strap proven end-to-end: `Q8` collector → JP5 → socket pin 1 |

**Why this was worth measuring.** The gate Phase 182 ships assumes JP5 ships bridged and is intact
on the operator's board. Had it come back cut, the gate would be refusing `write` and `erase` on a
shield that is not in fact exposed, and D-06's scope would have needed rethinking. It is intact, so
the hazard is real on this specific board and the gate is warranted on it — measured, not assumed.

The second check also confirms from the copper what the schematic trace claimed: `J6` pin 3, `Q8`'s
collector and JP5's A side are one node, and the bridged JP5 carries it to socket pin 1.

## Task 2c — the D-14 falsification: `hw_revision` across JP4 positions

**Method.** The firmware's `hw_get_version` reports two fields: `physical`, from a live
`rurp_get_physical_hardware_revision()` ADC read, and `effective`, the EEPROM override
(`src/hardware_operations.cpp`). The two are independent, so an EEPROM override cannot mask a
change in the physical reading — the test is not vacuous. This board carries an override set to
`Rev 2.0-class`, which is the correct broad bucket for a Rev 2.2 (`REVISION_2_0 = 2` covers
2.0/2.1/2.2), not a mis-set value.

Claude's reads over USB, one per position, on the operator's word. No polling loop.
Port identity verified this session: `/dev/ttyACM0`, `controller: leonardo`, firmware `3.0.0b22`.

| JP4 position | `physical` | `effective` (override) |
|---|---|---|
| as found at session start | `Rev 2.0-class` | `Rev 2.0-class` |
| jumper on the **socket-facing** pole (socket pin 3, 28-pin) | `Rev 2.0-class` | `Rev 2.0-class` |
| jumper on the **periphery-facing** pole (socket pin 25, 24-pin) | `Rev 2.0-class` | `Rev 2.0-class` |
| **no jumper fitted** | `Rev 2.0-class` | `Rev 2.0-class` |

**Verdict: D-14's retraction survives its bench falsification attempt.** The reported physical
revision is invariant across every position JP4 supports, including no jumper at all — the position
that would show the largest swing if JP4 sat anywhere in the detect divider. This is consistent
with the schematic and PCB finding that R41 sits between Arduino A3 and GND and touches no JP4 pin,
and therefore that the `hw_revision` detect band is independent of JP4 position.

**What this does and does not prove — stated precisely.** `firestarter hw` reports a *bucket*
(`Rev 2.0-class` spans revisions 2.0/2.1/2.2), not the raw ADC count, and no command on this
firmware exposes the raw count. So the measurement establishes that **JP4 position does not move
the reported revision**, which is the operationally relevant claim and the one D-14's retraction is
used for. It does not, and cannot on this firmware, establish that the A3 voltage is literally
unchanged to the LSB — a sub-band shift would be invisible here. Recorded as a failed falsification
of a schematic-derived claim, not as an independent measurement of the divider.
