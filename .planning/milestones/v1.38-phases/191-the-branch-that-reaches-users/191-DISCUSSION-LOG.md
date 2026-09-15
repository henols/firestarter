# Phase 191: The Branch That Reaches Users - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-13
**Phase:** 191-the-branch-that-reaches-users
**Areas discussed:** URL-02 on a one-constant branch, The automatic cut + broken publish, STABLE-02's instrument, main's README firmware link

---

## URL-02 on a one-constant branch

### Q1 — How to satisfy URL-02's "same three constants"?

| Option | Description | Selected |
|--------|-------------|----------|
| Repoint the one that exists | Change `constants.py:9` only; URL-02's intent is fully met with one constant and one consumer (`firmware.py:107`) | ✓ |
| Backport all three constant names | Satisfy URL-02's literal text; costs two module-level names no code on `main` imports | |
| Repoint one + amend URL-02's text | Change the requirement to match the branch it describes | |

**User's choice:** Repoint the one that exists.
**Notes:** Measured first — `origin/main` carries only `FIRESTARTER_RELEASE_URL`; the other two are `beta`-only surface added after `main` diverged 951 commits ago.

### Q2 — Nothing guards `main`'s constant against regression

| Option | Description | Selected |
|--------|-------------|----------|
| State the gap, add no guard | Consistent with 189 D-10 and 190 D-05; source-scanning gates here fail OPEN after renames | ✓ |
| Extend Phase 192's sweep to `origin/main` | A `git grep` over a ref, no test infra needed | |
| Bootstrap minimal `tests/` + `ci.yml` on `main` | A real pin test and a workflow to run it | |

**User's choice:** State the gap, add no guard.
**Notes:** `origin/main` has no `tests/` directory at all, no `[test]` extra, no `ci.yml` — a pin test would have nowhere to live. D-10 later closed most of the gap by assignment instead.

### Q3 — What does the main-bound PR contain?

| Option | Description | Selected |
|--------|-------------|----------|
| `constants.py` + `README.md` link | One PR, one review, one cut; README is in `release.yml`'s `paths-ignore` so it does not change whether the cut fires | ✓ |
| `constants.py` alone | Unambiguous criterion-1 evidence; needs a second protected-branch PR for the README | |
| `constants.py` + README + workflow fixes | Fold the pipeline repair in too | |

**User's choice:** `constants.py` + `README.md` link.
**Notes:** A boundary-aware sweep confirmed these are the *only* two bare-slug references on `origin/main`. The PR later grew a third file (`__init__.py`) as a consequence of D-04, not of this choice.

---

## The automatic cut + broken publish

### Q1 — `release.yml`'s auto-commit will be rejected by the ruleset

| Option | Description | Selected |
|--------|-------------|----------|
| Predict it, let it fail, hand-cut | Record the prediction, carry `__version__ = 2.0.9` in the PR, operator hand-cuts tag+release; file the collision as backlog | ✓ |
| Redesign `release.yml` to not push | Permanent fix; a real change to the stable release flow inside a rename milestone | |
| Change the ruleset to unblock the bot | Add a bypass actor; weakens the protection criterion 1 leans on | |

**User's choice:** Predict it, let it fail, hand-cut.
**Notes:** Research + measurement both fed this. GitHub docs and community guidance: `GITHUB_TOKEN` cannot bypass a `pull_request` ruleset. Locally: the auto-commit step's PAT env is commented out, the only bypass actor is `DeployKey`, `current_user_can_bypass` is `never`, and the ruleset postdates `release.yml`'s last successful run by 25 days.

### Q2 — `publish.yml`'s `release: published` trigger has never fired

| Option | Description | Selected |
|--------|-------------|----------|
| Dispatch manually, file the gap | The documented, 8-for-8 proven route; record both defects as backlog naming `beta-release.yml` as the fix pattern | ✓ |
| Port `beta`'s `pypi` job to `release.yml` | Structurally repairs `main` — but inert until the push blocker is also fixed | |
| Repair `main`'s pipeline end to end | Works unattended thereafter; turns a rename phase into a release-infrastructure phase | |

**User's choice:** Dispatch manually, file the gap.
**Notes:** All 8 `publish.yml` runs in repository history are `workflow_dispatch`; zero `release` events, ever. The evidence is already on disk — GitHub release `2.0.8` exists, PyPI's latest is `2.0.7`.

### Q3 — How to gate the operator steps

| Option | Description | Selected |
|--------|-------------|----------|
| Two gates, agent verifies between | Agent reads the `release.yml` run conclusion live and branches on what it sees | ✓ |
| One gate, full written procedure | Fewer interruptions; agent reports the outcome secondhand | |
| Three gates, verify each step | Maximum evidence quality; three interruptions | |

**User's choice:** Two gates, agent verifies between.
**Notes:** The unexpected-success branch matters — the bot would cut `2.0.10`, not `2.0.9`, because `update_version.py` bumps on top of whatever the PR carries. 189-04 explicitly refused to report a protected-branch outcome secondhand, which is why option 2 was not taken.

