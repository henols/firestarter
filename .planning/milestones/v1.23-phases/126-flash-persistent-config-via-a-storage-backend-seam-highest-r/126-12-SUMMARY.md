---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 12
subsystem: firmware/py32f071 config-storage — phase closeout
tags: [flash-config, py32f071, non-regression, closing-plan, cfg-01..07]

# Dependency graph
requires:
  - phase: 126-01
    provides: "the vendored design + geometry record (CFG-01/CFG-02 evidence base)"
  - phase: 126-11
    provides: "ARM CI run 30676982030, re-derivable read-only, cited as-is"
provides:
  - "126-NONREGRESSION.md: every gate, count and figure re-executed live in this closing session against the trees exactly as they stand, with all 5 ROADMAP criteria and all 19 decisions (D-01..D-19) accounted for"
  - "CFG-01 through CFG-07 ticked in .planning/REQUIREMENTS.md, each citing the specific re-executed row that discharges it"
  - "The ROADMAP's Phase 126 entry finalised: plan count, wave-grouped plan list, and a note recording the three decision amendments (D-08, D-18, D-16)"
affects: [127, 128, 129, 130]

tech-stack:
  added: []
  patterns:
    - "Re-execution over transcription: every observed value in this closing artifact comes from a command run in this session, never copied from a prior plan's SUMMARY"

key-files:
  created:
    - .planning/phases/126-flash-persistent-config-via-a-storage-backend-seam-highest-r/126-NONREGRESSION.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Criterion 3's literal 'empty git diff on the test file' was NOT achieved — recorded honestly with both blob SHAs (0ef805ff... pre-refactor, 12bd237a... post-fallback) and the reason (Plan 126-03's mandatory AVR board guard forced a one-line compile-invocation change). The substantive property (assertions unchanged, still green) held and is stated separately from the unmet literal wording."
  - "The native warning-count gate's first invocation reused a warm PlatformIO cache and under-reported (998/998/0 vs watermarks 1166/1166/138); a cold rebuild reproduced the recorded watermarks exactly. Both figures are <=-watermark PASSes; the cold figures are recorded as authoritative, and the discrepancy is recorded as a measurement-discipline note, not a regression."
  - "The pytest dual-slot/schema/geometry harness runs in ZERO CI legs on this branch (py32f071.yml has no pytest step) — discharged entirely by the local runs in this document, never claimed as CI-covered."
  - "No unresolved ARM gate exists — Plan 126-11 found the A-7 linker-region fallback unnecessary, so all seven CFG requirements were assessed against complete evidence, none blocked."

requirements-completed: [CFG-01, CFG-02, CFG-03, CFG-04, CFG-05, CFG-06, CFG-07]

