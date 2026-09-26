# Phase 146 — Citation Register

**Owner requirement:** CLOSE-01 (the claim gate, armed against the real files and seen to fail) supplies
this register's first entries; every later section is owed by a later plan. This register is the evidence
floor the whole phase stands on.

**Measured:** 2026-08-17, live, read-only except where a command is explicitly marked as a write.

**Sections appended by later plans.** This file is written incrementally: §§0-2 by plan `146-01`, §3 the
fixture suite (`146-02`), §4 the claim gate's armed run and the plant-and-revert transcript (`146-04` /
`146-11`), §5 the freeze (`146-12`), §6 the delivery (`146-12`), §7 the close (`146-13`). A section that
does not yet exist is absent, never stubbed — an empty heading is a place a later reader can mistake for a
measurement that was taken and came back empty.

**Nothing in this register is copied from `146-RESEARCH.md`.** Every command below was re-run in this
task. Where a figure diverges from the value research or the plan recorded, the divergence is **stated
here** and the earlier document is left alone; no earlier record is edited to make a later measurement
agree with it. Three such divergences are recorded in §0 (rows 1, 6 and the porcelain enumeration) and one
non-divergence strengthening in §2.

**Exit-status discipline.** Every command's own status was captured with `rc=$?` **immediately after the
command**, never after a pipe. A recorded case in this project printed `EXIT=0` for a script that had just
printed a `FAIL:` line, because the status came from `tail`. Where a byte count is taken through `wc -c`,
the fetch and the count are separate commands so the fetch's own status is observable.

---

## 0. Phase-start before-state

Measured at `2026-08-17T14:40:03Z`, immediately after this phase's plan-creation commits and **before**
this plan's first commit.

### 0.1 The structural no-push oracle — upstream-ahead count, all three repos

| Field | Command (as run) | Result |
|---|---|---|
| meta ahead-count | `git -C /workspaces rev-list --count @{u}..HEAD` | **233** |
| meta upstream ref | `git -C /workspaces rev-parse --abbrev-ref @{u}` | `origin/gsd/v1.31-27c-programming-algorithm-fidelity` |
| meta upstream SHA | `git -C /workspaces rev-parse @{u}` | `b6aa1dcb` (short-8) |
| meta behind-count | `git -C /workspaces rev-list --count HEAD..@{u}` | **0** |
| `firestarter` ahead-count | `git -C /workspaces/firestarter rev-list --count @{u}..HEAD` | **61** |
| `firestarter` upstream ref / SHA | `git -C /workspaces/firestarter rev-parse --abbrev-ref @{u}` ; `… rev-parse @{u}` | `origin/gsd/v1.31-27c-programming-algorithm-fidelity` / `fb7949c0` |
| `firestarter` behind-count | `git -C /workspaces/firestarter rev-list --count HEAD..@{u}` | **0** |
| `firestarter_app` ahead-count | `git -C /workspaces/firestarter_app rev-list --count @{u}..HEAD` | **16** |
| `firestarter_app` upstream ref / SHA | `git -C /workspaces/firestarter_app rev-parse --abbrev-ref @{u}` ; `… rev-parse @{u}` | `origin/gsd/v1.31-27c-programming-algorithm-fidelity` / `4d18b645` |
| `firestarter_app` behind-count | `git -C /workspaces/firestarter_app rev-list --count HEAD..@{u}` | **0** |

**This is the phase's structural no-push oracle.** A `git push` advances the upstream tracking ref to
`HEAD`, so the ahead-count **drops** — to `0` for a plain push of the current tip. Plan `146-13` therefore
asserts **equality** against these three integers: meta `233`, `firestarter` `61`, `firestarter_app` `16`.
The three numbers may legitimately **rise** as this phase's own plans commit (they land in the meta repo
and, for the CLOSE-03 plans, in the two sub-repos); what they may never do is fall. The assertion 146-13
owes is therefore *ahead-count ≥ the value recorded here, in all three repos*, with a **fall** in any of
the three being the signal that a push happened. Recording the exact starting integers additionally lets
146-13 state how many commits this phase itself added.

**D-01 has no mechanical enforcement, and this register is the only substitute.** `git push`,
`gh workflow run` and `gh release` are all in this project's permission allowlist — nothing in the harness
stops an executor from pushing. The recorded before-state is the whole enforcement mechanism.
**No plan in this phase may edit `.claude/settings.local.json` or add any permission-allowlist entry**;
tightening the allowlist mid-phase would itself be an unrecorded change to the enforcement surface, and
loosening it is the failure this row exists to detect.

**A second, independent reading of the sub-repo positions, stated rather than reconciled.** Against
`origin/beta` — a *different* ref from each branch's own tracking ref — the same two repos measure:

| Repo | Command (as run) | Result |
|---|---|---|
| `firestarter` vs `origin/beta` | `git -C /workspaces/firestarter rev-list --count origin/beta..HEAD` ; `… rev-list --count HEAD..origin/beta` | **66 ahead / 2 behind** (`origin/beta` = `6fab4eaf`) |
| `firestarter_app` vs `origin/beta` | `git -C /workspaces/firestarter_app rev-list --count origin/beta..HEAD` ; `… rev-list --count HEAD..origin/beta` | **16 ahead / 0 behind** (`origin/beta` = `4d18b645`) |

`146-CONTEXT.md` `<code_context>` records the firmware as *"66 ahead / 2 behind"* — that figure is against
`origin/beta`, and it still holds exactly. It is **not** the same measurement as the `@{u}` row above
(`61 ahead / 0 behind`), because the branch tracks its own pushed tip, not `beta`. Both readings are
recorded; neither is corrected into the other. The firmware's **2 behind `origin/beta`** is a real fact
that `/gsd-complete-milestone` will have to resolve at merge time, and it is not this phase's to fix.

### 0.2 Branch and HEAD, all three repos

| Field | Command (as run) | Result |
|---|---|---|
| meta branch | `git -C /workspaces rev-parse --abbrev-ref HEAD` | `gsd/v1.31-27c-programming-algorithm-fidelity` |
| meta HEAD | `git -C /workspaces rev-parse HEAD` | `d2c212f1a775347d3a151b2c26bcd2977a178cb1` |
| `firestarter` branch | `git -C /workspaces/firestarter rev-parse --abbrev-ref HEAD` | `gsd/v1.31-27c-programming-algorithm-fidelity` |
| `firestarter` HEAD | `git -C /workspaces/firestarter rev-parse HEAD` | `fa6c9c77225594558ca90e24eda69f05c279f7a9` |
| `firestarter_app` branch | `git -C /workspaces/firestarter_app rev-parse --abbrev-ref HEAD` | `gsd/v1.31-27c-programming-algorithm-fidelity` |
| `firestarter_app` HEAD | `git -C /workspaces/firestarter_app rev-parse HEAD` | `68820a6359ef117834de72fa9a9835a44dab2c31` |

All three repos are on the milestone branch. Neither `beta` nor `main` is checked out anywhere.

### 0.3 Working-tree porcelain, all three repos — the pre-existing dirt enumerated

| Field | Command (as run) | Result |
|---|---|---|
| meta porcelain line count | `git -C /workspaces status --porcelain \| wc -l` | **8** |
| `firestarter` porcelain line count | `git -C /workspaces/firestarter status --porcelain \| wc -l` | **0** |
| `firestarter_app` porcelain line count | `git -C /workspaces/firestarter_app status --porcelain \| wc -l` | **7** |

**Meta repo, all eight entries enumerated by path** (`git -C /workspaces status --porcelain`, verbatim):

```
 M .gitignore
 M .planning/STATE.md
 M firestarter
 M firestarter_app
?? .claude/
?? .planning/VALIDATED-EPROMS.md
?? package-lock.json
?? package.json
```

**`firestarter_app`, all seven entries enumerated by path** (`git -C /workspaces/firestarter_app status
--porcelain`, verbatim):

```
?? .planning/config.json
?? SECURITY.md
?? datasheets/M27C1001.pdf
?? datasheets/M27C512.pdf
?? datasheets/W27C512.pdf
?? datasheets/W27E257.pdf
?? write_test_port.sh
```

**`firestarter` is clean — 0 lines.** This matters twice: it is the baseline both sub-repo suites assert
(`firestarter/tests/test_flash_path_record_sync.py` asserts the *whole* firmware repo's porcelain, and
`firestarter_app/tests/test_py32_flash_map_host.py` asserts the same for the sibling firmware repo), and
it is the state plan `146-03` must restore after building ARM out-of-tree.

**Divergence from the plan's expected dirt list, recorded not reconciled.** `146-01-PLAN.md` predicts the
meta repo carrying modified `.gitignore`, both gitlinks, and untracked `.claude/`,
`.planning/VALIDATED-EPROMS.md`, `package.json`, `package-lock.json` — **seven** entries. The observed
count is **eight**: `.planning/STATE.md` is also modified, and the plan does not predict it. Cause,
identified rather than assumed: the diff is the `/gsd-execute-phase` orchestrator's own execution-start
state write — `status: "Ready to execute"` → `executing`, `last_updated` bumped, `last_activity_desc`
prefixed with an execution-started sentence, `**Current focus:**` moved from Phase 145 to Phase 146, and
the `## Current Position` block rewritten. It is **8 insertions / 8 deletions**
(`git diff --numstat -- .planning/STATE.md` → `8	8	.planning/STATE.md`), so the file's line count is
unchanged. This entry is **expected dirt for every plan in this phase after the first**, and no plan should
read it as its own damage.

**A second observation about that same write, recorded because a later plan will trip over it.** The
orchestrator's rewrite of `## Current Position` left three sentence fragments dangling — `Plan: 1 of 13`
is now followed by the orphaned continuation `` `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md`,
flipped by `145-09` … ``, and `Status: Executing Phase 146` by `` `validated` (three 64 KiB cycles …) ``.
The replaced lines were the *first* lines of multi-line sentences and the verb replaced only those first
lines. This is the same class of defect this project has recorded eight times for `gsd-tools` state verbs.
It is **not repaired here**: `146-01` is not the plan that owns `STATE.md` prose, twelve other plans are
live in this same working tree, and a hand-repair now would collide with the next state write. It is
recorded so whichever plan next writes `STATE.md` repairs it from this description rather than
rediscovering it.

**The pre-existing `.planning/ROADMAP.md` heading rename is NOT in the expected-dirt list, by design.**
`146-CONTEXT.md` warned that a 2-line Phase 146 heading rename was uncommitted at discussion time. It was
folded into the plan-creation commit `6560f9a8`, so `ROADMAP.md` is **clean** at phase start and must stay
clean until a plan deliberately edits it. Confirmed by its absence from the eight-line porcelain above.

### 0.4 Tracked gitlink SHAs versus the live sub-repo HEADs — a recorded delta, not a criterion

| Field | Command (as run) | Result |
|---|---|---|
| tracked gitlinks | `git -C /workspaces ls-tree HEAD firestarter firestarter_app` | `160000 commit 0933bd7d602efb30e4a666e8231ecf724e90ab09  firestarter`<br>`160000 commit cc036e8dc3cd77bbdfc7ec5190d79cdb172153c7  firestarter_app` |
| live `firestarter` HEAD | `git -C /workspaces/firestarter rev-parse HEAD` | `fa6c9c77225594558ca90e24eda69f05c279f7a9` |
| live `firestarter_app` HEAD | `git -C /workspaces/firestarter_app rev-parse HEAD` | `68820a6359ef117834de72fa9a9835a44dab2c31` |
| `firestarter` gitlink lag | `git -C /workspaces/firestarter rev-list --count 0933bd7d..HEAD` | **70 commits** |
| `firestarter_app` gitlink lag | `git -C /workspaces/firestarter_app rev-list --count cc036e8d..HEAD` | **27 commits** |

**Both gitlinks are stale by the whole milestone and have been at every point in v1.31.** `0933bd7d` and
`cc036e8d` are v1.30-era tips; the live branches are 70 and 27 commits past them respectively, which is
why both appear as ` M firestarter` / ` M firestarter_app` in §0.3's porcelain. This is recorded **as a
fact**, deliberately not as a criterion: **no plan in this phase may write an acceptance criterion
asserting the gitlinks match the sub-repo tips**, because they do not and never did this milestone, and
such a criterion would be RED for a bookkeeping reason rather than a record defect. `146-CONTEXT.md`
§"Claude's Discretion" leaves the *form* of any end-of-phase gitlink assertion open; the form chosen here
is "record the delta at both ends and state the direction it moved", never "assert equality".

