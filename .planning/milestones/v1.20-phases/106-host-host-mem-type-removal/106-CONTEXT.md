# Phase 106: HOST — Host `mem_type` Removal - Context

**Gathered:** 2026-07-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the Python host mirror the Phase 105 firmware removal: `algorithm` becomes
the **sole** dispatch datum on the wire. Concretely:

- Stop emitting the `type` key in any serial command payload (the only emit site
  is `convert_to_programmer` in `database.py`, consumed by
  `eprom_operations.py`'s command-dict builder). Closes WIRE-01's emit side.
- Drop `_ALGO_MEM_TYPE`, the derived `mem_type` (`determined_type`), and the
  "Generic Flash (legacy fallback only)" substring default from `database.py`.
- Remove the `mem_type`-keyed legacy display-label fallbacks in `ic_layout.py`
  (`get_chip_type_string` numeric `type_map`) and its callers
  (`eprom_info.py`) — labels derive from `electrical.type` / protocol only.
- Reject any chip entry (built-in or user-override) lacking a **usable
  `algorithm`** with a clear, actionable error **before any serial byte** — no
  silent fallback dispatch.

Pure cleanup — **no behavior change for any real DB chip** (all carry
`algorithm`). This is the host half of a breaking wire-contract change already
landed firmware-first in Phase 105 (fw stopped parsing `type`; `json_parser.c`
silently skips unknown fields, so the brief window where the host still emitted
`type` was harmless). Accepted consequence: user-override DB entries lacking
`algorithm` will no longer program (they must specify a protocol).

Requirements: HOST-01, HOST-02, HOST-03, HOST-04 (see `.planning/REQUIREMENTS.md`).

**Out of this phase:** docs + non-regression close (Phase 107 / DOC-01, GATE-01,
GATE-02, SAFE-01), and the milestone-level out-of-scope items
(`FLAG_VPE_AS_VPP` → LEGACY-01/v2, `EPROM_LEGACY` naming → LEGACY-02/v2,
canonical `electrical.type` string, phantom/named-infeasibility arms).

</domain>

<decisions>
## Implementation Decisions

### HOST-04 — rejection semantics & site
- **D-01 (rejection rule):** A "usable `algorithm`" means **present and non-zero**.
  Reject only when `algorithm` is absent or `0` — this exactly mirrors the
  firmware's `protocol == 0 → 0xBB` fail-close (Phase 105 D-04/D-06). Do NOT add
  a stricter "not in `KNOWN_PROTOCOLS`" gate: a non-zero-but-unknown protocol
  falls through to the firmware's fail-closed handler (host still receives a
  clean 0xBB), preserving the "trust the wire's real protocol" symmetry and not
  pre-rejecting a protocol the firmware may newly support.
- **D-02 (guard site + error surface):** Extend the existing single chokepoint
  `chip_resolver.resolve_chip` and **reuse `ChipNotImplementedError`**. The
  algorithm-presence check lands alongside the existing `support_status` refusal
  (which already fires BEFORE `convert_to_programmer` builds any wire dict), so
  no new serial byte can be emitted for an unusable entry. No new exception type.
  Message must be clear/actionable (e.g. name the chip and state a protocol/
  `algorithm` is required). The `info`/`list`/`search`/`id` display paths bypass
  `resolve_chip` and are intentionally unaffected by this guard.

### HOST-03 — display-label fallback
- **D-03 (label + signature):** `resolve_type_label` / `get_chip_type_string`
  derive the label from `electrical.type` first, then the protocol-based name;
  when **neither** resolves (entry lacks `electrical.type` AND has no known
  protocol — e.g. a broken user-override that `info`/`list` still renders), show
  **`"Unknown"`**. **Drop the now-dead `type_int` (mem_type) parameter** from both
  signatures and delete the numeric `type_map` (`{1: EPROM, 2: Flash type 2, …}`).
  Removes the `mem_type` axis fully rather than leaving a vestigial param.
  Requirement: no behavior regression for any chip that already resolved
  correctly via `electrical.type`/protocol.

### HOST-02 — internal `type` key blast radius
- **D-04 (full removal):** Delete the `"type"` key from `_map_data`'s output
  entirely (the `determined_type` derivation block at `database.py:~418–426,445`
  goes away with `_ALGO_MEM_TYPE`). Clean up **every** `.get("type", 0)`
  consumer: `convert_to_programmer` (`database.py:585` — the wire emit),
  `ic_layout.py:561`, `eprom_info.py:408`. Matches SC#2's "no derived
  `mem_type`" — no vestigial internal field left behind. (Chosen over
  drop-at-wire-only, which would leave the axis lingering internally.)

