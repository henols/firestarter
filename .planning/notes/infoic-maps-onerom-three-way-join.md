---
title: "infoic.xml <maps> x one-rom: a three-way join that determines pin maps without hardcoding — 364/744 chips uniquely determined, plus the two keying traps"
date: 2026-08-22
context: "/gsd-explore: why is MAX_27C020_SIZE configured and used in build_db.py, and what else is not extracted from infoic.xml"
---

# Determining pin maps from infoic + one-rom, with no invented values

`pinouts.json` stays hand-authored — it is the accepted layout input, not a hardcode to
eliminate. The job this note serves is narrower and harder: **decide, for every chip, which
pin map is actually correct, using only sourced data.** infoic.xml and one-rom cannot replace
each other; combined, they determine the answer for about half the catalog and constrain the
rest.

Related: [`onerom-pinout-external-corroboration.md`](onerom-pinout-external-corroboration.md)
is the authoritative record on one-rom itself (schema, licensing, per-family provenance,
the three CIRCULAR families). **Read that first.** This note adds the axis it lacks: infoic's
own per-chip connectivity table.

---

## 1. The discovery: infoic.xml has a `<maps>` section the generator never opens

`infoic.xml` has five top-level children, not one:

```
<database type="INFOICT76">    <database type="INFOIC2PLUS">    <database type="INFOIC">
<configurations>  (122 <config>)          <maps>  (121 <map>, index 0..120)
```

Each `<map>` carries the ZIF-socket ground pin(s) and the set of socket pins the part uses:

```xml
<map index="10">
  <gnd count="1">16</gnd>
  <mask count="30">1,2,...,15,25,...,37,39,40</mask>
</map>
```

**It is indexed by the `pin_map` low byte the generator already parses** at
`tools/build_db.py:504` (`pm_idx = pin_map_raw & 0xFF`). minipro reads the same low byte —
`database.c:611` `device->pin_map = (uint8_t)opts;` — and resolves it against this table at
`database.c:1891` (`/* Get a pointer to the pin_map_t structure specified by index */`).
So `pm_idx` was never an opaque family cluster: it is a *pointer into a physical table
shipped in the same file*, and `build_db.py` uses the pointer while ignoring the table.

`build_db.py:37-39` declares a section header — `PINOUT LIBRARY (The Missing Physical
Layer)` — and leaves it empty. The missing physical layer is in the XML.

### ZIF → chip pin translation

Parts are top-justified in the 40-pin ZIF, lower half wrapping to the socket's bottom:

| chip pins | ZIF pins |
|---|---|
| 24-pin | 1–12 → 1–12; 13–24 → 29–40 |
| 28-pin | 1–14 → 1–14; 15–28 → 27–40 |
| 32-pin | 1–16 → 1–16; 17–32 → 25–40 |

```python
def zif_to_chip(z, n):
    h = n // 2
    return z if 1 <= z <= h else (z - (40 - n) if 41 - h <= z <= 40 else None)
```

### Why the oracle is trustworthy

Validated against three independent things before being used to accuse anything:

1. **GND agreement is total.** Across every in-scope chip with map data and a resolved
   pinout, `maps` GND and the hand-authored `pinouts.json` `gnd-pin` agree — **zero
   mismatches**. Two independently-authored sources, one mechanical translation, no
   disagreement.
2. **`DIP28_28C64`'s hand-labelled `nc-pin: [1, 26]` is reproduced exactly** — the oracle
   independently derives both NC pins the author wrote by hand.
3. **`AM27C010`'s NC pin is 30 = A17**, correct per datasheet for a 128K part on the
   32-pin JEDEC layout.

### Its one real limit

A map index is shared across a *family*, so it is a family-level statement, not strictly
per-part. `CAT28C512@DIP32` (64K) shares `map 9` with the 128K `AT28C010` and therefore
shows pin 2 (A16) connected though a 64K part does not need it. Treat the connected set as
an upper bound for the smallest member of a map group.

The 79 chips on `map[0]` (`gnd 20`, empty mask — the SRAM/NVRAM `pm_idx=0` cluster) carry
**no** connectivity information. The oracle is silent there, not permissive.

---

## 2. The three-way join

Every key comes from infoic; one-rom supplies only pin *function*:

| axis | source | what it fixes |
|---|---|---|
| which pins are bonded, per chip | infoic `maps[pin_map & 0xFF]` | connectivity |
| which layout class | infoic `(pin_count, code_memory_size)` | candidate set |
| VPP-programmed vs WE-programmed | infoic **`flags & 0x10`** (see trap 1) | control shape |
| what each bonded pin does | one-rom `chip-types.json` | function |

### Result

Of the 744 chips that pass the generator's own gates (`KNOWN_PROTOCOLS`, resolvable pinout):

| outcome | chips |
|---|---|
| **uniquely determined** — one one-rom layout whose pin set equals infoic connectivity | **364** |
| no one-rom counterpart at that `(pins, size)` | 256 |
| no connectivity data (`map[0]` SRAM cluster) | 79 |
| ambiguous — >1 one-rom layout fits | 45 |

