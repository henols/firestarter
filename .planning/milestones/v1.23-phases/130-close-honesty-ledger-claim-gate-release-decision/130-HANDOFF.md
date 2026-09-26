# Phase 130 Plan 14 — Operator Hand-off Dossier

**Written:** 2026-08-02, immediately before hand-off (Plan 130-14, wave 7)

**Purpose.** This is the phase's structural gate, made real rather than merely asserted. The
ROADMAP's Ordering note, CONTEXT's Established Patterns, and `130-RESEARCH.md`'s break-a-plan
list all say the same thing: **`--auto` and `--chain` auto-approve human-verify checkpoints, and
`autonomous: false` does not protect an outward-facing gate.** So the protection is not a
checkpoint type or a flag — it is that the privileged commands (`git push`, `git merge` into
`beta`, `git tag`, `gh workflow run`, `gh release create/edit/delete`, `twine upload`) are **not in
any task, in any plan, in this phase.** They exist below only as text for a human to read and run.
No task in this plan, or any of the other fifteen `130-*-PLAN.md` files, executes any of them — see
§3's mechanical proof.

This dossier also refuses to let the operator act on stale numbers. `130-RESEARCH.md`'s live-state
table is stamped 2026-08-02 and was valid roughly a week from then; `130-DECISION.md` re-measured
everything one wave earlier, at 2026-08-02T18:50–18:57Z. §1 below re-measures again, minutes before
hand-off, because branch tips and tag ceilings move the instant anyone pushes.

**This plan ticks NO requirement id.** CLOSE-01, CLOSE-02, CLOSE-03 and CLOSE-04 stay unchecked;
only plan 130-16 may tick them.

---

## 0. CONSTRAINT 1 precondition — verified by reading git, not assumed

CLOSE-04's text is literal: the decision must exist and precede any push. v1.21's close skipped
exactly this step. Verified by:

```
$ git log --format='%H %cI %s' -1 -- .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-DECISION.md
db7978602ab9efd80a4a2d55aa7a2208bdcaf71d 2026-08-02T19:00:17Z docs(130-13): record beta-push decision before any push (CLOSE-04)
```

**`130-DECISION.md` is committed** as `db797860`, committer timestamp `2026-08-02T19:00:17Z`. This
timestamp is strictly earlier than anything in §2's procedure below can happen, because that
procedure has not yet been run by anyone. Plan 130-16 cites this SHA and timestamp as the
decision-preceded-the-act evidence.

---

## 1. Live state, re-measured immediately before hand-off (2026-08-02, ~19:15–19:20Z)

Every figure below was measured in this session, fetch-only and read-only (`git fetch origin`,
`git rev-parse`, `git rev-list`, `git tag --list`, `git diff --name-only`, `git status
--porcelain`, `git ls-tree`, `pytest`, `pio test`, and this phase's two Python checkers, plus a
read-only `gh release list`). **No merge, checkout, commit, push, or tag was executed against
either sub-repo, and no `gh` write call was made.** Verdict per row: **AGREES** with
`130-DECISION.md`'s recorded value, or **MOVED**, with the plan that moved it named.

### 1.1 Branch tips (`git fetch origin` then `rev-parse`)

| Repo | Branch | Tip SHA (this measurement) | `130-DECISION.md` value | Verdict |
|---|---|---|---|---|
| `firestarter` | `v1.23-py32f071-integration` | `05c20bf59a4f0f73acf28d48d5dbbedab5724c5f` | `05c20bf5…` | **AGREES** |
| `firestarter_app` | `v1.23-py32f071-integration` | `cc9452f4db9a814ffb221bab767c24db67288365` | `cc9452f4…` | **AGREES** |

Neither working tip moved since `130-DECISION.md`'s own re-measurement one wave ago — no plan
between 130-13 and this one committed inside either sub-repo.

### 1.2 `origin/beta` tips (after `git fetch origin` in each repo)

| Repo | `origin/beta` SHA | `130-DECISION.md` value | Verdict |
|---|---|---|---|
| `firestarter` | `5c9160a34b665878b05403ab014b959926feb6bf` | `5c9160a3…` | **AGREES** |
| `firestarter_app` | `e7d3ee8c8a41cd20e9159ab43b5cd969603d773e` | `e7d3ee8c…` | **AGREES** |

