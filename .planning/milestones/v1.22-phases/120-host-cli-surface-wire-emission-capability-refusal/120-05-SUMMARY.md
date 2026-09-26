---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 05
subsystem: host-cli
tags: [sdp, capability-gate, chip-database, infoic-xml, pytest, ruff, mypy, ast]

# Dependency graph
requires:
  - phase: 120-host-cli-surface-wire-emission-capability-refusal
    provides: "plan 120-01's sdp_capability.py predicate + core exhaustiveness gate this plan extends"
provides:
  - "tests/test_sdp_capability.py — 8 additional legs proving the derived partition's structure, the predicate's non-vacuity, and fail-closed runtime behavior through the local-override merge seam"
affects: [120-08-host-cli-surface-wire-emission-capability-refusal, 120-09-host-cli-surface-wire-emission-capability-refusal, 120-11-host-cli-surface-wire-emission-capability-refusal]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "AST-based import-purity assertion (parse the module, walk only tree.body, assert top-level import set subset) as a stable machine-checked gate for a later phase's own gate"
    - "Fail-closed proof exercised through the documented runtime merge seam (patch firestarter.config.DATABASE_FILE) rather than only against literal test dicts, so the property holds on the one path CI cannot otherwise see"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_sdp_capability.py

key-decisions:
  - "Task 1's five legs (named refusals + structural invariants) reuse the module's existing minimal-literal-dict idiom ({\"name\": ..., \"protocol-id\": ...} built from the shipped chip_database.json), matching plan 120-01's own documented convention for legs whose subject is the shipped ground truth, not resolve_chip()'s output."
  - "Task 2's shape leg is the one leg in the file required to use a real EpromDatabase(skip_local_override=True) + resolve_chip() rather than a literal, per the plan's explicit prohibition against faking the shape it exists to prove."
  - "Local-override leg isolates the config dir via patch(\"firestarter.config.DATABASE_FILE\", ...) — the same idiom test_config.py already uses — rather than the FIRESTARTER_CONFIG_DIR env var, because config.py's DATABASE_FILE/PIN_MAP_FILE constants are computed once at import time from HOME_PATH; setting the env var after config.py is already imported (as it is, transitively, by the time this test module runs) would not move them. PIN_MAP_FILE is patched to a nonexistent path in the same test so no local pin-map file — real or otherwise — is read."
  - "The synthetic local-override entry uses a manufacturer key not present in the shipped DB (SYNTHETIC_LOCAL_MFR_120_05), taking _merge_databases's simpler 'entirely new key' branch rather than its name-matching update-existing-entry branch — avoids any risk of colliding with or mutating a real shipped entry."

patterns-established:
  - "A plan-level test file can be built and verified as one coherent unit, then split into per-task commits by reverting to an intermediate Task-N-only state, re-verifying, committing, and re-applying the remainder — used here since both tasks touch the same single file."

requirements-completed: []  # HOST-04 spans plans 01/05/09 — only 120-09 may close it. Deliberately empty; verified Pending after this plan.

coverage:
  - id: D1
    description: "All 19 DIP24_2816 parts, both FRAM parts, the 8 HOST-04-named pre-SDP entries, and all 9 adapter-required parts are refused with the correct reason"
    verification:
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_all_dip24_2816_parts_are_refused"
        status: pass
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_both_fram_parts_are_refused_with_the_fram_reason"
        status: pass
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_host04_named_pre_sdp_class_is_refused"
        status: pass
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_all_nine_adapter_required_parts_are_refused_by_capability"
        status: pass
    human_judgment: false
  - id: D2
    description: "The two derived structural invariants (no adapter-required part, no DIP24_2816 part on the allow-set) hold as consequences of the derivation"
    verification:
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_allow_set_contains_no_adapter_required_and_no_dip24_2816_part"
        status: pass
    human_judgment: false
  - id: D3
    description: "F-06 dict-shape anti-vacuity: resolve_chip()'s real programmer dict lacks protocol-id/name/electrical-type; sdp_capability is name-keyed and does not need it; sdp_capability_for_entry raises on that dict rather than silently defaulting"
    verification:
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_predicate_is_name_keyed_and_a_programmer_dict_is_rejected"
        status: pass
    human_judgment: false
  - id: D4
    description: "Import purity: sdp_capability.py's top-level imports are a subset of {__future__, typing}, pinned via AST for Phase 121's GATE-01"
    verification:
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_sdp_capability_module_imports_nothing_but_stdlib_typing"
        status: pass
    human_judgment: false
  - id: D5
    description: "A synthetic algorithm==13 entry reaching the live DB only through the ~/.firestarter/database.json merge seam (invisible to CI) is refused at runtime"
    verification:
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_local_override_0x0d_entry_is_refused_at_runtime"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 05: HOST-04 Gate Extension — Structure, Anti-Vacuity, and Runtime Fail-Closed Legs Summary

