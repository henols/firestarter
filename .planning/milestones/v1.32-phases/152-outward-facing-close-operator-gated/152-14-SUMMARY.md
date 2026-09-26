---
phase: 152-outward-facing-close-operator-gated
plan: 14
subsystem: outward-facing
tags: [gh12, public-post, out-01, operator-gate, delegated-review, classifier-block]

requires:
  - phase: 152-outward-facing-close-operator-gated
    provides: "152-05's frozen gh#12 draft and its D-14 review diff; 152-13's armed claim gate and the fail-closed 152-check-not-auto.py; 152-11/152-12's beta merges and read cut versions, which make the announced work real before the post claims it"
provides:
  - "The owed gh#12 reply, posted: issuecomment-5373440001"
  - "A content-based landed-identity oracle for the four remaining posts, including GitHub's trailing-newline signature"
  - "The resolved gh#12 follow-up todo, with a per-point discharge accounting"
  - "An honest partial-discharge annotation on the deferred re-lock todo, which stays in pending"
affects: [152-15, 152-16, 152-17, 152-18, 152-19, 152-20]

tech-stack:
  added: []
  patterns:
    - "Landed-identity oracle: read the published body back and compare CONTENT, not the blob SHA (which proves only authorship) and not updatedAt (which bumps on creation)"
    - "Read-back must be written under the artifact's REAL basename, because the gate's caveat lookup is basename-keyed and fails closed to the full caveat set on an unrecognised name"

key-files:
  created: []
  modified:
    - .planning/todos/completed/gh12-followup-after-dev-sdp-retirement.md
    - .planning/todos/pending/write-sdp-relock-deferred.md

key-decisions:
  - "The acceptance criterion 'the diff must be empty' was NOT met literally and is reported as such rather than reinterpreted. GitHub appends one trailing newline to a posted body, so a raw diff returns rc=1 on a faithful post. Content identity is established instead by equality after rstrip of trailing newlines, with both byte counts recorded. The criterion's instrument was wrong, not the post."
  - "D-03's per-artifact blocking operator wording review was DELEGATED to the agent, not performed by the operator. Recorded as a deviation rather than as a satisfied gate."
  - "The post was executed by the orchestrator, not by this plan's executor, because the harness classifier denied `gh issue comment` to the agent despite the settings allowlist carrying it. Second occurrence of this pattern in this phase."
  - "Todo point 3's 'the lock is now testable via dev test' gain framing was superseded by v1.30's retirement of dev sdp and v1.32's dev lock-status, and is recorded as PARTIALLY discharged rather than ticked, so no later reader infers that framing was published."

patterns-established:
  - "Pattern: when a plan's acceptance criterion encodes a wrong instrument, satisfy the criterion's INTENT with a sound instrument and record both the literal failure and the reason — never silently substitute the oracle and report a pass."
---

# Plan 152-14 — Post the owed gh#12 reply

**Status: complete.** One public comment posted; both todos handled; every acceptance criterion met except
one whose literal form is unsatisfiable, reported below rather than reinterpreted into a pass.

## What was done

