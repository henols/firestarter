---
phase: 195-partial-writes-stop-destroying-the-page
plan: 05
subsystem: bench-evidence
tags: [w29c020, protocol-0x05, page-write, leonardo, bench-transcript, silicon-evidence]

requires:
  - phase: 195-partial-writes-stop-destroying-the-page
    provides: "the two-layer refusal (host pre-connect predicate + firmware per-chunk guard), the message catalog id, the full native/host test matrices, and the phase's own refusal record — all software evidence this plan puts on real silicon"
provides:
  - "the committed silicon transcript proving both WRITE-03 loss directions on a pre-fix W29C020 build, the post-fix refusal with a byte-identical read-back, and the aligned no-regression write"
  - "the first-ever silicon observation of the interior chunk-boundary loss direction (D-06), on a corrected payload size"
  - "WRITE-01, WRITE-02 and WRITE-03 flipped to Complete in REQUIREMENTS.md, citing this transcript"
affects: []

actuals:
  tokens: 6736
  tasks: 4
  commits: 1

tech-stack:
  added: []
  patterns:
    - "Scoped source revert to a named pre-phase commit, built, flashed, measured, then restored and re-verified clean, as the only way to bench-prove a defect a shipped fix has made unreproducible"
    - "Chunk-boundary interior loss requires a payload strictly larger than the transport chunk size (L > C); a payload equal to the chunk size degenerates to the already-characterized leading/trailing case"

key-files:
  created:
    - .planning/v1.39/195-w29c020-partial-write-bench-transcript.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The scoped revert touched four host files together (page_size_gate.py, exceptions.py, cli_handlers.py, eprom_operations.py), not page_size_gate.py alone, because eprom_operations.py and cli_handlers.py call require_page_alignment, which the pre-195 blob of page_size_gate.py does not define -- reverting one without the others would raise AttributeError rather than reproduce pre-195 behaviour. Confirmed by a clean-import check immediately after the revert."
  - "The plan's literal interior-direction payload (1024 bytes at 0x40 against a 2048-byte baseline) was tried first and found to degenerate to the leading/trailing case already characterized in 4d/4e, because the Leonardo's 1024-byte transport buffer accepts a 1024-byte payload in a single chunk (confirmed by counting 'Request data' cycles in verbose output: exactly one). The probe was corrected to 2048 bytes -- strictly larger than the chunk size -- which produced three chunk-request cycles and a genuine, previously-unobserved interior loss on the page straddling the chunk boundary. Recorded as a Rule 1 deviation from the plan's literal step, not as 'not attempted.'"
  - "Both sub-repo working trees were verified byte-for-byte restored against a captured pre-revert baseline (rather than against a literal empty 'git status --porcelain') because firestarter_app carries three pre-existing, unrelated untracked datasheet PDFs that this project's standing instruction requires leaving untouched. The restoration proof is 'identical to the pre-task-2 baseline,' which is strictly stronger than 'empty' would have been able to assert given that pre-existing noise."
  - "All three post-fix refusals were attributed to the host layer, not the firmware guard, because none of the three CLI invocations printed a Connecting... line before the error -- the serial port never opened. The firmware guard's own evidence remains the native suite; this transcript does not claim to have exercised it."

requirements-completed: [WRITE-01, WRITE-02, WRITE-03]

