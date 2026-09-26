Following up on the 2026-08-03 exchange further up this thread, @datapaganism. You'd hacked a
`CMD_ERASE` command into `configure_eeprom28c` yourself and asked how to trigger it from
`firestarter` proper. The answer that day was "It's not probably implemented yet, I will soon get
it pushed and I will keep you posted." That took a lot longer than "soon" — the push landed 18 days
later, in this milestone's work — but this comment is that promise being kept, not a silence being
broken.

You were reaching for exactly the right thing. The shipped implementation takes the same software
path your hand-hacked `CMD_ERASE` was reaching for — it just goes in through a manufacturer
application note instead of trial and error against the handler.

**Why `erase` refused in the first place**

This is the same shape of problem as the two defects the 2026-07-30 answer above diagnosed on this
protocol — a conflation between what the silicon and the upstream chip data say is possible, and
what firestarter itself was actually doing. On this chip family the host, the wire and the firmware
disagreed about erase capability in three separate places at once: `firestarter info` derived its
"can be erased: yes" line from this part's electrical type alone and said yes; the wire `flags`
firestarter actually sent to the board cleared the erase-capability bit for this algorithm; and the
firmware's protocol handler had no erase arm at all, so the command came back not-supported. The
capability was real — both the datasheet and the upstream chip data agree this family is
electrically erasable — what was false was only that firestarter itself could perform it.

For anyone who wants to check this against the datasheet directly: Microchip **DS20006386B**,
Table 6-1 ("Operating Modes", p. 11), lists two separate documented erase mechanisms — a hardware
chip erase, and an optional software chip erase run entirely over the normal data bus using a
six-byte code the datasheet points to a separate application note for.

**What shipped, and its honest limits**

A standalone `erase` step is now available on this protocol — an implementation of that software
six-byte chip-erase sequence, from Atmel Application Note 0544B ("Software Chip Erase"), with the
wire's erase-capability bit restored so the command reaches the firmware handler at all.

The software path was the deliberate choice over the datasheet's hardware mechanism: that hardware
path drives 12 V onto a pin of this part's pinout, and this project does not put a programming
voltage on a pin of a 5 V part.

The honest limit: the timing constant the erase cycle waits out is an Atmel-family maximum drawn
from that application note, and the algorithm bucket it applies to spans other vendors' parts, not
only Atmel's. A part with a longer actual erase-cycle time than that maximum could read non-blank
right after an erase that looked like it had succeeded, and nothing in the test suite would catch
that. There's a second, structural limit worth stating plainly too: no test in this project can show
that wall-clock wait is actually honoured on real hardware, because the native test harness this
project runs never stubs `delay()` and records no elapsed time at all — that particular assertion is
untestable by construction here, not merely untested so far.

**The write path, and your page-write analysis, @AndersBNielsen**

Your 2025-09-28 analysis of this family's page-write mode is the reason the pre-write blank check on
this protocol was wrong, and that check is gone now. A page write on this family auto-erases
internally exactly as you described, and every page firestarter writes gets read back and checked
byte-for-byte afterward regardless — so the blank check sitting in front of the write was never
actually a safety net. It was a precondition that made a non-blank part impossible to write at all
without an override flag.

One honest correction worth making here too, since a separate piece of work touched this family's
page handling in the same milestone: the firmware now reads this chip's page value from the chip
database instead of a hardcoded constant, and for this specific part the value the database holds is
the same value the constant already was. Nothing about how this chip behaves changed because of that
work, and it explains none of the failures reported on this thread.

One more thing worth being plain about: the write-path fix above lives in the firmware itself, not
the host app, and the host's own test step sends no override flag asking for the old behaviour — so
the fix only takes effect on a board that is actually running this milestone's firmware. `firestarter
fw --install` is the second, necessary half of picking it up; the host install alone does not.

**What remains unproven**

No AT28C part was tested at any point in v1.32 — not in writing the erase sequence, not in choosing
what runs before it, not in any test. @datapaganism and @AndersBNielsen are the only people who have
run an AT28C part against this project at all — everything else this project believes about this
family is derived from datasheets and the chip database, not from silicon. That was true when the
2026-07-30 comment above was written, and it is still true after this milestone.

`0x0D` stays UNVERIFIED in the project's own protocol ledger; nothing in this milestone moves it out
of that status. No chip's support classification in the database moved, and the chip database itself
is byte-for-byte the same as it was before. This thread, and the two other open threads about this
same chip family, all stay open — a code fix is not a validation. The erase timing limit above is
worth repeating here rather than assuming it carried over: an Atmel-family maximum, applied to a
bucket that spans other vendors, with nothing in the test suite that could catch a part whose real
cycle time runs longer than that figure.

**Where I need your help**

If you still have the part, a fresh run of `write` and `verify` — or `dev test at28c256` if you're
up for a full capability sweep — posted on this issue would tell us more than anything derived from
the database ever could. Two things need to be in place first, and both matter: the pre-release host
install, `pip install --pre --upgrade firestarter`, and `firestarter fw --install` to get the
matching firmware onto whichever board you plug in. Either outcome is useful — a clean pass, or a
failure that this time comes from firmware that can actually say which version produced it, which
none of your past reports on this thread could. I'm not promising which way it goes, and I'm
deliberately not naming a release version here, because this comment is meant to hold regardless of
which one you're on when you read it.
