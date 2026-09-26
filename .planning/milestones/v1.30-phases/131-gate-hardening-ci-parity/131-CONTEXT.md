# Phase 131: Gate Hardening & CI Parity - Context

**Gathered:** 2026-08-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Make `firestarter_app`'s two fail-open gates able to actually fail, add a derived
`sdp_capability` count gate, and author the CI-parity recipe every later v1.30 phase reuses.

**In scope:** `tools/check_mypy_watermark.py` (fail-closed rewrite + its first-ever paired pytest),
`pyproject.toml`'s `[tool.mypy]` `python_version` and the `[test]` mypy pin, a derived-subset test
over `tools/check_devtest_orchestrator.py`'s `_HANDLER_FUNCTION_NAMES`, a 43/41/84 ALLOW/REFUSE/total
count gate extending the existing `sdp_capability` test modules, a committed runnable CI-parity
script, and one operator-run `gh workflow run ci.yml` dispatch recorded as the number Phase 132
reconciles against.

**Out of scope — and load-bearing:**
- **Sets NO watermark.** The phase is deliberately count-independent; the `35` in `pyproject.toml`
  is not touched. Re-baselining belongs to Phase 132, *after* its `−6` deletion.
- **Deletes nothing.** `dev sdp` survives this phase intact.
- **Fixes no mypy errors.** Not one of the 69. Hardening the mechanism and discharging the debt are
  split on purpose — that split is what lets this phase come first.
- **Touches `firestarter` not at all.** Host-only milestone; no firmware change, no dual-repo
  lockstep, no `.hex` re-cut.
- **`eprom_operations.py`'s ring-fenced `[union-attr]` cluster is not opened.** CI can be green at
  watermark 35 without it (research A-2), so it is optional extra credit belonging to Phase 132's
  scoping, not a side effect of this phase.

</domain>

<decisions>
## Implementation Decisions

**Every decision below is Claude's discretion.** The operator was offered all seven gray areas and
delegated all seven ("You decide", both questions). They are grounded in measured research, not
preference, and each records *why* — so a later reader can overturn one on new facts rather than on
taste. The one thing delegation did **not** authorize is a change to the package's published
support contract (D-06a) — see that decision for why it was deliberately not taken.

### The gate's test seam (GATE-06)

- **D-01:** **No env-var seam in the production checker.** Split `count_mypy_errors()` into a pure
  `classify_mypy_result(returncode, output) -> int` plus a thin runner that does the
  `subprocess.run` and delegates. The four GATE-06 legs test the **pure classifier** against canned
  mypy output — no env var, no stdlib monkeypatching, no stub on `PATH`.

  *Why not research's suggested "env-override seam + fake-mypy stub":* the five committed checkers
  that use env seams override *scan targets* (which files to read), which is fail-closed-able —
  `os.environ.get(...)` with no default and `is not None` precedence means present-but-empty ⇒ zero
  targets ⇒ red. An env var that overrides the **mypy argv** is categorically different: it lets any
  caller substitute a program printing `Found 0 errors … (checked 120 source files)`. That is a
  bypass, added to the one gate whose entire sin was being bypassable — and it is the shape
  `firestarter/channel.py` forbids in its own docstring (*"Nothing here reads the environment"*),
  learned from `${sysenv.VAR}` failing OPEN on the firmware side.

  *Why not a stub earlier on `PATH`:* GATE-04 exists specifically to kill `PATH` resolution. A test
  depending on `PATH` would exercise the code path the fix removes.

