# Phase 122: CLOSE — honesty ledger, community ask, release decision - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-30
**Phase:** 122-CLOSE — honesty ledger, community ask, release decision
**Areas discussed:** Beta publish vs. ask timing; The beta-push decision (CLOSE-03); The honesty ledger + gh#11's silicon datapoint; gh#12 reply scope + issue disposition

---

## Beta publish vs. ask timing

### Q1 — Does Phase 122 publish a v1.22 beta itself?

| Option | Description | Selected |
|--------|-------------|----------|
| Publish b14 in-phase, then comment | Makes CLOSE-02's "please re-test" actionable in one touch; v1.21 Phase 115 precedent; b13 lacks Phase 121's phantom-erase fix and would auto-tag `community-fail` | ✓ |
| Publish b14, smoke-test it on the bench, then comment | Phase-115-shaped gate: `pip install --pre` → `fw -i` → one live op on a W27C512 before pointing a stranger at it; costs a bench session | |
| Comment now, publish and ping later | Keeps the close small, matches the 2026-07-28 promise; but the re-test ask is hollow against b13 and the ping lands outside the milestone | |

**User's choice:** Publish b14 in-phase, then comment.
**Notes:** The bench smoke-test gate was explicitly available and declined. Recorded as an owned trade-off in CONTEXT.md `<specifics>`: the b14 install/flash path is trusted rather than re-proven before two strangers are pointed at it.

### Q2 — What do we ask datapaganism to run on b14?

| Option | Description | Selected |
|--------|-------------|----------|
| Plain write + verify first, `dev test` optional | Directly answers "did your symptom go away"; `dev test` second gives the dedup-fingerprinted artifact; their chip already holds throwaway data | ✓ |
| Plain write + verify only | Smallest ask; forgoes the structured report Phase 121 exists to make trustworthy | |
| `dev test at28c256` only | Richest evidence, auto-files via `gh`; but writes the whole device unprompted (28C is non-UV) and buries their symptom in a sweep verdict | |

**User's choice:** Plain write + verify first, `dev test` as an optional bonus.
**Notes:** Phase 121 D-04's always-writes warning is inherited by the ask text.

### Q3 — Which channels must be live before the comments go out?

| Option | Description | Selected |
|--------|-------------|----------|
| Both channels, verified public before any comment | PyPI `--pre` + GitHub prerelease with `.hex` assets, then an explicit resolution check (Phase 115 Step 0) | ✓ |
| Both channels, comment as soon as CI reports success | Saves a step; but this is exactly how b12 was lost — a PAT-created release suppressed auto-publish while CI looked green | |
| GitHub prerelease only, point the tester at the asset | Avoids the manual PyPI dispatch; leaves PyPI `--pre` on b13 for everyone else | |

**User's choice:** Both channels, verified public before any comment.

### Q4 — What version number does the cut carry?

| Option | Description | Selected |
|--------|-------------|----------|
| Continue the beta series — 3.0.0b14 | What CI auto-increment produces; the host cannot order pre-release suffixes anyway (Phase 120 D-16), so a larger number buys no detection | ✓ |
| Minor bump — 3.1.0b1 | Signals the new wire commands and removed flags; breaks auto-increment, invites stable expectations, re-couples numbering to HOST-06 | |
| 3.0.0b14 plus a recorded 3.1.0 stable-candidate marker | Boring number, recorded intent; one more line nobody may read | |

**User's choice:** 3.0.0b14.
**Notes:** Closes the version-numbering question Phase 120 D-16 explicitly routed to CLOSE-03.

---

## The beta-push decision (CLOSE-03)

### Q1 — Which accept/avoid/cleanup decision gets recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| Accept — the merge IS the b14 cut | Merge `--no-ff` → push → CI auto-cuts b14 in both repos → manual `publish.yml` dispatch → verify → comment; no trigger surgery, no spurious extra release | ✓ |
| Avoid — cut from the branch first, then suppress the push trigger | Exact version control via `-f beta_version=`; two repos of trigger edits and a forgotten re-enable kills every future beta | |
| Accept, and clean up the stray b12 | As accept, plus deleting b12 prereleases; outward-facing deletion of something public for three days | |

**User's choice:** Accept — the merge IS the b14 cut.
**Notes:** b12 stays public. This is the "do the cut FROM beta so the merge IS the cut" option the v1.21 post-mortem named.

### Q2 — Where do the merge conflicts get resolved?

