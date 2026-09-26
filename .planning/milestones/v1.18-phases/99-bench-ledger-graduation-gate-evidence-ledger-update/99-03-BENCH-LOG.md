# Phase 99-03 — AM27C020 0x08 Graduation Bench Log

> Operator-witnessed raw bench log for the single empirical v1.18 gate: the Phase-98 `0x08`
> write-path fix tested on the seated AM27C020 (Leonardo + RURP Rev 2.0). Nothing here is
> fabricated. A tooling-blocked reading is recorded as "not measured" with reason.

**Session start:** 2026-07-01T11:17Z
**Operator:** Henrik (henrik@predictly.se)
**Driver:** Claude Code (orchestrator, inline "walk-it-now" mode; operator authorizes each spend)

---

## Gate 1 — Pre-spend bench-discipline + firmware-build + VPP (COMPLETE)

| Field | Value | Source |
|-------|-------|--------|
| Controller identity | `leonardo` | `firestarter fw` |
| Port | `/dev/ttyACM0` | `firestarter fw` |
| Hardware revision (reported) | Rev 2.0-class (Override HW: Rev 2.0-class) | `firestarter hw` |
| Shield silkscreen | **Rev 2.0 — operator eyes-on confirmed** | operator |
| Seated chip | **AM27C020 — operator confirmed** | operator |
| R1 readback | `270000` | `firestarter config` |
| R2 readback | `44000` | `firestarter config` |
| Firmware version string | `3.0.0b10` (does NOT distinguish the fix — version-string caveat) | `firestarter fw` |
| Firmware commit under test | **`35706c2`** (Phase 98-05 HEAD, corrected `DIP32_27C020` rw-pin:[31] → `CTRL_READ_WRITE 0x40`) | reflashed this session |
| Reflash proof | `pio run -t upload -e leonardo` → avrdude wrote+verified **25722 bytes** [SUCCESS] | build log |
| VPP target | 12.75 V ±0.25 (band ~12.75–13.0 V; DB `vpp_mv=13000`) | plan |
| VPP confirmation read | **12.9–13.0 V** (stable over ~12 s), Internal VCC 5.5 V | `timeout -s INT 12 firestarter vpp` (single sample, operator-set pot, no monitor loop) |
| `--force` used? | **No** (none of the recorded commands used `--force`) | source assertion |

**Firmware certainty note (threat T-99-03c):** the pre-flash board reported version `3.0.0b10`,
which cannot distinguish the Phase-98 fix build from an older `3.0.0b10`. To eliminate the
stale-build risk, the operator authorized a reflash from the firestarter submodule HEAD
(`35706c2`, the Phase 98-05 fix commit — verified as the actual working-tree HEAD before flash).
Leonardo is chip-out-sideload EXEMPT, so the reflash was done with the AM27C020 seated. The
commit `35706c2` (not the version string) is the build-under-test of record.

**Gate 1 verdict:** PASS — right board (Rev 2.0, silkscreen), right chip (AM27C020), right build
(`35706c2`), VPP in band (12.9–13.0 V), no `--force`. Cleared for the operator-authorized spend.

**imgA write-image SHA-256 (from 99-02 `SHA256SUMS.txt`, the compare oracle):**
`b2fc5cbfcc25be3daa0e8e88e6977c7da6164a6fcf9c577ca943da940a133457`

---

## Gate 2 — Live write → read-back → SHA compare → N≥3 stability (COMPLETE)

**Operator authorization:** "go" + constraint "no eraser, only do small writes" (2026-07-01).

### Methodology deviation (operator-driven, honest)
The staged full 262144-byte `imgA.bin` was **NOT** written. AM27C020 is a UV EPROM with **no
electrical erase and no UV eraser on hand** — every programmed bit (1→0) is permanent. Writing the
full pseudo-random image would consume the chip and could false-fail on 1→0 physics (a currently-0
bit cannot be set to 1). Instead we used the minimal, physically-valid **pure-1→0 program proof**:
a distinctive 64-byte ramp (`writeA.bin`, bytes 0x00..0x3F) written into a currently-all-`0xFF`
scratch region (verified against the pre-write baseline). From `0xFF`, every target byte is a
legal bit-clear, so a byte-exact read-back isolates exactly "does the `0x08` write path program?".
`firestarter dev write-cycle` was correctly NOT used (it erases first → fails on a UV EPROM).

