# Host app prerelease — SDP command retirement + a testable leg for the lock

`pip install --pre --upgrade firestarter`

This GitHub release carries no attached files — it is a tag-and-marker page only. PyPI is the
distribution channel for the host app; the command above pulls it. The matching firmware for this
release is published separately, and its `.hex` files are what `firestarter fw --install` pulls
when you update your board.

## Removed

`firestarter dev sdp <chip> enable|disable` is gone.

- **`disable` is gone because it is genuinely redundant.** `write` already auto-unlocks on every
  protocol-`0x0D` write by default (declinable via `--skip-sdp-unlock`), so `dev sdp disable` was
  sending a command sequence `write` already sends on its own.
- **`enable` is withdrawn, with no replacement in this release.** There is currently no supported
  way to deliberately protect an SDP part. On this chip family the protection bit cannot be read
  back afterward either, so even if a replacement existed today there would be no way to confirm
  the result. The design for a replacement is settled and tracked as **Backlog 999.28** — it is
  queued, not shipped, and no version is promised for it here.

## `dev test` changed shape again, and the lock now has an oracle

`firestarter dev test <chip>` still takes no options. Across the 43 SDP-capable chips on this
protocol (of 84 total), a run now derives a six-step leg: write a baseline pattern and verify it,
lock the part, send a write meant to be blocked, read the chip back and check it against the
baseline, unlock the part, then write and verify once more so the chip is left in a plain writable
state. On the other 41 chips on this protocol, the same six steps are reported as not applicable,
each carrying the reason.

This is the first oracle this behavior has ever had — a write that unexpectedly succeeds during
the blocked step is reported as a failure, never as skipped or not applicable. **It remains
untested on real AT28C silicon; this protocol stays recorded as unverified in the project's own
validation ledger, and no chip's support status changed in this release.**

## Also in this release

A stable-channel install of `firestarter dev` now exposes only the `read` and `test`
subcommands — every other `dev` subcommand is not merely left out of `--help` on a stable install,
it is not registered at all and refuses by name if invoked anyway. A beta/prerelease install keeps
every `dev` subcommand exactly as before.

## What is proven, and what is not

The lock and unlock command sequences are emitted exactly as specified, and the plan-derivation
and read-back-comparison logic above are both exercised end to end in this project's own native
test environment. What none of that establishes is whether the lock actually stops a write on real
hardware — that claim is reachable only from a report filed by someone running this release
against a physical AT28C part. **No AT28C silicon was tested during this milestone**, and nothing
in this release changes that.

## The ask

If you have AT28C hardware, running `firestarter dev test <chip>` and filing the report it offers
is the single most useful thing you could send back — it is exactly what would close this gap.
