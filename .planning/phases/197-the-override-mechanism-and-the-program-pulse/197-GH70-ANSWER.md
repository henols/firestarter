# gh#70 Answer — Draft

**This is an internal draft-tracking file. Only the "Comment Body" section below is the text
intended for posting to the public GitHub issue. The header above it and the notes below it are
internal project bookkeeping and must never be pasted onto the issue.**

## Status

**DRAFT — APPROVED, HELD PENDING THE BETA CUT. NOT POSTED.**

Operator decision recorded 2026-09-18:

1. **Publication route: `hold`.** The comment is held until the v1.40 beta cut, then posted naming
   the real published version. Reason given: nothing in this milestone is pushed —
   `v1.40-program-parameter-fidelity` has no upstream in either the meta repository or
   `firestarter_app`, and sits 41 commits (meta) / 14 commits (`firestarter_app`) ahead of
   `origin/beta`; `git branch -r --contains` on this branch's tip returns nothing in either
   repository. Both `post-with-beta` and `post-with-commit` would name something a reader cannot
   resolve today. `hold` is the only route on which every claim in the comment body is true at the
   moment it posts.
2. **One text amendment approved, and only one.** The "What changed" paragraph's sentence claiming
   the datasheet PDF is committed to this repository was replaced with wording that keeps the
   correction and the citation but drops that claim, per the exact replacement text the operator
   supplied. No other wording change was approved. The 215-row unverified-pulse-width paragraph
   proposed in an earlier draft round was explicitly NOT added.

**Nothing has been posted.** See "Held-pending deferral" near the end of this file for what releases
this hold and exactly what to do at that point.

## Internal provenance (project bookkeeping only — do not post)

- Produced by phase 197 ("the override mechanism and the program pulse"), plan 08, answering
  requirement PULSE-04.
- The pinout finding disclosed in the comment body below is filed in this project's backlog as
  entry 999.70, with its full evidence recorded in `197-PULSE-INVENTORY.md` and `197-07-SUMMARY.md`.
  That number is intentionally kept out of the public comment body — it is meaningless to a reader
  without this project's planning directory.
- The elevated programming-VCC gap the comment body mentions as "being worked separately" is
  tracked internally as Phase 200 of this project's roadmap.
- Technical cross-check for whoever resolves the version placeholder: the firmware's
  `overprogram_factor` parameter is 0 on all three algorithm 7/8 protocol rows (0x07/0x08/0x0B) —
  no over-program pulse is emitted on any of them, which is what the comment body's "does not
  apply the datasheet's separate over-program pulse" sentence refers to.
- This project's internal inventory of algorithm 7/8 rows still carrying an unverified 100 µs pulse
  width (not evidence that any of them are wrong, only that none has been checked) currently stands
  at 215 of 297 — not cited in the public text, since it names no part relevant to this reader.

## Comment Body

*(Post this section verbatim once the version line is resolved. Do not include this file's header
or footnotes.)*

---

Thanks for tracking down the MBM27C1000 datasheet, @dim20 — I read the PDF you attached page by
page against the earlier cross-check rather than taking your summary on faith, and confirmed the
AC Characteristics table on page 4-68 directly.

**What changed.** This project's chip database was asking for a 100 µs programming pulse on the
MBM27C1000. Your datasheet's Programming Pulse Width (tPW) row gives 0.475 ms minimum, 0.50 ms
typical, 0.525 ms maximum — the database's value was about a fifth of the part's own minimum. That
value is now corrected to 500 µs, taken directly from the AC Characteristics table (tPW) on page
4-68 of the MBM27C1000 datasheet you attached to this issue. The sibling part MBM27C1001 had the
identical defect and got the same correction from its own datasheet. A third Fujitsu part,
MBM27C4001, was also checked against its datasheet — its 100 µs value already matches that part's
own spec, so it was deliberately left unchanged.

**Version:** held pending the v1.40 beta cut; this line will be updated with the real published
version before this comment is posted.

**What this correction does not do.** The firmware applies this pulse width as the start of a loop
that verifies after every pulse and gives up after 25 attempts. On this firmware, none of these
Fujitsu parts get the datasheet's separate, longer over-program pulse that is allowed once a byte
first reads back as programmed. So the corrected pulse width makes the fast programming algorithm
this project already runs more accurate — it is not a complete implementation of everything the
datasheet describes.