Nine families come out corroborated on both the bonded-pin set **and** the ordered A0..An
list: `27256`, `27512`, `2764`, `27128`, `2732`, `2716`, `27C020`, `SST39SF040`, `27C040`.
Note `DIP28_2764` corroborates against **two** one-rom types — `2764` at 8K (29 chips) and
`27128` at 16K (26 chips) — which is direct evidence for the superset-plus-slicing design in
§3 and retires the "non-comparison" status the onerom note assigns that family.

The rows where the join *disagrees* with `pinouts.json` are filed as defects in
[`todos/pending/pinout-address-width-and-we-pin-corrections.md`](../todos/pending/pinout-address-width-and-we-pin-corrections.md).

---

## 3. What this makes derivable: address-bus slicing

`pinouts.json` stores `address-bus-pins` as a full ordered superset per layout. If the
generator **slices it to the part's real width** —

```python
n_lines = (mem_size - 1).bit_length()
address_bus = layout["address-bus-pins"][:n_lines]
```

— then pin 31's role on the 32-pin EPROM layout is *derived*, not declared: it is PGM
exactly when the slice does not reach it. one-rom independently confirms this
(`27C010`/`27C020`: `programming.pgm.pin = 31`; `27C040`: A18 at 31), and `maps` confirms
the connectivity both ways.

Consequences: `MAX_27C020_SIZE` disappears (see
[`todos/pending/derive-away-max-27c020-size-hardcode.md`](../todos/pending/derive-away-max-27c020-size-hardcode.md)),
and `DIP32_27C020` and `DIP32_STD` become one layout distinguished only by the slice.

---

## 4. Two keying traps — both hit on the first pass

### Trap 1: key the VPP/WE discriminator on `flags & 0x10`, NOT on raw `protocol_id`

Upstream files `AT28C256` under `protocol_id = 0x07` (an EPROM-family algorithm);
`classify()` promotes it to `0x0D`. A join keyed on the raw `protocol_id` therefore looks
for a VPP-programmed layout and matches one-rom's **`27256`** instead of **`28C256`**:

```
one-rom 27256 (EPROM):  A14 = pin 27,  VPP = pin 1
one-rom 28C256 (EEPROM): A14 = pin 1,  WE  = pin 27
```

Those two layouts are **pin-swapped on exactly the pair that matters**. Generating from the
protocol-keyed join would have put VPP on pin 1 of AT28C256 — re-authoring the precise
WARNING-5 hazard the 2026-05 one-rom pass removed (`a332464`). The same error re-fires on
the 24-pin `DIP24_2816` set, which matches one-rom `2716` rather than `28C16` for the Site-B
rows whose `proto_id` is demoted only *after* the XML read.

**Rule: the erasability bit (`flags & 0x10`), or the post-`classify()` algorithm, is the
control-shape key. The raw `protocol_id` is not.** Fixing this also recovers a large share of
the 256 "no counterpart" rows, most of which are promoted 5V EEPROMs rejected for wanting VPP.

### Trap 2: filter on rail compatibility

`(24-pin, 512 bytes)` matches one-rom's **`2704`** — a 3-rail bipolar-era PROM needing −5V
and +12V the RURP shield cannot source. It matched the 8 `AT28C04` rows purely on pin count
and size. Any candidate filter must exclude the hardware-blocked one-rom types the onerom
note already enumerates (`2704`, `2708`, `HM7641`, `27C200`, `27C400`).

---

## 5. The unexploited axis for the ambiguous 45

All 45 are 32-pin 128K EPROMs where one-rom's `27C010` and `27C301` both survive the
`(pins, size)` filter — the HN27C301 has a nonstandard layout (A16 on pin 24, one-rom
`27C301.address[-1] == 24`).

infoic does separate them, on two fields:

- **`pm_idx`**: the `AM27C010` group is 10 (`maps[10]`, NC = pin 30); the
  `MBM27C1000P` / `HN27C301AG` / `HN27C301G` / `M27C1000` group is 12 (`maps[12]`, all 32
  bonded).
- **the discarded `pin_map` upper byte**: `0xd0` on exactly those 4 rows
  (`0xd0005f0c`) versus `0x00` on the `AM27C010` group (`0x00005f0a`). Byte 3 takes only
  three values catalog-wide — `0x00` (737), `0x90` (26), `0xd0` (4) — and byte 2 is always
  zero.

So the discriminating axis exists in infoic and is unread. Resolving this ambiguity is a
decode question, not a datasheet question.

---

## 6. Reproduction

