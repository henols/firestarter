---
phase: 161-board-board-sweep-three-boards-on-rev-2-0
plan: 03
subsystem: bench
tags: [bench, on-device, cell-A1, uno, atmega328p, rev-2-0, w27c512, w29c020, sweep-position, board-01]

# Dependency graph
requires:
  - phase: 161-board-board-sweep-three-boards-on-rev-2-0 (plan 01)
    provides: append_evidence.py, PROCEDURE.md Amendment 3
  - phase: 161-board-board-sweep-three-boards-on-rev-2-0 (plan 02)
    provides: capture_provenance.py --board-probe-json/--no-image-plan seams (not needed by this cell, but proved arm-agnostic tooling), D-10 pre-proof
provides:
  - "Cell A1 (Uno + Rev 2.0) fully swept: four evidence positions, all `validated`"
  - "Derived D-08 W29C020 stall ceiling: 391.748 s (4x A1's measured control-arm wall-clock 97.937 s) — plans 161-04/161-05 inherit this, never recompute it"
  - "A1's 262144 B control-arm read wall-clock baseline: 73.344 s — a comparison baseline for A2/A3-B2, not a portable constant"
  - "BOARD-01 closed in full"
affects: [161-04, 161-05]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-position artifact layout (PD-1, Amendment 3): reads/<position_id>/, WRV-VERDICT_<id>.json, provenance_<id>.json — never a shared cell-root reads/ or written.bin"
    - "Append-then-render as one atomic pair after every position, never batched to teardown"
    - "P-06 (pot) settled by measurement, not operator declaration, when the operator's reply omits it — a single confirming vpp read taken by interrupting the tool's continuous-monitor design (no --once flag exists), never a re-invented tolerance band"
    - "Config-dir baseline drift (~/.firestarter changing) is recorded as a P-H1 finding with an explicit impact assessment, not silently absorbed or auto-fixed — product-code RCA stays out of scope (D-16)"

key-files:
  created:
    - .planning/v1.34/bench/cells/A1/ (CELL.md, POT.md, WRITE.md, SMOKE-W29C020.md, board_probe.json, board_probe_teardown.json, check_arms_pre_cell.json, check_arms_teardown.json, 4x provenance_<id>.json, 4x WRV-VERDICT_<id>.json, READBACK-VERDICT.json, readback_control/, readback_v133/, logs/ [46 invocation pairs])
  modified:
    - .planning/v1.34/bench/EVIDENCE.jsonl (+4 rows, all A1 positions)
    - .planning/v1.34/bench/EVIDENCE.md (re-rendered after each append)
    - .planning/STATE.md (SAFETY line hand-edited to true post-teardown state; plan pointer advanced 3->4)
    - .planning/REQUIREMENTS.md (BOARD-01 marked Complete; BOARD-04 deliberately left Pending — multi-plan requirement, A2/A3-B2 still owed)

key-decisions:
  - "P-06 (pot) was settled by Claude's single confirming vpp read rather than a re-prompt, when the operator's chip-seating reply omitted a pot declaration. The firestarter vpp CLI has no single-shot flag (confirmed via --help) and is an inherent continuous monitor ('Press Ctrl+C to stop'); the first reported reading (12.0V, matching the 12.0V target to the one-decimal precision used everywhere in this project) was taken as the confirming value and the process was then interrupted via SIGINT — one read, never a monitor loop, and not an invented numeric tolerance (none is stated anywhere in PROCEDURE.md/rig-pins.json)."
  - "The 600 s absolute fallback ceiling was used ONLY for position 2 (A1__control__w29c020) — the position that creates the derived figure — and named explicitly as a fallback in every record. From position 4 onward the derived 391.748 s ceiling (4x position 2's 97.937 s) was used and named as a derivation with its basis."
  - "The ~/.firestarter config-dir baseline check (Amendment 3 clause 4) fired CHANGED at teardown. Investigated every in-scope bench-tool source (check_arms.py, capture_provenance.py, judge_readback.py, probe_board.py) for an internal CLI subprocess call that could explain a non-transient port write to the default config dir; none found (every internal call either never invokes a real command, or passes explicit --port and inherits the correctly-set FIRESTARTER_CONFIG_DIR). Recorded as CHANGED — P-H1 with a full impact assessment (does not affect any of A1's four judged verdicts, since every judged command set FIRESTARTER_CONFIG_DIR inline directly and the judged oracles never consult the CLI's ConfigManager) rather than silently absorbed or investigated further into firestarter_app's product code (D-16 boundary — out of scope; handed to Phase 165). Mirrors the identical, previously-unresolved Phase 160 Plan 12 finding."

