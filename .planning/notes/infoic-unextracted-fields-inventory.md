---
title: "infoic.xml field ledger — all 19 <ic> attributes, what build_db.py reads, and the four unread axes that currently have hand-authored substitutes"
date: 2026-08-22
context: "/gsd-explore: what else is not extracted from infoic.xml — the premise being that everything needed is present without inventing values"
---

# What the generator reads from infoic.xml, and what it does not

Census over the generator's own filter (INFOIC2PLUS, 24–32 pin, no SMD, no serial,
`type ∈ {1,4}`) = **767 `<ic>` elements, 19 attributes each**, every attribute present on
every element. Counts below are over those 767 unless stated.

Companion note on the fifth top-level `<maps>` section — a per-chip physical connectivity
table the generator never opens — is
[`infoic-maps-onerom-three-way-join.md`](infoic-maps-onerom-three-way-join.md). It is the
largest single unread thing in the file and is not repeated here.

## Ledger

| attribute | status in `build_db.py` |
|---|---|
| `name` | read (alias split) |
| `type` | read (`type_int`) |
| `protocol_id` | read |
| `code_memory_size` | read (`mem_size`) |
| `chip_id` | read |
| `pulse_delay` | read (`interpret_timing`) |
| `package_details` | read (pin count / SMD / serial) |
| `variant` | **low byte only** — high byte correctly excluded, it is minipro's T56/T76 `algo_number` (`DECODE-NOTES.md` §2) |
| `flags` | **4 of 12 live bits** |
| `voltages` | **high nibble only** — low nibble masked off |
| `page_size` | **read into `raw_page_size` (`:497`), then withheld for all but 18 rows** |
| `pin_map` | **low byte only** (`:504`) — matches minipro (`database.c:611`); bytes 1 and 3 discarded |
| `chip_info` | **never read** |
| `read_buffer_size` | never read |
| `write_buffer_size` | never read |
| `data_memory_size` | never read — `0x00` on 765/767 |
| `data_memory2_size` | never read — `0x00` on 765/767 |
| `pages_per_block` | never read — `0x0000` on 764/767 |
| `config` | never read — `NULL` on all 767 |

The last four carry no information in scope. `package_details` takes only three values
(`0x18000000`/`0x1c000000`/`0x20000000`), so the SMD and serial filter arms are inert for
in-scope parts — they matter only for the parts they exclude.

---

## The four axes worth acting on

### 1. `page_size` — 86 rows carry a real value the generator drops

`build_db.py:827-835` emits `programming.page_size` from two arms: the datasheet-curated
`_PAGE_SIZE_BY_PART` map (`:131`), else the raw attribute **only when
`_upstream_proto_id == 0x0D`** (18 rows: 15 at 128, 3 at 64 — matching Phase 149's own
research count exactly, which independently validates this census against theirs).

Two findings:

**The curated map is redundant.** Both `[CITED: datasheet]` rows are byte-identical to the
attribute on the same `<ic>` element:

```
WINBOND  W29C020,W29C020C,W29C022   proto=0x05  page_size=0x0080   (curated: 128)
WINBOND  W29C040,W29C042            proto=0x05  page_size=0x0100   (curated: 256)
```

**86 further dispatchable rows carry a nonzero `page_size` that never reaches the database** —
53 at `0x07`, 27 at `0x05`, 6 at `0x0B`. The sharpest instance:

```
proto=0x07  page_size=64  ->  AT28C256, AT28C64B, AT28BV256, CAT28C256, XLE28C256, ... (22 rows)
```

`AT28C256`'s datasheet page size **is** 64 bytes. These are exactly the rows `classify()`
promotes into `0x0D`, and exactly the rows D-04 hands to the firmware's AT28C page-size floor
constant — an invented substitute for a correct value present on the chip's own element.

The Phase 149 provenance argument (a record filed upstream under `0x07` is not evidence about
a 28C page buffer) is coherent as a general rule, but here it discards a datasheet-correct
value in favour of a hardcoded one. Worth re-opening as a decode question with `AT28C256` as
the test case. Related: [[reference_db_algorithm_0x0d_is_66_promoted_rows]].

`page_size == 1` (31 rows) reads as a no-paging sentinel; `> 1` is the meaningful test, which
`build_db.py`'s own PROV-06 comment already uses.

### 2. `chip_info` — upstream's own "VCC is adjustable" flag, on 297 rows

minipro decodes it (`database.c:56-57`, `:676-677`):

```c
#define MP_VOLTAGES1  0x0006
#define MP_VOLTAGES2  0x0007
device->flags.can_adjust_vcc = (device->chip_info == MP_VOLTAGES1);
device->flags.can_adjust_vpp = (device->chip_info == MP_VOLTAGES2);
```

Census: `0x0000` ×390, **`0x0006` ×297**, `0x00e3` ×40, `0x00e4` ×37, `0x008f` ×2,
`0x0098` ×1. No `0x0007` in scope, so nothing claims adjustable VPP.

