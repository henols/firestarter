# Phase 187: Upstream Replies — Drafted for Operator Review

**Date:** 2026-09-12
**Requirements served:** REPLY-03 (gh#62), REPLY-04 (gh#60) drafted by this plan (187-05); REPLY-01
and REPLY-02 (gh#23, gh#28, gh#31) are drafted by Plan 187-06 and appended to this same document;
REPLY-05, REPLY-06 and REPLY-07 are cross-cutting and are not a single issue's disposition (REPLY-07
is already discharged — see `.planning/notes/` D-06/D-07 and `REQUIREMENTS.md:118`).

Per D-16, approval here is **per-issue, not document-level**: each issue below carries its own
status line, starting at the literal `PENDING OPERATOR REVIEW`, and is flipped only by that
issue's own posting plan (187-07 through 187-11) — never by this drafting plan, and never by one
issue's approval carrying to another's. Each body is stored a second time, byte-identical, as its
own file under `evidence/bodies/187-gh<n>.md` — that is the file its posting plan passes to
`gh issue comment --body-file` unmodified, so what the operator approves here is exactly what gets
posted.

**Status — gh#23:** PENDING OPERATOR REVIEW (drafted by 187-06, not yet drafted at this plan's time)
**Status — gh#28:** PENDING OPERATOR REVIEW (drafted by 187-06, not yet drafted at this plan's time)
**Status — gh#31:** PENDING OPERATOR REVIEW (drafted by 187-06, not yet drafted at this plan's time)
**Status — gh#60:** PENDING OPERATOR REVIEW
**Status — gh#62:** PENDING OPERATOR REVIEW

## Operator Review

Each status line above is flipped only by that issue's own posting plan (gh#60 and gh#62 by
187-07/187-08 in whichever order the operator sets; gh#23/#28/#31 by their own plans), never by
this drafting plan and never in bulk. Whatever verdict eventually gets recorded against a given
issue in this section is **the orchestrator's rendering of the operator's menu selection at that
issue's own gate, not a verbatim operator quotation** — matching the 173 precedent's own framing.
No verdict has been recorded yet for gh#60 or gh#62; both wait at `PENDING OPERATOR REVIEW`.

**Two items flagged explicitly for the operator to decide at the gate, per this plan's own
instructions — not chosen silently:**

1. **gh#60's label change is a candidate, not yet applied.** The body below states that
   `fix:released` replaces `enhancement` on close. `enhancement` is gh#60's only current label and
   is not a `dev test` taxonomy label to begin with; `fix:released` is the only taxonomy label that
   fits a delivered-and-closed feature request (187-RESEARCH.md §8.3), but no label edit has been
   made and none will be made by this plan. The operator confirms or changes this at the 187-07
   gate. Likewise, `--reason completed` for the close is this plan's assumption (RESEARCH
   Assumptions Log A2), not a named instruction from D-15 — confirm at the same gate.
2. **gh#62's label change is a candidate, not yet applied.** The body below states that
   `cause:firmware` is being added to an issue that currently carries zero labels. RESEARCH §8.3
   notes this is a genuine gray area — `cause:firmware` or no label at all are both defensible,
   since the refusal is correct behaviour rather than a defect. The operator confirms or changes
   this at the 187-08 gate.

**One rewording flagged explicitly for the operator to decide at the gh#62 gate:** the one-line
acknowledgement of gh#65 and gh#66 in gh#62's body says they are **open**, each with a maintainer
datasheet cross-check dated 2026-09-10 — not "unanswered", which is what CONTEXT.md's Deferred
Ideas block called them (DRIFT-2, `187-RESEARCH.md` §DRIFT-2, re-verified this plan's Task 1
against the live API). The operator should confirm this line still belongs in the reply at all,
given that both issues have in fact received a maintainer response since CONTEXT.md was written —
Open Question 2 in RESEARCH names this exact question and resolves it to "carry it, reworded, and
flag the drift" rather than choosing silently.

## Dispositions

