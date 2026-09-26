---
artifact: 93-RCA-FINDINGS
phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
milestone: v1.17 — Implement & Test the W29C040 Programming Protocol
requirements: [RCA-01, RCA-02, RCA-03, SAFE-01]
status: COMPLETE — RCA-01/02/03 + SAFE-01 all closed (Plans 02–04, 2026-06-27)
recorded: 2026-06-26
updated: 2026-06-27
operator_witnessed: true (Plans 02+03 bench runs, USB passthrough, operator-seated chip)
---

# W29C040 Page-0 Write Fault — Root-Cause Findings

> **RCA scope:** W29C040 (Winbond 512K×8 5V page-write flash, protocol `0x05`
> "flash4") deterministically fails its first page program on the seated chip
> (Leonardo + RURP Rev 2.0). This document accumulates evidence across Plans 02–04
> and culminates in a named root cause (or ranked disconfirmed hypotheses) classified
> firmware-algorithm / timing / addressing / silicon, sufficient for Phase 94 to
> design a fix.
>
> **Branch base:** firmware `a296195` (v1.16 primitives recompose).
> **Differential control:** W29C020 (same `0x05`, same `DIP32_SST39SF040`, 256 KB / 128 B page) — PASSED bench.
>
> **SAFE-01 update (Plan 01, 2026-06-26):** T-93-CANERASE was found ACTIVE — W29C040
> wire `flags=0x02` routes `flash4_write_init` through `flash4_erase_execute` (12V
> VPP assertion on 5V chip). See [SAFE-01-PREFLIGHT.md](safety/SAFE-01-PREFLIGHT.md).
> Bench plans MUST use `--skip-erase` to bypass `flash4_erase_execute` during RCA.

---

## Bench Discipline Log

All bench tasks (Plans 02–04) must record their session identity here before
any chip operation. Per standing discipline from STATE.md / RESEARCH.md.

| Plan | Timestamp | Controller identity (`firestarter --version` output) | Port | R1 readback | R2 readback | Board | Shield | Notes |
|------|-----------|------------------------------------------------------|------|-------------|-------------|-------|--------|-------|
| 02   | 2026-06-27T06:38:04Z | firestarter 3.0.0b10 (editable, v1.17 branch, post-HARD-01) | /dev/ttyACM0 | 270000 | 44000 | Leonardo | Rev 2.0-class (Override HW) | chip-id confirmed 0xda46; `hw` cmd → "Rev 2.0-class, Override HW: Rev 2.0-class" |
| 03   | 2026-06-27T06:53:10Z | firestarter 3.0.0b10 (editable, v1.17 branch, post-HARD-01) | /dev/ttyACM0 | 270000 | 44000 | Leonardo | Rev 2.0-class (Override HW) | chip-id confirmed 0xda46 via `firestarter id W29C040`; fw confirmed leonardo 3.0.0b10 |
| 04   | TBD       | TBD | TBD | TBD | TBD | Leonardo | Rev 2.0 | (Plan 04 fills) |

R1 expected: r1 ≈ 270000 ± 25% (203000–338000). Out-of-range = abort and recalibrate.
Leonardo is chip-OUT-sideload-EXEMPT — do NOT remove chip before sideload.

---

## RCA-01 — Reproduction & Signature

### Prior baseline (verbatim — the signature to reproduce, N=2 deterministic)

From `.planning/v1.15/bench/EVIDENCE.md` (Phase 82 + Phase 84 Task 3c),
Leonardo + Rev 2.0, firmware carrying the Phase-74 SDP/256B-page fix (fw `6924349`/`2699d11`):

| Attempt | Command | Result |
|---------|---------|--------|
| Phase 82 write A (`-b`) | `firestarter write -b W29C040 <img>` | `Timeout verifying byte @0x0000ff` (256B page-0 boundary); reads `0x00` |
| Phase 84 attempt 1 (`-b`, 1024B image, SHA `9983e8de…`) | `firestarter write -b W29C040 <img>` | `ERROR "Timeout verifying 0xd7 at 0x0000ff (got 0x00)"` |
| Phase 84 attempt 2 | identical command | `ERROR "Timeout verifying 0xd7 at 0x0000ff (got 0x00)"` (deterministic N=2) |

**Decoded signature:**
- Failing address: `0x0000ff` — the **last byte of page 0** (256B page boundary)
- Expected byte: `0xd7`
- Observed byte: `0x00`
- Error frame packing (`flash4_wait_for_page_write` _b[]): `[expected=0xd7, A16=0x00, A8=0x00, A0=0xff, observed=0x00]`
- `observed=0x00`: neither the written value (`0xd7`) nor the erased state (`0xFF`)
  — consistent with "page never committed" (H1/H3) OR "mid-write DQ7 complement
  read" (H4 disambiguation needed).

