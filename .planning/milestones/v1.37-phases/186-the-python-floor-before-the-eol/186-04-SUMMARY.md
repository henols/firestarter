---
phase: 186-the-python-floor-before-the-eol
plan: 04
subsystem: documentation
tags: [python, floor, rationale-note, backlog, gitlink, claim-hygiene]

requires:
  - phase: 186-03
    provides: "All four floor statements at 3.11, the four-way agreement gate green, FLOOR-01/02 Complete, and app-repo firestarter_app HEAD at 612aa69 with its own STACK.md pointing at this plan's note"
provides:
  - ".planning/notes/python-floor-decision.md: the FLOOR-03 record -- decision, three rejected alternatives with measured grounds, transcribed evidence, standing rule, enforcing gate, successor backlog item, and the named residual gap"
  - "Three meta-repo records (STACK.md, STRUCTURE.md, CONVENTIONS.md) corrected to state the 3.11 floor, closing the two surfaces (STRUCTURE.md, CONVENTIONS.md) the original discussion missed"
  - "Backlog 999.67, carrying 2027-10-31, filed as the successor to 999.26/999.27"
  - "The meta repo's firestarter_app gitlink advanced to 612aa69"
  - "FLOOR-03 marked Complete in .planning/REQUIREMENTS.md -- the phase's last requirement"
affects: []

actuals:
  tokens: 5624
  raw_tokens: 5624
  tasks: 3
  commits: 6
  plan_head_before: "e67ab115a75b8081ceaab307b214ad80b6d0b842"

tech-stack:
  added: []
  patterns:
    - "A rationale note's frontmatter (title/date/context) plus a VERDICT-first, numbered-section shape, matching the 27-note precedent and the freshest instance (notes/catalog-sync-check-retirement.md, Phase 185) -- figures transcribed verbatim from RESEARCH.md, never re-measured"
    - "A meta-repo codebase/*.md correction takes its replacement examples from real, currently-committed post-sweep source (address_parser.py), never composed prose, so the document describes a tree that actually exists"
    - "A successor backlog item's title carries the next hard deadline explicitly (2027-10-31), repeating the mechanism (Phase 131 D-13 -> 999.26/999.27) that made this phase land ahead of schedule rather than as a surprise"

key-files:
  created:
    - .planning/notes/python-floor-decision.md
  modified:
    - .planning/codebase/STACK.md
    - .planning/codebase/STRUCTURE.md
    - .planning/codebase/CONVENTIONS.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md
    - firestarter_app (gitlink, advanced to 612aa69)

