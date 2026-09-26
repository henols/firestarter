---
phase: 152-outward-facing-close-operator-gated
plan: 16
subsystem: outward-facing
tags: [gh11, public-post, out-03, attribution-fix, operator-decision, draft-amendment]

requires:
  - phase: 152-outward-facing-close-operator-gated
    provides: "152-07's frozen gh#11 draft; 152-13's armed claim gate and fail-closed guard; 152-14/152-15's content-based landed-identity oracle and the trailing-newline signature"
provides:
  - "The gh#11 reply, posted: issuecomment-5373770561 — a 2026-08-03 commitment discharged 18 days late, explicitly as a kept promise"
  - "A corrected public attribution: both AT28C reporters credited by name"
affects: [152-17, 152-18, 152-19, 152-20]

tech-stack:
  added: []
  patterns:
    - "A frozen draft can carry a defect no automated gate can see: an attribution claim about named third parties is not a forbidden phrase, so only a reader catches it"

key-files:
  created: []
  modified:
    - .planning/phases/152-outward-facing-close-operator-gated/152-GH11-COMMENT.md
    - .planning/phases/152-outward-facing-close-operator-gated/152-GH11-COMMENT.diff

key-decisions:
  - "The draft's claim that one reporter 'remains the only person who has ever run any part of this against real AT28C silicon' was found FALSE before posting and amended on an operator decision to credit both reporters by name. The other reporter was tagged two paragraphs earlier in the same draft, so publishing it would have read as erasing his contribution to his face."
  - "The amendment went through the authoring path (draft edit + recorded .diff + re-gate + its own commit attributed to 152-07) rather than being edited inside this posting plan, per this plan's prohibition on altering the draft."
  - "The ambiguity was escalated to the operator rather than resolved by the agent: gh#21 and gh#32 share fingerprint 00e121446ceb with byte-identical auto_capture blocks, which is consistent with one run reported twice, so the underlying data could not settle a claim about persons."
  - "D-03's per-artifact blocking operator wording review was DELEGATED for the wording generally, but the attribution question specifically WAS put to the operator and answered by them."

patterns-established:
  - "Pattern: escalate a factual claim about named third parties even under a broad delegation. The cost of asking is one question; the cost of being wrong is public and lands on someone else."
---

# Plan 152-16 — Post the gh#11 reply

**Status: complete.** **OUT-03** discharged outwardly, and one attribution defect caught before it went
public rather than after.

| | |
|---|---|
| URL | https://github.com/henols/firestarter_prom/issues/11#issuecomment-5373770561 |
| comment id | `IC_kwDOSX4ER88AAAABQE07QQ` |
| created | `2026-08-21T18:32:30Z` |
| comment count | 18 → **19** (delta exactly one) |
| gh#11 state after | **OPEN** — not closed |
| amended draft blob | `a4cba59b1c3c47c0d03175e4f7382a2f73ba11db` (intent oracle only) |

## Pre-flight

```
python3 152-check-not-auto.py                     rc=0
python3 152-check-claims.py  (7 armed defaults)   rc=0
gate on 152-GH11-COMMENT.md  (env seam)           rc=0   (before AND after the amendment)
pytest test_check_claims_152.py -q -o addopts=""  34 passed
```

The 2026-08-03 commitment this reply discharges was re-read live rather than taken from research:
`@datapaganism` reported hacking a `CMD_ERASE` into `configure_eeprom28c` and asked how to trigger it
(`IC_kwDOSX4ER88AAAABM9aCWw`, `09:33:02Z`); the reply that day was *"It's not probably implemented yet, I
will soon get it pushed and I will keep you posted"* (`IC_kwDOSX4ER88AAAABM9coOw`, `09:36:48Z`). He then
asked to be answered on the issue rather than Discord (`IC_kwDOSX4ER88AAAABM9jWmw`). So this reply is owed
in this venue specifically, and the posted text opens by naming that exchange, quoting the commitment, and
saying the push landed 18 days later — "that promise being kept, not a silence being broken."

## The defect caught before publication

The frozen draft said:

> `@datapaganism`, you remain **the only person who has ever run any part of this against real AT28C
> silicon** — that was true when the 2026-07-30 comment above was written, and it is still true after this
> milestone.

`@AndersBNielsen` filed gh#21, an `at28c256` `dev test` report, under his own account — and he is tagged
two paragraphs earlier in the same draft, credited for the page-write analysis that justified removing the
pre-write blank check. Publishing the sentence would have told one contributor he was the only one, in a
comment that simultaneously thanked the other.

**No automated gate could catch this.** It is not a forbidden phrase, a missing caveat, or an unqualified
claim word — the claim gate passed the draft cleanly both before and after the fix. It is an attribution
error about named third parties, and only a reader finds that class.

