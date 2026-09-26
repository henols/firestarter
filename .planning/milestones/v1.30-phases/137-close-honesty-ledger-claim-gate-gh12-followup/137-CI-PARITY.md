# Phase 137 — Final Whole-Milestone CI-Parity Record

Per ROADMAP.md's Phase 137 cross-cutting instruction: "Run the CI-parity recipe one final time over
the whole milestone diff before closing." This is the **last** CI-parity measurement of v1.30 — it
covers the accumulated diff of all seven active phases (131, 132, 133, 134, 136, 136.1, 137), not
merely this phase's own delta. Measured 2026-08-05, from `/workspaces/firestarter_app`, branch
`gsd/v1.30-sdp-surface-retirement`, HEAD `cc036e8dc3cd77bbdfc7ec5190d79cdb172153c7` (unchanged by this
plan — 137-06 makes no submodule commit; the meta-repo's own claim gate/RECORD are this plan's only
edits). Every number below is a **live re-run**, using `tools/ci_replica_venv.sh`'s venv, never the
devcontainer's ambient Python 3.12 — the only local path to a real mypy count in this environment.

---

## Before (Phase 136.1's own close, the last prior whole-milestone reading)

Cited from `136.1-CI-PARITY.md`'s own `## After (phase close)` section (measured 2026-08-05, HEAD
`31b5d74`):

| Metric | Value |
|---|---|
| mypy errors (watermark 35) | 33 |
| mypy headroom | 2 |
| checked source files | 132 |
| full suite (`pytest tests/`) | 1504 passed |
| coverage | 82.14% |
| ruff (check + format) | clean |
| SDP partition (ALLOW/REFUSE/TOTAL) | 43/41/84 |

---

## After (whole-milestone, phase close) — this plan's own live re-measurement

### 1. `python3 tools/check_diagnostic_report_claims.py` (plan 137-02) — re-confirmation

```
$ python3 tools/check_diagnostic_report_claims.py
PASS: scanned /workspaces/firestarter_app/tools/../firestarter/diagnostic_report.py, 164 string literals checked, zero forbidden matches
```

Exit 0. **Unchanged** — no plan in 137-03/04/05 touches `diagnostic_report.py`, so this is a
confirmation, not an expected change, and it is recorded live rather than assumed.

### 2. `tools/ci_parity.sh` — every leg's exit status, verbatim

```
CI-parity recipe (GATE-09) -- repo root: /workspaces/firestarter_app

Leg 1 (pytest, empty sibling root):  exit 0
Leg 2 (pytest, sibling present):     exit 0
Leg 3 (ruff check + format --check): exit 0
Leg 4 (mypy watermark gate):         exit 2
BOARD-ATTACHED: none
Python: Python 3.12.13
CI-PARITY: FAIL (legs:4)
```

**Identical in shape to every prior phase's own recorded run in this milestone** — legs 1-3 exit 0,
leg 4 exits 2 for the same documented reason (the devcontainer's ambient Python 3.12 `numpy` stub
truncates mypy at a PEP-695 syntax error before it can report a count; `error: Type statement is only
supported in Python 3.12 and greater [syntax]`, `Found 1 error in 1 file (errors prevented further
checking)`). `tools/ci_replica_venv.sh` below is the only local path to a real mypy count. No leg's
exit code has moved at any point across this entire milestone.

### 3. `tools/ci_replica_venv.sh` — all five legs + the two certifying lines

```
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
MYPY-VERSION: mypy 2.3.0 (compiled: yes)
NUMPY-PRESENT: no
Leg 1 (venv create-or-reuse + install): exit 0
Leg 2 (numpy absent):                   exit 0
Leg 3 (ruff check + format --check):    exit 0
Leg 4 (mypy watermark gate):            exit 0
Leg 5 (pytest --cov, CI's exact args):  exit 0
CI-REPLICA: PASS
```

**Certifying lines, verbatim:**

```
Found 33 errors in 13 files (checked 129 source files)
checked 129 source files
mypy errors: 33 (watermark: 35)
```

**mypy watermark is NOT moved** — stays at **35** regardless of the measured 33-error count, per this
task's own explicit instruction. Ruff: `All checks passed!`, `127 files already formatted` — clean.

Leg 5's full suite: **1508 passed, 1 warning** in 205.03s, coverage **82.14%** against the 70% floor
(30 snapshots passed).

### 4. `tests/test_sdp_db_invariant.py` — explicit, standalone re-run

```
$ .venv/ci-replica/bin/python -m pytest tests/test_sdp_db_invariant.py -o addopts="" -q
.........
9 passed in 0.17s
```

All 9 legs green, including both partition-comparison legs (the hand-curated-snapshot check and the
`infoic`-derived-DB-field check) — both independently agreeing the partition is unchanged.

### 5. SDP partition — fresh, independent re-derivation this plan (not read from any prior citation)

A fresh Python pass over the live `chip_database.json`, via the production `sdp_capability_for_entry`
predicate (the same bridge `tests/test_sdp_db_invariant.py` uses: `chip_database.json`'s `part_number`
and `programming.algorithm` synthesized into the `{"protocol-id": ..., "name": ...}` shape the
predicate reads):

```
FULL DB: ALLOW 43  REFUSE 703  TOTAL 746
0x0D:    ALLOW 43  REFUSE 41   TOTAL 84
ALLOW chips with nonzero chip-id: []
```

**Confirms the 43/41/84 `0x0D` partition, unchanged across the entire milestone** — this phase touches
no database file. Also independently re-confirms `137-LEDGER.md`'s claim class 1 (43/41/84) and claim
class 7 (the full-DB REFUSE population is 703, a superset of the 41 protocol-`0x0D`-scoped figure) and
claim class 6 (zero ALLOW chips carry a nonzero `chip-id` — the chip-ID destructive gate stays
structurally vacuous for the whole ALLOW population, exactly as recorded).

