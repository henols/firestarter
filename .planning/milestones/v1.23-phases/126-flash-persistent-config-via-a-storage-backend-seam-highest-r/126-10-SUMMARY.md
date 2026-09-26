---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 10
subsystem: firmware-storage
tags: [py32f071, config, schema-pinning, textual-gate, cfg-07]

# Dependency graph
requires:
  - phase: 126-03
    provides: "the seam header (include/rurp_config_storage.h) and the common policy layer (src/rurp_config_utils.cpp) carrying the four public config functions"
  - phase: 126-08
    provides: "platform/py32f071/src/config.cpp deleted (PR #48's drift) with its four drift points recorded before deletion in 126-08-SUMMARY.md"
provides:
  - "firestarter/tests/test_config_schema_pinned.py — a 17-function committed gate enforcing CFG-07's two halves: rurp_configuration_t's four-field schema + CONFIG_VERSION literal + default resistances pinned; StoredConfiguration's D-17 whole-struct embedding; config.cpp verified absent by path; the four public config functions defined exactly once and never under platform/; all four declared in rurp_shield.h; the C-14 consumer census (corrected to the verified nine sites)"
  - "the plan-level CFG-07 evidence ledger (this SUMMARY): both header blob SHAs re-confirmed at their pre-phase values, an empty phase-scoped git log over both paths, the VER06 literal quoted, the absence proof carried forward with Plan 126-08's drift record, and firmware porcelain named to the repository"
