# 152-CLAIM-GATE-TRANSCRIPTS.md — RED/GREEN evidence for `152-check-claims.py`

**This file deliberately contains forbidden vocabulary, quoted verbatim as evidence of what the
gate rejected. It is NOT a claim about the outward-facing close, and it is deliberately NOT a gate
target — it is absent from `152-check-claims.py`'s `_DEFAULT_TARGETS` by design (see the module's
own docstring and `test_the_transcript_file_is_not_a_gate_target` in `test_check_claims_152.py`).**
A future reader must not "fix" this file by rewording the RED blocks below to remove the forbidden
phrases — doing so would destroy the evidence the transcript exists to preserve. If this file were
ever added to `_DEFAULT_TARGETS`, every RED block below would make the gate permanently fail against
its own proof of itself working.

All commands below were run from
`.planning/phases/152-outward-facing-close-operator-gated/` with `python3` (3.12.13). Every `###`
heading pastes the literal command line, followed by the gate's literal stdout and its literal
`EXIT=` value — nothing paraphrased.

---

## RED — one block per forbidden-pattern label this phase added or modified

Each planted fixture carries all three required caveats and exactly one planted violation, so each
failure below is attributable to its own forbidden pattern and to nothing else about the document
(proven by `test_every_forbidden_pattern_has_a_planted_fixture` and the dedicated new legs, which
assert leg isolation programmatically; the transcripts below are the same runs, pasted for human
review).

### 1. `sdp-relock-as-shipped` — ADDED (plant = the roadmap's pre-amendment criterion-1 wording)

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_sdp_relock_as_shipped.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_sdp_relock_as_shipped.md:12: forbidden phrase match [sdp-relock-as-shipped]: 'write --sdp-relock'
EXIT=1
```

The plant's line 12 reads, in full: "The planted sentence, taken verbatim from ROADMAP.md's
pre-amendment criterion 1: `enable` returns as `write --sdp-relock`." — the command name is not
followed by a withdrawal predicate, so the negative lookahead does not permit it.

### 2. `sdp-relock-flag-as-shipped` — ADDED (the bare-flag companion)

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_sdp_relock_bare_flag.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_sdp_relock_bare_flag.md:11: forbidden phrase match [sdp-relock-flag-as-shipped]: '--sdp-relock'
EXIT=1
```

The plant's line 11 reads: "The planted sentence: the `--sdp-relock` option is available for
re-protecting a part." — no `write` precedes the flag (so the row-1 lookbehind does not suppress
it) and no withdrawal predicate follows it. Note this fires the bare-flag row alone, not the
command-first row — leg isolation, proven again by
`test_planted_sdp_relock_bare_flag_is_rejected`.

### 3. `issue-closed` — MODIFIED (32 dropped), with the three still-fires controls

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_issue_closed_gh21.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_issue_closed_gh21.md:11: forbidden phrase match [issue-closed]: 'gh#21 was closed'
EXIT=1
```

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_issue_closed_gh11.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_issue_closed_gh11.md:11: forbidden phrase match [issue-closed]: 'gh#11 was resolved'
EXIT=1
```

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_issue_closed_gh12.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_issue_closed_gh12.md:11: forbidden phrase match [issue-closed]: 'gh#12 was fixed'
EXIT=1
```

The row's alternation dropped `32` from `gh#(?:21|32|11|12)\b...` to `gh#(?:21|11|12)\b...`
(`152-RESEARCH.md` §C-5, D-05), so D-05's own required statement about gh#32 is expressible (see
the ALLOW section below) while gh#21, gh#11 and gh#12 all still fire — the narrowing did not become
a general loosening of the row.

---

## RED — donor-carried rows, for completeness

### 4. `proven-unqualified` — carried VERBATIM from the donor, narrowed to `(?<!software-)\bproven\b`

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_proven_unqualified.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 3 forbidden phrase match(es):
  fixtures/planted_proven_unqualified.md:2: forbidden phrase match [proven-unqualified]: 'proven'
  fixtures/planted_proven_unqualified.md:2: forbidden phrase match [proven-unqualified]: 'proven'
  fixtures/planted_proven_unqualified.md:16: forbidden phrase match [proven-unqualified]: 'proven'
EXIT=1
```

The plant's line 16 reads, in full: "The planted sentence: the write path is bench-proven on one
part, one controller, one shield revision." — a bare `bench-proven` compound, which is NOT the
`software-proven` compound the negative lookbehind permits. The two line-2 hits come from this
file's own HTML-comment header describing the plant, which independently uses the word twice. The
gate still exits non-zero and still names `proven-unqualified` — the narrowing did not disarm the
pattern.

### 5. `graduation` — donor-carried, unmodified

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_graduation.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_graduation.md:11: forbidden phrase match [graduation]: 'promoting protocol 13'
EXIT=1
```

