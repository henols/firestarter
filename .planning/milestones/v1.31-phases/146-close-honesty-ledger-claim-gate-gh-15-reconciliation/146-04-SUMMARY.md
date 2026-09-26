---
phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation
plan: 04
subsystem: planning-gates
tags: [claim-gate, fixtures, pytest, close-01, d-12, anti-hollow, fail-closed]
requires:
  - "146-check-claims.py (plan 146-01) — the gate under test, byte-unchanged by this plan"
  - ".planning/phases/137-…/test_check_permitted_claims_v130.py — the 11-leg donor suite"
  - ".planning/phases/137-…/fixtures/ — donor LAYOUT only; all five donor bodies are unusable here"
provides:
  - "fixtures/ — five probed fixtures: two clean controls, two single-reason forbidden plants, one single-reason caveat plant"
  - "test_check_claims_v131.py — the fifteen-leg subprocess-driven suite (D-12's FIRST proof of CLOSE-01)"
  - "146-CITATIONS.md §3 — the run transcript: five probe results, both suite runs, four selector counts, leg 9's RED verbatim"
  - "leg 9 (test_armed_against_the_five_real_closing_artifacts) — pre-authored, observed RED for its named reason, handed to plan 146-11 for its GREEN"
affects:
  - "plan 146-11 — inherits leg 9 and owns both its GREEN and D-12's second proof (the real-file plant-and-revert, §4)"
  - "plan 146-13 — may tick CLOSE-01 only after 146-11; this plan deliberately ticks nothing"
tech-stack:
  added: []
  patterns:
    - "subprocess-driven negative fixtures (anti-hollow): behavioural legs invoke the gate as a real process; only introspection legs import by file path"
    - "probe-before-assert: every plant's label set measured with the gate's own scan_text before the assertion naming it was written"
    - "single-reason plants: each planted fixture fails for exactly one reason, and each leg asserts the OTHER bucket is absent"
    - "cite-by-label-id / cite-by-file:line: forbidden phrases are never reproduced in the record that documents them"
    - "re-scan after every prose insertion rather than reasoning about inertness"
key-files:
  created:
    - ".planning/phases/146-…/fixtures/clean_control.md"
    - ".planning/phases/146-…/fixtures/clean_control_second.md"
    - ".planning/phases/146-…/fixtures/planted_forbidden_claim.md"
    - ".planning/phases/146-…/fixtures/planted_proven_unqualified.md"
    - ".planning/phases/146-…/fixtures/planted_missing_caveat.md"
    - ".planning/phases/146-…/test_check_claims_v131.py"
  modified:
    - ".planning/phases/146-…/146-CITATIONS.md (§3 appended; 210 insertions, 0 deletions)"
decisions:
  - "Leg 2's plant uses the confirmed-working label, the choice 146-PATTERNS.md:318 already probed, rather than the milestone's headline phrase — the headline phrase would have had to be reproduced in the suite, in the register and in two commit messages to be asserted"
  - "planted_missing_caveat.md omits exactly ONE caveat (the narrowing one) and keeps the voltage figure, so its leg names one label rather than two and cannot be satisfied by a fixture that lost both"
  - "Legs 14/15 build their input by FILTERING the already-probed plant fixture instead of writing a fresh forbidden literal into the suite source"
  - "The register's own header (:9-11) misattributes §3 to plan 146-02; per the register's stated discipline the earlier text was left alone and the divergence recorded inside §3"
metrics:
  duration: "~40 min"
  completed: 2026-08-17
  tasks: 2
  commits: "6 -- 28340b37 (fixtures), 302cb63d (suite + citations 3), 27b74179 (summary), 09969f85 (state + roadmap), 69a8b866 (ahead-count correction), and this metrics correction; the first draft of this field said 3, counting only the task commits and the summary"
  legs_authored: 15
  legs_green: 14
  legs_red_by_design: 1
status: complete
---

# Phase 146 Plan 04: Claim-Gate Fixture Suite Summary

