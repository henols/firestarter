# infoic.xml field audit

Work item #11. This document checks each `infoic.xml` attribute and `flags` bit against (a) the
minipro source and (b) the datasheets of the chips in `firestarter_app/datasheets/`. It also says how
Firestarter uses each one.

## Scope and method

- **Catalog:** minipro `infoic.xml` at commit `a8efaedc236c1d9718bd28299dfbb99536b010ff`, the pin
  used by `firestarter_app/tools/build_db.py`. Section `INFOIC2PLUS`, 938 rows with 24 to 32 pins.
- **Datasheets:** the 17 PDFs vendored in `firestarter_app/datasheets/`. Text was extracted with
  `pypdf`. Eight PDFs are image scans with no text layer (`AT28C256`, `HN482764`, `M27C1001`,
  `MBM27128`, `MBM27C1000`, `MBM27C4001`, `TMM27128AD`, `TMS2764`). Nothing was read from them in
  this audit. Their values are checked in `tools/datasheet_overrides.json` and
  `tools/DECODE-NOTES.md` instead.
- **Not done:** no datasheets were downloaded for the other ~650 DIP-parallel parts. The scope was
  agreed as a field-level audit with spot checks, not a per-chip audit. The attributes that a
  datasheet cannot answer (`variant` high byte, `pin_map`, `chip_info`, `protocol_id`) are checked
  against minipro source in `tools/DECODE-NOTES.md` §1 to §2 and §11.
- The per-field decode rules are in `firestarter_app/tools/DECODE-NOTES.md`. This document does not
  repeat them. It records what was re-verified.

## 1. Flag census (re-run)

The census of set `flags` bits over the 938 rows was recomputed from the pinned file. It matches the
counts in DECODE-NOTES §13.1 for every named bit:

| Bit | Rows | minipro name |
|---|---|---|
| `0x10` | 492 | `MP_ERASE_MASK` |
| `0x20` | 566 | `MP_ID_MASK` |
| `0x2000` | 93 | `MP_DATA_BUS_WIDTH` |
| `0x4000` | 149 | `MP_OFF_PROTECT_BEFORE` |
| `0x8000` | 71 | `MP_PROTECT_AFTER` |
| `0x40000` | 14 | `MP_LOCK_BIT_WRITE_ONLY` |
| `0x80000` | 17 | `MP_CALIBRATION` |
| `0x100000` | 118 | `prog_support` = 1 |

Unnamed bits in this set: `0x8` (674), `0x40` (673), `0x80` (3), `0x100` (126), `0x200` (224),
`0x400` (32), `0x800` (2), `0x10000` (1), `0x400000` (28), `0x1000000` (75), `0x2000000` (14). Notes
§13.1 lists some of these. `0x80`, `0x800` and `0x10000` are set on rows in this set and the notes
do not list them. They have no name in minipro. Firestarter does not read them.

## 2. Datasheet cross-checks

`=` means the datasheet agrees with the XML value. All XML values are from the pinned file.

| Chip (datasheet) | Field | XML | Datasheet | Result |
|---|---|---|---|---|
| W27E257 | `chip_id` | `0xda02` | manufacturer DA, device 02 | = |
| W27E257 | `flags` & 0x10 (erase), 0x20 (ID) | set, set (`0x78`) | electrical chip erase, ID mode | = |
| W27E257 | `pulse_delay` | 0x64 = 100 | TPWP 95 / 100 / 105 µs | = (µs, typical) |
| W27E257 | `voltages` VPP byte `0x80` | 13.5 V rail | program 12 V, erase 14 V | A rail index, not a chip requirement. See DECODE-NOTES §9 |
| W27C512 | `chip_id` | `0xda08` | DA, 08 | = |
| W27C512 | `pulse_delay` | 100 | TPWP 100 µs | = |
| W27C512 | `flags` 0x10 | set | electrical erase | = |
| W27C020 | ID bytes | not in the DIP rows searched | DA, 85 | Not compared |
| M27C512 | `chip_id` | `0x203d` | manufacturer 20h, device 3Dh | = |
| M27C512 | `flags` 0x10 | clear (`0x68`) | UV erase | = |
| M27C512 | `pulse_delay` | 100 | 100 µs pulse in the fast algorithm | = |
| MX27C4000 | `pulse_delay` | 100 | 100 µs pulse, up to 25 pulses | = |
| MX27C4000 | `chip_id` | `0xc240` | manufacturer C2H | Manufacturer byte = |
| MX27C4000 | `flags` 0x10 | clear | UV erase | = |
| MX27C4000A | `pulse_delay` | 10 | no datasheet vendored | Open: not verified |
| SST39SF040 | `chip_id` | `0xbfb7` | manufacturer BF, device B7 | = |
| SST39SF040 | `flags` | `0x78` (erase + ID) | Flash, sector and chip erase, ID mode | = |
| SST39SF040 | `flags` 0x4000 / 0x8000 | clear | fixed SDP sequence 5555/2AAA | = (the command sequence is part of protocol `0x06`) |
| MBM27C1001 | `chip_id` | `0x04e5` | Fujitsu signature table | ID row not machine-readable in the OCR text. Not verified |
| MBM27C1001 | `pulse_delay` | 100 | Quick Pro, 500 µs (notes §8) | Known upstream family default. Overridden in `datasheet_overrides.json` |
| UPD27128 | `chip_id` | `0` | no ID mode | = (`flags` has no 0x20) |
| UPD27128 | `pulse_delay` | 100 | high speed 1 ms | Known upstream default. Overridden in `datasheet_overrides.json` |
| AT28C256 | `page_size` | `0x40` | 64-byte page (scan, not read here) | Not machine-checked |
| AT28C256 | `flags` | `0xc010` | SDP on and off | Not machine-checked. Consistent with the 28C family |

