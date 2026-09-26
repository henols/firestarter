---
phase: 152-outward-facing-close-operator-gated
plan: 05
subsystem: docs
tags: [gh12, claim-gate, gh-issue-comment, honesty-ledger, sdp, backlog-999.28]

requires:
  - phase: 137-close-honesty-ledger-claim-gate-gh12-followup
    provides: "the 137-GH12-COMMENT.md donor — the v1.30 reply that was never posted"
  - phase: 152-01
    provides: "152-CLAIM-CLASSES.md and 152-check-claims.py, the claim gate this draft is scanned against"
  - phase: 153-close-honesty-ledger-erase-guard-gate-mechanism-correction
    provides: "the shipped write-path facts this draft describes: dropped pre-write blank check, software AN-0544B erase, firmware-identifying dev test reports"
provides:
  - "152-GH12-COMMENT.md — the frozen, gate-clean OUT-01 draft reply for gh#12"
  - "152-GH12-COMMENT.diff — the committed D-14 review diff against the 137 original"
affects: [152-12, 152-14]

tech-stack:
  added: []
  patterns:
    - "copy-donor-verbatim-then-adapt-with-a-committed-diff (D-14): commit the byte-identical baseline first so the adaptation is a readable git diff, not just a standalone .diff artifact"

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-GH12-COMMENT.md
    - .planning/phases/152-outward-facing-close-operator-gated/152-GH12-COMMENT.diff
  modified: []

key-decisions:
  - "Kept the donor's two operator-reviewed paragraphs (the two-halves framing and the isn't-the-enable/disable paragraph) in substance, per D-14."
  - "Replaced the donor's now-false 'the design for one is settled and the work is queued' sentence with an explicit second-release withdrawal naming Backlog 999.28, no version promised, and the deferred command never named."
  - "Never named check_dispatch.py or support_status as write-path evidence, per the phase's known gate traps and the Phase 153 mechanism correction."

patterns-established: []

requirements-completed: [OUT-01]

coverage:
  - id: D1
    description: "152-GH12-COMMENT.md drafted: keeps the donor's two hardest paragraphs, states the second withdrawal with Backlog 999.28 named and no version promised, describes lock-status/write-path/report-provenance in D-11-exempt terms, asks for a fresh run naming both install halves, carries the mandated no-AT28C-part-tested sentence, and passes the phase's claim gate via the env seam."
    requirement: "OUT-01"
    verification:
      - kind: other
        ref: "FIRESTARTER_CLAIMSCAN_TARGETS_152=<abs>/152-GH12-COMMENT.md python3 152-check-claims.py"
        status: pass
      - kind: other
        ref: "eleven acceptance-criteria greps in 152-05-PLAN.md Task 2 (999.28, second release, skip-sdp-unlock, lock-status, fw --install, dev test, the mandated non-claim sentence, zero check_dispatch, zero support_status, both donor paragraphs, zero release tags)"
        status: pass
    human_judgment: true
    rationale: "This is a draft of a public-facing GitHub comment. A green claim-gate run is compliance with the forbidden-phrase table and per-file caveat rule only (the gate's own explicit non-claim) — it cannot detect an implied overclaim, a misleading omission, or a wrong tone. D-03's per-artifact blocking operator wording review (owned by Plan 152-14, before posting) is the control that discharges tone and framing; this plan cannot self-certify that."
  - id: D2
    description: "152-GH12-COMMENT.diff committed: a real unified diff against the 137 original, with a change-class (kept/changed/added/omitted) header outside the diff hunks, so the operator's wording review in Plan 152-14 can read the diff instead of the whole file."
    requirement: "OUT-01"
    verification:
      - kind: other
        ref: "diff -u 137-GH12-COMMENT.md 152-GH12-COMMENT.md structural checks: >=1 hunk, >=5 added lines, .diff absent from 152-check-claims.py defaults"
        status: pass
    human_judgment: false

duration: ~15min
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 05: gh#12 Reply Draft (OUT-01) Summary