| Option | Description | Selected |
|--------|-------------|----------|
| Merge `beta` into the branch first, prove the gate green there, then merge out | Conflicts resolved where the nine-row non-regression set runs; `beta` never sees an unproven intermediate | ✓ |
| Resolve during the outbound v1.22→`beta` merge | One merge instead of two; but the proof happens after CI has already cut and published b14 | |
| Resolve on the branch, plus assert each of the 5 hotfix behaviours by name | Slower; the double-apply is exactly the case a green suite can hide | |

**User's choice:** Merge `beta` into the v1.22 branch first, prove the gate green there, then merge out.
**Notes:** The conflict is concrete — `version.h` b11 vs b13, and five `quick-260728-ahy` commits present on both sides with different SHAs, layered on Phase 121's rewrite of the same `submit_report` step order.

### Q3 — Does Phase 122 also tag v1.22 and bump the meta gitlinks?

| Option | Description | Selected |
|--------|-------------|----------|
| Ledger + comments + publish in-phase; tag and gitlink bump stay with `/gsd-complete-milestone` | Mirrors v1.21 exactly; the tag then points at a published, channel-verified beta | ✓ |
| Phase 122 does everything including the tag | Nothing dangling; collapses the close ritual into a phase and tags before the phase's own verification | |
| Publish + gitlink bump in-phase; tag deferred | Meta repo matches what the community installs; needs to wait for CI's version-bump auto-commit | |

**User's choice:** Tag and meta gitlink bump stay with `/gsd-complete-milestone`.

### Q4 — Does the b14 prerelease body carry the honesty statement?

| Option | Description | Selected |
|--------|-------------|----------|
| Hand-write the body with the permitted claim and the silicon caveat | Criterion 4 demands closing docs match the ceiling; an auto-generated commit list makes no claim yet a reader infers "SDP works" | ✓ |
| Leave CI's generated body; honesty stays in the ledger and comments | Zero extra release work; the artifact strangers land on stays silent about the ceiling | |
| Hand-write both repos' bodies with cross-links to the corrected docs | Most thorough; two more artifacts to keep consistent with the ledger | |

**User's choice:** Hand-write the b14 prerelease body with the permitted claim and the silicon caveat.

---

## The honesty ledger + gh#11's silicon datapoint

### Q1 — Where does the honesty ledger physically live?

| Option | Description | Selected |
|--------|-------------|----------|
| New `122-LEDGER.md`; `PROTOCOL-LEDGER` verified, not edited | CLOSE-01 asks that `0x0D` *stays* UNVERIFIED — a check, not a write; avoids touching a closed milestone's record whose header pins a non-ancestor commit | ✓ |
| `122-LEDGER.md` plus one cross-reference line in the `0x0D` row | Single ledger of record; edits a v1.16-scoped `.md`/`.json` and re-runs `check_ledger.py` | |
| Full v1.22 addendum appended to `PROTOCOL-LEDGER.{md,json}` | One authoritative file; grows a closed milestone's deliverable and needs schema extension | |

**User's choice:** New `122-LEDGER.md`; PROTOCOL-LEDGER is verified, never edited.

### Q2 — How is the community silicon datapoint recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| EIGHTH CORRECTION in PROJECT.md + a ledger row: premise silicon-confirmed, fix still unproven | A genuinely new asymmetric fact; raises TRACE-06 from predicted to corroborated without touching `support_status` | ✓ |
| Ledger row only; cite it in the reply, no PROJECT.md correction | Keeps the evidentiary bar honest — it arrived as an issue-comment paste, board revision and firmware build unconfirmed | |
| Keep it out of the ledger; mention only in the gh#11 reply | Strictest ceiling reading; leaves the headline premise with the weaker software-only proof on file | |

**User's choice:** EIGHTH CORRECTION + a ledger row reading premise-confirmed / fix-unproven.
**Notes:** Provenance must be stated honestly in both places — no captured logs beyond the pasted text.

### Q3 — What granularity does the ledger use?

| Option | Description | Selected |
|--------|-------------|----------|
| Claim-class rows, each with permitted wording and explicit non-claim | ~8 classes; makes the permitted/forbidden line auditable instead of re-deriving REQUIREMENTS.md | ✓ |
| Claim classes plus a 41-row requirement→class appendix | Full traceability in this project's usual style; length and a second place that must agree | |
| One row per v1 requirement (all 41) | Nothing hides; largely restates REQUIREMENTS.md's parentheticals | |

**User's choice:** Claim-class rows with explicit non-claims.

### Q4 — Does the ledger record the negative space?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — a short "chose not to prove" section | SDP-F1..F8 deferral reasons plus Phase 121's two owned trade-offs; a close listing only wins reads as overclaiming | ✓ |
| No — those live in REQUIREMENTS.md's Future Requirements and Out of Scope | Keeps the ledger to one job | |
| Only the two owned trade-offs, not the SDP-F deferrals | Keeps the ethically-relevant half at half the length | |