- **D-02:** Three test layers, all four GATE-06 legs on the first:
  1. **Pure-classifier legs** (canned output, `pytest.raises(SystemExit)` + `.code`):
     truncated-run ⇒ **2**, config-rejection ⇒ **2**, over-watermark ⇒ **1**,
     below-coverage-floor ⇒ **2**.
  2. **One argv-proof leg** — monkeypatch `subprocess.run` *inside the checker's module namespace*
     and assert the argv is exactly `[sys.executable, "-m", "mypy", "firestarter/", "tests/"]`.
     This is GATE-04's positive, fail-provable proof. Monkeypatching a stdlib call in the module
     under test adds **no production seam**.
  3. **One end-to-end leg** — invoke `python3 tools/check_mypy_watermark.py` as a real subprocess
     against the real tree; assert exit ∈ {0,1,2} **and** that stdout carries the
     `mypy errors: N (watermark: M)` line. Proves the runner half is wired. **Do not assert a
     count** — it is environment-dependent (that dependence is this phase's whole subject).

- **D-03:** **A RED-preserving proof is a named acceptance criterion, not a nicety.** With the
  returncode-before-regex reordering reverted, the truncated-run leg must be *seen* to fail before
  the fix is re-applied. *"A pre-authored gate leg can be UNREACHABLE — RED proves nothing until
  seen to pass."* Read the failure reasons; do not assume them.

### Canary floor and the files floor (GATE-02, GATE-03)

- **D-04:** **No canary fixture module.** P-13 calls the canary *"the load-bearing one"*, so this is
  a deliberate rejection with reasons, not an oversight — and it must be recorded as such (Phase 137
  ledger, negative space):
  1. A canary module with deliberate type errors sits **inside the checked tree**, so it adds N
     errors to the real count — the exact number Phase 132 must drive to ≤35 and re-baseline. It
     would corrupt the watermark's meaning permanently, and the watermark is this milestone's
     central honesty artifact.
  2. Excluding the canary from the main run and checking it in a second mypy invocation proves only
     that a *second, differently-scoped* run works. It does not guard the real run.
  3. The abort mode the canary targets is already caught **structurally** by requiring the
     `(checked N source files)` clause: the truncated path emits `(errors prevented further
     checking)` and **no** `checked` clause (measured). Requiring the completion clause makes the
     truncated shape unparseable ⇒ exit 2 *even if a future mypy returns 1 on it* — strictly
     stronger than a canary, because it does not depend on the canary's errors surviving.
  4. `MIN_CHECKED_SOURCE_FILES` is the coverage assertion, which is the project's own repeated
     lesson: assert the **coverage** of the check, not just its verdict.

- **D-05:** **`MIN_CHECKED_SOURCE_FILES = 120`, literal, not derived.** A derived count (glob over
  `firestarter/**/*.py` + `tests/**/*.py`) is by construction always satisfied — it equals whatever
  is there — so it cannot catch a run that checked fewer files than the tree contains. GATE-03 fixes
  the value at 120 by requirement. Comment it as: *a floor to be raised when the tree grows, never
  lowered to accommodate a smaller run; if a legitimate deletion drops the tree below it, lower it
  in the same commit as that deletion, with the new measured number.*

  Verified safe against what follows: Phase 132 `git mv`s one module (count holds at 120);
  Phases 133/134/136 add modules (count rises). None lowers it.

  *Note the asymmetry with GATE-08/GATE-10, deliberately:* "derived" is right when the derivation is
  **independent** of the thing measured (GATE-08 derives the partition from the DB and compares it to
  `sdp_capability()`; GATE-10 derives referenced helpers from the AST and compares to a hand list).
  It is wrong when the derivation *is* the measurement, which is the file-floor case.

### The 43/41/84 count gate (GATE-08)

- **D-06:** **Both axes plus a change protocol** — three legs, added to the existing
  `tests/test_sdp_db_invariant.py` / `tests/test_sdp_table_parity.py`. **Do not create a third
  module.**
  1. **Derived parity, element-wise.** Recompute the partition from `chip_database.json` + the
     committed `flags` bit-15 decode and assert it equals what `sdp_capability()` computes **for
     each of the 84 `0x0D` chips** — not just the totals. Element-wise is what catches a single chip
     moving.
  2. **Committed literal triple `43 / 41 / 84`**, asserted separately, with the measured side coming
     from the derivation. This is the leg that catches P-10's narrowing-for-convenience: a chip
     moved ALLOW→REFUSE reddens it, and the diff that greens it is a **visible edit to a named
     constant**.
  3. **Change protocol**, as a comment on that constant and echoed in Phase 137's ledger: a chip may
     move ALLOW→REFUSE only with a **decode** reason (its `flags` bit changed, or the decode was
     wrong) — **never** with a test-outcome reason.

  *Why both:* parity-only passes when both sides drift together, which is exactly P-10's hole;
  literal-only does not pin the derivation source. Both is one module's worth of work.

### The CI-parity recipe (GATE-09)

- **D-07:** **A committed runnable script in the app repo — `firestarter_app/tools/ci_parity.sh`** —
  plus a short prose block in the phase record naming what each leg proves. Not a Makefile target
  (the app repo has no Makefile); not documentation-only (GATE-09 says *runnable*, and a doc-only
  recipe is what every later phase will silently skip). It lives in the app repo because every later
  phase invokes it with the submodule as its working directory, and because it is the repo whose CI
  it mirrors.

- **D-08:** Four legs, each printing a labelled banner and its own status; the script exits non-zero
  if any leg fails and prints a final summary. **It must not swallow leg failures.**
  1. `FIRESTARTER_FW_ROOT=$(mktemp -d) python3 -m pytest tests/ -q` — empty sibling root. The env
     var must be set in the **pytest process environment**, never monkeypatched: `tests/fw_presence.py:80`
     reads it at module scope.
  2. `python3 -m pytest tests/ -q` — sibling present.
  3. `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` — **exactly** CI's
     path set, neither wider nor narrower.
  4. `python3 tools/check_mypy_watermark.py`.

- **D-09:** **The no-board leg is evidence metadata, not a fifth leg.** A script cannot detach
  hardware, and requiring physical detachment on every invocation would make the recipe unused.
  So the script enumerates `/dev/ttyACM* /dev/ttyUSB*` and stamps `BOARD-ATTACHED: <list>` or
  `BOARD-ATTACHED: none` into its summary. A run with a board attached is still valid — it simply
  cannot claim the no-board leg. **The phase's acceptance requires at least one recorded run
  carrying `BOARD-ATTACHED: none`.**

- **D-10:** **`check_no_exists_proxy.py` is a one-time recorded confirmation, not a recipe leg.**
  The recipe's contract is *CI parity*, and `ci.yml` runs no such step; the checker's behaviour is
  already covered by `tests/test_check_no_exists_proxy.py`, which legs 1–2 run. Run it once in this
  phase and record `PASS` in the phase record — that discharges STATE.md's *"six modules shared it
  — worth confirming none survive"* for free, without making the recipe an unfaithful mirror.

### The real CI dispatch (GATE-07)

- **D-11:** **Exactly one dispatch, on the fork base `beta` @ `16a313a`, run by the operator.**

  *Why one, not two:* the purpose (research A-1 and the Gaps list) is to obtain the **current
  post-fork number the watermark is later set from** — a property of the fork base, settled by one
  run. A second post-hardening dispatch would show the hardened gate at `exit 1` on a 69-error
  tree — the same red, for the same reason. It buys nothing and costs an operator round-trip. If a
  later phase needs the hardened gate proven red-for-the-right-reason in CI, **Phase 132 gets it for
  free**: it is the phase that turns the gate green, so its own dispatch is the proof.

  *Why operator-run:* the standing rule holds — no `<automated>` block in any plan may contain
  `gh workflow run`, `git push`, `git merge` into beta, `git tag`, `gh release …` or `twine upload`.
  The dispatch stays **prose in `131-HANDOFF.md`**. No workflow edit is needed: `ci.yml` already
  carries `workflow_dispatch:` (Phase 127 D-01).

  *Sequencing:* the dispatch targets the **fork base**, so it depends on nothing in this phase and
  can be requested first or in parallel. No branch push is required. Confirmed safe — `ci.yml`'s
  `push` trigger is `branches: [main]` only, so nothing else fires.

- **D-12:** **Recorded in `131-CI-BASELINE.md`**, carrying: run id + URL, `gh run view <id>` step
  statuses, the **verbatim** `Found N errors in M files (checked K source files)` line, mypy's
  resolved version, and the Python version. The count is **read, never computed** (the v1.22 C-5
  discipline). The file must state explicitly that this number is **an input to Phase 132's
  watermark, not a Phase 131 claim**. If the measured number differs from research's 69, the
  **measured number wins** and the divergence is recorded, not reconciled away.

### The py3.9 floor and the mypy pin (GATE-05)

- **D-13:** **Keep `requires-python = ">=3.9"` and the 3.9 classifier. Do not drop 3.9. Do not add
  a py3.9 CI matrix leg.** Dropping is a **published-metadata breaking change** on a live PyPI
  package, orthogonal to all six of this milestone's items — and it is not a call delegation covers:
  "you decide" extends to implementation shape, not to the package's advertised support contract. A
  3.9 matrix leg is real recurring CI cost for a floor `[tool.ruff] target-version = "py39"` already
  carries at the syntax/idiom level.

  **Record the residual gap explicitly** (it is GATE-05's honest cost, and REQUIREMENTS.md already
  gestures at it): after `python_version = "3.10"`, **nothing type-checks against the floor the
  package still advertises** in two places. ruff catches py3.10-only *syntax*; **nothing** catches a
  py3.10+ **stdlib API** used on 3.9. The gap is real, is **not new** (it has existed since
  2026-05-27, because `python_version = "3.9"` was silently discarded and never once took effect),
  and its correct closure is one of the two options above. **File it as its own backlog item** so it
  is scheduled rather than acknowledged a second time.

  **Record the treadmill too:** Python **3.10 EOLs 2026-10-31**, ~3 months out, and a future mypy
  clamping to ≥3.11 re-fires this exact failure. GATE-01's reordering is what makes that arrive as a
  **red gate instead of a silent green** — that is the durable value of this phase, and it belongs
  in the comment.

- **D-14:** **Add an upper bound: `mypy>=2.1.0,<3` in the `[test]` extra.** The gate's
  discriminator is now a **regex over mypy's summary-line format** (GATE-02's `(checked N source
  files)` clause). A major-version bump is exactly where that format is licensed to change, and the
  failure would be `exit 2` on every run — a hard CI stop with a confusing message, from a tool
  nobody upgraded deliberately. `<3` is one token, costs nothing today (2.3.0 resolves), and makes
  the format dependency explicit. Comment it naming the regex that depends on it.

  *This is not the pinned venv research rejected* — that was reproducibility infrastructure (a
  second venv, an install step, a cache key). This is a compatibility bound on a parsed output
  contract.

