---
phase: "173"
slug: "close-beta-cut-under-protection-close-procedure-honesty-ledg"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-02"
---

# Phase 173 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | **None.** No pytest/jest suite covers `.planning/`, the `tools/wiki/` checkers, `.planning/config.json`, or the wiki. Verification is by direct command invocation with captured output, exactly as Phases 171–172 did. |
| **Config file** | none — `tools/wiki/` has no `pytest.ini`, `conftest.py` or test directory |
| **Quick run command** | `python3 tools/wiki/<checker>.py --wiki-dir <clone> --migration-table .planning/v1.35/MIGRATION-TABLE.md; echo rc=$?` |
| **Full suite command** | `python3 tools/wiki/wiki.py links --source-dir <clone>` + `python3 tools/wiki/honest02_truth.py --wiki-dir <clone> --db firestarter_app/firestarter/data/chip_database.json --allowlist tools/wiki/claim-allowlist.json` + `python3 tools/wiki/dispatch_mirror.py --app-dir firestarter_app --fw-dir firestarter` + the new D-10 checker |
| **Estimated runtime** | ~40 seconds for the four checkers against one fresh clone; the clone itself dominates |

> `tools/wiki/selftest.sh` exists and is the nearest thing to a suite, but it **mutates Phase 168's
> evidence files**. If used, `git checkout --` them immediately afterwards and assert the restoration.

---

## Sampling Rate

- **After every task commit:** the touched checker's own quick run + the zero-comment source scan (< 5 s)
- **After every plan wave:** all four `tools/wiki/` checkers against one fresh wiki clone
- **Before `/gsd-verify-work`:** the full closing sweep, written **before** any checkbox is flipped (plan 172-09 T-172-35 pattern)
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

Task IDs are assigned by the planner; rows below are the requirement-level contract each task must
inherit. `❌ W0` marks a command whose target does not exist yet and is created by this phase.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | POLICY-04 | T-173-01 | Direct push to a protected `main` is rejected **by GitHub**, not client-side | integration | `git fetch origin main && git checkout -B ruleset-probe origin/main && git commit --allow-empty -m probe && git push origin HEAD:main 2>&1 \| tee evidence/173-probe-<repo>.txt` — assert a `remote:` rule-violation line, never the exit code alone | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | POLICY-04 | T-173-01 | Push to an **unprotected** ref is accepted, proving default-branch scoping | integration | `git push origin ruleset-probe:refs/heads/probe-<ts>` then `git push origin :refs/heads/probe-<ts>` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | POLICY-04 | T-173-02 | The probe leaves ruleset state byte-identical | integration | `gh api repos/henols/<r>/rulesets/<id> --jq '{id,enforcement,current_user_can_bypass,conditions,bypass_actors}'` before **and** after; assert equal | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | POLICY-04 | — | Both channels carry the observed tag (operator-gated cut only) | manual + integration | `gh release list`; PyPI JSON API; `pip install --pre` in a `$(mktemp -d)` venv — never the editable install, never a predicted version | ❌ W0, conditional | ⬜ pending |
| TBD | TBD | TBD | POLICY-05 | — | `git.base-branch` resolves `beta` | unit | `node .claude/gsd-core/bin/gsd-tools.cjs query git.base-branch` → `beta` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | POLICY-05 | — | `main` and `beta` both read protected; a feature branch does not | unit | `… --is-protected main` → `true`; `… --is-protected beta` → `true`; `… --is-protected gsd/v1.35-…` → `false` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | POLICY-05 | — | The close-procedure note exists and its pointer resolves | file assertion | `test -f .planning/notes/v135-close-procedure-under-protection.md` + `/usr/bin/grep -F 'v135-close-procedure-under-protection.md' CLAUDE.md` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | POLICY-05 (D-10) | T-173-03 | Footer checker RED on a planted defect, GREEN on real inputs | integration, planted-first | run against a mutated copy (RED, capture `ERROR:`), restore, re-run (GREEN) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | POLICY-05 (D-10) | — | The new leg does not break the three existing legs | integration | run all four against one fresh clone | partially exists | ⬜ pending |
| TBD | TBD | TBD | POLICY-05 (D-09) | T-173-04 | Footers do not turn `honest02_truth.py` or `wiki.py links` RED | integration | both checkers against a **fresh post-push** clone | exists (commands) | ⬜ pending |
| TBD | TBD | TBD | POLICY-04 (D-12) | T-173-05 | gh#9 pinned; gh#7 and gh#6 closed; gh#5 and gh#9 open; 4 comments present | integration | `gh api graphql` `pinnedIssues`; `gh api repos/henols/firestarter_prom/issues/{5,6,7,9} --jq '{state,comments}'` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | POLICY-04 (criterion 4) | — | 999.46 exists; the pending todo file is gone | file assertion | `/usr/bin/grep -c '^### Phase 999.46' .planning/ROADMAP.md` = 1; `test ! -e .planning/todos/pending/2026-09-02-rulesets-block-stable-release-version-bump.md` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | POLICY-05 | — | The new checker carries zero `#` lines but the shebang | source scan | `[ "$(/usr/bin/grep -cE '^\s*#' tools/wiki/<checker>.py)" = 1 ]` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | POLICY-04 | — | Both submodules re-pinned and gitlink-equal | integration | per-submodule `git -C <sub> rev-parse HEAD` vs `git ls-tree HEAD <sub>` | pattern exists (172-09) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tools/wiki/<checker>.py` — the footer/provenance guard (D-10); no test file, verified by direct invocation with planted-failure evidence
- [ ] `.github/workflows/wiki-check.yml` — a fourth `run:` leg, comment-free
- [ ] `.planning/v1.35/` — the directory does not exist and must be created before `CLOSE-RECORD.md`
- [ ] `.planning/notes/v135-close-procedure-under-protection.md` — does not exist
- [ ] `.planning/phases/173-.../evidence/` — does not exist yet
- [ ] Framework install: **none required** — stdlib Python 3 and `gh` are already present

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The `beta` lockstep cut itself | POLICY-04 | Outward-facing and operator-gated since v1.21; D-01 splits the in-phase probe from the real cut, and D-03 permits closing POLICY-04 with the cut unperformed | Operator authorizes; then run v1.22's recipe with v1.30's PR amendment, and verify from the published artefacts (`gh release list`, PyPI JSON, a clean-venv `pip install --pre`) — never from a prediction |
| The four upstream replies | POLICY-04 (criterion 5) | D-13 requires a blocking operator wording review before four public comments are posted | Drafts land in the phase record; operator reads and approves; only then does anything reach GitHub |
| Push-probe rejection text | POLICY-04 | The exact `remote:` string GitHub returns is unobservable without performing the outward-facing push | Assert on the presence of a `remote:` rule-violation line in captured output, not on a pre-guessed literal |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
