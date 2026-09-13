# Phase 186: The Python Floor, Before the EOL - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-11
**Phase:** 186-the-python-floor-before-the-eol
**Areas discussed:** Floor direction + landing version, Proving it at the floor, Where the reasoning is recorded, Blast radius of the change

**Area selection:** all four offered areas were selected.

---

## Floor direction + landing version

### Q1 — Which direction, and which version does the floor land on?

| Option | Description | Selected |
|--------|-------------|----------|
| Raise to 3.11 (Recommended) | Equals the one version CI runs, so the floor becomes proven rather than advertised. `tools/catalog` already needs 3.11 (tomllib). EOLs 2027-10. Cost: breaking metadata change on PyPI. | ✓ |
| Raise to 3.10 (minimum move) | Matches what mypy already enforces, zero watermark churn, smallest diff — but EOL on the day it lands, and CI still would not test at it. | |
| Hold 3.9, move mypy off the pin | Keeps the published floor — but requires leaving `mypy>=2.1.0,<3` or a second checker; 3.9 EOL'd 2025-10-31. | |
| Raise to 3.12 | Matches the devcontainer, removing the masking trap — but forces a CI change and drops supported 3.11 users. | |

**User's choice:** Raise to 3.11
**Notes:** Decided against a live measurement presented at ask time: `mypy.defaults.PYTHON3_VERSION_MIN` is `(3, 10)` in the installed mypy 2.3.1, making the "hold 3.9" branch unreachable under the standing pin. Closes the operator decision Phase 131 D-13 explicitly deferred.

### Q2 — What should the classifier list claim?

| Option | Description | Selected |
|--------|-------------|----------|
| 3.11 and 3.12 only (Recommended) | Drop 3.9/3.10 to match the floor; keep 3.12 because the devcontainer exercises it daily. Two claims, both backed by something. | ✓ |
| 3.11 only — strictly what CI proves | Most literal reading of the milestone's discipline; understates reality and may read as "does not run on 3.12". | |
| 3.11, 3.12, 3.13 | Adds a current runtime — but nothing tests 3.13, replacing a false floor claim with a fresh unproven ceiling claim. | |
| Drop version classifiers entirely | `requires-python` becomes the single source of truth; loses PyPI faceting, unconventional. | |

**User's choice:** 3.11 and 3.12 only

**Continue check:** "Next area" — ruff `target-version = "py311"` and mypy `python_version = "3.11"` were taken as mechanical consequences and decided without asking.

---

## Proving it at the floor

### Q1 — Install a fail-closed agreement check, or rely on the values coinciding?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — gate all four, incl. CI (Recommended) | Asserts `requires-python`, ruff `target-version`, mypy `python_version` and `ci.yml`'s `python-version` all name 3.11. Only option that catches CI drifting off the floor later. Costs a regex read of `ci.yml`. | ✓ |
| Yes — but pyproject's three only | Simplest (tomllib is stdlib at the new floor); catches the exact divergence that produced this phase but is blind to CI moving to 3.12. | |
| No gate — rely on GATE-01 | Phase 131's returncode-before-regex ordering catches mypy *rejecting* a value — not `requires-python` drifting from a value mypy accepts, which is how this survived since 2026-05-27. | |

**User's choice:** Gate all four, including CI
**Notes:** Follows CLAIM-09's stated reasoning in the same milestone — "nothing detected any of the above; this is what stops it recurring".

### Q2 — Watermark policy for the 3.10 → 3.11 mypy target move

