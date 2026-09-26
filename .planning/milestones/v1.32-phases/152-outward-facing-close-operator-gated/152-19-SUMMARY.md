---
phase: 152-outward-facing-close-operator-gated
plan: 19
subsystem: outward-facing
tags: [honesty-ledger, claim-gate, out-05, live-capture, process-failure]

requires:
  - phase: 152-outward-facing-close-operator-gated
    provides: "152-11/12's beta merges and merge-record; 152-13's seven-target armed gate and fail-closed auto-chain guard; 152-14..18's five published artifacts and the content-based landed-identity oracle; 152-01's pre-populated _CAVEAT_RULES entry for 152-LEDGER.md"
provides:
  - "152-LEDGER.md — the v1.32 honesty ledger, ten sections, a 7-row four-column claim table with every non-claim cell non-empty, a 5-entry amendment register, and a newly-found process failure (an uncorrectable part-name misattribution live in a published body)"
  - "152-check-claims.py armed at eight real outward artifacts (previously seven), including the ledger itself"
  - "test_check_claims_152.py's arming leg strengthened to assert all eight basenames"
affects: [152-20]

tech-stack:
  added: []
  patterns:
    - "Arm the claim gate at the document that carries the pairing discipline itself, not only at the artifacts it governs — an unscanned internal ledger is the one most likely to state a claim generously"
    - "A part-name misattribution in an already-published body is recorded plainly in the ledger rather than silently left for a future reader, even though the published artifact itself cannot be edited"

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-LEDGER.md
  modified:
    - .planning/phases/152-outward-facing-close-operator-gated/152-check-claims.py
    - .planning/phases/152-outward-facing-close-operator-gated/test_check_claims_152.py

key-decisions:
  - "The meta repository's git status shows ' M firestarter_app' rather than clean, because git decodes the submodule's pre-existing untracked content as S..U. The gitlink SHA is bit-identical to firestarter_app's own HEAD, confirmed live. Reported exactly as measured rather than forced into 'clean' — the plan's own acceptance criterion literally asked for this to be empty, and it is not, for a reason recorded rather than argued away."
  - "A genuine, previously-uncaught defect was found while live-capturing the ledger's evidence: the published app release body (3.0.0b23) names the bench part behind this milestone's one exploratory lock-status probe as a W29C040, but 151-BENCH.md's own primary record shows the physically-seated part was a W29C020 — the true W29C040 leg never ran, no sample was available, and 151-BENCH.md explicitly warned against exactly this misattribution. The error traces back through 152-RESEARCH.md to 152-CONTEXT.md's own citation. It cannot be corrected in the already-published body under this phase's own prohibition against altering a published draft, so it is recorded plainly in the ledger's process-failures section instead. The milestone's core non-claim (no AT28C part tested) is unaffected — both W29C020 and W29C040 are outside the AT28C/0x0D family."
  - "The ledger's initial draft tripped the gate's FORBIDDEN_PATTERNS table row at 152-check-claims.py:303 twice, outside the mandated software-proven compound — once describing this plan's own Task 3 as still to come, once citing 153-RECORD.md's section title. Both were caught by the gate on the first env-seam run and reworded before commit (demonstrated / What was NOT established) rather than the lookbehind being widened."
  - "The plan's Task 2 acceptance criterion demands the 'No AT28C part was tested at any point in v1.32' sentence appear exactly once. The first draft carried it twice (a header restatement plus the closing trio); the header restatement was removed rather than the criterion reinterpreted."

patterns-established:
  - "Pattern: when a live re-derivation for one document (the ledger's evidence capture) surfaces a defect in a document from an earlier, already-completed plan, record the finding at the point of discovery rather than deferring it — even when the artifact carrying the defect can no longer be edited."

requirements-completed: [OUT-05]

duration: ~50min
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 19: Write the Honesty Ledger, Arm the Gate at It

**Status: complete.** `152-LEDGER.md` written and gate-clean; `152-check-claims.py` extended from
seven to eight `_DEFAULT_TARGETS` entries; the gate demonstrated green over all eight, including the
ledger itself. No network write of any kind was performed in this plan.

This ships software-proven and unvalidated on silicon.

## Task 1 — Live capture, reproduced verbatim

Every value below was captured live by this plan (`2026-08-21T18:40:57Z` unless noted), never reused
from a prior document's citation.

**Three repository HEADs and two published-branch SHAs:**

