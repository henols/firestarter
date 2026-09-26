# Phase 98: FIX — Correct the 0x08 32-Pin Write/VPP Path - Context

**Gathered:** 2026-06-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Apply the **Phase 97 root cause (RC-1, CONFIRMED)** to the firmware/host `0x08`
32-pin write/VPP path so the AM27C020 program pulse actually flips bits — scoped
to the `0x08`-UV-32-pin class so existing DIP32 chips that legitimately use pin
31 (27C040 = A18, SST39SF040 = WE) are **not** broken. Keep the v1.16 golden
register traces + dispatch-mirror guard byte-identical for the passing `0x07`
and `0x0B` paths, cover the corrected `0x08` write path with native tests
(including at least one failure-case/mismatch test — the v1.16 P89 CR-01 lesson),
deliver any wire-crossing datum dual-repo lockstep, and keep host CI green on
**py3.11**.

**This is a blind, no-bench phase.** Phase 99 is the silicon graduation gate
(Leonardo + Rev 2.0, seated AM27C020). PRE-01's writability result and the D-06
OTP/dead disposition are Phase-99 verdicts, not Phase-98 outcomes.

**RC-1 (locked from Phase 97):** pin 31 is modeled as address line A18 in
`DIP32_STD`, not as a held PGM control; firmware `memory_set_data`
(`memory.cpp:346`) strobes **CE only** — no PGM concept. Classification:
**host-pinout** (primary) + **firmware-algorithm** (secondary). RC-2 (P1 VPP
routing/level) is **EXONERATED** — pin 1 measured 13.0V, P1 route asserted.

**⚠ Open mechanism caveat (from the Phase 97 verifier):** on a 256K chip A18 is
*never set*, so pin 31 is **already physically at VIL** (the program-active
level) at every address — yet 0 bits program. RC-1 is confirmed as an
*architectural mismodeling*, not a direct measurement of pin 31 being in the
wrong state. This means the pinout-redirect alone may not change the physical
signal; the belt-and-suspenders breadth (D-01) and the empirical Phase-99 gate
exist precisely to close this residual.

**Not in this phase:** the bench write→verify graduation (Phase 99); the
OTP/dead vs path-broken verdict (Phase 99, D-06); FUT-05 (W27E040 `0x08`
rewritable proof).
</domain>

<decisions>
## Implementation Decisions

### Fix Breadth (no-bench, blind fix)
- **D-01:** **Belt-and-suspenders.** Implement the named RCA hand-off surfaces
  (new `DIP32_27C020` pinout redirecting pin 31 to a PGM concept + hold
  `CTRL_VPP_P1_ENABLE` / P1 route across the **full program pulse window**, not
  only the per-byte data-write window) **PLUS an explicit firmware
  PGM-pulse / program-sequence change** so pin 31 is a *deliberately asserted*
  control during the CE pulse — not merely coincidentally-VIL via the
  address bus. Rationale: Phase 98 fixes blind and the verifier flagged that the
  pinout-redirect alone may not move the physical signal; deliberately asserting
  PGM maximizes the chance Phase 99 passes in a single bench trip. Accepted cost:
  this touches the shared program pulse, so the regression discipline (D-05) and
  the alias-collision guard (D-04) become hard constraints.

### Pin-31 Redirect Scoping (don't break 27C040 / SST39SF040)
- **D-02:** **New `DIP32_27C020` pinout class** in the host DB
  (`pinouts.json` + `database.py`), assigned only to the `0x08` ≤256K-class
  chip(s). Data-driven scope: 27C040 (A18 on pin 31) and SST39SF040 (WE on pin
  31, already on `DIP32_SST39SF040`) stay on their existing pinouts and are
  untouched. The change must be reviewable via `diff_db.py` showing only the
  intended rows.