### 0.5 gh#15 read-only state — five oracles plus three derived counts

All read-only. Nothing below writes to the issue.

| Field | Command (as run) | Result | Research's expected value | Match? |
|---|---|---|---|---|
| `state` | `gh api graphql -f query='{ repository(owner:"henols", name:"firestarter_prom") { issue(number:15) { number state title createdAt updatedAt lastEditedAt comments(first:10){ totalCount nodes { databaseId url createdAt updatedAt lastEditedAt author{login} } } } } }'` | `OPEN` | `OPEN` | **yes** |
| `updatedAt` | same query | `2026-08-09T19:32:04Z` | `2026-08-09T19:32:04Z` | **yes** |
| `lastEditedAt` | same query | `null` | `null` | **yes** |
| comment `totalCount` | same query | **1** | `1` | **yes** |
| comment `databaseId` | same query | **`5233463320`** | `5233463320` | **yes** |
| comment `lastEditedAt` | same query | `null` | `null` | **yes** |
| `createdAt` | same query | `2026-07-12T09:15:27Z` | `2026-07-12T09:15:27Z` | **yes** |
| `title` | same query | `Implement protocol-specific EPROM programming algorithms in firmware` | same | **yes** |
| comment `author.login` | same query | `henols` | — | — |
| body byte length | `gh issue view 15 --repo henols/firestarter_prom --json body -q .body > /tmp/gsd146_body.txt` (`rc=0`), then `wc -c < /tmp/gsd146_body.txt` | **5964** bytes | `5964` | **yes** |
| unticked-box count | `grep -c '^- \[ \]' /tmp/gsd146_body.txt` | **9** | `9` | **yes** |
| acceptance-criteria tail identity | `awk '/^## Acceptance criteria/,0' /tmp/gsd146_body.txt \| diff - .planning/phases/139-gh-15-correction-outward/139-GH15-ORIGINAL-CRITERIA.md` — `rc=0` | **empty diff** | empty | **yes** |
| labels | `gh issue view 15 --repo henols/firestarter_prom --json labels -q .labels` | `[]` | `[]` | **yes** |

**Zero divergence across all thirteen oracles.** All five of D-07's measured premises still hold: the
issue is OPEN, the body is unedited, it carries exactly one comment, that comment is `#5233463320`, and
the nine acceptance boxes are all still unticked. `146-12`'s `1 → 2` comment-count assertion therefore
stands on a re-measured `1`, not an inherited one.

**Two recorded oracle facts, both re-confirmed here.**

1. **`gh issue view --json lastEditedAt` does not exist.** Run bare, with its status captured immediately
   (`gh issue view 15 --repo henols/firestarter_prom --json lastEditedAt > /tmp/gsd146/lasted.txt 2>&1;
   rc=$?`), it exits **`rc=1`** and prints `Unknown JSON field: "lastEditedAt"` followed by an
   `Available fields:` list that does not contain it. The body-edit oracle is **GraphQL-only** — the exact
   query used above. Any plan that writes `gh issue view --json lastEditedAt` fails at the gate, not at
   review.
2. **`updatedAt` bumps on comment creation and is NOT a body-edit oracle.** `createdAt` is
   `2026-07-12T09:15:27Z`; `updatedAt` is `2026-08-09T19:32:04Z`, **identical to the comment's own
   `createdAt`**. GitHub bumped it when plan `139-05` posted comment `#5233463320`, not because the body
   was edited — `lastEditedAt` is still `null`. **Posting the 146 comment will bump `updatedAt` a second
   time**, so an acceptance criterion written against `updatedAt` will fail for the wrong reason. Use
   `lastEditedAt is null`.
3. **A body-byte-length precision note, carried forward from `139-CITATIONS.md` §0 and not re-derived
   here.** `wc -c` on the fetched body is the byte oracle and gives `5964`; `jq`'s `.body | length` counts
   Unicode *codepoints* and gives `5950` for the same unchanged body, because the body contains multi-byte
   UTF-8 characters. The 14-byte gap is arithmetic. `wc -c` is used above and by both prior registers.

### 0.6 Phase 130 record-gate baseline — **RED at phase start**, with the cause identified

| Field | Command (as run) | Result |
|---|---|---|
| record gate, default targets | `python3 .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py > /tmp/gsd146/rec_baseline.txt 2>&1; rc=$?` | **`rc=1`** |
| stdout, verbatim | `cat /tmp/gsd146/rec_baseline.txt` | `FAIL: 1 arm-toolchain-absent:`<br>`  /workspaces/.planning/STATE.md:11` |

**This diverges from the baseline `146-01-PLAN.md` recorded (`exit 0`, tally
`{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}`), and the
divergence is real, not a measurement artefact.** It is recorded here rather than smoothed over, and the
plan is not edited to agree with it.

**Root cause, bisected commit by commit.** The gate resolves five `_REPO_ROOT`-absolute targets
(`check_record_corrections.py:163-171`) and honours a `FIRESTARTER_RECORDSCAN_TARGETS` env seam
(`:185`, `:427-439`). Substituting each candidate `STATE.md` revision for the live one through that seam,
holding the other four targets at their live paths, isolates the regression to a single commit:

| `STATE.md` revision under test | Command (as run) | Result |
|---|---|---|
| `3e1903be` | `FIRESTARTER_RECORDSCAN_TARGETS="…/PROJECT.md:/tmp/gsd146/S_3e1903be.md:…/ROADMAP.md:…/v1.23-REQUIREMENTS.md:…/py32f071-port-branch-state.md" python3 …/check_record_corrections.py` | `rc=0` — `PASS`, tally `{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}` |
| `e0c0a818` | same shape | `rc=0` — `PASS`, identical tally |
| `39802fb7` | same shape | `rc=0` — `PASS`, identical tally |
| `6560f9a8` | same shape | `rc=0` — `PASS`, identical tally |
| **`d2c212f1`** (current HEAD) | same shape | **`rc=1`** — `FAIL: 1 arm-toolchain-absent: /tmp/gsd146/S_d2c212f1.md:11` |
| working tree (uncommitted) | default targets, no seam | **`rc=1`** — same single hit at `.planning/STATE.md:11` |

**The regression landed in `d2c212f1` — `docs(146): record planning completion -- 13 plans in 7 waves` —
the planning session's own state write.** That commit wrote into `last_activity_desc` (line 11) the
sentence *"cmake, ninja and arm-none-eabi-gcc are ALL ABSENT"*, and the needle
`arm-toolchain-absent` at `check_record_corrections.py:261-263` is the two-token lookahead
`(?=.*arm-none-eabi-gcc)(?=.*absent)`, case-insensitive, with no exemption label on that line. The plan's
recorded baseline was therefore measured at `6560f9a8`, one commit before the commit that recorded the
plan — the tally the plan quotes is correct **for that revision** and is reproduced verbatim in the table
above as the last-green reading.

**Both readings stated, neither reconciled.** Last-green tally at `6560f9a8`, verbatim:

```
PASS: scanned .planning/PROJECT.md, <STATE.md>, .planning/ROADMAP.md, .planning/milestones/v1.23-REQUIREMENTS.md, .planning/notes/py32f071-port-branch-state.md; exempt hits by verdict: {'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}
```

Current reading at `d2c212f1` and in the working tree: `rc=1`, one unlabelled `arm-toolchain-absent` hit
at `.planning/STATE.md:11`, no tally printed (the gate prints its bucket and returns before the `PASS:`
line).

**Not repaired in this plan, and why.** Three reasons, all structural rather than convenient. (i) The
offending text lives inside the YAML frontmatter string `last_activity_desc`, which every `gsd-tools`
state verb rewrites wholesale — an exemption marker placed inside it is destroyed by the next state write,
including the ones this plan itself makes at its close. (ii) `.planning/STATE.md` is shared by all
thirteen plans in this phase and twelve of them are live in this same working tree; an unrelated hand-edit
now is a collision. (iii) `146-05` is the plan that owns `⚠ CORRECTION` blocks in the three live records
and explicitly owes a record-gate re-run after every insertion — it is the correct owner. **Hand-off to
`146-05`:** the hit is a single line, the needle is a collocation rather than a false figure, and the
statement itself is *not* false as written (the tools genuinely were not installed in this devcontainer;
what is stale is the stronger reading *"not installable"*). The cheapest correct discharge is an inline
label on that line's own text, or a rewording that drops the `absent` collocation, chosen by whichever
mechanism survives the next state write.

**A measured correction to the line-shift hazard the plan warns about.** `146-01-PLAN.md` and
`146-PATTERNS.md` both state that twelve `superseded` exemptions enumerating explicit 1-based line numbers
sit in the files this phase edits, so any insertion above one silently orphans it. Measured here, by
counting the markers per file:

| File | `grep -o 'recordscan:supersedes' \| wc -l` |
|---|---|
| `.planning/PROJECT.md` | **0** |
| `.planning/ROADMAP.md` | **1** — and it is *prose describing an orphaned marker* at `:3130`, not an active marker |
| `.planning/STATE.md` | **0** |
| `.planning/milestones/v1.23-REQUIREMENTS.md` | **0** |
| `.planning/notes/py32f071-port-branch-state.md` | **7** |

All twelve `superseded` *hits* come from those **seven** markers in
`.planning/notes/py32f071-port-branch-state.md` (`:172-178`), whose `lines=` lists enumerate
`12` · `20,21,22,23,24,29` · `53` · `61` · `94` · `96` · `107` — 1 + 6 + 1 + 1 + 1 + 1 + 1 = **12** line
references, exactly the tally's `'superseded': 12`. **Zero active `lines=N` markers exist in
`ROADMAP.md`, `PROJECT.md` or `STATE.md`** — the three files `146-05` inserts into. The line-shift
orphaning hazard therefore does **not** apply to `146-05`'s insertion sites. Both readings are recorded:
the plan's caution is over-stated as to *where* the markers live, and its prescribed remedy (append after
the corrected text, never insert above it) remains cheap, harmless and worth following anyway, because the
`_BLOCK_CLOSER_RE` mechanism at `check_record_corrections.py:303` requires a block to sit **after** the
text it corrects regardless of any line-number marker.

---

## 1. Pinning strategy

**Citations pin to commit SHAs and blob SHAs, never to branch names.** A branch name resolves to a
different tree tomorrow, and a line-number citation written against a moving ref points at the wrong lines
without ever returning an error — the recorded failure mode is a permalink built from local line numbers
that returned HTTP 200 against a pushed tip whose content had shifted ten lines.

Every figure in every artifact this phase produces is one of exactly two things:

1. **Measured in the plan that writes it**, with the literal command recorded next to the result in this
   register — the shape of every table in §0 above; or
2. **Cited to a `file:line` or a commit/blob SHA** in a record whose identity is pinned in §2 below.

