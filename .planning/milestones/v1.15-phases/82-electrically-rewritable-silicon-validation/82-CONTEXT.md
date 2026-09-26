# Phase 82: Electrically-Rewritable Silicon Validation - Context

**Gathered:** 2026-06-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Prove the on-paper `supported` claim on **real silicon** for the **8 electrically-rewritable
chips** via full **write → (auto-erase) → read → verify with SHA match**, on **Leonardo +
RURP Rev 2.0 ONLY**, confirming the DB decode matches observed behaviour and that auto-erase
is correct for both the `EEPROM` and `Flash/EEPROM` electrical types.

**The 8 chips (5 families):**
- **0x07 EEPROM, 12V:** W27C512, W27E512, SST27SF512 — write→auto-erase→read→verify (REWR-01)
- **0x08 EEPROM, 512KB:** W27E040 — write→read→verify (REWR-02)
- **0x06 flash3 (AMD-style):** SST39SF040 — write→read→verify (REWR-03)
- **0x05 flash4 (Winbond), `Flash/EEPROM`:** W29C020, W29C040 — write→read→verify + auto-erase
  confirmed for the `Flash/EEPROM` type (REWR-04)
- **0x40 FRAM, overwrite/no-erase:** FM1608 — write→read-back→verify (REWR-05)

Plus **DB-01**: for every chip exercised, confirm the DB-recorded decode (pinout, VPP,
electrical type, algorithm, size) against real-silicon behaviour; flag any mismatch in the
evidence record.

**Out of scope:** the 3 UV-EPROMs (ST M27C512, AM27C020, 2516 — Phase 83 spend-vs-preserve,
gated on the Phase 81 blank-state); the consolidated decode-correctness audit + conditional
defect RCA (Phase 84 / FIX-01); the 2516 VPE-rail write proof (Phase 83 / GRAD-03); the v1.9
read-bug RCA (deferred). No new harness or third-party dependency (EVID-02). No firmware
change in this phase (see D-01 — CR-01 is deferred to Phase 84 if it fires).
</domain>

<decisions>
## Implementation Decisions

### W29C020 flash4 page-size known-risk (CR-01) — attempt as-is, defer any fix to Phase 84
- **D-01:** **Run W29C020 write→verify on the CURRENT firmware as-is.** The pending todo
  `flash4-page-size-datasheet-sourced-cr01` documents that the firmware's
  `flash4_page_size(mem_size)` heuristic **under-sizes the page for W29C020** (256KB → guesses
  128B; real datasheet page is 256B) — the *exact* mid-page-poll write failure mode Phase 74
  fixed for the W29C040. **W29C040 (512KB) is correct under the heuristic; W29C020 (256KB) is
  not.** If W29C020 fails mid-page-poll, record **FAIL with the CR-01 root-cause noted** in
  EVIDENCE and hand it to **Phase 84 (conditional defect RCA + FIX-01)** — do NOT fold the
  CR-01 fix into Phase 82. Rationale: keeps Phase 82 **host-only / no-firmware-scope**, matches
  the milestone's "validate on silicon first, RCA in Phase 84" ordering, and the proper CR-01
  fix is non-trivial (DB `page_size` field + host codegen + `configure_flash4` handle plumb +
  Leonardo flash-budget check at ~89.5%).
- **D-02:** The planner MUST pre-record the CR-01 risk against W29C020 in the plan so a failure
  is **expected and pre-attributed**, not a surprise — and so the EVIDENCE row can carry the
  root-cause pointer immediately rather than waiting for Phase 84 triage.

### Write payload / test image — full-size deterministic pseudo-random per chip
- **D-03:** Each chip's write→verify uses a **full-chip-size deterministic pseudo-random image**
  (fixed seed for reproducibility), generated per chip to the exact `size_bytes`. Rationale:
  exercises every address line + full paging, produces a non-trivial SHA, and **guarantees real
  bit transitions over the non-blank current contents** recorded in Phase 81 (an all-`0xFF`
  image would not prove writes actually landed). `dev write-cycle <chip> <source_image>`
  **requires** a SOURCE_IMAGE argument, so the image is a concrete per-chip artifact the plan
  must produce.
