# Phase 98: FIX — Correct the 0x08 32-Pin Write/VPP Path - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-30
**Phase:** 98-fix-correct-the-0x08-32-pin-write-vpp-path
**Areas discussed:** Fix breadth, Pin-31 redirect scope, Wire-field appetite, Phase-99 decisiveness

---

## Fix Breadth (no-bench, blind fix)

| Option | Description | Selected |
|--------|-------------|----------|
| Named surfaces only | DIP32_27C020 pinout + hold CTRL_VPP_P1_ENABLE across full pulse; let Phase 99 bench arbitrate; accept possible 99→98 round-trip | |
| Belt-and-suspenders | Named surfaces PLUS explicit firmware PGM-pulse/program-sequence so pin 31 is deliberately asserted; maximizes one-trip Phase 99 success; higher regression risk | ✓ |
| Minimal single surface | Only the single most-defensible change (likely the pinout); lowest blast radius, most likely to need a round-trip | |

**User's choice:** Belt-and-suspenders
**Notes:** Motivated by the Phase-97 verifier's nuance — pin 31 is already physically VIL on a 256K chip, so the pinout-redirect alone may not move the signal. Deliberately asserting PGM during the CE pulse is the architecturally correct response and best chance of a single-trip Phase-99 pass. Accepted cost: touches the shared program pulse → D-04 alias guard + D-05 trace discipline become hard constraints.

---

## Pin-31 Redirect Scope (don't break 27C040 / SST39SF040)

| Option | Description | Selected |
|--------|-------------|----------|
| New DIP32_27C020 pinout class | Dedicated host pinout assigned only to 0x08 ≤256K chips; data-driven scope; diff_db.py-reviewable | ✓ |
| New pinout + firmware protocol gate | DIP32_27C020 AND a firmware 0x08+32-pin branch; belt-and-suspenders so neither layer alone leaks behavior | |
| Firmware protocol gate only | No new pinout; gate PGM/P1-hold in firmware on 0x08+32-pin; smaller DB footprint but mixes concerns | |

**User's choice:** New DIP32_27C020 pinout class
**Notes:** Clean, data-driven, follows the DIP32_SST39SF040 precedent. 27C040 (A18) and SST39SF040 (WE) stay on existing pinouts, untouched. (The planner will still likely pair this with a protocol gate for the firmware PGM-assert per D-01 belt-and-suspenders + D-04 guard — but the *redirect mechanism* is the pinout class.)

---

## Wire-Field Appetite (lockstep blast radius)

| Option | Description | Selected |
|--------|-------------|----------|
| DB/pinout-only if possible | Express via new pinout + existing CTRL_* bits; new wire field only if firmware genuinely needs it | ✓ |
| New wire field OK | Greenlight a new control-pin wire field up front (page_size precedent) | |
| You decide | Planner picks based on the fix mechanism | |

**User's choice:** DB/pinout-only if possible
**Notes:** Interaction flagged with D-01 — belt-and-suspenders wants firmware to deliberately assert PGM, while this answer constrains new wire fields. Resolution: planner tries pinout-mapping + protocol-0x08 gate using existing control bits first; escalate to a new wire datum only as a last resort.

---

## Phase-99 Decisiveness (separate "fix worked" vs "chip OTP/dead")

| Option | Description | Selected |
|--------|-------------|----------|
| Add a pin-31 state diagnostic | Expose/log pin-31 (PGM) + P1 control-register state during the program window (held-rail-checkable) so Phase 99 can confirm deliberate assertion | |
| Pure fix, no extra instrumentation | Keep Phase 98 strictly the code fix + native tests; rely on Phase 99 DMM + write→verify + held-rail proxy | |
| You decide | Planner decides whether diagnostic hooks are worth the added surface | ✓ |

**User's choice:** You decide
**Notes:** Captured as Claude's-discretion in CONTEXT.md — add the diagnostic hook only if worth the added surface; otherwise Phase 99 reads state via DMM + held-rail proxy.

---

## Claude's Discretion

- Whether to add a Phase-99 pin-31/P1 state diagnostic hook (the 4th area, deferred to planner judgment).
- Concrete firmware sequencing for the PGM assert, exact CTRL_* composition, held-rail validation register value, and the precise gate predicate (protocol 0x08 + 32-pin + A18-unused).

## Deferred Ideas

- Phase 99 bench graduation (write→verify, EVIDENCE, PROTOCOL-LEDGER update, D-06 OTP/dead verdict) — gated on PRE-01.
- FUT-05 (REWR-02 0x08 rewritable write proof, W27E040) — separate deferred requirement, not v1.18 scope.
- No pending todos folded — none touch the 0x08 write-path fix.
