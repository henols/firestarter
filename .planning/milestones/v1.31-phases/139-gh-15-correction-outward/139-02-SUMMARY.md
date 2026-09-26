---
phase: 139-gh-15-correction-outward
plan: 02
subsystem: docs
tags: [claim-gate, honesty-discipline, gh15, forbidden-claim-scanner, python, non-vacuity]

requires:
  - phase: 139-gh-15-correction-outward (plan 01)
    provides: "139-GH15-ORIGINAL-CRITERIA.md and 139-CITATIONS.md (read-only context; neither modified by this plan)"
provides:
  - "139-check-claims.py: the Phase-139-scoped forbidden-claim gate -- argv/env/_HERE-defaults target resolution, a local-defaults self-check, a hoisted never-vacuous guard, a fail-closed missing-target branch, v1.31 forbidden vocabulary, and the ~6.25 V ceiling as the required caveat"
  - "a recorded, four-run non-vacuity transcript proving the gate can fail (Run 1, planted) before any pass (Run 2) is relied on, plus both fail-closed paths (Runs 3-4)"
affects: [139-03, 139-04, 139-05, 146-close]

tech-stack:
  added: []
  patterns:
    - "no proximity/context window on a forbidden-claim scanner -- RESEARCH F-04 proved by five executed probes that a window is exactly what made the v1.30 donor vacuous on this milestone's 0x07/0x08/0x0B vocabulary"
    - "planted-failure-first non-vacuity discipline: RED (Run 1) recorded before GREEN (Run 2) is relied on, never assumed"
    - "the required caveat IS the requirement: ISSUE-02's ~6.25 V program-VCC ceiling is the gate's REQUIRED_CAVEAT_PATTERNS entry, making the mechanical check and the requirement the same check"

key-files:
  created:
    - .planning/phases/139-gh-15-correction-outward/139-check-claims.py
  modified: []

key-decisions:
  - "Mechanics-only reuse of the Phase 137 donor script check_permitted_claims.py (read for reference, never imported/subclassed/env-seamed): the _HERE construction, resolve_targets's argv/env/defaults precedence, the hoisted never-vacuous guard, the fail-closed missing-target branch, _print_bucket, and the PASS line's shape were the only parts carried forward."
  - "No pytest module or committed fixtures. Phase 138's scratchpad-only, never-committed fixture strategy was chosen over Phase 137's committed-fixtures/paired-test-module precedent, per this plan's own explicit instruction -- a committed fixture set plus a paired test module is the shape of Phase 146's CLOSE-01 gate, a Deferred Idea for this phase."
  - "The donor's all-or-nothing early-return branch (the one that reports readiness and exits 0 when every default target is missing) is deleted entirely, not merely renamed or disabled. Phase 139 authors its two named artifacts (139-GH15-COMMENT.md, 139-GH15-BODY-AMENDMENT.md) in a later plan (139-03), not this one, so there is no pre-authored window this gate needs to protect, and Run 4 below proves the deletion at run time rather than by code inspection alone."
  - "scan_text(text, path) accepts `path` per the plan's literal signature even though the returned (label, matched_text, lineno) tuples do not embed it -- main() already threads the same path through its own loop variable when building violation messages, so no functional behavior depends on scan_text's internal use of `path`."

patterns-established:
  - "_assert_default_targets_are_local(): a startup self-check run first in main(), before target resolution or any scanning -- moves the Phase 137 precedent's two mandatory paired-pytest legs (default-targets-resolve-locally, default-targets-carry-this-phase's-prefix) inside the script itself, so a future cross-phase copy fails loudly at run time instead of passing vacuously."

requirements-completed: []

