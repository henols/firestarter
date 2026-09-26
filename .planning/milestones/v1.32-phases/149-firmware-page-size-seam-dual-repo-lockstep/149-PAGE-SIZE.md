# 149-PAGE-SIZE.md — Phase 149 D-16 review artifact

This is the phase's single reviewable-whole artifact for the firmware page-size seam. It carries
the fork point this phase measures every figure against, the cold pre-edit AVR baseline, the D-01
upstream-provenance table and its citation chain, the three measured non-claims the Evidence
Ceiling requires, the DB-side and firmware-side evidence each plan in this phase appended, and the
closing baseline-update and what-ships record.
Everything this document records about the page-size change is **software-proven and unvalidated on silicon**.

## The fork point

Branch: `gsd/v1.32-at28c-write-path-root-cause-report-provenance` — byte-identical to the branch
`firestarter_app` was already on, so the milestone's dual-repo pairing is legible by name alone.

Forked with:

```
git -C firestarter fetch origin
git -C firestarter status --porcelain          # empty before switching
git -C firestarter checkout -b gsd/v1.32-at28c-write-path-root-cause-report-provenance origin/beta
```

`origin/beta` resolved, at fork time, to:

```
7f6afc65be2022575989772cc0a5945611741831
```

(Research measured this as `7f6afc6` on 2026-08-19; the full SHA above is what this plan actually
observed and is the fork point every figure in this phase is measured against. It did not move
between research and execution.)

The firmware submodule was previously on `gsd/v1.31-27c-programming-algorithm-fidelity` at
`6992271`. The v1.31 PRs were squash-merged into `beta`, so a `git merge-base --is-ancestor` check
between `6992271` and the new branch returns a false negative. **Ancestry checks were deliberately
not used anywhere in this verification.** The fork was instead verified by five content checks,
each asserting the literal presence of v1.31 deliverables in the new `HEAD`:

```
$ git -C firestarter show HEAD:scripts/check_size_baseline.py | grep -n 'MERGE05'
123:MERGE05_UNO_CLASS_FLASH_BAND = 64
167:MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96
... (8 more references to both constants)

$ git -C firestarter cat-file -e HEAD:scripts/baseline/size_baseline_base01.json ; echo EXIT=$?
EXIT=0

$ git -C firestarter grep -c 'eprom_internal_program_pulse' HEAD -- src/proms/eprom.cpp
HEAD:src/proms/eprom.cpp:4

$ git -C firestarter grep -c 'CAP-02' HEAD -- src/firestarter.cpp
HEAD:src/firestarter.cpp:3

$ git -C firestarter diff --stat 6992271 HEAD -- src/json_parser.c include/json_parser.h \
    include/firestarter.h src/proms/eeprom_28c.cpp scripts/ platformio.ini test/native
(no output — byte-identical)
```

All five checks passed. `eprom_internal_program_pulse` appearing exactly 4 times proves Phase 145's
W27C512 fix landed; `CAP-02` appearing in `src/firestarter.cpp` proves fw#52's CAP-02 conflict is
resolved on `origin/beta`; the empty `diff --stat` proves every file this phase touches is
byte-identical between the old v1.31 tip and the new fork point, so no in-flight change on `beta`
contaminates this phase's baseline. `git -C firestarter status --porcelain` was empty both before
and after the fork.

## Pre-edit cold measurement (D-13)

Procedure, run once per env, in that order, from `/workspaces/firestarter`:

```
rm -rf .pio/build/<env>
pio run -e <env> 2>&1 | tee .../149-baseline-cold-<env>.log
```

Each of the three logs is one uninterrupted invocation (a single `Processing <env>` header), ends
in `[SUCCESS]`, and reports zero `warning:` lines.

| env       | flash_used | flash_total | ram_used | ram_total | warnings |
|-----------|-----------:|------------:|---------:|----------:|---------:|
| uno       | 24920      | 32256       | 1573     | 2048      | 0        |
| uno328pb  | 24970      | 32384       | 1579     | 2048      | 0        |
| leonardo  | 27002      | 28672       | 2014     | 2560      | 0        |

**Delta vs `size_baseline.json`** (the live baseline, uno 24920/1573, uno328pb 24970/1579,
leonardo 27002/2014): **0** on all six figures, on all three envs. Nothing was inherited from the
v1.31→beta merge beyond what `size_baseline.json` already records; the cold capture reproduces it
exactly.

**Delta vs `size_baseline_base01.json`** (BASE-01, MERGE-05's judged reference: leonardo 26906,
uno 24824, uno328pb 24874; RAM 1573/1579/2014 unchanged): **+96 B flash on all three envs, 0 B RAM
on all three envs.** This +96 B is Phase 145's already-adjudicated W27C512 defect fix, funded by
`MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96` — it is not new to this phase and this phase adds nothing
to it at this measurement point.

**Leonardo's MERGE-05 flash headroom is the number 0 bytes.** The leonardo must-not-grow band is
0 B; the only allowance leonardo has ever had is the 96 B defect-fix exemption, and the current
+96 B delta consumes all of it: `0 (band) + 96 (exemption) − 96 (current delta) = 0 bytes`
remaining. Leonardo's physical free flash is **1670 B of 28672 (5.8%)** (28672 − 27002 = 1670),
which is a separate number from the MERGE-05 allowance — plenty of physical flash remains, but the
policy allowance that governs this phase's own growth is exhausted.

**Uno-class MERGE-05 headroom is 64 bytes.** `MERGE05_UNO_CLASS_FLASH_BAND = 64` plus the same 96 B
exemption gives uno/uno328pb a 160 B total allowance; the current +96 B delta leaves
`160 − 96 = 64 bytes` of policy headroom before this phase adds a single byte.

**v1.31's open MERGE-05 band breach, named explicitly:** the leonardo band is 0 B and the current
delta is already +96 B over BASE-01 — entirely consumed by Phase 145's fix, before this phase's own
page-size change adds anything. Any flash growth this phase's firmware seam introduces on leonardo
has zero band left to land in and must be separately funded (D-12), not silently absorbed against
this already-spent allowance.

## Why the reference SHA in size_baseline.json is not usable

`scripts/baseline/size_baseline.json`'s `meta.firmware_tree_sha` field records `3d8ec49…`, the root
tree of commit `6cc4795` — a **Phase 144** commit. That tree does not contain the +96 B Phase 145
later added (the same file's own AVR figures already include Phase 145's fix), so the field and the
figures it sits next to are mutually inconsistent as a reproducibility anchor. This plan therefore
did not reason from `meta.firmware_tree_sha` at all — the fork was verified by content (see above)
and the cold capture was compared directly against the live figures in `size_baseline.json` and
`size_baseline_base01.json`. Plan 07 corrects the stale field; this plan deliberately leaves it
untouched and unused.

## Upstream provenance — which chips get a delivered page size (D-01)

`chip_database.json`'s 84 `algorithm: 13` (`0x0D`) rows are not 84 upstream-`0x0D` records.
`build_db.py`'s `classify()` promotes several DIP families into `0x0D` from whatever protocol they
actually arrived with in the pinned `infoic.xml`. Joining all 84 rows back to the upstream XML
(all 84 matched, zero unmatched):

| upstream `protocol_id` | `page_size` values → counts | row count |
|---|---|---:|
| `0x07` | 1→14 · 16→1 · 32→8 · 64→22 · 128→1 · 256→1 | 47 |
| `0x0B` | 1→17 · 16→2 | 19 |
| **`0x0D`** | **64→3 · 128→15** | 18 |

47 + 19 + 18 = 84. Of the 84, 66 are promoted (47 + 19) and 18 are upstream-native
(64→3, 128→15). `infoic_page_size_raw` is a **faithful** copy of the upstream field — zero fidelity
mismatches across all 84 rows. There is no decode bug anywhere in this pipeline; the question this
phase answers is purely semantic: which of the 84 rows' `page_size` values are evidence about a 28C
page buffer at all.

D-01: deliver a page size only where the upstream `<ic>` record's own `protocol_id` is `0x0D` —
i.e. only the 18 upstream-native rows. `classify()` arm 2 (`build_db.py:371-386`) is the promotion
that makes the other 66 of the 84 non-native, and it is exactly that promotion which disqualifies
them from D-01.

## The 15 movers and the 3 no-change rows

