# v1.15 Bench Evidence — Phase 81 Non-Destructive Read Sweep

**Harness version:** 81 · **Board:** leonardo · **Shield:** Rev 2.0 · **Generated:** 2026-06-23/24

## SAFE-01 Preconditions (verified per task)

- **Board:** leonardo (the only authoritative read board) · **Port:** /dev/ttyACM0 · **Firmware:** 3.0.0b8
- **Shield:** Rev 2.0 — operator-confirmed silkscreen (EEPROM hw byte reports "Rev 2.0-class", cannot distinguish revs)
- **Calibration:** R1=270000, R2=44000 (not the 1000 default)
- **Host suite:** green (Plan 81-01, 651 tests)
- **Negative control (EVID-03):** FIRED — wrong-file `verify` exited RC=1 on W27C512 (Task 1) and ST M27C512 (Task 2)
- **Non-destructive:** reads apply NO VPP — **zero chips consumed**

### Phase 82 SAFE-02 Gate (recorded Plan 82-01, 2026-06-24)

- **`ruff check` (files added by 82-01):** PASS — `tools/gen_test_image.py`, `tests/test_gen_test_image.py` ruff-clean (pre-existing I001 errors in unrelated tools unchanged)
- **`ruff format --check` (files added by 82-01):** PASS — both new files already formatted
- **Full host suite:** PASS — **663 tests** (651 + 12 new gen_test_image pinning tests), 29 snapshots
- **0xA4 guard `test_init_phase_data_frames_not_acked`:** PASS (1/1 — SAFE-02 ack_data=False guard green)
- **Python:** 3.12.13 (devcontainer); CI targets py3.9/3.11 — new files use no 3.9-incompatible syntax

### Phase 82 SAFE-01 Gate — Plan 82-02 write session (operator sign-off 2026-06-24)

- **`controller:`** leonardo on **/dev/ttyACM0** (firmware `firestarter fw`), firmware 3.0.0b8
- **Shield:** Rev 2.0 — **operator-confirmed silkscreen** this session ("Rev 2.0 — start now"); fw byte reports "Rev 2.0-class" (cannot distinguish revs, per policy)
- **Calibration (live readback):** R1=270000, R2=44000 (NOT the 1000 default → VPP read trustworthy)
- **SAFE-02:** green (Plan 82-01 — 663 tests + 0xA4 guard `test_init_phase_data_frames_not_acked` PASS)
- **Authorization:** destructive A→B write session cleared; chips seated one at a time on Leonardo + Rev 2.0

### Phase 83 SAFE-02 Gate (recorded Plan 83-01, 2026-06-24)

- **0xA4 guard `test_init_phase_data_frames_not_acked`:** PASS (1/1 — SAFE-02 `ack_data=False` guard green)
- **Full host suite:** PASS — **663 tests** (unchanged from Phase 82; no source/test files modified this plan), 29 snapshots
- **`ruff check firestarter/ tests/` (CI-authoritative scope):** PASS — `All checks passed!` (RC=0)
- **`ruff format --check firestarter/ tests/` (CI-authoritative scope):** PASS — 73 files already formatted (RC=0)
- **Broad `ruff check .` / `ruff format --check .`:** reports 4 pre-existing `tools/`-tree findings (`tools/audit_coverage_matrix.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py` I001/UP031; `+ .github/scripts/update_version.py`, `tools/check_mypy_watermark.py` format) — **FLAGGED as out-of-CI-scope, NOT masked**: `ci.yml` gates ruff over `firestarter/ tests/` only (`.github/workflows/ci.yml:60,63`), which is green. These are NOT introduced by this plan (zero source changes) and match the Phase 82 "pre-existing I001 errors in unrelated tools unchanged" note. Not a py3.12-vs-CI version discrepancy — purely a path-scope difference between `ruff check .` and the CI gate.
- **Python:** 3.12.13 (devcontainer); CI targets py3.9/3.11 — no source touched, so no new version-sensitive surface introduced
- **Verdict:** SAFE-02 GREEN — bench session (Plans 02/03) may open on the CI-authoritative gate.

### Phase 82 SAFE-01 Gate — Plan 82-03 flash4 write session (operator sign-off 2026-06-24)

