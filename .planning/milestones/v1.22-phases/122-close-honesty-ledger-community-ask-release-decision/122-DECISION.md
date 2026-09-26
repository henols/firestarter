# Phase 122 — CLOSE-03: Recorded `beta`-push Decision + Pre-flight Evidence

**Purpose:** CLOSE-03's text is literal — the accept/avoid/cleanup decision for the `beta` push
must be made and recorded **before any push**. v1.21's close skipped exactly this step and
auto-cut a stray `3.0.0b12`. This artifact's own commit timestamp is the evidence that the
decision preceded the act — nothing is pushed, merged, or published by this plan or this file.

---

## Pre-flight state (measured 2026-07-30T13:00–13:01Z)

**`122-RESEARCH.md` is stamped valid only until ~2026-08-02, precisely because `origin/beta` moves
on any push. Every number below was re-measured live in this session, not copied from RESEARCH.**
Verdict per item: **AGREES** or **⚠ DRIFTED** against the recorded value.

Commands run were fetch-only (`git fetch origin`) plus read-only inspection
(`rev-parse`, `rev-list`, `merge-base`, `show`, `tag --list`, `merge-tree --write-tree`, `status
--porcelain`, `ls-tree`). No merge, checkout, commit, or push was executed against either
sub-repo.

### 1. Branch tips

| Repo | Branch | Tip SHA measured | Recorded (RESEARCH) | Verdict |
|------|--------|-------------------|----------------------|---------|
| `firestarter` | `v1.22-at28c-software-data-protection-lifecycle` | `48c36e569c8ddfd3daa8aea7e55c5bbc79b48b08` | `48c36e5` | **AGREES** |
| `firestarter_app` | `v1.22-at28c-software-data-protection-lifecycle` | `c3c9424f7a299c6ff3498a15620e5235cf72a782` | `c3c9424` | **AGREES** |

Commands: `git -C firestarter rev-parse --abbrev-ref HEAD && git -C firestarter rev-parse HEAD`;
same for `firestarter_app`.

### 2. `origin/beta` tips (after `git fetch origin` in each repo)

| Repo | `origin/beta` SHA measured | Recorded (RESEARCH) | Verdict |
|------|------------------------------|----------------------|---------|
| `firestarter` | `6611fbae18e94abd58f1eea7a96deed533efdb38` | `6611fba` | **AGREES** |
| `firestarter_app` | `1bb55999965a30103f30c506b57032291421dda1` | `1bb5599` | **AGREES** |

`origin/beta` has **not moved** since RESEARCH was written. The push-safety premise this whole
plan rests on is intact.

### 3. Ahead/behind counts (`git rev-list --left-right --count HEAD...origin/beta`)

| Repo | Measured (ahead/behind) | Recorded | Verdict |
|------|--------------------------|----------|---------|
| `firestarter` | `42 / 2` | `42 / 2` | **AGREES** |
| `firestarter_app` | `75 / 7` | `75 / 7` | **AGREES** |

### 4. Merge-base / fork-point coincidence with `v1.21^{commit}` (C-9)

| Repo | `merge-base HEAD origin/beta` | `v1.21^{commit}` | Coincide? |
|------|-------------------------------|-------------------|-----------|
| `firestarter` | `ecf35ea5c022274fb1bf119a189be646b10acf83` | `ecf35ea5c022274fb1bf119a189be646b10acf83` | **YES — AGREES** |
| `firestarter_app` | `7c5dd13b1e52c1f0f66f8467f22873023178ef99` | `7c5dd13b1e52c1f0f66f8467f22873023178ef99` | **YES — AGREES** |

Confirms C-9: v1.22 forked off `beta` (the fork-off-the-previous-tag exception applied to v1.15
and v1.21, **not** v1.22 — this is the standing branch model, not a surprise).

### 5. Version strings on both sides

| Repo | File | `origin/beta` value (measured) | Branch working-tree value (measured) | Recorded | Verdict |
|------|------|----------------------------------|----------------------------------------|----------|---------|
| `firestarter` | `include/version.h` | `VERSION "3.0.0b13"` | `VERSION "3.0.0b11"` | b13/b11 | **AGREES** |
| `firestarter_app` | `firestarter/__init__.py` | `__version__ = "3.0.0b13"` | `__version__ = "3.0.0b11"` | b13/b11 | **AGREES** |

