---
phase: 152-outward-facing-close-operator-gated
plan: 17
subsystem: outward-facing
tags: [release-notes, app, out-04, pypi, delegated-review]

requires:
  - phase: 152-outward-facing-close-operator-gated
    provides: "152-08's authored app release body; 152-12's read cut tag and placeholder substitution; 152-13's armed gate; 152-14/15/16's content-based landed-identity oracle"
provides:
  - "The app release body, published on 3.0.0b23"
  - "Independent confirmation that the algorithm-13 bucket is 84 rows in the shipped database"
affects: [152-18, 152-19, 152-20]

tech-stack:
  added: []
  patterns:
    - "Resolve the target release by reading the release list, then confirm the release object's tag, prerelease flag and targetCommitish before writing to it"

key-files:
  created: []
  modified: []

key-decisions:
  - "The body's '84-row algorithm bucket' claim was independently re-measured against the shipped chip_database.json before publishing rather than trusted: 84 rows carry programming.algorithm == 13, and 27 carry 5. The claim stands as written."
  - "D-03's per-artifact blocking operator wording review was DELEGATED to the agent, not performed by the operator."

patterns-established:
  - "Pattern: re-measure any bare integer in outward text against the shipped artifact immediately before publishing. This phase has already had one published count fail to reproduce (151's protection-class figures), so a count is not inherited, it is measured."
---

# Plan 152-17 — Publish the app release body

**Status: complete.** The app half of **OUT-04** is discharged outwardly.

| | |
|---|---|
| release | https://github.com/henols/firestarter_app/releases/tag/3.0.0b23 |
| tag | `3.0.0b23` — resolved by reading the release list, not inferred |
| isPrerelease | `true` (unchanged) |
| targetCommitish | `86f85d77d8102b633da82aef4b5601947f6cc80b` (unchanged) |
| body length | 0 → **9261** |
| draft blob | `1fca36cdfa0e4bc733caa9847436d526464cea04` (intent oracle only) |

## Pre-flight

```
python3 152-check-not-auto.py                      rc=0
python3 152-check-claims.py  (7 armed defaults)    rc=0
gate on 152-RELEASE-NOTES-app.md (env seam)        rc=0
pytest test_check_claims_152.py -q -o addopts=""   34 passed
grep -c 'APP_TAG_TBD|FW_TAG_TBD'                   0   (no placeholder survived 152-12)
```

The publishing command was guarded so a non-zero gate result — or any surviving placeholder — aborted
before `gh release edit` ran.

## One number re-measured rather than trusted

The body states the erase timing constant is applied to an **84-row algorithm bucket**. Counts in this
project have already failed to reproduce once this milestone (151's protection-class figures, which plan
152-08 traced to a bucket conflation), so the figure was measured directly against the shipped database
instead of inherited:

```
total rows                        746
programming.algorithm == 13        84
programming.algorithm ==  5        27
```

84 is correct as shipped. The 27 also cross-checks the `protect_on_after` 27-of-27 constant recorded
earlier in the milestone. Note the row shape while doing this: `algorithm` lives under `programming`, not
at row top level, and a naive top-level read returns `None` for every row — which would have looked like a
missing field rather than a wrong path.

## Landed-identity proof

```
raw equal          : False
equal after rstrip : True
byte delta         : 1
```

Fourth consecutive publish with the platform's one-trailing-newline signature. Content identity holds.
Posted-mode gate over the read-back body under its real basename: **rc=0**.

## Non-tampering evidence

Earlier release bodies were re-read after publishing and are unchanged:

```
3.0.0b22  bodyLen=0
3.0.0b14  bodyLen=4490
2.0.8     bodyLen=0
```

`3.0.0b14` matters specifically: the published notes contain a paragraph correcting b14's *"An opt-in
re-lock after a write is deliberately not part of this release"* sentence, and the correction is made **in
the new notes** while b14 stays published exactly as written. Its body length is unchanged, so that promise
held in practice and not just in prose. This is the discharge of the folded todo's constraint to correct
the next release notes rather than rewrite the shipped ones.

## What the published body claims and declines to claim

It records its own provenance — the tag read, the reading command and timestamp, the merge commit it was
cut from and the target commit — so a reader can retrace it. It verifies PyPI **independently of GitHub**
and states the live divergence rather than glossing it: GitHub carries stable `2.0.8` that PyPI's
`info.version` does not report (still `2.0.7`), and the body explicitly disclaims that anything in it
should be read as claiming a GitHub-only release is pip-installable. It also warns that the two
repositories version independently, so the app and firmware numbers will not agree and are not expected
to — pre-empting a natural misreading.

It states that the write-path fix lives in the **firmware**, so installing the app update alone does not
pick it up, and names both install halves. It uses the robust protection-class framing (665 of 746 rows
resolve to a refusal class, 81 read-permitted) rather than any per-class count. The one exploratory
`lock-status` run this milestone made is called a **probe, never a validation**, with the note that it is
not even from the family under discussion. **Correction, 2026-08-21 (see 152-19-SUMMARY and 152-LEDGER
§process failures):** as published, that paragraph named the part a `W29C040`; the seated part was a
`W29C020` and no `W29C040` was ever available. Found during plan 152-19's live evidence capture, escalated,
and corrected in the published body with a visible errata line on an operator decision. The withdrawn re-lock command is named exactly once in the
body, in its withdrawal sentence, naming Backlog 999.28 with no version promised.

Its "Not established" list is the longer of the two sections: no AT28C part tested, `0x0D` still
UNVERIFIED, no support classification moved and the database otherwise byte-unchanged, all three community
threads still open with "a code fix is not a validation", the erase timing constant an Atmel-family maximum
over a bucket spanning other vendors with the concrete failure mode named, the wall-clock wait structurally
untestable because the native stubs record no elapsed time, and the advisory `protect_on_after` field
having no runtime consumer in this release.

## Deviations

**1. Executed inline by the orchestrator.** Fifth occurrence in this phase; mutating `gh` is denied to
subagents and delegating to one is denied too.

**2. D-03's per-artifact blocking operator wording review was delegated, not performed.** The operator
authorised the sequence, granted the `gh release edit` rule, and delegated the review. **No human read
this body before it was published.** The claim gate does not close that gap; its own PASS line disclaims
discharging D-03.

## Standing non-claim

No AT28C part was tested at any point in v1.32. Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER, and
everything this release announces about the 28C write path ships software-proven and unvalidated on
silicon. The published body says so in its own words, in a section longer than the one listing what works.

## Self-Check: PASSED

- Body published to the tag CI actually cut, resolved by reading rather than inference.
- Prerelease flag and target commit unchanged by the edit; three earlier bodies confirmed untouched.
- Published text shown identical to the reviewed draft by content comparison; literal raw-diff failure
  attributed to the platform's trailing newline.
- The one bare integer in the outward text re-measured against the shipped database before publishing.
- Posted-mode gate rc=0; 7 armed defaults rc=0; suite 34 passed.
- Branch still `gsd/v1.32-at28c-write-path-root-cause-report-provenance`.

*Completed 2026-08-21 — the app half of OUT-04 discharged outwardly; the checkbox is plan 152-20's to flip.*
