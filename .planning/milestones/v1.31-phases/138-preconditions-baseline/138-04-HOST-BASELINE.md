# 138-04-HOST-BASELINE: PREP-03 host-suite half — firestarter_app under CI parity

**Owner requirement:** PREP-03, host half only (the firmware half — golden trace, flash/RAM, native
suites — is Plans 03/05/06's scope, not this plan's). **Status:** measured, 0 requirement ticked by
this plan (`may_tick_requirements: []`).

**Measured:** 2026-08-08, this session, in `/workspaces/firestarter_app`, live and read-only against
the app's own git state. Nothing below is copied from `138-RESEARCH.md` — every command was re-run
fresh in this session, and any divergence from research's recorded figures is stated explicitly,
with both values kept on record, and is **not** reconciled.

---

## 1. Branch switch — provenance

| Field | Value | Command that produced it |
|---|---|---|
| Pre-switch branch | `fix/dev-test-blank-check-after-erase` | `git symbolic-ref --short HEAD` (before switch) |
| Pre-switch HEAD SHA | `7fe8dea9143a6ac4da3d656d3e4d5d538e14a175` | `git rev-parse HEAD` (before switch) |
| Pre-switch tracked-file modifications | 0 (8 untracked files present, expected and carried over) | `git status --porcelain \| grep -v '^??' \| wc -l` → `0` |
| Post-switch branch | `gsd/v1.31-27c-programming-algorithm-fidelity` | `git symbolic-ref --short HEAD` (after switch) |
| Post-switch HEAD SHA | `4d18b645ab18a2d2465f0f623062e9249eb24132` | `git rev-parse HEAD` (after switch) |
| Base SHA recorded in `138-BRANCH-BASES.md` §4 (Plan 01) | `4d18b645ab18a2d2465f0f623062e9249eb24132` | quoted from `138-BRANCH-BASES.md` §4, Section 4 table, `firestarter_app` row |
| HEAD == recorded base? | **Yes — exact match**, both the full 40-char SHA and the 7-char short form | `git rev-parse HEAD` compared byte-for-byte against the quoted value above |

The switch used `git checkout gsd/v1.31-27c-programming-algorithm-fidelity` (branch already existed,
created — but not checked out — by Plan 01). No branch was created by this plan; no branch was pushed;
no commit was made in `firestarter_app` by this task.

## 2. Interpreter and imported package — provenance

| Field | Value | Command that produced it |
|---|---|---|
| CI-parity interpreter path | `.venv/ci-replica/bin/python` (symlink → `python3.11`) | `ls -la .venv/ci-replica/bin/python` |
| CI-parity interpreter version | **`Python 3.11.15`** | `.venv/ci-replica/bin/python --version` |
| Ambient interpreter version (recorded for contrast, **NOT** used for any measurement below) | `Python 3.12.13` | `python3 --version` |
| Imported package file | `/workspaces/firestarter_app/firestarter/__init__.py` | `.venv/ci-replica/bin/python -c "import firestarter; print(firestarter.__file__); print(firestarter.__version__)"` |
| Imported package version | `3.0.0b20` | same command as above |

The devcontainer's ambient Python (`3.12.13`) is not used for any figure in this document — every
appearance of the string `3.12` in this file (here, the table row above, and §8's restatement of the
interpreter constraint) is inside a sentence explaining why it was **not** substituted for the
CI-parity interpreter, never a figure produced by running it. Every measurement below runs `.venv/ci-replica/bin/python`
explicitly, from inside `/workspaces/firestarter_app` (never a sibling directory — the package is
installed editable, and two tests resolve a path ending in the literal directory name
`firestarter_app`; see §4).

## 3. Full-suite measurement — provenance

**Stated condition of this measurement:** no serial devices are attached to this machine
(`/dev/ttyACM*` and `/dev/ttyUSB*` are both absent, confirmed immediately before this run). This
matters because `test_no_programmer_found_*`-style tests go spuriously RED when a live board is
present (a real `/dev/ttyACM*` device beats the `comports=[]` monkeypatch) — that failure mode does
not apply to this run.

