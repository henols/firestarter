# Phase 132 — mypy Ledger

This is the single file this phase appends its three mypy readings to: this plan's pre-change
reading (section 1, below), plan 132-06's post-fix reading, and plan 132-09's certifying CI
reading. Each reading is read from a run's output, never computed from the others.

## 1. Pre-change reading (this plan, 132-01)

Measured today, 2026-08-03, from `tools/ci_replica_venv.sh`'s leg 4 (this plan's Task 2), run
against `firestarter_app` @ `8caf77f458ba1bd1eeff47f9747838dc4183e2ca` on branch
`gsd/v1.30-sdp-surface-retirement`, inside the numpy-free `.venv/ci-replica` venv the script
builds. This is a fresh measurement taken in this session, not a value carried over from
`131-CI-BASELINE.md`.

**The gate's own stamp lines, verbatim:**

```
checked 121 source files
mypy errors: 69 (watermark: 35)
FAIL: 69 errors exceeds watermark 35. New errors introduced.
```

**mypy's own completion-summary line, verbatim:**

```
Found 69 errors in 17 files (checked 121 source files)
```

**Run stamps, verbatim:**

```
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
MYPY-VERSION: mypy 2.3.0 (compiled: yes)
NUMPY-PRESENT: no
```

**App-repo HEAD and branch:** `8caf77f` (full: `8caf77f458ba1bd1eeff47f9747838dc4183e2ca`), branch
`gsd/v1.30-sdp-surface-retirement`.

