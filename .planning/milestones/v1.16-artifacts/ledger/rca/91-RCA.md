# Phase 91 — 12V-VPP Write-Path Regression RCA (working document)

**Started:** 2026-06-26 · **Firmware-under-test:** `firestarter@a296195` (recompose) ·
**Baseline:** `firestarter@a1953c2` (tag 3.0.0b10) · **Host:** `firestarter_app@e46549f`
vs v1.15 `98b3a92` · **Oracle:** Leonardo `/dev/ttyACM0` + RURP Rev 2.0.

> Operator handed full autonomous control. SST39SF040 (0x06) is seated and is the
> must-prove deliverable; W27C512 (0x07) bench re-validation is deferred to operator
> return (chip swap). This doc accumulates the A/B-first decision-tree evidence.

---

## Diff Forensics (Wave 1, Task 1 — static, no hardware)

Raw hunks captured in `diff-forensics.txt` (`git diff a1953c2..a296195` for the write-path
files). Verdict per changed file along the 0x06/0x07 write path:

| File | Change classification | Evidence |
|------|----------------------|----------|
| `src/proms/flash_type_3.cpp` (0x06 SST39SF040) | **comment-only** | The entire +22-line delta is a doc block (handler description + INV-09 keep-Flash/EEPROM note). Zero code lines changed. `configure_flash3()` body byte-identical. |
| `src/proms/eprom.cpp` (0x07 W27C512) | **measurement/extraction only — program path UNTOUCHED** | Changed hunks are confined to `eprom_check_vpp` (line ~263; VPP *guard/measurement*, extracted to share P3) + `eprom_check_chip_id`/`eprom_generic_init` + a doc header. `eprom_write_execute` (line 197, the actual program loop) is in NO changed hunk → byte-identical. `eprom_write_execute` appears in the diff only inside a `+ *` comment line. |
| `src/proms/primitives.cpp` + `include/primitives.h` (P3/P4/P5) | **new shared primitives; bodies byte-identical to originals** | P3 `vpp_check_window`, P5 `poll_readback` extracted; bodies equal the pre-recompose inline code. |
| `src/proms/flash_type_4.cpp` (0x05 W29C020) | extraction (poll_readback) | **flash4 PASSED on the bench** through this same P5 primitive — exonerates P5. |

**P3 `vpp_check_window` formally EXONERATED:** its body is byte-identical, and the
SST39SF040 (0x06/flash3) write path does **not** call P3 at all (flash3 is 5V-only,
never enables the VPP regulator). A P3 (or any single-primitive) regression cannot
explain the SST39SF040 failure. The "revert the recompose" hypothesis is **closed**.

### Host + DB wire-param parity (`98b3a92` vs `e46549f`)

- `chip_database.json` entry `SST39SF040` — **byte-identical** across the two host revs
  (`diff` empty). Verified this session.
- `chip_database.json` entry `W27C512,W27E512` (and all `27C512*` variants) —
  **byte-identical** across the two host revs (`diff` empty).
- Host write path (`eprom_operations.py`) v1.15→v1.16 delta = cosmetic output-dir
  grouping + a SRAM-only blank-check short-circuit (does not touch flash3/EPROM). The
  FLAG_CAN_ERASE refactor is zero-delta (predicate identical). (Per 91-RESEARCH §Sources.)

