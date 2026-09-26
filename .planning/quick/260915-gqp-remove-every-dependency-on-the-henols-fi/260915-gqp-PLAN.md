---
phase: quick-260915-gqp
plan: 01
type: execute
wave: 1
depends_on: []
autonomous: false
requirements: [PROM-01, PROM-02, PROM-03, PROM-04]
files_modified:
  - tools/catalog/codegen.py
  - .claude/skills/devtest-rootcause/SKILL.md
  - .claude/skills/devtest-rootcause/scripts/seed_debug_session.py
  - .claude/skills/devtest-triage/SKILL.md
  - .claude/skills/devtest-triage/scripts/devtest_issues.py
  - firestarter_app/firestarter/submit.py
  - firestarter_app/firestarter/messages.py
  - firestarter_app/tests/test_submit.py
  - firestarter_app/README.md
  - firestarter_app/.github/CONTRIBUTING.md
  - firestarter_fw/include/messages.h
  - firestarter_fw/README.md
  - firestarter_fw/PINOUTS.md
  - firestarter_fw/PROTOCOLS.md

estimate:
  tokens: 40000
  tasks: 4
  confidence: medium

must_haves:
  truths:
    - No tracked, non-archival file in any of the three repositories resolves a GitHub
      URL or a `gh --repo` argument through the `henols/firestarter_prom` rename alias.
    - Historical citations (`firestarter_prom#6`, `#18`, `#41`, `gh#47`) survive unchanged,
      because they record where a decision was filed, not where traffic should go today.
  artifacts:
    - A retargeted `SUBMIT_REPO` whose pinning tests assert the new slug.
    - Regenerated `messages.h` / `messages.py` differing from beta by the banner line only.
  key_links:
    - .planning/notes/999.9-repo-rename-impact-analysis.md
---

# Quick 260915-gqp — drop every dependency on the firestarter_prom redirect

## Why

`henols/firestarter_prom` is not a repository. It is a rename alias left behind when the
meta repo was renamed to `henols/firestarter` on 2026-09-14 (`d9f5434b`). The operator
wants the alias gone. Everything that still addresses the project through that alias must
be repointed first, or it breaks the moment the alias is dropped.

This is the "kill the redirect first" ordering: repoint, release, then drop the alias.

## Requirements

- **PROM-01** — `SUBMIT_REPO` and its pinning tests name `henols/firestarter`.
- **PROM-02** — Sub-repo user-facing docs link to `henols/firestarter`.
- **PROM-03** — The codegen banner names the meta repo by its current slug, and both
  generated artifacts are re-synced from it.
- **PROM-04** — Tracked skills that shell out to `gh --repo` target the current slug.

## Tasks

1. Retarget `SUBMIT_REPO`; update the two repo-pinning assertions, the paired return-value
   assertion, and the mocked `gh` stdout URLs. Leave `prior_url` fixtures alone — they model
   dedup state stored before the rename, which is realistic input, not a stale link.
2. Sweep `henols/firestarter_prom` URLs and `[firestarter_prom]` link text out of the four
   sub-repo docs. Correct `Contributing.md`'s separate defect: it still called the *firmware*
   repo `firestarter`, a name that now belongs to the meta repo.
3. Fix both codegen banner templates and run `tools/catalog/sync_to_subrepos.sh`.
4. Retarget the `gh --repo` slug in the two tracked devtest skills and their scripts.

## Verification

- `pytest tests/` in `firestarter_app` on Python 3.11 (the CI floor).
- `pio test -e native` in `firestarter_fw`.
- Regenerated artifacts diff against beta by exactly one line each.
- A tree-wide scan shows no remaining non-archival `firestarter_prom` reference.

## Out of scope

- Dropping the alias itself — that is operator-performed on GitHub, and only after a CLI
  release carries the new `SUBMIT_REPO`.
- `.planning/` archives and issue-number citations, which are historical by intent.
- `.vscode/` and `.devcontainer/` occurrences: developer-local filesystem paths, not
  GitHub URLs, so the alias does not carry them.