- **D-04 (Claude's discretion):** Exact generator (seed scheme, tool — e.g. a tiny repo helper
  vs `head -c <size> /dev/urandom` captured to a file for reproducibility) and where the images
  are stored is the planner's call, provided each is full-size, deterministic/recorded, and
  non-trivial (not uniform `0xFF`/`0x00`).

### Auto-erase confirmation — explicit A→B rewrite for ALL 8 chips
- **D-05:** Auto-erase / overwrite correctness is confirmed by an **explicit two-image A→B
  rewrite on every one of the 8 chips** (not just the flash4 pair): write image **A**, verify A;
  then write image **B** (full-size, distinct seed) **without an explicit erase step**, verify B
  reads back clean. If auto-erase did NOT fire, residual A-bits would survive and break B's SHA
  — so a clean B verify is **positive proof** the erase/overwrite happened. This directly
  satisfies REWR-04 SC#3 ("auto-erase confirmed correct for the `Flash/EEPROM` type") and is the
  gold-standard erase proof. Operator chose the uniform-for-all-8 protocol over flash4-only.
- **D-06:** The A→B proof is interpreted per electrical type but the procedure is identical:
  - `EEPROM` (0x07, 0x08) + `Flash/EEPROM` (0x05) + flash3 (0x06) → A→B proves **auto-erase**.
  - **FM1608** (0x40 FRAM, no erase) → A→B proves clean **overwrite** (REWR-05's intent). FRAM
    has no erase cycle; the same A→B read-back confirms B fully replaced A.
- **D-07:** The A→B rewrite roughly doubles write cycles per chip; accepted because all 8 are
  electrically rewritable (zero consumption risk, unlike the Phase 83 UV parts).

### Write-failure disposition — reseat + retry, record, continue → Phase 84
- **D-08:** Extend Phase 81 D-06/D-07 to the write path: on a failed write→verify, **reseat the
  chip + retry up to N=2**, then if still failing **record FAIL (genuine defect) or ANOMALY
  (flaky/contact) in EVIDENCE and CONTINUE the sweep** — the rewritable chips are safe to retry
  and re-write. Genuine defects (incl. an expected W29C020 CR-01 failure per D-01) are **flagged
  for Phase 84 FIX-01, not root-caused inline**. Do NOT halt the phase on the first FAIL — full
  coverage of the remaining chips is more valuable than inline RCA.
- **D-09 (Claude's discretion):** Retry count default N=2 (planner may refine), consistent with
  Phase 81 D-07. FAIL-vs-ANOMALY verdict wording carries the Phase 81 EVIDENCE column semantics.

### Carried forward from Phase 81 / milestone (locked — not re-discussed)
- **D-10:** **Board = Leonardo + RURP Rev 2.0 ONLY** is authoritative for any write/verify
  (SAFE-01/03; v1.9 read-bug corrupts the oracle elsewhere; uno328pb is N/A for program/write —
  brownout 999.2). Per task: verify `controller:` port identity after any USB event, live
  `r1 ≈ 270000` readback, **ASK the operator which silkscreen shield rev is mounted** (EEPROM
  byte can't distinguish revs). Leonardo is **chip-OUT-sideload-EXEMPT**.
- **D-11:** **SAFE-02** — host suite green **including the 0xA4 `ack_data=False` guard**
  (`test_init_phase_data_frames_not_acked`) before any bench session; validate `ruff check` +
  `ruff format --check` against the CI target (devcontainer Py3.12 masks CI py3.9/3.11).
- **D-12:** **Reuse-first, no new harness (EVID-02):** `dev write-cycle` (Erase→write→read-back
  N times, asserts SHA-256 == source, 3-way verdict 0/1/2), `dev validate-family`,
  `write_test.sh`; existing gates `check_dispatch.py` / `diff_db.py`. The one new artifact is
  the per-chip EVIDENCE — see D-13.
- **D-13:** **EVIDENCE.{md,json}** at `.planning/v1.15/bench/` **extends (not replaces)** the
  v1.13 per-family matrix and the Phase 81 rows; carries the locked columns (chip,
  family/algorithm, board+shield, blank/prior-state, op, SHA-or-N/A, verdict, anomalies) and may
  extend them. Phase 81 already scaffolded this artifact — Phase 82 appends the write rows.
- **D-14:** **Non-vacuous PASS bar (EVID-03, locked):** every PASS proven by a trustworthy
  Leonardo read (**N≥3 byte-identical / SHA-matched**) plus a **negative control** (a wrong-file
  `verify` exits non-zero). The Phase 81 negative control fired (RC=1) — re-apply the same.

### Claude's Discretion
- Exact pseudo-random image generator + seed scheme + storage location (D-04).
- Reseat/retry count default (D-09, N=2 baseline) and FAIL-vs-ANOMALY column wording.
- Whether to drive writes via `dev write-cycle` (per-chip, explicit source image — natural fit
  for the A→B protocol) vs `dev validate-family <family> --source` (matrix-oriented). The A→B
  two-image protocol (D-05) maps most directly to two `dev write-cycle` invocations per chip.
- Per-chip vs single shared negative control (Phase 81 fired one; either satisfies EVID-03).
- Write/verify order across the 8 chips (all rewritable → low-stakes; planner's call).

### Folded Todos
- **`flash4-page-size-datasheet-sourced-cr01` (CR-01)** — folded as a **known pre-write risk
  against W29C020**, NOT as a fix to implement. Per D-01/D-02 the plan pre-records the risk and
  any W29C020 mid-page-poll failure is attributed to CR-01 and handed to Phase 84. The todo's
  `resolves_phase` stays null/Phase-84 — Phase 82 only *observes and attributes*, it does not
  fix. (W29C040, the heuristic-correct 512KB representative, is unaffected.)
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & requirements
- `.planning/ROADMAP.md` §"Phase 82: Electrically-Rewritable Silicon Validation" — goal + 5
  locked success criteria; §"Non-destructive-first safety ordering" + §"Bench discipline"
- `.planning/REQUIREMENTS.md` — REWR-01..05, DB-01 (Phase 82 reqs); EVID-01/02/03 (Phase 81,
  the evidence/non-vacuous/reuse contract that recurs here); DB-02 (Phase 81, FLAG_CAN_ERASE)
- `.planning/PROJECT.md` §"Current Milestone: v1.15" — milestone goal + board lock +
  inventory-already-supported framing
- `.planning/STATE.md` §"Standing bench precondition" — Leonardo+Rev2.0-only, `r1 ≈ 270000`,
  port-identity-per-task, ASK silkscreen rev, reuse-first, EVIDENCE artifact path

### Prior phase context (directly load-bearing)
- `.planning/phases/81-2516-db-entry-non-destructive-read-sweep/81-CONTEXT.md` — read-sweep
  decisions, evidence schema, reseat/retry/ANOMALY pattern (D-06/D-07), SAFE-01/02/03 framing
  (D-11), non-vacuous bar; **the prior-state of all 8 chips recorded here is the A→B starting
  point** (chips are non-blank → writes prove real transitions)
- `.planning/phases/77-erase-write-path-graduation-0x07-ee-eproms/77-CONTEXT.md` — the
  FLAG_CAN_ERASE wiring + 0xA4 `ack_data=False` regression test (prior art for the erase path)

### v1.15 research (milestone-level)
- `.planning/research/SUMMARY.md` — exec summary; Flag #1 (FLAG_CAN_ERASE Flash/EEPROM), Flag #2
  (0xA4 regression)
- `.planning/research/FEATURES.md` — the 11-chip / 5-family breakdown
- `.planning/research/PITFALLS.md` — false-PASS oracle, reseat-on-0xFF, port-identity drift,
  VPP-warning-during-read gotcha
- `.planning/research/STACK.md` — zero-new-deps; reuse `write_cycle_eprom` / `dev
  validate-family` / `write_test.sh`
- `.planning/research/ARCHITECTURE.md` — Leonardo preconditions, evidence schema

### The flash4 page-size risk (CR-01 — W29C020 attempt-as-is, D-01)
- `.planning/todos/pending/flash4-page-size-datasheet-sourced-cr01.md` — full CR-01 finding +
  per-family page-size table + WR-04 paired test gap
- `firestarter/src/proms/flash_type_4.cpp` (~lines 27–31) — `flash4_page_size(mem_size)`
  heuristic (the under-sizing source) + the page-write/poll loop
- `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` — hard-codes
  `mem_size = 524288` (the one correct capacity), greenlights while CR-01 is live (WR-04)
- `.planning/phases/74-per-family-correctness-fixes-flash-gated/74-REVIEW.md` — CR-01/WR-01..04
  origin

### Write/verify tooling (reuse — EVID-02)
- `firestarter_app/firestarter/cli_handlers.py` — `dev write-cycle` (~1139, Erase→write→read-back
  N, SHA assert, 3-way verdict 0/1/2), `dev validate-family` (~1419), `dev consistency-check`
  (~1049, the read oracle)
- `firestarter_app/firestarter/eprom_operations.py` — `write_cycle_eprom` (~766),
  read/verify/blank-check paths
- `firestarter_app/write_test.sh` / `firestarter_app/firestarter_test.sh` — integration scripts
- `firestarter_app/firestarter/chip_resolver.py` — `resolve_chip` (host guard; the 8 chips must
  all pass as `supported`)

### DB decode confirmation (DB-01) + safety gates
- `firestarter_app/firestarter/data/chip_database.json` — the DB-recorded decode for each of the
  8 chips (pinout, vpp_mv, electrical.type, algorithm, size_bytes) to confirm vs silicon
- `firestarter_app/firestarter/data/pinouts.json` — per-chip DIP pin → RURP bus mapping
- `firestarter_app/tools/check_dispatch.py` + `tools/diff_db.py` — full-DB VPP-safety + per-chip
  diff gates (all 8 are built-in chips, so these gates DO cover them — unlike the 2516 override)
- `firestarter_app/firestarter/constants.py` ↔ `firestarter/include/firestarter.h` —
  `FLAG_CAN_ERASE` (0x02) parity (SAFE-03 if ever touched; no constant change anticipated)

### Standing bench precondition (EVERY hardware task — SAFE-01)
- `.planning/STATE.md` §"Standing bench precondition" + `.planning/ROADMAP.md` §v1.15 "Bench
  discipline" — Leonardo + Rev 2.0 only authoritative; `r1 ≈ 270000`; verify `controller:` port
  identity per task; ASK silkscreen shield rev; host suite green incl. 0xA4 guard before session
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `dev write-cycle <chip> <source_image> [--runs N] [-f]` — Erase→write→read-back N cycles,
  asserts SHA-256 == source SHA, emits per-cycle binaries; **3-way verdict (0=PASS/1=mismatch/
  2=hw-error)**. The natural substrate for both the write→verify and the A→B two-image proof
  (D-05): run it twice per chip with image A then image B. **Requires** an explicit source image
  (drives D-03).
- `dev consistency-check --runs 3` — the non-destructive read oracle used in Phase 81 for the
  N≥3 byte-identical read (EVID-03 non-vacuous bar).
- `dev validate-family <family> --source <image>` — per-family Tier-3 matrix runner (composes
  `write_cycle_eprom`/`consistency_check_eprom`); Leonardo-only authoritative PASS, r1 gate,
  SKIP-deferred when no board/source. An alternative driver if a family-matrix shape is wanted.
- The Phase 81 EVIDENCE.{md,json} scaffold + the v1.13 per-family matrix — extend, don't replace.

### Established Patterns
- All 8 chips are **built-in DB entries** (generated by `build_db.py`) → `check_dispatch.py` /
  `diff_db.py` **DO cover them** (contrast the 2516 user-override which bypasses both). DB-01 is
  a real-silicon confirmation of an already-gated decode.
- DB regen is `python3 tools/build_db.py`; do NOT hand-edit `chip_database.json`. No DB change
  is anticipated in Phase 82 (validation-only) unless DB-01 surfaces a decode mismatch → then
  it's a Phase 84 disposition, not an inline edit.
- Tooling gate: `ruff check` + `ruff format --check` + `mypy` (strict 8 modules) +
  `pytest --cov-fail-under=70`; **devcontainer Py3.12 masks CI py3.9/3.11** — validate ruff
  against the target before claiming green.

### Integration Points
- `electrical.type` → `_map_data` (`info-flags`/`electrical-type`) → `convert_to_programmer`
  (`FLAG_CAN_ERASE`) → wire JSON `flags` → firmware `eprom_write_init` guard — the path the A→B
  auto-erase proof (D-05) exercises end-to-end on silicon (DB-02 re-audited this in Phase 81;
  Phase 82 is the FIRST bench proof of the `Flash/EEPROM` branch via W29C020/W29C040).
- flash4 write path: host wire → firmware `configure_flash4` → `flash_type_4.cpp` page loop
  using `flash4_page_size(mem_size)` — the CR-01 under-sizing site for W29C020 (D-01).
</code_context>

<specifics>
## Specific Ideas

- The operator chose the **most rigorous uniform protocol** — explicit A→B rewrite on **all 8**
  chips, not just the flash4 pair — because the chips are freely rewritable so the extra cycles
  cost nothing but buy gold-standard auto-erase/overwrite proof.
- The operator explicitly wants Phase 82 to **stay host-only / no-firmware-scope**: the known
  W29C020 CR-01 page-size bug is to be *observed and attributed*, with the actual fix living in
  Phase 84 — Phase 82 validates silicon, Phase 84 RCAs/fixes defects.
- Full coverage beats inline RCA: a failing chip is reseated/retried, recorded, and the sweep
  continues — never halt on first FAIL.
</specifics>

<deferred>
## Deferred Ideas

- **CR-01 proper fix** (datasheet-sourced flash4 `page_size`: DB field + host codegen +
  `configure_flash4` handle plumb + `flash4_page_size()` removal + WR-04 parameterized test) —
  Phase 84 FIX-01 *if* the W29C020 bench failure fires (conditional defect RCA). Dual-repo
  lockstep firmware change; confirm Leonardo stays under the flash ceiling (~89.5%).
- **3 UV-EPROM write proofs** (ST M27C512, AM27C020, 2516 spend-vs-preserve; 2516 VPE-rail proof
  closing FUT-03) — Phase 83, gated on the Phase 81 blank-state. **2516 read is currently
  UNSTABLE** (3 distinct SHAs / VPP instability per Phase 81) — Phase 83 must not write it until
  reads stabilize.
- **Consolidated decode-correctness audit + conditional defect RCA + milestone evidence
  consolidation** — Phase 84.
- **skip-vpp-error/warning-on-reads todo** (`resolves_phase: 84`) — not folded; it targets the
  read/blank-check VPP gate (Phase 81 anomaly). The verify-read step of Phase 82's
  write→read→verify is a read where VPP should be off, so the Phase 81 boot-VPP-refusal gotcha
  (board RESET clears it) may surface — handle operationally, not via a fix here.

### Reviewed Todos (not folded)
- `avrdude-mcu-detection-fallback` — off-board recovery tooling, unrelated to Phase 82.
- `cobs-decoder-framelevel-deadline-wr01` — transport-layer firmware item, unrelated.

None of the above are scope creep — they are explicitly later phases / future items.
</deferred>

---

*Phase: 82-electrically-rewritable-silicon-validation*
*Context gathered: 2026-06-24*
