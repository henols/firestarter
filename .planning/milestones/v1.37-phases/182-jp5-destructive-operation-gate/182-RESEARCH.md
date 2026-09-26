# Phase 182: JP5 Destructive-Operation Gate - Research

**Researched:** 2026-09-10
**Domain:** RURP shield VPP routing (KiCad schematic + PCB + gerber archaeology), Arduino firmware
control-register semantics, `firestarter_app` database generator / pinout layer, Click CLI gating
**Confidence:** HIGH on the VPP path and the 32-pin decode premise (both measured this session);
MEDIUM on the Rev 2.0/2.1 JP4 pole assignment (needs the D-12 continuity probe); MEDIUM on the
D-05 recommendation (rests on one inferred rail-level claim, named below).

---

## Summary

The desk trace succeeded, and it **overturns the phase's working assumption in the operator's
disfavour**. Three things came out of it.

**First, JP5 is a hard-wired VPP-to-socket-pin-1 strap, and JP4 is not a VPP *source* at all.**
Measured from the committed schematic and PCB: socket pin 1 sits on a single net carrying JP4's
*common* pole, JP5's B side, a 10 kΩ pull-down (R33) and a Schottky (D33) fed from the
`P1_VPP_ENABLE` control line. JP5's A side is the collector of Q8, a PNP high-side switch whose
emitter is the `VPE` rail. So JP5 bridged ⇒ Q8 conducting puts the VPE rail directly on socket pin 1.
JP4's two selectable poles do not bring VPP in — they *export* whatever socket pin 1 carries to
socket pin 3 (a 28-pin part's pin 1) or socket pin 25 (a 24-pin part's pin 21). That confirms D-10's
third-pole finding exactly, and corrects `jumper-display-ground-truth.md`'s JP4 row, which says JP4
routes "VPP to socket pin 1 only".

**Second, the firmware answer to gh#60 is "write and erase, not read" — but only because the boost
regulator happens to be off during a read.** `CTRL_VPP_P1_ENABLE` (the Q8 gate) is asserted from
exactly three code sites, all inside the EPROM write/erase paths, plus the Intel-flash protocol
where pin 1 genuinely *is* VPP. `read`, `verify`, `blank` and `id` never assert it. However — and
this is the load-bearing discovery — on Rev 2.x hardware the firmware maps **logical
`CTRL_ADDRESS_LINE_18` onto the same physical bit as `CTRL_VPP_P1_ENABLE` (0x08)**. Any pin map that
places an address line on socket pin 1 therefore drives Q8 from the address bus. During a write the
route mask is asserted **for the whole operation, across every block**, so the rail is at 12.75 V
while the address sweeps.

**Third, therefore the map fix does not supersede the gate — it relocates the hazard without
removing it.** Today the eight 8 Mbit rows declare `vpp-pin: [1]`, so a write asserts P1 and puts
12.75 V on a pin the part uses as A19: damage. After the fix, VPP correctly moves to socket pin 24
(the part's `/OE`-shared VPP), but A19 lands on bus line 21, which *is* the pin-1 line on Rev 2.x —
so every byte written above 0x7FFFF asserts Q8 while the rail is boosted. Same 12.75 V, same pin,
different route. Both before and after, the operation is safe **only if JP5 is cut** — which is
exactly, and unconditionally, what the silkscreen says.

**Primary recommendation:** ship the map fix **and** a gate. Recommend D-05 resolve to
"gate ships", scoped per D-06 to `write` and `erase` only, because the trace shows those two
operations — and only those two — put the boosted rail on socket pin 1 for an affected part.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** SAFE-01's literal wording ("the pin map puts A19 on socket pin 1") is **not satisfiable
  against the database as it stands** — measured 2026-09-10: no pin map in `pinouts.json` declares
  A19 at all, and all eight 1 MB (8 Mbit) rows sit on `DIP32_STD`, which declares 19 address lines
  (A0–A18) and `vpp-pin: [1]`. The phase does **not** work around this with a synthetic predicate
  (address-line shortfall, size threshold, or the 291-row VPP-on-pin-1 set were all considered and
  rejected). It **fixes the pin map so SAFE-01 becomes literally true**, and the gate predicate is
  then the requirement's own words.
- **D-02:** The fix is **rule-shaped, with no per-part special case**. `resolve_pinout_key` already
  dispatches on infoic's `variant_lo` for `pin_count == 24` and `pin_count == 28`; it abandons the
  field only at `pin_count == 32`, substituting a hand-tuned size threshold. The 32-pin arm
  dispatches on `variant_lo` like the other two widths: `0x01` → 256 KB 27C020 class → `DIP32_27C020`
  (pin 31 = PGM); `0x02` → 512 KB 27C040 class → `DIP32_STD` (pin 31 = A18); `0x03` → **1 MB**
  27C080 / M27C801, pin 1 = **A19** → **new layout, to be authored**. All three sit at
  `pin_map=0x000c`, `protocol_id=0x08`. A future 8 Mbit part added upstream carries `variant=0x03`
  and is classified correctly with **no generator edit**.
- **D-03:** `MAX_27C020_SIZE` and `tests/test_revision_constants_parity.py`'s `MAX_27C020_SIZE` arm
  are **retired**. The constant exists only in `firestarter_app`; the test's docstring cites a
  firmware `#define` which **does not exist** — the assertion compares the host constant to a
  literal copy of itself.
- **D-04:** The `chip_database.json` diff is **the output of a `build_db.py` re-run**, never a hand
  edit.
- **D-05:** Whether a warning gate ships **at all** is decided by the SAFE-03 trace that this phase
  produces, not before it. The operator's expected outcome is that **the map fix supersedes the
  gate**. If the trace confirms that JP5-bridged with VPP unasserted cannot damage the part,
  **SAFE-02 and SAFE-04 are formally retired in `REQUIREMENTS.md` with the trace as the recorded
  reason**. If the trace shows otherwise, a gate ships under D-06 and D-07.
- **D-06:** **If** a gate ships, it fires **only on operations that can physically damage the
  part**. Operations that merely return or write wrong data are explicitly **not** gated. The
  damage-capable set is defined by the SAFE-03 trace, not by inference.
- **D-07:** **If** a gate ships, its escape hatch is: an interactive **question to continue**;
  `-f`/`--force` **does not** satisfy or bypass it; and a **non-interactive invocation refuses**
  (no TTY, piped stdin, `dev test`, `--auto`/`--chain`). Never a default-yes.
- **D-08:** SAFE-05 stays in this phase — `_get_rev2_2_jumper_settings_data`
  (`ic_layout.py:186-201`) and its commented-out call site (`ic_layout.py:656`) are deleted.
- **D-09:** The shield photographs, the per-revision jumper configuration tables, and the
  `firestarter info` jumper-block rewrite are a **separate phase**. Not Phase 182.
- **D-10:** The operator's **Rev 2.2** board carries a **3-pole JP4**, not the 2-pin header the
  project record claims, and the third pole routes VPP to a 24-pin part's **pin 21**. Earlier
  revisions have no such capability. Whether Rev 2.3's silkscreen was corrected is **unresolved**.
- **D-11:** SAFE-03's trace is a **VPP-destination table**: revision family (Rev 0 / Rev 2.0–2.1 /
  Rev 2.2+) × JP4 state → **which socket pin actually carries VPP**. The table resolves
  `jumper-display-ground-truth.md`'s standing defect 4 as a by-product.
- **D-12:** The table is settled by **desk trace plus an operator continuity probe on the Rev 2.2
  board**. The table lives in `.planning/notes/jumper-display-ground-truth.md`, whose JP4 row is
  corrected in place.
- **D-13:** Phase 182 corrects **every JP4 claim in `.planning/v1.7-SHIELD-REVS.md` that the trace
  settles** — §1 row 19, §3 rows 44/45, §4 row 58, §5 rows 73/74, §6 rows 89/91, §7 row 132,
  §"Detect" line 175, and §"JP4 Caveat". §6's capability column conflates *can read* with *can
  program*: the 24-pin legacy UV-EPROM row is revision-qualified. Corrections use the file's
  existing inline dated/evidence-cited convention, plus **one note naming the systemic cause**.
- **D-14:** The §"JP4 Caveat" claim that R41's lower terminal couples to a JP4 pin is resolved in
  this phase, **characterize-only**: desk-trace whether the coupling exists at all, and read
  `hw_revision` at each JP4 position on the bench. **No firmware change in Phase 182.** If the
  detect band moves with JP4 position, that is recorded as a defect, not fixed here.
- **D-15:** Two findings are **recorded and backlogged, never gated**: (1) DIP24 unreachable VPP —
  `DIP24_2716`/`DIP24_2532` declare `vpp-pin: [21]`, unreachable on Rev 0/2.0/2.1; (2) the mirrored
  hazard — JP4 in the 24-pin position with a 28/32-pin part seated.

### Claude's Discretion

- The name of the new 32-pin layout key. `DIP32_27C801` follows the established
  `DIP32_27C020` / `DIP32_SST39SF040` convention (exemplar part number); the planner may settle it.
- ~~Whether the SAFE-03 trace is written as a standalone note or inline in `SUMMARY.md`.~~
  **Settled by D-12** — it extends `.planning/notes/jumper-display-ground-truth.md`.
- The exact shape of the VPP-destination table (D-11) — column order, how a JP4 state is named,
  whether Rev 0 gets its own row or a "JP4/JP5 not present" sentinel. It must be readable by the
  D-09 phase and citable by Phase 187.
- How the retired `MAX_27C020_SIZE` parity arm is disposed — deleted outright, or replaced by a
  test that asserts something real about the 32-pin dispatch.

### Deferred Ideas (OUT OF SCOPE)

- **The wider pin-map audit** — `AT27C011`/`D27011`/`D27C011` on `DIP28_2764` (14 address lines for
  128 KB parts); 18 rows on `DIP32_28C512_EEPROM` (up to 512 KB against 16 address lines). Worth a
  backlog item: a fail-closed generator assertion that every row's `size_bytes` fits the address
  lines its layout declares.
- **Silently-wrong 8 Mbit reads with JP5 bridged.** Explicitly **not** gated per D-06.
- **The D-09 phase itself does not exist yet** — needs inserting into `.planning/ROADMAP.md` before
  Phase 187.
- **`REQUIREMENTS.md` needs two edits from the discussion** — SAFE-01's wording, and SAFE-02/SAFE-04
  marked conditional on the SAFE-03 trace per D-05.
- **2516 / 2716 / 2532 programming support as a capability** — its own phase.
- **Backlog items** per D-15.1 and D-15.2, filed during this phase; no host behaviour change here.
- **Was the Rev 2.3 silkscreen corrected?** Unresolved; matters to D-09, not to Phase 182.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SAFE-01 | The affected-part set is derived from the chip database and its pin maps, not a hand-written list. Adding a part cannot silently omit it from the gate. | § *The new 32-pin layout definition* gives the layout that makes "A19 on socket pin 1" literally expressible; § *The affected-part predicate and its seam* names `EpromDatabase.get_pin_map` and gives the exact derivation + the test shape for success criterion 2. |
| SAFE-02 | Before an affected operation on an affected part, the operator is told JP5 must be cut and why, and the operation does not proceed without explicit confirmation. | § *Which operations energize socket pin 1* establishes the affected operation set (`write`, `erase`); § *The gate mechanism, priced* names the seam, the prompt pattern and the hazard text (checkable against the silkscreen). |
| SAFE-03 | Which operations the gate covers is settled from the shield schematics and the protocol's VPP path — not inferred — and recorded with evidence. gh#60's open question is answered. | § *The VPP-destination table* (schematic + PCB + gerber, all measured this session) and § *Which operations energize socket pin 1* (firmware file:line). |
| SAFE-04 | The gate cannot be auto-answered: non-interactive, piped stdin, `dev test`, `--auto`/`--chain` each refuse or require an explicit separate acknowledgement — never a default-yes. | § *The gate mechanism, priced* — the `submit.py` `isatty_fn`/`confirm_fn` pattern, the `_is_interactive` CLAIM-07 collision stated precisely, and the finding that `--auto`/`--chain` are **GSD** flags with no firestarter CLI counterpart, so the non-TTY refusal is what covers them. |
| SAFE-05 | `_get_rev2_2_jumper_settings_data` and its commented-out call site are deleted. | § *File:line inventory* rows 12–13, plus the **success-criterion-4 grep trap** (`build/` + ugrep) that would otherwise make the criterion pass or fail for the wrong reason. |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Deciding which socket pin carries VPP | Hardware (RURP shield: JP4/JP5 straps + Q6/Q7/Q8 switches) | — | Not software-visible; JP5 is a solder jumper the tool cannot read (project Out-of-Scope) |
| Asserting the VPP route for an operation | Firmware (`src/proms/eprom.cpp`, `flash_intel.cpp`) | — | The control register is written only by firmware; the host sends a bus config and a command |
| Chip → pin-map assignment | Generator (`tools/build_db.py`) | — | `chip_database.json` is generated; a hand edit is reverted by the next regen (D-04 / milestone D-6) |
| Pin-map → socket-pin definition | Authored data (`firestarter/data/pinouts.json`) | — | infoic's `<maps>` carries connectivity only, no signal function — it cannot generate a layout (CONTEXT, measured) |
| Socket-pin → RURP bus line | Host (`firestarter/database.py` `pin_conversions`) | — | Board-wiring layer; one source of truth per layer, composed in `get_bus_config()` |
| Operator-facing hazard warning + refusal | Host CLI (`firestarter/cli_handlers.py`) | Host operator layer (`eprom_operations.py`) | Must stop **before** the serial link opens; TTY policy belongs at the CLI boundary |
| Affected-part predicate | Host database layer (`EpromDatabase.get_pin_map`) | — | SAFE-01 requires derivation from the shipped pin maps, so the predicate must read `pinouts.json`, not a constant |