### Wire-Field Appetite (lockstep blast radius)
- **D-03:** **DB/pinout-only if possible.** Prefer expressing the fix via the new
  pinout entry + existing `CTRL_*` bits. A new wire field
  (`firestarter.h` ↔ `constants.py` lockstep, à la the v1.17 per-chip
  `page_size` precedent) is allowed **only if** the belt-and-suspenders firmware
  PGM-assert genuinely cannot be expressed otherwise. If a wire field is added,
  it carries the full parity-test + lockstep cost (`diff_db.py`,
  `check_dispatch.py`, constants-parity test all green).
  - *Note the interaction:* D-01 (firmware must deliberately assert PGM on pin 31)
    and D-03 (avoid new wire fields) pull against each other. The planner must
    first try to drive the PGM-assert from the new pinout mapping + a
    protocol-`0x08`-gated firmware branch using existing control bits; only escalate
    to a new wire datum as a last resort.

### Alias-Collision Guard (hard safety constraint)
- **D-04:** On Rev 2.0 the firmware control bits **`CTRL_VPP_P1_ENABLE_REV2`
  and `CTRL_ADDRESS_LINE_18_REV2` are the SAME physical bit (`0x08`)**
  (`rurp_pinout.h:121`/`:128`). Holding P1 across the pulse and/or asserting a
  PGM control via this bit is safe for a 256K AM27C020 (A18 never set) but would
  **corrupt A18 on a 512K 27C040**. The fix MUST be gated so the PGM/P1-hold
  behavior cannot leak to any chip that uses A18 (≥512K / 27C040 class). This
  alias is the v1.18 "Pitfall 6" carried from Phase 97 — treat it as a blocking
  design constraint, not a footnote.

### Regression & Test Posture (locked by roadmap SC #2, reinforced by D-01)
- **D-05:** v1.16 golden register traces + dispatch-mirror guard stay
  **byte-identical** for the passing `0x07` and `0x0B` EPROM paths. Where a trace
  legitimately changes for the `0x08` 32-pin path, **re-pin it with cited
  rationale**. Native tests must cover the corrected `0x08` write path
  (program-pulse / PGM asserted correctly) AND include at least one explicit
  **failure-case / mismatch test** (v1.16 P89 CR-01 lesson — a matching-id golden
  trace misses the WARNING-vs-ERROR / correct-vs-incorrect fork). Because D-01
  touches the shared program pulse, the `0x07`/`0x0B` trace-identity check is the
  primary regression tripwire.

### SAFE Invariant (SAFE-02)
- **D-06:** Over-voltage stays ERROR-blocked (`vpp_check_window` HIGH→ERROR, no
  `FLAG_FORCE` relaxation in the path); the host `chip_resolver.resolve_chip`
  guard is never bypassed; AM27C020 flows through normal `0x08` dispatch with no
  test-only escape hatch. Host CI green against the **py3.11** target (ruff check
  + ruff format --check + mypy + `diff_db` + `check_dispatch`) — avoid the
  py3.12-masks-CI-3.11 devcontainer trap (validate against py3.11 explicitly
  before claiming green).

### Claude's Discretion
- **Phase-99 decisiveness instrumentation (you decide):** whether the fix should
  expose/log the actual pin-31 (PGM) + P1 control-register state during the
  program window (held-rail-checkable) so Phase 99 can cleanly separate
  "path now correct but chip OTP/dead" (→ D-06-style clean FUT-06 deferral) from
  "still broken." Add the diagnostic hook only if it's worth the added surface;
  otherwise rely on Phase 99's DMM + write→verify + held-rail proxy.
- Within D-01–D-06: the concrete firmware sequencing for the PGM assert, exact
  `CTRL_*` composition, the held-rail control-register value used to validate
  the static pin-31 state, and the precise gate predicate (protocol `0x08` +
  32-pin + size/A18-unused) are planner/researcher choices.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Root cause & hand-off (read first)
