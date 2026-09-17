---
title: Adoption instrument retirement — the claim it gated was fired without it, and what is lost with it
date: 2026-09-17
context: v1.39 Phase 196, INSTR-01 / INSTR-02 (D-01, D-02, D-04, D-05, D-06) — read from the live script before deletion
---

# Adoption instrument retirement (INSTR-01)

## VERDICT

**The adoption instrument is retired outright — the script is deleted, on the operator's own
decision.** The operator fired the `henols/firestarter` slug claim on 2026-09-14 with the trigger
not met: fixed share was 12.8% against a 90% threshold, and there were 116 at-risk `2.0.7`
downloads against a ceiling of 10, both measured over the 90-day stable-channel window ending
2026-09-13. The operator was shown those figures and the consequence, and directed the act
regardless. The instrument's question now has no consumer because of that act, not because the
instrument stopped working — it still ran correctly, and would still have run correctly, on the
day it was retired. The operator's grounds, in their own words: *"I have no idea what it
is… Don't understand why we should need it."* Directed to be deleted outright, with none of the
underlying method kept regardless of what that cost. That is recorded here so a later reader does
not read the deletion as an oversight or as evidence the property stopped mattering. It was not a
threshold breach and it was not an accident.

This note carries everything the disposition requires it to carry: the cause of the retirement,
the two alternatives that were offered and declined, the accepted cost of losing the method, and
the residual gap that remains.

## 1. What the instrument measured, and what it reported

The instrument measured, for the `firestarter` PyPI package, the split between downloads of a
fixed stable version and downloads of the single at-risk stable version, restricted to the pip and
uv installers, over a rolling 90-day window on the stable channel.

Each run reported eight lines to standard output: the window's start and end dates, the two
download counts, the fixed-share percentage, the threshold the reading was judged against, and a
one-line `TRIGGER: MET` / `TRIGGER: NOT MET` verdict. Every run, unconditionally, then printed a
block naming what the reading did not and could not measure — that installed base is not directly
observable, that download share is only ever a proxy for it, and that a user who installed the
at-risk version and never reinstalls it generates zero downloads and is invisible to any instrument
of this kind.

## 2. The two alternatives offered and declined

Two alternatives were offered to the operator, and both were declined.

The first: re-point the instrument at stranded-`2.0.7` acquisition, so it would measure whether
people were still newly acquiring the stranded release, rather than continuing to answer the
fixed-share question it was built to answer. Declined — the operator's decision was to retire the
instrument outright, not to repurpose it toward a different, narrower question.

The second: defer the disposition to a post-research checkpoint rather than deciding it up front,
before planning began. Declined — the operator settled the question, retire it, ahead of that
checkpoint.

A disposition recorded without its rejected options is not auditable, which is why both are named
here rather than left implicit.

## 3. What is lost with it — stated, not hidden

Two distinct things are lost with the instrument, and both are stated here as losses rather than
left implicit.

The first is the method. The working approach took a phase to establish and is non-obvious — a
naive comparison of the version numbers as plain strings sorts them wrongly, so re-deriving the
same reading is not a short job. The undo cost is rated costly, and the operator accepted it
knowingly, directing that none of the method be kept regardless of that cost.

The second is epistemic. Installed base was never observable through this instrument, or through
any other instrument — download share was only ever a proxy for it. What is lost, then, is a
proxy, not a census, and nothing better replaces it.

## 4. The residual gap, named explicitly

**With the instrument gone, nothing in this repository measures the split between fixed-version
and at-risk-version downloads for the `firestarter` PyPI package, at all.** No successor is
planned, and no follow-up is filed for this gap here — the operator's decision was to retire the
question along with the instrument that answered it, not to defer it to a future guard.

A reader who meets only this description still has a way back to the artifact itself. The PyPI
per-version download-share instrument survives in the deleting commit — `git log
--diff-filter=D -- tools` finds it in this repository's history — and that commit's own message
names the removed path in full. Nothing about how the instrument worked comes back with that
route; it only locates where the artifact itself still exists.

Naming a gap and filing a gap are different acts; this note performs only the first.
