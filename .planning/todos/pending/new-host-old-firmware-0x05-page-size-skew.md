---
created: 2026-09-15T00:00:00Z
title: "New host / old firmware skew corrupts the 9 previously under-sized 0x05 parts silently"
area: both
resolves_phase: unassigned
files:
  - firestarter_app/firestarter/page_size_gate.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/channel.py
  - firestarter_app/firestarter/serial_comm.py
---

## Problem

Phase 194 (D-12) delivers a per-chip `page_size` on the wire for every protocol `0x05` part and
makes the firmware refuse a write when it cannot resolve one. The host does **not** gate a
protocol `0x05` write on the connected firmware's version. Deliberately, per D-12: the host
already sends `page-size` on every write today with zero code change (Phase 149's seam), and
adding a version gate for this phase's fix would be a separate, unbounded piece of work.

## The mechanism

A host carrying this phase's database resolves the real page size (e.g. `128` for `AT29C512`, one
of the 9 previously under-sized parts) and sends `page-size: 128` on the wire. Firmware older than
this phase (pre-`194-01`) has no `page_size` consumer on the `0x05` write path: it silently ignores
the field and re-derives the old, wrong capacity-bracket value (`64` for `AT29C512`). The result is
exactly the silent corruption this milestone exists to end (D-1) — a write against one of the 9
still corrupts every other page, the firmware never rejects it (the old code path has no refusal),
and the operator still sees `successful`.

This is a **regression path that only opens once the host is upgraded ahead of the firmware** — a
host at this phase's version, paired with firmware still at `3.0.0b22` or earlier. It does not
affect a host+firmware pair that upgrades together, and it does not affect any of the 18
already-correct parts (their derived and real pages already agreed).

## The caveat for whoever picks this up

**The host's own firmware version probe cannot resolve this precisely.** `_probe_port`'s version
regex (`[\d.x]+`) truncates the prerelease suffix, so the host cannot distinguish firmware `b11`
from `b12` from `b22` from whatever build first ships `194-01`'s consumption fix — only the
numeric `major.minor.patch` triple is visible to the host today. Any version boundary this fix
introduces must therefore be decided on the numeric triple alone, which means either:

- bumping to a new numeric version specifically to mark the boundary (a release-process decision,
  not a code change), or
- widening the probe to preserve the prerelease suffix first, so a boundary can be drawn precisely
  against a `b`-numbered prerelease instead of only a numeric release.

Neither is this phase's decision to make.

## What would close it

A host-side pre-write gate, keyed on the connected firmware's version (once precisely resolvable),
that refuses or warns before a protocol `0x05` write when the connected firmware predates the
`page_size`-consumption fix — mirroring the existing fail-closed pattern in
`firestarter/page_size_gate.py` (194-05) and `firestarter/flash4_erase_gate.py`, but keyed on
firmware version rather than on database content.

## Filed by

Phase 194 (real page size reaches the firmware), D-12, Plan 06.