**The 15 movers** (upstream `0x0D`, upstream page 128, growing from today's 64-byte floor):

- ATMEL: `AT28C010,AT28C010E`, `AT28C040,AT28C040E`, `AT28LV010`, `AT28MC020`, `AT28MC040` (5)
- CATALYST (CSI): `CAT28C512`, `CAT28C010`, `CAT28C020`, `CAT28C040` (4)
- MAXWELL: `28C010,28C010T,28C011,28C011T` (1 group, 4 part numbers)
- SGS-THOMSON: `M28010` (1)
- ST: `M28010` (1)
- WED: `WE512K8`, `WME128K8` (2)
- XICOR: `X28C010` (1)

**The 3 no-change rows** (upstream `0x0D`, upstream page 64 — already equal to today's floor):

- ATMEL: `AT28MC010`
- WED: `WE128K8`, `WE256K8`

Note that `AT28MC010` (64) and `AT28C010` (128) are both upstream-native `0x0D` — the
same-density-different-page argument the existing `eeprom_28c.cpp` comment rests on is fully
preserved by D-01's rule, and both chips are in the delivered set.

## Why this condition (D-01, with its citation)

The rule is stated as a claim about **provenance, never about a part**: the `page_size` attribute
is meaningful for the algorithm that consumes it; a record filed under `0x07`/`0x0B` is not
evidence about a 28C page buffer, even when its numeric value happens to be 64 or 128.

Citation: `firestarter_app/doc/infoic-field-dictionary.md:241` — the CONFIRMED `page_size` row:
"Page-write size for EEPROM/Flash. Typically 64 or 128 bytes for 28C-family; `0` or `1` if not
applicable to the device type", itself cited to minipro `database.c#L598` @ `a8efaedc`. Pinned
upstream source: the `infoic.xml` copy at commit `a8efaedc236c1d9718bd28299dfbb99536b010ff`
(md5 `b4548e57c4f6c6c8c4f7387add03fa77`, 17,861,009 bytes; `build_db.py` reads the `INFOIC2PLUS`
section only, of the three `<database>` sections the file contains).

Two rejected directions, and what each would have delivered:

1. **Grow-only, ignoring provenance** — 17 movers. Adds CYPRESS `FM28V020` and FUJITSU
   `MB85R256H`, **both FRAM**, one of them a 3.3 V part — parts with no page buffer at all in the
   sense the AT28C-family floor exists to protect. Rejected because it hands a page size to parts
   for which the concept is meaningless.
2. **All-real-values with sentinels** — 28 movers, 13 of which rest on a `page_size` read directly
   out of a `0x07`/`0x0B` record with no corroboration. Rejected because it reintroduces exactly the
   cross-algorithm reinterpretation D-01 exists to prevent, just with a sentinel fallback bolted on.

## No attribute in infoic.xml corroborates page_size

- `write_buffer_size` looks like the corroborating field one would want, and is not: it is the
  programmer's own transfer buffer. Across the 84 rows it takes `{128×46, 32×33, 64×4, 256×1}`, and
  for AT28C256 (a promoted `0x07` row) it reads 128 while the datasheet page is 64 — the opposite
  number from what this phase's floor uses for that chip.
- `read_buffer_size` is the same *kind* of field (a programmer buffer, not a chip attribute) but
  takes a different value set entirely: `{512, 2048, 128}`.
- `pages_per_block` is 0 on all 84 rows (a NAND-oriented field, inapplicable here).
- `firestarter_app/datasheets/` holds `AT28C256.pdf` and nothing else for any `0x0D` chip, so
  "check it against the datasheet" is unavailable for all 15 movers — and unavailable for the 11
  promoted 16/32-value rows discussed below.

## The three measured non-claims (Evidence Ceiling)

### 1. No silicon claim

No AT28C part exists in operator inventory. `.planning/REQUIREMENTS.md` §Out of Scope excludes
bench validation of the page-size change. ROADMAP criterion 1's "observed to deliver 128" is
satisfied purely as a **native flush-count** assertion on a host compiler (D-09) and must never be
described, here or anywhere else in this phase, as an observation made on real hardware.

### 2. AT28C256 (gh#21) is unchanged

AT28C256 — the part named in gh#21 — is a **promoted** row: its upstream `protocol_id` is `0x07`
and its raw `page_size` is `0x0040` (64). Under D-01 it receives no emitted `page-size` at all,
keeps the existing 64-byte floor, and its wire dictionary entry is **byte-unchanged** by this
phase. This phase cannot alter AT28C256's write behaviour in any way and explains nothing about
gh#21. `0x0D` stays `UNVERIFIED`; no `support_status` value changes anywhere in this phase; and
gh#21, gh#32, gh#11, and gh#12 all stay open.

### 3. The 16/32-value floor rows: unproven, not disproven

For the 11 promoted rows whose raw `page_size` is 16 or 32 (14 upstream-`0x07` at 1, 17
upstream-`0x0B` at 1, plus the 3-at-16 and 8-at-32 groups — see the deferred todo for the full
list), the 64-byte floor's safety is **unproven**, not disproven. Their `page_size` values come
from `0x07`/`0x0B` records whose own algorithm never treats that field as a 28C page-write buffer,
so this phase can assert neither that their real page is 16 or 32, nor that 64 is safe for them.
The correct word is unproven; "overruns today" is too strong a claim and does not appear anywhere
in this phase's artifacts.

## DB-side evidence (plan 03)

### python3 tools/diff_db.py ; echo EXIT=$?

```
$ python3 tools/diff_db.py; echo EXIT=$?
========================================================================
GATE-02 Per-chip Diff Report
  Baseline: /workspaces/firestarter_app/tools/baseline/chip_database.baseline.json  (746 chips, 746 diffed)
  Current:  /workspaces/firestarter_app/tools/../firestarter/data/chip_database.json  (746 chips, 746 diffed)
========================================================================

--- CHANGED chips (744 total) ---

[RULE_VCC_MARGIN_RAIL] (56 chips)
  Phase 148 DATA-01 (D-01/D-02/D-03) — VCC margin-rail substitution.
    infoic.xml's VCC nibble 2 (VCC_VOLTAGES[0x02] = 4000 mV) is decoded FAITHFULLY —
    this is not a decode repair. The defect is semantic: minipro's vcc is the TL866's
    low-margin VCC *verify* rail, and firestarter surfaced it as the chip's operating
    supply. The substitution targets the already-decoded vdd_mv (itself an
    infoic.xml-decoded value, so nothing is invented) whenever vcc_mv lands on this
    rail: build_db.py::_VCC_MARGIN_RAIL_MV, applied post-construction.
    No other delta: exactly 56 chips move, every one 4000 -> 5000 mV, and no chip's
    vcc_mv is ever lowered by this rule (Test 3's no-decrease guard,
    tests/test_vcc_margin_rail.py).
    [VERIFIED: minipro database.c#L130-L135 @ a8efaedc —
     tl866ii_vcc_voltages[] —
     https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc/src/database.c#L130]
    [CITED: .planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md]
  Affected part_numbers (56):
    AM28C64A,AM28C64AE,AM28C64B,AM28C64BE
    AT28BV256,AT28LV256
    AT28BV64,AT28LV64
    AT28BV64B,AT28LV64B
    AT28C010,AT28C010E
    AT28C04,AT28HC04
    AT28C040,AT28C040E
    AT28C04E,AT28C04F
    AT28C16,AT28HC16,AT28HC16L
    AT28C16E,AT28C16F
    AT28C17
    AT28C17E,AT28C17F
    AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L
    AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L
    AT28C64B,AT28HC64B,AT28HC64BF
    AT28C64E,AT28C64F
    AT28LV010
    AT28MC010
    AT28MC020
    AT28MC040
    AT28PC64,AT28PC64E
    CAT28C010
    CAT28C020
    CAT28C040
    CAT28C16A,CAT28C16AI
    CAT28C17A
    CAT28C256,CAT28C257
    CAT28C512
    CAT28C64A,CAT28C65
    CAT28C64B
    CAT28LV256
    CAT28LV64,CAT28LV65
    FM28V020
    HN58C256AP
    28C010,28C010T,28C011,28C011T
    UPD28C04
    UPD28C256
    UPD28C64
    KM28C64
    KM28C64A,KM28C65A
    M28010
    M28010
    M28256
    WE128K8
    WE256K8
    WE512K8
    WME128K8
    X2804A,X2804AI
    X2816A
    X2816B,X2816C
    X28256,X28C256
    X2864AP
    X28C010
    X28C64(NonStandard),X28HC64(NonStandard)
    X28C64,X28HC64
    X88C64P,X88C64S

[PGSZ_PAGE_SIZE] (2 chips)
  Phase 94 PGSZ-01 / CR-01 — datasheet-sourced per-chip page_size field added.
    Generalizes flash4 page sizing from the firmware capacity heuristic
    (flash4_page_size(mem_size)) to a DB-supplied per-chip value (emit-when-present).
    Only chips with a [CITED:] datasheet entry in build_db.py _PAGE_SIZE_BY_PART
    get this field. Chips without a cited datasheet continue using the heuristic.
      W29C040,W29C042: page_size=256 added.
        [CITED: firestarter/datasheets/0x05-FLASH-AMD-STD/W29C040.pdf §6.2
                'Every page contains 256 bytes of data.']
      W29C020,W29C020C,W29C022: page_size=128 added.
        [CITED: firestarter/datasheets/0x05-FLASH-AMD-STD/W29C020.pdf §6.2
                'Every page contains 128 bytes of data.' + FEATURES '128 bytes per page']
    No other fields changed. No dispatch / algorithm / VPP delta.
    [VERIFIED: Phase 94 Plan 02 — PGSZ-01/02/03 requirements + 94-RESEARCH.md A1/A2]
  Affected part_numbers (2):
    W29C020,W29C020C,W29C022
    W29C040,W29C042

[PROV01_PROTECT_METADATA] (686 chips)
  Phase 136.1 PROV-01 — flags bit 14/15 + raw page_size decode added to the
    programming block. Three new keys, decoded directly from each <ic> element's
    own flags/page_size attributes (never a cross-reference or token match):
      protect_off_before: bool(flags & 0x4000) — MP_OFF_PROTECT_BEFORE.
      protect_on_after:   bool(flags & 0x8000) — MP_PROTECT_AFTER (the same bit
        sdp_capability.py's SDP_CAPABLE_TOKENS transcription encodes, now
        committed as an explicit per-chip field for the first time).
      infoic_page_size_raw: the raw, un-curated upstream page_size attribute —
        PROV-06's corroborating axis only, NOT the same field as the existing
        datasheet-curated programming.page_size (PGSZ_PAGE_SIZE rule above), and
        not consulted by any ALLOW/REFUSE decision anywhere in this codebase.
    Universal: every upstream-decoded chip gains all three keys; the two
    tools/extra_chips.json supplement entries (2516/2532) do NOT, since they
    bypass this decode loop entirely (VAR-05 post-decode merge).
    Metadata only — no algorithm / pinout / vpp / electrical.type delta; the
    84/43/41 SDP ALLOW/REFUSE partition (tests/test_sdp_db_invariant.py) is
    unchanged.
    [VERIFIED: minipro src/database.c#L39-L50 @ a8efaedc236c1d9718bd28299dfbb99536b010ff —
     https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc236c1d9718bd28299dfbb99536b010ff/src/database.c#L39]
    [CITED: doc/infoic-field-dictionary.md CONFIRMED bit 14/15 row;
     .planning/phases/136.1-sdp-partition-provenance/136.1-01-PLAN.md;
     .planning/phases/136.1-sdp-partition-provenance/136.1-01-BLAST-RADIUS.md]
  Affected part_numbers (686):
    M8720
    AS29F002B
    AS29F002T
    AM27128A
    AM2716
    AM2716B
    AM27256
    AM2732,AM2732A
    AM2732B
    AM27512
    AM2764A
    AM27C010
    AM27C020
    AM27C040
    AM27C080
    AM27C128
    AM27C256
    AM27C512
    AM27C64
    AM27H010,AM27HB010
    AM27H256
    AM27LV010
    AM27LV020,AM27LV020B
    AM27LV040
    AM27LV080
    AM28C16A
    AM28C17A
    AM28F010
    AM28F010A
    AM28F020
    AM28F020A
    AM28F256
    AM28F512
    AM29F002B,AM29F002BB
    AM29F002BT,AM29F002T
    AM29F002NB,AM29F002NBB
    AM29F002NBT,AM29F002NT
    AM29F010,AM29F010B
    AM29F040,AM29F040B
    A27020
    A276308
    A276308A
    A278308
    A278308A
    A290011T
    A290011U
    A29001T
    A29001U
    A290021T
    A290021U
    A29002T
    A29002U
    A29010
    A29040,A29040A,A29040B,A29040C
    A29512
    A29512A
    A29L040,A29L040A
    27CX010
    27CX256
    AE29F1008
    AE29F2008
    AE29F4008
    AE49F2008
    SMJ27C010A
    SMJ27C040
    SMJ27C128
    SMJ27C256
    SMJ27C512
    AT27256
    AT2732A
    AT27BV010,AT27LV010,AT27LV010A
    AT27BV020,AT27LV020,AT27LV020A
    AT27BV040,AT27LV040,AT27LV040A
    AT27BV256,AT27LV256A,AT27LV256R
    AT27BV512,AT27LV512A,AT27LV512R
    AT27C010,AT27C010L
    AT27C011
    AT27C020
    AT27C040
    AT27C080
    AT27C128
    AT27C256
    AT27C256R
    AT27C512
    AT27C512R
    AT27HC256,AT27HC256L
    AT27HC256R,AT27HC256RL
    AT29BV010A,AT29LV010A
    AT29BV020,AT29LV020
    AT29BV040,AT29LV040
    AT29BV040A,AT29LV040A
    AT29C010A
    AT29C020
    AT29C040
    AT29C040A
    AT29C256
    AT29C257
    AT29C512
    AT29LV256
    AT29LV512
    AT49BV001,AT49BV001A,AT49LV001
    AT49BV001AN,AT49BV001N,AT49LV001N
    AT49BV001ANT,AT49BV001NT,AT49LV001NT
    AT49BV001AT,AT49BV001T,AT49LV001T
    AT49BV002,AT49BV002A,AT49LV002
    AT49BV002AN,AT49BV002N,AT49LV002N
    AT49BV002ANT,AT49BV002NT,AT49LV002NT
    AT49BV002AT,AT49BV002T,AT49LV002T
    AT49BV010,AT49HBV010,AT49HLV010,AT49LV010
    AT49BV020,AT49LV020
    AT49BV040,AT49BV040A,AT49BV040B,AT49LV040
    AT49BV040T,AT49LV040T
    AT49BV512,AT49LV512
    AT49F001,AT49F001A
    AT49F001AN,AT49F001N
    AT49F001ANT,AT49F001NT
    AT49F001AT,AT49F001T
    AT49F002,AT49F002A
    AT49F002AN,AT49F002N
    AT49F002ANT,AT49F002NT
    AT49F002AT,AT49F002T
    AT49F010,AT49HF010
    AT49F020
    AT49F040,AT49F040A
    AT49F040T
    AT49F512
    CAT27010
    CAT27128A
    CAT27256,CAT27HC256I
    CAT27512
    CAT2764A
    CAT27C16
    CAT27HC256
    CAT28F001P-B
    CAT28F001P-T
    CAT28F010
    CAT28F020
    CAT28F256
    CAT28F512
    EN29F002AB,EN29F002B
    EN29F002ANB,EN29F002NB
    EN29F002ANT,EN29F002NT
    EN29F002AT,EN29F002T
    EN29F010
    EN29F040,EN29F040A
    EN29F512
    EN29LV040A
    PM29F002B
    PM29F002T
    PM29F004B
    PM29F004T
    PM39F010
    PM39F020
    PM39F040
    CY27C010,CY27H010
    CY27C020
    CY27C040
    CY27C128
    CY27C256
    CY27C512
    CY27H256
    CY27H512
    DS1220(RW)
    DS1220(TEST)
    DS1225(RW)
    DS1225(TEST)
    DS1230AB(RW),DS1230Y(RW)
    DS1230AB(TEST),DS1230Y(TEST)
    DS1230W(RW3.3V)
    DS1230W(TEST3.3V)
    DS1245AB(RW),DS1245Y(RW)
    DS1245AB(TEST),DS1245Y(TEST)
    DS1245W(RW3.3V)
    DS1245W(TEST3.3V)
    DS1249AB(RW),DS1249Y(RW)
    DS1249AB(TEST),DS1249Y(TEST)
    DS1249W(RW3.3V)
    DS1249W(TEST3.3V)
    DS1250AB(RW),DS1250Y(RW)
    DS1250AB(TEST),DS1250Y(TEST)
    DS1250W(RW3.3V)
    DS1250W(TEST3.3V)
    DPV27C101
    DPV27C256
    DPV27C512
    F49B002UA
    EN27C010
    EN27C512
    EN29F002AB,EN29F002ANB,EN29F002B,EN29F002NB
    EN29F002ANT,EN29F002AT,EN29F002NT,EN29F002T
    EN29F010
    EN29F040,EN29F040A
    EN29F512
    EN29LV040A
    XL2804A
    XL2816A,XLE28C16A,XLS28C16A
    XLE2865A,XLS2865A
    XLE28C16B,XLS28C16B
    XLE28C256,XLS28C256
    XLE28C64A,XLS28C64A
    XLE28C64B,XLS28C64B
    FM27C010
    FM27C040
    FM27C256,NM27C256,NM27LC256,NMC27C256B,NMC27C256Q,NMC87C257Q,NMC87C257V
    FM27C512,NM27C512,NM27LC512,NM27LV512,NM27P512,NMC27C512A,NMC27C512Q
    NM27C010,NM27LC010,NM27LV010,NM27P010,NMC27C010
    NM27C020,NM27LV020,NM27P020
    NM27C040,NM27LV040,NM27P040
    NM27C128,NMC27C128B,NMC27C128C
    NM27C64Q,NM27LC64,NMC27C64Q
    NMC2732
    NMC27C16
    NMC27C16B,NMC27C16BQ
    NMC27C16Q
    NMC27C32,NMC27C32E,NMC27C32EH,NMC27C32H,NMC27C32Q
    NMC27C32B,NMC27C32BQ
    MB85R256H
    MBM27128
    MBM2716
    MBM27256
    MBM2732,MBM2732A,MBM27C32,MBM27C32A
    MBM2764
    MBM27C1000P,MBM27C1000
    MBM27C1001
    MBM27C128P
    MBM27C2000P,MBM27C2000
    MBM27C2001
    MBM27C256A
    MBM27C4001
    MBM27C512
    MBM27C64
    MBM28F010
    MBM29F002B
    MBM29F002T
    MBM29F040
    GR27128
    GR27256
    GR27512
    GR2764
    HN27128AG,HN27128AP
    HN27256G,HN27256P
    HN27512G,HN27512P
    HN27C101AG,HN27C101AP,HN27C101AFP,HN27C101ATT,HN27C101G,HN27C101P
    HN27C256AG,HN27C256AFP,HN27C256AP,HN27C256HG,HN27C256HP,HN27C256HFP
    HN27C256G
    HN27C301AG,HN27C301AP,HN27C301AFP
    HN27C301G
    HN27C4001G
    HN27C512G
    HN27C64FP
    HN27C64G
    HN28F101P,HN28F101FP
    HT27C010
    HT27C020
    HT27C040
    HT27C512
    HT27LC010
    HT27LC020
    HT27LC040
    HT27LC512
    HY27C64
    HY29F002T
    HY29F040
    HY29F040A,HY29F040T
    HY27C64
    HY29F002T
    HY29F040
    HY29F040A,HY29F040T
    ICE27C010,ICE27LC010
    ICE27C020,ICE27LC020
    ICE27C512,ICE27LC512
    27CX010
    27CX256
    27CX010
    27CX256
    IM29F001B
    IM29F001T
    IM29F002B
    IM29F002T
    IM29LV004B
    IM29LV004T
    27128,D27128
    27128A,D27128A,D27128B
    2732,2732A,M2732,M2732A
    27512
    2764
    2764A
    27C010,27C010A
    27C020
    27C040
    27C128
    27C256
    27C512
    87C257
    D27011
    D27256,M27256
    D27C011
    M2716,M2716M
    M28F256
    P27256
    P28F001BX-B
    P28F001BX-T
    P28F010
    P28F020
    P28F256A
    P28F512
    IS27C010,IS27HC010
    IS27C020,IS27HC020
    IS27C256,IS27HC256
    IS27C512,IS27HC512
    IS27LV010
    IS27LV020
    IS27LV256
    IS27LV512
    IS28F010
    IS28F020
    LG28C010
    LG28C020
    LG28C040
    LST28001
    LST28002
    LST28004
    MX26C1000
    MX26C2000
    MX26C4000
    MX26LV004B
    MX26LV004T
    MX26LV040
    MX27C1000
    MX27C1000A
    MX27C2000
    MX27C2000A
    MX27C256
    MX27C4000
    MX27C4000A
    MX27C512
    MX27C8000
    MX27C8000A
    MX27L1000
    MX27L2000
    MX27L256
    MX27L4000
    MX27L512
    MX28F1000P
    MX28F2000P
    MX28F2000T
    MX29F001B
    MX29F001T
    MX29F002B
    MX29F002NB
    MX29F002NT
    MX29F002T
    MX29F004B
    MX29F004T
    MX29F022B
    MX29F022NB
    MX29F022NT
    MX29F022T
    MX29F040,MX29F040C
    MX29LV002CB
    MX29LV002CT
    MX29LV002NCB
    MX29LV002NCT
    27C128
    27C256,27LV256
    27C32A
    27C512
    27C512A
    27C64,27LV64
    27HC256,27HC256L
    27HC64
    2804
    2816
    2817
    28C04A
    28C04AF
    28C16A
    28C16AF
    28C17A
    28C17AF
    28C256,28C256F
    28C64A
    28C64AF
    28C64B
    28LV64A
    M5L27256K
    M5M27C101K
    M5M27C128
    M5M27C256K
    M5M28F101,M5M28F101A
    V29C31001B
    V29C31001T
    V29C31002B
    V29C31002T
    V29C31004B
    V29C31004T
    V29C51001B
    V29C51001T
    V29C51002B
    V29C51002T
    V29C51004B
    V29C51004T
    V29LC51000
    V29LC51001
    V29LC51002
    UPD27128
    UPD27256
    UPD27512
    UPD2764,UPD2764C,UPD2764D
    UPD27C1001A
    UPD27C128
    UPD27C2001
    UPD27C256A
    UPD27C4001
    UPD27C512
    UPD27C8001
    NX29F010
    NM27C010
    NM27C020
    NM27C040
    NM27C128,NMC27C128B,NMC27C128C
    NM27C256,NM27LC256,NMC27C256B,NMC27C256Q,NMC87C257Q,NMC87C257V
    NM27C512,NM27LC512,NM27P512,NMC27C512A,NMC27C512Q
    NM27C64Q,NMC27C64Q
    NM27LC010,NM27P010,NMC27C010
    NM27LC64
    NM27LV010
    NM27LV020
    NM27LV040
    NM27LV512
    NM27P020
    NM27P040
    NMC2732
    NMC27C16
    NMC27C16B
    NMC27C16Q
    NMC27C32B
    MSM27C1000
    MSM27C2000
    MSM27C201
    MSM27C401
    MSM27C512
    27C010
    27C040
    27C256
    27C512
    PM29F002B
    PM29F002T
    PM29F004B
    PM29F004T
    PM39F010
    PM39F020
    PM39F040
    PT28C010
    PT28C020
    PT28C040
    FM1208
    FM1608
    FM16W08
    FM1808,FM1808B,FM18W08
    FM18L08
    ETC2716,M2716
    ETC2732
    M23C1001
    M23C2001
    M23C4001
    M27128A
    M27256
    M2732A
    M27512
    M2764A
    M27C1000
    M27C1001,M27V101
    M27C2001,M27V201,M27W201
    M27C256B
    M27C4001,M27V401
    M27C512,M27V512
    M27C64A
    M27C801
    M28C64,M28C64A
    M28C64-xxW
    M28F101
    M28F201
    M28F256
    M28F512,M28F512B,M28F010
    M29F002B,M29F002BB
    M29F002BNB
    M29F002BNT,M29F002NT
    M29F002BT,M29F002T
    M29F010B
    M29F040B
    M29F512B
    M48T02,M48T12,M48Z02,M48Z12
    M48T08,M48T08Y,M48T18,M48T58,M48T58Y,M48Z08,M48Z08Y,M48Z18,M48Z58,M48Z58Y
    M48T128V,M48T129V,M48Z128V,M48Z129V
    M48T128Y,M48T129Y,M48Z128Y,M48Z129Y
    M48T35AV,M48Z35V,M48Z35AV
    M48T35AY,M48Z35,M48Z35Y,M48Z35AY
    M48T512V,M48T513V,M48Z512V
    M48T512Y,M48T513Y,M48Z512Y
    M48T59,M48T59Y,M48Z59,M48Z59Y
    M48T59V,M48Z59V
    M87C257
    M87C257(8D)
    ST27128A
    ST27256
    ST2764A
    ST27C256,TS27C256
    TS27C64A
    AM29F002B,AM29F002BB
    AM29F002BT,AM29F002T
    AM29F002NB,AM29F002NBB
    AM29F002NBT,AM29F002NT
    AM29F010,AM29F010B
    AM29F040,AM29F040B
    MBM29F002B
    MBM29F002T
    MBM29F040
    SST27SF010
    SST27SF020
    SST27SF256
    SST27SF512
    SST27VF010
    SST27VF020
    SST27VF256
    SST27VF512
    SST28LF040,SST28LF040A,SST28VF040,SST28VF040A
    SST28SF040,SST28SF040A
    SST29EE010
    SST29EE020
    SST29EE512
    SST29LE010,SST29VE010
    SST29LE020,SST29VE020
    SST29LE512,SST29VE512
    SST29SF010
    SST29SF020
    SST29SF040
    SST29SF512
    SST29VF010
    SST29VF020
    SST29VF040
    SST29VF512
    SST37VF010
    SST37VF020
    SST37VF040
    SST37VF512
    SST39LH010,SST39VF010
    SST39LH020,SST39VF020
    SST39LH040
    SST39LH512,SST39VF512
    SST39SF010,SST39SF010A
    SST39SF020,SST39SF020A
    SST39SF040
    SST39SF512,SST39SF512A
    SST39VF040,SST39VF040A
    ETC2716,M2716
    ETC2732
    M27128A
    M27256
    M2732A
    M27512
    M2764A
    M27C1001,M27V101,M27W101
    M27C2001,M27V201,M27W201
    M27C256B
    M27C256B(2)
    M27C4001,M27V401,M27W401
    M27C512,M27V512,M27W512
    M27C64A
    M27C801
    M28C64,M28C64A
    M28C64-xxW
    M28F101
    M28F201
    M28F256
    M28F512,M28F512B,M28F010
    M28LV64
    M29F002B,M29F002BB
    M29F002BNB
    M29F002BNT,M29F002NT
    M29F002BT,M29F002T
    M29F010B
    M29F040B
    M29F512B
    M48T02,M48T12
    M48T08,M48T08Y,M48T18,M48T58,M48T58Y
    M48T128V,M48T129V
    M48T128Y,M48T129Y
    M48T35AV
    M48T35AY
    M48T512V,M48T513V
    M48T512Y,M48T513Y
    M48T59,M48T59Y
    M48T59V
    M87C257
    M87C257(8D)
    ST27128A
    ST27256
    ST2764A
    ST27C256
    TS27C256
    TS27C64A
    F29C31004B,S29C31004B
    F29C31004T,S29C31004T
    F29C51001B,S29C51001B
    F29C51001T,S29C51001T
    F29C51002B,S29C51002B
    F29C51002T,S29C51002T
    F29C51004B,S29C51004B
    F29C51004T,S29C51004T
    F29LC51000
    F29LC51001
    F29LC51002
    S29C31001B
    S29C31001T
    S29C31002B
    S29C31002T
    6116
    61256,62256
    61512,62512
    6164,6264
    628128
    628256
    628512
    BQ4010YMA(RW)
    BQ4010YMA(TEST)
    BQ4011LYMA(RW3.3V)
    BQ4011LYMA(TEST3.3V)
    BQ4011YMA(RW)
    BQ4011YMA(TEST)
    BQ4013LYMA(RW3.3V)
    BQ4013LYMA(TEST3.3V)
    BQ4013YMA(RW)
    BQ4013YMA(TEST)
    BQ4014LYMA(RW3.3V)
    BQ4014LYMA(TEST3.3V)
    BQ4014YMA(RW)
    BQ4014YMA(TEST)
    BQ4015LYMA(RW3.3V)
    BQ4015LYMA(TEST3.3V)
    BQ4015YMA(RW)
    BQ4015YMA(TEST)
    SMJ27C128,TMS27C128,TMS27PC128
    SMJ27C256,TMS27C256,TMS27PC256
    SMJ27C512,TMS27C512,TMS27PC512
    TMS2716
    TMS2732A
    TMS2764
    TMS27C010
    TMS27C010A,TMS27PC010A
    TMS27C020,TMS27PC020
    TMS27C040,TMS27PC040
    TMS27C64,TMS27PC64
    TMS28F010,TMS28F010A,TMS28F010B
    TMS28F020
    TMS87C257
    TC54256AF,TC54256AP
    TC57256D
    TC57512AD
    W24010
    W24020
    W24040
    W24256,W24257A
    W24512
    W2464,W2465
    W27C01,W27C010,W27E01,W27E010,W27L01,W27L010
    W27C02,W27C020,W27E02,W27E020,W27L02
    W27C04,W27C040,W27E040
    W27C257
    W27C512,W27E512
    W27E257
    W29C010,W29C011,W29C011A,W29EE010,W29EE012
    W29C512,W29EE512
    W29EE011
    W39F010
    W39L040A
    W49F002,W49F002A,W49F002B,W49F002U
    W49F020
    WS27C010F
    WS27C010L
    WS27C128F
    WS27C256L
    WS27C512F,WS27C512L
    WS27C64
    WS57C128FB
    WS57C256F

--- COMPOUND changes (58) — algo+other deltas ---

  These chips have a primary cause PLUS a secondary field delta that
  is itself explained by a known rule. Both are surfaced so a
  co-bundled change is not silently masked by the primary rationale.

  28C010,28C010T,28C011,28C011T [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  AM28C64A,AM28C64AE,AM28C64B,AM28C64BE [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28BV256,AT28LV256 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28BV64,AT28LV64 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28BV64B,AT28LV64B [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28C010,AT28C010E [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  AT28C04,AT28HC04 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28C040,AT28C040E [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  AT28C04E,AT28C04F [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28C16,AT28HC16,AT28HC16L [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28C16E,AT28C16F [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28C17 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28C17E,AT28C17F [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28C64B,AT28HC64B,AT28HC64BF [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28C64E,AT28C64F [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  AT28LV010 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  AT28MC010 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  AT28MC020 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  AT28MC040 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  AT28PC64,AT28PC64E [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  CAT28C010 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  CAT28C020 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  CAT28C040 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  CAT28C16A,CAT28C16AI [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  CAT28C17A [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  CAT28C256,CAT28C257 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  CAT28C512 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  CAT28C64A,CAT28C65 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  CAT28C64B [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  CAT28LV256 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  CAT28LV64,CAT28LV65 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  FM28V020 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  HN58C256AP [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  KM28C64 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  KM28C64A,KM28C65A [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  M28010 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  M28010 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  M28256 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  UPD28C04 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  UPD28C256 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  UPD28C64 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  W29C020,W29C020C,W29C022 [PGSZ_PAGE_SIZE] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  W29C040,W29C042 [PGSZ_PAGE_SIZE] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  WE128K8 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  WE256K8 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  WE512K8 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  WME128K8 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  X2804A,X2804AI [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  X2816A [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  X2816B,X2816C [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  X28256,X28C256 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  X2864AP [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  X28C010 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.page_size, programming.protect_off_before, programming.protect_on_after
  X28C64(NonStandard),X28HC64(NonStandard) [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  X28C64,X28HC64 [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after
  X88C64P,X88C64S [RULE_VCC_MARGIN_RAIL] + secondary: programming.infoic_page_size_raw, programming.protect_off_before, programming.protect_on_after

--- NEW chips (0) — expected Rule 1 unblock (DIP24_2816 + algo=0x0D) ---

--- MISSING chips (0) ---

PASS: all 744 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
EXIT=0
```

**Correction to `149-CONTEXT.md` section Integration Points.** That section's "Research item" note
read: "the 18 rows already classify under `PROV01_PROTECT_METADATA` in today's 744-changed-chip
report, so how `_classify_diff` combines a second changed field on an already-classified chip must
be measured, not assumed." Measured now: this prediction is **false**. All 18 rows classify under
`RULE_VCC_MARGIN_RAIL` (Phase 148's own bucket, priority 4 in `_classify_diff`'s chain) because
their `vcc_mv` also sits on the 4000 mV margin rail -- they were **never** under
`PROV01_PROTECT_METADATA`. They do **not** move to `PGSZ_PAGE_SIZE`; that bucket stays at its
pre-149 count of **2** (the datasheet-curated `_PAGE_SIZE_BY_PART` rows only).
`programming.page_size` merely joins each of the 18 rows' existing `RULE_VCC_MARGIN_RAIL`
compound-secondary list. The census is otherwise exactly invariant: `EXIT=0`, **744** changed
chips explained, **0** unexplained, **0** new, **0** missing, and the bucket triple
**686** / **56** / **2** (`PROV01_PROTECT_METADATA` / `RULE_VCC_MARGIN_RAIL` / `PGSZ_PAGE_SIZE`).

### RED — the wire golden goes red by design (D-17)

```
$ python3 -m pytest tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden -o addopts="" -q; echo EXIT=$?
F                                                                        [100%]
=================================== FAILURES ===================================
_______________________ test_live_capture_matches_golden _______________________

    def test_live_capture_matches_golden() -> None:
        doc = json.loads(_GOLDEN.read_text(encoding="utf-8"))
        recorded = doc["records"]
        live = _capture_wire_dicts(_REAL_DB)
>       assert recorded == live, (
            "live 746-chip wire-dict capture drifted from "
            "tests/golden/wire_dict_baseline.json; "
            "if this is a legitimate wire-value change, Phase 148 is "
            "specifically forbidden to make it (D-14) -- a legitimate future "
            "wire change must re-capture the golden deliberately and say in the "
            "commit message which chips and which keys moved. "
            f"Diff: {_describe_record_diff(recorded, live)}"
        )
E       AssertionError: live 746-chip wire-dict capture drifted from tests/golden/wire_dict_baseline.json; if this is a legitimate wire-value change, Phase 148 is specifically forbidden to make it (D-14) -- a legitimate future wire change must re-capture the golden deliberately and say in the commit message which chips and which keys moved. Diff: changed={'ATMEL|AT28C010,AT28C010E|22': ['page-size'], 'ATMEL|AT28C040,AT28C040E|25': ['page-size'], 'ATMEL|AT28LV010|34': ['page-size'], 'ATMEL|AT28MC010|35': ['page-size'], 'ATMEL|AT28MC020|36': ['page-size'], 'ATMEL|AT28MC040|37': ['page-size'], 'CATALYST(CSI)|CAT28C010|13': ['page-size'], 'CATALYST(CSI)|CAT28C020|14': ['page-size'], 'CATALYST(CSI)|CAT28C040|15': ['page-size'], 'CATALYST(CSI)|CAT28C512|12': ['page-size'], 'MAXWELL|28C010,28C010T,28C011,28C011T|0': ['page-size'], 'SGS-THOMSON|M28010|18': ['page-size'], 'ST|M28010|15': ['page-size'], 'WED|WE128K8|0': ['page-size'], 'WED|WE256K8|1': ['page-size'], 'WED|WE512K8|2': ['page-size'], 'WED|WME128K8|3': ['page-size'], 'XICOR|X28C010|5': ['page-size']}
E       assert {'ALI(Acer)|M... 0, ...}, ...} == {'ALI(Acer)|M...00, ...}, ...}
E         
E         Omitting 728 identical items, use -vv to show
E         Differing items:
E         {'CATALYST(CSI)|CAT28C512|12': {'algorithm': 13, 'bus-config': {'bus': [0, 1, 2, 3, 4, 5, ...], 'rw-pin': 20}, 'chip-id': 0, 'flags': 0, ...}} != {'CATALYST(CSI)|CAT28C512|12': {'memory-size': 65536, 'algorithm': 13, 'pin-count': 32, 'vpp_mv': 12000, ...}}
E         {'CATALYST(CSI)|CAT28C040|15': {'algorithm': 13, 'bus-config': {'bus': [0, 1, 2, 3, 4, 5, ...], 'rw-pin': 20}, 'chip-id': 0, 'flags': 0, ...}} != {'CATALYST(CSI)|CAT28C040|15': {'memory-size': 524288, 'algorithm': 13, 'pin-count': 32, 'vpp_mv': 12000, ...}}
E         {'...
E         
E         ...Full output truncated (17 lines hidden), use '-vv' to show

tests/test_wire_dict_equivalence.py:157: AssertionError
=========================== short test summary info ============================
FAILED tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden
1 failed in 0.31s
EXIT=1
```

The golden itself (`tests/golden/wire_dict_baseline.json`) is **preserved, byte-unchanged** by this
regeneration. This is the pre-149 capture going red against a live capture that now carries 18 more
`page-size` values -- exactly what D-17 predicts before Task 3 resolves it. The failure's own
`Diff: changed={...}` names exactly the 18 record keys `tests/golden/wire_dict_expected_deltas_149.json`
commits as data, never a re-baseline.

### GREEN — golden plus exactly the 18 named deltas

```
$ python3 -m pytest tests/test_wire_dict_equivalence.py -o addopts="" -q; echo EXIT=$?
.....                                                                    [100%]
5 passed in 1.69s
EXIT=0
```

`test_live_capture_matches_golden_plus_the_149_deltas` replaces the old bare-equality test (renamed,
not edited in place) with four assertions: the golden's own page-size-carrying record set is
exactly Phase 148's original two (anti-laundering); every delta key exists in the golden and is not
already present there (non-vacuity); `len(deltas) == 18` exactly; and golden-plus-deltas equals the
live capture, reusing `_describe_record_diff` unchanged in the failure message.
`test_wire_key_union_is_exactly_nine_keys` passes untouched -- the union stays 9, since `page-size`
was already in it.

### python3 -m pytest tests/test_page_size_invariants.py -o addopts="" -q

```
$ python3 -m pytest tests/test_page_size_invariants.py -o addopts="" -q; echo EXIT=$?
...........                                                              [100%]
11 passed in 0.10s
EXIT=0
```

This is the D-07 exhaustive host-side proof: 11 legs over the generated database (84-row 0x0D bucket
count, the 18 named native carriers split 15x128/3x64, 20 total carriers, an exhaustive
power-of-two-in-range check, a separate provenance check, AT28C256's non-change,
`support_status` byte-identity across all 84 rows against the committed baseline, the
`extra_chips.json` back door, and two synthetic non-vacuity legs). **What it does NOT cover:** it
iterates the *generated* `chip_database.json`, so a `~/.firestarter/database.json` operator
override could supply an unvalidated `page_size` that the host still emits over the wire -- the two
carry-sites in `database.py` are truthiness guards (`if page_size_val:`), not provenance checks, and
this test never sees an override file at all. That gap is precisely why the **firmware** half of
D-07 (plan 04's cheap silent fallback to the AT28C page-size floor for any non-power-of-two or
out-of-range value) is load-bearing rather than belt-and-braces.

### The 18 delivered rows

Grouped by manufacturer, upstream-native `protocol_id == 0x0D`, per-row page value:

- **ATMEL** (6): `AT28C010,AT28C010E` -> 128; `AT28C040,AT28C040E` -> 128; `AT28LV010` -> 128;
  `AT28MC010` -> **64**; `AT28MC020` -> 128; `AT28MC040` -> 128.
- **CATALYST(CSI)** (4): `CAT28C010` -> 128; `CAT28C020` -> 128; `CAT28C040` -> 128;
  `CAT28C512` -> 128.
- **MAXWELL** (1 group, 4 part numbers): `28C010,28C010T,28C011,28C011T` -> 128.
- **SGS-THOMSON** (1): `M28010` -> 128.
- **ST** (1): `M28010` -> 128.
- **WED** (4): `WE128K8` -> **64**; `WE256K8` -> **64**; `WE512K8` -> 128; `WME128K8` -> 128.
- **XICOR** (1): `X28C010` -> 128.

Totals: 6 + 4 + 1 + 1 + 1 + 4 + 1 = 18 rows; 15 at 128, 3 at 64 (`AT28MC010`, `WE128K8`, `WE256K8`).

`AT28MC010` (64) and `AT28C010` (128) are **both** upstream-native `0x0D` at the same 131072-byte
density -- so the same-density-different-page argument the existing `eeprom_28c.cpp` comment rests
on is fully preserved by this rule, and both chips are in the delivered set.

### The three stale host comments corrected (X-5)

- **`firestarter_app/tools/build_db.py`, `_PAGE_SIZE_BY_PART`'s header comment** -- named a firmware
  heuristic function by a name that was renamed away in v1.19 Phase 104 and does not exist in
  `firestarter/src/` or `firestarter/include/` today, and carried an unqualified correctness
  adjective this repo's claim gates treat as a violation shape. Corrected to state that absent
  chips omit the field, and that for `algorithm: 13` specifically the firmware falls back to its own
  named AT28C page-size floor constant (Phase 149 D-10 names it; this map is not extended to cover
  that fallback, per `REQUIREMENTS.md` section Out of Scope / DATA-04).
- **`firestarter_app/tools/build_db.py`, the `raw_page_size` decode comment** -- claimed the raw
  field "is not consulted by any ALLOW/REFUSE decision anywhere in this codebase". Falsified by this
  phase's emit arm, which now reads it directly for the 18 native rows. Corrected to say the raw
  field remains the raw provenance axis (PROV-06's corroborating axis) and is now *also* the value
  source for the 18 upstream-native `0x0D` rows -- the two fields stay deliberately distinct keys
  even where their values coincide.
- **`firestarter_app/firestarter/database.py` and `constants.py`** -- both named the same
  non-existent `flash4_page_size` firmware function, and `constants.py`'s sync note additionally
  claimed a firmware key (`key_page_size`) that does not exist yet (Phase 149 plan 04 creates it;
  plan 05's `test_json_key_parity.py` is the enforcing test) and misattributed the wire emit site to
  `eprom_operations.py`, which never mentions page size at all -- the real site is `database.py`'s
  `convert_to_programmer`. All three corrected with **zero executable change** to `database.py`
  (D-02's "zero host runtime code change" holds; verified by a comment-only `git diff`).

### Why an apparent duplicate is not one

`programming.infoic_page_size_raw` and `programming.page_size` are deliberately distinct keys, and
this phase does not collapse them. `infoic_page_size_raw` stays untouched as the raw upstream
provenance axis for **all** decoded rows (universal, Plan 136.1-01); `diff_db.py`'s
`PROV01_PROTECT_METADATA` rule keys on that raw field, not on `page_size`. For the 18 rows this
phase adds `page_size` to, the two fields hold **identical** values (the emit arm literally copies
`raw_page_size` into `page_size` when the provenance condition holds) -- which is exactly what makes
the provenance rule auditable after the fact: anyone can diff the two fields on any row and see
whether that row's `page_size` (if present) matches its own raw provenance, or was supplied instead
by the separate, disjoint `_PAGE_SIZE_BY_PART` curated table (both of whose entries are upstream
`0x05`, never `0x0D`).

## Firmware seam evidence (plan 04)

### Wire-key pre-check

Before writing the parser, the firmware source was grepped for any prior page-size handling
(`git -C firestarter grep -n "page.size\|page_size\|PAGE_SIZE" src/json_parser.c include/firestarter.h`).
Result: **no `page-size` wire key, no `page_size` handle field, and no parser dispatch entry existed
anywhere in the firmware before this plan.** The only pre-existing artifact was the hardcoded 64-byte
floor constant in `eeprom_28c.cpp`. This corroborates the project note that the v1.16
`primitives.{h,cpp}` recompose — which would have carried a wire page-size key — was never merged.
Full transcript: `149-FW-TRANSCRIPTS.md` §"Wire-key pre-check".

### Six edit points

1. **`firestarter_handle_t` gains `uint16_t page_size`** (`include/firestarter.h`), beside `chip_id`
   — the same in-struct width precedent as `vpp_mv`.
2. **`src/json_parser.c` gains the wire key** — a PROGMEM string `key_page_size` bound to the hyphen
   form `"page-size"` (the internal database key uses an underscore; a PROGMEM string against the
   underscore form would silently never match), a `key_parsers[]` row dispatching it, and a forward
   declaration alongside its siblings.
3. **`get_page_size`** uses the one-line `extract_int` form (`get_chip_id`'s model), not the Phase 44
   clamp form — validation stays in the 0x0D handler, keeping `json_parse` algorithm-agnostic.
4. **The per-command reset** — `handle->page_size = 0;` in `json_parse`'s reset block, beside
   `chip_id`. `firestarter_handle_t handle;` is a single file-scope global with no per-command
   `memset`, so without this reset a 128 parsed for one chip would persist into the next command.
5. **`eeprom28c_page_mask(uint16_t)`** (`src/proms/eeprom_28c.cpp`) resolves the validated mask —
   power of two in `[1, AT28C_PAGE_SIZE_MAX]`, else `AT28C_PAGE_SIZE_FALLBACK`, with the zero check
   ordered before the subtraction.
6. **The flush test** in `eeprom28c_write_execute` changes from `(address + 1) % PAGE_SIZE` to
   `(address + 1) & page_mask`, with `page_mask` hoisted once above the per-byte loop.

Also deleted: the dead `json_init()` (definition and declaration) — its token count was `sizeof()` on
a pointer parameter, zero call sites in `src/`. Zero flash saving counted toward any budget
(`--gc-sections` is on; the jsmn functions are also called from `firestarter.cpp`).

### The flush-count oracle — RED then GREEN

The oracle counts every entry to the mocked `firestarter_get_data` in `test_val_eeprom28c.cpp`
(`s_get_data_calls`) — the only seam every flush-path read in production goes through; the bus
recorder captures register writes only, never reads, and caps at 256 entries. For a clean write,
`calls == 2 * flushes + data_size` (the double read per flush in `eeprom28c_wait_for_page_write`'s
clean poll, plus one read per buffer byte in `eeprom28c_verify_page_readback`). At `data_size = 128`:
page 64 gives 2 flushes → **132**; page 128 gives 1 flush → **130**.

Five cases were added with the mask still using the modulo form, and the delivered-128 case was
**seen to fail**: `Expected 130 Was 132`. The unconditional 64-byte modulo produced 132 regardless of
`handle->page_size` — proving the modulo form never consulted it. Every other case (absent/64/96/2048)
already expected 132, which the pre-mask code also produced, so criterion 1 rests specifically on the
128 case, the only one whose expected value differs from what the unchanged code already gave.

After the mask landed, all five cases pass: **130** for delivered 128, **132** for absent / explicit
64 / non-power-of-two (96) / out-of-range (2048). Full RED and GREEN transcripts, including the exact
commands and literal output: `149-FW-TRANSCRIPTS.md` §"RED" and §"GREEN".

### The resolve site — mechanism-corrected, intent-satisfied

D-06's literal text says the mask is resolved "at write-INIT". It is instead resolved once, as a
hoisted local, at the top of `eeprom28c_write_execute` — above the per-byte loop, never per byte.
Recorded here as **mechanism-corrected / intent-satisfied**, never as failed, in the same voice as
`configure_eeprom28c`'s existing LOCK-04 precedent comment. Three measured reasons:

1. `--policy merge05` requires `ram_used` **exactly unchanged**; a second stored field (on the handle,
   or a file-scope static) would cost RAM the exemption does not authorise.
2. `eeprom28c_write_init` has an early `return` on a chip-ID mismatch, so a mask resolved after it
   would be only conditionally initialised.
3. Every existing native case in `test_val_eeprom28c.cpp` calls `configure_memory(&h)` then
   `h.firestarter_operation_main(&h)` and never `firestarter_operation_init` — a mask resolved in
   `write_init` would leave every `test_fix06_*` case at mask 0 (flushing every byte), silently
   changing `test_fix06_page_boundary_window_readback`'s two-window geometry.
   `write_execute`'s top is reached by every existing case and every new one.

D-06's substance — resolved once, never per byte, no runtime modulo by a variable divisor in the hot
path — is preserved exactly.

### The corrected floor comment

The header comment on `eeprom_28c.cpp`'s floor constant (renamed `AT28C_PAGE_SIZE_FALLBACK`, D-10)
now reads, in substance: the AT28MC010 (64) vs AT28C010 (128) same-density argument is preserved
verbatim (D-01 re-verified it, both chips are in the delivered set); the floor's safety for the 66
rows this phase leaves on it is **unproven**, not disproven, because their `page_size` comes from
records filed upstream under other algorithms and their real page cannot be asserted either; and the
per-chip delivery path (`infoic.xml -> build_db.py -> chip_database.json -> wire -> json_parser.c ->
the mask resolver`) is now landed, **software-proven and unvalidated on silicon** — closing the old
comment's "delivered by a separate, DEFERRED phase ... not yet inserted into ROADMAP.md" sentence.

### Validation bound (`AT28C_PAGE_SIZE_MAX`, 512)

The validation ceiling is the board-invariant literal **512**, not the per-board data-buffer
constant (512 on `uno`/`uno328pb`/`native`, 1024 on `leonardo`). Using the per-board constant would
make the validation contract board-dependent — one rule that is really two — and a native test could
never observe the `leonardo` bound at all, so coverage would be partial by construction. 512 makes the
contract identical on all four build environments, makes the native test's coverage of it total, and
is still at or above the largest page any of the 746 database rows carries (256).

### D-08 — `flash_5v_page.cpp` is a deliberate non-change

`flash_5v_page.cpp` is byte-unchanged by this plan
(`git -C firestarter diff --quiet src/proms/flash_5v_page.cpp` passes). Its `mem_size`-derived band
table stays exactly as-is, FIX-04 frozen, so `W29C020`/`W29C040` keep riding the heuristic **even
though the host already sends them `page-size`**. Recorded explicitly so a reader does not assume the
new wire key governs both handlers — those two rows look wired but are not.

### `NUMBER_JSNM_TOKENS` headroom, unchanged

`include/json_parser.h`'s `NUMBER_JSNM_TOKENS` stays **64** — untouched by this plan. The worst-case
wire dictionary in the committed golden costs 42 jsmn tokens with the new `page-size` key included
(measured in plan 03); headroom stays 22 tokens.

### A pre-existing latent instance, not fixed here

The two Phase 44 read-timing knobs (`read_settling_us`, `read_strobe_us`) are absent from
`json_parse`'s reset block and carry the identical stale-value defect one field over from the one this
plan closes for `page_size`. Not fixed here — fixing it would perturb
`test_read_timing_fields_default_zero_when_absent` — and filed as a pending todo by plan 07.

### The proof's honest ceiling

The entire flush-count proof above is a host-compiler call count at `data_size = 128`, produced by
`[env:native]` — a build with `DATA_BUFFER_SIZE = 512`, ArduinoFake stubs, and no clock (`delay()` is
unstubbed in the native trace stubs). It is **software-proven and unvalidated on silicon**: it proves
nothing about an AVR build's own runtime, nothing about timing, and nothing about whether any physical
AT28C die accepts a 128-byte page load. No AT28C part was involved anywhere in this plan, `0x0D` stays
`UNVERIFIED`, and no `support_status` entry changed.

## Cross-repo parity evidence (plan 05)

### The two-way parity result

`tests/test_json_key_parity.py` asserts, over `firestarter/src/json_parser.c`'s PROGMEM key-string
block and `key_parsers[]` dispatch table:

- **Declared and dispatched, not merely present.** `JSON_KEY_PAGE_SIZE` (`"page-size"`) is asserted
  string-equal to the firmware's `key_page_size` PROGMEM string, AND that identifier is asserted to
  appear inside the `key_parsers[]` initializer body — the specific hole a naive presence check
  misses is a string that exists but is never wired into dispatch.
- **Python → firmware, total.** All 3 `JSON_KEY_*` constants on `firestarter.constants` (discovered
  by introspection, not a hardcoded name list) are asserted present as firmware PROGMEM key strings.
- **Firmware → Python, with a named, completeness-checked exemption tuple.** `3 Python constants + 8
  named firmware exemptions = 11 extracted keys.` The 8 exemptions (`memory-size`, `address`,
  `flags`, `chip-id`, `pin-count`, `pulse-delay`, `vpp_mv`, `algorithm`) are asserted to be
  individually present in the firmware source (no stale entries) and, together with the 3 mapped
  constants, to cover the full 11-key extracted set exactly — no third, unclassified bucket.
- **Fails closed, not open, on a rename.** `fw_path("src", "json_parser.c")` is resolved at module
  scope; a present-but-renamed target raises `MissingScanTargetError` rather than skipping. A
  dedicated leg asserts exactly this by patching the module's path constant to a nonexistent file
  under a present repo.

### The two planted-RED messages

`planted_json_parser_key_string_drift.c` (page-size PROGMEM string spelled `page_size`, the wire's
hyphen replaced by the internal database key's underscore):

```
RAISED: no PROGMEM key string equal to JSON_KEY_PAGE_SIZE ('page-size') was found in
.../planted_json_parser_key_string_drift.c -- extracted key strings: [... 'page_size' ...]
```

`planted_json_parser_undispatched_key.c` (page-size PROGMEM string spelled correctly, `key_parsers[]`
row omitted):

```
RAISED: the page-size key string 'page-size' is declared as 'key_page_size' but that identifier does
not appear inside the key_parsers[] dispatch body -- a PROGMEM string that is declared but never
dispatched exists on the wire and never matches anything a host sends.
```

Both messages were observed directly (outside any pytest wrapper) and are mutually distinguishable —
each plant's leg asserts the OTHER plant's phrase is absent from its own message. Both plants inject
via `monkeypatch.setattr` on the module-scope path constant only; the real
`firestarter/src/json_parser.c` blob hash and the sibling repo's porcelain state were confirmed
unchanged before and after both runs. Full transcripts: `149-PARITY-TRANSCRIPTS.md`.

### The skip-leg transcript — this is the state app CI runs in

`tests/fw_presence.py` binds `FW_ROOT` at import, so the skip condition can only be proved in a
subprocess with `FIRESTARTER_FW_ROOT` pointed at a directory with no `.git` marker. That run: the 8
`@requires_fw` legs report **SKIPPED** with the absent-firmware reason text (not ERROR, not FAILED);
`test_planted_key_string_drift_is_detected` and `test_planted_undispatched_key_is_detected` are not
in the skipped set — they run and pass, because they read committed fixtures, never the sibling
checkout; the run's exit code is 0. **`firestarter_app`'s own standalone CI has no sibling firmware
checkout**, so this is precisely the state the module's live legs are in on every push, and the two
planted legs are the only part of this gate app CI ever exercises. Full transcript, including the
whole-`tests/`-suite run (1639 passed, 58 skipped, exit 0): `149-PARITY-TRANSCRIPTS.md` §"The
empty-FW_ROOT skip leg (D-18)".

### The inventory entry and the two stale counts

`tests/scan_paths.py`'s `CROSS_REPO_TEST_PATHS` gained `ScanPathEntry("src/json_parser.c",
("test_json_key_parity.py",))` — `src/json_parser.c` was cross-repo-scanned by this phase's plan 04
and this plan without ever being named in the committed inventory `scan_paths.py` exists to make
exhaustive. Two stale prose counts in that module's own docstring, both reading **6** where the
tuple had held **7** entries since Phase 147 added `src/firestarter.cpp`, are corrected to **8** in
this diff, with the surrounding sentences reworded to stay true. `tests/test_scan_paths_resolve.py`'s
`is_relative_to` name-collision guard passes for the new entry, and its exact-count assertion on the
11-file tool-resolver population (Population B) is untouched.

### `constants.py:144`'s "Firmware sync" note

That note has read "Firmware sync: `json_parser.c` (`key_page_size`)" since plan 03 corrected its
wording — a claim this project's own kickoff record measured as **false** at the time (no such key
existed in the firmware before plan 04). It is now a true claim, and — as of this plan —
**enforced**: `test_json_key_parity.py` fails the suite if the firmware string, the Python constant,
or the dispatch-table wiring between them ever drifts.

### The honest ceiling

This gate proves the two repositories agree on a **key string** and that the string is wired into
the firmware's dispatch table — **layout agreement**, nothing more. It does not prove the C getter
(`get_page_size`) stores that value into the right struct field, does not prove the 0x0D handler
reads that field correctly, and proves nothing about hardware. Like every other artifact this phase
produces, it is **software-proven and unvalidated on silicon**: no AT28C part was involved anywhere
in this plan, `0x0D` stays `UNVERIFIED`, and no `support_status` entry changed.

## Post-change cold measurement and MERGE-05 funding (plan 06)

### The cold three-env table

Procedure identical to plan 01's pre-edit capture (`rm -rf .pio/build/<env>` then one
uninterrupted `pio run -e <env>`), captured after the page-size seam (plan 04) and the
cross-repo parity gate (plan 05) both landed. All three ended `[SUCCESS]` with **zero**
`warning:` lines and unchanged `flash_total`/`ram_total`.

| env | pre-edit cold flash (plan 01) | post-change cold flash | Δ vs pre-edit | BASE-01 flash | Δ vs BASE-01 | pre-edit cold RAM | post-change cold RAM | Δ vs pre-edit | BASE-01 RAM | Δ vs BASE-01 |
|---|---|---|---|---|---|---|---|---|---|---|
| uno | 24920 | 25130 | +210 | 24824 | +306 | 1573 | 1575 | +2 | 1573 | +2 |
| uno328pb | 24970 | 25180 | +210 | 24874 | +306 | 1579 | 1581 | +2 | 1579 | +2 |
| leonardo | 27002 | 27212 | +210 | 26906 | +306 | 2014 | 2016 | +2 | 2014 | +2 |

**Seam flash cost `N = 210` B** (the BASE-01 delta of +306 B minus the already-admitted 96 B
Phase 145 defect-fix exemption), uniform on all three AVR targets. **Seam RAM cost `M = 2` B**,
also uniform, matching the predicted cost of the single `uint16_t page_size` field added to the
one file-scope `firestarter_handle_t` global (AVR aligns scalars to 1 byte, so there is no
padding to absorb it). Full transcripts, including the cold warning run: `149-SIZE-TRANSCRIPTS.md`.

### v1.31's MERGE-05 band breach, named

**Leonardo's MERGE-05 flash band is 0 B, and it was already fully breached before this phase
started.** v1.31 Phase 145's `eprom_internal_program_pulse()` fix added +96 B to all three AVR
targets against BASE-01, consuming the entire `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` exemption
with nothing left over. So leonardo's remaining MERGE-05 flash headroom **before this phase**
was **exactly 0 bytes** — the band admits nothing, and the pre-existing exemption admits
nothing further. This phase's own +210 B could not be absorbed by anything already on the
books; it had to be funded by a wholly new allowance or the gate would stay red permanently.

### Funding: two new, separately-named, SHA-attributed exemptions (D-12)

`firestarter/scripts/check_size_baseline.py` gained:

- **`MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = 210`** (flash), attributed to this phase's own
  firmware commits `58c6a3c` ("add page-size wire key, handle field and per-command reset") and
  `28bf089` ("validated bitwise page mask at the 0x0D flush boundary").
- **`MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2`** (RAM), attributed to the single
  `uint16_t page_size` field commit `58c6a3c` added to the global `handle`.

`MERGE05_UNO_CLASS_FLASH_BAND` stays exactly **64**, `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` stays
exactly **96**, and `scripts/baseline/size_baseline_base01.json` is **byte-unchanged** — verified
by `git diff --quiet` in the plan's own gate, not merely stated. `_merge05_flash_allowance`
returns a 5-tuple `(band, defect_exemption, seam_exemption, allowance, band_label)`, never a
summed 4-tuple, so both consumers (the FAIL arm and `main()`'s PASS-line builder) print the full
three-term decomposition — e.g. `band 0 B + defect-fix exemption 96 B + page-size-seam exemption
210 B` — rather than a single widened number. A companion `_merge05_ram_allowance(env)` resolves
the new RAM tolerance as the sole reader of the RAM constant.

**Three alternatives were considered and rejected, for both exemptions, exactly as they were for
the Phase 145 exemption they sit beside:**
1. **NOT a re-anchor of BASE-01.** Its own `re_anchor_note` already records the lesson this would
   repeat: a green `--policy merge05` run after a re-anchor means the anchor moved, not that
   flash growth stayed inside the original band. BASE-01's `avr_targets` stay byte-unchanged: uno
   24824, uno328pb 24874, leonardo 26906.
2. **NOT a widening of `MERGE05_UNO_CLASS_FLASH_BAND` or the leonardo 0 B band.** Either would
   silently admit unrelated future growth and destroy the tripwire.
3. **NOT a shrink of the seam (or of the RAM field).** The wire key, the handle field, the
   per-command reset and the validated mask are all load-bearing for PGSZ-01/PGSZ-02; trimming
   them to fit a band that predates the seam's own existence is the wrong incentive. A narrower
   `uint8_t` log2-exponent field was considered for the RAM cost and rejected on the same
   reasoning: the RAM clause's tolerance was zero either way, so a narrower field only changes
   this exemption's size, not whether it is needed.

### New allowances and leonardo's remaining headroom, as a number

| env | band | defect-fix exemption | page-size-seam exemption | **effective flash allowance** | RAM tolerance |
|---|---|---|---|---|---|
| leonardo | 0 | 96 | 210 | **306 B** | 2 B |
| uno / uno328pb | 64 | 96 | 210 | **370 B** | 2 B |

The post-change cold flash delta against BASE-01 is **exactly +306 B on leonardo** — precisely
equal to its new allowance. **Leonardo's remaining MERGE-05 flash headroom after this exemption
is exactly 0 bytes** — same shape as the Phase 145 admission it sits beside: the exemption funds
exactly what was measured, with zero spare margin, so the very next byte of unaccounted flash
growth on leonardo will fail the gate. Leonardo's raw **physical** free flash (unrelated to the
MERGE-05 band, a separate number) is `28672 - 27212 = 1460` bytes.

### RED, GREEN and the re-armed tripwire

- **RED** (before either exemption existed): `--policy merge05` against BASE-01 on the real cold
  logs exited **1**, naming `allowance of 96 B` on leonardo and a `ram_used` delta on every env.
- **GREEN** (after both exemptions landed): the same command against the same cold logs exits
  **0**, with every env's PASS line showing the full three-term flash decomposition and the RAM
  decomposition (e.g. `leonardo(flash=27212/28672[+306<=306=band0+exempt96+seam210],ram=2016/2560[+2<=2=seam2])`).
- **Re-armed tripwire:** all three planted fixtures
  (`planted_size_baseline_policy_{leonardo_growth,uno_over_band,ram_moved}.log`) were re-derived
  to exactly one byte past the **new** allowances (leonardo flash 27213, uno flash 25195, uno RAM
  1576) and each was run directly against the gate — all three **observed** to exit 1, not merely
  asserted to. `python3 -m pytest tests/test_check_size_baseline.py -q` passes 14/14 with every
  affected leg (5 repaired plus 1 new `test_base01_is_not_re_anchored_by_the_new_exemption` leg)
  present and green.

Full literal transcripts for every command above: `149-SIZE-TRANSCRIPTS.md`.

### Warnings, measured cold, nothing lowered

`check_build_warnings.py --rebuild`, run after removing all three native build directories by
hand (`_rebuild_native` does not clean), reports AVR macro-redefinition counts of **0/0/0** (the
`== 0` rule) and both pinned native watermarks (`native`, `native_nodevtools`) holding at exactly
**1166**, measured **cold** — no watermark is lowered by this plan.

### The honest ceiling

Every figure in this section is a measurement of the compiled binary's size and the build's
warning count — the only evidence in this phase that is about actual target code. It says
nothing about runtime behaviour on a real board: no AT28C part was involved in taking any of
these measurements, `0x0D` stays `UNVERIFIED`, and no `support_status` entry changed. Like every
other artifact this phase produces, the change these two exemptions fund is
**software-proven and unvalidated on silicon**.

## Baseline update and closing record (plan 07)

`scripts/baseline/size_baseline.json` — this project's live default baseline (D-14) — is
re-anchored to plan 06's cold post-change figures: uno 25130/1575, uno328pb 25180/1581, leonardo
27212/2016 (flash used / RAM used), transcribed byte-for-byte from the committed cold logs, never
re-measured warm. Both pinned native envs (`native`, `native_nodevtools`) move from 141 to 151
cases/succeeded; `suites` stays 17 and `envs_agree` stays true.

**The stale `firmware_tree_sha` is corrected (X-3).** `size_baseline.json`'s
`meta.firmware_tree_sha` had recorded `3d8ec49…`, the root tree of Phase 144 commit `6cc4795` — a
tree that predates Phase 145's +96 B fix the same file's own figures already included, so the
field and the figures beside it were mutually inconsistent as a reproducibility anchor. It is
replaced with `c6349d22bb15a0e2a3f1e95af946bfe28a8582ad`, the root tree of firmware commit
`581cff6` — the tree the cold logs in this phase were actually measured against.

**Both size gates are green simultaneously against the re-anchored baseline**: the default
byte-identity mode, and `--policy merge05` against the untouched `size_baseline_base01.json`
(BASE-01 stays byte-unchanged at uno 24824, uno328pb 24874, leonardo 26906 — not re-anchored a
third time).

**Orchestrator-directed severance, stated plainly — this plan does not narrate plan 07 as having
passed exactly as written.** Re-anchoring the live default baseline necessarily invalidated four
pre-existing `tests/test_check_size_baseline.py` legs that assert default-mode output against the
frozen pre-149 `captured_build_*.log` / `captured_test_native*.log` fixtures. Plan 07's own first
attempt — leaving those four legs failing and recording the gap as an accepted limitation — was
overridden by the orchestrator: a phase whose entire theme is honest measurement cannot close with
a failing firmware suite. The resolution actually landed is **severance**, the same mechanism the
Phase 145 debug session already used once in this exact file: a new `captured_build_v132_*.log`
fixture family (transcribed from the same committed cold post-change logs, never re-derived warm)
plus a matching planted-regression fixture, three legs re-pointed at that new family, and the two
native summary fixtures updated in place. `check_size_baseline.py`, `size_baseline_base01.json`,
`src/`, `include/`, the pre-149 `captured_build_*.log` trio and `merge05_base01_anchor_*.log` all
stay byte-unchanged. `python3 -m pytest tests/ -o addopts="" -q` now reports **315 passed, 0
failed** — every test in the suite passing, not merely a documented, accepted gap. The full
account of this override lives in `149-07-SUMMARY.md`'s own "Deviations from Plan" section.

Four pending todos were filed with measured provenance, none of them describing the underlying
question as answered by this phase: the 66-row floor's unproven safety
(`promoted-0x0d-rows-keep-the-64-byte-floor.md`), the two FRAM parts riding the `0x0D` handler by
pinout promotion (`fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md`), the deferred runtime
INFO log naming the effective page size (`runtime-info-log-naming-the-effective-page-size.md`),
and the Phase-44 read-timing knobs' own missing `json_parse` reset
(`phase-44-read-timing-knobs-missing-json-parse-reset.md`). The folded, dead-code
`remove-dead-json-init-sizeof-pointer-bug.md` todo was removed as a tracked deletion after
confirming `json_init()` is genuinely gone from `src/`.

## What ships, and what does not

**What ships:** 15 AT28C010-class parts (the movers named above) now write using their datasheet
128-byte page instead of the 64-byte floor. 3 more (`AT28MC010`, `WE128K8`, `WE256K8`) are
corroborated at 64 and are demonstrably unchanged in behaviour. The 66 rows arriving at `0x0D` by
promotion, and `AT28C256` specifically, are untouched — byte-identical on the wire, still on the
64-byte floor. The firmware falls back to its own named floor constant whenever the field is
absent, non-power-of-two, or out of range, in every one of those cases.

**What does not ship:** no silicon evidence of any kind; `0x0D` stays `UNVERIFIED`; no
`support_status` value is altered for any chip; gh#21, gh#32, gh#11 and gh#12 all stay open; and no
bench validation of this change exists or is planned — `REQUIREMENTS.md` §Out of Scope excludes it
by name. Every figure and every test result in this document is a compiler-time or host-side
measurement. Taken as a whole, the page-size seam this phase delivers is
**software-proven and unvalidated on silicon**.

## The changelog line, mirrored

The `firestarter_app/README.md` subsection added by this plan, quoted verbatim so it can be
reviewed here alongside the artifact it describes:

> ### AT28C010-class parts now write with a 128-byte page (software-proven, unvalidated on silicon)
>
> The database now delivers a per-chip page size over the existing JSON command path for the 18
> chips whose upstream record is natively protocol `0x0D`; 15 of them move from the firmware's
> 64-byte floor to their datasheet 128-byte page, and 3 are corroborated at 64 and therefore
> unchanged. Firmware that receives no page-size field keeps using the conservative 64-byte floor,
> so an older host against this firmware still issues legal write cycles.
>
> **This does alter write behaviour for those 15 parts** — unlike the VCC correction above, which
> did not — and it is stated as **software-proven and unvalidated on silicon**. No physical AT28C
> part was tested. **AT28C256 is unaffected**: its upstream record is not natively `0x0D` and its
> page size was already 64, so nothing about its behaviour changes and nothing here explains the
> failure reported against it. Protocol `0x0D` remains `UNVERIFIED` and no chip's support status
> changed.
>
> Writes to those 15 parts issue half as many page-write cycles, so they may complete faster;
> nothing else about the command surface changes.

## The deferred work, and where it is filed

Four pending todos, filed by plan 07, carry this phase's own deferred findings forward with their
measured provenance rather than closing the questions here:

- `.planning/todos/pending/promoted-0x0d-rows-keep-the-64-byte-floor.md` — the 66 rows arriving at
  `0x0D` by promotion keep the 64-byte floor; their real page size is unproven, not disproven, and
  neither datasheet curation nor a new corroboration axis exists yet to settle it.
- `.planning/todos/pending/fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md` — `FM28V020`
  and `MB85R256H`, both FRAM, ride the `0x0D` handler by pinout promotion; a classification
  question, not a page-size one.
- `.planning/todos/pending/runtime-info-log-naming-the-effective-page-size.md` — a runtime INFO log
  naming the effective page size, so a future community `dev test` report can show the granularity
  its firmware used; declined here on flash cost (D-09).
- `.planning/todos/pending/phase-44-read-timing-knobs-missing-json-parse-reset.md` — the two Phase
  44 read-timing knobs carry the identical stale-value defect this phase closed for `page_size`,
  one field over; not fixed here because it would perturb an existing, passing test.
