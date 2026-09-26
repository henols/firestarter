# Phase 78: X88C64 0x34 Firmware Handler - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-22
**Phase:** 78-x88c64-0x34-firmware-handler
**Areas discussed:** ALE-routing (method & deferral bar), Physical readiness for the graduation gate, Pinout entry strategy, Flash-ceiling contingency

---

## ALE-routing: investigation method & deferral bar (gating XIC-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Trace-first, defer if no clean bit | Claude schematic + rurp_pinout.h + register-utils trace; close A6 PCB-blocked unless a free CTRL_* bit or zero-risk reuse exists | ✓ |
| Attempt creative reuse before deferring | Trace + actively evaluate multiplexing an existing line; defer only if unworkable | |
| Operator bench-traces the hardware | Operator physical continuity/multimeter trace; highest confidence, needs bench time | |

**User's choice:** Trace-first, defer if no clean bit.
**Notes:** Scout pre-finding (8-bit control register fully allocated, bit 0x100 needs a 16-bit port the ATmega lacks) makes PCB-block deferral the expected landing. Conservative, honors the milestone "no blind handler" rule.

### Follow-up: deferral deliverable

| Option | Description | Selected |
|--------|-------------|----------|
| Trace conclusion + future-unblock spec | Record A6 verdict in X88C64-FEASIBILITY.md AND a short "what would unblock this" note (PCB mod / shield-rev bit / dedicated ALE pin); FUT-01 actionable | ✓ |
| Trace conclusion only | Record A6 verdict only; leave FUT-01 unchanged; defer unblock design to future milestone | |

**User's choice:** Trace conclusion + future-unblock spec.
**Notes:** Makes FUT-01 actionable later without committing handler code (honors SC#1).

---

## Physical readiness for the graduation gate (XIC-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Have both — graduation reachable | X88C64P + DIP24→DIP32 adapter on hand | |
| Have chip, no adapter | Adapter-gated, couples to Phase 80 | |
| Have neither — expect handler-only | No chip; graduation hardware-blocked like Phase 80 | ✓ |
| ALE likely blocks first anyway | Treat physical readiness as moot | |

**User's choice:** Have neither — expect handler-only.
**Notes:** SC#4 graduation is hardware-blocked regardless of the ALE verdict — no chip to run the N≥5 SHA-match.

### Follow-up: handler-write branch if ALE proves feasible but no chip

| Option | Description | Selected |
|--------|-------------|----------|
| Write handler + native test, defer graduation | Build configure_x88c64 + Tier-1 native test + wire round-trip + flash gate; leave chip refused; graduation waits for hardware | ✓ |
| Hold handler until chip in hand | Document A6 feasible but write no speculative firmware; defer all handler code | |

**User's choice:** Write handler + native test, defer graduation.
**Notes:** Banks the hardware-independent firmware work while context is hot; does NOT perform the SC#4 flip / host-guard removal without a bench SHA-match.

---

## Pinout entry strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated DIP24_X88C64 entry | Explicit ALE/WR/RD/WC/AD-bus mapping, no blast radius on DIP24_6116 | |
| Reuse DIP24_6116 | Zero churn but entry mislabels the bus | |
| You decide (planner's call) | Capture A7 as a research flag, let planner decide from host wire-config consumption | ✓ |

**User's choice:** You decide (planner's call).
**Notes:** Captured as a research flag, not a locked decision. Only relevant on the handler-write branch.

---

## Flash-ceiling contingency (XIC-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Stop & report, operator decides | Treat >~90% as a hard gate failure, escalate immediately | |
| Optimize first, then report | Attempt low-risk size cuts (28c helpers, PROGMEM, trim), re-measure, escalate only if still over | ✓ |
| Moot — deferral likely, no handler | Keep the gate dormant, don't over-spec | |

**User's choice:** Optimize first, then report.
**Notes:** Leonardo ~89.5% / ~3 KB free; handler est. ~1–3 KB.

---

## Claude's Discretion

- Pinout entry strategy (A7) — reuse DIP24_6116 vs. dedicated DIP24_X88C64; planner decides from host wire-config consumption.
- Handler file/header layout, `0x34` constant naming, Tier-1 test scaffold shape — consistent with `eeprom_28c` / `test_val_flash4` patterns.

## Deferred Ideas

None — discussion stayed within phase scope.
