# Phase 188: The Tools Directory - Research

**Researched:** 2026-09-12
**Domain:** Multi-repo deletion / dangling-reference safety (Python host repo, Arduino firmware repo, GSD meta repo)
**Confidence:** HIGH on the inventory, the reference sweep and the acceptance-gate arithmetic (all measured live this session); MEDIUM on the citation-sweep scope (a judgement boundary, not a measurement); LOW on nothing material.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `188-CONTEXT.md` §Implementation Decisions. **Do not re-litigate any of these.**

- **D-01:** All ten `check_*.py` gates are deleted, **no exceptions**, together with their test files. The operator was offered "retire unless load-bearing" and chose "retire the whole family, no exceptions" after being shown that `check_mypy_watermark.py` is the CI-named type-error floor and that `check_no_exists_proxy.py` was extended eight days ago by quick-260912-mo6. The gates to delete, by name: `check_devtest_orchestrator.py`, `check_diagnostic_report_claims.py`, `check_dispatch.py`, `check_is_memory_cmd_no_ifdef.py`, `check_mypy_watermark.py`, `check_no_community_support_status_write.py`, `check_no_exists_proxy.py`, `check_no_log_in_sdp_window.py`, `check_protection_readability_invariants.py`, `check_sdp_capability_invariants.py`. — **Reversibility:** costly.
- **D-02:** **mypy leaves CI entirely.** `ci.yml`'s `mypy type check (watermark gate)` step is deleted with the script it invokes, and nothing replaces it — not a plain `mypy` step, not an inline count.
- **D-03:** Three test-file naming conventions are in play and the planner must not assume `test_<tool>.py`. Measured: seven gates have `tests/test_<gate>.py`; the other three are `tests/test_check_dispatch_invariants.py`, `tests/test_check_protection_readability.py`, `tests/test_check_sdp_capability.py`.
- **D-04:** All six go: `audit_coverage_matrix.py`, `diff_db.py`, `measure_plan_shapes.py`, `measure_part_number_delta.py`, `snapshot_report_shapes.py`, `build_devtest_issue_corpus.py`, with their tests.
- **D-05:** **`diff_db.py` is not simply deleted — it relocates** to `.claude/skills/devtest-rootcause/scripts/`, and the skill's `check_dispatch.py` references are dropped. **The copy must land before the tool is deleted** — see D-21.
- **D-06:** Deleting `audit_coverage_matrix.py` dissolves **TOOLS-01 and TOOLS-07 outright**.
- **D-07:** `ci_parity.sh` (162 lines) and `ci_replica_venv.sh` (363 lines) are both deleted.
- **D-08:** The whole frame-vector apparatus goes: generator, catalog, both generated artifacts, and **both consuming tests**, on both sides. — **Reversibility: one-way in effect** — this removes the only mechanism proving host and firmware agree on the same wire bytes. **The operator was shown this cost explicitly and chose it anyway. Do not re-litigate it, and do not quietly preserve a fragment of it.**
- **D-09:** Both `codegen_vectors` CI steps are deleted — `Vector catalog validity check` and `Codegen drift gate (frame_vectors.py)`.
- **D-10:** **`catalog/codegen.py` and `build_db.py` stay.** The `Catalog validity check` and `Codegen drift gate (messages.py)` CI steps are untouched.
- **D-11:** **TOOLS-06 dissolves.** The sync script's `FILES` array is **not modified** by this phase.
- **D-12:** **TOOLS-02 is retired: no consumer declarations, and no check asserting them.** Recorded as a disclosed, accepted cost.
- **D-13:** `tests/scan_paths.py` and `tests/test_scan_paths_resolve.py` are **deleted entirely**, both populations. The pair goes RED the moment the first tool is deleted; that RED is expected. Delete the pair in the **same commit or wave** as the tools they index.
- **D-14:** `firestarter_app/tools/` ends at exactly **six scripts**: `build_db.py`, `catalog/codegen.py`, `gen_sdp_bus_config.py`, `gen_validation_header.py`, `parse_devtest_issue.py`, `gen_test_image.py`. Non-script files (`DECODE-NOTES.md`, `extra_chips.json`, `validation_matrix_spec.json`, `variant-decode-diff.txt`, `pin-layouts.odt`, `baseline/`) are **out of scope**.
- **D-15:** `derive_sdp_partition.py` is **deleted**. Disclosed, accepted.
- **D-16:** The citation sweep applies to the **six survivors only**.
- **D-17:** **`catalog/codegen.py` must be stripped at the META canonical copy, not in the sub-repo.** Strip at `/workspaces/tools/catalog/codegen.py`, then run `tools/catalog/sync_to_subrepos.sh`; `messages.h` and `messages.py` must be verified byte-unchanged.
- **D-18:** This is an *editing* task, not a regex task. Three automated passes were attempted and all three were reverted for collateral damage. Do it by hand with `ruff format --check` and the suite after each batch. Keep comments that explain the *code*; delete only process provenance.
- **D-19:** **Acceptance proof is the executable gates only — no ritual.** App: `ruff check firestarter/ tests/`, `ruff format --check firestarter/ tests/`, `pytest tests/ --cov=firestarter --cov-fail-under=70`, and the `firestarter --help` smoke test. Firmware: `pio test -e native` and `pio test -e native_nodevtools` green, and `python scripts/check_size_baseline.py` exit 0. A plain grep for dangling references is run **as part of the work**, not staged as a committed evidence artifact. **Not** a full cold three-target AVR rebuild with twelve-figure transcription, unless D-20's check says the AVR figures actually moved.
- **D-20:** **The size-baseline re-record is native-only, pending one verification.** If the AVR figures hold, move only the native `cases`/`suites` pair and leave the twelve AVR figures untouched. `size_baseline_base01.json` is **not** re-anchored either way.
- **D-21:** **Ordering — meta first, then host and firmware in parallel.** Wave 1 meta alone (`diff_db.py` copy + skill reference drop). Waves 2/3 host ∥ firmware. Two hard intra-wave constraints: (a) `ci.yml`'s mypy and vector steps are deleted in the *same commit* as the tools they invoke; (b) the firmware suite deletion and the baseline re-record are **one cold capture**, not two. `catalog/codegen.py`'s meta-side strip plus its sync is best landed as its own commit after waves 2 and 3.
- **D-22:** **The ledger is amended in-phase, and RETIRED is not Complete.** Expected end state: TOOLS-01, -02, -04, -06, -07 → RETIRED; TOOLS-03 → satisfied by family retirement; TOOLS-05 → Complete. **ROADMAP.md edits are hand-authored.** Do not run `roadmap.update-plan-progress` against this phase.
- **D-23:** One verdict document at `.planning/notes/host-tools-retirement.md`, on the shape of `.planning/notes/catalog-sync-check-retirement.md`. **No successor guard is authored**, and no new `check_*.py` or CI gate is created by this phase for any reason.
- **D-24:** Branch model per standing policy: a `v1.37`-slug branch forked off `beta` in **all three** repositories including meta. Never work directly on `beta` or `main`.

### Claude's Discretion

- Wave-to-plan decomposition and commit boundaries, subject to D-21's three named constraints.
- Whether the ten gate deletions land as one commit or several, and how their tests are batched with them.
- The verdict note's internal structure and prose.
- Which planted-violation fixtures under `tests/fixtures/` go with their gates and which are shared — read each before deleting; a fixture with a surviving consumer stays. **(Answered by measurement in §Fixture Ownership below.)**
- Exact wording of the six survivors' docstrings after the D-16 sweep, subject to D-18.

### Deferred Ideas (OUT OF SCOPE)

- A consumer-declaration convention for the six survivors. Retired by D-12, not refuted.
- Re-guarding the firmware-rename masking defect. D-13 deletes its only named guard.
- A replacement for the cross-repo wire-contract proof. D-08 removes it deliberately.
- The `firestarter_app/tests/` provenance sweep (~1,774 hits). Explicitly out of scope.
- A mypy floor in any form. D-02 removes it with no replacement.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (from REQUIREMENTS.md §TOOLS, lines 202-232) | Research Support |
|----|-------------|------------------|
| TOOLS-01 | `audit_coverage_matrix.py` refuses a default output path outside a checkout that is demonstrably this project | **DISSOLVED by D-06.** §Deletion Inventory row 21 confirms `firestarter_app/tools/audit_coverage_matrix.py` (1,952 lines) exists and is deletable; §Dangling References names its two remaining non-test consumers (`pyproject.toml:112-113`, `tests/test_numeric_schema_source_scan.py:72`) that must be edited in the same commit. Mark **RETIRED — dissolved by tool deletion (D-04/D-06)**. |
| TOOLS-02 | Every script in `firestarter_app/tools/` declares its consumer; a fail-closed check asserts the declaration | **RETIRED by D-12.** No research work; §Assumptions Log A-2 records the accepted blind spot. Mark **RETIRED — declaration layer and its check both dropped on operator decision (D-12)**. |
| TOOLS-03 | Each of the ten `check_*.py` gates is decided by name | **Satisfied by D-01.** §Deletion Inventory rows 1-20 name all ten gates and all ten test files with live line counts, resolving D-03's three-convention hazard exhaustively. §Dangling References is the evidence that "decided by name" is not the whole job — four of the ten export symbols that eight *surviving* test modules import. |
| TOOLS-04 | Each GSD-process tool is placed by name | **Satisfied by D-04/D-05.** §Deletion Inventory rows 21-31 place all six; §The `diff_db.py` Relocation gives the measured mechanism (`FIRESTARTER_DB_FILE` / `FIRESTARTER_BASELINE_FILE` env seams at `diff_db.py:33-40`) that makes D-05's relocation actually run. |
| TOOLS-05 | No file under `firestarter_app/tools/` cites a phase number, plan number, decision ID, or `.planning/` path | **THE ONLY REQUIREMENT STILL DOING WORK.** §The Six Survivors' Citations gives every hit by line with its text and a keep-vs-delete classification. §Pitfall 6 documents the measured divergence between CONTEXT.md's counts and the live tree. |
| TOOLS-06 | `frame-vectors.toml` and `codegen_vectors.py` covered by the meta-canonical sync | **DISSOLVED by D-11.** §Deletion Inventory rows 35-36 and 41-42 confirm all four files exist and carry no meta copy; §Catalog Strip confirms `sync_to_subrepos.sh:25` `FILES=(messages.toml codegen.py)` is unchanged. Mark **RETIRED — both files deleted (D-08), so there is nothing left to sync (D-11)**. |
| TOOLS-07 | `audit_coverage_matrix.py --check` exits 0, or the staleness is recorded | **DISSOLVED by D-06.** Mark **RETIRED — dissolved by tool deletion (D-04/D-06)**. |

</phase_requirements>

---

## Summary

Every one of the 46 file paths the CONTEXT.md decisions delete **exists in the live tree today** and was verified this session by path, with line counts (§Deletion Inventory). The measured host-side deletion mass is **15,362 lines**, not CONTEXT.md's 15,589 — the discrepancy is exactly 227 lines and is explained: CONTEXT.md's "their test files — 1,625" double-counted `tests/test_devtest_issue_corpus.py` (227 lines), a file its own `code_context` section correctly says *survives*. The firmware side measures **1,142 lines** exactly as stated. Grand total to delete: **16,504 lines**.