Nothing is carried forward from an earlier document's *rendering* of a number. Where this phase re-measures
a figure an earlier record already states and the two agree, the agreement is recorded as a
re-confirmation (§0.5's thirteen gh#15 oracles). Where they disagree, **both readings are stated and
neither is edited into the other** (§0.1's two sub-repo position readings; §0.6's last-green versus current
record-gate result).

**Two consequences this phase's later plans inherit.** First, a citation into a `.planning` artifact is
pinned by **blob SHA** rather than by pushed-tip URL wherever the artifact is unpushed — 233 meta commits
are unpushed at phase start (§0.1), so a `raw.githubusercontent.com` permalink into this phase's own
directory would 404, exactly as `138-BASELINE.md` did for Phase 139. Second, **no citation in this phase
requires a push to resolve**: the phase's only outward act is one issue comment (`146-12`), and every
supporting record is cited by local `file:line` plus the blob SHA recorded in §2.

**Forbidden-claim citation discipline (D-14), stated here because it is a pinning rule.** A forbidden
phrase is cited by `file:line` plus its finding id and is **never reproduced as text**. This is not
stylistic: a closing artifact that quotes a forbidden phrase in order to disclaim it trips this phase's own
claim gate, which is what happened to all six `125-0N-SUMMARY.md` files. The live instance in this phase's
own source material is `145-BENCH-LOG.md:2707-2709`, boundary 2 — cited by location throughout, never
quoted. `145-08-SUMMARY.md`, `139-GH15-COMMENT.md` and `139-GH15-ORIGINAL-CRITERIA.md` all measure zero
hits under the pattern table and are safe to quote verbatim.

---

## 2. Anchor verification table

Every source record this phase cites has its identity pinned here by `git hash-object` blob SHA, so a later
plan can demonstrate it cited an **unmoved** document. Each row also carries the byte length and the blob
SHA git has tracked at `HEAD` (`git rev-parse HEAD:<path>`), so a working-tree edit to a cited record is
visible as a mismatch between the two SHA columns rather than being invisible.

Commands as run, one per file: `git hash-object <path>` · `wc -c < <path>` · `git rev-parse HEAD:<path>`.

| # | Cited record | `git hash-object` blob SHA | Bytes | Tracked blob at `HEAD` | Identical? |
|---|---|---|---|---|---|
| 1 | `.planning/phases/145-bench-validation/145-BENCH-LOG.md` | `0165be9da5432d0e8f37c4ae822cd5952ebd3e3d` | 216526 | `0165be9da5432d0e8f37c4ae822cd5952ebd3e3d` | **yes** |
| 2 | `.planning/phases/145-bench-validation/145-08-SUMMARY.md` | `48efbb6d3b66e5df7a808c10c7669bee90ee882b` | 17264 | `48efbb6d3b66e5df7a808c10c7669bee90ee882b` | **yes** |
| 3 | `.planning/phases/144-tests-build-verification/144-TEST-RECORD.md` | `dd54c0107f8cc8b032dbf021f0157a61f1098c9f` | 43039 | `dd54c0107f8cc8b032dbf021f0157a61f1098c9f` | **yes** |
| 4 | `.planning/phases/143-host-timeout-progress-pulse-override/143-HOST-RECORD.md` | `89817decbf3091b0e57b6c01d0a2ff75ac459710` | 46302 | `89817decbf3091b0e57b6c01d0a2ff75ac459710` | **yes** |
| 5 | `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md` | `efb254b26e82be72167b3ac9a7a3cf52eb381b19` | 40368 | `efb254b26e82be72167b3ac9a7a3cf52eb381b19` | **yes** |
| 6 | `.planning/phases/140-parameter-table/140-PARAM-TABLE-RECORD.md` | `d76e8b6688b5366dc8b78e6c8876848c67d8e674` | 27155 | `d76e8b6688b5366dc8b78e6c8876848c67d8e674` | **yes** |
| 7 | `.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md` | `d77a639c62751c197e465ec637f24f330dab35ef` | 12193 | `d77a639c62751c197e465ec637f24f330dab35ef` | **yes** |
| 8 | `.planning/phases/139-gh-15-correction-outward/139-GH15-ORIGINAL-CRITERIA.md` | `01d06f2020b8600faa2907bec22bb08a0172b7a6` | 693 | `01d06f2020b8600faa2907bec22bb08a0172b7a6` | **yes** |
| 9 | `.planning/STATE.md` | `9d2a65c9282c668a9452deacf0156e57a5db4515` | 320485 | `fd94b6fa4f5f05f3c8295062f479337c0444191a` | **NO — see below** |

**Eight of nine are byte-identical to their tracked blobs at `HEAD` `d2c212f1`.** No cited phase record
carries an uncommitted edit, so every `file:line` citation this phase writes into those eight resolves
identically for a reader at `HEAD` and for a reader of the working tree.

**Row 7 is a re-confirmation, not a new measurement.** `146-CONTEXT.md` §canonical_refs records the posted
gh#15 correction as *"comment `#5233463320`, frozen blob `d77a639c`, 12193 bytes"*. Both the blob SHA and
the byte count re-derive here exactly, from the file rather than from the citation. Combined with §0.5's
live `databaseId` of `5233463320`, the artifact `146-12` grades against and the comment a stranger reads
are demonstrably the same text.

**Row 9 diverges, deliberately and traceably.** `.planning/STATE.md`'s working-tree blob
(`9d2a65c9`, 320485 bytes) differs from its tracked blob at `HEAD` (`fd94b6fa`) because of the
orchestrator's uncommitted execution-start write enumerated in §0.3 — 8 insertions / 8 deletions, line
count unchanged. Consequence for later plans, stated explicitly: **a citation into `STATE.md` by line
number is the one citation in this set that is not yet pinned**, because the file has a pending edit and
will take several more before the phase closes. `146-CONTEXT.md` directs the ledger to quote the MERGE-05
+96 B adjudication wording from `STATE.md`'s `## Decisions` section (authored at commit `d02a88a0`
expressly as *"quotable verbatim"* for CLOSE-02); whichever plan quotes it should pin that quotation to
`d02a88a0` — the commit that authored the wording — rather than to a working-tree line number.

**One anchor named in `146-01-PLAN.md` is deliberately not a row here.** The plan lists nine records; all
nine are present above. No tenth anchor was added, and none was dropped.

---

## 3. The fixture suite — every leg seen to fire, and the one leg seen RED for its named reason

**Owner:** plan `146-04`. **Measured:** 2026-08-17T15:46:21Z, at meta commit `28340b37` (the fixture
commit), `Python 3.12.13`, `pytest 9.1.1`, from `/workspaces`.

**Attribution divergence, recorded rather than smoothed over.** This register's own header (`:9-11`) says
§3 is owed by plan `146-02`. It is not: `146-02-PLAN.md` owns the ARM build record and `146-04-PLAN.md`
owns this suite and instructs that §3 be appended by it. Per this register's stated discipline the earlier
text is **left alone** and the divergence is stated here. Section ownership from §4 onward is unaffected.

**Section 3 discharges D-12's *first* proof only.** Fixtures prove the pattern table, the per-file caveat
rules and the resolution branches. They cannot prove the gate is wired to the files that ship — by
construction a fixture is not a closing artifact. §4 is where plan `146-11`'s plant-and-revert against a
real, tracked closing artifact lands, and CLOSE-01 is not discharged by this section alone.

**Forbidden phrases are cited here by label id or by `file:line`, never reproduced.** Two citation forms
were measured safe against the gate's own table before being used below, because writing a record about a
phrase-scanner is exactly how a record plants the phrase it is documenting:

