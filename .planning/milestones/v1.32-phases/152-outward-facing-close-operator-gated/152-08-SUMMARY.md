---
phase: 152-outward-facing-close-operator-gated
plan: 08
subsystem: docs
tags: [release-notes, claim-gate, lock-status, protection-readability, honesty-ledger]

requires:
  - phase: 151-firmware-protection-readability-lock-status
    provides: lock-status, protection_readability.py, lock_status.py, the eight D-09 class tokens
  - phase: 153-blank-check-erase-write-path-policy
    provides: the write-path blank-check removal and standalone 0x0D erase this body describes as shipped
provides:
  - 152-CLASS-SIZES.md, a live two-method re-derivation of the protection-class partition that settles RESEARCH Open Question 1
  - 152-RELEASE-NOTES-app.md, the frozen, version-placeholdered OUT-04 app release body
affects: [152-12, 152-17, 152-20]

tech-stack:
  added: []
  patterns: [version-placeholder-then-read (D-01), gate-word-order-mandated-withdrawal (RESEARCH §C-4), do-not-cite figure register]

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-CLASS-SIZES.md
    - .planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-app.md
  modified: []

key-decisions:
  - "Method B (alias-aware, the only method the shipped CLI can actually reach through EpromDatabase.get_eprom()) is the formulation cited outward -- 665 of 746 rows refuse, 81 read_permitted -- attributed to 'the live classifier', not to 'either counting method', because the two methods measured in this plan disagree by +/-1 row."
  - "151 D-06/D-09's published 406/111/39 does not reproduce because its own 111 = 84+27 arithmetic implicitly assumed every algorithm-5 row is not_readable; measured breakdown is 7 not_readable + 20 undocumented_alias + 0 read_permitted for those 27 rows -- a bucket conflation, not primarily an aliasing ambiguity."
  - "The b14 forward-looking sentence is corrected in the new notes' Removed section, never edited in the published body (D-02)."

requirements-completed: [OUT-04]

coverage: []

duration: 45min
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 08: Class-Size Re-derivation and App Release Notes Summary

**Re-derived the DB protection-class partition through two distinct methods, settled RESEARCH Open
Question 1 with a measured explanation for 151's non-reproducing figures, and authored the
version-placeholdered `152-RELEASE-NOTES-app.md` — gate-clean, `lock-status` announced refusal-first,
the deferred command withdrawn in the gate's mandated word order.**

## Performance

- **Duration:** ~45 min
- **Tasks:** 3 (Task 3 required no additional file change — see below)
- **Files modified:** 2 created

## Accomplishments

- `152-CLASS-SIZES.md`: ran `firestarter.protection_readability.protection_gate_for_entry` over all
  746 rows of `chip_database.json` under two methods, with zero classification errors in either run.
- Settled RESEARCH Open Question 1: 151's published 406/111/39 is explained primarily by a bucket
  conflation in that figure's own arithmetic (all 27 algorithm-5 rows assumed `not_readable`, when
  only 7 of 27 actually are), with a smaller, separately-recorded ±1-row method-dependent delta.
- `152-RELEASE-NOTES-app.md` authored, gate-clean, citing only the robust class-size formulation,
  correcting the published `b14` forward-looking sentence in the new notes, and naming the deferred
  command's withdrawal in the exact word order `152-check-claims.py` mandates.
- No network write of any kind performed. Nothing posted.

## Both derivation methods' partitions (verbatim from `152-CLASS-SIZES.md`)

**Method A — per-row canonical (first alias of `part_number` only, single token):**

| class token | count |
|---|---|
| `no_mechanism` | 405 |
| `not_implemented` | 40 |
| `not_readable` | 112 |
| `undocumented_alias` | 107 |
| `read_permitted` | 82 |
| total | 746 (0 errors) |

Refusal total: 405+40+112+107 = **664**. `read_permitted` = **82**. 664+82 = 746.

**Method B — alias-aware (full `part_number`, every alias tokenised — the shape
`firestarter.database.EpromDatabase.get_eprom()` always builds regardless of lookup key, and
therefore the only method the shipped CLI can ever actually run):**

| class token | count |
|---|---|
| `no_mechanism` | 405 |
| `not_implemented` | 40 |
| `not_readable` | 108 |
| `undocumented_alias` | 112 |
| `read_permitted` | 81 |
| total | 746 (0 errors) |

