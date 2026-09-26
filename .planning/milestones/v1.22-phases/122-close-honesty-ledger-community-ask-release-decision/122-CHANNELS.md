# Phase 122 Plan 08 — Both-Channels-Public Verification Transcript

**Written:** 2026-07-30 (Plan 122-08, wave 7)
**Purpose:** The committed proof that D-03's gate held — both distribution channels are publicly
live, verified by live resolution checks against the actual index/API, never by a green CI tick and
never by the devcontainer's editable install — before any comment reaches gh#11 or gh#12 (constraint
3). This is the artifact plans 122-11 and 122-12 cite as "channels verified" fact.

**Observed tags this transcript verifies (read from `122-CUT.md`, never hardcoded):**
- Firmware (`henols/firestarter`): `3.0.0b14`
- App (`henols/firestarter_app`): `3.0.0b14`

**`beta` HEADs at verification time (Pitfall 3 — local is stale immediately after CI):**

```
firestarter:     local beta b9bb6b7, origin/beta 5c9160a (1 commit ahead — the version bump)
firestarter_app: local beta 81fa53c, origin/beta e7d3ee8 (1 commit ahead — the version bump)
```

Unchanged from `122-CUT.md` §12 — recorded again here to pin the state this verification ran
against. Any later local operation touching either repo's `beta` must `git fetch` first.

---

## 1. The PyPI dispatch that made this verification possible

Constraint 7 — `publish.yml` requires a manual `workflow_dispatch`; it never fires as a side effect
of the merge. Before this dispatch, PyPI's newest beta was `3.0.0b13` (confirmed live, matching
`122-RESEARCH.md` C-3's historical miss list).

| Field | Value |
|---|---|
| Command | `gh workflow run publish.yml --repo henols/firestarter_app -f tag=3.0.0b14` |
| Tag input source | `122-CUT.md` §2, OBSERVED CUT TAG (app) — read, not typed from expectation (A3) |
| Run ID | `30555530238` |
| Trigger | `workflow_dispatch` |
| Conclusion | **success** |
| URL | https://github.com/henols/firestarter_app/actions/runs/30555530238 |
| Steps | Set up job ✓ · Checkout ✓ · `pip install --upgrade build && python3 -m build` ✓ · Publish package ✓ · Post Publish package ✓ · Post Checkout ✓ · Complete job ✓ |
| Local publish tools invoked | **none** — no `twine`, no local `python -m build`, no `pip wheel`, no `setup.py` command was run outside the workflow environment |
| `.github/` diff vs `origin/beta` | `git diff origin/beta --name-only -- .github/` in `firestarter_app` → **empty**. `publish.yml` was read (its `workflow_dispatch`/`tag` contract confirmed live) and never edited. |
| Secrets | `gh auth token` was never run; no `PYPI_API_TOKEN` / `PERSONAL_ACCESS_TOKEN` / `GITHUB_TOKEN` value appears anywhere in this transcript or in any command output quoted above. |

This is exactly one dispatch. No re-dispatch was needed — the first attempt concluded success.

---

## 2. Channel (a) — PyPI, the host app's sole distribution channel

Three independent checks, none of which reads the devcontainer's editable install
(`pip install -e .` in `/workspaces/firestarter_app` reports branch state, not PyPI state, and was
not consulted for any of the three).

