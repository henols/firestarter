---
phase: 02-naming-cleanup-wire-key-minipro-references
plan: 02
subsystem: data-files-and-internal-naming
tags: [clean-01, file-rename, git-mv, vpp_volts, packaging-fix, manifest-in, pyproject-toml, internal-dict-key]

# Dependency graph
requires:
  - phase: 02-naming-cleanup-wire-key-minipro-references
    plan: 01
    provides: WIRE-01 source-state assertion (Python emits "vpp_mv"; firmware parses "vpp_mv"; database.py:518 stable)
provides:
  - CLEAN-01 source-state assertion (chip-database file renamed; all 7 callsites flipped; blame chain preserved across rename)
  - D-04 internal vpp_volts rename closed (_map_data dict-write + emitter fallback + 2 downstream consumers symmetric with vpp_mv sibling)
  - Packaging-drift closure (v1.0 Phase 11 pyproject.toml + MANIFEST.in stale entries replaced with real shipping files)
  - SC#5 initial discharge (pip install -e . + firestarter info W27C512 exit 0 against the renamed DB)
affects:
  - Plan 02-03 (CLEAN-02 attribution scrub + WIRE-02 check_dispatch.py augmentation + full SC#5 CLI smoke — consumes the renamed file + the renamed internal dict key as post-state contract)
  - Future Phase 4 / HW-* hardware-validation scripts (will reference chip_database.json, not minipro_complete_db.json)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Atomic CLEAN-01 batch: git mv + 7 callsite path-flips staged together in one firestarter_app/ commit so working-tree readers stay valid at every revision (Phase 11 precedent: git mv parse_db_2.py build_db.py)"
    - "Index-only partial staging via `cp <worktree> /tmp/backup && git checkout HEAD -- <file> && <re-apply scoped edit> && git add <file> && cp /tmp/backup <file>` — isolates a single scoped line from a co-located out-of-scope reformat without disturbing the working tree's load-bearing pre-existing state"
    - "Three-layer 'vpp' semantic distinction preserved: upstream-schema READ (electrical.get('vpp', '0').replace('V','')) PRESERVED at database.py:375; internal dict KEY renamed to 'vpp_volts' at :417 + consumers; wire emit key already 'vpp_mv' from Plan 02-01 at :518"

key-files:
  created:
    - .planning/phases/02-naming-cleanup-wire-key-minipro-references/02-02-SUMMARY.md
  modified:
    - firestarter_app/firestarter/data/chip_database.json (RENAMED from minipro_complete_db.json via git mv; content byte-identical per D-16)
    - firestarter_app/firestarter/database.py (:189 reader path + :366 docstring + :417 dict-write key + :510 emitter fallback — 4 sites in one file)
    - firestarter_app/firestarter/eprom_info.py (:271 consumer ic.get('vpp_volts', '-'))
    - firestarter_app/firestarter/ic_layout.py (:516 consumer eprom_data.get('vpp_volts', 'N/A') — staged via index-only partial commit; pre-existing whitespace reformat left unstaged)
    - firestarter_app/tools/build_db.py (:12 OUTPUT_FILE)
    - firestarter_app/tools/check_dispatch.py (:2 docstring + :27 glob default)
    - firestarter_app/pyproject.toml ([tool.setuptools.package-data] rewritten to 3 real shipping files)
    - firestarter_app/MANIFEST.in (rewritten — 11 real include directives; stale database.json + pin-maps.json gone)
    - firestarter_app/CLAUDE.md (:19 data-flow + :36 Key Files + :68 Database Pipeline — 3 single-line filename touches)
    - firestarter/CLAUDE.md (:30 single-line filename touch)
    - CLAUDE.md (meta — :44 single-line filename touch)

key-decisions:
  - "Index-only partial staging for ic_layout.py to isolate the scoped vpp_volts line from a pre-existing co-located black-style reformat. The unstaged reformat carries a load-bearing pre-existing fix (pin_map_details['vpp-pin'] -> pin_map_details['vpp-pin'][0]) that is required for `firestarter info W27C512` to exit 0; that smoke test is the SC#5 acceptance criterion. Keeping the reformat unstaged means the smoke test passes today against the live editable install AND the commit is scoped to only Plan 02-02 work. A future plan should pick up the reformat + pin_map bugfix in its own scoped commit."
  - "All three tasks (02-02-01 rename + path flips, 02-02-02 vpp_volts internal rename, 02-02-03 packaging fix) collapsed into ONE firestarter_app/ sub-repo commit per plan D-13 'naturally atomic' framing. Splitting into siblings would have given no commit-hygiene benefit because all three touch package-data state and the plan explicitly authorises either option."
  - "firmware sub-repo CLAUDE.md edit (:30 only) committed in its own firestarter/ sub-repo commit (8bb85e1), distinct from the application sub-repo commit. The minipro substring at :69 stays UNTOUCHED — Plan 02-03 (CLEAN-02) owns the attribution scrub across both sub-repo CLAUDE.md files (D-14)."
  - "Upstream-schema read at database.py:375 (`electrical.get('vpp', '0').replace('V', '')`) PRESERVED per D-08-compat. RESEARCH.md Pitfall #2 — three different 'vpp' concepts share the same substring; the read at :375 fetches the on-disk DB's '12V' string (emitted by build_db.py:255) and legacy user-override DBs at ~/.firestarter/database.json. Renaming it would break legacy user-override DB loading. The grep gate at line 354 of the plan verifies the upstream-schema read still fires; it does."

patterns-established:
  - "Index-only partial staging recipe (cp worktree -> tmp; checkout HEAD; re-apply scoped edit; git add; restore tmp): captures a single-line edit committed cleanly while leaving out-of-scope co-located edits unstaged. Useful when the working tree carries pre-existing dirt that overlaps with a planned scoped edit and the dirt is load-bearing for verification gates."
  - "Three sub-repo CLEAN-01 commits-per-rename pattern: app sub-repo gets the data-file rename + all callsites + packaging fix in ONE commit (9e61061); firmware sub-repo gets the doc-sync commit (8bb85e1); meta-repo gets the inline-path edit + the two submodule pointer bumps + the SUMMARY in ONE commit (the final metadata commit). Mirrors Plan 02-01's per-sub-repo atomicity convention."

requirements-completed: [CLEAN-01, WIRE-01]
# Note: WIRE-01 was structurally closed by Plan 02-01 (firmware parser + Python wire emitter
# at database.py:518); this plan completes the D-04 "internal twin" portion that CONTEXT.md
# flagged as part of the same wire-protocol coherence story (frontmatter requirement tag).

# Metrics
duration: 5min
completed: 2026-05-12
---

# Phase 02 Plan 02: CLEAN-01 File Rename + D-04 vpp_volts Internal Rename + Packaging Fix Summary

**`minipro_complete_db.json` renamed to `chip_database.json` via `git mv` (blame preserved), all 7 reader/writer/doc callsites flipped atomically, the `_map_data()` internal dict key renamed from `"vpp"` to `"vpp_volts"` with both downstream consumers wired to the new key, and the v1.0 Phase 11 packaging-metadata drift in `pyproject.toml` + `MANIFEST.in` closed — all in one `firestarter_app/` sub-repo commit plus a tiny firmware sub-repo doc-sync commit.**

## Performance

- **Duration:** ~5 min (315 s plan-execution wallclock)
- **Started:** 2026-05-12T08:39:58Z
- **Completed:** 2026-05-12T08:45:13Z
- **Tasks:** 3 / 3 complete (collapsed into 2 sub-repo commits + 1 meta-repo commit per D-13 "naturally atomic" framing)
- **Files modified (in scope, committed):** 11 — 1 renamed, 9 modified across `firestarter_app/`, 1 modified in `firestarter/`, 1 modified in meta-repo
- **Sub-repo commits:** 2 (`firestarter_app`@`9e61061`, `firestarter`@`8bb85e1`)
- **Initial SC#5 smoke:** `pip install -e .` SUCCESS → `firestarter --help` EXIT 0 → `firestarter info W27C512` EXIT 0 (renamed DB resolves; `vpp_volts` flows through `_map_data` → `ic_layout.py:513` + `eprom_info.py:271` without `KeyError`)

## Accomplishments

- **`git mv` preserved blame across the rename.** `git -C firestarter_app log --follow --format='%H' -- firestarter/data/chip_database.json` returns 4 commits (current rename + 3 prior history entries under the old filename) — satisfies D-06 and the plan's `<verify>` block (>= 2 required).
- **Zero `minipro_complete_db` substrings remain in the working tree** across `firestarter_app/`, `firestarter/`, and the meta-repo `CLAUDE.md`. Final grep gate: `grep -rn 'minipro_complete_db' firestarter_app/ firestarter/ CLAUDE.md` returns nothing.
- **D-04 internal `_map_data()` rename closed end-to-end:** dict-write key at `database.py:417` (`"vpp_volts": vpp,`), emitter fallback at `database.py:510` (`int(full_eprom_data.get("vpp_volts", 0) * 1000)`), and both downstream consumers (`eprom_info.py:271` + `ic_layout.py:513`) all read `vpp_volts`. RESEARCH.md "Missed Callsites" inventory is fully discharged.
- **Upstream-schema READ at `database.py:375` PRESERVED** — `electrical.get("vpp", "0").replace("V", "")` is byte-identical to pre-edit state. Regression-proof against accidental "tidying" that would break legacy user-override DBs.
- **v1.0 Phase 11 packaging drift CLOSED:** `pyproject.toml [tool.setuptools.package-data]` and `MANIFEST.in` now declare only files that actually exist in `firestarter_app/firestarter/data/` (`chip_database.json`, `database_overrides.json`, `pinouts.json`). The three stale entries (`database_generated.json`, `pin-maps.json`, `database.json`) are gone. A built wheel from this commit will ship the renamed DB; SC#5 partial discharge confirmed via editable install.
- **Plan 02-01 wire-emit contract still holds:** `grep -nE '"vpp_mv":\s*vpp_mv,' firestarter_app/firestarter/database.py` returns lines `:418` (internal `_map_data` sibling untouched) AND `:518` (wire emit from Plan 02-01 untouched).
- **Out-of-scope items NOT staged:** `firestarter_app/firestarter/__init__.py` version bump (2.0.6 → 2.0.7_dev), `firestarter_app/.planning/codebase/*.md` deletions, and the `ic_layout.py` black/whitespace reformat carrying a `pin_map_details["vpp-pin"][0]` load-bearing bugfix remain unstaged in the working tree. Plan 02-01's SUMMARY documented the same pre-existing dirt; the scoping rule held this plan to its own footprint.

## Task Commits

Each task landed atomically in its sub-repo:

1. **Tasks 02-02-01 + 02-02-02 + 02-02-03 (collapsed per D-13):** atomic `git mv` rename + 7 path callsite flips + 4 `vpp_volts` rename edits + `pyproject.toml` + `MANIFEST.in` rewrites — `firestarter_app@9e61061` (`CLEAN-01: rename minipro_complete_db.json -> chip_database.json (+ D-04 vpp_volts internal rename + packaging fix)`).
2. **Task 02-02-01 firmware-side doc edit:** `firestarter/CLAUDE.md:30` filename flip only (`:69` minipro substring deliberately untouched, Plan 02-03's territory) — `firestarter@8bb85e1` (`docs(02-02): update CLAUDE.md filename reference to chip_database.json`).

**Parent-repo metadata commit** (recorded by the final metadata commit after this SUMMARY lands): meta `CLAUDE.md:44` inline-path edit + both submodule pointer bumps + this SUMMARY.md + STATE.md + ROADMAP.md updates.

## Files Created/Modified

### firestarter_app/ (Python application sub-repo) — commit 9e61061

- `firestarter/data/minipro_complete_db.json` → `firestarter/data/chip_database.json` (renamed via `git mv`; content byte-identical per D-16).
- `firestarter/database.py` — 4 single-line edits:
  - `:189` — `_read_config_file("chip_database.json")` (was `"minipro_complete_db.json"`).
  - `:366` — docstring substring `'chip_database.json'` (was `'minipro_complete_db.json'`).
  - `:417` — `_map_data()` dict-write key `"vpp_volts": vpp,` (was `"vpp": vpp,`). Adjacent `:418` `"vpp_mv": vpp_mv,` line UNCHANGED.
  - `:510` — `convert_to_programmer` fallback now reads `int(full_eprom_data.get("vpp_volts", 0) * 1000)` (was `"vpp"`). Primary `full_eprom_data.get("vpp_mv")` portion and `or` shape preserved.
- `firestarter/eprom_info.py:271` — `ic.get('vpp_volts', '-')` (was `'vpp'`). Surrounding f-string and `if ic.get("type") == 1` shape unchanged.
- `firestarter/ic_layout.py:513` — `eprom_data.get('vpp_volts', 'N/A')` (was `'vpp'`). Surrounding flag-check (`flags & 0x00000008`) unchanged. **Index-only partial stage:** the working-tree file also contains a pre-existing (un-stashed) black-style reformat which remains unstaged. The committed diff is exactly one line.
- `tools/build_db.py:12` — `OUTPUT_FILE = os.path.join(_DATA_DIR, "chip_database.json")`. `MINIPRO_XML_URL` at `:10` deliberately UNTOUCHED (Plan 02-03's territory per D-09).
- `tools/check_dispatch.py:2` (docstring) + `:27` (`_DATA_DIR` glob default) — both flipped to `chip_database.json`. The D-15 augmentation (in-loop wire-key regression asserts) is Plan 02-03's job.
- `pyproject.toml:64-69` — `[tool.setuptools.package-data]` rewritten:
  ```toml
  "firestarter" = [
      "data/chip_database.json",
      "data/database_overrides.json",
      "data/pinouts.json",
  ]
  ```
- `MANIFEST.in` — rewritten to 11 real `include` directives. Stale `firestarter/data/database.json` and `firestarter/data/pin-maps.json` gone; `chip_database.json`, `pinouts.json`, `database_overrides.json`, `avrdude.conf` plus the existing Python-module + README + LICENSE lines all present.
- `CLAUDE.md` — 3 single-line filename touches:
  - `:19` — data-flow ASCII diagram filename token flipped.
  - `:36` — Key Files bullet path flipped (`firestarter/data/chip_database.json`).
  - `:68` — Database Pipeline section filename token flipped. **Minipro attribution words at `:42`, `:69`, `:72` deliberately UNTOUCHED** (Plan 02-03 owns CLEAN-02 attribution scrub).

### firestarter/ (Arduino firmware sub-repo) — commit 8bb85e1

- `CLAUDE.md:30` — `regenerated chip_database.json` (was `regenerated minipro_complete_db.json`). **`minipro` substring at `:69` (protocol_id attribution) UNTOUCHED** — Plan 02-03 owns the attribution scrub.

### meta-repo (firestarter_prom) — will land in this plan's final metadata commit

- `CLAUDE.md:44` — `firestarter_app/firestarter/data/chip_database.json` (was `minipro_complete_db.json`). Single line, single file.
- Two submodule pointer bumps (firestarter → 8bb85e1; firestarter_app → 9e61061) — staged as part of the final metadata commit alongside this SUMMARY.md + STATE.md + ROADMAP.md updates.
- `.planning/phases/02-naming-cleanup-wire-key-minipro-references/02-02-SUMMARY.md` — this file.

## Decisions Made

- **Three tasks collapsed into one application sub-repo commit per D-13 "naturally atomic" framing.** The plan explicitly authorised either one commit or sibling commits; collapsing into one yields cleaner blame ("this commit closes CLEAN-01 + D-04 + packaging-drift in one shot") and the grep gates do not require physical separation.
- **Index-only partial staging for `ic_layout.py`** (`cp worktree → /tmp/backup → git checkout HEAD → re-apply vpp_volts → git add → restore worktree`). Required because the working tree contained a pre-existing co-located black-style reformat that was NOT scoped to Plan 02-02 but which carries a load-bearing `pin_map_details["vpp-pin"][0]` indexing fix necessary for `firestarter info W27C512` to exit 0 (the SC#5 acceptance criterion). Pure file-level `git add` would have committed the reformat; pure stash-then-edit would have failed the SC#5 smoke. The partial-stage recipe gives both clean scoping AND a green smoke test.
- **`firestarter info W27C512` SC#5 smoke executed against the live editable install** (`pip install -e .` ran against the modified `pyproject.toml` first). Build exits 0; `--help` exits 0; `info W27C512` exits 0 with the full DIP-layout + protocol-info output — confirms the renamed DB resolves AND `eprom_info.py:271` + `ic_layout.py:513` are wired to the renamed dict key without `KeyError`. Full SC#5 evidence (including `--adapter`) lives in Plan 02-03.
- **Upstream-schema read at `database.py:375` deliberately left as `electrical.get("vpp", "0").replace("V", "")`.** RESEARCH.md "Pitfall #2: three different vpp concepts" — same substring, different layers. This read fetches the on-disk DB's `"12V"` string (emitted by `build_db.py:255`) and legacy user-override DBs at `~/.firestarter/database.json`; renaming it would break user-override DB loading (D-08-compat). Documented in the commit body as a regression-proof boundary.
- **`MINIPRO_XML_URL` at `tools/build_db.py:10` UNTOUCHED** in this plan per D-09 (it's the surviving load-bearing attribution — the live URL where the upstream XML comes from). Plan 02-03 owns the surrounding comment scrub at `:23`. Confirmed via grep: still present.

## Deviations from Plan

**1. [Rule 1 - Workflow] Index-only partial staging for `firestarter_app/firestarter/ic_layout.py`**

- **Found during:** staging-prep for the Task 02-02-01/02/03 collapsed commit.
- **Issue:** The working tree `ic_layout.py` carried a pre-existing (un-stashed) black-style reformat (~530 lines added/changed) from a prior session, with the vpp_volts edit landing co-located. Naively `git add firestarter/ic_layout.py` would have committed the reformat alongside the scoped edit; stashing the reformat exposed a pre-existing bug (`pin_map_details["vpp-pin"]` is a list, not an int — fix lives in the reformat) that made `firestarter info W27C512` exit non-zero, breaking SC#5.
- **Fix:** Used the index-only partial-stage recipe — back up the working tree file to `/tmp`, `git checkout HEAD -- firestarter/ic_layout.py` to restore a clean baseline, re-apply the single vpp_volts line via Python script, `git add firestarter/ic_layout.py`, then restore the working tree from `/tmp`. Result: index contains exactly the one-line scoped edit (`git diff --cached` shows `2 +1 -1`); working tree retains the load-bearing pre-existing reformat for SC#5 smoke; the pre-existing reformat remains unstaged for a future plan to scope properly.
- **Files modified:** `firestarter_app/firestarter/ic_layout.py` (one line in index; ~530 lines of co-located reformat preserved unstaged in working tree).
- **Commit:** `9e61061` (`firestarter_app` sub-repo; the ic_layout.py portion is exactly the scoped vpp_volts line).

**2. [Rule 3 - Workflow] Stash-and-discard of dropped stash `70060c2` during recipe iteration**

- **Found during:** initial stash attempt to isolate pre-existing dirt.
- **Issue:** `git stash push --keep-index` with file arguments behaved differently than expected (the stash captured working-tree state but file restoration via `pop` had conflict-resolution ambiguities given my partial unstaged edits). After two failed `pop` iterations, the cleanest path was to drop the stash and use the index-only partial-stage recipe directly.
- **Fix:** `git stash drop stash@{0}` to discard the redundant stash entry after the recipe stabilised. The dropped stash content (the ic_layout reformat + __init__ version bump + .planning/codebase/*.md deletions) is preserved in the working tree (unstaged) — `git status --short` will continue to show it for a future scoped plan to pick up.
- **Files modified:** none (stash drop is git-state-only).

No other deviations — plan executed exactly as written. All 7 verification gates passed.

## Issues Encountered / Deferred Items

Pre-existing unrelated dirt in `firestarter_app/` (already documented in Plan 02-01's SUMMARY):

- `firestarter/__init__.py` — version bump `2.0.6` → `2.0.7_dev` from a prior session. Unstaged; out of scope for Plan 02-02.
- `.planning/codebase/*.md` (7 files) — auto-generated codebase snapshot files deleted in working tree from a prior session. Unstaged; out of scope.
- `firestarter/ic_layout.py` — pre-existing black/whitespace reformat (~530 lines) containing a load-bearing `pin_map_details["vpp-pin"][0]` indexing fix. The single vpp_volts line was extracted and committed via index-only partial-stage (see Deviation 1); the bulk of the reformat remains unstaged in the working tree for a future plan to scope properly.

These items are tracked here, NOT auto-fixed (Scope Boundary rule). A future plan should pick them up; the `pin_map_details["vpp-pin"][0]` fix in particular looks load-bearing and merits its own small scoped commit.

## Final Acceptance Gate Results

All 7 gates from plan `<verification>` block + the plan-body grep assertions:

| # | Gate | Expected | Actual | Status |
|---|------|----------|--------|--------|
| 1 | `grep -rn 'minipro_complete_db' firestarter_app/ firestarter/ CLAUDE.md` | zero matches | zero matches | PASS |
| 2 | `test -f firestarter_app/firestarter/data/chip_database.json && ! test -e firestarter_app/firestarter/data/minipro_complete_db.json` | file present, old absent | file present, old absent | PASS |
| 3 | `git -C firestarter_app log --follow --format='%H' -- firestarter/data/chip_database.json \| wc -l` | >= 2 | 4 | PASS |
| 4 | `grep -nE '"vpp_volts":\s*vpp,' firestarter_app/firestarter/database.py` | hits `:417` | hits `:417` | PASS |
| 5 | `grep -nE 'get\("vpp_volts",\s*0\)\s*\*\s*1000' firestarter_app/firestarter/database.py` | hits `:510` | hits `:510` | PASS |
| 6 | `grep -nE "'vpp_volts'" firestarter_app/firestarter/{eprom_info,ic_layout}.py` | >= 2 hits | hits `eprom_info.py:271` + `ic_layout.py:513` | PASS |
| 7 | `grep -nE 'electrical\.get\("vpp",\s*"0"\)' firestarter_app/firestarter/database.py` | hit near `:375` | hits `:375` | PASS |
| 8 | `pip install -e . && firestarter --help && firestarter info W27C512` | all exit 0 | all exit 0 | PASS |
| 9 | Plan 02-01 wire-emit contract at `:518` still `"vpp_mv": vpp_mv,` | unchanged | unchanged (and `:418` sibling preserved) | PASS |

## Next Phase Readiness

- **Plan 02-03 entry contract is met:**
  - The renamed file `firestarter_app/firestarter/data/chip_database.json` is the single source for Plan 02-03's `check_dispatch.py` D-15 augmentation + the full 743-chip scan.
  - The renamed internal dict key `"vpp_volts"` is the in-memory representation Plan 02-03's CLI smoke will exercise.
  - `firestarter info W27C512` exits 0; `firestarter info W27C512 --adapter <pinout>` smoke is owed by Plan 02-03 (full SC#5 discharge).
- **CLEAN-02 territory remains open for Plan 02-03:**
  - `firestarter_app/CLAUDE.md:42, :69, :72` — minipro attribution words in prose.
  - `firestarter/CLAUDE.md:69` — minipro protocol_id authoritative-flow attribution.
  - `firestarter_app/firestarter/database.py:45, :389` — minipro comments.
  - `firestarter_app/tools/check_dispatch.py:23, :30` — minipro comments (the `:23` mirror-comment is the survivor pointing at `build_db.py:11-13`; the `:30` D-10 wording rewrite is Plan 02-03's owned).
  - `firestarter_app/tools/build_db.py:10` — `MINIPRO_XML_URL` constant (the surviving load-bearing attribution per D-09 — name preserved; only surrounding comment may be tidied).
- **WIRE-02 regression evidence** (Plan 02-03 task): augment `check_dispatch.py`'s in-loop assertions with `"vpp_mv" in wire AND "vpp" not in wire` against the renamed DB. Plan 02-02's index-state and the renamed file are the exact inputs.

## Self-Check: PASSED

Verified post-Write, pre-metadata-commit:

- FOUND: `.planning/phases/02-naming-cleanup-wire-key-minipro-references/02-02-SUMMARY.md`
- FOUND: `firestarter_app/firestarter/data/chip_database.json` (renamed; old file absent)
- FOUND: firestarter_app sub-repo commit `9e61061` (`CLEAN-01: rename ... (+ D-04 vpp_volts internal rename + packaging fix)`) — 9 files, 17 insertions, 16 deletions, plus rename
- FOUND: firestarter sub-repo commit `8bb85e1` (`docs(02-02): update CLAUDE.md filename reference to chip_database.json`) — 1 file, 1 insertion, 1 deletion
- FOUND: meta-repo CLAUDE.md:44 edit (staged for final metadata commit)
- All 9 acceptance gates above pass.

---
*Phase: 02-naming-cleanup-wire-key-minipro-references*
*Plan: 02*
*Completed: 2026-05-12*