**Adapted the frozen 137 gh#12 donor into a gate-clean second-release withdrawal naming Backlog 999.28, with the D-14 review diff committed alongside it.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-08-21 (session start)
- **Completed:** 2026-08-21T15:08:00Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- Committed a byte-identical copy of `137-GH12-COMMENT.md` as `152-GH12-COMMENT.md` in its own commit, giving the adaptation a real git-history diff baseline (D-14).
- Adapted the draft in place: kept the donor's two operator-reviewed paragraphs verbatim in substance; replaced the now-false "settled and queued" sentence with an explicit second-release withdrawal naming Backlog 999.28 and promising no version, without ever naming the deferred command; rewrote "What did get better" around `lock-status` (refusal-as-feature, beta-only, matched-firmware), the write path's dropped pre-write blank check plus its software AN-0544B standalone erase step, and firmware-identifying `dev test` reports; added a one-clause acknowledgment that this is the second install-and-test ask in a row; extended the install ask with the firmware half (`firestarter fw --install`) alongside the pre-release install; carried the mandated "No AT28C part was tested at any point in v1.32" sentence.
- Generated and committed `152-GH12-COMMENT.diff`, a real unified diff against the 137 original with a change-class header, confirmed absent from the gate's default scan targets.

## Task Commits

Each task was committed atomically:

1. **Task 1: Copy the 137 donor verbatim as the diff baseline** - `1ce2c19a` (docs)
2. **Task 2: Adapt the draft** - `5918054d` (docs)
3. **Task 3: Produce and commit the D-14 diff artifact** - `bacd2ca2` (docs)

**Plan metadata:** committed alongside this summary (docs: complete plan).

## Files Created/Modified
- `.planning/phases/152-outward-facing-close-operator-gated/152-GH12-COMMENT.md` - the frozen, gate-clean OUT-01 draft reply for gh#12
- `.planning/phases/152-outward-facing-close-operator-gated/152-GH12-COMMENT.diff` - the committed D-14 review diff against the 137 original

## Decisions Made
- Kept the donor's "two halves don't survive equally" framing and "this isn't the 'enable/disable' you asked for" paragraph in substance, including the unreadable-protection-bit limitation — these were flagged as the hardest sentences in the file and already operator-reviewed once.
- The withdrawal sentence now names Backlog 999.28 explicitly and states the ask is half-answered for a second release, replacing the donor's now-false "settled and queued" framing. The deferred deliberate-protection command is never named anywhere in the draft, matching the donor's own discipline and avoiding the gate's fifth forbidden class entirely.
- Described the write-path change using D-11-exempt phrasing (statements of shipped, user-visible command behaviour): the pre-write blank check is gone because a page write auto-erases internally on this protocol, and a standalone erase step exists via the manufacturer's software AN-0544B sequence — chosen because it carries no over-voltage hazard on this pinout — never citing `check_dispatch.py` as the guard (Phase 153 corrected that mechanism claim, it did not satisfy it).
- Never cited `support_status` as write-path evidence, and never named `AT28C256` specifically (used the generic "AT28C" family, per the chip-level vs. protocol-level axis distinction in the must-haves).
- Acknowledged in one clause that this is the second maintainer comment in a row asking the reporter to install a pre-release and test, per RESEARCH §D-2's tone requirement, without narrating the project's own milestone process.

## Deviations from Plan

None - plan executed exactly as written. All eleven of Task 2's acceptance-criteria greps passed on the first draft; no rework was needed.

## Issues Encountered

**Diff-artifact whitespace correction (self-caught, not a plan deviation):** When first assembling `152-GH12-COMMENT.diff`, the header-plus-body was hand-transcribed and lost the literal single-space prefix `diff -u` uses on unchanged blank context lines (a bare blank line is not equivalent to a line containing exactly one space in unified-diff format). This was caught by re-diffing the hand-transcribed body against a freshly-generated `diff -u` run before committing, and the file was rebuilt by concatenating the header with the actual `diff -u` output byte-for-byte rather than by hand-transcription. The committed artifact is confirmed byte-identical to a fresh `diff -u` run (plus the header). No commit of the flawed version occurred.

## User Setup Required

None - no external service configuration required. Nothing was posted anywhere; this plan authors a draft only. Plan 152-14 posts it, behind its own blocking operator checkpoint, after the beta merges.

## Next Phase Readiness

- `152-GH12-COMMENT.md` and `152-GH12-COMMENT.diff` are ready for the operator wording review that Plan 152-14 gates on before posting.
- The draft is version-agnostic (no release tag appears anywhere in it), so it does not need rework if the cut version changes before Plan 152-14 runs.
- No blockers. Nothing in this plan touches `firestarter/` or `firestarter_app/`; no submodule commits were made.

This ships software-proven and unvalidated on silicon.

---
*Phase: 152-outward-facing-close-operator-gated*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-GH12-COMMENT.md`
- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-GH12-COMMENT.diff`
- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-05-SUMMARY.md`
- FOUND commit `1ce2c19a` (Task 1)
- FOUND commit `5918054d` (Task 2)
- FOUND commit `bacd2ca2` (Task 3)
