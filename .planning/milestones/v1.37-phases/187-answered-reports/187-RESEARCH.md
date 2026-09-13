# Phase 187: Answered Reports — Research

**Researched:** 2026-09-12
**Domain:** Outward-facing, operator-gated publication — three PRs to `beta`, two release cuts, six public
issue dispositions, five in-repo record repairs
**Confidence:** HIGH for everything below. Every claim carries the command that produced it. Nothing here
was taken from training memory.

> **Method note.** Every measurement in this document was taken on **2026-09-12** against the live GitHub
> API and the live working trees. Where CONTEXT.md's own `### Live upstream state` block recorded a
> different value, the difference appears under **`## Drift from CONTEXT.md`** — read that section first.
>
> All `gh` commands below were run with `XDG_CACHE_HOME` set to a writable scratch dir. All `grep`
> evidence was taken with `/usr/bin/grep` (the devcontainer's bare `grep` is ugrep and honours
> `.gitignore`).

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `187-CONTEXT.md` § Implementation Decisions. **These are the operator's calls. This
research does not re-litigate them** — it reports what is true now and what the exact mechanics are.

- **D-01:** **Phase 187 owns the merge and the cut, then posts.** Measured at discussion time:
  `git cat-file -e origin/beta:firestarter/jp5_gate.py` → *"exists on disk, but not in `origin/beta`"*;
  the app branch is **33 commits ahead** of `origin/beta`; firmware is **9 ahead**; **no v1.37 PR is open
  in any of the three repos**. REPLY-03 and REPLY-04 therefore describe code nobody can install today.
  This is Phase 152's D-04 situation exactly — which that phase called *"the load-bearing measurement of
  this whole phase"* — and it takes the same route rather than posting a reply that describes an
  intention.
  — **Reversibility:** one-way — a merge to `beta` triggers `beta-release.yml`, which publishes a
  pre-release to PyPI and GitHub Releases. A published version cannot be unpublished.

- **D-02:** **All three repositories merge: app, firmware, meta.** App is what a reporter installs
  (`jp5_gate.py`, `flash4_erase_gate.py`, the 3.11 floor). Firmware is **not** docs-only — measured,
  `src/proms/flash_5v_page.cpp` loses **52 lines** (SAFE-08's unreachable 12 V bulk-erase arm) alongside
  the re-recorded `size_baseline.json`; behaviour-neutral, because the host clears `FLAG_CAN_ERASE` for
  every `0x05` part, but it is a code edit. Meta carries `.planning/`, and D-13 below makes that merge
  load-bearing for the replies.
  — **Reversibility:** one-way — same publication reason as D-01. Two cuts fire (app + fw); meta has no
  release CI and cuts nothing.

- **D-03:** **187 ships; `/gsd-complete-milestone` afterwards is archive-only.** The three PRs and two cuts
  ARE the v1.37 ship. Close is hand-archival of `.planning/` per the standing rule that milestone close is
  never run through `milestone.complete`. **Accepted and stated:** 187's own tail (posting record,
  SUMMARY, verification) and the archive land on the milestone branch, not on `beta` — the same pattern
  v1.35's close produced. Do not "fix" this by scheduling a second meta PR unless the operator asks.

- **D-04:** **No `v1.37` tag in this phase.** Same call as v1.36 (merged to `beta` in all three repos,
  deliberately not tagged). Whether v1.37 is ever tagged stays a separate operator decision.

- **D-05:** **Versions are READ after the cut, never predicted.** Read the resulting app and firmware
  pre-release versions from `gh release list` after `beta-release.yml` has run, and name those in the
  replies. Reporters are told `pip install --pre -U firestarter`. Use `git cherry`, not SHA ancestry, to
  establish what `beta` already carries — v1.30's squashed merge already produced one `--is-ancestor`
  false negative. Re-read `origin/beta` before acting on it; local `beta` goes stale.

- **D-06:** **REPLY-07 is discharged by an existing comment; 187 posts nothing new on gh#9.**
- **D-07:** **The repair set is exactly five live sites, and the sweep stops there.** (Sites 1–5 enumerated
  in CONTEXT.md; `ROADMAP.md:967` and `:1224` explicitly NOT repaired; every hit under
  `.planning/milestones/` historical-by-intent, never repaired.)
- **D-08:** **The finding is recorded; nothing is filed.** Zero backlog items on this axis. A planner or
  executor must **NOT** file a "verify upstream claims against the live API" guard item.
- **D-09:** **One `.planning/notes/` document carries both the gh#9 finding and the phase's reply ledger.**
- **D-10:** **Concede attribution fully; keep the datasheet findings standing.** All three 2026-08-08
  datasheet findings are restated as unfixed, independent, still-open defects with measured values.
- **D-11:** **REPLY-01 is amended in-phase, because its literal wording would be an overclaim.** A fresh
  run today would still report `write BAD, verify BAD` and still file as `[dev test] w27e257 — FAIL`.
  Concede the general point; do **not** invent or imply a PASS run the tracker does not carry.
- **D-12:** **Both known caveats are carried into the re-run asks** (gh#28/#31 `FLAG_SKIP_BLANK_CHECK`
  divergence; gh#62 cross-links gh#68).
- **D-13:** **Short and plain; evidence linked, not inlined.** Links must be **commit-SHA permalinks**,
  never `blob/beta/…`, never `main`. **Sequencing consequence:** the meta merge (D-02) must land *before*
  any reply is posted, or the links 404.
- **D-14:** **Labels change deliberately, per issue, and the reply body says which label moved and why.**
  gh#23: add `cause:rig` + `needs:report`. gh#28/#31: add `needs:report`, **withhold `fix:released`**.
  gh#60/#62: labelled to match their D-15 disposition.
- **D-15:** **gh#60 closes; gh#62 stays open. gh#23, gh#28 and gh#31 stay open unconditionally.**
- **D-16:** **Per-artifact blocking operator gate; agents post.** A separate blocking checkpoint
  immediately before **each** public act. **Hard constraint:** this phase must **not** run under `--auto`
  or `--chain`. Every plan touching a public act carries `autonomous: false` *and* the phase is never
  dispatched in those modes.
- **D-17:** **REPLY-05's statement appears in every reply that asks for a re-run** — `schema_version` 2.0,
  deliberate `dedup_fingerprint` re-key.

### Claude's Discretion

- Exact prose of each reply body, subject to D-13's register and the operator gate at D-16.
- File naming inside the phase directory (`187-GH{N}-COMMENT.md` per Phase 152 is the obvious precedent).
- Which specific commit SHA each permalink pins, and how the `notes/` document is sectioned.
- Plan/wave decomposition, and where the record repairs (D-07) sit relative to the ship.

### Deferred Ideas (OUT OF SCOPE)

- **Answer gh#65 (`MX27C4000`) and gh#66 (`MBM27C4001`).** Their own phase's work.
- **gh#21 (`at28c256`, `needs:report`)** — still awaiting a fresh run from AndersBNielsen. Not touched here.
- **Detect a mis-wired VPP at the socket.** Not filed as a backlog item under D-08's discipline.
- **Fix the three standing datasheet defects.** All three restated in the replies as open; none fixed here.
- **The `0x05` software chip-erase** — backlog **999.63**. Already filed; not this phase.

</user_constraints>

---

<phase_requirements>

## Phase Requirements

| ID | Description (REQUIREMENTS.md:103-119) | Research Support |
|----|---------------------------------------|------------------|
| REPLY-01 | gh#23 receives a reply naming what v1.36's fault-attribution work changed and what a fresh run would now show, and acknowledging that the reporter's diagnosis — a rig fault reported as a chip verdict — was correct. | §4 verifies D-11's overclaim finding literally: `chip_test.py:2599`, `submit.py:149-172`, `diagnostic_report.py:56-68`. §3 supplies the unfixed `vpp_mv=13500`. §8 confirms `cause:rig` and `needs:report` exist. |
| REPLY-02 | gh#28 and gh#31 each receive a reply naming the v1.36 changes that bear on them and requesting an attributable re-run. | §3 supplies both parts' unfixed measured values and `type=UV-EPROM`. §9 verifies the folded-todo `FLAG_SKIP_BLANK_CHECK` divergence at `chip_test.py:3290`. |
| REPLY-03 | gh#62 receives the answer this milestone produces: why the refusal exists, what changed, and — explicitly — that re-running under another chip's identity with `--force` is not a safe workaround. | §9 quotes the verbatim REPLY-03 source paragraph from `ae29f2008-classification-verdict.md:77-113` and the 999.63 boot-block caveat at `:198-211`. §2 confirms gh#68 is open and names AE29F2008. |
| REPLY-04 | gh#60 receives a reply confirming the hazard from the project's own schematic record and stating what the gate does and does not do (it warns; it cannot detect the jumper). | §9 quotes `jumper-display-ground-truth.md:170-196` and `jp5_gate.hazard_text` at `jp5_gate.py:70-81`. **§7 carries a hard blocker: the version of that note on `origin/beta` does not contain the gh#60 section.** |
| REPLY-05 | Every reply that asks for a re-run states `schema_version` 2.0 and the deliberate `dedup_fingerprint` re-key. | §4 verifies `SCHEMA_VERSION = "2.0"` (`diagnostic_report.py:51`, exported `:992`) and the recorded deliberate re-key (`diagnostic_report.py:256-271`). |
| REPLY-06 | No issue is closed on our own reading. gh#23, #28, #31 stay open. | §2 confirms all three are OPEN today. This is a *do-not* requirement — the only way to fail it is to act. |
| REPLY-07 | gh#9 receives a closing reply or a close-as-done. | §2 + §6 prove the comment exists, is byte-identical to the approved body (sha256 round-trip), and that gh#9 is still pinned. **Already discharged.** §5 locates the five stale records. |

</phase_requirements>

---

## Summary

Every load-bearing measurement CONTEXT.md took at discussion time **still holds**, with three exceptions
that a planner must absorb before writing a plan (§ Drift). The release seam is exactly as D-01/D-02
describe: `jp5_gate.py` and `flash4_erase_gate.py` are absent from `origin/beta` in the app repo, the app
branch is 33 commits ahead, firmware is 9 ahead (with a real 52-line code deletion, not docs-only), meta is
174 ahead, and no v1.37 PR is open in any of the three repositories. The six issues are in exactly the
states CONTEXT.md recorded, gh#9 is still pinned, and the comment D-06 relies on is provably byte-identical
to the approved body on disk. All three datasheet defects are unfixed. D-11's overclaim finding is literally
correct against the current code.

The three drifts are: (1) the **firmware repo's release workflow is named `beta-build.yml`, not
`beta-release.yml`** — a plan that greps for the wrong filename will conclude the firmware cuts nothing;
(2) **gh#65 and gh#66 are no longer unanswered** — both received a maintainer datasheet cross-check on
2026-09-10, which changes what the one-line acknowledgement to dim20 may truthfully say; and (3) the copy
of `jumper-display-ground-truth.md` **on `origin/beta` is a 76-line stub that does not contain the gh#60
answer section REPLY-04 links** — so the meta merge is load-bearing for the *content* of an existing file,
not only for four new ones.

Two further findings are not drift but are new to this document: the working tree carries an **unintended
`config.json` sub_repos prune** plus stray untracked files that must not land in a public PR, and **`beta`
carries zero branch rules in all three repositories** — PRs to `beta` are this project's convention and
review surface, not a GitHub requirement.

**Primary recommendation:** plan the phase in four stages with a blocking operator checkpoint before each
public act — (A) tree hygiene + the five D-07 record repairs on the milestone branch; (B) three PRs to
`beta` in the order **meta → app → firmware** (meta first, so D-13's permalinks resolve the moment the
replies are drafted), each merge gated; (C) read both cut versions from `gh release list` and verify PyPI
independently; (D) draft five bodies to disk, obtain a hash-bound operator approval file, post with
`--body-file`, read each back and prove byte-identical using the exact command in §6 (the naive `gh api
--jq '.body'` comparison produces a **false mismatch** — see §6.4).

---

## Architectural Responsibility Map

This phase writes no product source. "Tier" here means which system owns the act and therefore where a
mistake becomes irreversible.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Record repairs (D-07, 5 sites) | Local git (meta milestone branch) | — | Plain file edits; fully reversible until merged. Hand-edit only — the `gsd-tools` requirements/roadmap verbs reformat the whole file. |
| Three PRs to `beta` | GitHub (3 repos) | GitHub Actions | A merge is reversible in git but **not** in its effects: CI publishes. |
| Two release cuts | GitHub Actions → GitHub Releases + PyPI | — | **Irreversible.** A published PyPI version cannot be unpublished. Fires automatically on merge; it is not a separate command. |
| Version discovery | `gh release list` (read-only) | PyPI JSON API | Read after the fact. **Never predicted** (D-05). |
| Five reply bodies | Local disk (phase dir) | — | Reversible. This is where the operator gate bites. |
| Posting the replies | GitHub Issues API | — | **Irreversible and public.** One `gh issue comment` per issue, `--body-file`, never inline text. |
| Label changes | GitHub Issues API | — | Reversible, but visible. Every label named in the reply body (D-14). |
| gh#60 close | GitHub Issues API | — | Reversible (`gh issue reopen`) but publicly visible. |
| `.planning/notes/` record (D-09) | Local git (milestone branch) | — | Written after posting; carries the permalinks and the posted comment URLs. |

---

## Standard Stack

No packages are installed by this phase. The "stack" is a fixed set of already-present CLI tools.

### Core

| Tool | Version measured | Purpose | Why standard |
|------|------------------|---------|--------------|
| `gh` (GitHub CLI) | present, authenticated as `henols` | Every public act: `pr create`, `pr merge`, `issue comment`, `issue edit`, `issue close`, `release list`, `api`, `api graphql`, `label list` | The established mechanism in both project skills and in Phases 152 and 173. `[VERIFIED: ran all of these read-only this session]` |
| `git` | present | `cherry`, `cat-file`, `ls-tree`, `diff`, `rev-parse` | `git cherry` is mandated by D-05 over `--is-ancestor`. |
| `python3` | 3.12 in devcontainer | JSON round-trip for the byte-identity proof (§6.4) | Avoids jq's trailing-newline artefact entirely. |
| `sha256sum` | present | Hash-binding the approved bodies (Phase 173 precedent) | The approval file names a sha256 per body; the same hash is re-derived from the API after posting. |

### Supporting

| Tool | Purpose | When to use |
|------|---------|-------------|
| `gh api graphql` | `pinnedIssues` read | Only to **verify** gh#9's pin is intact (D-06). No `pinIssue` mutation is needed this phase. |
| `curl` + PyPI JSON API | Independent verification that PyPI carries the cut | Phase 152 D-04's funded cost: "this project has had GitHub carrying betas past PyPI before." |

### Not applicable

No `npm install` / `pip install` step. **The Package Legitimacy Audit section is omitted: this phase
installs zero external packages.** `[VERIFIED: CONTEXT.md § Phase Boundary — "This phase writes no product
source"; confirmed by the deliverable list, which contains no dependency change]`

---

## Drift from CONTEXT.md

**Three measurements have moved, and two further facts were not in CONTEXT.md at all. Read all five.**

### DRIFT-1 — The firmware repo has **no** `beta-release.yml`. Its workflow is `beta-build.yml`.

CONTEXT.md § Integration Points says *"`beta-release.yml` fires on every merge to `beta` in both
sub-repos."* That is true for the **app** and false for the **firmware** by filename.

```
$ ls -1 /workspaces/firestarter/.github/workflows/
beta-build.yml
build.yml
py32f071.yml

$ ls -1 /workspaces/firestarter_app/.github/workflows/
beta-release.yml
ci.yml
publish.yml
release.yml
```

`beta-build.yml`'s own header reads `name: Firestarter beta pre-release build` and its trigger is
`push: branches: [beta]` plus `workflow_dispatch`. **The behaviour CONTEXT.md describes is correct — a
merge to firmware `beta` does cut a pre-release — only the filename is wrong.**

**Consequence for the planner:** any plan step, verify leg or `automated` block that greps for
`beta-release.yml` in the firmware repo will find nothing and either fail closed (wasting a cycle) or fail
open (falsely concluding no cut fires). Name `beta-build.yml` for firmware and `beta-release.yml` for the
app.

### DRIFT-2 — gh#65 and gh#66 are **no longer unanswered**.

CONTEXT.md § Deferred Ideas: *"Both filed 2026-09-09 by gh#62's own reporter, both **unanswered**, both
needing a full datasheet cross-check."* Both have since been answered.

```
$ gh issue view 65 --repo henols/firestarter_prom --json comments \
    --jq '.comments[]|{author:.author.login,at:.createdAt,url:.url}'
{"at":"2026-09-10T17:41:27Z","author":"henols",
 "url":"https://github.com/henols/firestarter_prom/issues/65#issuecomment-5622917641"}
  body begins: "### Datasheet cross-check — MX27C4000 … Macronix MX27C4000, 4M-BIT (512K x 8) CMOS
  EPROM, P/N PM00159, Rev 2.0, Feb 4 1993 … Read this first: this run never programmed a single byte."

$ gh issue view 66 --repo henols/firestarter_prom --json comments --jq '.comments[]|{…}'
{"at":"2026-09-10T17:41:30Z","author":"henols",
 "url":"https://github.com/henols/firestarter_prom/issues/66#issuecomment-5622918350"}
  body begins: "### Datasheet cross-check — MBM27C4001 … the MBM27C4001's own datasheet could not be
  obtained."
```

Both also carry cause labels applied in the same pass: gh#65 `dev-test`, `cause:harness`,
`cause:firmware`; gh#66 `dev-test`, `cause:firmware`, `cause:database`.

**Consequence for the planner:** CONTEXT.md § Specific Ideas asks for *"one line acknowledging gh#65 and
gh#66 … three are still open."* **"Three are still open" is still true** (gh#62, gh#65, gh#66 open; gh#61
closed `chip:validated`). **"Unanswered" is now false.** A body that says or implies gh#65/#66 are
unanswered would post a false statement into the public tracker, in the phase whose entire premise is not
doing that. The acknowledgement must be re-worded to something true — e.g. that gh#65 and gh#66 have had
their datasheet cross-check and remain open pending the fixes, with no timeline promised.

