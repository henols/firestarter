# Firmware prerelease — AT28C Software Data Protection lifecycle

This is a beta build of the firmware for the RURP shield. It carries three board builds as
attached assets: `firestarter_leonardo.hex`, `firestarter_uno.hex`, and `firestarter_uno328pb.hex`.
The normal way to install one is `firestarter fw --install`, which pulls the file matching your
host app's release channel; the three files are also attached directly to this release if you
need to flash by hand.

## The headline: the AT28C Software Data Protection commands now actually reach the chip

For years, the sequence that disables Software Data Protection (SDP) on AT28C-family EEPROMs was
emitted through a shared helper that bypassed this family's address-bus remap. On the 28C-family
pinouts, at least one command write went out with the chip's write-enable line held high — a
documented write-inhibit condition on these parts. On top of that, the sequence's own success
check was inverted: both datasheets describing this family state that, when the disable sequence
runs correctly, the command bytes are *not* written to the device as data — so the old check could
only report success when the sequence was *not* recognised by the chip at all. Both problems are
fixed in this release: a family-local, remap-aware command emitter, and a completion signal that
is no longer anti-correlated with success.

## A second, separate defect fixed in the same area

Per-page write verification previously sampled a single byte out of every 64-byte page, so a
partially-written page could still report success. This is a *conflation* of two different checks,
not a sampling-rate tweak, and it is likely the more common cause of reported write failures on
this family. Verification is now done per byte, with the first failing address named in the error,
and page-completion polling is split apart from readback verification.

## New capability: SDP lock, not just unlock

The lock (enable) sequence — three address/data loads followed by the datasheet's write-cycle
wait, with no data payload of its own — is now emitted, and both lock and unlock are available as
standalone commands rather than only as a side effect of writing. The automatic unlock that has
always run before a 28C write stays on by default, but it is now reported with one line before the
sequence and one after — never silently inside it — and it can be declined.

## What is proven, stated exactly

The SDP lock and unlock command sequences are emitted exactly as specified, and this has been
checked byte-exact by golden register trace across all four `0x0D`-protocol pinouts this family
spans, with a documented and measured host-side timing assumption. On the timing: the unlock
sequence's six writes complete in 568 microseconds on a Leonardo, 412 microseconds on an Uno, and
424 microseconds on a 328PB-Uno, measured against a 600-microsecond budget derived from the
datasheet's 100-microsecond-per-byte write-cycle maximum. (A separate bench run on a Leonardo later
measured 572 microseconds for the same emitter and board — cited here only as a second data point,
not averaged with the figure above.)

## What is NOT proven

On this chip family the resulting protection state cannot be read back afterward, so neither
direction — locking or unlocking — can be confirmed once the command sequence has been sent. A
successful run means only that the command sequence was emitted; it does not mean the state
changed on the physical part.

The caveat this whole release turns on: **no AT28C silicon was tested.** Nobody working on this
project currently has an AT28C part on the bench. Whether real silicon actually enters or leaves
the protected state is unverified; whether the write-cycle timing above is met as the die itself
would require is unverified; and this protocol family remains recorded as unverified in the
project's own validation ledger.

## The capability boundary

SDP commands are refused outright on parts in this family that have no SDP command decoder at
all — the two FRAM parts, and the earlier pre-SDP generation of parts (including the `2804`,
`2816`, and `2817` part numbers and their second-source equivalents). Measured across the full set
of 84 chips this protocol covers, 43 are allowed to receive an SDP command and 41 are refused, and
every 2K×8-sized part in the family sits on the refused side. This refusal is correct, not a gap:
on a part with no SDP decoder, the command bytes are not harmless — they would land as ordinary
data at addresses the chip's smaller bus truncates. State this boundary every time the capability
above is described; a sentence about "all four pinouts" without it reads as broader capability
than what shipped.

## One honest datapoint from the community

A community member running the previous beta on a real AT28C256 reproduced, on real hardware, the
exact failure this defect predicted from source alone. That corroborates the defect on real
silicon. It does not corroborate the fix in this release — that remains untested on any physical
part.

## Feedback wanted

If you have AT28C hardware and are willing to test this, please report back on the project
tracker. The open reports this release addresses stay open pending a report from real silicon.
