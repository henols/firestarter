# Phase 199: What the rails can actually deliver - Context

**Gathered:** 2026-09-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Measure what the RURP shield's high-voltage rails actually deliver at the socket, record the
generator's 25 V ceiling as the theoretical figure it is, classify the 30 rows asking 18 V or more
against what was measured, make the host route VPE as VPP by itself when the standard rail cannot
reach a part's required voltage, warn the operator with both numbers while still proceeding, and
answer gh#71.

**In scope:** one bench session on the Rev 2.0 shield measuring socket pin 1 on both VPP paths;
`tools/DECODE-NOTES.md` § 10 as the record; one datasheet-backed override entry
(`FUJITSU/MBM27128` `electrical.vpp_mv` 18000 → 21000); a new host-side policy module deciding the
shortfall and setting the already-shipped `FLAG_VPE_AS_VPP`; its warning on the `write` and `info`
paths; a test that reddens when the 30-row classification stops being true; the held gh#71 draft.

**Out of scope:** any firmware change — the mechanism this phase drives is already shipped
(`FLAG_VPE_AS_VPP = 0x10`, `eprom_hv_route_mask`, `eprom_check_vpp`'s window), and Phase 201 remains
the milestone's only firmware change; voltage-reading calibration (milestone D-5, 999.38 stays
filed); surfacing `vdd_mv` (Phase 200); narrowing the AT28C DIP24 hardware-damage guard (ruled OUT
of this phase, see Deferred); Rev 2.2 and Modified Rev 0 measurements; adding chips.

</domain>

<decisions>
## Implementation Decisions

### The ceiling stays; its status moves to prose

- **D-01:** **`RURP_VPP_CEILING_MV` stays at 25000 and keeps its job as the refusal gate.** No row's
  `support_status` moves in this phase, and nothing starts refusing. RAIL-02 explicitly permits
  "kept with its status recorded as theoretical", and that is the branch taken. The alternative —
  replacing it with a measured figure — was offered and **declined**: a measured VPP maximum near
  16–18 V would flip all 30 rows to `vpp-exceeds-max`, and `chip_resolver.py` turns a non-`supported`
  row into a `ChipNotImplementedError`, which is the silent refusal milestone **D-4** forbids.
  — **Reversibility:** reversible — nothing in the generator or the emitted database changes.

- **D-02:** **No new constant in the generator.** A second "measured deliverable maximum" constant
  beside the ceiling was offered and declined. Whatever threshold the host needs is a host-side
  figure, not a generator one.

- **D-03:** **The theoretical status and the measured figures are recorded in
  `firestarter_app/tools/DECODE-NOTES.md` § 10**, following § 8 (PULSE-01) and § 9 (VOLT-01).
  **This is not a stylistic choice.** `build_db.py` already carries a `# RURP boost regulator
  theoretical ceiling…` comment directly above the constant, and editing it emits a `+`-prefixed
  `#` line, which trips CLAUDE.md's own pre-commit comment check. The label **cannot** go in the
  source. § 10 carries: the 25 V figure's theoretical status, the measured per-rail figures with
  their method, the ADC error measured alongside them, and the 30-row classification table.

### What the bench measures

- **D-04:** **Rev 2.0 only.** Rev 2.2 and Modified Rev 0 are named in § 10 as unmeasured, not
  assumed. gh#71's reporter was on a Rev 2.0-class board, so this is the revision the report is
  about, and the v1.34 close already carries "every result is Rev 2.0 only" as a disclosed gap.
  Modified Rev 0 could not contribute an ADC figure in any case: `hw_read_voltage` returns
  `MSG_ERR_REV0_VPP_RD` and `eprom_check_vpp` returns early with `MSG_WARN_REV0_VPP_UNSUPPORTED`.

- **D-05:** **Held rail at the socket, operator DMM, plus exactly one paired ADC read.** Pot at
  maximum, chip out, rail routed and held, operator takes the multimeter reading at socket pin 1;
  Claude then takes one `firestarter vpp` / `vpe` reading at the same pot setting. The pair is what
  gives RAIL-01's "known error" figure as a **measurement of this rig** rather than a citation of
  999.38's older ~+7.5 % (6.8–8.3 %) number. The monitors alone were offered and declined — they
  assert no socket-routing bit and so do not satisfy "at the socket".
  **The naive `firestarter dev reg 0 0 <CTRL> -f` hold does not work**: pyserial's close de-asserts
  DTR, resets the board and drops the rail before the operator can read it. Use the
  `hold_rail.py` approach (`.planning/milestones/v1.18-artifacts/bench/hold_rail.py`), and note no
  `firestarter` command may run alongside it.

