---
phase: 99-bench-ledger-graduation-gate-evidence-ledger-update
verified: 2026-07-01T11:58:22Z
status: passed
score: 4/4 must-haves verified (the 1 documentation gap below was closed post-verification, commit pending)
overrides_applied: 0
gap_closed: "EVIDENCE.json/.md FUT-07 -> FUT-08 stale-reference gap fixed 2026-07-01 after the verifier flagged it; check_graduation.py + check_ledger.py re-run exit 0 after the edit. FUT-07 now appears in EVIDENCE only as an explicit disambiguation ('FUT-07 is the unrelated v1.17 W29C040 defect')."
resolved_gaps:
  - truth: "EVIDENCE record (EVIDENCE.json/EVIDENCE.md) cites the correct successor FUT id"
    status: resolved
    reason: "EVIDENCE.json cells[].verdict (phase99_deferral) and EVIDENCE.md Cell C verdict row updated FUT-07 -> FUT-08; gates re-verified green."
---

# Phase 99: BENCH + LEDGER — Graduation Gate, Evidence & Ledger Update — Verification Report

**Phase Goal:** The fixed `0x08` write path is bench-tested on the seated AM27C020 (Leonardo + Rev 2.0) — byte-exact write→verify (SHA match) if writable, OR a cleanly documented deferral if not; a per-chip EVIDENCE record is captured sufficient to update the PROTOCOL-LEDGER `0x08` entry; the PROTOCOL-LEDGER is updated and `check_ledger.py` passes with 0 contradictions.

**Verified:** 2026-07-01T11:58:22Z
**Status:** gaps_found (1 cosmetic cross-reference gap; does not block any gate or falsify the deferral)
**Re-verification:** No — initial verification

## Critical Framing Applied

This phase's ROADMAP success criteria are deliberately two-branched: BENCH-01 is satisfied by EITHER
a byte-exact write→verify graduation OR a cleanly documented, non-fabricated deferral to a FUT
carry-forward. The actual outcome this session is **DEFER (fix-effective-but-unreliable)**. This
verification does NOT penalize the phase for failing to reach byte-exact graduation — it instead
independently audits whether the deferral is honest, complete, and correctly gated.

