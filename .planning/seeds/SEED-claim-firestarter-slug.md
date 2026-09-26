---
title: Claim henols/firestarter for the meta repo (the destructive half of 999.9)
trigger_condition: >-
  Fixed share of `(>= 2.0.9) / ((>= 2.0.9) + 2.0.7)` is at or above 90%, AND `2.0.7`
  draws 10 or fewer `pip` plus `uv` downloads, both measured over a rolling 90-day
  window on the stable channel. A single reading from
  `tools/adoption/pypi_version_share.sh` is the evidence. No second consecutive
  reading is required. Re-examine the premise on 2027-09-13 if this has not fired by
  then. That date re-opens the question. It never fires the act itself.
planted_date: 2026-09-13
status: fired
fired_date: 2026-09-14
---

# Claim `henols/firestarter` for the meta repo

> **FIRED 2026-09-14, BY OPERATOR DECISION, AHEAD OF THIS TRIGGER.**
>
> `henols/firestarter_prom` was renamed to `henols/firestarter` (repo id `1232995399`).
> The trigger below was **NOT met** at the time: the reading taken minutes before the
> rename was fixed-share **12.8%** against a 90% threshold, and **116** at-risk `2.0.7`
> downloads against a ceiling of 10 — both over the 90-day stable-channel window ending
> 2026-09-13. The operator was shown those figures and the consequence, and directed the
> act regardless. It was not a threshold breach and it was not an accident.
>
> **What this destroyed:** the redirect `henols/firestarter` → `henols/firestarter_fw`.
> Every CLI at 2.0.7 or older resolves its three firmware endpoints at
> `henols/firestarter`, which is now this repository and carries **0 releases**. Measured
> immediately after: `repos/henols/firestarter/releases` returns `[]` and
> `/releases/latest` returns **404**. Per the impact analysis that 404 is caught in
> `firmware.py` and degrades to a logged error with no firmware found — those users get a
> failure, not a crash, and `fw` stays broken for them until they upgrade.
>
> `henols/firestarter_prom` now redirects here, permanently, because nothing will ever
> claim that slug. So `SUBMIT_REPO` and every recorded issue URL keep working.
>
> Evidence: `.planning/phases/193-the-deferred-claim-made-measurable/evidence/`.
> The trigger text below is retained unchanged as the record of the bar that was set and
> not cleared — it is history now, not a gate.
> The instrument was retired on 2026-09-17; see `.planning/notes/adoption-instrument-retirement.md`.


The deferred, destructive half of Backlog **999.9** (gh#2). The firmware rename
(`firestarter` → `firestarter_fw`) and every URL repoint are safe to do at any time and
belong in 999.9 proper. **This** step — renaming `firestarter_prom` → `firestarter`, which
re-occupies the slug the firmware repo vacated — is the only act in the plan that breaks
anything, and it is the one that must wait.

## Why it is separable

Both renames are individually covered by permanent GitHub redirects. Claiming the freed
`henols/firestarter` slug is what **deletes** the firmware repo's redirect. Until that
moment, every already-installed CLI keeps resolving
`api.github.com/repos/henols/firestarter/releases` correctly.

## Why the trigger is what it is

`pip install firestarter` served **2.0.7** from 2026-01-13 to 2026-09-13. The whole
`3.0.0bNN` line is prerelease and invisible to a default install, so the population that
breaks is the default install, not a neglectful tail. That population moves only once a
**stable** carrying the new URL ships. That stable **has** shipped: it is **2.0.9**,
published to PyPI on 2026-09-13. The app performs no self-version check, so a stranded
user gets no in-band upgrade hint.

The pre-2.0.7 tail is automation, not stranded humans, and it sits outside the
instrument's reach entirely. By quarter, `pip`+`uv` stable-channel downloads of
pre-2.0.7 versions run **398 / 254 / 320 / 265 / 52** (2025-Q3 through 2026-Q3). That
count holds at 250 to 400 even in quarters before 2.0.7 existed, spread thin across
roughly thirty ancient `1.x` versions. No threshold can separate a stranded human down
there from a scanner.

The threshold is a share **AND** an absolute floor, never a share alone. A ratio says
nothing about how many people sit behind it, and the thing that breaks is a count of
humans.

The window is 90 days, not 30. Monthly stable-channel totals show scraper spikes —
**342** in January and **312** in May, against a **34**-to-**75** baseline. A 30-day
window is swamped by one scraper pass.

The values themselves come from the 2.0.6-to-2.0.7 transition, the one natural
experiment this project has run. Share crossed 90% in about six weeks and then
plateaued against a thin tail that never reached zero. This threshold would have fired
roughly three months after that cut.

The baseline at authoring time — 2026-09-14, 90-day window, `pip` plus `uv`, stable
channel — reads: fixed **17**, `2.0.7` **116**, older-stable tail **52**. Fixed share of
the at-risk pair is **12.8%**. Nowhere near firing.

The instrument that produces the reading is `tools/adoption/pypi_version_share.sh`. One
reading over the 90-day window is the evidence. A second consecutive reading is not
required. The window already damps the spikes named above, and overlapping 90-day
windows would make "consecutive" ambiguous anyway.

The reading cannot establish everything. Installed base is not observable, and download
share is a proxy for it. A download of a stranded version today is a **new acquisition**
of an old version — a pin, a cache, a stale tutorial. A user who installed 2.0.7 and
never reinstalls generates zero downloads and stays invisible to this instrument. The
threshold therefore certifies that new acquisition of stranded versions has effectively
stopped — a **necessary condition, never a sufficient one**.

Gate on that stable having shipped and having displaced 2.0.7 — not on a calendar date.
If the trigger has not fired by **2027-09-13** — twelve months from 2.0.9's publish —
the **premise** is re-examined. That date never fires the act. It re-opens the question
of whether the threshold was right, whether the front-door problem was solved another
way, or whether 2.0.7 acquisition is structural.

## Do not fire this while any of these is untrue

- The three `FIRESTARTER_*_URL` constants point at `firestarter_fw` on **both** `beta`
  **and** `main` — they are separate changes, and `main` is the one that reaches the
  default install. **Satisfied.**
- A stable carrying the `main` fix has been published to PyPI. **Satisfied** — it is
  **2.0.9**.
- `.gitmodules` points at `firestarter_fw` and `git submodule sync --recursive` has run.
  **Satisfied on `origin/main`.**
  **Not yet satisfied on `origin/beta`**, whose `.gitmodules` still names the old slug
  until the v1.38 milestone merges.

A met trigger is a measurement, not an authorisation. A human decides. This seed does
not fire itself.

## Carry this rule forward when it fires

**Never publish a GitHub Release on the meta repo.** Bare milestone tags only. Its
zero-Releases state is what keeps the post-claim failure a clean 404 instead of a silent
wrong answer — see `.planning/notes/999.9-repo-rename-impact-analysis.md` for the
`_compare_versions` mechanism that a single Release would arm.

## Known residual, accepted

Users who never upgrade are unreachable by any sequencing. The claim permanently breaks
`fw` for them. Scope is narrow — those three URLs are used only by the `fw` command, so
read, write, verify, erase and `dev test` are unaffected.

Full analysis: `.planning/notes/999.9-repo-rename-impact-analysis.md`.
