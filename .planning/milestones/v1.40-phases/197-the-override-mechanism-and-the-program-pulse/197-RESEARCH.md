# Phase 197: The override mechanism and the program pulse - Research

**Researched:** 2026-09-18
**Domain:** Python database-generator design (`firestarter_app/tools/build_db.py`), datasheet evidence, test-golden maintenance
**Confidence:** HIGH on everything measured against live code, live data and in-repo datasheets. The
only LOW items are flagged explicitly in `## Assumptions Log`.

---

## Executive Summary

Five of CONTEXT.md's fourteen locked decisions rest on claims that do not survive measurement. All
five are reported below with the evidence, in the section **`## Contradictions With Locked
Decisions`**, which the planner must read before writing a single task. In brief:

1. **D-07 does not do what it says.** Deleting `_AT28C_DIP24_NAMES` flips **zero** rows to
   `supported`. The nine rows stay `adapter-required` because a *second, different* mechanism — the
   HARDWARE-DAMAGE GUARD at `:468` — already marks exactly those nine. The name list only overwrites
   a reason string. The 9-vs-10 split is not arbitrary: it is upstream's `flags & 0x10` erasable bit,
   measured exactly.
2. **D-08 understates its effect.** FM1608 changes **two** emitted fields, not one:
   `electrical.type` FRAM→SRAM *and* `electrical.vcc_mv` 3300→5000.
3. **D-10's "evidence is already on disk" is false for the gh#70 row.** `MBM27C1001.pdf` covers
   `MBM27C1001` only — the string `27C1000` appears zero times in it. The MBM27C1000 datasheet does
   exist, as an attachment on gh#70; it is not in the repo. Two of the three named datasheets are
   not even git-tracked.
4. **D-13's "10 rows change" is wrong.** Measured against a full simulated regeneration: **13 rows
   change, and zero `support_status` values change.**
5. **D-14's test list is wrong in both directions.** Of the three legs it names, **none** actually
   goes red. Of the five tests that *do* go red, it names one. It misses
   `tests/test_wire_dict_equivalence.py` entirely — a layered golden that needs a new
   `wire_dict_expected_deltas_197.json` file and a count bump.

D-01, D-02, D-04, D-05, D-06, D-09, D-11 and D-12 are all **confirmed by measurement**, several of
them with stronger evidence than CONTEXT.md claimed. D-09 in particular is proven twice: the
substitution regenerates the database **byte-identically**, and the identity is exact for every
non-negative integer, not just powers of two.

**Primary recommendation:** Structure the plan in this order — (1) hoist the decoded values into
named locals so an override has something real to substitute (there is no row dict at the D-03
insertion point today); (2) land the loader and its fail-closed legs with unit tests in `tests/`
using `from tools import ...`; (3) do the NMOS move and the D-09 derivation, both of which must
regenerate byte-identically; (4) do the pulse corrections; (5) re-derive the two golden fixtures.
Route D-07 back to the operator before touching the damage guard.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**The override file contract**

- **D-01:** A row is identified by **`MANUFACTURER/ALIAS`** — e.g. `FUJITSU/MBM27C1000`.
  Measured: manufacturer+alias is unique across all 746 rows with **zero** collisions, while bare
  alias collides on **152** of 953 aliases, and 234 rows carry a comma-joined `part_number` that no
  datasheet or reporter ever uses. — **Reversibility:** costly — the key is the file's public shape
  and phases 198, 199 and 200 all write entries into it; changing it later rewrites every entry.

- **D-02:** **One entry targets exactly one row.** No multi-target entries. The NMOS correction
  therefore becomes 6 entries rather than 3, and each states the datasheet that justifies *that*
  row. This is deliberate: the present `NMOS_TRUE_VPP_MV` applies Intel datasheet values to
  SGS-THOMSON and ST rows silently, and one-entry-one-row makes that impossible to repeat. It also
  makes a 217-row pulse sweep cost 217 datasheets, which is the intended deterrent.
  — **Reversibility:** reversible — widening to multi-target later is additive.

- **D-03:** An override **substitutes the decoded input, not the emitted output.** The generator's
  own rules then run on the overridden value: the 25 V ceiling check that derives `support_status`
  (`build_db.py:591-600`), the `vcc_mv`-from-`vdd_mv` rewrite (`:705`), and the `page_size`
  power-of-two validation. `support_status` stays derived and is never written by hand. Rejected:
  post-decode merge like `extra_chips.json`, because an overridden `vpp_mv` of 30000 would then ship
  `support_status: supported` — the exact silent fleet-scale fault this milestone exists to kill.
  — **Reversibility:** one-way — the generated database is consumed by the firmware wire protocol
  and by `chip_resolver`; a later switch to output substitution would silently un-derive
  `support_status` for every overridden row with no test able to see it.

- **D-04:** OVR-03's recorded prior value is **asserted against the live decode**; a mismatch fails
  the build. Decided by Claude on project precedent, not asked: `interpret_timing` raises rather than
  masking, the `page_size` validation raises, and OVR-04 already requires fail-closed. This makes the
  recorded value load-bearing instead of rotting prose, and subsumes OVR-04's no-op rule as the
  special case where the recorded value equals the override value.

- **D-05:** **Only decoded values may be overridden.** Operator, verbatim: *"only decoded values can
  be overridden, and the things in the code must be solved in some better way."* The file carries no
  support verdicts and no policy. Every non-decoded hardcode gets a real resolution (D-06, D-07),
  not a new home.

**Hardcode dispositions — all three leave `build_db.py`, only one moves into the file**

- **D-06:** `NMOS_TRUE_VPP_MV` (`build_db.py:87`) → **6 field overrides** on `electrical.vpp_mv`.
  Its 3 entries currently reach 6 rows (INTEL/SGS-THOMSON/ST for M2716; INTEL/SGS-THOMSON/ST for
  M2732A, with the INTEL row matching both M2732 and M2732A). Under D-01 each entry names one row,
  which **dissolves the "highest VPP wins" tie-break entirely** — that rule exists only because bare
  alias is ambiguous within a row. Generated values are unchanged by the move.

- **D-07:** `_AT28C_DIP24_NAMES` (`:506`) → **deleted, not moved.** Operator decision: no adapter is
  needed at all; Rev 2.2 and above supports these parts in hardware, earlier revisions with a wire,
  and that distinction is not modelled. The hardcode was hiding a defect: **19 rows share
  `pin_count 24` + `algorithm 13` + `pinout DIP24_2816`, and the name list marks 9 of them
  `adapter-required` while leaving 10 `supported`** — `AT28C16` refused while `X2816A`,
  `CAT28C16A`, `AM28C16A` and Microchip's plain `2816` are offered. `DIP24_2816` is fully defined in
  `pinouts.json` with no `vpp-pin`. **Effect: 9 rows flip to `supported`.**
  — **Reversibility:** costly — it makes nine previously-refused parts writable; reinstating the
  refusal means re-adding a list and re-reddening the tests below.

- **D-08:** `_ETYPE_RELABEL = {"FM1608": "FRAM"}` (`:573`) → **deleted, not moved.** Raised by the
  operator, then confirmed by measurement: **every host site treats `SRAM` and `FRAM` identically** —
  `eprom_operations.py:2288` (`etype in ("SRAM","FRAM")`), `eprom_info.py:390`
  (`_etype not in {"SRAM","FRAM"}`), and `database.py:368`/`:576` (`in ("EEPROM","Flash/EEPROM")`,
  which neither satisfies). The label changes nothing but a display string. It was also arbitrary:
  **algorithm 40 holds 34 rows, all SRAM-class, and FM1608 is the only one relabelled** while its
  Ramtron siblings `FM1208`, `FM16W08`, `FM1808` and `FM18L08` — equally FRAM parts — read `SRAM`.
  **Effect: FM1608's `electrical.type` flips `FRAM` → `SRAM`.**

- **D-09:** `_PGM_ON_PIN31_MAX_SIZE = 262144` (`:148`) → **derived away this phase**, from
  `code_memory_size` arithmetic. Operator chose derivation over naming it under OVR-06. The claim the
  constant encodes is "pin 31 is PGM when the part does not need A18", which is
  `(mem_size - 1).bit_length() <= 18`. That is provably equivalent to `mem_size <= 262144` for every
  power-of-two size in the database, so **a byte-identical regeneration is the proof.**
  — **Reversibility:** one-way in effect — it governs the `DIP32_27C020` vs `DIP32_STD` fork at
  `:241` (pin 31 = PGM vs A18). A wrong derivation puts programming voltage on an address line.
  The byte-identical regeneration is not optional.

**The pulse correction**

- **D-10:** Phase 197 corrects **the rows the three in-repo Fujitsu datasheets cover** —
  `datasheets/MBM27C1001.pdf`, `datasheets/MBM27C4001.pdf`, `datasheets/MBM27128.pdf` — up to 9 of
  Fujitsu's 12 algorithm 7/8 rows. Evidence is already on disk; nothing new to source. All three
  community reports live in this same 12-row block, so it pre-stages gh#66 (Phase 198) and gh#71
  (Phase 199). Rejected: MBM27C1000 alone (leaves MBM27C1001 wrong with its datasheet in the repo),
  and all 12 in-repo datasheets (pulls other algorithms into a phase scoped to the program pulse).

- **D-11:** The **"microseconds for all protocols" decode rule is expected to survive**, and
  PULSE-01's finding is expected to be "infoic carries a family default, not a per-part value."
  Evidence: the generator's reading is `[VERIFIED: minipro database.c#L866 @ a8efaedc]`; the observed
  distribution across algorithm 7/8 is 10/20/50/100/200/500/1000 µs, which already reads as plain
  microseconds; and no uniform multiplier maps 100→500 without making 1000→5000. This is the
  expectation the researcher must **falsify or confirm**, not an instruction to skip the work.

- **D-12:** **217 of 297 algorithm 7/8 rows carry `pulse_duration_us: 100`.** The rows this phase
  does not correct are recorded as a measured inventory in the phase directory and filed to the
  backlog. Decided by Claude, not asked — it is a bookkeeping location, not a design choice.

**Requirement amendments this discussion forces**

- **D-13: OVR-05 no longer holds as written.** It says the three hardcodes *move into the override
  file* and *the generated database is unchanged by the move*. Both clauses fail: only
  `NMOS_TRUE_VPP_MV` moves (D-06); the other two are deleted as defects (D-07, D-08); and the
  database changes by **10 rows** — 9 `support_status` flips plus FM1608's `electrical.type`. The
  planner must restate OVR-05 to match, and the acceptance evidence becomes a regeneration diff
  showing exactly those 10 rows and nothing else.

- **D-14: three test legs assert the retired behaviour** and must be rewritten, not deleted-around:
  `tests/test_sdp_capability.py:506` (*"all nine adapter-required parts are refused by capability"*),
  `tests/test_chip_resolver.py:87` (AT28C04 must raise `ChipNotImplementedError`), and
  `tests/test_sdp_honesty.py:59`. `tests/test_diagnostic_report.py` uses `"adapter-required"` only as
  a synthetic mock value and needs no change. For FM1608, the two behavioural tests
  (`test_database_conversion.py:236`, `test_ic_layout.py:130`) stay green unchanged because SRAM
  takes the same branch; only the display snapshot at `tests/__snapshots__/test_characterization.ambr`
  and `tests/test_build_db_inclusion.py:64` need updating.

### Claude's Discretion

- The override file's name, on-disk format and internal ordering (D-03 fixes its semantics, not its
  spelling). It sits beside `tools/extra_chips.json` per D-3 and must stay readable as a whole.
- Where the loader lives, and how it is covered given that `firestarter_app/tools/` sits outside
  every CI gate — no mypy, no `ruff check`, no `ruff format`.
- The exact wording of generator failure messages, subject to OVR-04's fail-closed requirement.
- Where the 216-row inventory file lands (D-12).

### Deferred Ideas (OUT OF SCOPE)

- **The wiki page "AT28C04 Adapter" goes stale.** D-07 deletes the reason string that cites it, and
  the adapter it documents is not needed. Documentation lives only in the `firestarter` GitHub wiki;
  no in-repo copy exists and no automated wiki guard exists now.
- **`FRAM_TOKENS` in `sdp_capability.py:121`** — the host's own hardcoded FRAM name list, covering
  `FM28V020` and `MB85R256H`. Unlike the generator's relabel it does real work (refusing SDP on parts
  that have none), and both are algorithm 13 promoted into the 0x0D EEPROM handler. Already tracked
  by the pending todo `fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md`.
- **The 216 algorithm 7/8 rows still at 100 µs** that D-10 does not reach. Inventoried under D-12,
  correctable later at one datasheet per row under D-02.
- **Whether the 9 newly-`supported` AT28C parts want bench proof** before shipping as writable. The
  operator's answer makes them supported on hardware grounds; no bench run is gated on it here.
- **Whether the generated database should mark a row as datasheet-corrected.** Raised and set aside:
  the emitted field set is guarded by `test_chip_database_field_inventory.py` and adding a field has
  firmware-parity consequences.

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| OVR-01 | A single override file beside `tools/extra_chips.json` carries per-part field overrides, and the generator applies them on top of the `infoic.xml` decode. | `## The Override File — Concrete Recommendation`; `## Integration Point (the hard part)` |
| OVR-02 | An entry holds only the fields that differ from the decoded value. A field whose override equals what infoic decodes to is not an entry. | `## Field Addressing`; the field-path table |
| OVR-03 | Every entry names the datasheet it comes from and the decoded value it replaces. | `## The Override File — Concrete Recommendation`; `## Datasheet Provenance and Git-Tracking Gap` |
| OVR-04 | The generator fails closed on an unknown part number, an unknown field, or a no-op override. | `## Fail-Closed Precedents (exact exception shapes)`; `## Coverage That Actually Runs` |
| OVR-05 | The three part-specific corrections move into the override file, and the generated database is unchanged by the move. | **Restated — see `## Contradictions` C-1, C-2, C-4.** Measured diff in `## The Measured Regeneration Diff` |
| OVR-06 | Any constant that remains part-specific is named, with the reason no alternative exists. | `## Part-Specific Constant Census After the Phase` |
| PULSE-01 | What `pulse_delay` encodes is established per algorithm family from evidence. | `## PULSE-01 — The Falsification Job` (D-11 **CONFIRMED**, with a positive datasheet match) |
| PULSE-02 | `MBM27C1000`'s program pulse falls inside 475–525 µs in the generated database. | `## PULSE-02 — Which Rows, To What Values`; 500 µs, from the part's own datasheet |
| PULSE-03 | The regeneration diff is measured across all 746 rows. | `## The Measured Regeneration Diff`; `## Regeneration and Diff Mechanics` |
| PULSE-04 | gh#70 is answered on the issue with the resulting values and the version carrying them. | `## gh#70 — What the Answer Must Actually Say` |