- **D-06:** **Two configurations, both at socket pin 1:** drop-resistor → pin 1 (this IS the
  threshold figure), and direct VPE → pin 1 (what VPE-as-VPP will deliver to the 10 stranded
  28-pin rows). The third configuration — direct VPE → pin 21, what the 20 algorithm-`0x0B` rows
  already receive — was offered and **declined**; those rows are classified against the pin-1 VPE
  figure, **and § 10 must state that this is an approximation across a different routing bit**
  (`CTRL_VPE_ENABLE` vs `CTRL_VPP_P1_ENABLE` are different physical destinations).

- **D-07:** **The measurement beats the provisional 18 V.** The operator named 18 V during
  discussion; if the DMM at pin 1 on the drop path disagrees, **the measured figure is what ships**.
  — **Reversibility:** costly — this makes the bench session load-bearing rather than confirmatory,
  and it imposes the sequencing constraint in D-08.

- **D-08:** **Sequencing, which the planner must honour:** the bench plan is a **hard predecessor**
  of the host-threshold plan, and **no plan may hardcode 18000 before the measurement exists.**
  A plan written against 18000 up front would make D-07 unobservable.

### RAIL-04 — the routing decision is: route it

- **D-09:** **The host sets `FLAG_VPE_AS_VPP` itself when the part's required `vpp_mv` exceeds the
  measured drop-path maximum.** Purely derived from two numbers the host already has. **No database
  field** (offered and declined — it would be a 15th emitted field against
  `tests/test_chip_database_field_inventory.py`'s guard, and it would encode a *shield* property
  into a *chip* record, the exact category error Phase 198's D-15 finding untangled). **No generator
  change**, so milestone **D-1** stays intact.
  — **Reversibility:** reversible — the flag and its whole downstream path already ship.

- **D-10:** **The mechanism is already built end-to-end and this phase adds no firmware.** Measured,
  not assumed: `FLAG_VPE_AS_VPP = 0x10` (`firestarter_fw/include/firestarter.h`;
  `firestarter_app/firestarter/constants.py:112`) → `build_flags(vpe_as_vpp=…)` →
  `--vpe-as-vpp` on `write` (`cli_handlers.py:588`) → wire → `eprom_hv_route_mask()`, which checks
  the flag **first** and returns `CTRL_VPP_REGULATOR_ENABLE` (the undropped rail). `eprom_check_vpp`
  calls the **same** `eprom_hv_route_mask(handle)` before reading, so the acceptance window already
  follows whichever rail is routed.

- **D-11:** **`write` only.** Not asked — forced by the code. `eprom_internal_erase` already asserts
  `CTRL_VPP_REGULATOR_ENABLE` with no drop bit, so there is nothing to route there, and
  `--vpe-as-vpp` exists on no other command. `--vpe-as-vpp` survives as a manual override for
  anything the rule does not catch.

- **D-12:** **A posture change, recorded rather than slipped in.** `eprom_hv_route_mask`'s own
  documentation calls `FLAG_VPE_AS_VPP` *"a pure human override (25V NMOS parts, the manual-pot
  workflow) set by no database entry"*. After D-09 it is also set by a host rule. The flag's
  resolution order is unchanged — it still wins over the table with no table read — but that comment
  no longer describes the only caller. **Do not edit it** (no-comments rule); state the change in
  § 10.

### RAIL-03 — the warning

- **D-13:** **Its own policy module, in the `jp5_gate.py` shape.** Whole input is the wire dict, the
  operation name and the threshold — no I/O, no serial, no environment reads — so the policy is
  testable without a board and `eprom_operations.py` / `cli_handlers.py` stay free of the reasoning.
  `jp5_gate.py`, `page_size_gate.py` and `flash4_erase_gate.py` are the three precedents.
  **The one difference from all three: this module never refuses.** It warns and returns a flag.

- **D-14:** **Emitted on `write` and `info`.** `write` is the path RAIL-03 names; `info` is where an
  operator checks a part before committing, and it already emits `Support status:` / `Reason:` as
  `logger.warning` lines (`eprom_info.py:237-244`). This also gives Phase 200's VCC-01 the surface
  it needs without adding one. The `dev test` diagnostic report was offered as a third surface and
  **declined** — it has a guarded field set and a schema version that would move.

