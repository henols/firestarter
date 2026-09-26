# Phase 146: Close — Honesty Ledger, Claim Gate & gh#15 Reconciliation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-17
**Phase:** 146-close-honesty-ledger-claim-gate-gh-15-reconciliation
**Areas discussed:** Publication boundary, CLOSE-04's real scope, gh#15's outward act, Claim-gate arming surface

**Area selection.** Four gray areas were presented; the operator selected **all four**. Areas
deliberately *not* presented, because prior phases or house precedent already settle them: the
honesty ledger's structural shape (122/130/137 are three prior instances), the claim gate's core
mechanics (`139-check-claims.py` already carries this milestone's vocabulary and its own
cross-phase-copy self-check), the hand-written-release-notes-behind-an-operator-wording-review rule
(v1.22 D-08/D-16, v1.23 D-02), the no-`--auto`/`--chain` rule, the premature-requirement-tick guard,
and 130 D-10's rule that negative space covers deferrals *and* residuals.

---

## Publication boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Draft only — no push | Release bodies as committed drafts behind the wording review; merge/cut/PyPI belong to `/gsd-complete-milestone`. Matches the requirement text literally and avoids the auto-fire-a-spurious-beta trap. | ✓ |
| Draft + merge to beta via PR | v1.30's shape (PR #44 → squash-merged). Lands the fix on beta in-phase; makes 146 outward-facing, adds a PR round-trip, and the squash leaves `--is-ancestor` a permanent false negative. | |
| Full v1.23-style cut | Merge, CI cut, manual `publish.yml` dispatch for PyPI, both channels verified. Most complete; nothing in CLOSE-01…05 asks for it. | |

**User's choice:** Draft only — no push.
**Notes:** CLOSE-01…CLOSE-05 name no push, merge or cut anywhere; CLOSE-05 asks only that release notes *describe* the change. This is the sharpest divergence from v1.23's close, where the beta push *was* CLOSE-04's literal text. → **D-01**

---

| Option | Description | Selected |
|--------|-------------|----------|
| Version-agnostic drafts | Explicit placeholder instead of any `3.0.0bNN` literal; the observed tag is filled at cut time from `gh release list`. | ✓ |
| Name the predicted next beta | Read the tag ceiling and write the next literal in. Reads as finished; bakes a computed tag into an outward-facing body, which v1.23 constraint 5 forbids. | |
| Anchor to the milestone, not the tag | Title by milestone name, never mention a beta number. Simplest; a release body that cannot identify itself reads oddly. | |

**User's choice:** Version-agnostic drafts.
**Notes:** Both repos' CI auto-increments from a git-tag scan on push to `beta`, so the real tag is only knowable after the cut. A body drafted here cannot be wrong about a tag it never saw. → **D-02**

---

| Option | Description | Selected |
|--------|-------------|----------|
| Ledger rows only | Negative-space rows in `146-LEDGER.md` citing `145-BENCH-LOG.md`; no new backlog stubs, no STATE.md block. Six of eight already have a home in `REQUIREMENTS.md` §Future Requirements or BENCH-02's disposition records. | ✓ |
| Ledger rows + file the genuinely homeless ones | Same, plus new stubs for items with no FUT-* and no backlog id. Nothing can fall out; extra triage onto a backlog already at 999.31. | |
| Ledger rows + a residuals block in STATE.md | More discoverable at `/gsd-new-milestone` time; a third place the same facts live. | |

**User's choice:** Ledger rows only.
**Notes:** Phase 145 closed with 12 carry-forwards, 10 of them literally `no v1.31 owner`. 999.30 and 999.31 are already filed. Precedent is 130 D-10. → **D-03**

---

## CLOSE-04's real scope

| Option | Description | Selected |
|--------|-------------|----------|
| Take all six, in a correction register | Discharge the queue: 143 D-01's roadmap prose, the sequencing-spine sentence, C3/H3's unclamped `extract_long`, F-140-05, F-140-07, F-141-07, F-144-01. Four prior phases named 146 as owner in writing. | ✓ |
| gh#15's nine boxes only | Read CLOSE-04 literally, re-file the rest as backlog. Smallest scope; hands forward corrections four phases already declined to make on the grounds that 146 would. | |
| Take the planning-record half only | Roadmap/PROJECT prose, F-140-05, F-140-07, F-144-01 here; the two source-text items re-filed. Keeps 146 out of a sub-repo edit entirely. | |

**User's choice:** Take all six, in a correction register.
**Notes:** Surfaced during the question that the queue is actually **seven**, not six — 141's H4 (the honest energy-cap ceiling: exactly 50 ms on shipped widths, worst case **99998 µs**) is also routed here. Also surfaced that **F-140-07 is an error in the *posted* gh#15 comment** — the TI TMS 2516 datasheet gives total programming time as 100 seconds, not 50 ms; 50 ms is the per-location `t_w(PR)`. → **D-04**

