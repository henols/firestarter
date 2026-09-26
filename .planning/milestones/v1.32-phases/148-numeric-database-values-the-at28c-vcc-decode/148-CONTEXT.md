# Phase 148: Numeric Database Values & the AT28C VCC Decode - Context

**Gathered:** 2026-08-18
**Status:** Ready for planning

<domain>
## Phase Boundary

The generated database states each electrical and timing value **once**, as an integer in one
unit — voltages in millivolts, timings in microseconds — and the AT28C family's VCC stops
reporting `4V`.

**In scope:** the numeric migration in `build_db.py`'s emitter (`vcc_mv` / `vdd_mv` / `vpp_mv` /
`pulse_duration_us`), the VCC margin-rail correction in the same decode function, deletion of
`database.py`'s string-coercion layer **and** `audit_coverage_matrix.py`'s `parse_pulse_us`, a
single mV→string render helper for the three display call sites, a normalizing comparator in
`diff_db.py`, and re-derivation of the two goldens the migration moves. DATA-01…DATA-05.
**Also in scope, added 2026-08-19 per `148-RESEARCH.md` F-1:** `tools/extra_chips.json` is a
**second emission path** — `build_db.py:830-857` merges its two records (TI `2516`, `2532`)
post-decode and byte-faithful, so they carry the old string schema verbatim. Unmigrated, 2 of 746
chips ship the old schema and D-10's direct indexing raises `KeyError` on both. It is also part of
the field-inventory golden's key union (`meta.generator_scan_scope`). Migrating it is a hand edit
to an **authored supplement** — state it explicitly in the plan; it is emphatically not a hand edit
to generated JSON.
**Host-only — `firestarter_app/` only.** The firmware never reads the JSON.

**Out of scope:** any firmware change (Phase 149 owns the only firmware-touching workstream);
`protect_on_after` (DATA-06 → **Phase 150**, where the consumer is created); the `vcc=5500`
EEPROM-class anomaly (29 chips — see `<deferred>`); any `support_status` change; `chip_id_value`
(stays a hex string per the seed); `pinout` / `type` / `part_number` (categoricals, stay strings).

**Cross-phase constraint:** Phase 149 also writes the host DB-consumption layer, so **148 and 149
must never share a parallel wave** (ROADMAP sequencing spine). Phase 148 does **not** touch
`cli_handlers.py`, so it has no collision with 147 or 150.

**Evidence Ceiling applies (binding, from `PROJECT.md` §Current Milestone: v1.32).** No AT28C part
exists in operator inventory. No criterion in this phase may require real silicon, assert the
`0x0D` write path is proven, graduate `0x0D` out of `UNVERIFIED`, change any `support_status`, or
be phrased as closing gh#21/#32/#11/#12. This phase corrects **data the generator emits**; it makes
**no claim** about AT28C silicon behaviour. Note also that `vcc` is **inert on the wire** — see
D-06 — so nothing here can explain or fix `write BAD`.

</domain>

<decisions>
## Implementation Decisions

### The VCC correction (DATA-01, DATA-04)

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

### The numeric migration (DATA-02, DATA-03)

- **D-07: The seed's schema is locked — do not re-open it.** `.planning/seeds/db-numeric-values-simplification.md`
  §"Decided design": `vcc: "5V"` → `vcc_mv: 5000`; `vdd` → `vdd_mv`; `vpp` + `vpp_mv` → `vpp_mv`
  only; `pulse_duration` → `pulse_duration_us`. `chip_id_value` **stays** a hex string (canonical
  in datasheets and `infoic.xml`; JSON has no hex literal). `type` / `support_status` / `pinout` /
  `part_number` stay categorical strings. Clean break — **no tolerant reader**.

- **D-08: The `pulse_duration_us: 0` sentinel keeps the seed's value — the conflation is closed at its source.**
  Today `interpret_timing` (`build_db.py:412-432`) defaults `val = 0` with a
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

