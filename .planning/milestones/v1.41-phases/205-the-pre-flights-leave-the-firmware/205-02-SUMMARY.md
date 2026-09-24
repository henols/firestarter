---
phase: 205-the-pre-flights-leave-the-firmware
plan: "02"
subsystem: testing, firmware-build
tags: [pytest, platformio, avr, meta-repo-path-citation, flash-ram-measurement]

requires:
  - phase: n/a
    provides: n/a
provides:
  - "A green firestarter_fw pytest tree (320/320, no ignore, no wholesale skip) so every
    later firmware plan in this phase can honestly claim the tree was green at the start."
  - "205-FLASH-RAM.md: FWBLANK-05's phase-entry baseline (flash + RAM + both artifact
    digests for uno, uno328pb, leonardo), the stated build configuration, and empty
    phase-exit/delta sections for plan 06."
affects: [205-03, 205-04, 205-05, 205-06, 205-07]

actuals:
  tokens: 9500
  tasks: 2
  commits: 3
  commits_by_repo:
    firestarter_fw: 1
    meta: 2

tech-stack:
  added: []
  patterns:
    - "Stale .planning/ citation repair: confirm each cited document's live location
      individually before rewriting a resolver literal — never batch-substitute a prefix
      across a file, because not every citation in the file necessarily moved."

key-files:
  created:
    - .planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md
  modified:
    - firestarter_fw/tests/test_flash_path_record_sync.py
    - firestarter_fw/CLAUDE.md

key-decisions:
  - "Only one of the four cited literals actually needed a path change (_META_DOC_REL at
    test_flash_path_record_sync.py:77, resolved via meta_path() at :377) — the other three
    were confirmed correct or corrected to match an already-correct target, not blindly
    rewritten. Recorded as findings rather than assumed."
  - "The two seed-link assertions (originally :1092/:1094, now shifted by the one-line
    docstring edit) were tightened from the seed's stale link LABEL
    ('../v1.23-FLASH-PATH-DECISION.md') to its already-correct link TARGET/href
    ('../milestones/v1.23-FLASH-PATH-DECISION.md') — both substrings are present in the
    seed today, so this is a correction to what the citation checks, not a behavior change
    in whether the test passes."
  - "The linker-script needle (test_flash_path_record_sync.py:363, inside _LINKER_NEEDLES)
    is a bare-filename substring check against platform/py32f071/linker/PY32F071xB_FLASH.ld's
    comment text, not a path resolution — confirmed it needs no change. The linker
    script's own comment still carries the stale full path
    '.planning/v1.23-FLASH-PATH-DECISION.md', but that is a firmware SOURCE file this plan
    is scoped not to touch (acceptance criteria pin the commit's file list to exactly the
    test module and CLAUDE.md), so it is recorded here as an out-of-scope finding, not
    fixed."

requirements-completed: []

coverage:
  - id: D1
    description: "firestarter_fw's pytest tree is honestly green (320/320, no ignore, no
      wholesale skip) after repairing the four stale .planning/ path citations in
      test_flash_path_record_sync.py, isolated in its own commit before any sweep work."
    requirement: FWBLANK-05
    verification:
      - kind: integration
        ref: "pytest tests/test_flash_path_record_sync.py -o addopts=\"\" -p no:cacheprovider -v (41 passed, 0 skipped, 0 MissingScanTargetError)"
        status: pass
      - kind: integration
        ref: "pytest tests/ -o addopts=\"\" -p no:cacheprovider -q (320 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "205-FLASH-RAM.md carries FWBLANK-05's phase-entry baseline: measured flash
      and RAM for uno, uno328pb and leonardo from a clean pio run (reproduced twice,
      byte-identical), six artifact digests, the stated build configuration correcting
      CONTEXT D-10's three premises, and both leonardo denominators (32768 and 28672)."
    requirement: FWBLANK-05
    verification:
      - kind: other
        ref: "python3 -c check for headings/tokens in 205-FLASH-RAM.md (see task 2 <verify>)"
        status: pass
      - kind: other
        ref: "pio run -t clean -e uno -e uno328pb -e leonardo, run twice, identical Flash:/RAM: lines and sha256 digests both times"
        status: pass
    human_judgment: false
---

# Phase 205 Plan 02: The firmware tree goes honestly green, and FWBLANK-05's before-figure lands Summary

**Repaired the one broken `.planning/` path resolution behind 17 red pytest legs in
`test_flash_path_record_sync.py`, then measured FWBLANK-05's phase-entry flash/RAM baseline
(21452/1398 uno, 21496/1404 uno328pb, 23810/1839 leonardo) with both Leonardo denominators
and six artifact digests, all before any blank-check code is touched.**

## Performance

- **Duration:** ~16 min
- **Started:** 2026-09-22T15:15:00Z (approximate — no start-time sentinel was captured at
  kickoff; bounded by the git commit timestamps below)
- **Completed:** 2026-09-22T15:30:36Z
- **Tasks:** 2
- **Files modified:** 3 (2 firmware, 1 new meta-repo document) + 1 gitlink advance

## Accomplishments
- `firestarter_fw`'s pytest tree (`tests/`) is honestly green: 320/320 collected and passing,
  no `--ignore`, no wholesale-skipped module, no `MissingScanTargetError`.
