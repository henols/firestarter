---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 01
subsystem: host-cli
tags: [sdp, capability-gate, chip-database, infoic-xml, pytest, ruff, mypy]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    provides: firmware CMD_SDP_LOCK/CMD_SDP_UNLOCK + FLASH_ENABLE_WRITE_PROTECTION wiring this predicate will gate
provides:
  - "firestarter/sdp_capability.py — a pure, name-keyed SDP capability predicate with a derived 65-token fail-closed allow-list"
  - "tests/test_sdp_capability.py — a machine-checked exhaustiveness/totality/non-vacuity gate over the shipped 84 protocol-0x0D chip_database.json entries"
affects: [120-05-host-cli-surface-wire-emission-capability-refusal, 120-08-host-cli-surface-wire-emission-capability-refusal, 120-09-host-cli-surface-wire-emission-capability-refusal]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Static fail-closed allow-list transcribed from a machine-readable partition artifact (120-sdp-partition.json), never re-derived by rule at runtime"
    - "Name-keyed predicate taking an injected db (not a resolve_chip() programmer dict) — the D-03 mechanism correction"
    - "Hard-fail (KeyError) instead of a silent default on an unexpected dict shape, to avoid reproducing the _SRAM_PROTO_IDS vacuity bug"

key-files:
  created:
    - firestarter_app/firestarter/sdp_capability.py
    - firestarter_app/tests/test_sdp_capability.py
  modified: []

key-decisions:
  - "Predicate is name-keyed (db.get_eprom(name)) with an injected db, not DB-loader-decoupled as CONTEXT.md D-03 originally specified — resolve_chip()'s programmer dict carries neither protocol-id nor name (RESEARCH F-06); D-03's semantics (pure, no serial/Click, -> (allowed, reason)) are preserved."
  - "sdp_capability_for_entry raises KeyError (never returns a silent False/True) when handed a dict with no protocol-id key, naming resolve_chip/convert_to_programmer as the likely wrong dict — this is the anti-vacuity behavior plan 120-05's shape leg will assert against."
  - "Kept the module's top-level import set to {__future__, typing} exactly as specified, importing Mapping from typing with a targeted `# noqa: UP035` rather than switching to collections.abc.Mapping (which would satisfy ruff's UP035 preference but break the plan's own AST-checked import-set invariant)."

patterns-established:
  - "Allow-list transcription discipline: production module docstring cites the exact minipro commit, section, and bit; test module holds an independently-transcribed REFUSE-side set so the exhaustiveness gate cannot degrade into a tautology against production."

requirements-completed: []  # HOST-04 spans plans 01/05/09 — only 120-09 may close it. Deliberately empty.

coverage:
  - id: D1
    description: "SDP_CAPABLE_TOKENS (65-token allow-set) + SDP_PROTOCOL_ID + FRAM_TOKENS + PRE_SDP_NAMED_TOKENS + split_part_number_tokens(), all transcribed from 120-sdp-partition.json with full provenance in the module docstring"
    verification:
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_allow_and_refuse_token_sets_are_disjoint_and_total"
        status: pass
    human_judgment: false
  - id: D2
    description: "sdp_capability()/sdp_capability_for_entry() name-keyed predicate with a 4-way refusal taxonomy (not found / wrong protocol / FRAM / not capable) plus a hard KeyError anti-vacuity failure mode"
    verification:
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_predicate_agrees_with_the_derived_partition_on_all_84_entries"
        status: pass
    human_judgment: false
  - id: D3
    description: "Core exhaustiveness gate: 84 shipped 0x0D entries partition exactly 43 ALLOW / 41 REFUSE, token-set equality against production SDP_CAPABLE_TOKENS, and a non-vacuity proof, with no skip marker"
    verification:
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_partition_covers_exactly_the_84_0x0d_entries"
        status: pass
      - kind: unit
        ref: "tests/test_sdp_capability.py::test_synthetic_unknown_0x0d_entry_is_refused_non_vacuous"
        status: pass
    human_judgment: false

# Metrics
duration: 15min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 01: SDP Capability Predicate + Exhaustiveness Gate Summary

**A pure, name-keyed `sdp_capability()` predicate in a new `firestarter/sdp_capability.py` module, backed by a 65-token fail-closed allow-list derived from `infoic.xml`'s `flags` bit 15, plus a machine-checked exhaustiveness gate proving the derived 43/41 partition is total, non-vacuous, and matches production token-for-token.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-29T10:11:08Z
- **Completed:** 2026-07-29T10:25:11Z
- **Tasks:** 3 (all `type="auto" tdd="true"` except Task 3, which was auto)
- **Files modified:** 2 (both new)

## Provenance carried into this plan