---

## The VPP-destination table (D-11)

### How the trace was done

Parsed `RelativelyUniversalROMProgrammer.kicad_sch` into an s-expression tree, resolved every symbol
instance's pin coordinates from `lib_symbols`, built a wire+junction connectivity graph, and read off
the nets at JP4's and JP5's pins. Cross-checked every conclusion against the committed
`RelativelyUniversalROMProgrammer.kicad_pcb` pad→net table and against the Rev 2.1 / Rev 2.2 gerber
drill files. All coordinates below are schematic mm unless stated.

### Settled topology

`[VERIFIED: RelativelyUniversalROMProgrammer.kicad_sch, symbol block at 22553-22623 + net trace]`
JP4 is `Jumper:Jumper_3_Open`, `Value "P1_VPP_JMP"`, `Description "Jumper, 3-pole, both open"`,
`Footprint Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical`, placed at (177.8, 69.85).
Its library pins are C=1 at local (0,−3.81), A=2 at (−6.35,0), B=3 at (+6.35,0), i.e. schematic
(177.8, 73.66), (171.45, 69.85), (184.15, 69.85) — matching CONTEXT.md's coordinates exactly.

Nets at those three points, and at JP5:

| Node | Net members (measured) | What it is |
|------|------------------------|------------|
| JP4 pin 1 **C** (177.8, 73.66) | `U5` pin **1** (socket pin 1), `JP5` pin 2 (B), `R33` 10 kΩ pin 2, `D33` 1N5819 cathode | **socket pin 1** |
| JP4 pin 2 **A** (171.45, 69.85) | `U5` pin **3**, `R19` 10 kΩ pin 2, `D11` 1N5819 cathode | **socket pin 3** = a 28-pin part's pin 1 |
| JP4 pin 3 **B** (184.15, 69.85) | `U5` pin **25**, `R20` 10 kΩ pin 2, `D34` 1N5819 cathode | **socket pin 25** = a 24-pin part's pin 21 |
| JP5 pin 1 **A** (184.15, 104.14) | `Q8` MMBT3906 **collector**, `J6` "VP" pin 3, `D31` RED LED anode | **the switched VPP node** |
| JP5 pin 2 **B** (191.77, 104.14) | same net as JP4 pin C | **socket pin 1** |

`[VERIFIED: RelativelyUniversalROMProgrammer.kicad_sch — Q8/Q5/R25/R31/R38 net trace]`
The pin-1 high-voltage switch chain is: global label `P1_VPP_ENABLE` → `R25` 22 kΩ → `Q5` MMBT3904
base; `Q5` collector → `R38` 4k7 → `Q8` MMBT3906 base (`R31` 22 kΩ base-emitter pull-up); `Q8`
emitter = global `VPE`; `Q8` collector → **JP5** → socket pin 1. Its three siblings on the same
`VPE` rail are `Q7` (from `A9_VPP_ENABLE` via `R24`/`Q4`) → socket pin **26** (A9, the chip-ID 12 V
path), `Q6` (from `VPE_ENABLE` via `R23`/`Q3`) → socket pin **24** (`/OE`), and `Q2` (from
`VPE_TO_VPP` via `R2`/`Q1`) → `R5` 270 kΩ → `U1` MIC2288 `FB` (the boost-regulator feedback that
selects the rail level).

`[VERIFIED: RelativelyUniversalROMProgrammer.kicad_sch:26840-ish symbol block]` JP5's own record:
`Value "A19_CUT"`, footprint
`Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm` — **bridged by default**.

`[VERIFIED: RelativelyUniversalROMProgrammer.kicad_pcb — JP4/JP5 footprint pad→net extraction]`
The PCB agrees, and adds the physical geometry:

| Component | Footprint | Pad | Pad position (local mm) | Net |
|---|---|---|---|---|
| JP4 @ (91.44, 81.788) | `PinHeader_2x02_P2.54mm_Vertical` | 1 | (0, 0) | `Net-(D33-K)` — socket pin 1 |
| | | 2 | (2.54, 0) | `Net-(D11-K)` — socket pin 3 |
| | | 3 | (0, 2.54) | `Net-(D34-K)` — socket pin 25 |
| | | *(4th grid position unpopulated)* | | — |
| JP5 @ (98.1456, 70.1548) | `SolderJumper-2_P1.3mm_Bridged…` | 1 | (−0.65, 0) | `Net-(D31-A)` — switched VPP node |
| | | 2 | (+0.65, 0) | `Net-(D33-K)` — socket pin 1 |

`[VERIFIED: Rev2.2/Rev2.2-gerbers.zip → W27C512Programmer-PTH.drl, extracted this session]` JP4 has
exactly **three** component drills (tool T2, ⌀1.0 mm): (91.440, −81.788), (93.980, −81.788),
(91.440, −84.328). The 2×2 grid's fourth position (93.980, −84.328) is **not drilled**. The
coordinates match the PCB's pad table one-for-one (the drill file's Y is the PCB's Y negated), which
also proves **the committed `kicad_pcb` is the Rev 2.2/2.3 layout** — Rev 2.2's own gerbers place JP4
at the identical coordinate the PCB does.

`[VERIFIED: Rev2.1/RURP-Rev2.1.zip → W27C512Programmer-PTH.drl, extracted this session]` Rev 2.1's
JP4 has exactly **two** component drills: (90.932, −84.074) and (90.932, −81.534) — a vertical pair,
2.54 mm apart, at a *different* board coordinate from Rev 2.2. Corroborated by
`Rev2.1/W27C512Programmer-top-pos.csv` (`"JP4","P1_VPP_JMP","PinHeader_1x02_P2.54mm_Vertical"`,
90.932, −84.074, rot 180) and `Rev2.2/W27C512Programmer-top-pos.csv`
(`"PinHeader_2x02_P2.54mm_Vertical"`, 91.440, −81.788, rot 0). `hardware/rev2/` (Rev 2.0) carries the
**same 1x02 row as Rev 2.1, byte-for-byte**. So the footprint change is at **2.1 → 2.2**, exactly as
D-10 states, and the project record's attribution of it to 2.2 → 2.3 (`v1.7-SHIELD-REVS.md` §4 row 6
/ §5 row 6) is wrong.

### The table

Read as: *for a part seated in the named socket position, on this revision, with JP4 in this state —
which socket pin can the shield energize to the VPE rail?*

| Revision family | JP4 physical state | Socket pin reachable by VPE via Q8 (`P1_VPP_ENABLE`) | Also reachable via other switches | Settled? |
|---|---|---|---|---|
| **Rev 0 / Rev 1** | **JP4 and JP5 do not exist** on these boards | Rev 0's equivalent strap is **JP3** (`W27C010/AT27C010 needs p1 VPE/VPP (32 pin)`), selecting the pin-1 position of a 32- vs 28-pin seated chip | socket 24 (`/OE`) via Q6; socket 26 (A9) via Q7 | **NEEDS PROBE** — Rev 0 schematic blob is `cfe6139f`, not read this session; `v1.7-SHIELD-REVS.md:59` records the whole Rev 0 jumper set as untraced. *Probe: continuity from the operator's modified Rev 0 JP3 pads to socket pins 1 and 3.* |
| **Rev 2.0 / Rev 2.1** (JP4 = 1×02, 2 pads) | **Open** | socket **1** only | socket 24, socket 26 | **SETTLED** — the 2-pad footprint means one pole at most, and open means none |
| | **Closed** | socket **1** *and* whichever socket pin the single fitted pole reaches | socket 24, socket 26 | **NEEDS PROBE** — no Rev 2.0/2.1 schematic or PCB is committed (Phase 31 Finding E). The silkscreen (*"Closed for 28 pin ROMs"*) and Rev 0's JP3 semantics both point to **socket 3**, and the Rev 2.2 pole to socket 25 is *newly added* per D-10 — but that is **inferred**, not measured. *Probe: with no chip seated and the board unpowered, ohm-meter continuity from each JP4 pad on the Rev 2.0 board to socket pin 1, socket pin 3 and socket pin 25.* |
| **Rev 2.2 / Rev 2.3** (JP4 = 3 pads in an L) | **No jumper** (32-pin mode) | socket **1** only | socket 24, socket 26 | **SETTLED** (schematic + PCB + Rev 2.2 drill) |
| | **Jumper across the corner pad and the pad +2.54 mm in +X** (28-pin mode) | socket **1** and socket **3** | socket 24, socket 26 | **SETTLED** electrically. *Residual: which physical direction is "+X" as the operator sees the silkscreen. Probe: continuity from each of the three JP4 pads to socket pins 1 / 3 / 25 on the Rev 2.2 board.* |
| | **Jumper across the corner pad and the pad +2.54 mm in −Y** (24-pin mode) | socket **1** and socket **25** | socket 24, socket 26 | **SETTLED** electrically, same residual as above |

**Reading the table for the two questions that motivated it:**

- **The 8 Mbit part (`<specifics>`).** A 27C080/M27C801 wants VPP on **socket pin 24**, not pin 1
  (see § *The new 32-pin layout definition*). The shield reaches socket pin 24 through Q6 /
  `VPE_ENABLE` on **every** Rev 2.x board, independent of JP4 and JP5. So these parts are **not**
  read-only on this hardware — they are programmable, and the honest answer to gh#60 is that the
  shield can deliver VPP where a 27C801 wants it. What it *cannot* do is drive socket pin 1 as a
  clean logic A19 while JP5 is bridged, because the only pin-1 driver is `P1_VPP_ENABLE` through
  D33 — and asserting `P1_VPP_ENABLE` also turns on Q8.
- **`jumper-display-ground-truth.md` standing defect 4 (24-pin VPP maps get no JP3/JP4 guidance).**
  Resolved. `DIP24_2716` and `DIP24_2532` declare `vpp-pin: [21]`
  `[VERIFIED: firestarter_app/firestarter/data/pinouts.json:5,118]`. A 24-pin part bottom-aligned in
  the 32-pin socket puts its pin 21 at **socket pin 25**, which is exactly JP4's third pole. So on
  Rev 0/2.0/2.1 those maps' declared VPP pin is **unreachable**, and on Rev 2.2+ it is reachable only
  with JP4 in the 24-pin position. That is D-15.1, now measured rather than suspected.

### The socket-position offsets the table depends on

`[VERIFIED: RelativelyUniversalROMProgrammer.kicad_sch — U5 symbol is `Memory_Flash:SST39SF040`,
pin 16 = GND, pin 32 = VCC]` The socket is a 32-pin position, bottom-aligned (GND end fixed), with
three `Pin1→` markers on the silkscreen
(`evidence/shield-rev2.2-jp4-jp5-jp6-jp9.jpg`, per CONTEXT). Standard bottom-aligned mapping:

| Seated part | Part pin 1 at socket pin | Part GND at socket pin | Part VCC at socket pin |
|---|---|---|---|
| 32-pin | 1 | 16 | 32 |
| 28-pin | 3 | 16 | 30 |
| 24-pin | 5 | 16 | 28 |

Consequently a 24-pin part's **pin 21** sits at **socket pin 25**, and a 28-pin part's **pin 1** sits
at **socket pin 3** — which is precisely what JP4's two poles reach. This is an *inferred* mapping
(from the standard DIP-in-wider-socket convention plus the GND/VCC anchor), but it is
independently corroborated: `pin_conversions[24][21] = 11` and `pin_conversions[32][25] = 11` — the
**same RURP bus line** `[VERIFIED: firestarter_app/firestarter/database.py:58,124]`, and likewise
`pin_conversions[28][1] = 15` and `pin_conversions[32][3] = 15`
`[VERIFIED: firestarter_app/firestarter/database.py:67,86]`. The host's own board-wiring table
already encodes the offsets.

