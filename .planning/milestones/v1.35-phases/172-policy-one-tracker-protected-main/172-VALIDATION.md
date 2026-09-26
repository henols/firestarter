---
phase: "172"
slug: "policy-one-tracker-protected-main"
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-01"
---

# Phase 172 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — this phase writes no product code. Validation is assertion scripts in `<automated>` verify blocks plus the three existing `tools/wiki/` checkers, `check-jsonschema`, and `gh api` read-backs |
| **Config file** | none |
| **Quick run command** | `python3 /workspaces/tools/wiki/wiki.py links --source-dir <wiki-clone>` |
| **Full suite command** | the three-checker recipe below, against a fresh wiki clone plus fresh `beta` clones of both sub-repos |
| **Estimated runtime** | ~30 seconds (dominated by three shallow clones) |

**The full suite, exactly as it must be run to mirror a *fixed* CI:**

```bash
D=$(mktemp -d) && git clone --depth 1 https://github.com/henols/firestarter_prom.wiki.git "$D/wiki-clone" \
 && git clone --depth 1 -b beta https://github.com/henols/firestarter.git "$D/firestarter" \
 && git clone --depth 1 -b beta https://github.com/henols/firestarter_app.git "$D/firestarter_app" \
 && python3 /workspaces/tools/wiki/wiki.py links --source-dir "$D/wiki-clone" \
 && python3 /workspaces/tools/wiki/honest02_truth.py --wiki-dir "$D/wiki-clone" --db "$D/firestarter_app/firestarter/data/chip_database.json" --allowlist /workspaces/tools/wiki/claim-allowlist.json \
 && python3 /workspaces/tools/wiki/dispatch_mirror.py --app-dir "$D/firestarter_app" --fw-dir "$D/firestarter"
```

All three legs are green under this recipe (measured 2026-09-01). It deliberately does **not** pass `--wiki-dir` to `dispatch_mirror.py`, and deliberately uses `beta` rather than `main` or the local working trees. **The committed `wiki-check.yml` does both of those things wrongly** — see Wave 0.

---

## Sampling Rate

- **After every task commit:** the single assertion for that task's artifact — `wiki.py links` for the wiki task, `check-jsonschema` for a template task, the three-way read-back leg for a ruleset task.
- **After every plan wave:** the full three-checker recipe plus the LEGACY-01 grep leg.
- **Before `/gsd-verify-work`:** full recipe green against a **fresh** wiki clone and **fresh** `beta` clones — not the local working trees — plus three-way ruleset equality.
- **Max feedback latency:** 30 seconds.

---

## Per-Task Verification Map

