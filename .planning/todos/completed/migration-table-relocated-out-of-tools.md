---
id: migration-table-relocated-out-of-tools
created: 2026-09-08T00:00:00Z
title: Relocate MIGRATION-TABLE.md out of tools/ — it is a closed-milestone record, not tooling
resolved: 2026-09-08 (git mv + scripted remap of 324 citations; round-trip oracle green)
status: resolved
area: meta
files:
  - .planning/v1.35/MIGRATION-TABLE.md (the file to move; the only survivor of 5426d7ef)
  - .planning/v1.35/ (proposed destination — the milestone whose output it is)
  - .planning/ROADMAP.md, .planning/STATE.md (live records that cite it)
  - .planning/milestones/v1.35-REQUIREMENTS.md, .planning/milestones/v1.35-ROADMAP.md
  - .planning/v1.35/CLOSE-RECORD.md, .planning/notes/v135-wiki-only-reversal.md
  - .planning/phases/167-*, 168-*, 171-*, 172-*, 173-*, 174-* (archived citers)
---

## Problem

Commit `5426d7ef` (2026-09-02) retired the wiki checkers, deleting `wiki.py`,
`honest01_claims.py`, `honest02_truth.py`, `provenance_footers.py`, `dispatch_mirror.py`,
`selftest.sh`, `claim-allowlist.json` and `claim-vocabulary.json`. `MIGRATION-TABLE.md` was left
behind as the sole occupant of `tools/wiki/`.

It is not tooling. It is the provenance record of the v1.35 wiki migration, and that milestone is
closed. Operator's call: *"it is done and does not belong in tools"*.

It must **not** be deleted — it is cited from live records (`ROADMAP.md`, `STATE.md`,
`v1.35/CLOSE-RECORD.md`, `MILESTONES.md`, `RETROSPECTIVE.md`, `PROJECT.md`) as well as archives.

## Measured citation surface

- **286** occurrences of the path form `.planning/v1.35/MIGRATION-TABLE.md` across **85** `.md` files
  under `.planning/`.
- **221** further bare `MIGRATION-TABLE` mentions with no path prefix — these need **no** change.
- Several citations are **line-anchored**: `MIGRATION-TABLE.md:15`, `:18-19`, `:20`, `:45-58`,
  `:52-53`, `:68-80`, `:104-105` (seen in `171-PATTERNS.md`, `171-03-PLAN.md`,
  `171-03-SUMMARY.md`). A pure `git mv` leaves file content byte-identical, so **every line
  anchor stays valid** — only the directory prefix changes.

## Approach

1. `git mv .planning/v1.35/MIGRATION-TABLE.md .planning/v1.35/MIGRATION-TABLE.md` — content untouched,
   so line anchors survive. `tools/wiki/` then disappears entirely.
2. **Scripted** path remap of the 286 path-form citations, `.planning/v1.35/MIGRATION-TABLE.md` ->
   `.planning/v1.35/MIGRATION-TABLE.md`. Do this with a script, not by hand — the citation-repair
   discipline requires a round-trip oracle, and 85 files is past the hand-edit threshold.
3. Round-trip oracle: after the remap, assert that **zero** files contain the old path and that
   the new path resolves to an existing file from every citing file's perspective.

## Precedent nuance to record in the SUMMARY

Before the move the 286 citations are `.planning/` -> **source**, which the repair rule covers:
never accept staleness, archives included. After the move they become `.planning/` ->
`.planning/`, which is historical-by-intent and explicitly **not** subject to future repair. So
this remap is a one-time transition across that boundary. State that explicitly, otherwise a
later reader may see 286 `.planning/`->`.planning/` citations and conclude the repair rule was
misapplied.

## Acceptance

- [ ] `tools/wiki/` no longer exists. `tools/` then contains `catalog/` and, until the
      re-key checker retirement todo lands, `rekey/` — which is itself slated for removal
      (see `2026-09-08-retire-the-rekey-cross-tree-checker.md`), leaving `catalog/` alone.
- [ ] `.planning/v1.35/MIGRATION-TABLE.md` exists and is byte-identical to the old file
      (`git log --follow` shows the rename; `git show HEAD~1:.planning/v1.35/MIGRATION-TABLE.md | diff - .planning/v1.35/MIGRATION-TABLE.md` is empty).
- [ ] `/usr/bin/grep -rn "tools/wiki/MIGRATION-TABLE" .planning | wc -l` is **0**.
- [ ] `/usr/bin/grep -rn "tools/wiki" .planning --include='*.md' | wc -l` — the remaining hits are
      only historical references to the *deleted checkers*, not to the table. Enumerate them in
      the SUMMARY rather than repairing them: they cite files `5426d7ef` removed, and rewriting
      those would destroy the retirement evidence.
- [ ] The count of line-anchored `MIGRATION-TABLE.md:<N>` citations is unchanged, and each anchor
      still lands on the line it names.
- [ ] No CI gate references `tools/wiki` — confirmed: `.github/workflows/` holds only
      `catalog-sync-check.yml` and `rekey-ledger-check.yml`.
- [ ] Record gates re-run clean (allow 300s — STATE.md carries a very long line).

## Note

Use `/gsd-quick` for this. It is a tracked-file change with a real oracle, not an inline edit.

## RESOLUTION (2026-09-08)

`git mv tools/wiki/MIGRATION-TABLE.md .planning/v1.35/MIGRATION-TABLE.md`, then a scripted remap.

| | |
|---|---|
| Content | **byte-identical** after the move (193 lines), so all **33** line-anchored `MIGRATION-TABLE.md:N` citations stay valid |
| Path citations remapped | **324** across **87** files |
| Old path remaining in `.planning/` | 0 live citations. Two literal occurrences survive **in this file only** — the `git mv` command recorded below, and the criterion's own grep string at line 66. Both are historical records of what was run, not references to a moved file, so criterion 3 above is self-defeating as written and is discharged by this row instead. |
| `tools/` now contains | `catalog/` only — `codegen.py`, `messages.toml`, `sync_to_subrepos.sh` |

**Deliberately NOT remapped:** roughly 1,150 citations to the *deleted* checkers
(`tools/wiki/wiki.py` ×411, `selftest.sh` ×313, `dispatch_mirror.py` ×92,
`provenance_footers.py` ×83, `honest01_claims.py`/`honest02_truth.py` ×58 each,
`claim-allowlist.json` ×41, bare `tools/wiki/` ×192). Those name files `5426d7ef` removed on
2026-09-02. Rewriting them would destroy the evidence of what the retirement removed — they are
historical by intent, exactly as the plan specified.

**Precedent note, as planned:** before the move these 324 were `.planning/` -> source citations,
which the repair rule covers. They are now `.planning/` -> `.planning/`, which is historical by
intent and explicitly NOT subject to future repair. This remap was the one-time transition across
that boundary; a later reader seeing 324 same-tree citations should not conclude the rule was
misapplied.

`tools/rekey/` is also gone as of the same day — see
`rekey-cross-tree-checker-retirement.md`. `tools/` is now `catalog/` alone.