coverage:
  - id: D1
    description: "126-NONREGRESSION.md re-executes every firmware, host, meta and ARM row live in this session (170 pytest, 141/141/17 both pinned native envs, 10/10/1 provisional, 3 cold AVR builds byte-identical, both size comparators exit 0, manifest at 26/15/5, 11 host rows H1-H9b all RAN, host suite 1158 passed matching Phase 124, ARM run re-queried read-only)"
    requirement: "CFG-01"
    verification:
      - kind: other
        ref: "126-NONREGRESSION.md §3 gate table, this session's live run"
        status: pass
    human_judgment: false
  - id: D2
    description: "CFG-02's ordering constraint re-derived: git merge-base --is-ancestor fd84820 f724613 exits 0, non-vacuity count = 1"
    requirement: "CFG-02"
    verification:
      - kind: other
        ref: "126-NONREGRESSION.md §Criterion 2"
        status: pass
    human_judgment: false
  - id: D3
    description: "CFG-03's structural split gate (tests/test_config_storage_seam_shape.py, 14 functions) re-run green; declaration census, C linkage, includer census all confirmed"
    requirement: "CFG-03"
    verification:
      - kind: unit
        ref: "tests/test_config_storage_seam_shape.py (14 passed, this session)"
        status: pass
    human_judgment: false
  - id: D4
    description: "CFG-04's regression test re-run green (7/7); the recorded blob SHA does NOT re-hash identical to the pre-refactor value — the documented fallback SHA (12bd237a...) is what matches, recorded honestly as an amended Criterion 3 satisfaction, not a literal empty-diff"
    requirement: "CFG-04"
    verification:
      - kind: unit
        ref: "tests/test_config_storage_eeprom_regression.py -v (7 passed, this session); 126-NONREGRESSION.md §Criterion 3"
        status: pass
    human_judgment: false
  - id: D5
    description: "CFG-05's six named dual-slot tests plus the D-05 CRC anchor re-run individually, all PASSED, no aggregate pass/fail"
    requirement: "CFG-05"
    verification:
      - kind: unit
        ref: "tests/test_config_storage_dualslot.py -v (9 passed, this session, 6 named + CRC anchor + 2 supporting legs)"
        status: pass
    human_judgment: false
  - id: D6
    description: "CFG-06's flash map re-parsed this session: CONFIG at 0x0801E000/8K, slots at 0x0801E000 and 0x0801E100 (different page erase units), four PROVIDEd symbols present, host FLASH_BASE/FLASH_SIZE asymmetry recorded as correct-not-drift"
    requirement: "CFG-06"
    verification:
      - kind: unit
        ref: "tests/test_py32_flash_map.py (20 passed, this session)"
        status: pass
    human_judgment: false
  - id: D7
    description: "CFG-07's schema/deletion gate re-run green (17 functions); config.cpp confirmed absent by path; rurp_configuration_t/CONFIG_VERSION unchanged (blob SHAs match); all 9 C-14 consumer sites re-grepped"
    requirement: "CFG-07"
    verification:
      - kind: unit
        ref: "tests/test_config_schema_pinned.py (17 passed, this session); 126-NONREGRESSION.md §Criterion 5"
        status: pass
    human_judgment: false

duration: ~2h
completed: 2026-08-01
status: complete
---

# Phase 126 Plan 12: Closing Non-Regression Sweep + CFG-01..CFG-07 Summary

**Re-executed every gate, count and figure this phase is judged against in this closing session — 170 pytest (per-module breakdown accounted for), both pinned native envs cold at 141/141/17, three AVR builds byte-identical, both size comparators green, the manifest at 26/15/5, all eleven cross-repo host rows shown to have RUN, the host suite at 1158 matching Phase 124, and the ARM CI run re-queried read-only — then wrote `126-NONREGRESSION.md` accounting for all 5 ROADMAP criteria and all 19 decisions (with D-08/D-16/D-18/D-19's amendments named as amendments and Criterion 3's unmet literal "empty diff" wording recorded honestly), and ticked CFG-01 through CFG-07.**

## Performance

- **Duration:** ~2h
- **Completed:** 2026-08-01
- **Tasks:** 3/3 completed
- **Files modified:** 1 created (`126-NONREGRESSION.md`), 3 modified (`REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`)

## Task 1 — Re-execute every firmware, host, meta and ARM row (read-only, no commit)

Every figure below was produced by a command run in **this session**, not transcribed from any of the eleven prior plans' SUMMARY files.

