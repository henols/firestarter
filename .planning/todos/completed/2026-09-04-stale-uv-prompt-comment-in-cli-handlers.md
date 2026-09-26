---
title: Stale UV-prompt design-history comment at `cli_handlers.py:2295-2303` describes the reverted `260821-wna` design
date: 2026-09-04
priority: medium
blocked_by: nothing technical; deferred by Phase 175's test-only boundary — the phase is test-only and `cli_handlers.py` is product code, so this phase could not touch it without invalidating its own zero-production-diff claim. Phase 179 re-examined this todo (Q8) and found a SECOND, independent blocker: the stale sentences begin mid-line and end mid-line inside the `# ALWAYS WRITES` paragraph, so a comment-preserving edit would require REWRITING two retained comment lines — and the standing operator rule forbids writing any `#` comment into source, ever, with no plan able to override it. The only zero-comment-added fix is deleting the WHOLE `ALWAYS WRITES` paragraph, which would also delete still-accurate prose about the AT28C family, the full-device write and report persistence. This needs the operator's call on which cost to pay (rewrite two lines vs. delete accurate prose); Phase 179 deliberately paid neither. See the "Q8 mid-line boundary finding (Phase 179)" section below for the measured line numbers.
resolves_phase: 181
resolved: 2026-09-09 (plan 181-04 -- whole ALWAYS WRITES paragraph deleted outright)
status: resolved
---

# Stale UV-prompt design-history comment at `cli_handlers.py:2295-2303`

## Exact range

`firestarter_app/firestarter/cli_handlers.py:2295-2303`. CONTEXT.md's cited `2295-2305` is correct at
its start, but RESEARCH corrected the end boundary: lines 2304-2308 describe the non-UV full-device
write and are still accurate today, so the strictly-stale block is only 2295-2303. This range was
re-verified against the live file during Phase 175's execution (2026-09-04), not merely copied from an
earlier plan.

## The offending sentence, quoted

> "ALWAYS WRITES: every run writes to the chip, unconditionally. A UV-erasable EPROM is asked first,
> and quick task `260821-wna` changes what the two answers DO: yes permits the whole device to be
> written IF the chip reads blank, and otherwise writes one masked 256-byte slot; no writes one
> 256-byte slot only, unconditionally -- never read-only or non-destructive either way, and the two
> answers no longer resolve to the same window on a used chip. Off a TTY the ask is treated as a
> DECLINED prompt, not absent consent, so a single 256-byte slot is written anyway."

## Why it is stale — three independent confirmations

1. **The function's own docstring, 59 lines above, says the opposite in the present tense.**
   `_resolve_write_scope`'s docstring (`cli_handlers.py:2245-2246`) states: "UV parts get \"partial\",
   everything else \"full\". That is the whole rule, and there is no prompt on any path."

2. **The function body is a two-branch `if` with `del interactive` and no prompt at all.** There is no
   `Confirm` call, no consent branch, and no TTY-detection logic anywhere in `_resolve_write_scope` — the
   comment describes a UI flow the current implementation structurally cannot execute.

3. **`TestUVWriteHasNoPrompt` pins the absence of `Confirm` and `_default_uv_write_confirm` structurally.**
   The test suite asserts the prompt path does not exist, across every UV row in the shipped database.

The reversal is quick task `260822-aq6`, `firestarter_app` commit `2b42dac`, "retire the full-device UV
write and its prompt; report rig life" — the operator-agreed reversal of `260821-wna` (commit `57c1b8f`)
from one day earlier. The comment at 2295-2303 still describes the `260821-wna` design that `aq6`
reversed.

## Why Phase 175 deliberately did not fix it

Phase 175 (`structural-sentinel-over-derive-plan`) is test-only: its central claim, measured and sealed
in `evidence/175-05-phase-seal.txt`, is a byte-identical `git status --porcelain` over
`firestarter_app/firestarter/` and the whole firmware repository. `cli_handlers.py` is a product file.
Editing it — even to delete eight lines of a demonstrably stale comment — would put a diff in the tree
the phase's own audit asserts is empty, voiding the phase's central claim. The defect is filed here
instead, to be fixed by a later phase that is not making a zero-production-diff assertion.

## Filing context

This comment block also falls under the standing no-comments-in-source rule and under the pending
`.planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md` sweep. Per
`175-CONTEXT.md`'s `<deferred>` block, this todo is filed ALONGSIDE that sweep, not merged into it — the
sweep is a milestone-wide hygiene pass and this is a specific, dated, content-level defect.