`origin/beta` has **not moved** in either repo. The push-safety premise this whole procedure rests
on — a clean, non-conflicting outbound merge — is still intact at the moment of hand-off.

### 1.3 Ahead/behind counts (`git rev-list --left-right --count origin/beta...HEAD`)

| Repo | Measured (behind / ahead) | `130-DECISION.md` value | Verdict |
|---|---|---|---|
| `firestarter` | `0 / 85` | `0 / 85` | **AGREES** |
| `firestarter_app` | `0 / 37` | `0 / 37` | **AGREES** |

Zero behind in both — the outbound `--no-ff` merge in §2 step 3 is still clean, with no inbound
catch-up to plan.

### 1.4 Local `beta` versus `origin/beta`

| Repo | Local `beta` SHA | `origin/beta` SHA | Verdict |
|---|---|---|---|
| `firestarter` | `5c9160a34b665878b05403ab014b959926feb6bf` | `5c9160a34b665878b05403ab014b959926feb6bf` | **AGREES — 0/0** |
| `firestarter_app` | `e7d3ee8c8a41cd20e9159ab43b5cd969603d773e` | `e7d3ee8c8a41cd20e9159ab43b5cd969603d773e` | **AGREES — 0/0** |

**Standing hazard, recorded rather than assumed away:** the instant CI cuts the next beta in either
repo, `git-auto-commit-action` pushes a version-bump commit directly onto `beta`, and local `beta`
falls one commit behind the remote in that repo. Any local operation that later touches `beta` in
either repo must `git fetch` first.

### 1.5 Version strings on both sides

| Repo | File | Working-tree value | `origin/beta` value | Verdict |
|---|---|---|---|---|
| `firestarter` | `include/version.h` | `VERSION "3.0.0b14"` | `VERSION "3.0.0b14"` | **AGREES** |
| `firestarter_app` | `firestarter/__init__.py` | `__version__ = "3.0.0b14"` | `__version__ = "3.0.0b14"` | **AGREES** |

Neither branch carries a pre-bumped version string — the outbound merge itself is the cut, matching
v1.22's pattern (D-05).

### 1.6 The measured tag ceiling — recorded as read output, never a derived instruction

```
$ gh release list --repo henols/firestarter --limit 5
3.0.0b14	Pre-release	3.0.0b14	2026-07-30T14:28:19Z
3.0.0b13	Pre-release	3.0.0b13	2026-07-28T10:01:43Z
3.0.0b12	Pre-release	3.0.0b12	2026-07-27T09:21:48Z
3.0.0b11	Pre-release	3.0.0b11	2026-07-26T11:10:01Z
3.0.0b10	Pre-release	3.0.0b10	2026-06-18T14:05:01Z

$ gh release list --repo henols/firestarter_app --limit 5
3.0.0b14	Pre-release	3.0.0b14	2026-07-30T14:58:35Z
3.0.0b13	Pre-release	3.0.0b13	2026-07-28T09:54:29Z
3.0.0b12	Pre-release	3.0.0b12	2026-07-27T09:21:09Z
3.0.0b11	Pre-release	3.0.0b11	2026-07-26T15:52:48Z
3.0.0b10	Pre-release	3.0.0b10	2026-06-18T14:03:37Z
```

**THE TAG CEILING, RECORDED HERE FOR PLAN 130-15 TO COMPARE AGAINST: `3.0.0b14` in both repos.**
Same `git tag --list '3.0.0b*' | sort -V | tail -1` output locally in both repos: `3.0.0b14`.
Neither repo shows a newer prerelease. **AGREES** with `130-DECISION.md`.

This is a **read**, not a computation. The auto-increment arithmetic (`is_beta_mode()` → tag-scan
max-plus-one) happens to predict the next value deterministically, one beyond the `3.0.0b14`
ceiling above, in both repos — that derivability is exactly why CONSTRAINT 5 is not relaxed: a
concurrent cut, an out-of-band tag, or a rehearsal-tag collision would change it. **No literal
next-version tag appears anywhere in §2's procedure.** Every tag position there is the placeholder
`<observed tag>`, to be filled from a fresh `gh release list` **after** the cut — the value plan
130-15 reads and fails closed against if it is not strictly newer than the `3.0.0b14` ceiling
recorded here.