### 6. Reconciliation against the Phase 136.1 baseline — every delta named, none silently asserted

| Metric | Phase 136.1 close (Before) | This plan's live measurement (After) | Delta | Reconciled |
|---|---|---|---|---|
| mypy errors (watermark 35) | 33 | 33 | **0** | Unmoved. |
| mypy headroom | 2 | 2 | **0** | Unmoved since Phase 133 (see `137-LEDGER.md`'s own corrected negative-space bullet — the error count moved 32→33 during Phase 133, per `132-RECORD.md` residual 2 / `133-RECORD.md` residual 4, and has not moved since). |
| checked source files | 132 | 129 | **-3** | **Reconciled, not silently accepted:** plan 137-02 added `exclude = ["^tests/fixtures/"]` to `[tool.mypy]` (Rule 3 fix — the required `planted_unparsable.py` fixture's genuine `SyntaxError` otherwise aborted mypy's whole directory walk). This excludes the 8-file `tests/fixtures/` directory (6 pre-existing + 2 new) from mypy's walk. Still **9 above** `MIN_CHECKED_SOURCE_FILES = 120`. A genuine, disclosed, floor-respecting reduction — `137-LEDGER.md`'s mechanism-correction #7 names this explicitly as "a genuine reduction, and the floor exists to notice exactly this class of change, not to wave it through silently." |
| full suite (`pytest tests/`) | 1504 passed | 1508 passed | **+4** | Exactly plan 137-02's own four new tests (`tests/test_check_diagnostic_report_claims.py`'s 4 subprocess-level legs). No plan in 137-01/03/04/05/06 adds a test to the `firestarter_app` submodule — 137-01 and 137-03/04/05/06 are meta-repo-only (the claim gate, the ledger, the release notes/decision doc, the gh#12 reply, and this record all live under `.planning/`). |
| coverage | 82.14% | 82.14% | **0.00 pp** | Unmoved. |
| ruff (check + format) | clean | clean | **0** | Unmoved. |
| SDP partition (ALLOW/REFUSE/TOTAL) | 43/41/84 | 43/41/84 | **0** | Unmoved — re-derived three independent ways this plan alone (partition invariant suite, live `sdp_capability_for_entry` pass, `chip-id` sweep). |

**No metric changed silently.** The only non-zero delta (checked-file count, -3) is a previously-disclosed,
floor-respecting consequence of plan 137-02's own Rule-3 fix, not a new finding this plan made — carried
forward from `137-02-SUMMARY.md` and `137-LEDGER.md`'s mechanism correction #7, reconciled here against
the Phase 136.1 baseline specifically (the prior CI-PARITY doc predates plan 137-02, so this is the
first CI-PARITY table to show the -3 delta explicitly).

### 7. Firmware submodule and package-manager confirmation

```
$ git -C /workspaces/firestarter status --porcelain
(empty)
```

No file under `/workspaces/firestarter/` (the firmware submodule) was touched at any point in Phase
137's six plans — v1.30 is host-only throughout.

```
$ git -C /workspaces/firestarter_app log --oneline a61a7814..HEAD -- '*.txt' pyproject.toml setup.py
(empty)
```

No `requirements*.txt`, `pyproject.toml`, or `setup.py` change appears anywhere in Phase 137's commit
range (from plan 137-01's first commit to HEAD) beyond the `[tool.mypy] exclude` line already accounted
for in row 3 above (a config-only edit, not a dependency change) — zero new pip/npm/cargo package
installed anywhere in this phase.

### Observed board state

`ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null` → no matches (no board attached). `ci_parity.sh` has no
no-board leg; this is an ambient observation, never a claimed leg.

---

## Whole-milestone summary (Phase 131 → Phase 137, every phase's own CI-PARITY reading)

| Phase | mypy errors/watermark | checked files | full suite | coverage | SDP partition |
|---|---|---|---|---|---|
| 131 (close) | 69/35 (baseline, unratcheted) | — | — | — | 43/41/84 (GATE-08 introduced) |
| 132 (close) | 32/35 | — | — | — | 43/41/84 |
| 133 (close) | 33/35 | — | — | — | 43/41/84 |
| 134 (close) | 33/35 | 126 | — | — | 43/41/84 |
| 136 (close) | 33/35 | 130 | 1494 passed | 82.14% | 43/41/84 |
| 136.1 (close) | 33/35 | 132 | 1504 passed | 82.14% | 43/41/84 |
| **137 (this record, whole-milestone close)** | **33/35** | **129** | **1508 passed** | **82.14%** | **43/41/84** |

**The mypy watermark has never moved from 35 across the entire milestone.** The true error count fell
69 → 32 at Phase 132's own close (RETIRE-\* discharging the mypy debt) and has sat at 33 (2 of headroom)
since Phase 133 — unmoved for five consecutive phase closes. The SDP partition has never moved at all,
across any phase, at any point — re-verified independently well over a dozen times across Phases 131,
133, 134, 136.1, and this record. The full suite grew monotonically (1494 → 1504 → 1508) as
Phase 136.1 and Phase 137 each added their own tests, with zero deletions and zero regressions
anywhere in the range.

---

*Phase: 137-close-honesty-ledger-claim-gate-gh12-followup*
*Measured: 2026-08-05, plan 137-06, against `firestarter_app` HEAD `cc036e8` (unchanged by this plan)
and meta-repo `137-LEDGER.md`/`132-RECORD.md`/`133-RECORD.md`/`136.1-CI-PARITY.md` as cited above.*