key-decisions:
  - "Stated the 3.9/3.10 consumer impact as measured, not assumed: an unpinned `pip install firestarter` on those interpreters emits no error and exits 0 -- pip silently pins to the last release advertising the old floor. The quoted refusal wording fires only on a pinned/exact request. Both the note (§2) and this SUMMARY's release fragment (below) use the corrected wording per D-12/C-5, never 'pip refuses'."
  - "CONVENTIONS.md's replacement examples (`parse_address`, `parse_size`) are taken verbatim from `firestarter_app/firestarter/address_parser.py`'s real, currently-committed post-sweep signatures, not composed -- the plan's own instruction was explicit that composed text would repeat the exact defect class (a document describing a tree that does not exist) the correction was meant to fix."
  - "CONVENTIONS.md's corrected sentence names `py32_dfu.py` as 'one deliberately preserved exception' rather than 'the only Optional[...] left in the tree' -- a scan found one further site (`serial_comm.py:816`, a quoted forward-reference `Optional[\"SerialCommunicator\"]` that ruff's own UP045 does not flag, confirmed live with `ruff check --select UP045`) that is a different, narrower technical shape (an autofix-rule boundary case, not a suppressed/preserved exception) and was not named by D-09/D-11/D-01's research pass. Naming it as a second 'exception' in the same sentence would conflate two different things; the phrasing chosen is accurate without requiring an exhaustive tree-wide inventory this plan was not chartered to produce."
  - "Task 2's acceptance criterion asserting the STRUCTURE.md provenance-caveat phrase prints exactly `1` does not hold: the phrase `[unverified in 2026-08-26 scoped remap ...]` is a document-wide marker appearing 5 times across STRUCTURE.md, not once, and this pre-dates this plan entirely (confirmed: `git diff` for this plan touches only line 363, the Python version). The underlying intent -- the caveat heading the Build Environments section is not deleted alongside the floor claim inside it -- is satisfied; the criterion's arithmetic assumption about the whole file was simply wrong. Recorded as a disposition, not silently waved past."
  - "999.67's title pattern departs slightly from 999.63-999.66's 'BACKLOG -- filed <date> during v1.37 Phase <N>' shape by also naming the deadline in the title itself, matching 999.27's own shape ('mypy minimum-target treadmill -- Python 3.10 EOLs 2026-10-31') more closely than the four freshest stubs -- because D-08 explicitly requires the deadline in the title, and 999.27 is 999.67's own direct ancestor, not 999.63-66."
  - "FLOOR-03 marked Complete in REQUIREMENTS.md by hand-edit (not the requirements.mark-complete verb) -- this is FLOOR-03's only contributing plan and it is genuinely satisfied: the note exists, carries all four of D-08's required contents, and the app-repo pointer (186-03) now resolves to a real file."
  - "STATE.md hand-repaired after every `state.*` verb call, per the known frontmatter-zeroing bug: `state.advance-plan` zeroed both `progress.completed_phases` (4 -> 0) and `progress.percent` (67 -> 0) in the same call that correctly advanced `Current Position` -- restored both to 4/67 (the orchestrator, not this commit, bumps `completed_phases` to 5 once the phase is verified closed) and set `completed_plans` to 28."
  - ".planning/config.json was found dirty after the state.* verb calls (`sub_repos` pruned from four entries to two -- the known GSD-verb bug) and deliberately left untouched, per this plan's hard rule 4; the orchestrator handles it."

requirements-completed: [FLOOR-03]

coverage:
  - id: D1
    description: "The rationale note exists in the established .planning/notes/ location and shape, carries all four of D-08's required contents (decision+alternatives, evidence, standing rule, successor) plus the named residual gap, states the consumer impact as measured rather than assumed, and pins its figures to mypy 2.3.1/ruff 0.16.4"
    requirement: "FLOOR-03"
    verification:
      - kind: unit
        ref: "grep -c '^## ' python-floor-decision.md -- 6; grep -n '^## VERDICT' -- line 9, first heading; grep -c '2027-10-31|999.67|PYTHON3_VERSION_MIN|py32_dfu|test_python_floor_agreement' each >=1; grep -c 'pip refuses' -- 0; head -1 -- '---' -- Task 1 <verify>"
        status: pass
    human_judgment: true
    rationale: "Whether the note's prose is genuinely non-vacuous -- whether it actually helps a future reader avoid re-deriving the decision, versus merely containing the required grep-able tokens -- is a judgment call a grep count cannot fully settle. The reviewer should read the note itself (155 lines) alongside this coverage entry."
  - id: D2
    description: "All five enumerated old-floor claims across STACK.md, STRUCTURE.md and CONVENTIONS.md are corrected, no sixth survives anywhere under .planning/codebase/, the STRUCTURE.md provenance caveat is preserved, and CONVENTIONS.md's replacement examples are real post-sweep source"
    requirement: "FLOOR-03"
    verification:
      - kind: unit
        ref: "grep -rnIE '3\\.9|py39' .planning/codebase/ -- no output, exit 1; grep -c '3\\.11' STACK.md -- 5; grep -c '3\\.11' STRUCTURE.md -- 1; grep -c 'py32_dfu' CONVENTIONS.md -- 1; git diff --numstat -- exactly 3 files -- Task 2 <verify>"
        status: pass
    human_judgment: true
    rationale: "The STRUCTURE.md provenance-caveat acceptance criterion (expected count 1) does not hold against the actual file (count 5, pre-existing, unrelated to this plan's edit) -- see key-decisions disposition. A human should confirm the disposition is correct (that the caveat heading THIS section, not the file-wide count, is what matters) rather than trust the raw grep count."
  - id: D3
    description: "Backlog 999.67 is filed immediately after 999.66, carries 2027-10-31 in its title, cites both the note and the enforcing gate, and the ROADMAP diff contains only the inserted block"
    requirement: "FLOOR-03"
    verification:
      - kind: unit
        ref: "grep -c '^### Phase 999.67:' -- 1, heading contains 2027-10-31; grep -c '^### Phase 999.68:' -- 0; grep -c 'python-floor-decision.md|test_python_floor_agreement' ROADMAP.md -- 3; diff <snapshot> ROADMAP.md -- only added, contiguous lines -- Task 3 <verify>"
        status: pass
    human_judgment: false
  - id: D4
    description: "The app repo's STACK.md pointer to python-floor-decision.md resolves from the meta repo root, and the meta repo's firestarter_app gitlink is advanced to 612aa69 (the app repo's HEAD after 186-01/02/03), once, last, with nothing pushed in either repository"
    requirement: "FLOOR-03"
    verification:
      - kind: unit
        ref: "test -f .planning/notes/python-floor-decision.md -- POINTER_RESOLVES; git log -1 --stat -- firestarter_app -- names the gitlink commit; git log origin/beta..HEAD -- 161 lines ahead, unpushed; firestarter_app git status --porcelain -- clean of tracked-file changes -- Task 3 <verify>"
        status: pass
    human_judgment: false
  - id: D5
    description: "FLOOR-03 marked Complete in REQUIREMENTS.md (checkbox + traceability row), the phase's full record (two D-10 deviations, three hand-fixed ruff findings, residual py32_dfu.py gap, release-note fragment) is assembled in this SUMMARY, and STATE.md's position/decisions are updated without corrupting the frontmatter progress block"
    requirement: "FLOOR-03"
    verification:
      - kind: unit
        ref: "grep -n 'FLOOR-03' REQUIREMENTS.md -- checkbox [x], traceability row Complete; diff STATE-before/after -- frontmatter progress.completed_phases/percent hand-repaired to 4/67 after state.advance-plan's known zeroing bug -- this SUMMARY, Deviations and STATE.md sections"
        status: pass
    human_judgment: false