requirements-completed: [BOARD-01]

coverage:
  - id: D1
    description: "Cell A1 holds four evidence positions (control x W27C512, control x W29C020, v1.33 x W27C512, v1.33 x W29C020), each with a full-device read-back SHA verdict against its own distinct written image — no position blank, none inferred from another"
    requirement: "BOARD-01"
    verification:
      - kind: manual_procedural
        ref: "EVIDENCE.jsonl: 4 rows with cell_id==A1, each position_id exactly once, all outcome=validated, sha_verdict_judged=match, size_violations=[], verdict_disagreement=false; judge_wrv.py runtime output for each position"
        status: pass
    human_judgment: false
  - id: D2
    description: "All four positions carry RIG-02 provenance captured at P-02 (captured_at_step==2), before the cell's first test step, with each arm confirmed by an independent on-device read-back rather than assumed from the flash command"
    requirement: "BOARD-01"
    verification:
      - kind: manual_procedural
        ref: "4x provenance_A1__*.json: captured_at_step==2; READBACK-VERDICT.json (control, preserved in readback_control/): judged_match=true, judged_span_bytes=26026; READBACK-VERDICT.json (v133, preserved in readback_v133/): judged_match=true, judged_span_bytes=22952 — the two judged spans and the two sha_actual_judged values differ, confirming the arms are distinguishable in the record"
        status: pass
    human_judgment: false
  - id: D3
    description: "Each of the four positions records a measured write duration — wall-clock as the judged measure, the app's own success-only figure alongside as an unjudged second datum"
    requirement: "BOARD-04"
    verification:
      - kind: manual_procedural
        ref: "EVIDENCE.jsonl write_duration_wallclock_s non-null for all 4 A1 rows (41.305/97.937/41.037/97.916 s); WRITE.md pairs each with its app-reported figure (37.48/94.47/37.48/94.48 s)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The milestone's first 262144-byte write and first 262144-byte read on silicon happened here, and their measured wall-clocks became the derived D-08 stall ceiling every later W29C020 position uses"
    requirement: "BOARD-01"
    verification:
      - kind: manual_procedural
        ref: "Position 2 (A1__control__w29c020): write wallclock 97.937 s under the 600 s absolute fallback (named as such); read wallclock 73.344 s; derived ceiling 4x97.937=391.748 s recorded in WRITE.md and used, named as derived, at position 4 (97.916 s write, well under 391.748 s)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The W29C020 was proven addressable on this rig by a non-destructive chip-id and blank check before the milestone's first 262144-byte write"
    requirement: "BOARD-01"
    verification:
      - kind: manual_procedural
        ref: "SMOKE-W29C020.md: id w29c020 exit 0 (chip-id matched); standalone blank w29c020 exit 1, not-blank at 0x000000 (a valid, expected outcome per D-09's own design, not a failure); no forbidden flag used"
        status: pass
    human_judgment: false
  - id: D6
    description: "Each position's EVIDENCE.jsonl row was appended as that position completed, not at teardown, each append paired atomically with a render_evidence.py re-render"
    requirement: "BOARD-01"
    verification:
      - kind: manual_procedural
        ref: "render_evidence.py --check green after each of the 4 append_evidence.py calls (Tasks 5, 7, 11, 13); gate_record.py --jsonl 0 violations; run_gates.sh 12/12 selftests + 5/5 live gates, exit 0"
        status: pass
    human_judgment: false

