# Phase 131 Record: Gate Hardening & CI Parity — Corrections, Negative Space, Prohibition Verification, Phase 137 Hand-off

**Owner:** Plan 131-07 (the phase's closing record). **Status:** phase closed — all ten GATE
requirements verified, none of this phase's own work is a Phase 132 achievement.

This document is the single place Phase 137's ledger reads for everything this phase amended,
rejected, or discharged by record rather than by work. It also carries the mechanical prohibition
verification this plan itself ran, with literal outputs, not paraphrases.

---

## 1. Corrections register (F-01…F-07)

Every correction below amends a locked `131-CONTEXT.md` decision on a measured fact, per that
document's own preamble ("a later reader can overturn one on new facts rather than on taste"). All
seven are flagged **for Phase 137's ledger**.

| # | Amends | What the locked decision said | Measured fact that overturned it | What replaced it | Why the replacement preserves the decision's purpose | Owning plan |
|---|---|---|---|---|---|---|
| **F-01** | D-06 leg 1 | Independently recompute the ALLOW/REFUSE partition from `chip_database.json` + the committed `flags` bit-15 decode, then compare it element-wise against `sdp_capability()` — a derivation genuinely independent of the function under test. | `chip_database.json` carries **zero** `"flags"` occurrences, and `tools/infoic*.xml` (the bit-15 source) is gitignored (`.gitignore:29`) and absent from the working tree. A literal reading would have to recompute the partition using the very predicate (`sdp_capability_for_entry`) it is meant to check against — self-parity, exactly P-10's hole (passes whenever both sides drift together). | A **committed, sorted, manufacturer-qualified 43-entry ALLOW snapshot** (`_COMMITTED_SDP_ALLOW_ENTRIES`), generated once from the real DB via `_partition_0x0d` (which calls the production predicate) and hand-verified against five spot-check anchors. The measured side still comes from the real predicate; the independent side is now a **committed constant**, not a second derivation. A chip moving ALLOW→REFUSE reddens the element-wise leg, and the only diff that greens it is a **visible edit to the named constant**, governed by its change-protocol comment. | The gate's whole purpose — catching a narrowed chip before it silently ships — survives intact. What changed is *where* the independent side lives (a committed snapshot instead of a second derivation), because the second derivation this repo could build would not actually be independent. This is the **one correction that changes what the gate actually proves**: a later reader must know the 43-name list is a **snapshot, not a derivation**, and that the repo cannot currently do better (no `flags` field shipped, no `infoic.xml` present). | 131-03 |
| **F-02** | D-06 placement | Extend **both** `tests/test_sdp_db_invariant.py` and `tests/test_sdp_table_parity.py` with the new 43/41/84 legs. | `tests/test_sdp_table_parity.py` imports `requires_fw` at `:55` and resolves firmware paths at import time, so the **whole module** is skipped under CI-parity recipe leg 1 (empty `FIRESTARTER_FW_ROOT`) and in standalone CI. A leg placed there would be invisible exactly where GATE-09's parity recipe needs it visible. | All DB-only legs (the two real legs plus the non-vacuity proof) went into `tests/test_sdp_db_invariant.py` only, which carries no FW-absent skip marker. `test_sdp_table_parity.py` was not touched. | The gate now runs under every condition D-06 needed it to run under (recipe leg 1, standalone CI, the full local suite), which placing half of it in a skippable module would not have guaranteed. Also mechanically discharges D-18's negative criterion for this phase's own new tests. | 131-03 |
| **F-03** | `REQUIREMENTS.md` Out-of-Scope row "Filing the py3.9-drop backlog item" | The row (dated 2026-08-03, same day) recorded an **operator decision not to file** the backlog stub, naming its own cost explicitly: without a stub, the gap "will present again rather than being scheduled." | `131-CONTEXT.md` D-13 — written later the **same day, same discussion session** — read that row's own stated cost and elected to pay it: file the stub after all. | The row is **superseded, not deleted or rewritten**. A `[⚠ SUPERSEDED 2026-08-03, Phase 131 plan 131-01 (131-CONTEXT.md D-13): …]` block is appended in the same cell, naming D-13, the two new stub numbers (ROADMAP 999.26, 999.27), and that `FUT-MYPY-01` remains the requirement-side record. | The original decision's reasoning is preserved as history (it was a real decision at the time), while the record no longer misleads a reader into thinking the gap is permanently unscheduled. This is the same defect class F-03 exists to fix, and the pattern step (f) below reuses verbatim. | 131-01 (task 1) |
| **F-04** | D-15 | The AST derivation of `dev_test`'s referenced helpers should walk the whole `dev_test` `FunctionDef` node. | Walking the whole node (`ast.walk(dev_test_node)`) includes `decorator_list`, which references `_complete_eprom` — `dev_test`'s `@click.argument(..., shell_complete=_complete_eprom)` decorator argument, a shell-completion callback shared by 15 unrelated commands and **not** listed in `_HANDLER_FUNCTION_NAMES`. A whole-node walk would be RED on day one for a name that is not a `dev_test`-body dependency at all. | The derivation walks **`dev_test.body` statement-by-statement**, never the whole `FunctionDef` node, so the decorator list is excluded by construction. Measured: body-only yields exactly six names, all listed; whole-node yields seven, with `_complete_eprom` the extra one. | The gate's purpose — catch a new helper `dev_test`'s **logic** calls but forgets to list — survives; what changed is the derivation's scope, narrowed to the function's actual behavior rather than its Click wiring. Proven live, not assumed: 131-04's Task 1 authored the naive whole-node walk first, **watched it fail** with `_complete_eprom` as the named extra, then applied the body-only fix and watched it pass. | 131-04 |
| **F-05** | D-02 layer 3 (the end-to-end pytest leg) | Assert `exit ∈ {0,1,2}` **and** that stdout carries the `mypy errors: N (watermark: M)` line, proving the runner half is wired without asserting a specific count. | In this devcontainer the hardened gate now legitimately exits **2** (numpy PEP-695 stub truncation) **before any count is printed** — printing a count on an exit-2 run would itself be the fail-open shape this phase removes. The original wording is therefore unsatisfiable here on an honest run. | A **two-shape, mutually-exclusive** assertion: either the complete shape (`mypy errors: N (watermark: M)`) or the incomplete shape (an `ERROR:` diagnostic, no count line) — never both, and an exit-2 run must never carry the count line. Both a real app-root invocation and a foreign `tmp_path` invocation are asserted to land in the *same* shape. | Strictly **stronger** than the original wording, since it additionally forbids the fail-open shape (a count line on an exit-2 run) that the original assertion could not see. Proves the runner is wired in either environment shape, not just one. | 131-02 |
| **F-06** | Planner-added, in scope (P-07's class) | — (no prior decision; a new test module must not silently escape `check_no_exists_proxy.py`'s fail-closed target list). | `tools/check_no_exists_proxy.py`'s `_DEFAULT_TARGETS` is explicit and non-glob; a new module not added to it is invisible to that gate. | `tests/test_check_mypy_watermark.py` was added to `_DEFAULT_TARGETS` in the **same commit** that created the module. | Keeps the checker's own coverage honest — the same lesson GATE-03's `MIN_CHECKED_SOURCE_FILES` encodes for mypy, applied here to the house `check_no_exists_proxy.py` registry. | 131-02 |
| **F-07** | D-12's `(checked K source files)` acceptance criterion; 131-05-PLAN.md task 3's automated grep | 131-05's task 3 required a verbatim `Found N errors in M files (checked K source files)` line, read from the real CI dispatch, as GATE-07's evidence. | Verified live against the real CI run (`30822281624`, `workflow_dispatch` on `beta` @ `16a313a`): mypy's raw completion clause is **structurally absent** from CI output — zero `checked` occurrences across the full 635-line run log. The **fork-base** (pre-131-01) `tools/check_mypy_watermark.py` captures mypy's stdout via `subprocess.run` and prints only its own two derived lines (`mypy errors: N (watermark: M)` / `FAIL: …`); it never prints mypy's raw stdout, so the completion clause never reaches CI's log at all — a property of the checker being measured, not a transcription gap. | `131-CI-BASELINE.md`'s count line and 131-05-PLAN.md task 3's automated `<verify>` were amended to key on the verbatim line CI actually emitted (`mypy errors: 69 (watermark: 35)`), not the unreachable `checked` clause. | The criterion is **amended, not fabricated around** — the evidence gate still proves GATE-07's substance (a real dispatch, a real read count) without requiring a line that structurally cannot appear at the fork base. **Corollary, worth recording:** Phase 131's own hardening makes the checker surface mypy's completion clause going forward, so this absence is a property of the **fork base being measured**, not of the hardened gate — Phase 132's own dispatch should see the richer, `checked`-bearing output. | 131-05 (task 3) |

**F-01 is the one correction that changes what a gate actually proves.** Do not compress it in any
downstream summary: the committed 43-name ALLOW list is a **snapshot**, not a derivation, and this
repo cannot currently do better — no `flags` field is shipped in `chip_database.json`, and
`tools/infoic.xml` is gitignored and absent. If either ever becomes available, F-01's rejection of a
true independent derivation should be revisited.

## 2. Deliberate rejections (negative space)

These are decisions, not oversights, and each is recorded as such for Phase 137's ledger.

### D-04 — no canary fixture module

P-13 calls the canary fixture *"the load-bearing one"* of its five mechanical preventions, so
rejecting it is a deliberate act with reasons, not a gap:

1. **A canary module with deliberate type errors sits inside the checked tree**, so it adds N errors
   to the real count — the exact number Phase 132 must drive to ≤35 and re-baseline. It would
   corrupt the watermark's meaning **permanently**, and the watermark is this milestone's central
   honesty artifact.
2. **Excluding the canary from the main run and checking it in a second mypy invocation proves only
   that a second, differently-scoped run works.** It does not guard the real run at all.
3. **The abort mode the canary targets is already caught structurally** by requiring the
   `(checked N source files)` completion clause: measured, the truncated path emits
   `(errors prevented further checking)` and **no** `checked` clause. Requiring the completion
   clause makes the truncated shape unparseable ⇒ exit 2 **even if a future mypy returns 1 on that
   path** — strictly stronger than a canary, because it does not depend on the canary's errors
   surviving a future mypy version.
4. **`MIN_CHECKED_SOURCE_FILES` is the coverage assertion**, which is this project's own repeated
   lesson: assert the **coverage** of the check, not just its verdict.

**Reopening condition, stated explicitly:** if anyone finds an abort mode that emits a valid
`(checked N source files)` clause over a truncated file set — i.e. a mypy failure mode that produces
a well-formed completion clause while having actually checked fewer files than the tree contains —
this rejection must be reopened, because reason 3 above would no longer hold.

### D-11 — exactly one CI dispatch

The choice assumes **Phase 132's own dispatch will serve as the hardened-gate-in-CI proof** — a
second, post-hardening dispatch here would show the hardened gate at `exit 1` on the same 69-error
tree, the same red for the same reason, buying nothing for an operator round-trip.

**Residual, recorded for a later reader:** if Phase 132 is replanned without its own CI dispatch,
this phase owes a second run to prove the hardened gate red-for-the-right-reason in CI. That has not
happened as of this writing.

### D-14 — the `mypy<3` bound

A judgement about where the gate's output-format dependency is licensed to change: the classifier's
discriminator is now a regex over mypy's summary-line format, and a mypy major version is exactly
where that format could change without warning. The bound is harmless if wrong (2.3.0 resolves
today) — revisit if it ever blocks a needed upgrade, per the raise protocol commented at the pin
site (raise the bound deliberately, re-verify both summary-line regexes in the same commit).

### D-13 — keeping `requires-python = ">=3.9"`

Delegation ("you decide") covers implementation shape; it does **not** extend to a live PyPI
package's advertised support contract. Dropping 3.9 is a published-metadata breaking change and
stays an operator decision, not an implementer's. The residual — after `python_version = "3.10"`,
nothing type-checks against the advertised 3.9 floor, and ruff's `target-version = "py39"` covers
syntax/idiom only, never a stdlib API — is filed as backlog **ROADMAP 999.26** and tracked as
requirement-side **FUT-MYPY-01**. The companion treadmill (Python 3.10 EOLs 2026-10-31; a future
mypy clamping to ≥3.11 re-fires this exact failure) is filed as backlog **ROADMAP 999.27**.

---

## 3. Record-only discharges

D-10, D-17, and D-18 — none of which is work performed by this phase.

### D-10 — `tools/check_no_exists_proxy.py`, one-time confirmation

Run once (131-06), result `PASS: scanned 79 file(s) …`, exit 0, recorded in `131-CI-PARITY.md`.
Deliberately **not** a recipe leg — `ci.yml` runs no such step, and adding one would make
`tools/ci_parity.sh` an unfaithful mirror of CI. This discharges STATE.md's standing note that six
modules shared the `_FW_ABSENT` idiom and it was "worth confirming none survive" — confirmed: **none
survive** outside the one recognised marker module (`tests/fw_presence.py` itself, which defines the
idiom rather than proxying it).

### D-17 — the research record is wrong on repo, commit, and substance

Research's operator-decision #7(a) and `PITFALLS.md` P-18 item 4 are corrected, not acted on:

1. **Wrong repo.** `test_present_root_with_missing_target_raises_not_skips` lives at
   `firestarter/tests/test_flash_path_record_sync.py:694` — the **firmware** repo, which this
   milestone does not touch at all. It is **not** in `firestarter_app`; no downstream agent should
   hunt for it there, and none should edit the firmware repo to "fix" it.
2. **Wrong commit.** The softening is firmware commit `1c511e8`
   ("scope the meta-root premise leg to skip when no meta root exists"), **not** app commit
   `5934a54` as research named — `5934a54` touched `tests/test_py32_flash_map_host.py` and
   `tests/test_scan_paths_resolve.py`, neither of which is that test.
3. **Not a weakened assertion — premise-scoped.** The gate's own subject — that a missing scan
   target **raises** `MissingScanTargetError` rather than being silently skipped — is still
   hard-asserted wherever its premise holds. What was scoped is the **environment premise**
   (`META_PRESENT`), which a prior phase had written as a bare `assert META_PRESENT`,
   hard-asserting an environment fact into a test failure rather than scoping the test to when that
   fact holds. The companion `test_absent_meta_claim_can_never_be_false` makes a false absence claim
   impossible by construction, closing the abuse path the "softening" framing worried about.

**Disposition: record the correction to the research record, do not act on it.** Correct
`PITFALLS.md` P-18 item 4 and `SUMMARY.md` §"Operator Decisions Needed" item 7(a) are both wrong on
provenance; this record is the correction. No agent should hunt for the test in `firestarter_app`,
and no agent should touch the firmware repo on this basis. STATE.md's own phrasing — *"softened a
Phase-129-authored hard assert to a skip — a defect-class change"* — is the **source** of the
mischaracterisation and is itself imprecise; correcting STATE.md's prose is not in this phase's
scope, and the divergence is recorded rather than reconciled (see `.planning/REQUIREMENTS.md`'s
"Restoring the softened Phase-129 assert" Out-of-Scope row, annotated by this plan's task 2 step (f)
— cross-referenced there and here, bidirectionally).

### D-18 — `81fa53c`, latent carry, record only

`81fa53c` (`fix(122-07): skip firmware-checkout-dependent clean-source tests in standalone CI`,
adding `skipif` guards to `test_check_is_memory_cmd_no_ifdef.py` and
`test_check_no_log_in_sdp_window.py`) is confirmed **present** in the app repo's history. `main` has
never been merged in any of the three repos, so the carry stays latent, and acting now would be work
against a merge that is not happening. Its criterion is **negative**: any test this phase adds must
pass under recipe leg 1 (empty sibling root). Recipe leg 1 discharged this mechanically over the
three new/extended modules from 131-02 (`test_check_mypy_watermark.py`), 131-03
(`test_sdp_db_invariant.py`), and 131-04 (`test_check_devtest_orchestrator.py`) — all three passed
under the empty-`FIRESTARTER_FW_ROOT` condition in 131-06's recorded run.

---

## 4. What this phase deliberately did NOT do

Stated plainly, with the mechanical evidence gathered in this plan's task 2 (§5 below):

- **Set no watermark.** `pyproject.toml`'s `# mypy_error_watermark = 35` is byte-unchanged.
- **Deleted nothing.** `dev sdp` survives this phase intact (`firestarter/cli_handlers.py` still
  defines `def dev_sdp(...)`; `git -C firestarter_app diff --diff-filter=D --name-only 16a313a..HEAD`
  is empty).
- **Fixed none of the inherited mypy errors.** Not one of the 69.
- **Touched the firmware repo not at all.** `git -C /workspaces/firestarter status --short` is
  empty and HEAD is unchanged throughout the phase.
- **Opened no `eprom_operations.py` ring-fence.** The `follow_imports = "silent"` override block in
  `pyproject.toml` is untouched.
- **Added no new pytest skip reason.** `tests/test_skip_census.py` is not in the phase diff and
  passes unmodified.
- **Ran no outward-facing command from any agent.** No `gh workflow run`, `git push`, `git merge`,
  `git tag`, `gh release`, or `twine upload` appears in any `automated` block across all seven plan
  files (verified mechanically — §5 below), and none was executed by any agent. **This statement is
  true but would mislead by omission if left unqualified — see §4a.**

### 4a. How GATE-07's prohibition was actually upheld

The bullet above is literally true, and a reader would still draw the wrong conclusion from it. The
full sequence, recorded because an auditor asking *"was that gate real, or merely unexercised?"*
needs it:

1. `131-05` reached its human-action checkpoint and returned without dispatching — correct behaviour,
   the prohibition working as intended.
2. **The operator then explicitly instructed the orchestrator to run the dispatch on their behalf.**
   That is a legitimate authorization, not a prohibited act: the prohibition exists to keep the
   *decision* with the operator, and the operator was exercising it.
3. The orchestrator attempted `gh workflow run ci.yml --repo henols/firestarter_app --ref beta`.
4. **The attempt was denied by Claude Code's auto-mode classifier** — a harness layer independent of
   the project permission allowlist. Note that `.claude/settings.local.json` *already* contains
   `Bash(gh workflow:*)`, so the allowlist was not the constraint. Read-only `gh run list` /
   `gh run view` / `gh auth status` all executed normally in the same session under the same
   allowlist; the classifier distinguishes state-changing `gh` from read-only `gh`.
5. The orchestrator declined to route around the denial — no `gh api --method POST`, and no editing
   of its own permission settings (both were available and both were refused; the classifier
   subsequently blocked settings access too).
6. **The operator ran the command themselves.** Run `30822281624` is therefore operator-executed.

**So the prohibition held, but not solely by agent restraint — it held by harness enforcement while
the agent was acting under explicit operator authorization.** Both facts belong in the record. A
future phase must not read this one as evidence that "the agent will never attempt a dispatch";
the correct reading is that the dispatch path is gated by a layer the agent cannot self-authorize
past, and that the agent did not attempt to.

**Consequence worth carrying to Phase 132:** any phase requiring a real CI dispatch must budget for
an operator turn. The dispatch cannot be automated in a non-interactive session regardless of the
project allowlist. Everything *downstream* of the dispatch is fully automatable — read-only
`gh run view` supplied every value in `131-CI-BASELINE.md` without operator involvement, provided
`XDG_CACHE_HOME` is redirected to a writable path (see §6).

## 5. The standing honesty statement

**`firestarter_app`'s primary `ci` job is RED before this phase and RED after it, by design.** This
phase hardened the gate mechanism (GATE-01…GATE-06), the anti-narrowing SDP partition gate
(GATE-08), the derived handler-list subset gate (GATE-10), and authored the CI-parity recipe
(GATE-09) plus the one real dispatch that measured the current fork-base count (GATE-07). It fixed
**zero** mypy errors and set **no** watermark. The count recorded in `131-CI-BASELINE.md` (69,
verbatim from CI run `30822281624`) is **an input to Phase 132's watermark, not a Phase 131 claim**.
Any artifact stating otherwise is the v1.22 C-5 overclaim class.

## 6. Phase 137 ledger hand-off

Everything Phase 137's honesty ledger must carry forward from this phase:

1. **The six corrections that change the built artifact** — F-01 (committed ALLOW snapshot replaces
   an unimplementable independent derivation — the one correction that changes what a gate proves),
   F-02 (43/41/84 legs live only in `test_sdp_db_invariant.py`, not `test_sdp_table_parity.py`),
   F-04 (body-only AST walk, decorator list excluded), F-05 (two-shape mutually-exclusive end-to-end
   assertion replaces a count-asserting one), F-06 (new test module registered in
   `check_no_exists_proxy.py`'s `_DEFAULT_TARGETS` in the same commit), F-07 (GATE-07's evidence
   keys on the literal CI line, not the unreachable `checked`-clause line).
2. **F-03** — the Out-of-Scope row superseding the py3.9-backlog non-filing decision.
3. **D-04's rejection of P-13's "load-bearing" canary**, its four reasons, and its explicit
   reopening condition (an abort mode that emits a valid `(checked N source files)` clause over a
   truncated file set).
4. **D-11's single-dispatch residual** — Phase 132's own dispatch is assumed to serve as the
   hardened-gate-in-CI proof; if Phase 132 is replanned without one, this phase owes a second run.
5. **D-13's two backlog filings** (999.26, 999.27) and the superseded Out-of-Scope row (F-03).
6. **D-14's judgement** on the `mypy<3` bound and its raise protocol.
7. **D-16's forward-looking note** for Phases 133/134: prefer `chip_test.py` (scanned by
   `check_devtest_orchestrator.py` in FULL) over adding new helpers to `cli_handlers.py`'s
   `dev_test`, sidestepping the allow-list maintenance burden entirely.
