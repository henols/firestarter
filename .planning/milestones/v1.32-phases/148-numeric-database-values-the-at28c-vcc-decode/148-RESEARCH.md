# Phase 148: Numeric Database Values & the AT28C VCC Decode - Research

**Researched:** 2026-08-19
**Domain:** Host-side generated-database schema migration + a decode-semantics correction, `firestarter_app/` only
**Confidence:** HIGH (nearly every claim below is a command output against the live tree)

> **Scope of this document.** CONTEXT.md's D-01…D-17 are LOCKED and are *not* re-opened here. This
> research answers only what a planner cannot get from CONTEXT.md: the exact current shape of every
> edit site, whether CONTEXT.md's load-bearing measurements still hold, the complete consumer
> inventory, the concrete test/proof mechanics, and the gate/regeneration preconditions.
>
> **Six findings contradict statements in CONTEXT.md.** They are collected in
> §"Flagged Findings" with evidence. None of them touches a locked decision — every one is a
> *measurement* CONTEXT.md asserted that the live tree disagrees with. Three of them would cause a
> plan to write an **unachievable acceptance criterion** if carried forward verbatim. Read that
> section before writing criteria.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: The measured premise — `vcc: "4V"` is a FAITHFUL decode, not a defect.**
  `VCC_VOLTAGES` (`tools/build_db.py:193`) maps index `0x02 → "4V"` and is tagged
  `[VERIFIED: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]]`; index `0x02`
  was **added deliberately** by the BUG-1 fix. `infoic.xml` genuinely encodes VCC-nibble `2` for
  these parts. The defect is **semantic, not arithmetic**: minipro's `vcc` is the TL866's
  low-margin VCC **verify rail**, and firestarter surfaces it as the chip's operating supply.
  This is the same category error the shipped SRAM block (`build_db.py:807-821`) already corrects
  for static-memory parts.
  **Consequence:** DATA-01's stated premise ("a genuine decode defect") and its stated target
  ("the datasheet's 4.5 V minimum") are both wrong. This is the **Phase 147 D-05/D-06 shape** —
  see D-04.

- **D-02: The target is 5000 mV — `vdd`, not 4500 mV.** `vdd` is itself an `infoic.xml`-decoded
  value, so substituting it invents nothing and DATA-04's proof rule holds cleanly. 4500 mV is a
  value `infoic.xml` does **not** carry for these parts (their nibble is `2`, not `3`), it is a
  datasheet *minimum* where every other VCC row reports the *applied* supply, and it is what the
  RURP shield actually delivers.
  **Rejected:** 4500 mV per DATA-01's literal text (invents a value, wrong quantity);
  a whole-database semantic re-derivation surfacing `vdd` as VCC everywhere (746-chip blast
  radius, and UV-EPROM `vdd` is the 6.5 V **program** rail on 105 chips — it must never become
  the "VCC:" row).

- **D-03: The condition is nibble-keyed and semantic — "4 V is never an operating supply".**

  ```python
  # build_db.py decode function
  _VCC_MARGIN_RAIL_MV = 4000        # VCC_VOLTAGES index 0x02
  if vcc_mv == _VCC_MARGIN_RAIL_MV:
      vcc_mv = vdd_mv
  ```

  One uniform claim about the **decode table**, keyed on nothing chip-specific — no part number,
  no type, no algorithm — so it cannot become a `_PAGE_SIZE_BY_PART` sibling.
  **Blast radius: exactly 56 chips, every one landing on 5000 mV** (55 × algorithm `0x0D`,
  1 × XICOR `X88C64P/S` algorithm `0x34`, protocol-not-implemented). No part in this database has
  a 4.0 V nominal supply, so the rule has no measured false positive.

  **This is the load-bearing measurement — do not re-derive it, and do not widen the condition:**
  `vcc != vdd` on **358 of 746** chips, and the `0x0D` family splits four ways:

  | count | vcc | vdd | aligning to vdd would give |
  |---|---|---|---|
  | 55 | 4000 | 5000 | **5000 ✓** — the intended movers |
  | 16 | 5500 | **3300** | **3300 ✗** — Microchip `28C256`, `28C16A`, `2817`… genuinely 5 V parts |
  | 12 | 5500 | 5000 | 5000 — EXEL / ST `28C64` |
  | 1 | 3300 | 5000 | 5000 |

  Measured blast radius of the conditions that were **rejected**: type-keyed
  (`type in EEPROM/Flash-EEPROM`) → **85** chips; algorithm-keyed (`algorithm == 0x0D`) → **84**;
  relation-keyed (`vcc < vdd and vdd <= 5500`) → **225** (sweeping in 168 UV-EPROMs). All three
  would set sixteen 5 V EEPROMs to **3.3 V** — worse than the `4V` being fixed. That is DATA-05's
  "the condition was too broad" guard firing before a line is written.

- **D-04: Hand-correct DATA-01 and ROADMAP criterion #1 BEFORE planning.** A criterion whose
  premise is false is how a verifier produces a false RED — or how an executor "fixes" the wrong
  thing to satisfy it. Restate both to the measured finding: the value is **5 V (= `vdd`)**, the
  correction is a **margin-rail substitution** rather than a decode-table repair, and the rule is
  keyed on the decoded value alone. Follow Phase 147's D-06 precedent exactly, including the dated
  parenthetical recording what the original text asserted and why it was superseded.
  **Mechanic:** use **hand edits** — the GSD requirements/roadmap verbs reformat the whole file
  (`_normalizeMd` blast radius). Snapshot and diff.

- **D-05: `vdd` survives as `vdd_mv` — it is load-bearing generator input, not dead data.**
  Read by the D-03 rule, by the shipped SRAM normalization, and by `diff_db.py`'s classification.
  It is not surfaced anywhere and that stays true. This is **not** the `protect_on_after` shape:
  that field states an *intent the system ignores*; `vdd_mv` is an input the generator *consumes*.
  **Rejected:** collapsing to a single resolved `vcc_mv` (destroys diff_db's ability to classify
  the two rails separately, removes the evidence trail for both normalizations, and makes the
  `vcc=5500` anomaly invisible to a future investigator); surfacing `vdd` in `firestarter info`
  (display field DATA-02 does not ask for, and UV-EPROM `vdd` is the 6.5 V program rail).

- **D-06: `vcc` is inert on the wire — state this, do not let it be forgotten.**
  `convert_to_programmer` (`database.py:536-557`) sends only `memory-size`, `algorithm`,
  `pin-count`, `vpp_mv`, `pulse-delay`, and optional `chip-id`. `vcc` and `vpp_volts` never leave
  the host, and the firmware has no VCC control register. The D-03 rule therefore **must produce
  zero wire-dict change** — an assertion worth making explicitly (see D-11).

- **D-07: The seed's schema is locked — do not re-open it.** `.planning/seeds/db-numeric-values-simplification.md`
  §"Decided design": `vcc: "5V"` → `vcc_mv: 5000`; `vdd` → `vdd_mv`; `vpp` + `vpp_mv` → `vpp_mv`
  only; `pulse_duration` → `pulse_duration_us`. `chip_id_value` **stays** a hex string (canonical
  in datasheets and `infoic.xml`; JSON has no hex literal). `type` / `support_status` / `pinout` /
  `part_number` stay categorical strings. Clean break — **no tolerant reader**.

- **D-08: The `pulse_duration_us: 0` sentinel keeps the seed's value, and the conflation is closed
  at its source.** Today `interpret_timing` (`build_db.py:412-432`) defaults `val = 0` with a
  stderr `WARN` when `pulse_delay` is unparseable, so after the collapse a `0` could mean either
  "algorithm-controlled" (417 chips) or "decode fault on a 0x07/0x08/0x0B chip". Make that
  `except (TypeError, ValueError)` branch **fatal** — the build fails rather than emitting a wrong
  `0`. Then `0` has exactly one meaning by construction. Wire behaviour is unchanged (the host
  already sends `0` for algorithm-controlled chips), and `ic_layout.py:605-607` **already** omits
  the "Pulse delay:" row on `0`, so the display convention is in place today.
  **Rejected:** shipping `0` with the conflation intact (a build emitting a wrong `0` still
  succeeds and the WARN scrolls past in CI); omitting the key for algorithm-controlled chips
  (a 329/746 sparse key — the exact hard case the field-inventory golden's own
  `why_counts_not_names` rationale warns about).

- **D-09: `audit_coverage_matrix.py`'s `parse_pulse_us` is deleted too — DATA-03's discipline is
  about the defect class, not one filename.** It is a second live string parser
  (`tools/audit_coverage_matrix.py:105-109`) that **raises** on any non-`" us"` value, called at
  ~8 sites, exercised by an imported test suite against the live database. Leaving it — or
  widening it to accept ints — is precisely the "bypassed, not gone" shape DATA-03 forbids, and a
  tolerant reader outlives the last string it was written for. Call sites read
  `chip["programming"]["pulse_duration_us"]` directly; the `_parseable_pulse_rows` filter at
  `:1718-1727` becomes `!= 0`.

- **D-10: Stale `~/.firestarter/database.json` overrides break silently — but they break, they do
  not mis-resolve.** No detection layer, no migration message, no warning: ship exactly the seed's
  clean break. **However**, read the new keys with direct indexing
  (`chip["electrical"]["vcc_mv"]`), **not** `.get(key, 0)` — otherwise a stale override missing
  `pulse_duration_us` resolves to `0`, which now means "algorithm-controlled", and a 0x07 chip is
  programmed with no pulse. Absent key ⇒ exception, never a valid-looking value. This adds no
  surface and is not a coercion layer.
  **Rejected:** a detect-and-refuse migration error naming the file and field; detect-warn-and-
  ignore (leaves the user silently running without the override they wrote).

- **D-11: `diff_db.py` gets a normalizing comparator — the migration must diff to ZERO.**
  `diff_db.py` classifies by literal field names (`:445-458`) against a pinned baseline and exits
  1 on any unexplained diff, so a key rename would make all 746 chips diff and none classify.
  Canonicalize both sides to mV / µs before comparing, so `"5V" == 5000` and `"100 us" == 100`.
  The pure-representation migration then produces **zero** diff rows and the only chips that
  surface are the 56 the D-03 rule actually moved. That artifact *is* DATA-05's proof: it
  demonstrates the migration changed no value and the rule changed exactly what it claimed.
  `tools/baseline/chip_database.baseline.json` is **NOT re-pinned** — the comparison stays live.
  A `RULE_VCC_MARGIN_RAIL` entry in `_RATIONALES` (with its minipro citation, matching the
  existing `RULE_ALGO` / `BUG2_AND_BUG3` format) is required for exit 0 — that is mechanical, not
  a choice.
  **Rejected:** two sequential passes with a `RULE_SCHEMA_NUMERIC` label and a re-pinned baseline
  (produces a 746-row "explained" artifact no reviewer can actually check, and re-pinning is what
  the field-inventory golden itself calls the silenceable move).

- **D-12: `148-DB-DIFF.md` in the phase directory is the review artifact.** It carries the
  `diff_db.py` run output, the 56-chip mover list, the D-03 justification with its citation, and
  the **explicit non-claim** that the `vcc=5500` group was deliberately left untouched. One
  document, reviewable whole, where a future investigator looks — not split across plan SUMMARYs.

- **D-13: `tests/golden/chip_database_field_inventory.json` is re-derived independently, with a
  seen-to-fail transcript.** Its own `how_to_update` forbids hand-editing a count: re-derive every
  number by a fresh two-level traversal of the regenerated database and a fresh AST walk of
  `build_db.py`'s `chip_entry` construction (unioned with `tools/extra_chips.json`), update
  `meta.recorded_at_head`, and name in the commit message which key changed on which level and
  why. Then **plant a violation, watch the gate go RED, revert, watch it go GREEN**, and commit
  both transcripts. Precedent: Phase 140 Plan 03 shipped four RED / one GREEN for this same gate.
  A golden regenerated without a fail proof is indistinguishable from a golden silenced.