- `.planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md` opened with the
  FWBLANK-05 phase-entry baseline, the measured build configuration (correcting three
  CONTEXT D-10 premises), and empty phase-exit/delta sections for plan 06 to fill.
- The `firestarter_fw` gitlink in the meta repo is advanced to carry this plan's commit.

## Task Commits

Each task was committed atomically:

1. **Task 1: repair the four stale path citations so the firmware tree is green** —
   `a4e002f2` (fix, in `firestarter_fw`) — repaired `_META_DOC_REL`'s `meta_path()`
   resolution and the two seed-link assertion literals in
   `tests/test_flash_path_record_sync.py`, plus the stale "about 286 tests" sentence in
   `CLAUDE.md`.
2. **Task 2: take the FWBLANK-05 phase-entry baseline and open the measurement record** —
   `e28cf766` (docs, in the meta repo) — `205-FLASH-RAM.md` created with the phase-entry
   table, digests and build-configuration statement.

**Plan metadata / gitlink:** `cdb4b96e` (chore, in the meta repo) — advances the
`firestarter_fw` gitlink to `a4e002f2`, per this project's per-phase (not milestone-close-only)
gitlink-advance convention.

_Note: no TDD tasks in this plan._

## Files Created/Modified
- `firestarter_fw/tests/test_flash_path_record_sync.py` — `_META_DOC_REL` now resolves under
  `milestones/`; the seed-link assertions check the seed's actual (already-correct) href
  target instead of its stale link label.
- `firestarter_fw/CLAUDE.md` — "about 286 tests" corrected to the measured 320 collected.
- `.planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md` — new. The
  FWBLANK-05 measurement record.

## Decisions Made

- **Only one of the four cited literals was actually broken.** Verification against the
  live `.planning` tree found:
  - `_META_DOC_REL` (test file `:77`, resolved via `meta_path(".planning", _META_DOC_REL)`
    at `:377`) — **broken.** Resolved to `.planning/v1.23-FLASH-PATH-DECISION.md`, which
    does not exist; the document lives at
    `.planning/milestones/v1.23-FLASH-PATH-DECISION.md`. This single resolution failure was
    the direct cause of all 17 pre-existing red legs (every one raised
    `MissingScanTargetError` from `_meta_doc()`, or depended on a fixture that did). Fixed
    by changing the constant to `"milestones/v1.23-FLASH-PATH-DECISION.md"`.
  - `_LINKER_NEEDLES`'s `"v1.23-FLASH-PATH-DECISION.md"` entry (test file `:363`) — **not a
    path, no fix needed.** It is a bare-filename substring check against the linker script's
    comment text (`platform/py32f071/linker/PY32F071xB_FLASH.ld:12`), which still literally
    contains the filename regardless of the document's directory. Confirmed as a finding,
    left unchanged.
  - The seed-link assertions (test file, originally cited around `:1092`/`:1094`) — **stale
    in what they checked, not in whether they passed.** `.planning/seeds/py32f071-no-
    external-tool-fw-install.md` already carries the *correct* markdown href
    `../milestones/v1.23-FLASH-PATH-DECISION.md`, but its *link label* is the stale
    `../v1.23-FLASH-PATH-DECISION.md`. The old assertion matched the stale label (a
    substring match, not markdown-aware), so it passed for the wrong reason. Corrected to
    check the actual href target, which the seed file already carries — the assertion
    still passes, but now for the right reason.
  - The seed's own citation to the flash-path record (`.planning/seeds/py32f071-...md`
    itself) — confirmed it did **not** move; it remains under `.planning/seeds/`, so
    `_SEED_REL` needed no change.
- **The linker script's own stale comment** (`.planning/v1.23-FLASH-PATH-DECISION.md`,
  missing the `milestones/` segment, at `PY32F071xB_FLASH.ld:12`) is a real finding but is
  **out of scope for this plan** — it is firmware source, and this plan's acceptance
  criteria pin the commit's file list to exactly `tests/test_flash_path_record_sync.py` and
  `CLAUDE.md`. Recorded here rather than fixed; a future firmware-source-touching plan
  should repair it.
- **FWBLANK-05's phase-entry figures matched `205-RESEARCH.md`'s simulated-sweep control
  build exactly** (same commit-state minus this plan's test/doc-only changes, same
  toolchain). This is treated as corroborating evidence that both runs measured the same
  tree correctly, not as license to skip the re-measurement this plan required — the
  numbers in `205-FLASH-RAM.md` are freshly taken here, with their own two-pio-run
  reproduction and their own six digests, not copied.

## Deviations from Plan

None — plan executed exactly as written. The investigation into which of the "four
literals" actually needed changing (documented above under Decisions Made) is exactly what
the plan's own task text asked for ("confirm each of the four individually... If any one of
them is not under `.planning/milestones/`, that is a finding").

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The firmware pytest tree is green and stays green as later plans in this phase run their
  own `fails_when` legs — no ambiguity between a real regression and a pre-existing failure.
- `205-FLASH-RAM.md`'s phase-entry baseline and build-configuration statement are ready for
  plan 06 to extend with the phase-exit figures and delta.
- No blocker for plan 03 (this plan touched no shared file and no shared gate with the
  removal plans; it ran in parallel with plan 01 per the plan's own objective statement).

---
*Phase: 205-the-pre-flights-leave-the-firmware*
*Completed: 2026-09-22*
