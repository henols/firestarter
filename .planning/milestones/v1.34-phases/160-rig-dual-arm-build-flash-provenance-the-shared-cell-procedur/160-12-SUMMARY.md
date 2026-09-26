---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 12
subsystem: infra
tags: [bench, w27c512, sha-oracle, judge_wrv, provenance, rig-04]

requires:
  - phase: 160 (plan 11)
    provides: the assembled Uno + Rev 2.0 rig with v1.33 flashed and proven, W27C512 seated,
      pot confirmed at 12.0V, and RIG-02's provenance mechanism proven on a live cell
provides:
  - The first real, on-silicon exercise of RIG-04's write-read-verify oracle: a distinct,
    address-attributable image regenerated and verified against its recorded hash, written
    with no forbidden flag, three independent v1.33-arm reads judged by full-device SHA
    against the written image (never against the app's own exit code)
  - A clean sha_verdict_judged=match with verdict_disagreement=false — the judge and the app's
    own unjudged verdict agreed on this run, proving the independent-judge mechanism works on
    real hardware without yet needing to exercise the Pitfall-6 false-green path itself
  - The 65536B read-set wall-clock cost baseline (53.437s for N=3) for Phase 161's 262144B
    W29C020 planning
  - A found-and-worked-around plan-authoring defect in this plan's own Task 2 verify leg (a
    literal-string mismatch against the app's real printed output)
  - A found, documented, not-silently-fixed P-H1 rig finding (~/.firestarter existing,
    traced circumstantially to plan 11) with the frozen FIRESTARTER_CONFIG_DIR independently
    confirmed unaffected
affects: [161, 162, 163, "160-13 (RIG-05 fresh-context record reconstruction)", 165, 166]

tech-stack:
  added: []
  patterns:
    - "A plan's own embedded <automated> verify leg can itself carry a hardcoded-literal
       defect (here: a string-match assumption never checked against the tool's real output)
       — the same measurement-trap class as an arm-agnostic numeric literal, just shaped as
       text. The fix is to run the CORRECTED assertion against the real evidence, never to
       adjust a measurement to force the original literal green."
    - "A P-11-style two-assertion teardown (env-var-fallback absence, then frozen-dir SHA
       equality) can fail its FIRST assertion for a reason entirely outside the current
       plan's own invocations — evidenced by an unchanged mtime across the whole session —
       while its SECOND assertion (the one that actually matters for D-07) still holds. Both
       facts are recorded, neither is allowed to stand in for the other."

key-files:
  created:
    - .planning/v1.34/bench/cells/BRINGUP-wrv/WRITE.md
    - .planning/v1.34/bench/cells/BRINGUP-wrv/WRV-VERDICT.json
    - .planning/v1.34/bench/cells/BRINGUP-wrv/check_arms_teardown.json
    - .planning/v1.34/bench/cells/BRINGUP-wrv/logs/09_gen_addr_image.{stdout,stderr}.log
    - .planning/v1.34/bench/cells/BRINGUP-wrv/logs/10_write_w27c512.{stdout,stderr}.log
    - .planning/v1.34/bench/cells/BRINGUP-wrv/logs/11_consistency_check.{stdout,stderr}.log
    - .planning/v1.34/bench/cells/BRINGUP-wrv/logs/12_judge_wrv.{stdout,stderr}.log
    - .planning/v1.34/bench/cells/BRINGUP-wrv/logs/13_check_arms_teardown.{stdout,stderr}.log
  modified:
    - .planning/v1.34/bench/cells/BRINGUP-wrv/SHA256SUMS.txt
    - .planning/v1.34/bench/cells/BRINGUP-wrv/provenance.json (commands[] extended with the
      teardown check_arms.py invocation and its ~/.firestarter finding note)
    - .planning/v1.34/bench/EVIDENCE.jsonl (4th bring-up row appended, 0 sweep rows)
    - .planning/v1.34/bench/EVIDENCE.md (re-rendered)
    - .planning/REQUIREMENTS.md (RIG-04 marked Complete)
    - .planning/ROADMAP.md (160-12-PLAN.md checkbox ticked)
    - .planning/STATE.md (position, decisions, session, metrics)
  not_committed_per_policy:
    - .planning/v1.34/bench/cells/BRINGUP-wrv/written.bin (clean match; SHA recorded, gitignored)
    - .planning/v1.34/bench/cells/BRINGUP-wrv/reads/run_0{1,2,3}.bin (clean match; SHAs recorded, gitignored)

key-decisions:
  - "The judged verdict was taken exclusively from judge_wrv.py's own sha_verdict_judged
     output — the app's dev consistency-check exit code (0/PASS) was recorded as
     app_verdict_unjudged and compared, never substituted for the judged verdict, at any step"
  - "This plan's own Task 2 second verify leg's hardcoded grep for the literal string
     'consistency-check' was found not to match the app's real printed verdict-block string
     ('Consistency check: PASS') on either arm; the corrected, case-insensitive assertion
     was run against the real captured log instead of adjusting any measurement"
  - "~/.firestarter's existence at teardown was recorded as a P-H1 rig finding with its
     circumstantial root-cause chain (never proven directly, stated as such), rather than
     silently deleted or silently ignored; removal was attempted and denied by this session's
     sandbox, so the contamination is carried forward as an open item"
  - "The frozen FIRESTARTER_CONFIG_DIR's content SHA was independently re-verified unchanged
     (check_arms.py --expect-config-sha, exit 0) as a SEPARATE fact from the ~/.firestarter
     finding — D-07 holds regardless of that finding, and the two facts are never conflated"

requirements-completed: [RIG-04]

coverage:
  - id: D1
    description: "This position's distinct, address-attributable image (mask 0x24,
      stamp_width 16) was regenerated from IMAGE-PLAN.json and verified byte-for-byte and by
      SHA-256 against its recorded hash before being written"
    requirement: RIG-04
    verification:
      - kind: other
        ref: "python3 -c sha256 comparison against IMAGE-PLAN.json's BRINGUP-wrv row (exit
          implicit pass, output 'OK written image regenerated and matches its recorded hash')"
        status: pass
    human_judgment: false
  - id: D2
    description: "Written with no --force/-f, no -b/--no-blank-check, no --skip-erase; wall-
      clock (41.010s) measured around the whole command, app-reported (37.48s) recorded
      alongside as the second, unjudged datum; high-voltage guard did not fire"
    requirement: RIG-04
    verification:
      - kind: other
        ref: "logs/10_write_w27c512.stdout.log ('Write to W27C512 successful (37.48s).', exit
          0); WRITE.md's forbidden-flag check against rig-pins.json's forbidden_flags list"
        status: pass
    human_judgment: false
  - id: D3
    description: "Three independent reads via the v1.33 arm's own dev consistency-check
      --runs 3 --keep-files; judged by judge_wrv.py over the full 65536B against the written
      image, independent of the app's own reads-agree-with-each-other check"
    requirement: RIG-04
    verification:
      - kind: other
        ref: "WRV-VERDICT.json (sha_verdict_judged=match, read_count=3, distinct_read_shas=1,
          app_verdict_unjudged=0, verdict_disagreement=false); SHA256SUMS.txt verifies with
          sha256sum -c"
        status: pass
    human_judgment: false
  - id: D4
    description: "BRINGUP-wrv EVIDENCE.jsonl row appended (4th bring-up row, 0 sweep rows);
      EVIDENCE.md re-rendered; the whole record and full gate suite green"
    requirement: RIG-04
    verification:
      - kind: other
        ref: "render_evidence.py --check (exit 0); gate_record.py --jsonl (exit 0); bash
          tools/run_gates.sh (exit 0, 11/11 selftests + 5/5 live gates)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The ~/.firestarter P-H1 finding and its circumstantial root-cause chain,
      and that removal was attempted and denied by the session sandbox rather than silently
      resolved or silently ignored"
    verification: []
    human_judgment: true
    rationale: "Whether the recorded circumstantial evidence (birth timestamp matching a
      disclosed-but-unlogged prior-plan invocation window, and content matching a bare port
      setting) is an adequate root-cause statement, and whether leaving the stray directory
      in place until an operator or a differently-permissioned session clears it is an
      acceptable interim state, are matters of project judgment, not a mechanically
      checkable pass/fail."

