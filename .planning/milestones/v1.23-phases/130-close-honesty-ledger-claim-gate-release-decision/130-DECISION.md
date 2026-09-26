# Phase 130 — CLOSE-04: Recorded `beta`-push Decision + Pre-flight Evidence

**Purpose:** CLOSE-04's text is literal — the accept/avoid/cleanup decision for the `beta` push
must be made and recorded **before any push**. v1.21's close skipped exactly this step and
auto-cut a stray `3.0.0b12` that is still public. This artifact's own commit timestamp is the
evidence that the decision preceded the act — nothing is pushed, merged, or published by this
plan or this file.

**No PY32F071 hardware exists.** Nothing measured below, and nothing decided below, is a claim
about a board — every figure is about a git ref, a CI run, a test suite, or a published tag.

---

## Pre-flight state (measured 2026-08-02T18:50–18:57Z)

**`130-RESEARCH.md`'s live-state table is stamped valid only until ~2026-08-09, and its own text
says branch tips and tag ceilings move the moment anyone pushes.** Every number below was
re-measured live in this session, not copied from RESEARCH. Verdict per item: **AGREES** or
**⚠ DRIFTED** against the recorded value.

Commands run were fetch-only (`git fetch origin`) plus read-only inspection (`rev-parse`,
`rev-list`, `tag --list`, `ls-tree`, `status --porcelain`, `git log <a>..<b>`, `git diff
--name-only`) plus read-only GitHub/PyPI inspection (`gh release list`). No merge, checkout,
commit, or push was executed against either sub-repo, and no `gh` write call was made.

### 1. Branch tips

| Repo | Branch | Tip SHA measured | RESEARCH-recorded | Verdict |
|------|--------|-------------------|--------------------|---------|
| `firestarter` | `v1.23-py32f071-integration` | `05c20bf59a4f0f73acf28d48d5dbbedab5724c5f` | `5a89ee7` | **⚠ DRIFTED — expected.** Two commits landed since RESEARCH: `c96b576` (`feat(130-03): swap py32 USB descriptor to pid.codes 1209:0001`) and `05c20bf` (`docs(130-03): rewrite [SHARED:S4] 5(a)/5(d)…`). This is plan 130-03 committing inside `firestarter`, not an out-of-band change. |
| `firestarter_app` | `v1.23-py32f071-integration` | `cc9452f4db9a814ffb221bab767c24db67288365` | `cc9452f` | **AGREES** — unchanged. This plan's own predecessors did not commit inside `firestarter_app`. |

Commands: `git -C firestarter rev-parse --abbrev-ref HEAD && git -C firestarter rev-parse HEAD`;
same for `firestarter_app`.

### 2. `origin/beta` tips (after `git fetch origin` in each repo)

| Repo | `origin/beta` SHA measured | RESEARCH-recorded | Verdict |
|------|------------------------------|--------------------|---------|
| `firestarter` | `5c9160a34b665878b05403ab014b959926feb6bf` | `5c9160a` | **AGREES** |
| `firestarter_app` | `e7d3ee8c8a41cd20e9159ab43b5cd969603d773e` | `e7d3ee8` | **AGREES** |

`origin/beta` has **not moved** in either repo since RESEARCH was written. The push-safety
premise this whole decision rests on is intact.

### 3. Ahead/behind counts (`git rev-list --left-right --count origin/beta...HEAD`)

| Repo | Measured (behind/ahead) | RESEARCH-recorded | Verdict |
|------|---------------------------|--------------------|---------|
| `firestarter` | `0 / 85` | `0 / 83` | **⚠ DRIFTED — expected**, by exactly the 2 commits named in item 1. Still **0 behind**: the outbound merge is still clean. |
| `firestarter_app` | `0 / 37` | `0 / 37` | **AGREES** |

Zero behind in both is what makes the outbound `--no-ff` merge clean in both repos, with no
inbound catch-up to plan.

### 4. Local `beta` versus `origin/beta`

