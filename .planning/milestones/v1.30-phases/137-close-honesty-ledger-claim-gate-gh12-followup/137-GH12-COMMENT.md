Following up here, because `firestarter dev sdp` was named in this thread and in the `3.0.0b14`
release notes, and it's being removed.

**What's changing**

`dev sdp <chip> enable|disable` is gone. The two halves don't survive equally, and I'd rather be
plain about that than let the release notes imply otherwise:

- **`disable`'s behaviour survives, and you no longer need a command for it.** Unlocking is already
  what `write` does by default on every protocol-`0x0D` part — it auto-unlocks unless you pass
  `--skip-sdp-unlock`. So `dev sdp disable` was genuinely redundant, not merely dropped.
- **`enable` is withdrawn, with no replacement in this release.** If you want a part deliberately
  left protected, there is currently no supported way to do it. The design for one is settled and the
  work is queued, but it is not in this release and I'm not going to promise a version for it.

This isn't the "enable/disable" you asked for. You asked for both, and what you get is one of them
automatically and none of the other. There's a second limitation worth stating: the protection bit on
these parts can't be read back, so even when a part is protected, nothing can show you that it is.

**What did get better**

The lock is now *checkable*, which it never was before. `dev test` on an SDP-capable part derives a
leg that writes a known pattern, locks the part, attempts a write without unlocking, and reads back
to see whether the contents changed — reporting `HELD` / `NOT-HELD` / `NOT-RUN` with a reason. If a
lock silently fails to hold, that leg is built to surface it rather than let the run look clean.

**This is where I need help, and it's the honest reason `dev test` exists**

I don't have most of these parts. No AT28C silicon was tested during this milestone — I can't buy
one of everything, and a lot of what the database
claims about a chip has never been checked against the actual silicon — including the AT28C family in
this thread. That's not a gap I can close on my own bench.

`dev test` is built for exactly that. If you have a part — the AT28C from this thread, or anything
else:

```
firestarter dev test <chip>
```

It derives what that chip's protocol supports, runs each operation as an independent step, and writes
a diagnostic report you can file straight back to this repo. Non-destructive by default; add
`--destructive` only on a chip you're willing to risk, and it'll tell you what it skipped without it.

One run from a part in someone's hand tells us more than anything I can derive from the database. If
the SDP lock doesn't actually hold on real AT28C silicon, a report is how we find out.
