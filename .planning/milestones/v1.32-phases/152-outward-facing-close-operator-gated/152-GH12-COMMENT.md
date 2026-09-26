Following up again here. `firestarter dev sdp <chip> enable|disable` is gone now — it was removed in
the release right after my last note on this thread — and I want to close the loop honestly rather
than let the release notes speak for themselves.

**What changed**

`dev sdp <chip> enable|disable` is gone. The two halves don't survive equally, and I'd rather be
plain about that than let the release notes imply otherwise:

- **`disable`'s behaviour survives, and you no longer need a command for it.** Unlocking is already
  what `write` does by default on every protocol-`0x0D` part — it auto-unlocks unless you pass
  `--skip-sdp-unlock`. So `dev sdp disable` was genuinely redundant, not merely dropped.
- **`enable` is withdrawn, with no replacement — for a second release now.** If you want a part
  deliberately left protected, there is still no supported way to do it. The ask is half-answered
  for a second release: deliberate protection stays tracked as Backlog 999.28, and I'm not going to
  promise a version for it.

This isn't the "enable/disable" you asked for. You asked for both, and what you get is one of them
automatically and none of the other. There's a second limitation worth stating: the protection bit on
these parts can't be read back, so even when a part is protected, nothing can show you that it is.

**What did get better**

- **`lock-status`.** The honest answer for this chip family is usually a refusal, and that's the
  feature, not a limitation of it: `firestarter dev lock-status <chip>` either reports a real
  protection state read back from the chip, or it refuses and names why — an actionable reason, not a
  guess. It's beta-channel only right now, and it needs firmware that matches: install the pre-release
  and run `firestarter fw --install`, or the command won't be recognized at all.
- **The write path no longer blank-checks before writing.** On this protocol, a page write auto-erases
  internally as part of the write itself, so a pre-write blank check was never actually protecting
  you — it's gone. A standalone erase step exists now too, using the manufacturer's own software erase
  sequence for this protocol rather than the 12 V-on-OE hardware path some older programmers use; the
  software path was chosen precisely because it carries no over-voltage hazard on this pinout. The
  standalone blank check is unaffected and still exists as its own step.
- **`dev test` reports now say which firmware they ran on.** That's new since the last time I asked
  you to test, and it's part of why the ask below is worth making at all.

I know this is the second time in a row I'm asking you to install a fresh pre-release and run
`dev test` on this thread — the last time pointed at a build whose reports couldn't say which
firmware they'd run on, and whose write step failed on a non-blank part for a reason that's since
been removed. I'd rather say that plainly than pretend this is the first ask.

**This is where I need help, and it's the honest reason `dev test` exists**

I don't have most of these parts. No AT28C part was tested at any point in v1.32 — I can't buy one
of everything, and a lot of what the database claims about a chip has never been checked against the
actual silicon — including the AT28C family in this thread. That's not a gap I can close on my own
bench.

`dev test` is built for exactly that. If you have a part — the AT28C from this thread, or anything
else — you'll need two things first, and both matter: the pre-release install, and a firmware update.
The write-path change lives in the firmware, and the host's test step doesn't send an override flag,
so on older firmware the old failure reproduces exactly as it did before.

```
pip install --pre firestarter
firestarter fw --install
firestarter dev test <chip>
```

It derives what that chip's protocol supports, runs each operation as an independent step, and writes
a diagnostic report you can file straight back to this repo. Non-destructive by default; add
`--destructive` only on a chip you're willing to risk, and it'll tell you what it skipped without it.

One run from a part in someone's hand tells us more than anything I can derive from the database. If
the lock doesn't actually hold on real AT28C silicon, a report is how we find out.
