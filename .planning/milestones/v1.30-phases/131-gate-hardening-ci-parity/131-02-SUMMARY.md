---
phase: 131-gate-hardening-ci-parity
plan: 02
subsystem: testing
tags: [mypy, ci, gate-hardening, pytest, red-preserving-proof, sdp_capability]

requires:
  - phase: 131-01
    provides: "Fail-closed classify_mypy_result()/run_mypy()/mypy_argv()/enforce_watermark() split, the returncode-before-regex guard order, the completion-clause requirement, MIN_CHECKED_SOURCE_FILES=120"
provides:
  - "tools/check_mypy_watermark.py's first-ever paired pytest suite: tests/test_check_mypy_watermark.py, 8 tests (6 legs + 2 controls)"
  - "GATE-06's positive, fail-provable evidence for GATE-01/02/03/04's mechanism (owned by 131-01)"
  - "D-03 RED-preserving proof: the truncated-run leg was seen to fail with the guard reordering reverted, failure reason read and recorded verbatim, guard restored byte-identically"
  - "F-06: tests/test_check_mypy_watermark.py registered in check_no_exists_proxy.py's _DEFAULT_TARGETS, same commit as the module's creation"
  - "F-05 correction: D-02 layer 3's original count-asserting end-to-end wording replaced with a two-shape mutually-exclusive assertion, recorded as an amendment"
affects: [132]

tech-stack:
  added: []
  patterns:
    - "In-process pure-classifier legs (pytest.raises(SystemExit) + .value.code) — first in-repo precedent for calling a tools/ checker function directly rather than via subprocess _run_checker"
    - "subprocess.run monkeypatched inside the checker's own module namespace for an argv-equality proof — a call-argument probe, not an environment simulation, adds no production seam"

key-files:
  created:
    - firestarter_app/tests/test_check_mypy_watermark.py
  modified:
    - firestarter_app/tools/check_no_exists_proxy.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "F-05: D-02 layer 3's original 'assert exit in {0,1,2} and stdout carries mypy errors: N (watermark: M)' is unsatisfiable in this devcontainer (the hardened gate exits 2 before any count prints); replaced with a two-shape mutually-exclusive assertion, strictly stronger since it also forbids the fail-open shape."
  - "F-06: tests/test_check_mypy_watermark.py added to check_no_exists_proxy.py's _DEFAULT_TARGETS in the same commit that created it, alphabetical position."
  - "D-03: the RED-preserving proof used the exact pre-131-01 loose regex (`Found (\\d+) errors?`, unanchored, no completion-clause requirement) as the reverted classify path, because reordering the returncode guard alone — while keeping the anchored completion-clause regex intact — is structurally incapable of producing a RED (the unconditional 'no completion clause' guard would still catch the truncated shape regardless of guard position). This was verified empirically, not assumed."

requirements-completed: [GATE-01, GATE-02, GATE-03, GATE-04, GATE-06]

