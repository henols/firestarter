# Validated EPROMs

Chips whose community `dev test` sweep passed every applicable step. One row per
closed issue. Appended by the `devtest-triage` skill.

`Firmware` is `not reported` where the report's `auto_capture.fw_board_identity` was
null — the host cannot read the firmware prerelease suffix, so it is not inferred from
the host version.

| Chip | Protocol | Pinout | Size | Host | Firmware | Issue | Closed |
|------|----------|--------|------|------|----------|-------|--------|
| fm1608 | 0x28 | DIP28_JEDEC_SRAM_8K | 0x2000 | 3.0.0b33 | 3.0.0b22 | #18, #49 | 2026-08-31 |
| sst39sf020 | 0x06 | DIP32_SST39SF040 | 0x40000 | 3.0.0b15 | not reported | #25 | 2026-08-08 |
| w27c512 | 0x07 | DIP28_27512 | 0x10000 | 3.0.0b33 | 3.0.0b22 | #42, #46 | 2026-08-31 |
| sst27sf512 | 0x07 | DIP28_27512 | 0x10000 | 3.0.0b33 | 3.0.0b22 | #47 | 2026-08-31 |
| w29c040 | 0x05 | DIP32_SST39SF040 | 0x80000 | 3.0.0b33 | 3.0.0b22 | #48 | 2026-08-31 |
| w27e020 | 0x08 | DIP32_27C020 | 0x40000 | 3.0.0b33 | 3.0.0b22 | #51 | 2026-08-31 |
| w29c020 | 0x05 | DIP32_SST39SF040 | 0x40000 | 3.0.0b33 | 3.0.0b22 | #52 | 2026-08-31 |
| AE29F2008 | 0x05 | DIP32_SST39SF040 | 0x40000 | 3.0.0b37 | 3.0.0b25 | #61 | 2026-09-10 |

AE29F2008 (ASD) and w29c020 (Winbond) are the same silicon: both report chip ID
`0xDA45` — Winbond manufacturer `0xDA`, device `0x45` — and their database entries are
identical but for a `page_size` field that algorithm `0x05` never reads. Two rows are kept
because two distinct physical parts were validated, not because two devices were.
