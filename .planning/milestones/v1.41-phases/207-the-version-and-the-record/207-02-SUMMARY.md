---
phase: 207-the-version-and-the-record
plan: 02
subsystem: docs
tags: [wiki, release-notes, compatibility-matrix, breaking-changes, cli-reference]

# Dependency graph
requires:
  - phase: 207-the-version-and-the-record
    provides: "plan 01's 3.1.0b1 bump pair in firestarter_fw and firestarter_app (the product version this plan documents)"
provides:
  - "Breaking-Changes.md 3.1.0b1 entry: retired commands (4 and 6), the mixed-version matrix in both directions, and what to do"
  - "the new Writing-and-Verifying.md page: write -b/--skip-erase, write --verify/--full, verify, blank, erase -b, all from 3.1.0b1"
  - "Home.md and _Sidebar.md navigation to the new page"
  - "version-pairing notes on Install-Beta.md and Testing-Chips.md"
  - "three local, unpushed wiki commits on top of f967398, proven link-clean and free of planning identifiers"
affects: [207-03-wiki-push, ship]

# Actuals (#2632)
actuals:
  tokens: 2957
  tasks: 3
  commits: 3
  plan_head_before: "N/A — wiki-clone plan; commits measured against the wiki clone's own pre-plan tip f967398fdf653f4ee77f7ad07b37a416927763be (git rev-list --count f967398..HEAD = 3), not the meta repo's commit ledger, because this plan's ledger lives in a declared sub_repo (firestarter.wiki), not in /workspaces itself"

tech-stack:
  added: []
  patterns:
    - "Per-entry compatibility statements in Breaking-Changes.md, replacing a page-wide claim that later became false — the shape a later breaking change should follow too"
    - "A command-reference wiki page (Writing-and-Verifying.md) transcribed verbatim from the snapshot-pinned --help text, following the Testing-Chips.md / Install-Beta.md structural precedent"

key-files:
  created:
    - firestarter.wiki/Writing-and-Verifying.md
  modified:
    - firestarter.wiki/Breaking-Changes.md
    - firestarter.wiki/Home.md
    - firestarter.wiki/_Sidebar.md
    - firestarter.wiki/Install-Beta.md
    - firestarter.wiki/Testing-Chips.md

key-decisions:
  - "D-02 (locked, operator): wiki work committed in the existing /workspaces/firestarter.wiki clone on top of the unpushed f967398 — verified: git rev-list --reverse origin/master..HEAD starts with f967398 and holds exactly four commits"
  - "D-03 (locked, operator): every new statement labelled 'from 3.1.0b1' — every new ### sub-section of the Breaking-Changes entry and every new ## section of Writing-and-Verifying.md carries the literal 3.1.0b1"
  - "F3 option A (Claude's discretion, taken): a new page Writing-and-Verifying, because no wiki page documented any command and a user looking for 'how do I verify a write' would not look in Breaking Changes"
  - "F4 (taken): heading is '## 3.1.0b1 — verify and blank check run on the host', in the page's existing '## <label> — <topic>' shape, using the product version rather than a milestone label. The existing v1.32/v1.20/v1.10 headings were left unrelabelled, per the plan's explicit prohibition"
  - "F5 (taken, with the plan's recorded departure): the page-wide preamble became a per-entry statement ('Each entry says which mixed CLI and firmware pairings work.'). Departure from research: the install one-liner gained --upgrade (pip install --pre --upgrade firestarter), because the reader is upgrading an existing install and plain 'pip install --pre firestarter' would leave an older CLI in place before flashing new firmware — exactly the unguarded pairing the new entry warns about"
  - "F9 (taken): no catalog id for the retired commands. The only sender of ordinals 4 and 6 is a pre-3.1.0 CLI rendering through its own already-shipped messages.py, which this phase cannot change and which a new id could not reach. The wiki quotes the verbatim 'ERROR: Unknown command: N' text instead, so a search for it lands on the explanation. This closes the deferral chain from Phase 204 D-05 through Phase 205 to this plan"
  - "F10 (taken): the full compatibility matrix in both directions is documented, leading with the unguarded write (the one pairing that can harm a chip). The two code-derived rows (an older CLI's erase -b not checking; a 3.1.0b1 CLI's plain erase blank-checking on older firmware) each carry the phrase 'not yet observed on hardware', matching the hedge register the page already uses for its v1.32 entry"