Phase 175 pinned the behaviour the comment misdescribes structurally: `derive_plan`'s UV write-scope
ceiling (`_resolve_write_scope` returning `"partial"` for every one of the 270 UV part numbers, both
`interactive` values) is now asserted over the whole database in
`firestarter_app/tests/test_derive_plan_structural_sentinel.py`. The correct fix, when this todo is
eventually resolved, is to **delete** the stale block rather than to update it — nothing in the current
design needs a comment describing a reverted UI flow, and the file's own docstring already states the
current rule accurately.

## Q8 mid-line boundary finding (Phase 179)

Phase 179 (`179-04-PLAN.md`, Task 2) re-examined this todo before Phase 179 closed, to decide whether
this phase's own zero-comment-added rule permitted a fix here. It does not. MEASURED against the live
tree (`firestarter_app/firestarter/cli_handlers.py`, current line numbers — they have shifted from the
`2295-2303` range this todo originally cited, but the block itself is unchanged):

```
2331: # ALWAYS WRITES: every run writes to the chip, unconditionally. A
2332: # UV-erasable EPROM is asked first, and quick task 260821-wna
2333: # changes what the two answers DO: yes permits the whole device to be
2334: # written IF the chip reads blank, and otherwise writes one masked
2335: # 256-byte slot; no writes one 256-byte slot only,
2336: # unconditionally -- never read-only or non-destructive either way, and
2337: # the two answers no longer resolve to the same window on a used chip. Off
2338: # a TTY the ask is treated as a DECLINED prompt, not absent consent, so a
2339: # single 256-byte slot is written anyway. Every OTHER family --
2340: # explicitly including this milestone's own AT28C family, an
```

The stale sentences **begin mid-line**: line 2331 opens `# ALWAYS WRITES: every run writes to the
chip, unconditionally. A` — the trailing `A` is the start of the next (stale) sentence, not the end of
a clean one. They **end mid-line**: line 2339 reads `# single 256-byte slot is written anyway. Every
OTHER family --` — the stale content ends at `anyway.` but the SAME physical line continues straight
into `Every OTHER family --`, which is the opening of still-accurate prose about the AT28C family
(lines 2339-onward describe the non-UV full-device write path, confirmed accurate by this todo's
original filing).

Because the stale and accurate content share physical lines at both boundaries, there is no edit that
removes only the stale text without rewriting at least two retained comment lines (2331 and 2339) to
re-terminate the sentences that survive. This project's standing operator rule is that **no `#`
comment is written into source, ever, by any plan** — including a corrective rewrite of an existing
line. The only edit that adds zero comment content is deleting the entire `ALWAYS WRITES` paragraph
(lines 2331-2339+), which would also delete the still-accurate AT28C-family, full-device-write and
report-persistence prose this todo's own filing confirmed was correct.

**This is an operator decision, not a mechanical one:** rewrite two retained comment lines (violates
the zero-comment rule to fix a stale one), or delete accurate prose along with the stale sentences
(loses correct documentation to remove incorrect documentation). Phase 179 deliberately paid neither
cost and left `cli_handlers.py` byte-unchanged — confirmed across the whole phase by
`git diff 835baba..HEAD --name-only -- firestarter/cli_handlers.py` reporting zero files.

## RESOLUTION (2026-09-09)

Fixed by plan `181-04`, which deleted the whole `# ALWAYS WRITES` paragraph outright rather than
rewriting it — the fix option Phase 179's Q8 finding above declined to choose. That finding
established the block could not be edited without rewriting two retained comment lines (2331 and
2339, which begin/end mid-sentence shared with still-accurate prose), forbidden by this project's
standing no-`#`-comments rule. A pure deletion of the whole paragraph is not a rewrite and cannot
exceed the comment-census baseline. The two blockers this todo recorded dissolve together: D-09
deletes `_resolve_write_scope` and its docstring in the same phase (removing the other half of the
contradiction this comment created), and Phase 175's test-only-boundary deferral no longer applies
because this phase is not making a zero-production-diff claim. The still-accurate AT28C-family,
full-device-write and report-persistence prose this todo's own filing confirmed correct is not
recoverable from the deleted comment; it is derivable from the code, which is where this project's
rule says it belongs.
