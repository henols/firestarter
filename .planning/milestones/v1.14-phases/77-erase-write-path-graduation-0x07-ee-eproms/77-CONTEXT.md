# Phase 77: Erase Write-Path Graduation (0x07 EE-EPROMs) - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire `FLAG_CAN_ERASE` from the canonical infoic.xml erase mask so a **default**
`firestarter write` (no `-b`) of a W27C512-class EE-EPROM auto-erases before
programming, and bench-prove the full write→auto-erase→program→verify cycle on
Leonardo with a real W27C512. **Host-only** change (`firestarter_app`); the
firmware `eprom_write_init` guard already honors `FLAG_CAN_ERASE`. Establishes
the milestone's SAFE-01/02/03 graduation discipline.

**Key reframe surfaced during scout:** the 7–8 0x07 EE-EPROMs
(W27C512/W27E512/W27C257/W27E257/SST27SF256/SST27SF512/SST27VF256/SST27VF512)
are **already `support_status: supported`** in `chip_database.json` — there is
**no `chip_resolver` host-guard refusal to remove** in this phase (unlike Phases
78–80). "Graduation" here = making the default write auto-erase (today a non-blank
chip needs `-b`), NOT lifting a refusal.

**Out of scope:** firmware changes (guard already correct); the other three v1.14
gaps (X88C64 / 25V NMOS / AT28C adapter — Phases 78–80); read-bug RCA (v1.9).
</domain>

<decisions>
## Implementation Decisions

### Erase-flag scope (canonical mask, not protocol heuristic)
- **D-01:** `FLAG_CAN_ERASE` is wired from the **canonical erase-capability
  ground truth** — the infoic.xml `flags & 0x10` (`MP_ERASE_MASK`) — which
  `build_db.py` already decodes into `electrical.type`. Wire it off
  `electrical.type`, NOT a `protocol_id` heuristic and NOT the raw runtime
  `info-flags` field.
