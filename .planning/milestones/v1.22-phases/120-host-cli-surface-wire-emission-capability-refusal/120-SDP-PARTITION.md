# Phase 120 — SDP Capability Partition, derived from `infoic.xml`

**Date:** 2026-07-29
**Status:** Derived and probe-validated. **Supersedes `120-RESEARCH.md` § F-01's curated 37/47 partition.**
**Operator directive (2026-07-29):** *"there shall be no guessing the ground truth is the infoic.xml"* →
*"You must research the flags in the INFOIC.xml to find the correct configuration."*

---

## 1. Provenance

| Property | Value |
|---|---|
| Source | minipro `infoic.xml` @ `a8efaedc236c1d9718bd28299dfbb99536b010ff` (the commit already pinned by `.planning/notes/infoic-xml-protection-flags-research.md`) |
| Retrieved | `https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaed…/infoic.xml` — 17,861,009 bytes |
| Section | `<database type="INFOIC2PLUS">` — the section `build_db.py:450` already treats as authoritative |
| `<ic>` entries in section | 11,481 |
| **Axis** | `flags` **bit 15** = `0x8000` = `MP_PROTECT_AFTER` (minipro `src/database.c` L39–50; `doc/infoic-field-dictionary.md:121`) |
| Corroborating axis | `page_size` (**not** equivalent — see §4) |
| Keying rule | **Exact token, parentheticals NOT stripped.** Matches `120-RESEARCH.md` § F-02 rule 1. Paren-stripping produces a spurious MIXED verdict — see §5. |
| Coverage | **84 / 84 chips matched. Zero unmatched, zero MIXED.** |
| Derivation script | `120-derive-sdp-allowset.py` (this directory) — re-runnable against the same commit |

**Result: ALLOW 43 / REFUSE 41 = 84.**

---

## 2. Why this axis is trusted — three ground-truth probes, all passing

The axis was not adopted on authority. It was tested against facts established independently of `infoic.xml`,
and it had to reproduce all of them or be rejected.

| Probe | Expectation | Result |
|---|---|---|
| **1.** HOST-04's named pre-SDP class + identical-generation second sources (`2804`, `2816`, `2817`, `X2804A,X2804AI`, `X2816A`, `X2816B,X2816C`, `XL2804A`, `XL2816A,XLE28C16A,XLS28C16A`) | b15 = 0 on all 8 | ✅ **8 / 8**, and 6 of the 8 carry `flags=0x00000000` exactly |
| **2.** The two FRAM parts (`FM28V020`, `MB85R256H`) — a different memory technology with no EEPROM command decoder at all | b15 = 0 on both | ✅ **2 / 2**, both `flags=0x00000000` |
| **3.** The datasheet-of-record Atmel parts (`AT28C256`, `AT28C64B`, `AT28C010`, `AT28C040`) — SDP confirmed in Atmel doc0270 §19 note 2, doc0353 §19, Microchip DS20006432B §6.6.2 | b15 = 1 on all | ✅ **4 / 4** (`0xc010` / `0xc058`) |

**No probe failed and nothing needed a special case.** That is the whole basis for adopting it.

### 2.1 Structural coherence — an independent sanity signal

The partition was derived per-part with no structural rule, yet it lands on clean structure:

| Group | ALLOW | REFUSE |
|---|---|---|
| `DIP24_2816` (19) | 0 | **19 — all of them** |
| `DIP32_28C512_EEPROM` (18) | **18 — all of them** | 0 |
| `DIP28_28C256` (12) | 10 | **2 — exactly the two FRAM parts** |
| `DIP28_28C64` (35) | 15 | 20 |
| `electrical.type == "Flash/EEPROM"` (18) | **18 — all** | 0 |
| `support_status == "adapter-required"` (9) | 0 | **9 — all** |

Two of these were predicted by the discussion and are now *derived* rather than asserted: `DIP24_2816` being
refused wholesale (`120-RESEARCH.md` § F-01 called it "the highest-harm group under F-120-01" and over-refused it
on a judgement call), and the two FRAM parts being the only `DIP28_28C256` refusals — which is HOST-04's own text.

**`120-RESEARCH.md` § F-03 still holds and is not contradicted:** no *structural* rule can express this partition
(`DIP28_28C64` splits 15/20, and `2817` sits on a different pinout from `2804`/`2816`). The table remains an
enumerated token list. What changed is its **provenance**: derived from a per-part datum, not curated by inference.

### 2.2 All 9 `adapter-required` parts are refused by capability

