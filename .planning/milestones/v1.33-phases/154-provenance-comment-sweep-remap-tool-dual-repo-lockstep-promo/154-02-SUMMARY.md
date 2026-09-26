---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "02"
subsystem: infra
tags: [static-analysis, python, cli, regex, gate-audit, comment-sweep, blob-sha]

requires:
  - phase: 154-01
    provides: "FW_PRE_SHA/APP_PRE_SHA anchors, both sub-repos branched off beta, pio-cwd trap documented, baseline-pre-sweep.md on disk (uncommitted)"
provides:
  - "survey_provenance.py — the committed, re-runnable corpus measuring instrument and SWEEP-03/SWEEP-06 oracle every later sweep plan calls"
  - "sweep-corpus-baseline.md — D-01's procedure stated verbatim, D-02/D-03/D-04 restated, the measured corpus (651 hits/169 files) fully reconciled against both recorded figures with every delta explained"
  - "sweep-gate-dispositions.md — all 8 ALL_CROSS_REPO_PATHS measured+dispositioned, all 22 firmware-repo fail-open gates re-classified by mechanism (not by stripper-name grep) into no-overlap/control/EXPOSURE, the 4 blob-sha exemptions + eprom_params.cpp's double-pin consequence recorded"
affects: [154-03, 154-04, 154-07, 154-08, 154-09, 154-10, 154-11, 154-12]

tech-stack:
  added: []
  patterns:
    - "Explicit-argument scan roots, never __file__-derived — the D-09 rule, enforced by a source assertion (grep -c '_HERE' == 0) rather than a promise"
    - "Three-way exit-code contract (0/1/2) with infra failures (missing root, explicit-empty-group, zero-hit corpus) distinguished from real violations"
    - "Classify a gate by READING its extraction mechanism, not by grepping for a named helper in the test file alone — the F4/A3 correction applied to all 22 firmware-repo gates"
    - "Measure both sides, explain every delta, adopt neither — reused from plan 01, applied here to the corpus hit-count reconciliation"

key-files:
  created:
    - .planning/v1.33/tools/survey_provenance.py
    - .planning/v1.33/sweep-corpus-baseline.md
    - .planning/v1.33/sweep-gate-dispositions.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "SWEEP-06 ticked complete in REQUIREMENTS.md; SWEEP-03/SWEEP-04 left unticked because their verbs ('stripped', 'receive the narrow treatment') describe later-plan sweep actions this plan does not perform — only the rule-statement and measurement clauses are discharged here"
  - "The corpus tool scans the .c/.cpp extensions the plan's own task 1 action text specifies, which counts 9 GSD-shaped test fixture files RESEARCH.md's re-derivation evidently missed (or scanned .py-only) — every one of the resulting +16-hit/+9-file deltas across this plan's two documents traces to exactly those 9 files, none left unexplained"
  - "test_check_erase_no_vpp.py and test_check_orphan_provisional.py reclassified from research F4's implicit 'no stripping' bucket to control, because their comment-stripping lives in the SUBPROCESSED checker script, not in the test file a stripper-name grep would check — the exact A3 blind spot named in the plan text, found by reading the checker source rather than trusting the original classification method"
  - "test_vpp_seam_manual_on_every_board.py and test_pinmap_guard_fires.py recorded as genuine EXPOSURE: both extract an expected #error string via a raw, unstripped re.search with first-match-wins semantics, the identical shape research proved fail-open in test_sdp_table_parity.py (F2) — not fixed in this plan (SWEEP-06 is not expanded), filed as a named follow-on"
  - "ROADMAP.md/REQUIREMENTS.md/STATE.md hand-edited, never via the roadmap/requirements GSD verbs, which would reformat six phase entries and 43 requirements (binding constraint carried from plan 01 and this milestone's own STATE.md)"

patterns-established:
  - "A hit-count criterion resolves to one committed command (survey_provenance.py's own CLI), never to an assertion restated in prose"
  - "A gate disposition table's three-value enum (no-overlap / control / EXPOSURE) forces every row to a concrete, falsifiable claim instead of a paragraph of hedging"

requirements-completed: [SWEEP-06]

