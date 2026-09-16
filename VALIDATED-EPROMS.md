# Validated EPROMs

Chips whose community `dev test` sweep passed every applicable step. One row per chip.
Appended by the `devtest-triage` skill when it closes a PASS issue.

`Firmware` is `not reported` where the report's `auto_capture.fw_board_identity` was
null. The host cannot read the firmware prerelease suffix, so it is not inferred from
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

AE29F2008 (ASD) and w29c020 (Winbond) are the same silicon. Both report chip ID
`0xDA45` — Winbond manufacturer `0xDA`, device `0x45` — and their database entries are
identical but for a `page_size` field that algorithm `0x05` never reads. Two rows are
kept because two distinct physical parts were validated, not because two devices were.

## Families

A **family** is every part that shares all three of `programming.algorithm`, `pinout`,
and `electrical.vpp_mv`. Those three decide the programming procedure, the socket
wiring, and the rail — so a part in the same family is driven down the same code path
as a validated one.

The key is **derived from `chip_database.json`, never typed here**. Regenerate it with:

```bash
python3 - <<'EOF'
import json, collections
d = json.load(open("firestarter_app/firestarter/data/chip_database.json"))
fam = collections.defaultdict(set)
for vendor, chips in d.items():
    for e in chips:
        k = (e["programming"]["algorithm"], e["pinout"], e["electrical"]["vpp_mv"])
        for pn in e["part_number"].split(","):
            fam[k].add(pn.strip())
for k in sorted(fam):
    print(f"algo 0x{k[0]:02X} / {k[1]} / {k[2]/1000:g}V — {len(fam[k])} parts")
EOF
```

The database holds **959 distinct part numbers in 41 families**. The eight validated
chips fall into five of them, covering **383 parts**.

| Family (algorithm / pinout / VPP) | Parts | Vendors | Validated members |
|---|---|---|---|
| `0x05` / `DIP32_SST39SF040` / 12V | 40 | 4 | AE29F2008, W29C020, W29C040 |
| `0x06` / `DIP32_SST39SF040` / 12V | 229 | 24 | SST39SF020 |
| `0x07` / `DIP28_27512` / 12V | 25 | 14 | SST27SF512, W27C512 |
| `0x08` / `DIP32_27C020` / 12V | 63 | 25 | W27E020 |
| `0x28` / `DIP28_JEDEC_SRAM_8K` / 12V | 26 | 7 | FM1608 |

### What family membership does and does not promise

A validated family member is **evidence for its siblings, not proof**. The key fixes the
programming path, the wiring and the rail. It does not fix every parameter the path
reads:

- **Size varies inside a family.** `0x05` spans `0x8000` to `0x80000`; `0x08` spans
  `0x10000` to `0x40000`. A larger sibling exercises address lines the validated part
  never drove — and on 32-pin parts that is where the JP4/JP5 straps and the A19-on-pin-1
  maps live.
- **Page size varies inside a family.** `0x05` carries page sizes 64, 128, 256 and 512.
  Since phase 194 the `0x05` write path reads the part's real page size, so a sibling
  with a different page size runs a materially different write than the validated one.
- **Chip ID is per-part.** A family shares no identity bytes. A sibling whose
  `chip_id_check` is true and whose recorded id is wrong fails at the `id` step no matter
  how well the family is validated.

So: a same-family part is a reasonable thing to expect to work, and a good candidate to
ask a reporter to try. It is not a chip this project has validated, and it must not be
described as one.