### GATE-10 — the derived handler list

- **D-15:** **Implement as a test, not as a change to the checker.** Making
  `check_devtest_orchestrator.py` derive its own scan set at runtime would broaden what it scans,
  and the narrow allow-list is load-bearing for the gate staying green — `cli_handlers.py` has 10
  pre-existing legitimate `--force` flags on unrelated commands, so a whole-file scan is
  permanently red by design.

  The test derives, from the AST, every module-level function whose name starts with `_` **and** is
  referenced from `dev_test`'s body, and asserts that set is a **subset of**
  `_HANDLER_FUNCTION_NAMES`, naming any omission. **Direction matters:** this new leg proves *every
  referenced helper is listed*; the existing
  `test_handler_function_names_all_resolve_to_real_callables` proves *every listed name is real*.
  Together they are bidirectional, converting an additive fail-open into an additive fail-closed.

- **D-16:** **Forward-looking note for Phases 133/134, not this phase's work:** prefer putting the
  new leg's logic in `chip_test.py`, which `_scan_file` scans in **FULL**, keeping the handler thin.
  That sidesteps the allow-list entirely and is the better architectural placement anyway.

### Adjacent fail-open debt

- **D-17:** **`test_present_root_with_missing_target_raises_not_skips` — do NOT act. Record the
  correction.** Research's operator-decision #7(a) and PITFALLS P-18 #4 are **wrong on both
  provenance and substance**, verified live this session:
  - **Wrong repo.** The test is at `firestarter/tests/test_flash_path_record_sync.py:694` — the
    **firmware** repo, which this milestone does not touch. Acting would breach the scope boundary
    the ROADMAP states three times. It is **not** in `firestarter_app`; a downstream agent must not
    go hunting for it there.
  - **Wrong commit.** The softening is firmware `1c511e8` (*"scope the meta-root premise leg to skip
    when no meta root exists"*). App `5934a54`, which research names, touched
    `tests/test_py32_flash_map_host.py` + `tests/test_scan_paths_resolve.py` — neither is that test.
  - **Not a weakened assertion.** Reading the code: the gate's own subject — that a missing scan
    target **raises** `MissingScanTargetError` rather than skipping — is **still hard-asserted**
    wherever the premise holds. What was scoped is the **environment premise** (`META_PRESENT`),
    which Phase 129 had written as a bare `assert META_PRESENT`, hard-asserting an environment fact
    into a failure. And the companion `test_absent_meta_claim_can_never_be_false` above it makes a
    false absence claim impossible by construction, closing the abuse path.

  So this "latent carry worth a decision at scoping" is **discharged as a correction to the research
  record, not as work**. Phase 137's ledger carries it as a negative-space row. STATE.md's own
  phrasing (*"softened a Phase-129-authored hard assert to a skip — a defect-class change"*) is the
  source of the mischaracterisation and is itself imprecise.

- **D-18:** **`81fa53c` — record, do not act.** Verified present in the app repo
  (`fix(122-07): skip firmware-checkout-dependent clean-source tests in standalone CI`, adding
  `skipif` guards to `test_check_is_memory_cmd_no_ifdef.py` and `test_check_no_log_in_sdp_window.py`).
  `main` has never been merged in any of the three repos, so the carry stays latent and acting now
  would be work against a merge that is not happening. Because this phase works in
  `check_no_log_in_sdp_window.py`'s neighbourhood, the criterion is **negative**: any test this
  phase adds must pass under recipe leg 1 (empty sibling root). That is checked mechanically by the
  leg, not asserted in prose.

### Claude's Discretion

All of D-01 through D-18 above. The operator delegated both question sets in full. Three carry more
residual judgement than the rest and are the ones to revisit first if a downstream agent finds new
facts:

- **The no-canary rejection** contradicts P-13's own "load-bearing" framing. The reasoning is that
  the completion-clause requirement dominates it *and* that a canary corrupts the watermark — but if
  a planner finds an abort mode that emits a valid `(checked N source files)` clause with a truncated
  file set, that rejection should be reopened.
- **The single-dispatch choice** assumes Phase 132's own dispatch will serve as the
  hardened-gate-in-CI proof. If Phase 132 is replanned without a dispatch, this phase owes a second
  run.
- **The `mypy<3` bound** is a judgement about where output format is licensed to change. Harmless if
  wrong; revisit if it ever blocks a needed upgrade.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

ROADMAP.md carries no `Canonical refs:` line for this phase; this list is accumulated from the
ROADMAP entry body, REQUIREMENTS.md, and the codebase scout.

### Milestone contract (read first)
- `.planning/REQUIREMENTS.md` §"Gate Hardening & CI Parity (GATE)" — GATE-01…GATE-10 verbatim, plus
  the **Evidence Ceiling** at the top, which must not be smoothed over in any artifact.
- `.planning/ROADMAP.md` §"Phase 131: Gate Hardening & CI Parity" (line 265) — goal, the 5 success
  criteria, and the cross-cutting rule to **name the exact requirement IDs each plan may mark
  Complete, at dispatch** (executors did this prematurely 4× in Phase 116).
- `.planning/ROADMAP.md` §"v1.30 — SDP Surface Retirement…" (line 151) — the dependency spine, and
  the two narrowings that must survive into every phase's artifacts.

### The fix, specified line by line (why this phase is research-SKIP)
- `.planning/research/STACK.md` §1 (lines 25–248) — the whole mechanism. §1b: why
  `python_version = "3.9"` has **never** taken effect and mypy clamps to **3.10** (branch-reachability
  probe). §1c: the numpy stub chain, a devcontainer-only artifact absent from CI. §1d: the two
  distinct failures side by side. §1e: the one-line bug (regex before returncode) plus two secondary
  defects. §1f: FIX-1/FIX-2/FIX-3 with the code, the rejected alternatives, and **"Do NOT switch the
  gate to `mypy --output json`"** (JSON mode emits no summary line, discarding the very signal
  GATE-02/GATE-03 depend on).
