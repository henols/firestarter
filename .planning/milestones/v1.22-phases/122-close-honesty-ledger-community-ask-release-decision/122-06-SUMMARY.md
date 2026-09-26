---
phase: 122-close-honesty-ledger-community-ask-release-decision
plan: 06
subsystem: docs
tags: [honesty-ledger, project-record, sdp, at28c, claim-scanner]

requires:
  - phase: 122-05
    provides: "122-LEDGER.md — the nine claim-class honesty ledger this correction cross-references rather than restates"
provides:
  - "PROJECT.md EIGHTH CORRECTION block recording D-10's premise-confirmed/fix-unproven asymmetry"
  - "Mechanical proof that the edit is purely additive and structurally sound (zero deletions, ordinal integrity)"
affects: [122-11, 122-13]

tech-stack:
  added: []
  patterns:
    - "Temporary-extract scanning: run check_permitted_claims.py against a one-off extract of new prose, not the whole non-target file, when the target isn't one of the scanner's five defaults"

key-files:
  created: []
  modified:
    - .planning/PROJECT.md

key-decisions:
  - "Item 3 (C-5/D-14 divergence) is recorded as flagged-and-unresolved, awaiting the operator's accept-or-overturn at the D-16 wording review (122-11) — per the plan's explicit instruction, not resolved in this plan"
  - "Reworded the plan's own drafted item text where it would trip the claim scanner by design (D-14's 'should now work' → 'had become able to do what they wanted'; item 9's 'SDP works on real AT28C silicon' → 'whether the SDP mechanism is effective on real AT28C silicon'), following the ledger's own precedent for citing forbidden-shaped phrases without reproducing them"
  - "Scanned a temporary extract of the new block (not the whole PROJECT.md) against check_permitted_claims.py, because the baseline file already fails the scanner on pre-existing content (2 forbidden-phrase hits, missing caveat) unrelated to this plan"

requirements-completed: []

coverage:
  - id: D1
    description: "PROJECT.md carries an EIGHTH CORRECTION block (9 items) recording D-10's premise-confirmed/fix-unproven asymmetry, the honest community-datapoint provenance, and the flagged C-5/D-14 divergence"
    verification:
      - kind: other
        ref: "grep -c '⚠ EIGHTH CORRECTION' .planning/PROJECT.md == 1; grep -q 'EEPROM timeout at 0x005555' .planning/PROJECT.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "Edit is proven purely additive (zero deleted lines) and structurally sound (all seven ordinals present exactly once, strictly increasing, EIGHTH inside the v1.22 section)"
    verification:
      - kind: other
        ref: "git diff --numstat -- .planning/PROJECT.md (0 deletions); grep -n for all seven ordinal markers in increasing line order"
        status: pass
    human_judgment: false
  - id: D3
    description: "New prose is green against check_permitted_claims.py via a temporary extract (PROJECT.md is not a default scan target and the whole file pre-fails on unrelated content)"
    verification:
      - kind: other
        ref: "python3 check_permitted_claims.py <temp-extract-of-live-block> exits 0"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-07-30
status: complete
---

# Phase 122 Plan 06: EIGHTH CORRECTION — community silicon datapoint, fix unproven Summary

**Appended a 9-item EIGHTH CORRECTION block to `PROJECT.md` recording that gh#11's reporter reproduced the exact predicted INIT abort on real AT28C256 silicon while the fix itself stays unverified — plus five carried-forward mechanism corrections (C-1..C-5, C-8) — proven purely additive by `git diff --numstat`.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-07-30T13:58:47Z (STATE.md last_updated at hand-off)
- **Completed:** 2026-07-30T14:09:38Z
- **Tasks:** 2 (both completed; Task 2 was a proof/gate task with no additional file edits)
- **Files modified:** 1 (`.planning/PROJECT.md`)

## Accomplishments

