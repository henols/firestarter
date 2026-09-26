---
id: rekey-cross-tree-checker-retirement
created: 2026-09-08T00:00:00Z
title: Retire the re-key cross-tree checker — CI must not police a .planning record, and GSD must not depend on it
resolved: 2026-09-08 (executed in-session; meta f81b1e8b, app e596853)
status: resolved
area: meta + app
files:
  - tools/rekey/check_rekey_ledger.py (223 lines — DELETE)
  - .github/workflows/rekey-ledger-check.yml (DELETE)
  - .planning/MILESTONES.md (rewrite — drops both "runners"; was line 49)
  - .planning/STATE.md (the other live citer)
  - firestarter_app/tests/test_rekey_ledger.py (drop 13 of 23 defs — every `_run_checker` leg)
  - firestarter_app/tests/fixtures/planted_rekey_mutation.py (DELETE — no other referent)
  - firestarter_app/tests/test_blast_radius_invariance.py:31-34 (prose cites the meta checker)
  - firestarter_app/tests/fixtures/rekey_ledger.py (KEEP — app-internal declaration mechanism)
---

## Decision

**Operator, 2026-09-08:** *"That is nothing we shall do, it's not the CI's job to do"* and *"gsd
shall not use it in any way at all, it will just break the GSD's intended workflow."*

The checker binds `firestarter_app/tests/fixtures/rekey_ledger.py` to a table in
`.planning/MILESTONES.md`. Keeping a `.planning/` record accurate is **GSD's** responsibility.
Wiring it to a CI gate means a planning-table drift turns a build red — CI testing the planning
process instead of the product. Provenance (Phase 174, GATE-06, D-13) explains why it exists; it
is not a justification for keeping it.

## Two measured defects that independently condemn the coupling

Both verified in the devcontainer on 2026-09-08.

**1. It breaks app CI.** `firestarter_app/tests/test_rekey_ledger.py` computes
`_REPO_ROOT = Path(__file__).parent.parent.parent` and subprocess-invokes
`_REPO_ROOT/tools/rekey/check_rekey_ledger.py`. That resolves only because the app is a submodule
of `/workspaces`. There is **no** skip guard — `pytest` is imported solely for a `parametrize` at
line 245 — and `tests/conftest.py`'s `collect_ignore` covers only `test_pyusb_api_surface.py`.
App CI (`ci.yml:90`, `beta-release.yml:76`) runs `pytest tests/` on a **bare
`actions/checkout@v4`** with no meta checkout and no submodule.

Measured on a simulated bare checkout:

| Tree | Result |
|---|---|
| devcontainer, meta present | `26 passed` |
| bare checkout (= app CI) | **`13 failed, 13 passed`** |

**2. Three of its own fail-closed proofs are tautological.** `python3` invoking a *missing*
script exits `2`. The checker's own fail-closed path also exits `2`. So
`test_check_rekey_ledger_fails_closed_on_missing_ledger`, `..._on_missing_milestones` and
`..._on_unparsable_ledger` — which assert `returncode == 2` — **pass with the checker absent**.
They were the evidence that the gate could not silently pass, and they cannot detect their own
subject's deletion. Confirmed: all three PASSED on the bare checkout.

## Timing — this is the clean moment

- No `180-*` phase directory exists yet, so **no active plan depends on the checker**.
- Live citers are only `.planning/MILESTONES.md` and `.planning/STATE.md`.
- Archived citers are the phase dirs `174`–`179` only.

## Approach

**Meta:**
1. `git rm tools/rekey/check_rekey_ledger.py` and
   `.github/workflows/rekey-ledger-check.yml`; remove the untracked `tools/rekey/__pycache__/`.
2. Rewrite the `MILESTONES.md` protocol paragraph (line 49 as it then stood): **drop both "runners"**. The
   `### v1.36 Re-Key Ledger` table itself **stays** — a human record of which frozen hashes moved
   and why is exactly what a GSD record is for. What goes is the claim that a script enforces it.
   The two-commit discipline (behaviour change first, declaration second, `before` never
   overwritten) stays as a **review** rule.
3. Repair the `STATE.md` citer.
4. **Leave the `174`–`179` archived records untouched.** They accurately record what existed at
   the time; rewriting them would destroy the evidence. Record the retirement in `MILESTONES.md`
   so a reader of those archives knows the checker is gone.

**App:**
5. Drop the 13 `_run_checker` defs from `tests/test_rekey_ledger.py`; **keep** the 10 that need no
   meta tree: `test_every_ledger_row_is_a_well_formed_four_tuple`,
   `..._shape_id_resolves_and_recomputes`, `..._ledger_id_matches_grammar`,
   `test_ledger_has_exactly_eight_rows_after_the_177_declaration`,
   `test_ledger_id_values_are_unique`, `test_shape_id_ledger_id_pairs_are_unique`,
   `test_no_declared_row_has_after_hash_equal_to_before_hash`,
   `test_ledger_sweep_is_well_defined_on_a_single_row_tuple`,
   `test_undeclared_after_hash_routes_to_before_hash_and_never_abstains`,
   `test_ledger_id_order_is_ascending`. These are app-internal and legitimately CI's job.
