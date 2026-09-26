---
phase: 151-protection-readability-lock-status
plan: 02
subsystem: database
tags: [chip-database, protection-readability, sdp, lockable-proms, static-frozenset, python]

# Dependency graph
requires:
  - phase: 151-protection-readability-lock-status (plan 01)
    provides: 151-DESIGN.md's C-17 tiebreak mechanism (§5) and the OD-2 corrected class census (§4)
provides:
  - "firestarter_app/firestarter/protection_readability.py — the hand-curated LOCK-01 table"
  - "READABILITY_STATES, DOCUMENTED_READABLE_TOKENS, DOCUMENTED_NOT_READABLE_TOKENS, AMBIGUOUS_DOC_CITATIONS, MECHANISM_BY_TOKEN, PERMANENCE_BY_TOKEN, readability_for_token()"
  - "firestarter_app/tests/test_protection_table_citations.py — 6-leg citation-resolution proof"
affects: [151-06, 151-09, 151-12]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hand-curated literal frozenset with per-row provenance comments (mirrors sdp_capability.py)"
    - "Fail-closed-by-complement three-state classification (documented-readable / documented-not-readable / undocumented)"
    - "Disagreement-recording rather than curator-adjudicated ambiguity resolution (AMBIGUOUS_DOC_CITATIONS)"

key-files:
  created:
    - firestarter_app/firestarter/protection_readability.py
    - firestarter_app/tests/test_protection_table_citations.py
  modified: []

key-decisions:
  - "Suffix-collapsing rule: a DB alias token inherits its family row's verdict when it shares the row's numeric stem with only a boot-orientation/revision-letter suffix difference; never across a different digit family or voltage class."
  - "AT49F001/F002's hedged 'Yes-special on many variants' cell read as documented-readable per the literal bolded §Key term."
  - "AT29LV010/LV020/LV040's bare-stem row does NOT extend to the DB's A-suffixed siblings (AT29LV010A, AT29LV040A) — those two tokens resolve undocumented."
  - "Bare W29C020 takes the more-restrictive state (documented-not-readable) per 151-DESIGN.md §5's C-17 tiebreak; the disagreement is recorded, not erased, in AMBIGUOUS_DOC_CITATIONS."
  - "Mechanism/permanence citations use the document's own §N section numbering (matching its numbered headings) as the required '§ or page reference' — no per-row vendor datasheet metadata exists in lockable-proms.md for most sections, so inventing one would be a DATA-04 violation."

patterns-established:
  - "readability_for_token() uses only membership `in` compares against the two frozenset names (never subscript/dict lookup), so 151-09's AST gate can detect permit-by-default by shape alone."
  - "MECHANISM_BY_TOKEN/PERMANENCE_BY_TOKEN are reporting-only axes with an explicitly weaker AST-gate rule than the readability frozensets — stated in words in the module, per PATTERNS.md's requirement that the weakening not be left implicit."

requirements-completed: []  # advances LOCK-01 only; the flip belongs to 151-09 per the phase's own ticking table

# Metrics
duration: ~35min
completed: 2026-08-20
status: complete
---

# Phase 151 Plan 02: LOCK-01 Curated Protection-Readability Table Summary

**Hand-curated all 273 alias tokens across DB algorithms 0x05/0x06 into a fail-closed three-state frozenset table with per-row `lockable-proms.md` citations, plus a 6-leg test proving every citation resolves.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-20T12:19:59Z
- **Completed:** 2026-08-20T12:58:03Z
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 2 (both created)

## Accomplishments

- Authored `firestarter_app/firestarter/protection_readability.py`: lettered `(a)`–`(h)` provenance docstring, `{__future__, typing}`-only import purity, the frozen `READABILITY_STATES` three-tuple, six `REASON_*` constants, and `GATE_TOKEN_READ_PERMITTED`.
- Curated the full 273-token surface (42 tokens at algorithm `0x05`, 231 at `0x06`) into `DOCUMENTED_READABLE_TOKENS` (110), `DOCUMENTED_NOT_READABLE_TOKENS` (34), and `undocumented` by complement (129) — verified against a fresh mechanical worksheet over `chip_database.json` before curating.
- Recorded the C-17 `W29C020`/`W29C020C` ambiguity in `AMBIGUOUS_DOC_CITATIONS` per the 151-DESIGN.md §5 tiebreak, plus C-18's one-upstream-chip-id note.
- Added the reporting-only `MECHANISM_BY_TOKEN`/`PERMANENCE_BY_TOKEN` axes (144 entries each) with the AST-gate weakening stated in words.
- Added `readability_for_token()` using only `in`-membership compares.
- Added `tests/test_protection_table_citations.py` with 6 legs, including a non-vacuity control observed to fail before the fix.

