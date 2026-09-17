---
created: 2026-09-17T20:15:00Z
title: A fired seed keeps matching /gsd-new-milestone's SEED-*.md glob
area: tooling
resolves_phase:
files:
  - .planning/seeds/SEED-claim-firestarter-slug.md (status: fired)
---

## Problem

`/gsd-new-milestone` globs `.planning/seeds/SEED-*.md` by filename and does not read each
seed's `status:` frontmatter. `SEED-claim-firestarter-slug.md` carries `status: fired` — its
trigger fired on 2026-09-14 and it can never fire again — yet it will keep surfacing as a
candidate every time a new milestone is created.

Phase 196 decision D-15 deliberately kept the seed at its canonical path, so moving or
renaming it is not the fix.

## Why it was not fixed in Phase 196

Recorded in `.planning/phases/196-adoption-instrument-disposition/196-CONTEXT.md`: this is GSD
tooling behaviour, not a Phase 196 deliverable. The phase's scope was the adoption instrument's
disposition, and D-15 fixed the seed's location against exactly this kind of drive-by edit.

## Options

- Teach the milestone-creation glob to skip seeds whose frontmatter `status:` is `fired`.
- Or give fired seeds a distinguishing filename convention the glob can exclude — but this
  conflicts with D-15, which keeps this seed at its canonical path.

The first option is the one that does not disturb a frozen record.