6. `git rm tests/fixtures/planted_rekey_mutation.py`.
7. Update the `test_blast_radius_invariance.py` docstring (lines 31-34) which cites the checker.
8. **Keep** `tests/fixtures/rekey_ledger.py` — `test_blast_radius_invariance.py:278` directs a
   developer to declare intentional shape changes there. That is a real app-internal mechanism.

## Acceptance

- [ ] `tools/rekey/` and `.github/workflows/rekey-ledger-check.yml` are gone; `tools/` holds only
      `catalog/` (plus `wiki/MIGRATION-TABLE.md` until its own relocation todo lands).
- [ ] `/usr/bin/grep -rn "check_rekey_ledger" .planning/*.md .planning/milestones/*.md | wc -l` is 0.
- [ ] `/usr/bin/grep -rn "check_rekey_ledger" firestarter_app | wc -l` is 0.
- [ ] `MILESTONES.md` still carries all 8 `RK-174-` rows and no longer claims any runner enforces
      them.
- [ ] **The bare-checkout run is now green**: copy `firestarter_app` to a parent with no `tools/`
      and `pytest tests/test_rekey_ledger.py` passes with 0 failures — this is the whole point, so
      it is the load-bearing check.
- [ ] Full app suite still meets its floor; `pytest tests/ -o addopts=""` reports no regression
      versus the pre-task count.
- [ ] Both repos committed on their `gsd/v1.36-*` branches. No push (ship time only).

## RESOLUTION (2026-09-08)

Executed in full. **meta `f81b1e8b`** (checker + workflow deleted, protocol and 8-row table
dropped from `MILESTONES.md`, `STATE.md` annotated, `firestarter_app` gitlink advanced) and
**app `e596853`** (`tests/test_rekey_ledger.py`, `tests/fixtures/rekey_ledger.py` and
`tests/fixtures/planted_rekey_mutation.py` deleted; prose and the frozen-shape failure message
repaired). Neither pushed — ship time only.

### The load-bearing check passed

The whole justification was that app CI could not work on a bare checkout. Full suite, run from a
copy of `firestarter_app` whose parent directory has no `tools/`:

| Tree | Before | After |
|---|---|---|
| bare checkout (= app CI) | **13 failed**, 13 passed | **2174 passed, 65 skipped, 32 snapshots, 0 failures** |
| devcontainer, CI-accurate `--cov` | 26 passed (module) | **2239 passed, 0 failures, 32 snapshots, 84.37% coverage** |

`--cov-fail-under=70` passes with 14 points of headroom. Zero `FAILED`/`ERROR` lines in either run.

### Deviations from the plan as written

1. **The whole protocol went, not just the enforcement.** The plan proposed keeping the `RK-174`
   table as a human record. Operator ruled the entire protocol and table out, so the app-side
   ledger fixture and its 10 self-contained tests went too — not just the 13 `_run_checker` legs.
2. **Three numeric/procedural residues were found and recorded** rather than left to bite a later
   phase. Each is now stated in the v1.36 section of `MILESTONES.md`:
   - The reusable green-tree ritual at `179-PATTERNS.md:454` / `179-RESEARCH.md:508` lists
     **eight** `rc=0` legs, one being the deleted checker. It is now **seven**, and they are named.
   - The **full-suite floor moved from `>= 2242` to 2239** (26 instances deleted; 2265 -> 2239).
     The old floor is recorded at `179-02-PLAN.md:39`/`:540` and `179-02-SUMMARY.md:92`. It is a
     phase-179 assertion, not a standing gate, but a plan copying it forward would read RED.
   - **~37 line-pinned citations into `MILESTONES.md` shifted by 11 lines** (`:14-45`, `:36-53`,
     `:39`, `:41`), and those naming table rows now name nothing. Left as written — a
     `.planning`-to-`.planning` citation is historical by intent — with the recovery pointer
     `git show f81b1e8b^:.planning/MILESTONES.md` recorded and verified to resolve.
3. **Archived records left unedited.** Phases 174-179 still describe the protocol as live, which
   was true when written. `174-05-PLAN.md:202`'s `<automated>` block invokes the deleted checker
   and parses the deleted workflow; archived, will not re-run. `STATE.md`'s 179-02 decision-log
   entry was annotated, not rewritten.

### Not done, deliberately

`.planning/milestone.lock` still names phase 179 with dead pid 1055301 (36 h stale as of this
session). Left in place — it is operator state, nothing was blocked by it, and clearing it was
not part of this task.
