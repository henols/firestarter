# Requirements: Firestarter v1.9 — Read-Bug RCA + Fix

**Defined:** 2026-05-29
**Milestone goal:** Root-cause and fix the EPROM read-bug deferred since v1.6, restoring N≥5 byte-identical reads across the shield fleet (Modified Rev 0, Rev 2.0, Rev 2.2). Inherits the v1.6 `dev consistency-check` diagnostic, the 15-binary N=5 W27C512 bench substrate, the Phase 29 v2 Bug A/Bug B characterization, the v1.7 schematics + shield-version-detect plumbing, and the v1.8 cleaned-up host read path (GATE-1.8d ring-fence intact → baselines still valid).

**Scope locked:** 2026-05-29 via `/gsd-new-milestone`. Phase numbering continues at **Phase 44** (after v1.8's last phase 43).

**Hardware-gated:** all bench operations are operator-authorized (shield swaps, reads, A/B fix trials). Firmware sub-repo work is expected (unlike v1.8's host-only scope). Per `feedback_chip_out_before_sideload`, the chip leaves the socket before any firmware sideload; per `feedback_verify_port_identity_each_task`, controller identity is verified per port at each bench task; per `user_shield_revisions`, the operator is asked which silkscreen rev is on the bench (the EEPROM hw_revision byte can't distinguish them).

## v1.9 Requirements

### 1. Root-Cause Analysis (RCA) — prove the mechanisms

- [x] **RCA-01**: Bug A root cause proven — the Modified Rev 0 upper-address (A15=1) jitter is instrumented to a definitive signal-integrity mechanism (ringing / crosstalk / settling-time), beyond the Phase 29 v2 characterized symptom (1.86× skew, 63% bit-raise).
- [ ] **RCA-02**: Bug B root cause proven — the Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch + VPP=13.1V failure is instrumented to a definitive root cause.
- [x] **RCA-03**: Per-rev failure-mode map confirmed — which of Modified Rev 0 / Rev 2.0 / Rev 2.2 exhibits which bug, using the v1.7 shield-version-detect plumbing so each bench step knows the silkscreen rev in play.

### 2. Fix Candidates (FIX) — instrumented A/B

- [ ] **FIX-01**: Bug A fix candidate(s) designed and A/B-tested, restoring byte-identical reads on Modified Rev 0 (address settling / slew / firmware-timing strategy informed by RCA-01).
- [ ] **FIX-02**: Bug B fix candidate(s) designed and A/B-tested on Rev 2.0 (timing/voltage strategy informed by RCA-02).
- [ ] **FIX-03**: Fix(es) regression-checked across the shield fleet — no fix for one rev breaks reads on another.

### 3. Verification & Acceptance (VERIFY)

- [ ] **VERIFY-A**: Phase 29 acceptance gate re-run — N≥5 byte-identical W27C512 reads across boards with the fix applied (the milestone's headline acceptance gate).
- [ ] **VERIFY-01**: uno328pb byte-identity closed (carried forward from v1.6 backlog).
- [ ] **VERIFY-03**: 1KB low-rate jitter closed (carried forward).
- [ ] **VERIFY-04**: Phase 24 BENCH-02 closure (carried forward).

### 4. Serial Data-Path Robustness (COBS) — evaluation

- [x] **COBS-01**: Evaluate COBS framing/resync on the serial data path; re-assess PacketSerial vs a custom COBS layer and record an **adopt / defer / reject** decision with rationale. Explicitly complementary to the hardware RCA — NOT a Bug A fix (Bug A is hardware upper-address jitter, not a serial-framing fault).

### 5. Post-RCA Cleanup (TYPE)

- [ ] **TYPE-01**: Lift the `eprom_operations.py` mypy strict-mode overrides (deferred per Phase 42 D-07 while the read path was ring-fenced) once the read path is fixed and free to touch.

## Out of Scope (v1.9)

- **New chip-family support / database expansion** — v1.9 is read-path RCA only; the W27C512 misclassification todo and the 28-/32-pin algo validation (paused v1.3 phases 11/12) are separate tracks.
- **Adopting COBS/PacketSerial as a committed rewrite** — v1.9 only *evaluates* and decides (COBS-01); any adoption is a future milestone if the decision is "adopt".
- **Stable `3.0.1` release** — deferred until a real read-bug fix lands and is bench-verified; v1.9 may cut a new beta but stable promotion is a separate gate.
- **avrdude MCU-detection fallback** (pending todo) — firmware-sideload recovery, unrelated to the read path.

## Future Requirements (deferred)

- COBS/PacketSerial adoption + protocol migration (if COBS-01 decides "adopt").
- Broader signal-integrity hardening across all read-capable chip families beyond W27C512.

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| RCA-01 | Phase 44 | Complete |
| RCA-02 | Phase 45 | pending |
| RCA-03 | Phase 45 | Complete |
| FIX-01 | Phase 46 | pending |
| FIX-02 | Phase 46 | pending |
| FIX-03 | Phase 46 | pending |
| VERIFY-A | Phase 47 | pending |
| VERIFY-01 | Phase 47 | pending |
| VERIFY-03 | Phase 47 | pending |
| VERIFY-04 | Phase 47 | pending |
| COBS-01 | Phase 48 | Complete |
| TYPE-01 | Phase 48 | pending |