```
/workspaces HEAD                2f194e29d62ebf0ef879e353f78d6afd381a2a9c
/workspaces/firestarter HEAD    d990a4ce80fcb56c9becf2312d1fe8757e1fc54d
/workspaces/firestarter_app HEAD a0bfd5e8b32989a60fc93b94e7b102506e6cf56f
firestarter origin/beta         88d204a5a023bcad6f708b33150502ba90fdec2b
firestarter_app origin/beta     86f85d77d8102b633da82aef4b5601947f6cc80b
```

**No divergence found** against `152-MERGE-RECORD.md` or `152-11-SUMMARY.md`'s own citations of the
same values — three independent readings across two plans and this one agree exactly.

**Both cut tags, re-read from the release list, body lengths non-zero:**

```
firestarter       3.0.0b20   2026-08-21T17:07:09Z   body length 9122
firestarter_app   3.0.0b23   2026-08-21T17:06:43Z   body length 9261
```

**Three comment ids/URLs plus gh#32's closure, re-read live from the issues themselves:**

```
gh#12  OPEN   11 comments  IC_kwDOSX4ER88AAAABQEgwAQ  2026-08-21T18:00:19Z
gh#21  OPEN    3 comments  IC_kwDOSX4ER88AAAABQEyGMg  2026-08-21T18:27:49Z
gh#11  OPEN   19 comments  IC_kwDOSX4ER88AAAABQE07QQ  2026-08-21T18:32:30Z
gh#32  CLOSED (stateReason COMPLETED, closedAt 2026-08-08T09:31:09Z)  1 comment
```

**Every gate and suite, run live, each with its own count and exit code:**

```
152-check-claims.py (7 armed defaults, pre-extension)     rc=0
test_check_claims_152.py                                  34 passed
152-check-not-auto.py                                      rc=0 ('_auto_chain_active' explicitly False)
../130-*/check_record_corrections.py (300s timeout)        rc=0, tally {block:23, line-label:4,
                                                            inline-history:6, inline-allow:10,
                                                            superseded:12}
firestarter/scripts/check_erase_no_vpp.py                  rc=0
```

**`git status --porcelain`, all three repos:**

```
firestarter        (empty, ignoring untracked)
firestarter_app     (empty, ignoring untracked)
meta (/workspaces)  M firestarter_app
```

The meta line is **not** the clean result the other two repos gave, and is reported exactly as
measured. `git status --porcelain=2 -- firestarter_app` decodes the flag as `S..U` — the submodule's
tracked gitlink SHA is bit-identical to `firestarter_app`'s own HEAD (confirmed above), and the `M` is
git's own convention for an **untracked-content** submodule, not a moved gitlink. The untracked
content is the same pre-existing set `152-11-SUMMARY.md` already recorded
(`.planning/config.json`, `SECURITY.md`, four datasheet PDFs, `write_test_port.sh`), untouched by any
plan in this phase.

## Task 2 — `152-LEDGER.md` written, ten sections, gate-clean

The ledger's ten sections, in the order the plan specifies: the header with live captures; the claim
key (`PERMITTED`/`CONTEXT-ONLY`/`FORBIDDEN`, unchanged from the donor); the Oracle block (the five
gates/suites above, all green); the Evidence ceiling (quoted verbatim from `PROJECT.md` §"Current
Milestone: v1.32"); the four-column claim table; the amendment register; negative space; process
failures; what no test/gate/review can close; and the cross-reference "Composes with" block, closed
with the porcelain statement.

**The claim table has 7 rows, and every fourth cell ("Explicitly does NOT prove") is non-empty** —
verified row by row before commit:

1. Write-path blank-check removal
2. Standalone erase step (software six-byte path) and its `AT28C_TEC_MAX_MS` (20 ms) timing constant
3. Protection-read command (`lock-status`), refusal-first
4. Report-provenance fix
5. Numeric database values
6. Page-size seam, with its explicit no-behaviour-change consequence for the AT28C256 part named in
   the community threads
7. The deferred deliberate-protection command's withdrawal

**The amendment register carries 5 entries**, one per amendment landed in Plans 152-03/152-04, each
naming its dated marker: the criterion-2 amendment (D-05), the criterion-5 narrowing (D-11), the four
`REQUIREMENTS.md` OUT-bullet amendments (D-05/D-11), the two stale-record-count sites (D-15), and the
disproven-premise correction (D-06/D-15).

**A genuine finding surfaced while live-capturing evidence for claim-table row 3**, recorded in the
ledger's process-failures section rather than left uncaught: the published app release body
(`3.0.0b23`) names the bench part behind this milestone's one exploratory `lock-status` probe as a
W29C040. Re-measured live against `151-BENCH.md`'s primary record, the physically-seated part for that
probe (Leg B) was a **W29C020** — the true W29C040 leg (Leg C) never ran, no sample was available, and
`151-BENCH.md`'s own text explicitly warns against reporting a W29C020 reading under the W29C040 name.
The mislabel traces back through `152-RESEARCH.md` to `152-CONTEXT.md`'s own citation of "the W29C040
probe result" for the same Leg B data. It passed the claim gate (a part-number identity error is not a
forbidden phrase) and the D-03 wording-review delegation (the operator did not read the body). It
cannot be corrected in the already-published body under this phase's own prohibition against altering
a published draft, so it is recorded plainly instead. The milestone's core non-claim — no AT28C part
was tested — is unaffected: both W29C020 and W29C040 sit outside the AT28C/`0x0D` family this milestone
is about.