- `.planning/phases/97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program/evidence/97-RCA-FINDINGS.md` — the authoritative RC-1 verdict, the 8-row 0x08-vs-0x07 differential matrix, the **Phase-98 Hand-Off** section (fix surfaces), and the **Host-vs-firmware bit-alias caveat (Pitfall 6)**. The whole of Phase 98 sits on this document.
- `.planning/phases/97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program/97-VERIFICATION.md` — the verifier's analytical nuance on RC-1 strength (pin 31 already VIL at addr 0) that motivates D-01's belt-and-suspenders breadth.
- `.planning/phases/97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program/97-CONTEXT.md` — Phase 97 decisions D-01..D-08 (the standing bench discipline + the deferred Phase-98 fix scoping).
- `.planning/research/v1.18-AM27C020-27C-EPROM.md` — the RCA brief: datasheet facts, current `0x08` path file:line, RC-1..RC-5 ranking, fix surfaces.
- `.planning/ROADMAP.md` §"Phase 98" — goal + 4 success criteria (FIX-01/02/03, SAFE-02) — the verbatim TRUE-conditions.
- `.planning/REQUIREMENTS.md` — v1.18 requirement bodies (FIX-01/02/03, SAFE-02) + Constraints/Standing-Context.

### Datasheets
- `firestarter/datasheets/0x08-EPROM-QUICK/AM27C020.pdf` — VPP 12.75V ±0.25 (12.5–13.0V), Flashrite 100µs pulse on CE with PGM=VIL, 32-pin pinout (pin 1=VPP, pin 31=PGM, pin 30=A17, pin 2=A16), 13.5V abs-max. The authoritative source for the PGM program-sequence the fix must implement.
- `firestarter/datasheets/0x08-EPROM-QUICK/W27C020.pdf` — a *different* chip (Winbond EEPROM, 12V) — do NOT conflate with the on-hand AMD AM27C020.

### Fix surfaces — firmware (`firestarter/`)
- `firestarter/src/proms/eprom.cpp` — `eprom_internal_set_control_register` (the `CTRL_VPE_ENABLE`→`CTRL_VPP_P1_ENABLE` rewrite for `using_p1_as_vpp`, `:319-326`), `eprom_write_init/execute`, `program_mismatched_bytes` (`:168`), `eprom_check_vpp`.
- `firestarter/src/proms/memory.cpp` — `memory_set_data` (`:274`, the CE-only program pulse that needs the PGM-assert concept), `mem_util_remap_address_bus` (`:309`, pin 31 → bus line 22), dispatch (`:121`).
- `firestarter/src/proms/primitives.cpp` — `vpp_check_window` (VPP-high = ERROR/block; only `FLAG_FORCE` relaxes — SAFE-02).
- `firestarter/include/rurp_pinout.h` — `CTRL_*` bit defs; **the `CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2 == 0x08` alias at `:122`/`:128`** (D-04).
- `firestarter/include/rurp_shield.h` (`VPP_P1_32_DIP=0x15`, CHIP_ENABLE), `firestarter/include/memory_utils.h` (`using_p1_as_vpp`).
- `firestarter/include/firestarter.h` — wire-struct (`page_size` precedent at `:97`) if D-03 escalates to a new wire field.

### Fix surfaces — host (`firestarter_app/`)
- `firestarter_app/firestarter/data/pinouts.json` — `DIP32_STD` (pin 31 = 19th address-bus pin / A18) + `DIP32_SST39SF040` (the precedent for a scoped DIP32 variant); the new `DIP32_27C020` entry lands here (D-02).
- `firestarter_app/firestarter/database.py` — `pin_conversions[32][31]=22` (the host-side A18 mapping, `:141`); host bus-config build.
- `firestarter_app/firestarter/data/chip_database.json` — AM27C020 row (pinout assignment to `DIP32_27C020`).
- `firestarter_app/firestarter/constants.py` — `JSON_KEY_PAGE_SIZE` (`:100`) is the lockstep precedent if D-03 escalates.