coverage:
  - id: D1
    description: "check_mypy_watermark.py has its first-ever paired pytest suite: 4 fail-closed legs (each asserting code AND message), 1 whole-list argv-equality proof, 1 two-shape end-to-end proof, 2 controls"
    requirement: "GATE-06"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_check_mypy_watermark.py -- 8 tests, all pass (python3 -m pytest tests/test_check_mypy_watermark.py -q)"
        status: pass
    human_judgment: false
  - id: D2
    description: "GATE-01/02 fail-provable proof: a truncated mypy run and a config-rejected-but-well-formed run both exit 2, with the message naming the specific cause"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "tests/test_check_mypy_watermark.py::test_truncated_run_exits_2, ::test_config_rejection_exits_2"
        status: pass
    human_judgment: false
  - id: D3
    description: "GATE-02 fail-provable proof: returncode is consulted before the regex, and the completion clause is required"
    requirement: "GATE-02"
    verification:
      - kind: unit
        ref: "tests/test_check_mypy_watermark.py::test_truncated_run_exits_2 (no checked clause -> exit 2 despite a returncode of 2)"
        status: pass
    human_judgment: false
  - id: D4
    description: "GATE-03 fail-provable proof: a plausible-looking count on a run that checked fewer than MIN_CHECKED_SOURCE_FILES files exits 2, naming both the observed count and the floor"
    requirement: "GATE-03"
    verification:
      - kind: unit
        ref: "tests/test_check_mypy_watermark.py::test_below_coverage_floor_exits_2"
        status: pass
    human_judgment: false
  - id: D5
    description: "GATE-04 fail-provable proof: mypy is invoked as [sys.executable, -m, mypy, firestarter/, tests/] by whole-list equality, never a bare mypy off PATH"
    requirement: "GATE-04"
    verification:
      - kind: unit
        ref: "tests/test_check_mypy_watermark.py::test_mypy_argv_is_sys_executable_dash_m"
        status: pass
    human_judgment: false
  - id: D6
    description: "D-03 RED-preserving proof: with the returncode-before-regex ordering reverted (using the exact pre-131-01 loose regex), test_truncated_run_exits_2 is SEEN to fail with 'DID NOT RAISE SystemExit' -- not an import/name/collection/wrong-code error -- and the file is restored byte-identically afterward"
    verification:
      - kind: unit
        ref: "manual session transcript: pytest -v showed 'Failed: DID NOT RAISE SystemExit' for test_truncated_run_exits_2 and test_below_coverage_floor_exits_2; git diff HEAD -- tools/check_mypy_watermark.py empty after restore"
        status: pass
    human_judgment: false
  - id: D7
    description: "New module registered in check_no_exists_proxy.py's explicit _DEFAULT_TARGETS list in the same commit that created it (F-06)"
    verification:
      - kind: unit
        ref: "python3 tools/check_no_exists_proxy.py -- PASS: names tests/test_check_mypy_watermark.py; git diff --name-only shows both files in one commit (f76cf94)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-08-03
status: complete
---

# Phase 131 Plan 02: First Paired Pytest for the mypy Watermark Gate + RED-Preserving Proof Summary

**`tests/test_check_mypy_watermark.py` (8 tests: 6 legs + 2 controls) gives `check_mypy_watermark.py` its first-ever paired pytest, and the D-03 revert-and-reobserve proved the truncated-run leg was genuinely RED (`DID NOT RAISE SystemExit`) before the fix was restored byte-identically — no mypy errors fixed, no watermark set.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 2 (Task 1: author the paired pytest suite; Task 2: RED-preserving proof, no commit — net diff on the target file is zero by construction)
- **Files modified:** 2 in `firestarter_app` (`tests/test_check_mypy_watermark.py` created, `tools/check_no_exists_proxy.py` extended) + 1 in the meta repo (`REQUIREMENTS.md`)

## Accomplishments

- Authored `tests/test_check_mypy_watermark.py` — the checker's first-ever paired pytest, 8 tests:
  4 in-process fail-closed legs against the pure `classify_mypy_result`/`enforce_watermark`
  functions (each asserting both the exit code AND a message substring naming the specific cause,
  never exit-code-only), 1 whole-list argv-equality proof (GATE-04's positive evidence, via
  `subprocess.run` monkeypatched inside the checker's own module namespace — a call-argument probe,
  not an environment simulation, adding no production seam per D-01), 1 two-shape end-to-end
  subprocess proof (correction F-05), and 2 controls proving the classifier does not raise
  unconditionally.
- Registered the new module in `tools/check_no_exists_proxy.py`'s `_DEFAULT_TARGETS`, alphabetical
  position, **in the same commit** that created the module (correction F-06) — verified
  `python3 tools/check_no_exists_proxy.py` exits 0 and names the new file in its PASS line.
- **D-03 RED-preserving proof, executed live this session** (see "RED-Preserving Proof" below for
  the verbatim transcript): temporarily reverted `classify_mypy_result`'s guard ordering to the
  exact pre-131-01 shape (loose, unanchored `Found (\d+) errors?` regex; returncode consulted only
  if nothing matched), ran the new suite, **observed** `test_truncated_run_exits_2` fail with
  `Failed: DID NOT RAISE SystemExit`, confirmed the argv and end-to-end legs were unaffected, then
  restored the file via `git checkout --` — `git diff HEAD -- tools/check_mypy_watermark.py` is
  empty.
- Ticked `GATE-01`, `GATE-02`, `GATE-03`, `GATE-04`, `GATE-06` in `REQUIREMENTS.md`, each with an
  evidence clause naming the specific test function(s) and commit hashes. This plan is the last in
  the GATE-01..04 span (131-01 built the mechanism; this plan supplies the fail-provable proof).
  `GATE-05` (ticked by 131-01), `GATE-07/08/09/10` (owned by other plans) were **not** touched.
