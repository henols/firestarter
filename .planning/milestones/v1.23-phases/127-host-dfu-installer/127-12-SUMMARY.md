---
phase: 127-host-dfu-installer
plan: 12
subsystem: non-regression-sweep
tags: [closing-sweep, requirements-tick, ci-evidence, mypy-watermark, claim-gate, honesty-ledger]

# Dependency graph
requires:
  - phase: 127-01
    provides: "the merge commit (63ce44e), 4ee64a1 as a literal parent"
  - phase: 127-02
    provides: "pyusb>=1.3.1,<2 floor + its non-vacuous gate"
  - phase: 127-03
    provides: "independent DFU/DfuSe opcode anchors, A1's residual"
  - phase: 127-04
    provides: "_reject_py32_only_option(), both-ways channel gating, the test_help_fw fix (C-1's real-merge disproof)"
  - phase: 127-05
    provides: "APP_REGION_END-bounded envelope + the cross-repo linker parity gate (D-13/D-14)"
  - phase: 127-06
    provides: "the ci-py32 job + workflow_dispatch:, the pyusb-gating collect_ignore"
  - phase: 127-07
    provides: "PyusbMissingError coverage + the sys.meta_path subprocess proof"
  - phase: 127-08
    provides: "the hoisted _finish() call site, A5 converted to measured, the fake-vs-real ctrl_transfer pin"
  - phase: 127-09
    provides: "VerifyResult, the DFU_UPLOAD readback sequence, the mock-only ceiling paragraph"
  - phase: 127-10
    provides: "the corrected install doc + its doc-vs-constant parity gate"
  - phase: 127-11
    provides: "the operator-authorised CI dispatch, both CI run IDs, the mypy fail-open finding and the 3-error fix"
provides:
  - "127-NONREGRESSION.md: every gate and figure this phase claims, re-executed in this session"
  - "HOST-01..HOST-08 all ticked in .planning/REQUIREMENTS.md, each citing its discharging plan"
  - "Both CI runs (30707902225, 30708836339) independently re-queried; run 30708836339 (head SHA string-equal to this session's HEAD) established as HOST-04's authoritative evidence"
  - "An independent, from-scratch mypy re-derivation (69 -> 72 -> 69) in a throwaway py3.11 venv, matching CI's own log exactly"
  - "The quotable mock-only HOST-03 ceiling paragraph for Phase 130's CLOSE-02 honesty ledger"
