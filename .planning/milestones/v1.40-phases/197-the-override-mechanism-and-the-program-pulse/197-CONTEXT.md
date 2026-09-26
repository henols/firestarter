# Phase 197: The override mechanism and the program pulse - Context

**Gathered:** 2026-09-18
**Status:** Ready for planning

<domain>
## Phase Boundary

A datasheet value can correct an `infoic.xml` decode without a line of part-specific code in
`build_db.py`, and the first correction proves it on the program pulse gh#70 measured.

**In scope:** the override file and its loader in `firestarter_app/tools/`; removal of every
part-specific constant from `build_db.py`; the Fujitsu program-pulse corrections the in-repo
datasheets support; the test legs whose expectations the removals invalidate.

**Out of scope:** voltage nibble semantics (Phase 198), rail ceilings and the warn-on-shortfall
surface (Phase 199), `vdd_mv` reporting (Phase 200), the firmware blank-check region (Phase 201),
pinout correctness, and any new chip — `tools/extra_chips.json` keeps that job.

</domain>

<decisions>
## Implementation Decisions

### The override file contract

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

### Hardcode dispositions — all three leave `build_db.py`, only one moves into the file

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

### The pulse correction

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

### Requirement amendments this discussion forces

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

### Plan-time amendments — research measurement and one operator ruling (2026-09-18)

*Added during `/gsd-plan-phase 197`, after `197-RESEARCH.md` measured five of the decisions above
against live code, the pinned `infoic.xml` and a full simulated regeneration. These supersede the
clauses they name; the superseded wording stays above as the record of what was believed.*

- **D-15:** The AT28C hardware-damage guard stays, and D-07 becomes a name-list deletion only. Measured: deleting `_AT28C_DIP24_NAMES` flips **zero** rows to `supported`, because the guard at `build_db.py:469-492` already sets `adapter-required` on exactly those 9 rows via `pin_count == 24 and proto_id in (0x07, 0x08, 0x0B) and (flags & 0x10)` — the erasable bit, matching the name list with zero exceptions — and the name-list arm only overwrites its reason string. D-07's "9 rows flip to `supported`" is therefore unreachable without narrowing the guard, which D-07 does not authorise. **Operator ruling, asked and answered during planning: delete the name list now; route the guard narrowing to Phase 199.** Phase 197 still satisfies OVR-05 and success criterion 2 — no part-number literal survives in the generator — and the 9 rows keep `adapter-required` with the guard's own reason text. Phase 199 inherits the evidence that the guard's stated hazard does not materialise for these rows: they resolve to `DIP24_2816` (`rw-pin: [21]`, no `vpp-pin`), not the `DIP24_2716` its in-code comment names, so socket pin 21 is the write strobe and not the 12 V rail. — **Reversibility:** reversible — nothing ships differently; the deferred change is additive in Phase 199.

- **D-16:** The regeneration diff is **13 rows and zero `support_status` changes**, superseding D-13's "10 rows, 9 `support_status` flips". Measured by full simulated regeneration against the live pinned `infoic.xml`, 746 rows in and 746 out: 9 `unsupported_reason` string swaps (D-07, per D-15), `RAMTRON/FM1608` on two fields, and 3 `programming.pulse_duration_us` changes. The D-06 NMOS move and the D-09 derivation each contribute **zero** diff, exactly as claimed. This 13-row set is the acceptance evidence for OVR-05 as restated: exactly these rows and nothing else.

- **D-17:** FM1608 changes **two** fields, not one, superseding D-08's "changes nothing but a display string". `electrical.type` flips `FRAM` → `SRAM` **and** `electrical.vcc_mv` flips `3300` → `5000`, because the FRAM label was bypassing the SRAM single-rail rewrite at `build_db.py:700-705`. The decision to delete the relabel is unchanged; only its stated effect is corrected.

- **D-18:** The red-test list is the measured one, superseding D-14. Measured against a simulated post-change database under Python 3.11 — baseline `2024 passed`, post-change `5 failed, 2019 passed`. The five are `test_build_db_inclusion.py::test_fm1608_resolves_sram_std`, `test_build_db_inclusion.py::test_at28c16_named_arm_reason_mentions_adapter_doc`, `test_characterization.py::test_list` (snapshot), and **two in `tests/test_wire_dict_equivalence.py`** — which D-14 misses entirely and which need a new `tests/golden/wire_dict_expected_deltas_197.json` layer plus an `84 → 87` count bump, copying the existing 194 layer. All three legs D-14 names as needing rewriting stay **green** and must not be touched; `tests/test_sdp_honesty.py:59` is additionally a bare comment line, so rewriting it would add a `+#` line and trip the project's mandatory pre-commit check. Deleting a stale clause there is permitted; rewriting it is not.

