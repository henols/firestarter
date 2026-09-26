---
phase: 167
slug: wiki-bootstrap-in-repo-source-sync-drift-check
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-30
---

# Phase 167 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `167-RESEARCH.md` § Validation Architecture. The per-task map below is filled by the planner; the rest is settled.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | **None exists in the meta repo.** Recommended (research-settled): `tools/wiki/selftest.sh` — bash fixture driver, real git, exit-code assertions. **No pytest** — cost priced and rejected in RESEARCH.md § Discretion Areas — Settled. |
| **Config file** | none — Wave 0 creates the driver, not a framework |
| **Quick run command** | `bash tools/wiki/selftest.sh` |
| **Full suite command** | `bash tools/wiki/selftest.sh && python3 tools/wiki/wiki.py check` |
| **Estimated runtime** | ~2 s (prototype equivalent measured < 2 s this session) |

---

## Sampling Rate

- **After every task commit:** Run `bash tools/wiki/selftest.sh`
- **After every plan wave:** Run `bash tools/wiki/selftest.sh && python3 tools/wiki/wiki.py check`
- **Before `/gsd-verify-work`:** Full suite green, all 11 negative cases carrying a captured red run, criterion 6 API read-back done
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

*Filled by the planner. Every row resolves to an automated command from the Requirement Map below, or appears in Manual-Only Verifications with a reason.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 167-01-01 | 01 | 1 | WIKI-04 | T-167-09 | The test driver's own failure branch is reachable and has been observed | unit | `bash tools/wiki/selftest.sh` | ❌ W0 | ⬜ pending |
| 167-01-02 | 01 | 1 | WIKI-04 | T-167-06 | Stale-sidebar and determinism cases exist and are red before the capability | unit | `bash tools/wiki/selftest.sh` | ❌ W0 | ⬜ pending |
| 167-01-03 | 01 | 1 | WIKI-04 | T-167-06 | `sidebar --check` returns before any write — a checker cannot repair what it checks | unit | `bash tools/wiki/selftest.sh` | ❌ W0 | ⬜ pending |
| 167-02-01 | 02 | 2 | WIKI-05 | T-167-06 | The five reachability/legality cases are red before the walker exists | unit | `bash tools/wiki/selftest.sh` | ❌ W0 | ⬜ pending |
| 167-02-02 | 02 | 2 | WIKI-05 | T-167-01, T-167-10, T-167-11 | Names validated before use; fenced code skipped; case-sensitive resolution | unit | `bash tools/wiki/selftest.sh` | ❌ W0 | ⬜ pending |
| 167-02-03 | 02 | 2 | WIKI-04 | T-167-06 | Aggregator runs both legs, writes nothing, and the orphan leg is proved load-bearing | unit | `bash tools/wiki/selftest.sh` | ❌ W0 | ⬜ pending |
| 167-03-01 | 03 | 3 | WIKI-01, WIKI-02, WIKI-03, WIKI-04 | T-167-12 | The five git cases are red before `publish` exists; fixtures only, no live remote | integration | `bash tools/wiki/selftest.sh` | ❌ W0 | ⬜ pending |
| 167-03-02 | 03 | 3 | WIKI-01, WIKI-02, WIKI-03, WIKI-04 | T-167-01, T-167-02, T-167-03, T-167-07, T-167-12 | Offline gate before remote; wipe guard; `master` assertion; no force, no `allow-empty` | integration | `bash tools/wiki/selftest.sh` | ❌ W0 | ⬜ pending |
| 167-03-03 | 03 | 3 | WIKI-02, WIKI-04 | T-167-06 | The mirror wipe is load-bearing, proved by a localised copy-over mutation | integration | `bash tools/wiki/selftest.sh` | ❌ W0 | ⬜ pending |
| 167-04-01 | 04 | 3 | WIKI-05 | T-167-13, T-167-14, T-167-15 | No credential or planning vocabulary published; future pages named, never linked | unit | `python3 tools/wiki/wiki.py links` | ❌ W0 | ⬜ pending |
| 167-04-02 | 04 | 3 | WIKI-04, WIKI-05 | T-167-13 | Committed generated sidebar is byte-stable over the real tree and banner-free | unit | `python3 tools/wiki/wiki.py check` | ❌ W0 | ⬜ pending |
| 167-04-03 | 04 | 3 | WIKI-02 | T-167-16 | The provenance table is not a registry — no tool reads it | unit | `test -f .planning/v1.35/MIGRATION-TABLE.md && python3 tools/wiki/wiki.py check` | ❌ W0 | ⬜ pending |
| 167-05-01 | 05 | 4 | WIKI-04, WIKI-05 | T-167-04, T-167-05, T-167-08, T-167-17 | `contents: read`, `pull_request` not `pull_request_target`, offline only, no fail-open | integration | `python3 tools/wiki/wiki.py check && bash tools/wiki/selftest.sh` | ❌ W0 | ⬜ pending |
| 167-05-02 | 05 | 4 | WIKI-04 | — | Documents of record stay true; scoped edits only | smoke | `grep -q 'tools/wiki' CLAUDE.md && grep -q 'wiki-check.yml' .planning/codebase/STRUCTURE.md` | ✓ runs today | ⬜ pending |
| 167-05-03 | 05 | 4 | WIKI-06 | T-167-18 | Read-back only; no setting-mutating API method permitted | smoke | `test "$(gh api repos/henols/firestarter --jq .has_wiki)" = "false"` (×3 repos) | ✓ runs today | ⬜ pending |
| 167-06-01 | 06 | 5 | WIKI-01 | T-167-21 | The operator gate is reported, never worked around | **manual, operator-gated** | `git ls-remote https://github.com/henols/firestarter_prom.wiki.git refs/heads/master` | ❌ blocked on operator | ⬜ pending |
| 167-06-02 | 06 | 5 | WIKI-01, WIKI-02, WIKI-03, WIKI-04 | T-167-03, T-167-12 | Live drift observed red before green; no credential in any capture | **manual + integration** | `python3 tools/wiki/wiki.py publish --require-wiki` | ❌ blocked on operator | ⬜ pending |
| 167-06-03 | 06 | 5 | WIKI-03, WIKI-04 | T-167-03, T-167-04, T-167-07, T-167-17, T-167-19, T-167-20 | `contents: write` on the publish job only; one token variable; remote never logged; A1 recorded unproven | smoke | `grep -q 'contents: write' .github/workflows/wiki-publish.yml && python3 tools/wiki/wiki.py check` | ❌ blocked on operator | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Requirement Map (research-settled)

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| WIKI-01 | Wiki remote absence reported, not worked around (exit 2, names the operator action) | unit (fixture) | `selftest.sh` → `wiki_absent_exit_2` | ❌ W0 |
| WIKI-01 | Wiki exists, clonable, Home lists every page | **manual, operator-gated** | `git ls-remote …firestarter_prom.wiki.git` then `wiki.py links` | ❌ blocked on operator |
| WIKI-02 | In-repo source overwrites a wiki-side edit | integration (fixture) | `selftest.sh` → `hand_edit_overwritten` | ❌ W0 |
| WIKI-02 | Same, against the real wiki | **manual, gated** | `wiki.py publish --push` after a deliberate web-UI edit | ❌ blocked |
| WIKI-03 | One command publishes | integration (fixture) | `wiki.py publish --push --wiki-remote <fixture>` | ❌ W0 |
| WIKI-03 | Second run creates no commit — `HEAD` unchanged | integration (fixture) | `selftest.sh` → `idempotent_head_unchanged` | ❌ W0 |
| WIKI-04 | Drift → non-zero exit, diff printed | integration (fixture) | `selftest.sh` → `drift_detected_exit_1` | ❌ W0 |
| WIKI-04 | Deletion mirrors (wiki is a true mirror) | integration (fixture) | `selftest.sh` → `deleted_page_removed` | ❌ W0 |
| WIKI-04 | Stale committed `_Sidebar.md` → non-zero | unit | `selftest.sh` → `stale_sidebar_exit_1` | ❌ W0 |
| WIKI-04 | Sidebar generation byte-stable across two runs | unit | `selftest.sh` → `sidebar_deterministic` | ❌ W0 |
| WIKI-05 | Orphan page → non-zero, **only Home links count as evidence** | unit | `selftest.sh` → `orphan_exit_1`, `sidebar_link_is_not_evidence` | ❌ W0 |
| WIKI-05 | Broken internal link → non-zero | unit | `selftest.sh` → `broken_link_exit_1` | ❌ W0 |
| WIKI-05 | `.md`-suffixed internal link → non-zero | unit | `selftest.sh` → `md_suffix_link_exit_1` | ❌ W0 |
| WIKI-05 | Illegal page filename (`\ / : * ? " < > \|`) → non-zero | unit | `selftest.sh` → `illegal_filename_exit_1` | ❌ W0 |
| WIKI-06 | `has_wiki` false/false/true, read from the API | smoke | `for r in firestarter firestarter_app firestarter_prom; do gh api repos/henols/$r --jq .has_wiki; done` | ✓ runs today |

