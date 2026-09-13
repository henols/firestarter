---
phase: 183-flash4-erase-refusal-the-ae29f2008-classification
plan: 02
subsystem: docs
tags: [chip-database, classification, ae29f2008, w29c020c, gh-62, backlog]

requires:
  - phase: 183-flash4-erase-refusal-the-ae29f2008-classification (RESEARCH.md §B)
    provides: >
      The full equivalence-chain evidence (upstream infoic.xml rows, W29C020C datasheet extracts,
      the D-23 vpp_mv trace) that this plan re-verified in-session and recorded into a durable note.
provides:
  - "A durable, citable SAFE-09 verdict at .planning/notes/ae29f2008-classification-verdict.md"
  - "Four new ROADMAP backlog entries (999.63-999.66) covering the follow-on items this phase surfaced but did not build"
affects: [187-reply-03, safe-06-erase-refusal-record]

actuals:
  tokens: 4750
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Equivalence-based classification verdict record, following the register established by .planning/notes/jumper-display-ground-truth.md"

key-files:
  created:
    - .planning/notes/ae29f2008-classification-verdict.md
  modified:
    - .planning/ROADMAP.md

key-decisions:
  - "Took the D-19/D-20 branch: AE29F2008's algorithm 5 classification is CORRECT and the gh#62 reporter is ALSO correct — the 0x05 firmware path just doesn't implement the chip-erase this silicon supports."
  - "D-21's misclassification-override mechanism was held ready and NOT used — no build_db.py rule, no regeneration, chip_database.json byte-unchanged."
  - "D-23 (vpp_mv: 12000 on a 5V-only part) settled as NOT hardware-live on algorithm 5 — no reader in flash_5v_page.cpp, excluded by name from check_dispatch.py's VPP invariant. Residual display-labelling question filed as backlog 999.65, not fixed."
  - "D-22 upheld: support_status stays supported, not edited."
  - "Software chip-erase for the 0x05 family (D-20) recorded with its boot-block caveat and filed as backlog 999.63, explicitly not built (reverses SAFE-06, needs an explicit operator scope decision)."

patterns-established:
  - "SAFE-09-style investigative requirements produce a durable .planning/notes/ record, not a code diff, when the evidence confirms the status quo is correct."

requirements-completed: [SAFE-09]

coverage:
  - id: D1
    description: "AE29F2008's algorithm 5 classification is verified correct via an equivalence chain (upstream infoic.xml transcription + shared chip_id with W29C020C + independent datasheet confirmation), and the verdict is recorded, never presented as a direct AE29F2008 datasheet reading."
    requirement: "SAFE-09"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter_app && .venv311/bin/python -c \"...AE29F2008_ROW_OK...\""
        status: pass
      - kind: other
        ref: "/usr/bin/grep -c 'equivalence' .planning/notes/ae29f2008-classification-verdict.md"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -n 'a8efaedc236c1d9718bd28299dfbb99536b010ff' .planning/notes/ae29f2008-classification-verdict.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-23's vpp_mv:12000 field is traced end-to-end and settled as not hardware-live on algorithm 5, with the residual display question filed rather than fixed."
    requirement: "SAFE-09"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter && /usr/bin/grep -n 'vpp_mv' src/proms/flash_5v_page.cpp (exit 1, no match)"
        status: pass
      - kind: other
        ref: "cd /workspaces/firestarter_app && /usr/bin/grep -n 'configure_flash_5v_page' tools/check_dispatch.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "chip_database.json, build_db.py and DECODE-NOTES.md are byte-unchanged; no misclassification-branch machinery was invoked."
    requirement: "SAFE-09"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter_app && git status --porcelain -- firestarter/data/chip_database.json tools/build_db.py tools/DECODE-NOTES.md (empty output)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Four ROADMAP backlog entries (999.63-999.66) filed, append-only, covering the software chip-erase, the generalized erase refusal, the VPP display residual, and the PROTOCOLS.md dangling citation."
    verification:
      - kind: other
        ref: "/usr/bin/grep -c '^### Phase 999\\.6[3-6]:' .planning/ROADMAP.md == 4; git diff --stat shows only insertions"
        status: pass
    human_judgment: false

duration: 14min
completed: 2026-09-11
status: complete
---

# Phase 183 Plan 02: AE29F2008 Classification Verdict & Backlog Filing Summary