- **D-09: `audit_coverage_matrix.py`'s `parse_pulse_us` is deleted too.**
  DATA-03's discipline is about the defect class, not one filename. It is a second live string parser
  (`tools/audit_coverage_matrix.py:105-109`) that **raises** on any non-`" us"` value, called at
  ~8 sites, exercised by an imported test suite against the live database. Leaving it — or
  widening it to accept ints — is precisely the "bypassed, not gone" shape DATA-03 forbids, and a
  tolerant reader outlives the last string it was written for. Call sites read
  `chip["programming"]["pulse_duration_us"]` directly; the `_parseable_pulse_rows` filter at
  `:1718-1727` becomes `!= 0`.

- **D-10: Stale `~/.firestarter/database.json` overrides break, they do not mis-resolve.**
  They break silently. No detection layer, no migration message, no warning: ship exactly the seed's
  clean break. **However**, read the new keys with direct indexing
  (`chip["electrical"]["vcc_mv"]`), **not** `.get(key, 0)` — otherwise a stale override missing
  `pulse_duration_us` resolves to `0`, which now means "algorithm-controlled", and a 0x07 chip is
  programmed with no pulse. Absent key ⇒ exception, never a valid-looking value. This adds no
  surface and is not a coercion layer.
  **Rejected:** a detect-and-refuse migration error naming the file and field; detect-warn-and-
  ignore (leaves the user silently running without the override they wrote).

### Proving the blast radius (DATA-05)

- **D-11: `diff_db.py` gets a normalizing comparator — the migration must move no chip between buckets.**
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

  *(Mechanism corrected 2026-08-19 by `148-RESEARCH.md` **F-2** — measured, not argued. The decision
  stands; its stated yardstick does not. `diff_db.py` **already reports 744 changed chips today**
  (`PGSZ_PAGE_SIZE` 2 + `PROV01_PROTECT_METADATA` 742, exit 0) because
  `tools/baseline/chip_database.baseline.json` predates Phase 136.1. "Produces **zero** diff rows"
  is therefore **unachievable** and would be a false RED. The achievable and equally strong form,
  measured in RESEARCH.md §"Validation Architecture": the changed-chip total and every existing
  bucket count are **unchanged**, no chip moves between buckets, and the 56 movers appear as their
  own **new** bucket. RESEARCH.md also measured that a `_RATIONALES` entry alone is **not**
  sufficient for that bucket — it needs a scoped `_classify_diff` branch (its Option B).)*

- **D-12: `148-DB-DIFF.md` in the phase directory is the review artifact.** It carries the
  `diff_db.py` run output, the 56-chip mover list, the D-03 justification with its citation, and
  the **explicit non-claim** that the `vcc=5500` group was deliberately left untouched. One
  document, reviewable whole, where a future investigator looks — not split across plan SUMMARYs.

- **D-13: `chip_database_field_inventory.json` is re-derived with a seen-to-fail transcript.**
  The golden is `tests/golden/chip_database_field_inventory.json`, and it is re-derived
  independently. Its own `how_to_update` forbids hand-editing a count: re-derive every
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

### Human output (DATA-02 display side)

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

  *(Mechanism corrected 2026-08-19 by `148-RESEARCH.md` **F-3**. The byte-identical render contract
  above **stands and is load-bearing**. What does not: "the snapshot diff then changes on exactly
  the AT28C-family lines". **No AT28C VCC line exists in any snapshot.** The only info-view snapshot
  is `test_info_known_chip`, which runs `firestarter info W27C512` — `vcc: "5V"`, **not a mover** —
  and the `test_list` snapshot renders only a VPP column. The correct criterion is **stronger**: the
  `.ambr` must be **byte-unchanged** by this phase. Two consequences: (a) do not plan a snapshot
  re-baseline; (b) **criterion 1 has zero existing test coverage** — a new test asserting
  `firestarter info AT28C256` renders `VCC: 5.0v` is a Wave 0 gap, not an optional extra.)*

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone charter & requirements (binding)
- `.planning/PROJECT.md` §"Current Milestone: v1.32" — the Evidence Ceiling, kickoff decision
  **D-02** (the proof rule for the `vcc` fix), workstream table rows 2 and 6.
- `.planning/REQUIREMENTS.md` §"Database Decode & Numeric Values (DATA)" — DATA-01…DATA-06.
  **DATA-01 is hand-corrected by this phase per D-04.** DATA-06 belongs to **Phase 150**.