- **D-15:** **The host says nothing about the pot.** One pot sets both rails, so auto-routing VPE for
  a 21 V part still needs the pot set so VPE lands near 21 V — otherwise the firmware's high guard
  hard-errors. Naming a pot target in the host message was offered and **declined**: the host advises
  nothing, the firmware's existing window adjudicates (`rail > target + 500` → `MSG_ERR_VPP_HIGH`
  unless `FLAG_FORCE`; `rail < target × 95/100` → `MSG_WARN_VPP_LOW`). This follows Phase 198's
  **D-10**, which deliberately declined to mirror a firmware constant onto the host.
  **Consequence to accept, not to solve:** the operator's first attempt on a newly-routed part may
  hard-error on the pot setting, and the firmware message is what tells them.

- **D-16:** **One wording for every shortfall.** Required voltage, deliverable voltage, routing VPE,
  proceeding. It does **not** distinguish "VPE rescues this" from "nothing on this shield rescues
  this" — the eight rows at 21–25 V get the same message as the ten at 18 V. Offered and declined:
  naming both rails, and marking the unreachable eight in the classification table. RAIL-03 asks only
  that both voltages be named. **VPE is still routed and the operation still proceeds** in every
  case, per D-4.

### RAIL-02 — what changes in the database, and how the classification is proved

- **D-17:** **Exactly one row's value moves: `FUJITSU/MBM27128` gains
  `electrical.vpp_mv` 18000 → 21000.** `datasheets/MBM27128.pdf` is already git-tracked and already
  cited in that part's existing override entry for `pulse_duration_us` and `vdd_mv`, so this is a
  field added to an entry that exists. Every other row of the 30 is classified in § 10 with a reason
  and left unchanged. Extending the NMOS class argument to the other capped rows was offered and
  **declined** — it is class inference without a datasheet per row, the practice Phase 197's D-02
  exists to prevent, and Phase 198's D-08 already refused it once for `MBM27C2001`.

- **D-18:** **The classification is a § 10 table *plus* a test that can fail.** The test asserts the
  live generated database still produces exactly those 30 rows, at those voltages, on those two
  `vpp_path` values. A 31st row arriving from upstream, or a row changing rails, reddens rather than
  drifting silently. A written table alone, and a regenerating script under
  `firestarter_app/tools/`, were both offered and declined — `tools/` sits outside every CI gate
  (no mypy, no `ruff check`, no `ruff format`), so a script there is unguarded and still would not
  fail when the answer changes.

### RAIL-05 — gh#71

- **D-19:** **The draft is written, held, and claims corrections and the routing answer only.**
  Carried forward from Phase 198's D-17 and 197-08's operator ruling without re-asking: nothing is
  pushed, the branch has no upstream, so no version or sha a reader could look up exists yet. The
  draft states `MBM27128`'s 18000 → 21000 from the vendored datasheet, credits `dim20`, and
  **answers their VPE-as-VPP proposal directly** — it is now automatic above the measured threshold.
  It says **nothing new about causation**: the maintainer's 2026-09-16 comment already argues the
  last-256-byte boundary rather than VPP, across three part sizes, and this phase does not advance
  that. Everything sits under an explicit *"this does not close this report"* heading.
  **RAIL-05 is left Pending**, exactly as PULSE-04 and VOLT-04 are.

- **D-20:** **Added to the one consolidated held-pending list.** Phase 198's D-18 established that
  `197-GH70-ANSWER.md` § "Held-pending deferral" is the single list whoever closes v1.40 reads.
  gh#71 joins gh#70 and gh#66 there.

### Carried forward from Phases 197 and 198 — locked, do not re-litigate

- Override key is **`MANUFACTURER/ALIAS`**; **one entry targets exactly one row** (197 D-01, D-02).
- An override **substitutes the decoded input**, before `classify()`'s downstream derivations
  (197 D-03). `support_status` stays derived and is never written by hand.
- Every entry carries `was`/`is` and a datasheet path or the literal `UNSOURCED`; the recorded `was`
  is asserted against the live decode and a mismatch fails the build (197 D-04, D-20).
- The generator **fails closed** on an unknown key, unknown field, duplicate target, unsorted file,
  per-field type mismatch, and a no-op entry (OVR-04).
- **Decode tables stay in code** — they are the decoder, not a correction (milestone D-2).
- **Nothing part-specific is hardcoded in the generator** (milestone D-1).
- Decode findings land in `tools/DECODE-NOTES.md` as a numbered section (§ 8 PULSE-01, § 9 VOLT-01).
- Inventory and disposition records follow the `177-READBACK-INVENTORY.md` precedent: reproducible
  method first, every row disposed, a named honesty limit.
