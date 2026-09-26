# Phase 175: Structural Sentinel over `derive_plan` - Research

**Researched:** 2026-09-04
**Domain:** Python test engineering — relational predicates over a pure planning function, whole-database sweeps, fail-closed vocabulary closures
**Confidence:** HIGH (every number below re-measured this session in the py3.11 CI-replica venv; every code claim read from source with a line range)

**Measurement environment (all figures below unless marked otherwise):**
`/workspaces/firestarter_app/.venv311/bin/python` — **Python 3.11.16**, pytest 9.1.1, editable install resolving to `/workspaces/firestarter_app/firestarter/__init__.py`. `firestarter_app @ c134530`, branch `gsd/v1.36-dev-test-fidelity`, working tree clean in both repos at measurement time. [VERIFIED: `./.venv311/bin/python -V`; `git rev-parse --short HEAD`; `git status --porcelain`]

---

## Summary

Everything CONTEXT.md's twelve decisions ask for is buildable test-side with stdlib + pytest, against shipped idioms this tree already carries. The measured shipped corpus is clean: **zero write-without-verify violations across all 1,354 plans**, **zero step/result misalignments across the whole `run_plan` sweep**, and **every UV structural pin holds on all 270 UV chips**. Two mutated-corpus sensitivity legs and a field-skew leg each flag **1,354 / 1,354** plans, so anti-vacuity is not merely arguable, it is measured.

Three findings materially change the plan, and the planner must act on all three.

**Finding 1 — D-05's erase leg is RED on 162 plans if "blank-check" is read as "*supported* blank-check."** 81 algorithm-`0x0D` (28C-family) chips emit a genuinely executable `OP_ERASE` followed at a higher index by an `OP_BLANK_CHECK` that is `supported=False`, carrying the reason `"protocol 0x0D (28C family) auto-erases per page during write; no step in this plan can ever leave the device blank"`. This is deliberate, already-pinned product behaviour, not a defect. The leg must be worded as *presence at a higher index in the same cycle block*, with the NA-blank-check population carved out by a named, counted reason — otherwise the executor meets a RED it cannot fix without touching product code, which this phase forbids.

**Finding 2 — the cost numbers from discussion are wrong in both directions.** The `run_plan` half is **~35–46 s**, not ~21 s (median ~37 s over three trials). The full app suite is **302 s**, not 737 s. So the execution half costs **~12 %** of the suite, not ~3 %. And `test_flash_path_record_sync` — the porcelain-asserting test the brief warns about — **is not in `firestarter_app` at all**; it lives in the firmware repo (`/workspaces/firestarter/tests/test_flash_path_record_sync.py`). The app suite has no whole-repo-porcelain gate.

**Finding 3 — the exemption-with-reasons partition D-01 asks for already ships, in a different registry.** `tests/test_op_registration_parity.py` is a total, fail-closed `(op, registry) → member-or-reasoned-exemption` gate over the same 13-op vocabulary, with empty-reason and stale-row guards and a non-vacuity leg. The new sentinel is a *new axis on an existing pattern*, not a new pattern. That module also carries `assert len(_ALL_OPS) == 13` at import time, so a 14th `OP_*` already fails collection there — useful context for how much the new closure adds.

**Primary recommendation:** Build one new test module `firestarter_app/tests/test_derive_plan_structural_sentinel.py` plus one committed artifact `firestarter_app/tests/fixtures/plan_shapes.json` and its generator `firestarter_app/tools/measure_plan_shapes.py`, copying `test_op_registration_parity.py`'s exemption-table shape for the closure, `test_erase_flag_invariants.py`'s two-level `_all_rows` selector for the sweep, and `test_part_number_delta_drift.py` + `tools/measure_part_number_delta.py` for the artifact/generator/drift triple. Use `dataclasses.replace(plan, steps=[...])` for every mutation. Split the ~37 s `run_plan` sweep into its own module so it can be deselected by path if the planner decides the 12 % is too much.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Write→verify relational predicate | Test suite (`tests/`) | — | D-06 keeps the classification test-side; `derive_plan` is a pure function and the predicate reads only its output |
| `OP_*` vocabulary closure | Test suite (`tests/`) | — | `Step.op` is a bare `str`, so no type checker can see an omission; runtime set-difference is the only route |
| Cycle-block determination | Product (`chip_test.cycle_block_bounds`) | Test (caller only) | D-02: the block rule is production-owned; the test must call it, never re-derive it |
| Frozen plan-shape pin | Committed artifact (`tests/fixtures/`) | Generator (`tools/`) | `chip_database.json` is GENERATED; the drift-test triple is this tree's shipped answer (D-16 precedent) |
| Step/result alignment proof | Test suite, via `run_plan` + operator double | — | Requires the dispatch layer; a mocked `EpromOperator` is the only hardware-free path |
| UV write-scope ceiling | Test suite, two levels: `derive_plan` output **and** `cli_handlers._resolve_write_scope` | — | D-12: the `derive_plan` pins stay true even if the handler line flips; only the handler leg guards the ceiling |
| Anti-vacuity | Test suite (planted plan + mutated corpus) | — | D-09 |

---

<user_constraints>
## User Constraints (from CONTEXT.md)

**The planner reads `175-CONTEXT.md` in full. This section is a pointer, not a restatement — CONTEXT.md is authoritative and every decision in it is LOCKED.** Named here only so nothing below is mistaken for a re-litigation:

### Locked Decisions
D-01 (total fail-closed `OP_*` partition), D-02 (same-cycle-block via the shipped `cycle_block_bounds`), D-03 (verify must be `supported=True`), D-04 (verify matches write on `write_region`, `region_policy`, `cycle_payload`), D-05 (erase→blank-check as a separately-named leg), D-06 (classification lives test-side, cross-checked against `vars(chip_test)`), D-07 (`EpromDatabase(skip_local_override=True)` only; closes REQUIREMENTS D-8), D-08 (scopes `"full"` and `"partial"`), D-09 (planted counter-plan **plus** mutated-corpus sweep), D-10 (both halves of the no-drop proof), D-11 (a database-regeneration redden is signal), D-12 (the `aq6` UV ceiling stands and is pinned, including the handler-level leg).

### Claude's Discretion (treated as locked per CONTEXT.md)
D-04's three-field set; **no re-key**; anti-vacuity must be *seen* RED; all measurement in the py3.11 CI-replica venv; no new library (HYG-02); `/usr/bin/grep` for gate evidence; no comments in source; module in `firestarter_app/tests/`, artifact in `firestarter_app/tests/fixtures/`; no sentinel over `Plan.locked_destructive`.

### Deferred Ideas (OUT OF SCOPE)
The stale `cli_handlers.py` comment (see §J — **file the todo, do not fix**); re-reversing `aq6`; a `Plan.locked_destructive` sentinel; whether the sweep is marked slow (planner call — see §E); the fault-mode table (Phase 177); `--fast` coverage (structurally impossible here).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **PRUNE-05** | Unsupported steps keep their `StepResult` with an NA verdict; only the work is skipped. They are **not** dropped from `Plan.steps` — 637 of 677 chips carry six `supported=False` SDP steps and they are hash ballast, not waste. | §D-10 halves both measured green: frozen half = **8 shape families** over 677 chips (§F); execution half = **1,354/1,354 aligned, 9,304/9,304 unsupported steps carry `NA`** (§E). Note the requirement's "637 of 677" figure is *not* what I measure — see §Common Pitfalls, Pitfall 6. |
| **PRUNE-06** | A structural test over `derive_plan` output fails when a plan emits a write with no verify behind it. Expressed as a relational predicate over `Plan.steps`, not a self-declared per-step annotation, and carrying anti-vacuity legs including a planted counter-example. | §Code Examples gives the predicate; §D gives three mutation legs each flagging 1,354/1,354; §B gives the total partition and its measured 13-op closure; §C gives `cycle_block_bounds`' real behaviour under every shipped shape and six edge shapes. |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md`, the directives that bind this phase:

| Directive | Source | Bearing on this phase |
|---|---|---|
| `firestarter/data/chip_database.json` is **generated — do NOT edit by hand** | `firestarter_app/CLAUDE.md` | The frozen pin reddening on regeneration is expected (D-11); the fix is to regenerate the artifact, never to edit the database |
| Constants/flag bits duplicated Python↔C++ must change together | `/workspaces/CLAUDE.md` | Inert here: the phase adds no constant to `constants.py` and touches no product file |
| Serial-protocol changes must stay in sync across `serial_comm.py` / `firestarter.cpp` | `/workspaces/CLAUDE.md` | Inert: the sweep never opens a port |
| `main` is protected in all three repos; this project's base branch is `beta` | `/workspaces/CLAUDE.md` | Phase work lands on `gsd/v1.36-dev-test-fidelity` in **both** the meta repo and the `firestarter_app` submodule |
| Meta repo tracks `.planning/`; `firestarter_app` is a separate repo | both | Test code + artifact + generator commit **inside** `firestarter_app`; evidence transcripts commit in the **meta** repo (§H) |

**Additional standing project rules that constrain this phase** (from the operator memory record, and reconfirmed against the tree this session):
- **No comments in source, at all** — docstrings are exempt. Every explanation in the new module goes in a docstring. Confirmed as the house style in the modules cited below, which are almost entirely docstring-carried.
- `grep` in this devcontainer is **ugrep 7.8.4** and honors `.gitignore`. [VERIFIED: `grep --version` → `ugrep 7.8.4 x86_64-pc-linux-gnu`] Use `/usr/bin/grep` or a `bash script.sh` for anything that becomes gate evidence.
- pytest `addopts = "-ra -q"`. [VERIFIED: `firestarter_app/pyproject.toml:107`, verbatim `addopts = "-ra -q"`] A second `-q` suppresses the count line — pass `-o addopts=""` when counts are needed.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pytest` | **9.1.1** (installed in `.venv311`) | The whole harness | Already the project's only test runner [VERIFIED: `./.venv311/bin/python -c "import pytest; print(pytest.__version__)"` → `9.1.1`] |
| `dataclasses` (stdlib) | py3.11 | `replace()` for corpus mutation | `Plan` and `Step` are plain `@dataclass`; `replace` is the only copy idiom that yields a fresh `steps` list without touching shared `Step` objects (§D) |
| `unittest.mock.Mock` (stdlib) | py3.11 | `EpromOperator` double | The shipped `_mock_operator` idiom uses `Mock(spec=[...])` |
| `json` (stdlib) | py3.11 | Frozen artifact I/O | Matches `tests/fixtures/part_number_delta.json` / `shape_ids.json` |
| `copy` / `collections` (stdlib) | py3.11 | Census + mutation helpers | — |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `argparse` (stdlib) | py3.11 | Generator CLI (`--check`) | Only if the planner takes the artifact-plus-generator route (§F) |
| `subprocess` (stdlib) | py3.11 | Drift test regenerates into a tempdir and diffs | Mirrors `tests/test_part_number_delta_drift.py` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Runtime set-difference closure | `assert_never` over `Enum`/`Literal` + mypy | **Closed here.** `Step.op` is a bare `str` [VERIFIED: `firestarter_app/firestarter/chip_test.py:406-445`, field declared verbatim as `    op: str`] and the vocabulary is 13 module-level `str` constants. CONTEXT D-06 already records this; measurement confirms it. |
| A new test module | A new registry row inside `test_op_registration_parity.py` | Tempting (§A) but rejected: that module's registries are all **product-side** containers in `chip_test.py`, and its `_POLICED_REGISTRY_COUNT = 7` is measured by AST against product source. A test-side verify-disposition table is a different axis. Keep it separate per D-06. |
| `copy.deepcopy(plan)` | — | Unnecessary and ~2 orders slower over 1,354 plans; `dataclasses.replace` suffices because no `Step` is mutated (§D) |
| `hypothesis` | — | **Forbidden.** `.planning/REQUIREMENTS.md` §"Out of Scope" lists `hypothesis`, `jsonschema`, `pydantic`, `jcs`/RFC 8785 as "Measured unnecessary." |

**Installation:** none. **No package is added by this phase.**

**Version verification:** the phase installs nothing, so no registry lookup applies. The two versions above are read from the already-installed CI-replica venv.

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.** HYG-02 is milestone-wide (stdlib + pytest only) and CONTEXT.md's discretion block restates it. The `## Standard Stack` table names only `pytest` (already a declared `[test]` extra) and Python standard-library modules. No `[SLOP]`, `[SUS]` or `[ASSUMED]` package name appears anywhere in this document.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

---

## A. Existing-Test Collision Survey

Scanned with `/usr/bin/grep` over `firestarter_app/tests/*.py` and `tests/fixtures/*.py`. [VERIFIED: `/usr/bin/grep -c "OP_[A-Z_]*"` per file; `/usr/bin/grep -rln "\.proms" tests/*.py`; `/usr/bin/grep -rn "derive_plan" tests/`]