**Verdict on the framing question: the deferral is genuine and non-fabricated.** Independent
byte-level inspection of the raw bench artifacts (below) confirms the claimed program signature
exactly, without relying on SUMMARY.md narrative.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | BENCH-01: a real silicon write→verify was attempted on the seated AM27C020 (Leonardo+Rev 2.0), operator-witnessed with controller identity + R1/R2 readback + firmware commit; outcome is byte-exact graduation OR a cleanly documented, non-faked deferral | ✓ VERIFIED | `99-03-BENCH-LOG.md` records controller=leonardo, port=/dev/ttyACM0, R1=270000/R2=44000, fw commit `35706c2` (reflashed + avrdude-verified, 25722 bytes). Independent byte-level check of `readback.bin`@0x1da00 = `ffffffff` + ramp `04..3f` (60/64 exact) and `readback2.bin`@0x16600 = all `ff` (0/64) — matches the claimed signature exactly. No `--force`/`--skip-erase` in any recorded command. Deferral is honest and grounded in real silicon, not narrated. |
| 2 | BENCH-02: an EVIDENCE record captures the program signature (bits programmed / failing-vs-fixed), VPP reading (or honest "not measured"), and the bench-discipline row sufficient to update the ledger | ✓ VERIFIED (minor stale cross-ref) | `EVIDENCE.json` `phase99_deferral` cell + `EVIDENCE.md` "Cell C" both carry the full bench-discipline row (controller/port/R1/R2/fw_commit), program signature (write#1 60/64, write#2 0/64), VPP idle (12900-13000mV) + honest "not measured" for program-window pin-1 DMM, and pre/post/write-image SHAs. `check_graduation.py` exits 0 confirming completeness + anti-fabrication self-consistency. One stale field: the record's own `verdict` text says "FUT-07" (pre-collision-fix id) instead of the corrected "FUT-08" — a copy/paste lag from the same session's id-collision fix that only touched PROTOCOL-LEDGER files. Does not affect gate exit code or evidence substance. |
| 3 | SC#3: PROTOCOL-LEDGER `0x08` entry updated (open-defect-carried → residual FUT, citing Phase-99 evidence); `check_ledger.py` passes 0 contradictions; FUT-06 retired/renamed per actual outcome | ✓ VERIFIED | `PROTOCOL-LEDGER.json`/`.md` `0x08` row: `on_hand_chip: AM27C020`, `defect_ref: FUT-08`, `verification_status: open-defect-carried`. `open_defects[]` contains `FUT-08` (supersedes FUT-06) with disposition citing Phase-99 bench evidence; `FUT-06` and any stray `FUT-07`/AM27C020 entry are absent from the ledger. `check_ledger.py` → exit 0, "12 rows, 3 open_defects, all LEDGER-01/02/03 + D-09 assertions satisfied." `pytest test_check_ledger.py -q` → 8 passed. |
| 4 | Ledger honesty guard (D-04): no raw SHA-256 hash leaks into the PROTOCOL-LEDGER files | ✓ VERIFIED | `grep -oE '\b[0-9a-f]{64}\b'` against both `PROTOCOL-LEDGER.json` and `PROTOCOL-LEDGER.md` returns 0 matches. All raw SHAs are confined to `EVIDENCE.json` and `SHA256SUMS.txt`, referenced from the ledger only by path. |

**Score:** 4/4 truths substantively verified; 1 truth (#2) carries a documented minor gap (stale FUT id text) that does not change its VERIFIED status but is reported for completeness per the adversarial-verification mandate.

### Independent Byte-Level Spot-Check (beyond narrative trust)

Rather than trusting `99-03-BENCH-LOG.md`'s prose, the raw binary artifacts were inspected directly:

| Check | Command | Result | Matches Claim? |
|---|---|---|---|
| Pre-write state at both target addresses is blank (0xFF) | `prewrite.bin[0x1da00:+64]`, `prewrite.bin[0x16600:+64]` | all `ff` | Yes |
| Write#1 readback | `readback.bin[0x1da00:+64]` | `ffffffff` + ramp `04..3f` (60/64 bytes match ramp, first 4 stayed FF) | Yes — exact byte-for-byte match to claimed 60/64 |
| Write#2 readback | `readback2.bin[0x16600:+64]` | all `ff` (0/64 programmed) | Yes — exact match to claimed 0/64 |
| Written payload | `writeA.bin` | 64-byte ramp `00..3f` | Yes |
| All 5 SHA256SUMS.txt entries self-verify | `sha256sum -c SHA256SUMS.txt` | 5/5 OK | Yes |

This independently falsifies the hypothesis that the bench outcome was fabricated or narrated without real hardware backing — the claimed partial-program signature is reproducible byte-for-byte from the raw artifact files.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/v1.16/ledger/tools/check_ledger.py` | D-09 extended for v1.18-native graduation | ✓ VERIFIED | Extension present (`v1_18_writeverify_sha_selfconsistent` branch); exit 0 on live ledger |
| `.planning/v1.16/ledger/tools/test_check_ledger.py` | 3 new tests (positive/negative/retirement) | ✓ VERIFIED | 8 tests total, all pass (`pytest -q` → 8 passed) |
| `.planning/v1.18/bench/AM27C020-graduation/imgA.bin` | deterministic 262144-byte write image | ✓ VERIFIED | exists, 262144 bytes, SHA matches SHA256SUMS.txt |
| `.planning/v1.18/bench/AM27C020-graduation/SHA256SUMS.txt` | annotated provenance header + all bench SHAs | ✓ VERIFIED | 5/5 self-verify via `sha256sum -c` |
| `.planning/v1.18/bench/check_graduation.py` | EVIDENCE-completeness anti-fabrication gate | ✓ VERIFIED | exit 0: "PASS: phase99 AM27C020 deferral cell complete" |
| `.planning/phases/.../99-03-BENCH-LOG.md` | operator-witnessed raw bench log | ✓ VERIFIED | present, detailed, matches raw artifact bytes independently |
| `.planning/v1.18/bench/EVIDENCE.json` / `.md` | Phase-99 deferral cell (json+md lockstep) | ⚠️ VERIFIED WITH STALE FIELD | cell present, complete, substantively correct; `verdict` text cites stale "FUT-07" instead of "FUT-08" |
| `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` / `.md` | 0x08 row + FUT-08 (json+md lockstep) | ✓ VERIFIED | fully correct and consistent; FUT-06/stray-FUT-07 absent, FUT-08 present in both files |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| Raw bench artifacts (`readback.bin`, `readback2.bin`, `prewrite.bin`) | `99-03-BENCH-LOG.md` narrative | byte-for-byte content match | WIRED | Independently confirmed — see spot-check table above |
| `EVIDENCE.json` `phase99_deferral` cell | `check_graduation.py` gate | `op` prefix filter (`phase99*`) | WIRED | Gate correctly locates the cell and exits 0 |
| `PROTOCOL-LEDGER.json` `0x08` row | `open_defects[]` `FUT-08` entry | `defect_ref` field | WIRED | Cross-reference consistent, both say FUT-08 |
| `99-03-BENCH-LOG.md` bench outcome | `EVIDENCE.json`/`PROTOCOL-LEDGER` transcription | manual transcription (99-04) | WIRED (with 1 stale field) | All numeric/SHA values transcribed correctly verbatim; only the FUT successor id text in EVIDENCE files lags the id-collision correction applied to the ledger |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| BENCH-01 | 99-03, 99-04 | Full write→verify cycle byte-exact OR clean deferral | ✓ SATISFIED | Deferral genuinely non-fabricated, independently verified at byte level |
| BENCH-02 | 99-01, 99-02, 99-03, 99-04 | EVIDENCE record sufficient to update ledger | ✓ SATISFIED (minor stale cross-ref, does not block) | Record complete and substantively correct; ledger update was in fact possible and was performed correctly |

No orphaned requirements found — REQUIREMENTS.md rows 73-74 (BENCH-01/02 → Phase 99) match the `requirements:` frontmatter declared across all four 99-0X-PLAN.md files.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.planning/v1.18/bench/EVIDENCE.json` | 84 | Stale defect-id reference ("FUT-07" not updated to "FUT-08") | ℹ️ Info | Does not affect any automated gate; text-only cross-reference lag in the EVIDENCE record vs. the (correct) PROTOCOL-LEDGER |
| `.planning/v1.18/bench/EVIDENCE.md` | 115 | Same stale reference, mirrored in the human-readable table | ℹ️ Info | Same as above |

No TBD/FIXME/XXX debt markers found in any phase-modified file. No placeholder/stub patterns found. `check_graduation.py`'s own `"TBD" in str(value...)` code is the anti-fabrication gate logic itself, not a debt marker.

### Verification Commands Run (all as specified)

| Command | Result | Status |
|---|---|---|
| `python3 .planning/v1.18/bench/check_graduation.py` | "PASS: phase99 AM27C020 deferral cell complete" | exit 0 ✓ |
| `python3 .planning/v1.18/bench/check_signature.py` | "RCA-01 signature complete; bits_flipped=0" | exit 0 ✓ |
| `python3 .planning/v1.18/bench/check_pre01.py` | "PRE-01 pre-flight captures present" | exit 0 ✓ |
| `python3 .planning/v1.16/ledger/tools/check_ledger.py` | "12 rows, 3 open_defects, ... satisfied" | exit 0 ✓ |
| `pytest test_check_ledger.py -q` | 8 passed | exit 0 ✓ |
| `grep -oE '[0-9a-f]{64}' PROTOCOL-LEDGER.{json,md}` | 0 matches | D-04 clean ✓ |

All six specified verification commands pass exactly as claimed in the SUMMARY files — independently re-run, not trusted from narrative.

### Human Verification Required

None. All checks in this phase are file-based, gate-script-based, or independently byte-verifiable against committed binary artifacts. The bench session itself was already operator-witnessed (Henrik, 2026-07-01) per `99-03-BENCH-LOG.md`; no further human action is needed to close this phase.

### Gaps Summary

**One minor, non-blocking documentation gap:** the FUT-06→FUT-08 id-collision fix (triggered when the
operator-requested "FUT-07" was found to collide with the pre-existing v1.17 W29C040 FUT-07 defect)
was applied correctly and completely to `PROTOCOL-LEDGER.json`/`.md` — the actual gate target for SC#3
— via commit `7d42894`. However, that same fix commit's diff shows it touched ONLY the two
PROTOCOL-LEDGER files; `EVIDENCE.json` (the `phase99_deferral` cell's `verdict` field) and
`EVIDENCE.md` (the mirrored "Cell C" table) still read "FUT-07" in their carry-forward text, a
cross-reference that is now technically wrong (that id belongs to a different, unrelated defect).

This does not affect:
- `check_graduation.py`'s pass/fail logic (it does not parse or validate the FUT id string)
- `check_ledger.py`'s 0-contradiction pass (it only reads the PROTOCOL-LEDGER files, which are correct)
- The substantive honesty of the deferral (byte-level evidence independently confirms the bench claims)

It is a real, findable inconsistency that a future reader following the EVIDENCE record's citation
would land on the wrong (already-claimed) FUT id. Recommended fix: a 2-line edit to
`EVIDENCE.json`/`EVIDENCE.md` swapping "FUT-07" → "FUT-08" in the verdict text, mirroring the fix
already applied to the ledger.

**This looks intentional-adjacent but is actually an incomplete propagation, not a deliberate
deviation** — no override is suggested; it should simply be corrected. Given its severity (cosmetic
cross-reference, zero gate impact, zero risk to the ledger's correctness or the deferral's honesty),
it does not block phase closure or milestone progression, but is reported per the adversarial
verification mandate rather than silently passed over.

---

_Verified: 2026-07-01T11:58:22Z_
_Verifier: Claude (gsd-verifier)_