### 1.7 Non-ignored changed-file counts — both pushes will trigger

Using each workflow's own `paths-ignore` set:

| Repo | Ignore set used | Non-ignored changed files vs `origin/beta` | `130-DECISION.md` value | Verdict |
|---|---|---|---|---|
| `firestarter` (`beta-build.yml`) | `**.md`, `**.sh`, `.gitignore`, `docs/**`, `documents/**`, `images/**`, `.vscode/**`, `.editorconfig/**` | **112** | 112 | **AGREES** |
| `firestarter_app` (`beta-release.yml`) | above plus `.github/**`, `tools/**` | **32** | 32 | **AGREES** |

Both counts are well above zero — `paths-ignore` suppresses neither cut. Separately,
`firestarter/.github/workflows/py32f071.yml` carries `push: branches: [beta]` with **no** paths
filter at all, so the LOUD ARM gate fires unconditionally on the outbound push regardless of which
files changed.

### 1.8 Working-tree dirt, all three repos (`git status --porcelain`)

**`firestarter`:** clean, no output. **AGREES** — matches `130-DECISION.md` item 10.

**`firestarter_app`:**
```
 M .gitignore
?? .coverage
?? .planning/config.json
?? SECURITY.md
?? write_test_port.sh
```
**Pre-existing dirt, predating this phase**, itemized so it is not mistaken for this plan's damage:
the modified `.gitignore` and the four untracked items (`.coverage`, `.planning/config.json`,
`SECURITY.md`, `write_test_port.sh`) were already present in `130-RESEARCH.md`'s and
`130-DECISION.md`'s own equivalent sections. This plan edited, staged, or committed none of them.
**AGREES.**

**`/workspaces` (meta):**
```
 M firestarter
 M firestarter_app
```
Both are the gitlink-versus-working-tip deltas named in §1.9 below. **AGREES.**

### 1.9 Meta gitlink assertion (D-04) — not staged or bumped by this plan

```
$ git ls-tree HEAD firestarter firestarter_app
160000 commit 5a89ee76dc4681abe18db259e57bb92f519520f4  firestarter
160000 commit cc9452f4db9a814ffb221bab767c24db67288365  firestarter_app
```

| Repo | Gitlink (meta HEAD) | Working tip (§1.1) | Match? |
|---|---|---|---|
| `firestarter` | `5a89ee7…` | `05c20bf…` | **No — expected.** D-04 **asserts** the gitlink matches the working tip; it does not pin it unchanged. Plan 130-03's two commits moved the firmware tip after the gitlink was last bumped. **Plan 130-16 owns re-bumping this gitlink** as part of its closing sweep — not this plan, and not the operator's merge either. |
| `firestarter_app` | `cc9452f…` | `cc9452f…` | **Yes.** No bump needed. |

This plan does **not** stage or commit either gitlink. `git status --porcelain` in `/workspaces`
shows ` M firestarter` and ` M firestarter_app` as the expected, unstaged consequence — the correct,
temporary state until plan 130-16 asserts and re-bumps it.

### 1.10 The gates, re-run on this exact tree

| Gate | Command | Result | vs. `130-DECISION.md` |
|---|---|---|---|
| `firestarter` suite | `python3 -m pytest tests/ -q` | **221 passed** | AGREES |
| `firestarter` native | `pio test -e native` | **141 test cases, 17 suites, 141 succeeded** | AGREES |
| `firestarter` sync gate | `FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q` | **41 passed** | AGREES |
| `firestarter_app` suite (C-13 gate) | `python3 -m pytest tests/ -q` | **1303 passed** | AGREES |
| `firestarter_app` codegen check | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | `OK: catalog valid (73 messages, version 1).` exit 0 | AGREES |
| `firestarter_app` codegen drift | regenerate + `ruff format` + `ruff check --add-noqa` + `git diff --exit-code firestarter/messages.py` | clean, exit 0 | AGREES |
| CLOSE-01 checker, default mode | `cd .planning/phases/130-*/ && python3 check_record_corrections.py` | `PASS` (exempt hits: block 23, line-label 5, inline-history 6, inline-allow 13, superseded 13) | AGREES |
| Claim gate, default mode | `cd .planning/phases/123-non-regression-baselines-gate-hardening && python3 check_permitted_claims.py` | **PASS** — scanned all four `130-*` contracted targets, all four carry the required silicon caveat | **MOVED — expected, and this is the point.** `130-DECISION.md` recorded this same gate as a transitional FAIL (missing `130-DECISION.md` itself, the fourth artifact). `130-DECISION.md`'s own commit supplied the fourth artifact; this measurement, run after that commit landed, is the first time all four contracted targets exist and the gate goes green. Not a regression — the arming (D-15) working as designed. |