coverage:
  - id: D1
    description: "survey_provenance.py: explicit-root, no-_HERE, 7-group corpus scanner with --json/--file-table/--assert-tokens-zero and the house 0/1/2 exit contract"
    requirement: "SWEEP-03"
    verification:
      - kind: integration
        ref: "python3 .planning/v1.33/tools/survey_provenance.py /workspaces/firestarter /workspaces/firestarter_app --json (exit 0, 7 group keys) / --group fw-lib (exit 2) / /nonexistent-root-xyz (exit 2) / grep -c '_HERE' == 0"
        status: pass
      - kind: integration
        ref: "python3 .planning/v1.33/tools/survey_provenance.py <roots> --assert-tokens-zero 'D-#' --group fw-src --group fw-include (exit 1, 34 hit lines) -- the RED-before-sweep leg"
        status: pass
    human_judgment: false
  - id: D2
    description: "sweep-corpus-baseline.md: D-01 procedure restated with the step-3 guard, D-02/D-03/D-04 restated, the measured corpus reconciled against both recorded figures (636/167, 635/160) with every delta traced to 9 fixture files"
    requirement: "SWEEP-04"
    verification:
      - kind: integration
        ref: "for t in D-01 D-02 D-03 D-04 'CORPUS DEFINITION' '182-200' 'PROTOCOLS.md' '2,657' 331 615; do grep -q \"$t\" .planning/v1.33/sweep-corpus-baseline.md; done && grep -cE '^\\| *(fw-src|fw-include|fw-test|app-pkg|app-tests|app-tools) *\\|' .planning/v1.33/sweep-corpus-baseline.md -ge 6"
        status: pass
    human_judgment: false
  - id: D3
    description: "sweep-gate-dispositions.md: all 8 ALL_CROSS_REPO_PATHS measured+dispositioned (both generated headers at a measured 0), the corrected D-06 comment-sensitivity table, all 22 firmware-repo gates dispositioned, the 4 blob-sha exemptions + double-pin consequence + eprom.cpp 627-citation answer"
    requirement: "SWEEP-06"
    verification:
      - kind: integration
        ref: "grep -cE 'test_(check_erase_no_vpp|...|pinmap_guard_fires)\\.py' .planning/v1.33/sweep-gate-dispositions.md -ge 22 && for t in ALL_CROSS_REPO_PATHS sdp_bus_config.h validation_matrix.h PROTOCOLS.md eprom_params_citations.json protocol_branch_inventory.json eprom_v131_trace_inventory.json sdp_expected_inventory.json 627 D-05 D-06; do grep -q \"$t\" .planning/v1.33/sweep-gate-dispositions.md; done"
        status: pass
    human_judgment: false
  - id: D4
    description: "Section B's two EXPOSURE rows (test_vpp_seam_manual_on_every_board.py, test_pinmap_guard_fires.py) are genuinely dangerous, not merely a coarse F4-inherited label"
    human_judgment: true
    rationale: "Whether a raw-regex #error extraction is EXACTLY the SDP gate's proven fail-open shape (vs. mitigated by the module's other assertions, e.g. the real-preprocessor invocation in test_pinmap_guard_fires.py) is a judgment about gate semantics that this plan states with its evidence but does not build a planted fixture to prove either way -- that fixture-building is explicitly deferred as a follow-on phase, not this plan's scope."

duration: 25min
completed: 2026-08-23
status: complete
---

# Phase 154 Plan 02: Corpus Survey Tool + Pre-Sweep Baseline + Gate Dispositions Summary

