# 132-CI-GREEN: The certifying `ci` job run — RETIRE-06 / ROADMAP criterion 4

**Owner requirement:** RETIRE-06. **Status:** GREEN, certified.

## 1. The run

| Field | Value |
|---|---|
| Run id | `30856059940` |
| URL | https://github.com/henols/firestarter_app/actions/runs/30856059940 |
| Event | `workflow_dispatch` |
| Head branch | `gsd/v1.30-sdp-surface-retirement` |
| Head SHA | `42a1971a072db2f3bcec558a3dc2bcb3d5d65e08` |
| Created | `2026-08-03T21:46:54Z` |
| Status | `completed` |
| **Conclusion** | **`success`** |

Both privileged actions (branch push, workflow dispatch) were performed by the **operator**, in
order, per this plan's task 2 handoff. No agent ran `git push` or `gh workflow run`. Every command
in this document is a read-only `gh run view` call, with `XDG_CACHE_HOME` exported to a writable
path (`/tmp/claude-1000/-workspaces/26f481f6-8c4e-4749-896a-422c0cdfe9de/scratchpad/ghcache`) before
any `--log` retrieval, per the recorded failure mode that log retrieval returns silently empty
without one.

## 2. Fail-closed precondition, seven-point, checked before any substantive reading

Via `gh run view 30856059940 --repo henols/firestarter_app --json databaseId,url,event,headBranch,headSha,createdAt,conclusion,status,jobs` (read-only):

1. Run id `30856059940` is numeric — **pass**
2. `gh run view` resolves it — **pass**
3. `event` is `workflow_dispatch` — **pass**
4. `headBranch` is `gsd/v1.30-sdp-surface-retirement` (the milestone branch) — **pass**
5. `headSha` (`42a1971a072db2f3bcec558a3dc2bcb3d5d65e08`) equals
   `git -C /workspaces/firestarter_app rev-parse HEAD` at plan time — **pass**
6. Run id is not the Phase 131 fork-base run `30822281624` — **pass**
7. `conclusion` is terminal (`success`, not `null`/in-progress) — **pass**, keyed on `conclusion`
   rather than `status` or `outcome`, per this project's own Phase 128 run-B receipt that those
   three fields are not interchangeable

No condition failed. Proceeding to read the run.

## 3. The `ci` job — per-step statuses

Read via `gh run view 30856059940 --repo henols/firestarter_app --json jobs` (job id
`91827219671`, name **`ci`**):

| # | Step | Conclusion |
|---|---|---|
| 1 | Set up job | success |
| 2 | Run actions/checkout@v4 | success |
| 3 | Set up Python 3.11 | success |
| 4 | Catalog validity check | success |
| 5 | Codegen drift gate (messages.py) | success |
| 6 | Vector catalog validity check | success |
| 7 | Codegen drift gate (frame_vectors.py) | success |
| 8 | Install package + test deps | success |
| 9 | ruff lint | success |
| 10 | ruff format check | success |
| 11 | **mypy type check (watermark gate)** | **success** |
| 12 | **Run pytest with coverage** | **success** |
| 13 | **Smoke test — firestarter entry point and --help** | **success** |
| 25 | Post Set up Python 3.11 | success |
| 26 | Post Run actions/checkout@v4 | success |
| 27 | Complete job | success |

Every step in the **`ci`** job succeeded. In particular, the mypy gate step (11) and both steps
after it (12, 13) — which at the Phase 131 fork base **failed** (step 11) and **never ran**
(steps 12, 13 were `skipped`) — now show `success`. This is the shape the fork-base record
(`131-CI-BASELINE.md` §3) predicted for a hardened, discharged run.

