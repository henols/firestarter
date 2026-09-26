# 152-CLAIM-CLASSES.md — the contract `152-check-claims.py` enforces

This file is itself a `152-check-claims.py` scan target — it is the gate's first and, at this
point in the phase, only `_DEFAULT_TARGETS` member, so the gate is armed against a real, existing
artifact from wave 1 rather than being RED-by-construction or vacuously green. It describes the
forbidden claim classes by **label and location**, per Pattern D, and it deliberately does not
reproduce any offending phrasing. The rejected phrasings this gate has been measured against live in
`152-CLAIM-GATE-TRANSCRIPTS.md`, which is permanently NOT a scan target.

⚠ A small number of `FORBIDDEN_PATTERNS` labels are themselves hyphenated spellings of the very
phrase they forbid (their compiled pattern is hyphen-tolerant, or keys on a bare completion-claim
word), so writing that label's own name as literal text in a live scan target would trip it. Those
rows are cited below by **table location** in `152-check-claims.py` instead of by literal label
spelling. This is the same by-location citation discipline this file uses for class (e)'s tested
phrasings, applied one layer further in.

## The five forbidden claim classes (ROADMAP criterion 5)

| # | Claim class | Enforcing gate label(s) |
|---|---|---|
| (a) | AT28C silicon validation | `at28c256-fixed`, `verified-on-silicon`, `confirmed-working`, `works-on-silicon`, plus `FORBIDDEN_PATTERNS` table rows 9, 10 and 13 (a hyphen-form completion claim paired with "silicon", the bare unqualified form of that same completion claim, and its page-size-scoped variant) |
| (b) | Page-size validation on silicon | `FORBIDDEN_PATTERNS` table row 13 (see above) |
| (c) | A `0x0D` graduation | `graduation` |
| (d) | A `support_status` change | `support-status-change` |
| (e) | The deferred deliberate-protection command named as shipped or available | `sdp-relock-as-shipped`, `sdp-relock-flag-as-shipped` |

For class (e), the mechanism is: the command name is rejected unless a withdrawal predicate
immediately follows it. See `152-RESEARCH.md` §C-4, and `152-CLAIM-GATE-TRANSCRIPTS.md` §RED 1-2
for the eighteen tested phrasings this mechanism was measured against. This file does not write out
any offending phrasing.

## The mandated word order for class (e)

The command name comes first; the withdrawal predicate follows it immediately. Any other order is
rejected by the gate. This is the intended cost of a fail-CLOSED mechanism, not a defect to be
"fixed" by loosening the pattern — it is the same cost 149 accepted when it mandated the single
`software-`-prefixed compound as the only permitted spelling of its own completion-claim word.

## The two narrowings, and why each is a narrowing

**(i) Table row 10's `(?<!software-)` lookbehind is kept verbatim.** The `software-`-prefixed
compound is this milestone's established vocabulary in three measured places: 149's own
required-caveat row, `153-RECORD.md`'s section naming what remains unconfirmed, and
`firestarter/README.md`'s Protocol Notes. Widening the lookbehind past that one prefix would
silently also permit three other hyphenated forms that pair the same bare completion-claim word
with "bench-", "datasheet-" and "silicon-".

**(ii) `issue-closed` drops `32` from its alternation.** D-05 requires this phase to state a
measured 2026-08-08 fact — gh#32 was folded into gh#21 at that closure — and the inherited row
blocked the natural phrasings of that fact. This is a narrowing to the true claim class ("claiming
an issue this milestone did not close is closed"), not a loosening: gh#32's status is a measured
fact, not a claim this milestone is making. gh#21, gh#11 and gh#12 all still trigger this row,
demonstrated by the three `planted_issue_closed_gh21.md`, `planted_issue_closed_gh11.md` and
`planted_issue_closed_gh12.md` fixtures.

## The three required-caveat rows

| Label | Mandated sentence | Required on |
|---|---|---|
| `software-proven-unvalidated` | This ships software-proven and unvalidated on silicon. | `152-CLAIM-CLASSES.md`, `152-RELEASE-NOTES-app.md`, `152-RELEASE-NOTES-fw.md`, `152-LEDGER.md`, every `152-NN-SUMMARY.md` |
| `no-at28c-part-tested` | No AT28C part was tested at any point in v1.32. | `152-CLAIM-CLASSES.md`, `152-GH12-COMMENT.md`, `152-GH21-COMMENT.md`, `152-GH11-COMMENT.md`, `152-RELEASE-NOTES-app.md`, `152-RELEASE-NOTES-fw.md`, `152-LEDGER.md` |
| `zero-d-stays-unverified` | Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER. | `152-CLAIM-CLASSES.md`, `152-RELEASE-NOTES-app.md`, `152-RELEASE-NOTES-fw.md`, `152-LEDGER.md` |

This ships software-proven and unvalidated on silicon.

No AT28C part was tested at any point in v1.32.

Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.

## What D-11 exempts

Statements of shipped, user-visible command behaviour are exempt from criterion 5's pairing clause;
claims about `0x0D` write-path correctness or validation status are not. D-11's own exempt
examples: "erase is now available" and "write no longer blank-checks" — both describe what a
command currently does, not whether silicon has confirmed it.

## What this gate does NOT discharge

A green run of this gate is compliance with the forbidden-phrase table and the per-file caveat rule
**only**. It cannot detect an implied overclaim, a misleading omission, a wrong tone, or a true
statement placed where it misleads. D-03's per-artifact blocking operator checkpoint is a separate
control, and a green gate run does not discharge it.