This fully exercises D-08's gate ordering. Its stated purpose — *"an `adapter-required` `0x0D` part with no SDP
hears 'this part has no SDP' rather than 'get an adapter'"* — applies to **all 9** of them, not to a hypothetical
subset. Capability-before-support-status is therefore load-bearing on every adapter-required part in the bucket.

---

## 3. The derived partition


#### ALLOW — 43 entries

| Manufacturer | `part_number` | infoic `flags` | `page_size` | pinout | electrical | support |
|---|---|---|---|---|---|---|
| `ATMEL` | `AT28BV256,AT28LV256` | 0x0000c010 | 0x40 | `DIP28_28C256` | EEPROM | supported |
| `ATMEL` | `AT28BV64B,AT28LV64B` | 0x0000c010 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `ATMEL` | `AT28C010,AT28C010E` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `ATMEL` | `AT28C040,AT28C040E` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `ATMEL` | `AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L` | 0x0000c010 | 0x40 | `DIP28_28C256` | EEPROM | supported |
| `ATMEL` | `AT28C64B,AT28HC64B,AT28HC64BF` | 0x0000c010 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `ATMEL` | `AT28LV010` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `ATMEL` | `AT28MC010` | 0x0000c048 | 0x40 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `ATMEL` | `AT28MC020` | 0x0000c048 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `ATMEL` | `AT28MC040` | 0x0000c048 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `CATALYST(CSI)` | `CAT28C010` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `CATALYST(CSI)` | `CAT28C020` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `CATALYST(CSI)` | `CAT28C040` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `CATALYST(CSI)` | `CAT28C256,CAT28C257` | 0x0000c000 | 0x40 | `DIP28_28C256` | EEPROM | supported |
| `CATALYST(CSI)` | `CAT28C512` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `CATALYST(CSI)` | `CAT28C64B` | 0x0000c000 | 0x20 | `DIP28_28C64` | EEPROM | supported |
| `CATALYST(CSI)` | `CAT28LV256` | 0x0000c000 | 0x40 | `DIP28_28C256` | EEPROM | supported |
| `CATALYST(CSI)` | `CAT28LV64,CAT28LV65` | 0x0000c000 | 0x20 | `DIP28_28C64` | EEPROM | supported |
| `EXEL` | `XLE28C256,XLS28C256` | 0x0000c000 | 0x40 | `DIP28_28C256` | EEPROM | supported |
| `EXEL` | `XLE28C64B,XLS28C64B` | 0x0000c000 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `HITACHI` | `HN58C256AP` | 0x0000c000 | 0x40 | `DIP28_28C256` | EEPROM | supported |
| `MAXWELL` | `28C010,28C010T,28C011,28C011T` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `MICROCHIP memory` | `28C256,28C256F` | 0x0000c010 | 0x40 | `DIP28_28C256` | EEPROM | supported |
| `MICROCHIP memory` | `28C64B` | 0x0000c010 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `NEC` | `UPD28C256` | 0x0000c010 | 0x40 | `DIP28_28C256` | EEPROM | supported |
| `SAMSUNG` | `KM28C64` | 0x0000c000 | 0x20 | `DIP28_28C64` | EEPROM | supported |
| `SAMSUNG` | `KM28C64A,KM28C65A` | 0x0000c000 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `SGS-THOMSON` | `M28010` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `SGS-THOMSON` | `M28C64,M28C64A` | 0x0000c000,0x0000c048 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `SGS-THOMSON` | `M28C64-xxW` | 0x0000c000,0x0000c048 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `ST` | `M28010` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `ST` | `M28256` | 0x0000c010 | 0x40 | `DIP28_28C256` | EEPROM | supported |
| `ST` | `M28C64,M28C64A` | 0x0000c000,0x0000c048 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `ST` | `M28C64-xxW` | 0x0000c000,0x0000c048 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `ST` | `M28LV64` | 0x0000c000 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `WED` | `WE128K8` | 0x0000c058 | 0x40 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `WED` | `WE256K8` | 0x0000c058 | 0x40 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `WED` | `WE512K8` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `WED` | `WME128K8` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `XICOR` | `X28256,X28C256` | 0x0000c000 | 0x40 | `DIP28_28C256` | EEPROM | supported |
| `XICOR` | `X28C010` | 0x0000c058 | 0x80 | `DIP32_28C512_EEPROM` | Flash/EEPROM | supported |
| `XICOR` | `X28C64(NonStandard),X28HC64(NonStandard)` | 0x0000c010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `XICOR` | `X28C64,X28HC64` | 0x0000c010 | 0x40 | `DIP28_28C64` | EEPROM | supported |

