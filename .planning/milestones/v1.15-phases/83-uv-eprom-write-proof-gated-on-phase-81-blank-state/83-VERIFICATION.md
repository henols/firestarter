---
phase: 83-uv-eprom-write-proof-gated-on-phase-81-blank-state
verified: 2026-06-24T15:05:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
deferred:
  - truth: "SC#4 — the 2516 is bench-proven on Leonardo + Rev 2.0 (read+blank-check then a VPE-rail write proof), closing FUT-03"
    addressed_in: "Phase 84"
    evidence: "ROADMAP Phase 83 Outcome block: 'Success criterion #4 (2516 bench-proven) is DEFERRED → Phase 84 per D-01.' Phase 84 goal/SC own the consolidated audit + FIX-01 RCA; CONTEXT D-01 + EVIDENCE.json phase83_grad03 + REQUIREMENTS.md GRAD-03/FUT-03 rows all record the handoff. 2516 never seated/selected/written in Phase 83."
  - truth: "GRAD-03 — 2516 VPE-rail write proof recorded"
    addressed_in: "Phase 84"
    evidence: "REQUIREMENTS.md GRAD-03 row: 'Phase 84 (reassigned from Phase 83 per CONTEXT D-01)'; D-08 Phase-84 PASS bar pre-recorded verbatim in EVIDENCE.md + EVIDENCE.json (phase83_grad03), contingent on Phase 84 FIX-01 stabilizing the 0x0B read path."
---

# Phase 83: UV-EPROM Write Proof (gated on Phase 81 blank-state) — Verification Report

