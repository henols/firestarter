# Phase 131 Plan 06: CI-Parity Recipe — Recorded Run (GATE-09)

**Date:** 2026-08-03
**Repo:** `firestarter_app`, branch `gsd/v1.30-sdp-surface-retirement`, HEAD `632434fae10a9b48301a89379849385ad637aee2` at recording time (script itself committed as `8caf77f`, one commit later, on the same branch)
**Interpreter:** Python 3.12.13 (this devcontainer) — CI runs 3.11
**mypy:** 2.3.0 (compiled: yes)
**Script:** `firestarter_app/tools/ci_parity.sh`

**This document records what was measured. It does not claim `firestarter_app`'s primary `ci` job
is green — it is not, and stays RED until Phase 132.**

---

## How this run was produced

Ran twice, to prove the script anchors on its own location rather than the caller's working
directory:

1. From a foreign working directory (`/tmp`) — `bash /workspaces/firestarter_app/tools/ci_parity.sh`
2. From the repo root — `cd /workspaces/firestarter_app && bash tools/ci_parity.sh`

Both runs produced **identical** leg banners, leg exit codes, board stamp, and aggregate result.
The transcript below is run 2 (repo root); run 1 (from `/tmp`) matched leg-for-leg (Leg 1 exit 0,
Leg 2 exit 0, Leg 3 exit 0, Leg 4 exit 2, `BOARD-ATTACHED: none`, aggregate `CI-PARITY: FAIL
(legs:4)`).

Confirmed first that no board was attached: `ls /dev/ttyACM* /dev/ttyUSB*` → both patterns report
"No such file or directory". This run's `BOARD-ATTACHED: none` stamp is a live enumeration, not a
fabricated value.

---

## Per-leg table