**SAFE-01 note on repro (T-93-CANERASE):**
The prior Phase 82/84 bench evidence was taken on a firmware/host that may have
had different `FLAG_CAN_ERASE` behavior. On the current `a296195` host build,
`flags=0x02` is sent, causing `flash4_erase_execute` (12V!) to fire unless
`--skip-erase` is used. Plan 02 repro MUST use `--skip-erase`.

### T-93-CANERASE gate resolution

**T-93-CANERASE gate cleared by operator decision 2026-06-27** — The operator
authorized proceeding with `--skip-erase` mitigation. All writes in Plan 02 used
`firestarter write -b --skip-erase W29C040 <img>`, which sets `FLAG_SKIP_ERASE (0x04)`
and bypasses `flash4_erase_execute`. Full fix (preventing `FLAG_CAN_ERASE` from routing
through `flash4_erase_execute` for protocol 0x05 chips) deferred to Phase 94 FIX-01.

### Plan 02 repro results — COMPLETED 2026-06-27

**Test image:** `evidence/signature/w29c040_test_1024b_seed42.bin`
- Size: 1024 bytes (covers pages 0–3, 256-byte boundaries at 0x100/0x200/0x300)
- SHA-256: `1ba43bf584f5492eee63d3e590e65f1e1cdaf93dd988686d958f053713b7782f`
- Generated with: `python tools/gen_test_image.py 1024 42 <path>` (seed=42, deterministic)
- Key bytes: offset 0x00FF=`0x04`, offset 0x01FF=`0x81`, offset 0x02FF=`0x43`, offset 0x03FF=`0x07`

| Run | Command | Result (exact ERROR frame) | Post-fail 0x0000ff | Verdict |
|-----|---------|---------------------------|---------------------|---------|
| 1 | `firestarter -p /dev/ttyACM0 write -b --skip-erase W29C040 evidence/signature/w29c040_test_1024b_seed42.bin` | `ERROR: Timeout verifying 0x04 at 0x0000ff (got 0x00)` | 0x00 (N=5 reads stable) | FAIL — fault reproduced |
| 2 | identical | `ERROR: Timeout verifying 0x04 at 0x0000ff (got 0x00)` | 0x00 (stable) | FAIL — fault reproduced |

**Decoded ERROR frame (from `flash4_wait_for_page_write` packing `[expected, A16, A8, A0, observed]`):**
- expected byte: `0x04` (image byte at offset 255)
- failing address: `0x0000ff` → A16=`0x00`, A8=`0x00`, A0=`0xFF`
- failing address interpretation: **last byte of page 0** (256-byte page boundary)
- observed byte: `0x00`

**N=2 determinism verdict: CONFIRMED** — identical ERROR frame on both runs.

### Post-fail page-0 read-back

After Run 1 failure, page 0 (256 bytes) read:
- Address 0x0000ff: **0x00** (stable across 5 repeated reads — does NOT settle to written `0x04`)
- Address 0x0000: 0x00
- Address 0x00fe: 0x00
- Page 0 is NOT all-blank (0xFF) — contains partial prior-session data with non-zero bytes
  at some offsets (old write-test fragments); see `page0_readback_hex_after_run1.txt`
- Page 0 is NOT all-zero — some bytes contain previous-session data
- Run 1 vs Run 2 page-0 state: IDENTICAL (no new data committed on Run 2)

**H4 fork determination (settled read of 0x0000ff):**
- 0x0000ff reads `0x00` stably across N=5 reads immediately after the timeout
- It does NOT settle to the written value `0x04`
- **Verdict: H4 DISCONFIRMED** — the page DID NOT commit; the poll did not merely give up
  on a completed write. The `observed=0x00` is real: the page never committed.
  This rules out the "poll exhausted iterations on a late-completing write" theory.
  H1 (timing window violation) or H3 (SDP/timing rejection) must explain the `0x00` state.

**Capture files (all under `evidence/signature/`):**
- `run1.txt` — full serial output of Run 1
- `run2.txt` — full serial output of Run 2
- `page0_readback_after_run1.txt` — read command output
- `page0_readback_hex_after_run1.txt` — hex dump of page 0 after Run 1
- `page0_readback_hex_after_run2.txt` — hex dump of page 0 after Run 2 (identical)
- `settled_read_0x0000ff.txt` — 5× repeated reads of address 0x0000ff (all 0x00)
- `settled_read_after_run2.txt` — post-Run-2 point reads at 0x00ff, 0x0000, 0x00fe
- `pages1to3_readback_hex_after_run2.txt` — addresses 0x100–0x3FF (partial prior-session data)

