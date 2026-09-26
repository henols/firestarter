# Phase 185: Records and Checks That Are Current - Context

**Gathered:** 2026-09-11
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase makes four records stop describing a tree that no longer exists, and nothing else:

1. **The firmware size baseline is re-recorded** to the current cold-build figures, by fixture
   severance, with the frozen `captured_build_v158_*` family left byte-unchanged (CLAIM-04, CLAIM-05).
2. **One docstring citation stops naming a line number** — `tests/test_numeric_schema_source_scan.py`
   cites `build_db.py:594` for a symbol that is not there (CLAIM-06).
3. **`_is_interactive` is removed**, and no test name claims TTY gating the test does not perform
   (CLAIM-07).
4. **`Catalog sync check` is retired**, and the cause of the failure standing since 2026-08-31 is
   recorded rather than merely cleared (CLAIM-08).

Plus one folded todo (D-14): `tools/catalog/sync_to_subrepos.sh`'s two self-comparing verifications.

**Not in this phase:**
- **Any firmware behaviour or protocol change.** The AVR flash figures move only because Phase 183
  already shrank them; this phase re-records a measurement, it does not cause one.
- **Re-anchoring `size_baseline_base01.json`** (D-09). BASE-01 is the frozen pre-landing anchor and
  `test_base01_is_not_re_anchored_by_the_new_exemption` exists to keep it that way.
- **Authoring a new MERGE-05 exemption.** CLAIM-05 forbids it, and Phase 183 already measured that the
  shrink needs none (`183-05-SUMMARY.md`'s `--policy merge05` run against
  `size_baseline_base01.json` exited 0).
- **A successor guard for cross-repo catalog identity** (D-03). Deliberately not filed.
- **Landing the vendored catalog on any repo's `main` branch.** That is a stable-release action,
  operator-gated.
- The REPLY strand (Phase 187) and the FLOOR strand (Phase 186).

</domain>

<decisions>
## Implementation Decisions

### CLAIM-08 — the check that only ever passed off `main`

- **D-01:** **`.github/workflows/catalog-sync-check.yml` is RETIRED OUTRIGHT — the file is deleted.**
  Operator decision, taken against the orchestrator's recommendation (which was to re-point the
  trigger at `beta`, where the property is real and passes today). The operator's grounds, recorded in
  their own terms: the catalog *"has no value to the main branch and shall not be executed by the
  CI — it's a tool that is used when a new message is created while developing and must be generated
  there and then. If it's not executed before fw is committed the fw will not compile."*

  Measured during discussion, supporting the call:
  - **The check has never passed on `main` — and only ever passes off it.** 8 runs total: 6 failures,
    2 successes. Both `main` runs (2026-07-11, 2026-08-31) failed. The two successes were on the
    `gsd/v1.31-…` PR branch on 2026-08-18, **after** `57e63429` landed — on a milestone branch the
    sub-repos do carry a same-named branch with the catalog, so the resolve step worked exactly as
    designed. The workflow is therefore meaningful only on development branches, which is precisely
    the operator's point: it is a dev-time tool, and `main` is where it has nothing to say.
  - Both sub-repos' CI already run, **on every branch**, a catalog validity check
    (`codegen.py --check`) and a codegen drift gate (regenerate, then `git diff --exit-code`) —
    `firestarter/.github/workflows/build.yml:111-120`, `firestarter_app/.github/workflows/ci.yml:56-64`.
    Each sub-repo independently proves *my vendored catalog generates my committed artifact*.
  - No `main` branch in any of the three repositories has **required status checks**
    (`required_status_checks: NONE` on all three, measured via the API), so the deletion cannot leave
    a PR permanently pending.
  - Outside `.planning/`, the only references to the workflow are **inside the file itself**. Nothing
    dangles. (87 `.planning/` files cite it; those are historical-by-intent and are NOT repaired.)
  — **Reversibility:** reversible — recoverable from git. But nothing will be watching, so re-opening
  depends on someone noticing unaided.