- Full `firestarter_app` suite: **1311 collected** (1303 + 8 new), all passing; `ruff check` /
  `ruff format --check` clean on `firestarter/ tests/`; `tests/test_skip_census.py` unmodified and
  passing (no new skip reason added).

## Task Commits

1. **Task 1: Author the gate's first paired pytest suite (GATE-06, six legs)** — `firestarter_app`
   commit `f76cf94` (`test(131-02): first paired pytest for check_mypy_watermark.py (GATE-06)`), on
   branch `gsd/v1.30-sdp-surface-retirement`. Two files: `tests/test_check_mypy_watermark.py`
   (created) and `tools/check_no_exists_proxy.py` (extended, F-06).
2. **Task 2: RED-preserving proof — revert the reordering, read the failure, re-apply (D-03)** —
   **no commit.** The task's own acceptance criteria require `tools/check_mypy_watermark.py`'s net
   diff to be zero at the end of the task, by construction (`git checkout --` restored it
   byte-identically). The evidence is this SUMMARY's verbatim transcript, not a commit.

**Plan metadata:** captured in this SUMMARY's own commit (final metadata commit, meta repo) —
includes the five GATE ticks in `.planning/REQUIREMENTS.md`.

## Files Created/Modified

- `firestarter_app/tests/test_check_mypy_watermark.py` — created. 8 tests, numbered `Coverage:`
  docstring, canned mypy output as module-level string constants (not `tests/fixtures/`, since it
  is text a pure function is called against in-process, not source a subprocess reads from disk).
- `firestarter_app/tools/check_no_exists_proxy.py` — one-line addition to `_DEFAULT_TARGETS`
  (F-06).
- `.planning/REQUIREMENTS.md` — `GATE-01/02/03/04/06` ticked with evidence clauses; Traceability
  table rows updated Pending → Complete.

## Decisions Made

- **F-05 (correction to D-02 layer 3):** the original wording — "assert exit in {0,1,2} and stdout
  carries the `mypy errors: N (watermark: M)` line" — is unsatisfiable in this devcontainer: the
  numpy PEP-695 stub truncates every real run here, mypy exits 2, and the hardened
  `classify_mypy_result` exits 2 **before** any count is printed (printing a count on an exit-2 run
  would be exactly the fail-open shape this phase removes). Rewrote the leg as a two-shape
  mutually-exclusive assertion: either the complete shape (`mypy errors: N (watermark: M)`) or the
  incomplete shape (an `ERROR:` diagnostic, no count line) — never both, and an exit-2 run never
  carries the count line. Strictly stronger than the original, since it additionally forbids the
  fail-open shape. Both invocations (real app-root cwd and a foreign `tmp_path` cwd) are asserted to
  land in the **same** shape, proving `REPO_ROOT`'s `Path(__file__).resolve()` anchoring survives a
  foreign working directory.
- **F-06 (planner-added, in scope):** the new test module rides the same commit as its
  `_DEFAULT_TARGETS` registration, since `check_no_exists_proxy.py` hard-fails on a listed-but-
  missing target — verified structurally by running the checker after staging both files together.
- **D-01 followed exactly:** no `os.environ` seam added to the production checker
  (`grep -c 'os.environ' tools/check_mypy_watermark.py` == 0). Leg 5's `subprocess.run` monkeypatch
  targets the checker's own module namespace (`monkeypatch.setattr(mod.subprocess, "run", fake)`),
  never a global patch, and asserts the captured argv by whole-list equality (not membership).
- **D-03's revert mechanism, chosen after empirical verification, not assumption.** Reordering
  *only* the returncode-not-in-(0,1) guard relative to the (still-anchored) completion-clause parse
  cannot produce a RED for the canned `TRUNCATED_OUTPUT`, because the hardened code's separate
  "no completion clause matched → exit 2" guard is unconditional on returncode and fires regardless
  of guard position. Verified this by implementing exactly that reordering first and observing the
  suite still passed 8/8. The revert that actually reproduces the historical bug — and satisfies the
  task's own acceptance criterion of `test_truncated_run_exits_2` failing with `DID NOT RAISE
  SystemExit` — is the literal pre-131-01 shape read from `git show 16a313a:tools/check_mypy_watermark.py`:
  an unanchored `re.search(r"Found (\d+) errors?", output)` that matches on a match with no
  returncode check at all, consulting `returncode` only in the `if m` branch's `else`.

## RED-Preserving Proof (D-03), Verbatim

**Step 1 — revert (not committed).** In `classify_mypy_result`, replaced the returncode guard,
the config-independent completion-clause parse, and the floor guard's reachability with the exact
pre-131-01 shape (config guard kept first, unchanged, since it postdates the bug and does not
interfere with reproducing it):

```python
    config_match = _CONFIG_REJECTION_RE.search(output)
    if config_match:
        ...
        sys.exit(2)

    m = re.search(r"Found (\d+) errors?", output)
    if m:
        return int(m.group(1))
    if returncode == 0 or "Success: no issues found" in output:
        return 0
    print(f"ERROR: mypy exited {returncode}, ...")
    sys.exit(2)