**Two gate-iteration fixes, before commit:** the first draft tripped the gate's `FORBIDDEN_PATTERNS`
table row at `152-check-claims.py:303` twice, outside the mandated `software-proven` compound (once
describing this plan's own remaining work, once citing a sibling document's section title) — both
reworded ("demonstrated" / "What was NOT established") and re-verified green. The first draft also repeated the "No AT28C part was tested at any point in v1.32"
sentence twice against the plan's own `== 1` acceptance criterion — the header's restatement was
removed, the closing trio kept.

**Final verification, all green:**

```
test -s 152-LEDGER.md                                            rc=0
grep -c 'Explicitly does NOT prove' 152-LEDGER.md                1
grep -c 'measured here' 152-LEDGER.md                             3
grep -c 'No AT28C part was tested at any point in v1.32'          1
grep -c 'software-proven and unvalidated on silicon'               1
grep -c 'AMENDED 2026-08-21'                                       5
FIRESTARTER_CLAIMSCAN_TARGETS_152=<abs>/152-LEDGER.md python3 152-check-claims.py
PASS: scanned 152-LEDGER.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands;
0 file(s) carry no caveat requirement (...)
rc=0
```

## Task 3 — the ledger armed as an eighth gate target

Exactly one line added to `_DEFAULT_TARGETS` (`os.path.join(_HERE, "152-LEDGER.md")`), bringing the
list to eight. `_CAVEAT_RULES` needed no edit — its entry for `152-LEDGER.md` was pre-populated in Plan
152-01 with all three caveat labels. The arming leg's literal membership set was extended from seven to
eight expected basenames, with the `len(...) == 8` check bumped accordingly.

**Final verification, untruncated, all green:**

```
$ python3 152-check-claims.py
PASS: scanned 152-CLAIM-CLASSES.md, 152-GH12-COMMENT.md, 152-GH21-COMMENT.md, 152-GH11-COMMENT.md,
152-RELEASE-NOTES-app.md, 152-RELEASE-NOTES-fw.md, 152-MERGE-RECORD.md, 152-LEDGER.md; 7 of 7
caveat-required file(s) carry every caveat their own rule demands; 1 file(s) carry no caveat
requirement (this PASS is compliance with the forbidden-phrase table and the per-file caveat rule
only -- see the module docstring's explicit non-claim, and note that a green run alone does not
discharge D-03's per-artifact blocking operator wording review)
GATE rc=0

$ python3 -c "... len(m._DEFAULT_TARGETS) ..."
n= 8
152-CLAIM-CLASSES.md True
152-GH12-COMMENT.md True
152-GH21-COMMENT.md True
152-GH11-COMMENT.md True
152-RELEASE-NOTES-app.md True
152-RELEASE-NOTES-fw.md True
152-MERGE-RECORD.md True
152-LEDGER.md True

$ python3 -m pytest test_check_claims_152.py -q -o addopts=""
..................................                                       [100%]
34 passed in 1.10s
SUITE rc=0

$ git -C /workspaces rev-parse --abbrev-ref HEAD
gsd/v1.32-at28c-write-path-root-cause-report-provenance
```

No `152-NN-SUMMARY.md` was added to `_DEFAULT_TARGETS` — confirmed by introspection (`[]`). That
extension is Plan 152-20's job.

