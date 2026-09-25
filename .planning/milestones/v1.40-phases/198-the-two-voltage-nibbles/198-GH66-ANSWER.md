# gh#66 Answer — Draft

**This is an internal draft-tracking file. Only the "Comment Body" section below is the text
intended for posting to the public GitHub issue. The header above it and the notes below it are
internal project bookkeeping and must never be pasted onto the issue.**

## Status

**POSTED 2026-09-20 — the hold is discharged.** (Was: DRAFT — APPROVED, HELD PENDING
THE BETA CUT, NOT POSTED.) See "HOLD RELEASED — POSTED" at the end of this file for the
comment URL and the version named.

Operator decision recorded 2026-09-18, carried forward from the ruling on gh#70 without
re-asking:

1. **Publication route: `hold`.** The comment is held until the v1.40 beta cut, then posted
   naming the real published version. Reason given: nothing in this milestone is pushed — the
   meta repository's `v1.40-program-parameter-fidelity` has no upstream and sits 65 commits ahead
   of `origin/beta`; `firestarter_app`'s branch of the same name has no upstream and sits 19
   commits ahead of its own `origin/beta`. `git branch -r --contains` on this branch's tip returns
   nothing in either repository. Naming a forthcoming beta version or a commit string would both
   name something a reader cannot resolve today. `hold` is the only route on which every claim in
   the comment body is true at the moment it posts — the identical reasoning the operator applied
   to gh#70.

**Superseded — this has now been posted; see the final section of this file.** The original note read: "Nothing has been posted." See "Held-pending deferral" near the end of this file for what
releases this hold and exactly what to do at that point.

## Internal provenance (project bookkeeping only — do not post)

- Both corrected values were produced by this milestone's plan `198-01`, Task 1, which corrected
  two entries in `firestarter_app/tools/datasheet_overrides.json`: `FUJITSU/MBM27C1001` and
  `FUJITSU/MBM27C4001`. Each entry's `electrical.vpp_mv` moved `12000 -> 12500` and
  `electrical.vdd_mv` moved `5500 -> 6000`.
- The two entries are backed by `datasheets/MBM27C1001.pdf` and `datasheets/MBM27C4001.pdf`
  respectively, both git-tracked in `firestarter_app`. The `MBM27C4001` entry's datasheet is the
  same PDF `@dim20` attached to this issue.