**Phase Goal:** Validate the write path for the UV-EPROMs without an eraser — spend-vs-preserve decided per chip live at the bench from the Phase 81 blank-state — captured in EVIDENCE. (ROADMAP-as-written also names the 2516 VPE-rail proof; CONTEXT D-01 narrows Phase-83 scope to the 2 read-stable UV chips and reassigns GRAD-03/SC#4/FUT-03 to Phase 84 — a documented handoff recorded in ROADMAP, EVIDENCE, and REQUIREMENTS.)
**Verified:** 2026-06-24T15:05:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

This is a bench-hardware validation phase (operator-driven, live Leonardo + RURP Rev 2.0 on /dev/ttyACM0). It modifies ONLY `.planning/` docs + evidence files and out-of-repo `/tmp` payloads — no source/firmware changes (EVID-02 reuse-first). Verification therefore checks: (a) the recorded EVIDENCE rows/cells exist and are internally consistent, (b) the recorded SHAs are corroborated by the saved bench artifacts (not fabricated), (c) the requirement/roadmap tracker reflects the deviations and the GRAD-03 handoff honestly, and (d) no genuine obligation was silently dropped.

### Observable Truths

| # | Truth (ROADMAP Success Criterion) | Status | Evidence |
| --- | --- | --- | --- |
| 1 | **SC#1 / UV-01+UV-02** — No UV part written until its blank-state is recorded AND the operator made an explicit spend-vs-preserve decision at the bench (read+blank-check precede every write) | ✓ VERIFIED | Both EVIDENCE rows record a non-destructive blank-state re-confirm BEFORE any VPP: ST M27C512 BLANK read-back SHA `71189f7f…48da9063` == Phase 81 (`blank` RC=0); AM27C020 NOT-BLANK SHA `08b687a3…177ed496` == Phase 81 (`blank` RC=1). Saved pre-read artifact `AM_pre_read.bin` SHA = `08b687a3…` confirms the pre-write read. Operator SPEND authorization captured per chip (cells[19]/cells[20] `spend_decision`). Board lock recorded (leonardo/ACM0, Rev 2.0 operator-stated, r1=270000). |
| 2 | **SC#2 / UV-03** — Each spent UV part is write-proven without an eraser (full image if blank, else all-0x00/1→0 write), verified by read-back SHA / verify exit code | ✓ VERIFIED (with recorded ANOMALY for AM27C020 — a valid D-14 outcome) | ST M27C512: write 16B @0x0000 RC=0, `verify -a` RC=0, N=3 reads 1 distinct SHA `008948af…`, neg-control RC=1 → PASS. AM27C020: all-0x00 16B write deterministically FAILED (`bad bytes 15/16`, 0 bits programmed, read-back unchanged) across initial + 2 retries → operator-classified ANOMALY under D-14, phase NOT halted, flagged Phase 84 FIX-01. Per the phase contract, a recorded non-vacuous verdict (PASS/FAIL/ANOMALY/PRESERVED) satisfies UV-03; an ANOMALY is a valid recorded outcome, not a phase failure. |
| 3 | **SC#3 / UV-04** — ST M27C512 (0x07) and AM27C020 (0x08) each have a recorded read + decode validation plus a write proof if spent, captured in EVIDENCE.{md,json} | ✓ VERIFIED | EVIDENCE.md rows 1+2 and EVIDENCE.json cells[19]+cells[20] both carry complete rows with all locked + extension columns. DB decode confirmed vs silicon: ST = UV-EPROM/13V/65536/0x07/0x203D; AM27C020 = UV-EPROM/13V/262144/0x08/DIP32/0x197 (DB VPP recorded as 13V vs the plan's stated 12V — a recorded observation, no DB edit, not a gap). |
| 4 | **SC#5** — Over-voltage stays blocked throughout; under-voltage warn-and-proceed accepted as best-effort | ✓ VERIFIED | Both cells record `vpp_path: standard 0x07/0x08 VPP path, over-voltage stayed blocked`. No VPE rail / NMOS best-effort caveat applied (those belong to the deferred 2516). No over-voltage event recorded. |
| 5 | **GRAD-03 handoff / scope-narrowing recorded** — the 2516 reassignment to Phase 84 is documented (not dropped), with the D-08 PASS bar pre-recorded; REQUIREMENTS.md + ROADMAP.md reflect it | ✓ VERIFIED | EVIDENCE.md "GRAD-03 / 2516 → Phase 84" record + 2516 row marked DEFERRED; EVIDENCE.json `phase83_grad03` (valid JSON) records disposition, rationale, moves_to_phase84 [GRAD-03, SC#4, FUT-03], contingent_on FIX-01, and the verbatim D-08 PASS bar; REQUIREMENTS.md GRAD-03 + FUT-03 rows reassigned to Phase 84; ROADMAP Phase 83 Outcome block records the reassignment + SC#4 DEFERRED. No 2516 chip seated/selected/written anywhere in Phase 83. |

**Score:** 5/5 truths verified

### Deferred Items

Items not met in Phase 83 but explicitly addressed in Phase 84 (per CONTEXT D-01 — a documented reassignment within the milestone, not an unmet obligation).

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | SC#4 — 2516 bench-proven on the ~22.4V VPE rail, closing FUT-03 | Phase 84 | ROADMAP Outcome: "Success criterion #4 (2516 bench-proven) is DEFERRED → Phase 84 per D-01." Phase 84 SC#2 owns the conditional defect RCA / write re-verify. |
| 2 | GRAD-03 — 2516 VPE-rail write proof | Phase 84 | REQUIREMENTS.md GRAD-03 row = "Phase 84 (reassigned from Phase 83 per CONTEXT D-01)"; D-08 PASS bar pre-recorded in EVIDENCE.{md,json}. Contingent on Phase 84 FIX-01. |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `/tmp/firestarter_bench_p83/ST_M27C512_img.bin` | 65536B deterministic image, SHA `604d9570…` | ✓ VERIFIED | Exists, 65536 bytes, SHA matches recorded oracle exactly |
| `/tmp/firestarter_bench_p83/AM27C020_zeros.bin` | 262144B all-0x00, SHA `8a39d2ab…` | ✓ VERIFIED | Exists, 262144 bytes, SHA matches recorded oracle AND `sha256(b'\x00'*262144)` |
| `.planning/v1.15/bench/EVIDENCE.md` | Phase 83 section: scope, 2516 deferral, 2 result rows, oracles | ✓ VERIFIED | Full section present (lines 107-181); both result rows complete; SAFE-02 gate recorded (lines 30-38) |
| `.planning/v1.15/bench/EVIDENCE.json` | phase83 + phase83_grad03 + per-chip cells | ✓ VERIFIED | Valid JSON; cells[19] (ST PASS) + cells[20] (AM27C020 ANOMALY) complete; phase83 + phase83_grad03 present |
| `.planning/REQUIREMENTS.md` | GRAD-03/FUT-03 → Phase 84; UV-01..04 traced | ✓ VERIFIED | Traceability rows 95-102 populated with per-chip outcome notes; GRAD-03/FUT-03 reassigned |
| `.planning/ROADMAP.md` | Phase 83 Outcome block + handoff note | ✓ VERIFIED | Outcome block (lines 149-154): ST PASS / AM27C020 ANOMALY / GRAD-03·SC#4·FUT-03 → Phase 84; all 3 plan checkboxes ticked |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| ST M27C512 write proof | EVIDENCE.{md,json} | verdict + read-back SHA recorded as a row | ✓ WIRED | EVIDENCE.md row 1 + cells[19] verdict=PASS; readback_sha256 `008948af…` corroborated by saved ST_post_read_1/2/3.bin (all 3 == `008948af…`) |
| AM27C020 write proof | EVIDENCE.{md,json} | verdict recorded as a row | ✓ WIRED | EVIDENCE.md row 2 + cells[20] verdict=ANOMALY; read instability corroborated — AM_pre_read/AM_post1 = `08b687a3…`, AM_post2 = `90cd45f5…` (exactly the "2 distinct SHAs" / localized glitch recorded) |
| REQUIREMENTS.md GRAD-03 | ROADMAP.md Phase 84 | documented 2516 deferral | ✓ WIRED | GRAD-03 + FUT-03 rows point at Phase 84; ROADMAP Phase 83 Outcome + Phase 84 own the 2516 |

### Data-Flow Trace (Level 4)

The recorded SHAs were traced back to the saved bench-read artifacts to confirm the evidence is real (not narrative-only):

| Artifact | Recorded value | Source corroboration | Status |
| -------- | -------------- | -------------------- | ------ |
| ST partial-spend payload | SHA `f705354e…`, hex `4420823c…01e4` | `ST_partial16.bin` SHA + hex match exactly; equals first 16B of seed=1 image | ✓ FLOWING |
| ST N=3 read oracle | 1 distinct SHA `008948af…` | `ST_post_read_1/2/3.bin` all == `008948af…` (genuinely byte-identical) | ✓ FLOWING |
| AM27C020 read instability | 2 distinct SHAs (`08b687a3…` ×2, `90cd45f5…` ×1) | `AM_pre_read`,`AM_post1` = `08b687a3…`; `AM_post2` = `90cd45f5…` | ✓ FLOWING |
| AM27C020 0 bits programmed | read-back unchanged at 0x02 | post-read SHA == pre-read SHA == Phase 81 SHA → confirms write programmed nothing | ✓ FLOWING |
| AM27C020 all-0x00 payload | `zeros16.bin` all-0x00; `wrong16.bin` neg-control | both present and as described | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| ST image oracle reproducible/correct | `sha256sum ST_M27C512_img.bin` | `604d9570…` == recorded | ✓ PASS |
| AM27C020 all-0x00 oracle correct | `sha256sum AM27C020_zeros.bin` vs `sha256(0x00*262144)` | both `8a39d2ab…` | ✓ PASS |
| EVIDENCE.json valid + per-chip cells present | `json.load` + cell inspection | valid; cells[19]/[20] complete | ✓ PASS |
| No Phase-83 source/firmware change (EVID-02) | submodule git log/diff | latest commits are Phase 82/79/77; no Phase 83 source | ✓ PASS |

### Probe Execution

Not applicable — no project probes declared for this bench/docs phase (`scripts/*/tests/probe-*.sh` not referenced in PLANs/SUMMARYs). The SAFE-02 host-suite gate (663 tests + 0xA4 guard + CI-scoped ruff) was recorded green in Plan 83-01 and is unchanged from Phase 82 (no source touched this phase).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ---------- | ----------- | ------ | -------- |
| UV-01 | 83-02, 83-03 | Non-destructive-first; blank-state recorded before write | ✓ SATISFIED | Both chips blank-state re-confirmed (no VPP) before write; SHAs == Phase 81 |
| UV-02 | 83-02, 83-03 | Explicit operator spend-vs-preserve decision before VPP | ✓ SATISFIED | SPEND captured per chip at the bench before any VPP (cells `spend_decision`) |
| UV-03 | 83-02, 83-03 | Spent UV part write-proven, verified | ✓ SATISFIED | ST PASS (write/verify/N=3/neg-control); AM27C020 ANOMALY recorded under D-14 (valid non-vacuous verdict) |
| UV-04 | 83-02, 83-03 | ST + AM27C020 recorded read+decode + write proof | ✓ SATISFIED | DB decode confirmed vs silicon for both; EVIDENCE rows complete |
| GRAD-03 | 83-03 | 2516 VPE-rail write proof | ⏸ DEFERRED → Phase 84 | Documented handoff per D-01 (REQUIREMENTS + ROADMAP + EVIDENCE); D-08 PASS bar pre-recorded. Not a Phase-83 obligation. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| (none in Phase 83 deliverables) | — | — | — | The "Plans: TBD" hits in ROADMAP are future-phase placeholders (Phase 84/45-48), not Phase-83 debt markers. No unreferenced TBD/FIXME/XXX in Phase 83 files. |

### Minor Tracker Inconsistency (informational — not a gap)

REQUIREMENTS.md carries UV-01..04 as unchecked `[ ]` in the requirement-definition list (lines 31-34) while the authoritative Traceability table (lines 95-98) marks all four **Complete** with detailed per-chip notes. This is a cosmetic checkbox-vs-table drift in the meta planning doc, not a functional gap — the authoritative status is correctly populated and the underlying evidence fully supports Complete. Recommend ticking the four `[ ]` boxes for consistency, but this does not block the phase. (GRAD-03 correctly remains `[ ]` since it is deferred.)

### Human Verification Required

None. All claims are corroborated by artifacts already on disk: the recorded SHAs were independently re-hashed and matched the saved bench-read files byte-for-byte (ST 3× `008948af`, AM27C020 `08b687a3`/`90cd45f5`, payloads, oracles). The operator-gated bench session already occurred inline (this phase was executed with the operator driving live hardware); no further live-hardware re-test is needed to confirm the recorded outcome. The two operator-directed deviations (partial 16B spends) and the AM27C020 ANOMALY classification are explicitly authorized/recorded operator decisions, not items needing fresh verification.

### Gaps Summary

No blocking gaps. The phase goal — validate the UV-EPROM write path on the 2 read-stable chips with per-chip operator spend decisions, captured non-vacuously in EVIDENCE — is achieved:

- **ST M27C512: PASS** — genuine write-path proof (write/verify RC=0, N=3 byte-identical read corroborated by saved artifacts, wrong-file negative control RC=1). The operator-directed partial 16B spend (deviation from full-image D-05) is a legitimate, recorded scope reduction that still exercises the write/VPP path + trusted-read oracle; it preserves the part. Not a gap.
- **AM27C020: ANOMALY (valid outcome)** — the all-0x00 write deterministically programmed 0 bits across initial + 2 retries (chip silicon intact, read-back unchanged), with a mild localized read glitch. Operator-classified ANOMALY under D-14 (0x08 write/VPP path on this bench, not chip wear), phase not halted, flagged Phase 84 FIX-01. Per the phase contract (D-14), a recorded non-vacuous verdict — including ANOMALY — is a valid Phase-83 outcome, not a phase failure. The evidence is honest and complete.
- **GRAD-03 / SC#4 / FUT-03 → Phase 84** — a documented, traceable reassignment (CONTEXT D-01), recorded in ROADMAP + REQUIREMENTS + EVIDENCE with the D-08 PASS bar pre-recorded. The irreplaceable 2516 was never written/dumped/re-read in Phase 83. Not a dropped requirement — correctly deferred (filed under `deferred`).

Only a cosmetic checkbox/table drift in REQUIREMENTS.md (UV-01..04) was noted; it does not affect status.

---

_Verified: 2026-06-24T15:05:00Z_
_Verifier: Claude (gsd-verifier)_
