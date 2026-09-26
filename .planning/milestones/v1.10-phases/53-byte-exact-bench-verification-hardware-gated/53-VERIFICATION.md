---
phase: 53-byte-exact-bench-verification-hardware-gated
verified: 2026-06-05T16:00:00Z
status: passed
score: 8/8 must-haves verified
resolution: "The sole human_needed item (REQUIREMENTS.md XACT-03 bookkeeping) was applied post-verification: line 41 checkbox [ ]->[x] and traceability table Pending->Complete. The verifier confirmed all XACT-01/02/03 bench evidence is complete; no bench work remained. Status flipped human_needed->passed."
overrides_applied: 0
overrides:
  - must_have: "N consecutive framed read+write transfers byte-identical on Uno + Leonardo (reproducing the GATE-1.8d W27C512 N=5 baselines)"
    reason: "D-05 allows self-consistency when the original baseline chip is absent. Neither chip on the bench this session was the 19710f6e baseline. Self-consistency form is the operator-accepted achieved form; the GATE-1.8d relation is explicitly recorded as 'self-consistency-only' in both the sha256sums files and SUMMARY.md. The phase goal language 'reproducing the baselines' is satisfied in this self-consistency form by operator authorization."
    accepted_by: "operator (henrik@predictly.se)"
    accepted_at: "2026-06-05T14:08:00Z"
human_verification:
  - test: "Confirm REQUIREMENTS.md XACT-03 checkbox is updated"
    expected: "Line 41 changes from '- [ ] **XACT-03**' to '- [x] **XACT-03**' and the traceability table row changes from 'Pending' to 'Complete'. The evidence (exoneration-verdict.txt with verbatim §2.0 line, timeout-retry-log.txt, and the SUMMARY.md XACT-03 section) is committed and satisfies the requirement as stated — the checkbox is a documentation-only update."
    why_human: "REQUIREMENTS.md is a planning artifact that only the operator/orchestrator should update to mark phase closure. The bench evidence satisfies XACT-03 in full (before/after shape, exoneration line, RCA-deferred note), but the checkbox on line 41 still reads '[ ]' and the traceability table still says 'Pending'. This is a documentation gap, not an evidence gap."
gaps: []
deferred: []
---

# Phase 53: Byte-Exact Bench Verification — Verification Report

**Phase Goal:** Operator-authorized bench proof: N consecutive framed read+write transfers byte-identical on Uno + Leonardo (reproducing the GATE-1.8d W27C512 N=5 baselines); fault-injection resync proven within one packet; uno328pb re-test recorded (transport-exoneration, not a hardware fix).

**Verified:** 2026-06-05T16:00:00Z
**Status:** human_needed — one documentation update pending (REQUIREMENTS.md XACT-03 checkbox)
**Re-verification:** No — initial verification

---

## Context: Operator-attested bench evidence

This is a hardware-gated, operator-witnessed bench phase. The deliverables are committed evidence artifacts under `.planning/v1.10/bench-verification/`, not runnable source code. Operator-attested bench evidence is treated as authoritative. The close-out-gaps audit (commit `37519af`, 09:53 UTC 2026-06-05) pre-dates the bench session; the actual bench evidence was committed in the afternoon (commits `9ccee1b` through `e395498`, 13:12–14:08 UTC). All SUMMARY files completed with 2026-06-05 dates reflect genuine completed bench work.

