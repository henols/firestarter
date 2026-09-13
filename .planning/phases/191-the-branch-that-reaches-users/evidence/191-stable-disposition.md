# Phase 191 disposition record

The version a person gets from `pip install firestarter` addresses `henols/firestarter_fw`, and
that claim is verified below by installing the published artefact rather than by reading the
diff. This record is the phase's answer to the ROADMAP's four success criteria, one section
each, every claim citing the evidence file and reading that supports it.

## Criterion 1 — `origin/main` carries the repointed constant(s), landed through a pull request

**URL-02's explicit reading (D-01), stated plainly:** `origin/main` carries **one** firmware-release
constant, `FIRESTARTER_RELEASE_URL` (`firestarter/constants.py:9`), whose only consumer is
`firestarter/firmware.py:107`. That one constant is repointed. The two `beta`-only names
(`FIRESTARTER_RELEASES_URL`, `FIRESTARTER_RELEASE_BY_TAG_URL`) were **deliberately not backported** —
no code on `main` imports them, and adding them would ship dead module-level surface to every
default install. **URL-02 is satisfied under this reading. It is NOT marked partial, and the
requirement text is not rewritten.**

- **Pull request:** `henols/firestarter_app#66`, base `main`, head `v1.38-url-02-main`, 3 files
  changed / 3 additions / 3 deletions.
- **Merged:** `merged: true`, `merge_commit_sha: 1d526ea30f0a00c23ad8198b4679ee9459f31a88`
  (`.../pulls/66` read live) — evidence/`191-url-02-merged-main.txt`.
- **Three `ref=main` contents-API readings**, all taken live after the merge, all recorded in
  evidence/`191-url-02-merged-main.txt`:
  - `firestarter/constants.py@main`: repointed endpoint (`.../repos/henols/firestarter_fw/releases/latest`)
    count 1; boundary-aware bare-slug sweep (`henols/firestarter([^_a-zA-Z0-9]|$)`) count 0.
  - `README.md@main`: repointed firmware link count 1; bare-slug sweep count 0; non-vacuity
    positive control (`henols/firestarter_app`) count 4 — proving the zeros above are a real
    absence, not an empty API response.
  - `firestarter/__init__.py@main`: reads `__version__ = "2.0.9"` — the value the PR carried
    directly, confirmed (Criterion 2 below) to be the value that reached PyPI, not a bot-bumped
    `2.0.10`.

## Criterion 2 — a stable cut from `main` is published to PyPI and a clean environment yields it

**Version: `2.0.9`.**

- **Tag:** `2.0.9`, peels (refs API → tag object → commits API) to
  `1d526ea30f0a00c23ad8198b4679ee9459f31a88` — the same sha as the PR merge commit above.
- **GitHub release:** `https://github.com/henols/firestarter_app/releases/tag/2.0.9`,
  `target_commitish: 1d526ea30f0a00c23ad8198b4679ee9459f31a88`, `draft: false`,
  `published_at: 2026-09-13T21:51:53Z` — evidence/`191-stable-01-pypi.txt`.
- **`publish.yml` run:** `https://github.com/henols/firestarter_app/actions/runs/34785081751`,
  `workflow_dispatch`, `status: completed` / `conclusion: success`, every step (including
  "Publish package") green — recorded as **context**, not as the verification, per the plan's
  own repudiation mitigation (T-191-04-02): a green publish-run tick has been trusted before,
  and that omission is exactly how GitHub release `2.0.8` ended up existing while PyPI stopped
  at `2.0.7`.
- **Live PyPI reading**, independent of the operator's report and of the run's own conclusion,
  captured `2026-09-13T21:54:10Z`: `https://pypi.org/pypi/firestarter/json` → `info.version:
  2.0.9`, both `firestarter-2.0.9-py3-none-any.whl` and `firestarter-2.0.9.tar.gz` present —
  evidence/`191-stable-01-pypi.txt`.
- **The pipeline observation next to the prediction it tested (D-06):** the merge's own
  `release.yml` run, `https://github.com/henols/firestarter_app/actions/runs/34784468070`
  (`headSha` exact-matched to the merge commit), failed at the `git-auto-commit-action@v5` push
  step ("Commit updated version") with `GH013: … Changes must be made through a pull request`;
  the `Release` step shows `conclusion: skipped`. **D-06 Branch A was taken** — the operator
  hand-cut the tag and release, and dispatched `publish.yml` manually — exactly as D-04
  predicted before the merge, converting a plausible guess into a checked measurement.
  Evidence/`191-stable-01-release-run.txt`.