coverage:
  - id: D1
    description: "WRITE-01's refusal branch proved on real silicon: the fixed firmware+host refuse both the trailing- and leading-loss commands with a named error, exit non-zero, and a full read-back byte-identical to the baseline, proving the device is unchanged"
    requirement: "WRITE-01"
    verification:
      - kind: manual_procedural
        ref: ".planning/v1.39/195-w29c020-partial-write-bench-transcript.md#4h"
        status: pass
    human_judgment: true
    rationale: "Silicon bench evidence driven over USB passthrough against physical hardware; not a test a CI runner executes. The transcript records every command and hash verbatim for a human to audit."
  - id: D2
    description: "WRITE-02's forbidden pattern (success line printed over erased bytes) reproduced on the pre-fix build, and its absence (no success line, non-zero exit) confirmed on the post-fix build for the identical commands"
    requirement: "WRITE-02"
    verification:
      - kind: manual_procedural
        ref: ".planning/v1.39/195-w29c020-partial-write-bench-transcript.md#4d-4e-4h"
        status: pass
    human_judgment: true
    rationale: "Silicon bench evidence; the same rationale as D1 applies."
  - id: D3
    description: "WRITE-03's both loss directions demonstrated on real silicon on W29C020 (already-correct page size, isolating this defect from PAGE-01/PAGE-02), plus a first-ever silicon observation of the derived interior chunk-boundary direction (D-06)"
    requirement: "WRITE-03"
    verification:
      - kind: manual_procedural
        ref: ".planning/v1.39/195-w29c020-partial-write-bench-transcript.md#4d-4g"
        status: pass
    human_judgment: true
    rationale: "Silicon bench evidence; the same rationale as D1 applies."

duration: 55min
completed: 2026-09-16
status: complete
---

# Phase 195 Plan 05: W29C020 silicon bench evidence — both loss directions, the post-fix refusal, and the interior finding Summary

**On the operator's Leonardo/W29C020 rig, a pre-fix firmware+host build reproduces the leading, trailing, and (on a corrected payload size) interior loss directions with the host still reporting success; the post-fix build refuses all three, leaves the device byte-identical, and the aligned no-regression write still succeeds — WRITE-01, WRITE-02 and WRITE-03 flip to Complete on this evidence.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-09-16T12:07:00Z (approx, from board attach)
- **Completed:** 2026-09-16T13:02:00Z (approx)
- **Tasks:** 4 (Task 1 answered by the operator before this session; Tasks 2-4 executed here)
- **Files modified:** 2 (1 created)

## Accomplishments

- Task 1's four operator answers recorded as stated: `W29C020` seated, `Rev 2.0` (operator
  statement), port `/dev/ttyACM0`, destructive writes permitted. Controller identity re-confirmed via
  USB sysfs (`idVendor 2341`, `idProduct 8036`, `Arduino LLC`, `Arduino Leonardo`) before any
  operation, matching the operator's port exactly.
- A scoped revert of exactly the paths this phase changed (firmware `src/proms/flash_5v_page.cpp` to
  `c2b8baa`; host `page_size_gate.py`, `exceptions.py`, `cli_handlers.py`, `eprom_operations.py` to
  `3140172`) reproduced both WRITE-03 loss directions on real silicon: trailing loss (`0x040-0x07F`
  erased on a 64-byte no-address write) and leading loss (`0x000-0x03F` erased on a 64-byte write at
  `0x40`), with the host printing `Write to W29C020 successful` over the erased bytes both times —
  the WRITE-02 defect this phase exists to close.
- The derived interior chunk-boundary direction (D-06) was attempted per the plan's literal payload
  size first (negative — degenerated to the single-chunk case), then re-attempted with a corrected,
  strictly-larger payload, producing the **first silicon observation** of a page fully inside the
  requested range (`0x400-0x43F`) being erased when the next transport chunk re-opened it — while the
  host still reported success.
- Both trees were restored and verified identical to their pre-revert baseline (fw fully clean; app
  showing only its three pre-existing, unrelated untracked datasheet PDFs) before the post-fix build.
- The fixed firmware (`bootloader-guard: leonardo 23798/28672 B`, +64 B over the pre-fix
  `23734/28672 B`) refuses the identical trailing, leading, and interior commands with a named error,
  a non-zero exit, no success line, and a read-back hash identical to the post-fix baseline in every
  case — proving the device stays unchanged rather than merely asserting it.
- The aligned 2048-byte / 16-page no-regression write still succeeds and reads back byte-identical,
  confirming the fix did not cost the case that works today.
- `.planning/v1.39/195-w29c020-partial-write-bench-transcript.md` committed with all of the above,
  and `.planning/REQUIREMENTS.md` flips `WRITE-01`, `WRITE-02` and `WRITE-03` to Complete, citing it.

