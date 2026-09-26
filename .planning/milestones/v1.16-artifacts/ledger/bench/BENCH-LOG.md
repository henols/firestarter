# Phase 90 — Bench Validation Log (LEDGER-02)

Per-protocol bench regression of the recomposed firmware against the v1.15 byte-exact
baseline. Every live silicon op is operator-gated (D-05). PASS = read-SHA (N≥3) **and**
write-cycle A→B final SHA both byte-identical to the v1.15 baseline (D-01). Any mismatch
is recorded FAIL-INVESTIGATE, never auto-passed (D-03). Gitlinks stay PINNED at b10 (D-06).

---

## Session Header

| Field | Value |
|-------|-------|
| Date | 2026-06-26 |
| Firmware-under-test (identity) | `firestarter` submodule HEAD **a296195** (Phase-89 recompose) |
| Version string (caveat) | `3.0.0b10` — NOT bumped at Phase 84; the version string does **not** distinguish the recompose from stock b10. The submodule commit `a296195` is the firmware-under-test identity (D / version_string_caveat). |
| Controller | **leonardo** on `/dev/ttyACM0` (`firestarter fw` confirmed pre- and post-flash) |
| Shield (oracle) | **Rev 2.0** — operator-confirmed silkscreen (the EEPROM HW byte reads "Rev 2.0-class" but cannot reliably distinguish Rev 2.0/2.2/Rev0; silkscreen is the mandatory oracle, D-09). |
| Build result | `pio run -e leonardo` → **Flash 87.7% (25136 B / 28672 B)**, RAM 78.1% (1999 B). Matches the expected recompose figure (RESEARCH §184). |
| Flash result | `pio run -t upload -e leonardo` → 25136 bytes written + **verified** (avrdude), SUCCESS. Operator-authorized; Leonardo EXEMPT from chip-out-before-sideload (D-06). |

### Image-SHA Sanity (BEFORE any silicon op)

`gen_test_image.py <size> <seed> <out>` — seed 1 = image A, seed 2 = image B. All 4 chips'
generated A/B SHAs are byte-identical to the v1.15 baseline (RESEARCH lines 123-128) — the
deterministic generator is byte-stable on this host. Any mismatch here would be a
generator/host problem; all matched, so we proceed to silicon.

| Chip | size (B) | img_A SHA (seed 1) | matches v1.15 | img_B SHA (seed 2) | matches v1.15 |
|------|----------|--------------------|---------------|--------------------|---------------|
| W29C020    | 262144 | `b2fc5cbfcc25be3daa0e8e88e6977c7da6164a6fcf9c577ca943da940a133457` | ✓ | `47304933ce388bfd97d23ea6bff1a5ed1f7728e99f2cc3e7d05c82a7c11ce58c` | ✓ |
| SST39SF040 | 524288 | `77a771b26acca207c670a22ade19f8d6f0258a79fefb789be2ea7a40f1662bbd` | ✓ | `a38b13b4d285756c1f385a75d0cdf89f72720764c21fd933ced75ebdd970b96b` | ✓ |
| W27C512    | 65536  | `604d957094f7cb1f98f50d7408f64e7720e5ae5d4acab8d1047a9a081645d637` | ✓ | `e16b2a5b26d99440a8e596963faa0f2d64fff4e1dd9682b93b2f8f1ddc326ab5` | ✓ |
| FM1608     | 8192   | `a89c4b45ae8a2dac63911f153cff29d4d59f8d61c5579f93a53e8d078ce5415d` | ✓ | `3c23e7fcbe88c5a09ab50cf8301e9adf884fcdd519b6f9fefc72583b34f75c90` | ✓ |

Images staged at `/tmp/firestarter_bench_p90/<chip>_img_{A,B}.bin`.

---

## Per-Chip Regression Blocks

> Sequencing (D-01): READ regression (N≥3) runs BEFORE the write-cycle per chip — the
> write overwrites the contents the read baseline measured. Preconditions per chip:
> operator confirms controller identity + port, confirms Rev 2.0 silkscreen, seats ONE
> chip, authorizes the live op.

### Harness deviation (grounded in v1.15 EVIDENCE) — applies to all flash/EPROM chips