---

## Negative Cases That Must Be OBSERVED RED

The phase's central evidentiary requirement — criteria 2, 4 and 5 each demand a demonstrated failure, and RESEARCH.md § Pitfall 1 documents this repository shipping assertions that could never fail (`tools/catalog/sync_to_subrepos.sh:88-90` and `:100-102` run `diff -q "$X" "$X"`).

| # | Case | Mutation | Expected |
|---|------|----------|----------|
| 1 | `drift_detected_exit_1` | mutate the fixture wiki | dry-run exits 1 |
| 2 | `hand_edit_overwritten` | edit fixture wiki, republish | content equals source |
| 3 | `idempotent_head_unchanged` | push twice, no source change | `rev-parse` equal |
| 4 | `deleted_page_removed` | delete a source page | wiki page gone |
| 5 | `orphan_exit_1` | page absent from `Home.md` | exit 1 |
| 6 | `sidebar_link_is_not_evidence` | page linked **only** from generated `_Sidebar.md` | still exit 1 — *this is the case that proves criterion 5 is not a tautology* |
| 7 | `broken_link_exit_1` | `[x](No-Such-Page)` | exit 1 |
| 8 | `md_suffix_link_exit_1` | `[x](Home.md)` | exit 1 |
| 9 | `illegal_filename_exit_1` | filename containing `:` | exit 1 |
| 10 | `stale_sidebar_exit_1` | add a page, do not regenerate | exit 1 |
| 11 | `wiki_absent_exit_2` | `--wiki-remote` at a nonexistent path | exit **2** (distinct from 1); message names WIKI-01 + the operator URL |

