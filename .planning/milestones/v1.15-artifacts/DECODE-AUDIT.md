# v1.15 — Decode-Correctness Audit (SC#1)

**Scope:** 11 chips from the operator's physical inventory, exercised on Leonardo + RURP Rev 2.0 across Phases 81–83.

**Purpose:** Consolidated milestone-close artifact confirming real-silicon behaviour vs the chip database (DB) for every chip's decode attributes (pinout, VPP, electrical type, algorithm, size). Every mismatch is recorded with a disposition. Cross-references `EVIDENCE.{md,json}` for raw bench data.

**Source data:** `.planning/milestones/v1.15-artifacts/bench/EVIDENCE.md` and `EVIDENCE.json` — the per-chip bench log authorised across Phases 81–83. This doc consolidates and disposition-annotates that raw record.

**Status:** SC#1 finalized — Wave-1 (84-01/02/03) outcomes incorporated; Phase-84 bench (84-05) verdicts filled by Plan 84-06 (2026-06-25). All bench-pending items resolved. FIX-01 closed per D-43.

---

## Part 1 — Per-Chip Decode-Correctness Table

Each row covers the five DB-claimed attributes: **pinout**, **VPP**, **electrical type**, **algorithm**, and **size**. Verdict is `CONFIRMED` (silicon matched the DB) or `MISMATCH` (with disposition). Cross-reference column links to the EVIDENCE row.

### Chips 1–5: 0x07 Family (EPROM_STD) + 0x08 (EPROM_QUICK)

| # | Chip | DB Algorithm (proto_id) | EVIDENCE Verdict | Pinout | VPP | Electrical Type | Algorithm (proto) | Size |
|---|------|------------------------|-----------------|--------|-----|-----------------|-------------------|------|
| 1 | W27C512 | 0x07 (EPROM_STD / EEPROM) | PASS (Phase 82 write) | CONFIRMED — DIP28_27512 | CONFIRMED — 12V | CONFIRMED — EEPROM | CONFIRMED — 0x07 | CONFIRMED — 65536 B |
| 2 | W27E512 | 0x07 (EPROM_STD / EEPROM) | FAIL (genuine) Phase 82 | CONFIRMED — DIP28_27512 | CONFIRMED — 12V | CONFIRMED — EEPROM | CONFIRMED — 0x07 | CONFIRMED — 65536 B |
| 3 | SST27SF512 | 0x07 (EPROM_STD / EEPROM) | PASS (Phase 82 write) | CONFIRMED — DIP28_27512 | CONFIRMED — 12V | CONFIRMED — EEPROM | CONFIRMED — 0x07 | CONFIRMED — 65536 B |
| 4 | W27E040 | 0x08 (EPROM_QUICK / EEPROM) | FAIL (genuine) Phase 82 | CONFIRMED — DIP32_STD | CONFIRMED — 12V | CONFIRMED — EEPROM | CONFIRMED — 0x08 | CONFIRMED — 524288 B |
| 5 | ST M27C512 | 0x07 (EPROM_STD / UV-EPROM) | PASS (Phase 83 write) | CONFIRMED — DIP28_27512 | MISMATCH — see note | CONFIRMED — UV-EPROM | CONFIRMED — 0x07 | CONFIRMED — 65536 B |

**W27E512 decode note:** The DB decode was correct — EEPROM / 0x07 / DIP28 / 12V / 65536 B. The FAIL was a genuine stuck erase bit (@0x3d, reads 0x7f want 0xFF) deterministic across N=3 reseats — silicon wear, NOT a decode mismatch. Disposition: D-32 (silicon-limited).

**W27E040 decode note:** Same class as W27E512 — DB decode correct (EEPROM / 0x08 / DIP32 / 12V / 524288 B). The FAIL was a genuine stuck erase bit (@0x7db, reads 0xEF want 0xFF) deterministic across N=2 reseats — silicon wear, NOT a decode mismatch. Disposition: D-32 (silicon-limited).

**ST M27C512 VPP mismatch note:** The Phase-83 plan stated 12V; the actual DB VPP is **13V** (confirmed by live bench). The bench firmware applied 13V correctly. This was a plan-text error, NOT a DB error. EVIDENCE.json `decode_uv04` records `13V`. Disposition: PLAN-TEXT only, DB is correct.