| Repo | Local `beta` SHA | `origin/beta` SHA | Verdict |
|------|-------------------|---------------------|---------|
| `firestarter` | `5c9160a34b665878b05403ab014b959926feb6bf` | `5c9160a34b665878b05403ab014b959926feb6bf` | **AGREES — 0/0**, matching RESEARCH exactly |
| `firestarter_app` | `e7d3ee8c8a41cd20e9159ab43b5cd969603d773e` | `e7d3ee8c8a41cd20e9159ab43b5cd969603d773e` | **AGREES — 0/0** |

**Standing hazard, recorded rather than assumed away:** once CI cuts the next beta in either
repo, `git-auto-commit-action` pushes a version-bump commit directly onto `beta`, so local `beta`
becomes one commit behind the remote in that repo. Any later local operation that touches `beta`
in either repo must `git fetch` first — this is the exact mechanism that produced the current
`origin/beta` tips above from the prior (b14) cut.

### 5. Version strings on both sides

| Repo | File | `origin/beta` value (measured) | Working-tree value (measured) | Verdict |
|------|------|-----------------------------------|----------------------------------|---------|
| `firestarter` | `include/version.h` | `VERSION "3.0.0b14"` | `VERSION "3.0.0b14"` | **AGREES.** The working tree still declares the last-cut version; the branch does not carry a pre-bumped version string, matching v1.22's pattern (D-05: the merge itself is the cut). |
| `firestarter_app` | `firestarter/__init__.py` | `__version__ = "3.0.0b14"` | `__version__ = "3.0.0b14"` | **AGREES** |

### 6. Highest `3.0.0b*` tag in both repos, and the absence of the next one

`git tag --list '3.0.0b*' | sort -V | tail -3` in both repos:

```
3.0.0b12
3.0.0b13
3.0.0b14
```

Identical highest tag in both `firestarter` and `firestarter_app`: **`3.0.0b14`**. The next
sequential tag is **absent from both**. **AGREES** with RESEARCH.

This makes the auto-increment target *derivable*, not assumed: `is_beta_mode()` returns true on
a push to `beta`, `compute_beta_version` falls back to a git tag scan of `3.0.0b*` and takes
max-plus-one, and `checkout` uses `fetch-depth: 0` so all tags are present at scan time. **This
does not relax CONSTRAINT 5.** A concurrent cut, an out-of-band tag, or a rehearsal-tag collision
would change the derived value — so the tag consumed by every downstream step in the accepted
sequence below is the one read from `gh release list` **after** the cut, never a literal written
into a command here. No command anywhere in this file writes the derived literal; every command
written for verbatim execution uses `<observed tag>`.

`gh release list` in both repos, run this session (read-only, no write):

```
firestarter:      3.0.0b14  Pre-release  3.0.0b14  2026-07-30T14:28:19Z   (newest)
firestarter_app:  3.0.0b14  Pre-release  3.0.0b14  2026-07-30T14:58:35Z   (newest)
```

Neither repo shows a newer prerelease than `3.0.0b14`. **AGREES** with RESEARCH's live-state
table.

### 7. No-op: dry-run merge-conflict probe

`122-DECISION.md`'s `git merge-tree --write-tree --messages HEAD origin/beta` probe has **no
subject here**: both repos measured **0 behind** `origin/beta` (item 3), so there is no inbound
content for either branch to conflict against — the outbound merge is a fast, clean `--no-ff`
merge of ahead-only work. Recorded as a **no-op**, not manufactured as an artifact, per this
plan's own prohibition.

### 8. No-op: `--ours` superset proof

Same reason as item 7: the `--ours` superset proof exists in `122-DECISION.md` only because
`firestarter_app`'s v1.22 merge had two genuinely conflicting files against an inbound `beta`
delta. With 0 behind in both repos this session, there is no conflict to resolve and nothing to
prove a superset of. Recorded as a **no-op**.

### 9. Meta gitlink assertion (D-04)

`git -C /workspaces ls-tree HEAD firestarter firestarter_app`:

```
160000 commit 5a89ee76dc4681abe18db259e57bb92f519520f4  firestarter
160000 commit cc9452f4db9a814ffb221bab767c24db67288365  firestarter_app
```

