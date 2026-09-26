---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 06
subsystem: bench-procedure
tags: [procedure, bench-discipline, arm-agnostic, gate, markdown-parser]

requires:
  - phase: 160-01
    provides: "rig-pins.json (avrdude binary/conf, per-target mcu/programmer/baud/judged_span_policy, arm venv_bin paths, chips.*.vpp_mv, forbidden_flags, pio_project_dir)"
  - phase: 160-03
    provides: "tools/gen_addr_image.py's --stamp-width/SIZE/MASK/OUT_PATH CLI shape and bench/IMAGE-PLAN.json's per-position mask/stamp_width/sha256 table the procedure's write steps reference"
  - phase: 160-04
    provides: "tools/probe_board.py, tools/capture_provenance.py and tools/gate_record.py CLI shapes (flags cited verbatim in the procedure), and capture_provenance.py's captured_at_step=2 constant that fixes P-02's place in the derived order"
  - phase: 160-05
    provides: "tools/judge_readback.py and tools/judge_wrv.py CLI shapes, and judge_readback.py's PENDING-xshowvector refusal that P-04's text must not assume away on uno328pb"
provides:
  - "PROCEDURE.md — the eleven-step (P-01..P-11), two-halt-branch (P-H1/P-H2), nine-section arm-agnostic per-cell bench procedure Phases 161-163 execute unchanged"
  - "tools/render_steps.py — the SC#3 empty-step-list-diff gate: parses PROCEDURE.md's Step list section, renders one line per step per arm with substitution tokens emitted literally, and fails closed on a malformed or empty step list"
affects: ["160-08", "160-09", "160-10", "160-11", "160-12", "160-13", "161", "162", "163"]

tech-stack:
  added: []
  patterns:
    - "render_steps.py never expands a substitution token (including $ARM_BIN) — it only filters step INCLUSION by an [arm: name] annotation marker, so an arm entering a step's TEXT (rather than its argv value) is structurally impossible to hide from the diff"
    - "A step's rendered 'imperative text' is its full body flattened onto one line (heading title + every paragraph/code line joined with single spaces), not just the heading — this is what makes $ARM_BIN and the other literal command shapes visible in the render rather than only in prose the gate never touches"
    - "Pure parse/validate/render functions (extract_step_list_section, parse_steps, validate_steps, render_for_arm) kept separate from the argparse/file-I/O wrapper in main(), so --selftest exercises every check via hand-built fixture strings with zero filesystem/device dependency beyond a temp dir"