patterns-established:
  - "Wiki breaking-change entries lead with the pairing that can cause physical harm, not the pairing that is merely inconvenient (F10)"
  - "Code-derived (not bench-observed) compatibility claims are marked 'not yet observed on hardware' rather than stated with bench-observed confidence"

requirements-completed: []
# REL-04 is NOT marked complete by this plan. This plan authors and commits the wiki content
# locally; plan 207-03 publishes it behind an operator checkpoint and is REL-04's remaining half.
# The orchestrator owns REQUIREMENTS.md and should mark REL-04 complete only after 207-03 lands.

coverage:
  - id: D1
    description: "Breaking-Changes.md documents the 3.1.0b1 compatibility break: retired commands 4 and 6 (verbatim refusals), the mixed-version matrix in both directions leading with the unguarded write, and what a user does about it"
    requirement: "REL-04"
    verification:
      - kind: other
        ref: "PASS-207-02-T1 and PASS-207-02-T1-LABELS (Task 1 verify legs, re-run against the final committed blob)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Writing-and-Verifying.md documents write (-b/--no-blank-check, --skip-erase, which parts the CLI checks), write --verify and --full with exit codes and verdict lines, verify and blank with --full, and erase -b — reachable from Home, the sidebar and the Breaking-Changes entry"
    requirement: "REL-04"
    verification:
      - kind: other
        ref: "PASS-207-02-T2-CONTENT and PASS-207-02-T2-NAV"
        status: pass
    human_judgment: false
  - id: D3
    description: "Install-Beta.md and Testing-Chips.md carry version-pairing notes; the whole outgoing wiki change (f967398 plus 3 commits) is link-clean, free of planning identifiers, and the live wiki is unmoved"
    requirement: "REL-04"
    verification:
      - kind: other
        ref: "PASS-207-02-T3 and PASS-207-02-SWEEP"
        status: pass
    human_judgment: false

duration: ~11min
completed: 2026-09-23
status: complete
---

# Phase 207 Plan 2: The version and the record Summary

**Three local, unpushed wiki commits on top of `f967398`: the 3.1.0b1 breaking-change entry (retired commands 4/6, the mixed-version matrix, what to do), a new `Writing-and-Verifying` command-reference page, and version-pairing notes on Install-Beta and Testing-Chips — nothing published.**

## Performance

- **Duration:** ~11 min
- **Started:** 2026-09-23T15:13:00Z (approx.)
- **Completed:** 2026-09-23T15:23:31Z
- **Tasks:** 3
- **Files modified:** 6 (1 created, 5 modified)

## Accomplishments
- Rewrote `Breaking-Changes.md`'s page-wide "every mismatch fails with a timeout" preamble (which the 3.1.0b1 release makes false) into a per-entry statement, and added the `## 3.1.0b1 — verify and blank check run on the host` entry: two sub-sections quoting the verbatim `ERROR: Unknown command: 6` / `ERROR: Unknown command: 4` / `ERROR: Not blank, at 0x000000, v: 0x11` refusals, leading with the unguarded-write hazard (an older CLI no longer stops a write to a non-blank UV EPROM against 3.1.0b1 firmware), and a `### What to do` section with the upgrade commands.
- Authored a new page, `Writing-and-Verifying.md`, the wiki's first page documenting `write`, `verify`, `blank` or `-b` at all: the CLI-side pre-write blank check and which chip families it applies to, `write --verify`/`--full` with their exit-code contract and all four verdict lines, `verify`/`blank` with their `--full` output shape and classification labels, `erase -b`'s inverted-sense check, and an exit-codes-at-a-glance table. Linked it from `Home.md`, `_Sidebar.md` and the Breaking-Changes entry.
- Added a version-pairing sentence to `Install-Beta.md` § 3 ("upgrade the CLI before flashing") and to `Testing-Chips.md` § "How to report it" ("a report is only valid when the CLI and the firmware are on the same side of 3.1.0b1"), and refreshed the stale `--version` example to `3.1.0b1`.
- Ran the whole-wiki pre-publication sweep: every internal `](Page-Name)` link resolves, no page or outgoing commit message carries a phase number, `D-NN` id, `.planning/` path or `v1.4x` label, the outgoing commit count is exactly `f967398` plus 3, the live `master` is still `81229d8` (nothing pushed), and `tools/catalog` in the meta repo is untouched (F9: no new catalog id).