---

| Option | Description | Selected |
|--------|-------------|----------|
| Wording only — no behavior change | F-141-07 fixed via the three-copy `messages.toml` + regen; `MSG_INFO_RETRIES`'s orphan status recorded; C3/H3's unclamped `extract_long` **recorded, not clamped**. | ✓ |
| Record everything, edit nothing | Purely docs-and-claims; the bench-validated image is provably the one that ships. Leaves a shipped debug message describing the deleted adaptive loop. | |
| Wording + clamp the wire field | Also clamps `extract_long`. Closes a reachable-today gap; a behaviour change landing after the bench evidence was taken, pre-empting a decision 999.31 owns. | |

**User's choice:** Wording only — no behavior change.
**Notes:** `messages.h` is codegen-generated and **ID-only**, so a wording-only change produces a zero diff there; the real diff is the three `messages.toml` copies plus `firestarter_app/firestarter/messages.py`. → **D-06**

---

| Option | Description | Selected |
|--------|-------------|----------|
| Correction blocks + a 146 register | Labelled `⚠ CORRECTION` blocks at each false statement's own site, plus `146-CORRECTIONS.md` indexing all seven with origin finding, false text, corrected text, owning file. | ✓ |
| Correction blocks only, no register | Matches v1.23 D-05 exactly; "item by item" then has no single readable surface. | |
| Fold the corrections into `146-LEDGER.md` | Fewest files; mixes "what may be claimed" with "what we previously got wrong", and leaves ROADMAP.md's false prose uncorrected at its own site. | |

**User's choice:** Correction blocks + a 146 register.
**Notes:** The in-situ block is what warns `/gsd-new-milestone`'s scoping pass — exactly how v1.23's stale prior-art paragraph was going to propagate. → **D-05**

---

## gh#15's outward act

| Option | Description | Selected |
|--------|-------------|----------|
| Post a closing comment, leave OPEN | Second comment reconciling all nine boxes, correcting F-140-07 in the same comment, stating what was and was not bench-proven. Same posture as 139. | ✓ |
| Post the comment AND close the issue | The work is done and the boxes are answered; closing an issue whose acceptance criteria the implementer amended reads as self-certification. | |
| Internal artifact only — nothing posted | Zero outward risk; leaves F-140-07's wrong justification public and uncorrected. | |
| Comment + amend the body's nine boxes | 139 drafted exactly this and the operator declined it ("Comment only"); re-editing the body would make it no longer the text readers were corrected *against*. | |

**User's choice:** Post a closing comment, leave OPEN.
**Notes:** Measured live — gh#15 is OPEN, one comment (`#5233463320`), body unedited (`lastEditedAt = null`), all nine boxes unticked. The decisive argument for posting is that our own comment already carries F-140-07's error in public. → **D-07**, with posting mechanics per 139 → **D-10**

---

| Option | Description | Selected |
|--------|-------------|----------|
| The original nine, correction named | Grade the boxes **as filed**; every box 139 amended is `met-as-corrected` with the correction quoted inline. | ✓ |
| The corrected set 139 published | Grade what was agreed post-correction with a pointer back; a stranger sees nine unticked boxes and a reconciliation grading different criteria. | |
| Both columns, side by side | Whole arc visible in one read; wider table, duplicates 139's own disposition column. | |

**User's choice:** The original nine, correction named.
**Notes:** CLOSE-04's own phrase — *met-as-corrected (naming the correction)* — only parses against the text as filed. → **D-08**

---

| Option | Description | Selected |
|--------|-------------|----------|
| Boxes + the F-140-07 correction + the bench boundary | Nine dispositions, the public correction, and one short paragraph: one part / one controller / one shield revision, `0x08`/`0x0B` skipped-with-reason, the 6.25 V ceiling, no comparative claim. | ✓ |
| Strictly the nine boxes + F-140-07 | Tightest claim surface; states the bench asymmetry only where strangers do not look. | |
| Boxes + boundary + a user-facing "what changed" | Doubles as the announcement; duplicates CLOSE-05 and creates two public texts that must not drift. | |

**User's choice:** Boxes + the F-140-07 correction + the bench boundary.
**Notes:** Answers the obvious "does it work?" follow-up without the comment becoming release notes. → **D-09**

---

## Claim-gate arming surface

| Option | Description | Selected |
|--------|-------------|----------|
| 146 artifacts, with per-file caveat rules | All-or-nothing on the five `.planning` artifacts; forbidden phrases scanned in all five, the 6.25 V caveat required only where it belongs. Sub-repo docs get a separate check. | ✓ |
| 146 artifacts + the sub-repo docs, one gate | Strongest single guarantee; forces a 6.25 V paragraph into `doc/PROTOCOLS.md` and the app README under a rule written for release bodies. | |
| 146 `.planning` artifacts only, uniform rules | Closest to the existing script; leaves the outward-facing sub-repo docs with no machine check at all. | |