- **D-14: Criterion 3 is proven by full 746-chip wire-dict equivalence, not a sample.**
  `convert_to_programmer` is the single seam where host state becomes wire values, and it has five
  keys. Capture its output for every chip on the pre-change tree, capture it again after, assert
  **byte-identical**. Total coverage in one assertion, and cheap. Per D-06 the VCC rule must show
  zero wire change — assert that too, since it is the load-bearing claim that this phase cannot
  affect `write` behaviour.
  **Rejected:** a per-protocol representative sample (a decode change moving only chips outside
  the sample passes silently — the exact defect class the field-inventory golden's
  `why_counts_not_names` rationale exists to catch); relying on the existing suite plus GATE-03
  (GATE-03 only checks `vpp_mv` against family bands; a `pulse-delay` or `memory-size` regression
  passes it, and criterion 3 would rest on an assertion nobody wrote).

- **D-15: The render helper emits byte-identical output to today — `"5.0v"`, `"12.0v"`, `"4.5v"`.**
  One-decimal, lowercase `v`, exactly as `ic_layout.py:568` produces now from the coerced float.
  `tests/__snapshots__/test_characterization.ambr:432` pins `VCC:  5.0v` / `VPP:  12.0v`, so the
  snapshot diff then changes on **exactly** the AT28C-family lines (`4.0v` → `5.0v`) and that diff
  *is* the proof that the migration changed nothing visible while the rule changed precisely what
  it claimed. Cosmetic churn would bury that signal, and v1.30 Phase 136's rule is that a pinned
  snapshot is never silently re-baselined.
  **Rejected:** datasheet style (`"5V"` / `"12.5V"`) — nicer, but it re-baselines every voltage
  line in the snapshot and makes the one line that matters indistinguishable from the ones that
  do not. Not filed as a follow-up todo either; it was considered and declined, not deferred.

- **D-16: One shared helper, in `database.py`.** It sits beside the code that owns the millivolt
  convention, in the same file the coercion layer is being deleted from — so `database.py` goes
  from "parses strings into numbers" to "owns the numeric convention and renders it", one clean
  reversal. Imported by all three call sites: `ic_layout.py:568` (`vcc_str`), `ic_layout.py:597`
  (`vpp_str`), `eprom_info.py:401` (list-view `vpp_str`). One definition, one format, one place to
  change.
  **Rejected:** hosting it in `ic_layout.py` (makes `eprom_info.py` import a formatting concern
  from a pin-diagram module); a new dedicated formatting module (a new file for one function;
  this codebase has repeatedly preferred extending an existing seam).

- **D-17: Nothing in the CLI explains the change.** The output simply becomes correct. The
  reasoning lives in `148-DB-DIFF.md`, and the user-facing statement is a `firestarter_app`
  changelog entry covering both the AT28C VCC correction and the **breaking** numeric schema
  (stale string-schema `~/.firestarter/database.json` overrides no longer load — per D-10).
  **Rejected:** surfacing the correction in `dev test` report output — a new report field with no
  consumer, the dead-data shape Phase 147 explicitly rejected in its own D-14, and it would touch
  Phase 147's file.

### Claude's Discretion

- Exact name of the D-03 constant and the D-16 helper (`_VCC_MARGIN_RAIL_MV`, `format_mv` are
  suggestions, not locks). Keep both single-sourced.
- Exact failure mechanism for D-08's fatal branch (`SystemExit` vs a raised exception) — it must
  stop the build and name the protocol and the unparseable value.
- Whether the migration and the D-03 rule land in one plan or two, provided `148-DB-DIFF.md` can
  still show them separately (D-11's comparator makes either ordering work).
- Fixture format and location for D-14's wire-dict capture.
- The `vpp_mv = ... or int(vpp_volts * 1000)` fallback in `convert_to_programmer`
  (`database.py:544-546`) is dead once the `vpp` string is gone — delete it with the rest of the
  coercion layer.

### Deferred Ideas (OUT OF SCOPE)

- **The `vcc = 5500` EEPROM-class group — 29 chips (D-03 non-claim).** Sixteen Microchip parts
  (`28C256`, `28C16A`, `28C64A`, `2817`, `2804`, `28LV64A`, …) carry `vcc: 5500` against
  `vdd: 3300`; thirteen EXEL / SGS-THOMSON / ST parts (`XL2816A`, `XLE28C64A`, `M28C64`, …) carry
  `vcc: 5500` against `vdd: 5000`. This is the same category error inverted — a **high**-margin
  verify rail surfaced as the operating supply — and it means `firestarter info` currently reports
  5.5 V for parts that run at 5 V. **Not fixed in Phase 148:** the correct target is unproven
  without establishing from `infoic.xml` what the two nibbles encode per family (algorithm `0x07`
  shows `vdd` as both 5500 and 6500, so the read-rail/program-rail reading is not uniform).
  **File as a pending todo carrying the exact counts and part list**, and state the non-claim
  explicitly in `148-DB-DIFF.md`.
- **A regression guard over the regenerated database** — asserting no chip's `vcc_mv` may fall
  below 4500, that exactly 56 chips moved `4000 → 5000`, and that no chip's `vcc_mv` ever
  decreases against the baseline. Considered and declined for this phase (D-03's rule cannot
  lower a VCC by construction), but it would have caught the rejected type-keyed rule's 3.3 V
  failure. Revisit if the `vcc=5500` group is ever taken on.
- **Datasheet-style voltage rendering** (`"5V"` / `"12.5V"` instead of `"5.0v"`) — declined, not
  deferred (D-15). It would bury this phase's one meaningful snapshot line in cosmetic churn. If
  it is ever wanted, it belongs in its own change with its own deliberate re-baseline.
- **Surfacing `vdd` in `firestarter info`** — rejected (D-05). Would need a label that cannot be
  misread as the supply, because UV-EPROM `vdd` is the 6.5 V program rail on 105 chips.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **DATA-01** | `electrical.vcc` for the AT28C family stops reporting `4V` and instead reports the 5 V supply the parts actually run at, fixed in `build_db.py`'s decode function — never in the generated JSON. *(hand-corrected 2026-08-19 per D-01/D-02/D-04)* | §"Verified Measurements" confirms all D-03 counts. §"Edit Sites" gives the exact `build_db.py:750-755` emitter and the `:807-821` SRAM precedent to mirror. §"Validation Architecture" REQ-DATA-01 supplies the missing `firestarter info AT28C256` test (there is **none** today) and the empirically captured before-state `VCC: 4.0v`. |
| **DATA-02** | Voltages stored as millivolt integers, timing as microsecond integers; no unit-suffixed string paired with its numeric twin. | §"Edit Sites" §A gives the emitter; §"Flagged Finding F-1" identifies `tools/extra_chips.json` as a **second, hand-authored** emission path CONTEXT.md does not name. §"Render Contract" enumerates every distinct value and proves `f"{mv/1000:.1f}v"` is byte-exact. |
| **DATA-03** | `database.py`'s string-coercion layer (`_map_data`'s `.replace("V","")` → `float()` and `_parse_pulse_duration`) is deleted, not merely bypassed. | §"Edit Sites" §B gives every line. §"Consumer Inventory" lists all 7 `parse_pulse_us` call sites (D-09) **plus one render-only read CONTEXT.md does not name** (`audit_coverage_matrix.py:537`). §"Validation Architecture" REQ-DATA-03 gives the 746-chip wire-dict equivalence mechanics, measured. |
| **DATA-04** | No generator field emitted that cannot be proven from `infoic.xml`; no per-chip lookup table, no `_PAGE_SIZE_BY_PART` sibling. | §"Edit Sites" §A shows the D-03 rule is a two-line value substitution keyed on nothing chip-specific. `_PAGE_SIZE_BY_PART` located at `build_db.py:146-159` (3 entries) as the anchor a plan must not extend. |
| **DATA-05** | `diff_db.py` is the review artifact; blast radius justified; GATE-03 stays green and is never weakened. | §"Validation Architecture" REQ-DATA-05 contains a **fully simulated** post-migration diff_db run with two candidate designs and their measured bucket distributions. §"Gates" confirms GATE-03 reads no migrated key and passes today (746 chips, exit 0). |
</phase_requirements>

---

## Summary

Phase 148 is a schema-representation migration plus a two-line decode-semantics correction, both
landing in `firestarter_app/tools/build_db.py`, with the consequences rippling through one
consumer file (`firestarter/database.py`), two display files, four tool/gate files, two goldens,
and one test fixture file. The working tree is in excellent shape for it: the full pytest suite is
**1616 passed** in 280 s, all four gates are green, the committed `chip_database.json` is
**byte-reproducible** from the pinned `infoic.xml` commit in **1.45 s**, and `firestarter_app` sits
on the correct milestone branch with **zero file overlap** against Phase 147.

Every load-bearing number in D-03 is **confirmed** against the live tree: 56 chips at `vcc == 4000`
(all landing on `vdd == 5000`), the four-way `0x0D` split 55/16/12/1, `vcc != vdd` on 358 of 746,
and the rejected conditions' 85/84/225 blast radii. `AT28C256` is among the 56 movers and
`firestarter info AT28C256` prints `VCC: 4.0v` today. The rule cannot lower any voltage.

**Six of CONTEXT.md's supporting statements do not survive contact with the live tree**, and three
of them would produce an unachievable acceptance criterion if a plan copied them. The largest:
`diff_db.py` does **not** currently diff to zero — it reports **744 changed chips** today, because
the pinned baseline predates Phase 136.1. "The migration must diff to ZERO" is therefore not
literally attainable; the achievable and equally strong form is *"the migration moves no chip into
a different bucket."* I built and ran a prototype normalizing comparator that proves this exactly,
and measured two candidate rule designs end to end.

**Primary recommendation:** plan against the measured numbers in §"Verified Measurements" and the
proven mechanics in §"Validation Architecture", not against CONTEXT.md's supporting prose. Adopt
comparator **Option B** (a scoped `RULE_VCC_MARGIN_RAIL` branch in `_classify_diff`, not just a
`_RATIONALES` entry) — it is the only design measured to give the 56 movers their own reviewable
bucket, which is what D-12's artifact requires. Treat the pytest suite's 280 s runtime and the
mypy gate's local unavailability as fixed constraints on task verification.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| VCC margin-rail substitution (D-03) | **Generator** (`tools/build_db.py`) | — | The project's proof rule: a value change lands in the decoder and is regenerated. The generated JSON is never hand-edited. |
| Numeric schema emission (`*_mv`, `*_us`) | **Generator** (`tools/build_db.py`) | **Hand-curated data** (`tools/extra_chips.json`) | Two emission paths exist — the decode loop *and* the byte-faithful post-decode merge. See F-1. |
| Numeric convention + mV→string render (D-16) | **Host DB layer** (`firestarter/database.py`) | — | D-16 locks it beside the millivolt convention, in the file the coercion layer leaves. |
| Human display | **Presentation** (`ic_layout.py`, `eprom_info.py`) | — | Three call sites consume the helper; none re-parses. |
| Wire values | **Host DB layer** (`convert_to_programmer`) | — | The single host→wire seam. `vcc` provably never crosses it (measured: 9 wire keys, `vcc` absent). |
| Blast-radius proof | **Gate tooling** (`tools/diff_db.py`) | Phase artifact (`148-DB-DIFF.md`) | GATE-02 owns classification; the phase doc owns the narrative and the non-claim. |
| Schema freeze | **Test gate** (`tests/test_chip_database_field_inventory.py` + golden) | — | Non-silenceable half of TABLE-05, deliberately not derived from the diff baseline. |
| Hardware-damage guard | **Gate tooling** (`tools/check_dispatch.py`) | — | Reads only `algorithm`, `type`, `vpp_mv`, `pinout`, `support_status` — **untouched by this phase** (verified). |

