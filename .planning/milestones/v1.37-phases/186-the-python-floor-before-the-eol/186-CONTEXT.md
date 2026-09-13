# Phase 186: The Python Floor, Before the EOL - Context

**Gathered:** 2026-09-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the three Python-version settings in `firestarter_app/pyproject.toml` — `requires-python`,
`[tool.ruff] target-version`, and `[tool.mypy] python_version` — agree on **3.11**, prove that floor in a
py3.11 environment rather than the devcontainer's 3.12, install a fail-closed check that stops them
diverging again, and record the reasoning where the next person finds it. Ahead of Python 3.10's
2026-10-31 EOL, not under it.

**In scope:** the three settings and every surface that co-states the floor (classifiers, the runtime guard
string, both `STACK.md` files, the falsified prose comments); the lint churn that raising ruff's target
exposes; a four-way agreement gate; one rationale note; one successor backlog item.

**Not in scope:** any behavioural change to the CLI; firmware (untouched — this phase is host-only); a
release or version bump (operator-gated, milestone-close work); broadening ruff's `select` beyond
`["E","F","I","UP"]`; adopting a second type-checker.

</domain>

<decisions>
## Implementation Decisions

### Floor direction and landing version

- **D-01:** **The floor is raised to 3.11.** `requires-python = ">=3.11"`, `[tool.ruff] target-version =
  "py311"`, `[tool.mypy] python_version = "3.11"` — all three move together. This resolves FLOOR-01 in the
  raise direction and closes the question Phase 131 D-13 explicitly deferred to the operator ("dropping it
  is a published-metadata breaking change on a live PyPI package, an operator decision, not this phase's to
  make"). — **Reversibility:** one-way — `requires-python` is published package metadata on a live PyPI
  project; once a release carries `>=3.11`, lowering it again does not un-publish the releases that
  advertised the higher floor, and pip's resolver behaviour for 3.9/3.10 users is already changed by the
  first upload.

- **D-02:** **3.11 was chosen against three alternatives, each rejected on a measured ground.** Recorded so
  no later phase re-derives it:
  - **3.10 (the minimum move)** — rejected: 3.10 EOLs 2026-10-31, so the floor would be end-of-life on the
    day it lands, and CI still would not test at it. Re-fires backlog 999.27 immediately.
  - **Hold 3.9** — rejected: measured, `mypy.defaults.PYTHON3_VERSION_MIN` is `(3, 10)` in the installed
    mypy 2.3.1, so **mypy cannot target 3.9 at all** under the standing `mypy>=2.1.0,<3` pin (set by
    Phase 131 D-14 for the watermark regexes). Holding 3.9 would require abandoning that pin or adopting a
    second checker. Python 3.9 itself EOL'd 2025-10-31 — the advertised floor is already a dead runtime.
  - **3.12** — rejected: CI runs 3.11, so 3.12 forces a CI change too and drops 3.11 users who are on a
    still-supported runtime.
  3.11 is the version CI already runs, so the floor becomes **proven rather than advertised**; it is what
  `tools/catalog/` already needs (`tomllib`); and it EOLs 2027-10, buying ~13 months rather than 7 weeks.

- **D-03:** **The classifier list becomes 3.11 and 3.12 only.** `Programming Language :: Python :: 3.9` and
  `:: 3.10` are removed to match the floor. 3.12 is kept because the devcontainer runs it daily and the
  suite passes there. 3.13 is **not** added — nothing tests it, and adding it would replace a false floor
  claim with a fresh unproven ceiling claim, which is the exact defect shape this milestone exists to
  remove.

### Proving it at the floor

- **D-04:** **A fail-closed check asserts all four floor statements name the same version** —
  `requires-python`, `[tool.ruff] target-version`, `[tool.mypy] python_version`, and the `python-version`
  pinned in `firestarter_app/.github/workflows/ci.yml`. Including CI is deliberate: it is the only clause
  that catches CI later moving to 3.12 and silently leaving the floor untested again, which is the exact
  mechanism that let this divergence survive from 2026-05-27 to now. This mirrors CLAIM-09's own
  reasoning — "nothing detected any of the above; this is what stops it recurring".
  Rejected: gating pyproject's three only (simpler, no YAML read, but blind to CI drift); and relying on
  Phase 131's GATE-01 returncode-before-regex ordering, which catches mypy *rejecting* a value, not
  `requires-python` drifting away from a value mypy happily accepts.

- **D-05:** **Watermark policy: ratchet down, fix a rise.** Re-measure the mypy error count at
  `python_version = "3.11"`. If it drops below the current `# mypy_error_watermark = 35`, lower the
  watermark to the measured value — `check_mypy_watermark.py`'s own INFO message invites exactly this, and
  its completeness clauses (`MIN_CHECKED_SOURCE_FILES = 120`) are the evidence that licenses it. If it
  rises, **fix the new errors; do not raise the watermark.** Absorbing errors a deliberate change
  introduced is the dishonesty this milestone exists to remove.

- **D-06 [informational]:** **999.27's instruction to re-verify `_FOUND_RE` / `_CLEAN_RE` does not apply here.** That
  instruction was written for a **mypy upgrade**; this phase moves only `python_version`, not the mypy
  version, so mypy's summary-line output format is unchanged. Settled at discussion time so no plan spends
  a task on it. (If a plan *does* bump mypy for an unrelated reason, the instruction re-arms.)

### Where the reasoning is recorded

- **D-07:** **Rationale lives in `.planning/notes/python-floor-decision.md`** (meta repo), matching all 29
  existing rationale notes and the citation style the milestone already uses (CLAIM-08 →
  `notes/catalog-sync-check-retirement.md`). **`firestarter_app/.planning/codebase/STACK.md` gets its
  corrected 3.11 claim plus a one-line pointer to that note**, so the app-repo editor — the person who next
  touches `pyproject.toml` and who does not have the meta repo's `.planning/notes/` — still finds it.
  Rejected: notes-only (invisible to the app-repo reader); app-repo-only (breaks the pattern the ROADMAP
  cites into); the prom wiki (no local clone, page creation is an operator-only web-UI step, and **no
  automated wiki guard has existed since 2026-09-02**, so it cannot be gated).

- **D-08:** **The note carries decision + evidence + a standing rule + a successor backlog item.** The rule
  must be applicable without re-deriving it, in the shape: *the floor tracks the version CI runs; when
  mypy's minimum supported target rises above it, move all four statements together.* A successor backlog
  item is filed carrying the next date — **3.11 EOLs 2027-10-31**. Phase 131 D-13 filed 999.26/999.27
  exactly this way, which is the only reason this phase exists on schedule rather than as a surprise.

### Blast radius

- **D-09:** **The full ruff autofix is absorbed, as its own commit, separate from the config change.**
  Measured: `ruff check --target-version py39` is clean today; `--target-version py311` yields **182
  errors — 177 UP045 (`Optional[X]` → `X | None`), 2 UP017 (`datetime.timezone.utc` → `datetime.UTC`), 2
  UP035 (deprecated-import), 1 I001**; **179 auto-fixable**, 3 needing `--unsafe-fixes` or hand treatment.
  The 3 non-auto-fixable ones must be named and handled individually, not swept. Keeping the churn in a
  separate commit from the floor change keeps both reviewable.
  Rejected: adding `UP045` to `extend-ignore` to skip the 177-line sweep, and suppressing all three rules —
  both leave `target-version = "py311"` a nominal setting whose consequences are switched off, which is a
  claim-shaped defect in a claim-hygiene milestone. — **Reversibility:** costly — the annotation rewrite
  touches a large share of `firestarter/` and `tests/`; reverting means reverting the commit, not editing
  back by hand.

- **D-10:** **Falsified prose comments are deleted, never rewritten.** In `pyproject.toml`: the `py32`/pyusb
  note citing "this project's py39 floor" (`:63-66`, the falsifying sentence at `:65`), the ruff-lint note
  about "py39 bounds" (`:127`), and the 16-line `[tool.mypy]` block explaining why `python_version` is 3.10
  and why `requires-python` stays 3.9 (`:139-154`, immediately above `python_version` at `:155`).
  In `tests/test_py32_packaging.py`: the floor prose at `:44-45` and `:79` — note `:44-45` is
  **already false today**, asserting mypy `python_version = "3.9"`. Deletion (not rewriting) is what the
  standing hard rule permits: **no comments written into product source, ever, and a plan cannot override
  it.** The rationale has a home by D-07.
  **`# mypy_error_watermark = 35` is NOT a comment for this purpose** — `check_mypy_watermark.py:96` parses
  it as configuration. It stays, with its value set per D-05.

- **D-11:** **Mechanical surfaces decided here so no plan asks:**
  - `firestarter/main.py:33` — the runtime guard string `"Error: Firestarter requires Python 3.9 or
    higher."` becomes 3.11. It is user-facing behaviour, not a comment.
  - `firestarter/cli_handlers.py:1814` — `# noqa: UP006 (python3.9 compat)` is resolved by the D-09 sweep,
    not preserved.
  - `.planning/codebase/STACK.md` (meta, ~:193, :203, :256) — the three "Python 3.9+" claims corrected.
  - `firestarter_app/.planning/codebase/STACK.md` (~:7, :12, :57) — corrected, plus the D-07 pointer.
  - `tools/check_mypy_watermark.py:68` and `tests/test_check_mypy_watermark.py:106` contain mypy's own
    *"3.9 is not supported"* output as **test fixture text**. That is a fixture of a real mypy message, not
    a claim about this project's floor — **leave both unchanged.**
  - The agreement gate (D-04) reads every `python-version:` in the app's workflows, not just `ci.yml`'s
    primary job — `ci.yml` pins it twice (`ci` and `ci-py32`) and `beta-release.yml` once.

- **D-12:** **`requires-python` is the user-facing notice; the release wording is recorded for ship, not
  written now.** pip already refuses on 3.9/3.10 with *"requires a different Python: 3.10.x not in
  '>=3.11'"*, and PyPI displays the floor — the tool says it at the moment it matters, which is this
  milestone's own standard. The phase records a one-line release-note fragment in its SUMMARY so the
  operator's beta-release body carries it at close, where release wording is already operator-gated.
  Rejected: introducing a `CHANGELOG.md` (the repo has never had one; a new upkeep surface is a new
  capability, not a clarification of this phase) and saying nothing at all (leaves the operator to remember
  the break unaided at the next beta cut).

### Claude's Discretion

- Plan decomposition and commit boundaries, subject to D-09's separate-commit constraint.
- The agreement gate's implementation shape (a `tests/` test vs a `tools/check_*.py` invoked from CI) and
  how it reads `ci.yml` — a regex or a minimal parse; `pyyaml` is **not** a dependency this project carries
  and must not become one for this.
- The note's internal structure and prose.
- Exact wording of the `main.py` guard string beyond the version number.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The file under change
- `firestarter_app/pyproject.toml` — every one of the three floor settings, the classifier list, the
  falsified prose blocks (D-10), and the parsed `# mypy_error_watermark` line. `:12` `requires-python`,
  `:37` the 3.9 classifier, `:110` `target-version`, `:155` `python_version`.
- `firestarter_app/.github/workflows/ci.yml` — the fourth floor statement (`python-version: '3.11'`, pinned
  at `:53` and `:112`) and the gate steps the change must keep green: `ruff check`, `ruff format --check`,
  `python tools/check_mypy_watermark.py`, `pytest --cov-fail-under=70`.
- `firestarter_app/.github/workflows/beta-release.yml` — a third `python-version: '3.11'` pin (`:52`).

### Measuring at the floor
- `firestarter_app/tools/ci_replica_venv.sh` — builds the numpy-free py3.11 interpreter that makes a
  trustworthy local mypy count possible; read its header block before running it. Its sibling
  `firestarter_app/tools/ci_parity.sh` is the faithful CI mirror and must not absorb it (Phase 132 D-07).

### The gate being extended, and its rules
- `firestarter_app/tools/check_mypy_watermark.py` — watermark semantics for D-05: fails when
  `count > watermark` (`:214`), reads the watermark from the `# mypy_error_watermark` comment by regex
  (`:96`), and enforces `MIN_CHECKED_SOURCE_FILES = 120` (`:48`) as the completeness evidence that licenses
  lowering it.
- `firestarter_app/tests/test_check_mypy_watermark.py` — `:106` holds mypy's "3.9 is not supported" message
  as fixture text; D-11 says leave it.

### Requirements and milestone decisions
- `.planning/REQUIREMENTS.md` § FLOOR — FLOOR-01, FLOOR-02, FLOOR-03 verbatim; § Decisions D-2 (why FLOOR is
  in this milestone at all: the deadline, not the theme).
- `.planning/ROADMAP.md` § Phase 186 — the four success criteria, including criterion 2's explicit
  instruction to measure in py3.11 and not the devcontainer's 3.12.
- `.planning/ROADMAP.md` `:5610` and `:5630` — backlog stubs 999.26 and 999.27, both marked PROMOTED to this
  phase. 999.27 carries the treadmill description the D-08 standing rule replaces.
- `.planning/PROJECT.md` § Current Milestone → Four strands → FLOOR row, and D-2's full rationale.

### Precedent for the rationale note
- `.planning/notes/catalog-sync-check-retirement.md` — the shape this milestone already uses for "a decision
  plus the cause, recorded outside a commit message"; cited by CLAIM-08's own amendment.
- `.planning/notes/dispatch-invariant-retirement-verdict.md` — a second instance of the same pattern.

### Standing rules that constrain this phase
- `/workspaces/CLAUDE.md` § "Source code comments — hard rule" — governs D-10. Applies to everything under
  `firestarter_app/`, is not overridable by a plan, and forbids writing comments, not deleting them.
- `/workspaces/CLAUDE.md` § "Milestone close and branch protection" — `main` is protected in all three
  repos; this project's close targets `beta`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured facts (live, at discussion time — re-verify before relying on the numbers)

- `mypy.defaults.PYTHON3_VERSION_MIN == (3, 10)` in the installed **mypy 2.3.1**. This is what makes
  "restore 3.9 enforcement" unreachable under the `mypy>=2.1.0,<3` pin, and it is the load-bearing fact
  behind D-01.
- `ruff check --target-version py39 firestarter/ tests/` → **clean**.
  `ruff check --target-version py311 firestarter/ tests/` → **182 errors** (177 UP045, 2 UP017, 2 UP035,
  1 I001); **179 auto-fixable**, 3 needing `--unsafe-fixes`.
- No `match`/`case`, no runtime `X | Y` unions, and no 3.10+ typing constructs in the shipped
  `firestarter/` package — the package is syntactically 3.9-clean today. The floor raise is a **policy**
  change, not a repair of code that already broke the floor.
- `tomllib` (3.11+) is used in `firestarter_app/tools/catalog/codegen.py` and `codegen_vectors.py` —
  dev tooling, outside the wheel (`packages = ["firestarter"]`) and outside every CI gate. The new floor
  makes this consistent rather than tolerated.
- Currently-resolved runtime deps already exceed the advertised floor: `click` 8.3.3, `requests` 2.34.2 and
  `pytest` 9.1.1 all declare `Requires-Python >=3.10`. A py3.9 install today silently resolves an older,
  never-tested dependency set — a second, independent reason the `>=3.9` claim was not real.

### Established patterns this phase must follow

- **Watermark ratchet** — `check_mypy_watermark.py` is a ceiling gate with a completeness floor; its INFO
  message states the conditions under which the watermark may be lowered. D-05 follows them.
- **Fixture severance / re-anchoring care** — the sibling precedent is `size_baseline.json` (D-7 of this
  milestone): re-recording a baseline in place reddens tests that deliberately depend on the pre-change
  figures. The mypy watermark is a single integer in one comment with no frozen fixtures behind it, so that
  hazard does **not** apply here — but a plan that widens scope to other baselines inherits it.
- **Rationale in `.planning/notes/`, cited by the ROADMAP** — 29 existing files.

### Integration points

- `pyproject.toml` is the single file carrying three of the four floor statements; `ci.yml` carries the
  fourth. The agreement gate (D-04) is the new code connecting them.
- The gate needs a home consistent with the repo's existing shape: `firestarter_app/tests/` (inside ruff +
  mypy + pytest coverage) or `firestarter_app/tools/check_*.py` invoked as an explicit CI step. **Note
  `firestarter_app/tools/` is outside every CI gate — no mypy, no ruff check, no ruff format** — so a
  `tools/` placement gets the CI step but not the lint/type coverage.

