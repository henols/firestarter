# API Coverage — Phase 191: The Branch That Reaches Users

The deterministic detector returned `detected: false` (no signals) at plan time, run over the
ROADMAP phase section. This matrix is recorded anyway, for two reasons: the seal-time re-detection
(`api-coverage.verify-pre`) runs over the plan bodies, which necessarily contain `api`, `endpoint`
and `consume`; and — as in Phase 190 — this phase genuinely does **consume** external APIs, so a bare
"no external API integration" declaration would be false.

**Three external surfaces are touched, and none gains a new capability here:**

1. **The GitHub Releases REST API**, consumed by `firestarter_app` through
   `firestarter/firmware.py`. This phase repoints the single endpoint constant that `origin/main`
   carries (`FIRESTARTER_RELEASE_URL`) from the unqualified slug to `henols/firestarter_fw`. It adds
   nothing. Phase 190 already recorded the full matrix for this surface on `beta`; the entries below
   are the `origin/main` subset, re-decided from the same full-coverage baseline rather than carried
   over — `main` is a different codebase (argparse, 2.0.x, 951 commits behind) and the checkpoint's
   own rule says a second integration against the same need re-decides each capability.
2. **The GitHub REST API via `gh`**, used read-only by the agent as verification evidence (contents
   at `ref=main`, pull requests, workflow runs, releases). No capability surface is being built
   against it; every write to GitHub in this phase is an operator act performed in the GitHub UI or
   CLI by a human, behind a `blocking-human` checkpoint.
3. **The PyPI JSON API**, read-only, used to verify the published artefact and its provenance.

`INTEGRATE` is the default. Every `OPT-OUT` carries a one-line reason.

## GitHub Releases API — as consumed by `origin/main`'s `firmware.py`

| capability | decision | reason |
|---|---|---|
| `GET /repos/{owner}/{repo}/releases/latest` | INTEGRATE | `FIRESTARTER_RELEASE_URL`; the only release endpoint on `origin/main`, and its only consumer is `firmware.py:107`. Repointed by URL-02. |
| Release asset download (`browser_download_url`) | INTEGRATE | `_download_firmware_file`; exercised live by the fixture and again by the bench leg. |
| Redirect transparency (`response.history`) | INTEGRATE | The single observable that distinguishes "addresses `firestarter_fw`" from "followed a 301"; the substance of D-07 and the fixture's central assertion. |
| `GET /repos/{owner}/{repo}/releases` (list, paginated) | OPT-OUT | `FIRESTARTER_RELEASES_URL` does not exist on `origin/main` — it is `beta`-only surface added after `main` diverged. D-01 explicitly declines to backport it: no code on `main` imports it, so it would be dead module-level surface shipped to every default install. |
| `GET /repos/{owner}/{repo}/releases/tags/{tag}` | OPT-OUT | `FIRESTARTER_RELEASE_BY_TAG_URL` does not exist on `origin/main`. Same reason as above; there is no `--firmware-version` pinned channel on `main`. |
| `GET /repos/{owner}/{repo}/releases/{release_id}` | OPT-OUT | The app never holds a numeric release id; the one lookup it makes is by channel. |
| `GET /repos/{owner}/{repo}/releases/{id}/assets` | OPT-OUT | Assets are already embedded in the release payload; a second round trip would add nothing. |
| Create / update / delete a release | OPT-OUT | The host CLI is a read-only consumer of the firmware repository's releases. |
| Upload / update / delete a release asset | OPT-OUT | Same — write operations against the firmware repository are outside the CLI's remit. |
| Generate release notes | OPT-OUT | `main`'s `fw` renders a version and an asset URL; release prose is consumed nowhere. |
| Release reactions | OPT-OUT | No use case; the CLI has no social surface. |
| Authenticated requests (token, higher rate limit) | OPT-OUT | The repository is public and the API is used unauthenticated by design. Introducing a token would create a secret where none exists. |
| Conditional requests / ETag caching | OPT-OUT | `fw` is an occasional interactive command; caching would introduce staleness into the one check whose job is to be fresh. |
| Rate-limit headers (`X-RateLimit-*`) | OPT-OUT | Not read today. Rate-limit rejections surface through the existing `RequestException` arm. |
| Asset provenance verification (signature / checksum) | OPT-OUT | Pre-existing gap, recorded as accepted in 190-04's threat model and again in this phase's `191-01` and `191-05` threat models. The Releases API exposes no signature for these assets, and adding one is a firmware-release-process change, not a host change. |
| GraphQL release queries | OPT-OUT | `requests` against REST is the incumbent; a second client for the same data is unjustified. |

## GitHub REST API via `gh` — agent verification reads only

| capability | decision | reason |
|---|---|---|
| `GET /repos/{owner}/{repo}/contents/{path}?ref=` | INTEGRATE | The 189-04 pattern: the merged state of a protected branch is read back from the API at the target ref, never from the local clone. |
| `GET /repos/{owner}/{repo}/pulls/{n}` | INTEGRATE | Reads `merged` and `merge_commit_sha` from the API rather than from the operator's report. |
| Workflow run listing / inspection | INTEGRATE | D-06's live branch decision reads the `release.yml` run conclusion rather than assuming D-04 was right. |
| `GET /repos/{owner}/{repo}/releases/latest` (app repo) | INTEGRATE | Used only in D-06's unexpected-success branch, to read back which version the bot actually cut. |
| Creating a pull request / merging | OPT-OUT | Operator act under D-7; `main` is protected with `current_user_can_bypass: never`. The agent never performs it. |
| Creating a tag / creating a release | OPT-OUT | Operator act under D-7 and D-04. |
| Dispatching a workflow | OPT-OUT | Operator act under D-7 and D-05. |
| Editing rulesets or branch protection | OPT-OUT | Explicitly out of scope — D-04 declines to change the ruleset inside a rename milestone; the collision is filed as a backlog item instead. |
| Editing `.github/workflows/` | OPT-OUT | D-05: both pipeline defects are filed, not fixed. `beta-release.yml` is read for the pattern and never ported. |

## PyPI JSON API — read-only verification

| capability | decision | reason |
|---|---|---|
| `GET /pypi/{project}/json` → `info.version` | INTEGRATE | The independent verification that the publish actually reached the index — the exact check whose absence let `2.0.8` exist on GitHub and not on PyPI. |
| `GET /pypi/{project}/json` → `info.project_urls` | INTEGRATE | The package-legitimacy provenance reading for the one package this phase installs. |
| `GET /pypi/{project}/json` → release file list | INTEGRATE | Recorded alongside the version so the artefacts are named, not just the number. |
| Upload / yank / delete a distribution | OPT-OUT | Performed by `publish.yml` with the repository's token, dispatched by the operator. Nothing uploads from this container. |
| `GET /pypi/{project}/{version}/json` (per-version) | OPT-OUT | The latest-stable reading answers the question; a per-version read adds nothing this phase needs. |
| Download-statistics APIs (BigQuery / pypistats) | OPT-OUT | That is GATE-01's adoption instrument, and it belongs to Phase 193 — it has nothing to measure until this phase publishes. |
