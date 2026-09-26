---
created: 2026-08-20T00:00:00Z
title: "All 13 seeds are invisible to /gsd-new-milestone -- explore.md writes {slug}.md, new-milestone.md globs SEED-*.md, and the miss is SILENT"
area: tooling
resolves_phase: unassigned
files:
  - .claude/gsd-core/workflows/new-milestone.md
  - .claude/gsd-core/workflows/explore.md
  - .claude/gsd-core/workflows/plant-seed.md
  - .planning/seeds/
---

## Problem

Seed surfacing at milestone start is **broken repo-wide and fails silently closed**. Two GSD
workflows disagree on the seed filename convention, and the consumer treats a total miss as
"no seeds exist":

| workflow | seed path | matches consumer glob? |
|---|---|---|
| `plant-seed.md:65` (**producer**) | `.planning/seeds/SEED-{PADDED}-{slug}.md` | **yes** |
| `explore.md:85,113` (**producer**) | `.planning/seeds/{slug}.md` | **NO** |
| `new-milestone.md:54` (**consumer**) | `ls .planning/seeds/SEED-*.md` | — |

`new-milestone.md:56` then says: *"**If no seed files exist:** Skip this step silently — do not
print any message or prompt."* So the glob returning nothing is indistinguishable from having
no seeds, and nothing is ever reported.

**All 13 seeds in `.planning/seeds/` use the bare-slug form** — i.e. every one came from
`/gsd-explore` (or another `{slug}.md` producer), and **not one has ever been surfaced at a
milestone start**:

```
27c-algorithm-fidelity-param-table-refactor    logging-macro-derives-response-code
binary-command-protocol                        mask-rom-24pin-read-support
bus-config-clean-redesign                      protocol-first-architecture-rebuild
community-chip-validation-command               py32f071-no-external-tool-fw-install
db-numeric-values-simplification                rev22-3pin-header-2516-family-support
jumper-settings-per-pin-map                     voltage-reading-whitebox-calibration
lock-status-command-hand-curated-protection-table
```

`ls .planning/seeds/SEED-*.md` → `No such file or directory`. Verified 2026-08-20.

This is the same failure class as the gates already recorded in
[[reference_firmware_renames_break_host_source_scanning_gates]] and
[[reference_check_permitted_claims_here_resolves_wrong_phase_dir]]: a **locator mismatch that
fails without a diagnostic**, so the absence of output reads as a clean pass.

## Why it has gone unnoticed

The seeds that actually got acted on were reachable by a *different* route — a hand-written
citation from a `ROADMAP.md` entry. The v1.25 line cites
`seeds/rev22-3pin-header-2516-family-support.md` inline, and that is why it is live. Seeds
without a ROADMAP citation have no path into planning at all.

Contrast **todos**, which *are* surfaced: `new-milestone.md:551` reads
`.planning/todos/pending/*.md | head -50` (24 present, within the cap) and tags them with
`resolves_phase` after the roadmap is written. That channel works — which is why this defect is
filed as a todo rather than as a seed.

## Fix options — none is free, pick deliberately

1. **Fix the consumer glob** to `.planning/seeds/*.md` (one line, `new-milestone.md:54`). Most
   correct, but `.claude/gsd-core/` is **vendored** and `/gsd-update` would overwrite it. Needs
   either an upstream fix or a documented re-patch step. Also make the miss non-silent: if the
   directory is non-empty but the glob is, that must *say so* — silence is what hid this.
2. **Rename all 13 seeds** to `SEED-NNN-{slug}.md`. Matches `plant-seed.md`, survives
   `/gsd-update` — but **breaks the hand-written path citations**: `ROADMAP.md`'s v1.25 entry
   cites `seeds/rev22-3pin-header-2516-family-support.md`, and
   `notes/onerom-pinout-external-corroboration.md` cites `seeds/mask-rom-24pin-read-support.md`.
   Grep every citation before renaming; a rename that leaves dead links trades a silent miss
   for a silent 404.
3. **Fix `explore.md`** to write the `SEED-` prefix. Stops the bleeding for *future* seeds but
   leaves the existing 13 invisible, so it is a partial fix at best and must be paired with (2).
4. **Cite each live seed from a ROADMAP line.** Works with today's tooling and needs no vendored
   edit, but it is manual and does not scale — and it is precisely the workaround whose absence
   caused this.

Recommended: (1) + (3) upstream, with (2) only if the citation sweep comes back clean.

## Do not "fix" this by deleting seeds

A stale-looking seed here is not evidence the idea was dropped — it is evidence the idea was
**never presented**. Judge each of the 13 on its merits at the next milestone start, after the
surfacing works. Several predate the currently-active milestone by months.
