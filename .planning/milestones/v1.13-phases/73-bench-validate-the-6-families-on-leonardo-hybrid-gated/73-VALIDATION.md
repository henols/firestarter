---
phase: 73
slug: bench-validate-the-6-families-on-leonardo-hybrid-gated
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-17
audited: 2026-06-18
---

# Phase 73 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (host, Tier-2) + PlatformIO/Unity native (firmware, Tier-1); bench HIL via `firestarter dev validate-family` (Tier-3) |
| **Config file** | `firestarter_app/pyproject.toml` (`[test]` extra) + `firestarter/platformio.ini` |
| **Quick run command** | `cd firestarter_app && pytest -q` |
| **Full suite command** | `cd firestarter_app && pytest && cd ../firestarter && pio test -e native` |
| **Estimated runtime** | ~120 seconds (software tiers); Tier-3 HIL is operator-paced |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && pytest -q`
- **After every plan wave:** Run full suite (host pytest + native Unity)
- **Before `/gsd-verify-work`:** Full software suite must be green; Tier-3 cells recorded in `validation-matrix.{json,md}`
- **Max feedback latency:** ~120 seconds (software); Tier-3 HIL recorded per-cell

---

## Per-Task Verification Map

> Populated by the planner per task. Tier-1/Tier-2 cells are automated; Tier-3 HIL cells are bench-recorded (matrix-cell evidence, not a watch-mode test).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 73-01-01 | 01 | 1 | VAL-01..06 (Tier-1) | T-73-03 | No false GREEN on a RED native cell | unit (native Unity) | `cd firestarter/ && pio test -e native -f "native/avr/test_val_*"` | ✅ (28 tests) | ✅ green |
| 73-01-01 | 01 | 1 | VAL-01..06 (Tier-2) | T-73-03 | Host wire round-trip matches per family | unit (host pytest) | `cd firestarter_app/ && pytest tests/test_val_wire_*.py` | ✅ (26 tests) | ✅ green |
| 73-01-02 | 01 | 1 | SC#3 enabling (R1 precondition + Leonardo identity) | T-73-01, T-73-02 | Live R1≈270000 in-band; controller=leonardo confirmed; gate fires (never silently skipped) | bench-cell (precondition gate) | manual pre-write gate (`fw`/`hw`/`config`) | ✅ recorded | ✅ green (gate armed) |
| 73-01-03 | 01 | 1 | VAL-02, VAL-05 (Tier-3) | T-73-04 | SKIP recorded explicitly, never as silent omission | bench-cell | `dev validate-family {eeprom28c,flash_intel}` (auto-SKIP path) | ✅ JSON cells | ✅ green (SKIP-deferred, reason recorded) |
| 73-02-01 | 02 | 2 | VAL-01 (Tier-3 eprom) | T-73-05, T-73-06, T-73-07 | Authoritative PASS w/ evidence_sha; negative control (wrong-file verify) exits non-zero — oracle non-vacuous | bench-cell | `dev validate-family eprom --board leonardo --chip W27C512` | ✅ JSON + bins | ✅ green (PASS, authoritative) |
| 73-03-01 | 03 | 2 | VAL-03 (Tier-3 flash3) | T-73-04, T-73-06 | Definitive recorded verdict; negative control non-vacuous | bench-cell | `dev validate-family flash3 --board leonardo --chip SST39SF040` (bonus) | ✅ JSON + bins | ✅ green (PASS, authoritative — SST39SF040 bonus; AM29F040 SKIP-deferred) |
| 73-03-01 | 03 | 2 | VAL-04 (Tier-3 flash4) | T-73-06, D-12 | FAIL is a valid recorded verdict; negative control non-vacuous; routes to Phase 74 | bench-cell | `dev validate-family flash4 --board leonardo --chip W29C040` | ✅ JSON + bins | ✅ green-as-recorded (FAIL, authoritative → Phase 74) |
| 73-04-01 | 04 | 2 | VAL-06 (Tier-3 sram, D-09 hard gate) | T-73-06, D-08, D-09 | Definitive two-pattern N≥2 verdict (table-stakes-PASS or FIX-01), never inconclusive; negative control non-vacuous | bench-cell | `firestarter write FM1608 pattern_{a,b}.bin -b` → readback compare (two-pattern N=2) | ✅ JSON + 7 bins + verdict.txt | ✅ green (PASS, authoritative, retry_count=2; table-stakes-PASS) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

> **Tier semantics:** Tier-1/Tier-2 cells are automated (existing Phase 71 harness — see Wave 0) and ran GREEN at execution time (28 + 26 = 54 tests). Tier-3 cells are operator-paced HIL evidence recorded as committed matrix-cell verdicts (`val-results/<family>/validation-matrix.json` + binary artifacts), not watch-mode tests — see Manual-Only. Every Tier-3 cell carries a definitive recorded verdict (PASS / FAIL / SKIP-deferred-with-reason); none are inconclusive.

---

## Wave 0 Requirements

*Existing infrastructure (Phase 71 harness: `dev validate-family` runner, matrix artifact, non-vacuous PASS oracle, SKIP-deferred mechanism) covers all phase requirements. Phase 73 adds zero production code — no Wave 0 test scaffolding required.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tier-3 HIL on Leonardo (W27C512, AM29F040, FM1608) | VAL-01/03/06 | Requires physical chip + Rev 2.0 shield on hand; Claude drives over USB passthrough, operator inserts chip / swaps shield | Per-family `dev validate-family` run with independent post-write full read + SHA compare + passing negative control; live R1/R2 readback (`r1 ≈ 270000`) recorded |
| FM1608 two-pattern A→B write+read-back (VAL-06 hard gate) | VAL-06 | Bench-only persistence proof; per-byte verdict separates whole-write no-op (FIX-01) from parked byte-0 FRAM bug | Write pattern A → read-back; write pattern B → read-back; baseline initial read + N≥2 confirm; per-byte D-08 classification |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify, a recorded bench-cell verdict, or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (excluding operator-paced Tier-3 HIL cells)
- [x] Wave 0 covers all MISSING references (none — Phase 71 infrastructure reused)
- [x] No watch-mode flags
- [x] Feedback latency < 120s (software tiers)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-06-18 (retroactive audit — no automated gaps; see audit trail)

---

## Validation Audit 2026-06-18

| Metric | Count |
|--------|-------|
| Requirements audited | 6 (VAL-01..VAL-06) |
| Automated half COVERED (Tier-1 + Tier-2, green) | 6 / 6 |
| Tier-3 HIL cells with recorded verdict | 6 / 6 (3 PASS, 1 FAIL→Phase 74, 2 SKIP-deferred) |
| Gaps found (MISSING automated tests) | 0 |
| Resolved (auditor-generated) | 0 |
| Escalated (impl bugs) | 0 |

**Disposition:** Phase 73 added zero production code; it re-uses the Phase 71 validation harness
(`dev validate-family` runner, matrix artifact, non-vacuous PASS oracle, SKIP-deferred mechanism).
The automated software half (28 Tier-1 native + 26 Tier-2 host wire = 54 tests) exists on disk for all
six families and ran GREEN at execution time. The Tier-3 HIL half is inherently hardware-bound
(physical chip + Rev 2.0 shield), correctly classified as Manual-Only, and every cell carries a
definitive recorded verdict in committed `val-results/<family>/` artifacts (cross-checked against
73-VERIFICATION.md, which passed 4/4). No automated coverage gap exists, so no test generation was
required and the gsd-nyquist-auditor was not spawned. `nyquist_compliant: true`.
