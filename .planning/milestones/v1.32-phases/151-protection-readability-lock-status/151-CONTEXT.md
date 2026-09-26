# Phase 151: Protection Readability — `lock-status` - Context

**Gathered:** 2026-08-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Three deliverables, and nothing else:

1. **A committed, hand-curated family-level protection table** recording protection *mechanism*, *readability* and *permanence*, each row cited to `firestarter_app/doc/lockable-proms.md` and its datasheet source (LOCK-01).
2. **`dev lock-status <chip>`** — a command that either reports a chip's real protection state read from silicon, or refuses with a named, actionable reason. Never a guess, never a fabricated value, and never wording that reads as a lock-state guarantee where none exists (LOCK-02, LOCK-03, LOCK-04).
3. **`protect_on_after` (and its sibling `protect_off_before`) documented once** as advisory upstream hints with no runtime effect, carrying the measurement rather than a shrug (DATA-06, re-homed here from the deferred Phase 150).

**This phase is dual-repo.** D-01 puts a new query command in the firmware, so work lands in **both** `firestarter/` and `firestarter_app/`. That makes 151 the milestone's *second* firmware-touching workstream — v1.32's own roadmap entry describes itself as "mostly host-side with **one** firmware-touching workstream (Phase 149)". That sentence is now out of date and Phase 152's outward-facing text must not repeat it.

**Not in scope:** `write --sdp-relock` (Backlog 999.28, deferred twice — do not implement, do not describe as shipped); folding lock state into `dev test` reports or a `--json` output mode; a live read for protocol `0x10`; curating families beyond what `lockable-proms.md` documents.

</domain>

<decisions>
## Implementation Decisions

### Read source and firmware scope

- **D-01: Real silicon read, exposed as a beta-only `dev lock-status`.** Registered only on a pre-release install, via the existing `_DevGroup` / `channel.BETA_ONLY_DEV_COMMANDS` gate, so a stable install never sees the command and cannot be over-promised to.

  **Rejected: host-only reporting from the curated table** (my recommendation, overruled deliberately). The operator chose the real read knowing the cost.

  **The cost, stated not argued away.** Channel gating is host-side only — the firmware has no notion of channels, and `-D DEV_TOOLS` lives in the shared `[env]` block at `platformio.ini:26` and **is inherited by `uno`, `uno328pb` and `leonardo`**. There is therefore *no* `#ifdef` that makes firmware code free; all three shipped AVR targets pay the bytes. Consequences the planner must fund explicitly:
  - `leonardo`'s MERGE-05 base band is **0 B must-not-grow**. Any growth needs a new named, SHA-attributed exemption in `firestarter/scripts/check_size_baseline.py`, alongside the existing `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` (96) and `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES` (210).
  - A cold triple-target re-measure (`rm -rf .pio/build/<env>` then exactly one `pio run -e <env>` per env) and re-planted tripwire fixtures in `firestarter/tests/test_check_size_baseline.py`. Prior phases learned to **sever affected legs onto a NEW fixture family** rather than editing shared fixtures in place, and never to use "tests byte-unchanged" as an acceptance criterion.
  - ⚠ **Read the live figures before planning, do not copy them from here.** A concurrent quick task (`260820-a7w`) is raising the reported flash ceiling on all three AVR targets to the MCUs' real 32768 B and re-recording `flash_total`/`flash_free` in both `size_baseline.json` and `size_baseline_base01.json`. Leonardo's headroom at the time of this discussion was 1460 B free; after that task it is materially larger. `flash_used` is unaffected by it, so the MERGE-05 growth bands and their arithmetic are unchanged.