- `.planning/REQUIREMENTS.md` §"Out of Scope" — the `_PAGE_SIZE_BY_PART` and GATE-03 rows are
  binding on this phase specifically.
- `.planning/ROADMAP.md` §"v1.32" — sequencing spine, locked decisions, must-not-do list;
  §"Phase 148" success criteria (**criterion #1 hand-corrected per D-04**).
- `.planning/seeds/db-numeric-values-simplification.md` — §"Decided design" is **locked** (D-07);
  §"Touch points"; §"Breaking-change note". Read before proposing any schema variation.

### The generator (where every decode change lands)
- `firestarter_app/tools/build_db.py:192-199` — `VCC_VOLTAGES`, the `[VERIFIED: minipro
  database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]]` table D-01 rests on.
- `firestarter_app/tools/build_db.py:730-760` — the `electrical` / `programming` emitter:
  `vpp`+`vpp_mv`, `vcc` at bits 11-8, `vdd` at bits 15-12, `pulse_duration`.
- `firestarter_app/tools/build_db.py:412-432` — `interpret_timing`; the `except` branch D-08
  makes fatal.
- `firestarter_app/tools/build_db.py:807-821` — the shipped SRAM `vcc = vdd` normalization. **The
  precedent D-03 extends, and its type-keyed comment explains why UV-EPROM `vdd` must never be
  surfaced as VCC.**
- `firestarter_app/tools/DECODE-NOTES.md` — decode provenance notes.

### The coercion layer being deleted
- `firestarter_app/firestarter/database.py:128-140` — `_parse_pulse_duration` (DATA-03).
- `firestarter_app/firestarter/database.py:379-393` — the `.replace("V","")` → `float()` path
  (DATA-03).
- `firestarter_app/firestarter/database.py:414-417` — `vpp_volts` / `vcc` / `pulse-delay` in the
  mapped dict.
- `firestarter_app/firestarter/database.py:536-557` — `convert_to_programmer`, **the wire seam**
  (D-06, D-14) and the dead `vpp_volts` fallback at `:544-546`.
- `firestarter_app/tools/audit_coverage_matrix.py:105-109` — `parse_pulse_us`, the second
  coercion site (D-09); its ~8 call sites and the `:1718-1727` string filter.

### Proof and gate surfaces
- `firestarter_app/tools/diff_db.py` — GATE-02. `:445-458` are the field-name-keyed classification
  rules D-11 normalizes; `_RATIONALES` (`:44+`) is the citation format the new rule follows;
  the module docstring documents exit codes 0/1/2.
- `firestarter_app/tools/baseline/chip_database.baseline.json` — **NOT re-pinned** (D-11).
- `firestarter_app/tests/test_chip_database_field_inventory.py` — the eight-test schema gate
  (TABLE-05 / D-12), including the AST walk of `chip_entry` and the `FIRESTARTER_CHIP_DB_JSON` /
  `FIRESTARTER_BUILD_DB_SOURCE` planted-violation seams (bind at import — set in a child process,
  never monkeypatch).
- `firestarter_app/tests/golden/chip_database_field_inventory.json` — read `meta.how_to_update`,
  `meta.why_counts_not_names`, and `meta.why_not_diff_db` **before** touching it (D-13).
- `firestarter_app/tools/check_dispatch.py` — **GATE-03. Never weakened, and needs no edit:** it
  reads only `electrical.vpp_mv` (already an int) and `electrical.type` (stays a string).
  `tools/baseline/dispatch_baseline.json` carries no voltage or timing field — verified.
- `firestarter_app/tests/test_diff_db_gate.py` — pins diff_db's gate behaviour.
- `firestarter_app/tests/test_audit_coverage_matrix.py:440-510` — the subprocess invocations; they
  already pass `--output` / `--ledger` into `tmp_path`, and `:581-610` compares the committed
  golden. `--check` against an empty ledger must exit 1; against the full ledger, 0.
- `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` — regenerated by D-09. Header says
  DO NOT EDIT BY HAND; re-run the tool.

### Display
- `firestarter_app/firestarter/ic_layout.py:568` (`vcc_str`), `:590-597` (`vpp_str`, gated on
  `vpp_mv > 0` and non-SRAM/FRAM), `:606-610` (pulse row, **already** omitted on 0).
- `firestarter_app/firestarter/eprom_info.py:248-263` (info card rows), `:395-421` (list view).
- `firestarter_app/tests/__snapshots__/test_characterization.ambr:432` — the pinned
  `VCC: 5.0v` / `VPP: 12.0v` / `Pulse delay: 100µS` block (D-15).
- `firestarter_app/tests/test_ic_layout.py:94-145` — the FM1608 `vpp_str`-absent assertions.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The SRAM `vcc = vdd` normalization** (`build_db.py:807-821`) — a shipped, cited, type-keyed
  correction of exactly this category error. D-03 is its sibling; write the new rule in the same
  place, in the same commented style, with the same kind of citation.
- **`_RATIONALES` in `diff_db.py`** — the established format for a cited root-cause rule
  (`RULE_ALGO`, `BUG2_AND_BUG3`), each embedding a `[VERIFIED: minipro ...]` permalink citation.
- **`electrical.vpp_mv`** — the migration's own precedent. It already exists on all 746 chips as
  an int, is already what the wire carries, and is already what GATE-03 reads. The job is to make
  the other three fields look like it.
- **`interpret_timing`'s narrowed `except`** (WR-05, Plan 98-03) — already narrowed from a bare
  `except Exception` for exactly the reason D-08 now finishes: an upstream decode fault must be
  visible, not silently shipped as a valid `0 us`.
- **The pulse-row omission at `ic_layout.py:603-607`** — `0` already means "no fixed programming
  pulse to report". D-08's sentinel needs no display work.

### Established Patterns
- **`chip_database.json` is GENERATED and never hand-edited.** Every value change lands in
  `build_db.py`'s decode function and is regenerated. Three per-chip lookup tables were
  deliberately deleted in Phase 70 (D-02/D-03 of that phase); the pattern is not reintroduced
  under a new name.
- **A blast radius is a measurement, not an estimate.** DATA-05's rule — "a one-chip fix that
  moves hundreds of chips means the condition was too broad" — is why D-03 carries the four-way
  split table. Any proposed widening must be re-measured against it, not argued.
- **Goldens are re-derived independently and proven to still fail.** The field-inventory golden's
  own `why_not_diff_db` note explains that a baseline which can be regenerated is a gate that can
  be silenced; that is the standard D-13 holds to.
- **`vcc` never reaches the firmware.** No VCC field on the wire, no VCC control register. The
  correction is display-and-data honesty only.
- **Every `# noqa: BLE001` in this repo is inert** (ruff `select` is `[E,F,I,UP]`), so a broad
  `except Exception:` added here is gated by nothing. Keep excepts narrow by hand.

### Integration Points
- `build_db.py` emitter → `chip_database.json` → `database.py._map_data` → `convert_to_programmer`
  → the wire. D-14 asserts equivalence at the last hop.
- `build_db.py` emitter → `chip_database.json` → `diff_db.py` (D-11), `check_dispatch.py`
  (unchanged), `test_chip_database_field_inventory.py` (D-13), `audit_coverage_matrix.py` (D-09).
- `database.py` (helper, D-16) → `ic_layout.py` ×2 → `eprom_info.py` → the characterization
  snapshot (D-15).

### Execution mechanics (preconditions, not decisions)

- **⚠ `audit_coverage_matrix.py` writes into the META repo by default.** `_REPO_ROOT` resolves to
  `dirname(dirname(dirname(__file__)))` = **`/workspaces`**, so `DEFAULT_OUTPUT` is
  `/workspaces/.planning/v1.3-COVERAGE-MATRIX.md` and `DEFAULT_LEDGER` is
  `/workspaces/.planning/v1.3-defect-coverage-ids.json`. **Both are tracked files in the meta
  repo**, and the tool mutates the ledger (mints new `DEFECT-COV-NN` IDs). Always pass explicit
  `--output` / `--ledger` to a scratch path, exactly as the module docstring and the test suite
  already do. If D-09's changes legitimately alter defect signatures, the tracked meta ledger
  update is a **separate, deliberate, cross-repo** decision — never a side effect of a regen run.
- **Sub-repo branch base.** `firestarter_app` is already on
  `gsd/v1.32-at28c-write-path-root-cause-report-provenance` (Phase 147's `147-01` moved it off the
  v1.31 branch and forked from `origin/beta`, app **3.0.0b21**). No re-basing needed — verify by
  content, not by `merge-base --is-ancestor` (the v1.31 PRs were squashed).
- **`build_db.py` fetches `infoic.xml` over the network** (`MINIPRO_XML_URL` pinned at commit
  `a8efaedc`); there is no cached copy in the repo. A regen step needs network access, and the
  pinned commit must not drift.
- **Wave scheduling.** 148 and 149 both write the host DB-consumption layer — never the same wave.
  148 touches no `cli_handlers.py` path, so it has no 147/150 collision.
- **Meta-repo working tree is dirty** (`.gitignore`, both submodule gitlinks, untracked
  `.claude/`, `package*.json`). Stage specific files only.
- **`test_flash_path_record_sync.py` asserts whole-repo porcelain** — commit before running the
  full suite, or it goes RED on any mid-change diff.

</code_context>

<specifics>
## Specific Ideas

- **The four-way split table in D-03 is the artifact of this discussion.** It was not in any
  requirement, roadmap criterion, or seed — it was measured during the discussion and it is what
  turned a plausible "align vcc to vdd for EEPROM parts" into a rule that would have set sixteen
  5 V Microchip EEPROMs to 3.3 V. Keep it in front of anyone who proposes touching the condition.
- **The strongest form of DATA-05's proof is a diff that is empty where it should be empty.**
  D-11's comparator makes the migration produce literally zero rows. "746 rows, all explained" and
  "0 rows, plus 56 explained movers" are not equally good artifacts, even though both exit 0.
- **`4V` is a real number that is not a real voltage.** Framing the rule as "no part in this
  database has a 4.0 V nominal supply — index `0x02` is a verify-margin rail" is what makes it a
  claim about the decode table rather than a patch aimed at one family. Keep that wording in the
  code comment and in `148-DB-DIFF.md`.

</specifics>

<deferred>
## Deferred Ideas

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

### Reviewed Todos (not folded)

20 pending todos were cross-referenced against Phase 148. **None folded** — every match scored on
keyword noise (`build`, `chip`, `values`, `data`, `phase`, `blank`, `vpp`), and the two that look
closest are already mapped elsewhere:

- *Decode infoic.xml flags bits 14/15 (protect-before/protect-after) in `build_db.py`* (0.6) —
  genuinely `build_db.py` decode work, but it is the `protect_on_after` story, which is **DATA-06
  → Phase 150**, deliberately mapped where the consumer is created so the decision cannot be taken
  twice.
- *`build_db_diff`'s `ladder_state` no longer reaches `community-reported`* (0.6) — despite the
  name, this is `diagnostic_report.py` / `classify_fingerprint`, not `tools/diff_db.py`.
  Defer-with-owner (`henols`) from v1.30's operator batch C-1; unrelated to this phase.
- *AT28C256 write-path failure (gh#20)* (0.6) — Backlog **999.29**, explicitly **not** retired by
  v1.32 and blocked by the Evidence Ceiling.
- *Skip VPP checks when VPP unused*, *CONFIG_VERSION not bumped*, *dev-tools build flag fails
  CLOSED*, *FM1608 byte 0*, *COBS frame deadline*, *dead `json_init()`*, *`DATA_BUFFER_SIZE`
  spike* — firmware, out of a host-only phase.
- *avrdude MCU-detection fallback*, *GSD plan-scan loose regex*, *Phase 130 record gate*, *JP4
  labels*, *JP5 dead renderer*, *`response_code` log macro*, *board photography /
  MODIFICATIONS.md* — unrelated tooling and hardware documentation.
- *Reply on gh#12 / correct the b14 release notes* (0.6) → **Phase 152** (OUT-01).
- *Land `write --sdp-relock`* (0.6) → **Phase 150** (Backlog 999.28, promoted).

</deferred>

---

*Phase: 148-Numeric Database Values & the AT28C VCC Decode*
*Context gathered: 2026-08-18*
