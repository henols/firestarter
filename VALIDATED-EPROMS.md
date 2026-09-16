# Validated EPROMs

Chips whose community `dev test` sweep passed every applicable step on real hardware.
The `devtest-triage` skill appends a row here when it closes a PASS issue.

Every value in this file is copied from `firestarter_app/firestarter/data/chip_database.json`
or from the closing `dev test` report. Nothing here is estimated.

## 1. Validated chips

| Chip | Vendor | Family | Size | VCC | Chip ID | Host | Firmware | Issues | Validated |
|---|---|---|---|---|---|---|---|---|---|
| AE29F2008 | ASD | F1 | 256 KiB | 5 V | `0xDA45` | 3.0.0b37 | 3.0.0b25 | #61 | 2026-09-10 |
| W29C020 | WINBOND | F1 | 256 KiB | 5 V | `0xDA45` | 3.0.0b33 | 3.0.0b22 | #52 | 2026-08-31 |
| W29C040 | WINBOND | F1 | 512 KiB | 5 V | `0xDA46` | 3.0.0b33 | 3.0.0b22 | #48 | 2026-08-31 |
| SST39SF020 | SST | F2 | 256 KiB | 5 V | `0xBFB6` | 3.0.0b15 | not reported | #25 | 2026-08-08 |
| SST27SF512 | SST | F3 | 64 KiB | 5 V | `0xBFA4` | 3.0.0b33 | 3.0.0b22 | #47 | 2026-08-31 |
| W27C512 | WINBOND | F3 | 64 KiB | 5 V | `0xDA08` | 3.0.0b33 | 3.0.0b22 | #42, #46 | 2026-08-31 |
| W27E020 | WINBOND | F4 | 256 KiB | 5 V | `0xDA85` | 3.0.0b33 | 3.0.0b22 | #51 | 2026-08-31 |
| FM1608 | RAMTRON | F5 | 8 KiB | 3.3 V | none | 3.0.0b33 | 3.0.0b22 | #18, #49 | 2026-08-31 |

Column meanings:

| Column | Source | Notes |
|---|---|---|
| Chip | `part_number`, first entry | Upper case, exactly as the database spells it |
| Family | derived, see §3 | Links to the family table below |
| Size | `electrical.size_bytes` | KiB = 1024 bytes |
| VCC | `electrical.vcc_mv` | Supply rail, not VPP |
| Chip ID | `programming.chip_id_value` | `none` means `chip_id_check` is false — the part reports no identity, so the `id` step is `NA`, not failed |
| Firmware | report `auto_capture.fw_board_identity` | `not reported` means the field was null. The host cannot read a firmware prerelease suffix, so it is never inferred from the host version |
| Issues | closing issue numbers | More than one means the chip passed more than once |

## 2. Part numbers each row covers

A database entry can name several part numbers that share one entry. Validating the
chip in the Chip column validated that entry, so these names are covered by the same row.

| Row | Also covers |
|---|---|
| SST39SF020 | SST39SF020A |
| W27C512 | W27E512 |
| W27E020 | W27C02, W27C020, W27E02, W27L02 |
| W29C020 | W29C020C, W29C022 |
| W29C040 | W29C042 |

AE29F2008 (ASD) and W29C020 (Winbond) are separate database entries whose fields are
**identical on every value** — same algorithm, pinout, VPP, VCC, size, page size, and
the same chip ID `0xDA45` (Winbond manufacturer `0xDA`, device `0x45`). They are the
same silicon sold under two names. Both rows are kept because two distinct physical
parts were tested.

## 3. Families

A **family** is every part in the database that shares all three of
`programming.algorithm`, `pinout` and `electrical.vpp_mv`. Those three decide the
programming procedure, the socket wiring and the programming rail, so a part in the
same family is driven down the same firmware code path as a validated one.

| Family | Algorithm | Pinout | VPP | Parts | Vendors | Validated members |
|---|---|---|---|---|---|---|
| F1 | `0x05` | `DIP32_SST39SF040` | 12 V | 40 | 4 | AE29F2008, W29C020, W29C040 |
| F2 | `0x06` | `DIP32_SST39SF040` | 12 V | 229 | 24 | SST39SF020 |
| F3 | `0x07` | `DIP28_27512` | 12 V | 25 | 14 | SST27SF512, W27C512 |
| F4 | `0x08` | `DIP32_27C020` | 12 V | 63 | 25 | W27E020 |
| F5 | `0x28` | `DIP28_JEDEC_SRAM_8K` | 12 V | 26 | 7 | FM1608 |

The database holds 959 distinct part numbers in 41 families. These five cover 383 of
them. All five happen to sit at 12 V. VPP still belongs in the key, because the database
carries eight distinct programming rails: 9, 12, 12.5, 13, 13.5, 18, 21 and 25 V.

Sections 2, 3 and 4 are **derived** from section 1 and the chip database. Do not edit
their numbers by hand — regenerate them, and compare them against the database:

```bash
S=.claude/skills/devtest-triage/scripts
python3 $S/eprom_families.py           # print the derived tables as markdown
python3 $S/eprom_families.py --check   # exit 1 if any derived row disagrees with the database
```

`--check` reads both this file and `chip_database.json` and compares them, so it fails
when either side moves. Section 1 is the authored half: it records what a bench run
reported, and the script reads the Chip column from it to decide which families matter.

## 4. What a family does and does not tell you

A validated member is **evidence for its untested siblings, never proof**. The family key
fixes the programming path, the wiring and the rail. It does not fix the values that path
reads. This table states exactly how much varies inside each family:

| Family | Size range | Page sizes in family | Untested siblings |
|---|---|---|---|
| F1 | 32–512 KiB (5 distinct) | 64, 128, 256, 512 | 37 |
| F2 | 64–512 KiB (4 distinct) | not used by `0x06` | 228 |
| F3 | 64 KiB only | not used by `0x07` | 23 |
| F4 | 64–256 KiB (3 distinct) | not used by `0x08` | 62 |
| F5 | 8 KiB only | not used by `0x28` | 25 |

Read it this way:

- **F3 and F5 carry no size variation at all.** Every member is the same capacity as the
  validated part, so those two families are the strongest evidence in this file.
- **F1, F2 and F4 vary in size.** A larger sibling drives address lines the validated part
  never drove. On 32-pin parts that is where the JP4 and JP5 straps and the A19-on-pin-1
  maps decide whether the socket is wired correctly at all.
- **F1 additionally varies in page size**, and algorithm `0x05` reads the part's real page
  size when it writes. An F1 sibling with a page size other than the validated 128 or 256
  therefore runs a different write than anything recorded here.
- **Chip ID is always per-part.** No family shares identity bytes. A sibling whose
  `chip_id_check` is true and whose recorded ID is wrong fails at the `id` step regardless
  of how well its family is validated.

A same-family part is a reasonable thing to expect to work and a good candidate to ask a
reporter to try. It is not a chip this project has validated, and must not be described
as one.