| Option | Description | Selected |
|--------|-------------|----------|
| Ratchet down; fix a rise (Recommended) | Lower the watermark if the count drops (the tool's own INFO message invites it); if it rises, fix the errors rather than raise the watermark. | ✓ |
| Re-measure and record, change nothing | Keeps the diff to the floor alone; leaves a drop unbanked and the gate looser than reality. | |
| Ratchet down; allow a raise if justified | Pragmatic if 3.11's stubs are stricter in unrelated ways — but hands the phase an escape hatch from its own gate. | |

**User's choice:** Ratchet down; fix a rise
**Notes:** Raised and settled without a question — 999.27's instruction to re-verify `_FOUND_RE` / `_CLEAN_RE` was written for a **mypy upgrade**, not a `python_version` move, so mypy's output format is unchanged and no plan task is needed for it.

**Continue check:** "Next area".

---

## Where the reasoning is recorded

### Q1 — Where does the floor reasoning live?

| Option | Description | Selected |
|--------|-------------|----------|
| notes/ + pointer in app STACK.md (Recommended) | Full rationale in `.planning/notes/python-floor-decision.md`; the app's `.planning/codebase/STACK.md` gets the corrected 3.11 claim plus a pointer. Covers the meta-repo planner and the app-repo editor. | ✓ |
| `.planning/notes/` only | Consistent with all 29 precedents; but an app-repo-only reader never sees it — and that is the person who next edits the value. | |
| App repo only | Closest to FLOOR-03's literal wording; breaks the pattern the ROADMAP cites into. | |
| The prom wiki | Most discoverable externally — but no local clone, operator-only page creation, and no automated wiki guard since 2026-09-02, so it cannot be gated. | |

**User's choice:** notes/ + pointer in the app's STACK.md
**Notes:** Context given at ask time — a comment beside `python_version` is the obvious spot and is ruled out by the standing hard rule against comments in product source.

### Q2 — What must that note carry?

| Option | Description | Selected |
|--------|-------------|----------|
| Decision + evidence + standing rule + successor backlog (Recommended) | Adds a rule applicable without re-deriving it, and files a successor item carrying 3.11's 2027-10-31 EOL. Phase 131 D-13 filed 999.26/999.27 this way, which is why this phase is on schedule. | ✓ |
| Decision + evidence + standing rule | Rule written down, nothing on a tracker surfaces it. | |
| Decision + evidence only | Satisfies FLOOR-03's literal text but leaves the next person to re-derive — the outcome its second sentence asks to prevent. | |

**User's choice:** Decision + evidence + standing rule + successor backlog item

**Continue check:** "Next area".

---

## Blast radius of the change

### Q1 — How does the phase handle the lint churn raising ruff to py311 exposes?

Measured and presented at ask time: `ruff check --target-version py39 firestarter/ tests/` is clean; `--target-version py311` yields **182 errors** (177 UP045, 2 UP017, 2 UP035, 1 I001), **179 auto-fixable**.

| Option | Description | Selected |
|--------|-------------|----------|
| Absorb the full autofix (Recommended) | `ruff check --fix` + `ruff format` as its own isolated commit; the 3 non-auto-fixable named and handled by hand. Large but machine-generated diff, no standing suppression. | ✓ |
| Fix the real ones, defer UP045 | Take the 5 genuine fixes, `extend-ignore` UP045's 177-line sweep. Smaller phase; costs a standing suppression. | |
| Suppress UP045/UP017/UP035 | Smallest possible phase — but makes `target-version = "py311"` a nominal setting with its consequences switched off. | |

**User's choice:** Absorb the full autofix

### Q2 — What happens to the prose comments the change falsifies?

| Option | Description | Selected |
|--------|-------------|----------|
| Delete the prose; rationale lives in the note (Recommended) | Strip the falsified blocks in `pyproject.toml` and `test_py32_packaging.py`, keeping the parsed `# mypy_error_watermark` line. Complies with the hard rule (delete, never rewrite). | ✓ |
| Delete only what became false | Preserves still-true context; leaves a half-commented file and a per-sentence true/false judgement where stale claims return. | |
| Leave them, change only the values | Smallest diff; produces a file whose comments contradict its own values — the defect the CLAIM strand exists to remove. | |

**User's choice:** Delete the prose
**Notes:** Flagged at ask time that `tests/test_py32_packaging.py:44-45` is *already* false today, asserting mypy `python_version = "3.9"`.

### Q3 — How is the floor raise communicated to users on 3.9/3.10?

| Option | Description | Selected |
|--------|-------------|----------|
| requires-python is the notice; record it for ship (Recommended) | pip already refuses with a clear message and PyPI shows the floor; a one-line release-note fragment goes in the SUMMARY for the operator's beta-release body at close. | ✓ |
| Add a CHANGELOG.md with this entry | Creates a durable user-facing record the repo lacks — but is a new capability and a new upkeep surface. | |
| Nothing user-facing | Lightest; leaves the operator to remember the break unaided at the next beta cut. | |

**User's choice:** `requires-python` is the notice; record the wording for ship

**Continue check:** "I'm ready for context".

---

## Claude's Discretion

- Plan decomposition and commit boundaries, subject to the separate-commit constraint on the ruff sweep.
- The agreement gate's implementation shape (`tests/` test vs `tools/check_*.py` CI step) and how it reads `ci.yml` — regex or minimal parse; `pyyaml` is not a dependency and must not become one.
- The rationale note's internal structure and prose.
- Exact wording of the `main.py` runtime guard string beyond the version number.

## Decided without asking (mechanical consequences, recorded for audit)

- ruff `target-version = "py311"`, mypy `python_version = "3.11"`.
- `firestarter/main.py:33`'s runtime guard string moves to 3.11.
- Both `STACK.md` files corrected (meta `:193`, `:203`, `:256`; app `:7`, `:12`, `:57`).
- `tools/check_mypy_watermark.py:68` and `tests/test_check_mypy_watermark.py:106` left unchanged — they hold mypy's own "3.9 is not supported" output as fixture text, not a claim about this project's floor.
- The agreement gate reads every `python-version:` in the app's workflows (`ci.yml` ×2, `beta-release.yml` ×1).
- 999.27's `_FOUND_RE` / `_CLEAN_RE` re-verification does not apply (no mypy upgrade here).

## Deferred Ideas

- Broadening ruff's `select` beyond `["E","F","I","UP"]` (B/SIM/C4, deferred since "Phase 42") — its own phase.
- The inert `# noqa: BLE001` suppressions across `firestarter_app` — adjacent to the sweep, deliberately untouched.
- Adding a `CHANGELOG.md` — rejected here as a new capability; its own phase if wanted.
- Claiming or testing 3.13 — revisit when a 3.13 CI leg exists.

## Todo cross-reference

`todo.match-phase 186` returned 34 matches, all keyword noise (`phase`, `app`, `check`, `run`, `2026`); none concerns the Python floor, packaging metadata, ruff or mypy. **Zero folded, zero deferred-with-relevance.**