### DRIFT-3 — `origin/beta`'s copy of `jumper-display-ground-truth.md` is a 76-line stub without the gh#60 section.

D-13 says *"`.planning/notes/` is tracked and already present on `beta` (verified: 26 entries)."* The count
is exactly right — and misleading, because the *file* REPLY-04 links is present on `beta` in an
earlier, much shorter form.

```
$ git show origin/beta:.planning/notes/jumper-display-ground-truth.md | wc -lc
     76    4334
$ git show HEAD:.planning/notes/jumper-display-ground-truth.md | wc -lc
    279   22340

$ git show origin/beta:.planning/notes/jumper-display-ground-truth.md \
    | /usr/bin/grep -n "energize socket pin 1"
>>> ABSENT on origin/beta

$ git show HEAD:.planning/notes/jumper-display-ground-truth.md \
    | /usr/bin/grep -n "energize socket pin 1"
170:## Which operations energize socket pin 1 — the answer to gh#60
```

**Consequence for the planner:** D-13's sequencing consequence is *stronger* than CONTEXT.md states. It is
not only that four brand-new notes files are missing from `beta` — an existing, linkable filename resolves
to a document that **does not contain the section the reply cites**, which is worse than a 404 because it
looks like it worked. A permalink pinned to any SHA at or before `origin/beta`'s current tip
(`0629e4ad365a3ef8d3fde38a1e28272e3c49ef59`) is silently wrong for REPLY-04. **Every permalink must pin a
SHA at or after the meta merge commit.**

### DRIFT-4 (new; not in CONTEXT.md) — the working tree is dirty, including an unintended config prune.

```
$ cd /workspaces && git status --short
 M .planning/VALIDATED-EPROMS.md
 M .planning/config.json
 ? firestarter_app
?? anything.txt
?? tmp/

$ git diff .planning/config.json
@@ -25,9 +25,7 @@
   "planning": {
     "sub_repos": [
       "firestarter",
-      "firestarter_app",
-      "firestarter_app_py32",
-      "firestarter_py32_ci"
+      "firestarter_app"
     ]
   },
```

That `config.json` diff is the **known GSD `sub_repos` prune** (a `loop render-hooks` side effect — the
phase-plan flow calls it). It is an unintended deletion of two configured sub-repos and **must be reverted,
not committed**. `git checkout -- .planning/config.json` restores the two entries.