- **D-02:** **CLAIM-08 and ROADMAP criterion 5 are AMENDED in this phase, with the reason on the
  record.** Both demand a run on `main` with conclusion `success`; once the workflow is deleted no run
  on `main` can exist at all, so both are unsatisfiable as written. The amended form: *the check is
  retired, and the cause of its standing failure is recorded.* Precedent for amending in the same
  phase as the work: 183's D-08 (SAFE-06 amended alongside the code) and 184's D-03 (criterion 1
  amended). Do NOT satisfy the original wording by some other route — the operator has decided the
  check should not run.
  — **Reversibility:** reversible.

- **D-03:** **A `.planning/notes/` verdict document carries CLAIM-08's record**, following 182
  (`jumper-display-ground-truth.md`), 183 (`ae29f2008-classification-verdict.md`) and 184. Location
  decided from precedent, not asked. It must carry all five of:
  1. **The cause.** `tools/catalog/**` has never existed on either sub-repo's `main`; the vendored
     catalog landed on `beta`. The failing step is
     `cmp firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml`,
     exiting **2** (operand missing, not differing) with
     `cmp: firestarter/tools/catalog/messages.toml: No such file or directory`.
  2. **Why the 2026-08-18 fix did not fix it.** `57e63429` replaced the hardcoded `ref: main` with
     "same branch name, else `beta`" — but its fallback only fires when the sub-repo branch is
     *missing*, and `main` exists in both sub-repos. Run `33447867312` (2026-08-31) resolved
     `firestarter -> main` and `firestarter_app -> main` and died on the identical error the fix's own
     comment describes. The fix **did work on milestone branches** — two successes the day it landed,
     where a same-named sub-repo branch carries the catalog — so what it failed to cover is `main`
     alone, the one branch where no fallback it could express would have helped.
  3. **That the workflow's own comment is now false.** It claims the check *"had never once
     succeeded (5 runs, 5 failures…) — so it has never actually asserted the authority property it
     exists to assert."* True when written; overtaken hours later by two successes. Since the file is
     being deleted, this note is the only place that correction can land.
  4. **That a naive `beta` fallback would not have worked either.** Measured:
     `meta@main` 27 867 B (`cd5a0bb9…`), `firestarter@beta` and `firestarter_app@beta` both 28 658 B
     (`26006603…`), `firestarter@main` absent. Assertion 1 would have passed; assertion 2
     (meta authority vs vendored) would have failed, because `meta@main` is 791 B behind. The failure
     would only have changed its reason.
  5. **The residual gap, named explicitly.** With the workflow gone, nothing checks the two sub-repos'
     vendored `messages.toml` copies against each other or against meta. Each sub-repo's drift gate
     only proves *its own* toml generates *its own* artifact. A hand-edit of one vendored copy that
     bypasses meta and `sync_to_subrepos.sh` would regenerate that repo's artifact cleanly, compile
     fine, and diverge silently from the other side — which is the exact silent-misreport the catalog
     exists to prevent. Why that is accepted: the compile is the practical gate during development,
     and `sync_to_subrepos.sh:65-70` asserts cross-sub-repo byte-identity at sync time (D-14 repairs
     the rest of that script).
  — **Reversibility:** reversible.

- **D-04:** **No successor guard and no backlog item are filed — this is deliberate, not an
  oversight.** A planner or executor must NOT helpfully file a "cross-repo catalog identity" guard
  item on the grounds that D-03's fourth bullet obviously warrants one. The operator chose
  "name it, file nothing". Same branch 184 took at D-05/D-06; the 182 (999.55–999.59) and 183
  (999.63–999.66) filing pattern does **not** apply here.

### CLAIM-07 — the dead TTY helper