No new mismatch was found beyond what `tools/datasheet_overrides.json` already records.

## 3. How Firestarter uses each attribute

| Attribute | Use in `build_db.py` | Verified by |
|---|---|---|
| `type` | Memory class. Only 1 (EEPROM) and 4 (SRAM) are emitted | Notes §2.3 |
| `protocol_id` | Algorithm family and `KNOWN_PROTOCOLS` gate | Notes §2, §4 |
| `variant` low byte | Pinout family inside a `pm_idx` cluster | Notes §1 |
| `variant` high byte | Not used. It is the T56/T76 algorithm-file suffix | Notes §2 |
| `code_memory_size` | `mem_size`. Chip size | Datasheets: sizes agree for every chip above |
| `page_size` | `programming.page_size`, when the provenance allows | Notes §13.2 |
| `read_buffer_size`, `write_buffer_size` | Not used (USB block size) | Notes §13.2 |
| `chip_id` | `chip_id_value` | Section 2 above |
| `voltages` | VPP and VCC rail index | Notes §9 |
| `pulse_delay` | `pulse_duration_us`, in µs | Notes §8, section 2 above |
| `flags` | 0x10 classification, 0x20 `chip_id_check`, 0x4000 `protect_off_before`, 0x8000 `protect_on_after` | Section 1 above |
| `chip_info` | Not used | Notes §13.4 |
| `pin_map` | Pin map and `pm_idx` | Notes §1, §11 |
| `data_memory*_size`, `pages_per_block`, `config`, `blank_value` | Not used for the chips supported | Notes §13.2, §13.3 |

## 4. Follow-ups

- Add MX27C4000A, W27C020 and other part-specific datasheets, so rows other than the 17 can be
  checked. Table `tools/datasheet_overrides.json` shows the format.
- OCR or re-source the eight scanned PDFs, so the `chip_id`, `page_size` and `flags` of
  AT28C256 and MBM27C1001 can be machine-checked.
- Decide whether to document flag bits `0x80`, `0x800` and `0x10000` in DECODE-NOTES §13.1. The
  change belongs in `firestarter_app`.

## Generator inclusion check (addendum)

Checked `firestarter/data/chip_database.json` from firestarter_app (749 rows)
against the gates in `tools/build_db.py`.

- Status counts: 618 supported, 125 protocol-not-implemented, 6 adapter-required.
- Every supported row has a pin map with enough address lines for its size
  (0 short rows), and a pin count of 24, 28 or 32.
- Supported rows have VPP of 12.0, 12.5, 13.0, 18, 21 or 25 V. The ceiling
  gate is 25 V (`RURP_VPP_CEILING_MV`), taken from a code comment, not from a
  datasheet.
- The gates cover pin map, address reach, VPP ceiling and the 0x10 pin-1 clash.
  They do not check the datasheet for each part.

Open risk, not verified against a datasheet (none is vendored):
upstream merges `2732`, `2732A`, `M2732` and `M2732A` into one record, and the
generator gives that row 25 V VPP. The 2732A is normally a 21 V part. A 25 V
pulse could exceed its absolute maximum. The generator also cannot tell
merged aliases apart. Check the other merged-alias rows with a 25 V or 21 V
VPP (2716, 2516, M2732A) the same way.