key-files:
  created:
    - .planning/v1.34/PROCEDURE.md
    - .planning/v1.34/tools/render_steps.py
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "P-02 (re-verify port identity) is where capture_provenance.py's hardcoded captured_at_step=2 constant is satisfied, but the tool's own full-record WRITE is deferred to the end of each chip's write-read-verify sequence (P-07/P-09) — capture_provenance.py hard-refuses to run without judge_readback.py's readback_verdict.json already existing (a precondition only true after P-04), so the plan's own draft phrasing ('runs capture_provenance.py for this position, then flashes') could not be followed literally without violating that tool's actual contract. The record's captured_at_step:2 field remains truthful because the identity fields it carries (board signature, controller string) were LIVE-VERIFIED at step 2 via probe_board.py/hw, even though the JSON file itself is written later once every field it needs exists."
  - "Firmware arm switching (unlike the host app's two worktrees) uses a single firestarter/ checkout with an in-place 'git checkout <fw_sha>' at P-04, because rig-pins.json/arms-provenance.json show no per-arm firmware worktree exists — only the host app got one (D-06 was scoped to the app). The 'arm implicit in the working tree' risk D-06 rejected for the app is mitigated the same way D-08 mitigates it for the app: the post-checkout fw_sha and an empty firmware porcelain check are both recorded fields, so a forgotten/wrong checkout is caught by the record rather than silently trusted."
  - "The control arm's 'single read normally' (D-11) is expressed as a plain 'read <chip> <cell_dir>/reads/run_01.bin' invocation (using the read command's positional output-file argument, per rig-pins.json's 'no -o flag' note) rather than 'dev consistency-check --runs 1' (invalid — the app's own contract floors --runs at 2). This keeps the control arm's default file naming compatible with judge_wrv.py's run_*.bin glob without inventing a new tool flag, and the escalation path (control's own N=3, fired only on a v1.33 disagreement) switches to the identical 'dev consistency-check --runs 3' shape the v1.33 arm always uses."
  - "render_steps.py flattens each step's FULL body (not just its heading) into the emitted line, specifically so $ARM_BIN and the procedure's other literal command-shape tokens are visible in the rendered output — the plan's own verify block greps the control render for the substring 'ARM_BIN', which a heading-only render (my first draft) could not satisfy since none of my step headings happen to contain a command line."
  - "Two literal-string mentions of the full step-id range ('P-01'..'P-11' together, and a forward reference to 'P-08' inside P-06's prose) had to be reworded during authoring because the plan's own verify script asserts ascending order by FIRST OCCURRENCE of each id string in the whole file, and an early summary sentence naming the full range would make 'P-11' appear before 'P-02' ever does. Resolved by describing the step count/order without repeating every id verbatim in prose that precedes the Step list section."
  - "Post-hoc fix (orchestrator spot-check): FIRESTARTER_CONFIG_DIR is established inline on every command line that invokes an arm binary or shells out to one ('FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN ...'), never by a session export, per Standing bench rule 9 — because config.py computes HOME_PATH/DATABASE_FILE/PIN_MAP_FILE as import-time constants, a variable exported after process launch or in a different shell silently leaves those three pointed at the unset default."
  - "P-11's config-dir check does NOT rely on gate_record.py's argv re-parse to detect a missing FIRESTARTER_CONFIG_DIR, despite the orchestrator's suggestion that it 'can already see' this — a shell-level VAR=val assignment is stripped by the shell before exec and never appears in a recorded argv, at every level this procedure's tools shell out through, so there is structurally nothing for an argv inspector to find. The actually-falsifiable proxy used instead: ~/.firestarter's continued absence, plus gate_record.py's existing check_config_dir_sha re-verification with a non-null-field requirement so the SHA check cannot pass by silently never running."

requirements-completed: [RIG-03]

coverage:
  - id: D1
    description: "PROCEDURE.md authored — eleven-step derived order (P-01..P-11), two halt branches (P-H1 rig-failure/P-H2 cell-failure), nine required sections, the $ARM_BIN substitution token with no arm-conditional step text, the two-state outcome taxonomy restated without relaxing Phase 145 D-14, and the write-duration definition resolving v1.31's 0.37s figure from the record — Task 1"
    requirement: "RIG-03"
    verification:
      - kind: unit
        ref: "python3 -c \"...\" structural check: 11 step ids ascending, P-H1/P-H2 present, all 9 '## ' section headings present, literal '$ARM_BIN' and '$FIRESTARTER_CONFIG_DIR' tokens present (rc=0, quoted in this SUMMARY; re-verified after the post-hoc fix commit)"
        status: pass
      - kind: unit
        ref: "bash content-marker grep: P-H1, P-H2, 'once per cell', 'wall clock', '0.37', 'same line', 'silkscreen' all present (rc=0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "tools/render_steps.py authored and the SC#3 diff gate observed both green (real PROCEDURE.md, both arms) and red (a temporary arm-conditional copy of the same real document) — Task 2"
    requirement: "RIG-03"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/render_steps.py --selftest (rc=0, 1 positive + 6 negative legs PASS)"
        status: pass
      - kind: other
        ref: "live diff of --arm control vs --arm v133 against the real committed PROCEDURE.md: both renders 11 lines, diff empty, 'ARM_BIN' appears 6 times in the control render, no arm worktree path leaked (quoted in this SUMMARY)"
        status: pass
      - kind: other
        ref: "live diff against a temporary copy of PROCEDURE.md with one step marked [arm: control]: control renders 11 lines, v133 renders 10, non-empty diff (quoted in this SUMMARY); committed PROCEDURE.md confirmed byte-unchanged via git diff --stat"
        status: pass
      - kind: other
        ref: "post-hoc: re-ran --selftest (7/7) and the live diff against the FIRESTARTER_CONFIG_DIR fix commit (9a6f29cb) -- both arms still render 11 byte-identical lines, ARM_BIN and FIRESTARTER_CONFIG_DIR both appear 5x each in the control render"
        status: pass
    human_judgment: false

