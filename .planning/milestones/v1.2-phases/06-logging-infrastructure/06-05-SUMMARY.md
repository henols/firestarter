---
phase: 06-logging-infrastructure
plan: 5
subsystem: infra
tags: [github-actions, ci, codegen, drift-gate, yaml, python-3.11]

# Dependency graph
requires:
  - phase: 06-logging-infrastructure
    provides: "Plan 01 — codegen.py CLI + canonical messages.toml + vendored sub-repo copies + sync_to_subrepos.sh"
  - phase: 06-logging-infrastructure
    provides: "Plans 02/03/04 — generated artifacts committed (messages.h, messages.c, messages.py) and drift-free baseline"
provides:
  - "Firmware sub-repo CI (build.yml) regenerates messages.h + messages.c and asserts git diff --exit-code before pio run"
  - "Host sub-repo CI (ci.yml, NEW) regenerates messages.py + runs catalog validity + pytest on push:main and pull_request:main"
  - "Meta-repo CI (catalog-sync-check.yml, NEW) cross-asserts vendored messages.toml byte-identity across both sub-repos and against the meta-repo authoritative copy"
  - "Trigger surface widened: both sub-repos drop tools/** from paths-ignore so catalog/codegen edits trigger CI; meta-repo workflow triggers on .planning/catalog/** edits"
  - "Cross-repo drift gate empirically validated by negative simulation (mutating include/messages.h, then `git diff --exit-code` exits non-zero)"
affects: [phase-07-convert-error-warn-info, phase-08-convert-state-machine-prefix, phase-09-delete-old-log-macros, all-future-catalog-edits]

# Tech tracking
tech-stack:
  added: [actions/setup-python@v5 (alongside existing @v4 in firmware repo), Python 3.11 pinned in CI for tomllib]
  patterns:
    - "Drift gate pattern: codegen --check (validity) → codegen --target (regen) → git diff --exit-code (assert) BEFORE slow build steps so failures short-circuit fast"
    - "Cross-repo authority assertion: meta-repo workflow checks out both sub-repos at ref:main + cmp/diff vendored copies against meta-repo authoritative source"
    - "Separation of CI concerns: ci.yml = test gate, release.yml = tag creation, publish.yml = PyPI publish (no multi-purposing)"

key-files:
  created:
    - "firestarter_app/.github/workflows/ci.yml (NEW — host sub-repo's first test-running CI)"
    - ".github/workflows/catalog-sync-check.yml (NEW — meta-repo's first CI workflow)"
  modified:
    - "firestarter/.github/workflows/build.yml (extended with Set up Python 3.11 + Catalog validity check + Codegen drift gate; dropped tools/** from paths-ignore; added pull_request trigger)"

key-decisions:
  - "release.yml NOT given `needs: [ci]` gate — plan body marks this as optional; preserving release.yml fully untouched keeps existing release semantics (operator can retrofit later if a bad-catalog → tag → publish race ever bites)"
  - "GitHub slugs pinned to `henols/firestarter` and `henols/firestarter_app` — confirmed against `git remote get-url origin` on both submodules"
  - "Both `cmp` (byte-equality) AND `diff` (human-readable output) used in meta-repo workflow assertions — cmp gives the exit code, diff gives the readable failure dump in CI logs"
  - "submodules: recursive on meta-repo checkout step — required so sub-repo TOMLs are present at the right SHA when the meta-repo workflow runs (orchestrator objective requirement)"

patterns-established:
  - "Drift-gate-before-slow-build: codegen + diff runs BEFORE pio run / before pytest install — fast failure short-circuits the slow pipeline (~30s PIO install + multi-minute build)"
  - "paths-ignore must NOT include tools/** in any drift-gated sub-repo CI — edits to catalog/codegen.py have to trigger CI or the gate is meaningless"
  - "Meta-repo .github/workflows/ is allowed in this otherwise-planning-only repo — tooling directories at repo root are fine; only `.planning/` and `.claude/` are the tracked-content namespaces"

requirements-completed: [LCI-01, LCI-02, LCI-03, LCI-04, LMIG-01]

# Metrics
duration: ~7 min
completed: 2026-05-18
---

# Phase 6 Plan 5: CI Drift Gates Summary

**Three-repo CI lockstep enforcement: firmware build.yml + new host ci.yml + new meta-repo catalog-sync-check.yml all assert codegen drift = CI failure, with `cmp` byte-equality cross-checks across vendored catalog copies.**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-05-18T12:22:19Z
- **Completed:** 2026-05-18T12:26:00Z (approx)
- **Tasks:** 3 (all auto)
- **Files modified:** 3 workflow files across 3 repos (+ 2 meta-repo pointer bumps)