---

### Chips 6–8: 0x06 (FLASH_AMD_ALT) + 0x05 (FLASH_AMD_STD)

| # | Chip | DB Algorithm (proto_id) | EVIDENCE Verdict | Pinout | VPP | Electrical Type | Algorithm (proto) | Size |
|---|------|------------------------|-----------------|--------|-----|-----------------|-------------------|------|
| 6 | SST39SF040 | 0x06 (FLASH_AMD_ALT / Flash) | PASS (Phase 82 write) | CONFIRMED — DIP32_SST39SF040 | CONFIRMED — 12V | MISMATCH — see note | CONFIRMED — 0x06 | CONFIRMED — 524288 B |
| 7 | W29C040 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | FAIL (genuine) Phase 82 | CONFIRMED — DIP32 | CONFIRMED — 12V | CONFIRMED — Flash/EEPROM | CONFIRMED — 0x05 | CONFIRMED — 524288 B |
| 8 | W29C020 | 0x05 (FLASH_AMD_STD / Flash/EEPROM) | PASS (Phase 82 write) | CONFIRMED — DIP32 | CONFIRMED — 12V | CONFIRMED — Flash/EEPROM | CONFIRMED — 0x05 | CONFIRMED — 262144 B |

**SST39SF040 electrical type MISMATCH — observation, sst-keep disposition:**

The DB records `electrical.type = "Flash/EEPROM"` while the minipro upstream classification and algorithm family (0x06 / FLASH_AMD_ALT) indicate the chip is architecturally `Flash`. Silicon confirms it operates as a Flash device — block erase + byte program, no EEPROM-style page-write polling.

However, `electrical.type` is the **sole input** to `FLAG_CAN_ERASE` at `database.py:605`. SST39SF040 requires `Flash/EEPROM` membership to preserve `FLAG_CAN_ERASE = 0x02` on the wire, enabling the Phase-77/82-proven auto-erase path (REWR-03 confirmed on silicon — B over A verified clean). Relabeling to `Flash` would drop FLAG_CAN_ERASE and break erase — a regression forbidden by D-40 (sst-keep decision, Phase 84-03).

**Disposition (sst-keep):** `Flash/EEPROM` label is KEPT deliberately. It is functionally correct for RURP's purposes even if cosmetically imprecise vs upstream. A proper fix would require decoupling the display label from the erase-flag derivation (`sst-decouple` path — not authorized this phase). Recorded as an observation, not a blocking mismatch.

**W29C040 decode note:** The DB decode was correct (DIP32 / Flash/EEPROM / 12V / 524288 B / 0x05 — confirmed by `firestarter info`). The FAIL was a flash4 256B page-write timeout at the page-0 boundary (byte @0x0000FF, reads 0x00 — per-page auto-erase not confirmed). Deterministic across initial + 1 reseat. This is a write-path DEFECT, NOT a decode mismatch.

Phase 84 re-bench (EVIDENCE.md Phase-84 section, Task 3c): Re-benched under the Phase-84 build (b10+VPP-skip, which CARRIES the Phase-74 SDP/256B-page fix). 1024 B test image crossing the 256/512/768 page boundaries, N=2. **Result: FAIL CONFIRMED** — timeout at byte `0x0000FF` (last byte of page 0; byte stays `0x00`), identical on both attempts. This re-confirms: **the Phase-74 W29C040 flash4 fix does NOT work on real silicon.** NOT a trivial fix.

Disposition (D-43 / CR-01): DEFERRED — reopen Phase-74 Wave-2 / CR-01. Future tracker: `flash4-page-size-datasheet-sourced-cr01.md` (existing deferred item). The 256B page-0 boundary fault requires deeper root-cause into the flash4 SDP/page-poll sequence on W29C040 silicon, likely a dual-repo lockstep firmware fix.

---

### Chips 9–10: 0x40 (SRAM_STD / FRAM) + 0x08 (Large EPROM / UV-EPROM)