| Field | Value | Command that produced it |
|---|---|---|
| Command (exact, run from `/workspaces/firestarter_app`) | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` | — |
| Timeout budget used | 600000 ms (>= the plan's required 540000 ms floor) | Bash tool invocation parameter |
| Wall-clock start | `2026-08-08T23:14:06Z` | `date -u` immediately before the run |
| Wall-clock end | `2026-08-08T23:17:07Z` | `date -u` immediately after the run |
| Exit code | `0` | shell `$?` |
| Collected | **1539** (= passed + skipped + failed, since pytest's `-q` summary omits a zero-count category) | tail of the same run |
| Passed | **1539** | tail of the same run: `1539 passed, 1 warning in 180.89s (0:03:00)` |
| Skipped | **0** | same tail line — no `skipped` clause present, and `grep -ic skip` on the full captured output returns `0` |
| Failed | **0** | same tail line — no `failed` clause present |
| Warnings | 1 (`test_click_group_gate_hook.py` — `Click` `MultiCommand` deprecation, pre-existing, unrelated to this measurement) | same run |
| Snapshot tests | `30 snapshots passed.` | same run's `snapshot report summary` block |
| Duration (pytest-reported) | `180.89s (0:03:00)` | same tail line |
| Duration (wall-clock, this session) | `181s` (`$SECONDS`) | shell timer wrapping the same invocation |

`-o addopts=""` is present in the command above and no `-qq` appears anywhere — `pyproject.toml` sets
`addopts = "-ra -q"`, and a second `-q` on the command line would reach `-qq`, which suppresses the
count line that is the entire measurement (Pitfall 9). The verbatim captured tail is reproduced in
full in §5 below, unedited.

## 4. Directory-name-dependent tests — in-place proof

| Field | Value | Command that produced it |
|---|---|---|
| Node id 1 | `tests/test_gen_validation_header.py::test_validate_spec_called_before_emission` | — |
| Node id 2 | `tests/test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing` | — |
| Command | `.venv/ci-replica/bin/python -m pytest tests/test_gen_validation_header.py::test_validate_spec_called_before_emission tests/test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing -o addopts="" -q` | — |
| Result | **`2 passed in 0.09s`** | same command, run from `/workspaces/firestarter_app` |

Both tests resolve a path ending in the literal directory name `firestarter_app` (per
`138-RESEARCH.md`'s Pitfall 8 / Runtime State Inventory) and were measured here **in place**, in
`/workspaces/firestarter_app` itself — not a sibling or renamed checkout. Their passing is the positive
evidence that this whole measurement was taken in the correct location.

## 5. Post-measurement worktree state — provenance

| Field | Value | Command that produced it |
|---|---|---|
| Tracked-file changes introduced by this task | 0 | `git status --porcelain \| grep -v '^??' \| wc -l` → `0` (re-run after both pytest invocations) |
| Untracked files (unchanged set of 8, all pre-existing) | `.coverage`, `.planning/config.json`, `SECURITY.md`, `datasheets/M27C1001.pdf`, `datasheets/M27C512.pdf`, `datasheets/W27C512.pdf`, `datasheets/W27E257.pdf`, `write_test_port.sh` | `git status --porcelain` |
| HEAD after both pytest runs | `4d18b64 Apply automatic changes` — unchanged | `git log --oneline -1` |
| Branch after both pytest runs | `gsd/v1.31-27c-programming-algorithm-fidelity` — left checked out, as later phases expect | `git symbolic-ref --short HEAD` |

**No commit was made inside `firestarter_app` by this task.** The app worktree is left on the v1.31
branch, as later Wave 3 plans (Phase 143) expect it.

---

## 6. Verbatim output — full-suite run

First line is the literal command; everything after is the unedited tail of the same run captured in
§3, copied byte-for-byte (progress dots collapsed to the final `[100%]` line; nothing reflowed,
nothing summarised):

```
$ .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q
...........................                                              [100%]
=============================== warnings summary ===============================
tests/test_click_group_gate_hook.py::test_multicommand_is_deprecated_alias_not_in_dir_but_still_reachable[MultiCommand]
  /workspaces/firestarter_app/tests/test_click_group_gate_hook.py:161: DeprecationWarning: 'MultiCommand' is deprecated and will be removed in Click 9.0. Use 'Group' instead.
    assert getattr(click, attr_name) is not None

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
1539 passed, 1 warning in 180.89s (0:03:00)
```

## 7. Divergence check against `138-RESEARCH.md`

**This run's figure** (§3 above): commit `4d18b645ab18a2d2465f0f623062e9249eb24132`, branch
`gsd/v1.31-27c-programming-algorithm-fidelity`, measured **in place** in
`/workspaces/firestarter_app` via `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` —
**1539 collected, 1539 passed, 0 skipped, 0 failed, 180.89s**.

**`138-RESEARCH.md`'s figure for the identical commit** (§"Host suite (`firestarter_app`)", row
"live beta `4d18b64`"): the **same commit** `4d18b64`, the **same interpreter**
(`.venv/ci-replica` py 3.11.15) — **1539 collected, 1493 passed, 46 skipped, 0 failed, 179s**.

**These are not two different trees — they are the identical commit, and the collected totals agree
exactly (1539 = 1539). The passed/skipped split disagrees sharply (1539/0 here vs 1493/46 in
research), and that disagreement is stated here with both values, unreconciled, per the plan's own
instruction not to adjust either number to make them meet.**

**Context on the divergence, offered as an observation and explicitly not a reconciliation:**
`138-RESEARCH.md`'s own text for that row states plainly that its full-suite pass/skip breakdown for
`4d18b64` was "measured in a directory named `app_beta_live`" — not `/workspaces/firestarter_app` —
and that research's own two directory-name-dependent tests **FAIL** in that location. This run, by
contrast, was measured in place, in the real `/workspaces/firestarter_app` checkout, with the real
sibling firmware repo reachable at `/workspaces/firestarter` one level up. `firestarter_app/tests/fw_presence.py`
gates **72** cross-repo-test references (`grep -rn "requires_fw" tests/*.py | grep -v fw_presence.py | wc -l`,
run this session) on `requires_fw = pytest.mark.skipif(not FW_REPO_PRESENT, reason=...)`, where
`FW_REPO_PRESENT` is decided by whether `<checkout>/../firestarter/.git` exists
relative to the checkout doing the measuring. A checkout named `app_beta_live` sitting somewhere other
than as a direct sibling of the real `/workspaces/firestarter` would fail that marker check and skip
every `requires_fw`-gated test — a batch consistent in shape with the missing 46. **This plan did not
independently re-verify that mechanism inside `app_beta_live` itself** (that directory's checkout is
not this plan's to re-inspect), so it is recorded here as a plausible, unconfirmed explanation for
*why* the two figures diverge, not as a correction to either one. Both numbers stand, attributed to
their own command and location, exactly as measured.

## 8. The three constraints, restated as measured facts

- **Interpreter.** This entire measurement ran under `.venv/ci-replica/bin/python`, verified to print
  `Python 3.11.15` (§2). The devcontainer's ambient interpreter, `python3`, is `Python 3.12.13` and
  **masks** `firestarter_app`'s py3.9/3.11 CI matrix — it was recorded once, in §2, purely for
  contrast, and was not used to produce any figure in this document.
- **The count line.** `firestarter_app/pyproject.toml`'s `[tool.pytest.ini_options]` sets
  `addopts = "-ra -q"`. Every pytest invocation in this document passes `-o addopts=""` on the command
  line specifically to prevent the configured `-q` from combining with a second `-q` into `-qq`, which
  would suppress the `N passed, ... in Ts` count line that is the entire measurement (Pitfall 9). The
  count line survived intact in every run recorded here (§3, §4, §6).
- **The directory name.** Two tests —
  `tests/test_gen_validation_header.py::test_validate_spec_called_before_emission` and
  `tests/test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing` — resolve a
  path ending in the literal directory name `firestarter_app` and fail in any checkout named
  otherwise (confirmed in `138-RESEARCH.md`, and independently corroborated by §7's divergence, where
  a differently-named checkout also produced a different skip count). Both were observed **passing**
  in this document's own measurement, run in place, by node id (§4).

## 9. What this number is — and is not

**This number is** the pre-change input Phase 144's TEST-03 compares against, for the host suite
half of PREP-03, measured against the named commit `4d18b645ab18a2d2465f0f623062e9249eb24132` on
branch `gsd/v1.31-27c-programming-algorithm-fidelity`, under the CI-parity interpreter, in place, in
`/workspaces/firestarter_app`.

**It is not:**
- **Not a claim that CI is green.** No CI workflow was dispatched by this plan, and no run id is
  recorded anywhere in this document. The operator-gated CI evidence for `firestarter_app` **is plan
  07's scope**, not this one's.
- **Not a claim about coverage.** `pytest-cov`/snapshot plugin output was captured only incidentally
  (the `.coverage` file already existed untracked before this task ran, per §5); no coverage
  percentage is asserted or claimed here.
- **Not a measurement of any tree other than the one named.** Every figure in this document is
  attributed to commit `4d18b645ab18a2d2465f0f623062e9249eb24132`; no figure describes the live
  `beta` tip, the `fix/dev-test-blank-check-after-erase` branch, or any other ref.

## 10. Not established by this measurement

- **Nothing about the firmware.** No golden trace, no flash/RAM figure, and no native-suite count is
  established here — that is Plans 03/05/06's scope within this same phase.
- **Nothing about the host's behaviour on Python 3.9**, the lowest version `firestarter_app`'s CI
  matrix supports. `.venv/ci-replica` is `3.11.15`; no 3.9 interpreter was invoked by this plan.
- **Nothing about the app's packaging or publish path.** No `pip install .` (non-editable), no
  `python -m build`, and no PyPI query was run by this plan.
- **No CI run.** Confirming §9: no `gh workflow run` (blocked by the auto-mode classifier in any case)
  and no `gh run view` were executed by this plan — plan 07 owns that evidence.
- **No re-derivation of `138-RESEARCH.md`'s exact 46-skipped test list.** §7's proposed mechanism
  (sibling-repo marker + a differently-named checkout) is offered as context, not proof — this plan did
  not re-open or re-measure inside the `app_beta_live` directory research used.

---

*Phase: 138-preconditions-baseline — Plan 04*
*Recorded: 2026-08-08, measured live in `/workspaces/firestarter_app` under `.venv/ci-replica`
(Python 3.11.15), commit `4d18b645ab18a2d2465f0f623062e9249eb24132`.*
