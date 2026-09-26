# Phase 120 — Residual-Risk Watch-List (HOST-04)

**Date:** 2026-07-29
**Status:** Recorded, not acted on. This is a record-keeping artifact, not a code change.

---

## 1. Why this file exists

The derived SDP capability partition's axis is `infoic.xml` flags bit 15 (`0x8000`, `MP_PROTECT_AFTER`).
Bit 15 is **not** a page-write proxy — tested directly, it disagrees with a page size greater than one on
**twelve of the eighty-four** protocol-`0x0D` entries (`120-SDP-PARTITION.md` §4).

Eleven of those twelve have bit 15 clear yet a page size above one. Two of the eleven are the FRAM parts
(`FM28V020`, `MB85R256H`), where bit 15 clear is the correct answer and the page-size figure is a buffer
size rather than an EEPROM page — not a residual risk.

The remaining **nine** are the entries where "no SDP" is least intuitive: an early part with page-write
capability but no software-data-protect flag. These nine are the only place a wrong bit-15 value would
cost a real `write` regression under D-04's auto-set of `FLAG_SKIP_SDP_UNLOCK`. Naming them here means a
future bench report against any of them is recognised immediately rather than re-investigated from scratch.

---

## 2. The watch-list

| # | Manufacturer | `part_number` | `page_size` | Pinout | What a contradicting bench report looks like |
|---|---|---|---|---|---|
| 1 | `AMD` | `AM28C64A,AM28C64AE,AM28C64B,AM28C64BE` | `0x20` | `DIP28_28C64` | User reports `dev sdp <part> enable`/`disable` refused on this part despite believing it has SDP, or a `write` that regressed vs `3.0.0b11` |
| 2 | `ATMEL` | `AT28PC64,AT28PC64E` | `0x20` | `DIP28_28C64` | Same as above |
| 3 | `CATALYST(CSI)` | `CAT28C64A,CAT28C65` | `0x20` | `DIP28_28C64` | Same as above |
| 4 | `EXEL` | `XLE2865A,XLS2865A` | `0x20` | `DIP28_28C64` | Same as above |
| 5 | `EXEL` | `XLE28C16B,XLS28C16B` | `0x10` | `DIP24_2816` | Same as above |
| 6 | `EXEL` | `XLE28C64A,XLS28C64A` | `0x40` | `DIP28_28C64` | Same as above |
| 7 | `NEC` | `UPD28C64` | `0x20` | `DIP28_28C64` | Same as above |
| 8 | `XICOR` | `X2816B,X2816C` | `0x10` | `DIP24_2816` | Same as above |
| 9 | `XICOR` | `X2864AP` | `0x10` | `DIP28_28C64` | Same as above |

All nine currently sit in the **REFUSE** half of the partition (bit 15 clear).

---

## 3. What a bench report against a watch-list entry means, and what it does not

A credible bench report against any of these nine entries is evidence that **this one entry's bit-15
value is wrong for that part** — it is **not** evidence that the axis itself is wrong. The axis passed
three independent ground-truth probes (8/8, 2/2, 4/4 — `120-SDP-PARTITION.md` §2) with no special cases;
a single disagreeing part does not overturn that.

The remedy, if a report is confirmed:

- Move that entry between the two sets in `120-sdp-partition.json` — **the production allow-list
  (`SDP_CAPABLE_TOKENS` in `firestarter/sdp_capability.py`) and the test-side expected partition
  (`EXPECTED_ALLOW_PART_NUMBERS`/`EXPECTED_REFUSE_PART_NUMBERS` in `tests/test_sdp_capability.py`)
  together, in the same change.**
- **Never** widen the allow-list by default in response to a report.
- **Never** relax the unanimity rule (an entry with tokens split across both sets is refused as a whole).

---

## 4. Two findings recorded here and deliberately not acted on

### 4.1 `doc/lockable-proms.md` §17 is wrong about `AT28C16`

`doc/lockable-proms.md` §17 lists "Atmel AT28C16 / 64 / 256" as SDP-capable. This is wrong for two of the
three: `AT28C16` (`AT28C16,AT28HC16,AT28HC16L`), `AT28C16E,AT28C16F`, and plain `AT28C64`
(`AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L`) all carry `infoic.xml` bit 15 **clear**, a
`page_size` of `0x01` (byte-write, no page mode), and are on the REFUSE side of the derived partition.
Only `AT28C256` and `AT28C64B` (the distinct, page-write, software-protect entry) are correctly SDP-capable.

**Correcting `doc/lockable-proms.md` §17 is GATE-02, Phase 121.** This phase records the finding and
changes no doc. The two Atmel entries the split turns on, so the Phase 121 author does not have to
re-derive them:

- `AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L` — flags `0x00000010`, b15=0, `page_size` `0x01`
  (byte-write, no protect) — **REFUSE**.
- `AT28C64B,AT28HC64B,AT28HC64BF` — flags `0x0000c010`, b15=1, `page_size` `0x40` (64-byte page,
  software protect) — **ALLOW**.

### 4.2 RESEARCH F-17's alias-group split question is answered

`120-RESEARCH.md` § F-17 recorded that `chip_database.json` splits alias groups the DB cannot distinguish,
"and we cannot see why." This is now **answered**: `chip_database.json`'s split mirrors `infoic.xml`'s own
split. `AT28C64` (with the `(Non-Standard)` `AT28C64B` alias) carries flags `0x10` — byte-write, no
software protect — while `AT28C64B,AT28HC64B,AT28HC64BF` carries flags `0xc010` — a 64-byte page and
software protect.

Therefore RESEARCH F-02 rule 1's "do not strip parentheticals" is now load-bearing on **correctness**, not
merely on stability. Stripping `(Non-Standard)` collapses that token onto the separate `AT28C64B` entry
and produces a spurious MIXED verdict (`120-SDP-PARTITION.md` §5).

---

## 5. Ceiling, restated

`.planning/REQUIREMENTS.md`'s Validation Ceiling still lists "that the curated capability partition is
correct per family" among the things **not provable** this milestone, and that remains true. This
derivation makes the partition **derived and reproducible**, not **bench-verified**. No AT28C part is on
the bench. The gate proves the partition is total and stable; `infoic.xml` raises confidence in its
contents; neither proves it right on silicon. `0x0D` stays `UNVERIFIED`; zero `support_status` changes;
the 84-chip count is unchanged.
