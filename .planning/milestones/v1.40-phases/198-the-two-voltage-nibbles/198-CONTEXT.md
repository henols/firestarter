# Phase 198: The two voltage nibbles - Context

**Gathered:** 2026-09-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Settle what `infoic.xml`'s voltage word encodes per algorithm family, write the finding down with
its evidence, correct the Fujitsu VPP and program-VCC the vendored datasheets contradict, and
dispose of the 28-row `vcc_mv: 5500` group either way — closing the todo that has blocked it since
v1.32 Phase 148.

**In scope:** `build_db.py`'s `VCC_VOLTAGES` / `VPP_MV` decode tables and the low-byte mask;
`tools/datasheet_overrides.json` entries for the datasheet-backed Fujitsu rows and the 12 held
rows; `tools/DECODE-NOTES.md` § 9; the per-row disposition of the 28; the todo close and its
successor backlog entry; the held gh#66 draft; the test legs the regeneration diff invalidates.

**Out of scope:** the rail ceiling, the measured deliverable maximum and the warn-on-shortfall
surface (Phase 199); surfacing `vdd_mv` to the operator (Phase 200); the firmware blank-check
region (Phase 201); any firmware change at all; pinout correctness; adding chips —
`tools/extra_chips.json` keeps that job.

</domain>

<decisions>
## Implementation Decisions

### The decode tables are completed, not corrected

- **D-01:** **`VCC_VOLTAGES` is completed from upstream's `xg_vcc_voltages[]`.** Measured against
  the pinned `database.c @ a8efaedc`: the `xg` table is a **strict, conflict-free superset** of
  `tl866ii_vcc_voltages[]` — 6 shared indices, **zero** value conflicts, plus 9 more
  (`0x06`=1800, `0x07`=2500, `0x08`=3000, `0x09`=1200, `0x0A`=4750, `0x0B`=5250, `0x0C`=5750,
  `0x0D`=6000, `0x0E`=6250). That is one encoding implemented to different depths by different
  programmer models, not two encodings — so completing it is **decoder completion under milestone
  D-2**, not a correction, and the table stays in code.
  **Contrast, and the reason this is not model-mixing:** `tl866a_vcc_voltages[]` conflicts on 4 of
  its 6 shared indices and `tl866a_vpp_voltages[]` on **8 of 8**. The TL866A is a genuinely
  different encoding and must not be used.
  **Effect:** 24 rows stop reaching a fabricated 5000 mV through `.get(idx, 5000)`.

- **D-02:** **`VPP_MV` is completed too, and the `& 0xF0` mask is fixed.** Add `0xF1`=25000 and
  `0xF2`=21000. The current `VPP_MV.get(voltages & 0xF0, 0)` collapses `0xF1` and `0xF2` onto
  `0xF0`, so a 25 V part would silently decode as 18 V — a 7 V under-report on the rail gh#71 is
  already about. Key on the full low byte with the option bits stripped instead.
  **No row carries `0xF1` or `0xF2` today** (measured across all 767 filtered rows), so
  **byte-identical regeneration is the proof** this change ships zero diff.
  — **Reversibility:** reversible — the entries are unreachable until upstream adds such a row.

- **D-03:** **The `.get(idx, default)` silent fallback is NOT replaced by a raise.** The
  fail-closed option was offered and declined. The generator keeps defaulting rather than stopping
  the build. Anything still unmapped after D-01 must therefore be named in the write-down, because
  nothing mechanical will report it.

### The 0x06 carve-out — the one place a completed decode is deliberately not emitted

- **D-04:** **The 12 rows at vdd index `0x06` keep `vdd_mv: 5000`, byte-identical to today.**
  The completed table decodes `0x06` to 1800 mV; 1.8 V is not credible as a program rail for a 5 V
  28C64-class EEPROM. Those 12 are exactly sub-group 2 of the VOLT-03 group
  (EXEL ×7, ST ×3, SGS-THOMSON ×2), all carrying `voltages=0x64xx`.
  — **Reversibility:** reversible — deleting the 12 entries restores the decoded 1800.

- **D-05:** **The carve-out is expressed as 12 explicit override entries, not as a table omission.**
  `VCC_VOLTAGES` gets `0x06`=1800 like every other index; the exception then lives in
  `datasheet_overrides.json` as 12 entries (`was: 1800, is: 5000`), each `UNSOURCED`, each stating
  that the completed decode is not credible for the part class and naming what would close it —
  the part's own datasheet. **Rejected: omitting `0x06` from the table.** That would be
  byte-identical too, but the 12 rows would reach 5000 through the same silent `.get` default this
  phase is otherwise closing, and it would read as an oversight rather than a decision.
  This follows the six `UNSOURCED` NMOS entries Phase 197 already ships.

