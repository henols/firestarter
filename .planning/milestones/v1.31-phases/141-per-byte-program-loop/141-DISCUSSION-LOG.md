# Phase 141: Per-Byte Program Loop - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-10
**Phase:** 141-per-byte-program-loop
**Areas discussed:** `0x0B` energy-cap arithmetic (selected); message-catalog scope (follow-up)
**Areas offered and declined:** skip order (LOOP-06), the final full-array verify pass, failure
report shape, pulse primitive + delay helper home, proving the `factor = 0` branches, DIP32
drop-bit/A16, gate & trace fallout — all answered "[No preference]" and taken as Claude's discretion

---

## Gray-area selection

**Question 1 (multiSelect) — loop-behaviour areas:** skip order (LOOP-06) · **0x0B energy-cap
arithmetic ✓** · the final verify pass · failure report shape (LOOP-05).
**User's choice:** `0x0B` energy-cap arithmetic only.

**Question 2 (multiSelect) — structural / proof areas:** pulse primitive + delay helper · proving
`factor = 0` branches · DIP32 drop-bit/A16 · gate & trace fallout.
**User's choice:** **[No preference]** — delegated to Claude in full. Recorded as CONTEXT.md
D-05…D-12 so downstream agents treat them as settled rather than re-asking.

---

## 0x0B energy-cap arithmetic

### Cap boundary — what happens when the next pulse would cross 50 ms

| Option | Description | Selected |
|--------|-------------|----------|
| Stop before overshoot | Never exceed 50 ms; the byte hard-fails at the cap. Keeps LOOP-01's fixed-width claim literally true and never exceeds the datasheet energy budget. *(This was the recommended option.)* | |
| Allow the crossing pulse, then stop | Emit the pulse that crosses the cap, then stop. Uses the full budget; overshoot bounded by one pulse width — up to 65535 µs via `--pulse-us`, so a real ceiling near 115 ms. | ✓ |
| Truncate the final pulse | Shorten the last pulse to land on exactly 50 ms. Maximum energy within the cap, but emits a pulse of a different width than all the others. | |

**User's choice:** Allow the crossing pulse, then stop.
**Notes:** Chosen against the recommendation. Consequence carried into CONTEXT.md D-01: the
effective per-byte ceiling becomes `50000 + pulse` µs, not 50 ms flat. Unreachable with any shipped
database width (500/1000/200 µs all divide 50 ms evenly), so `--pulse-us` is the only way to reach
it. D-03's pre-flight refusal was subsequently chosen to bound the pathological direction.

### What counts toward the accumulated total

| Option | Description | Selected |
|--------|-------------|----------|
| Pulse widths only | `N × pulse_delay`. Matches `t_w(PR)`; fully deterministic, so a native test can assert exact pulse counts without a clock. *(Recommended.)* | ✓ (by delegation) |
| Pulse widths + per-pulse overhead | Also charge `memory_set_data`'s 3 µs settle. ~0.6% of budget at 500 µs; ties the expected count to a constant in `memory.cpp`. | |
| Wall-clock elapsed | `millis()` around the loop. Truest to elapsed time, but non-deterministic and untestable natively — the stubs record no time. | |

**User's choice:** "you decide" → Claude selected **pulse widths only**.
**Notes:** The deciding factor was testability: native stubs leave `delay()` unstubbed, so a
wall-clock rule could not be proven off-hardware at all.

### Distinguishing which limit tripped

| Option | Description | Selected |
|--------|-------------|----------|
| One message + reason byte | Single write-failed message carrying address, pulse count and a reason discriminator. One host parser, one ID. *(Recommended, on a flash-cost argument that turned out to be wrong.)* | |
| Distinct message ID per limit | Separate `MSG_ERR_*` IDs for max-pulses and energy-cap exhaustion. Self-describing on the wire and in the host's message table. | ✓ |
| No discriminator | Address + pulse count only; let the reader infer. The host holds no copy of the table, so it cannot. | |

**User's choice:** Distinct message ID per limit.
**Notes:** **The option text overstated the cost of this choice.** It claimed two new IDs cost "two
codegen IDs plus two PROGMEM strings against very tight Uno-class flash". `messages.h` is in fact
**ID-only `#define`s** — the wording lives host-side — so the real cost is the extra call sites, not
PROGMEM strings. Corrected to the user immediately after the answer; the decision stands on better
ground than it was made on. The correction also surfaced that the canonical catalog lives in the
**meta** repo (`tools/catalog/messages.toml` + `sync_to_subrepos.sh`), which is what makes Phase 141
tri-repo.

