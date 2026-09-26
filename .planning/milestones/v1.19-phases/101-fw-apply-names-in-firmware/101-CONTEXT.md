# Phase 101: FW — Apply Names in Firmware - Context

**Gathered:** 2026-07-01
**Status:** Ready for planning
**Source:** Operator decisions captured during /gsd-plan-phase (research-informed, discuss-phase skipped)

<domain>
## Phase Boundary

Apply the operator-approved canonical protocol name set (from Phase 100) inside the
firmware. This is a **rename/relabel-only** phase: define `PROTO_<NAME>` constants for
every protocol number (numeric values unchanged — the label *is* the number), relabel the
raw-hex dispatch chain in `firestarter/src/proms/memory.cpp` to those named constants, and
confirm the many-to-one handler files/functions conform to the approved family-name layer.
Dispatch order, behavior, and every numeric value stay identical. No CLI change (GATE-03).
No `chip_database.json` change and no wire/lockstep-constant value change (GATE-02).

</domain>

<decisions>
## Implementation Decisions

### FW-03 handler naming — conformance-confirm, not wholesale rename
- **D-01:** FW-03 is satisfied by **confirming conformance** of the existing family handler
  files/functions to Phase 100's approved family-name layer, NOT by a wholesale rename.
  Research verified Phase 100's approved family names ARE the already-existing names
  (`configure_eprom`/`eprom.cpp`, `configure_flash4`/`flash_type_4.cpp`, `configure_eeprom28c`,
  the SRAM/EPROM family handlers). A literal rename would touch 100+ references and re-open
  Phase 100. Rename ONLY any handler that does not already match the approved layer; assert
  the rest conformant. Groupings are not split.

### PROTO_<NAME> constant home — firmware-only
- **D-02:** The `PROTO_<NAME>` constants live **only in the firmware** (a constant home in
  `firestarter/include/`). They are NOT mirrored into host `firestarter_app/constants.py`.
  Host `constants.py` currently has ZERO protocol constants and the constants-parity test
  asserts none — keeping firmware-only holds parity green with no change, keeps GATE-02
  (no lockstep-constant value change) trivially satisfied, and sidesteps the
  py3.12-masks-CI-py3.11 trap.

### Dispatch-mirror guard — fix the parser in-scope (Wave 0)
- **D-03:** The pre-existing RED `firestarter_app/tests/test_dispatch_mirror.py` guard
  (broken by Phase 100's PROTOCOLS.md table restructure — its parser returns an empty table)
  is reconciled **in-scope** as a Wave-0 task: fix the parser against Phase 100's new
  PROTOCOLS.md table layout so GATE-01 can be honestly claimed green. The baseline is NOT
  clean; the planner must not assume a green dispatch-mirror guard.

### Phantom / infeasible tokens
- **D-04:** The 0x35/0x39 dispatch arm gets operator-approved honest, explicitly-non-real
  phantom tokens (`PROTO_PHANTOM_0x35` / `PROTO_PHANTOM_0x39`) per Phase 100. The
  0x11/0x2A/0x2B/0x2C infeasible arm has NO approved tokens — leave it as raw hex; do not
  invent names here.

### Claude's Discretion
- Exact filename/location of the new `firestarter/include/` constant home, include-guard
  naming, and comment style, following existing `firestarter.h` conventions.
- Wave/plan decomposition and task ordering, provided Wave 0 reconciles the red guard before
  the GATE verification tasks assert green.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 100 contract (the approved name set — NO naming is invented in Phase 101)
- `.planning/phases/100-*/100-SUMMARY.md` — approved canonical protocol name set + handler-family layer
- `.planning/phases/100-*/100-VERIFICATION.md` — what Phase 100 shipped/verified
- `firestarter/doc/PROTOCOLS.md` (committed `6e7bd38`) — verbatim number→`PROTO_<NAME>` map + family layer

### Firmware targets
- `firestarter/src/proms/memory.cpp` — raw-hex dispatch chain to relabel
- `firestarter/include/firestarter.h` — existing constants/flag-bit home; conventions for the new PROTO_ home
- `firestarter/src/proms/` handler files — `eprom.cpp`, `flash_type_3.cpp`, `flash_type_4.cpp`, EEPROM/SRAM family handlers

### Guards (verification depends on these — see 101-RESEARCH.md for exact commands + green-state)
- `firestarter_app/tests/test_dispatch_mirror.py` — dispatch-mirror guard (RED at baseline — D-03)
- `firestarter_app/…/check_dispatch.py` — dispatch mirror check (PASS 746)
- `firestarter_app/…/diff_db.py` — chip_database.json identity (GATE-02)
- constants-parity pytest (`constants.py` ↔ `firestarter.h`)
- `pio test -e native` (82/82) + `pio run -e uno` (build) + v1.16 golden register traces

</canonical_refs>

<specifics>
## Specific Ideas

- Verbatim ground truth (14-row number→`PROTO_<NAME>` map, full memory.cpp dispatch chain
  quoted line-by-line with the token substitution table) is captured in `101-RESEARCH.md`.
- If any golden register trace re-pin is needed, it must be a purely-cosmetic token change
  with cited rationale (dispatch order/behavior unchanged).

</specifics>

<deferred>
## Deferred Ideas

- Accepting a protocol name/alias as CLI input (NAME-F2) — out of scope for v1.19 (GATE-03).
- Any `chip_database.json` value change / new chip becoming programmable — out of scope (GATE-02).

</deferred>

---

*Phase: 101-fw-apply-names-in-firmware*
*Context captured: 2026-07-01 during /gsd-plan-phase (research-informed operator decisions)*
