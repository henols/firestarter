---
phase: 151-protection-readability-lock-status
plan: 05
subsystem: firmware-protocol
tags: [messages-catalog, codegen, wire-protocol, dual-repo, pytest, ruff, mypy]

# Dependency graph
requires:
  - phase: 151-01
    provides: 151-DESIGN.md §1's wire shape decision (two-byte DATA id-frame, raw byte + decode code, 0xFF sentinel)
  - phase: 151-03
    provides: CMD_LOCK_STATUS 16, admitted at the wire-protocol layer
provides:
  - "MSG_DATA_PROTECTION_STATUS = 0xE1 minted in tools/catalog/messages.toml (DATA severity, two u8 params, wire_format=id_frame)"
  - "All three messages.toml copies (meta, firestarter, firestarter_app) byte-identical after sync"
  - "firestarter/include/messages.h regenerated (77 messages), ID-only, proven idempotent via a second regen + git diff --exit-code"
  - "firestarter_app/firestarter/messages.py regenerated (77 messages), proven idempotent the same way"
  - "firestarter_app/tests/test_protection_status_catalog.py — 5-leg catalog-presence proof, including a durable guard that 0xBF (ERROR band's last free id, C-11) stays unspent"
affects: [151-06, 151-08, 151-11, 151-13]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Catalog-presence test committed for an id with no emit site yet, following the test_val_wire_5v_page.py precedent (test_warn_fl4_boot_block_locked_in_catalog)."
    - "A regen's git diff is re-run a second time after landing to prove idempotency, rather than trusting the first sync's diff alone — this is the only local proof on the firmware side, which carries no CI drift gate."

key-files:
  created:
    - firestarter_app/tests/test_protection_status_catalog.py
  modified:
    - tools/catalog/messages.toml
    - firestarter/tools/catalog/messages.toml
    - firestarter/tools/catalog/codegen.py
    - firestarter/include/messages.h
    - firestarter_app/tools/catalog/messages.toml
    - firestarter_app/tools/catalog/codegen.py
    - firestarter_app/firestarter/messages.py

key-decisions:
  - "Chose id 0xE1 — the lowest free DATA-band value, confirmed by a tomllib occupancy pass (occupied: 0xE0, 0xE2, 0xE4, 0xE5, 0xE6, 0xF0) — rather than any ERROR-band id, per 151-DESIGN.md §1 and C-11."
  - "format string reads 'Lock status probe: raw=0x%02X decode=%u' — an observation, not a state claim; contains neither 'protected' nor 'unprotected' as a bare assertion (T-151-21 mitigation)."
  - "params = two u8 entries (raw silicon byte with hex_byte render, decode code with default dec render), matching the two-byte payload 151-DESIGN.md §1 fixes."
  - "Left the two pre-existing MSG_WARN_FL4_BOOT_BLOCK_LOCKED (0x85) / MSG_ERR_FL4_BOOT_BLOCK_LOCKED (0xBC) rows untouched — Plan 151-08 may give them an emit site without minting anything."

patterns-established:
  - "A single catalog edit propagates through exactly five tracked files across three repositories in one plan, each regen re-verified idempotent before commit."

requirements-completed: []

