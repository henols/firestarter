# gh#71 Answer — Draft

**This is an internal draft-tracking file. Only the "Comment Body" section below is the text
intended for posting to the public GitHub issue. The header above it and the notes below it are
internal project bookkeeping and must never be pasted onto the issue.**

## Status

**DRAFT — APPROVED, HELD PENDING THE BETA CUT. NOT POSTED.**

Operator decision recorded 2026-09-18, carried forward from the ruling on gh#70 and gh#66 without
re-asking:

1. **Publication route: `hold`.** The comment is held until the v1.40 beta cut, then posted naming
   the real published versions. Reason given: nothing in this milestone is pushed — the meta
   repository's `v1.40-program-parameter-fidelity` has no upstream and sits well ahead of
   `origin/beta`; `firestarter_app`'s and `firestarter_fw`'s branches of the same name likewise have
   no upstream and sit ahead of their own `origin/beta`. `git branch -r --contains` on this branch's
   tip returns nothing in any of the three repositories. Naming a forthcoming beta version, a
   pre-release, or a commit string would name something a reader cannot resolve today. `hold` is the
   only route on which every claim in the comment body is true at the moment it posts — the identical
   reasoning the operator applied to gh#70 and gh#66.

**Nothing has been posted.** See "Held-pending deferral" near the end of this file for what releases
this hold and exactly what to do at that point.

## Internal provenance (project bookkeeping only — do not post)

- Produced by this milestone's last plan for this work item, answering requirement RAIL-05. The
  database correction it claims was produced by an earlier plan in the same phase; the routing
  answer it claims was produced by the phase's firmware plan and is recorded in
  `firestarter_app/tools/DECODE-NOTES.md` section 10.
- Internal identifiers — plan ids, decision ids, requirement ids, and this project's backlog numbers
  — are kept out of the public comment body below because they are meaningless to a reader without
  this project's planning directory. They appear only in this section and in the deferral section.
- **This answer has two halves on two channels, and that is new relative to the two sibling drafts.**
  The chip-database correction ships in a `firestarter` Python package release, cut when
  `firestarter_app` is pushed to `beta`. The routing behaviour ships in a `firestarter_fw` firmware
  release, cut when `firestarter_fw` is pushed to `beta` — a **separate** repository and a
  **separate** push. Whoever resolves the two version-placeholder lines below must name whichever
  artifact actually carries each claim (the Python package version for the database line, the
  firmware pre-release tag for the routing line) rather than one version number for both.
- **The firmware claim is only true once a firmware pre-release exists that actually carries
  assets.** This project has already cut a firmware pre-release with zero build assets attached, and
  that specific failure is not repairable by re-running the same build at the same version. Whoever
  resolves the routing-half placeholder must confirm the named pre-release has assets before treating
  the claim as true.
- The measured figures the comment body quotes — the two socket-pin-1 readings and the corrected
  voltage — come from this phase's bench record and its database-regeneration record, and from
  `tools/DECODE-NOTES.md` section 10 as this plan left it. No figure appears in the comment body that
  those artifacts did not produce.
- The maintainer's own datasheet cross-check and boundary-hypothesis comments, already posted
  publicly on the issue, are the reason the comment body below does not restate the pulse-width
  mismatch or the voltage-cap decode explanation — repeating public text the maintainer already wrote
  would read as a project that does not read its own issues.

## Comment Body

*(Post this section verbatim once the version lines are resolved. Do not include this file's header
or footnotes.)*

---

Thanks for tracking down and attaching the datasheet, @dim20 — it's what made both the correction
below and the answer to your suggestion possible.

**What changed in the chip database — a correction only. This does not close the report.** This
part's programming voltage is now corrected from 18 V to 21 V, taken directly from the datasheet you
attached, and credited to you.

**Your suggestion — using VPE as VPP — is now automatic, and here is what changed to make that
true.** The board's standard programming-voltage path runs through a dropping resistor. Measured at
the actual programming socket, on a board with the pot turned to its maximum setting, that path tops
out at 17.38 V — it cannot go higher no matter how the pot is set. The alternate path, which skips
the dropping resistor entirely, was measured at the same socket pin and the same pot setting at
22.14 V. The firmware now compares a part's required programming voltage against what the standard
path can deliver, and automatically raises the alternate, undropped rail itself whenever a part asks
for more than that path can give — so a part like this one now takes that route without anyone
setting a flag by hand. The old manual override still exists for anything this automatic rule
doesn't catch. One thing does not change: a single knob still sets both paths' voltage, so it still
has to be turned to roughly the part's own requirement, and the firmware's own voltage check still
reports it when it isn't.

