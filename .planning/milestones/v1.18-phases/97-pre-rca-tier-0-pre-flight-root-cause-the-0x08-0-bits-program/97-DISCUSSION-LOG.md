# Phase 97: PRE + RCA — Tier-0 Pre-Flight & Root-Cause the 0x08 0-Bits-Programmed Fault - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-29
**Phase:** 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-programmed-fault
**Areas discussed:** Micro-probe timing, RCA exit bar, Pin-31 measure method, Deferral disposition

> The research brief (`.planning/research/v1.18-AM27C020-27C-EPROM.md`) already locked the RC-1..RC-5 ranking, the 5-step Tier-0 protocol, the VPP-measurement method, the hardware (Leonardo + Rev 2.0), and the SAFE invariant. Those were carried forward, not re-asked. The four areas below are the gray areas the operator selected for discussion.

---

## Micro-probe timing

| Option | Description | Selected |
|--------|-------------|----------|
| Fold into RCA-01 write | Micro-probe = the RCA-01 reproduction write at 0x0000; one attempt; 0 flips ⇒ failure reproduced + writability indeterminate; any flip ⇒ RC-5 total-block OUT. No separate destructive spend. | ✓ |
| Separate probe, now | Distinct micro-probe step before RCA, same destructive footprint but tracked separately. | |
| Defer probe to post-fix | No destructive 1→0 in Phase 97 at all; writability micro-probe deferred to Phase 99. | |

**User's choice:** Fold into RCA-01 write.
**Notes:** On the broken path a 0-flip is expected and non-destructive; it cannot prove writability, so PRE-01's Phase-97 verdict is "writability indeterminate pre-fix." Definitive writable/dead call slips to the post-fix Phase 99 bench. (CONTEXT D-01, D-02.)

---

## RCA exit bar

| Option | Description | Selected |
|--------|-------------|----------|
| Resolve the converging pair | RC-1 (PGM pin 31) and RC-2 (P1 VPP level) each individually confirmed-or-exonerated before handoff; RC-3/RC-4 only if the pair doesn't account for 0-bits. | ✓ |
| First confirmed cause | Stop at the first confirmed cause (likely RC-1); treat any remaining axis as a Phase 98 discovery. | |
| Exhaust RC-1..RC-4 | Bench-disconfirm/confirm every ranked cause before handoff. | |

**User's choice:** Resolve the converging pair.
**Notes:** RC-1 and RC-2 may compound — a one-axis fix could still flip 0 bits. (CONTEXT D-03.)

---

## Pin-31 measure method

| Option | Description | Selected |
|--------|-------------|----------|
| Held-rail static proxy + code | Freeze the program-time control register via `dev reg ... -f`; operator DMMs pin 31 & pin 1 steady-state; backed by bus-line-22/addr-bit-18 code-analysis; LA optional. | ✓ |
| Logic analyzer / probe | Capture the live 100µs pulse with an LA/logic probe on pin 31. | |
| Code-analysis primary | Code-analysis as the primary RC-1 verdict; DMM only a confirmation spot-check. | |

**User's choice:** Held-rail static proxy + code.
**Notes:** A handheld DMM can't resolve the ~100µs pulse; the held-rail proxy (proven v1.14) makes pin 31 statically measurable. Code-analysis note: a 256K chip never sets A18, so pin 31 may idle VIL (program-active) — bench confirmation decides RC-1. (CONTEXT D-05.)

---

## Deferral disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Path-exonerated, still 0 bits | Deferral is a Phase 99 verdict: only after RC-1+RC-2 fixes applied and bench-confirmed correct (pin 1 12.5–13.0V, pin 31 VIL) AND still 0 bits ⇒ silicon/OTP ⇒ FUT-06, re-scope software-fix-only, worded clean like W29C040. | ✓ |
| Positive OTP evidence in 97 | Allow an earlier OTP/dead call in Phase 97 on positive silicon evidence (e.g. control-chip writes clean same bench). | |
| Single fix candidate | Defer after just one fix candidate (RC-1 PGM) bench-fails. | |

**User's choice:** Path-exonerated, still 0 bits.
**Notes:** A 0-flip before the path is fixed never triggers deferral; the OTP/dead verdict requires the path exonerated first. (CONTEXT D-06.)

---

## Claude's Discretion

- Concrete command sequencing, cheapest-first disconfirmation ordering, and the held-rail control-register value(s) used for the pin-31 static proxy — within the locked RC ranking and 5-step Tier-0 protocol.

## Deferred Ideas

- The Phase 98 fix itself (PGM-pin assertion concept, P1 routing held across the pulse window, a dedicated `DIP32_27C020` pinout) — diagnostic-only phase; governed by the RCA-03 verdict.
- FUT-05 (REWR-02 `0x08` rewritable write proof, W27E040) — separate deferred requirement.
- No pending todos folded (none touch the 0x08 write-path RCA).