8. **D-17's three-way correction** to the research record (wrong repo, wrong commit, not a weakened
   assertion) — and the further correction that STATE.md's own phrasing is the mischaracterisation's
   source.
9. **D-18's latent carry** — `81fa53c` present in the app repo, acting deferred until `main` is
   actually merged in any of the three repos.
10. **The standing honesty statement (§5)** — RED before and after, by design; the 69-count is
    Phase 132's input, not this phase's achievement.
11. **How GATE-07's prohibition was actually upheld (§4a)** — operator-executed dispatch, agent
    attempt denied by the harness classifier under explicit operator authorization. Do not read this
    phase as evidence that an agent will never attempt a dispatch.

### 6a. Execution-environment facts (tooling, not phase, defects)

Recorded because each cost real time this phase and will recur in 132–137. None is a defect in the
work; all are properties of the harness or the devcontainer.

- **Worktree isolation was disabled for the entire phase, deliberately.** Five plans
  (`131-01/02/03/04/06`) touch the `firestarter_app` submodule, and the executor commit protocol
  cannot commit into a submodule from an isolated worktree. The other two (`131-05`, `131-07`)
  touch only `.planning/` but hardcode `/workspaces/firestarter_app` and `/workspaces/.planning/…`
  absolute paths **inside their own acceptance gates** — in a worktree those gates would have
  measured the main checkout while the agent wrote elsewhere, passing or failing for entirely the
  wrong reason. Same defect class as Phase 129. **Expect this for every host-only v1.30 phase:**
  either keep worktrees off, or write gate paths relative to the plan's own tree.
