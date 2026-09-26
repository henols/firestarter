---
phase: 148
slug: numeric-database-values-the-at28c-vcc-decode
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-19
---

# Phase 148 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `148-RESEARCH.md` §"Validation Architecture" — every command below was **run** by
> the researcher against the live tree on 2026-08-19, not inferred.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` 8.x + `syrupy` (snapshots) + `pytest-cov`, via `pip install -e '.[test]'` |
| **Config file** | `firestarter_app/pyproject.toml` — `[tool.pytest.ini_options] addopts = "-ra -q"` |
| **Quick run command** | `python3 -m pytest tests/<file>.py -o addopts="" -q` |
| **Full suite command** | `python3 -m pytest -o addopts="" -q` |
| **Estimated runtime** | ~280 s full suite (1616 passed) — **allow ≥ 600 s timeout** |

> ⚠️ **`-q` doubling trap.** `addopts` is already `-ra -q`; adding another `-q` **suppresses the
> count line**, so a run that collected nothing looks identical to a run that passed. Always pass
> `-o addopts=""`. All commands in this file already do.

**Working directory for every command below:** `/workspaces/firestarter_app`.

---

## Sampling Rate

- **After every task commit:** the targeted test file(s) — e.g.
  `python3 -m pytest tests/test_diff_db_gate.py tests/test_chip_database_field_inventory.py -o addopts="" -q` (< 5 s)
- **After every plan wave:**
  `python3 tools/build_db.py && python3 tools/diff_db.py && python3 tools/check_dispatch.py && python3 -m ruff check firestarter/ tests/`
- **Before `/gsd-verify-work`:** full suite green + all four gates + `git diff --quiet` on
  `tools/check_dispatch.py` and `tests/__snapshots__/`
- **Max feedback latency (measured 2026-08-19, not estimated):** < 0.3 s for every unit/gate
  suite this phase touches (`test_diff_db_gate` 0.24 s, `test_chip_database_field_inventory` 0.18 s,
  `test_ic_layout` 0.13 s, `test_eprom_info` 0.09 s, `test_extra_chips_supplement` 0.17 s);
  **16.7 s** for the two tasks that run `tests/test_characterization.py` (35 subprocess CLI
  snapshots — Plan 04 Task 2 and Plan 06 Task 3); ~280 s per full-suite phase gate.

---

## Per-Task Verification Map

> Task IDs are assigned by the planner; the rows below are the **behaviors** that must each land on
> a task. `File Exists` is measured — ❌ W0 means the test does not exist yet and is a Wave 0 gap.

| Behavior | Requirement | Test Type | Automated Command | File Exists | Status |
|----------|-------------|-----------|-------------------|-------------|--------|
| `firestarter info AT28C256` renders `VCC: 5.0v` (was `4.0v`); VPP row unchanged | DATA-01 | integration (CLI snapshot) | `python3 -m pytest tests/test_characterization.py -o addopts="" -q` | ❌ W0 — no AT28C info test exists (F-3) | ⬜ pending |
| Exactly 56 chips moved `vcc_mv` 4000→5000; **no chip's `vcc_mv` decreased**; all 56 land on their own `vdd_mv` | DATA-01 | unit (data) | `python3 -m pytest tests/test_vcc_margin_rail.py -o addopts="" -q` | ❌ W0 | ⬜ pending |
| `VCC_VOLTAGES[0x02]` still decodes the margin rail — the **table is not edited**, the rule sits after it | DATA-01, DATA-04 | unit | same file | ❌ W0 | ⬜ pending |
| Field-inventory golden matches: `vcc_mv`/`vdd_mv`/`vpp_mv` at 746, `vpp` absent, `pulse_duration_us` at 746 | DATA-02 | gate | `python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -v` | ✅ exists — golden **re-derived**, not hand-edited | ⬜ pending |
| `interpret_timing` **fails the build** on an unparseable `pulse_delay` (D-08) | DATA-02 | unit | new test importing `tools/build_db.py` | ❌ W0 — **not provable by a regen** (branch is dead across all 27,862 `<ic>` elements) | ⬜ pending |
| Render output byte-identical — `tests/__snapshots__/test_characterization.ambr` **unchanged** | DATA-02 | snapshot | `python3 -m pytest tests/test_characterization.py -o addopts="" -q` then `git diff --quiet tests/__snapshots__/test_characterization.ambr` | ✅ 30 snapshots exist | ⬜ pending |
| No `.replace("V","")` → `float()` path and no `_parse_pulse_duration` in `database.py` | DATA-03 | unit (source scan) | new grep/AST assertion | ❌ W0 | ⬜ pending |
| No `parse_pulse_us` anywhere in `audit_coverage_matrix.py` | DATA-03 | unit (source scan) | same | ❌ W0 | ⬜ pending |
| **746-chip wire-dict byte equivalence** against the pre-change capture | DATA-03 | integration | `python3 -m pytest tests/test_wire_dict_equivalence.py -o addopts="" -q` | ❌ W0 | ⬜ pending |
| `_PAGE_SIZE_BY_PART` still has exactly 2 entries; no new part-number-keyed dict in `build_db.py` | DATA-04 | unit (AST) | new assertion | ❌ W0 | ⬜ pending |
| `diff_db.py` exit 0; changed-chip total still **744**; every pre-existing bucket count unchanged; one **new** `RULE_VCC_MARGIN_RAIL` bucket of exactly **56** | DATA-05 | gate | `python3 tools/diff_db.py; echo EXIT=$?` + `python3 -m pytest tests/test_diff_db_gate.py -o addopts="" -q` | ✅ exists — comparator + rule added | ⬜ pending |
| GATE-03 zero violations **and** the gate file is byte-unchanged | DATA-05 | gate | `python3 tools/check_dispatch.py; echo EXIT=$?` + `git diff --quiet tools/check_dispatch.py` | ✅ exists | ⬜ pending |
| `tools/extra_chips.json`'s 2 records carry the numeric schema (F-1) | DATA-02, DATA-03 | unit (data) | field-inventory gate + wire-dict equivalence | ✅ covered by the two gates above | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

**Ordering constraint — this is not negotiable.** The wire-dict capture must be **task 1 of the
phase, before any edit**, or the equivalence claim has no baseline to compare against.

- [ ] `tests/golden/wire_dict_baseline.json` — 746-chip pre-change capture via
      `EpromDatabase(skip_local_override=True)` → `convert_to_programmer`. Measured: 746/746
      resolvable, 0.43 s, 332,716 bytes, canonical SHA-256
      `027a43a0dcef1085afa6a35d2500bd35556140dde4b838dfcd65bfae8cac7dab`. — DATA-03
- [ ] `tests/test_wire_dict_equivalence.py` — asserts byte-identity against that fixture. Note the
      wire dict has **9** keys, not five (F-8): `algorithm, bus-config, chip-id, flags,
      memory-size, page-size, pin-count, pulse-delay, vpp_mv`. A five-key fixture would miss
      `bus-config`, `flags` and `page-size`. — DATA-03
- [ ] `tests/test_vcc_margin_rail.py` — the 56-mover assertions, the no-decrease guard, and
      `VCC_VOLTAGES[0x02]` unchanged. — DATA-01
- [ ] A new `firestarter info AT28C256` snapshot (e.g. `test_info_at28c256`) — **the only coverage
      criterion 1 will have.** This is a *new* snapshot, not a re-baseline of a pinned one, so
      v1.30 Phase 136's no-silent-re-baseline rule is not engaged. — DATA-01
- [ ] A unit test for D-08's fatal branch on `interpret_timing` — **unreachable via a regen**, so a
      green build proves nothing here. — DATA-02
- [ ] Source-scan assertions: no `_parse_pulse_duration` / `.replace("V","")` in `database.py`; no
      `parse_pulse_us` in `audit_coverage_matrix.py`. — DATA-03
- [ ] An AST assertion that `_PAGE_SIZE_BY_PART` still has 2 entries and that no new
      part-number-keyed dict exists in `build_db.py`. — DATA-04
- [ ] Update `tests/test_diff_db_gate.py:86-91,118-123` to the numeric schema — the only existing
      fixture file affected.
- [ ] Re-derive `tests/golden/chip_database_field_inventory.json` **and** capture the RED/GREEN
      transcripts (see below). — DATA-02
- [ ] Regenerate `tests/golden/v1.3-COVERAGE-MATRIX.md` (**297** ` us` value cells change; the 6
      `pulse_bucket` label lines do **not**) — **always with
      explicit scratch `--output` / `--ledger`.** — DATA-03

*No framework install needed — pytest, syrupy and ruff are all present and green.*

---

## Seen-to-Fail Transcripts (D-13) — mandatory, not optional

> A golden regenerated without a fail proof is indistinguishable from a golden silenced. Precedent:
> Phase 140 Plan 03 shipped four RED / one GREEN for this same gate
> (`.planning/phases/140-parameter-table/140-03-SUMMARY.md` §"Planted Violations", Runs A–E).

**Seam mechanics (getting this wrong makes the RED leg unreachable, which proves nothing):**
`_DB_PATH` and `_GEN_PATH` in `tests/test_chip_database_field_inventory.py` resolve from
`os.environ` **at import**, so a planted violation must run in a **child process** — never
`monkeypatch`. `_EXTRA_CHIPS_PATH` is deliberately **not** overridable, by design.

Required legs, each `mktemp -d` outside both repos, `rm -rf`'d after, with `git diff --quiet`
confirmed before, between and after every run:

| Leg | Plant | Expected |
|---|---|---|
| A | New field on one chip | RED — test 2, `added={'foo':1}` |
| B | Delete a chip (count change, **no** new name) | RED — tests 1/2/3/5, proving counts-not-names |
| C | Vacuous `{}` target | RED — test 5 non-vacuity; never a silent pass |
| D | New key in the **generator only**, via `FIRESTARTER_BUILD_DB_SOURCE` | RED — test 6, `added=['foo']` |
| **E** | **New key inside an `extra_chips.json` record** — *Phase-148-specific, exercises the union path F-1 makes load-bearing* | RED — test 6 |
| F | Clean | GREEN — exit 0, 8 passed |

**The D-11 RED/GREEN transcript is free** and must also be captured: run the migration with the
canonicalizer and renames only → **exit 1, 56 `UNEXPLAINED`**; add `RULE_VCC_MARGIN_RAIL` →
**exit 0, 56 in their own bucket**.

---

## Gate Traps (measured — each has burned this repo before)

| # | Trap | Consequence |
|---|---|---|
| 1 | `tools/` is linted by **nothing** | A ruff-clean run says nothing about `build_db.py` / `diff_db.py` / `audit_coverage_matrix.py` |
| 2 | The mypy gate **cannot be run locally** (devcontainer is py3.12; CI pins 3.11) | A local mypy pass is not evidence — never make a task's verify depend on it |
| 3 | `audit_coverage_matrix.py` writes into the **meta repo** by default (`_REPO_ROOT` → `/workspaces`) and **mutates the tracked ledger**, minting `DEFECT-COV-NN` IDs | Always pass explicit scratch `--output` / `--ledger` |
| 4 | `--check`'s contract is relative to a **freshly generated** ledger | An empty ledger must exit 1; the full ledger, 0 |
| 5 | `test_flash_path_record_sync.py` asserts **whole-repo porcelain** — and it lives in the **firmware** repo, not this one | Commit before running the full suite, or it goes RED on any mid-change diff |
| 6 | `check_dispatch.py` reads the user override | `~/.firestarter/database.json` can perturb the gate — use `FIRESTARTER_CONFIG_DIR` |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

**All phase behaviors have automated verification.** This is a host-only, data-and-decode phase;
the **Evidence Ceiling** (PROJECT.md §v1.32) binds it — no criterion may require real silicon, and
no AT28C part exists in operator inventory. Nothing here is bench-verifiable and nothing here
claims to be.

---

## Validation Sign-Off

Ticked against the **planned** artifact set (8 plans / 22 tasks) on 2026-08-19. Boxes that
execution has to earn are deliberately left open — `wave_0_complete` stays `false` until Wave 0
actually runs.

- [x] All tasks have `<automated>` verify or a Wave 0 dependency — measured **22/22** tasks carry
      exactly one `<automated>` block (01: 3, 02: 2, 03: 3, 04: 3, 05: 3, 06: 3, 07: 2, 08: 3)
- [x] Sampling continuity: no 3 consecutive tasks without an automated verify — vacuously held,
      since no task lacks one
- [x] Wave 0 covers all ❌ MISSING references above — all **ten** ❌ W0 rows are assigned to a task
- [x] The wire-dict capture is task 1, before any edit — Plan 01 (`wave: 1`, `depends_on: []`)
      Task 1 *"Capture the 746-chip pre-change wire-dict golden"*, whose own verify asserts
      `git status --porcelain tools firestarter` is clean, i.e. that it edited nothing
- [x] Both RED/GREEN transcript sets are assigned to explicit tasks — D-13 golden legs A–F in
      Plan 07 Task 2; D-11 diff rule RED in Plan 06 Task 1 and GREEN in Plan 06 Task 2.
      *Capturing and committing them is earned at execution, not here.*
- [x] No watch-mode flags; every pytest command carries `-o addopts=""` — verified by scanning all
      8 plan files: zero `--watch` / `--looponfail`, zero bare `pytest` invocations
- [x] Feedback latency within the measured budget above — < 0.3 s for every unit/gate suite;
      the two `test_characterization.py` tasks are the outlier at 16.7 s, which is measured and
      accepted (35 subprocess CLI snapshots), not assumed to be under 5 s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-08-19 (planning)

> Scope of this approval: the plan set's *verification design*. It does not assert that any gate is
> green — no Phase 148 code has been written. Every count assertion in every `<automated>` block was
> re-run against the live tree at `/workspaces/firestarter_app` on 2026-08-19 to confirm the
> asserted number is reachable given what that task's own action changes.