Fifteen-leg subprocess-driven suite over five probed fixtures: every forbidden pattern leg, both caveat
labels, the D-11 per-file exemption in both directions, the fail-closed branch, the never-vacuous branch and
the argv/env precedence each seen to fire on a document authored to make it fire — with the one
pre-authored armed-against-the-real-files leg observed RED for its **named** reason, not for a collection
error.

## What Was Built

| # | Artifact | Commit |
|---|---|---|
| 1 | `fixtures/` — five files, 850–1032 B, 11–14 lines, each self-labelled on line 1 | `28340b37` |
| 2 | `test_check_claims_v131.py` — 15 legs, 11 behavioural + 4 introspection | `302cb63d` |
| 3 | `146-CITATIONS.md` §3 — the full transcript | `302cb63d` |

`146-check-claims.py` is **byte-unchanged**: `git diff --numstat -- 146-check-claims.py` produced no output
after both tasks. No leg was made to pass by editing the gate, and D-14's pattern table was not touched.

## The Five Probe Results, Verbatim

Recorded **before** a single assertion was written, by importing the gate by file path and calling its own
`scan_text` under the full caveat set. `full caveat labels: ['ceiling-narrowing', 'ceiling-voltage']`.

```
--- clean_control.md
  forbidden_hits = []
  missing_caveats = []
  required_caveats_for(basename) = ['ceiling-narrowing', 'ceiling-voltage']
--- clean_control_second.md
  forbidden_hits = []
  missing_caveats = []
  required_caveats_for(basename) = ['ceiling-narrowing', 'ceiling-voltage']
--- planted_forbidden_claim.md
  forbidden_hits = [('confirmed-working', <matched text>, 14)]
  missing_caveats = []
  required_caveats_for(basename) = ['ceiling-narrowing', 'ceiling-voltage']
--- planted_missing_caveat.md
  forbidden_hits = []
  missing_caveats = ['ceiling-narrowing']
  required_caveats_for(basename) = ['ceiling-narrowing', 'ceiling-voltage']
--- planted_proven_unqualified.md
  forbidden_hits = [(<pattern 10 label>, <matched text>, 12)]
  missing_caveats = []
  required_caveats_for(basename) = ['ceiling-narrowing', 'ceiling-voltage']
```

The `matched text` field and pattern 10's label id are elided **here and only here**, and cited instead as
`fixtures/planted_forbidden_claim.md:14`, `fixtures/planted_proven_unqualified.md:12` and
`test_check_claims_v131.py:242`. This is not squeamishness: this plan's own warning fired twice during
execution (see Deviations), and a SUMMARY that reproduces the phrases it documents is a new copy of them.
The label ids as the gate prints them are in the suite's assertions, where they are load-bearing.

**Four properties the probes establish, none of them assumed:**

1. Both clean controls return `[]` for forbidden hits **and** `[]` for missing caveats. A control missing a
   caveat would have made leg 1 red for the wrong reason and its green meaningless.
2. Both forbidden plants return exactly **one** hit and **zero** missing caveats — single-reason failures.
3. The caveat plant returns **zero** forbidden hits and exactly **one** missing label.
4. `required_caveats_for()` resolved every fixture basename to the **full** set, so the gate's fail-closed
   default was exercised incidentally by the probe itself, before leg 13 asserted it.

**The probe-before-assert rule earned its keep on fixture 5.** `planted_proven_unqualified.md`'s own line-2
comment cites pattern 10 in regex form. Had that citation form matched, the fixture would have returned two
hits and any leg asserting "one hit at line 12" would have been red for a reason unrelated to the gate. The
probe returned one hit, at line 12 — the regex form is inert, which was then reused as the safe citation
form throughout §3.

## The Fifteen Legs