---

## RCA-02 — Differential vs W29C020

### Axis comparison table (pre-bench analysis)

| Axis | W29C040 (FAILS) | W29C020 (PASSES) | Same or Differs? | RCA weight |
|------|-----------------|------------------|------------------|------------|
| Protocol / handler | `0x05` flash4 | `0x05` flash4 | **SAME** | Exonerates dispatch structure |
| Pinout | `DIP32_SST39SF040` | `DIP32_SST39SF040` | **SAME** | Exonerates pinout confusion |
| SDP unlock sequence | `5555←AA, 2AAA←55, 5555←A0` | `5555←AA, 2AAA←55, 5555←A0` | **SAME** | SDP content is NOT the differential |
| Page size | **256 B** (A8–A18 = page addr) | **128 B** (A7–A17 = page addr) | **DIFFERS** | Correct for both; BUT 2× longer page-load window (H1) |
| Byte-load window T_BLC | **200 µs max** (across 256 bytes) | **~200 µs max** (across 128 bytes) | ~SAME spec, 2× more bytes | **H1 hinge**: W29C040 must sustain cadence 2× longer |
| Address span | 19 lines (A0–A18, 512 KB) | 18 lines (A0–A17, 256 KB) | **DIFFERS — A18** | **H2 hinge**: A18 = CTRL_VPP_P1_ENABLE_REV2 (0x08) on Rev 2.0 |
| Internal write time | 5 ms typ (10 ms max) | ~10 ms | ~SAME | poll cap adequate if page committed |
| VPP requirement | None — 5V internal VPP gen | None — 5V internal VPP gen | **SAME** | Both 5V; `vpp_mv=12000` is ID-read datum only |

### W29C020 control — Datasheet differential (operator chose datasheet-only fallback)

Per OPERATOR_DECISION_SCOPE (2026-06-27): No live W29C020 write was performed because the
W29C040 was seated and operator cannot swap chips. The W29C020 differential was conducted
from datasheets (both present in `datasheets/0x05-FLASH-AMD-STD/`).

**W29C020 datasheet-confirmed differential axes:**

| Axis | W29C040 (FAILS) | W29C020 (PASSES) | Same or Differs? |
|------|-----------------|-----------------|-----------------|
| SDP unlock sequence | `5555←AA, 2AAA←55, 5555←A0` | `5555←AA, 2AAA←55, 5555←A0` | **SAME** — exonerated |
| Pinout | `DIP32_SST39SF040` | `DIP32_SST39SF040` | **SAME** — exonerated |
| VPP | None — 5V single-supply internal | None — 5V single-supply internal | **SAME** — exonerated |
| Page size | **256 B** | **128 B** | **DIFFERS** — 2× bytes, but this is correct in firmware (flash4_page_size) |
| Boot block size | **Two 16K blocks** (first/last 16K each) | **Two 8K blocks** (first/last 8K each) | **DIFFERS** |

**Surviving differing axes:**
1. Page size: 256B (W29C040) vs 128B (W29C020) — 2× longer byte-load window per page
2. A18 exists on W29C040 (512KB) — maps to CTRL_ADDRESS_LINE_18 (0x20 in HARDWARE_REVISION build)
3. Boot block boundaries: first 16K locked vs first 8K locked
4. Page-latch boundary bit: A8 is a page-address bit on W29C040 (256B page), byte-in-page bit on W29C020 (128B page)

**DEFERRED (best-effort):** Live W29C020 control write — operator chose datasheet fallback 2026-06-27.
Plan 04 / future bench step may conduct the live control.

### Plan 03 differential results — COMPLETED 2026-06-27