**User's choice:** Yes — include a "chose not to prove" section.

---

## gh#12 reply scope + issue disposition

### Q1 — What happens to gh#12 itself?

| Option | Description | Selected |
|--------|-------------|----------|
| Answer the design question, leave open pending a silicon re-test | Answers the maintainer's own unanswered 2024 question; closing would read as "verified fixed", which CLOSE-02 forbids | ✓ |
| Answer and close as implemented, ceiling stated in the closing comment | Capability genuinely exists and is emission-verified; a closed issue reads as a working feature regardless of the comment | |
| Answer, leave open, add an `awaiting-silicon-verification` label | Makes the open state mean something; the label must pre-exist or `gh issue edit --add-label` fails | |

**User's choice:** Answer the design question and leave open pending a silicon re-test.

### Q2 — What happens to gh#12's drifted asks?

| Option | Description | Selected |
|--------|-------------|----------|
| Address them inline in the reply, split nothing out | Two sentences each for `pdr0663`, `No-Hazmats`, `AndersBNielsen`; opens no issue nobody will own | ✓ |
| Split `pdr0663`'s crash into its own issue, rest inline | A genuinely different defect; but filing on someone's behalf from a year-old paste | |
| Answer only the SDP question | Tight and on-topic; leaves three participants unanswered after 1–2 years | |

**User's choice:** Address them inline; split nothing out.

### Q3 — How much of the story does gh#11's reply tell?

| Option | Description | Selected |
|--------|-------------|----------|
| Full account, and credit their b11 paste as the datapoint that confirmed the premise on silicon | Names both defects, explains that b11 turned silent-partial into an honest hard failure, states nothing is silicon-verified, thanks them | ✓ |
| Full technical account, no credit framing | Avoids implying a community comment carries the weight of a controlled measurement | |
| Short version — two defects found and fixed, please re-test b14 | Respects a volunteer's time; loses the explanation of why their re-test looked worse than 2024 | |

**User's choice:** Full account plus credit for the b11 reproduction.

### Q4 — How do the comments get from draft to GitHub?

| Option | Description | Selected |
|--------|-------------|----------|
| Draft as a committed artifact, blocking operator wording review, then post via `gh` | Plan 116-07 precedent; the draft is auditable against the ledger and the ceiling wording gets a human read | ✓ |
| Draft as an artifact; operator posts manually | Maximum tone control; posted text can drift from the committed draft | |
| Post directly via `gh` once the channels verify | Fewest steps; removes the human read on outward-facing text in the one phase whose job is not overclaiming | |

**User's choice:** Draft as a committed artifact behind a blocking operator wording review, then post via `gh`.

---

## Claude's Discretion

- Every word of the two comment drafts and the b14 prerelease body, bounded by three constraints: the permitted and forbidden claims come in substance from the validation ceiling; the `dev test` mention carries Phase 121 D-04's always-writes warning; nothing may be phrased as "verified fixed."
- The shape, column set, row count and section order of `122-LEDGER.md` (D-11 fixes only that rows are claim classes pairing a permitted wording with an explicit non-claim).
- How the b14 channel verification is evidenced — committed transcript, small script, or a named check in the plan's task list. Only the ordering (before the comments) is fixed.
- Plan ordering, subject to the seven hard sequencing constraints recorded in CONTEXT.md.
- Whether the two comment drafts live in one artifact or two.

## Deferred Ideas

- Deleting the stray b12 prereleases — declined; they stay public.
- A bench smoke-test of the b14 install/flash path — declined at Q1 of area 1; a hardware-gated task in its own right if wanted.
- A minor version bump to `3.1.0b1`, and a recorded `3.1.0` stable-candidate marker — both declined.
- Splitting `pdr0663`'s Windows `ClearCommError` crash into its own issue — declined; addressed inline.
- An `awaiting-silicon-verification` label on gh#12 — declined.
- Editing `PROTOCOL-LEDGER` with a v1.22 addendum or cross-reference row — declined.
- Carried forward from earlier phases and untouched here: `dev test`'s release-channel disposition (999.15 / gh#8), a read-only `dev test` mode, the wider CLI flag re-design, the `infoic.xml` `page_size` decode phase, widening `_probe_port`'s version capture, SDP-F1..F8, and `derive_plan`'s vestigial `locked_destructive`.
- 12 pending todos matched phase 122 by generic keyword overlap only; none folded. Same disposition as Phases 116–121.