#### REFUSE — 41 entries

| Manufacturer | `part_number` | infoic `flags` | `page_size` | pinout | electrical | support |
|---|---|---|---|---|---|---|
| `AMD` | `AM28C16A` | 0x00000000 | 0x01 | `DIP24_2816` | EEPROM | supported |
| `AMD` | `AM28C17A` | 0x00000000 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `AMD` | `AM28C64A,AM28C64AE,AM28C64B,AM28C64BE` | 0x00000000 | 0x20 | `DIP28_28C64` | EEPROM | supported |
| `ATMEL` | `AT28BV64,AT28LV64` | 0x00000010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `ATMEL` | `AT28C04,AT28HC04` | 0x00000010 | 0x01 | `DIP24_2816` | EEPROM | adapter-required |
| `ATMEL` | `AT28C04E,AT28C04F` | 0x00000010 | 0x01 | `DIP24_2816` | EEPROM | adapter-required |
| `ATMEL` | `AT28C16,AT28HC16,AT28HC16L` | 0x00000010 | 0x01 | `DIP24_2816` | EEPROM | adapter-required |
| `ATMEL` | `AT28C16E,AT28C16F` | 0x00000010 | 0x01 | `DIP24_2816` | EEPROM | adapter-required |
| `ATMEL` | `AT28C17` | 0x00000010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `ATMEL` | `AT28C17E,AT28C17F` | 0x00000010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `ATMEL` | `AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L` | 0x00000010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `ATMEL` | `AT28C64E,AT28C64F` | 0x00000010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `ATMEL` | `AT28PC64,AT28PC64E` | 0x00000010 | 0x20 | `DIP28_28C64` | EEPROM | supported |
| `CATALYST(CSI)` | `CAT28C16A,CAT28C16AI` | 0x00000000 | 0x01 | `DIP24_2816` | EEPROM | supported |
| `CATALYST(CSI)` | `CAT28C17A` | 0x00000000 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `CATALYST(CSI)` | `CAT28C64A,CAT28C65` | 0x00000000 | 0x20 | `DIP28_28C64` | EEPROM | supported |
| `CYPRESS` | `FM28V020` | 0x00000000 | 0x80 | `DIP28_28C256` | EEPROM | supported |
| `EXEL` | `XL2804A` | 0x00000000 | 0x01 | `DIP24_2816` | EEPROM | supported |
| `EXEL` | `XL2816A,XLE28C16A,XLS28C16A` | 0x00000000 | 0x01 | `DIP24_2816` | EEPROM | supported |
| `EXEL` | `XLE2865A,XLS2865A` | 0x00000010 | 0x20 | `DIP28_28C64` | EEPROM | supported |
| `EXEL` | `XLE28C16B,XLS28C16B` | 0x00000000 | 0x10 | `DIP24_2816` | EEPROM | supported |
| `EXEL` | `XLE28C64A,XLS28C64A` | 0x00000000 | 0x40 | `DIP28_28C64` | EEPROM | supported |
| `FUJITSU` | `MB85R256H` | 0x00000000 | 0x100 | `DIP28_28C256` | EEPROM | supported |
| `MICROCHIP memory` | `2804` | 0x00000000 | 0x01 | `DIP24_2816` | EEPROM | supported |
| `MICROCHIP memory` | `2816` | 0x00000000 | 0x01 | `DIP24_2816` | EEPROM | supported |
| `MICROCHIP memory` | `2817` | 0x00000000 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `MICROCHIP memory` | `28C04A` | 0x00000010 | 0x01 | `DIP24_2816` | EEPROM | adapter-required |
| `MICROCHIP memory` | `28C04AF` | 0x00000010 | 0x01 | `DIP24_2816` | EEPROM | adapter-required |
| `MICROCHIP memory` | `28C16A` | 0x00000010 | 0x01 | `DIP24_2816` | EEPROM | adapter-required |
| `MICROCHIP memory` | `28C16AF` | 0x00000010 | 0x01 | `DIP24_2816` | EEPROM | adapter-required |
| `MICROCHIP memory` | `28C17A` | 0x00000010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `MICROCHIP memory` | `28C17AF` | 0x00000010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `MICROCHIP memory` | `28C64A` | 0x00000010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `MICROCHIP memory` | `28C64AF` | 0x00000010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `MICROCHIP memory` | `28LV64A` | 0x00000010 | 0x01 | `DIP28_28C64` | EEPROM | supported |
| `NEC` | `UPD28C04` | 0x00000010 | 0x01 | `DIP24_2816` | EEPROM | adapter-required |
| `NEC` | `UPD28C64` | 0x00000010 | 0x20 | `DIP28_28C64` | EEPROM | supported |
| `XICOR` | `X2804A,X2804AI` | 0x00000000 | 0x01 | `DIP24_2816` | EEPROM | supported |
| `XICOR` | `X2816A` | 0x00000000 | 0x01 | `DIP24_2816` | EEPROM | supported |
| `XICOR` | `X2816B,X2816C` | 0x00000000 | 0x10 | `DIP24_2816` | EEPROM | supported |
| `XICOR` | `X2864AP` | 0x00000000 | 0x10 | `DIP28_28C64` | EEPROM | supported |