</phase_requirements>

---

## Contradictions With Locked Decisions

> Per the research constraints: where evidence contradicts a locked decision it is stated here
> explicitly and prominently, not planned around. Each item names the decision, the claim, the
> measurement, and what the planner must do.

### C-1 — D-07 achieves none of its stated effect. `[MEASURED]`

**D-07 claims:** deleting `_AT28C_DIP24_NAMES` makes *"9 rows flip to `supported`"*, and that the
9-vs-10 split among the 19 `DIP24_2816` rows is *"indefensible"*.

**Measured, from the raw pinned `infoic.xml` (commit `a8efaedc`), all 19 rows with
`pin_count 24 / pm_idx 23 / variant_lo 0x10`:**

| Row | upstream `protocol_id` | upstream `flags` | `flags & 0x10` | in `_AT28C_DIP24_NAMES` |
|---|---|---|---|---|
| AMD/AM28C16A | 0x0b | 0x000000 | False | no |
| ATMEL/AT28C04,AT28HC04 | 0x0b | 0x000010 | **True** | **yes** |
| ATMEL/AT28C04E,AT28C04F | 0x0b | 0x000010 | **True** | **yes** |
| ATMEL/AT28C16,AT28HC16,AT28HC16L | 0x0b | 0x000010 | **True** | **yes** |
| ATMEL/AT28C16E,AT28C16F | 0x0b | 0x000010 | **True** | **yes** |
| CATALYST(CSI)/CAT28C16A,CAT28C16AI | 0x0b | 0x000000 | False | no |
| EXEL/XL2804A | 0x0b | 0x000000 | False | no |
| EXEL/XL2816A,XLE28C16A,XLS28C16A | 0x0b | 0x000000 | False | no |
| EXEL/XLE28C16B,XLS28C16B | 0x0b | 0x000000 | False | no |
| MICROCHIP memory/2804 | 0x0b | 0x000000 | False | no |
| MICROCHIP memory/2816 | 0x0b | 0x000000 | False | no |
| MICROCHIP memory/28C04A | 0x0b | 0x000010 | **True** | **yes** |
| MICROCHIP memory/28C04AF | 0x0b | 0x000010 | **True** | **yes** |
| MICROCHIP memory/28C16A | 0x0b | 0x000010 | **True** | **yes** |
| MICROCHIP memory/28C16AF | 0x0b | 0x000010 | **True** | **yes** |
| NEC/UPD28C04 | 0x0b | 0x000010 | **True** | **yes** |
| XICOR/X2804A,X2804AI | 0x0b | 0x000000 | False | no |
| XICOR/X2816A | 0x0b | 0x000000 | False | no |
| XICOR/X2816B,X2816C | 0x0b | 0x000000 | False | no |

The split is **exactly** `flags & 0x10` — the electrically-erasable bit — with zero exceptions. It is
not a name list's whim. The nine names in `_AT28C_DIP24_NAMES` are precisely the nine rows that the
HARDWARE-DAMAGE GUARD at `build_db.py:468-492` already selects with
`pin_count == 24 and proto_id in (0x07, 0x08, 0x0B) and (flags & 0x10)`. All 19 arrive as
`proto_id 0x0b`, so the guard's condition is satisfied by exactly the nine erasable ones.

**Consequence, measured by full simulated regeneration:** deleting `_AT28C_DIP24_NAMES` changes only
the `unsupported_reason` **string** on those nine rows — from the wiki-adapter text back to the
damage-guard text. `support_status` stays `adapter-required` on all nine. **Zero rows flip to
`supported`.**

**What the planner must do:** to obtain D-07's stated effect the plan must narrow or delete the
HARDWARE-DAMAGE GUARD itself, whose documented hazard is *"12V onto a 5V write-enable pin"*. That is
a materially different, safety-adjacent change from "delete a name list", and D-07 does not
authorise it. **Escalate to the operator before planning it.**

Supporting evidence that the operator's *judgement* is nonetheless sound, if the escalation
proceeds: these rows resolve to `DIP24_2816`, not `DIP24_2716`. `pinouts.json` defines
`DIP24_2816` with **`"rw-pin": [21]` and no `vpp-pin`**, whereas `DIP24_2716` has
**`"vpp-pin": [21]`**. On the pinout these nine rows actually receive, socket pin 21 is the write
strobe, not the VPP rail — so the guard's stated hazard does not materialise for them. The guard's
own ordering comment (*"These chips resolve to DIP24_2716, not None"*) is **factually wrong** for
these rows: `resolve_pinout_key` selects `DIP24_2816` from `pm_idx == 23 and variant_lo == 0x10`,
independently of `proto_id`, so the guard's pre-emptive demotion to `NON_DISPATCHABLE_ALGO` never
affects their pinout — and `classify()` arm 2 re-promotes `proto_id` back to `0x0D` immediately
afterwards anyway.

### C-2 — D-08 changes two fields, not one. `[MEASURED]`

**D-08 claims:** *"The label changes nothing but a display string"*, effect *"FM1608's
`electrical.type` flips `FRAM` → `SRAM`"*.

**Measured:** FM1608 changes **two** emitted fields.

```
RAMTRON/FM1608
  electrical.type   : 'FRAM' -> 'SRAM'
  electrical.vcc_mv : 3300   -> 5000
```

The second change is caused by `build_db.py:700-705`, the SRAM single-rail rewrite:

```python
if _etype == "SRAM":
    chip_entry["electrical"]["vcc_mv"] = chip_entry["electrical"]["vdd_mv"]
```

The `FRAM` label was **bypassing** that rewrite. FM1608 decodes to `vcc_mv 3300, vdd_mv 5000`;
relabelling it `SRAM` makes it take the branch. Its sibling `RAMTRON/FM16W08` (already `SRAM`)
reads `vcc_mv 5000, vdd_mv 5000`, so the change makes FM1608 *consistent* with its siblings and is
arguably more correct — but it is a second emitted-value change that D-08 does not declare, and
`vcc_mv` is not a display string.

**What the planner must do:** restate D-08's effect as two fields and include both in the acceptance
diff.

### C-3 — D-10's "evidence is already on disk; nothing new to source" is false for the gh#70 row. `[MEASURED]`

**Measured:** `datasheets/MBM27C1001.pdf` (12 pages, OCR text layer present) contains the token
`MBM27C1001` 35 times and its OCR variants 10 more; the substring `27C1000` occurs **zero** times,
and no `1000`-shaped token appears anywhere in its extracted text. It is a datasheet for
`MBM27C1001-15/-20/-25` only.

Upstream agrees they are different parts. From the pinned `infoic.xml`:

```
MBM27C1000P@DIP32,MBM27C1000@SO32   proto=0x08  voltages=0xd060  variant=0xe200  size=0x20000
MBM27C1001,MBM27C1001@SO32          proto=0x08  voltages=0x4000  variant=0x1100  size=0x20000
```

Different `voltages` **and** different `variant`. Under D-02 — *"each entry states the datasheet that
justifies **that** row"* — `MBM27C1001.pdf` cannot justify an entry on `FUJITSU/MBM27C1000`.

**Resolution (good news):** the MBM27C1000 datasheet exists and was verified during this research. It
is an attachment on gh#70, posted by the reporter `@dim20`:
`https://github.com/user-attachments/files/32291377/Fujitsu-MBM27C1000-15Z-datasheet.pdf` —
*Fujitsu MBM27C1000-15/-20/-25, April 1988, Edition 2.0*, page 4-61 onward. It was downloaded and
read page by page for this research (see `## PULSE-02`). **The plan must vendor this PDF into
`firestarter_app/datasheets/` and cite it**, which resolves the D-02 conflict with no inference.

Additionally: of the three datasheets D-10 names, **only `MBM27C1001.pdf` is git-tracked.**
`datasheets/MBM27128.pdf` and `datasheets/MBM27C4001.pdf` are **untracked working-tree files**
(`git status` in `firestarter_app`). An OVR-03 citation pointing at an untracked file dangles for
everyone else. The plan must `git add` them.

### C-4 — D-13's "10 rows change" is wrong. Measured: 13 rows, zero `support_status` flips. `[MEASURED]`

See `## The Measured Regeneration Diff` for the full per-row output. Summary:

| D-13 says | Measured |
|---|---|
| 10 rows change | **13 rows change** |
| 9 `support_status` flips | **0 `support_status` flips** (see C-1) |
| FM1608 `electrical.type` | FM1608 `electrical.type` **and** `electrical.vcc_mv` (see C-2) |
| (pulse rows not counted) | 3 `programming.pulse_duration_us` changes |
| — | 9 `unsupported_reason` **string** changes |

### C-5 — D-14's test list is wrong in both directions. `[MEASURED]`

Measured by running the full suite (Python 3.11) against a simulated post-change database. Detail in
`## The Definitive Red List`. Of the three legs D-14 names as needing rewriting, **none goes red.**
Of the five tests that do go red, D-14 names one. It misses `tests/test_wire_dict_equivalence.py`
entirely — two failures there, requiring a new golden delta file.

A further trap in D-14: `tests/test_sdp_honesty.py:59` is a **bare comment line**, not an assertion.
Rewording it adds a `+#` line, which trips the project's mandatory pre-commit check
(`git diff --cached -- '*.py' | grep -E '^\+\s*#'`). Deleting the stale clause is permitted; rewriting
it is not.

---

## PULSE-01 — The Falsification Job

**Verdict: D-11 is CONFIRMED, and with stronger evidence than CONTEXT.md anticipated.** The
"microseconds for all protocols" decode rule **survives**, and the finding is *"infoic carries a
bulk family default, not a per-part value."*

### What the decode does today `[VERIFIED: firestarter_app/tools/build_db.py:339-380]`

```python
def interpret_timing(raw_hex, protocol_id):
    try:
        val = int(raw_hex, 16)
    except (TypeError, ValueError):
        raise ValueError(
            f"chip with protocol {protocol_id:#04x} has unparseable "
            f"pulse_delay {raw_hex!r} — refusing to default to 0 us"
        ) from None

    if protocol_id in (0x07, 0x08, 0x0B):
        return val

    return 0
```

Raw `pulse_delay` is parsed as hex and returned verbatim as microseconds, with no multiplier, for
algorithms 0x07/0x08/0x0B, and `0` for everything else.

### The positive confirmation — a datasheet that matches the raw value exactly

This is the decisive evidence, and it is a *positive* match rather than an absence of contradiction.

`FUJITSU/MBM27C4001` carries raw `pulse_delay=0x0064` = **100**. Its datasheet — read visually from
`datasheets/MBM27C4001.pdf`, page 8, *AC CHARACTERISTICS* — states:

| Parameter | Symbol | Min | Typ | Max | Unit |
|---|---|---|---|---|---|
| Programming Pulse Width | tPW | 95 | **100** | 105 | **µs** |
| Over Programming Pulse Number | N | 1 | | 50 | times |

Front page of the same datasheet: *"Fast programming: 0.1ms pulse"*.

Raw `0x0064` decoded as **100 µs** is exactly the datasheet's typical value, in the datasheet's own
unit. The unit is confirmed, not merely unrefuted.

### The falsification of "per-part value"

Two rows on the same algorithm, same raw value, different datasheet answers:

| DB row | raw `pulse_delay` | decoded | datasheet tPW (typ) | match? |
|---|---|---|---|---|
| `FUJITSU/MBM27C4001` | `0x0064` | 100 µs | **100 µs** | ✅ |
| `FUJITSU/MBM27C1001` | `0x0064` | 100 µs | **500 µs** | ❌ |
| `FUJITSU/MBM27C1000` | `0x0064` | 100 µs | **500 µs** | ❌ |
| `FUJITSU/MBM27128` | `0x00c8` | 200 µs | **1000 µs** (Quick Pro) | ❌ |

Distribution of raw `pulse_delay` across **every** `protocol_id` 0x07/0x08 `<ic>` in the pinned
`infoic.xml`, before the DIP filter — 675 entries `[MEASURED]`:

| raw hex | decimal | count | share |
|---|---|---|---|
| `0x0064` | 100 | **462** | 68.4 % |
| `0x0032` | 50 | 48 | 7.1 % |
| `0x00c8` | 200 | 38 | 5.6 % |
| `0x03e8` | 1000 | 36 | 5.3 % |
| `0x2710` | 10000 | 33 | 4.9 % |
| `0x000a` | 10 | 28 | 4.1 % |
| `0x0001` | 1 | 21 | 3.1 % |
| `0x01f4` | 500 | 4 | 0.6 % |
| `0x0014` | 20 | 2 | 0.3 % |
| `0x1388` | 5000 | 2 | 0.3 % |
| `0x0bb8` | 3000 | 1 | 0.1 % |

68 % of all algorithm 7/8 entries carry the single value 100. That is a bulk default, not 462
independent datasheet readings.

### Why no multiplier theory works `[MEASURED]`