- `.planning/research/PITFALLS.md` §P-13 (line 501) — reproduced locally with exact output; the five
  mechanical preventions (D-04 rejects the fifth, with reasons); and the two discharge traps: **do
  not lower the watermark to make the gate green**, and **fix the gate before counting**.
- `.planning/research/PITFALLS.md` §P-14 (line 545) — the fail-open idiom inventory, including which
  patterns to **copy** (explicit non-glob target lists; env seams read with no default and
  `is not None` precedence) and which this milestone's own new gates would inherit.
- `.planning/research/PITFALLS.md` §P-07 (line 287) — GATE-10's derived-subset fix and why the
  narrow allow-list must stay narrow.
- `.planning/research/PITFALLS.md` §P-10 (line 389) — GATE-08; the missing gate is against
  **narrowing** for convenience, not widening.
- `.planning/research/PITFALLS.md` §P-18 (line 647) — GATE-09's recipe verbatim, and the three
  defect classes this devcontainer cannot see. **⚠ Its item 4 is corrected by D-17 — read D-17 before
  acting on it.**
- `.planning/research/SUMMARY.md` §A-1 (line 244) — the CI-redness adjudication and the exact
  dispatch commands. §A-2 (line 272) — the 69-error arithmetic and the measured path to green
  **without** touching the `eprom_operations.py` ring-fence. §"Phase 131" (line 683) — the delivery
  list. §"Operator Decisions Needed" (line 854) — items 2, 3, 7 land here; **item 7(a) is corrected
  by D-17**. §"Gaps to Address" (line 919) — the current post-fork count is GATE-07's job.