coverage:
  - id: D1
    description: "139-check-claims.py exists, defines all nine required symbols, and carries zero v1.30 domain machinery (the silicon-lock part-family token, the two proximity-window helper identifiers, the relational self-verifying rule, and the arming-branch readiness string are all absent)"
    verification:
      - kind: unit
        ref: "python3 -c \"import ast;ast.parse(open('139-check-claims.py').read())\" plus 9-symbol grep loop -> AST-OK, SYMBOLS-OK; plus a 5-pattern absence grep and 6 presence greps -> VOCAB-OK"
        status: pass
    human_judgment: false
  - id: D2
    description: "The gate was observed RED on a planted four-label violation (Run 1) before any pass (Run 2) was relied on, and RED on both fail-closed paths (Run 3: empty env seam; Run 4: missing default targets) -- all four reproduced verbatim below"
    verification:
      - kind: unit
        ref: "four subprocess invocations of 139-check-claims.py, commands/stdout/exit-codes reproduced verbatim in '## Claim gate -- non-vacuity record' below"
        status: pass
    human_judgment: false

duration: ~14min
completed: 2026-08-09
status: complete
---

# Phase 139 Plan 02: Phase-139 Forbidden-Claim Gate Summary

**Authored `139-check-claims.py` -- a Phase-139-scoped forbidden-claim/required-caveat scanner carrying v1.31 vocabulary and the ~6.25 V program-VCC ceiling as its required caveat, with no proximity window and no arming branch -- and proved it can fail (a planted four-label RED) before its first pass was trusted, then proved both of its fail-closed paths RED as well.**

## Performance