**Eight additional legs in `tests/test_sdp_capability.py` proving the derived SDP-capability partition is *structured as derived* (not merely total), that the predicate is *not silently vacuous* on the real `resolve_chip()` dict shape, and that fail-closed refusal holds on the one runtime path — a user's `~/.firestarter/database.json` override — that CI can never see.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-29
- **Completed:** 2026-07-29
- **Tasks:** 2 (both `type="auto"`)
- **Files modified:** 1 (`firestarter_app/tests/test_sdp_capability.py`)

## Accomplishments

- **Task 1 — named-refusal and structural-invariant legs (5 new tests):**
  - `test_all_dip24_2816_parts_are_refused`: all 19 `DIP24_2816` algorithm==13 entries refuse with `REASON_NOT_CAPABLE` — the highest-harm group under F-120-01, now a *derived* fact from `infoic.xml` bit 15 rather than a curated judgement call.
  - `test_both_fram_parts_are_refused_with_the_fram_reason`: both FRAM parts (`FM28V020`, `MB85R256H`) refuse with `REASON_FRAM` present **and** `REASON_NOT_CAPABLE` absent — proving the FRAM branch fires ahead of the generic allow-list branch.
  - `test_host04_named_pre_sdp_class_is_refused`: exactly the 8 entries whose token set intersects `PRE_SDP_NAMED_TOKENS` (spanning two pinouts — `2817` on `DIP28_28C64`, `2804`/`2816` on `DIP24_2816` — RESEARCH F-03) all refuse.
  - `test_all_nine_adapter_required_parts_are_refused_by_capability`: all 9 `support_status == "adapter-required"` algorithm==13 entries refuse by capability — D-08's capability-before-support-status ordering exercised on the whole population, not a hypothetical subset.
  - `test_allow_set_contains_no_adapter_required_and_no_dip24_2816_part`: the two structural invariants — consequences of the derivation the partition happens to satisfy, never its rule (F-03 still holds: `DIP28_28C64` splits 15 ALLOW / 20 REFUSE).
- **Task 2 — F-06 shape, import-purity, and local-override legs (3 new tests):**
  - `test_predicate_is_name_keyed_and_a_programmer_dict_is_rejected`: builds a **real** `EpromDatabase(skip_local_override=True)` and calls `resolve_chip("at28c256", db=real_db)`; asserts the resulting programmer dict has none of `protocol-id`/`name`/`electrical-type`; asserts `sdp_capability("at28c256", real_db)` returns `(True, ...)` (proving the predicate is name-keyed and does not need that dict); asserts handing the programmer dict directly to `sdp_capability_for_entry` **raises `KeyError`**.
  - `test_sdp_capability_module_imports_nothing_but_stdlib_typing`: parses `sdp_capability.py` with `ast`, walks only `tree.body` (true top-level), and asserts the import-module set is a subset of `{"__future__", "typing"}`.
  - `test_local_override_0x0d_entry_is_refused_at_runtime`: writes a synthetic `algorithm: 13` entry under a manufacturer key not present in the shipped DB, patches `firestarter.config.DATABASE_FILE` (and `PIN_MAP_FILE`, to a nonexistent path) to isolate the config dir, constructs a real `EpromDatabase()` (not `skip_local_override`) so the entry merges in through the real seam, then asserts `sdp_capability` refuses it with `REASON_NOT_CAPABLE`.
- Module docstring's Coverage list extended with items 5–12, one per new leg, matching the plan's read-first instruction not to duplicate the existing numbered list.

## The highest-severity finding this plan defends against, now machine-checked

`resolve_chip(name, db)` returns `db.convert_to_programmer(db.get_eprom(name))`, whose measured keys are exactly `memory-size`, `algorithm`, `pin-count`, `vpp_mv`, `pulse-delay`, `chip-id`, `flags`, `bus-config`, `page-size` — **no `protocol-id`, no `electrical-type`, no `name`**. `check_eprom_blank`'s `_SRAM_PROTO_IDS` short-circuit reads exactly those two absent keys and was measured returning `False` for a real SRAM part; both its production callers (`cli_handlers.py:576`, `chip_test.py:737`) pass that same dict, so the short-circuit is vacuous in production. **This validation surface — a shape leg proving a predicate raises rather than silently misreading the wrong dict — is one this phase *invents*: the nearest in-tree precedent (`_SRAM_PROTO_IDS`) lacks it, and lacking it is exactly why that precedent went vacuous.**