### D-14: the R41 / JP4 coupling claim is FALSE

`[VERIFIED: RelativelyUniversalROMProgrammer.kicad_sch — R41 net trace]` R41 (10 kΩ, at schematic
(279.4, 50.8)) has pin 1 on the net carrying `A1` (Arduino_UNO_R3) pin 12 = **A3**, and pin 2 on the
**GND** net (shared with `SW1 RST` pin 2). It touches **no JP4 pin, in either the schematic or the
PCB**.

`[VERIFIED: RelativelyUniversalROMProgrammer.kicad_pcb — R41 pads]` `R41 at (90.3732, 52.7832)`,
pad 1 → `Net-(A1-A3)`, pad 2 → `GND`. JP4 is at (91.44, 81.788) — ~29 mm away, a different board
region.

So `v1.7-SHIELD-REVS.md` §"JP4 Caveat" (line 196-198) — *"R41's lower terminal connects to one pin
of JP4 such that the divider works only when JP4 is in a specific config; consult upstream Anders
schematic … for the exact wiring"* — is **wrong**, and it is wrong in the direction that mattered:
the `hw_revision` detect band is **independent of JP4 position**. `v1.7-SHIELD-REVS.md:154` ("GND
(via JP4 / P1_VPP_JMP)"), `:163`, `:175`, `:208`, `:209` and §3 rows 42-45 all repeat the same
"via JP4" phrasing and are all corrected by this trace.

D-14's bench half therefore becomes a **falsification attempt with a predicted answer**: reading
`hw_revision` at each JP4 position should show **no change**. Recording that is cheap and worth
doing while the board is open, but the desk trace is the primary evidence, not the bench read.

### What the trace cannot settle (and the exact probe for each)

1. **Rev 2.0 / Rev 2.1's single JP4 pole — which socket pin.** No Rev 2.0/2.1 schematic or PCB is
   committed; only pos-CSV, BOM and gerbers. Reading nets out of a Gerber copper layer is
   aperture-flash reconstruction and was judged untrustworthy for a hazard claim.
   **Probe:** unpowered Rev 2.0 board, no chip seated — continuity from each of JP4's two pads to
   socket pins 1, 3 and 25.
2. **Physical orientation of Rev 2.2's three JP4 pads as the operator sees them.** The electrical
   assignment is settled; which pad is the corner in board-view is a silkscreen-orientation question.
   **Probe:** unpowered Rev 2.2 board — continuity from each of the three JP4 pads to socket pins 1,
   3 and 25, recorded against the pad's position relative to the `JP4` silkscreen legend.
3. **Rev 0 / Rev 1's JP3 routing.** Not read this session (blob `cfe6139f` per
   `reference_rev0_schematic_blob_is_cfe6139f_not_d2a7f691`); the project record already carries it as
   untraced (`v1.7-SHIELD-REVS.md:59`). Desk-readable in a follow-up, or probe the operator's
   modified Rev 0 (noting its cut-and-jumper rework may not match stock Rev 0).
4. **The absolute VPE rail level with the boost regulator disabled.** See the next section — this is
   the one inferred link in the D-05 chain.

**Do not infer Rev 2.2 from Rev 2.1's shared schematic blob.** That has now produced three wrong
answers in this project: R41 4k7-vs-10k, JP4's footprint, and (found this session) the *revision* at
which the footprint changed. In every case Rev 2.2's own artefacts — `Rev2.2/…-top-pos.csv` and
`Rev2.2-gerbers.zip` — sat in the same directory. That is the systemic-cause note D-13 asks for.

---

## Which operations energize socket pin 1 (SAFE-03, success criterion 5)

Firmware read from `/workspaces/firestarter/` at HEAD (`gsd/v1.36-dev-test-fidelity`). `git diff HEAD
origin/beta` is **one line in `include/version.h`** `[VERIFIED: git diff --stat, this session]`, so
this reading is beta's.

### The control-register bit, and its Rev 2 alias

`[VERIFIED: firestarter/include/rurp_pinout.h:73-93]` Logical bits:
`CTRL_VPP_VPE_DROP_ENABLE 0x01`, `CTRL_VPP_A9_ENABLE 0x02`, `CTRL_VPE_ENABLE 0x04`,
`CTRL_VPP_P1_ENABLE 0x08`, `CTRL_ADDRESS_LINE_17 0x10`, `CTRL_ADDRESS_LINE_18 0x20`,
`CTRL_READ_WRITE 0x40`, `CTRL_VPP_REGULATOR_ENABLE 0x80`.

`[VERIFIED: firestarter/include/rurp_pinout.h:144]` **`#define CTRL_ADDRESS_LINE_18_REV2
CTRL_VPP_P1_ENABLE_REV2`** — and `CTRL_VPP_P1_ENABLE_REV2` is `0x08`
`[VERIFIED: firestarter/include/rurp_pinout.h:139]`.

`[VERIFIED: firestarter/include/rurp_hw_rev_utils.h:18-26]` `rurp_map_ctrl_reg_for_hardware_revision`
on `REVISION_2_0 / 2_1 / 2_2 / 2_3` passes `CTRL_VPP_P1_ENABLE` through unchanged **and** maps
`CTRL_ADDRESS_LINE_18 → CTRL_ADDRESS_LINE_18_REV2`. Both therefore land on **physical bit 0x08**.
On `REVISION_0 / REVISION_1` the mapping is `ctrl_reg = data` verbatim, so logical A18 stays at
physical 0x20 — a *different* line.

**This is the crux.** On any Rev 2.x board there is exactly one physical line to socket pin 1, and it
serves double duty as the top address bit and as the VPP-enable. `include/rurp_pinout.h:112-113` says
so in the source: *"On Rev 2-class, A18 and P1 collapse onto the same physical bit anyway."*

### The three assert sites, and the operations that reach them

`[VERIFIED: firestarter/src/proms/eprom.cpp:583-589]` `eprom_internal_set_control_register` rewrites
`CTRL_VPE_ENABLE → CTRL_VPP_P1_ENABLE` when `using_p1_as_vpp(handle)` holds. That predicate is
`(pins==32 && vpp_line==VPP_P1_32_DIP) || (pins==28 && vpp_line==VPP_P1_28_DIP) || (pins==24 &&
vpp_line==VPP_P21_24_DIP)` `[VERIFIED: firestarter/include/memory_utils.h:61-65]`, with
`VPP_P1_32_DIP 0x15`, `VPP_P1_28_DIP 0x0F`, `VPP_P21_24_DIP 0x0B`
`[VERIFIED: firestarter/include/rurp_shield.h:43-45]`. The header's own comment names the mechanism:
*"chips whose physical VPP pin is socket pin 1 (after bodge wire / Rev 2.2 JP4)"* — the three magic
values are the three JP4 destinations from the table above.

| Firmware site | Bits asserted | Function | Reached by |
|---|---|---|---|
| `eprom.cpp:453` / cleared `:462` | `CTRL_VPE_ENABLE` (→ P1 when `using_p1_as_vpp`) | `eprom_internal_write_execute_body`, the per-pass program pulse | **`CMD_WRITE` main** |
| `eprom.cpp:547` | `CTRL_VPP_A9_ENABLE \| CTRL_VPE_ENABLE` (→ P1 when `using_p1_as_vpp`) | `eprom_internal_erase` | **`CMD_ERASE` main** (`eprom.cpp:117-120`) **and** `CMD_WRITE` init when `FLAG_CAN_ERASE && !FLAG_SKIP_ERASE` (`eprom.cpp:136-141`) |
| `eprom.cpp:216` / cleared `:220` | `CTRL_VPE_ENABLE` | `eprom_internal_program_pulse` (overprogram) | `CMD_WRITE` only, and **inert on every shipped protocol** — `overprogram_factor == 0` on every row (`eprom.cpp:166-169`) |
| `flash_intel.cpp:73, 81, 87, 112, 124` | `CTRL_VPP_REGULATOR_ENABLE \| CTRL_VPP_P1_ENABLE` **directly** | `flash_intel_write_init`, `flash_intel_erase_execute`, `flash_intel_cleanup` | `CMD_WRITE` / `CMD_ERASE` on protocol **0x10** (Intel 28F), where socket pin 1 genuinely *is* VPP |

**Sites that do NOT reach socket pin 1:**

- `eprom_check_vpp` (`eprom.cpp:512-539`) asserts only `eprom_hv_route_mask(handle)` —
  `CTRL_VPP_REGULATOR_ENABLE` or `EPROM_HV_ROUTE_MASK (REGULATOR | DROP)`. **No `CTRL_VPE_ENABLE`**,
  so Q8 stays off. It boosts the rail, waits 100 ms at address 0, measures, and clears.
- `eprom_get_chip_id` (`eprom.cpp:499-510`) asserts `REGULATOR` then `CTRL_VPP_A9_ENABLE` — that is
  Q7 → **socket pin 26**, not pin 1. So **`id` energizes A9, never pin 1.**
- `mem_util_blank_check` (`memory.cpp:452+`) is pure `firestarter_get_data` reads.
- `flash_5v_page.cpp:200, 208, 224` asserts `REGULATOR | DROP | CTRL_VPE_ENABLE` — but that protocol
  (0x05) never installs eprom's override, so `CTRL_VPE_ENABLE` stays itself → Q6 → **socket pin 24**.
- `memory.cpp:417-419`: *"Set VPP line to high if VPP is not on P1"* —
  `if (config.vpp_line != 0xFF && !using_p1_as_vpp(handle))`. For a VPP-on-P1 part the host's VPP
  line is **deliberately not driven high** on any address set, including reads. Correct, and load-
  bearing: without the guard, every read would assert P1.

### `read` still enables the regulator — but at address 0

`[VERIFIED: firestarter/src/proms/memory.cpp:66-72, 108-111 and src/proms/eprom.cpp:43]`
`configure_memory` sets `operation_main = memory_read_execute` for `CMD_READ`, then dispatches to
`configure_eprom`, which sets `firestarter_operation_init = eprom_generic_init` **unconditionally,
before its per-command switch**. `eprom_generic_init` (`eprom.cpp:563-575`) calls `eprom_check_vpp`.
So **every** EPROM-family command — `read`, `verify`, `blank`, `id`, `write`, `erase` — boosts the
VPE rail for ~100 ms at init. `mem_util_set_address(handle, 0)` has already run
(`memory.cpp:86`), so the top address bit is low and Q8 is off during that window. *(This also
explains the standing firmware todo `skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads`.)*

### The write holds the boosted rail for the whole operation

`[VERIFIED: firestarter/src/proms/eprom.cpp:266-269 and 481-489]` `eprom_internal_write_execute_body`
asserts `eprom_hv_route_mask(handle)` once per block **only if the regulator is not already on**, and
the single-exit wrapper clears it **only on `RESPONSE_CODE_ERROR`** — the comment is explicit:
*"A successful block must leave the route asserted."* And `mem_util_calculate_top_address_register`'s
own comment (`memory.cpp:152-160`) says *"every address write … writes CONTROL_REGISTER
unconditionally on every byte, for both the pulse and the verify."*

So during a write, the rail is at the program voltage continuously, and the control register —
including physical bit 0x08 — is rewritten from the address on every byte.

### The answer to gh#60, stated plainly

> **Writing and erasing. Not reading, not verifying, not blank-checking, not `id`.**
>
> Socket pin 1 is energized to the VPE rail only through Q8, and Q8 is gated by
> `P1_VPP_ENABLE` (physical control bit 0x08). On a Rev 2.x board that bit is asserted by exactly two
> things: the EPROM protocol's program/erase pulse when the pin map says VPP is on socket pin 1, and
> the address bus when the pin map puts the top address line on socket pin 1. The read, verify,
> blank-check and chip-ID paths never assert it — `id` puts 12 V on socket pin **26** (A9) instead,
> and the VPP self-check that runs before every operation boosts the rail but leaves Q8 off with the
> address at zero.
>
> The consequence for a part with A19 on pin 1 and JP5 intact: a **read** drives pin 1 from the
> unboosted rail (a logic level) and is expected to work; a **write** drives the same pin from the
> 12.75 V programming rail every time the address crosses 0x80000. That is the damage path, and it
> is why JP5's instruction is unconditional.

**One inferred link, named as the research protocol requires.** The claim that the VPE rail sits at
roughly VCC when `CTRL_VPP_REGULATOR_ENABLE` is clear is **inferred** from the topology (`U1` is a
MIC2288 boost converter; a disabled boost passes VIN through its inductor and the `D1` Schottky to
`VPE`) — it is not measured, and no committed artefact states it. It is what makes "reading is safe"
true rather than merely "reading asserts a bit whose voltage we did not check". *Probe: with the
regulator disabled, measure `VPE` at `J6` pin 4 (the `VPE` header pin) and socket pin 1 while reading
a `DIP32_SST39SF040`-class part above address 0x40000 — that part already has A18 on socket pin 1
today, so the measurement needs no code change.* If that reading came back boosted, `read` would join
the damage-capable set and D-06's scope would widen.