---

## Verified Measurements

Every D-03 number, re-measured against the committed
`firestarter_app/firestarter/data/chip_database.json` on 2026-08-19.

**Command** (single Python pass over the committed DB; `mv(s) = int(round(float(s.replace("V",""))*1000))`):

```bash
cd /workspaces/firestarter_app && python3 -c "
import json,collections
db=json.load(open('firestarter/data/chip_database.json'))
chips=[(m,c) for m,l in db.items() for c in l]
def mv(s): return None if s is None else int(round(float(str(s).replace('V',''))*1000))
print('TOTAL', len(chips))
print('vcc==4000', sum(1 for m,c in chips if mv(c['electrical']['vcc'])==4000))
print('  ->vdd==5000', sum(1 for m,c in chips if mv(c['electrical']['vcc'])==4000 and mv(c['electrical']['vdd'])==5000))
print('vcc!=vdd', sum(1 for m,c in chips if mv(c['electrical']['vcc'])!=mv(c['electrical']['vdd'])))
"
```

| D-03 claim | CONTEXT.md | Measured | Verdict |
|---|---|---|---|
| Total chips | 746 | **746** | ✅ CONFIRMED |
| `vcc == 4000` | 56 | **56** | ✅ CONFIRMED |
| …of which `vdd == 5000` | all 56 | **56 of 56** | ✅ CONFIRMED |
| `vcc != vdd` | 358 of 746 | **358 of 746** | ✅ CONFIRMED |
| Movers by algorithm | 55 × `0x0D`, 1 × `0x34` | **55 × 13 (0x0D), 1 × 52 (0x34)** | ✅ CONFIRMED |
| `0x0D` split: 4000/5000 | 55 | **55** | ✅ CONFIRMED |
| `0x0D` split: 5500/3300 | 16 | **16** | ✅ CONFIRMED |
| `0x0D` split: 5500/5000 | 12 | **12** | ✅ CONFIRMED |
| `0x0D` split: 3300/5000 | 1 | **1** | ✅ CONFIRMED |
| `0x0D` total | (implied 84) | **84** | ✅ CONFIRMED |
| Rejected type-keyed blast radius | 85 | **85 movers** (369 chips match the predicate; 85 actually change) | ✅ CONFIRMED (as *movers* — see note) |
| Rejected algorithm-keyed blast radius | 84 | **84 movers** | ✅ CONFIRMED |
| Rejected relation-keyed blast radius | 225 | **225 movers** | ✅ CONFIRMED |
| Rejected rules set 16 EEPROMs to 3.3 V | "All three" | **type-keyed: 16 ✓ · algorithm-keyed: 16 ✓ · relation-keyed: 0** | ⚠️ **F-4** — two of three |
| Relation-keyed sweeps in UV-EPROMs | 168 | **167** | ⚠️ **F-5** — off by one |
| Deferred `vcc == 5500` group | 29 (16 + 13) | **28 (16 + 12)** | ⚠️ **F-6** — off by one |

**Note on "blast radius":** D-03's 85 / 84 / 225 are counts of chips a rejected rule would
**move**, not chips matching the predicate. `type in {EEPROM, Flash/EEPROM}` matches **369** chips;
only **85** of them have `vcc != vdd` and would actually change. Both readings are defensible; the
mover reading is the one that reproduces D-03's numbers exactly, and it is the correct one for a
blast-radius argument. A plan asserting "369" would be measuring a different thing.

**The rule provably cannot lower a voltage:** all 56 movers go `4000 → 5000`. Measured
`land-LOWER-than-today = 0` for the D-03 condition, versus 28 for both rejected keyed conditions.

**AT28C256 is among the 56 movers** (`ATMEL`, `vcc: "4V"`, `vdd: "5V"`, `algorithm: 13`,
`pinout: DIP28_28C256`), and its current CLI output is captured in
§"Validation Architecture" REQ-DATA-01.

---

## Flagged Findings

> Six statements in CONTEXT.md that the live tree contradicts. **None touches a locked decision** —
> every one is a supporting measurement or mechanism claim. Reported per the research brief's
> instruction ("report it as a flagged finding with evidence — do not act on it").
> **F-1, F-2 and F-3 will produce an unachievable acceptance criterion if copied into a plan.**

### F-1 — `tools/extra_chips.json` is a **second emission path** carrying the old string schema

CONTEXT.md §"In scope" names only "`build_db.py`'s emitter". But two of the 746 chips never pass
through the decode loop at all.

`build_db.py:830-857` merges `tools/extra_chips.json` **post-decode and byte-faithful**
("the merge does not mutate any wire value"). Both records carry the old schema verbatim:

```json
"electrical": { "type": "UV-EPROM", "size_bytes": 2048, "pin_count": 24,
                "vpp": "25V", "vpp_mv": 25000, "vcc": "5V", "vdd": "6.5V" },
"programming": { "algorithm": 11, "pulse_duration": "500 us", ... }
```
— `tools/extra_chips.json` (TI `2516` and `2532`)

**Consequence:** without a hand edit to `extra_chips.json`, 2 of 746 chips ship the string schema
after the migration, and D-10's direct indexing (`chip["electrical"]["vcc_mv"]`) raises `KeyError`
on both. It is also confirmed load-bearing for D-13: the golden's own `meta.generator_scan_scope`
states `generator_emitted_chip_entry_keys` is the **union** of the `chip_entry` AST walk and an
`extra_chips.json` key scan (21 + 5 = 26 names).

The `devtest-rootcause` skill permits editing this file ("authored supplement"), but scopes it to
"chips absent from `infoic.xml` entirely". A representation migration is a different concern and
should be stated explicitly in the plan rather than assumed.

**Corroborating measurement:** the TI `2516`/`2532` records are the **only 2 chips of 746 that do
not diff against the baseline today** — precisely because they are merged byte-faithful. They will
*start* diffing once migrated, and nothing currently explains them.

### F-2 — `diff_db.py` does **not** diff to zero today; it reports **744 changed chips**

D-11: *"The pure-representation migration then produces **zero** diff rows."*

```
$ cd /workspaces/firestarter_app && python3 tools/diff_db.py ; echo EXIT=$?
--- CHANGED chips (744 total) ---
[PGSZ_PAGE_SIZE] (2 chips)
[PROV01_PROTECT_METADATA] (742 chips)
--- NEW chips (0) ---   --- MISSING chips (0) ---
PASS: all 744 changed chips explained
EXIT=0
```

`tools/baseline/chip_database.baseline.json` predates Phase 136.1 — it carries no
`protect_off_before` / `protect_on_after` / `infoic_page_size_raw` and no `page_size`, so 744 of
746 chips already diff, all explained, exit 0.

**A criterion phrased "`diff_db.py` reports 0 changed chips" is unachievable** and would produce a
false RED. The achievable, equally strong form — **measured in §"Validation Architecture"** — is:
*the migration moves no chip into a different bucket; the changed-chip total and every existing
bucket count are unchanged, and the 56 movers appear as their own new bucket.*

### F-3 — D-15's snapshot proof does not exist: **no AT28C VCC line is in any snapshot**

D-15: *"the snapshot diff then changes on **exactly** the AT28C-family lines (`4.0v` → `5.0v`)."*

```
$ grep -rn "4\.0v" tests/__snapshots__/          →  (no matches)
$ grep -n "VCC:" tests/__snapshots__/test_characterization.ambr
432:  VCC:                5.0v
```

There is exactly **one** info-view snapshot, `test_info_known_chip`, and it runs
`firestarter info W27C512` (`tests/test_characterization.py:347-353`). W27C512 has `vcc: "5V"` —
**not a mover**. The `test_list` snapshot does contain AT28C rows (`.ambr:573-582`) but the list
view renders only the VPP column, never VCC.

**Consequences, both important:**
1. The correct criterion is that the `.ambr` file is **byte-unchanged** by this phase — a stronger
   statement than D-15's, and one the migration must satisfy exactly.
2. **Criterion 1 has zero existing test coverage.** A new test asserting
   `firestarter info AT28C256` → `VCC: 5.0v` is a **Wave 0 gap** (see §"Validation Architecture").

### F-4 — Only two of the three rejected conditions produce the 3.3 V failure

D-03: *"All three would set sixteen 5 V EEPROMs to 3.3 V."*

Measured `land-on-3300` per rejected condition: type-keyed **16**, algorithm-keyed **16**,
relation-keyed **0**. The relation-keyed rule is `vcc < vdd <= 5500`, so by construction it can
only ever *raise* a voltage. Its real defect is the one D-03 also states — it sweeps in 167
UV-EPROMs whose `vdd` is the elevated program rail. The 3.3 V argument is sound for the two keyed
conditions; it does not apply to the third.

### F-5 — Relation-keyed UV-EPROM sweep is **167**, not 168

`{'EEPROM': 39, 'UV-EPROM': 167, 'Flash/EEPROM': 18, 'FRAM': 1}` = 225 total. Cosmetic.

### F-6 — The deferred `vcc == 5500` group is **28 chips (16 + 12)**, not 29 (16 + 13)

CONTEXT.md's `<deferred>` block says 29 (16 Microchip + 13 EXEL/ST). Measured: 16 at `vdd 3300`
and **12** at `vdd 5000` = **28**. Note CONTEXT.md's own D-03 table says **12** for that row — the
`<deferred>` prose disagrees with D-03 internally, and D-03 is the correct one. This matters
because D-12 requires the non-claim to carry *"the exact counts and part list"*.

### F-7 (minor) — `STATE.md:93` still carries the superseded premise

D-04's hand-correction was applied to `REQUIREMENTS.md` and `ROADMAP.md` but not to STATE.md's
phase table:

```
$ sed -n '93p' .planning/STATE.md
| 148 Numeric DB Values & AT28C VCC Decode | `vcc` decodes to the datasheet's 4.5 V in `build_db.py`; ...
```

The false "4.5 V" premise D-04 exists to eliminate is still live in one tracked file.

### F-8 (minor) — `convert_to_programmer` has **9** wire keys, not five

D-06/D-14 say five (+ optional `chip-id`). Measured union across all 746 chips:

```
['algorithm', 'bus-config', 'chip-id', 'flags', 'memory-size', 'page-size', 'pin-count', 'pulse-delay', 'vpp_mv']
```

D-06's *substantive* claim is confirmed and strengthened: **`vcc` and `vpp_volts` are absent from
all nine.** But a D-14 fixture that captures only five keys would miss `bus-config`, `flags` and
`page-size` — three real wire fields.

---

## Edit Sites — exact current code (verified against the live tree, 2026-08-19)

> CONTEXT.md's line numbers were checked one by one. **All are accurate** except
> `database.py:128-140` (actual: `128-143`) and `audit_coverage_matrix.py:1718-1727`
> (actual: `1717-1734`). Both are trivially close.

### A. `firestarter_app/tools/build_db.py` (872 lines)

