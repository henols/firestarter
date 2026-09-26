---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 04
subsystem: testing
tags: [pytest, cross-repo-scan, fw-presence, test-fixtures, h1-hazard]

requires:
  - phase: 168-01
    provides: "sub-repo v1.35 branches and MIGRATION-TABLE.md filled with the HONEST-01 pre-deletion SHAs"
provides:
  - "firestarter_app/tests/test_dispatch_mirror.py deleted -- the sole module-scope fw_path('doc', 'PROTOCOLS.md') call that aborted the whole app suite at collection when firestarter/doc/ was missing (H-1)"
  - "the firmware-doc ScanPathEntry removed from tests/scan_paths.py; inventory 8 -> 7, still above the _FLOOR=6 non-vacuity guard"
  - "the fake_firestarter fixture rekeyed off include/firestarter.h -- its doc/PROTOCOLS.md stub deleted so the fixture no longer models a firmware layout the real repo will stop having"
  - "measured proof (evidence/h1-severance-proof.txt) that removing firestarter/doc/ from a present, clean firmware sibling no longer aborts collection: 1972 collected, 1972 executed, 0 failures"
affects: ["168-07 (owns the real firestarter/doc/ deletion this plan unblocks)", "168-09 (owns firestarter_app/doc/ deletion and the 17 doc-leg removals this plan's Task 3 finding traces to)", "168-10 (rebuilds the dispatch-mirror gate in the meta repo against the published wiki, using the regexes and handler-file map preserved below)"]

tech-stack:
  added: []
  patterns: ["reversible cross-repo experiment via an isolated scratch git clone with a real commit, never an in-place rename of a tracked sibling checkout, so 'plant must not touch the real file' porcelain-cleanliness controls in unrelated modules are not spuriously tripped"]

key-files:
  created: []
  modified:
    - firestarter_app/tests/scan_paths.py
    - firestarter_app/tests/test_fw_presence.py
    - firestarter_app/tests/fixtures/fake_firestarter/README.md
    - firestarter_app/tools/check_no_exists_proxy.py
  # deleted (not a Write/Edit modification, listed for completeness):
  #   firestarter_app/tests/test_dispatch_mirror.py
  #   firestarter_app/tests/fixtures/fake_firestarter/doc/PROTOCOLS.md

key-decisions:
  - "The surviving ScanPathEntry for test/native/avr/test_dispatch/test_configure_memory.cpp keeps its path (168-10's replacement checker still reads that file) but its resolved_by tuple now names the relocated meta-repo consumer instead of the deleted module, per the plan's explicit instruction not to remove that entry"
  - "Task 3's reversible experiment used an isolated scratch git clone with a real, committed doc/ removal, not the plan's literal 'mv' on the tracked /workspaces/firestarter checkout -- an in-place rename dirties that repo's whole-tree git-porcelain reading, which spuriously failed 9 unrelated tests across 5 other modules that assert repo-wide cleanliness (not per-file state) as a 'the plant did not touch the real file' control. Measured both ways; documented in evidence/h1-severance-proof.txt."
  - "The plan's 'expect 17 failures across five modules' prediction does not apply to this task's actual, narrower scope (firestarter/doc/ only, firmware sibling present) -- those 17 failures are 168-RESEARCH.md's measured baseline for a different configuration (firestarter_app/doc/ removed, no firmware sibling at all), which is 168-09's territory, not 168-04's. Confirmed against ROADMAP.md: 168-09 explicitly owns 'Remove the 17 doc test legs from 5 modules ... delete firestarter_app/doc/'. Recorded as a finding, not silently reconciled."
  - "requirements-completed left empty. Both MIGRATE-03 and MIGRATE-04 are declared in this plan's own frontmatter but remain genuinely incomplete after this plan (doc/ has not been deleted yet, and the bulk of MIGRATE-04's 30-file repair surface is untouched) -- per project precedent (multi-plan requirements must not be marked complete by an intermediate plan), the checkboxes are left for whichever plan actually closes out the full requirement."

patterns-established:
  - "Cross-repo hazard-severance proofs run against an isolated scratch clone of the sibling repo (real commit inside the clone, FIRESTARTER_FW_ROOT pointed at it), never an in-place mutation of the tracked sibling checkout -- the tracked checkout's git-porcelain state is a shared precondition many unrelated planted-violation controls in the SAME suite depend on."