- **`131-02`'s plan contained a second UNREACHABLE gate leg — independent of F-07.** Its literal
  revert instructions (reorder the returncode guard, keep the anchored completion-clause regex) are
  *structurally incapable* of producing a RED. The executor established that empirically rather than
  assuming the plan was right, then reproduced a genuine RED using the actual pre-131-01 loose regex
  read from `git show 16a313a:tools/check_mypy_watermark.py`. Two unreachable pre-authored legs in
  one phase (this and F-07) is the signal worth carrying: **a RED that has not been *seen* to fail
  for the right reason proves nothing**, and a plan asserting a revert will fail is not evidence.
- **`.planning/STATE.md` was corrupted three times by gsd state writers** — `state.begin-phase` once
  at phase start, `state.record-session` twice inside executors. Damage pattern: the first physical
  line of a multi-line body paragraph replaced with a one-liner while the continuation lines were
  left stranded mid-sentence, plus a stray em-dash prepended to `milestone_name` and the human phase
  title (`Gate Hardening & CI Parity`) swapped for the directory slug. All three were caught by
  diffing and hand-repaired; the orchestrator's repair is `179ea16d`. **Diff STATE.md after every
  state-verb call — the returned `updated` array is not a reliable report of what was written.**
- **`gh` cannot write its default cache directory in this container.** `gh run view --log` and
  `--log-failed` fail with `creating cache directory: mkdir /home/vscode/.cache/gh: permission
  denied` — and `--log` returns *silently empty* rather than erroring, which is the dangerous shape:
  a grep over it looks like "the line is absent" when the log was never fetched. Export
  `XDG_CACHE_HOME` to a writable path first. F-07's "zero `checked` occurrences" finding was
  re-confirmed **after** this redirect, against a genuinely retrieved 635-line log.