| Site | Lines | Current code | Phase 148 change |
|---|---|---|---|
| `VCC_VOLTAGES` | **192-200** | `{0x00:"5V", 0x01:"3.3V", 0x02:"4V" #BUG-1 fix, 0x03:"4.5V" #BUG-1 fix, 0x04:"5.5V", 0x05:"6.5V"}`, preceded by the `[VERIFIED: minipro database.c#L130-L135 @ a8efaedc]` tag | Values become mV ints (D-07). **Table stays faithful** — index `0x02` is *not* edited (D-01). |
| `interpret_timing` | **412-432** | `try: val=int(raw_hex,16)` / `except (TypeError,ValueError):` → stderr WARN + `val=0` (`:417-427`); then `if protocol_id in (0x07,0x08,0x0B): return f"{val} us"` else `return "Algorithm Controlled"` | Return int µs; make `except` fatal (D-08). **See §"D-08 reachability" — this branch is provably dead against the pinned XML.** |
| `vpp` / `vpp_mv` emit | **737-746** | `"vpp": f"{_nmos_vpp_mv//1000}V" if … else VPP_VOLTAGES.get(voltages & 0xF0,"Unknown")` and `"vpp_mv": _nmos_vpp_mv if … else VPP_MV.get(voltages & 0xF0, 0)` | Delete the `"vpp"` string key entirely; `vpp_mv` unchanged. |
| `vcc` / `vdd` emit | **747-755** | `"vcc": VCC_VOLTAGES.get((voltages>>8)&0x0F,"5V")` (bits 11-8), `"vdd": VCC_VOLTAGES.get((voltages>>12)&0x0F,"5V")` (bits 15-12), under the `[VERIFIED: minipro database.c#L921-L923]` BUG-3 comment | → `vcc_mv` / `vdd_mv`. **Note the `"5V"` default** becomes `5000`. |
| `pulse_duration` emit | **759-761** | `"pulse_duration": interpret_timing(ic.get("pulse_delay"), proto_id)` | → `"pulse_duration_us"`. |
| **SRAM `vcc = vdd` precedent** | **807-821** | 14 lines of cited comment + `if _etype == "SRAM": chip_entry["electrical"]["vcc"] = chip_entry["electrical"]["vdd"]` | The pattern D-03 mirrors. Its comment explicitly warns UV-EPROM `vdd` is the 6.5 V program rail. Both blocks sit after `chip_entry` is built and before `chips.append`. |
| `extra_chips` merge | **829-859** | `complete_db.setdefault(mfg_name, []).extend(extra_chips)` — byte-faithful, post-decode | **Not a code change — but see F-1: the JSON it reads must be migrated by hand.** |
| `_PAGE_SIZE_BY_PART` | **146-159** | 2 entries (`W29C040:256`, `W29C020:128`), each `[CITED: …pdf §6.2]` | **Do not extend, do not add a sibling** (DATA-04 / ROADMAP must-not-do). |
| `MINIPRO_XML_URL` | **17-20** | pinned at commit `a8efaedc236c1d9718bd28299dfbb99536b010ff` | Must not drift. |

**Ordering note (a real design constraint):** the D-03 rule needs both `vcc_mv` and `vdd_mv`. The
emitter builds them inline inside the `chip_entry` dict literal at `:750-755`, so the rule cannot
sit *inside* the literal — it must be a post-construction mutation, exactly like the SRAM block at
`:820-821`. Two mutations then run in sequence (SRAM first, then the margin rail). These do not
interact: SRAM parts have `vcc` set to `vdd`, and no SRAM part has `vdd == 4000` (SRAM `vdd`
values measured: 3300 / 5000 / 5500 only).

### B. `firestarter_app/firestarter/database.py` (732 lines)

| Site | Lines | Current code |
|---|---|---|
| `_parse_pulse_duration` | **128-143** | Whole function. Splits `"100 us"`, returns `int(parts[0])`, else `0`. |
| String coercion | **379-393** | `vpp_str = electrical.get("vpp","0").replace("V","")` · `vcc_str = electrical.get("vcc","0").replace("V","")` · two `try/except (ValueError,TypeError)` blocks whose bodies are the bare expression `None` (`:386`, `:391`) with commented-out `logger.warning`s · `vpp_mv = electrical.get("vpp_mv", 0)` |
| Mapped-dict keys | **414-417** | `"vpp_volts": vpp` · `"vpp_mv": vpp_mv` · `"vcc": vcc` · `"pulse-delay": _parse_pulse_duration(programming.get("pulse_duration",""))  # noqa: E501` |
| `convert_to_programmer` | **536-626** | Dead `vpp_volts` fallback at **544-547**: `vpp_mv = full_eprom_data.get("vpp_mv") or int(full_eprom_data.get("vpp_volts",0)*1000)`. Wire dict at **550-557**. Optional `chip-id` **559-560**, `bus-config` **562-563**, `page-size` **565-569**, `flags` **619-624**. |

> ⚠️ **The two `except` bodies at `:386` and `:391` are the literal expression `None`** — not
> `pass`, not a log. Ruff's `select = ["E","F","I","UP"]` does not flag a useless expression
> statement. They vanish with the coercion layer.

