# Releasing Firestarter

How a stable release is cut. Written for the operator, and for whoever has to do it when the
operator is not available.

**The stable channel has been frozen since 2025-11** at firmware `2.0.6` and CLI `2.0.9`. All work
lives on `beta`. Promoting `beta` to `main` is not a merge — it is the first stable 3.x release, and
it is a one-way door for every user in the field.

Read all of §1 before touching anything. Two of the three publish paths are broken today, and the
firmware one fails in a way that looks like success.

---

## 1. What is broken right now

### 1.1 The automated version bump cannot push to `main`

All three repositories carry an identical active `Protect main` ruleset:

| | |
|---|---|
| Scope | `~DEFAULT_BRANCH` — `main` only. Tags and `beta` are untouched. |
| Rules | `deletion`, `non_fast_forward`, `pull_request` |
| Bypass actors | exactly one: `DeployKey`, mode `always`. **GitHub Actions is not one.** |
| `current_user_can_bypass` | `never` — the owner cannot push to `main` directly either |

`release.yml` (app) and `build.yml` (firmware) both run
`stefanzweifel/git-auto-commit-action@v5` with the default `GITHUB_TOKEN`, pushing straight to
`main`. The ruleset rejects it.

**This is observed, not predicted.** `firestarter_app` run
[`34784468070`](https://github.com/henols/firestarter_app/actions/runs/34784468070), a push to
`main`:

```
✓ Create new patch release
X Commit updated version      ← GH013: Changes must be made through a pull request
- Release                     ← skipped
```

`2.0.9` was cut **by hand**: its release author is the user `henols`, created `2026-09-13T21:51:50Z`,
twelve minutes after that run failed.

### 1.2 The firmware publish path fails closed — for now

A push to `main` in `firestarter_fw` today publishes **nothing**. The auto-commit is step 2 of the
job; `pio run`, the no-dev-tools assertion and the `Release` step (which carries `make_latest: true`)
are steps 3, 4 and 5. Step 2 aborts the job before any of them run.

> **This inverts the old warning.** Older notes and `CLAUDE.md` revisions say *"any push to `main`
> cuts a stable release — there is no dry run."* That was true before 2026-09-01 and is false now.
> The hazard has changed shape, not disappeared: it **re-arms the instant the bump is unblocked**.
> Whoever fixes §1.1 must re-read this section the same day.

### 1.3 The stable PyPI upload does not cascade

`release.yml` has no `pypi:` job. It relies on `publish.yml`'s `release: [published]` trigger, which
**is not delivered for releases created by a bot**. The record:

| tag | release created by | `publish.yml` fired | reached PyPI |
|---|---|---|---|
| 2.0.7 | `henols` (User) | yes | yes |
| 2.0.8 | `github-actions[bot]` | **never** | **no** |
| 2.0.9 | `henols` (User) | yes, then failed on a duplicate | yes, via a hand dispatch |

`2.0.8` exists on GitHub and never reached PyPI, silently.

`beta-release.yml` already solves this on the beta side with a `pypi:` job that calls `publish.yml`
by `workflow_call`. `release.yml` is **byte-identical on `main` and `beta`**, so promoting does not
bring that fix with it.

### 1.4 `3.1.0` cannot be produced by the automation

`update_version.py` on `main` takes the stable path, discards the pre-release suffix and emits
`major.minor.(patch+1)`. From `3.1.0b2` that is **`3.1.1`**. `--set-version` cannot express a stable
version either: it forces beta mode and validates against a regex demanding a `b` or `rc` suffix.

**Decide before Phase 1: ship `3.1.1`, or hand-cut `3.1.0`.** `3.1.1` is recommended — it is what the
automation produces, it costs nothing, and "the first stable is 3.1.1" is one line in the CHANGELOG.

### 1.5 Options for unblocking the bump

Not chosen here. Record the choice in this file when it is made.

| | Approach | Assessment |
|---|---|---|
| **O-1** | **Hand-cut with the publishing workflows disabled.** Version bumped inside the promotion PR; tag, release and PyPI dispatch by hand. | **Recommended for the first cut.** The only option with evidence behind it — it is how `2.0.9` was cut. The runbook in §2 assumes it. |
| O-2 | Deploy-key bypass. The `DeployKey` slot is already in `bypass_actors`; add a write deploy key and give `actions/checkout` an `ssh-key:`. | Works without touching the ruleset. **Trap:** a deploy-key push is not a `GITHUB_TOKEN` push, so it re-triggers workflows — an infinite bump loop. Needs `[skip ci]` in the commit message, rehearsed first. Long-lived write credential. |
| O-3 | Add GitHub Actions as a bypass actor (`actor_type: "Integration"`). | Keeps the no-retrigger property, so no loop. **Unproven** — rehearse on a throwaway repository before trusting it. |
| O-4 | Bump by pull request instead of pushing. | Correct long-term. Adds a second merge to `main` that re-fires the workflow. Workflow rewrite. |
| O-5 | Stop bumping on `main`; the promotion PR carries the final version and the workflows read it. | Cleanest. Needs the `--set-version` gate in §1.4 fixed first. |

---

## 2. The promotion runbook

### Phase 0 — preconditions

None of these publish anything. All must be true before Phase 1.

- [ ] **P0-1.** The version number is decided and written into §1.4 of this file.
- [ ] **P0-2.** The `Known-Issues` wiki page is live and covers the open chip failures.
- [ ] **P0-3.** `firestarter_app/CHANGELOG.md` exists and the release's section is written.
- [ ] **P0-4.** The stable-install wiki page (`Install`) is live.
- [ ] **P0-5.** `VALIDATED-EPROMS.md` records that its rows are 3.0.x evidence.
- [ ] **P0-6.** The milestone is closed on `beta` and the newest `3.1.0bN` pre-release is green.
- [ ] **P0-7.** You have read §3. Publishing the stable firmware is the irreversible step.

### Phase 1 — the app, first

The app must reach PyPI before the firmware release flips `/releases/latest`, so that
`pip install --upgrade firestarter` already resolves to a CLI that can drive the new firmware.

1. `gh workflow disable release.yml --repo henols/firestarter_app`. Confirm with
   `gh workflow list --all`. Leave `ci.yml` enabled throughout.
2. Branch `release/3.1.x` from `main`; `git merge origin/beta`. Expect conflicts in `README.md`,
   `images/` and `firestarter/__init__.py`. **This is not a fast-forward** — `main` carries commits
   `beta` does not.
3. Set `firestarter/__init__.py` to the decided version by hand. Move `CHANGELOG.md`'s
   `## [Unreleased]` heading to the released version.
4. Open the PR.
   > **Blocking point.** `require_extra_approval_for_unattributed_changes` is `true` while
   > `required_approving_review_count` is `0`. A PR carrying commits not attributable to a GitHub
   > account therefore needs one approval. Over ~1140 commits that is a real risk. Check with
   > `gh pr view <n> --json mergeStateStatus,reviewDecision` **before** you need it, not after.
5. Merge with a **merge commit**. Never squash — a squash collapses the whole history that
   `git tag` scanning and `git log` both read.
6. Confirm `ci.yml` is green on `main`.
7. `git tag -a <version> -m <version> && git push origin <version>`. **Not blocked** — the ruleset
   scopes to `~DEFAULT_BRANCH`, not tags.
8. `gh release create <version> --latest --notes-file <notes>`.
   > **Create it as yourself, not via a bot.** §1.3 — a bot-created release does not cascade to
   > PyPI, and it fails silently.
9. **Do not also dispatch `publish.yml` by hand.** For `2.0.9` two runs started in the same second
   and the automatic one died on a PyPI duplicate. Wait for the release-event run. Dispatch by hand
   only if it never appears.
10. Verify: `pip download firestarter==<version> --no-deps` in a clean virtualenv.

### Phase 2 — the firmware, second

1. Branch `release/3.1.x` from `main`, merge `origin/beta`, resolve `README.md`, `images/` and
   `include/version.h`. Set the version by hand.
2. **Open the PR with `build.yml` still enabled.** `pull_request` carries no branch filter, so the
   workflow runs in full and gives you the compile plus the *"no AVR image gained the dev
   commands"* assertion — with no publish step anywhere in a PR run. This is the only dry run
   available. Use it.
3. Only once that run is green: `gh workflow disable build.yml --repo henols/firestarter_fw`, then
   merge.
4. > **Blocking point: nothing builds the release assets.** `build.yml` has no `workflow_dispatch`
   > trigger and no `upload-artifact` step, so the `.hex` files exist only as release assets. Build
   > them locally from the exact merge SHA, **without** `DEV_TOOLS`, and re-run the dev-tools
   > assertion by hand before attaching them.
5. Decide whether `firestarter_py32f071.hex` ships. `channel.BETA_ONLY_BOARDS` contains
   `py32f071`, so a stable CLI will never offer it — attaching it ships an asset nothing installs.
6. Tag, then `gh release create <version> --latest` with the `.hex` files attached.
   > **This is the irreversible step.** `/releases/latest` flips from `2.0.6`, and every
   > un-upgraded 2.0.x CLI in the field starts resolving the new firmware. Read §3 first.
7. Verify: `gh api repos/henols/firestarter_fw/releases/latest --jq .tag_name`.

### Phase 3 — the meta repository, last

1. Branch from `main`, merge `origin/beta`, resolve `.gitmodules`, `README.md` and `images/`.
   Advance both gitlinks to the sub-repositories' new `main` commits.
2. Open the PR, merge it.
3. **Push a bare tag only. Never publish a GitHub Release from the meta repository.**
   > A tag like `v1.42` parses as PEP 440 `1.42`. `Version("3.1.1") >= Version("1.42")` is **true**,
   > so any CLI that resolves firmware from the meta repository would report firmware up to date
   > forever, silently and permanently.

### Phase 4 — re-enable

1. `gh workflow enable release.yml` and `build.yml`.
   > From this moment every subsequent merge to `main` re-fires the blocked auto-commit. Nothing
   > publishes, but every merge leaves a red run until one of §1.5's options lands.
2. Apply the post-publication wiki edits: the `Breaking-Changes` preamble gains stable/pre-release
   marks, and the top entry is retitled with the stable version.

### Phase 5 — post-release checks

- A clean virtualenv: `pip install firestarter`, then `firestarter --version` prints the stable
  number with **no** `b` suffix.
- On a real board: `firestarter fw -i` resolves and flashes the new firmware, and `firestarter fw`
  then reports the matching version.

---

## 3. What happens to users still on 2.0.x

**Read this before Phase 2 step 6.**

The published `2.0.9` wheel hard-codes its firmware endpoint:

```
https://api.github.com/repos/henols/firestarter_fw/releases/latest
```

That endpoint excludes pre-releases, so it has been returning the matched `2.0.6` for the whole 3.x
beta programme. **The first stable 3.x firmware release flips it.** From that moment a 2.0.9 CLI
resolves 3.x firmware, and `_compare_versions` in that wheel reads `(2,0,6) >= (3,1,1)` as false —
so the old CLI does not merely permit the flash, it **recommends** it.

There is no host-side fix for this. A `2.0.10` guard release would reach almost nobody:
`pip install --upgrade firestarter` resolves to the newest stable, so once a stable 3.x is on PyPI
every upgrading user lands there directly, and a user who never upgrades never receives `2.0.10`
either.

What limits the damage is already in the firmware. Retired ordinals 4 (blank check) and 6 (verify)
fall through the dispatch `default:` arm and answer `MSG_ERR_UNKNOWN_CMD`, so a 2.0.9 host's verify
and standalone blank check **fail loudly**. The residual quiet gap is narrower and specific: the
retired `0x08` flag is ignored rather than refused, and blank-checking before a write moved to the
host in 3.1.0 — so a 2.0.x host that expected the firmware to blank-check gets no blank check from
either side.

Mitigation is documentation, and it must be in place before Phase 2:

- The `Install` wiki page leads with **upgrade the CLI first**, with the commands in order.
- The firmware release notes say the same thing in their first line.
- `Breaking-Changes` states which mixed pairings work.

---

## 4. Beta releases

Unchanged, and much simpler — but note that **a push to `beta` publishes**, in both
sub-repositories, with no path filter in either. A documentation-only push cuts a new pre-release
and uploads a new PyPI version. This is deliberate: the firmware compiles its version into the
binary, so a skipped bump would ship firmware that misreports itself.

**A PyPI version can never be reused.** Decide the scope of a beta push before making it.