---

## The 32-pin `variant_lo` dispatch fix (D-01, D-02)

### D-02's premise: verified, with one correction

Fetched the pinned infoic.xml this session
(`https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml`,
17.9 MB, 27862 `<ic>` records across `INFOICT76` / `INFOIC2PLUS` / `INFOIC`), applied
`build_db.py`'s own filter (`database[@type='INFOIC2PLUS']`, `24 ≤ pin_count ≤ 32`, not SMD, not
serial, `type ∈ {1,4}` — `build_db.py:420-443`) and decoded the fields it decodes
(`build_db.py:446-462`). 767 rows pass the filter; 444 are 32-pin.

`[VERIFIED: infoic.xml @ a8efaedc, decoded this session]` **All eight 8 Mbit rows carry the identical
tuple:**

| Part | Manufacturer | `variant` | `variant_lo` | `pin_map` | `pm_idx` | `protocol_id` | `code_memory_size` | `flags` |
|---|---|---|---|---|---|---|---|---|
| `AM27C080@DIP32` | AMD | `0x1303` | `0x03` | `0x600C` | 12 | `0x08` | 1048576 | `0x0068` |
| `AM27LV080@DIP32` | AMD | `0x1303` | `0x03` | `0x600C` | 12 | `0x08` | 1048576 | `0x0068` |
| `AT27C080@DIP32` | ATMEL | `0x1303` | `0x03` | `0x600C` | 12 | `0x08` | 1048576 | `0x0068` |
| `M27C801` | SGS-THOMSON | `0x1303` | `0x03` | `0x600C` | 12 | `0x08` | 1048576 | `0x0068` |
| `M27C801` | ST | `0x1303` | `0x03` | `0x600C` | 12 | `0x08` | 1048576 | `0x0068` |
| `MX27C8000@DIP32` | MACRONIX(MXIC) | `0x1303` | `0x03` | `0x600C` | 12 | `0x08` | 1048576 | `0x0068` |
| `MX27C8000A@DIP32` | MACRONIX(MXIC) | `0x1303` | `0x03` | `0x600C` | 12 | `0x08` | 1048576 | `0x0068` |
| `UPD27C8001@DIP32` | NEC | `0x1303` | `0x03` | `0x600C` | 12 | `0x08` | 1048576 | `0x0048` |

**Correction to D-02's table:** the field is `pin_map = 0x600C` (CONTEXT says `0x000c`); `pm_idx` is
its low byte, `0x0C = 12`. The decision's substance is unaffected — 12 is the cluster the three
density classes share.

The three classes at `pm_idx=12, protocol_id=0x08` do separate cleanly on `variant_lo`
`[VERIFIED: infoic.xml @ a8efaedc, decoded this session]`:

| `pin_map` | `variant_lo` | `code_memory_size` | rows | class |
|---|---|---|---|---|
| `0x600C` | `0x01` | 262144 | 33 | 27C020 / 27C2001 |
| `0x600C` | `0x02` | 524288 | 29 | 27C040 / 27C4001 |
| `0x600C` | `0x03` | **1048576** | **8** | 27C080 / M27C801 |

### But `variant_lo` alone does NOT partition the whole 32-pin 0x08 set

This is the finding the planner must not skip. `pm_idx=12` and `protocol_id=0x08` also hold rows
outside those three classes, and other `pm_idx` values reach `protocol_id=0x08` too
`[VERIFIED: infoic.xml @ a8efaedc, decoded this session]`:

| `pm_idx` | `variant_lo` | `code_memory_size` | rows | representative parts | current key |
|---|---|---|---|---|---|
| 10 | `0x00` | 131072 | 45 | `AM27C010`, `M27C1001`, `W27C010` | `DIP32_27C020` |
| 12 | `0x00` | 131072 | 4 | `HN27C301A…`, `M27C1000`, `MBM27C1000P` | `DIP32_27C020` |
| 12 | `0x00` | 262144 | 1 | `MBM27C2000P` | `DIP32_27C020` |
| 12 | `0x01` | 131072 | 1 | `MSM27C1000` | `DIP32_27C020` |
| 7 | `0x04` | 65536 | 1 | `SST37VF512` | `DIP32_27C020` |
| 9 | `0x04` | 131072 | 1 | `SST37VF010` | `DIP32_27C020` |
| 13 | `0x04` | 262144 | 1 | `SST37VF020` | `DIP32_27C020` |
| 13 | `0x04` | **524288** | 1 | `SST37VF040` | **`DIP32_STD`** |

A pure `variant_lo` ladder that mapped anything-not-0x02-or-0x03 to `DIP32_27C020` would move
`SST37VF040` off `DIP32_STD` — a 512 KB part whose pin 31 must stay A18. **So the size threshold
cannot be removed wholesale**; it must survive as the residual arm.

### The rule the research recommends, and its measured blast radius

```python
elif pin_count == 32:
    ...
    elif proto_id in {0x07, 0x08, 0x10}:
        if proto_id == 0x08 and variant_lo == 0x03:
            key = "DIP32_27C801"      # 1 MB, pin 1 = A19, VPP on pin 24 (/OE)
        elif proto_id == 0x08 and variant_lo == 0x02:
            key = "DIP32_STD"         # 512 KB, pin 1 = VPP, pin 31 = A18
        elif proto_id == 0x08 and mem_size <= _PGM_ON_PIN31_MAX_SIZE:
            key = "DIP32_27C020"      # residual 0x00/0x01/0x04 classes
        else:
            key = "DIP32_STD"
```

The `variant_lo` fork must stay **inside** the `proto_id == 0x08` arm. Protocol `0x10` rows at
`pm_idx ∈ {10, 13}` carry `variant_lo` values `0x10`, `0x11`, `0x12`, `0x13`
`[VERIFIED: infoic.xml @ a8efaedc, decoded this session]`; hoisting the fork above the protocol test
would reroute Intel-flash parts.

`[VERIFIED: ran `resolve_pinout_key` from `tools/build_db.py` over all 767 filtered rows, both under
today's logic and under the rule above, this session]` **Exactly 8 rows change key, and they are
exactly the eight 8 Mbit rows.** Nothing else in the 767-row set moves. That is the surgical
outcome D-02 wants, and it is measured, not projected.

### What the eight rows look like today, and what changes

`[VERIFIED: firestarter_app/firestarter/data/chip_database.json, read this session]` All eight
currently carry `"pinout": "DIP32_STD"`, `electrical.size_bytes = 1048576`,
`electrical.pin_count = 32`, `programming.algorithm = 8`, `support_status = "supported"`, and
`electrical.vpp_mv` of 13000 (AM27C080, AT27C080, MX27C8000, MX27C8000A, both M27C801) or 12000
(AM27LV080, UPD27C8001).

After the fix, the only generated field that changes is `pinout`. `support_status` is not derived from
the pinout key for these rows (all eight are already `supported`), so per CONTEXT's "treat any change
as an output" instruction the expectation is **no `support_status` movement** — but that is an
expectation, and `tools/diff_db.py` is the instrument that will confirm it (below).

The **wire-level** change is where it matters
`[VERIFIED: firestarter_app/tests/golden/wire_dict_baseline.json:437-467]`. `AMD|AM27C080|12` today:

```json
"bus-config": { "bus": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,20,22], "vpp-pin": 21 }
```

Nineteen bus lines, and bus line **21** used as the **VPP** line. After the fix it becomes twenty
bus lines with **21 appended as A19** and **no `vpp-pin` key at all** — because
`pin_conversions[32][24]` resolves to the `ROM_OE` sentinel and `get_bus_config` deliberately drops
it: `if pin_func == "vpp-pin" and resolved in (ROM_CE, ROM_OE): continue  # No dedicated VPP pin;
firmware defaults vpp_line=0xFF (VPE path)`
`[VERIFIED: firestarter_app/firestarter/database.py:277-279]`. That is the exact precedent
`DIP28_27512` already relies on (`vpp-pin: [22]`, `oe-pin: [22]`).

**Firmware consequence, which is the good news:** with `vpp_line == 0xFF`, `using_p1_as_vpp` is false,
so `eprom_internal_set_control_register` no longer substitutes P1, and the write asserts
`CTRL_VPE_ENABLE` → Q6 → **socket pin 24** — the 27C801's real VPP pin. The map fix makes these eight
parts *correctly* programmable for the first time. It also, as established above, makes A19 drivable
via bus line 21 = physical 0x08, which is the pin-1 line on Rev 2.x. Both effects are real; neither
cancels the other.

### The duplicate `M27C801` — not a defect

`[VERIFIED: firestarter_app/firestarter/data/chip_database.json, read this session]`
`chip_database.json` is manufacturer-keyed (59 manufacturers, 746 rows). `M27C801` appears once under
`SGS-THOMSON` and once under `ST`. Upstream infoic lists it under both manufacturers with identical
fields `[VERIFIED: infoic.xml @ a8efaedc, decoded this session]`. There are **no intra-manufacturer
duplicates anywhere in the DB**, and **66 part numbers appear under more than one manufacturer**
(`27C512` ×3, `M28F256` ×3, `27CX010` ×3, and 63 pairs). So this is upstream's own manufacturer
duplication, it is structurally normal for this database, and **regeneration preserves it**. Nothing
to do; worth one line in the phase record so it is not re-raised.

---

## The new 32-pin layout definition

### Pinout source

`[CITED: github.com/piersfinlayson/one-rom, docs/CHIP-TYPES.md — fetched this session]` The one-rom
`CHIP-TYPES.md` is the same independent, datasheet-verified oracle that four existing entries in
`pinouts.json` already cite by name (`DIP32_SST39SF040`, `DIP28_28C256`, `DIP28_28C64`,
`DIP32_28C512_EEPROM`). Nothing in this project derives the 27C080 pinout from it today, so citing it
here is **not circular**.

Line 89 — the 32-pin EPROM family table:

> `| 27C080 | 27C801 | 1MB | 20 (A0-A19) | /CE (pin 22), /OE (pin 24) | VPP: pin 24 (Acts as /OE); /PGM: pin 22 (Acts as /OE) | ✓ |`

Line 198 — the 32-pin package pin table, pin 1 row: `27C080` → **`A19`**.

Lines 818-830 — the per-chip section:

> ### 27C080 - 1MB EPROM with fixed active-low CE/OE
> **Package:** 32-pin DIP · **Capacity:** 1048576 bytes · **Control:** /CE, /OE
> | Address (A0-A19) | `12,11,10,9,8,7,6,5,27,26,23,25,4,28,29,3,2,30,31,1` | 20 address lines |
> | Data (D0-D7) | `13,14,15,17,18,19,20,21` | 8 data lines |
> | /CE | 22 | Active low |
> | /OE | 24 | Active low |
> | VPP | 24 | Acts as /OE during read |
> | /PGM | 22 | Acts as /OE during read |
> | VCC | 32 | +5V |
> | GND | 16 | 0V |

The address list is **`DIP32_STD`'s 19-entry list with `1` appended** — index 19 = pin 1 = A19. That
is precisely the shape D-01 needs to make SAFE-01's wording literally true, and it uses the existing
ordered-list semantics (`address-bus-pins` index *is* the address bit) with no new mechanism.

**The 27C080 puts VPP on pin 24, shared with `/OE`** — the same trick the 28-pin 27C512 uses
(`DIP28_27512`: `"vpp-pin": [22], "oe-pin": [22]`). The programming strobe is `/PGM` on pin 22,
shared with `/CE`, which is the pin the firmware already strobes (`rurp_chip_enable()`), so **no
`rw-pin` is required**.

### Verbatim JSON

Key name `DIP32_27C801` per CONTEXT's discretion note (`DIP32_27C020` / `DIP32_SST39SF040`
convention: exemplar part number).

