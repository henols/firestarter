---
phase: 260919-cli-beta-build-ships-dev-tools-so-dev-reg-an
plan: 01
subsystem: ci
tags: [firmware, ci, dev-tools, platformio, github-actions, bench-record-correction]

requires:
  - phase: 199-what-the-rails-can-actually-deliver
    provides: "the 199-02 bench session's falsified root cause and the four measured voltage/ADC figures this task must not disturb"
provides:
  - "Two mirror-image CI assertions (beta-build.yml presence, build.yml absence) proving the dev-tools channel split going forward, each observed passing and failing on both build polarities against real build trees"
  - "260919-cli-EVIDENCE.md: 6 bootloader-guard figures for uno/uno328pb/leonardo x plain/dev-tools, the oracle's 3/3-and-0/3 discrimination proof, and independent confirmation that the published 3.0.0b31 AVR assets carry dev_tools.cpp code"
  - "A corrected causal claim in 199-BENCH-RECORD.md (Fault 1 and Fault 2) and 199-02-SUMMARY.md, with every measured figure, transcript and observed symptom preserved byte-identical"
  - "A channel-split subsection in firestarter_fw/CLAUDE.md naming which publisher ships dev tools and the exact local command that reproduces it"
affects: [199-05, any future review of the beta/stable publisher workflows]

actuals:
  tokens: 4700
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Presence/absence CI assertion pair keyed on a source-literal needle (strings output written to a file, then grep -Fq -- on the file — never piped, to avoid the SIGPIPE/141 false-RED hazard) rather than on a translation-unit name, which can survive in an ELF's string table even when the guarded code compiles to nothing"

key-files:
  created:
    - .planning/quick/260919-cli-beta-build-ships-dev-tools-so-dev-reg-an/260919-cli-EVIDENCE.md
  modified:
    - firestarter_fw/.github/workflows/beta-build.yml
    - firestarter_fw/.github/workflows/build.yml
    - firestarter_fw/CLAUDE.md
    - .planning/phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md
    - .planning/phases/199-what-the-rails-can-actually-deliver/199-02-SUMMARY.md

key-decisions:
  - "Corrected both repetitions of the falsified root cause inside 199-BENCH-RECORD.md (Fault 1's causal claim AND Fault 2's closing 'no release ships' clause), not just the one Fault 1 sentence the plan named verbatim — Fault 2 repeated the same false premise and leaving it uncorrected next to a corrected Fault 1 would have produced an internally contradictory record."
  - "199-02-SUMMARY.md was not rewritten; a single correction block was inserted after Fault 2's paragraph, covering both of that file's repetitions (Fault 1's transcript paragraph and Deviation 1's 'ships in no release artifact' claim) in one place rather than editing each line in situ."
  - "Did not commit this SUMMARY.md or the quick task's PLAN.md, per explicit orchestrator instruction (project_rules #7) — only the EVIDENCE.md and the Phase 199 corrections were staged into the meta commit."

requirements-completed:
  - QUICK-260919-cli

coverage:
  - id: D1
    description: "The dev-tools oracle (strings needle 'CTRL remapped') is proven to discriminate: 3/3 on dev-tools builds, 0/3 on plain builds, 3/3 on independently-decoded published 3.0.0b31 assets, with 6 verbatim bootloader-guard figures recorded and no ceiling breach"
    requirement: "QUICK-260919-cli"
    verification:
      - kind: manual
        ref: "260919-cli-EVIDENCE.md; local commands run and captured in this session's transcript"
        status: pass
    human_judgment: false
  - id: D2
    description: "beta-build.yml fails before the Release step if any AVR image loses the dev commands; build.yml fails if any AVR image gains them; both step bodies observed passing on the correct polarity and failing on the other against real build trees, not just asserted by reading the YAML"
    requirement: "QUICK-260919-cli"
    verification:
      - kind: manual
        ref: "extracted step bodies run via bash against .pio/build trees in both configurations; TASK2_PASS verify command"
        status: pass
    human_judgment: false
  - id: D3
    description: "firestarter_fw/CLAUDE.md documents the channel split and the local reproduction command; the Phase 199 bench record's causal claim is corrected while its four parsed figure lines stay byte-identical; both native pio test environments and the Python test tree were run against committed trees"
    requirement: "QUICK-260919-cli"
    verification:
      - kind: manual
        ref: "TASK3_PASS verify command; pio test -e native (217/217); pio test -e native_nodevtools (217/217); python3 -m pytest tests/ -q (17 failed / 284 passed, matching the documented pre-existing baseline)"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-09-19
status: complete
---

# Quick Task 260919-cli: Prove Beta Already Ships Dev Tools, Fix the Falsified Diagnosis — Summary

**Beta was never missing dev tools — the bench session's diagnosis was wrong, and this task made that provable instead of believed.**

## What actually happened (read this before the task list)

