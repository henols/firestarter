---
phase: 191-the-branch-that-reaches-users
verified: 2026-09-13T23:10:00Z
status: passed
score: 4/4 must-haves verified (roadmap success criteria); 1 advisory finding raised and resolved
covered_files:
  - .planning/REQUIREMENTS.md
  - .planning/phases/191-the-branch-that-reaches-users/191-01-PLAN.md
  - .planning/phases/191-the-branch-that-reaches-users/191-01-SUMMARY.md
  - .planning/phases/191-the-branch-that-reaches-users/191-02-PLAN.md
  - .planning/phases/191-the-branch-that-reaches-users/191-02-SUMMARY.md
  - .planning/phases/191-the-branch-that-reaches-users/191-03-PLAN.md
  - .planning/phases/191-the-branch-that-reaches-users/191-03-SUMMARY.md
  - .planning/phases/191-the-branch-that-reaches-users/191-04-PLAN.md
  - .planning/phases/191-the-branch-that-reaches-users/191-04-SUMMARY.md
  - .planning/phases/191-the-branch-that-reaches-users/191-05-PLAN.md
  - .planning/phases/191-the-branch-that-reaches-users/191-05-SUMMARY.md
  - .planning/phases/191-the-branch-that-reaches-users/191-CONTEXT.md
  - .planning/phases/191-the-branch-that-reaches-users/191-stable-install-fixture.sh
  - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-01-pypi.txt
  - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-01-release-run.txt
  - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-bench-leonardo.txt
  - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-fixture-baseline.txt
  - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-fixture-published.txt
  - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-disposition.md
  - .planning/phases/191-the-branch-that-reaches-users/evidence/191-url-02-merged-main.txt
  - .planning/phases/191-the-branch-that-reaches-users/evidence/191-url-02-prepared-branch.txt
  - .planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md
  - .planning/todos/pending/2026-09-13-release-yml-autocommit-vs-ruleset.md
covered_digest: "v1:sha256:9526d4ed793c1ff54ba6b5d7c9a98fbc404ab2cd814220d3d4a38f3ad242ce20"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Decide whether to amend the phase disposition record (evidence/191-stable-disposition.md, Criterion 4 item 3) and/or the backlog item .planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md to reflect a newly observed fact: publish.yml's `release: published` trigger DID fire during this phase (GitHub Actions run 34785081535, event=release, created 2026-09-13T21:51:55Z), contradicting the record's repeated claim that it 'has never fired in 8 of 8 recorded runs, ever.' It ran concurrently with the operator's manual `workflow_dispatch` (run 34785081751) and failed with a PyPI upload race (500 then 'File already exists' on the sdist, because the concurrent dispatch had already uploaded that file) — not because the trigger failed to fire."
    expected: "Either the disposition record and backlog item are corrected to describe the actual, now-observed failure mode (a race between an automatically-fired release-event run and a manually-dispatched run, rather than an eternally-suppressed trigger), or a human explicitly decides the original 8-of-8 framing is still the right characterization to leave on record and accepts the staleness."
    why_human: "This is a factual, in-session discovery (confirmed independently against the live GitHub Actions API by this verification pass) that the phase's own evidence never surfaced or reconciled, despite the phase being built entirely around the discipline of reading live state rather than trusting a prior measurement. It does not change whether PyPI 2.0.9 is published (verified independently, unaffected), so it is not a blocking defect — but leaving the record uncorrected misdescribes the pipeline's real behavior for whoever picks up the filed backlog item next, and only a human can decide whether/how to amend a completed phase's evidence record."
---

# Phase 191: The Branch That Reaches Users Verification Report