duration: 24min
completed: 2026-08-27
status: complete
---

# Phase 160 Plan 12: BRINGUP-wrv Write-Read-Verify Oracle Summary

**RIG-04's write-read-verify oracle exercised on real silicon for the first time — a clean
full-device SHA match on W27C512, with a found-and-fixed plan verify-leg defect and a found,
disclosed (not silently resolved) rig-hygiene finding.**

## Performance

- **Duration:** 24 min
- **Started:** ~2026-08-27T08:12Z
- **Completed:** 2026-08-27T08:36Z
- **Tasks:** 3/3 complete
- **Files modified:** 17 (across 3 task commits) + 6 (metadata: REQUIREMENTS.md, ROADMAP.md,
  STATE.md)

## Accomplishments

- **RIG-04 discharged.** The write-read-verify oracle ran end to end on a real chip: this
  position's own address-attributable image (mask `0x24`, stamp_width 16) was regenerated
  from `IMAGE-PLAN.json` and verified against its recorded hash (`fff15da9...b35726`) *before*
  it touched the socket; written with no forbidden flag; three independent reads via the
  v1.33 arm's own `dev consistency-check --runs 3 --keep-files`; judged by `judge_wrv.py`
  over the full 65536B against the written image, never against the app's own exit code.
- **Clean match, both oracles agree.** `sha_verdict_judged=match`, `distinct_read_shas=1`,
  and the app's own unjudged verdict (`0`/PASS) agrees (`verdict_disagreement=false`). This
  run did not need to exercise the Pitfall-6 false-green path (a stable-but-wrong read
  passing the app's reads-agree-with-each-other check) to prove the judge itself works
  correctly on real hardware — it proved the *positive* case cleanly.
- **The 262144B read-set cost baseline is now a measured number, not an estimate.** The
  three-read set (65536B × 3) took 53.437s wall-clock; Phase 161 can plan the W29C020 sweep
  around this rather than guessing.
- **A plan-authoring defect found in this plan's own verify script**, not just in a prior
  plan's: Task 2's second `<automated>` leg greps logs for the literal, hyphenated string
  `"consistency-check"`, but the app's real printed verdict-block line is `"Consistency
  check: PASS"` (capitalized, spaced — `eprom_operations.py:1092`). The literal grep matches
  zero occurrences against genuine output on either arm. Fixed by running the corrected,
  case-insensitive assertion against the real log rather than adjusting any measurement.
- **A P-H1 rig finding surfaced at teardown, disclosed rather than hidden.** `~/.firestarter`
  was found to exist — exactly the failure PROCEDURE.md's own P-11 teardown text predicts
  ("the seam this rule exists to prove was not actually used by at least one invocation").
  Root-cause is circumstantial (birth timestamp and bare-port-only content match plan 11's
  own disclosed, unlogged, shell-timeout-killed first `vpp` invocation) and is stated as
  circumstantial, not proven. This plan's own two chip-facing invocations both set
  `FIRESTARTER_CONFIG_DIR` inline and never touched it (mtime unchanged across the whole
  session). Removal was attempted and denied by this session's own sandbox policy (a
  home-directory deletion outside the repo); the finding is recorded in full in
  `provenance.json`'s `commands[]` and the EVIDENCE row's `anomalies`, and carried forward
  as an open item rather than silently cleaned or silently ignored.