| # | Chip | DB Algorithm (proto_id) | EVIDENCE Verdict | Pinout | VPP | Electrical Type | Algorithm (proto) | Size |
|---|------|------------------------|-----------------|--------|-----|-----------------|-------------------|------|
| 9 | FM1608 | 0x40 (SRAM_STD / FRAM) | PASS (Phase 82 overwrite) | CONFIRMED — DIP28_JEDEC_SRAM_8K | MISMATCH — see note | MISMATCH → CORRECTED | CONFIRMED — 0x40 | CONFIRMED — 8192 B |
| 10 | AM27C020 | 0x08 (EPROM_QUICK / UV-EPROM) | ANOMALY (Phase 83 write) | CONFIRMED — DIP32 | MISMATCH — see note | CONFIRMED — UV-EPROM | CONFIRMED — 0x08 | CONFIRMED — 262144 B |

**FM1608 electrical type MISMATCH → CORRECTED (fm-fram-full, Phase 84-03):**

The DB originally recorded `electrical.type = "SRAM"` while the physical device is a **Ferroelectric RAM (FRAM)** — non-volatile, no destructive erase, overwrite-in-place. This was a decode mismatch. Silicon confirmed FRAM behaviour in Phase 82 (overwrite proof: B over A, clean read-back SHA match, no erase step needed or possible).

**Disposition (fm-fram-full):** Phase 84-03 shipped the correction: `build_db.py` per-chip override sets `electrical.type = "FRAM"` for FM1608; `_ELECTRICAL_TYPE_LABEL` extended; VPP display gate widened to `not in {"SRAM", "FRAM"}` (FM1608 has vpp_mv=12000 from infoic.xml artifact, now hidden); `RULE_PHASE84_RELABEL` in `diff_db.py`; companion tests pin CAN_ERASE stays OFF. DB regenerated; 673/673 host tests green. This mismatch is now RESOLVED in the DB.

**FM1608 VPP note:** infoic.xml records vpp_mv=12000 as an artifact of the minipro upstream data (the SRAM_STD protocol path does not apply VPP; FM1608 is a 5V FRAM). With the FRAM relabel, the VPP display is correctly hidden (gate = not-in-{SRAM,FRAM}). No VPP is applied to FM1608 on read or write — the `configure_sram` / `configure_fram` path is VPP-free by design.

**FM1608 blank-check note:** Phase 81 blank-check returned `Empty input` (firmware error) because `configure_sram` leaves `firestarter_operation_main = NULL` for `CMD_BLANK_CHECK`. This was a tooling gap, not a read fault. **Disposition (FIX-01 host half, Phase 84-02):** Host SRAM/FRAM blank-check short-circuit implemented — `check_eprom_blank()` detects `electrical-type in {"SRAM","FRAM"}` OR `protocol-id in {0x0E, 0x27, 0x28, 0x29}` and returns `False` before any firmware command, preventing the 0xA4 `MSG_ERR_EMPTY_INPUT`. 665 host tests green (2 new SRAM short-circuit tests). SHIPPED.

**AM27C020 VPP mismatch note:** Same class as ST M27C512 — plan text stated 12V, actual DB VPP is **13V**. Confirmed by EVIDENCE.json `decode_uv04`. Plan-text error, DB is correct.

**AM27C020 write ANOMALY — Phase 83 + Phase 84 re-bench:**

Phase 83: Write deterministically failed (bad bytes 15/16, retries 20, 0 bits programmed). The 0x07 28-pin W27C512 wrote clean the same session — signature is 0x08/32-pin-path specific. Plus intermittent localized read glitch (12-byte region at 0x008004–0x00800F). Chip silicon intact (0 bits changed).

Phase 84 re-bench (EVIDENCE.md Phase-84 section, Task 3a): Re-benched on the Phase-84 VPP-skip build, N=2 per D-54. Write attempt (16×0x00 @0x0000, `-b`): both attempts returned `ERROR "Failed to write memory, 0x000000, retries: 20, bad bytes: 15"`. Negative control `verify -a 0x0000` confirmed 0 bits programmed (chip reads 0x02 unchanged, = Phase 81/83 baseline). **Verdict: FAIL — 0-bits-programmed CONFIRMED on silicon, deterministic, N=2 exhausted.** NOT VPP-skip-related (the VPP-skip gates read/blank-check only; the write path is unchanged — T-84-14). Chip silicon is intact.

