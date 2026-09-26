# Phase 60: Display-Layer Decode Correctness - Context

**Gathered:** 2026-06-10
**Status:** Ready for planning

<domain>
## Phase Boundary

The scope is the **complete `firestarter info` operator-facing output** — every displayed field
is reviewed for decode-correctness and for "does not mislead," using the database's
`electrical.type` (and the erasable flag) as ground truth rather than keying solely on
`protocol_id`. The two known decode defects are the **Type** label and the **"Can be erased"**
status; the operator also wants the **`-- NOT VERIFIED --`** marker gone. Any other field in the
`info` output that is wrong or misleading under the same `electrical.type` lens is in-scope to fix.

The electrically-erasable parts reclassified in the Phase 59 follow-up `cca7d62` (W27C512,
SST27VF512, SST27SF512, W27C257, and the wider CMOS-EEPROM / SST SuperFlash family) display as
EEPROM; genuine UV-EPROMs (M27C512, 27C256, 2764, …) still display as UV-EPROM with no regression.

**HOST-ONLY.** Firmware electrical-erase support (making `firestarter erase W27C512` actually
work) is a separate firmware backlog item — NOT this phase.

**Root cause this phase fixes:** both an EEPROM (W27C512) and a UV-EPROM (2764) carry the
*identical* `programming.algorithm` / `protocol_id` = `0x07`. The ONLY field that distinguishes
them is `electrical.type` (`"EEPROM"` vs `"UV-EPROM"`). The current display keys on
`protocol_id` and therefore collapses both into "UV-EPROM / MTP-Flash (12V VPP)".

</domain>

<decisions>
## Implementation Decisions

