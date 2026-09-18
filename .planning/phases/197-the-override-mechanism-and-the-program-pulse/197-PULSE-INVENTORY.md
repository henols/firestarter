# PULSE-01/D-12 — The 100 µs Program-Pulse Inventory

Phase 197, plan 197-07. The evidence behind D-12's closure: every algorithm 7/8 row this phase
did not correct, disposed with a reason, following the `177-READBACK-INVENTORY.md` precedent —
reproducible method first, every row disposed with a verdict, and a named honesty limit.

## Reproducible method

Run against the shipped `firestarter_app/firestarter/data/chip_database.json`, from the
`firestarter_app` repository root:

```python
import json
db = json.load(open('firestarter/data/chip_database.json'))
rows = [(m, r) for m in sorted(db) for r in db[m] if r['programming']['algorithm'] in (7, 8) and r['programming']['pulse_duration_us'] == 100]
total = sum(1 for m in db for r in db[m] if r['programming']['algorithm'] in (7, 8))
print('TOTALS', total, len(rows))
```

Output: `TOTALS 297 215`.

The manufacturer/part-number/size/VPP columns for the non-Fujitsu rows below (and the
per-algorithm split, and the full pulse-width distribution) come from the same traversal with
the manufacturer, part number, `electrical.size_bytes` and `electrical.vpp_mv` fields projected
out and the algorithm split and pulse-duration histogram tallied with a `collections.Counter`
over the same `rows78` list — a plain extension of the query above, not a second source. Both
were run and their output inspected before this file was written.

## Census figures

- **297 algorithm 7/8 rows total** — 170 on algorithm 7, 127 on algorithm 8. Cross-checked
  against `tests/golden/chip_database_field_inventory.json`, which pins `programming` at 746
  (all rows) — this file adds the algorithm-7/8 split, which that golden does not itself assert.
- **Full pulse-width distribution across the 297 rows**, from the `Counter` over
  `pulse_duration_us`:

  | µs | rows |
  |---|---|
  | 10 | 7 |
  | 20 | 1 |
  | 50 | 15 |
  | 100 | **215** |
  | 200 | 28 |
  | 500 | 6 |
  | 1000 | 25 |

  Sum: 7 + 1 + 15 + 215 + 28 + 6 + 25 = 297, matching the total exactly.