> ⚠️ **`vpp_volts` (`:414`) is the key the two `vpp_str` display sites read**, not `vpp_mv`.
> Deleting it (per Claude's Discretion) *requires* both sites to switch to `vpp_mv` + the D-16
> helper. CONTEXT.md names those sites but not this coupling.

### C. `firestarter_app/tools/audit_coverage_matrix.py` (1942 lines) — D-09

`parse_pulse_us` appears **9 times**: 1 definition, **7 call sites**, 1 prose mention.
CONTEXT.md's "~8 call sites" over-counts by one.

| Line | Kind | Context |
|---|---|---|
| **106-110** | definition | `if not isinstance(s,str) or not s.endswith(" us"): raise ValueError(...)` ; `return int(s[:-3])` |
| **307** | call | `pulse_us = parse_pulse_us(chip["programming"]["pulse_duration"])` |
| **849** | call | inside `detect_correctness` — median/outlier computation |
| **1165** | call | |
| **1178** | call | |
| **1196** | call | |
| **1636** | call | wide-scan (`--all-algorithms`) path |
| **1730** | call | inside `_members_with_parseable_pulse` |
| 1562 | comment | wide-scan reuse note listing the shared primitives |

`_members_with_parseable_pulse` is at **1717-1734** (CONTEXT.md says `:1718-1727`); the string
filter is `if isinstance(pd,str) and pd.endswith(" us")` at `:1728` wrapping a
`try: parse_pulse_us(pd) except ValueError: continue`. Per D-09 this becomes `!= 0`.

**⚠️ An eighth read CONTEXT.md does not name — and it is a *render*, not a parse:**

```python
537:        _md_escape(chip["programming"]["pulse_duration"]),
```
inside `_enum_row` (`:522-542`). `_md_escape` is `str(s).replace("|", r"\|")` (`:516-519`), so it
survives an int — but the rendered cell changes from `100 us` to `100`. **This is what forces the
`tests/golden/v1.3-COVERAGE-MATRIX.md` regeneration**: the golden contains **303** lines carrying
` us` — but only **297** are value cells. The other 6 (`:54 :55 :1227 :1228 :1235 :1236`) are
`pulse_bucket` **labels** (`< 100 us`, `100-999 us`), which take ints today and are unchanged by
this phase. Re-measured by the planner 2026-08-19. The golden's header says *"DO NOT EDIT BY HAND. Re-run the tool."*

### D. `firestarter_app/tools/diff_db.py` (815 lines) — D-11

- **Exit-code contract** (module docstring `:1-20`): `0` all changed chips explained · `1`
  unexplained diff **or** a baseline chip missing · `2` infrastructure error (unloadable input),
  deliberately distinct so CI does not confuse a missing file with a real BLOCK (WR-04).
- **Env seams (CONTEXT.md does not mention these — they are the test hook):**
  `FIRESTARTER_DB_FILE` and `FIRESTARTER_BASELINE_FILE` at `:32-39`.
  `tests/test_diff_db_gate.py:31-68` already drives the tool via `subprocess.run` on this seam.
- **`_RATIONALES`** starts `:46`; the citation format is a multi-line string embedding
  `[VERIFIED: minipro …]`, permalink base documented at `:44`.
- **`_RULE_FIELD_PATHS` entries needing the rename:**

  | Line | Path | Action |
  |---|---|---|
  | 308 | `("programming","pulse_duration")` (in `BUG2_AND_BUG3`) | → `pulse_duration_us` |
  | 309-310 | `("electrical","vcc")`, `("electrical","vdd")` | → `vcc_mv`, `vdd_mv` |
  | 312 | `BUG2_TIMING` | → `pulse_duration_us` |
  | 313 | `BUG3_VCC_VDD` | → `vcc_mv`, `vdd_mv` |
  | 323 | `("electrical","vpp")` in `BUG_B_VPP` | **delete** (key gone) |
  | 334 | `("electrical","vpp")` in `RULE_PHASE66` | **delete** |

- **`_classify_diff` field-name reads** (`:440-460`): `:445` `pulse_duration` · `:447` `vcc` ·
  `:448` `vdd` · `:451` `vpp`/`vpp_mv` · `:458-459` `vpp`/`vpp_mv`. **All must be renamed** — see
  the measured failure mode in §"Validation Architecture" REQ-DATA-05.
- **`_diff_field_paths`** (`:373-392`) recurses dicts and is key-name agnostic — it needs no edit,
  and it is *why* an un-renamed classifier escalates the movers to `unexplained`.
- **Where the comparator hooks in:** `_load_db` (`:603-615`) → `_make_index` → the
  `bl_chip != cu_chip` guard at `:664`. **Canonicalizing at load time, immediately after
  `_load_db` returns, is the minimal-surface hook** — it makes `:664`, `_classify_diff` and
  `_diff_field_paths` all see one schema. Proven by simulation below.

### E. Display — the three D-16 call sites (all confirmed)

| File:line | Current code | Reads |
|---|---|---|
| `firestarter/ic_layout.py:568` | `"vcc_str": f"{eprom_data.get('vcc','N/A')}v"` | mapped-dict `vcc` (a **float**) |
| `firestarter/ic_layout.py:592-597` | `try: _vpp_mv=int(eprom_data.get("vpp_mv",0) or 0) except…: _vpp_mv=0` ; `if etype not in {"SRAM","FRAM"} and _vpp_mv>0: output_data["vpp_str"]=f"{eprom_data.get('vpp_volts','N/A')}v"` | gate on `vpp_mv`, render from `vpp_volts` |
| `firestarter/eprom_info.py:391-403` | same gate; `vpp_str = f"{ic.get('vpp_volts','N/A')}v"` else `"-"` | same |

Supporting (no change needed, but verified):
- `ic_layout.py:603-607` — pulse row already omitted on `0` (`_pulse_delay = eprom_data.get("pulse-delay",0) or 0; if _pulse_delay:`). D-08's sentinel needs no display work. ✅
- `eprom_info.py:256-264` — the info-card rows that print `vcc_str` / `vpp_str` / `pulse_delay_us_str`.
- `eprom_info.py:421` — the list-view row f-string (`vpp_str` in a 5-char cell).
- `eprom_info.py:88-91` — `_clean_config_for_export` pops `vdd` from a **`voltages` sub-dict**.
  This is a *different, legacy* structure (floats under `voltages`), reached by
  `firestarter/eprom_info.py:60-92` `key_map`, pinned by `tests/test_eprom_info.py:55-65`.
  It does **not** read `electrical.*` and is **not** part of this migration — but a plan that
  greps for `vdd` will hit it. Also note `eprom_info.py:71` hardcodes `"pulse-delay": "0"` (a
  **string**) as a `key_map` default in that same legacy path.

### Render Contract (proves D-15/D-16 are byte-exact)

Every distinct value the helper must reproduce, measured from the committed DB:

| DB value | mV | Today's render `f"{float(s.replace('V',''))}v"` | `f"{mv/1000:.1f}v"` |
|---|---|---|---|
| `3.3V` (19×vcc, 20×vdd) | 3300 | `3.3v` | `3.3v` ✅ |
| `4V` (56×vcc) | 4000 | `4.0v` | `4.0v` ✅ |
| `5V` (643×vcc, 454×vdd) | 5000 | `5.0v` | `5.0v` ✅ |
| `5.5V` (28×vcc, 167×vdd) | 5500 | `5.5v` | `5.5v` ✅ |
| `6.5V` (105×vdd — never rendered) | 6500 | `6.5v` | `6.5v` ✅ |
| `9V` (1×vpp) | 9000 | `9.0v` | `9.0v` ✅ |
| `12V` (563×vpp) | 12000 | `12.0v` | `12.0v` ✅ |
| `12.5V` (7×) | 12500 | `12.5v` | `12.5v` ✅ |
| `13V` (144×) | 13000 | `13.0v` | `13.0v` ✅ |
| `13.5V` (1×) | 13500 | `13.5v` | `13.5v` ✅ |
| `18V` (22×) | 18000 | `18.0v` | `18.0v` ✅ |
| `21V` (2×) | 21000 | `21.0v` | `21.0v` ✅ |
| `25V` (6×) | 25000 | `25.0v` | `25.0v` ✅ |

**No value in the database requires more than one decimal.** `f"{mv/1000:.1f}v"` is byte-exact for
all 13. Independently corroborated by the pinned snapshots, whose VPP column contains exactly
`12.0v`×492, `13.0v`×144, `18.0v`×22, `12.5v`×7, `25.0v`×6, `21.0v`×2, `13.5v`×2, `9.0v`×1.

**Unresolved edge:** today's `'N/A'` fallback renders `N/Av`. With `vpp_volts` deleted the helper
receives `vpp_mv` (always present, gated `> 0`), so the fallback becomes unreachable for the DB
path — but a user-override entry could still supply a non-int. The existing `try/except` coercion
at `ic_layout.py:589-592` / `eprom_info.py:391-394` guards the *gate*; the plan should decide
whether the helper mirrors that tolerance. (Not a locked decision; flagged so it is not missed.)

### `pulse_duration` value census

`Algorithm Controlled` ×**417** (matches the seed's 417 exactly) · `100 us` ×217 · `200 us` ×34 ·
`1000 us` ×30 · `500 us` ×25 · `50 us` ×15 · `10 us` ×7 · `20 us` ×1. Total 746; **329**
parseable. `pulse_duration_us: 0` will therefore appear on 417 chips.

---

## Consumer Inventory — every read of a migrated key

Grepped across the whole `firestarter_app/` tree (source, tools, tests, snapshots), excluding
`chip_database.json` and `tools/baseline/`. Access shape given per site.

### `electrical.vcc` → `vcc_mv`

| File:line | Shape | Note |
|---|---|---|
| `tools/build_db.py:750` | emit | producer |
| `tools/build_db.py:821` | `chip_entry["electrical"]["vcc"] = …["vdd"]` | SRAM normalization |
| `firestarter/database.py:382` | `electrical.get("vcc","0").replace("V","")` | **coercion — deleted** |
| `firestarter/database.py:416` | `"vcc": vcc` (mapped dict) | float → migrate |
| `firestarter/ic_layout.py:568` | `eprom_data.get('vcc','N/A')` | **render site** |
| `tools/diff_db.py:309,313` | `_RULE_FIELD_PATHS` tuples | rename |
| `tools/diff_db.py:447` | `bl_elec.get("vcc") != cu_elec.get("vcc")` | rename |
| `tests/test_diff_db_gate.py:86,118` | fixture literal `"vcc": "5V"` | **update** |
| `tests/test_chip_database_field_inventory.py:223,240` | docstring only | no change |

*(`firestarter/database.py:335` `pin_map_data.get("vcc-pin")` is the **pinout** file's pin list — unrelated.)*

### `electrical.vdd` → `vdd_mv`

`tools/build_db.py:753` (emit) · `:821` (SRAM read) · `tools/diff_db.py:310,313` (paths) ·
`:448` (compare) · `tests/test_diff_db_gate.py:87,119` (fixture).
**Never read by `database.py`, never displayed** — confirming D-05's "not surfaced anywhere".

### `electrical.vpp` (string) → **deleted**

`tools/build_db.py:737` (emit) · `firestarter/database.py:381,384` (**coercion — deleted**) ·
`tools/diff_db.py:323,334` (paths, **delete**) · `:451,458` (compare, **delete**) ·
`tests/test_diff_db_gate.py:88,120` (fixture) · `tools/check_dispatch.py:373` — asserts
`"vpp" not in wire` (**wire** dict, unaffected; stays green).

### `electrical.vpp_mv` (int — **name and type unchanged**)

Producer `build_db.py:742`. Consumers: `database.py:393,415,545,554` · `ic_layout.py:590` ·
`eprom_info.py:392` · `check_dispatch.py:314,371` (**GATE-03**) ·
`diff_db.py:324,335,452,459` · `tests/test_check_dispatch_invariants.py` (many) ·
`tests/test_variant_decode_evidence_stability.py:102,126` (`_WIRE_FIELDS`, baseline-pinned) ·
`tests/test_build_db_inclusion.py:263,318` · `tests/test_extra_chips_supplement.py:116` ·
`tests/test_chip_resolver.py:43,90` · `tests/test_eprom_database.py:101` ·
`tools/check_devtest_orchestrator.py:199`. **None require change.**

### `programming.pulse_duration` → `pulse_duration_us`

`tools/build_db.py:759` (emit) · `firestarter/database.py:417` (via `_parse_pulse_duration`) ·
`tools/diff_db.py:308,312,445` · `tools/audit_coverage_matrix.py:307,537,849,1165,1178,1196,1636,1727,1730` ·
`tests/test_diff_db_gate.py:91,123` (fixture).

### Mapped-dict `vpp_volts` (host-internal) → **deleted**

`database.py:414` (produced) · `:546` (dead fallback) · `ic_layout.py:597` (**render**) ·
`eprom_info.py:401` (**render**) + a comment at `:398`.

### Wire key `pulse-delay` (**unchanged on the wire**)

`database.py:417,555` · `ic_layout.py:605` · `cli_handlers.py:685` ·
`eprom_operations.py:1894` · `eprom_info.py:71` (legacy `key_map` string `"0"`) ·
`tools/check_devtest_orchestrator.py:204` (orchestrator wire-key gate) ·
`tests/test_pulse_us_override.py` (14 assertions) · `.ambr:375,1265` (help text only).

### Test-fixture surface

Exactly **one** test file constructs records in the old string schema:

```
$ grep -rl '"vcc"\s*:\s*"\|"vpp"\s*:\s*"\|"pulse_duration"\s*:\s*"' tests/
tests/test_diff_db_gate.py        (6 occurrences: :86,:87,:88,:91,:118,:119,:120,:123)
```

`tests/fixtures/` contains no chip-database fixture (only planted-source `.py`/`.h`/`.cpp` files).

---

## Regeneration Mechanics (verified end to end)

```bash
cd /workspaces/firestarter_app
python3 tools/build_db.py          # no arguments, no env vars required
```

| Property | Measured |
|---|---|
| Pinned URL | `https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml` (`build_db.py:17-20`) |
| Network from this environment | ✅ **HTTP 200**, 17,861,009 bytes, 1.52 s |
| Full regen wall time | **1.45 s** |
| Output | `744 upstream + 2 supplement = 746 total` → `firestarter/data/chip_database.json` (`indent=2, sort_keys=True`) |
| Exit code | 0 |
| **Byte-reproducibility** | ✅ **`diff` against the committed file: IDENTICAL.** `git status` clean after the run. |
| stderr | 32 lines — 26 `WARN: skipping … unknown protocol_id` (0x04/0x11/0x0A) + 6 `INFO: including … adapter-required`. **All pre-existing and benign.** |
| Env vars needed | **None.** `FIRESTARTER_CONFIG_DIR` is irrelevant to `build_db.py` (it reads only the network + `tools/extra_chips.json` + `firestarter/data/pinouts.json`). |
| Local user override | `~/.firestarter/` exists but contains only `config.json` (30 B) — **no `database.json`**, so the override path is not exercised here. |

**This byte-reproducibility is the phase's most important precondition** and it holds: any diff
after the migration is attributable to the change, never to upstream drift.

### D-08 reachability — the fatal branch is provably dead against the pinned XML

```bash
python3 -c "
import xml.etree.ElementTree as ET
root=ET.parse('infoic.xml').getroot()
tot=missing=unparse=0
for ic in root.iter('ic'):
    tot+=1; pd=ic.get('pulse_delay')
    if pd is None: missing+=1; continue
    try: int(pd,16)
    except (TypeError,ValueError): unparse+=1
print(tot, missing, unparse)"
→ total <ic> elements: 27862 · missing pulse_delay attr: 0 · present-but-unparseable: 0
```

Corroborated by the real run: **zero** `unparseable pulse_delay` WARN lines in stderr.

**Planning consequence:** making the branch fatal is **zero-risk** against the pinned commit — and
it is **not provable by a regen**. It must be proven by a direct unit test on `interpret_timing`.
See §"Validation Architecture" REQ-DATA-02.

---

## Gates — commands, current state, and fail-open traps

| Gate | Command (from `/workspaces/firestarter_app`) | Today | CI? |
|---|---|---|---|
| Full test suite | `python3 -m pytest -o addopts="" -q` | ✅ **1616 passed, 280 s** (30 snapshots) | ✅ `pytest tests/ --cov=firestarter --cov-fail-under=70` (py3.11) |
| GATE-02 | `python3 tools/diff_db.py` | ✅ exit 0 — **744 changed, all explained** (see F-2) | ✅ via `tests/test_diff_db_gate.py` |
| GATE-03 | `python3 tools/check_dispatch.py` | ✅ exit 0 — 746 scanned, 736 supported, 0 violations | ✅ via tests |
| Field-inventory | `python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -v` | ✅ 8 passed | ✅ |
| Coverage matrix | `python3 tools/audit_coverage_matrix.py --output "$SCRATCH/m.md" --ledger "$SCRATCH/l.json"` | ✅ exit 0; output **matches** `tests/golden/v1.3-COVERAGE-MATRIX.md` | ✅ via `tests/test_audit_coverage_matrix.py` |
| ruff lint | `python3 -m ruff check firestarter/ tests/` | ✅ All checks passed | ✅ |
| ruff format | `python3 -m ruff format --check firestarter/ tests/` | ✅ 135 files formatted | ✅ |
| mypy watermark | `python3 tools/check_mypy_watermark.py` | ❌ **exit 2 locally** (see trap 2) | ✅ (py3.11) |

### Trap 1 — `tools/` is linted by **nothing**

- ruff CI scope: `firestarter/ tests/` (`ci.yml:81,84`)
- mypy argv: `[sys.executable,"-m","mypy","firestarter/","tests/"]` (`tools/check_mypy_watermark.py:115`), with **no env-var seam by design (D-01)**

**`build_db.py`, `diff_db.py`, `audit_coverage_matrix.py`, `check_dispatch.py` — the four files
this phase edits most — are covered by neither ruff nor mypy.** Only pytest exercises them. This
compounds the standing repo fact that every `# noqa: BLE001` is inert
(`select = ["E","F","I","UP"]`, `pyproject.toml:131`). Keep excepts narrow by hand; a broad
`except Exception:` added in `tools/` is gated by absolutely nothing.

### Trap 2 — the mypy gate cannot be run locally

```
$ python3 tools/check_mypy_watermark.py
ERROR: mypy exited 2, which is neither the clean-run (0) nor errors-found (1) exit code.
/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater [syntax]
EXIT=2
```

The devcontainer runs py3.12 while CI pins **3.11**. The gate correctly refuses to treat exit 2 as
clean — so it is **fail-closed locally but unrunnable**. A plan must not make a task's verification
depend on a local mypy run. Since `tools/` is out of mypy scope anyway, the only Phase 148 files
mypy sees are `firestarter/database.py`, `ic_layout.py`, `eprom_info.py` and `tests/`.

### Trap 3 — `audit_coverage_matrix.py` writes into the **meta repo** by default

```
$ python3 -c "…exec_module…; print(m.DEFAULT_OUTPUT); print(m.DEFAULT_LEDGER)"
/workspaces/.planning/v1.3-COVERAGE-MATRIX.md
/workspaces/.planning/v1.3-defect-coverage-ids.json
```
Both are **tracked in the meta repo** (`git ls-files` confirms all four defaults). `_REPO_ROOT` is
`dirname×3(__file__)` = `/workspaces` (`:59-68`). **Always pass explicit `--output` / `--ledger` to
a scratch path**, exactly as the module docstring and `tests/test_audit_coverage_matrix.py:440-510`
already do.

### Trap 4 — `--check`'s contract is relative to a **freshly generated** ledger

CONTEXT.md: *"`--check` against an empty ledger must exit 1; against the full ledger, 0."*
Reproducing the exact three-step from `tests/test_audit_coverage_matrix.py:440-510`:

| Step | Result |
|---|---|
| 1. clean generate → scratch ledger | exit 0 |
| 2. `--check` vs `{}` empty ledger | **exit 1** ✅ |
| 3. `--check` vs the **step-1** ledger | **exit 0** ✅ |
| 4. `--check` vs the **meta repo's committed** ledger | **exit 1** ⚠️ |

The meta repo's committed ledger holds **78** entries; a fresh generate mints **68**. It is
**already drifted today**, before Phase 148 (consistent with the standing 121-01 note that the
golden was regenerated naming COV-78..95 against a ledger stopping at 77). **Phase 148 must not be
judged against the meta ledger**, and updating it is a separate cross-repo decision.

### Trap 5 — the whole-repo-porcelain test is in the **firmware** repo, not this one

```
$ find . -name test_flash_path_record_sync.py
./firestarter/tests/test_flash_path_record_sync.py
```

It lives in `firestarter/` (the Arduino repo). **Phase 148 is host-only, so this trap does not
apply.** Confirmed empirically: the full `firestarter_app` suite passed with 7 untracked files in
the tree.

### Note — `check_dispatch.py` reads the user override

`tools/check_dispatch.py:190` constructs `EpromDatabase()` **without** `skip_local_override=True`,
so a `~/.firestarter/database.json` would be merged into GATE-03's scan. None is present here.

---

## Validation Architecture

> **Framework detected.** This section is the source for VALIDATION.md (Nyquist Dimension 8).

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` 8.x + `syrupy` (snapshots) + `pytest-cov`, via `pip install -e '.[test]'` |
| Config file | `pyproject.toml` — `[tool.pytest.ini_options] addopts = "-ra -q"`; `[tool.ruff]`, `[tool.mypy]` |
| Interpreter | local `/usr/local/bin/python3` = **3.12**; CI pins **3.11**; editable install at `/workspaces/firestarter_app`, version **3.0.0b21** |
| Quick run command | `python3 -m pytest tests/<file>.py -o addopts="" -q` |
| Full suite command | `python3 -m pytest -o addopts="" -q` — **1616 passed in 280 s** |
| ⚠️ `-q` doubling | `addopts` is `-ra -q`; adding `-q` **suppresses the count line**. Always pass `-o addopts=""`. Confirmed in the Phase 140 precedent commands. |

### Phase Requirements → Test Map

| Req | Behavior | Type | Automated command | Exists? |
|---|---|---|---|---|
| DATA-01 | `firestarter info AT28C256` reports `VCC: 5.0v` | integration (CLI) | `python3 -m pytest tests/test_characterization.py -o addopts="" -q` | ❌ **Wave 0** — no AT28C info test exists (F-3) |
| DATA-01 | Exactly 56 chips carry `vcc_mv == 5000` that previously carried 4000; none decreased | unit (data) | new `tests/test_vcc_margin_rail.py` | ❌ **Wave 0** |
| DATA-01 | `VCC_VOLTAGES` index `0x02` still decodes the margin rail (table not edited) | unit | same file | ❌ **Wave 0** |
| DATA-02 | Field inventory golden matches (`vcc_mv`/`vdd_mv`/`pulse_duration_us` at 746; `vpp` absent) | gate | `python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -v` | ✅ exists — golden must be **re-derived** |
| DATA-02 | `interpret_timing` raises/exits on an unparseable `pulse_delay` (D-08) | unit | new test importing `tools/build_db.py` | ❌ **Wave 0** — *not provable by a regen* |
| DATA-02 | Render output byte-identical | snapshot | `python3 -m pytest tests/test_characterization.py -o addopts="" -q` | ✅ 30 snapshots; `.ambr` must be **byte-unchanged** |
| DATA-03 | No `.replace("V","")`/`float()` path and no `_parse_pulse_duration` in `database.py` | unit (source scan) | new grep/AST assertion | ❌ **Wave 0** |
| DATA-03 | No `parse_pulse_us` anywhere in `audit_coverage_matrix.py` | unit (source scan) | same | ❌ **Wave 0** |
| DATA-03 | **746-chip wire-dict byte equivalence** | integration | new `tests/test_wire_dict_equivalence.py` | ❌ **Wave 0** |
| DATA-04 | `_PAGE_SIZE_BY_PART` still has exactly 2 entries; no new part-keyed dict in `build_db.py` | unit (AST) | new assertion | ❌ **Wave 0** |
| DATA-05 | `diff_db.py` exit 0; bucket counts as specified | gate | `python3 tools/diff_db.py` / `tests/test_diff_db_gate.py` | ✅ exists — comparator + rule added |
| DATA-05 | GATE-03 zero violations, gate file byte-unchanged | gate | `python3 tools/check_dispatch.py` + `git diff --quiet tools/check_dispatch.py` | ✅ exists |

### D-11 — the normalizing comparator, measured

**Hook point:** canonicalize both loaded databases at load time (immediately after `_load_db`,
before `_make_index`). This makes `bl_chip != cu_chip` (`:664`), `_classify_diff` and
`_diff_field_paths` all see one schema, and is the minimal-surface option.

**Canonicalization:** `"5V"→5000`, `"12.5V"→12500` (`int(round(float(s.rstrip("V"))*1000))`);
`"100 us"→100`, `"Algorithm Controlled"→0`; drop `electrical.vpp`; rename
`vcc→vcc_mv`, `vdd→vdd_mv`, `pulse_duration→pulse_duration_us`.

**Measured result — canonicalizer alone, no rule change (this is the RED):**

| Bucket | Count |
|---|---|
| `PROV01_PROTECT_METADATA` | 686 |
| **`UNEXPLAINED`** | **56** ← every D-03 mover |
| `PGSZ_PAGE_SIZE` | 2 |
| `UNCHANGED` | 2 |
| **exit code** | **1** |

**Why** — and this is the subtle part CONTEXT.md's "a key rename would make all 746 chips diff"
does not capture. After the rename, `_classify_diff`'s `bl_elec.get("vcc") != cu_elec.get("vcc")`
compares `None != None` → **False**. The VCC change is *invisible* to the named reads, so the chip
falls through to `PROV01_PROTECT_METADATA`; but `_diff_field_paths` (key-agnostic) still yields
`("electrical","vcc_mv")`, which no rule claims → escalated to `unexplained`:

```
classify -> ('PROV01_PROTECT_METADATA', {('electrical','vcc_mv')})
baseline elec: {..., 'vcc_mv': 4000, 'vdd_mv': 5000}
current  elec: {..., 'vcc_mv': 5000, 'vdd_mv': 5000}
```

**Therefore D-11's "a `_RATIONALES` entry is required — mechanical, not a choice" is incomplete.**
Four edits are required: (1) the canonicalizer, (2) rename the five field-name reads at
`:445-459`, (3) rename/delete the six `_RULE_FIELD_PATHS` tuples, (4) add `RULE_VCC_MARGIN_RAIL`
to `_RATIONALES` **and** `_RULE_FIELD_PATHS` **and** — for a reviewable artifact — `_classify_diff`.

**Two designs measured end to end (both exit 0):**

| Design | `PROV01` | `RULE_VCC_MARGIN_RAIL` | `PGSZ` | `UNCHANGED` | compound notes | exit |
|---|---|---|---|---|---|---|
| **A** — `_RULE_FIELD_PATHS["RULE_VCC_MARGIN_RAIL"] = {("electrical","vcc_mv")}` only | 742 | — | 2 | 2 | 58 | 0 |
| **B** — A **plus** a priority branch in `_classify_diff` scoped `bl.vcc_mv == 4000 and cu.vcc_mv == cu.vdd_mv != 4000` | **686** | **56** | 2 | 2 | 58 | 0 |

**Recommend Option B.** D-12 requires the artifact to carry "the 56-chip mover list"; under
Option A the movers exist only as 56 of 58 undifferentiated compound notes attached to
`PROV01_PROTECT_METADATA`'s rationale, which is a *different* phase's citation. Option B gives
them their own labelled bucket with their own citation, which is exactly what D-11 describes.
(Branch placement: it must precede `BUG3_VCC_VDD` — otherwise a mover whose only other delta were
`vdd` would be attributed to the Phase 57/58 "BUG-3 label swap" rationale.)

**The RED/GREEN transcript for the new rule is free:** run the migration with the canonicalizer and
renames only → **exit 1, 56 unexplained**; add `RULE_VCC_MARGIN_RAIL` → **exit 0, 56 in bucket**.
Capture both.

**Test seam:** `tests/test_diff_db_gate.py:31-68` already runs `tools/diff_db.py` via
`subprocess.run`. `FIRESTARTER_DB_FILE` / `FIRESTARTER_BASELINE_FILE` (`diff_db.py:32-39`) allow a
scratch-DB variant without touching the real files.

**On the criterion wording (see F-2):** state it as *"the changed-chip total stays 744 and every
pre-existing bucket count is unchanged; the only new bucket is `RULE_VCC_MARGIN_RAIL` with
exactly 56 chips; exit 0"* — not "diffs to zero".

### D-13 — golden re-derivation with a seen-to-fail transcript

**What `meta` actually requires** (read verbatim from `tests/golden/chip_database_field_inventory.json`):

- `how_to_update`: *"Re-derive every number … with an independent traversal of the live
  chip_database.json (two levels deep) — **never hand-edit a count to make a surprise disappear.**
  State in the commit message which key changed, on which level, and why. If `tools/build_db.py`'s
  `chip_entry` construction **or `tools/extra_chips.json`** changed, also re-derive
  `generator_emitted_chip_entry_keys` … (an ast walk over `chip_entry` plus a key scan of
  `extra_chips.json`) rather than editing the list by hand."* — **both** triggers fire this phase.
- `why_counts_not_names`: counts, not names, because a field added to a *subset* slips past a
  names-only check.
- `why_not_diff_db`: this gate is deliberately **not** derived from the diff baseline, because a
  regenerable baseline is a silenceable gate.
- `generator_scan_scope`: the live derivation is the **union** of the `chip_entry` AST walk (21
  names) and the `extra_chips.json` key scan (5 more) = **26**.

**Exact golden deltas this phase must produce:**

| Level | Today | After |
|---|---|---|
| `levels.electrical` | 7 keys: `pin_count,size_bytes,type,vcc,vdd,vpp,vpp_mv` — all 746 | **6 keys**: `…,vcc_mv:746, vdd_mv:746, vpp_mv:746` — `vpp` **removed** |
| `levels.programming` | `…,pulse_duration:746,…` | `pulse_duration_us: 746` |
| `generator_emitted_chip_entry_keys` | 26 names incl. `vcc,vdd,vpp,pulse_duration` | **25 names**: `vcc_mv,vdd_mv,pulse_duration_us`; `vpp` dropped |
| `meta.recorded_at_head` | `4d18b645…` | new head |
| `totals`, `protocol_chip_counts` | 59 / 746; `{7:170, 8:127, 11:32}` | **unchanged** (assert this) |
| `levels.top` | 11 keys | **unchanged** |

**Seam mechanics — CONTEXT.md's warning is correct and there is a third path it omits:**
`_DB_PATH` (`:99`) and `_GEN_PATH` (`:100-102`) resolve from `os.environ` **at import**, so they
must be set in a **child process**, never monkeypatched. `_EXTRA_CHIPS_PATH` (`:106`) is
**deliberately not overridable** — by design, so a `FIRESTARTER_BUILD_DB_SOURCE` redirect at a
scratch `build_db.py` copy still finds the real supplement and fails on the *planted key* rather
than a `FileNotFoundError` (the "unreachable leg" trap). `test_default_targets_resolve_inside_this_repository`
(test 7) recomputes both defaults from `_APP_ROOT`, ignoring the environment, so a stray redirect
left set in CI turns the gate RED rather than silently green.

**Phase 140 Plan 03 precedent — the transcripts exist and are directly reusable:**
`.planning/phases/140-parameter-table/140-03-SUMMARY.md` §"Planted Violations", **Runs A–E** at
lines ~160-350. Shape of Run A:

```bash
T=$(mktemp -d)
python3 -c "import json,sys; db=json.load(open('firestarter/data/chip_database.json')); \
  db[sorted(db)[0]][0]['programming']['foo']=1; json.dump(db, open(sys.argv[1],'w'))" "$T/db.json"
FIRESTARTER_CHIP_DB_JSON="$T/db.json" python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -v
rm -rf "$T"
```

The four planted legs: **A** new field on one chip (RED test 2, `added={'foo':1}`) · **B** delete a
chip — count change with **no** new name (RED tests 1/2/3/5, proving counts-not-names) · **C**
vacuous `{}` target (RED test 5, non-vacuity, never a silent pass) · **D** new key in the
*generator only* via `FIRESTARTER_BUILD_DB_SOURCE` (RED test 6, `added=['foo']`) · **E** clean
(exit 0, 8 passed). Every planted copy lived under `mktemp -d` outside both repos and was
`rm -rf`'d; `git diff --quiet` was confirmed before, between and after every run.

**A Phase-148-specific fifth leg is worth adding:** plant a key inside `extra_chips.json`'s record
and confirm test 6 goes RED — it exercises the union path F-1 makes load-bearing.

### D-14 — 746-chip wire-dict equivalence, measured

**Feasibility proven.** Prototype capture:

```python
from firestarter.database import EpromDatabase
db = EpromDatabase(skip_local_override=True)      # ← determinism: skip ~/.firestarter
out = {}
for mfg, chips in db.proms.items():
    for i, c in enumerate(chips):
        pn = c.get("part_number")
        mapped = db.get_eprom(pn)
        out[f"{mfg}|{pn}|{i}"] = db.convert_to_programmer(mapped)
blob = json.dumps(out, sort_keys=True, indent=2)
```

| Property | Measured |
|---|---|
| Chips captured | **746 / 746** — zero unresolvable |
| Elapsed | **0.43 s** |
| Fixture size | **332,716 bytes** (325 KB) |
| SHA-256 of canonical blob | `027a43a0dcef1085afa6a35d2500bd35556140dde4b838dfcd65bfae8cac7dab` |
| Union of wire keys (**9**, see F-8) | `algorithm, bus-config, chip-id, flags, memory-size, page-size, pin-count, pulse-delay, vpp_mv` |
| `vcc` / `vpp_volts` present? | **No** — D-06 confirmed at the wire |

**Fixture-format tradeoff (Claude's Discretion, with numbers):**

| Option | Size | On failure |
|---|---|---|
| Full canonical JSON committed under `tests/golden/` | 325 KB | Full per-chip diff — best diagnostics |
| Per-chip SHA-256 map | ~65 KB | Names the chip, not the field |
| Single blob SHA-256 in the test source | 64 B | "Something changed" — poor diagnostics |

Recommend the **full JSON** under `tests/golden/wire_dict_baseline.json` — 325 KB is unremarkable
next to the 1.1 MB `chip_database.json` already committed, and it is the only option that makes a
regression self-explaining.

**Capture must happen on the pre-change tree** (task 1 of the phase, before any edit) and must use
`skip_local_override=True`.

**D-06's separate assertion (the VCC rule produces zero wire change):** capture the wire dicts
*after the numeric migration but before the D-03 rule*, or — simpler and order-independent —
assert directly that for all 746 chips the post-change wire dict is byte-identical to the
pre-change one. Since `vcc_mv` is never emitted, the D-03 rule cannot alter it, and the single
combined assertion covers both claims. If the plan splits the two changes across two plans, the
intermediate capture is free.

**Reuse note:** `tools/check_dispatch.py:368-370` already runs `db.get_eprom(part)` →
`db.convert_to_programmer(mapped)` for every chip. GATE-03 is itself a 746-chip wire exerciser —
but it only asserts `vpp_mv` present / `vpp` absent, which is exactly why D-14 says it is
insufficient.

### D-15 — snapshot delta (superseded by F-3)

**No snapshot entry moves.** The `.ambr` file must be **byte-unchanged**:

- `tests/__snapshots__/test_characterization.ambr:432-435` — `VCC: 5.0v` / `VPP: 12.0v` /
  `Pulse delay: 100µS` for **W27C512**, a non-mover.
- `:573-582` — AT28C rows in `test_list`, but the list view renders **only** VPP (`12.0v`).
- Zero `4.0v` anywhere in `tests/__snapshots__/`.

**Criterion:** `git diff --quiet tests/__snapshots__/test_characterization.ambr` after the change.
This is stronger than D-15's stated proof and it is achievable; D-15's version is not.

**Because of that, criterion 1 needs a NEW test** — the only reason the AT28C VCC correction has
any coverage at all. Captured before-state:

```
$ firestarter info AT28C256
Eprom Info
Name:               AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L
Manufacturer:       ATMEL
Number of pins:     28
Memory size         0x8000
Type:               EEPROM
Can be erased:      yes (electrically erasable)
VCC:                4.0v          ← must become 5.0v
VPP:                12.0v         ← must NOT change
Chip ID:            -
```

Adding it as a **new syrupy snapshot** (e.g. `test_info_at28c256`) rather than a string assertion
also pins the VPP/pulse rows against collateral drift. That is a *new* snapshot, not a
re-baselining of a pinned one, so v1.30 Phase 136's rule is not engaged.

### Sampling Rate

- **Per task commit:** the targeted file(s) — e.g.
  `python3 -m pytest tests/test_diff_db_gate.py tests/test_chip_database_field_inventory.py -o addopts="" -q` (< 5 s)
- **Per wave merge:** `python3 tools/build_db.py && python3 tools/diff_db.py && python3 tools/check_dispatch.py && python3 -m ruff check firestarter/ tests/`
- **Phase gate:** full suite green (**budget 280 s — allow ≥ 600 s timeout**) + all four gates + `git diff --quiet` on `tools/check_dispatch.py` and `tests/__snapshots__/`

### Wave 0 Gaps

- [ ] `tests/golden/wire_dict_baseline.json` — the 746-chip pre-change capture (**must be taken before any edit**) — DATA-03
- [ ] `tests/test_wire_dict_equivalence.py` — asserts byte-identity against it — DATA-03
- [ ] `tests/test_vcc_margin_rail.py` — the 56-mover assertions, the "no `vcc_mv` decreased" guard, `VCC_VOLTAGES[0x02]` unchanged — DATA-01
- [ ] A new `firestarter info AT28C256` snapshot/assertion — **the only coverage criterion 1 will have** — DATA-01
- [ ] A unit test for D-08's fatal branch on `interpret_timing` — **unreachable via regen** — DATA-02
- [ ] Source-scan assertions: no `_parse_pulse_duration` / `.replace("V","")` in `database.py`; no `parse_pulse_us` in `audit_coverage_matrix.py` — DATA-03
- [ ] An AST assertion that `_PAGE_SIZE_BY_PART` still has 2 entries and no new part-number-keyed dict exists in `build_db.py` — DATA-04
- [ ] Update `tests/test_diff_db_gate.py:86-91,118-123` to the numeric schema (the only fixture file affected)
- [ ] Re-derive `tests/golden/chip_database_field_inventory.json` + capture the 4-or-5 RED / 1 GREEN transcripts — DATA-02
- [ ] Regenerate `tests/golden/v1.3-COVERAGE-MATRIX.md` (**297** ` us` value cells change; the 6
      `pulse_bucket` label lines do **not**) — DATA-03

*No framework install needed — pytest, syrupy and ruff are all present and green.*

---

## Sequencing & Collision Facts

| Fact | Verified |
|---|---|
| `firestarter_app` branch | `gsd/v1.32-at28c-write-path-root-cause-report-provenance` ✅ |
| `firestarter_app` HEAD | `9701209 test(147-05): W-3 — null-identity frozen fixture, marker parity, claim-pattern assert` |
| Phase 147 work present | ✅ 12 commits ahead of `origin/beta` |
| App version | `3.0.0b21` (`firestarter/__init__.py:1`; `firestarter --version` agrees) |
| **Files Phase 147 touched** | `firestarter/cli_handlers.py`, `firestarter/diagnostic_report.py`, `firestarter/hardware.py`, `tests/test_dev_test_cmd.py`, `tests/test_diagnostic_report.py`, `tests/test_hardware.py`, `tests/test_parse_devtest_issue.py`, `tools/parse_devtest_issue.py` |
| **Overlap with Phase 148's edit set** | ✅ **ZERO** — Phase 148 touches `tools/build_db.py`, `tools/extra_chips.json`, `tools/diff_db.py`, `tools/audit_coverage_matrix.py`, `firestarter/database.py`, `firestarter/ic_layout.py`, `firestarter/eprom_info.py`, `firestarter/data/chip_database.json`, two goldens, `tests/test_diff_db_gate.py` |
| Meta repo branch / HEAD | `gsd/v1.32-…` @ `27f65718 docs(148): correct DATA-01 and Phase 148 criterion 1 to the measured VCC finding` |
| Meta working tree | dirty: ` M firestarter` (gitlink), untracked `.claude/skills/devtest-rootcause/`, `.claude/skills/skill-writer/`, `package*.json` — **stage specific files only** |
| Firmware repo branch | ⚠️ `gsd/v1.31-27c-programming-algorithm-fidelity` @ `6992271` — **still on the v1.31 branch.** Irrelevant to host-only Phase 148; **Phase 149 (dual-repo) will need it moved.** |
| Wave constraint | 148 and 149 both write the host DB-consumption layer → **never the same wave**. 148 touches no `cli_handlers.py` path → no 147/150 collision. ✅ |
| `test_flash_path_record_sync.py` porcelain trap | **Does not apply** — that file is in `firestarter/tests/`, the firmware repo (Trap 5). |

---

## Project Constraints (from CLAUDE.md and project skills)

From `/workspaces/CLAUDE.md`:
- Meta repo tracks only `.planning/` and `.claude/`; neither sub-repo is committed here. Executors commit **inside** `firestarter_app/`.
- EPROM database is `firestarter_app/firestarter/data/chip_database.json`; user overrides in `~/.firestarter/database.json`.
- Serial-protocol changes must stay in sync between `serial_comm.py` and `firestarter.cpp` — **not engaged**, no wire change.
- Constants/flag bits duplicated between `constants.py` and `firestarter.h` — **not engaged**.

From `.claude/skills/devtest-rootcause/SKILL.md`:
- `chip_database.json` is **GENERATED** — *"NEVER. Edits are erased on the next regen. Fix the generator, regenerate."*
- `tools/build_db.py` — editable, subject to the proof rule.
- `tools/extra_chips.json` — *"authored supplement. Only for chips **absent from infoic.xml entirely** (2516, 2532). Not an override for a chip upstream already has."* ⚠️ A representation migration is a different concern than adding a chip — the plan should say so explicitly (F-1).
- **The proof rule:** *"The generator may not emit a field it cannot prove from `infoic.xml`. … Do not add invented fields, per-chip lookup tables keyed on part number, or hand-maintained override stacks. Three such guess tables were deliberately deleted in Phase 70."*
- `_PAGE_SIZE_BY_PART` is flagged in the skill itself as *"the exact shape the rule forbids. Do not extend it or add siblings to it."*

Standing repo facts that bear on this phase:
- Every `# noqa: BLE001` is **inert** (`select = ["E","F","I","UP"]`) — keep excepts narrow by hand.
- `tools/` is outside both ruff's and mypy's CI scope (Trap 1).
- GSD requirements/roadmap verbs reformat the whole file (`_normalizeMd`) — D-04's hand-edit mechanic; snapshot and diff.

---

## Common Pitfalls (specific to this phase)

### Pitfall 1 — Writing "diff_db reports zero changed chips" as a criterion
**What goes wrong:** unachievable; produces a false RED. **Why:** the baseline predates Phase 136.1
and 744/746 chips already diff. **Avoid:** phrase it as bucket-count invariance + one new 56-chip
bucket (F-2). **Warning sign:** a criterion containing the literal word "zero" next to `diff_db`.

### Pitfall 2 — Expecting the snapshot to change
**What goes wrong:** a task waits for an AT28C snapshot delta that cannot occur. **Why:** the only
info-view snapshot is W27C512 (F-3). **Avoid:** assert `.ambr` byte-unchanged **and** add a new
AT28C test.

### Pitfall 3 — Forgetting `tools/extra_chips.json`
**What goes wrong:** 2 chips keep the string schema; D-10's direct indexing raises `KeyError`; the
field-inventory golden's union path disagrees. **Why:** it is merged post-decode, byte-faithful
(F-1). **Warning sign:** the two TI chips are the only records that do not diff today.

### Pitfall 4 — Adding only a `_RATIONALES` entry for `RULE_VCC_MARGIN_RAIL`
**What goes wrong:** the 56 movers land in `unexplained` → exit 1, or (with a field-path claim
only) get buried as compound notes under another phase's citation. **Avoid:** Option B — all four
edits, with the branch placed before `BUG3_VCC_VDD`.

### Pitfall 5 — Running `audit_coverage_matrix.py` without `--output`/`--ledger`
**What goes wrong:** silently rewrites two tracked **meta-repo** files and mints new
`DEFECT-COV-NN` IDs (Trap 3).

### Pitfall 6 — Trying to prove D-08 by a regen
**What goes wrong:** the fatal branch is unreachable — 0 of 27,862 `<ic>` elements have a
missing/unparseable `pulse_delay`. A "the build still passes" run proves nothing. **Avoid:** a
direct unit test on `interpret_timing`.

### Pitfall 7 — Making a task's verification depend on local mypy
**What goes wrong:** exits 2 on the devcontainer's py3.12 numpy stubs (Trap 2). **Avoid:** trust it
to CI; note that `tools/` is out of its scope regardless.

### Pitfall 8 — Under-budgeting the full suite
280 s measured. A 120 s default timeout returns rc=124 and reads like a RED.

### Pitfall 9 — Placing the D-03 rule inside the `chip_entry` dict literal
`vcc_mv`/`vdd_mv` are built inline at `:750-755`; the rule must be a post-construction mutation
beside the SRAM block at `:820-821`.

---

## Open Questions (RESOLVED)

All three were settled during planning on 2026-08-19. Each is recorded here so this document can be
read standalone; the binding statement lives in the cited plan.

1. **Does the D-16 helper keep the `'N/A'` tolerance?**
   Known: today's `f"{eprom_data.get('vcc','N/A')}v"` yields `N/Av` for a malformed entry, and the
   two `vpp_str` sites already `try/except` a non-int `vpp_mv`. Unclear: whether D-10's
   "absent key ⇒ exception" applies to the *display* path or only the DB-read path.
   Recommendation: keep the existing display tolerance (it guards user overrides, not the generated
   DB) and apply D-10's strictness only in `_map_data`. Flag for the planner to settle.

   > **RESOLVED — Plan 04, `P-03`.** The recommendation was **not** taken. `format_mv` is
   > **strict**: no `'N/A'` fallback inside the helper. D-10's strictness lives in `_map_data`
   > (direct indexing, so an absent key raises rather than resolving to a valid-looking `0`), which
   > means every value reaching a render site is already an int. A tolerant fallback inside the
   > helper would recreate in the display layer exactly the tolerant-reader shape D-07 forbids. The
   > *existing* `try/except` int-coercion at `ic_layout.py:589-592` and `eprom_info.py:391-394`
   > stays — it guards the `vpp_mv > 0` **gate**, a separate concern — and its already-coerced
   > `_vpp_mv` local is what is passed to `format_mv`.

2. **One plan or two?** (explicitly Claude's Discretion.) The simulation shows the comparator makes
   either ordering work. Two plans give a free intermediate capture for D-06's "zero wire change"
   assertion and a cleaner `148-DB-DIFF.md`; one plan avoids an intermediate state where
   `diff_db.py` exits 1. Recommendation: **two**, with the migration first — the intermediate RED
   is a *deliberate, captured* transcript, not an accident.

   > **RESOLVED — Plan 06, `P-05`.** **Two**, as recommended. The schema migration landed in
   > Plan 03; the D-03 margin-rail rule lands in Plan 06. This makes the D-11 RED transcript a
   > deliberate captured artifact rather than an accident, and it lets Plan 03's own proof be the
   > strongest available statement — *every pre-existing bucket count unchanged*.

3. **Does the meta-repo `v1.3-defect-coverage-ids.json` get updated?** It is already drifted (78 vs
   68). CONTEXT.md says a legitimate defect-signature change is "a separate, deliberate,
   cross-repo decision — never a side effect". Since D-09 changes only the *rendering* of the pulse
   column and not the bucketing (`pulse_bucket` takes ints today), signatures should be stable —
   but this should be measured after the change, not assumed.

   > **RESOLVED — Plan 05, Task 3, and deliberately resolved *by measurement*, not by assumption.**
   > The answer is **NO**, the meta ledger is not written by this phase. Task 3 generates a ledger
   > into a scratch path on both sides of the change and compares the `DEFECT-COV-NN` ID sets,
   > recording the result in the plan SUMMARY. If the sets differ, the ledger is still **not**
   > updated — the delta is recorded and flagged as a separate cross-repo decision. This is what
   > retires Assumption **A1** below; the assumption is discharged by that comparison rather than
   > carried into execution. Note also that the meta ledger is already drifted today (78 committed
   > entries vs 68 from a fresh generate, consistent with the standing 121-01 note), so Phase 148
   > must not be judged against it.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | Deleting `parse_pulse_us` leaves `DEFECT-COV-NN` signatures unchanged, so the meta ledger needs no update | Open Q3 | A regen would mint new IDs into a tracked meta file |
| A2 | The 2 `extra_chips.json` records are the only non-decode-path emission | F-1 | A third path would leave chips on the old schema |
| A3 | 325 KB is an acceptable committed-fixture size | D-14 | Reviewer objection; falls back to a per-chip SHA map |
| A4 | The D-03 and SRAM mutations do not interact | Edit Sites §A | Measured: no SRAM part has `vdd == 4000`, so no interaction is possible |
| A5 | CI (py3.11) reproduces the local pytest result | Gates | A py3.11-only failure would surface at PR time |

*Everything else in this document is a command output reproduced above, or a verbatim quotation
from a tracked file.*

---

## Sources

### Primary (HIGH — direct measurement on the live tree, 2026-08-19)
- `firestarter_app/firestarter/data/chip_database.json` — all D-03 counts, value censuses, the 56-mover list
- `firestarter_app/tools/build_db.py` — `:17-20, 146-159, 192-200, 412-432, 708-803, 807-821, 829-859`
- `firestarter_app/tools/extra_chips.json` — both supplement records, verbatim
- `firestarter_app/firestarter/database.py` — `:128-143, 174-200, 370-441, 536-626`
- `firestarter_app/tools/diff_db.py` — `:1-45, 306-370, 373-392, 400-597, 603-700`
- `firestarter_app/tools/audit_coverage_matrix.py` — `:59-68, 106-119, 516-542, 1717-1739, 1885-1936`
- `firestarter_app/tools/check_dispatch.py` — `:58-108, 180-215, 310-376`
- `firestarter_app/firestarter/ic_layout.py:557-612`, `eprom_info.py:60-92, 240-270, 383-425`
- `firestarter_app/tests/test_chip_database_field_inventory.py:36-110, 290-445` + `tests/golden/chip_database_field_inventory.json` (`meta` read in full)
- `firestarter_app/tests/test_diff_db_gate.py:28-132`, `tests/test_audit_coverage_matrix.py:440-620`
- `firestarter_app/tests/__snapshots__/test_characterization.ambr`, `tests/test_characterization.py:345-358`
- `firestarter_app/.github/workflows/ci.yml:80-90`, `pyproject.toml:109-190`, `tools/check_mypy_watermark.py:106-126`
- Live runs: `build_db.py` (exit 0, byte-identical), `diff_db.py` (exit 0, 744), `check_dispatch.py` (exit 0, 746), `audit_coverage_matrix.py` (exit 0, matches golden), `pytest` (1616 passed, 280 s), `ruff` (pass ×2), `check_mypy_watermark.py` (exit 2)
- Two purpose-built simulations of the post-migration `diff_db` classification, and a working 746-chip wire-dict capture prototype
- `https://gitlab.com/DavidGriffith/minipro/…a8efaedc…/infoic.xml` — fetched (HTTP 200, 17.8 MB); 27,862 `<ic>` elements scanned for `pulse_delay`

### Primary (HIGH — tracked project documents)
- `.planning/phases/148-…/148-CONTEXT.md` (read in full), `.planning/REQUIREMENTS.md` §DATA + §Out of Scope, `.planning/ROADMAP.md:150-262`, `.planning/PROJECT.md:42-137`, `.planning/STATE.md:5-103`, `.planning/seeds/db-numeric-values-simplification.md`
- `.planning/phases/140-parameter-table/140-03-SUMMARY.md:20-380` — the planted-violation precedent
- `/workspaces/CLAUDE.md`, `.claude/skills/devtest-rootcause/SKILL.md`

### Not used
- Knowledge graph — `graphify status` reports `stale: true`, **1168 h old, 1392 commits behind**; a query for the phase's core terms returned zero nodes. No graph context is carried into this document.

---

## Metadata

**Confidence breakdown:**
- Current code shape — **HIGH**: every line quoted from the live tree with `awk`-verified numbers.
- D-03 measurements — **HIGH**: reproduced by independent script; 12 of 15 exact, 3 off-by-small documented as F-4/F-5/F-6.
- Proof mechanics (D-11/D-13/D-14/D-15) — **HIGH**: D-11 and D-14 were *executed*, not reasoned; D-13's precedent transcripts read verbatim; D-15 verified by exhaustive snapshot grep.
- Regeneration & gates — **HIGH**: every command run, exit codes and timings recorded.
- Open questions 1 and 3 — **MEDIUM**: depend on decisions/measurements not yet taken.

**Research date:** 2026-08-19
**Valid until:** ~2026-09-18 for the code-shape findings (stable, single-branch repo). The
`diff_db` bucket counts and the pytest total are valid **only until the next commit to
`firestarter_app`** — re-measure if the branch advances before planning.