```json
    "DIP32_27C801": {
        "name": "JEDEC 32-pin UV-EPROM 1M (27C080 / M27C801 — A19 on pin 1, VPP on pin 24)",
        "comment": "Per piersfinlayson/one-rom docs/CHIP-TYPES.md (datasheet-verified): the 8 Mbit 27C080/M27C801 class has 20 address lines (A0-A19) with A19 at pin 1, and VPP at pin 24 shared with /OE — the same OE/VPP sharing DIP28_27512 uses at pin 22. /PGM is pin 22 shared with /CE. Distinct from DIP32_STD (27C040 class: pin 1 = VPP, pin 31 = A18, 19 address lines) and from DIP32_27C020 (pin 31 = PGM). Assigned by resolve_pinout_key to pin_count=32 && pm_idx=12 && proto_id=0x08 && variant_lo=0x03 — the eight 1 MB rows AM27C080, AM27LV080, AT27C080, M27C801 (x2), MX27C8000, MX27C8000A, UPD27C8001. HARDWARE: A19 at pin 1 means socket pin 1 carries an address line, and on Rev 2.x shields socket pin 1 is also the VPP-enable line (JP5 = A19_CUT bridges it to the switched VPP node). JP5 must be cut for these parts, per the shield silkscreen.",
        "pins": {
            "vcc-pin": [32], "gnd-pin": [16],
            "vpp-pin": [24], "oe-pin": [24],
            "address-bus-pins": [12, 11, 10, 9, 8, 7, 6, 5, 27, 26, 23, 25, 4, 28, 29, 3, 2, 30, 31, 1],
            "data-bus-pins": [13, 14, 15, 17, 18, 19, 20, 21],
            "ce-pin": [22]
        }
    }
```

**Host-side resolution check** `[VERIFIED: firestarter_app/firestarter/database.py:86-107]` — every
pin the entry names is present in `pin_conversions[32]`: `1→21`, `2→16`, `3→15`, `4→12`, `5..12→7..0`,
`22→ROM_CE`, `23→10`, `24→ROM_OE`, `25→11`, `26→9`, `27→8`, `28→13`, `29→14`, `30→20`, `31→22`. So
`get_bus_config` emits no `Pin N not in pin_conversions` warning, and the resulting bus is
`[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,20,22,21]` with `vpp-pin` dropped by the `ROM_OE` rule.

**Registration.** `VALID_PINOUT_KEYS` is `set(json.load(_f).keys())` over `pinouts.json`
`[VERIFIED: firestarter_app/tools/build_db.py:183]`, so adding the top-level key registers it. Note
the guard at `build_db.py:286-287` **prints `WARN:` to stderr and continues** — it does not fail
closed. CONTEXT calls it "self-checking"; it is self-*announcing*. If the planner wants the property
CONTEXT assumes, that is a one-line change to raise instead of warn (and it would be a genuine
improvement, since `tools/` is outside every CI gate).

---

## The affected-part predicate and its seam (SAFE-01, success criterion 2)

**The seam is `EpromDatabase.get_pin_map(pins, pin_map_id)`**
`[VERIFIED: firestarter_app/firestarter/database.py:232-238]`:

```python
def get_pin_map(self, pins: int, pin_map_id: str):
    if pin_map_id in self.pin_maps:
        return self.pin_maps[pin_map_id].get("pins")
    return None
```

It reads `self.pin_maps`, which is loaded from `pinouts.json` and merged with the user's
`~/.firestarter/database.json` overrides via `_merge_pin_maps`
`[VERIFIED: firestarter_app/firestarter/database.py:215-230]`. So a predicate expressed against it is
derived from the shipped pin maps **and** honours user overrides — which is what SAFE-01 asks for and
what makes success criterion 2 satisfiable.

**The literal SAFE-01 predicate** ("the pin map puts A19 on socket pin 1"), plus the generalisation
the trace justifies:

```python
def pin1_carries_an_address_line(pin_map: dict) -> Optional[int]:
    """Return the address-bit index socket pin 1 carries, or None.

    `address-bus-pins` is an ordered A0..An list, so the index IS the address bit.
    """
    abp = pin_map.get("address-bus-pins") or []
    return abp.index(1) if 1 in abp else None
```

- Literal SAFE-01: `pin1_carries_an_address_line(pm) == 19`.
- Structural (what the hardware actually cares about): `pin1_carries_an_address_line(pm) is not None`.

The two differ on exactly one shipped layout: `DIP32_SST39SF040` puts **A18** on pin 1
`[VERIFIED: firestarter_app/firestarter/data/pinouts.json:79]`, covering ~47 rows. Those parts are
5 V flash on protocol 0x06, whose firmware path (`flash_utils.cpp:23,27,32`) touches only
`CTRL_READ_WRITE` and never enables the regulator — so they are **structurally affected but not
damage-capable**, which is precisely the D-06 distinction. **Recommendation: compute the structural
set, then intersect it with the damage-capable protocol/command set for the gate**, and record the
non-damage-capable remainder in the phase record rather than gating it. That keeps SAFE-01's
"derived, never hand-listed" property while honouring D-06.

**The test for success criterion 2.** `tests/test_eprom_database.py` already exercises
`get_bus_config` against the real `chip_database.json` + `pinouts.json`
(`[VERIFIED: firestarter_app/tests/test_eprom_database.py:129-130, 178, 201, 259]`), and
`_merge_pin_maps` gives a no-source-edit injection point. The criterion is satisfied by a test that
merges a synthetic pin map carrying `address-bus-pins[19] == 1` plus a synthetic chip row referencing
it, then asserts the part appears in the affected set — with the assertion written over the predicate
function, not over a literal list.

---

## The gate mechanism, priced (D-05, D-06, D-07)

### D-05 recommendation: the gate ships

**Recommended resolution: SAFE-02 and SAFE-04 are NOT retired. A gate ships, scoped to `write` and
`erase`.**

The evidence that carries it, in one chain:

1. Socket pin 1 is strapped to the switched VPP node by JP5, bridged by default
   `[VERIFIED: kicad_sch JP5 symbol + kicad_pcb JP5 pads]`.
2. On Rev 2.x, physical control bit 0x08 is both `CTRL_VPP_P1_ENABLE` and `CTRL_ADDRESS_LINE_18`
   `[VERIFIED: rurp_pinout.h:144, rurp_hw_rev_utils.h:18-26]`.
3. Socket pin 1 is bus line 21 `[VERIFIED: database.py:86]`, and bus line 21 is inside the address
   mask that `mem_util_calculate_top_address_register` drives from the address
   `[VERIFIED: memory.cpp:152-153]`.
4. A write holds the boosted route asserted across every block and rewrites the control register on
   every byte `[VERIFIED: eprom.cpp:266-269, 481-489; memory.cpp:152-160]`.
5. Therefore, on a Rev 2.x board with JP5 bridged, writing an 8 Mbit part drives socket pin 1 —
   the part's A19 — from the 12.75 V programming rail for every address ≥ 0x80000. **This is true
   after the map fix, not only before it**: the fix moves VPP off pin 1 but puts A19 there, and A19
   and VPP-enable are the same physical line.
6. Before the fix the same pin is energized by the other route (`vpp-pin: [1]` ⇒
   `using_p1_as_vpp` ⇒ the write's `CTRL_VPE_ENABLE` is rewritten to P1). So the map fix **relocates**
   the hazard; it does not remove it.

The operator's expected outcome — that the map fix supersedes the gate — is not supported by the
trace. The only reading under which it would hold is if the shield could drive socket pin 1 as a
logic line without turning on Q8; it cannot, because `P1_VPP_ENABLE` feeds D33 (the logic driver) and
Q5→Q8 (the 12 V switch) from the **same net** `[VERIFIED: kicad_sch — D33 anode and R25 pin 1 are
both on the `P1_VPP_ENABLE` global-label net]`.

**Honest limit on this recommendation.** The trace is sufficient to decide *that* something is owed.
It rests on one unmeasured link — the unboosted rail level (§ above) — for the narrower claim that
**reads** are safe and so need no gate. If that probe came back boosted, D-06's damage-capable set
widens from `{write, erase}` to `{write, erase, read, verify, blank}` for affected parts, and the
gate's scope changes with it. **That probe is the single measurement that would change the gate's
shape, and it is cheap: measure `VPE` at `J6` pin 4 with the regulator off.** Everything else needed
to decide is already on the desk.

### D-06 scope: `write` and `erase`

Damage-capable, from the firmware table above:

| Host command | CLI | Reaches socket pin 1 for an affected part? |
|---|---|---|
| `write` | `cli_handlers.py:543` (decorator) / `:608` (def) | **Yes** — the per-pass pulse (`eprom.cpp:453`) and the pre-write erase (`eprom.cpp:136-141` → `:547`) |
| `erase` | `cli_handlers.py:819` / `:845` | **Yes** — `eprom.cpp:117-120` → `:547` |
| `read` | `cli_handlers.py:512` / `:522` | No 12 V — the address drives the pin, but the rail is unboosted (**inferred**, probe named) |
| `verify` | `cli_handlers.py:769` / `:781` | Same as `read` |
| `blank` | `cli_handlers.py:800` / `:810` | Same as `read` |
| `id` | `cli_handlers.py:873` / `:883` | No — 12 V goes to socket pin **26** (A9) |
| `dev test` | `cli_handlers.py:2379` (def; decorators from `:2363`) | **Yes** — it writes; and it is the canonical non-interactive caller |

### D-07 escape hatch: what exists and what does not

`[VERIFIED: firestarter_app/firestarter/submit.py:641, 701, 728, 745, 778]` The established pattern
is exactly what CONTEXT names: `isatty_fn: Any = None` in the signature,
`isatty_fn = isatty_fn or (lambda: sys.stdin.isatty())` at the top, `if not isatty_fn():` for the
off-TTY branch that returns without ever calling `confirm_fn`, and
`confirm_fn: Any = Confirm.ask` with `default=False` at each ask. `firestarter/firmware.py:20, 895`
uses `Confirm.ask` directly. No new mechanism is needed.

`[VERIFIED: firestarter_app/firestarter/cli_handlers.py, `-f/--force` option definitions]` Current
`--force` semantics, confirming D-07's premise:

| Command | `--force` help text |
|---|---|
| `read` (`:516`), `write` (`:565-566`), `verify` (`:774-775`) | "Force, even if the chip id doesn't match." |
| `blank` (`:803-806`), `erase` (`:822-825`) | "Force, even if the VPP or chip id doesn't match." |
| `id` (`:876-879`) | "Force, even if the VPP is not correct." |

`--force` maps to `FLAG_FORCE`, which firmware consumes to downgrade a VPP or chip-ID **error** to a
**warning** (`eprom.cpp:533-536`, `eprom.cpp:571`). It is a measurement-tolerance override. D-07's
refusal to reuse it is right, and the reasoning is checkable against `mem_util_report_chip_id`'s own
comment: *"eprom.cpp's standalone `CMD_CHECK_CHIP_ID` path must keep refusing unconditionally
regardless of `--force`"* `[VERIFIED: firestarter/include/memory_utils.h:50-58]`.

**`--auto` and `--chain` do not exist in the firestarter CLI.**
`[VERIFIED: /usr/bin/grep -rn '"--auto"|"--chain"' firestarter_app/firestarter/ → no matches]` They
are GSD execution-mode flags. SAFE-04 lists them because a GSD run in those modes invokes the CLI
non-interactively — so **the non-TTY refusal is the mechanism that covers them**, and no new flag is
required. The planner should say this explicitly in the plan so no one goes looking for CLI options to
plumb.

### CLAIM-07 collision — stated precisely

`[VERIFIED: firestarter_app/firestarter/cli_handlers.py:2299-2306]` `_is_interactive()` is
`return sys.stdin.isatty()`, with a docstring explaining that `CliRunner.invoke` replaces `sys.stdin`
so tests must patch the function rather than `sys.stdin.isatty`.

`[VERIFIED: /usr/bin/grep -rn "_is_interactive" firestarter_app --include=*.py, excluding build/ and
__pycache__]` **It has no production consumer today.** Its only references are:
`tests/test_dev_test_cmd.py:10, 14, 520, 843, 871`; `tools/check_devtest_orchestrator.py:66, 163`
(the `_HANDLER_FUNCTION_NAMES` allow-list); and `tests/test_check_devtest_orchestrator.py:585`.

That is *why* CLAIM-07 removes it. And `tests/test_check_devtest_orchestrator.py:575-598` says so in
prose: the subset assertion *"is a SUBSET, never an equality, because `_is_interactive` is
legitimately listed but not referenced from `dev_test`'s body — an equality assertion would be red for
the opposite reason on day one."*

**The honest options, for the planner to choose between:**

| Option | What it means | Cost |
|---|---|---|
| **A — Phase 182 becomes `_is_interactive`'s first live consumer** | The gate calls it (or an injectable `isatty_fn` defaulting to it). CLAIM-07 must be **revisited before Phase 185 runs**: "removed" becomes "kept, now genuinely consumed, and the two `..._on_a_tty` tests rewritten to gate real behaviour". | One `REQUIREMENTS.md` edit to CLAIM-07's wording, plus a note in `test_check_devtest_orchestrator.py:585`'s docstring (the "legitimately listed but not referenced" clause becomes stale the moment the gate lands). |
| **B — Phase 182 uses the `submit.py` `isatty_fn` pattern and does not touch `_is_interactive`** | The gate carries its own injectable `isatty_fn` default, exactly as `submit_report` does. `_is_interactive` stays unreferenced and CLAIM-07 removes it in Phase 185 as planned. | Nothing. Two tiny lambdas instead of one shared helper. Phase 185 stays unblocked. |

**Recommendation: Option B.** It is the established pattern in this codebase (`submit.py`), it keeps
the two phases decoupled, it is more testable (injection beats monkeypatching), and it avoids
reviving a symbol another phase in the same milestone is deleting. If the planner prefers A, the plan
**must** carry an explicit task to amend CLAIM-07 and the orchestrator-test docstring — silently
reviving `_is_interactive` is the failure mode CONTEXT warns about.

### Where the gate goes

`[VERIFIED: firestarter_app/firestarter/eprom_operations.py:381, 1967, 2130]` Every chip operation
enters through `EpromOperator`'s `_operation_context` (`write_eprom` at `:2000`, `erase_eprom` at
`:2137`), which is what opens the serial link. "Stops before touching the bus" therefore means
**before** that `with` statement.

