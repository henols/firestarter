# Requirements: Firestarter — v1.42 Jumper Display Correctness & Rev 2.2 3-Pin Header

**Defined:** 2026-09-25
**Milestone:** v1.42 — "Tell the operator the jumper setting the board and the chip actually need"
**Core Value (this milestone):** `firestarter info` prints, for every chip and every shield revision,
the jumper configuration that the hardware actually requires — derived from where the chip's pin map
puts VPP, never from its pin count — and the 24-pin parts that JP4's Rev 2.2 third position exists for
are programmed with the polarity their datasheets specify.

**Scope:** The host jumper display (`firestarter_app/firestarter/ic_layout.py`, `eprom_info.py`), the
host bus-config guard (`database.py`), the generator (`firestarter_app/tools/build_db.py`,
`tools/datasheet_overrides.json`, `tools/extra_chips.json`), the firmware `0x0B` write and read path
for 24-pin VPP-on-pin-21 parts (`firestarter_fw/src/proms/memory.cpp`, `eprom.cpp`), a version bump in
both repositories, bench evidence on the operator's Rev 2.0 and Rev 2.2 shields and TMS2516, and the
`firestarter` wiki. No change to any other protocol's firmware path.

**Provenance:** Backlog 999.58 (the D-09 phase), 999.55 and 999.65; seed
[`rev22-3pin-header-2516-family-support`](seeds/rev22-3pin-header-2516-family-support.md); todos
[`fix-jp4-labels-and-rev2-revision-block`](todos/pending/fix-jp4-labels-and-rev2-revision-block.md) and
[`2026-08-31-jp4-third-position-vpp-destination-pin`](todos/pending/2026-08-31-jp4-third-position-vpp-destination-pin.md);
the Phase 182 ground truth in [`notes/jumper-display-ground-truth.md`](notes/jumper-display-ground-truth.md);
and the activation research in [`research/SUMMARY.md`](research/SUMMARY.md), which **falsified the
seed's premise** — the TMS2516 strobes on pin 18 like the Intel 2716, so no TI database distinguisher is
needed — and found instead that firmware `0x0B` pulses the whole `DIP24_2716` class with inverted
polarity.

## Decisions taken at activation (operator, 2026-09-25)

- **D-1 — Display plus the 2716-class programming fix** (re-scoped after research). The TI distinguisher
  is dropped. Firmware `0x0B` is corrected for every 24-pin part with VPP on pin 21: active-high PGM,
  VPP = VCC in read.
- **D-2 — All revision blocks, split correctly.** No filtering by detected revision, because the shield
  revision cannot be read reliably from the board.
- **D-3 — Info note only** for 24-pin VPP unreachable on Rev 0–2.1. No write gate, no confirm prompt.
- **D-4 — Rev 0/1 corrected from the committed rev1 PDF**, not probed.
- **D-5 — Bench part is a TMS2516.** No TMS2532 is available; the 2532 is covered by the fail-closed
  guard only and is never claimed as working or silicon-proven.
- **D-6 — TMS2516 bench goes to a masked write.** An N≥3 stable read first, then a bit-masked (1→0
  only) write, verified, with the measured VPP disclosed against the part's 24 V minimum. The shield's
  ~22.5 V ceiling makes this best-effort below spec, accepted as the v1.14 Phase 79 25 V NMOS stance.
- **D-7 — All four database/host safety items are in:** TMS2716 off `supported`, the 2532 fail-closed,
  the datasheets vendored, and the 2716-class pulse width set from the datasheet.

## v1 Requirements

### PROBE — shield evidence, measured before code (D-4)

- [ ] **PROBE-01**: An unpowered, empty-socket continuity probe on the operator's Rev 2.0 board records, for each JP4 pad, which of socket pins 1, 3 and 25 it reaches, settling the Rev 2.0/2.1 "Closed" destination that `notes/jumper-display-ground-truth.md` marks PROBE-PENDING
- [ ] **PROBE-02**: A diode test on the operator's Rev 2.2 board records whether D34 blocks the VPE rail from reaching the A11 latch output at socket pin 25
- [ ] **PROBE-03**: On the Rev 2.2 board, with JP4 on the 24-pin (periphery-facing) pole and the socket empty, the VPE voltage at socket pin 25 is measured at pot maximum and recorded against the TMS2516's 24 V programming minimum