## 7. Cross-reference table — GATE-01…GATE-10

| GATE ID | Owning plan | Proving artifact / test function |
|---|---|---|
| GATE-01 | 131-01 (mechanism), 131-02 (proof) | `firestarter_app/tools/check_mypy_watermark.py` (`9465c4c`); `tests/test_check_mypy_watermark.py::test_truncated_run_exits_2` + `::test_end_to_end_terminal_shape_is_legible` (`f76cf94`); D-03's RED-preserving revert (uncommitted, net diff empty) |
| GATE-02 | 131-01 (mechanism), 131-02 (proof) | Same mechanism commit; `tests/test_check_mypy_watermark.py::test_truncated_run_exits_2` (no `checked` clause ⇒ exit 2) and `::test_config_rejection_exits_2` (config diagnostic ⇒ exit 2 independent of the completion clause) |
| GATE-03 | 131-01 (mechanism), 131-02 (proof) | `MIN_CHECKED_SOURCE_FILES = 120`; `tests/test_check_mypy_watermark.py::test_below_coverage_floor_exits_2` |
| GATE-04 | 131-01 (mechanism), 131-02 (proof) | `mypy_argv()` returning `[sys.executable, "-m", "mypy", "firestarter/", "tests/"]`; `tests/test_check_mypy_watermark.py::test_mypy_argv_is_sys_executable_dash_m` |
| GATE-05 | 131-01 | `firestarter_app/pyproject.toml` `[tool.mypy] python_version = "3.10"` (`9465c4c`) |
| GATE-06 | 131-02 | `firestarter_app/tests/test_check_mypy_watermark.py`, 8 tests (`f76cf94`) |
| GATE-07 | 131-05 (delivery), 131-07 (tick) | `131-CI-BASELINE.md` — CI run `30822281624`, `workflow_dispatch` on `beta` @ `16a313a`, verbatim `mypy errors: 69 (watermark: 35)` |
| GATE-08 | 131-03 | `firestarter_app/tests/test_sdp_db_invariant.py::test_sdp_partition_matches_committed_allow_list_element_wise` + `::test_sdp_partition_counts_are_43_41_84`, non-vacuous per `::test_partition_flags_a_moved_chip_non_vacuous` |
| GATE-09 | 131-06 | `firestarter_app/tools/ci_parity.sh` (`8caf77f`) + `131-CI-PARITY.md`'s recorded run (`BOARD-ATTACHED: none`) |
| GATE-10 | 131-04 | `firestarter_app/tests/test_check_devtest_orchestrator.py::test_every_helper_referenced_by_dev_test_is_listed` + `::test_derivation_flags_an_unlisted_helper_non_vacuous` |