### Baseline & payload SHAs
| Artifact | SHA-256 | Note |
|----------|---------|------|
| `prewrite.bin` (full chip, pre-any-write) | `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297` | pre-write read SHA (defer-branch evidence) |
| `writeA.bin` (64-byte ramp 0x00..0x3F) | `fdeab9acf3710362bd2658cdc9a29e8f9c757fcf9811603a8c447cd1d9151108` | the written image (small-write) |
| `imgA.bin` (staged full 256 KiB, UNUSED) | `b2fc5cbfcc25be3daa0e8e88e6977c7da6164a6fcf9c577ca943da940a133457` | staged in 99-02; not written (no-eraser constraint) |
| `readback.bin` (full chip, after write#1) | `4b192bbaeb928a5b99e0f5651f5c6c9439fa74efefe69c1cbcaa83962647a418` | == consistency-check SHA |
| `readback2.bin` (full chip, after write#2) | `5586826791e919f0e3bb150d67ce4ab80d132290dc9d76d97cb32d836c679487` | final chip state |

### Write #1 — `firestarter write AM27C020 writeA.bin -a 0x1da00 -b`
- Command RC: **1** — tool report: `Failed to write memory, 0x01da00, retries: 20, bad bytes: 4`.
- Read-back region `0x1da00..+64`: **60 / 64 bytes byte-exact** to the ramp (`+0x04`…`+0x3F`).
- Failed bytes: the **first 4** (`0x1da00`–`0x1da03`) stayed `0xFF` (unprogrammed).
- **This categorically refutes the Phase-97 "0 bits programmed" signature — the Phase-98 fix
  (rw-pin:[31] → `CTRL_READ_WRITE 0x40`) IS effective: the `0x08` write path programs bits.**

### Read stability — `firestarter dev consistency-check AM27C020 --runs 3`
- Verdict: **PASS**, N=3, **1 distinct SHA** (`4b192bba…a418`) — the partial-program state is
  real and stable, not a read glitch.

### Write #2 (confirmatory, different region) — `firestarter write AM27C020 writeA.bin -a 0x16600 -b`
- Command RC: **1** — tool report: `Failed to write memory, 0x016600, retries: 20, bad bytes: 64`.
- Read-back region `0x16600..+64`: **0 / 64** — entire region stayed `0xFF` (total program failure).
- Purpose was to test whether "first-4-bytes fail" is systematic. It is **not**: the two writes
  gave 60/64 vs 0/64 at the same VPP/firmware → the residual defect is **marginal / unreliable
  programming**, NOT a deterministic leading-byte offset bug.

### VPP
- Idle confirmation reads (both before write#1 and after write#2): **12.9–13.0 V**, Internal VCC 5.5 V
  — stable, in the 12.75±0.25 band.
- **Program-window VPP at socket pin 1: NOT MEASURED by DMM** — held-rail proxy is tooling-blocked
  (Phase-97 DTR-reset-on-close, see `.planning/…/reference_held_rail_dtr_reset_hold_script`). Program-
  window droop under load is the leading hypothesis for the marginality but was not instrumented
  this session. Recorded honestly as "not measured"; the idle ADC value is the only VPP evidence.

### SAFE-01 source assertion
- Both writes used `-b` only — **no `--skip-erase`, no `--force`** (verifiable in the recorded
  command lines above). SAFE-01 over-voltage guard intact.

---

## VERDICT: DEFER (fix-effective-but-unreliable) — BENCH-01 non-faked deferral

No byte-exact write→verify graduation was achieved (write#1 60/64, write#2 0/64), so `0x08` does
**not** graduate to PASS in v1.18. This is a **clean, documented, non-fabricated deferral** — and a
qualitatively different one from Phase-97:

- **Positive, RCA-critical finding:** the Phase-98 fix WORKS — the `0x08` write path now programs
  1→0 bits (60/64 byte-exact once; Phase-97's absolute "0 bits" is disproven).
- **Residual defect (new):** programming is **marginal/unreliable** — inconsistent across writes
  (60/64 vs 0/64) at a stable idle VPP. Not a deterministic offset bug.
- **Carry-forward:** open a new FUT (successor to FUT-06) — "AM27C020 0x08 write is functional but
  unreliable; characterize program-window VPP-under-load droop (DMM at pin 1) and write timing."
- **Pre-fix read SHA (defer evidence), by path:** `prewrite.bin` = `90cd45f5…7297`.

**Session end:** 2026-07-01 (operator-witnessed; Henrik).