The plan's Task 2 prescribes `dev write-cycle` for W29C020/SST39SF040/W27C512. The v1.15
EVIDENCE (`.planning/milestones/v1.15-artifacts/bench/EVIDENCE.md` rows 1/5/6/8) shows **all four** baselines were
produced via the **`write -b` direct path** (`write -b A` → verify → `write -b B` → verify →
`consistency-check N=3`), which proves auto-erase by writing B over A with *no explicit erase*.
`dev write-cycle` does erase→blank-checked-write, which (a) **fails on flash4** — confirmed: two
`dev write-cycle` attempts on W29C020 returned `Not blank, at 0x000000, v:0x1c` (RC=2) because
flash4 has no real bulk-erase (per-page auto-erase on write), and (b) would defeat the auto-erase
proof even where it works. **Deviation: use the v1.15 `write -b` direct path for all 4 chips** —
the exact method that produced the baselines. The failed `dev write-cycle` attempts wrote nothing
(blank-check refused), so no chip state was altered by them.

> **D-01 read-baseline nuance (all 4 chips):** v1.15's own write-cycle left image B on each chip,
> overwriting the pre-write contents the v1.15 read-baseline measured (RESEARCH line 130). So each
> Phase-90 pre-write read returns image B = the v1.15 **write-cycle-final** SHA, NOT the v1.15
> read-baseline (which is unreachable by design). A read PASS = N≥3 internally consistent AND
> byte-identical to the v1.15 write-cycle-final baseline (image B retained). Read path confirmed
> behavior-preserving.

---

### Chip 1 — W29C020 (0x05 FLASH-AMD-STD, flash4, 262144 B) — **PASS**

| Field | Value |
|-------|-------|
| Port identity | leonardo on `/dev/ttyACM0` (`firestarter fw` confirmed pre-op) |
| Shield | Rev 2.0 (operator silkscreen confirmed) |
| Operator authorize | Seated + authorized W29C020 live ops |
| **READ** (N=3, ran FIRST) | `firestarter dev consistency-check W29C020 --runs 3 --output-dir bench/W29C020-read/` → RC=0, **PASS, 1 distinct SHA** |
| Read SHA | `47304933ce388bfd97d23ea6bff1a5ed1f7728e99f2cc3e7d05c82a7c11ce58c` |
| Read SHA-match | ✓ == v1.15 **write-cycle-final** baseline (chip holds image B; D-01 nuance above). Read path byte-identical. |
| `dev write-cycle` attempt | RC=2 `Not blank @0x000000 v:0x1c` — expected flash4 limitation, wrote nothing (see deviation note). |
| **WRITE-CYCLE A→B** (`write -b`) | `write -b A` RC=0 → `verify A` RC=0 (34.28s) → `write -b B` RC=0 → `verify B` RC=0 (34.26s). B over A, no explicit erase = **auto-erase proven**. |
| Post-B readback (N=3) | `consistency-check --runs 3 --output-dir bench/W29C020-wcB/` → RC=0, PASS, 1 distinct SHA = `47304933ce388bfd97d23ea6bff1a5ed1f7728e99f2cc3e7d05c82a7c11ce58c` |
| Write-cycle SHA-match | ✓ == v1.15 write-cycle-final baseline `47304933…c11ce58c` |
| Negative control | `verify W29C020 img_A` → RC=1 ✓ (verify non-vacuous) |
| Evidence refs | `bench/W29C020-read/run_{01,02,03}.bin`, `bench/W29C020-wcB/run_{01,02,03}.bin` |
| **Verdict** | **PASS** — read + write-cycle both byte-identical to v1.15 baseline. |

### Chip 2 — W27C512 (0x07 EPROM-STD, 65536 B) — **FAIL-INVESTIGATE** (write path; read PASS)

