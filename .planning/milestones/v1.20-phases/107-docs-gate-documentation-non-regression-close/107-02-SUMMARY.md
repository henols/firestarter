---
phase: 107-docs-gate-documentation-non-regression-close
plan: 02
subsystem: infra
tags: [codegen, messages-catalog, toml, cross-repo-sync, firmware, python]

requires:
  - phase: 105-fw-firmware-mem-type-removal
    provides: "Firmware retired MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE) from messages.h/messages.toml"
provides:
  - "0xAE removed from meta canonical + both vendored messages.toml"
  - "messages.py / messages.h regenerated 0xAE-free via codegen.py (no hand-edits)"
  - "Meta canonical toml reconciled with a pre-existing, unrelated Phase-95 desync (0x85/0xBC FL4_BOOT_BLOCK_LOCKED messages) discovered while running the sync"
affects: [107-03]

tech-stack:
  added: []
  patterns: ["canonical-toml -> sync_to_subrepos.sh -> codegen.py regen (never hand-edit generated messages.py/messages.h)"]

key-files:
  created: []
  modified:
    - tools/catalog/messages.toml
    - firestarter/tools/catalog/messages.toml
    - firestarter/include/messages.h
    - firestarter_app/tools/catalog/messages.toml
    - firestarter_app/firestarter/messages.py

key-decisions:
  - "Restored MSG_WARN_FL4_BOOT_BLOCK_LOCKED (0x85) / MSG_ERR_FL4_BOOT_BLOCK_LOCKED (0xBC) to the meta canonical toml before running the 0xAE sync, because they existed in the host's vendored catalog since Phase 95 but were never present in the canonical source — running the sync without restoring them first silently deleted them from messages.py and broke tests/test_val_wire_5v_page.py (caught by full pytest run, fixed under Rule 1 before commit)"
  - "Firmware's include/messages.h/toml gained the same two message definitions as an inert side effect (firmware source never references either name) — accepted as a correctness fix to the canonical source of truth, not a firmware behavior change"

patterns-established: []

requirements-completed: [DOC-01]

coverage:
  - id: D1
    description: "Retired MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE) removed from canonical + both vendored messages.toml and regenerated out of messages.py/messages.h via codegen.py"
    requirement: "DOC-01"
    verification:
      - kind: unit
        ref: "grep -rn 'MSG_ERR_MEM_TYPE_UNSUPPORTED|0xAE|0xae' across all 5 files — 0 hits"
        status: pass
      - kind: integration
        ref: "python tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check (firestarter_app) — OK: catalog valid (66 messages)"
        status: pass
      - kind: integration
        ref: "regen-to-temp diff of messages.py and messages.h vs committed files — empty diff (no hand-edit drift)"
        status: pass
    human_judgment: false
  - id: D2
    description: "No other message definition altered; MSG_ERR_VERIFY (0xAF) and all others preserved; vendored sub-repo toml copies stay byte-identical"
    requirement: "DOC-01"
    verification:
      - kind: unit
        ref: "grep -c 'MSG_ERR_VERIFY' tools/catalog/messages.toml == 1"
        status: pass
      - kind: unit
        ref: "diff -q firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml — clean"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full non-regression sweep after the catalog change: firmware native suite, host pytest, check_dispatch.py, diff_db.py all green or matching the documented pre-existing baseline"
    requirement: "DOC-01"
    verification:
      - kind: integration
        ref: "pio test -e native (firestarter) — 80/80 PASS"
        status: pass
      - kind: integration
        ref: "python -m pytest (firestarter_app) — 710 passed, 1 pre-existing failure (test_golden_file_matches, unrelated to messages catalog)"
        status: pass
      - kind: integration
        ref: "python tools/check_dispatch.py — PASS, 0 dispatch regressions, 0 consistency violations"
        status: pass
      - kind: integration
        ref: "python tools/diff_db.py — PASS, 2 pre-explained chip changes (Phase 94 page_size), 0 unexplained"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-07-02
status: complete
---

# Phase 107 Plan 02: Retire 0xAE Codegen Desync Summary