### 6. Highest `3.0.0b*` tag and absence of `3.0.0b14`

`git tag --list '3.0.0b*'` in both repos, sorted (`sort -V`):

```
3.0.0b1 3.0.0b2 3.0.0b3 3.0.0b4 3.0.0b5 3.0.0b6 3.0.0b7 3.0.0b8 3.0.0b9
3.0.0b10 3.0.0b11 3.0.0b12 3.0.0b13
```

Identical list in both `firestarter` and `firestarter_app`. Highest tag in each: **`3.0.0b13`**.
`3.0.0b14` is **absent from both**. **AGREES** with RESEARCH. This is what makes the
auto-increment's target *derivable*, not assumed — A3 still applies: the observed cut tag is read
later, in plan 122-07, never hardcoded as `3.0.0b14` here or anywhere downstream.

### 7. Dry-run merge conflict probe (`git merge-tree --write-tree --messages HEAD origin/beta`)

**`firestarter`:**

```
$ git merge-tree --write-tree --messages HEAD origin/beta
cc86c8b0e721122f369fb3427979f395882eed5b
(exit code 0 — clean tree, zero conflict lines)
```

**Zero conflicts.** `include/version.h` auto-merges b11→b13 and is **not** a conflict. Matches
RESEARCH C-1 exactly. **AGREES.**

**`firestarter_app`:**

```
$ git merge-tree --write-tree --messages HEAD origin/beta
5dbcc06a27302f58a6a4942c7cb6ea760a0773d3
100644 a42034bf82e6809f531dc5b97dbdf88c4cb0c609 1 firestarter/submit.py
100644 2affa16ec9d372c92e57f63204a616aacea597ee 2 firestarter/submit.py
100644 0dc5a3bd70e3e09c03c14e7cd77fa1fde735a420 3 firestarter/submit.py
100644 8eb3363d3a39513683ca0cfd402138aa7d56e3a9 1 tests/test_submit.py
100644 8c46de2f5364e11b17feba07e1743fdf44eae3ec 2 tests/test_submit.py
100644 265fd9057bf740a883da1620d7f71496a4b77659 3 tests/test_submit.py

Auto-merging firestarter/submit.py
CONFLICT (content): Merge conflict in firestarter/submit.py
Auto-merging tests/test_submit.py
CONFLICT (content): Merge conflict in tests/test_submit.py
(exit code 1)
```

**Exactly two conflicted files** — `firestarter/submit.py` and `tests/test_submit.py`.
`firestarter/__init__.py` auto-merges b11→b13 and is **not** a conflict (no `CONFLICT` line names
it). Matches RESEARCH C-2 exactly. **AGREES.**

**Both `include/version.h` (firmware) and `firestarter/__init__.py` (app) are auto-merged, not
conflicted.** A plan or summary naming either as a conflict is wrong.

### 8. `--ours` superset proof for the app conflict resolution

The `comm -23` pipeline (RESEARCH §"Code Examples"), comparing `origin/beta:tests/test_submit.py`'s
`def test_*` names against `HEAD:tests/test_submit.py`'s:

```
$ comm -23 <(git show origin/beta:tests/test_submit.py | grep -o '^\s*def test_[a-z0-9_]*' \
               | sed 's/^ *def //' | sort) \
           <(git show HEAD:tests/test_submit.py | grep -o '^\s*def test_[a-z0-9_]*' \
               | sed 's/^ *def //' | sort)
(empty output)
```

Counts: `origin/beta:tests/test_submit.py` has **60** `def test_*` functions;
`HEAD:tests/test_submit.py` has **77**. `comm -23` (beta names not present on HEAD) is **empty** —
every one of `beta`'s 60 test names exists among HEAD's 77 by name. Matches RESEARCH C-11 exactly
(60/77, empty diff). **AGREES.**

Five `quick-260728-ahy` hotfix behaviours spot-confirmed present on `HEAD:firestarter/submit.py`:

| Behaviour | Grep target | Found at |
|---|---|---|
| `SUBMIT_REPO` retargeted to the project tracker | `henols/firestarter_prom` | line 73 (`SUBMIT_REPO = "henols/firestarter_prom"`), also lines 38/67/69 in comments |
| `gh` tier surfaces stderr regardless of permission tier | `getattr(proc, "stderr"` | lines 272, 425 |
| Caller owns the fallback narration | `degrading to` | lines 577 (docstring), 640, 669 |
| Browser tier / created-issue URL echoed on success | `Report filed` | lines 681, 683 |

All five present. **AGREES** with RESEARCH's superset-proof table.

### 9. A5 gitlink baseline (meta repo, must stay unchanged at phase end — D-07)

```
$ git -C /workspaces ls-tree HEAD firestarter firestarter_app
160000 commit 0048b3d9a3b9aaec5e7e3030f9313acce8e6411a  firestarter
160000 commit 96e062261b8a5e8c29fe3eb6d888468cf876a6cf  firestarter_app
```

Matches RESEARCH's recorded `0048b3d…` / `96e0622…` exactly. **AGREES.** These are one phase
behind the working tips (`48c36e5` / `c3c9424`) by design — per D-07 they stay PINNED, and
correcting them is `/gsd-complete-milestone`'s job, not this phase's.

### 10. Working-tree dirt, all three repos (`git status --porcelain`)

**`firestarter`:**
```
?? firestarter/
```
Pre-existing, known dirt (a nested untracked dir artifact) — unrelated to this plan.

**`firestarter_app`:**
```
 M .gitignore
?? .coverage
?? .planning/config.json
?? SECURITY.md
?? write_test_port.sh
```
Pre-existing, known dirt — matches the phase's documented baseline exactly.

**`/workspaces` (meta):**
```
 M .planning/config.json
 M firestarter
 M firestarter_app
?? .planning/graphs/
?? .planning/notes/bus-config-mask-model.md
?? .planning/notes/dev-test-unknown-chip-fail-fast.md
?? .planning/phases/107-.../107-RESEARCH.md
?? .planning/phases/108-.../108-PATTERNS.md
?? .planning/phases/108-.../108-RESEARCH.md
?? .planning/phases/109-.../109-PATTERNS.md
?? .planning/phases/119-.../119-PATTERNS.md
?? .planning/seeds/27c-algorithm-fidelity-param-table-refactor.md
?? .planning/seeds/bus-config-clean-redesign.md
?? .planning/seeds/db-numeric-values-simplification.md
?? W29C040.bin
?? chip-test/
?? firestarter_app_py32/
?? firestarter_py32_ci/
?? graphify-out/
```
The `M firestarter` / `M firestarter_app` gitlink lines are the expected consequence of each
submodule's checked-out HEAD (`48c36e5`/`c3c9424`) differing from the committed pinned pointer
(`0048b3d`/`96e0622`, item 9 above) — not new damage, and not staged. `.planning/config.json` is
the documented pre-existing modification, left uncommitted per standing instruction (do not
iterate `planning.sub_repos`, which lists four repos, two of them v1.29 PY32 scratch repos outside
this milestone). This snapshot is recorded so a later cleanliness assertion in this phase cannot
mistake this pre-existing dirt for its own damage.

### No mutation occurred

Confirmed after every read-only command above: `git -C firestarter rev-parse HEAD` still
`48c36e5…`; `git -C firestarter_app rev-parse HEAD` still `c3c9424…`; both
`rev-parse --abbrev-ref HEAD` still report the v1.22 branch; `git -C firestarter_app log
origin/beta -1 --format=%H` still resolves to `1bb5599…`, the exact value fetched above — nothing
was pushed to `beta` by this measurement pass.

### ⚠ Divergence from 122-RESEARCH.md

**None.** Every measured value in items 1–10 above matches RESEARCH's recorded value exactly —
branch tips, `origin/beta` tips, ahead/behind counts, merge-base/fork-point coincidence, version
strings, tag ceilings, the firmware zero-conflict/app two-conflict split, the 60/77 superset proof,
the gitlink baseline, and the documented dirt. `origin/beta` has not moved since RESEARCH was
written (~2026-07-30, within its stated ~2026-08-02 validity window). The wave-2 merge plan
(122-03) rests on an unchanged foundation.

