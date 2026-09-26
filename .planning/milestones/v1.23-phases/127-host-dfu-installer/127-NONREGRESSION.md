# Phase 127 Non-Regression Sweep — closing plan (127-12)

**Written:** 2026-08-01 (Plan 127-12)
**Host branch (`firestarter_app`):** `v1.23-py32f071-integration` · **HEAD at this sweep:**
`a62ca7647aed22d8c82ecf3aac3db4a81780260f`
**Firmware branch (`firestarter`):** `v1.23-py32f071-integration` · **HEAD:**
`240fb19c50190797ffdc2062d39390e074f8566f` (unmodified by this phase — read-only input)
**Meta branch:** `gsd/v1.23-py32f071-integration`

**No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon, and
nothing in it can.

**Re-execution pledge.** Every row below was executed in **this session** (Plan 127-12's Task 1),
against the trees exactly as they now stand — nothing is copied from any of this phase's eleven
prior plans' (127-01 through 127-11) SUMMARY files. Where a prior SUMMARY made a claim (a gate's
exit code, a collected count, a commit SHA, a mypy error count), this document re-checked it
independently against the live tree or a live, read-only `gh` query and says so below.

---

## 1. The claim, as precise statements

1. **`feature/py32f071-fw-install` @ `4ee64a1` is merged onto `v1.23-py32f071-integration` as a real
   `--no-ff` merge commit (`63ce44e`)**, whose parent SHAs include `4ee64a1` literally. Evidenced by
   `git log -1 --format=%P`, re-run this session. See §Criterion 1.
2. **`--usb-id` is rejected on a simulated stable channel by the exact same shared mechanism
   `--dfu-probe` already uses** (`_reject_py32_only_option()`), and channel gating is proven both
   ways (stable hides `py32f071`/rejects both options; pre-release exposes both), with an explicit
   import-time-by-construction assertion. See §Criterion 1 and §Criterion 5.
3. **A CI leg (`ci-py32`) installs `.[test,py32]` and genuinely exercises `usb.core.find` and
   `ctrl_transfer`**, distinct from the primary `.[test]`-only leg, confirmed green on **two**
   independently re-queried CI runs, the second on the phase's final tree. See §Criterion 2 and the
   CI row.
4. **`PyusbMissingError`'s `# pragma: no cover` is removed from `_require_usb()`'s `except` clause
   and its two statements are covered in-process; `fw --list`/`fw --help`/`firestarter --help` all
   exit 0 under a genuine `sys.meta_path` import blocker with pyusb truly unreachable.** See
   §Criterion 3.
5. **`DFU_UPLOAD` readback verification exists as a `VerifyResult` enum on the flasher** (`VERIFIED`,
   `SKIPPED_NO_UPLOAD`, `SKIPPED_PLAIN_DFU`, `MISMATCH`), fails **soft** with a named reason when a
   mock device reports `bitCanUpload = 0` or the dialect is plain DFU 1.1, and fails **hard** (exit 1,
   naming the first differing offset) on a genuine byte mismatch — never manifesting the device off
   the bus first. The DFU opcode literals are anchored independently of the module under test. See
   §Criterion 4.
6. **The `pyusb` floor is `>=1.3.1,<2`** in `pyproject.toml`'s `[py32]` extra, held by a non-vacuous,
   fail-closed textual gate. See §Criterion 5.
7. **The host flash-envelope guard is tightened to `APP_REGION_END` (`0x0801E000`)**, matching the
   linker script Phase 126 actually shipped, held by a fail-closed cross-repo parity gate — a
   deliberate in-scope addition carrying **no HOST id** (D-13/D-14).

**Explicit non-claims, stated as plainly as the claims above:**

- **No claim that the complete DFU install sequence succeeds from start to finish, that firmware
  executes on PY32F071 silicon, or that any part of the sequence has been validated against a bench or
  real hardware.** No PCB exists. §7 states this at length; it is the ceiling this whole phase
  operates under.
- **HOST-03's evidence is asserted against a mock, and only against a mock.** The mock answers
  exactly as told; nothing here proves a genuine PY32F071 bootloader's `DFU_UPLOAD` behaviour, its
  dialect fork, or its `bitCanUpload` bit actually work this way.
- **A1's residual is not resolved by this document.** UM1504 (the Puya/ST DfuSe application note)
  was never fetched — two independent network attempts (Plan 127-03) failed at the network layer.
  The DfuSe-specific opcode literals remain *consistent with the module*, not *independent of it*.
- **The primary `ci` job's RED conclusion is a pre-existing, milestone-wide mypy-debt finding, not a
  Phase 127 regression** — Phase 127's own net contribution to that debt is independently measured
  at zero (§6, §Informational Findings).

---

## 2. The baseline, as recorded and as re-verified

**Pre-merge baseline** (Plan 127-01, `ccbc401e16e2d2298f7376c3086164700bba0278`, the real sibling
checkout — **not** the scratch-worktree figure research first reported): **1158 collected / 1158
passed / 0 skipped / 0 failed.** Re-measured 2026-08-01 in this session by archiving `ccbc401` into a
scratch directory and confirming the tree is unchanged; the collected count of 1158 matches every
prior plan's own record of this baseline (127-01, 127-02). Research's own scratch-worktree figure —
**1213 passed / 3 skipped** — was measured in a *different* checkout where `.planning/` was
unreachable, tripping the two meta-repo-ledger skip reasons in `tests/test_skip_census.py`'s
`ALLOWED_SKIP_REASONS`. In the real sibling layout, `.planning/` **is** reachable (this is the meta
repo's own worktree), so those two skips never fire and **0 skipped is the correct figure here** —
not a discrepancy to explain away.

**Post-merge count** (Plan 127-01, commit `63ce44e`): **1216 collected**, exactly matching
`127-RESEARCH.md`'s Q1 prediction (1158 + 58 from `tests/test_py32_dfu.py`). **But — and this is the
first correction this document carries forward — the post-merge run was NOT 1216/1216 green.**
`127-RESEARCH.md`'s C-1 measured "zero fixups required" in a scratch worktree; the real merge, landed
for real by Plan 127-01 in the correct sibling layout, left the suite at **1215 passed / 1 failed**
(`tests/test_characterization.py::test_help_fw`), because the merge added `py32f071` to
`_ALL_BOARDS` and the pre-existing `fw --help` snapshot (captured at Phase 120) did not include it.
Plan 127-04 fixed this under operator-approved added scope, replacing the single channel-blind
snapshot with two channel-named ones (`test_help_fw_stable` / `test_help_fw_prerelease`). Reproduction
of the disproven claim, re-confirmed this session:

```
$ cd /workspaces/firestarter_app && python -m pytest tests/test_characterization.py::test_help_fw -q
.                                                                        [100%]
2 snapshots passed.
1 passed in 1.53s
```

This now **passes** (post-127-04 fix) but the command is preserved here because it is the exact
reproduction of C-1's disproof at the moment C-1 was measured false — the test itself is
parametrized across both channels since Plan 127-04, so "1 passed" now covers both snapshot
variants in one node id.

**This phase's final total, re-measured in this session** (HEAD `a62ca7647aed22d8c82ecf3aac3db4a81780260f`,
sibling layout, pyusb absent, no serial device attached):

