---
phase: 56-snapshot-field-dictionary-corrected-docs
plan: "02"
subsystem: firestarter_app/doc
tags: [documentation, field-dictionary, infoic, decode-correctness, v1.11]
dependency_graph:
  requires: ["56-01"]
  provides: ["firestarter_app/doc/infoic-field-dictionary.md"]
  affects: ["Phase 57 bug-fix code", "Phase 59 GATE-02 regression diff"]
tech_stack:
  added: []
  patterns: ["minipro GitLab permalink citations pinned to single SHA", "CONFIRMED/INFERRED/UNKNOWN attribute confidence markers"]
key_files:
  created:
    - firestarter_app/doc/infoic-field-dictionary.md
  modified: []
decisions:
  - "D-06: Single citation SHA a8efaedc236c1d9718bd28299dfbb99536b010ff at top of file; all 13 attribute permalinks reuse it"
  - "D-11: BUG-1..4 documented with correct semantics and Phase-57-deferral wording; no build_db.py decode changes in this plan"
  - "bits 3/6/7 of flags explicitly marked UNKNOWN (not INFERRED) — no MP_* constant in database.c lines 39-50"
metrics:
  duration: "~20 minutes"
  completed: "2026-06-08"
  tasks_completed: 1
  tasks_total: 1
  files_created: 1
  files_modified: 0
---

# Phase 56 Plan 02: Write infoic-field-dictionary.md Summary

Created `firestarter_app/doc/infoic-field-dictionary.md` — authoritative source-cited field dictionary covering all 13 in-scope `infoic.xml` attributes with CONFIRMED/INFERRED/UNKNOWN markers, pinned minipro citation SHA, and four confirmed bug entries (BUG-1..4) stating correct decode semantics with Phase-57-deferral wording.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Write infoic-field-dictionary.md with all 13 attributes, citation SHA, and bug semantics | `6f45456` | `firestarter_app/doc/infoic-field-dictionary.md` (created, 288 lines) |

## Verification

### Automated Check (DICT_OK)

```
cd /workspaces/firestarter_app && test -f doc/infoic-field-dictionary.md \
  && grep -q "a8efaedc236c1d9718bd28299dfbb99536b010ff" doc/infoic-field-dictionary.md \
  && N=$(grep -c -E '^### `(package_details|type|variant|protocol_id|flags|voltages|pin_map|pulse_delay|chip_id|code_memory_size|page_size|chip_info|blank_value)`' doc/infoic-field-dictionary.md) \
  && [ "$N" -eq 13 ] \
  && grep -qE "MP_ERASE_MASK" doc/infoic-field-dictionary.md \
  && grep -qE "UNKNOWN" doc/infoic-field-dictionary.md \
  && grep -qE "IC2_ALG_GAL16" doc/infoic-field-dictionary.md \
  && grep -qE "4V|0x02" doc/infoic-field-dictionary.md \
  && echo DICT_OK
```

Result: **DICT_OK**

### Acceptance Criteria

- [x] `test -f firestarter_app/doc/infoic-field-dictionary.md` — file exists (288 lines, >= 120)
- [x] Citation SHA `a8efaedc236c1d9718bd28299dfbb99536b010ff` present at top of file
- [x] Exactly 13 H3 attribute headings — grep count = 13
- [x] `MP_ERASE_MASK` present — bit 4 documented as WARNING-5 discriminator
- [x] `UNKNOWN` present — bits 3/6/7 explicitly marked UNKNOWN
- [x] `IC2_ALG_GAL16` present — BUG-4 canonical names + exclusion rationale
- [x] VCC nibbles `0x02=4V` and `0x03=4.5V` documented (BUG-1)
- [x] `vdd=>>12` / `vcc=>>8` correct positions documented (BUG-3)
- [x] `pulse_delay` = raw µs no multiplier documented (BUG-2)
- [x] Each bug entry phrased "correct is X; current build_db.py does Y; fix deferred to Phase 57"
- [x] `build_db.py` and `chip_database.json` unchanged — `git diff --name-only` returns empty
- [x] Line 1 is verbatim logo-header block; line 3 is `---`

## Content Summary

The dictionary covers all 13 in-scope attributes:

| Attribute | Type | Confidence | Bug? |
|-----------|------|------------|------|
| `package_details` | uint32 hex | CONFIRMED | No |
| `type` | uint32 hex | CONFIRMED | No |
| `variant` | uint32 hex | CONFIRMED | No |
| `protocol_id` | uint8 hex | CONFIRMED | BUG-4 |
| `flags` | uint32 hex | CONFIRMED (decoded bits) / UNKNOWN (bits 3/6/7) | No (bits 3/6/7 UNKNOWN, not INFERRED) |
| `voltages` | uint32 hex | CONFIRMED | BUG-1, BUG-3 |
| `pin_map` | uint32 hex | CONFIRMED | No |
| `pulse_delay` | uint32 hex | CONFIRMED | BUG-2 |
| `chip_id` | uint32 hex | CONFIRMED | No |
| `code_memory_size` | uint32 hex | CONFIRMED | No |
| `page_size` | uint32 hex | CONFIRMED | No |
| `chip_info` | uint32 hex | CONFIRMED | No |
| `blank_value` | uint8 hex | CONFIRMED | No |

## Bug Documentation (BUG-1..4)

Each bug is phrased: "correct decode is X; current build_db.py does Y; fix deferred to Phase 57."

- **BUG-1 (DEC-04):** VCC nibble table — correct: complete 6-entry table `0x00=5V, 0x01=3.3V, 0x02=4V, 0x03=4.5V, 0x04=5.5V, 0x05=6.5V`; `build_db.py VCC_VOLTAGES` missing `0x02` and `0x03`.
- **BUG-2 (DEC-03):** `pulse_delay` — correct: raw value is µs for ALL protocols, no transformation; `build_db.py interpret_timing()` applies ×100 for `0x07` and `0x0B` (252 chips affected).
- **BUG-3 (DEC-04):** Voltage field positions — correct: `vdd=(>>12)`, `vcc=(>>8)`; `build_db.py` lines 510–511 have labels swapped.
- **BUG-4 (DEC-05):** `protocol_id` canonical names — correct: `IC2_ALG_*` from `database.h#L24`–`L77`; `0x2A=IC2_ALG_GAL16`, `0x2C=IC2_ALG_GAL22`, `0x2E=IC2_ALG_PIC32X_2`, `0x35=IC2_ALG_ITE`, `0x39`=phantom, `0x3C`=invented.

## Deviations from Plan

None — plan executed exactly as written. `build_db.py` and `chip_database.json` are unchanged.

## Known Stubs

None — all 13 attributes are fully populated with source citations and build_db.py usage notes.

## Threat Flags

None — this plan adds only a markdown reference document. No new network endpoints, auth paths, file access patterns, or schema changes.

## Self-Check: PASSED

- `firestarter_app/doc/infoic-field-dictionary.md` exists: FOUND
- Commit `6f45456` exists on `v1.11-infoic-decode-correctness` branch: FOUND
- DICT_OK grep: PASSED
- build_db.py unchanged: CONFIRMED (git diff empty)
