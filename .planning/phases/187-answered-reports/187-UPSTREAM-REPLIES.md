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

**Status — gh#23:** PENDING OPERATOR REVIEW
**Status — gh#28:** PENDING OPERATOR REVIEW
**Status — gh#31:** PENDING OPERATOR REVIEW
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
| [gh#23](https://github.com/henols/firestarter_prom/issues/23) | `[dev test] w27e257 — FAIL (7a89fcea856a)` | Reply, stays open (REPLY-01/REPLY-06) — drafted below |
| [gh#28](https://github.com/henols/firestarter_prom/issues/28) | `[dev test] m27c512 — FAIL (31547956e56b)` | Reply, stays open (REPLY-02/REPLY-06) — drafted below |
| [gh#31](https://github.com/henols/firestarter_prom/issues/31) | `[dev test] m27c1001 — INCONCLUSIVE (d8771536cb43)` | Reply, stays open (REPLY-02/REPLY-06) — drafted below |
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

Neither body drafted by Plan 187-05 asks the reporter for a `dev test` re-run — gh#60 answers a
feature request that has already shipped, and gh#62 answers a support question about a refusal
that is already correct behaviour. Per D-17, the `schema_version`/`dedup_fingerprint` re-run
sentence is required only in a reply that asks for a re-run, so its absence from both bodies below
is a decision, not an omission:

- **gh#60:** no re-run ask; REPLY-05 sentence not required, not present.
- **gh#62:** no re-run ask; REPLY-05 sentence not required, not present.

All three bodies drafted by Plan 187-06 DO ask for a `dev test` re-run, so each carries the
REPLY-05 `schema_version`/`dedup_fingerprint` sentence, placed in the same bolded section as its
re-run ask (immediately adjacent, never in a later section):

- **gh#23:** re-run ask present, in the **"If you want to re-run it."** section; REPLY-05 sentence
  present in that same section.
- **gh#28:** re-run ask present, in the **"If you want to re-run it, with that caveat in mind."**
  section; REPLY-05 sentence present in that same section, immediately preceded by the D-12
  write-shortcut caveat in the section above it.
- **gh#31:** re-run ask present, in the **"If you want to re-run it, with that caveat in mind."**
  section; REPLY-05 sentence present in that same section, immediately preceded by the D-12
  write-shortcut caveat in the section above it.

---

## gh#60 — `[Feature Request] Warning about JP5 for 8MBit EPROMs`

**Body file:** `evidence/bodies/187-gh60.md`
**Posted:**

```
Hi @AstoriaFloyd — thanks for filing this, and you're right on both the question and the limit.

**Your question, answered directly.** Writing and erasing energize socket pin 1; reading, verifying, blank-checking and reading the chip `id` do not. On this shield, socket pin 1 doubles as address line A19 and as the destination of the programming-voltage enable line, and only a write or an erase asserts that enable line — none of the read-only operations touch it.

**You're also right that JP5's state can't be checked systematically — confirmed from the project's own schematic record, not offered as an opinion.** The warning the tool now prints says so in its own words:

> "...JP5 (silkscreened "Cut for ROMs with A19 on P1") ships bridged by default (a Bridged SolderJumper footprint) and this tool cannot read its current state on the attached board. JP5 must be cut before this write or erase proceeds, or the part can be damaged. The only escape is answering yes at the interactive prompt."

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

---

## gh#23 — `[dev test] w27e257 — FAIL (7a89fcea856a)`

**Body file:** `evidence/bodies/187-gh23.md`
**Posted:**

```
Hi @AndersBNielsen — resuming the thread from 2026-08-09. You were right: what you flagged as a rig fault got reported back to you as a chip verdict, and the triage argued against you on exactly that point. That argument was wrong.

**The limit this tool still has, stated plainly.** The fix here is not "the tool can now see an unhooked VPP" — it can't, and it still won't be able to on your next run. The report's status axis only fires for a serial error or a hardware-operation error; a mis-wired VPP doesn't raise either of those, it just produces bad read/write/verify data that still gets treated as an ordinary chip result. So a fresh run today, on the same rig fault, would still show `write BAD, verify BAD` and would still file under a `FAIL` title — not a harness-status title. Re-running with the same VPP wiring will not come back clean.

**What actually changed.** Two things, and neither is "the tool now detects your fault":

- The misleading `vpp_mv`/`vpe_mv` voltage fields were removed from the report entirely. They read the boost-regulator rail, and a regulator rail reads healthy even when the socket itself isn't wired up — which is exactly the trap you hit.
- A disclosure line was added to every report instead, and it says so in its own words:

> "vpp/vpe readings measure the regulator rail only -- they do not show whether the eprom socket is connected (advisory)"

That's the honest version of what those readings can and can't tell you. It would have kept you from reading a healthy rail as a healthy socket connection back in August.

**The W27E257 datasheet defect is still open, unfixed, and on the record.** The programming voltage this project's own database carries for the W27E257 is `13.5 V`; the datasheet gives `12 V`. That's not retracted, not quietly dropped, and nothing else currently tracks it as fixed. When it's corrected, the fix goes into the database generator's decode function; the generated database file itself is regenerated wholesale from that generator and is never hand-edited. Separately: the W27E257 is an EEPROM, not a UV-EPROM, so none of that recent UV-part harness work touches this chip's family at all.

**Being precise about what I'm conceding.** You mentioned the second run actually passed — I want to be careful here, because I looked, and there's no w27e257 run in the tracker that reads PASS; both w27e257 reports here (this one and the earlier #24) are FAIL. What I'm conceding in full is the general point you made: a rig fault got written up as a chip verdict. I'm not going to imply a passing run exists when the tracker doesn't carry one.

**Labels changing on this issue, and why.** I'm adding `cause:rig` alongside the standing `cause:database` — the database defect above is real and unfixed, so that label was never wrong, it's just not the whole story. And I'm adding `needs:report` because this is now waiting on a fresh run from you.

**If you want to re-run it.** Reports are now at `schema_version` `2.0`, and the deduplication fingerprint was deliberately re-keyed in this same release — a fresh run will not group with this old one, and that's expected, not a new defect on top of the old one. Install the released app version `3.0.0b39` (`pip install --pre -U firestarter` — the plain, non-`--pre` install on PyPI is still a 2.x release, none of this is in it), flash firmware `3.0.0b27` with `firestarter fw --install`, then run `firestarter dev test w27e257` again. If your VPP wiring is fixed this time, the report will tell you plainly rather than reading a healthy rail as a healthy connection.

This issue stays open — I'm not closing it on my own reading, only on your response.
```

---

## gh#28 — `[dev test] m27c512 — FAIL (31547956e56b)`

**Body file:** `evidence/bodies/187-gh28.md`
**Posted:**

```
Hi @AndersBNielsen — resuming the thread from 2026-08-09. Same concession as the other reports from that day: what you were pushing back on was how a failure got attributed and reported, and that's what actually changed here — not a fix to the chip.

**What shipped, and what it changes for this issue.** The validation harness (`dev test`) was changed to attribute a failure correctly instead of blaming the wrong layer — that's the harness fix your original report pushed against, and it's in the released app version `3.0.0b39`. It doesn't touch the M27C512-specific defect below at all.

**The M27C512 datasheet defect is still open, unfixed, and on the record.** The database still declares a `6.5 V` programming supply for this chip, distinct from its `5 V` operating supply, and nothing in the current system actually applies that `6.5 V` — it's asserted but never delivered. That's not retracted, not quietly dropped, and no other record currently tracks it as fixed. When it's corrected, the fix goes into the database generator's decode function; the generated database file is regenerated wholesale from that generator and is never hand-edited. The M27C512 is a UV-EPROM, so the recent harness work for UV-type parts does apply to it, unlike the W27E257 case in the sibling thread.

**One caveat, and I want it in front of the ask, not after it.** The harness now gets a non-blank UV part through `dev test` by skipping the blank check, on a path `firestarter write` itself does not take. The identical firmware still refuses a plain `write` on the identical part. So if you re-run and get a PASS, that PASS does not mean `write` works on your M27C512 — it means the validation path passed, on a path your actual write command doesn't use. I'm not adding a field to the report to flag that divergence; that question is still open and unresolved elsewhere, and this reply isn't the place it gets settled.

**Why I'm not calling this `fix:released`.** Only the harness attribution fix shipped — the chip's own defect above did not. Applying `fix:released` here would read as "this is fixed," and it isn't. I'm adding `needs:report` instead, because this is waiting on a fresh run from you.

**If you want to re-run it, with that caveat in mind.** Reports are now at `schema_version` `2.0`, and the deduplication fingerprint was deliberately re-keyed in this release — a fresh run will not group with this old one, and that's expected, not a new defect on top of the old one. Install the released app version `3.0.0b39` (`pip install --pre -U firestarter` — the plain, non-`--pre` install on PyPI is still a 2.x release), flash firmware `3.0.0b27` with `firestarter fw --install`, then run `firestarter dev test m27c512` again.

This issue stays open — I'm not closing it on my own reading, only on your response.
```

---

## gh#31 — `[dev test] m27c1001 — INCONCLUSIVE (d8771536cb43)`

**Body file:** `evidence/bodies/187-gh31.md`
**Posted:**

```
Hi @AndersBNielsen — resuming the thread from 2026-08-09, same as the other two reports in this batch. What you were disputing was how a failure got attributed and reported, and that's the thing that actually changed here — not a fix to the chip.

**What shipped, and what it changes for this issue.** The validation harness (`dev test`) was changed to attribute a failure correctly instead of blaming the wrong layer, in the released app version `3.0.0b39`. That harness fix doesn't touch the M27C1001-specific defect below.

**The M27C1001 datasheet defect is still open, unfixed, and on the record.** The database still maps this chip's pin 30 as an address line, and the datasheet for this part gives that pin no connection at all. The row still points at the 32-pin 27C020 pin map, which is where the mismatch comes from. That's not retracted, not quietly dropped, and no other record currently tracks it as fixed. When it's corrected, the fix goes into the database generator's decode function; the generated database file is regenerated wholesale from that generator and is never hand-edited. The M27C1001 is a UV-EPROM, so the recent harness work for UV-type parts does apply to it — unlike the EEPROM case in the sibling thread.

**One caveat, and I want it in front of the ask, not after it.** The harness now gets a non-blank UV part through `dev test` by skipping the blank check, on a path `firestarter write` itself does not take. The identical firmware still refuses a plain `write` on the identical part. So if you re-run and get a PASS, that PASS does not mean `write` works on your M27C1001 — it means the validation path passed, on a path your actual write command doesn't use. I'm not adding a field to the report to flag that divergence; that question is still open and unresolved elsewhere, and this reply isn't the place it gets settled.

**Why I'm not calling this `fix:released`.** Only the harness attribution fix shipped — the chip's own pin-30 defect above did not. Applying `fix:released` here would read as "this is fixed," and it isn't. I'm adding `needs:report` instead, because this is waiting on a fresh run from you.

**If you want to re-run it, with that caveat in mind.** Reports are now at `schema_version` `2.0`, and the deduplication fingerprint was deliberately re-keyed in this release — a fresh run will not group with this old one, and that's expected, not a new defect on top of the old one. Install the released app version `3.0.0b39` (`pip install --pre -U firestarter` — the plain, non-`--pre` install on PyPI is still a 2.x release), flash firmware `3.0.0b27` with `firestarter fw --install`, then run `firestarter dev test m27c1001` again.

This issue stays open — I'm not closing it on my own reading, only on your response.
```