Task IDs are provisional until the planner fixes plan/wave numbering; the requirement, test type and command columns are not.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 172-0W-01 | W0 | 0 | D-14 precondition | — | N/A | integration | drop `--wiki-dir wiki-clone` from the dispatch-mirror step; full recipe exits 0 | ❌ W0 | ⬜ pending |
| 172-0W-02 | W0 | 0 | D-14 precondition | — | N/A | integration | resolver lands scheduled runs on `beta`; all three legs green | ❌ W0 | ⬜ pending |
| 172-0W-03 | W0 | 0 | D-10 | T-172-01 | one-way delete is recoverable-by-record | unit | `test -s evidence/172-*-ruleset-4998759-pre-delete.json` **&&** `jq -e '.id == 4998759'` on it | ❌ W0 | ⬜ pending |
| 172-xx-01 | — | 1 | POLICY-01 | — | policy states only what is configured | integration | fresh wiki clone carries `Contributing.md` with all three statements; `wiki.py links` green | ✅ | ⬜ pending |
| 172-xx-02 | — | 1 | POLICY-01 | — | N/A | unit | three READMEs each link and do not restate; `.github/CONTRIBUTING.md` present in all three repos | ✅ | ⬜ pending |
| 172-xx-03 | — | 1 | POLICY-02 | — | N/A | unit | `check-jsonschema --builtin-schema vendor.github-issue-forms .github/ISSUE_TEMPLATE/*.yml` | ❌ W0 | ⬜ pending |
| 172-xx-04 | — | 1 | POLICY-02 / D-06 | — | hand-filed reports cannot masquerade as machine reports | unit | `! grep -q '\[dev test\]'` in the `dev test` template | ❌ W0 | ⬜ pending |
| 172-xx-05 | — | 1 | POLICY-02 / D-07 | — | N/A | unit | `config.yml` sets `blank_issues_enabled: true` | ❌ W0 | ⬜ pending |
| 172-xx-06 | — | 2 | LEGACY-01 / D-13 | — | N/A | unit | grep leg over `meta/ firestarter/ firestarter_app/ wiki-clone/`, excluding `.planning/` and `.git/`, exits 0 | ✅ | ⬜ pending |
| 172-xx-07 | — | 2 | LEGACY-01 / D-14 | — | the guard is not vacuous | unit | plant `henols/firestarter/issues` → leg exits 1; remove → exits 0 | ✅ | ⬜ pending |
| 172-xx-08 | — | 3 | POLICY-03 | T-172-01 | protection is real, not merely present | integration | three-way read-back: `enforcement == "active"`, four clauses present, bypass list is exactly Actions, equality modulo `id`/`node_id`/`created_at`/`updated_at`/`_links`/`source` | ✅ | ⬜ pending |
| 172-xx-09 | — | 4 | POLICY-02 / LEGACY-01 | — | N/A | integration | after merge: `gh api .../contents/.github/ISSUE_TEMPLATE?ref=main`; `gh workflow list` includes `wiki-check.yml` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `.github/workflows/wiki-check.yml` — remove `--wiki-dir wiki-clone` from the dispatch-mirror step. **`dispatch_mirror.py` declares only `--app-dir` and `--fw-dir`** (`tools/wiki/dispatch_mirror.py:157-158`), so the step exits 2 unconditionally today. Blocks D-14.
- [ ] `.github/workflows/wiki-check.yml` — the ref resolver must land scheduled runs on `beta`. On a schedule `github.ref_name` is the workflow's own default branch, which **exists** in both sub-repos, so the resolver keeps it instead of falling back to `beta` — contradicting its own inline comment. Against `main`, `firestarter_app` has no `firestarter/data/chip_database.json` and `firestarter` has no `PROTOCOLS.md`, so the other two legs exit 2 as well. Blocks D-14.
- [ ] `.github/workflows/wiki-check.yml` — add the LEGACY-01 grep leg (D-13/D-15). Must be written as `if grep …; then exit 1; fi`, **not** `! grep … && echo …` — the latter fails open under the runner's `bash -e`. No comments.
- [ ] `firestarter_prom/.github/ISSUE_TEMPLATE/` — two issue forms (`.yml`), one Markdown `dev test` template, and `config.yml`. Covers POLICY-02.
- [ ] `evidence/172-*-ruleset-4998759-pre-delete.json` — the full JSON of ruleset `4998759`, captured **before** the DELETE. Covers D-10, the phase's only one-way decision.
- [ ] A local issue-form validator — `check-jsonschema --builtin-schema vendor.github-issue-forms` (verified this session to reject `type: texarea` against the documented enum), or the documented inline key/enum fallback.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The Actions bypass actually covers `git-auto-commit-action`'s default-`GITHUB_TOKEN` push | POLICY-03 / D-09 | GitHub documents Apps as bypass actors and documents `GITHUB_TOKEN` as an App installation token, but never connects the two; community reports run the other way. Not settleable from documentation. **Highest blast radius in the phase** — if wrong, the next stable release breaks in both sub-repos. | Falsify with a throwaway-repo probe (create repo, add the same ruleset, run a workflow that pushes with the default token, observe) **before** the one-way DELETE of `4998759`. Gate as a human checkpoint. |
| `/issues/new?title=&body=` still prefills once templates exist | POLICY-02 / D-07 | Only observable from a logged-in browser against the live default branch, which means after the prom PR merges. | Open the URL `submit.py:283` builds and confirm the title and body arrive prefilled rather than a redirect to `/issues/new/choose`. A negative result is **filed, not fixed** — product-code changes are out of scope. |
| Whether `firestarter`'s `build.yml` `paths-ignore: '**.md'` covers a dot-directory path | POLICY-02 / D-08 | `build.yml`'s `paths-ignore` lacks `.github/**` (unlike the app's `release.yml`), so whether the `.github`-only merge cuts a release turns on one glob question. | Free to answer on the PR itself: read the PR's own check list before merging. Two named fallbacks if it would fire — edit `build.yml`, or move the file. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] Every `<automated>` block contains literal `&&`, never an HTML entity
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