- **D-02:** Set the flag for **all erasable types** — `electrical.type in
  {"EEPROM", "Flash/EEPROM"}` (operator decision: uniform with the mask
  semantics). This matches the existing `_map_data` keying
  ([database.py:434](../../../firestarter_app/firestarter/database.py#L434)).
  The flag only changes firmware behavior on the `configure_eprom`
  (0x07/0x08/0x0B) path; on the 0x0D `configure_eeprom28c` path it is expected
  to be **inert** (that handler manages its own erase).
- **D-03 (downstream verify — MANDATORY):** Because D-02 now also sets the flag
  on the 0x0D `Flash/EEPROM` parts, the researcher/planner MUST confirm the
  firmware `configure_eeprom28c` path genuinely **ignores** `FLAG_CAN_ERASE`
  (no double-erase, no VPP/behavior change, no hazard for 28C-family chips). If
  it does NOT ignore it, narrow the scope back to the `configure_eprom`
  EEPROMs only and record why.

### Bench acceptance rigor
- **D-04:** Bench proof = a **single** write→auto-erase→program→verify cycle per
  SC#2 (N≥5 NOT required here): one `firestarter write` (no `-b`) of a **non-blank**
  real W27C512 on Leonardo, an independent post-write full read that SHA-matches
  the source file, and a **non-vacuous negative control** (a wrong-file verify
  exits non-zero). Standing bench precondition applies (see Canonical refs).

### SAFE-01/02/03 framing for this phase
- **D-05:** SAFE-01's host-guard removal is **N/A-no-refusal** here — the chips
  are already `supported`, so there is no `chip_resolver.resolve_chip` refusal to
  drop. Document this explicitly so downstream agents do not hunt for / fabricate
  a refusal. The evidence-gated "FINAL step" that the SAFE discipline protects is
  instead the **`FLAG_CAN_ERASE` wiring itself** — it lands only after the
  native + wire round-trip + Leonardo bench evidence is on record.
- **D-06:** SAFE-02 (full-DB `check_dispatch.py` VPP-safety gate green after the
  change) and SAFE-03 (firmware↔host constant parity if any `FLAG_*`/protocol
  constant in `constants.py` ↔ `firestarter.h` is touched, parity tests green)
  **still fully apply**.

### 0xA4 regression guard
- **D-07:** Add an explicit **host-side regression test** asserting the default
  (no `-b`) auto-erase write path keeps `ack_data=False` on INIT/END DATA frames,
  so the 2026-06-17 0xA4 desync (per-chunk blank-check INIT DATA being acked)
  cannot silently return. Plus a bench note confirming the no-`-b` write completes
  clean (the SC#2 cycle doubles as the live proof).

### Research flags (resolve during RESEARCH, not user decisions)
- **RF-01:** The ROADMAP's premise "the **always-zero** `info-flags & 0x10`" is a
  wording trap — it refers to the *runtime `_map_data` synthetic `info_flags`
  field*, NOT the `build_db.py` `flags` ground truth. `_map_data`
  ([database.py:434](../../../firestarter_app/firestarter/database.py#L434))
  **already injects** `info_flags |= 0x10` for `electrical.type in
  ("EEPROM","Flash/EEPROM")`, and `convert_to_programmer`
  ([database.py:596](../../../firestarter_app/firestarter/database.py#L596))
  reads that. So `FLAG_CAN_ERASE` may **already be partially set** today via that
  indirection. The fix should make the derivation **explicit and canonical**
  (read `electrical.type`/`electrical-type` directly in `convert_to_programmer`)
  rather than rely on the fragile synthetic-`info_flags` round-trip — and verify
  the actual current-state behavior for the 8 chips before/after.

### Claude's Discretion
- Exact placement/shape of the `convert_to_programmer` edit and the regression
  test (file, fixture style) — planner's call, consistent with existing patterns.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & requirements
- `.planning/ROADMAP.md` §"Phase 77: Erase Write-Path Graduation" — goal + 4 locked success criteria
- `.planning/REQUIREMENTS.md` — ERASE-01, ERASE-02, SAFE-01, SAFE-02, SAFE-03 (lines 12–16, 38–40)
- `.planning/research/SUMMARY.md` §999.4 + Feature Landscape — host-only erase-wiring finding (lines 10–12, 30, 38)

### The decode chain (the heart of this phase)
- `firestarter_app/tools/build_db.py` lines 607–643 — Pass-2 `_etype` re-derivation: for proto 0x07/0x08/0x0B, `flags & 0x10` → `"EEPROM"` else `"UV-EPROM"`; 0x0D/0x05/0x06/0x10 → `"Flash/EEPROM"`. **This is the canonical `MP_ERASE_MASK` → `electrical.type` decode D-01 relies on.**
- `firestarter_app/firestarter/database.py` — `_map_data` (line ~434: synthetic `info_flags |= 0x10` for EEPROM/Flash-EEPROM; carries `electrical-type`) + `convert_to_programmer` (line ~562; flags calc at ~592–600 — **the edit site**)
- `.planning/phases/56-*/` field-dictionary work + `firestarter_app/doc/protocol-flags.md` — flag bit 4 (0x10) = `can_erase` (`MP_ERASE_MASK`), the source-grounded semantics

### Safety gates & constants
- `firestarter_app/tools/check_dispatch.py` — full-DB VPP-safety gate (SAFE-02); must stay green
- `firestarter_app/firestarter/constants.py` ↔ `firestarter/include/firestarter.h` — `FLAG_CAN_ERASE` (0x02) parity (SAFE-03)
- `firestarter_app/firestarter/chip_resolver.py` — `resolve_chip` host guard (confirm the 8 chips are NOT refused → SAFE-01 N/A here)
- Firmware `eprom_write_init` (`firestarter/`) — already honors `FLAG_CAN_ERASE`; + `configure_eeprom28c` (verify it ignores the flag, per D-03)

### Standing bench precondition (EVERY hardware task)
- `.planning/ROADMAP.md` §v1.14 "Standing bench precondition" — Leonardo is the ONLY trustworthy write/verify board (v1.9 read bug); uno328pb N/A (brownout); chip-OUT before any Uno-class sideload (**Leonardo exempt**); **ASK which silkscreen shield rev is mounted** (EEPROM byte can't distinguish Rev 2.2 / 2.0 / Modified Rev 0); re-verify `controller:` port identity per task; live `r1 ≈ 270000` reconcile; 14V erase-rail chip-OUT VPP multimeter dry-run first, measured VPP recorded.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `convert_to_programmer` already computes a `simple_flags` and sets `FLAG_CAN_ERASE` — the edit is to change its *source* from `info-flags & 0x10` to the canonical `electrical-type`, not to add new plumbing.
- The decode in `build_db.py` (lines 607–643) already produces the authoritative `electrical.type` from `flags & 0x10`; no rebuild-pipeline change needed for D-01.
- Existing `ack_data=False` INIT/END handling (host write path, fix `fcf7974`) is the surface the D-07 regression test pins.

### Established Patterns
- Host↔firmware constant parity is a hard CI/CLAUDE.md rule — touching `FLAG_*` means lockstep `constants.py` ↔ `firestarter.h` + parity tests (SAFE-03).
- `check_dispatch.py` is the standing VPP-safety regression gate run after any DB/dispatch-affecting change (SAFE-02).
- Tooling gate: `ruff check` + `ruff format --check` + `mypy` (strict on the 8 modules) + `pytest --cov-fail-under=70`. NOTE the devcontainer Python 3.12 masks CI py3.9/3.11 — validate ruff against the target before claiming green.

### Integration Points
- `electrical.type` (DB) → `_map_data` `electrical-type` / `info-flags` → `convert_to_programmer` `flags` → wire JSON `flags` → firmware `eprom_write_init` `FLAG_CAN_ERASE` guard → auto-erase before program.
</code_context>

<specifics>
## Specific Ideas

- Operator's framing of the flag source is the load-bearing decision: **"the flag is set according to infoic.xml, where `_etype` derived from `flags & 0x10` (`MP_ERASE_MASK`) — the correct derivation."** Honor the canonical erase mask end-to-end; `electrical.type` is its faithful, protocol-disambiguated proxy.
- Bench chip is a real W27C512, started non-blank (so the auto-erase is actually exercised, not a no-op on an already-blank part).
</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (Phases 78–80 cover the other three v1.14 gaps; v1.9 covers the read-bug RCA.)
</deferred>

---

*Phase: 77-erase-write-path-graduation-0x07-ee-eproms*
*Context gathered: 2026-06-21*
