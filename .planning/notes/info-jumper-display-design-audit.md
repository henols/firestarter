---
title: "info jumper-display design audit"
date: 2026-07-02
context: /gsd-explore session — auditing whether the jumper settings shown by `firestarter info <CHIP>` are correctly designed
---

# `info` jumper-display design audit

Audit of the jumper settings printed by `firestarter info <CHIP>`. Verdict: **not
correctly designed** — the failure runs deeper than a display bug, down to the
chip-database data model.

## Where the code lives

- Display render: [eprom_info.py:286-292](../../firestarter_app/firestarter/eprom_info.py#L286-L292)
- Jumper computation: [ic_layout.py:618-655](../../firestarter_app/firestarter/ic_layout.py#L621-L658)
- Rev 0/1 structure (`_get_rev1_jumper_settings_data`): [ic_layout.py:140-167](../../firestarter_app/firestarter/ic_layout.py#L140-L167)
- Rev 2.x structure (`_get_rev2_jumper_settings_data`): [ic_layout.py:169-184](../../firestarter_app/firestarter/ic_layout.py#L169-L184)
- Dead phantom-JP5 method (`_get_rev2_2_jumper_settings_data`): [ic_layout.py:186-199](../../firestarter_app/firestarter/ic_layout.py#L186-L199)

## What holds up ✅

- The safety heuristic `has_vpp_pin_on_map → jp4 = Closed` keys on the **same
  signal** as the firmware GATE-03 guard. Verified: the WARNING-5 5V-EEPROM
  chips (AT28C256/64, …) now sit on `DIP28_28C64`/`DIP28_28C256`, which have
  **no `vpp-pin`**, so `info` correctly advises JP4=**Open** and never tells the
  user to route 12V onto an address pin. Genuine UV-EPROMs on
  `DIP28_2764`/`27256`/`27512` do carry a vpp-pin → JP4=Closed, correct.

## What's broken ❌

1. **JP4 label bug (confirmed).** `_get_rev2_jumper_settings_data` sets
   `config_text="28pin"`, `pin_text="32pin"` for JP4 — copy-pasted from JP3.
   JP4 is the VPP Open/Closed jumper; those fields are meaningless and render
   `JP4:  ● ●   (28pin, 32pin = Open)`.

2. **Stale revision model.** The display is hard-labeled only `"2.0 & 2.1"`.
   Rev 2.2 and Rev 2.3 owners get no block naming their board. The commented-out
   `_get_rev2_2_jumper_settings_data` invents a phantom **"JP5"** for Rev 2.2 —
   there is no JP5; 2.2/2.3 use the same JP4 header as 2.1.

3. **Structural gap.** `jp4_rev2 ∈ {1,2}` (Open/Closed) is binary. Per operator:
   **Rev 2.2 and 2.3 have a 3-pin angled header**, whose 3rd position supports
   the 2516 family. The code structurally cannot represent that 3rd position.

4. **Data-model gap (root problem).** The 3rd position serves the TI "25xx"
   family (TMS2516 / TMS2532). Datasheet-confirmed distinguishing fact: on Intel
   2716 the program strobe is **pin 18** (CE/PGM), but on **TMS2516/2532 the
   program pulse goes to pin 20 (PD/PGM)** — pin 18 is a static line (A11 on the
   2532). The 3rd jumper most plausibly **routes the write-strobe to pin 20
   instead of pin 18.** This is **not derivable** from any existing chip-database
   field:
   - `pin_count` — all these parts are 24-pin
   - `vpp` — all 25V, shared with Intel M2716 / ST ETC2716
   - `pinout` — 2516 shares `DIP24_2716` with the ordinary 2716 (collision)
   - `algorithm` — all `0x0B`

   → A **new per-chip field** (e.g. "TI-25xx / PGM-on-pin-20") is required.

## Bonus concern 🔶

Because 2516 is modeled identically to a 2716 (`DIP24_2716`) and firmware 0x0B
presumably strobes pin 18, Firestarter may not correctly **program** a 2516/2532
today at all — yet both are marked `support_status: supported`. See the open
research questions. Also: one web source claimed TMS2532 VPP=21V vs the
datasheet's 25V — unverified.

## Datasheet reference (24-pin single-+5V NMOS)

| Pin | Intel 2716 | TMS2516 | Intel 2732/A | TMS2532 |
|-----|-----------|---------|--------------|---------|
| 18 | CE/PGM | **PD/PGM** | CE | **A11** |
| 20 | OE | **CS** (read only) | OE/VPP (shared) | **PD/PGM** |
| 21 | VPP | VPP | A11 | VPP |
| VPP pin | 21 | 21 | 20 (=OE) | 21 |
| Program strobe | pin 18 | pin 18 | pin 20 | pin 20 |

Sources: TMS2516 datasheet (archive.org), Intel M2732A datasheet, PeterVis
TMS2532/2732 comparison.

## Related artifacts

- Todo: `todos/pending/fix-jp4-labels-and-rev2-revision-block.md`
- Seed: `seeds/rev22-3pin-header-2516-family-support.md`
- Research questions appended to `research/questions.md` (2026-07-02)
