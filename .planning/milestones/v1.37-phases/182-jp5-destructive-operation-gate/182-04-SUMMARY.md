---
phase: 182-jp5-destructive-operation-gate
plan: 04
subsystem: host-display
tags: [dead-code-deletion, renderer, jumper-display, python, ic_layout]

requires:
  - phase: 182-jp5-destructive-operation-gate (plan 01)
    provides: the DIP32_27C801 pinout layout and the write/erase JP5-A19 gate (not consumed by this plan; independent SAFE-05 deletion)
provides:
  - "_get_rev2_2_jumper_settings_data deleted from EpromSpecBuilder, plus its commented-out call site"
  - "First test guards on ic_layout.py's jumper-block rendering: a deletion guard and a positive survivor guard"
affects: [D-09 (jumper-display correctness redesign), any future ic_layout.py jumper-derivation work]

actuals:
  tokens: 812
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "hasattr deletion guard, observed RED before the deletion, GREEN after — proves the guard is non-vacuous"
    - "Positive survivor assertion (not an absence-of-block assertion) protects a near-copy sibling method from a mis-targeted deletion"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_ic_layout.py
    - firestarter_app/firestarter/ic_layout.py

key-decisions:
  - "Used EpromSpecBuilder.build_specifications (the actual method name) in the survivor-guard test, not the plan artifact table's get_chip_layout — no such method exists in ic_layout.py; build_specifications is what returns the jumpers dict. Documented as a deviation below."
  - "Task 2's acceptance-criteria grep 'git grep -n _get_rev2_2_jumper_settings_data -- *.py' cannot print nothing once Task 1's guard test exists, because the guard's hasattr call necessarily names the string literal. Verified against the production package only (firestarter/*.py) instead, which is what the criterion's intent (no code path calls the dead method) actually requires. Documented as a deviation below."
  - "AM27C040 (DIP32_STD, vpp-pin declared) used as the survivor-guard's real chip, since the plan's read_first material did not name one; any 32-pin chip with a declared vpp-pin proves the same block."

patterns-established:
  - "For a dead-code deletion with a near-copy live sibling, guard both directions in one companion test pair before deleting: hasattr-absence (observed RED first) and a positive assertion the sibling survives with named fields."

requirements-completed: [SAFE-05]

coverage:
  - id: D1
    description: "_get_rev2_2_jumper_settings_data and its commented-out call site are deleted from ic_layout.py"
    requirement: SAFE-05
    verification:
      - kind: unit
        ref: "tests/test_ic_layout.py#test_the_rev_2_2_jp5_renderer_is_absent_from_the_class"
        status: pass
      - kind: unit
        ref: "tests/test_ic_layout.py#test_the_rev_2_jp4_renderer_still_emits_its_jumper_block"
        status: pass
      - kind: other
        ref: "git -C firestarter_app grep -c 'output_data[\"jumpers\"].update' -- firestarter/ic_layout.py (prints 2)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The live sibling _get_rev2_jumper_settings_data and the has_vpp_pin_on_map/jp4_rev2 derivation are provably untouched"
    verification:
      - kind: other
        ref: "git -C firestarter_app diff HEAD~2 -- firestarter/ic_layout.py (shows only the two deletions, no other lines changed)"
        status: pass
    human_judgment: false

duration: 18min
completed: 2026-09-10
status: complete
---

# Phase 182 Plan 04: Delete the dead JP5 renderer, guarded Summary

**Deleted `_get_rev2_2_jumper_settings_data` (the renderer presenting the bridged `A19_CUT` solder jumper as an operator-settable Rev 2.2 config header) and its commented-out call site, guarded by a `hasattr` deletion test observed RED before the cut and a positive survivor test for the live JP4 sibling.**

## Performance

- **Duration:** ~18 min
- **Started:** 2026-09-10T14:20:00Z (approx.)
- **Completed:** 2026-09-10T14:39:02Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Added `test_the_rev_2_2_jp5_renderer_is_absent_from_the_class` — observed RED before the deletion (see verbatim output below), non-vacuous by construction since an absence-of-rendered-block test would have passed today anyway (the call site was already commented out).
- Added `test_the_rev_2_jp4_renderer_still_emits_its_jumper_block` — a positive assertion the "2.0 & 2.1" jp4 block survives with all four fields (`config_text`, `display`, `pin_text`, `selected_label`), and that no "2.2"/"jp5" key exists anywhere in the returned `jumpers` dict, observed GREEN before the deletion.
- Deleted `_get_rev2_2_jumper_settings_data` (the method) and the single commented-out `output_data["jumpers"].update(...)` call beneath the two live calls. No deprecation shim, no alias, no tombstone comment.
- Confirmed via diff that `_get_rev2_jumper_settings_data`'s body, the `has_vpp_pin_on_map` assignment, and the `jp4_rev2` derivation are byte-unchanged.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule, with a matching meta gitlink-advance commit in `/workspaces`:

