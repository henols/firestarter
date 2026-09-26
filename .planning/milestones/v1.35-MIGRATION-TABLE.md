# Wiki Migration Table

This table is the auditable record of where every wiki page came from. Documentation now
lives only in the GitHub wiki (`firestarter_prom.wiki.git`); there is no in-repo source tree
mirroring it, and pages reach the wiki by cloning the wiki repository, committing the pages,
and pushing (D-19). This table exists for two consumers: a reviewer checking that a moved
file kept its content and its claims, and the Backlog 999.9 repository-rename sweep that
greps it for a source path before renaming anything.

| Source repo | Source path | Wiki page | Rendered title | Pre-deletion SHA | Moved in | Post-move edits |
|---|---|---|---|---|---|---|
| firestarter_prom | — | Home | Home | — | 167 | — |
| firestarter | firestarter/doc/PROTOCOLS.md | Programming-Protocols | Programming Protocols | a218b4f5273d14f0abd796b21ac104792de01603 | 168 | — |
| firestarter | firestarter/doc/SHIELD-REVISIONS.md | Shield-Revisions | Shield Revisions | a218b4f5273d14f0abd796b21ac104792de01603 | 168 | trimmed 2026-08-31 |
| firestarter_app | firestarter_app/doc/beta-testing-install.md | Install-Beta | Install Beta | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 | rewritten 2026-08-31 |
| firestarter_app | firestarter_app/doc/community-validation.md | Testing-Chips | Testing Chips | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 | rewritten 2026-08-31 |
| firestarter_app | firestarter_app/doc/lockable-proms.md | Lockable-PROMs | Lockable PROMs | d56424e1979edf7245cffb9ec3111c0469f5b23f | 168 | trimmed 2026-08-31 |
| firestarter_app | firestarter_app/autocomplete.md | Shell-Completion | Shell Completion | d56424e1979edf7245cffb9ec3111c0469f5b23f | 171 | — |
| firestarter_prom | — | Contributing | Contributing | — | 172 | — |
| firestarter_prom | — | Breaking-Changes | Breaking Changes | — | — | — |
| firestarter_prom | — | Chip-Database-Fields | Chip Database Fields | — | — | — |
| firestarter_prom | — | Pin-Maps | Pin Maps | — | — | — |

The Pre-deletion SHA is the sub-repo commit that created the
`gsd/v1.35-documentation-consolidation-wiki-migration` branch (Task 1 of Plan 168-01) —
`doc/` content is never edited in-repo by this phase, only deleted, so that commit's tree is
exact for every row. This is the *only* future oracle for the pre-migration text once `doc/`
is deleted (D-02): the checker reads the source side with
`git -C <subrepo> show <sha>:doc/<file>`. Task 3 of this plan proves all 13 rows resolve to
non-empty content before this plan is allowed to close.

`How-To-Edit-This-Wiki` (originally `How-This-Wiki-Is-Published`, renamed per D-21) was
**deleted from the wiki on 2026-08-31 at the operator's direction**, after the migration
closed. It was wiki-authored prose rather than a migrated `doc/` file, so it never had a
source SHA and its removal costs no migrated content. Phase 167's D-12 justification for
authoring it — pipeline scaffolding, not product documentation — is also the reason it could
go: with the publish pipeline retired there is no pipeline left to document, and the editing
conventions it carried are enforced by the checkers rather than by prose.

**Two pages were renamed on 2026-08-31, after the migration closed**, again at the operator's
direction: `Beta-Testing-Install` → `Install-Beta`, and `Community-Validation` → `Testing-Chips`
(the latter also absorbed the "help test a chip" section from the former). The `Wiki page`
column above records the *current* page name, which is what the Backlog 999.9 rename sweep
needs; the `Source path` column still records where the content came from. Both pages were
substantially rewritten for a community audience in the same change — see the honesty note
below.

