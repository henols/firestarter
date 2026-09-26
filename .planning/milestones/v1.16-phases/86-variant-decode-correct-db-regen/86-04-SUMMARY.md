---
phase: 86-variant-decode-correct-db-regen
plan: 04
subsystem: build-tooling
tags: [extra_chips, non-upstream-supplement, 2516, 2532, build_db, diff_db, check_dispatch, pinouts, SAFE-04, host-only]

# Dependency graph
requires:
  - phase: 86-variant-decode-correct-db-regen
    plan: 02
    provides: "classify()-based correct DB regen (744 chips); diff_db VARIANT_DECODE label exit 0; check_dispatch 0 violations; EVIDENCE-11 wire-stable (2516 excluded, owned here)"
provides:
  - "tools/extra_chips.json — curated provenance-cited non-upstream chip supplement (2516 + 2532), pure {mfg:[chips]} schema, each record carrying source=non-upstream-supplement + datasheet citation"
  - "build_db.py post-decode merge (VAR-05/D-10): extra_chips.json merged into complete_db AFTER the infoic.xml decode loop, BEFORE json.dump; supplement count reported distinctly (744 upstream + 2 = 746)"
  - "firestarter/data/pinouts.json DIP24_2532 entry — non-JEDEC 24-pin 4KB UV-EPROM (VPP=pin 21, A11=pin 18) distinct from DIP24_2732; vpp-pin satisfies GATE-03"
  - "diff_db.py EXTRA_CHIPS_SUPPLEMENT rationale + NEW-chips fencing: 2516/2532 reported as cited non-upstream-supplement rows (no WARN), exit 0 vs OLD baseline"
  - "tests/test_extra_chips_supplement.py — 8 tests pinning presence, SAFE-04 2516 wire stability + UNVERIFIED, per-record datasheet provenance, GATE-03 vpp-pin safety"
  - "regenerated chip_database.json (746 chips) containing 2516 + 2532 byte-faithful to extra_chips.json"
affects: [86-03-baseline-repin, 87-naming-pass, 89-recompose, 90-bench-ledger]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Non-upstream supplement merged post-decode: curated {mfg:[chips]} JSON merged into complete_db AFTER the infoic.xml decode and BEFORE the JSON write; records arrive fully-specified, NOT routed through classify()/resolve_pinout_key"
    - "Provenance fencing: each supplement record carries source=non-upstream-supplement + a datasheet citation so diff_db.py and tests can identify and explain it without per-part hardcoding"
    - "UNVERIFIED-via-provenance-not-guard: 2516 keeps support_status=supported (resolvable for read/info, host guard unchanged) and is marked NOT write-graduated via a verification_status=UNVERIFIED field — separating provenance status from the dispatch-refusal guard"

key-files:
  created:
    - firestarter_app/tools/extra_chips.json
    - firestarter_app/tests/test_extra_chips_supplement.py
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/tools/diff_db.py
    - firestarter_app/firestarter/data/pinouts.json
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tools/DECODE-NOTES.md
    - firestarter_app/tools/variant-decode-diff.txt
    - firestarter_app/tests/test_audit_coverage_matrix.py
    - firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "2516 UNVERIFIED expressed via verification_status field, NOT support_status — support_status stays 'supported' so the chip remains resolvable for read/info (the host guard in chip_resolver.resolve_chip refuses ANY non-'supported' chip, which would block read too). This keeps SAFE-04 (host guards intact, wire values unmoved) while honestly marking the chip non-write-graduated. The v1.15 read instability is a hardware issue (FUT-03), not a guard refusal."
  - "DIP24_2532 added as a new pinout (NOT reuse of DIP24_2732). The TI 2532 is non-JEDEC: VPP on pin 21, A11 on pin 18, !PD/PGM on pin 20 — vs the JEDEC 2732 (OE/VPP=pin 20, A11=pin 21, CE=pin 18). Conflating them is a 12-25V-to-wrong-pin hazard. vpp-pin=21 satisfies the GATE-03 structural VPP guard."
  - "extra_chips.json is a pure {mfg:[chips]} map (no top-level meta dict) so build_db.py's merge is a trivial per-manufacturer extend AND the plan's literal Task-1 gate (which iterates e.values() as chip lists) passes. Supplement-level provenance lives in per-chip source/provenance fields + the build_db.py merge comment + DECODE-NOTES §6."
  - "Baselines NOT re-pinned — deferred to Plan 86-03 by design. diff_db runs vs the OLD baseline and explains 2516/2532 as cited non-upstream-supplement NEW rows (exit 0)."

