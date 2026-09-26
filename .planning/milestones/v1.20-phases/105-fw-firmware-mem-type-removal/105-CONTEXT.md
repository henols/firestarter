# Phase 105: FW — Firmware `mem_type` Removal - Context

**Gathered:** 2026-07-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the firmware dispatch **only** on `handle->protocol`. Delete the `mem_type`
fallback dispatch chain (`memory.cpp` steps 7–11) so `protocol == 0` fail-closes
to `configure_not_implemented()` (`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, 0xBB)
instead of silently falling back; drop `handle->mem_type` from
`firestarter_handle_t`; stop parsing the `type` JSON field in `json_parser.c`;
and retire `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` plus the
`TYPE_EPROM`/`TYPE_SRAM`/`TYPE_FLASH_TYPE_3`/`TYPE_FLASH_TYPE_4` constants.

Pure removal — **no behavior change for any real DB chip** (all carry
`algorithm`). Removing the `type` field from the wire is a breaking wire-contract
change; it lands **firmware-first** (fw stops parsing `type` here in Phase 105;
host stops emitting it in Phase 106). Safe ordering: `json_parser.c` silently
skips unknown fields, so a host still emitting `type` after this phase is
unaffected.

Requirements: FW-01, FW-02, FW-03, WIRE-01 (see `.planning/REQUIREMENTS.md`).
Dual-repo lockstep applies (`constants.py` ↔ `firestarter.h` parity), though
this phase's edits are firmware-only.

**Out of this phase:** host emit-side removal (Phase 106), docs + non-regression
close (Phase 107), and the milestone-level out-of-scope items (`FLAG_VPE_AS_VPP`
→ LEGACY-01/v2, `EPROM_LEGACY` naming → LEGACY-02/v2, canonical
`electrical.type` string, phantom/named-infeasibility arms).

</domain>

<decisions>
## Implementation Decisions

### Branch base / lockstep setup (prerequisite before planning execution)
- **D-01 [informational]:** The v1.20 sub-repo branches fork off **beta, but only after v1.19 is
  merged into beta first.** Confirmed state: `beta` in the fw sub-repo does NOT
  contain the v1.19 PROTO_ naming layer — beta's `memory.cpp` still dispatches on
  raw hex (`0x10`, `0x0D`, …), there is no `include/proto_constants.h`, and the
  Phase 104 handler renames (`flash_type_3/4` → `flash_nor_unlock`/`flash_5v_page`)
  are absent. All 15 v1.19 commits (Phases 100–104) are unmerged, living only on
  `v1.19-protocol-naming-labels`. Since Phase 105/107 reference PROTO_ tokens,
  renamed handlers, and `PROTOCOLS.md`, forking off unmerged beta would mismatch
  those refs and risk a Phase-70-style collision. **Operator authorized merging
  v1.19 → beta first**, then forking v1.20 off the updated beta.
- **D-02 [informational]:** The authorization is for the **v1.19 branch merge into beta only** —
  NOT the beta **release cut**. The `3.0.0bXX` beta tag + gitlink bump remain
  operator-gated per the standing "nothing is stable until I say so" rule;
  gitlinks stay PINNED (`2d93379` fw / `e0bdea4` app). Apply this to BOTH
  sub-repos (`firestarter/` + `firestarter_app/`) in lockstep.
- **D-03 [informational]:** The v1.19→beta merge is a **setup action performed before Phase 105
  execution**, not part of the discuss step. It was NOT done during discussion.

### `memory.cpp` dispatch code shape
- **D-04:** Collapse to **one terminal fail-closed exit.** Replace the
  `if (handle->protocol != 0) { configure_not_implemented(handle); return; }`
  guard (currently `memory.cpp:117`) with an unconditional terminal
  `configure_not_implemented(handle); return;` after all recognized dispatch
  arms. `protocol == 0` and any unknown non-zero protocol share ONE fail-closed
  exit — matches "trust only the real protocol" and removes the last
  `mem_type`-era conditional. (Recognized arms — steps 1–6b, the PROTO_ chain
  and named-infeasibility arm — stay unchanged.)

### Native dispatch test disposition
- **D-05:** **Delete the fallback-specific test cases**, don't rewrite them.
  Remove `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` from BOTH
  suites (`test_dispatch/test_configure_memory.cpp` and
  `test_not_implemented/test_not_implemented.cpp`) and the
  `test_unknown_protocol_with_unknown_mem_type_errors` case, since they assert
  the deleted behavior. Rely on `test_not_implemented`'s generic coverage
  (0x11 / 0x2A / 0x2B / 0x2C named-infeasibility + `0x99` unknown-non-zero) for
  fail-closed proof. No "type field ignored" test is required by operator choice.
- **D-06 (coverage flag for planner/verifier — NOT a re-decision):** SC#1 is
  specifically *"`protocol == 0` → 0xBB via `configure_not_implemented()`"*, and
  the deleted `test_protocol_zero_...` case is currently the ONLY `protocol == 0`
  test. `test_not_implemented` covers unknown **non-zero** (0x99) but not zero.
  The planner/verifier must confirm SC#1 stays provable — either explicitly
  accept the generic coverage as sufficient, or add a single minimal
  `protocol == 0 → configure_not_implemented` assertion (the *inverse* of the
  deleted fallback test — this is NOT a "fallback test" and does not contradict
  D-05). Do not silently ship without resolving this.

### Claude's Discretion
- Exact grouping of edits into commits — but note SC#3 requires the `0xAE` +
  `TYPE_*` constant retirement to land **in the same commit** as the dispatch-chain
  deletion (no orphaned dead constants). Removing `handle->mem_type` from the
  struct forces the `json_parser.c` `extract_int("type", …)` removal and the
  `key_type[] PROGMEM = "type"` constant removal together (they reference the
  deleted field).
- Whether `make_handle(protocol, mem_type, cmd)` in the two native test suites
  keeps or drops its `mem_type` parameter after the struct field is removed
  (mechanical; the field no longer exists so the param becomes vestigial).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — v1.20 requirements; FW-01, FW-02, FW-03, WIRE-01
  are Phase-105-owned. Out-of-scope table + LEGACY-01/02 deferrals live here.
- `.planning/ROADMAP.md` — v1.20 milestone section + Phase 105 Success Criteria
  (SC#1–#4 are the acceptance bar); Phase 106/107 dependencies.

### Firmware dispatch (source of truth to edit)
- `firestarter/src/proms/memory.cpp` — `configure_memory()`; steps 7–11 (the
  `mem_type` fallback, current lines ~122–138) are deleted; the `TYPE_*`
  `#define`s (lines 27–30) are removed; the `protocol != 0` guard collapses (D-04).
- `firestarter/include/firestarter.h` — `firestarter_handle_t`; remove
  `uint8_t mem_type;` (line ~88).
- `firestarter/src/json_parser.c` — remove `extract_int("type", handle->mem_type)`
  (line ~307) and `const char key_type[] PROGMEM = "type";` (line ~64).
- `firestarter/include/messages.h` — retire `MSG_ERR_MEM_TYPE_UNSUPPORTED 0xAE`
  (line ~83). NOTE: the `0xAE` at `firestarter/src/boards/rurp_serial_utils.cpp:374`
  is a CRC8 lookup-table byte, NOT a message-code reference — leave it untouched.

### Dispatch semantics & non-regression gates
- `firestarter/CLAUDE.md` → "Protocol Dispatch" section — documents the step 1–11
  order and the "no `mem_type == 2`" note; describes the fail-closed invariant.
  (Doc updates to this are Phase 107 / DOC-01, not this phase — but read it to
  understand the current dispatch contract.)
- `firestarter/doc/PROTOCOLS.md` — operator-approved PROTO_ name set (v1.19).
- `firestarter/include/proto_constants.h` — PROTO_ token definitions (v1.19 layer;
  present only after the v1.19→beta merge per D-01).
- v1.16 golden register traces + dispatch-mirror guard + `check_dispatch.py` —
  MUST stay green (SC#4 / GATE-01/02); prove the removed fallback was dead for
  every real chip.

### Native test suites to edit (D-05)
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`
- `firestarter/test/native/avr/test_not_implemented/test_not_implemented.cpp`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `configure_not_implemented(handle)` (`not_implemented.cpp`, wired via
  `not_implemented.h`) is the existing fail-closed handler returning 0xBB — reused
  as the single terminal exit (D-04). Already the target of steps 6a/6b.
- `test_not_implemented` suite is the existing home for fail-closed dispatch
  assertions; generic coverage there is what D-05 relies on.

### Established Patterns
- Dispatch is a linear `if (handle->protocol == …) { configure_*(); return; }`
  chain in `configure_memory()`. Steps 1–6b (PROTO_ chain + named-infeasibility
  arm) are unchanged; only the tail (guard + steps 7–11) changes.
- `json_parser.c` silently skips unknown JSON fields — this is WHY fw-first
  removal is safe (a host still emitting `type` is harmless post-Phase-105).
- Constants that mirror between firmware and host are tracked for parity
  (`constants.py` ↔ `firestarter.h`); watch the py3.12-masks-CI-3.11 ruff/codegen
  trap when host changes land in Phase 106 (not this phase).

### Integration Points
- `handle->mem_type` has exactly two firmware consumers: `memory.cpp` (dispatch)
  and `json_parser.c` (populate). Removing the struct field is clean once both
  go. Test files also set `h.mem_type` via `make_handle()` — those edits are
  forced by the field removal (folds into D-05).

</code_context>

<specifics>
## Specific Ideas

- Fail-closed collapse must sit AFTER all recognized dispatch arms (steps 1–6b)
  and become the function's terminal statement — mirroring the intent of the
  current `T-64-01` 12V-VPP-hazard guard, now generalized to include `protocol == 0`.
- SC#2's "hand-crafted JSON with `type` is silently ignored" is satisfied
  structurally by removing the `type` parse (unknown-field-skip), not by a test
  (per D-05).

</specifics>

<deferred>
## Deferred Ideas

- **LEGACY-01 (v2):** `FLAG_VPE_AS_VPP (0x10)` removal — operator scoped v1.20 to
  the `mem_type` axis only, not the broader vestige sweep.
- **LEGACY-02 (v2):** Rename `EPROM_LEGACY (0x0B)` label + scrub remaining
  "legacy fallback" prose once the mem_type axis is gone.
- **Phase 106 (this milestone):** Host emit-side `type` removal + `_ALGO_MEM_TYPE`
  / derived `mem_type` / "Generic Flash (legacy fallback only)" default removal +
  in-host `algorithm`-presence rejection. Completes WIRE-01.
- **Phase 107 (close):** Doc updates (`CLAUDE.md` steps 7–11, `PROTOCOLS.md`, JSON
  wire-field docs) + breaking-change/changelog record + full non-regression
  re-verification.
- **Beta release cut (operator-gated):** `3.0.0bXX` tag + gitlink bump — NOT a
  phase; deferred to manual operator authorization (D-02).

None of the above are in Phase 105 scope — discussion stayed within the firmware
removal boundary.

</deferred>

---

*Phase: 105-fw-firmware-mem-type-removal*
*Context gathered: 2026-07-02*