`Contributing` was **authored from gh#9, not migrated**. It has no `doc/` source and
therefore no pre-deletion SHA: its text is the operator's own words from issue 9,
relocated to a wiki page rather than pulled from a deleted file. It was added in
Phase 172 under POLICY-01.

Five rows above carry `—` for `Source path` and `Pre-deletion SHA`: `Home`, `Contributing`,
`Breaking-Changes`, `Chip-Database-Fields` and `Pin-Maps`. All five were authored on the wiki
rather than migrated from a deleted `doc/` file, so none has a pre-migration source for a
footer to state. `Breaking-Changes`, `Chip-Database-Fields` and `Pin-Maps` were added on
2026-08-31 — the same day as the rewrite and trim passes the honesty note below records —
`Chip-Database-Fields` superseding the retired `Infoic-Field-Dictionary` and `Pin-Maps`
superseding both retired `Pinout-Safety-Review` and the retired `AT28C04-Adapter`'s pin map.
`git log --follow` against the wiki clone puts the earliest commit for all three at
`3cf74c0` (2026-08-31, "docs: cut the reference pages down to what a user needs"). No
`.planning/` artifact names a phase for that commit or for the two later commits that
introduced `Breaking-Changes` (`7ec9988`) and restored `Pin-Maps`'s chip pin maps
(`ff2668f`): Phase 170's own commits, recorded in
`.planning/notes/v135-phases-169-170-executed-ad-hoc.md`, touch only the three README files
and `REQUIREMENTS.md`, never a wiki page. The `Moved in` cell for these three therefore
carries `—` rather than a guessed phase number, and this gap is carried forward as its own
row in Phase 173's honesty ledger rather than silently defaulted to 170.

The seventh column, `Post-move edits`, is sourced from this file's own closing honesty note
(below): a row carries `rewritten <date>` or `trimmed <date>` when that note records an
editorial pass on the page after it reached the wiki, and `—` when the page has had none.
It exists because a footer that stated every page's content was unchanged would be false on
four of the six footer-eligible pages — `Install-Beta`, `Testing-Chips`, `Shield-Revisions`
and `Lockable-PROMs` were each edited after their migration closed, and the generated footer
must say so rather than repeat a blanket claim the honesty note itself contradicts.

## Retired from the wiki after the migration closed

These pages were migrated in Phase 168 and then removed on 2026-08-31 at the operator's
direction. Their `doc/` sources are still recoverable at the recorded SHAs — the content is
not lost, it is simply no longer published. Recorded here rather than deleted from the table,
because "what happened to this document" is the question this table exists to answer.

| Source path | Was published as | What happened |
|---|---|---|
| `firestarter/doc/AT28C04-ADAPTER.md` | `AT28C04-Adapter` | Removed; the adapter pin map and its reroute now live on `Pin-Maps`. Operator noted it may be picked up again later. |
| `firestarter_app/doc/pinout-safety-review.md` | `Pinout-Safety-Review` | Superseded by `Pin-Maps`, which is dedicated to pin maps rather than to a review. The 5 V-only guarantee it carried is restated there. |
| `firestarter_app/doc/infoic-field-dictionary.md` | `Infoic-Field-Dictionary` | Superseded by `Chip-Database-Fields`, which describes the Firestarter chip database directly instead of the upstream format it was derived from. Not a migration of the old text — the new page was written from the live database. |
| `firestarter_app/doc/package-details.md` | `Package-Details` | Removed. Its `flags` tables duplicated `Protocol-Flags`; its own half documented the DIP filter, which is machinery for excluding non-DIP parts on a programmer that only supports DIP. Nothing was worth relocating. |
| `firestarter_app/doc/sram-nvram-behavior.md` | `SRAM-and-NVRAM-Behavior` | Removed. |
| `firestarter_app/doc/protocol-flags.md` | `Protocol-Flags` | Trimmed in the 2026-08-31 editorial pass and no longer published, but the main table above still carried it as a current page from Phase 168 through Phase 172 — a defect noticed and deferred in both phases. Corrected here by moving the row rather than by restoring the page, per activation decision 4's relocate-and-correct-only posture. |
| `firestarter_app/doc/protocol-id.md` | `Protocol-ID` | Trimmed in the 2026-08-31 editorial pass and no longer published, but the main table above still carried it as a current page from Phase 168 through Phase 172 — a defect noticed and deferred in both phases. Corrected here by moving the row rather than by restoring the page, per activation decision 4's relocate-and-correct-only posture. |

