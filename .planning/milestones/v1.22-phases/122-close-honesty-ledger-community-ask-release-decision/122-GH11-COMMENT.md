Hi @datapaganism,

Thank you for coming back with the 2026-07-27 re-test on your actual AT28C256 hardware, and for the
"happy to test for you" offer — that is genuinely valuable, because nobody working on this project
owns an AT28C part right now. Your paste turned a prediction made from reading the source into a
confirmed defect, and it is the only real-silicon evidence this work has had to go on.

## What was actually wrong

There were two separate defects here, not one.

**1. The command emitter.** The SDP-disable sequence the firmware sends before every 28C write went
through a shared helper that bypassed the address-bus remap. On 28C-family pinouts, at least one
command write went out with the write-enable line held HIGH — a documented Write Inhibit condition,
so the command never actually reached the device. The success check on that sequence was also
inverted: both relevant datasheets state the command bytes are never written back, so the old check
could only pass when the sequence had *not* been recognised at all.

**2. The page verification — the one that likely explains your actual 2024 symptom.** Per-page write
verification sampled a single byte per 64-byte page, and used that same read as both the "did the
write finish" check and the "did the data land" check. That is a conflation, not a sampling-rate
shortfall: a partial write inside a page could still report success as long as the one sampled byte
happened to match. It is now split into two separate checks — completion polling, and a per-byte
readback verification that names the failing address on a mismatch.

## Why your last re-test looked worse than 2024, and why it is not a regression

In 2024 your write *completed* — it reported success after 339 seconds, and only part of the image
was actually burned. On the beta you re-tested, it hard-fails at INIT with a timeout at `0x005555`.
That is the first fix landing halfway: the inverted check above got corrected before the emitter fix
did, which turned a silent partial write into an honest, loud refusal. Reading that as worse than
what you had before is a completely reasonable reading, and it is not what actually happened — it is
the software refusing to pretend a broken write succeeded, rather than a new problem.

## What is in the newer beta, and how to get it

`pip install --pre --upgrade firestarter` gets the host tools, and `firestarter fw --install` flashes
the matching firmware for whichever board you plug in. The three board `.hex` files are also
attached directly to the firmware release if you would rather flash by hand. Since you mentioned
doing the rev-2 mod on your shield, make sure whichever firmware you flash was built for that board —
the install command handles that matching automatically.

## What is proven, and what still is not

The lock and unlock command sequences are emitted exactly as specified — checked byte-exact by an
automated register trace across all four AT28C-family pinouts, with a measured host-side timing
figure against the datasheet's write-cycle budget. That is a software-only check, though: on this
chip family the protection state cannot be read back afterward, so a clean run only proves the
command sequence was emitted, nothing more. To be direct about it: no AT28C silicon was tested during
this work. This whole chip family is still recorded as unverified in the project's own internal
tracking. That is exactly why your re-test would be genuinely useful rather than a formality.

## The ask, in two parts — either one on its own is useful

**First, and this is the one that actually answers your question:** `firestarter write at28c256
<file>` followed by `firestarter verify at28c256 <file>`. Does the INIT abort at `0x005555` still
happen? There is no new command to learn here, and it is a direct read on whether the fix landed.
One note on this family: because it has no erase operation and each page write auto-erases
internally, a non-blank part needs the `-b` flag on the write.

**Second, and entirely optional:** `firestarter dev test at28c256` runs a full capability sweep and
can offer to file a structured report for you. Before running it, one thing worth knowing plainly:
`dev test` always writes to the chip and expects a blank or scratch part — it takes no options and
there is no way to change that. Because your own 2024 report said the input file was 32Kb of random
data, a full-device write is safe on that specific part — but please do not run it against anything
you actually care about. You do not need to do both of these; either one alone is genuinely useful.

## What happens next

This issue is staying open pending a real re-test on hardware — it is not being closed as fixed,
because nothing here has been confirmed against actual silicon. Whatever you find, a reproduction or
a clean pass, please post it here either way.