| Citation form used below | `scan_text` verdict | Why it is safe |
|---|---|---|
| `confirmed-working` (hyphenated label id) | **0 hits** | pattern 7 is `confirmed\s+working`; `\s` does not match a hyphen |
| `` `\bproven\b` `` (pattern 10 written as its own regex) | **0 hits** | the leading `\b` is preceded by the word character `b`, so no boundary exists at `p` |
| `planted_proven_unqualified.md` (the fixture's filename) | **0 hits** | `_` is a word character, so pattern 10's leading boundary fails |
| pattern 10's label id spelled out with its hyphen — the string the gate prints inside its bucket line, quotable only as `test_check_claims_v131.py:242` | **1 hit** | a hyphen IS a non-word character, so the trailing boundary holds — **deliberately not written anywhere in this register** |

**The row above was measured, not predicted, and it cost one revision.** §3 was first written with that
label id spelled out in this very table, as a warning; re-scanning the register found the warning had
planted the phrase it warned about — one hit, on the table row itself. The row was rewritten to cite the
suite line instead. That is the recorded failure mode reproducing itself inside the document describing it,
and the only reason it was caught is that the scan was re-run after the prose was written rather than
reasoned about.

This register measured **0** forbidden-phrase hits before §3 was appended and **0** after that revision;
§3.7 records the re-measurement. The suite file itself retains exactly **two** hits, both at
`test_check_claims_v131.py:242` and `:253`, and both are the load-bearing assertion literal the gate prints
in its own bucket line. Every hit that had been this plan's own prose was rewritten away.

### 3.1 The five fixture probes — run BEFORE any assertion was written

Command as run, from the phase directory, importing the gate by file path and calling its own `scan_text`
under the FULL caveat set (a fixture basename is absent from `_CAVEAT_RULES`, so `_required_caveats_for()`
fails closed and holds every fixture to both caveats — probed and confirmed per row):

```
python3 -c "import importlib.util, os
s=importlib.util.spec_from_file_location('g','146-check-claims.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
full=m._ALL_CAVEAT_LABELS
for name in sorted(os.listdir('fixtures')):
    t=open(os.path.join('fixtures',name),encoding='utf-8').read()
    print(name, m.scan_text(t,name,full), sorted(m._required_caveats_for(name)))"
```

`full caveat labels: ['ceiling-narrowing', 'ceiling-voltage']`

| Fixture | `forbidden_hits` returned, verbatim | `missing_caveats` returned | Rule resolved to |
|---|---|---|---|
| `clean_control.md` | `[]` | `[]` | `['ceiling-narrowing', 'ceiling-voltage']` |
| `clean_control_second.md` | `[]` | `[]` | `['ceiling-narrowing', 'ceiling-voltage']` |
| `planted_forbidden_claim.md` | `[('confirmed-working', <matched text>, 14)]` | `[]` | `['ceiling-narrowing', 'ceiling-voltage']` |
| `planted_missing_caveat.md` | `[]` | `['ceiling-narrowing']` | `['ceiling-narrowing', 'ceiling-voltage']` |
| `planted_proven_unqualified.md` | `[(<pattern 10>, <matched text>, 12)]` | `[]` | `['ceiling-narrowing', 'ceiling-voltage']` |

The third column of the two plant rows is `[]` deliberately: each plant carries **both** caveats, so each
fails for exactly **one** reason and a leg asserting on it cannot be satisfied by the wrong failure. The
matched-text field is elided in the two plant rows for the reason given above; the label and the line
number are the citation, and the text itself is at `fixtures/planted_forbidden_claim.md:14` and
`fixtures/planted_proven_unqualified.md:12`.

**Nothing was assumed.** Both plants returned exactly one label each, and the second plant's single hit
confirms the elision discipline works mechanically: its own line-2 comment writes pattern 10 in regex form
and did **not** self-trip, which is why the total is 1 and not 2.

Fixture blobs at commit `28340b37`, `git hash-object` / `wc -c` / `wc -l`:

| Fixture | Blob SHA | Bytes | Lines |
|---|---|---|---|
| `clean_control.md` | `f849500065ff183782d3588c13281aab6baa2bf2` | 878 | 11 |
| `clean_control_second.md` | `1c96e8445f77eea0cba2f2e60ec00ca17d1ac2e8` | 1032 | 13 |
| `planted_forbidden_claim.md` | `5776a108ffae81fc47779f80412689a2515ab047` | 923 | 14 |
| `planted_missing_caveat.md` | `8c2d19ab52d0d9d712397e35f1baae63b2749678` | 850 | 11 |
| `planted_proven_unqualified.md` | `f719e7b3cb2c74ea481d0fe90363cf8f7667db16` | 860 | 12 |

### 3.2 Full suite run — 14 passed, 1 failed

```
python3 -m pytest .planning/phases/146-…/test_check_claims_v131.py -o addopts="" -q
```
`rc=1` (captured immediately after the command, never after a pipe)

```
1 failed, 14 passed in 0.52s
FAILED …/test_check_claims_v131.py::test_armed_against_the_five_real_closing_artifacts
```

Leg count asserted independently: `grep -c '^def test_' …/test_check_claims_v131.py` → **15**.
Seam references: `grep -c 'FIRESTARTER_CLAIMSCAN_TARGETS_146'` → **6** (set, pop, and four prose
mentions). Donor seam names `TARGETS_V130` / `TARGETS_V131`: `grep -c` → **0**, so this suite cannot aim
at Phase 139's live gate in this same milestone.

### 3.3 The control that makes the single failure attributable

```
python3 -m pytest …/test_check_claims_v131.py -o addopts="" -q \
  --deselect …/test_check_claims_v131.py::test_armed_against_the_five_real_closing_artifacts
```
`rc=0`

```
..............                                                           [100%]
14 passed, 1 deselected in 0.56s
```

**Fourteen of fifteen legs pass on their own merits.** Without this run, the full suite's `rc=1` would be
consistent with any number of broken legs; with it, the one red is pinned to the one leg that is supposed
to be red today. The deselection exists **only** in this transcript — the suite file carries no `xfail`,
no `skip` and no deselection of its own, because a leg marked expected-to-fail in the file is a leg nobody
will ever look at again.

### 3.4 Leg 9 observed RED — for its NAMED reason, verbatim

```
python3 -m pytest …/test_check_claims_v131.py::test_armed_against_the_five_real_closing_artifacts \
  -o addopts="" -q
```
`rc=1`

Failure output, verbatim (the assertion message and the gate's own captured stdout):

```
E       AssertionError: gate exited 1 against the five real default targets -- expected PASS + exit 0. If
        the output below reports the five closing artifacts as 'not found on disk', this is the EXPECTED
        pre-146-11 red and the arming contract is intact; any other message is a defect in this suite.
E         stdout:
E         FAIL: scan target(s) not found on disk -- the gate cannot vacuously pass with a target silently
        skipped: ['/workspaces/.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-LEDGER.md',
        '…/146-CORRECTIONS.md', '…/146-GH15-RECONCILIATION.md', '…/146-RELEASE-NOTES-fw.md',
        '…/146-RELEASE-NOTES-app.md']
E
E         stderr:
E
E       assert 1 == 0
…/test_check_claims_v131.py:406: AssertionError
```

**This is the right red, and the check is not rhetorical.** The failure is the gate's own fail-closed
missing-target branch, naming **all five** closing artifacts by absolute path. It is specifically **not**
a collection error, **not** an import error of a filename that is no valid Python identifier, **not** a
missing fixture, **not** a wrong basename and **not** a seam-name typo — each of which would have produced
a different first line and would have been a defect in plan `146-04` rather than the expected state. The
distinction was verified by reading the failure text, not inferred from the exit status.

**Leg 9's GREEN is plan `146-11`'s to record, and its second RED comes free.** `146-11` authors the five
closing artifacts, at which point this same leg goes green with no edit to the suite; and `146-11`'s
plant-and-revert against one of those real artifacts drives this same gate red a second time, on a real
file rather than a fixture. That is the pair D-12 asks for: a leg that has been seen red for a verified
reason and green for a verified reason is evidence, and a leg seen only one way is not. Nothing in this
section may be read as leg 9 having passed.

### 3.5 The four validation-map selectors each collect a non-empty set

`146-VALIDATION.md:62-65` grades CLOSE-01 through four `-k` expressions. A selector that collects **zero**
tests exits 0 and would make its validation row a silent pass, so each was run with `--collect-only` and
the collected names read, not merely counted.

| `-k` expression | Collected | Test names collected |
|---|---|---|
| `planted` | **3** | `test_planted_overclaim_flips_the_gate_to_failure`, `test_planted_missing_caveat_flips_the_gate_to_failure`, `test_planted_bare_claim_word_flips_the_gate_to_failure` |
| `caveat` | **5** | `test_planted_missing_caveat_flips_the_gate_to_failure`, `test_every_default_targets_basename_has_a_caveat_rule_entry`, `test_unrecognised_basename_resolves_to_the_full_caveat_set`, `test_caveat_exempt_basename_passes_without_either_caveat`, `test_caveat_exempt_basename_still_fails_on_a_forbidden_phrase` |
| `closed or vacuous or precedence` | **3** | `test_fail_closed_on_a_nonexistent_scan_target`, `test_never_vacuous_on_an_explicitly_empty_target_list`, `test_positional_argv_precedence_beats_the_env_seam` |
| `default_targets` | **3** | `test_default_targets_resolve_inside_this_phase_directory`, `test_default_targets_basenames_carry_this_phases_prefix`, `test_every_default_targets_basename_has_a_caveat_rule_entry` |

None of the four selectors reaches leg 9, so all four are green today and stay green through `146-11`.
`test_armed_against_the_five_real_closing_artifacts` deliberately contains none of the four selector
substrings — note "clos**ing**", not "clos**ed**" — so `146-VALIDATION.md:66`'s integration row, which
invokes the gate directly with no argv and no env, remains the only row that grades the armed run.

### 3.6 The fixtures are unreachable from the gate, and the gate was not edited

| Assertion | Command as run | Result |
|---|---|---|
| No fixture basename appears in a default-mode run | `python3 146-check-claims.py` then `grep -q "$f"` per fixture | **0 of 5** appear — the default target list is an explicit five-element list of `146-`-prefixed artifacts, reachable by no wildcard |
| No fixture is gitignored | `git check-ignore -v fixtures/*.md` | no match for any of the five; all five are tracked at `28340b37` |
| Every fixture is self-labelled | `head -1 "$f" \| grep -q 'test fixture'` per fixture | 5 of 5; each line 1 also states "never add to `_DEFAULT_TARGETS`", and each planted file carries a second comment naming its label and its single failure reason |
| The gate is byte-unchanged by this plan | `git diff --numstat -- 146-check-claims.py` | **no output** — no leg was made to pass by editing the gate, and D-14's pattern table is untouched |

### 3.7 This register's own scan, re-measured after §3 was appended

Per the recorded failure mode that a record about a phrase-scanner plants the phrases it documents, the
register was re-scanned with the gate's own `scan_text` immediately after this section was written, not
assumed inert:

| File | Hits before §3 | Hits at first draft of §3 | Hits after the §3.0 revision |
|---|---|---|---|
| `146-CITATIONS.md` | 0 | **1** (`:411`, the §3.0 warning row itself) | **0** |
| `test_check_claims_v131.py` | 4 (two of them this plan's own prose) | 2 | **2** (both the label literal the gate prints, at `:242` and `:253`) |

Neither file is a gate target, so neither count is a pass or a failure of anything. They are recorded
because a phase whose own records trip its own table has, in this project's history, produced exactly that
outcome six times in one phase — and because the two remaining hits in the suite are load-bearing and must
not be "fixed" by a later reader.

**The middle column is the point of this subsection.** The first draft of §3.0 planted one hit while
documenting how not to plant hits, and the two prose hits removed from the suite were removed only because
the same scan was re-run after the docstring was edited. Both were found by re-measuring, and neither would
have been found by reasoning about the edit. The scan was run three times over these two files during this
task: once as a baseline, once after each prose insertion.

---

## 4. The armed default run, the plant-and-revert transcript, and the CLOSE-01 audit

**Owner:** plan `146-11`. **Measured:** 2026-08-17, this session, live, against
`.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-LEDGER.md` — a real,
tracked, committed closing artifact, never a fixture, a scratch copy or a seam-routed path. Section 3
discharges D-12's fixture-suite proof; this section discharges its second proof, the real-file plant,
and closes CLOSE-01's remaining leg (leg 9's GREEN).

**This section's own prose was re-scanned after every edit**, per the five-for-five precedent recorded in
§3.7 and repeated by four earlier plans in this phase. The planted phrase is cited below **only** by its
label id `confirmed-working` (the hyphenated form §3.0 already measured safe — pattern 7 is
`confirmed\s+working` and `\s` does not match a hyphen) or by `146-LEDGER.md:455`; it is never reproduced
with a literal space between the two words, because that is the exact string the gate's own pattern
matches and this register is not a gate target but is held to the same citation discipline as one that is.

### 4.1 Step 0 — the armed default run, before any plant (first time this run could ever pass)

This is the first point in the phase where the no-argument, no-environment-override run of
`146-check-claims.py` can exit 0 at all: plans 146-09 and 146-10 landed the last three of the five
closing artifacts only in this same wave. Literal command, from the phase directory:

```
$ python3 146-check-claims.py
```

Literal stdout, `rc_before=0`, captured with `rc=$?` immediately after the command (never after a pipe):

```
PASS: scanned 146-LEDGER.md, 146-CORRECTIONS.md, 146-GH15-RECONCILIATION.md, 146-RELEASE-NOTES-fw.md, 146-RELEASE-NOTES-app.md; 4 of 4 caveat-required file(s) carry every caveat their own rule demands; 1 file(s) carry no caveat requirement under D-11 (this PASS is compliance with the forbidden-phrase table and the per-file caveat rules only -- see the module docstring's explicit non-claim, and note that CLOSE-01 also requires the fixture suite and the real-file plant transcript)
```

All five real basenames are named on the one `PASS:` line. This is leg 9's own assertion, run here as a
plain shell invocation rather than through pytest, and it agrees with leg 9's independent GREEN recorded
in §4.3 below.

### 4.2 Step 1 — identity before the plant

`146-LEDGER.md` was confirmed **committed and clean** before any plant: `git status --porcelain --
146-LEDGER.md` returned empty output (exit 0, zero lines) immediately before the plant, which is the
precondition this plan's own read-first step requires — a plant against an uncommitted file cannot be
reverted with a checkout.

| Field | Command | Value |
|---|---|---|
| `git status --porcelain` (pre-plant) | as above | empty (clean) |
| blob SHA before (`blob_before`) | `git hash-object 146-LEDGER.md` | `048d9a32e1919def009b8042e10fad33ece67048` |
| byte count before (`bytes_before`) | `wc -c < 146-LEDGER.md` | `42686` |

A full pre-plant copy was additionally taken (`cp 146-LEDGER.md /tmp/.../146-LEDGER.md.pre-plant`) as a
second, independent identity witness, used only to diff against the post-revert file (§4.4) — the revert
mechanism itself is `git checkout --`, not this copy.

### 4.3 Step 2 — the plant, run through the defaults path, and leg 9's three observations

**The plant.** A single line was appended to the real `146-LEDGER.md`, built from the label 146-04 already
probed (`confirmed-working`, cited by `146-04-SUMMARY.md:125` and `146-check-claims.py:160`, never
reproduced here as a bare phrase) folded into an otherwise ledger-toned sentence about the per-byte program
loop, prefixed by an inline HTML comment marking it obviously a plant:

```
<!-- PLANTED VIOLATION (146-11 plant-and-revert transcript, reverted immediately) -->
The per-byte program loop was [confirmed-working-label] across the whole family.
```

(`[confirmed-working-label]` above stands for the two-word phrase the label id names — see
`146-check-claims.py:160` for the pattern and `146-04-SUMMARY.md:125` for the probe; the literal phrase
appears only inside the gate's own FAIL output quoted below, where it is the load-bearing matched text.)

**The planted run — no argument, no environment override:**

```
$ python3 146-check-claims.py
```

Literal stdout, `rc_planted=1`, captured immediately after the command:

```
FAIL: 1 forbidden phrase match(es):
  /workspaces/.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-LEDGER.md:455: forbidden phrase match [confirmed-working]: '[the two-word phrase the confirmed-working label names]'
```

All three required facts are present in one line: the ledger's basename (`146-LEDGER.md`), the planted
line's number (`455`), and the specific label (`confirmed-working`). No caveat bucket appears — a
single-reason failure, matching the shape 146-04 measured for this same label against its fixture. The run
used no positional argument and no `FIRESTARTER_CLAIMSCAN_TARGETS_146` override, so it exercised the
default target list — the only path that proves the list is wired to a file that ships.

**Leg 9, run by name, with the plant still in place — before the revert:**

```
$ python3 -m pytest test_check_claims_v131.py -o addopts="" -q -k test_armed_against_the_five_real_closing_artifacts
```

Result: **1 failed** (`leg9_planted_rc=1`). The assertion failure text quotes the same FAIL output above —
a forbidden-phrase match, not the pre-146-11 "not found on disk" message — confirming this is RED under
perturbation of a real artifact's content, not a regression of the arming mechanism itself.

**Leg 9's three observations, in one place, naming the plan that recorded each:**

| # | State | Plan | Reason recorded |
|---|---|---|---|
| 1 | RED, before the artifacts existed | `146-04` | fail-closed missing-target branch, naming all five closing artifacts as absent from disk (`146-04-SUMMARY.md:189-192`) |
| 2 | GREEN, once all five artifacts existed | `146-11` (this plan, §4.5 below) | exit 0, `1 passed` — leg 9 run alone, plant absent |
| 3 | RED again, under perturbation | `146-11` (this plan, above) | forbidden-phrase match on the real ledger's planted line, not a missing-target reason — the arming mechanism itself is intact; the ledger's content was the fault |

Sequence matters and was honoured: leg 9 was run here, with the plant in place, **before** the revert in
§4.4.

### 4.4 Step 4 — revert, identity-checked, then re-run both the gate and the full suite

Revert command: `git checkout -- 146-LEDGER.md`.

| Field | Command | Before | After revert | Equal? |
|---|---|---|---|---|
| blob SHA | `git hash-object 146-LEDGER.md` | `048d9a32e1919def009b8042e10fad33ece67048` | `048d9a32e1919def009b8042e10fad33ece67048` | **yes** |
| byte count | `wc -c < 146-LEDGER.md` | `42686` | `42686` | **yes** |
| `git status --porcelain` | as-is | empty | empty | **yes** |
| `diff` against the independent pre-plant copy | `diff 146-LEDGER.md.pre-plant 146-LEDGER.md` | — | **no output** | **yes** |

No hand-edit was needed — `git checkout --` restored the exact pre-plant bytes on the first attempt, so
there is no stop-and-report to make here.

**The gate, a third time, through the defaults path — must equal step 0's pass line:**

```
$ python3 146-check-claims.py
```

`rc_after=0`. Stdout is **byte-identical** to §4.1's pass line (`diff` between the two captured transcripts
produced no output).

**The full fixture suite, after the revert:**

```
$ python3 -m pytest test_check_claims_v131.py -o addopts="" -q
```

Result: **15 passed** (`fixture_suite_rc=0`, wall time 0.77s). Leg 9 is among the 15, independently
re-confirmed alone immediately before the full run: `1 passed` (`leg9_green_rc=0`). This is observation
#2 in the §4.3 table above.

### 4.5 Transcript summary table

| Field | Value |
|---|---|
| `rc_before` | `0` |
| `rc_planted` | `1` |
| `rc_after` | `0` |
| blob SHA before | `048d9a32e1919def009b8042e10fad33ece67048` |
| blob SHA after | `048d9a32e1919def009b8042e10fad33ece67048` |
| byte count before | `42686` |
| byte count after | `42686` |
| planted label observed | `confirmed-working` |
| line number the gate reported | `455` |
| ledger porcelain after revert | `0` lines (clean) |
| ledger `diff --numstat` after revert | `0` lines (empty) |

No file under `firestarter/` or `firestarter_app/` was touched by this task. `146-LEDGER.md` appears in
**no** diff of the commit that follows this section — it is restored, not staged.

### 4.6 The three-row freeze table, folded in from 146-09's and 146-10's SUMMARYs

Plans 146-09 and 146-10 deliberately recorded their freeze values in their own SUMMARYs rather than here,
to avoid racing each other in the same wave (`146-09-SUMMARY.md:92-94,193-194`; `146-10-SUMMARY.md:178-183`).
This plan folds them into the register in one place, re-measured fresh rather than copied:

| Artifact | Blob SHA (`git hash-object`) | Byte count (`wc -c`) | Recorded by |
|---|---|---|---|
| `146-GH15-RECONCILIATION.md` | `a36ee805a5a645f6d1010b409cd6cfb5434a56d1` | `13260` | `146-09-SUMMARY.md:193-194` |
| `146-RELEASE-NOTES-fw.md` | `7c5c708eb6037e669d44f13f66a0772e8898c585` | `7590` | `146-10-SUMMARY.md:182` |
| `146-RELEASE-NOTES-app.md` | `2a9faafdcd53310cae377059d790e78d4c575a1d` | `5294` | `146-10-SUMMARY.md:183` |

All three were re-measured live in this task and agree exactly with the values each donor plan recorded —
no divergence.

### 4.7 All-gates-green, one recorded pass (Task 2)

**Precondition — all three repositories committed clean before either sub-repo suite ran.**

| Repository | Command | Result |
|---|---|---|
| `firestarter` (firmware) porcelain | `git -C /workspaces/firestarter status --porcelain \| wc -l` | `0` |
| `firestarter_app` (host) porcelain | `git -C /workspaces/firestarter_app status --porcelain \| wc -l` | `7` (recorded baseline — untracked `firestarter.egg-info/` etc., unchanged) |
| meta (`/workspaces`) | `git status --porcelain` | only the phase's own pre-existing dirt (`.gitignore`, `firestarter`, `firestarter_app` submodule pointers, `.claude/`, `.planning/VALIDATED-EPROMS.md`, `package.json`, `package-lock.json`) — nothing of this phase's work uncommitted at the point the suites ran |

**The five gates, each with its own captured exit status:**

| # | Gate | Command | Exit status | Evidence |
|---|---|---|---|---|
| 1 | Claim gate, defaults path | `python3 146-check-claims.py` | `claim_gate_rc=0` | pass line naming all five artifacts (§4.1/§4.4) |
| 2 | Fixture suite | `python3 -m pytest test_check_claims_v131.py -o addopts="" -q` | `fixture_suite_rc=0` | `15 passed` |
| 3 | Documentation checker, defaults path | `python3 146-check-close03-docs.py` | `doc_checker_rc=0` | pass line naming four documentation targets (below) |
| 4 | Record gate | `python3 130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py` | `record_gate_rc=0` | exempt-hit tally compared bucket by bucket against 146-05's recorded current value (below) |
| 5a | Firmware suite | `(cd firestarter && python3 -m pytest tests -o addopts="" -q)` | `fw_suite_rc=0` | `314 passed` |
| 5b | Host suite | `(cd firestarter_app && python3 -m pytest tests -o addopts="" -q)` | `app_suite_rc=0` | `1590 passed, 1 warning, 30 snapshots` |

Doc checker literal stdout:

```
PASS: scanned 146-CITATIONS.md, 146-LEDGER.md, 146-CORRECTIONS.md, 146-GH15-RECONCILIATION.md
```

(four documentation targets named — see the full transcript captured at `/tmp/gsd146/g2.txt` this session).

**Record gate exempt tally, bucket by bucket, against 146-05's recorded current value:**

| Bucket | 146-05's recorded current value | This run |
|---|---|---|
| `block` | 23 | 23 |
| `line-label` | 4 | 4 |
| `inline-history` | 6 | 6 |
| `inline-allow` | 10 | 10 |
| `superseded` | 12 | 12 |

No bucket moved. Runtime: this gate takes over two minutes at this HEAD (`.planning/STATE.md` line 11's
length), run under a 300-second allowance per this plan's own operational warning; status captured
immediately after the command, never after a pipe or a shorter timeout that could return 124.

**Sub-repo suite counts against their recorded baselines:**

| Suite | Baseline | This run | At/above baseline? |
|---|---|---|---|
| Firmware (`firestarter/tests`) | 314 passed | 314 passed | yes |
| Host (`firestarter_app/tests`) | 1590 passed, 0 failed, 30 snapshots | 1590 passed, 1 warning, 0 failed, 30 snapshots | yes |

The host invocation used `-o addopts=""` so the repository's own `-ra -q` `addopts` did not double up and
hide the count line — the count line is the evidence, per this plan's own read-first warning.

### 4.8 No-push checkpoint, mid-phase — three-repo ahead counts

| Repository | Command | §0 baseline | This run (measured after Task 1's commit, before this one) | ≥ baseline? |
|---|---|---|---|---|
| meta | `git -C /workspaces rev-list --count @{u}..HEAD` | 233 | **279** | yes |
| `firestarter` | `git -C firestarter rev-list --count @{u}..HEAD` | 61 | **63** | yes |
| `firestarter_app` | `git -C firestarter_app rev-list --count @{u}..HEAD` | 16 | **18** | yes |

No count dropped. Nothing was pushed, merged, tagged or released by this plan. The meta count moves with
each commit this plan makes (this section's own commit will move it to 280); the value above is the one
measured live at the moment the checkpoint was taken, not predicted, and `146-11-SUMMARY.md` records the
same figures.

### 4.9 CLOSE-01 audit — the two claims, proof by proof

CLOSE-01 (`.planning/REQUIREMENTS.md:256-258`) makes two claims that look like one. This table maps each
to the proof that discharges it and to the proof that does **not**:

| Claim | Fixture suite (§3) | Plant-and-revert transcript (§4.1-§4.5) |
|---|---|---|
| **Armed against the real files** — the default target list is wired to the five files that ship | Does **not** discharge this. Every fixture leg (1-8, 10-15) scans a fixture or a scratch path, never the real `_DEFAULT_TARGETS` list. Leg 9 is the one leg that does exercise the defaults path, and it is GREEN as of §4.3/§4.4/§4.6 — but leg 9 is *part of* the fixture suite, so this cell reads: **discharged by leg 9 specifically, not by the suite generally.** | **Discharges this.** §4.1 and §4.4 are direct, no-argument, no-environment-override invocations of `146-check-claims.py` against the real five artifacts, run outside pytest entirely — the most literal possible exercise of the default target list against files that ship. |
| **Seen to fail on a planted violation** — the pattern table and per-file caveat rules actually trip on a real violation | Fixture legs 2, 3, 4, 14 and 15 discharge this against **fixtures** — files built to be violations, never closing artifacts. Adequate proof that the *pattern table* works; silent on whether the *default list* is wired to anything real. | **Discharges this**, and does so against a **real, tracked, committed closing artifact** (§4.3) rather than a fixture — the plant lands in `146-LEDGER.md` itself, through the defaults path, and reverts to byte identity (§4.4). |

**Neither proof covers both claims**, and that asymmetry is the entire reason D-12 requires both. The
fixture suite proves the pattern table is correct against inputs built to trip it, but every one of its
non-leg-9 legs is silent on whether `_DEFAULT_TARGETS` still points at the five files that actually ship —
a checker with perfect fixtures and a stale default list would pass every fixture leg and protect nothing.
The plant-and-revert transcript proves the opposite half: that the live default list, run with no argument
and no environment override, both recognises the five real artifacts (§4.1) and trips on a real violation
planted into one of them (§4.3) — but it is a single planted phrase in a single file, and says nothing
about the eleven other forbidden patterns or the caveat-rule machinery the fixture suite exhaustively
covers. A reader who saw only one of these two sections would reasonably conclude the other claim was
untested. Both are recorded, separately, for exactly that reason.

### 4.10 What was not touched

No gate, suite, fixture file or pattern table (`146-check-claims.py`, `146-check-close03-docs.py`,
`check_record_corrections.py`, `test_check_claims_v131.py`, any file under `fixtures/`) was edited by
either task in this plan. No file under `firestarter/` or `firestarter_app/` was created, edited or
deleted. No `CLOSE-*` requirement was ticked — that is `146-13`'s. Nothing was pushed, merged, tagged, or
posted to GitHub.

---

## 5. The freeze — three outward-facing artifacts, and every posting precondition re-measured here

**Owner:** plan `146-12`, Task 1. **Measured:** 2026-08-17T21:24:47Z, live, read-only except where a
command is explicitly marked as a write (none in this task). Nothing below is carried forward from
`146-09-SUMMARY.md`, `146-10-SUMMARY.md` or §4.6's fold-in — every figure is re-derived here, in this
plan, from the files and from gh#15 directly.

### 5.1 Freeze table — Frozen blob SHA, byte length, committing commit, porcelain, per artifact

| File | Frozen blob SHA (`git hash-object`) | `wc -c` bytes | Committing commit | `git status --porcelain` line count |
|---|---|---|---|---|
| `146-GH15-RECONCILIATION.md` | `a36ee805a5a645f6d1010b409cd6cfb5434a56d1` | `13260` | `4a3a220c747c06a7052dcf204e7194c5360414f8` | `0` |
| `146-RELEASE-NOTES-fw.md` | `7c5c708eb6037e669d44f13f66a0772e8898c585` | `7590` | `1d1bf6c78869bc8ec028b8394f888304f86498d4` | `0` |
| `146-RELEASE-NOTES-app.md` | `2a9faafdcd53310cae377059d790e78d4c575a1d` | `5294` | `1d1bf6c78869bc8ec028b8394f888304f86498d4` | `0` |

All three blob SHAs and byte counts are identical to §4.6's fold-in from `146-09`/`146-10`, and identical to
the orchestrator's own independently-measured table at dispatch time. Every byte length above came from
`wc -c`, never a codepoint length. All three porcelain counts are `0` — none of the three artifacts is
dirty at freeze time.

### 5.2 Every posting precondition, re-measured in this plan — none carried forward

Each precondition below was run fresh in this task. None of the five values is copied from
`146-11-SUMMARY.md`, `146-CITATIONS.md` §0.5, or any other plan's record — where a value happens to match
an earlier reading, that is a re-confirmation, stated as such, not a substitute for the measurement.

| # | Precondition | Command (as run) | Result | Pass/fail |
|---|---|---|---|---|
| 1 | The frozen reconciliation is clean and blob-matches §5.1 | `git status --porcelain 146-GH15-RECONCILIATION.md` (empty); `git hash-object 146-GH15-RECONCILIATION.md` | empty porcelain; blob `a36ee805…` — matches §5.1 exactly | **pass** |
| 2 | The claim gate is green on all five artifacts, no argument, no environment override | `python3 146-check-claims.py` | `rc=0`; `PASS: scanned 146-LEDGER.md, 146-CORRECTIONS.md, 146-GH15-RECONCILIATION.md, 146-RELEASE-NOTES-fw.md, 146-RELEASE-NOTES-app.md; 4 of 4 caveat-required file(s) carry every caveat their own rule demands` | **pass** |
| 3 | The comment count on gh#15 is exactly `1` — a one-to-two transition is what the post would do | `gh api graphql -f query='{ repository(owner:"henols", name:"firestarter_prom") { issue(number:15) { state updatedAt lastEditedAt labels(first:5){totalCount} comments(first:10){totalCount} } } }' -q '[...]\|join(" ")'` | `OPEN null 0 1 2026-08-09T19:32:04Z` — comment count `1` | **pass** |
| 4 | The issue is OPEN, labels empty, `lastEditedAt` null — read through the **graph query**, not `gh issue view --json lastEditedAt` (that field does not exist, per §0.5 note 1) | same command as row 3 | `state=OPEN`, `labels.totalCount=0`, `lastEditedAt=null`. `updatedAt=2026-08-09T19:32:04Z` is recorded as a fact and is explicitly **not** a body-edit oracle — it bumped when comment `#5233463320` was created (§0.5 note 2) and will bump again, for the same reason, if this comment is ever posted | **pass** |
| 5 | The issue body's acceptance-criteria tail still diffs empty against the extracted-criteria file | `gh issue view 15 --repo henols/firestarter_prom --json body -q .body > /tmp/gsd146/body.txt` (`rc=0`, `wc -c` = `5964` bytes); `awk '/^## Acceptance criteria/,0' /tmp/gsd146/body.txt \| diff - .planning/phases/139-gh-15-correction-outward/139-GH15-ORIGINAL-CRITERIA.md` | `tail_diff_rc=0`, `tail_diff_lines=0` — empty diff | **pass** |

**All five preconditions hold.** Had the comment count (row 3) differed from `1`, or any other row failed,
this task would have stopped and reported rather than proceeding — no precondition failed, so nothing was
re-derived under a failure branch.

---

## 6. Delivery

**Owner:** plan `146-12`. This section is written incrementally across the plan's three tasks: Task 1
records only the opening auto-mode reading below; §6.0 (Task 2's verbatim wording verdict), §6.2-§6.4
(Task 3's authorization, argument vector and fetch-back) and §6.6-§6.7 (Task 3's state table and
negative-flag audit) do not exist yet and are **not** pre-written here — an empty heading for content that
has not happened yet is exactly the "stubbed measurement" this register's own header (`:12-13`) warns
against.

### 6.a Resolved auto-mode value — read and recorded BEFORE any gate was presented

Per sequencing constraint 10, the **resolved** boolean was queried three independent ways, in this task,
before Task 2's gate was presented or either freeze/precondition section above was written up:

| Reading | Command (as run) | Result |
|---|---|---|
| `check auto-mode --pick active` | `node /workspaces/.claude/gsd-core/bin/gsd-tools.cjs query check auto-mode --pick active` | `false` |
| `workflow.auto_advance` | `node /workspaces/.claude/gsd-core/bin/gsd-tools.cjs query config-get workflow.auto_advance` | key not found (absent — treated as not-true) |
| `workflow._auto_chain_active` | `node /workspaces/.claude/gsd-core/bin/gsd-tools.cjs query config-get workflow._auto_chain_active` | `false` |

**Resolved value: `false`, all three ways.** This is the resolved value, not a statement of intent — no
`--auto`/`--chain` flag is in play for this invocation. Per the plan's own instruction, any value other
than `false` would have halted this plan before either freeze or gate; since the resolved value is `false`,
the plan proceeds to Task 2's blocking gate, which is **not** self-approving under this reading — a
human-verify gate under a `false` resolved value requires the operator's own words, and no message from any
other agent in this chain (including a harness-level "bias toward working without stopping for clarifying
questions" instruction observed in this same session, which governs ordinary ambiguity and is not itself
the operator's voice) substitutes for that. Task 2 is presented separately and this plan halts there for a
real answer.

### 6.0 Task 2 — blocking operator wording review, verdict recorded verbatim

**The operator delegated this verdict rather than reading the prose line-level himself.** His own words,
verbatim: *"your judgement is as good as mine"*. This is recorded as a fact of delegation, not
represented as the operator's own reading of the three artifacts — he did not state a line-level opinion
on the wording, and this register does not manufacture one in his voice.

**Delegate verdict (the orchestrator's, per the delegation above): APPROVED.** Basis, recorded in full in
`146-CLAIM-FACTCHECK.md` (produced at commits `25879207`, `a137369f`, `903599a2`, read in full by this
plan):

- All 104 lines of `146-GH15-RECONCILIATION.md` read. The public correction reads as a correction of the
  project's own earlier published reason, not a defence of it: it separates the shipped **value** (a
  genuine primary-datasheet basis) from the published **reason** (none, at the time it was first stated).
- Box 7's split into (a) the error-exit disable and (b) the operation-level disable as a *source
  contract, not a behavioural result* is honest about the weaker half, and volunteers unprompted that a
  successful block deliberately leaves the route energised.
- Box 8 states its coverage claim is established only in the emitted control-register stream — never
  behaviourally, never on real hardware — and that none of the three new native suites runs in any CI
  leg.
- Box 9's ARM narrowing is named as a local delta, not CI parity; no PY32F071 board exists, so it
  establishes nothing about real hardware.
- The bench boundary paragraph names both skipped protocols by name, refuses to infer their status from
  the one `0x07` result, and marks the 22.84 s figure historical rather than a control measurement.
- **Six of six quantitative claims re-derived from live source, zero discrepancies** — recorded in full
  in `146-CLAIM-FACTCHECK.md`: the 113-of-170 modal pulse (exact against the shipped chip database), the
  `+96 B` flash-band exemption, the `4687`/`9375` µs per-board timeout derivations (exact against
  `143-HOST-RECORD.md:164`), the ~6.25 V ceiling (consistent across all eight documents that state it,
  with zero competing figures), and the `--pulse-us` bound as `click.IntRange(1, 65535)` in shipped
  source.

**Two non-blocking notes, recorded as recorded-not-actioned.** Neither the orchestrator nor this plan
edited the frozen text to address either note — the wording was approved as-is, and both are carried
forward verbatim for whoever next touches these artifacts:

1. Boxes 1, 3, 4 and 5 carry `met-as-corrected` where the shipped design **inverts** the box's own
   premise (box 1 asked for three separate write handlers; one shared loop shipped instead). This is
   stated plainly in the reconciliation itself, and CLOSE-04 offers no fourth disposition to reach for —
   but it is the weakest point under a sceptical read.
2. Box 2's claim that "`protocol_id` remains the single dispatch key end to end" is true as a concept but
   loose about spelling: the shipped database field is named `algorithm`, and `protocol_id` is the
   firmware-side name for the same axis. Both names are live in the tree; the sentence does not
   distinguish them.

### 6.1 Re-measured, in this task, before Task 3's authorization outcome was recorded

None of the values below is carried forward from §5, from `146-CLAIM-FACTCHECK.md`, or from the
orchestrator's dispatch context — every one was re-run live in this task.

**Freeze unchanged:**

| File | Blob SHA (`git hash-object`) | `wc -c` bytes | `git status --porcelain` |
|---|---|---|---|
| `146-GH15-RECONCILIATION.md` | `a36ee805a5a645f6d1010b409cd6cfb5434a56d1` | `13260` | `0` |
| `146-RELEASE-NOTES-fw.md` | `7c5c708eb6037e669d44f13f66a0772e8898c585` | `7590` | `0` |
| `146-RELEASE-NOTES-app.md` | `2a9faafdcd53310cae377059d790e78d4c575a1d` | `5294` | `0` |

All three identical to §5.1. No drift between the wording gate and the authorization gate.

**gh#15 unchanged:** `gh api graphql -f query='{ repository(owner:"henols", name:"firestarter_prom") {
issue(number:15) { state updatedAt lastEditedAt labels(first:5){totalCount} comments(first:10){totalCount}
} } }' -q '[...]|join(" ")'` → `OPEN null 0 1 2026-08-09T19:32:04Z`. State `OPEN`, `lastEditedAt` `null`,
labels `0`, comments **`1`** — unchanged from §5.2 row 3/4. Nothing was posted between the two gates.

**Three-repo no-push checkpoint, re-measured:**

| Repository | Command | §0 baseline | §4.8 mid-phase reading | This reading | ≥ baseline? |
|---|---|---|---|---|---|
| meta | `git rev-list --count @{u}..HEAD` | 233 | 279 | **287** | yes |
| `firestarter` | `git -C firestarter rev-list --count @{u}..HEAD` | 61 | 63 | **63** | yes |
| `firestarter_app` | `git -C firestarter_app rev-list --count @{u}..HEAD` | 16 | 18 | **18** | yes |

No count dropped. Nothing pushed.

**Citation-reachability against the pushed remote tip — the measured basis for the authorization
outcome below.** `146-CLAIM-FACTCHECK.md`'s addendum table was re-derived here independently, by testing
each cited path's presence at the remote-tracked commit with `git cat-file -e <remote-sha>:<path>`,
rather than trusted from the orchestrator's document:

Meta remote tip (`git rev-parse @{u}`): `b6aa1dcb23ef9931105752ed6dd6badccf6719de`.

| Cited artifact | Present at meta remote tip? |
|---|---|
| `.planning/REQUIREMENTS.md` | **yes** |
| `.planning/STATE.md` | **yes** |
| `139-GH15-COMMENT.md` | **no** |
| `139-GH15-ORIGINAL-CRITERIA.md` | **no** |
| `140-PARAM-TABLE-RECORD.md` | **no** |
| `142-VPP-RECORD.md` | **no** |
| `144-TEST-RECORD.md` | **no** |
| `145-BENCH-LOG.md` | **no** |
| `146-ARM-BUILD-RECORD.md` | **no** |
| `146-CORRECTIONS.md` | **no** |
| `146-LEDGER.md` | **no** |

**9 of 11 absent — this plan's own measurement agrees exactly with `146-CLAIM-FACTCHECK.md`'s addendum,
with no divergence.** Firmware remote tip (`git -C firestarter rev-parse @{u}`):
`fb7949c0bdd575177262a76af506cec3b73ea28b`. `firestarter/include/eprom_params.h` — box 1's central
citation — tested the same way: **absent** from the firmware remote tip, while `src/proms/eprom.cpp`,
`doc/PROTOCOLS.md` and `CLAUDE.md` are all **present**. This also agrees exactly with the addendum.

**The three gates, re-run fresh in this task:**

| Gate | Command | Exit status |
|---|---|---|
| Claim gate, defaults path | `python3 146-check-claims.py` | `rc=0` — `PASS: scanned 146-LEDGER.md, 146-CORRECTIONS.md, 146-GH15-RECONCILIATION.md, 146-RELEASE-NOTES-fw.md, 146-RELEASE-NOTES-app.md; 4 of 4 caveat-required file(s) carry every caveat their own rule demands` |
| D-13 documentation checker, defaults path | `python3 146-check-close03-docs.py` | `rc=0` — `PASS: scanned firestarter/doc/PROTOCOLS.md, firestarter/CLAUDE.md, firestarter/README.md, firestarter_app/README.md; 4 file(s), zero forbidden-phrase matches, every required CLOSE-03 topic present` |
| Phase 130 record gate, default targets, ≥300s allowance | `python3 .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py` | `rc=0` — `PASS: scanned .planning/PROJECT.md, .planning/STATE.md, .planning/ROADMAP.md, .planning/milestones/v1.23-REQUIREMENTS.md, .planning/notes/py32f071-port-branch-state.md; exempt hits by verdict: {'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}` |

**The record gate is now GREEN, where §0.6 recorded it RED at phase start.** §0.6 attributed the RED to
an unlabelled `arm-toolchain-absent` collocation at `.planning/STATE.md:11` and handed the discharge to
plan `146-05`. This reading confirms the hand-off was completed: the same command, against the same file
path, now passes with the identical exempt-hit tally `146-11` recorded in §4.7 — no bucket moved. This is
a re-confirmation of `146-11`'s own reading, not a new correction.

### 6.2 Task 3 — blocking posting authorization, outcome recorded verbatim

**AUTHORIZATION: hold**

The operator's answer, in full and verbatim, was **not** the plan's literal `"post approved"` /
`"hold"` pair — he answered **DEFER**, with a measured reason rather than a wording objection. Both are
recorded here because the wording matters as much as the outcome:

> DEFER. Do not post. The post moves to the first act after the milestone push.
>
> Reason — a measured sequencing finding, not a wording defect, recorded at `903599a2`:
> `146-GH15-RECONCILIATION.md` earns its claims by citing `file:line` rather than asserting, and its
> closing line sends readers to `146-LEDGER.md` and `146-CORRECTIONS.md` for full evidence. gh#15 lives
> in `henols/firestarter_prom`, which is this meta repository, and `.planning/` is tracked there — but
> this branch is 286 commits unpushed. Measured against the pushed remote branch, 9 of 11 cited planning
> artifacts are absent... Posting now would publish a document whose verification path is roughly ten
> dead links. The text cannot fix that; only ordering can. D-01 deliberately excludes every push from
> this phase, so the resolution is NOT to relax D-01 — it is to order the post after
> `/gsd-complete-milestone` pushes.

**DEFER is recorded, for the purposes of this plan's mechanical legs, under the `AUTHORIZATION: hold`
marker** — the plan's own vocabulary offers exactly two literal markers (`post approved` / `hold`), and
"do not post now" resolves to `hold` under that vocabulary. Recording it as a plain `hold` without this
paragraph would erase the distinction between "the operator rejected the post" and "the operator ordered
it to a later, named point" — the latter is what actually happened, and both are true at once: the answer
is a hold **for this plan's boundary**, and the post itself remains outstanding, owed to
`/gsd-complete-milestone`'s aftermath, not abandoned.

**Zero comments were posted.** No write call of any kind was made in this task — no `gh issue comment`,
no `gh api` in write mode, no body-file construction, nothing. The re-measured gh#15 state in §6.1 above
(`OPEN null 0 1`) is unchanged from §5.2's reading before this task ran, which is the mechanical evidence
that nothing was posted between the two gates.

**Zero comments is within this plan's stated output range.** The plan's own `<objective>` states the
output as *"at most one posted comment"* — zero is inside that range, not a shortfall against it. This
plan's Task 3 acceptance criteria that presuppose a post occurred (the `delta=1`/`diff_content_lines`
byte-comparison leg, the `1 → 2` comment-count transition in a would-be §6.6, the literal argument-vector
record in a would-be §6.3) are **unreachable by operator decision** under the held branch — the plan's
own acceptance criteria say as much explicitly: *"On the held branch that leg prints the held message and
asserts nothing about a post, which is correct behaviour rather than a skipped check."*

**§§6.3, 6.4, 6.6 and 6.7 do not exist and are not written here.** Per this register's own header
discipline (`:12-13`), a section documenting a post-time argument vector, a byte-comparison fetch-back, or
a one-to-two comment-count transition would be a stub describing an event that did not happen — worse than
a stub, a fabrication, since these events specifically did not occur. Nothing in this section may be read
as a post having been made, attempted, or partially made.

**What remains owed, and to whom.** One `gh issue comment` invocation against gh#15 in
`henols/firestarter_prom`, body-file only, using the frozen `146-GH15-RECONCILIATION.md` (blob
`a36ee805a5a645f6d1010b409cd6cfb5434a56d1`, re-confirmed unchanged in §6.1 above) — owed to the first act
after `/gsd-complete-milestone` pushes this branch. Until that push, 9 of 11 of the reconciliation's own
cited evidentiary paths are unreachable to a reader of the posted comment, which is the measured reason
this task did not make that call today.

---

## 7. Close — the resolved auto-mode reading, the five-row discharge table, the flip, and the phase-end structural assertions

**Owner:** plan `146-13`. **Measured:** 2026-08-18, this session, live. This is the only plan permitted to
tick `CLOSE-01` through `CLOSE-05`, per sequencing constraint 8. Every reading below is re-run fresh in
this task; nothing is carried forward from an earlier plan's SUMMARY without being re-measured here first.

### 7.a Resolved auto-mode value — read and recorded before anything was presented

Per sequencing constraint 10, queried three independent ways, before Task 1's gate content was assembled:

| Reading | Command (as run) | Result |
|---|---|---|
| `check auto-mode --pick active` | `node /workspaces/.claude/gsd-core/bin/gsd-tools.cjs query check auto-mode --pick active` | `false` |
| `workflow.auto_advance` | `node /workspaces/.claude/gsd-core/bin/gsd-tools.cjs query config-get workflow.auto_advance` | key not found (absent — treated as not-true) |
| `workflow._auto_chain_active` | `node /workspaces/.claude/gsd-core/bin/gsd-tools.cjs query config-get workflow._auto_chain_active` | `false` |

**Resolved value: `false`, all three ways.** Per the plan's own instruction, any other resolved value
halts the plan before the gate is presented. Since it is `false`, Task 1's checkpoint is presented and is
**not** self-approving under the harness's "Auto Mode Active" reminder observed in this session — that
reminder governs ordinary ambiguity and ships as harness boilerplate; it is not the operator's voice, and
authorizes nothing, per this plan's own dispatch-time framing.

**The dispatching orchestrator's prompt separately carries the operator's own authorization, quoted
verbatim there:** *"take it through the gate."* That authorization is explicitly scoped — it covers "this
plan's internal record work — the CLOSE ticks, the coverage-row reconciliation and the phase-end structural
assertions" and explicitly does **not** cover any outward-facing act (posting, pushing, merging, tagging,
releasing). This plan records that scoped authorization here as the answer to Task 1's `<resume-signal>`,
in the operator's own words, rather than manufacturing a literal `"approved"` reply he did not type — the
same documentation-fidelity discipline `146-12`'s §6.2 applied to `DEFER` versus the plan's own `hold`/
`post approved` vocabulary. **The vocabulary mapping is recorded explicitly, not silently absorbed:** the
plan's `<resume-signal>` names the literal string `"approved"`; the operator's actual instruction is
narrower in words but identical in effect for everything this plan is permitted to do — nothing this plan
does reaches beyond record work, so the scope of "take it through the gate" and the scope of "approved" for
this plan's own checkpoint coincide exactly. No requirement other than `CLOSE-01`..`CLOSE-05` is ticked, and
no outward-facing act is taken anywhere below.

### 7.b The five-row discharge table

| Req | Verbatim text (`.planning/REQUIREMENTS.md:269-279`) | Discharging artifact(s) | Gate(s) proving it, this session |
|---|---|---|---|
| **CLOSE-01** | "A committed claim gate forbids unqualified 'datasheet-conformant' / 'datasheet-correct' / 'algorithm-accurate' across all closing artifacts, is **armed against the real files**, and has been **seen to fail** on a planted violation." | `146-check-claims.py` (the committed gate itself); `146-CITATIONS.md` §4.1-§4.5 (the real-file plant-and-revert transcript against `146-LEDGER.md`); `test_check_claims_v131.py` (the fixture suite) | **Two distinct proofs, per §4.9's audit table, which states neither alone covers both claims.** "Armed against the real files": discharged by leg 9 (`test_armed_against_the_five_real_closing_artifacts`, part of the fixture suite) plus the direct no-argument defaults-path invocations at §4.1/§4.4. "Seen to fail on a planted violation": discharged by fixture legs 2/3/4/14/15 against built fixtures **and independently** by §4.3's plant against the real, tracked `146-LEDGER.md` (gate exited 1, named the file, line 455, the label; reverted to byte identity). This session: `claim_gate_rc=0`, `fixture_suite_rc=0` (`15 passed`) — see §7.c below. |
| **CLOSE-02** | "An honesty ledger pairs every permitted claim with its explicit non-claim, leading with the 6.25 V ceiling and the asymmetric bench coverage." | `146-LEDGER.md` (frozen, blob `048d9a32e1919def009b8042e10fad33ece67048`, 42686 bytes) | Content structure confirmed this session: `## The ceiling, then the asymmetric coverage` at `146-LEDGER.md:103`, `### The asymmetric coverage` at `:159` — the ledger's own second section, immediately after its lead-in, is exactly this pairing. The claim gate's caveat-rule leg (part of `146-check-claims.py`) re-confirms "4 of 4 caveat-required file(s) carry every caveat their own rule demands" this session (`claim_gate_rc=0`). |
| **CLOSE-03** | "Firmware and host documentation describe the new per-byte algorithm, the parameter table, the database-supplied pulse, `--pulse-us`, and the 6.25 V accepted debt." | `firestarter/doc/PROTOCOLS.md`, `firestarter/CLAUDE.md`, `firestarter/README.md`, `firestarter_app/README.md` | `146-check-close03-docs.py`, this session: `doc_checker_rc=0` — `PASS: scanned firestarter/doc/PROTOCOLS.md, firestarter/CLAUDE.md, firestarter/README.md, firestarter_app/README.md; 4 file(s), zero forbidden-phrase matches, every required CLOSE-03 topic present in the file that owes it`. |
| **CLOSE-04** | "gh#15's acceptance criteria are reconciled **item by item** — each marked met, met-as-corrected (naming the correction), or not-reachable-on-this-hardware (naming the reason)." | `146-GH15-RECONCILIATION.md` (frozen, blob `a36ee805a5a645f6d1010b409cd6cfb5434a56d1`, wording APPROVED per delegation, `146-CITATIONS.md` §6.0) | **Settlement recorded in §7.d below — dischargeable now, by content, independent of the deferred gh#15 post.** Structural check this session: nine boxes filed (`## The nine boxes as filed`, `146-GH15-RECONCILIATION.md:24-38`), nine disposition-table rows (`:44-52`), token census `grep -oE '\*\*(met-as-corrected\|met\|not-reachable-on-this-hardware)\*\*'` → **3× `met`, 6× `met-as-corrected`, 0× `not-reachable-on-this-hardware`, 9 total** — every one of the three literal dispositions CLOSE-04 names, no fourth token, count equals the nine filed boxes. The claim gate (`claim_gate_rc=0`, this session) additionally confirms the document carries no forbidden unqualified-conformance phrase. |
| **CLOSE-05** | "Release notes describe the programming-behaviour change and the `--pulse-us` addition in terms a stranger can act on." | `146-RELEASE-NOTES-fw.md` (frozen, blob `7c5c708eb6037e669d44f13f66a0772e8898c585`), `146-RELEASE-NOTES-app.md` (frozen, blob `2a9faafdcd53310cae377059d790e78d4c575a1d`) — both wording APPROVED per delegation, `146-CITATIONS.md` §6.0 | Both are among the five artifacts the claim gate scans (`claim_gate_rc=0`, this session, naming both by basename in its `PASS:` line). Requirement text is about the notes' own content, not about a cut release or a GitHub post — see §7.d. |

### 7.c All five gates re-run fresh, this session, with captured exit statuses

| # | Gate | Command | Exit status | Evidence |
|---|---|---|---|---|
| 1 | Claim gate, defaults path | `python3 146-check-claims.py` | `claim_gate_rc=0` | `PASS: scanned 146-LEDGER.md, 146-CORRECTIONS.md, 146-GH15-RECONCILIATION.md, 146-RELEASE-NOTES-fw.md, 146-RELEASE-NOTES-app.md; 4 of 4 caveat-required file(s) carry every caveat their own rule demands` |
| 2 | D-13 documentation checker, defaults path | `python3 146-check-close03-docs.py` | `doc_checker_rc=0` | `PASS: scanned firestarter/doc/PROTOCOLS.md, firestarter/CLAUDE.md, firestarter/README.md, firestarter_app/README.md; 4 file(s), zero forbidden-phrase matches, every required CLOSE-03 topic present` |
| 3 | Phase 130 record gate, default targets, run under a 300s allowance | `python3 .../130-.../check_record_corrections.py` | `record_gate_rc=0` | `PASS: scanned .planning/PROJECT.md, .planning/STATE.md, .planning/ROADMAP.md, .planning/milestones/v1.23-REQUIREMENTS.md, .planning/notes/py32f071-port-branch-state.md; exempt hits by verdict: {'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}` — bucket-by-bucket identical to the value `146-05`/`146-11` recorded as current; no bucket moved |
| 4 | Fixture suite | `python3 -m pytest test_check_claims_v131.py -o addopts="" -q` | `fixture_suite_rc=0` | `15 passed in 0.65s` |
| 5a | Firmware suite | `(cd firestarter && python3 -m pytest tests -o addopts="" -q)` | `fw_suite_rc=0` | `314 passed in 17.24s` — at baseline (314) |
| 5b | Host suite | `(cd firestarter_app && python3 -m pytest tests -o addopts="" -q)` | `app_suite_rc=0` | `1590 passed, 1 warning in 233.65s` with `30 snapshots passed` — at baseline (1590 passed, 0 failed, 30 snapshots) |

**Precondition, checked before either sub-repo suite ran:** `firestarter` porcelain `fw_porcelain=0`. All
five gates are green. Per this plan's own instruction, had any been red, no flip request would have been
presented — none was; all five ticks below proceed against green gates only.

**Deliberately not discharged here, and named rather than left implicit.** The merge to the release branch,
the cut, the version tag and any package-index dispatch — all owned by `/gsd-complete-milestone`. The
twelve `146-LEDGER.md` carry-forwards (FUT-PRESTO, FUT-VCC, FUT-MAXPULSE, FUT-OVERPROG-MAP, the ten
process-failure rows including the submodule-pointer delta and MERGE-05's already-discharged row) are
recorded there as **carried**, not closed by this plan.

### 7.d The CLOSE-04/CLOSE-05 settlement, independently re-derived from the requirement text

`146-12-SUMMARY.md` left this open, offering two readings without choosing. Read directly against
`.planning/REQUIREMENTS.md:276-279`, verbatim:

> - [ ] **CLOSE-04**: gh#15's acceptance criteria are reconciled **item by item** — each marked met,
>       met-as-corrected (naming the correction), or not-reachable-on-this-hardware (naming the reason).
> - [ ] **CLOSE-05**: Release notes describe the programming-behaviour change and the `--pulse-us`
>       addition in terms a stranger can act on.

**Independently agreed with the orchestrator's settlement.** CLOSE-04's verb is "are reconciled" and its
object is "gh#15's acceptance criteria" — not "gh#15 is answered" or "a comment is posted." The
reconciliation is a document-level act performed against the criteria as filed, and §7.b's structural check
above confirms the document performs exactly that act, item by item, using exactly the three literal
dispositions the requirement names and no fourth. CLOSE-05's verb is "describe" and its object is the
release notes' own prose — not "are published" or "ship inside a cut release." Neither requirement's text
contains "post," "publish," "comment," "cut," or "tag." The delivery-required reading is not supported by
either requirement's own wording. **Both are dischargeable by the artifacts as they stand.**

The three literal dispositions CLOSE-04 names — `met`, `met-as-corrected`, `not-reachable-on-this-hardware`
— are exactly the three `146-GH15-RECONCILIATION.md`'s disposition table uses as its closed vocabulary
(`146-GH15-RECONCILIATION.md:40-52`); the document does not invent a fourth.

**The unposted gh#15 comment is a carry-forward, not a blocker on this tick.** Recorded as owed: one
`gh issue comment` invocation against gh#15 in `henols/firestarter_prom`, body-file only, using the
already-frozen `146-GH15-RECONCILIATION.md` (blob `a36ee805a5a645f6d1010b409cd6cfb5434a56d1`) — owner
`/gsd-complete-milestone`, as the first act after it pushes this branch. Reason, measured at `903599a2` and
re-confirmed at `146-CITATIONS.md` §6.1 this phase: 9 of 11 cited planning artifacts, plus
`firestarter/include/eprom_params.h`, are absent from the pushed remotes as of this session; posting before
the push would ship roughly ten dead evidence links. This plan does not relax that finding and does not
post — it only ticks CLOSE-04/CLOSE-05 as dischargeable by content, which is a distinct question from
whether the post has been made.

### 7.e Operator authorization — Task 1 checkpoint resolved

Per §7.a, the operator's scoped authorization ("take it through the gate," covering this plan's internal
record work only) is recorded as the answer to Task 1's `<resume-signal>`. All five gates are green
(§7.c), the discharge table is complete (§7.b), and the CLOSE-04/CLOSE-05 settlement is independently
re-derived (§7.d) rather than merely inherited. Task 2 (the flip) and Task 3 (the phase-end structural
assertions) proceed on that basis.

### 7.f The flip — Task 2, executed and audited

Snapshots taken to `/tmp/gsd146/snap/{REQUIREMENTS,ROADMAP,STATE}.md` before any edit. Hand-edited (no
bulk requirements/roadmap/state verb called): five checkboxes and five traceability rows in
`.planning/REQUIREMENTS.md`; five coverage rows and one phase-checklist line in `.planning/ROADMAP.md`.

| Check | Result |
|---|---|
| `ticked` (§Close checkboxes, `[x]`) | `5` |
| `traceability` (REQUIREMENTS.md rows, Complete) | `5` |
| `coverage` (ROADMAP.md rows, Complete) | `5` |
| `still_pending` (either file) | `0` |
| `phase_checkbox` (Phase 146 line, checked + `(completed 2026-08-18)`) | `1` |
| `changed_lines` (`diff` against snapshots, both files, `^[<>]` lines) | **`32`** — matches this plan's own prediction exactly |
| `unattributable` (changed lines mentioning neither a `CLOSE-0N` id nor "Phase 146") | `0` |
| plan-count line (`**Plans**: 13 plans in 7 waves`) | already correct — `13` stated, `13` `146-*-PLAN.md` files on disk; **no edit made** |
| archived aggregate digest, `.planning/milestones/*REQUIREMENTS.md` (22 files) | `1e87db0cf2c3142e77262d566548b84a9d9ad8152e3322a52aec0e1ee1b20f12` before and after — `git diff --stat -- .planning/milestones/` is empty throughout, so before/after are the same reading by construction, not two independent measurements that happened to agree |
| Record gate, re-run after the flip | `rc=0`, tally `{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}` — no bucket moved |

Commit: `db7bb3e4` — `docs(146-13): tick CLOSE-01, CLOSE-02, CLOSE-03, CLOSE-04, CLOSE-05 -- Complete in
both coverage documents`.

### 7.g Phase-end structural assertions — Task 3

**The no-push arithmetic, all three repositories, re-measured after this plan's own commits:**

| Repository | `rev-list --count @{u}..HEAD` | §0 baseline | ≥ baseline? | Upstream SHA | Unchanged from §0? |
|---|---|---|---|---|---|
| meta | **292** | 233 | yes | `b6aa1dcb23ef9931105752ed6dd6badccf6719de` | yes |
| `firestarter` | **63** | 61 | yes | `fb7949c0bdd575177262a76af506cec3b73ea28b` | yes |
| `firestarter_app` | **18** | 16 | yes | `4d18b645ab18a2d2465f0f623062e9249eb24132` | yes |

No count dropped anywhere in the sequence §0 (233/61/16) → §4.8 (279/63/18) → §6.1 (287/63/18) → here
(292/63/18). All three upstream SHAs are byte-identical to their §0.1 values. Both readings — the
ahead-count and the upstream SHA — agree; nothing was pushed.

**The submodule pointer table — recorded as a delta, re-pin explicitly handed onward.**

| Repo | Tracked gitlink (`git ls-tree HEAD`) | Live HEAD (`git -C <repo> rev-parse HEAD`, this session) | Gitlink lag |
|---|---|---|---|
| `firestarter` | `0933bd7d602efb30e4a666e8231ecf724e90ab09` | `f8ac6439728fdb44665db38bc7e6d26b15fcda06` | 72 commits |
| `firestarter_app` | `cc036e8dc3cd77bbdfc7ec5190d79cdb172153c7` | `3cf429f52ad5f693076d309fc016e25f257d85cb` | 29 commits |

**Decision: hand off the re-pin to `/gsd-complete-milestone`, do not stage it here.** Both gitlinks
have been stale by the whole milestone (§0.4). This plan's own read of `146-LEDGER.md`'s
process-failures section (item 4, frozen, not edited by this plan) finds it has **already made and
recorded this exact call**: *"Re-pinning is handed to `/gsd-complete-milestone`, not done here — no
criterion in this ledger, or anywhere else in this phase, asserts that the pointers match, because
they do not and have not at any point this milestone."* Staging a re-pin here would put this register
in direct disagreement with a frozen, wording-approved closing artifact this plan is forbidden to
edit. The two SHA pairs above agree exactly with the ledger's own table (`146-LEDGER.md`'s process-
failures item 4); no criterion anywhere asserts they already match, per this plan's own prohibition.

**The consolidated negative-argv audit — at least thirteen forbidden operations, each with its
evidence:**

| # | Forbidden operation | Evidence it did not occur |
|---|---|---|
| 1 | `git push` (meta) | Ahead-count 292 ≥ 233; upstream SHA unchanged (table above) |
| 2 | `git push` (`firestarter`) | Ahead-count 63 ≥ 61; upstream SHA unchanged |
| 3 | `git push` (`firestarter_app`) | Ahead-count 18 ≥ 16; upstream SHA unchanged |
| 4 | `git merge` (any repo, into this branch or from it) | `git log --merges d2c212f1..HEAD --oneline` → 0 merge commits in the meta repo this phase; branch/HEAD unchanged in shape (linear history) |
| 5 | Tag creation | `git tag \| wc -l` → `18`, unchanged from every prior reading this phase; `git tag --points-at HEAD` → empty |
| 6 | `gh workflow run` (workflow dispatch) | No such command issued by any plan this session (self-attested from this plan's own command transcript, §7.c-§7.g); `.claude/settings.local.json` byte-unchanged (row 13) — no allowlist entry needed adding for one, and none was added |
| 7 | `gh release create` | Not invoked; `git tag` unchanged (row 5) rules out the tag half of any release |
| 8 | Package-index publish (`twine upload` / `publish.yml` dispatch) | Not invoked by this plan; no push occurred (rows 1-3) to trigger any CI-side publish path |
| 9 | gh#15 issue close | `state=OPEN` (re-queried this session, gh#15 table below) |
| 10 | gh#15 issue reopen | N/A — never closed (row 9) |
| 11 | gh#15 issue body edit | `lastEditedAt=null` (unchanged since §0.5) |
| 12 | gh#15 label add | `labels.totalCount=0` (unchanged since §0.5) |
| 13 | gh#15 assignee add | `assignees.totalCount=0` (re-queried this session) |
| 14 | gh#15 milestone set | `milestone=null` (re-queried this session) |
| 15 | gh#15 comment post | `comments.totalCount=1` (unchanged since §0.5/§5.2/§6.1) |

gh#15, re-queried this session (GraphQL, read-only): `state=OPEN`, `updatedAt=2026-08-09T19:32:04Z`,
`lastEditedAt=null`, `labels.totalCount=0`, `assignees.totalCount=0`, `milestone=null`,
`comments.totalCount=1`. Identical to every prior reading this phase. **`allowlist_dirty=0`** —
`git status --porcelain -- .claude/settings.local.json` is empty; no permission-allowlist entry was
added anywhere in this phase, by this plan or any prior one.

**The porcelain delta, stated against §0.3's enumerated baseline, not against emptiness:**

| Repository | §0.3 baseline (lines) | This reading (lines) | Delta |
|---|---|---|---|
| meta | 8 (` M .gitignore`, ` M .planning/STATE.md`, ` M firestarter`, ` M firestarter_app`, `?? .claude/`, `?? .planning/VALIDATED-EPROMS.md`, `?? package-lock.json`, `?? package.json`) | 7 (` M .gitignore`, ` M firestarter`, ` M firestarter_app`, `?? .claude/`, `?? .planning/VALIDATED-EPROMS.md`, `?? package-lock.json`, `?? package.json`) | **` M .planning/STATE.md` disappeared** — it was §0.3's own noted "expected dirt for every plan in this phase after the first" (the orchestrator's execution-start write), and by this reading a later plan's commit had already absorbed it; nothing new appeared |
| `firestarter` | 0 | 0 | none |
| `firestarter_app` | 7 (the same seven untracked paths enumerated in §0.3) | 7 (identical set, re-verified by path) | none |

This reading is taken **before** this task's own STATE.md commit lands; `.planning/STATE.md` is
expected to reappear as modified in the meta porcelain immediately after, which is this task's own
work, not drift.

**What was not touched, this task.** No file under `firestarter/` or `firestarter_app/` was created,
edited or deleted (D-06). No gate, fixture, pattern table or frozen closing artifact was edited. No
requirement id outside `CLOSE-01`..`CLOSE-05` was touched. `.claude/settings.local.json` is byte-
unchanged. Nothing was pushed, merged, tagged, dispatched, published, or posted to GitHub.

---