| Placement | Covers | Tradeoff |
|---|---|---|
| CLI command bodies (`cli_handlers.py` `write` `:608`, `erase` `:845`) | Both CLI paths | TTY policy sits at the CLI boundary where it belongs; but `dev test` calls the operator layer, so it needs its own arm |
| Top of `write_eprom` / `erase_eprom`, before `_operation_context` | CLI **and** `dev test` **and** any future caller | One place, fail-closed by default; but it puts a TTY concern in the operator layer |

**Recommendation: predicate + hazard-text helper in its own small module (or beside `get_pin_map` in
`database.py`); the interactive prompt in the two CLI command bodies; a hard, unconditional refusal at
the top of `write_eprom`/`erase_eprom` for any caller that did not pass an explicit acknowledgement.**
That gives D-07's "non-interactive refuses" for free at the operator layer and keeps the prompt where
`isatty` reasoning is natural. It also means `dev test` refuses without a special case.

### Hazard text — checkable against the silkscreen

CONTEXT's `<specifics>` sets the standard: any operator-facing jumper text should be checkable
against JP4's own sentence, *"Only for ROMs with VPP on P1."* The JP5 legend is unconditional:
*"JP5: Cut for ROMs with A19 on P1"* `[CITED: evidence/shield-rev2-jp4-jp5.jpg, per CONTEXT.md]`. The
gate's message should say the same thing, name the part's A19 pin, name the operation, and not claim
to know JP5's state. Do **not** reproduce *"Open for 32 pin ROMs, Closed for 28 pin ROMs"* — D-10 and
this trace both establish it is two-state language on a three-pole part.

---

## File:line inventory — every edit the phase must make

| # | Path | Line(s) | Change | Requirement |
|---|---|---|---|---|
| 1 | `firestarter_app/firestarter/data/pinouts.json` | after `:93` (end of `DIP32_27C020`) or at end of object | Add the `DIP32_27C801` layout (verbatim JSON above) | SAFE-01 / D-01 |
| 2 | `firestarter_app/tools/build_db.py` | `:270-280` (the `proto_id in {0x07,0x08,0x10}` arm) | Add the `variant_lo == 0x03` and `== 0x02` forks ahead of the residual size test | D-02 |
| 3 | `firestarter_app/tools/build_db.py` | `:8` (`from firestarter.constants import MAX_27C020_SIZE`) and `:271` (its only use) | Replace with a module-local boundary constant carrying an honest name and no firmware-parity claim | D-03 |
| 4 | `firestarter_app/firestarter/constants.py` | `:43-51` (comment block + `MAX_27C020_SIZE = 262144`) | Delete; the comment's claim *"Firmware parity: firestarter.h #define MAX_27C020_SIZE 262144"* is false | D-03 |
| 5 | `firestarter_app/tests/test_revision_constants_parity.py` | `:686-710` (`@requires_fw` + `test_max_27c020_size_parity`, docstring `:688-707`, assert `:710`) | Delete, or replace per the recommendation below | D-03 |
| 6 | `firestarter_app/tools/DECODE-NOTES.md` | `:53-69` (§1's `variant_lo` table + the "Critical (Pitfall 3)" note) | Add the three 32-pin `pm_idx=12` rows; §1 currently documents only the 24- and 28-pin arms, and its opening sentence *"It is NOT changed this phase — `resolve_pinout_key` stays verbatim"* becomes stale | D-02 |
| 7 | `firestarter_app/firestarter/data/chip_database.json` | 8 rows (`AMD/AM27C080`, `AMD/AM27LV080`, `ATMEL/AT27C080`, `MACRONIX(MXIC)/MX27C8000`, `MACRONIX(MXIC)/MX27C8000A`, `NEC/UPD27C8001`, `SGS-THOMSON/M27C801`, `ST/M27C801`) | **Output of a `build_db.py` re-run**, never hand-edited | D-04 |
| 8 | `firestarter_app/tools/diff_db.py` | `_RULE_FIELD_PATHS` at `:317-370`, the rule-text dict at `:48-190`, the dispatch ladder at `:435-600` | New rule label (e.g. `RULE_PHASE182_A19_PINOUT`) scoped to `("pinout",)` for the eight part numbers — **without it the regen exits 1 (BLOCK: unexplained diff)** per `diff_db.py:11-18` | D-04 |
| 9 | `firestarter_app/tests/golden/wire_dict_baseline.json` | **do not touch** — `:437` (`AMD\|AM27C080\|12`), `:745` (`AM27LV080`), `:2518`, `:11465`, `:11498`, `:13920`, `:15996`, `:18886` | The golden stays byte-unchanged (D-17); see #10 | D-04 |
| 10 | `firestarter_app/tests/golden/wire_dict_expected_deltas_182.json` | new file | 8 deltas, each `{"bus-config": {"bus": [...20 lines...]}}`. The composition is a **shallow** `expected[key].update(delta_wire)` (`test_wire_dict_equivalence.py:300-305`), so supplying the whole `bus-config` object is what removes the `vpp-pin` key | D-04 |
| 11 | `firestarter_app/tests/test_wire_dict_equivalence.py` | `_DELTAS_*` constants `:93-101`; the composition test `:212-318` (non-vacuity legs (b)/(d), exact-count legs (c)/(e), field-disjointness leg (f), composition (g)); the capability-to-fail leg `:438` | Add a `_DELTAS_182` layer with its own non-vacuity + exact-count (`== 8`) + capable-of-failing legs. Field-disjointness holds: 149 touches `page-size`, 153 touches `flags`, 182 touches `bus-config`. `test_wire_key_union_is_exactly_nine_keys` (`:325`) is **unaffected** — `vpp-pin` is nested inside `bus-config`, not a top-level wire key | D-04 |
| 12 | `firestarter_app/firestarter/ic_layout.py` | `:186-201` (`_get_rev2_2_jumper_settings_data`, `def` at `:186`) | Delete | **SAFE-05** |
| 13 | `firestarter_app/firestarter/ic_layout.py` | `:656` (`# output_data["jumpers"].update( self._get_rev2_2_jumper_settings_data(jp4_rev2))  # noqa: E501`) | Delete | **SAFE-05** |
| 14 | `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` | `:428` (AM27C080), `:430` (AT27C080), `:431` (MX27C8000) and the other five 8 Mbit rows — the `DIP32_STD` column | Regenerated artefact; consumed by `tests/test_audit_coverage_matrix.py` via `tools/audit_coverage_matrix.py`. **Memory warns the regenerator MUTATES the ledger** (`reference_audit_coverage_matrix_golden_stale`) — treat as a deliberate, reviewed regeneration, not a sweep | D-04 |
| 15 | `.planning/notes/jumper-display-ground-truth.md` | JP4 row in §"What each jumper actually routes" (`:37`); §"Confirmed defects" item 4 (`:60-64`); the Rev-2.3 footprint claim in the same JP4 row | Correct JP4's description (it is not "VPP to socket pin 1 only" — pin 1 is its *common*), move the footprint change from 2.3 to 2.2, add the VPP-destination table, resolve standing defect 4 | D-11 / D-12 |
| 16 | `.planning/v1.7-SHIELD-REVS.md` | §1 `:19`, `:21`, `:23`; §3 `:42`, `:43`, `:44`, `:45`; §4 `:54`, `:55`, `:56`, `:58`; §5 `:70`, `:71`, `:72`, `:73`, `:74`; §6 `:89`, `:91`; §7 `:132`; §"Detect" `:154`, `:163`, `:175`; §"JP4 Caveat" `:196-198`; §"Detect table" `:208`, `:209` | Correct the footprint-change revision (2.1→2.2, not 2.2→2.3) and **retract the R41-couples-to-JP4 claim outright** — measured false. Add the systemic-cause note per D-13. Revision-qualify §6's 24-pin capability rows | D-13 / D-14 |
| 17 | `.planning/REQUIREMENTS.md` | § SAFE `:35-46`, Traceability table | SAFE-01 wording (predicate achieved by correcting the pin map); SAFE-02/SAFE-04 status per the D-05 resolution; **if Option A is chosen for `_is_interactive`, CLAIM-07 `:105-107` too** | D-05 (+ CONTEXT deferred item) |
| 18 | `.planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md` | frontmatter `resolves_phase: 182` | Re-point once the D-09 phase has a number (items 1 and 2 move there; item 3 lands here) | CONTEXT Folded Todos |
| 19 | New backlog items | `.planning/ROADMAP.md` § Backlog | D-15.1 (DIP24 unreachable VPP — now measured, see the VPP table), D-15.2 (mirrored hazard), and the deferred fail-closed "size_bytes fits declared address lines" generator assertion | D-15 |
| 20 | *(gate only, if D-05 ships one)* `firestarter_app/firestarter/cli_handlers.py` | `write` body from `:608`, `erase` body from `:845` | Prompt + refusal per § *The gate mechanism, priced* | SAFE-02 / SAFE-04 |
| 21 | *(gate only)* `firestarter_app/firestarter/eprom_operations.py` | top of `write_eprom` `:1967-2000` (before the `with _operation_context`), top of `erase_eprom` `:2130-2137` | Unconditional refusal absent an explicit acknowledgement — covers `dev test` and any future caller | SAFE-04 |
| 22 | *(gate only)* new/extended test file in `firestarter_app/tests/` | — | Predicate test (success criterion 2), TTY-refusal test, decline-aborts-with-no-operation test | SAFE-01/02/04 |

### Success criterion 4 has a grep trap — flag it to the planner

The criterion is `grep -rn '_get_rev2_2_jumper_settings_data' firestarter_app/` returns nothing.
Measured this session, two hazards make that command answer the wrong question:

1. **A stale `build/lib/` copy exists.** `/usr/bin/grep -rn` finds the symbol at
   `firestarter_app/build/lib/firestarter/ic_layout.py:186` and `:656` in addition to the live file.
   `build/` is gitignored (`.gitignore:3`), so the criterion would read RED after a correct deletion.
2. **`grep` on PATH in this devcontainer is ugrep and honours `.gitignore`**
   (`reference_devcontainer_grep_is_ugrep_honors_gitignore`), so the *same* command reads GREEN with
   the PATH grep and RED with `/usr/bin/grep` — for reasons that have nothing to do with the deletion.

**Recommendation:** the plan's automated leg should be scoped so it cannot pass or fail for the wrong
reason, e.g. `git -C firestarter_app grep -n '_get_rev2_2_jumper_settings_data' -- '*.py'` (tracked
files only, tool-independent), or `/usr/bin/grep -rn --exclude-dir=build --exclude-dir=__pycache__`.
Do **not** leave it as the bare command in the phase's acceptance criteria.

---

## Test infrastructure the phase sits beside

`[VERIFIED: firestarter_app/pyproject.toml:12, 71-73, 105-107, 110, 155]`
`requires-python = ">=3.9"`, `target-version = "py39"`, mypy `python_version = "3.10"`,
`[tool.pytest.ini_options] testpaths = ["tests"]`, `addopts = "-ra -q"`, `test` extra pins
`pytest>=8.0`, `syrupy>=5.0,<7`, `ruff>=0.15.14`.

Install and run:

```bash
cd /workspaces/firestarter_app
uv venv --python 3.11 .venv-ci && . .venv-ci/bin/activate   # CI is py3.11 ONLY; this container is 3.12
pip install -e '.[test]'
pytest tests/test_eprom_database.py tests/test_build_db_inclusion.py \
       tests/test_wire_dict_equivalence.py tests/test_ic_layout.py \
       tests/test_revision_constants_parity.py -o addopts=""
```

`-o addopts=""` is required to see the count line — the repo's `-ra -q` plus a `-q` on the command
line suppresses it (`reference_pytest_addopts_q_suppresses_count_line`). The py3.11 venv matters:
this devcontainer's 3.12 has already been **proven** to mask app CI breakage
(`reference_devcontainer_py312_masks_ci_py39`).

What already guards this code:

| Area | Test | Note |
|---|---|---|
| `resolve_pinout_key` | `tests/test_build_db_inclusion.py` (`:79-709`; SRAM-pinout class at `:379-475`) | Exercises it via classification outcomes; no direct 32-pin arm test exists |
| `pinouts.json` × `pin_conversions` composition | `tests/test_eprom_database.py` (`:129-130`, `:178`, `:201`, `:259`) | Asserts against the **real** shipped data — the natural home for the new-layout test |
| Wire-level equivalence (746 chips) | `tests/test_wire_dict_equivalence.py` + `tests/golden/wire_dict_baseline.json` + `wire_dict_expected_deltas_{149,153}.json` | The delta-layer discipline (D-17: never re-capture the golden) |
| Regeneration diff | `tools/diff_db.py` + `tests/test_diff_db_gate.py` against `tools/baseline/chip_database.baseline.json` (744 chips) | Exit 1 on an unexplained diff — this is the instrument that proves the regen is exactly the 8 rows |
| DB field inventory | `tests/test_chip_database_field_inventory.py` + `tests/golden/chip_database_field_inventory.json` (`meta`/`totals`/`levels`/`protocol_chip_counts`/`generator_emitted_chip_entry_keys`) | No new field is emitted, so expected unchanged — verify, don't assume |
| `ic_layout.py` jumper derivation | **nothing** | `/usr/bin/grep -rln "jumper" firestarter_app/tests/` returns no matches. `tests/test_ic_layout.py` (312 lines, 9 tests) covers pin-name display, type labels and erase-capability rows — **not** the jumper block. SAFE-05's deletion is currently unguarded, and a new test would be the first |

`[VERIFIED: firestarter_app/tests/scan_paths.py:298, 306, 339]` `pinouts.json` is registered as a
guarded path (including via `tools/gen_sdp_bus_config.py`'s `_PINOUTS_DEFAULT`). Adding a top-level
key does not change the path set, so no `scan_paths` edit is expected — but Phase 185's CLAIM-09 adds
a fail-closed existence check over `ScanPathEntry` targets, so do not *move* the file.

---

## The `ic_layout.py` derivation still prints JP4 = Closed after the fix

`[VERIFIED: firestarter_app/firestarter/ic_layout.py:625-656]` The jumper derivation sets
`has_vpp_pin_on_map = True` whenever the pin map contains **any** `vpp-pin` key, then at
`pin_count == 32` does `jp4_rev2 = 2 if has_vpp_pin_on_map else 1` (2 = "Closed").

The new layout declares `"vpp-pin": [24]`, so `has_vpp_pin_on_map` stays `True` and
`firestarter info` will **still print JP4 = Closed** for the eight 8 Mbit parts — which is wrong for a
32-pin part, and is `jumper-display-ground-truth.md`'s confirmed defect 1 (pin-count key instead of
pin-map identity). **The map fix does not fix the display.** That is squarely D-09's job and out of
scope here; the phase record should say so explicitly so the next reader does not read the surviving
wrong output as a Phase 182 regression.

---

## Common pitfalls

### Pitfall 1: treating the map fix as the whole answer
**What goes wrong:** the plan ships the pinout correction, retires SAFE-02/SAFE-04, and closes gh#60
saying the tool no longer asks for VPP on pin 1 — while a `write` on the corrected map still drives
12.75 V onto A19 for the upper half of the part.
**Why it happens:** the Rev-2 `CTRL_ADDRESS_LINE_18` / `CTRL_VPP_P1_ENABLE` alias is one `#define`
(`rurp_pinout.h:144`) two headers away from the code that looks safe.
**How to avoid:** hold the chain in § *D-05 recommendation* — pin map → bus line 21 →
`CTRL_ADDRESS_LINE_18` → Rev 2 physical 0x08 → Q8 → JP5 → socket pin 1.
**Warning signs:** any sentence of the form "once VPP is on pin 24 the hazard is gone".

### Pitfall 2: dispatching on `variant_lo` alone at 32 pins
**What goes wrong:** `SST37VF040` (pm 13, `variant_lo=0x04`, 524288) moves off `DIP32_STD` onto
`DIP32_27C020`, putting a 512 KB part's A18 pin onto a PGM strobe. Protocol-0x10 rows carrying
`variant_lo` 0x10–0x13 also reroute if the fork is hoisted above the protocol test.
**Why it happens:** the 24- and 28-pin arms dispatch on `variant_lo` alone, so it looks like the
pattern to copy wholesale.
**How to avoid:** keep the fork inside `proto_id == 0x08`, and keep the size threshold as the residual
arm. The measured diff is then exactly 8 rows.
**Warning signs:** a diff touching more than eight rows; `tools/diff_db.py` exiting 1.

### Pitfall 3: hand-editing `chip_database.json`
**What goes wrong:** the next regeneration silently reverts it, and the other parts sharing the decode
path stay wrong.
**How to avoid:** D-04 / milestone D-6 — the diff is a `build_db.py` output. `tools/` is outside every
CI gate, so nothing catches a generator that was never re-run.

### Pitfall 4: re-capturing `wire_dict_baseline.json`
**What goes wrong:** `test_live_capture_matches_golden_plus_the_149_and_153_deltas`'s
anti-laundering leg (`:219-234`) goes red, and the phase erases Phase 148's central claim.
**How to avoid:** add `wire_dict_expected_deltas_182.json`. The composition is a shallow `update`, so
the delta must carry the **whole** replacement `bus-config` object — which is also how the `vpp-pin`
key gets removed.

### Pitfall 5: reviving `_is_interactive`
**What goes wrong:** Phase 185's CLAIM-07 is contradicted mid-milestone, and
`tests/test_check_devtest_orchestrator.py:585`'s "legitimately listed but not referenced" docstring
becomes false without anyone noticing.
**How to avoid:** Option B — carry an injectable `isatty_fn` per the `submit.py` pattern. If Option A,
amend CLAIM-07 and that docstring in the same plan.

### Pitfall 6: inferring Rev 2.2 from the shared Rev 2.1 schematic blob
**What goes wrong:** three recorded wrong answers so far (R41 4k7-vs-10k, JP4's footprint, and the
revision at which the footprint changed). Rev 2.2 has **no committed schematic** (Phase 31 Finding E)
but it does have its own pos CSV and gerber bundle.
**How to avoid:** read `Rev2.2/W27C512Programmer-top-pos.csv` and `Rev2.2-gerbers.zip` first. This
session's drill-file extraction settled JP4's pad count in about a minute.

### Pitfall 7: writing a source comment
**What goes wrong:** violates `/workspaces/CLAUDE.md`'s hard rule, which is not overridable by a plan.
**How to avoid:** rationale goes in `SUMMARY.md`, `REQUIREMENTS.md` traceability, or the commit
message. Note `pinouts.json`'s `"comment"` field is **data, not a source comment** (every existing
entry has one), and Click docstrings are user-facing `--help` text, not commentary
(`reference_click_docstrings_are_user_facing_help_text`).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| A yes/no prompt with an off-TTY refusal | A bespoke `input()` + `sys.stdin.isatty()` block | `rich.prompt.Confirm.ask` behind an injectable `confirm_fn`, plus an injectable `isatty_fn` — `submit.py:641, 701, 728, 745, 778` | Established, test-friendly, and `CliRunner.invoke` breaks naive `sys.stdin` patching (`cli_handlers.py:2299-2306` says so) |
| The affected-part list | A constant tuple of eight part numbers | A predicate over `EpromDatabase.get_pin_map`'s `address-bus-pins` | SAFE-01 forbids the hand list; the predicate also picks up `~/.firestarter/database.json` overrides via `_merge_pin_maps` |
| Socket-pin → bus-line arithmetic | New offset maths in the gate | `pin_conversions` (`database.py:45-107`) | One source of truth per layer, composed in `get_bus_config`; it already encodes the 24/28/32-pin socket offsets |
| Proving the regen changed only 8 rows | An ad-hoc `git diff` eyeball over a 746-row JSON | `tools/diff_db.py` (+ `tests/test_diff_db_gate.py`) | It is the project's own root-cause-classified diff with exit codes; an unexplained change is exit 1 |
| Recording a wire-level change | Re-capturing `wire_dict_baseline.json` | A new `wire_dict_expected_deltas_182.json` layer | D-17; the golden has an explicit anti-laundering assertion |
| A 27C801 pinout from memory | Reconstructing it from the 27C040 | one-rom `docs/CHIP-TYPES.md` lines 89 / 198 / 818-830 | The same oracle four existing `pinouts.json` entries already cite; caught two real defects historically |
| A pinout oracle from infoic | Parsing infoic's `<maps>` section | Don't — CONTEXT measured it: 121 records, GND pin + masked-pin list only, connectivity with no signal function | It cannot generate a layout definition |