Known deviations pre-accepted per the verification brief:
- **Self-consistency (D-05):** no chip on the bench was the `19710f6e` baseline; self-consistency is the operator-accepted achieved form.
- **Write path uses plain `write -b`:** W27C512 standalone erase is firmware-"Not supported" on the 0x07 path; write→read-back==source verdict 0 is the achieved proof.
- **Leonardo VPP-high (13.1 V) guard force-bypassed (`-f`):** operator-authorized. Reads route no VPP.
- **uno328pb VPP 12.7 V:** non-fatal warning; board proceeded.
- **XACT-03 still-unstable uno328pb is PASS:** transport-exoneration requires the instability to persist on the hardened transport; it does.
- **XACT-02 latency path:** 53-04 required a harness false-negative fix (`firestarter_app 630fafd`), a `--mode latency` refinement (`8480ff3`), and a firmware drop-delimiter optimization (`firestarter 0266ee2`) to make the sub-second per-frame latency honestly demonstrable. Final measured values: corrupt-crc8 = 0.001 s; drop-delimiter = 1.001 s (single inter-byte deadline, optimized from ~2 s).

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | N=5 consecutive framed reads on clean Uno (512 B) are all SHA-256-identical to each other | VERIFIED | `clean-board-uno/read-leg/sha256sums.txt`: 5/5 `8144ae57…`, verdict 0. Post-55 fw `OK: FW: 3.0.0b6:uno`. |
| 2 | N=5 consecutive framed reads on clean Leonardo (1024 B) are all SHA-256-identical to each other | VERIFIED | `clean-board-leonardo/read-leg/sha256sums.txt`: 5/5 `25bae52d…`, verdict 0. Rev 2.0, operator-confirmed. |
| 3 | N=5 write→read-back==source per board (Uno + Leonardo) | VERIFIED | `clean-board-uno/write-leg/sha256sums.txt`: 5/5 == `8144ae57…`. `clean-board-leonardo/write-leg/sha256sums.txt`: 5/5 == `25bae52d…`. Both verdict 0. |
| 4 | Self-consistency form recorded (D-05): no original GATE-1.8d chip present, so baseline hash-match not attempted | VERIFIED (override) | Both sha256sums files explicitly record `≠ 19710f6e… → SELF-CONSISTENCY is the achieved form`. SUMMARY.md §Form repeats this. Override: D-05 explicitly allows self-consistency; operator-chosen. |
| 5 | A deliberately corrupted host→fw command frame surfaces a clean error immediately (sub-second for complete frames, single bounded deadline for truncated frames, NOT a 2 s cascade) AND the next transfer on the SAME open connection is byte-exact | VERIFIED | `latency-opt-corrupt-crc8-leonardo/`: per_frame_nak_latency=0.001 s, SUB-SECOND, recovery=True. `latency-opt-drop-delimiter-leonardo/`: per_frame_nak_latency=1.001 s, single bounded inter-byte deadline, recovery=True. Both fault forms, same-connection recovery. `FINDINGS-2026-06-05.md` documents the full arc (harness false-negative fix → RCA → latency measurement → firmware optimization). |
| 6 | A mutated fw→host frame triggers the host decoder resync (clean error, no hang) and the next frame decodes clean; both fault forms exercised | VERIFIED | `fault-inject-incoming-log.txt`: corrupt-crc8 and drop-delimiter both show `fault_fired: True`, host detection `CRC mismatch for ID 0x10: expected 0x70, got 0x71`, `recovery (clean follow-on byte-exact): PASSED`. No silent corruption. |
| 7 | uno328pb re-test on HARDENED firmware only: timeouts logged and retried (never aborted, never collapsed to verdict 1); structured D-10 exoneration verdict with verbatim §2.0 transport-exoneration line | VERIFIED | `uno328pb/timeout-retry-log.txt`: 5 attempts across the session; timeouts logged, verdict 2 (hw-error) preserved, never collapsed. `uno328pb/exoneration-verdict.txt`: before/after shapes, shape-changed=PARTIAL, verbatim line `transport-exoneration per v1.9-COBS-DECISION §2.0 — NOT a per-shield hardware fix; the actual RCA stays deferred to v1.9 Phase 45+.` |
| 8 | REQUIREMENTS.md XACT-03 checkbox and traceability row updated to reflect completion | UNCERTAIN | `REQUIREMENTS.md` line 41: `- [ ] **XACT-03**` (still unchecked); traceability row: `Pending`. The bench evidence fully satisfies the requirement, but the documentation flag was not updated after the 53-05 close-out. Requires human update. |

**Score:** 7/8 truths verified (1 override applied for D-05 self-consistency, 1 uncertain for REQUIREMENTS.md documentation update)

---

### Required Artifacts (per plan frontmatter must_haves)