- **D-05:** **`_off_tty()` is deleted and all 51 call sites are unwrapped.** Measured during
  discussion: **51 uses across 50 distinct tests** in `firestarter_app/tests/test_dev_test_cmd.py`,
  plus 3 direct `patch("firestarter.cli_handlers._is_interactive", …)` calls — the source todo's
  "~14" was a substantial undercount, and a planner must budget for the real figure. `CliRunner`
  replaces `sys.stdin` with a non-TTY stream for the duration of `invoke()`, so the off-TTY state is
  guaranteed by construction and needs no forcing. The change is behaviour-neutral; the suite passing
  unchanged is the proof. Rejected: re-pointing the helper at `submit.py`'s `isatty_fn` seam (it would
  force a state already guaranteed — 51 wrappers doing real work that changes nothing, which is how
  this arose) and keeping a documented no-op shim (51 wrappers that do nothing behind a name saying
  they do — the same fail-open shape CLAIM-07 exists to close).
  — **Reversibility:** reversible, but costly to redo — the diff touches 51 sites in one file.

- **D-06:** **The two `..._on_a_tty` tests are renamed and the redundant pair merged.** Once the inert
  patches are gone, `test_uv_part_writes_one_slot_on_a_tty` and
  `test_uv_part_writes_one_slot_off_a_tty_too` assert **identical** things — a UV part receives a slot
  write — with no TTY difference between them; one is redundant. They collapse into a single test
  whose name carries no TTY claim. `test_no_prompt_on_a_uv_part_even_on_a_tty` is renamed too: its
  body is a pure `hasattr` structural check that does no TTY work at all, so its name has always been
  a misnomer. Rejected: giving them real TTY simulation — there is no TTY-dependent behaviour left in
  `dev test` to exercise (the UV write prompt was retired by quick task 260822-aq6), so the seam would
  test nothing.
  — **Reversibility:** reversible.

- **D-07:** **`_is_interactive` is deleted, and its three dependents are carried deliberately.**
  Measured: the symbol is defined at `firestarter_app/firestarter/cli_handlers.py:2328` and has
  **zero call sites** in live source — Phase 181 plan 04 deleted the only one. The live TTY readers
  are `submit.py:701,728` and `jp5_gate.py:139-140`, each via its own injectable `isatty_fn`, and
  neither imports `_is_interactive`. Deleting it requires, in the same change:
  1. removing `"_is_interactive"` from `_HANDLER_FUNCTION_NAMES` in
     `firestarter_app/tools/check_devtest_orchestrator.py:163` — that gate asserts every listed name
     resolves to a real callable and goes red otherwise;
  2. repairing `firestarter_app/tests/test_check_devtest_orchestrator.py:585`, whose docstring cites
     `_is_interactive` as the reason its assertion is a SUBSET rather than an equality. After the
     deletion that rationale needs a different live example or a restated reason — it must not be left
     citing a symbol that no longer exists, which is this milestone's own defect class;
  3. updating `test_dev_test_cmd.py`'s module docstring, which claims *"TTY-gating is controlled by
     patching the module-level `firestarter.cli_handlers._is_interactive`"* — false today.
  — **Reversibility:** reversible.

### CLAIM-04 / CLAIM-05 — the baseline re-record

- **D-08:** **A new phase-numbered fixture family, `captured_build_v185_{uno,uno328pb,leonardo}.log`
  plus `planted_size_baseline_flash_regression_v185.log`.** Decided from precedent, not asked: the
  families are phase-numbered (`v132`, `v151`, `v153`, `v158`), and **Phase 158 was itself
  *"Residual Optimizations + Cold Baseline Re-Record (firmware-only)"*** — the direct template for
  this work. The `captured_build_v158_*` family is left **byte-unchanged**; criterion 2's empty
  `git diff` over those paths is the proof.
  — **Reversibility:** reversible.

