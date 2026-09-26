# Phase 168 — Deferred Items

Out-of-scope discoveries logged during execution, not fixed per the executor's
scope-boundary discipline (fix only what the current task's changes directly
caused to break).

## Plan 168-04, Task 1 — two orphaned C++ fixture files

Deleting `firestarter_app/tests/test_dispatch_mirror.py` (its sole consumer)
leaves two committed fixture files unreferenced by any Python code in the
repository:

- `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp`
- `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp`

Both were SWEEP-07 planted-violation controls consumed exclusively by
`test_dispatch_mirror.py`'s `test_planted_missing_hex_is_detected` and
`test_planted_comment_only_hex_is_NOT_detected`. No test currently fails as a
result of their being orphaned (nothing scans `tests/fixtures/` for unused
files), so this is tidiness, not a defect: leaving them does not violate any
of plan 168-04's acceptance criteria, and 168-04's `files_modified` does not
name them.

Recommended follow-up: delete both files in whichever later 168 plan next
touches `tests/fixtures/` (e.g. a plan doing broader test-tree cleanup), or
in a dedicated hygiene pass after the phase closes.

## Plan 168-05, Task 2 — `wiki.py links` false-positives on `Lockable-PROMs.md`'s external reference-style links

`Lockable-PROMs.md` (migrated byte-for-byte from `lockable-proms.md` except for
the title insertion and stamp) carries 8 standard Markdown reference-style
citations to external datasheet URLs — `([Infineon][1])`, `([macronix.com][4])`,
`([Microchip][6])`, etc., each resolved by a `[N]: https://...` definition
further down the same file (lines 51, 106, 119, 130, 248, 273, 304; definitions
at 392–399). `wiki.py`'s `extract_internal_links` (`tools/wiki/wiki.py:69-90`)
treats **any** `[text][ref]` bracket pair as an attempted internal link — it has
no way to distinguish a reference-style external citation from a malformed
internal link attempt — so `check_link_forms` reports all 8 as
`illegal internal link form`, even though every one resolves to a real external
URL and none was ever intended as a wiki-internal link.

This is a pre-existing property of the source document surfaced for the first
time by migration (the checker never ran against this content before, since it
lived in the app repo, not the wiki). It was not introduced by this plan's
edits (title + stamp only), does not affect this plan's own acceptance criteria
(Task 2's `<verify>` only counts `orphan` occurrences; the top-level plan
`<verification>` only requires the `links` run to exit 1 with 12 orphan lines,
both satisfied regardless), and fixing it would mean rewriting the 8 citations
into inline-link form — content-shape editing beyond this plan's bounded edit
set (title / unopenable planning paths / stamp / the three named cross-file
links). Left as-is; not fixed here.

Recommended follow-up: whichever later plan owns the "clean" (post-Home-rewrite)
`wiki.py links` run against the live clone (168-13's workflow repoint, or a
dedicated hygiene pass) should either convert `Lockable-PROMs.md`'s 8
reference-style external citations to inline `[text](url)` form, or teach
`extract_internal_links` to recognize a `[N]: <url>` reference-definition block
and skip reference-style links whose `ref` resolves to one — whichever the
610-line `wiki.py` checker's owning plan judges cheaper.

**Resolved by plan 168-08.** `extract_internal_links` now resolves a
`[text][ref]` pair against a `[ref]: <url>` reference-definition block found
anywhere in the same page and skips it when the resolved target is external
(`http://`, `https://`, `mailto:`); a reference-style link whose `ref` does not
resolve, or resolves to a non-external target, is still flagged. `wiki.py links`
against the live clone (master @ 9d7e9bc) reports zero errors on
`Lockable-PROMs.md`. Two new selftest cases
(`reference_style_external_citation_exit_0`, `dotdir_ignored_exit_0`) cover the
fix and a second, previously-unnoticed defect discovered in the same pass: a
real git clone's `.git` directory was unconditionally flagged as an "illegal
page filename" by `check_page_names`, which would have made `wiki.py links`
unable to exit 0 against any live clone at all. `check_page_names` now skips
dot-prefixed entries.

## Plan 168-06 — `tools/baseline/chip_database.baseline.json` still carries 9 stale `doc/` references

168-03 fixed the generator (`build_db.py`) and regenerated the live
`firestarter_app/firestarter/data/chip_database.json`, which now carries 0
`doc/AT28C04-ADAPTER.md` references. The committed baseline snapshot
`tools/baseline/chip_database.baseline.json`, used by the diff-against-baseline
regression gate, was not re-baselined at the same time and still carries the 9
old `unsupported_reason` strings citing `firestarter/doc/AT28C04-ADAPTER.md`.

This file is not in 168-06's `files_modified` list and its repair (regenerating
a baseline snapshot) is generator/re-baseline work of the same shape as D-14,
not a docstring/comment/string repair — out of this plan's bounded edit set.
Left as-is; not fixed here.

Recommended follow-up: whichever plan re-anchors baselines against the
168-03-regenerated database should also refresh
`tools/baseline/chip_database.baseline.json`, repointing the 9
`unsupported_reason` strings at the wiki page title `AT28C04 Adapter` per D-13.

**Decided by plan 168-09.** Explicit named historical exclusion, not fixed.
The baseline is a pinned Phase-98 snapshot (`362bfa0`, 2026-06-30) consumed
by six modules; `diff_db.py` is measured indifferent to the literal
`unsupported_reason` text (RC=0 under a mutated-string control), and no test
asserts the path itself. Re-anchoring a frozen baseline has previously
reddened unrelated legs elsewhere in this project. It is the *only* file the
strict repair-sweep grep (`git grep -lE '(^|[^A-Za-z"])doc/[A-Za-z0-9_.-]+\.md'
-- .`) still lists across `firestarter_app` after 168-09. See
168-09-SUMMARY.md's "The `chip_database.baseline.json` Stale-Reference
Decision" section for the full reasoning.