### Milestone design intent
- `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md` — full design, traps, accepted
  costs. Background for why the gate work precedes everything, not a spec for this phase.

### Live code this phase edits or extends
- `firestarter_app/tools/check_mypy_watermark.py` — 96 lines. `count_mypy_errors()` at `:43-73` is
  the subject; the bare `["mypy", …]` argv is at `:56`; the regex-before-returncode ordering is
  `:62-65`.
- `firestarter_app/pyproject.toml` — `requires-python` `:12`; `mypy>=2.1.0` `:76`;
  `[tool.ruff] target-version = "py39"` `:101-102`; `extend-exclude = ["tests/golden", "tests/fixtures"]`
  `:113`; `[tool.mypy]` `:130`; the false comment on `python_version` `:131`; the watermark comment
  `:135`; the `follow_imports = "silent"` ring-fence block near `:170`.
- `firestarter_app/.github/workflows/ci.yml` — the gate step at `:69-70`, `workflow_dispatch:` at
  `:25`, `push: branches: [main]` at `:9-11`, Python **3.11** at `:33-36`, and the exact ruff path
  set at `:63-67` that recipe leg 3 must mirror.
- `firestarter_app/tools/check_devtest_orchestrator.py` — `_HANDLER_FUNCTION_NAMES` (9 names) and the
  comment above it already stating that every future helper MUST be listed.
