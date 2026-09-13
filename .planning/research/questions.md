# Open research questions

## What PyPI version-share decay looks like for `firestarter`, and what threshold makes claiming `henols/firestarter` safe

**Filed:** 2026-09-13 · **Source:** `/gsd-explore` repo-rename session · **Blocks:** Backlog 999.9 (gh#2), Phase C — see `.planning/seeds/SEED-claim-firestarter-slug.md`

Backlog 999.9's destructive step must be gated on adoption rather than on a calendar date,
and there is currently no instrument for that gate.

**Established facts** (measured 2026-09-13, not researched):

- `pip install firestarter` resolves to **2.0.7**; the entire `3.0.0bNN` line is prerelease
  and invisible to a default install.
- `origin/main` is 2.0.7-era code, **948 commits** behind `origin/beta`.
- The app performs **no self-version check** — there is no telemetry and no upgrade nag.

**To answer:**

1. What does `pypistats` (or the PyPI BigQuery dataset) expose for per-version download
   share of `firestarter`, and how far back does it reach? Is per-version granularity
   available without BigQuery credentials?
2. How quickly has a past stable displaced its predecessor for this package? The 2.x
   release history gives several natural experiments.
3. What share threshold and observation window is a defensible gate? State it as a number,
   with the reasoning for that number.
4. Is there a better proxy than download share — GitHub release-asset download counts on
   the firmware repo would measure `fw --install` traffic directly, which is the exact
   behaviour at risk. Are those counts retrievable per release, and do they distinguish
   client versions?

**Constraint on the answer:** it must be honest that no instrument measures installed base
directly. A download-share gate is a proxy, and the residual — users who never upgrade —
cannot be eliminated by any threshold. The deliverable is a defensible number plus a plain
statement of what it does not cover.