## Task Commits

Tasks 2 and 3 drove hardware and captured output for Task 4; they modified no tracked file (the
scoped revert was reverted back out before any commit, per the plan's own prohibition on leaving
either tree modified) and therefore produced no commit of their own.

1. **Task 1: Operator checkpoint** — answered before this session began; recorded in transcript §1, no commit (no file edited).
2. **Task 2: Reproduce both loss directions on a pre-fix build, then restore the tree** — hardware-only, no commit.
3. **Task 3: Flash the fix and prove the same two commands refuse and change nothing** — hardware-only, no commit.
4. **Task 4: Commit the transcript and move the requirements only as far as the evidence reaches** — meta: `320cdf0f` (docs)

**Plan metadata:** this SUMMARY commit, meta repo.

## Files Created/Modified

- `.planning/v1.39/195-w29c020-partial-write-bench-transcript.md` — the five-section silicon transcript, firmware section recorded twice (pre-fix and post-fix builds)
- `.planning/REQUIREMENTS.md` — WRITE-01, WRITE-02, WRITE-03 checkboxes and traceability rows flipped to Complete, each citing the transcript section that supports it

## Decisions Made

- **Four host files reverted together, not one.** `page_size_gate.py` alone would have left
  `eprom_operations.py` and `cli_handlers.py` calling a function the pre-195 blob doesn't define,
  raising `AttributeError` instead of reproducing pre-195 behaviour. Confirmed by an explicit
  clean-import check immediately after the revert.
- **Interior-direction payload size corrected from the plan's literal 1024 bytes to 2048 bytes.**
  The Leonardo's 1024-byte transport buffer accepts a 1024-byte payload as a single chunk (verified:
  exactly one `Request data` cycle in verbose output), so the plan's literal instruction cannot
  exercise the multi-chunk mechanism it names. A 2048-byte payload (confirmed multi-chunk via three
  `Request data` cycles) produced the actual interior loss.
- **Tree-restoration proof compared against a captured pre-revert baseline, not a literal empty
  porcelain.** `firestarter_app` carries three pre-existing, unrelated untracked datasheet PDFs this
  project's standing instruction requires leaving untouched; asserting "identical to the captured
  baseline" is the correct and stronger claim given that known noise.
- **Every refusal attributed to the host layer.** No `Connecting...` line preceded any of the three
  post-fix error messages, meaning the serial port never opened; the firmware guard's own evidence
  stays with the native suite, and this transcript does not claim otherwise.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The plan's literal interior-direction payload size (1024 bytes) cannot exercise its own named mechanism on this rig**
- **Found during:** Task 2, STEP 10 (the interior direction probe)
- **Issue:** The plan instructs writing a 1024-byte file at `0x40` against a 2048-byte baseline to test the interior chunk-boundary direction. The Leonardo's transport chunk size is also 1024 bytes (`Buffer size: 1024` per the host's own debug log), so a 1024-byte payload transfers in exactly one chunk — verified by counting `Request data` cycles in `-v` output (exactly 1). With no second chunk, no page is ever re-opened by a later chunk, so the interior mechanism (`S % P != 0 and L > C`, per `195-RESEARCH.md` §1c) cannot fire; the resulting read-back showed only the already-characterized leading and trailing loss on the single chunk.
- **Fix:** Re-ran the probe with a 2048-byte payload (strictly larger than the 1024-byte chunk) at the same address `0x40` against the same 2048-byte baseline. Verbose output confirmed 3 `Request data` cycles (multi-chunk transfer). The read-back showed a genuine interior loss: page 8 (`0x400-0x47F`) had its first half (`0x400-0x43F`, legitimately written by chunk 1 and strictly inside the requested range) erased to `0xFF` when chunk 2's first byte re-opened the same page.
- **Files modified:** none (bench-drive correction only; no tracked file).
- **Verification:** transcript §4g records both the negative literal attempt and the positive corrected attempt, with the exact byte ranges and command outputs for both.
- **Committed in:** `320cdf0f` (transcript records the deviation; no separate code commit — no source was touched).

