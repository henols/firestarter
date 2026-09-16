# v1.18 Bench EVIDENCE — AM27C020 0x08 Write-Path RCA

**Generated:** 2026-06-29T15:43:35Z
**Milestone:** v1.18 — AM27C020 0x08 Write-Path RCA & Fix
**Phase:** 97 — pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
**Board / Shield (LOCKED):** Leonardo + RURP Rev 2.0
**Branch base:** firmware `bccd995` (v1.17 tip) · host `e0bdea4`

> **STATUS: COMPLETE (Plans 97-02/03, 2026-06-30).** **NEVER-fabricated** cells,
> mirroring `EVIDENCE.json`. Cell A (AM27C020 / `0x08`) = the reproduced 0-bits
> signature (Plan 97-02); Cell B (W27C512 / `0x07`) = the byte-exact
> differential-control PASS (Plan 97-03). Per **D-02** the Tier-0 0-bit-flip is
> **INDETERMINATE pre-fix** and is **never fabricated** (tooling-blocked DMM reads
> recorded "not measured"); per **D-01** a 0-flip never triggers deferral.
> Schema reuses the v1.15 `EVIDENCE.{md,json}` cell shape so Phase 99 + the
> PROTOCOL-LEDGER consume the same format ("Don't Hand-Roll" §EVIDENCE format).

---

## PRE-01 Result Line (artifact 4)

| Field | Value |
|-------|-------|
| pre_01_result | PRE-01 reads captured 2026-06-30 (oracle N=3 PASS; decode 0x08/0x197 confirmed; NOT-BLANK 0x02@0x0000). Writability verdict = **INDETERMINATE pre-fix**, set by the Task-3 micro-probe (D-01/D-02) |
| blank_state_sha256 | `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297` (consistency-check N=3 byte-identical; NOT-BLANK `0x02 @ 0x0000`) |

PRE-01's Phase-97 deliverable is **"writability indeterminate pre-fix"** — NOT a
pass/fail blocker (D-02). The Tier-0 micro-probe and the RCA-01 failure
reproduction are the **same single bench action** (D-01); a 0-bit-flip is
consistent with both "broken path" and "OTP" so it proves nothing about silicon
and **never triggers deferral** (deferral is a Phase-99 verdict only, D-06).

---

## Bench-Discipline Columns (D-08) — filled per task at the bench

| Plan | Timestamp | Controller identity | Port | R1 | R2 | Board | Shield | JP4 position + silkscreen meaning | fw commit | Notes |
|------|-----------|---------------------|------|----|----|-------|--------|-----------------------------------|-----------|-------|
| 97-02 | 2026-06-30 ~07:29Z | leonardo | /dev/ttyACM0 | 270000 | 44000 | Leonardo | Rev 2.0 | **open** (operator-stated); silkscreen meaning PENDING (D-08) — fw `info` says 32-pin=Closed, **discrepancy flagged** | bccd995 (3.0.0b10) | PRE-01 reads done; VPP adjusted 12.0→13.0V before Task-3 (operator) |
| 97-03 | 2026-06-30 ~09:40Z | leonardo | /dev/ttyACM0 | 270000 | 44000 | Leonardo | Rev 2.0 | **open** (28-pin position for W27C512) | bccd995 | 0x07 control; VPP 12.0V (W27C512 target). First seated ST M27C512 (0x203d/13V/UV) → swapped to Winbond W27C512 (0xda08/12V/EEPROM) |

R1 expected ≈ 270000 ± 25% (Leonardo). `controller:` identity re-verified per task (ACM ports shuffle — D-08). Leonardo is chip-OUT-sideload-EXEMPT.

---

## Cell A — AM27C020 (`0x08` EPROM_QUICK) — Plan 97-02

Op: `tier0_microprobe+rca01` (the combined single program attempt at `0x000000`).