affects: ["126-11 (the gated ARM CI run)", "126-12 (the only plan permitted to tick CFG-01..CFG-07)", "126-NONREGRESSION.md (re-executes the exact-bytes claim this ledger records)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Definition-vs-declaration census: a function DEFINITION is detected as NAME(...) immediately followed by '{' (never ';'), scanned across src/, platform/ and lib/ after comment-stripping — the same idiom used for the includer census in test_config_storage_seam_shape.py, applied here to catch a second per-platform reimplementation of a public function (the PR #48 shape) rather than a second includer of a header."
    - "tmp_path-built planted copies: every RED demonstration in this module writes a real mutated file under tmp_path and reads it back before feeding it to the shared helper, rather than mutating an in-memory string directly — the plan's explicit instruction for this module, stronger than the analog's mixed approach."

key-files:
  created:
    - firestarter/tests/test_config_schema_pinned.py
  modified: []

key-decisions:
  - "CORRECTED a miscount inherited from 126-RESEARCH.md's C-14 section: its heading and every prose reference call this 'the seven consumers', but its own read_first enumeration (reproduced verbatim in this plan's read_first block) lists NINE distinct (file, line) call sites across five files. The test function keeps the plan-specified name (test_the_seven_consumers_call_only_the_public_api) but its assertions use the verified count of nine, not the mislabeled seven — 'verified facts win' is this phase's own stated read-order precedence, and the same shape as Phase 121's corrected CONTEXT/ROADMAP miscounts. Documented in the module's own docstring and in the test's own docstring so a future reader is not confused by the name/count mismatch."
  - "Added a dedicated tenth function (test_absence_check_fires_when_config_cpp_is_planted) beyond the plan's six-case parametrized RED demonstration, per this dispatch's explicit anti-vacuity directive to prove the absence check (Coverage 5) fires on a planted scratch config.cpp, independent of the six-case list the plan names for test_helper_reports_violations_on_planted_copies."
  - "The four public config functions' 'definition' detector requires NAME(...) immediately followed by '{' (not ';'), after comment-stripping. This distinguishes a real definition from the many prose/comment/declaration occurrences of these names already in the tree (include/rurp_config_storage.h's own docstring names all four in prose, and several call sites end their line with '()' inside an if-condition) — verified against the live tree before writing the regex, not assumed."

requirements-completed: []  # CFG-07 spans 126-03 (schema untouched), 126-08 (deletion) and this plan (the gate). Only Plan 126-12 ticks CFG-01..CFG-07.

coverage:
  - id: D1
    description: "rurp_configuration_t's four fields (char version[6], long r1, long r2, uint8_t hardware_revision), in that order, pinned as a field-list-and-order assertion with no size or offset literal"
    requirement: "CFG-07"
    verification:
      - kind: unit
        ref: "tests/test_config_schema_pinned.py::test_rurp_configuration_t_has_exactly_the_four_pinned_fields"
        status: pass
    human_judgment: false
  - id: D2
    description: "CONFIG_VERSION pinned as the literal VER06; VALUE_R1/VALUE_R2 pinned at 270000/44000"
    requirement: "CFG-07"
    verification:
      - kind: unit
        ref: "tests/test_config_schema_pinned.py::test_config_version_literal_is_ver06"
        status: pass
      - kind: unit
        ref: "tests/test_config_schema_pinned.py::test_default_resistance_values_are_unchanged"
        status: pass
    human_judgment: false
  - id: D3
    description: "StoredConfiguration (D-17) asserted to embed rurp_configuration_t as a single whole member, with its own version member a uint16_t distinct from the embedded CONFIG_VERSION char[6]"
    requirement: "CFG-07"
    verification:
      - kind: unit
        ref: "tests/test_config_schema_pinned.py::test_stored_configuration_embeds_the_struct_whole"
        status: pass
    human_judgment: false
  - id: D4
    description: "platform/py32f071/src/config.cpp verified absent from the tree by path existence (Criterion 5), not by diff"
    requirement: "CFG-07"
    verification:
      - kind: unit
        ref: "tests/test_config_schema_pinned.py::test_pr48_config_cpp_is_absent_from_the_tree"
        status: pass
      - kind: unit
        ref: "tests/test_config_schema_pinned.py::test_absence_check_fires_when_config_cpp_is_planted"
        status: pass
    human_judgment: false
  - id: D5
    description: "The four public config functions (rurp_get_config/rurp_load_config/rurp_save_config/rurp_validate_config) defined exactly once, in src/rurp_config_utils.cpp, never under platform/ — the standing guard against PR #48's drift reappearing — and all four declared in include/rurp_shield.h"
    requirement: "CFG-07"
    verification:
      - kind: unit
        ref: "tests/test_config_schema_pinned.py::test_the_four_public_functions_are_defined_exactly_once"
        status: pass
      - kind: unit
        ref: "tests/test_config_schema_pinned.py::test_the_four_public_functions_are_declared_in_rurp_shield_h"
        status: pass
    human_judgment: false
  - id: D6
    description: "The C-14 consumer census (corrected to nine verified sites) confirms every consumer sits above the seam and calls only the four public functions"
    requirement: "CFG-07"
    verification:
      - kind: unit
        ref: "tests/test_config_schema_pinned.py::test_the_seven_consumers_call_only_the_public_api"
        status: pass
    human_judgment: false
  - id: D7
    description: "Every assertion demonstrated able to fail: six planted mutations (tmp_path-built) plus the dedicated absence-check demonstration, each producing a non-empty violation list; no committed file mutated (three blob SHAs re-checked before/after)"
    verification:
      - kind: unit
        ref: "tests/test_config_schema_pinned.py::test_helper_reports_violations_on_planted_copies (6 parametrized cases)"
        status: pass
    human_judgment: false
  - id: D8
    description: "No AVR-visible regression: pytest tests/ grew by exactly 17 (153 -> 170); both pinned native envs unchanged at 141/141 across 17 suites; manifest gate unchanged at 26 enforced sources"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/ -q (170 passed); pio test -e native and -e native_nodevtools (141 test cases: 141 succeeded, 17 suites, each); python3 scripts/check_cmake_manifest.py (PASS, 26 enforced)"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-08-01
status: complete
---

# Phase 126 Plan 10: The CFG-07 Schema-and-Deletion Gate Summary

**A 17-function committed pytest gate (`tests/test_config_schema_pinned.py`) pins `rurp_configuration_t`'s four-field schema, the `VER06`/`270000`/`44000` literals, `StoredConfiguration`'s D-17 whole-struct embedding, `config.cpp`'s absence by path, and the four public config functions' single-definition/never-under-`platform/` invariant — every assertion demonstrated able to fail on a `tmp_path`-planted copy, and a corrected miscount (nine verified C-14 consumer sites, not RESEARCH.md's mislabeled seven) carried forward explicitly.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-01T00:54:03Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments

- Authored `firestarter/tests/test_config_schema_pinned.py`: 17 test functions (12 named coverage items, one of which is a 6-case parametrized RED demonstration) gating both halves of CFG-07.
- Schema half: `rurp_configuration_t`'s four fields — `char version[6]`, `long r1`, `long r2`, `uint8_t hardware_revision` — asserted by name, type and **order**, with no size or offset literal anywhere in the module (host `long` is 8 bytes, the target's is 4; `g++ -m32` is unavailable, per C-6). `CONFIG_VERSION` asserted as the literal `"VER06"`; `VALUE_R1`/`VALUE_R2` asserted at `270000`/`44000`.
- D-17 half: `StoredConfiguration` (in `platform/py32f071/src/config_storage_dualslot.h`) asserted to embed `rurp_configuration_t` as a single named member (never inlined), with its own top-level `version` member asserted `uint16_t`, distinct from the embedded struct's `char[6]` `CONFIG_VERSION` literal.
- Deletion half: `platform/py32f071/src/config.cpp` asserted absent by path existence (Criterion 5's verified-by-absence, never a diff) — with a **dedicated second RED demonstration** (`test_absence_check_fires_when_config_cpp_is_planted`) planting a scratch `config.cpp` under `tmp_path` and confirming the same helper fires, per this dispatch's explicit anti-vacuity directive that an absence check is the easiest kind to write vacuously.
- D-07 half (the standing anti-drift guard): the four public config functions (`rurp_get_config`, `rurp_load_config`, `rurp_save_config`, `rurp_validate_config`) asserted defined **exactly once**, located in `src/rurp_config_utils.cpp`, with **none anywhere under `platform/`** — the exact shape that would let PR #48's drift reappear undetected. All four also asserted declared in `include/rurp_shield.h`.
- C-14 consumer census: all nine verified `(file, line, function)` call sites — `src/firestarter.cpp:40,99,105`; `src/boards/rurp_common.cpp:53`; `include/rurp_hw_rev_utils.h:95,101`; `src/hardware_operations.cpp:106,118`; `platform/py32f071/src/py32f071_rurp_shield.cpp:297` — located and asserted to call only the four public functions, with the found count asserted equal to nine exactly.
- Six planted-mutation RED demonstrations, each building a real file under `tmp_path` (never touching a committed file) and feeding it to the same module-level helper the corresponding positive test calls: a fifth struct member; a reordered field list; a changed `CONFIG_VERSION` literal; a changed `VALUE_R1`; a second definition of `rurp_validate_config` under a scratch `platform/` tree; and a `StoredConfiguration` with the struct's fields inlined instead of embedded. All six produced a non-empty violation list on the first run.
- No blob SHA literal appears anywhere in the module (verified by grep); the only SHA computation the module performs is self-referential (before/after each planted-copy demonstration).
- No skip call or conditional-skip marker anywhere in the module, self-enforced by the copied-verbatim concatenation-trick leg.

## Task Commits

Each task was committed atomically (firmware submodule, `/workspaces/firestarter`, branch `v1.23-py32f071-integration`):

1. **Task 1: Author tests/test_config_schema_pinned.py — the CFG-07 gate** — `240fb19` (test) — `firestarter/tests/test_config_schema_pinned.py` (created)
2. **Task 2: Record the CFG-07 evidence ledger at plan level** — no file changes (evidence recorded below and in this SUMMARY only)

**Plan metadata:** this SUMMARY commit (docs, meta repo)

## Files Created/Modified

- `firestarter/tests/test_config_schema_pinned.py` — new (709 lines). MIT header, `Phase 126 Plan 10` attribution, `Requirements: CFG-07`, `Decisions covered: D-01, D-07, D-17`, the no-CI-leg statement, self-contained-path note, a 12-item `Coverage:` list, and both required reasoning paragraphs (PR #48's four drift points, and why the schema pin outlives this phase). 17 test functions total (module-level helpers factored so positive tests and RED demonstrations share code, per Phase 124 D-14's "a guard that supplies the answer it tests is structurally dead").

## CFG-07 Evidence Ledger (Task 2)

Recorded as observed values, per this plan's Task 2 action text:

- `git hash-object include/rurp_types.h` = `d3fe5203a91527bdb7b20a33843c81065e21c613` — **matches the pre-phase value**. No STOP finding.
- `git hash-object include/rurp_shield.h` = `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` — **matches the pre-phase value**. No STOP finding.
- Phase-scoped `git log --oneline -- include/rurp_types.h include/rurp_shield.h`, range `fd84820~1..HEAD` (`fd84820` is Plan 126-01's first commit; HEAD is this plan's commit `240fb19`): **empty**. The last commit touching either path anywhere in history is `e2c422d` (`feat(124-04)`), which predates Phase 126 entirely.
- `CONFIG_VERSION` line, verbatim, `include/rurp_shield.h:46`: `#define CONFIG_VERSION "VER06"` — still the literal `VER06`.
- `platform/py32f071/src/config.cpp` absence: confirmed by `test ! -e` (exit 0, "config.cpp ABSENT"). Carried forward from Plan 126-08 (deletion commit `5b08495` in the firmware submodule) and its four recorded drift points: (1) a private static `configuration` instead of the shared `rurp_config` global; (2) a second, drifted `rurp_validate_config` with an extra `|| r2 == 0` disjunct and a leading `memset` neither present in the common policy; (3) no write-back call at all inside `rurp_load_config`, so a virgin part's defaults were computed but never persisted; (4) a `rurp_save_config` that validated, assigned to the private static, and persisted nothing. **This drift record now exists only in `126-08-SUMMARY.md`; this ledger and the new gate's docstring carry it forward.**
- `git status --porcelain` for `/workspaces/firestarter`, named by repository: **0 lines** (clean working tree after this plan's single commit). No pre-existing lines were observed in this environment at ledger time (differs from the plan's anticipated "five known pre-existing lines" — none were present when this ledger was recorded).
- `pytest tests/ -q`: **170 passed** (153 before this plan's Task 1 commit, +17 from the new module — exactly the module's function count, zero regressions).
- `pio test -e native`: **141 test cases: 141 succeeded**, 17 suites.
- `pio test -e native_nodevtools`: **141 test cases: 141 succeeded**, 17 suites.
- `python3 scripts/check_cmake_manifest.py`: **PASS** — 26 enforced source(s) resolved; 15 `PY32_SDK_SOURCES` exempt; 5 allow-listed omissions (`src/boards/leonardo_rurp_shield.cpp`, `src/boards/rurp_common.cpp`, `src/boards/rurp_config_storage_eeprom.cpp`, `src/boards/uno_rurp_shield.cpp`, `src/dev_tools.cpp`).

**Division of labour, stated explicitly:** the **committed gate** (`tests/test_config_schema_pinned.py`) uses textual anchors (field names/order, macro literals, path existence, definition census) and will keep working across future milestones without needing a hash update. The **exact-bytes claim** (both header blob SHAs unchanged since before the phase) is this phase's plan-level record, captured here and re-executed by `126-NONREGRESSION.md`. A path-scoped `git diff` is corroboration only, never the primary proof — `124-VERIFICATION.md` recorded that shape passing vacuously on a wrong path, which is exactly why Criterion 5 is worded as absence-from-the-tree rather than diff-based.

**Gitignored py32 worktrees:** not touched by this plan (no writes attempted; both worktrees are outside this plan's scope entirely).

**Branch re-check (both repos, RESEARCH Pitfall 7):** `git -C /workspaces/firestarter rev-parse --abbrev-ref HEAD` → `v1.23-py32f071-integration` after the commit. Meta repo remains on `gsd/v1.23-py32f071-integration` for the SUMMARY commit.

**No requirement checkbox ticked:** confirmed — CFG-07 (and CFG-01..CFG-06) remain unticked in `.planning/REQUIREMENTS.md`; only Plan 126-12 may tick them.

## Decisions Made

- Corrected RESEARCH.md's C-14 "seven consumers" mislabel to the verified nine call sites its own enumeration lists, keeping the plan-specified test function name but asserting the correct count (documented in both the module docstring and the test's own docstring, and in `key-decisions` above).
- Added a dedicated tenth RED-demonstration function for the absence check specifically, beyond the plan's six-case parametrized list, per this dispatch's explicit anti-vacuity directive.
- Used a comment-stripped "`NAME(...)` immediately followed by `{`, never `;`" regex to distinguish a function *definition* from the many prose/declaration/call-site occurrences of the same four names already in the tree (verified against the live tree's actual occurrences before writing the regex — `include/rurp_config_storage.h`'s own docstring names all four in prose, and several call sites end mid-line inside an `if` condition).
- Searched `src/`, `platform/` and `lib/` (not `include/`) for the definition census, matching the plan's action text exactly — the public functions are declared, never defined, in `include/rurp_shield.h`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected RESEARCH.md's C-14 consumer count from "seven" to the verified nine**
- **Found during:** Task 1, while building `_C14_CONSUMER_SITES` from the plan's `read_first` enumeration.
- **Issue:** `126-RESEARCH.md`'s C-14 section (and six other locations in that document) label this "the seven consumers of the config API", but the same section's own enumerated list — reproduced verbatim in this plan's `read_first` block — names nine distinct `(file, line)` call sites across five files: `src/firestarter.cpp:40,99,105`; `src/boards/rurp_common.cpp:53`; `include/rurp_hw_rev_utils.h:95,101`; `src/hardware_operations.cpp:106,118`; `platform/py32f071/src/py32f071_rurp_shield.cpp:297`. Asserting `== 7` against a correct nine-item enumeration would either fail spuriously or force dropping two real, verified consumer sites.
- **Fix:** Kept the plan-specified function name (`test_the_seven_consumers_call_only_the_public_api`) but implemented the census against all nine verified sites, asserting `found == len(sites) == 9`. Documented the correction in the module's own docstring (Coverage 8) and the test function's own docstring, so a future reader is not misled by the name/count mismatch.
- **Files modified:** `firestarter/tests/test_config_schema_pinned.py` (within Task 1's single commit — not a separate fix commit).
- **Verification:** `test_the_seven_consumers_call_only_the_public_api` passes, locating and asserting exactly 9 sites, each verified by direct line-content inspection against the live tree (`grep -n` cross-checked at pattern-map time, matching the plan's stated line numbers exactly).
- **Commit:** `240fb19` (part of Task 1's commit, caught before commit during authoring).

---

**Total deviations:** 1 auto-fixed (Rule 1 — a verified-count correction carried from an upstream research-document mislabel, caught before the module was committed).
**Impact on plan:** No scope creep. The correction only changes the *number* asserted (nine, matching the plan's own enumerated evidence) — it does not add, remove or reinterpret any of the plan's required assertions, and the function keeps its plan-specified name.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None — no external service configuration required.

## Non-Claims (Claim Ceiling, explicit)

- This module reads source text and compiles nothing. It makes no build or runtime claim — see `.planning/REQUIREMENTS.md`'s "Validation Ceiling" section.
- No PY32F071 silicon exists; nothing here claims behaviour observed on real hardware.
- The ARM link is **not** proven here — `arm-none-eabi-gcc`/`cmake`/`ninja` remain absent from this environment (unchanged from Plan 126-08's non-claim). Plan 126-11's gated CI run remains the sole authoritative evidence for the ARM target.

## Next Phase Readiness

- CFG-07 is now an exit code in both halves at the plan-commit level: the schema/version/resistance/embedding assertions and the deletion-by-absence assertion are all committed, green, and each demonstrated able to fail.
- The plan-level evidence ledger above is ready for `126-NONREGRESSION.md` (Plan 126-12) to re-execute the exact-bytes claim.
- No requirement checkbox was ticked; CFG-01 through CFG-07 remain `[ ]`, ready for Plan 126-12 to close.
- No blockers. `pytest tests/` at 170; both native envs at 141/141 across 17 suites; manifest gate at 26 enforced sources; both repos on their expected branches.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: `firestarter/tests/test_config_schema_pinned.py`
- FOUND: commit `240fb19` in `/workspaces/firestarter` history
- FOUND: this SUMMARY.md at the meta path
