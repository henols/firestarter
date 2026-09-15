---
phase: 193-the-deferred-claim-made-measurable
plan: 02
subsystem: infra
tags: [gsd-seed, yaml-frontmatter, gate-01, adoption-metrics]

requires:
  - phase: 193-the-deferred-claim-made-measurable
    provides: "tools/adoption/pypi_version_share.sh — the committed instrument this seed now cites by path (193-01)"
provides:
  - "SEED-claim-firestarter-slug.md's trigger_condition rewritten as a parse-safe folded scalar carrying D-09's threshold, window, instrument path and review date verbatim"
  - "The seed's prose brought current with what has actually shipped (2.0.9, past tense) and its readiness checklist scoped to the ref each leg is actually true on"
affects: [193-05]

actuals:
  tokens: 1360
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "YAML folded block scalar (`>-`) for a frontmatter value that must both parse safely and carry backticked tokens — GSD's frontmatter parser rejects a value whose first character is a backtick, but tolerates backticks mid-string once the scalar opens on a word"
    - "Readiness-checklist legs scoped to the ref on which they are true, not asserted globally, when a stated fact differs across branches"

key-files:
  modified:
    - .planning/seeds/SEED-claim-firestarter-slug.md

key-decisions:
  - "Split two originally semicolon-joined clauses in the trigger_condition scalar into separate sentences after the project's asd-ste100 structural lint flagged the semicolons post-edit. The split preserves every fact, number, and condition. Only the punctuation changed."
  - "Put `origin/main` and `origin/beta` on separate lines within the third readiness-checklist bullet, rather than one combined sentence, so the ref-scoping is verifiable by a per-line grep rather than requiring occurrence-counting logic the plan's verify block does not use."
  - "Left `## Carry this rule forward when it fires` and `## Known residual, accepted` untouched — neither contains a version reference or tense construction the D-12 correction pass targets, and the residual section's substance already agrees with the caveat language this plan's prose carries (both state the never-upgrade population is unreachable by any threshold)."

requirements-completed: [GATE-01]

coverage:
  - id: D1
    description: "The trigger_condition frontmatter states D-09's threshold (fixed share >= 90% AND 2.0.7 downloads <= 10) and its 90-day observation window, as a number a reader can evaluate rather than a judgement call"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "node -e against .claude/gsd-core/bin/lib/frontmatter.cjs extractFrontmatter, asserting trigger_condition contains 90, 10, 90-day, 2.0.9, 2.0.7, 2027-09-13, tools/adoption/pypi_version_share.sh"
        status: pass
    human_judgment: false
  - id: D2
    description: "The frontmatter still parses to exactly 4 keys with status: dormant, and the trigger_condition scalar's first character is not a backtick"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "node -e extractFrontmatter: keys=4 status=dormant trigger_len=446 first_is_backtick=false"
        status: pass
    human_judgment: false
  - id: D3
    description: "planted_date: 2026-09-13 and status: dormant survive byte-identical, and the file's five body headings plus the trailing Full analysis line are unchanged"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "/usr/bin/grep -c -E '^(planted_date: 2026-09-13|status: dormant)$' -> 2; /usr/bin/grep -c '^## ' -> 5; /usr/bin/grep -cF 'Full analysis: ...' -> 1"
        status: pass
    human_judgment: false
  - id: D4
    description: "The 'Why the trigger is what it is' section names the instrument (tools/adoption/pypi_version_share.sh) by path. It states one 90-day reading suffices. It states the trigger never fires the act itself. The 2027-09-13 date re-examines the premise, not a calendar-fire"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "/usr/bin/grep -cF 'not on a calendar date' -> 1 (existing sentence preserved verbatim); section text asserts 'That date never fires the act. It re-opens the question...'"
        status: pass
    human_judgment: false
  - id: D5
    description: "The prose is corrected to the past tense throughout. 2.0.9 (published 2026-09-13) is named as the stable that has shipped. 2.0.8 is named nowhere. No sentence places the stable's publication in the future"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "/usr/bin/grep -cF '2.0.8' -> 0; /usr/bin/grep -cE 'will (ship|be published)|has not yet shipped|once a stable ships' -> 0"
        status: pass
    human_judgment: false
  - id: D6
    description: "The readiness checklist's three legs are corrected. Legs 1 and 2 (the FIRESTARTER_*_URL constants and the published stable) are marked satisfied. Leg 3 (.gitmodules) is scoped to the ref it is true on: satisfied on origin/main, not yet satisfied on origin/beta until v1.38 merges. This replaces an unqualified claim a reader could falsify with one git show"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "awk range over the checklist section piped to /usr/bin/grep -c -F -e 'origin/main' -e 'origin/beta' -> 2 (both refs named on separate lines); section still holds exactly 3 bullets"
        status: pass
    human_judgment: false
  - id: D7
    description: "The caveat carries the strong form established in CONTEXT.md D-02. A download of a stranded version today is a new acquisition. The threshold certifies a necessary condition, never a sufficient one. No weaker paraphrase appears"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "/usr/bin/grep -cF 'necessary condition, never a sufficient one' -> 1; phrase 'new acquisition' present twice in the section"
        status: pass
    human_judgment: false
  - id: D8
    description: "A sentence states plainly that a met trigger is a measurement, not an authorisation, and that a human decides — the trigger cannot fire the destructive act by itself"
    requirement: GATE-01
    verification:
      - kind: other
        ref: "Sentence present immediately after the three checklist legs: 'A met trigger is a measurement, not an authorisation. A human decides. This seed does not fire itself.'"
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-09-14
status: complete
---