| Field (Failure Signature Capture Schema) | Source | Value |
|------------------------------------------|--------|-------|
| failing_addresses | `firestarter write` stderr (`MSG_ERR_VERIFY`) | **0x000000** |
| bad_bytes | write output | **1/1** |
| retries | write output | **20** (matches v1.15 seed) |
| bits_flipped | post-attempt consistency-check vs pre-SHA | **0** → writability INDETERMINATE pre-fix (D-01/D-02) |
| vpp_adc_mv | `firestarter vpp` ADC node | baseline 12000 (as-found); adjusted to **13000** before Task-3; during-attempt value = Task-3 |
| dmm_pin1_v | [OP] held-rail proxy DMM at socket pin 1 | **not measured** — held-rail proxy blocked by DTR-reset-on-close tooling bug (debug: held-rail-dev-reg-timeout, H1). VPP→pin-1 routing **confirmed by code** (-f 0x188 → physical 0x89, P1 asserted; H2 disproven) |
| dmm_pin31_v | [OP] held-rail proxy DMM at socket pin 31 | **not measured** — same tooling block; pin-31 = A18 mapping confirmed by `info` decode (RC-1) |
| pre_read_sha256 | consistency-check (pre-attempt) | `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297` |
| post_read_sha256 | consistency-check (post-attempt) | `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297` (**== pre → chip pristine**) |
| controller | `firestarter fw` / `hw` | leonardo |
| port | `firestarter fw` | /dev/ttyACM0 |
| r1_readback | `firestarter config` | 270000 |
| r2_readback | `firestarter config` | 44000 |
| fw_commit | `git -C firestarter rev-parse HEAD` | bccd995 (fw 3.0.0b10) |
| jp4_position | [OP] | open (operator-stated 2026-06-30) |
| jp4_silkscreen_meaning | [OP] — ASK first (D-08) | PENDING — fw `info` says 32-pin=Closed; operator has OPEN → discrepancy flagged, resolve before Task-3 |
| verdict | RCA synthesis | **RCA-01 REPRODUCED** — 0x08 writes 0 bits @ 0x000000 (1/1 bad, retries 20) at VPP=13.0V + JP4 **closed**; chip pristine. Writability INDETERMINATE. Confounds (VPP-level, JP4) exonerated → cause = RC-1 (pin31=A18) / RC-2-routing |
| anomalies | — | VPP as-found 12.0V→13.0V (operator); VPE 13.8→15.1V; pin 31 = A18 (RC-1); flags=0x08 SkipBlankCheck only (SAFE-01 intact); `-b` used (chip non-blank — justified deviation, Phase-92 decouple = blank-check skip only) |

---

## Cell B — W27C512 (`0x07` EPROM_STD) — Plan 97-03 differential control

Op: `differential_control_write` (passing-sibling control, same session/bench, same `configure_eprom()`).

| Field | Source | Value |
|-------|--------|-------|
| write_image_sha256 | generated 4KB control image | `d9471636ca34b84f863a666eff6ff6aa4fc44396b2ff11a38e036e54b4b39ee3` |
| readback_sha256 | post-write read (first-4096) | `d9471636…b39ee3` (**== image → byte-exact**) |
| vpp_adc_mv | `firestarter vpp` | 12000 (12.0–12.1V; W27C512 target 12.0V) |
| dmm_pin1_v | [OP] | not measured (proxy tooling-blocked; N/A — 28-pin pin 1 = A15, not VPP) |
| verdict | expect PASS (exonerates unchanged axes) | **PASS** — write 6.52s + verify 0.64s + readback byte-exact; exonerates all shared axes → cause = RC-1 (32-pin pin-31=A18) |
| anomalies | — | Operator first seated ST **M27C512** (id 0x203d, UV, 13V) → chip-ID aborted write (pristine); swapped to Winbond **W27C512** (0xda08, EEPROM, 12V) = correct reversible control. JP4 open (28-pin), VPP 12.0V |

---

## Cell C — AM27C020 (`0x08` EPROM_QUICK) — Plan 99-03/04 (post-fix bench)

Op: `phase99_deferral` (Phase-98 fix bench-tested; small pure-1→0 writes, no UV eraser on hand).

**Method deviation (operator-driven, honest):** the staged full 262144-byte `imgA.bin` was NOT
written — AM27C020 is a UV EPROM with no electrical erase and no UV eraser on hand, so every
programmed bit is permanent and a full pseudo-random image could false-fail on 1→0 physics.
Instead, a distinctive 64-byte ramp (`writeA.bin`, bytes `0x00..0x3F`) was written into scratch
regions that were confirmed all-`0xFF` against the pre-write baseline, so a byte-exact read-back
isolates exactly "does the `0x08` write path program?". `firestarter dev write-cycle` was
correctly NOT used (it erases first, which fails on a UV EPROM).