duration: ~75min
completed: 2026-08-26
status: complete
---

# Phase 160 Plan 06: The Arm-Agnostic Cell Procedure and Its Diff Gate Summary

**Wrote `PROCEDURE.md`'s derived eleven-step cell run (mount → identity → chip-out → flash+read-back-judge → pot → write→read→judge ×2 chips → arm switch → teardown) with two named halt branches and `$FIRESTARTER_CONFIG_DIR` established inline on every app invocation, then authored `render_steps.py` — the tool that turns SC#3's "no step differs by arm" claim into an enforced, falsifiable diff gate, observed both empty (the real document) and non-empty (a deliberately arm-conditional copy of it).**

## Performance

- **Duration:** ~75 min (includes a post-hoc orchestrator-spot-check fix)
- **Started:** 2026-08-26T23:05Z (context load)
- **Completed:** 2026-08-26T23:40Z initial; fix follow-up completed same session
- **Tasks:** 2/2, both `type="auto"`, plus one targeted post-hoc fix commit
- **Files modified:** 2 created (`PROCEDURE.md`, `tools/render_steps.py`), 2 modified (`REQUIREMENTS.md`; `PROCEDURE.md` again for the fix)

## Accomplishments

- `.planning/v1.34/PROCEDURE.md` prescribes the derived eleven-step order Pattern 6 (RESEARCH.md) lays out: the chip-out window on `uno`/`uno328pb` covers both the flash *and* its independent read-back proof (an avrdude read is the same electrical situation as a write), the Leonardo is named exempt, the pot is set **once per cell** (both bench chips declare `vpp_mv: 12000`), and the two-chip rotation (`P-05`→`P-09`) sits inside a single arm's pass before `P-10` switches to the other arm, control first.
- Every step names its performer, its literal command shape (using the tools authored in plans 03-05, with flags verified against each tool's own `argparse`/Click definition — `probe_board.py --target/--port/--pins/--out`, `judge_readback.py --target/--port/--flashed-arm/--expect-arm/--out-dir/--pins`, `gen_addr_image.py --stamp-width SIZE MASK OUT_PATH`, `judge_wrv.py --written/--reads/--expect-size/--app-verdict/--position-id/--pins/--out`, `capture_provenance.py --cell-id/--position-id/--arm/--target/--port/--chip/--shield-rev/--pins/--out`, plus the app's own `-p/--port` global option before `hw`/`vpp`/`write`/`read`/`dev consistency-check`), and the record fields it contributes.
- The `## Outcome taxonomy` section states the two-state cell-outcome axis (`validated`/`skipped-with-reason`) and the *separate* three-state Phase-165 triage axis, explicit that Phase 145's ban on a third cell state is not relaxed.
- The `## Halt policy` section defines `P-H1` (rig failure — halt, fix in-phase) and `P-H2` (cell failure — record, carry to Phase 165, sweep continues), and states the prior bench phase's halt-and-`/gsd-debug` policy is deliberately not inherited.
- The `## Write-duration definition` section names wall-clock as the judged measure and the app's own success-line figure as an unjudged second datum, then resolves v1.31's 0.37 s W27C512 figure from `145-BENCH-LOG.md`: it is the **spread** (max−min: 106.06/105.69/106.06 s) of three cycles' **app-reported** success-line figures, never an independently wall-clocked duration and never a single write's time — so v1.34's per-position wall-clock figures are a different quantity by a different method, stated as a Phase 166 honesty-ledger line rather than drawn as a silent comparison.
- The `## Forbidden invocations` section names every entry in `rig-pins.json`'s `forbidden_flags` plus bare `firestarter`, the host app's own `fw -i` install path, the stale avrdude 6.3, and the wrong-cwd `pio` case, each with its reason — including the superseded-framing correction that `-b`/`--no-blank-check` does **not** also skip the erase (current help text: the erase still runs).
- `tools/render_steps.py` parses `PROCEDURE.md`'s `## Step list` section, and for `--arm control`/`--arm v133` emits one `<id>\t<text>` line per step in document order, with every substitution token (including `$ARM_BIN`) emitted **literally, never expanded** — the arm enters a step only through inclusion (an `[arm: name]` marker in the heading), never through altered text. Fails closed with a named `FAIL:` reason on an absent `## Step list` section, a section with zero step headings, a duplicate step id, out-of-ascending-order ids, or an annotation naming an unknown arm.
- `--selftest` passes 7/7 legs (1 positive + 6 negative, all named individually). The plan's own falsification leg — a single `[arm: ...]`-annotated step producing a **non-empty** diff — is the most important of the six and is exercised both in `--selftest` and, separately, live against a temporary copy of the real committed `PROCEDURE.md` (quoted below); the committed file itself was never touched.
- The live gate against the real `PROCEDURE.md`: both arms render exactly 11 lines, the diff is empty, and `ARM_BIN` appears 6 times in the control render with zero arm-worktree-path leakage — so the empty diff is not the empty-output tautology T-160-41 exists to catch.
- `.planning/REQUIREMENTS.md`: `RIG-03`'s checkbox and traceability-table row hand-edited to `Complete` (this plan's own "Requirement completion" section states it closes RIG-03 in full) — a targeted hand edit, not the `requirements mark-complete` GSD verb, per standing memory that verb reformats the whole file.
- Both sub-repos (`firestarter`, `firestarter_app`) confirmed porcelain-clean throughout; no file outside this plan's declared `files_modified` plus `REQUIREMENTS.md`/`STATE.md`/`ROADMAP.md` was touched.