# Phase 193 Plan 02: The Deferred Claim's Trigger, Made Measurable Summary

**`SEED-claim-firestarter-slug.md`'s `trigger_condition` rewritten from a judgement-call sentence into a parse-safe folded scalar carrying D-09's exact threshold (>= 90% fixed share AND <= 10 at-risk downloads, 90-day window), with the prose corrected to name 2.0.9 in the past tense and the `.gitmodules` readiness leg scoped to the ref it is actually true on.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-09-14T10:56:34Z (approx., immediately after 193-03's completion commit)
- **Completed:** 2026-09-14T11:03:32Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Rewrote `trigger_condition:` as a YAML folded block scalar (`>-`). It begins with a word
  (`Fixed`), not a backtick. This avoids the parser trap RESEARCH F-7 identified. A leading
  backtick makes `extractFrontmatter` return `{}`. That silently drops `status: dormant` and
  unhooks the seed from `audit.cjs`'s `scanSeeds`. Proved the parse directly against GSD's own
  `.claude/gsd-core/bin/lib/frontmatter.cjs`. 4 keys survive. `status` reads `dormant`. The
  parsed `trigger_condition` string contains every one of D-09's numbers, the 90-day window,
  the 2027-09-13 review date, and the instrument's path.
- Rewrote the `## Why the trigger is what it is` section end to end. It names 2.0.9 as the
  stable that **has** shipped (2026-09-13). It never names 2.0.8. It carries the pre-2.0.7
  automation-tail figures (398/254/320/265/52 by quarter). It explains the share-AND-floor
  rationale, the 90-day-not-30 rationale (scraper spikes), and the 2.0.6-to-2.0.7 natural
  experiment. It states the 17/116/12.8% authoring-time baseline. It names the instrument by
  path. It carries the strong "new acquisition" / "necessary condition, never a sufficient
  one" caveat framing verbatim from CONTEXT.md D-02.
- Preserved the existing "Gate on that stable having shipped and having displaced 2.0.7 —
  not on a calendar date" sentence byte-for-byte. Added the 2027-09-13 premise
  re-examination clause beside it. That clause states plainly it re-opens the question. It
  never fires the act.
- Corrected the `## Do not fire this while any of these is untrue` checklist. Legs 1 and 2
  (the `FIRESTARTER_*_URL` constants and the published stable) are genuinely satisfied.
  Phase 190/191 landed them, and the checklist now says so. Leg 3 (`.gitmodules`) is scoped
  to the ref it is true on. `origin/main` is satisfied. `origin/beta` is not, until the v1.38
  milestone merges. This replaces an unqualified claim a reader could falsify with one
  `git show origin/beta:.gitmodules`. Added a closing sentence stating a met trigger is a
  measurement, not an authorisation.

## Task Commits

1. **Task 1: The trigger becomes a number, and the frontmatter is proved to still parse** - `ac30e68b` (feat)
2. **Task 2: The prose catches up with what actually shipped** - `4a0c8dbd` (feat)

**Plan metadata:** pending (this SUMMARY commit)

## Files Created/Modified

- `.planning/seeds/SEED-claim-firestarter-slug.md` — `trigger_condition` frontmatter rewritten
  to a folded scalar carrying D-09's threshold, window, instrument path and review date. The
  "Why the trigger is what it is" section rewritten to the past tense with 2.0.9 named. The
  "Do not fire this while any of these is untrue" checklist's third leg scoped to
  `origin/main` vs `origin/beta`.

## Decisions Made

- **Semicolons split into separate sentences in the trigger_condition scalar.** The project's
  `asd-ste100` structural lint flagged two semicolons in the first draft. Both were split into
  standalone sentences with no loss of fact, condition, or number — the acceptance criteria's
  required substrings (90, 10, 90-day, 2.0.9, 2.0.7, 2027-09-13, the instrument path) were
  re-verified present after the split.
- **`origin/main` and `origin/beta` placed on separate lines within the third checklist bullet.**
  The plan's own verify command counts matching *lines*, not occurrences (`awk` range piped to
  `grep -c -F -e 'origin/main' -e 'origin/beta'`, requiring >= 2). A single combined sentence
  naming both refs on one line would return a count of 1 against that command. Splitting the
  sentence in two, each stating one ref's state, satisfies the letter of the verification.