**Go/no-go rule for the operator: if any row above is RED, do not push.** The `firestarter_app`
suite row is the one whose RED breaks the lockstep pair **asymmetrically** — a RED there, discovered
only after the firmware half has already published, leaves the two channels out of lockstep
(C-13). Every row above is green at hand-off time.

### 1.11 No mutation occurred during this re-measurement

```
$ git -C firestarter rev-parse origin/beta   → 5c9160a34b665878b05403ab014b959926feb6bf (unchanged)
$ git -C firestarter_app rev-parse origin/beta → e7d3ee8c8a41cd20e9159ab43b5cd969603d773e (unchanged)
$ git -C firestarter rev-parse HEAD          → 05c20bf59a4f0f73acf28d48d5dbbedab5724c5f (unchanged)
$ git -C firestarter_app rev-parse HEAD      → cc9452f4db9a814ffb221bab767c24db67288365 (unchanged)
```

Both remotes were fetched, never pushed to. No gitlink was staged. `git -C /workspaces log
--oneline -3` at the top of this task showed no commit touching `130-HANDOFF.md` — this file's own
commit, made after this write, is the only one this plan produces.

---

## 2. The operator procedure — instructions for a human, in no task anywhere in this phase

**Every command below is text to be read and run by a human.** This is the only place in the whole
phase these commands are written down, and they are written as *prose describing a procedure*, not
as an executable task, because `--auto` and `--chain` auto-approve human-verify checkpoints and an
`autonomous:` flag protects nothing against an outward-facing act. The structural gate is that no
`<automated>` block in any of this phase's sixteen plans contains any of these commands — proven
mechanically in §3, not merely asserted here.

### Step 1 — The D-02 blocking wording review (**precedes step 3**)

Read `130-RELEASE-NOTES-fw.md` and `130-RELEASE-NOTES-app.md` in full — not a diff, not a summary.
Look for what no scanner in this phase can detect: an implied overclaim, a misleading omission by
what it leaves out, or a tone that reads as more finished than the evidence supports. Four specific
questions to ask, drawn from this phase's own record:

1. Does the firmware release's headline read, to a skimmer, as "it works" rather than "it
   publishes"? (The permitted claim is publication only — nothing about the image running,
   booting, or installing.)
2. Does either body leave a reader thinking a PY32F071 board exists? (None does, anywhere.)
3. Is the USB-identity section clear that `1209:0001` is pid.codes' private-testing id and **not**
   an allocated PID — a disclosure, not an advertisement?
4. Does the app body's beta-only gating section read as an intentional design decision rather than
   an apology for a limitation?

This review **precedes step 3** below. The operator may overrule this phase's own D-17 judgment
(that a caveated disclosure of a non-allocated test id is not "advertising a USB identity") or
`130-RESEARCH.md`'s assumption A3 (that publishing an image is not "redistributing a device" under
pid.codes' terms) right here, before anything is pushed. Nothing downstream can undo a decision made
after step 3.

### Step 2 — Confirm the pre-flight state