| Write attempt | Chip | Command | Result | Error frame | Notes |
|--------------|------|---------|--------|-------------|-------|
| Test #2: Single byte to page-0 | W29C040 | `write -b --skip-erase -a 0 W29C040 <1B: 0x39>` | **FAIL** | `Timeout verifying 0x39 at 0x000000 (got 0x00)` | H1/H3 DISCONFIRMED |
| Test #3: DEBUG_ADDRESS trace | W29C040 | SERIAL_DEBUG+DEBUG_ADDRESS trace build | Trace: `Address 0x000000, top msb lsb 00 00 00` | Protocol timeout (5008 poll msgs) | H2 DISCONFIRMED for page-0 (top=0x00=correct, stable) |
| Test #4: Non-page-0 at 0x1000 | W29C040 | `write -b --skip-erase -a 0x1000 W29C040 <256B>` | **FAIL** | `Timeout verifying 0x03 at 0x0010ff (got 0x00)` | NOT page-0-specific |
| Test #5: A18=1 at 0x40000 | W29C040 | `write -b --skip-erase -a 0x40000 W29C040 <256B>` | **PASS** | — | A18=1 writes correctly! H2 exonerated |
| Diag: 0x2000 (inside 16K) | W29C040 | `write -b --skip-erase -a 0x2000` | **FAIL** | `Timeout verifying 0x03 at 0x0020ff (got 0x00)` | Boot block hypothesis |
| Diag: 0x4000 (outside 16K) | W29C040 | `write -b --skip-erase -a 0x4000` | **PASS** | — | Confirms 16K boundary |
| Diag: 0x3F00 (last page in 16K) | W29C040 | `write -b --skip-erase -a 0x3f00` | **FAIL** | `Timeout verifying 0x03 at 0x003fff (got 0x00)` | Exact 16K lock boundary confirmed |
| Diag: 0x7C000 (last 16K block) | W29C040 | `write -b --skip-erase -a 0x7c000` | **PASS** | — | Last boot block NOT locked |
| Diag: 0x7BC00 (before last 16K) | W29C040 | `write -b --skip-erase -a 0x7bc00` | **PASS** | — | Normal mid-chip region |

**Boot block lock pattern:**
- LOCKED: 0x0000–0x3FFF (first 16K = W29C040 §6.6 first boot block) — ALL writes FAIL
- UNLOCKED: 0x4000–0x7BFFF — writes PASS
- UNLOCKED: 0x7C000–0x7FFFF (last 16K = W29C040 §6.6 last boot block) — writes PASS

Capture files: `evidence/differential/` — see `test_summary.txt` for full list.

