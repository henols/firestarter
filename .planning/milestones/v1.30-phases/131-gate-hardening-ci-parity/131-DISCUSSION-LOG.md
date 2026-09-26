# Phase 131: Gate Hardening & CI Parity - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-03
**Phase:** 131-gate-hardening-ci-parity
**Areas discussed:** Gate test seam, Canary & file floor, Count gate shape, CI-parity recipe form,
The real CI dispatch, py3.9 floor + mypy pin, Adjacent fail-open debt

**Shape of this discussion:** seven gray areas were identified and presented across two multiSelect
questions. The operator answered **"You decide"** to both — delegating all seven. No per-area
question rounds were run; instead all seven were resolved by Claude against the measured research,
and each resulting decision in CONTEXT.md records its own rationale. This log preserves the
alternatives that were on the table when the delegation happened.

---

## Gate test seam (GATE-06)

| Option | Description | Selected |
|--------|-------------|----------|
| Env-var argv override seam | Research's suggestion — a `FIRESTARTER_*` env var lets the test substitute a fake-mypy stub; matches the five committed checker seams | |
| Fake mypy stub earlier on `PATH` | Test controls which `mypy` resolves | |
| Pure classifier + thin runner | Split `count_mypy_errors()`; test the pure half against canned output; no production seam | ✓ |

**Choice:** pure classifier + thin runner (D-01/D-02/D-03).
**Why the others lost:** the env-var form is a bypass added to the one gate whose sin was being
bypassable — and it is the shape `channel.py` forbids in its own docstring, learned from
`${sysenv.VAR}` failing OPEN on the firmware side. The existing checker seams override *scan
targets* (fail-closed-able), not *what program runs*. The `PATH` stub form contradicts GATE-04,
which exists precisely to kill `PATH` resolution.

---

## Canary floor & the files floor (GATE-02, GATE-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Add P-13's canary fixture | A module with known deliberate type errors, asserted as a floor; P-13 calls it "the load-bearing one" | |
| Completion clause + `MIN_CHECKED_SOURCE_FILES` only | STACK's FIX-2 shape; no canary | ✓ |
| Derived file floor | Compute the expected file count from a glob instead of committing 120 | |

**Choice:** no canary; literal `MIN_CHECKED_SOURCE_FILES = 120` (D-04/D-05).
**Why:** a canary sits *inside* the checked tree, so it inflates the very count Phase 132 must drive
to ≤35 — it would corrupt the watermark's meaning permanently. Excluding it into a second mypy run
proves only that a differently-scoped run works. The abort mode it targets is already caught
structurally by requiring `(checked N source files)`, which is strictly stronger since it does not
depend on the canary's errors surviving. A *derived* file floor is always satisfied by construction,
so it cannot catch a truncated run — this is why "derived" is right for GATE-08/GATE-10 (independent
derivations) and wrong here.
**Recorded as a deliberate rejection**, not an oversight, since P-13 frames the canary as
load-bearing. Reopen if an abort mode is found that emits a valid completion clause over a truncated
file set.

---

## Count gate shape (GATE-08)

| Option | Description | Selected |
|--------|-------------|----------|
| Derived parity only | Recompute the partition from the DB and compare to `sdp_capability()` | |
| Committed literal triple only | Assert `43/41/84` as constants | |
| Both + a change protocol | Element-wise parity, plus the literal triple, plus a stated ALLOW→REFUSE rule | ✓ |

**Choice:** both, element-wise, extending the existing modules (D-06).
**Why:** parity-only passes when both sides drift together — exactly P-10's narrowing-for-convenience
hole. Literal-only fails to pin the derivation source. Element-wise (not just totals) is what catches
a *single* chip moving. The change protocol — ALLOW→REFUSE only for a **decode** reason, never a
test-outcome reason — is what makes the gate mean something in the field.
**Note:** extend `tests/test_sdp_db_invariant.py` / `test_sdp_table_parity.py`; do not add a third
module.

---

## CI-parity recipe form (GATE-09)

| Option | Description | Selected |
|--------|-------------|----------|
| Documented steps in the meta record | Prose checklist every phase follows | |
| Makefile target | `make ci-parity` | |
| Committed script in the app repo | `firestarter_app/tools/ci_parity.sh`, four legs, non-zero on any failure | ✓ |

**Choice:** committed script in the app repo (D-07/D-08), with board presence as **evidence
metadata** rather than a fifth leg (D-09), and `check_no_exists_proxy.py` as a one-time recorded
confirmation rather than a recipe leg (D-10).
**Why:** GATE-09 says *runnable*, and a doc-only recipe is what every later phase silently skips. No
Makefile exists in the app repo. It lives in the app repo because later phases invoke it with the
submodule as their working directory, and because it is the repo whose CI it mirrors. The no-board
leg cannot be a script step — a script cannot detach hardware — so the script stamps
`BOARD-ATTACHED: <list>|none` and the phase's acceptance requires one recorded `none` run. Keeping
`check_no_exists_proxy.py` out of the script preserves the recipe as a faithful `ci.yml` mirror.

---

## The real CI dispatch (GATE-07)

| Option | Description | Selected |
|--------|-------------|----------|
| One dispatch on the fork base | `beta` @ `16a313a`, operator-run, captures the current post-fork count | ✓ |
| Two dispatches | Add a post-hardening run on the milestone branch to prove the hardened gate in CI | |