---

## The decision (CLOSE-03, D-05)

**Verdict: ACCEPT the auto-fire — the merge IS the b14 cut.**

Both repos carry `on: push: branches: [beta]` with auto-increment driven by a git-tag scan
(`.github/scripts/update_version.py` → `compute_beta_version()` → `_git_tag_scan_fallback`), and
both sit at `3.0.0b13` (confirmed live, item 6 above) with `3.0.0b14` absent from both tag lists.
So the outbound `--no-ff` merge push to `beta`, once made, cuts the next beta by itself in both
repos — no separate cut step is needed or wanted.

### The three options, all recorded (CLOSE-03 asks for accept/avoid/cleanup, not merely a plan)

| Option | Disposition | Why |
|---|---|---|
| **ACCEPT** | **CHOSEN** | Both workflows fire unconditionally on a `beta` push carrying non-ignored paths (`paths-ignore` cannot suppress either: the app merge carries 42 non-ignored paths under `firestarter/*.py`, `pyproject.toml`, `tests/**`; the firmware merge carries `src/`, `include/`, `test/`, `platformio.ini`, `tools/`). This is the *"do the cut FROM beta so the merge IS the cut"* option the v1.21 post-mortem named. |
| **AVOID** | **DECLINED** | A `workflow_dispatch` cut from the branch with an explicit `-f beta_version=3.0.0b14`, plus temporarily disabling `push: beta` in both repos' workflow YAMLs, means two repos of trigger edits and a forgotten re-enable silently kills every future beta cut. **No workflow trigger is edited by this phase, and `paths-ignore` is not weakened, in either repo.** |
| **CLEANUP** | **DECLINED** | The stray `3.0.0b12` prereleases **stay public** in both repos. They have been public for roughly three days and may already be installed; firmware b12 is byte-identical to b11, and app b12 was the v1.21 close artifact. Deleting a published artifact is an operator-driven outward-facing act, not close work. **No `--force` push, no history rewrite, and no deletion of any published artifact occurs in this phase.** |

### The accepted sequence, each step naming its owning plan and the CONTEXT constraint it satisfies

1. **This decision recorded and committed** (this plan, 122-02) — constraint 1 (CLOSE-03's literal
   text: the decision exists and precedes any push).
2. **`beta` → branch inbound merge**, with the two-file whole-file `--ours` resolution on
   `firestarter/submit.py` and `tests/test_submit.py` (plan 122-03) — D-06. Hunk-level resolution
   is forbidden (C-12): hunks 3 and 4 of `submit.py`'s conflict sandwich a shared region HEAD needs
   *twice* (two distinct `submit_via_browser(` call sites), so a textual "ours" on those hunks
   alone would leave a dangling `elif url:` bound to the wrong `if` — code that compiles and may
   even pass. The mandated proof is `git diff HEAD -- firestarter/submit.py tests/test_submit.py`
   returning empty after `git checkout --ours -- <both paths>`.
3. **The eleven-row (nine-row cross-repo gate plus both full suites plus CLOSE-01's four
   mechanisms) non-regression sweep run on the merged tree** (plan 122-04) — constraints 2 and 6.
   The gate must prove itself on the post-merge state, not the pre-merge branch — otherwise `beta`
   would see an unproven intermediate state.
4. **Branch → `beta` outbound `--no-ff` merge and push** (plan 122-07), letting CI cut the next
   beta and auto-commit the version-bump onto `beta` in both repos.
5. **A manual `gh workflow run publish.yml --repo henols/firestarter_app -f tag=<observed tag>`**
   for PyPI (plan 122-08) — constraint 7. The tag passed is the tag **observed** after CI cuts it,
   never assumed as `3.0.0b14` in advance.
6. **Both channels verified public** — PyPI JSON API or a clean-env install for the app, the
   GitHub prerelease + `.hex` assets for firmware (plan 122-08) — constraint 3.
7. **The D-16 blocking wording review** on the closing documentation and community replies (plan
   122-11) — constraint 4.