patterns-established:
  - "Downstream golden/snapshot regen for a legitimate chip-count change: a +2-chip supplement is a Rule-1/Rule-2 authorized addition, so the count-keyed coverage-matrix golden + test_summary_stats assertion (744->746) and the test_characterization list snapshot are regenerated as legitimate downstream effects (diff verified to be only the 2 new rows, no unrelated churn)"

requirements-completed: [VAR-05, SAFE-04]

# Metrics
duration: 34min
completed: 2026-06-25
---

# Phase 86 Plan 04: Non-Upstream Chip Supplement (2516 + 2532) Summary

**Shipped the two upstream-absent 24-pin oddballs (2516, 2532) first-class in `chip_database.json` via a curated, provenance-cited non-upstream supplement (`tools/extra_chips.json`) that `build_db.py` merges AFTER the infoic.xml decode loop (VAR-05 / D-10); proved the supplement rows pass the same gates as decoded chips — `check_dispatch.py` 0 violations and `diff_db.py` explains them as cited non-upstream-supplement rows (exit 0) — and pinned 2516's SAFE-04 UNVERIFIED status with its v1.15 wire values unmoved.**

## Performance

- **Duration:** ~34 min
- **Completed:** 2026-06-25
- **Tasks:** 3
- **Files:** 11 changed (2 created, 9 modified) inside the `firestarter_app` submodule

## Accomplishments

- **Task 1 — `tools/extra_chips.json` + `DIP24_2532` pinout.** Authored the curated supplement with one record each for 2516 and 2532, in the same manufacturer-keyed schema `build_db.py` emits. Each record carries an explicit non-upstream provenance marker (`source: "non-upstream-supplement"`) and a `datasheet` citation (D-11). The 2516 record's wire values match the v1.15 user-override exactly (algorithm 0x0B, pinout DIP24_2716, electrical.type UV-EPROM, vpp_mv 25000, size_bytes 2048) and carry `verification_status: "UNVERIFIED"` (resolvable for read/info, NOT write-graduated; FUT-03). Resolved the 2532 pinout: the TI 2532 is **non-JEDEC** (VPP=pin 21, A11=pin 18, !PD/PGM=pin 20) vs the JEDEC 2732, so a new `DIP24_2532` entry was added to `pinouts.json` (it differs in the VPP/A11 pin roles — reuse of DIP24_2732 would be a 12-25V-to-wrong-pin hazard). Gate: `SUPPLEMENT-AUTHORED-OK`.
- **Task 2 — post-decode merge + DB regen.** Added the `VAR-05 / D-10` merge block to `build_db.py` (and the `EXTRA_CHIPS_FILE` constant): after the per-manufacturer decode loop completes `complete_db` and before `json.dump(...)`, it loads `tools/extra_chips.json` and extends each manufacturer list (the records are NOT routed through `classify()`/`resolve_pinout_key` — they arrive fully-specified). Regenerated `chip_database.json`: **744 upstream + 2 supplement = 746 total** (count reported distinctly). The merged 2516/2532 records are byte-faithful to `extra_chips.json` (verified). Gate: `MERGE-OK`.
- **Task 3 — diff_db supplement rule + check_dispatch proof + supplement test.** Extended `diff_db.py` with an `EXTRA_CHIPS_SUPPLEMENT` rationale (cites VAR-05/D-10 + the datasheet provenance) and reworked the NEW-chips reporting path so a new chip carrying the `source="non-upstream-supplement"` marker is reported under a cited supplement label (with its datasheet + UNVERIFIED status) rather than tripping the "expected Rule 1 unblock" WARN. `python tools/diff_db.py` exits 0 with `PASS: all 72 changed chips explained`; the transcript `tools/variant-decode-diff.txt` now includes the supplement section. `python tools/check_dispatch.py` (UNCHANGED) prints `0 dispatch regressions; 0 consistency violations` with the supplement present (DIP24_2716 and DIP24_2532 both expose a vpp-pin, so the GATE-03 structural VPP guard is satisfied). Created `tests/test_extra_chips_supplement.py` (8 tests, all green). Gate: `VAR05-GATE-OK`.

