# Requirements: Firestarter — v1.40 Program-Parameter Fidelity

**Defined:** 2026-09-18
**Milestone:** v1.40 — "Ask the chip for what its datasheet says, or say plainly that you cannot"
**Core Value (this milestone):** Every programming parameter the host sends is either what
`infoic.xml` decodes to, or a datasheet value recorded in one readable override file — and when the
shield cannot deliver what a part needs, the operator is told before the attempt, not after the
failure.

**Scope:** The database generator (`firestarter_app/tools/build_db.py`) and one new data file beside
it; the host surfaces that report voltages and warn; and one firmware change in the write-init blank
check. No protocol dispatch changes. No new chip is added — `tools/extra_chips.json` keeps that job.

**Provenance:** Three community reports, each carrying a datasheet the reporter attached, proved that
the parameters are wrong at fleet scale rather than per chip:
[gh#66](https://github.com/henols/firestarter/issues/66) (MBM27C4001 — VPP below the family floor),
[gh#70](https://github.com/henols/firestarter/issues/70) (MBM27C1000 — a program pulse five times
shorter than the datasheet minimum), and
[gh#71](https://github.com/henols/firestarter/issues/71) (MBM27128 — needs 21 V where the VPP rail
measured 17.8 V and the VPE rail measured 22.7 V). Measured against the live 746-row database:
**217 of the 297 algorithm 7/8 rows carry `pulse_duration_us: 100`**, **563 of 746 rows carry
`vpp_mv: 12000`**, and **30 rows ask for 18 V or more — 8 of them 21–25 V — every one of them
`support_status: supported`**.

## Decisions taken at activation (operator, 2026-09-18)

| | Decision |
|---|---|
| **D-1** | **`infoic.xml` is the baseline for everything.** Nothing part-specific may be hardcoded in the generator. A hardcode is permitted only where there is provably no alternative, and it must carry the proof that no alternative exists. |
| **D-2** | **Decode tables are not corrections.** `VPP_MV`, `VCC_VOLTAGES` and `PROTOCOL_MAP` stay in code: they *are* the reader of infoic's own encoding. What moves out is every value that contradicts what infoic decodes to. |
| **D-3** | **Datasheet findings live in one override file holding only the changed fields.** No whole rows, no restated infoic values, so the file stays small enough for a person to read and see the full picture. Sibling to `tools/extra_chips.json`, which adds chips absent from infoic; this one corrects chips present in it. |
| **D-4** | **When the shield cannot reach the voltage a part needs, do the best that can be done and warn.** If the deliverable maximum is high enough, attempt the operation with a warning that names both numbers. A silent refusal and a silent attempt are both wrong; the operator decides with the numbers in front of them. |
| **D-5** | **Voltage-reading calibration stays out of scope** (derived from D-4, not chosen by the operator against it). Backlog 999.38's ~+7.5 % ratiometric VPP ADC error and the dormant white-box bandgap/divider calibration seed stay filed. A warn-and-attempt policy does not need a calibrated ADC; a refusal threshold would have. |
| **D-6** | **Phase numbering continues at 197.** v1.39 ran 194–196. The vacated 150 slot and the v1.24–v1.29 version slots stay unreused so every by-number cross-reference keeps resolving. |

## v1 Requirements

### OVR — one readable override file, and no part-specific constants in the generator (D-1, D-2, D-3)

- [x] **OVR-01**: A single override file beside `tools/extra_chips.json` carries per-part field
      overrides, and the generator applies them on top of the `infoic.xml` decode.
- [x] **OVR-02**: An entry holds only the fields that differ from the decoded value. A field whose
      override equals what infoic decodes to is not an entry.
- [ ] **OVR-03**: Every entry names the datasheet it comes from and the decoded value it replaces, so
      a reader sees what changed and why without running the generator.
- [x] **OVR-04**: The generator fails closed on an override it cannot apply — an unknown part number,
      an unknown field, or an override that has become a no-op because the decode now agrees with it.
- [x] **OVR-05**: The three part-specific corrections currently hardcoded in `build_db.py`
      (`NMOS_TRUE_VPP_MV`, `_AT28C_DIP24_NAMES`, and the relabel map) move into the override file,
      and the generated database is unchanged by the move.
- [x] **OVR-06**: Any constant that remains part-specific in the generator after OVR-05 is named, with
      the reason no alternative exists. An empty list is the expected answer.

### PULSE — the program pulse is the one the datasheet asks for (gh#70)

- [x] **PULSE-01**: What `pulse_delay` encodes is established per algorithm family from evidence, and
      the finding is written down — including whether the generator's current "microseconds for all
      protocols" reading survives contact with the datasheets.
- [x] **PULSE-02**: `MBM27C1000`'s program pulse falls inside its datasheet window (475–525 µs) in the
      generated database.
- [x] **PULSE-03**: The regeneration diff is measured across all 746 rows, and no row changes value
      without either a decode rule that explains it or an override that cites a datasheet for it.
- [ ] **PULSE-04**: gh#70 is answered on the issue with the resulting values and the version carrying
      them.

### VOLT — the programming voltage clears the part's own floor (gh#66)

- [x] **VOLT-01**: What the two voltage nibbles encode is established per algorithm family — the
      unproven question that has blocked the 28-row `vcc_mv: 5500` group since v1.32 Phase 148.
- [x] **VOLT-02**: The Fujitsu 1 Mbit and 4 Mbit parts ask for a VPP at or above their datasheet floor
      of 12.2 V, rather than the 12.0 V that reads as in-band under the accepted window while sitting
      below the part's own minimum.
- [x] **VOLT-03**: The 28 rows reporting 5.5 V either report their real operating voltage or are left
      unchanged with the reason recorded. Leaving them unproven and unchanged is an acceptable outcome;
      changing them on an unproven assumption is not.
- [ ] **VOLT-04**: gh#66 is answered on the issue with the resulting values and the version carrying
      them.

### RAIL — what the shield can actually deliver, and what it does when that is not enough (D-4, gh#71)

- [ ] **RAIL-01**: The deliverable maximum of the VPP and VPE rails is established at the socket per
      shield revision and recorded, with the method named — a meter reading and an ADC reading are not
      interchangeable, and an ADC-derived figure carries its known error.
- [ ] **RAIL-02**: The generator's `RURP_VPP_CEILING_MV = 25000` is either replaced by a measured
      figure or kept with its status recorded as theoretical, and the 30 rows asking 18 V or more are
      classified against whichever figure stands.
- [ ] **RAIL-03**: When a part's required VPP exceeds what the shield can deliver, the operation
      proceeds with a warning that names the required voltage and the deliverable one. It does not
      refuse silently, and it does not attempt silently.
- [ ] **RAIL-04**: Where the VPE rail is the only one that reaches a part's requirement, the routing
      decision is made and recorded — including a decision not to route it.
- [ ] **RAIL-05**: gh#71 is answered on the issue, whichever way RAIL-04 goes.

### VCC — an elevated programming supply is stated, not silently dropped

- [ ] **VCC-01**: A part that needs a programming VCC above the shield's fixed 5.0 V says so where the
      operator will see it, rather than carrying a decoded `vdd_mv` that nothing applies.
- [ ] **VCC-02**: That statement uses the same warning shape as RAIL-03, so one fact does not get two
      explanations.

### BLANK — a partial write is gated on the region it writes (backlog 999.44, firmware half)

- [ ] **BLANK-01**: The write-init blank check applies to the region being written, not to the whole
      device, so a non-erasable part holding data outside the target region accepts a write into a
      blank region.
- [ ] **BLANK-02**: `mem_util_blank_check`'s whole-device behaviour is unchanged for its other two
      callers — the standalone blank-check command and the erase-end check — and the multi-call
      chunking contract through `blank_check_saved_address` still resumes correctly.
- [ ] **BLANK-03**: A UV part holding data outside the target slot accepts a slot write, proved by the
      regression test whose absence is why this shipped.

## Future Requirements

Tracked, not in this milestone.

| ID | Requirement | Why deferred |
|---|---|---|
| **OVR-F1** | The database records, per field, whether the value came from infoic or from an override, and `info` can show it | The override file already answers this for a reader; a per-field provenance channel on the wire is a separate design |
| **CAL-F1** | White-box bandgap and divider calibration so the board's own voltage readings are trustworthy | D-5 — the warn-and-attempt policy does not need it; seed `voltage-reading-whitebox-calibration` stays dormant, 999.38 stays filed |
| **VOLT-F1** | The remaining families touching `VCC_VOLTAGES[0x04]` beyond the 28 rows | Only if VOLT-01 proves the nibble semantics generalise |

## Out of Scope

| Feature | Reason |
|---------|--------|
| Adding chips absent from `infoic.xml` | `tools/extra_chips.json` already owns that, and this milestone corrects rows that exist |
| Hand-editing `chip_database.json` | It is generated. A wrong value is a decode fault or a missing override, never a row to patch |
| Protocol dispatch changes | The algorithm axis is settled; this milestone changes parameters, not paths |
| The SST39SF040 write stall (gh#86/#90) and the 62256 read divergence (gh#83) | Undiagnosed, and neither is a parameter fault — investigation work, not this milestone |
| Voltage-reading calibration | D-5 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| OVR-01 | Phase 197 | Complete |
| OVR-02 | Phase 197 | Complete |
| OVR-03 | Phase 197 | Pending |
| OVR-04 | Phase 197 | Complete |
| OVR-05 | Phase 197 | Complete |
| OVR-06 | Phase 197 | Complete |
| PULSE-01 | Phase 197 | Complete |
| PULSE-02 | Phase 197 | Complete |
| PULSE-03 | Phase 197 | Complete |
| PULSE-04 | Phase 197 | Pending |
| VOLT-01 | Phase 198 | Complete |
| VOLT-02 | Phase 198 | Complete |
| VOLT-03 | Phase 198 | Complete |
| VOLT-04 | Phase 198 | Pending |
| RAIL-01 | Phase 199 | Pending |
| RAIL-02 | Phase 199 | Pending |
| RAIL-03 | Phase 199 | Pending |
| RAIL-04 | Phase 199 | Pending |
| RAIL-05 | Phase 199 | Pending |
| VCC-01 | Phase 200 | Pending |
| VCC-02 | Phase 200 | Pending |
| BLANK-01 | Phase 201 | Pending |
| BLANK-02 | Phase 201 | Pending |
| BLANK-03 | Phase 201 | Pending |

**Coverage:**

- v1 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-18*
*Last updated: 2026-09-18 at milestone activation*