### A pulse wider than the cap (`--pulse-us` > 50000)

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-flight refusal | Refuse in `configure_eprom` before any HV is enabled when `energy_cap_us > 0 && pulse_delay > energy_cap_us`. Fail-closed; clear message; firmware-side backstop for Phase 143's bounds. *(Recommended.)* | ✓ |
| Accept the uniform rule | First pulse crosses the cap, is allowed, byte hard-fails. Smallest flash, but applies an up-to-65 ms VPE pulse to silicon and reports it as a verify failure. | |
| Clamp the pulse to the cap | Silently shorten to 50 ms and proceed — a silent substitution of the requested width. | |

**User's choice:** Pre-flight refusal.

---

## Message-catalog scope (follow-up, raised by the distinct-IDs choice)

| Option | Description | Selected |
|--------|-------------|----------|
| Catalog + sync + regen only | Add the IDs to meta's `messages.toml`, sync and regenerate both sub-repos' generated files; no host CLI behaviour change. Phase 143's HOST-03 owns user-facing rendering. *(Recommended.)* | ✓ |
| Firmware-only, defer the catalog | Emit raw IDs now, author catalog entries in 143 — leaves an unrenderable message on any intermediate build and breaks Phase 144's parity leg if run before 143. | |
| Carry it through to the CLI | Also wire host-side surfacing — takes HOST-03 out of Phase 143 and puts host CLI work in a firmware-scoped phase. | |

**User's choice:** Catalog + sync + regen only.

---

## Claude's Discretion

Delegated in full (CONTEXT.md D-05…D-12), plus D-02 delegated explicitly during the discussion:

- **D-02** — what counts toward the energy total (answered "you decide").
- **D-05** — reuse `firestarter_set_data`/`get_data` as the pulse and verify primitives; no
  EPROM-local duplicate write path.
- **D-06** — the 32-bit-safe delay helper lives beside `mem_util_*` and is applied at **both**
  `delayMicroseconds(handle->pulse_delay)` sites (`memory.cpp:329`, `eprom.cpp:283`); structured as a
  pure split so the arithmetic is unit-testable.
- **D-07** — the overprogram pulse uses the existing `org_delay` save/restore idiom, not a new width
  parameter on the primitive.
- **D-08** — LOOP-03 proven through a pure `(pulse_count, pulse_us, factor, cap_us)` function, since
  `overprogram_factor = 0` on all three shipped rows; the end-to-end path is a named non-claim.
- **D-09** — the DIP32 `CTRL_VPP_VPE_DROP_ENABLE`/A16 collision gets an explicit guarded path plus a
  test; the route choice stays Phase 142's.
- **D-10** — `native_trace_v131` goes RED and is **not** re-frozen here; the phase authors its own
  sixth native env instead, on the `native_params_v131` precedent.
- **D-11** — the D-13 protocol-branch-inventory gate goes RED and is re-derived by its own scanner,
  never hand-edited; the tier-2 shrinkage is recorded as evidence of LOOP-02's removals.
- **D-12** — no chunking or progress emission here, but the loop stays shape-compatible with
  `mem_util_blank_check`'s progress pattern for Phase 143.
- Free within those: function decomposition and naming, counter widths, helper signatures, the sixth
  env's name and plumbing, plan and wave structure.

## Findings surfaced during discussion

- **Milestone C3 needs a correction, and it is this phase's to name.** Measured live during the
  discussion: **zero** chips in the shipped `chip_database.json` carry a pulse above 1000 µs. But
  `--pulse-us` is a uint16 (65535 µs ceiling), 4× `delayMicroseconds()`'s limit — so C3's "no bare
  pulse comes near it" is true of the database and false of the CLI. With `overprogram_factor = 0`
  everywhere, `--pulse-us` is the **only** live caller LOOP-07's helper will have. → Phase 146 /
  CLOSE-04, alongside F-140-05 and F-140-07.
- **Phase 143 may not be host-only.** The roadmap calls it "independent of 140–142 (different repo)",
  but HOST-02's own named precedent (the blank-check progress/chunk pattern, `memory.cpp:379-413`) is
  a **firmware** pattern. Flagged before Phase 143 plans, not after.
- **Phase 141 is tri-repo**, not dual-repo as the milestone framing implies — the message catalog
  lives in meta.

## Deferred Ideas

All routed to their owning phase in CONTEXT.md `<deferred>`: VPP routing consolidation and the
DIP32 route choice (Phase 142); `--pulse-us` bounds, host timeout/progress, and rendering the new
message IDs (Phase 143); trace freeze/diff, TEST-01's flip, and the flash/RAM reconciliation
(Phase 144); the three published-text reconciliations and the `0x07` family-split candidate
(Phase 146); F-138-05 (inherited, owner `henols`). No scope creep was raised during the discussion.
