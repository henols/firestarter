---
phase: 86-variant-decode-correct-db-regen
plan: 02
subsystem: build-tooling
tags: [build_db, classify, infoic.xml, variant-decode, diff_db, check_dispatch, chip-database, host-only]

# Dependency graph
requires:
  - phase: 86-variant-decode-correct-db-regen
    plan: 01
    provides: "DECODE-NOTES.md (classify() spec) + refactor-under-test oracle (FM1608/X88C64/EVIDENCE-11) + pinned minipro SHA a8efaedc"
provides:
  - "build_db.py classify(type,proto,pm_idx,flags,pinout,mem_size) — the SOLE classifier; Rule 1/2/3 + two-pass _etype deleted"
  - "regenerated chip_database.json (744 chips) — FM1608 0x28/FRAM/DIP28_JEDEC_SRAM_8K, X88C64 EEPROM (proto-not-implemented), W27C512 stable, AT29C256 stable"
  - "diff_db.py VARIANT_DECODE rule label + cited rationale (database.c#L1918 / minipro.h#L70) — explains the regen diff vs OLD baseline (exit 0)"
  - "tools/variant-decode-diff.txt — explained-diff transcript (PASS: all 72 changed chips explained)"
affects: [86-03-baseline-repin, 86-04-non-upstream-supplement, 87-naming-pass]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single principled classifier: (electrical.type, algorithm, pinout) derived once from type/proto/pm_idx/flags — no override stack (variant HIGH byte deliberately not a classification input)"
    - "Override-scope-preservation: each deleted rule's exact predicate folded into one classify() arm; arm-2 scoped to EPROM-family proto to avoid moving genuine flash"
    - "Cited diff-rule consolidation label (VARIANT_DECODE) scoped by new-type+proto so it does not shadow the narrower BUG_A_ETYPE / part_number-scoped PHASE84 labels"

key-files:
  created:
    - firestarter_app/tools/variant-decode-diff.txt
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/tools/diff_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "classify() arm-2 (5V-EEPROM pinout clusters) scoped to EPROM-family proto (0x07/0x08/0x0B) for DIP28 clusters and any-proto only for DIP24_2816 — exactly the deleted Rule 1 + Rule 2 scope; prevents the genuine 5V-flash AT29C256/AT29LV256 (proto 0x05) from being mis-flipped to 0x0D"
  - "MINIPRO_XML_URL pinned from /-/raw/master/ to /-/raw/a8efaedc.../ (DECODE-NOTES.md §3, D-05 discretion) for a deterministic, reproducible fetch"
  - "VARIANT_DECODE diff label scoped to type-only changes where new type==EEPROM AND proto in {0x0D,0x34} — claims the 66 proto-0x0D Flash/EEPROM->EEPROM rows + X88C64P proto-0x34 UV-EPROM->EEPROM without shadowing BUG_A_ETYPE or RULE_PHASE84_RELABEL"
  - "Baseline NOT re-pinned (deferred to Plan 86-03 by design); diff runs vs the OLD baseline and is fully explained"

patterns-established:
  - "Override-stack collapse with exact-scope preservation verified by a vs-pre-regen algorithm-stability check (0 algorithm changes) in addition to the vs-OLD-baseline explained diff"

requirements-completed: [VAR-02, VAR-03, VAR-04]

# Metrics
duration: 38min
completed: 2026-06-25
---

# Phase 86 Plan 02: Principled classify() + Correct DB Regen Summary

**Replaced the build_db.py Rule 1 / Rule 2 (WARNING-5) / Rule 3 override stack and the two-pass `_etype` derivation with one principled `classify(type,proto,pm_idx,flags,pinout,mem_size)` keyed on minipro's own classification fields; regenerated chip_database.json (744 chips) so FM1608 (0x28/FRAM) and X88C64 (EEPROM) fall out of the general decode; extended diff_db.py with a cited VARIANT_DECODE label that fully explains the regen diff vs the OLD baseline; and proved check_dispatch.py 0 violations + EVIDENCE-11 wire-stability (zero chips moved).**