**Removed the retired `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` message from the canonical catalog and regenerated host/firmware artifacts, incidentally catching and fixing an unrelated pre-existing Phase-95 catalog desync (`MSG_WARN`/`MSG_ERR_FL4_BOOT_BLOCK_LOCKED`) that the naive sync would otherwise have silently deleted from the host, breaking a live test.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-07-02T14:54:43Z
- **Completed:** 2026-07-02T15:07:17Z
- **Tasks:** 2
- **Files modified:** 5 (across meta repo + 2 sub-repos)

## Accomplishments
- Deleted the dead `[[messages]] id = 0xAE name = "MSG_ERR_MEM_TYPE_UNSUPPORTED"` block from the meta canonical `tools/catalog/messages.toml`, then ran the canonical `sync_to_subrepos.sh` regen path to propagate to both sub-repos and regenerate `messages.h` (firmware) / `messages.py` (host) via `codegen.py` — never hand-edited.
- Confirmed the codegen drift gate is clean: `codegen.py --check` exits 0 (66 messages, valid), and a regen-to-temp diff of both `messages.py` and `messages.h` against the committed files is byte-empty (faithful regeneration, no drift).
- Discovered mid-task that the meta canonical toml was also missing two unrelated, host-only Phase-95 messages (`MSG_WARN_FL4_BOOT_BLOCK_LOCKED` 0x85, `MSG_ERR_FL4_BOOT_BLOCK_LOCKED` 0xBC) that existed only in the vendored host toml/`messages.py` — never synced back to canonical. The first sync run silently deleted them from `messages.py`, breaking `tests/test_val_wire_5v_page.py` (2 failing tests). Restored both to the canonical toml and re-ran the sync before committing, so the fix ships alongside the 0xAE removal rather than as a silent regression.
- Ran the full non-regression sweep after the fix: firmware native suite 80/80 PASS, host pytest 710 passed / 1 pre-existing failure (matches the Phase 107 RESEARCH.md documented baseline exactly, unrelated to this change), `check_dispatch.py` and `diff_db.py` both clean.

## Task Commits

Each task was committed atomically, inside the correct repo:

1. **Task 1: Remove the 0xAE `[[messages]]` block + regenerate via `sync_to_subrepos.sh`**
   - `759f803` (firestarter submodule) — `chore(catalog): sync canonical messages.toml (drop 0xAE, restore 0x85/0xBC)`
   - `0e9137f` (firestarter_app submodule) — `chore(catalog): remove retired MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)`
   - `4cb0d56` (meta repo) — `chore(107-02): remove retired 0xAE + reconcile FL4_BOOT_BLOCK canonical drift`
2. **Task 2: Confirm the codegen drift gate is clean** — verification-only task; no additional file changes. Results folded into the Task 1 commit messages and this SUMMARY's coverage evidence (codegen `--check` exit 0; regen-to-temp diffs empty for both `messages.py` and `messages.h`).