- Inserted the EIGHTH CORRECTION block into `.planning/PROJECT.md` §"Current Milestone: v1.22", immediately after the SEVENTH CORRECTION's item 9 and before the pre-existing `- **No AT28C part in operator inventory**` bullet, via a scoped `Edit` (never `Write`).
- Item 1 states the D-10 asymmetry precisely: the community reporter's 2026-07-27 reproduction of the verbatim `ERROR: EEPROM timeout at 0x005555: wrote 0x20 got 0xff` INIT abort on a real AT28C256 raises TRACE-06 from software-predicted to community-corroborated, while `0x0D` stays `UNVERIFIED`, zero chips change `support_status`, and the 84-chip count is unchanged. Provenance stated honestly: an issue-comment paste, no captured logs, board revision and firmware build unconfirmed.
- Item 3 records the C-5/D-14 locked-decision divergence (D-14's prescribed `No-Hazmats` reply vs. the measured 19-of-19 `DIP24_2816` refusal) as **flagged and unresolved**, explicitly deferring the accept-or-overturn call to the operator at the D-16 wording review in plan 122-11 — not resolved here, per the plan's own instruction.
- Items 4-9 carry forward the phase's other mechanism corrections (C-4's pre-existing `check_ledger.py` RED, C-1/C-2/C-11/C-12's corrected merge-conflict set, C-3's manual-publish norm, A3/C-8's tag-is-read-not-assumed + `ci.yml` scope, the D-01 owned bench-smoke-test trade-off, and the closing-criterion's mechanizable-vs-judgement split), each cross-referencing `122-LEDGER.md`, `122-NONREGRESSION.md`, or `122-DECISION.md` by name rather than restating their figures.
- Proved the edit purely additive: `git diff --numstat -- .planning/PROJECT.md` reports `12  0` (12 insertions, 0 deletions); `git diff -- .planning/PROJECT.md | grep -c '^-[^-]'` returns `0`.
- Proved ordinal integrity: all seven ⚠ markers (SECOND REFRAMING, THIRD, FOURTH, FIFTH, SIXTH, SEVENTH, EIGHTH CORRECTION) appear exactly once, at strictly increasing line numbers `59 < 67 < 73 < 81 < 91 < 101 < 113`, and 113 (EIGHTH) is well before the `## v1.21 Archive` heading — confirming the insertion landed inside §"Current Milestone: v1.22", not the archive.
- Confirmed `grep -c 'all 84' .planning/PROJECT.md` is unchanged at `6` — no new occurrence of the literal phrase was introduced (the new block uses "84-chip `algorithm == 13` count" and "the full 84-entry `0x0D` set" instead).
- Ran the claim scanner (`check_permitted_claims.py`) against a temporary extract of the live inserted block (`sed -n '113,122p' .planning/PROJECT.md`) — **exit 0**, with the required silicon caveat present. The whole `PROJECT.md` file was NOT used as the scan target: a baseline run against the full file (before this edit) already fails with 2 pre-existing forbidden-phrase hits ("proven on silicon", "proven on real silicon") and a missing caveat, both unrelated to this plan — confirming the plan's own note that `PROJECT.md` is not one of the scanner's five default outward-facing targets and this is a courtesy check on new prose only, never a contract on the whole file.
- Reworded two spots where the plan's own drafted prose would have tripped the scanner if used verbatim: D-14's "AT28C parts should now work" → "AT28C parts had become able to do what they wanted" (matches `122-LEDGER.md`'s own precedent for citing this exact overclaim without reproducing its trigger shape), and item 9's "SDP works on real AT28C silicon" → "whether the SDP mechanism is effective on real AT28C silicon" (avoids the `works-on-silicon` pattern while preserving the identical meaning).
- No requirement checkbox was ticked. `REQUIREMENTS.md` is untouched (`git status --porcelain -- .planning/REQUIREMENTS.md` empty). `.planning/v1.16/ledger/` (`PROTOCOL-LEDGER.{md,json}`) is untouched. Neither sub-repo gitlink was staged.

## Task Commits

1. **Task 1: Author the EIGHTH CORRECTION block and insert it immediately after the SEVENTH** — `c80a9ac` (docs) — includes Task 2's verification-only work, since Task 2 produced no additional file edits (it was a mechanical proof/gate task run against Task 1's committed edit).

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md updates (separate commit, per the execute-plan final_commit step).

_Note: Task 2 ("Prove the edit's structural integrity and gate the new block against the claim scanner") is a verification task with `files_modified: .planning/PROJECT.md` shared with Task 1 — no new edit was made; its acceptance criteria (additive-diff proof, ordinal-integrity proof, scanner gate, no-requirement-ticked statement) were all verified against Task 1's single commit and are recorded above and in this SUMMARY. No separate commit was needed._

## Files Created/Modified

- `.planning/PROJECT.md` — appended the EIGHTH CORRECTION block (9 numbered items) between the SEVENTH CORRECTION's item 9 and the pre-existing `- **No AT28C part in operator inventory**` bullet.