**Conclusion (Task 1):** Neither failing chip's write path changed in firmware OR host
OR DB between v1.15 and the recompose. The CONTEXT prior ("recompose regressed the write
path") is contradicted by the diffs.

---

## Native Trace Confirmation (Wave 1, Task 2 — unit, no board)

Re-ran the Phase-88 golden bus-sequence traces (pinned on the pre-recompose handlers,
green at Phase 89 on a296195) on the current recompose HEAD:

| Command | Result | Key cases |
|---------|--------|-----------|
| `pio test -e native -f "*test_val_flash3*"` | **6/6 PASSED** (3.26 s) | `test_golden_flash3_write`, `test_inv09_flash3_sst39sf040_keep_flash_eeprom`, write/erase/blank-check configure-no-VPP |
| `pio test -e native -f "*test_val_eprom*"` | **19/19 PASSED** (0.67 s) | `test_golden_eprom_0x07_write`, `test_inv05_eprom_vpp_skip_on_read`, `test_inv06_eprom_pulse_delay_defaults`, WR-02 chip-id severity fork |

**Coverage caveat** (per `reference_golden_trace_misses_severity_fork`): golden traces
with a matching id can miss the WARNING-vs-ERROR fork; the eprom suite now includes
explicit WR-02 mismatch cases, so this caveat is covered for 0x07. Analysis-only here.

**Conclusion (Task 2):** The recompose preserves the exact 0x06 write bus sequence
(12-entry golden) and the 0x07 write+chip-id sequence at the unit level. **Therefore any
bench write failure must be rail / timing / chip-state on real silicon — NOT a
bus-sequence code change.**

---

## A/B Prep (Wave 1, Task 3 — staged, no flash yet)

- **Images:** `/tmp/firestarter_bench_p90/SST39SF040_img_{A,B}.bin` (524288 B each)
  present. Image B SHA = `a38b13b4d285756c1f385a75d0cdf89f72720764c21fd933ced75ebdd970b96b`
  ✓ == v1.15 baseline + the **FIX-91 gate**.
- **b10 baseline build:** `git worktree add /tmp/fs-b10 a1953c2` (detached @ tag
  3.0.0b10), `pio run -e leonardo` → **SUCCESS, Flash 25654 B (89.5%)**, RAM 1999 B.
  Artifact: `/tmp/fs-b10/.pio/build/leonardo/firestarter_leonardo.hex`. Recompose HEAD
  still `a296195` (worktree did not move it).
- **Identity-disambiguation rule:** `firestarter fw` reports `3.0.0b10` for BOTH the
  recompose and b10 (version string NOT bumped). The ONLY reliable in-band discriminator
  is the **flash byte count: b10 = 25654 B, recompose = 25136 B** — confirm via the
  avrdude bytes-written line on each upload.

### Plan deviation (recorded)
Plan 01 Task 3 verify checks `/tmp/fs-b10/.pio/build/leonardo/firmware.hex`; this project
names the artifact `firestarter_leonardo.hex` (+ `.elf`). The build succeeded and the
artifact exists — substance met; the literal filename in the plan's `<automated>` check
was wrong. No impact on the A/B.

---

## ebca6266 Content Forensic (Open Q1) — Wave 2 Task 1

Re-read the seated SST39SF040 (non-destructive; read path proven byte-identical) BEFORE any
overwrite → SHA `ebca626663a78613a7572b792e00de11472aaefa84b41539ec5f5cfae3533e0b`,
**byte-identical to the Phase-90 capture** (read path stable; chip properly seated). Byte-compared
vs image B (`a38b13b4…`). Raw map in `ebca6266-forensic.txt`. Key result:

- **524285 / 524288 bytes match image B (99.9994%).** Only **3 bytes differ — all at offsets 0x0,
  0x1, 0x2.** Per-64KB block: every block 100.00% match except block 0 (the 3 bytes).
- All 3 differing bytes satisfy **`chip == imgA & imgB`** exactly:
  - 0x0: chip `0x04` = imgA `0x44` & imgB `0x1c`
  - 0x1: chip `0x20` = imgA `0x20` & imgB `0x2e`
  - 0x2: chip `0x02` = imgA `0x82` & imgB `0x2b`
- **Classification: partial-program / incomplete-erase at sector 0.** NOR cells erase to 0xFF
  (all-1) and program only clears 1→0. The `imgA & imgB` residue means those cells were NOT
  re-erased before image B was programmed over image A — the new bits that needed to go 0→1
  (require erase) could not be set. **A2 branch: timing/rail (erase-completeness), NOT
  addressing/buffer.** The Phase-90 "deterministically-wrong content" verdict was technically true
  (SHA differs) but is, mechanically, 3 un-erased bytes at the chip's very start.

## Reproduce on Recompose (a296195) — Wave 2 Task 2 (recompose leg)

Clean `write -b SST39SF040 imgB` on the current recompose fw: write reported **"successful
(177.66s)" RC=0**, but `verify` **RC=1: `0x1c != 0x04 at 0x000000`** — the SAME offset-0 failure,
**reproduced deterministically**. `0x04` (= prior residue) is a bit-subset of target `0x1c`
(needs bits 3,4 set → requires an erase). Confirms an erase-completeness failure at the start. The
firmware reports success because the per-byte DQ7 data-poll (`flash_util_verify_operation`, `& 0x80`
only) matches on bit 7 (both `0x04` and `0x1c` have bit7=0) and never detects the un-set low bits;
only the final full verify catches it. **[CORRECTED in "## Root Cause — DEFINITIVE": the erase was
not merely "not finishing" — it was SKIPPED entirely, because `write -b` sets `FLAG_SKIP_ERASE`.]**

> Note: VPP loaded-rail capture is N/A for flash3 — SST39SF040 is **5V-only and never enables the
> VPP regulator** (CLAUDE.md handler table 0x06 = None/5V). Also, a single serial port cannot
> monitor `vpp` and `write` concurrently. The "12V-VPP write-path" label never applied to 0x06;
> the real axis is **erase-before-write completeness**.

## Root Cause (RCA-91) — DEFINITIVE

**The erase was never running. `firestarter write -b` skips the erase that flash3 (NOR) requires.**

> An earlier intermediate hypothesis (marginal 105 ms chip-erase *timing*) is **SUPERSEDED**: a
> 105→500 ms firmware delay bump did NOT fix it (write B still `0x1c != 0x04 @0x0`), because the
> erase code block is never entered on the `-b` path. That firmware change was reverted; the
> recompose firmware is byte-identical and innocent.

Chain of evidence:
1. **`-b` sets `FLAG_SKIP_ERASE`.** Host `cli_handlers.py` write handler:
   `build_flags(blank_check, …, skip_erase=not blank_check)`. The `-b/--no-blank-check` option help
   literally reads *"Do not perform blank check before write (and skip erase)."* So `-b` →
   `blank_check=False` → `skip_erase=True` → `FLAG_SKIP_ERASE (0x04)` set. (Same in v1.15 host
   98b3a92 — documented, D-13.3 rationale-locked behavior.)
2. **flash3 honors it.** `flash3_write_init`: `if (FLAG_CAN_ERASE) { if (!FLAG_SKIP_ERASE) { erase }
   else { LOG skipping erase } }`. With `-b`, erase is **skipped**.
3. **SST39SF040 is NOR flash — it MUST be erased before write.** Programming only clears bits
   (1→0); setting a bit (0→1) requires erase to 0xFF. With no erase, any target byte that needs a
   bit the current content lacks cannot be written.
4. **Why it looked "99.99% correct":** the chip already held ≈image B from the prior write, so
   bytes 3+ were no-op re-writes (already correct); only bytes 0x0–0x2 (which needed bits set)
   stayed at `prev & new`. The DQ7-only per-byte poll (`flash_util_verify_operation`, `& 0x80`)
   matched on bit 7 and falsely reported each byte "successful" — so the firmware reported the whole
   write "successful" and only the final full verify caught it.
5. **Confirmed by the fix:** plain `firestarter write SST39SF040 imgB` (NO `-b`) → `blank_check=True`
   → `skip_erase=False` → flash3 erases (then post-erase blank-check passes, then programs) →
   **write RC=0 (239.89 s) + verify RC=0** (chip == image B == `a38b13b4…`). The ~240 s vs ~177 s
   delta is exactly the added chip-erase + blank-check pass.

**Why a P3 / VPP explanation never fit:** flash3 (0x06) is 5V-only, uses no P3 and never enables
the VPP regulator. The axis is **erase-before-write**. The W27C512 (0x07) `bad bytes:921 @0x0`
symptom is the same axis (a non-blank chip written with `write -b` → erase skipped → first block
can't take the new bits). The Phase-90 "12V-VPP write-path regression" was a **test-method error**:
`write -b` was used for both NOR/erase-required chips, silently skipping the required erase. The
firmware AND host are innocent of any v1.16 regression (b10 fails identically; the code is
byte-identical / the `-b` coupling predates v1.16).

## Fix Applied (FIX-91)

**Fix = use the erase-enabled write path for flash3.** SST39SF040 (and any electrically-erasable
NOR/EEPROM-class part) must be written with plain `firestarter write <chip> <file>` — which runs
erase → blank-check → program — NOT `firestarter write -b` (which skips both blank-check AND erase
and is only appropriate for already-blank or non-erasable/UV parts). No firmware or host **code**
change is required; the recompose firmware stays byte-identical to a296195 (reverted the
exploratory delay bump). The corrected method is recorded in BENCH-LOG, the ledger note, and the
W27C512 operator checklist.

**Recommended future hardening (NOT applied — touches D-13.3-locked `-b` semantics; left for
operator decision):** when `-b`/`FLAG_SKIP_ERASE` is used on a chip that reports `FLAG_CAN_ERASE`
(electrically erasable), emit a prominent WARNING (host pre-flight and/or firmware) that the erase
was skipped, so a skipped-erase NOR write cannot silently report "successful" while corrupting the
first bytes. This removes the footgun without changing the documented `-b` behavior.

## Decision Gate — Wave 2 Task 3

**b10 leg result:** reflashed b10 baseline fw (`a1953c2`, 25654 B avrdude-verified). The Leonardo
re-enumerated after upload (port ACM0→ACM1; the firestarter CLI auto-detected). `write -b imgB`
RC=0 "successful"; `verify` **RC=1 → `0x1c != 0x04 at 0x000000`** — **byte-identical failure to the
recompose leg.** SHAs in `bench/SST39SF040-ab/SHA256SUMS.txt`.

**Verdict: pre-existing / environmental — the recompose is INNOCENT.** Both the v1.16 recompose
(a296195) and the v1.15 baseline (a1953c2) fail identically at offset 0, on the same seated
SST39SF040 + Rev 2.0, because the flash3 write path (including the 105 ms erase delay) is
byte-identical between them (diff = comment-only). This is NOT recompose-fw and NOT host (the
write path runs on the firmware; the host merely streams bytes). It is a pre-existing marginal
chip-erase-completion timing bug. No host-axis A/B is needed (fw-cause is established on both legs).

**Indicated fix for Plan 03 (initial hypothesis — later CORRECTED):** the gate first pointed at a
flash3 chip-erase settle-timing margin. Wave-3 silicon testing **disproved** that (the 105→500 ms
bump did not fix it) and revealed the true cause: **`write -b` skips the required erase**
(`FLAG_SKIP_ERASE`). See "## Root Cause (RCA-91) — DEFINITIVE" and "## Fix Applied" below. The real
fix is the erase-enabled plain `write` path; no firmware change.

## Both Symptoms Explained (RCA-91 Success Criterion 2)

- **SST39SF040 (0x06, flash3):** write-A "timeout" + write-B "successful-but-wrong" is ONE
  mechanism — an **incomplete chip-erase at the 105 ms blind delay**. The first bytes programmed
  in the erase-tail overlap window land on un-erased cells (`prev & new` residue at 0x0–0x2); DQ7
  data-polling masks it per-byte; the final verify catches `0x1c != 0x04 @0x0`. Write-A's "timeout"
  in Phase 90 is the same family (the 524 KB write is a ~177 s slow path; a transient erase/poll
  stall on the first attempt). flash3 is **5V-only, no VPP** — so this is an erase-timing bug, not
  a VPP-rail bug.
- **W27C512 (0x07, EPROM-STD):** `bad bytes:921 @0x000000` on a clean 12.0 V rail is the **same
  erase-before-write axis** — a non-blank W27C512 whose erase did not clear the first block, so the
  program could not set the needed 0→1 bits (NOR/EEPROM-class). Per memory
  `reference_w27c512_bench_write_erase_gotcha`: "bad bytes:N is chip-state, not transport." (0x07
  bench re-validation is DEFERRED — operator chip swap; see the operator checklist.)
- **Why a P3-only / VPP explanation fails to cover both:** flash3 (0x06) uses **P4/P7, never P3,
  and never enables the VPP regulator** (5V-only). The common axis is **erase-before-write
  completeness**, NOT the 12V-VPP path. The Phase-90 "12V-VPP write-path" label was correlational
  (both happened to be write failures) — the mechanism is erase, for both.

## A/B Decision Tree (resolved by the legs above)

```
Reproduce SST39SF040 write on CURRENT fw (a296195)
        │  (expect: write-A timeout + write-B wrong content `ebca6266…`, per Phase 90)
        ▼
Flash b10 (a1953c2, 25654 B), re-run write -b cycle on SST39SF040
        ├─ b10 PASSES (SHA a38b13b4…) → recompose-fw causal (UNEXPECTED given zero code delta) → fix in fw
        ├─ b10 ALSO FAILS identically  → recompose INNOCENT → environmental/pre-existing  ◀── PRIMARY (HIGH prior)
        │        └─ host-axis backup A/B (pip install 98b3a92) → isolate host vs hardware/timing
        └─ b10 fails DIFFERENTLY        → mixed/marginal → deeper instrumentation
```

**Leading hypothesis (MEDIUM):** recompose innocent; the SST39SF040 failure is an
environmental / slow-path / timeout effect (flash3 is a ~177–240 s/write slow path; the
12.0 V rail was measured idle, never under write load). The `ebca6266…` content forensic
(Wave 2) + the loaded-rail `vpp` capture will discriminate partial-program vs transform.

---

## SST39SF040 Working-Write Confirmation (FIX-91 — Wave 3)

On **stock recompose firmware** (a296195, 25136 B, byte-identical — no firmware edit), Leonardo +
RURP Rev 2.0, using the erase-enabled plain `firestarter write` path:

| Step | Result |
|------|--------|
| `write SST39SF040 imgA` | RC=0 (240 s) — erase ran (chip held imgB; imgA needs bits erase must set) |
| `verify SST39SF040 imgA` | **RC=0** — erase + program of fully-different content succeeded |
| `write SST39SF040 imgB` | RC=0 (240 s) |
| `verify SST39SF040 imgB` | **RC=0** — chip == image B |
| `dev consistency-check --runs 3` | **PASS, 1 distinct SHA = `a38b13b4d285…970b96b`** (3/3) == v1.15 gate |
| negative control `verify imgA` | **RC=1** (verify non-vacuous) |

**FIX-91 GATE MET.** Evidence: `bench/SST39SF040-fix/SHA256SUMS.txt`. The ~240 s write (vs ~177 s
for `write -b`) is exactly the added chip-erase + post-erase blank-check pass.

## Board Restore + SAFE-04 (Wave 3)

- **Board left on milestone firmware:** stock recompose a296195 (25136 B), `firestarter fw` →
  leonardo on /dev/ttyACM0 (port re-settled to ACM0 after the final reflash). The exploratory
  105→500 ms delay change was **reverted** — `git status --porcelain src include` is empty
  (firmware byte-identical to a296195).
- **SAFE-04 verified intact:** the VPP over-voltage guard `vpp_check_window` (+500 mV HIGH check,
  D-08, `primitives.cpp:106`) is PRESENT + UNMODIFIED; BLOCKER-2 (no 12V to a no-VPP pinout)
  unaffected (flash3 is 5V-only and never enables the regulator). No safety guard was weakened to
  achieve the working write.
- **Worktrees cleaned:** `/tmp/fs-b10` (b10 fw) and `/tmp/fsa-b8` (v1.15 host) removed. Meta
  gitlinks NOT bumped (D-06).

## Status
- [x] Wave 1 Task 1 — diff forensics captured + verdict (recompose innocent)
- [x] Wave 1 Task 2 — native golden traces green (bus sequence preserved)
- [x] Wave 1 Task 3 — A/B images SHA-verified + b10 baseline built + identity rule
- [x] Wave 2 — bench A/B + ebca6266 forensic + decision gate (recompose innocent)
- [x] Wave 3 — TRUE root cause (`write -b` skips required erase); fix = plain `write`; SST39SF040
      confirmed == a38b13b4 (3/3) on stock recompose; firmware reverted; SAFE-04 intact
- [ ] Wave 4 — disposition ledger rows + W27C512 operator checklist

## Phase 91 Wrap-Up

- **RCA-91 (cause attribution + both symptoms):** the 0x06/0x07 "12V-VPP write-path regression" is a
  **test-method error**, not a code regression. `firestarter write -b` sets `FLAG_SKIP_ERASE`; flash3
  (SST39SF040, NOR) and the EEPROM-class W27C512 require erase-before-write, so `-b` leaves bits that
  can't be programmed (SST39SF040: 3 stuck bytes @0x0-0x2 `== imgA & imgB`; W27C512: bad-bytes @0x0
  on a non-blank chip). The DQ7-only poll masked it as "write successful." Controlled A/B: b10
  (a1953c2) fails identically to the recompose (a296195) → recompose **innocent**; diff is
  comment-only and DB wire params byte-identical. Both symptoms = one axis (erase-before-write), NOT
  VPP — flash3 is 5V-only and never enables the regulator.
- **FIX-91 (SST39SF040 / 0x06):** **CONFIRMED WORKING.** Erase-enabled plain `firestarter write`
  (writeA→verifyA→writeB→verifyB→consistency-check N=3) is byte-identical to the v1.15 baseline
  `a38b13b4…` (3/3, 1 distinct SHA) on **stock recompose firmware** (no code edit); neg-control RC=1;
  SAFE-04 intact. 0x06 PROTOCOL-LEDGER row **graduated to PASS** (LEDGER-02 satisfied for 0x06).
- **0x07 W27C512:** **NOW PASS (operator returned + W27C512 seated, 2026-06-26).** chip-ID check
  PASSED (0xDA08); erase-enabled plain `firestarter write` (writeA→verifyA→writeB→verifyB→
  consistency-check N=3) byte-identical to v1.15 `e16b2a5b…` on stock recompose a296195; no VPP-high
  guard. Confirms the SAME `write -b` skipped-erase cause/fix as 0x06 (`eprom_internal_erase` gated
  on FLAG_CAN_ERASE, which W27C512 has). Evidence: `bench/W27C512-fix/`.
- **LEDGER-02 status: FULLY SATISFIED — all 4 on-hand protocols PASS (0x05, 0x06, 0x07, 0x28).**
- **Recommended hardening (NOT applied — D-13.3 `-b` semantics are rationale-locked):** warn when
  `-b`/`FLAG_SKIP_ERASE` is used on a `FLAG_CAN_ERASE` chip, so a skipped-erase NOR/EEPROM write
  cannot silently report "successful." Left for operator decision.