**Phase Goal:** The version a person gets from `pip install firestarter` addresses
`firestarter_fw`, and that claim is verified by installing it rather than by reading the diff.
**Verified:** 2026-09-13T23:10:00Z
**Status:** passed (human verification item resolved 2026-09-13 — see `191-UAT.md`)
**Re-fingerprinted:** 2026-09-13 — resolving the human-verification item edited two covered files
(`evidence/191-stable-disposition.md`, `todos/pending/2026-09-13-publish-yml-release-published-never-fires.md`),
so `covered_digest` was recomputed via `gsd-tools query verification.fingerprint` over the same
`covered_files` list. Prior digest: `v1:sha256:6db0e0c1…`. No verified finding changed — the edits
are the correction this report itself asked for.
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `origin/main` carries the repointed firmware-release constant(s), landed through a PR | ✓ VERIFIED | Live `gh api repos/henols/firestarter_app/pulls/66` → `merged: true`, `merge_commit_sha 1d526ea3...`. Live `ref=main` contents-API reads (re-run independently by this verifier, not copied from the transcript) confirm `constants.py` line 9 is `https://api.github.com/repos/henols/firestarter_fw/releases/latest`, `README.md:17` links `henols/firestarter_fw`, `__init__.py` reads `2.0.9`. Live-confirmed `constants.py` on `main` defines **no** other `FIRESTARTER_*_URL` name and `firmware.py:107` is its only consumer — D-01's "one constant, not three" reading is factually grounded, not a convenient redefinition (see narrowing discussion below). |
| 2 | A stable cut from `main` is published to PyPI; a clean install yields a version whose `FIRESTARTER_RELEASE_URL` names `firestarter_fw` | ✓ VERIFIED | Live `curl https://pypi.org/pypi/firestarter/json` (re-run independently by this verifier) → `info.version: 2.0.9`, both `firestarter-2.0.9-py3-none-any.whl` and `firestarter-2.0.9.tar.gz` present, homepage unchanged as expected. Live `gh api .../releases/tags/2.0.9` → `target_commitish` and tag-peel both equal the merge commit `1d526ea3...`, matching. Fixture pair: RED (`191-stable-02-fixture-baseline.txt`, 2.0.7, `subject_redirects: 1`, exit 1) vs GREEN (`191-stable-02-fixture-published.txt`, 2.0.9, `subject_redirects: 0`, exit 0) — same `control_redirects: 1` in both. `git log --follow` on the fixture script shows exactly one commit ever touched it, confirming the pair used a byte-identical script (not merely asserted). |
| 3 | 999.9's full validation (install → query → locate release → download asset → update-check) is run against that stable, version named | ✓ VERIFIED | Fixture (`191-stable-02-fixture-published.txt`) covers install/query/locate/download, exit 0 against `2.0.9`. Bench leg (`191-stable-02-bench-leonardo.txt`) covers the update-check leg on a live Leonardo at `/dev/ttyACM0`: the no-flag path could not complete a version handshake against the board's `3.0.0b22` (two consecutive attempts, transcript shows the real failure honestly rather than smoothing it over), so the named fallback `fw --install` was used to flash `2.0.6`; the **closing** no-flag, no-stdin invocation then performed a real, successful update-check — `Current firmware version: 2.0.6, for controller: leonardo` / `Firmware is already up to date` — which is a genuine, live exercise of the same `check_current_firmware`/`manage_firmware_update` code path 999.9 names, just landing on the "already up to date" branch rather than the predicted "downgrade offer" branch. The chain is closed; the specific D-09-predicted parse-warning scenario simply didn't get material to fire on, and the record says so plainly rather than claiming it occurred. |
| 4 | The phase record states plainly what this does NOT achieve (three things) | ✓ VERIFIED, with one advisory correction needed | `191-stable-disposition.md` names all three: stranded non-upgrading users; `origin/main` left with no regression guard (D-02); `main`'s stable release pipeline left broken in two places (D-05), linking both backlog items by filename. All three are present and evidenced. **However**, this verification pass discovered (via live GitHub Actions API) that the "publish.yml's `release: published` trigger has never fired in 8 of 8 runs, ever" claim reused verbatim in this record and in the backlog item is now stale: a 9th run (`34785081535`, `event: release`, `conclusion: failure`) fired during this very phase, when the operator created the GitHub release, racing with the manual `workflow_dispatch` (`34785081751`) and failing on a PyPI "file already exists" collision rather than on the previously-observed suppression. See `human_verification` above. |

**Score:** 4/4 ROADMAP success criteria substantively verified, live, independent of the phase's own transcripts. 0 present-but-behavior-unverified truths. 1 advisory/human-decision item (does not block any of the four criteria; see below).