| Field | Value |
|-------|-------|
| Port identity | leonardo on `/dev/ttyACM0` (confirmed pre-op + after reseat) |
| Shield | Rev 2.0 (operator silkscreen confirmed) |
| Operator authorize | Seated + authorized; reseat + 1 retry authorized after first fail |
| **READ** (N=3, ran FIRST) | `consistency-check W27C512 --runs 3 --output-dir bench/W27C512-read/` → RC=0, **PASS, 1 distinct SHA** |
| Read SHA | `e16b2a5b26d99440a8e596963faa0f2d64fff4e1dd9682b93b2f8f1ddc326ab5` |
| Read SHA-match | ✓ == v1.15 **write-cycle-final** baseline (chip held image B; D-01 nuance). **Read path byte-identical — no regression on read.** |
| VPP rail (diagnostic) | `firestarter vpp` → stable **12.0–12.1V** (VPE 13.8V, VCC 5.5V). NOT the v1.15 VPP-high issue; rail is on-target. |
| **WRITE attempt 1** (`write -b`) | `write -b A` → **RC=1** `Failed to write memory, 0x000000, retries:20, bad bytes:921`; `write -b B` → RC=1 bad bytes:923. verify A/B RC=1. |
| **WRITE attempt 2** (reseat) | Operator reseated chip. `write -b A` → **RC=1, bad bytes:921 @0x000000** (byte-identical to attempt 1); `write -b B` → RC=1 bad bytes:923. **Reproducible — reseat ruled out contact.** |
| Post-fail chip state (N=3) | `consistency-check` → PASS, 1 distinct SHA = `ce12c20a1f8f64e575baa89c38157e0795b9774c4c0f7a5e949b9736bcb7b3c6` (partial/corrupt; first ~921 B did not program). Chip rewritable — recoverable once RCA'd. |
| Write-cycle SHA-match | ✗ chip holds `ce12c20a…`, NOT the v1.15 write-cycle-final baseline `e16b2a5b…`. |
| Negative control | `verify W27C512 img_A` → RC=1 ✓ (verify non-vacuous; confirms the fail is a real write failure, not a vacuous verify) |
| Evidence refs | `bench/W27C512-read/run_{01,02,03}.bin` (read PASS), `bench/W27C512-wcB/run_{01,02,03}.bin` (post-fail `ce12c20a` capture) |
| **Verdict** | **FAIL-INVESTIGATE (D-03).** Reproducible write-path failure on recompose firmware a296195 at a clean 12.0V rail. Read path clean. Candidate **P3 `vpp_check_window` recompose regression** (−402 B, biggest recompose change): W27C512 (0x07) is the ONLY of the 4 chips that exercises P3 on write; W29C020 (flash4, no P3) wrote clean. Failure at write-start (first ~921 B) is consistent with a VPP-gate engage/settle timing change at write-init. Row 0x07 NOT flipped to PASS. Needs RCA: diff a296195 `eprom_check_vpp`/`vpp_check_window` vs b10; consider reflash-b10 A/B test to confirm regression vs pre-existing. |

### Chip 3 — FM1608 (0x28 SRAM-STD / FRAM, 8192 B) — **PASS**

| Field | Value |
|-------|-------|
| Port identity | leonardo on `/dev/ttyACM0` (confirmed pre-op) |
| Shield | Rev 2.0 (operator silkscreen confirmed) |
| Operator authorize | Seated + authorized FM1608 live ops |
| **READ** (N=3, ran FIRST) | `consistency-check FM1608 --runs 3 --output-dir bench/FM1608-read/` → RC=0, **PASS, 1 distinct SHA** |
| Read SHA | `3c23e7fcbe88c5a09ab50cf8301e9adf884fcdd519b6f9fefc72583b34f75c90` |
| Read SHA-match | ✓ == v1.15 write-cycle-final baseline (chip held image B; D-01 nuance). Read path byte-identical. |
| **WRITE A→B** (`write -b`, FRAM method) | `write -b A` RC=0 (0.74s) → `verify A` RC=0 → `write -b B` RC=0 (0.75s) → `verify B` RC=0. B over A, no explicit erase (FRAM overwrite). |
| Post-B readback (N=3) | `consistency-check --runs 3 --output-dir bench/FM1608-wcB/` → RC=0, PASS, 1 distinct SHA = `3c23e7fcbe88c5a09ab50cf8301e9adf884fcdd519b6f9fefc72583b34f75c90` |
| Write-cycle SHA-match | ✓ == v1.15 write-cycle-final baseline `3c23e7fc…b34f75c90` |
| Negative control | `verify FM1608 img_A` → RC=1 ✓ (verify non-vacuous) |
| "Empty input" note | Not emitted — `-b` skips the blank-check, so the benign FRAM "Empty input" blank-check note (expected only on the default blank-check path) did not fire. Consistent with the FRAM exception. |
| Evidence refs | `bench/FM1608-read/run_{01,02,03}.bin`, `bench/FM1608-wcB/run_{01,02,03}.bin` |
| **Verdict** | **PASS** — read + write both byte-identical to v1.15 baseline. (No P3 — supports P3-isolated regression boundary for W27C512.) |

### Chip 4 — SST39SF040 (0x06 FLASH-AMD-ALT, flash3, 524288 B) — **FAIL-INVESTIGATE** (write path; read PASS)

