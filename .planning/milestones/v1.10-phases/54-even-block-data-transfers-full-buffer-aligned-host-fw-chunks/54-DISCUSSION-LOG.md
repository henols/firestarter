# Phase 54: Even-Block Data Transfers (full-buffer-aligned host→fw chunks) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-04
**Phase:** 54-even-block-data-transfers-full-buffer-aligned-host-fw-chunks
**Areas discussed:** Decoupling mechanism, FW advertise / where −2 dies, Breaking-change posture, Verification gates

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Decoupling mechanism | Grow buffer vs CRC8 out-of-band vs data-path NUL-skip vs research-decides | ✓ |
| FW advertise / where −2 dies | Advertise effective capacity vs host-drops-−2 vs research | ✓ |
| Breaking-change posture | Beta lockstep vs graceful fallback vs handshake guard | ✓ |
| Verification gates | Regression-test home + RAM-fit close gate | ✓ |

**User's choice:** All four areas.

---

## Decoupling mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Data-path NUL skip (research-confirm) | Lift NUL reservation on write-receive path only; full 512 fits, zero RAM | |
| Grow decode buffer | Size buffer to full block + NUL; spends Uno RAM | |
| CRC8 out-of-band | Carry CRC8/length outside COBS payload; touches frozen contract | |
| Let research decide | Capture all candidates; RESEARCH.md scores + recommends | ✓ |

**User's choice:** Let research decide.
**Notes:** Tie-breaker follow-up asked. User: *"No preference, but breaking the contract is not an
issue and I want it to be as dynamic as possible."* → contract-breaking explicitly PERMITTED for this
phase (relaxes Phase 49/52 frozen status); optimise for a dynamic/board-parameterized solution with no
hardcoded per-board constants. Recorded as CONTEXT D-01/D-02/D-03.

---

## FW advertise / where −2 dies

| Option | Description | Selected |
|--------|-------------|----------|
| Advertise effective decode capacity | New identity-string field; host uses it exactly | ✓ |
| Keep ':buf', host drops the −2 | Advertisement unchanged; host derives full chunk from buffer | |
| Let research/planner decide | Capture both; pick to fit the chosen decoupling mechanism | |

**User's choice:** Advertise effective decode capacity.
**Notes:** Makes the buffer-RAM ↔ usable-chunk decoupling explicit on the wire; aligns with the
"as dynamic as possible" steer. Recorded as CONTEXT D-04.

---

## Breaking-change posture

| Option | Description | Selected |
|--------|-------------|----------|
| Beta lockstep, no mixed-version interop | Host+FW upgrade together; host assumes new field present | ✓ |
| Graceful fallback to buf−2 | New host falls back for old firmware | |
| Add a handshake/capability guard | Negotiate/verify even-block capability, refuse mismatches | |

**User's choice:** Beta lockstep, no mixed-version interop.
**Notes:** Carries Phase 50 D-03 — no fallback branch; host may assume the capacity field present.
Beta-only. Recorded as CONTEXT D-05.

---

## Verification gates

**Q1 — Regression-test home:**

| Option | Description | Selected |
|--------|-------------|----------|
| Extend Phase 52 golden-vector corpus | Add full-buffer round-trip vectors to vendored catalog | |
| Dedicated EVEN regression test | Separate no-remainder/division + decode round-trip test | |
| Both | Vectors pin bytes; dedicated test asserts whole-block division | |

**User's choice:** "Your choice" → Claude's discretion (CONTEXT D-09). Recommendation: extend the
Phase 52 corpus + a small no-remainder assertion (D-07).

**Q2 — RAM-fit close gate:**

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit close gate | Uno + uno328pb RAM report under ~545 B ceiling as hard criterion | ✓ |
| Only if mechanism grows RAM | Skip the gate for a zero-growth outcome | |

**User's choice:** Explicit close gate (CONTEXT D-08) — required even for a zero-growth mechanism.

---

## Claude's Discretion

- Regression-test exact shape and home (D-09) — leaning extend-Phase-52-corpus + no-remainder assertion.
- Identity-string capacity-field name/format (D-04).
- Internal decoder cap parameterization for the chosen mechanism (D-01), subject to the RAM gate (D-08).

## Deferred Ideas

- **WR-01** — frame-level decoder byte-wait deadline; behavior change, distinct from even-block sizing,
  though Phase 54 edits the same decoder. Reviewed, not folded.
- **`avrdude-mcu-detection-fallback`**, **`w27c512-eeprom-misclassification`** — unrelated; no overlap.
