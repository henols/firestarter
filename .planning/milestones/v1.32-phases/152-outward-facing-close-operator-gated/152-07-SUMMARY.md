---
phase: 152-outward-facing-close-operator-gated
plan: 07
subsystem: docs
tags: [github-issues, claim-gate, outward-comms, at28c, erase]

requires:
  - phase: 152-01
    provides: 152-check-claims.py gate armed against 152-CLAIM-CLASSES.md
  - phase: 152-05
    provides: 152-GH12-COMMENT.md (sibling public draft — tonal/content consistency)
  - phase: 152-06
    provides: 152-GH21-COMMENT.md (sibling public draft — tonal/content consistency)
provides:
  - 152-GH11-COMMENT.md — frozen OUT-03 draft answering gh#11's 2024 report
affects: [152-16 (posts this draft), 152-20 (close-out scan)]

tech-stack:
  added: []
  patterns:
    - "gh issue view --json comments as the live re-measurement oracle before authoring an outward reply"

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-GH11-COMMENT.md
  modified: []

key-decisions:
  - "Framed the 2026-08-03 exchange as a kept-late promise (18 days), not a broken silence — RESEARCH §D-4's correction to CONTEXT's 'unanswered' framing carried through verbatim into the reply's opening section."
  - "Cited Microchip DS20006386B Table 6-1 (p.11) by document number exactly once, naming both the hardware 12V-on-OE erase mechanism and the software six-byte mechanism, so the reader can check the claim independently."
  - "Rephrased RESEARCH §B-10's 'no support_status field moved' bullet as 'no chip's support classification in the database moved' to satisfy the acceptance criterion that the literal string 'support_status' never appear in a posted artifact."
  - "Omitted literal 'gh#11' self-reference inside the gh#11 comment itself, to sidestep the issue-closed forbidden-pattern row entirely rather than relying on word-distance safety margins."

requirements-completed: [OUT-03]

coverage:
  - id: D1
    description: "152-GH11-COMMENT.md drafted: discharges the 2026-08-03 commitment, answers the 2024 report in FIX-06 conflation terms with a datasheet citation, states the shipped erase step's honest limits, corrects the page-write expectation, transcribes the not-yet-confirmed list, and asks for a run naming both install halves."
    requirement: "OUT-03"
    verification:
      - kind: other
        ref: "FIRESTARTER_CLAIMSCAN_TARGETS_152=<abs>/152-GH11-COMMENT.md python3 152-check-claims.py — rc=0"
        status: pass
      - kind: unit
        ref: "python3 -m pytest test_check_claims_152.py -q -o addopts=\"\" — 30 passed"
        status: pass
    human_judgment: true
    rationale: "D-03's per-artifact blocking operator wording review is a separate control this gate does not discharge; the draft still needs operator sign-off before Plan 152-16 posts it."

duration: 35min
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 07: gh#11 OUT-03 reply draft Summary

**Authored `152-GH11-COMMENT.md`, a frozen gh#11 reply that discharges the 2026-08-03 "I will soon get it pushed and I will keep you posted" commitment 18 days late, answers the 2024 report in FIX-06 conflation terms citing Microchip DS20006386B, and passes `152-check-claims.py` (rc=0).**

## Performance

- **Duration:** 35 min
- **Started:** 2026-08-21T14:50:00Z
- **Completed:** 2026-08-21T15:25:00Z
- **Tasks:** 3
- **Files modified:** 1 (+ this SUMMARY)

## Accomplishments

- Re-measured gh#11's live comment timeline via `gh issue view` (18 comments, state `OPEN`) with zero delta against RESEARCH §D-4's 2026-08-21 baseline; the five load-bearing comments (2025-09-28, 2026-07-30, 2026-08-03×2, 2026-08-03 no-Discord) all match verbatim.
- Confirmed the shipped erase arm in the committed firmware tree: `eeprom28c_erase_execute` referenced 3× (`firestarter/src/proms/eeprom_28c.cpp:144,246,515` — declaration, dispatch-comment, definition) and the `0544`/AN-0544B application-note citation 7× (lines 63, 148, 246, 499, 501, 518, 527), all at `firestarter@8b7feac`.
- Authored `152-GH11-COMMENT.md` addressing both thread participants (`@datapaganism`, `@AndersBNielsen`) by their measured logins, in six sections: (1) the commitment discharged by name, without apologizing for a silence that never existed; (2) the FIX-06-shaped conflation answer, with Microchip DS20006386B Table 6-1 (Operating Modes, p.11) cited by document number; (3) what shipped (the AN-0544B software six-byte erase) and its honest limits (Atmel-family timing maximum spanning a multi-vendor bucket; the structural, not-merely-untested wall-clock-proof limit); (4) the page-write analysis acknowledged, with the page-size seam explicitly stated to change nothing for this part; (5) the not-yet-confirmed list, carrying the mandated "No AT28C part was tested at any point in v1.32." sentence exactly once; (6) the ask, naming both install halves (`pip install --pre --upgrade firestarter` and `firestarter fw --install`) without naming a release version.
- Froze the draft with a clean commit; recorded the pre-post baseline Plan 152-16 must re-capture and assert a delta of exactly 1 against.