| Field | Value |
|-------|-------|
| Port identity | leonardo on `/dev/ttyACM0` (confirmed pre-op + after reseat) |
| Shield | Rev 2.0 (operator silkscreen confirmed) |
| Operator authorize | Seated + authorized; reseat + 1 retry authorized |
| **READ** (N=3, ran FIRST) | `consistency-check SST39SF040 --runs 3 --output-dir bench/SST39SF040-read/` → RC=0, **PASS, 1 distinct SHA** |
| Read SHA | `a38b13b4d285756c1f385a75d0cdf89f72720764c21fd933ced75ebdd970b96b` |
| Read SHA-match | ✓ == v1.15 write-cycle-final baseline (chip held image B; D-01 nuance). **Read path byte-identical.** |
| **WRITE attempt 1** | `write -b A` → **RC=1 `Operation timed out`** (firmware-level, not bash); verify A RC=1; `write -b B` → RC=0 "successful (177.64s)" but **verify B RC=1**; chip held `ebca6266…` (not image B). |
| **WRITE attempt 2** (reseat) | Operator reseated. `write -b A` → **RC=1 `Operation timed out`** (same); `write -b B` → RC=0 "successful (177.70s)", **verify B RC=1**; chip held **`ebca626663a78613a7572b792e00de11472aaefa84b41539ec5f5cfae3533e0b`** — byte-identical to attempt 1. **Reproducible, deterministic.** |
| Post-fail chip state (N=3) | `consistency-check` → PASS, 1 distinct SHA = `ebca6266…3533e0b` (consistent but wrong; ≠ image B `a38b13b4…`). Chip rewritable. |
| Write-cycle SHA-match | ✗ chip holds `ebca6266…`, NOT v1.15 write-cycle-final baseline `a38b13b4…`. |
| Negative control | `verify SST39SF040 img_A` → RC=1 ✓ (verify non-vacuous) |
| Evidence refs | `bench/SST39SF040-read/run_{01,02,03}.bin` (read PASS), `bench/SST39SF040-wcB/run_{01,02,03}.bin` (post-fail `ebca6266` capture) |
| **Verdict** | **FAIL-INVESTIGATE (D-03).** Reproducible write-path failure on recompose a296195: write A times out, write B reports success but produces deterministically-wrong content. Read path clean. flash3 uses **P4/P7, NOT P3** — distinct symptom from W27C512, so the regression is NOT P3-isolated. Row 0x06 NOT flipped to PASS. |

---

## Session Summary — 2 PASS / 2 FAIL-INVESTIGATE

| Bucket | Chip | Read (N≥3 vs v1.15) | Write-cycle (vs v1.15) | Verdict |
|--------|------|---------------------|------------------------|---------|
| 0x05 FLASH-AMD-STD | W29C020 | ✓ `47304933…` | ✓ `47304933…` (auto-erase proven) | **PASS** |
| 0x06 FLASH-AMD-ALT | SST39SF040 | ✓ `a38b13b4…` | ✗ `ebca6266…` (write A timeout, write B wrong) | **FAIL-INVESTIGATE** |
| 0x07 EPROM-STD | W27C512 | ✓ `e16b2a5b…` | ✗ `ce12c20a…` (bad bytes @0x0, write-start) | **FAIL-INVESTIGATE** |
| 0x28 SRAM-STD | FM1608 | ✓ `3c23e7fc…` | ✓ `3c23e7fc…` | **PASS** |

**All 4 READ paths byte-identical to v1.15 baseline.** **2 of 4 WRITE paths fail reproducibly.**

### RCA scope (handed to follow-up; NOT resolved in this bench session)
- **Failure axis:** the two **12V-VPP-listed flash/EPROM** write paths (0x06 flash3, 0x07 EPROM-STD) fail; the two **5V/no-VPP** paths (0x05 flash4 auto-erase-at-5V, 0x28 SRAM) pass. Reads (no VPP) all pass. ⇒ the regression is in the **VPP-gated / 12V write path**, with two distinct symptoms (W27C512 bad-bytes-at-start; SST39SF040 write-A-timeout + wrong-content).
- **Primitive map:** P3 `vpp_check_window` (−402 B, biggest recompose change) is used by 0x07; flash3 (0x06) is mapped to P4/P7 only — so a single-primitive (P3-only) explanation does not cover both. Examine the recompose's VPP-application/ timing path for 12V writes across `eprom.cpp` (`eprom_check_vpp`) and `flash_type_3.cpp`.
- **Host vs firmware:** firmware-under-test = `firestarter@a296195`; **host = `firestarter_app@e46549f`** (also a v1.16 build, NOT the v1.15 host `98b3a92`). Failure could be fw OR host. Recommended controlled A/B: reflash b10 fw (or check out v1.15 host) and re-run W27C512/SST39SF040 to confirm recompose-causality vs pre-existing.
- **Recoverability:** both failing chips are rewritable; they currently hold partial/wrong content (`ce12c20a` / `ebca6266`) and can be restored once the write path is fixed.
- **Disposition:** LEDGER-02 (each on-hand protocol → PASS) is **NOT satisfied for 0x06 and 0x07**. Operator/verifier decision required on milestone disposition (carry as defect rows vs pause for fw/host fix).