duration: 24min
completed: 2026-09-12
status: complete
---

# Phase 186 Plan 04: The Python Floor Decision Record, Corrected Meta-Repo Docs, and the Successor Backlog Item Summary

**Recorded why the Python floor is 3.11 in `.planning/notes/python-floor-decision.md` (decision, evidence, standing rule, successor, residual gap), corrected the three meta-repo records that still stated the old floor (including two the discussion missed), filed backlog 999.67 carrying 2027-10-31, and advanced the meta repo's `firestarter_app` gitlink to `612aa69` — closing FLOOR-03 and the phase.**

## Performance

- **Duration:** 24 min
- **Completed:** 2026-09-12
- **Tasks:** 3
- **Files modified:** 7 (1 created, 6 modified, 1 gitlink advanced)

## Accomplishments

- **Task 1 (the rationale note):** Created `.planning/notes/python-floor-decision.md` (155 lines) following the analog (`notes/catalog-sync-check-retirement.md`) and the 27-note precedent's measured shape: three-key frontmatter, an `# H1` naming FLOOR-01, `## VERDICT` first (line 9, before any of the five numbered sections), then `## 1.` the decision and its three rejected alternatives (3.10 — end-of-life on landing; hold 3.9 — unreachable under `mypy.defaults.PYTHON3_VERSION_MIN == (3, 10)` in mypy 2.3.1; 3.12 — forces an unneeded CI change), `## 2.` the evidence transcribed from `186-RESEARCH.md` (mypy 35/35 byte-identical at 3.10 and 3.11; the 182-finding/190-fixed/3-hand-fixed ruff sweep; the ordering constraint; the measured 3.9/3.10 consumer behavior stated as a silent pin, never "pip refuses"), `## 3.` the standing rule and its enforcing gate (`test_python_floor_agreement.py`), `## 4.` the successor (999.67, 2027-10-31, flagged as an inherited rather than re-verified date), and `## 5.` the residual gap (`py32_dfu.py`'s 14 pre-suppressed `Optional[...]` sites). All nine acceptance-criteria greps passed on first write.
- **Task 2 (the three meta-repo records):** Corrected all five enumerated old-floor claims — `STACK.md:193,203,256` (three "Python 3.9+" claims; the tested-through claim at `:203` now says "classifiers: 3.11-3.12; CI tests 3.11" rather than a broader unproven range), `STRUCTURE.md:363` ("Python: 3.9+" → "3.11+", its unrelated 2026-08-26 provenance caveat at `:360` left untouched), and `CONVENTIONS.md:162-177` (the doubly-falsified union-spelling sentence rewritten to describe the tree the 186-02 sweep actually produced, with real post-sweep examples taken verbatim from `address_parser.py` and one named, deliberately preserved exception, `py32_dfu.py`). `/usr/bin/grep -rnIE '3\.9|py39' .planning/codebase/` returns no output (exit 1) — confirmed clean after one self-caught fix (see Deviations). `git diff --numstat` confirms exactly the three intended files touched, nothing else in `.planning/codebase/`.
- **Task 3 (the successor, the pointer, the gitlink):** Filed `### Phase 999.67` immediately after `999.66` and before the `v1.20` archive separator, carrying **2027-10-31** in its own title and citing both `python-floor-decision.md` and `test_python_floor_agreement.py`; a before/after snapshot diff confirms the ROADMAP edit is nothing but the inserted, contiguous block. Confirmed the app repo's `STACK.md` pointer (written in 186-03) resolves: `test -f .planning/notes/python-floor-decision.md` → `POINTER_RESOLVES`. Advanced the meta repo's `firestarter_app` gitlink to `612aa69` (the app repo's HEAD after 186-01/02/03 and plan 186-03's `CI-REPLICA: PASS`), in its own commit, last. Marked FLOOR-03 Complete in `.planning/REQUIREMENTS.md` (checkbox + traceability row, hand-edited). Nothing was pushed in either repository; `git log origin/beta..HEAD` shows 161 commits ahead, unpushed.