```

**Step 2 — observed RED, reason read.** `python3 -m pytest tests/test_check_mypy_watermark.py -v`:

```
tests/test_check_mypy_watermark.py F..F....                              [100%]

=================================== FAILURES ===================================
__________________________ test_truncated_run_exits_2 __________________________
    with pytest.raises(SystemExit) as exc:
>       ...
E       Failed: DID NOT RAISE SystemExit

______________________ test_below_coverage_floor_exits_2 _______________________
    with pytest.raises(SystemExit) as exc:
>       ...
E       Failed: DID NOT RAISE SystemExit

========================= 2 failed, 6 passed in 0.44s ==========================
```

Confirmed:
- `test_truncated_run_exits_2` **fails**, and the failure is `Failed: DID NOT RAISE SystemExit` —
  not an import error, not a name error, not a wrong-code assertion, not a collection error. The
  loose regex `r"Found (\d+) errors?"` matched `TRUNCATED_OUTPUT`'s `"Found 1 error in 1 file
  (errors prevented further checking)"` line (which lacks the `(checked N source files)` clause the
  anchored `_FOUND_RE` requires), returned `1` directly, and `returncode` (2) was never consulted —
  exactly the bug's shape ("the count is taken from whatever regex matches, and the returncode is
  consulted only if nothing matched").
- **The coverage-floor leg's behaviour, recorded as observed:** `test_below_coverage_floor_exits_2`
  **also** failed the same way (`DID NOT RAISE SystemExit`), because with the reordering reverted,
  the truncated file-set shape (`UNDER_FLOOR_OUTPUT`, "Found 3 errors in 2 files (checked 4 source
  files)") also matches the loose regex and returns immediately, never reaching the floor guard at
  all. This is exactly what the plan anticipated ("the truncated shape no longer reaches the floor
  guard") and instructed to record, not treat as a problem.
- **The argv leg and the end-to-end leg were confirmed UNAFFECTED**, run in isolation:
  `python3 -m pytest tests/test_check_mypy_watermark.py -v -k "argv or end_to_end"` →
  `2 passed, 6 deselected`. `test_mypy_argv_is_sys_executable_dash_m` does not call
  `classify_mypy_result` at all (only `run_mypy()`), so it is structurally independent. The
  end-to-end leg's assertions are shape-consistency checks (mutual exclusivity + code/count
  correlation), not a hardcoded expectation of *which* shape occurs, so it remained passing even
  though the real subprocess's observed exit code changed underneath it (see next point) — this is
  the correct, intentional robustness the leg was designed for, not a blind spot.
