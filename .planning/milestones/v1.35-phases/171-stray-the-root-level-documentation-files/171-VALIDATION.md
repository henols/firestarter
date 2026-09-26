---
phase: 171
slug: stray-the-root-level-documentation-files
status: draft
nyquist_compliant: false
wave_0_complete: true
created: 2026-09-01
---

# Phase 171 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `171-RESEARCH.md` § *Validation Architecture* (lines 1234–1305).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `tools/wiki/wiki.py links` (stdlib argparse CLI, exit-code contract 0/1/2) as the primary oracle; pytest 8.x for the app-health leg |
| **Config file** | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `addopts = "-ra -q"`) |
| **Quick run command** | `python3 /workspaces/tools/wiki/wiki.py links --source-dir <wiki-clone>` |
| **Full suite command** | `cd /workspaces/firestarter_app && <venv311>/bin/python3 -m pytest tests/ -o addopts="" -q` |
| **Estimated runtime** | ~1 s (wiki oracle) · ~30–60 s (app suite) |

**⚠ CI reality — no CI covers this phase.** `.github/workflows/wiki-check.yml` is absent from
`origin/main` (the default branch), so GitHub never registered its `schedule` or
`workflow_dispatch`; `gh workflow list --all` returns only `Catalog sync check`. The app's
`ci.yml` skips `**.md`-only commits. **Every check below must be run locally and its output
recorded as evidence** — there is no safety net that catches a miss later.

---

## Sampling Rate

- **After every task commit:** `python3 tools/wiki/wiki.py links --source-dir <clone>` (wiki tasks) ·
  `git show --stat --format="" HEAD` (deletion tasks)
- **After every plan wave:** fresh-clone wiki verification + clean-tree sdist manifest diff
- **Before `/gsd-verify-work`:** every automated row below green, plus the py3.11 app suite
- **Max feedback latency:** ~60 s

---

## Per-Task Verification Map

Task IDs are assigned by the planner. Every automated row below MUST be claimed by at least one
task's `<verify><automated>` block; a row left unclaimed is a Nyquist gap.

| Ref | Requirement | Behaviour to prove | Test Type | Automated Command (cwd shown) | Runs against | Status |
|-----|-------------|--------------------|-----------|-------------------------------|--------------|--------|
| V-01 | LEGACY-04 | `things.md` gone from the app repo root | integration | `cd /workspaces/firestarter_app && ! test -e things.md && ! git cat-file -e HEAD:things.md` | this repo | ⬜ pending |
| V-02 | LEGACY-04 | the deletion is committed, not merely unstaged | integration | `cd /workspaces/firestarter_app && git log -1 --diff-filter=D --name-only --format="" HEAD -- things.md \| grep -qx things.md` | this repo | ⬜ pending |
| V-03 | LEGACY-04 | content recoverable at the recorded SHA | integration | `git -C /workspaces/firestarter_app show d56424e1979edf7245cffb9ec3111c0469f5b23f:things.md \| sha256sum \| cut -c1-16` → `637974e9dcab7870` | this repo | ⬜ pending |
| V-04 | LEGACY-05 | `SECURITY.md` gone from the branch tip | integration | `cd /workspaces/firestarter_app && ! test -e SECURITY.md && ! git cat-file -e HEAD:SECURITY.md` | this repo | ⬜ pending |
| V-05 | LEGACY-05 | no replacement policy smuggled in anywhere (D-02) | integration | `cd /workspaces && ! git -C firestarter_app grep -riq "report a vulnerability\|security policy\|responsible disclosure" -- ':(exclude).planning'` | this repo | ⬜ pending |
| V-06 | LEGACY-05 | recoverable at the recorded SHA | integration | `git -C /workspaces/firestarter_app show d56424e1979edf7245cffb9ec3111c0469f5b23f:SECURITY.md \| sha256sum \| cut -c1-16` → `35077cac80e15a8a` | this repo | ⬜ pending |
| V-07 | LEGACY-05 | canonical Phase 69 audit record still exists in meta | integration | `test -f /workspaces/.planning/milestones/v1.12-phases/69-cli-command-surface-robustness-audit/69-SECURITY.md` | this repo | ⬜ pending |
| V-08 | LEGACY-07 | `autocomplete.md` gone from the app repo root | integration | `cd /workspaces/firestarter_app && ! test -e autocomplete.md && ! git cat-file -e HEAD:autocomplete.md` | this repo | ⬜ pending |
| V-09 | LEGACY-07 | recoverable at the recorded SHA | integration | `git -C /workspaces/firestarter_app show d56424e1979edf7245cffb9ec3111c0469f5b23f:autocomplete.md \| sha256sum \| cut -c1-16` → `6e3a0116f2a3759f` | this repo | ⬜ pending |
| V-10 | LEGACY-07 | the page exists on the **live** wiki | integration | `git clone --depth 1 https://github.com/henols/firestarter_prom.wiki.git "$V" && test -f "$V/Shell-Completion.md"` | live wiki | ⬜ pending |
| V-11 | LEGACY-07 | reachable + sidebar-listed + links legal | integration | `python3 /workspaces/tools/wiki/wiki.py links --source-dir "$V"` → rc=0, stdout contains `OK: 10 pages,` and `Shell-Completion -> "Shell Completion"` | live wiki | ⬜ pending |
| V-12 | LEGACY-07 | page shape matches the other nine | integration | `sed -n '3,5p' "$V/Shell-Completion.md" \| tr '\n' '\|'` → `---\|\|# Shell Completion\|` | live wiki | ⬜ pending |
| V-13 | LEGACY-07 | content preserved — four shell sections + pipx + migration note survived | integration | `for s in Bash Zsh Fish PowerShell "pipx Installations" "Migrating from a previous Firestarter"; do grep -qF "### $s" "$V/Shell-Completion.md" \|\| { echo "MISSING: $s"; exit 1; }; done` | live wiki | ⬜ pending |
| V-14 | LEGACY-04/05/07 | nothing anywhere links to the three old paths | integration | the RESEARCH §C.10 sweep; only permitted hit is `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md:637` (historical, no action) | this repo | ⬜ pending |
| V-15 | D-06 | all three MIGRATION-TABLE rows present, SHA cited | integration | `grep -c 'd56424e1979edf7245cffb9ec3111c0469f5b23f' /workspaces/.planning/v1.35/MIGRATION-TABLE.md` → ≥ 8, plus the `Shell-Completion` main-table row grep | this repo | ⬜ pending |
| V-16 | D-06 | the new deletion section does not corrupt `honest01`'s parse | integration | RESEARCH §C.9 `parse_migration_table` snippet → 8 SHA-bearing rows, none a deletion row | this repo | ⬜ pending |
| V-17 | packaging | the sdist manifest is unchanged | integration | RESEARCH §B.7 **clean-tree** before/after `diff` → empty; 173 entries each side | this repo | ⬜ pending |
| V-18 | app health | the suite still passes on the CI Python floor | integration | RESEARCH §B.7 py3.11 route → `N passed`, zero `failed`/`error` | this repo | ⬜ pending |
| V-19 | gitlink | meta records the app's new tip | integration | RESEARCH §D.12 equality assertion → `OK` for both submodules | this repo | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Two oracle traps the planner and executor must not walk into:**

