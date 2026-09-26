# Phase 152: Outward-Facing Close (operator-gated) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-20
**Phase:** 152-outward-facing-close-operator-gated
**Areas discussed:** Publication boundary, The three issue threads, The claim gate, What may be claimed

**Area selection:** the operator selected all four presented areas, and in the same answer raised a
fifth item (split firmware builds for the leonardo ceiling) which was redirected as scope creep and
captured as a deferred idea with live measurements.

---

## Publication boundary

### Q1 — Where is the publication boundary?

| Option | Description | Selected |
|--------|-------------|----------|
| Post the comments, hold the notes | Comments posted in-phase (satisfies criteria 1-2 literally); release notes authored version-agnostic and posted at close | ✓ (via discretion) |
| Post everything in 152 | Merge to beta first, read the cut version, post everything | |
| Draft everything, post at close | Follow 146 D-01 exactly; nothing published in 152 | |

**User's choice:** "you 6" → clarified as **"you decide"**.
**Notes:** Claude recommended option 1 and it was accepted. Rationale: criteria 1-2 use the verbs
"is posted"/"carries a comment", which 146's draft-only boundary cannot satisfy; criterion 4's verb
is "announce", dischargeable by content per 146 D-13. **Later superseded in sequencing by Q4.**

### Q2 — Which releases does the release-notes work target?

| Option | Description | Selected |
|--------|-------------|----------|
| Only the v1.32 cut | One app body + one fw body; b16-b22 stay bodiless as a recorded cost; b14 not rewritten | ✓ |
| v1.32 cut + backfill b21 | Also post 146's authored notes where they were meant to go | |
| v1.32 cut with a gap section | Two bodies carrying a "what happened in b16-b22" catch-up | |

**User's choice:** Only the v1.32 cut.
**Notes:** Measured and presented before the question: every app release b16→b22 and every fw release
b16→b19 has body length exactly 0; `beta-release.yml` passes no `body:`. Last live notes are b14,
which still publicly announce `dev sdp enable|disable` (deleted 2026-08-05) and say an opt-in re-lock
is "deliberately not part of this release" — the forward-looking wording OUT-04 names.

### Q3 — How is the operator gate made structurally self-protecting?

| Option | Description | Selected |
|--------|-------------|----------|
| Agents never post — you run the command | Plans produce artifacts + a POST-COMMANDS.md; capability absent rather than gated; survives --auto by construction | |
| One blocking review, then agents post | Single checkpoint over all bodies | |
| Per-artifact gate, agents post | Separate blocking checkpoint immediately before each post | ✓ |

**User's choice:** Per-artifact gate, agents post.
**Notes:** Accepted cost stated back: protection remains checkpoint-dependent, so the roadmap's
"must NOT run under --auto/--chain" rule stays load-bearing and is restated in every posting plan's
frontmatter.

### Q4 — gh#21's provenance claim is false in every published version. How to handle?

| Option | Description | Selected |
|--------|-------------|----------|
| Split it: post 12 and 11, gate 21 on the cut | One owed carry-forward, recorded | |
| Post all three now, word gh#21 as pending | Nothing overclaimed, nothing carried; softens "answerable because" | |
| 152 owns the beta merges, then posts all three | Merge, let CI cut, read both versions, then post everything | ✓ |

**User's choice:** 152 owns the beta merges, then posts all three.
**Notes:** The question was raised because a mid-discussion check found `origin/beta` (the commit that
cut b22) still carries `fw_board_identity=None` hardcoded at `cli_handlers.py:2514` — the provenance
fix exists only on the unmerged milestone branch, 67 commits ahead. Claude then named what the phase
absorbs: PRs to beta not direct merges, two cuts firing by design, `git cherry` not SHA ancestry,
the empty-sibling-root precondition, `gh workflow run` blocked by the auto-mode classifier, and
telling `/gsd-complete-milestone` the merges are done.

### Q5 — continue or move on?

Operator chose **Next area**, delegating the merge-gating mechanics to Claude's discretion.

---

## The three issue threads