1. **The task's premise was falsified before any code was written**, and the planner and orchestrator
   had already confirmed it independently. `beta-build.yml`'s "Build PlatformIO Project" step has
   set `PLATFORMIO_BUILD_FLAGS: -D DEV_TOOLS=1` since firmware commit `e6888a9` (2026-09-14). The
   published `3.0.0b31` AVR release assets were downloaded fresh, decoded from Intel HEX, and
   confirmed on 2026-09-19 to all contain `dev_tools.cpp` code (`CTRL remapped`, the discriminating
   needle). There was nothing to "enable." The work became: prove the discrimination, guard it in
   CI so it cannot silently regress, and correct the record that concluded the opposite.

2. **A shipped beta carries the dev commands but not yet a working implementation.** Firmware commit
   `7eed3af` (`dt_set_registers` re-entrancy fix, already on this milestone branch) has not reached
   `beta`. Every published pre-release through `3.0.0b33` dispatches `CMD_DEV_REGISTER` (`8`) and
   then times out. Do not read this task as making shipped `dev reg` work — it does not, yet.

3. **Two host-side defects remain open and untouched, exactly as the plan scoped them out:**
   `.planning/milestones/v1.18-artifacts/bench/hold_rail.py` reports `RAIL HELD` without ever calling
   `expect_ack()`, so it cannot observe a firmware refusal; and `firestarter dev reg` exits `0` while
   printing a firmware error line. Both are backlog candidates.

4. **The unresolved reconciliation, left as a labelled inference, not a measurement.** The bench
   session's own board, reporting itself as `3.0.0b31`, refused command 8 with
   `ERROR: Unknown command: 8` — yet the actual published `3.0.0b31` assets implement that command.
   The most likely explanation is that the attached board was running a locally built image rather
   than the genuine published asset (the session's own "Rig state left by this session" paragraph
   documents exactly that hazard for the image it left behind), but no image was pulled off the
   board and compared byte-for-byte against the release asset, so this is recorded as inference in
   `199-BENCH-RECORD.md`, not fact.

## Tasks completed

**Task 1 (tracer) — Prove the oracle discriminates, measure all three AVR targets.**
Built `uno`, `uno328pb` and `leonardo` twice each (plain, then `-D DEV_TOOLS=1`), captured all six
`bootloader-guard:` lines, ran the `strings`-on-a-file-then-`grep -Fq` oracle against all six ELFs
(3/3 present under dev tools, 0/3 under plain), and independently re-decoded the published
`3.0.0b31` release assets from Intel HEX with a standalone Python decoder (3/3, matching the
planning-time figures of 22734/22778/24830 B exactly). No file under `firestarter_fw` was edited in
this task. Committed as part of Task 3's meta commit (`260919-cli-EVIDENCE.md` is evidence-only,
lives in the meta repo).

**Task 2 (auto) — Assert the channel split in both publishers.**
Added one presence-assertion step to `beta-build.yml` (after "Build PlatformIO Project," before
"Build PY32F071 firmware," i.e. strictly before the Release step) and one mirror-image
absence-assertion step to `build.yml` (after its own "Build PlatformIO Project" step, ungated by
branch). Both extract exactly the needle-search idiom Task 1 proved, count the three envs checked
so an empty loop cannot pass vacuously, and write a PASS line to `$GITHUB_STEP_SUMMARY`. Both step
bodies were extracted to standalone scripts and run against real build trees in **both**
configurations: beta-build's body passed on the dev-tools tree and failed on the all-plain tree;
build.yml's body failed on the dev-tools tree and passed on the all-plain tree — all four
combinations observed directly, not just the two "expected-green" ones. The dev-tools build tree
was restored as the final state before moving to Task 3 (matching Task 1's own convention; `.pio`
is gitignored so this has no bearing on what gets committed).

