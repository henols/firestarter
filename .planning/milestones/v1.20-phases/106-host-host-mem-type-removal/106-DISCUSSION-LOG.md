# Phase 106: HOST — Host `mem_type` Removal - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-02
**Phase:** 106-host-host-mem-type-removal
**Areas discussed:** HOST-04 rejection rule, HOST-04 rejection site/error, HOST-03 label fallback, HOST-02 internal `type` key blast radius

---

## HOST-04 — Reject rule (what counts as a "usable algorithm")

| Option | Description | Selected |
|--------|-------------|----------|
| Absent/0 only (mirror FW) | Reject only when `algorithm` is missing or 0 — mirrors firmware `protocol==0 → 0xBB`. Unknown non-zero protocols fall through to firmware fail-close. Minimal, symmetric with Phase 105. | ✓ |
| Not in KNOWN_PROTOCOLS | Stricter: reject any algorithm not in host `KNOWN_PROTOCOLS`. More host-side safety but diverges from FW's trust-the-wire symmetry; could reject a protocol the FW newly supports. | |

**User's choice:** Absent/0 only (mirror FW)
**Notes:** Keeps host/firmware symmetry; non-zero-but-unknown protocols still get a clean 0xBB from the firmware fail-closed handler. → CONTEXT D-01.

---

## HOST-04 — Reject site & error surface

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse resolve_chip + ChipNotImplementedError | Extend the existing chokepoint `chip_resolver.resolve_chip` (already raises before any wire dict for `support_status`). One chokepoint, consistent with existing refusal path. | ✓ |
| New dedicated exception/message | Add a distinct exception (e.g. MissingAlgorithmError) with its own message. Clearer diagnostics but a new type in the hierarchy. | |

**User's choice:** Reuse resolve_chip + ChipNotImplementedError
**Notes:** Guard lands beside the `support_status` guard, upstream of `convert_to_programmer`/serial — satisfies "before any serial byte" structurally. → CONTEXT D-02.

---

## HOST-03 — Display-label fallback (no electrical.type + no known protocol)

| Option | Description | Selected |
|--------|-------------|----------|
| 'Unknown' label + drop type_int param | Derive from `electrical.type` → protocol name → `"Unknown"`. Drop the dead `type_int` (mem_type) param and numeric `type_map` from both signatures. Cleanest — removes the axis fully. | ✓ |
| Keep protocol fallback, drop only type_map | Remove numeric `type_map` but keep `type_int` param signature (pass-through/ignored). Smaller churn, leaves a vestigial param. | |

**User's choice:** 'Unknown' label + drop type_int param
**Notes:** Full axis removal preferred; no regression for chips already resolving via electrical.type/protocol. → CONTEXT D-03.

---

## HOST-02 — Internal `type` key blast radius

| Option | Description | Selected |
|--------|-------------|----------|
| Full removal from mapped dict | Delete the `"type"` key from `_map_data` output entirely; clean every `.get("type", 0)` consumer (ic_layout, eprom_info, convert_to_programmer). Matches SC#2. Larger diff, no vestigial field. | ✓ |
| Drop at wire only, keep internal key | Stop emitting `type` at the wire but keep a benign internal key for display. Smaller diff, weaker vs SC#2 intent. | |

**User's choice:** Full removal from mapped dict
**Notes:** Removes `_ALGO_MEM_TYPE` + `determined_type` derivation + "Generic Flash (legacy fallback only)" default. → CONTEXT D-04.

---

## Claude's Discretion

- Exact wording of the HOST-04 rejection message (must name chip + require a protocol/`algorithm`).
- Commit grouping and any additional `type_int` call-site ripples found during planning.
- Whether `eprom_info.py:69`'s string-typed `"type": "unknown"` (unrelated to numeric `mem_type`) needs any touch — planner to confirm and likely leave.

## Folded-in test items (decided by Phase-105 pattern, not separately asked)

- **D-05:** Invert the `tests/test_val_wire_*.py` assertions — assert `"type"` is ABSENT from the command dict (HOST-01 proof).
- **D-06:** Add a broken-user-override test in `tests/test_chip_resolver.py` — no `algorithm` → `ChipNotImplementedError`, no serial byte (SC#4).

## Deferred Ideas

- Phase 107 (close): doc updates (`CLAUDE.md`, `PROTOCOLS.md`, wire-field docs, changelog) + full non-regression re-verification (GATE-01/02, SAFE-01).
- LEGACY-01 (v2): `FLAG_VPE_AS_VPP (0x10)` removal.
- LEGACY-02 (v2): rename `EPROM_LEGACY (0x0B)` + scrub "legacy fallback" prose.
- Beta release cut (operator-gated): `3.0.0bXX` tag + gitlink bump; gitlinks PINNED at b10.
