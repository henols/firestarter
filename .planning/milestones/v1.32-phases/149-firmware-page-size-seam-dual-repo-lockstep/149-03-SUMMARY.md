---
phase: 149-firmware-page-size-seam-dual-repo-lockstep
plan: 03
subsystem: chip-database-generator
tags: [chip-database, provenance, page-size, golden-fixtures, pytest, ruff]

# Dependency graph
requires:
  - phase: 149-01
    provides: "149-PAGE-SIZE.md skeleton carrying the D-01 upstream-provenance table and the fork-point cold baseline this plan's DB-side section extends"
  - phase: 149-02
    provides: "149-check-claims.py D-19 claim gate armed against 149-PAGE-SIZE.md, which this plan's edited artifact must still pass"
provides:
  - "the provenance-keyed page_size emit arm in build_db.py, keyed on each <ic>'s OWN upstream protocol_id (captured before classify() reassigns it), not the post-classification algorithm"
  - "regenerated chip_database.json: exactly 18 upstream-native protocol_id==0x0D rows gain programming.page_size (15 at 128, 3 at 64); the 66 promoted rows and AT28C256 unchanged"
  - "tests/test_page_size_invariants.py: 11-leg D-07 exhaustive host proof (selection, power-of-two/range, provenance, AT28C256 non-change, support_status byte-identity, extra_chips.json back door, 2 synthetic non-vacuity legs)"
  - "tests/golden/wire_dict_expected_deltas_149.json: committed, programmatically-generated 18-entry wire delta list (D-17)"
  - "test_live_capture_matches_golden_plus_the_149_deltas: renamed 4-assertion golden test (anti-laundering, non-vacuity, exact count, golden-plus-deltas)"
  - "the DB-side evidence section of 149-PAGE-SIZE.md, including the X-1 correction to 149-CONTEXT.md"
affects: [149-04, 149-05, 149-06, 149-07, 149-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Capture a variable's pre-resolution value under a new name before a downstream function reassigns it in a tuple-unpack (classify()'s `_etype, proto_id, pinout_key = classify(...)` overwrites proto_id with the resolved algorithm) -- reading the SAME name post-assignment silently reads the wrong population"
    - "Golden preserved + committed programmatic delta list (D-17): never re-derive a golden by hand, generate the delta from a live capture against the untouched golden, then assert anti-laundering + non-vacuity + exact-count + sum-equals-live"
    - "A generated-DB golden's own how_to_update note is itself the authorization to re-derive a count it did not anticipate -- re-run the SAME traversal the test uses, never hand-edit the number"

key-files:
  created:
    - firestarter_app/tests/test_page_size_invariants.py
    - firestarter_app/tests/golden/wire_dict_expected_deltas_149.json
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-DB-TRANSCRIPTS.md
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/firestarter/database.py
    - firestarter_app/firestarter/constants.py
    - firestarter_app/tests/test_wire_dict_equivalence.py
    - firestarter_app/tests/golden/chip_database_field_inventory.json
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md

key-decisions:
  - "Captured _upstream_proto_id immediately before classify()'s tuple-unpack reassigns proto_id to the resolved algorithm -- the emit arm reads _upstream_proto_id, never the post-classification proto_id classify() returns, which is exactly the value the plan's own read_first notes said the emitter must avoid"
  - "Re-derived tests/golden/chip_database_field_inventory.json's programming.page_size count from 2 to 20 -- a neighbouring golden not named in this plan's files_modified list, but broken by this plan's own regeneration and re-derived per that golden's own committed how_to_update instruction (independent traversal, never a hand-edited number), with every other one of its ~25 counts confirmed unchanged"
  - "Described the two corrected stale build_db.py comments in 149-PAGE-SIZE.md without quoting their literal forbidden-phrase text (the old comment made an unqualified correctness claim about the firmware heuristic) -- the claim gate flags the bare word even when quoted as a description of what was wrong, mirroring plan 02's docstring fix"

patterns-established:
  - "The D-07 host proof's own non-coverage statement (it iterates the generated DB, not a live ~/.firestarter/database.json override) is written into both the test module's docstring and 149-PAGE-SIZE.md, naming the firmware-side D-07 fallback (plan 04) as the reason that half is load-bearing rather than belt-and-braces"

requirements-completed: []  # PGSZ-01/PGSZ-05 span multiple plans; per this phase's planner_decisions, plan 08 alone flips PGSZ-0N checkboxes after the whole-phase gate is green

# Metrics
duration: ~50min
completed: 2026-08-19
status: complete
---