- `chip_database.json` is **GENERATED**. Never hand-edit.
- **No comments in product source**, for any reason (CLAUDE.md, hard rule) — and see D-03, where
  that rule actively determines where this phase's record goes.

### Claude's Discretion

- The exact wording of the shortfall message, subject to D-16 (one shape) and D-15 (says nothing
  about the pot).
- The policy module's name, and whether the threshold reaches it as a module constant or a
  parameter.
- The exact control-register composites held for each of D-06's two configurations, and whether
  `hold_rail.py` is copied into this phase's bench directory or invoked from the v1.18 artifacts
  path.
- Whether the D-18 test lives in a new file or extends an existing one, and whether it is one test
  over all 30 rows or split by `vpp_path`.
- Whether § 10's 30-row table is ordered by voltage, by path, or by manufacturer.
- Whether `197-REGEN-DIFF.md`'s shape is reused for this phase's one-row regeneration diff — it
  almost certainly should be, and note `vpp_mv` **crosses the wire**, so the `MBM27128` correction
  will redden `tests/test_wire_dict_equivalence.py` and need a `wire_dict_expected_deltas_199.json`
  layer the way 197 and 198 both did. Measure it rather than assuming.

### Folded Todos

None folded. See Reviewed Todos below.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone intent and locked decisions
- `.planning/ROADMAP.md` § "v1.40 — Program-Parameter Fidelity" — the milestone goal, the D-1…D-6
  activation decisions and the phase table. Phase 199's own goal, dependencies and five success
  criteria sit under `### Phase 199: What the rails can actually deliver`.
- `.planning/REQUIREMENTS.md` — RAIL-01…05 in full, plus the activation decision table. **D-4** and
  **D-5** are the two that shape every decision above: warn-and-attempt, and calibration out of
  scope *because of* warn-and-attempt.
- `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-CONTEXT.md` — the override
  file's contract, D-01…D-21.