---

## 8. Block-scoped outward-facing-command scan (task 2, step c)

Command run, verbatim:

```bash
D=/workspaces/.planning/phases/131-gate-hardening-ci-parity
awk '/^[[:space:]]*<automated>/{b=1} b{print} /<[/]automated>/{b=0}' $D/131-*-PLAN.md \
  | grep -E 'gh workflo[w] run|git pus[h]|git merg[e]|git ta[g]|gh releas[e]|twine uploa[d]'
```

**Output: empty.** `grep` exits 1 (no match) over the extracted `automated` bodies of all seven
`131-*-PLAN.md` files. The `awk` pass is anchored to the start of a line
(`/^[[:space:]]*<automated>/`), so a prose mention of the tag name mid-sentence — e.g.
`131-HANDOFF.md`'s procedure text or 131-05's `<how-to-verify>` checkpoint prose, neither of which is
an `automated` block — cannot open a spurious range. The six forbidden forms are written with a
bracketed final character (`gh workflo[w] run`, `git pus[h]`, etc.) so the scan pattern finds every
real occurrence while containing none of the six literal phrases itself (the self-exclusion problem
this same scan would otherwise trip on its own text).

**Confirms T-131-41's mitigation held**: no privileged command reaches an `automated` block anywhere
in this phase's seven plans.