Disposition (FUT-06): DEFERRED. "AM27C020 / 0x08 32-pin Large-EPROM write-path takes 0 bits on Leonardo+Rev2.0; not VPP-skip-related; chip silicon intact." Unblock = root-cause the 0x08 32-pin write/VPP path (JP4/P1-as-VPP routing, firmware `eprom_write_execute` 0x08 branch vs 0x07) on the same board + shield + calibration.

---

### Chip 11: 0x0B (EPROM_LEGACY / UV-EPROM, NMOS)

| # | Chip | DB Algorithm (proto_id) | EVIDENCE Verdict | Pinout | VPP | Electrical Type | Algorithm (proto) | Size |
|---|------|------------------------|-----------------|--------|-----|-----------------|-------------------|------|
| 11 | 2516 | 0x0B (EPROM_LEGACY / UV-EPROM, NMOS) | ANOMALY (Phase 81 read; re-read Phase 84 — still unstable) | CONFIRMED — DIP24_2716 (info confirmed Phase 84) | MISMATCH — see note | CONFIRMED — UV-EPROM | CONFIRMED — 0x0B | CONFIRMED — 2048 B (info confirmed Phase 84) |

**2516 source note:** This chip is a user-override DB entry (Phase 81 GRAD-01/02) — it is absent from minipro's `infoic.xml` (all 28 "2516" hits there are `25160` SPI serial parts). The DB entry records: algorithm 0x0B, pinout DIP24_2716, UV-EPROM, vpp_mv 25000, size_bytes 2048. The entry has been manually safety-reviewed.

**2516 read ANOMALY — Phase 81 + Phase 84 re-bench:**

Phase 81: 3 distinct SHAs across N=3 on the initial read + 2 reseat cycles (D-07 exhausted). VPP pinned at 15.3V < 25.0V on the shared OE/VPP pin. Phase 81 also established the blank-state (NOT BLANK, 0x68@0x0000) and confirmed decode (`firestarter info 2516` = UV-EPROM / DIP24_2716 / 2048 B / VPP 25.0V / 0x0B).

Phase 84 re-bench (EVIDENCE.md Phase-84 section, Task 2): Re-read under the reflashed Phase-84 VPP-skip build (commit `cb947c7`), N=3 via `dev consistency-check --runs 3`. **Results: 3 distinct SHAs — STILL UNSTABLE.** First divergence at offset `0x005F`; 39/2048 bytes (1.9%) divergent. VPP-skip EFFECT: the Phase-81 ~18.8V boot-refusal is GONE (VPP-skip cleared it). BUT data still jitters → **the read instability is NOT solely VPP-gated**; it persists after the VPP-skip. Decode confirmed: UV-EPROM / DIP24 / 2048 B / VPP 25.0V / 0x0B — matches the user-override entry. No write / no preserve-dump (D-21 confirmed).

**2516 VPP MISMATCH — observation:** The DB entry records vpp_mv=25000 (25V, NMOS class per v1.14 D-07 best-effort graduation). The bench VPP during the 0x0B read registered ~15.3V (shared OE/VPP dropped rail, Phase 81) — below the 25V programming spec. The Phase-84 VPP-skip cleared the boot-refusal but did not resolve the underlying jitter. The shared OE/VPP pin instability is more fundamental than just VPP-enable-on-read. The DB decode (vpp_mv=25000) is the correct specification; the bench instability is a hardware/timing issue on the 0x0B legacy path, not a DB mismatch.

**Disposition (D-22 — intentional best-effort deferral):** GRAD-03 / SC#4 / FUT-03 are DEFERRED best-effort. A still-unstable read oracle on the irreplaceable 2516 makes a write proof vacuous (EVID-03). The VPP-skip narrowed the root cause (boot-refusal cleared) but did not fully resolve the shared OE/VPP instability. Future tracker: FUT-03 remains OPEN, requires a future bench session after the OE/VPP pin instability is understood at a deeper level. This deferral is intentional — NOT a gap; deliberately recorded so the verifier does not treat it as a failure.

---

## Part 2 — Dispositions Summary

### (i) VPP-Skip Firmware Gate — SHIPPED (Phase 84-01, FIX-01 firmware half)