## Accomplishments

- Firmware sub-repo CI (`firestarter/.github/workflows/build.yml`) now runs Python 3.11 + `codegen.py --check` + `codegen.py` (cpp + cpp-table) + `git diff --exit-code include/messages.h src/messages.c` **before** the slow `pio run`. Dropped `'tools/**'` from `paths-ignore`. Added `pull_request: branches: [main]` trigger.
- Host sub-repo (`firestarter_app/.github/workflows/ci.yml`) gained its **first test-running** CI workflow: catalog validity + codegen drift gate on `firestarter/messages.py` + `pip install -e .[dev]` + `pytest tests/ -v`. Triggers on push:main AND pull_request:main. release.yml and publish.yml remain untouched.
- Meta-repo (`.github/workflows/catalog-sync-check.yml`) gained its **first CI workflow** — cross-sub-repo authority assertion. Checks out meta-repo (with `submodules: recursive`) + `henols/firestarter` + `henols/firestarter_app` at ref:main, then `cmp` + `diff` asserts byte-identity of vendored `tools/catalog/messages.toml` copies against each other AND against `.planning/catalog/messages.toml`.
- Empirically verified the drift gate: positive simulation (regen + diff exits 0 on the committed state) and negative simulation (mutate `include/messages.h`, `git diff --exit-code` exits 1 — the exact CI failure mode).

## Task Commits

Each task was committed atomically. Tasks 1 + 2 are submodule commits with paired meta-repo pointer bumps; Task 3 is a single meta-repo commit; the final plan-metadata commit will follow this SUMMARY.