- **GitHub release `2.0.8` remains orphaned** — cut 2026-08-07, never published to PyPI (PyPI's
  latest stable was `2.0.7` before this phase). This phase **deliberately neither cleans it up
  nor back-publishes it**; `2.0.9` supersedes it for `pip install` purposes.

## Criterion 3 — 999.9's full validation run against that stable, with the version named

**Version run against: `2.0.9`, exclusively — never a `3.0.0bNN` prerelease.**

999.9's chain — install → query → locate release → download asset → update-check — is split
across its two instruments:

- **The fixture** (`191-stable-install-fixture.sh`, unmodified since 191-01) covers install,
  query, locate release, and download asset — board-free. Re-run against `2.0.9` in
  evidence/`191-stable-02-fixture-published.txt`: exit 0, `installed_version: 2.0.9`,
  `installed_release_url: https://api.github.com/repos/henols/firestarter_fw/releases/latest`,
  `pypi_latest_stable: 2.0.9`.
- **The bench leg** (this plan) covers the update-check on a real Leonardo, on
  `/dev/ttyACM0`, from a separate clean install of `2.0.9`. Evidence/`191-stable-02-bench-leonardo.txt`:
  the closing reading shows `Current firmware version: 2.0.6, for controller: leonardo on port
  /dev/ttyACM0` / `Firmware is already up to date` — the board flashed and left on `2.0.6`.

**The red/green pair is the argument, and a bare successful resolve would have proved nothing:**
`api.github.com/repos/henols/firestarter/releases/latest` and
`.../repos/henols/firestarter_fw/releases/latest` return **byte-identical bodies** — the only
observable that separates them is the redirect count. Run against the identical, unmodified
script:

| Run | Version installed | `control_redirects` | `subject_redirects` | Exit |
|---|---|---|---|---|
| RED (`191-stable-02-fixture-baseline.txt`, 191-01) | `2.0.7` | 1 | **1** | 1 |
| GREEN (`191-stable-02-fixture-published.txt`, 191-04) | `2.0.9` | 1 | **0** | 0 |

Both runs read `control_redirects: 1` identically — the probe can see a redirect when one
exists in both cases — and only `subject_redirects` moves, from `1` to `0`, when the installed
package's own `FIRESTARTER_RELEASE_URL` is repointed. A green resolve alone (a version string, an
exit code, an asset URL) is compatible with the pre-change state exactly as much as the
post-change one; only the redirect count separates them, which is why `redirects == 0` — not a
successful HTTP round-trip — is what this criterion actually rests on.

## Criterion 4 — what this does NOT achieve. Three things, named, not one

1. **Users who never upgrade remain unreachable, and the eventual claim of the unqualified slug
   will break `fw` for them.** No sequencing in this phase or the next changes that. What bounds
   the damage is the blast radius: the endpoint constant is consumed only by `firmware.py`, so
   only the `fw` subcommand breaks when the bare `henols/firestarter` slug is eventually
   claimed — read, write, verify, erase, blank-check and `dev test` are all untouched, on both
   `main` and `beta`.

2. **`origin/main` is left with no regression guard** (D-02). It has no `tests/` directory, no
   `[test]` extra in `pyproject.toml`, and no `ci.yml` — a pin test asserting the repointed
   constant stays repointed would have nowhere to live and nothing to run it. Phase 192 sweeps
   the **milestone branch**, not `origin/main` as a live ref beyond the boundary-check named in
   D-10 below, so nothing in this milestone actually watches `origin/main` for regression on an
   ongoing basis. D-10 closes the gap by **assignment** (this phase owns the references, Phase
   192 only re-verifies the ref once), not by tooling — a weaker instrument than a test, and
   this record says so rather than letting a verifier assume a guard exists where none does.