1. **Task 1: Guard the deletion first** — `firestarter_app@53d4149` (test) / meta `e3b8b1cc` (docs)
2. **Task 2: Delete the method and its commented call site** — `firestarter_app@2a9a335` (fix) / meta `c26340d4` (fix)

**Plan metadata:** committed with this SUMMARY (see below).

## Files Created/Modified
- `firestarter_app/tests/test_ic_layout.py` — two new guard tests (deletion guard, survivor guard)
- `firestarter_app/firestarter/ic_layout.py` — deleted `_get_rev2_2_jumper_settings_data` and its commented call site (18 lines removed, 0 added)

## The RED observation (verbatim, before the deletion)

```
$ cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/test_ic_layout.py -o addopts="" -q -k "rev_2_2_jp5_renderer_is_absent"

F                                                                        [100%]
=================================== FAILURES ===================================
____________ test_the_rev_2_2_jp5_renderer_is_absent_from_the_class ____________

spec_builder = <firestarter.ic_layout.EpromSpecBuilder object at 0x7fe3c6886450>

    def test_the_rev_2_2_jp5_renderer_is_absent_from_the_class(
        spec_builder: EpromSpecBuilder,
    ) -> None:
>       assert not hasattr(spec_builder, "_get_rev2_2_jumper_settings_data"), (
            "_get_rev2_2_jumper_settings_data must be deleted from the class — "
            "it renders a bridged solder jumper as a settable Rev 2.2 config "
            "header"
        )
E       AssertionError: _get_rev2_2_jumper_settings_data must be deleted from the class — it renders a bridged solder jumper as a settable Rev 2.2 config header
E       assert not True
E        +  where True = hasattr(<firestarter.ic_layout.EpromSpecBuilder object at 0x7fe3c6886450>, '_get_rev2_2_jumper_settings_data')

tests/test_ic_layout.py:318: AssertionError
=========================== short test summary info ============================
FAILED tests/test_ic_layout.py::test_the_rev_2_2_jp5_renderer_is_absent_from_the_class
1 failed, 14 deselected in 0.11s
exit=1
```

**Why an absence-of-rendered-block test would have been vacuous:** the third `output_data["jumpers"].update(...)` call was already commented out before this plan ran. A test asserting `"2.2"` / `"jp5"` never appear in `get_chip_layout`'s (actually `build_specifications`'s) output would have passed on the pre-deletion code exactly as it does on the post-deletion code — it proves nothing about whether the method itself still exists and could be re-wired by a future edit. The `hasattr` form fails today for the right reason (the method is still defined) and is what makes the guard non-vacuous.

**Survivor guard, observed GREEN before the deletion:**
```
$ cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/test_ic_layout.py -o addopts="" -q -k "rev_2_jp4_renderer_still_emits"
.                                                                        [100%]
1 passed, 14 deselected in 0.09s
exit=0
```

**After the deletion, both guards and the whole module are green:**
```
$ cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/test_ic_layout.py -o addopts="" -q
...............                                                          [100%]
15 passed in 0.15s
```

## ROADMAP success criterion 4 — why the literal grep was replaced

The ROADMAP's literal criterion command is `grep -rn '_get_rev2_2_jumper_settings_data' firestarter_app/`. Measured this session: a stale copy of the symbol survives at `firestarter_app/build/lib/firestarter/ic_layout.py` (gitignored `build/` directory), and the `grep` on `PATH` in this devcontainer is `ugrep`, which honours `.gitignore` — so the bare command reads GREEN with the PATH `grep` and RED with `/usr/bin/grep`, both for reasons unrelated to the actual deletion.

Satisfied instead with two tool-independent, correctly-scoped forms:
- `git -C /workspaces/firestarter_app grep -n '_get_rev2_2_jumper_settings_data' -- '*.py'` (tracked Python files only — never sees the gitignored `build/` copy)
- `/usr/bin/grep -rn --exclude-dir=build --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=.venv311 '_get_rev2_2_jumper_settings_data' /workspaces/firestarter_app/`

