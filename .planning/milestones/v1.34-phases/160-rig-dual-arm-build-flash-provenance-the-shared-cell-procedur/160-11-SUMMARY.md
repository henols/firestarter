---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 11
subsystem: infra
tags: [bench, provenance, avrdude, uno, w27c512, vpp, rig-02]

requires:
  - phase: 160 (plans 01-10)
    provides: both arms standing (D-06/D-08), the frozen shared config dir (D-07), the
      per-target read chain proven and D-03 cross-flash detectors observed on all three
      boards, and the uno arm-span fix (hex_span_expected_by_arm)
provides:
  - The first real invocation of capture_provenance.py against a live cell -- five Rule 1
    bugs found and fixed in-phase, each with new --selftest coverage
  - A two-phase capture mode (--pending-readback / --patch-readback) so RIG-02's
    "before any test step" ordering is proven by log timestamps, not only claimed by a
    constant
  - The v1.33 arm flashed and proven on the Uno via an independent read-back matching its
    OWN hex extent (judged_span_bytes=22952) -- the direct complement of plan 08's
    cross-flash MISMATCH against the other arm's hex
  - RIG-02 discharged: the full provenance mechanism and its before-any-test-step ordering
  - The W27C512 seated and the pot confirmed at 12.0V by one reading, with no monitor loop --
    the rig left assembled exactly as Phase 161's first cell needs it
affects: [161, 162, 163, "160-12 (write-read-verify on this exact cell)", "160-13 (RIG-02 reconstruction)"]

tech-stack:
  added: []
  patterns:
    - "A capture tool that must run before a test step but needs data the test step
       produces is split into --pending/--patch phases, so log timestamps -- not a
       hardcoded step-number constant -- are the falsifiable evidence of ordering"
    - "Neither tool's own --selftest fixtures ever ran the OTHER tool's real output through
       it; the first live pairing of two independently-fixtured tools is where a schema
       mismatch (a missing top-level _schema block) surfaces, not in either tool's isolated
       test suite"

key-files:
  created:
    - .planning/v1.34/bench/cells/BRINGUP-wrv/provenance.json
    - .planning/v1.34/bench/cells/BRINGUP-wrv/probe.json
    - .planning/v1.34/bench/cells/BRINGUP-wrv/READBACK-VERDICT.json
    - .planning/v1.34/bench/cells/BRINGUP-wrv/flash_readback.bin
    - .planning/v1.34/bench/cells/BRINGUP-wrv/expected_span.bin
    - .planning/v1.34/bench/cells/BRINGUP-wrv/judged_span.bin
    - .planning/v1.34/bench/cells/BRINGUP-wrv/SHA256SUMS.txt
    - .planning/v1.34/bench/cells/BRINGUP-wrv/POT.md
    - .planning/v1.34/bench/cells/BRINGUP-wrv/logs/ (9 invocation logs)
  modified:
    - .planning/v1.34/tools/capture_provenance.py (five Rule 1 fixes + --pending-readback/--patch-readback modes)
    - .planning/v1.34/tools/gate_record.py (Rule 1 fix: venv_python missing from the argv0 allow-list)
    - .planning/REQUIREMENTS.md (RIG-02 marked Complete)

key-decisions:
  - "The controller_string probe's missing 'I: FW:' line is recorded as a not-measured
     datum with its reason (the hw command never forwards -v into firmware's wire flags,
     measured live at BRINGUP-uno), never as a hard failure -- it is unconditional on every
     arm, so a hard failure here would have blocked every future cell permanently"
  - "read_readback_verdict()'s filename/keys were fixed to judge_readback.py's REAL on-disk
     shape (READBACK-VERDICT.json / sha_actual_judged / sha_whole_flash_unjudged), not the
     aspirational shape the docstring named before any real cell ran"
  - "write_record_atomic() now emits the _schema block gate_record.py --cell requires;
     gate_record.py's argv0 allow-list now includes each arm's venv_python -- both fixes
     needed together before gate_record.py --cell could pass on ANY record this tool
     produces"
  - "The vpp CLI has no single-shot exit mode (continuous print loop until Ctrl+C or
     --timeout); the single confirming reading is the first sample from one invocation,
     never a second launch -- documented as a tooling finding, not fixed (D-16: no
     host-app source changes in this phase)"