**User's choice:** 146 artifacts, with per-file caveat rules.
**Notes:** 139's scanner *requires* its caveat in every file it scans, so extending the surface would have dragged the caveat into public docs by construction. → **D-11**

---

| Option | Description | Selected |
|--------|-------------|----------|
| Fixtures + a real-file plant transcript | pytest over `fixtures/` proves the patterns; a plant-and-revert against a real artifact proves `_DEFAULT_TARGETS` is wired to the files that ship. Covers both of CLOSE-01's clauses. | ✓ |
| Fixtures only | The established BASE-08 pattern; says nothing about whether the target list points at what ships. | |
| Real-file plants only | Directly proves arming; leaves no standing regression test for the pattern table. | |

**User's choice:** Fixtures + a real-file plant transcript.
**Notes:** CLOSE-01 makes two distinct claims — *armed against the real files* and *seen to fail*. Phase 145 found three acceptance locators that were false GREENs, one passing against a record with no content in it. → **D-12**

---

| Option | Description | Selected |
|--------|-------------|----------|
| Phase-local script, forbidden phrases only | Second small scanner reading the changed sub-repo doc files: zero forbidden phrases plus the presence of CLOSE-03's five required topics. No blanket caveat rule. | ✓ |
| A committed test in each sub-repo | Strongest against drift (PROTOCOLS.md genuinely went stale); adds brittle doc-content assertions to two repos at close. | |
| No machine check — the operator review covers it | Zero tooling; drops the mechanizable half of a discipline this project says is only half mechanizable. | |

**User's choice:** Phase-local script, forbidden phrases only.
**Notes:** Turns CLOSE-03's five topics from a prose promise into a machine-checkable list. `firestarter_app` has had **zero** v1.31 doc commits and `--pulse-us` appears nowhere in its README. → **D-13**

---

| Option | Description | Selected |
|--------|-------------|----------|
| Cite by `file:line`, never reproduce | v1.22's solution; forbidden claims referred to by location and finding id, only permitted wording quoted. Preserves 139's no-proximity-window design. | ✓ |
| Narrow the pattern table for the ledger's needs | Lets the ledger write naturally; risks a real overclaim slipping through at the artifact that matters most. | |
| One explicitly-labelled quarantine block | Readable, has label-aware precedent; every exclusion is a hole, and 145-08 caught a check that self-matched its own quoted literal. | |

**User's choice:** Cite by `file:line`, never reproduce.
**Notes:** The self-reference trap bit all six `125-0N-SUMMARY.md` files. Consequence carried into CONTEXT.md: 139's table forbids `\bproven\b` unqualified and the phase records use it honestly throughout, so the closing artifacts must be **written** around it rather than the pattern loosened. → **D-14**

---

## Claude's Discretion

Recorded in CONTEXT.md's `### Claude's Discretion` index. In brief: every word of the five closing
artifacts subject to D-14's citation discipline; the ledger's row count, column set and section order
(including whether the 6.25 V ceiling or the MERGE-05 exemption leads within the opening section); which
of the nine gh#15 boxes gets which disposition and each reason's wording; the correction register's
table shape; which files CLOSE-03 touches and the split between `firestarter/CLAUDE.md` and
`firestarter/doc/PROTOCOLS.md`, and whether the host half is a README edit, a new `doc/` chapter, or
both; whether D-11's gate and D-13's doc check are one file with two modes or two files; plan
decomposition and wave structure; and the form of any meta-gitlink assertion at phase end.

## Deferred Ideas

Full list in CONTEXT.md's `<deferred>`. Declined during this discussion, each with its reason: a PR
into `beta` or a full cut (D-01); a predicted tag literal in the release bodies (D-02); backlog stubs
or a STATE.md block for Phase 145's residuals (D-03); clamping `extract_long`'s `pulse-delay` (D-06);
closing gh#15 and amending its body boxes (D-07); one gate over the sub-repo docs (D-11); committed
doc-content tests in both sub-repos (D-13); loosening `\bproven\b` or adding a quarantine block (D-14).

Carried forward untouched with a ledger row each: the ten `no v1.31 owner` items from Phase 145 (A1's
multi-pulse regime, row 27's smooth-vs-end-burst discriminator, 999.30's bar-never-100 %, 999.31's
missing firmware pulse ceiling and T-145-45, FUT-08's VPP-under-load, the single-byte margin failure's
root cause, `0x08` and `0x0B` bench validation, a true-UV `0x07` point, the 6.25 V ceiling), plus
F-140-05's `0x07` Intel-family split, FUT-PRESTO / FUT-MAXPULSE / FUT-OVERPROG-MAP, the orphaned
F-141-11 / F-143-02 / F-143-03 porcelain coupling, and F-138-05 / F-143-04's `KeyError`.

**Scope creep:** none raised. Every area the operator selected clarified how an already-scoped
requirement is implemented; no new capability was proposed.
