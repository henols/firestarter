# Phase 90: Per-Protocol Bench Validation + Ledger - Research

**Researched:** 2026-06-26
**Domain:** Documentation-authoring + bench-validation (hardware-in-the-loop regression). No firmware/host source change.
**Confidence:** HIGH (all sources are in-repo, read directly this session; no external/web lookups required)

<user_constraints>
## User Constraints (from 90-CONTEXT.md)

### Locked Decisions
- **D-01: PASS = regression-match to the v1.15 EVIDENCE baseline**, not a standalone clean op. Re-run each on-hand chip's op on the recomposed firmware; PASS requires a result **byte-identical** to v1.15 (same read SHA-256, same write-cycle verdict + image SHA). Proves the recompose "changed nothing on silicon."
- **D-02: Both ops per chip — non-destructive read AND write-cycle A→B.** Recompose changed the **write-path** primitives (P3 VPP gate / P4 chip-id / P5 poll-readback); a read-only test would not exercise the recomposed code. Each chip earns PASS from BOTH a read-SHA regression and the write-cycle A→B (auto-erase verdict + image-SHA) regression.
- **D-03: N ≥ 3 byte-identical reads** define a clean read-SHA cell (never trust N=1; reseat+retry per v1.15). Any read OR write SHA that **differs** from the v1.15 baseline → recorded **FAIL / INVESTIGATE** (recompose-regression candidate) — never auto-passed.
- **D-04: Compose by cross-reference, no data duplication.** `PROTOCOL-LEDGER.json` rows reference `EVIDENCE.json` cells (by chip name) and `validation_matrix_spec.json` family entries (by family/protocol id) as **keys** — it does NOT copy SHA/verdict data. `.md` = human view of the same rows. Exact JSON field names/ordering are researcher/planner discretion within this principle.
- **D-05: Claude drives the bench via USB passthrough; operator gates each silicon op.** Claude flashes the final recomposed Phase-89 firmware + runs each op; operator confirms Rev 2.0 silkscreen, confirms controller/port identity per task, authorizes each live op.
- **D-06: Gitlinks stay PINNED at b10** (a1953c2 / 98b3a92); **no lockstep beta cut.** Leonardo is EXEMPT from chip-out-before-sideload (Uno-class only) — but operator still authorizes each flash.
- **D-07: Full UNVERIFIED rows; status-only defect rows.** Each of the 6 no-silicon buckets (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34) gets a complete row (proposed name, datasheet-representative chip citation, primitives used, flash delta) with `verification_status: UNVERIFIED` + `reason: "no on-hand silicon"`. The 3 open-defect rows reproduce their current documented status verbatim (id + one-line disposition + link to source record) — no re-litigation, no status change.
- **D-08: SAFE-04 throughout.** Over-voltage stays blocked at the firmware VPP check; the host `chip_resolver.resolve_chip` guard is never bypassed; 2516 stays UNVERIFIED; no irreplaceable UV part written on an unstable read path.
- **D-09: Mandatory PASS fields (ROADMAP SC#2).** An authoritative PASS row cannot be recorded without `oracle: leonardo+Rev2.0` AND non-empty evidence references (stored bench artifact paths). Missing either → not a PASS.
- **D-10: Frozen world stands.** No DB / dispatch / wire change; this phase validates silicon + authors the ledger only — no `firestarter` or `firestarter_app` source change expected beyond rerunning existing gates.

### Claude's Discretion
- Exact `PROTOCOL-LEDGER.json` field names, row ordering, `.md` table layout (within D-04 compose-by-cross-reference).
- Bench evidence artifact storage layout/paths (consistent with the v1.15 `.planning/v1.15/bench/` convention) — paths just have to be the non-empty evidence references D-09 requires.
- Chosen N for reads is ≥ 3 (D-03); the exact harness invocation (e.g. reuse `firestarter dev consistency-check`) is planner discretion.

### Deferred Ideas (OUT OF SCOPE)
- Fixing the 3 open defects — W29C040/CR-01, AM27C020/FUT-06, 2516/FUT-03. Carried at documented status only.
- 0x34 X88C64 programming handler — PCB-blocked (FUT-01); stays not_implemented / UNVERIFIED.
- Acquiring silicon for the 6 no-silicon buckets.
- Lockstep beta cut `3.0.0b11` + gitlink bump — standing operator-gated release item.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LEDGER-01 | `PROTOCOL-LEDGER.{md,json}` records a per-protocol row (proposed name, datasheet citation, primitives used, verification status) and composes with — does not replace — the v1.13 `validation_matrix_spec.json` (by family) and v1.15 `EVIDENCE.json` (by chip+sha). | §"Upstream Schemas + Join Keys" gives exact keys that exist in both files; §"12-Bucket Row Identities" enumerates all rows; §"Primitives Used Per Bucket" supplies the primitives column; §"JSON Schema Proposal" gives a non-duplicating shape. |
| LEDGER-02 | Each protocol with on-hand silicon is bench-validated on Leonardo + RURP Rev 2.0; a PASS row structurally requires `oracle: leonardo+Rev2.0` plus non-empty evidence references. | §"Bench Harness + Exact Commands" gives the read-SHA + write-cycle ops; §"Evidence Artifact Storage" gives the non-empty refs path; §"JSON Schema Proposal" encodes the structural PASS constraint (D-09). |
| LEDGER-03 | The 6 no-silicon buckets recorded as explicit UNVERIFIED; the 3 open-defect rows carried at current documented status (not silently changed). | §"12-Bucket Row Identities" (UNVERIFIED rep chips); §"Open-Defect Rows" (verbatim dispositions + source links). |
| SAFE-04 | Over-voltage stays blocked at firmware VPP check; `chip_resolver.resolve_chip` host guard never bypassed; no irreplaceable UV part written on an unstable read path (2516 stays UNVERIFIED). | §"SAFE-04 Verification Targets" gives exact post-recompose file:line for both guards (NOTE: CONTEXT line numbers are pre-recompose — corrected here). |
</phase_requirements>

## Summary

Phase 90 is a **documentation + hardware-regression** phase, not a code phase. The recomposed firmware (Phase 89 HEAD `firestarter@a296195`, Leonardo flash 25136 B / 87.7%) is the build under test. The deliverable is `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` — one row per protocol bucket — that **cross-references** (never copies) the two upstream sources of truth: the v1.13 per-family matrix (`firestarter_app/tools/validation_matrix_spec.json`) and the v1.15 per-chip evidence (`.planning/v1.15/bench/EVIDENCE.json`).

The load-bearing technical work is the bench regression: for each of the 4 on-hand chips (W29C020/0x05, SST39SF040/0x06, W27C512/0x07, FM1608/0x28) re-run BOTH a non-destructive N≥3 read and a write-cycle A→B on the recomposed firmware, and assert the produced SHA-256s are **byte-identical** to the v1.15 baseline SHAs (which are hard-codable from EVIDENCE.json — listed in this doc). An identical SHA proves the recompose was behavior-preserving on silicon; any mismatch is a FAIL/INVESTIGATE alarm. The 6 no-silicon buckets get full UNVERIFIED rows; the 3 open defects (W29C040/CR-01, AM27C020/FUT-06, 2516/FUT-03) are carried verbatim.

**Primary recommendation:** Reuse the existing v1.15 harness verbatim — `firestarter dev consistency-check --runs 3` for the read-SHA cells and `tools/gen_test_image.py` (seed 1 / seed 2) + the write path for the A→B cells. Hard-code the v1.15 baseline SHAs (table below) as the regression oracle. Author the ledger as cross-reference rows. Touch no source; rerun `check_dispatch.py` / `diff_db.py` / `pio test -e native` only to re-confirm the frozen world. Do NOT bump gitlinks, do NOT cut beta.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Per-chip silicon regression (read SHA, write-cycle A→B) | Bench hardware (Leonardo + Rev 2.0) driven by host CLI | Firmware (recomposed handlers under test) | The thing being validated is silicon behavior of the recomposed firmware; the host CLI is the driver, the firmware is the SUT. |
| SHA-256 oracle / image generation | Host tooling (`tools/gen_test_image.py`, host `hashlib`) | — | Deterministic image + digest computation is pure host Python; no chip involved until write. |
| Read-SHA divergence verdict (N≥3) | Host CLI (`dev consistency-check`) | Firmware read path | Consistency diagnostic already exists host-side; firmware just streams bytes. |
| Ledger authoring (`PROTOCOL-LEDGER.{md,json}`) | Meta-repo `.planning/` (docs only) | — | Pure documentation artifact; cross-references but does not modify sub-repo files. |
| Cross-reference integrity (join keys resolve) | Meta-repo doc + the two upstream JSON files | — | The ledger is the consumer; the upstream files stay authoritative (D-04). |
| Safety posture (SAFE-04) | Firmware VPP check + host resolve_chip guard | — | Both are pre-existing guards; this phase only *verifies present + unmodified*, never edits. |

## Standard Stack

This phase introduces **no new libraries** (SAFE-05 carried from milestone — only new artifact is the ledger). The "stack" is the existing in-repo harness, reused verbatim.

### Core (existing harness — reuse, do not build)
| Tool | Location | Purpose | Why Standard |
|------|----------|---------|--------------|
| `firestarter dev consistency-check` | `firestarter_app/firestarter/cli_handlers.py:1047` | N consecutive reads → SHA-256 divergence verdict (0=PASS / 1=FAIL / 2=hw-error) | The carried-since-v1.6 N-read diagnostic; exactly the D-03 N≥3 read-SHA tool. Default `--runs 3`, minimum 2. |
| `tools/gen_test_image.py` | `firestarter_app/tools/gen_test_image.py` | Deterministic `random.Random(seed)` image; `<size_bytes> <seed> <out>` prints SHA-256 | The v1.15 phase82 A→B oracle generator. seed=1 = image A, seed=2 = image B by convention. |
| `firestarter dev write-cycle` | `firestarter_app/firestarter/cli_handlers.py:1137` | Erase → write source image → read-back N times; assert SHA-256 == source SHA (0/1/2 verdict) | The write-cycle proof tool. NB: takes ONE `source_image` arg + `--runs`; the A→B *sequence* is two invocations (write A, then write B over A to prove auto-erase). See pitfalls re: FRAM. |
| `firestarter write -b` (direct) | `firestarter_app/firestarter/cli_handlers.py` (`write` cmd) | Direct write with skip-blank-check | Required for FM1608/FRAM where `dev write-cycle` erase step is "Not supported" (v1.15 used `write -b` for the FM1608 A→B). |
| `pio run -e leonardo` / `pio run -t upload -e leonardo` | `firestarter/` | Build + flash the recomposed firmware to the Leonardo | Per `firestarter/CLAUDE.md`; 250000 baud, 1024 B buffer. |
| `pio test -e native` | `firestarter/` | Re-confirm frozen-world native suite green | 105/105 at Phase 89 close; rerun to confirm no drift. |
| `tools/check_dispatch.py`, `tools/diff_db.py` | `firestarter_app/tools/` | Frozen-world DB gates (0 violations / identity diff) | Rerun-to-confirm only; no DB change this phase. |
| host `sha256sum` / Python `hashlib` | host | Compute/compare SHA-256 against the baseline | `gen_test_image.py` already prints the digest; `sha256sum <file>` for read dumps. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `dev consistency-check --runs 3` | Manual `read` × 3 + `sha256sum` | consistency-check already does the N-read + divergence verdict + per-run binary capture (the evidence artifacts) — no reason to hand-roll. |
| `dev write-cycle` for FM1608 | `write -b` direct (as v1.15 did) | `dev write-cycle` erase step is unsupported on FRAM/0x28 (returns "Not supported"); v1.15 proved the A→B overwrite via two `write -b` calls. Reuse that exact method for the FM1608 row. |

**Installation:** None. Verify the harness is importable in the devcontainer: `cd firestarter_app && pip install -e '.[test]'` (per `reference_firestarter_app_python_test_env`), then `firestarter --help`.

## Package Legitimacy Audit

> **Not applicable.** This phase installs no external packages (SAFE-05 — no new third-party dependency; the only new artifact is the ledger). Audit skipped with reason.

## Upstream Schemas + Join Keys (LEDGER-01 / D-04)

The ledger composes by cross-reference. Both upstream files were read this session; the join keys below **exist in both files** and are confirmed.

### Source 1 — `.planning/v1.15/bench/EVIDENCE.json` (per-chip baseline; join by **chip name**)
- `cells[]` array; each cell carries `chip`, `family`, `board`, `shield`, `op`, `sha256`, `verdict`, `read_count`, and (for write-cycle cells) `write_image_seed_A/B`, `sha256_image_A/B`. `[VERIFIED: EVIDENCE.json read this session]`
- `locked_columns`: `chip, family, board, shield, blank_state, op, sha256, verdict, anomalies`. `evid_extension_columns`: `read_count, blank_check_result, write_image_seed_A, sha256_image_A, write_image_seed_B, sha256_image_B, cr01_risk`.
- `phase82` block defines the write-cycle op (`write_A+verify_A → write_B+verify_B`), the verdict taxonomy (PASS / FAIL (CR-01) / FAIL (genuine) / ANOMALY), the `gen_test_image.py` seed convention, and storage convention `/tmp/firestarter_bench_p82/<chip>_img_{A,B}.bin`.
- **JOIN KEY = `cell.chip` (string).** Each ledger PASS row references the matching EVIDENCE cell(s) by `evidence_chip: "<chip name>"` + the `op` value. Do NOT copy the SHA into the ledger (D-04) — reference the cell.

### Source 2 — `firestarter_app/tools/validation_matrix_spec.json` (per-family matrix; join by **family id / protocol id**)
- `families[]`; each entry has `id` (e.g. `eprom`, `flash3`, `flash4`, `flash_intel`, `eeprom28c`, `sram`), `handler`, `protocols` (DECIMAL list), `rep_chip`, `tier1/tier2/tier3`. `[VERIFIED: validation_matrix_spec.json read this session]`
- **Protocols are DECIMAL** in this file: eprom `[7, 8, 11]` (0x07/0x08/0x0B), eeprom28c `[13]` (0x0D), flash3 `[6]` (0x06), flash4 `[5]` (0x05), flash_intel `[16]` (0x10), sram `[14, 39, 40, 41]` (0x0E/0x27/0x28/0x29). **0x34 has NO family entry** (it is `not_implemented`, never validated) — the ledger's 0x34 row references no matrix family (carry `matrix_family: null`).
- **JOIN KEY = `family.id` + protocol membership.** Each ledger row references its family by `matrix_family: "<id>"` and notes the hex bucket. Confirmed: every real bucket maps to exactly one family id except 0x34.

### Join-key confirmation matrix (both keys present)
| Bucket | EVIDENCE join (`chip`) | matrix_spec join (`family.id`, dec protocol) |
|--------|------------------------|----------------------------------------------|
| 0x05 | `W29C020` ✓ (+ `W29C040` defect cell ✓) | `flash4`, protocol 5 ✓ |
| 0x06 | `SST39SF040` ✓ | `flash3`, protocol 6 ✓ |
| 0x07 | `W27C512` ✓ | `eprom`, protocol 7 ✓ |
| 0x28 | `FM1608` ✓ | `sram`, protocol 40 ✓ |
| 0x0D/0E/10/27/29 | none (no-silicon) | `eeprom28c`/`sram`/`flash_intel`/`sram`/`sram` ✓ |
| 0x34 | none | none (no family entry — not_implemented) |

> **EVIDENCE family-string caveat:** EVIDENCE cells label FM1608 `family: "0x40 (SRAM_STD / FRAM)"` — `0x40` is **decimal 40 = hex 0x28** (the historical conflation retired in NAME-04 / PROTOCOLS.md §1.10). The ledger must use the corrected `0x28` bucket id and may footnote the EVIDENCE `0x40` label as the decimal-40↔hex-0x28 conflation. `[VERIFIED: EVIDENCE.json + PROTOCOLS.md §1.10]`

## v1.15 Baseline SHAs — the hard-coded regression targets (D-01)

These are the byte-exact PASS oracles for the 4 on-hand chips. PASS on the recomposed firmware = produce these exact SHAs. `[VERIFIED: EVIDENCE.json cells read this session]`

| Bucket | Chip | Read-SHA (op `read+blank_check`, N=3) | Write-cycle final SHA (op `write_A→write_B`) | image A (seed 1) | image B (seed 2) | v1.15 verdict |
|--------|------|----------------------------------------|-----------------------------------------------|------------------|------------------|---------------|
| 0x05 | W29C020 | `93ff5287b7e6eff8b0e8463b86476baf4f2f97e412a3053551303d6566b53602` | `47304933ce388bfd97d23ea6bff1a5ed1f7728e99f2cc3e7d05c82a7c11ce58c` | `b2fc5cbf…a133457` | `47304933…c11ce58c` | PASS / PASS (CR-01 did NOT manifest on b10; 256 KB part) |
| 0x06 | SST39SF040 | `c19c3e07b94b12beb32fbb6afd3de432453a895d82406a38390db78fa348368d` | `a38b13b4d285756c1f385a75d0cdf89f72720764c21fd933ced75ebdd970b96b` | `77a771b2…f1662bbd` | `a38b13b4…d970b96b` | PASS / PASS (flash3 slow ~240 s/write) |
| 0x07 | W27C512 | `9376dcd81713e7edc4f8df8e98b7c834eefcd880c2f9fef04ee1602397ad23c8` | `e16b2a5b26d99440a8e596963faa0f2d64fff4e1dd9682b93b2f8f1ddc326ab5` | `604d9570…1645d637` | `e16b2a5b…dc326ab5` | PASS / PASS |
| 0x28 | FM1608 | `2ef1444bc950050c92f373cd2f5442022af98aa900aefd82c749cff93d4c0037` | `3c23e7fcbe88c5a09ab50cf8301e9adf884fcdd519b6f9fefc72583b34f75c90` | `a89c4b45…8ce5415d` | `3c23e7fc…b34f75c90` | PASS / PASS (FRAM: used `write -b` direct, NOT `dev write-cycle`) |

> **Critical D-01 nuance:** the read-SHA baseline is a property of the chip's **current contents** at v1.15 sweep time (these chips are not factory-blank). For the read regression to be a valid D-01 match, the chip contents must be unchanged since v1.15. **Sequencing matters:** run the read regression BEFORE the write-cycle on each chip (the write-cycle overwrites contents and would invalidate the read-SHA baseline). After the write-cycle, the chip holds image B — a subsequent read SHA would equal the write-cycle final SHA, not the original read baseline. Plan tasks must order read-then-write per chip, or explicitly note the chip is no longer at its v1.15 read baseline. This is a planner sequencing constraint, not a defect. `[VERIFIED: EVIDENCE.json blank_state notes + read/write op semantics]`

## 12-Bucket Row Identities (LEDGER-01 / LEDGER-03 / D-07)

From `firestarter/doc/PROTOCOLS.md` §0 + §1 and `firestarter/datasheets/README.md`. The ledger has **12 real-bucket rows** (plus the open-defect carries). `[VERIFIED: PROTOCOLS.md + datasheets/README.md read this session]`

| hex | proposed name | handler (file) | datasheet folder slug | on-hand chip → status | UNVERIFIED rep chip + datasheet path |
|-----|---------------|----------------|-----------------------|------------------------|--------------------------------------|
| 0x05 | FLASH-AMD-STD | `configure_flash4()` → `flash_type_4.cpp` | `0x05-FLASH-AMD-STD` | **W29C020** → bench (PASS target) | — (on-hand) |
| 0x06 | FLASH-AMD-ALT | `configure_flash3()` → `flash_type_3.cpp` | `0x06-FLASH-AMD-ALT` | **SST39SF040** → bench (PASS target) | — (on-hand) |
| 0x07 | EPROM-STD | `configure_eprom()` → `eprom.cpp` | `0x07-EPROM-STD` | **W27C512** → bench (PASS target) | — (on-hand) |
| 0x08 | EPROM-QUICK | `configure_eprom()` → `eprom.cpp` | `0x08-EPROM-QUICK` | (W27E040/W27C020/AM27C020 on hand but NOT in Phase-90 4-chip scope; AM27C020 carried as FUT-06 defect row) | — |
| 0x0B | EPROM-LEGACY | `configure_eprom()` → `eprom.cpp` | `0x0B-EPROM-LEGACY` | (2516 carried as FUT-03 defect row; UNVERIFIED) | rep = 2516 (`2516_EPROM.pdf`) — but see defect row |
| 0x0D | EEPROM-POLL | `configure_eeprom28c()` → `eeprom_28c.cpp` | `0x0D-EEPROM-POLL` | UNVERIFIED | **AT28C256** — `datasheets/0x0D-EEPROM-POLL/AT28C256.pdf` |
| 0x0E | SRAM-32PIN | `configure_sram()` → `sram.cpp` | `0x0E-SRAM-32PIN` | UNVERIFIED | **DS1245Y** — `datasheets/0x0E-SRAM-32PIN/DS1245Y.pdf` |
| 0x10 | FLASH-INTEL | `configure_flash_intel()` → `flash_intel.cpp` | `0x10-FLASH-INTEL` | UNVERIFIED | **Intel-28F010** — `datasheets/0x10-FLASH-INTEL/Intel-28F010.pdf` |
| 0x27 | SRAM-24PIN | `configure_sram()` → `sram.cpp` | `0x27-SRAM-24PIN` | UNVERIFIED | **6116** — `datasheets/0x27-SRAM-24PIN/6116.pdf` |
| 0x28 | SRAM-STD | `configure_sram()` → `sram.cpp` | `0x28-SRAM-STD` | **FM1608** → bench (PASS target) | — (on-hand) |
| 0x29 | SRAM-512K-1M | `configure_sram()` → `sram.cpp` | `0x29-SRAM-512K-1M` | UNVERIFIED | **DS1245Y** (substitute for DS1250Y) — `datasheets/0x29-SRAM-512K-1M/DS1245Y.pdf` |
| 0x34 | EEPROM-X88C64 | `configure_not_implemented()` → `not_implemented.cpp` | `0x34-EEPROM-X88C64` | UNVERIFIED (PCB-blocked FUT-01) | **X88C64** — `datasheets/0x34-EEPROM-X88C64/X88C64.pdf` (data-book scan) |

> **The CONTEXT scope's "6 no-silicon buckets" = 0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34.** Note 0x0B is NOT in that 6: it has an on-hand chip (2516) but that chip is read-unstable, so its bucket is represented by the **FUT-03 open-defect carry** rather than an UNVERIFIED-for-no-silicon row. 0x08 likewise has on-hand chips but is represented by the AM27C020/FUT-06 defect carry (the 4-chip bench scope deliberately excludes 0x08). Confirm this framing with the planner — the ledger should still show all 12 buckets as rows; the *reason* a bucket is not bench-proven differs (no-silicon vs open-defect). `[VERIFIED: CONTEXT scope + EVIDENCE + STATE deferred table]`

### Open-Defect Rows (carried verbatim — D-07, LEDGER-03)
Reproduce current documented status; no re-litigation. Source records to link: `.planning/STATE.md` Deferred Items table + `EVIDENCE.json` phase84 blocks. `[VERIFIED: STATE.md + EVIDENCE.json phase84]`

| Defect id | Chip / bucket | Verbatim disposition | Source link |
|-----------|---------------|----------------------|-------------|
| CR-01 / Phase-74 Wave-2 | W29C040 / 0x05 (flash4) | "W29C040 flash4 256B page-write fault — open, reopened by Phase 84. Phase-74 fix not silicon-effective. Reopen Phase-74 Wave-2 (likely dual-repo lockstep firmware fix)." FAIL CONFIRMED: timeout verifying byte @0x0000ff (256 B page-0 boundary). | STATE.md Deferred Items; `EVIDENCE.json` `phase84.task3c_w29c040`; `flash4-page-size-datasheet-sourced-cr01.md` |
| FUT-06 | AM27C020 / 0x08 (Large EPROM) | "AM27C020 0x08 32-pin write/VPP path — deferred, RCA'd, not trivially fixable. 0-bits-programmed; requires 0x08 32-pin Large EPROM write/VPP root-cause." Silicon intact; not VPP-skip-related. | STATE.md Deferred Items; `EVIDENCE.json` `phase84.task3a_am27c020` |
| FUT-03 | 2516 / 0x0B (Legacy NMOS) | "2516 0x0B read instability + write proof — deferred best-effort (D-22). 3 distinct SHAs after VPP-skip; shared OE/VPP pin. 2516 stays UNVERIFIED; not write-graduated (SAFE-04)." | STATE.md Deferred Items; `EVIDENCE.json` `phase84.task2_2516_reread` |

## Primitives Used Per Bucket (the "primitives used" + "flash delta" columns)

From Phase 89 `primitives.cpp` caller map (read this session) + 89-FLASH-LEDGER.md. The 4 primitives are P4 `chip_id_report`, P3 `vpp_check_window`, P5 `poll_readback`, P7 SDP/const-table dedup. `[VERIFIED: primitives.cpp header caller map + 89-FLASH-LEDGER.md]`

| Bucket | Handler | P4 chip_id_report | P3 vpp_check_window | P5 poll_readback | P7 SDP dedup |
|--------|---------|-------------------|---------------------|------------------|--------------|
| 0x05 FLASH-AMD-STD | flash_type_4.cpp | ✓ (via flash_utils.cpp AMD/JEDEC FLASH_ENABLE_ID) | — (5V, no VPP) | ✓ (flash4_wait_for_page_write, cap=1024) | ✓ (uses shared SDP tables) |
| 0x06 FLASH-AMD-ALT | flash_type_3.cpp | ✓ (via flash_utils.cpp) | — (5V) | — | ✓ (shared SDP tables) |
| 0x07 EPROM-STD | eprom.cpp | ✓ (A9-12V; CHECK_CHIP_ID path force_warning=false per CR-01; generic-init path FLAG_FORCE) | ✓ (via eprom_check_vpp) | — (verify is whole-buffer bitmask, NOT poll_readback — D-02 deferral) | — |
| 0x08 EPROM-QUICK | eprom.cpp | ✓ | ✓ | — | — |
| 0x0B EPROM-LEGACY | eprom.cpp | ✓ | ✓ (direct-VPE rail; INV-01) | — | — |
| 0x0D EEPROM-POLL | eeprom_28c.cpp | ✓ (A9-12V, mfr_addr=mem_size-64) | — (5V) | ✓ (eeprom28c_wait_for_write, cap=2000) | ✓ (P7 dedup landed in eeprom_28c.cpp) |
| 0x0E/0x27/0x28/0x29 SRAM | sram.cpp | — | — | — | — (plain read/write; no primitive use) |
| 0x10 FLASH-INTEL | flash_intel.cpp | ✓ (command-register 0x90 autoselect) | ✓ (via flash_intel_check_vpp; 12V mandatory) | — | — |
| 0x34 EEPROM-X88C64 | not_implemented.cpp | — | — | — | — (returns 0xBB; no handler) |

**Flash deltas (per-primitive, Phase 89 close — feed the ledger "flash delta" column):** `[VERIFIED: 89-FLASH-LEDGER.md]`
- P7 (PRIM-02 SDP dedup): 0 B
- P4 (PRIM-03 chip_id_report): −164 B
- P3 (PRIM-04 vpp_check_window): −402 B (biggest single saving)
- P5 (PRIM-05 poll_readback): +2 B
- CR-01 fix (post-phase, caller-keyed force_warning + 3 WR-02 tests): +46 B
- **Phase-cumulative: −518 B net.** Baseline (Phase 88) 25654 B / 89.5% → final (`firestarter@a296195`) **25136 B / 87.7%**.

> Note: the flash delta is a per-*primitive* number, not per-*bucket* — primitives are shared across buckets, so a bucket row's "flash delta" should reference which primitives it uses and cite the aggregate −518 B (the ledger cannot attribute B-savings to a single bucket). Recommend a single milestone-level "flash impact" note + per-row "primitives used" list, rather than a fictitious per-bucket byte number.

## Bench Harness + Exact Commands (LEDGER-02 / D-02 / D-03 / D-05)

Reuse the v1.15 workflow verbatim. Per-chip, per-task preconditions (operator-gated): confirm `controller:` identity on the port (ttyACM* shuffles on replug — `feedback_verify_port_identity_each_task`), confirm Rev 2.0 silkscreen (`user_shield_revisions` — the EEPROM hw byte cannot distinguish revs), operator authorizes each live op.

### Step 0 — Flash the recomposed firmware (once, operator-authorized)
```bash
cd firestarter
git -C . rev-parse HEAD          # confirm == a296195 (Phase 89 HEAD, recomposed build under test)
pio run -e leonardo              # build; expect Flash 87.7% (25136 B / 28672 B)
pio run -t upload -e leonardo    # flash (Leonardo EXEMPT from chip-out-before-sideload, D-06)
```
> The VERSION STRING still reports `3.0.0b10` (Phase 84 did not bump FIRMWARE_VERSION; the build is the v1.16-branch recompose, NOT stock b10). Record the **submodule commit a296195**, not the version string, as the firmware-under-test identity. `[VERIFIED: 89-FLASH-LEDGER.md + EVIDENCE phase84 version_string_caveat]`

### Step 1 — Read-SHA regression (D-03 N≥3), run BEFORE write per chip
```bash
cd firestarter_app
firestarter dev consistency-check <CHIP> --runs 3 --output-dir <evidence_dir>/<chip>-read/
# verdict: 0=PASS(1 distinct SHA) / 1=FAIL(divergent) / 2=hw-error
# then compare the captured per-run SHA to the v1.15 baseline read-SHA (table above)
```
- `<CHIP>` CLI names: `W29C020`, `SST39SF040`, `W27C512`, `FM1608` (verify exact CLI spelling via `firestarter list | grep -i`).
- D-01 PASS = the consistency-check distinct SHA equals the v1.15 baseline read-SHA. Divergent across N=3, OR differs from baseline → FAIL/INVESTIGATE.

### Step 2 — Write-cycle A→B regression (D-02), the load-bearing op
```bash
# generate deterministic images (seed 1 = A, seed 2 = B); <SIZE> = chip size in bytes
python tools/gen_test_image.py <SIZE> 1 /tmp/firestarter_bench_p90/<chip>_img_A.bin   # prints SHA == baseline image A
python tools/gen_test_image.py <SIZE> 2 /tmp/firestarter_bench_p90/<chip>_img_B.bin   # prints SHA == baseline image B

# Flash/EEPROM + EPROM path (W29C020, SST39SF040, W27C512): dev write-cycle proves auto-erase A→B
firestarter dev write-cycle <CHIP> /tmp/firestarter_bench_p90/<chip>_img_A.bin --runs 1 --output-dir <evidence_dir>/<chip>-wcA/
firestarter dev write-cycle <CHIP> /tmp/firestarter_bench_p90/<chip>_img_B.bin --runs 1 --output-dir <evidence_dir>/<chip>-wcB/
# B written over A with NO explicit erase; clean B verify == auto-erase proof; readback SHA must == baseline image-B SHA

# FRAM path (FM1608 ONLY): dev write-cycle erase is "Not supported" — use DIRECT write -b (v1.15 method)
firestarter write FM1608 -b /tmp/firestarter_bench_p90/FM1608_img_A.bin   # verify RC=0
firestarter write FM1608 -b /tmp/firestarter_bench_p90/FM1608_img_B.bin   # verify RC=0; B overwrites A
firestarter dev consistency-check FM1608 --runs 3   # confirm N=3 == image-B SHA
```
- Chip sizes (from EVIDENCE / DB): W29C020 = 262144 B; SST39SF040 = 524288 B; W27C512 = 65536 B; FM1608 = 8192 B.
- **Image-SHA sanity:** `gen_test_image.py` printing the baseline image-A/B SHA (table above) confirms the generator is deterministic across host versions before any chip is touched.
- D-01 PASS = write-cycle verdict 0 (PASS) AND readback SHA == v1.15 baseline write-cycle final SHA (table above). Any mismatch → FAIL/INVESTIGATE.
- Negative control (carry the v1.15 pattern): a wrong-file `verify` should exit RC=1 — proves the verify is non-vacuous.

### SHA comparison
`gen_test_image.py` prints the digest; for read dumps use `sha256sum <per-run.bin>`. Compare against the hard-coded baseline strings (table above) — equality is the entire D-01 verdict.

## Evidence Artifact Storage + Ledger Location (LEDGER-02 / D-09 discretion)

`[CITED: v1.15 convention .planning/v1.15/bench/]` The v1.15 bench dir contains exactly `EVIDENCE.json` + `EVIDENCE.md` (no binaries committed — binaries lived in `/tmp/firestarter_bench_p82/`). For D-09 the ledger needs **non-empty evidence references** = stored artifact paths. Recommended layout (planner discretion):

```
.planning/v1.16/
└── ledger/
    ├── PROTOCOL-LEDGER.json          # the cross-reference rows (machine view)
    ├── PROTOCOL-LEDGER.md            # human view of the same rows
    └── bench/                        # Phase-90 bench artifacts (the D-09 evidence refs)
        ├── W29C020-read/  W29C020-wcA/  W29C020-wcB/   (consistency-check + write-cycle per-run binaries)
        ├── SST39SF040-read/ …
        ├── W27C512-read/ …
        ├── FM1608-read/ FM1608-wcA/ FM1608-wcB/
        └── BENCH-LOG.md              # per-task: port identity, Rev confirm, command, RC, SHA, operator-authorize note
```
- `.planning/v1.16/` does not yet exist — Phase 90 creates it. Confirmed `.planning/v1.16/ledger/` is the ledger home (CONTEXT/REQUIREMENTS). `[VERIFIED: ls — dir absent]`
- D-09 evidence refs in PROTOCOL-LEDGER.json should be repo-relative paths under `.planning/v1.16/ledger/bench/...` (committed binaries) OR a `BENCH-LOG.md` anchor capturing the run + SHA, so the reference is non-empty and durable. Recommend committing at least the captured per-run SHAs + the BENCH-LOG (the binaries themselves may be large for SST39SF040 512 KB — planner may choose to commit SHAs + log rather than 512 KB binaries; the *reference* must still resolve).
- `commit_docs` is on (init); ledger + bench artifacts get committed to the meta-repo `.planning/` on the v1.16 branch (meta tracks only `.planning/`). Sub-repo gitlinks stay PINNED at b10 (D-06).

## JSON Schema Proposal (LEDGER-01 / D-04 / D-09)

Honors compose-by-cross-reference (keys, not data), the mandatory-PASS structural constraint (D-09), and a `verification_status` enum. Field names are discretion; this is a recommended shape.

```jsonc
{
  "schema_version": 1,
  "generated": "2026-06-26",
  "milestone": "v1.16",
  "firmware_under_test": { "submodule_commit": "a296195", "flash_bytes": 25136, "flash_pct": 87.7,
                            "version_string_caveat": "reports 3.0.0b10; build is v1.16 recompose" },
  "oracle": "leonardo+Rev2.0",
  "composes_with": {
    "v1_13_matrix": "firestarter_app/tools/validation_matrix_spec.json",
    "v1_15_evidence": ".planning/v1.15/bench/EVIDENCE.json"
  },
  "milestone_flash_impact": { "net_delta_bytes": -518, "baseline_bytes": 25654,
    "per_primitive": { "P7": 0, "P4": -164, "P3": -402, "P5": 2, "CR01_fix": 46 } },
  "rows": [
    {
      "bucket": "0x05",
      "proposed_name": "FLASH-AMD-STD",
      "handler": "configure_flash4()",
      "handler_file": "flash_type_4.cpp",
      "datasheet_slug": "0x05-FLASH-AMD-STD",
      "datasheet_citation": "datasheets/0x05-FLASH-AMD-STD/W29C020.pdf",
      "matrix_family": "flash4",                       // cross-ref key into validation_matrix_spec.json
      "matrix_protocols_dec": [5],
      "primitives_used": ["P4", "P5", "P7"],           // P3 not used (5V)
      "verification_status": "PASS",                   // enum below
      "oracle": "leonardo+Rev2.0",                     // REQUIRED non-null for PASS (D-09)
      "on_hand_chip": "W29C020",
      "evidence": {                                    // REQUIRED non-empty for PASS (D-09)
        "v1_15_read_cell": { "evidence_chip": "W29C020", "op": "read+blank_check" },     // KEY, not SHA
        "v1_15_writecycle_cell": { "evidence_chip": "W29C020", "op": "write_A+verify_A → write_B+verify_B" },
        "p90_artifacts": [".planning/v1.16/ledger/bench/W29C020-read/", ".planning/v1.16/ledger/bench/W29C020-wcB/"],
        "p90_read_sha_matches_v115": true,             // the D-01 regression verdict
        "p90_writecycle_sha_matches_v115": true
      }
    }
    // … one row per the 12 buckets …
  ],
  "open_defects": [
    { "id": "CR-01", "chip": "W29C040", "bucket": "0x05",
      "disposition": "<verbatim from STATE.md>",
      "source_link": ".planning/STATE.md#deferred-items / EVIDENCE.json#phase84.task3c_w29c040",
      "status_changed": false }
    // FUT-06, FUT-03 …
  ]
}
```

**`verification_status` enum:** `PASS` | `UNVERIFIED` | `FAIL-INVESTIGATE` | `open-defect-carried`.

**Structural PASS constraint (D-09) — encode as an authoring/validation rule:** a row may have `verification_status: "PASS"` **only if** `oracle == "leonardo+Rev2.0"` AND `evidence.p90_artifacts` is non-empty AND both `p90_*_sha_matches_v115 == true`. A row missing any of these is not a PASS (downgrade to `FAIL-INVESTIGATE` or `UNVERIFIED` as appropriate). This is independently checkable (see Validation Architecture).

## Architecture Patterns

### System Architecture Diagram (data flow)
```
v1.15 EVIDENCE.json (baseline SHAs) ───┐
                                       ├──► [ledger authoring] ──► PROTOCOL-LEDGER.{json,md}
validation_matrix_spec.json (family) ──┘            ▲                     │ (cross-ref keys only,
                                                    │                     │  no SHA copy — D-04)
                                                    │                     ▼
gen_test_image.py (seed 1/2) ──► img_A/img_B.bin ──┤            .planning/v1.16/ledger/bench/
                                                    │                  (D-09 evidence refs)
                                                    │
[recomposed fw a296195] ──flash──► Leonardo+Rev2.0 ─┤
   │                                                │
   ▼ (operator-gated per op)                        │
firestarter dev consistency-check (read N≥3) ──► per-run SHA ──► compare to baseline read-SHA ──► PASS/FAIL
firestarter dev write-cycle (A then B) / write -b (FRAM) ──► readback SHA ──► compare to baseline wc-SHA ──► PASS/FAIL
```

### Recommended Task Structure
```
.planning/v1.16/ledger/      # new — created by Phase 90
├── PROTOCOL-LEDGER.json
├── PROTOCOL-LEDGER.md
└── bench/                    # per-chip artifacts + BENCH-LOG.md
```

### Pattern: Read-then-write per chip (sequencing)
**What:** For each on-hand chip, run the read-SHA regression first, then the write-cycle. **Why:** the write-cycle overwrites the chip contents that the read-SHA baseline measured (see D-01 nuance above).

### Anti-Patterns to Avoid
- **Copying SHA/verdict data from EVIDENCE.json into the ledger** — violates D-04; reference by key only.
- **Auto-passing a SHA mismatch** — D-03 forbids it; any mismatch is FAIL/INVESTIGATE (a recompose-regression alarm).
- **Using `dev write-cycle` on FM1608** — FRAM erase is "Not supported"; use `write -b` (the v1.15 method).
- **Recording a per-bucket flash-delta byte number** — primitives are shared; attribute the −518 B at milestone level + list primitives per row.
- **Trusting the firmware VERSION STRING (`3.0.0b10`) as the build identity** — record the submodule commit `a296195`.
- **Bumping gitlinks or cutting beta** — D-06: PINNED at b10, no cut.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| N-read divergence + SHA capture | A bash loop of `read` + `sha256sum` | `firestarter dev consistency-check --runs 3` | Already does N reads, divergence verdict (0/1/2), per-run binary capture (the evidence artifacts). |
| Deterministic A/B images | `dd if=/dev/urandom` | `tools/gen_test_image.py <size> <seed>` | urandom is non-reproducible; the seed convention is the v1.15 oracle and produces the hard-coded baseline SHAs. |
| Auto-erase A→B proof | Manual erase + write + diff | `dev write-cycle` (writes B over A with no explicit erase) | The "no explicit erase, clean B" is exactly the auto-erase proof; re-implementing risks a vacuous pass. |
| Frozen-world DB check | Manual JSON diff | `check_dispatch.py` + `diff_db.py` | Rerun-to-confirm; identity diff / 0 violations is the contract. |

**Key insight:** The entire v1.15 phase81–84 harness already produces every artifact Phase 90 needs. Phase 90's novelty is the *cross-reference ledger* and the *regression-match-to-baseline verdict*, not new tooling.

## Runtime State Inventory

> Not a rename/refactor/migration phase (doc + bench validation only). Section omitted per template guidance, except the one stateful concern below.

- **Chip physical contents are stateful across milestones.** The v1.15 read-SHA baselines assume the on-hand chips' contents are unchanged since the v1.15 sweep (2026-06-23/24). If any chip was written between then and now, its read-SHA will not match the v1.15 baseline (a false FAIL). Plan a per-chip "is this still at its v1.15 contents?" precondition, or treat the first read as a fresh baseline + note the deviation. The write-cycle A→B is unaffected (it establishes its own A then B). `[VERIFIED: EVIDENCE blank_state notes]`

## Common Pitfalls

### Pitfall 1: FM1608 "Empty input" blank-check on FRAM
**What goes wrong:** `dev write-cycle` / `blank_check` on FM1608 (0x28 FRAM) errors with "Empty input" / erase "Not supported" — FRAM has no blank concept.
**Why it happens:** FRAM is not erasable; the blank-check/erase tooling has no FRAM path (v1.15 flagged this as a benign tooling gap, NOT a read/write fault).
**How to avoid:** Use `write -b` (direct, skip blank-check) for the FM1608 A→B, exactly as v1.15 did. The read N=3 was identical PASS in v1.15. Record the "Empty input" note as benign.
**Warning signs:** "Empty input" or "Not supported" on the erase step for FM1608 — expected, not a failure. `[VERIFIED: EVIDENCE FM1608 cells]`

### Pitfall 2: VPP-regulator instability on the bench (v1.15 family)
**What goes wrong:** read-init refusal at boot (VPP >12V), benign VPP-low warnings, or VPP-high on first write attempt.
**Why it happens:** Known v1.15 VPP-regulator instability on this bench; cleared by board reset / operator VPP correction.
**How to avoid:** Pin to the **Leonardo + Rev 2.0 oracle** (the whole point of the fixed oracle — it avoids the deferred v1.9 shield-fleet read bug AND the uno328pb/Rev-2.2 W27C512 instability). On a VPP hiccup, reset board + retry (do not record N=1). `[VERIFIED: EVIDENCE notes + project_uno328pb_bench_instability_27_04 memory]`

### Pitfall 3: uno328pb / Rev-2.2 instability if the wrong board/shield is used
**What goes wrong:** Using a uno328pb or Rev 2.2 shield yields timeouts + 0xff drift on W27C512 reads — false FAILs.
**How to avoid:** Confirm controller identity per task (ttyACM* shuffles) and operator-confirm Rev 2.0 silkscreen every task. The Leonardo+Rev2.0 oracle is mandatory (D-05). `[VERIFIED: memory project_uno328pb_bench_instability_27_04 + user_shield_revisions]`

### Pitfall 4: py3.12-devcontainer masks py3.11 CI for host tooling
**What goes wrong:** Running `gen_test_image.py` / host suite under devcontainer py3.12 may behave differently than the py3.11 CI target.
**Why it happens:** Devcontainer is Python 3.12; CI is py3.9/3.11 (`reference_devcontainer_py312_masks_ci_py39`).
**How to avoid:** This phase changes no host source, so CI risk is minimal — but if any host file is touched, validate `ruff check` + `ruff format --check` against py3.11 before claiming green. `gen_test_image.py` uses only stdlib `random`/`hashlib` (deterministic across versions — verified: pure `random.Random(seed)`), so the baseline SHAs are version-stable. `[VERIFIED: gen_test_image.py source + memory]`

### Pitfall 5: SAFE-04 line numbers in CONTEXT are pre-recompose
**What goes wrong:** D-08 cites `eprom.cpp:282` and `flash_intel.cpp:65` for the over-voltage check — but Phase 89 (P3) **moved** that check into `primitives.cpp`.
**How to avoid:** Verify the over-voltage HIGH check at its **post-recompose** location (see SAFE-04 targets below). `[VERIFIED: primitives.cpp:106 + eprom.cpp:280 + flash_intel.cpp:64 read this session]`

### Pitfall 6: Confusing decimal-40 EVIDENCE family label with hex
**What goes wrong:** EVIDENCE labels FM1608 `family: "0x40"`; treating `0x40` as a hex bucket id is wrong.
**How to avoid:** `0x40` in that label is **decimal 40 = hex 0x28** (NAME-04 conflation, retired). Use 0x28 in the ledger. `[VERIFIED: PROTOCOLS.md §1.10]`

## SAFE-04 Verification Targets (D-08 — exact post-recompose locations)

The CONTEXT D-08 line numbers are pre-recompose. Verify these **current** locations (read this session, `firestarter@a296195`):

| Check | Current location | Verdict to record |
|-------|------------------|-------------------|
| Over-voltage HIGH check `vpp_mv > (uint32_t)handle->vpp_mv + 500` (+500 mV threshold, FORCE→WARN / else ERROR) | `firestarter/src/proms/primitives.cpp:106` (inside `vpp_check_window`) — called by `eprom_check_vpp` (`eprom.cpp:280`) and `flash_intel_check_vpp` (`flash_intel.cpp:64`) | PRESENT + UNMODIFIED (threshold + semantics byte-identical; moved to shared primitive in P3, behavior unchanged) |
| Host `chip_resolver.resolve_chip` support-status guard (refuses non-`supported` chips before any wire dict / serial byte) | `firestarter_app/firestarter/chip_resolver.py` `resolve_chip()` (support_status guard ~line 55; function starts line 12) | PRESENT + UNCHANGED (`git -C firestarter_app diff --quiet` clean at Phase 89 close) |
| 2516 UNVERIFIED status | `firestarter_app/firestarter/data/chip_database.json` (`verification_status=UNVERIFIED`, `support_status=supported`) | UNVERIFIED — no write-graduation this phase |

> Verification method (no edits): `grep -n "vpp_mv > (uint32_t)handle->vpp_mv + 500" firestarter/src/proms/primitives.cpp`; `grep -n "support_status" firestarter_app/firestarter/chip_resolver.py`; `git -C firestarter_app diff --quiet && echo CLEAN`; `git -C firestarter diff --quiet && echo CLEAN`. `[VERIFIED: 89-FLASH-LEDGER SAFE-04 table + direct grep this session]`

## Code Examples

### Confirm the firmware-under-test identity (no version-string trust)
```bash
git -C firestarter rev-parse HEAD          # must == a296195
cd firestarter && pio run -e leonardo      # expect: Flash 87.7% (used 25136 bytes from 28672)
```

### One on-hand chip, full D-02 regression (W27C512 example)
```bash
cd firestarter_app
# 1. read regression FIRST (D-01: chip still at v1.15 contents)
firestarter dev consistency-check W27C512 --runs 3 --output-dir .planning/v1.16/ledger/bench/W27C512-read/
#    expect distinct SHA == 9376dcd8…97ad23c8  (v1.15 read baseline) → PASS

# 2. write-cycle A→B (load-bearing — exercises recomposed write primitives)
python tools/gen_test_image.py 65536 1 /tmp/firestarter_bench_p90/W27C512_img_A.bin   # prints 604d9570…1645d637
python tools/gen_test_image.py 65536 2 /tmp/firestarter_bench_p90/W27C512_img_B.bin   # prints e16b2a5b…dc326ab5
firestarter dev write-cycle W27C512 /tmp/firestarter_bench_p90/W27C512_img_A.bin --runs 1
firestarter dev write-cycle W27C512 /tmp/firestarter_bench_p90/W27C512_img_B.bin --runs 1 --output-dir .planning/v1.16/ledger/bench/W27C512-wcB/
#    expect readback SHA == e16b2a5b…dc326ab5  (v1.15 write-cycle baseline) → PASS
```

### Re-confirm frozen world (rerun-only, no edits)
```bash
cd firestarter && pio test -e native            # expect 105/105 green
cd firestarter_app && python tools/check_dispatch.py   # exit 0, 0 violations
python tools/diff_db.py                          # exit 0, identity diff
git -C . diff --quiet && echo HOST-CLEAN
git -C ../firestarter diff --quiet && echo FW-CLEAN
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Per-handler inline VPP check + chip-id compare | Shared `primitives.cpp` (P3/P4/P5) | Phase 89 (v1.16) | SAFE-04 check now lives in `vpp_check_window` (primitives.cpp:106), not in handler bodies — verify there, not at the CONTEXT line numbers. |
| Bench = standalone clean-op proof | Bench = regression-match to v1.15 baseline SHA | Phase 90 (this) | A mismatch is now a recompose-regression alarm, not just "op failed." |
| build_db Rule 1/2/3 overrides (WARNING-5, FM1608→0x28) | Variant-decode (Phase 86) | Phase 86 (v1.16) | FM1608 is now structurally 0x28; the EVIDENCE `0x40` label is the retired decimal-40 conflation. |

**Deprecated/outdated:**
- CONTEXT D-08 SAFE-04 line numbers (`eprom.cpp:282`, `flash_intel.cpp:65`) — superseded by `primitives.cpp:106` after the P3 extraction.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The 4 on-hand chips are still at their v1.15 read-SHA contents (not written since 2026-06-24). | Baseline SHAs / Runtime State | A read regression would false-FAIL; mitigated by read-then-write ordering + a per-chip precondition note. |
| A2 | Exact CLI chip names are `W29C020` / `SST39SF040` / `W27C512` / `FM1608`. | Bench Commands | Wrong name → "chip not found"; mitigated by `firestarter list \| grep -i` at task start. (FM1608/W27C512 confirmed in EVIDENCE phase83 `cli_name`; W29C020/SST39SF040 inferred from chip column.) |
| A3 | Committing 512 KB SST39SF040 per-run binaries vs SHAs-only is acceptable for D-09 evidence refs. | Evidence Storage | If binaries must be committed, repo size grows; recommend SHA + BENCH-LOG refs (still non-empty). Planner/operator to confirm. |
| A4 | The 0x08 and 0x0B buckets are represented by open-defect carries (FUT-06 / FUT-03), not separate UNVERIFIED-for-no-silicon rows, even though chips are on hand. | 12-Bucket Row Identities | If the operator wants 0x08/0x0B bench-proven via a sibling chip, scope expands; CONTEXT scope says the 4-chip set is fixed — confirm framing. |
| A5 | `gen_test_image.py` output is byte-stable across Python 3.9/3.11/3.12 (stdlib `random.Random`). | Pitfalls / Stack | If a CPython `random` change altered the stream, baseline image SHAs would not reproduce; mitigated — the printed SHA is checked before any write, and `random.Random` MT stream is stable across these versions. |

## Open Questions (RESOLVED)

> All three were resolved during planning — the plans (90-04) and CONTEXT.md scope
> encode each resolution; recorded here so the section is closed, not carried open.

1. **Are the on-hand chips still at v1.15 contents?**
   - Known: v1.15 read baselines recorded 2026-06-24; chips not factory-blank.
   - Unclear: whether anything wrote them since.
   - Recommendation: read-then-write ordering; if a read diverges from baseline, record the actual SHA as a fresh baseline + note the deviation (do NOT auto-FAIL the recompose for a content change unrelated to firmware).
   - **RESOLVED:** read-before-write ordering catches content drift; a divergent read SHA is recorded as a fresh baseline + note, NOT an auto-FAIL of the recompose. Encoded in Plan 90-04 Task 2 how-to-verify.
2. **Commit binaries or SHAs+log for D-09 evidence?**
   - Recommendation: commit per-run SHAs + `BENCH-LOG.md` (non-empty refs) and optionally the small binaries (FM1608 8 KB, W27C512 64 KB); skip committing the 512 KB SST39SF040 binary unless operator wants it.
   - **RESOLVED:** commit per-run SHAs + `BENCH-LOG.md` as the non-empty D-09 evidence refs; skip the 512 KB SST39SF040 binary unless the operator explicitly requests it. Encoded in Plan 90-04 Task 2 acceptance criteria.
3. **Does the operator want 0x08/0x0B bench-proven via sibling chips this phase?**
   - CONTEXT scope says no (4-chip set fixed; 0x08/0x0B carried as defect rows). Confirm before planning.
   - **RESOLVED:** CONTEXT.md scope locks the 4-chip set (W29C020 / SST39SF040 / W27C512 / FM1608); 0x08 and 0x0B are carried as open-defect rows only (FUT-06 / FUT-03). No additional silicon needed.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Leonardo + RURP Rev 2.0 bench (USB passthrough) | All LEDGER-02 bench ops | ✗ (hardware — operator-gated) | — | NONE — bench ops cannot proceed without it (ROADMAP-fixed oracle). |
| `pio` (PlatformIO) | Build/flash recomposed fw | probe `command -v pio` | — | NONE for flashing; build can be confirmed from 89 ledger (25136 B) if pio absent. |
| `firestarter` CLI (host) | read/write-cycle ops | probe `firestarter --help` after `pip install -e '.[test]'` | 3.0.0b-series | NONE. |
| `node` (for gsd-tools) | research/commit tooling | via vscode-server glob (not on PATH) | — | `reference_gsd_sdk_in_devcontainer`. |
| Python 3 stdlib (`random`, `hashlib`) | `gen_test_image.py` | ✓ | py3.12 devcontainer | — (version-stable). |

**Missing dependencies with no fallback:**
- The physical Leonardo + Rev 2.0 bench (operator-owned hardware). This phase's LEDGER-02 PASS rows **cannot be produced without it**; the UNVERIFIED rows + open-defect carries + ledger authoring CAN proceed doc-only. If the bench is unavailable in this session, the planner should structure tasks so the doc/UNVERIFIED/defect work is independent of the operator-gated bench ops (which become a `checkpoint:human-verify` gate).

## Validation Architecture

> `workflow.nyquist_validation` is absent from `.planning/config.json` → treated as enabled. The deliverable is a ledger + bench evidence, so each LEDGER-0x / SAFE-04 requirement is made independently observable below.

### Test Framework
| Property | Value |
|----------|-------|
| Framework (firmware) | PlatformIO Unity native suite — `pio test -e native` (105/105 at Phase 89 close) |
| Framework (host) | pytest (`firestarter_app`, py3.11 CI target) |
| Config file | `firestarter/platformio.ini` `[env:native]`; `firestarter_app` pyproject + `.github/workflows/ci.yml` |
| Quick run command | `cd firestarter && pio test -e native` |
| Full suite command | `pio test -e native` + `python tools/check_dispatch.py` + `python tools/diff_db.py` |

> NB: there is no automated test for the *ledger* itself (it is a doc). The "tests" here are (a) the rerun-to-confirm frozen-world gates, and (b) a small **ledger self-consistency check** the planner should add (Wave 0 gap) — a script asserting every PASS row satisfies the D-09 structural constraint and every join key resolves into the upstream files.

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated/observable command | Exists? |
|--------|----------|-----------|------------------------------|---------|
| LEDGER-01 | Ledger has a row per bucket; join keys resolve into both upstream files; no SHA duplication | script/manual | `jq` check: every `rows[].matrix_family` ∈ `validation_matrix_spec families[].id`; every `evidence.*_cell.evidence_chip` ∈ `EVIDENCE.json cells[].chip`; assert no raw SHA strings copied | ❌ Wave 0 (write `tools/check_ledger.py` or a jq snippet) |
| LEDGER-02 | Each on-hand PASS row has `oracle: leonardo+Rev2.0` + non-empty evidence refs + SHA-match=true | script | `jq` assert: for each `verification_status=="PASS"` → `oracle=="leonardo+Rev2.0"` && `evidence.p90_artifacts \| length > 0` && both `*_matches_v115==true` | ❌ Wave 0 |
| LEDGER-02 | Bench SHA byte-identical to v1.15 baseline (the D-01 regression) | hardware (operator-gated) | `dev consistency-check`/`write-cycle` SHA == hard-coded baseline (table) | ✅ harness exists; ❌ run is bench-gated |
| LEDGER-03 | 6 no-silicon buckets `UNVERIFIED`; 3 defect rows verbatim, `status_changed:false` | script/manual | `jq` assert exactly {0x0D,0x0E,0x10,0x27,0x29,0x34} carry `UNVERIFIED`; `open_defects[].status_changed==false`; defect text matches STATE.md | ❌ Wave 0 |
| SAFE-04 | Over-voltage check present+unmodified; host guard present+unmodified; 2516 UNVERIFIED | grep + git | `grep` the +500 mV check in `primitives.cpp`; `grep support_status` in `chip_resolver.py`; `git diff --quiet` both repos; `grep` 2516 verification_status | ✅ commands exist |

### Sampling Rate
- **Per ledger edit:** rerun the `jq`/`check_ledger` self-consistency assertions (LEDGER-01/02/03 structural).
- **Per bench op:** capture SHA + compare to baseline immediately (D-03 N≥3; reseat on mismatch before recording).
- **Phase gate:** frozen-world trio green (`pio test -e native`, `check_dispatch.py`, `diff_db.py`) + both repos `git diff --quiet` + all PASS rows satisfy D-09 + all 12 buckets present.

### Wave 0 Gaps
- [ ] `tools/check_ledger.py` (or committed jq snippet) — asserts LEDGER-01 join-key resolution, LEDGER-02 D-09 PASS constraint, LEDGER-03 UNVERIFIED/defect shape. (Lives in meta-repo `.planning/v1.16/ledger/` or `firestarter_app/tools/` — planner discretion; if host-side, mind py3.11 CI.)
- [ ] `BENCH-LOG.md` template — per-task port identity / Rev confirm / command / RC / SHA / operator-authorize note (the D-09 evidence anchor).
- [ ] No new framework install needed (harness exists).

*(No firmware/host *source* tests are added — D-10 frozen world; the only new "test" is the doc self-consistency checker.)*

## Security Domain

> `security_enforcement` not set to `false` in config → included. This phase writes no code and adds no input surface; the relevant control is the **physical-safety SAFE-04 guard chain**, not classic app-sec.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes (carried, not changed) | Host `resolve_chip` support-status guard refuses non-`supported` chips before any serial byte; firmware over-voltage VPP gate (+500 mV) blocks write/erase. Both VERIFY-present-only this phase. |
| V6 Cryptography | no | SHA-256 used only as a content fingerprint (integrity oracle), not a security control — `hashlib`, never hand-rolled. |
| V2/V3/V4 Auth/Session/Access | no | No network/auth surface. |

### Known Threat Patterns for this phase
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Over-voltage on a 5V part (hardware damage) | Tampering/DoS (physical) | Firmware `vpp_check_window` +500 mV gate (primitives.cpp:106) — verify present+unmodified; SAFE-04. |
| Driving a non-supported chip (12V on wrong pin) | Tampering (physical) | Host `resolve_chip` guard fires before wire dict built — verify present+unmodified. |
| Spending the irreplaceable 2516 on an unstable read path | Loss of asset | 2516 stays UNVERIFIED; no write/preserve on unstable read (D-08/SAFE-04). |
| Recompose regression silently shipped | (process) | D-01 regression-match-to-baseline + D-03 never-auto-pass a mismatch. |

## Sources

### Primary (HIGH confidence — read directly this session)
- `.planning/phases/90-per-protocol-bench-validation-ledger/90-CONTEXT.md` — D-01..D-10, scope.
- `.planning/REQUIREMENTS.md` — LEDGER-01/02/03, SAFE-04 + traceability.
- `.planning/v1.15/bench/EVIDENCE.json` — baseline SHAs, cell schema, phase82/83/84 blocks, open-defect dispositions.
- `firestarter/doc/PROTOCOLS.md` — 12-bucket §0 table, §1 per-bucket facets, §3 INV matrix, NAME-04 FM1608/X88C64.
- `firestarter/datasheets/README.md` — datasheet folder slugs + UNVERIFIED rep chips + provenance.
- `firestarter/src/proms/primitives.{cpp}` — P3/P4/P5 caller map + the +500 mV over-voltage check (primitives.cpp:106).
- `firestarter_app/tools/validation_matrix_spec.json` — family entries (decimal protocols), join keys.
- `firestarter_app/tools/gen_test_image.py` — seed convention + deterministic generator.
- `firestarter_app/firestarter/cli_handlers.py` — `dev consistency-check` / `dev write-cycle` signatures.
- `firestarter_app/firestarter/chip_resolver.py` — host support-status guard.
- `.planning/phases/89-incremental-primitive-recompose/89-FLASH-LEDGER.md` — flash deltas, firmware HEAD a296195, SAFE-04 table.
- `.planning/STATE.md` — deferred-items table (CR-01/FUT-03/FUT-06/FUT-01 dispositions), Phase-90 posture.
- `firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md`, `./CLAUDE.md` — build/flash, dispatch order, env.

### Secondary (MEDIUM — user auto-memory, cross-checked with EVIDENCE)
- `project_uno328pb_bench_instability_27_04`, `user_shield_revisions`, `feedback_verify_port_identity_each_task`, `feedback_chip_out_before_sideload`, `reference_usb_passthrough_bench`, `reference_devcontainer_py312_masks_ci_py39`, `reference_firestarter_app_python_test_env`, `reference_gsd_sdk_in_devcontainer`.

### Tertiary (LOW)
- None — no web/external lookups; this phase is fully grounded in-repo.

## Metadata

**Confidence breakdown:**
- Upstream schemas + join keys: HIGH — both files read; keys confirmed present in both.
- Baseline SHAs: HIGH — copied verbatim from EVIDENCE.json cells.
- 12-bucket identities + primitives map: HIGH — PROTOCOLS.md + primitives.cpp caller header read directly.
- Bench commands: HIGH — CLI signatures + v1.15 method read directly; chip CLI names A2 (medium for 2 of 4).
- SAFE-04 locations: HIGH — corrected to post-recompose primitives.cpp:106 by direct grep.
- Bench *outcomes*: N/A — hardware-gated, produced during execution.

**Research date:** 2026-06-26
**Valid until:** 2026-07-26 (stable — in-repo artifacts; invalidated only if a chip is rewritten or the firmware HEAD moves off a296195)
