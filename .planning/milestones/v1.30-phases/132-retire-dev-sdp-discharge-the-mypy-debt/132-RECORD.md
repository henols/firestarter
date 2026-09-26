# Phase 132 Record — Retire `dev sdp` & Discharge the mypy Debt

## Outcome

`firestarter dev sdp` and its four gates are deleted from `firestarter_app`; the honesty wording
and the unknown-command mapping that survived the deletion live in a new shared production module
(`firestarter/sdp_honesty.py`) with four behavioural assertions retargeted onto it; a typed
`AppContext` factory replaces the untyped `**overrides: object` copies that produced ~30 of the
phase's mypy errors; six missing collection-type annotations are added; a three-site tripwire
records the removal-safety dependency on `write`'s auto-unlock default; all five stale
`eprom_operations.py:301`/`:377` dereference citations are corrected to name the real anchors
(`_setup_operation:329`, `_operation_context:405`); and `firestarter_app`'s primary `ci` job — red
for two months, invisible outside PRs and manual dispatch because its `push` trigger is
`main`-only — is now certified GREEN at the existing watermark of 35, with the true count measured
at 32. Certification cost exactly the two privileged operator actions this phase's plan budgeted:
one branch push (creating `gsd/v1.30-sdp-surface-retirement` on origin, which did not exist there
before) and one `workflow_dispatch` (run `30856059940`, conclusion `success`).