**This correction does not close this report.** @henols's observation on this thread still stands
and is untouched by the pulse-width fix: this report and the two related reports (issues #66 and
#71) all stop at the first byte of the final 256-byte block, on three parts of three different
sizes; raising the programming voltage into the datasheet's window did not move the failure at
all; the failure reproduced across multiple physical chips; and six firmware versions in a row
changed nothing. Whatever is causing the reported write failure, the evidence so far points
somewhere other than pulse timing.

**A second finding, measured but not yet tested on real hardware.** While checking the MBM27C1000's
own datasheet against this project's pin-map data, something turned up that was not visible before:
the MBM27C1000's own pin assignment puts /OE (output enable) on pin 2 and A16 (an address line) on
pin 24. Its sibling, the MBM27C1001, has those two pins swapped — A16 on pin 2, /OE on pin 24 — and
this project's pin map for the MBM27C1000 currently uses the MBM27C1001's arrangement, not its own.
That part is a measured, directly-checked fact.

What it would mean if it matters is not yet confirmed: if the pin map really is swapped for this
part, a program pulse and the verify read that follows it could disagree about which physical pin
is actually carrying A16, which could produce exactly the kind of address that never converges near
the top of the chip — matching the failure you reported. That explanation is inferred, not
bench-tested: nobody has put a chip on a bench and isolated the pin-map question from the
pulse-width correction above. It is also worth saying plainly: an earlier comparison on this thread
concluded the pin map was "a match on every pin the part uses." That comparison was made against
the MBM27C1001's datasheet, before the MBM27C1000's own datasheet — the one you supplied — was
available to check directly, and for this specific pair of pins it appears to have been wrong. This
pinout question is being tracked and worked on separately from the pulse-width correction above.

**Two more things worth recording here.** The 6.0 V programming supply the datasheet calls for is a
separate, already-known gap — the software reads that value from its data, but the hardware in use
does not currently apply it during programming — and it is not addressed by this change; it is
being worked on separately. And the programming voltage target for this specific part, 12.5 V, was
already correct in the database, unlike a couple of its Fujitsu relatives, which matches what was
already noted on this thread.

---

## Held-pending deferral (internal — do not post)

**This comment is held, not posted, by explicit operator decision dated 2026-09-18 (`hold`).**
**This is now the consolidated list for every held answer in this milestone.** Two further held
drafts exist: for gh#66, at
`.planning/phases/198-the-two-voltage-nibbles/198-GH66-ANSWER.md`, and for gh#71, at
`.planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md`. Both carry the same
five-section shape and their own copy of these same four steps, so a reader who finds any one of the
three files reaches complete instructions for all three. Whoever runs the v1.40 beta cut should read
this list once and post all three.

- **What is held:** the entire "## Comment Body" section above — the full public answer to gh#70,
  including the corrected pulse width, the firmware limitation, the standing failure hypothesis, and
  the pinout finding — and, in the sibling file
  `.planning/phases/198-the-two-voltage-nibbles/198-GH66-ANSWER.md`, the full public answer to
  gh#66, stating the corrected VPP and program-VCC values for the MBM27C4001 report — and, in the
  further sibling file
  `.planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md`, the full public
  answer to gh#71, crediting the reporter, claiming the one database correction, and answering the
  VPE-as-VPP proposal as now automatic in firmware. None has reached its issue. gh#70 remains OPEN
  with 3 comments, none from this project; gh#66 remains OPEN with 6 comments, none from this
  project; **gh#71 remains OPEN with 3 comments — one from the reporter, and two from this project's
  own maintainer**, so the "none from this project" phrasing used for the other two entries does not
  apply to gh#71 and is not reused for it.
- **Why:** at the time of this decision, `v1.40-program-parameter-fidelity` has no upstream in
  either the meta repository or `firestarter_app`, and sits 41 commits (meta) / 14 commits
  (`firestarter_app`) ahead of `origin/beta`. `git branch -r --contains` on this branch's tip
  returns nothing in either repository. Naming a forthcoming beta version or a commit string would
  both name something a reader cannot resolve today — `post-with-beta` would name a version that
  does not exist, and `post-with-commit` would name a commit nobody can find on any remote branch.
  `hold` is the only route on which every sentence in either comment body is true at the instant it
  is posted. This reasoning is not per-issue; it applies identically to gh#66's and gh#71's held
  drafts.
- **What releases the hold:** the v1.40 beta cut — the point at which `firestarter_app` (and, if the
  correction also touches firmware, `firestarter_fw`) are pushed to `beta` and a real, installable
  version number exists. The same beta cut releases all three held drafts; there is no separate
  trigger for gh#66 or gh#71. **gh#71 is the first held answer whose claims span both
  repositories**, so its two version lines resolve against two different artifacts rather than one:
  the Python package cut at the `firestarter_app` beta push, and the firmware pre-release cut at the
  separate `firestarter_fw` beta push. The firmware half is only postable once that pre-release
  exists **and carries build assets** — this project has already cut a firmware pre-release with zero
  assets attached, and that specific failure cannot be repaired by re-running the build at the same
  version.
- **Exactly what to do at that point — the following four steps apply once per issue, run
  separately for gh#70, for gh#66, and for gh#71:**
  1. Replace the `**Version:**` line(s) in the "## Comment Body" section of the relevant draft (this
     file for gh#70; `198-GH66-ANSWER.md` for gh#66; `199-GH71-ANSWER.md` for gh#71 — which carries
     two such lines, one per release channel) with the real published version(s) (the
     `firestarter_app` version string cut at that beta push, and, for gh#71's firmware line, the
     `firestarter_fw` pre-release confirmed to carry assets).
  2. Re-run the no-over-claim and no-attribution checks against that draft's final "## Comment
     Body" text only — a hand edit at this step can reintroduce either.
  3. Post ONLY that draft's "## Comment Body" section — verbatim, starting after the opening `---`
     and ending before the closing `---` — with
     `gh issue comment 70 --repo henols/firestarter --body-file` for gh#70,
     `gh issue comment 66 --repo henols/firestarter --body-file` for gh#66, or
     `gh issue comment 71 --repo henols/firestarter --body-file` for gh#71. Never paste any of the
     three files' header, "Status", "Internal provenance", or "Held-pending deferral" section onto
     any issue.
  4. Record the returned comment URL back into that draft (in its own deferral section) and mark
     the corresponding requirement complete in `.planning/REQUIREMENTS.md` — PULSE-04 for gh#70,
     VOLT-04 for gh#66, RAIL-05 for gh#71.
- **Requirement status:** PULSE-04 (gh#70), VOLT-04 (gh#66) and RAIL-05 (gh#71) are NOT satisfied by
  their respective plans. All three are explicitly carried forward to the milestone close, to be
  satisfied when each comment above actually posts, per the steps above. The artifacts carrying them
  are this file, `.planning/phases/197-the-override-mechanism-and-the-program-pulse/197-GH70-ANSWER.md`
  for PULSE-04; `.planning/phases/198-the-two-voltage-nibbles/198-GH66-ANSWER.md` for VOLT-04; and
  `.planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md` for RAIL-05.