- **D-02: The firmware read covers protocol `0x06` (AMD Autoselect) and the Winbond Product-ID boot-block status on the `0x05` rows.** Not `0x10`.

  `0x06` is 190 DB rows (`configure_flash_nor_unlock`, per `firestarter/doc/PROTOCOLS.md`); the neighbouring sequence machinery already exists — `flash_util_get_chip_id` (`firestarter/src/proms/flash_utils.cpp:82`) already issues `FLASH_ENABLE_ID` and reads 0x0000/0x0001, and Autoselect sector-protect verify is a read at the same mode's `SA+0x02`.

  **`0x10` (39 rows: Intel, AMD, Catalyst, ST) is documented-readable but deliberately unimplemented.** This is a *fourth* answer class, distinct from both "not readable" and "unprotected" — see D-09. It must never be reported as unprotected.

  **Rejected:** `0x06` only (leaves the Winbond boot-block question unaddressed, and it is the one family with a chip on the operator's bench); `0x06 + 0x10`; all three (largest byte cost against a 0 B band).

- **D-03: One operator-gated bench leg, on the W29C040, framed as an exploratory PROBE — never as validation.**

  **This corrects a claim made earlier in the discussion and the correction is load-bearing.** `lockable-proms.md` §1 documents **W29C040 / W29C040P** as *"Variant-dependent — Boot blocks or SDP — Must check the exact suffix and revision"*. It is **not** in the documented-readable set. The part that *is* documented readable is **W29C020 / W29C020C** — *"Yes—special, read boot-block status in Product ID mode"*, permanence *Yes*. v1.17's finding that the operator's W29C040 carries a permanently locked first-16K boot block is **empirical** (write→verify failed across the range), not a documented readable-status claim.

  So: the table's readable verdict on `0x05` is gated to **W29C020C only**, and the W29C040 run is a probe whose result is recorded **either way**. A plausible locked-boot-block reading corroborates v1.17 from the read side; garbage vindicates the table's variant-dependent refusal and keeps the sequence gated. **No artifact may claim the `0x05` sequence is silicon-validated on the strength of this leg.**

  Mechanics: the operator seats the chip (chip handling is operator-only); driving the port is permitted.

- **D-04: Against firmware predating the new command, send it and map `MSG_ERR_UNKNOWN_CMD` to `FirmwareOutdatedError`.** Exactly as `sdp_honesty.map_unknown_cmd_to_outdated` already does for `CMD_SDP_LOCK`/`CMD_SDP_UNLOCK`. Keyed on the message **id**, never on text. That helper is currently worded for `"SDP {mode}"`; it is generalised or gains a sibling.

  **Rejected: probing the firmware version first.** `_probe_port`'s `[\d.x]+` truncates the pre-release suffix, so a version probe cannot distinguish the beta that has the command from the beta that does not, and would have to refuse both.

### The curated table and its key

- **D-05: The table is a new Python module in `firestarter_app/firestarter/`, shaped like `sdp_capability.py`** — a literal table of string literals, with each row's `lockable-proms.md` + datasheet citation in a comment directly above it, the way `SDP_CAPABLE_TOKENS` carries its `120-sdp-partition.json` provenance. Importable with no loader; gateable the way `tools/check_sdp_capability_invariants.py` gates its neighbour.

  **Rejected:** JSON under `firestarter/data/` (a hand-curated file sitting beside the **generated** `chip_database.json` is a footgun for the next reader, and costs a loader + schema test + packaging config); markdown-only under `doc/` (two sources of truth with nothing keeping them equal).

  **Hard constraint:** `chip_database.json` is **generated**. The table does not live there and no per-chip field is added to it (DATA-04's proof rule; Phase 148 D-01).

- **D-06: Three-state alias tokens, fail-closed, and the refusal names the offending alias.** Each alias token resolves to `documented-readable`, `documented-not-readable`, or `undocumented`. An entry answers **only** if every one of its alias tokens is `documented-readable`; otherwise it refuses, and the refusal names the specific alias and which state it is in.

  This is the sharp case, measured: the DB entries are `W29C020,W29C020C,W29C022` and `W29C040,W29C042`, and **`W29C022` appears nowhere in `lockable-proms.md` at all**. Unanimity is inherited from `sdp_capability_for_entry`'s own reasoning — a single DB entry can only be answered once, never token-by-token — but the third state makes refusals *actionable*: curating `W29C022` later flips that entry with no rule change.

  **Consequence, accepted:** no `0x05` row answers by default. The sequence is reachable only via D-07.

  **Rejected:** per-entry curated verdicts where the curator adjudicates the undocumented alias (introduces a claim `lockable-proms.md` does not make — the edge DATA-04 polices); strict two-state unanimity (cannot tell the user whether an alias is documented-unreadable or simply never documented).

- **D-07: `--force` is the only path to an unadjudicated read.** The table keeps refusing; `dev lock-status W29C040 --force` runs the sequence anyway and labels the output as an unadjudicated probe, never a state claim. Explicit user opt-in is the guard against the output being read as a guarantee, and `--force` already means "proceed past a safety refusal" on `id`, `blank` and `erase`, with `FLAG_FORCE` downgrading chip-ID mismatch to a warning in firmware.

  **Rejected:** a fourth `probe-permitted` table state (the whole honesty burden would land on wording, with no user opt-in); both mechanisms together (most machinery for one bench leg).

### Output, refusal and exit code

- **D-08: Every answer leads with a machine-stable class token, followed by explanatory prose.** The class name **is** the honesty contract: tests assert the exact token rather than grepping wording, so a later prose edit cannot silently collapse two classes, and `unprotected` can never be produced by a path that did not read silicon.

  **Rejected:** prose-only (pushes LOCK-04's distinction into full-text snapshot assertions — this codebase already carries two such syrupy snapshots and they go red on any rewording); adding `--json` (report-layer consumption is a deferred idea).

- **D-09: Eight classes, and they must remain distinguishable.** `protected` · `unprotected` · `not_readable` · `not_implemented` · `undocumented_alias` · `no_mechanism` · `firmware_outdated` · `unadjudicated_probe`.

  `no_mechanism` is a real and separate answer, not a synonym for `unprotected`: **406 of 746 DB rows have no write-protection mechanism at all** (UV-EPROM `0x07`/`0x08`/`0x0B`, SRAM/NVRAM `0x0E`/`0x27`/`0x28`/`0x29`). Measured class sizes at discussion time — re-derive, do not trust: readable families 229 (`0x06` 190 + `0x10` 39), documented-not-readable 111 (`0x0D` 84 + `0x05` 27), no mechanism 406.

- **D-10: Exit 0 only for a real silicon read** (`protected` or `unprotected`). A distinct non-zero for "cannot answer" (`not_readable`, `not_implemented`, `undocumented_alias`, `no_mechanism`); a separate non-zero for operational failure (`firmware_outdated`, comms). `$? == 0` therefore means exactly "I hold a real state". The class token still carries the detail, so tests assert **token and code together, never the code alone**.

  **Rejected:** 0 for every honest answer (a script cannot distinguish answered from correctly-declined); per-class codes throughout (makes a correct `protected` read a non-zero failure; this codebase already has exit-code precedence defects where `max()` picked the wrong verdict).

- **D-11: The refusal prose lives in an extended `firestarter_app/firestarter/sdp_honesty.py`.** Its `unreadable_state_caveat()` already returns *"The resulting protection state cannot be read back on this chip family, so this is not a claim about the chip's actual state"* — near-exactly what `not_readable` needs. **Both of that module's declared forward callers were deferred** (Phase 134's leg-report rows, Phase 135/150's `write --sdp-relock`), so `lock-status` is the first one to actually land. It has no `click` dependency by design, so the command can import it freely.

  Accepted cost: the module's name says SDP while it will also carry Autoselect and boot-block wording. Keeping one copy of the sentence beats the drift the module exists to prevent.

  **Rejected:** prose in the curated-table module; a new dedicated honesty module (two modules obliged to agree about one physical fact).

- **D-12: LOCK-04 is enforced by a DB-wide class invariant test, not by careful authoring.** Walk all 746 DB entries, resolve each to its class token, and assert the partition exhaustively; assert the structural invariant that `protected` and `unprotected` are **unreachable** on any path that did not actually read silicon; assert every readable-verdict row carries a citation. It tests the mechanism rather than the prose — it cannot be satisfied by rewording, it goes red when a new DB row lands in no class, and it does not rot when someone edits a sentence.

  **Rejected:** a phase-local `151-check-claims.py`. The `check_permitted_claims.py` family has already failed **open** once, because its `_HERE` resolves to the *checking* phase's own directory, so cross-phase reuse scans nothing and exits 0.

### DATA-06 — `protect_on_after`'s single home

- **D-13: The single authoritative statement goes in `firestarter_app/doc/infoic-field-dictionary.md`**, as a section alongside the existing per-field entries (which already carry CONFIRMED/UNKNOWN status lines and feed that file's *"build_db.py Known Bugs vs Correct Semantics"* summary). It is the artifact whose declared job is "what this field means and what we do with it".

  The upstream **bit** is already tabled in three places — `doc/package-details.md:43-44`, `doc/infoic-field-dictionary.md:120-121`, `doc/protocol-flags.md:24-25` — but those document minipro's bit semantics, a *different* fact from the emitted field's runtime status. The other two tables get a **one-line pointer**, so "documented once" means one statement, not one mention.

- **D-14: Cover both siblings in that one section, each with its own measurement.** Verified against `chip_database.json` during this discussion (746 rows, 59 vendors, nested under `programming`):
  - `protect_on_after`: **70 of 746** true. By algorithm: `5` → **27 of 27** (a constant there), `13` (`0x0D`) → 43. Zero elsewhere.
  - `protect_off_before`: **148 of 746** true. By algorithm: `5` → 27, `6` → 77, `13` → 43, `52` → 1.
  - Neither field has any runtime consumer: the only references in `firestarter_app/firestarter/` are a *comment* at `sdp_capability.py:74` and the test files `test_b15_page_size_corroboration.py` / `test_sdp_db_invariant.py`.

  Documenting one and leaving its sibling silently dead would reproduce the exact condition DATA-06 exists to end — and a reader who finds one field explained and the neighbour unexplained will reasonably assume the neighbour *is* consumed.

  **Rejected:** DATA-06's literal `protect_on_after`-only scope plus a todo for the sibling; additionally chasing the undocumented bits 22 (`0x00400000`) and 9 (`0x200`).

- **D-15: The wording must carry the measurement, not a shrug, and must state why no consumer exists.** `MP_PROTECT_AFTER` means *"can re-protect after write"* — it gates minipro `-P`, so it is a **capability, not a policy**. Its only discriminating information anywhere is the `0x0D` ALLOW/REFUSE split, which `sdp_capability` already transcribes and `tests/test_sdp_db_invariant.py::test_sdp_partition_matches_infoic_derived_field_element_wise` already proves element-wise equal. The doc must say plainly that **no runtime consumer exists in this release because `write --sdp-relock` is deferred to Backlog 999.28**, and must not imply the field is honoured.

- **D-16: DATA-06 ships with no behaviour change, no new gate, and no `sdp_capability.py` edit.** `tools/check_sdp_capability_invariants.py`'s Class 2(b) forbids binding `SDP_CAPABLE_TOKENS` to anything but a literal `frozenset`, and that gate is **not weakened**. The D-12 invariant test is scoped to the new curated table and the class partition; it is not a DATA-06 deliverable.

### Claude's Discretion

The operator did not choose to discuss these; the planner decides them, consistent with the decisions above:

- Wire protocol shape for the new firmware command — command number, response framing, and whether the payload is a single status byte or a per-region structure. Note `MSG_OK_READY` extends with **zero** codegen (length-discriminated blob, read at a computed `ver_end`), and firmware `messages.h` **is codegen-generated and ID-only** — wording-only changes there produce a zero diff; edit the meta repo's `messages.toml` and regenerate.
- Whether the read reports device-global or per-sector/per-region state, and how a multi-region answer renders under D-08's single leading class token.
- Which named MERGE-05 exemption the new firmware bytes are funded under, and its framing.
- How `permanence` is represented in the table separately from `readability` (`lockable-proms.md` treats them as independent axes, and W29C020C is the case where permanence matters most).
- Whether `protect_off_before`'s `algorithm: 6` correlation (77 rows, the AMD Autoselect family) is worth a sentence in D-13's section. It is suggestive given D-02, but the research note's verdict — flags 14/15 cannot derive readability, `W29C020C` is flag-identical to `W29EE011` — stands and must not be relitigated.

### Folded Todos

- **`decode-infoic-flags-bits-14-15-protect-metadata.md`** — *"Decode infoic.xml flags bits 14/15 (protect-before/protect-after) in build_db.py"*. Its emit half is **already landed**: both `protect_off_before` and `protect_on_after` are present under `programming` on 744 of 746 rows. What remains unmet is its own interpretation guardrail — *"these are write-path reversibility hints, NOT lock-status readability"* — which is exactly D-13/D-15's statement. Folded: closing DATA-06 closes this todo, and the planner should mark it resolved rather than leaving a todo whose acceptance criteria are met.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The protection table's source (LOCK-01)
- `firestarter_app/doc/lockable-proms.md` — the family-level master list of protection mechanism / readability / permanence. **§Key** defines the `Yes—sector` / `Yes—global` / `Yes—special` / `Indirect` / `No` / `Permanent` vocabulary; **§1 Winbond parallel flash** is where W29C020C is `Yes—special` and W29C040 is variant-dependent (D-03); **§Practical summary** partitions readable / not-readable / potentially-irreversible families; **§Important programmer implementation rule** proposes the `protection_kind` / `status_readable` / `unlockability` taxonomy the table transcribes.
- `.planning/seeds/lock-status-command-hand-curated-protection-table.md` — the originating seed. Carries the two-axis scope shape (database axis + firmware per-family query sequences) and names the three sequence families.
- `.planning/notes/infoic-xml-protection-flags-research.md` — **negative result, do not re-investigate.** `status_readable` is not derivable from `infoic.xml`; `W29C020C` is flag-identical to `W29EE011`; the whole AMD readable group carries zero protection bits. This is what makes hand-curation compliant with DATA-04 rather than a violation of it. Read the 2026-07-29 scoped-exception note at the end too.

### Host patterns this phase reuses (D-05, D-06, D-11)
- `firestarter_app/firestarter/sdp_capability.py` — the shape to copy: literal `frozenset` of string literals with provenance comments; `split_part_number_tokens` (do **not** strip parentheticals); `sdp_capability_for_entry`'s fail-closed unanimity rule and its `(bool, reason)` return; and the hard-fail on a missing `protocol-id` key that exists because a silent default is how `check_eprom_blank`'s SRAM short-circuit went vacuous.
- `firestarter_app/firestarter/sdp_honesty.py` — the honesty carrier being extended. `unreadable_state_caveat()`, `emission_summary()`, `map_unknown_cmd_to_outdated()`.
- `firestarter_app/tools/check_sdp_capability_invariants.py` — Class 2(b) literal-frozenset gate. Model for gating the new table; **not to be weakened** (D-16).
- `firestarter_app/firestarter/cli_handlers.py` — `_DevGroup` and its `get_command` override (the empirically-settled hook; `resolve_command` needs no override), `_DEV_TOOLS_ENABLED`, and the conditional-registration pattern at each gated `@dev.command`. `--force` precedents live on `id` / `blank` / `erase`.
- `firestarter_app/firestarter/channel.py` — `is_dev_tools_enabled()`, `BETA_ONLY_DEV_COMMANDS`, `dev_command_gate_message()`.
- `firestarter_app/tests/test_dev_group_channel_gating.py`, `firestarter_app/tests/test_dev_tools_channel_gate.py`, `firestarter_app/tests/test_click_group_gate_hook.py` — the gating tests a new beta-only command must extend.

### Firmware (D-01, D-02)
- `firestarter/doc/PROTOCOLS.md` — **operator-approved source of truth** for the protocol↔handler map. The handler-family table names the 7 `configure_*` groupings; `0x06` → `configure_flash_nor_unlock()`, `0x05` → `configure_flash_5v_page()`, `0x0D` → `configure_eeprom28c()`, `0x10` → `configure_flash_intel()`.
- `firestarter/src/proms/flash_utils.cpp` §`flash_util_get_chip_id` (~:81) — the existing Autoselect-adjacent sequence: `FLASH_ENABLE_ID`, read 0x0000/0x0001, `FLASH_DISABLE_ID`.
- `firestarter/src/proms/flash_nor_unlock.cpp` — the `0x06` handler and its `byte_flip_t` sequence idiom.
- `firestarter/src/proms/flash_5v_page.cpp` — the `0x05` handler; its :87 comment records that W29C040 ships with SDP enabled.
- `firestarter/include/firestarter.h` — the `CMD_*` block (currently ends at `CMD_HW_VERSION` 15) and the `handler`-dispatch allow-list a new command must be added to.
- `firestarter/include/flash_utils.h` — `FLASH_ENABLE_WRITE_PROTECTION` / `FLASH_DISABLE_WRITE_PROTECTION` tables (:48, :53).
- `firestarter/platformio.ini` — **:26 is where `-D DEV_TOOLS` lives, in the shared `[env]` block inherited by all three AVR targets.** This is why there is no free `#ifdef`.
- `firestarter/scripts/check_size_baseline.py` — MERGE-05 band and exemption literals; the `flash_total` invariant sites (~:374, ~:499).
- `firestarter/scripts/baseline/size_baseline.json` and `.../size_baseline_base01.json` — the live and frozen baselines. **Both are being edited by quick task `260820-a7w`; read them fresh.**
- `firestarter/tests/test_check_size_baseline.py` — the tripwire fixtures that redden on any baseline movement.

### DATA-06 (D-13, D-14, D-15)
- `firestarter_app/doc/infoic-field-dictionary.md` — the chosen home. §`flags` (:107) is the existing bit table; :120-121 are the bit-14/15 rows.
- `firestarter_app/doc/package-details.md` :43-44 and `firestarter_app/doc/protocol-flags.md` :24-25 — the two other bit tables that get one-line pointers.
- `firestarter_app/tests/test_sdp_db_invariant.py::test_sdp_partition_matches_infoic_derived_field_element_wise` — the existing element-wise proof D-15 must cite.
- `firestarter_app/tests/test_b15_page_size_corroboration.py` — in-tree precedent for "documentation carrying a measured refutation" rather than a claim.
- `.planning/todos/pending/decode-infoic-flags-bits-14-15-protect-metadata.md` — folded (see Folded Todos).

### Milestone framing
- `.planning/REQUIREMENTS.md` §LOCK (LOCK-01…04), §DATA (DATA-04, DATA-06), §Out of Scope (the RELOCK deferral row).
- `.planning/ROADMAP.md` §"Phase 151" and §"Phase 150" (the deferral record), plus §"Phase 999.28".

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `sdp_capability_for_entry` — a pure `(entry, display_name) -> (bool, reason)` predicate with fail-closed unanimity over alias tokens. D-06 is this rule with a third state; the signature generalises to `-> (class_token, reason)`.
- `sdp_honesty.unreadable_state_caveat()` — the `not_readable` sentence, already written and already test-pinned.
- `sdp_honesty.map_unknown_cmd_to_outdated()` — D-04's mechanism, needing only generalisation off the `"SDP {mode}"` wording.
- `flash_util_get_chip_id` / `flash_util_byte_flipping` / `byte_flip_t` — the firmware sequence primitives; a protect-verify read is the same mode with a different read address.
- `_DevGroup` + `BETA_ONLY_DEV_COMMANDS` + conditional registration — D-01's channel gate, already built and tested, needing one more name.
- `--force` / `FLAG_FORCE` — D-07's opt-in, with three existing command precedents and a firmware-side severity-downgrade convention.

### Established Patterns
- **Hand-curated data lives as literal string-literal collections with provenance comments, guarded by an AST-based invariant gate.** `SDP_CAPABLE_TOKENS` + `check_sdp_capability_invariants.py` is the template (D-05).
- **`chip_database.json` is generated.** Never hand-edited; no per-chip lookup table keyed on part number, and no sibling to the pre-existing `_PAGE_SIZE_BY_PART` exception (DATA-04).
- **Honesty wording is centralised, never duplicated**, precisely so two copies cannot drift (D-11).
- **Fail-closed is the default direction** on anything touching a chip whose identity cannot be confirmed — one DB entry gets one answer, never a per-token verdict.
- **Firmware growth is adjudicated, not absorbed:** named, SHA-attributed exemptions stacked on an unchanged base band, with the admitted growth left visible in the report rather than disappearing into a re-anchored reference point.

### Integration Points
- **Host → firmware:** a new `CMD_*` in `firestarter/include/firestarter.h`, its dispatch allow-list arm, and the matching constant in `firestarter_app/firestarter/constants.py`. Per `CLAUDE.md`, constants and flag bits are duplicated between the two and **must change together**; likewise any `serial_comm.py` ↔ `firestarter.cpp` protocol change.
- **Host CLI:** one new `@dev.command` in `cli_handlers.py`, module-scope-guarded by `_DEV_TOOLS_ENABLED`, plus its name in `channel.BETA_ONLY_DEV_COMMANDS`.
- **Chip resolution:** the predicate must receive the **full dict from `db.get_eprom()`** — `resolve_chip()`/`convert_to_programmer()`'s programmer dict carries neither `protocol-id` nor `name`, which is exactly the trap `sdp_capability_for_entry` hard-fails on.
- **Dual-repo lockstep:** executors commit **inside** each submodule, on the milestone branch (`gsd/v1.32-at28c-write-path-root-cause-report-provenance` in both). Use `commits_land_in:` in plan frontmatter — worktrees leave submodules empty and the gate under-detects.

</code_context>

<specifics>
## Specific Ideas

- The `0x05` sequence was funded specifically to make the **v1.17 W29C040 locked-boot-block RCA** answerable from the read side, closing it without needing the second sample that RCA asked for. That payoff is the reason those bytes are being spent — but D-03 caps what may be claimed from it.
- `sdp_honesty.py`'s existing sentence is the wording target for `not_readable`; the operator chose to extend that module partly so there is exactly one copy of it.
- The `W29C020,W29C020C,W29C022` entry is the worked example for D-06 — a readable part, a documented sibling, and an alias that appears in no source document. If the refusal for that entry does not name `W29C022` specifically, D-06 is not implemented.

</specifics>

<deferred>
## Deferred Ideas

- **Fold lock state into `dev test` diagnostic reports, and/or add a `--json` output mode** — a real payoff named in the seed (a write-path pre-flight that says "this chip has a locked boot block, full-range verify will fail" would have short-circuited the v1.17 mystery), but it is a new capability and belongs in its own phase. D-08 keeps the class token machine-stable so this stays cheap later.
- **A live protection read for protocol `0x10`** (39 rows, Intel 0x90 command-register) — deliberately unimplemented per D-02; ships as the `not_implemented` class.
- **Curating `W29C022`** — would flip the `W29C020,W29C020C,W29C022` entry to answerable with no rule change (D-06). Needs a datasheet, not an inference.
- **Decoding `infoic.xml` bits 22 (`0x00400000`) and 9 (`0x200`)** — undocumented, no minipro constant; bit 22 set on the AT29C/W29C/W29EE page-write group, bit 9 observed only on MX29F040. Recorded in the research note's loose ends, declined here (D-14).
- **`write --sdp-relock`** — Backlog **999.28**, deferred twice (v1.30 Phase 135, v1.32 Phase 150). Not this phase. Phase 152's OUT-01/OUT-04 must describe a **withdrawal, never a migration**, and OUT-05's claim gate rejects any outward text naming the command as shipped.
- **A compensating bootloader-safe flash guard** — raised while the concurrent quick task `260820-a7w` removed the linker's protection over the bootloader region. The operator declined it there; noting it here because D-01's firmware growth now lands against a raised ceiling.

### Reviewed Todos (not folded)

`todo.match-phase 151` returned 24 matches, all at a flat score of 0.6 — keyword noise rather than signal. Reviewed and **not** folded:

- **`land-write-sdp-relock…`** — Backlog 999.28. Explicitly out of scope; see Deferred Ideas.
- **`fm28v020-mb85r256h-fram-ride-0x0d…`** — FRAM parts riding the `0x0D` handler by pinout promotion. A classification question from Phase 149 D-04, not a protection-readability one. Note `sdp_capability.FRAM_TOKENS` already refuses these two, so they land in a refusal class regardless.
- **`66-promoted-0x0d-rows-keep-the-64-byte-page-floor…`** — Phase 149's page-size floor. Unrelated axis.
- **`runtime-info-log-naming-the-effective-page-size…`**, **`phase-44-read-timing-knobs…`**, **`skip-vpp-error-warning-checks…`**, **`frame-level-deadline-cobs-decoder…`**, **`config-version-not-bumped…`**, **`fm1608-byte-0-write-never-lands…`**, **`prove-platformio-dev-tools-flag-fails-closed…`** — firmware items unrelated to protection state. The dev-tools-flag one is *adjacent* to D-01's finding that `-D DEV_TOOLS` ships in all three AVR builds, but proving it fails closed is its own task.
- **`at28c256-write-path-failure-gh20…`** — Backlog 999.29, still open; no AT28C part in inventory.
- **`reply-on-gh12…`** — Phase 152 OUT-01.
- The remaining matches (board photography, MODIFICATIONS.md, jumper renderers, `ladder_state`, GSD plan-scan, record-gate timing, `response_code` log macro, `vcc == 5500` verify-rail group, DATA_BUFFER_SIZE spike) matched on generic tokens only.

</deferred>

---

*Phase: 151-protection-readability-lock-status*
*Context gathered: 2026-08-20*
