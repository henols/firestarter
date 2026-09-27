---
id: gsd-plan-scan-loose-plan-regex-phantom-plan
title: GSD plan-scan's loose /PLAN/i fallback counts non-plan artifacts as plans
captured: 2026-08-18
status: pending
type: bug
target_milestone: v1.32+
priority: low
related_phase: 146
resolves_phase: null
owner: upstream (@opengsd/gsd-core)
---

# GSD `plan-scan.cjs` counts non-plan artifacts as plans

Found during the v1.31 milestone close. **Filed, not fixed** — the defect is in vendored
upstream tooling (`.claude/gsd-core/bin/lib/plan-scan.cjs`), not in this project's code.

## The defect

`isRootPlanFile()` ends with a loose fallback:

```js
return /\.md$/i.test(fileName) && /PLAN/i.test(fileName);
```

So **any** `*.md` in a phase directory whose basename contains the substring `PLAN` —
case-insensitively, anywhere — is counted as a plan. `146-REPLAN-BRIEF.md` matched on
`RE·PLAN·-BRIEF`.

## Measured consequence

Phase 146 has **13** plans and 13 summaries. The scanner reported `plan_count: 14`, so:

- `implementation_complete = planCount > 0 && summaryCount >= planCount` → **false**
- `verification_status` → `not_required` (never even read the real `146-VERIFICATION.md`,
  which says `status: passed`)
- `phase_complete` → **false**, for a phase that was closed and verified
- `gsd-tools query milestone.complete` then wrote `completed_phases: 8`, `total_plans: 75`
  and `percent: 89` into `STATE.md` for a 9/9, 74-plan milestone

The **v1.30** close shows the same signature in git (`completed_phases: 7` of 8,
`percent: 88`), so this has been mis-reporting silently for at least two milestones.

## Workaround applied

`146-REPLAN-BRIEF.md` → `146-RESCOPE-BRIEF.md` (`git mv`), with a provenance note added at
the top of the file recording the original name and this reason. Verified safe first: no file
in the repository referenced the brief by name, so no citation broke. Content byte-unchanged
below the note.

## Real fix (upstream)

Tighten the fallback so it cannot match a derivative artifact — e.g. require a plan-number
shape (`/^\d+[A-Z]?(\.\d+)*-\d+.*PLAN.*\.md$/i`) rather than a bare substring, in the same
spirit as the existing `PLAN_OUTLINE_RE` / `PLAN_PRE_BOUNCE_RE` exclusions and the
`isRootSummaryFile` guard that already prevents `…-PLAN-NN-SUMMARY.md` double-counting.

Note the exclusion list is **denylist-shaped**: every future derivative naming (`-REPLAN-`,
`-PLANNING-`, `-PLAN-NOTES-`) has to be discovered the same way this one was.

## Detection

Anywhere in a project:

```bash
find .planning/phases -maxdepth 2 -name "*.md" -printf "%f\n" \
  | grep -i PLAN | grep -v -- "-PLAN\.md$" | grep -v -- "-SUMMARY\.md$" | sort -u
```

At v1.31 close this returned exactly one file, the one above.