---

## Phase 91 A/B + Fix Results — 2026-06-26 (RCA + FIX-91)

**The Phase-90 0x06/0x07 "12V-VPP write-path regression" was a TEST-METHOD error, not a
firmware/host regression.** `firestarter write -b` sets `FLAG_SKIP_ERASE` (its `--no-blank-check`
help reads "…and skip erase"). flash3 (SST39SF040) and the EEPROM-class W27C512 are
electrically-erasable parts that REQUIRE an erase before write; with `-b` the erase is skipped, so
bytes needing 0→1 transitions cannot be programmed.

### Forensic (SST39SF040, on-chip `ebca6266` capture vs image B)
- 524285 / 524288 bytes match image B (99.9994%); only 3 bytes differ, all @0x0–0x2, all
  `== imgA & imgB` — the NOR incomplete-/skipped-erase signature. The per-byte DQ7 poll
  (`& 0x80`) matched on bit 7, so the firmware reported "write successful"; only full verify caught
  `0x1c != 0x04 @0x0`.

### A/B (controlled, Leonardo + Rev 2.0, image B)
| Leg | Firmware | `write -b` imgB | Verdict |
|-----|----------|-----------------|---------|
| recompose | a296195 (25136 B) | write RC=0; verify RC=1 `0x1c != 0x04 @0x0` | FAIL (erase skipped) |
| b10 baseline | a1953c2 (25654 B, avrdude-verified) | write RC=0; verify RC=1 `0x1c != 0x04 @0x0` | FAIL — **identical** → recompose innocent |

### FIX (SST39SF040, stock recompose a296195 — NO firmware edit)
Erase-enabled plain `firestarter write` (writeA→verifyA→writeB→verifyB→consistency-check N=3):
- writeA RC=0 (240 s) / verifyA RC=0 (erase proof) → writeB RC=0 (240 s) / verifyB RC=0 →
  consistency-check N=3 **PASS, 1 distinct SHA = `a38b13b4…970b96b`** (== v1.15 gate); neg-control
  verify(imgA) RC=1. Evidence: `bench/SST39SF040-fix/SHA256SUMS.txt`.
- An exploratory firmware erase-delay bump (105→500 ms) was tried and **reverted** — silicon proved
  the erase was *skipped*, not slow. Firmware byte-identical to a296195; SAFE-04 (`vpp_check_window`
  +500 mV) intact.

### Disposition
- **0x06 SST39SF040 → PASS** (erase-enabled write, oracle leonardo+Rev2.0, evidence
  `bench/SST39SF040-fix/`). LEDGER-02 satisfied for 0x06.
- **0x07 W27C512 → bench-pending** (same root cause; fix = plain `write`; live re-bench DEFERRED to
  operator — chip swap). See `rca/W27C512-OPERATOR-CHECKLIST.md`.

### W27C512 (0x07) — operator-return bench (2026-06-26)
Operator swapped in the W27C512; chip-ID check **PASSED** (0xDA08). Erase-enabled plain `firestarter
write` (NO `-b`): writeA RC=0 (22.85 s) / verifyA RC=0 → writeB RC=0 / verifyB RC=0 →
consistency-check N=3 **PASS, 1 distinct SHA = `e16b2a5b…`** (== v1.15 gate); neg-control
verify(imgA) RC=1; no VPP-high guard fired. **0x07 → PASS** — confirms the SAME root cause/fix as
0x06 (`write -b` skipped the required erase). Evidence: `bench/W27C512-fix/`. **All 4 on-hand
protocols now PASS (0x05, 0x06, 0x07, 0x28) — LEDGER-02 fully satisfied.**