requirements-completed: []

coverage:
  - id: D1
    description: "test_dispatch_mirror.py deleted; its firmware-doc ScanPathEntry removed from scan_paths.py (inventory 8->7, _FLOOR=6 still satisfied); the sibling test_configure_memory.cpp entry kept with an updated consumer note; the two parsing regexes and the DOC_FILE_TO_FUNC handler map are preserved verbatim below for 168-10 to lift"
    requirement: "MIGRATE-03"
    verification:
      - kind: unit
        ref: "tests/test_scan_paths_resolve.py -o addopts=\"\" -q -> 5 passed (includes the _FLOOR non-vacuity legs and ALL_CROSS_REPO_PATHS length == 7)"
        status: pass
      - kind: unit
        ref: "tests/test_fw_presence.py -o addopts=\"\" -q -> 7 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "tools/check_no_exists_proxy.py's default target list no longer names the deleted module -- a Rule 3 blocking-issue fix discovered during Task 1 verification (its own real-tree control test resolves the default list against disk and fails closed on any missing target)"
    requirement: "MIGRATE-03"
    verification:
      - kind: unit
        ref: "tests/test_check_no_exists_proxy.py -o addopts=\"\" -q -> 12 passed, including test_checker_exits_zero_on_real_default_tree"
        status: pass
    human_judgment: false
  - id: D3
    description: "fake_firestarter fixture rekeyed off include/firestarter.h; doc/PROTOCOLS.md stub and its parent directory deleted; the fixture README repointed to describe the surviving present-stub"
    requirement: "MIGRATE-04"
    verification:
      - kind: unit
        ref: "tests/test_fw_presence.py -o addopts=\"\" -q -> 7 passed, same count as before this task"
        status: pass
      - kind: other
        ref: "find tests/fixtures/fake_firestarter -type f | wc -l -> 2; grep -rc PROTOCOLS tests/fixtures/ tests/test_fw_presence.py -> 0 everywhere; git diff --stat shows no added '#' line in any touched .py file"
        status: pass
    human_judgment: false
  - id: D4
    description: "Reversible experiment proves the H-1 collection-abort hazard is severed: with firestarter/doc/ genuinely absent under a present, clean firmware sibling, the app suite collects (1972, no abort) and executes (1972 passed, 0 failed) -- the real /workspaces/firestarter checkout was left byte-identical throughout (HEAD unchanged, empty porcelain)"
    requirement: "MIGRATE-03"
    verification:
      - kind: integration
        ref: "evidence/h1-severance-proof.txt -- pytest --collect-only against an isolated scratch clone with doc/ removed and committed: '1972 tests collected in 1.13s'; full run: '1972 passed, 1 warning in 293.16s'; targeted five-module run: '50 passed in 1.42s'"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 04: Severing the H-1 Collection Hazard Summary

**Deleted the one module (`test_dispatch_mirror.py`) whose module-scope `fw_path("doc", "PROTOCOLS.md")` call aborted the entire app test suite at collection when `firestarter/doc/` went missing, rekeyed the fake-firmware fixture off the same vanishing path, and proved via an isolated scratch clone (not an in-place mutation of the tracked sibling repo) that the hazard is genuinely severed: 1972 tests collect and execute cleanly with `firestarter/doc/` absent, versus 1972 collected / 0 executed before this plan.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-08-31
- **Tasks:** 3 completed (all `type="auto"`)
- **Files modified:** 6 (4 planned edits, 1 additional Rule-3 fix, 1 evidence file; plus 1 new deferred-items.md log)

## Accomplishments