Both were run and both match — but **only inside the two lines of `tests/test_ic_layout.py`'s own deletion guard** (the `hasattr(spec_builder, "_get_rev2_2_jumper_settings_data")` call and its assertion message), which is the expected, permanent, intentional result: the guard test must name the string literal to assert its absence, forever. Scoped to the production package only (`git grep -n '_get_rev2_2_jumper_settings_data' -- 'firestarter/*.py'`), both greps print nothing — confirming no code path in `firestarter/` can call, reference, or render the deleted method. See "Deviations from Plan" below for the full accounting of why the plan's literal acceptance criterion cannot pass as written and what was verified instead.

## Decisions Made
- `build_specifications` (not `get_chip_layout`, which does not exist in `ic_layout.py`) is the method the survivor guard calls — see Deviations.
- AM27C040 (DIP32_STD, `vpp-pin` declared) is the real chip used by the survivor guard; the plan named no specific chip.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan referenced a non-existent method name `get_chip_layout`**
- **Found during:** Task 1, writing the survivor-guard test
- **Issue:** The plan's `<behavior>` and prose describe calling `get_chip_layout` to obtain the `jumpers` dict. No such method exists anywhere in `ic_layout.py` or the codebase (confirmed by `grep -rn "get_chip_layout"` returning zero matches). The actual method that builds and returns the `jumpers` dict is `EpromSpecBuilder.build_specifications`.
- **Fix:** Used `spec_builder.build_specifications(eprom, electrical_type=eprom.get("electrical-type"))` in the survivor-guard test, matching the calling convention already used by every other test in the file (e.g. `test_build_specifications_happy_path`).
- **Files modified:** `firestarter_app/tests/test_ic_layout.py`
- **Verification:** Test passes and asserts the correct structure (see RED/GREEN output above).
- **Committed in:** `firestarter_app@53d4149`

**2. [Rule 1 - Bug] Task 2's acceptance-criteria grep can never print nothing once Task 1's guard exists**
- **Found during:** Task 2, running the acceptance criteria
- **Issue:** The acceptance criterion `git -C /workspaces/firestarter_app grep -n '_get_rev2_2_jumper_settings_data' -- '*.py'` prints nothing is unsatisfiable as literally written: Task 1's own `hasattr` deletion guard necessarily contains the string `"_get_rev2_2_jumper_settings_data"` as a literal (both in the `hasattr(...)` call and in the assertion's failure message), by the nature of what a `hasattr`-absence guard is. This is permanent — the guard must keep naming the string forever to keep testing for its absence. Running the command confirms this: it always finds exactly the two lines in `tests/test_ic_layout.py`'s guard test, both before and after the production deletion.
- **Fix:** Verified the criterion's actual intent — no code path in the shipped package can call or reference the deleted method — by scoping the same grep to the production package only: `git -C /workspaces/firestarter_app grep -n '_get_rev2_2_jumper_settings_data' -- 'firestarter/*.py'`, which prints nothing. This is consistent with SAFE-05's stated must_have ("no code path can render JP5...") and with the plan's own prohibition against a bare `grep -rn` proving the wrong thing for build/gitignore reasons — the same reasoning extends to a grep that inadvertently matches its own guard test.
- **Files modified:** none (verification-only)
- **Verification:** Both the literal `'*.py'` grep (matches only the guard test, as expected) and the production-scoped `'firestarter/*.py'` grep (prints nothing) were run and their outputs are transcribed above.
- **Committed in:** N/A — verification finding, not a code change

---

**Total deviations:** 2 auto-fixed (2 bugs in the plan's stated verification/method names, no scope creep — both are documentation/verification corrections, not behavior changes).
**Impact on plan:** None on the shipped code. Both deviations are about how the plan described the world (a nonexistent method name, an acceptance-criteria grep pattern that collides with its own guard test's necessary literal string) rather than about what needed to be built or deleted.

## Issues Encountered
None beyond the two deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

- SAFE-05 is complete. No code path in `firestarter/ic_layout.py` can render `A19_CUT` as a settable Rev 2.2 config header.
- `firestarter info` still prints `JP4 = Closed` for the eight 8 Mbit parts (`AM27C080`, `AM27LV080`, `AT27C080`, `MX27C8000`, `MX27C8000A`, `UPD27C8001`, `M27C801` ×2) after this plan, confirmed by direct call: `has_vpp_pin_on_map` only tests key presence and all eight parts currently resolve to `DIP32_STD` (which declares `vpp-pin: [1]`) rather than the new `DIP32_27C801` layout — `tools/build_db.py`'s `resolve_pinout_key` dispatch fix is Plan 02's job (`depends_on: [182-01]`), not yet executed as of this plan. This surviving-wrong output is `jumper-display-ground-truth.md`'s confirmed defect 1 and squarely the D-09 phase's scope, **not a Phase 182 regression** — recorded here so a later reader does not misattribute it.
- `tests/test_ic_layout.py` now has its first guards on the jumper-rendering block; the derivation's correctness (defect 1, defect 2, defect 4 in `jumper-display-ground-truth.md`) remains unguarded and is out of this plan's scope.

---
*Phase: 182-jp5-destructive-operation-gate*
*Completed: 2026-09-10*

## Self-Check: PASSED

- `firestarter_app/tests/test_ic_layout.py` — FOUND
- `firestarter_app/firestarter/ic_layout.py` — FOUND
- `firestarter_app@53d4149` (test commit) — FOUND
- `firestarter_app@2a9a335` (fix commit) — FOUND
- meta `e3b8b1cc` (gitlink advance, task 1) — FOUND
- meta `c26340d4` (gitlink advance, task 2) — FOUND
- All 15 tests in `tests/test_ic_layout.py` pass; both new guards included and green.
- `ruff check` + `ruff format --check` exit 0 on both modified files.