| # | Test | Kind | Asserts |
|---|---|---|---|
| 1 | `test_gate_exits_zero_on_the_clean_control` | subprocess | exit 0, `PASS:` |
| 2 | `test_planted_overclaim_flips_the_gate_to_failure` | subprocess | non-zero, `FAIL:`, the **probed** `confirmed-working` label, **no** caveat bucket |
| 3 | `test_planted_missing_caveat_flips_the_gate_to_failure` | subprocess | non-zero, the gate's real caveat bucket string, the one absent label, **no** forbidden bucket |
| 4 | `test_planted_bare_claim_word_flips_the_gate_to_failure` | subprocess | non-zero, the **probed** pattern-10 label, **no** caveat bucket |
| 5 | `test_fail_closed_on_a_nonexistent_scan_target` | subprocess | non-zero, `not found on disk`, **and the absent path named** |
| 6 | `test_never_vacuous_on_an_explicitly_empty_target_list` | subprocess | non-zero, never-vacuous message, `PASS:` absent, `UNARMED:` absent |
| 7 | `test_pass_line_names_every_scanned_file` | subprocess | exit 0 and both basenames **on the one PASS line** |
| 8 | `test_positional_argv_precedence_beats_the_env_seam` | subprocess | exit 0, and the seam's plant never scanned at all |
| 9 | `test_armed_against_the_five_real_closing_artifacts` | subprocess | exit 0 + all five real basenames — **RED by design today** |
| 10 | `test_default_targets_resolve_inside_this_phase_directory` | introspection | every default target's dirname is this phase dir |
| 11 | `test_default_targets_basenames_carry_this_phases_prefix` | introspection | every basename starts `146-` |
| 12 | `test_every_default_targets_basename_has_a_caveat_rule_entry` | introspection | every basename is a `_CAVEAT_RULES` key |
| 13 | `test_unrecognised_basename_resolves_to_the_full_caveat_set` | introspection | three unknown basenames → the FULL set; the set is derived, not restated |
| 14 | `test_caveat_exempt_basename_passes_without_either_caveat` | subprocess | the exempt basename with **neither** caveat exits 0 |
| 15 | `test_caveat_exempt_basename_still_fails_on_a_forbidden_phrase` | subprocess | same basename + forbidden phrase → non-zero, and still **no** caveat demanded |

`grep -c '^def test_'` → **15**. Seam references (`FIRESTARTER_CLAIMSCAN_TARGETS_146`) → **6**. Donor seam
names (`TARGETS_V130` / `TARGETS_V131`) → **0**, so this suite cannot aim at Phase 139's live gate in this
same milestone.

**Three legs go beyond the donor's shape**, each for a measured reason:

- **Leg 4 replaces the donor's relational-rule leg.** This gate has no relational rule, no proximity window
  and no exclusion mechanism (D-14), so the donor's `self-verifying` label and its v1.30 caveat-bucket
  string were **not** copied: an assertion against a string the gate never emits is a leg that can only
  ever be red.
- **Legs 14 and 15 are a pair, and neither is sufficient alone.** Leg 14 alone (exempt basename passes
  without a caveat) is equally consistent with the gate *skipping* the exempt file entirely. Leg 15 closes
  that: the same basename with a forbidden phrase still exits non-zero, and no caveat is demanded of it.
  Together they say the D-11 exemption is caveat-only.
- **Legs 2, 3 and 4 each assert the absence of the other bucket.** A plant that quietly lost a caveat would
  still exit non-zero and would still satisfy a weaker leg; the negative assertion is what keeps each plant
  single-reason over time.

## Both Suite Runs

**Full suite** — `python3 -m pytest …/test_check_claims_v131.py -o addopts="" -q`, `rc=1`:

```
1 failed, 14 passed in 0.41s
FAILED …/test_check_claims_v131.py::test_armed_against_the_five_real_closing_artifacts
```

**Suite minus leg 9** — same command with `--deselect …::test_armed_against_the_five_real_closing_artifacts`,
`rc=0`:

```
..............                                                           [100%]
14 passed, 1 deselected in 0.38s
```

The second run is what makes the first attributable. Without it, `rc=1` is consistent with any number of
broken legs. The deselection lives **only** in the transcript: the suite file carries no `xfail`, no `skip`
and no deselection of its own, because a leg marked expected-to-fail in the file is a leg nobody looks at
again.