**Recorded the SAFE-09 verdict as equivalence-based — AE29F2008's algorithm-5 classification is correct AND gh#62's reporter is correct, and filed the four follow-on backlog items this phase surfaces but deliberately does not build.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-09-11T00:00:00Z (session start)
- **Completed:** 2026-09-11
- **Tasks:** 3/3
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments
- Re-verified in this session all four in-repo facts RESEARCH.md's SAFE-09 verdict rests on (DB row agreement, `classify()`'s flash-family pass-through, `FLASH_ERASE`'s six-cycle sequence, `vpp_mv`'s absence in `flash_5v_page.cpp`) — no citation drift found against RESEARCH.md.
- Wrote `.planning/notes/ae29f2008-classification-verdict.md` (220 lines) as the durable, citable SAFE-09 record: the verdict stated up front as equivalence-based, the three-leg evidence chain, the REPLY-03 material on why the reporter's `--force` erase worked and why that's a coincidence not a licence, D-23's settled trace, D-22's confirmation, and D-21's deliberate non-invocation.
- Filed four ROADMAP backlog entries (999.63-999.66), append-only, zero deletions to existing content.

## Task Commits

Each task was committed atomically (Task 1 produced re-verified evidence only, no file changes, so no separate commit):

1. **Task 1: Re-verify SAFE-09's load-bearing in-repo evidence in this session** — no commit (no files modified; evidence folded into Task 2's record)
2. **Task 2: Write the AE29F2008 classification verdict record (D-18, D-19, D-22, D-23)** - `9bfe1bfc` (docs)
3. **Task 3: File backlog entries 999.63-999.66 (D-20, D-05, D-23)** - `205b8c17` (docs)

**Plan metadata:** (pending — this SUMMARY commit)

## Files Created/Modified
- `.planning/notes/ae29f2008-classification-verdict.md` - The durable SAFE-09 verdict record: equivalence-based classification confirmation, REPLY-03 material, D-23 trace, D-21/D-22 dispositions.
- `.planning/ROADMAP.md` - Four new backlog entries (999.63-999.66) appended after 999.62; zero existing content deleted or reflowed.

## Decisions Made
- Took the D-19/D-20 branch (classification CORRECT, reporter also correct) — confirmed on every leg re-verified in this session, matching RESEARCH.md's projection exactly.
- D-21's misclassification-override mechanism was deliberately NOT invoked — `chip_database.json`, `build_db.py`, and `DECODE-NOTES.md` are byte-unchanged, confirmed by `git status --porcelain`.
- D-23 settled as not hardware-live on algorithm 5; the residual display-labelling defect (301 rows across three 5V-only families) is filed as backlog 999.65, not fixed in this phase.
- The software chip-erase capability for the `0x05` family (D-20) is recorded with its boot-block caveat and filed as backlog 999.63, explicitly flagged as reversing SAFE-06's refusal and requiring an explicit operator scope decision — not built here.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None. All four Task 1 re-verification commands reproduced RESEARCH.md's cited facts with zero citation drift (line numbers for `flash_utils.h`'s `FLASH_ERASE` array and `check_dispatch.py`'s VPP-invariant scope note matched exactly). The `flash_5v_page.cpp` grep for `vpp_mv` correctly returned no match (exit 1), confirming the D-23 negative claim.

## Self-Check: PASSED

- `.planning/notes/ae29f2008-classification-verdict.md` exists on disk: FOUND (220 lines)
- `git log --oneline --all --grep="183-02"` returns commits: FOUND (`9bfe1bfc`, `205b8c17`)
- All task-level `<acceptance_criteria>` re-run and passing (see verification commands above)
- Plan-level `<verification>` re-run:
  - Verdict file exists, states equivalence-based verdict, names pinned commit `a8efaedc236c1d9718bd28299dfbb99536b010ff` and shared `chip_id`, carries REPLY-03 material section: PASS
  - Four backlog entries 999.63-999.66 exist; `git diff -- .planning/ROADMAP.md` shows zero deletions: PASS
  - `cd /workspaces/firestarter_app && git status --porcelain -- firestarter/data/chip_database.json tools/build_db.py tools/DECODE-NOTES.md` is empty: PASS
  - Nothing under `firestarter/` or `firestarter_app/` was edited by this plan: PASS (only pre-existing untracked datasheet PDFs remain, unrelated to this plan)
