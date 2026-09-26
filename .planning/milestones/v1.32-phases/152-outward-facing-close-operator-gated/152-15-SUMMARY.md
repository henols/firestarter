---
phase: 152-outward-facing-close-operator-gated
plan: 15
subsystem: outward-facing
tags: [gh21, gh32, public-post, out-02, delegated-review, plan-defect]

requires:
  - phase: 152-outward-facing-close-operator-gated
    provides: "152-06's frozen gh#21 draft; 152-13's armed claim gate and fail-closed 152-check-not-auto.py; 152-11's beta merges, without which criterion 2's conditional would be false; 152-14's content-based landed-identity oracle"
provides:
  - "The gh#21 comment, posted: issuecomment-5373724210"
  - "Published-branch confirmation that the report-provenance fix is live, which is what makes the fresh-run request answerable"
  - "A second confirmation that the plans' main.py lock-status locator is wrong and cli_handlers.py is right"
affects: [152-16, 152-17, 152-18, 152-19, 152-20]

tech-stack:
  added: []
  patterns:
    - "Verify an outward conditional against the PUBLISHED branch (origin/beta) immediately before posting, not against the local working tree"

key-files:
  created: []
  modified: []

key-decisions:
  - "Task 1's acceptance criterion naming firestarter/main.py as the lock-status locator is WRONG and is recorded as such, not force-passed: main.py yields 0 matches because it is a re-export stub, while cli_handlers.py yields 9 at the real registration site. Second independent confirmation of this plan-authoring defect; plan 152-12 found it first."
  - "The raw body diff returns rc=1 because GitHub appends one trailing newline. Recorded as a literal criterion failure with content identity established by rstrip comparison, consistent with plan 152-14. The criterion's instrument is wrong on this platform, not the post."
  - "D-03's per-artifact blocking operator wording review was DELEGATED to the agent, not performed by the operator."

patterns-established:
  - "Pattern: when two plans independently measure the same locator wrong, record it as a defect in the plan set rather than a per-plan deviation — 152-12 and 152-15 both hit main.py vs cli_handlers.py."
---

# Plan 152-15 — Post the gh#21 comment (gh#32 folded)

**Status: complete.** One public comment posted on the AT28C thread this milestone exists to answer.
**OUT-02** is discharged outwardly.

| | |
|---|---|
| URL | https://github.com/henols/firestarter_prom/issues/21#issuecomment-5373724210 |
| comment id | `IC_kwDOSX4ER88AAAABQEyGMg` |
| created | `2026-08-21T18:27:49Z` |
| author | `henols` |
| comment count | 2 → **3** (delta exactly one) |
| gh#21 state after | **OPEN** — not closed |
| gh#32 state after | **CLOSED**, `closedAt` `2026-08-08T09:31:09Z` — identical to baseline, untouched |
| draft blob SHA | `5dc0001ffc1e50cc250d9d8f54f5941c4316a0f6` (intent oracle only) |

## Pre-flight (Task 1)

```
python3 152-check-not-auto.py                          rc=0  ("explicitly False" — live read)
python3 152-check-claims.py   (7 armed defaults)       rc=0
gate targeted at 152-GH21-COMMENT.md (env seam)        rc=0
pytest test_check_claims_152.py -q -o addopts=""       34 passed
```

## The criterion-2 verification, re-run on the published branch

This is the check the whole comment turns on: the fresh-run request is only worth making *because* a
report can now say which firmware produced it. That became true when plan 152-11 merged, so it was
re-read on `origin/beta` rather than inherited:

```
firestarter_app  origin/beta:firestarter/cli_handlers.py:2658
                 fw_board_identity=identity.fw_board_identity
firestarter      origin/beta:src/proms/eeprom_28c.cpp   eeprom28c_erase_execute  -> 3 refs
```

The provenance field is **populated on the published branch**, no longer a hardcoded null, and the
standalone erase arm is present in the published firmware. The comment's central conditional is true at
the moment it was posted.

### A plan defect, recorded rather than force-passed

Task 1's acceptance criterion reads:

> `git -C /workspaces/firestarter_app show origin/beta:firestarter/main.py | grep -c 'lock.status'` ≥ 1

Measured: **0**. The criterion as written **fails**. It fails because it names the wrong file —
`firestarter/main.py` is a re-export stub, and the command is registered in `firestarter/cli_handlers.py`,
which yields **9** matches on the same published branch. So the criterion's *intent* — the protection-read
command is reachable in what was published — holds, measured at the real site.