- **Pre-phase count at 100 µs: 217.** Measured by running the identical query against
  `git show 70c92ce:firestarter/data/chip_database.json` (the phase's fork point) instead of the
  live file — same 297-row population, same algorithm filter.
- **Post-phase count at 100 µs: 215.** The measured value, from the query above against the
  live, regenerated database.
- **Reconciliation:** 217 − 215 = 2. This phase moved exactly two rows out of the 100 µs bucket
  (`FUJITSU/MBM27C1000P,MBM27C1000` and `FUJITSU/MBM27C1001`, both 100 → 500, per
  `tools/datasheet_overrides.json`) and zero rows into it. The phase's third correction,
  `FUJITSU/MBM27128`, moved 200 → 1000 and never touched the 100 µs bucket either way. 217 − 2 −
  0 = 215, exactly the measured post-phase figure.

**Discrepancy against `CONTEXT.md`:** `CONTEXT.md`'s deferred note states *"The 216 algorithm 7/8
rows still at 100 µs that D-10 does not reach"* — **216, not 215.** The measured post-phase
figure, re-derived independently above and cross-checked against the pre-phase count and the
phase's own three known corrections, is **215**. This inventory records the measured number
(215) and states the discrepancy rather than silently adopting either. The off-by-one is not
explained further here — `CONTEXT.md`'s 216 predates this plan's own re-derivation and this
inventory does not attempt to reconstruct how it was originally produced.

## The twelve Fujitsu algorithm 7/8 rows, each disposed

Fujitsu is the manufacturer this phase's datasheets cover, so its twelve algorithm 7/8 rows get
individual dispositions rather than folding into the per-manufacturer summary below.

| # | Row | Current `pulse_duration_us` | Verdict | Detail |
|---|---|---|---|---|
| 1 | `FUJITSU/MBM27128` | 1000 | **CORRECTED** | 200 → 1000 µs, citing `datasheets/MBM27128.pdf`. Figure 3, the Quick Pro flow chart on page 4-20, specifies `TPW = 1 ms ± 50 µs`; the conventional 50 ms single-shot procedure on page 4-19 is the wrong reading, because the firmware consumes this field as the initial pulse width of a verify-per-pulse loop capped at 25 pulses with `overprogram_factor = 0`, which is the Quick Pro shape and not the conventional single-shot one. `tools/datasheet_overrides.json` entry `FUJITSU/MBM27128`. |
| 2 | `FUJITSU/MBM27256` | 200 (unchanged) | **NO DATASHEET** | No in-repo datasheet covers this part. |
| 3 | `FUJITSU/MBM2764` | 200 (unchanged) | **NO DATASHEET** | No in-repo datasheet covers this part. |
| 4 | `FUJITSU/MBM27C1000P,MBM27C1000` | 500 | **CORRECTED** | 100 → 500 µs, citing `datasheets/MBM27C1000.pdf` (vendored from the gh#70 attachment per D-21). AC CHARACTERISTICS (Single Byte Programming), p.4-68: `tPW` 0.475/0.50/0.525 ms. `tools/datasheet_overrides.json` entry `FUJITSU/MBM27C1000`. |
| 5 | `FUJITSU/MBM27C1001` | 500 | **CORRECTED** | 100 → 500 µs, citing `datasheets/MBM27C1001.pdf`. Page 9-90's AC CHARACTERISTICS table: `tPW` 0.475/0.50/0.525 ms, N 1 to 25, `tOPW` 1.4/1.5/39.4 ms, measured at VCC1 6V ± 0.25V and VPP2 12.5V ± 0.3V. `tools/datasheet_overrides.json` entry `FUJITSU/MBM27C1001`. |
| 6 | `FUJITSU/MBM27C128P` | 100 (unchanged) | **NO DATASHEET** | No in-repo datasheet covers this part. |
| 7 | `FUJITSU/MBM27C2000P,MBM27C2000` | 100 (unchanged) | **NO DATASHEET** | No in-repo datasheet covers this part. |
| 8 | `FUJITSU/MBM27C2001` | 100 (unchanged) | **NO DATASHEET** | No in-repo datasheet covers this part. |
| 9 | `FUJITSU/MBM27C256A` | 100 (unchanged) | **NO DATASHEET** | No in-repo datasheet covers this part. |
| 10 | `FUJITSU/MBM27C4001` | 100 (unchanged) | **DATASHEET-CONFIRMED-CORRECT** | `datasheets/MBM27C4001.pdf`, page 8, AC CHARACTERISTICS: Programming Pulse Width `tPW` min 95, typ **100**, max 105 µs. Front page: *"Fast programming: 0.1ms pulse"*. The decoded 100 µs already matches the datasheet's typical value exactly, in the datasheet's own unit — this is the positive proof behind PULSE-01's finding (see `tools/DECODE-NOTES.md` § 8). **No override entry exists or should exist for this row**: `was == is` (100 == 100) is a no-op, and under D-04/OVR-04 a no-op override entry fails the build. This row belongs here, in the inventory, rather than in `tools/datasheet_overrides.json`. |
| 11 | `FUJITSU/MBM27C512` | 100 (unchanged) | **NO DATASHEET** | No in-repo datasheet covers this part. |
| 12 | `FUJITSU/MBM27C64` | 100 (unchanged) | **NO DATASHEET** | No in-repo datasheet covers this part. |

Eight rows carry **NO DATASHEET** (#2, #3, #6, #7, #8, #9, #11, #12); three carry **CORRECTED**
(#1, #4, #5); one carries **DATASHEET-CONFIRMED-CORRECT** (#10). 8 + 3 + 1 = 12, all twelve
Fujitsu algorithm 7/8 rows.

Of these twelve, seven currently sit at `pulse_duration_us == 100`: the six **NO DATASHEET** rows
still at 100 (#6, #7, #8, #9, #11, #12) plus **DATASHEET-CONFIRMED-CORRECT** `MBM27C4001` (#10).
`MBM27256` and `MBM2764` (#2, #3) carry **NO DATASHEET** too, but sit at 200 µs, not 100, so they
are outside the 215-row 100 µs census above.

## The 100 µs rows outside the Fujitsu block: 208 rows, per-manufacturer

The measured 215-row total at 100 µs includes the 7 Fujitsu rows disposed individually above (6
**NO DATASHEET** + 1 **DATASHEET-CONFIRMED-CORRECT**). Subtracting those 7 from 215 leaves
**208 non-Fujitsu rows**, all carrying the verdict **NO DATASHEET** — no in-repo datasheet covers
any of them, and none has been checked.

Generating command (same population as the reproducible-method query above, with `m != 'FUJITSU'`
added and `electrical.size_bytes` / `electrical.vpp_mv` projected):

```python
import json
db = json.load(open('firestarter/data/chip_database.json'))
rows78 = [(m, r) for m in sorted(db) for r in db[m] if r['programming']['algorithm'] in (7, 8)]
at100 = [(m, r) for m, r in rows78 if r['programming']['pulse_duration_us'] == 100]
non_fujitsu = sorted(
    ((m, r) for m, r in at100 if m != 'FUJITSU'),
    key=lambda x: (x[0], x[1]['part_number']),
)
for m, r in non_fujitsu:
    print(f"{m} | {r['part_number']} | {r['electrical']['size_bytes']} | {r['electrical']['vpp_mv']}")
```

Output: 208 lines. Per-manufacturer counts, descending:

| Manufacturer | Rows |
|---|---|
| ATMEL | 16 |
| NSC | 15 |
| AMD | 14 |
| SGS-THOMSON | 14 |
| MACRONIX(MXIC) | 13 |
| INTEL | 11 |
| ST | 11 |
| FAIRCHILD | 9 |
| CYPRESS | 8 |
| HOLTEK | 8 |
| ISSI | 8 |
| NEC | 8 |
| TI | 8 |
| HITACHI | 7 |
| MICROCHIP memory | 7 |
| WSI | 7 |
| WINBOND | 6 |
| AMIC | 5 |
| ASI Semic | 5 |
| DENSE-PAC | 3 |
| ICE | 3 |
| LINKAGE | 3 |
| OKI | 3 |
| PTC | 3 |
| ANACHIP | 2 |
| EON | 2 |
| ICMIC | 2 |
| ICT | 2 |
| TOSHIBA/KIOXIA | 2 |
| CATALYST(CSI) | 1 |
| HYNIX | 1 |
| HYUNDAI | 1 |

32 manufacturers, 208 rows total (16+15+14+14+13+11+11+9+8+8+8+8+8+7+7+7+6+5+5+3+3+3+3+3+2+2+2+2+2+1+1+1 = 208).

The complete 208-row list — manufacturer, part number, size in bytes, VPP in millivolts — from
the generating command above:

```
AMD | AM27C010 | 131072 | 13000
AMD | AM27C020 | 262144 | 13000
AMD | AM27C040 | 524288 | 13000
AMD | AM27C080 | 1048576 | 13000
AMD | AM27C128 | 16384 | 13000
AMD | AM27C256 | 32768 | 13000
AMD | AM27C512 | 65536 | 13000
AMD | AM27C64 | 8192 | 13000
AMD | AM27H010,AM27HB010 | 131072 | 13000
AMD | AM27H256 | 32768 | 13000
AMD | AM27LV010 | 131072 | 12000
AMD | AM27LV020,AM27LV020B | 262144 | 12000
AMD | AM27LV040 | 524288 | 12000
AMD | AM27LV080 | 1048576 | 12000
AMIC | A27020 | 262144 | 12000
AMIC | A276308 | 65536 | 13000
AMIC | A276308A | 65536 | 13000
AMIC | A278308 | 32768 | 13000
AMIC | A278308A | 32768 | 13000
ANACHIP | 27CX010 | 131072 | 12000
ANACHIP | 27CX256 | 32768 | 12000
ASI Semic | SMJ27C010A | 131072 | 13000
ASI Semic | SMJ27C040 | 524288 | 13000
ASI Semic | SMJ27C128 | 16384 | 13000
ASI Semic | SMJ27C256 | 32768 | 13000
ASI Semic | SMJ27C512 | 65536 | 13000
ATMEL | AT27BV010,AT27LV010,AT27LV010A | 131072 | 12000
ATMEL | AT27BV020,AT27LV020,AT27LV020A | 262144 | 12000
ATMEL | AT27BV040,AT27LV040,AT27LV040A | 524288 | 12000
ATMEL | AT27BV256,AT27LV256A,AT27LV256R | 32768 | 12000
ATMEL | AT27BV512,AT27LV512A,AT27LV512R | 65536 | 12000
ATMEL | AT27C010,AT27C010L | 131072 | 13000
ATMEL | AT27C011 | 131072 | 13000
ATMEL | AT27C020 | 262144 | 13000
ATMEL | AT27C040 | 524288 | 13000
ATMEL | AT27C128 | 16384 | 13000
ATMEL | AT27C256 | 32768 | 12000
ATMEL | AT27C256R | 32768 | 13000
ATMEL | AT27C512 | 65536 | 12000
ATMEL | AT27C512R | 65536 | 13000
ATMEL | AT27HC256,AT27HC256L | 32768 | 12000
ATMEL | AT27HC256R,AT27HC256RL | 32768 | 13000
CATALYST(CSI) | CAT27010 | 131072 | 13000
CYPRESS | CY27C010,CY27H010 | 131072 | 12000
CYPRESS | CY27C020 | 262144 | 12000
CYPRESS | CY27C040 | 524288 | 12000
CYPRESS | CY27C128 | 16384 | 13000
CYPRESS | CY27C256 | 32768 | 12000
CYPRESS | CY27C512 | 65536 | 12000
CYPRESS | CY27H256 | 32768 | 12000
CYPRESS | CY27H512 | 65536 | 12000
DENSE-PAC | DPV27C101 | 131072 | 12000
DENSE-PAC | DPV27C256 | 32768 | 12000
DENSE-PAC | DPV27C512 | 65536 | 12000
EON | EN27C010 | 131072 | 12000
EON | EN27C512 | 65536 | 12000
FAIRCHILD | FM27C010 | 131072 | 12000
FAIRCHILD | FM27C040 | 524288 | 12000
FAIRCHILD | FM27C256,NM27C256,NM27LC256,NMC27C256B,NMC27C256Q,NMC87C257Q,NMC87C257V | 32768 | 13000
FAIRCHILD | FM27C512,NM27C512,NM27LC512,NM27LV512,NM27P512,NMC27C512A,NMC27C512Q | 65536 | 13000
FAIRCHILD | NM27C010,NM27LC010,NM27LV010,NM27P010,NMC27C010 | 131072 | 13000
FAIRCHILD | NM27C020,NM27LV020,NM27P020 | 262144 | 13000
FAIRCHILD | NM27C040,NM27LV040,NM27P040 | 524288 | 13000
FAIRCHILD | NM27C128,NMC27C128B,NMC27C128C | 16384 | 13000
FAIRCHILD | NM27C64Q,NM27LC64,NMC27C64Q | 8192 | 13000
HITACHI | HN27C101AG,HN27C101AP,HN27C101AFP,HN27C101ATT,HN27C101G,HN27C101P | 131072 | 13000
HITACHI | HN27C301AG,HN27C301AP,HN27C301AFP | 131072 | 12500
HITACHI | HN27C301G | 131072 | 12500
HITACHI | HN27C4001G | 524288 | 13000
HITACHI | HN27C512G | 65536 | 13000
HITACHI | HN27C64FP | 8192 | 18000
HITACHI | HN27C64G | 8192 | 18000
HOLTEK | HT27C010 | 131072 | 12000
HOLTEK | HT27C020 | 262144 | 12000
HOLTEK | HT27C040 | 524288 | 12000
HOLTEK | HT27C512 | 65536 | 12000
HOLTEK | HT27LC010 | 131072 | 12000
HOLTEK | HT27LC020 | 262144 | 12000
HOLTEK | HT27LC040 | 524288 | 12000
HOLTEK | HT27LC512 | 65536 | 12000
HYNIX | HY27C64 | 8192 | 13000
HYUNDAI | HY27C64 | 8192 | 13000
ICE | ICE27C010,ICE27LC010 | 131072 | 13000
ICE | ICE27C020,ICE27LC020 | 262144 | 13000
ICE | ICE27C512,ICE27LC512 | 65536 | 13000
ICMIC | 27CX010 | 131072 | 12000
ICMIC | 27CX256 | 32768 | 12000
ICT | 27CX010 | 131072 | 12000
ICT | 27CX256 | 32768 | 12000
INTEL | 27C010,27C010A | 131072 | 12000
INTEL | 27C020 | 262144 | 12000
INTEL | 27C040 | 524288 | 12000
INTEL | 27C128 | 16384 | 12000
INTEL | 27C256 | 32768 | 12000
INTEL | 27C512 | 65536 | 12000
INTEL | 87C257 | 32768 | 13000
INTEL | D27011 | 131072 | 13000
INTEL | D27256,M27256 | 32768 | 12000
INTEL | D27C011 | 131072 | 13000
INTEL | P27256 | 32768 | 12000
ISSI | IS27C010,IS27HC010 | 131072 | 12000
ISSI | IS27C020,IS27HC020 | 262144 | 12000
ISSI | IS27C256,IS27HC256 | 32768 | 12000
ISSI | IS27C512,IS27HC512 | 65536 | 12000
ISSI | IS27LV010 | 131072 | 12000
ISSI | IS27LV020 | 262144 | 12000
ISSI | IS27LV256 | 32768 | 12000
ISSI | IS27LV512 | 65536 | 12000
LINKAGE | LG28C010 | 131072 | 12000
LINKAGE | LG28C020 | 262144 | 12000
LINKAGE | LG28C040 | 524288 | 12000
MACRONIX(MXIC) | MX26C1000 | 131072 | 12000
MACRONIX(MXIC) | MX26C2000 | 262144 | 12000
MACRONIX(MXIC) | MX26C4000 | 524288 | 12000
MACRONIX(MXIC) | MX27C1000 | 131072 | 13000
MACRONIX(MXIC) | MX27C2000 | 262144 | 13000
MACRONIX(MXIC) | MX27C256 | 32768 | 13000
MACRONIX(MXIC) | MX27C4000 | 524288 | 13000
MACRONIX(MXIC) | MX27C512 | 65536 | 13000
MACRONIX(MXIC) | MX27L1000 | 131072 | 13000
MACRONIX(MXIC) | MX27L2000 | 262144 | 13000
MACRONIX(MXIC) | MX27L256 | 32768 | 13000
MACRONIX(MXIC) | MX27L4000 | 524288 | 13000
MACRONIX(MXIC) | MX27L512 | 65536 | 13000
MICROCHIP memory | 27C128 | 16384 | 13000
MICROCHIP memory | 27C256,27LV256 | 32768 | 13000
MICROCHIP memory | 27C512 | 65536 | 13000
MICROCHIP memory | 27C512A | 65536 | 13000
MICROCHIP memory | 27C64,27LV64 | 8192 | 13000
MICROCHIP memory | 27HC256,27HC256L | 32768 | 13000
MICROCHIP memory | 27HC64 | 8192 | 13000
NEC | UPD27128 | 16384 | 12000
NEC | UPD27512 | 65536 | 12000
NEC | UPD27C1001A | 131072 | 12000
NEC | UPD27C128 | 16384 | 12000
NEC | UPD27C2001 | 262144 | 12000
NEC | UPD27C4001 | 524288 | 12000
NEC | UPD27C512 | 65536 | 12000
NEC | UPD27C8001 | 1048576 | 12000
NSC | NM27C010 | 131072 | 13000
NSC | NM27C020 | 262144 | 13000
NSC | NM27C040 | 524288 | 13000
NSC | NM27C128,NMC27C128B,NMC27C128C | 16384 | 13000
NSC | NM27C256,NM27LC256,NMC27C256B,NMC27C256Q,NMC87C257Q,NMC87C257V | 32768 | 13000
NSC | NM27C512,NM27LC512,NM27P512,NMC27C512A,NMC27C512Q | 65536 | 13000
NSC | NM27C64Q,NMC27C64Q | 8192 | 13000
NSC | NM27LC010,NM27P010,NMC27C010 | 131072 | 13000
NSC | NM27LC64 | 8192 | 13000
NSC | NM27LV010 | 131072 | 13000
NSC | NM27LV020 | 262144 | 13000
NSC | NM27LV040 | 524288 | 13000
NSC | NM27LV512 | 65536 | 13000
NSC | NM27P020 | 262144 | 13000
NSC | NM27P040 | 524288 | 13000
OKI | MSM27C1000 | 131072 | 12500
OKI | MSM27C2000 | 262144 | 12500
OKI | MSM27C512 | 65536 | 12000
PTC | PT28C010 | 131072 | 12000
PTC | PT28C020 | 262144 | 12000
PTC | PT28C040 | 524288 | 12000
SGS-THOMSON | M23C1001 | 131072 | 12000
SGS-THOMSON | M23C2001 | 262144 | 12000
SGS-THOMSON | M23C4001 | 524288 | 12000
SGS-THOMSON | M27128A | 16384 | 12000
SGS-THOMSON | M27512 | 65536 | 13000
SGS-THOMSON | M27C1000 | 131072 | 13000
SGS-THOMSON | M27C1001,M27V101 | 131072 | 13000
SGS-THOMSON | M27C2001,M27V201,M27W201 | 262144 | 13000
SGS-THOMSON | M27C256B | 32768 | 13000
SGS-THOMSON | M27C4001,M27V401 | 524288 | 13000
SGS-THOMSON | M27C512,M27V512 | 65536 | 13000
SGS-THOMSON | M87C257 | 32768 | 13000
SGS-THOMSON | M87C257(8D) | 32768 | 13000
SGS-THOMSON | ST27128A | 16384 | 12000
ST | M27128A | 16384 | 12000
ST | M27512 | 65536 | 13000
ST | M27C1001,M27V101,M27W101 | 131072 | 13000
ST | M27C2001,M27V201,M27W201 | 262144 | 13000
ST | M27C256B | 32768 | 13000
ST | M27C256B(2) | 32768 | 13000
ST | M27C4001,M27V401,M27W401 | 524288 | 13000
ST | M27C512,M27V512,M27W512 | 65536 | 13000
ST | M87C257 | 32768 | 13000
ST | M87C257(8D) | 32768 | 13000
ST | ST27128A | 16384 | 12000
TI | SMJ27C128,TMS27C128,TMS27PC128 | 16384 | 13000
TI | SMJ27C256,TMS27C256,TMS27PC256 | 32768 | 13000
TI | SMJ27C512,TMS27C512,TMS27PC512 | 65536 | 13000
TI | TMS27C010A,TMS27PC010A | 131072 | 13000
TI | TMS27C020,TMS27PC020 | 262144 | 13000
TI | TMS27C040,TMS27PC040 | 524288 | 13000
TI | TMS27C64,TMS27PC64 | 8192 | 13000
TI | TMS87C257 | 32768 | 13000
TOSHIBA/KIOXIA | TC57256D | 32768 | 13000
TOSHIBA/KIOXIA | TC57512AD | 65536 | 13000
WINBOND | W27C01,W27C010,W27E01,W27E010,W27L01,W27L010 | 131072 | 12000
WINBOND | W27C02,W27C020,W27E02,W27E020,W27L02 | 262144 | 12000
WINBOND | W27C04,W27C040,W27E040 | 524288 | 12000
WINBOND | W27C257 | 32768 | 12000
WINBOND | W27C512,W27E512 | 65536 | 12000
WINBOND | W27E257 | 32768 | 13500
WSI | WS27C010F | 131072 | 13000
WSI | WS27C010L | 131072 | 13000
WSI | WS27C128F | 16384 | 13000
WSI | WS27C256L | 32768 | 12000
WSI | WS27C512F,WS27C512L | 65536 | 12000
WSI | WS57C128FB | 16384 | 13000
WSI | WS57C256F | 32768 | 12000
```

## Honesty limit

**These 215 rows are inventoried, not audited.** A row's presence in this list — whether in the
twelve-row Fujitsu table's **NO DATASHEET** entries or in the 208-row non-Fujitsu list — is not a
claim that its 100 µs value is wrong. It is a claim that nobody has checked it against that part's
own datasheet. D-02 makes correcting one row cost exactly one datasheet, which is the intended
deterrent against a bulk sweep that would apply one vendor's figure across many parts — precisely
the failure mode the six `UNSOURCED` NMOS entries in `tools/datasheet_overrides.json` already
carry forward from before this phase, and which backlog entry 999.71 (filed by this same plan)
names directly.

Filed to the backlog as entry 999.69 (see `.planning/ROADMAP.md` § Backlog), pointing back at this
file as the inventory of record.

---
*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Measured: 2026-09-18*