## Task Commits

Each task was committed atomically, in `/workspaces/firestarter.wiki` on `master`:

1. **Task 1: Breaking-Changes end to end** — `39f46e4` (docs) — `Document the 3.1.0b1 compatibility break between the CLI and the firmware`
2. **Task 2: The Writing-and-Verifying page** — `6894ed3` (docs) — `Add Writing and Verifying: write, verify, blank and erase -b from 3.1.0b1`
3. **Task 3: Version-pairing notes + sweep** — `880a59b` (docs) — `Say which CLI and firmware versions go together when installing and testing`

**Plan metadata:** this SUMMARY, committed in the meta repo on `v1.41-verification-to-host` (see hash below).

_Note: no TDD tasks in this plan; each commit above is a single production step._

## Files Created/Modified

- `firestarter.wiki/Breaking-Changes.md` — per-entry preamble, plus the new `## 3.1.0b1 …` entry and its link to the new page
- `firestarter.wiki/Writing-and-Verifying.md` (new) — the only wiki page documenting `write`, `write --verify`/`--full`, `verify`, `blank` and `erase -b`
- `firestarter.wiki/Home.md` — one new `## Reference` bullet
- `firestarter.wiki/_Sidebar.md` — one new nav line, after `Testing Chips`
- `firestarter.wiki/Install-Beta.md` — refreshed `--version` example; one new sentence in § 3
- `firestarter.wiki/Testing-Chips.md` — one new paragraph in § "How to report it"; footer untouched

## Decisions Made