| # | Channel | Command | Expected | Observed | Verdict |
|---|---|---|---|---|---|
| 1 | PyPI (JSON API) | `python3 -c "import json,urllib.request; d=json.load(urllib.request.urlopen('https://pypi.org/pypi/firestarter/json')); print('3.0.0b14' in d['releases'])"` | `3.0.0b14` present in `releases` | First attempt (immediately post-dispatch-conclusion): `False`. Retried at 15 s intervals (eventual-consistency caveat below); attempt 1 of the retry loop (≈15 s later): `True`. Full `3.0.0b*` list: `['3.0.0b1', '3.0.0b2', '3.0.0b3', '3.0.0b7', '3.0.0b8', '3.0.0b11', '3.0.0b13', '3.0.0b14']`. `info.version` (latest **stable**): `2.0.7` | **VERIFIED** |
| 2 | PyPI (clean-env resolution) | `pip index versions firestarter --pre`, run from `$(mktemp -d)` — never the repo's editable env | `3.0.0b14` reported as `LATEST` prerelease | `firestarter (3.0.0b14)` / `Available versions: 3.0.0b14, 3.0.0b13, 3.0.0b11, 3.0.0b8, 3.0.0b7, 3.0.0b3, 3.0.0b2, 3.0.0b1, 2.0.7, …` / `LATEST: 3.0.0b14 (pre-release; install with pip install --pre)`. (The command's own `INSTALLED:` line read `3.0.0b11` — that is this container's system-python package state from an earlier session, unrelated to and not read as evidence for this check; the assertion is against `LATEST`, which comes from the live index, not the local install.) | **VERIFIED** |
| 3 | PyPI (downloadability) | `pip download firestarter==3.0.0b14 --no-deps -d $(mktemp -d)` | A wheel or sdist lands; nothing installed anywhere | `Downloading firestarter-3.0.0b14-py3-none-any.whl (196 kB)` → `Saved ./firestarter-3.0.0b14-py3-none-any.whl` in the scratch dir. `--no-deps` was used. This is a verification read of the artifact this plan's Task 1 just published — it introduces no dependency and installs nothing into any environment (RESEARCH's Package Legitimacy Audit records zero package installs in phase scope; this does not change that). | **VERIFIED** |

**Channel (a) verdict: VERIFIED.** All three independent checks agree; none used the editable
install; none used a workflow status as evidence.

### The eventual-consistency caveat (explicit, not a failure)

Check #1's first read returned `False` immediately after the dispatch's run conclusion — PyPI's JSON
API is served from a cache layer that lags the actual index by up to roughly 15-30 seconds after a
new file lands. This is expected and is **not** recorded as `NOT VERIFIED`: per this task's own
instruction, a check that fails once is re-run after a short interval before being scored. The retry
(15 s later) returned `True` and matched checks #2 and #3, which read the live index directly and
already showed `3.0.0b14`. Both PyPI and the GitHub releases API used in §3 below are eventually
consistent in the same way — any future re-run of this transcript that reads a stale negative on a
first attempt should retry before recording `NOT VERIFIED`.

---

## 3. Channel (b) — the firmware GitHub prerelease (carries the actual `.hex` deliverable)

C-7's asymmetry stated plainly: channel (a) above is PyPI and it is where the host **app** actually
lives; channel (b) here is the firmware **GitHub prerelease**, and it is where the three board `.hex`
files actually live. The **app's own** GitHub release (checked separately in §4) carries **zero**
assets and is a tag-and-release marker only — a verification that checked only the app's GH release
would prove nothing a user can install.

| # | Channel | Command | Expected | Observed | Verdict |
|---|---|---|---|---|---|
| 4 | Firmware GitHub prerelease | `gh release view 3.0.0b14 --repo henols/firestarter --json isPrerelease,assets,body -q '{pre:.isPrerelease, hex:[.assets[].name], body_len:(.body|length)}'` | `pre=true`; assets exactly `firestarter_leonardo.hex`, `firestarter_uno.hex`, `firestarter_uno328pb.hex`; `body_len` 0 (expected at this point — the hand-written body lands in 122-12) | `{"body_len":0,"hex":["firestarter_leonardo.hex","firestarter_uno.hex","firestarter_uno328pb.hex"],"pre":true}` | **VERIFIED** |

**Channel (b) verdict: VERIFIED.**

---

## 4. Presence-only — the app's own GitHub release (not an install path, recorded as expected)