affects: [128-release-asset-fold, 129, 130-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Closing-sweep discipline: every figure re-executed in the closing session itself, never inherited from a prior plan's SUMMARY -- the Phase-116 four-times-in-one-phase premature-tick failure is prevented structurally by making exactly one plan permitted to tick, against rows it re-ran itself"
    - "Two-run CI comparison: when a mid-phase fix commit lands after the first CI dispatch, the closing sweep re-queries BOTH runs and names the one whose head SHA is string-equal to the sweep's own HEAD as authoritative, rather than accepting the first"
    - "Independent mypy re-derivation bypassing a known fail-open gate: a throwaway venv on a supported interpreter (python3.11, not the devcontainer's py3.12), invoking mypy via sys.executable -m mypy (not a bare PATH lookup), deleted immediately after measurement"

key-files:
  created:
    - .planning/phases/127-host-dfu-installer/127-NONREGRESSION.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "HOST-04 ticked against CI run 30708836339 (head SHA a62ca76..., string-equal to this session's HEAD) rather than the earlier run 30707902225 (head SHA 84cdd86..., pre-mypy-fix) -- the second run is on the phase's final tree and is the one Phase 130 would find if it re-queried today"
  - "The primary ci job's RED conclusion (mypy watermark, 69 > 35 on both runs) is recorded alongside HOST-04's tick but explicitly NOT folded into it -- HOST-04's claim is that ci-py32 installs .[test,py32] and exercises real pyusb, which it does, green, on both runs. The inherited mypy debt is a separate, pre-existing, non-Phase-127 finding"
  - "HOST-06 ticked with A1's residual named directly beside it in both REQUIREMENTS.md and 127-NONREGRESSION.md -- UM1504 was never fetched (two network-layer failures against st.com), so the DfuSe-specific literals remain consistent-with-the-module rather than independently sourced. The USB DFU 1.1 half of the anchor genuinely was fetched and read, so the tick is warranted, but not read as a fully independent oracle on every literal"
  - "The claim-gate trip on my own drafted prose (7 forbidden-phrase matches on the first pass) was resolved by rewording the ceiling section in the author's own words -- never by narrowing the gate's pattern list or the py32-token proximity window -- per the gate's own module docstring instruction"
  - "No requirement was ticked against a figure quoted from a prior SUMMARY. Every row cited in 127-NONREGRESSION.md's gate table was re-run in this session; where a figure matched a prior plan's own record (e.g. the 69/72/69 mypy sequence, the four flash-map constants), this session independently reproduced it rather than copying it"

requirements-completed: [HOST-01, HOST-02, HOST-03, HOST-04, HOST-05, HOST-06, HOST-07, HOST-08]

coverage:
  - id: D1
    description: "Every gate and figure this phase claims re-executed in this session against the live sibling-layout trees: merge-parent check, full suite, coverage, all eight primary ci.yml gates, seven named test modules, skip census, asset_candidates(), flash-map parity, three grep counts"
    verification:
      - kind: other
        ref: "127-NONREGRESSION.md §3 gate table (24 host-repo rows + 3 firmware-repo rows + 2 meta-repo rows), all re-run this session"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both CI runs re-queried read-only via gh; run 30708836339 confirmed on the final tree (head SHA string-equal to this session's HEAD), ci-py32 green, primary ci RED at the mypy watermark step (69 > 35)"
    requirement: "HOST-04"
    verification:
      - kind: other
        ref: "gh run view 30707902225 and 30708836339 --json ...; gh api .../logs for both mypy step and ci-py32 pytest step"
        status: pass
    human_judgment: false
  - id: D3
    description: "Independent mypy re-derivation in a throwaway python3.11 venv (bypassing the devcontainer's fail-open bare-mypy-from-PATH bug): 69 (pre-127) -> 72 (post-127 pre-fix) -> 69 (post-127 post-fix), matching CI run 30708836339's own log exactly"
    verification:
      - kind: other
        ref: "git archive snapshots of ccbc401 and 84cdd86, plus the working tree at a62ca76, each mypy-checked via <venv>/bin/python -m mypy firestarter/ tests/"
        status: pass
    human_judgment: false
  - id: D4
    description: "127-NONREGRESSION.md written with all required sections; claim gate run against it with an explicit target, exits 0 after two rounds of rewording (never by narrowing the gate)"
    verification:
      - kind: other
        ref: "python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py .planning/phases/127-host-dfu-installer/127-NONREGRESSION.md -> PASS, exit 0"
        status: pass
    human_judgment: false
  - id: D5
    description: "HOST-01..HOST-08 all ticked in REQUIREMENTS.md via a scoped edit (8 checkbox lines + 1 summary-table row only); HOST-03 cited to 127-08/127-09 only, never to 127-05/127-10; HOST-04 gated on the CI run URL"
    verification:
      - kind: other
        ref: "git diff .planning/REQUIREMENTS.md -- touches exactly 8 checkbox lines + 1 table row"
        status: pass
    human_judgment: false
  - id: D6
    description: "Both sub-repos unmodified by this plan: firestarter porcelain empty throughout; firestarter_app porcelain unchanged apart from its 5 known pre-existing lines. No push, tag, release, or gh workflow run performed"
    verification: []
    human_judgment: true
    rationale: "Absence of a destructive/outward-facing command cannot be proven by a unit test; confirmed by review of every Bash invocation in this session (only read-only gh queries, git status/log/diff, pytest, ruff, mypy, and two throwaway venvs that were deleted) and by re-checking both sub-repos' git status before the meta-repo commit."

# Metrics
duration: ~2h10m
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 12: Closing Non-Regression Sweep + Resolve HOST-01…HOST-08 Summary

**Every gate and figure Phase 127 claims was re-executed in this session against the live sibling-layout trees — including an independent, from-scratch mypy re-derivation (69 → 72 → 69) and a read-only re-query of both CI runs — and all eight of HOST-01…HOST-08 are now ticked in `REQUIREMENTS.md`, each citing the specific plan that discharges it; this is the only plan in the phase permitted to do either.**

## Performance

- **Duration:** ~2h10m
- **Started:** 2026-08-01
- **Completed:** 2026-08-01
- **Tasks:** 3/3 executed
- **Files modified:** 2 (1 new, 1 modified)

## Accomplishments

- Confirmed the layout precondition first: `basename "$PWD"` = `firestarter_app`, `../firestarter/.git` present, no `/dev/ttyACM*`/`/dev/ttyUSB*` attached.
- Re-derived HOST-01's structural claim: `git log -1 --format=%P 63ce44e` contains `4ee64a14a8933b60896c8b168bb1c7e34d788fa4`.
- Re-ran the full suite in this session: `1293 tests collected in 0.56s`; `1293 passed in 164.61s (0:02:44)`, 0 failed, 0 skipped, 30 snapshots passed. Coverage `81.88%` total (`py32_dfu.py` 79%).
- Re-ran all eight primary `ci.yml` gate commands locally, each exit 0 (the mypy watermark's local reading is the known devcontainer fail-open bug, recorded as such, not as a genuine clean run).
- Ran each of the seven named test modules individually: `test_py32_packaging.py` (12), `test_dfu_opcode_anchors.py` (7), `test_py32_channel_gating.py` (14), `test_py32_flash_map_host.py` (16), `test_pyusb_gating.py` (6), `test_py32_pyusb_absent.py` (11), `test_py32_dfu.py` (69).
- Confirmed the skip census (5 passed, `ALLOWED_SKIP_REASONS` still 4 entries), `test_pyusb_api_surface.py` not collected in the pyusb-absent full-suite run (0 occurrences), `importlib.util.find_spec("usb")` still `None`.
- Called `asset_candidates("py32f071")` directly and recorded the returned list: `['firestarter_py32f071.hex', 'firestarter_py32f071.bin']`.
- Quoted and compared both sides of the flash-map parity: host constants (`FLASH_BASE=0x8000000`, `APP_REGION_END=0x801e000`, etc.) against the live linker script read directly from `/workspaces/firestarter` — matching exactly.
- Confirmed the three grep counts: `pragma: no cover` = 2, `self\._finish(` = 1, `no such option` = 1.
- Re-took C-8's pyusb-present full-suite measurement on the final tree in a throwaway venv (deleted after): `1299 passed, 0 failed, 0 skipped` — identical outcome to the pyusb-absent run apart from the 6 additionally-collected tests.
- Re-queried **both** CI runs read-only via `gh run view`/`gh api .../logs`: run `30707902225` (head SHA `84cdd86...`, pre-mypy-fix, `ci-py32` green / `ci` RED at mypy 72>35) and run `30708836339` (head SHA `a62ca76...`, **string-equal to this session's own HEAD**, `ci-py32` green / `ci` RED at mypy 69>35) — the second is authoritative for HOST-04.
- Independently re-derived the mypy fail-open finding and the zero-net-debt claim: built a throwaway venv on `/home/vscode/.local/bin/python3.11`, installed `.[test]`, ran `mypy` via `sys.executable -m mypy` (never a bare `PATH` lookup) against `git archive` snapshots of `ccbc401` (69 errors) and `84cdd86` (72 errors) plus the current working tree (69 errors) — matching CI run `30708836339`'s own log exactly, then deleted the venv.
- Confirmed `git -C /workspaces/firestarter status --porcelain` empty and HEAD unchanged (`240fb19c...`) throughout.
- Wrote `.planning/phases/127-host-dfu-installer/127-NONREGRESSION.md` with all required sections. Ran the claim gate against it with an explicit target: first pass tripped on 7 forbidden-phrase matches (negated phrasing landing next to a `py32` token in the non-claims prose); reworded the prose twice (never narrowed the gate) until it passed clean.
- Ticked HOST-01…HOST-08 in `.planning/REQUIREMENTS.md` via a scoped edit (8 checkbox lines + 1 summary-table row only), each citing its discharging plan; HOST-03 cites only 127-08/127-09 (127-05/127-10 are traceability-only, per their own objectives); HOST-04 cites the authoritative CI run; HOST-06's tick names A1's residual beside it.
- Confirmed both sub-repos' porcelain: `firestarter_app` unchanged apart from its 5 known pre-existing lines; `firestarter` empty throughout.

## Task Commits

1. **Task 1: Re-execute every gate and figure (read-only sweep)** — no commit (captured into this SUMMARY, per the plan)
2. **Task 2 + Task 3: Write `127-NONREGRESSION.md` and resolve HOST-01…HOST-08 in `REQUIREMENTS.md`** — `3e2316e` (docs, meta repo)

**Meta-repo tracking commit:** pending (this SUMMARY + STATE.md/ROADMAP.md updates, committed next per `<final_commit>`)

## Files Created/Modified

- `.planning/phases/127-host-dfu-installer/127-NONREGRESSION.md` — the phase's evidence artifact: claim statements, baseline history (1158/1216/1293), the full gate table (host/firmware/meta/CI), all five ROADMAP criteria discharged, all nineteen decisions with corrections, informational findings (C-1, C-8, A1, A4, A5, the traceability gap, the mypy fail-open finding, the Phase-129 tripwire), and the quotable HOST-03 ceiling for Phase 130's CLOSE-02
- `.planning/REQUIREMENTS.md` — HOST-01…HOST-08 ticked; the Phase 127 summary-table row updated from `Pending` to `Complete`

## Decisions Made

See `key-decisions` in the frontmatter for the full list. Most load-bearing: HOST-04 is ticked against the **second** CI run (the one on the final tree, head-SHA-matched to this session), not the first; the primary `ci` job's mypy-debt RED is recorded but kept structurally separate from HOST-04's own claim; and the claim-gate trip on this document's own prose was fixed by rewording, never by narrowing the gate's forbidden-phrase list or proximity window.

## Deviations from Plan

None (Rule 1-4 sense). The claim-gate trip on the drafted artifact's own ceiling prose (7 forbidden-phrase matches, then 1 after a first reword) was anticipated by the plan itself (`127-CONTEXT.md`'s "self-reference trap" note) and resolved exactly as instructed — by rewording in the author's own words, never by weakening the gate. Not a deviation; the expected discipline, executed.

## Issues Encountered

- The claim gate's proximity-window design (D-16 in `check_permitted_claims.py`) correctly fired on an early, more literal phrasing of the non-claims section ("firmware runs on a PY32F071", "silicon-verified, bench-validated, or hardware-validated", "pin map is correct" — all within one line of a `py32` token). Resolved across two rewording passes; the second pass introduced "works end to end" as an unintended substitute forbidden phrase, caught by re-running the gate and fixed in a third, smaller edit.
- Both CI runs needed independent re-querying rather than accepting Plan 127-11's own recorded run (`30707902225`) — Plan 127-11 landed a mypy-fix commit (`a62ca76`) *after* recording that run, so a second, later run (`30708836339`) exists on the final tree and is the one this closing sweep must cite for HOST-04. Confirmed by checking `git rev-parse HEAD` in `firestarter_app` against both runs' `headSha` fields.

## User Setup Required

None — no external service configuration required. All CI queries were read-only (`gh run view`, `gh api .../logs`); no `git push`, `gh workflow run`, `gh release`, tag, or any `git stash` subcommand was executed in this session.

## Claim Ceiling

This plan re-executed the phase's evidence and resolved its eight requirements. It proves nothing about a PY32F071 board beyond what the eleven prior plans already built and this sweep re-confirmed: the target builds clean, the suites pass, the DFU sequence is exercised against device descriptors and mocks. `127-NONREGRESSION.md` §7 carries the mock-only HOST-03 ceiling as a quotable, self-contained paragraph for Phase 130's CLOSE-02 honesty ledger. No PCB exists; nothing in this document or in `127-NONREGRESSION.md` claims otherwise.

## Next Phase Readiness

- Phase 128 can cite `asset_candidates("py32f071")`'s recorded return value (`['firestarter_py32f071.hex', 'firestarter_py32f071.bin']`) as a measured fact, not an assumption — its Criterion 4 depends on this.
- Phase 129 will find `tests/test_py32_flash_map_host.py` named as the gate that goes RED the moment `BOOTLOADER` gets a non-zero length, pointing at `127-CONTEXT.md`'s `<deferred>` section — both the envelope gate and the doc-parity gate are built from `py32_dfu.APP_REGION_END`/`FLASH_BASE`, never a literal, so both will trip together.
- Phase 130's CLOSE-02 honesty ledger can quote `127-NONREGRESSION.md` §7's mock-only HOST-03 ceiling paragraph verbatim, plus the two adjacent non-claims (the untested DfuSe-vs-plain-DFU fork, and the narrow meaning of "success" on this path).
- Phase 130 (or a future gate-hardening phase under Phase 123's charter) still owns: the 69 inherited mypy errors (recorded, not fixed, per the operator's explicit scope decision), `tools/check_mypy_watermark.py`'s two stacked fail-open defects (bare `PATH` lookup + the py3.12/`python_version=3.9`/numpy-stub collapse), and A1's UM1504 residual (a future fetch attempt from a different network vantage point would fully discharge it).
- HOST-01…HOST-08 are now `Complete` in `.planning/REQUIREMENTS.md`'s traceability table, each citing `127-NONREGRESSION.md` §4/§5 for its discharging row — matching the shape Phases 124/125/126 already established for their own requirement blocks.

## Self-Check: PASSED

- FOUND: `.planning/phases/127-host-dfu-installer/127-NONREGRESSION.md`
- FOUND: commit `3e2316e` in meta-repo git log (`/workspaces`)
- CONFIRMED: `.planning/REQUIREMENTS.md` HOST-01…HOST-08 all `[x]`, summary-table row `Complete`
- CONFIRMED: claim gate exits 0 against `127-NONREGRESSION.md` with an explicit target
- CONFIRMED: `git -C /workspaces/firestarter_app status --porcelain` shows only the 5 known pre-existing lines
- CONFIRMED: `git -C /workspaces/firestarter status --porcelain` empty, HEAD unchanged at `240fb19c50190797ffdc2062d39390e074f8566f`