---

## Project Constraints (from CLAUDE.md)

| Directive | Source | Bearing on this phase |
|---|---|---|
| **No comments in product source, at all** — not overridable by plan, task, skill or subagent. GSD provenance never goes in code. | `/workspaces/CLAUDE.md` § "Source code comments — hard rule" | Binds the `build_db.py` edit, the `pinouts.json` entry (its `"comment"` field is data, not a source comment), and any gate code. Planners must not write "add a comment citing X" and must not make "a comment exists" an acceptance criterion. |
| Rationale goes in the phase `SUMMARY.md`, `REQUIREMENTS.md` traceability, or the commit message | same | The SAFE-03 trace's home is `.planning/notes/jumper-display-ground-truth.md` per D-12, with the record in `SUMMARY.md`. |
| Click docstrings are user-facing `--help` text, not commentary | same | Any new CLI option's help text is required, not a comment. |
| Constants duplicated host↔firmware move together | `/workspaces/CLAUDE.md` § Key Architecture Points | `MAX_27C020_SIZE` is the counter-example: it is **not** duplicated (no firmware `#define` exists), which is exactly why D-03 retires it. Retiring it is host-only and keeps the milestone's "firmware at the edges only" constraint. |
| Serial-protocol and flag-bit changes must be kept in sync between `serial_comm.py`/`constants.py` and `firestarter.cpp`/`firestarter.h` | same | **No wire-protocol or flag change is needed.** The bus config is data, not protocol; `vpp_line` absence is already a defined firmware state (`0xFF`). |
| `chip_database.json` is GENERATED; a decode defect is fixed in `build_db.py` | `.claude/skills/devtest-rootcause`, `devtest-triage`; milestone D-6 | D-04. |
| `firestarter_app/tools/` sits outside every CI gate (no mypy, no ruff check, no ruff format) | `/workspaces/CLAUDE.md`; CONTEXT | The `build_db.py` and `diff_db.py` edits are not caught by CI. The plan should carry an explicit local verification step. |
| Milestone close targets `beta`, not `main`; `main` is protected in all three repos | `/workspaces/CLAUDE.md` § Milestone close | Firmware was read at HEAD, which differs from `origin/beta` by one line in `include/version.h` — so this reading is beta's. |

---

## Security Domain

`workflow.security_enforcement` is absent from `.planning/config.json`, so it is enabled. This phase's
security surface is **physical safety and refusal integrity**, not network or credential handling.

### Applicable ASVS categories

| ASVS Category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | Local CLI, no identity |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | No multi-tenant surface |
| V5 Input Validation | **yes** | Click option parsing + `resolve_chip`; the affected-part predicate must fail **closed** on a malformed or unknown pin map (`get_pin_map` returns `None`, and `get_bus_config` already returns `None` for an unknown key — `database.py:240-243`, guarded by `test_unknown_pinout_returns_none` at `tests/test_eprom_database.py:201`) |
| V6 Cryptography | no | None involved |

### Known threat patterns for this stack