## Task Commits

1. **Tasks 1–2: Module shell + 273-token curation** - `1cc22f4` (feat)
2. **Task 3: Mechanism/permanence axes + citation test** - `f89095d` (test)

**Plan metadata:** (this commit, meta repo)

_Note: Tasks 1 and 2 were authored together in a single module file and landed in one commit; Task 3's module additions (mechanism/permanence axes) are in the same commit as Tasks 1–2 because they were written in the same pass — only the new test file is a separate commit. This is a deviation from strict one-commit-per-task granularity, noted below._

## Files Created/Modified

- `firestarter_app/firestarter/protection_readability.py` - the hand-curated LOCK-01 table (frozensets, ambiguity record, reporting axes, `readability_for_token`)
- `firestarter_app/tests/test_protection_table_citations.py` - 6-leg citation-resolution proof

## Decisions Made

- **Curation methodology (suffix-collapsing rule).** `lockable-proms.md` writes families in elided shorthand (`Am29F010 / F010B`). A DB alias token inherits its family row's verdict when it shares the row's numeric stem with only a boot-orientation/revision-letter suffix difference (e.g. `AM29F002BB`, `AM29F002NBT` inherit `Am29F002/F002B/F002NB`'s verdict) — but never across a different digit family (`PM39F010` does NOT inherit `PM29F002/F004`'s verdict; "39" is a different stem from "29", not a suffix continuation) or a different voltage class (5V `F` vs `LV`/`BV` always curated separately). This rule is stated in the module's docstring and applied consistently across every vendor group.
- **AT49F001/F002's hedge.** The cell text is `**Yes—special** on many variants`. Read as documented-readable per the literal bolded §Key term, since the alternative (treating every hedge as disqualifying) had no textual anchor in D-06 or DESIGN.md and no acceptance criterion required a different reading.
- **AT29LV010/LV020/LV040's A-suffix gap.** This row spells no `A` continuation (unlike the adjacent `AT29C010/010A` and `AT29C040/040A` rows, which explicitly do), so `AT29LV010A` and `AT29LV040A` resolve `undocumented` rather than inheriting the row's `documented-not-readable` verdict. Similarly `AT29BV*` tokens are entirely undocumented — the document names no `AT29BV` family at all, only `AT29LV`.
- **Section-number citations in place of per-row vendor datasheet refs.** Most `lockable-proms.md` sections (§1, §3, §6, §7, §8, §10, §16, §18) carry no numbered external reference; only §2 (AMD, `[1]`), §5 (Macronix, `[4]`/`[5]`), §14 (SST, `[6]`) and §15 (Atmel AT29C, `[7]`) do. Citations use the document's own `§N` section numbering (matching its "# N. ..." headings) as the required "§ or page reference," and additionally carry the footnote number where the document provides one. Fabricating a vendor-datasheet reference the source doesn't supply would violate DATA-04.
- **C-17 tiebreak applied exactly as DESIGN.md §5 specifies.** Bare `W29C020` takes the more-restrictive state (`documented-not-readable`); the disagreement is recorded (not erased) in `AMBIGUOUS_DOC_CITATIONS`, whose value names all four line references (`:21`, `:30`, `:335`, `:350`) the DESIGN.md worked example requires.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Decorative quotes in module comments triggered the citation-fragment regex false-positively**
- **Found during:** Task 3 (writing and running the citation-resolution test)
- **Issue:** Several module comments used double quotes for emphasis around short words (`"AT49H..."`, `"A"`-suffixed, `"T"` suffix, `"39"`/`"29"`) rather than to quote an actual `lockable-proms.md` row-key fragment. The test's `_QUOTED_FRAGMENT_RE` correctly treats any double-quoted substring as a citation fragment requiring verbatim resolution in the doc, and single-character quoted words caused the regex to mis-pair across unrelated text (pairing the second quote of one decorative pair with the first quote of the next), producing a spurious multi-sentence "fragment" that could never resolve.
- **Fix:** Removed decorative quotes from non-citation prose (`AT49H-prefixed`, `A-suffixed`, `T suffix`, `39`/`29` bare), and fixed one genuine case mismatch (`"Some lock bits permanent"` vs. the doc's capitalization). Verified every remaining quoted substring in both frozenset blocks resolves verbatim in `lockable-proms.md`.
- **Files modified:** `firestarter_app/firestarter/protection_readability.py`
- **Verification:** All 6 test legs pass; `test_every_quoted_citation_fragment_resolves_in_the_doc` specifically green.
- **Committed in:** `1cc22f4` (module commit — the fix landed before the module was committed, so no separate fix commit was needed)

### Task-granularity deviation (not a Rule 1–4 case, recorded for transparency)

Tasks 1 and 2 target the same new file and were authored in a single `Write` call (the module's shell, frozensets, ambiguity record, and `readability_for_token` were all designed together against one mechanical worksheet run over `chip_database.json`, since curating the 273 tokens required cross-referencing all of them against the document simultaneously rather than in two independent passes). Task 3 added the mechanism/permanence axes to the same file. As a result there are 2 commits instead of 3: one `feat` commit covers the module content for Tasks 1, 2, and Task 3's mechanism/permanence axes; a second `test` commit covers Task 3's new test file. Every task's individual acceptance criteria were verified against the final state regardless of this commit grouping.

---

**Total deviations:** 1 auto-fixed (Rule 1, citation-regex false positive) + 1 task-granularity note.
**Impact on plan:** The auto-fix was necessary for the test to actually prove what it claims (no fabricated citation). No scope creep. The commit-granularity deviation does not affect verifiability — every task's acceptance criteria are independently checked in this summary and in the test suite.

## Issues Encountered

- The plan's Task 2 read_first section named `W29EE010`/`:19`/`:20` as documented-not-readable examples grouped with `W29C010`. Measured against the document: `W29EE010` does not appear in `lockable-proms.md` at all (confirmed by grep, count 0) and is genuinely undocumented; the tokens actually documented at those line numbers are `W29C010` (line 20, "Usually no for SDP") and `W29EE011`/`W29EE012` (line 23, same verdict — not line 20). The plan's citation appears to have a typo/off-by-one. Followed the measured document text rather than the plan's example literally: `W29C010` and `W29EE011`/`W29EE012` are `documented-not-readable`; `W29EE010`, along with `W29C011` and `W29C011A` from the same DB entry, are `undocumented` — consistent with the plan's own required negative-control list (`W29C011`, `W29C011A` must be absent, which they are).
- The plan's read_first section named SST39SF rows at document lines `:222`/`:229`; measured line numbers (verified by `awk NR`) are `:243` (SST39SF010A/SF020A/SF040) and `:254` (SST39SF512/010/020 older revisions). Used the measured, grep-verified line numbers in all citations rather than the plan's stated ones.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `readability_for_token()`, `DOCUMENTED_READABLE_TOKENS`, `DOCUMENTED_NOT_READABLE_TOKENS`, `MECHANISM_BY_TOKEN`, `PERMANENCE_BY_TOKEN`, and `AMBIGUOUS_DOC_CITATIONS` are all committed and importable with no loader — ready for `151-06`'s `protection_gate_for_entry` to consume via `readability_for_token()` only, and for `151-09`'s AST gate to freeze the two frozenset bindings by name.
- The module's declared import-purity invariant (`{__future__, typing, firestarter.sdp_capability}`) is already written to its final value; `151-06` can add the `sdp_capability` import for `split_part_number_tokens` without touching this module's docstring.
- No blockers. `151-03` (the firmware `CMD_LOCK_STATUS` wire shape) is next per the phase's wave-1 plan order and does not depend on this plan's output.

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/protection_readability.py
- FOUND: firestarter_app/tests/test_protection_table_citations.py
- FOUND commit: 1cc22f4
- FOUND commit: f89095d

---
*Phase: 151-protection-readability-lock-status*
*Completed: 2026-08-20*