The raw ladder spans `0x0001` (1) to `0x2710` (10000) — four orders of magnitude. Any uniform
multiplier that maps 100 → 500 (×5) also maps 10000 → 50000 and 1 → 5. A ×5 reading makes the
`0x0001` entries a 5 µs program pulse, which no EPROM specifies. Plain microseconds is the only
coherent reading, and `MBM27C4001` pins it exactly.

### What `pulse_duration_us` means on the wire `[VERIFIED: firestarter_fw/src/proms/eprom.cpp:68-105, src/proms/eprom_params.cpp:30-33, include/eprom_params.h]`

This settles which datasheet number to carry when a datasheet gives two.

The firmware runs an **intelligent, verify-per-pulse loop** — the Quick-Pro / Intel-inteligent shape
— not a single fixed pulse. From `eprom_params.cpp`, the const PROGMEM table:

```
/* 0x07 PROTO_EPROM_28PIN */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
/* 0x08 PROTO_EPROM_32PIN */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
/* 0x0B PROTO_EPROM_24PIN */ { 75000UL, 50000UL, 255, 0, VERIFY_PER_PULSE,            VPP_PATH_DIRECT_VPE    },
```

Columns are `overprogram_cap_us, energy_cap_us, max_pulses, overprogram_factor, verify_mode, vpp_path`.

- `handle->pulse_delay` is the **per-byte program pulse width in µs**, applied up to `max_pulses`
  times (25 for 0x07/0x08) with a verify after each.
- `overprogram_factor` is **0 on all three rows** — the header states *"no over-program pulse is
  emitted on any target"*. So the datasheet's `tOPW` margin pulse is not implemented.
- `energy_cap_us` is 0 (uncapped) for 0x07/0x08, so no pre-flight refusal applies there.
- The host-sends-nothing fallback in `eprom.cpp:68-75` is `0x08 → 100 µs`, `0x0B → 500 µs`,
  default (`0x07`) → `1000 µs`.

**Therefore: the value to carry is the fast-algorithm (Quick Pro / inteligent) *initial* programming
pulse width `tPW`, never the conventional single-shot width.** For `MBM27128` that means 1000 µs
(Quick Pro), not 50000 µs (conventional).

Note the recorded known-divergence in `eprom_params.cpp`: *"the 22 Intel-family 1 ms parts on 0x07
genuinely want a 3xN margin pulse. Serving them would need a second 0x07 row, which the table's
no-second-dispatch-key rule forbids."* This applies to the Fujitsu parts too — a corrected 500 µs
`tPW` still gives an incomplete Quick Pro because `tOPW` is never emitted. **PULSE-04's answer on
gh#70 must say so.**

### PULSE-01 finding, as it should be written down

> Raw `pulse_delay` in `infoic.xml` is plain microseconds for every protocol that consumes it
> (0x07/0x08/0x0B), confirmed positively by `FUJITSU/MBM27C4001`: raw `0x0064` decodes to 100 µs and
> its datasheet specifies `tPW` typ = 100 µs. The value is **not** per-part: 462 of 675 algorithm
> 7/8 entries carry the identical raw `0x0064`, and two Fujitsu parts sharing that raw value have
> datasheet pulses of 100 µs and 500 µs respectively. The generator's decode rule is correct; the
> upstream *data* carries a bulk family default. `pulse_duration_us` is consumed by the firmware as
> the initial pulse width of a verify-per-pulse loop capped at 25 pulses, so the datasheet figure to
> record is the fast-algorithm initial `tPW`, not a conventional single-shot width.

---

## PULSE-02 — Which Rows, To What Values

### Fujitsu's 12 algorithm 7/8 rows, and their datasheet coverage `[MEASURED]`

| # | DB row (`MANUFACTURER/part_number`) | alg | size | current `pulse_duration_us` | datasheet available | datasheet `tPW` | action |
|---|---|---|---|---|---|---|---|
| 1 | `FUJITSU/MBM27128` | 7 | 16384 | 200 | `datasheets/MBM27128.pdf` **(untracked)** | **1000 µs** Quick Pro (50 ms conventional) | **override → 1000** |
| 2 | `FUJITSU/MBM27256` | 7 | 32768 | 200 | none | — | uncorrected |
| 3 | `FUJITSU/MBM2764` | 7 | 8192 | 200 | none | — | uncorrected |
| 4 | `FUJITSU/MBM27C1000P,MBM27C1000` | 8 | 131072 | 100 | **gh#70 attachment** (must be vendored) | **500 µs** (0.475/0.50/0.525 ms) | **override → 500** |
| 5 | `FUJITSU/MBM27C1001` | 8 | 131072 | 100 | `datasheets/MBM27C1001.pdf` (tracked) | **500 µs** (0.475/0.50/0.525 ms) | **override → 500** |
| 6 | `FUJITSU/MBM27C128P` | 7 | 16384 | 100 | none | — | uncorrected |
| 7 | `FUJITSU/MBM27C2000P,MBM27C2000` | 8 | 262144 | 100 | none | — | uncorrected |
| 8 | `FUJITSU/MBM27C2001` | 8 | 262144 | 100 | none | — | uncorrected |
| 9 | `FUJITSU/MBM27C256A` | 7 | 32768 | 100 | none | — | uncorrected |
| 10 | `FUJITSU/MBM27C4001` | 8 | 524288 | 100 | `datasheets/MBM27C4001.pdf` **(untracked)** | **100 µs** (95/100/105) | **NO-OP — write no entry** |
| 11 | `FUJITSU/MBM27C512` | 7 | 65536 | 100 | none | — | uncorrected |
| 12 | `FUJITSU/MBM27C64` | 7 | 8192 | 100 | none | — | uncorrected |

**The three in-repo datasheets cover exactly 3 rows, not "up to 9".** Two need a change; one is
datasheet-confirmed already correct.

### `MBM27C4001` is a datasheet-confirmed no-op — do not write an entry for it

Under D-04/OVR-04 an override whose value equals the decode **fails the build**. `MBM27C4001`'s
datasheet agrees with the decoded 100 µs, so it must **not** get an entry. Record the verification
in the D-12 inventory file instead. This is a trap: a planner working from D-10's "up to 9 rows"
would naturally write an entry for every datasheet-covered row and the build would refuse.

### The evidence, verbatim from the datasheets

**`MBM27C1000-15/-20/-25`, Fujitsu, April 1988, Edition 2.0, page 4-68 — AC CHARACTERISTICS (Single
Byte Programming)** — read visually from the gh#70 attachment:

| Parameter | Symbol | Min | Typ | Max | Unit |
|---|---|---|---|---|---|
| Programming Pulse Width | tPW | **0.475** | **0.50** | **0.525** | **ms** |
| Over Programming Pulse Number | N | 1 | | 25 | times |
| Over Programming Pulse Width | tOPW | 1.4 | 1.5 | 39.4 | ms |

`NOTE: tOPW = 1.5 x Nms ± 5%`. DC CHARACTERISTICS header on the same page:
`(TA = 25 °C ± 5 °C, VCC1 = 6V ± 0.25V, VPP2 = 12.5V ± 0.3V)`.

→ **500 µs**, dead centre of PULSE-02's 475–525 µs gate. `[VERIFIED: Fujitsu MBM27C1000 datasheet
p.4-68, AC CHARACTERISTICS table]`

**`MBM27C1001-15/-20/-25`, page 9-90** — identical table, identical values (0.475 / 0.50 / 0.525 ms;
N 1..25; tOPW 1.4/1.5/39.4 ms; VCC1 = 6V ± 0.25V, VPP2 = 12.5V ± 0.3V).
`[VERIFIED: firestarter_app/datasheets/MBM27C1001.pdf p.9-90]`

**`MBM27128-25/-30`, pages 4-19 and 4-20** `[VERIFIED: firestarter_app/datasheets/MBM27128.pdf]`:

- Conventional Programming (p.4-19): *"+21V is applied to the VPP pin … a stable, **50 msec**, TTL
  low level pulse is applied to the P input … It is necessary that this program pulse width not
  exceed 55 msec."*
- Quick Pro (p.4-20): *"In addition to the standard 50 millisecond pulse width programming
  procedure, the MBM27128 can be programmed with a fast programming algorithm designed by Fujitsu
  called Quick Pro. The algorithm … utilizes a sequence of **1 millisecond** pulse to program each
  location."*
- Figure 3 Quick Pro flow chart, verbatim: `VCC = 6V ± 0.25V`, `VPP = 21V ± 0.5V`,
  **`TPW = 1 ms ± 50 µs`**, `APPLY 1 PROG. PULSE (1 ms)`, `X = 20` ceiling.

→ **1000 µs**, per the firmware-semantics argument in PULSE-01.

### Two out-of-scope discrepancies these datasheets surface — route, do not fix here

Both are Phase 198/199 territory (`## domain` puts voltage nibbles and rail ceilings out of scope),
but they are measured and should be filed so the later phases inherit them:

| Row | DB `vpp_mv` | Datasheet | Delta |
|---|---|---|---|
| `FUJITSU/MBM27C1001` | 12000 | 12.5 V ± 0.3 V | **−500 mV, below the datasheet floor of 12.2 V** |
| `FUJITSU/MBM27C4001` | 12000 | 12.5 V ± 0.3 V | **−500 mV, below the datasheet floor of 12.2 V** |
| `FUJITSU/MBM27128` | 18000 | 21 V ± 0.5 V | **−3 V** |
| `FUJITSU/MBM27C1000` | 12500 | 12.5 V ± 0.3 V | correct |

`MBM27C1000` is the only one of the four already right — matching gh#70's own note *"The VPP target
is right on this one."*

### ⚠️ A safety-adjacent finding the planner must route: the MBM27C1000 pinout

`[MEASURED — high confidence on the fact, INFERRED on the consequence]`

`MBM27C1000` and `MBM27C1001` have **different pin assignments**, and the database gives both rows
the same `pinout: DIP32_27C020`.

From the MBM27C1000 datasheet, page 4-61 PIN ASSIGNMENT, read visually at 520 dpi:

```
pin 1 = VPP   pin 2  = /OE   pin 3 = A15  pin 4 = A12 ...
pin 22 = /CE  pin 23 = A10   pin 24 = A16  pin 25 = A11 ...  pin 31 = /PGM  pin 32 = VCC
```

From the MBM27C1001 datasheet, page 9-86 PIN DESCRIPTION (verbatim): `Vpp 1`, `A0–A16 2-12, 23,
25-29`, `D0–D7 13-15, 17-21`, `GND 16`, `CE 22`, **`OE 24`**, `NC 30`, `PGM 31`, `Vcc 32`.

So **pins 2 and 24 are swapped between the two parts**: MBM27C1000 has `/OE` on 2 and `A16` on 24;
MBM27C1001 has `A16` on 2 and `/OE` on 24.

`firestarter/data/pinouts.json` → `DIP32_27C020` has
`"address-bus-pins": [12,11,10,9,8,7,6,5,27,26,23,25,4,28,29,3,2,30]` (index 16 → **pin 2**) and
`"oe-pin": [24]`. That is the **MBM27C1001** layout. `FUJITSU/MBM27C1000P,MBM27C1000` is on the wrong
pinout.

**This contradicts a published cross-check on gh#70**, which concluded *"MATCH on every pin the part
uses"* — a conclusion drawn from the MBM27C1001 datasheet, before the MBM27C1000 datasheet was
available.

`[INFERRED]` It plausibly explains the reported failure signature better than the pulse width does.
Writing at `0x01FF00` requires `A16 = 1`. Under the swap, the programmer drives socket pin 2 with the
A16 value while the part's real A16 sits on pin 24 carrying the OE line. During a program pulse OE is
deasserted (high) so the real A16 reads 1; during the verify OE is asserted (low) so the real A16
reads 0 — the verify reads address `0x0FF00` instead of `0x1FF00` and never converges. That is
exactly *"Byte at 0x01ff00 failed to program within 25 pulses"*. The reported clean `read` does not
refute it: the run's `divergence` block compares run 1 against run 2 (`repeat_divergent: false`,
`bad: 0`), which proves the two reads agree, not that either is correct.

**Pinout correctness is explicitly out of scope for Phase 197.** Do not fix it here. **File it** — it
belongs with the folded `pinout-address-width-and-we-pin-corrections.md` todo, and it materially
changes what PULSE-04 may claim on gh#70.

---

## The Measured Regeneration Diff

Produced by copying `tools/build_db.py` to a scratch directory, applying every Phase-197 change
(D-06 as 6 overrides, D-07 delete, D-08 delete, D-09 derivation, and the 3 pulse overrides), running
it against the live pinned `infoic.xml`, and diffing every field path of all 746 rows against the
shipped database. No tracked file was modified. `[MEASURED]`

**13 rows change. 0 `support_status` values change. 0 rows added or removed (746 → 746).**

| # | Row | Field | Before | After | Cause |
|---|---|---|---|---|---|
| 1 | `ATMEL/AT28C04,AT28HC04` | `unsupported_reason` | wiki-adapter text | damage-guard text | D-07 |
| 2 | `ATMEL/AT28C04E,AT28C04F` | `unsupported_reason` | wiki-adapter text | damage-guard text | D-07 |
| 3 | `ATMEL/AT28C16,AT28HC16,AT28HC16L` | `unsupported_reason` | wiki-adapter text | damage-guard text | D-07 |
| 4 | `ATMEL/AT28C16E,AT28C16F` | `unsupported_reason` | wiki-adapter text | damage-guard text | D-07 |
| 5 | `MICROCHIP memory/28C04A` | `unsupported_reason` | wiki-adapter text | damage-guard text | D-07 |
| 6 | `MICROCHIP memory/28C04AF` | `unsupported_reason` | wiki-adapter text | damage-guard text | D-07 |
| 7 | `MICROCHIP memory/28C16A` | `unsupported_reason` | wiki-adapter text | damage-guard text | D-07 |
| 8 | `MICROCHIP memory/28C16AF` | `unsupported_reason` | wiki-adapter text | damage-guard text | D-07 |
| 9 | `NEC/UPD28C04` | `unsupported_reason` | wiki-adapter text | damage-guard text | D-07 |
| 10 | `RAMTRON/FM1608` | `electrical.type` | `FRAM` | `SRAM` | D-08 |
| 10 | `RAMTRON/FM1608` | `electrical.vcc_mv` | `3300` | `5000` | D-08 → `:700-705` SRAM rewrite |
| 11 | `FUJITSU/MBM27128` | `programming.pulse_duration_us` | `200` | `1000` | PULSE |
| 12 | `FUJITSU/MBM27C1000P,MBM27C1000` | `programming.pulse_duration_us` | `100` | `500` | PULSE |
| 13 | `FUJITSU/MBM27C1001` | `programming.pulse_duration_us` | `100` | `500` | PULSE |