## Task Commits

1. **Task 1: Write `PROCEDURE.md`** — `6fbfdc46` (docs)
2. **Task 2: Author `tools/render_steps.py` and observe the SC#3 diff gate both green and red** — `812fd2d9` (feat)
3. **Post-hoc fix: establish `FIRESTARTER_CONFIG_DIR` at process launch, close the vacuous P-11 oracle** — `9a6f29cb` (fix)

**Plan metadata:** committed below (this SUMMARY + REQUIREMENTS.md/STATE.md/ROADMAP.md)

## Files Created/Modified

- `.planning/v1.34/PROCEDURE.md` — the arm-agnostic eleven-step per-cell bench procedure (Task 1)
- `.planning/v1.34/tools/render_steps.py` — the SC#3 empty-step-list-diff gate (Task 2)
- `.planning/REQUIREMENTS.md` — `RIG-03` checkbox + traceability row marked `Complete` (hand-edited)

## Decisions Made

See `key-decisions` in the frontmatter for the full list with rationale. Summary:

- `capture_provenance.py`'s full-record write happens at the end of each chip's write-read-verify sequence (`P-07`/`P-09`), not literally "before the flash" as an earlier draft phrasing might suggest — because the tool hard-refuses without `judge_readback.py`'s verdict file, which only exists after `P-04`. Its `captured_at_step: 2` field stays truthful because the identity fields it carries were live-verified at `P-02`.
- Firmware arm-switching uses an in-place `git checkout <fw_sha>` at `P-04` (no second firmware worktree exists, unlike the host app's two), mitigated by recording the post-checkout `fw_sha` and an empty porcelain check — the same class of mitigation D-08 applies to the app.
- The control arm's normal single read uses the plain `read <chip> <path>` command (positional output path, matching `judge_wrv.py`'s `run_NN.bin` glob by naming convention) rather than `dev consistency-check --runs 1`, which the app's own contract forbids (floor of 2).
- `render_steps.py` renders a step's full body (not just its heading) so that `$ARM_BIN` and other literal command-shape tokens are visible in the output, satisfying the plan's own `grep -q "ARM_BIN"` verify leg.
- Two early-draft sentences that named the full `P-01`..`P-11` range (or forward-referenced `P-08`) in prose preceding the Step list section were reworded, because the plan's own ascending-order verify check is keyed to each id's *first* textual occurrence in the whole file.

## Deviations from Plan