- **D-09:** **The two native summary fixtures are updated IN PLACE, not severed.**
  `captured_test_native_summary.log` and `captured_test_native_nodevtools_summary.log` both record
  `================ 184 test cases: 184 succeeded …` and must land on **185** on both envs. Updating
  this pair in place rather than severing it is the established convention (recorded in
  `test_check_size_baseline.py`'s own docstring as "the established convention for that pair"), and
  criterion 2 freezes only `captured_build_v158_*`, so the two are consistent.
  — **Reversibility:** reversible.

- **D-10:** **`size_baseline_base01.json` is NOT re-anchored, and the `merge05_*` policy fixtures are
  NOT touched.** BASE-01 is the frozen pre-landing anchor;
  `test_base01_is_not_re_anchored_by_the_new_exemption` reads it and the checker source directly and
  must never read a fixture. The `planted_size_baseline_policy_*` and `merge05_*` fixtures are
  BASE-01-anchored and assert at fixed sub-allowance deltas, so a live-baseline move changes nothing
  they assert — the same "legs deliberately left untouched" reasoning the v158 severance recorded.
  CLAIM-05 additionally forbids authoring any new MERGE-05 exemption.
  — **Reversibility:** costly — re-anchoring BASE-01 has been considered and rejected three times.

- **D-11:** **The baseline JSON and the fixture logs must come from the SAME cold rebuild.** The gate
  is byte-identity between two committed artifacts, so they are only honest if captured together. Two
  failure modes a planner must design against:
  1. **Re-recording flash but not native.** The ROADMAP's dependency note is explicit: Phase 183
     delivered *both* a flash shrink (uno −234 B, uno328pb −238 B, leonardo −284 B; +0 B RAM on all
     three) *and* a native case-count move (184 → 185 on both native envs). `compare_native` asserts
     `cases` exactly, so picking up only the flash figures leaves the gate red.
  2. **Transcribing the figures in `REQUIREMENTS.md`.** CLAIM-04's parenthetical (uno 22968,
     uno328pb 23016, leonardo 25114) is explicitly marked *"to be re-measured, not transcribed from
     this line"* — and it predates Phase 183's shrink, so it is wrong now by construction.
  — **Reversibility:** n/a — an execution-order requirement.