## Task Commits

Each task committed atomically inside the `firestarter_app` submodule on branch `v1.16-protocol-first-architecture-rebuild`:

1. **Task 1: extra_chips.json + DIP24_2532 pinout** — `94ea3b5` (feat)
2. **Task 2: post-decode merge + DB regen (746 chips)** — `4054bfe` (feat)
3. **Task 3: diff_db supplement rule + supplement test + downstream goldens** — `5e368d1` (test)

## Files Created/Modified

- `firestarter_app/tools/extra_chips.json` (created) — 2516 + 2532 supplement records, provenance-cited.
- `firestarter_app/tests/test_extra_chips_supplement.py` (created) — 8-test supplement gate.
- `firestarter_app/tools/build_db.py` (modified) — `EXTRA_CHIPS_FILE` + post-decode merge block + distinct supplement-count reporting.
- `firestarter_app/tools/diff_db.py` (modified) — `EXTRA_CHIPS_SUPPLEMENT` rationale + NEW-chips supplement fencing.
- `firestarter_app/firestarter/data/pinouts.json` (modified) — new `DIP24_2532` entry.
- `firestarter_app/firestarter/data/chip_database.json` (modified) — regenerated, 746 chips (2516 + 2532 added).
- `firestarter_app/tools/DECODE-NOTES.md` (modified) — §6 records the implemented merge + UNVERIFIED posture.
- `firestarter_app/tools/variant-decode-diff.txt` (modified) — transcript refreshed with the supplement section.
- `firestarter_app/tests/test_audit_coverage_matrix.py` (modified) — `744`→`746` count assertion + docstring note.
- `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` (modified) — regenerated golden (746 total; 0x0B 30→32).
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` (modified) — `list` snapshot (+2516/+2532 only).

## Decisions Made

- **2516 UNVERIFIED via `verification_status`, not `support_status`.** The host guard (`chip_resolver.resolve_chip`) refuses **every** chip whose `support_status != "supported"` — including read. The v1.15 2516 user-override was `supported` (it was read-tested; the read jitter is a hardware/silicon issue, FUT-03, not a guard refusal). To keep 2516 "resolvable but not write-graduated" (D-11) while honoring SAFE-04 (host guards intact, wire values unmoved), `support_status` stays `"supported"` and a separate `verification_status: "UNVERIFIED"` field records the non-graduation. This avoids silently moving the wire posture and avoids breaking read resolvability.
- **`DIP24_2532` is a new pinout, not a DIP24_2732 reuse.** The 2532's VPP (pin 21) and A11 (pin 18) pin roles differ from the JEDEC 2732 (OE/VPP=pin 20, A11=pin 21). Modeled the 2532's true map (vpp-pin=21, ce-pin=20, A11 on the address bus at pin 18). Datasheet provenance: the committed `2516_EPROM.pdf` is the TI 2500-series UV-EPROM family scan covering the 2516/2532 lineage. The scan is image-only (no extractable text), so the pin map is grounded in the well-established TI 2532 family pinout; the row carries the UNVERIFIED posture (no on-hand 2532 bench proof) and the new pinout is marked tentative pending bench validation.
- **`extra_chips.json` is a pure `{mfg:[chips]}` map.** No top-level meta dict — supplement-level provenance lives in per-chip `source`/`provenance` fields, the `build_db.py` merge comment, and DECODE-NOTES §6. This keeps the merge a trivial per-manufacturer `extend` and lets the plan's literal Task-1 gate (which iterates `e.values()` as chip lists) pass.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Downstream count-keyed goldens broke on the legitimate 744→746 DB regen**
- **Found during:** Task 3 full-suite run.
- **Issue:** Adding 2 supplement chips moved the live DB total 744→746, breaking three byte-identity / count-keyed downstream tests: `test_audit_coverage_matrix::test_summary_stats` (hardcoded `744` assertion), `test_audit_coverage_matrix::test_golden_file_matches` (byte-identical golden), and `test_characterization::test_list` (syrupy snapshot of the DB list output).
- **Fix:** Updated the `test_summary_stats` assertion `744`→`746` (+ docstring note; in-scope 0x07+0x08 count stays 297 because the supplement is 0x0B, only the full-DB total and 0x0B histogram 30→32 move); regenerated the coverage-matrix golden byte-identically (seeding the tmp ledger from the committed meta-repo ledger exactly as `test_golden_file_matches` does); regenerated the `test_list` syrupy snapshot. Verified the snapshot diff is **only** the 2 new 2516/2532 rows (no unrelated churn).
- **Files modified:** `tests/test_audit_coverage_matrix.py`, `tests/golden/v1.3-COVERAGE-MATRIX.md`, `tests/__snapshots__/test_characterization.ambr`.
- **Commit:** `5e368d1`.

## Out-of-Scope Discoveries (NOT fixed — pre-existing)

- Pre-existing stray working-tree changes in the submodule (`.gitignore` modified; untracked `.coverage`, `SECURITY.md`, `write_test_port.sh`) were left untouched per the submodule_commit_protocol — only the files this plan touched were committed.

## SAFE-04 / 2516 Wire-Stability Confirmation

**2516 wire values are unmoved and the chip is UNVERIFIED.** The regenerated DB 2516 record carries algorithm 0x0B, pinout DIP24_2716, electrical.type UV-EPROM, vpp_mv 25000, size_bytes 2048 — verbatim from the v1.15 user-override (`.planning/v1.15/DECODE-AUDIT.md`). `support_status` stays `"supported"` (host guard unchanged; resolvable for read/info) and `verification_status: "UNVERIFIED"` marks it non-write-graduated (FUT-03). `test_extra_chips_supplement.py` pins all of these.

## Verification Results

- Task 1 gate: `SUPPLEMENT-AUTHORED-OK` — 2516 + 2532 present in extra_chips.json; both pinouts (DIP24_2716, DIP24_2532) exist in pinouts.json.
- Task 2 gate: `MERGE-OK` — regenerated DB contains 2516 (algo 11 / DIP24_2716 / 25000mV) + 2532; byte-faithful merge; 744 + 2 = 746 reported.
- Task 3 gate: `VAR05-GATE-OK` — `diff_db.py` exit 0 (`PASS: all 72 changed chips explained`; 2516/2532 under the cited non-upstream-supplement section, no WARN); `check_dispatch.py` `0 dispatch regressions; 0 consistency violations` (746 chips; 736 supported); `test_extra_chips_supplement.py` 8 passed.
- Full submodule suite: **686 passed** (29 snapshots passed). ruff check + ruff format --check clean on all touched Python (validated against the `/usr/local` py-toolchain; mypy present).
- Baselines (`tools/baseline/*.json`) **NOT modified** (re-pin is Plan 86-03; last touched Phase 70).
- Chip count: 746 (744 upstream + 2 supplement).

## Next Phase Readiness

- **Plan 86-03 (baseline re-pin):** the diff vs the OLD baseline is now fully explained including the 2516/2532 supplement rows (exit 0). 86-03 can re-pin `chip_database.baseline.json` + `dispatch_baseline.json` to the corrected 746-chip DB — the supplement rows become baseline members at that point.
- 2516/2532 ship first-class; 2516 UNVERIFIED + wire-stable; both pass check_dispatch (24-pin VPP-pin safety holds).
- No blockers; no re-bench flags.

## Self-Check: PASSED

- FOUND: firestarter_app/tools/extra_chips.json
- FOUND: firestarter_app/tools/build_db.py (post-decode merge present)
- FOUND: firestarter_app/tools/diff_db.py (EXTRA_CHIPS_SUPPLEMENT present)
- FOUND: firestarter_app/firestarter/data/pinouts.json (DIP24_2532 present)
- FOUND: firestarter_app/firestarter/data/chip_database.json (746 chips; 2516 + 2532)
- FOUND: firestarter_app/tests/test_extra_chips_supplement.py
- FOUND: firestarter_app/tools/variant-decode-diff.txt
- FOUND commit: 94ea3b5 (Task 1)
- FOUND commit: 4054bfe (Task 2)
- FOUND commit: 5e368d1 (Task 3)

---
*Phase: 86-variant-decode-correct-db-regen*
*Completed: 2026-06-25*