**The sibling job `ci-py32`** (id `91827219611`) also concluded `success`. **This is recorded as
an observation only — it is outside the RETIRE-06 claim in both directions.** `ci-py32` installs
the optional `[py32]` USB extra and runs no ruff, no ruff-format, no mypy gate, no coverage step
and no codegen-drift step (per `132-09-PLAN.md`'s `workflow_facts` block); its success does not
support this certification, and — symmetrically — had it failed, that would not have failed
RETIRE-06. A record stating only "the ci job passed" without this exclusion would be the
ambiguity this project's overclaim history is made of; this record states it explicitly, in both
directions.

## 4. The verbatim gate-step output

Read via `gh run view 30856059940 --repo henols/firestarter_app --log --job 91827219671`, step
`mypy type check (watermark gate)`. These are the substantive lines that step emitted, quoted
verbatim, in order:

```
checked 122 source files
mypy errors: 32 (watermark: 35)
INFO: 32 errors -- 3 below watermark (35). The watermark may be lowered to 32, but only if this
run is complete: this run's mypy invocation passed both the completion-clause guard and the
MIN_CHECKED_SOURCE_FILES coverage floor, which is the evidence of completeness. Lower it in the
same commit as the fixes that reduced the count -- never to make a failing gate pass.
```

The `mypy errors: 32 (watermark: 35)` line matches this plan's required pattern exactly.

## 5. Mypy's own completion clause — investigated, found structurally absent from this step's
   output by construction, and the completion proven anyway from the gate's own guard structure

**The literal mypy line `Found 32 errors in 12 files (checked 122 source files)` does not appear
in this step's log**, verified by `gh run view 30856059940 --repo henols/firestarter_app --log
--job 91827219671 | grep -c "Found.*error"` → `0`. This absence is investigated below rather than
either ignored or papered over with a locally-computed substitute (D-08).

**Why, structurally — and why this is a different absence from Phase 131's F-07.** F-07
(`131-CI-BASELINE.md` §5) found the clause absent because the *pre-hardening* checker's regex
(`re.search(r"Found (\d+) errors?", output)`) never captured the `(checked K source files)`
portion at all, and its `main()` never printed mypy's raw output — the clause was discarded before
it could reach any log, by a checker that could not have printed it even if asked. This run uses
the *hardened, post-131* `check_mypy_watermark.py` (read from `firestarter_app` @ `42a1971`,
unchanged from plan 132-08). Its `classify_mypy_result()` **does** capture and successfully match
the full clause via `_FOUND_RE` — `r"^Found (\d+) errors? in \d+ files? \(checked (\d+) source
files?\)$"` — because that match is what produces both the `count` and `checked` values used in
this step's own printed lines (§4). What the *hardened* checker's success path does **not** do is
echo mypy's raw `result.stdout`/`result.stderr` back to the caller on the passing branch — `main()`
calls `classify_mypy_result()` then `enforce_watermark()`, and neither prints the raw text; the raw
output is only ever printed (via `output.strip()`) inside the four `sys.exit(2)` failure branches
(lines 152–205 of `tools/check_mypy_watermark.py`). The workflow step invokes
`python tools/check_mypy_watermark.py` directly — the same code path `ci.yml` has always used — so
this step's log carries only the gate's own two derived stamp lines plus its INFO line, never
mypy's own raw completion sentence. (Contrast `tools/ci_replica_venv.sh`'s leg 4, which
deliberately re-parses `run_mypy()`'s raw output a second time with its own copy of the same regex
specifically so its own log carries the raw line too — that is a property of the replica script's
extra instrumentation, not of the gate itself.)

**The run's completion is provable from the gate's own guard order, without computing anything
locally.** `classify_mypy_result()`'s guards run in a fixed, hoisted order (its own docstring,
quoted in `tools/check_mypy_watermark.py:133-150`): guard 1 (`returncode not in (0, 1)`), guard 2
(a config-rejection diagnostic), then either the clean-run or found-errors regex, then guard 5 (**no
completion clause matched at all** — the truncated-run shape), then guard 6 (`checked` below the
120 floor). Each failing guard `sys.exit(2)`s with a distinct `ERROR:` message *before* the
function ever reaches its final `print(f"checked {checked} source files")` (line 207) and `return
count`. This step's own log contains that exact `checked 122 source files` line (§4) — which is
**only reachable if guard 5 did not fire**, i.e. only if `_FOUND_RE` matched mypy's raw output
internally. A run that aborted, crashed, or produced no parseable clause would have printed one of
the four `ERROR:` messages instead and exited 2 — the job's `mypy type check (watermark gate)` step
would then show `failure`, not `success`. Since the step's recorded conclusion is `success` (§3)
and its log shows the post-guard-5 stamp lines and nothing resembling an `ERROR:` prefix, the
completion clause was present and consumed internally by mypy's own regex match, even though its
literal text is not re-printed to this log. **This is an investigation of the run's completeness
from the gate's own documented control flow, not a locally-computed substitute for the count** —
the count itself (`32`) is read verbatim from line §4, never recomputed.