Both fetches are the only network steps. `infoic.xml` is pinned to the SHA already recorded
in `tools/DECODE-NOTES.md` §0; one-rom is `main` (pin it before vendoring — see the onerom
note's "do not auto-refresh" warning).

```bash
curl -sS -o infoic.xml \
  https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml
curl -sL -o chip-types.json \
  https://raw.githubusercontent.com/piersfinlayson/one-rom/main/rust/config/json/chip-types.json
```

```python
# run from firestarter_app/ with the two files alongside
import sys, json, xml.etree.ElementTree as ET
from collections import Counter
sys.path.insert(0, "."); sys.path.insert(0, "tools")
import build_db as B

root = ET.parse("infoic.xml").getroot()
OR = json.load(open("chip-types.json"))["chip_types"]
FS = json.load(open("firestarter/data/pinouts.json"))

ints = lambda t: [int(x) for x in (t or "").split(",") if x.strip()]
MAPS = {int(m.get("index")): (ints(m.find("gnd").text), ints(m.find("mask").text))
        for m in root.find("maps")}
def z2c(z, n):
    h = n // 2
    return z if 1 <= z <= h else (z - (40 - n) if 41 - h <= z <= 40 else None)

def or_pinset(e):
    s = set(e.get("address") or []) | set(e.get("data") or [])
    for grp in ("control", "programming"):
        for c in (e.get(grp) or {}).values():
            if c and c.get("pin"): s.add(c["pin"])
    return s | {p["pin"] for p in (e.get("power") or [])}

# NOTE: has_vpp must be compared against flags & 0x10, NOT protocol_id (trap 1).
BLOCKED = {"2704", "2708", "HM7641", "27C200", "27C400"}          # trap 2
res, det = Counter(), {}
for db in root.findall(".//database[@type='INFOIC2PLUS']"):
  for mfg in db.findall(".//manufacturer"):
    for ic in mfg.findall(".//ic"):
        try:
            pkg = int(ic.get("package_details"), 16); pin = (pkg & 0x7F000000) >> 24
            if pkg & 0x80000000 or (pkg & 0xFF00) >> 8: continue
            tp = int(ic.get("type"), 16)
        except Exception: continue
        if not (24 <= pin <= 32) or tp not in (1, 4): continue
        pr = int(ic.get("protocol_id"), 16)
        if pr not in B.KNOWN_PROTOCOLS: continue
        fl = int(ic.get("flags"), 16); sz = int(ic.get("code_memory_size"), 16)
        pm = int(ic.get("pin_map", "0"), 16)
        key = B.resolve_pinout_key(pin, int(ic.get("variant"), 16), fl, pm_idx=pm & 0xFF,
                                   proto_id=pr, type_int=tp, mem_size=sz)
        if key is None: continue
        g, mk = MAPS.get(pm & 0xFF, ([], []))
        conn = {z2c(z, pin) for z in set(g) | set(mk)} - {None}
        if len(conn) <= 1: res["no maps data"] += 1; continue
        want_vpp = not (fl & 0x10)                                 # trap 1
        cand = [k for k, e in OR.items()
                if k not in BLOCKED and e.get("pins") == pin and e.get("size") == sz
                and or_pinset(e) == conn
                and bool(((e.get("programming") or {}).get("vpp") or {}).get("pin")) == want_vpp]
        if len(cand) == 1:
            res["DETERMINED"] += 1
            det.setdefault((key, cand[0]), []).append(ic.get("name").split(",")[0])
        else:
            res["ambiguous" if cand else "no qualifying layout"] += 1
print(dict(res))
for (key, ork), chips in sorted(det.items(), key=lambda x: -len(x[1])):
    fs = FS[key]["pins"].get("address-bus-pins", [])
    oa = OR[ork].get("address") or []
    print(f"{key:22s} -> {ork:12s} {len(chips):3d} "
          f"{'AGREES' if fs[:len(oa)] == oa else 'DISAGREES'}")
```

The published numbers in §2 were produced with `want_vpp = pr in {0x07,0x08,0x0B}` (the
trap-1 form). Re-running with the `flags & 0x10` form above **will** shift the buckets —
expect more DETERMINED rows and fewer "no qualifying layout" — and the promoted-EEPROM
families to re-pair against `28C256` / `28C16` instead of `27256` / `2716`. Regenerate
before quoting counts.

---

## Downstream

- Pinout corrections this join found:
  [`todos/pending/pinout-address-width-and-we-pin-corrections.md`](../todos/pending/pinout-address-width-and-we-pin-corrections.md)
- The `MAX_27C020_SIZE` removal it enables:
  [`todos/pending/derive-away-max-27c020-size-hardcode.md`](../todos/pending/derive-away-max-27c020-size-hardcode.md)
- Other unread infoic fields (`page_size`, `chip_info`, `voltages` low nibble, `pin_map`
  upper byte): [`infoic-unextracted-fields-inventory.md`](infoic-unextracted-fields-inventory.md)
- The one-rom gate this should be folded into rather than compete with:
  [`todos/pending/onerom-pinout-external-corroboration-gate.md`](../todos/pending/onerom-pinout-external-corroboration-gate.md).
  `<maps>` is per-chip connectivity; one-rom is per-layout function. A gate carrying both
  checks strictly more than either alone, and `<maps>` needs no vendoring — it ships in the
  file the generator already fetches.