- **The frozen `FIRESTARTER_CONFIG_DIR` itself is independently confirmed unaffected.**
  `check_arms.py --expect-config-sha <recorded>` exits 0 — D-07 holds regardless of the
  `~/.firestarter` finding above; the two facts are recorded separately and never conflated.
- **RIG-04 fully closes this requirement's SC scope for the 65536B size on real hardware.**
  The 262144B size is proven only by `judge_wrv.py`'s own `--selftest` fixture in this phase
  (both its `_VALID_SIZES` entries are exercised in code, not on silicon) — Phase 161
  exercises 262144B on the W29C020 for the first time on real hardware; this distinction is
  stated explicitly per the plan's own "Requirement completion" instruction.

## Task Commits

Each task was committed atomically:

1. **Task 1: Regenerate this position's image, verify it against its recorded hash, and write
   it with measured duration** - `e95fbc65` (feat)
2. **Task 2: Take three independent reads with the arm's own command and judge them by SHA
   over the full device size** - `f048c204` (feat)
3. **Task 3: Append the bring-up row, re-verify the config directory, and take the whole
   record green** - `61fa09a4` (docs)

**Plan metadata commit:** pending (STATE.md/ROADMAP.md/REQUIREMENTS.md/SUMMARY.md, immediately
following this file).

## Files Created/Modified

