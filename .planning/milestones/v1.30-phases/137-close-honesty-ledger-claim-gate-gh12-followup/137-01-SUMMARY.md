---
phase: 137-close-honesty-ledger-claim-gate-gh12-followup
plan: 01
subsystem: testing
tags: [claim-gate, honesty-ledger, pytest, regex, subprocess-testing, v1.30]

# Dependency graph
requires:
  - phase: 122-close-honesty-ledger-community-ask-release-decision
    provides: "check_permitted_claims.py's VOCABULARY donor — 8 forbidden AT28C/silicon patterns, REQUIRED_CAVEAT_PROSE shape, PASS-line shape"
  - phase: 123-non-regression-baselines-gate-hardening
    provides: "check_permitted_claims.py's MECHANICS donor — D-16 proximity window, D-15 all-or-nothing arming, hoisted never-vacuous guard (also the exact _HERE-resolves-to-a-sibling-dir defect this plan's two new legs exist to catch)"
provides:
  - "v1.30's own claim gate (check_permitted_claims.py), authored AND hosted in Phase 137's own directory, targets resolving via _HERE alone"
  - "14 forbidden-phrase patterns (8 inherited + 6 v1.30-specific) plus a relational self-verifying rule"
  - "11 subprocess-level pytest legs, including the two mandatory P-11 target-resolution/basename legs, both proven non-vacuous via two independent seen-to-fail-then-restore demonstrations"
  - "five committed fixtures (2 clean, 3 planted-violation) exercising the vocabulary and the self-verifying rule specifically"