#### 53-01/02 Software Harness

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/eprom_operations.py` | `write_cycle_eprom()` + `fault_inject_cycle()` | VERIFIED | `def write_cycle_eprom` at line 724; `def fault_inject_cycle` at line 835. 3-way verdict (0/1/2). |
| `firestarter_app/firestarter/serial_comm.py` | `_fault_inject_outgoing` attribute + `FaultInjectingSerialCommunicator` subclass | VERIFIED | `_fault_inject_outgoing = None` in `__init__` at line 114; `class FaultInjectingSerialCommunicator` at line 763. Getattr-guarded hook confirmed at line 195. |
| `firestarter_app/firestarter/cli_handlers.py` | `dev write-cycle` + `dev fault-inject` Click subcommands | VERIFIED | `@dev.command(name="write-cycle")` at line 1120; `@dev.command(name="fault-inject")` at line 1173. sys.exit(verdict_int) wiring confirmed. |
| `firestarter_app/tests/test_serial_comm.py` | Ring-fence compliance test pinning `_read_and_parse_lines` SHA-256 | VERIFIED | `test_read_and_parse_lines_ringfence_unchanged` at line 426; runs GREEN (confirmed by live pytest run). GATE-1.8d enforced. |

#### 53-03 Clean-board evidence (XACT-01)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `clean-board-uno/read-leg/sha256sums.txt` | Uno N=5 read SHA table, verdict 0 | VERIFIED | 5/5 `8144ae57…`, Rev 2.0, unforced. |
| `clean-board-uno/read-leg/run_01..05.bin` | Per-run binaries | VERIFIED | 5 files confirmed on disk. |
| `clean-board-uno/write-leg/sha256sums.txt` | Uno N=5 write read-back SHA table, verdict 0 | VERIFIED | 5/5 readback == source `8144ae57…`. |
| `clean-board-leonardo/read-leg/sha256sums.txt` | Leonardo N=5 read SHA table + GATE-1.8d comparison | VERIFIED | 5/5 `25bae52d…`; explicit `SELF-CONSISTENCY is the achieved form (D-05)` note. |
| `clean-board-leonardo/write-leg/sha256sums.txt` | Leonardo write→read-back SHAs vs source | VERIFIED | 5/5 readback == source `25bae52d…`. |

#### 53-04 Fault-injection evidence (XACT-02)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `fault-injection/fault-inject-outgoing-log.txt` | host→fw corruption evidence, both fault forms | VERIFIED | Corrupt-crc8 + drop-delimiter both documented. Correction note + FINDINGS reference included. Final per-frame latencies in `latency-opt-*-leonardo/`. |
| `fault-injection/fault-inject-incoming-log.txt` | fw→host mutation evidence | VERIFIED | Both fault forms: `fault_fired: True`, `CRC mismatch` detected, `recovery: PASSED`. |
| `fault-injection/latency-opt-corrupt-crc8-leonardo/fault-inject-corrupt-crc8-latency.txt` | Per-frame corrupt-crc8 latency, post-optimization firmware | VERIFIED | `per_frame_nak_latency: 0.001s`, `latency_verdict: SUB-SECOND`, `recovery_clean_command_same_connection_ok: True`. |
| `fault-injection/latency-opt-drop-delimiter-leonardo/fault-inject-drop-delimiter-latency.txt` | Per-frame drop-delimiter latency, post-optimization firmware | VERIFIED | `per_frame_nak_latency: 1.001s`, `latency_verdict: SUB-2s (bounded; ~inter-byte deadline)`, `recovery_clean_command_same_connection_ok: True`. |
| `fault-injection/FINDINGS-2026-06-05.md` | Full arc documentation (harness fix + RCA + latency + optimization) | VERIFIED | Exists; documents 4-combo matrix, firmware fast-NAK RCA, clean per-frame measurements, firmware optimization result. |

#### 53-05 uno328pb evidence (XACT-03)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `uno328pb/timeout-retry-log.txt` | Raw timeout + retry log across N=5 attempts | VERIFIED | 5 retry attempts, timeouts logged, never aborted; verdict 2 never collapsed to verdict 1. Raw consistency-check output included. |
| `uno328pb/exoneration-verdict.txt` | D-10 structured before/after + exoneration verdict block | VERIFIED | Before-shape cited from v1.6-EVIDENCE.md; after-shape quantified (PARTIAL shape change); verbatim §2.0 exoneration line; clarifying paragraph. D-08 verdict-integrity confirmation. |
| `uno328pb/attempt-1..5/` per-run binaries | However many runs completed | VERIFIED | `attempt-1` through `attempt-5` directories exist. |

#### 53-06 Milestone evidence artifact (SC4)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/v1.10/bench-verification/SUMMARY.md` | Aggregated SHA table, fault log, exoneration verdict, operator attestation, milestone claim | VERIFIED | File exists; contains operator attestation (boards, shield revs per D-07, date, bench caveats); full XACT-01/02/03 sections; self-consistency form stated; settled-variable milestone claim present; exoneration line present. 53-06 Task-2 completeness check conditions all pass (confirmed by direct grep/test commands). |