- `firestarter_app/firestarter/sdp_capability.py` — the fail-closed allow-set. **Re-measure its
  entry-point line at execution** (research read 266 vs 272; cosmetic, but do not trust either).
- `firestarter_app/tools/check_sdp_capability_invariants.py` — states the 43/41/84 provenance
  (`infoic.xml` `INFOIC2PLUS` `flags` bit 15) at `:12`; gates **widening** today.
- `firestarter_app/tests/test_sdp_db_invariant.py` (the 84-count assertion at `:81-93`) and
  `firestarter_app/tests/test_sdp_table_parity.py` — **extend these**, per D-06.
- `firestarter_app/tests/fw_presence.py` — `FIRESTARTER_FW_ROOT` at `:80`, read at **module scope**;
  `MissingScanTargetError` at `:105`; the import-time-binding warning at `:37-42`.
- `firestarter_app/tools/check_no_exists_proxy.py` — run once, record `PASS` (D-10).

### Pattern precedents to copy
- `firestarter_app/tests/test_check_devtest_orchestrator.py` — the
  `FIRESTARTER_DEVTEST_SRC`/`FIRESTARTER_DEVTEST_HANDLER` seam shape and
  `test_handler_function_names_all_resolve_to_real_callables`, whose counterpart D-14 adds.
