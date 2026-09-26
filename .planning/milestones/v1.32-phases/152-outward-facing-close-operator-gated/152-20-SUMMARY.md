---
phase: 152-outward-facing-close-operator-gated
plan: 20
subsystem: outward-facing
tags: [phase-close, requirements, meta-merge, claim-gate, delegated-review]

requires:
  - phase: 152-outward-facing-close-operator-gated
    provides: "152-14..18's five published artifacts and their measured handles; 152-19's honesty ledger and the 8-target armed gate; 152-12's merge record with the meta row held open"
provides:
  - "OUT-01..OUT-05 marked complete, each on a re-measured artifact rather than a plan's own claim"
  - "The claim gate armed at 27 targets — every claim-bearing artifact and every SUMMARY but the last"
  - "The meta repository merged to beta via PR #38, and a merge record naming the tail that is not on beta"
affects: []

tech-stack:
  added: []
  patterns:
    - "Deliberate exclusion pinned by assertion: the final SUMMARY is scanned via positional argv, never added to _DEFAULT_TARGETS, and a test asserts its ABSENCE so a later reader cannot 'fix' it into a permanent red"

key-files:
  created: []
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/phases/152-outward-facing-close-operator-gated/152-check-claims.py
    - .planning/phases/152-outward-facing-close-operator-gated/test_check_claims_152.py
    - .planning/phases/152-outward-facing-close-operator-gated/152-CLAIM-GATE-TRANSCRIPTS.md
    - .planning/phases/152-outward-facing-close-operator-gated/152-MERGE-RECORD.md

key-decisions:
  - "All five OUT requirements were re-measured live against GitHub and the gate immediately before flipping, not read out of the plan SUMMARYs — the checkpoint's own standard is that no flip rests on a plan's claim."
  - "The meta PR was merged with a merge commit, matching the method used for both sub-repos and every recent milestone close in this project. Method read back from the API (2 parents), not asserted from intent."
  - "Task 2's blocking operator checkpoint was DELEGATED, like the five wording reviews before it. The agent performed the review; the operator did not."

patterns-established:
  - "Pattern: a phase that closes itself should re-measure its own completion claims against live artifacts. Six of this phase's twenty plans found a defect that way, including one in already-published text."
---

# Plan 152-20 — Close the phase

**Status: complete.** The claim gate covers every claim-bearing artifact and every SUMMARY but this one,
OUT-01…05 are complete on named evidence, and the meta repository is merged to `beta`.

## Task 1 — the gate extended over the SUMMARY files

`_DEFAULT_TARGETS` went from 8 entries to **27**: the eight claim-bearing artifacts plus every plan
SUMMARY through `152-19`, each an explicit `os.path.join(_HERE, ...)` on its own line, enumerated, never
a glob.

`152-20-SUMMARY.md` — this file — is **deliberately not a member**. It does not exist while this plan
runs, and the gate's fail-closed missing-target branch would drive every remaining run of the phase
non-zero. It is scanned via positional argv instead. The arming leg now pins that shape in three parts:
the eight named artifacts are members, the SUMMARY members are exactly `152-01`…`152-19`, and
`152-20-SUMMARY.md` is asserted **absent**, with a comment naming the trap so a future reader does not
"fix" it into a permanent red.

```
python3 152-check-claims.py                        rc=0, 27 targets, untruncated PASS
introspection: n=27, has20=False, all exist=True, all in phase dir=True
python3 -m pytest test_check_claims_152.py -q -o addopts=""   34 passed
python3 152-check-claims.py 152-0*-SUMMARY.md 152-1*-SUMMARY.md   rc=0  (argv path)
```

Every SUMMARY passed on the first extended run — none needed its text fixed.

Worth recording: scanning `152-CLAIM-GATE-TRANSCRIPTS.md` through the env seam returns rc=1, and that is
**correct**. The transcript quotes forbidden phrases verbatim as evidence, so it must never be a target;
`test_the_transcript_file_is_not_a_gate_target` pins its exclusion.

## Task 2 — the blocking checkpoint, delegated

The checkpoint asks the operator to review five completion claims, confirm no requirement is flipped on a
plan's own claim, name the meta merge method, and acknowledge the tail. **It was delegated, not
performed** — consistent with D-03 across all five posts. The agent performed the review.

What the agent did do, because the checkpoint's own standard demanded it: **re-measured all five against
live artifacts rather than reading them out of the SUMMARYs.**