## Task Commits

Each task was committed atomically, in the meta repo at `/workspaces` on branch `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`:

1. **Task 1: The rationale note** — `d8759a53` (docs)
2. **Task 2: Correct the three meta-repo documents** — `face9459` (docs)
3. **Task 3a: File backlog 999.67** — `d8109932` (docs)
3. **Task 3b: Advance the firestarter_app gitlink** — `caff4d4e` (chore)
3. **Task 3c: Mark FLOOR-03 Complete** — `37a0a39f` (docs)

**Plan metadata:** `.planning/STATE.md` — `6596b2eb` (docs); this SUMMARY.md — see final commit below.

## Files Created/Modified

- `.planning/notes/python-floor-decision.md` — the FLOOR-03 rationale record (new, 155 lines)
- `.planning/codebase/STACK.md` — three floor claims corrected to 3.11
- `.planning/codebase/STRUCTURE.md` — one floor claim corrected; provenance caveat intact
- `.planning/codebase/CONVENTIONS.md` — the union-spelling convention rewritten to match the post-sweep tree, with one named exception
- `.planning/ROADMAP.md` — backlog 999.67 inserted (the only change; snapshot-diffed)
- `.planning/REQUIREMENTS.md` — FLOOR-03 marked Complete (checkbox + traceability row)
- `.planning/STATE.md` — plan position, decisions, metrics, session (hand-repaired after known verb bugs)
- `firestarter_app` (gitlink) — advanced to `612aa69`

## Decisions Made