**Task 3 (auto) — State the rule, correct the record, commit.**
Added a "Which channel ships dev tools" subsection to `firestarter_fw/CLAUDE.md` under "What CI
runs," naming the split, the exact `PLATFORMIO_BUILD_FLAGS="-D DEV_TOOLS=1" pio run -e leonardo`
local reproduction command, and the measured `3.0.0b31` evidence. Corrected `199-BENCH-RECORD.md`'s
Fault 1 (the falsified "no shipped AVR firmware implements command 8" claim) and, going one step
past the plan's literal instruction, Fault 2's closing clause (which repeated the same false "no
release ships" premise about `dev_tools.cpp`) — both now state the corrected mechanism, name the
unresolved reconciliation as an explicit inference, and preserve every transcript line, observed
symptom, and the four `DELIVERABLE_*`/`ADC_PAIRED_*` figure lines byte-identical. Applied one
consolidated correction block to `199-02-SUMMARY.md` (not a rewrite) covering that file's two
repetitions of the same false claim. Committed in two commits, firmware first then meta, both
verified on branch `v1.40-program-parameter-fidelity` after each commit, using plain `git commit`
with explicit pathspecs — never a gsd-tools commit verb.

## Verification results

**Task 1 / Task 3 automated verify legs:** both `TASK1_PASS` and `TASK3_PASS` echoed.

**Task 2 automated verify:** `YAML_OK`, `STEPS_OK`, `TASK2_PASS` all echoed; both workflow files
parse; each carries exactly one new step containing the needle in the correct position; neither
pipes into `grep`; the firmware working tree showed exactly the two workflow files changed at that
point.

**bootloader-guard lines (verbatim, all six measured this session):**
```
bootloader-guard: uno 21680/32256 B (67.2% of the safe ceiling, 10576 B margin, 512 B bootloader reserved)
bootloader-guard: uno328pb 21724/32384 B (67.1% of the safe ceiling, 10660 B margin, 384 B bootloader reserved)
bootloader-guard: leonardo 23798/28672 B (83.0% of the safe ceiling, 4874 B margin, 4096 B bootloader reserved)
bootloader-guard: uno 22838/32256 B (70.8% of the safe ceiling, 9418 B margin, 512 B bootloader reserved)
bootloader-guard: uno328pb 22882/32384 B (70.7% of the safe ceiling, 9502 B margin, 384 B bootloader reserved)
bootloader-guard: leonardo 24936/28672 B (87.0% of the safe ceiling, 3736 B margin, 4096 B bootloader reserved)
```
No breach; leonardo (tightest) still carries 3736 B margin under dev tools.

**CI assertion body reachability (all four combinations observed, not just the two expected-green legs):**

| Build tree | beta-build.yml body | build.yml body |
|---|---|---|
| all dev-tools | exit 0, "PASS: uno, uno328pb and leonardo all implement the dev commands" | exit 1, "::error::uno image implements the dev commands..." |
| all plain | exit 1, "::error::uno image does not implement the dev commands..." | exit 0, "PASS: uno, uno328pb and leonardo all lack the dev commands" |

**`pytest tests/ -v` / `pio test` counts against the documented 19-failed/282-passed baseline:**
- `pio test -e native`: 217/217 passed.
- `pio test -e native_nodevtools`: 217/217 passed.
- `python3 -m pytest tests/ -q`: **17 failed, 284 passed** (run against the fully committed tree,
  after the firmware commit, per the plan's stated ordering). All 17 failures are in
  `test_flash_path_record_sync.py`, matching the documented pre-existing cause (it scans
  `/workspaces/.planning/v1.23-FLASH-PATH-DECISION.md`, which moved to `.planning/milestones/`) —
  not something this task touches or was asked to fix. **The count differs from the stated 19/282
  baseline by 2, in the improving direction**: the two `test_trace_segment_exhaustiveness_v131.py`
  failures the baseline names are not present in this run — all 11 of that module's tests passed.
  This was not something this task did on purpose; it is reported rather than investigated further,
  since the plan's boundary is explicit that pre-existing conditions in this test tree are not this
  task's to fix or explain.

## Deviations from Plan

**None that required Rule 1-4 auto-fixing.** One instruction was extended beyond its literal text,
recorded as a decision above: Fault 2's closing sentence in `199-BENCH-RECORD.md` repeated the same
falsified "ships in no release artifact" premise the plan named only in Fault 1, and was corrected
alongside it to avoid leaving an internally contradictory record.

## Commits

- **firestarter_fw** `f72b2195eea8791671ad921c386eac25869491bd` — `ci(199-02): prove and assert the dev-tools channel split (beta ships, stable refuses)` — `.github/workflows/beta-build.yml`, `.github/workflows/build.yml`, `CLAUDE.md`. Branch `v1.40-program-parameter-fidelity`, verified after commit.
- **meta** `44baa601850898b9643e2c690731806ec4af161a` — `docs(260919-cli): prove beta already ships dev tools, correct Phase 199's root cause` — advances the `firestarter_fw` gitlink, `.planning/phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md`, `.planning/phases/199-what-the-rails-can-actually-deliver/199-02-SUMMARY.md`, `.planning/quick/260919-cli-beta-build-ships-dev-tools-so-dev-reg-an/260919-cli-EVIDENCE.md`. Branch `v1.40-program-parameter-fidelity`, verified after commit.

Nothing was pushed, tagged, or dispatched in either repository. No branch was created or switched —
confirmed by listing both repositories' local branches before and after and finding no new
`gsd/v1.40-…` or other stray branch.

## Self-Check: PASSED

- `firestarter_fw/.github/workflows/beta-build.yml` — FOUND, contains the new assertion step.
- `firestarter_fw/.github/workflows/build.yml` — FOUND, contains the mirror assertion step.
- `firestarter_fw/CLAUDE.md` — FOUND, contains the new "Which channel ships dev tools" subsection.
- `.planning/phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md` — FOUND, corrected,
  four `DELIVERABLE_*`/`ADC_PAIRED_*` lines confirmed byte-identical via `grep -Fqx`.
- `.planning/phases/199-what-the-rails-can-actually-deliver/199-02-SUMMARY.md` — FOUND, correction
  block present.
- `.planning/quick/260919-cli-beta-build-ships-dev-tools-so-dev-reg-an/260919-cli-EVIDENCE.md` —
  FOUND, committed.
- Commit `f72b2195eea8791671ad921c386eac25869491bd` in `firestarter_fw` — FOUND in `git log --oneline --all`.
- Commit `44baa601850898b9643e2c690731806ec4af161a` in meta — FOUND in `git log --oneline --all`.
- Both repositories on branch `v1.40-program-parameter-fidelity`, both working trees clean except
  for the pre-existing, out-of-scope modifications named in the task's project rules.
