# Phase 77: Erase Write-Path Graduation (0x07 EE-EPROMs) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-21
**Phase:** 77-erase-write-path-graduation-0x07-ee-eproms
**Areas discussed:** Erase-flag scope, Bench acceptance rigor, SAFE-01 framing, 0xA4 regression guard

---

## Erase-flag scope (initial decision)

| Option | Description | Selected |
|--------|-------------|----------|
| 0x07 EEPROMs only | FLAG_CAN_ERASE for electrical.type=='EEPROM' AND protocol_id==0x07; narrowest blast radius | |
| All electrical.type=='EEPROM' | Set for every EEPROM regardless of protocol | |

**User's choice:** Free-text — *"I expected the flag is set accordingly to what the infoic.xml, where `_etype` derived from `flags & 0x10` (`MP_ERASE_MASK`) — correct derives from."*

**Notes:** User reframed the question: the source of truth is the canonical infoic.xml erase mask `flags & 0x10` (`MP_ERASE_MASK`), and `electrical.type` is *derived from* that mask, so neither a protocol heuristic nor a bare type-string match — follow the canonical decode. Confirmed against `build_db.py:607–643` (Pass-2 `_etype`: for 0x07/0x08/0x0B, `flags & 0x10` → "EEPROM"). Roadmap's "always-zero info-flags & 0x10" was identified as referring to the runtime `_map_data` synthetic field, not the build_db `flags` ground truth → captured as research flag RF-01.

## Erase-flag reach (follow-up)

| Option | Description | Selected |
|--------|-------------|----------|
| configure_eprom EEPROMs only | Flag only for electrical.type=='EEPROM' (0x07/0x08/0x0B path) where firmware consumes it | |
| All erasable (EEPROM + Flash/EEPROM) | Flag wherever the canonical mask says erasable, incl. 0x0D Flash/EEPROM | ✓ |

**User's choice:** All erasable (EEPROM + Flash/EEPROM)
**Notes:** Uniform with the mask semantics. Flag is inert on the 0x0D `configure_eeprom28c` path → added mandatory downstream verification (D-03) that the firmware genuinely ignores it there (no double-erase / hazard for 28C parts).

---

## Bench acceptance rigor

| Option | Description | Selected |
|--------|-------------|----------|
| Single cycle (per SC#2) | One no-`-b` write of a non-blank W27C512 + independent SHA-match read + non-vacuous negative control | ✓ |
| N>=5 repeated cycles | Repeat full write+verify N>=5× for byte-identity (SAFE read rigor) | |

**User's choice:** Single cycle (per SC#2)
**Notes:** Matches the locked SC#2; N≥5 reserved for read-acceptance elsewhere.

---

## SAFE-01 framing here

| Option | Description | Selected |
|--------|-------------|----------|
| Document N/A-no-refusal + keep gate | Record SAFE-01 host-guard removal as N/A (chips already supported); FLAG_CAN_ERASE wiring is the evidence-gated final step; SAFE-02/03 still apply | ✓ |
| Treat the -b workaround as the 'refusal' | Frame removing the need for `-b` as the graduation, gate the wiring as final step | |

**User's choice:** Document N/A-no-refusal + keep gate
**Notes:** The 8 chips were confirmed `support_status: supported` in chip_database.json during scout — no `chip_resolver` refusal exists to remove.

---

## 0xA4 regression guard

| Option | Description | Selected |
|--------|-------------|----------|
| Add explicit regression test | Host test asserting default no-`-b` auto-erase write keeps ack_data=False on INIT/END DATA frames | ✓ |
| Bench-confirm only | Rely on SC#2 bench cycle without a dedicated unit test | |

**User's choice:** Add explicit regression test
**Notes:** Cheap insurance on the known-fragile default-write blank-check path (0xA4 desync resolved 2026-06-17, commit fcf7974).

---

## Claude's Discretion

- Exact placement/shape of the `convert_to_programmer` edit and the regression-test fixture style — planner's call, consistent with existing patterns.

## Deferred Ideas

None — discussion stayed within phase scope.