## Decisions Made

- **Flagged, not resolved, the C-5/D-14 divergence (item 3).** The plan's `<what_this_correction_records>` section explicitly instructed "Do not resolve it here" — worded item 3 as a divergence from a locked decision, flagged for the operator's accept-or-overturn at plan 122-11's D-16 wording review, consistent with how `122-LEDGER.md` records the same divergence (mechanism 3 in its "Mechanism corrections" section).
- **Reworded two scanner-tripping phrases from the plan's own literal drafted text** rather than reproducing them verbatim or weakening the scanner's pattern set — following the explicit guidance in this plan's dispatch prompt ("Known tension, already resolved twice this phase: quoting a forbidden phrase verbatim trips the scanner by design... Reword your prose; never weaken the scanner's pattern set") and `122-LEDGER.md`'s own established precedent for the identical D-14 phrase.
- **Scanned a temporary extract, not the whole `PROJECT.md` file.** Verified via a baseline scanner run against the pre-edit file that it already fails (2 forbidden hits, missing caveat, both pre-existing and unrelated to this plan) — confirming `PROJECT.md`'s status as a non-default, courtesy-only scan target per the plan's Task 2 instructions. The temporary extract (the live inserted block, lines 113-122) was scanned and passed exit 0.
- **Naturally included the exact caveat sentence "No AT28C silicon was tested" in item 1**, rather than adding it "purely to satisfy the courtesy check" — this phrasing is a truthful restatement of the validation ceiling and is used verbatim elsewhere in this same phase's own artifacts (`122-LEDGER.md` lines 8, 30, 77), so it is substantively motivated, not contrived.
- **Cross-referenced `122-DECISION.md` by name** in items 6 and 8 (the release-mechanics narrative and the owned bench-smoke-test trade-off) alongside the required `122-LEDGER.md` and `122-NONREGRESSION.md` references — `122-CHANNELS.md` was deliberately NOT referenced by name, since that artifact (plan 122-08) does not exist yet at this plan's execution point and referencing a not-yet-existing file in a permanent project record would be premature.

## Deviations from Plan

None — plan executed exactly as specified, with two narrow, explicitly-justified wording adjustments (documented above under Decisions Made) made to satisfy the plan's own scanner-gate requirement (Task 2's acceptance criterion that the scanner exit 0) without weakening the scanner or reproducing a forbidden phrase verbatim. These are not Rule 1-4 deviations — they are prose-wording choices explicitly anticipated and directed by the plan's own `<use_the_scanner>` guidance and Task 2's action text.

## Issues Encountered

- The plan's literal drafted text for item 3 ("their AT28C parts should now work") and item 9 ("that SDP works on real AT28C silicon") would each trip a forbidden pattern in `check_permitted_claims.py` (`should-now-work` and `works-on-silicon` respectively) if used verbatim. Resolved by rewording both to preserve identical meaning without the trigger shape, per the dispatch prompt's explicit precedent-based guidance and `122-LEDGER.md`'s own prior handling of the same D-14 phrase.
- Confirmed via a baseline scanner run that scanning the whole (pre-edit) `PROJECT.md` file already fails (2 pre-existing forbidden-phrase hits at lines discussing FIX-04/TRACE-06, plus a missing caveat) — this is expected and unrelated to this plan; `PROJECT.md` is explicitly not one of the scanner's five default targets, so the gate in this plan's Task 2 was satisfied via a temporary extract of only the new block, per the plan's own instructions.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The EIGHTH CORRECTION block is now the project-level evidence record for D-10's asymmetric community datapoint, ready for plan 122-11's D-16 blocking operator wording review, which is where the flagged C-5/D-14 divergence gets its accept-or-overturn decision.
- No blockers. `.planning/PROJECT.md`'s six prior correction blocks and all archive sections are untouched and byte-identical apart from the new insertion.
- Plan 122-13 (the phase's final closing plan) is the only plan permitted to tick `CLOSE-01` — this plan deliberately left it, and all of `REQUIREMENTS.md`, untouched.

---
*Phase: 122-close-honesty-ledger-community-ask-release-decision*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: `.planning/PROJECT.md`
- FOUND: `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-06-SUMMARY.md`
- FOUND commit: `c80a9ac` (EIGHTH CORRECTION edit)
- FOUND commit: `6e3c924` (this SUMMARY)