---

## 4. `page_size` is a corroborating axis, NOT an equivalent one

`.planning/notes/infoic-xml-protection-flags-research.md` hedged bit 15 as *"≈ SDP page-write family marker"*.
Tested directly: **b15 and `page_size > 1` disagree on 12 of the 84.** So b15 is **not** a page-write proxy —
it carries information `page_size` does not, which is what makes it usable as its own signal.

| Direction | n | Entries |
|---|---|---|
| b15=0 but `page_size > 1` — has page mode, no protect flag | 11 | `AMD/AM28C64A,…` (0x20) · `ATMEL/AT28PC64,AT28PC64E` (0x20) · `CATALYST(CSI)/CAT28C64A,CAT28C65` (0x20) · `EXEL/XLE2865A,XLS2865A` (0x20) · `EXEL/XLE28C16B,XLS28C16B` (0x10) · `EXEL/XLE28C64A,XLS28C64A` (0x40) · `NEC/UPD28C64` (0x20) · `XICOR/X2816B,X2816C` (0x10) · `XICOR/X2864AP` (0x10) · **`CYPRESS/FM28V020` (0x80)** · **`FUJITSU/MB85R256H` (0x100)** |
| b15=1 but `page_size == 1` | 1 | `XICOR/X28C64(NonStandard),X28HC64(NonStandard)` |

The two FRAM entries in that first row are a useful check on both axes: FRAM has no page-write in the EEPROM
sense — the figure is a buffer size — and b15=0 is the correct answer for them, which `page_size` alone would
have got wrong.

### Residual-risk watch-list (9 entries)

The nine non-FRAM entries in the first row are where "no SDP" is least intuitive: an early part with page-write
but no software protect. They are the entries where a wrong b15 would cost a real `write` regression under D-04.
**Name them in the plan as a watch-list**, so a future bench report against any of them is recognised
immediately rather than re-investigated from scratch.

---

## 5. The one MIXED verdict, and what resolving it explained

A first pass with paren-stripped keys produced one MIXED entry:
`ATMEL/AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L` → both `0x10` and `0xc010`.

Cause: stripping `(Non-Standard)` collapses that token onto the **separate** `AT28C64B` entry. With exact-token
keying the ambiguity disappears:

| infoic entry | `flags` | b15 | `page_size` |
|---|---|---|---|
| `AT28C64, AT28C64B(Non-Standard), AT28HC64, AT28HC64L` | `0x00000010` | **0** | `0x01` — byte write |
| `AT28C64B, AT28HC64B, AT28HC64BF` | `0x0000c010` | **1** | `0x40` — 64-byte page |

**This answers `120-RESEARCH.md` § F-17**, which recorded that the DB splits alias groups "and we cannot see why."
The reason is now visible: `chip_database.json`'s split mirrors `infoic.xml`'s own split, and the distinction is
page-write + software protect (`AT28C64B` proper) versus byte-write with neither (plain `AT28C64` and the
`(Non-Standard)` variant). F-02 rule 1's "do not strip parentheticals" was already the right call for a
different reason; it is now also load-bearing on correctness.

---

## 6. What this supersedes, and what it does not

**Superseded:**
- `120-RESEARCH.md` § F-01's curated **37 / 47** partition and all five of its named judgement calls. Scored
  against the derived answer: judgement calls **1** (`X2864AP` refuse) and **2** (Atmel `DIP24_2816` refuse,
  its A6 "highest-value item for operator review") were **right**; **3** (`AT28C17`/`28C17A`/`CAT28C17A` allow)
  and **5** (ST/SGS-THOMSON `M28C64` refuse) were **wrong**; **4** (Catalyst 1M/2M/4M allow) was **right**.
  Its assumptions **A5** and **A6** are confirmed; **A4** and **A7** are refuted in both directions.
- The operator's interim "allow both disputed groups" membership (2026-07-29). It was chosen *because* the
  alternative was guessing; the directive that accompanied it — no guessing, use `infoic.xml` — is what this
  artifact executes, and it is the reason the interim pick no longer applies.