## Leg 9's RED — Verified, Not Assumed

`python3 -m pytest …::test_armed_against_the_five_real_closing_artifacts -o addopts="" -q`, `rc=1`:

```
E       AssertionError: gate exited 1 against the five real default targets -- expected PASS + exit 0. If
        the output below reports the five closing artifacts as 'not found on disk', this is the EXPECTED
        pre-146-11 red and the arming contract is intact; any other message is a defect in this suite.
E         stdout:
E         FAIL: scan target(s) not found on disk -- the gate cannot vacuously pass with a target silently
        skipped: ['/workspaces/.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-LEDGER.md',
        '…/146-CORRECTIONS.md', '…/146-GH15-RECONCILIATION.md', '…/146-RELEASE-NOTES-fw.md',
        '…/146-RELEASE-NOTES-app.md']
E
E         stderr:
E
E       assert 1 == 0
…/test_check_claims_v131.py:406: AssertionError
```

**Which of the two reds this is.** The plan required stating explicitly whether the observed red is the
expected one or a defect. It is **the expected one**: the failure is the gate's own fail-closed
missing-target branch, naming **all five** closing artifacts by absolute path. It is specifically not a
collection error, not an import error of a filename that is no valid Python identifier, not a missing
fixture, not a wrong basename and not a seam-name typo — each of which produces a different first line.
The distinction was made by **reading the failure text**, and it was cross-checked independently: running
the gate directly with no argv and no env (`python3 146-check-claims.py`, `rc=1`) prints the same
five-path fail-closed line, so the red originates in the gate's arming contract and not in the harness.

**Leg 9's GREEN belongs to plan 146-11, and its second RED comes free from that plan's plant.** 146-11
authors the five artifacts, at which point this leg goes green with no edit to the suite; its
plant-and-revert then drives the same gate red a second time against a real tracked file. Nothing in this
plan may be read as leg 9 having passed.

## The Four Validation-Map Selectors

`146-VALIDATION.md:62-65` grades CLOSE-01 through four `-k` expressions. A selector collecting **zero**
tests exits 0 and would make its row a silent pass, so each was run with `--collect-only` and the collected
**names** read, not merely counted.

| `-k` expression | Collects | Legs reached |
|---|---|---|
| `planted` | **3** | 2, 3, 4 |
| `caveat` | **5** | 3, 12, 13, 14, 15 |
| `closed or vacuous or precedence` | **3** | 5, 6, 8 |
| `default_targets` | **3** | 10, 11, 12 |

All four match the plan's intended leg sets exactly, and none reaches leg 9 — so all four rows are green
today and stay green through 146-11. Leg 9's name deliberately contains none of the four substrings: note
"clos**ing**", not "clos**ed**". `146-VALIDATION.md:66`'s integration row, which invokes the gate directly,
remains the only row grading the armed run.

## Fixtures Are Unreachable From the Gate

| Assertion | Result |
|---|---|
| No fixture basename in a default-mode gate run | **0 of 5** — the default list is an explicit five-element list of `146-`-prefixed artifacts, reachable by no wildcard |
| No fixture gitignored (`git check-ignore -v`) | no match for any of the five; all five tracked at `28340b37` |
| Every fixture self-labelled on line 1 | 5 of 5, each also stating "never add to `_DEFAULT_TARGETS`" |
| Each planted fixture carries a second comment | 3 of 3, each naming its label **and** its single failure reason |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] §3's own warning table planted the phrase it warned about**
- **Found during:** Task 2, on the mandatory re-scan after the prose insertion
- **Issue:** `146-CITATIONS.md` §3.0 was drafted with pattern 10's label id spelled out in a table row
  explaining that that spelling is unsafe. Re-scanning the register found **1** forbidden hit — the warning
  row itself. The register had measured **0** before §3 was appended.
- **Fix:** the row now cites the suite line (`test_check_claims_v131.py:242`) instead of spelling the id,
  and the incident is recorded in §3.0 and in §3.7's middle column rather than smoothed away.