- **The real checker's own live behaviour flipped to the exact pre-131-01 fail-open output**,
  confirming the revert reached production code, not just the test:
  ```
  $ python3 tools/check_mypy_watermark.py; echo "EXIT: $?"
  mypy errors: 1 (watermark: 35)
  INFO: 1 errors -- 34 below watermark (35). ...
  EXIT: 0
  ```
  (Compare 131-01's own measured pre-hardening output: `mypy errors: 1 (watermark: 35)` / `INFO: 1
  errors — 34 below watermark. Lower watermark in pyproject.toml.` / exit 0 — the same shape.)

**Step 3 — re-apply and re-verify.** `git checkout -- tools/check_mypy_watermark.py`, restoring the
file byte-identically (not a hand-retyped approximation). Re-ran:
- `python3 -m pytest tests/test_check_mypy_watermark.py -q` → `8 passed` (all legs, including
  `test_truncated_run_exits_2` and `test_below_coverage_floor_exits_2`, back to passing).
- `git diff HEAD -- tools/check_mypy_watermark.py` → empty.
- `git status --porcelain tools/check_mypy_watermark.py` → empty.
- `python3 tools/check_mypy_watermark.py; echo $?` → the same hardened message
  (`ERROR: mypy exited 2, which is neither the clean-run (0) nor errors-found (1) exit code. ...`)
  and **exit 2** — matching 131-01's measured post-hardening behaviour.

No commit in this plan's history contains the reverted state — the revert was made, observed, and
reverted entirely within the working tree before Task 1's own commit (`f76cf94`) was created, and
Task 1's commit already carried the hardened (never-reverted) file.

## Deviations from Plan

None — plan executed exactly as written, including correction F-05 (explicitly directed by the
plan itself) and F-06 (also explicitly directed). One clarification, not a deviation: the plan's
`<action>` text for Task 2 says "move the returncode guard from first position to after the
summary-line parse," which — if implemented as a pure positional swap while keeping the anchored
completion-clause regex — cannot reproduce a RED (verified empirically: implementing exactly that
swap first still left all 8 tests passing, since the unconditional "no completion clause matched"
guard catches the truncated shape regardless of the returncode guard's position). The instruction's
own stated goal — "reproducing the original defect: the count is taken from whatever regex matches,
and the returncode is consulted only if nothing matched" — is only achievable using the **original,
unanchored** regex (read directly from `git show 16a313a:tools/check_mypy_watermark.py`), which is
what was implemented for the revert. This satisfies the task's literal acceptance criteria (the
`DID NOT RAISE SystemExit` failure, the floor leg's behaviour "recorded as observed, whichever way
it lands," and the argv/end-to-end legs unaffected) more precisely than a pure reordering would
have, and is recorded here per D-03's own instruction to read the reason rather than assume it.

## Issues Encountered

One self-caught authoring mistake in Task 1, fixed before the commit: the first draft of
`test_over_watermark_exits_1` read `captured.out`'s first line immediately after calling
`classify_mypy_result`, but that function itself prints a `checked N source files` line before
returning — so the "first printed line" the test asserted against was that coverage line, not
`enforce_watermark`'s `mypy errors: 200 (watermark: 35)` line. Fixed by discarding
`classify_mypy_result`'s own stdout via an interstitial `capsys.readouterr()` call before invoking
`enforce_watermark`, then asserting on the freshly-captured output. Re-verified the exact expected
first line.

## Known Stubs

None.

## Threat Flags

None — this plan adds a test module and one registration-list entry; no new network endpoint, auth
path, file-access pattern, or schema change at a trust boundary was introduced. The threat model's
own T-131-08..14 rows are the ones this plan directly discharges (see the plan's `<threat_model>`).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **GATE-01, GATE-02, GATE-03, GATE-04, GATE-06 are all ticked Complete in `REQUIREMENTS.md`**, each
  with an evidence clause naming the proving test function(s). This closes the GATE-01..04 span that
  131-01 opened.
- **This plan fixed no mypy errors, set no watermark, and left `firestarter_app`'s primary `ci`
  job RED by design.** The real, unhardened checker still reports 1 error locally (a devcontainer-
  only truncation artifact) and 69 inherited errors are still present against the tree; none of
  that was touched. Any sentence implying CI is green after this plan, or reporting an error count
  as a Phase 131 achievement, would be the v1.22 C-5 overclaim class — none exists here.
- `firestarter` (firmware) remains completely untouched — `git -C /workspaces/firestarter status
  --short` is empty throughout this plan.
- No push, tag, merge, or `gh workflow run` was performed by this plan.
- Remaining phase 131 plans (`131-03` GATE-08, `131-04` GATE-10, `131-05` GATE-07 dispatch,
  `131-06` GATE-09, `131-07` close) are unaffected by this plan's scope and can proceed
  independently against the same `gsd/v1.30-sdp-surface-retirement` branch tip (`f76cf94`).

---
*Phase: 131-gate-hardening-ci-parity*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_check_mypy_watermark.py`
- FOUND: `.planning/phases/131-gate-hardening-ci-parity/131-02-SUMMARY.md`
- FOUND commit `f76cf94` (firestarter_app: paired pytest + F-06 registration) on branch
  `gsd/v1.30-sdp-surface-retirement`
- FOUND: `git -C firestarter status --short` empty (firmware untouched)
