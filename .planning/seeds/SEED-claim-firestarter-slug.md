---
title: Claim henols/firestarter for the meta repo (the destructive half of 999.9)
trigger_condition: A stable release of the app carrying the firestarter_fw firmware URLs has shipped AND has displaced 2.0.7 as the dominant PyPI version
planted_date: 2026-09-13
status: dormant
---

# Claim `henols/firestarter` for the meta repo

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

`pip install firestarter` resolves to **2.0.7** — the whole `3.0.0bNN` line is prerelease
and invisible to a default install. So the population that breaks is the default install,
not a neglectful tail, and it only moves when a **stable** carrying the new URL ships.
The app performs no self-version check, so a stranded user gets no in-band upgrade hint.

Gate on that stable having shipped and having displaced 2.0.7 — not on a calendar date.

## Do not fire this while any of these is untrue

- The three `FIRESTARTER_*_URL` constants point at `firestarter_fw` on **both** `beta`
  **and** `main` — they are separate changes, and `main` is the one that reaches the
  default install.
- A stable carrying the `main` fix has been published to PyPI.
- `.gitmodules` points at `firestarter_fw` and `git submodule sync --recursive` has run.

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