- `.planning/phases/198-the-two-voltage-nibbles/198-CONTEXT.md` — D-10 (do not mirror a firmware
  constant onto the host), D-15 (voltages are *programmer rail indices*, not chip requirements — the
  framing this phase's warning inherits), D-16 (`0xF1`=25 V / `0xF2`=21 V exist in the table and no
  row reaches them), D-17/D-18 (the held-draft discipline this phase's D-19/D-20 follow).

### Inherited evidence
- `.planning/notes/197-at28c-guard-evidence-for-phase-199.md` — written *for* this phase. The guard
  narrowing it routes here is **ruled out of Phase 199** (see Deferred); this note becomes that
  backlog item's brief. Its § "What Phase 199 must decide" is superseded by that ruling.
- `.planning/milestones/v1.34-artifacts/PROCEDURE.md` § "Standing bench rules" — all nine bind this
  phase's bench session. Rules 3, 4, 5, 6 and 7 are the load-bearing ones here: DMM/pot/chip
  handling are operator-only; Claude states a pot target and takes **exactly one** confirming read,
  never a monitor loop; the monitors do not route to the socket; shield identity is by silkscreen,
  never by `hw_revision`; and **this procedure must not run under `--auto` / `--chain`**.
- `.planning/milestones/v1.18-artifacts/bench/hold_rail.py` — the working held-rail script. See D-05
  for why `dev reg -f` alone is not sufficient.
- `.planning/ROADMAP.md` § "Phase 999.38" — the ~+7.5 % (6.8–8.3 %) ratiometric VPP ADC error, and
  its standing operational rule: **set any pot target from a multimeter reading, never from the
  firmware's own `vpp` figure.**

### The generator and its record
- `firestarter_app/tools/build_db.py` — cited by content, not line number. Load-bearing sites:
  `RURP_VPP_CEILING_MV = 25000` and the strict `>` comparison above `chip_entry` (six rows sit
  exactly on 25000 and stay `supported` because of it); the `VPP_MV` table including `0xF0`=18000,
  `0xF1`=25000, `0xF2`=21000; `load_datasheet_overrides` / `apply_datasheet_override`.
- `firestarter_app/tools/DECODE-NOTES.md` — § 8 and § 9 are the template for § 10; § 6 "Honest gaps"
  is the template for its named limits.
- `firestarter_app/tools/datasheet_overrides.json` — 22 entries today. `FUJITSU/MBM27128` already
  exists (`pulse_duration_us` 200 → 1000, `vdd_mv` 5500 → 6000, cited to `datasheets/MBM27128.pdf`);
  D-17 adds `electrical.vpp_mv` to it. The six `UNSOURCED` NMOS VPP entries
  (`INTEL/M2716`, `INTEL/M2732`, `SGS-THOMSON/M2716`, `ST/M2716` → 25000;
  `SGS-THOMSON/M2732A`, `ST/M2732A` → 21000) are six of the eight high rows.
- `firestarter_app/tools/extra_chips.json` — `TEXAS INSTRUMENTS/2516` and `/2532` carry a hardcoded
  `vpp_mv: 25000`, are `UNVERIFIED` and **not write-graduated**. They are the other two high rows and
  come from neither the decode nor the override file.
- `firestarter_app/firestarter/data/chip_database.json` — **GENERATED. Never hand-edit.**

### The host surfaces this phase touches
- `firestarter_app/firestarter/jp5_gate.py` — the shape D-13 copies: module docstring stating the
  policy, pure functions over the wire dict, the operation name as the other input, no I/O.
  **Its outcome is a refusal; this phase's is a warning.**
- `firestarter_app/firestarter/page_size_gate.py`, `firestarter_app/firestarter/flash4_erase_gate.py`
  — the other two instances of the same pattern.
- `firestarter_app/firestarter/eprom_operations.py` — `build_flags(vpe_as_vpp=…)` sets
  `FLAG_VPE_AS_VPP`; this is where D-09's derived flag has to land.
- `firestarter_app/firestarter/cli_handlers.py` — `--vpe-as-vpp` is declared on `write`; the
  `vpe_as_vpp` parameter threads through `_build_op_flags` and the write handler.
- `firestarter_app/firestarter/eprom_info.py` — the `Support status:` / `Reason:` `logger.warning`
  block is the `info` surface D-14 adds to.
- `firestarter_app/firestarter/chip_resolver.py` — raises `ChipNotImplementedError` for any
  `support_status != "supported"`. **This is why D-01 leaves the ceiling alone.**
- `firestarter_app/firestarter/constants.py` — `FLAG_VPE_AS_VPP = 0x10`. Note the file's own warning
  that `CTRL_VPP_VPE_DROP_ENABLE` is **also** `0x100` and is a different thing with its own parity
  leg.
- `firestarter_app/firestarter/diagnostic_report.py` — `vpp_before_mv` / `vpe_before_mv` and
  `_RAIL_READING_DISCLOSURE` (*"vpp/vpe readings measure the regulator rail only — they do not show
  whether the eprom socket is connected"*). **Not** a surface this phase writes to (D-14), but the
  disclosure sentence is the honesty model § 10 should match.

### The firmware this phase drives without changing
- `firestarter_fw/src/proms/eprom_params.cpp` — the protocol-keyed table that assigns
  `VPP_PATH_DROP_RESISTOR` to `0x07` and `0x08` and `VPP_PATH_DIRECT_VPE` to `0x0B`. **This table is
  what splits the 30 rows 10 / 20.**
- `firestarter_fw/src/proms/eprom.cpp` — `eprom_hv_route_mask()` and its documented resolution order
  (flag first, then `row == NULL` fail-closed, then the table); `eprom_check_vpp()`, which routes via
  the same call *then* reads *then* applies the ±window; `eprom_internal_erase()`, already undropped.
- `firestarter_fw/src/proms/memory.cpp` — `mem_util_calculate_top_address_register`'s preserve mask,
  and the comment establishing that `CTRL_VPP_VPE_DROP_ENABLE` selects a **level**, not a route.
- `firestarter_fw/src/hardware_operations.cpp` — `hw_read_voltage`: `CMD_READ_VPP` sets
  `REGULATOR | DROP`, `CMD_READ_VPE` sets `REGULATOR` alone, **neither asserts a socket-routing bit**,
  and `REVISION_0` returns `MSG_ERR_REV0_VPP_RD` before either.
- `firestarter_fw/include/firestarter.h` — `FLAG_VPE_AS_VPP 0x10`.
- `firestarter_app/firestarter/data/pinouts.json` — `DIP28_2764` has `vpp-pin: [1]`; `DIP24_2716` and
  `DIP24_2532` have `vpp-pin: [21]`. This is why D-06's two configurations are both on pin 1 and why
  the pin-21 rows are an approximation.

### The community report this phase answers
- gh#71 — https://github.com/henols/firestarter/issues/71 (`[dev test] MBM27128 — FAIL`). **OPEN**,
  labelled `cause:firmware` and `cause:database`. `dim20`'s 2026-09-12 comment attaches the Fujitsu
  datasheet (21.0 V ± 0.5 V), reports `vpp_before_mv: 17800` / `vpe_before_mv: 22700`, and
  **explicitly proposes using VPE as VPP** — the proposal D-09 implements. The maintainer's
  2026-09-16 cross-check publishes the 21 V and 1 ms mismatches and the `0xF0`-is-a-cap explanation,
  and the 2026-09-16 follow-up argues the **last-256-byte boundary** across three part sizes is the
  likelier cause and keeps the issue open on that basis. **D-19 constrains what the draft may claim.**
- `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md`
  § "Held-pending deferral" — the single list D-20 adds gh#71 to. **Whoever closes v1.40 must read
  it.**

### Project rules that constrain execution
- `/workspaces/CLAUDE.md` § "Source code comments — hard rule" — **write no comments into product
  source**, not overridable by a plan, task, skill or subagent instruction. This rule **decides D-03
  and D-12**, it is not merely a constraint on them. Run the staged-diff check before every commit.
- `/workspaces/CLAUDE.md` § "Cross-repo obligations" — this phase is **host-only**. D-10 is the
  evidence that no firmware change is needed, and D-15 declines to mirror a firmware constant.
- `/workspaces/CLAUDE.md` § "Milestone close and branch protection" — a push to `beta` in
  `firestarter_app` **publishes to PyPI**. Both sub-repos are already on
  `v1.40-program-parameter-fidelity`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`FLAG_VPE_AS_VPP` end-to-end** — the single largest finding of this discussion. The routing
  mechanism RAIL-04 asks about is **already shipped on both sides**, from the CLI flag to
  `eprom_hv_route_mask` to the acceptance window that follows the routed rail. The phase adds a
  decision rule in front of it, not a mechanism.
- **`jp5_gate.py` / `page_size_gate.py` / `flash4_erase_gate.py`** — three instances of the same
  policy-module pattern D-13 copies, with a settled testing style that needs no board.
- **`eprom_info.py`'s `Support status:` / `Reason:` warning block** — the `info` surface already
  emits operator-facing warnings through `logger.warning`; D-14 adds to it rather than inventing one.
- **`diagnostic_report.py`'s `_RAIL_READING_DISCLOSURE`** — an existing, single-sourced sentence that
  states what a rail reading does *not* prove. The model for § 10's honesty limit.
- **`.planning/milestones/v1.18-artifacts/bench/hold_rail.py`** — a working held-rail script for the
  DMM window, and the reason `dev reg -f` alone is not enough.
- **`197-REGEN-DIFF.md` and `tests/golden/wire_dict_expected_deltas_197.json`** — the shape for this
  phase's one-row regeneration diff and, almost certainly, its delta layer.
- **`.planning/notes/197-at28c-guard-evidence-for-phase-199.md`** — the disposition-record format
  (reproducible method, every row disposed, named honesty limit) that § 10's 30-row table follows.

### Established Patterns
- **Decode tables and constants carry `[VERIFIED: … @ sha]` provenance markers.** Anything § 10
  claims about the 25 V figure should name what it is and is not sourced from.
- **`support_status` is computed, never assigned.** Nothing in this phase writes it, and D-01 keeps
  it that way.
- **Measure before claiming.** Every count in this document was measured against the live 746-row
  database or read out of the two repos during discussion, not inferred.
- **A phase that finds a mechanism already exists says so and does not rebuild it.** Phase 197's
  finding was that two of the three things the override file was built to hold should not exist;
  this phase's adjacent finding is that the routing mechanism RAIL-04 asks for was already there,
  reachable only by an operator who knew the flag's name.

### Integration Points
- The override applies **after** decode and `classify()` but **before** the ceiling check, so
  `MBM27128`'s 21000 is what the ceiling compares. 21000 < 25000, so **no `support_status` moves** —
  D-01 holds even with D-17 applied.
- `vpp_mv` **crosses the wire**; `vcc_mv` and `vdd_mv` do not. The `MBM27128` correction is therefore
  wire-visible and will redden `tests/test_wire_dict_equivalence.py`.
- `tests/test_chip_database_field_inventory.py` guards the emitted field set at **14 fields** —
  the reason D-09 refused a per-part routing field.
- `tests/test_build_db_inclusion.py` asserts against `build_db.RURP_VPP_CEILING_MV` in three places,
  including a synthetic row proving the ceiling reason string. D-01 leaves all three green.
- `firestarter_app/tools/` sits **outside every CI gate** — no mypy, no `ruff check`, no
  `ruff format`. Coverage must land in `tests/`, which does run.
- Python floor is **3.11**. The devcontainer default is 3.12 and has masked app CI before.
- `tests/__snapshots__/test_characterization.ambr` pins display output; a `vpp_str` change on
  `MBM27128` may need a **single-line re-record** verified with `--numstat`, not a blanket
  regeneration (the 197-04 precedent).
- Both sub-repos are on `v1.40-program-parameter-fidelity`; the gitlink advances per phase (v1.36
  convention).

### Measured facts this phase rests on
All measured 2026-09-18 during discussion, against the live 746-row database and both repos.

- **30 rows carry `vpp_mv >= 18000`**: 22 at 18000, 2 at 21000, 6 at 25000. **Every one is
  `supported`.**
- **They split 10 / 20 by VPP path**, from `eprom_params.cpp`'s protocol-keyed table:
  **10 rows are algorithm `0x07` (28-pin) on `VPP_PATH_DROP_RESISTOR`, all at exactly 18000** —
  `TI/TMS2764`, `NEC/UPD2764`, `MITSUBISHI/M5M27C128`, `INTEL/2764`, `INTEL/27128`,
  `HITACHI/HN27C64G`, `HITACHI/HN27C64FP`, `FUJITSU/MBM27C64`, `FUJITSU/MBM27C128P`, and gh#71's
  **`FUJITSU/MBM27128`**. The other **20 are algorithm `0x0B` (24-pin) and already run on
  `VPP_PATH_DIRECT_VPE`**, and they hold all eight of the 21000/25000 rows.
- **Provenance of the eight high rows:** six from Phase 197's `UNSOURCED` NMOS override entries, two
  (`TEXAS INSTRUMENTS/2516`, `/2532`) hardcoded in `extra_chips.json`, `UNVERIFIED` and not
  write-graduated. **None of the eight comes from an infoic decode** — no filtered row carries VPP
  low byte `0xF1` or `0xF2` (Phase 198 D-16).
- **The ceiling compare is strict** (`_d_vpp_mv > RURP_VPP_CEILING_MV`), so the six rows sitting
  exactly on 25000 stay `supported`.
- **gh#71's 17.8 V and 22.7 V are firmware ADC readings** on a Rev 2.0-class board, and 999.38
  measured that ADC ~**+7.5 %** high (6.8–8.3 %). The real rails were nearer **16.6 V and 21.1 V**.
- **The pot is the only setpoint**, and the drop resistor is what makes VPP ≈ 17.8 V while VPE
  ≈ 22.7 V at the same setting. There is no firmware-settable VPP target.
- **`eprom_check_vpp` skips entirely on Rev 0** (`MSG_WARN_REV0_VPP_UNSUPPORTED`, response code
  warning, early return), and `hw_read_voltage` refuses on Rev 0 (`MSG_ERR_REV0_VPP_RD`).
- **The three routing bits go to three different socket destinations**: `CTRL_VPP_P1_ENABLE` → pin 1
  (28-pin VPP), `CTRL_VPE_ENABLE` → the non-P1 destination (pin 21 for 24-pin parts),
  `CTRL_VPP_A9_ENABLE` → the chip-ID route. `using_p1_as_vpp()` is what swaps the first two.

</code_context>

<specifics>
## Specific Ideas

- The operator's own framing of the mechanism, verbatim: *"a defalt generic constant of 18v, and then
  vpe must be used as vpp and read and bloced if its to high the sam way the vpp is dealt with"*.
  Every one of those three clauses turned out to describe something that already exists in firmware
  except the first — the threshold — and the trigger, which is what this phase builds.
- 18 V is not an arbitrary number: it is `VPP_MV[0xF0]`, the top of upstream's own VPP scale, and
  every capped row is capped *at* it. That is the argument for keeping it if the bench comes close —
  though D-07 says the measurement wins outright if it does not.
- The phase's shape, stated plainly for the record: **a bench session, one JSON field, one new host
  module, one markdown section, one test, one held draft.** Anything larger than that is scope
  growth, not thoroughness.
- The honest summary of RAIL-04: the answer is "route it", and the reason it is cheap is that someone
  already built it and only an operator who knew the flag's name could reach it.

</specifics>

<deferred>
## Deferred Ideas

- **Narrowing the AT28C DIP24 hardware-damage guard.** Routed here by the Phase 197 operator ruling,
  but no RAIL requirement covers it, and **the operator ruled it OUT of Phase 199 during this
  discussion.** It becomes its own backlog item, with
  `.planning/notes/197-at28c-guard-evidence-for-phase-199.md` as its brief — that note already holds
  the reproducible method, the 19-row table, the operator's verbatim framing, the measured finding
  that the guard's stated hazard does not materialise on the pinout these rows actually resolve to,
  and the three test legs that redden together the moment it is narrowed
  (`tests/test_sdp_capability.py`, `test_chip_resolver.py::test_resolve_chip_adapter_required_raises_not_implemented`,
  `test_build_db_inclusion.py::TestUnsupportedReasonStrings::test_at28c16_named_arm_reason_mentions_adapter_doc`).
  Its own honesty limit stands: **no AT28C part has ever been written, read or erased on any shield
  revision.** Phase 198 noted that four `adapter-required` rows inside its 28-row group flip to
  `supported` if this is ever done.
- **Rev 2.2 and Modified Rev 0 rail measurements** (D-04). Named unmeasured rather than assumed.
  Overlaps backlog **999.42**, the unfinished v1.34 sweep.
- **The direct-VPE → pin 21 configuration** (D-06). The 20 algorithm-`0x0B` rows are classified
  against a pin-1 figure taken through a different routing bit.
- **The two TI rows at a hardcoded `vpp_mv: 25000`** in `extra_chips.json` — `UNVERIFIED`, not
  write-graduated, and reachable by neither rail at pot maximum. They get D-16's generic warning like
  everything else; whether a non-upstream supplement should be able to assert a voltage no shield can
  deliver is a separate question.
- **Naming the pot target in the host message** (D-15, declined). If ever wanted, it belongs with
  whatever phase is willing to mirror the firmware's ±window constant onto the host — which Phase 198
  D-10 declined for the same reason.
- **A distinct wording for "no rail reaches this part"** (D-16, declined).
- **The `dev test` diagnostic report as a third warning surface** (D-14, declined) — it would put the
  shortfall into community issues automatically, which is exactly how gh#71 was diagnosed by hand.
  Costs a schema version bump.
- **Restoring the pot to a working setting before Phase 201's bench work**, and whether Phase 79's
  "≥25 V at pot maximum is a hard pre-gate" still stands. Operational; belongs in § 10's method or in
  the bench plan, not in a decision.
- **Whether `--vpe-as-vpp` should stay a manual override at all** once D-09's rule exists.

### Reviewed Todos (not folded)

`todo.match-phase 199` returned 39 of 40 pending todos, scored on generic keyword overlap
(`phase`, `firestarter`, `app`, `operator`) rather than subject — the same pattern Phase 198 recorded.
Reviewed and **not** folded:

- `2026-08-31-jp4-third-position-vpp-destination-pin.md` (0.6) — **the closest real relative.** Asks
  which pin JP4's third position routes VPP to on Rev 2.2 / Rev 2.3, and the operator is the source.
  Genuinely adjacent to D-06's routing-destination question, but it is about **JP4 and pin
  destinations on Rev 2.2**, and D-04 measures **Rev 2.0** only. Folding it would pull an unmeasured
  revision into a phase that deliberately excluded it. Note also that Rev 2.2 carries a **JP8 `VPE`**
  jumper absent from `ic_layout.py`'s renderer entirely.
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (0.6) — touches
  `eprom_check_vpp`, the exact function D-10 rests on. **Firmware**, and this phase is host-only;
  Phase 201 is the milestone's firmware slot.
- `2026-08-30-write-init-blank-check-is-whole-device.md` (0.6) — this is Phase 201's subject
  (BLANK-01…03 / backlog 999.44), not this phase's.
- `fix-jp4-labels-and-rev2-revision-block.md` (0.6) — jumper display rendering, not rails.
- `2026-08-27-strip-gsd-provenance-comments-from-source.md` (0.9) — already governed by CLAUDE.md's
  hard rule, which this phase obeys; not phase work.
- `2026-09-16-reject-negative-write-start-address.md`, `2026-09-13-close-six-stale-claims-wr01-wr06.md`,
  `new-host-old-firmware-0x05-page-size-skew.md`, `2026-08-30-remove-cmd-verify-from-firmware-compare-in-app.md`
  (0.9 each) — high scores purely from the words `phase`, `firestarter` and `app`. None is about
  voltage or rails.
- The remaining 30 are keyword noise.

</deferred>

---

*Phase: 199-what-the-rails-can-actually-deliver*
*Context gathered: 2026-09-18*