**297 rows are flagged VCC-adjustable upstream, and the field is unread.** This bears
directly on Phase 148 DATA-01 (`build_db.py:197`, `_VCC_MARGIN_RAIL_MV`), which reasons at
length that minipro's `vcc` for certain parts is the TL866's low-margin *verify* rail rather
than the operating supply, and keys the correction on the decoded value alone because
type-, algorithm- and relation-keyed alternatives all measured worse. Whether the
`chip_info == 0x0006` set coincides with that rule's 56 movers is a single pass and has never
been checked. If it does, the rule has an upstream key instead of a value heuristic.

### 3. `voltages` low nibble — 142 rows, decoded upstream, masked off here

`build_db.py` masks `& 0xF0` for the VPP index. minipro keeps the whole low byte
(`database.c:697` `device->voltages.vpp = voltages & 0xff;`) and decodes the nibble as
powerdown behaviour (`:678-681`):

```c
device->flags.has_power_down        = (voltages & LAST_JEDEC_BIT_IS_POWERDOWN_ENABLE) != 0;
device->flags.is_powerdown_disabled = (voltages & POWERDOWN_MODE_DISABLE) != 0;
```

Census: `0x0` ×625, **`0x1` ×123**, `0x8` ×13, `0xa` ×3, `0x4` ×2, `0xb` ×1.

The `& 0xF0` mask is a deliberate, documented fix (BUG-B — the full byte produced 0 mV
whenever any option bit was set) and should stay as the *VPP* key. The finding is only that
the discarded nibble is not noise: it is a JEDEC-pin/powerdown semantic on 142 parts,
relevant to CE-pin handling on the SRAM/NVRAM families.

### 4. `pin_map` bytes 1 and 3 — the layout-variant discriminator

Byte 2 is always `0x00`. Byte 3 takes three values: `0x00` ×737, `0x90` ×26, `0xd0` ×4.
Byte 1 indexes `<maps>` too but with programmer-side entries (multi-pin `gnd`, e.g.
`gnd = 6,10,12`), so it is not the chip socket map.

The `0xd0` set is exactly `MBM27C1000P`, `HN27C301AG`, `HN27C301G`, `M27C1000` — the group
that makes the 32-pin 128K EPROM class ambiguous between one-rom's `27C010` and the
nonstandard-pinout `27C301`. So byte 3 is a candidate discriminator for precisely the
ambiguity that blocks 45 rows in the three-way join. Decode question, not a datasheet
question. Details: the join note §5.

---

## `flags` — how much is actually left

Bits set anywhere in scope, against minipro's own defines (`database.c:41-52`):

| bit | mask | rows | upstream meaning | read by `build_db.py` |
|---|---|---|---|---|
| 3 | `0x08` | 623 | **undefined upstream** | no |
| 4 | `0x10` | 353 | `MP_ERASE_MASK` → `can_erase` | yes |
| 5 | `0x20` | 465 | `MP_ID_MASK` → `has_chip_id` | yes |
| 6 | `0x40` | 622 | **undefined upstream** | no |
| 7 | `0x80` | 3 | **undefined upstream** | no |
| 9 | `0x200` | 80 | **undefined upstream** | no |
| 11 | `0x800` | 2 | **undefined upstream** | no |
| 14 | `0x4000` | 148 | `MP_OFF_PROTECT_BEFORE` | yes |
| 15 | `0x8000` | 70 | `MP_PROTECT_AFTER` | yes |
| 16 | `0x10000` | 1 | **undefined upstream** | no |
| 19 | `0x80000` | 2 | `MP_CALIBRATION` → `has_calibration` | no |
| 22 | `0x400000` | 28 | **undefined upstream** (outside `MP_SUPPORTED_PROGRAMMING` = bits 20–21, which are zero in scope) | no |

So of the 12 live bits: 4 are read, **1 is decoded upstream and unread** (`MP_CALIBRATION`,
2 rows), and **7 are undecoded by minipro as well**. Extracting those 7 would be extracting
uninterpreted bits — present in the file, but with no sourced meaning, which is the thing to
avoid rather than the gap to close. `MP_DATA_BUS_WIDTH` (word size), `MP_REVERSED_PACKAGE`,
`MP_DATA_MEMORY_ADDRESS`, `MP_LOCK_BIT_WRITE_ONLY` and `MP_SUPPORTED_PROGRAMMING` are all
zero across the whole in-scope set. Prior work on bits 14/15 specifically:
[`infoic-xml-protection-flags-research.md`](infoic-xml-protection-flags-research.md).

---

## Negative result — pin this so nobody chases it

**`write_buffer_size` is not a page size.** It tracks `protocol_id`, not the chip:

```
proto 0x07 / 0x08          ->  write_buffer_size = 128   (272 rows)
proto 0x06 / 0x10 / 0x0E   ->  write_buffer_size = 256
proto 0x0B / 0x27/28/29    ->  write_buffer_size = 32
```

It is the TL866's transfer chunk per algorithm (`database.c:590-591`), and it disagrees with
`page_size` on 674 of 767 rows. `read_buffer_size` is the same kind of field. Neither is a
substitute for the `page_size` work in §1.