### 6. `support-status-change` — donor-carried, unmodified

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_support_status_change.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_support_status_change.md:11: forbidden phrase match [support-status-change]: 'support_status:'
EXIT=1
```

### 7. `at28c256-fixed` — donor-carried, unmodified

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_at28c256_fixed.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_at28c256_fixed.md:11: forbidden phrase match [at28c256-fixed]: 'AT28C256 write path is finally fixed'
EXIT=1
```

### 8. `page-size-proven` — donor-carried, unmodified

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_page_size_proven.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_page_size_proven.md:11: forbidden phrase match [page-size-proven]: 'page size is validated'
EXIT=1
```

### 9. Missing required caveat — the `software-proven-unvalidated` row

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_missing_caveat_software_proven.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 file(s) missing a required caveat:
  fixtures/planted_missing_caveat_software_proven.md: missing required caveat [software-proven-unvalidated]: expected a phrase matching 'the software-proven / unvalidated-on-silicon qualifier'
EXIT=1
```

### 10. Missing required caveat — the `no-at28c-part-tested` row

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_missing_caveat_no_at28c.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 file(s) missing a required caveat:
  fixtures/planted_missing_caveat_no_at28c.md: missing required caveat [no-at28c-part-tested]: expected a phrase matching 'the "no AT28C part was tested" qualifier'
EXIT=1
```

### 11. Missing required caveat — the `zero-d-stays-unverified` row

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=fixtures/planted_missing_caveat_unverified.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 file(s) missing a required caveat:
  fixtures/planted_missing_caveat_unverified.md: missing required caveat [zero-d-stays-unverified]: expected a phrase matching 'the "0x0D stays UNVERIFIED in PROTOCOL-LEDGER" qualifier'
EXIT=1
```

---

## ALLOW — the two clean controls

```
$ python3 152-check-claims.py fixtures/clean_control.md ; echo EXIT=$?
PASS: scanned fixtures/clean_control.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
EXIT=0
```

```
$ python3 152-check-claims.py fixtures/clean_control_second.md ; echo EXIT=$?
PASS: scanned fixtures/clean_control_second.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
EXIT=0
```

