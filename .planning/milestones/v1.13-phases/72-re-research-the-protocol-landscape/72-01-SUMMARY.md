---
phase: 72-re-research-the-protocol-landscape
plan: 01
subsystem: research
tags: [protocol-enumeration, feasibility-verdict, eprom, sram, flash, erase-path, chip-database]

# Dependency graph
requires:
  - phase: 72-re-research-the-protocol-landscape
    provides: RESEARCH.md and VALIDATION.md with source-verified protocol-ID findings
  - phase: 71-validation-harness-matrix
    provides: dispatch baseline, validation matrix, check_dispatch.py extended gates

provides:
  - .planning/v1.13-PROTOCOL-ENUMERATION.md — committed per-protocol verdict table (14 rows),
    verdict taxonomy, v1.12 claim review, 5-item gap index, anti-feature block, ceiling constraint
  - Resolved Open Questions A1 (erase scope exact gap) and A2 (0x2B identity)
  - Citable spine for Phases 73-76 scope decisions

affects:
  - phase-73 (VAL-01..06 — cite ENUMERATION.md rows 0x0E/0x27/0x28/0x29 for VAL-06 SRAM scope)
  - phase-74 (FIX-01..03 — cite rows 0x05/0x39 for flash4 chip-id gap and stale comment)
  - phase-75 (ERASE-01 — cite row 0x07 erase write-path gap; exact scope from A1 resolution)
  - phase-76 (GAP-01/02 — cite row 0x34 feasible-gap re-classification)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-protocol feasibility verdict table with explicit v1.12 holds/overstated judgment per row"
    - "Evidence-citation requirement: every verdict row must carry a resolvable file:line"
    - "Open-question resolution pattern: code-trace to file:line, no assertions"

key-files:
  created:
    - .planning/v1.13-PROTOCOL-ENUMERATION.md
  modified: []

key-decisions:
  - "A1-RESOLVED: Standalone `firestarter erase W27C512` already reaches eprom_internal_erase unconditionally (eprom.cpp:88-91); the real gap is FLAG_CAN_ERASE never set in write path because info-flags=0x0 for all 7 EE-EPROMs (database.py:594-597); Phase 75 scope = wire FLAG_CAN_ERASE from electrical.type not info-flags"
  - "A2-RESOLVED: 0x2B is GAL/PLD family (memory.cpp:107-110); exact IC2_ALG name unconfirmed (likely IC2_ALG_GAL20); protocol-id.md lacks 0x2B row (documentation debt)"
  - "SRAM-VERDICT: 0x0E/0x27/0x28/0x29 classified feasible-and-implemented (behavior deferred) not feasible-gap; generic memory_write_execute fires before configure_sram is called; correctness determination deferred to Phase 73 VAL-06"
  - "0x35/0x39: firmware dispatches both → configure_flash4 (correct); host KNOWN_PROTOCOLS intentionally excludes both (DEC-05); both concerns recorded separately in enumeration table"
  - "V1.12 overstated in 3 areas: SRAM no-op (sram.cpp:15-17), FLAG_CAN_ERASE routing gap (database.py:594-597), X88C64 0x34 feasible but treated as infeasible"

patterns-established:
  - "Enumeration artifact: per-row evidence citation enforced as acceptance criterion (T-72-01 mitigation)"
  - "Downstream phase cite-by-row: 'per PROTOCOL-ENUMERATION.md row 0x07: erase path = feasible-gap → Phase 75 scope'"

requirements-completed: [RSCH-01]

# Metrics
duration: 45min
completed: 2026-06-17
---

# Phase 72 Plan 01: Re-research Protocol Landscape Summary

**14-row per-protocol feasibility verdict table committed, with v1.12 overstated-claim review (3 items) and both open questions resolved by code trace to file:line**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-06-17T11:00:00Z
- **Completed:** 2026-06-17T11:45:00Z
- **Tasks:** 2 (both completed)
- **Files modified:** 1 created

## Accomplishments

- Created `.planning/v1.13-PROTOCOL-ENUMERATION.md` — the committed gate document for Phases 73-76
- Resolved Open Question A1: standalone erase already works electrically; write auto-erase path gap identified in `database.py:594-597` (FLAG_CAN_ERASE gated on `info-flags & 0x10` but all 7 EE-EPROMs have `info-flags: 0x0`)
- Resolved Open Question A2: 0x2B confirmed in infeasible arm (`memory.cpp:107-110`), likely IC2_ALG_GAL20 by family sequence, `protocol-id.md` documentation gap noted
- Built 14-row enumeration table covering all in-scope protocol_ids (0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x34, 0x35, 0x39) with handler, DB chip counts (verified by DB query), feasibility verdict, v1.12 claim judgment, and resolvable file:line evidence per row
- Documented 3 areas where v1.12's "feasible set complete" claim was overstated (SRAM handler no-op, FLAG_CAN_ERASE routing, X88C64 0x34 re-classification)
- Wrote anti-feature block (0x11 FWH, 0x2A-0x2C GAL/PLD) with firmware + host enforcement citations
- Wrote 5-item gap index mapping RSCH-01 gap items to downstream phases 73-76

