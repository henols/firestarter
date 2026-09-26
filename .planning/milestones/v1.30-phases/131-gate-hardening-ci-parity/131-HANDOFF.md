# 131-HANDOFF: Operator dispatch of `ci.yml` on the fork base

**Owner requirement:** GATE-07. **Status:** awaiting operator action.

This is an **operator procedure**. Every privileged command below is copy-pasteable prose for the
operator to run from their own shell. No `<automated>` block in this phase's plans contains any of
them — that is a standing rule, not an oversight.

## 1. What is being asked, and why

One dispatch of `ci.yml` on ref `beta`, whose tip is the fork base `16a313a`. The purpose is **not**
to re-establish that the job is red — run `30708836339` (Host CI, `workflow_dispatch`, 2026-08-01)
already did that: every step before the mypy gate went green, `mypy type check (watermark gate)`
failed with *"Process completed with exit code 1"*, and `pytest` plus the entry-point smoke test
never ran.

What this dispatch obtains instead is a **current** post-fork mypy error count on the **exact
commit this milestone forked from** (`16a313a` on `beta`). Research settled on **69** errors as the
honest count (STACK at py3.11 in a numpy-free CI-replica venv, ARCHITECTURE at py3.12 with an
explicit `--python-version 3.12`; both agree on 69, on the 17-file/120-checked shape, and on the
25-in-`firestarter/` / 44-in-`tests/` split). That number is well established, but Phase 132's
watermark must be set from a **current CI run**, not from a devcontainer measurement or from
research's own reproduction — this milestone's own devcontainer has an ambient numpy that truncates
the run to 1 error and reports the gate green, which is the third recorded instance of this
devcontainer masking a CI-only defect. This dispatch is the pre-planning action research's own
adjudication (SUMMARY.md §A-1) named explicitly, to be done "before the roadmap commits to a
watermark number."

## 2. Why exactly one dispatch, not two

A second, post-hardening dispatch (i.e. after Phase 131's gate-hardening lands) would show the
hardened gate at `exit 1` on a 69-error tree — the same red, for the same reason. It buys nothing
and costs an operator round-trip. If a later phase needs the hardened gate proven red-for-the-right-
reason in CI, **Phase 132 gets it for free**: it is the phase that turns the gate green, so its own
dispatch is the proof that the hardened mechanism works end to end.

**Residual, recorded for a later reader:** if Phase 132 is replanned without its own dispatch, this
phase owes a second run to prove the hardened gate in CI. That has not happened as of this writing.

## 3. Why the operator runs it

The standing rule for this whole milestone: no `<automated>` block in any plan may contain
`gh workflow run`, `git push`, `git merge` into `beta`, `git tag`, `gh release …`, or
`twine upload`. Dispatching a workflow is a privileged, outward-facing action reserved to the
operator. It therefore lives here, as prose, never as an agent-executed step.

## 4. Safety

`ci.yml`'s `push` trigger is `branches: [main]` only (confirmed by reading the file at execution
time: `on: push: branches: [main]`, lines 9–11). A `workflow_dispatch` on `beta` therefore fires
**`ci.yml` and nothing else**:

- `beta-release.yml` is triggered by pushes to `beta` — but this is a `workflow_dispatch`, not a
  push, so it does not fire.
- `release.yml` / `publish.yml` are tag/PyPI-only triggers — unaffected by any dispatch or push to
  `beta`.

No branch push is required — `beta` already exists at `16a313a`; the dispatch targets an existing
ref.

## 5. The commands

Run these, in order, from any directory with `gh` authenticated against `henols/firestarter_app`:

```bash
# 1. Dispatch ci.yml on the fork base
gh workflow run ci.yml --repo henols/firestarter_app --ref beta

# 2. Wait roughly a minute, then list recent runs to find the new one
gh run list --workflow=ci.yml --repo henols/firestarter_app --limit 3

# 3. Identify the run whose event is `workflow_dispatch` and branch is `beta`.
#    Wait for it to reach a terminal conclusion (expected: failure, on the mypy gate step).
```

The agent runs these **read-only** follow-ups itself once given the run id — do not run them
yourself unless you want to see the same thing early:

```bash
gh run view <id> --repo henols/firestarter_app
gh run view <id> --repo henols/firestarter_app --log
```

## 6. What to hand back

Exactly one thing: **the numeric run id** (e.g. `30708836339`). Nothing else needs to be
transcribed — the agent reads the step statuses, the log, mypy's resolved version, and the Python
version for itself directly from the run.

A fabricated, guessed, or placeholder id will be caught: task 3 of `131-05-PLAN.md` opens with a
fail-closed precondition that resolves the supplied id via `gh run view` before writing a single
file, and rejects it if it does not resolve, is not a `workflow_dispatch` on `beta`, does not have a
head SHA beginning `16a313a`, equals the prior run `30708836339` (a re-used id is not a current
measurement), or has not reached a terminal conclusion.

## 7. What this run does NOT establish

The `ci` job is **expected to be RED** on the `mypy type check (watermark gate)` step, and the
steps after it (`pytest`, the entry-point smoke test) will **not run**. That is the current,
correct state of the fork base, and it stays that way after Phase 131 completes: this phase hardens
the gate mechanism and the CI-parity recipe — it fixes **zero** of the inherited mypy errors and
sets **no** watermark. Phase 132 is the phase that turns the job green. **Any artifact in this
milestone claiming CI is green as a result of Phase 131 is an overclaim** (the v1.22 C-5 class).

---

*Phase: 131-gate-hardening-ci-parity — Plan 05, Task 1*