**Per-file error distribution** (counted from the run's own detailed mypy output, 69 lines total):

| File | Count |
|---|---|
| `firestarter/eprom_operations.py` | 10 (ring-fenced — `FUT-MYPY-02`, not opened by this phase) |
| `tests/test_dev_test_cmd.py` | 9 |
| `tests/test_write_skip_sdp_unlock.py` | 7 |
| `tests/test_write_skip_erase_0x0d.py` | 6 |
| `tests/test_validate_family_cmd.py` | 6 |
| `tests/test_dev_sdp_cmd.py` | 6 |
| `firestarter/database.py` | 6 |
| `tests/test_serial_comm.py` | 3 |
| `tests/test_revision_constants_parity.py` | 3 |
| `firestarter/firmware.py` | 3 |
| `firestarter/config.py` | 3 |
| `firestarter/ic_layout.py` | 2 |
| `tests/test_provenance.py` | 1 |
| `tests/test_protocol_not_implemented_production_path.py` | 1 |
| `tests/test_eprom_database.py` | 1 |
| `tests/test_characterization.py` | 1 |
| `firestarter/submit.py` | 1 |
| **Sum** | **69** |

**Per-code error distribution** (counted from the same run):

| Code | Count |
|---|---|
| `[arg-type]` | 39 |
| `[union-attr]` | 10 |
| `[assignment]` | 7 |
| `[var-annotated]` | 6 |
| `[attr-defined]` | 4 |
| `[func-returns-value]` | 3 |
| **Sum** | **69** |

**`[var-annotated]` locations, verbatim from the run** (confirms `132-PATTERNS.md`'s
correction — `config.py:84/85/102` and `database.py:174/175/325`, none in `ic_layout.py`):

```
firestarter/config.py:84: error: Need type annotation for "_instances" ... [var-annotated]
firestarter/config.py:85: error: Need type annotation for "_initialized_configs" ... [var-annotated]
firestarter/config.py:102: error: Need type annotation for "_config" ... [var-annotated]
firestarter/database.py:174: error: Need type annotation for "proms" ... [var-annotated]
firestarter/database.py:175: error: Need type annotation for "pin_maps" ... [var-annotated]
firestarter/database.py:325: error: Need type annotation for "pin_signals" ... [var-annotated]
```

**The `[annotation-unchecked]` lines are mypy notes, not errors, and are excluded from the
count.** The same run's output additionally carries 28 lines of the form
`note: By default the bodies of untyped functions are not checked...` /
`[annotation-unchecked]` — these are mypy **notes**, counted separately from mypy's own `Found 69
errors` clause, and are deliberately excluded from every count in this ledger. A later reader who
independently counts every line containing the word "error" or every diagnostic-shaped line in
the raw log and arrives at a number near 97 (69 + 28) is counting notes as errors; this ledger's
69 is correct and matches mypy's own self-reported completion clause exactly.

## 2. Divergence check against Phase 131's inherited 69

This phase's measured count (69) **agrees exactly** with `131-CI-BASELINE.md`'s CI reading of 69
(read verbatim from CI run `30822281624`, `workflow_dispatch` on `beta` @ `16a313a`, mypy 2.3.0,
Python 3.11.15). There is nothing to reconcile: the fork-base count Phase 131 recorded as an
input to Phase 132's watermark is the same number this phase independently re-measures today, in
a different environment (a fresh numpy-free `.venv/ci-replica` venv on Python 3.11.15) against the
same commit family. Per Phase 131 D-12's rule, had these two numbers disagreed, the measured
number would win and both would be recorded without reconciliation — that rule is not invoked
here because no disagreement exists.

## 3. The checked-source-files floor

The measured `checked` value is **121**, against `MIN_CHECKED_SOURCE_FILES = 120`
(`tools/check_mypy_watermark.py:48`) — one file of margin. This phase's own two new files
(`firestarter/sdp_honesty.py`, added by plan 132-02, and `tests/test_sdp_honesty.py`, the `git mv`
target of plan 132-03) are additions with no corresponding net removal, so the checked count can
only rise from 121, never fall below the 120 floor as a side effect of this phase's own work.
**Conclusion: no floor edit is needed or permitted in this phase.** This discharges Phase 131
D-05's "a `git mv` holds the count at 120 — verify" as a verified fact, measured today, rather
than an inherited assumption.

## 4. Projected path to the watermark (a projection, not a claim)

The following arithmetic is a **projection**, not a claim of a measured post-fix count. It is
attributed by owning plan, each subtraction against the measured 69 above:

```
69                                            (this reading, section 1)
 - 6   (plan 132-03: the retargeted tests/test_sdp_honesty.py module needs
        no AppContext factory at all — its production SUT is the new pure
        firestarter/sdp_honesty.py helper, not an AppContext-constructing
        CLI handler)
 - 25  (plan 132-05: the four surviving typed-factory modules —
        tests/test_dev_test_cmd.py (9 in the file total, but the
        AppContext-factory-attributable subset per module boundary is
        counted per the four survivors' own factory-driven errors:
        6 + 6 + 6 + 7 = 25 — test_write_skip_erase_0x0d.py (6),
        test_validate_family_cmd.py (6), test_dev_test_cmd.py (6), and
        test_write_skip_sdp_unlock.py (7, not 6 — this module carries a
        seventh error at :72, `Argument 1 to "EpromOperator" has
        incompatible type "object"`, beyond its own make_app_context
        factory))
 - 6   (plan 132-06: the six [var-annotated] annotations at
        config.py:84,85,102 and database.py:174,175,325)
= 32
```

Watermark stays at 35 → **3 of headroom projected**, versus research's own prior projection of
33 (the measured seventh error in `test_write_skip_sdp_unlock.py` makes it 32, one lower than
research projected). **This is a projection, not a claim.** Plan 132-06 measures the real,
post-fix count in the numpy-free replica venv, and plan 132-09 reads CI's own certifying count —
neither later plan may treat this section's arithmetic as a substitute for its own measurement.

## 5. What this document does not establish

A locally-measured count, in a replica venv, is **not** a green CI job. `firestarter_app`'s
primary `ci` job is **RED at the start of this phase by design** — Phase 131 hardened the
watermark mechanism and fixed zero of the 69 errors it measures; this phase is the one that
attempts the fixes and the certifying dispatch. Nothing in this document is a claim that
anything is green, that the `dev sdp` deletion has landed, or that any mypy fix has been made —
this ledger's section 1 is a **pre-change** reading, taken before a single line of `dev sdp` or a
single mypy fix moves, exactly as this plan's objective requires.

**D-09's accepted cost, stated plainly.** The watermark stays at **35** and is **not ratcheted**
in this phase (see `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CONTEXT.md`
D-09). If the count lands at the projected 32 (section 4), there are **3 of silent headroom** in
what Phase 131 D-04 called the milestone's central honesty artifact — an accepted, stated cost.
The actual defence against new errors sneaking in under that headroom is plan 132-05's typed
`make_app_context` factory (D-10), not a tight watermark. The measured true count this phase
produces becomes a named input to a later phase's ratchet decision — the same "measure, don't
set" split Phase 131 used for its own inherited 69.

## 1a. Behavioural-equivalence proof (plan 132-02)

Before any deletion, `firestarter/sdp_honesty.py` was authored (D-01, D-02) carrying the D-10
honesty caveat and the D-14 unknown-command mapping, and `firestarter/cli_handlers.py`'s
still-live `dev_sdp` subcommand was rewired to obtain both pieces of wording from the helper
instead of composing them inline.

**The unmodified `tests/test_dev_sdp_cmd.py` module was then run against the rewired command:
26 collected, 26 passed, 0 failed, 0 skipped, 0 errors.** No test file was touched in the rewire
commit (`git diff --stat tests/` was empty at commit time).

**Rewire commit sha:** `821ca89c3c744d1b9e2109ee93a2ba6eac3427ff` (`firestarter_app`, branch
`gsd/v1.30-sdp-surface-retirement`).

**What this run exercised.** This is the full delivery path, end to end through `CliRunner`: the
helper's return value → `click.echo` → the user's captured console output. The four surviving
honesty assertions (`test_summary_line_carries_the_unreadable_state_caveat_on_both_directions`,
`test_summary_line_carries_no_duration_figure`, `test_no_fabricated_lock_state_boolean_in_the_report`,
`test_firmware_too_old_is_reported_when_unknown_cmd_comes_back`) all passed against this delivery
path in this run.

**The honest scope limit, stated plainly (D-05).** After plan 132-04 deletes `dev_sdp`, this
delivery path becomes unreachable forever — no test in the tree can prove the helper's output
reaches `click.echo` and a real console again. The four assertions that retarget onto the helper
in plan 132-03 guard the **wording** the helper returns, not its **delivery** through a CLI
command, because between this phase and Phase 134 the caveat has no user-reachable carrier at
all (D-05's stated residual: no honesty caveat is added to the `write` auto-unlock path in this
phase). This run, taken here, is the only point in the phase's history where both the wording and
its delivery were provable in the same assertion set.

**Post-registration mypy count.** `firestarter.sdp_honesty` was appended to `pyproject.toml`'s
Phase-42 production strict-island `[[tool.mypy.overrides]]` module list (now nine modules), with
that block's header comment updated in the same edit to name the ninth module and cite D-02.
`bash tools/ci_replica_venv.sh` was then re-run:

```
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
MYPY-VERSION: mypy 2.3.0 (compiled: yes)
NUMPY-PRESENT: no
Found 69 errors in 17 files (checked 122 source files)
mypy errors: 69 (watermark: 35)
```

**Comparison against section 1's pre-change reading: 69 errors, unchanged.** The checked-file
count rose from 121 to 122 (the one new module), consistent with §3's "adds, never removes"
conclusion. The new module type-checks cleanly under `disallow_untyped_defs = true` /
`check_untyped_defs = true` with zero errors of its own — no regression. Leg 4 of
`ci_replica_venv.sh` still exits 1 (69 > watermark 35), exactly as expected: the watermark is not
ratcheted in this phase (D-09) and no fix has landed yet.

## 6. Measured post-fix reading (plan 132-06)

Measured today, 2026-08-03, from `tools/ci_replica_venv.sh`'s leg 4 (this plan's Task 1/Task 2
verification step), run against `firestarter_app` @ `db990e826fb52d23dea175cbb87fc24f5cf2be85`
on branch `gsd/v1.30-sdp-surface-retirement`, inside the same numpy-free `.venv/ci-replica` venv
plan 132-01 built (leg 1: `REUSED`).

**The gate's own stamp lines, verbatim:**

```
checked 122 source files
mypy errors: 32 (watermark: 35)
INFO: 32 errors -- 3 below watermark (35). The watermark may be lowered to 32, but only if this
run is complete: this run's mypy invocation passed both the completion-clause guard and the
MIN_CHECKED_SOURCE_FILES coverage floor, which is the evidence of completeness. Lower it in the
same commit as the fixes that reduced the count -- never to make a failing gate pass.
```

**mypy's own completion-summary line, verbatim:**

```
Found 32 errors in 12 files (checked 122 source files)
```

**Run stamps, verbatim:**

```
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
MYPY-VERSION: mypy 2.3.0 (compiled: yes)
NUMPY-PRESENT: no
```

**App-repo HEAD and branch:** `db990e8` (full: `db990e826fb52d23dea175cbb87fc24f5cf2be85`),
branch `gsd/v1.30-sdp-surface-retirement` — the second of this plan's two task commits
(`b76b9db` config.py, `db990e8` database.py).

**Subtraction table, one row per contributing plan, expected vs observed:**

| Plan | What it removed | Expected (section 4 projection) | Observed (measured) | Note |
|---|---|---|---|---|
| 132-03 | Section 4 attributed a `-6` step to plan 132-03 ("`tests/test_sdp_honesty.py` needs no `AppContext` factory at all") | 69 → 63 | **No standalone 132-03 reading exists in this ledger.** Section 1a's post-132-02 reading is still 69 (registration only, before deletion). The `-6` did not measure as landed until plan 132-04 physically deleted `dev_sdp` and its local 6-error `make_app_context` copy — recorded as `63` in `132-05-SUMMARY.md`'s own dependency line ("`132-04` ... mypy count re-measured at 63 ... as this plan's pre-change baseline") | **Plan-attribution mismatch, not a count mismatch.** The magnitude (`-6`, landing at 63) is exactly what section 4 projected; the *plan* that physically produced the number was 132-04 (the deletion), not 132-03 (the retarget decision that made the deletion safe). Section 4's prose already hints at this — it describes what 132-03's retarget *implies*, not a reading 132-03 itself took. Recorded here rather than reconciled away, per this task's own instruction |
| 132-05 | The four surviving typed-factory modules' mock-typing errors (`test_dev_test_cmd.py`, `test_write_skip_erase_0x0d.py`, `test_validate_family_cmd.py`, `test_write_skip_sdp_unlock.py`) | `-25` (63 → 38) | `-25` (63 → 38, `132-05-SUMMARY.md`) | Exact match |
| 132-06 (this plan) | The six `[var-annotated]` collection-annotation errors (`config.py:84,85,102`, `database.py:174,175,325`) | `-6` (38 → 32) | `-6` (38 → 32, this reading) | Exact match |

**Remaining error population by file** (12 files, 32 errors, counted from this run's own
detailed mypy output, `: error:` lines only — `[annotation-unchecked]` notes excluded per
section 1's own rule):

| File | Count | Disposition |
|---|---|---|
| `firestarter/eprom_operations.py` | 10 | **Ring-fenced carry — `FUT-MYPY-02`.** One root cause (`[union-attr]`), dispositioned to a future item by operator decision of 2026-08-03. Not opened by this plan; diff confirmed empty |
| `tests/test_serial_comm.py` | 3 | Inside the watermark, not this plan's class |
| `tests/test_revision_constants_parity.py` | 3 | Inside the watermark, not this plan's class |
| `tests/test_dev_test_cmd.py` | 3 | Pre-existing `[attr-defined]` errors, unrelated to this plan (132-05-SUMMARY already recorded these as present before its own changes) |
| `firestarter/firmware.py` | 3 | Inside the watermark, not this plan's class |
| `firestarter/database.py` | 3 | **The three carried assignment errors**, measured at `:296` (`int` assigned to a `list[int]`-typed target), `:384` and `:389` (`float` assigned to `int`-typed variables) — deliberately left untouched per this plan's Task 2 instruction. (Task 2's read-first anchors named `:295`/`:383`/`:388`; the measured lines are one higher at `:296`/`:384`/`:389` — mypy's own output is the authority, consistent with this phase's other line-number corrections) |
| `firestarter/ic_layout.py` | 2 | Inside the watermark, not this plan's class (`[attr-defined]` at `:447`, `[arg-type]` at `:630` per 132-PATTERNS.md's correction) |
| `tests/test_provenance.py` | 1 | Inside the watermark |
| `tests/test_protocol_not_implemented_production_path.py` | 1 | Inside the watermark |
| `tests/test_eprom_database.py` | 1 | Inside the watermark |
| `tests/test_characterization.py` | 1 | Inside the watermark |
| `firestarter/submit.py` | 1 | Inside the watermark |
| **Sum** | **32** | |

**Remaining error population by code:**

| Code | Count |
|---|---|
| `[union-attr]` | 10 (all 10 are the ring-fenced `eprom_operations.py` cluster) |
| `[arg-type]` | 8 |
| `[assignment]` | 7 |
| `[attr-defined]` | 4 |
| `[func-returns-value]` | 3 |
| **Sum** | **32** |

**Projection versus measurement: the projection was right, exactly, at the total.** Section 4
projected **32** as the post-132-06 count (correcting research's own prior projection of 33 by
one, on account of the measured seventh error in `test_write_skip_sdp_unlock.py`). This plan's
measured count is **32** — an exact match at the total. The one divergence found is *not* in the
number but in the per-plan attribution of the `-6` step from 69 to 63 (132-03 named in section 4's
prose vs. 132-04 where the number actually landed), recorded in the subtraction table above rather
than smoothed over. Section 4 itself is unchanged by this append — no line inside it was deleted
or edited.

## 7. The number a later phase ratchets to, and the cost of not doing it here

**The measured true count is 32.** The watermark stays at **35** and is **not** ratcheted in this
plan or this phase (D-09) — this is the same "measure, don't set" split Phase 131 used for its own
inherited 69, applied one level down.

**Two rejected alternatives, both already named in D-09 and reconfirmed here against the now-real
number:**

1. **Setting the watermark to 32 before plan 132-09's single certifying dispatch.** Rejected: a
   ±1 local-versus-CI divergence would redden the gate on the one dispatch this phase is
   structured around, costing a second operator turn to recover. This project's own record
   (`131-CI-BASELINE.md` vs this ledger's own section 2) already contains one instance of a local
   reading and a CI reading needing independent confirmation on this exact class of number — the
   caution is not hypothetical.
2. **Certifying green at 35, then ratcheting to 32 in a second pass within this same phase.**
   Rejected: this would cost two operator push-and-dispatch turns in one phase, where Phase 131
   spent a full turn on one. RETIRE-06 and ROADMAP criterion 4 are both worded as "certify green at
   the existing watermark," not "ratchet it" — a second pass here would be scope this plan and this
   phase were not asked to carry.

**The accepted cost, stated without softening.** `35 - 32 = 3` of silent headroom persists in what
Phase 131 D-04 called the milestone's central honesty artifact. This headroom is not new: it was
already `3` in section 4's own projection, and is now confirmed as a real, measured `3` rather than
a projected one. **The actual defence against new errors of the discharged pattern is plan
132-05's typed `make_app_context` factory (D-10), not a tight watermark** — any new test module
that imports the shared factory instead of hand-rolling a `**overrides: object` copy cannot
reproduce the 30-error class this phase discharged, regardless of where the watermark number sits.

**Named ratchet input, with an owner obligation stated, not discharged.** The number **32** is the
input a later phase's watermark ratchet consumes. Per `132-CONTEXT.md`'s Deferred block, "ratchet
the watermark to the measured true count... needs a named owner or it becomes a seventh consecutive
acknowledgement." This plan does not file that backlog item — filing it is this phase's own
Deferred-block instruction to a later close, not a task this plan's `<tasks>` block assigned. Stating
that absence here, rather than silently letting the number sit unfiled, is the honest form of "named
input."

## 8. Still not established

A locally-measured count, in a replica venv, is **not** a green CI job. Nothing in section 6 or 7
is a claim that `firestarter_app`'s primary `ci` job is green, that RETIRE-06 is satisfied, or that
any CI run has been dispatched. The `ci` job's actual state is unknown until plan 132-09's dispatch
reads it — and per this plan's own `<objective>`, **nothing** in this plan may be marked Complete on
the strength of this local reading alone.

## 9. The certifying CI reading

Read from CI run `30856059940` (`workflow_dispatch` on `gsd/v1.30-sdp-surface-retirement` @
`42a1971`, `ci` job, step `mypy type check (watermark gate)`), via `gh run view 30856059940
--repo henols/firestarter_app --log --job 91827219671` — see `132-CI-GREEN.md` §4-5 for the full
reading and the completion-clause investigation.

**CI reported:**

```
checked 122 source files
mypy errors: 32 (watermark: 35)
```

**This plan's own task 1 local replica re-measurement reported (`132-CI-PARITY.md` §2, same
commit `42a1971`):**

```
Found 32 errors in 12 files (checked 122 source files)
checked 122 source files
mypy errors: 32 (watermark: 35)
```

**CI and local agree exactly: 32 errors, checked 122 source files, watermark 35.** No
reconciliation is needed and none is performed — this is the third independent reading of the same
number (section 1's pre-change 69, section 6's post-fix local 32, and this section's CI 32), and
unlike section 2's fork-base cross-check, there is no divergence to record here. Per D-08/D-12's
rule, had CI and local disagreed, CI's number would be the one RETIRE-06 is certified against and
both would stand recorded without reconciliation — that branch is not invoked because no
disagreement exists.

**Note on this project's own precedent for exactly this class of number.** `131-CI-BASELINE.md` §8
recorded an instance where a fork-base CI reading and a locally/research-measured reading needed
independent confirmation before being treated as equal — the caution that motivated D-09's
"certify at the existing watermark, don't set it to a local reading first" choice
(`132-CONTEXT.md` D-09). That caution is not invoked as a live divergence here; it is cited only
because this section is the one place in the ledger where a live CI/local disagreement *could* have
appeared, and did not.

**This is the number RETIRE-06 and ROADMAP criterion 4 are certified against: 32, three below the
unratcheted watermark of 35.** The watermark itself is untouched by this reading, per D-09 — see
`132-RECORD.md` for the residual headroom arithmetic.