**The single dominant risk in this phase is not the deletion — it is the repair.** Four of the ten `check_*.py` gates and one of the six process tools are not only gates; they also export library symbols that **eight surviving test modules import**. Measured live: deleting the named set without repair produces **45 collection errors** (seven whole test modules fail to import) plus **48 runtime failures**, for **93 broken surviving tests**. CONTEXT.md's `code_context` explicitly states that `test_blast_radius_invariance.py` "reads committed artifacts and does not invoke their generators — they survive D-04 untouched." **That statement is refuted by live measurement**: the module does `from tools.snapshot_report_shapes import render_shape` at two parametrized sites (`:758`, `:820`), each swept over 19 shape ids — **38 of its 106 tests break**. None of these repairs is named anywhere in CONTEXT.md, and the biggest one (`check_dispatch.dispatch()`, a host-side model of the firmware dispatch order consumed by six `test_val_wire_*` modules plus `test_decoder` and `test_build_db_inclusion`) cannot be resolved by the decisions as written — it needs an operator checkpoint (§Open Questions Q1).

Three CI edits CONTEXT.md does not name were found. D-09 names two `codegen_vectors` steps in the host `ci.yml`; the firmware repo carries **two more pairs** — `build.yml:122-131` and `beta-build.yml:107-116` — and deleting `codegen_vectors.py` without deleting those four steps reddens firmware CI on every branch and on every beta push. The host `beta-release.yml` was checked and is clean (it runs `codegen.py` only).

Three D-19/D-20 acceptance claims were falsified or refined by running them. `python scripts/check_size_baseline.py` **with no arguments exits 1** by design (never-vacuous guard) — the gate as worded in D-19 is un-runnable and needs `--native-log ENV=PATH` pairs. D-20's premise that `frame_vectors.h` is unreachable from `src/` is **VERIFIED** (`git grep frame_vectors -- src/` returns nothing; a cold `rm -rf .pio/build/uno && pio run -e uno` reproduces the pinned `flash_used: 22734` exactly), so the twelve AVR figures do not move. But re-recording the native pair 185/17 → 179/16 **reddens `firestarter/tests/test_check_size_baseline.py::test_clean_native_both_envs_pass`**, proven by running the checker against a 179/16 baseline and the committed fixtures; both `captured_test_native*.log` fixtures must be re-captured in the same commit. Finally, the coverage question is closed: the whole deletion moves `--cov=firestarter` from **85% to 85%** against a 70% floor — measured by two full suite runs.

**Primary recommendation:** Plan this as **deletion + repair**, not deletion. Front-load a plan (or a checkpoint) that resolves the four orphaned library symbols before any gate file is removed, because seven test modules stop *collecting* — not merely failing — the instant `check_dispatch.py` and `check_devtest_orchestrator.py` disappear, and a suite that cannot collect gives no signal about anything else the phase did.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Retiring the ten AST gates + tests | Host repo (`firestarter_app`) | — | The whole `check_*` family lives only there; `firestarter/tools/` has no checker family [VERIFIED: `firestarter_app/tools/` listing, this session]. |
| Repairing orphaned library imports | Host repo test tier (`firestarter_app/tests/`) | — | The eight consuming modules are all under `tests/`; the symbols they need are decode models, not product code. |
| Deleting the mypy CI leg | Host repo CI (`.github/workflows/ci.yml`) | — | `check_mypy_watermark.py` is named at exactly one CI site (`ci.yml:87`). |
| Deleting the frame-vector generator + catalog | Host repo **and** firmware repo, symmetrically | Meta repo (none — no canonical copy exists) | Both sub-repos carry independent copies; neither is synced [VERIFIED: `ls /workspaces/tools/catalog/` → `codegen.py`, `messages.toml`, `sync_to_subrepos.sh` only]. |
| Deleting the frame-vector CI gates | Firmware CI (`build.yml`, `beta-build.yml`) **and** host CI (`ci.yml`) | — | Four firmware steps + two host steps. D-09 names only the host pair. |
| Re-recording the native size baseline | Firmware repo (`scripts/baseline/`) | Firmware python test tier (`tests/fixtures/`) | The JSON pin and its two fixture logs move together or the suite reddens. |
| Relocating `diff_db.py` | Meta repo (`.claude/skills/devtest-rootcause/scripts/`) | Host repo (data stays put) | The skill owns its script; the 476 KB baseline it reads stays in `firestarter_app/tools/baseline/` (D-14 out of scope), so the copy must be driven by env seams. |
| Stripping `codegen.py` citations | Meta repo (`/workspaces/tools/catalog/codegen.py`) | Both sub-repos (receive the sync) | Editing a sub-repo copy is reverted by the next sync (D-17). |
| Amending the requirement/criteria ledger | Meta repo (`.planning/`) | — | Hand-authored only (D-22). |

---

## Deletion Inventory — all 46 paths, verified live

**Every path below was confirmed to exist on 2026-09-12** by `[ -f "$p" ]` over the full list, with `wc -l`. [VERIFIED: filesystem probe, this session — all 46 returned `OK`, zero `MISS`.]

### Host repo — the ten `check_*.py` gates and their tests (D-01, D-03)

| # | Gate path | Lines | Test path | Lines |
|---|---|---|---|---|
| 1 | `firestarter_app/tools/check_devtest_orchestrator.py` | 666 | `tests/test_check_devtest_orchestrator.py` | 995 |
| 2 | `firestarter_app/tools/check_diagnostic_report_claims.py` | 269 | `tests/test_check_diagnostic_report_claims.py` | 119 |
| 3 | `firestarter_app/tools/check_dispatch.py` | 510 | **`tests/test_check_dispatch_invariants.py`** | 250 |
| 4 | `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` | 340 | `tests/test_check_is_memory_cmd_no_ifdef.py` | 362 |
| 5 | `firestarter_app/tools/check_mypy_watermark.py` | 238 | `tests/test_check_mypy_watermark.py` | 367 |
| 6 | `firestarter_app/tools/check_no_community_support_status_write.py` | 261 | `tests/test_check_no_community_support_status_write.py` | 232 |
| 7 | `firestarter_app/tools/check_no_exists_proxy.py` | 375 | `tests/test_check_no_exists_proxy.py` | 237 |
| 8 | `firestarter_app/tools/check_no_log_in_sdp_window.py` | 438 | `tests/test_check_no_log_in_sdp_window.py` | 333 |
| 9 | `firestarter_app/tools/check_protection_readability_invariants.py` | 524 | **`tests/test_check_protection_readability.py`** | 394 |
| 10 | `firestarter_app/tools/check_sdp_capability_invariants.py` | 364 | **`tests/test_check_sdp_capability.py`** | 248 |

**Gates: 3,985 lines** (matches CONTEXT.md exactly). **Tests: 3,537 lines** (matches exactly). **D-03's 7+3 split is confirmed** — the three bolded test names are the non-obvious ones. **No fourth naming convention exists**; every one of the ten has exactly one test file and the mapping is complete.

### Host repo — the six process tools and their tests (D-04)

| # | Tool path | Lines | Test path(s) | Lines |
|---|---|---|---|---|
| 21 | `firestarter_app/tools/audit_coverage_matrix.py` | 1,952 | `tests/test_audit_coverage_matrix.py` (646) **+ `tests/test_audit_coverage_matrix_default_paths.py` (147)** | 793 |
| 22 | `firestarter_app/tools/diff_db.py` | 984 | **`tests/test_diff_db_gate.py`** — *not named in CONTEXT.md* | 234 |
| 23 | `firestarter_app/tools/measure_plan_shapes.py` | 370 | `tests/test_plan_shapes_drift.py` | 201 |
| 24 | `firestarter_app/tools/measure_part_number_delta.py` | 303 | `tests/test_part_number_delta_drift.py` | 170 |
| 25 | `firestarter_app/tools/snapshot_report_shapes.py` | 190 | *(none of its own — but see §Dangling References; `test_blast_radius_invariance.py` imports it)* | — |
| 26 | `firestarter_app/tools/build_devtest_issue_corpus.py` | 345 | *(none of its own — `tests/test_devtest_issue_corpus.py` reads the committed artifact and **SURVIVES**)* | — |

**Tools: 4,144 lines** (matches CONTEXT.md exactly). **Tests: 1,398 lines, not 1,625** — see §Pitfall 5.

> **Flagged, not named by any decision:** `tests/test_diff_db_gate.py` (234 lines). CONTEXT.md's D-04 says "with their tests" but never names this file. It is `diff_db.py`'s only test, it invokes the tool, and it must be deleted with it. It is also named in a surviving census list at `tests/test_voltage_field_census.py:53` — see §Dangling References.

### Host repo — the two CI mirrors (D-07), the orphan (D-15), the frame-vector half (D-08), the scan-path pair (D-13)

| # | Path | Lines | Note |
|---|---|---|---|
| 32 | `firestarter_app/tools/ci_parity.sh` | 162 | Zero external references [VERIFIED: `git grep ci_parity` across all three repos, excluding `.planning/` and self, returns nothing] |
| 33 | `firestarter_app/tools/ci_replica_venv.sh` | 363 | Zero external references, same probe |
| 34 | `firestarter_app/tools/derive_sdp_partition.py` | 263 | **Zero references anywhere in any of the three repos** outside `.planning/` and itself [VERIFIED: same probe] |
| 35 | `firestarter_app/tools/catalog/codegen_vectors.py` | 418 | sha256 `93f8db1112fd28c9…` |
| 36 | `firestarter_app/tools/catalog/frame-vectors.toml` | 120 | sha256 `c93b8f7c32ad57be…` (identical to firmware copy) |
| 37 | `firestarter_app/firestarter/frame_vectors.py` | 129 | **Ships in the wheel** via `pyproject.toml:92` `packages = ["firestarter"]`; coverage shows it at **7 statements, 100% covered** |
| 38 | `firestarter_app/tests/test_frame_vectors.py` | 282 | |
| 39 | `firestarter_app/tests/scan_paths.py` | 354 | Imported by exactly one module — `test_scan_paths_resolve.py:39`. The pair is self-contained. |
| 40 | `firestarter_app/tests/test_scan_paths_resolve.py` | 207 | |

**Host subtotal: 15,362 lines.**

### Firmware repo — the frame-vector half (D-08)

| # | Path | Lines |
|---|---|---|
| 41 | `firestarter/tools/catalog/codegen_vectors.py` | 418 |
| 42 | `firestarter/tools/catalog/frame-vectors.toml` | 120 |
| 43 | `firestarter/include/frame_vectors.h` | 57 |
| 44 | `firestarter/test/native/avr/test_frame_vectors/host_stubs.cpp` | 29 |
| 45 | `firestarter/test/native/avr/test_frame_vectors/serial_read_mock.h` | 119 |
| 46 | `firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp` | 399 |

**Firmware subtotal: 1,142 lines** — matches CONTEXT.md exactly. The `test_frame_vectors/` directory holds exactly these three files; deleting the directory is complete. **The codegen drift confirmed:** the two `codegen_vectors.py` copies differ (`93f8db11…` host vs `3ffef0c4…` firmware); `frame-vectors.toml` is byte-identical across both; neither has a meta copy.

**Grand total: 16,504 lines across 46 files.**

### Files the decisions plainly intend but do not name