## Task Commits

1. **Tasks 1+2: write `152-LEDGER.md`** — `ce342e35` (docs) — `152-LEDGER.md`
2. **Task 3: extend `_DEFAULT_TARGETS` to eight, strengthen the arming leg** — `b40eaa54` (feat) —
   `152-check-claims.py`, `test_check_claims_152.py`

## Files Created/Modified

- `.planning/phases/152-outward-facing-close-operator-gated/152-LEDGER.md` — new; the v1.32 honesty
  ledger.
- `.planning/phases/152-outward-facing-close-operator-gated/152-check-claims.py` —
  `_DEFAULT_TARGETS` extended from 7 to 8 entries; no `_CAVEAT_RULES` edit needed.
- `.planning/phases/152-outward-facing-close-operator-gated/test_check_claims_152.py` — arming leg's
  literal membership set extended to eight basenames; `len(...) == 8`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The ledger's first draft tripped the gate's `FORBIDDEN_PATTERNS` table row at `152-check-claims.py:303`, twice**
- **Found during:** Task 2's own gate run before commit.
- **Issue:** Two sentences used the row's bare, unqualified target word outside the mandated
  `software-`-prefixed compound — describing this plan's own remaining work, and citing a sibling
  document's section title.
- **Fix:** Reworded both ("demonstrated"; "What was NOT established", matching `153-RECORD.md`'s own
  actual section heading rather than a paraphrase).
- **Files modified:** `152-LEDGER.md` (pre-commit).
- **Verification:** re-ran the env-seam gate; rc=0.
- **Committed in:** `ce342e35`.

**2. [Rule 3 - Blocking] The ledger's first draft repeated a mandated caveat sentence twice against the plan's own `== 1` criterion**
- **Found during:** Task 2's own acceptance-criteria check before commit.
- **Issue:** "No AT28C part was tested at any point in v1.32" appeared in both a header restatement and
  the closing trio; the plan's acceptance criterion requires exactly one occurrence.
- **Fix:** Removed the header restatement, kept the closing trio (matching the donor convention of
  stating the milestone-level non-claim once, at the close).
- **Files modified:** `152-LEDGER.md` (pre-commit).
- **Verification:** re-ran the grep count; 1. Re-ran the env-seam gate; rc=0.
- **Committed in:** `ce342e35`.

---

**Total deviations:** 2 auto-fixed (both gate-iteration corrections caught before their commit).
**Impact on plan:** Neither affects any claim's substance; both are wording-mechanics corrections. No
scope creep.

## Issues Encountered

None beyond the two gate-iteration fixes above and the part-name misattribution finding, which is a
discovery this plan's own live-capture work surfaced and recorded, not a defect in this plan's own
output.

## User Setup Required

None. No network write of any kind was performed in this plan — no `gh issue comment`, no
`gh release edit`, no `gh pr` call.

## Next Phase Readiness

- `152-LEDGER.md` exists, is gate-clean, and is itself a hard-coded gate target — the pairing
  discipline it carries is now enforced on itself, per D-12's own reasoning.
- Plan 152-20 owns: extending `_DEFAULT_TARGETS` over the phase's own `152-NN-SUMMARY.md` files (with
  the last one scanned via positional argv, per this file's own governing rule); flipping the five
  requirement checkboxes on named evidence; merging the meta repository to `beta`; and completing the
  handoff `152-MERGE-RECORD.md` describes.
- The part-name misattribution finding (W29C040 vs the actually-probed W29C020) is now recorded in the
  ledger; it cannot be corrected in the already-published `3.0.0b23` body and is not this plan's, or
  any remaining plan's, work to fix — a future release's notes are the earliest place it could be
  corrected, and this ledger states that plainly rather than implying otherwise.

This ships software-proven and unvalidated on silicon.

## Self-Check: PASSED

- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-LEDGER.md`
- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-check-claims.py`
- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/test_check_claims_152.py`
- FOUND commit: `ce342e35`
- FOUND commit: `b40eaa54`
- Gate re-run against this SUMMARY (via the env seam) exits 0, after two gate-iteration fixes
  (citing the FORBIDDEN_PATTERNS row by table location rather than by label, since the label's own
  name contains the word it forbids).

---
*Phase: 152-outward-facing-close-operator-gated*
*Completed: 2026-08-21*