- `.planning/v1.34/bench/cells/BRINGUP-wrv/WRITE.md` — the write record: stated target, both
  duration figures, the literal command, the per-position-image insurance rationale, the
  shared-DB-row physical-part note
- `.planning/v1.34/bench/cells/BRINGUP-wrv/WRV-VERDICT.json` — the judged verdict (match,
  read_count=3, distinct_read_shas=1, verdict_disagreement=false)
- `.planning/v1.34/bench/cells/BRINGUP-wrv/SHA256SUMS.txt` — written image + 3 read hashes,
  verifies with `sha256sum -c`
- `.planning/v1.34/bench/cells/BRINGUP-wrv/check_arms_teardown.json` — the P-11 teardown
  `check_arms.py` re-run result (2 arms, all checks clean)
- `.planning/v1.34/bench/cells/BRINGUP-wrv/provenance.json` — `commands[]` extended with the
  teardown invocation and the full `~/.firestarter` finding writeup
- `.planning/v1.34/bench/cells/BRINGUP-wrv/logs/` — 9 new invocation logs (gen_addr_image,
  write, consistency-check, judge_wrv, check_arms teardown)
- `.planning/v1.34/bench/EVIDENCE.jsonl` / `EVIDENCE.md` — 4th bring-up row appended and
  re-rendered
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` — hand-edited
  (never regenerated via the GSD state/roadmap verbs, per this project's standing corruption
  history)

## Decisions Made

- The judged verdict came exclusively from `judge_wrv.py`'s own output; the app's exit code
  was recorded as `app_verdict_unjudged` and compared, never substituted.
- This plan's own Task 2 verify-leg defect (hardcoded literal `"consistency-check"` vs. the
  app's real `"Consistency check: PASS"`) was corrected by running the case-insensitive
  assertion against the real evidence — never by adjusting a measurement to force the
  original literal green.
- The `~/.firestarter` finding was recorded in full, with its circumstantial (not proven)
  root cause, rather than silently deleted (deletion was attempted and denied) or silently
  ignored.
- The frozen `FIRESTARTER_CONFIG_DIR`'s unchanged SHA was recorded as a fact independent of
  the `~/.firestarter` finding — the two are never conflated.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] This plan's own Task 2 second `<automated>` verify leg matched a literal
string the app never prints**
- **Found during:** Task 2, running the plan's own embedded verify script
- **Issue:** `grep -c "consistency-check" $D/logs/*` (hyphenated, lowercase) against the
  captured `dev consistency-check` stdout log. The app's real printed verdict-block line is
  `Consistency check: PASS` (`eprom_operations.py:1092`) — capitalized, space not hyphen.
  The literal grep matched zero occurrences on this real invocation, which would have failed
  every future cell that runs this same class of leg, regardless of whether the read set
  actually ran correctly — a plan-authoring defect of the exact class the measurement-traps
  note flags for plans 08/09/10's hardcoded span literals, here manifesting as a string match
  rather than a numeric one.
- **Fix:** Ran the corrected assertion — a case-insensitive match against the real
  `"Consistency check"` substring — against the same captured log. It passed, correctly
  proving the read-set invocation occurred and (since the verdict was `match`, not
  `disagreement`) that no retry was needed or performed.
- **Files modified:** none (the plan's own embedded verify script text is not a project file
  to edit; the corrected assertion was run ad hoc and is recorded here and in the EVIDENCE
  row's `anomalies` field, per this plan's own "never adjust a measurement to make a gate
  green" instruction — only the check's own pattern was corrected, not any measurement).
- **Verification:** the corrected assertion's output (`OK read set invoked (N=1 matches on
  the real verdict-block string), no retry needed`) is recorded above and in the EVIDENCE row.

**2. [Rule 3 - Blocking issue, disclosed rather than silently resolved] `~/.firestarter` found
to exist at P-11 teardown**
- **Found during:** Task 3, the first of PROCEDURE.md P-11's two teardown assertions
- **Issue:** `~/.firestarter` (a directory, birth/mtime `2026-08-27T07:59:25Z`, containing
  only `config.json = {"port": "/dev/ttyACM0"}`) exists — standing bench rule 9's own
  predicted P-H1 rig failure ("the seam this rule exists to prove was not actually used by at
  least one invocation"). Root-cause is circumstantial: the timestamp and bare-port-only
  content match exactly what `POT.md`'s own disclosed plan-11 deviation describes (an
  unlogged first `vpp` invocation killed by the surrounding shell's 120s command timeout,
  window ~07:57:25Z–07:59:25Z) — never proven directly, since that invocation left no
  numbered log artifact.
- **Resolution:** This plan's own two chip-facing invocations (Task 1 write, Task 2 `dev
  consistency-check`) both set `FIRESTARTER_CONFIG_DIR` inline and did not touch
  `~/.firestarter` — its mtime is unchanged from `07:59:25Z` across this entire plan's
  session, confirmed by re-checking after both invocations. The FROZEN
  `FIRESTARTER_CONFIG_DIR` (a separate, unrelated directory) was independently re-verified
  unchanged via `check_arms.py --expect-config-sha` (exit 0) — D-07 holds regardless.
  Removal (`rm`/`rmdir`) was attempted twice and denied both times by this session's own
  sandbox policy (a home-directory deletion outside the repo is treated as too risky to
  auto-approve). Per this project's record-honesty standard, the finding is recorded in full
  — in `provenance.json`'s `commands[]` and the EVIDENCE row's `anomalies` — rather than
  silently cleaned or silently left unmentioned, and is carried forward as an open item for
  a session with the needed permission, or for the operator to clear by hand.
- **Files modified:** `.planning/v1.34/bench/cells/BRINGUP-wrv/provenance.json` (appended
  `commands[]` entry with the full writeup), `.planning/v1.34/bench/EVIDENCE.jsonl` (the
  finding is cited in the row's `anomalies` field).
- **Verification:** `check_arms.py --expect-config-sha` exits 0 (frozen dir unaffected);
  `test -e ~/.firestarter` still reports it present (open item, not resolved).

---

**Total deviations:** 2 auto-handled (1 Rule 1 verify-leg fix, 1 Rule 3 finding disclosed
without a code change or a silent resolution).
**Impact on plan:** Neither deviation affected the oracle's own correctness — the write, the
three reads, and the judged verdict are all clean and independently cross-checked. Both are
scoped to this plan's own artifacts (a plan-authoring verify-leg text and a rig-hygiene
finding), never to firmware or host-app source (D-16 boundary respected throughout).

## Issues Encountered

None beyond the two deviations above. The write, the three reads, the judge, the EVIDENCE
append, the render, the record gate and the full `run_gates.sh` suite all passed on their
first real attempt.

## User Setup Required

None — no external service configuration required. The `~/.firestarter` open item does not
require any user *setup*; it requires either an operator or a session with home-directory
deletion permission to clear a stray, non-git-tracked directory. No product configuration is
affected.

## Next Phase Readiness

- **RIG-04 is Complete.** RIG-05 (fresh-context record reconstruction) is explicitly not
  closed by this plan and is 160-13's job.
- **The rig is left exactly as it was entering this plan**, safe for 160-13 or Phase 161 to
  drive without reconfiguration: Uno (ATmega328P) + Rev 2.0 shield, v1.33 arm flashed and
  proven, **W27C512 seated**, pot confirmed at 12.0V, port `/dev/ttyACM0`. No avrdude
  firmware operation ran against this board with the chip seated (the chip-out window closed
  before plan 11's task 3 seated the chip, and this plan never needed to reopen it).
- **The 65536B read-set cost baseline (53.437s for N=3) is available for Phase 161's
  W29C020 planning** (that part's read set will be ~4× the bytes; Phase 161 should measure
  it directly rather than extrapolate).
- **Open item carried forward, not a blocker:** `~/.firestarter` still exists on the
  container filesystem outside git tracking. It does not affect the frozen
  `FIRESTARTER_CONFIG_DIR` (independently confirmed unchanged) or any recorded SHA in this
  cell's evidence. A future session with the needed permission, or the operator, should clear
  it; until then it is a standing, disclosed finding, not a silent one.
- **160-13 (RIG-05) can proceed**: this plan's full record (`provenance.json`, `WRITE.md`,
  `WRV-VERDICT.json`, `SHA256SUMS.txt`, the EVIDENCE row) is self-contained per the
  record-substrate convention, ready for a fresh-context reconstruction test.

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-27*

## Self-Check: PASSED

All claimed files found on disk; all four commit hashes (`e95fbc65`, `f048c204`, `61fa09a4`,
`de39d274`) found in `git log --oneline --all`.