- **`controller:`** leonardo on **/dev/ttyACM0** (re-verified `firestarter fw` for this session — no USB replug since 82-02), firmware 3.0.0b8
- **Shield:** Rev 2.0 — **operator-re-confirmed silkscreen** this flash4 session
- **Calibration (live readback):** R1=270000, R2=44000 (not the 1000 default)
- **SAFE-02:** green (Plan 82-01 — unchanged since 82-02)
- **DB-01 decode (firestarter info):** W29C040 = 32-pin / 0x80000 (524288) / Flash/EEPROM / 12V / 0x05; W29C020 = 32-pin / 0x40000 (262144) / Flash/EEPROM / 12V / 0x05

## Sweep Result — 10 PASS / 1 ANOMALY

| # | Chip | Family / Algorithm | Board+Shield | Op | Blank-state | Read N | SHA-256 | Verdict | Anomalies |
|---|------|--------------------|--------------|----|-------------|--------|---------|---------|-----------|
| 1 | W27C512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `9376dcd81713…97ad23c8` | **PASS** | VPP-high read refusal (~18.8V) cleared by board reset before this read; negative-control verify exited RC=1 |
| 2 | W27E512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `71189f7fb6ae…48da9063` | **PASS** | none |
| 3 | SST27SF512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `f633b2f5c06c…f8056360` | **PASS** | none |
| 4 | W27E040 | 0x08 (EPROM_QUICK / EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `67f70ccdae30…468b4254` | **PASS** | none |
| 5 | SST39SF040 | 0x06 (FLASH_AMD_ALT / Flash) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `c19c3e07b94b…a348368d` | **PASS** | none |
| 6 | W29C020 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `93ff5287b7e6…66b53602` | **PASS** | none |
| 7 | W29C040 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `d44736a9c4fa…1e3b48b3` | **PASS** | none |
| 8 | FM1608 | 0x40 (SRAM_STD / FRAM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `2ef1444bc950…3d4c0037` | **PASS** | blank-check 'Empty input' on FRAM (0x40) — read N=3 identical, flag for Phase 84 FIX-01 review (blank-check tooling gap, not a read fault) |
| 9 | ST M27C512 | 0x07 (EPROM_STD / UV-EPROM) | leonardo Rev 2.0 | read+blank_check | BLANK | 3 | `71189f7fb6ae…48da9063` | **PASS** | benign VPP-low warning 11.9V<13.0V on read (non-blocking; reads apply no VPP); negative-control verify RC=1 |
| 10 | AM27C020 | 0x08 (EPROM_QUICK / UV-EPROM) | leonardo Rev 2.0 | read+blank_check | NOT-BLANK | 3 | `08b687a3d711…177ed496` | **PASS** | none |
| 11 | 2516 | 0x0B (EPROM_LEGACY / UV-EPROM, NMOS) | leonardo Rev 2.0 | read+blank_check | NOT-BLANK | 3 | `—` | **ANOMALY** | READ UNSTABLE: 3 distinct SHAs across N=3 on initial + 2 reseat cycles (D-07 exhausted). VPP pinned 15.3V<25.0V on shared OE/VPP pin during read (0x0B Legacy path) — same VPP-regulator instability family as chip-1 18.8V boot refusal. Signature is 0x0B-specific (all 0x07/0x08 UV chips read clean on this bench). GATES Phase 83 (no 2516 write/preserve until read path stable). Flag Phase 84 FIX-01. |

## UV-EPROM Gating Blank-States (the Phase 83 gate)

| UV Chip | Gating blank-state | Notes |
|---------|--------------------|-------|
| ST M27C512 | **BLANK** | stable all-0xFF, N=3 byte-identical |
| AM27C020 | **NOT-BLANK** | data present (0x02@0x0000), N=3 byte-identical |
| 2516 | **NOT-BLANK** (read-unstable) | blank-check deterministically not-blank; reads jitter (3 SHAs) — exact contents unreliable |

## ⚠ Phase 83 Gate / Phase 84 FIX-01

The **2516** (0x0B Legacy, shared OE/VPP pin) read is **UNSTABLE** — 3 distinct SHAs across the initial read + 2 reseat cycles (D-07 exhausted), with VPP pinned at 15.3V on the shared OE/VPP pin. Every 0x07/0x08 UV chip read clean on this same bench, so the signature is **0x0B-specific**, not seating. This is the same VPP-regulator-instability family as the chip-1 boot refusal (VPP 18.8V>12V, cleared by reset).

- **Phase 83:** MUST NOT write or preserve-dump the irreplaceable 2516 until its read path is stable (blank-state/contents cannot be trusted).
- **Phase 84 FIX-01:** investigate the 0x0B read-path VPP control + the FM1608 blank-check "Empty input" tooling gap.

---

## Phase 82 — Rewritable A→B Write Validation

**Protocol (D-05/D-06):** For each of the 8 electrically-rewritable chips, write image A (seed=1,
full-size deterministic pseudo-random), verify A; then write image B (seed=2, same size) **without
an explicit erase step**, verify B. A clean B SHA-256 match proves auto-erase fired. Images generated
by `tools/gen_test_image.py`; stored at `/tmp/firestarter_bench_p82/<chip>_img_{A,B}.bin`.

**Known risk:** W29C020 (256KB flash4) carries **cr01_risk=yes** — `flash4_page_size(262144)` guesses
128B but the real datasheet page is 256B. A mid-page-poll write failure is pre-attributed to CR-01
and handed to Phase 84 FIX-01; it is NOT a surprise failure if it occurs.

**Verdict key:** `PASS` / `FAIL (CR-01)` / `FAIL (genuine)` / `ANOMALY`

| # | Chip | Family / Algorithm | Board+Shield | Op | Blank-state | SHA-256 (image B read-back) | Verdict | seed_A | sha256_image_A | seed_B | sha256_image_B | cr01_risk | Anomalies |
|---|------|--------------------|--------------|-------|-------------|------------------------------|---------|--------|----------------|--------|----------------|-----------|-----------|
| 1 | W27C512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `e16b2a5b…dc326ab5` | **PASS** | 1 | `604d9570…1645d637` | 2 | `e16b2a5b…dc326ab5` | none | Auto-erase proven (clean B over A, no explicit erase); consistency-check N=3 1-distinct-SHA; neg-control verify(A) RC=1. Initial attempt hit VPP-high 13.1V>12.0V (Phase-81 VPP-regulator family) — operator corrected VPP, clean retry. DB-01: DIP28_27512/EEPROM/12V/65536 confirmed vs silicon. |
| 2 | W27E512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `—…—` | **FAIL (genuine)** | 1 | `604d9570…1645d637` | 2 | `e16b2a5b…dc326ab5` | none | FAIL (genuine): erase cannot clear bit 7 @0x3d (reads 0x7f, want 0xFF) — DETERMINISTIC across initial run + 2 reseats (D-08 N=2 exhausted), identical offset/value every time = stuck cell, not contact/VPP. First session: write-cycle A RC=0 then write-cycle B erase failed + read jittered 14/65536 bytes (0xEF↔0xFF); both retries failed at erase-A. Chip read clean in Phase 81 (read-only) — defect manifests only on erase/write. DB-01 DIP28_27512/EEPROM/12V/65536 confirmed (write path engaged correctly; genuine silicon wear, not DB/algo mismatch). neg-control verify(A) RC=1. REWR-01 partial. |
| 3 | SST27SF512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `e16b2a5b…dc326ab5` | **PASS** | 1 | `604d9570…1645d637` | 2 | `e16b2a5b…dc326ab5` | none | Auto-erase proven (clean B over A, no explicit erase); consistency-check N=3 1-distinct-SHA == image B; neg-control verify(A) RC=1. No VPP hiccup. DB-01: DIP28_27512/EEPROM/12V/65536 confirmed vs silicon. |
| 4 | W27E040 | 0x08 (EPROM_QUICK / EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `—…—` | **FAIL (genuine)** | 1 | `77a771b2…f1662bbd` | 2 | `a38b13b4…d970b96b` | none | FAIL (genuine): erase cannot clear bit 4 @0x7db (reads 0xef, want 0xFF) — DETERMINISTIC across initial run + 1 reseat (same offset/value), genuine stuck cell. Same stuck-bit-on-erase signature class as W27E512 (different offset). Chip read clean in Phase 81 (read-only); defect manifests only on erase/write. DB-01 DIP32_STD/EEPROM/12V/524288 confirmed (write path engaged at correct params; genuine silicon wear, not DB/algo). REWR-02 partial. |
| 5 | SST39SF040 | 0x06 (FLASH_AMD_ALT / Flash) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `a38b13b4…d970b96b` | **PASS** | 1 | `77a771b2…f1662bbd` | 2 | `a38b13b4…d970b96b` | none | Auto-erase proven (clean B over A, no explicit erase); flash3 slow path ~240s/write; consistency-check N=3 1-distinct-SHA == image B; neg-control verify(A) RC=1. DB-01: pinout DIP32_SST39SF040 / 12V / 524288 confirmed vs silicon. DB-01 NOTE for Phase 84: DB electrical.type reads 'Flash/EEPROM' while milestone classes this as 0x06 flash3/Flash — observation, not a blocker; no inline DB edit. |
| 6 | FM1608 | 0x40 (SRAM_STD / FRAM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `3c23e7fc…34f75c90` | **PASS** | 1 | `a89c4b45…8ce5415d` | 2 | `3c23e7fc…34f75c90` | none | Overwrite proof, no erase (D-06): clean B read-back SHA == image B confirms B fully replaced A. Used DIRECT write path (write -b) — 'dev write-cycle' unusable on FRAM (erase 'Not supported'; same Phase-81 erase/blank-check tooling gap, flag Phase 84 FIX-01, NOT fixed here). write A/verify A RC=0, write B/verify B RC=0, consistency-check N=3 1-distinct-SHA == image B, neg-control verify(A) RC=1. DB-01: pinout DIP28_JEDEC_SRAM_8K / 8192 confirmed vs silicon; NOTE for Phase 84 — DB electrical.type 'SRAM' vs FRAM family (observation, no inline DB edit). |
| 7 | W29C040 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `—…—` | **FAIL (genuine)** | 1 | `77a771b2…f1662bbd` | 2 | `a38b13b4…d970b96b` | none | FAIL (genuine, flash4 page-write): write A (-b) times out verifying byte @0x0000ff (256B page-0 boundary), reads 0x00 (page not auto-erased/programmed) — DETERMINISTIC across initial + 1 reseat (same offset/byte). Per-page auto-erase NOT confirmed → REWR-04 SC#3 NOT met on silicon. FW FLASHED b8→b10 THIS SESSION (operator-authorized deviation) to get the Phase-74 W29C040 SDP/256B-page fix; standalone erase is a 0.06s no-op on both b8 and b10 (chip stays 0x00). KEY: this is the FIRST real-silicon test of the Phase-74 fix — Phase-74 Wave-2 (W29C040 re-bench) was DEFERRED, so the fix was only native-test-verified. Reopens Phase-74 Wave-2 / hands to Phase 84 FIX-01. Distinct from the W29C020 CR-01 128-vs-256 under-sizing. DB-01: DIP32/Flash-EEPROM/12V/524288 decode confirmed vs silicon (info read clean; failure is write-path, not decode). |
| 8 | W29C020 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | leonardo Rev 2.0 | write_A+verify_A → write_B+verify_B | n/a — A→B | `47304933…c11ce58c` | **PASS** | 1 | `b2fc5cbf…0a133457` | 2 | `47304933…c11ce58c` | no (CR-01 did NOT manifest) | PASS — A→B auto-erase proven for the Flash/EEPROM type (write B over A, no explicit erase, clean B verify): THIS is the REWR-04 SC#3 silicon confirmation of the FLAG_CAN_ERASE Flash/EEPROM branch (landed on W29C020, not W29C040). Direct write -b path (write-cycle blank-checks; flash4 has no real bulk-erase — per-page auto-erase on write). write A/verify A RC=0, write B/verify B RC=0, consistency-check N=3 1-distinct-SHA == image B, neg-control verify(A) RC=1. CR-01 (flash4_page_size 128-vs-256 under-sizing) did NOT manifest on b10 — 256B page handling was correct here. FW b10 (flashed this session). DB-01: DIP32/Flash-EEPROM/12V/262144 decode confirmed vs silicon. NB: contrast W29C040 (512KB) FAIL — reopen Phase-74 Wave-2 in Phase 84. |

---

## Phase 83 — UV-EPROM Write Proof (gated on Phase 81 blank-state)

**Scope (D-01/D-02):** This phase covers **ONLY the 2 read-stable UV-EPROM chips** —
**ST M27C512** (0x07, BLANK) and **AM27C020** (0x08, NOT-BLANK). Board = **Leonardo + RURP
Rev 2.0 ONLY** (SAFE-01/D-09). Every UV write is **irreversible** (operator has no eraser) →
non-destructive-first (UV-01): the Phase 81 blank-state is re-confirmed and the operator
authorizes the spend **at the bench** before any VPP is applied (D-04). Default lean = **SPEND**
the 2 commodity parts (D-03), but the explicit per-chip spend-vs-preserve call stays a live
bench decision.

**2516 → Phase 84 deferral (D-01 — IMPORTANT, narrows the roadmap scope):** the entire **2516**
is **OUT of Phase 83** — **no write, no preserve-dump, no re-read** in this phase. Its read was
ANOMALOUS in Phase 81 (3 distinct SHAs / N=3 + 2 reseats, VPP pinned 15.3V<25V on the shared
OE/VPP pin, 0x0B-specific). Writing/dumping the **irreplaceable** 2516 on an untrusted read path
would consume it for a **vacuous** PASS (EVID-03). Therefore **GRAD-03** (2516 VPE-rail write
proof), **SC#4** (2516 bench-proven), and the **FUT-03** close all move to **Phase 84**,
contingent on **Phase 84 FIX-01** root-causing and fixing the 0x0B read-path VPP instability so
the read oracle becomes trustworthy.

**Pre-recorded Phase 84 PASS bar for the 2516 (D-08 — inherited without re-discussion):** when
the 2516 write proof runs in Phase 84 (after FIX-01 stabilizes its read), the PASS bar is a clean
**read-back SHA match** on the spent image (after a stabilized N≥3 read); the firmware
**under-voltage warning** (~22.4V VPE < 25V NMOS spec) is captured **verbatim** and the result
recorded **best-effort** (per v1.14 D-07). **Over-voltage stays blocked throughout** (SC#5).
Achieving this closes FUT-03 (best-effort).

**Write-proof method per blank-state (UV-03):**
- **ST M27C512 (BLANK) → full known image (D-05):** spend = write a full-chip 64KB deterministic
  pseudo-random image, verify read-back **SHA == image SHA**. Strongest proof (every address line
  + bit pattern exercised). Image via `tools/gen_test_image.py` (size_bytes=65536, seed=1).
- **AM27C020 (NOT-BLANK) → all-`0x00` full wipe (D-06):** spend = write all-`0x00` over the entire
  `0x40000` (262144 B) chip (proves every currently-`1` bit can be driven `1→0` — the only legal
  transition on a UV part without erase), verify read-back **SHA == SHA(all-`0x00`)**.

**Verify oracle (D-07/D-13, non-vacuous EVID-03):** read-back SHA match on the trusted Leonardo
read, N≥3 byte-identical, plus a negative control (a wrong-file `verify` exits non-zero). Both
chips read stably in Phase 81 → their write proofs CAN be SHA-verified.

**Write-failure disposition (D-14):** reseat + retry up to N=2, then record FAIL (genuine defect)
or ANOMALY and CONTINUE; genuine defects flagged for Phase 84 FIX-01, not root-caused inline. A
UV part once spent cannot be re-blanked — a "retry" re-writes the same all-`0x00`/image
(idempotent for these proofs).

**Image SHA oracles (recorded Plan 83-01, 2026-06-24; reuse-first, EVID-02 — no new module/dep):**

| Chip | Image file (`/tmp/firestarter_bench_p83/`) | Size (bytes) | Generator | SHA-256 oracle |
|------|--------------------------------------------|--------------|-----------|----------------|
| ST M27C512 | `ST_M27C512_img.bin` | 65536 (0x10000) | `tools/gen_test_image.py 65536 1` (seed=1, deterministic — reproducible) | `604d957094f7cb1f98f50d7408f64e7720e5ae5d4acab8d1047a9a081645d637` |
| AM27C020 | `AM27C020_zeros.bin` | 262144 (0x40000) | direct byte-write of 262144 × `0x00` (NOT gen_test_image; D-06) | `8a39d2abd3999ab73c34db2476849cddf303ce389b35826850f9a700589b4a90` |

> The AM27C020 oracle equals `sha256(b"\x00" * 262144)` (verified independently). The ST M27C512
> oracle is reproducible: re-running `python tools/gen_test_image.py 65536 1 <path>` prints the
> identical digest. (NB: it also matches the Phase 82 seed=1/65536 "image A" SHA `604d9570…1645d637`
> — same generator, size, and seed.)

**Write-proof results (filled at the bench in Plans 02/03 — empty until the spend session opens):**

| # | Chip | Family / Algorithm | Board+Shield | Blank-state | Spend-vs-preserve decision | Op | Image SHA | Read-back SHA | Read N | Verdict | Anomalies |
|---|------|--------------------|--------------|-------------|----------------------------|----|-----------|---------------|--------|---------|-----------|
| 1 | ST M27C512 (CLI name `M27C512`, ST/SGS-THOMSON, chip-id 0x203D) | 0x07 (EPROM_STD / UV-EPROM) | leonardo Rev 2.0 /dev/ttyACM0, r1=270000 | BLANK re-confirmed 2026-06-24 (all-0xFF, read-back SHA `71189f7f…48da9063` == Phase 81; `blank` RC=0) | **SPEND (partial, operator-directed)** | write 16 B @0x0000 → `verify -a 0x0000` | payload `f705354e…873897a` (16 B `4420823cfde6f1c26b30f90ec7dd01e4` = first 16 B of seed=1 image) | `008948af…ec397c3f` (full-chip post-write: first 16 B = payload, rest 0xFF) | 3 (1 distinct SHA) | **PASS** | DEVIATION from D-05 (full-image): operator authorized a minimal 16-byte partial-spend so the part stays mostly blank/reusable. write RC=0, `verify`(written 16 B) RC=0, neg-control wrong-file `verify -a` RC=1 (`0x00 != 0x44 @0x000000`), N=3 byte-identical. UV-04 decode UV-EPROM/13V/65536/0x07 confirmed (DB VPP 13V, not the plan's stated 12V). Standard 0x07 VPP path, no over-voltage. "ST M27C512" is a human label; resolving DB name is `M27C512`. |
| 2 | AM27C020 (AMD, DIP32, chip-id 0x197) | 0x08 (Large EPROM / UV-EPROM) | leonardo Rev 2.0 /dev/ttyACM0, r1=270000, JP4 closed (32-pin) | NOT-BLANK re-confirmed 2026-06-24 (data 0x02@0x0000, read SHA `08b687a3…177ed496` == Phase 81; `blank` RC=1) | **SPEND (partial, operator-directed)** | write 16 B `0x00` @0x0000 (`-b`) → FAILED | payload `374708ff…28ec37bb` (16 B all-`0x00`) | N/A — write did not program | 3 (2 distinct SHAs) | **ANOMALY** | D-14 retry budget exhausted (initial + 2 retries, JP4 closed): `write` deterministically fails `bad bytes 15/16, retries 20` at 0x000000, **0 bits programmed** (read-back unchanged at 0x02), so chip silicon intact — NOT a write success and NOT chip wear; signature = the **0x08 (32-pin Large EPROM) write/VPP path on this bench** (the 0x07 28-pin part wrote clean on the same bench this session). ALSO mild **read instability**: 2 of 3 N=3 reads byte-identical, the 3rd had a localized 12-byte glitch reading `0x00` at 0x008004–0x00800f (distinct from the chip's clean Phase 81 read). Negative-control `verify -a 0x0000` RC=1 (`0x00 != 0x02 @0x000000`, confirms no programming). UV-04 decode UV-EPROM/13V/262144/0x08/DIP32 confirmed (DB VPP 13V, not the plan's 12V). Over-voltage stayed blocked. **Flag Phase 84 FIX-01** (0x08 write/VPP path + intermittent read). |
| — | 2516 | 0x0B (EPROM_LEGACY / UV-EPROM, NMOS) | — | NOT-BLANK, READ-UNSTABLE | **DEFERRED → Phase 84** (D-01) | — no write / no preserve-dump / no re-read in Phase 83 — | — | — | — | **DEFERRED** | GRAD-03 / SC#4 / FUT-03 move to Phase 84 (after FIX-01 stabilizes the 0x0B read); D-08 PASS bar pre-recorded above |

**GRAD-03 / 2516 → Phase 84 (Task 3 handoff record):** The entire 2516 is OUT of Phase 83 — no
write, no preserve-dump, no re-read (D-01). **GRAD-03** (2516 VPE-rail write proof), **SC#4** (2516
bench-proven), and the **FUT-03** close are reassigned to **Phase 84**, contingent on **Phase 84
FIX-01** stabilizing the 0x0B read-path VPP instability. The **D-08 Phase-84 PASS bar** is
pre-recorded in the section header above (clean read-back SHA on a stabilized N≥3 read = PASS;
firmware under-voltage warning ~22.4V VPE < 25V captured verbatim, best-effort per v1.14 D-07;
over-voltage stays blocked). REQUIREMENTS.md GRAD-03/FUT-03 rows + ROADMAP Phase 83 reflect the
reassignment. **No 2516 chip was selected, seated, or written anywhere in Phase 83.**

**AM27C020 ANOMALY → Phase 84 FIX-01 (additional handoff):** independent of the 2516/0x0B item,
the AM27C020 (0x08, 32-pin Large EPROM) write path takes **no programming** on this bench (0 bits
programmed; deterministic) while the 0x07 28-pin part wrote clean the same session — plus an
intermittent localized read glitch. Recorded as an ANOMALY (not chip wear, chip silicon intact)
and flagged for **Phase 84 FIX-01** alongside the 0x0B read-path investigation.

---

## Phase 84 — FIX-01 Re-bench (VPP-skip re-flash + 2516 re-read + 0x08/flash4 RCA-and-defer)

**Session date:** 2026-06-25 · **Board:** leonardo · **Shield:** Rev 2.0 (operator-confirmed silkscreen) · **Port:** /dev/ttyACM0 (USB by-id `usb-Arduino_LLC_Arduino_Leonardo-if00`)

### Phase 84 SAFE-01/02 Gate

- **`controller:`** leonardo on **/dev/ttyACM0**; hw byte reports "Rev 2.0-class"; **operator-confirmed silkscreen = Rev 2.0** (D-50 — EEPROM hw byte cannot distinguish revs; operator stated silkscreen directly).
- **Calibration (live readback):** R1=270000, R2=44000 (NOT the 1000 default → VPP trustworthy).
- **Firmware re-flash:** Leonardo re-flashed with the Phase-84 VPP-skip build via `pio run -t upload -e leonardo` from the `firestarter` submodule at commit `cb947c7` (branch `v1.15-bench-validation-of-operator-inventory`). avrdude wrote + verified **25666 bytes**; Leonardo flash **89.5%** (confirmed ≤90%, per 84-01).
- **VERSION STRING CAVEAT (record explicitly):** the firmware VERSION STRING still reports `3.0.0b10` — Plan 84-01 did NOT bump `FIRMWARE_VERSION`; the VPP-skip is a **behavioral source change**. The board carries the freshly-compiled v1.15-branch build, NOT the stock b10 release. Behavioral proof = Task 2 below (the Phase-81 ~18.8V boot-refusal is cleared after this re-flash).
- **SAFE-02 host gate GREEN:** full host suite PASSED (29 snapshots passed); 0xA4 guard `test_init_phase_data_frames_not_acked` PASS; `ruff check firestarter/ tests/` clean; `ruff format --check` clean (73 files).

### Task 2: 2516 (0x0B) Re-read — READ ONLY, N=3 (D-20/D-21)

**Method:** `firestarter dev consistency-check 2516 --runs 3` (N≥3 read oracle, EVID-02 reuse).
**HARD RULE D-21:** no write / no preserve-dump performed on the irreplaceable 2516.

**Run results:**

| Run | SHA-256 | Size | Duration |
|-----|---------|------|----------|
| 1 | `fee34d5ac3739fce151ade718450d9aa054a2da773d390d7494ef51d81015edd` | 2048 B | 4.15s |
| 2 | `9e9134a1c060cbb005a11d229dff1dde063914992b4e7f52ca81b72344dbef0a` | 2048 B | 3.94s |
| 3 | `506b43503e7f135dce969a56a5c47e095e3ea6c24a5d0fb86ddf0707cf70f432` | 2048 B | 4.02s |

**Stability verdict: FAIL (still unstable)** — 3 distinct SHAs across N=3 reads. First divergence at offset `0x005F` (run1=`0x1A`, run2=`0x18`); **39/2048 bytes (1.9%) divergent**. First 10 divergent offsets: `0x005F`, `0x013C`, `0x015D`, `0x01FD`, `0x01FF`, `0x0219`, `0x0259`, `0x0264`, `0x0280`, `0x02F5`.

**Blank-check result:** `firestarter blank 2516` → **NOT BLANK** (Not blank, at 0x000000, v: 0x68).

**Decode vs DB (`firestarter info 2516`):** UV-EPROM / DIP24 / 0x800 (2048 B) / VPP 25.0V / "Can be erased: no (UV erase only)" / INTEL — **CONFIRMED matches the user-override entry** (algorithm 0x0B, DIP24_2716, UV-EPROM, vpp_mv 25000, 2048 B).

**VPP-skip effect (explicit record):** the Phase-81 ~18.8V boot-refusal is **GONE** — all 3 reads + the blank-check completed with NO VPP refusal/error. In Phase 81 the read was VPP-refused / VPP pinned at 15.3V on the shared OE/VPP pin. The VPP-skip cleared the refusal. **BUT the data still jitters** → the read instability is NOT solely VPP-gated; it persists after the VPP-skip.

**No write / No preserve-dump (D-21 confirmed):** Zero writes or dumps to the 2516 occurred in this session. **GRAD-03 / SC#4 / FUT-03 stay DEFERRED best-effort (D-22)** regardless of read stability. A still-unstable read is the EXPECTED trigger for the clean FUT-03 deferral.

### Task 3a: AM27C020 (0x08, 32-pin Large EPROM) Re-bench (RCA-and-defer, N=2 per D-54)

**Decode (`firestarter info AM27C020`):** UV-EPROM / DIP32 / 0x40000 (262144 B) / VPP 13.0V / chip-id 0x197 — matches Phase 83.

**Write attempt (16×0x00 @0x0000, `-b` flag; AM27C020 already NOT-BLANK/spent so idempotent):**

| Attempt | Result |
|---------|--------|
| 1 | ERROR "Failed to write memory, 0x000000, retries: 20, bad bytes: 15" |
| 2 | Identical (bad bytes 15/16) |

**Negative control `verify -a 0x0000` (zeros16):** ERROR "0x00 != 0x02 at 0x000000" — confirms **0 bits programmed**; chip still reads 0x02 (silicon intact, unchanged from Phase 81/83 baseline).

**Verdict: FAIL — 0-bits-programmed CONFIRMED on silicon (deterministic, N=2 exhausted).** NOT VPP-skip-related (the VPP-skip gates read/blank-check only; the write path is unchanged — T-84-14). The 0x08 32-pin Large-EPROM write/VPP path on this bench is the defect signature (the 0x07 28-pin part wrote clean same bench in Phase 83). NOT a trivial fix.

**Disposition: DEFERRED — FUT-06:** "AM27C020 / 0x08 32-pin Large-EPROM write-path takes 0 bits on Leonardo+Rev2.0; not VPP-skip-related; chip silicon intact." Unblock = root-cause the 0x08 32-pin write/VPP path (JP4/P1-as-VPP routing, firmware `eprom_write_execute` 0x08 branch vs 0x07) on the same board + shield + calibration.

### Task 3c: W29C040 (0x05 flash4, 512KB) Re-bench (RCA-and-defer, N=2 per D-54)

**Decode (`firestarter info W29C040`):** Flash/EEPROM (erasable) / DIP32 / 0x80000 (512KB) / VPP 12.0V / chip-id 0xda46 / protocol 0x05 (flash4) — matches Phase 82.

**Write attempt (-b, 1024 B deterministic image from `tools/gen_test_image.py 1024 1`; SHA `9983e8de67c0a81ea203c12b257a9ce03f57b12717c3633ce1142c1f29eca883`; image crosses the 256/512/768 page boundaries):**

| Attempt | Result |
|---------|--------|
| 1 | ERROR "Timeout verifying 0xd7 at 0x0000ff (got 0x00)" |
| 2 | Identical |

**Verdict: FAIL CONFIRMED** — timeout at the 256B page-0 boundary (`0x0000ff` = last byte of page 0; byte stays `0x00`), deterministic N=2. This re-bench ran on the Phase-84 build (= b10 base + VPP-skip), which **CARRIES the Phase-74 SDP/256B-page fix**. This re-confirms the Phase-82 finding: **the Phase-74 W29C040 flash4 fix does NOT work on real silicon.** NOT a trivial fix.

**Disposition: DEFERRED — reopen Phase-74 Wave-2 / CR-01.** Future tracker: `flash4-page-size-datasheet-sourced-cr01.md` (already in Deferred Items — Phase-74 CR-01 todo). The 256B page-0 boundary fault requires deeper root-cause into the flash4 SDP/page-poll sequence on W29C040 silicon, likely a dual-repo lockstep firmware fix.

### Excluded (D-32): W27E512 + W27E040

W27E512 and W27E040 NOT re-benched — genuine silicon stuck-bit wear (Phase 82, deterministic across reseats; D-32 classification), not FIX-01 material.