Refusal total: 405+40+108+112 = **665**. `read_permitted` = **81**. 665+81 = 746.

Method B reproduces `152-RESEARCH.md` §A-8's own live re-derivation exactly, because RESEARCH's
script — despite describing itself as "keyed on the first alias" — in fact supplied the full
multi-alias `part_number` string as `entry["name"]`, the same shape the production `get_eprom()`
call always produces. `no_mechanism` (405) and `not_implemented` (40) are identical under both
methods, because those two classes are decided purely by `protocol-id` membership and never consult
alias tokens at all.

**Per-algorithm breakdown inside the curated surface (Method B):** algorithm 5 (27 rows) = 7
`not_readable` + 20 `undocumented_alias` + 0 `read_permitted`; algorithm 6 (190 rows) = 17
`not_readable` + 92 `undocumented_alias` + 81 `read_permitted`. **No algorithm-5 row is
`read_permitted`** — this is the measured fact behind D-13's "no `0x05` row answers by default"
statement, and it is the load-bearing explanation for why 151's "111 = 84+27" figure does not
reproduce: it is not primarily an aliasing artefact, it is a conflation of two different
classification outcomes (`not_readable` and `undocumented_alias`) into one number.

## Publishable formulation

Measured through the live production code path (Method B — the only method the shipped CLI can
actually run): **665 of 746 database rows (89%) resolve to a refusal class; 81 are
`read_permitted`.** This is the exact figure cited in `152-RELEASE-NOTES-app.md`'s `lock-status`
section, attributed there to "the live classifier," not to "either counting method" — Method A and
Method B measured in this plan disagree by exactly 1 row (664/82 vs. 665/81), so the two methods do
not agree on a shared robust figure to within zero rows, only to within one.

## Do-not-cite list (verbatim from `152-CLASS-SIZES.md`)

- 107 vs. 112 for `undocumented_alias` (method-dependent).
- 112 vs. 108 for `not_readable` (method-dependent).
- 82 vs. 81 for `read_permitted` (method-dependent).
- 664 vs. 665 for the refusal-class total (method-dependent).
- 151's own published 406/111/39 triple — does not reproduce under either method measured here.
- Any algorithm-5-only readability count implying all 27 rows share one verdict.
- 664/82 (Method A) specifically — a synthetic, unreachable counterfactual; the shipped CLI cannot
  produce it.

## The measured b14 sentence

Re-grepped live (`gh release view 3.0.0b14 --repo henols/firestarter_app --json body --jq
'.body'`), the app `3.0.0b14` body (2026-07-30) still contains, verbatim: *"An opt-in re-lock after
a write is deliberately not part of this release."* `152-RELEASE-NOTES-app.md`'s Removed section
quotes this sentence and corrects it in the new notes without editing the published body (D-02).

## Task Commits

1. **Task 1: Re-derive the protection-class partition and settle Open Question 1** — `d60b3da5`
   (docs) — `152-CLASS-SIZES.md`
2. **Task 2: Author `152-RELEASE-NOTES-app.md`** — `971c679c` (docs) — `152-RELEASE-NOTES-app.md`
3. **Task 3: Freeze the draft and hand the placeholder contract forward** — no additional commit;
   both artifacts were already clean on disk after Task 2's commit (verified below), so Task 3
   consisted of verification and this handoff record only.

## Files Created/Modified

- `.planning/phases/152-outward-facing-close-operator-gated/152-CLASS-SIZES.md` — the two-method
  derivation record; not a `152-check-claims.py` scan target by design.
- `.planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-app.md` — the frozen
  OUT-04 app release body; a `_CAVEAT_RULES` entry requiring all three caveat labels (already
  present in `152-check-claims.py`, confirmed green against it).

## Placeholder token handoff (for Plan 152-12)

| Token | Lines in `152-RELEASE-NOTES-app.md` | Replaced by | Read command |
|---|---|---|---|
| `APP_TAG_TBD` | 3, 10 | the cut app tag | `gh release list --repo henols/firestarter_app --limit 5` (take the newest pre-release after the merge lands) |
| `FW_TAG_TBD` | 14, 42 | the cut firmware tag | `gh release list --repo henols/firestarter --limit 5` (the firmware sub-repo; take the newest pre-release after its merge lands) |