## Task Commits

1. **Task 1 + Task 2: Re-measure gh#11 timeline; author 152-GH11-COMMENT.md** - `df04127a` (docs)
2. **Task 3: Freeze and record handoff data** - satisfied by the same commit (`df04127a`); no further file change was required — the draft was already committed clean, so Task 3's action was measurement/recording only (blob SHA, baseline comment count, both `gh` invocations, branch confirmation — all recorded below).

**Plan metadata:** this SUMMARY's own commit (recorded after write, see below).

## Files Created/Modified

- `.planning/phases/152-outward-facing-close-operator-gated/152-GH11-COMMENT.md` - the frozen OUT-03 draft, gate-clean, version-agnostic.

## Task 1 — Re-measured Timeline (verbatim)

`gh issue view 11 --repo henols/firestarter_prom --json number,title,state,author,createdAt,comments`:

- `state`: `OPEN`
- `comment_count`: `18` (matches RESEARCH §D-4's 2026-08-21 baseline exactly — **no delta**)
- `author`: `datapaganism`, `createdAt`: `2024-09-26T18:27:55Z`

**Five load-bearing comments, captured verbatim:**

| Date | Author | Substance |
|---|---|---|
| 2025-09-28T18:14:03Z | `AndersBNielsen` | The page-write analysis: 28C256 enters page-write mode above 1 byte; accepts up to 64 bytes before a 150µs timeout latches the page; workarounds and a fix suggestion given. |
| 2026-07-30T16:00:19Z | `henols` | The FIX-06 conflation answer: two defects (an inverted command-emitter success check, and a page-verification conflation of "write finished" with "data landed"); states no AT28C silicon was tested; asks for a `write`/`verify` re-test and offers `dev test`. |
| 2026-08-03T09:33:02Z | `datapaganism` | Reports hand-hacking a `CMD_ERASE` into `configure_eeprom28c`; asks how to trigger it from `firestarter` and whether the app blocks it. |
| 2026-08-03T09:36:48Z | `henols` | **"It's not probably implemented yet, I will soon get it pushed and I will keep you posted."** — an answer, and a commitment. Also asks about Anders' Discord. |
| 2026-08-03T09:47:39Z | `datapaganism` | "Yes but I am not using discord anymore ... reply directly here" — confirms the reply-on-the-issue preference. |

**Firmware tree confirmation** (`firestarter/src/proms/eeprom_28c.cpp` @ `8b7feac`):

- `grep -c 'eeprom28c_erase_execute'` → `3` (declaration `:150`, dispatch-arm comment `:246`, definition `:545`)
- `grep -c '0544'` → `7` (lines `63, 148, 246, 499, 501, 518, 527`)
- `case CMD_ERASE:` at `:262-263` dispatches to `eeprom28c_erase_execute`, confirmed live.

**Delta against RESEARCH §D-4:** none. Every measured field matches the recorded baseline exactly.

## Task 3 — Freeze and Handoff Data (verbatim)

- **Blob SHA** (`git hash-object 152-GH11-COMMENT.md`): `8bcffe965b96ccd7351837ab9b784dcdf603ad39`
- **Commit SHA** (`git log --oneline -1 -- .../152-GH11-COMMENT.md`): `df04127a`
- ⚠ **The blob SHA is an intent oracle and never a landed oracle** — it proves what was authored, not what GitHub stored. Plan 152-16 must use the body-content re-read (`gh issue view 11 --json comments --jq '.comments[-1].body'` diffed against this draft) as its sound post-verification oracle, per RESEARCH §D-5.
- **Baseline comment count:** `18`, captured via `gh issue view 11 --repo henols/firestarter_prom --json comments --jq '.comments | length'` at `2026-08-21T15:24:20Z`. Plan 152-16 re-captures this immediately before posting and must assert a delta of exactly `1` after posting.
- **The two `gh` invocations for Plan 152-16:**
  - Post: `gh issue comment 11 --repo henols/firestarter_prom --body-file .planning/phases/152-outward-facing-close-operator-gated/152-GH11-COMMENT.md`
  - Verify: `gh issue view 11 --repo henols/firestarter_prom --json comments --jq '.comments[-1].body'` piped into `diff -u - .planning/phases/152-outward-facing-close-operator-gated/152-GH11-COMMENT.md`
- **Branch confirmation:** `git -C /workspaces rev-parse --abbrev-ref HEAD` → `gsd/v1.32-at28c-write-path-root-cause-report-provenance` (unchanged after commit).

## Gate Verification

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_152="$(pwd)/152-GH11-COMMENT.md" python3 152-check-claims.py; echo "GATE rc=$?"
PASS: scanned 152-GH11-COMMENT.md; 1 of 1 caveat-required file(s) carry every caveat their own rule
demands; 0 file(s) carry no caveat requirement (this PASS is compliance with the forbidden-phrase
table and the per-file caveat rule only ...)
GATE rc=0
```

Ten acceptance-criteria greps from Task 2, all matched expected counts:

| Grep target | Expected | Measured |
|---|---|---|
| `keep you posted` | ≥1 | 1 |
| `DS20006386B` | ==1 | 1 |
| `conflation` | ≥1 | 1 |
| `fw --install` | ≥1 | 2 |
| `No AT28C part was tested at any point in v1.32` | ==1 | 1 |
| `discord` (case-insensitive) | ==0 | 0 |
| `sorry\|apolog` (case-insensitive) | ==0 | 0 |
| `support_status` | ==0 | 0 |
| `check_dispatch` | ==0 | 0 |
| `3\.0\.0b[0-9]+` | ==0 | 0 |

`python3 -m pytest test_check_claims_152.py -q -o addopts=""` → `30 passed` (no regression in the existing gate suite from authoring this draft).

## Decisions Made

- Framed the 2026-08-03 exchange as a kept-late promise (18 days), never as a broken silence, per RESEARCH §D-4's correction to CONTEXT's "unanswered" framing.
- Rephrased the "no support_status field moved" §B-10 bullet as "no chip's support classification in the database moved" so the literal forbidden string `support_status` never appears in the posted artifact, while preserving the same factual claim.
- Deliberately omitted a literal "gh#11" self-reference inside the gh#11 comment, avoiding any proximity to the `issue-closed` forbidden-pattern row rather than relying on word-distance margins.
- Kept both install halves (`pip install --pre --upgrade firestarter`, `firestarter fw --install`) explicit in the ask, per RESEARCH §B-8's matched-firmware consequence — the host's `dev test`/`write` step sends no override flag, so the fix only takes effect on firmware running this milestone's build.

## Deviations from Plan

None - plan executed exactly as written. Task 1's live re-measurement found zero delta against RESEARCH §D-4, so no re-derivation of the draft's factual basis was needed.

## Issues Encountered

None. The known gate trap in `FORBIDDEN_PATTERNS` (the `verified-on-silicon` row, which has no leading word boundary and so also matches the negated form of that phrase) was avoided by construction — the draft never places the word "on" immediately after any verified/unverified form that is itself followed by "silicon"; the ledger-status sentence uses "in", not "on", after that form.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `152-GH11-COMMENT.md` is frozen, gate-clean, and ready for Plan 152-16's blocking operator checkpoint and post — nothing further is needed from this plan.
- Plan 152-16 has everything it needs recorded above: the blob/commit SHAs (intent oracle only), the 18-comment baseline with capture timestamp, and both `gh` invocations for posting and body-content verification.
- No blockers. This ships software-proven and unvalidated on silicon, and that stays true of the underlying erase/write-path work regardless of when this draft is posted — nothing in this plan changes that status.

---
*Phase: 152-outward-facing-close-operator-gated*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-GH11-COMMENT.md`
- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-07-SUMMARY.md`
- FOUND: commit `df04127a` in `git log --oneline --all`