**A state change this phase caused that a later reader needs:** the milestone branch
`gsd/v1.30-sdp-surface-retirement` now exists on `origin` (it did not before this phase's task 2),
and the submodule is **28 commits ahead of `origin/beta`** (`git -C firestarter_app rev-list
--count origin/beta..HEAD`). Neither the branch nor those commits are merged into `beta`; that
merge is a later, operator-gated milestone-close action, not something this phase or plan performs.

## Requirements

| ID | Completing plan | Evidence artifact |
|---|---|---|
| RETIRE-01 | 132-04 | `firestarter_app` commit `259a0f0` — `dev_sdp` span + orphaned import deleted; `323c515` — node-scoped `.ambr` update |
| RETIRE-02 | 132-03 | `firestarter_app` commit `7495c9e` — `git mv test_dev_sdp_cmd.py → test_sdp_honesty.py` + `check_no_exists_proxy.py:157` target-list edit, same commit |
| RETIRE-03 | 132-03 | `firestarter_app` commit `3dddfe3` — four honesty assertions retargeted onto `sdp_honesty.py`, no net loss measured (`132-PRUNE-LEDGER.md`) |
| RETIRE-04 | 132-08 | `firestarter_app` commit `831c95f` — `test_command_names_dereferences_both_sdp_commands`, proven by two RED demonstrations |
| RETIRE-05 | 132-05 | `firestarter_app` commit `ab1a9b4` — typed `make_app_context(...) -> AppContext` factory + `app_context` fixture in `conftest.py` |
| RETIRE-06 | 132-09 | `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-GREEN.md` — CI run `30856059940`, conclusion `success`, `mypy errors: 32 (watermark: 35)` |
| RETIRE-07 | 132-07 | `firestarter_app` commits `5ec3a89`/`1fdb455`/`cc5d223` — tripwire comments at the auto-unlock decision site + named test |
| RETIRE-08 | 132-08 | `firestarter_app` commit `42a1971` — all five stale references corrected (not the three the requirement text originally claimed); `.planning/REQUIREMENTS.md` commit `88a521e` — text itself corrected |

All eight accounted for; none partially met.

## Decisions

Fourteen locked decisions from `132-CONTEXT.md`, one line each on how the phase honoured each.

| ID | How honoured |
|---|---|
| D-01 | `firestarter/sdp_honesty.py` authored as the shared production helper; the four honesty tests retarget onto it, not onto a source-string-presence scan and not pre-staged on Phase 135's `write --sdp-relock` path. |
| D-02 | The helper lands at `firestarter/sdp_honesty.py`, added to `pyproject.toml`'s Phase-42 production strict island (now nine modules) in the same edit as its authoring commit — type-checked from birth. |
| D-03 | `git mv tests/test_dev_sdp_cmd.py → tests/test_sdp_honesty.py` and `tools/check_no_exists_proxy.py:157`'s target-list edit landed in one commit (`7495c9e`) — one same-commit edit, as decided. |
| D-04 | The gate-ordering cases whose subject dies with the command (nine-way adapter-required ordering, off-TTY refusal, exit-code contract) are pruned and named in `132-PRUNE-LEDGER.md` §2/§4, not silently absorbed into the `git mv`'s line-count reduction. |
| D-05 | No honesty caveat was added to `write`'s auto-unlock path. The residual — no user-reachable carrier for the caveat between this phase and Phase 134 — is stated plainly below, not closed early. |
| D-06 | GREEN was proven by iterating against a committed numpy-free CI-replica venv (`tools/ci_replica_venv.sh`, authored 132-01) and certifying with exactly one operator push + one dispatch (task 2 of this plan) — no dispatch-per-batch iteration was used. |
| D-07 | The venv recipe is `firestarter_app/tools/ci_replica_venv.sh`, a separate committed script, never folded into `tools/ci_parity.sh` — confirmed by `git diff --stat tools/ci_parity.sh` staying empty across this entire phase. |
| D-08 | Every number in `132-CI-GREEN.md` and this record was read from the run's log via `gh run view`/`--log`, never computed locally; the one clause the log did not literally contain (mypy's raw completion sentence) was investigated rather than substituted (`132-CI-GREEN.md` §5). |
| D-09 | The watermark stayed at 35, unratcheted, through the certifying dispatch. The measured true count (32) is recorded as the input to a later phase's ratchet, not applied here. See the headroom residual below. |
| D-10 | `tests/conftest.py` carries a typed `make_app_context(...) -> AppContext` factory with explicit typed keyword parameters (no `**overrides: object`) plus a thin `app_context` fixture, authored in 132-05 before any of the migrating modules were touched. |
| D-11 | Every corrected `eprom_operations.py:301`/`:377` citation now names `_setup_operation`(`:329`)/`_operation_context`(`:405`) function-name-first, with the line number alongside, across `constants.py` and `test_revision_constants_parity.py` (132-08). |
| D-12 | **Honoured in a non-literal form.** RETIRE-08's text correction could not land "in the same commit" as its fixes because the fixes are a submodule commit (`42a1971`) and the text is a meta-repo commit (`88a521e`) — two git repositories cannot share a commit. Honoured instead as adjacent, cross-citing commits: `42a1971`'s message names the meta-repo file and requirement it awaits; `88a521e`'s message names `42a1971` (and `831c95f`) by SHA. Stated explicitly in `132-08-SUMMARY.md`, not silently worked around. |
| D-13 | The `.ambr` update (132-04 task 2) was scoped to the `test_help_dev` node id only, reviewed against the named expected shape ("only line 141's `sdp` line is removed"), never a broad `--snapshot-update`. |
| D-14 | The P-21 tripwire landed at the decision site — `cli_handlers.py`'s `skip_sdp_unlock` defaults and D-04 auto-set block, plus `constants.py`'s `FLAG_SKIP_SDP_UNLOCK` definition — not at the `eprom_operations.py` audit site R-7 found mis-attributed (132-07). |

**Two decisions honoured in a non-literal form, both already flagged above:** D-12 (impossible
cross-repository "same commit," honoured as adjacent cross-citing commits) and — worth restating
because it is easy to miss in a table — **RETIRE-03's "retargeted onto the new leg" wording**,
which `132-CONTEXT.md`'s own live correction #1 established is **not executable in Phase 132**: the
leg is Phase 134's, and the wording's only production carrier (`cli_handlers.py:2215/2267/2316-18`)
sat inside the deleted `dev_sdp` span. RETIRE-03 was honoured instead by retargeting onto the
shared helper (`sdp_honesty.py`) this phase authored, which is what makes the wording reachable by
Phase 134's leg at all, rather than by a leg that does not yet exist.

## Corrections

Every place a prior artifact was measured wrong and corrected at plan or execution time, at least
seven, each naming the wrong artifact, the measured truth, and how it was measured.

