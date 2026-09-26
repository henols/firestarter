# Project-level research snapshot — as of the v1.30 research run

**Snapshotted:** 2026-08-18, immediately after the v1.31 milestone close, before any
`/gsd-new-milestone` run for the next milestone.

## What this is

Byte-identical copies of the five project-level research documents that
`/gsd-new-milestone`'s researchers **overwrite in place**. Their live paths under
`.planning/research/` are deliberately **left untouched** — this is a copy, not a move.

| File | blob SHA at snapshot |
|---|---|
| `ARCHITECTURE.md` | `1000411aeefabad5a9605684c051c0bed20cf9a6` |
| `FEATURES.md` | `830ac30e779d4d16b62bcb8530d4fc6ac61327f4` |
| `PITFALLS.md` | `b3f648ba220a24bf16dbd759cb61616a09441c37` |
| `STACK.md` | `b496399e224ecb5b902888648a33e5d484f4ade3` |
| `SUMMARY.md` | `74f5150b4ca5119aa1dfb6c697fc3e4548f847bb` |

## Why it is labelled v1.30, not v1.31

All five were last written by commit `97b434b5` (2026-08-03) — the **v1.30** research run.
**v1.31 deliberately skipped project-level research** (operator decision 2026-08-08; its
ROADMAP says so explicitly and notes that "`.planning/research/SUMMARY.md` on disk belongs
to an older milestone"). Labelling this snapshot `v1.31-research` would attribute work to a
milestone that did not do it.

## Why a copy and not a move

`.planning/research/` is **not** a per-milestone artifact — it is a live, shared knowledge
base spanning five milestones, and it carries **25 live references** from `ROADMAP.md`,
`PROJECT.md` and `STATE.md`:

- `SUMMARY.md` — 13 references
- `questions.md` — 10 references
- `PITFALLS.md` — 1 reference
- `v1.18-AM27C020-27C-EPROM.md` — 1 reference

Moving the directory would break every one of them. Most consequentially, `questions.md`
holds the **open scoping gates that queued milestones v1.24, v1.25 and v1.26 must clear
before activation** — and it is **not** in the overwrite set, so it must stay exactly where
it is and is deliberately *not* copied here.

The eight files not copied (`questions.md`, `ECOSYSTEM.md`, `CHIP_FAMILIES.md`,
`HARDWARE.md`, `PROTOCOLS.md`, `HARDWARE_SIM_SPEC.md`, `ARCHITECTURE_PATTERNS.md`,
`v1.18-AM27C020-27C-EPROM.md`) are omitted because no research run overwrites them — they
are not at risk, and duplicating them would create two paths that could silently diverge.

## The hazard this guards, stated plainly

Milestone close does **not** archive `.planning/research/`. The next `/gsd-new-milestone`
spawns four researchers that write `STACK.md`, `FEATURES.md`, `ARCHITECTURE.md`,
`PITFALLS.md`, then a synthesizer that writes `SUMMARY.md` — all in place, no backup. This
has already happened once silently: the v1.30 run overwrote the v1.0-era versions of these
same files (`fc694e15`, 2026-05-08). Recovery was git-history-only. After this snapshot,
the pre-overwrite content is recoverable **by path**.
