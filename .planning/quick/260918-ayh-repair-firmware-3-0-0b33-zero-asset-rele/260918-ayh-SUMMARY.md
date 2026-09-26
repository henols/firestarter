---
phase: 260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele
plan: 01
subsystem: release-ops
tags: [github-actions, beta-build, gh-cli, issue-triage, firmware-release]

requires: []
provides:
  - "GitHub pre-release `3.0.0b33` in `henols/firestarter_fw` carries `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex` (plus a bonus `firestarter_py32f071.hex`)"
  - "#67 and #68 closed with `fix:released`, comment naming firmware `3.0.0b33` / host `3.0.0b48`"
  - "#2 and #5 closed with a factual comment each"
  - "#15 and #16 left OPEN, evidence re-verified against `origin/beta`"
affects: [firestarter_fw-release-pipeline, firestarter-issue-tracker]

actuals:
  tokens: 3000
  tasks: 3
  commits: 0

tech-stack:
  added: []
  patterns: ["workflow_dispatch repair of a zero-asset release rather than hand-upload"]

key-files:
  created:
    - .planning/quick/260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele/260918-ayh-SUMMARY.md
  modified: []

key-decisions:
  - "Dispatched beta-build.yml on ref beta with beta_version=3.0.0b33 exactly once, per plan — no rehearsal input, no rerun of the failed run."
  - "Closed #67/#68 only after independently confirming asset count >=3 on the release (precondition gate), so fix:released was never applied to an uninstallable release."
  - "Left #15 and #16 open after re-running the planner's own evidence checks against a freshly fetched origin/beta; both re-assertions matched the plan's stated findings with no drift, so both issues were left untouched exactly as planned."
  - "Skipped the plan's Task 3 SUMMARY commit step per orchestrator constraint — the orchestrator commits SUMMARY.md/PLAN.md/STATE.md itself."

requirements-completed:
  - QUICK-260918-ayh

coverage:
  - id: D1
    description: "Pre-release 3.0.0b33 repaired to carry the three AVR install images"
    requirement: "QUICK-260918-ayh"
    verification:
      - kind: other
        ref: "gh release view 3.0.0b33 --repo henols/firestarter_fw --json assets (4 assets: uno, uno328pb, leonardo, py32f071)"
        status: pass
    human_judgment: false
  - id: D2
    description: "origin/beta unmoved by the dispatch"
    requirement: "QUICK-260918-ayh"
    verification:
      - kind: other
        ref: "git -C firestarter_fw rev-parse origin/beta == 11024ee47bdc99dde9308c5179aae608871979bc"
        status: pass
    human_judgment: false
  - id: D3
    description: "#67 and #68 closed, fix:released, comments name 3.0.0b33 and 3.0.0b48, no internal-identifier leak"
    requirement: "QUICK-260918-ayh"
    verification:
      - kind: other
        ref: "gh issue view 67/68 --json state,labels,comments (scripted token/leak assertions in PLAN.md Task 2 verify)"
        status: pass
    human_judgment: false
  - id: D4
    description: "#2 and #5 closed with one comment each; #15 and #16 left OPEN with unchanged comment counts"
    requirement: "QUICK-260918-ayh"
    verification:
      - kind: other
        ref: "gh issue view 2/5/15/16 --json state,comments (scripted assertions in PLAN.md Task 3 verify)"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-09-18
status: complete
---

# Quick Task 260918-ayh: Repair firmware 3.0.0b33 zero-asset release and close shipped-fix issues

**Re-dispatched `beta-build.yml` on `beta` to attach the three missing AVR `.hex` assets to the already-published `3.0.0b33` pre-release, then closed four GitHub issues whose fixes are now verifiably shipped while leaving two mixed-evidence issues open.**

## Performance

- **Duration:** ~8 min (dispatch to final verify)
- **Started:** 2026-09-18T08:08:43Z (workflow dispatch)
- **Completed:** 2026-09-18T08:14:39Z
- **Tasks:** 3/3 completed
- **Files modified:** 0 product files (GitHub Actions dispatch + issue-tracker state only); 1 file created (this SUMMARY)

## Accomplishments

