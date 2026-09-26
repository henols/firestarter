---
phase: 122-close-honesty-ledger-community-ask-release-decision
plan: 05
subsystem: infra
tags: [honesty-ledger, documentation, claim-scanner, release-close, at28c-sdp]

# Dependency graph
requires:
  - phase: 122-01
    provides: "check_permitted_claims.py, its paired test, and the four fixtures the scanner uses to prove it can fail"
  - phase: 122-04
    provides: "122-NONREGRESSION.md's merged-tree measurements (84/43/41 partition, DIP24_2816 0/19, 66-of-84 trace coverage, 568/572 µs, 2600 B free) that this ledger cites as its evidence register"
provides:
  - "122-LEDGER.md — the single source of permitted wording that the two prerelease bodies (Plan 122-09) and both community-comment drafts (Plan 122-10) must match"
  - "The C-5/D-14 locked-decision divergence recorded as an explicit, traceable, overturnable item for Plan 122-11's operator wording review"
  - "The nine claim-class rows, the four-0x0D-pinout composition table, five mechanism corrections, D-12's negative space, and the three-way sampling split, all scanner-clean"
affects: ["122-06", "122-08", "122-09", "122-10", "122-11", "122-13"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Cite a forbidden claim by file:line reference instead of reproducing its exact wording, when the claim scanner's phrase-shape matching would otherwise trip on the quotation itself"
    - "Record a locked-decision divergence in the evidence-of-record artifact (this ledger) rather than silently correcting it in the downstream draft that acts on it, so an operator override is traceable back to one place"

key-files:
  created:
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-LEDGER.md
  modified: []

key-decisions:
  - "Wrote nine claim-class rows instead of D-11's 'roughly eight' — the single timing claim splits into two rows with different sources and different dispositions: the SDP unlock emitter's measured duration (a gating figure, budgeted against 600 µs) and the page-load per-byte interval (context only, per Phase 119 D-16, never a gate). Recording the split here rather than silently, per the plan's own instruction."
  - "The C-5/D-14 divergence is recorded as an explicit flagged item, not silently corrected — D-14's original prescribed wording is cited by CONTEXT.md line reference (122-CONTEXT.md:185) rather than reproduced verbatim, because reproducing it would trip the ledger's own claim scanner (the 'should now work' pattern). The corrected, measured answer (0/19 DIP24_2816 ALLOW) replaces it in the ledger's own prose."
  - "Every occurrence of the substring 'all 84' was rewritten to an equivalent phrasing ('every one of the 84', 'the full 84-entry set', '84 of 84') during drafting, after an initial pass produced five literal hits against the plan's own hard grep -c 'all 84' == 0 gate — none of the five were the trace-coverage overclaim the gate exists to catch, but the gate is textual, not semantic, so all five were reworded rather than argued around."

requirements-completed: []  # This plan ticks nothing — CLOSE-01/02/03 close only in 122-13

coverage:
  - id: D1
    description: "122-LEDGER.md exists with pinned-provenance header, verbatim ceiling quote, nine claim-class rows (each with a non-empty non-claim cell), and the four-value status key"
    requirement: "CLOSE-01"
    verification:
      - kind: other
        ref: "cd .planning/phases/122-.../ && L=122-LEDGER.md && test -f $L && grep -q 'does NOT prove' $L && grep -c '^| \\*\\*[1-9]\\.' $L (returns 9) && grep -q PERMITTED $L && grep -q CONTEXT-ONLY $L && grep -q COMMUNITY-CORROBORATED $L && grep -q FORBIDDEN $L"
        status: pass
    human_judgment: false
  - id: D2
    description: "The four-0x0D-pinout composition table (84/43/41, DIP24_2816 0/19) and the emission-traced-vs-operation-permitted distinction, plus five mechanism corrections including the flagged C-5/D-14 divergence"
    requirement: "CLOSE-01"
    verification:
      - kind: other
        ref: "grep -q DIP24_2816 122-LEDGER.md && grep -q a8efaedc236c1d9718bd28299dfbb99536b010ff 122-LEDGER.md && grep -qi divergence 122-LEDGER.md && git status --porcelain -- .planning/REQUIREMENTS.md (empty)"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-12's negative space (SDP-F1..F8, Phase 121's two owned trade-offs, this phase's own D-01 trade-off), the three-way sampling split with the explicit criterion-4 non-claim, and check_permitted_claims.py exiting 0 against the ledger"
    requirement: "CLOSE-01"
    verification:
      - kind: other
        ref: "for f in SDP-F1..SDP-F8: grep -q $f 122-LEDGER.md (all present); grep -q 'criterion 4' 122-LEDGER.md; FIRESTARTER_CLAIMSCAN_TARGETS=<abs path> python3 check_permitted_claims.py -> exit 0, PASS line names 122-LEDGER.md"
        status: pass
    human_judgment: false
  - id: D4
    description: "The whole ledger reads honestly against the validation ceiling — this is D-16's operator judgement call, not a string-scan outcome"
    human_judgment: true
    rationale: "A green claim-scan (D1-D3 above) proves the absence of eight specific forbidden phrase shapes and the presence of the required caveat. It cannot judge whether the prose as a whole implies more than it should, whether the DIP24_2816 refusal is stated prominently enough, or whether tone drifts toward overclaiming. This is exactly D-16's blocking operator wording review, scheduled for Plan 122-11, and this ledger states its own non-claim on this point explicitly."

duration: 35min
completed: 2026-07-30
status: complete
---

# Phase 122 Plan 05: The v1.22 Honesty Ledger Summary

**Wrote `122-LEDGER.md` — nine claim-class rows pairing permitted wording with explicit non-claims, the measured four-pinout ALLOW/REFUSE partition, five mechanism corrections including a flagged locked-decision divergence, and D-12's negative space — scanner-clean on the first real run.**

## Performance

- **Duration:** ~35 min
- **Tasks:** 3 completed (single-file plan; all three tasks build one artifact incrementally)
- **Files modified:** 1 created

## Accomplishments

- Wrote the ledger's header with both inbound-merge commit SHAs pinned (firmware `953f748…`, host `4001396…`), a version-string caveat (merged trees read `3.0.0b13`; that string is not the identity of what gets published), and a `composes with (cross-reference only)` list — while leaving the published cut tag as an explicit `TBD` field for Plan 122-08 to fill with the *observed* tag, per RESEARCH's A3 warning never to assume `3.0.0b14`.
- Quoted `REQUIREMENTS.md`'s permitted claim verbatim; cited the forbidden claim by file:line reference instead of reproducing it, because reproducing it would trip this document's own scanner — the same deliberate interaction `122-NONREGRESSION.md` §7 already documented and resolved the same way.
- Wrote nine claim-class rows (not D-11's "roughly eight" — see Decisions), each pairing a permitted wording with an evidence citation and an explicit "does NOT prove" cell, closing with class 8's stated asymmetry: the defect is community-corroborated on real AT28C256 silicon, the fix is not.
- Wrote the four-`0x0D`-pinout composition table (84 chips / 43 ALLOW / 41 REFUSE; `DIP24_2816` at 0/19) as its own section, with the emission-traced-vs-operation-permitted distinction as a standalone paragraph — not a parenthetical — and the derived-provenance commit (`a8efaedc236c1d9718bd28299dfbb99536b010ff`) pinned.
- Recorded five mechanism corrections (`check_ledger.py`'s pre-existing RED, the actual zero/two-file conflict set, the C-5/D-14 divergence, the empty-body release mechanics, `diff_db.py`'s self-interpreted identity reading), opening with the statement that `REQUIREMENTS.md` is deliberately not edited for any of them.
- Recorded D-12's negative space: all eight `SDP-F1`..`SDP-F8` deferral reasons, Phase 121's two owned trade-offs (off-TTY `dev test` writes with no consent; `lockable-proms.md`'s missing provenance header), and this phase's own D-01 trade-off (no bench smoke-test of the b14 install/flash path).
- Reproduced `122-VALIDATION.md`'s three-way sampling split in the ledger's own voice — mechanically checkable / requires the D-16 operator review / inherently unverifiable at a sampling rate of zero, permanently, by design — stating explicitly that a green claim-scan does NOT satisfy ROADMAP criterion 4.
- Ran `check_permitted_claims.py` against the finished ledger via the `FIRESTARTER_CLAIMSCAN_TARGETS` env seam: **exit 0**, `PASS: scanned 122-LEDGER.md; 1 file(s) carry the required silicon caveat`.

## Task Commits

Single commit covers all three tasks — they build one artifact incrementally and were verified together before staging:

1. **Tasks 1–3: header, ceiling quote, status key, nine claim-class rows, pinout composition, mechanism corrections, negative space, three-way split, scanner PASS** — `79be6f0` (docs)

**Plan metadata:** captured in this SUMMARY's own commit (final step).

_Note: no TDD tasks in this plan; all three are `type="auto"` documentation tasks operating on one file._

## Files Created/Modified

- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-LEDGER.md` — the v1.22 honesty ledger (140 lines): pinned-provenance header, verbatim ceiling quote, four-value status key, nine claim-class table, four-pinout composition table with derived provenance, five mechanism corrections, D-12 negative space, three-way sampling split, scanner status note.

## Decisions Made

- **Nine rows, not "roughly eight" (D-11 deviation).** The single "measured host-side timing" claim splits into two rows with different sources and different dispositions: the SDP unlock emitter's duration (Class 2, a gating figure measured against a 600 µs budget — Leonardo 568 µs, with F-118-01's separate 572 µs observation cited but never averaged) and the page-load per-byte interval (Class 3, `CONTEXT-ONLY` — Phase 119 D-16 explicitly declined to gate on it). Recording the split here per the plan's own instruction rather than silently collapsing to eight.
- **The C-5/D-14 divergence is flagged, not silently fixed.** D-14's original prescribed wording (`122-CONTEXT.md:185`) is cited by line reference rather than quoted, because its exact phrase ("...AT28C parts should now work") would trip this ledger's own `should-now-work` scanner pattern — the pattern doing its job, per the scanner's own docstring guidance to reword rather than weaken the pattern set. The ledger states plainly what D-14 said and what research measured (0/19 `DIP24_2816` ALLOW), and names Plan 122-11 as the place this is put to the operator as an explicit accept-or-overturn — an overturn traces back to this row.
- **Every literal "all 84" substring was rewritten during drafting.** An initial pass produced five hits against the plan's hard `grep -c 'all 84' == 0` acceptance gate. None of the five were instances of the specific trace-coverage overclaim the gate targets (they were legitimate references to "all 84 chips" / "all 84 `0x0D` entries" in unrelated sentences), but the gate is a literal substring check, not a semantic one, so all five were reworded to equivalent phrasing (`every one of the 84`, `the full 84-entry set`, `84 of 84`) rather than treated as false positives to argue past.

## Line-by-line ceiling review (recorded per the plan's `<output>` instruction)

Read the finished ledger end to end against `.planning/REQUIREMENTS.md` §"Validation Ceiling" after Task 3's scanner run. Verdict:

- **Zero affirmative silicon-validation claims.** Every sentence asserting a positive result names a software artifact as its subject (a git blob identity, a golden trace, a pytest exit code, a source-scan result, a size report, a derived-partition computation) or, for Class 8 alone, explicitly and narrowly attributes the silicon-side observation to a named third party's own report — never to this project's own verification.
- **Every figure is measured, not predicted.** 66/84, 568/572 µs (cited separately, never averaged), 84/88 µs, 2600 B, 43/41, and the pinout 35/19/18/12 breakdown all trace to `122-NONREGRESSION.md`'s live re-execution on the merged tree.
- **The one superseded figure (`3348 B`) is labelled superseded** at its single occurrence, with the reason (Phase 117 `+204 B`, Phase 118 `+152 B`, already spent) stated inline.
- **The phrase "all 84" appears nowhere** in the committed file (`grep -c 'all 84'` → 0), confirmed after the rewrite pass above.
- **No claim implies the fix is silicon-effective.** Class 8's non-claim cell states the asymmetry — premise corroborated, fix unproven — in exactly those terms.

## Scanner result

`FIRESTARTER_CLAIMSCAN_TARGETS=<abs-path-to-122-LEDGER.md> python3 check_permitted_claims.py` → **exit 0**:

```
PASS: scanned 122-LEDGER.md; 1 file(s) carry the required silicon caveat (this PASS is the
mechanizable half of criterion 4 only -- see the module docstring's explicit non-claim)
```

The pattern set (`FORBIDDEN_PATTERNS`, `REQUIRED_CAVEAT_PATTERN`) was not touched — the ledger's prose was reworded to fit the existing gate, per the plan's explicit "reword, never weaken the pattern set" instruction. No exclusion list, no scanner edit.

## Deviations from Plan

None beyond the two documented above under Decisions Made (the nine-row split and the "all 84" rewrite pass), both of which the plan itself anticipated and instructed be recorded rather than treated as silent adjustments.

## Issues Encountered

- Initial draft produced 5 literal `all 84` substring matches against the plan's hard `grep -c` gate, none of them the semantic overclaim the gate targets. Resolved by rewording all five occurrences (see Decisions Made) rather than weakening or reinterpreting the gate — the gate is deliberately textual and strict.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `122-LEDGER.md` exists and is scanner-clean, making it usable as the single source of permitted wording for Plan 122-09's two prerelease bodies and Plan 122-10's two community-comment drafts (CONTEXT constraint 5).
- The C-5/D-14 divergence is recorded in a form Plan 122-11's blocking operator wording review can act on directly — accept the corrected wording as written, or overturn it, with the overturn traceable back to this ledger's mechanism-corrections section.
- `PROTOCOL-LEDGER.{md,json}` and `.planning/REQUIREMENTS.md` are both confirmed untouched (`git status --porcelain` empty for both paths) at every task boundary and after the final commit.
- No blocker. No requirement checkbox was ticked — `CLOSE-01`/`CLOSE-02`/`CLOSE-03` close only in Plan 122-13, per this plan's explicit scope.

---
*Phase: 122-close-honesty-ledger-community-ask-release-decision*
*Completed: 2026-07-30*

## Self-Check: PASSED

- FOUND: `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-LEDGER.md`
- FOUND: `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-05-SUMMARY.md`
- FOUND: `79be6f0` (ledger content commit)
- FOUND: `50cd797` (plan summary commit)