```
$ cd /workspaces/firestarter_app && python3 -m pytest tests/ --collect-only -q -o addopts=
[... 1293 lines of node ids ...]
1293 tests collected in 0.56s
```

```
$ cd /workspaces/firestarter_app && python3 -m pytest tests/ -q --no-cov -o addopts=
[... dots ...]
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
1293 passed in 164.61s (0:02:44)
```

**1293 collected / 1293 passed / 0 failed / 0 skipped.**

**No assertion in this codebase pins any of the three integers above (1158, 1216, 1293) to an exact
literal.** This is a **deliberate, reasoned exception** to the standing operator preference (recorded
in `123-CONTEXT.md`) for an exit code over a human reading output — Phase 123's own D-10 rejected a
pinned collected-test count for measured flakiness, and `tests/test_skip_census.py::test_no_pinned_skip_count`
mechanically enforces that rejection today. Recording the number without gating on it is therefore
not a lapse in this phase's own discipline; it is the same discipline Phase 123 itself established,
applied consistently. Every later phase that adds a test will legitimately move this integer upward,
and no gate in this repository should — or does — go red because of that.

**Coverage**, measured this session:

```
$ cd /workspaces/firestarter_app && python3 -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70
TOTAL                               4767    864    82%
Required test coverage of 70% reached. Total coverage: 81.88%
```

Total **81.88%** against the 70% floor. `firestarter/py32_dfu.py` — the module HOST-03/HOST-05/HOST-06
built out — is individually at **79%** (`463 stmts, 95 miss`).

**C-8's measurement, re-taken this session on the final tree** — the full suite run under
**pyusb-present** (a throwaway `.[test,py32]` venv, deleted immediately after):

```
$ <venv>/bin/python -m pytest tests/ -q --no-cov
1299 passed in 177.36s (0:02:57)
```

**1299 passed / 0 failed / 0 skipped** — the +6 over the pyusb-absent 1293 is exactly
`tests/test_pyusb_api_surface.py`'s five (now six, after Plan 127-08's fake-vs-real signature test)
tests becoming collectable once `usb` is importable (`tests/conftest.py`'s `collect_ignore` is keyed
on `importlib.util.find_spec("usb") is None`). **Same outcome as the pyusb-absent run in every other
respect: 0 failed, 0 skipped.** This converts D-02's "accepted cost" (a behaviour-under-pyusb-presence
regression the isolated `ci-py32` leg alone would not catch) from an assertion into a measurement,
re-grounded on this session's final HEAD rather than inherited from research's earlier, separate
measurement.

---

## 3. The gate table — command, expected, observed

Every command below was re-executed in this session against the trees as they now stand. Sibling
layout confirmed first: `cd /workspaces/firestarter_app` → `basename "$PWD"` = `firestarter_app`;
`test -e ../firestarter/.git` → present; `ls /dev/ttyACM* /dev/ttyUSB*` → no such device (no serial
board attached, so the known live-board artifact cannot confound this sweep).

### Host repo (`/workspaces/firestarter_app`)

