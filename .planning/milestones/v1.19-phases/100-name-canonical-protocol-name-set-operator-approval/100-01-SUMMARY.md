---
phase: 100-name-canonical-protocol-name-set-operator-approval
plan: 01
subsystem: docs
tags: [firmware, protocol-naming, documentation, v1.19]

# Dependency graph
requires:
  - phase: 87-naming-documentation-pass
    provides: "firestarter/doc/PROTOCOLS.md baseline (5-column Canonical bucket set table, §1.1-§1.12 per-bucket facet prose, §2 honest non-protocols, §3 INV-01..09 matrix)"
provides:
  - "Operator-approved 3-field canonical name set (PROTO_ token + display name + handler-family) for all 12 DB protocols + 2 phantom rows in firestarter/doc/PROTOCOLS.md"
  - "0x0E/0x29 32-pin SRAM D-05 name collision resolved with two distinct final tokens"
  - "Handler-family layer naming the 7 existing configure_* dispatch groupings"
  - "The single authoritative source Phases 101/102/103 cite by section"
affects: [101-firmware-proto-tokens, 102-host-display-names, 103-facet-prose-inv-reconciliation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Revise-in-place doc pattern: expand a single algorithm-axis column into a 3-field schema while preserving frozen slug column + facet prose verbatim"
    - "Blocking human-verify checkpoint gate for irreversible naming decisions (NAME-02 — no silent auto-approval)"

key-files:
  created: []
  modified:
    - "firestarter/doc/PROTOCOLS.md (revised in place — Region A Canonical bucket set table, §1.1-§1.12 col-2 name lines, §2.1 phantom table, footer provenance)"

key-decisions:
  - "0x0E = PROTO_SRAM_32PIN (unchanged from draft); 0x29 = PROTO_SRAM_32PIN_NVRAM (operator CHANGED from draft PROTO_SRAM_32PIN_LARGE) — resolves the D-05 32-pin SRAM name collision with two distinct tokens"
  - "Phantom tokens use hex-in-name spelling: PROTO_PHANTOM_0x35 / PROTO_PHANTOM_0x39 (operator CHANGED from draft numeric PROTO_PHANTOM_35/_39), applied consistently in both the Region-A table and the §2.1 phantom table"
  - "0x34 = PROTO_EEPROM_8051BUS (operator CHANGED from draft PROTO_EEPROM_X88C64, behavior-axis per D-03); the frozen slug 0x34-EEPROM-X88C64 and the §1.12 NAME-04 X88C64 identity-correction prose are kept VERBATIM as the intentional DOC-02 divergence anchor"
  - "Every other proposed PROTO_ token, display name, and handler-family name approved as drafted — no further changes"
  - "Operator approved the rendered table at the blocking Task-2 gate on 2026-07-01; footer records the approval date"

patterns-established:
  - "Doc-only naming/decision phases follow: draft (Task 1) -> blocking human-verify gate (Task 2) -> finalize exactly per operator decision (Task 3), with no silent auto-approval of irreversible naming choices"

requirements-completed: [NAME-01, NAME-02, NAME-03]

coverage:
  - id: D1
    description: "3-field canonical name entry (PROTO_ token + display name + handler-family) exists for all 12 DB protocols + 2 phantom rows in the Canonical bucket set table"
    requirement: "NAME-01"
    verification:
      - kind: other
        ref: "grep -c 'INV-0' firestarter/doc/PROTOCOLS.md == 34; all 14 hex ids present with PROTO_ tokens"
        status: pass
    human_judgment: false
  - id: D2
    description: "Operator explicitly approved the rendered table at a blocking gate and resolved the 0x0E/0x29 tiebreak (no silent auto-approval)"
    requirement: "NAME-02"
    verification:
      - kind: manual_procedural
        ref: "Task-2 checkpoint:human-verify gate — operator decisions captured verbatim in the plan prompt (2026-07-01)"
        status: pass
    human_judgment: true
    rationale: "NAME-02 requires an explicit human sign-off on an irreversible naming decision; this is inherently a human-judgment gate, not an automatable check."
  - id: D3
    description: "Approved name set recorded in the single authoritative source (firestarter/doc/PROTOCOLS.md, revised in place) with handler-family layer and frozen slug column retained"
    requirement: "NAME-03"
    verification:
      - kind: other
        ref: "git -C firestarter diff --stat doc/PROTOCOLS.md shows exactly one file changed; FINALIZE_OK automated verify passed"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-07-01
status: complete
---

# Phase 100 Plan 01: Canonical Protocol Name Set + Operator Approval Summary

**Operator-approved 3-field canonical protocol vocabulary (`PROTO_` token + display name + handler-family) recorded in `firestarter/doc/PROTOCOLS.md`, resolving the 0x0E/0x29 32-pin SRAM name collision with `PROTO_SRAM_32PIN` vs `PROTO_SRAM_32PIN_NVRAM`.**

## Performance

- **Duration:** ~20 min (this continuation covers Task 3 + SUMMARY only; Task 1 was executed in a prior session)
- **Completed:** 2026-07-01
- **Tasks:** 3/3 (Task 1 authored draft, Task 2 was the blocking operator-approval gate, Task 3 finalized)
- **Files modified:** 1 (`firestarter/doc/PROTOCOLS.md`)

## Context

This plan runs inside the `firestarter` submodule, on branch `v1.19-protocol-naming-labels`
(forked off `beta`; `PROTOCOLS.md` was seeded from the v1.16 tip onto this branch in commit
`9e6325a` before Task 1 authored the draft). The meta-repo tracks only `.planning/`; the
submodule commits are the actual deliverable, and the meta-repo orchestrator owns the gitlink
bump, `STATE.md`, and `ROADMAP.md` updates separately.

## Accomplishments
- Authored (Task 1, prior session) and finalized (Task 3, this session) the single
  operator-approved 3-field canonical name set for all 12 DB protocols (0x05/06/07/08/0B/0D/0E/10/27/28/29/34) plus 2 flagged phantom rows (0x35/0x39) in `firestarter/doc/PROTOCOLS.md`.
- Resolved the D-05 0x0E-vs-0x29 32-pin SRAM name collision with two distinct final tokens.
- Applied the operator's three changed-from-draft decisions exactly as specified, with no re-opening of naming.
- Preserved the §1.x four-facet prose, the §1.10/§1.12 NAME-04 identity-correction call-outs, the §2.2 infeasible-bucket table, and the §3 INV-01..09 matrix byte-for-byte (SAFE-02 grep-intact contract intact — `grep -c 'INV-0'` still returns 34).
- Removed every "PROPOSED" / tiebreak / "offer both spellings" annotation so the doc now reads as fully authoritative.
- Recorded the operator-approval date (2026-07-01) in the footer provenance line.

## Task Commits

Task 1 was executed and committed in a prior session (this executor picked up as a fresh continuation for Task 3 after the operator approved at the Task-2 gate):

1. **Task 1: Author the draft 3-field name set + phantom rows + handler-family layer** - `43a3068` (docs) — prior session
2. **Task 2: BLOCKING operator approval of the name set + 0x0E/0x29 tiebreak** - checkpoint (no commit; operator approved with 3 changes at the gate, 2026-07-01)
3. **Task 3: Finalize the operator-approved names in PROTOCOLS.md + record approval provenance** - `6e7bd38` (docs) — this session

Both commits are inside the `firestarter` submodule on branch `v1.19-protocol-naming-labels`.
No meta-repo gitlink bump was made by this executor — that is the orchestrator's responsibility.

**Plan metadata:** not committed by this executor (SUMMARY.md is left uncommitted per instruction; the orchestrator commits meta-repo docs + the gitlink bump together).

## Files Created/Modified
- `firestarter/doc/PROTOCOLS.md` - Revised in place: Region A Canonical bucket set table (3-field schema finalized), §1.1-§1.12 `**Canonical name (col 2):**` lines updated to final tokens, §2.1 phantom table finalized, footer provenance line updated with operator-approval date.

## Operator-Approved Final Names (Task 2 gate decisions applied in Task 3)

| Protocol | Draft (Task 1) | Final (operator-approved) | Changed? |
|----------|----------------|---------------------------|----------|
| 0x0E | `PROTO_SRAM_32PIN` | `PROTO_SRAM_32PIN` | No — unchanged |
| 0x29 | `PROTO_SRAM_32PIN_LARGE` (tiebreak marker) | `PROTO_SRAM_32PIN_NVRAM` | **Yes** — D-05 tiebreak resolved; display name retains the "large / 512K-1M" descriptor to stay distinct from 0x0E |
| 0x35 | `PROTO_PHANTOM_35` (offered alt `_0x35`) | `PROTO_PHANTOM_0x35` | **Yes** — hex-in-name spelling chosen, applied in both Region-A table and §2.1 |
| 0x39 | `PROTO_PHANTOM_39` (offered alt `_0x39`) | `PROTO_PHANTOM_0x39` | **Yes** — hex-in-name spelling chosen, applied in both Region-A table and §2.1 |
| 0x34 | `PROTO_EEPROM_X88C64` | `PROTO_EEPROM_8051BUS` | **Yes** — behavior-axis per D-03; frozen slug `0x34-EEPROM-X88C64` and §1.12 NAME-04 X88C64 prose kept VERBATIM (the intentional DOC-02 anchor divergence) |
| All others (0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x10, 0x27, 0x28) | as drafted | as drafted | No — approved as-is |

## Decisions Made
- Applied all three operator-directed changes exactly as specified in the Task-2 resume signal; no naming was re-opened or second-guessed.
- Kept the frozen `datasheets/<hex>-<NAME>/` slug column and §1.12 NAME-04 X88C64 call-out prose verbatim even though the 0x34 token changed — this divergence between slug and token IS the intended DOC-02 anchor per plan instructions.
- Did not touch the §3 INV matrix, the four-facet prose paragraphs, the §2.2 infeasible table, or any file under `datasheets/`.

## Deviations from Plan

None — plan executed exactly as written. All Task 3 actions matched the plan's `<action>` block and the operator's Task-2 decisions verbatim.

## Issues Encountered

None. The Task 3 automated verify check printed `FINALIZE_OK` on the first run:
- `grep -c 'INV-0' firestarter/doc/PROTOCOLS.md` == 34
- No `tiebreak` or `PROPOSED` strings remain
- 2 distinct `PROTO_SRAM_*32PIN*` tokens present (`PROTO_SRAM_32PIN`, `PROTO_SRAM_32PIN_NVRAM`)
- A `2026-07` footer date is present
- `git -C firestarter diff --stat doc/PROTOCOLS.md` showed exactly one file changed (27 insertions, 27 deletions)

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`firestarter/doc/PROTOCOLS.md` is now the single authoritative, operator-approved canonical
protocol vocabulary source for the rest of the v1.19 milestone:
- Phase 101 can read the `PROTO_` tokens + handler-family layer to author the actual `#define`s and firmware dispatch renames.
- Phase 102 can read the finalized display names to reconcile the host `ic_layout.py` maps (which are currently missing 0x34 — the new `PROTO_EEPROM_8051BUS` display name closes that gap).
- Phase 103 can reconcile the §1.x facet prose and §3 INV matrix to the final names (both were deliberately left untouched by this phase).

No blockers. The submodule commit `6e7bd38` (plus prior `43a3068`) is on branch
`v1.19-protocol-naming-labels`, ready for the orchestrator to bump the meta-repo gitlink.

---
*Phase: 100-name-canonical-protocol-name-set-operator-approval*
*Completed: 2026-07-01*