| Path | Why it is in scope | Disposition |
|---|---|---|
| `firestarter_app/tests/test_diff_db_gate.py` (234 lines) | `diff_db.py`'s only test; invokes the tool | **Delete with row 22** |
| `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md` (186 KB) | Its **only** consumer is `test_audit_coverage_matrix.py:581` (`test_golden_file_matches`), deleted by D-04 | **Orphaned.** Recommend delete; if kept, note that `pyproject.toml:110-119`'s `extend-exclude = ["tests/golden", ...]` justification (1) — which names `audit_coverage_matrix.py` and `test_audit_coverage_matrix.py` by name — becomes false either way |
| `firestarter_app/tools/baseline/dispatch_baseline.json` (158 KB) | **Zero consumers anywhere** [VERIFIED: `git grep -ln dispatch_baseline` returns nothing]; it was `check_dispatch.py`'s data | Out of scope per D-14 (non-script). Flag in the verdict note as newly-orphaned data. |
| `firestarter_app/tools/__pycache__/`, `tools/catalog/__pycache__/` | Untracked (D-14) | No action |

---

## Dangling-Reference Sweep — the real risk

All sweeps below use `git grep` (not the devcontainer's ugrep-backed `grep`, which honors `.gitignore` and silently under-scans). [VERIFIED: commands and output captured this session.]

### A. Surviving test modules that IMPORT a deleted tool — 93 tests break

This is the finding CONTEXT.md does not carry. Five deleted files export symbols that surviving tests consume.

#### A1 — Collection-time breakage: 45 tests in 7 modules fail to *import*

A module-level import of a deleted module is a **collection error**, not a test failure. pytest reports `ERROR`, the module contributes zero results, and the whole run's signal degrades.

| Surviving module | Import site | Symbol | Tests lost |
|---|---|---|---|
| `tests/test_val_wire_5v_page.py` | `:34` `from check_dispatch import dispatch` | `dispatch` | 14 |
| `tests/test_val_wire_sram.py` | `:33` `from check_dispatch import _SRAM_PROTOCOLS, dispatch` | `_SRAM_PROTOCOLS`, `dispatch` | 6 |
| `tests/test_val_wire_eeprom28c.py` | `:37` `from check_dispatch import dispatch` | `dispatch` | 6 |
| `tests/test_val_wire_eprom.py` | `:31` `from check_dispatch import dispatch` | `dispatch` | 4 |
| `tests/test_val_wire_flash_intel.py` | `:27` `from check_dispatch import dispatch` | `dispatch` | 4 |
| `tests/test_val_wire_nor_unlock.py` | `:27` `from check_dispatch import dispatch` | `dispatch` | 4 |
| `tests/test_op_registration_parity.py` | `:113` `import tools.check_devtest_orchestrator as check_devtest_orchestrator_mod` | `_HANDLER_FUNCTION_NAMES` (used at `:365`) | 7 |
| | | **Subtotal** | **45** |

The six `test_val_wire_*` modules each prepend `tools/` to `sys.path` first (`_TOOLS_DIR = Path(__file__).parent.parent / "tools"`), so the import is a bare `from check_dispatch import ...`, not a `tools.`-qualified one — a naive grep for `tools.check_dispatch` misses all six.

#### A2 — Runtime breakage: 48 tests in 6 modules

| Surviving module | Site | Mechanism | Tests lost |
|---|---|---|---|
| `tests/test_blast_radius_invariance.py` | `:758`, `:820` | `from tools.snapshot_report_shapes import render_shape`, two `@pytest.mark.parametrize` sweeps over 19 `SHAPE_IDS` | **38** |
| `tests/test_decoder.py` | `:703, :713, :723, :733, :743` | in-function `from check_dispatch import dispatch` (class `TestDispatchGate02`) | 5 |
| `tests/test_lock_status_class_partition.py` | `:598` via `_run_protection_readability_checker`, called at `:618` and `:640` | `subprocess.run([sys.executable, "tools/check_protection_readability_invariants.py"], …)` | 2 |
| `tests/test_build_db_inclusion.py` | `:729` | `from check_dispatch import _ALGO_MEM_TYPE, dispatch` | 1 |
| `tests/test_parse_devtest_issue.py` | `:740` | `from tools.check_diagnostic_report_claims import FORBIDDEN_PATTERNS` | 1 |
| `tests/test_numeric_schema_source_scan.py` | `:72` `_AUDIT_COVERAGE_MATRIX_PY = _APP_ROOT / "tools" / "audit_coverage_matrix.py"`; read at `:173` | `.read_text()` on a deleted file → `FileNotFoundError` | 1 |
| | | **Subtotal** | **48** |

**Total surviving tests broken by the deletion set: 93.** Each must be repaired in the same commit as the deletion, or the suite gives no signal.

> **On `test_blast_radius_invariance.py` specifically:** CONTEXT.md `code_context` states it "read committed artifacts and do not invoke their generators — they survive D-04 untouched." **Live value contradicts this.** `:751` is `test_committed_snapshot_matches_a_fresh_regeneration`, whose own docstring says *"snapshot_report_shapes.py --check did catch it, but nothing in the suite or in CI invoked that script"* — and the test's remedy was to invoke `render_shape` in-process. It genuinely regenerates. **This affects D-04's blast radius, not D-04 itself.**

### B. Prose / comment references that die with their target (edit, but nothing breaks)

| Path | Lines | What it says |
|---|---|---|
| `firestarter_app/CLAUDE.md` | `:122-128` | *"Regression guard: `tools/check_dispatch.py` asserts (a) … (b) …"* — a whole paragraph telling future agents a guard exists. **Becomes false; must be edited.** |
| `firestarter_app/pyproject.toml` | `:74-78`, `:110-119`, `:146`, `:154`, `:195` | Five comment blocks naming `check_mypy_watermark.py`, `audit_coverage_matrix.py`, `check_diagnostic_report_claims.py`. Not under `tools/`, so **out of TOOLS-05 scope**, but all become stale. `:74` is load-bearing prose for a live `mypy<3` version pin. |
| `firestarter_app/tests/` (≈20 modules) | various | Docstring/comment mentions of gate names in surviving tests (`test_sdp_honesty.py:13`, `test_sdp_db_invariant.py:165,213`, `test_parse_gate_admission.py:22-23`, `test_fw_presence.py:52`, `tests/fw_presence.py:125`, `test_extra_chips_supplement.py:26,187,190`, `test_sdp_table_parity.py:84`, `test_voltage_field_census.py:7,48,53`, `test_chip_test_sdp_leg.py:1492`, `test_vcc_margin_rail.py:62,79`, `test_wire_dict_equivalence.py:154`, `test_skip_census.py:133`, `test_gen_validation_header.py:30`, `test_sdp_bus_config_drift.py:30`, `tests/golden/chip_database_field_inventory.json:10`). **Out of TOOLS-05 scope** (the `tests/` sweep is a deferred idea) and none breaks. Leave them; do not open the tests sweep by the back door. |
| `firestarter/test/native/avr/_shared/host_stubs_common.inc` | `:54` | Names `test_frame_vectors` in a comment about a flag. **Compile-inert** — verified it is a comment, not an `#include`. |
| `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` | `:576` | Prose list including `test_frame_vectors`. Inert. |

### C. CI / workflow references — six steps across three workflow files

See §The CI Workflow Edits for exact line ranges. **The two firmware pairs are not named in CONTEXT.md.**

### D. `tests/scan_paths.py`'s resolver table

The table indexes **11 tools** by name: `check_dispatch.py` (`:158`), `build_db.py` (`:165`), `gen_validation_header.py` (`:171`), `check_no_log_in_sdp_window.py` (`:179`), `check_no_community_support_status_write.py` (`:186`), `check_devtest_orchestrator.py` (`:197`), `check_is_memory_cmd_no_ifdef.py` (`:207`), `check_sdp_capability_invariants.py` (`:214`), `diff_db.py` (`:221`), `gen_sdp_bus_config.py` (`:227`), `audit_coverage_matrix.py` (`:239`). Eight are deleted, three survive. D-13 deletes the whole module and its only importer, so **no partial edit is needed** — this is the cleanest deletion in the phase.

### E. Things that are clean

- `firestarter_app/tests/conftest.py` (349 lines): **no reference to any deleted tool** [VERIFIED: grep for `tools|check_|scan_paths|frame_vect` returns only `:290`, an unrelated mypy-prose mention of `check_untyped_defs`]. No conftest edit needed.
- `firestarter_app/firestarter_test.sh`, `write_test.sh`, `write_test_port.sh`: no `tools/` references.
- `firestarter_app/.github/workflows/beta-release.yml`: runs `codegen.py` only (`:58`, `:67-68`) — **no `codegen_vectors` steps, no edit needed.**
- `firestarter_app/.github/workflows/release.yml:14`: `'tools/**'` is a `paths-ignore` glob — unaffected.
- `firestarter/scripts/check_cmake_manifest.py`: scoped to `platform/py32f071/CMakeLists.txt` only (`:135`), **not** to `test/native/avr/`. Deleting the suite cannot trip the manifest gate.
- No `Makefile` exists in either sub-repo.
- `firestarter_app/tools/` has no `__init__.py`; `import tools.X` works via implicit namespace packages with rootdir on `sys.path`. Deleting files does not break that mechanism for survivors.

---

## Fixture Ownership (Claude's Discretion — answered by measurement)

Every `tests/fixtures/` entry plausibly in scope was mapped to its consumers with `git grep -ln` over `tests/ tools/ .github/ pyproject.toml`. [VERIFIED: this session.]

### DELETE — sole consumers are deleted gates/tools

| Fixture | Only consumers |
|---|---|
| `planted_diagnostic_report_claim.py` | `tests/test_check_diagnostic_report_claims.py` (deleted) |
| `planted_ifdef_in_predicate.h` | `tests/test_check_is_memory_cmd_no_ifdef.py` + `tools/check_is_memory_cmd_no_ifdef.py` (both deleted) |
| `planted_log_in_window.cpp` | `tests/test_check_no_log_in_sdp_window.py` + its gate (both deleted) |
| `planted_no_exists_proxy.py` | `tests/test_check_no_exists_proxy.py` + its gate (both deleted) |
| `planted_permit_by_default.py` | `tests/test_check_sdp_capability.py` + its gate (both deleted). The extra hit at `tests/fixtures/synthetic_nonzero_chip_id.py:11` is a **docstring mention**, not a load. |
| `planted_widenable_allowset.py` | `tests/test_check_sdp_capability.py` + its gate. The extra hit at `tests/test_sdp_db_invariant.py:214` is a **comment**, not a load. |
| `planted_protection_widenable_tokenset.py` | `tests/test_check_protection_readability.py` + its gate (both deleted) |
| `plan_shapes.json` | `tests/test_plan_shapes_drift.py` + `tools/measure_plan_shapes.py` (both deleted) |

### KEEP — a surviving test loads it

| Fixture | Surviving consumer | Evidence |
|---|---|---|
| **`part_number_delta.json`** | `tests/test_canonical_part_number.py` | `:40` `_DELTA_PATH = Path(__file__).parent / "fixtures" / "part_number_delta.json"` — a **real load**, not a mention. Its generator `measure_part_number_delta.py` dies; the fixture stays as a frozen artifact. |
| **`planted_protection_permit_by_default.py`** | `tests/test_lock_status_class_partition.py` | `:618` routes it through `FIRESTARTER_PROTECTION_READABILITY_SRC` into the gate. **Note:** this consumer is itself broken by A2 — the fixture survives only if that test is repaired. |
| `planted_unparsable.py` | `pyproject.toml:141-155` (mypy `exclude` rationale) | The fixture's *test* (`test_check_diagnostic_report_claims.py`) dies, but `tests/fixtures/` stays mypy-excluded for other reasons. Keeping it is harmless; deleting it makes `pyproject.toml:146`'s comment false. **Recommend keep.** |
| `devtest_issue_corpus.json` | `tests/test_devtest_issue_corpus.py` (survives) | Reads the committed artifact; does not invoke its generator. |
| `report_shapes.py`, `reports/*.json` (19), `shape_ids.json` | `tests/test_blast_radius_invariance.py`, `tests/test_derive_plan_structural_sentinel.py`, `tests/test_devtest_issue_corpus.py` | All survive |

### UNRELATED to this phase — do not touch

`planted_cap03_literal_index.cpp`, `planted_cap03_truncated_length.cpp`, `planted_constants_{fw_missing,host_missing,value_drift}.h`, `planted_json_parser_{key_string_drift,undispatched_key}.c`, `planted_sdp_comment_{brace,misanchor}.cpp`, `synthetic_nonzero_chip_id.py`, `fake_firestarter/`.

---

## The CI Workflow Edits — line-exact, live 2026-09-12

### Host: `firestarter_app/.github/workflows/ci.yml`

| Lines | Step | Disposition |
|---|---|---|
| `55-56` | `Catalog validity check` → `codegen.py --check` | **STAYS** (D-10) |
| `58-64` | `Codegen drift gate (messages.py)` | **STAYS** (D-10) |
| **`66-67`** | `Vector catalog validity check` → `codegen_vectors.py --check` | **DELETE** (D-09) |
| **`69-75`** | `Codegen drift gate (frame_vectors.py)` | **DELETE** (D-09) |
| `77-78` | `Install package + test deps` → `pip install -e .[test]` | STAYS |
| `80-81` | `ruff lint` → `ruff check firestarter/ tests/` | STAYS — **acceptance gate** (D-19) |
| `83-84` | `ruff format check` → `ruff format --check firestarter/ tests/` | STAYS — **acceptance gate** (D-19) |
| **`86-87`** | `mypy type check (watermark gate)` → `python tools/check_mypy_watermark.py` | **DELETE** (D-02) |
| `89-90` | `Run pytest with coverage` → `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | STAYS — **acceptance gate** (D-19) |
| `92-96` | `Smoke test - firestarter entry point and --help` | STAYS — **acceptance gate** (D-19) |
| `104-…` | second job `ci-py32` | Untouched — runs no ruff/mypy/coverage/codegen step |

**CONTEXT.md's line numbers are all still correct.** Delete the blank separator lines with each block (`68`, `76`, `88`) so no double blank remains.

Note `ci.yml:3` is a header comment reading *"gate steps: ruff check, ruff format --check, mypy watermark, pytest --cov"* — becomes false with D-02 and should be amended in the same commit.

### Firmware: `firestarter/.github/workflows/build.yml` — **not named in CONTEXT.md**

| Lines | Step | Disposition |
|---|---|---|
| `111-112` | `Catalog validity check` → `codegen.py --check` | STAYS |
| `114-120` | `Codegen drift gate (messages.h)` | STAYS |
| **`122-123`** | `Vector catalog validity check` → `codegen_vectors.py --check` | **DELETE** — required by D-08 |
| **`125-131`** | `Codegen drift gate (frame_vectors.h)` | **DELETE** — required by D-08 |
| `141-142` | `Run native unit tests` → `pio test -e native` | STAYS — **acceptance gate** (D-19) |
| `154-155` | `Run native unit tests (no DEV_TOOLS)` → `pio test -e native_nodevtools` | STAYS — **acceptance gate** (D-19) |
| `157-161` | `Install pytest` + `pytest tests/ -v` | STAYS — **this is where the baseline re-record can redden CI** |
| `192-193` | `Build PlatformIO Project` → `pio run` | STAYS |

### Firmware: `firestarter/.github/workflows/beta-build.yml` — **not named in CONTEXT.md**

| Lines | Step | Disposition |
|---|---|---|
| `93-99` | `Codegen drift gate (messages.h)` | STAYS |
| **`101-106`** | Comment block explaining why the vector pair was added here | **DELETE with the steps** |
| **`107-108`** | `Vector catalog validity check` | **DELETE** |
| **`110-116`** | `Codegen drift gate (frame_vectors.h)` | **DELETE** |
| `121-122` | `pio test -e native` | STAYS |
| `130-134` | `pytest tests/ -v` | STAYS |

**Six workflow steps total must be deleted, across three files in two repos — D-09 names two of them.** `check_size_baseline.py` is invoked by **no** workflow; it is an operator/local gate only.

---

## The Firmware Baseline Arithmetic (D-20)

### Measured live, this session

```
$ pio test -e native
================ 185 test cases: 185 succeeded in 00:00:20.233 ================
   … 17 suites, all PASSED, including  native/avr/test_frame_vectors  PASSED

$ pio test -e native_nodevtools
================ 185 test cases: 185 succeeded in 00:00:19.880 ================
   … 17 suites, all PASSED, including  native/avr/test_frame_vectors  PASSED
```

`test_frame_vectors.cpp` contributes **6 `RUN_TEST(...)` cases in 1 suite** [VERIFIED: `firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp:391-396` — `test_crc8_known_answer`, `test_vector_encode_leg`, `test_vector_decode_leg`, `test_vector_decode_leg_main_path`, `test_cmd_idle_overflow_at_full_block`, `test_even_block_no_remainder`; `grep -c "RUN_TEST("` → 6, `grep -cE "^(static )?void test_"` → 6].

**Projected new pair: `cases: 179, succeeded: 179, suites: 16` for both pinned envs.** This projection is stated **only so the planner can size the work**. Per the standing rule the plan MUST transcribe both figures from the cold capture log and must NOT compute them by arithmetic on 185−6.

### Baseline file sites to move (`firestarter/scripts/baseline/size_baseline.json`)

| Line | Key | Current |
|---|---|---|
| `:69` | `native_envs.native.cases` | `185` |
| `:70` | `native_envs.native.succeeded` | `185` |
| `:71` | `native_envs.native.suites` | `17` |
| `:75` | `native_envs.native_nodevtools.cases` | `185` |
| `:76` | `native_envs.native_nodevtools.succeeded` | `185` |
| `:77` | `native_envs.native_nodevtools.suites` | `17` |
| `:88` | `envs_agree_note` | quotes `{cases: 185, suites: 17, all_passed: true}` **in prose** — must move with them |

`native_envs.native_pinmap_provisional` (`:80-85`, `cases: 11, suites: 1`) is untouched — that env's `test_filter` does not name `test_frame_vectors`. `size_baseline_base01.json` is not re-anchored (D-20).

### What `check_size_baseline.py` compares — exactly vs. tolerantly

| Function | Fields | Comparison |
|---|---|---|
| `compare_native` (`:730-751`) | `cases`, `suites` | **EXACT** — `!=` on both, one failure line each |
| `compare_native` | `all_passed` | **EXACT** — must be `True`; names every non-`PASSED` suite, capped at 20 |
| `compare_avr` (`:541-569`) | `flash_used`, `flash_total`, `ram_used`, `ram_total` | **EXACT** — zero tolerance on all four |
| `compare_avr_policy_merge05` (`:640+`, only under `--policy merge05`) | flash / RAM deltas | **TOLERANT** — band + four named exemptions via `_merge05_flash_allowance`; RAM via `_merge05_ram_allowance` |

The default path is `compare_avr`, i.e. **exact**; the tolerant path fires only with `--policy merge05`.

### AVR reachability — D-20's premise VERIFIED

```
$ git grep -n "frame_vectors" -- src/
(no output)
```

`frame_vectors.h` is included only from `test/native/avr/test_frame_vectors/{host_stubs.cpp, serial_read_mock.h, test_frame_vectors.cpp}`; the only other hits repo-wide are a **comment** at `test/native/avr/_shared/host_stubs_common.inc:54` and prose in `test_eeprom28c_sdp/RED-BASELINE.md:576`. Neither is an `#include`.

Confirmed empirically by a cold AVR rebuild:

```
$ rm -rf .pio/build/uno && pio run -e uno
Flash: [=======   ]  69.4% (used 22734 bytes from 32768 bytes)
   pinned size_baseline.json avr_targets.uno.flash_used = 22734   ← exact match
```

**Conclusion: the twelve AVR figures do not move. D-19's "not a full cold three-target AVR rebuild" holds.** The native suite runs in ~20 s per env, so the "one cold capture" of D-21(b) is cheap.

### The cold-capture command sequence

Run from `/workspaces/firestarter`, **after** the suite and its `platformio.ini` registrations are deleted, in the same working tree that will be committed:

```bash
rm -rf .pio/build/native .pio/build/native_nodevtools
pio test -e native              2>&1 | tee <capture>/native.log
pio test -e native_nodevtools   2>&1 | tee <capture>/native_nodevtools.log
```

Transcribe `cases`/`succeeded` from each log's `======== N test cases: N succeeded ========` line and `suites` by counting the SUMMARY rows. Then verify:

```bash
python3 scripts/check_size_baseline.py \
  --native-log native=<capture>/native.log \
  --native-log native_nodevtools=<capture>/native_nodevtools.log
```

### The `platformio.ini` edits (all four confirmed live)

`:101` and `:160` — the `native/avr/test_frame_vectors` entries in each pinned env's `test_filter`. `:122` and `:182` — the `-I test/native/avr/test_frame_vectors` build flags. **All four line numbers in CONTEXT.md are still correct.**

---

## The `catalog/codegen.py` Meta-Canonical Strip (D-17)

### Byte-identity confirmed across all three repos

```
58982e87fc3ed6e465adb7a58502e0cd54485692b656005d86a61e73a09e0bcd  tools/catalog/codegen.py
58982e87fc3ed6e465adb7a58502e0cd54485692b656005d86a61e73a09e0bcd  firestarter/tools/catalog/codegen.py
58982e87fc3ed6e465adb7a58502e0cd54485692b656005d86a61e73a09e0bcd  firestarter_app/tools/catalog/codegen.py

260066039d07ab5ce6776709e34e91ea23099ada67a68f7c616b432bd41849dd  tools/catalog/messages.toml   (+ both sub-repos, identical)
```

[VERIFIED: `sha256sum`, this session.] D-17's premise holds exactly.

### The citations, by line (live, `/workspaces/tools/catalog/codegen.py`)

| Line | Verbatim text | Classification |
|---|---|---|
| `13` | `LCAT-03 historical note: an earlier revision emitted a third output` | **Explains the code** (why `--language cpp-table` no longer exists). Keep; drop `LCAT-03 `. |
| `18` | `Dropped post-Phase-7 to reclaim that space; the cpp-table emitter and` | **Explains the code.** Keep; drop `post-Phase-7`. **CONTEXT.md's D-17 counts four hits and does not name this one** — see §Pitfall 6. |
| `21` | `Determinism contract (LCAT-05): two consecutive runs against the same catalog` | **Explains the code** (the determinism contract is real behaviour). Keep; drop ` (LCAT-05)`. |
| `29` | `Validation (LCAT-02 + LCI-04): the --check flag runs the full 10-rule catalog` | **Explains the code.** Keep; drop ` (LCAT-02 + LCI-04)`. |
| `151` | `# 2. CATALOG VALIDATION (LCAT-02 + LCI-04)` | Section-header comment. Keep the header; drop ` (LCAT-02 + LCI-04)`. |

**Five hits, not four.** None is pure process provenance — all five surround real code explanation. The correct edit in every case is *drop the identifier, keep the sentence*.

### PROVEN: the strip cannot move `messages.h` or `messages.py`

A stripped copy was built in a scratch directory and both artifacts regenerated from it:

```
$ python3 codegen_stripped.py --catalog tools/catalog/messages.toml --language cpp    --target messages_new.h
OK: wrote …/messages_new.h (cpp, 77 messages).
$ python3 codegen_stripped.py --catalog tools/catalog/messages.toml --language python --target messages_new.py
OK: wrote …/messages_new.py (python, 77 messages).
$ cmp messages_new.h  firestarter/include/messages.h            && echo "messages.h BYTE-IDENTICAL"
messages.h BYTE-IDENTICAL
$ cmp messages_new.py firestarter_app/firestarter/messages.py   && echo "messages.py BYTE-IDENTICAL"
messages.py BYTE-IDENTICAL
```

[VERIFIED: falsification attempt run this session — the docstring/comment strip is provably output-neutral. The banner emitter does not embed the module docstring.]

### What `sync_to_subrepos.sh` does — read live

`/workspaces/tools/catalog/sync_to_subrepos.sh` (115 lines):

1. **Copies** `FILES=(messages.toml codegen.py)` (`:25`) from `$SCRIPT_DIR` into `firestarter/tools/catalog/` and `firestarter_app/tools/catalog/` (`:38-55`), `diff -q`-ing each copy against its source.
2. **Asserts cross-sub-repo identity** of the two vendored `messages.toml` copies with a real two-operand `diff` (`:63-70`), `exit 1` with an `ERROR:` line on divergence.
3. **Regenerates** `firestarter/include/messages.h` (`:78-93`) and `firestarter_app/firestarter/messages.py` (`:98-113`) into a `mktemp` file using the **meta** `codegen.py` + **meta** `messages.toml`, then `cp`s each over the sub-repo target.
4. Prints `OK: catalog synced to both sub-repos.`

**Critical:** step 3 **overwrites unconditionally and asserts nothing about the prior content** — its `diff -q "$tmp" "$target"` after the `cp` is trivially true. The script therefore **cannot** prove `messages.h`/`messages.py` unchanged. D-17's "verified byte-unchanged" must be proven the only way available:

```bash
cd /workspaces/firestarter     && git diff --exit-code include/messages.h
cd /workspaces/firestarter_app && git diff --exit-code firestarter/messages.py
```

Run **after** the sync. Exit 0 is the proof; exit 1 means the strip moved a generated artifact, which the falsification test above says cannot happen.

**`FILES` is not modified** (D-11) — confirmed the array is `(messages.toml codegen.py)` at `:25` and contains nothing else.

**Standing memory reconciled:** "`codegen.py` emits ruff-clean `messages.py`; do NOT hand-normalize" is about codegen's **output**. `codegen.py` **itself is not ruff-format clean** — see §Pitfall 3.

---

## The Six Survivors' Citations (D-16 / D-18)

Scanned with `/usr/bin/grep -nE '[Pp]hase[ -][0-9]|\bD-[0-9]+|[Pp]lan [0-9]|\.planning|\b[A-Z]{2,8}-[0-9]{2}\b|quick-[0-9]'`.

### `tools/build_db.py` — 13 hits (CONTEXT.md said 4)

All thirteen **explain the code**; all thirteen are "keep the comment, drop the identifier."

| Line | Verbatim citation text | Action |
|---|---|---|
| `11` | `# Pinned to the SHA recorded in tools/DECODE-NOTES.md §0/§3 (the Phase-86 regen` | Drop `(the Phase-86 regen provenance of record)`. Keep the pin rationale; `tools/DECODE-NOTES.md` is an in-repo file, not `.planning/` — keep that reference. |
| `113` | `# … omitted per PGSZ-01 discipline. The shared entry gets W29C040's citation…` | Drop `per PGSZ-01 discipline`. |
| `118` | `# Not individually documented in the in-repo datasheet — omitted per PGSZ-01` | Drop `per PGSZ-01`. |
| `150` | `# NOT 0x35 or 0x39 — removed by v1.11 DEC-05` | Drop `by v1.11 DEC-05`. |
| `457` | `# DB-07: Initialize support classification fields.` | Drop `DB-07: `. |
| `480` | `# DB-04 Approach A (67.1-01): reason string begins with SC-required` | Drop `DB-04 Approach A (67.1-01): `. |
| `507` | `# DB-04 Approach A (67.1-01): reason string begins with` | Same. |
| `509` | `# Non-empty adapter note required (DB-02 SC#1).` | Drop `(DB-02 SC#1)`. |
| `522` | `# CR-01 Option A: demote to NON_DISPATCHABLE_ALGO so dispatch()` | Drop `CR-01 Option A: `. |
| `612` | `# Site C: DB-03 NMOS VPP correction.` | Drop `DB-03 `. |
| `626` | `# DB-04 Approach A (67.1-01): reason string begins with` | Same as `480`. |
| `634` | `# CR-01 Option A: demote to NON_DISPATCHABLE_ALGO so dispatch()` | Same as `522`. |

**Do NOT touch** `build_db.py:116` and its siblings — `[CITED: firestarter/datasheets/…/W29C020.pdf §6.2 …]` are **datasheet** citations, not process citations, and the project's generator-proof rule depends on them.

### `tools/parse_devtest_issue.py` — 6 hits (CONTEXT.md said 2)

| Line | Verbatim | Kind | Action |
|---|---|---|---|
| `26` | `Phase-114 1.0 -> 1.1 \`ladder_state\` addition) without a code change.` | module docstring, explains behaviour | Rewrite as "a future 1.0 → 1.1 `ladder_state` addition" |
| `40` | `Phase-108's internal per-run N>=2 (a single sweep's own repeat-run` | module docstring, explains a real distinction | Rewrite as "the report's own internal per-run N≥2" |
| `127` | `and of a missing \`ladder_state\` key (schema 1.0, pre-Phase-114) --` | function docstring | Drop `, pre-Phase-114` |
| `170` | `would conflate this with Phase-108's internal per-run N>=2, RESEARCH` | function docstring; `RESEARCH Pitfall 5` is also a GSD artifact reference | Rewrite; drop both |
| `268` | `firmware-version claim can rest on this report (PROV-06): a labelled` | function docstring | Drop ` (PROV-06)` |
| `390` | `"INBOX-01 stdlib triage parser for a community \`dev test\` GitHub "` | **`argparse` `description=` — user-facing `--help` text** | See §Pitfall 2 |

`:22` also carries `Untrusted input (T-114-03/T-114-04, RESEARCH Pitfall 6)` — a threat-ID citation in the module docstring; in scope by the same reading.

### `tools/gen_sdp_bus_config.py` — 3 hits (CONTEXT.md said 1)

| Line | Verbatim | Kind | Action |
|---|---|---|---|
| `5` | `Derives, validates and emits the \`bus_config_t\` ground truth the Phase-116 trace` | module docstring | Rewrite as "…the SDP trace suites assert against" |
| `280` | `"bus_config (D-09 premise) but diverged"` | **`ValueError` message — runtime user-visible string** | Drop `(D-09 premise)`; see §Pitfall 2 |
| `347` | `"Derive + emit the bus_config_t ground truth for the Phase-116 "` | **`argparse` `description=` — user-facing `--help` text** | See §Pitfall 2 |

### `tools/gen_test_image.py` — 0 regex hits, 3 real hits (CONTEXT.md said 3)

The file (79 lines, read in full) contains **no `Phase N`, no `D-NN`, no `plan N`, no `.planning/`**. CONTEXT.md's count of 3 is almost certainly:

| Line | Verbatim | Why it counts |
|---|---|---|
| `17` | `oracle value to record in EVIDENCE.json as sha256_image_A / sha256_image_B.` | `EVIDENCE.json` is a GSD phase artifact |
| `20` | `/tmp/firestarter_bench_p82/<chip>_img_A.bin  (seed=1)` | **`p82` is a phase number encoded in a path** |
| `21` | `/tmp/firestarter_bench_p82/<chip>_img_B.bin  (seed=2)` | same |

**This is the concrete reason D-18 forbids a regex pass** — `p82` matches no reasonable citation pattern. Every survivor must be read end-to-end.

### `tools/gen_validation_header.py` — 0 hits

[VERIFIED: broad-regex scan returns nothing.] CONTEXT.md's 0 is correct. **No edit needed.**

### `tools/catalog/codegen.py` — 5 hits, edited at the meta copy only

See §The Catalog Strip. **Never edit `firestarter_app/tools/catalog/codegen.py` directly** (D-17).

---

## Order-of-Operations Hazards

D-21 fixes the wave order and names three constraints. These are the hazards **it does not name**, all measured live.

### H1 (BLOCKING) — 45 tests stop collecting the moment `check_dispatch.py` / `check_devtest_orchestrator.py` are removed

Seven modules import at module level. A collection error is not a failure — pytest reports `ERROR` and the run's exit code is non-zero with **no** result for those modules. Any wave that deletes these two gates without landing the repair in the same commit leaves the suite unable to report on anything else that wave did. **This must be resolved before Wave 2 starts** (§Open Questions Q1).

### H2 (BLOCKING) — the firmware baseline re-record reddens the firmware's own python suite

`firestarter/tests/test_check_size_baseline.py::test_clean_native_both_envs_pass` (`:570-601`) runs the checker against two committed fixture logs and asserts `"185" in result.stdout` and `"17" in result.stdout`. Simulated live against a 179/16 baseline:

```
### LEG A: clean native fixture vs 179/16 baseline
FAIL:
  native: cases baseline=179 observed=185
  native: suites baseline=16 observed=17
rc=1
```

**Remedy (the precedent the test's own docstring names):** re-capture `tests/fixtures/captured_test_native_summary.log` and `tests/fixtures/captured_test_native_nodevtools_summary.log` **in place** from the post-deletion tree, in the same cold capture and same commit — *"D-09: these two fixtures are never severed."* Do **not** sever onto a new fixture family here; that convention applies to the AVR `captured_build_*` family only.

**Re-capture shape:** both fixtures are **21 lines** — only the `=== SUMMARY ===` block, not the full build log. A raw `pio test` capture is 6,954 lines with 998 `warning:` lines. Truncate to the SUMMARY block to preserve the shape. (Even untruncated it would pass `check_build_warnings.py` — 998 is under the 1166 watermark, verified — but `test_check_build_warnings.py:327-341` Coverage 8 documents the fixture as "truncated, 0 warning lines", so keep it truncated.)

### H3 (SOFT) — a planted-failure fixture becomes partially vacuous

`test_planted_suites_errored_flips_checker_to_failure` (`:671`) still passes against a 179/16 baseline — verified:

```
### LEG B: planted suites-errored vs 179/16 baseline
FAIL:
  native: cases baseline=179 observed=141
  native: suites baseline=16 observed=17
  native: not all suites PASSED …; non-PASSED: … native/avr/test_frame_vectors=ERRORED, …
rc=1
```

`rc != 0` and `"ERRORED" in stdout` both hold, so the leg is green — but it now fails for three reasons instead of the one it exists to prove, and its fixture still lists a suite that no longer exists. Recommend re-deriving `tests/fixtures/planted_size_baseline_suites_errored.log` from the fresh capture in the same commit.

### H4 (RESOLVED, no action) — the coverage floor is not at risk

Two full suite runs this session, `--cov=firestarter`:

| Run | Stmts | Miss | Cover | Tests |
|---|---|---|---|---|
| Baseline (whole suite) | 5878 | 896 | **85%** | 2373 passed, 409 s |
| All 17 deleted test files deselected | 5878 | 903 | **85%** | 2222 passed, 400 s |

The 7-statement delta is **exactly** `firestarter/frame_vectors.py` (7 stmts, 0 miss, 100% in the baseline). After also deleting that module: 5871 stmts, 896 miss → **84.74%, rounds to 85%**. Against `--cov-fail-under=70` there are **15 percentage points of headroom**. **The `~15,589` lines leaving the tree are all under `tools/` and `tests/`, neither of which `--cov=firestarter` ever counted.** CONTEXT.md's note on this is correct.

This also independently confirms CONTEXT.md's claim that `tests/test_cobs.py` strands no product coverage: the only product-source coverage the whole deletion set removes is `frame_vectors.py`'s own 7 statements.

### H5 — `pyproject.toml` packaging

`packages = ["firestarter"]` (`:92`) is a package-level declaration; `frame_vectors.py` is not named individually anywhere in `[tool.setuptools]` or `[tool.setuptools.package-data]`. [VERIFIED: read `pyproject.toml:90-101`.] **No packaging edit is required**, and no packaging test names the module. Deleting it silently shrinks the wheel by one module.

### H6 — the meta repo's `config.json` `sub_repos` list is currently pruned in the working tree

```
   "planning": {
     "sub_repos": [
       "firestarter",
-      "firestarter_app",
-      "firestarter_app_py32",
-      "firestarter_py32_ci"
+      "firestarter_app"
     ]
```

An uncommitted prune from 4 entries to 2, live right now. This is the documented "GSD verbs silently prune `sub_repos`" hazard, and `config.json` is a VERIFICATION-covered file, so a prune alone can read `stale` and block phase transition. **A three-repo phase should restore this before Wave 1**, and no plan should re-run a verb that re-prunes it.

### H7 — firmware working-tree porcelain

`firestarter/tests/test_flash_path_record_sync.py::test_dirty_tree_is_detected` (`:838-875`) builds its dirty repo under `tmp_path`; the live-repo call at `:841-843` is only asserted "must not raise". Firmware pytest baseline this session: **360 passed in 11.6 s** with the tree dirty. **No porcelain blocker.**

### H8 — wave independence holds

Waves 2 and 3 are genuinely file-disjoint: the host deletion set and the firmware deletion set share no path, and the only cross-repo coupling (the `codegen.py` strip + sync) is D-21's separate post-wave commit. No generated file needs regenerating after a deletion **except** `messages.h`/`messages.py` at the sync, and those are proven output-neutral.

---

## Acceptance Gates — verbatim, runnable, with failure signals (D-19)

### App — run from `/workspaces/firestarter_app`

| # | Command | cwd | PASS signal | FAIL signal (`<fails_when>`) |
|---|---|---|---|---|
| 1 | `ruff check firestarter/ tests/` | `firestarter_app/` | `All checks passed!`, exit 0 | exit 1; output ends `Found N errors.` |
| 2 | `ruff format --check firestarter/ tests/` | `firestarter_app/` | `181 files already formatted`, exit 0 | exit 1; output ends `N files would be reformatted` |
| 3 | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | `firestarter_app/` | exit 0; `N passed`; `TOTAL … 85%` | exit 1; any of `failed`, `error`, or `FAIL Required test coverage of 70% not reached` |
| 4 | `firestarter --help` | anywhere (console script) | exit 0; Click usage block | exit ≠ 0 |
| 5 | `ruff check tools/` **(new, free)** | `firestarter_app/` | `All checks passed!` after the phase | exit 1 |

**Live pre-phase state:** gates 1, 2 and 4 are green; gate 3 is green at **2373 passed, 85%, 409 s**. Gate 5 is **currently RED with 6 errors, all in files this phase deletes** — `audit_coverage_matrix.py:39` (I001), `build_devtest_issue_corpus.py:159` (I001), `catalog/codegen_vectors.py:189` (UP031), `snapshot_report_shapes.py:41,42,43` (E402 ×3). After the phase `ruff check tools/` passes clean; it is a free, honest, zero-cost acceptance signal and does not violate D-23 (it authors no new gate — it is an existing tool invoked with a wider scope).

**Environment for gate 3.** The devcontainer is Python **3.12.14**; app CI pins **3.11 only**. Devcontainer python and the editable install are already present and the suite runs green there, but the CI-faithful form is:

```bash
cd /workspaces/firestarter_app
uv venv --python 3.11 .venv-ci && . .venv-ci/bin/activate
pip install -e '.[test]'
pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```

`uv 0.12.6` is installed at `/usr/local/bin/uv` [VERIFIED]. Note the standing hazard: a sibling `firestarter/` checkout in the devcontainer can mask CI-only test failures (`tests/fw_presence.py` flips modules PASS→SKIP when the firmware tree is absent). D-13 deletes the only guard against the inverse defect; the sibling *is* present here, so devcontainer runs are the **permissive** direction.

Also note `[tool.pytest.ini_options] addopts = "-ra -q"` (`pyproject.toml:105`) — doubling `-q` suppresses the count line. Use `-o addopts=""` when you need the `N passed` figure.

### Firmware — run from `/workspaces/firestarter`

| # | Command | cwd | PASS signal | FAIL signal (`<fails_when>`) |
|---|---|---|---|---|
| 6 | `pio test -e native` | `firestarter/` | exit 0; `======== N test cases: N succeeded ========`; every SUMMARY row `PASSED` | exit ≠ 0; any SUMMARY row `FAILED`/`ERRORED` |
| 7 | `pio test -e native_nodevtools` | `firestarter/` | same | same |
| 8 | `python3 scripts/check_size_baseline.py --native-log native=<log> --native-log native_nodevtools=<log>` | `firestarter/` | exit 0; `PASS: native(cases=N,suites=M), native_nodevtools(cases=N,suites=M)` | exit 1; first line exactly `FAIL:` followed by indented `  <env>: cases baseline=X observed=Y` lines |
| 9 | `python3 -m pytest tests/ -q` | `firestarter/` | exit 0; `360 passed` pre-phase | exit ≠ 0 |
| 10 | `pio run` | `firestarter/` | exit 0; all AVR envs `SUCCESS` | exit ≠ 0 |

**CORRECTION to D-19.** `python scripts/check_size_baseline.py` with **no arguments exits 1** by design:

```
$ python3 scripts/check_size_baseline.py
FAIL: no envs compared -- supply --avr-log/--native-log or --rebuild (never-vacuous guard: a comparator that compares nothing must not pass)
rc=1
```

D-19's gate as worded is un-runnable. Use form #8. Verified working form and its failure signal, live:

```
$ python3 scripts/check_size_baseline.py --native-log native=/tmp/…/native.log
PASS: native(cases=185,suites=17)
rc=0

$ python3 scripts/check_size_baseline.py --native-log native=/tmp/…/native_planted.log
FAIL:
  native: cases baseline=185 observed=179
rc=1
```

`--rebuild` is an alternative but invokes `pio run -t clean` on **all three AVR envs** as well as the two native envs — far more than D-19 asks for. Prefer explicit `--native-log` pairs.

**Gate 9 is not in D-19's list but is in both firmware workflows** (`build.yml:161`, `beta-build.yml:134`) and is the leg H2 reddens. It must be run.

### The dangling-reference grep (D-19, "part of the work")

```bash
cd /workspaces && for n in check_devtest_orchestrator check_diagnostic_report_claims check_dispatch \
  check_is_memory_cmd_no_ifdef check_mypy_watermark check_no_community_support_status_write \
  check_no_exists_proxy check_no_log_in_sdp_window check_protection_readability_invariants \
  check_sdp_capability_invariants audit_coverage_matrix diff_db measure_plan_shapes \
  measure_part_number_delta snapshot_report_shapes build_devtest_issue_corpus ci_parity \
  ci_replica_venv codegen_vectors frame-vectors frame_vectors derive_sdp_partition scan_paths; do
  for r in . firestarter firestarter_app; do
    (cd "$r" && git grep -n -- "$n" -- . ':!.planning/' 2>/dev/null | sed "s|^|$r/|")
  done
done
```

**Use `git grep` or `/usr/bin/grep`, never the bare devcontainer `grep`** — it is ugrep and honors `.gitignore`, which silently under-scans and would make this gate fail open. Also avoid `grep -qF` with a dash-leading pattern (exits 2, fails open); use `-qFe`.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Stripping citations from the six survivors | A regex/AST rewriter | Hand editing, file by file, `ruff format --check` on the five clean survivors after each batch | D-18: three automated passes were reverted for collateral damage (a line-wise re-wrapper corrupted a string literal until the module stopped parsing; a prose-aware scrubber flattened docstring indentation package-wide). `gen_test_image.py`'s three hits (`p82`, `EVIDENCE.json`) match no plausible pattern. |
| Proving `messages.h`/`messages.py` unchanged | A new comparison script | `git diff --exit-code` in each sub-repo after `sync_to_subrepos.sh` | The sync script overwrites unconditionally and its own post-`cp` `diff -q` is a tautology. |
| A successor guard for anything retired | Any new `check_*.py`, CI step, or pre-commit hook | The verdict note at `.planning/notes/host-tools-retirement.md` | **D-23 forbids it, for any reason.** Third instance of the established pattern (`catalog-sync-check-retirement.md`, `dispatch-invariant-retirement-verdict.md`). |
| Computing the new native `cases`/`suites` | `185 − 6` | Transcribe from the committed cold-capture log | Standing rule; never compute a baseline figure by arithmetic on a prior record, and never use `--rebuild` to write one. |
| Amending ROADMAP.md | `roadmap.update-plan-progress` | Hand edits | D-22 + standing memory: the verb overwrites the dependency table positionally and kills phase name + req IDs. |
| Relocating `diff_db.py` | A `sys.path` hack or a cross-repo import | A copy plus the existing `FIRESTARTER_DB_FILE` / `FIRESTARTER_BASELINE_FILE` env seams | Standing rule "a skill owns its scripts"; and the file's own `__file__`-relative paths break on the move (see below). |

---

## The `diff_db.py` Relocation (D-05) — a hazard the decision does not name

`diff_db.py` resolves **both** its inputs relative to its own location:

```
firestarter_app/tools/diff_db.py:30   _DATA_DIR     = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
firestarter_app/tools/diff_db.py:31   _BASELINE_DIR = os.path.join(os.path.dirname(__file__), "baseline")
```

[VERIFIED: `firestarter_app/tools/diff_db.py:28-40`, read this session.]

Moved to `.claude/skills/devtest-rootcause/scripts/`, those resolve to `.claude/skills/devtest-rootcause/firestarter/data/` and `.claude/skills/devtest-rootcause/scripts/baseline/` — **neither exists**. The baseline it needs, `firestarter_app/tools/baseline/chip_database.baseline.json` (476 KB), **stays in the host repo** because D-14 puts `tools/baseline/` out of scope.

**The file already carries the seams to fix this** (`:33-40`):

```python
DB_FILE       = os.environ.get("FIRESTARTER_DB_FILE",       os.path.join(_DATA_DIR, "chip_database.json"))
BASELINE_FILE = os.environ.get("FIRESTARTER_BASELINE_FILE", os.path.join(_BASELINE_DIR, "chip_database.baseline.json"))
```

So the relocated copy runs correctly when invoked as, e.g.:

```bash
FIRESTARTER_DB_FILE=firestarter_app/firestarter/data/chip_database.json \
FIRESTARTER_BASELINE_FILE=firestarter_app/tools/baseline/chip_database.baseline.json \
python3 .claude/skills/devtest-rootcause/scripts/diff_db.py
```

Failure mode if this is missed: exit **2** with a missing/malformed-DB message (`diff_db.py:18` documents exit 2 as distinct from 1) — it fails closed, not silently, but the skill's documented procedure is broken.

### The skill's reference sites (live)

| File | Lines naming `diff_db.py` | Lines naming `check_dispatch.py` (to DROP) |
|---|---|---|
| `.claude/skills/devtest-rootcause/SKILL.md` | `17`, `272`, `281`, `353`, `420` | `17`, `273`, `392`, `422` |
| `.claude/skills/devtest-rootcause/scripts/seed_debug_session.py` | `68` | `59`, `69` |

CONTEXT.md's SKILL.md line list (`:17, :272, :281, :353, :420`) is **exactly correct** for `diff_db.py`. It does not enumerate the four `check_dispatch.py` sites; they are listed above. `seed_debug_session.py:68-69` emits a single command line invoking `build_db.py && diff_db.py && check_dispatch.py && pytest` — the `check_dispatch.py` clause must come out and the `diff_db.py` clause must be re-pointed at the relocated path with its env vars.

`SKILL.md:271-273` is the §4 regeneration block carrying the same three commands; same treatment. `SKILL.md:392` (*"Never weaken `check_dispatch.py` (GATE-03)…"*) and `:422` (a troubleshooting-table row) are standalone rules that simply go.

`build_db.py` references throughout SKILL.md (`13, 16, 31, 42, 43, 63, 90, 97, 98, 123, 141, 271, 277, 323, 418, 419, 431`) are **untouched** — `build_db.py` survives (D-10/D-14).

**TOOLS-05 does not follow the file.** The relocated `diff_db.py` lands under `.claude/` in the meta repo, outside both `firestarter_app/tools/` (TOOLS-05's scope) and `firestarter/`/`firestarter_app/` (CLAUDE.md's comment rule's scope). **No citation sweep is required on the copy** — it keeps its 9 `.planning` refs, 19 phase refs and 9 `D-NN` refs, including the runtime output string at `:911` (`"Phase 86 VAR-05 / D-10 (cited)"`). That is correct and intended: a GSD-process tool living in the GSD process directory may cite GSD.

---

## Common Pitfalls

### Pitfall 1 — Treating this as a deletion phase

**What goes wrong:** 93 surviving tests break, 45 of them at collection time, and the suite reports nothing about the rest of the work.
**Why it happens:** CONTEXT.md's mass table counts lines to remove and its `code_context` says the surviving generator-adjacent tests "survive untouched" — which is measured-wrong for `test_blast_radius_invariance.py`.
**How to avoid:** Plan deletion + repair as one unit per commit. Run `pytest tests/ -q --co` after each deletion batch; a collection error is the early warning.
**Warning signs:** `ERROR tests/test_val_wire_*.py - ModuleNotFoundError: No module named 'check_dispatch'`.

### Pitfall 2 — Sweeping a citation out of a user-facing string

Three of the survivors' citations are **not comments**:
- `parse_devtest_issue.py:390` — `argparse` `description=` → printed by `--help`
- `gen_sdp_bus_config.py:347` — `argparse` `description=` → printed by `--help`
- `gen_sdp_bus_config.py:280` — a `ValueError` message raised at runtime

CLAUDE.md's carve-out names *Click* docstrings as user-facing `--help` text; `argparse` descriptions are the same category by the same reasoning. TOOLS-05 nonetheless says *no file under `tools/` cites a phase number*. **They are both right and they conflict here.** Recommended resolution, needing no new decision: rewrite these three strings so they keep their meaning and lose the identifier (`"stdlib triage parser for a community dev test GitHub issue"`, `"…for the SDP trace suites"`, `"…but diverged"`). No test asserts on any of the three [VERIFIED: `git grep -nE "INBOX-01|D-09 premise|Phase-116 " -- tests/` returns only two unrelated docstring mentions; `tests/__snapshots__/` holds only `test_characterization.ambr`, which does not cover these tools].

### Pitfall 3 — Running `ruff format` on `catalog/codegen.py`

`tools/catalog/codegen.py` is **not ruff-format clean**. `ruff format --check` on it proposes ~120 lines of change (aligned dict literals unaligned, tuple literals exploded one-per-line, `argparse` calls rewrapped, two blank-line insertions). Running `ruff format` (write mode) on it would:

1. produce a large collateral diff unrelated to the citation strip, and
2. **break the three-repo byte-identity invariant** unless the change is made at the meta copy and re-synced.

D-18's instruction *"Do it by hand with `ruff format --check`"* is satisfiable for the other five survivors (all already formatted) but **not** for `codegen.py`. Scope the formatter check to the five:

```bash
ruff format --check tools/build_db.py tools/gen_sdp_bus_config.py \
                    tools/gen_validation_header.py tools/parse_devtest_issue.py tools/gen_test_image.py
```

`ruff check` on all six passes clean today and must still pass after the sweep.

The standing memory *"codegen.py emits ruff-clean messages.py; do NOT hand-normalize"* is about the **output**, not the emitter. Both statements are true simultaneously.

### Pitfall 4 — Forgetting the firmware's two `codegen_vectors` workflow pairs

D-09 names the host pair only. The firmware carries `build.yml:122-131` and `beta-build.yml:107-116`. Deleting `firestarter/tools/catalog/codegen_vectors.py` without them turns firmware CI red on **every branch** (`build.yml` triggers on all branches) and on **every beta push** (`beta-build.yml` is the artefact-publishing path).

### Pitfall 5 — Trusting CONTEXT.md's line arithmetic

Live measurement differs in two places. Report the live values:

| CONTEXT.md | Live | Cause |
|---|---|---|
| Process tools' test files: **1,625** | **1,398** | The 227-line difference is exactly `tests/test_devtest_issue_corpus.py`, which CONTEXT.md's own `code_context` says **survives**. Double-counted. |
| Host repo subtotal: **15,589** | **15,362** | Same 227 lines. |
| Total deleted: **~16,700** | **16,504** | Same, plus rounding. |

Neither affects any decision — the mass is a framing figure. **Affects D-04's blast radius only insofar as the planner must not delete `test_devtest_issue_corpus.py`.**

### Pitfall 6 — Trusting CONTEXT.md's citation counts

D-16's per-file counts were taken with a narrower pattern than TOOLS-05's own wording:

| File | CONTEXT.md | Live (broad scan) |
|---|---|---|
| `catalog/codegen.py` | 4 | **5** (adds `:18`, `post-Phase-7`) |
| `build_db.py` | 4 | **13** |
| `gen_test_image.py` | 3 | **0 by regex, 3 by reading** (`p82` ×2, `EVIDENCE.json`) |
| `parse_devtest_issue.py` | 2 | **6** (+ `:22` threat IDs) |
| `gen_sdp_bus_config.py` | 1 | **3** |
| `gen_validation_header.py` | 0 | **0** ✓ |

The live counts are what TOOLS-05's wording actually covers (*"a phase number, plan number, decision ID, or `.planning/` path"* — and `CLAUDE.md`'s rule explicitly includes `REQ-NN`-shaped requirement IDs). **Report the live figure in the SUMMARY, not CONTEXT.md's.**

### Pitfall 7 — Editing `firestarter_app/tools/catalog/codegen.py`

D-17 is explicit and the hashes confirm the mechanism. A sub-repo edit is reverted by the next `sync_to_subrepos.sh` run and breaks the cross-repo identity the script asserts at `:63-70`.

### Pitfall 8 — Leaving `firestarter_app/CLAUDE.md:122-128` stale

That paragraph tells every future agent that `tools/check_dispatch.py` is a live regression guard for the WARNING-5 / GATE-03 invariants. After D-01 it is false, and the file is the first thing an agent reads. Edit it in the same commit as the gate deletion. This is *deleting* prose, which the no-comments rule permits.

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| One-shot phase gates stay on the payroll permanently | Retire the gate, write a verdict note, author no successor | `catalog-sync-check-retirement.md` (2026-09-11, Phase 185); `tools/wiki/` retired wholesale 2026-09-02; `dispatch-invariant-retirement-verdict.md` | D-23 is the third instance; the note shape is settled |
| Amend success criteria at milestone audit | Amend them in-phase, by hand, quoting the conflict | Phase 185 criterion 5; Phase 187 criterion 4 | D-22 follows both |
| Baseline figures computed from a prior record | Transcribed from a committed cold-capture log; never `--rebuild` | Standing since Phase 149 | D-20's re-record |
| A skill imports a script from `firestarter_app/tools/` | A skill owns a copy plus a drift check | Standing rule | D-05 |

**Retired / removed and not to be revived by this phase:** the meta repo's only workflow (deleted Phase 185 — `.github/workflows/` is empty and meta runs no CI at all); `tools/wiki/` and `wiki-check.yml`; any mypy floor (D-02).

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Python (devcontainer) | app suite, codegen | ✓ | 3.12.14 | — |
| `uv` | CI-faithful py3.11 venv | ✓ | 0.12.6 (`/usr/local/bin/uv`) | devcontainer 3.12 (permissive, masks CI-only failures) |
| `pytest` | gates 3, 9 | ✓ | 9.1.1 | — |
| `ruff` | gates 1, 2, 5 | ✓ | 0.16.5 | — |
| `pio` (PlatformIO Core) | gates 6, 7, 10 | ✓ | 6.1.19 | — |
| AVR toolchain | cold `pio run -e uno` | ✓ | `toolchain-atmelavr`, `framework-arduino-avr`, `tool-avrdude` present | — |
| `firestarter` console script | gate 4 | ✓ | editable install resolves to `/workspaces/firestarter_app/firestarter/__init__.py` | — |
| `git` | all sweeps | ✓ | — | — |
| `/usr/bin/grep` (GNU) | evidence greps | ✓ | — | `git grep`. **Not** bare `grep` (ugrep, honors `.gitignore`) |
| Network | none | n/a | — | Nothing in this phase fetches |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none. Every acceptance gate was executed successfully this session.

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → treated as enabled. This phase deletes code and installs nothing.

### Applicable ASVS categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | No auth surface touched |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | No access-control code touched |
| V5 Input Validation | **yes, indirectly** | `parse_devtest_issue.py` treats community-authored issue bodies as hostile (`:22` — *"every issue body is community-authored and MUST be treated as hostile"*). **The D-16 sweep must not weaken that docstring's substance** — drop the `T-114-03/T-114-04` identifiers only, keep the hostile-input statement and every behaviour it describes |
| V6 Cryptography | no | `gen_test_image.py` uses `hashlib.sha256` as a test oracle, not a security control; `codegen.py`'s CRC8 is a wire checksum |

### Threat patterns for this change class

| Pattern | STRIDE | Mitigation |
|---|---|---|
| Deleting a gate that was the only control on a real hazard | Repudiation / Tampering | **Accepted and disclosed** for D-08 (cross-repo wire contract), D-12 (consumer declarations), D-13 (firmware-rename masking), D-15. D-23's verdict note is the record. `check_dispatch.py`'s GATE-03 electrical-safety guard (no 12 V handler on a no-VPP-pin part) goes with D-01 — its disclosure belongs in the note with the others |
| A deletion silently disabling a test rather than failing it | Repudiation | A collection error is loud; a `SKIP` is not. Use `pytest --co` and compare the collected count against the 2373 baseline, not just the pass count |
| Weakening a hostile-input docstring during a prose sweep | Tampering | Keep the substance of `parse_devtest_issue.py:22-46`; strip only identifiers |
| Losing the electrical-safety invariant's documentation | Information Disclosure (of a hazard) | `firestarter_app/CLAUDE.md:115-128` carries the WARNING-5 / VPP-pin explanation. **Edit only the "Regression guard:" sentences (`:122-128`); keep `:115-121`, the hazard description itself** |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The expected post-deletion native pair is `cases: 179, suites: 16` | Firmware Baseline | Low — stated as a projection only; the plan must transcribe from a cold capture, which self-corrects any error |
| A2 | CONTEXT.md's D-16 counts were taken with a narrower regex than TOOLS-05's wording, rather than reflecting a different intended scope | Pitfall 6 | Medium — if the operator intended the narrow scope, the sweep does more work than asked. It does not do *less*, so it cannot under-satisfy TOOLS-05. Worth one line of confirmation at plan-check |
| A3 | `argparse` `description=` strings fall under CLAUDE.md's "user-facing `--help` text" carve-out by the same reasoning as Click docstrings | Pitfall 2 | Low — the recommended rewrite satisfies both readings simultaneously |
| A4 | `tests/golden/v1.3-COVERAGE-MATRIX.md` (186 KB) should be deleted with its only consumer | Deletion Inventory | Low — keeping it is harmless; it just becomes unreferenced data. D-14's spirit (scripts, not data) argues for keeping it; the ledger it mirrors lives in `.planning/` anyway |
| A5 | The `planted_size_baseline_suites_errored.log` re-derivation (H3) is worth doing | H3 | Low — the leg stays green either way; this is a vacuity-hygiene recommendation, not a blocker |

---

## Open Questions

### Q1 — `check_dispatch.dispatch()` has no home, and D-01 does not decide one **(BLOCKING — needs a `checkpoint:human-verify`)**

**What we know.** `tools/check_dispatch.py` is two things in one file. `main()` (`:177`) is the gate D-01 retires. But `dispatch()` (`:136`), `_ALGO_MEM_TYPE` (`:38`), `_SRAM_PROTOCOLS` (`:55`) and `KNOWN_PROTOCOLS` (`:120`) are a **host-side software model of the firmware's `configure_memory()` dispatch order** — the module docstring says so: *"Mirrors the post-Phase-12 dispatch order documented in `firestarter/src/proms/memory.cpp::configure_memory`."* Eight surviving test modules import those symbols as their oracle: six `test_val_wire_*` modules (module-level, 38 tests), `test_decoder.py` (5 tests), `test_build_db_inclusion.py` (1 test).

**What's unclear.** D-01 says "all ten, no exceptions." D-08 says "do not quietly preserve a fragment." Whether that prohibition extends to `check_dispatch.py`'s library half is not decided anywhere in CONTEXT.md, and the three available answers have very different costs:

| Option | Cost |
|---|---|
| (a) Move `dispatch()` + the three tables into a surviving test helper (e.g. `tests/dispatch_model.py`), delete only the gate half | ~90 lines preserved; 44 tests keep working; arguably "preserving a fragment" |
| (b) Delete the eight consuming test modules too | ~105 tests and six wire-contract modules destroyed; far beyond the phase's scope and never offered to the operator |
| (c) Leave `check_dispatch.py` in place | Violates D-01 outright |

**Recommendation.** Option (a), gated behind a `checkpoint:human-verify` task at the head of Wave 2, with the 44-test figure and the "this is a decode model, not a gate" distinction put to the operator in one sentence. Option (b) must not be chosen silently; option (c) must not be chosen at all. **The same question, smaller, applies to three more symbols:** `snapshot_report_shapes.render_shape` (38 tests), `check_devtest_orchestrator._HANDLER_FUNCTION_NAMES` (7 tests), `check_diagnostic_report_claims.FORBIDDEN_PATTERNS` (1 test). Bundle all four into one checkpoint.

### Q2 — Does the TOOLS-05 sweep reach runtime strings and requirement IDs?

**What we know.** TOOLS-05's text covers "a phase number, plan number, decision ID, or `.planning/` path"; `CLAUDE.md` adds `REQ-NN`-shaped requirement IDs by example. `build_db.py` carries 12 requirement-ID citations and 1 phase citation; three survivor citations live in `--help`/error strings.
**What's unclear.** Whether the operator's D-16 counts (4 / 3 / 2 / 1 / 0) were a scope statement or a measurement artifact.
**Recommendation.** Do the broad sweep (the live counts), note the divergence in the plan, and surface the three user-facing strings as a one-line confirmation at plan-check rather than a checkpoint. The broad sweep cannot under-satisfy TOOLS-05.

### Q3 — Where does the `firestarter_app/tests/` half of the provenance todo end up?

**What we know.** `.planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md` is to be **amended, not closed** (its `tests/` half, ~1,774 hits, stays open). The `tools/` half is discharged mostly by deletion.
**What's unclear.** Nothing blocking — this is a bookkeeping instruction already in CONTEXT.md.
**Recommendation.** One task in the ledger plan; amend the todo with the measured live remainder (the six survivors' actual hit count after the sweep, not CONTEXT.md's ~296).

### Q4 — `.planning/config.json`'s pruned `sub_repos`

**What we know.** The working tree has an uncommitted prune from 4 entries to 2 (H6).
**What's unclear.** Whether the two dropped entries (`firestarter_app_py32`, `firestarter_py32_ci`) are still wanted.
**Recommendation.** Restore the committed value before Wave 1 and do not let any plan run a verb that re-prunes it. Not this phase's work, but it can block this phase's transition.

---

## Sources

### Primary (HIGH confidence — measured live against the working tree, 2026-09-12)

- Filesystem existence + `wc -l` probe over all 46 deletion paths — §Deletion Inventory
- `git grep` reference sweeps across all three repos (`/workspaces`, `firestarter`, `firestarter_app`) — §Dangling References
- `pytest tests/ --cov=firestarter`, two full runs (2373 passed / 85%; 2222 passed / 85%) — §H4
- `pytest --co` per-module collected counts — §A1, §A2
- `pio test -e native` and `-e native_nodevtools` (185/17 each) — §Firmware Baseline
- `rm -rf .pio/build/uno && pio run -e uno` → Flash 22734 = pinned figure — §D-20 verification
- `check_size_baseline.py` invoked with a real log, a planted log, and a simulated 179/16 baseline — §H2, §H3, §Acceptance Gates
- `sha256sum` across all three `codegen.py` / `messages.toml` copies — §Catalog Strip
- Falsification test: stripped `codegen.py` regenerating `messages.h` / `messages.py` byte-identically — §Catalog Strip
- `ruff check` / `ruff format --check` on `firestarter/ tests/`, `tools/`, and the six survivors — §Acceptance Gates, §Pitfall 3
- Direct `Read`/`sed` of: `ci.yml`, `build.yml`, `beta-build.yml`, `beta-release.yml`, `platformio.ini`, `size_baseline.json`, `check_size_baseline.py`, `sync_to_subrepos.sh`, `pyproject.toml`, `conftest.py`, `diff_db.py`, `check_dispatch.py`, `gen_test_image.py`, `SKILL.md`, `seed_debug_session.py`, and the six survivors

### Secondary (MEDIUM confidence — read this session, authoritative for intent but not for the live tree)

- `.planning/phases/188-the-tools-directory/188-CONTEXT.md` — the 24 decisions, verbatim
- `.planning/notes/host-tools-checker-apparatus-audit.md` — including both self-corrections
- `.planning/notes/catalog-sync-check-retirement.md` — D-23's template
- `.planning/REQUIREMENTS.md` §TOOLS (lines 202-232) and traceability rows 278-284
- `/workspaces/CLAUDE.md` §"Source code comments — hard rule", §"Milestone close and branch protection"

### Tertiary (LOW confidence — not independently re-verified)

- CONTEXT.md's mass table figures where they diverge from live measurement (§Pitfall 5, §Pitfall 6) — the live figure is reported instead in every case

---

## Project Constraints (from CLAUDE.md)

| Directive | Where | Bearing on this phase |
|---|---|---|
| **Write no comments into product source** under `firestarter/` or `firestarter_app/`; not overridable by a plan | `/workspaces/CLAUDE.md` §"Source code comments" | Governs D-16/D-18. **It forbids writing, not deleting** — the sweep is permitted. Rewriting a comment to drop its identifier is *editing an existing* comment; do not add new ones. Do not make "a comment exists" an acceptance criterion |
| Click docstrings are user-facing `--help` text, **not** comments | same | Extends by the same reasoning to `argparse` `description=` — §Pitfall 2 |
| `main` is protected in all three repos; base branch is `beta` | same §"Milestone close" | D-24. Work on a `v1.37`-slug branch in all three repos including meta |
| Constants/flag bits duplicated between `constants.py` and `firestarter.h` — change both together | same §"Key Architecture Points" | Not engaged; this phase changes no constants |
| `chip_database.json` is generated; never hand-edit | same | Not engaged; CONTEXT.md puts DB content out of scope explicitly |
| Serial protocol changes must stay in sync between `serial_comm.py` and `firestarter.cpp` | same | **Engaged indirectly.** D-08 deletes the only automated proof that the two sides agree on the wire bytes. The rule survives as a human discipline; D-23's note must say so |
| Documentation lives only in the `firestarter_prom` wiki; no automated wiki guard exists | same §"Repository Structure" | The verdict note goes in `.planning/notes/`, not the wiki |

---

## Metadata

**Confidence breakdown:**

- Deletion inventory — **HIGH.** All 46 paths probed for existence with line counts; the three naming conventions resolved exhaustively; one unnamed test file and two orphaned data files surfaced.
- Dangling-reference sweep — **HIGH.** `git grep` across all three repos, every hit classified as breaking vs inert, breakage counted per module by `pytest --co`. This is the section that most changes the plan.
- Fixture ownership — **HIGH.** Every candidate mapped to consumers; the mention-vs-load distinction checked by reading each ambiguous site.
- CI workflow edits — **HIGH.** Every line range read live; two firmware pairs found that CONTEXT.md does not name.
- Firmware baseline arithmetic — **HIGH.** Both native envs run, the suite's 6 cases counted at source, the AVR premise verified by a cold build matching the pin, and the re-record's RED leg reproduced against a simulated baseline.
- Catalog strip — **HIGH.** Byte-identity hashed, and the output-neutrality of the strip proven by a falsification attempt with pasted output.
- Citation sweep — **MEDIUM.** The hits are measured exactly; the *scope boundary* (requirement IDs, `--help` strings) is a judgement the operator may narrow — hence Q2.
- Acceptance gates — **HIGH.** Every one executed; two failure signals reproduced by planting; one D-19 command found to be un-runnable as worded.
- Coverage risk — **HIGH.** Two full suite runs, 13 minutes of wall clock, decisive.

**Research date:** 2026-09-12
**Valid until:** 2026-09-19 — the tree is under active modification (an uncommitted `config.json` change is already present) and a single commit to any of the three repos can move a line number. Re-verify the four CI line ranges and the `size_baseline.json` line numbers immediately before editing.