| # | Artifact measured wrong | Measured truth | How measured |
|---|---|---|---|
| 1 | `REQUIREMENTS.md`'s RETIRE-08 text ("three" stale references) | **Five**, across two files: `constants.py:69-70` (one) and `test_revision_constants_parity.py:71-72`/`:527`/`:549`/`:585-586` (four) | `grep -rn` for the stale `301`/`377` tokens across both files, enumerated in `132-CONTEXT.md`'s live correction #2 and re-confirmed at 132-08 execution time |
| 2 | `132-PATTERNS.md`'s `[var-annotated]` candidate list (named `ic_layout.py:233`'s bare `properties = []` as a third target file) | `ic_layout.py` carries **zero** of the six `[var-annotated]` errors; all six landed in exactly two files — `config.py` (3: `:84`,`:85`,`:102`) and `database.py` (3: `:174`,`:175`,`:325`) | The actual 132-01 mypy run's verbatim per-error output, recorded in `132-MYPY-LEDGER.md` §1, which states explicitly "confirms 132-PATTERNS.md's correction" |
| 3 | `132-PATTERNS.md`'s own re-verified `database.py` line numbers (claimed `:173`/`:174`) | `132-CONTEXT.md`'s original numbers were right: `:174`/`:175` (plus `:325`, uncontested) | The 132-01 mypy run's verbatim output (`132-MYPY-LEDGER.md` §1) matches `:174`/`:175`/`:325`, not `:173`/`:174` |
| 4 | `132-PATTERNS.md`'s re-measurement of the `Confirm.ask` prompt-call anchor (claimed the call sits where the prompt *string* is defined) | The call itself is at `cli_handlers.py:2270`, not `:2267` (`:2267` is inside the prompt string literal) | Live re-read of `cli_handlers.py` at plan-authoring time, recorded in `132-PATTERNS.md:324-325` |
| 5 | `132-CONTEXT.md`'s honesty-`click.echo` span citation (`:2316-2318`) | The actual span is `:2315-2319` | Live re-read of `cli_handlers.py`, recorded in `132-PATTERNS.md:74` |
| 6 | `132-CONTEXT.md`'s `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK` constant-definition line numbers (`:72`/`:73`) | The actual definitions are at `:73`/`:74` | Live re-read of `constants.py`, recorded in `132-PATTERNS.md:542-543` |
| 7 | `tools/check_mypy_watermark.py`'s `MIN_CHECKED_SOURCE_FILES = 120` floor, treated as matching the tree's actual checked-file count | The measured `checked` value throughout this phase is **121** (pre-change) rising to **122** (post-registration of `sdp_honesty.py`) — one and two files of margin respectively, never below the floor | `132-01`'s and `132-02`'s replica-venv runs, recorded in `132-MYPY-LEDGER.md` §3 and §1a |

## Residuals

Stated plainly, without softening.

1. **The honesty caveat has no user-reachable carrier between this phase and Phase 134.** The four
   surviving assertions (`132-PRUNE-LEDGER.md` §1) now pin the wording `sdp_honesty.py` returns,
   not its delivery through a CLI command — the delivery path was proven exactly once, in plan
   132-02's equivalence run against the still-live `dev_sdp` command (`132-MYPY-LEDGER.md` §1a: the
   unmodified 26-test suite, 26 passed, against the rewired command), and cannot be re-proven from
   the tree after 132-03's move made the delivery path unreachable forever. D-05 declined to close
   this gap early, on purpose — `write`'s auto-unlock makes no claim about lock state, so there was
   no dishonest claim in this phase's own scope to caveat.