- **Files modified:** `146-CITATIONS.md`
- **Commit:** `302cb63d`
- **Re-measured:** register back to **0** hits.

**2. [Rule 1 — Bug] Two of the suite's own docstring lines reproduced forbidden literals**
- **Found during:** Task 2, on the same re-scan discipline applied to the suite file
- **Issue:** the suite measured **4** hits: two were load-bearing assertion literals, but two were this
  plan's own prose — a recorded plant candidate quoted verbatim in the module docstring, and the word
  pattern 10 forbids used casually in the leg-14 coverage line.
- **Fix:** the quoted candidate is now cited as `146-PATTERNS.md:357`; the casual use was reworded. The
  suite is down to **2** hits, both at `:242` and `:253`, both the label literal the gate itself prints
  inside its bucket line, both required by the assertions.
- **Files modified:** `test_check_claims_v131.py`
- **Commit:** `302cb63d`

**3. [Rule 3 — Recorded divergence, no file edited] The register misattributes §3's ownership**
- **Found during:** Task 2, reading `146-CITATIONS.md:9-11` before appending
- **Issue:** the register's header says §3 is owed by plan `146-02`. It is not — `146-02` owns the ARM build
  record, and `146-04-PLAN.md` instructs this plan to append §3.
- **Fix:** none applied to the header. Per the register's own stated discipline ("the divergence is stated
  here and the earlier document is left alone"), the divergence is recorded inside §3 and §§0-2 were left
  byte-untouched. `git diff --numstat` on the register: **210 insertions, 0 deletions**.
- **Files modified:** none beyond the §3 append.

Neither the gate nor any fixture was changed to make a leg pass. No pattern-table change was made (D-14).

## Not Discharged By This Plan

- **CLOSE-01 is NOT ticked**, in `REQUIREMENTS.md` or in ROADMAP's coverage table. D-12 requires two
  different proofs and this plan owns only the first: fixtures prove the pattern table, not that the gate is
  wired to the files that ship. Plan 146-11 owns the second proof; plan 146-13 is the only plan permitted to
  tick CLOSE-01 through CLOSE-05.
- **Leg 9 has not passed.** It is authored, and observed red for a verified reason.
- **A green run of this suite is compliance with the pattern table and the per-file caveat rules only.** It
  cannot detect an implied overclaim, a misleading omission, a wrong tone, or a true statement placed where
  it misleads — that is plan 146-12's blocking operator wording review.
- **No push, merge, tag, release or workflow dispatch** was performed (D-01). Meta upstream-ahead moved
  243 → 247 (four commits: two task commits, the summary, the state record); both sub-repos untouched (`firestarter` porcelain **0**, `firestarter_app` porcelain **7**, the
  pre-existing dirt, both unchanged from the wave-1 baseline).

## Known Stubs

None. Leg 9 is a pre-authored assertion, not a stub: it exercises the gate end-to-end today and reports a
real, named failure. Its expected transition to green is recorded in the leg's own docstring, in
`146-CITATIONS.md` §3.4 and above, and it is assigned to plan 146-11.

## Self-Check: PASSED

| Claim | Verification | Result |
|---|---|---|
| five fixtures exist | `ls fixtures/*.md \| wc -l` | 5 |
| suite exists with 15 legs | `grep -c '^def test_'` | 15 |
| `146-CITATIONS.md` §3 present, §§0-2 intact | `grep -qF '## 3.'` + `## 0./1./2.` | all four present |
| commit `28340b37` exists | `git log --oneline --all \| grep -q 28340b37` | FOUND |
| commit `302cb63d` exists | `git log --oneline --all \| grep -q 302cb63d` | FOUND |
| gate byte-unchanged | `git diff --numstat -- 146-check-claims.py` | no output |
| 14 legs green, 1 red by design | two pytest runs | `rc=1` full / `rc=0` minus leg 9 |
| sub-repos untouched | `git -C firestarter status --porcelain \| wc -l` / same for app | 0 / 7 |