`clean_control.md` carries the mandated `write --sdp-relock` withdrawal word order ("is
withdrawn -- tracked as Backlog 999.28") and D-05's gh#32 statement in the natural past-tense
phrasing ("gh#32 was closed on 2026-08-08 as a duplicate fold into gh#21") — this control proves
that the mandated withdrawal word order survives class (e), and that D-05's gh#32 statement
survives the narrowed `issue-closed` row.

`clean_control_second.md` carries a second, differently-worded withdrawal predicate ("remains
withdrawn, for a second release"), the parenthetical gh#32 form ("gh#32 (closed 2026-08-08, folded
into gh#21)"), and D-11's two exempted statements of shipped command behaviour ("Standalone erase
is now available on this protocol, and write no longer performs a blank check on it") — this
control proves that a second withdrawal phrasing and D-11's exempted statements of current,
user-visible command behaviour both survive the same forbidden-class table.

---

## GREEN — the real default targets, no argv, no seam

```
$ python3 152-check-claims.py ; echo EXIT=$?
PASS: scanned 152-CLAIM-CLASSES.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
EXIT=0
```

This is the literal mechanical discharge of "armed against the real files" for this plan's scope:
the gate is armed against `152-CLAIM-CLASSES.md`, the one artifact Plan 152-01 already wrote,
while every other `152-*` artifact this phase will publish is still being written. A later plan
extends `_DEFAULT_TARGETS` and re-runs this transcript (see the "Extended target list" section
below).

---

## Paired suite — `python3 -m pytest test_check_claims_152.py -q -o addopts=""`

```
$ python3 -m pytest test_check_claims_152.py -q -o addopts=""
..............................                                           [100%]
30 passed in 1.13s
```

All 30 legs pass: the 20 donor legs (renamed to this phase's own module, env seam, and adapted to
this phase's committed fixtures where the donor's own generic fixtures do not exist here) plus the
six phase-specific legs — the two `sdp-relock` isolation legs, the mandated-withdrawal-sentence
leg, the three-fixture `issue-closed` still-fires leg, the gh#32-permitted leg, and the
three-fixture required-caveat-independence leg.

---

## What this transcript does and does not prove

**Does prove:** every forbidden-pattern label this phase added or modified (`sdp-relock-as-shipped`,
`sdp-relock-flag-as-shipped`, the narrowed `issue-closed`) fires on a real planted document via a
real subprocess invocation of the real gate script, attributable to that label alone; every
donor-carried row this phase did not modify still fires; each of the three required-caveat rows
fails independently on its own dedicated missing-caveat plant; the mandated `write --sdp-relock`
withdrawal word order and D-05's gh#32 closure statement both survive the same table that rejects
their shipped-framing and closed-issue counterparts; the gate is armed against the real
`152-CLAIM-CLASSES.md` artifact and passes.

**Does not prove (the gate's own explicit non-claim, from its module docstring):** that any scanned
document's prose is honest in every implication, omission or tone — only that it is free of this
specific forbidden-phrase table and carries the caveats its own per-file rule demands. A green gate
is not a wording review. D-03's per-artifact blocking operator checkpoint is the separate control
that reviews wording, and this transcript does not discharge it and must not be cited as
discharging it.

---

## Extended target list (Plan 152-13)

Plan 152-13 extends `_DEFAULT_TARGETS` from the single `152-CLAIM-CLASSES.md` entry armed above to
seven entries: the claim-classes contract, the three GitHub comment drafts (gh#12, gh#21, gh#11),
both release-note bodies (app, firmware), and the merge record. All commands below were re-run from
this same directory with `python3` (3.12.13), immediately after the extension.

### RED — armed at the real seven-target list, plus the specified plant via the env seam

The env seam is pointed at all seven real `_DEFAULT_TARGETS` entries **plus**
`fixtures/planted_sdp_relock_as_shipped.md` (the same plant described above, in the section titled
"one block per forbidden-pattern label this phase added or modified" — the roadmap's pre-amendment
criterion-1 wording, taken verbatim). This is the proof that the gate rejects the specified planted
violation *while pointed at the real outward artifacts*, not only at a fixture scanned in isolation.

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152="152-CLAIM-CLASSES.md:152-GH12-COMMENT.md:152-GH21-COMMENT.md:152-GH11-COMMENT.md:152-RELEASE-NOTES-app.md:152-RELEASE-NOTES-fw.md:152-MERGE-RECORD.md:fixtures/planted_sdp_relock_as_shipped.md" python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  fixtures/planted_sdp_relock_as_shipped.md:12: forbidden phrase match [sdp-relock-as-shipped]: 'write --sdp-relock'
EXIT=1
```

The six real outward artifacts all scan clean; only the appended plant fails, attributed to its own
label alone — the six real files are not named in the `FAIL:` output at all, which is the gate's
per-file scanning contract working exactly as designed even when a plant is mixed into the real list.

### GREEN — defaults only, no argv, no seam

```
$ python3 152-check-claims.py ; echo EXIT=$?
PASS: scanned 152-CLAIM-CLASSES.md, 152-GH12-COMMENT.md, 152-GH21-COMMENT.md, 152-GH11-COMMENT.md, 152-RELEASE-NOTES-app.md, 152-RELEASE-NOTES-fw.md, 152-MERGE-RECORD.md; 6 of 6 caveat-required file(s) carry every caveat their own rule demands; 1 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
EXIT=0
```

All seven real artifacts are named in the single `PASS:` line. Six are caveat-required and carry
every caveat their own rule demands (`152-CLAIM-CLASSES.md`, the three comment drafts, both
release-note bodies); the seventh, `152-MERGE-RECORD.md`, is the one file counted in "1 file(s)
carry no caveat requirement" — matching its empty-frozenset exemption in `_CAVEAT_RULES`, mirroring
the donor's own transcript-file exemption for a captured handoff record that is not itself a claim
register.

### Paired suite — re-run after the extension

```
$ python3 -m pytest test_check_claims_152.py -q -o addopts=""
..................................                                       [100%]
34 passed in 1.15s
```

34 legs: the 30 legs recorded above plus one new leg from this same plan (the `verified-on-silicon`
word-boundary fix's paired both-directions leg) and three new guard legs for `152-check-not-auto.py`
(selectable by `-k not_auto`).

---

### The `verified-on-silicon` false-positive — found and fixed in this plan

**Reproduced before the fix:**

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=/tmp/probe.md python3 152-check-claims.py ; echo EXIT=$?
FAIL: 1 forbidden phrase match(es):
  /tmp/probe.md:1: forbidden phrase match [verified-on-silicon]: 'VERIFIED on silicon'
FAIL: 3 file(s) missing a required caveat:
  /tmp/probe.md: missing required caveat [no-at28c-part-tested]: expected a phrase matching 'the "no AT28C part was tested" qualifier'
  /tmp/probe.md: missing required caveat [software-proven-unvalidated]: expected a phrase matching 'the software-proven / unvalidated-on-silicon qualifier'
  /tmp/probe.md: missing required caveat [zero-d-stays-unverified]: expected a phrase matching 'the "0x0D stays UNVERIFIED in PROTOCOL-LEDGER" qualifier'
EXIT=1
```

`/tmp/probe.md` contained one line: `Protocol \`0x0D\` remains UNVERIFIED on silicon.` — a NON-claim,
the exact opposite of the forbidden claim the row exists to catch. The donor's row had no leading word
boundary, so "UNVERIFIED on silicon" matched. **Fixed** with a fixed-width negative lookbehind
`(?<!un)` immediately ahead of `verified` in the `verified-on-silicon` pattern (Python's `re` requires
fixed-width lookbehinds; two characters, case-insensitive by the compiled flag, so it also suppresses
"Un-verified"-style spellings this milestone's own usage does not produce). A paired both-directions
test leg (`test_verified_on_silicon_permits_unverified_but_still_rejects_verified`) now asserts the
non-claim is permitted and the real claim is still rejected, in one leg, so the fix cannot silently
become a hole. Nothing shipped in this phase before the fix ever hit this pattern — the three
canonical required caveats all phrase the non-claim as "stays UNVERIFIED in PROTOCOL-LEDGER", never
"...on silicon" — so this was a latent trap for future outward text, not a live break.

---

## The withdrawal-presence check, and why it is not a gate row

Criterion 4 requires each release-note body to name `write --sdp-relock` explicitly, as withdrawn;
criterion 5 forbids naming it as shipped. This gate's `sdp-relock-as-shipped` / `sdp-relock-
flag-as-shipped` rows enforce the WORD-ORDER half of that pair — reject unless a withdrawal predicate
immediately follows the command name. A fourth required-caveat row was considered, to enforce the
PRESENCE half the same way the three `REQUIRED_CAVEAT_PATTERNS` rows enforce the ledger qualifiers,
and was **not** taken: `_required_caveats_for()`'s fail-closed default demands the FULL caveat set for
any basename absent from `_CAVEAT_RULES`, so adding a fourth row would have forced the literal
`write --sdp-relock` command string into every fixture and every scanned artifact this gate has ever
been armed against — including the three comment drafts, which never mention SDP relock at all — just
to keep the fail-closed default from producing a false failure on files that have no reason to carry
that sentence.

The presence half is instead enforced where it is cheap to enforce without that side effect: a
positive `grep` assertion on both release-note bodies, run in Plans 152-08, 152-09 and re-verified
after the tag substitution in Plan 152-12; the same assertion is re-run against the **posted** bodies
in Plans 152-17 and 152-18. The word-order half stays the gate's job, everywhere, forever. Both halves
are named here so the split is a recorded decision, not an omission a future reader has to rediscover.

## Posted mode

Posted-mode temp files — the copies a posting plan writes out of a just-posted body, to re-verify it
byte-for-byte against the frozen draft — are written under the SAME basename as the draft they verify
(e.g. a posted-mode copy of the gh#12 comment is named `152-GH12-COMMENT.md` in its own temp
directory). This is because `_required_caveats_for()` is keyed on `os.path.basename(path)` and fails
closed to the FULL caveat set for any basename it does not recognise: a posted comment body carries no
release-note caveat requirement (`_CAVEAT_RULES["152-GH12-COMMENT.md"]` is `frozenset({"no-at28c-part-
tested"})`, not the full set), so a temp file under any other basename would be held to the full set
and produce a false missing-caveat failure against a document that was never required to carry a
release-note qualifier in the first place. This rule is recorded as a comment in `152-check-claims.py`
immediately above `_DEFAULT_TARGETS`, and the posting plans (152-14 through 152-18) are its consumers.

---

## Final target list (close-out, Plan 152-20 — the last SUMMARY added via argv)

Plan 152-20 extended `_DEFAULT_TARGETS` from eight entries to **27** — the eight claim-bearing
artifacts plus every plan SUMMARY through `152-19`. `152-20-SUMMARY.md` is deliberately **not** a
member: it does not exist while Plan 152-20 runs, and the gate's fail-closed missing-target branch
would drive every remaining run of this phase non-zero. The suite's arming leg now pins that shape
in three parts — the eight named artifacts are members, the SUMMARY members are exactly
`152-01`…`152-19`, and `152-20-SUMMARY.md` is asserted *absent* with a comment naming the trap so a
future reader does not "fix" it.

### The extended list (27 entries, every one existing on disk, every dirname this phase directory)

```
   1. 152-CLAIM-CLASSES.md
   2. 152-GH12-COMMENT.md
   3. 152-GH21-COMMENT.md
   4. 152-GH11-COMMENT.md
   5. 152-RELEASE-NOTES-app.md
   6. 152-RELEASE-NOTES-fw.md
   7. 152-MERGE-RECORD.md
   8. 152-LEDGER.md
   9. 152-01-SUMMARY.md
  10. 152-02-SUMMARY.md
  11. 152-03-SUMMARY.md
  12. 152-04-SUMMARY.md
  13. 152-05-SUMMARY.md
  14. 152-06-SUMMARY.md
  15. 152-07-SUMMARY.md
  16. 152-08-SUMMARY.md
  17. 152-09-SUMMARY.md
  18. 152-10-SUMMARY.md
  19. 152-11-SUMMARY.md
  20. 152-12-SUMMARY.md
  21. 152-13-SUMMARY.md
  22. 152-14-SUMMARY.md
  23. 152-15-SUMMARY.md
  24. 152-16-SUMMARY.md
  25. 152-17-SUMMARY.md
  26. 152-18-SUMMARY.md
  27. 152-19-SUMMARY.md
```

### Defaults GREEN — untruncated

```
$ python3 152-check-claims.py
PASS: scanned 152-CLAIM-CLASSES.md, 152-GH12-COMMENT.md, 152-GH21-COMMENT.md, 152-GH11-COMMENT.md, 152-RELEASE-NOTES-app.md, 152-RELEASE-NOTES-fw.md, 152-MERGE-RECORD.md, 152-LEDGER.md, 152-01-SUMMARY.md, 152-02-SUMMARY.md, 152-03-SUMMARY.md, 152-04-SUMMARY.md, 152-05-SUMMARY.md, 152-06-SUMMARY.md, 152-07-SUMMARY.md, 152-08-SUMMARY.md, 152-09-SUMMARY.md, 152-10-SUMMARY.md, 152-11-SUMMARY.md, 152-12-SUMMARY.md, 152-13-SUMMARY.md, 152-14-SUMMARY.md, 152-15-SUMMARY.md, 152-16-SUMMARY.md, 152-17-SUMMARY.md, 152-18-SUMMARY.md, 152-19-SUMMARY.md; 26 of 26 caveat-required file(s) carry every caveat their own rule demands; 1 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
GATE rc=0
```

### Positional-argv run over the nineteen SUMMARY files

This proves the positional path works on exactly the class of file that will carry the final one.

```
$ python3 152-check-claims.py 152-0*-SUMMARY.md 152-1*-SUMMARY.md
PASS: scanned 152-01-SUMMARY.md, 152-02-SUMMARY.md, 152-03-SUMMARY.md, 152-04-SUMMARY.md, 152-05-SUMMARY.md, 152-06-SUMMARY.md, 152-07-SUMMARY.md, 152-08-SUMMARY.md, 152-09-SUMMARY.md, 152-10-SUMMARY.md, 152-11-SUMMARY.md, 152-12-SUMMARY.md, 152-13-SUMMARY.md, 152-14-SUMMARY.md, 152-15-SUMMARY.md, 152-16-SUMMARY.md, 152-17-SUMMARY.md, 152-18-SUMMARY.md, 152-19-SUMMARY.md; 19 of 19 caveat-required file(s) carry every caveat their own rule demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
ARGV rc=0
```

### Suite

```
$ python3 -m pytest test_check_claims_152.py -q -o addopts=""
34 passed in 1.15s
```

### The final SUMMARY's argv scan

`152-20-SUMMARY.md` is scanned **after** it is written, via positional argv, with exactly:

```
cd /workspaces/.planning/phases/152-outward-facing-close-operator-gated
python3 152-check-claims.py 152-20-SUMMARY.md
```

Its pasted result is appended by Plan 152-20's output step, below.

### The final SUMMARY's argv scan — RESULT

Run after `152-20-SUMMARY.md` was written, exactly as specified above:

```
$ python3 152-check-claims.py 152-20-SUMMARY.md
PASS: scanned 152-20-SUMMARY.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule only -- see the module docstring's explicit non-claim, and note that a green run alone does not discharge D-03's per-artifact blocking operator wording review)
FINAL-ARGV rc=0
```

One iteration was needed: the first draft of `152-20-SUMMARY.md` used a reserved claim word bare
("argv path ... over the nineteen SUMMARY files") and the gate rejected it at line 149. The word was
requalified — the gate was not. That is the third time in this phase the gate has rejected a record
file written by the same agent that armed it, which is the only real evidence that it constrains its
author rather than only its subjects.