- **D-12:** **The six orphaned build fixtures are deleted.** Measured repo-wide (whole firmware repo,
  excluding `.git`/`.pio`, excluding each file's own self-match): these six are referenced **nowhere**
  — not in code, not even in docstring prose:
  `captured_build_fullflash_uno.log`, `captured_build_fullflash_uno328pb.log`,
  `captured_build_v132_uno.log`, `captured_build_v132_uno328pb.log`,
  `captured_build_v151_uno.log`, `captured_build_v151_uno328pb.log`.
  Same defect class as CLAIM-02 and the same disposal Phase 184 applied to the orphaned
  `planted_dispatch_*` fixtures. Every other retired-generation fixture is still named somewhere
  (prose citations in the checker's own docstring count as a live reference and are kept as prior
  exemptions' evidence) and is **not** in scope.
  — **Reversibility:** reversible — recoverable from git.

### CLAIM-06 — the citation that has already staled three times

- **D-13:** **The citation is replaced with the symbol-and-scope form the same file already uses
  correctly.** Decided from precedent, not asked. `tests/test_numeric_schema_source_scan.py:40` reads
  `` `_AT28C_DIP24_NAMES` (build_db.py:594) ``; line 129 of the same file already gets it right —
  *"`_AT28C_DIP24_NAMES`, a local variable nested inside a `for` loop deep in `main()`"* — with no
  line number. Line 40 adopts that form. Measured: line 40 is the **only** `.py:NNN` citation left in
  the file, so this is a one-site change.

  **Evidence that the line-number form cannot be kept:** the requirement says the symbol lives at
  545; it is at **538** today. `529d6e1` (Phase 182-02, 2026-09-10) moved it — **the same day
  `REQUIREMENTS.md` was written.** Verified: at `529d6e1^` the symbol was at 545, matching the
  requirement text exactly. The citation has now staled a third time, and the requirement's own
  figure staled within a day of being authored. A planner must not transcribe either 594 or 545.
  — **Reversibility:** reversible.

### Folded scope

- **D-14:** **`tools/catalog/sync_to_subrepos.sh`'s two self-comparing verifications are repaired in
  this phase.** Folded from `.planning/todos/pending/2026-08-30-sync-to-subrepos-self-diff-asserts-nothing.md`.
  Lines 84-86 and 97-99 each run `diff -q "$X" "$X"` — a path against itself — then print a success
  line for a property never tested, with no `else` branch, so no failure can ever be observed. It is
  the same defect class as the workflow D-01 retires, in the repository's only sync tooling,
  immediately after the `codegen.py` invocations it purports to verify.

  **Why it folds in now rather than staying deferred:** D-01 removes the only CI check on cross-repo
  catalog identity, which makes this script the sole remaining mechanism asserting it (its lines
  65-70 hold the one *correct* two-operand assertion). Repairing the two tautologies directly narrows
  the residual gap D-03 is required to record.

  The todo's own candidate fix applies: regenerate into a temp path and diff the committed artifact
  against that copy (two traceably distinct operands); add the missing `else` with a non-zero exit;
  and **prove it by mutating a committed artifact, watching it go red, then restoring** — a
  verification whose red state has never been seen proves nothing. Copy the shape already at
  lines 65-70.
  — **Reversibility:** reversible.

### Claude's Discretion

The operator answered "All sounds good" to four recommendations and delegated six mechanical calls to
precedent. These are Claude's calls, recorded above with their reasoning; a planner may revisit them
on evidence:

- D-05, D-06 (the `_off_tty` disposition and the test rename/merge)
- D-12 (deleting the six orphans)
- D-14 (folding the sync-script todo)
- D-08, D-09, D-10, D-13 and D-03's location — taken from precedent and stated to the operator as
  decided-not-asked, with no objection raised.

The decisions the operator made directly, which must NOT be revisited without asking them:
**D-01** (retire the workflow outright — chosen over the recommended re-point-to-beta) and
**D-04** (name the gap, file nothing).

### Folded Todos

- **`2026-09-09-is-interactive-dead-after-181-04.md`** — carries `resolves_phase: 185` in its own
  frontmatter, so it was earmarked for this phase before the milestone began. Source: `181-REVIEW.md`
  WR-01. Its four-point "what a fix has to cover" list is subsumed by D-05/D-06/D-07, with one
  correction: its call-site estimate of ~14 is measured at **51**.
- **`2026-08-30-sync-to-subrepos-self-diff-asserts-nothing.md`** — folded per D-14.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap
- `.planning/REQUIREMENTS.md` § CLAIM — CLAIM-04…CLAIM-08 verbatim. **CLAIM-08 is amended by D-02.**
  CLAIM-04's line-number and byte figures are stale by construction (D-11, D-13).
- `.planning/REQUIREMENTS.md` § "Decisions taken at activation" — **D-7**: the re-record uses the
  fixture-severance pattern, and *"no acceptance criterion may say 'tests byte-unchanged' — it is
  unsatisfiable by construction."*
- `.planning/ROADMAP.md` § Phase 185 — the five success criteria and the "Depends on Phase 183"
  paragraph naming both inputs (flash shrink and native case count). **Criterion 5 is amended by D-02.**

### The size baseline (CLAIM-04, CLAIM-05)
- `firestarter/scripts/check_size_baseline.py` — the two-mode checker. `--rebuild` drives criterion
  1's cold rebuild; `--policy merge05` is the band mode and is **not** used for the default gate.
- `firestarter/tests/test_check_size_baseline.py` — read the module docstring (lines 1-490) in full
  before planning. It contains the v158 severance's own account: the four legs that couple to the
  live baseline, the legs deliberately left untouched and why, and the CI consequence.
- `firestarter/scripts/baseline/size_baseline.json` — the live baseline. Today: uno 22952,
  uno328pb 23000, leonardo 25098; native `cases: 184, suites: 17` on both envs.
- `firestarter/scripts/baseline/size_baseline_base01.json` — **frozen. Never re-anchored** (D-10).
- `firestarter/.github/workflows/build.yml:161` — `pytest tests/ -v`, ungated, on
  `push: branches: ['**', '!beta']`. **Consequence:** moving the live baseline without severing the
  fixtures in the same commit turns this suite red in CI. `check_size_baseline.py` itself is invoked
  by **no** workflow — the cold rebuild is a local-run obligation.

### The dead TTY helper (CLAIM-07)
- `firestarter_app/firestarter/cli_handlers.py:2328` — `_is_interactive`, zero call sites.
- `firestarter_app/tests/test_dev_test_cmd.py` — `_off_tty()` at 518-520, its 51 uses, the three
  direct patches, the `TestUVWriteHasNoPrompt` class, and the false module docstring at lines 8-14.
- `firestarter_app/tools/check_devtest_orchestrator.py:163` — `_HANDLER_FUNCTION_NAMES` (D-07.1).
- `firestarter_app/tests/test_check_devtest_orchestrator.py:585` — the subset-vs-equality rationale
  that cites `_is_interactive` (D-07.2).
- `firestarter_app/firestarter/submit.py:641,701,728` and `firestarter_app/firestarter/jp5_gate.py:121,139-140`
  — the two **real** TTY readers, each with its own injectable `isatty_fn`. Neither imports
  `_is_interactive`; do not disturb them.

### The stale citation (CLAIM-06)
- `firestarter_app/tests/test_numeric_schema_source_scan.py:40` — the defect; **line 129 of the same
  file is the correct form to copy** (D-13).
- `firestarter_app/tools/build_db.py:538` — `_AT28C_DIP24_NAMES`, a local inside `main()` (`def` at
  line 398). Verify the line before citing anything; do not write a line number.

### The retired check (CLAIM-08)
- `.github/workflows/catalog-sync-check.yml` — the file D-01 deletes. Read it **before** deleting:
  its "Resolve sub-repo ref" comment is a primary source for D-03's record.
- `tools/catalog/sync_to_subrepos.sh` — lines 84-86 and 97-99 (the tautologies, D-14) and lines 65-70
  (the correct shape to copy).
- `tools/catalog/messages.toml` and `tools/catalog/codegen.py` — the authoritative catalog and its
  generator. Generated artifacts: `firestarter/include/messages.h`,
  `firestarter_app/firestarter/messages.py`.
- `firestarter/.github/workflows/build.yml:111-120` and `firestarter_app/.github/workflows/ci.yml:56-64`
  — the per-sub-repo catalog validity and codegen drift gates that survive the retirement.

### Precedent
- `.planning/phases/184-guards-that-exist/184-CONTEXT.md` — D-03 (criterion amended in-phase), D-05/D-06
  (retire outright, file nothing), D-07 (delete orphaned fixtures), D-08 (the `.planning/notes/`
  verdict-document pattern and its four required contents).
- `.planning/phases/183-.../183-CONTEXT.md` D-08 — a requirement amended alongside the code, with the
  conflict stated on the record before the choice was made.
- `.planning/notes/jumper-display-ground-truth.md` and `.planning/notes/ae29f2008-classification-verdict.md`
  — the two templates for D-03's note.

### Project rules that constrain execution
- `/workspaces/CLAUDE.md` § "Source code comments — hard rule" — **absolute, not overridable by this
  plan.** Directly binds D-07.2 and D-07.3: the permitted operations are deleting a false clause and
  deleting a symbol. If a repair cannot be made without authoring replacement commentary in
  `firestarter/` or `firestarter_app/` source, leave it and record the deviation in the plan's
  `SUMMARY.md`. **Docstrings are a separate question** — `test_*.py` docstrings and Click `--help`
  text are not comments, and CLAIM-06 and CLAIM-07 are largely docstring work.
- `/workspaces/CLAUDE.md` § "Milestone close and branch protection" — `git.base_branch` is `beta`;
  `main` is protected in all three repositories.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The v158 severance is a complete worked template** for D-08/D-09. `test_check_size_baseline.py`'s
  docstring records which legs coupled to the live baseline, which were left alone and why, and the
  reconciliation between the expected and observed red-leg counts. Phase 158 was literally
  *"Residual Optimizations + Cold Baseline Re-Record"* — the same job as this one.
- **`sync_to_subrepos.sh:65-70`** — the one correct two-operand assertion in that file; D-14 copies its
  shape into lines 84-86 and 97-99.
- **The `.planning/notes/` verdict-document pattern** — 182, 183 and 184 each produced one; D-03's is
  the fourth.

### Established Patterns
- **Fixture severance over fixture mutation** — a re-record creates a new phase-numbered family and
  leaves the prior one frozen as evidence. Six generations deep now.
- **RED-first proof** — 183-04 and 184's D-13 both landed a guard, watched it go red, then made the
  change. D-14 requires the same: mutate a committed artifact, observe red, restore.
- **Record the absence rather than silently erase it** — meta `CLAUDE.md`'s *"no automated wiki guard
  exists now"*, and 184's D-09. D-03's fourth bullet is this pattern applied to CLAIM-08.
- **Amend a requirement in the same phase as the work, with the conflict stated first** — 183 D-08,
  184 D-03, now D-02.

### Integration Points
- **All three repositories are touched.** Meta (workflow deletion, `sync_to_subrepos.sh`,
  `.planning/notes/`, `REQUIREMENTS.md`, `ROADMAP.md`), firmware (baseline JSON, six fixture
  deletions, four new fixtures, two native summaries, the checker's test docstring), app
  (`cli_handlers.py`, `test_dev_test_cmd.py`, `check_devtest_orchestrator.py`,
  `test_check_devtest_orchestrator.py`, `test_numeric_schema_source_scan.py`).
- **The firmware and app work is file-disjoint** and shares no dependency, so the two can run as
  parallel waves; the meta record close-out depends on both.
- **Gitlink:** advanced per-phase by name since v1.36. Both sub-repos are written here, so both
  advance.
- **CI reachability:** the firmware suite runs in CI on every branch but `beta` (plus `beta-build.yml`
  for `beta`), so a baseline move without severance is caught there. The app suite runs on every
  branch. Neither CI path rebuilds and compares — they compare committed artifacts only, which is
  why D-11's same-rebuild discipline is the executor's responsibility, not CI's.

### Measurement traps a planner must design around
- **`grep` in this devcontainer is ugrep and honors `.gitignore`** — it silently under-scans. Use
  `/usr/bin/grep` or a script for any gate evidence. The inverse trap also applies here:
  `firestarter_app/build/lib/firestarter/cli_handlers.py` is a **gitignored, untracked** stale build
  artifact that still contains a live `_is_interactive()` call site. `/usr/bin/grep` will hit it and
  it looks like a surviving reference. It is not source; do not chase it, and do not let it fail a
  "no references remain" check.
- **`firestarter_app/tools/` sits outside every CI gate** — no mypy, no `ruff check`, no
  `ruff format`. `check_devtest_orchestrator.py` lives there (D-07.1).

</code_context>

<specifics>
## Specific Ideas

- **The three measured facts behind D-01**, for the note:

  | Artifact | Size | sha256 (first 16) |
  |---|---|---|
  | `meta@main` | 27 867 B | `cd5a0bb99a74d4f7` |
  | `firestarter@beta` | 28 658 B | `260066039d07ab5c` |
  | `firestarter_app@beta` | 28 658 B | `260066039d07ab5c` |
  | `firestarter@main` | **absent** | — |

- **The failing run, for citation:** `33447867312`, `main`, push, 2026-08-31T22:47:56Z, 20 s.
  Resolve step output: `meta ref under test: main` / `firestarter -> main` / `firestarter_app -> main`.
  Failing step: `Assert cross-sub-repo vendored catalog identity`, `##[error]Process completed with
  exit code 2`.

- **The full run history — 8 runs, 6 failures, 2 successes:**

  | Date | Conclusion | Branch | Event | Run |
  |---|---|---|---|---|
  | 2026-07-11 | failure | `main` | push | 29147915116 |
  | 2026-08-09 | failure | `gsd/v1.31-27c-…` | pull_request | 31316652539 |
  | 2026-08-18 | failure | `gsd/v1.31-27c-…` | pull_request | 32110106709 |
  | 2026-08-18 | failure | `gsd/v1.31-27c-…` | pull_request | 32110732140 |
  | 2026-08-18 | failure | `gsd/v1.31-27c-…` | pull_request | 32118301480 |
  | 2026-08-18 | **success** | `gsd/v1.31-27c-…` | pull_request | 32118599666 |
  | 2026-08-18 | **success** | `gsd/v1.31-27c-…` | pull_request | 32122444857 |
  | 2026-08-31 | failure | `main` | push | 33447867312 |

  Both `main` runs failed; both successes are post-`57e63429`, on a milestone branch.

- **The workflow's own comment is now stale, and the note should say so.** Its "Resolve sub-repo ref"
  block asserts *"this workflow had never once succeeded (5 runs, 5 failures, 2026-07-11 through
  2026-08-18) — so it has never actually asserted the authority property it exists to assert."* That
  was true when written, hours before the same day's two successes. It is false now. A comment in the
  repo that is no longer true is this milestone's own defect class, and it is being deleted along with
  the file — so the note is the only place the correction can land.

- **The two `..._on_a_tty` tests, verbatim on what they actually do** (D-06):
  `test_no_prompt_on_a_uv_part_even_on_a_tty` asserts
  `not hasattr(cli_handlers_mod, "Confirm")` and `not hasattr(…, "_default_uv_write_confirm")` —
  no TTY work of any kind. `test_uv_part_writes_one_slot_on_a_tty` wraps its `invoke` in
  `patch("firestarter.cli_handlers._is_interactive", return_value=True)` and asserts
  `"write-partial" in {s["op"] for s in data["steps"]}` — the identical assertion its
  `off_a_tty_too` sibling makes.

- **Native summary fixtures, the exact line to move:**
  `================ 184 test cases: 184 succeeded in 00:00:21.189 ================` (native) and
  `… in 00:00:36.658 ================` (native_nodevtools). The case count moves to 185; the
  durations are re-captured, not edited.

</specifics>

<deferred>
## Deferred Ideas

- **A successor guard for cross-repo vendored-catalog identity.** Both vendored copies and meta's
  authoritative copy are byte-comparable, so it could be checked properly — as a sub-repo CI step, or
  as a pre-commit hook, rather than as a meta-repo workflow that can only see all three by checking
  them out. **The operator explicitly declined to file this** (D-04). Recorded here as a rejected
  option so a later reader knows it was considered, **not** as a backlog candidate. Do not file it.

- **`test_configure_memory.cpp:9` cites `build_db.py:89` by line number**, where `KNOWN_PROTOCOLS`
  actually lives at 137. Exactly CLAIM-06's defect class, in the firmware repo, outside this phase's
  requirements. Carried forward unfiled from 184's own deferred list — flagged again here for whoever
  scopes a citation sweep, since this phase proves the form is unsafe (D-13).

- **A mechanical guard against line-number citations in docstrings.** CLAIM-06 has now staled three
  times, and the requirement text staled within a day of being written. A check that no test docstring
  contains a `\.py:\d+` citation would make the defect unwritable, in the spirit of 184's CLAIM-09.
  Not filed — it is a new capability and belongs in its own phase.

- **The retired-generation fixtures that survive D-12.** `captured_build_v132_leonardo.log`,
  `v151_leonardo`, `v153_*` and the bare/`_fullflash` families remain, each still named somewhere.
  The tree accumulates one generation per re-record and nothing prunes it on a schedule. Named, not
  filed.

### Reviewed Todos (not folded)

`todo.match-phase 185` returned 35 matches. All but two scored 0.6 on generic keyword overlap
("test", "check", "phase", "firestarter") with no semantic bearing on any CLAIM requirement — the
matcher has no signal here. The two that matter were both folded (see § Folded Todos). The two
highest-scoring matches (0.9) — `2026-08-27-strip-gsd-provenance-comments-from-source.md` and
`2026-08-30-remove-cmd-verify-from-firmware-compare-in-app.md` — were reviewed and **not** folded:
the first is a standing hard rule already enforced by `CLAUDE.md` rather than a unit of work, and the
second is a firmware protocol change, which this milestone's Out of Scope bars outright.

</deferred>

---

*Phase: 185-records-and-checks-that-are-current*
*Context gathered: 2026-09-11*
