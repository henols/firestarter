---
phase: 97
slug: pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-29
---

# Phase 97 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> **This is a diagnostic / RCA phase — no firmware/host source changes.** Its "tests" are
> **bench measurements and file:line code-analysis findings**, not unit tests. No native/host
> test suites run in Phase 97 (those gate Phases 98–99). Validation here = the RC-1..RC-5
> disconfirmation logic + artifact completeness + the read-oracle/SAFE-01 gates.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Bench measurement (held-rail DMM at socket pin 1/pin 31 + VPP ADC readback) + file:line code-analysis |
| **Config file** | none — no test harness is invoked this phase |
| **Quick run command** | `firestarter dev consistency-check AM27C020 --runs 3` (the read-oracle gate, N≥3 byte-identical) |
| **Full suite command** | the combined Tier-0+RCA-01 bench procedure + the 0x07 differential + the SAFE-01 code-read |
| **Estimated runtime** | ~bench-paced (operator-gated; not wall-clock bounded) |

---

## Sampling Rate

- **Per bench task:** re-confirm `controller:` identity + live R1/R2 readback (`firestarter hw`) before any measurement (D-08).
- **Read verdict gate:** N≥3 byte-identical reads before trusting any write outcome (never N=1 — v1.15 saw a localized 12-byte glitch at 0x008004–0x00800f).
- **Phase gate (before `/gsd-verify-work`):** RC-1 AND RC-2 each carry a recorded verdict (D-03) + EVIDENCE row complete + RCA-FINDINGS doc written.
- **Max feedback latency:** N/A (bench-paced; no automated loop).

---

## Per-Task Verification Map

> Task IDs are assigned by the planner. The requirement→validation rows below are the
> authoritative validation contract; the planner maps each to concrete task IDs/waves.

| Req | Behavior to validate | Test Type | Method / Command | Threat Ref | Status |
|-----|----------------------|-----------|------------------|------------|--------|
| PRE-01 | read oracle stable (N≥3), blank-state SHA recorded, identity/decode confirmed, single 1→0 micro-probe attempt documented (never fabricated) | bench | `firestarter info` + `dev consistency-check AM27C020 --runs 3` + blank-state read+SHA + one `write` attempt at 0x000000 | — | ⬜ pending |
| RCA-01 | 0x08 0-bits failure reproduces with full signature (failing bytes, VPP ADC readback, DMM pin 1 + pin 31, PGM state) | bench | combined procedure steps 1–6 + Failure Signature Capture Schema | T-97 SAFE-01 | ⬜ pending |
| RCA-02 | differential isolates the 32-pin / P1-VPP / PGM-pin axes; 0x07 W27C512 exonerates unchanged axes | bench | passing `0x07` control write, same session/bench, single-session differential matrix | — | ⬜ pending |
| RCA-03 | RC-1 (PGM pin 31 as address line) AND RC-2 (P1 VPP routing/level) each carry a confirm-or-exonerate verdict; root cause named + classified | analysis | disconfirmation table + `dev reg 0 0 0x180` vs `0x188 -f` held-rail experiment + code-analysis; RCA-FINDINGS doc | — | ⬜ pending |
| SAFE-01 | over-voltage ERROR path intact, `resolve_chip` guard never bypassed, no test-only escape hatch | code-read | grep/file:line confirm `vpp_check_window` HIGH→ERROR (primitives.cpp:122-126) + `resolve_chip` in live path; non-invasive | T-97 SAFE-01 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- All driving commands (`dev consistency-check`, `dev reg -f`, `vpp`/`vpe`, `info`, `write`, `read`) are verified present in the live CLI — **no test infrastructure to build.**
- The only "scaffold" is the artifact files the phase emits (EVIDENCE row + RCA-FINDINGS doc + SAFE-01 note + PRE-01 result line — see RESEARCH.md §"Artifacts the Phase Should Emit").

*Existing bench/CLI infrastructure covers all phase requirements.*

---

## Manual-Only Verifications

> This phase is **entirely manual/bench by design** — the diagnostic verdicts come from
> operator DMM readings + Claude-driven CLI captures + code-analysis, not automated tests.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| DMM at socket pin 1 (VPP) and pin 31 (PGM) during the program window | RCA-01, RCA-03 (RC-1/RC-2) | Handheld DMM cannot resolve the ~100µs pulse → use held-rail static proxy (`dev reg ... -f`); physical probe is operator-only | Freeze program-time control register, operator reads pin 1 + pin 31 steady-state; record vs expected 12.5–13.0V (pin 1) and VIL (pin 31 if RC-1 true) |
| JP4 (`JMP_VPP_P1_BYPASS`) position confirmation | RCA-02 (RC-3, conditional) | Physical jumper; EEPROM hw byte cannot distinguish shield revs | **ASK operator the exact Rev 2.0 silkscreen / open-vs-closed meaning before measuring or toggling** |
| Chip seating + irreversible micro-probe | PRE-01, RCA-01 | UV part, no eraser on hand → every program is irreversible | Operator seats AM27C020; single program attempt at 0x000000 only (D-01) |

---

## Validation Sign-Off

- [ ] Every requirement (PRE-01, RCA-01, RCA-02, RCA-03, SAFE-01) has a bench or code-analysis verification method
- [ ] RC-1 AND RC-2 each have a recorded confirm-or-exonerate verdict (D-03)
- [ ] Read-oracle gate (N≥3 byte-identical) precedes every write verdict
- [ ] PRE-01 result documented as "writability indeterminate pre-fix" (or "partial — N bits flipped") — never fabricated (D-02)
- [ ] SAFE-01 verified non-invasively (no bypass, no escape hatch)
- [ ] `nyquist_compliant: true` set in frontmatter after planning sign-off

**Approval:** pending
