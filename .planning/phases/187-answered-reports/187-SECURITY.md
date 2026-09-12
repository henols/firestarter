---
phase: "187"
slug: "answered-reports"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
block_on: high
register_authored_at_plan_time: true
created: "2026-09-12"
---

# Phase 187 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

This phase's register was authored at plan time — all twelve `187-*-PLAN.md` files carry a
`<threat_model>` block — so this audit **verifies that the declared mitigations hold**; it does
not scan for new threats (retroactive-STRIDE was not required).

**Audit depth.** ASVS L1 (grep-depth) is what the configuration requires. The `Evidence` column
below distinguishes two grades, because a record about honesty should not blur them:

- **LIVE** — re-measured during this audit against the GitHub API, the live git remotes, or the
  files on disk. Not read from any SUMMARY's claim about itself.
- **L1** — classified at grep depth from the plan's own automated verify legs and its SUMMARY,
  which is the depth ASVS L1 calls for and no more.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| working tree → public `beta` of `henols/firestarter_prom` | Everything committed becomes world-readable at merge; no redaction step exists downstream | The whole `.planning/` tree, including operator notes |
| app milestone branch → public `beta` → PyPI | The least reversible act in the phase; a published PyPI version can never be unpublished or its number reused | Python package `firestarter` |
| firmware milestone branch → public `beta` → GitHub Releases | Publishes `.hex` binaries a reporter will flash onto their own hardware | Compiled firmware images |
| approved body on disk → public issue comment | The moment of publication; delivered by email to every watcher, editable but never un-seen | Reply prose, version claims, permalinks |
| operator's approval → the agent's act | The only thing between a drafted body and a public statement; auto-mode is the one way it can be bypassed | Approval decision |
| a verdict label → a reporter's conclusion | `fix:released` on an unfixed defect communicates a closure no sentence ever claims | Issue labels |
| local clone → GitHub contents API | A local `git show` proves only what the clone holds; only the API at a pinned ref proves what a reporter's browser sees | Permalink targets |
| this phase's PRs → the stale external contribution `firestarter#54` | A third-party PR shares the repository and the `beta` base ref; an over-broad action could close or merge it | Someone else's contribution |
| GSD tooling → `.planning/` config | `loop render-hooks` and `query init.verify-work` mutate `config.json` with no author; an unreviewed commit publishes that mutation | `planning.sub_repos` |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status | Evidence |
|-----------|----------|-----------|----------|-------------|------------|--------|----------|
| T-187-01 | Information Disclosure | `anything.txt`, `tmp/`, `datasheets/*.pdf` | high | mitigate | Explicit-path staging; `git add -A` and `git clean -Xdf` forbidden by name | closed | LIVE — all four scratch paths `git ls-files`-untracked in both repos |
| T-187-02 | Tampering | `.planning/config.json` `planning.sub_repos` | high | mitigate | Revert with `git checkout --`; assert empty diff and both pruned entries present | closed | LIVE — clean diff; all four entries present. See standing caveat below |
| T-187-03 | Repudiation | `ROADMAP.md`, `REQUIREMENTS.md` | medium | mitigate | AMENDED-clause form keeps original wording; correction auditable, not a silent rewrite | closed | L1 |
| T-187-04 | Tampering | `.planning/milestones/` historical citations | medium | mitigate | Prohibition in `must_haves` plus a `git status --porcelain` leg | closed | LIVE — `git status --porcelain -- .planning/milestones` empty |
| T-187-05 | Information Disclosure | `.planning/state.json`, v1.34 bench `.bin` | medium | mitigate | `git clean -Xdf` forbidden by name; removal by explicit path only | closed | L1 |
| T-187-06 | Information Disclosure | whole `.planning/` tree at branch tip | high | mitigate | Pre-gate `git status` re-run; verbatim statement to operator of what becomes public | closed | L1 |
| T-187-07 | Spoofing | permalinks in reply bodies | high | mitigate | Pinned SHA captured only after merge, proven at the API before drafting; pre-merge SHA prohibited | closed | LIVE — both blob links pin `ebd80b53…`; API returns 13552 B and 22340 B; SHA `identical` to `beta` |
| T-187-08 | Tampering | `v1.37` tag creation | high | mitigate | `/gsd-ship` not used; PRs opened directly; tag absence an automated leg | closed | LIVE — 0 `v1.37` tags via `gh api repos/henols/firestarter_prom/tags` |
| T-187-09 | Repudiation | the meta merge itself | high | mitigate | Per-act approval file `APPROVED-FOR-MERGE: meta` as the tracer's `<precondition>` | closed | LIVE — file present, names the operator and the selected option |
| T-187-10 | Tampering | `sub_repos` prune re-introduced between plans | medium | mitigate | Re-check and revert; assert empty diff before the gate | closed | LIVE — see standing caveat below |
| T-187-11 | Denial of Service | published PyPI release | high | mitigate | Blocking-human approval file as `<precondition>`; one-way rating stated in D-01's words | closed | LIVE — `187-03-operator-approval.txt` records the `merge` selection and the one-way statement |
| T-187-12 | Information Disclosure | `MBM27C1001.pdf`, `MX27C4000.pdf` | high | mitigate | Asserted untracked before the PR and after the merge; explicit-path staging | closed | LIVE — both untracked in `firestarter_app` |
| T-187-13 | Spoofing | version named in a reply (app) | high | mitigate | Read from `gh release list` after completion; computing it prohibited | closed | LIVE — `3.0.0b39` ×7 in bodies; pre-cut `3.0.0b38` ×0 |
| T-187-14 | Tampering | `v1.37` tag creation | high | mitigate | Tag absence an automated leg, re-asserted in 187-04 and 187-12 | closed | LIVE — 0 tags, all three repos |
| T-187-15 | Elevation of Privilege | `gh workflow run` manual dispatch | medium | mitigate | Manual dispatch a named prohibition and operator-only; only read-only `gh run list` used | closed | L1 |
| T-187-16 | Denial of Service | published firmware pre-release | high | mitigate | Blocking-human approval file as `<precondition>`; live delta incl. the 52-line deletion shown | closed | LIVE — `187-04-operator-approval.txt` present with harness disclosure |
| T-187-17 | Tampering | `firestarter#54` (third-party PR) | high | mitigate | State/head/base/comment-count captured before and reconciled after; touching it prohibited | closed | LIVE — `#54 OPEN updated=2026-08-22T17:56:22Z comments=0`, three weeks before the window |
| T-187-18 | Spoofing | firmware version named in a reply | high | mitigate | Read from `gh release list`; computing it prohibited | closed | LIVE — `3.0.0b27` ×3; pre-cut `3.0.0b26` ×0 |
| T-187-19 | Denial of Service | short poll timeout acting against a healthy 70-min cut | medium | mitigate | Break only on `status == completed`; no deadline under 90 minutes; timestamped polls | closed | L1 |
| T-187-20 | Tampering | `v1.37` tag across all three repositories | high | mitigate | Tag absence asserted for all three at once, again in 187-12 | closed | LIVE — 0/0/0 |
| T-187-21 | Information Disclosure | leg grepping firmware repo for `beta-release.yml` | medium | mitigate | Assert `beta-build.yml` present and `beta-release.yml` absent before the merge | closed | L1 |
| T-187-22 | Spoofing | permalinks in both bodies | high | mitigate | Resolved at the pinned SHA via the contents API; branch links grep-forbidden | closed | LIVE — zero branch-ref blob links; both resolve |
| T-187-23 | Repudiation | false claim about gh#65 and gh#66 | high | mitigate | Answered state re-measured; string `unanswered` asserted absent from both bodies | closed | L1 |
| T-187-24 | Tampering | a body drifting between draft and post | high | mitigate | One sha256 per body recorded; approval gates bind against it | closed | LIVE — all 5 body hashes match their approval binding |
| T-187-25 | Information Disclosure | a version predicted rather than read | high | mitigate | Version strings grep-matched against line 1 of the cut-version files | closed | LIVE — only read versions appear |
| T-187-26 | Repudiation | implying the `0x05` chip-erase is scheduled | medium | mitigate | Named prohibition; 999.63 stated unbuilt with the boot-block caveat, no timeline | closed | L1 |
| T-187-27 | Repudiation | gh#23's concession scope (invented PASS) | high | mitigate | Live tracker search for a w27e257 PASS; body concedes without naming a run | closed | L1 |
| T-187-28 | Spoofing | one body posted to two issues | high | mitigate | The two bodies' sha256 asserted distinct; each names only its own chip | closed | LIVE — all 5 hashes distinct; posted lengths differ (2822 vs 2776) |
| T-187-29 | Repudiation | implied closure via `fix:released` | high | mitigate | Label prohibited on gh#23/28/31; each body names it and states why it is withheld | closed | LIVE — `fix:released` absent from gh#23/28/31/62; present only on gh#60, where the operator explicitly selected it |
| T-187-30 | Repudiation | a re-run PASS read as proof the write path works | high | mitigate | D-12 caveat positioned at or before the ask in every re-run-asking body | closed | L1 |
| T-187-31 | Spoofing | a predicted version in a re-run instruction | high | mitigate | Both versions grep-matched byte-exactly against the cut-version files | closed | LIVE — see T-187-13/18 |
| T-187-32 | Tampering | adding a report key for the write-shortcut divergence | medium | mitigate | Named prohibition; the folded todo supplies reply material only and stays pending | closed | L1 |
| T-187-33 | Repudiation | posting a body the operator never approved (gh#60) | critical | mitigate | Per-issue approval literal plus sha256 binding as `<precondition>`; read-back after | closed | LIVE — posted body byte-identical to approved file (2272 B); approval committed 15:32:11Z, comment created 15:32:28Z |
| T-187-34 | Tampering | false mismatch from the naive read-back | high | mitigate | Naive `--jq '.body'` diff prohibited; JSON round trip the only permitted check | closed | L1 |
| T-187-35 | Elevation of Privilege | auto-mode approving the gate | critical | mitigate | `gate="blocking-human"`; never-dispatch constraint; operator confirms the mode | closed | LIVE — approval file discloses `auto_advance: false` / `_auto_chain_active: false` |
| T-187-36 | Tampering | collateral acts on issues this gate did not approve | high | mitigate | State and comment-count legs assert the other four unchanged | closed | LIVE — repo-wide sweep since 15:32:19Z returns exactly 5 comments on exactly the 5 approved issues |
| T-187-37 | Spoofing | a close reason the operator did not name | medium | mitigate | Reason flag presented as an explicit assumption, recorded, and compared after | closed | LIVE — gh#60 `stateReason: COMPLETED`, matching the approval |
| T-187-38 | Repudiation | posting a body the operator never approved (gh#62) | critical | mitigate | Approval literal plus sha256 binding; byte-identity read-back | closed | LIVE — byte-identical (3915 B) |
| T-187-39 | Elevation of Privilege | closing gh#62 | high | mitigate | Closing a named prohibition; post-plan state asserted `OPEN` | closed | LIVE — gh#62 `OPEN` |
| T-187-40 | Repudiation | false claim that gh#65/gh#66 are unanswered | high | mitigate | Re-measured; drafted line says open rather than unanswered; drift put to the operator | closed | L1 |
| T-187-41 | Tampering | silent reclassification on an issue that had no labels | high | mitigate | Both candidates and grounds presented with "no change" as an equal option | closed | LIVE — gh#62 carries exactly `cause:firmware`, matching its approval |
| T-187-42 | Tampering | false mismatch from the naive read-back | high | mitigate | Naive form prohibited; only the JSON round trip permitted | closed | L1 |
| T-187-43 | Elevation of Privilege | auto-mode approving the gate | critical | mitigate | `gate="blocking-human"`; explicit mode confirmation | closed | LIVE — disclosed in the approval file |
| T-187-44 | Repudiation | posting a body the operator never approved (gh#23) | critical | mitigate | Approval literal plus sha256 binding; byte-identity read-back | closed | LIVE — byte-identical (3676 B) |
| T-187-45 | Elevation of Privilege | closing gh#23 | critical | mitigate | Unconditional named prohibition; state asserted `OPEN`, re-asserted in 187-12 | closed | LIVE — gh#23 `OPEN` |
| T-187-46 | Tampering | dropping `cause:database` during the label edit | high | mitigate | Only `--add-label` permitted; resulting set reconciled field by field | closed | LIVE — gh#23 set is exactly `dev-test, cause:database, cause:rig, needs:report`, matching the approval |
| T-187-47 | Repudiation | implying a w27e257 run that passed | high | mitigate | Named prohibition, re-surfaced at the gate as an explicit honesty point | closed | L1 |
| T-187-48 | Tampering | false mismatch from the naive read-back | high | mitigate | Only the JSON round trip permitted | closed | L1 |
| T-187-49 | Elevation of Privilege | auto-mode approving the gate | critical | mitigate | `gate="blocking-human"`; explicit mode confirmation | closed | LIVE — disclosed in the approval file |
| T-187-50 | Repudiation | posting a body the operator never approved (gh#28) | critical | mitigate | Approval literal plus sha256 binding; byte-identity read-back | closed | LIVE — byte-identical (2822 B) |
| T-187-51 | Elevation of Privilege | closing gh#28 | critical | mitigate | Unconditional named prohibition; state asserted `OPEN` | closed | LIVE — gh#28 `OPEN` |
| T-187-52 | Repudiation | `fix:released` implying a closure | high | mitigate | Applying it prohibited; absence an automated assertion; body states the withholding | closed | LIVE — absent from gh#28 |
| T-187-53 | Repudiation | a re-run PASS read as proof the write path works | high | mitigate | Caveat positioned at or before the ask; re-shown to the operator | closed | L1 |
| T-187-54 | Tampering | dropping a pre-existing label during the edit | medium | mitigate | Only `--add-label` permitted; set reconciled against the pre-phase capture | closed | LIVE — `dev-test` and `cause:harness` both retained on gh#28 |
| T-187-55 | Elevation of Privilege | auto-mode approving the gate | critical | mitigate | `gate="blocking-human"`; explicit mode confirmation | closed | LIVE — disclosed in the approval file |
| T-187-56 | Repudiation | posting a body the operator never approved (gh#31) | critical | mitigate | Approval literal plus sha256 binding; byte-identity read-back | closed | LIVE — byte-identical (2776 B) |
| T-187-57 | Elevation of Privilege | closing gh#31 | critical | mitigate | Unconditional named prohibition; all three disputed issues re-asserted `OPEN` | closed | LIVE — gh#31 `OPEN` |
| T-187-58 | Repudiation | `fix:released` implying a closure | high | mitigate | Applying it prohibited; absence an automated assertion | closed | LIVE — absent from gh#31 |
| T-187-59 | Tampering | dropping `cause:database` or `cause:harness` | high | mitigate | Only `--add-label` permitted; both asserted present | closed | LIVE — gh#31 carries both |
| T-187-60 | Tampering | false mismatch from the naive read-back | high | mitigate | Only the JSON round trip permitted | closed | L1 |
| T-187-61 | Elevation of Privilege | auto-mode approving the gate | critical | mitigate | `gate="blocking-human"`; explicit mode confirmation | closed | LIVE — disclosed in the approval file |
| T-187-62 | Repudiation | an unapproved public act going unnoticed | high | mitigate | Before/after reconciliation naming every difference; repo-wide collateral sweep | closed | LIVE — exactly 5 comments in the window, all by `henols`, none edited |
| T-187-63 | Elevation of Privilege | a disputed issue found closed | critical | mitigate | All three asserted `OPEN` again after the posting plans asserted it individually | closed | LIVE — gh#23/28/31 all `OPEN` |
| T-187-64 | Tampering | gh#9 modified or unpinned | high | mitigate | Read-only pin and comment verification; created-vs-updated comparison; pin mutation prohibited | closed | LIVE — 1 comment, `createdAt == updatedAt == 2026-09-02T14:50:37Z`, 10 days before the window |
| T-187-65 | Repudiation | filing a backlog item against a locked decision | high | mitigate | Named prohibition plus a `git status` leg over todo and backlog directories | closed | LIVE — `git status --porcelain -- .planning/todos .planning/backlog` empty |
| T-187-66 | Repudiation | restating a measurement known to be wrong | medium | mitigate | Named prohibition on the historical-file count; a count is stated only if re-measured | closed | L1 |
| T-187-67 | Repudiation | a REPLY requirement marked Complete that was not delivered | medium | mitigate | Traceability legs assert seven Complete rows, zero Pending, each carrying a trace | closed | LIVE — 7 Complete / 0 Pending, and all five cited `issuecomment` IDs match the live comment IDs exactly |
| T-187-68 | Information Disclosure | operator scratch tracked at any point in the phase | high | mitigate | Final `git ls-files` leg closing the loop opened in 187-01 | closed | LIVE — all scratch paths untracked |
| T-187-SC | Tampering | npm/pip/cargo installs | low | accept | No plan in this phase runs a package-manager install; there is no install step to gate | closed | Accepted in all 12 plans — see Accepted Risks Log |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` count toward `threats_open`*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

**Counts:** 69 threats total — 68 `mitigate` (all closed), 1 `accept` (`T-187-SC`, declared identically in all twelve plans). 14 of the 68 are `critical`; all 14 are LIVE-verified. `threats_open: 0`.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-187-01 | T-187-SC | Supply chain. No plan in this phase runs `npm`/`pip`/`cargo` install. Plan 187-03 *publishes* a package built from tracked source but installs nothing, so there is no dependency-resolution step to pin or gate. The disposition is declared identically in all twelve plans' threat models. | Henrik Olsson (plan-time disposition, all 12 plans) | 2026-09-12 |

---

## Standing Caveat — not a threat, a live hazard (T-187-02 / T-187-10)

`.planning/config.json` is a covered file of `187-VERIFICATION.md` **and** a GSD-tooling write
target. Re-confirmed during this audit: `gsd-tools query init.verify-work` and
`gsd-tools loop render-hooks` each rewrite it in place, silently dropping the `planning.sub_repos`
entries whose directories are not cloned (`firestarter_app_py32`, `firestarter_py32_ci`). This is
broader than previously recorded — the prune was believed isolated to `loop render-hooks`.

Consequence: running an ordinary GSD verb dirties a covered file, which alone flips the
verification content fingerprint to `stale` with no real drift. The mitigation that held during
the phase still holds — revert with `git checkout -- .planning/config.json` and re-assert the
empty diff — but it must be re-applied after **any** GSD verb run, not only after `render-hooks`.
Committed state at audit time: clean, all four entries present.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-12 | 69 | 69 | 0 | `/gsd-secure-phase 187` (orchestrator, ASVS L1, block_on `high`) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-12