Point at §1.10's gate table above and at `130-DECISION.md`'s own pre-flight section. **Go/no-go
rule: if any gate is RED, do not push.** The `firestarter_app` full suite is the one gate whose RED
breaks the lockstep pairing asymmetrically — a RED there discovered only *after* the firmware half
has already published leaves one channel cut and the other not, with no clean way to un-cut the
first (C-13, RESEARCH's single worst-outcome-avoidance measurement for this phase).

### Step 3 — The outbound merge and push, in both sub-repos

Two independent `--no-ff` merges and pushes, one per sub-repo. Either order works — the two cuts are
independent — but firmware first is recommended, so the `.hex` asset exists before the app's PyPI
publish (step 6) is dispatched.

```
# firestarter
cd firestarter
git checkout beta
git fetch origin
git merge --no-ff v1.23-py32f071-integration
git push origin beta

# firestarter_app
cd ../firestarter_app
git checkout beta
git fetch origin
git merge --no-ff v1.23-py32f071-integration
git push origin beta
```

What happens next, automatically, in both repos: `beta-build.yml` / `beta-release.yml` fire.
`.github/scripts/update_version.py` runs with an empty `BETA_VERSION` on a plain `beta` push, so
`is_beta_mode()` takes the beta path and the git-tag-scan auto-increment fires (§1.6's derivability —
still not a value to type anywhere). `stefanzweifel/git-auto-commit-action` lands the version bump
directly on `beta` in each repo. In `firestarter`, `py32f071.yml` also fires — **unconditionally**,
with no paths filter — as the LOUD ARM gate.

### Step 4 — Wait for CI, then read the observed tag (never compute it)

```
gh release list --repo henols/firestarter --limit 3
gh release list --repo henols/firestarter_app --limit 3
```

Both are read-only. The tag is **read**, never computed — even though §1.6 above shows the
arithmetic would predict the same value in both repos, no step in this procedure may substitute a
derived literal for what `gh release list` actually reports. Whatever it reports becomes
`<observed tag>` for every step below.

### Step 5 — Check the ARM gate's outcome before trusting a green `beta-build.yml` run

```
gh run list --repo henols/firestarter --workflow beta-build.yml --limit 3
gh run list --repo henols/firestarter --workflow py32f071.yml --limit 3
gh run view <run id> --repo henols/firestarter
```

`beta-build.yml`'s ARM build step is wrapped in `continue-on-error: true` by design (it must never
be able to block the three AVR assets) — **so a green `beta-build.yml` run is NOT evidence the py32
asset actually published.** `py32f071.yml` carries no such wrapping; it is the LOUD gate and says
what broke, if anything did. The asset-presence assertion itself — reading `gh release view
<observed tag> --json assets` against the real release — is plan 130-15's job (D-03), not this
step's; this step is only the CI-outcome read.

### Step 6 — Dispatch `publish.yml` manually for PyPI

```
gh workflow run publish.yml --repo henols/firestarter_app -f tag=<observed tag>
```

This is manual, not automatic, for a specific and recorded reason: `publish.yml`'s own in-file
comment states that when a release is created by another workflow using a PAT lacking `workflow`
scope, GitHub suppresses the `release.published` event that would otherwise fire this workflow.
Six of the thirteen previously published app betas never reached PyPI by the automatic path, and
`3.0.0b12`'s absence from PyPI (still unresolved as of this writing) corroborates it.

**Warning: the `tag` input flows directly into `publish.yml`'s checkout `ref:`
(`ref: ${{ github.event.inputs.tag || github.ref }}`).** It must be exactly the tag observed in
step 4 and nothing else — a guessed, remembered, or mistyped value here is a checkout-of-arbitrary-
ref vector, not merely a wrong version number.

### Step 7 — Post both release bodies, after step 1's review

```
gh release view <observed tag> --repo henols/firestarter --json body
gh release edit <observed tag> --repo henols/firestarter --notes-file .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-fw.md

gh release view <observed tag> --repo henols/firestarter_app --json body
gh release edit <observed tag> --repo henols/firestarter_app --notes-file .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-app.md
```

The first command of each pair is read-only, for inspecting the current (empty, CI-authored) body
before editing it. The posting itself — the `gh release edit` calls — is the operator's act; it
happens only after step 1's review is complete, never before.

### Step 8 — Hand back to plan 130-15

Resume execution at plan 130-15 for the channel verification: the observed tag (read fresh, not
carried from memory), the py32 asset-presence assertion against the real release (D-03), and the
PyPI resolution check from a clean temporary environment (CONSTRAINT 7). Plan 130-15 **will refuse
to proceed** unless a release tag strictly newer than the `3.0.0b14` ceiling recorded at §1.6 above
exists in **both** repos — so an accidentally auto-approved continuation fails closed and records a
clear stop, rather than claiming a cut that did not happen.

