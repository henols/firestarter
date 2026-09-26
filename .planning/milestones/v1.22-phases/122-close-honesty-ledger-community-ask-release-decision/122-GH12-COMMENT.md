Hi all,

This has sat unanswered for a while, and one of the open questions on this thread was mine, so let me
close the loop with what got decided and built.

## The 2024 question, answered

Back in 2024 the question here was: *"Always unlock, write and lock the chip again? A special command
for unlocking and locking? What are the use cases?"* Nobody ever came back to that, so here is the
policy that shipped:

- Automatic unlock before a write stays **on by default**, and it is no longer silent — one line is
  printed before the unlock sequence runs, and one line after.
- `firestarter write --skip-sdp-unlock` declines the automatic unlock if you do not want it.
- `firestarter dev sdp <chip> enable|disable` gives standalone control in both directions — chip name
  first, then the mode.
- An opt-in "re-lock automatically after a successful write" step is deferred for now. The reason:
  an unconditional re-lock step inside a pipeline that can fail partway through is a hazard, and
  re-locking after a failed verify would strand you with a locked chip you cannot immediately retry.

## What was actually wrong, briefly

The underlying command sequence the firmware had always sent almost certainly never reached silicon
correctly — a shared code path bypassed some address-bus handling, so at least one command write went
out with the chip's write-enable line held in the wrong state, and the success check for that sequence
was inverted besides. Both are fixed in the current beta. The write-up on issue #11 has the long
version if you want it; keeping this one short on purpose.

## The capability boundary — read this before assuming it covers your part

The new lock/unlock commands are refused outright on any chip in this protocol family that has no SDP
command decoder at all — that includes two FRAM parts and the older pre-SDP `2804`/`2816`/`2817`
generation. Across the 84 parts this protocol bucket covers, 43 are allowed and 41 are refused. That
refusal is deliberate, not a gap: on a part with no decoder, the unlock/lock command bytes are not
harmless — they would be stored as ordinary data at addresses the bus truncates, which is worse than
doing nothing.

## What is proven, and what is not

The lock and unlock command sequences are emitted exactly as specified — checked byte-exact by an
automated register trace across all four relevant pinouts, with a measured host-side timing figure.
That is where the proof stops: on this chip family the resulting protection state cannot be read back
afterward, so neither locking nor unlocking can be confirmed by the software itself — a successful run
means only that the command sequence was emitted, nothing more. Plainly: no AT28C silicon was tested
during this work.

## Three things raised on this thread that never got a reply

**The SST39SF request.** Chip-erase and byte-program sequences for that family are deferred — mainly
because it would multiply the "nobody has silicon to test against" problem into a family that
currently has settled bench evidence behind it, and that tradeoff was not worth making right now. One
thing worth confirming since it was raised as the main concern: this protocol family is 5V-only, and
the firmware never asserts the programming-voltage regulator on it, so there is no path for a
programming voltage to reach a pin on these parts.

**The 2025 write failure.** Looking back at that report: the debug log header shows the host app at
version 1.3.44 with firmware 1.4.2, and the failure was a Windows `ClearCommError` during the send —
which lines up with a pre-3.0 transport bug that a later rewrite (the COBS framing change) replaced
outright. If that same failure still shows up on the current beta, please open a fresh report — it
would be a genuinely new bug rather than the same one.

**The 2K by 8 part.** This is the one where an earlier internal note of mine got this wrong, so I want
to correct it plainly rather than repeat it: a 2K×8 part in this chip family is not in the allowed set
above — it sits on the same 24-pin footprint as the `2816`-class parts, and every one of those is
refused (some because they predate SDP entirely, some because we cannot yet recognise their
particular command set). So whatever protection-related failure you saw on that part is not the bug
this thread is about, and this release's SDP support does not reach it. The datasheet verification and
socket-pin question for that specific footprint are both still open and unresolved. Someone else on
this thread already pointed you toward an alternative part that is supported — that recommendation
still stands. If you want a second look at your specific failure, tell me the exact part number and
what the command output showed, and I will take a look.

## Where this leaves things

This issue is staying open pending an actual re-test on hardware — closing it now would overstate
what has actually been confirmed, since none of this has been checked against real silicon. If you
want to try the current beta: `pip install --pre --upgrade firestarter` plus `firestarter fw
--install`.