**1. [Rule 1 - Bug] Reworded two forward-referencing prose sentences that broke the plan's own ascending-order check**
- **Found during:** Task 1 verification (running the plan's automated structural check against my first draft)
- **Issue:** An introductory sentence naming the full step-id range (`P-01`…`P-11`) together, and a `P-06` sentence forward-referencing `P-08`, made `P-11`'s and `P-08`'s *first* occurrence in the file precede several lower-numbered ids' first occurrence — failing the plan's own `assert pos==sorted(pos)` check.
- **Fix:** Reworded both sentences to describe the step count/position without repeating a not-yet-reached id verbatim.
- **Files modified:** `.planning/v1.34/PROCEDURE.md`
- **Verification:** Re-ran the plan's exact verify script; `pos==sorted(pos)` now holds.
- **Committed in:** `6fbfdc46` (Task 1 commit — found and fixed before the first commit, not a follow-up)

**2. [Rule 1 - Bug] `render_steps.py`'s first design (heading-only render) could not satisfy the plan's own `ARM_BIN` grep leg**
- **Found during:** Task 2, running the plan's exact verify commands after the first implementation
- **Issue:** My initial `parse_steps()` captured only each step's short heading title (e.g. "Mount and declare"), which never contains a literal `$ARM_BIN` token — none of `PROCEDURE.md`'s eleven headings happen to spell out a command. The plan's verify block asserts `grep -q "ARM_BIN" "$A"` against the rendered control output.
- **Fix:** Redesigned `parse_steps()` to capture and flatten each step's *full body* (every paragraph and code line between its heading and the next), onto one line, so the literal command shapes — and their `$ARM_BIN` tokens — are part of the emitted text.
- **Files modified:** `.planning/v1.34/tools/render_steps.py`
- **Verification:** Re-ran the live gate; `ARM_BIN` appears 6 times in the control render, diff against `v133` still empty, still 11 lines each.
- **Committed in:** `812fd2d9` (Task 2 commit — found and fixed before the first commit)

**3. [Rule 1 - Bug, post-hoc orchestrator spot-check] `$FIRESTARTER_CONFIG_DIR` was referenced at P-11 but never established anywhere, making P-11's SHA check vacuous**
- **Found during:** Orchestrator spot-check after this plan's initial completion — `FIRESTARTER_CONFIG_DIR` appeared exactly once in the whole document (P-11's "re-verify content SHA is unchanged"), never set. Every bench app invocation would have silently resolved `firestarter_app/firestarter/config.py`'s import-time `HOME_PATH`/`DATABASE_FILE`/`PIN_MAP_FILE` constants against the unset default (`~/.firestarter`, confirmed absent — 160-01's clean slate), defeating D-07 and making P-11's "SHA unchanged" pass vacuously, since nothing would ever have written to the frozen dir in the first place.
- **Fix:** Added `$FIRESTARTER_CONFIG_DIR` to the substitution-token table (pinned value from `rig-pins.json`'s `config_dir`, not arm-dependent); added Standing bench rule 9 stating the import-time-vs-call-time nuance and requiring the variable be set **inline** on every command line, never by a session `export` (which the fresh-shell case defeats); set `FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR` inline on every `P-02`/`P-06`/`P-07`/`P-09` command that invokes `$ARM_BIN` directly or shells out to it (`capture_provenance.py`); rewrote P-11's check as two assertions in order rather than one: (1) `~/.firestarter` still does not exist — the actually-falsifiable proxy, since a shell-level `VAR=val cmd` assignment is stripped before exec and therefore never appears in any recorded `argv`, meaning `gate_record.py`'s argv re-parse literally has nothing to inspect for this (a correction to the orchestrator's own "which gate_record.py's argv re-parse can already see" framing, made explicit in the procedure text rather than silently followed); (2) only then, the `config_dir_sha` re-verification via `gate_record.py`'s existing `check_config_dir_sha`, plus a non-null-field check so the SHA comparison cannot pass by silently never running.
- **Files modified:** `.planning/v1.34/PROCEDURE.md`
- **Verification:** Re-ran the plan's full structural + content-marker check (all pass); re-ran `render_steps.py --selftest` (7/7 legs, unchanged); re-diffed `--arm control` vs `--arm v133` against the edited document — still 11 byte-identical lines each, SC#3 diff still empty, `ARM_BIN` and `FIRESTARTER_CONFIG_DIR` both appear literally in the render (5 occurrences each).
- **Committed in:** `9a6f29cb` (fix commit, post-completion)

---

