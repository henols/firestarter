---
phase: 149-firmware-page-size-seam-dual-repo-lockstep
plan: 05
subsystem: testing
tags: [cross-repo-parity, json-parser, pytest, host-firmware-lockstep, fw-presence, page-size]

# Dependency graph
requires:
  - phase: 149-04
    provides: "the firmware page-size wire key (key_page_size / \"page-size\") parsed into firestarter_handle_t and dispatched from key_parsers[], which this plan's parity gate asserts against"
provides:
  - "tests/test_json_key_parity.py: a 10-leg cross-repo parity gate asserting JSON_KEY_PAGE_SIZE is declared AND dispatched in firestarter/src/json_parser.c, all 3 JSON_KEY_* constants map two-way to the firmware's 11 PROGMEM keys via a completeness-checked 8-key named exemption tuple, and the gate fails closed (not open) on a firmware rename"
  - "two committed planted-violation fixtures (key-string drift, undispatched key), each observed RED with a distinguishable message and leg isolation, staying live in app CI with no requires_fw decorator"
  - "src/json_parser.c added to tests/scan_paths.py's committed cross-repo inventory; two stale prose counts corrected 6 -> 8"
  - "the empty-FIRESTARTER_FW_ROOT skip-leg transcript proving the gate's 8 live legs SKIP cleanly while both planted legs stay live -- the exact state app CI runs in"
  - "constants.py:144's previously-false \"Firmware sync\" note is now enforced"