Exact before/after reason strings:

- before: `"adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter"` (`build_db.py:527-530`)
- after: `"adapter required: requires a dedicated DIP24 EEPROM adapter or firmware handler — socket pin 21 = WE, which the RURP DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)"` (`build_db.py:478-482`)

**The D-06 NMOS move and the D-09 derivation contribute zero diff**, exactly as D-06 and D-09 claim.
The 6 override entries reproduce the 6 values; the derivation regenerates byte-identically.

---

## The Definitive Red List

Measured by copying the whole `firestarter_app` tree to scratch, swapping in the simulated database,
and running the full suite under Python 3.11. `[MEASURED]`

**Baseline (unchanged DB, Python 3.11): `2024 passed in 198.32s`, `32 snapshots passed`, 0 failures.**

**Against the simulated post-change DB: `5 failed, 2019 passed in 182.91s`, `1 snapshot failed`.**

| # | Test | Why it goes red | Named by D-14? |
|---|---|---|---|
| 1 | `tests/test_build_db_inclusion.py::TestVariantDecodeClassification::test_fm1608_resolves_sram_std` | asserts `electrical.type == "FRAM"` (`:97`) | **partially** — D-14 cites `test_build_db_inclusion.py:64`, which is this class's docstring |
| 2 | `tests/test_build_db_inclusion.py::TestUnsupportedReasonStrings::test_at28c16_named_arm_reason_mentions_adapter_doc` | asserts `"AT28C04 Adapter" in reason` (`:584`) — the damage-guard text does not contain it | **no** |
| 3 | `tests/test_characterization.py::test_list` | `tests/__snapshots__/test_characterization.ambr:1001` renders `FM1608 … FRAM` | yes |
| 4 | `tests/test_wire_dict_equivalence.py::test_live_capture_matches_golden_plus_the_149_and_153_and_182_and_194_deltas` | 3 wire dicts change; no 197 delta file exists | **no** |
| 5 | `tests/test_wire_dict_equivalence.py::test_exactly_84_records_change_flags_and_no_other_field_moves` | `assert len(changed_keys) == 84` → found **87**; the 3 extra are `FUJITSU\|MBM27128\|2`, `FUJITSU\|MBM27C1000P,MBM27C1000\|6`, `FUJITSU\|MBM27C1001\|7` | **no** |

### Tests D-14 names that do **not** go red `[MEASURED]`

| Test | D-14 expectation | Measured |
|---|---|---|
| `tests/test_sdp_capability.py:519` `assert len(adapter_required) == 9` | must be rewritten | **GREEN** — the 9 rows stay `adapter-required` (C-1) |
| `tests/test_chip_resolver.py:87` `resolve_chip("AT28C04")` raises | must be rewritten | **GREEN** — same reason |
| `tests/test_sdp_honesty.py:59` | must be rewritten | **GREEN** — it is a comment line, not an assertion |

D-14's three *correct* negative predictions are confirmed: `tests/test_diagnostic_report.py`
(synthetic `_mock_db` only), `tests/test_database_conversion.py:236` and `tests/test_ic_layout.py:130`
all stay green. `tests/test_chip_database_field_inventory.py` also stays green — its
`"unsupported_reason": 10` count is preserved because the 9 rows keep the key (with different text).

### What `tests/test_wire_dict_equivalence.py` needs `[VERIFIED: tests/test_wire_dict_equivalence.py:25-120, :209-330]`

It is a **layered golden** with a base file plus one delta file per phase that changed wire values:

```
tests/golden/wire_dict_baseline.json
tests/golden/wire_dict_expected_deltas_149.json
tests/golden/wire_dict_expected_deltas_153.json   (len == 84, asserted exactly)
tests/golden/wire_dict_expected_deltas_182.json   (len == 8,  asserted exactly)
tests/golden/wire_dict_expected_deltas_194.json   (len == 25, asserted exactly)
```

The plan must add `tests/golden/wire_dict_expected_deltas_197.json`, load it in
`test_live_capture_matches_golden_plus_…`, add its exact-count and non-vacuity assertions in the same
shape as the 182/194 layers, extend the pairwise-disjointness checks around `:321`, and bump the
`== 84` in `test_exactly_84_records_change_flags_and_no_other_field_moves` to `87`. Four prior phases
give a working template — copy the 194 layer.

---

## The Override File — Concrete Recommendation

> This closes the four Claude's-Discretion items.

### Name and location

**`firestarter_app/tools/datasheet_overrides.json`**

Rationale: it sits beside `tools/extra_chips.json` as D-3 requires; `datasheet_` states the source of
authority and distinguishes it from the operator's runtime `~/.firestarter/database.json`; and it
avoids the name `database_overrides.json`, which `pyproject.toml:85-90` already reserves under
`[tool.setuptools.package-data]` for `firestarter/data/` (the file does not exist yet, but the name
is claimed and reusing it would be confusing).

### On-disk format

A flat object keyed by `MANUFACTURER/ALIAS` (D-01), one entry per row (D-02), each entry carrying
`datasheet`, a `fields` map of dotted field paths, and per field the recorded prior value (D-04):

```json
{
  "FUJITSU/MBM27C1000": {
    "datasheet": "datasheets/MBM27C1000.pdf",
    "note": "AC CHARACTERISTICS (Single Byte Programming), p.4-68: tPW 0.475/0.50/0.525 ms",
    "fields": {
      "programming.pulse_duration_us": { "was": 100, "is": 500 }
    }
  },
  "INTEL/M2716": {
    "datasheet": "Intel 2716 datasheet",
    "note": "NMOS 2716 requires 25 V VPP; upstream aliases it under a generic 2716 entry capped at 18 V",
    "fields": {
      "electrical.vpp_mv": { "was": 18000, "is": 25000 }
    }
  }
}
```

Why `{"was": …, "is": …}` rather than a bare value: D-04 requires the recorded prior value to be
**asserted against the live decode**, which makes it load-bearing rather than prose. A bare value
would force the prior into a comment, and JSON has no comments. This shape also makes OVR-02's no-op
rule mechanical — `was == is` is a one-line check.

### Internal ordering