## Performance

- **Duration:** ~38 min
- **Completed:** 2026-06-25
- **Tasks:** 3
- **Files modified:** 4 (1 created, 3 modified) inside the `firestarter_app` submodule

## Accomplishments

- **VAR-02 — Override-stack collapse.** Added `classify()` to `build_db.py` as the sole classifier (returns `(etype, algorithm, pinout)`); deleted the inline Pass-1 flags-based `_etype`, Rule 1 (DIP24_2816 force 0x0D), Rule 2 (WARNING-5 5V-EEPROM-pinout flip), Rule 3 (type=4 SRAM/FRAM → 0x28 + pinout re-route), and Pass-2 protocol-aware `_etype`. `grep` over non-comment code returns no `Rule 1:` / `Rule 2 WARNING-5` / `Rule 3:` markers. `resolve_pinout_key` (variant LOW byte) is unchanged; Site A/B, the AT28C named arm, NMOS Site C, the Phase-84 FM1608→FRAM relabel, and SRAM vcc-normalization are all preserved.
- **classify() arm order** (per RESEARCH §"Recommended classifier shape"): (1) SRAM/FRAM/NVRAM — `type==4` or SRAM-family proto → algorithm 0x28 when arrived with EPROM-family proto, plus the Rule-3 28-pin pinout re-route; (2) 5V-EEPROM pinout clusters → EEPROM/0x0D (DIP24_2816 any-proto; DIP28_28C64/28C256/2764+flags only for EPROM-family proto); (3) EPROM-family proto → EEPROM if flags&0x10 else UV-EPROM; (4) Flash families → Flash/EEPROM; (4b) X88C64 `proto==0x34` → EEPROM (display-only); (5) default UV-EPROM.
- **VAR-03 — Correct DB + explained diff.** Regenerated `chip_database.json` (744 chips). FM1608 → algorithm 40 (0x28) / FRAM / DIP28_JEDEC_SRAM_8K; X88C64 → electrical.type EEPROM / support_status protocol-not-implemented; W27C512 stays 0x07 / EEPROM / DIP28_27512. Extended `diff_db.py` with the `VARIANT_DECODE` rationale (citing `database.c#L1918` algo_number + `minipro.h#L70` MP_SRAM, cross-ref DECODE-NOTES.md), a `_RULE_FIELD_PATHS` entry, and priority-chain wiring before `BUG_A_ETYPE`. `python tools/diff_db.py` exits 0: **PASS: all 72 changed chips explained** (transcript at `tools/variant-decode-diff.txt`).
- **VAR-04 — Safety gate.** `python tools/check_dispatch.py` → `0 dispatch regressions; 0 consistency violations` on the regenerated DB (D-08, file unchanged). `pytest tests/test_build_db_inclusion.py tests/test_variant_decode_evidence_stability.py` → 22 passed: X88C64 inclusion test now GREEN (Plan-01 gap closed), FM1608 GREEN, and the D-09 EVIDENCE-11 wire-stability oracle GREEN (all 10 upstream-decoded chips unchanged vs OLD baseline; 2516 excluded → Plan 86-04).
- **MINIPRO_XML_URL pinned** to the SHA `a8efaedc` (DECODE-NOTES.md §3, D-05) so the fetch and the eventual baseline re-pin are deterministic/reproducible.

## Task Commits

Each task committed atomically inside the `firestarter_app` submodule on branch `v1.16-protocol-first-architecture-rebuild`:

1. **Task 1: classify() replaces Rule 1/2/3 + regen DB + MINIPRO_XML_URL pin** — `cab9349` (feat)
2. **Task 2: VARIANT_DECODE diff label + explained-diff transcript** — `46efe6e` (feat)
3. **Task 3: arm-2 scope fix (Rule-1 bug) + VAR-04 gate proof + golden snapshot** — `16fd2e2` (fix)