- **Repaired the zero-asset release.** Dispatched `beta-build.yml` (`--ref beta -f beta_version=3.0.0b33`), run [35322889419](https://github.com/henols/firestarter_fw/actions/runs/35322889419), conclusion `success`. Pre-release `3.0.0b33` now carries:
  - `firestarter_uno.hex` (64155 bytes)
  - `firestarter_uno328pb.hex` (64282 bytes)
  - `firestarter_leonardo.hex` (70050 bytes)
  - `firestarter_py32f071.hex` (75648 bytes, bonus — the ARM `continue-on-error` job also succeeded this run)

  `origin/beta` in `henols/firestarter_fw` is confirmed unchanged at `11024ee47bdc99dde9308c5179aae608871979bc` after the dispatch — no commit pushed, no tag moved, as the plan's safety analysis predicted (the version-bump diff was empty going in).

- **Closed #67 and #68** ([Protocol 0x05 page-size derivation](https://github.com/henols/firestarter/issues/67), [Protocol 0x05 unaligned-write silent erasure](https://github.com/henols/firestarter/issues/68)) with the plan's fixed comment bodies, posted verbatim:
  - #67: comment [issuecomment-5727194544](https://github.com/henols/firestarter/issues/67#issuecomment-5727194544), labelled `fix:released` (alongside existing `bug`, `cause:firmware`), closed.
  - #68: comment [issuecomment-5727195349](https://github.com/henols/firestarter/issues/68#issuecomment-5727195349), labelled `fix:released` (alongside existing `bug`, `cause:firmware`), closed.
  - Gated on the asset-count precondition (>= 3) passing first, so `fix:released` was never applied while the release was still uninstallable.

- **Closed #2 and #5** (repo-rename / documentation-move enhancements) with the plan's fixed comment bodies, posted verbatim:
  - #2: comment [issuecomment-5727201600](https://github.com/henols/firestarter/issues/2#issuecomment-5727201600), `enhancement` label kept, no `fix:released` added (not a bug fix), closed.
  - #5: comment [issuecomment-5727202176](https://github.com/henols/firestarter/issues/5#issuecomment-5727202176), `enhancement` label kept, closed.

- **Left #15 and #16 open, deliberately**, after re-running the planner's own evidence checks against a freshly-fetched `origin/beta` (no drift found — see below). No comment was posted on either; their comment counts are unchanged (2 and 0).

## Issues Left Open (with re-verified evidence)

**[#15 — protocol-specific EPROM programming algorithms](https://github.com/henols/firestarter/issues/15).** Re-checked at execution time against `origin/beta`:
- `git grep -nE 'eprom_(regular|quick|legacy)_write_execute' origin/beta -- src include` → no matches. The issue's required design (three separate write handlers) does not exist; there is still one `eprom_write_execute`.
- `src/proms/eprom_params.cpp` param table → exactly 3 rows (`0x07`, `0x08`, `0x0B`), all with `overprogram_factor` (the second field) at `0UL` — the final overprogram pulse the issue asks for is still inert.
- `0x0B`'s row still carries `max_pulses = 255` and the default-width fallback the issue asks to remove for a long-fixed-pulse/one-attempt design.

All three of the planner's cited unmet-criteria signals reproduced identically at execution time. Substantial real work has shipped (the const parameter table, per-byte pulse counting, retry-loop removal), but the specific acceptance criteria named above remain unmet. Closing on mixed evidence would be a wrong answer to a two-month-old community request — left open.

**[#16 — prepare HAL for PY32F071](https://github.com/henols/firestarter/issues/16).** Re-checked at execution time against `origin/beta`:
- `platform/py32f071/CMakeLists.txt` still sets `RURP_HAS_VPP_DAC=0` — the closed DAC-VPP loop the issue's acceptance criterion names is still out of scope.
- `.github/workflows/py32f071.yml`'s `path:` release-asset line still names only `build/py32f071/firestarter_py32f071.hex` — the workflow does emit `.elf` as a build artifact internally, but that line is not a `path:` upload entry, and no BIN/ELF is published as the issue asks CI to do.

Both signals reproduced identically. The HAL groundwork is substantial and real (platform headers, board headers, the CMake/arm-none-eabi build, the dedicated CI workflow) but the DAC-VPP and CI-artifact acceptance criteria are unmet, and no PY32F071 board has ever been flashed. Left open.

## Task Commits

No product-repository commits were made — every action in this quick task was a GitHub Actions dispatch or an issue-tracker state change (comment/label/close), and no file under `firestarter_fw/` or `firestarter_app/` was touched at any point.

**Plan metadata:** not committed by this executor — see Deviations below.

## Files Created/Modified

- `.planning/quick/260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele/260918-ayh-SUMMARY.md` — this file (created)

No other file was created or modified. `firestarter_fw` and `firestarter_app` working trees were not touched; the only interaction with either was read-only (`git fetch`, `git rev-parse`, `git show`, `git grep`) against `origin/beta`.

## Decisions Made

- Dispatched the repair exactly once, on `--ref beta`, with only `beta_version=3.0.0b33` — no `rehearsal` input passed, matching the plan's explicit prohibition.
- Verified the asset-count precondition (>= 3) via a fresh `gh release view` call before touching #67/#68, rather than trusting the earlier planning-time snapshot, since closing those issues makes a public claim that the fix is installable.
- Re-ran the #15/#16 evidence checks against a freshly-fetched `origin/beta` rather than trusting the planner's snapshot verbatim, per the plan's own instruction; both re-assertions matched with zero drift, so both issues were left open exactly as planned with no contradiction to report.

## Deviations from Plan

**1. [Constraint-directed] Skipped the Task 3 SUMMARY.md commit step.**
- **Found during:** Task 3 (writing/committing the SUMMARY)
- **Issue:** The plan's Task 3 action instructs committing this SUMMARY.md with plain `git` from `/workspaces`. The orchestrator's explicit constraint for this execution states: "Do NOT commit docs artifacts (SUMMARY.md, PLAN.md, STATE.md) — the orchestrator handles that commit. If the plan's own Task 3 instructs a SUMMARY commit, skip that commit step and note the deviation in the SUMMARY."
- **Fix:** Wrote the SUMMARY.md file only; no `git add`/`git commit` was run by this executor. The orchestrator is expected to commit this file (and any STATE.md/ROADMAP.md updates) separately.
- **Files modified:** none beyond the SUMMARY.md write itself.
- **Verification:** `git status --short` at `/workspaces` shows the SUMMARY.md as untracked/new, staged by no one, alongside the same pre-existing dirty/untracked paths noted before this task ran (`.devcontainer/devcontainer.json`, `.vscode/*`, `.planning/graphs/*`, `anything.txt`, `firestarter.wiki/`, `setup-claude-pr-policy.sh`, `tmp/`) — none of which this task touched.
- **Committed in:** not committed by this executor (deferred to orchestrator).

No other deviations. All three tasks executed exactly as the plan specified: one workflow dispatch, four issue closes with the fixed comment bodies verbatim, two issues left open with re-verified evidence.

## Issues Encountered

None. The dispatched run completed in ~4 minutes with conclusion `success` on its first and only attempt; no auto-fix, retry, or halt was needed anywhere in the plan.

## Operator Note (not filed to backlog, per plan instruction)

**`beta-build.yml` can publish a release object whose asset upload silently fails without failing the run.** The prior run (that produced the original zero-asset `3.0.0b33`) completed with the release object created and tagged correctly, but `softprops/action-gh-release@v2`'s upload step failed with "Error creating asset temp dir" — and that failure did not turn the job or the run red. A `firestarter fw --install --pre` user would have hit a silent, uninstallable pre-release with no signal in the Actions UI that anything was wrong, until this repair. Compounding this: the failed run **could not be re-run in place** to fix it — `gh run rerun` re-invokes `update_version.py`, which auto-increments the version when dispatched without an explicit `beta_version`, and the resulting tag push is then rejected non-fast-forward against the already-existing `3.0.0b33` tag. The only working repair was a fresh `workflow_dispatch` that explicitly re-supplied the *same* `beta_version`, relying on the version-bump diff being empty (so the auto-commit step became a no-op) rather than on any retry mechanism the workflow itself provides. This is a real gap in the release pipeline's failure signalling; recorded here for the operator's awareness rather than filed as a backlog item, per this task's scope.

## Next Phase Readiness

- `firestarter fw --install --pre` now resolves a `.hex` for every AVR board (`uno`, `uno328pb`, `leonardo`) from `3.0.0b33`. The pre-release channel is installable again.
- Four issues closed with factual, version-naming comments; the tracker's open-issue count for shipped work is now accurate.
- #15 and #16 remain open, correctly, with their unmet criteria stated in full above for whoever picks either up next — no re-derivation needed.
- The `beta-build.yml` silent-asset-upload-failure gap (Operator Note above) is not fixed by this task; it is out of scope for a quick task and is flagged for the operator to decide whether it warrants a durable fix (e.g. `fail_on_unmatched_files: true` or an explicit post-upload asset-count assertion step).

---
*Quick task: 260918-ayh*
*Completed: 2026-09-18*

## Self-Check: PASSED

- FOUND: `.planning/quick/260918-ayh-repair-firmware-3-0-0b33-zero-asset-rele/260918-ayh-SUMMARY.md`
- FOUND: release `3.0.0b33` assets (`gh release view` confirms 4 assets including all 3 AVR names)
- FOUND: run `35322889419` at conclusion `success` (`gh run view`)
- FOUND: issues #67, #68, #2, #5 CLOSED with the expected comment counts and labels (`gh issue view`)
- FOUND: issues #15, #16 still OPEN with unchanged comment counts of 2 and 0 (`gh issue view`)
- FOUND: `origin/beta` unchanged at `11024ee47bdc99dde9308c5179aae608871979bc` (`git rev-parse`)
- CONFIRMED: no unrelated pre-existing dirty/untracked path was modified (`git status --short` diff-checked before/after)