| Leg | Command | Exit code | What it proves |
|-----|---------|-----------|-----------------|
| 1 | `FIRESTARTER_FW_ROOT=<mktemp -d dir> python3 -m pytest tests/ -q` | **0** | The suite passes with the firmware sibling **absent** — the standalone-CI condition this devcontainer otherwise hides. 38 tests SKIPPED in this leg (the firmware-repo-dependent modules, correctly `requires_fw`-skipped under an empty sibling root), 0 failures. |
| 2 | `python3 -m pytest tests/ -q` | **0** | The suite passes with the firmware sibling **present** (this devcontainer's own layout, including the tests leg 1 skips). |
| 3 | `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` | **0** | `ruff check` → "All checks passed!"; `ruff format --check` → "116 files already formatted". CI's exact path set, neither wider nor narrower. |
| 4 | `python3 tools/check_mypy_watermark.py` | **2** | See "Leg 4 — expected local exit 2" below. This is the deliverable working, not a defect. |

**Board stamp, quoted verbatim from the summary:** `BOARD-ATTACHED: none`

**Aggregate script exit code: 1** (`CI-PARITY: FAIL (legs:4)`) — non-zero because leg 4 failed.
**Phase acceptance does not require a zero aggregate exit.** It requires all four legs to run,
each to print its own exit code, the board stamp to say `none`, and the only failing leg to be
leg 4 for the stated reason — all four hold in this run.

---

## Full summary block, verbatim (run 2, from the repo root)

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

## Leg 4 transcript, verbatim

```
---------------------------------
Leg 4: python3 tools/check_mypy_watermark.py
Proves: the hardened watermark gate (GATE-01/02/03/04) reaches a legible terminal state. A local
exit 2 here (ambient numpy PEP-695 stub truncating mypy) is the gate working correctly, not a
script defect -- see this script's header and 131-CI-PARITY.md.
---------------------------------
ERROR: mypy exited 2, which is neither the clean-run (0) nor errors-found (1) exit code. Treating
as a tool/config failure, not a clean tree.
/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only
supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
Leg 4 exit code: 2
```

## Leg 4 — expected local exit 2, explained

Leg 4 exited **2** because an ambient `numpy` stub installed in this devcontainer
(`/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737`) uses a PEP-695 `type` statement
that is only valid syntax under Python 3.12+. mypy, invoked here under this same 3.12 interpreter,
trips on that stub file while type-checking and aborts mid-run, printing
`(errors prevented further checking)` with **no** `(checked N source files)` completion clause.
Phase 131's hardened `classify_mypy_result()` (131-01) requires that completion clause before it
will trust any parsed error count; its absence here correctly routes to `sys.exit(2)` — "the run
cannot be trusted as a complete, well-formed mypy run" — rather than silently reporting a
plausible-but-wrong count, which is exactly what the **pre-hardening** checker did (measured at
131-01 plan time: `mypy errors: 1 (watermark: 35)`, exit 0 — the fail-open this phase closes).

**This is the Phase 131 deliverable working, not a script defect.** Do not "fix" this by weakening
a guard, adding `|| true`, or excluding leg 4 from the recipe to force a green aggregate exit.

**The same leg is expected to exit differently in CI.** CI runs Python 3.11 (`ci.yml:33-36`),
which does not carry this devcontainer's ambient numpy PEP-695 stub, so mypy is expected to run to
completion there and report the real inherited count — research measured **69 errors** against the
watermark of **35** at the v1.23 close, so leg 4 is expected to exit **1** in CI (count exceeds
watermark), not 2. Both are non-zero for different, legitimate reasons: locally, the tool run
itself cannot be trusted; in CI, the tool run completes and reports more errors than the watermark
allows. **`firestarter_app`'s primary `ci` job stays RED until Phase 132** in either case — this
phase sets no watermark, deletes nothing, and fixes no mypy errors.

---

## D-10: `check_no_exists_proxy.py` — one-time recorded confirmation, not a recipe leg

Run once, separately from the recipe, per D-10:

```
$ python3 tools/check_no_exists_proxy.py; echo "EXIT: $?"
PASS: scanned 79 file(s) for the module-level absence-proxy idiom: tests/__init__.py,
tests/conftest.py, tests/fw_presence.py, ... tests/test_check_mypy_watermark.py, ...
tests/write_skip_erase_0x0d.py, tests/test_write_skip_sdp_unlock.py
EXIT: 0
```

**Exit code: 0.** The `PASS:` line names 79 scanned files, including
`tests/test_check_mypy_watermark.py` — the module 131-02 added and registered in this checker's
`_DEFAULT_TARGETS` in the same commit (F-06) — confirming that registration survived intact.

**This confirmation is explicitly a one-time recorded check, not a leg of `tools/ci_parity.sh`.**
`ci.yml` runs no such step (confirmed: the string does not appear anywhere in `ci.yml`), and
running it as a recipe leg would make the recipe an unfaithful mirror of CI. Its own behaviour is
already covered on every recipe run by its paired pytest module (`tests/test_check_no_exists_proxy.py`),
which both leg 1 and leg 2 run as part of the whole `tests/` suite. This single run discharges
STATE.md's standing note that the `_FW_ABSENT` idiom was fixed for the host suite in Phase 123 and
*"six modules shared it — worth confirming none survive"* — confirmed here: **none survive**
outside the one recognised marker module (`tests/fw_presence.py` itself, which defines the
canonical idiom rather than proxying it).

---

## D-17 — record-only correction, not acted on

Research's operator-decision #7(a) and PITFALLS P-18 item 4 are **wrong on repo, on commit, and
on substance**, verified live this session:

1. **Wrong repo.** The test named,
   `test_present_root_with_missing_target_raises_not_skips`, is at
   `firestarter/tests/test_flash_path_record_sync.py:694` — the **firmware** repo, which this
   milestone does not touch at all. It is **not** in `firestarter_app`; no agent should hunt for it
   there, and no agent should edit the firmware repo to "fix" it.
2. **Wrong commit.** The softening being described is firmware commit `1c511e8`, not app commit
   `5934a54` — the commit research named. `5934a54` touched `tests/test_py32_flash_map_host.py`
   and `tests/test_scan_paths_resolve.py`, neither of which is the test in question.
3. **Not a weakened assertion.** Reading the code directly: the gate's own subject — that a
   missing scan target **raises** `MissingScanTargetError` rather than being silently skipped — is
   still **hard-asserted** wherever its premise holds. What was actually scoped is the
   **environment premise** (`META_PRESENT`), which a prior phase had written as a bare
   `assert META_PRESENT`, hard-asserting an *environment fact* into a test failure rather than
   scoping the test to when that fact holds. The companion
   `test_absent_meta_claim_can_never_be_false` makes a false absence claim impossible by
   construction, closing the abuse path the "softening" framing worried about.

**Disposition: record the correction, do not act on it.** This is discharged as a correction to
the research record, not as work performed in this plan. Phase 137's ledger carries it as a
negative-space row. STATE.md's own phrasing (*"softened a Phase-129-authored hard assert to a
skip — a defect-class change"*) is itself the source of the mischaracterisation and is imprecise.

---

## D-18 — record-only correction, not acted on

`81fa53c` (`fix(122-07): skip firmware-checkout-dependent clean-source tests in standalone CI`,
adding `skipif` guards to `test_check_is_memory_cmd_no_ifdef.py` and
`test_check_no_log_in_sdp_window.py`) is confirmed **present** in the `firestarter_app` repo's
history. `main` has never been merged in any of the three project repos, so the carry this commit
represents stays latent — acting on it now would be work against a merge that is not happening.

**Its criterion is negative, and this run discharges it mechanically.** Because this phase's work
sits in `check_no_log_in_sdp_window.py`'s neighbourhood, the obligation D-18 states is: *any test
this phase adds must pass under recipe leg 1 (empty sibling root)*. This is not asserted in prose —
it is checked mechanically by leg 1 itself. Leg 1's transcript above (**exit 0**, 38 expected
firmware-dependent skips, zero unexpected failures) ran the full `tests/` suite, which includes
every module this phase's three prior plans added to or extended:

- `firestarter_app/tests/test_check_mypy_watermark.py` (131-02, newly created)
- `firestarter_app/tests/test_sdp_db_invariant.py` (131-03, extended)
- `firestarter_app/tests/test_check_devtest_orchestrator.py` (131-04, extended)

All three passed under leg 1's empty-sibling-root condition, in the same run whose transcript is
recorded above. D-18's negative criterion is discharged.

---

## Summary of what this plan did and did not do

- **Set no watermark.** `pyproject.toml`'s `# mypy_error_watermark = 35` (`:159`) is untouched by
  this plan.
- **Deleted nothing.**
- **Fixed no mypy errors.** Not one of the locally-observed 1 (truncation artifact) or the
  CI-measured 69 (research figure, to be reconciled by Phase 132).
- **`firestarter_app`'s primary `ci` job is RED before and after this plan, by design.** Any
  sentence anywhere in this document implying otherwise would be the v1.22 C-5 overclaim class —
  none exists here.
- `firestarter` (firmware) remains completely untouched: `git -C /workspaces/firestarter status
  --short` is empty; HEAD is unchanged at `0933bd7d602efb30e4a666e8231ecf724e90ab09` throughout
  this plan.
- No push, tag, merge, remote CI dispatch, or release/publish command was run by this plan.