3. **`main`'s stable release pipeline is left broken in two places** (D-05), so the *next* stable
   cut will need exactly the same manual handling this phase performed. Both defects are filed,
   not fixed, each naming `beta-release.yml`'s `pypi` job as the proven, unported fix:
   - `.planning/todos/pending/2026-09-13-release-yml-autocommit-vs-ruleset.md` — `release.yml`'s
     `git-auto-commit-action@v5` push to `main` is rejected by ruleset `22046179` ("Protect
     main"), whose only bypass actor is `DeployKey`.
   - `.planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md` —
     `publish.yml`'s `release: published` trigger has never fired in 8 of 8 recorded runs (all
     `workflow_dispatch`), with GitHub release `2.0.8` already orphaned unpublished on PyPI as
     the on-disk consequence.

## Three shorter records a later reader would otherwise misread

- **The stated `Bench: none` deviation.** The v1.38 activation text says "Bench: none. No phase
  needs a board." That no longer holds for Phase 191: the operator directed D-09's bench leg on
  the Leonardo attached at `/dev/ttyACM0`. This is stated here plainly as a deliberate,
  operator-directed deviation from the activation text — not scope creep introduced by a plan or
  an executor.

- **The 191/192 boundary (D-10).** Phase 191 owns `origin/main`'s slug references outright (both
  edits above); Phase 192 re-verifies `origin/main` as a git ref and does not edit it. This
  matters beyond tidiness: SWEEP-01 names "both sub-repo READMEs", but Phase 192 sweeps the
  **milestone branch**, where `origin/main`'s `README.md` is invisible. Without this stated
  boundary, SWEEP-01's line would fall through both phases unnoticed.

- **The fixture's deliberate control slug.** `191-stable-install-fixture.sh` contains the
  unqualified firmware slug (`https://api.github.com/repos/henols/firestarter/releases/latest`)
  as its positive control's URL, **on purpose** — a zero-redirect reading on the subject is only
  meaningful next to a reading that does redirect. Phase 192's sweep must read this control line
  as intentional, exactly as Phase 190's fixture line 8 and Phase 189's fixture line 204 already
  carry the same property.

- **The gitlink.** No commit in this phase lands on `firestarter_app`'s milestone branch — the
  `main`-targeted commit (`186a1524f13a4df6e4d9ac5a4c1b3e7177a7ee79`) lives on the scratch branch
  `v1.38-url-02-main`, forked from `origin/main`, not from the milestone branch. So the meta
  repository's `firestarter_app` gitlink is **deliberately not advanced** by this phase, despite
  the per-phase gitlink-advance norm in force since v1.36 — that norm applies to commits landing
  on the milestone branch, and none did here.

## A measured `main`-branch defect worth recording here, not filed separately

`main`'s `_compare_versions` (`firestarter/firmware.py:132-146`) splits a version string on `.`
and calls `int()` on each part. A firmware string like `3.0.0b22` raises `ValueError` on
`int("0b22")`, is caught, logs `"Could not parse version strings for comparison"`, and returns
`False` — so the stable CLI treats every beta-flashed board as out of date and offers a
downgrade. This was predicted in `191-CONTEXT.md` (D-09) and recorded as an observation in
191-02's SUMMARY rather than filed as a third backlog item (Claude's Discretion, per the plan).
This bench leg could not directly reproduce the parse warning itself: the no-flag path
(`firestarter fw -b leonardo -p /dev/ttyACM0`, answered `y`) failed to complete a version
handshake against the board's actual firmware at all — `Could not determine current firmware
version` — on two consecutive attempts, so no current-version string was ever available for
`_compare_versions` to receive. The named fallback (`fw --install`) was used instead, which
takes the no-current-version arm and never calls `_compare_versions`. The defect stands as
measured in 191-02 and is not contradicted by this leg; this leg simply did not exercise the
code path that raises it, because the handshake never produced two version strings to compare.

## Summary table

| Criterion | Version / artefact | Evidence |
|---|---|---|
| 1 — `main` carries the repointed constant, via PR | PR `henols/firestarter_app#66`, merge `1d526ea3` | `191-url-02-merged-main.txt` |
| 2 — stable cut published to PyPI | `2.0.9` | `191-stable-01-pypi.txt`, `191-stable-01-release-run.txt` |
| 3 — 999.9 validated against that stable | `2.0.9` (fixture + bench) | `191-stable-02-fixture-published.txt`, `191-stable-02-bench-leonardo.txt` |
| 4 — three unachieved items named | stranded users; no `main` regression guard (D-02); pipeline broken in two places (D-05) | this record, both backlog items |