### Q1 — Criterion 2 says gh#32 is still OPEN, but it was closed 2026-08-08. Resolve how?

| Option | Description | Selected |
|--------|-------------|----------|
| Amend the criterion to #21/#11/#12 | Record the pre-milestone duplicate-fold; dated amendment, pre-amendment wording retained | ✓ (via discretion) |
| Reopen #32 | Literally satisfies the text | |
| Treat folded-as-satisfying, no amendment | Read "still OPEN" as "not closed by this milestone" | |

**User's choice:** "you decide" → Claude amended.
**Notes:** Reopening would un-do a correct `devtest-triage` fold under the very rule that closed it;
leaving it stands a criterion whose plain reading is false. Claude also folded in the same-class
finding that REQUIREMENTS.md's OUT-01/OUT-04 bullets are stale — OUT-04's own text currently violates
OUT-05's fifth claim class.

### Q2 — What does OUT-03's gh#11 comment carry, given FIX-06 was already answered 2026-07-30?

| Option | Description | Selected |
|--------|-------------|----------|
| The unblocker + the honest non-claims | Lead with what unblocks the reporter, then the non-claims | |
| Provenance + non-claims only | Milestone deliverables only; cite the old comment for FIX-06 | |
| Declare OUT-03 discharged, post nothing | Record the discharge | |

**User's choice:** *"I don't really understand, is it erasable or not? does the infoic file and the
datasheet say the same thing? and the truth must be sent to firestarter and the fw must follow the
rules"*
**Notes:** Not an answer to the options — a direct factual challenge. Claude investigated primary
sources: extracted the AT28C256 datasheet (needed `pip install pypdf 'cryptography>=3.1'`; the PDF is
AES-encrypted and `pdftotext` is absent), and read the `infoic.xml` record. Result: **the part IS
erasable** — datasheet Table 6-1 documents a hardware Chip Erase mode (OE at 12.0 V, tW 10 ms min)
plus an optional 6-byte software erase code held in an app note; infoic sets flags bit 0x10
(erasable). firestarter's three surfaces disagree with each other, and Phase 121 D-12's stated premise
("advertising FLAG_CAN_ERASE for these 84 chips is a false capability statement") is disproven.

### Q3 — Given that, how should 152 handle it?

| Option | Description | Selected |
|--------|-------------|----------|
| State it outward + file two backlog items | Say it in the comments, backlog the fixes, correct D-12's premise in the record; no code change | ✓ |
| Outward text only, no record correction | Leave D-12's reasoning as written | |
| Fix info's row inside 152 | One-line host change plus the outward text | |

**User's choice:** State it outward + file two backlog items.

### Q4 — Criterion 2 asks for a fresh `dev test` run. What does the comment actually ask for?

| Option | Description | Selected |
|--------|-------------|----------|
| Ask for both, either alone is useful | `write -b` + `verify` primary; `dev test` secondary with the blank-part precondition | |
| Ask only for write -b + verify | Don't ask for a run we know fails | |
| Ask for dev test with the precondition stated | Keep it as the single ask | |

**User's choice:** *"if blank prom isn't needed for writing it shall never do a blank check before
writing. but erase and blank check shall be possible to do in there own steps"*
**Notes:** A policy decision rather than an answer. Presented before the question: `chip_test.py:1893`
calls `write_eprom` with no flags and the signature defaults `operation_flags: int = 0`, so
`FLAG_SKIP_BLANK_CHECK` is never set and `dev test` fails at write INIT on any non-blank part — the
exact `Not blank, at 0x000000, v: 0x40` pasted on gh#20 with b15. Claude reflected the policy back,
then measured its decomposition and found `blank` as a standalone step **already works**
(`cli_handlers.py:854` + `eeprom_28c.cpp:218`), so only the write-path conditional at
`eeprom_28c.cpp:517` and the missing `CMD_ERASE` arm are owed — plus the 12 V-on-OE / GATE-03 hazard.

### Q5 — Where does the policy land?