`anything.txt` is a 492-byte operator scratch note at the meta repo root (it begins *"If the pin maps are
wrong that must be created and soleved from the infoic.xml"*). `tmp/` is an untracked scratch directory.
**Neither may land in a public PR.** `.planning/VALIDATED-EPROMS.md` carries a +6-line uncommitted edit
that needs an explicit disposition (commit or revert) before the meta PR is opened.

The app sub-repo also carries two untracked PDFs:

```
$ git -C /workspaces/firestarter_app status --short
?? datasheets/MBM27C4000.pdf     (actually: MBM27C1001.pdf)
?? datasheets/MX27C4000.pdf
```

These are gh#65/gh#66 research material (deferred work). They must not be swept into the app PR.

> **Do NOT use `git clean -Xdf` to tidy any of this.** `.planning/state.json` and bench `.bin` files are
> gitignored in this repo and would be destroyed. Remove scratch by explicit path only.

### DRIFT-5 (new; not in CONTEXT.md) — `beta` carries **zero** branch rules in all three repos.

```
$ for R in henols/firestarter_prom henols/firestarter henols/firestarter_app; do
    gh api "repos/$R/rules/branches/beta" --jq 'length'
    gh api "repos/$R/rules/branches/main" --jq '[.[].type]'
  done
0   ["deletion","non_fast_forward","pull_request"]      # firestarter_prom
0   ["deletion","non_fast_forward","pull_request"]      # firestarter
0   ["deletion","non_fast_forward","pull_request"]      # firestarter_app
```

Each repo has exactly one active ruleset, `Protect main`, `target: branch`, `enforcement: active`.

**Consequence:** "PRs to `beta`, never direct merges" (Phase 152 D-04) is this project's **convention and
review surface**, not something GitHub enforces. A plan must therefore *choose* the PR route deliberately
and carry it as an acceptance criterion — nothing will stop a direct push to `beta`, and a direct push
would fire the same irreversible cut with no review artefact. This also means the merge step needs **no**
admin bypass and no special handling; the route is unobstructed.

---

## Finding 1 — The release seam (D-01, D-02, D-05)

### 1.1 How far ahead each repo is — `git cherry`, per D-05

All three `origin` remotes were fetched immediately before measuring (`git fetch origin`, rc=0 in each).

| Repo | Path | Branch | `origin/beta` SHA | Branch HEAD | **New (`+`)** | Equivalent (`-`) |
|---|---|---|---|---|---|---|
| meta (`firestarter_prom`) | `/workspaces` | `gsd/v1.37-operator-safety-answered-reports-claim-hygiene-activated-202` | `0629e4ad365a3ef8d3fde38a1e28272e3c49ef59` | `e7268b201efd2802befc99ab640ed21d157bb03d` | **174** | 0 |
| firmware (`firestarter`) | `/workspaces/firestarter` | `gsd/v1.37-operator-safety-answered-reports-claim-hygiene` | `3e26c1bb23e351954227ad48ad6e8f27663914f1` | `3c3c802c18896ad8d498fd8a829b11d2300a72f4` | **9** | 0 |
| app (`firestarter_app`) | `/workspaces/firestarter_app` | `gsd/v1.37-operator-safety-answered-reports-claim-hygiene` | `1efdc5769ab4c78f9237b70c6826d217673cc164` | `612aa6983e781d0d9437071da1d3daaba5e71aae` | **33** | 0 |

Command used in each:

```bash
git fetch origin
B=$(git rev-parse --abbrev-ref HEAD)
git cherry origin/beta "$B"                       # full list
git cherry origin/beta "$B" | grep -c '^+'        # new commits
git cherry origin/beta "$B" | grep -c '^-'        # already-equivalent on beta
git rev-parse origin/beta HEAD
```

**App = 33, firmware = 9 — both exactly as D-01 measured.** Meta = 174 (CONTEXT.md gave no meta figure).
**Zero `-` lines in any repo**, so no commit on any milestone branch already has an equivalent on `beta` —
there is no squash-merge ambiguity to navigate this time. `[VERIFIED: git cherry, 2026-09-12]`

### 1.2 Is any v1.37 PR open?

```bash
for R in henols/firestarter_prom henols/firestarter henols/firestarter_app; do
  gh pr list --repo $R --state open --json number,title,headRefName,baseRefName,createdAt --limit 30
done
```

| Repo | Open PRs |
|---|---|
| `firestarter_prom` | **none** (`[]`) |
| `firestarter` | **#54** — *"OLED support for the Firestarter project has been added…"*, `head: beta`, `base: beta`, created **2026-08-22** |
| `firestarter_app` | **#36** — *"[Snyk] Security upgrade zipp from 3.15.0 to 3.19.1"*, `base: main`, created **2026-02-10** |

**D-01's claim stands: no v1.37 PR is open in any of the three repos.** `[VERIFIED: gh pr list, 2026-09-12]`

**But the firmware repo is not PR-free.** `firestarter#54` is a stale external contribution
(`head: beta` → `base: beta`, i.e. from a fork's `beta`) that has been open 3 weeks. A plan that asserts
"zero open PRs" as a precondition or a verify leg **will go red on the firmware repo**. Phrase the check as
"no PR whose head is the v1.37 milestone branch", not "no open PRs". #54 is unrelated to this phase and
must not be touched.

### 1.3 D-01's specific file claim — `jp5_gate.py` on `origin/beta`

```bash
$ cd /workspaces/firestarter_app
$ git cat-file -e origin/beta:firestarter/jp5_gate.py
fatal: path 'firestarter/jp5_gate.py' exists on disk, but not in 'origin/beta'
# rc=128

$ git cat-file -e origin/beta:firestarter/flash4_erase_gate.py
fatal: path 'firestarter/flash4_erase_gate.py' exists on disk, but not in 'origin/beta'
# rc=128

$ git cat-file -e HEAD:firestarter/jp5_gate.py          # rc=0
$ git cat-file -e HEAD:firestarter/flash4_erase_gate.py # rc=0
```

**Confirmed verbatim, including the exact wording D-01 quotes.** Both gates — REPLY-04's subject and
REPLY-03's subject — are absent from what `pip install --pre firestarter` gives a reporter today.
`[VERIFIED: git cat-file, 2026-09-12]`

### 1.4 D-02's firmware claim — not docs-only

```bash
$ cd /workspaces/firestarter && git diff --stat origin/beta...HEAD
 CLAUDE.md                                          |   9 +-
 PROTOCOLS.md                                       |   9 +-
 scripts/baseline/size_baseline.json                |  25 +--
 scripts/check_erase_no_vpp.py                      |  28 +--
 src/proms/flash_5v_page.cpp                        |  52 ------
 tests/avr/test_dispatch/test_configure_memory.cpp  |   3 +-
 tests/avr/test_val_5v_page/test_val_5v_page.cpp    |  66 ++++---
 tests/fixtures/captured_build_v185_leonardo.log    |  91 ++++++++++
 tests/fixtures/captured_build_v185_uno.log         |  91 ++++++++++
 tests/fixtures/captured_build_v185_uno328pb.log    |  91 ++++++++++
 tests/fixtures/captured_test_native_nodevtools_summary.log | 36 ++--
 tests/fixtures/captured_test_native_summary.log    |  36 ++--
 tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp |  12 +-
 tests/fixtures/planted_size_baseline_flash_regression_v185.log | 91 +++++
 tests/test_check_size_baseline.py                  | 189 ++++++++---------
 15 files changed, 582 insertions(+), 247 deletions(-)

$ git diff --numstat origin/beta...HEAD -- src/proms/flash_5v_page.cpp
0	52	src/proms/flash_5v_page.cpp
```

**Exactly as D-02 states: `src/proms/flash_5v_page.cpp` is a pure 52-line deletion (0 added), and
`scripts/baseline/size_baseline.json` is re-recorded. The firmware delta is NOT docs-only** — it carries
a C++ source deletion, a Python script change, AVR test changes, and a new `captured_build_v185_*` fixture
family (the CLAIM-05 fixture severance). `[VERIFIED: git diff --stat / --numstat, 2026-09-12]`

### 1.5 What each repo's CI does on a merge to `beta`

| Repo | Workflow | Trigger | What it produces | Where it publishes |
|---|---|---|---|---|
| `firestarter_app` | `.github/workflows/beta-release.yml`<br>*"Create a new beta pre-release"* | `push: branches: [beta]`, `workflow_dispatch` | PEP 440 pre-release, computed by `.github/scripts/update_version.py` | **GitHub Releases** (`softprops/action-gh-release@v2`, `prerelease: true`, `make_latest: false`) **and PyPI** (the `pypi` job calls `publish.yml` directly via `uses:` + `secrets: inherit`) |
| `firestarter` | `.github/workflows/**beta-build.yml**`<br>*"Firestarter beta pre-release build"* | `push: branches: [beta]`, `workflow_dispatch` (with a `rehearsal` boolean) | PEP 440 pre-release compiled into `include/version.h`, plus `.hex` assets for uno / uno328pb / leonardo (+ optional py32f071) | **GitHub Releases only.** No PyPI step; uses the built-in `GITHUB_TOKEN`. |
| `firestarter_prom` (meta) | **none** | — | — | — |

Meta has no release CI, confirmed twice:

```bash
$ cd /workspaces && ls -1 .github/workflows/
ls: cannot access '.github/workflows/': No such file or directory

$ git ls-files .github
.github/CONTRIBUTING.md
.github/ISSUE_TEMPLATE/bug-report.yml
.github/ISSUE_TEMPLATE/config.yml
.github/ISSUE_TEMPLATE/dev-test-report.md
.github/ISSUE_TEMPLATE/feature-request.yml
```

**D-02's "meta has no release CI and cuts nothing" is confirmed: the meta repo has no workflows directory
at all.** `[VERIFIED: ls + git ls-files, 2026-09-12]`

**Both workflows deliberately have no `paths-ignore` filter.** Each carries a long header comment
explaining that the filter was removed because a docs-only merge that bumped no version left the published
beta not corresponding to the beta branch. **Every merge to `beta` cuts, including a docs-only one.** The
firmware header adds the reason it matters more there: `FW_VERSION` is compiled in from
`include/version.h`, so a skipped bump would ship a binary that misreports its own version.

**No publish loop:** both use `stefanzweifel/git-auto-commit-action@v5` with the default `GITHUB_TOKEN`,
and pushes made with `GITHUB_TOKEN` do not trigger workflow runs. Both headers record this as measured
empirically, not reasoned.

### 1.6 How long a cut takes — measured, with its variance

```bash
gh run list --repo henols/firestarter_app --workflow beta-release.yml --limit 5 \
  --json databaseId,conclusion,createdAt,updatedAt,headBranch,displayTitle
gh run list --repo henols/firestarter  --workflow beta-build.yml    --limit 5 --json …
```

| Repo | Run | Trigger | Start → End | Duration | Conclusion |
|---|---|---|---|---|---|
| app | 34391909769 | Merge PR #61 (v1.36) | 18:54:56 → 18:59:49 | **4m53s** | success |
| app | 34350398177 | Merge PR #60 (hotfix) | 12:19:57 → 12:23:33 | 3m36s | success |
| app | 33653368797 | Merge PR #58 (v1.35) | 16:11:30 → 16:15:11 | 3m41s | success |
| fw | 34391938385 | Merge PR #60 (v1.36) | 18:55:14 → 18:58:45 | 3m31s | success |
| fw | 33653360056 | Merge PR #59 (v1.35) | 16:11:25 → 17:21:46 | **70m21s** | success |
| fw | 33446931934 | Merge PR #57 | 22:35:43 → 22:47:31 | 11m48s | success |

**Plan for ~4 minutes and be prepared for an hour.** The firmware build is the variable one (PlatformIO
cold cache, three AVR targets plus an ARM build). A plan step that polls with a short hard timeout will
report a false failure. Poll with `gh run list --workflow … --limit 1 --json status,conclusion` until
`status == "completed"`, with no wall-clock deadline shorter than 90 minutes.

### 1.7 How the version is produced — mechanism only, never predicted (D-05)

Both repos use `.github/scripts/update_version.py`. Its beta path:

```
$ /usr/bin/grep -n "def \|git tag\|b{\|beta" \
    /workspaces/firestarter_app/.github/scripts/update_version.py
50:def is_beta_mode(args) -> bool:
52:    """Return True when script is invoked in a beta-branch context."""
54:    if os.environ.get("GITHUB_REF") == "refs/heads/beta":
61:def _git_tag_scan_fallback(base: str) -> str:
62:    """Scan git tags for highest bN on this base; emit b(N+1) or b1."""
78:    return f"{base}b{n}"
81:def compute_beta_version(major, minor, patch):
```

**Mechanism:** the script detects beta mode from `GITHUB_REF == refs/heads/beta` (or an explicit
`BETA_VERSION` / `--beta`), scans existing git tags for the highest `bN` on the current base, and emits
`b(N+1)`. The workflow then auto-commits the bumped version file back onto `beta` and tags the release at
the **post-auto-commit** SHA (both workflows resolve a `release_target` SHA explicitly for this reason).

**Read the result, never compute it:**

```bash
gh release list --repo henols/firestarter_app --limit 3
gh release list --repo henols/firestarter    --limit 3
```

**Current published state, for orientation only — this is what exists BEFORE the cut, and naming it in a
reply would be naming the wrong version:**

| Repo | Latest pre-release | Published |
|---|---|---|
| `firestarter_app` | `3.0.0b38` | 2026-09-09T18:59:10Z |
| `firestarter` | `3.0.0b26` | 2026-09-09T18:58:36Z |

PyPI independent check (Phase 152 D-04's funded cost — "this project has had GitHub carrying betas past
PyPI before"):

```bash
$ curl -s https://pypi.org/pypi/firestarter/json | python3 -c \
  "import json,sys; d=json.load(sys.stdin); rs=sorted(d['releases']);
   print('latest stable:',d['info']['version']); print('recent:',rs[-4:])"
latest stable: 2.0.7
recent: ['3.0.0b35', '3.0.0b36', '3.0.0b37', '3.0.0b38']
```

**GitHub and PyPI are currently in sync at `3.0.0b38`.** And note why D-05's install instruction is
`pip install --pre -U firestarter`: PyPI's *latest stable* is `2.0.7`, so a plain `pip install firestarter`
gives a reporter a 2.x host that none of this milestone's work is in.

### 1.8 Gitlinks — the meta PR carries submodule pointers

```bash
$ cd /workspaces
$ git ls-tree HEAD firestarter firestarter_app
160000 commit 3c3c802c18896ad8d498fd8a829b11d2300a72f4	firestarter
160000 commit 612aa6983e781d0d9437071da1d3daaba5e71aae	firestarter_app

$ git submodule status
 3c3c802c18896ad8d498fd8a829b11d2300a72f4 firestarter (v1.23-190-g3c3c802)
 612aa6983e781d0d9437071da1d3daaba5e71aae firestarter_app (v1.23-345-g612aa69)

$ git ls-tree origin/beta firestarter firestarter_app
160000 commit c14f1913d85230a0a82642da6c3c8f252f73db87	firestarter
160000 commit 1a8d27231c86b428fd386550f42b074f24573eb0	firestarter_app
```

Meta HEAD's gitlinks point **exactly** at the two sub-repo milestone-branch tips — they are in sync, and no
gitlink advance is owed before the meta PR.

The gitlinks on `origin/beta` are each **2 commits behind** their sub-repo's `origin/beta`:

```bash
$ git -C firestarter rev-list --count c14f1913..origin/beta        # 2
$ git -C firestarter_app rev-list --count 1a8d2723..origin/beta    # 2
```

Those two commits per repo are the v1.36 merge commit plus CI's auto version-bump commit. **This is the
structural reason meta's gitlinks can never point at a post-cut `beta` tip without a second meta commit:
the bump commit does not exist until after the merge.** A planner should expect the meta PR's gitlinks to
name the milestone-branch tips (as they do now) and treat that as correct and precedented, not as drift.

---

## Finding 2 — Live issue state (all eight issues)

Single command shape used for each:

```bash
gh issue view <N> --repo henols/firestarter_prom \
  --json number,title,state,stateReason,labels,comments,createdAt,updatedAt,author \
  --jq '{n:.number,title:.title,state:.state,reason:.stateReason,author:.author.login,
         created:.createdAt,updated:.updatedAt,labels:[.labels[].name],
         ncomments:(.comments|length),
         last_comment:(.comments[-1]|{author:.author.login,at:.createdAt,url:.url})}'
```

| # | Title | State | Reason | Labels (live) | #cmt | Last comment (author, date) |
|---|---|---|---|---|---|---|
| **23** | `[dev test] w27e257 — FAIL (7a89fcea856a)` | **OPEN** | — | `dev-test`, `cause:database` | 3 | AndersBNielsen, **2026-08-09T09:59:11Z** ([#issuecomment-5230919008](https://github.com/henols/firestarter_prom/issues/23#issuecomment-5230919008)) |
| **28** | `[dev test] m27c512 — FAIL (31547956e56b)` | **OPEN** | — | `dev-test`, `cause:harness` | 4 | AndersBNielsen, **2026-08-09T09:57:29Z** ([…5230913040](https://github.com/henols/firestarter_prom/issues/28#issuecomment-5230913040)) |
| **31** | `[dev test] m27c1001 — INCONCLUSIVE (d8771536cb43)` | **OPEN** | — | `dev-test`, `cause:harness`, `cause:database` | 2 | AndersBNielsen, **2026-08-09T09:56:21Z** ([…5230908888](https://github.com/henols/firestarter_prom/issues/31#issuecomment-5230908888)) |
| **60** | `[Feature Request] Warning about JP5 for 8MBit EPROMs` | **OPEN** | — | `enhancement` | **0** | — (author AstoriaFloyd, filed 2026-09-04) |
| **62** | `Unable to erase AE29F2008` | **OPEN** | — | **none** | **0** | — (author dim20, filed 2026-09-09T16:18:27Z) |
| **9** | `Repository Structure and Contribution Guide` | **OPEN** | — | none | 1 | henols, **2026-09-02T14:50:37Z** ([#issuecomment-5511487546](https://github.com/henols/firestarter_prom/issues/9#issuecomment-5511487546)) |
| **61** | `[dev test] AE29F2008 — PASS (d8fb2b626af1)` | **CLOSED** | `COMPLETED` | `dev-test`, `chip:validated` | 1 | henols, 2026-09-10T17:41:42Z |
| **68** | `Protocol 0x05: partial or unaligned writes silently erase the rest of the touched page and report success` | **OPEN** | — | `bug`, `cause:firmware` | 0 | — (author henols, filed 2026-09-11T13:27:58Z) |

**Every row matches CONTEXT.md's `### Live upstream state` block.** The reporters' last comments are all
still 2026-08-09, all three still disputing the triage, and none of the six has moved.

Notable specifics:

- **gh#62 carries ZERO labels.** D-14's "gh#60 / gh#62 — labelled to match their disposition under D-15"
  therefore means *adding the first labels this issue has ever had*, not moving one. `enhancement` is the
  only label gh#60 carries.
- **gh#24 — the folded w27e257 sibling — carries no labels at all** and is `CLOSED`/`COMPLETED`:
  `{"l":[],"n":24,"r":"COMPLETED","s":"CLOSED","t":"[dev test] w27e257 — FAIL (3870f9b5f6ca)"}`. It has no
  `fixed:superseded`. Not in scope; noted so a planner does not mistake its absence for a discrepancy.

### 2.1 gh#9 is still pinned

```bash
$ gh api graphql -f query='{ repository(owner:"henols", name:"firestarter_prom"){
    pinnedIssues(first:10){ totalCount nodes { issue { number title state } } } } }'
{"data":{"repository":{"pinnedIssues":{"totalCount":1,
  "nodes":[{"issue":{"number":9,"title":"Repository Structure and Contribution Guide","state":"OPEN"}}]}}}}
```

**`totalCount: 1`, naming issue 9, state OPEN. D-06's "the pin is live" holds.** `[VERIFIED: gh api
graphql, 2026-09-12]` No mutation is needed this phase — this is a read-only confirmation.

### 2.2 `#issuecomment-5511487546` exists and is byte-identical to the approved body

```bash
$ gh api repos/henols/firestarter_prom/issues/comments/5511487546 \
    --jq '{id:.id,user:.user.login,created:.created_at,updated:.updated_at,len:(.body|length)}'
{"created":"2026-09-02T14:50:37Z","id":5511487546,"updated":"2026-09-02T14:50:37Z",
 "user":"henols","len":1336}
```

`created_at == updated_at` — the comment has **never been edited** since it was posted.

Byte-identity proof against the on-disk approved body:

```bash
$ F=.planning/milestones/v1.35-phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/bodies/173-gh9.md
$ gh api repos/henols/firestarter_prom/issues/comments/5511487546 > /tmp/comment.json
$ python3 -c "
import json,hashlib
b=json.load(open('/tmp/comment.json'))['body'].encode()
d=open('$F','rb').read()
print('api bytes:',len(b),'disk bytes:',len(d))
print('api sha256:',hashlib.sha256(b).hexdigest())
print('disk sha256:',hashlib.sha256(d).hexdigest())
print('IDENTICAL' if b==d else 'DIFFER')"
api bytes: 1348 disk bytes: 1348
api sha256: 0db65fe80d52497b0f78fcb281bd96d8ae5d62e47947fdb6cd5d4789b0c6fe95
disk sha256: 0db65fe80d52497b0f78fcb281bd96d8ae5d62e47947fdb6cd5d4789b0c6fe95
IDENTICAL
```

And that sha256 is **the same value Phase 173's own approval file recorded before posting**:

```
$ cat …/173-07-operator-approval.txt | tail -1
sha256(evidence/bodies/173-gh9.md) = 0db65fe80d52497b0f78fcb281bd96d8ae5d62e47947fdb6cd5d4789b0c6fe95
```

**A complete round trip: operator-approved body → posted → read back from the API ten days later →
identical hash. D-06 is fully verified.** `[VERIFIED: gh api + python3 hashlib + on-disk approval file,
2026-09-12]`

### 2.3 gh#62's cross-links: gh#61, gh#67, gh#68

`gh#68` (open, `bug`, `cause:firmware`, filed by henols 2026-09-11) names AE29F2008 explicitly in its
first paragraph, confirming D-12:

> *"This affects **all 27** protocol-`0x05` parts, including the validated ones (w29c020, w29c040,
> sst39sf020, AE29F2008). It is independent of #67, which is about the page size being *wrong* on 9 of
> them; this one bites even when the page size is right."*

**gh#67 also exists and CONTEXT.md does not mention it:** *"Protocol 0x05: firmware-derived page size is
smaller than the physical page on 9 parts — contiguous writes lose every other 64-byte run"*, OPEN, `bug`,
`cause:firmware`. It is gh#68's sibling and is cited inside gh#68's own body. **D-12 fences the gh#62
cross-link at gh#68 only; this research does not propose widening it** — but a planner should know gh#67
exists so a reply body does not accidentally describe gh#68's scope as covering the page-size defect too.

---

## Finding 3 — The three standing datasheet defects (D-10): all three still unfixed

Measured against the **shipped** database file in the app working tree,
`firestarter_app/firestarter/data/chip_database.json` (431,814 bytes, mtime 2026-09-10).

> **Database keys are comma-joined alias lists.** `M27C512` and `M27C1001` are not findable by exact
> `part_number` match — they live under vendor `ST` as `"M27C512,M27V512,M27W512"` and
> `"M27C1001,M27V101,M27W101"`. A plan verify leg that greps for the bare part number will find nothing
> and fail open.

| Chip | DB key | 2026-08-08 claim | **Measured 2026-09-12** | Status |
|---|---|---|---|---|
| `WINBOND W27E257` | `WINBOND` / `W27E257` | `vpp` 13.5 V should be 12 V | `"vpp_mv": 13500` | **UNFIXED** |
| `ST M27C512` | `ST` / `M27C512,M27V512,M27W512` | `vdd` 6.5 V vs `vcc` 5 V, nothing applies it | `"vdd_mv": 6500`, `"vcc_mv": 5000` | **UNFIXED** |
| `ST M27C1001` | `ST` / `M27C1001,M27V101,M27W101` | pin 30 maps A17, datasheet says NC | `"pinout": "DIP32_27C020"` | **UNFIXED** |

Verbatim extracts:

```json
// WINBOND / W27E257
"electrical": { "pin_count": 28, "size_bytes": 32768, "type": "EEPROM",
                "vcc_mv": 5000, "vdd_mv": 5000, "vpp_mv": 13500 },
"pinout": "DIP28_27256",
"programming": { "algorithm": 7, "chip_id_value": "0x0000da02", "pulse_duration_us": 100, … }

// ST / M27C512,M27V512,M27W512
"electrical": { "pin_count": 28, "size_bytes": 65536, "type": "UV-EPROM",
                "vcc_mv": 5000, "vdd_mv": 6500, "vpp_mv": 13000 },
"pinout": "DIP28_27512",
"programming": { "algorithm": 7, "chip_id_value": "0x0000203d", … }

// ST / M27C1001,M27V101,M27W101
"electrical": { "pin_count": 32, "size_bytes": 131072, "type": "UV-EPROM",
                "vcc_mv": 5000, "vdd_mv": 6500, "vpp_mv": 13000 },
"pinout": "DIP32_27C020",
"programming": { "algorithm": 8, "chip_id_value": "0x00002005", … }
```

### 3.1 The `type` split D-10 relies on — confirmed

| Chip | `electrical.type` | Does Phase 179's UV slot work apply? |
|---|---|---|
| `W27E257` | **`EEPROM`** | **NO** — Phase 179's UV slot work does not apply to gh#23 |
| `M27C512` | **`UV-EPROM`** | **YES** |
| `M27C1001` | **`UV-EPROM`** | **YES** |

**D-10's split is exactly right.** `[VERIFIED: json parse of shipped chip_database.json, 2026-09-12]`

### 3.2 The v1.37 delta DOES touch the database — but not these three rows

```bash
$ cd /workspaces/firestarter_app && git diff --stat origin/beta...HEAD -- firestarter/data/
 firestarter/data/chip_database.json | 16 ++++++++--------
 firestarter/data/pinouts.json       | 11 +++++++++++
 2 files changed, 19 insertions(+), 8 deletions(-)
```

The v1.37 delta changes 8 DB rows and adds a pin map — that is Phase 182's SAFE-01 pin-map correction (the
8 Mbit VPP-on-pin-1 parts). **None of the three D-10 rows is among them**: all three carry their
pre-existing values in the working tree at HEAD, which is what will be on `beta` after the merge. A reply
naming these measured values will still be true after the cut.

### 3.3 Standing constraint

`chip_database.json` is **GENERATED**. Any fix belongs in `build_db.py`'s decode function, never in the
JSON. This is milestone decision **D-6** (`REQUIREMENTS.md:27`) and a standing project rule. **No plan may
propose editing the JSON, and no reply may imply a hand-edit is the fix.** The deferred-ideas entry states
the correct locus explicitly: *"`W27E257` `vpp_mv` 13500→12000 (in `build_db.py`'s decode, never in the
generated JSON)."*

---

## Finding 4 — D-11's evidence (REPLY-01's amendment) verifies literally

D-11 asserts that a fresh gh#23 run **would still** report `write BAD, verify BAD` and still file as
`[dev test] w27e257 — FAIL`. REPLY-01's text depends on that being literally true. It is.

### 4.1 The status-axis trigger — `chip_test.py:2599` still resolves

```bash
$ /usr/bin/grep -n "except (SerialError, HardwareOperationError)" \
    /workspaces/firestarter_app/firestarter/chip_test.py
2599:    except (SerialError, HardwareOperationError) as exc:
```

**Exact line-number match with CONTEXT.md's citation.** The surrounding block (`chip_test.py:2580-2612`):

```python
2580    ProgrammerNotFoundError,
2581    FirmwareOutdatedError,
2582    HardwareRevisionUnsupportedError,
2583 ):
2584    # These SerialError subclasses are run-fatal host-setup conditions …
2585    # … This clause MUST precede the (SerialError, HardwareOperationError)
2586    # clause below …
2598    raise
2599 except (SerialError, HardwareOperationError) as exc:
2600    return StepResult(op=step.op, verdict=VERDICT_SKIPPED,
2602                      status=STATUS_ERROR, reason=str(exc), run_count=1)
2607 except EpromOperationError as exc:
2608    return StepResult(op=step.op, verdict=VERDICT_BAD,
2611                      reason=str(exc), error_code=exc.error_code, …)
```

CONTEXT.md's cited range `:2585-2606` is the host-setup ordering comment plus the status clause. Both
resolve. `[VERIFIED: /usr/bin/grep -n + sed, 2026-09-12]`

**The mechanism:** a gh#23-shape fault (VPP not hooked up) produces bad *data*, which raises
`EpromOperationError`, which lands at `:2607` → `verdict=VERDICT_BAD`, `status` defaulting to
`STATUS_COMPLETE`. It does **not** raise `SerialError` or `HardwareOperationError`, so `:2599`'s
`status=STATUS_ERROR` arm never fires.

### 4.2 Which means the title is still `FAIL` — `submit.py:149-172`

```python
149 def overall_verdict(results: Any) -> str:
    """FAIL-dominant title verdict … Returns `_TITLE_VERDICT_HARNESS` if any result's
       status axis reads `STATUS_ERROR` …; else `FAIL` if any step verdict is `BAD`; …"""
165     if any(getattr(r, "status", STATUS_COMPLETE) == STATUS_ERROR for r in results):
166         return _TITLE_VERDICT_HARNESS          # "INCONCLUSIVE (harness)"
167     verdicts = {r.verdict for r in results}
168     if "BAD" in verdicts:
169         return "FAIL"
…
174 def build_title(report: Any, chip: str) -> str:
192     return f"[dev test] {name} — {verdict} ({shorthash})"
```

**With `status=COMPLETE` and `verdict=BAD`, `overall_verdict` returns `"FAIL"` and `build_title` produces
`[dev test] w27e257 — FAIL (<12-hex>)`. D-11's claim is verified verbatim.**

### 4.3 The disclosure — `diagnostic_report.py:56-68`

```bash
$ /usr/bin/grep -n "_RAIL_READING_DISCLOSURE\|SCHEMA_VERSION = \|rail_reading_disclosure" \
    /workspaces/firestarter_app/firestarter/diagnostic_report.py
51:SCHEMA_VERSION = "2.0"  # baked into to_dict() output
61:`rail_reading_disclosure`, and read by `render()` off the exported dict --
65:_RAIL_READING_DISCLOSURE = (
1006:            "rail_reading_disclosure": _RAIL_READING_DISCLOSURE,
1139:        table.add_row("rail reading", d["rail_reading_disclosure"])
```

The docstring (`:56-63`) and the constant (`:65-68`):

```python
56 """ATTR-06 (D-14): the sentence the report says about its own rail readings.
57 `hw_read_voltage` energizes and measures the boost-regulator rail only -- it
58 asserts no socket-routing bit, so a rig with VPP unhooked still reads a
59 healthy rail. …"""
65 _RAIL_READING_DISCLOSURE = (
66     "vpp/vpe readings measure the regulator rail only -- they do not show "
67     "whether the eprom socket is connected (advisory)"
68 )
```

**CONTEXT.md's citation `:55-68` is accurate to within one line** (the docstring opens at 56, not 55). The
sentence D-11 quotes — *"a rig with VPP unhooked still reads a healthy rail"* — is present verbatim at
`:58-59`. The disclosure is exported at `:1006` and rendered at `:1139`.

**REPLY-01 may therefore say, truthfully:** v1.36 did not make the tool able to see an unhooked VPP — it
cannot; Phase 181 deleted the misleading `voltage.vpp_mv`/`vpe_mv` from the report; Phase 178 added
`rail_reading_disclosure`, whose exact text is the two-line string above.

### 4.4 D-17 / REPLY-05: `schema_version` 2.0 and the deliberate re-key

```bash
$ /usr/bin/grep -n '"schema_version"' /workspaces/firestarter_app/firestarter/diagnostic_report.py
992:            "schema_version": SCHEMA_VERSION,
```

`SCHEMA_VERSION = "2.0"` at `:51`, exported at `:992`. **Confirmed.**

The deliberate re-key is recorded in-code at `diagnostic_report.py:256-271`, immediately above
`def dedup_fingerprint`:

> *"The SDP leg's six new steps … necessarily **re-key every one of the 43 measured ALLOW chips** through
> the hashed `op=verdict:cls` triples below — b14/b15-era reports stop grouping with v1.30-era ones and
> their accumulated N>=2 promotion counts reset; gh#20's orphaned id `00e121446ceb` is a recorded
> instance."*

The function's own docstring adds the `coverage_tag` discriminator and states the design intent:

> *"Hashes chip name, plus each step's op / verdict / fingerprint classification, plus `repeat_policy_tag`
> and `coverage_tag` when non-empty. It deliberately EXCLUDES every volatile field … so a clean re-test of
> the same chip with the same outcome shape dedups to the SAME id."*

**REPLY-05's mandated sentence is factually supported by the code, not just by the roadmap.** The re-key
was deliberate, documented at the site, and the consequence (a fresh run will not group with the old one)
follows from the docstring's own description. `[VERIFIED: source read of diagnostic_report.py, 2026-09-12]`

### 4.5 D-11's care note — no `w27e257` PASS exists anywhere

```bash
$ gh issue list --repo henols/firestarter_prom --state all --search "w27e257" \
    --json number,title,state --limit 20
[{"number":23,"state":"OPEN",  "title":"[dev test] w27e257 — FAIL (7a89fcea856a)"},
 {"number":24,"state":"CLOSED","title":"[dev test] w27e257 — FAIL (3870f9b5f6ca)"}]
```

**Two w27e257 issues exist in the entire tracker, both FAIL. There is no PASS.** D-11's instruction —
concede the general point (a rig fault was reported as a chip verdict) and do **not** invent or imply a
PASS run — is backed by a complete tracker search. `[VERIFIED: gh issue list --search, 2026-09-12]`

---

## Finding 5 — The five record-repair sites (D-07)

**All five citations still resolve to the text D-07 says they do. No line number has shifted.**

| # | Citation | Resolves? | Verbatim text at that line |
|---|---|---|---|
| 1 | `.planning/ROADMAP.md:5409-5411` | ✅ | `5409: **Absorbed 999.16 / gh#9 remains partially owed:** [gh#9](…/issues/9)`<br>`5410: (\`Repository Structure and Contribution Guide\`) is **still OPEN**, last touched 2026-09-02. The end-state it`<br>`5411: describes is now configured, so what it needs is a closing reply or a close-as-done, not implementation.` |
| 2 | `.planning/ROADMAP.md:5424` | ✅ | `5424: - [x] Shipped as **v1.35 Phases 172–173** (closed 2026-09-02). Residuals live on as **999.46** and **999.47**; gh#9 still owes a closing reply.` |
| 3 | `.planning/ROADMAP.md:502` | ✅ | `502: 4. gh#9 carries a closing reply or is closed as done.` |
| 4 | `.planning/REQUIREMENTS.md:118` | ✅ | `118: - [ ] **REPLY-07**: gh#9 (\`Repository Structure and Contribution Guide\`) receives a closing reply or a`<br>`119:       close-as-done — the end-state it describes has been configured since v1.35 Phase 172.` |
| 5 | `.planning/REQUIREMENTS.md:217` | ✅ | `217: \| REPLY-07 \| Phase 187 \| Pending \|` |

Commands:

```bash
awk 'NR>=5405 && NR<=5430 {print NR": "$0}' .planning/ROADMAP.md
awk 'NR>=488  && NR<=510  {print NR": "$0}' .planning/ROADMAP.md
awk 'NR>=116  && NR<=120  {print NR": "$0}' .planning/REQUIREMENTS.md
awk 'NR>=211  && NR<=218  {print NR": "$0}' .planning/REQUIREMENTS.md
```

**Note on site 1:** the stale claim actually spans the whole 5409–5411 block, and the **heading itself**
(`**Absorbed 999.16 / gh#9 remains partially owed:**`, line 5409) is part of what is false. D-07's range is
correct; a repair that only rewrites line 5411 would leave the heading asserting the same falsehood.

**Note on site 4:** REPLY-07's text is a two-line wrapped bullet (`:118-119`). An amendment must handle
both lines. **Be careful with the decision-coverage gate**, which needs single-line `D-NN` labels and fails
closed on wrapped ones — that gate keys on plan files, not REQUIREMENTS.md, but the wrapping discipline is
worth carrying.

### 5.1 The two explicitly-excluded sites say exactly what D-07 claims

```
967: **Upstream action owed at close.** … [gh#9](…/issues/9) stays open as the pinned orientation
     issue describing the end state POLICY-01…03 configure.

1224: 5. The upstream replies owed on GitHub are sent or explicitly deferred with a reason: gh#7 …,
      gh#5 …, gh#9 (pinned orientation issue describing the configured end state).
```

**Both are literally true today** — gh#9 is open (§2) and pinned (§2.1). **Correctly excluded. Do not
widen into them.** `[VERIFIED: awk on ROADMAP.md, 2026-09-12]`

### 5.2 One factual error inside D-07's own fence — the exclusion *count* is wrong

D-07 says: *"Every hit under `.planning/milestones/` (**10 files**) — historical-by-intent, never
repaired."*

```bash
$ /usr/bin/grep -rn "gh#9" .planning/milestones --include=*.md -l | wc -l
33
```

**It is 33 files, not 10.**

This does **not** change the repair set: every one of those 33 is under `.planning/milestones/` and is
excluded by the same rule, and the standing project rule is that `.planning/`→`.planning/` citations are
historical-by-intent and repairing them destroys the evidence. **The fence is right; only its stated
magnitude is wrong.** A planner should not restate "10 files" in any plan, SUMMARY, or the D-09 notes
document, because that would file a fresh false measurement in the phase that exists to stop doing that.

### 5.3 Three further live (non-`milestones/`) files mention gh#9 — all three checked, none needs repair

```bash
$ /usr/bin/grep -rn "gh#9" .planning --include=*.md -l | grep -v milestones
.planning/REQUIREMENTS.md      # sites 4 & 5, in the repair set
.planning/ROADMAP.md           # sites 1-3 + the two excluded, in/out per D-07
.planning/STATE.md
.planning/v1.35/CLOSE-RECORD.md
.planning/v1.35/MIGRATION-TABLE.md
.planning/phases/187-answered-reports/187-{CONTEXT,DISCUSSION-LOG}.md
```

| File | Hit | Verdict |
|---|---|---|
| `.planning/STATE.md:11`, `:241` | Both describe *this phase's* context-gathering session and already say REPLY-07 was discharged by the 2026-09-02 comment. | **Correct. No repair.** |
| `.planning/v1.35/CLOSE-RECORD.md:178-181` | *"**gh#9 was never pinned** … `pinnedIssues` was measured empty at phase start. Plan 173-07 pinned it via GraphQL."* | **Past-tense historical account of a discovery, and accurate.** No repair — repairing it would destroy the record of the finding. |
| `.planning/v1.35/CLOSE-RECORD.md:244` | Lists the four upstream reply comment URLs including gh#9's. | **Correct. No repair.** |
| `.planning/v1.35/MIGRATION-TABLE.md:48` | *"`Contributing` was **authored from gh#9, not migrated**."* | **Unrelated to the staleness. No repair.** |
| `187-CONTEXT.md`, `187-DISCUSSION-LOG.md` | This phase's own inputs. | Not repair targets. |

**Conclusion: D-07's five-site repair set is complete and correct for the live records.** This sweep is
reported here so the planner can cite it as evidence that the fence was checked, and so it never needs
re-running. **Do not turn this into a general stale-upstream-claim hunt (D-08).**

---

## Finding 6 — Posting and verification mechanics (Phases 152 and 173)

### 6.1 What Phase 152 funded, that this phase inherits

From `.planning/milestones/v1.32-phases/152-outward-facing-close-operator-gated/152-CONTEXT.md` § D-04
(*"the load-bearing measurement of this whole phase"*), the **funded costs** a planner must budget for
explicitly:

| Cost | Phase 152's verbatim wording | Status in 2026-09 |
|---|---|---|
| PRs, not direct merges | *"**PRs to `beta`, never direct merges** — v1.31 used fw #52 / app #51 / meta #35; v1.30 used #44. Meta gets a PR too but has no release CI, so it cuts nothing."* | Still the convention; **§DRIFT-5 shows GitHub does not enforce it on `beta`** |
| Two cuts fire | *"**Two cuts fire, by design.** Every merge to `beta` triggers `beta-release.yml`. Versions are **read after the fact**, never predicted. Re-read `origin/beta`'s version before acting on it — local `beta` lags."* | Confirmed §1.5/§1.6. Firmware's file is `beta-build.yml` (DRIFT-1). |
| `git cherry` | *"**`git cherry`, not SHA ancestry** … v1.30's squashed merge already produced one `--is-ancestor` false negative."* | Applied §1.1; 0 equivalent commits this time |
| Manual dispatch is operator-only | *"**`gh workflow run` is blocked by the auto-mode classifier** — any manual PyPI dispatch is operator-only. Settings edits cannot fix it; read-only `gh run` works."* | **Still applies.** Plan no `gh workflow run` step; if PyPI needs a manual dispatch, it is an operator task. |
| CI gotchas | *"codegen drift vs ruff; `.[dev]` vs `.[test]`; PyPI needs manual dispatch. **Verify the PyPI artifacts independently of GitHub** — this project has had GitHub carrying betas past PyPI before."* | §1.7 shows the independent PyPI check; currently in sync at b38 |
| Per-artifact gate | D-03: *"A separate blocking checkpoint immediately before each post, so approval for gh#12 cannot carry to gh#11."* | This is CONTEXT.md D-16's direct precedent |

Phase 152's D-03 also records the **rejected** safer option, worth knowing because D-16 made the same
choice: *"agents-never-post with a `152-POST-COMMANDS.md` (structurally safest — the capability would be
absent rather than gated — but rejected by the operator in favour of fewer manual steps)."*

### 6.2 The Phase 173 approve-on-disk → post → read-back discipline, in full

The artifact shape (`173-UPSTREAM-REPLIES.md`) is:

1. A single review document with a **`**D-13 review status:**` line** that starts at a pending-review
   literal. Its own rule: *"Plan 173-07 is the only plan permitted to post them, and only after this status
   line reads something other than the pending-review literal it started at."*
2. Each body stored **twice**: inline in the review document, and byte-identically as its own file under
   `evidence/bodies/173-gh<n>.md`. The standalone file is *"the file plan 173-07 passes to `gh issue
   comment --body-file` unmodified, so what the operator approves here is exactly what gets posted."*
3. A **`Dispositions` table** — issue, title, disposition — written before any body.
4. A **pre-post state capture** (`evidence/173-04-issue-state-before.json`) read from the API, and re-read
   a second time at the end of drafting.
5. An **approval file** (`evidence/173-07-operator-approval.txt`) carrying an approval literal, the
   operator's name and date, the decision prose, and **a sha256 per body file**, computed over the bodies
   *as approved and as they will be posted*. The plan's own gate asserts these hashes before a single post.
6. An **after-state capture** (`evidence/173-07-issue-state-after.json`) reconciled field-by-field against
   the before-capture.
7. The review document is then flipped to `APPROVED AND POSTED` with a comment URL beside each body.

Phase 173 executed all seven in **12 minutes** (`173-07-SUMMARY.md`: started 14:44:00Z, completed
14:55:48Z, 3 tasks).

### 6.3 The exact posting command

From `173-07-post-transcript.txt` (one block per issue, verbatim):

```
Command: gh issue comment 9 --repo henols/firestarter_prom --body-file .planning/phases/173-…/evidence/bodies/173-gh9.md
Exit code: 0
Returned URL: https://github.com/henols/firestarter_prom/issues/9#issuecomment-5511487546
```

Which is the same convention both project skills mandate:

```
.claude/skills/devtest-triage/SKILL.md:345-349
  "Write the body to a file and pass `--body-file`; never interpolate report text into the command line."
  gh issue comment 21 --repo henols/firestarter_prom --body-file /tmp/comment.md

.claude/skills/devtest-rootcause/SKILL.md:336
  gh issue comment 45 --repo henols/firestarter_prom --body-file /tmp/fix.md
```

### 6.4 ⚠ How to read a comment back and prove it byte-identical — and the trap

**The naive comparison produces a FALSE MISMATCH.** Measured this session:

```bash
$ gh api repos/henols/firestarter_prom/issues/comments/5511487546 --jq '.body' > /tmp/live.md
$ diff /tmp/live.md evidence/bodies/173-gh9.md
13d12
<
# ^^ reports a spurious extra blank line — the bodies are actually identical
```

The cause: **`jq` appends its own trailing newline to raw string output.** The stored body already ends
`own.\n`; jq emits `own.\n\n`. `od -c` on the last 12 bytes of each:

```
live (via jq):  t h e i r   o w n . \n \n
disk:         space t h e i r   o w n . \n
```

**Two correct methods, both verified to produce the identical sha256 `0db65fe8…`:**

```bash
# METHOD A — shell only; strip jq's added trailing newline
gh api repos/henols/firestarter_prom/issues/comments/<ID> --jq '.body' | head -c -1 > /tmp/readback.md
cmp /tmp/readback.md <body-file> && echo "BYTE-IDENTICAL"
sha256sum /tmp/readback.md <body-file>

# METHOD B — python, no jq involved at all (recommended: no newline semantics to get wrong)
gh api repos/henols/firestarter_prom/issues/comments/<ID> > /tmp/comment.json
python3 -c "
import json,hashlib,sys
b=json.load(open('/tmp/comment.json'))['body'].encode()
d=open(sys.argv[1],'rb').read()
print('api',len(b),hashlib.sha256(b).hexdigest())
print('disk',len(d),hashlib.sha256(d).hexdigest())
sys.exit(0 if b==d else 1)" <body-file>
```

**Recommend METHOD B as the plan's verify leg**: it exits non-zero on mismatch, prints both hashes, and has
no newline-handling subtlety. A plan that writes METHOD A's `diff` without `head -c -1` will go red on a
perfectly correct post — the most expensive possible false alarm in an operator-gated phase.

**Getting the comment ID:** `gh issue comment` prints the URL, whose fragment is `#issuecomment-<ID>`.
Extract it, or re-read the last comment:

```bash
gh issue view <N> --repo henols/firestarter_prom --json comments \
  --jq '.comments[-1] | {id:(.url|split("-")|last), url:.url, at:.createdAt}'
```

### 6.5 The collateral-comment sweep — Phase 173's corrected verification

Phase 173's plan contained a **bug in its own verify script**: it asserted zero comments on every issue
outside the target set, which was never true of this repository (39 of 53 issues already carried comments).
The corrected leg, which Phase 187 should reuse, proves what the gate actually intends — that the plan
added no comment anywhere else — by listing every comment created in the posting window:

```bash
gh api repos/henols/firestarter_prom/issues/comments --paginate \
  --jq '.[] | select(.created_at >= "<WINDOW_START_ISO8601>") | {issue:(.issue_url|split("/")|last), created_at, id}'
```

Phase 173's result was exactly four rows, one each on 5, 6, 7, 9. **This is the right shape for 187's own
"no collateral post" proof.** Capture a `WINDOW_START` timestamp immediately before the first post.

### 6.6 Precedent on the meta close-tail PR — a tension worth surfacing

D-03 says the phase tail lands on the milestone branch, not `beta`, and *"Do not 'fix' this by scheduling a
second meta PR unless the operator asks."*

Measured precedent:

```bash
$ gh pr list --repo henols/firestarter_prom --state merged --base beta --limit 5 \
    --json number,title,mergedAt
{"n":64,"t":"v1.36 close tail: milestone archive and close record","merged":"2026-09-09T19:38:28Z"}
{"n":63,"t":"Milestone v1.36: `dev test` Fidelity — planning record (phases 174–181)","merged":"2026-09-09T18:55:41Z"}
{"n":59,"t":"v1.35: land the Phase 173 closing record on beta","merged":"2026-09-02T19:12:14Z"}
{"n":58,"t":"Retire wiki-check.yml and the tools/wiki checkers","merged":"2026-09-02T18:47:16Z"}
{"n":56,"t":"v1.35 close: Phases 171-173 remainder, beta lockstep cut","merged":"2026-09-02T16:11:30Z"}
```

**Both v1.35 and v1.36 did in fact open a second meta PR for the close tail** (prom#59 and prom#64). **This
research does not re-litigate D-03** — D-03's statement is that this is the operator's call and that a plan
must not schedule it unilaterally. The measurement is reported so a planner writing the SUMMARY does not
describe "tail lands on the milestone branch" as the project's invariable pattern when the last two
milestones both landed it on `beta` afterwards, by a separate operator-initiated PR. **Plan for D-03 as
written; simply do not claim the opposite is unprecedented.**

### 6.7 Merging under protection — what applies and what does not

From `.planning/notes/v135-close-procedure-under-protection.md` (113 lines, read in full):

- **A PR is the only route into `main` in all three repos; `current_user_can_bypass` is `never`.** Confirmed
  live (§DRIFT-5: `main` carries `deletion`, `non_fast_forward`, `pull_request`).
- **`beta` is in no ruleset condition in any of the three repositories** — the note says so and §DRIFT-5
  confirms it live.
- **`ship.md`'s `RANGE_BASE=$(git merge-base "${BASE_BRANCH}" HEAD)` mis-anchors on a stale local `beta`.**
  Local `beta` measured 205 commits behind `origin/beta` when the note was written. **Recreate local `beta`
  from `origin/beta` before running `/gsd-ship`.**
- **Meta's `origin/beta` tip is a merge commit with two parents**, so the close tail must be **merged**, not
  fast-forwarded, and any ancestry check must use `git cherry` (§1.1 does).
- **`git-base-branch.cjs:305` folds the resolved base branch into `protectedBranches`**, so GSD treats
  `beta` as protected while GitHub does not. Both consumers only *warn* and continue, so this cannot block
  the close — but expect the warning and do not treat it as a stop.
- **Banked evidence the PR route works:** `prom#54`, `firestarter#58`, `firestarter_app#57` all merged into
  a protected `main` on 2026-09-02 between 08:56:58Z and 08:57:06Z, after the rulesets were created.

**⚠ `.planning/config.json` sets `git.create_tag: true`, which contradicts D-04's "no `v1.37` tag".** A
`/gsd-ship` or close flow that honours `create_tag` would push a tag the operator has decided against. The
note records that *"the only `git push` in the whole `complete-milestone` tree is a **tag** push, at
`git-tag.md:26` (`git push origin v[X.Y]`)"* — i.e. the tag step is real and reachable. **The plan must
explicitly suppress or skip the tag step, or the phase will do the one publication D-04 forbids.**

---

## Finding 7 — Permalink mechanics (D-13)

### 7.1 `.planning/notes/` on `origin/beta` — 26 entries, exactly as D-13 measured

```bash
$ git ls-tree --name-only origin/beta .planning/notes/ | wc -l
26
$ git ls-tree --name-only HEAD .planning/notes/ | wc -l
30
$ comm -13 <(git ls-tree --name-only origin/beta .planning/notes/|sort) \
           <(git ls-tree --name-only HEAD .planning/notes/|sort)
.planning/notes/ae29f2008-classification-verdict.md
.planning/notes/catalog-sync-check-retirement.md
.planning/notes/dispatch-invariant-retirement-verdict.md
.planning/notes/python-floor-decision.md
```

**D-13's "26 entries" is exact.** Four new notes land with the meta merge — including
**`ae29f2008-classification-verdict.md`, which is REPLY-03's entire linked evidence.** It does not exist on
`beta` today.

Plus DRIFT-3: `jumper-display-ground-truth.md` exists on `beta` but as a 76-line stub without REPLY-04's
section.

### 7.2 The exact permalink URL shape

**Verified against the live API that a blob exists at a pinned SHA:**

```bash
$ SHA=$(git rev-parse origin/beta)        # 0629e4ad365a3ef8d3fde38a1e28272e3c49ef59
$ gh api "repos/henols/firestarter_prom/contents/.planning/notes/jumper-display-ground-truth.md?ref=$SHA" \
    --jq '{path:.path,size:.size,sha:.sha}'
{"path":".planning/notes/jumper-display-ground-truth.md",
 "sha":"2f82520ff2ebb61548b7664741c51b90c1201fd5","size":4334}
```

**URL shape:**

```
https://github.com/henols/firestarter_prom/blob/<40-char-commit-sha>/<path>#<anchor>
```

Concretely, for REPLY-04 (SHA to be replaced with the post-merge one):

```
https://github.com/henols/firestarter_prom/blob/<MERGE_SHA>/.planning/notes/jumper-display-ground-truth.md#which-operations-energize-socket-pin-1--the-answer-to-gh60
```

**Anchor derivation** (GitHub's markdown slug rule): lowercase, spaces → `-`, punctuation dropped, em-dash
dropped leaving its surrounding spaces as two hyphens. The headings available in the HEAD version:

```bash
$ /usr/bin/grep -n "^#\+ " .planning/notes/jumper-display-ground-truth.md
7:# Jumper display ground truth
170:## Which operations energize socket pin 1 — the answer to gh#60
246:### The structural remainder this gate does not cover
254:## Evidence photographs (Phase 182)
```

```bash
$ /usr/bin/grep -n "^#\+ " .planning/notes/ae29f2008-classification-verdict.md
9:## THE VERDICT
77:## WHY THE REPORTER'S `--force` ERASE WORKED, AND WHY THAT IS NOT A LICENCE
198:## Software chip-erase for the `0x05` family — recorded, backlogged, not built (D-20)
```

> **Anchor caution:** these headings contain a backtick-quoted `--force`, an em-dash, and a `#` inside
> `gh#60`. Do **not** hand-derive the slug from memory — after the meta merge, open the rendered page and
> copy the anchor GitHub actually emits (or use `gh api …/contents/...?ref=SHA` to confirm the file, then
> click the heading's own `¶` link). One wrong anchor silently lands the reader at the top of a 279-line
> document instead of at the answer.

**Rules from D-13, restated as mechanics:**
- **Never `blob/beta/…`** — `beta` moves on every merge *and every CI version bump*, so a branch link's
  content changes under the reader.
- **Never `main`** — `main` lags `beta` by a large margin in all three repos.
- **Always a 40-char commit SHA.** Get it after the meta merge: `git rev-parse origin/beta` (re-fetch
  first), or read the merge commit SHA from `gh pr view <N> --json mergeCommit`.

### 7.3 The sequencing consequence, confirmed and strengthened

**The meta merge must land before any reply is drafted with a live link, and certainly before any is
posted.** Three independent reasons, all measured:

1. `ae29f2008-classification-verdict.md` (REPLY-03's evidence) does not exist on `beta` → **404**.
2. `jumper-display-ground-truth.md` exists on `beta` **without** REPLY-04's section → **a link that
   resolves to the wrong content**, which is worse than a 404 because nothing signals the failure.
3. Any SHA available to pin *before* the merge is a SHA at which those files are absent or stubbed.

**Recommended order:** meta PR → merge → `git fetch origin && git rev-parse origin/beta` → pin that SHA in
every permalink → *then* the app and firmware PRs (for the versions) → then draft/approve/post.

Alternatively meta first, sub-repos second, as above — but **meta must be first regardless**, and this is
the one ordering constraint in the phase that is not about irreversibility but about correctness of the
text.

---

## Finding 8 — Label taxonomy (D-14)

### 8.1 The taxonomy, verbatim from `.claude/skills/devtest-triage/SKILL.md:208-220`

```
| Label              | Meaning                                                      | Applied by |
| `dev-test`         | A community `dev test` report                                | `fold --apply`, and by hand on any issue you triage |
| `chip:validated`   | Every applicable step passed; chip is in the ledger          | you, at §4 |
| `fixed:superseded` | Closed against a qualifying later PASS                       | `fold --apply` |
| `intermittent`     | A later PASS exists but the software did not move            | `fold --apply` |
| `needs:report`     | Waiting on a fresh run from the reporter                     | you |
| `fix:committed`    | A fix exists in a branch or PR; no release carries it yet    | `devtest-rootcause` |
| `fix:released`     | A released version carries the fix; re-test to close         | `devtest-rootcause` |
| `cause:harness`    | Defect in the `dev test` harness itself                      | you, after §5 |
| `cause:firmware`   | Defect in the Arduino firmware                               | you, after §5 |
| `cause:database`   | Wrong field in the generated chip database                   | you, after §5 |
| `cause:rig`        | Operator wiring, socket or voltage — not a software defect   | you, after §5 |
```

`:222-225` adds the rule D-14 is applying: *"The `cause:*` label is the single most useful thing triage
produces … It encodes a judgement no parser can derive, so it is never applied mechanically … **More than
one may apply; apply every one you can defend.**"* — which is precisely D-14's "add `cause:rig` alongside
the standing `cause:database`."

### 8.2 Every label D-14 needs already exists in the repo

```bash
$ gh label list --repo henols/firestarter_prom --limit 100
```

| Label | Exists? | Description in repo | Colour |
|---|---|---|---|
| **`cause:rig`** | ✅ | `Operator wiring, socket or voltage fault — not a software defect` | `#d876e3` |
| **`needs:report`** | ✅ | `Waiting on a fresh \`dev test\` run from the reporter` | `#fef2c0` |
| `cause:database` | ✅ | `Wrong field in the generated chip database` | `#d93f0b` |
| `cause:harness` | ✅ | `Defect in the \`dev test\` harness itself` | `#d93f0b` |
| `cause:firmware` | ✅ | `Defect in the Arduino firmware` | `#d93f0b` |
| `fix:released` | ✅ | `A released firmware or host version carries the fix; re-test to close` | `#0052cc` |
| `fix:committed` | ✅ | `A fix exists in a branch or PR but no released artefact carries it yet` | `#bfd4f2` |
| `chip:validated` | ✅ | `Every applicable step passed; chip logged in the validated-EPROM ledger` | `#0e8a16` |
| `fixed:superseded` | ✅ | `Closed: a later qualifying PASS report supersedes this failure` | `#c2e0c6` |
| `intermittent` | ✅ | `A later PASS exists but the software did not move — flaky, not fixed` | `#fbca04` |
| `dev-test` | ✅ | `Community \`dev test\` chip-validation report` | `#1d76db` |
| `enhancement` | ✅ | `New feature or request` | `#a2eeef` |
| `bug` | ✅ | `Something isn't working` | `#d73a4a` |

**All 21 repo labels were listed; every label D-14 names is present. `gh issue edit --add-label` will not
fail on a nonexistent label.** `[VERIFIED: gh label list, 2026-09-12]`

### 8.3 Per-issue label plan derived from D-14/D-15 and the live state

| Issue | Current labels | D-14/D-15 action | Resulting labels |
|---|---|---|---|
| gh#23 | `dev-test`, `cause:database` | **add** `cause:rig`, `needs:report` | `dev-test`, `cause:database`, `cause:rig`, `needs:report` |
| gh#28 | `dev-test`, `cause:harness` | **add** `needs:report`; **withhold** `fix:released` | `dev-test`, `cause:harness`, `needs:report` |
| gh#31 | `dev-test`, `cause:harness`, `cause:database` | **add** `needs:report`; **withhold** `fix:released` | + `needs:report` |
| gh#60 | `enhancement` | label to match "closes as done" disposition; **close** | planner's call (see note) |
| gh#62 | **none** | label to match "stays open" disposition | planner's call (see note) |
| gh#9 | none | **no change** — D-06: 187 posts nothing and changes nothing on gh#9 | unchanged |

**Note on gh#60 / gh#62:** D-14 leaves these to "match their disposition under D-15" without naming labels.
The taxonomy is a `dev test` taxonomy; gh#60 is an `enhancement` and gh#62 is a plain bug report, neither
of which is a `dev test` report. `fix:released` is defensible for gh#60 (a released host version carries
the delivered feature) and is the only taxonomy label that fits a delivered-and-closed feature request.
For gh#62 the honest labels are arguably `cause:firmware` (the capability gap) or none at all, since the
refusal is correct behaviour, not a defect. **This is a genuine gray area within a locked decision; the
planner should put the specific labels in front of the operator inside the same blocking gate that approves
gh#60's and gh#62's bodies, rather than choosing silently.**

Command shape (one label edit per issue, named in the reply body per D-14):

```bash
gh issue edit 23 --repo henols/firestarter_prom --add-label "cause:rig" --add-label "needs:report"
gh issue close 60 --repo henols/firestarter_prom --reason completed
```

---

## Finding 9 — The reply source material, verified in place

### 9.1 REPLY-03 — `ae29f2008-classification-verdict.md:77-113`

The section is present and explicitly marked for this phase:

```bash
$ /usr/bin/grep -n "Phase 187\|REPLY-03\|999.63" .planning/notes/ae29f2008-classification-verdict.md
79:**(Material for Phase 187's REPLY-03, per D-09.)**
109:rail the target part does not expect. REPLY-03 should carry this paragraph verbatim: the erase
201:quoted above under the REPLY-03 section — and a fast (50 ms) chip-erase timing. A future firmware
209:an explicit scope decision, not a quiet follow-on). Filed as backlog **999.63**.
213:- **999.63** — software chip-erase for the `0x05` family (D-20), with the boot-block caveat.
```

**The four load-bearing claims D-13 says the reply must carry "in substance, not in register":**

1. **The erase was real.** *"Driving `erase` under that identity dispatches to
   `flash_nor_unlock_erase_execute` (`firestarter/src/proms/flash_nor_unlock.cpp:121-129`), which for a
   zero address calls `flash_execute_command(FLASH_ERASE)`."*
2. **It used the documented six-cycle sequence.** *"`FLASH_ERASE` (`include/flash_utils.h:34-41`) is the
   six-cycle sequence `{0x5555,0xAA} {0x2AAA,0x55} {0x5555,0x80} {0x5555,0xAA} {0x2AAA,0x55}
   {0x5555,0x10}` — cycle for cycle identical to the W29C020C datasheet's own 'Command Codes for Software
   Chip Erase' table … the 50 ms internal erase plus serial round-trips is consistent with the observed
   0.14 s."*
3. **Benign only by coincidence.** *"Both identities … sit on the same pinout `DIP32_SST39SF040` and the
   same `size_bytes` 262144, so the bus config was identical when misdeclared; and
   `configure_flash_nor_unlock`'s `CMD_ERASE` arm energises no VPP rail … **This benignity is a coincidence
   of this particular chip pair sharing a pinout and a voltage class — it is not a property of `--force` in
   general.**"*
4. **`--force` identity forgery is not a safe workaround.** *"Forging a different identity onto a different
   real part could route a genuinely mismatched bus config or energize a rail the target part does not
   expect."*

And the 999.63 caveat for the "what the reporter actually wants" paragraph (`:198-211`):

> *"The W29C020C datasheet documents a six-byte software chip-erase … and a fast (50 ms) chip-erase timing.
> … The datasheet also documents a boot-block caveat that any such implementation must handle: **'Once the
> boot block programming lockout feature is activated, the chip erase function will be disabled.'** … Filed
> as backlog **999.63**."*

**Cross-check against gh#62's own body** (read live this session) — the reporter's paste matches the
verdict's account exactly: `firestarter erase AE29F2008` → `ERROR: Not supported`;
`firestarter erase SST39SF020 --force` → `WARN: Chip ID 0xda45 does not match expected ID 0xbfb6` then
`Erase for SST39SF020 successful (0.14s)`; `firestarter blank AE29F2008` → successful over `0x40000` in
27.96 s. **Every number the reply will cite is in the reporter's own paste.**

### 9.2 REPLY-04 — `jumper-display-ground-truth.md:170-196` and `jp5_gate.py`

The direct answer to the reporter's question, verbatim from `:170-176`:

> ## Which operations energize socket pin 1 — the answer to gh#60
> Settled 2026-09-10 (SAFE-03, success criterion 5) …
> > **Writing and erasing. Not reading, not verifying, not blank-checking, not `id`.**

**gh#60's body, read live, asks exactly that** and also states the limit:

> *"Unfortunately, **I don't believe you can check if JP5 is cut systematically**, so it might be useful to
> put a warning before every operation involving these kinds of EPROMs"*
> *"\*Just writing, or reading too? Not sure when the VPP is on... still learning about this whole project
> really"*
> *"\*\*With A19 on pin 1"*
> Under *What would you like Firestarter to do?*: *"Warn, and stop operation, unless confirmation that the
> RURP is in a safe state to do the operation."*

**The shipped gate says the reporter is right**, verbatim from `jp5_gate.py:70-81`:

```python
70 def hazard_text(chip_name: str, operation: str, address_bit: int) -> str:
71     """The operator-facing hazard message, checkable against the JP5 silkscreen."""
72     return (
73         f"{chip_name.upper()}: socket pin 1 on this part carries address line "
74         f"A{address_bit}. A {operation} drives socket pin 1 from the 12.75V "
75         f"programming rail once the address crosses A{address_bit}. JP5 "
76         '(silkscreened "Cut for ROMs with A19 on P1") ships bridged by '
77         "default (a Bridged SolderJumper footprint) and this tool cannot read "
78         "its current state on the attached board. JP5 must be cut before this "
79         f"{operation} proceeds, or the part can be damaged. The only escape "
80         "is answering yes at the interactive prompt."
81     )
```

**Call sites — write and erase only, confirming the "not reading" half:**

```bash
$ /usr/bin/grep -n "jp5_gate\|require_acknowledged" firestarter/cli_handlers.py firestarter/eprom_operations.py
cli_handlers.py:754:    if not jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "write"):
cli_handlers.py:889:    if not jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "erase"):
eprom_operations.py:2003:        require_acknowledged( … "write", …)
eprom_operations.py:2147:        require_acknowledged( … "erase", …)
```

**All four CONTEXT.md citations resolve exactly.** Four call sites, two operations, zero on read / verify /
blank / id. `[VERIFIED: /usr/bin/grep + awk, 2026-09-12]`

### 9.3 REPLY-03's sibling — `flash4_erase_gate.py:43`

```python
41 FLASH4_PROTOCOL_ID = 5
43 _REFUSAL_FORMAT = "Erase not supported for {chip_name}"
```

Call site: `cli_handlers.py:885-886`. **Exactly as CONTEXT.md cites — a one-line refusal naming the part,
deliberately carrying no cause and no alternative (SAFE-06 as amended by 183's D-07/D-08). The cause and
the alternative are REPLY-03's job.**

### 9.4 D-12's gh#28/#31 caveat — the folded todo's measurement still holds

`.planning/todos/pending/2026-09-08-uv-write-shortcut-disclosure-key.md` exists (3,179 bytes, 2026-09-08),
`resolves_phase: none`, and states:

> *"`firestarter dev test m27c512` now passes (`overall_verdict == "PASS"`, `run_count == 2`) on a
> non-blank UV part, by passing `FLAG_SKIP_BLANK_CHECK` on a proven monotonic masked write. On the IDENTICAL
> part, `firestarter write -a 0x…` is still refused by the identical firmware write-init pre-flight — the
> user-facing write command does not set `FLAG_SKIP_BLANK_CHECK`, and nothing in the current report
> discloses that the `dev test` harness took a path the product's own write command does not take."*

Verified in the shipped code:

```bash
$ /usr/bin/grep -n "FLAG_SKIP_BLANK_CHECK" firestarter/chip_test.py
34:    FLAG_SKIP_BLANK_CHECK,
2373:    witness the `FLAG_SKIP_BLANK_CHECK` pass is derived from. It exists as a
3290:        FLAG_SKIP_BLANK_CHECK if _is_monotonic_masked_target(resolved_target) else 0
```

**`chip_test.py:3290` sets the flag conditionally on a monotonic-masked target; nothing analogous exists on
the `write` command path.** D-12's caveat — *"a PASS on a re-run does not mean `write` works on their
chip"* — is measured and current.

**D-12's fold is reply-material-only: the todo stays pending and this phase must not add a report key.**

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Proving a posted comment matches the approved body | A `diff` of `gh api --jq '.body'` against the file | The METHOD B python round-trip in §6.4 | The naive form produces a **false mismatch** from jq's trailing newline — measured this session on a comment that is in fact identical |
| Establishing what `beta` already carries | `git merge-base --is-ancestor` | `git cherry origin/beta <branch>` | D-05, and v1.30's squashed merge already produced one `--is-ancestor` false negative |
| Knowing the cut version | Computing `b(N+1)` from the current release | `gh release list --repo … --limit 3` **after** the run completes | D-05. The bump runs in CI against git tags; a local computation can race or diverge |
| Posting a comment | Inline `--body "…"` | `--body-file <path>` | Both project skills mandate it (`SKILL.md:345-349`); shell interpolation mangles markdown and makes byte-identity unprovable |
| Editing `ROADMAP.md` / `REQUIREMENTS.md` | `gsd-tools` requirements/roadmap verbs | Hand edits | Those verbs run `_normalizeMd` over the whole file, reformatting far beyond the edit (Phase 152 D-05 says so explicitly; standing project rule) |
| Fixing a chip's DB field | Editing `chip_database.json` | `build_db.py`'s decode — and **not in this phase at all** | The DB is generated (milestone D-6). Any hand edit is overwritten on the next generation |
| Archiving the milestone | `milestone.complete` | Hand archival (D-03) | Standing rule: the CLI would overwrite the hand-authored ROADMAP |
| Tidying the working tree | `git clean -Xdf` | `rm` by explicit path | `.planning/state.json` and bench `.bin` files are gitignored here and would be destroyed |
| Reading `STATE.md` | `state.load` / bare `cat` | `grep` for a heading then `sed -n` a window | `STATE.md` is 510 KB; `state.load` returns the whole thing (~125k tokens) |

**Key insight:** every hand-rolled shortcut in this table has a measured failure in this project's own
history. The phase's risk is not that a step is hard; it is that a plausible-looking step produces a false
reading and an irreversible act is taken on it.

---

## Common Pitfalls

### Pitfall 1: Posting before the meta merge
**What goes wrong:** REPLY-03's permalink 404s; REPLY-04's permalink resolves to a 76-line stub that lacks
the section it cites.
**Why it happens:** `.planning/notes/` *is* on `beta` and *does* have 26 entries, so a shallow check passes.
**How to avoid:** merge meta first; re-fetch; pin the post-merge SHA; then draft.
**Warning sign:** a permalink whose SHA is ≤ `0629e4ad365a3ef8d3fde38a1e28272e3c49ef59`.

### Pitfall 2: A verify leg that greps the firmware repo for `beta-release.yml`
**What goes wrong:** finds nothing; either blocks or falsely concludes no cut fires.
**How to avoid:** `beta-build.yml` for firmware, `beta-release.yml` for the app (DRIFT-1).

### Pitfall 3: Asserting "zero open PRs" as a precondition
**What goes wrong:** `firestarter#54` (stale external OLED PR, base `beta`) makes the check red.
**How to avoid:** scope the assertion to "no open PR whose head is the v1.37 milestone branch."

### Pitfall 4: Committing the `config.json` sub_repos prune
**What goes wrong:** two configured sub-repos (`firestarter_app_py32`, `firestarter_py32_ci`) are silently
deleted from the project config, in a public PR.
**How to avoid:** `git checkout -- .planning/config.json` before staging anything. Re-check right before the
meta PR — the prune is re-introduced by `loop render-hooks`, which the plan-phase flow calls.
**Warning sign:** `git diff .planning/config.json` is non-empty and you did not edit it.

### Pitfall 5: `anything.txt` / `tmp/` / the two datasheet PDFs in a public PR
**What goes wrong:** operator scratch notes and unrelated research PDFs land in the public tracker repo.
**How to avoid:** explicit `git status --short` review in both meta and the app repo immediately before each
PR; remove by explicit path, never `git clean -Xdf`.

### Pitfall 6: A short poll timeout on the firmware cut
**What goes wrong:** one measured firmware run took **70 minutes**. A 10-minute timeout reports failure on a
run that later succeeds — and the plan may then take corrective action against a healthy cut.
**How to avoid:** poll on `status == "completed"` with no deadline under 90 minutes.

### Pitfall 7: Claiming gh#65/#66 are unanswered
**What goes wrong:** a public, false statement, in the phase about not making those (DRIFT-2).
**How to avoid:** the acknowledgement says they are open, not that they are unanswered.

### Pitfall 8: Letting the tag step run
**What goes wrong:** `config.json` has `git.create_tag: true`; D-04 forbids a `v1.37` tag; the close flow's
only `git push` is a tag push (`git-tag.md:26`).
**How to avoid:** explicitly skip or suppress the tag step and make its absence an acceptance criterion.

### Pitfall 9: Dispatching the phase under `--auto` / `--chain`
**What goes wrong:** those modes auto-approve human-verify gates. `autonomous: false` is **not**
self-protecting against them. Five public, irreversible acts would be approved by the harness.
**How to avoid:** D-16's hard constraint — never dispatch in those modes; every public-act plan carries
`autonomous: false` *as well*.

### Pitfall 10: Restating D-07's "10 files"
**What goes wrong:** files a fresh false measurement (it is 33) in the phase that exists to stop that.
**How to avoid:** §5.2. State the count only if re-measured, or omit it.

### Pitfall 11: A wrapped `D-NN` bullet or a bare `<!--` in a plan file
**What goes wrong:** the decision-coverage gate fails closed on wrapped labels; a bare `<!--` in a PLAN.md
swallows the frontmatter's closing `---`.
**How to avoid:** single-line `D-NN` labels; no bare HTML comment openers in plan frontmatter.

### Pitfall 12: `gh run view --log` without `XDG_CACHE_HOME`
**What goes wrong:** `~/.cache/gh` is unwritable in this devcontainer; the failure presents as an auth error
and misdiagnoses.
**How to avoid:** `export XDG_CACHE_HOME=<writable dir>` before any `gh run view --log`. `gh pr list`,
`gh issue view`, `gh api` and `gh label list` are unaffected.

---

## Code Examples

### Re-measure the release seam (run immediately before the merge stage)

```bash
for D in /workspaces /workspaces/firestarter /workspaces/firestarter_app; do
  ( cd "$D"
    git fetch origin --quiet
    B=$(git rev-parse --abbrev-ref HEAD)
    echo "=== $D ($B) ==="
    echo "origin/beta: $(git rev-parse origin/beta)"
    echo "HEAD:        $(git rev-parse HEAD)"
    echo "new(+):      $(git cherry origin/beta "$B" | grep -c '^+')"
    echo "equiv(-):    $(git cherry origin/beta "$B" | grep -c '^-')" )
done
```

### Read the cut versions (never predict them)

```bash
export XDG_CACHE_HOME=/tmp/gh-cache; mkdir -p "$XDG_CACHE_HOME"
gh release list --repo henols/firestarter_app --limit 3
gh release list --repo henols/firestarter    --limit 3
# independent PyPI confirmation
curl -s https://pypi.org/pypi/firestarter/json \
 | python3 -c "import json,sys;d=json.load(sys.stdin);print(sorted(d['releases'])[-3:])"
```

### Wait for a cut to complete

```bash
poll() {  # poll <repo> <workflow-file>
  while :; do
    S=$(gh run list --repo "$1" --workflow "$2" --limit 1 --json status,conclusion,databaseId \
        --jq '.[0]|"\(.status) \(.conclusion) \(.databaseId)"')
    echo "$(date -u +%H:%M:%S) $S"
    case "$S" in completed*) break;; esac
    sleep 30
  done
}
poll henols/firestarter_app beta-release.yml
poll henols/firestarter    beta-build.yml      # NOTE: not beta-release.yml
```

### Hash-bind the approved bodies (Phase 173 approval-file pattern)

```bash
cd /workspaces/.planning/phases/187-answered-reports
for F in evidence/bodies/187-gh*.md; do
  printf 'sha256(%s) = %s\n' "$F" "$(sha256sum "$F" | cut -d' ' -f1)"
done >> evidence/187-operator-approval.txt
```

### Post, then prove byte-identical (the one that does not false-alarm)

```bash
N=23; F=evidence/bodies/187-gh23.md
URL=$(gh issue comment "$N" --repo henols/firestarter_prom --body-file "$F")
echo "$URL"
ID=${URL##*-}
gh api "repos/henols/firestarter_prom/issues/comments/$ID" > /tmp/c.json
python3 -c "
import json,hashlib,sys
b=json.load(open('/tmp/c.json'))['body'].encode(); d=open(sys.argv[1],'rb').read()
print('api ',len(b),hashlib.sha256(b).hexdigest())
print('disk',len(d),hashlib.sha256(d).hexdigest())
print('BYTE-IDENTICAL' if b==d else 'MISMATCH'); sys.exit(0 if b==d else 1)" "$F"
```

### Prove no collateral comment was created

```bash
WINDOW_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)   # capture BEFORE the first post
# … posting happens …
gh api repos/henols/firestarter_prom/issues/comments --paginate \
  --jq ".[] | select(.created_at >= \"$WINDOW_START\") | {issue:(.issue_url|split(\"/\")|last),created_at,id}"
# expect exactly one row per targeted issue, and nothing else
```

### Capture before/after issue state (Phase 173 pattern)

```bash
for N in 9 23 28 31 60 62; do
  gh issue view $N --repo henols/firestarter_prom \
    --json number,title,state,stateReason,labels,comments \
    --jq '{n:.number,state:.state,reason:.stateReason,labels:[.labels[].name],
           ncomments:(.comments|length)}'
done > evidence/187-issue-state-before.json
gh api graphql -f query='{repository(owner:"henols",name:"firestarter_prom"){
  pinnedIssues(first:10){totalCount nodes{issue{number}}}}}' \
  >> evidence/187-issue-state-before.json
```

---

## Project Constraints (from CLAUDE.md)

Directives extracted from `/workspaces/CLAUDE.md`. The planner must verify compliance.

| Directive | Bearing on Phase 187 |
|---|---|
| **No comments in product source — "hard rule", not overridable by a plan, task, skill or subagent** | This phase writes no product source, so it should not arise. **But:** if a reply body quotes shipped code, the plan must not treat that as licence to add or alter a source comment. GSD identifiers (`D-06`, `REQ-NN`, phase numbers) must not appear in any `firestarter/` or `firestarter_app/` file. |
| **Planners: do not write "add a comment citing X" into a plan; do not make "a comment exists" an acceptance criterion** | Directly binding on the planner. |
| **Rationale goes in `SUMMARY.md`, `REQUIREMENTS.md` traceability, or the commit message** | The D-09 `.planning/notes/` document and each plan's SUMMARY are the correct homes. |
| **Click docstrings in `firestarter_app` are user-facing `--help` text, not commentary** | Not touched here; noted so a "comment sweep" instinct does not reach them. |
| **`main` is protected in all three repos; PR required; `current_user_can_bypass` is `never`** | Confirmed live (§DRIFT-5). Nothing this phase does targets `main`. |
| **This project's close targets `beta`, not `main` (`git.base_branch: beta`)** | Confirmed in `.planning/config.json`. All three PRs go to `beta`. |
| **Before `/gsd-ship`, recreate local `beta` from `origin/beta`** — `ship.md` anchors on `merge-base beta HEAD` and local `beta` goes stale | Binding if the plan routes any step through `/gsd-ship`. |
| **Mechanics are in `.planning/notes/v135-close-procedure-under-protection.md`** | Read in full; summarised at §6.7. |
| **Serial protocol / constants must stay in sync across repos** | Not applicable — no protocol or constant change in this phase. |
| **`chip_database.json` is generated; user overrides go to `~/.firestarter/database.json`** | Reinforces §3.3 — no hand edit, and no reply may imply one. |

---

## Runtime State Inventory

This is not a rename/refactor phase, but it **is** a phase whose deliverables are external state. The same
question — *"what lives outside the repo that this phase changes?"* — is answered here.

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | None. No database, no Mem0, no ChromaDB, no persisted keys are touched. | **None — verified:** the deliverable list contains no data write, and `chip_database.json` is explicitly not edited (§3.3). |
| **Live service config** | **GitHub Issues state on `henols/firestarter_prom`:** 5 new comments, ~6 label edits, 1 close (gh#60). **GitHub Releases:** 1 new app pre-release, 1 new firmware pre-release. **PyPI:** 1 new `firestarter` pre-release. **Branch `beta` in 3 repos:** advanced by 174 / 33 / 9 commits plus 2 CI auto-commits. | All are the phase's intended output. Every one is behind a D-16 blocking gate. **The PyPI publication is the single irreversible item with no undo.** |
| **OS-registered state** | None — no Task Scheduler, pm2, launchd or systemd registration is involved. | **None — verified:** phase deliverables are git + GitHub API only. |
| **Secrets / env vars** | `PERSONAL_ACCESS_TOKEN` (app repo, used by the Release step) and `PYPI_API_TOKEN` (inherited by `publish.yml`) are consumed by CI, not by this phase. `XDG_CACHE_HOME` must be set locally for `gh run view --log`. | **No secret is created, rotated or read by this phase.** Do not touch them. |
| **Build artifacts / installed packages** | The devcontainer's editable `firestarter` install points at the working tree, so it already reflects the milestone branch. Published `.hex` assets (uno / uno328pb / leonardo, + optional py32f071) are produced by CI. | **None owed locally.** Reporters install via `pip install --pre -U firestarter` and `firestarter fw --install`. |
| **In-repo state the phase leaves dirty** | `.planning/config.json` prune, `.planning/VALIDATED-EPROMS.md` +6, `anything.txt`, `tmp/`, two untracked app-repo PDFs. | **Disposition required before the first PR** (§DRIFT-4). |

---

## Environment Availability

| Dependency | Required by | Available | Version / evidence | Fallback |
|---|---|---|---|---|
| `gh` CLI, authenticated | every public act | ✅ | all `gh pr/issue/api/label/release/run` calls succeeded this session as `henols` | none — blocking |
| `gh api graphql` | gh#9 pin verification | ✅ | `pinnedIssues` query returned `totalCount: 1` | none needed (read-only) |
| `git` with all three remotes fetchable | `git cherry`, `cat-file`, `ls-tree` | ✅ | `git fetch origin` rc=0 in all three repos | none — blocking |
| `python3` | byte-identity proof, JSON parsing | ✅ | 3.12 in devcontainer | `head -c -1` + `cmp` (METHOD A) |
| `sha256sum` | hash-binding the approval file | ✅ | present | `python3 hashlib` |
| `curl` + network to pypi.org | independent PyPI check | ✅ | `pypi.org/pypi/firestarter/json` returned 200 with release list | `pip index versions firestarter --pre` |
| `/usr/bin/grep` (real GNU grep) | all evidence greps | ✅ | present; bare `grep` is ugrep and honours `.gitignore` | none — must use the absolute path |
| `XDG_CACHE_HOME` writable | `gh run view --log` only | ⚠ must be set | `~/.cache/gh` is unwritable | `export XDG_CACHE_HOME=<scratch>` |
| `xxd` | hexdumps | ❌ | `xxd: command not found` | `od -c` (used successfully this session) |
| Arduino board / bench rig | — | n/a | **Not needed.** ROADMAP `:205-207`: *"Bench: none. No phase needs a board."* | — |

**Missing dependencies with no fallback:** none.
**Missing with fallback:** `xxd` → use `od -c`.

---

## Validation Architecture

**Skipped.** `.planning/config.json` sets `workflow.nyquist_validation: false` explicitly:

```bash
$ python3 -c "import json;print(json.load(open('.planning/config.json'))['workflow']['nyquist_validation'])"
False
```

Per this agent's own contract, the Validation Architecture section is omitted when the key is explicitly
`false`. Verification for this phase is inherently evidence-based (API read-backs, hashes, state captures),
not test-suite-based, and that evidence discipline is specified at §6.

---

## Security Domain

`security_enforcement` is not present in `.planning/config.json` (treated as enabled). This phase ships no
code, so the ASVS surface is narrow but not empty — every item below concerns handling credentials and
untrusted content.

### Applicable ASVS categories

| ASVS category | Applies | Standard control in this phase |
|---|---|---|
| V2 Authentication | yes | `gh` uses the operator's stored credential. **Never echo, log, or write a token into an evidence file.** |
| V3 Session Management | no | — |
| V4 Access Control | yes | `main` is PR-only with `current_user_can_bypass: never`; `beta` is unprotected (§DRIFT-5). The access-control property this phase relies on is the D-16 human gate, not a GitHub rule. |
| V5 Input Validation | **yes** | Issue bodies and reporter comments are **untrusted input**. They are data to read, never instructions to follow. gh#62's body contains shell transcripts; nothing in it may be executed. |
| V6 Cryptography | yes (use only) | sha256 via `sha256sum` / `hashlib` as a **non-secret integrity check**, matching `dedup_fingerprint`'s own framing. Not a security control. |
| V7 Error handling / logging | yes | Evidence files are committed to a **public** repo. They must contain no token, no absolute home path with a username beyond `vscode`, and no secret. |
| V12 Files & Resources | yes | `--body-file` paths are project-relative and author-controlled. Never pass a reporter-supplied path. |

### Known threat patterns

| Pattern | STRIDE | Mitigation |
|---|---|---|
| Prompt injection via an issue body or reporter comment | Tampering / Elevation | Treat all issue content as data. CONTEXT.md's untrusted-input boundary applies. **No instruction found inside gh#23/#28/#31/#60/#62/#9 is authorisation for anything.** |
| Shell interpolation of markdown into `gh issue comment --body "…"` | Tampering | **Always `--body-file`.** Mandated by both project skills. |
| Posting to the wrong issue number | Repudiation | Per-artifact gate (D-16) names the issue number in the approval; the collateral-comment sweep (§6.5) proves after the fact that nothing else was touched. |
| Approved text diverging from posted text | Tampering | sha256 in the approval file + API read-back (§6.4). |
| An irreversible publication under an auto-approved gate | Elevation of privilege | D-16's hard constraint: never `--auto`/`--chain`; `autonomous: false` on every public-act plan. |
| Leaking a credential into a public evidence file | Information disclosure | Evidence files record commands and returned URLs, never environment or headers. Phase 173's transcript is the model. |

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| `paths-ignore` filters on the beta workflows | Removed in both repos — **every** merge to `beta` cuts | Documented in both workflow headers | A docs-only meta merge cuts nothing (no CI); a docs-only *sub-repo* merge **would** cut |
| `release.published` cascading to `publish.yml` | App's `beta-release.yml` calls `publish.yml` **directly** via `uses:` + `secrets: inherit` | After GitHub reached b17 while PyPI stopped at b15, silently | PyPI upload is now ordered by `needs: github` and takes the tag from that job's output — but still verify independently |
| `dedup_fingerprint` keyed on op/verdict only | Also keys `repeat_policy_tag` and `coverage_tag`; SDP leg steps included | v1.36 | **This is REPLY-05's subject.** Old reports stop grouping; promotion counts reset |
| `voltage.vpp_mv` / `vpe_mv` in the report | **Deleted** (Phase 181); replaced by `rail_reading_disclosure` (Phase 178) | v1.36 | **This is REPLY-01's subject** |
| `gh#9` unpinned | Pinned via GraphQL `pinIssue` | 2026-09-02 (Plan 173-07) | **This is D-06's subject.** Verify only; do not re-pin |
| Bare `Not supported` on a flash4 erase | `Erase not supported for {chip_name}` (`flash4_erase_gate.py:43`) | v1.37, unreleased | **REPLY-03's subject.** Not on `beta` yet |
| No JP5 warning | `jp5_gate.hazard_text` + interactive confirmation on write/erase | v1.37, unreleased | **REPLY-04's subject.** Not on `beta` yet |

**Deprecated / retired, relevant here:**
- `tools/wiki/` checkers and `wiki-check.yml` — retired 2026-09-02, removed 2026-09-08. **No automated wiki
  guard exists.** No reply should cite one.
- `Catalog sync check` on `main` — retired in Phase 185 (CLAIM-08), cause recorded in
  `.planning/notes/catalog-sync-check-retirement.md`. That note is **not on `beta`** until the meta merge.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The next app/firmware pre-release versions will be produced by `update_version.py`'s tag-scan increment. `[VERIFIED by source read of the script's beta path; the *resulting numbers* are deliberately NOT predicted per D-05]` | §1.7 | None — the plan reads the version, so a different increment changes nothing |
| A2 | `gh#60` closing as `completed` is the right `--reason`. `[ASSUMED]` — D-15 says "closes as done"; `gh issue close --reason completed` is the mapping, but the operator has not named the flag | §8.3 | Low. A wrong reason is reversible and visible |
| A3 | The specific labels for gh#60 and gh#62 under D-14. `[ASSUMED]` — D-14 defers to "match their disposition under D-15" without naming them | §8.3 | Medium. **Surface at the operator gate rather than choosing silently** |
| A4 | The anchor slugs for the two linked note sections. `[ASSUMED]` — GitHub's slug rule is well known but these headings contain backticks, an em-dash and a `#` | §7.2 | Medium. A wrong anchor silently lands the reader at the top of the doc. **Copy the real anchor from the rendered page after the merge** |
| A5 | `.planning/VALIDATED-EPROMS.md`'s uncommitted +6 lines are intended content. `[ASSUMED]` — not inspected line-by-line | §DRIFT-4 | Low, but it will land in a public PR if committed unreviewed |
| A6 | Recommending meta-first merge ordering. `[ASSUMED]` as a recommendation; the *constraint* it serves (§7.3) is `[VERIFIED]` | §7.3 | Low. Any order works provided meta lands before drafting |

**Everything else in this document is `[VERIFIED: <command>, 2026-09-12]` or `[CITED: <file>:<lines>]`.**

---

## Open Questions (RESOLVED)

*All five were carried into the plans during planning on 2026-09-12; each carries an inline `RESOLVED:` clause naming the plan that discharges it.*

1. **What labels do gh#60 and gh#62 actually get?**
   - What we know: D-14 says "labelled to match their disposition under D-15"; all taxonomy labels exist.
   - What's unclear: the `dev test` taxonomy does not cleanly fit an `enhancement` or a plain bug report.
   - **Recommendation:** put the concrete label list in front of the operator inside the same blocking gate
     that approves each body. Do not choose silently — D-14 forbids silent reclassification by name.
   - **RESOLVED:** carried to the operator gates in `187-07` (gh#60) and `187-08` (gh#62) as an explicit
     item the operator sees, per D-14's ban on silent reclassification. Not chosen by the plan.

2. **Does the acknowledgement to dim20 change shape now that gh#65/#66 are answered?**
   - What we know: both carry a maintainer datasheet cross-check dated 2026-09-10; three of dim20's four
     issues remain open.
   - What's unclear: whether the operator still wants the one-line acknowledgement at all.
   - **Recommendation:** carry it, re-worded to "open" rather than "unanswered", and flag the change at the
     gh#62 gate so the operator sees the drift.
   - **RESOLVED:** `187-05` drafts it as "open", never "unanswered", and the DRIFT-2 finding is flagged
     at the gh#62 gate so the operator decides whether the line survives at all.

3. **Which commit SHA does each permalink pin?**
   - What we know: it must be at or after the meta merge (§7.3); D-13 leaves the choice to discretion.
   - **Recommendation:** pin **one** SHA — the meta merge commit — across all permalinks. One SHA is one
     thing to verify, and the D-09 notes document can state it once.
   - **RESOLVED:** `187-02` pins **one** SHA — the meta merge commit — across every permalink in every
     body, recorded there as a D-13 discretion decision.

4. **Is `/gsd-ship` used at all, and if so how is the tag suppressed?**
   - What we know: `git.create_tag: true` vs D-04's no-tag; `ship.md` mis-anchors on a stale local `beta`.
   - **Recommendation:** open the three PRs directly with `gh pr create --base beta` rather than routing
     through `/gsd-ship`, and make "no `v1.37` tag exists" an explicit verification leg
     (`git ls-remote --tags origin | grep -c v1.37` → 0 in all three repos).
   - **RESOLVED:** `/gsd-ship` is not used. `187-02`, `187-03` and `187-04` open and merge the PRs directly
     with `gh pr create --base beta` / `gh pr merge`, and each asserts no `v1.37` tag exists in any of the
     three repos; `187-12` re-asserts it at closeout.

5. **What disposition do the uncommitted working-tree items get?**
   - What we know: the config prune must be reverted; `anything.txt` and `tmp/` must not be committed;
     `VALIDATED-EPROMS.md` is undetermined.
   - **Recommendation:** a first plan whose only job is tree hygiene + the five D-07 repairs, with a clean
     `git status` as its acceptance criterion, before any PR exists.
   - **RESOLVED:** `187-01` is exactly that tree-hygiene-first plan — it reverts the `sub_repos` prune,
     stages by explicit path only, forbids `git clean -Xdf`, leaves `anything.txt`/`tmp/` and the two app
     datasheet PDFs untracked, and commits `VALIDATED-EPROMS.md` (the gh#61 AE29F2008 PASS log entry,
     dispositioned as intended content by the orchestrator).

---

## Sources

### Primary (HIGH confidence) — measured live this session, 2026-09-12

- `git fetch` + `git cherry origin/beta <branch>` in all three repos — ahead-counts, SHAs
- `git cat-file -e origin/beta:<path>` — gate-file absence on `beta`
- `git diff --stat / --numstat origin/beta...HEAD` — firmware and app deltas
- `git ls-tree origin/beta|HEAD .planning/notes/` + `comm` — notes inventory and the four new files
- `git show origin/beta:<path> | wc -lc | /usr/bin/grep` — DRIFT-3 stub finding
- `gh pr list` (open + merged, all three repos) — PR state and precedent
- `gh issue view <N> --json …` for 9, 21, 23, 24, 28, 31, 60, 61, 62, 65, 66, 67, 68
- `gh issue list --search "w27e257" --state all` — no PASS exists
- `gh api graphql { pinnedIssues }` — gh#9 pin live
- `gh api repos/…/issues/comments/5511487546` + `python3 hashlib` — byte-identity round trip
- `gh api repos/<R>/rulesets` and `repos/<R>/rules/branches/{beta,main}` — DRIFT-5
- `gh label list --repo henols/firestarter_prom --limit 100` — all 21 labels
- `gh release list` (both sub-repos) + `gh run list --workflow …` — cut state and timings
- `curl https://pypi.org/pypi/firestarter/json` — independent PyPI confirmation
- `python3 -c json` over `firestarter_app/firestarter/data/chip_database.json` — the three defects
- `/usr/bin/grep -n` + `awk`/`sed` over `chip_test.py`, `submit.py`, `diagnostic_report.py`,
  `jp5_gate.py`, `flash4_erase_gate.py`, `cli_handlers.py`, `eprom_operations.py`
- `awk 'NR>=… && NR<=…'` over `ROADMAP.md` and `REQUIREMENTS.md` — all five repair sites + both exclusions

### Secondary (HIGH confidence) — in-repo primary records read in full or in cited range

- `.planning/phases/187-answered-reports/187-CONTEXT.md` (361 lines, full)
- `.planning/REQUIREMENTS.md` (228 lines, full)
- `.planning/milestones/v1.32-phases/152-outward-facing-close-operator-gated/152-CONTEXT.md` § decisions
- `.planning/milestones/v1.35-phases/173-…/173-07-SUMMARY.md:95-140`
- `.planning/milestones/v1.35-phases/173-…/173-UPSTREAM-REPLIES.md:1-80`
- `.planning/milestones/v1.35-phases/173-…/evidence/173-07-post-transcript.txt` (full)
- `.planning/milestones/v1.35-phases/173-…/evidence/173-07-operator-approval.txt` (full)
- `.planning/notes/v135-close-procedure-under-protection.md` (113 lines, full)
- `.planning/notes/ae29f2008-classification-verdict.md:77-113`, `:198-215`
- `.planning/notes/jumper-display-ground-truth.md:170-200`
- `.planning/todos/pending/2026-09-08-uv-write-shortcut-disclosure-key.md:1-40`
- `.claude/skills/devtest-triage/SKILL.md:205-225`, `:340-355`
- `.claude/skills/devtest-rootcause/SKILL.md:330-342`
- `/workspaces/CLAUDE.md` (full)
- `firestarter_app/.github/workflows/beta-release.yml` (full)
- `firestarter/.github/workflows/beta-build.yml` (full)

### Tertiary (LOW confidence)

None. **No web search was used and no training-memory claim appears in this document.**

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Release seam (§1) | **HIGH** | Every figure from `git cherry` / `gh` this session; three of D-01's four specific claims reproduced verbatim |
| Live issue state (§2) | **HIGH** | Full `gh issue view` on all eight issues plus GraphQL pin read; a complete sha256 round trip on the gh#9 comment |
| Datasheet defects (§3) | **HIGH** | Parsed from the shipped JSON; the alias-key gotcha found and documented |
| D-11 evidence (§4) | **HIGH** | Line numbers reproduce exactly; the FAIL-title mechanism traced end to end through `chip_test.py` → `submit.py` |
| Record repairs (§5) | **HIGH** | All five sites + both exclusions re-read; one factual error inside D-07's fence found |
| Posting mechanics (§6) | **HIGH** | Precedent read in full; the byte-identity trap discovered by running the naive comparison and finding it false |
| Permalinks (§7) | **HIGH** | URL shape confirmed against the contents API at a pinned SHA; DRIFT-3 is a hard, measured blocker |
| Labels (§8) | **HIGH** for existence, **MEDIUM** for gh#60/#62 assignment | All labels enumerated live; the two assignments are a genuine gray area D-14 did not resolve |

**Research date:** 2026-09-12
**Valid until:** **7 days at most — and re-measure §1 and §2 immediately before acting regardless.** This
document's whole subject is live upstream state. CONTEXT.md's own measurements were 2 days old and three
had already moved. Assume the same of this document.

---

## RESEARCH COMPLETE