- **D-06:** **The `vdd < vcc` predicate is the group's key, and it is exact.** Measured under the
  completed table across all 767 filtered rows: `decoded vdd < decoded vcc` selects **exactly 28
  rows and nothing else** — 12 at (5500, 1800) and 16 at (5500, 3300) — against 373 rows at
  `vdd == vcc` and 366 at `vdd > vcc`. A program rail below the read rail is internally
  contradictory, so this is value-keyed, part-name-free and non-tunable: the `_VCC_MARGIN_RAIL_MV`
  shape, relational. **Phase 148 measured and rejected the inverse relation** (`vcc < vdd`, 225
  rows, sweeping 167 UV-EPROMs); this is its complement and does not inherit that defect.
  **The predicate is documented, not shipped as a correction** — no value hangs off it this phase.

### VOLT-02 — the Fujitsu corrections

- **D-07:** **VPP goes to 12500, not 12200.** MBM27C4001's own datasheet (Edition 1.0, March 1993,
  attached to gh#66 by `dim20`) specifies 12.5 V ± 0.3 V, i.e. 12.2–12.8 V. 12500 is the datasheet
  nominal, is what the sibling `MBM27C1000P` already carries via VPP index `0x60`, and is a rail
  the encoding can express. 12200 would satisfy VOLT-02's literal "at or above 12.2 V" while
  sitting at the very bottom of the tolerance band with no margin below it.

- **D-08:** **Two rows get the VPP correction: `FUJITSU/MBM27C1001` and `FUJITSU/MBM27C4001`.**
  Both PDFs are git-tracked, so no OVR-03 citation dangles. **`FUJITSU/MBM27C2001` gets nothing**
  and stays at 12000 — it carries the identical `voltages=0x4000` word but has no vendored
  datasheet, and citing its sibling `MBM27C2000P`'s 12500 would apply one part's reading to another
  without evidence, which is the practice D-02 of Phase 197 exists to make impossible. Record it in
  the write-down as a known, unsourced family inconsistency.

- **D-09:** **`vdd_mv` 5500 → 6000 is corrected in THIS phase, not Phase 200,** for the three rows
  whose vendored datasheets state it: `FUJITSU/MBM27C4001`, `FUJITSU/MBM27C1001` and
  `FUJITSU/MBM27128`. All three datasheets say 6.0 V ± 0.25 V, and two of the three override notes
  already quote that figure verbatim. Phase 200 owns *surfacing* `vdd_mv`, so it should surface a
  correct number rather than open by re-deciding a data correction whose evidence is on disk.

- **D-10:** **The firmware guard-band consequence is recorded in the phase record only.** The
  firmware accepts `vpp_mv × 95/100` (low, warning) to `vpp_mv + 500` (high, hard error). Raising
  to 12500 moves the settable band **11400–12500 → 11875–13000**, which makes the datasheet's
  12.2–12.8 V window fully settable — `dim20` could not set 12.5 V precisely because the database
  targeted 12000. 13000 still sits under the datasheet's 13.5 V abs-max warning. **No host-side
  test encodes this** (it would duplicate a firmware constant across repos) and **the public gh#66
  answer does not mention it** — that answer stays strictly to database values that changed.

### VOLT-03 — the 28 rows, and how the todo closes

- **D-11:** **All 28 rows ship unchanged.** VOLT-03 explicitly permits this: *"Leaving them
  unproven and unchanged is an acceptable outcome; changing them on an unproven assumption is
  not."* No plausibility floor, no clamp, no `support_status` change. The four options of
  fail-the-build, mark-unproven and clamp-to-vcc were each offered and declined.
  — **Reversibility:** reversible — nothing ships differently from today for these rows.

- **D-12:** **The todo closes to `completed/` and a successor backlog entry is filed.**
  `.planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md` asked what the nibbles encode;
  this phase answers it, so it is genuinely completed even though no value moved. The successor
  carries the residue: 28 rows still reporting 5.5 V, 12 of them held at an unsourced 5000, closable
  only at one datasheet per row. Follows Phase 197's 999.69/70/71 pattern.

