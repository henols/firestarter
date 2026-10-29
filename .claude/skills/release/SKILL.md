---
name: release
description: Cut a release of the Firestarter CLI (firestarter_app) or firmware (firestarter_fw). A script computes the next version tag, checks CI, pushes the tag, watches the release run, verifies GitHub and PyPI, and opens the meta CHANGELOG/gitlink PR. Use when asked to release, publish, tag or ship the app or the firmware, cut a beta or pre-release, promote a beta to stable, bump the minor or major version, push to PyPI, or make 3.x.y / the next b-number.
---

# Release a sub-repo

The script does all the work. Your job: know the repo, ask the release type, show the plan,
get one confirmation, run it.

```bash
S=/workspaces/.claude/skills/release/scripts

python3 $S/release.py <app|fw> <pre|regular|minor|major>                 # dry run: checks + PLAN
python3 $S/release.py <app|fw> <type> --yes --expect <VERSION>           # publish
python3 $S/release.py --selftest                                         # offline tests
```

Never choose a version yourself. The script computes it. To publish, run the `publish:`
command that the PLAN prints; its `--expect` value is the version that the operator confirmed.
For a release from `main`, never call `git tag` or the sub-repos' `tools/release.sh`. Never
work around a check that the script refuses.

## Steps

1. **Repo.** Infer `app` (firestarter_app, the CLI, PyPI) or `fw` (firestarter_fw, the
   firmware) from the conversation. Ask only if it is unclear. A new line (`minor`/`major`)
   with no repo named: suggest both, because the CLI and the firmware must share `X.Y`.
2. **Type.** When the request names the type plainly, do not ask. Say which type you read; the
   confirmation in step 4 catches a misread. "Beta" means `pre` unless a new line (3.3, 4.0)
   is named. "Stable" or "the real release" means `regular`. Otherwise ask with
   AskUserQuestion, or return the question to your caller when you cannot ask. Show the
   version that each option gives:

   | Type | From a beta `3.2.7b3` | From a stable `3.2.6` |
   |---|---|---|
   | `pre` | `3.2.7b4` | `3.2.7b1` |
   | `regular` (stable) | `3.2.7` (promote) | `3.2.7`, refused (no beta on the commit) |
   | `minor` | `3.3.0b1` | `3.3.0b1` |
   | `major` | `4.0.0b1` | `4.0.0b1` |

   `minor` and `major` always start with a beta. Later `pre` runs give `b2, b3…`, and
   `regular` promotes the line to stable. An `rc` tip continues as `rcN+1`.
3. **Dry run.** Run it without `--yes`. Show the operator these lines: the version line, the
   `target` line, the `changes since` list, every `WARN`, and the `PLAN` line.
   - On `REFUSED`, report the `FAIL` lines and stop. Refer to Troubleshooting.
   - For a missing CHANGELOG entry, offer to draft it as a meta PR from the commits since the
     last stable tag. Do not draft it unasked. The operator merges it, then you run again.
4. **Confirm once.** The tag push publishes, and a PyPI version can never be used again. Ask
   one yes/no question that names:
   - the exact version and the commit;
   - for `regular`, the beta that it promotes (the `pre-release … is on the same commit` line);
   - for `minor`/`major`, what `main` holds. A new line is usually named for a feature. Ask
     whether that feature is on `main`, or still on a branch such as `perf/fw-offload`.

   For "both", confirm both plans in one question. Choosing `regular` and confirming is the
   operator's stable go-ahead.
5. **Publish.** Run the `publish:` command that the PLAN printed. A release run takes 4 to 25
   minutes, so use `run_in_background: true` and wait for the notification. Report the release
   URL, PyPI (app) and the meta PR URL (stable only). `--no-meta` skips the meta PR; use it only
   when the operator asks.
   - For "both", run them one at a time: app first, then fw after the app succeeds. A newer CLI
     operates older firmware, but older CLIs refuse newer firmware with a higher `X.Y`. If the
     app fails, do not start fw.

## What a run does

- **Dry run** (no `--yes`): runs the checks and prints `PLAN` or `REFUSED`. It pushes nothing.
- **`--yes --expect V`**: runs the same checks again, and refuses when the next version is no
  longer `V`. Then it pushes the tag on the `origin/main` commit, waits for the release run, and
  checks the GitHub release and, for the app, PyPI. Your local checkout does not change.
- **Stable only**: it then opens a meta PR that records the CHANGELOG entry and moves the
  gitlink. It never merges the PR.