### Verification environment (binding)

- **The devcontainer is Python 3.12 and masks app CI, which is 3.11-only.** This is proven, not
  theoretical — it has broken beta CI before. Success criterion 2 requires the type-check be measured at
  the chosen floor in a **py3.11** environment.
- **`firestarter_app/tools/ci_replica_venv.sh` already exists to do exactly this** and is the intended
  instrument — do not hand-roll a `uv venv` in its place. It builds and reuses a **numpy-free Python 3.11
  interpreter**, because the devcontainer's ambient `numpy` ships a `.pyi` stub using PEP-695 `type`
  statement syntax that mypy's configured target cannot parse; mypy aborts with exit 2 before checking a
  single project file, and `check_mypy_watermark.py` then correctly refuses to report a count. **Raising
  the target to 3.11 does not lift that wall** — PEP-695 `type` statements are 3.12 syntax — so the script
  stays necessary after this phase, and any plan that assumes the bump removes the need is wrong.
- It is deliberately **not** a leg of `tools/ci_parity.sh` (Phase 132 D-07) — sibling, never replacement.
  It also deliberately does not mirror the two codegen-drift gates, the two catalog-validity steps, the
  `firestarter --help` smoke step, or the `ci-py32` job; those still need CI or a separate local run.
- After an editable install into a fresh venv, print `firestarter.__file__` before trusting any result —
  an editable install does not follow a worktree.