1. **The sdist build must run on a clean tree.** A build in `/workspaces/firestarter_app` emits a
   220-entry sdist that *contains* `autocomplete.md` and `things.md` — setuptools' `manifest_maker`
   re-absorbs the gitignored `firestarter.egg-info/SOURCES.txt`. A `git archive` tree emits 173
   entries with none of them. A working-tree build is a **false positive** (V-17).
2. **`gh api …/community/profile -q .files.security_policy` is a vacuous leg.** It reads the
   *default branch*, where `SECURITY.md` has never existed, so it returns `null` both before and
   after the work. It would pass a plan that did nothing. Do not use it (V-04 is the real oracle).

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* Every oracle already exists and was
exercised during research:

- `tools/wiki/wiki.py links` — present; run 4× including both negative legs (missing sidebar entry
  → rc=1 named error; missing `Home.md` link → rc=1 orphan error).
- `tools/wiki/honest01_claims.py:74` `parse_migration_table` — present, importable.
- Clean-tree sdist route — established by Phase 168's `evidence/migrate03-sdist-doc-delta.txt`.
- py3.11 venv route — established by `evidence/migrate03-py311-suite.txt`.

No test file, fixture or framework install is owed before implementation.

---

## Manual-Only Verifications

These MUST be `checkpoint:human-verify` in the plans, **never** `<automated>` verify legs.

| Behaviour | Requirement | Why Manual | Test Instructions |
|-----------|-------------|------------|-------------------|
| The `git push` to `firestarter_prom.wiki.git` succeeds | LEGACY-07 | State-changing network operation; research verified `admin:true, push:true` and a configured credential helper but deliberately did not exercise the push. Its failure is a hard stop for the phase. | Executor performs the push, then immediately discharges V-10/V-11 against a **fresh** clone — not the working clone. |
| The rendered `Shell-Completion` page looks right on github.com | LEGACY-07 | Markdown rendering, logo image resolution, sidebar placement, and the title reading "Shell Completion" are properties of GitHub's renderer. `wiki.py links` renders nothing and does **not** check page shape — a mis-shaped page passes rc=0. | Operator opens the page, the sidebar, and `Home`; confirms the logo resolves, the title reads "Shell Completion", and the page is listed in the sidebar. Precedent: Phase 168, `ROADMAP.md:236`. |
| `henols/firestarter_app`'s Security tab is empty | LEGACY-05 | The tab derives from the **default branch**. This phase does not merge to `main`, so the property cannot be observed now — and the API already reports `null` today, so recording it as a pass would be vacuous. | Defer the real observation to the milestone merge. Record here only that the branch tip no longer carries the file (V-04). |
| `wiki-check.yml` is not made red by this phase | — | The workflow is not registered with Actions at all (absent from the default branch); there is no run to inspect. Putting it on the default branch is Phase 172/173 territory. | No action. Recorded so a future red run is not misattributed to Phase 171. |

**Known pre-existing defect, explicitly out of scope:** `.github/workflows/wiki-check.yml:104-107`
passes `--wiki-dir` to `dispatch_mirror.py`, which accepts only `--app-dir` / `--fw-dir`
(`tools/wiki/dispatch_mirror.py:157-158`). That step exits 2 the first time the workflow ever runs.
Introduced by `4b14a5a2`. **Do not fix it in this phase** — record it only.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or are declared manual-only above
- [ ] Every V-01…V-19 row is claimed by at least one task
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references — *N/A, none missing*
- [ ] No watch-mode flags
- [ ] Neither oracle trap (working-tree sdist, `community/profile`) appears in any `<automated>` leg
- [ ] Feedback latency < 60 s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