- **Duration:** ~14 min
- **Started:** 2026-08-09T12:10:39Z (immediately after plan 139-01's completion commit `7ea2e35a`)
- **Completed:** 2026-08-09T12:24:39Z
- **Tasks:** 2 of 2
- **Files modified:** 1 (`139-check-claims.py`, created)

## Task 1 -- Author 139-check-claims.py

Wrote `.planning/phases/139-gh-15-correction-outward/139-check-claims.py` (330 lines) from scratch,
reading the Phase 137 donor script (`check_permitted_claims.py`) for MECHANICS reference only -- never
imported, subclassed, or env-seamed. Carried forward verbatim in shape (not in content): the `_HERE`
construction, `resolve_targets`'s argv/env/defaults precedence with its `is not None` subtlety,
`_print_bucket`, the hoisted never-vacuous guard, and the fail-closed missing-target branch.

**Deliberately NOT carried forward:** the donor's proximity/context window (RESEARCH F-04 proved by five
executed probes that this exact window is what makes the donor scan a planted violation clean when the
surrounding text is `0x07`/`0x08`/`0x0B` vocabulary instead of the donor's own AT28C/SDP/`0x0D` tokens);
the donor's required-caveat sentence (a silicon-lock-part caveat has no place in a 27C EPROM comment);
the donor's relational "self-verifying" rule (v1.30-domain-specific, not reused); and the donor's
all-or-nothing early-return branch that reports readiness and exits 0 when every default target is
missing (deleted entirely -- Phase 139 authors its own two named artifacts in plan 139-03, not this one,
so there is no pre-authored window to protect).

**New in this module:** `_assert_default_targets_are_local()`, a startup self-check run first in
`main()` that fails loudly, naming the offending entry and the exact defect, if any `_DEFAULT_TARGETS`
entry is not local to the module's own directory or does not carry the `139-` prefix -- this moves the
Phase 137 precedent's two mandatory paired-pytest legs inside the script itself. Twelve v1.31 forbidden
patterns (`datasheet-conformant`, `datasheet-correct`, `algorithm-accurate`,
`datasheet-compound-unqualified`, `verified-on-silicon`, `silicon-verified`, `confirmed-working`,
`works-on-silicon`, `proven-on-silicon`, `proven-unqualified`, `now-works`, `should-now-work`) and two
required-caveat patterns (`ceiling-voltage` -- `6\.25\s*V`; `ceiling-narrowing` -- `silicon[-\s]margin`).
Env seam is `FIRESTARTER_CLAIMSCAN_TARGETS_V131` (suffixed to avoid colliding with the three prior
checkers' bare or `_V130`-suffixed seams).

**Verify block 1 (AST parse + 9-symbol presence):**
```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && python3 -c "import ast;ast.parse(open('139-check-claims.py').read());print('AST-OK')" && for s in _HERE _DEFAULT_TARGETS FORBIDDEN_PATTERNS REQUIRED_CAVEAT_PATTERNS _assert_default_targets_are_local resolve_targets scan_text _print_bucket "def main"; do grep -qF "$s" 139-check-claims.py || { echo "MISSING $s"; exit 1; }; done && echo SYMBOLS-OK
AST-OK
SYMBOLS-OK
```

**Verify block 2 (v1.30-machinery absence + v1.31 vocabulary presence):**
```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && test "$(grep -c -iE 'at28c|_SDP_CONTEXT_TOKENS|_sdp_context_in_window|SELF_VERIFYING|UNARMED' 139-check-claims.py)" = "0" && grep -qF 'mechanizable half' 139-check-claims.py && grep -qF 'CLOSE-01' 139-check-claims.py && grep -qF '6\.25' 139-check-claims.py && grep -qF 'silicon[-' 139-check-claims.py && grep -qF 'FIRESTARTER_CLAIMSCAN_TARGETS_V131' 139-check-claims.py && echo VOCAB-OK
VOCAB-OK
```

**Supplementary checks (beyond the two mechanical verify blocks, against the plan's fuller
acceptance_criteria list):** `_DEFAULT_TARGETS` has exactly 2 entries, both `os.path.dirname(entry) ==
_HERE`; no `..` path segment or another phase's directory name appears in any string literal (the two
`grep -n '\.\.'` hits are prose ellipses -- `os.environ.get(...)` and `"... and N more"` -- not path
segments); `datasheet[-`, `conformant`, `correct`, and the literal `algorithm[-\s]accurate` regex are
all present; file is 330 lines (>= the 90-line minimum); no file under `firestarter/` or
`firestarter_app/` was touched (the pre-existing ` M firestarter` / ` M firestarter_app` submodule-gitlink
dirt predates this session).

## Task 2 -- Prove the gate can fail

All four runs passed exactly as designed on the first attempt -- no fix to `139-check-claims.py` was
needed, so this task produced no additional commit of its own; the proof lives entirely in the section
below. Every planted/control input lived only in the session scratchpad directory
(`/tmp/claude-1000/-workspaces/15f3308e-b699-443e-a9e5-12d260956ef2/scratchpad`, via `TMPDIR`), was
deleted immediately after its run by the verify command's own `rm -rf "$T"`, and was never committed --
confirmed by `git status --porcelain -- .planning/phases/139-gh-15-correction-outward` returning empty
after all four runs.

## Claim gate -- non-vacuity record

A gate that has only ever passed is untrusted. **Run 1 preceded Run 2**, in that literal order, and no
pass of this gate is relied on anywhere in this plan, this SUMMARY, or any later plan until Run 1 below
was observed RED for the four attributable reasons it names. Runs 3 and 4 additionally prove both
fail-closed paths RED, and Run 4's absence of the string `UNARMED` in its own stdout is the run-time proof
that the donor's early-return branch was actually deleted, not merely renamed.

### Run 1 -- non-vacuity proof (planted violation), MUST FAIL -- observed FAIL

Input file (`planted.md`, written only to the session scratchpad, deleted immediately after this run,
never committed), exact content:

```
Protocol 0x07 and 0x0B notes.
The ~6.25 V program-VCC rail is unreachable on this shield, so this buys timing fidelity and not silicon-margin fidelity.
This firmware is datasheet-conformant and algorithm-accurate.
It was verified on silicon and is confirmed working for 0x08.
```

The required caveats (`6.25 V`, `silicon-margin`) are present by design, so the failure below is
attributable exclusively to the four planted forbidden phrases, not to a missing caveat. Command as run
(scratchpad `mktemp -d` directory created under `$TMPDIR`, populated, scanned, then removed):

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && T=$(mktemp -d) && printf '<the four lines above>' > "$T/planted.md" && out=$(python3 139-check-claims.py "$T/planted.md"); rc=$?; printf '%s\n' "$out"; rm -rf "$T"
```

Literal stdout:

```
FAIL: 4 forbidden phrase match(es):
  /tmp/claude-1000/-workspaces/15f3308e-b699-443e-a9e5-12d260956ef2/scratchpad/tmp.3sLVRK93nC/planted.md:3: forbidden phrase match [datasheet-conformant]: 'datasheet-conformant'
  /tmp/claude-1000/-workspaces/15f3308e-b699-443e-a9e5-12d260956ef2/scratchpad/tmp.3sLVRK93nC/planted.md:3: forbidden phrase match [algorithm-accurate]: 'algorithm-accurate'
  /tmp/claude-1000/-workspaces/15f3308e-b699-443e-a9e5-12d260956ef2/scratchpad/tmp.3sLVRK93nC/planted.md:4: forbidden phrase match [verified-on-silicon]: 'verified on silicon'
  /tmp/claude-1000/-workspaces/15f3308e-b699-443e-a9e5-12d260956ef2/scratchpad/tmp.3sLVRK93nC/planted.md:4: forbidden phrase match [confirmed-working]: 'confirmed working'
```

**Exit code: 1.** All four required labels present verbatim: `datasheet-conformant`, `algorithm-accurate`,
`verified-on-silicon`, `confirmed-working`. This is an exit 1 attributable to the correct, named reasons
-- not merely a non-zero exit -- which is what distinguishes this from Run 1's donor-checker analogue
(RESEARCH probe B), which failed on an irrelevant caveat with zero forbidden hits reported.

### Run 2 -- clean control, MUST PASS -- observed PASS (only meaningful because Run 1 was already RED)

Input file (`clean.md`, scratchpad-only, deleted immediately after, never committed), exact content:

```
Protocol 0x0B programs each byte with a pulse width taken from the database.
The ~6.25 V program-VCC these algorithms assume is unreachable on this shield, so this buys timing, pulse-count and verify fidelity and not silicon-margin fidelity.
```

Command as run:

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && T=$(mktemp -d) && printf '<the two lines above>' > "$T/clean.md" && out=$(python3 139-check-claims.py "$T/clean.md"); rc=$?; printf '%s\n' "$out"; rm -rf "$T"
```

Literal stdout:

```
PASS: scanned ../../../../tmp/claude-1000/-workspaces/15f3308e-b699-443e-a9e5-12d260956ef2/scratchpad/tmp.h5ENQX2Lgs/clean.md; 1 file(s) carry both required caveats (this PASS is the mechanizable half of the ISSUE-02 / D-05 discipline only -- see the module docstring's explicit non-claim)
```

**Exit code: 0.** The `PASS:` line names `clean.md` by path relative to `_HERE`, real `0x0B` prose, zero
forbidden phrases, both caveats present.

### Run 3 -- never-vacuous guard on an explicitly empty env seam, MUST FAIL -- observed FAIL

Command as run (no scratchpad file needed -- this run exercises target resolution, not scanning):

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && out=$(FIRESTARTER_CLAIMSCAN_TARGETS_V131= python3 139-check-claims.py); rc=$?; printf '%s\n' "$out"
```

Literal stdout:

```
FAIL: no scan targets resolved -- the gate cannot vacuously pass with nothing scanned
```

**Exit code: 1.** `PASS:` absent from stdout, confirmed by grep. The explicitly-empty env value resolved
to zero targets (via the `is not None` check, not truthiness) rather than silently falling back to
`_DEFAULT_TARGETS` -- proving `resolve_targets`'s precedence subtlety at run time, not just by code
inspection.

### Run 4 -- fail-closed on missing default targets, MUST FAIL -- observed FAIL

Command as run (no arguments, no env override -- `_DEFAULT_TARGETS` resolves to the two artifacts
plan 139-03 has not authored yet):

```
$ cd /workspaces/.planning/phases/139-gh-15-correction-outward && out=$(python3 139-check-claims.py); rc=$?; printf '%s\n' "$out"
```

Literal stdout:

```
FAIL: scan target(s) not found on disk -- the gate cannot vacuously pass with a target silently skipped: ['/workspaces/.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md', '/workspaces/.planning/phases/139-gh-15-correction-outward/139-GH15-BODY-AMENDMENT.md']
```

**Exit code: 1.** Both missing basenames (`139-GH15-COMMENT.md`, `139-GH15-BODY-AMENDMENT.md`) named
verbatim. Both `PASS:` and `UNARMED` are absent from stdout, confirmed by grep -- the absence of
`UNARMED` specifically is the run-time proof that the donor's early-return-and-exit-0 branch was
actually deleted from this module, not merely disabled or renamed.

### Post-run cleanup verification

```
$ git status --porcelain -- .planning/phases/139-gh-15-correction-outward
(empty)
```

No planted or control fixture survives anywhere under `.planning/`, `firestarter/`, or
`firestarter_app/`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author 139-check-claims.py** -- `49881518` (feat) -- adds the 330-line gate script, staged
   individually (`git add .planning/phases/139-gh-15-correction-outward/139-check-claims.py`), no other
   file touched.
2. **Task 2: Prove the gate can fail** -- no additional commit. All four runs passed on the first
   attempt; nothing about `139-check-claims.py` changed, so there was nothing to commit beyond this
   SUMMARY (which itself is committed separately, per the plan's own output instruction).

## Files Created/Modified

- `.planning/phases/139-gh-15-correction-outward/139-check-claims.py` -- the Phase-139 forbidden-claim
  gate: 330 lines, 9 required symbols, v1.31 vocabulary, the 6.25 V ceiling as its required caveat, no
  proximity window, no arming branch.

## Decisions Made

See `key-decisions` in the frontmatter above. In summary: mechanics-only reuse of the Phase 137 donor
(never imported/subclassed/env-seamed); Phase 138's scratchpad-only fixture strategy chosen over Phase
137's committed-fixtures/pytest-module strategy (a committed fixture set is Phase 146 CLOSE-01's shape,
a Deferred Idea here); the donor's early-return branch deleted entirely rather than renamed; and
`scan_text`'s `path` parameter accepted per the plan's literal signature without being required by the
return shape (no behavior depends on it).

## Deviations from Plan

None -- plan executed exactly as written. Both tasks completed on the first attempt with no auto-fixes,
no blocking issues, and no architectural questions. All four Task 2 runs produced exactly the outcomes
the plan's acceptance criteria specified, so no "fix and re-run all four from the top" cycle was
triggered.

## Issues Encountered

None. One minor operational note, not a deviation: the plan's own `<verify>` blocks use bare `mktemp -d`
(which defaults to system `/tmp`); this session pointed `TMPDIR` at the session scratchpad directory
before running each block so the resulting temp directories landed under the scratchpad rather than
generic `/tmp`, honoring both the plan's `<action>` instruction ("use the session scratchpad directory
for every planted or synthetic input") and the literal, unmodified verify commands (`TMPDIR` is an
ambient environment setting, not a change to the command text itself).

## User Setup Required

None -- no external service configuration required. This plan makes no network call and no `gh` call
of any kind.

## Next Phase Readiness

- `139-check-claims.py` is committed, proven non-vacuous, and ready for plan 139-04 to run against the
  frozen `139-GH15-COMMENT.md` and `139-GH15-BODY-AMENDMENT.md` once plan 139-03 authors them.
- **No requirement ticked by this plan.** `requirements-completed: []` per the plan's own scope guard --
  ISSUE-02 is a multi-plan requirement; it ticks only when plan 139-05 completes the operator's wording
  approval, which is the other (non-mechanizable) half of the ISSUE-02 / D-05 discipline this gate's own
  docstring explicitly disclaims satisfying alone.
- No sub-repo commit was made by this plan (meta-repo documentation and tooling only; `firestarter/` and
  `firestarter_app/` were read-only inspected, never modified, and their pre-existing dirty
  submodule-gitlink status predates this session).

---
*Phase: 139-gh-15-correction-outward*
*Completed: 2026-08-09*

## Self-Check: PASSED

- FOUND: `139-check-claims.py`
- FOUND: `139-02-SUMMARY.md`
- FOUND commit: `49881518` (Task 1: author 139-check-claims.py)
- FOUND commit: `07906161` (this SUMMARY)