| Field | Source | Value |
|-------|--------|-------|
| controller | `firestarter fw` / `hw` | leonardo |
| port | `firestarter fw` | /dev/ttyACM0 |
| r1_readback | `firestarter config` | 270000 |
| r2_readback | `firestarter config` | 44000 |
| fw_commit | `git -C firestarter rev-parse HEAD` (reflashed + avrdude-verified this session) | **35706c2** (Phase 98-05 fix; version string 3.0.0b10, does not distinguish the fix) |
| jp4_position | [OP] | not recorded this session |
| vpp_adc_mv | `firestarter vpp` ADC node | **12900–13000** (idle, before write#1 and after write#2; stable, 12.75±0.25 band) |
| dmm_pin1_v | [OP] held-rail proxy DMM at socket pin 1 | **not measured** — held-rail proxy blocked (DTR-reset-on-close, Phase-97 precedent). Program-window VPP droop under load is the leading marginality hypothesis but was not instrumented; idle ADC is the only VPP evidence |
| write_image_sha256 | `writeA.bin` (64-byte ramp) | `fdeab9acf3710362bd2658cdc9a29e8f9c757fcf9811603a8c447cd1d9151108` |
| pre_read_sha256 | `prewrite.bin` (full chip, pre-any-write) | `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297` |
| post_read_sha256 | `readback2.bin` (full chip, after write#2, final chip state) | `5586826791e919f0e3bb150d67ce4ab80d132290dc9d76d97cb32d836c679487` (**!= pre → bits DID program**, unlike the Phase-97 pristine result) |
| bits_flipped | write#1/#2 read-back comparison | **write#1 @0x1da00: 60/64 bytes byte-exact** (ramp `+0x04`…`+0x3F`; first 4 bytes stayed `0xFF`; bad_bytes 4, retries 20). **write#2 @0x16600 (confirmatory, different region): 0/64** (bad_bytes 64, retries 20) — marginal/unreliable, not a deterministic leading-byte-offset bug |
| readback | full-chip readback SHA after write#1 | `4b192bbaeb928a5b99e0f5651f5c6c9439fa74efefe69c1cbcaa83962647a418`; `firestarter dev consistency-check --runs 3` = **PASS**, 1 distinct SHA (partial-program state is real and stable, not a read glitch) |
| verdict | bench synthesis | **DEFER (fix-effective-but-unreliable)** — Phase-98 fix (rw-pin:[31] → `CTRL_READ_WRITE 0x40`) programs bits (Phase-97 absolute "0 bits" REFUTED: 60/64 byte-exact once) but programming is marginal/unreliable (write#2 0/64 at the same stable idle VPP); no byte-exact graduation → `0x08` does not graduate to PASS. Carry-forward: **FUT-08** (successor to FUT-06; FUT-07 is the unrelated v1.17 W29C040 defect) — characterize program-window VPP-under-load droop (DMM at pin 1) + write timing |
| anomalies | — | No UV eraser on hand; full `imgA.bin` NOT written (see Method deviation above). Both writes used `-b` only — no `--skip-erase`, no `--force` (SAFE-01 intact) |

**Positive, RCA-critical finding:** the Phase-98 fix WORKS — `pre_read_sha256 != post_read_sha256`
proves the `0x08` write path programs 1→0 bits post-fix, categorically refuting the Phase-97 cell's
"0 bits programmed" signature. The residual defect is a **new, qualitatively different** one:
marginal/unreliable programming (60/64 vs 0/64 across two attempts at the same stable idle VPP),
not the deterministic 0-bits failure RCA'd in Phase 97.

---

## Differential collapse (RCA-02 framing)

The matrix collapses to **two converging differing axes** — both absent on the
passing `0x07` part:

1. **P1-VPP-delivery** — VPP routed to socket **pin 1** via the
   `CTRL_VPE_ENABLE → CTRL_VPP_P1_ENABLE` rewrite (`eprom.cpp:319-326`), never
   bench-proven on a `0x08` UV part.
2. **pin-31-as-address** — DIP `pin 31` modeled as bus line 22 (address-driven),
   not held program-active (`database.py:141`, `memory.cpp:346`).

Both verdicts (RC-1 / RC-2) are recorded in
`evidence/97-RCA-FINDINGS.md` (D-03: each must individually carry a verdict).