- `firestarter_app/tests/test_check_no_exists_proxy.py`, `test_check_sdp_capability.py`,
  `test_check_no_community_support_status_write.py` — the house `test_check_*` shape, including their
  `*_fails_closed_on_missing_target` legs.
- `firestarter/tests/test_flash_path_record_sync.py:694` — **read-only, for D-17's correction.** Do
  not edit; the firmware repo is out of scope this milestone.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- **Six committed `tools/check_*.py` checkers with paired `tests/test_check_*.py` modules** —
  `check_dispatch`, `check_no_log_in_sdp_window`, `check_no_exists_proxy`,
  `check_no_community_support_status_write`, `check_devtest_orchestrator`, `check_sdp_capability`.
  `check_mypy_watermark.py` is the **only** checker with no paired test; GATE-06 closes that. The
  house shape is already established — follow it rather than inventing one.
- **`tests/fixtures/` is `extend-exclude`d from ruff** (`pyproject.toml:113`), which is exactly what
  makes planted-violation fixtures and canned-output files viable there.
- **`tests/fw_presence.py`** already provides `FW_ROOT`, `FW_REPO_PRESENT`, `fw_path`,
  `MissingScanTargetError` and the `FIRESTARTER_FW_ROOT` seam recipe leg 1 needs.
- **`tests/test_skip_census.py`** is a free ally: `ALLOWED_SKIP_REASONS` fails **closed** on any new
  skip reason, `test_census_child_run_is_live` prevents a collection regression from silencing it,
  and `test_parser_recognises_a_real_skip` prevents a dead parser making it vacuous. Do not add an
  entry casually — and note this phase should need **no** new skip reason at all.

### Established patterns
- **Explicit non-glob default target lists** in every checker (never a tree-walk), which is what
  keeps `fixtures/` unreachable from the real scan. Copy this.
- **Env seams read with `os.environ.get(...)` and NO default, precedence tested with `is not None`**
  — so present-but-empty ⇒ zero targets ⇒ red, never a silent fallback. Note `fw_presence.py:80` is
  the deliberate exception: it *does* take a default, because a root path needs one for normal
  operation.
- **Import-time binding is pervasive and treacherous** — `FW_ROOT`, `FW_REPO_PRESENT`,
  `requires_fw`, `_BOARD_CHOICES` and `channel.is_prerelease_build()`'s effect on option
  construction are all frozen at import/collection. `monkeypatch.setenv` runs **after** and has no
  effect. Anything simulating a different environment must use a **subprocess**.
- **`_HERE`-style path resolution is a live trap** — `check_permitted_claims.py`'s `_DEFAULT_TARGETS`
  resolving against the wrong phase dir scanned nothing and exited 0 on v1.23's only outward-facing
  gate. Any new default target list must resolve **locally** and be proven to.

### Integration points
- `ci.yml`'s `ci` job step `mypy type check (watermark gate)` (`:70`) is the only consumer of the
  hardened checker. **The primary `ci` job is currently RED and will stay RED after this phase** —
  by design: this phase hardens the mechanism and fixes zero errors. Phase 132 turns it green. Any
  artifact claiming otherwise is an overclaim.
- Recipe leg 3 must mirror `ci.yml:63-67`'s path set **exactly** — `firestarter/ tests/`, neither
  wider nor narrower. ruff *is* correctly CI-scoped today; the failure mode is running it locally at
  a different scope.

### Measured live this session (re-verify at plan time; do not inherit)
- **The fail-open premise reproduces exactly**, 2026-08-03, in this devcontainer:
  `python3 tools/check_mypy_watermark.py` → `mypy errors: 1 (watermark: 35)` /
  `INFO: 1 errors — 34 below watermark. Lower watermark in pyproject.toml.` / **exit 0**. The gate
  invites you to bake a broken run's number in permanently.
- `firestarter_app` is on **`beta` @ `16a313a`** — the stated fork base. **The milestone branch does
  not exist yet**; create it before dispatching any executor into the sub-repo.