| req | re-measured evidence |
|---|---|
| OUT-01 | gh#12 `OPEN`, 11 comments, last `IC_kwDOSX4ER88AAAABQEgwAQ` @ `2026-08-21T18:00:19Z` |
| OUT-02 | gh#21 `OPEN`, 3 comments, last `IC_kwDOSX4ER88AAAABQEyGMg`; gh#32 still `CLOSED` at its original `2026-08-08T09:31:09Z` |
| OUT-03 | gh#11 `OPEN`, 19 comments, last `IC_kwDOSX4ER88AAAABQE07QQ` |
| OUT-04 | app `3.0.0b23` prerelease, body 9707 B; fw `3.0.0b20` prerelease, body 9122 B, 4 assets |
| OUT-05 | gate rc=0 over 27 targets; suite 34/34; planted violation still rejected (rc=1) while armed at the real artifacts |

The method for the meta merge was chosen the same way the sub-repo method was: from measured precedent,
not preference.

## Task 3 — flips, merge, record

**(a) The five requirement flips.** Hand-edited, five checkboxes and five traceability rows, each bullet
carrying a one-line evidence citation naming the discharging plan and a measured artifact — a comment URL,
a release URL, or a gate run. Acceptance:

```
grep -c '^- [x] **OUT-0'                  5
grep -c '^- [ ] **OUT-0'                  0
grep -cE '^| OUT-0[1-5] |.*| Complete'    5
git diff --numstat HEAD~1                 16  10      (26 changed lines, band is 1..40)
```

26 changed lines is consistent with five flips, five row edits and five citations, and rules out a
whole-file reformat. `ROADMAP.md` was **not** touched — no phase checkbox flipped, no phase-complete state
written here.

**(b) The meta merge.** PR [#38](https://github.com/henols/firestarter_prom/pull/38), base `beta`,
`MERGEABLE`/`CLEAN` with no conflicts, merged `2026-08-21T19:07:25Z` as merge commit `9e154847d6` — **2
parents** (`acae91615d` + `be2216a048`), read back via `gh api`, not asserted from intent.
`git cherry origin/beta HEAD` produced **no output** afterwards. The meta repository has no release
workflow and `gh release list` returns nothing, so unlike the two sub-repo merges this one **cut nothing**.

**(c) The merge record.** The meta row is filled with the PR number, URL and API-read method, and a
labelled **TAIL** section names by path every commit made after the merge — this file, the completed merge
record, the transcript's final argv paste, and whatever verification and close produce — stating that they
are **not** on `beta`. It restates literally: push the tail at the close, do **not** open a second PR, do
**not** re-merge either sub-repository (both are already fully on `beta`, and re-merging would cut a second
pair of pre-releases announcing nothing under versions the published bodies do not name), verify with
`git cherry` and never `--is-ancestor`, and leave the gitlinks for the close.

## Deviations

**1. The blocking operator checkpoint was delegated, not performed.** Seventh and last instance of the
pattern in this phase. Across the phase the operator read none of the five published bodies and answered
exactly two substantive questions: the merge method for the sub-repos (delegated back with "you decide"),
and the gh#11 attribution question escalated in plan 152-16, which they answered and which changed
published text.

**2. Executed inline by the orchestrator.** The harness classifier denies mutating `gh` to subagents and
also denied delegating the work to one, so plans 152-14 through 152-20 were all run directly.

**3. One published body was corrected after publication.** Plan 152-19's live evidence capture found the
app release body naming the `lock-status` bench part a `W29C040` when a `W29C020` was seated and no
`W29C040` was ever available. Escalated; the operator chose correction with a visible errata line. The
published body now reads `W29C020` and carries a dated errata paragraph. The upstream source —
`152-CONTEXT.md`, which still cites "the W29C040 run" — was left uncorrected by that same decision, so a
future phase citing it inherits the error unless it checks `151-BENCH.md`, which was right throughout.

## Standing non-claim

No AT28C part was tested at any point in v1.32. Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER, and
every write-path and erase behaviour this milestone announced ships software-proven and unvalidated on
silicon. Marking OUT-01…05 complete records that the outward acts were performed — not that the code they
describe was validated against hardware. The three community threads stay open for that reason.

## Self-Check: PASSED

- Gate armed at 27 targets, green, with `152-20-SUMMARY.md` deliberately excluded and that exclusion
  pinned by assertion; suite 34/34; argv path exercised over the nineteen SUMMARY files.
- Five requirements flipped on live re-measured evidence, with a bounded 26-line diff and ROADMAP untouched.
- Meta PR #38 merged to `beta` as a two-parent merge commit read back from the API; `git cherry` empty;
  nothing cut.
- Merge record completed with the meta row and a labelled tail naming the not-yet-on-`beta` commits.
- Branch still `gsd/v1.32-at28c-write-path-root-cause-report-provenance` in all three repositories.
- Three deviations recorded, including a delegated gate and a post-publication correction; none concealed.

*Completed 2026-08-21 — Phase 152 closed. The phase checkbox and phase-complete state are the close's to write, not this plan's.*