## 6. Resolved versions

Both read from the log, never invoked locally:

- **mypy:** `2.3.0` — from step `Install package + test deps`'s
  `Successfully installed … mypy-2.3.0 …` line (job `ci`, resolved as a dependency of
  `firestarter==3.0.0b15` against the `mypy>=2.1.0,<3` bound).
- **Python:** `3.11.15` — from step `Set up Python 3.11`'s
  `Successfully set up CPython (3.11.15)` line.

Both match `131-CI-BASELINE.md`'s §6 readings and this phase's own local replica-venv readings
exactly.

## 7. Coverage result

From step `Run pytest with coverage`'s own output, verbatim:

```
TOTAL                               4743    867    82%
Required test coverage of 70% reached. Total coverage: 81.72%
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
```

and, from the pytest summary line further down the same step:

```
1251 passed, 46 skipped in 81.04s (0:01:21)
```

**Coverage is 81.72% against the workflow's 70% floor — well clear.** This exactly matches this
plan's own task 1 local reading (`132-CI-PARITY.md` §2) and plan 132-08's prior reading, confirming
the ~126-line-of-production plus ~550-line-of-test deletion this phase made did not push the suite
toward the floor at any point in this phase's history.

**The pass/skip split (1251/46) differs from this devcontainer's local reading (1297 passed, 0
skipped in the sibling-present leg) — expected, and attributable, not a defect.** CI's `ci` job
checks out `firestarter_app` alone with no firmware sibling and no meta-repo work tree present
(the genuine standalone-CI condition this phase's leg 1 mirrors), and does **not** install the
optional `[py32]` extra (only `ci-py32` does). Reading the step's own `SKIPPED` lines: 43 are the
same firmware-checkout-absent skips this plan's own local leg 1 recorded verbatim in
`132-CI-PARITY.md`, plus 3 more specific to CI's checkout shape —
`test_audit_coverage_matrix.py:615` (meta-repo ledger absent) and
`test_variant_decode_evidence_stability.py:147`, `[2]` (meta-repo `EVIDENCE.json` absent) — both
skip because the standalone `ci` job has no `.planning/` meta-repo tree at all, unlike this
devcontainer's sibling-checkout layout. `43 + 3 = 46`, the total. `1251 + 46 = 1297`, matching every
other reading of this phase's collected test count exactly. No test failed, and no SDP-related or
mypy-related test contributed to either skip category.

## 8. Discharging Phase 131 D-11

Phase 131 D-11 deferred a promise: "this discharges Phase 131 D-11's promise that 132's own
dispatch is the hardened-gate-in-CI proof" (`132-CONTEXT.md` D-06). **This run discharges that
promise.** It is the first CI run in which the *hardened* `check_mypy_watermark.py`
(GATE-01…GATE-04, Phase 131) both ran to completion in the `ci` job and reported a passing count —
proven by §5's guard-order argument and §3's per-step green table. The Phase 131 fork-base run
(`30822281624`) exercised the pre-hardening checker only, on a tree with zero of the 69 errors
fixed; this run exercises the hardened checker's success path for the first time in CI, at the
measured count of 32. Phase 131 D-11's deferred obligation is closed by this run, not by any local
measurement.

## 9. What this run does not establish

This run proves the `firestarter_app` command `dev sdp` is gone and the primary `ci` job is green.
**It proves nothing about SDP behaviour on real silicon.** The `0x0D` SDP protocol stays
`UNVERIFIED` at the database level; no AT28C-family part carrying this protocol has ever been in
operator inventory; and the causal claim "the lock inhibited a write" is reachable only from a
community `dev test` report (`gh#20`) that, by design, does not gate this milestone's close. Green
CI is what makes every later phase's own "green suite" claim checkable at all — it is not, and was
never claimed to be, a hardware-behavioural proof.

---

*Phase: 132-retire-dev-sdp-discharge-the-mypy-debt — Plan 09, Task 3*
*Recorded: 2026-08-03, from the real run dispatched by the operator per this plan's task 2 handoff.*
</content>