coverage:
  - id: D1
    description: "MSG_DATA_PROTECTION_STATUS minted at 0xE1 in the meta catalog, DATA severity, two u8 params, wire_format=id_frame; codegen.py --check passes"
    verification:
      - kind: unit
        ref: "python3 tools/catalog/codegen.py --check --catalog tools/catalog/messages.toml (exit 0, 77 messages)"
        status: pass
      - kind: other
        ref: "tomllib occupancy pass + assertion script (id in range, params==[u8,u8], wire_format=id_frame, 0xBF absent, no duplicate ids)"
        status: pass
    human_judgment: false
  - id: D2
    description: "All three messages.toml copies (meta/firestarter/firestarter_app) byte-identical; both generated outputs (messages.h, messages.py) regenerated and proven idempotent"
    verification:
      - kind: other
        ref: "bash tools/catalog/sync_to_subrepos.sh (exit 0) + md5sum of the three copies (single checksum) + a second codegen.py invocation each producing git diff --exit-code clean on include/messages.h and firestarter/messages.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "firestarter/include/messages.h stays ID-only (no format string leaked); grep count of the new define is exactly 1; importing the name from firestarter.messages succeeds"
    verification:
      - kind: other
        ref: "grep -c MSG_DATA_PROTECTION_STATUS firestarter/include/messages.h == 1; python3 -c import firestarter.messages.MSG_DATA_PROTECTION_STATUS == 0xE1"
        status: pass
    human_judgment: false
  - id: D4
    description: "Committed catalog-presence test: id literal, DATA severity, two-u8 param shape, 0xBF absence (C-11 guard), boot-block ids undisturbed"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_protection_status_catalog.py (5 tests, pytest -x -o addopts=\"\")"
        status: pass
    human_judgment: false
  - id: D5
    description: "Leonardo build stays inside the unguarded 28672 B Caterina cliff, byte-for-byte unchanged from the 151-03 baseline since the new id has no emit site yet"
    verification:
      - kind: other
        ref: "pio run -e uno -> 25166 B flash/1575 B RAM; pio run -e leonardo -> 27248 B flash/2016 B RAM (identical to 151-03); margin 28672-27248 = 1424 B (UNGUARDED)"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-20
status: complete
---

# Phase 151 Plan 05: `MSG_DATA_PROTECTION_STATUS` Catalog Mint & Dual-Repo Regen Summary

**Minted one new DATA-band catalog id (`0xE1`, two `u8` params) and propagated it through the codegen path across all five tracked files in three repositories, each generated output re-verified idempotent before commit, while leaving the ERROR band's last free id `0xBF` unspent behind a durable pytest guard.**

## Performance

- **Duration:** ~35 min
- **Started:** ~2026-08-20T13:45Z (approximate)
- **Completed:** 2026-08-20T14:20Z
- **Tasks:** 3 completed
- **Files modified:** 7 (1 meta catalog, 2 firmware [catalog copy + generated header], 2 firmware vendored codegen.py, 2 app [catalog copy + generated messages.py]) + 1 new app test file

## Accomplishments

- Meta catalog `tools/catalog/messages.toml` gained one row: `MSG_DATA_PROTECTION_STATUS = 0xE1`, `severity = "DATA"`, `format = "Lock status probe: raw=0x%02X decode=%u"`, `params = [{u8, hex_byte}, {u8}]`, `wire_format = "id_frame"` — placed immediately after `MSG_DATA_PROGRESS` (0xE0) with a Phase 151 / LOCK-02 comment block naming the raw-byte/decode-code/0xFF-sentinel contract from `151-DESIGN.md` §1. `codegen.py --check` passes at 77 messages.
- The id `0xE1` is the lowest free DATA-band value, confirmed by a `tomllib` occupancy pass over the full catalog before choosing (occupied: `0xE0`, `0xE2`, `0xE4`, `0xE5`, `0xE6`, `0xF0`) — not the ERROR band's `0xBF`, which stays the band's single free slot.
- `bash tools/catalog/sync_to_subrepos.sh` copied the catalog and `codegen.py` into both sub-repos and regenerated `firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py`. Both outputs were then regenerated a **second** time after landing, each producing a clean `git diff --exit-code` — the load-bearing proof on the firmware side, which carries no CI drift gate. All three `messages.toml` copies share one checksum.
- Incidental fix surfaced by the regen (not authored in this plan): both sub-repos' vendored `tools/catalog/codegen.py` carried a stale 2024 copyright banner relative to meta's already-2026 template (an earlier, unrelated meta commit — `3c4de81f Update copyright year` — had never been synced down because the firmware side has no drift gate). The sync step's routine copy of `codegen.py` brought both current; this produced the "2024 -> 2026" banner lines alongside the new id in both generated files' diffs, and both regenerated files' message counts moved 76 -> 77.
- `firestarter/include/messages.h` stays strictly ID-only: `grep -c 'MSG_DATA_PROTECTION_STATUS'` is 1, and no format string for the new id appears anywhere in the file.
- New `firestarter_app/tests/test_protection_status_catalog.py` (5 legs, none asserting full format-string text): id literal `0xE1`; `CATALOG` membership with `SEVERITY_DATA`; param shape exactly `["u8", "u8"]`; `0xBF` absent from every `CATALOG` id (citing C-11 in its docstring); and both pre-existing boot-block ids (`0x85`/`0xBC`) present with unchanged severities.
- `pio run -e uno` and `-e leonardo` both build clean with the regenerated header: uno 25166 B flash / 1575 B RAM, leonardo 27248 B flash / 2016 B RAM — byte-for-byte identical to the 151-03 baseline, because the new `#define` has no emit site referencing it yet (Plan 151-08 lands that). Leonardo's unguarded Caterina-cliff margin (`28672 - 27248`) stays **1424 B, UNGUARDED**.
- Full `firestarter_app` host suite: 1713 passed (up from 1708 at 151-03, +5 new legs), 0 failed, in 303.65s. `ruff check`/`ruff format --check` clean. `check_mypy_watermark.py` run under a `uv`-managed Python 3.11 venv (this devcontainer's default 3.12 fails it closed on the known numpy-stub syntax issue): 34 errors, 1 below the watermark of 35, no new errors.

## Task Commits

Each task was committed atomically, dual-repo:

1. **Task 1: Add `MSG_DATA_PROTECTION_STATUS` to the meta catalog and pass `codegen.py --check`** — meta `a21ac4f5` (feat)
2. **Task 2: Sync and regenerate all five tracked files, and prove neither generated file is stale** — firestarter `f66d817` (feat), firestarter_app `bc47b14` (feat), meta `df1af512` (chore: gitlink bumps)
3. **Task 3: A committed catalog-presence test, in the in-tree precedent's shape** — firestarter_app `3f33f7e` (test), meta `1b4b7fe1` (chore: gitlink bump)

**Plan metadata:** recorded in this SUMMARY commit (meta repo).

_Note: this plan's `commits_land_in: [meta, firestarter, firestarter_app]` — the meta repo carries the catalog-row commit (Task 1) plus two gitlink-bump commits (Tasks 2 and 3); firestarter and firestarter_app each carry their own regen/test commits._

## Files Created/Modified

- `tools/catalog/messages.toml` — new `MSG_DATA_PROTECTION_STATUS` row at `0xE1` + Phase 151 comment block
- `firestarter/tools/catalog/messages.toml` — synced copy (byte-identical to meta)
- `firestarter/tools/catalog/codegen.py` — synced copy (picks up the pending 2024->2026 copyright fix)
- `firestarter/include/messages.h` — regenerated: 76 -> 77 messages, adds `#define MSG_DATA_PROTECTION_STATUS 0xE1`
- `firestarter_app/tools/catalog/messages.toml` — synced copy (byte-identical to meta)
- `firestarter_app/tools/catalog/codegen.py` — synced copy (same banner fix)
- `firestarter_app/firestarter/messages.py` — regenerated: 76 -> 77 messages, adds the `0xE1` `MessageDef` entry
- `firestarter_app/tests/test_protection_status_catalog.py` (new) — 5-leg catalog-presence proof

## Decisions Made

- Chose `0xE1` as the lowest free DATA-band id, verified by a `tomllib` occupancy pass, rather than reusing an ERROR-band id — per `151-DESIGN.md` §1 and C-11 (ERROR band has exactly one free id, `0xBF`, with no documented band-extension procedure).
- Format string worded as an observation ("raw=... decode=...") with no bare "protected"/"unprotected" assertion, per the action's requirement and T-151-21's mitigation — the class token is produced on the host, not in this catalog string.
- Params declared as two `u8` entries (first with `render = "hex_byte"` for the raw silicon byte, second with the default `dec` render for the decode code), matching the precedent set by `MSG_INFO_REG_HEADER`'s byte-buffer param declaration style.
- Left `MSG_WARN_FL4_BOOT_BLOCK_LOCKED` (0x85) and `MSG_ERR_FL4_BOOT_BLOCK_LOCKED` (0xBC) completely untouched, per the plan's explicit instruction — Plan 151-08 may give them an emit site without any catalog change.
- Ran `check_mypy_watermark.py` under a `uv`-managed Python 3.11 venv rather than this devcontainer's default 3.12, which fails the gate closed on an unrelated numpy stub syntax issue (documented project environment trap, consistent with 151-03's finding).

## Deviations from Plan

None — plan executed exactly as written. The copyright-banner diff surfaced by the regen (2024 -> 2026 in both sub-repos' vendored `codegen.py`) is a mechanical consequence of Task 2's own instruction to sync `codegen.py` alongside `messages.toml` — the meta repo's `codegen.py` had already carried the 2026 banner since an earlier, unrelated commit (`3c4de81f`), and the firmware/app sides simply had never re-synced since (no drift gate on the firmware side per the plan's own `key_links`). This is recorded here as an observed consequence, not a discovery requiring a numbered Rule.

## Issues Encountered

None. `check_mypy_watermark.py` under this devcontainer's default Python 3.12 fails closed on the same unrelated numpy stub issue documented in 151-03's SUMMARY; resolved the same way, via a `uv`-managed Python 3.11 venv (`uv venv --python 3.11`), producing 34 errors / 1 below the watermark of 35, no new errors introduced by this plan's new test file.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `MSG_DATA_PROTECTION_STATUS = 0xE1` exists in all three catalog copies and both generated outputs, ready for Plan 151-08 (the firmware emit site via `LOG_DATA_ID_BYTES`) and Plan 151-11 (the host response-consuming decode).
- The ERROR band's last free id `0xBF` remains unspent, now with a durable pytest guard (`test_error_band_last_free_id_unspent`) in addition to the RESEARCH.md C-11 measurement.
- Leonardo's Caterina-cliff margin after this plan is unchanged at 1424 B (the new id costs zero firmware bytes until an emit site references it) — 151-10's cold-rebuild MERGE-05 measurement remains the authoritative post-all-firmware-plans figure.
- No requirement was flipped (`requirements: []`); this plan **advances** `LOCK-02`, whose checkbox flip belongs to Plan 151-13.
- Plan 151-04 (datasheet sourcing, non-autonomous) remains not yet executed; this plan ran ahead of it in numeric order because wave 1's `depends_on: []` plans may execute independently.

---
*Phase: 151-protection-readability-lock-status*
*Completed: 2026-08-20*

## Self-Check: PASSED

All 5 created/modified files verified present on disk (`tools/catalog/messages.toml`,
`firestarter/include/messages.h`, `firestarter_app/firestarter/messages.py`,
`firestarter_app/tests/test_protection_status_catalog.py`, this SUMMARY.md); all 5 commits
(meta `a21ac4f5`, `df1af512`, `1b4b7fe1`; firestarter `f66d817`; firestarter_app `bc47b14`,
`3f33f7e`) verified present in their respective repositories' `git log --oneline --all`.