| # | Channel | Command | Expected | Observed | Verdict |
|---|---|---|---|---|---|
| 5 | App GitHub release (presence only) | `gh release view 3.0.0b14 --repo henols/firestarter_app --json isPrerelease,assets -q '{pre:.isPrerelease, asset_count:(.assets|length)}'` | Exists; `pre=true`; `asset_count=0` — **expected**, per C-7 PyPI is the app's sole distribution channel, not this release | `{"asset_count":0,"pre":true}` | **VERIFIED (presence-only, 0 assets is correct, not a gap)** |

Also confirmed at the same moment for completeness (not part of the acceptance criteria, but a fact
worth pinning alongside §1's firmware body): `gh release view 3.0.0b14 --repo henols/firestarter_app
--json body -q '.body|length'` → `0`. No release body has been written for either repo yet — the
hand-written bodies are 122-12's job, after the D-16 wording review.

---

## 5. A green workflow tick was explicitly NOT accepted as evidence for either channel

This is the whole reason D-03 gates on a live resolution check rather than a CI status, and it is the
exact mechanism that lost `b12`: `beta-release.yml` reported green, the app's GitHub release existed,
and PyPI never moved, because the release was created by a PAT lacking `workflow` scope, which
suppresses the `release.published` event that would otherwise have cascaded into `publish.yml`. In
this plan, Task 1's `publish.yml` run reporting `success` (§1) was **not** treated as sufficient —
§2's three independent PyPI checks against the live index and a clean environment are what earned the
`VERIFIED` verdict, and they were run and recorded after the workflow's own conclusion, as separate
evidence.

---

## 6. No stable release was published

`info.version` on PyPI (§2, check #1) is still `2.0.7`. Nothing in Task 1's dispatch or this
verification approached the stable channel; stable remains operator-gated per longstanding project
policy (`feedback_stable_release_operator_gated`), and this plan's scope never included it.

---

## 7. No community comment has been posted at this point

Comment counts on both tracked issues, read immediately before writing this artifact, match
`122-RESEARCH.md`'s recorded Community Thread Ground Truth exactly — unchanged:

```
$ gh issue view 11 --repo henols/firestarter_prom --json comments -q '.comments|length'
12
$ gh issue view 12 --repo henols/firestarter_prom --json comments -q '.comments|length'
8
```

Neither `henols/firestarter_prom#11` nor `#12` has been touched by this plan. Constraint 3 ("b14
exists and both channels are verified public before any comment is posted") is satisfied by this
artifact's existence, committed before plans 122-11 (wording review) and 122-12 (the comments) run —
not by anything said to either reporter, because nothing has been said yet.

---

## 8. Summary verdict

| Channel | Verdict |
|---|---|
| (a) PyPI (host app) | **VERIFIED** — JSON API, clean-env `pip index versions --pre`, and an actual `pip download --no-deps` all agree on `3.0.0b14` as the latest prerelease |
| (b) Firmware GitHub prerelease (`.hex` assets) | **VERIFIED** — `isPrerelease=true`, exactly the three expected asset names |
| App GitHub release (presence only) | **VERIFIED** — exists, `isPrerelease=true`, 0 assets, expected per C-7 |

**Both channels are publicly live. No stable release exists beyond `2.0.7`. No community comment has
been posted. This artifact is committed before any wording review or comment plan runs.**

---

## Self-verifying facts for downstream automation

- `TAG=3.0.0b14` (read from `122-CUT.md`, never hardcoded independently by this file's consumers)
- `PYPI-VERIFIED` — `3.0.0b14` present in PyPI's `releases` (§2 #1)
- `FIRMWARE-HEX-VERIFIED` — three named `.hex` assets present on the firmware prerelease (§3 #4)
- `APP-RELEASE-PRESENT` — app release exists, 0 assets, expected (§4 #5)
- `NO-STABLE-PUBLISHED` — `info.version` == `2.0.7` (§2 #1, §6)
- `NO-COMMENT-YET` — issue 11 comment count 12, issue 12 comment count 8, both unchanged (§7)
