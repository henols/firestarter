# Phase 149 Plan 03 -- DB Transcripts

Evidence for the D-17 seen-to-fail RED (the wire golden must go red by design when the
provenance-keyed emit arm adds `page-size` to 18 records) and the X-1 `diff_db` census
invariance GREEN, captured from `/workspaces/firestarter_app` immediately after
`python3 tools/build_db.py` regenerated `firestarter/data/chip_database.json` with the
provenance-keyed emit arm from Task 1.

## RED -- the golden goes red by design (D-17)

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

The failure's own `Diff: changed={...}` dict names exactly 18 record keys, each with `['page-size']`
as its only changed key -- the same 18 keys Task 3's committed
`tests/golden/wire_dict_expected_deltas_149.json` enumerates. The golden file itself
(`tests/golden/wire_dict_baseline.json`) is **not modified** by this regeneration -- this is the
pre-149 capture going red against a live capture that now carries 18 more `page-size` values, which
is precisely what D-17 predicts. Task 3 resolves this RED by renaming the test and asserting
"golden plus exactly these 18 named deltas equals live" instead of bare equality; it does not touch
the golden file.

## GREEN -- diff_db census invariance (X-1)

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

**X-1 finding, stated as measured fact:** the 18 rows classify under `RULE_VCC_MARGIN_RAIL`
(Phase 148's own bucket, priority 4 in `_classify_diff`'s chain) -- they were **never** in
`PROV01_PROTECT_METADATA` and they do **not** move to `PGSZ_PAGE_SIZE`. `PGSZ_PAGE_SIZE` stays at
**2**, unchanged from before this plan. `149-CONTEXT.md`'s own "Research item" note (Integration
Points) predicted the 18 rows "already classify under `PROV01_PROTECT_METADATA` in today's
744-changed-chip report" -- that prediction is measured **false**: they classify under
`RULE_VCC_MARGIN_RAIL`. This is recorded as a **correction to `149-CONTEXT.md` section Integration
Points**, not an error in this plan's own work.

Exactly 18 of the 56 `RULE_VCC_MARGIN_RAIL` compound rows above carry `programming.page_size` in
their secondary-field list (grep count of the literal string `programming.page_size` in the
transcript above is 19 -- 1 is the rule-description prose on `PROV01_PROTECT_METADATA`'s own
paragraph, not a per-row line; the remaining 18 are the per-row compound entries), and they are
exactly the 18 named rows: `28C010,28C010T,28C011,28C011T` (MAXWELL); `AT28C010,AT28C010E`;
`AT28C040,AT28C040E`; `AT28LV010`; `AT28MC010`; `AT28MC020`; `AT28MC040` (all ATMEL); `CAT28C010`;
`CAT28C020`; `CAT28C040`; `CAT28C512` (all CATALYST(CSI)); `M28010` (SGS-THOMSON); `M28010` (ST);
`WE128K8`; `WE256K8`; `WE512K8`; `WME128K8` (all WED); `X28C010` (XICOR).