</code_context>

<specifics>
## Specific Ideas

- The standing rule in D-08 should be written so it can be applied mechanically: *the floor tracks the
  version CI runs; when mypy's minimum supported target rises above it, move all four statements together.*
  The point of FLOOR-03's second sentence is that the next person does not re-derive this.
- D-09's 3 non-auto-fixable ruff findings must be enumerated by rule and location in the plan or SUMMARY,
  not folded silently into the autofix commit.
- The successor backlog item should carry **2027-10-31** (3.11 EOL) explicitly in its title or first line,
  the way 999.27 carried 2026-10-31 — that date is what made this phase land ahead of the deadline instead
  of under it.

</specifics>

<deferred>
## Deferred Ideas

- **Broadening ruff's `select` beyond `["E","F","I","UP"]`** — the pyproject comment notes B/SIM/C4 were
  deferred to "Phase 42" and never landed. Raising the target version invites re-opening it; that is its
  own phase, not this one.
- **Every `# noqa: BLE001` in `firestarter_app` is inert** because `select` is `[E,F,I,UP]`. Adjacent to
  D-09's sweep and deliberately untouched by it.
- **Adding a `CHANGELOG.md`** — rejected in D-12 as a new capability rather than a clarification. If the
  project later wants a user-facing release record, it is a phase of its own.
- **A 3.13 CI leg / claiming 3.13 support** — rejected in D-03 for lack of any test. Revisit when a 3.13
  leg actually exists.

### Reviewed Todos (not folded)

`todo.match-phase 186` returned **34 matches, none topical.** Every match scored on generic keyword overlap
(`phase`, `app`, `check`, `run`, `2026`) — the highest were firmware VPP checks, a `dev test` issue-filing
flag, and AT28C256 write-path failures. **None concerns the Python floor, packaging metadata, ruff, or
mypy.** Zero folded, and the scan is recorded here so a later phase does not re-run it expecting a signal.

</deferred>

---

*Phase: 186-the-python-floor-before-the-eol*
*Context gathered: 2026-09-11*