### (i) Modules reading `OP_*` from `firestarter.chip_test`

| Module | `OP_*` refs | `derive_plan` calls | Verdict for the new sentinel |
|---|---:|---:|---|
| `tests/test_chip_test.py` | 157 | 138 | **Overlaps in kind, never in scope.** Single-chip assertions (`M8720`, `M27C512`, `AT28C256`, `W27C512`, `AM27C020`, `W29C040`). The new sweep is a strict generalization. One direct near-duplicate: `:2612` asserts `len(results) == len(plan.steps)` for **one** chip — see (ii). |
| `tests/test_chip_test_sdp_leg.py` | 154 | 30 | **The closure template.** `test_shipped_ops_never_reach_sdp_arm` (`:827`) is the `vars(chip_test)` idiom D-01/D-06 copy. No collision: it partitions ops by *dispatch arm*, not by verify-disposition. |
| `tests/test_op_registration_parity.py` | 100 | 14 | **Closest structural collision — see below.** |
| `tests/test_erase_flag_invariants.py` | 44 | 3 | **The sweep template.** Whole-DB, two-level `_all_rows`. Its legs 5/6 pin AT28C256's `full` and `none` op orders — a two-chip subset of the new frozen pin. Not a collision; the new pin covers it and 676 more. |
| `tests/test_chip_test_blank_check_order.py` | 19 | 7 | **Direct precedent for D-05 and for D-12's blank-check-index pin.** Four named chips. `test_at28c256_blank_check_moves_after_erase_but_stays_na` (`:130`) already pins Finding 1's exact case for one chip. Genuinely new: the whole-DB generalization + the 81-chip carve-out count. |
| `tests/test_devtest_firmware_error_propagation.py` | 9 | 0 | No overlap (error-code propagation). |
| `tests/test_dev_test_cmd.py` | 6 | 8 | Contains `TestUVWriteHasNoPrompt` — see below. |
| `tests/test_chip_test_cycle.py` | 5 | 5 | No overlap. **Caution:** its `_REAL_DB` is `EpromDatabase()` **without** `skip_local_override=True` [VERIFIED: `tests/test_chip_test_cycle.py:24`]. Do not copy that line. |
| `tests/test_revision_constants_parity.py`, `tests/test_write_progress.py`, `tests/test_hardware.py`, `tests/test_diagnostic_report.py`, `tests/fixtures/synthetic_nonzero_chip_id.py` | 1–5 each | — | Incidental references. No overlap. |

**`tests/test_op_registration_parity.py` — the structural collision, in detail.**
This module already implements exactly the shape D-01 describes, on a different axis:
- `_ALL_OPS` is built from `vars(chip_test_mod)` with the same three-line idiom [VERIFIED: `tests/test_op_registration_parity.py:136-141`].
- `_OP_REGISTRY_EXEMPTIONS: dict[tuple[str, str], str]` maps `(op, registry)` to a **prose reason** [VERIFIED: `:456`].
- `test_exemption_empty_reason_fails` (`:821`) rejects an empty/whitespace/None reason.
- `test_stale_row_fails` (`:843`) rejects an exemption naming a vanished op or registry.
- `test_altered_registry_copy_fails_parity_non_vacuous` (`:903`) is the mutated-copy anti-vacuity leg.

**Does the new sentinel collide?** No, and it cannot make this module RED. `_POLICED_REGISTRIES` holds only product-side containers plus three AST-derived reference sets [VERIFIED: `:269-279`, keys `_DESTRUCTIVE_OPS`, `_MULTI_RUN_OPS`, `_SDP_OPS`, `_SDP_LEG_OPS`, `_dispatch_step`, `derive_plan`, `_dispatch_multi_run`], and `_POLICED_REGISTRY_COUNT = 7` [VERIFIED: `:295`]. A table living in a *test* module is invisible to it.

**The one thing the planner must know about it:** it carries a hard import-time count pin —
```
assert len(_ALL_OPS) == 13, (
    f"measured {len(_ALL_OPS)} OP_* string constants in chip_test.py, "
    "expected 13 -- the census baked into this module's docstring and "
    "_POLICED_REGISTRIES/_OP_REGISTRY_EXEMPTIONS needs re-measuring"
)
```
[VERIFIED: `tests/test_op_registration_parity.py:186-190`, quoted verbatim]. So a 14th `OP_*` already breaks **collection** of that module. The new closure's added value is therefore not "catch a new op" (already caught) but "**say what the new op's verify-disposition is**" — which is precisely CONTEXT's "the exemption bucket is where the thinking is." State that in the new module's docstring so a later reader does not delete the closure as a duplicate.

### (ii) Tests asserting an op sequence or step count

| Site | What it pins | Relation to the new work |
|---|---|---|
| `tests/test_chip_test.py:2612` | `assert len(results) == len(plan.steps)` for `M8720` @ `write_scope="full"` | **The nearest duplicate of PRUNE-05's execution half — for one chip.** The sweep generalizes it 1,354×. Keep both; the single-chip one is fast and named. |
| `tests/test_chip_test_sdp_leg.py:276-324` | `_SHIPPED_OPS_SEQUENCE` — `["id","read","blank-check"]`, per-step `(verdict, run_count)`, `len_results: 3`, for `M8720` @ `write_scope="none"` | Different scope (`"none"`, excluded by D-08). No collision. |
| `tests/test_chip_test_sdp_leg.py:892` | `len(results) == len(_SHIPPED_OP_STRINGS)` under the widened-`_SDP_OPS` sentinel | Hand-built plan, not a DB plan. No collision. |
| `tests/test_erase_flag_invariants.py:289-303, 339-371` | AT28C256 `full` and `none` op orders, element-wise | Subset of the new frozen pin. |
| `tests/test_chip_test.py:678-752` | Op lists for `write_scope` `none`/`full`/`partial` on named chips | Subset. |
| `tests/test_chip_test.py:1453-1476` (`test_cycle_block_bounds_matches_each_family_plan_shape`) | `cycle_block_bounds` block contents for `M8720`, `W27C512`, `M27C512`, `W29C040`, plus "the SDP leg is never swallowed" | **Directly relevant to D-02.** Four chips. The new work must not restate it; cite it and generalize. |
| `tests/test_chip_test_blank_check_order.py:75-190` | Blank-check placement, four chips, five legs | Subset of D-05 + D-12's index pin. |

### (iii) UV region policy / `_resolve_write_scope`

| Site | What it pins |
|---|---|
| `tests/test_chip_test.py:855-877` | `M27C512` only: at `full` — `region_policy == REGION_POLICY_UV_SLOT`, `write_region == (65280, 256)`, verify likewise, `full_device_permitted is True`; at `partial` — same region, `full_device_permitted is False` |
| `tests/test_chip_test.py:968-979` | `plan.is_uv` for exactly four chips: `M27C512` True, `AM27C020` True, `W27C512` False, `AT28C256` False |
| `tests/test_chip_test.py:879-891` | SDP-leg steps keep `REGION_POLICY_FIXED` and `_DEFAULT_REGION` at `full` (AT28C256) |
| `tests/test_diagnostic_report.py:1354, 1374` | `coverage_tag` behaviour for `REGION_POLICY_UV_SLOT` — report layer, not `derive_plan` |
| `tests/test_uv_mask.py:98-116` | `uv_slot_starts` top-down ordering/count — helper level |
| `tests/test_check_devtest_orchestrator.py:496-577` | That `_resolve_write_scope` and `_is_uv_eprom` are on the orchestrator checker's `_HANDLER_FUNCTION_NAMES` allow-list — a *name* pin, not a *behaviour* pin |

**`TestUVWriteHasNoPrompt` — exactly what it already pins** [VERIFIED: `tests/test_dev_test_cmd.py:708-801`, five methods read in full]:

1. `test_no_prompt_on_a_uv_part_even_on_a_tty` — **structural, not behavioural**: `not hasattr(cli_handlers_mod, "Confirm")` and `not hasattr(cli_handlers_mod, "_default_uv_write_confirm")`. It asserts two names are absent from the module namespace. It says nothing about what `_resolve_write_scope` returns.
2. `test_uv_part_writes_one_slot_on_a_tty` — end-to-end through `CliRunner` for **one** chip, `_CHIP_UV = "AM27512"` [VERIFIED: `tests/test_dev_test_cmd.py:104`], with `_is_interactive` patched True; asserts `"write-partial" in {s["op"] for s in data["steps"]}` **read back from a persisted report file**.
3. `test_uv_part_writes_one_slot_off_a_tty_too` — the same one chip, off-TTY, same assertion.
4. `test_non_uv_part_is_still_written_in_full_without_a_prompt` — **one** chip, `_CHIP_NO_ID = "M8720"` [VERIFIED: `:96`]; asserts `"write" in ops` and `"write-partial" not in ops`.
5. `test_write_scope_resolver_needs_no_confirm_callable` — `inspect.signature(_resolve_write_scope).parameters` has no `confirm_fn` and equals exactly `{"app", "chip", "interactive"}`.

**So the new handler leg must NOT restate:** the absence of `Confirm`/`_default_uv_write_confirm`; the exact parameter-name set of `_resolve_write_scope`; or the TTY-invariance of the outcome. Those are legs 1, 5 and 2-vs-3 and they are complete.

**What the new leg adds, and it is the whole of D-12's "leg that matters":** `TestUVWriteHasNoPrompt` never calls `_resolve_write_scope` for its **return value**, and covers exactly **two** chips end-to-end. The new leg calls the function directly over **all 677 part numbers** and asserts `"partial"` for all **270** UV rows and `"full"` for all **407** non-UV rows. Phrase its docstring as "extends `TestUVWriteHasNoPrompt` from two named chips to the whole database, and from the report's rendered op string to the resolver's own return value" so the relationship is explicit and neither test is later deleted as redundant.

### (iv) Whole-database sweeps that already exist

| Module | Selector | Calls `derive_plan`? |
|---|---|---|
| `tests/test_erase_flag_invariants.py` | `_all_rows` / `_select_algorithm_13_rows`, two-level descent over `db.proms` | Only for AT28C256 (2 calls) |
| `tests/test_eprom_database.py` | `.proms` (5 refs) | No |
| `tests/test_wire_dict_equivalence.py` | `.proms` (1 ref) | No |
| `tests/test_sdp_db_invariant.py` | Whole-DB, 84-row + 43/41 partition sweeps | No |
| `tests/test_page_size_invariants.py` | Whole-DB, all-746-row sweeps | No |