# Phase 149 Plan 03: Provenance-Keyed Page-Size Emit Arm (DB-side) Summary

**Added a provenance-keyed emit rule to `build_db.py` that delivers `programming.page_size` for exactly the 18 upstream-native protocol-`0x0D` rows (15 at 128, 3 at 64), proved it exhaustively with an 11-leg host invariant suite, and preserved Phase 148's wire golden with a committed 18-entry delta list instead of a re-baseline.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-08-19
- **Tasks:** 3/3 completed
- **Files modified:** 10 (7 in `firestarter_app`, 3 in meta; `firestarter` untouched — read-only per this plan's `commits_land_in`)

## Accomplishments

- `build_db.py`'s emit site now carries a disjoint two-arm rule: the pre-existing curated `_PAGE_SIZE_BY_PART` lookup (unchanged, checked first), and — new — emission of `raw_page_size` whenever the chip's OWN upstream `protocol_id` (captured as `_upstream_proto_id` **before** `classify()`'s tuple-unpack reassigns `proto_id` to the resolved algorithm and discards provenance) equals `0x0D`. The 66 rows `classify()` promotes into `0x0D` from a foreign protocol never trigger this arm. Hoisted the canonical-name expression (`name.split(",")[0].split("@")[0].strip()`) to `_canon`, used once.
- Regenerated `chip_database.json` via `python3 tools/build_db.py` (never hand-edited): exactly 18 added `page_size` keys, zero removed, byte-reproducible on a second run. Verified against the plan's exact named 18-row set — `AT28C010,AT28C010E`, `AT28C040,AT28C040E`, `AT28LV010`, `AT28MC020`, `AT28MC040` (ATMEL); `CAT28C010`, `CAT28C020`, `CAT28C040`, `CAT28C512` (CATALYST(CSI)); `28C010,28C010T,28C011,28C011T` (MAXWELL); `M28010` (SGS-THOMSON, ST); `WE512K8`, `WME128K8` (WED, at 128); `X28C010` (XICOR) — 15 at 128; plus `AT28MC010` (ATMEL), `WE128K8`, `WE256K8` (WED) — 3 at 64. `AT28C256` (gh#21, a promoted row) is untouched: no `page_size`, `infoic_page_size_raw` still 64.
- `tools/diff_db.py` confirms census invariance: `EXIT=0`, 744 explained, 0 unexplained/new/missing, buckets `PROV01_PROTECT_METADATA` (686) / `RULE_VCC_MARGIN_RAIL` (56) / `PGSZ_PAGE_SIZE` (2, unchanged). The 18 rows classify under `RULE_VCC_MARGIN_RAIL` — **never** `PROV01_PROTECT_METADATA` and **never** moving to `PGSZ_PAGE_SIZE` — falsifying `149-CONTEXT.md`'s own Integration Points prediction; recorded there as a correction, not a defect in this plan's work.
- `tests/test_page_size_invariants.py` (11 legs, no firmware-presence skip marker): the 84-row 0x0D bucket count, the 18 named native carriers split 15×128/3×64, 20 total carriers, an exhaustive power-of-two-in-`[1,512]` check, a **separate** provenance check (256 is a power of two and would still be wrong on a promoted row), AT28C256's non-change, `support_status` byte-identity across all 84 rows against the committed baseline, the `extra_chips.json` back door, and 2 synthetic non-vacuity legs proving both shared helpers can fail.
- `tests/golden/wire_dict_expected_deltas_149.json` generated programmatically from a live capture against the **untouched** `wire_dict_baseline.json` — 18 entries, 15×`{"page-size":128}` + 3×`{"page-size":64}`, matching the plan's named record-key set exactly. `test_live_capture_matches_golden` renamed to `test_live_capture_matches_golden_plus_the_149_deltas` with four assertions (anti-laundering pinning the golden's own 2 pre-existing page-size carriers; per-delta non-vacuity; exact count 18; golden-plus-deltas equals live). `test_wire_key_union_is_exactly_nine_keys` passes untouched.
- Full host suite: **1687 passed** (up from the pre-change baseline of 1641), `ruff check`/`ruff format --check` clean, `check_dispatch.py` PASS, `tools/build_db.py` byte-reproducible on a second run, `tools/ci_parity.sh` legs 1–3 green (leg 4, the mypy watermark, exits 2 locally on py3.12 due to a pre-existing ambient numpy PEP-695 stub incompatibility — **green locally on 3.12** is the honest statement per this plan's own note; not evaluated as "green in CI").
- `149-PAGE-SIZE.md`'s DB-side section is complete with all 7 required subsections (diff_db census + X-1 correction, D-17 RED/GREEN transcripts, the D-07 pytest transcript with its stated override-file non-coverage, the 18-row table by manufacturer, the three corrected stale comments, and the raw-vs-curated duplicate-key explanation). `149-check-claims.py` exits 0 over the edited artifact.
- Every emit-rule, census, and test result recorded here is a host-side database/software measurement; no AT28C part exists in operator inventory and none was involved in this plan. The DB-side half of the page-size seam this plan delivers is **software-proven and unvalidated on silicon**.

## Task Commits

Each task committed atomically, split across the two repos per `commits_land_in`:

1. **Task 1: Add the provenance-keyed emit arm to `build_db.py`, regenerate, assert the diff_db census** — `c254cbc` (feat, `firestarter_app`), `4da4281c` (docs, meta — D-17 RED + X-1 GREEN transcripts)
2. **Task 2: Author `test_page_size_invariants.py`, correct stale host comments** — `a020bff` (test, `firestarter_app`)
3. **Task 3: Commit the 18-delta fixture, rework the golden assertion, write the DB-side artifact section** — `6a433e3` (test, `firestarter_app`), `92707267` (docs, meta)

**Plan metadata:** committed after this SUMMARY (STATE.md / ROADMAP.md update, meta).

## Files Created/Modified

- `firestarter_app/tools/build_db.py` — the provenance-keyed emit arm, `_canon` hoist, `_upstream_proto_id` capture, two corrected stale comments
- `firestarter_app/firestarter/data/chip_database.json` — regenerated (never hand-edited); 18 rows gained `page_size`
- `firestarter_app/firestarter/database.py` — two comment-only corrections (zero executable change; D-02 verified intact)
- `firestarter_app/firestarter/constants.py` — `JSON_KEY_PAGE_SIZE`'s sync-note comment corrected (value byte-unchanged)
- `firestarter_app/tests/test_page_size_invariants.py` — new, 11-leg D-07 exhaustive proof
- `firestarter_app/tests/test_wire_dict_equivalence.py` — golden test renamed with four assertions; golden file itself untouched
- `firestarter_app/tests/golden/wire_dict_expected_deltas_149.json` — new, committed 18-entry delta fixture
- `firestarter_app/tests/golden/chip_database_field_inventory.json` — `programming.page_size` count re-derived 2→20 (see Deviations)
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-DB-TRANSCRIPTS.md` — new, D-17 RED + X-1 GREEN transcripts
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md` — DB-side evidence section completed

## Decisions Made

1. **`_upstream_proto_id` capture, not a reuse of `proto_id`.** The plan's read_first notes said "the emitter must read `proto_id` directly," but `classify()`'s call site (`_etype, proto_id, pinout_key = classify(...)`) reassigns the SAME local to the resolved algorithm before the emit site runs. A first-draft implementation that read `proto_id` at the emit site produced 84 carriers (every algorithm-13 row), not 18 — caught immediately by this task's own acceptance script before any commit. Fixed by capturing the chip's own upstream value under a new name (`_upstream_proto_id`) right before the `classify()` call, and reading that name at the emit site instead.
2. **`tests/golden/chip_database_field_inventory.json` re-derived, not left broken.** Not in this plan's `files_modified` list, but the full-suite run surfaced `test_programming_field_inventory_matches` going red (`page_size: 20 != 2`) — a direct, in-scope consequence of this plan's own regeneration. The golden's own `meta.how_to_update` field explicitly authorizes re-deriving a count via the same independent traversal the test uses, never a hand-edit; did exactly that, confirmed every other one of its ~25 counts (top-level, programming, electrical, protocol_chip_counts, generator_emitted_chip_entry_keys) unchanged, and appended a `meta.phase_149_update` note naming what changed and why.
3. **Described corrected stale comments without quoting their forbidden literal text.** `149-check-claims.py`'s narrowed bare-claim-word pattern fired on a `149-PAGE-SIZE.md` passage that quoted the OLD `build_db.py` comment verbatim (which made an unqualified correctness claim about a heuristic) as part of explaining what got corrected. Reworded to describe the defect (an unqualified correctness adjective) without repeating the literal phrase — the same discipline plan 02's docstring fix already established for this gate.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `proto_id` reassignment made the first emit-arm draft fire on all 84 rows, not 18**
- **Found during:** Task 1, before any commit
- **Issue:** `classify()`'s call site tuple-unpacks its return into `proto_id`, overwriting the chip's own upstream value with the post-classification resolved algorithm. An emit arm reading `proto_id` at the emit site (as the plan's read_first notes literally say to do) therefore compares the WRONG population — every algorithm-13 row's post-classification value is `13` (decimal), which happens to equal `0x0D`, so all 84 rows (not 18) gained `page_size`.
- **Fix:** Captured the chip's own upstream value as `_upstream_proto_id` immediately before the `classify()` call, and read that name at the emit site instead of `proto_id`.
- **Files modified:** `firestarter_app/tools/build_db.py`
- **Verification:** Re-ran the plan's exact Task 1 acceptance script; regenerated database now shows exactly 18 carriers matching the named set.
- **Committed in:** `c254cbc` (the bug was never committed in its broken state — caught pre-commit)

**2. [Rule 1 - Bug] `tests/golden/chip_database_field_inventory.json` broken by this plan's own regeneration**
- **Found during:** post-Task-3 full-suite run (`python3 -m pytest tests/ -o addopts="" -q`)
- **Issue:** `test_programming_field_inventory_matches` failed: the golden's frozen `programming.page_size` count (2, recorded by Phase 148 Plan 07) no longer matched the live database's 20.
- **Fix:** Re-derived the single changed count via the golden's own `_walk()`-equivalent independent traversal (never hand-typed), confirmed all other counts byte-identical, and appended a `meta.phase_149_update` note.
- **Files modified:** `firestarter_app/tests/golden/chip_database_field_inventory.json`
- **Verification:** `python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -q` — 8 passed; full suite re-run — 1687 passed, 0 failed.
- **Committed in:** `6a433e3`

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs directly caused by this plan's own edits, caught and fixed before or immediately after the responsible commit).
**Impact on plan:** No scope creep. Both fixes are corrections to this plan's own regeneration side-effects, not new features; neither touches a `PGSZ-0N` requirement checkbox or any file outside `firestarter_app`/meta.

## Issues Encountered

None beyond the two deviations above, both caught by this plan's own verification steps (the Task 1 acceptance script and the full-suite run) before this plan's own gate would have reported green falsely.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Plan 04 (firmware-side seam: `json_parser.c` key, `firestarter_handle_t` field, `eeprom28c_write_execute`'s mask-based flush) can proceed: the host now emits `programming.page_size` → wire `page-size` for exactly the 18 corroborated rows, with zero host runtime code change (D-02 verified — `database.py`'s two carry-sites are comment-only diffs). `149-PAGE-SIZE.md`'s DB-side section is complete for plan 04 to extend with the Firmware seam evidence section. One item carried forward: plan 08 must extend the D-19 claim gate's `_DEFAULT_TARGETS` to include this SUMMARY (and all `149-*-SUMMARY.md` files) before the phase closes, per plan 02's own stated non-extension boundary.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter_app/tools/build_db.py` (provenance arm present)
- FOUND: `/workspaces/firestarter_app/firestarter/data/chip_database.json` (18 carriers added)
- FOUND: `/workspaces/firestarter_app/tests/test_page_size_invariants.py` (11 tests, all passing)
- FOUND: `/workspaces/firestarter_app/tests/golden/wire_dict_expected_deltas_149.json` (18 deltas)
- FOUND: `/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-DB-TRANSCRIPTS.md`
- FOUND: `/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md` (DB-side section present)
- FOUND commit: `c254cbc` (firestarter_app)
- FOUND commit: `a020bff` (firestarter_app)
- FOUND commit: `6a433e3` (firestarter_app)
- FOUND commit: `4da4281c` (meta)
- FOUND commit: `92707267` (meta)
- CONFIRMED: `python3 -m pytest tests/ -o addopts="" -q` in `firestarter_app` — 1687 passed, 0 failed
- CONFIRMED: `python3 tools/diff_db.py; echo EXIT=$?` — EXIT=0, 744/0/0/0, buckets 686/56/2
- CONFIRMED: `python3 .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-check-claims.py; echo EXIT=$?` — EXIT=0
- CONFIRMED: `git -C /workspaces/firestarter status --porcelain` — empty (firmware submodule untouched)
- CONFIRMED: no `PGSZ-0N` checkbox or traceability row touched in `REQUIREMENTS.md` or `ROADMAP.md`
- CONFIRMED: meta `M firestarter` / `M firestarter_app` gitlinks not staged by this plan

---
*Phase: 149-firmware-page-size-seam-dual-repo-lockstep*
*Completed: 2026-08-19*