## Files Created/Modified
- `tools/catalog/messages.toml` (meta) — removed 0xAE block; restored 0x85/0xBC blocks (pre-existing canonical omission)
- `firestarter/tools/catalog/messages.toml` — synced from canonical (byte-identical to `firestarter_app`'s copy)
- `firestarter/include/messages.h` — regenerated via `codegen.py` (cpp target); gained the two restored message `#define`s (inert — firmware source never references them), 0xAE was already absent
- `firestarter_app/tools/catalog/messages.toml` — synced from canonical
- `firestarter_app/firestarter/messages.py` — regenerated via `codegen.py` (python target); 0xAE removed, 0x85/0xBC preserved (were already present pre-sync)

## Decisions Made
- **Restored 0x85/0xBC to the canonical toml before finalizing the 0xAE sync.** These two messages existed in the host's vendored `messages.toml`/`messages.py` since Phase 95 (W29C040 boot-block-lockout feature) but were never present in the meta canonical `tools/catalog/messages.toml` — an independent, pre-existing cross-repo desync unrelated to the `mem_type` removal. Running the sanctioned `sync_to_subrepos.sh` sync without correcting this first would have silently deleted both messages from `messages.py` (since the canonical source doesn't define them), breaking `tests/test_val_wire_5v_page.py::test_warn_fl4_boot_block_locked_in_catalog` and `::test_err_fl4_boot_block_locked_section_6_6_text`. This is a Rule 1 auto-fix (bug caused directly by the mandated regen step) — restored the exact original block content (verified via `git show HEAD:tools/catalog/messages.toml` in `firestarter_app`) and re-ran the sync so the final state has zero regressions.
- **Firmware `messages.h`/`messages.toml` gained the two restored message definitions as an inert side effect.** Grepped `firestarter/src/` and `include/` — neither name is referenced anywhere in firmware source; the two `#define`s are unused constants. This is a correction of the canonical source-of-truth catalog (which should always have matched the host), not a firmware behavior change, and does not affect dispatch, wire format, or any other verified message.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Restored a pre-existing Phase-95 canonical-toml omission (0x85/0xBC) before it could be silently regressed by the 0xAE sync**
- **Found during:** Task 1 (running `sync_to_subrepos.sh` after removing the 0xAE block)
- **Issue:** The meta canonical `tools/catalog/messages.toml` was independently missing `MSG_WARN_FL4_BOOT_BLOCK_LOCKED (0x85)` and `MSG_ERR_FL4_BOOT_BLOCK_LOCKED (0xBC)`, which the host's vendored copy and `messages.py` had carried since Phase 95. The first sync run (0xAE-removal only) regenerated `messages.py` from the now-de-synced canonical source and silently dropped both messages, breaking 2 tests in `tests/test_val_wire_5v_page.py` (`ImportError: cannot import name 'MSG_WARN_FL4_BOOT_BLOCK_LOCKED'`).
- **Fix:** Restored both `[[messages]]` blocks to the meta canonical toml (exact content recovered via `git show HEAD:tools/catalog/messages.toml` in `firestarter_app`, the pre-sync source of truth for these two entries), then re-ran `sync_to_subrepos.sh`. Firmware's `include/messages.h` gained the same two `#define`s as an inert byproduct (never referenced by firmware source).
- **Files modified:** `tools/catalog/messages.toml` (meta), `firestarter/tools/catalog/messages.toml`, `firestarter/include/messages.h`, `firestarter_app/tools/catalog/messages.toml`, `firestarter_app/firestarter/messages.py`
- **Verification:** `python -m pytest tests/test_val_wire_5v_page.py -q` — 14/14 pass (previously 2 failing); full host suite re-run — 710 passed / 1 pre-existing unrelated failure (unchanged from the documented baseline); firmware native suite 80/80 PASS.
- **Committed in:** `759f803` (firestarter), `0e9137f` (firestarter_app), `4cb0d56` (meta) — folded into the Task 1 commits since the fix was required to make the sanctioned sync run safely, not a separate follow-up.

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug caused by the mandated regen step)
**Impact on plan:** The auto-fix was necessary to avoid shipping a real regression as a side effect of the sanctioned 0xAE removal. No scope creep beyond the message catalog itself — no dispatch, wire-format, or behavior change; strictly a catalog-consistency correction. The 0xAE removal itself is exactly as scoped (D-06): only that one block deleted, all other messages (including 0xAF `MSG_ERR_VERIFY`) byte-identical.

## Issues Encountered
None beyond the deviation documented above (which was caught and resolved before any commit landed).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- 0xAE fully retired from every layer (firmware, meta canonical, both sub-repo vendored copies, generated artifacts) — v1.20 now has zero `mem_type`-family residue in the message catalog.
- Codegen drift gate clean; full non-regression sweep green (matching the Phase 107 RESEARCH.md pre-existing baseline exactly — no new regressions).
- Ready for 107-03 (final gate sweep / phase close).

---
*Phase: 107-docs-gate-documentation-non-regression-close*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: `.planning/phases/107-docs-gate-documentation-non-regression-close/107-02-SUMMARY.md`
- FOUND (firestarter submodule): `759f803`
- FOUND (firestarter_app submodule): `0e9137f`
- FOUND (meta repo): `4cb0d56`