The SDP-capability partition landed by this plan is **derived, not curated**: minipro `infoic.xml` at commit `a8efaedc236c1d9718bd28299dfbb99536b010ff`, section `<database type="INFOIC2PLUS">`, `flags` **bit 15** (`0x8000`, `MP_PROTECT_AFTER`). It **supersedes** `120-RESEARCH.md` § F-01's curated 37/47 partition (and all five of its judgement calls) and the interim operator placeholder ("allow both disputed groups," ~74/10) — both existed only because the alternative was guessing, and the operator's own directive was *"there shall be no guessing — the ground truth is the infoic.xml."*

The refusal-cost trade-off the operator was originally asked to weigh (over-refusal costing a working `write` on a genuinely-locked part) is **dissolved, not decided**: for a part with no SDP command decoder there is nothing to unlock, so suppressing its auto-unlock is a no-op for that part *and* avoids storing three bytes as data at the bus-truncated magic addresses (F-120-01). Residual risk is confined to `120-SDP-PARTITION.md` §4's 9-entry watch-list (parts where `flags` bit 15 = 0 but `page_size > 1`) — none of which are AT28C-family and none of which are on the operator's bench.

## Accomplishments
- `firestarter_app/firestarter/sdp_capability.py`: `SDP_PROTOCOL_ID = 13`, `SDP_CAPABLE_TOKENS` (65 distinct uppercased tokens transcribed from the 43 ALLOW entries in `120-sdp-partition.json`, parentheticals retained verbatim), `FRAM_TOKENS`, `PRE_SDP_NAMED_TOKENS` (HOST-04's 12-token pre-SDP class), `split_part_number_tokens()`, and the five `REASON_*` constants.
- `sdp_capability_for_entry(entry, display_name)` and `sdp_capability(chip_name, db)`: a pure, name-keyed predicate evaluating (in order) not-found → wrong-protocol → FRAM → unanimity-not-capable → allowed, with the unanimity rule refusing a whole entry if *any* alias token is unrecognised (e.g. `EXEL/XL2816A,XLE28C16A,XLS28C16A` refuses wholesale even though two of its three tokens superficially resemble `28C`-generation parts).
- `sdp_capability_for_entry` raises `KeyError` — never a silent default — when handed a dict with no `protocol-id` key, naming `resolve_chip`/`convert_to_programmer` as the likely wrong dict shape; this directly targets the vacuity failure mode that made `check_eprom_blank`'s `_SRAM_PROTO_IDS` short-circuit unreachable in production (RESEARCH F-06).
- `firestarter_app/tests/test_sdp_capability.py`: a 4-leg core exhaustiveness gate — totality (84 shipped 0x0D entries partition exactly into 43 ALLOW / 41 REFUSE pairs, 81 distinct part_number strings, disjoint sets), token-set equality (134 token instances / 130 distinct / 65 ALLOW + 65 REFUSE disjoint, and the ALLOW-side set equals `sdp_capability.SDP_CAPABLE_TOKENS` exactly), predicate agreement (all 84 real DB entries agree with the derived partition, mismatches collected and reported together), and non-vacuity (a synthetic unrecognised `0x0D` part is refused by both the predicate and the totality helper). No skip marker of any kind.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule:

1. **Task 1: Create sdp_capability.py with the derived allow-set and provenance docstring** - `a1023ba` (feat)
2. **Task 2: Add the name-keyed sdp_capability predicate with a four-way refusal taxonomy** - `5e26fa8` (feat)
3. **Task 3: Ship the core exhaustiveness gate — 43/41 totality, per-entry predicate agreement, non-vacuity** - `7e00565` (test)

No plan-metadata commit in `firestarter_app` — this plan does not touch `.planning/`; the metadata commit for this plan lives in the meta repo (below).

_Note: both `sdp_capability_for_entry`/`sdp_capability` (Task 2) landed as edits to the same file Task 1 created — the module was written once with both the allow-set and the predicate present, then the two tasks were committed and independently re-verified against their own `<verify>` blocks in sequence, matching the plan's task boundary even though the code was authored together._

## Files Created/Modified
- `firestarter_app/firestarter/sdp_capability.py` — the derived 65-token allow-set + name-keyed `sdp_capability()`/`sdp_capability_for_entry()` predicate, fully provenance-documented.
- `firestarter_app/tests/test_sdp_capability.py` — the core exhaustiveness/totality/non-vacuity gate over the shipped 84 protocol-0x0D `chip_database.json` entries.

## Decisions Made
- **D-03 mechanism correction, re-confirmed in code:** the predicate is name-keyed (`db.get_eprom(chip_name)`) with an injected `db`, not the DB-loader-decoupled shape CONTEXT.md originally specified — `resolve_chip()`'s programmer dict has no `protocol-id`, no `electrical-type`, and no part number, so "no DB-loader coupling" was unachievable. Pure-function semantics (no serial, no Click, `-> (allowed, reason)`) are preserved.
- **Anti-vacuity as a hard failure, not a return value:** a dict missing `protocol-id` raises `KeyError` rather than defaulting to refuse-or-allow, because a silent default is exactly the mechanism that made `_SRAM_PROTO_IDS`'s short-circuit vacuous in production.
- **Import-set literal compliance over UP035:** kept `from typing import Any, Mapping` (with a targeted `# noqa: UP035`) instead of moving `Mapping` to `collections.abc`, because the plan's own verify command AST-asserts the module's import set is a subset of exactly `{"__future__", "typing"}`. Silencing the one deprecation-preference lint locally was the smaller deviation than breaking a plan-specified, machine-checked invariant.

## Deviations from Plan

**1. [Rule 3 - Blocking] Reordered `from __future__ import annotations` after the module docstring**
- **Found during:** Task 1, first `ruff check` run.
- **Issue:** The plan's action text said "Start the file with `from __future__ import annotations`," which — taken literally with the module docstring following it — makes the docstring a bare string-expression statement rather than the true module `__doc__`, and ruff's `E402` then flags the subsequent `from typing import` line as an import not at the top of the file.
- **Fix:** Moved the module docstring to be the file's first statement (standard Python convention: docstring, then `__future__` imports, then other imports) so it is the real `__doc__` and no import trails a non-import statement. Verified via `ast.get_docstring()` that all four required literals (`a8efaedc236c1d9718bd28299dfbb99536b010ff`, `INFOIC2PLUS`, `bit 15`, `120-SDP-PARTITION.md`) are present in the actual module docstring.
- **Files modified:** `firestarter_app/firestarter/sdp_capability.py`
- **Verification:** `ruff check` and `ruff format --check` both pass; `ast.get_docstring()` check passes.
- **Committed in:** `a1023ba` (Task 1 commit)

**2. [Rule 3 - Blocking] `# noqa: UP035` on `from typing import Any, Mapping`**
- **Found during:** Task 2, first `ruff check` run.
- **Issue:** Ruff's `UP035` rule (target `py39`) prefers `collections.abc.Mapping` over `typing.Mapping`. Switching to `collections.abc` would pass ruff cleanly but would add `collections` to the module's top-level import set, which the plan's Task 2 `<verify>` command explicitly AST-asserts is a subset of `{"__future__", "typing"}` — a literal, load-bearing D-03-purity check.
- **Fix:** Kept `Mapping` imported from `typing` and suppressed the single UP035 finding with an inline `# noqa: UP035`, documented with a comment explaining the tension.
- **Files modified:** `firestarter_app/firestarter/sdp_capability.py`
- **Verification:** `ruff check` passes; the AST import-set assertion (`mods <= {"__future__", "typing"}`) passes.
- **Committed in:** `5e26fa8` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 3 - blocking, both resolved within the same task before its commit).
**Impact on plan:** Both fixes are mechanical (import ordering, one targeted lint suppression) and preserve every literal invariant the plan's own verify commands check. No scope creep; no behavior change to the derived partition or predicate logic.

