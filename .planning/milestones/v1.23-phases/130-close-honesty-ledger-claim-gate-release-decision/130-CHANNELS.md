# Phase 130 Plan 15 — Both-Channels-Public Verification Transcript

**Written:** 2026-08-02 (Plan 130-15, wave 8)
**Purpose:** The committed proof that both distribution channels are actually public, after the
operator performed `130-HANDOFF.md`'s procedure — verified by live resolution checks against the
actual index/API/release surfaces, never by a green CI tick and never by this devcontainer's
editable install. This plan is read-only against every remote; Task 2 below is the fail-closed
precondition that would have stopped this transcript cold had the operator not acted.

**Observed tags this transcript verifies (read from `gh release list`, never hardcoded or
computed from the version-bump arithmetic that happens to predict the same value):**
- Firmware (`henols/firestarter`): `3.0.0b15`
- App (`henols/firestarter_app`): `3.0.0b15`

**The ceiling this was compared against, and where it came from:** `3.0.0b14` in both repos,
read from `130-HANDOFF.md` line 121 ("THE TAG CEILING, RECORDED HERE FOR PLAN 130-15 TO COMPARE
AGAINST: `3.0.0b14` in both repos"), **not** from the default embedded in this plan's own verify
snippet.

**`origin/beta` at verification time (read fresh in this session, not carried from any prior
plan's measurement):**

```
firestarter:      origin/beta = 0933bd7d602efb30e4a666e8231ecf724e90ab09
firestarter_app:  origin/beta = 16a313a040389aa7c88a98b85f79a7d667ca2f6f
```

Each includes CI's own `git-auto-commit-action` version-bump commit on top of the operator's
merge — the standing hazard `130-HANDOFF.md` §1.4 named in advance. Neither value moved during
this plan's execution; every check below re-confirms it unchanged.

---

## 0. Task 1 — the fail-closed hand-off boundary

Task 1 is a `checkpoint:human-verify` gate whose resume signal is "pushed and dispatched." **The
run continued on the operator's explicit authorization that `130-HANDOFF.md` §2 steps 1–7 were
performed in full** — this is recorded here plainly, per the plan's own acceptance criteria, so
that if this transcript is ever read after an accidental auto-approval, the distinction between
"the operator confirmed" and "the run continued unconfirmed" is visible rather than papered over.

- `130-HANDOFF.md` is committed: `git log --oneline -1 -- .../130-HANDOFF.md` → commit exists on
  the meta branch (verified below in the self-check section).
- This task itself executed no command against any remote. `git -C firestarter rev-parse
  origin/beta` and `git -C firestarter_app rev-parse origin/beta`, read at the start of this
  plan's execution and again just before this section was written, are identical — both quoted
  above — confirming Task 1 performed no push, merge, tag, or dispatch of its own.
- Resume signal recorded verbatim: **"pushed and dispatched."** The operator confirmed steps 1–7
  of `130-HANDOFF.md` §2 complete: the D-02 blocking wording review, the pre-flight go/no-go
  check, the `--no-ff` merge and push in both sub-repos, the observed-tag read, the ARM-gate
  check, the manual `publish.yml` dispatch, and the posting of both release bodies.

This plan's own Task 2, immediately below, does not trust that confirmation — it independently
re-derives the same conclusion from the public release surfaces themselves.

---

## 1. Task 2 — the fail-closed precondition, read and not computed

Both repos' release lists, captured verbatim:

```
$ gh release list --repo henols/firestarter --limit 5
3.0.0b15	Pre-release	3.0.0b15	2026-08-02T21:22:42Z
3.0.0b14	Pre-release	3.0.0b14	2026-07-30T14:28:19Z
3.0.0b13	Pre-release	3.0.0b13	2026-07-28T10:01:43Z
3.0.0b12	Pre-release	3.0.0b12	2026-07-27T09:21:48Z
3.0.0b11	Pre-release	3.0.0b11	2026-07-26T11:10:01Z

$ gh release list --repo henols/firestarter_app --limit 5
3.0.0b15	Pre-release	3.0.0b15	2026-08-02T21:21:19Z
3.0.0b14	Pre-release	3.0.0b14	2026-07-30T14:58:35Z
3.0.0b13	Pre-release	3.0.0b13	2026-07-28T09:54:29Z
3.0.0b12	Pre-release	3.0.0b12	2026-07-27T09:21:09Z
3.0.0b11	Pre-release	3.0.0b11	2026-07-26T15:52:48Z
```

**The precondition check:** the newest tag in each repo (`3.0.0b15`, `3.0.0b15`) is compared
against the ceiling read from `130-HANDOFF.md` (`3.0.0b14`, `3.0.0b14`). `b15 > b14` in both
repos — **strictly newer in both.** The automated verify script (embedded in `130-15-PLAN.md`
Task 2) was run against this exact data and printed `PRECONDITION MET`, exit `0`:

```
henols/firestarter {'tagName': '3.0.0b15', 'isDraft': False, 'isPrerelease': True, 'publishedAt': '2026-08-02T21:22:42Z'}
henols/firestarter_app {'tagName': '3.0.0b15', 'isDraft': False, 'isPrerelease': True, 'publishedAt': '2026-08-02T21:21:19Z'}
PRECONDITION MET
```

**This is a read, not a computation.** The auto-increment arithmetic (`is_beta_mode()` →
tag-scan max-plus-one) happens to predict `b15` deterministically from the `b14` ceiling in both
repos — that derivability is exactly why CONSTRAINT 5 is not relaxed: a concurrent cut, an
out-of-band tag, or a rehearsal-tag collision would have changed it. The value recorded above and
used throughout the rest of this transcript is the one `gh release list` and `gh release view`
actually reported, in this session, after the cut — never a literal typed from expectation. (No
`3.0.0b15` string appears in any command in this file intended to be *run* verbatim — the two
verify-script snippets quoted above are the plan's own pre-authored `<automated>` blocks, executed
as written, not hand-typed with the tag substituted in.)

**Draft/prerelease status, asserted and recorded for both repos:**

```
$ gh release view 3.0.0b15 --repo henols/firestarter --json tagName,isDraft,isPrerelease,publishedAt
{"isDraft":false,"isPrerelease":true,"publishedAt":"2026-08-02T21:22:42Z","tagName":"3.0.0b15"}

$ gh release view 3.0.0b15 --repo henols/firestarter_app --json tagName,isDraft,isPrerelease,publishedAt
{"isDraft":false,"isPrerelease":true,"publishedAt":"2026-08-02T21:21:19Z","tagName":"3.0.0b15"}
```

`isDraft` **false** and `isPrerelease` **true** in both repos — neither release is a draft (which
would not be public), and both are correctly marked as prereleases (no stable channel was
touched). **Precondition met. Proceeding to Task 3.**

---

## 2. The two-attempt cut — first CI attempt FAILED, three pre-existing CI-only test defects fixed and re-pushed

This is not something this plan fixed — it happened during the operator's execution of
`130-HANDOFF.md` §2 step 3, outside any plan's task, and is recorded here because it is a real
finding of this phase's close and plan 130-16's sweep needs to be able to account for it without
re-deriving it.

**Root cause, shared by all three defects:** tests that assume the devcontainer's sibling-checkout
layout (`firestarter` and `firestarter_app` checked out side-by-side under one parent) and break in
a standalone CI checkout, where each repo's workflow checks out only itself.

**Confirmed from CI run history, read-only, this session:**

```
$ gh run list --repo henols/firestarter --workflow beta-build.yml --limit 3 --json databaseId,headSha,conclusion,createdAt,url
[first attempt] 30766766233  f114356a  FAILURE   2026-08-02T20:56:59Z
[second attempt] 30767636067 1c511e8   success   2026-08-02T21:19:53Z

$ gh run list --repo henols/firestarter --workflow py32f071.yml --limit 3 --json databaseId,headSha,conclusion,createdAt,url
[first attempt] 30766766225  f114356a  success   2026-08-02T20:56:59Z   (ARM gate itself was already green)
[second attempt] 30767636043 1c511e8   success   2026-08-02T21:19:53Z

$ gh run list --repo henols/firestarter_app --workflow beta-release.yml --limit 4 --json databaseId,headSha,conclusion,createdAt,url
[first attempt] 30766774000  a1e9c52f  FAILURE   2026-08-02T20:57:11Z
[second attempt] 30767629015 5934a54   success   2026-08-02T21:19:42Z
```

The firmware's own ARM gate (`py32f071.yml`) was green on the *first* attempt already — the
failure was in `beta-build.yml`'s host-side test job, not the ARM build itself.

**Fix 1 — `firestarter` `tests/test_flash_path_record_sync.py::
TestFlashPathRecordSyncFailsClosed::test_present_root_with_missing_target_raises_not_skips`.**
Hard-asserted `META_PRESENT`. That is the leg's *premise*, not its claim; in CI no meta root is
fetched, so an unmet premise became a red build. Changed to `pytest.skip(META_ABSENT_REASON)`, the
same idiom roughly 20 sibling legs in the same file already use. Commit `1c511e8`. **This softened
a leg Phase 129 wrote as a bare hard assert — recorded explicitly, not left to be discovered
silently**, because a hard assert on an unfetched premise is a different defect class than a
logic bug, and the softening changes what the leg can ever catch in CI. Verified both ways in this
session's own re-run context: 41/41 with the meta root present (devcontainer), 9 passed / 32
skipped / 0 failed with it absent (CI shape).

**Fix 2 — `firestarter_app` `tests/test_py32_flash_map_host.py::
TestLinkerScriptParityFailsClosedOnBadInput::test_planted_mutated_config_origin_is_detected`.**
Reads the *real* linker script and git-hashes it via `git -C .../firestarter hash-object`, so it
genuinely requires the sibling checkout — but carried no `@requires_fw` marker, so in CI (no
sibling `firestarter` checkout present) it died on exit 128 rather than skipping. Gated with
`@requires_fw`. The class docstring's claim "None carries `@requires_fw`" was also corrected — true
of the two synthetic legs in that class, false of this one. Commit `5934a54`.

**Fix 3 — `firestarter_app` `tests/test_scan_paths_resolve.py::
test_no_entry_is_a_same_repo_lookalike`.** A genuine logic bug, not a CI-layout artifact:
`assert "firestarter_app" not in str(resolved)` conflated "is inside the app repo" with "the app
repo's name appears anywhere in the path." Under GitHub Actions' `work/<repo>/<repo>` checkout
layout, the sibling firmware checkout lands at `work/firestarter_app/firestarter` — **not** inside
the app repo, yet containing its name as a substring. Replaced with `Path.is_relative_to`
containment against the app root. RED proven both directions in this session: the old string-`in`
assertion fails on that exact path shape (`work/firestarter_app/firestarter` contains
`"firestarter_app"` as a substring while not being inside it); the new containment-based assertion
passes. Same commit `5934a54`.

**Why none of this was visible before this publish:** locally, all three legs pass, because the
devcontainer *has* the sibling-checkout layout that CI lacks. The app's own separate Host CI
(`ci.yml`) was already red from unrelated pre-existing type-check debt (`reference_devcontainer_py312_masks_ci_py39`),
so there was no green baseline to visibly lose when these three broke — they had simply never been
exercised in a standalone CI checkout before this cut.

Both fix commits are confirmed present and on `origin/beta` in this session:

```
$ git -C firestarter log --oneline -1 1c511e8
1c511e8 fix(130): scope the meta-root premise leg to skip when no meta root exists
$ git -C firestarter merge-base --is-ancestor 1c511e8 origin/beta && echo ancestor
ancestor

$ git -C firestarter_app log --oneline -1 5934a54
5934a54 fix(130): make two cross-repo legs correct in a standalone CI checkout
$ git -C firestarter_app merge-base --is-ancestor 5934a54 origin/beta && echo ancestor
ancestor
```

---

## 3. Task 3 — Channel (b): the firmware GitHub prerelease, the real deliverable

D-03 / CONSTRAINT 8: `beta-build.yml`'s ARM steps are `continue-on-error: true` by design, so a
green run is never accepted as evidence the py32 asset shipped (§7 names this explicitly). The
assertion is made against the real, published `3.0.0b15` release only.

```
$ gh release view 3.0.0b15 --repo henols/firestarter --json assets
```

| Asset | Size | SHA-256 digest (prefix) |
|---|---|---|
| `firestarter_leonardo.hex` | 73196 | `fc09dee4…` |
| `firestarter_py32f071.hex` | 77284 | `798ae8a1…` |
| `firestarter_uno.hex` | 67395 | `a5074ade…` |
| `firestarter_uno328pb.hex` | 67534 | `13f43174…` |

**`firestarter_py32f071.hex` is present.** D-03's hard gate **PASSES**. All three AVR hexes
(`firestarter_leonardo.hex`, `firestarter_uno.hex`, `firestarter_uno328pb.hex`) are also present —
REL-03's containment property (a broken ARM build still publishes all three AVR assets) holds on
this real cut, though it was not exercised here since the ARM leg did not break.

**The b14 before-state, recorded for contrast** (the transition this cut represents):

```
$ gh release view 3.0.0b14 --repo henols/firestarter --json assets
```

| Asset | Size |
|---|---|
| `firestarter_leonardo.hex` | 73347 |
| `firestarter_uno.hex` | 67338 |
| `firestarter_uno328pb.hex` | 67452 |

**Zero py32 asset at b14. Four assets including `firestarter_py32f071.hex` at b15.** This is the
**first publication ever** of `firestarter_py32f071.hex` as a real, downloadable release asset —
the only thing that makes the already-landed host capabilities (the DFU installer, `--dfu-probe`,
`--usb-id`, the beta-gated `py32f071` board choice) reachable by anyone outside this tree.

---

## 4. Presence-only — the app's own GitHub release

```
$ gh release view 3.0.0b15 --repo henols/firestarter_app --json assets
{"assets":[]}
```

**Zero assets, as expected.** The app's release workflow (`beta-release.yml` /
`.github/scripts/update_version.py`) has no `files:` step; b14 also carried none. The GitHub
release is a tag-and-marker page — PyPI, verified in §5 below, is the app's actual install path.
This is recorded as expected, not as a gap.

---

## 5. Channel (a) — PyPI, the host app's sole distribution channel, verified from a clean temp env

CONSTRAINT 7: verified **directly**, from a fresh `python3 -m venv` created under the scratch
directory — never this project's own environment, which already carries an editable install that
could satisfy a resolution check PyPI itself could not.

```
$ SCR=/tmp/.../scratchpad/pypi-check
$ rm -rf "$SCR" && mkdir -p "$SCR"
$ python3 -m venv "$SCR/venv"
exit: 0

$ APPTAG=$(gh release list --repo henols/firestarter_app --limit 20 --json tagName -q '.[].tagName' | grep -E '^3\.0\.0b[0-9]+$' | sort -V | tail -1)
observed app tag: 3.0.0b15

$ "$SCR/venv/bin/pip" download --no-deps --pre "firestarter==3.0.0b15" -d "$SCR/dl"
Collecting firestarter==3.0.0b15
  Downloading firestarter-3.0.0b15-py3-none-any.whl.metadata (37 kB)
Downloading firestarter-3.0.0b15-py3-none-any.whl (215 kB)
Saved .../scratchpad/pypi-check/dl/firestarter-3.0.0b15-py3-none-any.whl
Successfully downloaded firestarter
exit: 0

$ ls -l "$SCR/dl"
firestarter-3.0.0b15-py3-none-any.whl   (215951 bytes, the only file)
```

**Resolved on the first attempt — no retry needed.** The eventual-consistency caveat carried
forward from `122-CHANNELS.md` §"eventual-consistency caveat" is recorded here as a **non-failure
note**, not because it fired this time: PyPI's JSON API and simple index can lag seconds to
minutes after an upload (the operator's `publish.yml` dispatch completed roughly 6–7 minutes before
this check ran, well past any plausible lag window), so a first-attempt miss would have been
retried at a short interval and recorded as a retry, not a failure. This run's retry count is
**zero attempts beyond the first** because the first attempt already resolved.

```
$ python3 -c "import json,urllib.request;print(json.load(urllib.request.urlopen('https://pypi.org/pypi/firestarter/json'))['info']['version'])"
2.0.7
```

**PyPI's `info.version` (the latest *stable*) is `2.0.7`, unchanged.** No stable release was
published by this cut.

---

## 6. The section this transcript exists for — a green workflow tick was explicitly NOT accepted as evidence for either channel

**For the firmware asset:** `beta-build.yml`'s ARM build step is wrapped in
`continue-on-error: true` by design (evaluated on `outcome`, not `conclusion`), and its `files:`
glob (`build/py32f071/firestarter_*.hex`) runs with `fail_on_unmatched_files` unset, so an
unmatched glob only **warns** rather than failing the job. A fully green `beta-build.yml` run is
therefore structurally compatible with zero py32 assets publishing. The read-only command accepted
as evidence instead was `gh release view 3.0.0b15 --repo henols/firestarter --json assets` against
the real, non-rehearsal cut (§3 above) — not the run conclusion recorded in §2.

**For PyPI:** `publish.yml`'s own in-file comment records that a release created by another
workflow using a PAT lacking `workflow` scope suppresses the `release.published` event that would
otherwise trigger it automatically — which is exactly why step 6 of `130-HANDOFF.md`'s procedure
dispatches it **manually**. Six of the thirteen previously published app betas never reached PyPI
by the automatic path, and `3.0.0b12`'s absence from PyPI (still unresolved as of this writing) is
the corroborating case. The read-only commands accepted as evidence instead were the fresh-venv
`pip download` (§5) and the direct `info.version` read (§5) — not `publish.yml`'s own `conclusion`
(recorded read-only in §2's table: run `30767771243`, `success`, `workflow_dispatch`), which was
consulted only to know *when* to check, never treated as proof PyPI actually carries the version.

---

## 7. No stable release

- PyPI's `info.version` is `2.0.7` — unchanged from before this cut (§5).
- Neither release is marked "latest" by GitHub's own semantics: `isPrerelease: true` for both
  (§1), and GitHub's `/releases/latest` endpoint — which returns only the newest non-prerelease,
  non-draft release — still resolves to the old stable tags:
  ```
  $ curl -s https://api.github.com/repos/henols/firestarter/releases/latest | jq .tag_name
  "2.0.6"
  $ curl -s https://api.github.com/repos/henols/firestarter_app/releases/latest | jq .tag_name
  "2.0.7"
  ```
- `main` is untouched in all three repos this session — `origin/main` was read, never written:
  `firestarter` `b3b6cce6…`, `firestarter_app` `f4bd03c8…`, meta `1c8b96da…`. No merge, checkout,
  or push targeted `main` anywhere in this plan.
- Stable promotion remains operator-gated standing policy (`feedback_stable_release_operator_gated`);
  this close is beta-only, exactly like v1.22.

---

## 8. No community comment — and the inbox is NOT empty

No thread received a comment this milestone, and no CLOSE requirement depended on a reply. But the
inbox is not clear — two items arrived after the 2026-07-27 import that stopped at gh#17, both
confirmed open in this session and both out of scope here:

```
$ gh issue view 20 --repo henols/firestarter_prom --json number,title,createdAt,state
{"number":20,"title":"[dev test] at28c256 — FAIL (00e121446ceb)","createdAt":"2026-07-30T16:44:03Z","state":"OPEN"}
$ gh issue view 18 --repo henols/firestarter_prom --json number,title,createdAt,state
{"number":18,"title":"[dev test] fm1608 — PASS (a6915f4437ee)","createdAt":"2026-07-28T08:19:31Z","state":"OPEN"}
```

gh#20 (an AT28C256 `dev test` FAIL) and gh#18 (an FM1608 `dev test` PASS report) are both named
here explicitly so no reader concludes the inbox is empty because this plan is silent about it.

---

## 9. Summary verdict

| Channel | Verdict |
|---|---|
| (b) Firmware GitHub prerelease (`.hex` assets, including py32) | **VERIFIED** — `isDraft=false`, `isPrerelease=true`, all four expected assets present, b14-vs-b15 contrast recorded |
| (a) PyPI (host app) | **VERIFIED** — clean-venv `pip download --no-deps --pre` resolved on the first attempt; `info.version` confirms no stable regression |
| App GitHub release (presence-only) | **VERIFIED** — exists, `isPrerelease=true`, 0 assets, expected per the app's own release workflow having no `files:` step |

**Both distribution channels are publicly live. `firestarter_py32f071.hex` shipped as a real
release asset for the first time this milestone. No stable release exists beyond `2.0.6`/`2.0.7`.
No community comment has been posted, and the inbox carries two unrelated open items (gh#18,
gh#20). The first CI attempt of this cut failed on three pre-existing CI-only test defects, fixed
and re-pushed to a green second attempt — this is recorded as a real finding of this phase's
close, not smoothed over.**

**Every claim above is about publication.** Nothing in this transcript says the published
`firestarter_py32f071.hex` image runs, boots, or installs on any board — no PY32F071 board exists,
and the claim ceiling recorded in `130-LEDGER.md` and `130-DECISION.md` stands unchanged by
anything in this file.

---

## Self-verifying facts for downstream automation (plan 130-16 may lift these without re-deriving them)

- `OBSERVED-TAG=3.0.0b15` — read from `gh release list` in both repos, not computed (§1, §2)
- `CEILING=3.0.0b14` — read from `130-HANDOFF.md` line 121 (§1)
- `PRECONDITION-MET` — both repos strictly newer than the ceiling, neither a draft (§1)
- `FIRMWARE-HEX-VERIFIED` — all four assets (including `firestarter_py32f071.hex`) present on the
  real `3.0.0b15` release (§3)
- `PY32-ASSET-FIRST-EVER` — absent at b14, present at b15 (§3)
- `APP-RELEASE-PRESENT` — app release exists, 0 assets, expected (§4)
- `PYPI-VERIFIED` — `firestarter==3.0.0b15` downloadable from a fresh venv, first attempt, no
  retry needed (§5)
- `NO-STABLE-PUBLISHED` — PyPI `info.version` == `2.0.7`; GitHub `/releases/latest` ==
  `2.0.6` (fw) / `2.0.7` (app) (§7)
- `MAIN-UNTOUCHED` — `origin/main` read-only in all three repos (§7)
- `NO-COMMENT-YET` — no thread touched this milestone (§8)
- `INBOX-NOT-EMPTY` — gh#20 (OPEN, FAIL) and gh#18 (OPEN, PASS) both named (§8)
- `CI-TWO-ATTEMPT-CUT` — first attempt failed in both repos (`beta-build.yml` run `30766766233`,
  `beta-release.yml` run `30766774000`); three pre-existing CI-only sibling-checkout test defects
  fixed via `1c511e8` (firestarter) and `5934a54` (firestarter_app); second attempt green in both
  (§2)
- `GITLINK-BUMP-NOT-DONE-HERE` — this plan touched neither gitlink; that is plan 130-16's job
- `NO-REQUIREMENT-TICKED-HERE` — this plan ticks no `CLOSE-*` id; CLOSE-04 is 130-16's alone