| Option | Description | Selected |
|--------|-------------|----------|
| Backlog item, stated outward as queued | Consistent with how the erase finding was routed | |
| Do the blank-check half in 152 | One conditional, unblocks a reporter today | |
| New phase 153, close v1.32 without it | Add a phase to v1.32; 152 closes referencing it | ✓ |

**User's choice:** New phase 153.

### Q6 — What order do 152 and 153 run in?

| Option | Description | Selected |
|--------|-------------|----------|
| 153 first, then 152 closes | Out-of-number-order dependency; one merge, one cut, one set of notes | ✓ (via discretion) |
| 152 first, 153 gets its own cut | Close the record sooner; two cuts, two announcements | |
| Fold 153's work into 152's merge | Keep numbering, hold the merge | |

**User's choice:** "you decide" → Claude chose 153 first.
**Notes:** Option 2 was disqualified on the phase's own terms — it would post `write -b` as
recommended practice into the most public artifact hours after the operator declared that check
shouldn't exist, which is the failure class OUT-05's gate exists to catch. Option 3 would draft the
close's artifacts against code landing after them and collide on `cli_handlers.py` under
one-writer-per-file. A hard precondition was recorded: Phase 153 does not yet exist in
ROADMAP.md/REQUIREMENTS.md, and creating it is a `/gsd-phase` operation.

---

## The claim gate

### Q1 — What surface does the gate scan?

| Option | Description | Selected |
|--------|-------------|----------|
| Frozen drafts, then re-scan what was posted | Two invocation modes, one pattern table | ✓ (via discretion) |
| Frozen drafts only, verified by blob SHA | 146 D-10's mechanics | |
| Live posted text only | Only the real outward surface is asserted on | |

**User's choice:** "you decide" → Claude chose drafts-then-posted.
**Notes:** A blob SHA proves intent, not what GitHub stored, and `updatedAt` bumps on creation so it
is not a body-edit oracle. Mechanics inherited from 149's gate, including enumerated-never-wildcard
targets, hard-coded paths (the `_HERE` fail-open), the `FIRESTARTER_CLAIMSCAN_TARGETS_152` seam, and
the `"152-"` self-check literal in both the call and its message.

### Q2 — How does the gate treat the Phase 153 capabilities, which WILL ship?

| Option | Description | Selected |
|--------|-------------|----------|
| Permitted, but caveat-required | Move them to the required-caveat table; mirrors 149's PGSZ-05 mechanism | |
| Forbidden entirely until silicon confirms | Maximally conservative | |
| Permitted with no caveat requirement | Least machinery | ✓ |

**User's choice:** Permitted with no caveat requirement.
**Notes:** The concern was stated inside the option text — nothing would then stop "erase now works on
AT28C256" standing unqualified beside a family nobody here owns, the "now provable" → "now proven"
drift v1.22's C-5 correction exists to prevent. Chosen anyway; treated as the operator's decision.

### Q3 — That collides with criterion 5's pairing clause. Which moves?

| Option | Description | Selected |
|--------|-------------|----------|
| Amend criterion 5 to exempt shipped behaviour | Narrow the pairing clause to correctness/validation claims | ✓ (via discretion) |
| Keep criterion 5, require the caveat after all | Reverses Q2 | |
| You decide | | ✓ |

**User's choice:** "You decide" → Claude amended criterion 5.
**Notes:** Raised as new information rather than re-litigation: criterion 5's second half requires
every permitted `0x0D` claim to be paired with its non-claim, and erase / the write-path policy are
literally `0x0D` handler changes, so a caveat-free gate would pass artifacts the criterion says should
fail. Claude narrowed the criterion, leaving all five forbidden classes untouched, and added — flagged
as vetoable — a once-per-artifact milestone-level non-claim, which is where v1.22/v1.23/v1.31 actually
put the discipline and matches b14/b15's own "What is NOT proven" sections.

### Q4 — Does 152 produce a milestone honesty ledger?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — 152-LEDGER.md, and it's a gate target | Follows 137/146; the ledger cannot itself overclaim | ✓ |
| Yes, but not a gate target | Gate armed only at outward text | |
| No — fold it into the phase record | Least churn | |

