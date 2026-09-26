---
phase: 149-firmware-page-size-seam-dual-repo-lockstep
plan: 02
subsystem: honesty-gate
tags: [claim-gate, regex, pytest, subprocess, fixtures]

# Dependency graph
requires:
  - phase: 149-01
    provides: "149-PAGE-SIZE.md skeleton carrying the software-proven-and-unvalidated-on-silicon phrase (D-16), which this plan's gate is armed against"
provides:
  - "149-check-claims.py: D-19 phase-local claim gate, 17 forbidden patterns (12 donor + 5 new), 1 required caveat, single-entry _DEFAULT_TARGETS"
  - "the X-2 bare-claim-word collision resolved: a negative lookbehind requiring an immediately preceding 'software-' permits only PGSZ-05's mandated compound, operator-reviewed and approved"
  - "test_check_claims_v132.py: 20-leg paired suite (15 donor legs renamed + 5 phase-specific legs)"
  - "10 committed fixtures (2 clean controls + 8 isolated plants, one per forbidden label this phase added or modified)"
  - "149-CLAIM-GATE-TRANSCRIPTS.md: committed RED (8 blocks) and GREEN (1 block) evidence, deliberately excluded from _DEFAULT_TARGETS"
affects: [149-03, 149-04, 149-05, 149-06, 149-07, 149-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Negative lookbehind to narrow (not drop) a forbidden pattern that collides with a mandated required phrase, shown satisfiable by both a forward fixture (phrase alone passes) and a negative control (the bare claim word still fails)"
    - "Per-basename _CAVEAT_RULES exemption for an evidence/transcript file, mirroring the donor's D-11 146-CORRECTIONS.md exemption, with the fail-closed default (unmapped basename -> FULL caveat set) left untouched"

key-files:
  created:
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-check-claims.py
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/test_check_claims_v132.py
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/clean_control.md
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/clean_control_second.md
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/planted_forbidden_claim.md
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/planted_missing_caveat.md
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/planted_proven_unqualified.md
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/planted_page_size_proven.md
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/planted_graduation.md
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/planted_support_status_change.md
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/planted_issue_closed.md
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/planted_at28c256_fixed.md
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-CLAIM-GATE-TRANSCRIPTS.md
  modified: []

key-decisions:
  - "Narrowed the bare-claim-word pattern with a negative lookbehind requiring an immediately preceding 'software-' (149-RESEARCH.md §X-2) — permits only PGSZ-05's mandated 'software-proven' compound; still fires on the word standalone, on the word followed by 'on silicon', and on the word prefixed by 'bench-', 'silicon-', or 'datasheet-'. Operator reviewed the exact lookbehind width and approved: 'approved'."
  - "Added one _CAVEAT_RULES entry not in task 1's literal action text: 149-CLAIM-GATE-TRANSCRIPTS.md -> frozenset() (empty caveat set), mirroring the donor's D-11 146-CORRECTIONS.md exemption, so legs 14/15 (the caveat-exempt-basename behavioral pair specified by 149-PATTERNS.md) have a real committed basename to exercise instead of an invented one. Operator was shown this deviation and accepted it."
  - "_DEFAULT_TARGETS holds exactly one entry (149-PAGE-SIZE.md) at this plan's authoring time, per 149-RESEARCH.md §R9e option 1 — the gate is armed while the artifact is being written, not deferred to the phase's final plan. Plan 08 extends the list to every 149-*-SUMMARY.md."

patterns-established:
  - "Every fixture text is probed in-memory against the gate's own scan_text() before being written to disk, so a leg's asserted label is never a coincidence — caught one contamination case during authoring (a fixture's own HTML-comment header spelling out a label name that itself contained the bare claim-word suffix, tripping the pattern it was documenting)."

requirements-completed: []  # PGSZ-05 spans multiple plans; per this phase's planner_decisions, plan 08 alone flips PGSZ-01...05

# Metrics
duration: ~50min
completed: 2026-08-19
status: complete
---

# Phase 149 Plan 02: The D-19 Phase-Local Claim Gate Summary

**Authored the D-19 claim gate over `149-PAGE-SIZE.md`, resolved the measured bare-claim-word / PGSZ-05 collision with a negative-lookbehind narrowing shown satisfiable by both a forward fixture and a negative control, and got the operator's explicit sign-off on the narrowing's exact width before the rest of the phase relies on it.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-08-19
- **Tasks:** 3/3 completed (2 `auto` + 1 `checkpoint:human-verify`, operator-approved)
- **Files modified:** 13 created (1 gate script, 1 paired suite, 10 fixtures, 1 transcript file), 0 modified outside this plan's own new files

## Accomplishments

- `149-check-claims.py` is a Phase-149-scoped sibling of the Phase 146 donor gate: 17 forbidden patterns (the donor's 12, with the bare-claim-word label narrowed and 5 new phase-specific labels — a page-size-validation-claim label, `graduation`, `support-status-change`, `issue-closed`, `at28c256-fixed`), 1 required caveat (PGSZ-05's literal phrase), a single-entry `_DEFAULT_TARGETS` built from a `__file__`-derived `_HERE`, no globbing anywhere, and the donor's fail-closed exit-code contract (never 0 on nothing scanned, never 0 on a missing target).
- The measured `149-RESEARCH.md` §X-2 collision — the donor's bare-word pattern would forbid PGSZ-05's own mandated phrase, "software-proven and unvalidated on silicon" — is resolved by narrowing the lookbehind to require an immediately preceding "software-". Verified two ways: a forward fixture whose only occurrence of the claim word is inside the mandated compound passes clean, and a negative-control fixture with a bare, differently-prefixed claim word still fails, named by label, in both the paired suite and the committed transcript.
- `test_check_claims_v132.py`: 20 legs, all green — the donor's 15 legs transcribed and renamed to this phase's own module/env-seam, plus 5 new legs covering the X-2 forward/negative-control pair, the transcript/upstream-artifact exclusion pair, and an every-added-label-has-an-isolated-fixture leg.
- 10 fixtures committed: 2 clean controls (both carrying the required caveat, so the anti-skip PASS-line leg is non-trivial) and 8 planted violations, one per forbidden label this phase added or modified — each probed in-memory against the gate's own `scan_text()` before being written, so every leg's asserted label is a measured fact, not an assumption.
- `149-CLAIM-GATE-TRANSCRIPTS.md` commits 8 RED blocks (one per added/modified label plus the two donor-carried rows) and 1 GREEN block (the real `149-PAGE-SIZE.md` target, no argv, no seam), plus the pytest run — all pasted as literal command + literal output. It opens with a bold warning that it deliberately carries forbidden vocabulary as evidence and is deliberately excluded from `_DEFAULT_TARGETS`; two test legs assert that exclusion, alongside the exclusion of `149-CONTEXT.md`, `149-RESEARCH.md` and `149-DISCUSSION-LOG.md`.
- **Task 3 checkpoint (blocking, `gate="blocking"`):** presented the narrowing's exact width, the automated width-probe results, and the dual-submodule liveness/cleanliness checks to the operator. The operator reviewed and responded **"approved"** — the `(?<!software-)` lookbehind is accepted as the minimum narrowing, with no pattern change requested. The operator was also shown, and separately accepted, the `_CAVEAT_RULES` deviation below.
- Both sub-repos were confirmed real, populated git repositories (`git rev-parse --git-dir` succeeded in both `firestarter` and `firestarter_app` — the leg an empty worktree submodule fails). `firestarter`'s working tree is clean. `firestarter_app`'s pre-existing state carries **no tracked, modified content** (`git status --porcelain --untracked-files=no` returned empty output) — its only non-clean state is untracked files left over from earlier phases (`SECURITY.md`, `datasheets/*.pdf`, `write_test_port.sh`, `.planning/config.json`), none of them touched by this plan.

## Task Commits

Each task was committed atomically in the meta repo (no `firestarter`/`firestarter_app` commit — this plan touches only `.planning/`):

1. **Task 1: Author `149-check-claims.py` from the 146 donor, with the narrowed bare-claim-word pattern** — `22bd6e9f` (feat)
2. **Task 2: Author the paired suite, the fixtures, and the committed RED/GREEN transcripts** — `8208d9e6` (test)
3. **Task 3: Operator review of the narrowed bare-claim-word pattern** — no code commit (checkpoint decision only); the operator's "approved" response is recorded here and in this SUMMARY's key-decisions.

**Plan metadata:** committed alongside this SUMMARY (see below).

## Files Created/Modified

- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-check-claims.py` — the D-19 claim gate (497 lines at task 1, +14 lines at task 2 for the transcript exemption entry)
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/test_check_claims_v132.py` — the 20-leg paired suite
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/*.md` — 10 fixtures (2 clean, 8 planted)
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-CLAIM-GATE-TRANSCRIPTS.md` — committed RED/GREEN evidence, never quoted here (see below)

**Note on this SUMMARY's own compliance:** per plan 08's future extension of `_DEFAULT_TARGETS` to every `149-*-SUMMARY.md`, no planted overclaim text is quoted anywhere in this document — see `149-CLAIM-GATE-TRANSCRIPTS.md` by path for the literal RED output instead.

## Decisions Made

1. **The X-2 narrowing is a negative lookbehind requiring an immediately preceding "software-", exactly, one occurrence** — verified by both the paired suite and the operator's manual review of the exact regex text. The operator explicitly confirmed it is not the wider hyphen-only lookbehind form, which would have silently also permitted a "bench-", "datasheet-" or "silicon-" prefixed variant of the claim word.
2. **Deviation — one `_CAVEAT_RULES` entry beyond task 1's literal action text.** Task 1's action said to map only `"149-PAGE-SIZE.md"` in `_CAVEAT_RULES`. Task 2's specified leg list (from `149-PATTERNS.md` §5, transcribing the donor's legs 14/15) requires a *caveat-exempt basename* to exercise behaviorally — but 149's caveat table has exactly one required caveat and, as authored in task 1, no basename mapped to an empty set. Rather than invent a fictitious exempt basename with no real referent, `149-CLAIM-GATE-TRANSCRIPTS.md` (a real, committed artifact of this same plan) was added to `_CAVEAT_RULES` mapped to `frozenset()`, mirroring the donor's own D-11 exemption for `146-CORRECTIONS.md` (an evidence register, not a claim body). This entry is inert in normal gate operation — the transcript file is never a member of `_DEFAULT_TARGETS` and is never passed via argv or the env seam by any real invocation (asserted by `test_the_transcript_file_is_not_a_gate_target`) — it exists solely so legs 14/15 prove the exemption mechanism behaviorally rather than only by introspection. **Unknown basenames still fail CLOSED to the full caveat set** (`_required_caveats_for()`'s default, verified by `test_unrecognised_basename_resolves_to_the_full_caveat_set`), so a future rename of a real artifact cannot silently disable its caveat check — this exemption is a single, explicitly named, documented entry, not a loosening of the fail-closed default. The operator was shown this deviation during the checkpoint and accepted it.
3. **`_DEFAULT_TARGETS` holds one entry at this plan's authoring time** (`149-RESEARCH.md` §R9e option 1) — arms the gate against the one real artifact that exists now (`149-PAGE-SIZE.md`), rather than deferring all scanning to the phase's final plan. Plan 08 extends the list to every `149-*-SUMMARY.md`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] The gate's own module docstring tripped its own literal-text acceptance criteria**
- **Found during:** Task 1
- **Issue:** The plan's automated verify checks `src.split('_HERE')[1][:120]` for `__file__` (to confirm `_HERE` is `__file__`-derived) and `src.count('(?<!software-)')==1` and rejects any literal `*.md` substring anywhere in the file (anti-glob check). The module docstring, written to explain the gate's own mechanisms in prose, initially (a) mentioned `` `_HERE` `` by name before the real assignment line, (b) quoted the literal lookbehind text `(?<!software-)` twice more in explanatory prose beyond the one code occurrence, and (c) wrote out `` `149-*.md` `` as an example of a rejected wildcard form.
- **Fix:** Reworded the docstring to describe the `_HERE` construction without using the literal backtick-quoted name before its assignment; described the lookbehind's exact prefix in prose without repeating the regex literal; replaced the `149-*.md` example with an equivalent prose description ("a wildcard `149-`-prefixed default").
- **Files modified:** `149-check-claims.py`
- **Verification:** Re-ran the plan's exact task-1 automated verify block after each fix; all assertions pass.
- **Committed in:** `22bd6e9f` (part of task 1 commit — the docstring was never committed in a failing state)

---

**Total deviations:** 1 auto-fixed (Rule 3) + 1 deliberate scope addition (documented above, operator-approved, not a rule-based auto-fix since it required judgment about a real vs. invented exempt basename).
**Impact on plan:** No scope creep. The docstring fix was necessary to satisfy the plan's own literal acceptance criteria without weakening any documented rationale. The `_CAVEAT_RULES` addition is a single, real, inert, documented entry that makes two already-specified test legs behaviorally meaningful; it does not touch `_DEFAULT_TARGETS`, does not add a second caveat, and does not weaken the fail-closed default for any unmapped basename.

## Issues Encountered

During fixture authoring, a fixture's own HTML-comment header — spelling out the forbidden page-size-validation-claim label name for a human reader — was itself flagged by the gate as a bare-claim-word violation, because the label string contains the claim word immediately preceded by a non-`software-` sequence. Caught by the mandatory in-memory `scan_text()` probe run against every fixture text before writing it to disk (per this plan's own "probed before committed" discipline, inherited from the donor). Resolved by rewording the affected comment to describe the label's behavior instead of quoting its literal name. No fixture was committed in a state that tripped an unintended second label.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Plan 03 (DB-side provenance-keyed emit arm) can proceed independently of this plan's gate — the gate does not scan any DB or firmware source path, only `149-PAGE-SIZE.md` and (per plan 08) the eventual SUMMARYs. No blockers. One item carried forward: plan 08 must extend `_DEFAULT_TARGETS` to every `149-*-SUMMARY.md` (including this one) and re-run both the gate and the paired suite before the phase closes, per this plan's own explicit non-extension boundary.

## Self-Check: PASSED

- FOUND: `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-check-claims.py`
- FOUND: `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/test_check_claims_v132.py`
- FOUND: `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-CLAIM-GATE-TRANSCRIPTS.md`
- FOUND: `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/` (10 files: clean_control.md, clean_control_second.md, planted_forbidden_claim.md, planted_missing_caveat.md, planted_proven_unqualified.md, planted_page_size_proven.md, planted_graduation.md, planted_support_status_change.md, planted_issue_closed.md, planted_at28c256_fixed.md)
- FOUND commit: `22bd6e9f` (meta, task 1)
- FOUND commit: `8208d9e6` (meta, task 2)
- CONFIRMED: `python3 149-check-claims.py` exits 0 against the real `149-PAGE-SIZE.md`
- CONFIRMED: `python3 -m pytest test_check_claims_v132.py -q -o addopts=""` — 20 passed
- CONFIRMED: `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md` not modified by this plan (`git status --porcelain` empty for that path)
- CONFIRMED: no `PGSZ-0N` checkbox or traceability row touched in `REQUIREMENTS.md` or `ROADMAP.md`
- CONFIRMED: meta `M firestarter` / `M firestarter_app` gitlinks not staged by this plan