**Total deviations:** 3 auto-fixed (2 Rule 1 bugs found against the plan's own verify commands during initial execution; 1 Rule 1 bug found by orchestrator spot-check after initial completion and fixed in a targeted follow-up commit). None changed scope.
**Impact on plan:** None on scope. All three fixes were needed for correctness — two to satisfy the plan's own automated verification, one to make D-07's config-dir isolation seam and P-11's oracle actually non-vacuous rather than merely present in prose.

## Issues Encountered

**A genuine ordering tension in the plan's own action text, resolved and documented rather than silently reconciled.** The plan's Task 1 action text describes `P-04` as "Claude runs `capture_provenance.py` for this position, then flashes the arm... then proves the flash with `judge_readback.py`" — but `capture_provenance.py` (authored in plan 04) hard-refuses to run without `judge_readback.py`'s (plan 05) `readback_verdict.json` already existing for that cell/arm. Following the plan's literal sub-order inside `P-04` would make every real invocation of `capture_provenance.py` fail on its very first cell. Resolved by keeping `P-04` as flash-then-judge only, and placing `capture_provenance.py`'s actual invocation at the close of each chip's write-read-verify sequence (`P-07`/`P-09`), once its precondition is satisfiable — while preserving the *textual* fact the plan actually cared about (RIG-02's "before any test step" identity capture happening at logical step 2), via `capture_provenance.py`'s own `captured_at_step: 2` constant and `P-02`'s live identity verification. Documented as a key decision above rather than filed as a Rule 4 architectural question, because no tool code changed and no new capability was invented — only the procedure's prose was written to match the tools' actual, already-authored preconditions.

No blocking issues. No auth gates.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `PROCEDURE.md` is ready for Phases 161-163 to execute unchanged, citing its step ids. Plans 08-10 (bring-up) should read `P-04`'s firmware-checkout sub-step and `P-06`'s VPP-guard-restart clause carefully, since those are the two places this procedure's prose makes a claim (the checkout mitigation; the guard-restart-from-`P-06`) that has not yet been exercised against a live board.
- `render_steps.py` is ready to run as a standing gate at the start of every future cell-executing plan (08-13): `diff <(render_steps.py --arm control) <(render_steps.py --arm v133)` should stay empty for the life of this milestone; a non-empty result means an edit introduced an arm-conditional step and must be treated as a stop-and-report, not silently merged.
- RIG-03 is marked `Complete` in `REQUIREMENTS.md`, per this plan's own "Requirement completion" section — no other requirement's status changed.
- Open item for the bring-up plans (not blocking this plan): this procedure resolves the firmware arm-switching mechanism as an in-place `git checkout` (no second firmware worktree, unlike the host app's two) — plans 08-10 are the first point this gets exercised against a live board and should confirm the mitigation (recorded `fw_sha` + empty porcelain) is sufficient in practice.
- Post-hoc fix applied and verified: `$FIRESTARTER_CONFIG_DIR` is now established inline on every app invocation in the procedure, and P-11's config-dir check is a non-vacuous two-assertion gate (`~/.firestarter` absence, then the `config_dir_sha` re-verification). Plans 08-13 should follow `PROCEDURE.md` as committed at `9a6f29cb`, not the earlier `812fd2d9` state.
- No blockers.

## Self-Check: PASSED

- `FOUND: .planning/v1.34/PROCEDURE.md`
- `FOUND: .planning/v1.34/tools/render_steps.py`
- `FOUND: commit 6fbfdc46` (Task 1)
- `FOUND: commit 812fd2d9` (Task 2)
- `FOUND: commit 9a6f29cb` (post-hoc fix)
- `python3 .planning/v1.34/tools/render_steps.py --selftest` → rc=0 (7/7 legs, re-verified after the fix)
- Live SC#3 gate against the real `PROCEDURE.md` (post-fix): diff empty, 11 lines each arm, `ARM_BIN` and `FIRESTARTER_CONFIG_DIR` both present (5x each)
- Live SC#3 gate against a temporary arm-conditional copy: diff non-empty (11 vs 10 lines); `git diff --stat -- .planning/v1.34/PROCEDURE.md` → empty (committed file unchanged)
- `git -C /workspaces/firestarter status --porcelain` → empty
- `git -C /workspaces/firestarter_app status --porcelain` → empty

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-26*