| Repo | Gitlink (meta HEAD) | Working tip (item 1) | Match? |
|------|----------------------|------------------------|--------|
| `firestarter` | `5a89ee7…` | `05c20bf…` | **No — expected.** D-04 **asserts** the gitlink matches the working tip; it does not pin the gitlink unchanged (that is v1.22's model, explicitly declined for this milestone). Plan 130-03's two commits (item 1) moved the firmware tip after the gitlink was last bumped. **Plan 130-16 owns re-bumping this gitlink** as part of its closing sweep (CONSTRAINT 10) — not this plan. |
| `firestarter_app` | `cc9452f…` | `cc9452f…` | **Yes.** No bump needed; no plan in this phase committed inside `firestarter_app`. |

This plan does **not** stage or commit either gitlink. `git status --porcelain` in `/workspaces`
shows ` M firestarter` and ` M firestarter_app` (item 10) as the expected, unstaged consequence of
each submodule's checked-out HEAD differing from the committed pointer — this is the correct,
temporary state until plan 130-16 asserts and re-bumps it.

### 10. Working-tree dirt, all three repos (`git status --porcelain`)

**`firestarter`:**
```
(clean — no output)
```
The firmware working tree is fully clean. This is directly relevant to the sync gate's own
`test_dirty_tree_is_detected` leg (RESEARCH "Things That Would Break a Plan" item 10): a clean
tree here is not this plan's accomplishment, it predates this plan, and it must not be read as
evidence this plan produced.

**`firestarter_app`:**
```
 M .gitignore
?? .coverage
?? .planning/config.json
?? SECURITY.md
?? write_test_port.sh
```
**Pre-existing dirt, predating this phase**, itemized so a later cleanliness assertion does not
mistake it for this phase's damage: the modified `.gitignore` and the four untracked items
(`.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`) were already present
in `130-RESEARCH.md`'s live-state table and in `122-DECISION.md`'s own equivalent section. No
plan in this phase edited, staged, or committed any of them.

**`/workspaces` (meta):**
```
 M firestarter
 M firestarter_app
```
Both are the gitlink-versus-working-tip deltas named in item 9 — `firestarter_app`'s gitlink
matches its tip exactly (byte-for-byte), so its ` M` marker here reflects only the submodule's own
internal dirt (the block above), not a commit delta.

### 11. `paths-ignore` will not suppress either cut

Non-ignored changed files measured against `origin/beta`, using each workflow's own ignore list
(`firestarter/.github/workflows/beta-build.yml`: `**.md`, `**.sh`, `.gitignore`, `docs/**`,
`documents/**`, `images/**`, `.vscode/**`, `.editorconfig/**`; `firestarter_app/.github/workflows/beta-release.yml`
additionally: `.github/**`, `tools/**`):

| Repo | Non-ignored changed files vs `origin/beta` | RESEARCH-recorded | Verdict |
|------|-----------------------------------------------|--------------------|---------|
| `firestarter` | **112** | 112 | **AGREES** |
| `firestarter_app` | **32** | 32 | **AGREES** |

Both counts are well above zero, so `paths-ignore` suppresses neither cut. Separately,
`firestarter/.github/workflows/py32f071.yml` carries `push: branches: [beta]` with **no** paths
filter of any kind, so the LOUD ARM gate fires unconditionally on the outbound push regardless of
which files changed. Worth recording explicitly: a documentation-only close would silently cut
**nothing** while looking successful; this close is not documentation-only, and both figures above
confirm it.

### 12. The gates, run on this exact tree (CONSTRAINT 9)

Every gate below was run in this session, on the tree named by item 1's SHAs — the tree that will
be merged, not an earlier or hypothetical one.

| Gate | Command | Result |
|------|---------|--------|
| `firestarter` suite | `python3 -m pytest tests/ -q` | **221 passed** (matches RESEARCH exactly) |
| `firestarter` native | `pio test -e native` | **141 test cases, 17 suites, 141 succeeded** (matches RESEARCH exactly) |
| `firestarter` sync gate | `FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q` | **41 passed** |
| `firestarter_app` suite (C-13 gate) | `python3 -m pytest tests/ -v --tb=no` | **1303 passed in 111.14s** (matches RESEARCH exactly) |
| `firestarter_app` codegen check | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | `OK: catalog valid (73 messages, version 1).` exit 0 |
| `firestarter_app` codegen drift | `git diff --exit-code firestarter/messages.py` | clean, exit 0 |
| CLOSE-01 checker, default mode | `python3 check_record_corrections.py` | `PASS: scanned .planning/PROJECT.md, .planning/STATE.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md, .planning/notes/py32f071-port-branch-state.md; exempt hits by verdict: {'block': 23, 'line-label': 5, 'inline-history': 6, 'inline-allow': 13, 'superseded': 13}` exit 0 |
| CLOSE-01 checker fixture suite | `python3 -m pytest test_check_record_corrections.py -q` | **20 passed** |
| Claim gate, default mode | `cd .planning/phases/123-non-regression-baselines-gate-hardening && python3 check_permitted_claims.py` | **FAIL** (see note below) |
| Claim gate suite | `python3 -m pytest test_check_permitted_claims.py -q` | **11 passed** |

**Note on the claim-gate row — this is the expected transitional state, not a gate the operator
must not push past.** Run *before* this file existed, it reported: `FAIL: armed (at least one of
the 4 named v1.23 closing artifacts exists) but not all 4 exist -- a half-written close is a hard
failure (D-15). Missing: ['.../130-DECISION.md']` — naming this file, and only this file, as
missing. That is the intended pre-commit state: `130-LEDGER.md`, `130-RELEASE-NOTES-fw.md` and
`130-RELEASE-NOTES-app.md` already exist on disk; this file is the fourth. The moment this file is
committed, the gate has all four and — per plan 130-13's Task 2 — is re-run and recorded going
green. If it is *not* green after this commit, that **is** a real RED and the operator must not
push; Task 2 below records the actual post-commit result.

**Environment note (RESEARCH assumption A2, MEDIUM risk):** every suite above ran on Python 3.12
locally; both CI workflows pin Python 3.11. The known live-board REDs
(`test_no_programmer_found_*`) cannot fire on a runner with no `/dev/ttyACM*` attached, and the
HOST-04 mypy-debt failure lives in the separate `ci.yml` workflow, which does not gate the cut.
No 3.11-specific RED was reachable from this devcontainer's toolchain this session; this residual
risk is recorded, not eliminated.

**All ten gates are green except the claim gate, whose one RED is this file's own absence and is
resolved by this file's own commit (verified in Task 2 below).** No other RED was observed. If any
gate other than the claim gate had come back RED, this plan would stop here and record it as a
reason the operator must not push — none did.

### No mutation occurred (pre-flight)

Confirmed after every command above: `git -C firestarter rev-parse HEAD` still
`05c20bf59a4f0f73acf28d48d5dbbedab5724c5f`; `git -C firestarter_app rev-parse HEAD` still
`cc9452f4db9a814ffb221bab767c24db67288365`; `git -C firestarter rev-parse origin/beta` still
`5c9160a34b665878b05403ab014b959926feb6bf`; `git -C firestarter_app rev-parse origin/beta` still
`e7d3ee8c8a41cd20e9159ab43b5cd969603d773e` — unchanged from items 1 and 2 above. Neither gitlink
was staged. No `gh` write call was made; only `gh release list` (read-only).

### ⚠ Divergence from 130-RESEARCH.md

**Two items drifted, both expected and both explained: item 1 and item 3, `firestarter`'s branch
tip and ahead-count, moved by exactly the two commits plan 130-03 landed since RESEARCH was
written.** Every other item — both `origin/beta` tips, both local-`beta` states, both version
strings, both tag ceilings, both non-ignored file counts, the `firestarter_app` gitlink, and every
gate result — matches RESEARCH's recorded value exactly. `origin/beta` has not moved in either
repo. The accepted sequence below rests on an unchanged foundation for the one fact that matters
most: neither repo has been pushed to since RESEARCH, and both remain 0 behind.

---

## The decision (CLOSE-04)

### The three options, all recorded (CLOSE-04 asks for accept/avoid/cleanup, not merely a plan)

| Option | Disposition | Why |
|---|---|---|
| **ACCEPT** | **CHOSEN** | Both repos carry `on: push: branches: [beta]` with git-tag-scan auto-increment (item 6) and both sit at a `3.0.0b14` ceiling with the next tag absent from both (item 6), so the outbound `--no-ff` merge push cuts the next beta by itself in both repos — no separate cut step is needed or wanted. This is the first publication of `firestarter_py32f071.hex` as a real release asset, which is the only thing that makes the already-landed host capabilities (the DFU installer, `--dfu-probe`, `--usb-id`, the beta-gated `py32f071` board choice) reachable by anyone outside this tree. The two halves are lockstep by construction: a firmware asset with no published host that can install it is inert, and a host installer with no published firmware asset to install is equally inert. Risk is bounded on both sides of that pairing: no PY32F071 board exists anywhere (item 10, and this file's own header), and the py32 board choice is beta-only by construction (`_BOARD_CHOICES` computed from the installed app's own version at CLI-import time — a stable release of the host app hides it entirely). |
| **AVOID** | **DECLINED** | A recorded no-push leaves the milestone's one user-visible deliverable — `firestarter_py32f071.hex` as a real, downloadable asset — permanently unexercised, and makes both `130-RELEASE-NOTES-fw.md` and `130-RELEASE-NOTES-app.md` notes for nothing. Stated explicitly: no workflow trigger is edited by this phase in either repo, and `paths-ignore` (item 11) is not weakened in either repo. |
| **CLEANUP** | **DECLINED** | The stray `3.0.0b12` prereleases (both repos, published 2026-07-27) stay public. Cleaning them up was already declined at v1.22 D-05 for the same reason that still holds: `b12` has been public for roughly a week and may already be installed by someone, and force-removing a published artifact is an operator-driven outward-facing act, not close work. Stated explicitly: no `--force` push, no history rewrite, and no deletion of any published artifact occurs in this phase. |

**A fourth option was considered and declined at D-01, named so it is not silently re-opened:**
**accept gated on a fresh `rehearsal=true` dispatch.** Declined because CI run `30722352902`
(SHA `7a0a375`, `conclusion: success`) already demonstrated the full pipeline — the ARM target
configuring and linking inside the same job as the three AVR images, and the resulting
`firestarter_py32f071.hex` asset publishing and remaining readable — and re-deriving that evidence
with a second rehearsal costs an operator round-trip plus a draft-release cleanup for no new
information. A second run, `30722537152` (SHA `6c1c31f`, `conclusion: success`), separately
rehearsed a deliberately broken ARM leg and confirmed the three AVR assets still publish with a
warning annotation naming the missing py32 asset — proving the failure-containment path without
needing a third dispatch either.

### The accepted sequence, each step naming its owning plan and the CONTEXT constraint it satisfies

Each item is marked **Agent** or **Operator**.

1. **This decision recorded and committed** — plan 130-13, CONSTRAINT 1 (CLOSE-04's literal text:
   the decision exists and precedes any push). **Agent.**
2. **The `usb_cdc.c` descriptor swap to pid.codes `1209:0001`, its `[SHARED:S4]` §5(a)+§5(d)
   lockstep body update in both copies, and a local ARM pass** — plan 130-03, CONSTRAINT 2.
   **Agent.** Outcome, as item 12 measured this session's re-run of the sync gate (41 passed): the
   ARM configure-and-build exited 0 both before and after the descriptor edit; the rebuild recompiled
   **exactly one** translation unit (`usb_cdc.c`'s object) plus the final link; the `.hex` SHA-256
   differs between the two builds (the descriptor bytes changed, by design) while the `.text`/
   `.data`/`.bss` totals are numerically identical at both the object and image level — a
   size-neutral value swap, reported as a **confined delta only**, never as byte-identity and never
   as an absolute CI-comparable size. No LOUD-gate fallback was needed: the local pass completed.
3. **`130-LEDGER.md` written before either release-notes draft** — plan 130-11, CONSTRAINT 3.
   **Agent.**
4. **Both release bodies hand-written as committed drafts, and the blocking operator wording
   review** — plan 130-12 for the drafts, CONSTRAINT 4 for the review. **Operator** for the review
   itself, and it precedes step 5. The drafts as committed already carry the canonical caveat, the
   pid.codes should-not-must wording (C-6), and the negative-space sections; the review's job is
   judging tone and omission, which no scanner in this phase can do (see the "mechanizable half
   only" non-claim, restated below).
5. **The outbound `--no-ff` merge of the milestone branch into `beta`, and the push, in both
   sub-repos** — plan 130-14's written procedure. **Operator.** Stated plainly: **no plan in this
   phase or any prior phase contains this command.** Item 3's zero-behind measurement is what makes
   this merge clean rather than a merge requiring conflict resolution.
6. **CI cuts the beta in both repos.** Automatic, no human or agent dispatch. Record that
   `firestarter`'s `beta-build.yml` ARM step is `continue-on-error: true` by design (keyed on
   `outcome`, not `conclusion`), so a green run of that workflow is **not** evidence the py32 asset
   actually published — and that `py32f071.yml`'s unconditional, unfiltered `push: branches: [beta]`
   trigger (item 11) fires regardless and says explicitly what broke if anything does.
7. **The observed cut tag read from `gh release list` in both repos** — plan 130-15, CONSTRAINT 5.
   **Agent, read-only.** Never computed: item 6 above shows the value is derivable (`b15` in both
   repos, from the tag-scan arithmetic), but the value actually consumed downstream is the one
   `gh release list` reports **after** the cut. Every command written for verbatim execution in
   this file and in plan 130-15's procedure uses the literal placeholder `<observed tag>`.
8. **A manual `workflow_dispatch` of `firestarter_app`'s `publish.yml` with `tag=<observed tag>`**
   — plan 130-14's procedure, CONSTRAINT 6. **Operator.** Recorded why it is manual, not automatic:
   `publish.yml`'s own in-file comment states that when a release is created by another workflow
   using a PAT lacking `workflow` scope, GitHub suppresses the `release.published` event that would
   otherwise trigger it — and `3.0.0b12`'s absence from PyPI (confirmed this session, item 6's `gh`
   read plus RESEARCH's PyPI check) corroborates it. Six of the thirteen previously published app
   betas never reached PyPI by the automatic path. The `tag` input flows directly into `publish.yml`'s
   `ref:` for the checkout it performs, so the value dispatched must be the **observed** tag from
   step 7 and never an untrusted, guessed, or computed one (Security V5).
9. **`firestarter_py32f071.hex` asserted present among the real cut's release assets** — plan
   130-15, CONSTRAINT 8, D-03. **Agent, read-only.** `continue-on-error: true` (step 6) means a
   green CI tick is never accepted as this proof; the assertion is made against `gh release view
   <observed tag> --repo henols/firestarter --json assets` on the actual, non-rehearsal cut.
10. **Both channels verified public, PyPI resolution checked from a clean temp env** — plan
    130-15, CONSTRAINT 7. **Agent.** `python3 -m venv` + `pip download --no-deps --pre` against the
    observed tag, not inferred from a green `publish.yml` run.
11. **Both release bodies posted after the D-02 review (step 4)** — plan 130-14's procedure.
    **Operator.**
12. **The closing sweep: the gitlink assertion and re-bump named in item 9 above, and the
    CLOSE-01…CLOSE-04 ticks** — plan 130-16, CONSTRAINT 10. **Agent.** Stated plainly, per this
    plan's own held-writes contract: **plan 130-16 is the only plan in this phase permitted to tick
    a CLOSE requirement id.** This plan ticks none.
13. **Out of scope for this phase**, named so it is not silently re-opened: the `v1.23` annotated
    tag and any merge toward `main`, both of which stay with `/gsd-complete-milestone` (D-04,
    mirroring v1.21's and v1.22's precedent); any stable release; deleting the stray `b12`
    prereleases (the declined CLEANUP option above).

### Facts the sequence depends on

- Both repos measured **0 behind** `origin/beta` (item 3) — the outbound merge is clean in both,
  with no inbound catch-up to plan.
- The tag ceiling is **`3.0.0b14`** in both repos, with the next tag absent from both (item 6) —
  what makes the auto-increment target derivable without being assumed.
- Both pushes will trigger despite `paths-ignore` — **112** and **32** non-ignored changed files
  respectively (item 11).
- The app's blocking pre-cut steps — the full suite, the catalog check, and the codegen-drift
  gate — are all green on this exact tree (item 12), which is what RESEARCH C-13 names as the
  single worst-outcome-avoidance measurement in this phase: a RED there would mean no app cut at
  all, **after** the firmware half has already published, breaking the lockstep pairing this
  decision's ACCEPT option rests on.

### Out of scope for this phase (mirrors D-04, restated for CLOSE-04)

The **`v1.23` annotated tag** and the **meta-repo's final gitlink state** both stay with
`/gsd-complete-milestone` for the tag; the gitlink re-bump itself is plan 130-16's job **within**
this phase (item 9 above), not deferred to milestone-close the way v1.22 pinned it. This is a
deliberate departure from v1.22's model, matching this milestone's own in-phase gitlink practice
at Phases 125, 128 and 129.

---

## The USB-identity descriptor tension (D-17)

Recording this reasoning in full, rather than leaving it implicit, is precisely the discipline
this phase's own D-11 third rejected option (an outward-facing artifact that omits a known
problem) was rejected for.

`.planning/v1.23-FLASH-PATH-DECISION.md` §5(c), verbatim and unchanged by this plan:

> **Ship gate: no PY32F071 board ships, and no release advertises a USB identity, until a PID
> allocated under VID 0x1209 exists.**
>
> This is deliberately a condition rather than a warning, so a future reader can fail it.

`1209:0001` — the value `usb_cdc.c` now presents, per plan 130-03 — is the registry's own
documented private-testing product id, explicitly **not** an allocated PID (§5(b)). The plain
reading of §5(c)'s second clause is that this release discloses a USB identity before an
allocation exists, and §5(c)'s own wording says outright that it is written as a condition
precisely so a future reader **can** find it unmet.

**This file leaves §5(c) byte-unchanged**, in both the meta and firmware copies. The reasoning:
amending a condition so that the very act about to be taken clears it destroys the condition's
whole mechanism — the same fail-open move BASE-08 exists to prevent elsewhere in this project.
A gate that gets reworded the moment it becomes inconvenient is not a gate.

**Why this phase does not read a caveated disclosure of an explicitly non-allocated test id as
*advertising an identity*:** `1209:0001` is disclosed in the release body (`130-RELEASE-NOTES-fw.md`
§"The USB identity this image presents") as a *judgment call recorded, not a claim asserted* —
the body states plainly that `1209:0001` is not an allocated PID, that it replaces a pair this
project had no right to present (the silicon vendor's own registered `0x36B7:0xFFFF`), and that
whether this counts as "advertising" is left to the reader rather than decided by the release
itself. Advertising, in the ordinary sense this project's own record uses the word, is an
unqualified assertion of ownership; a disclosure that names its own non-allocated, interim, and
explicitly caveated status is closer to a confession than a claim. **A future reader may
reasonably disagree with that reading — the condition's own wording deliberately permits exactly
that disagreement**, and the operator may overrule this judgment entirely at the D-02 wording
review named in the accepted sequence's step 4.

**RESEARCH assumption A3, recorded as a judgment call, not a settled reading of the registry's
terms:** publishing a `.hex` release asset that carries `1209:0001` is taken **not** to trip
pid.codes' clause forbidding the id's use "on any device that will be redistributed, sold, or
manufactured," because no device — no physical board — is being redistributed; only a firmware
file is. This is a reasoned inference about a registry's own wording, not a fact independently
confirmed with pid.codes; §5(b) transcribes the terms from this project's own prior record rather
than a fresh fetch this session (RESEARCH C-6, MEDIUM confidence on the transcription). The
operator may overrule this reading at the same D-02 review.

**Also recorded, so no reader concludes this milestone chose to weaken the wording obligation:**
pid.codes' own terms, transcribed at `.planning/v1.23-FLASH-PATH-DECISION.md:198`, **ask** — they
do not require — that source referencing `1209:0001` warn a reader it is not universally unique.
`usb_cdc.c`'s in-source comment (landed by plan 130-03) is worded to match that ask exactly, and
neither this file nor either release body ever upgrades that SHOULD to a MUST.

---

## No mutation occurred

Named explicitly and last, because this is the entire evidentiary weight this file carries:

- **No push** to `origin/beta` or any other remote ref, in either sub-repo.
- **No merge** into `beta`, local or remote, in either sub-repo.
- **No tag** created, moved, or pushed, annotated or lightweight, in either sub-repo or the meta
  repo.
- **No `gh workflow run`** or any other `workflow_dispatch` invocation.
- **No GitHub release created, edited, or deleted**, by `gh` or any other means.
- **No `twine upload`** or any other package upload, to PyPI or any other index.
- **No force push**, in either sub-repo.
- **No history rewrite**, in either sub-repo or the meta repo.
- **No deletion of any published artifact** — the stray `3.0.0b12` prereleases (CLEANUP, declined
  above) remain exactly as public as they were before this plan started.

The only commands run against either sub-repo were `git fetch origin` (fetch-only), `git
rev-parse`, `git rev-list`, `git tag --list`, `git log <a>..<b>`, `git diff --name-only`, `git
status --porcelain`, `git ls-tree` (all read-only), plus `python3 -m pytest`, `pio test`, and this
phase's two Python checkers (all read-only against the working tree, none of them writing to
git). The only `gh` command run was `gh release list` (read-only).

`git -C firestarter rev-parse origin/beta` and `git -C firestarter_app rev-parse origin/beta`
remain, after every command in this file, exactly the values recorded in item 2 above:
`5c9160a34b665878b05403ab014b959926feb6bf` and `e7d3ee8c8a41cd20e9159ab43b5cd969603d773e`. Neither
moved.

---

## Summary of what this artifact proves

1. The pre-flight evidence this decision rests on was measured **live**, in this session, not
   copied from a document with a stated validity window — and it agrees with that document on
   every item except the two expected drifts named above, both explained by this phase's own
   prior work.
2. The decision names all four considered options (accept/avoid/cleanup, plus the declined
   rehearsal-gated variant), which was chosen, and why the others were declined, in writing.
3. Every one of ten measured gates is green on the exact tree that will be merged, with the app's
   full suite recorded as a **gate** rather than an assumption (RESEARCH C-13) — the single
   worst-outcome-avoidance measurement this phase makes. The one RED observed (the claim gate,
   pre-commit) is this file's own absence, resolved by this file's own commit, and re-verified
   green in plan 130-13's Task 2.
4. The accepted sequence names an owning plan and a CONTEXT constraint for every step, and marks
   every step **Agent** or **Operator** — every privileged command is structurally absent from
   every plan in this phase, never merely gated by a checkpoint type.
5. The USB-identity tension (D-17) and research assumption A3 are both recorded as explicit,
   overrulable judgments rather than left implicit or silently resolved.
6. Nothing has been pushed, merged, tagged, dispatched, or published. Both sub-repos' `HEAD`s,
   both `origin/beta` tips, and the meta repo's gitlink state (item 9's known, expected, and
   plan-130-16-owned exception) are all exactly where they were before this plan started.
7. This file's own commit (recorded by `git log` immediately after this write, and cited in
   `130-13-SUMMARY.md`) is the evidence that the decision preceded the act — the ordering
   CLOSE-04's literal text requires.

**A green result from the claim gate or any checker named in this file is the mechanizable half
of this milestone's honesty criterion only.** It cannot detect an implied overclaim, a misleading
omission, or wrong tone. It must never be reported, here or in any SUMMARY, as by itself
satisfying the honesty criterion — that is the blocking operator wording review's job (step 4
above), not this file's and not any scanner's.

---

*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Written: 2026-08-02 (Plan 130-13)*
