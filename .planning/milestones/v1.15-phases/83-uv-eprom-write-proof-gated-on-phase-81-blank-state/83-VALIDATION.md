---
phase: 83
slug: uv-eprom-write-proof-gated-on-phase-81-blank-state
status: validated
nyquist_compliant: partial
wave_0_complete: true
created: 2026-06-24
---

# Phase 83 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> **Reconstructed retroactively (State B)** from PLAN/SUMMARY/VERIFICATION artifacts.
> Phase 83 is a **bench-hardware validation + documentation** phase with **zero source/firmware
> code changes** (EVID-02 reuse-first). No new test files were generated because no new software
> behavior was added — all automatable behavior is covered by the existing committed host suite
> plus inline preflight/doc verifies; the UV write proofs are inherently manual hardware.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (firestarter_app) |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter_app && python -m pytest -q -k test_init_phase_data_frames_not_acked` |
| **Full suite command** | `cd firestarter_app && python -m pytest -q && ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` |
| **Estimated runtime** | ~30 seconds (663 tests) |

---

## Sampling Rate

- **After every task commit:** Run quick command (0xA4 `ack_data=False` SAFE-02 guard)
- **After every plan wave:** Run full suite (663 tests + CI-scoped ruff)
- **Before any bench session opens (SAFE-02):** Full suite must be green (STOP-on-red)
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 83-01-01 | 01 | 1 | UV-01 (SAFE-02 gate) | T-83-02 | Bench session blocked on a red host suite | unit (existing) | `python -m pytest -q -k test_init_phase_data_frames_not_acked && ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` | ✅ `tests/test_eprom_operations.py` | ✅ green |
| 83-01-02 | 01 | 1 | UV-03 (write payloads) | T-83-01 | Exact-size/exact-content image fixed before any irreversible write | preflight assert | `test "$(stat -c%s …/ST_M27C512_img.bin)" = 65536 && test "$(stat -c%s …/AM27C020_zeros.bin)" = 262144 && grep -q "Phase 83" .planning/v1.15/bench/EVIDENCE.md` | ✅ `/tmp/firestarter_bench_p83/*.bin` (out-of-repo) | ✅ green |
| 83-02-01 | 02 | 2 | UV-01, UV-02 | T-83-04..07 | No VPP until blank-state recorded + operator spend authorized | manual hardware | — (operator-gated, irreversible UV silicon) | n/a | ✅ manual (PASS) |
| 83-02-02 | 02 | 2 | UV-03, UV-04 (ST M27C512) | T-83-04..07 | Write proven by trusted Leonardo read-back (N≥3) + neg-control RC=1 | manual hardware | — (live bench: `write -a` / `verify -a` / N=3 read / wrong-file verify) | n/a | ✅ manual (PASS) |
| 83-03-01 | 03 | 3 | UV-01, UV-02 | T-83-08..11 | No VPP until NOT-BLANK recorded + operator spend authorized | manual hardware | — (operator-gated, irreversible UV silicon) | n/a | ✅ manual |
| 83-03-02 | 03 | 3 | UV-03, UV-04 (AM27C020) | T-83-08..11 | Write attempt on trusted read; non-vacuous verdict recorded | manual hardware | — (live bench: write / N=3 read / wrong-file verify) | n/a | ⚠️ manual (ANOMALY — valid D-14 outcome → Phase 84 FIX-01) |
| 83-03-03 | 03 | 3 | GRAD-03 (handoff doc) | — | 2516 reassignment documented, not silently dropped | doc assert | `grep -q "GRAD-03" .planning/v1.15/bench/EVIDENCE.md && grep -q "Phase 84" .planning/v1.15/bench/EVIDENCE.md && grep -v '^#' .planning/REQUIREMENTS.md | grep -q "GRAD-03" && python3 -c "import json;json.load(open('.planning/v1.15/bench/EVIDENCE.json'))"` | ✅ EVIDENCE/REQUIREMENTS/ROADMAP | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky/anomaly · manual = operator hardware*

---

## Wave 0 Requirements

Existing infrastructure covers all automatable phase requirements. No Wave 0 framework install or
test stubs were required — Phase 83 added no code, and the SAFE-02 guard (`test_init_phase_data_frames_not_acked`)
already exists from Phase 81/82. The only new artifacts were out-of-repo `/tmp` write payloads
(verified by inline size/content asserts) and `.planning/` evidence/tracker updates (verified by
inline grep/JSON-validity asserts).

---

## Manual-Only Verifications

The UV write proofs operate on **irreversible UV-EPROM silicon** with **operator-gated VPP** on a
specific board (Leonardo + RURP Rev 2.0). They cannot be automated as unit tests — the verify
oracle is a live trusted-board read, and every write permanently consumes the part. These are
recorded in `.planning/v1.15/bench/EVIDENCE.{md,json}` with SHAs corroborated against saved
bench-read artifacts (see 83-VERIFICATION.md Data-Flow Trace).

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Non-destructive-first blank-state re-confirm before any VPP | UV-01 | Requires live read on Leonardo + Rev 2.0; recorded SHA == Phase 81 | `firestarter read <chip>` + `firestarter blank <chip>` (no VPP); confirm SHA == Phase 81 recorded blank-state before any write |
| Operator spend-vs-preserve authorization before VPP | UV-02 | Irreversible bench decision; operator authority is the gate | Present spend-vs-preserve at bench; capture verbatim; apply VPP only after explicit SPEND |
| ST M27C512 (0x07) spent write proof | UV-03 | Live write + trusted read-back oracle; consumes part | `write M27C512 <img> -a`; `verify -a` RC=0; N=3 read 1-distinct-SHA; wrong-file `verify -a` RC=1 (recorded PASS) |
| AM27C020 (0x08) spent write proof | UV-03 | Live write on irreversible silicon | `write AM27C020 <img> -b -a`; N=3 read; wrong-file `verify -a` RC=1 (recorded ANOMALY — 0 bits programmed → Phase 84 FIX-01) |
| ST + AM27C020 DB-decode vs silicon | UV-04 | Confirms decoded DB fields against physical chip | `firestarter info <chip>` — confirm UV-EPROM / VPP / size / algorithm vs silicon |
| Board lock (controller/shield/r1) | SAFE-01 / D-09 | EEPROM byte cannot distinguish silkscreen rev; operator statement authoritative | `firestarter fw` (controller: leonardo), ASK silkscreen Rev 2.0, `firestarter config` (r1≈270000) |

*GRAD-03 (2516 VPE-rail write proof) is **deferred to Phase 84** per CONTEXT D-01 — not a Phase-83
manual item; the D-08 PASS bar is pre-recorded in EVIDENCE for Phase 84 to inherit.*

---

## Validation Sign-Off

- [x] All tasks have an automated verify, an existing-test mapping, or a documented manual-only reason
- [x] Sampling continuity: SAFE-02 host suite green before every bench session (no 3 consecutive tasks without automated verify — manual bench tasks are bracketed by automated preflight 83-01 + automated doc gate 83-03-03)
- [x] Wave 0 covers all MISSING references (none — no code added; existing suite covers the only automatable behavior)
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: partial` set in frontmatter (automatable behavior fully covered; UV write proofs are inherently manual hardware)

**Approval:** approved 2026-06-24

---

## Validation Audit 2026-06-24

| Metric | Count |
|--------|-------|
| Gaps found | 0 (no automatable gaps — phase added no code) |
| Resolved | 0 |
| Escalated | 0 |
| Manual-only (hardware) | 4 behaviors (UV-01/02/03/04 bench portions) |
| Deferred | 1 (GRAD-03 → Phase 84) |

**Auditor:** not spawned — no automatable gaps to fill (zero source/firmware change; spawning a
test-generator would have nothing legitimate to generate). All automatable behavior was already
covered by the existing committed host suite (`test_init_phase_data_frames_not_acked` + full
suite + CI-scoped ruff) and the inline preflight/doc verifies in Plans 83-01 and 83-03.

---

## Validation Audit 2026-06-24 (re-audit, State A)

Re-ran the validate-phase audit against the live artifacts and git history. Findings reconfirmed:

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

**Evidence checked this pass:**
- `firestarter_app` git log shows **no Phase 83 commits** (HEAD = `646afae`, Phase 82); firmware
  sub-repo on `beta` with no Phase 83 delta → confirms zero source/firmware code was added.
- SAFE-02 guard `test_init_phase_data_frames_not_acked` confirmed present at
  `firestarter_app/tests/test_eprom_operations.py:135` (the COVERED mapping is real, not phantom).
- All three plan SUMMARYs carry `tech-stack.added: []`; only `.planning/` evidence + `/tmp/`
  bench payloads changed.

**Verdict:** no automatable gaps; Per-Task Map statuses, Manual-Only list, and frontmatter
unchanged. Phase remains `nyquist_compliant: partial` (automatable behavior fully covered; UV
write proofs inherently manual hardware — irreversible silicon, operator-gated VPP). Auditor not
spawned (nothing to generate).