**A case whose red state was never captured counts as unproven.** Each must appear in a plan with its mutation, expected exit code, and a captured run showing red *before* green.

---

## Wave 0 Requirements

- [ ] `tools/wiki/wiki.py` — single entry point; `--wiki-remote` parameterisation is a Wave 0 requirement, not a later refinement, because nothing else is testable without it
- [ ] `tools/wiki/selftest.sh` — fixture driver + the 11 cases
- [ ] `wiki/Home.md`, `wiki/How-This-Wiki-Is-Published.md` (D-12), `wiki/_Sidebar.md` (generated, committed per D-10)
- [ ] `.planning/v1.35/MIGRATION-TABLE.md` — D-04 shell, with a rendered-title column (RESEARCH.md § Pitfall 4)
- [ ] `.github/workflows/wiki-check.yml` — offline legs only
- [ ] Framework install: **none** — this is the point of the harness recommendation

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Wiki repo exists and is clonable | WIKI-01 | GitHub creates `<repo>.wiki.git` only on the first web-UI page save. No REST endpoint; push-to-create returns `Repository not found` (re-verified 2026-08-30). **Operator-only.** | Operator saves any page at `https://github.com/henols/firestarter_prom/wiki`, then `git ls-remote https://github.com/henols/firestarter_prom.wiki.git` |
| Live hand-edit overwrite | WIKI-02 | Requires the real wiki | Edit a page in the web UI, run `wiki.py publish --push`, confirm the in-repo content won |
| Live idempotence | WIKI-03 | Requires the real wiki | Two consecutive `--push` runs, compare remote `HEAD` |
| Live drift detection | WIKI-04 | Requires the real wiki | Diverge the wiki, run the check, observe non-zero |
| `master` is the branch that makes pages live | — | Only observable against a real wiki | Confirm pushed pages render after publish |
| `_Sidebar.md` renders as the sidebar | WIKI-05 | GitHub-side rendering | Visual confirmation post-publish |
| Rendered page titles match intent | WIKI-05 | GitHub-side rendering | Compare rendered titles to the MIGRATION-TABLE rendered-title column |
| CI push authorization (`GITHUB_TOKEN` vs PAT) | WIKI-03 | Unprovable until the wiki exists — Assumption A1 | First live CI publish run is the measurement; do not pre-write "verified" |

**Blocked-on-operator work is recorded, not worked around.** Criterion 1 and the live halves of criteria 2/3/4 remain outstanding until the operator acts; the phase must close with WIKI-01 explicitly open rather than claimed.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — every one of the 18 tasks carries an `<automated>` command
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references — plan 167-01 creates `selftest.sh` and `wiki.py`; plan 167-04 creates the `wiki/` tree
- [x] No watch-mode flags
- [x] Feedback latency < 5s — `selftest.sh` prototype ran in under 2 s
- [x] All 11 negative cases carry a captured red run — plan 167-01 tasks 2-3 (2 cases), plan 167-02 tasks 1-2 (5 cases), plan 167-03 tasks 1-2 (5 cases, of which `wiki_absent_exit_2` is the 11th); `sidebar_deterministic` is a 12th case carried as a byte-stability assertion
- [x] `nyquist_compliant: true` set in frontmatter

**Additional evidence beyond the 11 cases** — three localised mutation runs, each captured in its
plan's SUMMARY, proving the assertions are attributable rather than merely reachable:
plan 167-01 `Harness negative control`; plan 167-02 `Negative control: check_orphans neutered`;
plan 167-03 `Negative control: mirror wipe replaced by copy-over`.

**Approval:** planned 2026-08-30