affects: [137-06 (arms this gate against the four real artifacts and ticks CLOSE-01), 137-03 (137-LEDGER.md must pass this gate), 137-04 (137-RELEASE-NOTES-app.md must pass this gate), 137-05 (137-GH12-COMMENT.md must pass this gate)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Claim-gate fork discipline: vocabulary from one donor, mechanics from another, per PITFALLS.md P-11 — never copy either donor verbatim"
    - "_DEFAULT_TARGETS built exclusively from _HERE (os.path.dirname(os.path.abspath(__file__))), never a sibling-directory string constant"
    - "Suffixed env seam (_V130) + renamed test module (_v130.py) to defuse a 3-way collision across sibling phase directories"
    - "Relational forbidden-pattern rule (self-verifying) distinct from bare FORBIDDEN_PATTERNS matches — requires absence of a qualifier in the same proximity window, not just presence of the trigger word"

key-files:
  created:
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/check_permitted_claims.py
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/test_check_permitted_claims_v130.py
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/fixtures/clean_control.md
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/fixtures/clean_control_second.md
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/fixtures/planted_forbidden_claim.md
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/fixtures/planted_missing_caveat.md
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/fixtures/planted_self_verifying_unqualified.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Followed the plan's exact instruction to fork Phase 122's 8 forbidden patterns verbatim (same labels, same regexes) rather than re-deriving them, to keep the AT28C/silicon vocabulary that already correctly detects the v1.22 C-5 overclaim shape"
  - "Ran BOTH P-11 mandatory legs' deliberate-break controls (not just the single one the plan's Task 3 acceptance criteria names), to satisfy the orchestrator's explicit 'both target-resolution legs present and non-vacuous' success criterion — confirmed each mutation flips exactly one leg red and leaves the other green, proving the two legs are independent, not redundant"
  - "The self-verifying rule's qualifier check (emission OR caveat presence) is layered on top of, not instead of, the general SDP-context proximity filter — in practice the caveat's own literal 'AT28C' text always also satisfies the SDP-context check, so the OR is belt-and-braces per the plan's own note, not load-bearing today"

requirements-completed: [CLOSE-02]

coverage:
  - id: D1
    description: "v1.30 claim gate authored and hosted inside Phase 137's own directory, vocabulary forked from Phase 122, mechanics forked from Phase 123, 6 new v1.30-specific forbidden patterns plus a relational self-verifying rule, currently UNARMED + exit 0 (correct — none of the four real artifacts exist yet)"
    requirement: "CLOSE-02"
    verification:
      - kind: unit
        ref: "check_permitted_claims.py run with no args — prints UNARMED: naming all four 137-prefixed basenames, exit 0"
        status: pass
      - kind: unit
        ref: "test_check_permitted_claims_v130.py::test_unarmed_when_zero_of_four_default_targets_exist"
        status: pass
    human_judgment: false
  - id: D2
    description: "Two mandatory P-11 target-resolution/basename legs exist, pass, and are proven non-vacuous via two independent seen-to-fail-then-byte-identically-restored demonstrations"
    requirement: "CLOSE-02"
    verification:
      - kind: unit
        ref: "test_check_permitted_claims_v130.py::test_default_targets_resolve_inside_this_phase_directory"
        status: pass
      - kind: unit
        ref: "test_check_permitted_claims_v130.py::test_default_target_basenames_are_this_milestones"
        status: pass
    human_judgment: false
  - id: D3
    description: "Five committed fixtures (2 clean, 3 planted) prove the vocabulary and the self-verifying rule are non-hollow"
    verification:
      - kind: unit
        ref: "test_check_permitted_claims_v130.py (11 legs, includes tests 1-4 and 7-8 exercising all five fixtures) -o addopts=\"\" -q"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-08-05
status: complete
---

# Phase 137 Plan 01: v1.30 Claim Gate (CLOSE-02) Summary

**Forked v1.30's own claim gate from Phase 122's vocabulary + Phase 123's mechanics per PITFALLS.md P-11, hosted inside Phase 137's own directory so `_DEFAULT_TARGETS` can never repeat the sibling-dir resolution defect, and proved the two mandatory target-resolution/basename tests non-vacuous via two independent seen-to-fail-then-restore demonstrations.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-05T17:26:00Z (plan/context read)
- **Completed:** 2026-08-05T17:46:00Z
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 8 (2 new source files, 5 fixtures, 1 REQUIREMENTS.md edit)

## Accomplishments

- `check_permitted_claims.py` authored fresh inside `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/` — `_DEFAULT_TARGETS` resolves exclusively via `_HERE` (this module's own directory computed from `__file__`), with no sibling-directory string constant anywhere in the file. Fourteen forbidden-phrase labels shipped, all case-insensitive:
  - **8 inherited verbatim from Phase 122's copy:** `verified-fixed`, `confirmed-working`, `silicon-verified`, `verified-on-silicon`, `works-on-silicon`, `now-works`, `should-now-work`, `proven-on-silicon`.
  - **6 new v1.30-specific patterns** (PITFALLS.md P-11 point 2, cross-checked against REQUIREMENTS.md's Evidence Ceiling section): `lock-inhibited-the-write`, `lock-held-unqualified` (deliberately requires the words "the", "lock", "held" in that order so it never collides with the literal rendered `HELD`/`NOT-HELD` enum values from `chip_test.sdp_hold_state()`, which are permitted data, not a prose causal claim), `proven-behaviour`, `behaviourally-verified`, `now-proven`, `dev-test-proves-unqualified`.
  - **Relational self-verifying rule** (`_SELF_VERIFYING_PATTERN`, handled outside `FORBIDDEN_PATTERNS`): a bare "self-verifying" near an SDP/AT28C/0x0D context token is a violation UNLESS the immediately surrounding `[i-1, i, i+1]` line window also carries the literal word **"emission"** or the required caveat pattern itself. E.g. "a self-verifying SDP lifecycle for lock EMISSION" is permitted; bare "the new SDP lifecycle is self-verifying" with no nearby qualifier is not.
  - Suffixed env seam `FIRESTARTER_CLAIMSCAN_TARGETS_V130` (never the bare unsuffixed name anywhere in the source, including comments — verified via `grep -c 'FIRESTARTER_CLAIMSCAN_TARGETS\b'` returning 0) to avoid a third checker colliding with the two unsuffixed copies already on disk (Phase 122's, Phase 123's).
  - All-or-nothing arming (v1.23 D-15 mechanics): a partial set (1-3 of 4 default targets present) is a hard `FAIL:`, never `UNARMED:` — only zero-of-four is legitimately UNARMED.
  - **Observed UNARMED behavior, verbatim:** `UNARMED: none of Phase 137's 4 named closing artifacts exist yet (137-LEDGER.md, 137-DECISION.md, 137-RELEASE-NOTES-app.md, 137-GH12-COMMENT.md) -- Phase 137's four closing artifacts do not exist yet -- this is expected before they are authored, not a failure.` Exit 0 — correct and expected at this wave; none of the four real artifacts exist yet (they are authored by Plans 137-03, 137-04, and 137-05).

- Five fixtures committed under `fixtures/`: `clean_control.md` and `clean_control_second.md` (textually different, both carry the canonical `no AT28C silicon was tested` caveat verbatim, zero forbidden matches, PASS both singly and jointly, jointly naming both basenames); `planted_forbidden_claim.md` (trips `lock-inhibited-the-write` — the real Evidence Ceiling causal overclaim, not a synthetic one); `planted_missing_caveat.md` (caveat sentence removed, zero forbidden matches, fails on the missing-caveat bucket only); `planted_self_verifying_unqualified.md` (the caveat sentence sits on line 5 and the unqualified "self-verifying" claim on line 17 — 12 lines apart — genuinely exercising the proximity-window relational rule rather than relying on same-line coincidence).

- `test_check_permitted_claims_v130.py` — 11 subprocess-only pytest legs (never an in-process import of the scanner), 11/11 passing. Legs 1-9 fork Phase 122's seven-leg subprocess shape plus a self-verifying-specific leg and a current-state UNARMED leg. Legs 10-11 are the two **mandatory P-11 legs**:
  - `test_default_targets_resolve_inside_this_phase_directory` — imports the scanner by file path via `importlib.util.spec_from_file_location` and asserts every `_DEFAULT_TARGETS` entry's `os.path.dirname(...)` equals this test module's own resolved directory.
  - `test_default_target_basenames_are_this_milestones` — asserts every `_DEFAULT_TARGETS` basename starts with `"137-"`.

## Non-Vacuity Proof (both P-11 legs, not just the plan's single mandated one)

The plan's own Task 3 acceptance criteria named exactly one deliberate-break control (renaming `"137-LEDGER.md"` to `"130-LEDGER.md"`, confirming leg 11 goes RED). The orchestrator's own success criteria additionally required **both** target-resolution legs to be proven non-vacuous, so both were exercised, each under its own distinct mutation, each cross-checked to leave the *other* leg green (proving the two legs test genuinely independent properties, not the same thing twice):

**Mutation 1 — basename staleness (matches the plan's mandated control):**
`_DEFAULT_TARGETS`'s `"137-LEDGER.md"` entry temporarily renamed to `"130-LEDGER.md"`.
- `test_default_target_basenames_are_this_milestones` went RED, observed verbatim:
  ```
  AssertionError: _DEFAULT_TARGETS basename '130-LEDGER.md' does not carry this milestone's own '137-' prefix -- this is the exact stale-name defect this test exists to catch
  ```
- `test_default_targets_resolve_inside_this_phase_directory` stayed GREEN (dirname unaffected by a basename-only change) — confirming the two legs are independent.
- Reverted; `diff` against the pre-mutation copy was empty (byte-identical); 11/11 passed again.

**Mutation 2 — sibling-directory escape (the exact v1.23 P-11 defect class):**
One `_DEFAULT_TARGETS` entry temporarily joined through `os.pardir` (`os.path.join(_HERE, os.pardir, "137-LEDGER.md")`), escaping `_HERE`.
- `test_default_targets_resolve_inside_this_phase_directory` went RED, observed verbatim:
  ```
  AssertionError: _DEFAULT_TARGETS entry '/workspaces/.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/../137-LEDGER.md' does not resolve inside this phase's own directory '/workspaces/.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup' -- this is the exact cross-phase-copy defect this test exists to catch
  ```
- `test_default_target_basenames_are_this_milestones` stayed GREEN (basename unaffected by a directory-escape change) — confirming independence in the other direction.
- Reverted; `diff` against the pre-mutation copy was empty (byte-identical); 11/11 passed again.

Both mutations, both observed-RED messages, and both restorations are recorded here verbatim, per the objective's non-vacuity mandate.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author `check_permitted_claims.py`** - `a61a7814` (feat)
2. **Task 2: Commit five fixtures** - `fcd10742` (test)
3. **Task 3: Pair the gate with 11 subprocess pytest legs** - `997b16b9` (test)

**Plan metadata:** (this commit, following SUMMARY write)

## Files Created/Modified

- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/check_permitted_claims.py` - the v1.30 claim gate, 14 forbidden patterns + self-verifying relational rule, all-or-nothing arming, currently UNARMED
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/test_check_permitted_claims_v130.py` - 11 subprocess-only pytest legs, including the two mandatory P-11 legs
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/fixtures/clean_control.md` - clean control 1
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/fixtures/clean_control_second.md` - clean control 2 (textually different)
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/fixtures/planted_forbidden_claim.md` - trips `lock-inhibited-the-write`
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/fixtures/planted_missing_caveat.md` - trips the missing-caveat bucket
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/fixtures/planted_self_verifying_unqualified.md` - trips the self-verifying relational rule
- `.planning/REQUIREMENTS.md` - CLOSE-02 ticked `[x]` with evidence citation; traceability table row updated to Complete. No other requirement checkbox touched.

## Decisions Made

- Forked Phase 122's 8 forbidden patterns verbatim (same labels, same regexes) rather than re-deriving — the plan's own instruction, and the right call since that vocabulary already correctly detects the v1.22 C-5 overclaim shape.
- Ran both P-11 mandatory legs' deliberate-break controls (the plan's Task 3 only mandated one), to satisfy the orchestrator's explicit "both target-resolution legs present and non-vacuous" success criterion, and to demonstrate the two legs are independent rather than redundant.
- Kept the self-verifying rule's window-based qualifier check (emission OR caveat) layered on top of the general SDP-context proximity filter exactly as specified, even though in every fixture built here the caveat's own literal "AT28C" text already independently satisfies the SDP-context check — the OR is belt-and-braces, not load-bearing, exactly as the plan's own note predicts.

## Deviations from Plan

None — plan executed exactly as written. The one addition beyond the plan's literal Task 3 acceptance criteria (running both P-11 legs' seen-to-fail demonstrations instead of only the one named) is not a deviation from the plan's own intent — it satisfies the same objective (proving both mandatory legs non-vacuous) more completely, and is explicitly permitted by the plan's own phrasing that legs 10 and 11 are "both mandatory."

## Known Stubs

None. No hardcoded empty values, placeholder text, or unwired data sources were introduced. The scanner's own `UNARMED:` state is not a stub — it is a designed, tested, and load-bearing state (Non-Vacuity Obligations table, `137-VALIDATION.md`) that correctly reflects that the four real closing artifacts are authored by later plans in this phase.

## Threat Flags

None. This plan introduces no new network endpoint, auth path, file-access pattern, or schema change at a trust boundary — it is a standalone, stdlib-only, read-only scanner over `.md` files inside its own phase directory, exactly matching the threat model's own T-137-01 through T-137-05 register (all `mitigate` or `accept`, none newly discovered).

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The v1.30 claim gate mechanism is proven correct via fixtures, in its legitimate UNARMED state, before any of the four real closing artifacts exist — exactly the design 137-VALIDATION.md calls for ("Wave 0 Requirements": no Wave 0 needed; the UNARMED state is a legitimate, tested, non-failing state).
- Plans 137-03 (`137-LEDGER.md`), 137-04 (`137-RELEASE-NOTES-app.md`), and 137-05 (`137-GH12-COMMENT.md`) can each validate their own artifact against this gate via `FIRESTARTER_CLAIMSCAN_TARGETS_V130=<path> python3 check_permitted_claims.py` as they are authored.
- Plan 137-06 is the only plan that may tick CLOSE-01 — once all four artifacts exist, it re-runs the gate with no arguments and expects `PASS:` naming all four.
- CLOSE-02 is the only requirement this plan ticks. Project-wide requirement state after this plan: 50 ticked `[x]` / 6 open (`CLOSE-01`, `CLOSE-03`, `CLOSE-04`, `CLOSE-05`, `CLOSE-06`, `RELOCK-07`) — confirmed by direct grep count, matching the mandated ticking scope exactly.

---
*Phase: 137-close-honesty-ledger-claim-gate-gh12-followup*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: `check_permitted_claims.py`
- FOUND: `test_check_permitted_claims_v130.py`
- FOUND: `fixtures/clean_control.md`
- FOUND: `fixtures/clean_control_second.md`
- FOUND: `fixtures/planted_forbidden_claim.md`
- FOUND: `fixtures/planted_missing_caveat.md`
- FOUND: `fixtures/planted_self_verifying_unqualified.md`
- FOUND commit `a61a7814` (Task 1)
- FOUND commit `fcd10742` (Task 2)
- FOUND commit `997b16b9` (Task 3)
- Re-confirmed `check_permitted_claims.py` byte-identical to its state immediately after Task 1's commit (both deliberate-break mutations fully reverted)
- Re-ran `test_check_permitted_claims_v130.py -o addopts="" -q`: 11 passed