# Metrics
duration: ~65min (executor wall-clock across the session; excludes operator checkpoint wait intervals between the six physical handovers)
completed: 2026-08-27
status: complete
---

# Phase 161 Plan 03: Cell A1 — Uno + Rev 2.0, Both Arms x Both Chips Summary

**Cell A1 fully swept on the Arduino Uno (ATmega328P, Rev 2.0 shield): four positions all `validated`, the milestone's first 262144-byte write/read on silicon measured (97.937 s / 73.344 s), and the derived W29C020 stall ceiling (391.748 s) established for cells A2 and A3/B2 to inherit — BOARD-01 closed.**

## Performance

- **Duration:** ~65 min executor wall-clock (13:13–14:18 UTC), across six operator physical checkpoints (mount+chip-out, seat+pot, swap to W29C020, chip-out for arm switch, seat W27C512 again, swap to W29C020 again, final chip-out)
- **Completed:** 2026-08-27T14:18Z
- **Tasks:** 15 (6 operator checkpoints, 9 automated)
- **Files modified:** 143 files across 10 task commits (bench cell artifacts, `EVIDENCE.jsonl`/`.md`, `STATE.md`, `REQUIREMENTS.md`)

## Accomplishments

- **All four A1 positions `validated`:** `A1__control__w27c512` (wall 41.305 s / app 37.48 s), `A1__control__w29c020` (wall 97.937 s / app 94.47 s — first 262144 B write on silicon), `A1__v133__w27c512` (wall 41.037 s / app 37.48 s, N=3 consistency set, all three reads agreed with each other and the written image), `A1__v133__w29c020` (wall 97.916 s / app 94.48 s, N=3 consistency set, clean). **No read-set disagreement anywhere in this cell — no escalation was due.**
- **Both arms proven and distinguishable by independent read-back**, never avrdude's own upload-time verify: control `judged_match=true`, `judged_span_bytes=26026` (control's own span via `hex_span_expected_by_arm`, never the legacy 22952 scalar), `sha_actual_judged=f60fa76f...`; v1.33 `judged_match=true`, `judged_span_bytes=22952`, `sha_actual_judged=dc2ae8a1...`. **The two arms' judged read-back SHAs differ** — itself evidence the A/B is a real firmware difference, not one image relabeled. Both arms' full read-back binary sets preserved side by side (`readback_control/`, `readback_v133/`).
- **D-09 addressability proof, W29C020:** chip-id matched (`0xDA45`); standalone `blank` reported not-blank at `0x000000` — a valid, expected outcome per D-09's own design (proves addressability, not blankness), never treated as a failure or forced past.
- **Derived D-08 W29C020 ceiling established: 391.748 s** (4x position 2's measured control-arm wall-clock, 97.937 s) — used, named as a derivation, at position 4 (97.916 s, well under it). Position 2 itself used the 600 s absolute fallback, named explicitly as a fallback, because it is the position that creates the derivation.
- **A1's 262144 B control-arm read baseline: 73.344 s** wall-clock — carried forward as a comparison baseline (not a portable constant, since the Uno moves 512 B chunks where the Leonardo moves 1024 B) for A2/A3-B2.
- **Both A/B pairs show no divergence on A1:** W27C512 control/v133 wall-clocks agree within 0.3 s (41.305 vs 41.037), app-reported figures identical (37.48 s both). W29C020 pair agrees within 0.02 s wall-clock (97.937 vs 97.916), 0.01 s app-reported (94.47 vs 94.48). Every figure is a **single write per position — a data point, not a spread** — explicitly stated as NOT comparable to v1.31's 0.37 s figure, which is a three-cycle app-reported spread on Leonardo hardware, not a wall-clock duration.
- **Per-cell gate (D-04) green:** `run_gates.sh` exit 0 (captured directly via `$?`), 12/12 tool selftests, ALL GATES PASSED (5/5 live gates). `gate_record.py --jsonl`: 0 violations.
- **A genuine finding surfaced, not buried:** `~/.firestarter/config.json` changed from the Amendment 3 pinned baseline during this plan's execution (mtime 07:59:25 -> 13:24:25 UTC, content now `{"port": "/dev/ttyACM1"}`). Investigated every in-scope bench-tool source; no internal CLI call explains it (every one either never invokes a real command, or passes explicit `--port` and inherits the correctly-set `FIRESTARTER_CONFIG_DIR`). Recorded as `CHANGED — P-H1` with a full impact assessment: does **not** affect any of A1's four judged verdicts, because every judged write/read/judge command set `FIRESTARTER_CONFIG_DIR` inline directly and the judged oracles (`judge_wrv.py`, `judge_readback.py`) never consult the CLI's `ConfigManager`. The frozen `FIRESTARTER_CONFIG_DIR` content SHA itself is independently confirmed unchanged. Mirrors the identical, still-unresolved Phase 160 Plan 12 finding — handed to Phase 165 (product code, D-16 boundary, not investigated or fixed here).
- **Both sub-repos byte-unchanged.** `firestarter/` ends on the v1.33 arm exactly as required (HEAD `5759dc8d`, the originally pinned SHA, meta's gitlink diff empty — no gitlink change to commit); `firestarter_app/` untouched throughout. No product code changed.

## Task Commits

Each task was committed atomically:

1. **Task 1: P-01 mount Uno, chip out, declare Rev 2.0** - `fa299270` (feat)
2. **Task 2: P-02 board-identity probe + pending provenance (4 positions)** - `b237c053` (feat)
3. **Task 3: P-03/P-04 control arm flashed + proven by read-back** - `57c68df1` (feat)
4. **Task 4: P-05/P-06 seat W27C512, pot confirmed by single vpp read** - `8bf204ac` (feat)
5. **Task 5: P-07 position 1 (`A1__control__w27c512`)** - `a861af2b` (feat)
6. **Task 6+7: P-08 swap + D-09 smoke + P-09 position 2 (first 262144B write)** - `bbfa5136` (feat)
7. **Task 8+9: P-10/P-04 v1.33 arm flashed + proven by read-back** - `2eaf60a7` (feat)
8. **Task 10+11: P-05(2nd arm)+P-07 position 3 (`A1__v133__w27c512`)** - `062eb68f` (feat)
9. **Task 12+13: P-08(2nd arm)+P-09 position 4 (`A1__v133__w29c020`)** - `c40f5797` (feat)
10. **Task 14+15: P-11 teardown, cell close, gate, STATE.md/REQUIREMENTS.md** - `9fe9c9f2` (feat)

**Plan metadata:** _pending — this SUMMARY's own commit_

## Files Created/Modified

- `.planning/v1.34/bench/cells/A1/` — `CELL.md` (full narrative: P-01 through P-11), `POT.md`, `WRITE.md` (per-position sections + A/B summary table), `SMOKE-W29C020.md`, `board_probe.json`/`board_probe_teardown.json`, `check_arms_pre_cell.json`/`check_arms_teardown.json`, 4x `provenance_A1__*.json`, 4x `WRV-VERDICT_A1__*.json`, `READBACK-VERDICT.json` (cell-root, ends on v133), `readback_control/` + `readback_v133/` (preserved six-artifact sets, both arms), `logs/` (46 numbered invocation pairs)
- `.planning/v1.34/bench/EVIDENCE.jsonl` / `EVIDENCE.md` — +4 rows (all A1 positions, all `validated`), re-rendered after each append
- `.planning/STATE.md` — SAFETY line hand-edited to the true post-teardown state (Uno connected on `/dev/ttyACM1`, socket empty, v1.33 arm, pot 12.0V untouched, plus the `~/.firestarter` P-H1 finding and its impact assessment); plan pointer advanced 3 of 5 -> 4 of 5
- `.planning/REQUIREMENTS.md` — BOARD-01 marked `[x]` Complete and its traceability row updated; BOARD-04 deliberately left `Pending` (multi-plan requirement — A2 and A3/B2 still owed their figures)

## Decisions Made

- **P-06 (pot) settled by measurement when the operator's reply omitted it.** Rather than re-prompting for a pot declaration the operator's chip-seating reply didn't include, Claude's single confirming `vpp` read was treated as the arbiter — consistent with Standing bench rule 4 (Claude takes exactly one confirming read; the operator adjusts the pot). The `vpp` CLI has no single-shot mode and is a continuous monitor by design; the first reading (12.0V) was taken and the process interrupted via `SIGINT`, never left to poll. No numeric tolerance is stated anywhere in `PROCEDURE.md`/`rig-pins.json` beyond the one-decimal precision this project records the figure at everywhere else — the reading matched the target exactly at that precision, so no invented tolerance band was needed.
- **The 600 s absolute fallback was used exactly once** (position 2, the position that creates the derived figure) and named as a fallback in every record; the 391.748 s derived figure was used, and named as derived with its basis, at position 4.
- **The `~/.firestarter` config-dir drift was recorded, investigated, and NOT fixed.** Root-causing `firestarter_app`'s `ConfigManager`/`serial_comm.py` internals is product code, out of scope under this plan's D-16 boundary. The investigation performed (checking every in-scope bench tool for an internal CLI call that could explain it) ruled out every candidate this plan's own tooling controls, and the impact assessment confirms it did not touch any judged result. Handed to Phase 165 rather than silently absorbed.

## Deviations from Plan

### Auto-fixed Issues

None that required a code change — this plan touches only bench artifacts and hand-edited planning docs, never `firestarter/` or `firestarter_app/` source.

### Findings Recorded, Not Fixed (Rule 4 territory — architectural/out-of-scope, surfaced rather than resolved)

**1. [Recorded, not auto-fixed — D-16 boundary] `~/.firestarter/config.json` changed from the Amendment 3 pinned baseline**
- **Found during:** Task 15 (P-11 teardown, config-dir assertion 1 of 2)
- **Issue:** `config.json`'s mtime advanced from the pinned baseline's `07:59:25 UTC` to `13:24:25 UTC` during this plan's execution, and its content changed to `{"port": "/dev/ttyACM1"}` — the "port" key is written only by `ConfigManager.remember_port()`, which should not persist a `--port`-typed value (marked transient). Every direct CLI invocation this plan made carried explicit `--port` and an inline `FIRESTARTER_CONFIG_DIR=` prefix; every in-scope bench-tool's internal CLI call either never invokes a real command or also carries explicit `--port` and inherits the correctly-set env var. No in-scope source explains the write.
- **Fix:** None applied — this is product-code (`firestarter_app`) behavior, forbidden to touch under this plan's "no product code" rule. Recorded as `CHANGED — P-H1` in `CELL.md` and `STATE.md`'s SAFETY line, with the full investigation and an explicit impact assessment (does not affect any of A1's four judged results).
- **Files modified:** None in `firestarter_app/` (confirmed byte-unchanged). Documentation only: `CELL.md`, `STATE.md`.
- **Verification:** The frozen `FIRESTARTER_CONFIG_DIR` content SHA is independently confirmed unchanged (`check_arms_teardown.json`); all four A1 provenance records carry a matching, non-null `config_dir_sha`.
- **Committed in:** `9fe9c9f2` (Task 14+15 commit)

---

**Total deviations:** 0 code fixes; 1 finding recorded and investigated but deliberately not fixed (out of scope, product code, handed to Phase 165).
**Impact on plan:** None on this cell's own results — all four positions are `validated` regardless. The finding is a genuine, previously-recurring config-hygiene issue (mirrors Phase 160 Plan 12's identical, still-unresolved carry-forward) surfaced for Phase 165's RCA, not a defect in this plan's own execution or tooling.

## Issues Encountered

- **The operator's Task 4 checkpoint reply confirmed chip seating but omitted a pot declaration.** Resolved per the orchestrator's explicit direction: took the single confirming `vpp` read as the arbiter rather than re-prompting, recorded honestly that the operator did not declare it in words (see `POT.md`).
- **The `vpp` CLI command has no single-shot mode** and ran as a continuous monitor until interrupted — handled per Standing bench rule 4 (one reading taken, then `SIGINT`, never a polling loop).
- **A three-run 262144 B consistency-check invocation (position 4's read) ran ~219 s**, exceeding the Bash tool's default 120 s foreground timeout and moving to background automatically; waited for completion rather than polling aggressively, per the harness's own background-task notification contract.

## Known Stubs

None. Every field in every artifact this plan produced is either a real measured value or an explicit `"not measured — <reason>"` placeholder — no blank or fabricated value anywhere.

## Threat Flags

None beyond the plan's own `<threat_model>` (T-161-11..16, T-161-SC), all of which this plan's execution satisfies as designed: the arm was proven only by `judge_readback.py` against `hex_span_expected_by_arm[arm]`, never by version string (T-161-11); per-position `reads/<position_id>/` directories with `read_count`/`size_violations` assertions prevented cross-position contamination at every position (T-161-12); `judge_wrv.py`'s SHA against the written image was the sole oracle at every position, with the app's 0/1/2 stored separately and never substituted (T-161-13); D-08 ceilings with `timeout --signal=INT` and full stdout/stderr capture bounded every write (T-161-14); zero forbidden flags reached any command, verified by direct inspection of every recorded argv (T-161-15); zero non-clean positions meant zero force-adds — nothing beyond the ignored `cells/*/reads/` was committed (T-161-16); zero package installs (T-161-SC).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Plan 161-04 (cell A2, uno328pb)** inherits: the derived D-08 W29C020 stall ceiling **391.748 s** (4x A1's measured control-arm wall-clock) — to be used directly, never recomputed, unless A2's own figures show high variance (in which case the widening must be stated explicitly, per D-08). A1's 262144 B control-arm read baseline (**73.344 s**) is a comparison figure, not a portable constant. `BRINGUP-uno328pb-v133/READBACK-VERDICT.json` (from Plan 161-02) gives A2 a proven, in-hand v1.33-arm result on this exact MCU before A2's own cell runs.
- **Plan 161-05 (cell A3/B2, Leonardo)** inherits the same derived ceiling and read baseline, plus `BRINGUP-leonardo-provenance/PREPROOF.md`'s measured `P-02` command sequence from Plan 161-02. A3/B2 is the **only** cell where v1.31's 0.37 s figure is a valid (if still apples-to-oranges) comparison point — A1 (Uno) draws no such comparison, correctly.
- **The `~/.firestarter` config-dir drift finding** (recorded, not fixed) should be watched by A2 and A3/B2's own `P-11` teardown assertions — if it recurs, that strengthens the case for Phase 165 to treat it as a systemic (not one-off) `firestarter_app` defect rather than session noise.
- BOARD-01 is closed. BOARD-04 remains open, needing A2's and A3/B2's write-duration figures before it can close.
- Both sub-repos (`firestarter/`, `firestarter_app/`) confirmed byte-unchanged (`git status --porcelain` empty) throughout; `firestarter/`'s gitlink ends at the originally pinned v1.33 SHA with zero diff to commit.

---
*Phase: 161-board-board-sweep-three-boards-on-rev-2-0*
*Completed: 2026-08-27*

## Self-Check: PASSED

All claimed files verified present on disk; all claimed commit hashes (`fa299270`, `b237c053`, `57c68df1`, `8bf204ac`, `a861af2b`, `bbfa5136`, `2eaf60a7`, `062eb68f`, `c40f5797`, `9fe9c9f2`) verified in `git log --oneline --all`.