- **D-13:** **Sub-group 1's premise is tested per row, not restated.** The todo characterises its 16
  rows as *"genuinely-3.3V Microchip memory-family parts"*, but `28C16A`, `28C17A`, `28C64A`,
  `28C64B` and `28C256` are 5 V parts by class and only `28LV64A` is low-voltage. If that is right,
  substituting `vdd` there would set 5 V EEPROMs to 3.3 V — exactly the outcome Phase 148 measured
  and rejected for all three of its alternative keys. Classify all 16 by part class, state which way
  each cuts, on the `197-at28c-guard-evidence-for-phase-199.md` precedent: reproducible method
  first, every row disposed with a reason, a named honesty limit. Note the repo vendors **no**
  Microchip or AMD 28C datasheet, so the honesty limit is real and must be stated.

- **D-14:** **The archived `148-DB-DIFF.md` is NOT edited.** Its § Non-claim states sub-group 2's
  `vdd_mv` "already records" 5.0 V, which this phase falsifies — that 5000 is a fallback from an
  unmapped index, not a decode. **Decided by Claude on project precedent, not asked:** archived
  `.planning` records are historical-by-intent and rewriting one destroys the evidence of what was
  believed. The falsification is recorded in Phase 198's artifacts and in `DECODE-NOTES.md`,
  pointing at the archived text.

### VOLT-01 — what the write-down claims

- **D-15:** **`DECODE-NOTES.md` § 9 makes the general finding, with its limits named.** The finding:
  the two nibbles and the VPP byte select a **programmer rail index, not a chip requirement**; the
  index→volt map is **model-dependent** (`0x00` is 12 V on the TL866-II and 12.5 V on the TL866A;
  `0x20` is 9.5 V and 21 V respectively); and a part whose datasheet value is not a rail gets the
  **nearest selectable one**. Evidence: upstream's own comment at `database.c:123` —
  *"These are not raw DAC output values, but rather indices into internal lookup tables defined in
  the firmware"* — plus three Fujitsu datasheets on disk that all state 6.0 V ± 0.25 V where the
  index selects 5.5 V, because **neither 5.5 nor 6.5 is inside 5.75–6.25** and those are the only
  two rails the TL866-II has near it.
  **The limits are mandatory:** name that the datasheet corroboration is n = 3, all Fujitsu; that
  no claim is made about the 167 unreached index-`0x4` rows; and that the finding does not assert
  any particular row's value is correct.
  § 9 follows PULSE-01's § 8 — markdown, next to the code, so the no-comments rule does not reach it.
  — **Reversibility:** costly — Phases 199 and 200 will build their warning wording on this
  framing, and it reframes every voltage in the generated database as a programmer setting rather
  than a chip requirement.

- **D-16:** **The NMOS 25 V / 21 V values are NOT secretly decodable — this was checked and closed.**
  `xg_vpp_voltages[]` carries `0xF1`=25 V and `0xF2`=21 V, which are exactly the two figures Phase
  197's six `UNSOURCED` entries hold. Measured: **no filtered row carries `0xF1` or `0xF2`**. All
  eight NMOS 2716/2732 rows carry VPP byte `0xF0` = 18 V, the TL866-II's maximum — as does
  `MBM27128`, which gh#71 measured as needing 21 V. Record this: it is a tempting false lead that
  would otherwise be rediscovered, and the saturation-at-the-model-maximum pattern is direct
  evidence for D-15.

### VOLT-04 — gh#66

- **D-17:** **The draft is written, held, and claims corrections only.** Carried forward from
  197-08's operator ruling without re-asking: nothing is pushed, the branch has no upstream, so no
  version or sha a reader could look up exists yet. The draft states the two corrected values and
  the confirmed 6.0 V `vdd_mv` finding under an explicit *"this does not close this report"*
  heading, credits `dim20` for the datasheet, and **says nothing new about causation** — `dim20`
  already proved correct VPP alone does not fix it (12.4 V, identical failure at `0x07ff00`), and
  the last-256-byte hypothesis is already posted and is not this phase's to advance.
  **VOLT-04 is left Pending**, exactly as PULSE-04 is.

- **D-18:** **One consolidated held-pending list.** Phase 198 adds gh#66 to the deferral record that
  `197-GH70-ANSWER.md` § "Held-pending deferral" established, so whoever closes v1.40 finds one list
  naming every issue to post with the same four steps each, rather than two held drafts in two
  directories to find independently.