### JMP — the `info` jumper block (D-2, D-3, D-4)

- [ ] **JMP-01**: The jumper settings `firestarter info` prints are derived from an explicit per-pin-map table keyed on where the pin map's resolved VPP lands (socket pin 1, socket pin 3, socket pin 25, the OE line, or none) and what socket pin 1 carries; the pin-count and `"vpp-pin" in pin_map` heuristic in `ic_layout.py` is removed
- [ ] **JMP-02**: A test driven by `pinouts.json` fails when any pin map lacks a jumper entry for any revision family, so a new pin map cannot ship with an undefined jumper display
- [ ] **JMP-03**: `firestarter info` prints three revision blocks — Rev 0/1 (JP1–JP3), Rev 2.0/2.1 (two-position JP4) and Rev 2.2/2.3 (three-position JP4: no jumper, 28-pin socket-facing pole, 24-pin periphery-facing pole) — for every chip
- [ ] **JMP-04**: JP4's text is written to its silkscreen rule "Only for ROMs with VPP on P1"; no operator-facing string reproduces "Open for 32 pin ROMs, Closed for 28 pin ROMs", and the `28pin`/`32pin` labels copied from JP3 are gone from JP4
- [ ] **JMP-05**: The known wrong outputs are corrected: the 45 `DIP28_27512` rows and the 8 `DIP32_27C801` rows are no longer told JP3 `28pin`/`32pin` or JP4 `Closed`, and the 158 `DIP32_STD` / `DIP32_27C020` rows are told JP4 `Open` on Rev 2.0/2.1
- [ ] **JMP-06**: For pin maps whose VPP lands on socket pin 25 (`DIP24_2716`), the Rev 2.2/2.3 block names the 24-pin pole, and the Rev 0/1 and Rev 2.0/2.1 blocks state that the VPP pin is unreachable on that revision and programming needs a Rev 2.2 or later shield (Backlog 999.55); `write` behaviour is unchanged
- [ ] **JMP-07**: A "this jumper does not matter" line appears only where the table says so; on Rev 2.2/2.3 a 28- or 32-pin part that needs no JP4 is told "no jumper", never "does not matter", because the 24-pin pole joins socket pin 1 to a live pin on those parts (Backlog 999.56)
- [ ] **JMP-08**: The Rev 0/1 block's JP1, JP2 and JP3 values match `firestarter_fw/document/rurp_schematics_rev1.pdf` for every pin map, with the per-map values recorded in the table's source

### INFO — the rest of `info`'s text (Backlog 999.65)

- [ ] **INFO-01**: `firestarter info` does not present a WP-pin voltage as a programming VPP on the 5V-only rows that `check_dispatch.py`'s WP-pin carve-out already exempts (301 rows measured in v1.37 Phase 183)
- [ ] **INFO-02**: `firestarter info`'s "Can be erased" line agrees with whether `firestarter erase` accepts the chip, instead of being derived from `electrical.type` alone
- [ ] **INFO-03**: The protocol `0x0B` description no longer says every part shares OE and VPP (true only for `DIP24_2732`), and `firestarter_fw/PROTOCOLS.md`'s "via JP4 jumper routing" wording and `firestarter_fw/CLAUDE.md`'s note that project documents disagree about the jumper are corrected to the measured routing

### DBSAFE — database and host safety (D-5, D-7)

