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
python3 $S/release.py <app|fw> <type> --yes --expect <VERSION>          # publish
python3 $S/release.py --selftest                                         # offline tests
```

Every release goes through this script, and the script computes the version. To publish, run
the `publish:` command that the PLAN prints. Its `--expect` value is the version that the
operator confirmed.

## Steps

1. **Repo.** Infer `app` (firestarter_app, the CLI, PyPI) or `fw` (firestarter_fw, the
   firmware) from the conversation. Ask only if it is unclear. A new line (`minor`/`major`)
   with no repo named: suggest both, because the CLI and the firmware must share `X.Y`.
   Every release tags `main`. There is no maintenance branch for an older line.
2. **Type.** When the request names the type plainly, use it and say which type you read; the
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
   - On `REFUSED`, report the `FAIL` lines and stop. Troubleshooting has the fix for each.
   - For a missing CHANGELOG entry, offer to draft it as a meta PR from the commits since the
     last stable tag. Draft it when the operator says yes. The operator merges it, then you run
     again.
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
   URL, PyPI (app) and the meta PR URL (stable only). Add `--no-meta` when the operator asks to
   skip the meta PR.
   - For "both", run them one at a time: the app first, then fw after the app succeeds. A newer
     CLI operates older firmware, but older CLIs refuse newer firmware with a higher `X.Y`.

## What a run does

- **Dry run** (no `--yes`): runs the checks and prints `PLAN` or `REFUSED`. It pushes nothing.
- **`--yes --expect V`**: runs the same checks again, and refuses when the next version is no
  longer `V`. Then it pushes the tag on the `target` commit, waits for the release run, and
  checks the GitHub release and, for the app, PyPI. Your local checkout does not change.
- **Stable only**: it then opens a meta PR that records the CHANGELOG entry and moves the
  gitlink. The operator merges the PR.

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

A dry run on 2026-10-29 after `main` became the 3.3 line. A `pre` from `3.2.3b2` stays on 3.2,
so the floor check refuses it; the 3.3 line starts with `minor`:

```
$ python3 $S/release.py fw pre
firestarter_fw: latest tag 3.2.3b2 -> 3.2.3b3 (pre-release)
  target origin/main 0d05f67 Merge pull request #112 from henols/chore/purge-release-3.2
  changes since 3.2.3b2: 4 commit(s) on main
  ok   tag 3.2.3b3 is free
  ok   3.2.3b3 sorts above every release tag
  FAIL 3.2.3b3 is below 3.3, the binary-frame floor on main; release.yml would refuse the tag. Start the line with 'minor'
  ok   pre-release: no meta follow-up

REFUSED fw 3.2.3b3: 1 check(s) failed. Nothing pushed.
```

**Not yet run:** a real `--yes` publish. Watch the first one closely.

## Out of scope

Refer to [RELEASING.md](/workspaces/RELEASING.md) for these:

- An `rc` tag for a new line. The types never start one.
- After a firmware release, the check on a real board: `firestarter fw -i -b <board>` (section
  2.2). It is hardware, so the operator does it.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `FAIL CHANGELOG [Unreleased] … has no … items` | Write the entry in the meta `CHANGELOG.md` under `## [Unreleased]`. Each bullet starts with `- **CLI:**`, `- **Firmware:**` or `- **CLI, Firmware:**`. Merge it to meta `main`, then run again. |
| `FAIL CHANGELOG already records …` | That part already has this version. Look at the tags: the release may already be done. |
| `FAIL no pre-release tag on this commit` | Stable needs a tested beta of the same commit. The branch moved after the last beta, or the latest tag is already stable. Release `pre`, test it, then `regular`. |
| `FAIL … is below X.Y, the binary-frame floor on main` | `main` already holds the next line. Start it with `minor`. |
| `FAIL CI not green` | Wait for a green run, or fix the branch. |
| `FAIL … does not sort above …` | A higher tag exists. Report it to the operator. |
| `FAIL a local tag … exists that origin does not have` | A stale local tag. Run the `git tag -d` that it prints, then run again. |
| `WARN … has nothing new since …` | The new tag would rebuild the same commit. Ask whether the operator wants that, for example after a CI fix. Usually they do not. |
| `WARN no CI run on … for this commit` | Usually a doc-only commit. Tell the operator, and continue when they agree. |
| `WARN … must share X.Y` | In a "both" run this is expected; it clears when the second repo is published. Otherwise, the other repo gets the same `X.Y` before the line goes stable. |
| `REFUSED: the next version is now …` | Someone tagged between the dry run and `--yes`. Show the new plan and confirm again. |
| The release run failed after the push | Follow the recovery that the script prints (RELEASING.md 2.3). |
| `FAIL release flags …`, `FAIL assets missing …` or `FAIL PyPI has no …` after the push | The version is published. Report the lines to the operator, and follow RELEASING.md 2.3. |
| `error: branch docs/release-… already exists on origin` | The meta PR for this release exists. Open it, or delete the stale branch. |
| `error: … is not checked out` | Run from the main `/workspaces` checkout. Worktrees have empty submodules. |