| Pattern | STRIDE | Standard mitigation |
|---|---|---|
| Gate silently auto-answered in a non-interactive run | Tampering / Elevation | Refuse when `isatty_fn()` is false; `default=False` on every `Confirm.ask`; a separate acknowledgement, never `--force` (D-07) |
| Escape hatch overloaded onto an existing flag | Elevation of privilege | `--force` means "tolerate a VPP/chip-ID mismatch" (`cli_handlers.py:516, 803-806, 876-879`); gh#62 is a reporter already reaching for it. Do not extend it |
| Predicate fails open on unknown data | Tampering | Unknown pinout key ⇒ no pin map ⇒ the gate must treat the part as affected or refuse, never as safe-by-default |
| Hand-maintained safety list drifts from the database | Repudiation | SAFE-01: derive from `pinouts.json`, and prove it with a synthetic-part test (success criterion 2) |
| Warning printed but operation proceeds | Tampering | Decline must abort with **no operation performed** (success criterion 1) — i.e. the gate sits before `_operation_context` opens the link |
| Supply chain | — | No new package is installed by this phase; see below |

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** The only new runtime dependency
touched is `rich.prompt.Confirm`, already a first-class dependency imported at
`firestarter_app/firestarter/firmware.py:20` and `firestarter/submit.py`. Test extras
(`pytest`, `syrupy`, `ruff`) are already pinned in `pyproject.toml:71-83`. No `npm`/`pip`/`cargo`
install step belongs in this plan.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Python 3.12 (container default) | running the app tests | ✓ | 3.12 | — |
| Python 3.11 | matching app CI exactly | ✓ (via `uv venv --python 3.11`) | 3.11 | None — 3.12 has **proven** to mask CI breakage; use the 3.11 venv |
| `uv` | building the 3.11 venv | ✓ | — | `python3.11 -m venv` |
| `/usr/bin/grep` (GNU) | evidence-grade searching | ✓ | — | None — PATH `grep` is ugrep and honours `.gitignore` |
| `git` | submodule reads, `git grep` scoping | ✓ | — | — |
| Network (gitlab.com raw) | `build_db.py` regeneration, pinned infoic.xml | ✓ (fetched 17.9 MB this session) | commit `a8efaedc` | None — the regen fetches at run time; no committed copy of infoic.xml exists in the repo |
| Network (raw.githubusercontent.com) | one-rom pinout oracle | ✓ | — | Already extracted into this document |
| `pdftotext` | reading a committed datasheet PDF | ✗ | — | Not needed — the pinout came from one-rom's markdown |
| `unzip` | Rev 2.1 / Rev 2.2 gerber archives | ✓ | — | — |
| Bench hardware (Rev 2.2 + Rev 2.0 boards, DMM, USB) | the three D-12 continuity probes and the D-14 `hw_revision` reads | operator-gated | — | None. Chip handling, photographs and multimeter work are operator-only; Claude can drive the boards over USB (`reference_usb_passthrough_bench`) |

**Missing with no fallback:** the continuity probes and the DMM rail measurement. These are the named
outputs of the desk trace, not blockers on planning — the plan can be written with them as explicit
bench tasks.

**Note for the regeneration task:** `build_db.py` fetches infoic.xml from the network at run time
(`build_db.py:406-411`, `MINIPRO_XML_URL` pinned to `a8efaedc`). The fetch succeeded this session. If
it fails during execution the script `sys.exit(1)`s with the error — there is no cached copy and no
offline mode. Worth a one-line precondition in the plan.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | With `CTRL_VPP_REGULATOR_ENABLE` clear, the `VPE` rail sits near VCC (boost pass-through via the inductor and `D1`), so a read driving socket pin 1 applies a logic level rather than a programming voltage | *Which operations energize socket pin 1*; *D-05 recommendation* | **High.** If wrong, `read`/`verify`/`blank` join the damage-capable set and D-06's gate scope must widen. Probe: measure `VPE` at `J6` pin 4 with the regulator off. |
| A2 | Rev 2.0 / Rev 2.1's single JP4 pole connects socket pin 1 to socket pin 3 (the 28-pin position) | *The VPP-destination table* | Medium. Only affects the two Rev 2.0/2.1 table cells and the D-13 corrections for those rows; does not affect the gate. Probe: continuity on the operator's Rev 2.0 board. |
| A3 | A 24-pin part bottom-aligned in the 32-pin socket puts its pin 21 at socket pin 25, and a 28-pin part's pin 1 at socket pin 3 | *The socket-position offsets* | Low — independently corroborated by `pin_conversions` sharing bus line 11 between `[24][21]` and `[32][25]`, and bus line 15 between `[28][1]` and `[32][3]`. |
| A4 | Regenerating with the fixed rule leaves `support_status` and `programming.*` unchanged on the eight rows | *What the eight rows look like today* | Low — all eight are already `supported`, and no rule keys `support_status` off the pinout for them. `tools/diff_db.py` will show it either way; treat any movement as an output, not a defect (CONTEXT). |
| A5 | `pinouts.json`'s `"comment"` field is data, not a "source comment", so the new entry may carry one | *Pitfall 7*; *Project Constraints* | Low — every one of the eight commented entries in the shipped file carries one, so the precedent is unambiguous. Flagged because the CLAUDE.md rule is absolute and the planner should confirm rather than assume. |
| A6 | The Rev 2.2 drill file's fourth 2×2 grid position being undrilled means the 4th pad is genuinely unpopulated (rather than an NPTH or a same-net tie) | *The VPP-destination table* | Low — the PCB pad extraction independently shows only three pads with nets. |

## Open Questions

1. **Does a `read` on an affected part apply a logic level or a programming voltage to pin 1?**
   - What we know: the pin is driven from the address bus via physical bit 0x08 on Rev 2.x, and the
     regulator is off during the read main loop.
   - What's unclear: the absolute `VPE` rail level with the regulator disabled (A1).
   - Recommendation: one DMM reading at `J6` pin 4. Until then, scope the gate to `write` and `erase`
     per the firmware evidence, and record A1 as the assumption the scope rests on.

2. **Which socket pin does Rev 2.0/2.1's single JP4 pole reach?**
   - What we know: two pads, one pole; the silkscreen says "Closed for 28 pin ROMs"; Rev 0's JP3 is
     the two-state ancestor; Rev 2.2 *adds* the 24-pin pole per D-10.
   - What's unclear: no Rev 2.0/2.1 schematic or PCB is committed; the Rev 2.1 pad pair is *vertical*,
     matching Rev 2.2's common+24-pin pair geometrically, which is mildly discordant with the
     inference.
   - Recommendation: continuity probe on the Rev 2.0 board while it is out; record the cell as
     probe-pending in the table meanwhile.

3. **Was Rev 2.3's JP4 silkscreen corrected?**
   - Unresolved and out of scope (CONTEXT deferred). Needs an upstream question to Anders or a
     photograph from a Rev 2.3 holder. Matters to D-09, not to Phase 182.

4. **Does the deferred `size_bytes` ≤ `2**len(address-bus-pins)` generator assertion belong in this
   phase's backlog item or in the wider audit (D-07 deferred)?**
   - It would have caught the 8 Mbit defect at build time, and the corrected layout is the first row
     that satisfies it for 1 MB. Recommendation: file it as a backlog item now (CONTEXT already asks
     for that), do not build it here.

5. **How should the `MAX_27C020_SIZE` parity arm be disposed?**
   - **Recommendation: delete the parity test outright, and keep the decode boundary as a module-local
     constant in `build_db.py` with an honest name and no firmware-parity claim.** Reasoning: the
     boundary is still load-bearing — the measured rule needs it for the residual `variant_lo`
     0x00/0x01/0x04 classes, and removing it moves `SST37VF040` incorrectly. What is false is not the
     number, it is the *parity claim*: no firmware `#define MAX_27C020_SIZE` exists
     (`/usr/bin/grep -rn "MAX_27C020" /workspaces/firestarter/` returns nothing), so the assertion
     compares the host constant to a literal copy of itself and can never fail for a real reason.
     Replacing it with "a test that asserts something real about the 32-pin dispatch" is the other
     option CONTEXT allows and is *also* good — but that test belongs in
     `tests/test_build_db_inclusion.py` beside the other `resolve_pinout_key` coverage, not in a
     *parity* file whose whole premise is host↔firmware duplication. Splitting it that way keeps each
     file's claim true.

---

## Sources

### Primary (HIGH confidence — measured this session)

- `/workspaces/.planning/v1.7/upstream-rurp/hardware/RelativelyUniversalROMProgrammer.kicad_sch` —
  parsed into an s-expression tree; JP4/JP5/Q2/Q6/Q7/Q8/R41/D11/D33/D34/J6/U5 net traces
- `/workspaces/.planning/v1.7/upstream-rurp/hardware/RelativelyUniversalROMProgrammer.kicad_pcb` —
  JP4/JP5/R19/R20/R33/R41 footprint pad→net extraction
- `.../hardware/Rev2.2/Rev2.2-gerbers.zip` → `W27C512Programmer-PTH.drl` — JP4 = 3 drills
- `.../hardware/Rev2.1/RURP-Rev2.1.zip` → `W27C512Programmer-PTH.drl` — JP4 = 2 drills
- `.../hardware/{Rev2.1,Rev2.2,rev2}/W27C512Programmer-top-pos.csv` — JP4 footprint per revision
- `https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml`
  — fetched and decoded through `build_db.py`'s own filter; the eight-row tuple and the 32-pin
  histograms
- `/workspaces/firestarter/` @ `gsd/v1.36-dev-test-fidelity` (= `origin/beta` ± `include/version.h`):
  `include/rurp_pinout.h`, `include/rurp_hw_rev_utils.h`, `include/rurp_shield.h`,
  `include/memory_utils.h`, `src/proms/eprom.cpp`, `src/proms/memory.cpp`,
  `src/proms/flash_intel.cpp`, `src/proms/flash_5v_page.cpp`
- `/workspaces/firestarter_app/`: `tools/build_db.py`, `tools/DECODE-NOTES.md`, `tools/diff_db.py`,
  `firestarter/database.py`, `firestarter/data/pinouts.json`, `firestarter/data/chip_database.json`,
  `firestarter/constants.py`, `firestarter/ic_layout.py`, `firestarter/cli_handlers.py`,
  `firestarter/eprom_operations.py`, `firestarter/submit.py`, `firestarter/firmware.py`,
  `tests/test_wire_dict_equivalence.py`, `tests/golden/wire_dict_baseline.json`,
  `tests/test_revision_constants_parity.py`, `tests/test_eprom_database.py`,
  `tests/test_build_db_inclusion.py`, `tests/test_ic_layout.py`, `tests/scan_paths.py`,
  `tests/test_check_devtest_orchestrator.py`, `pyproject.toml`
- `ran resolve_pinout_key over all 767 filtered infoic rows, current logic vs proposed` — the 8-row
  blast radius

### Secondary (MEDIUM confidence — cited, not independently re-derived)

- `https://github.com/piersfinlayson/one-rom` `docs/CHIP-TYPES.md` lines 89, 196-215, 814-830 — the
  27C080/M27C801 pinout. Datasheet-verified upstream; the same oracle four existing `pinouts.json`
  entries cite. Not circular for this part.
- `.planning/notes/jumper-display-ground-truth.md` — prior schematic-verified JP1–JP5 routing and its
  five confirmed defects (JP4 row corrected by this research)
- `.planning/v1.7-SHIELD-REVS.md` — per-revision deltas (multiple JP4 claims corrected by this
  research; the R41/JP4 coupling claim retracted)
- `.planning/phases/182-jp5-destructive-operation-gate/182-CONTEXT.md` — D-01…D-15, canonical refs,
  the evidence photographs' silkscreen transcriptions

### Tertiary (LOW confidence — flagged, not relied on)

- WebSearch was unavailable this session; no search-derived claim appears in this document.
- Two attempts to fetch an ST/AMD 27C801 datasheet PDF failed (404 / 403 / wrong document). The
  pinout is cited from one-rom instead, which is why it is `[CITED]` rather than `[VERIFIED]`. If the
  planner wants the stronger tag, the repo's own precedent is to commit the datasheet under
  `firestarter_app/datasheets/` (as `M27C512.pdf`, `W27C020.pdf`, `SST39SF0x0A.pdf` already are) and
  cite the page.

---

## Metadata

**Confidence breakdown:**

- VPP-destination topology (JP4/JP5/Q8/socket pins): **HIGH** — three independent committed artefacts
  agree (schematic net trace, PCB pad→net, Rev 2.2 drill file), and Rev 2.2's own gerbers place JP4
  at the identical coordinate the PCB does
- Which operations energize pin 1: **HIGH** for the firmware control-flow (every assert site read at
  file:line); **MEDIUM** for the "reads are safe" conclusion, which rests on assumption A1
- 32-pin decode premise and blast radius: **HIGH** — decoded from the pinned infoic.xml this session
  and cross-run through the real `resolve_pinout_key`
- New layout definition: **MEDIUM** — one independent datasheet-verified oracle, no datasheet page
  read directly
- Rev 2.0/2.1 JP4 pole assignment: **MEDIUM** — inference from footprint pad count, silkscreen and
  Rev 0's JP3, with the probe named
- Rev 0 / Rev 1 column: **LOW** — not traced this session; the project record already carries it as
  untraced
- D-14 (R41 ↔ JP4): **HIGH** — schematic and PCB both show R41 between A3 and GND with no JP4
  connection
- File:line inventory: **HIGH** — every path and range opened this session
- D-05 recommendation: **MEDIUM** — the "a gate is owed" half is HIGH; the "scoped to write and erase"
  half depends on A1

**Research date:** 2026-09-10
**Valid until:** 2026-10-10 for the app/firmware citations (line numbers move on any refactor — cite
symbols alongside them per CLAIM-06's lesson). The hardware artefacts are archival and do not expire.