---

**Total deviations:** 1 auto-fixed (Rule 1 — the plan's own literal step size did not match its stated goal on this rig's actual chunk size; corrected in place and the correction fully documented in the transcript, not silently substituted).
**Impact on plan:** The correction produced a genuine positive result for D-06 (previously "derived, never observed") rather than a null result from a mis-sized probe. No scope creep — the corrected probe tests exactly the mechanism the plan names, at the size actually required to exercise it.

## Issues Encountered

- `firestarter_app`'s working tree carries three pre-existing, unrelated untracked datasheet PDFs
  (`datasheets/LST62832I.pdf`, `datasheets/MBM27128.pdf`, `datasheets/MBM27C4001.pdf`). These are not
  from this plan, are not touched by it, and their presence means a literal `test -z "$(git status
  --porcelain)"` check would always read "dirty" regardless of this plan's own tracked-file discipline.
  Verified instead against a captured pre-task-2 baseline snapshot, showing byte-for-byte identical
  porcelain output before and after the revert-and-restore cycle — the correct proof given the known,
  standing noise.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All three WRITE requirements (`WRITE-01`, `WRITE-02`, `WRITE-03`) are now `Complete` in
  `REQUIREMENTS.md`, each citing the specific transcript section that supports it. No WRITE
  requirement was left open — the run reached everything this plan set out to prove.
- The interior chunk-boundary direction (D-06), previously "derived from source and a datasheet
  quotation, never observed," now has a first silicon observation, recorded in transcript §4g/§4h.
  This is beyond what WRITE-03 requires (which names only the leading and trailing directions) and is
  not itself a v1 requirement, but it strengthens the phase record per D-06's own instruction to
  record the result either way.
- Both sub-repo working trees are clean (verified identical to their pre-plan baseline) and no branch
  was pushed. `.planning/STATE.md` and `.planning/ROADMAP.md` were not touched — the orchestrator owns
  those writes after the wave completes.
- Phase 195's five plans are now all executed. This transcript, together with
  `195-partial-write-refusal-record.md` (the software-side record it `pairs_with`), is the complete
  evidentiary basis for closing out the phase's WRITE requirements.

---
*Phase: 195-partial-writes-stop-destroying-the-page*
*Completed: 2026-09-16*

## Self-Check: PASSED

- `.planning/v1.39/195-w29c020-partial-write-bench-transcript.md` confirmed present on disk with `[ -f ]`.
- Commit `320cdf0f` confirmed present via `git log --oneline --all --grep="195-05"` in the meta repository.
- Task-level acceptance criteria re-run and passing: transcript has frontmatter, `pairs_with`, ≥2 `bootloader-guard` lines (2 found), ≥5 `## ` sections (5 found); required tokens `W29C020`, `0xFF`, `sha256`, `c2b8baa`, `3140172` all present; `REQUIREMENTS.md` checkboxes and traceability rows agree (all three `[x]` / `Complete`); `git status --porcelain` empty for both committed paths with a commit line present for the transcript.
- Plan-level `<verification>` re-run: operator statements recorded (§1); controller identity confirmed on `/dev/ttyACM0` before every operation and after each flash (§2); installed package resolves under `/workspaces/firestarter_app` (§2); scoped-revert porcelain listing recorded and both trees clean after restoration (§3a); two distinct `bootloader-guard` lines present, one per build (§3); both loss directions recorded with exact erased ranges and the host's outcome line (§4d, §4e); both post-fix repeats refuse, exit non-zero, print no success line, and read back byte-identical (§4h); the aligned 2048-byte write reads back byte-identical (§4i); the interior direction's result (both the negative literal attempt and the positive corrected attempt) is recorded (§4g); requirement checkboxes and traceability table agree; `git status --porcelain` is empty in all three repositories (verified directly, modulo the three pre-existing untracked datasheet PDFs in `firestarter_app`, which are unrelated to this plan and were left untouched per standing project instruction).