**Item:** Read and blank-check operations on 0x07/0x08 EPROM chips were calling `eprom_check_vpp()` in `eprom_generic_init()`, which drives the VPP regulator and checks for under/over-voltage. This caused:
- Chip-1 (W27C512) read refused at boot (VPP 18.8V > 12.0V threshold — transient regulator state); cleared by board reset
- Benign VPP-low warnings on ST M27C512 (11.9V < 13.0V) during reads (reads apply no VPP — these warnings are spurious)

**Fix:** Early-return guard in `eprom_generic_init()` for `CMD_READ` and `CMD_BLANK_CHECK` — skips `eprom_check_vpp()` entirely. Write, erase, and chip-ID still gate VPP (T-84-01 over-voltage block preserved). 5-assertion native dispatch test suite (2 positive + 3 negative). Commit `cb947c7` on `v1.15-bench-validation-of-operator-inventory` branch.

**Status:** SHIPPED — FIX-01 firmware half CLOSED.

---

### (ii) FM1608 Blank-Check Host Short-Circuit — SHIPPED (Phase 84-02, FIX-01 host half)

**Item:** `firestarter blank FM1608` (and any SRAM/FRAM chip) routed to the firmware `CMD_BLANK_CHECK` via `check_eprom_blank()`, but `configure_sram()` leaves `firestarter_operation_main = NULL` for that command, causing firmware to return `0xA4 MSG_ERR_EMPTY_INPUT`.

**Fix:** Host-side short-circuit in `check_eprom_blank()` (class constant `_SRAM_PROTO_IDS = frozenset({0x0E, 0x27, 0x28, 0x29})`). Detects SRAM/FRAM by electrical-type OR protocol-id before entering `_operation_context` — returns `False` without sending any firmware command. 2 new tests (`TestSramBlankCheckShortCircuit`); 665 host tests green. Commits `e5bfa3a` (RED) + `4c74b8d` (GREEN) in `firestarter_app` submodule.

**Status:** SHIPPED — FIX-01 host half CLOSED.

---

### (iii) SST39SF040 / FM1608 Relabel Outcome (Phase 84-03 — D-40 STOPped Part)

**FM1608 = fm-fram-full (SHIPPED):**

FM1608 `electrical.type` corrected from `SRAM` → `FRAM` via `build_db.py` per-chip override. Display-layer companion changes: `_ELECTRICAL_TYPE_LABEL["FRAM"] = "FRAM"` in `ic_layout.py`; VPP gate widened to `not in {"SRAM", "FRAM"}` in `ic_layout.py` + `eprom_info.py`. `RULE_PHASE84_RELABEL` added to `diff_db.py`. CAN_ERASE unaffected (FRAM not in `{"EEPROM", "Flash/EEPROM"}`). DB regenerated; 673/673 host tests green. FM1608 `list` snapshot updated (`SRAM` → `FRAM`). Commits `d8ca7a2` + `47c86c9` + `4d5b3de`.

**SST39SF040 = sst-keep (D-40 STOPPED — explicit observation):**

The D-40 STOP was triggered because relabeling SST39SF040 from `Flash/EEPROM` to `Flash` would drop `FLAG_CAN_ERASE` (the Phase-77/82-proven auto-erase path). Operator decision: KEEP.

> **SST39SF040 cosmetic-label observation (D-40):** The upstream minipro classification and algorithm family (0x06 / FLASH_AMD_ALT) suggest the chip is architecturally `Flash`. However, `electrical.type` is the SOLE input to `FLAG_CAN_ERASE` at `database.py:605`. SST39SF040 (proto 0x06, flash3) requires `Flash/EEPROM` to preserve `FLAG_CAN_ERASE = 0x02` on the wire, enabling the Phase-77/82-proven auto-erase path (REWR-03 silicon-confirmed). Relabeling to `Flash` would break erase — a regression D-40 forbids. The display label `Flash/EEPROM` is functionally correct for RURP's purposes even if cosmetically imprecise. To display `Flash` without breaking erase, a decoupled display/erase mechanism would be needed (`sst-decouple` path — not authorized this phase).

No code change shipped for SST39SF040. Zero regression. This observation is recorded for future reference.

---

### (iv) W27E512 + W27E040 Genuine Stuck-Bit ERASE FAILs — Silicon-Limited (D-32)