- [ ] **DBSAFE-01**: The three-supply `TI/TMS2716` (VBB −5 V on pin 21, VDD +12 V on pin 19) is no longer `support_status: supported`, through `build_db.py` / `datasheet_overrides.json` with a datasheet citation; `chip_database.json` is regenerated, never hand-edited
- [ ] **DBSAFE-02**: The host refuses to build a bus config whose address-bus pins resolve to the `ROM_CE` or `ROM_OE` sentinel, with an operator-facing message, and the `DIP24_2532` row stops being `supported` until a 2532 firmware mode exists
- [ ] **DBSAFE-03**: The TMS2516, TMS2532 and Intel 2716 datasheets are committed to `firestarter_app`, and every datasheet path `tools/extra_chips.json` names for these parts resolves to a committed file
- [ ] **DBSAFE-04**: The program pulse for the `DIP24_2716` class is set through the generator from the datasheet (a 45–55 ms single pulse, or iterative pulses under the firmware's energy cap), with the citation and the reason for the choice recorded

### PGM — firmware `0x0B` for the 2716 class (D-1)

- [ ] **PGM-01**: For 24-pin parts with VPP on pin 21, the firmware holds the PGM line (the shield's CE line, socket pin 22) low while the VPP route is up, changes address and data only while it is low, and pulses it high for the pulse width with OE high
- [ ] **PGM-02**: For the same class, read and verify hold pin 21 at VCC rather than at about 0 V
- [ ] **PGM-03**: Native trace tests record the CE level at every register write while the VPP route is up; they fail on the pre-fix firmware and pass after it for `DIP24_2716`, and prove `DIP24_2732` and every 28- and 32-pin path unchanged
- [ ] **PGM-04**: Every AVR build target stays within its flash and RAM ceiling, and the size delta against the milestone's starting build is recorded

### TMS — the TMS2516 on silicon (D-5, D-6)

- [ ] **TMS-01**: On the Rev 2.2 shield (`firestarter config --rev 4`, JP4 on the 24-pin pole), N≥3 consecutive reads of the operator's TMS2516 return an identical SHA-256
- [ ] **TMS-02**: A bit-masked write to the TMS2516 that only clears bits (1→0) verifies byte-exact, and the VPP measured during it is recorded beside the part's 24 V minimum and disclosed as below specification
- [ ] **TMS-03**: `VALIDATED-EPROMS.md` records the TMS2516 result with its shield revision, board and measured VPP, and makes no claim for the TMS2532

### JWIKI — the wiki (Backlog 999.58)

- [ ] **JWIKI-01**: The `firestarter` wiki carries a jumper table per shield revision covering every pin map, whose values match what `firestarter info` prints, and no wiki text reproduces the two-state JP4 silkscreen clause
- [ ] **JWIKI-02**: The Rev 0 modified, Rev 2 and Rev 2.2 shield photographs are re-exported from the originals at publication resolution and published on the wiki

### JREL — release (D-1)

- [ ] **JREL-01**: Both `firestarter_app` and `firestarter_fw` bump to `3.1.0b2`
- [ ] **JREL-02**: The host refuses a write to a `DIP24_2716`-class part when the attached firmware predates the PGM polarity fix, so a new CLI on old firmware cannot pulse the part inverted

## Future Requirements

Deferred. Tracked but not in this roadmap.

- **TMS2532 firmware mode** — the CE line carries A11 and the OE line is an active-low PGM. Needs a new firmware mode and a wire signal; no bench part is available (D-5).
- **The 13 non-TI `DIP24_2716` rows' VPP values** — only the Intel 2716 and NMC27C16 are datasheet-confirmed; the database's 12–18 V values disagree with the NMC27C16 sheet's 25 V.
- **A gate for the mirrored JP4 hazard** (Backlog 999.56) — needs its own damage-capability trace.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Reading JP4 or JP5 state from the board | Neither jumper is sensed by any shield revision |
| A TI manufacturer-keyed database distinguisher | Research falsified its premise; it would also sweep in the three-supply TMS2716 |
| Hardware change to reach 25 V VPP | Standing stance since v1.14 Phase 79: 25 V NMOS is best-effort, no hardware change |
| Filtering revision blocks by detected revision | The revision byte cannot tell Rev 2.0 from Rev 2.2 (D-2) |
| The 255-row `DIP32_SST39SF040` A18-on-pin-1 remainder | Backlog 999.59, deliberately not gated |
| A write gate for 24-pin parts on Rev 0–2.1 | D-3: note only |

## Traceability

Which phases cover which requirements. Filled by the roadmap.

| Requirement | Phase | Status |
|-------------|-------|--------|

**Coverage:**

- v1 requirements: 29 total
- Mapped to phases: 0
- Unmapped: 29 ⚠️

---
*Requirements defined: 2026-09-25*
*Last updated: 2026-09-25 at milestone activation*
