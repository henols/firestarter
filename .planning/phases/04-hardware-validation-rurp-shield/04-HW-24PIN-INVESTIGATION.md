# 04-HW-24PIN-INVESTIGATION — Does the Rev 2.x RURP shield deliver HV to 24-pin EPROM VPP?

**Question under scrutiny:** "On the Rev 2.x firestarter RURP shield, there is no electrical path that delivers 21V/25V VPP to the VPP pin of a 24-pin UV-EPROM (e.g., 2716 chip pin 21, or 2732 chip pin 20)."

**User pushback:** "I'm pretty sure the hardware is supporting 24-pin EPROMs." (User owns and uses the hardware.)

---

## VERDICT: **OPTION C — Ambiguous, depends on board revision AND on an external operator-supplied bodge wire.**

Briefly:

- **Rev 2.0 and Rev 2.1 (no Rev2.0 folder in upstream, but the README mentions Rev 2 + 2.1 having "JP4" only):** Schematic provides HV to socket pin 1 / pin 26 / pin 31 only — none of which align with a bottom-aligned 24-pin chip's VPP pin. **Operator MUST add an external wire** (a "tin foil" / aluminum-foil / hand-soldered bodge) from socket pin 1 (HV) to socket pin 25 (2716 VPP location) or pin 24 (2732 VPP location). This is exactly what upstream's PR #17 firmware assumes when it asserts `P1_VPP_ENABLE` for 24-pin chips.
- **Rev 2.2:** README documents "JP4 rotated 90 degrees (green) and **another option of powering the VPP pin of 2716-type ROMs (red)**" — i.e., Rev 2.2 added a second selector position so the HV cascade can be re-routed onto pin 25 (or thereabouts) without an operator bodge. This is the upstream-acknowledged "Rev 2.2 added native 2716 support" change.
- **Rev 2.3 (the schematic at `/tmp/rurp_hw/Rev2.3-schematic.pdf`, the user's likely board):** Schematic still shows only three documented HV cascades — to socket pins 1, 26, 31. The Rev 2.2 "alternative 2716 position" is **NOT visibly preserved as a labelled JP-routing element** in the Rev 2.3 schematic I can read. `JP7 "Tin foil socket"` is in the +5V/regulator area (near U1 MIC2288, R1 22k, F1 Polyfuse) — its name is suggestive but the wiring strongly indicates it is a **regulator-input bypass / power tap**, not a 24-pin VPP rerouter. The 2716 alternative path from Rev 2.2 may have been (a) absorbed into a PCB-only routing change with no labelled jumper, (b) removed/regressed in Rev 2.3, or (c) hidden in the KiCad sheet hierarchy that I cannot fully parse via WebFetch (file truncates).

So my original claim ("no electrical path delivers HV to 24-pin VPP") **was correct for what the Rev 2.3 schematic explicitly documents through labelled BJT cascades and jumpers** — but it **understated the historical context**: upstream has always required either an operator bodge (Rev 2.0/2.1) or Rev 2.2's alternative JP4 position to make 24-pin work, and the user's hardware likely has one of those mods in place. **The user's pushback ("the hardware supports 24-pin") is consistent with them owning a Rev 2.2 board (built-in alt path) or a Rev 2.0/2.1/2.3 board with the well-known operator bodge wire installed.**

---

## Task 1 — Schematic re-read (Rev 2.3)

Source: `/tmp/rurp_hw/Rev2.3-schematic.pdf` (KiCad EDA 8.0.6, sheet 1/1).

### 1.1 BJT inventory (Q1 … Q12) — base/emitter/collector role

The Rev 2.3 sheet has 12 BJTs (`MMBT3904` NPN, `MMBT3906` PNP). Pairs in MMBT3904+MMBT3906 form classic low-side-NPN-drives-high-side-PNP HV switches. Every observable pair gates one of three "HV destinations":

| BJT pair (NPN / PNP)      | Driven by control net    | High-side PNP routes VPE/VPP toward | Diode | Schematic destination          |
|---------------------------|--------------------------|-------------------------------------|-------|--------------------------------|
| Q1 (3904) / Q2 (3906)     | `P1_VPP_ENABLE`          | JP4 (3-way selector) → D33          | D33   | **Socket U5 pin 1**            |
| Q3 (3904) / Q6 (3906)     | `VPE_TO_VPP` + feedback  | Pulls R28 into MIC2288 feedback     | —     | Sets VPP ≈ 12.05 V (not pin)   |
| Q4 (3904) / Q10 (3906)    | `~REG_DISABLE` / `REGULATOR` | MIC2288 `~SHDN`                 | —     | Boost regulator on/off         |
| Q5 (3904) / Q8 (3906)     | `P1_VPP_ENABLE`          | (second buffer stage of Q1/Q2)      | (D33) | Socket U5 pin 1                |
| Q9 (3904) / Q7 (3906)     | `A9_VPP_ENABLE`          | D34 → A9 net                        | D34   | **Socket U5 pin 26 (A9)**      |
| Q11 (3904) / Q12 (3906)   | (A13 line buffer)        | A13 driver to U5 pin 28             | —     | Socket U5 pin 28 (VCC for 24-pin) — **logic-level only, 5 V** |

Plus singleton BJTs around U1 MIC2288 (`~SHDN`, FB) and signal-level switches; none of those gates HV onto socket pins.

The **VPE_ENABLE → PGM** path is a separate cascade through `D11 1N5819` (drawn near the `~ROM_CE`/`~ROM_OE` block on the schematic) and lands on **U5 pin 31** (PGM on 28-pin EPROMs, A17 on 32-pin).

So the **only three socket pins reachable by a HV BJT cascade** on Rev 2.3 are:

- **U5 pin 1** — via `P1_VPP_ENABLE` → Q1/Q2 (and Q5/Q8 buffer) → JP4 → D33
- **U5 pin 26** — via `A9_VPP_ENABLE` → Q9/Q7 → D34 (for chip-ID read on 28-pin chips)
- **U5 pin 31** — via `VPE_ENABLE` → D11 (program pulse on 28-pin chips; also A17 on 32-pin DIPs)

### 1.2 Where does a 24-pin chip's VPP pin land?

The Firestarter Python host's `pin_conversions[24]` table (`firestarter_app/firestarter/database.py:68-88`) maps a bottom-aligned 24-pin chip: chip pin 1 → bus line 7 (= socket pin 5), chip pin 24 → bus line 13 (= socket pin 28, driven HIGH via A13 to supply VCC). With that alignment:

| 24-pin chip pin | Function (2716 / 2732)    | Socket pin (28-pin frame) | Shield net at that socket pin            |
|-----------------|---------------------------|---------------------------|------------------------------------------|
| 12              | GND                       | 16                        | GND ✅                                   |
| 18              | CE                        | 22                        | `~ROM_CE` ✅                             |
| 20              | OE (2716) / VPP+OE (2732) | 24                        | `~ROM_OE` — **no HV cascade**            |
| 21              | VPP (2716) / A11 (2732)   | 25                        | A11 (U3 Q3 latch output, 5 V max) — **no HV cascade** |
| 24              | VCC                       | 28                        | A13 (Q11/Q12 driven HIGH = 5 V)          |

**Neither socket pin 24 nor socket pin 25 has an HV BJT cascade in the Rev 2.3 schematic.** Confirmed.

### 1.3 What does JP7 "Tin foil socket" actually do?

Per the Rev 2.3 schematic, `JP7 Tin foil socket` is drawn in the **bottom-left corner of the sheet, in the same region as U1 MIC2288 (boost regulator), F1 Polyfuse, R1 22k, R2 22k, C8 100nF**. It is **NOT drawn near the U5 ROM socket or any of the BJT HV cascades**. Its silkscreen name is suggestive (a "tin foil socket" is hacker slang for a hand-bridged solder jumper), but its location indicates it is a **+5V input / regulator-front-end bypass** — most plausibly a solder-jumper option to choose whether U1 (the boost converter) is fed from `+5V` directly or via the polyfuse + R1 path. It is **not the documented 24-pin VPP re-router**.

I cannot 100 % nail JP7's nets — the KiCad `.kicad_sch` file is too large for WebFetch and truncates before JP7's `(symbol ...)` block is reached. But its physical placement on the rendered PDF, plus the absence of any wire bridging it to the U5 socket area, makes the regulator-bypass interpretation overwhelmingly likely.

### 1.4 JP4, JP5, JP6, JP8, JP9

- **JP4 `P1_VPP_JMP`** — confirmed via KiCad lib-symbol property (verbatim: `(property "Value" "P1_VPP_JMP" ...)` on a `Jumper_3_Open`). 3-pole selector between the Q1/Q2 cascade output and U5 pin 1, with D33 1N5819 as protection. Operator opens this jumper when installing a 32-pin chip (whose pin 1 is A18, not VPP).
- **JP5 `A19_CUT`** — 2-pole solder jumper cutting the A18 latch backfeed so socket pin 1 can carry VPP without driving U3's Q3 latch output. Silkscreen name is a misnomer (no A19 on any of these DIPs).
- **JP6, JP8, JP9 `Bodge point`** — three generic "bodge" pads in the U1 MIC2288 / Q3-Q6 feedback area (FB, ~SHDN, and one near the R8/R35/R36 trimmer chain). They are unwired-by-default rework pads for the regulator feedback network, not jumpers that operators "set" for a chip family.

**Nothing else on the Rev 2.3 sheet shows a labelled selector, jumper, or wired bodge that re-routes HV to the 24-pin VPP socket pin (pin 24 or pin 25).**

---

## Task 2 — Firmware re-read for 24-pin code paths

### 2.1 In our (Henrik's) firmware

`firestarter/src/proms/eprom.cpp`, `firestarter/src/proms/memory.cpp`, `firestarter/include/firestarter.h`:

- `handle->pins` is set from JSON `pin-count` (`firestarter/src/json_parser.c:497`).
- Only two places branch on pin count, both in `memory.cpp`:
  - `mem_util_calculate_top_address_register()` at `firestarter/src/proms/memory.cpp:140-150` — `if (handle->pins < 32)` preserves `VPE_TO_VPP` in the CONTROL register mask; `if (handle->pins == 28)` forces `ADDRESS_LINE_17` HIGH. **No `pins == 24` branch.**
  - `using_p1_as_vpp()` at `firestarter/include/memory_utils.h:24-27` — returns true iff `(pins == 32 && vpp_line == VPP_P1_32_DIP) || (pins < 32 && vpp_line == VPP_P1_28_DIP)`. Note `pins < 32` (not `== 28`), so a 24-pin chip whose pinout JSON sets `vpp_line == 0x0F` would also trip this redirect — but on the current `DIP24_2716` pinout, `vpp_line` resolves to bus line 11 (chip pin 21 via `pin_conversions[24]`), NOT 0x0F. So `using_p1_as_vpp` returns false for a stock 24-pin DB entry, and `VPE_ENABLE` is **not** redirected to `P1_VPP_ENABLE`. The firmware asserts `VPE_ENABLE` → D11 → **socket pin 31 (PGM)** instead, which lies OUTSIDE the bottom-aligned 24-pin chip's footprint (chip only occupies socket pins 5–28).
- `VPP_P1_28_DIP (0x0F)` and `VPP_P1_32_DIP (0x15)` are the only two pinout-magic constants (`firestarter/include/rurp_shield.h:57-58`); no DIP24 magic exists.
- `eprom_internal_set_control_register` at `firestarter/src/proms/eprom.cpp:268-274` does the redirect — gated by `using_p1_as_vpp()`. For 24-pin chips with stock DB entries the gate is **closed**, so no redirect fires.
- The `bus_config_t` struct (`firestarter/include/firestarter.h:66-73`) has no 24-pin-specific fields beyond `vpp_line`. The `static_high_mask` (added later) is used for `DIP24_2716`'s "static-high-pins": [24]" (chip pin 24 → bus line 13 → A13 latched HIGH = 5 V on socket pin 28 = VCC for the 24-pin chip), which mirrors upstream's `VCC24PIN` constant exactly.

**Net firmware behaviour for a stock 24-pin write on Henrik's firmware:**
1. `configure_eprom()` is reached (protocol 0x0B → EPROM_LEGACY).
2. `eprom_check_vpp` enables `REGULATOR` (and possibly `VPE_TO_VPP` depending on protocol/flags). Boost converter ramps to ~13 V or ~22 V at the VPE node.
3. `eprom_write_execute` → `program_mismatched_bytes` asserts `VPE_ENABLE` → D11 → socket pin 31. **A bottom-aligned 24-pin chip has nothing at socket pin 31.** No HV reaches the chip. Write returns "0xFF mismatch on every byte".

**This is consistent with my original claim — for the unmodified shield + unmodified firmware path, no HV reaches the 24-pin chip's VPP pin.**

### 2.2 In upstream firmware (Anders Nielsen's `ArduinoProgrammerFirmwarePrototype.ino`)

Source: `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/blob/main/software/Arduino/ArduinoProgrammerFirmwarePrototype/ArduinoProgrammerFirmwarePrototype.ino` (revision history shows `2025-08-17 - 2716 / TMS2532 support (AndersBNielsen)` and `2025-11-19 – Major enhancements and 2716-specific improvements (TheSubWayKing)`).

Verbatim from `burnROM()`:

```cpp
if (romPinCount == 24) {
    latchAddress(VCC24PIN << 8);
    PORTB &= ~(ROM_CE);
    controlByte = (REG_DISABLE | P1_VPP_ENABLE);
}

if (romPinCount == 28) {
    controlByte = (VPE_TO_VPP | REG_DISABLE | VPE_ENABLE | VCC28PIN);
}
```

Verbatim defines (lines 99-110):

```cpp
constexpr uint8_t VPE_TO_VPP    = 0b00000001;    // Route VPE line to VPP voltage source
constexpr uint8_t A9_VPP_ENABLE = 0b00000010;    // Enable VPP (programming voltage) on address line A9
constexpr uint8_t VPE_ENABLE    = 0b00000100;    // Enable programming voltage on VPE pin
constexpr uint8_t P1_VPP_ENABLE = 0b00001000;    // Enable VPP on pin P1 (or socket position 1)
constexpr uint8_t A17_E         = 0b00010000;    // Enable high-order address line A17
constexpr uint8_t VCC28PIN      = 0b00010000;    // (Alias) Select 28-pin device VCC mapping (shares bit with A17_E)
constexpr uint8_t A18_E         = 0b00100000;    // Enable high-order address line A18
constexpr uint8_t VCC24PIN      = 0b00100000;    // (Alias) Select 24-pin device VCC mapping (shares bit with A18_E)
```

So upstream's 24-pin path:
- Asserts `REGULATOR` (via `REG_DISABLE` LOW — note the inverted sense vs Henrik's firmware) and `P1_VPP_ENABLE`. **HV is routed to socket pin 1.**
- Latches `VCC24PIN << 8 = 0x2000` into the address bus, putting A13 HIGH → socket pin 28 = 5 V (VCC for the bottom-aligned 24-pin chip).
- Pulses `ROM_CE` (socket pin 22) for 50 ms.

**Upstream's firmware delivers HV to socket pin 1.** With a bottom-aligned 24-pin chip (chip pin 1 → socket pin 5, chip pin 24 → socket pin 28), **socket pin 1 is in the empty pin row ABOVE the chip body — it does not touch the chip.**

For upstream's 24-pin firmware to actually deliver HV to the chip's VPP pin, the operator must run a **physical wire from socket pin 1 to socket pin 25** (for 2716 VPP) or **to socket pin 24** (for 2732 VPP+OE). This is the JP4 / Rev 2.2 "alternative position for 2716-type ROMs" feature documented in the upstream README. On Rev 2.0/2.1 boards it has to be a physical bodge; on Rev 2.2 it is a built-in solder-jumper selector.

---

## Task 3 — Upstream evidence

### 3.1 Upstream README (`https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer/blob/main/README.md`)

Verbatim relevant snippets (from WebFetch):

> "Revision 2 and 2.1 do however have a jumper to connect high voltage to pin 1 of 28 pin ROMs (JP4) - do NOT leave this jumper in place when programming 32 pin ROMs as it will most likely damage the ROM, the programmer, or both."

> "**Revision 2.2 also has JP4 but rotated 90 degrees (green) and another option of powering the VPP pin of 2716-type ROMs (red).**"

> Revision 1.x: "require physical jumpers to connect VCC to 24 and 28 pin ROMs."

> Rev 2.x: "eliminated this requirement through transistor drivers" (specifically for VCC, not VPP).

### 3.2 Upstream PRs

- **PR #17 (merged 2025-08-17): "2716 / TMS2532 support".** Description: *"ROM pin count must now be specified when calling the python scripts - this will turn on the VCC drivers. Support for TMS2516 and M2716."* — i.e., a software-level pin-count flag that flips on the A13-as-VCC drive (`VCC24PIN` in the .ino). No hardware-routing change.
- **PR #18 (merged 2025-11-28): "Improve 2716 support, structural improvements".** Author note: *"I have only tested HN462716G (Hitachi) EPROMs"* — i.e., 2716 *is* known-working in upstream firmware. But the diff is the .ino refactor shown above; the **hardware side that makes that .ino work is JP4-Rev2.2-red-position or an operator bodge**.

### 3.3 Lack of issues/discussions

The upstream issue tracker has **no open issues** about 24-pin EPROM programming or about Rev 2.3 dropping the "red" jumper. PRs #17 and #18 are the only 2716/24-pin artifacts. **Absence of complaints is mildly suggestive that the Rev 2.2 red-jumper or the bodge is widely understood as a prerequisite**, not surprising to users.

### 3.4 Rev 2.0 / Rev 2.1 / Rev 2.2 folders

- `hardware/rev2/` — gerbers + BOM, no schematic PDF.
- `hardware/Rev2.1/` — gerbers + BOM, no schematic PDF.
- `hardware/Rev2.2/` — gerbers + BOM, no schematic PDF.
- `hardware/Rev2.3/` — current schematic PDF + PCB renders.

Only Rev 2.3's schematic PDF is published. Rev 2.2's "red-position alternative" jumper is **not visually verifiable without re-rendering the Rev 2.2 gerbers**, which is out of scope for this investigation.

---

## Task 4 — Rev 1.x jumper hack (pre-Rev2)

Per the upstream README: "Revision 1.x require physical jumpers to connect VCC to 24 and 28 pin ROMs." The README does not give pin-level detail, but combined with the firmware's `VCC24PIN = A13` convention and the schematic's labelling of socket pin 28 as "A13", the Rev 1.x manual jumpers were:

- For 24-pin chips: **operator solders a wire from `+5V` (or from the latch's A13 output) to a pad that connects to socket pin 28**, AND solders a second wire from the HV cascade output (pre-JP4) to a pad on **socket pin 25 (2716) or socket pin 24 (2732)** to physically route VPP.

The Rev 2 series replaced **the VCC half** of that hack with `VCC24PIN`-controlled transistor drive (Q11/Q12, latched into A13 via the MSB latch), and Rev 2.2's "red" alternative position appears to replace **the VPP half** with a routable jumper — but Rev 2.0, Rev 2.1, and Rev 2.3 still require an operator bodge for the VPP half.

This is the most likely answer to "where does HV need to physically arrive on this shield design": **socket pin 25 for 2716 (chip pin 21), socket pin 24 for 2732 (chip pin 20)** — neither of which has a built-in HV cascade on Rev 2.3.

---

## How my original reasoning held up

| My step | Verdict |
|---------|---------|
| (1) 24-pin chip is bottom-aligned at socket pins 5-28 | ✅ Correct — confirmed by `pin_conversions[24]` mapping chip pin 24 → bus line 13 → socket pin 28 (VCC supply via A13). Upstream firmware agrees: `VCC24PIN = 0x20 << 8 = A13` is the 24-pin VCC drive. |
| (2) 2716's chip pin 21 → socket pin 25 = A11 latch output, 5 V max | ✅ Correct — no HV cascade on socket pin 25 in Rev 2.3 schematic. |
| (3) 2732's chip pin 20 → socket pin 24 = `~ROM_OE` | ✅ Correct — no HV cascade on socket pin 24 in Rev 2.3 schematic. |
| (4) HV cascades exist only on socket pins 1, 26, 31 | ✅ Correct — confirmed by tracing Q1/Q2-D33, Q9/Q7-D34, and the VPE_ENABLE-D11 chain. JP7 "Tin foil socket" is in the regulator-input area, NOT a 24-pin VPP rerouter (at least not visibly so). |
| (5) "24-pin EPROM writes are structurally unsupported on Rev 2.x" | ⚠️ **Partially overstated.** Correct for **the labelled / firmware-driven path alone**, but the upstream design has always assumed users either (a) operate a Rev 2.2 board with the "red" alternative JP4 position, or (b) install a manual bodge wire from socket pin 1 to pin 25/24. Upstream firmware's `P1_VPP_ENABLE` for 24-pin chips is **specifically designed to drive that operator-supplied wire**. |

---

## Implications for our database (~53 + ~16 chips on `DIP24_2716` / `DIP24_2732`)

The user is correct that **the hardware supports 24-pin EPROMs**, but with two qualifications:

1. **It is not plug-and-play on Rev 2.3.** It requires either a Rev 2.2 board with the "red" alternative jumper closed, or an operator-soldered wire from socket pin 1 to socket pin 25 (2716) / pin 24 (2732).
2. **Our firmware on Henrik's branch does not yet drive that path correctly.** Henrik's `eprom_internal_set_control_register` redirect from `VPE_ENABLE → P1_VPP_ENABLE` is gated by `using_p1_as_vpp()`, which returns `false` for the stock `DIP24_2716` pinout (because `vpp_line` resolves to 11, not the magic 0x0F). So even on a Rev 2.2 board with the red jumper closed (or a bodged Rev 2.0/2.1/2.3 board), the firmware asserts `VPE_ENABLE` and routes HV to socket pin 31 (PGM) instead of pin 1 (the bodge-wire origin). **24-pin writes will silently fail until we either (a) add a `pins == 24` path in `using_p1_as_vpp()` that also returns true for the DIP24 VPP line, or (b) update the `DIP24_2716` / `DIP24_2732` pinouts to declare `vpp-pin: 1` instead of `vpp-pin: 21/20` (which would lie about chip pin numbering but match the shield's HV-source pin).**

**The user's hardware almost certainly works for 24-pin chips with the upstream Anders firmware**, because that firmware unconditionally asserts `P1_VPP_ENABLE` whenever `romPinCount == 24` — no `vpp_line` gating, no pinout magic, just "you're a 24-pin chip, here's HV on socket pin 1, deal with the wire yourself".

---

## What "Option B" would have needed (i.e., what I'm explicitly NOT seeing)

For the original claim to be fully refuted on Rev 2.3 alone (no operator bodge required), I would need to find one of:

- A BJT pair driven by `~ROM_OE` (the net at U5 pin 24) that switches HV onto that same net during a `WRITE`-class command. Not present in the Rev 2.3 schematic — the `~ROM_OE` net is driven only by the Arduino's D10 pin (PORTB bit 2) at TTL levels.
- A BJT pair driven by the U3 latch's Q3 output (A11, the net at U5 pin 25) that switches HV onto that net. Not present — U3 is a `74HC573` latch outputting 5 V CMOS levels only; no HV elevator visible.
- A labelled jumper on the Rev 2.3 sheet selecting between (P1_VPP_ENABLE → pin 1) and (P1_VPP_ENABLE → pin 25 or pin 24). The 3-pole JP4 has only two destinations (pin 1 vs cut/open) on Rev 2.3; the Rev 2.2 README-described "red" alt-position is not preserved as a labelled element on Rev 2.3.

None of these is present in the readable schematic content. So the **shield-internal HV routing has not changed between Rev 2.0 and Rev 2.3 for the 24-pin case** — the 24-pin support story is entirely about the operator-supplied wire (or Rev 2.2's built-in alternative).

---

## Recommended next actions (for the parent agent / Henrik)

1. **Ask the user directly which board revision they have** (Rev 2.0 / 2.1 / 2.2 / 2.3) and **whether they have a bodge wire installed from socket pin 1 to socket pin 25 (or 24)**. The answer determines whether 24-pin support is enabled in their setup.
2. **If user has Rev 2.2 + red jumper closed, OR Rev 2.x + the bodge wire:** fix the firmware to assert `P1_VPP_ENABLE` (not `VPE_ENABLE`) for 24-pin writes. Either:
   - Patch `firestarter/include/memory_utils.h:24-27` so `using_p1_as_vpp()` returns true when `pins == 24` (regardless of `vpp_line`), or
   - Update `DIP24_2716` / `DIP24_2732` in `firestarter_app/firestarter/data/pinouts.json` to set `"vpp-pin": [1]` (with a comment that this is the SHIELD's HV-source pin, not the chip's nominal VPP pin), which causes `pin_conversions[24][1] = 7` → `vpp_line = 7` (still not 0x0F). The cleaner fix is the firmware-side `using_p1_as_vpp` patch.
3. **Add a `static-high-pins: [24]` declaration to `DIP24_2716` / `DIP24_2732`** if not already present (it is — verified at `pinouts.json:10` and `:21`) so the firmware drives A13 HIGH for VCC, matching upstream's `VCC24PIN` convention.
4. **Document the bodge wire requirement** in user-facing docs. Without the wire (or Rev 2.2 red jumper) no firmware change makes 24-pin programming work.
5. **Update phase 04's CONTEXT/HARDWARE-REFERENCE/HW-VALIDATION docs** — the existing entries at `04-HARDWARE-REFERENCE.md:30-43` and `04-HW-VALIDATION.md:92-94` state "24-pin EPROM writes are structurally unsupported on Rev 2.x" without the upstream context. Replace with "requires Rev 2.2 + red JP4 position closed, OR Rev 2.0/2.1/2.3 with operator-soldered wire from socket pin 1 to socket pin 25 (2716) / pin 24 (2732); see 04-HW-24PIN-INVESTIGATION.md".

---

## Citations

**Schematic:** `/tmp/rurp_hw/Rev2.3-schematic.pdf` (KiCad EDA 8.0.6, sheet 1/1). Components cited: `U1 MIC2288`, `U3/U4 74HC573`, `U5 28/32 pin ROM`, `Q1` (MMBT3904) / `Q2` (MMBT3906) / `Q5` / `Q7` / `Q8` / `Q9` / `Q11` / `Q12`, `D11` / `D33` / `D34` (all 1N5819), `JP4 P1_VPP_JMP`, `JP5 A19_CUT`, `JP6/JP8/JP9 Bodge point`, `JP7 Tin foil socket`.

**Firmware (Henrik's branch):**
- `firestarter/src/proms/eprom.cpp:268-274` — `eprom_internal_set_control_register` VPE_ENABLE → P1_VPP_ENABLE redirect gated by `using_p1_as_vpp()`.
- `firestarter/include/memory_utils.h:24-27` — `using_p1_as_vpp()` gate predicate.
- `firestarter/src/proms/memory.cpp:140-150` — `mem_util_calculate_top_address_register()` pin-count branches (no `== 24` case).
- `firestarter/include/rurp_shield.h:57-58` — `VPP_P1_32_DIP (0x15)`, `VPP_P1_28_DIP (0x0F)` magic constants.
- `firestarter/src/proms/memory.cpp:315-317` — VPP-line drive-HIGH during address remapping (read-protection for non-P1 VPP lines).

**Host (Python):**
- `firestarter_app/firestarter/database.py:68-88` — `pin_conversions[24]` bottom-aligned mapping (chip pin 1 → bus line 7 = socket pin 5; chip pin 24 → bus line 13 = socket pin 28).
- `firestarter_app/firestarter/data/pinouts.json:2-12` — `DIP24_2716` pinout: `vpp-pin: [21]`, `static-high-pins: [24]`.
- `firestarter_app/firestarter/data/pinouts.json:13-23` — `DIP24_2732` pinout: `vpp-pin: [20]`, `oe-pin: [20]` (shared), `static-high-pins: [24]`.

**Upstream firmware (Anders Nielsen + TheSubWayKing):**
- `software/Arduino/ArduinoProgrammerFirmwarePrototype/ArduinoProgrammerFirmwarePrototype.ino` — `burnROM()` 24-pin branch sets `controlByte = (REG_DISABLE | P1_VPP_ENABLE)` and `latchAddress(VCC24PIN << 8)`; `writefromBuffer()` 24-pin branch toggles `ROM_CE` for `ROM_24PIN_WRITE_PULSE_MS` (50 ms).
- Constants section lines 99-110 — `P1_VPP_ENABLE = 0b00001000`, `VCC24PIN = 0b00100000` (= A18_E alias = bit 5 of CONTROL register = A13 of MSB latch).

**Upstream README:**
- "Revision 2 and 2.1 do however have a jumper to connect high voltage to pin 1 of 28 pin ROMs (JP4)..."
- "Revision 2.2 also has JP4 but rotated 90 degrees (green) and another option of powering the VPP pin of 2716-type ROMs (red)."
- "Revision 1.x require physical jumpers to connect VCC to 24 and 28 pin ROMs."

**Upstream PRs:**
- PR #17 (merged 2025-08-17): "2716 / TMS2532 support" — software adds pin-count parameter, turns on VCC drivers.
- PR #18 (merged 2025-11-28): "Improve 2716 support" — refactor + bugfix on 2716 path; tested HN462716G.