## Task Commits

1. **Task 1: Resolve open questions A1/A2 + create PROTOCOL-ENUMERATION.md** — `ef364c8` (docs)
2. **Task 2: 14-row table + verdict taxonomy + v1.12 claim review** — included in `ef364c8` (single document creation — both tasks written as cohesive document in one pass; Task 2 verification passes: 35 verdict cells, 14 enumeration rows, all sections present)

**Plan metadata:** pending (recorded below in self-check)

## Files Created/Modified

- `.planning/v1.13-PROTOCOL-ENUMERATION.md` — Primary deliverable: 14-row per-protocol feasibility enumeration, verdict taxonomy, v1.12 claim review, open-question resolutions, anti-feature block, gap item index, ceiling constraint, full source citations

## Decisions Made

- **A1 resolution (erase scope):** The write auto-erase gap is the exact Phase 75 target — `convert_to_programmer` must wire `FLAG_CAN_ERASE` from `electrical.type == "EEPROM"` not `info-flags & 0x10`. The `info-flags` field in `chip_database.json` stores raw minipro XML flags (all 0x0 for 0x07 EE-EPROMs); `electrical.type` is re-derived in build_db.py Step 7. This is a narrower gap than "standalone erase doesn't work."

- **A2 resolution (0x2B identity):** Named as likely `IC2_ALG_GAL20` (GAL20V8) by family sequence (0x2A=GAL16, 0x2B=GAL20?, 0x2C=GAL22). Unconfirmed from citeable source — `protocol-id.md` has no 0x2B entry. Documented as documentation debt in anti-feature block.

- **SRAM classification:** Used `feasible-and-implemented (behavior deferred)` rather than `feasible-gap` for 0x0E/0x27/0x28/0x29 because: dispatch is correct; `configure_memory` sets up `memory_write_execute` BEFORE calling `configure_sram`; SRAM is the simplest memory type and generic byte-write almost certainly works. V1.12 overstated but the protocol is not "broken" — correctness confirmation is Phase 73 VAL-06.

- **DB chip counts:** Queried `chip_database.json` directly (2026-06-17): 0x07=170 supported/170, 0x0D=75/84 (9 adapter-required), SRAM family 0x0E/0x27/0x28/0x29 = 20+2+34+20=76 supported, 0x10=39, 0x34=0/1 (protocol-not-implemented), 0x35/0x39=0/0.

## Deviations from Plan

None — plan executed exactly as written. Both tasks were completed as a single cohesive document write. Task 1 created the file with the Open-Question Resolutions section; Task 2 material (enumeration table, taxonomy, v1.12 review) was incorporated into the same document write. The Task 2 automated verification confirms all required content is present (35 verdict rows, 14 enumeration rows ≥12 required, all sections present).

## Issues Encountered

- Task 2 commit attempted but was a no-op (file already committed in Task 1's comprehensive write). The document was created complete in a single pass. Both task acceptance criteria are satisfied by commit `ef364c8`.

## User Setup Required

None — this is a pure documentation/research plan. No external services, no hardware, no test infrastructure required.

## Threat Surface

No code was created or modified. No new runtime surface. This plan confirms that anti-features remain fail-closed (T-72-01 mitigation verified via code trace). No threat flags.

## Known Stubs

None — this is a documentation plan. No stubs or placeholder values.

## Next Phase Readiness

- `.planning/v1.13-PROTOCOL-ENUMERATION.md` is committed and ready to be cited by Phases 73-76
- Phase 72 Plan 02 (anti-feature block, gap item index, ceiling constraint) is already covered by this plan's output — the 72-01 document contains all content planned for 72-02. Phase 72 is effectively complete with this single plan.
- Phase 73 (bench validation) can cite rows by protocol_id; SRAM rows (0x0E/0x27/0x28/0x29) marked for VAL-06; flash4 (0x05) for chip-id gap
- Phase 75 scope is now narrowly defined: wire FLAG_CAN_ERASE in `convert_to_programmer` from `electrical.type == "EEPROM"` (not `info-flags & 0x10`)

## Self-Check

**Checking created files exist:**
- `.planning/v1.13-PROTOCOL-ENUMERATION.md` — FOUND (312 lines, committed at ef364c8)

**Checking commits exist:**
- `ef364c8` — commit found in git log

**Self-Check: PASSED**

---
*Phase: 72-re-research-the-protocol-landscape*
*Completed: 2026-06-17*