## Issues Encountered
None beyond the two deviations above.

## Non-regression checks (plan `<verification>` block, run in full)
- `python3 -m pytest tests/test_sdp_capability.py -q` — 4/4 passed.
- `python3 -m pytest` (full suite) — **985 passed, 1 failed**. The 1 failure is the pre-existing, out-of-scope `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` (stale golden, named in this plan's prohibitions as not-this-plan's-regression). No live board was attached this session, so `test_no_programmer_found_*` did not trigger its known-RED condition either way.
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` (CI-scoped) — all pass, 96 files already formatted.
- `python3 tools/check_mypy_watermark.py` — 1 error (watermark 35, pre-existing `firestarter/submit.py:446`) — unchanged.
- `git -C /workspaces/firestarter status --porcelain` — empty; `git -C /workspaces/firestarter rev-parse --short HEAD` — still `0048b3d`. Firmware sub-repo byte-untouched.
- `git -C /workspaces/firestarter_app diff --stat -- firestarter/data/ firestarter/messages.py tools/build_db.py` — empty. DB, codegen, and messages untouched.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `sdp_capability.py` is a self-contained, dependency-free (`__future__` + `typing` only) module ready for plan 120-05's shape leg (proving `db.get_eprom()` really produces the `name`/`protocol-id` shape this predicate expects for real parts) and for the CLI/wire call sites in plans 120-08/120-09.
- HOST-04 is **not** ticked by this plan — verified `.planning/REQUIREMENTS.md` still reads Pending for HOST-01 through HOST-06 (no edits were made to that file by this plan).
- No blockers. Both sub-repo working trees stayed clean throughout except for the two committed files above.

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/sdp_capability.py`
- FOUND: `firestarter_app/tests/test_sdp_capability.py`
- FOUND: `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-01-SUMMARY.md`
- FOUND commit `a1023ba` (Task 1)
- FOUND commit `5e26fa8` (Task 2)
- FOUND commit `7e00565` (Task 3)