affects: [149-06, 149-07, 149-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Zero-argument, fresh-read check helpers (_extract_key_map, _extract_dispatch_identifiers, _check_page_size_key_present_and_dispatched) that re-read the module-scope path constant on every call, so the SAME helper serves both the live leg and both planted-violation legs via monkeypatch.setattr on that one constant -- never a parallel reimplementation"
    - "Errors-list-then-assert-empty two-way parity with a completeness-checked named exemption tuple (3 Python-mapped + 8 named-exempt = 11 extracted firmware keys), following test_revision_constants_parity.py's established shape"
    - "requires_fw as the only skip marker, module-scope fw_path resolution making a firmware rename a hard MissingScanTargetError rather than a silent skip"

key-files:
  created:
    - firestarter_app/tests/test_json_key_parity.py
    - firestarter_app/tests/fixtures/planted_json_parser_key_string_drift.c
    - firestarter_app/tests/fixtures/planted_json_parser_undispatched_key.c
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PARITY-TRANSCRIPTS.md
  modified:
    - firestarter_app/tests/scan_paths.py
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md

key-decisions:
  - "Decorated all 8 live legs (including the fails-closed-on-rename leg and the self-protection leg) with @requires_fw, per the plan's explicit instruction -- a deliberate departure from the closest analog (test_cap03_ack_layout_parity.py), where those two leg types carry no requires_fw. Verified this satisfies every acceptance criterion including the empty-FW_ROOT skip-leg transcript (8 skipped, 2 live)."
  - "Isolated the two planted legs' distinguishing phrases structurally (each raise branch in the shared helper produces a phrase only reachable from that branch), rather than adding separate marker strings -- natural leg isolation with no extra bookkeeping."
  - "Moved the undispatched-key fixture's explanatory comment about the omitted row to OUTSIDE the key_parsers[] initializer braces, because the dispatch-identifier extractor scans the raw initializer body and a comment inside it that named the identifier would self-satisfy the very check the fixture exists to fail (caught by the fixture's own first pytest run, before commit)."

patterns-established:
  - "Cross-repo JSON-key parity as a two-way, completeness-checked exemption-tuple gate is now the third instance of this shape in this repo (CMD_*/FLAG_* in test_revision_constants_parity.py, CAP-03 byte layout in test_cap03_ack_layout_parity.py, JSON keys here) -- a future JSON-wire-key addition has a template to follow."

requirements-completed: []  # PGSZ-03 spans plan 05 alone at the test-authoring level, but per this phase's planner_decisions, plan 08 alone flips PGSZ-0N checkboxes after the whole-phase gate is green

coverage:
  - id: D1
    description: "JSON_KEY_PAGE_SIZE is asserted string-equal to the firmware's key_page_size PROGMEM string AND that identifier is asserted present inside key_parsers[] -- declared and dispatched, not merely present"
    requirement: "PGSZ-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_json_key_parity.py#test_page_size_key_string_matches_constants_py"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_json_key_parity.py#test_planted_key_string_drift_is_detected"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_json_key_parity.py#test_planted_undispatched_key_is_detected"
        status: pass
    human_judgment: false
  - id: D2
    description: "All 3 JSON_KEY_* constants map to firmware totally; all 11 extracted firmware keys map back or are named in a complete, non-stale 8-key exemption tuple (3 + 8 = 11)"
    requirement: "PGSZ-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_json_key_parity.py#test_every_json_key_constant_maps_to_a_firmware_key"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_json_key_parity.py#test_every_firmware_key_maps_back_or_is_named_exempt"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_json_key_parity.py#test_the_exemption_tuple_is_complete_and_has_no_stale_entries"
        status: pass
    human_judgment: false
  - id: D3
    description: "The gate fails closed (MissingScanTargetError) on a present-but-renamed firmware path rather than silently skipping, and SKIPS cleanly (not error) with no firmware checkout while the two planted legs stay live -- the state app CI actually runs in"
    requirement: "PGSZ-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_json_key_parity.py#test_gate_fails_closed_on_an_unreadable_firmware_path"
        status: pass
      - kind: other
        ref: "TMPROOT=$(mktemp -d) FIRESTARTER_FW_ROOT=$TMPROOT python3 -m pytest tests/test_json_key_parity.py -rs -o addopts=\"\" -q -- 8 skipped, 2 passed, exit 0 (149-PARITY-TRANSCRIPTS.md)"
        status: pass
    human_judgment: false
  - id: D4
    description: "src/json_parser.c is in the committed cross-repo scan-path inventory, both stale prose counts are corrected 6 -> 8, and the name-collision guard passes for the new entry"
    requirement: "PGSZ-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_scan_paths_resolve.py#test_all_cross_repo_paths_resolve"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_scan_paths_resolve.py#test_no_entry_is_a_same_repo_lookalike"
        status: pass
    human_judgment: false

# Metrics
duration: ~70min
completed: 2026-08-19
status: complete
---

# Phase 149 Plan 05: Cross-Repo JSON-Key Parity Gate (PGSZ-03, D-18) Summary

**Added a 10-leg pytest module proving `constants.py`'s `JSON_KEY_PAGE_SIZE` is both declared and dispatched in `firestarter/src/json_parser.c`, with all 3 host JSON keys mapping two-way to the firmware's 11 PROGMEM keys via a completeness-checked 8-key exemption tuple, and two planted fixtures observed RED before being committed in their intentionally-violating state.**

## Performance

- **Duration:** ~70 min
- **Completed:** 2026-08-19
- **Tasks:** 3/3 completed
- **Files modified:** 6 (3 in `firestarter_app`, 2 in meta, plus the new meta transcripts file)

## Accomplishments

- **`tests/test_json_key_parity.py`** (10 legs, all passing, 0 skipped in this devcontainer): resolves
  `firestarter/src/json_parser.c` via `fw_path` at module scope (a rename is a hard
  `MissingScanTargetError`, never a silent skip); extracts the 11 PROGMEM key strings tolerant of
  `key_read_strobe[]`'s aligned extra whitespace; and asserts the page-size key is both **declared**
  (string-equal to `JSON_KEY_PAGE_SIZE`) and **dispatched** (its identifier appears inside
  `key_parsers[]`) in one check, closing the specific hole a naive presence check misses.
- **Two-way JSON-key parity, completeness-checked.** All 3 `JSON_KEY_*` constants on
  `firestarter.constants` (discovered by introspection, not a hardcoded list) map totally to
  firmware keys; the reverse direction uses a named, commented `_EXEMPT_FIRMWARE_KEYS` frozenset (the
  8 keys with no Python counterpart) whose own completeness is asserted — `3 + 8 = 11`, no third,
  unclassified bucket.
- **Two planted fixtures, both observed RED before being committed in their violating state.**
  `planted_json_parser_key_string_drift.c` spells the page-size PROGMEM string with an underscore
  (Pitfall 10's exact database-key/wire-key confusion); `planted_json_parser_undispatched_key.c`
  spells it correctly but omits its `key_parsers[]` row. Both fixture-reading legs carry **no**
  `@requires_fw` decorator, so they stay live in `firestarter_app`'s own CI (no sibling checkout
  there). Each asserts the shared helper raises with a distinguishable message and leg isolation
  (the other plant's phrase is asserted absent), and each carries the full V12 ceremony: a
  before/after `git hash-object` comparison and an empty-porcelain assertion on the real firmware
  repo, proving neither plant ever touched it.
- **The empty-`FIRESTARTER_FW_ROOT` skip-leg transcript.** Because `fw_presence.py` binds its
  environment lookup at import, the skip condition was proved in a subprocess pointed at a fresh
  `mktemp -d`: the 8 `@requires_fw` legs report **SKIPPED** with the absent-firmware reason text (not
  ERROR, not FAILED), both planted legs stay live and pass, and the run exits 0 — both for the module
  alone and for the whole `tests/` suite (1639 passed, 58 skipped). This is exactly the state
  `firestarter_app`'s standalone CI runs in, stated as such in both the transcript and the artifact.
- **`src/json_parser.c` added to `tests/scan_paths.py`'s committed cross-repo inventory** —
  scanned by plan 04 and this plan without ever being named there, exactly the off-inventory scan the
  module exists to prevent. Corrected two stale prose counts (both read "6"; the tuple has held 7
  entries since Phase 147 added `src/firestarter.cpp`, now 8 with this entry).
- **`constants.py:144`'s "Firmware sync" note is now enforced.** It read `json_parser.c
  (key_page_size)` since plan 03's wording fix — a claim measured false at kickoff, since no such
  key existed until plan 04. This plan's gate is what makes that claim a machine-checked fact rather
  than an unverified comment.
- **`149-PAGE-SIZE.md`'s "Cross-repo parity evidence (plan 05)" section is complete** with all
  required subsections; `149-check-claims.py` exits 0 over the edited artifact.
- Full `tests/` suite: **1697 passed**, 0 failures. `bash tools/ci_parity.sh`: legs 1-3 (empty-sibling
  pytest, sibling-present pytest, ruff) all exit 0; leg 4 (mypy watermark) exits 2, the devcontainer's
  documented pre-existing local condition (ambient numpy PEP-695 stub on Python 3.12), unrelated to
  and unaffected by this plan's changes.
- The parity gate proves **layout agreement** between the two repositories' key strings and dispatch tables — nothing about hardware. No AT28C part was involved anywhere in this plan, `0x0D` stays `UNVERIFIED`, and no `support_status` entry changed. Like every other artifact this phase produces, this cross-repo parity evidence is **software-proven and unvalidated on silicon**.

## Task Commits

Each task committed atomically, split across the two repos per `commits_land_in`:

1. **Task 1: Author `test_json_key_parity.py`** — `efea9aa` (test, `firestarter_app`)
2. **Task 2: Commit the two planted fixtures** — `075905a` (test, `firestarter_app`), `2a0567a1`
   (docs, meta — plant transcripts)
3. **Task 3: Inventory entry, stale-count fix, skip-leg transcript** — `693b466` (test,
   `firestarter_app`), `f76d648e` (docs, meta — skip-leg transcript and `149-PAGE-SIZE.md` section)

**Plan metadata:** committed after this SUMMARY (STATE.md / ROADMAP.md update, meta).

## Files Created/Modified

- `firestarter_app/tests/test_json_key_parity.py` — the 10-leg parity gate
- `firestarter_app/tests/fixtures/planted_json_parser_key_string_drift.c` — RED fixture, underscore
  key spelling
- `firestarter_app/tests/fixtures/planted_json_parser_undispatched_key.c` — RED fixture, missing
  dispatch row
- `firestarter_app/tests/scan_paths.py` — new inventory entry, two stale counts corrected
- `firestarter_app/firestarter/constants.py` — corrected the now-false page-size "Firmware sync"
  note (post-completion fix, see Deviations #3)
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PARITY-TRANSCRIPTS.md` — new;
  both planted-RED transcripts, the empty-`FW_ROOT` skip-leg transcript, the `ci_parity.sh` summary
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md` — the
  "Cross-repo parity evidence (plan 05)" section

## Decisions Made

1. **Decorated all 8 live legs with `@requires_fw`**, including the fails-closed-on-rename leg and
   the self-protection leg — a deliberate departure from the closest analog module, per this plan's
   explicit acceptance criteria. Verified against the empty-`FW_ROOT` transcript: exactly 8 skipped,
   2 live, matching the plan's stated shape.
2. **Structural leg isolation** — each planted leg's distinguishing phrase is only reachable from its
   own raise branch inside the shared helper, so no extra marker bookkeeping was needed to prove the
   other plant's phrase is absent.
3. **Moved the undispatched-key fixture's explanatory comment outside the `key_parsers[]`
   initializer braces** after the fixture's first run showed the leg did not raise — the dispatch
   extractor scans the raw initializer body, and a comment inside it naming the omitted identifier
   would have self-satisfied the check the fixture exists to fail.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Undispatched-key fixture's own header/inline comment defeated its own leg**
- **Found during:** Task 2, first pytest run of the two new planted-fixture tests
- **Issue:** `planted_json_parser_undispatched_key.c`'s in-table comment named the omitted
  identifier (`key_page_size`) literally, inside the `key_parsers[]` initializer's brace region. The
  gate's dispatch-identifier extractor scans that region's raw text with a `\bkey_\w+\b` regex, so
  the comment text itself satisfied the "identifier appears in the dispatch body" check, making
  `test_planted_undispatched_key_is_detected` fail with "DID NOT RAISE" instead of proving the
  expected defect.
- **Fix:** Moved the explanatory comment to immediately above the `key_parsers[]` declaration
  (outside the `{...}` body the extractor scans) and reworded it to avoid naming the identifier a
  second time inside the region under test.
- **Files modified:** `firestarter_app/tests/fixtures/planted_json_parser_undispatched_key.c`
- **Verification:** Re-ran `python3 -m pytest tests/test_json_key_parity.py -o addopts="" -q` — all
  10 legs pass.
- **Committed in:** `075905a` (Task 2 commit — never committed in its broken state)

**2. [Rule 3 - Blocking] The plan's own Task 3 acceptance snippet uses attribute names
`ScanPathEntry` does not have**
- **Found during:** Task 3, reading `tests/scan_paths.py` before adding the new entry
- **Issue:** The plan's Task 3 `<verify>` block checks `e.path` and `'test_json_key_parity.py' in
  e.consumers`, but the real `ScanPathEntry` dataclass (already committed, Phase 123 Plan 08) has
  fields `fw_relative_path` and `resolved_by`, not `path`/`consumers`. Running the plan's literal
  snippet against the real dataclass would raise `AttributeError`.
- **Fix:** Added the new entry using the real field names
  (`ScanPathEntry("src/json_parser.c", ("test_json_key_parity.py",))`, positional, matching every
  existing entry in the tuple) and verified the entry's presence with the correct attribute names
  instead of the plan's literal snippet.
- **Files modified:** none beyond the intended `tests/scan_paths.py` edit — this is a
  verification-script correction, not a source change.
- **Verification:** `python3 -m pytest tests/test_scan_paths_resolve.py -o addopts="" -q` — 4/4
  pass, including the name-collision guard for the new entry.
- **Committed in:** `693b466` (Task 3 commit)

**3. [Rule 1 - Bug] Truth #7 was initially missed: `constants.py:144`'s "Firmware sync" note was
never corrected**
- **Found during:** Post-completion coordinator review, after this plan's first pass was reported
  done.
- **Issue:** This plan built the enforcing test (`test_json_key_parity.py`) but never touched
  `firestarter_app/firestarter/constants.py` itself. Its page-size sync note (lines 151-154 at the
  time) still read "this key does not yet exist in firestarter/src/json_parser.c ... Phase 149 plan
  04 adds it" — a claim that was true when plan 03 wrote it but became false the moment plan 04
  landed the key (`firestarter` commit `58c6a3c`). A reader of `constants.py` after plan 04 was told
  the firmware side was still missing when it was present — exactly the class of false in-code sync
  note must_have truth #7 exists to eliminate. The gate's own passing tests did not catch this
  because the gate asserts the wire-key VALUE matches, not the prose of a comment two lines above it.
- **Fix:** Rewrote the note to state the current truth — the key exists in
  `firestarter/src/json_parser.c` (landed by plan 04, commit `58c6a3c`), and
  `tests/test_json_key_parity.py` is the enforcing gate. Also independently re-verified the adjacent
  `JSON_KEY_READ_SETTLING_DELAY`/`JSON_KEY_READ_STROBE_US` "Firmware sync" note (line ~139): both
  `key_read_settling` and `key_read_strobe` are confirmed present and dispatched in the live
  firmware source, so that note was already true and needed no change.
- **Files modified:** `firestarter_app/firestarter/constants.py`
- **Verification:** Re-ran `python3 -m pytest tests/test_json_key_parity.py -o addopts="" -q -rs`
  (10 passed) and `ruff check` / `ruff format --check` on the changed file (both clean) after the
  correction.
- **Committed in:** `0744348` (`firestarter_app`, separate commit — this plan's task commits had
  already landed by the time the gap was found)

---

**Total deviations:** 3 auto-fixed (1 Rule 1 self-introduced fixture defect caught by its own
gate before commit, 1 Rule 3 plan-verification-script field-name correction with no source-code
impact, 1 Rule 1 post-completion fix closing a must_have truth this plan's first pass missed).
**Impact on plan:** No scope creep. None of the three fixes touches a test assertion's intent, a
`PGSZ-0N` requirement checkbox, or any file outside this plan's own scope.

## Issues Encountered

The whole-`tests/` pytest run (1639-item and 1697-item invocations) each took roughly 3.5 minutes
in this devcontainer — well within the plan's stated 600s budget, but long enough that the default
2-minute Bash timeout needed raising for those specific invocations. No test failures, no flaky
results across repeated runs.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Plan 06 (post-change cold measurement and MERGE-05 funding) can proceed independently — this plan
touches no firmware source and no build artifact. Plan 08's whole-phase gate now has a machine-
checked cross-repo parity fact to cite for PGSZ-03 rather than an unverified comment. No `PGSZ-0N`
requirement checkbox or traceability row was touched — plan 08 alone flips them.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter_app/tests/test_json_key_parity.py`
- FOUND: `/workspaces/firestarter_app/tests/fixtures/planted_json_parser_key_string_drift.c`
- FOUND: `/workspaces/firestarter_app/tests/fixtures/planted_json_parser_undispatched_key.c`
- FOUND: `/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PARITY-TRANSCRIPTS.md`
- FOUND: `ScanPathEntry("src/json_parser.c", ...)` in `/workspaces/firestarter_app/tests/scan_paths.py`
- FOUND: "Cross-repo parity evidence (plan 05)" section, fully populated, in `149-PAGE-SIZE.md`
- FOUND commit: `efea9aa` (firestarter_app)
- FOUND commit: `075905a` (firestarter_app)
- FOUND commit: `693b466` (firestarter_app)
- FOUND commit: `0744348` (firestarter_app — post-completion truth-#7 correction)
- FOUND commit: `2a0567a1` (meta)
- FOUND commit: `f76d648e` (meta)
- CONFIRMED: `constants.py:150-153`'s page-size "Firmware sync" note now states the key exists in
  `firestarter/src/json_parser.c` (plan 04, commit `58c6a3c`) rather than the stale "does not yet
  exist" claim — must_have truth #7 satisfied
- CONFIRMED: `python3 -m pytest tests/test_json_key_parity.py -o addopts="" -q -rs` — 10 passed, 0 skipped
- CONFIRMED: empty-`FIRESTARTER_FW_ROOT` subprocess run — 8 skipped (requires_fw, absent-firmware
  reason), 2 passed (planted legs), exit 0
- CONFIRMED: `python3 -m pytest tests/ -o addopts="" -q` (firestarter_app) — 1697 passed
- CONFIRMED: `python3 -m ruff check firestarter/ tests/` and `ruff format --check` — both exit 0
- CONFIRMED: `python3 /workspaces/.planning/phases/149-*/149-check-claims.py` — EXIT=0
- CONFIRMED: `git -C /workspaces/firestarter status --porcelain` — empty
- CONFIRMED: `git -C /workspaces/firestarter_app diff --quiet firestarter/data/chip_database.json` — unchanged
- CONFIRMED: no `PGSZ-0N` checkbox or traceability row touched in `REQUIREMENTS.md` or `ROADMAP.md`
- CONFIRMED: meta `M firestarter` / `M firestarter_app` gitlinks not staged by this plan

---
*Phase: 149-firmware-page-size-seam-dual-repo-lockstep*
*Completed: 2026-08-19*

## Self-Check: PASSED

All files and commits listed in the Self-Check section above were independently re-verified on
disk/in git history after this SUMMARY was written: all 5 files FOUND, all 5 commit hashes FOUND
in their respective repos' history.