2. **Silent watermark headroom persists.** The measured true count is **32**; the watermark stays
   at the unratcheted **35** — `35 - 32 = 3` of silent headroom in what Phase 131 D-04 named the
   milestone's central honesty artifact. This is not new: it was projected at 3 in
   `132-MYPY-LEDGER.md` §4 before any fix landed, and is now confirmed as a real, CI-certified 3
   rather than a local projection (§9, this ledger's third reading). The actual defence against new
   errors of the discharged 30-error pattern is D-10's typed `make_app_context` factory, not a tight
   watermark. **This number is a named input to a later phase's ratchet, not yet filed as its own
   backlog item** — `132-CONTEXT.md`'s Deferred block requires that filing carry a named owner or it
   becomes a seventh consecutive acknowledgement; this plan's own `<tasks>` block did not assign that
   filing, so it is named here as still outstanding rather than silently left unfiled.

3. **The ring-fenced ten `[union-attr]` errors in `eprom_operations.py` remain**, dispositioned by
   the 2026-08-03 operator decision recorded in `REQUIREMENTS.md`'s Out-of-Scope table →
   `FUT-MYPY-02`, untouched by design throughout this phase (`git diff --stat
   firestarter/eprom_operations.py` stayed empty across every plan, confirmed again by this plan's
   task 1 and by `132-CI-GREEN.md`'s certifying run), and visible in `132-MYPY-LEDGER.md` §6's
   remaining-error-by-file table rather than absorbed into an unattributed remainder.

4. **The coverage-gate gap in the parity recipe remains a gap in that recipe specifically.**
   `tools/ci_parity.sh`'s legs 1/2 still run pytest with no coverage flags at all — that recipe never
   gained a coverage leg in this phase, by design (D-07: it is a faithful CI-path mirror, not a
   coverage-floor check). `tools/ci_replica_venv.sh`'s leg 5 is the artifact that closes this gap,
   running pytest with CI's exact `--cov-fail-under=70` invocation. A later reader must not assume
   `ci_parity.sh` alone proves the coverage floor holds — it does not, and was never asked to.

**The pre-existing-dirt substitution, stated rather than silently claimed.** This plan's own
acceptance criterion that `git -C /workspaces/firestarter_app status --porcelain` reads empty was
**unreachable before this phase began** — measured at meta `666d2512` / app `8caf77f`, before this
phase wrote a single line: `firestarter_app` already carried ` M .gitignore`, `?? .coverage`,
`?? .planning/config.json`, `?? SECURITY.md`, `?? write_test_port.sh`, none attributable to Phase
132 and none deleted or gitignored to force emptiness. This record and `132-CI-PARITY.md` §2 both
discharge that criterion as a **delta check** instead: at every measurement point in this phase,
`status --porcelain` contained exactly that baseline dirt and nothing more — confirmed most recently
at this plan's task 1 (`132-CI-PARITY.md` §2) and unchanged since.

## The split, said out loud

This phase proves the command `dev sdp` is *gone* and the primary `ci` job is *green*. **It proves
nothing about SDP behaviour on silicon.** The `0x0D` SDP protocol stays `UNVERIFIED` at the database
level; no AT28C-family part carrying it has ever been in operator inventory; and the causal claim
"the lock inhibited a write" is reachable only from a community `dev test` report (`gh#20`) that, by
design, does not gate this milestone's close. `132-CI-GREEN.md` §9 states this identically at the
level of the certifying run itself.

## Forward handoff

What Phases 133 and 134 inherit from this phase:

- **The typed `make_app_context(...) -> AppContext` factory + `app_context` fixture** in
  `tests/conftest.py` (D-10, 132-05) is the pattern any new test module authoring an `AppContext`
  must use — hand-rolling a sixth `**overrides: object` copy reproduces exactly the error class this
  phase discharged, regardless of where the watermark sits.
- **The watermark is settled at 35, with a measured true count of 32 (3 of headroom).** No later
  phase in this milestone should redden the `ci` job's mypy gate; any new error pushes directly into
  that headroom, not into slack that does not exist.
- **`firestarter/sdp_honesty.py`'s API is a forward contract, not an internal detail.** Phase 134's
  leg report rows and Phase 135's `write --sdp-relock` (if and when scoped) are its next intended
  callers — its `emission_summary` and `map_unknown_cmd_to_outdated` functions are named for what
  they carry, not for the retired `dev sdp` command, precisely so they read correctly from either
  caller.
- **Phase 134 is what finally gives the honesty caveat a user-reachable carrier again** — closing
  residual 1 above. Until then, the caveat's wording is pinned by four tests with no CLI delivery
  path proving it reaches a console.

---

*Phase: 132-retire-dev-sdp-discharge-the-mypy-debt*
*Recorded: 2026-08-03, plan 132-09 task 4, after RETIRE-06's certifying CI read as `success`.*
</content>
