# Phase 122 Plan 12 — The Delivery Record

**Written:** 2026-07-30 (Plan 122-12, wave 10)
**Purpose:** The committed proof that all four outward-facing deliveries — both prerelease bodies
and both community comments — were posted exclusively from the five files `122-11-SUMMARY.md` froze
by committed git blob SHA, verified byte-equal both before and after each call, with both issues
staying `OPEN` and label-free throughout. This is the record `122-13` reads when it ticks CLOSE-02
and CLOSE-03.

**Observed cut tag (read from `122-CUT.md`, never hardcoded):** `3.0.0b14` (both repos).

---

## 1. Pre-flight — blob SHAs re-asserted immediately before any call

All five frozen artifacts (only four are delivered by this plan; `122-LEDGER.md` is the fifth,
delivered nowhere — it is the internal source-of-truth, not an outward artifact) were re-checked
against `122-11-SUMMARY.md`'s freeze table:

| File | Frozen blob SHA (`122-11-SUMMARY.md`) | Re-measured blob SHA (this plan, pre-call) | Match | `git status --porcelain` |
|---|---|---|---|---|
| `122-RELEASE-NOTES-fw.md` | `897848c44df9c15f7d273d726f1e14b53526fc97` | `897848c44df9c15f7d273d726f1e14b53526fc97` | ✅ | empty |
| `122-RELEASE-NOTES-app.md` | `b253b73b8b14d3b56a1fa292c0ac07dbd0d8ceda` | `b253b73b8b14d3b56a1fa292c0ac07dbd0d8ceda` | ✅ | empty |
| `122-GH11-COMMENT.md` | `f72fa20f96539ec89b8c32de5a4af8e208e21a3b` | `f72fa20f96539ec89b8c32de5a4af8e208e21a3b` | ✅ | empty |
| `122-GH12-COMMENT.md` | `454db0fd48540b3b0e56eaa116340071c02164c6` | `454db0fd48540b3b0e56eaa116340071c02164c6` | ✅ | empty |

All four SHAs matched exactly. The working tree carried zero uncommitted changes to any of the
four files. Nothing the operator did not review was posted.

## 2. Operator's final go/no-go — recorded verbatim

Task 2 of this plan is the BLOCKING final go/no-go, positioned after the two release bodies are
live and rendered — new information the D-16 wording review (122-11) did not have. Per the dispatch
prompt's `<operator_final_go_granted>` block, the operator had already been shown (by the
orchestrator, ahead of this plan's execution): all five artifacts frozen at committed blob SHAs with
a clean working tree; the exact four outward-facing calls and their frozen blobs; confirmation that
nothing had yet been posted (`gh#11` at 12 comments, `gh#12` at 8, both `OPEN`, both release bodies
length 0); and the explicit statement that a posted comment notifies real subscribers immediately
and cannot be recalled. The operator had already read both comment drafts in full and approved the
wording at the D-16 review (122-11), accepting the C-5 correction.

**Operator's verbatim verdict, 2026-07-30:**

> "Post it — all four calls."

Read per this plan's Task 2 acceptance criteria: unconditional go on all four calls (both release
bodies, both comments); no change named to either release body; both comment drafts' blob SHAs
re-confirmed unchanged at the moment the gate closed (§1 above, re-run again in §4 below
immediately before the `gh issue comment` calls); both issues confirmed still `OPEN` with unchanged
comment counts at the moment the gate closed. No re-prompt was issued — the go/no-go was already
satisfied before this plan began the delivery calls, per the dispatch instruction.

## 3. The four delivery calls