See `key-decisions` in the frontmatter for full detail. In brief: stated the 3.9/3.10 consumer impact as measured (silent pin, not "pip refuses"); took CONVENTIONS.md's replacement examples verbatim from real post-sweep source; phrased `py32_dfu.py` as "one deliberately preserved exception" rather than an absolute "the only" claim, after a live `ruff check --select UP045` scan surfaced one further, narrower-shaped site (`serial_comm.py:816`, a quoted forward reference ruff's own rule does not flag) that is not the same kind of thing and was not part of this phase's named scope; dispositioned the STRUCTURE.md provenance-caveat acceptance criterion's wrong count assumption; matched 999.67's title shape to 999.27 (its direct ancestor) rather than 999.63-66; marked FLOOR-03 Complete by hand; and hand-repaired STATE.md's frontmatter after `state.advance-plan` zeroed `progress.completed_phases`/`percent`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] CONVENTIONS.md's first-draft replacement sentence still contained the literal substring `3.9`**
- **Found during:** Task 2, acceptance-criteria pass
- **Issue:** The rewritten union-spelling paragraph's phrase "an `>=3.9`-era ... norm" left a literal `3.9` in the file, which the plan's own acceptance criterion (`grep -rnIE '3\.9|py39' .planning/codebase/` must produce no output) flagged.
- **Fix:** Reworded to "the pre-raise `Optional[X]`/`Tuple[...]` norm" — same meaning, no version-number literal.
- **Files modified:** `.planning/codebase/CONVENTIONS.md`
- **Verification:** `/usr/bin/grep -rnIE '3\.9|py39' .planning/codebase/` → no output, exit 1.
- **Committed in:** `face9459` (fixed before commit, not a follow-up)

### Dispositioned, not fixed (the underlying file, not this plan's edit, is the source)

**2. [Disposition] STRUCTURE.md's provenance-caveat acceptance criterion assumed a count of 1; the actual file carries 5**
- **Found during:** Task 2, acceptance-criteria pass
- **Issue:** `grep -c 'unverified in 2026-08-26 scoped remap' .planning/codebase/STRUCTURE.md` prints `5`, not the `1` the plan's acceptance criteria predicted — the phrase is a document-wide provenance marker used to head four sections, not one.
- **Resolution:** Confirmed via `git diff -- .planning/codebase/STRUCTURE.md` that this plan's edit touches only line 363 (the Python version); the caveat at line 360, immediately above it, is untouched and intact — the property the criterion exists to protect (the caveat is not deleted alongside the floor claim) holds. Not a defect to fix; the criterion's arithmetic assumption about the whole file was simply wrong.
- **Files modified:** none (disposition only)
- **Verification:** `git diff -- .planning/codebase/STRUCTURE.md` shows exactly one changed line.