Here is the part worth explaining, because it is not obvious. The decision above is **not** based on
what the board's own voltage sensor reports while a part is being programmed. That sensor reads from
a point before the socket, not at the socket itself, and on this same board it read about 7.5% higher
than a multimeter measured at the actual pin. At a part requiring 18 V, that sensor would have read
high enough to call the rail healthy — while the socket itself was still short of 18 V. Using the
part's own requirement against what the path can physically deliver, instead of trusting that
sensor, is why the automatic routing above correctly rescues a part like this one instead of
silently continuing to under-power it.

**Where this lands, and when.** The voltage-routing change described above is a firmware behaviour —
it reaches you in a firmware release, not by upgrading the Python package. The database correction is
the other half, and it reaches you in a Python package release. **Neither has shipped yet.**

- Database correction: held pending the v1.40 beta cut; this line will be updated with the real
  published Python package version before this comment is posted.
- Firmware routing change: held pending the v1.40 beta cut; this line will be updated with the real
  published firmware release before this comment is posted.

**What this does not do.** It does not mean this specific chip is confirmed to program — nothing of
this type has been put through a full write in this work. It does not change the standing
explanation for why this report, and the two related ones, stay open: the position the maintainer
already laid out on this thread about where the failure actually sits. This issue stays open.

---

## Held-pending deferral (internal — do not post)

**This comment is held, not posted, by the same operator decision that holds gh#70 and gh#66, dated
2026-09-18 (`hold`).** See `197-GH70-ANSWER.md` § "Held-pending deferral" in
`.planning/phases/197-the-override-mechanism-and-the-program-pulse/` for the single consolidated
list — now naming all three held issues, all three draft files and all three outstanding
requirements. That section is the operational entry point for the milestone close; the bullets below
restate the same instructions for this draft specifically so this file is also a complete entry
point on its own.

- **What is held:** the entire "## Comment Body" section above — the full public answer to gh#71,
  crediting the reporter, claiming the one database correction and answering the VPE-as-VPP proposal
  as now automatic in firmware. Nothing in it has reached the issue. gh#71 remains OPEN with 3
  comments — one from `dim20`, and two from this project's own maintainer (`henols`), so the
  comment-origin sentence the sibling entries use does not apply to this issue and must not be
  reused here.
- **Why:** at the time of this decision, none of the three repositories' `v1.40-program-parameter-fidelity`
  branches has an upstream, and `git branch -r --contains` on any of their tips returns nothing in
  any of the three repositories' remotes. Naming a forthcoming beta version, pre-release tag, or
  commit string would name something a reader cannot resolve today. `hold` is the only route on
  which every sentence in the comment body is true at the instant it is posted.
- **What releases the hold:** the v1.40 beta cut — the same cut that releases the other two held
  drafts. This entry differs from its two siblings in one respect: its two version-placeholder lines
  resolve against **two different artifacts on two different release channels** — the Python package
  cut at the `firestarter_app` beta push, and the firmware pre-release cut at the separate
  `firestarter_fw` beta push. The firmware line is only postable once that pre-release exists and
  actually carries build assets — a pre-release with none has happened on this project before, and
  cannot be repaired by re-running the same build.
- **Exactly what to do at that point:**
  1. Replace both version-placeholder lines in the "## Comment Body" section above — the database
     line with the real published `firestarter_app` (Python package) version, and the firmware
     routing line with the real published `firestarter_fw` pre-release, confirmed to carry assets.
  2. Re-run the no-over-claim and no-attribution checks against this draft's final "## Comment Body"
     text only — a hand edit at this step can reintroduce either.
  3. Post ONLY this draft's "## Comment Body" section — verbatim, starting after the opening `---`
     and ending before the closing `---` — with
     `gh issue comment 71 --repo henols/firestarter --body-file`. Never paste this file's header,
     "Status", "Internal provenance", or "Held-pending deferral" section onto the issue.
  4. Record the returned comment URL back into this file (in this section) and mark RAIL-05 complete
     in `.planning/REQUIREMENTS.md`.
- **Requirement status:** RAIL-05 is NOT satisfied by this plan. It is explicitly carried forward to
  the milestone close, to be satisfied when the comment above actually posts, per the steps above.
  The artifact carrying it is this file:
  `.planning/phases/199-what-the-rails-can-actually-deliver/199-GH71-ANSWER.md`.