---

## STABLE-02's instrument

### Q1 — What is the instrument?

| Option | Description | Selected |
|--------|-------------|----------|
| New main-flavoured fixture | `191-stable-install-fixture.sh` under the phase dir; re-runnable by Phase 193 and a post-claim milestone | ✓ |
| Adapt 190's fixture with capability probing | One script for both API shapes; would live in 190's directory while proving a 191 criterion | |
| Plain captured transcript | Cheapest; not re-runnable, breaks the 189/190 precedent | |

**User's choice:** New main-flavoured fixture.
**Notes:** 190's D-16 said Phase 191 would re-run its fixture. That is not executable — it imports `fetch_release_info(channel=)`, `FIRESTARTER_RELEASES_URL`, `click`, `cli_handlers.cli`, `fw --list` and `fw --stable`, none of which exist in 2.0.x. The premise was re-measured live: both endpoints return byte-identical bodies, so only `redirects == 0` discriminates.

### Q2 — What is the "clean environment"?

| Option | Description | Selected |
|--------|-------------|----------|
| Plain venv, default `python3` | Closest to what a real user gets; fixture prints `firestarter.__file__` to prove which artefact ran | ✓ |
| `uv venv --python 3.11` | Mirrors 190 D-17 | |
| Both interpreters | Doubles the transcript for a claim with no plausible interpreter dependence | |

**User's choice:** Plain venv, default `python3`.
**Notes:** 190's py3.11 pin existed to match Host CI. `origin/main` has no `ci.yml` and declares `requires-python = ">=3.9"`, so that reason does not carry over.

### Q3 — How is update-check demonstrated?

| Option | Description | Selected |
|--------|-------------|----------|
| Drive `_compare_versions` directly, no board | Honours the milestone's "Bench: none" | |
| Use the bench board over USB passthrough | A genuine end-to-end update-check against hardware | ✓ |
| Stop at download asset | Leaves the last named step of STABLE-02 unevidenced | |

**User's choice:** *(free text)* "Do the bench test." — overriding the board-free recommendation.

**Follow-up — how far does the bench test go?**

| Option | Description | Selected |
|--------|-------------|----------|
| Answer `y` — full flash, then restore | Flash `2.0.6`, then re-flash `3.0.0b29`/`b22` to leave the bench as found | |
| Answer `y` — full flash, leave on `2.0.6` | Single pass; the board reflects what a default-install user gets | ✓ |
| Answer `n` — stop at the prompt | Every step exercised against hardware except the flash | |

**User's choice:** Full flash, leave the board on `2.0.6`.
**Notes:** The operator then sent an unprompted correction — *"No guard or questions needs to be Asked it a test board"* — so the planned no-flash guard and every per-flash confirmation were dropped from the design. Board identified first: Leonardo on `/dev/ttyACM0` at firmware `3.0.0b22`; stable `2.0.6` ships `firestarter_leonardo.hex`, and `_compare_versions` was measured to raise `ValueError` on `int("0b22")`, so the CLI offers a downgrade.

---

## main's README firmware link

### Q1 — How is the 191/192 boundary recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| 191 owns `main` outright; 192 re-verifies | The 189 D-09 / 190 D-04 pattern; 192 checks `origin/main` as a ref rather than editing it | ✓ |
| 191 changes it, 192 claims coverage | Less work in 192; nothing independently confirms the merged state | |
| Leave README to Phase 192 entirely | Reverts D-03; costs a second protected-branch PR and ships a stale README in the 2.0.9 sdist | |

**User's choice:** 191 owns `main` outright; 192 re-verifies.
**Notes:** Without this, `origin/main`'s `README.md:17` falls through both phases — SWEEP-01 names "both sub-repo READMEs" but Phase 192 sweeps the milestone branch, where that line is invisible. Re-verifying a ref also partially closes D-02's stated gap at no cost.

---

## Claude's Discretion

- The fixture's name, argument handling, temp-directory strategy and transcript capture.
- How the bench transcript is captured and where under the phase directory it lands.
- The wording of `README.md:17`'s repointed link beyond changing the slug.
- Commit granularity across the prepared `main` branch, the fixture, the evidence and the backlog items.
- The exact wording of the two backlog items, so long as each names `beta-release.yml` as the proven pattern.
- Whether the `_compare_versions` beta-string finding becomes its own backlog item or a `SUMMARY.md` observation.

## Deferred Ideas

- `release.yml`'s auto-commit cannot push to a protected `main` — filed as backlog.
- `publish.yml`'s `release: published` trigger has never fired (0 of 8 runs) — filed as backlog.
- `main`'s `_compare_versions` cannot parse a `3.0.0bNN` firmware string.
- GitHub release `2.0.8` is orphaned — cut 2026-08-07, never published to PyPI.
- Porting Phase 190's URL-04 improvements to `main`.
- A `tests/` directory and `ci.yml` on `main`.
- Resolving the PyPI/GitHub name incoherence (already in the milestone's Out of Scope table).
- `.planning/config.json`'s pruned `sub_repos` block.