### Test approach (folded in — decided-by-Phase-105-pattern, not re-asked)
- **D-05 (wire-val tests — delete-and-invert):** The `tests/test_val_wire_*.py`
  suite currently asserts `"type"` is IN the emitted command dict. Flip each to
  **positively assert `"type"` is NOT in the command** — that absence IS HOST-01's
  proof. Same delete-and-invert discipline as Phase 105 D-05 (test the inverse of
  the deleted behavior).
- **D-06 (HOST-04 test — SC#4):** Add a test in `tests/test_chip_resolver.py`
  (alongside the existing `support_status` refusal tests) exercising a
  **deliberately-broken user-override entry** (no `algorithm` / `algorithm == 0`)
  → asserts `ChipNotImplementedError` raised, with **no serial byte** emitted.

### Claude's Discretion
- Exact wording of the HOST-04 rejection message (must name the chip and state a
  protocol/`algorithm` is required — clear and actionable).
- Exact grouping of edits into commits, and whether the `type_int` param removal
  ripples into any other `ic_layout`/`eprom_info` call sites discovered during
  planning (mechanical, forced by the signature change).
- Whether `eprom_info.py:69`'s raw-JSON `"type": "unknown"` string field (a
  different, string-typed key unrelated to numeric `mem_type`) needs any touch —
  planner to confirm it is NOT the `mem_type` axis and leave it unless it
  consumes the removed integer `type`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — v1.20 requirements; HOST-01..04 are Phase-106-owned
  (WIRE-01 emit side). GATE-01/02 + SAFE-01 are Phase-107 gates but constrain
  this phase (no `chip_database.json` value change; native+host suites green).
