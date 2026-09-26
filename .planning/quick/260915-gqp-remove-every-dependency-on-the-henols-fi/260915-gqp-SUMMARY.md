---
phase: quick-260915-gqp
plan: 01
status: complete
subsystem: docs
tags: [repo-rename, redirect, submit-repo, codegen, skills]

requires:
  - phase: 189-free-the-name
    provides: the rename of the firmware repo that created the alias this task removes reliance on
provides:
  - A SUBMIT_REPO that does not resolve through the rename alias
  - Sub-repo and wiki documentation addressing henols/firestarter directly
  - A codegen banner naming the meta repo by its current slug, with both artifacts re-synced
  - Two tracked devtest skills whose `gh --repo` argument targets the current slug
affects: [alias-retirement, dev-test-submit, catalog-codegen]

actuals:
  tokens: 52000
  tasks: 4
---

# Quick 260915-gqp — drop every dependency on the firestarter_prom redirect

## What was done

`henols/firestarter_prom` is a rename alias for `henols/firestarter` (id 1232995399),
not a separate repository. The operator asked for it to be deleted; deleting a repository
by that name would have deleted the meta repo itself, so the actual work is removing
everything that still addresses the project through the alias. This is the "repoint first,
then drop" half of that.

**firestarter_app** — `SUBMIT_REPO` retargeted, with the two repo-pinning assertions, the
paired return-value assertion, and seven mocked `gh` stdout URLs updated to match. README
and `.github/CONTRIBUTING.md` swept (7 links).

**firestarter_fw** — README, PINOUTS.md, PROTOCOLS.md swept (7 links).

**meta** — both `codegen.py` banner templates fixed, then `sync_to_subrepos.sh` re-ran to
regenerate `messages.h` and `messages.py`. Both artifacts differ from beta by exactly one
line, which confirms the catalog was already in sync and the regeneration introduced no
drift.

**meta `.claude/skills/`** — found during the sweep, not anticipated by the plan:
`devtest-rootcause` and `devtest-triage` shell out to `gh issue … --repo
henols/firestarter_prom`, and both carry a `REPO = "henols/firestarter_prom"` constant in
their scripts. These are live API targets. They would have failed silently — `gh` against
a dead slug — the moment the alias dropped.

## Key decisions

- **Historical citations kept verbatim.** `firestarter_prom#6`, `#18`, `#41` and `gh#47`
  record where decisions were filed, not where traffic should go. Issue numbers survive a
  rename, so these still resolve. The quoted title of #6 inside `submit.py` was likewise
  left alone: editing a quotation to match a later rename turns it into a misquote.
- **`prior_url` fixtures kept.** They model dedup state stored *before* the rename. Old
  stored URLs are exactly what a real upgraded install will hold, so the fixture is more
  honest unchanged.
- **`.vscode/` and `.devcontainer/` excluded.** Their `firestarter_prom` occurrences are
  `/home/henrik/dev/...` local filesystem paths and comments about the checkout's directory
  name, not GitHub URLs. The alias does not carry them.
- **Gitlinks deliberately not advanced.** The sub-repo commits sit on unmerged branches;
  pointing the meta gitlink at them would make the fresh-clone fixture exit 3. They advance
  when the sub-repo PRs merge.

## Deviations

- **No planner or executor subagent was spawned.** Most of the work was already complete
  and verified when `/gsd-quick` was invoked, so the orchestrator filled both roles inline.
- **`branch_name` came back null** from `init.quick`, which would have committed onto the
  active `v1.39-protocol-0x05-write-correctness` branch. A concurrent session was committing
  to that branch in the shared checkout, so the work was done in isolated clones of all
  three repositories forked from `beta` instead, on `quick/260915-gqp-no-prom-redirect`.

## Verification

- `firestarter_app`: `pytest tests/` on Python 3.11 — **1886 passed, 32 snapshots passed**.
- `firestarter_fw`: `pio test -e native` — **194 test cases, 194 succeeded**.
- Regenerated artifacts diff beta by one banner line each.
- Tree-wide scan: no remaining `firestarter_prom` outside `.planning/` archives, issue
  citations, and the local-path files listed above.

## Disclosed residuals

- **A first `pio run -e native` was reported as a build failure. That was the wrong
  command** — CI runs `pio test -e native`. The link error it produced also reproduces on
  untouched `beta`, so it is a property of that invocation, not a regression, and not a
  breakage of beta.
- **The alias is still live and must stay live until a CLI release ships this
  `SUBMIT_REPO`.** Dropping it earlier breaks `dev test --submit` for every existing
  install. Release is operator-gated.
- **`sub_repos` is `null` in `.planning/config.json`,** in `HEAD` as well as the working
  tree. Pre-existing, untouched here, recorded because it blocks milestone transition.