1. **Task 1: firestarter build.yml — codegen drift gate + catalog validity + drop tools/** (submodule)** — `firestarter@c436c18` (ci)
   - Meta-repo pointer bump: `cbf84cc` (chore)
2. **Task 2: firestarter_app ci.yml — NEW host CI (submodule)** — `firestarter_app@43ce826` (ci)
   - Meta-repo pointer bump: `d8d42f6` (chore)
3. **Task 3: meta-repo catalog-sync-check.yml — NEW** — committed together with this SUMMARY + STATE.md + ROADMAP.md as the plan-metadata commit (see "Plan metadata" below).

**Plan metadata:** committed in same commit as Task 3 workflow file + SUMMARY.md + STATE.md + ROADMAP.md (sequential mode lets us combine the meta-repo workflow with the close-out).

## Files Created/Modified

### Firmware sub-repo (firestarter)

**`firestarter/.github/workflows/build.yml`** — MODIFIED (38 insertions, 3 deletions):

Diff summary:
- `on:` block: dropped `- 'tools/**'` from `paths-ignore`; mirrored the full block under a new `pull_request: branches: [main]` trigger.
- Inserted three new steps after `stefanzweifel/git-auto-commit-action@v5` and BEFORE `Install PlatformIO Core`:
  - `Set up Python 3.11 for codegen` (`actions/setup-python@v5` with `python-version: '3.11'`)
  - `Catalog validity check` (`python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check`)
  - `Codegen drift gate (messages.h + messages.c)` (regens both targets + `git diff --exit-code include/messages.h src/messages.c`)
- Header comment: `# Phase 6 (LCI-01 + LCI-04): codegen drift + catalog validity. Drift fails CI visibly in the PR.`
- Pre-existing steps preserved verbatim: cache, setup-python@v4, update_version.py, git-auto-commit-action, Install PlatformIO Core, Build PlatformIO Project, Release.

### Host sub-repo (firestarter_app)

**`firestarter_app/.github/workflows/ci.yml`** — NEW (49 lines). Full content:

```yaml
# Phase 6 (LCI-02 + LCI-03 + LCI-04): host CI — codegen drift + catalog validity + pytest. release.yml and publish.yml are tag/PyPI-only.
name: Host CI
on:
  push:
    branches:
    - main
    paths-ignore:
    - '**.md'
    - '.gitignore'
    - 'docs/**'
    - '.vscode/**'
    - '.editorconfig'
  pull_request:
    branches:
    - main
    paths-ignore:
    - '**.md'
    - '.gitignore'
    - 'docs/**'
    - '.vscode/**'
    - '.editorconfig'

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Catalog validity check
        run: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check

      - name: Codegen drift gate (messages.py)
        run: |
          python3 tools/catalog/codegen.py \
            --catalog tools/catalog/messages.toml \
            --target firestarter/messages.py \
            --language python
          git diff --exit-code firestarter/messages.py

      - name: Install package + dev deps
        run: pip install -e .[dev]

      - name: Run pytest
        run: pytest tests/ -v
```

`release.yml` and `publish.yml` are UNCHANGED (verified via `git status --short`).

### Meta-repo

**`.github/workflows/catalog-sync-check.yml`** — NEW. Full content:

```yaml
# Phase 6 (LCI-02 supplementary): cross-sub-repo authority assertion per RESEARCH §"Authority Assertion". Triggers on catalog edits OR this workflow's own edits.
name: Catalog sync check
on:
  push:
    branches:
    - main
    paths:
    - '.planning/catalog/**'
    - '.github/workflows/catalog-sync-check.yml'
  pull_request:
    branches:
    - main
    paths:
    - '.planning/catalog/**'
    - '.github/workflows/catalog-sync-check.yml'
  workflow_dispatch:

jobs:
  sync-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check out meta-repo
        uses: actions/checkout@v4
        with:
          path: meta
          submodules: recursive

      - name: Check out firestarter (firmware sub-repo)
        uses: actions/checkout@v4
        with:
          repository: henols/firestarter
          path: firestarter
          ref: main

      - name: Check out firestarter_app (host sub-repo)
        uses: actions/checkout@v4
        with:
          repository: henols/firestarter_app
          path: firestarter_app
          ref: main

      - name: Assert cross-sub-repo vendored catalog identity
        run: |
          cmp firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
          diff firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
          echo "OK: vendored messages.toml byte-identical across sub-repos"

      - name: Assert vendored catalog matches meta-repo authoritative copy
        run: |
          cmp meta/.planning/catalog/messages.toml firestarter/tools/catalog/messages.toml
          cmp meta/.planning/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
          diff meta/.planning/catalog/messages.toml firestarter/tools/catalog/messages.toml
          diff meta/.planning/catalog/messages.toml firestarter_app/tools/catalog/messages.toml
          echo "OK: meta-repo authority preserved end-to-end"
```

## Decisions Made

1. **`release.yml` left fully untouched** (no `needs: [ci]` gate added). Plan body explicitly marks this as optional; preserving release.yml semantics is the conservative path. If a "bad catalog → tag → PyPI publish" race ever bites, retrofitting `needs: [ci]` is a one-line follow-up.
2. **GitHub repo slugs pinned to `henols/firestarter` and `henols/firestarter_app`.** Confirmed against `git remote get-url origin` on both submodules — both point to `git@github.com:henols/<repo>.git`.
3. **Both `cmp` (byte-equality) AND `diff` (readable diff)** used in the meta-repo workflow's assertion steps. `cmp` provides the load-bearing non-zero exit code on drift; `diff` provides the readable failure dump in CI logs so a reviewer can see exactly which line(s) drifted.
4. **`submodules: recursive` added to meta-repo checkout step** per the sequential_execution objective ("workflow needs `submodules: recursive` on the checkout step"). This is belt-and-braces: the workflow ALSO independently clones both sub-repos via `repository:` slugs (so it doesn't depend on the meta-repo's submodule pointer being current). Both mechanisms work; recursive checkout means the meta-repo's `firestarter/` and `firestarter_app/` paths will be populated at the meta-repo's pinned SHAs, which is useful for any future assertion that compares meta-repo's pinned submodule state vs. each sub-repo's `main`.
5. **Step ordering: validity → codegen → diff → install → build/test.** `--check` runs FIRST so an invalid catalog fails with a clear `"catalog validation failed at <id> <name>"` message rather than an opaque diff. Codegen + diff runs BEFORE `pip install` / `pio install` so a fast failure short-circuits the slow pipeline (~30s PIO install + multi-minute firmware build; ~10s pip install on host).

## Deviations from Plan

None - plan executed exactly as written. The plan's `<action>` block specified `diff …` assertions; the sequential_execution objective layered an additional `cmp` byte-equality requirement on the meta-repo workflow which was added without altering the plan's `diff` assertions (they coexist in the same `run: |` blocks). Plan's optional `needs: [ci]` gate on release.yml was NOT added; decision documented in "Decisions Made" #1.

## Issues Encountered

- **PyYAML missing from devcontainer** (one-off): The acceptance-criteria automated checks rely on `python3 -c "import yaml; ..."` for parsed-YAML step ordering assertions. Resolved with `pip install -q pyyaml` (6.0.3) before re-running. Not a plan deviation; just a verification-time tooling install. Did not alter any committed file.

## Empirical Drift-Gate Validation

Performed local simulation of the CI behaviour (per plan acceptance criteria):

**Positive (committed state is drift-free):**
- `firestarter`: `python3 tools/catalog/codegen.py … --target include/messages.h --language cpp && git diff --exit-code include/messages.h` → exit 0
- `firestarter_app`: `python3 tools/catalog/codegen.py … --target firestarter/messages.py --language python && git diff --exit-code firestarter/messages.py` → exit 0
- Cross-repo: `diff firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml` → exit 0
- Meta vs vendored: `diff .planning/catalog/messages.toml firestarter/tools/catalog/messages.toml` → exit 0; same for firestarter_app → exit 0

**Negative (CI failure mode reproduced and reverted):**
- Mutated `firestarter/include/messages.h` (appended `// drift-test` comment).
- `git diff --exit-code include/messages.h` → exit 1 (the exact CI failure mode).
- Then ran `codegen.py` → regen overwrote the mutation → `git diff --exit-code` → exit 0 (confirms codegen is idempotent).
- Reverted with `git checkout -- include/messages.h`; tree clean.

**Pytest sanity:** `pytest tests/ -v` in `firestarter_app/` reported `14 passed in 0.28s` (10 decoder + 4 fwguard tests) — confirming the new ci.yml's `Run pytest` step would pass.

## Pre-Existing Uncommitted Files (Untouched)

The plan's success criteria explicitly required leaving pre-existing uncommitted files unstaged. Per `git status --short` at plan close (excluding the staged plan-metadata files), the following pre-existing files remain unstaged and unmodified by this plan:

- **firestarter submodule:** `include/rurp_register_utils.h` (M)
- **firestarter_app submodule:** `firestarter/config.py` (M), `firestarter/main.py` (M), `tests/__pycache__/` (untracked)
- **meta-repo:** `.devcontainer/devcontainer.json` (M), `.devcontainer/devcontainer-lock.json` (untracked), `.planning/debug/fm1608-fresh-chip-baseline.md` (M), `.planning/phases/01-…/01-PATTERNS.md` (untracked), `.planning/phases/03-…/03-LEARNINGS.md` (untracked), `.planning/research/HARDWARE_SIM_SPEC.md` (untracked). The meta-repo `.planning/config.json` (M) is also pre-existing.

## User Setup Required

None — workflows run on GitHub Actions infrastructure with default `secrets.GITHUB_TOKEN`. Both sub-repos are public (`henols/firestarter`, `henols/firestarter_app`), so no PAT is needed for the meta-repo's cross-repo checkouts. The first time `catalog-sync-check.yml` runs in production, the operator should confirm the workflow is visible in the Actions tab and triggers correctly via `workflow_dispatch`.

## Next Phase Readiness

- Phase 7+ catalog edits and call-site conversions are now protected by three independent drift gates. Any of the following PR scenarios will fail CI visibly:
  - Hand-editing `messages.h` / `messages.c` / `messages.py` without updating the catalog (firmware build.yml + host ci.yml codegen drift assertions).
  - Editing the catalog in one sub-repo only (meta-repo catalog-sync-check.yml cross-diff).
  - Editing the meta-repo catalog without running `.planning/catalog/sync_to_subrepos.sh` (meta-repo catalog-sync-check.yml `meta vs vendored` diff).
  - Pushing an invalid catalog (e.g. duplicate id) — `--check` step fails before the drift gate runs.
- Phase 6 (logging-infrastructure) closes with this plan. The next milestone-v1.2 phase is Phase 7 (Convert ERROR + WARN + INFO Call-Sites, LMIG-02).

## Self-Check: PASSED

- `[ -f /workspaces/firestarter_prom/firestarter/.github/workflows/build.yml ]` → FOUND (M)
- `[ -f /workspaces/firestarter_prom/firestarter_app/.github/workflows/ci.yml ]` → FOUND (A)
- `[ -f /workspaces/firestarter_prom/.github/workflows/catalog-sync-check.yml ]` → FOUND (NEW)
- `firestarter@c436c18` → FOUND in `git -C firestarter log`
- `firestarter_app@43ce826` → FOUND in `git -C firestarter_app log`
- Meta-repo pointer bumps `cbf84cc` and `d8d42f6` → FOUND in meta-repo `git log`
- Task 3 meta-repo workflow committed in plan-metadata commit (this SUMMARY).

---
*Phase: 06-logging-infrastructure*
*Completed: 2026-05-18*