PROJECT.md SIXTH CORRECTION item 6's **KEEP disposition for `_SRAM_PROTO_IDS` stands** — this plan changes no production code in `eprom_operations.py` (`git diff --stat -- firestarter/eprom_operations.py` empty, confirmed below). Only the *stated reason* for that KEEP (that the short-circuit fires and produces a better message) is corrected — it does not fire in production. Plan 120-11 carries the PROJECT.md correction; this plan only records the finding in test form.

## Task Commits

Committed atomically inside the `firestarter_app` submodule, on branch `v1.22-at28c-software-data-protection-lifecycle`:

1. **Task 1: Add the named-refusal and structural-invariant legs** — `649fde7` (test)
2. **Task 2: Add the F-06 dict-shape anti-vacuity leg, the import-purity leg, and the runtime local-override refusal leg** — `d82d23a` (test)

Both commits touch the same single file (`tests/test_sdp_capability.py`); the plan-metadata commit for this plan lives in the meta repo (below), not in `firestarter_app`.

## Files Created/Modified

- `firestarter_app/tests/test_sdp_capability.py` — extended from 4 legs (plan 120-01) to 12 legs total; no new production files.

## Decisions Made

- All nine `adapter-required` parts are refused by capability, so D-08's capability-before-support-status ordering is exercised on the entire population this milestone cares about, not a hypothetical subset — plan 120-08 asserts the CLI-level ordering separately; this plan establishes the population it applies to.
- The two structural invariants (no adapter-required, no DIP24_2816 on the allow-set) are asserted as **consequences** of the derivation, never as the derivation's rule — RESEARCH F-03's "no structural rule expresses this partition" still holds, since `DIP28_28C64` splits 15 ALLOW / 20 REFUSE.
- The local-override leg's isolation idiom is `patch("firestarter.config.DATABASE_FILE", ...)` (matching `test_config.py`'s existing pattern), not `FIRESTARTER_CONFIG_DIR` monkeypatching — `config.py`'s `DATABASE_FILE`/`PIN_MAP_FILE` module constants are resolved once at import time from `HOME_PATH`, so an env-var patch applied after `config.py` is already imported (which it is, transitively, well before this test module runs in the full suite) would have no effect on those constants.

## Deviations from Plan

None — plan executed exactly as written. No Rule 1/2/3 auto-fixes were needed; both tasks' acceptance criteria were met on the first implementation pass.

## Issues Encountered

None.

## Non-regression checks (plan `<verification>` block, run in full)

- `python3 -m pytest tests/test_sdp_capability.py -q` — 12/12 passed (4 from plan 120-01 + 8 from this plan).
- `python3 -m pytest tests/test_sdp_capability.py tests/test_eprom_operations.py tests/test_cli_handlers.py -q` — all green (per Task 2's `<verify>` block).
- `python3 -m pytest` (full suite) — **1 failed**, the pre-existing, out-of-scope `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` (stale golden: 186034 vs 184631 bytes), named in this plan's dispatch context as not-this-plan's-regression. No live board was attached this session.
- `ruff check tests/test_sdp_capability.py` and `ruff format --check tests/test_sdp_capability.py` — pass.
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` (CI-scoped) — all pass, 96 files already formatted.
- `python3 tools/check_mypy_watermark.py` — 1 error (watermark 35) — unchanged from plan 120-01's baseline.
- `git diff --stat -- firestarter/eprom_operations.py` — empty. `eprom_operations.py` untouched by this plan.
- `git -C /workspaces/firestarter status --porcelain` — empty; `git -C /workspaces/firestarter rev-parse --short HEAD` — still `0048b3d`. Firmware sub-repo byte-untouched.
- `git -C /workspaces/firestarter_app diff --stat -- firestarter/data/ firestarter/messages.py firestarter/eprom_operations.py` — empty. DB, codegen, and operations layer untouched.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `tests/test_sdp_capability.py` now carries 12 legs covering totality, token-set equality, predicate agreement, non-vacuity (plan 120-01), named refusals, structural invariants, F-06 shape anti-vacuity, import purity, and runtime local-override refusal (this plan).
- The import-purity leg gives Phase 121's GATE-01 a stable, machine-checked shape to assert against.
- HOST-04 is **not** ticked by this plan — verified `.planning/REQUIREMENTS.md` still reads Pending for HOST-01 through HOST-06 after this plan's commits (no edits were made to that file).
- No blockers. Both sub-repo working trees stayed clean throughout except for the two committed hunks of the single file above.

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_sdp_capability.py`
- FOUND: `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-05-SUMMARY.md`
- FOUND commit `649fde7` (Task 1)
- FOUND commit `d82d23a` (Task 2)