| # | Target | Exact argv | Source file + frozen blob SHA | Byte-equality verdict | Result URL |
|---|---|---|---|---|---|
| 1 | Firmware prerelease body (`henols/firestarter` `3.0.0b14`) | `gh release edit 3.0.0b14 --repo henols/firestarter --notes-file .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-RELEASE-NOTES-fw.md` | `122-RELEASE-NOTES-fw.md` @ `897848c44df9c15f7d273d726f1e14b53526fc97` (5284 bytes) | **byte-equal** under one normalization: GitHub appended exactly one trailing newline (5284→5285 bytes; `diff` on the sole trailing-newline-normalized streams showed no content difference, only line 84's added blank line) | https://github.com/henols/firestarter/releases/tag/3.0.0b14 |
| 2 | App prerelease body (`henols/firestarter_app` `3.0.0b14`) | `gh release edit 3.0.0b14 --repo henols/firestarter_app --notes-file .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-RELEASE-NOTES-app.md` | `122-RELEASE-NOTES-app.md` @ `b253b73b8b14d3b56a1fa292c0ac07dbd0d8ceda` (4507 bytes) | **byte-equal** under one normalization: GitHub appended exactly one trailing newline (4507→4508 bytes; same single-blank-line-at-EOF diff, no content difference) | https://github.com/henols/firestarter_app/releases/tag/3.0.0b14 |
| 3 | Issue comment (`henols/firestarter_prom` #11) | `gh issue comment 11 --repo henols/firestarter_prom --body-file .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-GH11-COMMENT.md` | `122-GH11-COMMENT.md` @ `f72fa20f96539ec89b8c32de5a4af8e208e21a3b` (4887 bytes) | **byte-equal** under one normalization: GitHub appended exactly one trailing newline (4887→4888 bytes; single-blank-line-at-EOF diff only) | https://github.com/henols/firestarter_prom/issues/11#issuecomment-5133252178 |
| 4 | Issue comment (`henols/firestarter_prom` #12) | `gh issue comment 12 --repo henols/firestarter_prom --body-file .planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-GH12-COMMENT.md` | `122-GH12-COMMENT.md` @ `454db0fd48540b3b0e56eaa116340071c02164c6` (5122 bytes) | **byte-equal** under one normalization: GitHub appended exactly one trailing newline (5122→5123 bytes; single-blank-line-at-EOF diff only) | https://github.com/henols/firestarter_prom/issues/12#issuecomment-5133257778 |

**Normalization applied, stated once for all four rows:** CRLF→LF (no CRLF present in any of the
four retrieved bodies — a no-op in practice) and collapsing to a single trailing newline. In every
one of the four cases the *only* difference between the committed file and the retrieved body was
GitHub appending exactly one trailing newline the committed file did not already end with; the byte
length differs by exactly 1 in all four cases, and the line-level `diff` shows exactly one added
blank line at end-of-file and nothing else. No other divergence occurred on any of the four calls.

**Retrieval commands used for the byte-equality proof:**
- Release bodies: `gh release view <tag> --repo <repo> --json body -q '.body'`, piped through
  `tr -d '\r'`, written to a file in `$(mktemp -d)`.
- Issue comments: `gh issue view <n> --repo henols/firestarter_prom --json comments -q
  '.comments[-1].body'`, piped through `tr -d '\r'`, written to a file in `$(mktemp -d)`.
- Comparison: `diff <(sed -e '$a\' <committed file>) <(sed -e '$a\' <retrieved file>)` — the
  `sed -e '$a\'` idiom ensures both sides end in exactly one newline before comparing, isolating the
  trailing-newline normalization from any real content difference.

## 4. Before/after issue state and the exact-increment assertion

Pre-delivery state (re-read immediately before the two `gh issue comment` calls, matching
`122-08-SUMMARY.md`'s recorded baseline of 12/8 exactly):

```
$ gh issue view 11 --repo henols/firestarter_prom --json state,comments,labels -q '{state:.state,n:(.comments|length),labels:.labels}'
{"labels":[],"n":12,"state":"OPEN"}
$ gh issue view 12 --repo henols/firestarter_prom --json state,comments,labels -q '{state:.state,n:(.comments|length),labels:.labels}'
{"labels":[],"n":8,"state":"OPEN"}
```

Post-delivery state (read immediately after both `gh issue comment` calls completed):

```
$ gh issue view 11 --repo henols/firestarter_prom --json state,comments,labels -q '{state:.state,n:(.comments|length),labels:.labels}'
{"labels":[],"n":13,"state":"OPEN"}
$ gh issue view 12 --repo henols/firestarter_prom --json state,comments,labels -q '{state:.state,n:(.comments|length),labels:.labels}'
{"labels":[],"n":9,"state":"OPEN"}
```

| Assertion | Issue 11 | Issue 12 | Result |
|---|---|---|---|
| Comment count incremented by exactly 1 | 12 → 13 | 8 → 9 | ✅ both exactly +1 |
| `state` still `OPEN` | `OPEN` | `OPEN` | ✅ neither closed |
| Label list still empty | `[]` | `[]` | ✅ zero labels on either issue |
| New comment author | `henols` (the authenticated `gh` account posting on the operator's behalf) | `henols` | recorded |

**D-13 explicitly honored: `gh issue close` was never run, on either issue, at any point in this
plan.**

## 5. Release attribute checks — nothing else touched

```
$ gh release view 3.0.0b14 --repo henols/firestarter --json isPrerelease,assets -q '{p:.isPrerelease,n:(.assets|length),names:[.assets[].name]}'
{"n":3,"names":["firestarter_leonardo.hex","firestarter_uno.hex","firestarter_uno328pb.hex"],"p":true}
$ gh release view 3.0.0b14 --repo henols/firestarter_app --json isPrerelease,assets -q '{p:.isPrerelease,n:(.assets|length)}'
{"n":0,"p":true}
```

Both prereleases still `isPrerelease: true`; firmware still carries exactly its three `.hex`
assets; app still carries zero assets (expected — PyPI is its sole distribution channel, per C-7).
No flag beyond `--notes-file` was ever passed to `gh release edit` — `--prerelease`, `--latest`,
`--draft`, and `--tag` were never touched.

```
$ gh release list --repo henols/firestarter --limit 20 | grep -c '3.0.0b12'
1
$ gh release list --repo henols/firestarter_app --limit 20 | grep -c '3.0.0b12'
1
```

`3.0.0b12` remains present and unmodified in both repos' release lists. Nothing was deleted.

## 6. The negative flag list — every forbidden flag confirmed absent from every call's argv

The four argv strings recorded in §3's table are the literal, complete commands executed —
copy-pasted, not paraphrased. Auditing them against the plan's forbidden-flag list:

| Forbidden flag | Present in any of the 4 calls? |
|---|---|
| `--label` / `--add-label` / `-l` | **No** |
| `--assignee` / `-a` | **No** |
| `--milestone` / `-m` | **No** |
| `--project` / `-p` | **No** |
| `--web` / `-w` | **No** |
| `--editor` / `-e` | **No** |
| `--edit-last` / `--delete-last` | **No** |
| `--notes` (inline string form, release edit) | **No** — `--notes-file` used exclusively |
| `--body` (inline string form, issue comment) | **No** — `--body-file` used exclusively |
| Heredoc / shell-piped body construction | **No** — every body/notes argument is a literal committed file path |
| `gh issue close` | **No** — never invoked, on either issue |
| `gh auth token` | **No** — never invoked at any point in this plan |

Every call used list-form argv with an explicit `--repo`, and either `--notes-file` or
`--body-file` pointing at the committed path. No secret value of any kind appears anywhere in this
artifact, in any commit message, or in any narration produced by this plan.

## 7. The seven-constraint satisfaction ledger (plus the observed-tag rule)

Per `122-DECISION.md`'s "accepted sequence" (§"The accepted sequence, each step naming its owning
plan and the CONTEXT constraint it satisfies") and `122-12-PLAN.md`'s objective, every CONTEXT
sequencing constraint is now satisfied and provable in one place:

| Constraint | What it requires | Owning plan | Evidence |
|---|---|---|---|
| **1** | The CLOSE-03 decision recorded and committed, preceding any push | `122-02` (`122-DECISION.md`) | `122-DECISION.md` committed `d5c49d4` at `2026-07-30T13:03:38Z`, strictly before both outbound merge commits (`b9bb6b7` @ 14:24:48Z firmware, `0adfb4f` @ 14:30:00Z app) — table in `122-CUT.md` §13 |
| **2** | The full non-regression sweep runs on the merged tree, before the outbound merge | `122-04` (`122-NONREGRESSION.md`) | Eleven-row sweep (nine cross-repo gate rows + both full suites + CLOSE-01's four mechanisms) proven on `firestarter_app@4001396` / `firestarter@953f748` — the exact tree wave 6 pushed, not an earlier commit |
| **3** | Both distribution channels verified publicly live, before any comment is posted | `122-08` (`122-CHANNELS.md`) | PyPI (JSON API + clean-env `pip index versions --pre` + `pip download --no-deps`) and the firmware GitHub prerelease (`isPrerelease=true`, 3 named `.hex` assets) both independently `VERIFIED`, committed before 122-11/122-12 ran; §7 of `122-CHANNELS.md` confirms zero comments posted at verification time |
| **4** | The D-16 blocking operator wording review happens before any comment or release body reaches GitHub | `122-11` (`122-11-SUMMARY.md`) | Operator's verbatim verdict "Approve — accept the C-5 correction," recorded 2026-07-30, zero content edits made, five artifacts frozen by blob SHA immediately after — before this plan's Task 1 made anything public |
| **5** | The ledger (`122-LEDGER.md`) and the PROJECT.md EIGHTH CORRECTION precede all four outward-facing artifacts as the single source of permitted wording | `122-05` / `122-06` | `122-LEDGER.md` committed `79be6f0`; the EIGHTH CORRECTION block landed in `122-06` before `122-09`/`122-10` drafted the four artifacts against it; the default five-target claim scanner (`check_permitted_claims.py`) reproduced green against all five files as late as `122-11`'s final run |
| **6** | The four CLOSE-01 mechanisms hold on the merged tree specifically (shared evidence with constraint 2) | `122-04` (`122-NONREGRESSION.md`) | Same eleven-row sweep — zero chips changed `support_status`, the 84-chip `algorithm == 13` count unchanged, proven on the merged tree by three existing mechanisms plus one independent second measurement path |
| **7** | The PyPI publish is one explicit manual `workflow_dispatch`, never a side effect of the merge | `122-08` | `gh workflow run publish.yml --repo henols/firestarter_app -f tag=3.0.0b14`, run `30555530238`, `workflow_dispatch` trigger, conclusion `success` — tag input read from `122-CUT.md` §2, not typed from expectation |
| **Observed-tag rule (A3)** | The cut tag is *derived* by CI, never *executed* by any command in this phase — every downstream step reads the observed value | `122-07` (`122-CUT.md`) | Both repos' observed tags read from `122-CUT.md` §1/§2 (`3.0.0b14` == `3.0.0b14`) at the top of this plan's execution, before either `gh release edit` call — never typed as a literal derived independently |

**This plan's own contribution to the sequence** is step 8 of `122-DECISION.md`'s accepted
sequence: "The two `gh issue comment` calls on `henols/firestarter_prom` #11 and #12" plus the
two `gh release edit` calls that make the sequence's step-6-adjacent release bodies non-empty. All
eight steps of the accepted sequence are now complete.

## 8. What this plan deliberately did not do

- No release deleted, edited beyond its body, or created.
- No `v1.22` tag created in either sub-repo (D-07); no meta gitlink bump — `firestarter` /
  `firestarter_app` gitlinks remain unstaged drift only, exactly as `122-CUT.md` §10 recorded them.
- No push to `beta` or any branch in either sub-repo.
- No PyPI action of any kind (already done, constraint 7, in `122-08`).
- No `.github/` file touched.
- No `git stash`, no `--force` git operation.
- No secret value echoed, logged, or pasted into any artifact, commit message, or narration; `gh
  auth token` was never run.

---
*Phase: 122-close-honesty-ledger-community-ask-release-decision*
*Plan: 12*
*Completed: 2026-07-30*