### Criterion 1's narrowing (D-01), judged

URL-02's literal text reads "the same three constants." D-01 records that `origin/main` carries
only one (`FIRESTARTER_RELEASE_URL`) and settles the requirement as satisfied under that reading.
This verifier re-checked `origin/main` live rather than accepting the record: `constants.py` at
`ref=main` defines exactly one `FIRESTARTER_*_URL` name, and `firmware.py` at `ref=main` has
exactly one consumer of it (line 107) with no reference anywhere to `FIRESTARTER_RELEASES_URL` or
`FIRESTARTER_RELEASE_BY_TAG_URL`. This is not a criterion quietly redefined to fit what was
built — it is a discovery that the requirement's premise (three constants existing on `main`,
mirroring `beta`) was factually false, because `main` is 951 commits stale and predates the
click/channel refactor that introduced the other two names. The requirement's underlying intent —
no code path on `main` depends on GitHub's rename redirect — is fully met by repointing the one
constant that exists and is consumed. The narrowing is sound and transparently disclosed, not a
cop-out.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `191-stable-install-fixture.sh` | Board-free, re-runnable STABLE-02 fixture, ≥200 lines, `redirects==0` assertion | ✓ VERIFIED | 492 lines; single commit in its entire git history (`26401224`), confirming the red/green pair used a byte-identical script; strict mode, `--help`/bad-arg discipline, no `--pre`/`git clean`/bare `grep` present (re-grepped independently). |
| `evidence/191-stable-02-fixture-baseline.txt` | Fail-first pre-cut baseline (2.0.7, exit 1) | ✓ VERIFIED | Contains `control_redirects: 1`, `subject_redirects: 1`, no final verdict token, explicit "pre-cut fail-first baseline" annotation. |
| `evidence/191-stable-02-fixture-published.txt` | Green post-cut run (2.0.9, exit 0) | ✓ VERIFIED | `subject_redirects: 0`, `control_redirects: 1`, `STABLE INSTALL CONTRACT OK`. |
| `evidence/191-url-02-prepared-branch.txt`, `191-url-02-merged-main.txt` | Prepared-branch and post-merge readings | ✓ VERIFIED | Both cross-checked live against `gh api` in this pass; all counts and shas match. |
| `evidence/191-stable-01-release-run.txt` | Observed `release.yml` run, D-06 branch selected | ✓ VERIFIED | Live-rechecked: run `34784468070` failed at "Commit updated version" with `GH013`, `Release` step `skipped`, headSha exact match to merge commit — matches the transcript exactly. |
| `evidence/191-stable-01-pypi.txt` | Live PyPI verification + propagation-lag disclosure | ✓ VERIFIED | Live-rechecked: `info.version 2.0.9`, both files present, tag/release/merge-commit sha agreement all confirmed independently. |
| `evidence/191-stable-02-bench-leonardo.txt` | Real bench transcript, board left on 2.0.6 | ✓ VERIFIED | Honest, detailed transcript; controller-identity line present; no `.hex` residue claim consistent with `manage_firmware_update`'s own cleanup behavior. |
| `evidence/191-stable-disposition.md` | Phase disposition, 3 unachieved items + 4 boundary notes | ✓ VERIFIED, with the one advisory correction noted above | All required sections and citations present. |
| Two backlog items (`.planning/todos/pending/2026-09-13-*.md`) | Filed pipeline defects naming `beta-release.yml` | ✓ VERIFIED | Both exist, valid frontmatter, name `beta-release.yml`, cite ruleset `22046179` and the workflow_dispatch-only history (item 2's premise is now partially superseded by the same-session `release`-event run — see advisory item). |

### Key Link Verification

| From | To | Via | Status |
|------|----|----|--------|
| `firestarter_app` branch `v1.38-url-02-main` | `henols/firestarter_fw` releases API | `FIRESTARTER_RELEASE_URL` at `constants.py:9`, consumed by `firmware.py:107` | ✓ WIRED — confirmed live at `ref=main` |
| merged commit on `main` | published PyPI artefact `2.0.9` | operator tag + release + `publish.yml` dispatch | ✓ WIRED — three independent sha readings agree (tag peel, release `target_commitish`, PR merge commit) |
| `pip install firestarter` (clean venv) | `api.github.com/repos/henols/firestarter_fw/releases/latest`, zero redirects | unmodified fixture script, run twice (red then green) | ✓ WIRED — `git log` confirms one commit ever touched the script |
| published `2.0.9` install | Leonardo `/dev/ttyACM0` running `2.0.6` | `fw --install` fallback path (named contingency, taken because the no-flag handshake failed) | ✓ WIRED — closing reading confirms `2.0.6` / "already up to date" |

### Data-Flow Trace (Level 4)

Not separately applicable — this phase produces no rendered UI/dynamic data; its "data flow" is
the live API/PyPI/hardware chain traced above, and every terminus was independently re-queried by
this verifier against the live GitHub API and PyPI JSON API rather than accepted from the
transcripts.

### Behavioral Spot-Checks / Probe Execution

Not run as separate scripted probes beyond re-executing the same live API reads the phase itself
used (`gh api`, `curl https://pypi.org/pypi/firestarter/json`) — all reproduced independently in
this verification pass with matching results (see truths table above). No project-defined
`scripts/*/tests/probe-*.sh` apply to this phase.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| URL-02 | 191-02, 191-03 | `main` addresses `firestarter_fw` for the release endpoint | ✓ SATISFIED | Live `ref=main` reads; REQUIREMENTS.md row Complete |
| STABLE-01 | 191-03, 191-04 | Stable cut from `main` published to PyPI | ✓ SATISFIED | Live PyPI JSON read; REQUIREMENTS.md row Complete |
| STABLE-02 | 191-01, 191-04, 191-05 | Clean-environment validation run against that stable | ✓ SATISFIED | Fixture pair + bench leg; REQUIREMENTS.md row Complete |

No orphaned requirements: `.planning/REQUIREMENTS.md` maps exactly these three IDs to Phase 191,
and all three are declared across the five plans' `requirements:` frontmatter.

### Anti-Patterns Found

None. Swept the fixture script, all evidence `.txt`/`.md` files, and the two backlog items for
`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` — zero hits outside quoted historical strings
(none found). `.planning/config.json`'s `sub_repos` list is intact (4 entries); the
`firestarter_app` gitlink is unchanged on the milestone branch, as the phase requires.

### Human Verification Required

1. **Reconcile the disposition record / backlog item with the newly observed `release`-event run.**
   **Test:** Read `gh api repos/henols/firestarter_app/actions/runs/34785081535` and its job log
   (`gh run view 34785081535 -R henols/firestarter_app --log-failed`, with `XDG_CACHE_HOME` set).
   **Expected:** Confirm the run is `event: release`, `conclusion: failure`, created
   `2026-09-13T21:51:55Z` — the same second as the operator's manual `workflow_dispatch` run
   `34785081751` — and that its failure is a PyPI upload race ("File already exists" on the sdist)
   rather than the trigger failing to fire. Then decide whether `evidence/191-stable-disposition.md`
   (Criterion 4, item 3) and/or
   `.planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md` should be
   amended to describe this, or whether the existing "8 of 8, never fired" framing is accepted as
   a point-in-time measurement that a human is comfortable leaving as-is.
   **Why human:** This is a judgment call about amending a completed, committed phase record; it
   doesn't change any of the four ROADMAP success criteria (PyPI 2.0.9 is published and verified
   independently either way), so it is not a blocking defect, but it is a real, discoverable
   inaccuracy this verification pass surfaced by holding the phase to its own stated standard
   ("verify live, don't trust a prior measurement").

### Gaps Summary

No ROADMAP success criterion failed. All four are independently, live-verified — not merely
accepted from the phase's own transcripts. The one open item is a factual-accuracy correction to
the phase's disposition record / backlog item, discovered by this verification pass via a live
GitHub Actions API read the phase itself did not perform for this specific workflow run. It does
not reopen or invalidate URL-02, STABLE-01, or STABLE-02, all of which are marked Complete in
`REQUIREMENTS.md` correctly.

---

*Verified: 2026-09-13T23:10:00Z*
*Verifier: Claude (gsd-verifier)*