8. **The two `gh issue comment` calls** on `henols/firestarter_prom` #11 and #12 (plan 122-12).

### Four facts the sequence depends on

- **The observed cut tag is read, never assumed (A3).** CI producing `3.0.0b14` is *derived* from
  `update_version.py`'s live git-tag scan, not *executed* by any command in this phase. Every
  downstream step — the `publish.yml -f tag=` dispatch, both `gh release edit` calls, and the PyPI
  verification — must consume the tag actually observed after the cut, never a hardcoded
  `3.0.0b14` literal in a command to be run verbatim. (Every `3.0.0b14` reference in this document
  is inside a sentence describing what the auto-increment is *expected* to derive from the item-6
  tag-ceiling measurement — none is inside an executable command.)
- **The PyPI publish is not a side effect of the merge.** `firestarter_app/beta-release.yml`
  creates the GitHub release using `secrets.PERSONAL_ACCESS_TOKEN`; a PAT lacking `workflow` scope
  suppresses the `release.published` event that would otherwise trigger `publish.yml` — documented
  in `publish.yml`'s own in-file comment. Historical evidence (RESEARCH C-3, re-affirmed by this
  session's re-derivation of the tag ceiling): **6 of the app's 13 GitHub betas never reached PyPI**
  (b4, b5, b6, b9, b10, b12) — a 46% historical miss rate. The manual dispatch in step 5 is the
  **norm**, not a contingency plan.
- **`ci.yml` never runs on a `beta` push** (`push: branches: [main]` + `pull_request` only), and
  neither does firmware's `build.yml` (`main` only). The merge push in step 4 fires **only**
  `beta-release.yml` (app) / `beta-build.yml` (firmware). Do not wait for, or chase, `ci.yml`
  output after the push. The pre-existing `ruff check`/`ruff format` findings in `tools/` and
  `.github/scripts/` sit outside `ci.yml`'s `firestarter/ tests/` scope, are structurally invisible
  to CI, are out of this phase's scope, and are **not** to be fixed here (C-8).
- **After CI runs, local `beta` is 1 commit behind the remote in each repo**, because each
  workflow's `git-auto-commit-action` pushes the version-bump commit onto `beta`. Any later local
  operation touching `beta` must `git fetch` first. This is the exact mechanism that produced
  `a981642` (app) and `6611fba` (firmware, this session's measured `origin/beta` tip).

### Out of scope for this phase (D-07)

The **`v1.22` annotated tag** and the **meta-repo gitlink bump** both stay with
`/gsd-complete-milestone`, mirroring v1.21 exactly (Phase 115 published in-phase while tag and
final merge stayed separate). The current gitlink values — `0048b3d` (firmware) / `96e0622` (app),
one phase behind the working tips `48c36e5`/`c3c9424` — are deliberately left alone; this phase
asserts `git ls-tree HEAD firestarter firestarter_app` is **unchanged** at phase end (A5, item 9
above). Doing publish + gitlink bump + tag all in-phase, or publish + gitlink bump in-phase with
the tag deferred, were both considered and declined — both couple this phase's verification scope
to work that belongs to the milestone-close ritual.

**One further owned trade-off (D-01), named so it is not silently re-opened:** **no bench
smoke-test of the b14 install/flash path is performed in this phase.** The `pip install --pre` →
`fw -i` → one live op chain that Phase 115 existed to prove is **trusted, not re-verified**, before
either `henols/firestarter_prom` reporter is pointed at b14. This is a known, accepted gap — if a
b14 install problem surfaces downstream, this record shows it was accepted, not overlooked.

---

## Summary of what this artifact proves

1. The pre-flight evidence CLOSE-03's decision rests on was measured **live**, in this session, not
   copied from a document with a validity window — and it agrees with that document on every item.
2. The decision names all three options (accept/avoid/cleanup), which was chosen, and why the other
   two were declined, in writing.
3. Nothing has been pushed, merged, or published. Both sub-repo `HEAD`s, both `origin/beta` tips,
   and the meta repo's gitlink baseline are all unchanged from their pre-measurement values.
4. This file's own commit (recorded by `git log` immediately after this write) is the evidence that
   the decision preceded the act — the ordering CLOSE-03 requires.