See `key-decisions` in the frontmatter for D-02, D-03, and forks F3, F4, F5, F9, F10, including the recorded F5 departure (`--upgrade` added to the preamble's install one-liner).

**No place was found where the code disagreed with this plan's summary of it.** Every flag, exit code, verdict line and classification label transcribed into `Writing-and-Verifying.md` matched the snapshot-pinned `--help` text in `firestarter_app/tests/__snapshots__/test_characterization.ambr` and the source read alongside it (`write_blank_guard.py`, `compare.py`, `database.py`), and the two code-derived compatibility rows matched `firestarter_fw/src/proms/eprom.cpp` (current tree) against `git show 3.0.0b35:src/proms/eprom.cpp`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Task 1's commit initially linked to a page that did not exist yet**
- **Found during:** Task 1, immediately after committing
- **Issue:** The plan's Task 1 action explicitly says "Do not link to the new page yet: Task 2 adds that link in the same commit that creates the page, so the link check stays green at every commit." The Task 1 draft nonetheless included the `[Writing-and-Verifying](Writing-and-Verifying)` sentence in the same commit, before `Writing-and-Verifying.md` existed — a self-inconsistent commit state, even though no automated verify leg in this plan checks link-resolution per-commit (only the final working-tree state).
- **Fix:** Removed the forward-reference sentence, amended Task 1's commit (`git commit --amend --no-edit -- Breaking-Changes.md`, parent unchanged at `f967398`), re-ran Task 1's two verify legs (`PASS-207-02-T1`, `PASS-207-02-T1-LABELS`) against the amended commit to confirm nothing else regressed, then added the same sentence back as part of Task 2's commit alongside the new page and its navigation lines, matching the plan's intended shape.
- **Files modified:** `firestarter.wiki/Breaking-Changes.md`
- **Verification:** Both Task 1 verify legs re-run and passed against the amended commit; Task 2's `PASS-207-02-T2-NAV` (which checks the link resolves) passed against the final state.
- **Committed in:** `39f46e4` (amended Task 1 commit, link removed), `6894ed3` (Task 2 commit, link restored)

---

**Total deviations:** 1 auto-fixed (Rule 1 — a plan-instruction ordering slip, corrected before any other work depended on the affected commit's sha).
**Impact on plan:** None on content or scope. The only sub-repo affected is the wiki clone itself; nothing outside this plan referenced the pre-amend sha (it was never pushed, and no other task or file cited it).

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- REL-04 is **advanced, not complete**, by this plan (per this plan's explicit dispatch instruction): the wiki content is authored and committed locally, proven link-clean and free of planning identifiers by the Task 3 sweep, but nothing is published. Plan 207-03 publishes it behind an operator `checkpoint:human-action` and is REL-04's remaining half.
- The live wiki `master` is unchanged at `81229d8ed8a280b935cf84c4c74f4c97afcdf475` — confirmed by `git ls-remote origin refs/heads/master` inside the Task 3 sweep.
- The wiki clone carries exactly 4 outgoing commits ahead of `origin/master`: `f967398` (pre-existing, unpushed, named per D-02) plus this plan's 3 commits (`39f46e4`, `6894ed3`, `880a59b`).
- `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` and `.planning/config.json` were not touched by this executor, per this plan's dispatch instructions — the orchestrator owns them and should hand-mark progress after reviewing this SUMMARY, without marking REL-04 complete until 207-03 also lands.
- Nothing was pushed or tagged from any of the three repositories in this plan.

## Self-Check: PASSED

- `[ -f /workspaces/firestarter.wiki/Writing-and-Verifying.md ]` → FOUND.
- `[ -f /workspaces/firestarter.wiki/Breaking-Changes.md ]` → FOUND, carries the `## 3.1.0b1 …` entry.
- `[ -f /workspaces/firestarter.wiki/Home.md ]` → FOUND, carries the new Reference bullet.
- `[ -f /workspaces/firestarter.wiki/_Sidebar.md ]` → FOUND, carries the new nav line.
- `[ -f /workspaces/firestarter.wiki/Install-Beta.md ]` → FOUND, carries the refreshed example and the new sentence.
- `[ -f /workspaces/firestarter.wiki/Testing-Chips.md ]` → FOUND, carries the new paragraph; footer byte-identical to `f967398`'s.
- `git -C /workspaces/firestarter.wiki log --oneline --all | grep -q 39f46e4` → FOUND.
- `git -C /workspaces/firestarter.wiki log --oneline --all | grep -q 6894ed3` → FOUND.
- `git -C /workspaces/firestarter.wiki log --oneline --all | grep -q 880a59b` → FOUND.
- All task-level verify legs re-confirmed: `PASS-207-02-T1`, `PASS-207-02-T1-LABELS`, `PASS-207-02-T2-CONTENT`, `PASS-207-02-T2-NAV`, `PASS-207-02-T3`, `PASS-207-02-SWEEP` all printed.
- `git -C /workspaces/firestarter.wiki rev-parse --abbrev-ref HEAD` prints `master`.
- `git -C /workspaces rev-parse --abbrev-ref HEAD` prints `v1.41-verification-to-host`.
- `git -C /workspaces/firestarter.wiki ls-remote origin refs/heads/master` prints `81229d8ed8a280b935cf84c4c74f4c97afcdf475` (unchanged; nothing pushed).

## Full Sweep Output (Task 3, `PASS-207-02-SWEEP` leg)

```
$ cd /workspaces/firestarter.wiki && git fetch -q origin && \
  for p in 'Unknown command: 6' 'Unknown command: 4' '3.1.0b1' \
    'pip install --pre --upgrade firestarter' '--verify' '--full' \
    '--no-blank-check' 'Refusing write to'; do
    /usr/bin/grep -qF -e "$p" *.md || { echo "MISSING: $p"; exit 1; }
  done
  # (no output — every required fact present)
  /usr/bin/grep -nE 'Phase [0-9]{3}|\bD-[0-9]+\b|\.planning/|v1\.4[0-9]' *.md
  # (no output — no planning identifier in any page)
  git log --format=%B origin/master..HEAD | \
    /usr/bin/grep -nE 'Phase [0-9]{3}|\bD-[0-9]+\b|\.planning/|v1\.4[0-9]|\b20[0-9]-[0-9]{2}\b'
  # (no output — no planning identifier in any outgoing commit message)
  # link check: every ](Page-Name) resolves to Page-Name.md — no BROKEN: lines
  git rev-list --count origin/master..HEAD            # => 4
  git rev-list --reverse origin/master..HEAD | head -1 # => f967398fdf653f4ee77f7ad07b37a416927763be
  git ls-remote origin refs/heads/master | cut -f1     # => 81229d8ed8a280b935cf84c4c74f4c97afcdf475
  git -C /workspaces status --porcelain -- tools/catalog  # (empty)
  git status --porcelain                                  # (empty)
  echo PASS-207-02-SWEEP
PASS-207-02-SWEEP
```

---
*Phase: 207-the-version-and-the-record*
*Completed: 2026-09-23*
