# Deferred items — Phase 201

Out-of-scope discoveries logged during execution, per the executor's scope-boundary rule. Not
fixed here; recorded so they are not mistaken for something this phase's plans caused.

## 1. Pre-existing untracked file makes `firestarter_app` read as dirty (found during plan 201-06)

`git status --porcelain firestarter_fw firestarter_app` from `/workspaces` reports ` M
firestarter_app`. The cause is a single untracked file inside the submodule,
`firestarter_app/datasheets/LST62832I.pdf`, with an on-disk mtime of 2026-09-19 09:48 — created
the day before this bench session and unrelated to any commit in this phase. `git -C
firestarter_app status` shows no tracked-file modifications and the gitlink SHA recorded in the
meta repo matches `firestarter_app`'s actual HEAD; the only reason the submodule reads dirty is
that untracked file.

This predates plan 201-06's bench session and was not created by it. It is out of scope per the
executor's scope-boundary rule ("only auto-fix issues DIRECTLY caused by the current task's
changes") and is left in place rather than deleted without the operator's say-so. It does mean
`201-06-PLAN.md` Task 2's own automated verify leg (`test -z "$DIRTY"` over `firestarter_fw
firestarter_app`) reads dirty for a reason that has nothing to do with the bench work recorded
under it. Recorded here so a later reader does not chase it as a regression this phase introduced.