**Total deviations:** 1 auto-fixed (Rule 1, caught by this plan's own acceptance criteria before commit); 1 dispositioned (a pre-existing, unrelated fact about the file, not introduced by this plan).
**Impact on plan:** Both were caught and resolved within Task 2's own verification loop, before any commit was trusted. No scope creep.

## The Phase's Full Record (assembled here, per Task 3's own acceptance criteria)

**The two deliberate D-10 deviations, from `186-01-SUMMARY.md`:** (1) Site 2 (the `# UP: pyupgrade` legend line) was narrowed to deleting only the parenthetical, not the whole line, so the legend still lists four entries matching `select`'s four rule families. (2) Site 4 (the "Why a regex scan, not a TOML parse" docstring paragraph in `tests/test_py32_packaging.py`) was widened to delete the whole paragraph, not just the two lines D-10 named, since its argument no longer follows once `tomllib` is stdlib at the new floor. Both committed in `bd25270`.

**The three hand-fixed ruff findings, from `186-02-SUMMARY.md`:** `firestarter/eprom_info.py`'s `prepare_detailed_eprom_data` signature — `:97:24` (`eprom_details`), `:100:36` (`eprom_data_for_programmer`), `:103:26` (`raw_config_data`) — each an `Optional[...]` subscript ruff classifies unsafe to autofix because it spans lines and encloses a comment. Collapsed by hand to `dict | None`, orphaned inner comments dropped (not replaced), with a second `--fix` pass catching the resulting second-order `F401`. Committed in `1ebc548`.

**The residual `py32_dfu.py` gap:** 14 `Optional[...]` annotations, each individually `# noqa: UP045`-suppressed, pre-dating this phase and left untouched by the sweep — recorded in `python-floor-decision.md` § 5 and named as the one exception in `CONVENTIONS.md`'s corrected convention statement. Not tasked; closing it would mean touching working, already-tested DFU protocol code for a lint-only reason outside this phase's charter.

**The release-note fragment (D-12), for the operator's next beta cut:**

> The minimum supported Python version is now **3.11**. Users on Python 3.9 or 3.10 are **not** told to upgrade by an install error — an unpinned `pip install firestarter` on those interpreters silently installs the last release that still advertised the old floor, with no further updates arriving. Users wanting to keep receiving updates must upgrade to Python 3.11 or later.

Per D-12: this fragment is recorded here for the operator to use at the next beta cut, per this project's operator-gated release process. No release, tag, version bump or `CHANGELOG.md` was created or touched by this phase.

## Issues Encountered

- STRUCTURE.md's provenance-caveat acceptance criterion's count assumption was wrong (see Deviations #2) — dispositioned, not a blocker.
- CONVENTIONS.md's first-draft phrasing leaked a literal `3.9` — self-caught and fixed before commit (see Deviations #1).
- None of the above blocked any task.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- FLOOR-01, FLOOR-02 and FLOOR-03 are all Complete in `.planning/REQUIREMENTS.md`. This phase (186) has no more requirements pending.
- The meta repo's `firestarter_app` gitlink is advanced to `612aa69`; the `firestarter` (firmware) gitlink is untouched, as this phase never touched the firmware repository.
- Backlog 999.67 is filed and will re-fire the same four-statement move when mypy's minimum supported target next rises, or when Python 3.11 reaches its own end of life (2027-10-31) — whichever comes first — with `.planning/notes/python-floor-decision.md` and the fail-closed agreement gate as its evidence trail.
- Neither repository was pushed. This project pushes at ship time only.
- No blockers. This is the phase's last plan.

---
*Phase: 186-the-python-floor-before-the-eol*
*Completed: 2026-09-12*

## Self-Check: PASSED

- `.planning/notes/python-floor-decision.md` exists (155 lines), first line `---`, `## VERDICT` at line 9 before any of the five numbered sections; all nine plan-level acceptance-criteria greps re-run and passing.
- `/usr/bin/grep -rnIE '3\.9|py39' .planning/codebase/` — no output, exit 1.
- `.planning/codebase/STRUCTURE.md:360` still carries its 2026-08-26 provenance caveat (confirmed via `git diff` scoped to line 363 alone).
- `.planning/codebase/CONVENTIONS.md` names `py32_dfu` once, with real post-sweep examples from `address_parser.py`.
- `### Phase 999.67:` exists exactly once in `.planning/ROADMAP.md`, its heading contains `2027-10-31`, and its body cites both `python-floor-decision.md` and `test_python_floor_agreement.py`; snapshot diff shows only the inserted, contiguous block.
- `test -f .planning/notes/python-floor-decision.md` → `POINTER_RESOLVES`, confirming the app repo's `STACK.md` pointer (186-03) now resolves.
- `git log -1 --stat -- firestarter_app` names commit `caff4d4e`; `firestarter_app` HEAD is `612aa6983e781d0d9437071da1d3daaba5e71aae`; `firestarter` gitlink shows no diff.
- Commits `d8759a53`, `face9459`, `d8109932`, `caff4d4e`, `37a0a39f`, `6596b2eb` all found in `git log --oneline --all`.
- `.planning/REQUIREMENTS.md` diff confirmed scoped to the FLOOR-03 checkbox and traceability row.
- `.planning/STATE.md` diff confirmed: frontmatter `progress.completed_phases`/`percent` hand-repaired to `4`/`67` after `state.advance-plan`'s known zeroing bug; `completed_plans` at `28`; `Plan: 3 of 4` → `Plan: 4 of 4`; two new decision bullets; one new metrics-table row; Session section updated. `.planning/config.json` confirmed dirty (known `sub_repos`-pruning verb bug) and deliberately left untouched.
- `git status --short` in the meta repo shows only the pre-existing operator files (`VALIDATED-EPROMS.md`, `anything.txt`, `tmp/`, dirty `config.json`) untouched; `firestarter_app`'s own `git status --porcelain` shows only the two pre-existing untracked datasheet PDFs.
- `git log origin/beta..HEAD --oneline` — 161+ commits ahead, confirming nothing was pushed.