`How-To-Edit-This-Wiki` was also removed — see the note above.

**MIGRATE-01's "all 12 files reachable on the wiki" was true at Phase 168's close** (wiki
commit `aa4a5c7`) and was verified there. It is deliberately no longer true: five of those
twelve are no longer published. That is an editorial decision taken after the phase closed,
not a regression in the migration, and the recorded SHAs mean any of them can be brought back.

## Removed without ever being published

These two files sat at the `firestarter_app` repository root and were never wiki pages at all —
they predate the migration and were never published anywhere on it. They were removed outright in
Phase 171 under LEGACY-04 and LEGACY-05. Their content is still recoverable at the recorded commit,
so nothing is lost; they are recorded here rather than dropped, because "what happened to this
document" is the question this table exists to answer.

| Source path | What it was | What happened |
|---|---|---|
| `firestarter_app/things.md` | A seven-line note holding the logo block, one sentence about finding avrtools on Windows, and one external link. | Deleted outright in Phase 171 under LEGACY-04 (D-05); its single fact is already answered on the wiki `Home` page, which gives the `apt` and `brew` lines and adds that avrdude also ships inside the Arduino IDE and PlatformIO. Recoverable at `git -C firestarter_app show d56424e1979edf7245cffb9ec3111c0469f5b23f:things.md`. |
| `firestarter_app/SECURITY.md` | The GSD Phase 69 security-audit record dated 2026-06-15, opening `# SECURITY.md`, `## Phase Security Audit` and `**Phase:** 69 — cli-command-surface-robustness-audit`, sitting at the path GitHub surfaces under a repository's Security tab. | Deleted outright in Phase 171 under LEGACY-05 (D-01) with no replacement; the same audit already has a canonical home in the meta repo at `.planning/milestones/v1.12-phases/69-cli-command-surface-robustness-audit/69-SECURITY.md`, from which it differs only in framing. Recoverable at `git -C firestarter_app show d56424e1979edf7245cffb9ec3111c0469f5b23f:SECURITY.md`. |

## Honesty note: HONEST-01 no longer applies to the surviving rewritten pages

HONEST-01 compared the claim-token multiset of each page against its frozen pre-deletion
source, and it passed clean for all 12 migrated pages at wiki commit `aa4a5c7` — the migration
itself upgraded no claim. That result stands as a fact about the migration.

It is **no longer a live property of `Install-Beta` and `Testing-Chips`.** On 2026-08-31, after
the migration closed, the operator directed a substantial rewrite of both for a community
audience: `Testing-Chips` absorbed the "help test a chip" section from `Install-Beta` and dropped
the ladder internals, the code references, and the summary table; `Install-Beta` lost its board
`.hex`/avrdude asset columns, its port-numbering note, and most of its flashing detail. Running
HONEST-01 against them now reports dropped tokens, and that is correct rather than a defect —
the pages deliberately no longer say what the 2026-08-30 source documents said.

Each dropped token was reviewed against the frozen source before the rewrite was published:

- `Testing-Chips` `never` 16 -> 1: thirteen were implementation detail that left with the code
  references (`never in chip_database.json`, `never a second hand-maintained field list`,
  `never a string build_db_diff can produce`). The three user-facing claims were kept in force
  with different wording — a report never changes what the project claims to support, a single
  report can never promote a chip, and promotion is a maintainer decision rather than a function
  of report volume. One claim was found genuinely missing during this review and restored before
  publication: that `--fast` reports are excluded from the two-report agreement count.