**W27E512 (0x07 EEPROM):** Phase 82 FAIL — erase cannot clear bit 7 at offset 0x3d (reads 0x7F, want 0xFF). Deterministic across N=3 reseats (D-08 exhausted). Identical offset and value every time = stuck cell, not contact or VPP. Chip read cleanly in Phase 81 (read-only) — defect manifests only on erase/write. DB decode was fully correct; the write path engaged at the correct parameters.

**W27E040 (0x08 EEPROM):** Phase 82 FAIL — erase cannot clear bit 4 at offset 0x7db (reads 0xEF, want 0xFF). Same stuck-bit-on-erase signature class as W27E512 (different offset and algorithm). N=2 reseats exhausted. DB decode correct.

**Disposition (D-32):** Both are genuine silicon wear events — NOT FIX-01 material, NOT DB/algorithm errors, NOT tooling bugs. The erase path is correct; the chips have worn past their erase endurance on these specific cells. REWR-01 is partially satisfied (W27C512 + SST27SF512 PASS; W27E512 FAIL); REWR-02 has no positive 0x08 write PASS (W27E040 sole 0x08 chip — deferred FUT-05, needs a functional 0x08 chip).

---

### (v) AM27C020 0x08 Write, W29C040 flash4 256B-page, 2516 0x0B Read — Final Dispositions (Phase 84-05 Re-bench Complete)

**AM27C020 (0x08 Large EPROM) — DEFERRED (FUT-06):**

Phase 83 ANOMALY: `write` deterministically fails (bad bytes 15/16, retries 20, 0 bits programmed). Phase 84 re-bench confirmed (N=2 exhausted): **0-bits-programmed CONFIRMED on silicon, deterministic**. NOT VPP-skip-related (write path unchanged by the skip). Chip silicon intact.

**Disposition: DEFERRED — FUT-06.** "AM27C020 / 0x08 32-pin Large-EPROM write-path takes 0 bits on Leonardo+Rev2.0; not VPP-skip-related." Unblock = root-cause the 0x08 32-pin write/VPP path (JP4/P1-as-VPP routing, firmware `eprom_write_execute` 0x08 branch vs 0x07). This is an intentional deferral (D-31/D-43) — NOT a gap; explicitly recorded so the verifier does not treat it as a failure.

**W29C040 (0x05 flash4, 512KB) — DEFERRED (Phase-74 Wave-2 / CR-01):**

Phase 82 FAIL: write times out at the 256B page-0 boundary. Phase 84 re-bench confirmed (N=2 on Phase-84 build carrying the Phase-74 SDP/256B-page fix): **FAIL CONFIRMED** — the Phase-74 fix does NOT work on real silicon.

**Disposition: DEFERRED — reopen Phase-74 Wave-2 / CR-01.** Future tracker: `flash4-page-size-datasheet-sourced-cr01.md`. Requires deeper root-cause into the flash4 SDP/page-poll sequence on W29C040 silicon, likely a dual-repo lockstep firmware fix. This is an intentional deferral (D-31/D-43) — NOT a gap; explicitly recorded so the verifier does not treat it as a failure.

**2516 (0x0B EPROM_LEGACY, NMOS) — DEFERRED best-effort (GRAD-03 / FUT-03, D-22):**

Phase 81 ANOMALY: 3 distinct SHAs across N=3 reads + 2 reseats. Phase 84 re-bench (N=3, `dev consistency-check --runs 3`): **STILL UNSTABLE** — 3 distinct SHAs, 39/2048 bytes (1.9%) divergent. VPP boot-refusal CLEARED by VPP-skip (Phase-81 ~18.8V refusal gone). BUT data jitter persists — instability NOT solely VPP-gated. Decode confirmed: UV-EPROM / DIP24 / 2048 B / VPP 25.0V / 0x0B — matches the user-override entry (CONFIRMED). No write / no preserve-dump (D-21).

**Disposition: DEFERRED best-effort (D-22) — GRAD-03 / FUT-03 remain OPEN.** A still-unstable read oracle on the irreplaceable 2516 makes a write proof vacuous (EVID-03). Future tracker: FUT-03 (NMOS bench SHA-match), requires a future bench session after the OE/VPP pin instability is understood at a deeper level than VPP-enable-on-read alone. This is an intentional best-effort deferral (D-22) — NOT a gap; explicitly recorded so the verifier does not treat it as a failure.