| # | Command | Expected | Observed |
|---|---|---|---|
| H1 | `git log -1 --format=%P 63ce44e` | contains `4ee64a14a8933b60896c8b168bb1c7e34d788fa4` | **`ccbc401e16e2d2298f7376c3086164700bba0278 4ee64a14a8933b60896c8b168bb1c7e34d788fa4`** — contains it, HOST-01's structural claim re-derived |
| H2 | `pytest tests/ --collect-only -q` (verbatim trailer) | a collected count, recorded not gated | **`1293 tests collected in 0.56s`** |
| H3 | `pytest tests/ -q --no-cov` (verbatim run summary) | passed, 0 failed, 0 skipped | **`1293 passed in 164.61s (0:02:44)`**, `30 snapshots passed` |
| H4 | `pytest tests/ --cov=firestarter --cov-fail-under=70` | exit 0, total ≥ 70% | **exit 0** — TOTAL 82% (81.88%); `py32_dfu.py` 79% |
| H5 | Catalog validity check (`codegen.py --check`) | `OK`, exit 0 | **`OK: catalog valid (73 messages, version 1).`** |
| H6 | `messages.py` codegen + `git diff --exit-code` | exit 0, no diff | **`OK: wrote firestarter/messages.py (python, 73 messages).`**, diff exit 0 |
| H7 | Vector catalog validity check | `OK`, exit 0 | **`OK: catalog valid (12 vectors, version 1).`** |
| H8 | `frame_vectors.py` codegen + `git diff --exit-code` | exit 0, no diff | **`OK: wrote firestarter/frame_vectors.py (python-vectors, 12 vectors).`**, diff exit 0 |
| H9 | `ruff check firestarter/ tests/` | clean | **`All checks passed!`** |
| H10 | `ruff format --check firestarter/ tests/` | clean | **`114 files already formatted`** |
| H11 | `python tools/check_mypy_watermark.py` | (devcontainer fail-open reading) | **`mypy errors: 1 (watermark: 35)`** — this is the fail-open bug's reading, not a genuine clean run; see §6 and the CI row for the corrected figure |
| H12 | `pip install -e . && firestarter --help` | renders, exit 0 | **exit 0**, full Click help rendered with all 14 commands |
| H13 | `tests/test_skip_census.py` | passed, `ALLOWED_SKIP_REASONS` unchanged | **5 passed**; `len(ALLOWED_SKIP_REASONS) == 4` (confirmed by direct import: firmware-checkout-absent, meta-ledger-absent, entry-point-absent, `EVIDENCE.json`-absent — the phase added none) |
| H14 | `tests/test_pyusb_api_surface.py --collect-only` inside the full-suite run | **not collected** (pyusb absent) | **0 occurrences** in `pytest tests/ --collect-only -q` output — confirmed by grep count |
| H15 | `importlib.util.find_spec("usb")` | `None` in this devcontainer | **`None`** |
| H16 | `asset_candidates("py32f071")` | Phase 128's contract | **`['firestarter_py32f071.hex', 'firestarter_py32f071.bin']`** — called directly, list recorded verbatim |
| H17 | Four flash-map host constants vs. the live linker script (quoted both sides) | consistent | **host:** `FLASH_BASE=0x8000000`, `FLASH_SIZE=0x20000` (128 KiB), `APP_REGION_SIZE=0x1e000` (120 KiB), `APP_REGION_END=0x801e000`, `CONFIG_REGION_SIZE=0x2000` (8 KiB) · **linker (`/workspaces/firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld`):** `BOOTLOADER (rx): ORIGIN=0x08000000, LENGTH=0` · `FLASH (rx): ORIGIN=0x08000000, LENGTH=120K` · `CONFIG (r): ORIGIN=0x0801E000, LENGTH=8K` · `RAM (xrw): ORIGIN=0x20000000, LENGTH=16K` — **`APP_REGION_END` string-equals `ORIGIN(CONFIG)`; `FLASH_BASE` string-equals `ORIGIN(FLASH)`** |
| H18 | `grep -c 'pragma: no cover' firestarter/py32_dfu.py` | 2 | **2** — both are the `_dev`/`_index` property guards (currently at lines 754/760), untouched by HOST-05; `_require_usb()`'s `except ImportError` line (line 402) carries none |
| H19 | `grep -c 'self\._finish(' firestarter/py32_dfu.py` | 1 | **1** — the single hoisted call site in `flash()` (D-12/C-5) |
| H20 | `grep -c 'no such option' firestarter/cli_handlers.py` | 1 | **1** — D-08's one-code-path property, `_reject_py32_only_option()` |
| H21 | `pip install 'firestarter[py32]'` reject on stable, live probe | `UsageError: no such option: --usb-id` | **reproduced live** (subprocess with `firestarter.__version__` patched to `3.0.0` before import): `click.exceptions.UsageError: no such option: --usb-id` |
| H22 | Each of the seven named test modules, run individually | passed, count recorded | see table below |
| H23 | `grep -c 'extend-exclude' pyproject.toml` | (plan-text said 1) | **2** — one real `[tool.ruff] extend-exclude = [...]` line plus one pre-existing explanatory comment containing the word (127-02's own recorded finding, re-confirmed; not a defect, a stale plan-acceptance-criterion literal) |
| H24 | `git status --porcelain` (host repo) | 5 known pre-existing lines | **5 lines, exactly the known set**: ` M .gitignore`; untracked `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh` |

**Per-module counts (H22), each run individually, this session:**

| Module | Count | Result |
|---|---:|---|
| `tests/test_py32_packaging.py` | 12 | 12 passed |
| `tests/test_dfu_opcode_anchors.py` | 7 | 7 passed |
| `tests/test_py32_channel_gating.py` | 14 | 14 passed |
| `tests/test_py32_flash_map_host.py` | 16 | 16 passed |
| `tests/test_pyusb_gating.py` | 6 | 6 passed |
| `tests/test_py32_pyusb_absent.py` | 11 | 11 passed |
| `tests/test_py32_dfu.py` | 69 | 69 passed (58 pre-existing + 8 `TestReadbackVerification` + 3 `TestInstallWithDfuVerifyLogging`, all from Plan 127-09) |

### Firmware repo (`/workspaces/firestarter`) — read-only input, this phase writes nothing here

| # | Command | Expected | Observed |
|---|---|---|---|
| F1 | `git status --porcelain \| wc -l` | 0 | **0** |
| F2 | `git rev-parse --abbrev-ref HEAD` | `v1.23-py32f071-integration` | **`v1.23-py32f071-integration`** |
| F3 | `git rev-parse HEAD` | unchanged throughout the phase | **`240fb19c50190797ffdc2062d39390e074f8566f`** |

### Meta repo (`/workspaces`)

| # | Command | Expected | Observed |
|---|---|---|---|
| M1 | `git rev-parse --abbrev-ref HEAD` | `gsd/v1.23-py32f071-integration` | **`gsd/v1.23-py32f071-integration`** |
| M2 | Claim gate, explicit target (never the default empty-target path) | exit 0 on this artifact once written | see §7 |

### CI row — two runs, both re-queried read-only this session; the second is authoritative for HOST-04

**Attribution, recorded precisely (this is an input fact, not derivable from the repo alone): the
127-11 gate was removed by explicit operator authorisation mid-phase. Plan 127-11 was structured so
that no task in it contains `git push` or `gh workflow run` — that structural absence was the gate.
The operator explicitly directed the orchestrator (not a task in the plan, and not the operator
personally, unlike Plans 124-11/125-05/126-11) to run both commands. The orchestrator ran the push
and the dispatch. No task inside Plan 127-11 executed either command; the structural gate held from
that plan's own task perspective.**

| # | Field | Run 1 (`30707902225`) | Run 2 (`30708836339`, **authoritative for HOST-04**) |
|---|---|---|---|
| C1 | Run URL | `https://github.com/henols/firestarter_app/actions/runs/30707902225` | `https://github.com/henols/firestarter_app/actions/runs/30708836339` |
| C2 | Event | `workflow_dispatch` | `workflow_dispatch` |
| C3 | Head branch | `v1.23-py32f071-integration` | `v1.23-py32f071-integration` |
| C4 | Head SHA | `84cdd86e1f21f88d59129c849ca2ab0f8c8e1901` | `a62ca7647aed22d8c82ecf3aac3db4a81780260f` — **string-equal to this sweep's HEAD** |
| C5 | Overall conclusion | `failure` | `failure` |
| C6 | `ci-py32` job | **success** | **success** |
| C7 | `ci` (primary) job | **failure** (mypy watermark step) | **failure** (mypy watermark step) |
| C8 | mypy step log | `mypy errors: 72 (watermark: 35)` — `FAIL: 72 errors exceeds watermark 35.` | `mypy errors: 69 (watermark: 35)` — `FAIL: 69 errors exceeds watermark 35.` |
| C9 | `ci-py32` resolved pyusb version | `1.3.1` | `1.3.1` |
| C10 | `ci-py32` pytest step | 6 dots / `[100%]`, success | `......  [100%]`, success (6 tests) |

Both re-queried this session via `gh run view <id> --repo henols/firestarter_app --json ...` and
`gh api repos/henols/firestarter_app/actions/jobs/<id>/logs` (raw log text, not just the summary
JSON). **Run 2's head SHA (`a62ca76…`) is this sweep's own HEAD** — it is the CI evidence for the
phase's final tree, including the mypy fix commit. Run 1 predates that fix (head SHA `84cdd86…`, the
commit before `a62ca76`) and is retained in this table only as the earlier of the two; it is not
cited as HOST-04's discharging evidence.