requirements-completed: [RIG-02]

coverage:
  - id: D1
    description: "capture_provenance.py's identity fields captured before the flash step (RIG-02 ordering), corroborated by logs/ timestamps"
    requirement: RIG-02
    verification:
      - kind: other
        ref: "gate_record.py --cell .planning/v1.34/bench/cells/BRINGUP-wrv/provenance.json (exit 0); logs/03_capture_provenance_pending.* precede logs/05_pio_upload_v133.* and logs/06_judge_readback_v133.* by wall-clock mtime"
        status: pass
    human_judgment: false
  - id: D2
    description: "gate_record.py observed RED against a copy of the real record with one required field (host_arm_sha) nulled, message naming the field, copy deleted"
    verification:
      - kind: other
        ref: "python3 .planning/v1.34/tools/gate_record.py --cell /tmp/provenance_negcheck.json -> exit 1, 'FAIL: required field host_arm_sha is null/blank/placeholder: None'"
        status: pass
    human_judgment: false
  - id: D3
    description: "v1.33 arm flashed on the Uno and proven by independent read-back against its OWN hex extent (judged_match=true, judged_span_bytes=22952), complementing plan 08's MISMATCH against the other arm's hex"
    requirement: RIG-02
    verification:
      - kind: other
        ref: "READBACK-VERDICT.json (flashed_arm=v133, expect_arm=v133, judged_match=true); flash_readback.bin is exactly 32768 B; SHA256SUMS.txt verifies with sha256sum -c"
        status: pass
    human_judgment: false
  - id: D4
    description: "Five Rule 1 bugs in capture_provenance.py and one in gate_record.py, found on this tool's first-ever real invocation, fixed with new --selftest coverage"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/capture_provenance.py --selftest (exit 0); python3 .planning/v1.34/tools/gate_record.py --selftest (exit 0)"
        status: pass
    human_judgment: false
  - id: D5
    description: "W27C512 seated and pot confirmed at 12.0V by exactly one Claude-taken reading, no monitor loop, operator's 'pot set' reply and absence of an operator instrument reading recorded verbatim"
    requirement: RIG-02
    verification: []
    human_judgment: true
    rationale: "Physical chip seating and pot adjustment cannot be verified by any automated check available to this agent -- the operator's own report and the single confirming reading are the only evidence, and their faithful, non-overstated transcription is a human-judgment matter, not a test."

duration: 39min
completed: 2026-08-27
status: complete
---

# Phase 160 Plan 11: BRINGUP-wrv Provenance Capture & Rail Confirmation Summary

**RIG-02's provenance mechanism run for the first time against a live cell, on-device v1.33
proof on the Uno via v1.33's own hex extent, and the rig left seated at 12.0V for plan 12.**

## Performance