Both release workflows (`firestarter_app/.github/workflows/beta-release.yml` and
`firestarter/.github/workflows/beta-build.yml`) pass no `body:` field to
`softprops/action-gh-release@v2` — confirmed by reading both files during RESEARCH §E-1/§E-2 — so a
release body is **always** added manually via `gh release edit --notes-file`, never by CI. Plan
152-12 must read both tags from a live `gh release list` after the two merges cut, never predict
them, and Plan 152-17 posts this body only after that read.

**Current body length of the release this will land on:** measured live just now,
`gh release view 3.0.0b22 --repo henols/firestarter_app --json body --jq '.body | length'` → `0` —
the latest pre-release ahead of this milestone's cut is bodiless, consistent with D-02's finding
that every app release from `3.0.0b16` through `3.0.0b22` has body length exactly 0.

## Posting and verification invocations for Plan 152-17

Posting invocation (not run in this plan):

```
gh release edit APP_TAG_TBD --repo henols/firestarter_app --notes-file <path to this draft>
```

Verification invocation (not run in this plan):

```
gh release view APP_TAG_TBD --repo henols/firestarter_app --json body --jq '.body'
```

piped into `diff -u` against `152-RELEASE-NOTES-app.md`, plus the body-length read
(`... --jq '.body | length'`) as the 0-to-N non-vacuity guard.

## Wording-review items for Plan 152-17's operator checkpoint

1. **The stable-channel sentence** — the opening paragraph's disclaimer that GitHub's `2.0.8`
   stable release is not asserted to be installable from PyPI (PyPI's own `info.version` was still
   `2.0.7` as of 2026-08-21).
2. **The withdrawal sentence's word order** — in the `## Removed` section, the deferred command's
   name is immediately followed by its withdrawal predicate, naming Backlog 999.28, in the exact
   shape `152-check-claims.py`'s fifth forbidden class mandates. Confirm this reads correctly to a
   human, not only to the gate.
3. **The `lock-status` paragraph's refusal-first framing** — confirm the paragraph leads with the
   refusal as the feature (per D-13), names the beta-channel and matched-firmware requirements, and
   does not read as promising a state read for chips outside the classes measured in
   `152-CLASS-SIZES.md`.

## Decisions Made

- Method B (alias-aware, matching the production code path) is the only formulation cited outward;
  Method A is recorded as a synthetic counterfactual the shipped CLI cannot reach.
- 151's non-reproducing figures are attributed primarily to a bucket-conflation in that figure's own
  published arithmetic, not to an aliasing ambiguity, based on the measured algorithm-5 breakdown.
- The withdrawal sentence uses the exact phrasing already measured clean against the gate in
  `fixtures/clean_control.md`
  (`` `write --sdp-relock` is withdrawn — tracked as Backlog 999.28. ``).

## Deviations from Plan

None — plan executed exactly as written. Task 3 produced no additional file diff because both
artifacts were already clean on disk after Task 2's own commit; its "recording" obligations are
discharged in this SUMMARY, which is where the plan's own `<output>` section directs the handoff
content to live.

## Issues Encountered

One authoring correction, caught by verification before commit: the required-caveat sentence "No
AT28C part was tested at any point in v1.32" was initially written wrapped across two source lines
in the markdown body. `grep -c` on the exact phrase returned 0 (the acceptance criterion demands
exactly 1) because the sentence was split mid-line. Fixed by un-wrapping that paragraph onto a
single line before the commit; re-verified `grep -c` == 1 and the gate still green.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

`152-RELEASE-NOTES-app.md` is frozen and gate-clean, with both placeholder tokens enumerated above
for Plan 152-12 to fill from a live read after the beta merges cut. Plan 152-17 posts this body only
after that read and only past its own blocking operator checkpoint covering the three wording-review
items above.

This ships software-proven and unvalidated on silicon. No AT28C part was tested at any point in v1.32. Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.

---
*Phase: 152-outward-facing-close-operator-gated*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-CLASS-SIZES.md`
- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-app.md`
- FOUND commit: `d60b3da5`
- FOUND commit: `971c679c`
- `FIRESTARTER_CLAIMSCAN_TARGETS_152=<this file> python3 152-check-claims.py` → rc=0
- `python3 152-check-claims.py` (defaults) → rc=0
