# CHIPS-MAP-DERIVATION.md — `rig-pins.json`'s nine new `chips` entries (162-01 Task 1)

PD-4 (RESEARCH R7 option A): the nine new entries are derived from the **v1.33 arm's own**
`EpromDatabase`, by a script, never hand-typed. The two pre-existing entries (`w27c512`,
`w29c020`) are untouched field-for-field.

## Exact command run

```bash
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
/workspaces/.v1.34-arms/v133/.venv/bin/python -P /path/to/scratch/derive_chips_map.py
```

The script (session scratch dir, never under `.planning/milestones/v1.34-artifacts/tools/`):

```python
#!/usr/bin/env python3
"""Scratch derivation script for 162-01 Task 1. NOT committed; lives outside .planning/milestones/v1.34-artifacts/tools/.
Derives the nine new rig-pins.json chips entries from the v1.33 arm's own EpromDatabase."""
import json

from firestarter.database import EpromDatabase

TOKENS = [
    "W27C512", "W27E512", "SST27SF512", "FM1608", "W27E040",
    "SST39SF040", "W29C040", "W29C020", "AM27C020", "M27C512", "2516",
]

PIN_COUNT_TO_PACKAGE = {24: "DIP24", 28: "DIP28", 32: "DIP32"}

db = EpromDatabase()
out = {}
for tok in TOKENS:
    e = db.get_eprom(tok)
    if e is None:
        out[tok] = {"ERROR": "get_eprom returned None"}
        continue
    pin_count = e.get("pin-count")
    package = PIN_COUNT_TO_PACKAGE.get(pin_count, f"UNKNOWN({pin_count})")
    out[tok] = {
        "size_bytes": e.get("memory-size"),
        "pin_count": pin_count,
        "package": package,
        "vpp_mv": e.get("vpp_mv"),
        "algorithm": e.get("protocol-id"),
        "manufacturer": e.get("manufacturer"),
        "name": e.get("name"),
    }

print(json.dumps(out, indent=2, sort_keys=True))
```

`-P` is required — without it `/workspaces/firestarter` (the firmware repo) wins as a PEP 420
namespace-package portion and `import firestarter` silently yields `None` (Pitfall 1).
`FIRESTARTER_CONFIG_DIR` is set inline, never exported, per Standing bench rule 9.

## Verbatim output

```json
{
  "2516": {
    "algorithm": 11,
    "manufacturer": "TEXAS INSTRUMENTS",
    "name": "2516",
    "package": "DIP24",
    "pin_count": 24,
    "size_bytes": 2048,
    "vpp_mv": 25000
  },
  "AM27C020": {
    "algorithm": 8,
    "manufacturer": "AMD",
    "name": "AM27C020",
    "package": "DIP32",
    "pin_count": 32,
    "size_bytes": 262144,
    "vpp_mv": 13000
  },
  "FM1608": {
    "algorithm": 40,
    "manufacturer": "RAMTRON",
    "name": "FM1608",
    "package": "DIP28",
    "pin_count": 28,
    "size_bytes": 8192,
    "vpp_mv": 12000
  },
  "M27C512": {
    "algorithm": 7,
    "manufacturer": "SGS-THOMSON",
    "name": "M27C512,M27V512",
    "package": "DIP28",
    "pin_count": 28,
    "size_bytes": 65536,
    "vpp_mv": 13000
  },
  "SST27SF512": {
    "algorithm": 7,
    "manufacturer": "SST",
    "name": "SST27SF512",
    "package": "DIP28",
    "pin_count": 28,
    "size_bytes": 65536,
    "vpp_mv": 12000
  },
  "SST39SF040": {
    "algorithm": 6,
    "manufacturer": "SST",
    "name": "SST39SF040",
    "package": "DIP32",
    "pin_count": 32,
    "size_bytes": 524288,
    "vpp_mv": 12000
  },
  "W27C512": {
    "algorithm": 7,
    "manufacturer": "WINBOND",
    "name": "W27C512,W27E512",
    "package": "DIP28",
    "pin_count": 28,
    "size_bytes": 65536,
    "vpp_mv": 12000
  },
  "W27E040": {
    "algorithm": 8,
    "manufacturer": "WINBOND",
    "name": "W27C04,W27C040,W27E040",
    "package": "DIP32",
    "pin_count": 32,
    "size_bytes": 524288,
    "vpp_mv": 12000
  },
  "W27E512": {
    "algorithm": 7,
    "manufacturer": "WINBOND",
    "name": "W27C512,W27E512",
    "package": "DIP28",
    "pin_count": 28,
    "size_bytes": 65536,
    "vpp_mv": 12000
  },
  "W29C020": {
    "algorithm": 5,
    "manufacturer": "WINBOND",
    "name": "W29C020,W29C020C,W29C022",
    "package": "DIP32",
    "pin_count": 32,
    "size_bytes": 262144,
    "vpp_mv": 12000
  },
  "W29C040": {
    "algorithm": 5,
    "manufacturer": "WINBOND",
    "name": "W29C040,W29C042",
    "package": "DIP32",
    "pin_count": 32,
    "size_bytes": 524288,
    "vpp_mv": 12000
  }
}
```

