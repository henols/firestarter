---
created: 2026-09-15T13:35:00Z
title: Strike the obsolete _PAGE_SIZE_BY_PART exception paragraph from devtest-rootcause SKILL.md
area: skills
blocked_on: phase 194-01 settling (page-size mechanism is mid-change)
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
