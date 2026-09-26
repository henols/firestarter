---
status: passed
phase: 131-gate-hardening-ci-parity
verified: 2026-08-03
score: 10/10 must-haves verified
author: orchestrator (inline) — see "Independence limitation" below
independence: limited
---

# Phase 131 Verification — Gate Hardening & CI Parity

## Independence limitation (read this first)

**This report was authored inline by the execute-phase orchestrator, not by an independent
`gsd-verifier` agent.** The dispatched verifier terminated early on a provider session limit
(`resets 16:10 UTC`) after 44 tool calls, without writing a report. Re-dispatching before the reset
risked an identical death mid-run.

What that costs: the agent that shaped the executors' instructions also graded the result, so any
error baked into those instructions would be verified against its own premise. What it does *not*
cost: every finding below is a mechanical, re-runnable measurement whose outcome does not depend on
who ran it — three of them are destructive mutation tests. The commands are recorded inline so any
reader can reproduce them.

**Recommendation:** run one independent pass (`/gsd-verify-work 131`, or re-dispatch `gsd-verifier`
after the quota reset) before Phase 132 consumes the 69-count. This is a real gap, not a formality —
flagged rather than papered over, consistent with this phase's own subject matter.

## Verdict

**PASSED — 10/10 requirements verified.** GATE-01…GATE-10 are ticked in both the REQUIREMENTS.md
checkbox list and the Traceability table, each with evidence that was independently re-measured
rather than accepted from a SUMMARY.

## The claim that mattered most: are these gates fail-PROVABLE, or merely present?