### Type label (displayed chip "Type")
- **D-01:** The displayed Type comes from a **curated `{electrical.type → display string}` map**
  keyed on `electrical.type` (e.g. `EEPROM`, `UV-EPROM`, `SRAM`, `Flash`). This map is the **sole
  source** of the Type label. The protocol/voltage detail (currently embedded in the Type string
  via `get_chip_type_string`'s `proto_display` table) moves to the **separate `protocol_info`
  block only** — it is no longer part of the Type label.

### "Can be erased" line
- **D-02:** The "Can be erased" line reports **electrical erasability only**, derived from
  `electrical.type` / the erasable flag. It does **NOT** reference or gate on firmware
  erase-command availability. EEPROM/Flash → erasable; UV-EPROM → not electrically erasable
  (UV-only). **This intentionally simplifies ROADMAP success-criterion 2** (which had asked to
  surface the firmware-erase gap inline): the operator-directed decision is "show whether the
  chip *can* be erased, and don't tie that line to the firmware." Do NOT add firmware caveats to
  this line — the firmware gap stays a separate backlog item (see Deferred).

### Where the ground-truth field is read (plumbing)
- **D-03:** `ic_layout.py` reads the **raw `electrical` block directly** (the raw `electrical`
  dict is passed/looked up into the presenter). `_map_data`'s existing mapped fields are left
  alone **except** for fixing the stale erasable-flag derivation: today
  `info_flags |= 0x10` only fires when `electrical.type == "Flash/EEPROM"`, but real records say
  `"EEPROM"` — so the erasable bit currently never fires for W27C512 / SST27VF512. Fix that
  match to cover the EEPROM/Flash family.

### Test coverage
- **D-04:** **Both** layers: (a) **synthetic fixtures** — minimal hand-built records, one per
  `electrical.type` (`EEPROM`, `UV-EPROM`, and at least `SRAM`/`Flash`) — drive the label /
  can-erase unit logic in isolation from DB regeneration; (b) a **parametrized real-DB smoke
  set** asserts the EEPROM cases **W27C512, SST27VF512, SST27SF512, W27C257** display as EEPROM
  and the UV-EPROM controls **M27C512, 27C256, 2764** display as UV-EPROM, end-to-end against
  the real `chip_database.json`.

### Operator-facing presentation cleanup (folded in during discussion)
- **D-05:** Remove the **`-- NOT VERIFIED --`** marker from the `firestarter info` output (the
  `verified_str` field built in `prepare_detailed_eprom_data`, [ic_layout.py:490-492]). The
  operator no longer wants this marker shown. Same `info` output / same method as the decode
  work — folded into this display-layer phase at the operator's request.

### Scope = the whole `firestarter info` output
- **D-06:** The phase covers **everything in the `firestarter info` output**, not only the three
  fields above. Audit every displayed field — `Type`, `Can be erased`, `verified` marker (D-05),
  `protocol_info`, `flags_info` (the `_interpret_flags` strings), `vpp`/`vcc`, pin/jumper layout,
  chip-id — and correct anything that is wrong or misleading under the `electrical.type`
  ground-truth lens. **Also confirm `firestarter info` does not crash for any in-DB chip.** The
  historical `vpp-pin` list-vs-int `TypeError` appears already mitigated (see code_context); if
  any crash remains in the `info` path, fix it — but if a remaining crash genuinely requires the
  v1.9-deferred read-bug work, **surface that as a milestone-boundary decision** rather than
  silently pulling v1.9 work into v1.11. Bound the audit to *correctness/not-misleading* — this is
  not a redesign of the `info` layout.

### Protocol & flags explanations must be correct (operator-flagged)
- **D-07:** The `protocol_info` block (`_get_protocol_info_structured`, L260+) and the `flags_info`
  block (`_interpret_flags`, L236-258, assembled at L580-583) must be reviewed and corrected.
  Confirmed concrete defects to fix:
  - **0x10 bit semantic collision.** `_map_data` sets `info-flags & 0x10` to mean "can be
    **electrically erased**" (used by the can-erase line at L514) — but `_interpret_flags` labels
    `0x10` as **"Needs software write-enable/unlock sequence"** and labels `0x80` as
    "Electrically erasable". So once D-03 sets the erasable bit, `flags_info` would render the
    *wrong* description. Reconcile the bit→meaning mapping across `_map_data`, `_interpret_flags`,
    and the can-erase derivation so all three agree.
  - **Missing erasable property for EEPROMs.** Today W27C512's `flags_info` shows only `0x20`
    ("readable ID") and no erasable property (the D-03 `== "Flash/EEPROM"` bug). After the fix the
    erasable property must appear for the EEPROM family.
  - **Dead `_interpret_flags` entries.** Only the two synthesized `info-flags` bits (`0x20`,
    `0x10`) are ever derivable from the new DB (raw upstream `flags` are not carried), so most of
    the `_interpret_flags` table can never fire. Verify the table reflects what is actually
    derivable (prune or re-source) rather than implying properties the data can't express.
  - **VPP voltage never shown.** `vpp_str` is gated on `eprom_data["flags"] & 0x08` (L517-520),
    but mapped `flags` is always `0`, so `info` never prints VPP even for 12V-VPP chips. Source
    the VPP display from `vpp_volts`/`vpp_mv` (which are populated) instead.
  - **Protocol description text accuracy.** `protocol_info` IS populated (e.g. 0x07 →
    "EPROM/EEPROM"). Review each protocol's descriptive text so it is accurate and does not
    contradict the new `electrical.type`-sourced Type label — note 0x07 is genuinely the *shared*
    algorithm for both UV-EPROM and these EEPROMs, so the protocol label legitimately stays
    "EPROM/EEPROM" while the Type label (D-01) is the per-chip electrical truth.

### Claude's Discretion
- The exact display strings inside the curated `electrical.type → label` map and the precise
  yes / no / "UV-only" wording of the "Can be erased" line (within the rules in D-01 / D-02).
- Whether to drop the `verified_str` field entirely or blank it / remove only the output row
  (D-05) — pick whatever is cleanest given how the presenter assembles output.
- Fallback label when `electrical.type` is absent/empty (legacy user-override DB entries):
  fall back to the existing protocol-based label rather than crashing.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope
- `.planning/ROADMAP.md` §"Phase 60: Display-Layer Decode Correctness" — goal + 5 success
  criteria (note D-02 above adjusts criterion 2's emphasis).

### The display code to change (host, `firestarter_app/`)
- `firestarter_app/firestarter/ic_layout.py` — `get_chip_type_string` (L203, the `proto_display`
  table + int `type_map`), the "Can be erased" derivation (L504–515), `_interpret_flags` (L236–258,
  the flag→description table; D-07) + the `flags_info` assembly (L580–583), `_get_protocol_info_structured`
  (L260, where protocol detail should live; D-07), the `vpp_str` gate (L517–520; D-07),
  `verified_str` (L490–492, D-05), and the `prepare_detailed_eprom_data` assembler that builds
  `output_data`.
- `firestarter_app/firestarter/eprom_info.py` — `EpromConsolePresenter` (the `info` command
  presenter that calls into ic_layout).
- `firestarter_app/firestarter/database.py` — `_map_data` (L383–460), `_ALGO_MEM_TYPE` (L48, why
  `0x07` collapses EPROM+EEPROM to int type 1), `get_eprom` (L526). The erasable-flag fix in D-03
  lives at L432–433.
- `firestarter_app/firestarter/data/chip_database.json` — decode ground truth; each record's
  `electrical.type` is the distinguishing field (`"EEPROM"` vs `"UV-EPROM"`).

### Background / decode RCA
- `firestarter_app/CLAUDE.md` — data-flow (build_db → DB → _map_data → display), the WARNING-5
  override note, and the `cca7d62` electrical-erasable family note (W27C512/SST27VF512/… are
  `electrical.type="EEPROM"`, NOT UV-EPROMs).
- `.planning/debug/resolved/infoic-decode-eeprom-misclass.md` — the EEPROM-vs-UV
  misclassification RCA + VPP decode fix (`cca7d62`) that produced the corrected `electrical.type`.
- `tests/test_eprom_info.py` (`firestarter_app/tests/test_eprom_info.py`) — existing presenter
  test patterns + the `skip_local_override=True` DB fixture to reuse.

### Landmine to read before writing happy-path tests
- `.planning/debug/firestarter-info-vpp-pin-crash.md` — the pre-existing `vpp-pin <= pin_count`
  TypeError (list-vs-int) in `ic_layout`'s full layout path. See code_context risk below.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `EpromConsolePresenter` (`eprom_info.py`) + the `SpecBuilder`/layout logic in `ic_layout.py`
  are the existing `info` rendering path — extend, don't replace.
- `tests/test_eprom_info.py` already has `db` / `presenter` module fixtures
  (`EpromDatabase(skip_local_override=True)`) to build on for D-04's smoke set.

### Established Patterns
- Canonical data flow (per `firestarter_app/CLAUDE.md`): `build_db.py → chip_database.json →
  EpromDatabase.get_eprom → _map_data → display`. D-03 deliberately has the presenter reach the
  **raw** `electrical` block rather than threading a new mapped field.
- Tooling gate: `ruff check` + `ruff format --check` + `pytest --cov-fail-under=70`. **mypy
  strict applies to 8 modules** (`main, cli_handlers, chip_resolver, frame_parser, codec,
  address_parser, exceptions, serial_comm`) — `ic_layout.py` and `eprom_info.py` are NOT in the
  strict set, so changes there need ruff-clean + non-strict mypy, not strict annotations.

### Integration Points
- CLI: `firestarter info <chip>` → `EpromConsolePresenter.prepare_detailed_eprom_data(...)` →
  `ic_layout.get_chip_type_string(...)` + the can-erase / verified_str assembly in `output_data`.

### Risk / landmine (FLAG for planner — verify, don't assume)
- **`vpp-pin <= pin_count` TypeError (list-vs-int)** in `ic_layout` was the **GATE-1.8b witness**
  (`test_eprom_info.py` historically avoided the full `prepare_detailed_eprom_data` happy path
  because of it). It now **appears mitigated**: `ic_layout.py:404-412` extracts scalars from
  list-valued pin maps via `_first_pin`, and a live call to `prepare_detailed_eprom_data` for
  `W27C512` / `27C256` returned cleanly (no crash, full `output_data`). So D-04's real-DB smoke
  set is most likely safe on the full path — but the planner should **confirm** against the
  current code (and the GATE-1.8b snapshot witness `test_info_known_chip_stderr`) rather than
  trusting this note, and must not regress that snapshot.

</code_context>

<specifics>
## Specific Ideas

- Reclassified EEPROM display set (must show EEPROM): **W27C512, SST27VF512, SST27SF512, W27C257**.
- UV-EPROM control set (must still show UV-EPROM): **M27C512, 27C256, 2764**.
- Ground-truth example: `W27C512` → `electrical.type="EEPROM"`, `algorithm=7`; `2764` →
  `electrical.type="UV-EPROM"`, `algorithm=7` — same algorithm, different `electrical.type`.

</specifics>

<deferred>
## Deferred Ideas

- **Firmware electrical-erase support** (so `firestarter erase W27C512` actually works) — explicit
  separate firmware backlog item per the ROADMAP; out of scope for this host-only phase. D-02
  deliberately keeps the "Can be erased" line decoupled from this gap.
- **Full fix of the `vpp-pin` list-vs-int TypeError** — belongs to v1.9 / GATE-1.8b; only touch
  it here if it directly blocks the D-04 smoke tests, and only minimally.

</deferred>

---

*Phase: 60-display-layer-decode-correctness*
*Context gathered: 2026-06-10*