- **D-19:** The pulse correction is **3 rows, not "up to 9"**, and `MBM27C4001` must get no entry. The three in-repo Fujitsu datasheets cover exactly three database rows: `FUJITSU/MBM27128` → **1000 µs** (Quick Pro `TPW = 1 ms ± 50 µs`; the conventional 50 ms single-shot is the wrong reading because the firmware runs a verify-per-pulse loop capped at 25 pulses with `overprogram_factor = 0`, which is the fast algorithm's shape), `FUJITSU/MBM27C1000P,MBM27C1000` → **500 µs**, and `FUJITSU/MBM27C1001` → **500 µs**. `FUJITSU/MBM27C4001`'s datasheet confirms the decoded 100 µs is already correct, so under D-04 an entry for it would be a no-op that **fails the build** — record it in the D-12 inventory instead. — **Reversibility:** reversible — each value is one override entry, and deleting the entry restores the decode.

- **D-20:** The override file is `firestarter_app/tools/datasheet_overrides.json`, keyed `MANUFACTURER/ALIAS`, each field carrying its datasheet citation and an explicit `was`/`is` pair so D-04's assertion against the live decode is mechanical. CONTEXT.md left the name, format and ordering to Claude's discretion; this fixes them, because phases 198, 199 and 200 all write entries into this file and D-01 already treats its public shape as costly to change. The name `database_overrides.json` is avoided — it is already claimed in `pyproject.toml` package-data.

- **D-21:** The `MBM27C1000` datasheet must be **vendored from the gh#70 attachment**, and the two untracked Fujitsu datasheets tracked, before any OVR-03 citation resolves. Measured: `datasheets/MBM27C1001.pdf` contains the string `27C1000` zero times and upstream gives the two parts different `voltages` and `variant`, so D-10's "evidence is already on disk; nothing new to source" is false for the one row gh#70 is about. `datasheets/MBM27128.pdf` and `datasheets/MBM27C4001.pdf` are present but **untracked**, so a citation to either would dangle for every other checkout.

### Claude's Discretion

- The override file's name, on-disk format and internal ordering (D-03 fixes its semantics, not its
  spelling). It sits beside `tools/extra_chips.json` per D-3 and must stay readable as a whole.
- Where the loader lives, and how it is covered given that `firestarter_app/tools/` sits outside
  every CI gate — no mypy, no `ruff check`, no `ruff format`.
- The exact wording of generator failure messages, subject to OVR-04's fail-closed requirement.
- Where the 216-row inventory file lands (D-12).

### Folded Todos

- **`derive-away-max-27c020-size-hardcode.md`** — folded as D-09. Its point 1 ("it is derivable, so
  it should not exist") is the surviving open item; points 2 and 3 were closed by v1.32 Phase 182-02,
  which moved the constant into `build_db.py` and deleted its fake firmware-parity test. Phase 197
  closes point 1 and the todo.
- **`pinout-address-width-and-we-pin-corrections.md`** — folded as a **downstream consumer only**,
  not as work. The 29 mis-pinouted chips (AM27C080 taking 13 V on A19, AT28C040 addressing 64 KB of
  512 KB) are precisely the class of datasheet correction the new file exists to carry, so the file's
  design must not preclude them. Fixing them is a different phase.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone intent and locked decisions
- `.planning/ROADMAP.md` § "v1.40 — Program-Parameter Fidelity" — milestone goal, the D-1…D-6
  activation decisions, phase ordering and dependencies.
- `.planning/REQUIREMENTS.md` — OVR-01…06 and PULSE-01…04 in full, plus the activation decision
  table. Note D-13 above: OVR-05 needs restating.

### The generator
- `firestarter_app/tools/build_db.py` — the decode loop. Load-bearing line references:
  `:87` `NMOS_TRUE_VPP_MV`, `:94` `RURP_VPP_CEILING_MV`, `:142` `_VCC_MARGIN_RAIL_MV`,
  `:148` `_PGM_ON_PIN31_MAX_SIZE`, `:241` the `DIP32_27C020`/`DIP32_STD` fork,
  `:339` `interpret_timing`, `:506` `_AT28C_DIP24_NAMES`, `:573` `_ETYPE_RELABEL`,
  `:591-600` the ceiling → `support_status` derivation, `:705` the `vcc_mv` rewrite,
  `:710` `chips.append`, `:716` the `extra_chips` merge, `:741` the `page_size` validation.
- `firestarter_app/tools/extra_chips.json` — the sibling file D-3 names. Its entries are FULLY
  SPECIFIED and bypass `classify()`; the override file is the opposite kind and must not be modelled
  on it.
- `firestarter_app/tools/DECODE-NOTES.md` — existing decode findings.
- `firestarter_app/firestarter/data/chip_database.json` — **GENERATED. Never hand-edit.**
- `firestarter_app/firestarter/data/pinouts.json` — `DIP24_2816` is fully defined there, which is
  what makes D-07's 9-vs-10 split indefensible.

### Host consumers of the fields this phase changes
- `firestarter_app/firestarter/chip_resolver.py:28` — guards generically on
  `support_status != "supported"`; it never names `adapter-required`, so D-07 needs **no host source
  change**.
- `firestarter_app/firestarter/database.py:368`, `:553-579` — `FLAG_CAN_ERASE` is set directly from
  `electrical.type`.
- `firestarter_app/firestarter/eprom_operations.py:2288` and
  `firestarter_app/firestarter/eprom_info.py:390` — the two sites that prove SRAM and FRAM are
  interchangeable (D-08).
- `firestarter_app/firestarter/sdp_capability.py:121` — `FRAM_TOKENS = {"FM28V020","MB85R256H"}`, a
  **second** hardcoded FRAM name list, in the host, covering two **algorithm 13** parts that share
  nothing with FM1608. Out of scope here; see deferred.

### Community reports this phase answers
- gh#70 — https://github.com/henols/firestarter/issues/70 (MBM27C1000 program pulse). PULSE-04
  requires the answer and the carrying version to be posted.

### Project rules that constrain execution
- `/workspaces/CLAUDE.md` § "Source code comments — hard rule" — **write no comments into product
  source**, and this is not overridable by a plan or a subagent instruction. `build_db.py` is dense
  with existing comments; deleting the three hardcodes will orphan surrounding prose, and the rule
  requires reading the remainder so every pronoun still has an antecedent. **Add nothing new.**
- `/workspaces/CLAUDE.md` § "Cross-repo obligations" — this phase is host-only; no firmware change.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`extra_chips.json` merge** (`build_db.py:716-737`) — an existing, tested precedent for reading a
  sibling JSON file and folding it into the generated database. Its *mechanism* is reusable; its
  *semantics* are the opposite of the override file's (fully-specified rows appended post-decode,
  versus partial field substitution pre-derivation).