- `Install-Beta` `will not` 2 -> 0, `never` 2 -> 0, `does not` 3 -> 1: the safety-bearing ones
  survive as rewordings — the signature check still stops a mismatched flash, the smoke test
  still states it touches no chip in the socket, and the UV 256-byte slot limit moved intact to
  `Testing-Chips` as "only ever writes a small 256-byte slot".

**A second editorial pass on 2026-08-31** trimmed `Shield-Revisions`, `Protocol-ID`,
`Protocol-Flags` and `Lockable-PROMs` for a user audience — dropping git provenance, the
silkscreen alias table, the ADC band table, the `IC2_ALG`/handler columns, the unconfirmed
bit-3/6/7 guesses, and the build-database explanations. Those pages will now also report
dropped tokens against their frozen sources, for the same reason and with the same standing:
deliberate, reviewed, and not a migration defect.

**Do not re-baseline these rows to make the checker green.** The source SHAs are the frozen
oracle for what the documents said on 2026-08-30 and are still the right answer to that question.
HONEST-01 is a retired one-shot (D-03), not a standing gate; the standing guard on wiki content
is HONEST-02, which covers both pages and is green.

## Deferred, not migrating

`firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` is **not** part of the migration. The
PY32F071 work it describes exists only at the planning stage and its code is a
proof-of-concept, so publishing an install guide for it would promise a capability the
project cannot currently back. It is deferred to future wiki work alongside FUT-W-01…05
and is deliberately absent from the table above so no migration pass picks it up by
accident.

It is still **deleted** — MIGRATE-02 removes the whole `firestarter_app/doc/` directory, and
this file is inside it — so "deferred" would silently become "lost" without a recorded
oracle. Its pre-deletion SHA is `d56424e1979edf7245cffb9ec3111c0469f5b23f` (the same
branch-creation commit as the migrating app files), readable as
`git -C firestarter_app show d56424e1979edf7245cffb9ec3111c0469f5b23f:firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md`.

## The hyphen hazard

GitHub renders a hyphen in a wiki page's filename as a space in its rendered title, so a
title that needs a literal hyphen cannot be expressed as a wiki page name and must be
reworded instead. Do not work around this by substituting a look-alike, non-ASCII hyphen
character (such as U+2010) into the filename to smuggle a literal hyphen through — an
invisible non-ASCII character inside a URL that gets hand-written into other repositories'
READMEs is a worse defect than a reworded title, and it would not be visible on review.

Two of the twelve filenames above are the specific cases worth checking deliberately
when this table is filled in: `AT28C04-ADAPTER.md`, whose natural title is a part number
that already contains a hyphen, and `sram-nvram-behavior.md`, whose natural title reads
most naturally with a slash (SRAM/NVRAM) rather than a hyphen. Both need a reworded title
that a rendered wiki page can actually carry, decided deliberately rather than defaulted
into by whatever the mechanical hyphen-to-space substitution happens to produce.

**Resolved.** `AT28C04-ADAPTER.md` needs no literal hyphen in its intended title at all —
the page stem `AT28C04-Adapter` renders as "AT28C04 Adapter", which reads correctly without
the hyphen `render_title` would otherwise strip. `sram-nvram-behavior.md`'s natural
"SRAM/NVRAM" is illegal under `wiki.py`'s `check_page_names` (which rejects `/` outright),
so it is reworded to "SRAM and NVRAM Behavior", page stem `SRAM-and-NVRAM-Behavior`. Both
stems use only the alphabet `[A-Za-z0-9-]` that `_LEGAL_TARGET_RE` admits
(`tools/wiki/wiki.py:52`), so both are reachable by the only legal internal link form.
Neither uses the U+2010 look-alike workaround this section forbids.