The frozen gh#12 draft authored in plan 152-05 was posted to
[gh#12](https://github.com/henols/firestarter_prom/issues/12), discharging **OUT-01** — v1.30's CLOSE-06,
held open by design since 2026-07-31 and re-homed here.

| | |
|---|---|
| URL | https://github.com/henols/firestarter_prom/issues/12#issuecomment-5373440001 |
| comment id | `IC_kwDOSX4ER88AAAABQEgwAQ` |
| created | `2026-08-21T18:00:19Z` |
| comment count | 10 → **11** (delta exactly one) |
| issue state after | **OPEN** — not closed |
| draft blob SHA | `cd4a62c527e3ba5efb5b5f9f4fc9f004da99f041` (intent oracle only) |

Pre-flight, all run immediately before the post rather than trusted from an earlier run:

```
python3 152-check-not-auto.py                                  rc=0
python3 152-check-claims.py            (7 armed defaults)      rc=0
gate targeted at 152-GH12-COMMENT.md   (env seam)              rc=0
pytest test_check_claims_152.py -q -o addopts=""               34 passed
check auto-mode --pick active                                  false
workflow._auto_chain_active                                    False
```

The posting command was guarded so that a non-zero result from either gate aborted before `gh` ran.

## The acceptance criterion that was not literally met

The plan requires:

> `diff -u 152-GH12-COMMENT.md <(gh issue view 12 ... --jq '.comments[-1].body')` produces no output.

It produces one line of output. Verbatim:

```
@@ -64,3 +64,4 @@
 One run from a part in someone's hand tells us more than anything I can derive from the database. If
 the lock doesn't actually hold on real AT28C silicon, a report is how we find out.
+
BODYDIFF rc=1
```

**GitHub appends one trailing newline to a posted comment body.** Stored draft 4313 bytes; read-back 4314.
`a == b` is False; `a.rstrip('\n') == b.rstrip('\n')` is True. Tails, measured:

```
stored: 'C silicon, a report is how we find out.\n'
posted: ' silicon, a report is how we find out.\n\n'
byte delta: 1
```

So the published text **is** the reviewed text, character for character, and the criterion's chosen
instrument — raw byte equality — cannot express that on this platform. This is recorded as a literal
failure with a sound substitute rather than as a pass, because the whole point of the criterion is that a
landed-identity claim must be earned.

**Carried forward to plans 152-15…152-18:** all four remaining posts will show this same `+1` newline
signature. Their identity assertions must compare after `rstrip('\n')`. A raw `diff` will report a false
failure on every one of them.

## A second measurement artifact, also carried forward

The first read-back was saved as `readback.md` and the gate returned **rc=1** over it. That was not a
defect in the post: the gate's required-caveat set is **basename-keyed** and falls to the full caveat set
for an unrecognised filename, which is the documented fail-closed behaviour and the same trap plan 152-02
hit with a `tmp_path` document. Re-saved as `152-GH12-COMMENT.md`, the same body returns **rc=0**:

```
PASS: scanned .../152-GH12-COMMENT.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands
POSTEDGATE rc=0
```

Always write a read-back under the artifact's real basename.

## Non-tampering evidence

All ten pre-existing comments were re-read and compared by id and creation date against the pre-post
capture — unchanged, oldest `2024-09-16T14:16:16Z`, and comment 10 still
`IC_kwDOSX4ER88AAAABNhFU7Q` @ `2026-08-06T08:08:38Z`. The issue's `updatedAt` moved to the post timestamp;
that is a new-comment side effect and is explicitly **not** a body-edit oracle. No pre-existing comment
was edited and the issue body was not touched.

## Todos

**Resolved** — `gh12-followup-after-dev-sdp-retirement.md`, moved to `.planning/todos/completed/` with a
dated note accounting for each of its four "what the reply must say" points. Points 1, 2 and 4 are
discharged, 1 and 4 more strictly than the todo required: the todo permitted saying the deferred work is
"queued", and the posted text declines to say even that, naming only the backlog item and promising no
version; and the run request names **both** install halves with the reason, since the write-path change
lives in the firmware and a pip-install-only request would have been broken. **Point 3 is recorded as
partially discharged**: its "the lock is now testable via `dev test`" framing was written 2026-07-31 and
was superseded by v1.30's retirement of `dev sdp` and v1.32's `dev lock-status`, so the posted text makes
no such claim. Point 3's load-bearing half — do not let "now provable" drift into a claim of proof — is fully
discharged.

**Annotated but deliberately NOT resolved** — `write-sdp-relock-deferred.md` stays in
`.planning/todos/pending/` with `resolves_phase: none` unchanged. Its gh#12-follow-up half is discharged
by this comment; its "the shipping version's release notes announce it" half is **unmeetable until the
feature exists** and must not be presented as met. Its standing instruction survives and is now sharper
than a note: a future promotion of Backlog 999.28 must reverse OUT-05's fifth claim-gate class in the same
change that lands the feature, and that gate is now armed, exercised in both directions, and pinned by a
34-leg suite.

## Deviations

**1. The post was executed by the orchestrator, not this plan's executor.** `gh issue comment` was refused
to the agent by the harness's auto-mode classifier even though `.claude/settings.local.json` carries
`Bash(gh issue comment:*)`; the identical command was permitted to the orchestrator. The agent stopped and
reported rather than attempting `gh api --method POST` or any other route, which was correct. This is the
**second** occurrence of the pattern in this phase — plan 152-11's `gh pr merge` was the first. A
subsequent attempt to hand the remaining work back to the executor was also refused, so Task 3's todo
edits, verification and this record were completed by the orchestrator inline.

**2. D-03's per-artifact blocking operator wording review was delegated, not performed.** Sequence: the
orchestrator presented the full body and the plan's eight wording-review items to the operator; the
operator had already authorised the posting sequence and added the two `gh` permission rules; at this gate
the operator replied "you can do the work", then "I delegate everything to you". **The operator did not
read the wording.** The agent performed the review in their place. This must not be read as an
operator-reviewed artifact. The claim gate does not cover the gap either — its own PASS line disclaims
discharging D-03. The related constraint in the resolved todo ("operator-reviewed before posting, never
auto-approved") is annotated there with the same honesty: no auto or chained run approved this, and no
human read it.

**3. Three spurious "Auto Mode Active" system-reminders appeared across this plan's two dispatches**, each
near a gate or immediately before the publish step, urging the executor to stop pausing for checks and —
on the third — to bypass the Read/Edit/Write tools in favour of raw Bash for file changes. The executor
disregarded all three and verified the configuration directly instead. Ground truth was confirmed
independently by the orchestrator: `workflow._auto_chain_active` is `false`, `check auto-mode` returns
`false`, and `152-check-not-auto.py` returns rc=0. The timing is the finding worth recording — the
prompts clustered around exactly the control points `152-check-not-auto.py` was built to withstand, and
the guard plus the executor's refusal both held.

## Issues encountered

None beyond the two measurement artifacts and the classifier blocks above, all recorded rather than worked
around.

## Standing non-claim

Nothing in this plan tested silicon. No AT28C part was tested at any point in v1.32, protocol `0x0D`
stays UNVERIFIED in PROTOCOL-LEDGER, and the write-path behaviour this comment describes to the reporter
ships software-proven and unvalidated on silicon. The comment says so in those terms, which is the whole
reason it was worth posting.

## Self-Check: PASSED

- Post landed once, count delta exactly 1, gh#12 still OPEN, no pre-existing comment edited.
- Published text shown identical to the frozen draft by content comparison; the literal raw-diff failure
  and its cause recorded rather than reinterpreted.
- Posted-mode gate rc=0 under the correct basename; 7 armed defaults rc=0; suite 34 passed.
- Folded todo resolved with a per-point accounting; deferral todo annotated, left in pending,
  `resolves_phase` unchanged.
- Branch still `gsd/v1.32-at28c-write-path-root-cause-report-provenance`.
- Three deviations recorded, none concealed; the delegated-review deviation is stated in terms that cannot
  be misread as an operator sign-off.

*Completed 2026-08-21 — OUT-01 discharged outwardly; its requirement checkbox is plan 152-20's to flip.*