**The data could not settle it either**, which is why it went to the operator instead of being decided
here. gh#21 (`AndersBNielsen`, 2026-08-06) and gh#32 (`datapaganism`, 2026-08-07) share fingerprint
`00e121446ceb`, and their `auto_capture` blocks are byte-identical — same host `3.0.0b15`, same
`"Rev 2.0-class, Override HW: Rev 2.3"`, same nulls throughout. That is consistent with one run reported
twice, in which case the original sentence would have been defensible. The operator resolved it: two
people, two runs, credit both by name.

### The amendment, via the authoring path

This plan's prohibitions forbid altering the draft here — wording changes go back through the gate and the
diff artifact first. So the edit was made to the draft, a unified diff was written to
`152-GH11-COMMENT.diff`, the gate was re-run green, and it was committed as `12973677` attributed to
**152-07** (the authoring plan), not to this one. Then this plan posted.

```
-what runs before it, not in any test. @datapaganism, you remain the only person who has ever run any
-part of this against real AT28C silicon — that was true when the 2026-07-30 comment above was
-written, and it is still true after this milestone.
+what runs before it, not in any test. @datapaganism and @AndersBNielsen are the only people who have
+run an AT28C part against this project at all — everything else this project believes about this
+family is derived from datasheets and the chip database, not from silicon. That was true when the
+2026-07-30 comment above was written, and it is still true after this milestone.
```

The replacement also avoids a fragile count of reports, saying instead what is durably true: everything
else the project believes about this family comes from datasheets and the chip database, not silicon.
`grep -c '@datapaganism and @AndersBNielsen'` over the **published** body returns 1.

## Landed-identity proof

```
raw equal          : False
equal after rstrip : True
byte delta         : 1
```

Third consecutive post with GitHub's one-trailing-newline signature. Content identity holds; the literal
"diff must be empty" criterion is unmet for the platform reason recorded in 152-14, not for anything about
the post. Posted-mode gate over the read-back body under its real basename: **rc=0**.

## What the posted comment claims and declines to claim

It answers the report in terms of the completion-vs-data-landed conflation, which is its actual shape: the
host's `info` said the part was erasable from its electrical type, the wire `flags` cleared the
erase-capability bit for the algorithm, and the firmware handler had no erase arm — three places
disagreeing at once. It states the capability was real in silicon and that what was false was only that
firestarter could perform it, which is the corrected Phase 121 premise this milestone also fixed in the
in-repo record. It cites Microchip DS20006386B Table 6-1 (p. 11) so a reader can check independently, names
Atmel Application Note 0544B as the shipped software six-byte path, and states why the datasheet's hardware
mechanism was rejected — it drives 12 V onto a pin of a 5 V part's pinout.

Its limits are volunteered rather than extracted: the erase timing constant is an Atmel-family maximum
applied to an algorithm bucket spanning other vendors, with the concrete failure mode named; and the
wall-clock wait is "untestable by construction here, not merely untested so far", because the native test
harness never stubs `delay()` and records no elapsed time. It also pre-empts an overclaim nobody asked
about — the firmware now reads the page value from the database rather than a constant, and for this part
those values are identical, so that work explains none of the failures on the thread. It names both install
halves with the reason, and deliberately names no release version, so the comment holds whenever it is read.

## Deviations

**1. Executed inline by the orchestrator.** Fourth occurrence in this phase — mutating `gh` is denied to
subagents and delegating to a subagent is denied too, so pre-flight, the amendment, the post, verification
and this record were all done directly.

**2. The draft was amended after being frozen.** Recorded above; done through the authoring path with a
committed diff, on an operator decision, not as an ad-hoc edit inside the posting plan.

**3. D-03's wording review was delegated in general — but not on the point that mattered.** The operator
delegated the wording review ("you can do the work", "I delegate everything to you") and did not read the
body. The attribution question **was** escalated and **was** answered by the operator, who chose to credit
both reporters by name. So: the general wording was agent-reviewed; the one factual claim about named third
parties was operator-decided. Recorded at that resolution so neither half is overstated.

## Standing non-claim

No AT28C part was tested at any point in v1.32. Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER, and
the erase and write behaviour this comment describes ships software-proven and unvalidated on silicon. The
posted text says as much in its own words, including that a code fix is not a validation and that all three
threads on this chip family stay open.

## Self-Check: PASSED

- One comment posted, count delta exactly 1, gh#11 still OPEN.
- An attribution error found before publication, escalated rather than guessed, fixed through the
  authoring path with a committed diff, and confirmed present in the published body.
- Published text shown identical to the amended draft by content comparison; literal raw-diff failure
  attributed to the platform, not the post.
- Posted-mode gate rc=0; 7 armed defaults rc=0; suite 34 passed, before and after the amendment.
- Branch still `gsd/v1.32-at28c-write-path-root-cause-report-provenance`.

*Completed 2026-08-21 — OUT-03 discharged outwardly; its requirement checkbox is plan 152-20's to flip.*
