# Validated EPROMs

## Validated chips

| Chip | Vendor | Family | Size | VCC | Chip ID | Host | Firmware | Issues | Validated |
|---|---|---|---|---|---|---|---|---|---|
| SST27SF512 | SST | PROTO_EPROM_28PIN | 64 KiB | 5 V | `0xBFA4` | 3.0.0b33 | 3.0.0b22 | #47 | 2026-08-31 |
| W27C512 | WINBOND | PROTO_EPROM_28PIN | 64 KiB | 5 V | `0xDA08` | 3.0.0b33 | 3.0.0b22 | #42, #46 | 2026-08-31 |
| W27E020 | WINBOND | PROTO_EPROM_32PIN | 256 KiB | 5 V | `0xDA85` | 3.0.0b33 | 3.0.0b22 | #51 | 2026-08-31 |
| AE29F2008 | ASD | PROTO_FLASH_5V_PAGE | 256 KiB | 5 V | `0xDA45` | 3.0.0b37 | 3.0.0b25 | #61 | 2026-09-10 |
| W29C020 | WINBOND | PROTO_FLASH_5V_PAGE | 256 KiB | 5 V | `0xDA45` | 3.0.0b33 | 3.0.0b22 | #52 | 2026-08-31 |
| W29C040 | WINBOND | PROTO_FLASH_5V_PAGE | 512 KiB | 5 V | `0xDA46` | 3.0.0b33 | 3.0.0b22 | #48 | 2026-08-31 |
| SST39SF020 | SST | PROTO_FLASH_NOR_UNLOCK | 256 KiB | 5 V | `0xBFB6` | 3.0.0b15 | not reported | #25 | 2026-08-08 |
| FM1608 | RAMTRON | PROTO_SRAM_28PIN | 8 KiB | 3.3 V | none | 3.0.0b33 | 3.0.0b22 | #18, #49 | 2026-08-31 |

## Alternative part numbers

| Chip | Same database entry |
|---|---|
| W27C512 | W27E512 |
| W27E020 | W27C02, W27C020, W27E02, W27L02 |
| W29C020 | W29C020C, W29C022 |
| W29C040 | W29C042 |
| SST39SF020 | SST39SF020A |

## Families

| Family | Algorithm | Pinout | VPP | Parts | Vendors | Validated members |
|---|---|---|---|---|---|---|
| PROTO_EPROM_28PIN | `0x07` | `DIP28_27512` | 12 V | 25 | 14 | SST27SF512, W27C512 |
| PROTO_EPROM_32PIN | `0x08` | `DIP32_27C020` | 12 V | 63 | 25 | W27E020 |
| PROTO_FLASH_5V_PAGE | `0x05` | `DIP32_SST39SF040` | 12 V | 40 | 4 | AE29F2008, W29C020, W29C040 |
| PROTO_FLASH_NOR_UNLOCK | `0x06` | `DIP32_SST39SF040` | 12 V | 229 | 24 | SST39SF020 |
| PROTO_SRAM_28PIN | `0x28` | `DIP28_JEDEC_SRAM_8K` | 12 V | 26 | 7 | FM1608 |

## Family variation

| Family | Size range | Page sizes | Validated | Untested siblings |
|---|---|---|---|---|
| PROTO_EPROM_28PIN | 64 KiB | not used | 2 | 23 |
| PROTO_EPROM_32PIN | 64–256 KiB | not used | 1 | 62 |
| PROTO_FLASH_5V_PAGE | 32–512 KiB | 64, 128, 256, 512 | 3 | 37 |
| PROTO_FLASH_NOR_UNLOCK | 64–512 KiB | not used | 1 | 228 |
| PROTO_SRAM_28PIN | 8 KiB | not used | 1 | 25 |

## Notes

- AE29F2008 and W29C020 are the same silicon under two names. Their database entries are
  identical on every field, including chip ID `0xDA45`. A finding on one applies to the
  other, and both rows are kept only because two distinct physical parts were tested.