- **`doc/lockable-proms.md` §17 is wrong about `AT28C16`.** It lists "Atmel AT28C16 / 64 / 256" as SDP-capable;
  `AT28C16`, `AT28C16E,F` and plain `AT28C64` are all b15=0. Correcting that doc is **GATE-02, Phase 121** —
  this phase records the finding and changes no doc.

**NOT superseded — the old note's verdict stands, correctly scoped:**
`.planning/notes/infoic-xml-protection-flags-research.md` concluded b14/b15 are "too coarse to derive lock-status
metadata" and told us not to re-investigate. That verdict was about the **`protection_kind` / `status_readable` /
`unlockability` taxonomy**, and it remains true: `W29C020C` (permanent boot-block lockout) and `W29EE011`
(SDP-only) are still flag-identical, so **readability is still not derivable**. Neither of those parts is in the
`0x0D` bucket. The question answered here is strictly narrower — *does this 28C-family part have an SDP command
decoder* — and on that question the axis reproduces every known fact. **Both findings are correct; they answer
different questions.** Update the note with this scoped exception rather than treating either as overturned.

**Unchanged scope fences.** Zero `chip_database.json` change. Zero `build_db.py` change. Zero firmware change.
No `support_status` change. The 84-chip count is unchanged. `0x0D` stays `UNVERIFIED`. `infoic.xml` is **not**
added to either sub-repo — it stays an external input, exactly as `build_db.py` already treats it.

---

## 7. How the partition ships (mechanism, unchanged from D-01/D-02)

D-01's **fail-closed allow-list** mechanism is untouched, and this is the part that matters most:

- The shipped artifact is still a **static token table in `firestarter/sdp_capability.py`** plus the D-02
  runtime exhaustiveness gate. Nothing reads `infoic.xml` at runtime, or in CI.
- **Anything not on the allow-list is still refused** — including a `0x0D` part a user adds to
  `~/.firestarter/database.json` (merged live at `database.py:187-199`, invisible to CI). That property is
  what D-01 was written for and it is fully preserved.
- What changed is only **how the table's contents were determined**: a per-part datum from `infoic.xml` b15
  instead of family-level inference. Record the provenance in the module docstring — the minipro commit, the
  section, the bit, and a pointer to this artifact — so a future reader can re-derive rather than re-guess.
- **The refusal cost argument changes shape, in our favour.** `120-RESEARCH.md` § F-01 warned that over-refusal
  costs a working `write` on a genuinely-locked part (D-04 auto-sets `FLAG_SKIP_SDP_UNLOCK` for refused parts).
  That cost only exists for a part that *has* SDP. For a part with no SDP there is nothing to unlock, so
  suppressing its auto-unlock is a no-op for it and additionally avoids F-120-01's three stored bytes at the
  truncated magic addresses. **On the derived partition, refusal has no cost for the parts it refuses** — the
  trade-off the operator was asked to weigh is dissolved, not decided. The residual risk is confined to §4's
  9-entry watch-list.
- **Expected future supersession, restated honestly:** decoding b14/b15 into the DB proper
  (`.planning/todos/pending/decode-infoic-flags-bits-14-15-protect-metadata.md`) would make this table
  generated rather than transcribed. It would *narrow* the curation, not remove the need for a partition.

---

## 8. Validation consequences

`120-VALIDATION.md`'s HOST-04 rows change count only — **74/10 and 37/47 both become 43/41**. Every oracle
already written stays valid, and two gain reach:

- The exhaustiveness gate (`allow ∪ refuse == the 84 algorithm==13 entries`) pins **43/41**.
- The named-refusals test can now assert all 19 `DIP24_2816` parts and both FRAM parts refuse, not just the
  8 HOST-04 names.
- The adapter-required leg becomes exhaustive: **all 9** adapter-required parts must hear the capability reason.
- **New leg worth adding:** assert the allow-set contains **no** `adapter-required` part and **no** part on
  `DIP24_2816` — two structural invariants the derived partition happens to satisfy, which would catch a
  hand-edit that widens the table carelessly.

**The ceiling is unchanged.** `REQUIREMENTS.md` § "Validation Ceiling" still lists "that the curated capability
partition is correct per family" among the things not provable this milestone, and that is still true: this
artifact makes the partition *derived and reproducible*, not *bench-verified*. No AT28C part is on the bench.
The gate proves the partition is total and stable; `infoic.xml` raises confidence in its contents; neither
proves it right on silicon.