This is the **second independent confirmation** of the same defect: plan 152-12 hit it first and
root-caused it to `cli_handlers.py:1788`. Two plans measuring the same locator wrong makes this a defect
in the plan set, not a per-plan deviation. Any later plan or phase inheriting this locator should use
`cli_handlers.py`.

## Landed-identity proof

The raw diff returns **rc=1** with one added blank line — GitHub's trailing-newline normalisation, the
same signature plan 152-14 recorded:

```
raw equal          : False
equal after rstrip : True
byte delta         : 1
```

So the published text is character-for-character the frozen draft. As in 152-14, the literal criterion
("the diff must be empty") is reported as unmet with a sound substitute, rather than the oracle being
quietly swapped for one that passes. The posted-mode gate over the read-back body, written under its real
basename, exits **0**.

## Non-tampering evidence

Both pre-existing comments re-read and compared against the Task 1 capture — unchanged:

```
1  IC_kwDOSX4ER88AAAABN3crjQ  2026-08-08T09:31:07Z  henols
2  IC_kwDOSX4ER88AAAABN3frjA  2026-08-08T09:46:28Z  henols   <- baseline last comment, unchanged
3  IC_kwDOSX4ER88AAAABQEyGMg  2026-08-21T18:27:49Z  henols   <- this post
```

gh#32 was **not** reopened, **not** commented on, and its `closedAt` is bit-identical to the pre-post
capture. `updatedAt` was not used as an oracle anywhere.

## What the posted comment actually claims, and what it declines to claim

Worth recording because this is the thread the milestone is named for. The comment works entirely from the
reporter's own submitted data — the `"fw_board_identity": null` field, host version `3.0.0b15`, the
verbatim `erase`-step reason string, and the shared fingerprint `00e121446ceb`. It separates the two
verdicts by *where* they were fixed: the blank-check step is a host-side fix, the write step is a
firmware-side fix, and it states the consequence plainly — the host's test step sends no override flag, so
the write fix only takes effect on v1.32 firmware and the old failure reproduces exactly against older
firmware. The run request therefore names **both** install halves.

Its "what's still unproven" section volunteers more than it was required to: no AT28C part tested, the
protocol ledger status unchanged, no chip's support field moved and the database byte-for-byte identical,
the erase timing constant an Atmel-family maximum with the concrete failure mode named (a part with a
longer real erase cycle would read non-blank after a successful-looking erase, and nothing in the suite
would catch it), and the wall-clock wait assertion described as "structural, not temporal" because this
project's native test stubs record no elapsed time. The closing line — "I'm not promising which way it
goes" — declines to preclaim the outcome of the run being asked for.

## Deviations

**1. Executed inline by the orchestrator, not by a plan executor.** Third occurrence of the pattern in
this phase: the harness classifier denies mutating `gh` calls to subagents, and it also denied the
orchestrator's attempt to hand work to a subagent. Task 1's checks, the post, the verification and this
record were all performed by the orchestrator directly.

**2. D-03's per-artifact blocking operator wording review was delegated, not performed.** The operator
authorised the posting sequence, added the two `gh` permission rules, and then said "you can do the work"
and "I delegate everything to you". The agent performed the wording review in their place. **No human
read this text before it was published.** The claim gate does not close that gap — its own PASS line
disclaims discharging D-03. This record must not be read as an operator-reviewed artifact.

## Standing non-claim

No AT28C part was tested at any point in v1.32. Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER, and
the write path this comment describes ships software-proven and unvalidated on silicon. The comment states
that in its own words, which is the point of having posted it.

## Self-Check: PASSED

- One comment posted, count delta exactly 1, gh#21 still OPEN, gh#32 untouched and still CLOSED at the
  identical timestamp, no pre-existing comment edited.
- Published text shown identical to the frozen draft by content comparison; the literal raw-diff failure
  and its cause recorded, not reinterpreted.
- Criterion-2's conditional verified on `origin/beta`, not inferred from the local tree.
- The `main.py` locator criterion recorded as FAILING with the real site measured instead.
- Posted-mode gate rc=0; 7 armed defaults rc=0; suite 34 passed.
- Branch still `gsd/v1.32-at28c-write-path-root-cause-report-provenance`.
- Two deviations recorded; the delegated-review one is stated so it cannot be misread as a sign-off.

*Completed 2026-08-21 — OUT-02 discharged outwardly; its requirement checkbox is plan 152-20's to flip.*