- **Duration:** 39 min (07:27 operator gate presented -- 08:06 task 3 committed; this
  agent's own working span was ~40 min across two turns)
- **Started:** 2026-08-27T07:27:35Z (pre-swap node enumeration)
- **Completed:** 2026-08-27T08:06:32Z (task 3 commit)
- **Tasks:** 3/3 complete (task 1 satisfied by the orchestrator before this agent started)
- **Files modified:** 26 (task 2) + 3 (task 3) = 29 total across two commits

## Accomplishments

- **RIG-02 discharged.** `capture_provenance.py`'s identity fields (board signature,
  controller string, host-arm SHA/porcelain/file, config-dir SHA, interpreter, dep-freeze
  SHA) are captured via a new `--pending-readback` mode BEFORE the v1.33 firmware is
  flashed; the flash runs via the PlatformIO upload path; an independent
  `judge_readback.py` read-back proves it (`judged_match=true`, `judged_span_bytes=22952`,
  matching v1.33's own uno hex span); a new `--patch-readback` mode then completes the two
  `fw_readback_sha_*` fields on the EXISTING record without re-running any identity probe,
  so the `logs/` timestamps stay honest evidence that identity was captured before the test
  step (verified: `03_capture_provenance_pending.*` at 07:41:12-17, `05_pio_upload_v133.*`
  at 07:41:52, `06_judge_readback_v133.*` at 07:42:02-08, `07_capture_provenance_patch.*`
  at 07:42:19).
- **The complement of plan 08's cross-flash proof.** Plan 08 flashed v1.33 on the Uno and
  judged it against the *control* arm's hex -- MISMATCH. This plan flashes v1.33 and judges
  it against its *own* hex -- MATCH. The pair together is what shows the detector
  discriminates rather than merely rejecting.
- **Five Rule 1 bugs found and fixed** on `capture_provenance.py`'s first-ever real
  invocation (no prior plan ran it against a live cell; 08/09/10 proved
  `probe_board.py`/`judge_readback.py` in isolation only) -- see Deviations below. A sixth
  Rule 1 bug was found and fixed in `gate_record.py`.
- **The rig left exactly as Phase 161's first cell needs it:** Uno + Rev 2.0, v1.33
  flashed, W27C512 seated, pot confirmed at 12.0V by one reading. No re-flash, re-seat or
  re-mount is needed to start plan 12 or Phase 161.
- **The `vpp` CLI's continuous-streaming behaviour documented as a finding**, not fixed
  (D-16 boundary) -- the single confirming reading used is the first sample from the one
  invocation launched, never a second read.

## Task Commits

Each task was committed atomically:

1. **Task 1: Operator mounts the Rev 2.0 shield, declares revision, socket empty** -- no
   separate commit (satisfied by the orchestrator's pre-gate enumeration and the
   operator's reply before this agent was spawned; recorded verbatim below and folded into
   task 2's provenance capture)
2. **Task 2: Capture provenance before any test step, flash v1.33, prove on-device** -
   `5f392c00` (feat)
3. **Task 3: Seat the W27C512, set the pot, one confirming reading** - `949d4253` (feat)

_No plan-metadata commit yet at the time this summary is written; the SUMMARY/STATE/ROADMAP
docs commit follows immediately after this file is written, per the standard flow._

## Files Created/Modified

- `.planning/v1.34/bench/cells/BRINGUP-wrv/provenance.json` - the full RIG-02 provenance
  block for this position; gate-green
- `.planning/v1.34/bench/cells/BRINGUP-wrv/probe.json` - the signature probe result,
  enriched with the operator's task-1 declarations and the node-identity-trap evidence
- `.planning/v1.34/bench/cells/BRINGUP-wrv/READBACK-VERDICT.json` - v1.33-on-uno judged
  against its own hex: `judged_match=true`, `judged_span_bytes=22952`
- `.planning/v1.34/bench/cells/BRINGUP-wrv/flash_readback.bin` - the full 32768 B read-back
- `.planning/v1.34/bench/cells/BRINGUP-wrv/SHA256SUMS.txt` - verifies with `sha256sum -c`
- `.planning/v1.34/bench/cells/BRINGUP-wrv/POT.md` - the stated 12.0V target, the
  operator's "pot set" reply, the single confirming reading, and the EEPROM calibration
  cross-check
- `.planning/v1.34/bench/cells/BRINGUP-wrv/logs/` - 9 invocation logs with stdout+stderr
  captured separately, corroborating the before/after-flash ordering by mtime
- `.planning/v1.34/tools/capture_provenance.py` - five Rule 1 fixes (see Deviations) plus
  the new `--pending-readback`/`--patch-readback` two-phase capture modes, each with new
  `--selftest` coverage
- `.planning/v1.34/tools/gate_record.py` - one Rule 1 fix (venv_python missing from the
  argv0 allow-list), with new `--selftest` coverage

## Decisions Made

- **The two-phase `--pending-readback`/`--patch-readback` design** was chosen over simply
  re-running `capture_provenance.py` a second time after the flash, because a full re-run
  would re-invoke the identity probes with post-flash timestamps, destroying the very
  ordering evidence RIG-02 needs the `logs/` to corroborate. The patch mode touches only
  the two readback fields and runs no probe at all.
- **The `hw`-output "not measured" allowance is scoped to a clean exit only.** `_interpret_hw_probe` now treats a missing `I: FW:` line as not-measured *only* when the
  process exited 0; a genuine execution failure (bad port, no device) still hard-fails,
  so the fix cannot paper over a real contact/communication fault.
- **The single confirming VPP reading is the FIRST sample from ONE invocation**, not an
  average or a cleaner second read -- the `vpp` CLI's own continuous-print design produced
  ~175 duplicate-valued lines in that one invocation's log; only the first is used, and no
  second process was launched to get a tidier exit code.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `probe_controller_string()` hard-failed on every real `hw` invocation**
- **Found during:** Task 2, first real run of `capture_provenance.py`
- **Issue:** `_interpret_hw_probe()` treated an absent `I: FW:` line as an unconditional
  hard failure. `hw`'s CLI handler never forwards `-v`/`--verbose` into the wire command's
  flags (measured live at BRINGUP-uno, 160-08, and re-confirmed here), so firmware's FW-info
  line is NEVER emitted, on any arm, regardless of verbosity -- this would have hard-failed
  every future cell unconditionally, with no fix available inside this phase's D-16 boundary.
- **Fix:** on a clean (exit 0) `hw` invocation, an absent FW-info line is now recorded as a
  not-measured datum with its reason; a genuine nonzero exit is still a hard failure.
- **Files modified:** `.planning/v1.34/tools/capture_provenance.py`
- **Verification:** `--selftest` legs for both the not-measured allowance and the
  still-hard-failing nonzero-exit case; live run against the real board confirmed the
  not-measured path fires and the record still passes `gate_record.py --cell`.
- **Committed in:** `5f392c00`

**2. [Rule 1 - Bug] `read_readback_verdict()` read a filename/key pair `judge_readback.py` never produces**
- **Found during:** Task 2
- **Issue:** the docstring and function named `readback_verdict.json` / `judged_sha256` /
  `whole_flash_sha256` -- an aspirational shape written before `judge_readback.py` (authored
  in a later plan) existed. The real tool writes `READBACK-VERDICT.json` with
  `sha_actual_judged` / `sha_whole_flash_unjudged`. No prior plan ever exercised the two
  tools together against a live cell, so the mismatch was invisible until now.
- **Fix:** filename and keys corrected to the real, measured shape.
- **Files modified:** `.planning/v1.34/tools/capture_provenance.py`
- **Verification:** `--selftest` positive leg against the real shape, negative leg
  confirming the old filename/keys are no longer read; live run succeeded.
- **Committed in:** `5f392c00`

**3. [Rule 1 - Bug] `check_head()`/`get_python_version()` unpacked as 3-tuples**
- **Found during:** Task 2
- **Issue:** `capture_provenance.py`'s `main()` unpacked both calls as `ok, value, detail =
  ...`, but `check_arms.py`'s `check_head()` and `get_python_version()` both return 2-tuples
  `(ok, detail_or_value)`. Every real call raised `ValueError: not enough values to unpack`.
- **Fix:** unpacked as 2-tuples, matching the real return shape.
- **Files modified:** `.planning/v1.34/tools/capture_provenance.py`
- **Verification:** live run against the real arms succeeded past both probes.
- **Committed in:** `5f392c00`

**4. [Rule 1 - Bug] Two `_log()` calls recorded a bare `"git"` argv0**
- **Found during:** Task 2
- **Issue:** the git-HEAD and git-porcelain probe log entries recorded `["git", ...]`
  instead of `rig-pins.json`'s pinned absolute `git_binary` -- `gate_record.py`'s own argv0
  allow-list would have rejected a bare, PATH-resolved `git` as an unrecognized binary.
- **Fix:** both `_log()` calls now use `pins.get("git_binary", "git")`.
- **Files modified:** `.planning/v1.34/tools/capture_provenance.py`
- **Verification:** the real record's `commands[]` entries all carry absolute argv0s;
  `gate_record.py --cell` passes.
- **Committed in:** `5f392c00`

**5. [Rule 1 - Bug] `write_record_atomic()` never emitted the `_schema` block `gate_record.py --cell` requires**
- **Found during:** Task 2, first time the two tools were run together against a real
  record (neither tool's own `--selftest` fixtures ever exercised the other tool's real
  output)
- **Issue:** `gate_record.py --cell`'s docstring is explicit that its input must carry a
  top-level `_schema` key (`record_keys` + `outcome_values`); `capture_provenance.py` never
  wrote one, so `gate_record.py --cell` could not have passed against ANY record this tool
  ever produced.
- **Fix:** `write_record_atomic()` now injects `_schema: {record_keys: RECORD_KEYS,
  outcome_values: ["validated", "skipped-with-reason"]}` on every write.
- **Files modified:** `.planning/v1.34/tools/capture_provenance.py`
- **Verification:** `gate_record.py --cell` now passes on the real record; `--selftest`
  round-trip leg confirms every key still present after the change.
- **Committed in:** `5f392c00`

**6. [Rule 1 - Bug] `gate_record.py`'s argv0 allow-list was missing each arm's `venv_python`**
- **Found during:** Task 2, first real `gate_record.py --cell` run against a real record
- **Issue:** `_allowed_argv0_set()` added each arm's `venv_bin` but never `venv_python` -- a
  second, equally pinned, equally legitimate executable `capture_provenance.py` invokes
  directly for the git-delegation/`__file__`/`--version` probes. Every such command was
  rejected as an unrecognized binary.
- **Fix:** `venv_python` added to the allow-list alongside `venv_bin`.
- **Files modified:** `.planning/v1.34/tools/gate_record.py`
- **Verification:** new `--selftest` positive leg; live run's record passes.
- **Committed in:** `5f392c00`

**7. [Rule 3 - Blocking issue, tooling behaviour only, no product-code change] `vpp` CLI has no single-shot exit mode**
- **Found during:** Task 3
- **Issue:** `firestarter vpp` streams DATA frames continuously (`\r`-overwritten) until
  Ctrl+C or its hidden `--timeout` elapses; there is no flag that samples once and exits.
  The one invocation launched (without `--timeout`) was terminated by the surrounding
  shell's own 120s command timeout (SIGTERM, exit 143) rather than the tool's own exit path.
- **Resolution:** no second process was launched. The single confirming reading recorded
  in `POT.md` is the FIRST value that one invocation printed. `HardwareManager` already has
  a value-returning, bounded, single-shot sampler (`sample_vpp_mv()`/`sample_vpe_mv()`,
  used internally by `dev test`'s energize-and-measure step) but it is not exposed as its
  own CLI flag; exposing it would be a host-app source change, out of this phase's D-16
  boundary. Recorded as a finding for a future phase.
- **Files modified:** none (documented in `POT.md` only)
- **Committed in:** `949d4253`

---

**Total deviations:** 7 auto-fixed (6 Rule 1 bug fixes, 1 Rule 3 blocking-issue finding
with no code change).
**Impact on plan:** All six code fixes were necessary for `capture_provenance.py` and
`gate_record.py` to work at all against a real cell -- exactly the class of gap this plan's
own objective predicted ("A field that is capturable in a tool's self-test but not in a real
cell would surface here"). No scope creep: every fix is confined to this phase's own
meta-repo bench tooling (`.planning/v1.34/tools/`), never firmware or host-app source.

## Issues Encountered

None beyond the deviations above. The board-signature probe, arms verification (before and
after the cell), and every automated verify leg in the plan's own `<verify>` block passed on
the first attempt after the tool fixes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 12 can run the write-read-verify oracle immediately: the v1.33 arm is flashed and
  proven, the W27C512 is seated, and the pot is confirmed at 12.0V (shared with the
  W29C020's own target, so no re-adjustment is needed when that chip is swapped in).
- Phase 161's first cell inherits this exact assembled state (Uno + Rev 2.0, chip seated,
  rail set) with no reconfiguration cost.
- `capture_provenance.py` and `gate_record.py` are now proven against a real cell, with six
  latent bugs fixed and new `--selftest` coverage added for each -- the next 19 sweep
  positions run against tools that have actually been exercised once, not only fixtured.
- R1/R2/R16/R14R15 calibration values remain genuinely unavailable from both the operator
  (declared "can't read them") and the firmware (no read-back CLI path in this app
  version) -- this is recorded, not silently worked around, and stands for every future
  cell on this same rig until a future host-app change adds a read-back path.

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-27*

## Self-Check: PASSED

All claimed files found on disk; both task commit hashes (`5f392c00`, `949d4253`) found in
`git log --oneline --all`.