**HOST-04's claim ("a CI leg installs `.[test,py32]` and exercises the real `pyusb` import and API
surface") is satisfied by `ci-py32`'s green conclusion on Run 2 — 9/9 steps success, `pyusb` resolved
to `1.3.1`, and `tests/test_pyusb_api_surface.py` (6 tests) passed for real on a GitHub-hosted
runner.** The primary `ci` job's RED conclusion is **not** HOST-04's claim and is recorded alongside,
not folded into it — see §6 for the mypy fail-open finding that explains why this branch's local mypy
gate never caught it.

---

## 4. Success criteria — one subsection each, quoting the ROADMAP verbatim

### Criterion 1

> *"`feature/py32f071-fw-install` @ `4ee64a1` is merged (the merge commit's parent SHAs include
> `4ee64a1`), `--usb-id` is rejected on a simulated stable channel by the same mechanism `--dfu-probe`
> already uses, and the full host suite passes in the sibling layout at its **exact collected-test
> count**, 0 failures — not merely 'green.'"*

**Merge-parent check** — H1, re-run this session: `git log -1 --format=%P 63ce44e` contains
`4ee64a14a8933b60896c8b168bb1c7e34d788fa4`. **Discharged by Plan 127-01.**

**`--usb-id` refusal** — H21, reproduced live this session in a subprocess simulating a stable
channel: `click.exceptions.UsageError: no such option: --usb-id`, the identical mechanism
`--dfu-probe` uses (`_reject_py32_only_option()`, `grep -c 'no such option' == 1`). **Discharged by
Plan 127-04.**

**Full suite, sibling layout, exact collected count** — H2/H3, this session: **1293 collected / 1293
passed / 0 failed / 0 skipped.** This is genuinely "not merely green": the *first* real attempt at
this criterion (Plan 127-01's own post-merge run) was **1215/1216, one failure** —
`tests/test_characterization.py::test_help_fw` — directly contradicting research's C-1 "zero fixups"
prediction. Plan 127-04 fixed it under approved added scope. The criterion's literal reading (an
*exact* count, 0 failures) is satisfied at this sweep's HEAD, not at the merge commit alone — the
distinction matters and is recorded rather than smoothed over.

### Criterion 2

> *"A CI leg installs `.[test,py32]` (distinct from the existing `.[test]`-only leg) and a test
> genuinely imports `pyusb`, exercising real calls (`usb.core.find`, `ctrl_transfer`) rather than a
> mock of the module."*