| Issue | Title | Disposition |
|---|---|---|
| [gh#23](https://github.com/henols/firestarter_prom/issues/23) | `[dev test] w27e257 — FAIL (7a89fcea856a)` | Reply, stays open (REPLY-01/REPLY-06) — drafted by 187-06 |
| [gh#28](https://github.com/henols/firestarter_prom/issues/28) | `[dev test] m27c512 — FAIL (31547956e56b)` | Reply, stays open (REPLY-02/REPLY-06) — drafted by 187-06 |
| [gh#31](https://github.com/henols/firestarter_prom/issues/31) | `[dev test] m27c1001 — INCONCLUSIVE (d8771536cb43)` | Reply, stays open (REPLY-02/REPLY-06) — drafted by 187-06 |
| [gh#60](https://github.com/henols/firestarter_prom/issues/60) | `[Feature Request] Warning about JP5 for 8MBit EPROMs` | Reply, then close (REPLY-04/D-15) — drafted below |
| [gh#62](https://github.com/henols/firestarter_prom/issues/62) | `Unable to erase AE29F2008` | Reply, stays open (REPLY-03/D-15) — drafted below |

This table is written before gh#23/#28/#31's bodies exist, per this plan's own instruction; 187-06
appends their sections without altering this table's rows (only the "drafted by 187-06" / "drafted
below" annotations become stale once 187-06 lands, and 187-06 is responsible for correcting them).

## Pre-post state

See `evidence/187-05-issue-state-before.json` for the full live capture: state, `stateReason`,
labels and comment count for all six issues this phase touches, plus the `pinnedIssues` GraphQL
read (D-06's verification — no `pinIssue` mutation is made by this phase). Re-verified there,
with command and output: gh#65 and gh#66 are each OPEN with exactly one comment dated 2026-09-10
(the maintainer datasheet cross-check); gh#68 is OPEN and names `AE29F2008` in its own body; gh#61
is CLOSED/`COMPLETED` with `chip:validated`; gh#67 exists as gh#68's sibling with a distinct scope.

## REPLY-05 applicability, per body

Neither body drafted by this plan asks the reporter for a `dev test` re-run — gh#60 answers a
feature request that has already shipped, and gh#62 answers a support question about a refusal
that is already correct behaviour. Per D-17, the `schema_version`/`dedup_fingerprint` re-run
sentence is required only in a reply that asks for a re-run, so its absence from both bodies below
is a decision, not an omission:

- **gh#60:** no re-run ask; REPLY-05 sentence not required, not present.
- **gh#62:** no re-run ask; REPLY-05 sentence not required, not present.

---

## gh#60 — `[Feature Request] Warning about JP5 for 8MBit EPROMs`

**Body file:** `evidence/bodies/187-gh60.md`
**Posted:**

```
Hi @AstoriaFloyd — thanks for filing this, and you're right on both the question and the limit.

**Your question, answered directly.** Writing and erasing energize socket pin 1; reading, verifying, blank-checking and reading the chip `id` do not. On this shield, socket pin 1 doubles as address line A19 and as the destination of the programming-voltage enable line, and only a write or an erase asserts that enable line — none of the read-only operations touch it.

**You're also right that JP5's state can't be checked systematically — confirmed from the project's own schematic record, not offered as an opinion.** The warning the tool now prints says so in its own words:

> "...JP5 (silkscreened "Cut for ROMs with A19 on P1") ships bridged by default (a Bridged SolderJumper footprint) and this tool cannot read its current state on the attached board. JP5 must be cut before this {operation} proceeds, or the part can be damaged. The only escape is answering yes at the interactive prompt."

And the silkscreen on the shield itself reads, verbatim:

> "JP5: Cut for ROMs with A19 on P1"

That instruction is unconditional on the board — check it against the physical shield in front of you; that's the ground truth this gate is built around, not something the tool can infer or detect on its own.

**What shipped.** In the released version `3.0.0b39` (`pip install --pre -U firestarter`), any write or erase on a chip whose pin 1 carries A19 now prints the warning above and refuses to proceed unless you explicitly confirm at an interactive prompt. That's the "warn, and stop operation, unless confirmation that the RURP is in a safe state to do the operation" behavior you asked for.

The full trace behind the "writing and erasing only" answer — which operations assert the enable line, which don't, and why — is here: https://github.com/henols/firestarter_prom/blob/ebd80b53b06b49678e41f12d31136f5b9d3edd26/.planning/notes/jumper-display-ground-truth.md#which-operations-energize-socket-pin-1--the-answer-to-gh60

**Closing this as done.** The feature you asked for shipped in a released version. I'm closing this issue and adding the `fix:released` label in place of `enhancement`, to reflect that a released version now carries the behavior you asked for.
```

---

## gh#62 — `Unable to erase AE29F2008`

**Body file:** `evidence/bodies/187-gh62.md`
**Posted:**

```
Hi @dim20 — you're right, on both halves at once. The `AE29F2008` classification as algorithm 5 is correct, and you're also correct that this silicon can be chip-erased. Those two things aren't in tension: the `0x05` firmware path simply doesn't implement the chip-erase this part's silicon actually supports, so both statements are true simultaneously.

**Your `--force` erase was real, not a no-op.** Running `erase` under the `SST39SF020` identity dispatched into a real hardware erase-execute path for a full-chip erase — the same class of operation any chip-erase performs, not a silently faked success.

**It used the exact software chip-erase sequence the W29C020C datasheet documents for this silicon** — a six-cycle unlock-and-erase command sequence, cycle for cycle identical to that datasheet's own "Command Codes for Software Chip Erase" table. The datasheet's own internal erase time (50 ms), plus the serial round-trips involved in issuing it, is consistent with the 0.14 s you measured.

**It was safe on your board only because `AE29F2008` and `SST39SF020` happen to share a pinout and a voltage class, and because that particular erase path never energizes a programming-voltage rail.** That's a property of this specific chip pair, not a property of `--force` in general. Forcing a different identity onto a different real part could route a mismatched bus configuration, or energize a rail that part doesn't expect — so this isn't a safe general-purpose workaround for a missing capability, even though it happened to be harmless here.

**What changed:** the refusal you hit now names the specific part instead of printing a bare `Not supported` message — in the released version `3.0.0b39` (`pip install --pre -U firestarter`). It doesn't unlock the erase itself.

**What you actually want — a software chip-erase for the `0x05` family — is real, undelivered work.** The datasheet documents the command sequence your `--force` run happened to trigger, so it is buildable, and it's tracked as backlog item 999.63. It is not scheduled, and I'm not going to promise a version for it. One caveat any implementation of it will have to handle: the same datasheet documents that "once the boot block programming lockout feature is activated, the chip erase function will be disabled" — so a correct `0x05` chip-erase needs to account for the part's boot blocks, not merely replay the six-cycle command.

**Related, and worth knowing about:** https://github.com/henols/firestarter_prom/issues/68 — partial or unaligned writes on protocol `0x05` parts (including `AE29F2008`) silently erase the rest of the touched page and still report success. That's a separate, already-filed defect on the same protocol family; it does not cover the page-size issue tracked separately in #67.

Also worth noting from your own earlier report (#61): `read`, `write` and `blank-check` all pass on your `AE29F2008` — only the standalone `erase` command is refused, and that refusal is correct given what's actually implemented today.

The full evidence trace — the exact command sequence, the datasheet cross-reference, and why the benignity here doesn't generalize — is here: https://github.com/henols/firestarter_prom/blob/ebd80b53b06b49678e41f12d31136f5b9d3edd26/.planning/notes/ae29f2008-classification-verdict.md#why-the-reporters---force-erase-worked-and-why-that-is-not-a-licence

**Keeping this open.** The refusal is correct, but the capability you actually want isn't built yet, so closing this would file "we refuse, correctly" as the end of the story. I'm adding the `cause:firmware` label to reflect that this is a real, tracked capability gap rather than a bug in the refusal.

One more thing, since you filed several reports the same day: #65 and #66 are still open, each with a maintainer datasheet cross-check on them as of 2026-09-10. No timeline to promise there either, but they haven't been dropped.
```