- **`test_extra_chips_supplement.py`** — an existing test shape for a sibling-data-file feature.
- **Fail-closed precedent** — `interpret_timing` raising on an unparseable `pulse_delay`, and the
  `page_size` power-of-two check raising before the write, are the two models D-04 follows.

### Established Patterns
- **Alias parsing** — `{a.split("@")[0].strip() for a in name.split(",")}` appears at three separate
  sites (`:522`, `:574`, `:586`). D-01's key resolution needs this exactly once, and the three
  existing copies go away with their hardcodes.
- **Support-status derivation** — `support_status` is computed, never assigned from data. D-03
  preserves this; D-05 is what keeps it true.
- **`classify()` reassigns `proto_id`** — the original upstream protocol is captured as
  `_upstream_proto_id` before the call (`:562`). Any override touching algorithm-adjacent fields must
  respect that ordering.

### Integration Points
- The override applies **after** decode and `classify()` but **before** the ceiling check at `:591`,
  so every derivation downstream sees overridden values.
- `firestarter_app/tools/` is outside every CI gate — no mypy, no `ruff check`, no `ruff format`.
  Whatever lands there is ungated unless the plan puts coverage somewhere that runs.
- `tests/test_chip_database_field_inventory.py` guards the emitted field set. The 14 emitted fields
  are fixed; `datasheet`/`provenance`/`source`/`verification_*` appear on the 2 `extra_chips` rows
  only. Provenance for an overridden row therefore lives in the override file, not the database —
  adding a marker field would trip that test and is not in scope.
- Python floor is **3.11** (v1.37 Phase 186). The devcontainer's default 3.12 masks CI.

</code_context>

<specifics>
## Specific Ideas

- The operator's framing for D-05, verbatim: *"only decoded values can be overridden, and the things
  in the code must be solved in some better way and be discussed."* That sentence is why D-07 and
  D-08 are deletions rather than migrations, and it should govern any hardcode found later.
- On D-07, verbatim: *"No adapter shall be needed at all, but its only 2.2 and above that supports it
  by hardware, but that is not a real blocker, the other versions can do the same with a wire, but
  that's nothing to care about here."* The shield-revision distinction is explicitly **not** to be
  modelled in the database.
- Both remaining hardcodes turned out to be the same defect shape as the community reports
  themselves: a per-part name list standing in for a fleet-wide property. Phase 197's real finding is
  that the override mechanism's first job was to reveal that two of the three things it was meant to
  hold should not exist.

</specifics>

<deferred>
## Deferred Ideas

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

### Reviewed Todos (not folded)

None — both surfaced todos were folded (see Folded Todos above; the pinout one as a design
constraint only, not as work).

</deferred>

---

*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Context gathered: 2026-09-18*