- `.planning/ROADMAP.md` — v1.20 milestone section + Phase 106 Success Criteria
  (SC#1–#4 are the acceptance bar); Phase 105 (upstream firmware removal) +
  Phase 107 (close) dependencies.

### Prior-phase context (the firmware half — read for wire-contract symmetry)
- `.planning/phases/105-fw-firmware-mem-type-removal/105-CONTEXT.md` — Phase 105
  decisions (D-04 single terminal fail-closed exit; D-05 delete-don't-rewrite
  tests; D-06 test-the-inverse). This host phase mirrors that discipline.
- `.planning/phases/105-fw-firmware-mem-type-removal/105-SUMMARY.md` — what
  actually landed firmware-side (fw @96b93a9); confirms `type` is no longer
  parsed on the wire.

### Host source to edit (source of truth)
- `firestarter_app/firestarter/database.py` — `_ALGO_MEM_TYPE` (`:48`), the
  `determined_type` derivation (`:418–428`), the `"type": determined_type`
  mapped-dict key (`:445`), and the `"type": full_eprom_data.get("type", 0)`
  wire emit in `convert_to_programmer` (`:585`). All removed (D-04).
- `firestarter_app/firestarter/chip_resolver.py` — `resolve_chip` chokepoint;
  add the `algorithm`-presence guard beside the `support_status` guard (D-02).
- `firestarter_app/firestarter/ic_layout.py` — `get_chip_type_string` (`:203`,
  numeric `type_map` `:222`) and `resolve_type_label` (`:504–534`); drop
  `type_int` param + `type_map` (D-03); caller `build_specifications` (`:564`).
- `firestarter_app/firestarter/eprom_info.py` — `resolve_type_label` caller at
  `:408` (list/search Type column); the string-typed `"type": "unknown"` at
  `:69` is a different field (Claude's-discretion check, likely untouched).
- `firestarter_app/firestarter/eprom_operations.py` — command-dict builder
  (`_prepare... `, `command_dict = eprom_data_dict.copy()` at `:307`) consumes
  `convert_to_programmer`'s output; verify no independent `type` injection.

### Constants / parity note
- `firestarter_app/firestarter/constants.py` — verified to contain **no**
  `TYPE_*` / `mem_type` / `0xAE` constants, so there is NO dual-repo parity
  constant to remove this phase (Phase 105 already retired the firmware `TYPE_*`
  + `0xAE`). Do not introduce one.

### Non-regression gates (must stay green — enforced/re-verified in Phase 107)
- `firestarter_app/tools/check_dispatch.py` — 0 violations (GATE-01).
- `firestarter_app/tools/diff_db.py` — no `chip_database.json` value change for
  real chips (GATE-01). This phase edits code, not the generated DB.
- `firestarter_app/tests/test_dispatch_mirror.py` — dispatch-mirror guard stays
  green (host algorithm → firmware handler; unaffected by `type` removal).
- CI: py3.11-target `ruff check` + `ruff format --check` + `mypy` (strict on the
  8 Phase-42 modules incl. `chip_resolver.py`) + `pytest`. Watch the
  py3.12-masks-CI-3.11 ruff/codegen drift trap (validate against py3.11 target).

### Wire-contract reference
- `firestarter_app/CLAUDE.md` → "Wire Protocol" — the example command still shows
  `"type": 1`; that doc line is a Phase-107 / DOC-01 update, but read it to
  understand the current wire shape being changed.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `chip_resolver.resolve_chip` is the **single chokepoint** between CLI dispatch
  and DB lookup/conversion, already raising `ChipNotImplementedError` for
  `support_status != "supported"` BEFORE any wire dict is built — the natural,
  already-tested home for the HOST-04 `algorithm`-presence guard (D-02).
- `ChipNotImplementedError` (`exceptions.py`) already carries the
  refuse-before-serial semantics; reuse it rather than adding a type (D-02).
- `resolve_type_label` (`ic_layout.py`) is the D-04/IN-01 single-source-of-truth
  label helper shared by `build_specifications` (info) and
  `print_eprom_list_table` (list/search) — editing it once fixes both views.
- `test_chip_resolver.py` is the existing home for refuse-before-serial tests
  (D-06); `test_val_wire_*.py` is the per-protocol wire-shape suite (D-05).

### Established Patterns
- Wire command = `convert_to_programmer`'s dict copied verbatim into the command
  frame (`eprom_operations.py:307`). Removing `"type"` there removes it from the
  wire; there is exactly ONE emit site.
- Display labels flow: `electrical.type` (ground truth) → protocol name →
  (currently) numeric `mem_type` fallback. D-03 removes the last tier and lands
  on `"Unknown"`.
- Delete-and-invert test discipline from Phase 105: prove HOST-01 by asserting
  `"type"` is ABSENT (not by keeping and mutating the old assertion).
- `constants.py` ↔ `firestarter.h` parity is tracked but has no `TYPE_*`/
  `mem_type` member to touch here.

### Integration Points
- `mem_type` derivation has two host consumers today: the wire (via
  `convert_to_programmer`) and display (via `resolve_type_label` /
  `get_chip_type_string`). Removing the mapped-dict `"type"` key (D-04) forces
  both consumers to be cleaned in lockstep — clean once the derivation is gone.
- Program-capable ops route through `resolve_chip`; display ops
  (`info`/`list`/`search`/`id`) do NOT — the HOST-04 guard correctly affects only
  the former, while D-03 keeps the latter rendering gracefully (`"Unknown"`).

</code_context>

<specifics>
## Specific Ideas

- The host change is the emit-side completion of a firmware-first breaking wire
  change; because `json_parser.c` skips unknown fields, ordering is safe and no
  in-flight desync is possible (mirrors Phase 105 C-ontext's safe-ordering note).
- SC#1 ("no `type` key on the wire") is proven by the inverted `test_val_wire_*`
  assertions (D-05), not merely by inspection.
- SC#4's "before any serial byte" is satisfied structurally by placing the guard
  in `resolve_chip`, upstream of `convert_to_programmer` and all serial I/O (D-02).

</specifics>

<deferred>
## Deferred Ideas

- **Phase 107 (this milestone, close):** Doc updates — `firestarter/CLAUDE.md`
  (dispatch steps 7–11 + the `"type": 1` wire example), `firestarter/doc/PROTOCOLS.md`,
  JSON wire-field docs, sub-repo README/changelog breaking-change record — plus
  full non-regression re-verification (GATE-01/02, SAFE-01).
- **LEGACY-01 (v2):** `FLAG_VPE_AS_VPP (0x10)` removal — out of the `mem_type`-axis
  scope.
- **LEGACY-02 (v2):** Rename `EPROM_LEGACY (0x0B)` label + scrub remaining "legacy
  fallback" prose once the `mem_type` axis is gone.
- **Beta release cut (operator-gated):** `3.0.0bXX` tag + gitlink bump — NOT a
  phase; gitlinks stay PINNED at b10 pending manual operator authorization.

None of the above are in Phase 106 scope — discussion stayed within the host
removal boundary.

</deferred>

---

*Phase: 106-host-host-mem-type-removal*
*Context gathered: 2026-07-02*