- **`## Carry this rule forward when it fires` and `## Known residual, accepted` left
  untouched.** Neither section contains a version reference or a tense construction the D-12
  correction pass targets. The residual section's "unreachable by any sequencing" language
  already agrees with the new caveat's "necessary condition, never a sufficient one" framing.
  No reconciliation was needed.

## Deviations from Plan

None - plan executed exactly as written. The two-round edit-and-reverify cycle within Task 2
(described above under "Decisions Made") was driven by two things. First, the project's own
ASD-STE100 lint hook. Second, the plan's own verify command's line-counting semantics. Both
sit within the ordinary acceptance-criteria loop the executor protocol requires ("if a
criterion fails, fix and re-run all criteria"). Neither is a deviation from the plan's
instructions.

## Issues Encountered

None. GSD's `extractFrontmatter` parser and every `/usr/bin/grep`/`awk`/`node` verification
command ran cleanly on the first or second attempt. The second attempt was only needed for
the line-splitting fix above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`SEED-claim-firestarter-slug.md` now states a threshold and observation window a reader can
evaluate with one committed command (`tools/adoption/pypi_version_share.sh`). It still
parses. It is still dormant. It makes no readiness-checklist claim a reader can falsify with
a single `git show`. Plan 193-05 (CLAUDE.md's GATE-02/GATE-03 additions) is unaffected by
this plan's changes and can proceed independently. No blockers.

---
*Phase: 193-the-deferred-claim-made-measurable*
*Completed: 2026-09-14*

## Self-Check: PASSED

- `.planning/seeds/SEED-claim-firestarter-slug.md` exists and its frontmatter parses to 4 keys
  with `status: dormant` via GSD's own `extractFrontmatter`.
- Commits `ac30e68b` and `4a0c8dbd` both present in `git log --oneline --all`.
- All 8 acceptance criteria across both tasks re-verified passing at SUMMARY time (see
  Coverage block above, D1-D8).
- No phase, requirement, decision, or plan citation appears in the seed's prose (`.planning/`
  house norm permits decision-id citations, but none were needed here and none were added).
- Work is on branch `gsd/v1.38-repository-rename-activated-2026-09-13`.