- Untracked in `firestarter_app`: `.coverage`, `.planning/config.json`, `SECURITY.md`,
  `write_test_port.sh`, plus a modified `.gitignore`. None are this phase's business; do not sweep
  them, and do not let them into a commit.
- `firestarter/tests/test_flash_path_record_sync.py:694` exists and is **premise-scoped, not
  weakened** (D-17).
- `81fa53c` is present in the app repo's history (D-18).

</code_context>

<specifics>
## Specific Ideas

- **The phase's durable value, stated for the record:** Python **3.10 EOLs 2026-10-31**, ~3 months
  out. A future mypy clamping its minimum target to ≥3.11 re-fires this exact failure. What this
  phase buys is that the re-fire arrives as a **red gate** rather than a silent green. That sentence
  belongs in the `python_version` comment, not only in the planning record.
- **Ordering is non-negotiable and comes from P-13:** harden → measure in a CI-equivalent env → fix
  → re-measure → set watermark. This phase owns *harden* and *measure*; Phase 132 owns the rest. A
  count measured with the broken gate is meaningless.
- **The gate must never again invite lowering the watermark as the remedy.** The current `INFO:`
  message does exactly that. Reword it so the suggestion is conditional on a *complete* run — the
  message is part of the fail-open, not decoration.

</specifics>

<deferred>
## Deferred Ideas

- **Drop Python 3.9 support** (`requires-python = ">=3.10"`, drop the 3.9 classifier) — EOL
  2025-10-31, research calls it *"defensible and arguably overdue."* A published-metadata breaking
  change requiring an operator decision; **file as its own backlog item** (D-13). The alternative
  closure is a py3.9 CI matrix leg. Either way, after GATE-05 nothing type-checks against the
  advertised floor, and ruff's `py39` target covers syntax only — not stdlib APIs.
- **The `eprom_operations.py` `[union-attr]` ring-fence** — 10 errors, one root cause, one fix,
  deliberately outside the strict island per the **v1.8-era** ring-fence decision (*"GATE-1.8d
  read-path ring-fence, deferred to v1.9 post-RCA"*, visible as `pyproject.toml`'s
  `follow_imports = "silent"` override block). This milestone opens that file anyway (Phase 132's `sdp_lock`/`sdp_unlock`
  survivors and the R-7 comment corrections), so decide it **deliberately at Phase 132's scoping**.
  Not this phase: CI can be green at watermark 35 without it (A-2).
- **`gh#20`** (AT28C256 `dev test` FAIL, open since 2026-07-30) — the first community `dev test`
  report on an SDP-capable `0x0D` part is a **failure**, and it is the live instance of the "lock a
  part whose baseline write never worked" hazard. Triage before or with Phase 134's leg, not here.
- **`_HANDLER_FUNCTION_NAMES` additions themselves** — Phase 133/134 add the helpers; D-15 only adds
  the gate that will catch them. Prefer `chip_test.py` (scanned in FULL) over the handler (D-16).
- **Restoring `test_present_root_with_missing_target_raises_not_skips`** — **not deferred, closed**:
  D-17 discharges it as a research-record correction. Recorded here only so a later reader does not
  re-open it as an unhandled carry.

### Reviewed todos (not folded)

`todo.match-phase 131` returned 9 matches; **none folded**. All are keyword-noise against a
host-only gate-hardening phase — six are firmware-area or firmware-subject items
(`skip-vpp-error-and-warning-checks…`, `prove-pio-dev-flag-fails-closed`,
`avrdude-mcu-detection-fallback`, `cobs-decoder-framelevel-deadline-wr01`, and the JP4/jumper item),
matching on generic tokens like "gate", "flag", "phase", "firmware".

The one substantive hit is **`gh12-followup-after-dev-sdp-retirement`** — already owned by
**Phase 137** (CLOSE-05/06) by requirement, behind a blocking operator wording-review gate. Not
foldable here: it describes a substitution that must already be true, and `dev sdp` still exists
until Phase 132.

</deferred>

---

*Phase: 131-Gate Hardening & CI Parity*
*Context gathered: 2026-08-03*
