---
title: "one-rom chip-types.json vs pinouts.json — external corroboration result (8/15 families genuinely corroborated; 3 are CIRCULAR; vacuous for the programming axis)"
date: 2026-08-20
context: "/gsd-explore: can the files in piersfinlayson/one-rom rust/config/json be used to confirm the firestarter database?"
---

# one-rom `chip-types.json` — what it corroborates and what it cannot

Investigated whether [One ROM](https://github.com/piersfinlayson/one-rom)'s published
hardware config JSON can serve as a second source for `firestarter_app/firestarter/data/pinouts.json`.

**Verdict: POSITIVE for bus maps, but weaker than a naive diff suggests — and this is the
third use of this source, not the first.** Of 15 pinout families: **8 genuinely corroborated**,
**2 ambiguous**, **3 CIRCULAR** (their pin maps were *authored from* one-rom, so their
agreement proves nothing), 1 family-superset non-comparison, 1 with no counterpart. Zero new
defects found. **VACUOUS for the programming axis**, where every recent defect has actually
landed.

Read the "Prior art" section before treating any of this as new.

## Prior art — this source has already caught two real defects here

**Do not re-discover this.** One ROM was cross-checked against our pin maps on **2026-05-13**
(meta commit `fd9efaea`, phase 04 hardware validation) and the findings were acted on in
**2026-05-20** (`a332464`, "correct pinouts for SST39SF040 / 28C256 / 2732 / 6116 families —
one-rom verified"). That pass found **two genuine defects**:

1. **AT28C256 was routed to `DIP28_2764`** — wrong. Per one-rom's `28C256`, it needs 15
   address lines with **A14 at pin 1 (not VPP)** and **WE at pin 27 (not PGM)**. Algorithm
   dispatch was already correct via WARNING-5 → `configure_eeprom28c`; the *pinout* was wrong.
   Fix: authored `DIP28_28C256`, moved 8 chips onto it.
2. **SST39SF040 was routed to `DIP32_STD`** (a 27C040 layout) — **pins 1 and 31 swapped**.
   Per one-rom, SST39SF040 has A18 at pin 1 (not VPP) and WE at pin 31 (not an address line).
   This **likely explained the 2026-05-12 bench failure** (chip-ID reading `0x0000` +
   address-bus crosstalk symptoms) that had been attributed to a dead chip. Fix: authored
   `DIP32_SST39SF040`, moved 47 chips onto it.

That same commit also moved 16 chips `DIP24_2716` → `DIP24_2732` (a 2K layout was being used
for 4K parts) and 2 chips → `DIP24_6116` + type SRAM. 92 database entries changed in total.

So the track record is the strongest argument this source has: **it has already found a
bench-visible defect here that we had misattributed to hardware.** What it has *not* done is
get re-run since — the May pass covered "priority chips", not all 15 families.

## Why it is an independent oracle

1. **Different lineage.** No relationship to `infoic.xml`. Authored from datasheets by a
   different maintainer for a different product. Contrast the candidates rejected in
   `research/questions.md` — most open programmer tables are infoic forks, and a fork
   corroborates nothing.
2. **Different validation oracle.** One ROM *emulates* a ROM; it never programs one. Its bus
   maps are proven by the emulator working when seated in a real retro machine — in-circuit
   read-path evidence, orthogonal to our write-path bench evidence.
3. **Disjoint blind spot.** No VPP millivolts, no `pulse_duration_us`, no algorithm, no chip
   ID, no page size — so where it speaks, it speaks only about the axis `pinouts.json` owns.

Active project (345 stars, `updated_at` 2026-08-20), so a maintained source, not a stale snapshot.

**But independence is per-family, not global.** Any family whose pins we *authored from*
one-rom cannot be corroborated by one-rom. Three families are in that position. Getting this
wrong is the single easiest way to manufacture false confidence from this source.

## What's in the directory

26 files, two unrelated kinds:

- **`fire-*.json` / `ice-*.json` (24 files)** — One ROM PCB hardware configs: RP2350/STM32F4
  GPIO-to-pin-type mappings and jumper-header layouts. **No relevance to us.** Do not re-read
  these hoping for chip data.
- **`chip-types.json` (58601 bytes, 37 entries — 34 real chip types + 3 plugin stubs)** — the
  only file that matters.

## Schema correspondence

Near-1:1, which is why the diff is mechanical rather than interpretive:

| one-rom | firestarter `pinouts.json` |
|---|---|
| `address` (ordered A0..An) | `address-bus-pins` (ordered A0..An) |
| `data` (D0..D7) | `data-bus-pins` |
| `control.ce.pin` | `ce-pin` |
| `control.oe.pin` | `oe-pin` |
| `control.write.pin` | `rw-pin` |
| `programming.vpp.pin` | `vpp-pin` |
| `programming.pgm.pin` | (no direct equivalent — see `DIP32_27C020` below) |
| `power[].pin` where `name == "VCC"` / `"GND"` | `vcc-pin` / `gnd-pin` |
| `control.*.type` (`fixed_active_low` / `configurable`) | (**not representable** — see below) |

Both sides number pins as physical DIP positions and both order the address list A0-first.
The `control.*.type` row is the one real schema gap on our side, and it is the blocker in
[`seeds/mask-rom-24pin-read-support.md`](../seeds/mask-rom-24pin-read-support.md).

## Result

Snapshot: blob `56cb04ca91e66aef0fd15236cc357602367c2b05`, `main`, fetched 2026-08-20.
Fields compared: `address-bus-pins`, `data-bus-pins`, `ce-pin`, `oe-pin`, `rw-pin`,
`vpp-pin`, `vcc-pin`, `gnd-pin`.

**12 families are byte-identical on every compared field. What that's worth depends entirely
on provenance**, so the table carries it:

| firestarter family | one-rom type | chips | pins authored | corroborating? |
|---|---|---|---|---|
| `DIP24_2716` | `2716` | 15 | `86a31ca` 05-08 | **yes** — predates any one-rom use |
| `DIP24_2732` | `2732` | 16 | `86a31ca` 05-08 | **yes** — `a332464` changed only *routing* onto it, not its pins |
| `DIP28_27256` | `27256` | 67 | `86a31ca` 05-08 | **yes** — predates |
| `DIP28_27512` | `27512` | 45 | `86a31ca` 05-08 | **yes** — predates; also checked-and-unchanged in the May pass |
| `DIP32_STD` | `27C040` | 78 | `86a31ca` 05-08 | **yes** — predates |
| `DIP28_JEDEC_SRAM_8K` | `28C64` | 14 | `b0d939f` 05-13, from XML `type=4` | **yes** — independent derivation; checked-unchanged in May |
| `DIP24_2816` | `28C16` | 19 | `fa0c1a4` 06-09 | **yes** — postdates, no one-rom reference |
| `DIP28_28C64` | `28C64` | 35 | `ff70920` 05-13 | **ambiguous** — same day as the cross-check, message is silent |
| `DIP32_28C512_EEPROM` | `28C512` | 18 | `ff70920` 05-13 | **ambiguous** — same as above |
| `DIP24_6116` | `6116` | 7 | `a332464` 05-13 | **NO — circular.** Created *from* one-rom |
| `DIP28_28C256` | `28C256` | 30 | `a332464` 05-13 | **NO — circular.** Created *from* one-rom |
| `DIP32_SST39SF040` | `SST39SF040` | 255 | `a332464` 05-13 | **NO — circular.** Created *from* one-rom |

Note `DIP28_JEDEC_SRAM_8K` pairs with one-rom **`28C64`**, not `62256` — 13 address lines,
CE 20, OE 22, WE 27, and our `nc-pin: [1, 26]` matches their "pin 1 NC". Pairing it against
`62256` (32 KB, 15 lines) produces a spurious DIFF; the May pass got this right and a fresh
attempt can easily get it wrong.

### 1 family corroborated semantically, not literally — and it settles an open question

`DIP32_27C020` (88 chips, authored `38b55d5`/`3659121` 06-30/07-01 from `AM27C020.pdf` plus an
operator schematic study — **no one-rom involvement, so genuinely corroborating**): ours
carries `rw-pin: [31]`, theirs has no `control.write`. **Not a divergence.** One ROM records
`programming.pgm.pin = 31` for **both** `27C010` and `27C020`, independently confirming the
CR-01 premise: on ≤256K parts pin 31 is **/PGM, not A18**. Our `rw-pin` is the mechanism that
drives it — host resolves pin 31 → `pin_conversions[32][31] = 22` → `config.rw_line = 22`,
which the firmware folds into `CTRL_READ_WRITE` (0x40).

**Consequence for an open investigation:** the marginal Phase 99 AM27C020 bench result
(write#1 60/64 bytes, write#2 0/64 — [[project_v118_phase99_bench_defer]]) **cannot** be
explained by a wrong pin-31 assignment. VPP droop stands as the hypothesis, with one competing
explanation eliminated by an independent source rather than by re-reading our own schematic.

### 1 non-comparison

**`DIP28_2764`** — ours has 14 address lines (pin 26 = A13), theirs 13. Ours is a deliberate
**2764 + 27128 superset family** (58 chips, incl. `AM27128A`, `AM27C128`, `SMJ27C128`). Pin 26
is NC on a true 2764 and A13 on a 27128. Correct as authored — the "diff" is an artifact of
them modelling one chip where we model a family. A naive automated diff reports RED and the
code is right; any gate must encode the reason, not just the exception.

### 1 family with no counterpart

`DIP24_2532` (1 chip). One ROM has `2332` (a 4 KB *mask ROM*), not the TI 2532 EPROM. Ours
came from `94ea3b5` (86-04) via `tools/extra_chips.json`. Stays single-sourced.

## Reproduction

Offline-reproducible from the vendored blob; the fetch is the only network step.

```bash
curl -sL -o chip-types.json \
  https://raw.githubusercontent.com/piersfinlayson/one-rom/main/rust/config/json/chip-types.json
# then, from firestarter_app/:
python3 - <<'PY'
import json
fs = json.load(open('firestarter/data/pinouts.json'))
oo = json.load(open('chip-types.json'))['chip_types']
M = {'DIP24_2716':'2716','DIP24_2732':'2732','DIP28_2764':'2764','DIP28_27256':'27256',
     'DIP28_27512':'27512','DIP28_28C256':'28C256','DIP24_6116':'6116','DIP32_27C020':'27C020',
     'DIP32_SST39SF040':'SST39SF040','DIP28_28C64':'28C64','DIP32_28C512_EEPROM':'28C512',
     'DIP24_2816':'28C16','DIP32_STD':'27C040','DIP28_JEDEC_SRAM_8K':'28C64'}
for fsk, ook in M.items():
    p, o = fs[fsk]['pins'], oo[ook]
    g = lambda n: (o.get('control', {}).get(n) or {}).get('pin')
    f = lambda n: (p.get(n) or [None])[0]
    flags = []
    if p.get('address-bus-pins', []) != o.get('address', []): flags.append('ADDR')
    if p.get('data-bus-pins', []) != o.get('data', []):       flags.append('DATA')
    for label, fk, ok in [('CE','ce-pin','ce'), ('OE','oe-pin','oe'), ('WE','rw-pin','write')]:
        if f(fk) != g(ok): flags.append(f'{label} fs={f(fk)} oo={g(ok)}')
    if f('vpp-pin') != (o.get('programming', {}).get('vpp') or {}).get('pin'): flags.append('VPP')
    for label, fk, nm in [('VCC','vcc-pin','VCC'), ('GND','gnd-pin','GND')]:
        if f(fk) != next((x['pin'] for x in o.get('power', []) if x['name'] == nm), None):
            flags.append(label)
    print(('AGREE  ' if not flags else 'DIFF   ') + f'{fsk:22s} vs {ook:10s} ' + ' | '.join(flags))
PY
```

Expected: 12 AGREE, 2 DIFF — `DIP28_2764` (ADDR, superset) and `DIP32_27C020`
(`WE fs=31 oo=None`, semantic agreement via `programming.pgm`).

**Two mapping gotchas that will waste your time:**

- Map their `control.write` to our **`rw-pin`**, not to a `we-pin`. We have **no `we-pin` key** —
  a pass looking for one reports 6 spurious WE mismatches (`DIP28_28C256`, `DIP24_6116`,
  `DIP28_28C64`, `DIP32_28C512_EEPROM`, `DIP24_2816`, `DIP32_SST39SF040`), all agreements.
- Pair `DIP28_JEDEC_SRAM_8K` with **`28C64`**, not `62256`. Ours is an 8 KB family; their
  `62256` is 32 KB. Our own `61256,62256` row routes to `DIP28_28C256` instead.

## What it cannot do — three hard limits

1. **Nothing on the programming axis.** No `vpp_mv`, `pulse_duration_us`, `algorithm`,
   `chip_id_value`, or page size. Those are precisely where the recent defects lived: the
   4.5 V premise disproved in Phase 148 (present in 5 files, not 2), the 128/64 B page seam in
   Phase 149, the deleted `CTRL_VPE_ENABLE` assert behind the Phase 145 W27C512 byte-0
   failure. One ROM never programs a chip. Treating this as general database validation would
   be an overclaim of exactly the class corrected in v1.22's C-5.
2. **It cannot touch `chip_database.json`.** That file is generated from `infoic.xml` and the
   generator may not invent fields without upstream proof
   ([[feedback_generator_no_fields_without_infoic_proof]],
   [[reference_chip_database_schema_algorithm_pulse_duration]]). The usable seam is
   `pinouts.json`, which `tools/build_db.py:23` reads as an **input** — hand-maintained, and
   therefore *unprotected* by the generator's decode tests.
3. **Licensing permits vendoring, but read the right file.** `LICENSE.md` dual-licenses:
   **MIT** for "software and firmware files", CERN-OHL-W-2.0 for "schematic, PCB files, 3d
   models and other hardware files, in particular those in the `hardware/` directory".
   `rust/config/json/chip-types.json` is a software config consumed by the `onerom-config`
   crate and sits nowhere near `hardware/` — **MIT applies**; vendor with the notice and
   `Copyright (c) 2026 Piers Finlayson`. The GitHub API reports the repo license as
   `NOASSERTION` / "Other" and there is **no root `LICENSE` file** (it is `LICENSE.md`) — both
   are artifacts of the dual-license layout, not an absence of license. Do not let either
   re-open this question.

## Coverage it has that we don't

20 one-rom types have no counterpart in any of firestarter's 953 part numbers or aliases —
checked exhaustively, not sampled. Split by whether they are reachable:

- **Plausible (read-only, 5 V single rail, 24/28-pin):** `2316`, `2332`, `2364`, `23128`,
  `23256`, `23512`, `231024`, `23QL384`, `23QL512`, `23C1001`, `23C1010` — the Commodore /
  arcade mask ROMs. Routed to [`seeds/mask-rom-24pin-read-support.md`](../seeds/mask-rom-24pin-read-support.md);
  blocked on `configurable` CS polarity, which `database.py:297` cannot express
  (`static-high-pins` only, no `static-low-pins`).
- **Hardware-blocked, do not let these ride along:** `2704`/`2708` (3-rail, need −5 V and
  +12 V the RURP shield cannot source), `HM7641` (bipolar fusible-link PROM),
  `27C200`/`27C400` (40-pin, 16-bit data bus — no socket).
- **Write-path scope, not a pin-map question:** `27C301`, `27C080` (32-pin EPROMs).

## Downstream

- Gate spec (lock the byte-identical set, pin the exceptions with reasons):
  [`todos/pending/onerom-pinout-external-corroboration-gate.md`](../todos/pending/onerom-pinout-external-corroboration-gate.md).
  **The gate's real value is not "confirming" the 8 genuinely-corroborated families — it is
  that the 3 circular families (`DIP24_6116`, `DIP28_28C256`, `DIP32_SST39SF040`, together
  292 chips) are the *fixes* the May pass produced, and nothing today would notice if an edit
  silently un-fixed one.** A regression in `DIP32_SST39SF040` reintroduces a defect that
  already once looked like dead silicon on the bench.
- Mask-ROM family seed: [`seeds/mask-rom-24pin-read-support.md`](../seeds/mask-rom-24pin-read-support.md)
- The gap on the programming axis: `research/questions.md`, section "Is there an independent
  second source for the PROGRAMMING axis?" (2026-08-20)
- Original cross-check: meta `fd9efaea`; corrections `a332464`; full audit data in
  `.planning/phases/04-hardware-validation-rurp-shield/04-HW-VALIDATION.md`