- It never tags or releases the meta repo (CLAUDE.md, Release Hazards).

## Real output

Dry runs captured on 2026-10-29 against the live repos:

```
$ python3 $S/release.py fw pre
firestarter_fw: latest tag 3.2.3b2 -> 3.2.3b3 (pre-release)
  target origin/main c70ce14 Merge pull request #107 from henols/fix/p1-read-level-null-deref
  changes since 3.2.3b2: 0 commit(s) on main
  WARN main has nothing new since 3.2.3b2; 3.2.3b3 would publish the same code
  ok   tag 3.2.3b3 is free
  ok   3.2.3b3 sorts above every release tag
  ok   CI green: Firestarter CI, PY32F071 firmware
  ok   pre-release: no meta follow-up

PLAN fw 3.2.3b3 (pre-release) on origin/main c70ce14
  publish: python3 /workspaces/.claude/skills/release/scripts/release.py fw pre --yes --expect 3.2.3b3
```

```
$ python3 $S/release.py fw regular
firestarter_fw: latest tag 3.2.3b2 -> 3.2.3 (stable)
  target origin/main c70ce14 Merge pull request #107 from henols/fix/p1-read-level-null-deref
  changes since 3.2.3b2: 0 commit(s) on main
  ok   tag 3.2.3 is free
  ok   3.2.3 sorts above every release tag
  ok   CI green: Firestarter CI, PY32F071 firmware
  ok   pre-release 3.2.3b2 is on the same commit
  FAIL CHANGELOG [Unreleased] on meta main has no '- **Firmware:**' items; write the entry and merge it first (RELEASING.md 2.1)
  ok   after the release: a meta PR records the CHANGELOG and moves the gitlink

REFUSED fw 3.2.3: 1 check(s) failed. Nothing pushed.
```

**Not yet run:** a real `--yes` publish. Watch the first one closely.

## Out of scope

Refer to [RELEASING.md](/workspaces/RELEASING.md) for these:

- A release from a maintenance branch `release/X.Y` (section 2.4). The script tags
  `origin/main` only; the dry run's `target` line shows the commit.
- An `rc` tag for a new line. The types never start one.
- After a firmware release, the check on a real board: `firestarter fw -i -b <board>` (section
  2.2). It is hardware, so the operator does it.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `FAIL CHANGELOG [Unreleased] … has no … items` | Write the entry in the meta `CHANGELOG.md` under `[Unreleased]`, with each bullet starting `- **CLI:**` or `- **Firmware:**`. Merge it to meta `main`, then run again. |
| `FAIL CHANGELOG already records …` | That part already has this version. Look at the tags: the release may already be done. |
| `FAIL no pre-release tag on this commit` | Stable needs a tested beta of the same commit. `main` moved after the last beta, or the latest tag is already stable. Release `pre`, test it, then `regular`. |
| `FAIL … is below X.Y, the binary-frame floor on main` | `main` already holds the next line. Start it with `minor`. |
| `FAIL CI not green` | Wait for the run, or fix `main`. Do not release over a red CI. |
| `FAIL … does not sort above …` | A higher tag exists. Report it to the operator. |
| `FAIL a local tag … exists that origin does not have` | A stale local tag. Run the `git tag -d` that it prints, then run again. |
| `WARN main has nothing new since …` | The new tag would rebuild the same commit. Ask whether the operator wants that, for example after a CI fix. Usually they do not. |
| `WARN no CI run on main for this commit` | Usually a doc-only commit. Tell the operator, and continue only when they agree. |
| `WARN … must share X.Y` | In a "both" run this is expected; it clears when the second repo is published. Otherwise, the other repo must get the same `X.Y` before the line goes stable. |
| `REFUSED: the next version is now …` | Someone tagged between the dry run and `--yes`. Show the new plan and confirm again. |
| The release run failed after the push | Follow the recovery that the script prints (RELEASING.md 2.3). Delete the tag only when the run failed before the GitHub release was created. When PyPI has the version, never use it again. |
| `FAIL release flags …`, `FAIL assets missing …` or `FAIL PyPI has no …` after the push | The version is published. Report the lines to the operator, and follow RELEASING.md 2.3. |
| `error: branch docs/release-… already exists on origin` | The meta PR for this release exists. Open it, or delete the stale branch. |
| `error: … is not checked out` | Run from the main `/workspaces` checkout, not from a worktree. Worktrees have empty submodules. |