**Choice:** one, operator-run, recorded in `131-CI-BASELINE.md` (D-11/D-12).
**Why:** the count is a property of the fork base, and one run settles it. A post-hardening dispatch
would show `exit 1` on a 69-error tree — the same red for the same reason. Phase 132 gets the
hardened-gate-in-CI proof for free, being the phase that turns it green.
**Authorization:** unchanged standing rule — no plan's `<automated>` block may contain
`gh workflow run`; it stays prose in `131-HANDOFF.md`. No workflow edit needed (`workflow_dispatch:`
landed in Phase 127). Pushing nothing else fires, since `ci.yml`'s `push` trigger is `main`-only.
**Honesty clause:** the count is read, never computed; if it differs from research's 69, the measured
number wins and the divergence is recorded.

---

## py3.9 floor + mypy pin (GATE-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Accept the gap, record it, backlog the drop | Keep `>=3.9`; ruff's `py39` target carries the syntax floor | ✓ |
| Add a py3.9 CI matrix leg | Closes the gap at recurring CI cost | |
| Drop 3.9 support | `requires-python = ">=3.10"`, drop the classifier | |
| Bound mypy at `<3` | Separate call — protects the summary-line regex GATE-02 depends on | ✓ |

**Choice:** keep `>=3.9` and record the residual gap; add `mypy>=2.1.0,<3` (D-13/D-14).
**Why:** dropping 3.9 is a **published-metadata breaking change** on a live PyPI package, orthogonal
to all six milestone items — and it is not a call delegation covers. "You decide" extends to
implementation shape, not to the package's advertised support contract, so the conservative
non-change was taken deliberately and filed as its own backlog item. A matrix leg is real recurring
cost for a floor ruff already carries at the syntax/idiom level.
**The gap, stated:** after `python_version = "3.10"`, nothing type-checks against the advertised
floor; ruff catches py3.10-only *syntax*, nothing catches a py3.10+ *stdlib API* on 3.9. Not new —
it has held since 2026-05-27, because `python_version = "3.9"` was silently discarded and never once
took effect.
**The `<3` bound** is a compatibility bound on a parsed output contract, not the pinned venv research
rejected (that was a second venv + install step + cache key).

---

## Adjacent fail-open debt

| Option | Description | Selected |
|--------|-------------|----------|
| Restore the softened Phase-129 assert here | Research's operator-decision 7(a) | |
| Record the downgrade deliberately, act elsewhere | Carry it forward with a stated owner | |
| Investigate first, then decide | Verify the claim before scoping work to it | ✓ |

**Choice:** investigated, and the finding overturned the premise (D-17/D-18).
**What was found — verified live this session, and a correction to the research record:**
- **Wrong repo.** `test_present_root_with_missing_target_raises_not_skips` is at
  `firestarter/tests/test_flash_path_record_sync.py:694` — the **firmware** repo, which this
  milestone does not touch. It is **not** in `firestarter_app`.
- **Wrong commit.** The softening is firmware `1c511e8`. App `5934a54`, which research names, touched
  `tests/test_py32_flash_map_host.py` + `tests/test_scan_paths_resolve.py` — neither is that test.
- **Not a weakened assertion.** The gate's subject — that a missing scan target **raises** rather
  than skipping — is still hard-asserted wherever the premise holds. What was scoped is the
  *environment premise* (`META_PRESENT`), which Phase 129 had written as a bare `assert META_PRESENT`.
  The companion `test_absent_meta_claim_can_never_be_false` closes the abuse path by construction.

So the item is **discharged as a research-record correction, not as work** — which is why the third
option was taken rather than either of the first two. `81fa53c` is confirmed present in app history
and stays latent (`main` has never been merged in any of the three repos); the criterion for it is
*negative* and checked mechanically by recipe leg 1.

---

## Claude's Discretion

All seven areas, hence all eighteen decisions (D-01 through D-18). The operator answered "You decide"
to both question sets. The three carrying the most residual judgement — flagged in CONTEXT.md as the
first to revisit on new facts — are the no-canary rejection, the single-dispatch choice, and the
`mypy<3` bound.

One boundary was drawn on the delegation rather than exercised: **the py3.9 drop was deliberately not
taken**, on the grounds that delegated implementation discretion does not extend to changing a
published package's support contract.

## Deferred Ideas

- Drop Python 3.9 support (or add a py3.9 CI matrix leg) — needs an operator decision; filed as its
  own backlog item.
- The `eprom_operations.py` `[union-attr]` ring-fence — 10 errors, one root cause; decide at
  Phase 132's scoping, since CI can be green at watermark 35 without opening it.
- `gh#20` (AT28C256 `dev test` FAIL) — triage before or with Phase 134's leg.
- `_HANDLER_FUNCTION_NAMES` additions — Phase 133/134; prefer `chip_test.py`, which is scanned in
  full.

**Todos:** 9 matched, none folded. Eight are keyword noise against a host-only gate phase;
`gh12-followup-after-dev-sdp-retirement` is already owned by Phase 137 (CLOSE-05/06) and is not
foldable here — `dev sdp` still exists until Phase 132.