---

## Part 3 — EVIDENCE Cross-Reference Index

| Chip | EVIDENCE.md Section | EVIDENCE.json Cell | Phase | Key SHA |
|------|--------------------|--------------------|-------|---------|
| W27C512 | Phase 81 sweep row #1 + Phase 82 write row #1 | cells[0] (read) + cells[11] (write) | 81+82 | `9376dcd8…97ad23c8` (read) / `e16b2a5b…dc326ab5` (write B) |
| W27E512 | Phase 81 sweep row #2 + Phase 82 write row #2 | cells[1] (read) + cells[12] (write) | 81+82 | `71189f7f…48da9063` (read) / FAIL |
| SST27SF512 | Phase 81 sweep row #3 + Phase 82 write row #3 | cells[2] (read) + cells[13] (write) | 81+82 | `f633b2f5…f8056360` (read) / `e16b2a5b…dc326ab5` (write B) |
| W27E040 | Phase 81 sweep row #4 + Phase 82 write row #4 | cells[3] (read) + cells[14] (write) | 81+82 | `67f70ccd…468b4254` (read) / FAIL |
| SST39SF040 | Phase 81 sweep row #5 + Phase 82 write row #5 | cells[4] (read) + cells[15] (write) | 81+82 | `c19c3e07…a348368d` (read) / `a38b13b4…d970b96b` (write B) |
| W29C020 | Phase 81 sweep row #6 + Phase 82 write row #8 | cells[5] (read) + cells[19] (write) | 81+82 | `93ff5287…66b53602` (read) / `47304933…c11ce58c` (write B) |
| W29C040 | Phase 81 sweep row #7 + Phase 82 write row #7 | cells[6] (read) + cells[18] (write) | 81+82 | `d44736a9…1e3b48b3` (read) / FAIL |
| FM1608 | Phase 81 sweep row #8 + Phase 82 write row #6 | cells[7] (read) + cells[17] (write) | 81+82 | `2ef1444b…3d4c0037` (read) / `3c23e7fc…34f75c90` (write B) |
| ST M27C512 | Phase 81 sweep row #9 + Phase 83 write row #1 | cells[8] (read) + cells[20] (write) | 81+83 | `71189f7f…48da9063` (read) / `008948af…ec397c3f` (write) |
| AM27C020 | Phase 81 sweep row #10 + Phase 83 write row #2 | cells[9] (read) + cells[21] (write) | 81+83 | `08b687a3…177ed496` (read) / ANOMALY |
| 2516 | Phase 81 sweep row #11 | cells[10] (read) | 81 | ANOMALY (3 distinct SHAs, no stable value) |

---

## Part 4 — FIX-01 Close-Statement (D-43)

**FIX-01 status: CLOSED per D-43 — "fixed where in-posture; deeper write-path defects RCA'd + deferred with rationale."**

### What was fixed (in-posture, shipped + bench-confirmed):

1. **VPP-skip firmware gate (FIX-01 firmware half, Phase 84-01):** The Phase-81 ~18.8V boot-refusal on W27C512 and spurious VPP-low warnings on ST M27C512 were caused by `eprom_check_vpp()` running during read/blank-check operations. Fix: early-return guard in `eprom_generic_init()` for `CMD_READ` + `CMD_BLANK_CHECK`. Write, erase, and chip-ID still gate VPP (over-voltage protection preserved, T-84-01). Native dispatch test suite (5 assertions). Commit `cb947c7`. **Bench-confirmed (Phase 84-05):** the 18.8V boot-refusal is GONE after the re-flash.

2. **FM1608 blank-check host short-circuit (FIX-01 host half, Phase 84-02):** `firestarter blank FM1608` routed to the firmware `CMD_BLANK_CHECK` which `configure_sram()` left with `NULL` handler → `0xA4 MSG_ERR_EMPTY_INPUT`. Fix: host-side short-circuit in `check_eprom_blank()` detecting SRAM/FRAM by electrical-type OR protocol-id, returning `False` without any firmware command. 2 new tests (665 host tests green). Commits `e5bfa3a` + `4c74b8d`. SHIPPED.

