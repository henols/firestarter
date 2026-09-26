# Plan 99-03 Summary — Operator Bench (AM27C020 0x08 graduation gate)

**Requirements:** BENCH-01, BENCH-02
**Wave:** 2 | **Autonomous:** false (operator-witnessed) | **Outcome:** DEFER (fix-effective-but-unreliable)

## What happened

The single empirical v1.18 gate ran on the seated AM27C020 (Leonardo + RURP Rev 2.0), firmware
reflashed to the Phase-98 fix commit `35706c2` and avrdude-verified. VPP idle 12.9–13.0 V. Operator
constraint (no UV eraser) forced a small-write methodology instead of the staged full-image write:
a 64-byte pure-1→0 ramp written into currently-all-`0xFF` scratch regions, read-back compared.

| Write | Address | Result | RC / bad-bytes |
|-------|---------|--------|----------------|
| #1 | `0x1da00` | **60/64 byte-exact** (first 4 stayed `0xFF`) | 1 / 4 |
| #2 | `0x16600` | **0/64** (all stayed `0xFF`) | 1 / 64 |

Read stability: `consistency-check --runs 3` → PASS, 1 distinct SHA.

## Verdict: DEFER (BENCH-01), non-faked

- **Fix is effective (RCA-critical):** the `0x08` write path now programs 1→0 bits (60/64 once) —
  Phase-97's absolute "0 bits programmed" is **refuted**.
- **Residual defect (new):** programming is **marginal/unreliable** (60/64 vs 0/64 at stable idle
  VPP) — not a deterministic offset bug. No byte-exact graduation → `0x08` does not reach PASS.
- **Program-window VPP at pin 1:** NOT MEASURED (held-rail DMM tooling-blocked; DTR-reset). Idle
  ADC only. Program-window droop under load is the leading (uninstrumented) hypothesis.
- **Carry-forward:** new FUT (successor to FUT-06) — "0x08 write functional but unreliable;
  characterize program-window VPP-under-load + write timing."

## Key artifacts (all under `.planning/v1.18/bench/AM27C020-graduation/`)
- `99-03-BENCH-LOG.md` — full operator-witnessed raw log (discipline row, commands, RCs, SHAs, verdict)
- `SHA256SUMS.txt` — header verdict updated (`DEFER`), all artifact SHAs (imgA/writeA/prewrite/readback/readback2)
- `readback.bin` (post-write#1), `readback2.bin` (post-write#2), `writeA.bin`, `prewrite.bin`

## SAFE-01
Both writes used `-b` only — no `--skip-erase`, no `--force`. Guard intact.

## Self-Check: PASSED
- BENCH-LOG has discipline row + write/read/consistency commands + RCs + readback SHAs + verdict ✓
- SHA256SUMS.txt readback lines appended, header verdict no longer `PENDING BENCH` ✓
- No `--force` / `--skip-erase` in any recorded command ✓
- Outcome recorded from real silicon; nothing fabricated; DMM honestly "not measured" ✓

## Downstream (99-04)
Transcribe this DEFER outcome into `EVIDENCE.json/.md` and the PROTOCOL-LEDGER `0x08` entry
(residual-defect/FUT status, NOT PASS — the v1.18-native graduation marker is intentionally NOT set,
so the D-09 PASS constraint is not triggered). Rename/repoint FUT-06 to the new "unreliable" FUT.