---

## 3. What this procedure deliberately does NOT include

- **Creating the `v1.23` annotated tag, or merging toward `main`.** Both stay with
  `/gsd-complete-milestone` (D-04), mirroring v1.21's and v1.22's precedent.
- **Any stable release.** Stable promotion is operator-gated standing policy; this close is
  beta-only, exactly like v1.22.
- **Deleting the stray `3.0.0b12` prereleases**, in either repo. They stay public — declined at
  v1.22 D-05 for the same reason that still holds: `b12` has been public for roughly a week and may
  already be installed by someone, and force-removing a published artifact is an operator act
  outside this close, not close work.
- **Editing any workflow trigger, in either repo.** No `on:` block, `paths-ignore` list, or
  `workflow_dispatch` default is touched by this phase.
- **Weakening `paths-ignore`, in either repo.**
- **Removing `continue-on-error` from `beta-build.yml`'s ARM step.** It comes off only when the
  target is validated on real silicon — no PY32F071 PCB exists, so that trigger is unreachable this
  milestone and the flag stays.
- **Any force push or history rewrite**, in any of the three repos.

### Mechanical proof the structural gate holds

```
$ cd .planning/phases/130-close-honesty-ledger-claim-gate-release-decision
$ python3 - <<'PY'
import re,glob
files = sorted(glob.glob('130-*-PLAN.md'))
all_bad = {}
for p in files:
    s=open(p).read()
    tasks=re.findall(r'<automated>(.*?)</automated>', s, re.S)
    bad=[]
    for t in tasks:
        for pat in ('git push','git tag','gh workflow run','gh release create','gh release edit','gh release delete','twine upload'):
            if pat in t: bad.append((pat,t[:80]))
        if re.search(r'git\s+(-C\s+\S+\s+)?merge\b', t): bad.append(('git merge',t[:80]))
    all_bad[p]=bad
for p,b in all_bad.items():
    print(p, '->', b if b else 'EMPTY')
PY
```

Result, run this session against all sixteen `130-*-PLAN.md` files (`130-01-PLAN.md` through
`130-16-PLAN.md`, including this file's own `130-14-PLAN.md`):

```
130-01-PLAN.md -> EMPTY
130-02-PLAN.md -> EMPTY
130-03-PLAN.md -> EMPTY
130-04-PLAN.md -> EMPTY
130-05-PLAN.md -> EMPTY
130-06-PLAN.md -> EMPTY
130-07-PLAN.md -> EMPTY
130-08-PLAN.md -> EMPTY
130-09-PLAN.md -> EMPTY
130-10-PLAN.md -> EMPTY
130-11-PLAN.md -> EMPTY
130-12-PLAN.md -> EMPTY
130-13-PLAN.md -> EMPTY
130-14-PLAN.md -> EMPTY
130-15-PLAN.md -> EMPTY
130-16-PLAN.md -> EMPTY
```

**Zero violations across all sixteen plans.** The privileged commands are absent from every
`<automated>` block in this phase — not decorated by a checkpoint type, structurally absent. A
fully auto-approved execution of every plan in this phase cannot publish anything; only the human
steps in §2 can.

---

## 4. What the operator is being asked to accept

Per `130-DECISION.md`'s ACCEPT row: **the merge is the cut, in both repos.** Both sub-repos carry
`push: branches: [beta]` triggers with git-tag-scan auto-increment, and both sit at the `3.0.0b14`
ceiling with the next tag absent from both (§1.6) — so the outbound `--no-ff` merge and push in §2
step 3 cuts the next beta by itself, in both repos, with no separate cut step wanted or needed. This
is the first publication of `firestarter_py32f071.hex` as a real release asset, which is the only
thing that makes the already-landed host capabilities (the DFU installer, `--dfu-probe`, `--usb-id`,
the beta-gated `py32f071` board choice) reachable by anyone outside this tree. The risk is bounded on
both sides of that pairing: **no PY32F071 board exists anywhere**, and the py32 board choice is
beta-only by construction (`_BOARD_CHOICES` is computed from the installed app's own version at
CLI-import time — a stable release of the host app hides it entirely).

---

*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Plan: 14*
*Written: 2026-08-02*