### Carried forward from Phase 197 — locked, do not re-litigate

- Override key is **`MANUFACTURER/ALIAS`**; **one entry targets exactly one row** (197 D-01, D-02).
- An override **substitutes the decoded input**, before `classify()`'s downstream derivations
  (197 D-03). `support_status` stays derived and is never written by hand.
- Every entry carries `was`/`is` and a datasheet path or the literal `UNSOURCED`; the recorded
  `was` is asserted against the live decode and a mismatch fails the build (197 D-04, D-20).
- The generator **fails closed** on an unknown key, unknown field, duplicate target, unsorted file,
  per-field type mismatch, and a no-op entry (OVR-04, 197 D-04).
- **Decode tables stay in code** — they are the decoder, not a correction (milestone D-2). Only
  values that contradict the decode move into the override file (milestone D-3).
- **Nothing part-specific is hardcoded in the generator** (milestone D-1); any survivor is named
  with its proof under the OVR-06 census.
- Decode findings land in `tools/DECODE-NOTES.md` as a numbered section (PULSE-01 is § 8).
- Inventory and disposition records land in the phase directory on the
  `177-READBACK-INVENTORY.md` precedent: reproducible method first, every row disposed, a named
  honesty limit.
- `chip_database.json` is **GENERATED**. Never hand-edit.
- **No comments in product source**, for any reason (CLAUDE.md, hard rule).

### Claude's Discretion

- How the 12 `0x06` override entries are covered for non-vacuity — whether one planted-mutation
  test in the 197-06 shape, or per-entry assertions.
- Whether the regeneration diff needs a `tests/golden/wire_dict_expected_deltas_198.json` delta
  layer. It almost certainly does: `vpp_mv` crosses the wire, so the two VPP corrections will
  redden `tests/test_wire_dict_equivalence.py` the way the three pulse corrections did. Measure it
  rather than assuming — note that `vcc`/`vdd` are inert on the wire (148-DB-DIFF § Evidence
  Ceiling), so the vdd changes may contribute nothing.
- Where the sub-group-1 per-row disposition file lands, and its exact name.
- The exact wording of the 12 `UNSOURCED` notes, subject to D-05's requirement that each names what
  would close it.
- Whether the `vdd < vcc` predicate ships as a build-time assertion (reporting, not correcting) or
  only as a documented measurement.

### Folded Todos

- **`vcc-5500-high-margin-verify-rail-group.md`** — folded as the subject of VOLT-03. Its
  frontmatter already reads `resolves_phase: 198`. Closed to `completed/` under D-12, with its
  central premise falsified under D-04 and D-13.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone intent and locked decisions
- `.planning/ROADMAP.md` § "v1.40 — Program-Parameter Fidelity" — milestone goal, the D-1…D-6
  activation decisions, phase ordering. Phase 198's own entry and success criteria sit under
  `### Phase 198: The two voltage nibbles`.
