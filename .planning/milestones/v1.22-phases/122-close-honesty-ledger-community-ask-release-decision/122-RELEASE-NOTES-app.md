# Host app prerelease — AT28C Software Data Protection lifecycle

`pip install --pre --upgrade firestarter`

This GitHub release carries no attached files — it is a tag-and-marker page only. PyPI is the
distribution channel for the host app; the command above pulls it. The matching firmware for this
release is published separately, and its three `.hex` files are what `firestarter fw --install`
pulls when you update your board.

## New command surface for AT28C write protection

`firestarter dev sdp <chip> enable|disable` gives standalone control over Software Data Protection
in both directions. On an ordinary write, the automatic unlock step stays on by default and is now
reported rather than silent; `firestarter write --skip-sdp-unlock` declines it if you want to send
a write without touching the protection state first. An opt-in re-lock after a write is
deliberately not part of this release.

## The refusal, stated before you try it

On parts in this family with no SDP command decoder at all — the two FRAM parts, and the earlier
pre-SDP generation of parts (including the `2804`, `2816`, and `2817` part numbers and their
second-source equivalents) — the `dev sdp` command is refused before the serial port is even
opened, and the reason is named in the refusal. Measured across the full set of 84 chips this
protocol covers: 43 are allowed, 41 are refused, and every 2K×8-sized part in the family sits on
the refused side. The refusal is correct, not a gap: on a part with no decoder, the command bytes
would land as ordinary data at addresses the chip's smaller bus truncates, so sending them is not
harmless.

## `dev test` changed shape, and it always writes

`firestarter dev test <chip>` now takes no options at all. Destructive handling is scoped to
UV-erasable EPROMs, where the sweep stops partway and asks whether the full device may be written;
answering no writes only a small region instead. Every run asks whether to file a report, checking
first for an identical prior report from the same user. **Please read this warning carefully: `dev
test` always writes to the chip you point it at, and it expects a blank or scratch part.** This is
true of every version of the command, not a change in this release, and it should accompany any
public mention of the command.

## A report-filing fix that only reaches users starting with this beta

Reports filed by `dev test` now go to the project-wide issue tracker. Earlier published betas
filed them against the wrong repository — a defect in a released build, fixed in source some time
ago, that only becomes effective for users from this release onward. If you filed a report from an
older beta, it may be sitting in the wrong place.

## Also in this release

This chip family has no erase operation at the hardware level, so a `dev test` sweep now marks
erase as not-applicable with a stated reason instead of reporting a successful erase that did
nothing — the old behavior could mistakenly mark an otherwise-good community test run as a failure.
Documentation has also been corrected wherever it described behavior that never reached silicon,
including that a non-blank AT28C part needs the `-b` write flag and that `-b` skips nothing else on
this family.

## What is proven, and what is not

The SDP lock and unlock command sequences are emitted exactly as specified, checked byte-exact by
golden register trace across all four `0x0D`-protocol pinouts this family spans, with a documented
and measured host-side timing assumption.

On this chip family the resulting protection state cannot be read back afterward, so neither
direction — locking or unlocking — can be confirmed once the command sequence has been sent. A
successful run means only that the command sequence was emitted, nothing more. The caveat this
whole release turns on: **no AT28C silicon was tested.** This protocol family stays recorded as
unverified in the project's validation ledger, and no chip's support status changed in this
release.

## The community datapoint, and the ask

A community member running the previous beta on a real AT28C256 reproduced, on real hardware, the
exact failure this work predicted from source alone. That corroborates the defect on real silicon;
it does not corroborate the fix in this release. If you have AT28C hardware, a plain `write`
followed by a `verify` is the single most useful thing you could report back. The open reports this
release addresses stay open pending a report from real silicon.