**Built `survey_provenance.py` — a 7-group, explicit-root, fail-closed corpus scanner with an `--assert-tokens-zero` oracle armed and proven RED pre-sweep (34 `D-#` hits in `fw-src`+`fw-include`) — then used it to reconcile the pre-sweep corpus baseline (651 hits/169 files, every delta from the 635/160 research figure traced to 9 GSD-shaped test fixtures) and to disposition all 30 gates this sweep can reach: the 8 `ALL_CROSS_REPO_PATHS` app paths (both generated headers confirmed at a measured 0) plus all 22 firmware-repo fail-open gates, re-classified by reading each one's actual extraction mechanism rather than by the presence of a named stripper — surfacing 2 genuine `EXPOSURE` rows research's coarser method missed the shape of.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-08-23T01:50:00Z (approx., following directly from plan 01's completion)
- **Completed:** 2026-08-23T02:15:45Z
- **Tasks:** 3 of 3
- **Files modified:** 3 created (meta), 2 hand-edited (REQUIREMENTS.md, ROADMAP.md), 1 to be updated (STATE.md)

## Accomplishments

- **`survey_provenance.py` built as the phase's one committed measuring instrument.** Explicit `fw_root`/`app_root` positional arguments (`grep -c '_HERE'` == 0, verified), seven fixed groups, source extensions `.cpp .c .h .hpp .ino .py`, and the exact regex research reconstructed, stated verbatim in the docstring as a raw string so the literal pattern matches character-for-character. House 0/1/2 exit contract: 2 for a missing root, an *explicitly*-requested empty group (`--group fw-lib` alone), or a zero-hit corpus; 1 for an `--assert-tokens-zero` violation; 0 otherwise. The default all-groups run correctly tolerates `fw-lib`'s legitimate 0-files/0-hits without tripping the empty-group infra check — verified as two separate exit codes for the same group, selected vs. default.
- **The `--assert-tokens-zero` leg demonstrated RED before any sweep, as the task's own done-criterion required.** `D-#` over `fw-src`+`fw-include` returns exit 1 with 34 hit lines (191 across the whole corpus); `P###` and `REQ-` (research's two dead alternations) both return exit 0 at 0 hits, confirming they are armed-but-empty rather than broken.
- **The corpus baseline was measured, not copied.** `651 hits / 169 files` total, `129 hits / 34 files` for `fw-src`+`fw-include` (matching research to the hit and the file). Every one of this session's deltas from research's `635/160` — the whole-corpus delta, the `app-tests` sub-delta, the `CAP-0` exemption sub-delta (22 vs. 20), and the `firestarter/tests/*.py` exclusion sub-delta (21/8 vs. 20/7) — was traced to the exact same 9 named fixture files under `firestarter_app/tests/fixtures/` and 1 under `firestarter/tests/fixtures/`, none left unexplained.
- **All 8 `ALL_CROSS_REPO_PATHS` measured individually.** Both generated headers (`sdp_bus_config.h`, `validation_matrix.h`) confirmed at a measured **0** hits, discharging SWEEP-06's "fixed at their generators or shown to need no fix" by measurement. `doc/PROTOCOLS.md` confirmed at 2 hits with an explicit out-of-scope ruling. The `test_sdp_table_parity.py` D-06 row was corrected per the plan's instruction (it does ship a non-vacuity leg and a purpose-built planting seam; what it lacks is a control for either comment-blind mechanism).
- **All 22 non-comment-stripping firmware-repo gates re-classified by reading their actual mechanism, not by a stripper-name grep.** Found 2 gates (`test_check_erase_no_vpp.py`, `test_check_orphan_provisional.py`) that F4's classification method missed entirely: their comment-stripping lives in the *subprocessed checker script* the test invokes, not in the test file itself — reclassified `control`, cause stated. Found 5 more `control` rows via structural immunity (byte-count comparison, git-log commit-presence, CMake filename-membership, git-ancestry/blob-divergence) and 2 via cross-reference to Section C's blob-sha exemption. Found 2 genuine `EXPOSURE` rows (`test_vpp_seam_manual_on_every_board.py`, `test_pinmap_guard_fires.py`) sharing the exact first-match-wins raw-regex shape research proved fail-open in `test_sdp_table_parity.py` — named as a real follow-on, not fixed here (SWEEP-06's text is not expanded).
- **The blob-sha exemptions and their double-pin consequence recorded.** 4 files / 28 of 615 hits exempted, each named with its pinning sidecar; `src/proms/eprom_params.cpp`'s two-sidecar pin independently re-verified this session (`5dffe841…` in both `meta.blob_shas` maps); the two facts that bound plan 07's regeneration (no line-number dependency in either sidecar's non-`blob_shas` content; the gate's own re-derive-don't-hand-edit instruction) both confirmed by reading the actual JSON structure, not assumed. `eprom.cpp`'s 627-citation manifest-shape question answered (no — the manifest is built from the pre-sweep candidate set, exemption only narrows the actual swept set).

## Task Commits

1. **Task 1: Build survey_provenance.py** — `3ee003f6` (feat) — the corpus measuring instrument, seven groups, exit-code contract, `--assert-tokens-zero` armed and RED.
2. **Task 2: Record the pre-sweep corpus baseline** — `9c7605ea` (docs) — D-01 procedure, D-02/D-03/D-04 restated, measured corpus reconciled.
3. **Task 3: Write sweep-gate-dispositions.md** — `1680c30a` (docs) — 8 app paths + 22 firmware gates + blob-sha exemptions.

**Plan metadata:** pending — this SUMMARY.md, STATE.md, ROADMAP.md, REQUIREMENTS.md land in the plan's closing `docs(154-02)` commit (or an SDK-reported intentional skip; see Final Commit note below).

## Files Created/Modified

- `.planning/v1.33/tools/survey_provenance.py` — the corpus scanner + `SWEEP-03`/`SWEEP-06` oracle (340 lines).
- `.planning/v1.33/sweep-corpus-baseline.md` — the pre-sweep corpus record (236 lines).
- `.planning/v1.33/sweep-gate-dispositions.md` — the gate accountability record (187 lines).
- `.planning/REQUIREMENTS.md` — 2-line hand edit: `SWEEP-06` ticked `[x]` and its traceability row moved to `Complete (154-02)`.
- `.planning/ROADMAP.md` — 2-line hand edit: `154-02-PLAN.md` ticked, Phase 154 progress `1/12` → `2/12`.
- `.planning/STATE.md` — position, decisions, session (this step, below).

## Decisions Made

1. **SWEEP-06 ticked; SWEEP-03/SWEEP-04 left unticked (partial).** SWEEP-06's full text ("classified and disposed of... fixed at their generators or shown to need no fix") is entirely a classification/measurement claim, fully discharged by Section A of `sweep-gate-dispositions.md`. SWEEP-03 and SWEEP-04 both contain a verb describing the actual sweep action ("stripped", "receive the narrow treatment") that later plans (154-07/08/09) perform; this plan discharges only their rule-statement and measurement clauses. Recorded as partial contributions below, not ticked, per `reference_executors_prematurely_mark_requirements_complete`.
2. **The tool's `.c`/`.cpp` extension inclusion for `app-tests`, taken exactly as task 1's action text specifies, is the sole and fully-explained source of every measurement delta in this plan's two documents.** Not adjusted to match research's narrower (evidently `.py`-only) app-tests scan, because the task's own extension list is explicit and the delta is traced file-by-file rather than hand-waved.
3. **Two gates reclassified from F4's implicit "unsafe" bucket to `control` on direct evidence, not assumption.** `test_check_erase_no_vpp.py` and `test_check_orphan_provisional.py` both invoke a subprocessed checker script that defines and calls `_strip_comments()` internally — confirmed by reading `scripts/check_erase_no_vpp.py` and `scripts/check_orphan_provisional.py` directly, not by re-trusting the original test-file-only grep.
4. **Two gates recorded as genuine `EXPOSURE`, not smoothed into "probably fine."** `test_vpp_seam_manual_on_every_board.py` and `test_pinmap_guard_fires.py` each extract an expected `#error "..."` string via `re.search` on raw, unstripped text with no comment-blindness defense — the identical first-match-wins shape research's F2 proved fail-open. Filed as a named follow-on per the plan's own instruction (building 22 planted controls is a separate phase), not silently downgraded to `no-overlap`.
5. **ROADMAP.md/REQUIREMENTS.md hand-edited, `roadmap.update-plan-progress`/`requirements.mark-complete` verbs NOT run.** Per this plan's own `<state_updates>` instruction and the milestone-wide hand-authored-files constraint (`reference_gsd_requirements_roadmap_verbs_reformat_whole_file`). Snapshotted before/after; `git diff --numstat` confirms 2/2 on both files, zero reformatting.

## Deviations from Plan

### Auto-fixed Issues

None — Rule 1/2/3 auto-fixes were not triggered; no bug, missing critical functionality, or blocking issue arose during execution.

### Measurement deltas recorded, not adopted

Per this plan's own execution note ("where your number differs from a figure recorded in RESEARCH.md or CONTEXT.md, print both and the command that produced yours"), several measured figures differ from recorded ones. All are fully explained, none silently adopted or overwritten:

1. **Whole-corpus total: 651/169 measured vs. 635/160 (research) / 636/167 (writeup).** Fully explained: 9 GSD-shaped test fixture files under `firestarter_app/tests/fixtures/` (`planted_cap03_literal_index.cpp`, `planted_cap03_truncated_length.cpp`, `planted_constants_fw_missing.h`, `planted_constants_host_missing.h`, `planted_constants_value_drift.h`, `planted_ifdef_in_predicate.h`, `planted_json_parser_key_string_drift.c`, `planted_json_parser_undispatched_key.c`, `planted_log_in_window.cpp`) carry 16 hits between them — `651 - 635 = 16`, `169 - 160 = 9`, exact. Both figures printed side by side in `sweep-corpus-baseline.md` §6.
2. **CAP-0N exemption sub-count: 22 measured vs. 20 recorded (D-02).** The +2 delta is `planted_cap03_literal_index.cpp` + `planted_cap03_truncated_length.cpp`, the same fixture-inclusion cause as #1. Both the recorded 20/615 figures (restated verbatim per the plan's action text) and the independently-measured 22/613 pair are recorded side by side in `sweep-corpus-baseline.md` §3, with the D-02 figures retained as authoritative per the task instruction.
3. **`firestarter/tests/*.py` exclusion: 21 hits/8 files measured vs. 20/7 recorded (research F4).** The +1 delta is `tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp`, same cause. Recorded in `sweep-corpus-baseline.md` §7.

None of these deltas required a fix — they are measurement facts about which files the tool's extension list reaches, printed per the plan's own "explain or state-as-unexplained" instruction. All three are, in fact, fully explained.

---

**Total deviations:** 0 auto-fixed; 3 measurement deltas recorded and fully explained (not adopted, not left unexplained).
**Impact on plan:** None on scope. The plan's own instruction anticipated exactly this class of finding ("where your number differs... print both... never silently adopt either").

## TDD Gate Compliance

Task 1 carries `tdd="true"` but its `<files>` declaration names only `survey_provenance.py` itself — no sibling pytest module is part of this plan's deliverable set (unlike `remap_citations.py`/`test_remap_citations.py` in plan 05). There is therefore no separate test file to RED-then-GREEN against. The task's own `<done>` criterion substitutes a different, and arguably stronger, RED/GREEN evidence shape: the tool's `--assert-tokens-zero` leg is required to be **demonstrated RED before the sweep** (verified: `D-#` over `fw-src`+`fw-include` exits 1 with 34 hit lines) **so its post-sweep GREEN is evidence** — i.e., the RED state is a property of the *corpus*, proven by running the finished tool against the pre-sweep tree, not a property of an *intentionally-failing test file* authored before the implementation. This plan committed the tool in one `feat` commit (`3ee003f6`) rather than a `test(...)`-then-`feat(...)` pair, because no `test(...)`-shaped artifact exists to commit separately. The RED evidence itself was captured and is reproducible on demand via the exact command recorded in this SUMMARY's Accomplishments section and in `sweep-corpus-baseline.md`.

## Issues Encountered

None. `pio` was not invoked in this plan (no firmware build or test run was needed — this plan only reads source text and writes `.planning/` records), so plan 01's `platformio.ini`-at-`/workspaces`-root trap did not apply here.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **154-03** (SWEEP-07 planted controls) can proceed: `sweep-gate-dispositions.md` Section A's corrected D-06 table gives it the exact two gates and mechanisms to control (`test_sdp_table_parity.py`'s `_PAIR_RE`/brace-slice pair, `test_dispatch_mirror.py`'s C++ leg).
- **154-04** (citation manifest) can proceed: the corpus baseline's reconciled figures and the gate-disposition record are both committed and stable inputs.
- **154-07** (shipped firmware sweep) has its exact scope narrowed by Section C: sweep `eprom_params.cpp` and regenerate both its sidecars in the same commit; leave the other four pinned files untouched.
- **Follow-on filed, not built here:** planted-violation controls for the two Section-B `EXPOSURE` gates (`test_vpp_seam_manual_on_every_board.py`, `test_pinmap_guard_fires.py`), and, more broadly, controls for all 22 firmware-repo gates as defense in depth — both explicitly named as separate, later phases in `sweep-gate-dispositions.md` Section B's closing note.
- No blockers. `.planning/v1.33/baseline-pre-sweep.md` remains uncommitted by design (plan 01/D-11); this plan did not touch it and re-confirmed it is still present on disk.

## Self-Check: PASSED

Created files verified present on disk:
- `FOUND: .planning/v1.33/tools/survey_provenance.py`
- `FOUND: .planning/v1.33/sweep-corpus-baseline.md`
- `FOUND: .planning/v1.33/sweep-gate-dispositions.md`
- `FOUND: .planning/phases/154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo/154-02-SUMMARY.md`

Commits verified present in git (`git log --oneline --all`):
- `FOUND: 3ee003f6` — feat(154-02): build survey_provenance.py
- `FOUND: 9c7605ea` — docs(154-02): record sweep-corpus-baseline.md
- `FOUND: 1680c30a` — docs(154-02): record sweep-gate-dispositions.md
- `FOUND: 11bc9b38` — docs(154-02): plan-metadata commit (this SUMMARY + STATE + ROADMAP + REQUIREMENTS)

All three tasks' `<automated>` verify blocks re-run at plan end: task 1 (file-table/json/`_HERE`/bad-root chain) exit 0, task 2 (literal-token + row-count checks) all present, task 3 (22-module count + literal-token checks) all present.

`.planning/config.json` shows as modified in `git status` but was already dirty before this plan started (pre-existing, unrelated to this plan's scope) and was not staged or committed by any of this plan's commits. `.planning/v1.33/baseline-pre-sweep.md` remains untracked, exactly as plan 01 left it.

---
*Phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo*
*Completed: 2026-08-23*