- `.planning/REQUIREMENTS.md` — VOLT-01…04 in full, plus the activation decision table and the
  `VOLT-F1` future requirement (*"the remaining families touching `VCC_VOLTAGES[0x04]`… only if
  VOLT-01 proves the nibble semantics generalise"*), which D-15 bears on directly.
- `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-CONTEXT.md` — the
  override file's contract, D-01…D-21. **Everything in "Carried forward" above is sourced here.**

### The blocking todo and its origin
- `.planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md` — the 28-row group, both
  sub-group lists, and the "Solution (TBD)" that D-01/D-06 now answer. **Its premise that
  sub-group 2 runs at 5.0 V is falsified** — see D-04.
- `.planning/milestones/v1.32-phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md`
  § "Non-claim" — the 28-row derivation and the blast-radius discipline this group must be held to;
  § "Evidence Ceiling" — *"`vcc` is inert on the wire"*. **Read, do not edit** (D-14).
- `.planning/milestones/v1.32-phases/148-numeric-database-values-the-at28c-vcc-decode/148-RESEARCH.md`
  F-6 — the direct measurement that settled 12 rather than 13 in sub-group 2.

### The generator
- `firestarter_app/tools/build_db.py` — cited by content, not line number. Load-bearing sites:
  the `VPP_MV` table and its `& 0xF0` masking comment; the `VCC_VOLTAGES` table and
  `_VCC_MARGIN_RAIL_MV`; the `_d_vpp_mv` / `_d_vcc_mv` / `_d_vdd_mv` decode triple; the
  `_decoded_view` / `apply_datasheet_override` block; the `RURP_VPP_CEILING_MV` ceiling check; the
  SRAM `vcc_mv`-from-`vdd_mv` rewrite; the `_VCC_MARGIN_RAIL_MV` value-keyed rewrite immediately
  after it — **that block is the shape D-06's predicate mirrors**; the DIP-parallel filter
  (24–32 pins, not SMD, not serial, `type` in {1, 4}) which defines the 767-row population every
  measurement in this document is taken over.
- `firestarter_app/tools/datasheet_overrides.json` — 9 entries today; this phase adds up to 17
  (2 VPP + 3 vdd + 12 held). Note `MBM27128`'s and `MBM27C1001`'s existing notes already quote the
  6.0 V ± 0.25 V figure D-09 acts on.
- `firestarter_app/tools/DECODE-NOTES.md` — § 8 is PULSE-01's finding and the template for § 9;
  § 6 "Honest gaps" is the template for D-15's named limits.
- `firestarter_app/firestarter/data/chip_database.json` — **GENERATED. Never hand-edit.**

### Upstream ground truth
- `https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/src/database.c`
  — the pinned sha `MINIPRO_XML_URL` also uses. The decisive comment sits immediately above
  `tl866a_vpp_voltages[]`: *"These are not raw DAC output values, but rather indices into internal
  lookup tables defined in the firmware."* Read `tl866a_vpp_voltages`, `tl866a_vcc_voltages`,
  `tl866ii_vpp_voltages`, `tl866ii_vcc_voltages`, `xg_vpp_voltages`, `xg_vcc_voltages`, and the
  unpack at `device->voltages.vdd/vcc/vpp` — note upstream reads `vpp = voltages & 0xff`, the full
  low byte, where the generator masks `& 0xF0`. `LAST_JEDEC_BIT_IS_POWERDOWN_ENABLE` and
  `POWERDOWN_MODE_DISABLE` corroborate that the low nibble is flags.
  **Also unused by the generator and worth a look:** `can_adjust_vcc`/`can_adjust_vpp` are gated on
  a `chip_info` field the generator ignores entirely.
- `infoic.xml` @ the same sha — the `voltages` attribute. A copy exists at
  `/tmp/claude-1000/-workspaces/9f02488d-40fe-469d-84c5-d75d1a492230/scratchpad/infoic.xml`
  (17,861,009 bytes); **verify its sha against the pinned URL before relying on it.**

### The community report this phase answers
- gh#66 — https://github.com/henols/firestarter/issues/66 (`[dev test] MBM27C4001 — FAIL`). OPEN.
  The maintainer's 2026-09-16 cross-check already publishes VPP 12.5 V ± 0.3 V and VCC 6.0 V ±
  0.25 V as confirmed mismatches — **this phase's corrections agree with what is already posted, so
  no retraction is needed**, unlike 197-08's pinout finding. `dim20`'s 2026-09-16 retest at 12.4 V
  failed identically, and the maintainer's reply argues a last-256-byte address pattern across
  three chip sizes. D-17 constrains what the draft may claim.
- `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md`
  § "Held-pending deferral" — the four steps to take at the v1.40 beta cut, and the list D-18 adds
  gh#66 to. **Whoever closes v1.40 must read it.**

### Project rules that constrain execution
- `/workspaces/CLAUDE.md` § "Source code comments — hard rule" — **write no comments into product
  source**, not overridable by a plan, task, skill or subagent instruction. `build_db.py` is dense
  with existing comments; the `VPP_MV` mask comment and the `_VCC_MARGIN_RAIL_MV` comment both sit
  directly on code this phase edits, so deleting a clause will orphan surrounding prose — read the
  remainder and confirm every pronoun still has an antecedent. **Add nothing new.**
- `/workspaces/CLAUDE.md` § "Cross-repo obligations" — this phase is **host-only**; no firmware
  change, and D-10 deliberately declines to mirror a firmware constant onto the host.
- `/workspaces/CLAUDE.md` § "Milestone close and branch protection" — a push to `beta` in
  `firestarter_app` **publishes to PyPI**. The milestone branch is `v1.40-program-parameter-fidelity`
  in all three repos.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The `_VCC_MARGIN_RAIL_MV` rewrite** — an existing, shipped, value-keyed correction written as a
  table lookup rather than a literal *"so it cannot drift from the table"*. D-06's `vdd < vcc`
  predicate is the same shape made relational, and its in-code comment already carries the
  "do NOT widen this to a type, algorithm or relational key without re-measuring" warning that
  Phase 148 earned.
- **`apply_datasheet_override` / `load_datasheet_overrides`** — shipped in Phase 197 with five
  fail-closed legs and 18 tests in `tests/test_datasheet_overrides.py`. This phase adds entries; it
  should not need to change the loader.
- **`tests/test_build_db_constant_census.py` + its frozen golden** — the OVR-06 gate, with three
  planted-literal controls. Any new named constant must be considered against it.
- **`197-REGEN-DIFF.md`** — the shape for this phase's regeneration diff record.
- **`tests/golden/wire_dict_expected_deltas_197.json`** and its non-vacuity test
  `test_the_197_delta_layer_is_capable_of_failing` — the template if a 198 delta layer is needed.

### Established Patterns
- **Decode tables are keyed lookups, never literals.** Both `VPP_MV` and `VCC_VOLTAGES` carry a
  `[VERIFIED: minipro … @ a8efaedc]` provenance marker naming the upstream file and sha. D-01 and
  D-02 must extend that marker to name `xg_vcc_voltages[]` / `xg_vpp_voltages[]` as the source of
  the added indices, not silently widen a table attributed to `tl866ii_*`.
- **`support_status` is computed, never assigned.** Nothing in this phase writes it.
- **`classify()` reassigns `proto_id`**; `_upstream_proto_id` is captured before the call. All 28
  VOLT-03 rows arrive as upstream `0x07` or `0x0B` and leave as algorithm `13` — they are promoted
  rows, so their `programming.*` belongs to another algorithm.
- **Measure before claiming.** Phase 148 measured and published the blast radius of three rejected
  keys; Phase 197 measured its 13-row diff rather than asserting 10. Every count in this document
  was measured against the live 746-row database or the 767-row filtered infoic population.

### Integration Points
- The override applies **after** decode and `classify()` but **before** the ceiling check, so every
  downstream derivation sees overridden values. Raising VPP to 12500 stays far below
  `RURP_VPP_CEILING_MV` (25000), so **no `support_status` moves**.
- `vpp_mv` **crosses the wire**; `vcc_mv` and `vdd_mv` do **not** (148-DB-DIFF § Evidence Ceiling,
  and `test_vcc_and_vpp_volts_never_cross_the_wire`). So the two VPP corrections are the only ones
  that can redden `tests/test_wire_dict_equivalence.py`.
- `tests/test_chip_database_field_inventory.py` guards the emitted field set at 14 fields. Adding a
  provenance marker field to overridden rows would trip it and is not in scope.
- `firestarter_app/tools/` sits **outside every CI gate** — no mypy, no `ruff check`, no
  `ruff format`. Coverage must land in `tests/`, which does run.
- Python floor is **3.11**. The devcontainer default is 3.12 and has masked app CI before — run the
  suite under 3.11.
- `tests/__snapshots__/test_characterization.ambr` pins display output; a `vpp_str` change on a
  corrected Fujitsu row may require a **single-line re-record**, not a blanket regeneration (the
  197-04 precedent, verified with `--numstat`).

### Measured facts this phase rests on
All measured 2026-09-18 during discussion, against the live database and the pinned `infoic.xml`.

- **767 rows** pass the generator's DIP-parallel filter; **746** reach the database.
- **vcc nibble** indices present: `0x0`×641, `0x1`×38, `0x2`×60, `0x4`×28. All mapped.
- **vdd nibble** indices present: `0x0`×450, `0x1`×20, `0x4`×170, `0x5`×103, **`0x6`×12, `0xD`×5,
  `0xE`×7** — the last three unmapped, silently 5000.
- The 28 `vcc_mv == 5500` rows split (5500, 3300)×16 and (5500, 5000)×12; the 12 are exactly the
  `0x6` rows, so their 5000 is a fallback.
- `0xD`→6000 hits `MBM27C1000P`, `MBM27C2000P`, `HN27C301AG`, `HN27C301G`, `M5M27C101K`.
  `0xE`→6250 hits NSC/Fairchild `NMC27C16*`, OKI `MSM27C1000/2000`, SGS-THOMSON `M27C1000`.
  All 12 are 1 Mbit-class UV EPROMs where 6.0/6.25 V program VCC is textbook.
- **28 rows carry VPP byte `0xF0`** (18 V, the TL866-II maximum) — including all eight NMOS
  2716/2732 rows and `MBM27128`, which needs 21 V.
- VPP low-byte distribution: `0x00`×453, `0x01`×113, `0x70`×136, `0x71`×9, `0xF0`×28, and a tail.
  The `0x01`/`0x71` pairs are the same index with a powerdown flag set.

</code_context>

<specifics>
## Specific Ideas

- The phrase to build § 9 around is upstream's own, in `database.c` immediately above the tables:
  *"These are not raw DAC output values, but rather indices into internal lookup tables defined in
  the firmware."* Everything this phase found follows from taking that sentence literally.
- The sharpest single piece of evidence for D-15 is arithmetic, not argument: the datasheet band is
  5.75–6.25 V and the TL866-II's two nearest rails are **5.5 and 6.5**. Neither is inside it. A
  field that cannot represent the datasheet value is not recording the datasheet value.
- Phase 197's real finding was that the override mechanism's first job was to reveal that two of the
  three things it was built to hold should not exist. Phase 198's is adjacent: the decoder was not
  wrong so much as **incomplete**, and the incompleteness was invisible because the fallback was a
  plausible number.
- On the 12 held rows: 1.8 V is not a worse answer than 5.0 V, it is a *more honest* one — but the
  decision is to keep the emitted value stable and make the exception legible, rather than ship a
  figure that would read as a regression to anyone running `firestarter info`.

</specifics>

<deferred>
## Deferred Ideas

- **The 167 index-`0x4` rows this phase does not reach.** `vdd 5500` where the datasheet band is
  5.75–6.25 and the programmer has no rail inside it. Fleet-scale, in the same shape as the 215-row
  pulse inventory and the 563-row `vpp 12000` group. One datasheet per row under Phase 197's D-02.
  Phase 200 will surface whatever these say.
- **`FUJITSU/MBM27C2001`** stays at `vpp 12000` with no vendored datasheet while its sibling
  `MBM27C2000P` carries 12500 — the family stays internally inconsistent by decision (D-08).
- **The 4 `adapter-required` rows inside the 28** (`28C04A`, `28C04AF`, `28C16A`, `28C16AF`) flip to
  `supported` if Phase 199 narrows the AT28C hardware-damage guard, and would then ship `vcc 5500`.
  Phase 199 inherits this via `.planning/notes/197-at28c-guard-evidence-for-phase-199.md`.
- **`chip_info` gates `can_adjust_vcc` / `can_adjust_vpp` upstream and the generator ignores it
  entirely.** Unexamined; may say which rows' voltages upstream itself treats as adjustable.
- **Making the `.get(idx, default)` fallbacks fail closed** — offered and declined (D-03). If ever
  wanted, it belongs with whatever phase is willing to absorb a build that stops on existing rows.
- **A build-time assertion on the `vdd < vcc` predicate** — reporting rather than correcting, so a
  29th row joining the group cannot arrive silently. Left to Claude's discretion this phase.
- **`VOLT-F1`** (REQUIREMENTS.md, Future) — the remaining families touching `VCC_VOLTAGES[0x04]`.
  D-15's general finding bears on whether it is ever worth opening.

### Reviewed Todos (not folded)

`todo.match-phase 198` returned 41 of 41 pending todos, scored on generic keyword overlap
(`phase`, `two`, `left`, `correct`) rather than subject. Reviewed and **not** folded — none is
about the voltage decode:

- `2026-08-27-strip-gsd-provenance-comments-from-source.md` (0.9) — already governed by CLAUDE.md's
  hard rule, which this phase obeys; not phase work.
- `2026-09-13-close-six-stale-claims-wr01-wr06.md` (0.9) — Phase 188 enforcement claims, unrelated.
- `new-host-old-firmware-0x05-page-size-skew.md` (0.7) — page size, not voltage.
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (0.6) — touches the
  same firmware guard D-10 measures, but it is a **firmware** change about skipping the check on
  reads. Out of scope here; closest relative is Phase 199.
- `pinout-address-width-and-we-pin-corrections.md` (0.6) — already folded by Phase 197 as a design
  constraint on the override file, not as work.
- `fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md` (0.2) — algorithm 13 promotion, which
  all 28 VOLT-03 rows undergo, but the todo is about SDP capability on FRAM parts.
- The remaining 34 are keyword noise.

</deferred>

---

*Phase: 198-the-two-voltage-nibbles*
*Context gathered: 2026-09-18*