### Guards, traces & ledger
- v1.16 golden register traces + dispatch-mirror guard (`check_dispatch.py`) — the 0x07/0x0B byte-identity tripwire (D-05).
- `firestarter_app/.../diff_db.py` — DB-diff gate (D-02 review surface).
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` — `0x08` = `open-defect-carried (FUT-06)`; updated by Phase 99 (not Phase 98).

### Shield / hardware
- `firestarter/doc/SHIELD-REVISIONS.md` §7 + `.planning/v1.7-SHIELD-REVS.md` §3/§4 — JP4 = `JMP_VPP_P1_BYPASS`; Rev 2.0 P1 routing context for D-04.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`DIP32_SST39SF040` pinout entry** — the proven precedent for a scoped DIP32
  variant (it already redirects pins 1/31 for the 5V-flash family). `DIP32_27C020`
  follows the same shape: a sibling of `DIP32_STD` differing only in pin-31 role.
- **`eprom_internal_set_control_register` rewrite** (`eprom.cpp:319-326`) — the
  existing `using_p1_as_vpp` hook that already remaps `CTRL_VPE_ENABLE` →
  `CTRL_VPP_P1_ENABLE` for this family; the natural seam for the belt-and-suspenders
  P1-hold / PGM-assert change.
- **v1.17 per-chip `page_size` wire field** — the lockstep precedent
  (`firestarter.h:97` ↔ `constants.py:100`, `JSON_KEY_PAGE_SIZE`) if D-03 must
  escalate to a new control-pin wire datum.
- **Held-rail static proxy** (`firestarter dev reg ... -f`) — for any Phase-99
  diagnostic hook (Claude's-discretion) to be checkable statically.

### Established Patterns
- **Protocol-keyed defense-in-depth** (v1.17 T-93-CANERASE): gate behavior on
  `handle->protocol` in firmware AND mirror the gate host-side — the model for the
  D-04 alias-collision guard (PGM/P1-hold scoped to `0x08`-32-pin, never reaching
  A18 users).
- **Golden-trace + mismatch-test discipline** (v1.16 P89 CR-01): behavior-preserving
  refactors need an explicit failure-case test; the `0x07`/`0x0B` trace identity is
  the regression tripwire (D-05).

### Integration Points
- The new `DIP32_27C020` pinout flows: `chip_database.json` → `database.py`
  bus-config build → wire → firmware `mem_util_remap_address_bus`. The firmware
  PGM-assert must read pin 31's new role from this mapping (or a protocol gate),
  NOT hardcode it.
- VPP-skip on read/blank-check (v1.15) is the write-path-untouched baseline — the
  0-bits fault is genuinely in the `0x08`/32-pin **write/VPP** path.
</code_context>

<specifics>
## Specific Ideas

- The belt-and-suspenders firmware change (D-01) should make pin 31 a
  **deliberately asserted PGM control during the CE program pulse** — addressing
  the verifier's nuance that pin 31 being "coincidentally VIL via the address bus"
  is architecturally wrong even when the level happens to be right. The fix is the
  correct engineering response regardless of whether the addr-0 signal is already
  VIL.
- Hold `CTRL_VPP_P1_ENABLE` (P1 route) across the **full** program-pulse window,
  not just the per-byte data-write window (the RC-2 fix surface, kept as the
  "suspenders" even though RC-2 was exonerated — cheap insurance on a blind fix).
- Preferred gate predicate for the PGM/P1-hold behavior: protocol `0x08` + 32-pin
  + A18-unused (≤256K), driven by the new `DIP32_27C020` pinout assignment — so
  27C040 (A18) and SST39SF040 (WE) are structurally excluded (D-02/D-04).
</specifics>

<deferred>
## Deferred Ideas

- **Phase 99 bench graduation** — byte-exact write→verify on the seated AM27C020,
  EVIDENCE record, PROTOCOL-LEDGER `0x08` update, and the D-06 OTP/dead-vs-fixed
  verdict — all Phase 99, gated on PRE-01.
- **FUT-05** (REWR-02 `0x08` rewritable write proof, W27E040 stuck-bit) — a
  separate deferred requirement; may benefit from this `0x08` fix but is not v1.18
  scope.
- **None of the 5 pending todos folded** — none touch the `0x08` write-path fix
  (closest, "skip VPP checks when unused on reads," is the read/blank-check path,
  shipped in v1.15).

</deferred>

---

*Phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path*
*Context gathered: 2026-06-30*