#### 53-07 Post-54/55 corpus extension

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `even-block-ack/fw-identity-raw.txt` | Verbatim raw FW identity wire line, pure `OK: FW: <ver>:<board>` (no suffix) | VERIFIED | ACM0/leonardo: `OK: FW: 3.0.0b6:leonardo` — exactly 2 colon-fields; ACM1/uno: `OK: FW: 3.0.0b6:uno` — 2 fields. Post-55 SC1 confirmed on real hardware. |
| `even-block-ack/chunk-evidence.txt` | 1024×64 ack-sourced + no-remainder + write full-buffer size | VERIFIED | Leonardo: read 1024 bytes ×64; write buffer size 1024 (not 1022); 65536 % 1024 == 0; ack-sourcing proof (host default 512, only MSG_OK_READY ack yields 1024). |
| `even-block-ack/read-leg/leonardo/sha256sums.txt` | N=5 read SHA table, verdict 0 | VERIFIED | 5/5 `de2f2560…`, verdict 0. |
| `even-block-ack/write-leg/leonardo/sha256sums.txt` | N=5 write read-back SHAs == source, verdict 0 | VERIFIED | 5/5 readback == source `de2f2560…`. |
| `even-block-ack/safe-512-note.txt` | Software-covered safe-512 attestation + self-sufficient operator attestation + 53-06 linkage recommendation | VERIFIED | Contains `ALREADY-COVERED-IN-SOFTWARE`, cites `TestCapSafeDefault` 3/3, self-sufficient operator attestation (board/rev/date/raw identity/chunks/verdicts), 53-06 linkage recommendation. Task-3 verify command: OK. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `dev write-cycle` CLI subcommand | `EpromOperator.write_cycle_eprom` | `app.eprom_operator.write_cycle_eprom(...); sys.exit(verdict_int)` | VERIFIED | `cli_handlers.py` line 1162; 3-way verdict passthrough confirmed (no bool-to-int wrap). |
| `send_json_command` in `serial_comm.py` | `self._fault_inject_outgoing` hook | `getattr(self, "_fault_inject_outgoing", None)` guard before `send_bytes` | VERIFIED | Line 195; production path byte-identical when hook is None. |
| `dev fault-inject` CLI | `fault_inject_cycle` + `FaultInjectingSerialCommunicator` | `fault_inject_cycle(direction, fault_form)` inside `dev_fault_inject` handler | VERIFIED | `cli_handlers.py` line 1229; `eprom_operations.py` lines 835+ implement the cycle. |
| `fault-inject-outgoing-log.txt` + `latency-opt-*-leonardo/` logs | firmware COBS decoder fast-NAK | measured per-frame NAK latency on established connection | VERIFIED | `latency-opt-corrupt-crc8-leonardo`: 0.001 s SUB-SECOND. `latency-opt-drop-delimiter-leonardo`: 1.001 s single bounded deadline. |
| `uno328pb/exoneration-verdict.txt` | v1.9-COBS-DECISION §2.0 + v1.6-EVIDENCE.md before-shape | verbatim exoneration line + cited before-shape | VERIFIED | Exact line `transport-exoneration per v1.9-COBS-DECISION §2.0 — NOT a per-shield hardware fix; the actual RCA stays deferred to v1.9 Phase 45+.` confirmed at line 40 of verdict file. |
| `bench-verification/SUMMARY.md` | all per-leg sub-artifacts | aggregated SHA table + fault log + exoneration verdict + attestation | VERIFIED | 53-06 completeness check conditions: SUMMARY_EXISTS, EXONERATION_OK, ATTESTATION_OK, UNO_RUN05_OK, LEONARDO_RUN05_OK — all confirmed. |