This phase's subject is gate honesty, and it already surfaced two pre-authored gate legs that could
not fail as written (F-07, and 131-02's revert instructions). So presence was not accepted as proof.
Three gates were **mutation-tested**: the mechanism was deliberately broken, the test was required to
go RED *for the right reason*, and the tree was restored and re-verified clean.

| Gate | Mutation applied | Result | Failed for the right reason? |
|---|---|---|---|
| GATE-03 | `MIN_CHECKED_SOURCE_FILES` 120 → 0 | `test_below_coverage_floor_exits_2` FAILED — `DID NOT RAISE SystemExit`, captured stdout `checked 4 source files` | Yes — floor no longer triggers, which is exactly the mutated property |
| GATE-08 | dropped one entry from `_COMMITTED_SDP_ALLOW_ENTRIES` | `test_sdp_partition_matches_committed_allow_list_element_wise` FAILED, naming `ATMEL/AT28BV256,AT28LV256` and classifying it under *"Entered ALLOW (widening signal)"* with *"Left ALLOW (narrowing signal): []"* | Yes — and it proved the comparison is **live and directional**, distinguishing narrowing from widening as the requirement demands |
| GATE-10 | `for stmt in dev_test_node.body:` → `for stmt in [dev_test_node]:` (reinstating the naive whole-node walk) | BOTH `test_every_helper_referenced_by_dev_test_is_listed` and `test_derivation_flags_an_unlisted_helper_non_vacuous` FAILED — the real test caught `_complete_eprom` leaking from the `shell_complete=` decorator argument, the synthetic one caught `_decorator_only_helper` | Yes — precisely correction F-04's failure mode, caught from two independent directions |

All three mutations restored to a clean diff (`git diff --quiet` per file: CLEAN), and the full suite
returns exit 0 afterwards. **These gates can fail. They are real.**

A first mutation attempt on GATE-10 mis-targeted the idiom and did not apply; it is recorded here
because the suite passed during that attempt, and a careless reader of that run would have concluded
the gate was proven when nothing had been mutated. The mutation was re-applied correctly before any
conclusion was drawn. This is the same failure shape as F-07 and 131-02's unreachable RED — a green
that means nothing — encountered a third time, during verification itself.

## Requirement-by-requirement

| ID | Verified how | Result |
|---|---|---|
| GATE-01 | `classify_mypy_result` / `enforce_watermark` split present in `tools/check_mypy_watermark.py`; 8 tests in `tests/test_check_mypy_watermark.py` pass | ✓ |
| GATE-02 | `returncode` consulted before the regex (source read at `:12`, `:133`); completion clause required | ✓ |
| GATE-03 | `MIN_CHECKED_SOURCE_FILES = 120` at `:48`; **mutation-proven** above | ✓ |
| GATE-04 | `sys.executable` at `:109-112`, built at call time; `test_mypy_argv_is_sys_executable_dash_m` | ✓ |
| GATE-05 | `pyproject.toml:155` `python_version = "3.10"`, with the discarded-`"3.9"` comment at `:153-154` referencing backlog 999.27 | ✓ |
| GATE-06 | `tests/test_check_mypy_watermark.py` exists — the gate's first-ever paired suite — 8 tests, all pass | ✓ |
| GATE-07 | CI run `30822281624` re-read independently via `gh run view`: `workflow_dispatch` on `beta`, headSha `16a313a040389aa7c88a98b85f79a7d667ca2f6f`, job `ci` `failure`, sole failing step `[11] mypy type check (watermark gate)`, steps `[12]`/`[13]` skipped, both ruff steps success, job `ci-py32` success. Verbatim `mypy errors: 69 (watermark: 35)`. mypy 2.3.0, Python 3.11.15 | ✓ |
| GATE-08 | 7 tests in `tests/test_sdp_db_invariant.py` pass; **mutation-proven** above | ✓ |
| GATE-09 | `tools/ci_parity.sh` executed independently: legs 1–3 exit 0, leg 4 exit 2, `BOARD-ATTACHED: none`, aggregate exit 1 — matching `131-CI-PARITY.md` exactly | ✓ |
| GATE-10 | 18 tests in `tests/test_check_devtest_orchestrator.py` pass; **mutation-proven** above | ✓ |

## Fabrication check (explicitly prohibited, explicitly verified)

`131-CI-BASELINE.md` contains **zero** occurrences of a synthesized
`Found N errors in M files (checked K source files)` line. That clause is structurally absent from
the real CI log — the fork-base `check_mypy_watermark.py` captures mypy's stdout and prints only its
own two derived lines — and writing one would have forged output CI never emitted. Its absence is
correct; F-07 records the amendment. Confirmed against a **genuinely retrieved** 635-line log, after
redirecting `XDG_CACHE_HOME` (unredirected, `gh run view --log` returns silently empty, which would
have made "zero occurrences" meaningless).

## Overclaim check

Clean. No phrase asserting a watermark was set, errors were fixed, or CI went green. The record
states affirmatively: *"Set no watermark"* (`:154`), *"Fixed none of the inherited mypy errors. Not
one of the 69."* (`:158`), and *"RED before this phase and RED after it, by design"* (`:206`), with
the 69-count framed as an input to Phase 132 rather than a Phase 131 achievement. Not the v1.22 C-5
class.

## Scope containment

`git -C firestarter_app diff --name-only 16a313a..HEAD` = exactly the 7 permitted paths
(`pyproject.toml`, three `tests/` files, `tools/check_mypy_watermark.py`,
`tools/check_no_exists_proxy.py`, `tools/ci_parity.sh`). `--diff-filter=D` empty — nothing deleted.
Nothing under `.github/`. `git -C firestarter status --short` empty, firmware HEAD unchanged.
Full suite exit 0; `ruff check` and `ruff format --check` clean at CI's scope (`firestarter/ tests/`).

Pre-existing, not attributable to this phase: `ruff check tools/` reports 4 errors in files this
phase did not touch (`tools/` is outside CI's lint scope; both `tools/` files this phase *did* touch
are clean), and `firestarter_app/.gitignore` carries an unrelated uncommitted `+consistency*` line.

## Human verification

None required. The one human-action gate (GATE-07's `ci.yml` dispatch) was discharged by the operator
during execution — run `30822281624`. See `131-RECORD.md` §4a for how that prohibition was upheld,
including the agent's denied attempt under operator authorization.

## Carried forward

`131-RECORD.md` §6 (ten-item Phase 137 hand-off), §4a (GATE-07 prohibition mechanics), and §6a
(execution-environment facts: worktrees off phase-wide, two unreachable pre-authored gate legs, three
STATE.md writer corruptions, the `gh` cache-dir trap). The independence limitation at the top of this
report should be carried into Phase 137's ledger as well.