**No whole-database `derive_plan` sweep exists today.** [VERIFIED: cross-product of the `\.proms` grep and the `derive_plan` grep is empty except for AT28C256's two calls.] Every plan-shape assertion in the tree is single-chip or four-chip. The new sweep is therefore genuinely new and cannot collide with an existing sweep.

**Definitive collision verdict:** nothing the new sentinel does duplicates an existing test's *coverage*. Three modules supply *patterns* to copy. One assertion (`test_chip_test.py:2612`) is a one-chip instance of one new leg and should be left alone.

---

## B. The Op Vocabulary, Enumerated

**13 `OP_*` module-level string constants, all `str`, none non-`str`.** [VERIFIED: `./.venv311/bin/python -c "import firestarter.chip_test as ct; ops={n:v for n,v in vars(ct).items() if n.startswith('OP_')}"` — count 13, `isinstance(v, str)` True for all 13, non-str set empty]

| Constant | Value | Source | Bucket | Reason (one line, for the exemption table) |
|---|---|---|---|---|
| `OP_ID` | `"id"` | `chip_test.py:314` | **exempt** | Read-only identity compare; changes no device state, so there is nothing for a verify to confirm. |
| `OP_READ` | `"read"` | `:315` | **exempt** | Read-only; the step's own output *is* its result. |
| `OP_BLANK_CHECK` | `"blank-check"` | `:316` | **exempt** | Read-only, and itself an oracle (it is `OP_ERASE`'s, per D-05) — an oracle does not need an oracle. |
| `OP_WRITE` | `"write"` | `:317` | **requires-verify** | Mutates memory contents; a write with no read-back comparison has no oracle at all. |
| `OP_WRITE_PARTIAL` | `"write-partial"` | `:318` | **requires-verify** | Same mutation, narrower window; the window is on `write_region`, not on the op's obligation. |
| `OP_VERIFY` | `"verify"` | `:319` | **exempt** | It *is* the oracle; the firmware compares on-device. |
| `OP_ERASE` | `"erase"` | `:320` | **exempt from write→verify, carries its own D-05 leg** | Mutates by clearing, not by staging bytes; a verify has no expected buffer to compare against. Its oracle is the blank-check `derive_plan` relocates behind it. |
| `OP_SDP_LOCK` | `"sdp-lock"` | `:329` | **exempt** | Changes protection state, not memory contents; SDP state is not readable back on this family. Its oracle is the subsequent `write-inhibited` read-back. |
| `OP_SDP_UNLOCK` | `"sdp-unlock"` | `:330` | **exempt** | Same, inverse; its oracle is the subsequent `write-restored` read-back. |
| `OP_WRITE_BASELINE_B` | `"write-baseline-b"` | `:341` | **exempt** | SDP-leg write; `_dispatch_sdp_leg` performs its own read-back-equality check inline — there is no `OP_VERIFY` step for it, by design. |
| `OP_WRITE_BASELINE_A` | `"write-baseline-a"` | `:342` | **exempt** | Same; the two directions together are what distinguishes a dead write path from a chip already holding the pattern. |
| `OP_WRITE_INHIBITED` | `"write-inhibited"` | `:343` | **exempt — load-bearing** | The read-back *is* the oracle **and it expects inequality**. `_dispatch_sdp_leg` sets `source_payload, expected_readback, flags = (pattern_b, pattern_a, FLAG_SKIP_SDP_UNLOCK)` [VERIFIED: `chip_test.py:3291-3296`, quoted verbatim below]. An `OP_VERIFY` asserts the written bytes *took* — the exact opposite of this step's intent. A naive predicate does not merely over-fire here; it would demand a step that inverts the test. |
| `OP_WRITE_RESTORED` | `"write-restored"` | `:344` | **exempt** | SDP-leg write with `expected_readback = pattern_a`; same inline read-back oracle. |

Verbatim from `firestarter_app/firestarter/chip_test.py:3291-3298`:
```python
    elif op == OP_WRITE_INHIBITED:
        source_payload, expected_readback, flags = (
            pattern_b,
            pattern_a,
            FLAG_SKIP_SDP_UNLOCK,
        )
    elif op == OP_WRITE_RESTORED:
        source_payload, expected_readback, flags = pattern_a, pattern_a, 0
```

**Partition arithmetic:** 2 requires-verify + 11 exempt = 13 = `len(module_op_constants)`. The two buckets are disjoint. Both properties are runtime-assertable.

**Cross-check against the module's own registries** [VERIFIED: read from the live module this session]:
```
_DESTRUCTIVE_OPS      = ['erase', 'sdp-lock', 'write', 'write-baseline-a', 'write-baseline-b',
                         'write-inhibited', 'write-partial', 'write-restored']   (8)
_MULTI_RUN_OPS        = ['erase', 'verify', 'write', 'write-partial']            (4)
_SDP_OPS              = ['sdp-lock', 'sdp-unlock']                               (2)
_SDP_LEG_OPS          = ['write-baseline-a', 'write-baseline-b',
                         'write-inhibited', 'write-restored']                    (4)
_SDP_BASELINE_OPS     = ['write-baseline-a', 'write-baseline-b']                 (2)
_SDP_LEG_GATED_OPS    = ['sdp-lock', 'sdp-unlock', 'write-inhibited',
                         'write-restored']                                       (4)
_CYCLE_BLOCK_OPS      = ['blank-check', 'erase', 'verify', 'write', 'write-partial'] (5)
_CYCLE_BLOCK_START_OPS= ['write', 'write-partial']                               (2)
```
Note `requires-verify` == `_CYCLE_BLOCK_START_OPS` **by value today**. Do **not** derive the bucket from that set — CONTEXT D-01 rejects derivation by subtraction for exactly this reason, and `_CYCLE_BLOCK_START_OPS` could be widened for an ordering purpose unrelated to oracles. Declare the two buckets literally, then assert the union/disjointness against `vars(chip_test)`.

### Is there a hole in `vars()` discovery?

**No — measured, not assumed.** Two AST scans of `chip_test.py`:

1. **Module-level `str` constants not named `OP_*`: 27, and not one has a value colliding with an op value.** [VERIFIED: `ast.parse` over `inspect.getsourcefile(ct)`, `ast.literal_eval` on every module-level `Assign`/`AnnAssign`] They are `COVERAGE_TAG_FULL_DEVICE`, `CYCLE_PAYLOAD_{ALTERNATE,SAME,UV_TRANCHE}`, `FP_{ADDRESS_LINE,BLANK_CONTACT,INDETERMINATE,TRANSPORT}`, `REGION_POLICY_{FIXED,FULL_DEVICE,UV_SLOT}`, `REPEAT_POLICY_DEGRADED_TAG`, `SDP_HOLD_{HELD,NOT_HELD,NOT_RUN}`, `VERDICT_{BAD,MARGINAL,NA,OK,SKIPPED}`, `_DESTRUCTIVE_GATE_REASON`, `_SDP_BASELINE_GATE_REASON`, `_SDP_LOCKED_REASON`, `_SDP_UNLOCK_GATE_REASON`, `_WRITE_SCOPE_{FULL,NONE,PARTIAL}`. None is op-like in value.
2. **Zero `Step(op=<string literal>)` call sites.** Every `op=` keyword argument in a `Step(...)` construction is an `ast.Name` identifier. [VERIFIED: `ast.walk` over every `ast.Call` with `func.id == "Step"`]

**One caveat the planner must handle.** `run_plan` constructs a `StepResult` with a bare literal on its guard path:
```python
            StepResult(
                op="__plan__",
```
[VERIFIED: `firestarter_app/firestarter/chip_test.py:1633-1634`, quoted verbatim]. This is a `StepResult`, never a `Step`, so it is outside the `Plan.steps` predicate's domain — but it means **`len(results)` can be 1 while `len(plan.steps)` is 12** when `runs < 2` without `allow_single_run=True`. The alignment sweep must use `run_plan`'s default `runs=2` (or pass `allow_single_run=True` deliberately) or it fails for a reason that has nothing to do with PRUNE-05. Both variants were measured green (§E).

---

## C. `cycle_block_bounds` Semantics Under Every Shape

**Measured, not read from the docstring.** [VERIFIED: sweep over all 1,354 shipped `full`+`partial` plans plus eight hand-built shapes]

### The shipped shapes — four op-sequences, two block shapes

| n (plans) | Op sequence | `cycle_block_bounds` | Block contents |
|---:|---|---|---|
| 373 | `id, read, blank-check, write, verify, erase, ` + 6 SDP | **`(3, 6)`** | `['write', 'verify', 'erase']` |
| 373 | `id, read, blank-check, write-partial, verify, erase, ` + 6 SDP | **`(3, 6)`** | `['write-partial', 'verify', 'erase']` |
| 304 | `id, read, write, verify, erase, blank-check, ` + 6 SDP | **`(2, 6)`** | `['write', 'verify', 'erase', 'blank-check']` |
| 304 | `id, read, write-partial, verify, erase, blank-check, ` + 6 SDP | **`(2, 6)`** | `['write-partial', 'verify', 'erase', 'blank-check']` |

**Exactly 4 distinct op-sequences across the whole database at `full`+`partial`** — CONTEXT's figure confirmed. Every plan has exactly 1 write, 1 verify, 1 erase and 1 blank-check step. [VERIFIED: `Counter(...)` over all 1,354 plans → `{1: 1354}` for each of the four ops]

**The docstring is accurate but incomplete for this purpose.** It lists four *families* — `erasable`, `UV`, `flash4`, `SRAM/FRAM` — as
```
    * erasable  -- `id, read, [write, verify, erase, blank-check], sdp x6`
    * UV        -- `id, read, blank-check, [write, verify], sdp x6`
```
[VERIFIED: `firestarter_app/firestarter/chip_test.py:1236-1252`, quoted verbatim]. **The UV/flash4/SRAM shapes shown without an `erase` inside the block are what the block looks like when NA steps are ignored — but `derive_plan` emits the erase step anyway, as `supported=False`, and `cycle_block_bounds` does not filter on `supported`.** So the real UV block is `(3, 6)` = `['write', 'verify', 'erase']`, with `erase` NA. Planning from the docstring alone would produce a predicate that assumes the block is 2 wide on UV parts.

### The edge cases

| Shape | `cycle_block_bounds` | What the predicate must do |
|---|---|---|
| `write_scope="none"` (no write step) — all 677 plans | **`None`** [VERIFIED: `Counter(...)` over all 677 `none`-scope plans → `{None: 677}`] | Vacuously satisfied. Out of scope per D-08 anyway. |
| Empty `steps` list | `None` | Same. |
| `['id','read','blank-check']` (no write) | `None` | Same. |
| `['id','read','write(NA)','verify','erase']` — **write is `supported=False`** | **`(2, 5)`** | The block **opens on an unsupported write**. `cycle_block_bounds` reads only `step.op`. The predicate must decide explicitly whether an NA write requires a verify. **Recommendation: skip NA writes** (a step that never calls the operator cannot be a write with no oracle), and *say so in a docstring* — the shipped corpus has **zero** unsupported `OP_WRITE`/`OP_WRITE_PARTIAL` steps [VERIFIED: count 0 over 1,354 plans], so this arm is currently unreachable and would otherwise be an unexercised, unexplained branch. |
| `['id','read','write','erase']` — **block with no verify** | `(2, 4)` | Violation. This is the hand-built counter-plan's shape (D-09). |
| `['write']` alone | `(0, 1)` | Violation — block is 1 wide, contains no verify. |
| `['verify','write']` — verify at a *lower* index | `(1, 2)` | Violation. Confirms "at a higher index" is load-bearing, not decorative. |
| `['write','sdp-lock','verify']` — verify outside the block | **`(0, 1)`** | Violation. Confirms D-02 beats "anywhere-later in `Plan.steps`". |
| `['write','verify','sdp-lock','write','verify']` — **two writes, second outside the block** | **`(0, 2)`** | **The hole the planner must close.** `cycle_block_bounds` finds only the **first** maximal run. The second write at index 3 is outside `[0, 2)` entirely. **The predicate must treat "this write is not inside the returned block" as a violation** (fail-closed), never as "no block applies, skip." Unreachable on the shipped corpus today (every plan has exactly one write), which is precisely why it must be coded fail-closed and covered by a hand-built leg. |

**No shipped shape has a block without a verify.** [VERIFIED: 0 violations over 1,354 plans under the full predicate.]

---

## D. The Mutated-Corpus Leg, Concretely

`Plan` and `Step` are both plain, **mutable**, non-frozen `@dataclass`es. [VERIFIED: `dataclasses.fields(...)`; `p.steps[0].op = "x"` succeeds without raising]
```
Plan fields: ['name', 'steps', 'reason', 'locked_destructive', 'is_uv']
Step fields: ['op', 'supported', 'reason', 'destructive', 'write_region',
              'cycle_payload', 'region_policy', 'full_device_permitted']
```

### The cheapest correct copy

```python
import dataclasses

def _without_verify(plan):
    return dataclasses.replace(plan, steps=[s for s in plan.steps if s.op != OP_VERIFY])
```

Measured properties [VERIFIED, all four in one run]:
- `mutant.steps is plan.steps` → **False** (fresh list — the shared-list trap is avoided).
- `mutant.steps[0] is plan.steps[0]` → **True** (Step objects are shared — fine, because the list comprehension never *mutates* a Step).
- `mutant.is_uv` and `mutant.name` are preserved (`False`, `"AT28C256"`).
- Re-deriving the same plan afterwards is unaffected.

**`copy.copy(plan)` shares the `steps` list** (`c.steps is p.steps` → **True**) [VERIFIED]. Do not use it, and do not use `copy.deepcopy` (unnecessary and far slower over 1,354 plans).

**The rule that must be in the plan, because it is Phase 174's own CR-01 defect wearing new clothes:** for any mutation that changes a *field* rather than list membership, build a new `Step` with `dataclasses.replace(step, ...)`. Never assign to a `Step` attribute in place — the corpus fixture is module-scoped and shares those objects, so an in-place edit silently corrupts every later test in the module. Phase 174's gap-closure plan `174-06` fixed exactly this shape ("CR-01, the three frozen shapes sharing one mutable `results` list").

### Sensitivity, measured

Plans in the corpus containing a supported write: **1,354 of 1,354** (every `full`/`partial` plan has exactly one). [VERIFIED]

| Mutation | Flagged | Rate |
|---|---:|---|
| Remove the `OP_VERIFY` step entirely | **1,354 / 1,354** | 100 % |
| Set the verify's `supported=False` (via `dataclasses.replace`) — tests **D-03** | **1,354 / 1,354** | 100 % |
| Skew the verify's `write_region` by +1 on the start — tests **D-04** | **1,354 / 1,354** | 100 % |
| Remove the `OP_BLANK_CHECK` step, over the 608 plans with an executable erase — tests **D-05** | **608 / 608** | 100 % |

An empty sweep is therefore impossible to pass silently: the mutated leg asserts a **non-zero, exactly-equal** flagged count against the corpus size, which a zero-row sweep fails on both sides.

---

## E. The `run_plan` Half — Real Cost and Hazards

### Cost — the discussion figure is roughly half the truth

| Measurement | Value |
|---|---|
| `derive_plan` sweep, **677 unique names × 2 scopes = 1,354 plans** | **1.26 s** |
| `derive_plan` sweep, **746 rows × 2 scopes = 1,492 calls** | **1.19 s** |
| `derive_plan` at `write_scope="none"`, 677 plans | 0.64 s |
| **`run_plan` sweep, 1,354 plans, `runs=2` (default)** | **37.79 s / 34.73 s / 38.26 s** over three consecutive trials; a fourth, cold-cache run with per-step census bookkeeping took **46.13 s** |
| `run_plan` sweep, `runs=1, allow_single_run=True` | 33.22 s |
| `run_plan`, `partial` scope only (677 plans) | 8.64 s |
| `run_plan`, `full` scope only (677 plans) | 27.64 s |
| `_resolve_write_scope` over 677 unique names | **0.48 s** (0.67 s over all 746 rows) |
| **Full app suite, `pytest tests/ -o addopts="" -q`** | **302.20 s, 2108 passed, 1 warning, 32 snapshots passed** |

[VERIFIED: all of the above via scripts under the scratchpad, run with `./.venv311/bin/python`]

**Report ~37 s, plan for 46 s.** The discussion's ~21 s extrapolation is not reproducible in the CI replica. **And the suite is 302 s, not 737 s** — so the execution half is **~12 %** of the suite, not ~3 %. That materially changes the "mark it slow?" question CONTEXT defers to the planner.

`runs=1` saves only 4 s (12 %) because the cost is not the repeat loop. Profiling shows it is `generate_pattern` — **7.2 s of 12.5 s** on a 300-plan sample, with 11.5 M calls into its inner generator expression and `address_fold_byte`, driven by `_resolve_write_target` materialising full-device patterns for large parts. [VERIFIED: `cProfile` over 150 names × 2 scopes] The `full` scope is 3.2× the `partial` scope for the same reason. **There is no cheap knob** — a `runs=1` sweep is a weaker mode for a 12 % saving and is not worth it.

### Hazards audited

**Filesystem:** `run_plan` *does* use the filesystem transiently — `tempfile` at `chip_test.py:2639` (`TemporaryDirectory(prefix="chip_test_read_")`), `:2726` (`prefix="chip_test_region_"`), `:3056` and `:3309` (`NamedTemporaryFile`, unlinked at `:3123` and `:3341`). [VERIFIED: `/usr/bin/grep -n "tempfile\|NamedTemporaryFile\|TemporaryDirectory\|\.unlink"`] **It cleans up completely.** After the full 1,354-plan sweep:
- new entries in `$HOME`: **none**
- new entries in `~/.firestarter`: **none**
- new entries in the CWD: **none**
- new entries in `tempfile.gettempdir()`: **0**

[VERIFIED: before/after directory snapshots taken around the sweep in one process]

**Network:** none. `run_plan`'s only outbound calls are to the injected `operator`, which is a `Mock(spec=[...])`. The engine "never imports hardware.py" [VERIFIED: `chip_test.py:1615-1616` docstring, verbatim `` `sampler` is an optional opaque callable; this engine never imports hardware.py``] and `sampler` defaults to `None`.

**`~/.firestarter`:** untouched by `run_plan` **when the operator is a bare `Mock` and the database is `EpromDatabase(skip_local_override=True)`**. The known project leak (the app writing `~/.firestarter/config.json` despite `FIRESTARTER_CONFIG_DIR`) lives in `ConfigManager`, which `run_plan` never constructs. **But `tests/conftest.py:make_app_context()` constructs a real `ConfigManager()` when `config_manager is None`** [VERIFIED: `tests/conftest.py:314-315`, verbatim `    if config_manager is None:` / `        config_manager = ConfigManager()`]. For the §G handler leg, pass `config_manager=Mock()` explicitly so the leak is not touched at all.

**`monkeypatch`:** **not needed anywhere.** The corpus mutation is on plan copies (D-09's own point), the database is injected, and the operator is injected. No global is patched. This is a genuine simplification over the `test_shipped_ops_never_reach_sdp_arm` template, which does use `monkeypatch`.

**Console output:** **zero.** `stdout` and `stderr` captured around the full 1,354-plan sweep were both **0 characters**. [VERIFIED: `io.StringIO` redirection around the sweep] Nothing will swamp pytest.

**Module-scoped fixture:** yes, and it is worth it. Build both the plan corpus (1.26 s) and, if the alignment leg is split across several test functions, the `run_plan` results (37 s) once at module scope. But note the results are large: 16,248 `StepResult` objects. If only one test function needs them, a plain module-level loop inside that function is simpler and equally cheap. **Recommendation:** module-scoped fixture for the *plan corpus* (used by every leg); a single test function for the alignment sweep that builds and discards results as it goes, so peak memory stays flat.

**What the sweep actually exercises — an honest caveat.** Verdict census over all 16,248 steps: `{(supported=False, 'NA'): 9304, (True, 'OK'): 3431, (True, 'SKIPPED'): 2545, (True, 'BAD'): 968}`. The 2,545 SKIPPED are dominated by `('write', 'chip-ID mismatch — destructive steps gated (chip left pristine)')` ×131, the same for `write-partial` ×131 and `erase` ×108, and `('verify', 'no write target available for verify')` ×189 (counts from a 400-plan sample). Cause: `_mock_operator`'s `check_eprom_id` returns a fixed `(True, 0x1234)`, which mismatches most chips' real IDs and closes the destructive gate. **This does not weaken PRUNE-05** — a SKIPPED step still produces a `StepResult`, and alignment plus NA-on-unsupported both hold at 100 %. But the plan must not claim the sweep "exercises the write path on every chip." It does not. State the limit in the test docstring.

### Where `_mock_operator` should live

**`_mock_operator` is not importable from a shared home today — there is no shared home.** It is **copied**, not shared:
- `tests/test_chip_test.py:1009` — the fuller copy; sets `sdp_lock`/`sdp_unlock` return values.
- `tests/test_chip_test_sdp_leg.py:239` — a near-copy that **omits** the `sdp_lock`/`sdp_unlock` return values (they fall through to a truthy auto-`Mock`).
- `tests/test_chip_test_cycle.py:26` — a third `_OPERATOR_METHODS` list.

[VERIFIED: `/usr/bin/grep -rn "def _mock_operator"` → three definitions; both bodies read in full] The docstring line at `test_chip_test_sdp_leg.py:26` that reads like an import is **prose inside the module docstring's taxonomy**, not an `import` statement.

`tests/` **is** a package (`tests/__init__.py` exists) and `from tests.X import ...` is the established idiom [VERIFIED: `tests/scan_paths.py:80` `from tests.fw_presence import FW_ROOT`; `tests/test_devtest_issue_corpus.py:74` `from tests.fixtures.report_shapes import build_shape_from_step_specs`; seven more `from tests.fw_presence import ...` sites]. So `from tests.test_chip_test import _mock_operator` **would work mechanically**.

**Do not do it.** Every shared test helper in this tree lives in a module that is *not* `test_*`-prefixed: `tests/fw_presence.py`, `tests/scan_paths.py`, `tests/fixtures/report_shapes.py`, `tests/fixtures/rekey_ledger.py`, `tests/conftest.py`. Importing from a `test_*` module would be the first such import in the tree and drags the exporting module's whole import-time cost (including its module-level `EpromDatabase`) into the importer.

**Recommendation, in order:**
1. **Best — a new `tests/plan_corpus.py`** (top level, *not* under `tests/fixtures/`). It holds the shared `_REAL_DB`, the corpus builder, and a fourth `_mock_operator`. Top-level `tests/` is inside `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` [VERIFIED: `.github/workflows/ci.yml:81, 84`], whereas **`tests/fixtures/` is excluded from ruff** (`extend-exclude = ["tests/golden", "tests/fixtures"]`, `pyproject.toml:121`) *and* from mypy (`exclude = ["^tests/fixtures/"]`, `:174`). A shared helper should be linted; a planted counter-example should not. Put the helper in `tests/`, the JSON artifact in `tests/fixtures/`.
2. **Acceptable — `tests/conftest.py`**, alongside `make_app_context`. Costs a fourth copy's worth of divergence risk being centralised, but conftest is already the home for `make_app_context`, and CONTEXT's D-06 does not forbid it.
3. **Rejected — import from `tests/test_chip_test.py`.** Works, breaks convention, couples two test modules' import order.

Whichever is chosen, **copy `test_chip_test.py`'s fuller variant** (the one that sets `sdp_lock.return_value` and `sdp_unlock.return_value`), not the sdp_leg near-copy. And record in the docstring that a fourth copy now exists, so the drift is visible rather than discovered later.

---

## F. The Frozen Op-Sequence Pin — Format and Home

### What the database actually produces

| Grain | Distinct shapes |
|---|---:|
| Op strings only (`[s.op for s in plan.steps]`) | **4** |
| Op string **+ `supported` flag** (`[(s.op, s.supported)]`) | **16** |
| Per-chip **(full, partial) pair** of the above | **8 shape families** |

[VERIFIED: `collections.Counter` over all 1,354 plans]

The 16 collapse to 8 families because a chip's `full` and `partial` shapes always pair (they differ only in `write` vs `write-partial`), and every count is exactly duplicated across the two scopes. The 8 families, with chip counts:

| Family (id / bc-position / erase / sdp) | Chips |
|---|---:|
| `id-bcpost-erase-sdpNA` | 197 |
| `id-bcpre-eraseNA-sdpNA` | 180 |
| `noid-bcpre-eraseNA-sdpNA` | 90 |
| `noid-bcpreNA-eraseNA-sdpNA` | 76 |
| `noid-bcpostNA-erase-sdpNA` | 41 |
| `noid-bcpostNA-erase-sdp` | **40** ← the only family with a live SDP leg |
| `id-bcpreNA-eraseNA-sdpNA` | 27 |
| `noid-bcpost-erase-sdpNA` | 26 |
| **Total** | **677** |

**Pin the 16 `(op, supported)` sequences, not the 4 op-only sequences.** The 4-sequence grain is blind to the change PRUNE-05 most needs to catch: flipping an SDP step from `supported=True` to `supported=False` (or the reverse) moves 40 chips' hash ballast and leaves the op-only sequence byte-identical. CONTEXT's D-10 says "the 4 distinct op-sequences … plus the chip counts"; the 4 is a correct measurement of the *op-only* grain and I am not contradicting it, but the finer grain is strictly stronger for the same artifact size and I recommend it. **This is a planner call, and it should be made explicitly rather than inherited.**

### Format: JSON, not a Python literal

Three prototypes were built and measured:

| Shape | Bytes | Lines | Diff on a one-chip database change |
|---|---:|---:|---|
| 16 flat shapes + per-chip `{full, partial}` object | 67,456 | 3,586 | 2 lines |
| 8 families + per-chip family string, `[op, bool]` arrays | 45,581 | 1,515 | 1 line |
| **8 families + per-chip family string, `"op"` / `"op(NA)"` string tokens** | **38,646** | **940** | **1 line** |

[VERIFIED: all three generated and `os.path.getsize`'d this session]

**Recommend the third.** Sample:
```json
"shape_families": {
  "id-bcpost-erase-sdpNA": {
    "chip_count": 197,
    "full": ["id", "read", "write", "verify", "erase", "blank-check",
             "write-baseline-b(NA)", "write-baseline-a(NA)", "sdp-lock(NA)",
             "write-inhibited(NA)", "sdp-unlock(NA)", "write-restored(NA)"],
    "partial": ["id", "read", "write-partial", "verify", "erase", "blank-check", ...]
  }, ...
},
"chips": {
  "2516": "noid-bcpre-eraseNA-sdpNA",
  "2532": "noid-bcpre-eraseNA-sdpNA",
  "27128,D27128": "id-bcpre-eraseNA-sdpNA", ...
}
```

**Why JSON over a Python literal:** the tree's two committed data artifacts of this exact kind are JSON — `tests/fixtures/shape_ids.json` (735 B) and `tests/fixtures/part_number_delta.json` (182 kB, with a `_generated_by` string and an `aggregate` block of absolute numbers). A 940-line Python literal inside a test module would be the largest literal in `tests/` by a wide margin and would be reformatted by `ruff format` on every touch.

**Why the family/chip split gives a readable diff (D-11's requirement):** the `chips` map is one line per part number, sorted. A generator change that moves three chips between families produces a **three-line diff naming those three chips**, plus a `chip_count` delta on two families. An opaque alternative — hashing the whole corpus, or listing 677 full sequences — would produce either a one-line meaningless change or a 677-line churn.

**Keying:** by `part_number`, sorted, one entry per **unique** part number (677), because that is `derive_plan`'s actual input key. **Not** by `(manufacturer, part_number)` row: 65 part numbers appear on more than one row (69 extra rows; e.g. `AM29F002B,AM29F002BB` ×2), and `derive_plan(name, db)` resolves them all to the same chip and the same plan [VERIFIED: 746 rows → 677 unique names; the 746-row sweep produced 1,492 calls but only 1,354 distinct `(name, scope)` results]. Keying by row would put 69 duplicate values in the artifact that can never diverge.

Include an `aggregate` block of absolute measured numbers, following `part_number_delta.json`'s precedent: `rows: 746`, `distinct_part_numbers: 677`, `plans: 1354`, `distinct_shape_families: 8`, `total_steps: 16248`, `unsupported_steps: 9304`. Assert them **absolutely**, not merely for self-consistency — `test_part_number_delta_drift.py`'s docstring makes exactly this argument for its eleven aggregates [VERIFIED: `tests/test_part_number_delta_drift.py:14-18`].

### Home and generator

- Artifact: **`firestarter_app/tests/fixtures/plan_shapes.json`** — CONTEXT's discretion block and Phase 174's D-03 both place committed artifacts there.
- Generator: **`firestarter_app/tools/measure_plan_shapes.py`** — exact analog of `tools/measure_part_number_delta.py`, whose shape is: shebang, module docstring stating exit codes, `argparse` with a `--check` mode, `_TARGET_DEFAULT = _APP_ROOT / "tests" / "fixtures" / <name>.json`, `sys.path.insert(0, str(_APP_ROOT))`, `def main() -> int`, `if __name__ == "__main__":`. [VERIFIED: `tools/measure_part_number_delta.py:1-40, 224-302`]
- Drift test: **`firestarter_app/tests/test_plan_shapes_drift.py`** — copy `tests/test_part_number_delta_drift.py`'s four-leg shape (regenerate to a tempdir via `subprocess`, compare; assert the aggregates absolutely; no skip marker, because nothing here depends on the sibling firmware repo).

**Note on `tools/`:** CI runs `ruff check firestarter/ tests/` only, so `tools/` is **not** linted or type-checked in CI. That is the existing state for `measure_part_number_delta.py`; do not treat it as licence to write sloppy code there, but do not spend plan budget on making it strict either.

**Simpler alternative the planner may prefer:** skip the generator and the drift test entirely; put the 8 families as a module-level Python literal in the sentinel module and assert them element-wise (the `_AT28C256_FULL_EXPECTED_OP_ORDER` idiom, `tests/test_erase_flag_invariants.py:264-303`), together with the per-family chip counts and the six aggregates — no 677-row map. That is a literal reading of D-10 ("the 4 distinct op-sequences … plus the chip counts mapping onto them") and costs three fewer files. It loses only the *which chip moved* diff. **Recommend the artifact route** on D-11's grounds (the whole point of the pin is to make a generator change legible), but the smaller option is defensible and cheaper.

---

## G. The Handler Leg

`_resolve_write_scope` is at **`firestarter_app/firestarter/cli_handlers.py:2236`** [VERIFIED: exact, `def _resolve_write_scope(` on that line]. Body, verbatim (`:2258-2261`):
```python
    del interactive  # no branch keys on it any more -- see the docstring
    if not _is_uv_eprom(app, chip):
        return "full"
    return "partial"
```
`_is_uv_eprom` (`:2229-2232`), verbatim:
```python
    full = app.db.get_eprom(chip)
    if not full:
        return False
    return is_uv_eprom(full)
```

**What `AppContext` needs to be:** only `.db`. Everything else can be a bare `Mock`. `AppContext` is a six-field dataclass [VERIFIED: `cli_handlers.py:110-122`] — `db`, `config_manager`, `eprom_operator`, `hardware_manager`, `firmware_manager`, `eprom_presenter`.

**There is an existing double: `tests/conftest.py:make_app_context(...)`** (`:241`), plus a no-argument `app_context` fixture (`:339`). Keyword-only, six parameters, each defaulting to a hardware-free build: `EpromDatabase(skip_local_override=True)`, a real `ConfigManager()`, and `Mock(spec=...)` for the four managers. Fifteen call sites across the suite use it.

**Use it, but pass two arguments explicitly:**
```python
app = make_app_context(db=_REAL_DB, config_manager=Mock())
```
- `db=_REAL_DB` reuses the module's single `EpromDatabase(skip_local_override=True)` instead of building a second (the default *would* build a correct one, but a second parse costs ~0.2 s and desynchronises the corpus from the handler leg).
- `config_manager=Mock()` avoids constructing a real `ConfigManager`, which is where this project's documented `~/.firestarter/config.json` write leak lives. `_resolve_write_scope` never touches it.

**Is the sweep 746 database lookups or one?** **677 lookups, one per call — `get_eprom` is not cached.** [VERIFIED: `[a for a in dir(db) if 'cache' in a.lower()]` → `[]`; 5 × 677 = 3,385 `get_eprom` calls took 1.656 s, i.e. ~0.49 ms each, linear in the call count] Profiling the `run_plan` sweep shows `database.get_eprom_config` at `:446` doing a `_strip_paren` regex `re.sub` per candidate — 523,756 calls in a 300-plan sample. It is a linear scan with per-row regex normalisation.

**Measured cost of the whole handler leg: 0.48 s over 677 unique names** (0.67 s if driven over all 746 rows). [VERIFIED] That is negligible; there is no reason to memoise or to reduce the domain.

**Measured result — the leg is green today:**
```
_resolve_write_scope over 677 unique names: Counter({'full': 407, 'partial': 270})
mismatch vs derive_plan(...).is_uv: 0
```
[VERIFIED] Every one of the 270 UV rows returns `"partial"`; every one of the 407 non-UV rows returns `"full"`; and the resolver agrees with `Plan.is_uv` on all 677 — so a second, cross-check assertion (`_resolve_write_scope(app, n) == ("partial" if plan.is_uv else "full")`) is available for free and pins the handler and the planner to the *same* UV axis, which is the drift D-12 is actually worried about.

Pass `interactive=False` **and** `interactive=True` and assert the results are identical — that is the one property `TestUVWriteHasNoPrompt` legs 2/3 prove for two chips and this leg can prove for 677 at no extra cost.

---

## H. Anti-Vacuity RED Evidence Mechanics

Phase 174's evidence directory is **`.planning/phases/174-blast-radius-invariance-harness/evidence/`**, containing 13 `.txt` transcripts named `174-<NN>-<slug>.txt`. **All 13 are git-tracked in the meta repo.** [VERIFIED: `git ls-files` returns all 13 paths]

**The transcript idiom**, from `evidence/174-06-duplicate-row-red-green.txt` (head, verbatim):
```
dup_rows_for_that_id=2
== LEG A1 duplicate ledger_id against PRE-FIX blob 5c0c7c9 -- RED expected, it exits 0 where non-zero is required
OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound
rc_prefix_dup=0
== LEG A2 the same file against the FIXED checker -- GREEN expected, exit 2 naming the duplicate
ERROR: duplicate MILESTONES.md row for ledger_id 'RK-174-01-p177-readback-gating'
rc_fixed_dup=2
== LEG A3 the real unmutated pair still binds
OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound
rc_fixed_clean=0
```
The shape is: a `== LABEL` line stating the leg and **what outcome is expected**, then the raw command output, then a `rc_<name>=N` line carrying the exit code. Plain text, no markdown, no ANSI.

**How the plan references it**, from `174-06-PLAN.md` [VERIFIED: lines 13-15, 49-53, 164, 172]:
- Frontmatter lists each evidence path (lines 13-15).
- Each is repeated under an `artifacts:` block as `- path: <full path>` (lines 49-53).
- Each task's `<files>` element names the evidence file alongside the source files it proves (line 164).
- Tasks cite a *prior* transcript as the idiom to follow: `` `.planning/phases/174-.../evidence/174-01-anti-vacuity-red-green.txt` — the legs A through H transcript, for the `== LABEL` / `rc=` idiom this task's transcript follows `` (line 172).

**For Phase 175:** create `.planning/phases/175-structural-sentinel-over-derive-plan/evidence/`, commit `175-<NN>-<slug>.txt` transcripts in the **meta** repo (the test code itself commits in `firestarter_app`), and follow the `== LABEL` / `rc_<name>=` shape exactly. Every leg CONTEXT's discretion block requires to be *seen* RED gets one section.

**One mechanical warning.** With pytest's `addopts = "-ra -q"`, a transcript captured without `-o addopts=""` has no count line, so it cannot show "1 failed, N passed." Every transcript in this phase must be captured with `-o addopts=""`.

---

## I. The `dedup_fingerprint` No-Move Check

**The exact command, verbatim, ready to become a verify leg:**
```bash
cd /workspaces/firestarter_app && ./.venv311/bin/python -m pytest \
  tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py \
  -o addopts="" -q
```

**Result this session: `114 passed in 1.57s`** (wall clock 1.892 s). [VERIFIED]

**The modules and what they hold:**
- `firestarter_app/tests/test_blast_radius_invariance.py` — 30 test functions including `test_dedup_fingerprint_is_frozen` (`:244`, parametrized over `shape_id`/`expected`), `test_build_db_diff_ladder_pin_for_all_shapes` (`:331`), the seven `to_dict` key-list pins (`:385-461`), `test_schema_version_is_pinned` (`:470`), `test_shape_id_set_is_pinned_and_disjoint_from_reserved` (`:535`), `test_committed_snapshot_matches_a_fresh_regeneration` (`:566`), and the two planted-mutation legs (`:587`, `:601`).
- `firestarter_app/tests/test_rekey_ledger.py` — the ledger closure.
- Supporting data: `tests/fixtures/rekey_ledger.py` (`LEDGER`, four-tuples, `ast.literal_eval`-parseable by the meta-side checker), `tests/fixtures/shape_ids.json`, `tests/fixtures/report_shapes.py`, `tests/fixtures/reports/<shape_id>.json`, `tests/fixtures/planted_rekey_mutation.py`.

**Two additions worth making verify legs alongside it:**

1. **The meta-side ledger checker**, `/workspaces/tools/rekey/check_rekey_ledger.py` — D-13's cross-tree binding. Phase 175 declares nothing into `MILESTONES.md`, so this must stay at "6 ledger row(s), 6 MILESTONES.md row(s) bound" and exit 0.
2. **`git diff --quiet -- firestarter_app/tests/fixtures/rekey_ledger.py`** and the same for `tests/fixtures/reports/` — a byte-level proof that this phase touched no frozen input, not merely that the assertions still pass. CONTEXT is explicit that "if any frozen hash moves, that is a defect in this phase," and a byte-level check is the honest statement of that.

**Correction to the task brief's environment fact 4.** `test_flash_path_record_sync` **does not exist in `firestarter_app`.** [VERIFIED: `/usr/bin/grep -rn "flash_path_record" tests/ tools/ --include=*.py` → no matches; `git log --all -S"flash_path_record"` → no commits] It lives in the **firmware** repo, `/workspaces/firestarter/tests/test_flash_path_record_sync.py`, where `_git_porcelain` at `:252-261` runs `git status --porcelain` against the firmware repo. **The `firestarter_app` suite has no whole-repo-porcelain gate at all**, and I ran the full 2,108-test app suite from a clean tree with zero failures to confirm no such coupling exists. The phase's own hygiene reason to commit before a full run still stands; the named test is not the reason.

---

## J. The Stale-Comment Defect (file the todo; DO NOT fix)

**Exact range: `firestarter_app/firestarter/cli_handlers.py:2295-2303`.** CONTEXT's cited `2295-2305` is correct at its start; the strictly-stale sentence ends at 2303 (2304-2308 describe the non-UV full-device write, which is still accurate). Verbatim, with line numbers [VERIFIED: `/usr/bin/grep -n "" firestarter/cli_handlers.py | sed -n '2295,2308p'`]:

```
2295 # ALWAYS WRITES: every run writes to the chip, unconditionally. A
2296 # UV-erasable EPROM is asked first, and quick task 260821-wna
2297 # changes what the two answers DO: yes permits the whole device to be
2298 # written IF the chip reads blank, and otherwise writes one masked
2299 # 256-byte slot; no writes one 256-byte slot only,
2300 # unconditionally -- never read-only or non-destructive either way, and
2301 # the two answers no longer resolve to the same window on a used chip. Off
2302 # a TTY the ask is treated as a DECLINED prompt, not absent consent, so a
2303 # single 256-byte slot is written anyway. Every OTHER family --
```

**The offending sentence, quoted for the todo:**
> "A UV-erasable EPROM is asked first, and quick task `260821-wna` changes what the two answers DO: yes permits the whole device to be written IF the chip reads blank, and otherwise writes one masked 256-byte slot; no writes one 256-byte slot only, unconditionally … Off a TTY the ask is treated as a DECLINED prompt, not absent consent, so a single 256-byte slot is written anyway."

**Why it is stale, evidenced:** 59 lines above it, `_resolve_write_scope`'s own docstring says the opposite in the present tense — `"UV parts get \"partial\", everything else \"full\". That is the whole rule, and there is no prompt on any path."` [VERIFIED: `cli_handlers.py:2245-2246`] — and the body is a two-branch `if` with `del interactive` and no prompt. `TestUVWriteHasNoPrompt` pins the absence of `Confirm` structurally. Three independent confirmations that lines 2295-2303 describe the reverted `260821-wna` design.

**Todo filing notes:** it is a comment block, so it also falls under the standing **no-comments-in-source** rule and under the pending `2026-08-27-strip-gsd-provenance-comments-from-source.md` sweep. CONTEXT says file it **alongside** that sweep, not merged into it. **This phase must not touch `cli_handlers.py`** — it is a product file and the phase is test-only. Doing so would also invalidate the "zero production diff" claim the phase's own audit rests on.

---

## Architecture Patterns

### System Architecture Diagram

```
                        firestarter_app/firestarter/data/chip_database.json
                                    (GENERATED — never hand-edited)
                                              │
                                              ▼
                          EpromDatabase(skip_local_override=True)      ◄── module-level, ONE instance
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     │  _all_rows(db): two-level descent over db.proms │
                     │  → 746 rows → 677 unique part_number strings    │
                     └────────────────────────┬────────────────────────┘
                                              │
        ┌─────────────────────────────────────┼──────────────────────────────────┐
        ▼                                     ▼                                  ▼
  derive_plan(name, db,                 _resolve_write_scope(               vars(chip_test)
    write_scope="full")                   AppContext(db=…), name,             → 13 OP_* strings
  derive_plan(name, db,                   interactive=…)                          │
    write_scope="partial")                      │                                 ▼
        │  1,354 Plans, 1.26 s                  │  677 calls, 0.48 s      ┌────────────────────┐
        │                                       │                        │ requires-verify (2)│
        ▼                                       ▼                        │ exempt+reason (11) │
  ┌──────────────────────────┐        ┌──────────────────────┐          │ union == all 13    │
  │ MODULE-SCOPED FIXTURE    │        │ UV handler leg       │          │ intersection == ∅  │
  │ corpus: {(name,scope):   │        │ 270 UV → "partial"   │          └─────────┬──────────┘
  │          Plan}           │        │ 407 non-UV → "full"  │                    │
  └────────┬─────────────────┘        └──────────────────────┘                    │
           │                                                                       │
   ┌───────┼──────────────┬──────────────────┬─────────────────┬──────────────────┘
   ▼       ▼              ▼                  ▼                 ▼
 write→  erase→        UV structural     frozen shape      run_plan alignment
 verify  blank-check   pins              pin               sweep
 pred.   leg (D-05)    (D-12)            (D-10 half 1)     (D-10 half 2)
   │       │              │                  │                 │
   │       │              │                  │                 │  Mock(spec=[8 methods])
   │       │              │                  ▼                 ▼  37 s, no FS/net/console
   │       │              │       tests/fixtures/         len(results)==len(steps)
   │       │              │       plan_shapes.json        + NA on every unsupported step
   │       │              │              ▲                      │
   │       │              │              │  --check             │
   │       │              │       tools/measure_plan_shapes.py  │
   │       │              │                                     │
   ▼       ▼              ▼                                     ▼
 cycle_block_bounds(steps)  ◄── PRODUCTION helper, chip_test.py:1236 — CALLED, never re-derived
   │
   ▼
 ANTI-VACUITY (D-09)
   ├─ hand-built counter-plan via _plan_with_steps(write, no verify)  → must be flagged
   └─ mutated corpus: dataclasses.replace(plan, steps=[… verify removed])
         → 1,354/1,354 flagged (measured)
```

### Recommended Project Structure

```
firestarter_app/
├── tests/
│   ├── plan_corpus.py                            # NEW: shared _REAL_DB, corpus builder,
│   │                                             #      _mock_operator (4th copy, declared)
│   ├── test_derive_plan_structural_sentinel.py   # NEW: closure + write→verify + erase leg
│   │                                             #      + UV pins + anti-vacuity (fast, ~2 s)
│   ├── test_derive_plan_no_drop_sweep.py         # NEW: run_plan alignment sweep (~37 s)
│   ├── test_plan_shapes_drift.py                 # NEW: artifact drift gate
│   └── fixtures/
│       └── plan_shapes.json                      # NEW: committed frozen pin (~39 kB, 940 lines)
└── tools/
    └── measure_plan_shapes.py                    # NEW: generator, argparse + --check
```

**Split the ~37 s sweep into its own module.** It makes `pytest tests/ --deselect tests/test_derive_plan_no_drop_sweep.py` a one-flag escape hatch without inventing a marker, and it keeps the fast structural legs runnable in ~2 s during development. This also directly answers CONTEXT's deferred "does the sweep run on every push?" question with the cheapest reversible answer: **yes, it runs, and it is one path away from not running.** No `pytest.ini` `markers` entry exists in this project today [VERIFIED: no `markers` key in `pyproject.toml`, no `mark.slow` anywhere in `tests/`], so adding a marker would be a new convention; a module split is not.

### Pattern 1: Total, fail-closed partition with named exemptions

**What:** every member of a runtime-discovered vocabulary lands in exactly one of two buckets; one bucket carries a prose reason per member; the union is asserted against the vocabulary and the intersection against the empty set.
**When to use:** whenever a rule must be total over a vocabulary that no type checker can see (D-01, D-06).
**Example** — the shipped closure this is modelled on, `tests/test_chip_test_sdp_leg.py:840-846`:
```python
    module_op_constants = {
        value
        for name, value in vars(chip_test_mod).items()
        if name.startswith("OP_") and isinstance(value, str)
    }
    shipped_op_set = module_op_constants - _SDP_OPS - _SDP_LEG_OPS
```
and the reason-carrying half, `tests/test_op_registration_parity.py:456` (`_OP_REGISTRY_EXEMPTIONS: dict[tuple[str, str], str]`) with its empty-reason guard at `:821` and stale-row guard at `:843`.

### Pattern 2: Two-level whole-database selector

**What:** descend `db.proms` twice — manufacturer key, then the per-manufacturer list — because a one-level loop iterates *strings*.
**When to use:** every whole-database sweep. Three shipped modules already do it.
**Example** — `tests/test_erase_flag_invariants.py:125-132`:
```python
def _all_rows(db: EpromDatabase) -> list[tuple[str, dict]]:
    """Every (manufacturer, chip_record) pair in the database, exhaustively."""
    rows = []
    for manufacturer, chips in db.proms.items():
        for chip in chips:
            rows.append((manufacturer, chip))
    return rows
```
Verified live: `type(db.proms)` is `dict`, `len` 59 (manufacturers), first value is a `list`. A one-level scan yields 59 strings and every downstream assertion passes vacuously.

### Pattern 3: Committed artifact + generator + drift test

**What:** a script emits a JSON artifact; the artifact is committed; a test regenerates into a tempdir and asserts byte-equality, plus asserts the aggregate numbers absolutely.
**When to use:** any pin over generated data (D-11, D-16).
**Example:** `tools/measure_part_number_delta.py` → `tests/fixtures/part_number_delta.json` → `tests/test_part_number_delta_drift.py`.

### Anti-Patterns to Avoid

- **Re-implementing the cycle-block rule.** D-02 forbids it; measurement shows why (the docstring's family list omits the NA `erase`, so a hand-rolled rule built from it would be wrong on 373 plans).
- **Deriving `requires-verify` from `_DESTRUCTIVE_OPS` or `_CYCLE_BLOCK_START_OPS`.** Both happen to work today; both silently re-scope when widened for an unrelated reason. D-01 rejects it.
- **A one-level `for row in db.proms:` selector.** Documented in this repo's own test docstring as the vacuous-pass trap.
- **Mutating a `Step` in place.** `Step` is not frozen and the corpus is shared. Use `dataclasses.replace`.
- **`copy.copy(plan)` and then mutating `.steps`.** Shares the list; measured.
- **Asserting `full_device_permitted is False` on a UV write step.** CONTEXT D-12 forbids it; measurement confirms it would be a false invariant — UV writes at `write_scope="full"` carry `full_device_permitted=True` on all 270 UV chips [VERIFIED: `Counter({('full', True): 270, ('partial', False): 270})`].
- **Adding a `pytest.mark.slow`.** No marker convention exists here; a module split is the cheaper reversible answer.
- **Writing explanatory comments in the new module.** Standing operator rule; use docstrings.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Finding the repeat-cycle block | An adjacency or "next N steps" rule | `chip_test.cycle_block_bounds(plan.steps)` (`:1236`) | D-02; and the docstring's family list omits the NA `erase`, so a hand-rolled rule is wrong on 373 plans |
| Enumerating chips | `db.proms` one-level, or a hand-listed chip array | `_all_rows`-style two-level descent | The documented vacuous-pass trap |
| A hardware-free `EpromOperator` | A new fake | `Mock(spec=_OPERATOR_METHODS)` per `test_chip_test.py:1009` | `spec=` is what makes an out-of-spec attribute access raise instead of silently returning a truthy Mock |
| An `AppContext` for the handler leg | A hand-built dataclass instance | `tests/conftest.py:make_app_context(db=_REAL_DB, config_manager=Mock())` | Already casts six doubles correctly for mypy; hand-building reintroduces the 30-error splat its docstring describes |
| A `Plan` for the counter-example | A fresh helper | `_plan_with_steps(*steps)` (`test_chip_test.py:1093`) | One line, house idiom |
| Copying a plan for mutation | `copy.copy` / `copy.deepcopy` / manual reconstruction | `dataclasses.replace(plan, steps=[...])` | `copy.copy` shares the list (measured); `deepcopy` is needlessly slow at 1,354× |
| Comparing a committed artifact to a fresh run | Hand-rolled diffing | `tests/test_part_number_delta_drift.py`'s subprocess-regenerate-into-tempdir shape | Shipped, four legs, already proven |
| Op-vocabulary discovery | A hardcoded list, or a regex over source | `vars(chip_test)` + `startswith("OP_")` + `isinstance(v, str)` | Shipped in two modules; a regex would false-positive on hyphenated op values appearing in prose (`test_op_registration_parity.py`'s docstring makes this argument at length) |

**Key insight:** every mechanism this phase needs is already in the tree, in a module whose docstring explains why it is shaped that way. The genuinely new work is the **reasoning content** — which ops need an oracle and why the other eleven do not — not the machinery.

---

## Common Pitfalls

### Pitfall 1: D-05's erase leg reddens on 162 plans if "blank-check" means "supported blank-check"

**What goes wrong:** the natural reading of "an executable erase step has a blank-check at a higher index" is "…has a *working* blank-check." Under that reading the leg is **RED on 81 chips × 2 scopes = 162 plans** on the shipped, unmodified database.

**Measured:** 608 of 1,354 plans have a `supported=True` `OP_ERASE`. Of those, **162 have no `supported=True` `OP_BLANK_CHECK` at a higher index** — but **all 162 do have a blank-check *step* at a higher index**, carrying `supported=False` and the reason:
```
protocol 0x0D (28C family) auto-erases per page during write; no step in this plan can ever leave the device blank
```
All 81 chips share that one reason string. [VERIFIED: sweep over 677 chips at `write_scope="full"`; `Counter` over the offenders' reasons → a single key with count 81]

**Why it happens:** `blank_check_step`'s case 3 — `write_execute and protocol in _AUTO_ERASE_ON_WRITE_PROTOCOLS` where `_AUTO_ERASE_ON_WRITE_PROTOCOLS = [5, 13]` — marks the blank-check NA. But `erase_is_executable = can_erase and protocol != _PROTOCOL_FLASH4 and write_execute` [VERIFIED: `chip_test.py:645`, verbatim] is **True** for protocol `0x0D`, since Phase 153 restored `FLAG_CAN_ERASE` on all 84 algorithm-13 rows. So the erase branch runs `steps.append(blank_check_step)` [VERIFIED: `chip_test.py:749-750`] and appends an already-NA step behind a live erase.

**How to avoid:** word the leg as **presence at a higher index within the same cycle block**, and add a second, separately-counted assertion that the population whose behind-erase blank-check is NA is **exactly 81 chips / 162 plans, all carrying that one reason string**. That turns Finding 1 from a RED into a pinned fact — and pins the *count*, so a future change that quietly widens the NA population reddens.

**Warning signs:** a plan task whose acceptance criterion says "every executable erase has a supported blank-check behind it"; an executor reporting a 162-plan RED and proposing to edit `chip_test.py`.

**Precedent to cite, so the planner does not think this is new:** `tests/test_chip_test_blank_check_order.py:130` — `test_at28c256_blank_check_moves_after_erase_but_stays_na` already pins exactly this for AT28C256.

### Pitfall 2: `cycle_block_bounds` finds only the FIRST block

**What goes wrong:** the predicate loops over write steps, calls `cycle_block_bounds` once, and checks "is there a verify after me in the block." A second write outside the block is then silently unguarded — or worse, is checked against the *first* block's verify.

**Measured:** `[write, verify, sdp-lock, write, verify]` → bounds `(0, 2)`. The second write at index 3 is entirely outside. [VERIFIED]

**How to avoid:** make "this write's index is not inside `[start, stop)`" a **violation**, not a skip. Cover it with a hand-built leg, because the shipped corpus has exactly one write per plan (`Counter({1: 1354})`) and will never exercise it.

**Warning signs:** `if bounds is None: continue`; any `bounds[0] <= i` check without the matching `i < bounds[1]`.

### Pitfall 3: an alignment-only no-drop proof cannot catch the change PRUNE-05 forbids

CONTEXT's own §Specific Ideas states this; measurement confirms the trap is real: a prune shrinks `Plan.steps` and `results` together, so `len(results) == len(plan.steps)` stays true while 40 chips' six SDP ballast steps vanish from the dedup hash. **Both halves are mandatory.** Put the argument in the sweep module's docstring so a later "simplification" cannot delete the frozen half without reading why it exists.

### Pitfall 4: `run_plan` with `runs < 2` returns a single `__plan__` result

**What goes wrong:** the alignment assertion fires for a reason unrelated to PRUNE-05. `run_plan` returns exactly one `StepResult(op="__plan__", verdict=VERDICT_BAD, …)` when `runs < 1 or (runs < 2 and not allow_single_run)` [VERIFIED: `chip_test.py:1631-1642`], so `len(results) == 1` against `len(plan.steps) == 12`.
**How to avoid:** use the default `runs=2`. Both `runs=2` and `runs=1, allow_single_run=True` were measured green (0 mismatches each), so either is safe — but a bare `runs=1` is not.

### Pitfall 5: the sweep does not exercise the write path on most chips

2,545 of the 6,944 supported steps come back `SKIPPED`, dominated by `chip-ID mismatch — destructive steps gated (chip left pristine)` because `_mock_operator`'s `check_eprom_id` returns a fixed `(True, 0x1234)`. PRUNE-05 is unaffected (a SKIPPED step still yields a `StepResult`), but the plan must not overclaim. Say what the sweep proves — step/result alignment and NA-on-unsupported — and nothing more.

### Pitfall 6: "637 of 677 chips carry six `supported=False` SDP steps" is not what the database says

PRUNE-05's own wording asserts 637/677. **Measured: 40 chips have a *live* SDP leg** (family `noid-bcpostNA-erase-sdp`, all six leg steps `supported=True`), so **637 have the leg NA** — the arithmetic is right. But **every one of the 677 carries the six steps**; the 637 is the count of chips whose six are *unsupported*, not the count that carry them. The distinction matters when writing the pin's assertion message. [VERIFIED: 677 − 40 = 637; `Counter` over the 8 shape families]

### Pitfall 7: the devcontainer `grep` under-scans, silently

`grep` is **ugrep 7.8.4** and honors `.gitignore`. A `grep -r` over `firestarter_app/` silently skips `.venv311/`, `__pycache__/` and anything else ignored. It happened to agree with `/usr/bin/grep` on every tracked-file count I took this session, which is exactly why it is dangerous — it fails quietly, not loudly. **Every evidence-producing scan in this phase's plans must use `/usr/bin/grep` or a `bash script.sh`.**

### Pitfall 8: the mypy watermark has zero headroom

`python tools/check_mypy_watermark.py` reports **`checked 165 source files` / `mypy errors: 35 (watermark: 35)` / `OK: error count at watermark.`** [VERIFIED, run this session in `.venv311`] **One new mypy error in the new test module fails CI.** New test modules are not in a strict island by default, and `disallow_untyped_defs = false` / `check_untyped_defs = false` are the global settings [VERIFIED: `pyproject.toml:159-161`], so unannotated test functions are not checked — but an *annotated* helper's body is (`make_app_context`'s docstring explains this exact mechanic). Keep the new module's annotated helpers simple, and run the watermark before committing.

Note also `tests/fixtures/` is excluded from **both** ruff and mypy (`extend-exclude = ["tests/golden", "tests/fixtures"]`, `pyproject.toml:121`; `exclude = ["^tests/fixtures/"]`, `:174`). Do not put a shared *helper* there thinking it will be checked.

### Pitfall 9: `test_chip_test_cycle.py`'s `_REAL_DB` omits `skip_local_override`

`tests/test_chip_test_cycle.py:24` is `_REAL_DB = EpromDatabase()` — no `skip_local_override=True`. Every other whole-DB module passes it. If the new module is written by copying that one, D-07 is silently violated and results become machine-dependent. **Copy `test_erase_flag_invariants.py:98` instead.**

---

## Code Examples

### The write→verify predicate (measured green on all 1,354 shipped plans, and 100 % sensitive under three mutations)

```python
# Source: composed from firestarter_app/firestarter/chip_test.py:1236
# (cycle_block_bounds) and the D-01/D-04 field set. Measured this session:
# 0 violations over 1,354 shipped plans; 1,354/1,354 flagged under each of
# three mutations.

_REQUIRES_VERIFY = frozenset({chip_test.OP_WRITE, chip_test.OP_WRITE_PARTIAL})


def write_verify_violations(plan):
    """Every write step in `plan` with no supported, field-matching verify
    behind it inside the same cycle block.

    Fail-closed on three axes: a write outside the returned block is a
    violation (cycle_block_bounds finds only the FIRST block); a verify with
    supported=False is not an oracle (D-03); and a verify whose
    write_region / region_policy / cycle_payload differ from the write's is
    verifying a different thing (D-04).
    """
    bounds = chip_test.cycle_block_bounds(plan.steps)
    violations = []
    for index, step in enumerate(plan.steps):
        if step.op not in _REQUIRES_VERIFY or not step.supported:
            continue
        if bounds is None or not (bounds[0] <= index < bounds[1]):
            violations.append((index, step.op, "write sits outside the cycle block"))
            continue
        covered = any(
            candidate.op == chip_test.OP_VERIFY
            and candidate.supported
            and candidate.write_region == step.write_region
            and candidate.region_policy == step.region_policy
            and candidate.cycle_payload == step.cycle_payload
            for candidate in plan.steps[index + 1 : bounds[1]]
        )
        if not covered:
            violations.append(
                (index, step.op, "no supported, field-matching verify in the block")
            )
    return violations
```

### The total, fail-closed partition (D-01 / D-06)

```python
# Source: the vars() idiom is verbatim from
# firestarter_app/tests/test_chip_test_sdp_leg.py:840-846; the
# reason-carrying exemption dict follows
# firestarter_app/tests/test_op_registration_parity.py:456.

_EXEMPT_REASONS = {
    chip_test.OP_ID: "read-only identity compare; changes no device state",
    chip_test.OP_READ: "read-only; the step's own output is its result",
    chip_test.OP_BLANK_CHECK: "read-only, and itself an oracle (OP_ERASE's, per D-05)",
    chip_test.OP_VERIFY: "it IS the oracle; the firmware compares on-device",
    chip_test.OP_ERASE: "clears rather than stages bytes; oracle is the relocated blank-check (own leg)",
    chip_test.OP_SDP_LOCK: "changes protection state, not contents; oracle is the following write-inhibited read-back",
    chip_test.OP_SDP_UNLOCK: "changes protection state, not contents; oracle is the following write-restored read-back",
    chip_test.OP_WRITE_BASELINE_B: "SDP-leg write; _dispatch_sdp_leg read-back-equality is its inline oracle",
    chip_test.OP_WRITE_BASELINE_A: "SDP-leg write; _dispatch_sdp_leg read-back-equality is its inline oracle",
    chip_test.OP_WRITE_INHIBITED: "the read-back IS the oracle and expects INEQUALITY (expected_readback=pattern_a while source_payload=pattern_b, chip_test.py:3291-3296); a verify would assert the opposite",
    chip_test.OP_WRITE_RESTORED: "SDP-leg write; expected_readback=pattern_a is its inline oracle",
}


def test_op_vocabulary_is_totally_partitioned() -> None:
    module_op_constants = {
        value
        for name, value in vars(chip_test).items()
        if name.startswith("OP_") and isinstance(value, str)
    }
    partitioned = _REQUIRES_VERIFY | set(_EXEMPT_REASONS)
    assert partitioned == module_op_constants, (
        "an OP_* constant is in neither bucket (or in a bucket but no longer "
        "in the module); symmetric difference: "
        f"{sorted(partitioned.symmetric_difference(module_op_constants))}"
    )
    assert not (_REQUIRES_VERIFY & set(_EXEMPT_REASONS))
    assert all(reason.strip() for reason in _EXEMPT_REASONS.values())
```

### Mutated-corpus sensitivity (D-09)

```python
# Source: dataclasses.replace semantics verified this session against
# firestarter_app/firestarter/chip_test.py:406-445 (Plan/Step are plain,
# MUTABLE dataclasses). Measured: 1,354/1,354 flagged.

def test_removing_the_verify_flags_every_write_bearing_plan(plan_corpus) -> None:
    with_write = [
        plan
        for plan in plan_corpus.values()
        if any(s.op in _REQUIRES_VERIFY and s.supported for s in plan.steps)
    ]
    assert len(with_write) == 1354, (
        f"the corpus yielded {len(with_write)} write-bearing plans, expected "
        "1354 -- a sweep that visits zero rows must not pass"
    )
    unflagged = [
        plan.name
        for plan in with_write
        if not write_verify_violations(
            dataclasses.replace(
                plan, steps=[s for s in plan.steps if s.op != chip_test.OP_VERIFY]
            )
        )
    ]
    assert not unflagged, (
        f"{len(unflagged)} plans were NOT flagged after their verify was "
        f"removed -- the predicate is insensitive: {unflagged[:10]}"
    )
```

### The UV handler leg (D-12's load-bearing assertion)

```python
# Source: firestarter/cli_handlers.py:2236 (_resolve_write_scope) and
# tests/conftest.py:241 (make_app_context). Measured: 0.48 s over 677
# names; 270 "partial", 407 "full", 0 disagreements with Plan.is_uv.

def test_resolve_write_scope_returns_partial_for_every_uv_row(plan_corpus) -> None:
    app = make_app_context(db=_REAL_DB, config_manager=Mock())
    offenders = []
    uv_count = 0
    for name in sorted({n for n, _ in plan_corpus}):
        is_uv = plan_corpus[(name, "full")].is_uv
        uv_count += int(is_uv)
        expected = "partial" if is_uv else "full"
        for interactive in (True, False):
            actual = _resolve_write_scope(app, name, interactive=interactive)
            if actual != expected:
                offenders.append((name, is_uv, interactive, actual))
    assert uv_count == 270, f"expected 270 UV rows, the sweep saw {uv_count}"
    assert not offenders, (
        "_resolve_write_scope broke the aq6 UV write-scope ceiling: "
        f"{offenders[:10]}"
    )
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact on this phase |
|---|---|---|---|
| UV write: prompt, and "yes" permits a full-device write on a blank part | UV → `"partial"` unconditionally, no prompt on any path | quick task `260822-aq6`, `firestarter_app` commit `2b42dac`, 2026-08-22 | D-12 pins this. `cli_handlers.py:2295-2303` still describes the **reverted** design (§J). |
| Algorithm-13 (0x0D) rows had `FLAG_CAN_ERASE` cleared | Restored on all 84 rows | Phase 153 (ERASE-03/04) | **This is what creates Finding 1**: a live erase with an NA blank-check behind it on 81 chips. |
| Blank-check always emitted right after `read` | Relocated behind an executable erase (`erase_is_executable`, single-sourced) | quick task `260807-kaq` | D-05's pairing exists because of this; it has no guard today. |
| SDP leg: four steps | Six steps, `_SDP_LEG_STEP_ORDER` | v1.30 Phase 133/134 | The exemption bucket has 4 write-shaped members, not 2. |
| No cycle repeat | `runs=2` default, cycle block via `cycle_block_bounds` | v1.32 | D-02's "same cycle" only means something because of this. |

**Deprecated/outdated in the inputs to this phase:**
- **"~21 s for the `run_plan` sweep"** → measured **35–46 s** in the py3.11 replica.
- **"the full app suite is ~737 s"** → measured **302.20 s** (2,108 tests) in the py3.11 replica on this machine.
- **"1,492 plans"** → 1,492 *calls* over 746 rows, but only **1,354 distinct plans** (677 unique part numbers × 2 scopes). 17,904 steps / 10,190 unsupported are the per-row figures; the distinct-plan figures are **16,248 / 9,304**.
- **"`test_flash_path_record_sync` asserts whole-repo porcelain"** → true, but it is in the **firmware** repo, not `firestarter_app`.
- **`cycle_block_bounds`' docstring family list** → accurate about supported steps, misleading about emitted ones (the NA `erase` is inside the block).

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| Python 3.11 CI-replica venv | Every measurement and every plan verify leg | ✓ | 3.11.16 at `/workspaces/firestarter_app/.venv311` | `uv venv --python 3.11` + `pip install -e '.[test]'` |
| `firestarter` editable install in that venv | Importing `firestarter.chip_test` | ✓ | resolves to `/workspaces/firestarter_app/firestarter/__init__.py` | re-run `pip install -e '.[test]'` |
| pytest | The suite | ✓ | 9.1.1 | — |
| `/usr/bin/grep` (GNU grep) | Evidence-producing scans | ✓ | — | `bash script.sh` |
| `git` in both repos | Evidence, no-move check | ✓ | both clean on `gsd/v1.36-dev-test-fidelity` | — |
| `chip_database.json` | Every sweep | ✓ | 59 vendors → 746 rows → 677 unique part numbers | — |
| `tools/check_mypy_watermark.py` | Pre-commit gate | ✓ | reports `165` checked, `35/35` | — |
| Serial hardware / a real board | — | ✗ | — | **Not needed.** Nothing in this phase touches a port. |
| Network | — | ✗ | — | **Not needed.** |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. [VERIFIED: `/usr/bin/grep -n "security" .planning/config.json` → no match]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | Test-only phase; no auth surface exists in `firestarter_app` |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | No access-control surface |
| V5 Input Validation | **partially** | The sweep's only input is the **committed, generated** `chip_database.json`, read through `EpromDatabase(skip_local_override=True)`. D-07 deliberately excludes `~/.firestarter/database.json`, so no user-controlled input reaches the sentinel. |
| V6 Cryptography | no | `dedup_fingerprint` hashing is Phase 174's and is only *read* here (§I) |
| V12 File / Resource | **partially** | `run_plan` uses `tempfile` with `TemporaryDirectory`/`NamedTemporaryFile` and unlinks its own files; audited clean this session (§E) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation | Status in this phase |
|---|---|---|---|
| A hostile DB row widening the write window | Tampering | `derive_plan` takes region **width** from a module constant, never a DB field, for `fixed`/`uv-slot` [VERIFIED: `chip_test.py:406-445` docstring] | Product-side, unchanged; the UV pins (§Code Examples) reinforce it by test |
| A developer's local override changing CI results | Tampering | `EpromDatabase(skip_local_override=True)` | D-07; every new sweep uses it |
| A test writing into `~/.firestarter` | Tampering | Pass `config_manager=Mock()` to `make_app_context` | §E/§G; audited: 0 new entries in `$HOME`, `~/.firestarter`, CWD, tmp |
| A vacuous gate reading green forever | Repudiation | Mutated-corpus + planted counter-example legs, each with an absolute non-zero count assertion | D-09; all four mutations measured at 100 % |

**No new attack surface.** The phase adds no runtime code path, no dependency, no network call, no file write outside `tests/fixtures/` at generation time.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The GitHub-hosted CI runner's timings are proportional to this devcontainer's (302 s suite, 37 s sweep). Only the local machine was measured. | §E | If the CI runner is materially slower, the sweep's absolute cost could push a job near a timeout. Mitigated by the module split. |
| A2 | `run_plan`'s tempfile churn stays inside the system temp directory on the CI runner as it does here. Verified locally only. | §E | A runner with an unusual `TMPDIR` could leave artifacts. Low risk — `TemporaryDirectory`/`unlink` are unconditional. |
| A3 | The recommended `tests/plan_corpus.py` helper module will not trip a new mypy error at watermark 35. Not yet written, so not yet checked. | §E, Pitfall 8 | CI RED. Cheap to check: run `tools/check_mypy_watermark.py` before committing. |
| A4 | Splitting the sweep into its own module is sufficient for the deferred "does it run on every push?" question. Whether the operator wants it deselected is not a research question. | §Architecture Patterns | None technical — a planner/operator call. |
| A5 | The 16-shape `(op, supported)` grain is preferable to the 4-shape op-only grain for the frozen pin. This is my recommendation, not a CONTEXT decision. | §F | If the planner takes the 4-shape reading literally, the pin is blind to `supported` flips on 40 chips. Flagged rather than decided. |

**No claim above is load-bearing for correctness. Every number in the body of this document was measured this session, in the py3.11 venv, and is tagged `[VERIFIED: …]` with the command or the file and line range that produced it.**

---

## Open Questions

1. **Should the frozen pin use the 4 op-only sequences (CONTEXT's literal wording) or the 16 `(op, supported)` sequences / 8 families?**
   - What we know: both are measured; 4 op-only, 16 with `supported`, collapsing to 8 chip-level families. The finer grain costs nothing extra in artifact size.
   - What's unclear: whether D-10's "4 distinct op-sequences" is a specification or an observation.
   - Recommendation: **use the 8 families (16 sequences)** and say in the plan that it is a strengthening of D-10, not a departure. The op-only grain cannot see an SDP `supported` flip on 40 chips, which is squarely inside PRUNE-05's concern.

2. **Artifact + generator + drift test, or a Python literal in the test module?**
   - What we know: the artifact route is 3 new files and ~39 kB committed, with a per-chip readable diff; the literal route is 0 new files and pins families + counts + aggregates only.
   - What's unclear: how much the planner values "which chip moved" over file count.
   - Recommendation: **artifact route**, on D-11's grounds. Both are fully specified in §F so the planner can take either without further research.

3. **Does the ~37 s sweep run on every push?**
   - What we know: it is 12 % of a 302 s suite, not the 3 % the discussion assumed. No `slow` marker convention exists in this project.
   - What's unclear: the operator's tolerance.
   - Recommendation: **run it**, in its own module, so `--deselect <path>` is a one-flag escape without inventing a marker. CONTEXT notes Phase 174 set the same question aside for its own sweep; the module-split answer works for both.

4. **Where does the shared `_mock_operator` live?**
   - What we know: three divergent copies exist; no shared home; `tests/fixtures/` is excluded from ruff and mypy; `tests/*.py` top-level is not.
   - Recommendation: **`tests/plan_corpus.py`**, with `tests/conftest.py` as an acceptable second. Do not import from `tests/test_chip_test.py`.

5. **How should the 81-chip / 162-plan `0x0D` carve-out be expressed?**
   - What we know: as a *presence* assertion plus a counted, reason-matched carve-out, both green today.
   - What's unclear: whether the planner wants the count asserted absolutely (81/162) or only the reason string matched.
   - Recommendation: **assert both** — the absolute count is what catches a silent widening, and `test_erase_flag_invariants.py` already establishes absolute-count assertions as house style.

---

## Sources

### Primary (HIGH confidence) — read from source or measured this session

**Product code (read, never modified):**
- `firestarter_app/firestarter/chip_test.py` — `:300-344` (op vocabulary), `:406-445` (`Step`/`Plan`), `:486-520` (`derive_plan` signature + docstring), `:620-700` (`blank_check_step` construction, `erase_is_executable`), `:700-785` (write / verify / erase emission, the erase→blank-check relocation), `:786-845` (SDP-leg emission), `:914-1004` (op registries), `:1220-1263` (`_CYCLE_BLOCK_OPS`, `_CYCLE_BLOCK_START_OPS`, `cycle_block_bounds`), `:1582-1642` (`run_plan` + the `__plan__` guard), `:2639/:2726/:3056/:3123/:3309/:3341` (tempfile use and cleanup), `:3290-3298` (`_dispatch_sdp_leg`'s payload/expected-read-back triples)
- `firestarter_app/firestarter/cli_handlers.py` — `:110-122` (`AppContext`), `:2225-2232` (`_is_uv_eprom`), `:2236-2261` (`_resolve_write_scope`), `:2290-2312` (the stale comment block)
- `firestarter_app/pyproject.toml` — `:105-107` (pytest), `:109-132` (ruff), `:138-215` (mypy)
- `firestarter_app/.github/workflows/ci.yml` — `:53, 80-90` (py3.11, ruff scope, watermark, coverage)

**Test code (patterns to copy):**
- `tests/test_chip_test_sdp_leg.py:215-268` (`_REAL_DB`, `_OPERATOR_METHODS`, `_mock_operator`, `_plan_with_steps`, `_result`), `:268-324` (`_SHIPPED_OPS_SEQUENCE`), `:827-897` (`test_shipped_ops_never_reach_sdp_arm`)
- `tests/test_erase_flag_invariants.py:1-80` (anti-vacuity docstring), `:98` (`_REAL_DB`), `:113-132` (`_select_algorithm_13_rows`, `_all_rows`), `:264-371` (element-wise pins)
- `tests/test_op_registration_parity.py:1-60` (coverage taxonomy), `:126-190` (`_ALL_OPS`, the 13-count assert), `:265-295` (`_POLICED_REGISTRIES`, `_POLICED_REGISTRY_COUNT`), `:393-456` (exemption reasons), `:810-936` (the seven legs)
- `tests/test_chip_test.py:855-891` (UV region policy), `:961-979` (`is_uv` wiring), `:985-1100` (operator doubles), `:1453-1476` (`cycle_block_bounds` per family), `:2601-2612` (`len(results) == len(plan.steps)`)
- `tests/test_chip_test_blank_check_order.py:1-190` (blank-check placement, four chips)
- `tests/test_dev_test_cmd.py:96-112` (chip fixtures), `:708-801` (`TestUVWriteHasNoPrompt`)
- `tests/test_blast_radius_invariance.py:244-760` (frozen-hash and closure legs), `tests/test_rekey_ledger.py`, `tests/fixtures/rekey_ledger.py:1-30`, `tests/fixtures/shape_ids.json`
- `tests/test_part_number_delta_drift.py:1-45`, `tools/measure_part_number_delta.py:1-40, 224-302`
- `tests/conftest.py:241-345` (`make_app_context`, `app_context`)

**Measurements (all in `.venv311`, py3.11.16):** the `derive_plan` census, the `run_plan` sweep and its filesystem/console audit, the three timing trials, the `cProfile` hot-spot run, the four mutation legs, the erase/blank-check offender census, the UV pin census, the `_resolve_write_scope` sweep, the two AST scans, the three artifact prototypes, `pytest tests/ -o addopts="" -q` (302.20 s / 2108 passed), `pytest tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py` (114 passed / 1.57 s), `tools/check_mypy_watermark.py` (35/35).

**Planning inputs read in full:** `.planning/phases/175-.../175-CONTEXT.md`; `.planning/ROADMAP.md` §Phase 175; `.planning/REQUIREMENTS.md` §"Decisions taken at definition", §"No-Information Operations", §"Out of Scope", §Traceability; `.planning/research/SUMMARY.md` §Phase 175 + §"What NOT to do"; `.planning/research/PITFALLS.md` §Pitfall 3, §Pitfall 4; `.planning/phases/174-.../174-CONTEXT.md` §D-09…D-16 + §"Claude's Discretion"; `.planning/phases/174-.../174-PATTERNS.md`; `.planning/phases/174-.../174-06-PLAN.md` + `evidence/174-06-duplicate-row-red-green.txt`; `.planning/STATE.md` frontmatter only; `.planning/config.json`; `/workspaces/CLAUDE.md`; `/workspaces/firestarter_app/CLAUDE.md`.

### Secondary (MEDIUM confidence)
- Project skills at `/workspaces/.claude/skills/` — `devtest-rootcause`, `devtest-triage`, `find-skills`, `skill-creator`. None bears on a test-only sentinel phase; `devtest-rootcause`'s "the DB is GENERATED, never hand-edit it" rule is consistent with D-11 and is reflected in §Project Constraints.

### Tertiary (LOW confidence)
- None. **No web search, no external documentation lookup, and no package-registry query was performed or needed** — this phase adds no dependency and every question is answerable from this tree.

---

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — nothing is added; the two names given are read from the installed CI-replica venv.
- Architecture / patterns: **HIGH** — every pattern is a shipped module in this tree, cited by file and line range, with the load-bearing lines quoted verbatim.
- Measurements: **HIGH** — every number re-taken this session in the py3.11 venv against a clean tree; three of the four figures carried in from discussion were wrong and are corrected with the commands that produced the new ones.
- Pitfalls: **HIGH** — 1, 2, 4, 5, 6, 8, 9 were each measured or read from source; 3 is CONTEXT's own reasoning, confirmed; 7 is a confirmed environment fact.
- Open questions: **MEDIUM** — all five are planner/operator preference calls, each fully specified so no further research is needed to decide them.

**Research date:** 2026-09-04
**Measured against:** `firestarter_app @ c134530`, branch `gsd/v1.36-dev-test-fidelity`, both repos clean
**Valid until:** 2026-10-04, or **immediately invalid** if `firestarter/data/chip_database.json` is regenerated or `chip_test.py` / `cli_handlers.py` is modified — in which case re-take the §B, §C, §D, §E, §F and §G measurements before planning.