- Measured regeneration (this milestone's Task 1 run): 3 rows / 5 electrical field values changed
  database-wide. Of those, the two rows this issue is about — `MBM27C1001` and `MBM27C4001` — each
  moved 2 fields (`vpp_mv`, `vdd_mv`), for 2 rows / 4 field values specific to this report. The
  third changed row, `FUJITSU/MBM27128`, is a different part number and moved only `vdd_mv`; it is
  not part of this issue's report and is not mentioned in the comment body.
- Re-read directly from the shipped `firestarter_app/firestarter/data/chip_database.json` at the
  time this draft was written: `FUJITSU/MBM27C1001.electrical.vpp_mv == 12500` and
  `FUJITSU/MBM27C4001.electrical.vpp_mv == 12500`. Both match the value the comment body states.
- `FUJITSU/MBM27C2001` carries the identical voltage word (`0x4000`) as the two corrected rows but
  has no vendored datasheet, so it was deliberately left unchanged at `(12000, 5500)`. This is a
  known, recorded family inconsistency and is not mentioned in the comment body — citing a
  sibling's datasheet reading for an unvendored part is exactly what this project's override
  discipline forbids.
- The firmware guard-band consequence (the settable VPP window widening as a result of the 12500
  correction) is recorded in this phase's regeneration diff record only. The public comment body
  stays strictly to database values that changed and does not mention it.
- The maintainer (`@henols`) already published both of these values as confirmed mismatches on
  the issue on 2026-09-16, citing page 8 of the same MBM27C4001 datasheet's DC Characteristics
  table (VPP 12.5 V ± 0.3 V; VCC 6 V ± 0.25 V). This draft's corrections agree with what the
  maintainer already posted, so nothing here is a retraction of prior public text.

## Comment Body

*(Post this section verbatim once the version line is resolved. Do not include this file's header
or footnotes.)*

---

Thanks for tracking down and attaching the MBM27C4001 datasheet, @dim20 — its DC Characteristics
table settles the two value mismatches this report and the cross-check above were already about.

**What changed — corrections only. This does not close the report.**

The programming voltage (VPP) target for the MBM27C4001 you tested, and for its 1 Mbit sibling
MBM27C1001, is now 12.5 V rather than 12.0 V — matching page 8's DC Characteristics table in the
datasheet you attached, which specifies 12.5 V ± 0.3 V.

The programming supply (VCC) figure carried for both of those parts is now 6.0 V, confirming the
same table's 6 V ± 0.25 V reading rather than the 5.5 V previously carried.

**Version:** held pending the v1.40 beta cut; this line will be updated with the real published
version before this comment is posted.

You already retested at a corrected VPP and reported the identical write failure, on multiple
chips, at the same address as before. That result stands and is untouched by this change —
whatever is causing the failure, the evidence so far still points somewhere other than the
programming voltage.

---

## Held-pending deferral (internal — do not post)

**This comment is held, not posted, by the same operator decision that holds gh#70, dated
2026-09-18 (`hold`).** See `197-GH70-ANSWER.md` § "Held-pending deferral" in
`.planning/phases/197-the-override-mechanism-and-the-program-pulse/` for the single consolidated
list naming both held issues, both draft files and both outstanding requirements — that section
is the operational entry point for the milestone close; the bullets below restate the same
instructions for this draft specifically so either file is a complete entry point on its own.

- **What is held:** the entire "Comment Body" section above — the full public answer to gh#66,
  the two corrected voltage values and the explicit non-closure statement. Nothing in it has
  reached the issue. gh#66 remains OPEN with 6 comments, none from this project.
- **Why:** at the time of this decision, neither the meta repository's nor `firestarter_app`'s
  `v1.40-program-parameter-fidelity` branch has an upstream, and `git branch -r --contains` on
  either branch's tip returns nothing in either repository's remotes. Naming a forthcoming beta
  version or a commit string would name something a reader cannot resolve today. `hold` is the
  only route on which every sentence in the comment body is true at the instant it is posted.
- **What releases the hold:** the v1.40 beta cut — the point at which `firestarter_app` is pushed
  to `beta` and a real, installable version number exists.
- **Exactly what to do at that point:**
  1. Replace the `**Version:**` line in the "Comment Body" section above with the real
     published version (the `firestarter_app` version string cut at that beta push).
  2. Re-run the no-over-claim and no-attribution checks against the final "Comment Body" text
     only — a hand edit at this step can reintroduce either.
  3. Post ONLY the "Comment Body" section — verbatim, starting after the opening `---` and
     ending before the closing `---` — to gh#66 with
     `gh issue comment 66 --repo henols/firestarter --body-file`. Never paste this file's header,
     "Status", "Internal provenance", or this "Held-pending deferral" section onto the issue.
  4. Record the returned comment URL back into this file (in this section) and mark VOLT-04
     complete in `.planning/REQUIREMENTS.md`.
- **Requirement status:** VOLT-04 is NOT satisfied by this plan. It is explicitly carried forward
  to the milestone close, to be satisfied when the comment above actually posts, per the steps
  above. The artifact carrying it is this file:
  `.planning/phases/198-the-two-voltage-nibbles/198-GH66-ANSWER.md`.

---

## HOLD RELEASED — POSTED 2026-09-20

**The hold described above is discharged. This draft's `## Comment Body` was posted to gh#66.**

- **Comment URL:** https://github.com/henols/firestarter/issues/66#issuecomment-5749346372
- **Version named:** `firestarter` 3.0.0b49 — the release in which the correction first shipped, verified
  against the published artifact rather than assumed.
- **Requirement VOLT-04:** marked Complete in `.planning/REQUIREMENTS.md` and
  `.planning/milestones/v1.40-REQUIREMENTS.md`.
- **Released by:** the v1.40 beta cut — `firestarter_app` 3.0.0b49 (on PyPI) and
  `firestarter_fw` 3.0.0b34 (pre-release, four `.hex` assets attached and verified).
- The no-over-claim and no-attribution checks were re-run against the final posted text.
