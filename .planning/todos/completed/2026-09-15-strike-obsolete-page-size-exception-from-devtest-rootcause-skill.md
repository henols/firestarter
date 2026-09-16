---
created: 2026-09-15T13:35:00Z
title: Strike the obsolete _PAGE_SIZE_BY_PART exception paragraph from devtest-rootcause SKILL.md
area: skills
completed: 2026-09-16
resolution: struck after phase 194 closed
files:
  - .claude/skills/devtest-rootcause/SKILL.md (lines 63-66, the "One exception exists:" blockquote)
  - firestarter_app/tools/build_db.py (the generator that no longer carries the symbol)
---

# Strike the obsolete page-size exception paragraph

`.claude/skills/devtest-rootcause/SKILL.md` lines 63-66 carry this blockquote, directly
under **The proof rule**:

> One exception exists: `_PAGE_SIZE_BY_PART` (`build_db.py:114`) adds `page_size` from
> `[CITED:]` **datasheets**, not from `infoic.xml` — the exact shape this rule forbids.
> Do not extend it or add siblings to it. Upstream carries `infoic_page_size_raw`, which
> is the principled seam if page size ever needs revisiting.

## Why this is not a stale line number

`_PAGE_SIZE_BY_PART` no longer exists anywhere in `build_db.py`. Commit `859109d`
(`feat(194-01): emit the real page size for every upstream-native 0x05 row`, 2026-09-15
13:27:20) deleted it — confirmed with `git log -S'_PAGE_SIZE_BY_PART' -- tools/build_db.py`.

Page size now derives from `infoic_page_size_raw`, which is **exactly the "principled
seam" this paragraph names as the alternative**. So phase 194-01 did the thing the
paragraph asked for, and in doing so made the paragraph describe a mechanism that is gone.

The paragraph is therefore obsolete, not mis-cited. Repairing the line number would
produce a confidently false citation pointing at a deleted symbol — worse than the
staleness it set out to fix.

## Why it was not fixed on 2026-09-15

Quick-batch `260915-idi` rewrote this file in Strict ASD-STE100. The `_PAGE_SIZE_BY_PART`
citation repair was in its original scope, and `gsd-plan-checker` blocked it on exactly
the grounds above. Phase 194-01 was still executing in the same working tree at the time,
so the replacement mechanism was actively changing. The operator decided to strike the
paragraph once 194 settles rather than document a moving target.

Lines 63-66 were frozen byte-identical during that rewrite, and a gate leg asserted it.
None of `ste-lint.py`'s findings falls in that range, so freezing it cost nothing.

## What to do once 194 closes

1. Re-read the page-size path in `build_db.py` and confirm the mechanism has settled.
2. Delete the blockquote. With the exception gone, **The proof rule** above it stands
   unqualified — which is now simply true, and is the stronger statement.
3. If some new exception has appeared, document that one instead; do not resurrect this text.
4. Re-run `python3 /home/vscode/.claude/skills/asd-ste100/scripts/ste-lint.py` on the file
   and confirm it still exits 0.

## Resolution — 2026-09-16

Phase 194 closed. `_PAGE_SIZE_BY_PART` is confirmed absent from `build_db.py`, and
page size now decodes from the upstream attribute (`raw_page_size`, emitted as
`infoic_page_size_raw`) — the seam the struck paragraph itself named.

The blockquote is gone. **The proof rule now stands with no exceptions**, which is the
stronger statement, and the replacement text says so while recording that page size was
the last exception and must not be reintroduced as a per-part table.

Two further dangling references turned up in `scripts/diff_db.py` — its `PGSZ_PAGE_SIZE`
allowlist entry described the Phase 94 mechanism in the present tense. Those were not
deleted: the entry is a historical record of an accepted delta, so it was re-framed as
past tense with an explicit supersession note. It also now warns that the rule can match
a far wider set of chips than the Phase 94 list, because the gate is no longer a
per-part table.