- Deleted `firestarter_app/tests/test_dispatch_mirror.py` in full (366 lines) — the only module in the app repo that resolves a firmware `doc/` path at import time via `fw_path`, which raises `MissingScanTargetError` under a present-but-mismatched firmware repo. Its two `§0`-table parsing regexes (`_BUCKET_ROW_RE`, `_FAMILY_ROW_RE`) and its `DOC_FILE_TO_FUNC` seven-handler map are preserved verbatim in this summary (below) for plan 168-10 to lift rather than re-derive.
- Removed the firmware-doc `ScanPathEntry("doc/PROTOCOLS.md", ("test_dispatch_mirror.py",))` from `tests/scan_paths.py`. `ALL_CROSS_REPO_PATHS` dropped from 8 to 7 entries, confirmed still above `test_scan_paths_resolve.py`'s `_FLOOR = 6` non-vacuity guard. Kept the sibling `test/native/avr/test_dispatch/test_configure_memory.cpp` entry per the plan's explicit instruction, updating its `resolved_by` tuple to name the relocated meta-repo consumer (`tools/wiki/dispatch_mirror.py`, 168-10) instead of the deleted module.
- Rekeyed the `fake_firestarter` fixture: deleted `tests/fixtures/fake_firestarter/doc/PROTOCOLS.md` and its parent directory, removed the corresponding present-stub assertion from `test_fw_presence.py` (the sibling `include/firestarter.h` assertion already covers the present-stub half of the contract), and repointed the fixture's own `README.md` to describe `include/firestarter.h` as the present stub.
- **Auto-fixed a Rule 3 blocking issue discovered during Task 1 verification:** `tools/check_no_exists_proxy.py`'s hardcoded `_DEFAULT_TARGETS` list still named `tests/test_dispatch_mirror.py`. That checker's own real-tree control test (`test_checker_exits_zero_on_real_default_tree`) resolves every default target against disk and fails closed (`FAIL: scan target(s) not found on disk`) on any missing one — deleting the module without this fix would have broken an unrelated, currently-green gate. Removed the stale entry.
- Ran the reversible H-1 severance experiment (Task 3) via an isolated scratch git clone of `/workspaces/firestarter` (same HEAD, `a218b4f5`) with `doc/` genuinely `git rm`'d and committed inside the clone only, then pointed `FIRESTARTER_FW_ROOT` at it for the app suite. Collection completed at 1972 tests with no abort line; the full run executed all 1972 with zero failures. The real, tracked `/workspaces/firestarter` checkout was verified untouched throughout (HEAD unchanged, empty porcelain). Evidence committed to `.planning/phases/168-.../evidence/h1-severance-proof.txt`.
- **Corrected the experimental method mid-task, and recorded why.** The plan's literal instruction ("a rename, not a delete") was tried first as an in-place `mv firestarter/doc firestarter/doc.tmp` on the real tracked checkout. That produced 9 spurious failures across 5 unrelated modules (`test_cap03_ack_layout_parity.py`, `test_json_key_parity.py`, `test_py32_asset_name_host.py`, `test_py32_flash_map_host.py`, `test_sdp_table_parity.py`), all of them "planted violation" controls asserting `git -C FW_ROOT status --porcelain() == ""` as a whole-repo cleanliness precondition — dirtying the tracked repo's working tree trips those controls for a reason that has nothing to do with `doc/` content. Reverted immediately (confirmed clean, HEAD unchanged) and re-ran via the scratch-clone method instead, which reproduces the exact H-1 precondition (a present, clean firmware repo missing `doc/`) without ever touching the real checkout.
- **Discovered the plan's failure-count prediction does not apply to this task's actual scope, and traced it to its real owner.** The plan's Task 3 text expects "17 genuine doc-caused assertion failures" across five modules, but those modules (`test_lockable_proms_doc_claims.py` etc.) read `firestarter_app/doc/` (the app's OWN doc directory via `_FA_DIR / "doc" / ...`), not `firestarter/doc/` (the firmware sibling's doc directory this task actually removes). Ran the five named modules directly against the doc-less firmware clone to confirm: 50/50 passed, zero failures — `firestarter_app/doc/` was never touched. Cross-checked against `ROADMAP.md`: plan 168-09 explicitly owns "Remove the 17 doc test legs from 5 modules ... delete `firestarter_app/doc/`" — confirming the 17-failure prediction belongs there, not here.

## Task Commits

1. **Task 1: Retire the app-side dispatch-mirror module and its scan-path entry** - `39ea3e8` (fix, `firestarter_app`)
2. **Task 2: Rekey the fake-firmware fixture off the vanishing doc path** - `6fba178` (fix, `firestarter_app`)
3. **Task 3: Prove the coupling is severed** - `63756e24` (test, meta repo — evidence file only, per the task's own "commits nothing outside the evidence file" scope)

## Files Created/Modified

- `firestarter_app/tests/test_dispatch_mirror.py` - **deleted** (366 lines; the module-scope `fw_path` collection hazard)
- `firestarter_app/tests/scan_paths.py` - removed the firmware-doc `ScanPathEntry`; updated the surviving sibling entry's `resolved_by` tuple
- `firestarter_app/tools/check_no_exists_proxy.py` - removed the stale `tests/test_dispatch_mirror.py` line from `_DEFAULT_TARGETS` (Rule 3 auto-fix)
- `firestarter_app/tests/test_fw_presence.py` - removed the `doc/PROTOCOLS.md` present-stub assertion from `test_committed_fixture_is_genuinely_incomplete`
- `firestarter_app/tests/fixtures/fake_firestarter/doc/PROTOCOLS.md` - **deleted**, with its now-empty parent `doc/` directory
- `firestarter_app/tests/fixtures/fake_firestarter/README.md` - repointed to describe `include/firestarter.h` as the sole present stub
- `.planning/phases/168-.../evidence/h1-severance-proof.txt` - **created** (Task 3's measured evidence, meta repo commit)
- `.planning/phases/168-.../deferred-items.md` - **created** (out-of-scope discovery log, see below)

## Preserved for plan 168-10 (per Task 1's acceptance criterion)

Verbatim from the deleted module, `firestarter_app/tests/test_dispatch_mirror.py:72-91`:

```python
_BUCKET_ROW_RE = re.compile(
    r"^\|\s*0x([0-9A-Fa-f]+)\s*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
)
_FAMILY_ROW_RE = re.compile(
    r"^\|\s*([a-z0-9_-]+)\s*\|\s*`[a-z0-9_]+\(\)`\s*\|\s*`([a-z0-9_]+\.cpp)`\s*\|"
)
DOC_FILE_TO_FUNC: dict[str, str] = {
    "flash_5v_page.cpp": "configure_flash_5v_page",
    "flash_nor_unlock.cpp": "configure_flash_nor_unlock",
    "eprom.cpp": "configure_eprom",
    "eeprom_28c.cpp": "configure_eeprom28c",
    "flash_intel.cpp": "configure_flash_intel",
    "sram.cpp": "configure_sram",
    "not_implemented.cpp": "not_implemented",
}
```

`_BUCKET_ROW_RE` needs a 7-column pipe row (`| 0xNN | ... | ... | ... | ... | <family> | <phantom?> |`); `_FAMILY_ROW_RE` needs a 4-column row (`| <family> | \`configure_*()\` | \`<file>.cpp\` | ... |`). Both are table-shape dependencies, not content ones — 168-05's migration of `PROTOCOLS.md` §0 should preserve these table shapes byte-for-byte if the relocated checker is to parse the wiki page without modification.

## Decisions Made

- Kept the surviving `ScanPathEntry` for `test_configure_memory.cpp` rather than removing it, per the plan's explicit instruction — its `resolved_by` tuple now documents the relocated meta-repo consumer instead of claiming a consumer that no longer exists.
- Ran the Task 3 experiment via an isolated scratch git clone with a real, committed `doc/` removal, deviating from the plan's literal "rename, not a delete" instruction on the tracked checkout — see Deviations below for the measured reason.
- Left `requirements-completed` empty for both `MIGRATE-03` and `MIGRATE-04` despite both being declared in this plan's frontmatter — neither is actually complete after this plan (the real `firestarter/doc/` deletion is 168-07's job; the bulk of the 30-file repair surface and `firestarter_app/doc/` deletion are 168-06/168-07/168-09's). Marking either complete here would repeat a known project failure mode (executors prematurely closing multi-plan requirements).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `tools/check_no_exists_proxy.py`'s default target list named the deleted module**
- **Found during:** Task 1's verification (running `tests/test_check_no_exists_proxy.py` proactively before committing)
- **Issue:** `_DEFAULT_TARGETS` is a literal, committed enumeration of `tests/*.py` files that this recurrence-lint checker scans by default. It still listed `"tests/test_dispatch_mirror.py"` after that file was deleted. The checker's own `main()` resolves every default target against disk and fails closed (`missing = [t for t in targets if not os.path.isfile(t)]`) — so `test_checker_exits_zero_on_real_default_tree` (which calls `main()` with the real default list) would have started failing as a direct, mechanical consequence of Task 1's deletion, on a module not named in this plan's `files_modified`.
- **Fix:** Removed the stale line from `_DEFAULT_TARGETS`.
- **Files modified:** `firestarter_app/tools/check_no_exists_proxy.py`
- **Verification:** `pytest tests/test_check_no_exists_proxy.py -o addopts="" -q` → 12 passed (unchanged count), including the real-tree control test.
- **Committed in:** `39ea3e8` (Task 1 commit)

**2. [Rule 1 - Bug] Task 3's literal in-place rename produced 9 spurious failures unrelated to `doc/` content**
- **Found during:** Task 3's first attempt (`mv firestarter/doc firestarter/doc.h1-severance-tmp` on the real, tracked checkout, then a full suite run)
- **Issue:** 9 tests across 5 unrelated modules failed, all "planted violation" controls asserting `git -C FW_ROOT status --porcelain() == ""` as a whole-repo cleanliness precondition (proving a plant never touched the real firmware file). Renaming a tracked directory out from under a live git checkout dirties that whole-repo reading for reasons that have nothing to do with `doc/` content — a false positive against the task's own severance claim.
- **Fix:** Reverted the in-place rename immediately (confirmed `firestarter/doc` restored, HEAD unchanged, empty porcelain), then re-ran the experiment against an isolated scratch git clone with `doc/` genuinely `git rm`'d and committed inside the clone only. The real checkout was never touched by the corrected method.
- **Files modified:** None outside the evidence file (per the task's own scope) — this was a methodology correction, not a code change.
- **Verification:** `evidence/h1-severance-proof.txt` documents both attempts and the measured reason for the correction.
- **Committed in:** `63756e24` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug-in-methodology)
**Impact on plan:** Both were necessary corrections discovered during verification, not scope creep. Neither changed the plan's intended files_modified for Tasks 1–2; the methodology fix in Task 3 produced a cleaner, more attributable result than the plan's literal instruction would have.

## Issues Encountered

The plan's Task 3 "expect 17 failures" paragraph does not describe this task's actual configuration (see Accomplishments and Decisions above) — not an issue requiring a fix, but a factual correction worth flagging because it is the kind of unverified-claim drift this whole phase exists to catch. Traced to its real owner (plan 168-09) via `ROADMAP.md` rather than left unresolved.

Two fixture files became orphaned by Task 1's deletion (`tests/fixtures/planted_dispatch_missing_hex.cpp`, `tests/fixtures/planted_dispatch_comment_only_hex.cpp`) — no test currently fails as a result, so left in place per the scope-boundary discipline and logged to `deferred-items.md` for a later cleanup pass.

## User Setup Required

None. All verification ran against the existing `.venv/ci-replica` Python 3.11 venv already present in the repo (no network access or credentials needed for this plan's tasks).

## Next Phase Readiness

- The H-1 ordering constraint that blocked plan 168-07 is resolved and observed, not merely reasoned: plan 168-07 can now delete `firestarter/doc/` without silencing the app test suite.
- `firestarter_app` is on `gsd/v1.35-documentation-consolidation-wiki-migration` with 2 new commits (`39ea3e8`, `6fba178`), full suite green (1972 passed, matching the pre-plan 1976 minus the 4 deleted dispatch-mirror legs), tree clean except this plan's own changes.
- The meta repo has 1 new commit (`63756e24`) adding the H-1 evidence file; `.planning/config.json`, `.planning/notes/dev-test-sequence-cost-model.md`, `package.json`, `package-lock.json`, and the pending todo file were pre-existing uncommitted changes not owned by this plan and were left untouched.
- `firestarter_app/doc/` (10 files, including the deferred `PY32F071-FIRMWARE-INSTALL.md`) is completely untouched and still exists — plan 168-09 owns its deletion and the associated 17 doc-leg removals across the five named modules.
- No blockers for plan 168-07 or subsequent Wave 3 plans.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*

## Self-Check: PASSED

- FOUND: firestarter_app/tests/scan_paths.py
- FOUND: firestarter_app/tests/test_fw_presence.py
- FOUND: test_dispatch_mirror.py correctly absent
- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/h1-severance-proof.txt
- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/168-04-SUMMARY.md
- FOUND commit: 39ea3e8 (firestarter_app)
- FOUND commit: 6fba178 (firestarter_app)
- FOUND commit: 63756e24 (meta)