---

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| XACT-01 | 53-01, 53-02, 53-03, 53-07 | Transport proven byte-exact on clean Uno (512 B) + Leonardo (1024 B); N=5 reads + write→read-back==source | VERIFIED | Uno read 5/5 `8144ae57…` (verdict 0); Leonardo read 5/5 `25bae52d…` (verdict 0); both write legs verdict 0. 53-07 corpus extension: Leonardo 1024×64 ack-sourced + even-block, 5/5 `de2f2560…` (verdict 0) both legs. Self-consistency form (D-05), operator-accepted. REQUIREMENTS.md checkbox: [x]. |
| XACT-02 | 53-01, 53-02, 53-04 | Resync under fault injection: detect + recover within one packet; no 2 s cascade | VERIFIED | Corrupt-crc8: 0.001 s SUB-SECOND per-frame NAK + same-connection byte-exact recovery. Drop-delimiter: 1.001 s single bounded inter-byte deadline + same-connection recovery. Incoming (fw→host): CRC mismatch detected + next frame clean. Both fault forms, both directions. REQUIREMENTS.md checkbox: [x]. |
| XACT-03 | 53-01, 53-02, 53-05 | uno328pb re-test: failure shape on hardened transport documented; transport-exoneration per COBS-DECISION §2.0; NOT misread as hardware fix | VERIFIED (evidence complete; documentation gap) | `exoneration-verdict.txt`: before-shape cited (99.4% 0xff, 100% unstable, 4×N=5 timeouts); after-shape quantified (PARTIAL — floating-bus resolved, timeout + jitter persist, mean 15% pairwise divergence); shape-changed=PARTIAL; verbatim §2.0 line present. `timeout-retry-log.txt`: 5 attempts, verdict 2 never collapsed. REQUIREMENTS.md checkbox: still `[ ]` (documentation update pending — see human verification item). |

---

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| `.planning/REQUIREMENTS.md` line 41 | `- [ ] **XACT-03**` checkbox not updated after bench completion (committed at `37519af`); traceability table row still shows "Pending" | Warning | Documentation-only discrepancy. The bench evidence in `uno328pb/` fully satisfies XACT-03 as defined. No impact on the actual evidence artifacts or phase goal achievement. Requires a one-line edit to flip checkbox and update traceability row. |

No `TBD`, `FIXME`, or `XXX` markers found in the bench evidence artifacts, SUMMARY.md, exoneration-verdict.txt, or sha256sums files.

---

### Human Verification Required

#### 1. Update REQUIREMENTS.md XACT-03 checkbox and traceability row

**Test:** Open `.planning/REQUIREMENTS.md`. Line 41 reads `- [ ] **XACT-03**: uno328pb re-test recorded...`. Change to `- [x]`. In the traceability table, change `| XACT-03 | Phase 53 | Pending |` to `| XACT-03 | Phase 53 | Complete |`.

**Expected:** Both locations reflect the completed XACT-03 bench work (53-05 close-out committed `8975fe3`, 14:05 UTC 2026-06-05; `exoneration-verdict.txt` has all required D-10 content including the verbatim §2.0 exoneration line; `timeout-retry-log.txt` has 5 attempts with D-08 discipline).

**Why human:** REQUIREMENTS.md is a planning artifact maintained by the operator/orchestrator at phase close-out. The evidence is already committed and satisfies the requirement text; the checkbox is a bookkeeping record. This is a deliberate documentation update, not a gap in the evidence.

---

### Gaps Summary

No blocking gaps. The phase goal is achieved:

- **XACT-01 (clean-board byte-identity):** N=5 read self-consistency + N=5 write→read-back==source on both Uno (512 B) and Leonardo (1024 B), operator-witnessed, Rev 2.0, post-55 hardened firmware. Self-consistency form is the achieved form per D-05 (no original baseline chip present). Corpus extended by 53-07 to the actually-shipped post-54/55 contract (ack-sourced 1024×64, even-block, pure identity). Evidence artifacts fully committed and internally consistent.

- **XACT-02 (fault-injection resync):** Detect + recover proven in both directions (host→fw and fw→host) for both fault forms (corrupt-crc8 and drop-delimiter). Per-frame NAK: complete corrupt frame 0.001 s (sub-second fast-fail); truncated frame 1.001 s (single bounded inter-byte deadline, firmware-optimized from ~2 s). No path exceeds 1 s. No silent corruption. Recovery byte-exact on the same open connection confirmed for both.

- **XACT-03 (uno328pb transport-exoneration):** Re-tested on hardened firmware only (D-09). Timeouts logged and retried per D-08; verdict 2 never collapsed to verdict 1. Before/after shape comparison: floating-bus mode (~99.4% 0xff) resolved; read instability (intermittent mid-read timeouts + run-to-run divergence) persists → shape-changed=PARTIAL. Structured D-10 exoneration verdict with verbatim §2.0 line committed. This is a PASS for XACT-03 (a still-unstable uno328pb on the hardened transport is the expected, correct result — it proves transport is not the fix).

The only pending item is the REQUIREMENTS.md XACT-03 checkbox (documentation bookkeeping), which requires a human one-line edit.

---

_Verified: 2026-06-05T16:00:00Z_
_Verifier: Claude (gsd-verifier)_
