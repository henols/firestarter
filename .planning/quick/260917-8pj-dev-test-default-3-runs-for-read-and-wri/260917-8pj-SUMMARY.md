---
quick_id: 260917-8pj
status: complete
date: 2026-09-17
commits_land_in: firestarter_app
---

# Quick task 260917-8pj

`dev test` now runs three passes by default for the read step and for the
write/verify/erase cycle block, and a new `--submit` flag files the report with
no prompt. The single-pass-read machinery built earlier the same day was
reverted first, because the operator changed the decision it rested on.

## What landed

All commits are in the `firestarter_app` submodule, on
`v1.39-protocol-0x05-write-correctness`, over base `ff5dd1d` (== `origin/beta`,
3.0.0b45).

| Commit | Task |
|---|---|
| `11419a0`, `bb56e30`, `f5e073b` | Three forward reverts of the single-pass-read work |
| `b596249` | `_DEFAULT_RUNS = 3` at the CLI call site |
| `d9a0036` | `submit_report` gains an `auto_submit` consent path |
| `1847920` | The `--submit` flag, wired to that consent |
| `6047d2e` | Widened the SDP-leg option-surface pin |

Net of the reverts, `chip_test.py` is untouched and
`tests/fixtures/report_shapes.py` is byte-identical to `ff5dd1d`.

## Decisions carried in from the operator

- `--submit` may file ANY run, including a `--fast` one. No accuracy gate.
- When the duplicate check cannot run, file anyway and say the check did not
  run. Fail open, not closed.
- A bare run is unchanged: it asks on a TTY and prints the URL off one. The
  flag is the only thing that changes behaviour, and a test pins that on both
  TTY paths.

`--submit` reverses v1.21 SUB-01's ban on silent off-TTY submission. That
reversal is the operator's, made with the outward-facing consequence stated:
the flag creates public issues with no human in the loop.

## Why the reverts

The earlier work gave the read step its own count defaulting to one pass, added
`--compare-reads`, and took `OP_READ` out of `_REPEAT_POLICY_OPS`. With the
default moving to three passes there is nothing left for `--compare-reads` to
opt into, and read is a normal repeat-policy op again, so all of it was undone
rather than left as unused generality.

Reverting also restored the frozen hash `m27c512-full-runs-1` to
`e4838f7bb1d3`. That fixture had re-keyed under the earlier change because its
write and verify never dispatch, leaving the read count as its only
repeat-policy signal.

## The correctness property

`dedup_fingerprint` does not hash `run_count`. It hashes the chip, the
protocol, each step's `op=verdict:classification`, then `repeat_policy_tag` and
`coverage_tag` only when non-empty, and the repeat-policy tag fires only at
`run_count == 1`. So moving the default from two to three leaves every
already-filed fingerprint byte-identical, and the four fixtures transcribed
from real filed issues still reproduce their filed hashes.

## Deviations

- **The executor was killed mid-task by an API error**, after committing tasks
  1 to 3 and leaving task 4 complete but uncommitted in the working tree. The
  orchestrator verified that work, committed it as `1847920`, then found and
  repaired the one test the executor never reached.
- **`test_derive_plan_allow_adds_no_cli_option` failed** on the first full run
  and was not caught by the targeted run. It pins `dev_test`'s option set
  exactly. The pin guards the claim that the SDP leg adds no CLI option, not
  the incidental fact that the command had one option, so it was widened to
  `["fast", "submit"]` and the widening recorded in its docstring, which
  already carried the record of a previous widening for `--fast`.
- **Both Python virtualenvs were destroyed mid-task** by something outside this
  work: their interpreter symlinks pointed into uv's Python store, which had
  been removed. `.venv311` was rebuilt with `uv venv --python 3.11`, with
  `UV_CACHE_DIR` redirected because `~/.cache` is not writable here.
- **The planning-citation gate the plan named no longer exists.** Both
  sub-repos' copies and three CI steps were removed by operator decision the
  same day. The comment rule was checked with the pre-commit grep that
  `CLAUDE.md` now carries instead.

## Verification

- Full suite on Python 3.11.16: `2024 passed in 181.66s`, zero failures.
- `ruff check`: all checks passed. `ruff format --check`: 139 files already
  formatted.
- The staged diff adds no comment line and no task id, phase number or
  `.planning/` path to any source file.