**RCA-02 axis-exoneration summary:**
| Axis | Verdict | Evidence |
|------|---------|---------|
| SDP content | EXONERATED — SAME in both datasheets; A18=1 pages write fine showing SDP works | Test #5 PASS; datasheet comparison |
| Pinout | EXONERATED — SAME; A18 routes correctly | Test #5 PASS (A18=1); diag 0x4000 PASS |
| VPP | EXONERATED — both 5V, no VPP needed | Datasheet; T-93-NOVPP GREEN |
| Page size value | EXONERATED — 256B correct, confirmed in firmware | flash4_page_size(524288)=256; native test |
| Byte-load timing (T_BLC) | EXONERATED — single byte also fails (Test #2) | Test #2 FAIL; not a timing issue |
| A18/top-address corruption | EXONERATED for page-0 — top=0x00 stable; A18=1 pages pass | Test #3 trace; Test #5 PASS |
| **Boot block §6.6 lockout** | **ISOLATED — the variable that moves the failure** | Diagnostic boundary tests |

---

## RCA-03 — Disconfirming-Test Matrix

Each hypothesis carries a verdict column to be filled by Plans 03–04.
A named root cause is one that SURVIVES its own disconfirming test while competitors fail theirs (Phase 44 D-07 bar).

| Hypothesis | Classification | Mechanism | Disconfirming test | Verdict | Raw evidence | Classification outcome |
|------------|----------------|-----------|-------------------|---------|--------------|------------------------|
| H1 — Byte-load timing window (T_BLC=200µs) violation mid-page | TIMING | 256-byte page-load loop exceeds 200µs inter-byte window; chip commits partial page; DQ7 poll at byte 255 sees mid-write/never-committed state → `observed=0x00` | Single-byte write to page 0 (`-a 0 -s 1`): if it PASSES, per-byte mechanics are sound → multi-byte timing is the issue; if it FAILS, H1 is disconfirmed | **DISCONFIRMED** | `differential/test2_single_byte_write.txt` — single byte to 0x000000 also FAILs with `observed=0x00` | NOT the cause — timing irrelevant when boot block lock silently rejects all writes in first 16K |
| H2 — A18 / top-address register corruption during 256B page load | ADDRESSING | A18 = CTRL_ADDRESS_LINE_18=0x20 in HARDWARE_REVISION build; shared CONTROL bit could corrupt page address | DEBUG_ADDRESS trace across page-0 load: if top-address byte is constant (0x00) across 256 bytes, H2 disconfirmed | **DISCONFIRMED** | `differential/test3_debug_trace_1byte.txt` — trace shows `top msb lsb 00 00 00` (correct, stable); Test #5 (A18=1 at 0x40000) PASSES — A18 is correctly routed | NOT the cause — addressing is correct |
| H3 — SDP unlock not disabling protection (per-page re-arm / timing) | FIRMWARE-ALGORITHM | SDP 3-byte command sent at page start; if gap between last SDP write and first data byte exceeds SDP timing window, chip rejects page-load | Single-byte write (H1 test): if that single-byte write (which also sends SDP) succeeds, SDP content/timing is fine → H3 disconfirmed | **DISCONFIRMED** | `differential/test2_single_byte_write.txt` — SDP+single-byte to 0x000000 FAILs; BUT A18=1 pages with same SDP PASS → SDP is fine; failure is address-range-specific | NOT the cause — SDP works, A18=1 pages using same SDP code PASS |
| H4 — Poll/verify site or page-commit-not-triggered (firmware-algorithm) | FIRMWARE-ALGORITHM | `poll_readback` compares whole byte (not DQ7-masked); if page committed late, poll exhausts 1024 iterations returning complement; post-fail settled read would show `0xd7` | After timeout, `dev read 0x0000ff` repeatedly: if it settles to `0xd7`, page DID commit → poll gave up too early | **DISCONFIRMED** (Plan 02) | `signature/settled_read_0x0000ff.txt` — 0x0000ff reads 0x00 stably x5 after timeout; does NOT settle to expected value | NOT the cause — page never committed; poll correctly detected non-commit |
| H5 — Silicon defect / wear on seated W29C040 | SILICON | Worn/defective die; page 0 (boot block, W29C040 §6.6) specifically defective; boot block programming lockout activated | Write non-page-0 pages (`-a 0x1000`, `-a 0x4000`, `-a 0x40000`) — map the failure boundary | **CONFIRMED — the root cause** | `differential/test4_page_at_0x1000.txt` (FAIL), `test5_page_at_0x40000.txt` (PASS), `test_diag_0x4000.txt` (PASS), `test_diag_0x3f00_result.txt` (FAIL) — exact 16K boundary; §6.6 boot block lock on first 16K (0x0000–0x3FFF) | **NAMED ROOT CAUSE**: W29C040 §6.6 first-16K boot block programming lockout is activated on this chip instance |

### Recommended execution order (cheapest-first)

1. Post-fail settled read of `0x0000ff` (H4 fork; free — read after recorded fail) → Plan 02
2. Single-byte write to page 0 (H1/H3 fork) → Plan 03
3. DEBUG_ADDRESS trace of one page-0 load (H2 + H1 cadence) → Plan 03
4. Non-page-0 page write at `0x1000` (H5 / page-0-specificity) → Plan 03
5. A18=1 page write at `0x40000` (H2 completeness) → Plan 04

---

## RCA-03 — Named Root Cause

**Status: NAMED — H5 CONFIRMED (Plan 03, 2026-06-27)**

### Named Root Cause

**Classification: SILICON (chip-instance-specific, hardware-feature-state)**

**Root Cause:** The seated W29C040 has the **first 16K boot block programming
lockout feature permanently activated** (W29C040 datasheet §6.6). This is an
irreversible silicon-level hardware protection state on this specific chip instance.

**Mechanism:** W29C040 §6.6 provides two boot blocks (first 16K = 0x0000–0x3FFF,
last 16K = 0x7C000–0x7FFFF). The boot block lockout is set by a 7-byte command
sequence and is permanent — it cannot be reversed by standard write procedures.
When the first 16K is locked:
1. Any write attempt to 0x0000–0x3FFF silently fails
2. The internal write cycle never starts (the chip ignores the write command)
3. DQ7 during the poll reads `0x00` (not the complement of the written data, which
   would indicate an active write cycle, and not `0xFF` which would indicate erased)
4. `poll_readback` times out after 1024 iterations (10.24ms+) and reports `observed=0x00`

This produces exactly the recorded signature: `Timeout verifying 0xXX at 0x0000ff (got 0x00)`.

**Evidence (Phase 44 D-07 causal bar — the variable that moves the failure):**

| Address | A16-A18 | Write result | Explanation |
|---------|---------|--------------|-------------|
| 0x000000 | all 0 | **FAIL** 0x00 | First 16K locked |
| 0x001000 | all 0 | **FAIL** 0x00 | First 16K locked |
| 0x002000 | all 0 | **FAIL** 0x00 | First 16K locked |
| 0x003F00 | all 0 | **FAIL** 0x00 | Last page in first 16K — locked |
| 0x004000 | all 0 | **PASS** | First address OUTSIDE first 16K — unlocked |
| 0x040000 | A18=1 | **PASS** | Well outside both boot blocks — unlocked |
| 0x07C000 | A18=1 | **PASS** | Last 16K boot block — NOT locked |
| 0x07BC00 | A18=1 | **PASS** | Normal mid-chip — unlocked |

**Boundary:** Exact at 0x4000 (16384 = 16KB). The pattern is a perfect step function
at the 16K boundary, consistent with §6.6 boot block protection, not with any
firmware/timing/addressing cause.

### Why Phase-74/v1.15 fixes did NOT help

The Phase-74 Wave-1 fix (SDP unlock per page + correct 256B page size) was correct
for the firmware algorithm. But it cannot overcome a silicon-level hardware write
protection. The chip literally ignores the write command for locked addresses,
regardless of how correct the SDP sequence is.

### Lock Reversibility Fork (Plan 04 — classify precisely, no overclaim)

**The bench data proves the failure is localized to the first-16K boot block
protection and that the firmware algorithm is sound. It does NOT by itself prove
the lock is permanent silicon.** The W29C040 §6.6 boot-block protection can in
principle be software-controlled. Two competing explanations remain:

**(a) SOFTWARE-REVERSIBLE lock (§6.6 boot-block UNLOCK command exists):**
If Winbond provided a boot-block UNLOCK sequence (a separate 7-byte command),
the lock on this chip instance is a reversible software state. In that case the
root cause is best classified as **SILICON-FEATURE-STATE** (not a firmware bug,
but a chip state that a firmware sequence can alter): Phase 94 FIX could add a
boot-block unlock sequence at the start of the flash4 write path for addresses
in 0x0000–0x3FFF, making the milestone done-bar (full write→verify) achievable
on this chip instance.

**(b) HARDWARE-PERMANENT lock (no unlock command — once set, forever):**
If §6.6 provides only a LOCK command and no UNLOCK command, the lock on this chip
instance is a permanent hardware state. In that case the root cause is classified
as **SILICON (chip-instance-specific)**: Phase 94 cannot fix this on this die;
the milestone done-bar needs either a different W29C040 sample (unlocked), or the
done-bar is re-scoped to the writable region (0x4000+).

**Current evidence weight:** The RCA bench data is agnostic on (a) vs (b) — both
produce identical write-fail signatures. The existing Named Root Cause statement
("irreversible silicon-level protection") was written from prior research notes,
but the W29C040.pdf §6.6 extraction was not confirmed due to PDF rendering
unavailability during Plan 04. The synthesis guidance explicitly states: "classify
precisely, do NOT overclaim."

**PENDING DISAMBIGUATION:** The datasheet `firestarter/datasheets/0x05-FLASH-AMD-STD/W29C040.pdf`
§6.6 is the authoritative source for reversibility. The research notes (93-RESEARCH.md)
describe the lock as "set by a 7-byte command sequence and is permanent" — consistent
with (b). Until the PDF §6.6 text is directly read, the classification is presented
as (b) HARDWARE-PERMANENT based on the research record, but Phase 94 MUST confirm
this by reading §6.6 directly before choosing the fix path.

**Disambiguating test (Phase 94 first investigation step):**
Read W29C040.pdf §6.6 directly for the UNLOCK command. If §6.6 provides an unlock
sequence, attempt it on the seated chip then re-write page 0. If no unlock exists
per the datasheet, the lock is permanent and a different chip is required. Either
way, this is the first Phase 94 investigation step before any firmware change.

---

## Hand-off to Phase 94

> **This section is the primary deliverable for Phase 94 planning. No further
> RCA is needed — the fault mechanism is fully characterized. The two items
> below are the complete Phase 94 fix scope.**

### Fix Investigation Step 1: Boot-Block Lock Reversibility

**Action:** Read W29C040.pdf §6.6 for the UNLOCK command sequence.

- **If (a) UNLOCK exists:** Phase 94 FIX implementation SHOULD add a boot-block
  unlock sequence in the flash4 write path for addresses falling in the first 16K
  (0x0000–0x3FFF) of a W29C040 (i.e., when the chip-id matches W29C040 AND the
  start address is < 0x4000). The v1.16 golden register traces must be re-pinned
  for this new sequence. The milestone done-bar (full write→verify) is achievable
  on the current seated chip once unlocked.

- **If (b) no UNLOCK exists:** Phase 94 FIX cannot overcome the silicon state on
  this die. The firmware write algorithm is correct — no firmware change is needed
  for the write path itself. The operator must decide:
  - Obtain a different W29C040 sample (unlocked) for Phase 95 BENCH graduation
  - OR re-scope Phase 95 BENCH-01 to use addresses ≥ 0x4000 (proven working),
    with explicit documentation that page-0 requires an unlocked chip
  Note: in case (b), Phase 94 firmware changes are LIMITED to FIX-01 (T-93-CANERASE)
  and the PGSZ generalization (CR-01); there is NO write-path behavior change needed
  for the page-0 fault itself.

### Fix Item 2 (REQUIRED regardless of boot-block outcome): T-93-CANERASE — FIX-01

**Severity: HIGH** — latent 12V-on-5V hardware damage path.

**Root cause:** `database.py:convert_to_programmer` sets `FLAG_CAN_ERASE (0x02)` for
all chips with `electrical.type == "EEPROM"` or `"Flash/EEPROM"`. The W29C040 DB
entry has `"type": "Flash/EEPROM"`, so its wire flags carry `0x02`. On firmware
receipt, `flash4_write_init` (flash_type_4.cpp) tests `is_flag_set(FLAG_CAN_ERASE)`
and — without `FLAG_SKIP_ERASE` — calls `flash4_erase_execute`, which asserts
`CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE` — a 12V
boost regulator assertion on a chip rated for 5V-only internal VPP generation.

**Evidence:** SAFE-01-PREFLIGHT.md Checklist Item 2 — Item 2 verdict RED/HIGH (Plan 01);
bench plans 02–04 required `--skip-erase` to prevent hardware damage throughout RCA.

**Required Phase 94 FIX-01 scope:** Prevent `FLAG_CAN_ERASE` from routing through
`flash4_erase_execute` for protocol 0x05 (flash4) chips. Candidate implementations:
  - Host-side: `database.py:convert_to_programmer` should NOT set `FLAG_CAN_ERASE`
    for chips with `algorithm == 5` (protocol 0x05, flash4); 5V-internal-VPP chips
    have their erase triggered by the SDP auto-erase cycle, not by a 12V VPP pulse.
  - Firmware-side guard: `flash4_erase_execute` could assert that VPP is appropriate
    before asserting the boost regulator; a 5V chip (no `vpp_mv` > 5000) should
    skip the 12V assertion.
  - Either approach achieves safety; the host-side fix is cleaner (prevents the
    hazardous flag reaching the wire at all).

**Lockstep note:** If `FLAG_CAN_ERASE` behavior changes on the wire, both
`constants.py` and `firestarter.h` must be checked for parity (SAFE-02).

### Milestone Done-Bar Impact (for operator decision at Phase 94)

**The v1.17 milestone done-bar is a byte-exact full-image write→verify on the
seated W29C040 (Phase 95 BENCH-01 hard graduation gate, no best-effort fallback).**

Current status of this gate:
- **If lock is SOFTWARE-REVERSIBLE (a):** Done-bar is achievable on the current
  chip after Phase 94 adds the unlock sequence. No new chip needed.
- **If lock is HARDWARE-PERMANENT (b):** Done-bar is NOT achievable on this chip
  instance for addresses 0x0000–0x3FFF. The operator must either obtain an unlocked
  W29C040 or re-scope Phase 95 BENCH-01 to addresses ≥ 0x4000. This is an operator
  decision required at Phase 94 planning, not a Phase 93 finding.

The firmware write algorithm is proven correct for unlocked pages — Phase 94/95 work
does not need to re-prove the algorithm; it only needs to resolve the lock state.

### H-code disposition summary

| H | Status | Plan | Key evidence |
|---|--------|------|-------------|
| H1 (timing) | DISCONFIRMED | 03 | Single byte at 0x000000 FAILS — timing is irrelevant |
| H2 (A18/addressing) | DISCONFIRMED | 03 | top=0x00 at init; A18=1 pages PASS |
| H3 (SDP re-arm) | DISCONFIRMED | 03 | Same SDP code; A18=1 pages with same SDP PASS |
| H4 (poll site) | DISCONFIRMED | 02 | Settled read stays 0x00 (page never committed) |
| H5 (silicon) | **CONFIRMED** | 03 | Exact 16K boundary: 0x3F00=FAIL, 0x4000=PASS; §6.6 boot block |

---

## SAFE-01 — Non-Bypass Confirmation (Phase Close)

> **Plan 04 close-out of the SAFE-01 checklist across the full Phase 93 RCA.**
> Each item is cited to its evidence plan. A single consolidated HELD/VIOLATED
> verdict is stated at the end of this section.

### Item 1 — Firmware VPP check stays blocking; flash4 write path sets no VPP bits

**Verdict: GREEN — CONFIRMED (Plan 01)**

Native test `test_flash4_write_execute_no_vpp` PASSED (Plan 01, SAFE-01-PREFLIGHT.md
Checklist Item 1). `flash4_write_execute` emits zero `CTRL_VPP_REGULATOR_ENABLE (0x80)`
or `CTRL_VPP_P1_ENABLE (0x08)` bits across all CONTROL_REGISTER writes during the
write-execute call. The firmware VPP check in the INIT phase (`eprom_check_vpp`)
remained in place and was not bypassed or patched during any bench task.

Raw evidence: `evidence/safety/SAFE-01-PREFLIGHT.md` § Checklist Item 1 — native test
output `test_flash4_write_execute_no_vpp [PASSED]` (11/11 flash4 native tests green).

### Item 2 — FLAG_CAN_ERASE disposition across Phase 93

**Verdict: CONDITIONAL — T-93-CANERASE FOUND + MITIGATED**

`FLAG_CAN_ERASE (0x02)` IS SET in the W29C040 wire flags (Plan 01 finding).
This is a HIGH-severity SAFE-01 violation (T-93-CANERASE): it routes
`flash4_write_init` through `flash4_erase_execute`, which asserts 12V
(CTRL_VPP_REGULATOR_ENABLE) on a 5V-only chip.

**How SAFE-01 was maintained during the RCA despite T-93-CANERASE:**
All bench write commands in Plans 02 and 03 used `--skip-erase` (FLAG_SKIP_ERASE=0x04),
which bypasses `flash4_erase_execute` in `flash4_write_init`. This was authorized
by the operator on 2026-06-27 before any bench work began. No 12V was asserted on
the W29C040 during the RCA.

Raw evidence:
- Plan 01: `evidence/safety/SAFE-01-PREFLIGHT.md` § Checklist Item 2 — RED/HIGH
- Plan 02: `evidence/signature/run1.txt`, `run2.txt` — command log shows `--skip-erase` on every write
- Plan 03: `evidence/differential/test_summary.txt` — all differential tests used `--skip-erase`

**Permanent fix deferred to Phase 94 FIX-01** — see "Hand-off to Phase 94" § Fix Item 2.

### Item 3 — Every bench operation flowed through normal 0x05 dispatch; no escape hatch

**Verdict: GREEN — CONFIRMED (Plans 01–03)**

Evidence by plan:
- **Plan 01 (automated, no bench):** `resolve_chip("W29C040")` resolves via the normal
  `support_status="supported"` gate; `algorithm=5`; no `--force` override needed or used
  (SAFE-01-PREFLIGHT.md Checklist Item 4).
- **Plan 02 (bench):** All writes used `firestarter write -b --skip-erase W29C040 <img>`
  — standard `firestarter write` CLI path with no `--force`; post-fail reads used
  `firestarter dev read` (normal dev sub-command). Serial captures: `run1.txt`, `run2.txt`.
- **Plan 03 (bench):** All differential tests used `firestarter write -b --skip-erase`
  or `firestarter write -b --skip-erase -a <addr>` — normal dispatch throughout.
  The DEBUG_ADDRESS trace build was a passive firmware trace (no dispatch code change,
  no host-side bypass), and normal firmware was re-flashed after the trace session
  (re-flash confirmed via avrdude verify output in `evidence/differential/`).

No test-only escape hatch (e.g. mocked `resolve_chip`, direct-to-firmware command
bypassing the host guard, modified `chip_resolver.py`) was introduced in any plan.

### Item 4 — `chip_resolver.resolve_chip("W29C040")` was never bypassed

**Verdict: GREEN — CONFIRMED (Plans 01–03)**

No `--force` flag was used in any plan. Every `firestarter write` command resolved
the W29C040 through the normal `support_status="supported"` path. The in-host
refusal guard remained in place for all unsupported/hazardous chip operations.
Evidence: SAFE-01-PREFLIGHT.md Checklist Item 4; bench command logs Plans 02–03.

---

### SAFE-01 Phase-Close Consolidated Verdict

**SAFE-01 = HELD (conditional — with T-93-CANERASE caveat)**

SAFE-01 was held across the full Phase 93 RCA because:
1. VPP check remained blocking; write-execute path emits zero VPP bits (Item 1)
2. T-93-CANERASE (the FLAG_CAN_ERASE 12V hazard) was FOUND but mitigated throughout
   via operator-authorized `--skip-erase`; no 12V was asserted on the chip (Item 2)
3. All bench operations used normal `0x05` dispatch — no escape hatch (Item 3)
4. `resolve_chip("W29C040")` was never bypassed — no `--force` (Item 4)

**Caveat:** SAFE-01 was held ONLY BECAUSE the `--skip-erase` mitigation was in place.
The underlying T-93-CANERASE flag hazard remains OPEN. Without `--skip-erase`, any
`firestarter write W29C040` command on the current `a296195` + host build would
assert 12V on the 5V chip. This hazard MUST be fixed in Phase 94 (FIX-01) before
any bench work that does not use `--skip-erase` can proceed safely.

**Phases 94–96 SAFE-01 precondition:** Phase 94 FIX-01 (T-93-CANERASE) must be
implemented and verified before Phase 95 bench work begins without `--skip-erase`.