**User's choice:** Yes — 152-LEDGER.md, and it's a gate target.

### Q5 — continue or move on?

Operator chose **Next area**, delegating the target list, fixture-suite shape and plant-and-revert
transcript to Claude's discretion.

---

## What may be claimed

### Q1 — How is `lock-status` framed, given it's beta-only and mostly refuses?

| Option | Description | Selected |
|--------|-------------|----------|
| Announce with the refusal as the feature | Lead with the named refusal; beta-only; matched firmware; W29C040 was a probe | ✓ (via discretion) |
| Announce plainly, caveats in a NOT-proven section | Matches b14/b15's shape | |
| Mention it minimally | Two sentences | |

**User's choice:** "you decide" → Claude chose refusal-as-feature.
**Notes:** Decided on 151's own measured class sizes: 406 of 746 rows have no protection mechanism,
111 are documented-not-readable, and no `0x05` row answers by default. A named refusal is the
command's dominant designed behaviour, so opening with "reports your chip's protection state" would be
wrong for most chips a reader tries.

### Q2 — How is OUT-01's gh#12 reply produced?

| Option | Description | Selected |
|--------|-------------|----------|
| Adapt the 137 draft, diff recorded | Preserve once-reviewed wording; add the second withdrawal, 999.28, lock-status, 153 | ✓ (via discretion) |
| Author fresh, cite 137 as input | Nothing stale carries by accident | |
| Adapt, and say plainly it was owed since v1.30 | Most candid; surfaces a process failure publicly | |

**User's choice:** "you decide" → Claude chose adapt-with-diff, omitting option 3's process narration.
**Notes:** Criterion 1 already mandates stating the ask is half-answered *for a second release*, which
discloses the slip in the terms that affect the reporter; narrating milestone process serves us, not
them, and the operator had flagged that half as their call.

### Final check

Operator chose **"I'm ready for context"**, declining three further areas Claude offered (plan/wave
shape given three repo merges; what `/gsd-complete-milestone` is left holding; whether the firmware
notes address the three `.hex` assets and the leonardo ceiling). All three are recorded in CONTEXT.md
under Claude's Discretion.

---

## Claude's Discretion

Areas the operator explicitly delegated: the publication boundary (Q1); the gh#32 criterion amendment;
the 153-before-152 ordering; the gate's scan surface; the criterion-5 narrowing; `lock-status`'s
framing; and adapt-vs-author-fresh for the gh#12 reply. Each is recorded in CONTEXT.md as a numbered
decision with its reasoning and its rejected alternatives.

Additionally delegated by moving on: the merge-gating mechanics; the exact `_DEFAULT_TARGETS` list; the
fixture-suite and plant-and-revert transcript shapes; plan/wave decomposition; the
`/gsd-complete-milestone` handoff; and the firmware notes' treatment of the `.hex` assets.

One item was decided without asking, on precedent: PROJECT.md's "one firmware-touching workstream"
correction, and assigning the `database.py:591` code-comment fix to Phase 153 rather than reaching into
a sub-repo from a docs-only close.

## Deferred Ideas

- **Split or trimmed AVR firmware builds** to relieve the leonardo ceiling — raised by the operator
  while answering the area-selection question. Redirected as scope creep and captured with live
  measurements (27500 B used, 1172 B below the unguarded Caterina cliff, exactly zero MERGE-05
  headroom, and the existing `[env:native_nodevtools]` precedent at `platformio.ini:194`).
- Backfilling b16-b22 release bodies, including 146's orphaned b21 notes.
- Obtaining the Atmel/Microchip *Software Chip Erase* application note — it holds the 6-byte code that
  is the hazard-free path for Phase 153's erase.
- Carried forward unchanged from Phase 151: a `--json` mode for `lock-status`; folding lock state into
  `dev test` reports; a live `0x10` protection read; curating `W29C022`; `write --sdp-relock`
  (Backlog 999.28).