**Discharged by Plans 127-06 (the `ci-py32` job + `workflow_dispatch:`) and 127-11 (the operator-
authorised dispatch and the read-only re-derivation of its result).** This session independently
re-queried **both** CI runs (§3's CI row); Run 2 (`30708836339`, head SHA string-equal to this
sweep's own HEAD) shows `ci-py32` green: `pip install -e .[test,py32]` succeeded, `pyusb` resolved to
`1.3.1` and genuinely imported, and `tests/test_pyusb_api_surface.py` (6 tests, including Plan
127-08's fake-vs-real `ctrl_transfer` signature comparison) passed for real on a GitHub-hosted
runner — never a mock of the `usb` module itself. The primary `ci` job's separate RED conclusion is
recorded in the same row without being folded into this criterion's claim.

### Criterion 3

> *"`PyusbMissingError`'s `# pragma: no cover` is removed and a test exercises that code path
> directly; a separate test proves `fw --list` and `fw --help` both work (exit 0, expected output)
> with `pyusb` genuinely uninstalled in that test's environment."*

**Discharged by Plan 127-07.** H18, re-run this session: `grep -c 'pragma: no cover'
firestarter/py32_dfu.py` == 2 (both are the unrelated `_dev`/`_index` guards; `_require_usb()`'s
`except ImportError` line carries none). `tests/test_py32_pyusb_absent.py` — 11 tests, re-run
individually this session, all passed: 5 in-process (covering the de-pragma'd statements, the
message's three C-4-measured substrings, `__cause__` chaining, the `DfuError` subclass relationship)
and 6 subprocess-based, using a genuine `sys.meta_path.MetaPathFinder` whose `find_spec` **raises**
`ModuleNotFoundError` for `usb`/`usb.*` — proving `fw --help`, `fw --list`, and `firestarter --help`
all exit 0 with `usb` truly unreachable, and that no invocation leaves any `usb*` entry in
`sys.modules` afterward.

### Criterion 4

> *"`DFU_UPLOAD` readback verification fails **soft** (no exception, a recorded soft-fail state) when
> a mock device reports `bitCanUpload = 0`, and one test anchors the DFU opcode literals to UM1504/DFU
> 1.1 values written independently in the test file, not imported from the module under test and
> asserted against themselves."*

**Discharged by Plans 127-09 (the `VerifyResult` enum, the readback/verify sequence, the soft/hard
fail split) and 127-03 + 127-09 (the independent opcode anchors, the `bitCanUpload` handoff closed).**
Re-run this session: `tests/test_py32_dfu.py::TestReadbackVerification` (8 of the module's 69 tests)
— `bitCanUpload = 0` and plain-DFU-1.1 both fail soft with a named `verify_reason` and zero
`DFU_UPLOAD` calls; a matching multi-block readback sets `VERIFIED`; a byte-differing and a
truncated readback both raise `DfuProtocolError` naming the first differing offset and set
`MISMATCH`; ordering is asserted on `device.calls` indices (last `DFU_UPLOAD` strictly precedes the
single hoisted `_finish()` call — H19, `grep -c 'self\._finish(' == 1`); a `MISMATCH` path contains no
zero-length `DFU_DNLOAD` at all, so the device is never told to leave DFU mode on a bad compare.
`tests/test_dfu_opcode_anchors.py` (7 tests, re-run this session, all passed) anchors the DFU 1.1
request codes, the functional-descriptor type, the `bitCanUpload` mask, and the DfuSe/`FLASH_BASE`
constants against independently-written literals — the USB DFU 1.1 half fetched and read directly
from `usb.org` (Plan 127-03); the UM1504-specific half remains a residual, see §6/A1.

### Criterion 5

> *"The `pyusb` floor is `>=1.3.1,<2` in packaging metadata, and channel gating is proven **both
> ways** in one test module: a simulated stable `__version__` hides `py32f071` from `fw --help`'s
> board choices and rejects `--dfu-probe`; a simulated pre-release version exposes both — with an
> explicit assertion that `_BOARD_CHOICES` is computed at import time, not cached stale across a
> version change."*

**Floor** — discharged by Plan 127-02. `grep -n pyusb pyproject.toml` this session confirms
`"pyusb>=1.3.1,<2"` in the `[py32]` extra, held by `tests/test_py32_packaging.py`'s non-vacuous,
fail-closed gate (12 tests total in that module now, re-run this session, all passed).

**Both-ways channel gating** — discharged by Plan 127-04. `tests/test_py32_channel_gating.py` (14
tests, re-run this session, all passed): one subprocess per simulated version
(`firestarter.__version__` patched **before** `firestarter.cli_handlers` is ever imported in that
child process), covering both directions plus the explicit import-time-by-construction assertion
quoting this exact criterion, plus the in-process helper truth table and the one-code-path source
scan.

---

## 5. Decision coverage — all nineteen, D-01…D-19

| Decision | One line | Implemented in | Verified by (this session) |
|---|---|---|---|
| D-01 | CI evidence via `workflow_dispatch:` + operator-personally-run push/dispatch, structural gate not a checkpoint | Plan 127-06 (`workflow_dispatch:`); dispatch performed by the **orchestrator** under explicit operator authorisation (see attribution note, §3 CI row) — **not** the operator personally, differing from Plans 124-11/125-05/126-11 | §3 CI row; both runs re-queried, no task in 127-11 ran either command |
| D-02 | Separate `ci-py32` job, "accepted cost" of not re-running the full suite under pyusb-present | Plan 127-06 | §2's C-8 re-measurement this session (1299/1299/0/0, pyusb-present) — the accepted cost measures as **zero** on the final tree |
| D-03 | Real API-surface test: `usb.core.find` either/or, `ctrl_transfer` signature pinned | Plan 127-06 (base) + Plan 127-08 (fake-vs-real comparison, C-6) | `tests/test_pyusb_api_surface.py`, exercised green on both CI runs (§3 CI row) |
| D-04 | Exact collected count recorded, never gated | This plan (127-12) | §2 — 1158 / 1216 / 1293, all recorded, none asserted `==` anywhere; `test_skip_census.py::test_no_pinned_skip_count` enforces the rejection |
| D-05 | `sys.meta_path` import-blocker subprocess for genuine pyusb absence | Plan 127-07 | `tests/test_py32_pyusb_absent.py` (11 tests, re-run: 11 passed) |
| D-06 | HOST-05 as two tests (in-process coverage + subprocess CLI proof); **CORRECTED by C-3/C-4**: pragma line drifted, message says `WinUSB` not `Zadig` | Plan 127-07 | H18 (`pragma: no cover` count = 2); message-substring tests in `test_py32_pyusb_absent.py` assert `pip install 'firestarter[py32]'`, `libusb`, `WinUSB` — never `Zadig` |
| D-07 | One subprocess per simulated version, import-time computation proven by construction | Plan 127-04 | `tests/test_py32_channel_gating.py::test_board_choices_are_computed_at_import_not_cached_across_a_version_change` |
| D-08 | One shared `_reject_py32_only_option()` for both py32-only options | Plan 127-04 | H20 (`grep -c 'no such option' == 1`); H21 (live refusal reproduced) |
| D-09 | Readback only when `interface.is_dfuse`; plain DFU 1.1 soft-fails with `"load address not under host control"` | Plan 127-09 | `TestReadbackVerification::test_plain_dfu11_fails_soft_with_cause_named` |
| D-10 | `VerifyResult` enum on the flasher; `flash()` stays `bool` | Plan 127-09 | `VerifyResult` members confirmed (`VERIFIED`/`SKIPPED_NO_UPLOAD`/`SKIPPED_PLAIN_DFU`/`MISMATCH`); `firmware.py`'s "written but NOT verified" line, `grep -c` == 1 |
| D-11 | Genuine `MISMATCH` is a hard failure, never soft; no `--force` opt-out | Plan 127-09 | `TestReadbackVerification::test_differing_readback_is_a_hard_failure_too`; `grep -c 'force\|override' firestarter/py32_dfu.py` == 0 (unchanged since the merge) |
| D-12 | Readback strictly before `_finish()`; **CORRECTED by C-5**: the named call-site (`flash()`) never called `_finish()` — hoist shape (b) adopted per operator decision | Plan 127-08 (hoist) + Plan 127-09 (readback insertion) | H19 (`grep -c 'self\._finish(' == 1`); `test_ordering_last_upload_precedes_finish`, `test_mismatch_never_manifests` |
| D-13 | Host envelope guard tightened to `APP_REGION_END`; **no HOST id** | Plan 127-05 | H17 (host constants vs. live linker script, both quoted, matching) |
| D-14 | Fail-closed cross-repo linker-script parity gate, non-vacuity-guarded; **no HOST id** | Plan 127-05 | `tests/test_py32_flash_map_host.py::TestLinkerScriptParity` (5) + `::TestLinkerScriptParityFailsClosedOnBadInput` (3), all inside the 16-test module re-run this session |
| D-15 | `doc/PY32F071-FIRMWARE-INSTALL.md` updated only for facts this phase changed | Plan 127-10 | Doc-vs-constant parity gate in `tests/test_py32_packaging.py` (6 of its 12 tests), re-run this session |
| D-16 | Real `--no-ff` merge commit, `4ee64a1` a literal parent; **CORRECTED by C-1, then re-disproven on the real tree, then fixed** — see §Criterion 1 and §2 | Plan 127-01 (merge) + Plan 127-04 (the fixup C-1's own scratch-worktree measurement did not anticipate) | H1; §2's full narrative |
| D-17 | `flash_method()` router accepted as an accepted deviation; `_install_with_avrdude` untouched | Plan 127-01 (Task 2) + held by Plan 127-02's non-vacuous gate | `tests/test_py32_packaging.py::test_d17_record_phrases_present_and_proximate_to_flash_method`, re-run this session |
| D-18 | Opcode anchoring; **CORRECTED by C-2**: no self-referential assertions exist in `tests/test_py32_dfu.py` to remove — HOST-06 is purely additive | Plan 127-03 (additive module) + Plan 127-09 (closes the `bitCanUpload` handoff) | `tests/test_dfu_opcode_anchors.py::test_test_py32_dfu_still_contains_no_source_source_opcode_oracle`, re-run this session (7/7 passed) |
| D-19 | `pyusb>=1.3.1,<2` in `[py32]`, zero cost on the py39 floor | Plan 127-02 | `grep -n pyusb pyproject.toml`, this session; `tests/test_py32_packaging.py` |

**D-13 and D-14 carry no HOST-01…08 id** — they are recorded, per `127-CONTEXT.md`, as a deliberate
in-scope addition closing a host/linker divergence Phase 126 created, in the only repo that can close
it. They are cited above for completeness of decision coverage, not as evidence for any HOST tick in
§Section on Requirements (see the companion Task 3 edit to `REQUIREMENTS.md`).

**C-2 and C-5 were the two corrections research itself flagged as most likely to misdirect a plan if
applied literally** (`127-RESEARCH.md`'s own framing). Both were applied correctly across the phase:
D-18's "remove or convert" instruction was not followed (it would have damaged 58 working tests to
satisfy an instruction its own source never gave); D-12's edit landed at the hoisted call site in
`flash()`, not at either non-existent named call-site inside the downloaders.

---

## 6. Informational findings carried forward

- **C-1 is disproven on the real tree, not merely re-measured.** `127-RESEARCH.md`'s C-1 claimed
  "zero fixups required" from a scratch-worktree merge. The real, in-session merge (Plan 127-01) left
  the suite at 1215/1216 with one genuine failure
  (`tests/test_characterization.py::test_help_fw`), fixed under approved added scope by Plan 127-04.
  Reproduction command (now green, post-fix): `cd /workspaces/firestarter_app && python -m pytest
  tests/test_characterization.py::test_help_fw -q`.
- **C-8's pyusb-present full-suite measurement, re-taken this session on the final tree
  (`a62ca76`):** 1299 passed / 0 failed / 0 skipped — identical outcome to the pyusb-absent 1293 in
  every respect except the 6 additionally-collected `test_pyusb_api_surface.py` tests. Grounds D-02's
  "accepted cost" as a measurement, not an assertion.
- **A1 — the UM1504 / DFU 1.1 opcode literals are HALF discharged, not resolved.** Plan 127-03
  independently fetched and read the real **USB DFU 1.1 Revision 1.1** specification from `usb.org`
  (sha256 `bbe4a3341c3bfc80cc6ba31b676998c379dcc42602f4b2ca7c5ea8b8dccd5c0d`), confirming the 7 request
  codes, the functional-descriptor type (`0x21`), and the `bitCanUpload` bit position independently.
  **UM1504 (the Puya/ST DfuSe application note) was never obtained** — two read-only fetch attempts
  against `st.com` both failed at the network layer (an environmental failure, not evidence the
  document doesn't exist). The four DfuSe-specific constants (`DFUSE_SET_ADDRESS`, `DFUSE_ERASE_PAGE`,
  `DFUSE_READ_UNPROTECT`, `DFUSE_VERSION`) and `FLASH_BASE` therefore remain **consistent-with-the-
  module rather than independently sourced** — carried forward as a residual, not claimed resolved.
- **A4 — which branch `usb.core.find` took on the CI runner is unresolved from the log, by design of
  the test, not a gap in this sweep.** `tests/test_pyusb_api_surface.py::test_usb_core_find_for_real`
  stores its either/or outcome in a local variable and asserts on it in-process without printing it;
  `pytest -q` suppresses captured stdout on a passing test, and the raw job log (fetched via
  `gh api .../logs`) contains no `NoBackendError`/`enumerated` token. The test's internal assertion did
  fire correctly either way (the step is `success`), so A4's *acceptability* claim holds; *which*
  branch fired on that specific runner is simply not recoverable post hoc. In this devcontainer,
  locally, `usb.core.find(find_all=True)` enumerates (a different, irrelevant machine).
- **A5 — converted from `[INFERRED]` to measured, by Plan 127-08.** Before/after `device.calls`
  sequences for one DfuSe flash (15 calls) and one plain-DFU flash (7 calls) were captured across the
  `_finish()` hoist and diffed element-by-element: identical in both cases. Verified present in
  127-08-SUMMARY.md and consistent with this session's re-run of `tests/test_py32_dfu.py` (69/69
  passed, unmodified assertions for the 58 pre-existing tests).
- **D-17's accepted deviation and the reviewed-not-folded todo.** `avrdude-mcu-detection-fallback`
  targets `_install_with_avrdude`, which HOST-01 explicitly freezes as an accepted deviation —
  correctly **not** folded into this phase. The D-17 comment at `flash_method()` and its five-phrase
  gate (`tests/test_py32_packaging.py`) are both confirmed present this session.
- **The sibling-layout requirement and its 6-failure trap, confirmed structurally present, not
  triggered.** `tests/test_sdp_bus_config_drift.py` and `tests/test_gen_validation_header.py` both
  hardcode `_REPO_ROOT / "firestarter_app"`. This sweep ran from a directory literally named
  `firestarter_app` (H's layout precondition, confirmed first), so the trap did not fire — the full
  suite's 1293/1293 result includes both of those modules passing normally.
- **Four pre-existing `tools/` ruff diagnostics, non-findings, re-confirmed this session and
  unaffected by this phase:** `ruff check tools/` → 4 errors across 3 files
  (`tools/audit_coverage_matrix.py:37` I001, `tools/catalog/codegen.py:36` I001,
  `tools/catalog/codegen_vectors.py:32` I001 and `:189` UP031); `ruff format --check tools/` wants to
  reformat those same 3 files. CI lints only `firestarter/ tests/` (`ci.yml`'s own `ruff` steps), so
  this never reaches a gate. Not this phase's scope; recorded so a later reader does not mistake it
  for new drift.
- **The Phase-129 tripwire.** `tests/test_py32_flash_map_host.py` (specifically
  `TestLinkerScriptParity` and the `BOOTLOADER`-seam assertions) is the gate that will go RED the
  moment Phase 129 gives `BOOTLOADER` a non-zero length — because that moves the application's
  `ORIGIN`, and `APP_REGION_END`/`APP_REGION_SIZE` are currently derived assuming `BOOTLOADER`'s
  length is 0. See `127-CONTEXT.md`'s `<deferred>` section: *"Re-checking D-13's application-region
  constant once `BOOTLOADER` gets a non-zero length → Phase 129. Giving it a length moves the
  application's ORIGIN, so the guard's lower bound moves too, not just its upper."* Plan 127-10's
  documentation-parity gate (`tests/test_py32_packaging.py`) will trip alongside it for the same
  reason, since both are built from `py32_dfu.APP_REGION_END`/`FLASH_BASE`, never a literal.
- **Traceability gap: Plan 127-05's three app commits do not carry the plan ID in their subjects.**
  `921f9eb` (`fix(py32): tighten flash envelope to application region (D-13)`), `1843962`
  (`test(py32): pin the tightened envelope at both boundaries (D-13)`) and `ee6c5af`
  (`test(py32): fail-closed cross-repo linker-script parity gate (D-14, A-7)`) are scoped `(py32)`,
  not `(127-05)` — re-confirmed this session: `git log --grep="127-05"` finds nothing. The work itself
  is complete and correctly attributed to D-13/D-14 in the subject; only the plan-ID convention
  slipped. Enumerated here by SHA so a later reader does not need to re-derive it.
- **The mypy fail-open gate — a first-class finding, recorded and NOT fixed in this phase (Phase
  123's charter owns the gate; the operator's own scope decision, "fix my 3, record the rest," bounded
  this).** `tools/check_mypy_watermark.py` has two stacked fail-open defects, both re-confirmed this
  session:
  1. It shells out to a bare `mypy` resolved from `PATH` (`subprocess.run(["mypy", ...])`), not
     `sys.executable -m mypy` — so its result depends on whichever interpreter/environment happens to
     resolve first, not the project's own installed dependency set.
  2. Under this devcontainer's `PATH`-resolved `mypy` (running on Python 3.12), the project's
     `pyproject.toml` `[mypy]` config (`python_version = "3.9"`) is rejected outright and a numpy stub
     then aborts the run before any real project file is checked — mypy reports **1 error**,
     `count_mypy_errors()` matches it, `1 <= 35`, and the gate prints `OK` **without having
     type-checked a single project file.** Reproduced this session verbatim (H11: `mypy errors: 1
     (watermark: 35)`).

  **The honest measurement, re-derived independently in this session** (bypassing both defects via a
  throwaway venv on `/home/vscode/.local/bin/python3.11`, `.[test]` installed, `<venv>/bin/python -m
  mypy firestarter/ tests/`, then deleted):

  | Snapshot | mypy error count (this session, independent re-derivation) |
  |---|---:|
  | pre-127 baseline (`ccbc401`, via `git archive`) | **69** |
  | post-127, pre-fix (`84cdd86`, via `git archive`) | **72** |
  | post-127, post-fix (current HEAD `a62ca76`, working tree) | **69** |

  **69 → 72 → 69, independently reproduced.** This matches CI Run 2's own step log exactly (§3, C8:
  `mypy errors: 69 (watermark: 35)`) — the runner's clean Python 3.11 environment reports the true
  figure that this devcontainer's fail-open gate cannot see. **Phase 127 adds exactly zero net mypy
  debt.** The 69 inherited errors remain **OPEN** — not this phase's to fix, and not fixed here. The
  primary `ci` job will stay RED on this branch until a dedicated phase (Phase 123's charter, or a new
  one) either fixes the 69 inherited errors or deliberately raises the watermark with justification.
  This is stated plainly so it does not read as a lapse: the operator's own instruction was "fix my 3,
  record the rest," and this document is the record.

---

## 7. Claim ceiling

Stated **by reference** to `.planning/REQUIREMENTS.md` §"Validation Ceiling" — this document does not
reproduce that section's forbidden-phrase list, per the Phase-125 C-16 self-reference trap (all six of
Phase 125's own plan SUMMARYs tripped the claim checker by quoting the forbidden phrases inside their
own compliance paragraphs; `125-NONREGRESSION.md` and `126-NONREGRESSION.md` both avoided it by stating
the ceiling by reference instead, and this document follows the same approach).

**The mock-only ceiling on HOST-03, written so Phase 130's CLOSE-02 honesty ledger can quote it
verbatim (this paragraph is intentionally self-contained):**

> The `DFU_UPLOAD` readback sequence built in this phase — the `VerifyResult` enum, `_read_back()`,
> `_verify_readback()`, and all four of its outcomes — has never run against a PY32F071. No PCB exists
> as of this writing, and no evidence anywhere in this project's history shows any tool, `dfu-util`
> included, ever driving a real PY32 upload. The tests that exercise this sequence do so entirely
> against a mock USB device that answers exactly as it is told — a matching backing image produces
> `VERIFIED`, an altered byte produces `MISMATCH`, a short slice produces a truncation failure. What
> is proven is that the flasher's own logic responds correctly to each of those told answers, and
> nothing beyond that. The dialect fork this module implements (`DFUSE`-style readback versus plain
> DFU 1.1's soft-skip) has likewise never been exercised against a real bootloader, so it is unknown
> which of its two branches a real PY32F071 device would actually take, or whether either branch's
> assumptions hold on real silicon.

**Two adjacent non-claims, recorded alongside for completeness:**

- **The DfuSe-versus-plain-DFU fork is untested against reality.** No public evidence exists that any
  tool has ever driven a PY32 upload of either dialect, so one of the module's two branches has never
  been the branch a real bootloader actually takes.
- **"Success" on this path currently means only that the transfer completed and, where verification
  was possible, the readback matched — nothing more.** It does not mean the programmed firmware boots
  or operates correctly, and it does not mean any part of the sequence has been validated against a
  bench or real hardware.

**What this document does not claim, in its own words, using `.planning/REQUIREMENTS.md`'s
§"Validation Ceiling" as the standard it holds itself to:** it does not claim the DFU install works
end to end; it does not claim PY32F071 firmware has been confirmed to execute on real silicon; it
does not claim any part of this sequence has been confirmed working on a bench or on real hardware in
any unqualified sense; and it does not claim the provisional PY32F071 pin assignment has been
confirmed accurate. The only claims made anywhere in this document are the seven listed in §1, each
cited to a specific, re-executed row.

**The claim gate, run for real, target named explicitly** (this artifact):

```
$ cd /workspaces && python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py \
    .planning/phases/127-host-dfu-installer/127-NONREGRESSION.md
```

Result recorded in the Self-Check section of `127-12-SUMMARY.md`, the companion document to this
artifact, per this phase's own discipline that the gate must be run against the finished artifact
with an explicit target (never the default empty-target path) and that a trip is fixed by rewording
the artifact, not by weakening the gate.

---

## Sweep Summary

| Gate | Result |
|---|---|
| Host `git log -1 --format=%P` on the merge commit | contains `4ee64a1` — HOST-01 confirmed |
| `pytest --collect-only` (verbatim trailer) | **1293 tests collected in 0.56s** |
| `pytest tests/ -q --no-cov` (verbatim run summary) | **1293 passed in 164.61s (0:02:44)**, 30 snapshots passed |
| Coverage | **81.88%** total (70% floor); `py32_dfu.py` 79% |
| Eight primary `ci.yml` gate commands, local | all exit 0 (mypy gate's local reading is the known fail-open bug, see §6) |
| Seven named test modules, individually | all green — 12/7/14/16/6/11/69 |
| Skip census | 5 passed, `ALLOWED_SKIP_REASONS` at 4, unchanged |
| `test_pyusb_api_surface.py` collection | confirmed **not collected** in the full-suite run (pyusb absent) |
| `find_spec("usb")` | `None`, confirmed |
| `asset_candidates("py32f071")` | `['firestarter_py32f071.hex', 'firestarter_py32f071.bin']` — called and recorded |
| Flash-map host constants vs. live linker script | both quoted, matching |
| Three grep counts (pragma=2, finish=1, refusal=1) | all confirmed |
| C-8 pyusb-present full suite, re-taken this session | **1299 passed, 0 failed, 0 skipped** |
| CI Run 1 (`30707902225`) | `ci-py32` success, `ci` failure (mypy 72 > 35) |
| CI Run 2 (`30708836339`, final tree, authoritative) | `ci-py32` success, `ci` failure (mypy 69 > 35), head SHA string-equal to this sweep's HEAD |
| mypy honest re-derivation (independent throwaway venv) | **69 → 72 → 69**, matching CI Run 2 exactly — zero net Phase 127 debt |
| Firmware repo | untouched — 0 porcelain lines, HEAD unchanged |
| Meta repo claim gate | run with an explicit target against this artifact — see §7 / SUMMARY self-check |
| No push, tag, release, or `beta` touch performed by this plan | confirmed |

**This phase's entire verification surface is green except for two honestly-recorded, pre-existing,
non-Phase-127 findings: the primary `ci` job's mypy-debt RED (69 inherited errors, zero contributed by
this phase) and A1's UM1504 residual (network-unreachable, not a document-existence finding).** Every
figure in this document was re-executed against the tree exactly as it stands at the end of this
phase, in this session — including both CI runs, re-queried read-only, and an independent mypy
re-derivation in a fresh throwaway venv. This plan resolves HOST-01…HOST-08 in
`.planning/REQUIREMENTS.md`, each citing the specific row above (or the discharging plan) that
resolves it.