## 9. Phase-wide prohibition checks (task 2, step d), literal output

All commands re-run in this session, from `/workspaces/firestarter_app` unless noted:

**Watermark unchanged:**
```
$ grep -n 'mypy_error_watermark = 35' pyproject.toml
159:# mypy_error_watermark = 35   # Updated Phase 71-07: floor after 71-06 added test_validate_family_cmd.py (6 AppContext mock-type errors). Prior: 29 (Phase 69-03).
```
Byte-identical to its `16a313a` state (this line is outside the phase's seven-file diff — see below).

**Nothing deleted:**
```
$ git diff --diff-filter=D --name-only 16a313a..HEAD
(empty)
```

**`dev sdp` intact:**
```
$ grep -n 'def dev_sdp' firestarter/cli_handlers.py
2213:def dev_sdp(app: AppContext, eprom: str, mode: str, assume_yes: bool) -> None:
```
Count is 1 — present, unremoved.

**No mypy error fixed — the phase's whole diff over `firestarter_app` touches exactly the seven
permitted files, none under `firestarter/`:**
```
$ git diff --name-only 16a313a..HEAD
pyproject.toml
tests/test_check_devtest_orchestrator.py
tests/test_check_mypy_watermark.py
tests/test_sdp_db_invariant.py
tools/check_mypy_watermark.py
tools/check_no_exists_proxy.py
tools/ci_parity.sh
```
Seven files, matching the acceptance criterion's named list exactly. Zero of them are under
`firestarter/`.

**`requires-python` and the 3.9 classifier unchanged:**
```
$ grep -c 'requires-python = ">=3.9"' pyproject.toml
1
```

**Firmware untouched:**
```
$ git -C /workspaces/firestarter status --short
(empty)
```
HEAD unchanged throughout the phase (confirmed at 131-01 through 131-07, each plan's own SUMMARY
recorded this empty).

**No new skip reason:**
```
$ git diff --name-only 16a313a..HEAD | grep -x 'tests/test_skip_census.py'
(no match, grep exit 1)
$ python3 -m pytest tests/test_skip_census.py -q
.....                                                    [100%]
```
Five tests, all pass. `tests/test_skip_census.py` is not in the phase diff.

**Five pre-existing untracked/modified paths never entered any commit** (`.coverage`,
`.planning/config.json`, `SECURITY.md`, `write_test_port.sh`, the modified `.gitignore` — named at
131-01 plan time): confirmed by the seven-file diff list above containing none of them, across every
commit from `9465c4c` through `8caf77f`.

## 10. Final suite and recipe state (task 2, step e)

`bash tools/ci_parity.sh`, re-run this session from the repo root:

```
=================================
CI-PARITY SUMMARY
=================================
Leg 1 (pytest, empty sibling root):  exit 0
Leg 2 (pytest, sibling present):     exit 0
Leg 3 (ruff check + format --check): exit 0
Leg 4 (mypy watermark gate):         exit 2
BOARD-ATTACHED: none
Python: Python 3.12.13
CI-PARITY: FAIL (legs:4)
```

Matches 131-CI-PARITY.md's originally recorded run exactly, leg-for-leg. **Leg 4's non-zero exit is
the hardened gate working, not a defect** — an ambient numpy PEP-695 stub in this devcontainer
truncates the local mypy run before it reaches a completion clause, and the hardened
`classify_mypy_result` correctly refuses to trust an incomplete run (exit 2), rather than reporting a
plausible-but-wrong count (the pre-hardening behaviour: `mypy errors: 1 (watermark: 35)`, exit 0).
CI itself is expected to exit 1 on this leg (a complete run, 69 errors over the 35 watermark) — both
non-zero, for different, legitimate reasons. **The primary `ci` job stays RED until Phase 132** in
either case.

Full suite independently re-run this session (`python3 -m pytest tests/ -q`, both with the firmware
sibling present and with `FIRESTARTER_FW_ROOT` pointed at an empty directory): **exit 0** in both
conditions (1316 tests collected under the sibling-present layout; the empty-sibling-root run
correctly skips the firmware-dependent subset via `requires_fw`, with zero unexpected failures).
`ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`: both clean
(`All checks passed!` / `116 files already formatted`).

---

## 11. GATE-07 tick — evidence re-read independently

Before ticking `GATE-07`, `131-CI-BASELINE.md` was re-read in full this session (not inherited from
131-05's own say-so). Confirmed present: run id `30822281624` (numeric); full run URL
(`https://github.com/henols/firestarter_app/actions/runs/30822281624`); event `workflow_dispatch`;
branch `beta`; head SHA `16a313a040389aa7c88a98b85f79a7d667ca2f6f` (begins `16a313a`, the stated fork
base); and the verbatim gate-step output:

```
mypy errors: 69 (watermark: 35)
FAIL: 69 errors exceeds watermark 35. New errors introduced.
##[error]Process completed with exit code 1.
```

**Not present, and correctly so per F-07**: a `Found N errors in M files (checked K source files)`
line — structurally absent from this run's log (§ F-07 above), which is why GATE-07's evidence keys
on the `mypy errors: N (watermark: M)` line instead. `GATE-07`'s tick in `.planning/REQUIREMENTS.md`
carries this run id and the explicit qualifier that the count is an input to Phase 132's watermark,
not a Phase 131 claim.

## 12. Requirement ledger verification (task 2, step b) — the other nine ticks

Each of `GATE-01`…`GATE-06`, `GATE-08`…`GATE-10` was independently re-read in `.planning/REQUIREMENTS.md`
this session: all nine checkboxes are `[x]`, all nine Traceability rows read `Complete`, and every one
carries an evidence clause naming a concrete artifact and/or test function (quoted in §7's
cross-reference table above, reproduced from the ledger's own evidence text, not invented here).
**No gap found.** This plan does not re-tick, reword, or otherwise touch any of these nine — only
verifies them, per this phase's own rule that a requirement spanning multiple plans is ticked only by
the last plan in its span, and that gaps are reported, not silently filled.

---

*Phase: 131-gate-hardening-ci-parity*
*Record authored and closed: 2026-08-03, by plan 131-07*