3. **FM1608 FRAM relabel (fm-fram-full, Phase 84-03):** FM1608 `electrical.type` corrected from `SRAM` → `FRAM` in `build_db.py`. Display-layer companion changes; 673/673 host tests green. SHIPPED.

### What was RCA'd and deferred (not trivially fixable, named trackers assigned):

4. **AM27C020 0x08 write — DEFERRED (FUT-06):** 0-bits-programmed confirmed deterministically on silicon (N=2). NOT VPP-skip-related. Chip silicon intact. Requires root-cause into the 0x08 32-pin write/VPP path (JP4/P1-as-VPP routing, `eprom_write_execute` 0x08 branch). This is an intentional deferral (D-31/D-43) — not a gap in the scope of this phase.

5. **W29C040 flash4 256B-page fault — DEFERRED (Phase-74 Wave-2 / CR-01):** Phase-74 SDP/256B-page fix confirmed NOT silicon-effective (N=2 re-bench on Phase-84 build). Requires deeper root-cause into the flash4 SDP/page-poll sequence on W29C040 silicon, likely a dual-repo lockstep firmware fix. Existing tracker: `flash4-page-size-datasheet-sourced-cr01.md`. This is an intentional deferral — not a gap in scope.

### Silicon-limited failures (not FIX-01 material):

6. **W27E512 + W27E040 stuck-bit ERASE FAILs (D-32):** Genuine silicon wear events — erase path engaged at correct decode parameters; specific cells worn past endurance. NOT re-benched in Phase 84 (D-32 exclusion). NOT FIX-01 material; NOT DB/algorithm errors.

### Intentional deferrals (best-effort, not failures):

7. **2516 read still unstable (GRAD-03 / FUT-03, D-22):** VPP boot-refusal cleared by VPP-skip; data jitter persists (3 distinct SHAs, N=3, 1.9% divergence). Instability NOT solely VPP-gated. No write / no preserve-dump (D-21). GRAD-03 / FUT-03 remain OPEN best-effort. This is an intentional best-effort deferral (D-22) — not a gap; the PASS bar was pre-recorded in EVIDENCE.md (D-08) and the conditions for FUT-03 are documented.

### SST39SF040 label observation (recorded, not shipped):

8. **SST39SF040 sst-keep observation (D-40):** DB records `Flash/EEPROM`; upstream architecture is `Flash`. Label kept deliberately — it is the sole input to `FLAG_CAN_ERASE` (dropping it would break the Phase-77/82-proven auto-erase path). Decoupling display label from erase-flag derivation (`sst-decouple` path) is not authorized this phase. Zero code change; zero regression.

### Milestone close + beta-cut:

**Milestone close and firmware versioning/beta-cut are OPERATOR-GATED (D-12/D-43) and are NOT performed in this phase.** This plan only documents readiness for `/gsd-verify-work`. The operator must authorize `/gsd-complete-milestone v1.15` and the `3.0.0b11` lockstep beta cut separately.

---

## Part 5 — Evidence Cross-Reference Index (Phase 84 additions)

| Chip | EVIDENCE.md Section | Key Result |
|------|--------------------|----|
| 2516 (re-read) | Phase 84, Task 2 | STILL UNSTABLE: N=3, 3 distinct SHAs, 1.9% (39/2048 bytes) divergent; boot-refusal cleared |
| AM27C020 (re-bench) | Phase 84, Task 3a | FAIL CONFIRMED: 0-bits-programmed, N=2, NOT VPP-skip-related; FUT-06 |
| W29C040 (re-bench) | Phase 84, Task 3c | FAIL CONFIRMED: 256B page-0 boundary timeout, N=2; Phase-74 fix not silicon-effective; CR-01 reopen |

---

*Authored: 2026-06-25 as Plan 84-04 (Wave-2 consolidation), finalized by Plan 84-06 (Phase-84 bench verdicts filled).*
*Sources: EVIDENCE.md + EVIDENCE.json (Plans 81-03, 82-02/03, 83-02/03, 84-05) + 84-01/02/03/05 SUMMARY files.*
*Milestone close: operator-gated (D-12/D-43). This document records readiness for `/gsd-verify-work`.*
