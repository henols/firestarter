# Phase 88: Golden Traces + Dispatch-Mirror Guard - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-26
**Phase:** 88-golden-traces-dispatch-mirror-guard-was-87
**Areas discussed:** Trace fidelity, Golden-ref form, Trace coverage, Dispatch-mirror source

---

## Trace fidelity

| Option | Description | Selected |
|--------|-------------|----------|
| Byte-exact full seq | Assert the complete ordered (reg,data) sequence, equality-compared against a pinned expected array. Strongest oracle; benign reorders also trip it (re-bless). | ✓ |
| Key-register subset | Pin only semantically-load-bearing writes (CONTROL_REGISTER/address/data) as an ordered subsequence; tolerant of benign reordering. | |
| Hybrid: full+blessed | Byte-exact full sequence with a one-line re-bless workflow as the review checkpoint. | |

**User's choice:** Byte-exact full sequence.
**Notes:** Maximum-strength oracle chosen deliberately.

### Follow-up — Re-bless policy

| Option | Description | Selected |
|--------|-------------|----------|
| Frozen byte-identical | Trace immutable through Phase 89; output-preserving refactor only, no reorder. | |
| Re-bless allowed | Phase 89 may regenerate the expected array after confirming a diff is benign; the re-bless commit is the audit checkpoint. | ✓ |
| Frozen, escape-hatch | Frozen by default; re-bless allowed as a documented exception per family. | |

**User's choice:** Re-bless allowed.
**Notes:** Re-bless is the deliberate human-review checkpoint, not a failure mode.

---

## Golden-reference form

| Option | Description | Selected |
|--------|-------------|----------|
| Generated .inc fixture | Committed generated header per family; recorder regenerates; clean line-by-line diff for re-bless. | |
| Inline literal in test | Expected array written directly in the test .cpp. | |
| You decide | Planner chooses; must be committed, equality-compared, cheaply regenerable. | ✓ |

**User's choice:** You decide (planner's discretion).
**Notes:** Constraint retained — committed, equality-compared (count + every element), cheaply regenerable so re-bless is a one-step rerun with a reviewable diff.

---

## Trace coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Write + chip-id | End-to-end write/program path (covers P3/P5/P7) + chip-id path (P4) per family. Union of Phase-89 primitive touchpoints. | ✓ |
| Write path only | Just the write/program path; misses P4's separate chip-id command path. | |
| Every command path | Read+write+blank+erase+chip-id; duplicates existing INV coverage and bloats traces vs the 256-entry cap. | |

**User's choice:** Write + chip-id.
**Notes:** Read/blank stay covered by Phase-87 INV tests; flagged the 256-entry recording cap as a fixture-sizing constraint (flash4 page write).

---

## Dispatch-mirror source of truth

| Option | Description | Selected |
|--------|-------------|----------|
| Bind all three | PROTOCOLS.md §0 table (canonical) == check_dispatch.py == firmware configure_memory dispatch; any drift trips. | ✓ |
| Native: firmware vs doc | Native C test pins firmware dispatch against the documented order; check_dispatch.py not re-asserted. | |
| Host: tool vs doc | Host pytest asserts check_dispatch.py matches the documented order; weakest coupling to firmware. | |

**User's choice:** Bind all three.
**Notes:** PROTOCOLS.md §0 table (lines ~22–35) is already machine-parseable; the mirror guards the full dispatch table (incl. SRAM + 0x34), while the golden traces cover the five recompose families.

---

## Claude's Discretion

- Golden-reference representation (inline literal vs generated .inc vs other) — constrained to committed + equality-compared + cheaply regenerable.
- Which `test_val_*` suite hosts each trace + the assertion-helper mechanics.
- Whether the dispatch-mirror test lives native-side, host-side, or as a cross-repo parse harness — as long as all three representations are bound.

## Deferred Ideas

- The primitive recompose itself (P7→P4→P3→P5) — Phase 89.
- Per-protocol bench validation + PROTOCOL-LEDGER — Phase 90.
- 0x34 X88C64 programming handler — still PCB-blocked (FUT-01), out of v1.16 scope.