Sort by key, ascending, and enforce it in the loader (fail closed on unsorted). This keeps the file
readable as a whole (D-3's requirement) and makes diffs across Phases 198/199/200 stable as each adds
entries. The six NMOS entries and the pulse entries will then interleave alphabetically, which is
correct — the file is organised by row, not by campaign.

### Where the loader lives

Put the loader **in `tools/build_db.py` itself**, as two module-level functions:

- `load_datasheet_overrides(path) -> dict` — reads, validates structure, validates sort order.
- `apply_datasheet_override(overrides, mfg_name, aliases, decoded) -> None` — resolves the
  `MANUFACTURER/ALIAS` key, asserts every `was` against `decoded`, substitutes every `is`, and raises
  on an unknown field path.

Reason: `build_db.py` is already the single import surface tests reach (`from tools import build_db`,
see below), the file is 764 lines and a second module buys nothing, and keeping the ceiling check and
the substitution in one file makes the D-03 ordering visible in one read.

A tracking set of consumed keys, checked after the decode loop, gives the unknown-part failure —
this is the only way to detect it, since a key that matches no row simply never fires.

---

## Integration Point — the hard part

### ⚠️ There is no decoded row dict at the D-03 insertion point `[MEASURED]`

D-03 fixes the insertion point as *"after decode and `classify()` but BEFORE the ceiling check at
`:591`"*. That location is **verified correct**, but at that point in `build_db.py` **no row-shaped
object exists**. The decoded values live only as loose local variables:

```
name, mfg_name, pin_count, type_int, variant, proto_id, flags, raw_page_size,
voltages, mem_size, pm_idx, pinout_key, _etype, _upstream_proto_id,
_support_status, _unsupported_reason, _nmos_vpp_mv
```

`chip_entry` is constructed at **`:607-681`**, *after* the ceiling check, and the emitted values are
computed **inline inside the dict literal**:

```python
"vpp_mv": (
    _nmos_vpp_mv
    if _nmos_vpp_mv is not None
    else VPP_MV.get(voltages & 0xF0, 0)
),
...
"pulse_duration_us": interpret_timing(
    ic.get("pulse_delay"), proto_id
),
```

So an override key like `electrical.vpp_mv` **resolves to nothing** at the insertion point today.
The plan's first task must create something for it to resolve to.

### ⚠️ The `chip_entry` dict literal must survive `[VERIFIED: tests/test_chip_database_field_inventory.py:234-263]`

`test_generator_emits_no_key_outside_the_frozen_inventory` **ast-walks `tools/build_db.py`** and
collects string key literals from `ast.Assign` nodes whose target is a `Name` called `chip_entry`
with an `ast.Dict` value, plus `chip_entry[...] = ...` subscript chains. `_collect_dict_keys` handles
nested dicts and the existing conditional `**{...}` spread.

**A refactor that replaces the literal with `chip_entry = dict(decoded)` or `chip_entry = {**decoded}`
makes the AST walk collect nothing and the golden's 25-key
`generator_emitted_chip_entry_keys` list mismatch → RED.**

**Therefore the design is forced, and this is the single most important implementation fact in this
document:**

> Hoist the computed values into **named local variables** immediately before the ceiling check,
> apply overrides to those locals through a dotted-path view, and leave the `chip_entry = { ... }`
> dict literal structurally intact — with every one of its 14 key literals in place — referencing the
> hoisted locals instead of inline expressions.

Sketch of the shape (illustrative; the executor writes the real code — and note the project's hard
rule: **no comments in source**):

```python
_d_vpp_mv  = VPP_MV.get(voltages & 0xF0, 0)
_d_vcc_mv  = VCC_VOLTAGES.get((voltages >> 8) & 0x0F, 5000)
_d_vdd_mv  = VCC_VOLTAGES.get((voltages >> 12) & 0x0F, 5000)
_d_pulse   = interpret_timing(ic.get("pulse_delay"), proto_id)
...
apply_datasheet_override(_OVERRIDES, mfg_name, _aliases, _decoded_view)
...
chip_entry = {
    "part_number": ...,
    "support_status": _support_status,
    "electrical": {
        "type": _etype,
        "size_bytes": _d_size_bytes,
        "pin_count": _d_pin_count,
        "vpp_mv": _d_vpp_mv,
        "vcc_mv": _d_vcc_mv,
        "vdd_mv": _d_vdd_mv,
    },
    ...
}
```

Every key literal stays. Only the right-hand sides change from expressions to names.

### ⚠️ The ceiling check does not do what D-03 assumes `[MEASURED]`

D-03's rationale is that a post-decode merge would let *"an overridden `vpp_mv` of 30000 … ship
`support_status: supported`"*. That hazard is real — but **the current pre-derivation check does not
prevent it either**, because it is gated on the NMOS flag rather than on the value:

```python
if _nmos_vpp_mv is not None:                    # :591
    if _nmos_vpp_mv > RURP_VPP_CEILING_MV:      # :592
        _support_status = "vpp-exceeds-max"
```

A row whose *decoded* `VPP_MV.get(voltages & 0xF0, 0)` exceeded 25000 would ship `supported` today.
(It cannot happen at present only because `VPP_MV` tops out at 18000.) Deleting `NMOS_TRUE_VPP_MV`
per D-06 deletes the gate variable entirely.

**The plan must generalise the check to key on the effective `vpp_mv`**, i.e.
`if _d_vpp_mv > RURP_VPP_CEILING_MV:`, after the override is applied. This is what makes D-03's
stated protection actually exist.

### ⚠️ The comparison is `>`, not `>=` — and six rows sit exactly on the boundary `[MEASURED]`

```
vpp_mv distribution, shipped DB: 12000×563, 13000×144, 18000×22, 12500×7, 25000×6, 21000×2, 9000×1, 13500×1
support_status distribution:     supported×736, adapter-required×9, protocol-not-implemented×1
```

**Zero rows carry `vpp-exceeds-max`.** The six 25000 mV rows all ship `supported`, because
`25000 > 25000` is false. The source comment at `:64-68` says *"The 25 V parts are unprogrammable on
this shield regardless (~22 V max)"*, which reads as if they were refused; they are not.

D-06 promises *"Generated values are unchanged by the move"*. That holds **only if the generalised
check keeps `>` and not `>=`**. Using `>=` would flip six rows to `vpp-exceeds-max`, demote their
algorithm to `NON_DISPATCHABLE_ALGO`, and redden `tests/test_chip_resolver.py:72-84`
(`test_resolve_chip_m2716…` asserts `vpp_mv == 25000` and `algorithm == 11` after a *successful*
resolve). That test is a useful positive control for D-06 — keep it green.

Whether the boundary should be `>=` is a separate question that belongs to Phase 199 (rail ceilings).
**Do not change it here.**

### The six NMOS rows, enumerated for D-06 `[MEASURED]`

`NMOS_TRUE_VPP_MV`'s three entries reach exactly six rows. D-06's count is confirmed.

| Override key (D-01) | Row `part_number` | Matched alias(es) | Value | Current DB |
|---|---|---|---|---|
| `INTEL/M2716` | `M2716,M2716M` | `M2716` | 25000 | 25000 ✓ |
| `SGS-THOMSON/M2716` | `ETC2716,M2716` | `M2716` | 25000 | 25000 ✓ |
| `ST/M2716` | `ETC2716,M2716` | `M2716` | 25000 | 25000 ✓ |
| `INTEL/M2732` | `2732,2732A,M2732,M2732A` | `M2732` **and** `M2732A` | 25000 | 25000 ✓ |
| `SGS-THOMSON/M2732A` | `M2732A` | `M2732A` | 21000 | 21000 ✓ |
| `ST/M2732A` | `M2732A` | `M2732A` | 21000 | 21000 ✓ |

All six are `algorithm 11` (0x0B). The INTEL row is the one D-06 describes: it matches both `M2732`
(25000) and `M2732A` (21000), and "highest VPP wins" resolves it to 25000. Under D-01 the entry is
keyed `INTEL/M2732` with value 25000 and the tie-break dissolves — **but the loader must then reject
a second entry keyed `INTEL/M2732A`**, because both keys resolve to the same row and two entries
would silently race. A per-row "already overridden this field" check catches it. This is a concrete
OVR-04 fail-closed leg worth a test.

`TEXAS INSTRUMENTS/2516` and `TEXAS INSTRUMENTS/2532` also carry `vpp_mv: 25000` but come from
`tools/extra_chips.json` (fully-specified, post-decode) and are **not** reached by the NMOS block.
Do not include them.

### `_upstream_proto_id` ordering constraint `[VERIFIED: build_db.py:558-566]`

```python
_upstream_proto_id = proto_id
_etype, proto_id, pinout_key = classify(
    type_int, proto_id, pm_idx, flags, pinout_key, mem_size
)
```

`classify()` **reassigns** `proto_id` (a 5V EEPROM arrives as 0x07/0x0B and leaves as 0x0D). The
`page_size` emission arm at `:667-676` reads `_upstream_proto_id`, not `proto_id`.

Consequence for the override: the D-03 insertion point is **after** this capture, so an override on
`programming.algorithm` would change the *emitted* algorithm without changing `_upstream_proto_id`,
and therefore without changing whether `page_size` is emitted. That is a latent inconsistency.

**Recommendation:** restrict the overridable field set for Phase 197 to the fields the phase actually
needs plus the ones Phases 198–200 need, and **exclude `programming.algorithm` and `pinout` from the
allowed set for now**, failing closed on them via OVR-04's unknown-field leg. Widening later is
additive; getting algorithm-vs-page_size wrong is not.

Note also: `interpret_timing(ic.get("pulse_delay"), proto_id)` is called with the **post-`classify()`**
`proto_id`. A row promoted out of 0x07/0x08/0x0B into 0x0D therefore emits `pulse_duration_us: 0`.
The hoisted `_d_pulse` must preserve that exact call, with the same `proto_id`, or 417 rows move.

---

## Field Addressing

Measured shape of an emitted row `[MEASURED: firestarter/data/chip_database.json + tests/golden/chip_database_field_inventory.json]`. Nested two levels; `electrical.vpp_mv` is a real path.

| Dotted path | Occurrences / 746 | Source expression in `build_db.py` | Overridable? |
|---|---|---|---|
| `part_number` | 746 | alias join (`:607-624`) | no — it is the key's own basis |
| `support_status` | 746 | derived (`:625`) | **no** (D-03/D-05) |
| `unsupported_reason` | 10 | derived (`:682-683`) | **no** (D-05) |
| `electrical.type` | 746 | `classify()` (`:563`) | defer |
| `electrical.size_bytes` | 746 | `mem_size` (`:417`) | yes |
| `electrical.pin_count` | 746 | package decode (`:392`) | yes |
| `electrical.vpp_mv` | 746 | `VPP_MV.get(voltages & 0xF0, 0)` (`:638-642`) | **yes — Phase 197 (D-06), Phase 199** |
| `electrical.vcc_mv` | 746 | `VCC_VOLTAGES.get((voltages >> 8) & 0x0F, 5000)` (`:646-648`) | **yes — Phase 198/200** |
| `electrical.vdd_mv` | 746 | `VCC_VOLTAGES.get((voltages >> 12) & 0x0F, 5000)` (`:649-651`) | **yes — Phase 198/200** |
| `programming.algorithm` | 746 | `classify()` (`:654`) | **no for now** — see `_upstream_proto_id` above |
| `programming.pulse_duration_us` | 746 | `interpret_timing(...)` (`:655-657`) | **yes — Phase 197 (PULSE)** |
| `programming.chip_id_check` | 746 | `flags & 0x20` (`:658`) | yes |
| `programming.chip_id_value` | 746 | `ic.get("chip_id")` (`:659`) | yes |
| `programming.protect_off_before` | 744 | `flags & 0x4000` (`:664`) | yes |
| `programming.protect_on_after` | 744 | `flags & 0x8000` (`:665`) | yes |
| `programming.infoic_page_size_raw` | 744 | `raw_page_size` (`:666`) | yes |
| `programming.page_size` | 45 | conditional on `_upstream_proto_id` (`:667-676`) | defer — conditional presence |
| `pinout` | 746 | `resolve_pinout_key()` / `classify()` (`:680`) | **no for now** |
| `datasheet`, `provenance`, `source`, `verification_note`, `verification_status` | 2 each | `extra_chips.json` merge only | n/a |

`electrical` and `programming` themselves are 746/746 as containers.

**Note the two-level maximum.** A dotted path of exactly two segments (`section.field`), or one
segment for a top-level field, covers every real case. The loader does not need general deep-path
resolution; a two-level resolver with an explicit allow-list is simpler and fails closed by
construction on an unknown field.

---

## Fail-Closed Precedents (exact exception shapes)

D-04 says it follows two existing models. Both verified `[VERIFIED: firestarter_app/tools/build_db.py]`.

**1. `interpret_timing` (`:349-363`)** — raises `ValueError`, names both the protocol and the
offending raw value, uses `from None` to suppress chaining:

```python
raise ValueError(
    f"chip with protocol {protocol_id:#04x} has unparseable "
    f"pulse_delay {raw_hex!r} — refusing to default to 0 us"
) from None
```

**2. `page_size` validation (`:739-752`)** — raises `ValueError`, names the manufacturer, the part,
the offending value, and the file it is refusing to write:

```python
raise ValueError(
    f"{mfg_name}/{chip.get('part_number')} would emit "
    f"page_size {emitted_page_size!r}, which is not a power "
    f"of two in [1, 512] — refusing to write {OUTPUT_FILE}"
)
```

**House style to match, all four elements:** `ValueError`; f-string; name the offending row **and**
value; end with an explicit `— refusing to …` clause. `main()` does not catch `ValueError`, so either
aborts the process before the JSON write, with a traceback. That is the correct fail-closed behaviour
— no partial database is emitted.

### The four OVR-04 legs, and why each needs a unit test

`tests/test_build_db_interpret_timing.py` records the precedent reasoning exactly
`[VERIFIED: tests/test_build_db_interpret_timing.py:16-19]`:

> *"the fatal branch is PROVABLY DEAD against the pinned infoic.xml commit … That means a green
> `python3 tools/build_db.py` run proves NOTHING about this branch — this module is its ONLY
> coverage."*

The same applies to every OVR-04 leg: against a **correct** override file none of them fires, so a
green regeneration proves nothing. Each needs a direct unit test:

| Leg | Trigger | Expected |
|---|---|---|
| unknown part | a key matching no `MANUFACTURER/ALIAS` in any row | `ValueError` naming the key |
| unknown field | a field path outside the allow-list | `ValueError` naming the path and the row |
| no-op override (OVR-02/D-04) | `was == is` | `ValueError` naming the row, the field and the value |
| stale recorded prior (D-04) | `was != live decode` | `ValueError` naming the row, the field, the recorded value and the live value |
| duplicate row target | two keys resolving to the same row + field | `ValueError` naming both keys |

---

## Coverage That Actually Runs

**The discretion question is answered by an existing precedent:
`tests/test_build_db_interpret_timing.py:40` does `from tools import build_db`.** A plain package
import of `tools/` works from the pytest rootdir. `tools/build_db.py`'s module-level code only opens
`pinouts.json`; `main()` is `if __name__ == "__main__"`-guarded, so importing is side-effect-safe.

Three tests already reach into `tools/`: `test_build_db_interpret_timing.py`,
`test_parse_devtest_issue.py`, `test_diagnostic_report.py`.

**So:**

| Location | `ruff check` | `ruff format --check` | `mypy` | `pytest` in CI |
|---|---|---|---|---|
| `tools/datasheet_overrides.json` | n/a | n/a | n/a | read by tests |
| loader code in `tools/build_db.py` | ✗ | ✗ | ✗ | **executed by tests** |
| `tests/test_datasheet_overrides.py` | ✓ | ✓ | ✗ (not a CI gate) | ✓ |

`[VERIFIED: firestarter_app/pyproject.toml:100-120, .github/workflows/ci.yml:53-71]` — CI runs
`ruff check firestarter/ tests/`, `ruff format --check firestarter/ tests/`, then
`pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70`, all on Python 3.11.
`tools/` is in no lint or type scope, and `--cov=firestarter` means loader code in `tools/` contributes
no coverage — but the **behaviour** is gated by the tests, which is what matters.

**Recommendation:** put every fail-closed leg in `tests/test_datasheet_overrides.py`, importing
`from tools import build_db`. The new test file *is* ruff-checked and ruff-format-checked, so it must
be clean under `select = ["E", "F", "I", "UP"]` with `E501` ignored, `line-length = 88`,
`quote-style = "double"`.

---

## Regeneration and Diff Mechanics

### The exact command `[MEASURED]`

```bash
cd /workspaces/firestarter_app
python tools/build_db.py
```

- **Runtime: ~1.7 s wall**, including the 17.9 MB network fetch. Not a slow step.
- **Requires network.** `MINIPRO_XML_URL` (`build_db.py:14-17`) fetches
  `https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml`.
  **No copy of `infoic.xml` is vendored in the repo** — verified: `find /workspaces -name "infoic*.xml"`
  returns nothing. Confirmed reachable from this devcontainer: HTTP 200, 17,861,009 bytes.
- Writes `firestarter/data/chip_database.json` and nothing else. Prints 32 lines of `WARN:`/`INFO:` to
  stderr and 3 progress lines to stdout, ending
  `Done! 744 upstream chips processed + 2 non-upstream supplement chip(s) = 746 total.`

### ✅ The pipeline is byte-reproducible today `[MEASURED]`

A scratch copy of `build_db.py` with only its output path redirected produced a file that is
**`cmp`-identical** to the shipped `firestarter/data/chip_database.json`. This is the precondition
D-09's "byte-identical regeneration is the proof" depends on, and it holds. Any diff after the plan's
changes is attributable to the plan.

### Producing an auditable 746-row diff

**There is no existing diff tool.** `tools/diff_db.py` is referenced by
`tests/golden/chip_database_field_inventory.json`'s `meta.why_not_diff_db` but **does not exist** —
`ls tools/` shows `DECODE-NOTES.md`, `baseline/`, `build_db.py`, `catalog/`, `extra_chips.json`,
`gen_sdp_bus_config.py`, `gen_test_image.py`, `gen_validation_header.py`, `parse_devtest_issue.py`,
`pin-layouts.odt`, `validation_matrix_spec.json`, `variant-decode-diff.txt`. The stale reference is
worth a one-line correction while the plan is in that file anyway.

`tools/baseline/chip_database.baseline.json` exists but is **stale** — it differs from the live
database (475,857 vs 432,461 bytes). Do not diff against it.

**Recommended approach — a throwaway script, not a committed tool.** A flat field-path diff over the
`(manufacturer, part_number)` key produces exactly the "these N rows changed and nothing else"
evidence PULSE-03 wants, in ~25 lines. This is the script used to produce
`## The Measured Regeneration Diff` above; the plan can reuse its shape:

```python
import json

def flat(d):
    return {(m, r["part_number"]): r for m, rows in d.items() for r in rows}

def paths(r, pre=""):
    out = {}
    for k, v in r.items():
        if isinstance(v, dict):
            out.update(paths(v, pre + k + "."))
        else:
            out[pre + k] = v
    return out

A = flat(json.load(open("before.json")))
B = flat(json.load(open("after.json")))
assert set(A) == set(B), (set(A) ^ set(B))
for key in sorted(A):
    pa, pb = paths(A[key]), paths(B[key])
    diff = {f: (pa.get(f, "<absent>"), pb.get(f, "<absent>"))
            for f in set(pa) | set(pb)
            if pa.get(f, "<absent>") != pb.get(f, "<absent>")}
    if diff:
        print(key, diff)
```

Take `before.json` from `git show HEAD:firestarter/data/chip_database.json`.

---

## D-09 — Proven Twice

`[MEASURED]` The substitution
`mem_size <= _PGM_ON_PIN31_MAX_SIZE` → `(mem_size - 1).bit_length() <= 18`, with the constant
deleted, regenerates the database **`cmp`-identical** to the shipped file.

`[MEASURED]` The identity is **exact for every non-negative integer**, not merely for the
power-of-two sizes in the database. Checked exhaustively for `s` in `[0, 2_100_000)`: **zero
mismatches.** Boundary values:

| `s` | `(s-1).bit_length()` | `<= 18` | `s <= 262144` |
|---|---|---|---|
| 0 | 1 (Python: `(-1).bit_length() == 1`) | True | True |
| 262144 | 18 | True | True |
| 262145 | 19 | False | False |

Algebraically: `(s-1).bit_length() <= 18 ⟺ s-1 < 2^18 ⟺ s <= 262144`.

The 11 distinct `electrical.size_bytes` values in the shipped database are all powers of two —
512 (×8), 2048 (×39), 4096 (×17), 8192 (×72), 16384 (×26), 32768 (×104), 65536 (×73), 131072 (×145),
262144 (×148), 524288 (×106), 1048576 (×8) — but the derivation does not depend on that, so a future
non-power-of-two `code_memory_size` cannot break it either.

The fork's blast radius, for reference: 166 of the 439 32-pin rows sit on the three forked pinouts
(`DIP32_27C020` ×88, `DIP32_STD` ×70, `DIP32_27C801` ×8).

**This is the strongest-evidenced decision in the phase. Its acceptance criterion should be a literal
`cmp` of the regenerated file against `git show HEAD:firestarter/data/chip_database.json` with only
the D-09 change applied, run as its own task before any other change lands.**

---

## D-12 — The Inventory

`[MEASURED]` Both of D-12's numbers are exact.

```
algorithm 7/8 rows:                   297   (alg 7 = 170, alg 8 = 127)
of which pulse_duration_us == 100:    217
```

Cross-checked against the frozen golden's `protocol_chip_counts`: `{"7": 170, "8": 127, "11": 32}` —
which `tests/test_chip_database_field_inventory.py::test_27c_protocol_chip_counts_match` already
pins. The override must not move an algorithm, or that test reddens.

Full algorithm 7/8 `pulse_duration_us` distribution:

| µs | rows |
|---|---|
| 10 | 7 |
| 20 | 1 |
| 50 | 15 |
| **100** | **217** |
| 200 | 29 |
| 500 | 4 |
| 1000 | 24 |

Top manufacturers in the 217: ATMEL 16, NSC 15, AMD 14, SGS-THOMSON 14, MACRONIX(MXIC) 13, INTEL 11,
ST 11, FAIRCHILD 9.

After Phase 197: two rows leave the pool (`MBM27C1000`, `MBM27C1001` → 500) and one is
datasheet-verified correct at 100 (`MBM27C4001`), leaving **215 rows at 100 µs with no datasheet
evidence**. CONTEXT.md's deferred note says "216"; the measured figure is 215. It is a bookkeeping
number, not load-bearing.

**Command that produces the inventory file:**

```bash
cd /workspaces/firestarter_app
python3 -c "
import json
db = json.load(open('firestarter/data/chip_database.json'))
rows = [(m, r) for m in sorted(db) for r in db[m]
        if r['programming']['algorithm'] in (7, 8)
        and r['programming']['pulse_duration_us'] == 100]
print(len(rows))
for m, r in rows:
    print(f\"{m}/{r['part_number']}\t{r['electrical']['size_bytes']}\t{r['electrical']['vpp_mv']}\")
"
```

**Recommended landing place:** `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-PULSE-INVENTORY.md`
— a phase-directory artifact, per D-12's "recorded as a measured inventory in the phase directory",
with the backlog item filed separately. Do not put it in `firestarter_app/`: it is planning evidence,
and `.planning/` is the meta repo.

---

## Part-Specific Constant Census After the Phase (OVR-06)

`[MEASURED]` Every named constant in `build_db.py`, classified.

| Constant | Line | Kind | Disposition |
|---|---|---|---|
| `MINIPRO_XML_URL` | 14 | pinned upstream source | stays — not part-specific |
| `PROTOCOL_MAP` | 32 | decode table | stays (D-2) |
| `VPP_MV` | 69 | decode table | stays (D-2) |
| `NMOS_TRUE_VPP_MV` | 87 | **part-specific** | **→ 6 override entries (D-06)** |
| `RURP_VPP_CEILING_MV` | 94 | hardware property | stays — shield ceiling, not a part |
| `NON_DISPATCHABLE_ALGO` | 104 | sentinel | stays |
| `KNOWN_PROTOCOLS` | 113 | decode table | stays (D-2) |
| `VCC_VOLTAGES` | 133 | decode table | stays (D-2) |
| `_VCC_MARGIN_RAIL_MV` | 142 | derived from `VCC_VOLTAGES[0x02]` | stays — already derived, not a literal |
| `_PGM_ON_PIN31_MAX_SIZE` | 148 | **derivable** | **→ deleted, derived (D-09)** |
| `_AT28C_DIP24_NAMES` | 506 | **part-specific** | **→ see C-1; deleting it achieves nothing** |
| `_ETYPE_RELABEL` | 573 | **part-specific** | **→ deleted (D-08)** |

**Expected OVR-06 answer after the phase: an empty list**, as the requirement anticipates — *provided
C-1 is resolved*. If the operator declines to touch the damage guard, `_AT28C_DIP24_NAMES` must
either stay (and be named under OVR-06 with the reason) or be deleted with the understanding that its
only effect is the reason string. The honest OVR-06 entry in that case is: *"the nine-row selection
is not part-specific at all — it is `flags & 0x10` — and the name list is redundant with the guard
that already selects them."*

Three alias-parsing duplicates also go away with their hardcodes
`[VERIFIED: build_db.py:522-524, :574, :586]` — the idiom
`{a.split("@")[0].strip() for a in name.split(",")}` appears at `:522`, `:574` and `:586`. D-01's key
resolution needs it exactly once. Note the subtle difference: `:522` filters empty strings
(`if a.strip()`), `:574` and `:586` do not. Use the filtering form.

---

## Verified Line Citations

Every CONTEXT.md code citation was re-checked against the live files on 2026-09-18. `[MEASURED]`

| CONTEXT.md citation | Status | Live content |
|---|---|---|
| `build_db.py:87` `NMOS_TRUE_VPP_MV` | ✅ exact | `NMOS_TRUE_VPP_MV: dict[str, int] = {` |
| `build_db.py:94` `RURP_VPP_CEILING_MV` | ✅ exact | `RURP_VPP_CEILING_MV = 25000` |
| `build_db.py:142` `_VCC_MARGIN_RAIL_MV` | ✅ exact | `_VCC_MARGIN_RAIL_MV = VCC_VOLTAGES[0x02]` |
| `build_db.py:148` `_PGM_ON_PIN31_MAX_SIZE` | ✅ exact | `_PGM_ON_PIN31_MAX_SIZE = 262144` |
| `build_db.py:241` the fork | ✅ exact | `elif proto_id == 0x08 and mem_size <= _PGM_ON_PIN31_MAX_SIZE:` |
| `build_db.py:339` `interpret_timing` | ✅ exact | `def interpret_timing(raw_hex, protocol_id):` |
| `build_db.py:506` `_AT28C_DIP24_NAMES` | ✅ exact | `_AT28C_DIP24_NAMES = {` |
| `build_db.py:562` `_upstream_proto_id` | ✅ exact | `_upstream_proto_id = proto_id` |
| `build_db.py:573` `_ETYPE_RELABEL` | ✅ exact | `_ETYPE_RELABEL = {"FM1608": "FRAM"}` |
| `build_db.py:591-600` ceiling → status | ✅ range correct | `:591` is `if _nmos_vpp_mv is not None:`; the compare is `:592` |
| `build_db.py:705` `vcc_mv` rewrite | ✅ exact | `if chip_entry["electrical"]["vcc_mv"] == _VCC_MARGIN_RAIL_MV:` |
| `build_db.py:710` `chips.append` | ✅ exact | `chips.append(chip_entry)` |
| `build_db.py:716` extra_chips merge | ✅ exact | merge comment; loop at `:721-731` |
| `build_db.py:741` `page_size` validation | ✅ exact | `emitted_page_size = chip.get("programming", {}).get("page_size")` |
| `chip_resolver.py:28` generic guard | ✅ correct | docstring `:26-32`, guard generic on `support_status != "supported"` |
| `sdp_capability.py:121` `FRAM_TOKENS` | ✅ exact | `FRAM_TOKENS: frozenset[str] = frozenset({"FM28V020", "MB85R256H"})` |
| `test_sdp_capability.py:506` | ✅ exact | `def test_all_nine_adapter_required_parts_are_refused_by_capability`; hard assert at `:519` |
| `test_chip_resolver.py:87` | ✅ exact | `def test_resolve_chip_adapter_required_raises_not_implemented(db):` |
| `test_sdp_honesty.py:59` | ✅ exact — but it is a **comment line**, not an assertion | `# protocol part, and the nine adapter-required parts) was pruned with the` |
| `test_build_db_inclusion.py:64` | ✅ near | class docstring line; the failing assert is `:97` |
| `test_characterization.ambr` FM1608 | ✅ found | `:1001` — `\| FM1608 \| RAMTRON \| 28 \| \| FRAM \| - \|` |

**Not verified — does not exist:** `tools/diff_db.py` (referenced by the field-inventory golden's
`meta`). Also note `firestarter/data/database_overrides.json` is declared in
`pyproject.toml` `[tool.setuptools.package-data]` but does not exist on disk.

---

## Runnable Verify Commands

Verbatim, with cwd and a stateable failure signal. `[MEASURED]` — every one was executed during this
research.

| # | cwd | Command | Pass signal | Fail signal |
|---|---|---|---|---|
| 1 | `/workspaces/firestarter_app` | `python tools/build_db.py` | exit 0; stdout ends `= 746 total.` | non-zero exit; a `ValueError` traceback |
| 2 | `/workspaces/firestarter_app` | `git diff --stat -- firestarter/data/chip_database.json` | for D-09-only task: **empty output** | any output |
| 3 | `/workspaces/firestarter_app` | `python -m pytest tests/ -o addopts="" -q` | `2024 passed` (pre-change) / expected new count; `0 failed` | any `FAILED` line |
| 4 | `/workspaces/firestarter_app` | `python -m pytest tests/test_datasheet_overrides.py -o addopts="" -q` | all pass | any `FAILED` |
| 5 | `/workspaces/firestarter_app` | `ruff check firestarter/ tests/` | `All checks passed!` | any diagnostic |
| 6 | `/workspaces/firestarter_app` | `ruff format --check firestarter/ tests/` | `N files already formatted` | `would reformat` |
| 7 | `/workspaces/firestarter_app` | `git diff --cached -- '*.py' \| /usr/bin/grep -E '^\+\s*#' \| /usr/bin/grep -v '^\+\s*#!'` | **prints nothing** | any line |
| 8 | `/workspaces/firestarter_app` | `python -c "import json;d=json.load(open('firestarter/data/chip_database.json'));print([r['programming']['pulse_duration_us'] for r in d['FUJITSU'] if 'MBM27C1000' in r['part_number']])"` | `[500]` | anything else |

### ⚠️ Run the suite on Python 3.11, not the devcontainer default `[MEASURED]`

| Interpreter | Result |
|---|---|
| **3.11.16** (CI's version) | `2024 passed in 198.32s`, `32 snapshots passed` |
| **3.12.14** (devcontainer default) | `1995 passed, 29 errors in 203.67s` |

The 29 are **collection errors** in `tests/test_characterization.py`, exactly the symptom
`firestarter_app/CLAUDE.md` documents (*"A later interpreter turns some snapshot failures into
collection errors, so a green local run does not prove a green CI run"*). The 29-test gap is the
whole of `test_characterization.py` — **which is one of the files this phase must touch.** A plan that
verifies on 3.12 will not see the `.ambr` snapshot failure at all.

Exact 3.11 setup used (writable cache is required — `~/.cache` is not writable in this container):

```bash
export S=<scratch>
export UV_CACHE_DIR=$S/uvcache XDG_CACHE_HOME=$S/xdg
uv venv --python 3.11 $S/v311
cd /workspaces/firestarter_app
VIRTUAL_ENV=$S/v311 uv pip install -e '.[test]'
$S/v311/bin/python -m pytest tests/ -o addopts="" -q
```

`-o addopts=""` is required to see the count line: `pyproject.toml:97` sets `addopts = "-ra -q"` and
doubling `-q` suppresses it.

### `tests/test_flash_path_record_sync.py` — not applicable here `[MEASURED]`

It does not exist in `firestarter_app` (it lives in `firestarter_fw`). Nothing in this phase
interacts with it. The related hazard that *does* apply: installing into a venv can create an
`*.egg-info/` directory in the repo — verified clean after the 3.11 install above
(`git status --porcelain` showed only the three untracked datasheet PDFs).

---

## Datasheet Provenance and Git-Tracking Gap

`[MEASURED]` `git ls-files datasheets/` in `firestarter_app` returns 9 files. The working tree has 12.

| File | Tracked? | Text layer? | Needed by Phase 197 |
|---|---|---|---|
| `MBM27C1001.pdf` | ✅ tracked | yes (OCR, 12 pp) | ✅ justifies `FUJITSU/MBM27C1001` |
| `MBM27C4001.pdf` | ❌ **untracked** | no — pure scan, 0 fonts | ✅ justifies the `MBM27C4001` no-op record |
| `MBM27128.pdf` | ❌ **untracked** | no — pure scan, 0 fonts | ✅ justifies `FUJITSU/MBM27128` |
| `LST62832I.pdf` | ❌ untracked | — | no |
| `MBM27C1000.pdf` | ❌ **absent** — must be fetched from gh#70 | no — pure scan | ✅ justifies `FUJITSU/MBM27C1000` |

**Plan actions:** download the gh#70 attachment to `datasheets/MBM27C1000.pdf`, then
`git add datasheets/MBM27C1000.pdf datasheets/MBM27C4001.pdf datasheets/MBM27128.pdf`.

**Note on reading these scans:** `poppler-utils` is not installed and cannot be installed without
root in this container. `pip install pymupdf` works and was used here. Three of the four PDFs have no
text layer at all, so a `grep`-style check of a datasheet citation is impossible — they must be
rendered and read visually (`page.get_pixmap(dpi=160).save(...)`). Budget for that if a task asks an
executor to re-verify a datasheet value.

---

## gh#70 — What the Answer Must Actually Say (PULSE-04)

`[MEASURED from the issue thread]` gh#70 is `[dev test] MBM27C1000 — FAIL (6fa1bb16ce43)`, OPEN,
labels `dev-test`, `cause:firmware`, `cause:database`. Host `3.0.0b39`, firmware `3.0.0b27:uno`,
`Rev 2.0-class`. `id` OK, `read` OK ×2, `write-partial` **BAD** — *"Byte at 0x01ff00 failed to program
within 25 pulses"*, `verify` **BAD** — *"0x02 != 0x03 at 0x01ff00"*.

The thread already contains three things the answer must respect:

1. **The reporter supplied the real MBM27C1000 datasheet** and confirmed 0.50 ms / 12.5 V / 6.0 V /
   mfr `#04` device `#E5`. The answer should credit that and confirm it was read, not merely
   accepted.
2. **The maintainer has already posted a competing hypothesis** and asked for it not to harden the
   wrong way: all three Fujitsu reports (#66 `0x07ff00` on a `0x80000` part, #70 `0x01ff00` on a
   `0x20000` part, #71 `0x003f01` on a `0x04000` part) stop at *"the first byte of the final 256-byte
   block"*, on three parts of three different sizes; raising VPP into the datasheet window moved the
   failure not at all; it reproduced across multiple physical chips; and six firmware versions changed
   nothing. His conclusion: *"That is an observation, not a conclusion … it now looks unlikely to be
   the cause of *this* failure signature."*
3. **The issue is explicitly tracking two separable things** — the pulse-width and VCC database
   defects, and the final-block boundary.

**Therefore PULSE-04's answer must NOT claim the failure is fixed.** It must say, precisely:

- the database defect is real and corrected: `pulse_duration_us` 100 → **500 µs**, from the part's
  own datasheet (`tPW` 0.475/0.50/0.525 ms, p.4-68), now vendored at `datasheets/MBM27C1000.pdf`;
- the carrying version;
- that the firmware emits `pulse_delay` as the initial pulse of a verify-per-pulse loop capped at 25
  pulses, and **does not** emit the datasheet's `tOPW` over-program pulse
  (`eprom_params.cpp` `overprogram_factor = 0` on all three 27C rows), so the corrected value is a
  more correct Quick Pro but still not a complete one;
- that the 6.0 V VCC gap is unaddressed here (Phase 200);
- that the final-block hypothesis stands and is not closed by this change;
- **and, new from this research:** that the MBM27C1000's own pin assignment puts `/OE` on pin 2 and
  `A16` on pin 24, which is the **opposite** of `DIP32_27C020` and of the earlier cross-check drawn
  from the MBM27C1001 datasheet — a finding that may explain the deterministic top-of-address-space
  stop far better than any timing or voltage margin, and which is being routed separately.

Withholding the last point while posting "we fixed the pulse" would be the same class of error the
maintainer's own comment warns against.

---

## Recommended Task Decomposition

Not a plan — a dependency-ordered sketch the planner can restructure.

| Wave | Task | Why here |
|---|---|---|
| 0 | Escalate C-1 (D-07) to the operator. | It changes whether a safety guard is touched. Everything else is independent of the answer. |
| 0 | Vendor + `git add` the four datasheets. | OVR-03 citations must resolve. |
| 1 | **D-09 alone.** Derive away `_PGM_ON_PIN31_MAX_SIZE`; regenerate; `cmp` against `git show HEAD:…`. | One-way-in-effect. Prove it in isolation, where "byte-identical" is an unambiguous signal. |
| 2 | Hoist decoded values into named locals; keep the `chip_entry` literal intact; generalise the ceiling check to the effective `vpp_mv` (keep `>`). Regenerate; must be byte-identical. | Pure refactor. Byte-identity is the proof. Everything downstream needs it. |
| 3 | Land `tools/datasheet_overrides.json` + loader + `tests/test_datasheet_overrides.py` with all five fail-closed legs. File contains only the 6 NMOS entries. Delete `NMOS_TRUE_VPP_MV`. Regenerate; must be byte-identical. | D-06 promises zero diff. Proving it here isolates the mechanism from the corrections. |
| 4 | D-08: delete `_ETYPE_RELABEL`. Update `test_build_db_inclusion.py` FM1608 assertion, re-record the `.ambr` snapshot. | 1 row, 2 fields. |
| 5 | PULSE: add the 3 entries (`MBM27C1000` 500, `MBM27C1001` 500, `MBM27128` 1000). **No entry for `MBM27C4001`.** | 3 rows. |
| 6 | Re-derive `tests/golden/wire_dict_expected_deltas_197.json`; bump `84` → `87`; extend the layer chain. | Depends on waves 4–5 being final. |
| 7 | D-12 inventory file + backlog item; PULSE-01 finding written into `tools/DECODE-NOTES.md` (new section) or the phase directory. | Bookkeeping. |
| 8 | PULSE-04: post on gh#70 after the carrying version exists. | Needs a released version. |
| — | D-07 execution, if the operator approves. | Gated on wave 0. |

**Note on wave 7:** `tools/DECODE-NOTES.md` has 8 numbered sections (`§0`–`§7`); §5 is already
*"FM1608 identity (no decode change — already correct in the DB)"* and will need a correction note
after D-08. A new §8 for the `pulse_delay` finding is the natural home, and it is prose in a markdown
file, not a source comment, so the no-comments rule does not apply.

---

## Project Constraints (from CLAUDE.md)

Extracted from `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md`. The planner must
verify compliance.

1. **Write NO comments into product source.** Everything under `firestarter_fw/` and
   `firestarter_app/`. Not `#`, not `//`, not `/* */`, for any reason. Not overridable by a plan,
   task, skill or subagent instruction. This covers `tools/build_db.py` and everything in `tests/`.
   - **Planners: do not write "add a comment citing X" into a plan, and do not make "a comment
     exists" an acceptance criterion.**
   - **Executors: if an existing plan instructs a source comment, do not add it; record the deviation
     in `SUMMARY.md`.**
   - **This phase deletes three blocks from a comment-dense file.** `build_db.py` carries long
     explanatory comments attached to each hardcode. Deleting a hardcode orphans its prose. The rule
     requires reading the remainder and confirming it still parses and that every pronoun still has
     an antecedent. **Add nothing new.** Concretely: `:60-68` (the NMOS paragraph inside the `VPP_MV`
     comment), `:85-86`, `:493-505`, `:568-572`, `:581-585`, and the `_PGM_ON_PIN31_MAX_SIZE`
     neighbourhood at `:144-148` all need reading after their subjects are removed.
   - **Docstrings are exempt**, and Click docstrings are user-facing `--help` text — never touch them
     as if they were comments. No Click command is in this phase's scope.
   - **`tests/test_sdp_honesty.py:59` is a comment.** Deleting the stale clause is allowed; rewording
     it adds a `+#` line and trips the pre-commit check.
2. **Pre-commit check, mandatory, must print nothing** (pathspec is load-bearing):
   `git -C firestarter_app diff --cached -- '*.py' | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!'`
3. **`chip_database.json` is GENERATED. Never hand-edit.** Every change goes through
   `tools/build_db.py`.
4. **Host-only phase.** No firmware change. `firestarter_fw/` was read for semantics only.
5. **Messages are generated only in the meta repo.** Not touched here.
6. **Milestone work forks off `beta`, in all three repositories.** Branch `v1.X-slug`. Never commit to
   `beta` or `main` directly. **⚠️ `firestarter_app` is currently on branch `beta` at `70c92ce`** —
   it must be moved to `v1.40-program-parameter-fidelity` before any commit lands.
7. **A push to `beta` in `firestarter_app` PUBLISHES to PyPI.** No path filter. A PyPI version can
   never be reused.
8. **Python floor is 3.11.** CI pins 3.11; the devcontainer default 3.12 masks 29 tests.
9. **`firestarter_app/tools/` is outside every CI gate** — no mypy, no `ruff check`, no
   `ruff format`. `ruff` selects `["E","F","I","UP"]` with `E501` ignored; a `# noqa` outside that
   selection is inert (and would be a comment anyway — forbidden).

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Reading a sibling JSON data file into the generator | A bespoke loader with a new error convention | The `extra_chips.json` merge shape (`build_db.py:716-737`) for *mechanism* only | Tested precedent. But its **semantics are the opposite** — fully-specified rows appended post-decode, versus partial-field substitution pre-derivation. Copy the file-reading, not the merging. |
| Testing generator internals | A subprocess that runs `build_db.py` and greps stdout | `from tools import build_db` in a `tests/` module | Existing precedent (`test_build_db_interpret_timing.py:40`). Runs in CI, gets ruff coverage, and reaches branches a regeneration cannot. |
| Proving a refactor changed nothing | Spot-checking a handful of rows | `cmp` the regenerated file against `git show HEAD:firestarter/data/chip_database.json` | The pipeline is **byte-reproducible** — measured. A weaker check throws that away. |
| A 746-row diff | A committed `tools/diff_db.py` | A throwaway field-path diff script (25 lines, given above) | `tools/diff_db.py` was deleted once already; the golden's `meta` still references it. A committed tool becomes another ungated file in `tools/`. |
| Detecting schema drift | A new marker field on overridden rows | Nothing — provenance lives in the override file | `test_chip_database_field_inventory.py` freezes the emitted key set *and* per-key counts. Adding a field trips it and has firmware-parity consequences. Explicitly deferred in CONTEXT.md. |
| A no-op / stale-value check | Prose in the override file saying what the old value was | D-04's `{"was": …, "is": …}` asserted against the live decode | Prose rots silently. An assertion fails the build. |

---

## Common Pitfalls

### Pitfall 1: refactoring `chip_entry` out of a dict literal
**What goes wrong:** `test_generator_emits_no_key_outside_the_frozen_inventory` ast-walks for a
`chip_entry = {…}` `ast.Dict`. A `dict(decoded)` or `{**decoded}` form collects zero keys → RED.
**Avoid:** keep the literal, change only its right-hand sides.
**Warning sign:** the failure message names *removed* keys, not added ones.

### Pitfall 2: writing an override entry for `MBM27C4001`
**What goes wrong:** its datasheet agrees with the decode; D-04/OVR-04 make a no-op a build failure.
**Why it happens:** D-10 says "up to 9 rows", which invites one entry per datasheet-covered row.
**Avoid:** record the verification in the D-12 inventory, not in the override file.

### Pitfall 3: changing the ceiling comparison to `>=`
**What goes wrong:** six rows flip to `vpp-exceeds-max`, their algorithm demotes to
`NON_DISPATCHABLE_ALGO`, and `test_resolve_chip_m2716…` reddens.
**Why it happens:** the source comment at `:64-68` reads as though 25 V parts are already refused.
**Avoid:** keep `>`. The boundary question belongs to Phase 199.

### Pitfall 4: verifying on the devcontainer's Python 3.12
**What goes wrong:** the 29 `test_characterization.py` tests never run, so the `.ambr` snapshot
failure this phase causes is invisible.
**Avoid:** the `uv venv --python 3.11` recipe above. Check the count line says 2024, not 1995.

### Pitfall 5: taking D-14's test list as the work item
**What goes wrong:** three legs are rewritten that did not need it, and
`tests/test_wire_dict_equivalence.py` is discovered red at the end.
**Avoid:** use `## The Definitive Red List`. Re-measure after every wave.

### Pitfall 6: assuming `MBM27C1001.pdf` covers `MBM27C1000`
**What goes wrong:** an OVR-03 citation that D-02 exists specifically to forbid, on a part whose real
datasheet differs in pin assignment.
**Avoid:** vendor the gh#70 attachment.

### Pitfall 7: reflowing an orphaned comment after deleting a hardcode
**What goes wrong:** the no-comments rule forbids adding a `#` line, so "fixing" a broken sentence by
rewriting it trips the pre-commit check.
**Avoid:** delete whole comment blocks that lose their subject. Do not rewrite them.

### Pitfall 8: diffing against `tools/baseline/chip_database.baseline.json`
**What goes wrong:** it is stale (475,857 bytes vs the live 432,461) and produces a huge spurious diff.
**Avoid:** diff against `git show HEAD:firestarter/data/chip_database.json`.

### Pitfall 9: committing on `beta`
**What goes wrong:** `firestarter_app` is currently checked out on `beta`, and a push there publishes
to PyPI. A version can never be reused.
**Avoid:** create/checkout `v1.40-program-parameter-fidelity` in `firestarter_app` first.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Python | everything | ✅ | 3.12.14 default | — |
| Python 3.11 | matching CI | ✅ via `uv` | 3.11.16 | none — 3.12 masks 29 tests |
| `uv` | 3.11 venv | ✅ | `/usr/local/bin/uv` | needs `UV_CACHE_DIR` + `XDG_CACHE_HOME` redirect; `~/.cache` is unwritable |
| `pytest` | test suite | ✅ | 9.1.1 | — |
| `ruff` | CI parity | ✅ in the `.[test]` extra | — | — |
| `mypy` | local pre-commit only | ✅ | `/usr/local/py-utils/bin/mypy` | not a CI gate |
| Network to `gitlab.com` | `build_db.py` fetch | ✅ | HTTP 200, 17,861,009 bytes | **none** — no vendored `infoic.xml` |
| `gh` CLI | gh#70 | ✅ | — | needs `XDG_CACHE_HOME` set |
| `poppler-utils` | reading scanned datasheets | ❌ | — | `pip install pymupdf` (works, no root) |
| root / `apt-get` | — | ❌ | — | — |

**Missing with no fallback:** none blocking.
**Missing with fallback:** `poppler-utils` → `pymupdf`; writable cache dirs → env redirect.

---

## Validation Architecture

### Test framework

| Property | Value |
|---|---|
| Framework | pytest 9.1.1 + `syrupy` (`.ambr` snapshots) |
| Config | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]`, `testpaths = ["tests"]`, `addopts = "-ra -q"` |
| Quick run | `python -m pytest tests/test_datasheet_overrides.py tests/test_build_db_inclusion.py -o addopts="" -q` |
| Full suite | `python -m pytest tests/ -o addopts="" -q` (**on 3.11**) |
| Baseline | `2024 passed in 198.32s`, `32 snapshots passed` |
| Snapshot update | `python -m pytest tests/test_characterization.py --snapshot-update` |

### Requirements → test map

| Req | Behaviour | Type | Command | Exists? |
|---|---|---|---|---|
| OVR-01 | override file is read and applied | unit | `pytest tests/test_datasheet_overrides.py -o addopts="" -q` | ❌ Wave 0 |
| OVR-02 | no-op entry rejected | unit | same | ❌ Wave 0 |
| OVR-03 | every entry names a datasheet; the path exists in the repo | unit | same | ❌ Wave 0 |
| OVR-04 | unknown part / unknown field / no-op / stale `was` / duplicate target all raise | unit ×5 | same | ❌ Wave 0 |
| OVR-05 | regeneration diff is exactly the expected rows | integration | `python tools/build_db.py && git diff --stat -- firestarter/data/chip_database.json` | uses existing tooling |
| OVR-06 | no part-number literal survives in `build_db.py` | unit (source scan) | a new AST/grep leg — see note | ❌ Wave 0 |
| PULSE-01 | decode rule unchanged; finding recorded | doc + existing | `pytest tests/test_build_db_interpret_timing.py -o addopts="" -q` | ✅ exists |
| PULSE-02 | `MBM27C1000` in 475–525 µs | integration | verify command #8 above | ❌ Wave 0 |
| PULSE-03 | 746-row diff accounted for | manual + script | the diff script above | ❌ Wave 0 |
| PULSE-04 | gh#70 answered | manual | `gh issue view 70 --repo henols/firestarter` | manual-only — needs a released version |

**Note on OVR-06's test:** `firestarter_fw` precedent shows source-scanning gates fail OPEN on a
rename. A "no part-number literal in `build_db.py`" scan must be written so that it fails closed —
assert against a **frozen allow-list of surviving literals** rather than grepping for a regex that
might match nothing after a refactor. Success criterion 2 explicitly permits survivors that are
"named with the proof that no alternative exists", so an allow-list is the right shape.

### Wave 0 gaps

- [ ] `tests/test_datasheet_overrides.py` — OVR-01..04, 5 fail-closed legs + happy path
- [ ] `tests/golden/wire_dict_expected_deltas_197.json` — 3 entries
- [ ] a source-scan leg for OVR-06 with a frozen allow-list
- [ ] no framework install needed

---

## Security Domain

`security_enforcement` is not disabled in `.planning/config.json`. Applicability is narrow: this is
an offline build-time code generator with no user input, no network input beyond one pinned URL, and
no authentication surface.

| ASVS category | Applies | Control |
|---|---|---|
| V2 Authentication | no | no auth surface |
| V3 Session Management | no | no sessions |
| V4 Access Control | no | local CLI |
| V5 Input Validation | **yes** | the override file is trusted repo content, but the loader must still fail closed on structure, unknown keys, and unknown field paths — OVR-04 is the control |
| V6 Cryptography | no | none used |
| V10 Malicious Code | **yes** (weakly) | `MINIPRO_XML_URL` is pinned to commit `a8efaedc`, which is the existing supply-chain control. Do not unpin. |

| Threat pattern | STRIDE | Mitigation |
|---|---|---|
| A silently-wrong override ships a hazardous voltage or pulse to the firmware | Tampering | D-03 pre-derivation substitution + the **generalised** ceiling check; D-04's `was`-assertion |
| A stale override survives an upstream decode change | Tampering | D-04's `was`-vs-live-decode assertion fails the build |
| Two override entries racing on one row | Tampering | duplicate-target fail-closed leg |
| A derivation error puts VPP on an address line (D-09) | Tampering | byte-identical regeneration, proven, plus the exhaustive integer identity |
| Unpinning the upstream XML | Supply chain | `MINIPRO_XML_URL` stays pinned |

**No new external package is installed by this phase**, so `## Package Legitimacy Audit` is not
applicable. (`pymupdf` was used only as a research tool in a scratch environment and must not enter
`pyproject.toml`.)

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The pinout swap explains the deterministic `0x…FF00` write failure on `MBM27C1000`. The **pinout mismatch itself is MEASURED**; the causal chain is INFERRED and has not been bench-tested. | PULSE-02 ⚠️ | gh#70's answer over-claims. Mitigated by phrasing it as an observation to route, exactly as the maintainer phrased his own. |
| A2 | `MBM27128`'s corrected value should be 1000 µs (Quick Pro) rather than 50000 µs (conventional). Grounded in firmware semantics (verify-per-pulse, `max_pulses = 25`), which is MEASURED — but the operator has not ruled on which datasheet figure the field carries. | PULSE-02 | A 50 ms pulse would exceed the 0x07 row's uncapped budget in practice and take ~9 hours for 16 KB. The 1000 µs reading is strongly indicated; still, confirm. |
| A3 | `programming.algorithm` and `pinout` should be excluded from the overridable field set in this phase. A recommendation from the `_upstream_proto_id` ordering hazard, not an operator decision. | Integration Point | Phases 198–200 may want one of them; widening is additive, so the cost is low. |
| A4 | The file should be named `tools/datasheet_overrides.json` with a `{"was":…,"is":…}` shape. Explicitly Claude's Discretion; no operator input. | Override File | Renaming later rewrites every entry across four phases (D-01's stated reversibility cost applies to the shape too). Worth a checkpoint. |
| A5 | The D-12 inventory belongs in the phase directory as `197-PULSE-INVENTORY.md`. Discretion item; no operator input. | D-12 | Trivially movable. |
| A6 | Deleting `_AT28C_DIP24_NAMES` is still worth doing even though it achieves nothing beyond a reason-string swap. Not decided — depends on the C-1 escalation. | Contradictions C-1 | If the operator wants the nine parts `supported`, the damage guard must change and this phase's risk profile changes with it. |

---

## Open Questions (ALL RESOLVED — see the resolution line under each)

*Resolved during `/gsd-plan-phase 197`. Each question below keeps its original wording; the
**Resolution** line records what settled it and where that decision now lives.*

1. **Does the operator want the HARDWARE-DAMAGE GUARD narrowed?** (C-1)
   - Known: the nine rows are selected by `flags & 0x10`, not by the name list; they resolve to
     `DIP24_2816`, which has `rw-pin: [21]` and no `vpp-pin`, so the guard's stated 12 V hazard does
     not apply to them.
   - Unclear: whether the operator's *"no adapter shall be needed at all"* extends to removing a
     guard he has not been shown.
   - Recommendation: **escalate before planning.** Do not delete the guard on the strength of D-07,
     which describes a different mechanism.
   - **Resolution — escalated and answered.** The operator ruled: delete the name list now, route the
     guard narrowing to Phase 199. Recorded as **D-15** in `197-CONTEXT.md`. Plan 04 deletes only the
     name list and asserts the guard's condition and reason string are byte-unchanged; the evidence
     for Phase 199 lands in `.planning/notes/197-at28c-guard-evidence-for-phase-199.md`.

2. **Which `MBM27128` figure does the field carry — 1000 µs or 50000 µs?** (A2)
   - Known: the datasheet gives both; the firmware implements the Quick Pro shape.
   - Recommendation: 1000 µs, recorded with the reasoning in the override entry's `note`.
   - **Resolution — 1000 µs, as recommended.** Settled on the firmware's own shape rather than left
     to preference: `pulse_duration_us` is the initial pulse of a verify-per-pulse loop capped at 25
     pulses with `overprogram_factor = 0`, which is the Quick Pro algorithm, not the conventional
     50 ms single shot. Recorded as **D-19** in `197-CONTEXT.md`; carried by plan 05.

3. **Is `FUJITSU/MBM27C1000`'s `DIP32_27C020` assignment a live hazard?**
   - Known: the datasheets put `/OE` and `A16` on opposite pins between the two parts, and the
     database gives them the same pinout key.
   - Unclear: which of the two the RURP actually drives correctly, and whether any other 32-pin row
     is mis-assigned the same way.
   - Recommendation: file against the `pinout-address-width-and-we-pin-corrections.md` todo. **Out of
     scope here**, but it must be in gh#70's answer.
   - **Resolution — filed and disclosed, not fixed.** Pinout correctness is out of scope per the phase
     `<domain>`. Plan 07 files it to the backlog; plan 08 requires gh#70's answer to disclose it
     rather than let the pulse fix read as closing the issue.

4. **Should the ceiling comparison become `>=`?**
   - Known: six rows sit exactly on 25000 and ship `supported`; the shield reaches ~22 V.
   - Recommendation: **not this phase.** Phase 199 owns rail ceilings and the warn-on-shortfall
     surface. Flagged so it is not lost.
   - **Resolution — deferred to Phase 199, comparison stays `>`.** Settled by scope: the phase
     `<domain>` puts rail ceilings and the warn-on-shortfall surface in Phase 199. Changing `>` to
     `>=` here would flip the six rows sitting exactly on 25000 and redden `test_chip_resolver.py`.

---

## Sources

### Primary (HIGH confidence — read directly this session)

- `firestarter_app/tools/build_db.py` — read in full, 764 lines
- `firestarter_app/tools/extra_chips.json`, `tools/DECODE-NOTES.md` (section index)
- `firestarter_app/firestarter/data/chip_database.json` (746 rows), `firestarter/data/pinouts.json` (16 keys)
- `firestarter_app/tests/` — `test_chip_database_field_inventory.py`, `test_wire_dict_equivalence.py`,
  `test_build_db_inclusion.py`, `test_sdp_capability.py`, `test_chip_resolver.py`, `test_sdp_honesty.py`,
  `test_build_db_interpret_timing.py`, `test_extra_chips_supplement.py`, `test_cli_handlers.py`,
  `test_chip_test.py`, `__snapshots__/test_characterization.ambr`
- `firestarter_app/tests/golden/chip_database_field_inventory.json`
- `firestarter_app/pyproject.toml`, `.github/workflows/ci.yml`, `firestarter_app/CLAUDE.md`
- `firestarter_fw/src/proms/eprom.cpp`, `src/proms/eprom_params.cpp`, `include/eprom_params.h`,
  `src/proms/eprom_budget.cpp`
- `minipro infoic.xml` @ `a8efaedc236c1d9718bd28299dfbb99536b010ff` — fetched, 17,861,009 bytes
- **Datasheets, read page by page (rendered at 160–520 dpi where there is no text layer):**
  - Fujitsu `MBM27C1000-15/-20/-25`, April 1988, Edition 2.0 — pp. 4-61, 4-68 (gh#70 attachment)
  - Fujitsu `MBM27C1001-15/-20/-25`, April 1988, Edition 2.0 — pp. 9-83, 9-86, 9-88, 9-90, 9-91
  - Fujitsu `MBM27C4001-12-X/-15-X`, March 1993, Edition 1.0 — pp. 1, 8
  - Fujitsu `MBM27128-25/-30` — pp. 4-16, 4-19, 4-20
- `github.com/henols/firestarter` issue #70 — full body + 3 comments, via `gh issue view`
- `/workspaces/CLAUDE.md`, `/workspaces/.planning/REQUIREMENTS.md`,
  `/workspaces/.planning/phases/197-…/197-CONTEXT.md`

### Measurements performed this session (HIGH confidence)

- Full suite, Python 3.11.16, unchanged DB: `2024 passed in 198.32s`
- Full suite, Python 3.12.14, unchanged DB: `1995 passed, 29 errors`
- Full suite, Python 3.11.16, **simulated post-change DB**: `5 failed, 2019 passed in 182.91s`
- Scratch regeneration, unmodified generator: **`cmp`-identical to the shipped database**
- Scratch regeneration, D-09 substitution only: **`cmp`-identical**
- Scratch regeneration, all Phase-197 changes: 13 changed rows, enumerated above
- Exhaustive integer check of the D-09 identity over `[0, 2_100_000)`: 0 mismatches
- D-01 uniqueness: 746 rows → 1113 distinct `(mfg, alias)` pairs, **0 collisions**; 953 bare aliases,
  152 collisions; 234 comma-joined `part_number` values

### Secondary (MEDIUM confidence)

- `@dim20`'s summary on gh#70 of the MBM27C1000 datasheet — **independently verified** against the
  attached PDF; every figure matched

### Not used

No WebSearch was performed. Every claim in this document traces to a file in this workspace, a
network fetch of the pinned upstream XML, the gh#70 thread, or a command executed here.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| The five contradictions (C-1..C-5) | **HIGH** | Each measured by a full simulated regeneration and/or a full test-suite run |
| PULSE-01 finding | **HIGH** | Positive datasheet match on the raw value, plus a 675-entry distribution, plus firmware semantics read from source |
| PULSE-02 values | **HIGH** | Read visually from each part's own datasheet at 160–520 dpi |
| D-09 derivation | **HIGH** | Proven twice — byte-identical regeneration and exhaustive integer check |
| D-01, D-06, D-12 | **HIGH** | Exact counts reproduced |
| Integration-point design | **HIGH** | Forced by a measured AST-walking test; not a preference |
| Override file name/shape | **MEDIUM** | Discretion item, reasoned but not operator-confirmed (A4) |
| `MBM27128` = 1000 µs | **MEDIUM** | Firmware semantics are measured; the datasheet offers two figures (A2) |
| Pinout-swap causal chain | **LOW** | The mismatch is measured; the failure explanation is inferred and unbenched (A1) |

**Research date:** 2026-09-18
**Valid until:** 2026-10-18 — or immediately invalidated by any change to `tools/build_db.py`,
`firestarter/data/chip_database.json`, or the pinned `MINIPRO_XML_URL`.