**Firmware repo (`/workspaces/firestarter`):**
- `git rev-parse --abbrev-ref HEAD` = `v1.23-py32f071-integration`; `HEAD` = `240fb19c50190797ffdc2062d39390e074f8566f` (string-equal to Plan 126-11's recorded ARM-run head SHA); `git status --porcelain` = 0 lines.
- `python3 -m pytest tests/ -q` → **170 passed**, with a per-module breakdown of the seven modules this phase added/extended (9+7+14+8+20+9+17 = 84; 86 pre-phase + 84 = 170, matching exactly — no module silently uncollected).
- Three cold AVR builds (uno/uno328pb/leonardo): all byte-identical to the pre-existing baseline (0 B flash/RAM delta on all three, all eight relevant plans in this phase). Both comparators (`compare_avr` strict, `compare_avr_policy_merge05` A-5 band) exit 0.
- Both pinned native envs (`native`, `native_nodevtools`), cold: **141 cases / 141 succeeded / 17 suites**, both. `native_pinmap_provisional`: **10/10/1**.
- Warning gates: AVR all exit 0 (`macro_redefinition=0`); native — **first pass under-reported due to a warm PlatformIO cache** (998/998/0 vs watermarks 1166/1166/138); a cold rebuild (`rm -rf .pio/build/native*`) reproduced the recorded watermarks exactly (1166/1166/138). Both passes are `<=`-watermark PASSes; the cold figures are recorded as authoritative in `126-NONREGRESSION.md`.
- `check_cmake_manifest.py`: PASS, **26 enforced / 15 exempt / 5 allow-listed**. `check_orphan_provisional.py` and `check_landing_range.py`: both exit 0. Golden traces (`test_golden_trace_identity.py`): **6 passed**, per-array basis unchanged.
- Five must-not-touch blob SHAs (`rurp_types.h`, `rurp_shield.h`, `platformio.ini`, `messages.h`, `size_baseline_base01.json`): **all five match** pre-phase values exactly.
- `platform/py32f071/src/config.cpp`: confirmed **absent**. `grep -c hal_flash CMakeLists.txt` = **1**.
- Criterion 2 (`git merge-base --is-ancestor fd84820 f724613`): exit **0**; non-vacuity commit count = **1**.
- Criterion 3 blob re-hash: `12bd237a7aeec174d2eaf5c99f206737255388f3` — **matches the documented post-fallback SHA, NOT the pre-refactor SHA** (`0ef805ff8e915f9321bda5dc50d61b8a8dd26eaf`). Recorded honestly as an amended satisfaction, not an empty diff.
- C-14 consumer census: all 9 sites re-grepped and confirmed present at their recorded lines. D-09 includer census: 3 sanctioned TU includers.

**Host repo (`/workspaces/firestarter_app`):** all eleven MERGE-07 rows (H1–H9b) re-run, all **RAN and PASSED** (combined 37 pytest across H2/H3/H4b/H6/H7/H8). Skip census (`-rs`, full suite): **0 skipped**, no false firmware-absence reason (`../firestarter/.git` exists throughout). Full suite: **1158 passed**, byte-identical to Phase 124's recorded 1158. No live board attached (`/dev/ttyACM*`/`/dev/ttyUSB*` absent) — recorded so a future characterisation-test red is attributable. Hygiene rows (ruff check/format, mypy watermark, no-exists-proxy): all green. Porcelain: 5 known pre-existing lines, named.

**Meta repo:** `test_check_permitted_claims.py` — **10 passed**.

**ARM row:** `gh run view 30676982030` re-queried read-only — conclusion=success, headSha string-equal to freshly re-derived firmware HEAD, Configure and Build both independently success. No unresolved ARM gate (Plan 126-11's A-7 fallback was found unnecessary).

## Task 2 — Write `126-NONREGRESSION.md`

Written in `125-NONREGRESSION.md`'s command/expected/observed row shape, with all seven required sections: (1) summary claims and explicit non-claims; (2) the baseline as recorded and re-verified; (3) the gate table split by repository, with the C-8 note that eleven rows represent nine gates; (4) all five ROADMAP criteria, each quoted and discharged by row — **Criterion 3 recorded as a partial/amended satisfaction with both blob SHAs and the reason, explicitly not claiming an empty diff**; (5) the nineteen-row decision-coverage table (D-01…D-19), with D-08, D-16, D-18 described as amendments and D-18/D-19 named as the two escalation-locked decisions; (6) informational findings carried forward (the warm-cache warning-count artifact, the 126-02/126-03 acceptance-criteria inconsistency, the stale 2600 B figure, RESEARCH's "seven vs nine" and "eleven vs twelve" miscounts, CRC32 never called a security primitive); (7) the claim ceiling stated by reference, with the claim gate run with named explicit targets.

**Claim gate results:** `CONFIG-STORAGE.md` alone — exit 0. The document itself, self-scanned after being written — exit 0 (confirmed below in Self-Check). The eleven prior `126-*-SUMMARY.md` files, scanned together — exit 1 (each missing the exact canonical caveat phrase this checker's regex requires, though each states the non-claim in its own words) — **recorded as an informational finding in `126-NONREGRESSION.md` §7, the same shape Phase 125 recorded its own six SUMMARY trips.**

**Commit:** `542b937` (docs, meta repo) — `git show --stat` lists exactly one path: `126-NONREGRESSION.md` (589 insertions).

## Task 3 — Tick CFG-01…CFG-07, finalise the ROADMAP entry, hand-correct STATE.md

**Each requirement ticked against a specific re-executed row, not a prior plan's claim:**

- **CFG-01** — discharged by `CONFIG-STORAGE.md`'s vendored design (blob `4b1a441`, PRs #46/#47 named, all seven module names in the SUPERSEDED block), re-confirmed present and its own claim-gate PASS re-run this session (§Criterion 1 of `126-NONREGRESSION.md`).
- **CFG-02** — discharged by the re-derived `git merge-base --is-ancestor fd84820 f724613` (exit 0) plus the non-vacuity leg (§Criterion 2).
- **CFG-03** — discharged by `tests/test_config_storage_seam_shape.py`'s 14 functions, re-run green this session, plus the C-14 consumer census re-grepped (§Criterion 5, D-07 row).
- **CFG-04** — discharged by `tests/test_config_storage_eeprom_regression.py`'s 7/7 pass and the AVR delta measured at 0 B on all three targets — **with Criterion 3's amended (not literal) satisfaction recorded explicitly** (§Criterion 3).
- **CFG-05** — discharged by the six individually-named `test_config_storage_dualslot.py` functions plus the D-05 CRC anchor, each re-run and individually PASSED (§Criterion 4).
- **CFG-06** — discharged by the re-parsed flash map (`CONFIG` at `0x0801E000`/8K, two slots in different page erase units, four `PROVIDE`d symbols) plus the ARM CI run's successful link, confirming the linker script assembles on real `arm-none-eabi-ld` (§Criterion 5).
- **CFG-07** — discharged by the schema/version/embedding pin (`tests/test_config_schema_pinned.py`, 17/17), `config.cpp`'s confirmed absence, and the four public functions' single-definition census (§Criterion 5).

**No requirement was left unticked** — Plan 126-11 recorded no unresolved ARM gate, so none of the seven was blocked.

**`.planning/REQUIREMENTS.md`:** all seven CFG boxes ticked (`[ ] → [x]`); the coverage row `CFG-01 … CFG-07 | Phase 126` updated from `Pending` to `Complete — all 7 ticked, see 126-NONREGRESSION.md §4/§5 for the row cited per requirement`.

**`.planning/ROADMAP.md`:** Phase 126's `**Plans**: 11/12` replaced with `**Plans**: 12/12 plans executed — CLOSED 2026-08-01`; the 126-12 plan-list checkbox ticked; a new note block added recording the three decision amendments (D-08's split-commit manifest churn, D-18's whole-sector shrink quantum, D-16's supersession by RESEARCH C-2) and Criterion 3's unmet literal wording, in the same shape Phase 125's entry uses for its own falsified-mechanism note. All edits were scoped `Edit` calls, confined to the Phase 126 section — no whole-file `Write` was used.

**`.planning/STATE.md`:** hand-corrected past the known `state.planned-phase` under-write tooling gap — `gsd-tools query state.advance-plan` was run and correctly reported `last_plan`/`ready_for_verification` (status moved to `verifying`, `stopped_at` updated to "Completed 126-12-PLAN.md — Phase 126 CLOSED"); `state.update-progress`, `state.record-metric`, `state.add-decision` and `state.record-session` were all run via `gsd-tools` (not hand-edited blindly) to keep the frontmatter's `progress` block and body sections consistent with the tool's own computation rather than a guessed number. **This hand-correction is recorded here per the plan's explicit instruction to note it.**

**Requirement-tick verb double-check:** `gsd-tools query requirements.mark-complete CFG-01..CFG-07` was run after the manual `Edit` and reported `already_complete` for all seven — confirming the manual tick and the tool agree, with no double-application.

## Task Commits

1. **Task 1: Re-execute every row** — no commit (read-only evidence capture)
2. **Task 2: Write `126-NONREGRESSION.md`** — `542b937` (docs, meta repo)
3. **Task 3: Tick CFG-01..CFG-07, finalise ROADMAP, hand-correct STATE.md** — this SUMMARY's own commit (docs, meta repo), to follow

## Files Created/Modified

- `.planning/phases/126-flash-persistent-config-via-a-storage-backend-seam-highest-r/126-NONREGRESSION.md` — the re-execution record.
- `.planning/REQUIREMENTS.md` — CFG-01..CFG-07 ticked, coverage row updated.
- `.planning/ROADMAP.md` — Phase 126 finalised: plan count, plan-list checkbox, amendment note.
- `.planning/STATE.md` — position/progress/session fields updated via `gsd-tools` commands.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Native warning-count gate's first invocation under-reported due to a warm build cache**
- **Found during:** Task 1, first `check_build_warnings.py` invocation against `pio test` logs captured earlier in the same session (which reused already-built `.pio/build/native*` artifacts from an even earlier command).
- **Issue:** `998`/`998`/`0` observed vs recorded watermarks `1166`/`1166`/`138` — both still `<=`-watermark PASSes, but not the authoritative cold figure this closing document is required to record.
- **Fix:** `rm -rf .pio/build/native .pio/build/native_nodevtools .pio/build/native_pinmap_provisional`, then re-ran all three `pio test` invocations cold and re-ran the warning gate against the fresh logs — reproduced the recorded watermarks exactly (1166/1166/138).
- **Files modified:** none (measurement-only).
- **Verification:** cold logs' warning counts match `123-`/`124-`/`125-NONREGRESSION.md`'s own recorded watermarks exactly.
- **Committed in:** N/A (no file change; recorded as an informational finding in `126-NONREGRESSION.md` §1/§2/§6).

---

**Total deviations:** 1, a measurement-discipline correction (re-running cold after a warm-cache first pass), not a code or requirement-scope deviation.
**Impact on plan:** None on the plan's tick/artifact scope. The cold figures are what `126-NONREGRESSION.md` records as authoritative.

## Issues Encountered

None beyond the measurement-discipline note above, resolved by re-running cold within the same task.

## Known Stubs

None. This plan produces documentation and requirement/roadmap bookkeeping only — no code, no UI, nothing that could stub a data source.

## Threat Flags

None. This plan reads existing gates and records their output; it introduces no new network endpoint, auth path, file-access pattern, or schema change at a trust boundary.

## Claim Ceiling

No PY32F071 hardware exists. Every figure in this plan and in `126-NONREGRESSION.md` is either a local pytest/PlatformIO measurement or a read-only re-query of Plan 126-11's ARM CI run (workflow_dispatch, `30676982030`) — never a claim about silicon. Config surviving a real DFU install remains the *intended*, unverified behaviour; D-14's first-boot flash-write cost remains **not measured**, never *acceptable*; the new pytest modules run in **zero CI legs** on this branch and are discharged entirely by this session's local runs.

## Next Phase Readiness

- Phase 126 is CLOSED: all 5 ROADMAP criteria discharged (Criterion 3 as an honestly-recorded amendment), all 19 decisions accounted for, all 7 CFG requirements ticked against re-executed evidence.
- Phase 127 (Host DFU Installer) already runs in parallel with 125/126 per the ROADMAP and is unblocked by this close — it owns Criterion 5's cross-repo host half (D-12) as its own scope, not something this phase's close needed to satisfy.
- Phase 129 (PCB record) can cite this phase's actual reserved addresses (`CONFIG` at `0x0801E000`/8K, slots at `0x0801E000`/`0x0801E100`, `BOOTLOADER`'s zero-length seam with its migration-cost comment) as real reservations, not proposals.
- No blockers.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: `.planning/phases/126-flash-persistent-config-via-a-storage-backend-seam-highest-r/126-NONREGRESSION.md`
- FOUND: commit `542b937` in meta repo history
- CONFIRMED: `CFG-01`…`CFG-07` all `[x]` in `.planning/REQUIREMENTS.md`
- CONFIRMED: ROADMAP Phase 126 entry shows `12/12 plans executed — CLOSED 2026-08-01`
- CONFIRMED: claim gate over `126-NONREGRESSION.md` itself exits 0 (re-run after commit, below)
