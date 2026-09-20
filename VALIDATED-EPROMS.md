# Validated EPROMs

## Validated chips

| Chip | Vendor | Family | Size | VCC | Chip ID | Host | Firmware | Issues | Validated |
|---|---|---|---|---|---|---|---|---|---|
| SST27SF512 | SST | PROTO_EPROM_28PIN/DIP28_27512/12V | 64 KiB | 5 V | `0xBFA4` | 3.0.0b33 | 3.0.0b22 | #47 | 2026-08-31 |
| W27C512 | WINBOND | PROTO_EPROM_28PIN/DIP28_27512/12V | 64 KiB | 5 V | `0xDA08` | 3.0.0b33 | 3.0.0b22 | #42, #46 | 2026-08-31 |
| TMS27C512 | TI | PROTO_EPROM_28PIN/DIP28_27512/13V | 64 KiB | 5 V | `0x9785` | 3.0.0b39 | 3.0.0b27 | #72 | 2026-09-12 |
| W27E020 | WINBOND | PROTO_EPROM_32PIN/DIP32_27C020/12V | 256 KiB | 5 V | `0xDA85` | 3.0.0b33 | 3.0.0b22 | #51 | 2026-08-31 |
| W27C040 | WINBOND | PROTO_EPROM_32PIN/DIP32_STD/12V | 512 KiB | 5 V | `0xDA86` | 3.0.0b44 | 3.0.0b31 | #87 | 2026-09-16 |
| MX27C4000 | MACRONIX(MXIC) | PROTO_EPROM_32PIN/DIP32_STD/13V | 512 KiB | 5 V | `0xC240` | 3.0.0b39 | 3.0.0b27 | #74, #75 | 2026-09-12 |
| AE29F2008 | ASD | PROTO_FLASH_5V_PAGE/DIP32_SST39SF040/12V | 256 KiB | 5 V | `0xDA45` | 3.0.0b37 | 3.0.0b25 | #61 | 2026-09-10 |
| W29C020 | WINBOND | PROTO_FLASH_5V_PAGE/DIP32_SST39SF040/12V | 256 KiB | 5 V | `0xDA45` | 3.0.0b33 | 3.0.0b22 | #52 | 2026-08-31 |
| W29C040 | WINBOND | PROTO_FLASH_5V_PAGE/DIP32_SST39SF040/12V | 512 KiB | 5 V | `0xDA46` | 3.0.0b44 | 3.0.0b31 | #48, #88 | 2026-09-16 |
| SST39SF020 | SST | PROTO_FLASH_NOR_UNLOCK/DIP32_SST39SF040/12V | 256 KiB | 5 V | `0xBFB6` | 3.0.0b15 | not reported | #25 | 2026-08-08 |
| FM1608 | RAMTRON | PROTO_SRAM_28PIN/DIP28_JEDEC_SRAM_8K/12V | 8 KiB | 5 V | none | 3.0.0b33 | 3.0.0b22 | #18, #49 | 2026-08-31 |

## Alternative part numbers

| Chip | Same database entry |
|---|---|
| W27C512 | W27E512 |
| TMS27C512 | SMJ27C512, TMS27PC512 |
| W27E020 | W27C02, W27C020, W27E02, W27L02 |
| W27C040 | W27C04, W27E040 |
| W29C020 | W29C020C, W29C022 |
| W29C040 | W29C042 |
| SST39SF020 | SST39SF020A |

## Families

| Family | Parts | Vendors | Validated members |
|---|---|---|---|
| PROTO_EPROM_28PIN/DIP28_27512/12V | 25 | 14 | SST27SF512, W27C512 |
| PROTO_EPROM_28PIN/DIP28_27512/13V | 31 | 16 | TMS27C512 |
| PROTO_EPROM_32PIN/DIP32_27C020/12V | 62 | 25 | W27E020 |
| PROTO_EPROM_32PIN/DIP32_STD/12V | 19 | 15 | W27C040 |
| PROTO_EPROM_32PIN/DIP32_STD/13V | 15 | 10 | MX27C4000 |
| PROTO_FLASH_5V_PAGE/DIP32_SST39SF040/12V | 40 | 4 | AE29F2008, W29C020, W29C040 |
| PROTO_FLASH_NOR_UNLOCK/DIP32_SST39SF040/12V | 229 | 24 | SST39SF020 |
| PROTO_SRAM_28PIN/DIP28_JEDEC_SRAM_8K/12V | 26 | 7 | FM1608 |

## Family variation

| Family | Size range | Page sizes | Validated | Untested siblings |
|---|---|---|---|---|
| PROTO_EPROM_28PIN/DIP28_27512/12V | 64 KiB | not used | 2 | 23 |
| PROTO_EPROM_28PIN/DIP28_27512/13V | 64 KiB | not used | 1 | 30 |
| PROTO_EPROM_32PIN/DIP32_27C020/12V | 64–256 KiB | not used | 1 | 61 |
| PROTO_EPROM_32PIN/DIP32_STD/12V | 512 KiB | not used | 1 | 18 |
| PROTO_EPROM_32PIN/DIP32_STD/13V | 512 KiB | not used | 1 | 14 |
| PROTO_FLASH_5V_PAGE/DIP32_SST39SF040/12V | 32–512 KiB | 64, 128, 256, 512 | 3 | 37 |
| PROTO_FLASH_NOR_UNLOCK/DIP32_SST39SF040/12V | 64–512 KiB | not used | 1 | 228 |
| PROTO_SRAM_28PIN/DIP28_JEDEC_SRAM_8K/12V | 8 KiB | not used | 1 | 25 |

## Notes

- AE29F2008 and W29C020 are the same silicon under two names. Their database entries are
  identical on every field, including chip ID `0xDA45`. A finding on one applies to the
  other, and both rows are kept only because two distinct physical parts were tested.
- SST39SF020 is `algorithm: 6` (a sector-erase NOR part handled by a different firmware file,
  `PROTO_FLASH_NOR_UNLOCK`), not a protocol `0x05` part. It never traverses the page-write path,
  so a finding about protocol `0x05` writes does not apply to it.
