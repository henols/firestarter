# Phase 105: FW — Firmware `mem_type` Removal - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-02
**Phase:** 105-fw-firmware-mem-type-removal
**Areas discussed:** v1.20 branch base, Fallback test disposition, protocol==0 code shape

---

## Gray-area selection

Presented 3 gray areas (multiSelect). Operator selected **all three**:
Fallback test disposition, protocol==0 code shape, v1.20 branch base.

Resolved during scouting (not asked): `0xAE` at `rurp_serial_utils.cpp:374` is a
CRC8 lookup-table byte, not a message-code reference — leave untouched.

---

## v1.20 branch base

Context surfaced: `beta` (fw sub-repo) lacks the entire v1.19 PROTO_ naming +
handler-rename work. Beta's `memory.cpp` dispatches on raw hex, no
`proto_constants.h`, old handler names; all 15 v1.19 commits (Phases 100–104)
unmerged, only on `v1.19-protocol-naming-labels`. Same pattern as v1.15.

| Option | Description | Selected |
|--------|-------------|----------|
| Off v1.19 tip (chain) | Fork v1.20 off v1.19 branch; bundle v1.19+v1.20 at later beta merge (v1.15 precedent) | |
| Merge v1.19→beta first | Authorize the gated v1.19 beta merge, then fork v1.20 off updated beta | ✓ |
| Off beta (literal rule) | Fork off beta as written; accept raw-hex/old-names mismatch + collision risk | |

**User's choice:** Merge v1.19→beta first.
**Notes:** Clarified with operator that this authorizes the **branch merge into
beta only** — the beta release cut (`3.0.0bXX` tag + gitlink bump) stays
operator-gated, gitlinks PINNED. Merge is a prerequisite setup action before
Phase 105 execution; NOT performed during discussion. Applies to both sub-repos.

---

## Fallback test disposition

Context: two native suites assert the OLD fallback (protocol==0 + mem_type=1 →
configure_eprom); removal inverts that to fail-closed 0xBB.

| Option | Description | Selected |
|--------|-------------|----------|
| Invert in place + add type-ignored test | Rewrite tests to assert fail-closed 0xBB + add SC#2 "type ignored" test; keep as regression proof | |
| Delete fallback tests | Remove the fallback-specific cases; rely on test_not_implemented generic coverage | ✓ |
| Discuss test details | Talk through make_handle() signature + assertions before locking | |

**User's choice:** Delete fallback tests.
**Notes:** Builder flagged (not a re-decision) that SC#1 specifically requires a
`protocol == 0 → 0xBB` assertion and the deleted case is the only protocol==0
test; `test_not_implemented` covers only unknown non-zero (0x99). Recorded as
D-06 coverage flag for the planner/verifier to resolve — accept generic coverage
or add a single minimal inverse assertion.

---

## protocol==0 code shape

| Option | Description | Selected |
|--------|-------------|----------|
| Collapse to one terminal exit | Unconditional terminal configure_not_implemented() after recognized arms; protocol==0 + unknown-nonzero share one fail-closed exit | ✓ |
| Keep guard + explicit 0 arm | Keep `protocol != 0` guard + add separate explicit protocol==0 arm | |

**User's choice:** Collapse to one terminal exit.
**Notes:** Matches "trust only the real protocol"; removes the last mem_type-era
conditional. Recognized arms (steps 1–6b) unchanged.

---

## Claude's Discretion

- Exact commit grouping (subject to SC#3: `0xAE` + `TYPE_*` retirement in the
  same commit as dispatch-chain deletion).
- Whether `make_handle()` keeps/drops its now-vestigial `mem_type` parameter.

## Deferred Ideas

- LEGACY-01 (v2): `FLAG_VPE_AS_VPP (0x10)` removal.
- LEGACY-02 (v2): `EPROM_LEGACY (0x0B)` rename + "legacy fallback" prose scrub.
- Phase 106: host emit-side removal (WIRE-01 completion).
- Phase 107: docs + non-regression close.
- Beta release cut (`3.0.0bXX` tag + gitlink bump) — operator-gated, not a phase.
