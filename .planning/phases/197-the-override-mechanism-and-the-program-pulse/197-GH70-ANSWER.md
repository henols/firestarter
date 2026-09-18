# gh#70 Answer — Draft

**This is an internal draft-tracking file. Only the "Comment Body" section below is the text
intended for posting to the public GitHub issue. The header above it and the notes below it are
internal project bookkeeping and must never be pasted onto the issue.**

## Status

**DRAFT — NOT POSTED.** Awaiting an operator decision on:

1. Approval or amendment of the comment body below.
2. Which value replaces the version placeholder — post now naming the forthcoming beta, hold the
   comment until the beta actually publishes, or post now naming the carrying commit instead.

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
value is now corrected to 500 µs, taken directly from that table, and the datasheet PDF you
supplied is committed to this project's repository at `datasheets/MBM27C1000.pdf` so anyone can
check it directly. The sibling part MBM27C1001 had the identical defect and got the same
correction from its own datasheet. A third Fujitsu part, MBM27C4001, was also checked against its
datasheet — its 100 µs value already matches that part's own spec, so it was deliberately left
unchanged.

**Version:** PLACEHOLDER

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

## Version resolution note (internal — do not post)

The comment body above contains one unresolved line: `**Version:** PLACEHOLDER`. This project has
not cut a release carrying the correction yet, and a `beta` push in the `firestarter_app`
repository publishes to PyPI irreversibly, so this placeholder cannot be resolved without an
operator decision. The checkpoint that follows this draft puts three readings to the operator:

- Post now, naming the forthcoming beta version, and say plainly it is not yet published.
- Hold the comment until the milestone's beta cut, then post with the real published version.
- Post now, naming the commit that carries the change instead of a version, and follow up once a
  version exists.

Whichever is chosen, substitute the exact string into the `**Version:**` line above before this
text reaches the issue, and re-run the no-over-claim and no-attribution checks against the final
text, since a hand edit can reintroduce either.