## Files Created/Modified

- `firestarter_app/tools/build_db.py` (modified) — added `classify()`; deleted Rule 1/2/3 + two-pass `_etype`; pinned `MINIPRO_XML_URL`.
- `firestarter_app/firestarter/data/chip_database.json` (modified) — regenerated, 744 chips.
- `firestarter_app/tools/diff_db.py` (modified) — `VARIANT_DECODE` rationale + field paths + priority wiring.
- `firestarter_app/tools/variant-decode-diff.txt` (created) — explained-diff transcript (exit 0).
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` (modified) — `test_list` golden updated for the type-only flips (downstream of the legitimate regen).

## Decisions Made

- **classify() arm-2 scope preservation (the Task-3 bug fix).** The first cut of arm-2 flipped *any* chip on `DIP28_28C256`/`DIP28_28C64` to algorithm 0x0D; that mis-moved the two genuine Atmel 5V-flash parts **AT29C256 / AT29LV256** (proto 0x05) from Flash/0x05 → EEPROM/0x0D — an algorithm change the deleted Rule 2 never made (Rule 2 keyed on `proto==0x07`). Fix: scope the DIP28 cluster flip to EPROM-family proto (0x07/0x08/0x0B); keep DIP24_2816 as any-proto (exact old Rule 1). Verified by a vs-pre-regen check: **0 algorithm changes** caused by the regen.
- **VARIANT_DECODE label scope.** Keyed on type-only delta where new type==EEPROM and proto in {0x0D, 0x34}. This claims exactly the consolidation rows (66 proto-0x0D Flash/EEPROM→EEPROM + X88C64P proto-0x34 UV-EPROM→EEPROM) and never shadows genuine `BUG_A_ETYPE` (flags-based 0x07 reclassification) or the part_number-scoped `RULE_PHASE84_RELABEL` (FM1608 SRAM→FRAM).
- **Variant HIGH byte not wired into classification** (DECODE-NOTES.md §2): it is minipro's T56/T76 `algo_number`; classify() keys on type/proto/pm_idx/flags only.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] classify() arm-2 mis-flipped genuine 5V flash (AT29C256/AT29LV256) to algorithm 0x0D**
- **Found during:** Task 3 verification (golden-matrix proto-count drift 0x05 27→25, 0x0D 84→86 surfaced an unexpected *algorithm* move).
- **Issue:** The initial arm-2 condition (`pinout_key in {DIP24_2816, DIP28_28C64, DIP28_28C256}` regardless of proto) broadened the deleted Rule 2's scope. Rule 2 only flipped `proto==0x07` chips on those DIP28 pinouts; the genuine Atmel 5V flash AT29C256/AT29LV256 (proto 0x05) on `DIP28_28C256` got wrongly forced to 0x0D.
- **Fix:** Split arm-2 — `DIP24_2816` forces 0x0D for any proto (Rule 1), but `DIP28_28C64`/`DIP28_28C256`/(`DIP28_2764` + flags&0x10) flip **only** EPROM-family proto (0x07/0x08/0x0B) (Rule 2). Regenerated DB now shows **0 algorithm changes** vs pre-regen.
- **Files modified:** `firestarter_app/tools/build_db.py`, `firestarter/data/chip_database.json`.
- **Commit:** `16fd2e2`.

**2. [Rule 1 - Bug] Downstream golden snapshots broke on the legitimate DB regen**
- **Found during:** Task 3 full-suite run.
- **Issue:** `test_characterization::test_list` (syrupy `.ambr`) and `test_audit_coverage_matrix::test_golden_file_matches` are byte-identity snapshots of DB-derived output; the legitimate `Flash/EEPROM→EEPROM` + X88C64 type flips changed them.
- **Fix:** Regenerated the `test_list` syrupy snapshot (`--snapshot-update`); verified the coverage-matrix golden is already byte-identical to the corrected DB when generated against the committed meta-repo ledger (no new DEFECT-COV ids minted). Confirmed every changed snapshot line is an EEPROM/FRAM type-flip — no unrelated churn.
- **Files modified:** `firestarter_app/tests/__snapshots__/test_characterization.ambr`.
- **Commit:** `16fd2e2`.

## Out-of-Scope Discoveries (NOT fixed — pre-existing)

- `ruff check` reports 4 pre-existing errors in files NOT touched by this plan (`tools/audit_coverage_matrix.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`). Confirmed present at the pre-plan commit. Left untouched per the scope boundary. The files this plan touches (`build_db.py`, `diff_db.py`) are ruff-clean + format-stable.

## EVIDENCE-11 Wire Stability (D-09)

**No EVIDENCE chip moved.** `test_upstream_evidence_wire_values_stable_vs_baseline` passes: all 10 upstream-decoded EVIDENCE chips (W27C512, W27E512, SST27SF512, W27E040/W27C040, SST39SF040, W29C020, W29C040, FM1608, ST M27C512/M27C512, AM27C020) keep `algorithm`/`vpp_mv`/`pinout` vs the OLD baseline. 2516 excluded (owned by Plan 86-04). **No Leonardo + RURP Rev 2.0 re-bench flag is required.**

## Verification Results

- Rules removed: `grep -vE '^\s*#' tools/build_db.py | grep -Ei "Rule 1:|Rule 2 WARNING-5|Rule 3:"` → nothing. ruff + format clean on build_db.py/diff_db.py.
- Task 1 gate: `CLASSIFY-OK` (FM1608 algo 40 + DIP28_JEDEC_SRAM_8K; X88C64 EEPROM + protocol-not-implemented); W27C512 0x07/EEPROM/DIP28_27512 stable; AT29C256 0x05/Flash/EEPROM stable.
- Task 2 gate: `DIFF-EXPLAINED-OK` — `python tools/diff_db.py` exit 0, `PASS: all 72 changed chips explained`; VARIANT_DECODE bucket 67 chips; transcript saved.
- Task 3 gate: `VAR04-GATE-OK` — `check_dispatch.py` `0 dispatch regressions; 0 consistency violations`; `test_build_db_inclusion.py` + `test_variant_decode_evidence_stability.py` 22 passed; X88C64 inclusion GREEN.
- Full submodule test suite: green (29 syrupy snapshots passed; all functional tests pass).
- Baseline files (`tools/baseline/*.json`) NOT modified (re-pin is Plan 86-03).
- Chip count: 744.

## Next Phase Readiness

- **Plan 86-03 (baseline re-pin):** the diff vs the OLD baseline is now fully explained (exit 0). 86-03 can re-pin `chip_database.baseline.json` (load-bearing) and `dispatch_baseline.json` (provenance) to the corrected DB. Order matters — re-pin is last (Pitfall 4).
- **Plan 86-04 (non-upstream supplement):** merges 2516/2532 AFTER this decode regen and BEFORE the 86-03 re-pin; the EVIDENCE-stability oracle already fences 2516 out of this plan.
- No blockers; no re-bench flags.

## Self-Check: PASSED

- FOUND: firestarter_app/tools/build_db.py (classify present; Rule 1/2/3 markers absent in active code)
- FOUND: firestarter_app/firestarter/data/chip_database.json (744 chips)
- FOUND: firestarter_app/tools/diff_db.py (VARIANT_DECODE present)
- FOUND: firestarter_app/tools/variant-decode-diff.txt
- FOUND commit: cab9349 (Task 1)
- FOUND commit: 46efe6e (Task 2)
- FOUND commit: 16fd2e2 (Task 3)

---
*Phase: 86-variant-decode-correct-db-regen*
*Completed: 2026-06-25*