## Eleven-row resulting table (as landed in `rig-pins.json`)

| key | chip_token | size_bytes | pin_count | package | vpp_mv | algorithm | stamp_width |
|---|---|---|---|---|---|---|---|
| `w27c512` | `W27C512` | 65536 | 28 | DIP28 | 12000 | 7 | 16 (frozen) |
| `w27e512` | `W27E512` | 65536 | 28 | DIP28 | 12000 | 7 | — |
| `sst27sf512` | `SST27SF512` | 65536 | 28 | DIP28 | 12000 | 7 | — |
| `fm1608` | `FM1608` | 8192 | 28 | DIP28 | 12000 | 40 | — |
| `w27e040` | `W27E040` | 524288 | 32 | DIP32 | 12000 | 8 | — |
| `sst39sf040` | `SST39SF040` | 524288 | 32 | DIP32 | 12000 | 6 | — |
| `w29c040` | `W29C040` | 524288 | 32 | DIP32 | 12000 | 5 | — |
| `w29c020` | `W29C020` | 262144 | 32 | DIP32 | 12000 | 5 | 32 (frozen) |
| `am27c020` | `AM27C020` | 262144 | 32 | DIP32 | 13000 | 8 | — |
| `m27c512` | `M27C512` | 65536 | 28 | DIP28 | 13000 | 7 | — |
| `2516` | `2516` | 2048 | 24 | DIP24 | 25000 | 11 | — |

## Cross-check against RESEARCH R7's independently-measured table

**Verdict: PASS — zero disagreement.** Every one of the nine derived values (`size_bytes`,
`pin_count`, `package`, `vpp_mv`, `algorithm`) matches R7's table exactly, part for part:
`w27e512` 65536/28/DIP28/12000/7; `sst27sf512` 65536/28/DIP28/12000/7; `fm1608` 8192/28/DIP28/
12000/40; `w27e040` 524288/32/DIP32/12000/8; `sst39sf040` 524288/32/DIP32/12000/6; `w29c040`
524288/32/DIP32/12000/5; `am27c020` 262144/32/DIP32/**13000**/8; `m27c512` 65536/28/DIP28/
**13000**/7; `2516` 2048/24/DIP24/25000/11. The two frozen entries (`w27c512`, `w29c020`) were
not re-derived; they were asserted byte-unchanged field-for-field against `HEAD`.

## SGS-THOMSON vs. "ST M27C512"

`M27C512`'s DB row resolves to manufacturer **SGS-THOMSON**, name `M27C512,M27V512` — two DB rows
carry identical electrical and programming data (`ST` and `SGS-THOMSON` badge the same silicon
history) and `get_eprom` returns the SGS-THOMSON one. The roadmap's human label for the physical
part is "ST M27C512". Per v1.15 Phase 83's convention (`.planning/milestones/v1.15-artifacts/bench/EVIDENCE.md:166`):
record the human label and the resolving DB name **separately** — "ST M27C512" is a human label;
the resolving DB name is `M27C512`, vendor SGS-THOMSON. `rig-pins.json`'s key and `chip_token` are
both `m27c512` / `M27C512`; the "ST" prefix is never part of either.

## The `0x28`-vs-`0x40` family-column trap

v1.15's `EVIDENCE.md:59`/`:101` label FM1608's family **`0x40 (SRAM_STD / FRAM)`** — decimal 40
written as if it were hex. The DB algorithm for FM1608 is **40 decimal**, which formats as
**`0x28`** hex (`"0x%02x" % 40 == "0x28"`). `.planning/milestones/v1.16-artifacts/ledger/PROTOCOL-LEDGER.md:31` already
caught and retired this conflation (NAME-04). A `family` column in this phase's evidence, formatted
as `"0x%02x" % algorithm`, will correctly emit `0x28` for FM1608 — which will **look like** a
divergence against v1.15's `0x40` label. **It is not a divergence.** State this in FM1608's row's
`anomalies` once, and do not let a search conflate the two meanings of the token `0x40`: separately,
`0x40` also means `CTRL_READ_WRITE` in the v1.18 AM27C020 fix — the same hex token names two
unrelated things in this project's record, and this phase's chip-sweep evidence must not confuse
the two occurrences.

## Note on `algorithm`/`protocol-id`

`EpromDatabase.get_eprom()`'s wire dict names this field `protocol-id`; `rig-pins.json`'s `chips`
schema names it `algorithm`. Both name the identical DB value (verified: `w27c512`'s
`protocol-id: 7` matches its pre-existing `algorithm: 7`), so the derivation script reads
`protocol-id` and writes it under the `algorithm` key — a rename, not a different quantity.
