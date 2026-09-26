---
phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation
plan: 07
subsystem: docs
tags: [documentation, codegen, catalog, readme, cli, click, honesty-ledger, close-03]

# Dependency graph
requires:
  - phase: 146-02
    provides: 146-check-close03-docs.py (RED half) and 146-DOC-CHECK-RECORD.md §§1-4
  - phase: 146-06
    provides: firmware-doc GREEN (146-DOC-CHECK-RECORD.md §7), catalog/messages.h/messages.py baseline
provides:
  - firestarter_app/README.md completing the shipped write-option surface (--no-blank-check, --skip-erase, --vpe-as-vpp, --pulse-us, --skip-sdp-unlock), with the two adjacency defects (A-1, A-2) corrected
  - The database-supplied per-byte pulse-delay and the ~6.25 V program-VCC ceiling documented in the host README
  - DBG_PULSE_DELAY_MISMATCH catalog wording corrected (canonical + both sub-repo copies + regenerated messages.py) to match the shipped fixed-width per-byte loop, id/name/params unchanged
  - 146-check-close03-docs.py GREEN (rc=0) across all four CLOSE-03 documentation targets, with its failure capability re-shown in the same session
  - 146-DOC-CHECK-RECORD.md §8
affects: [146-11, 146-12, 146-13]

# Tech tracking
tech-stack:
  added: []
  patterns: ["catalog-source-of-truth: edit tools/catalog/messages.toml only, sync_to_subrepos.sh propagates + regenerates, pre-commit numstat is the evidence not the script's self-comparing confirmation lines"]

key-files:
  created: []
  modified:
    - firestarter_app/README.md
    - tools/catalog/messages.toml
    - firestarter/tools/catalog/messages.toml
    - firestarter_app/tools/catalog/messages.toml
    - firestarter_app/firestarter/messages.py
    - .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-DOC-CHECK-RECORD.md

key-decisions:
  - "DBG_PULSE_DELAY_MISMATCH format string replaced with 'Pulse delay mismatch: expected %d, got %d' — neutral wording that does not claim an adaptive retry-escalation loop the shipped per-byte loop does not run; id (0x15), name and the two-u8 param list left byte-identical."
  - "MSG_INFO_RETRIES (0x51) left byte-unchanged per 141-LOOP-RECORD.md §6 — orphaned, recorded not repaired."
  - "firestarter's regen commit carries only the catalog copy (messages.h diff is genuinely zero lines); firestarter_app's commit carries both the catalog copy and the regenerated messages.py."
  - "Database-supplied-pulse user text extends the existing EEPROM-configuration section (pulse-delay override) rather than duplicating it, per the plan's read_first guidance."

requirements-completed: []

coverage:
  - id: D1
    description: "firestarter_app/README.md documents the complete shipped write() option surface (--no-blank-check, --skip-erase, --force, --address, --vpe-as-vpp, --pulse-us, --skip-sdp-unlock) with both adjacency defects (stale --ignore-blank-check name, erase-skip misattribution) corrected"
    requirement: "CLOSE-03"
    verification:
      - kind: other
        ref: "grep -q for each of --no-blank-check/--skip-erase/--vpe-as-vpp/--skip-sdp-unlock/--pulse-us in firestarter_app/README.md, and grep -c -- '--ignore-blank-check' == 0"
        status: pass
    human_judgment: true
    rationale: "Presence of the option spellings is grep-verified, but whether the prose correctly and completely describes each option's behavior is plan 146-12's blocking operator wording review, not something this plan's automated checks can certify."
  - id: D2
    description: "firestarter_app/README.md documents the database-supplied per-byte pulse-delay and the ~6.25 V program-VCC ceiling"
    requirement: "CLOSE-03"
    verification:
      - kind: other
        ref: "grep -c '6\\.25' firestarter_app/README.md >= 1 and grep -oiE '\\bpro[v]en\\b' == 0"
        status: pass
    human_judgment: true
    rationale: "146-check-close03-docs.py's topic patterns are presence tests only (module docstring's explicit non-claim); correctness of the wording is plan 146-12's job."
  - id: D3
    description: "DBG_PULSE_DELAY_MISMATCH wording corrected through the canonical catalog, propagated to both sub-repo copies at one sha256 digest, and regenerated with a zero-line messages.h diff and a one-line messages.py diff at the format line, captured before any commit"
    requirement: null
    verification:
      - kind: other
        ref: "pre-commit numstat: tools/catalog/messages.toml 1/1, firestarter/include/messages.h empty (0 lines), firestarter_app/firestarter/messages.py 1/1; sha256sum of all three catalog copies identical"
        status: pass
    human_judgment: false
  - id: D4
    description: "146-check-close03-docs.py exits 0 with no argv/no env override, naming all four CLOSE-03 documentation targets, with its failure capability re-shown (emptied seam, missing-path seam) in the same session, and §8 appended to 146-DOC-CHECK-RECORD.md"
    requirement: "CLOSE-03"
    verification:
      - kind: other
        ref: "python3 146-check-close03-docs.py -> rc=0, PASS: line naming all 4 files; FIRESTARTER_DOCSCAN_TARGETS_146=\"\" -> rc=1, 0 PASS lines; missing-path seam -> rc=1 naming path; grep -c '^## 8\\.' 146-DOC-CHECK-RECORD.md == 1"
        status: pass
    human_judgment: false

# Metrics
duration: ~30min
completed: 2026-08-17
status: complete
---

# Phase 146 Plan 07: CLOSE-03 Host Docs + Catalog Wording + Doc-Checker GREEN Summary

**Completed CLOSE-03's host half in firestarter_app/README.md (full write-option surface, two adjacency corrections, DB-pulse and 6.25 V ceiling text), corrected DBG_PULSE_DELAY_MISMATCH's stale wording through the catalog with a pre-commit-verified regen shape, and flipped 146-check-close03-docs.py from RED to GREEN across all four sub-repo targets.**

## Performance

- **Duration:** ~30 min
- **Tasks:** 3 completed
- **Files modified:** 6 (1 host doc, 3 catalog copies, 1 regenerated host module, 1 phase record)
- **Commits:** 5 (4 task commits across 3 repositories; one further metadata commit for STATE/ROADMAP follows this SUMMARY commit)

## Accomplishments

- `firestarter_app/README.md`'s `write` options list now matches the shipped `cli_handlers.py` surface exactly: corrected `-b`'s long name (`--no-blank-check`, not the stale `--ignore-blank-check`), split erase-skipping into its own `--skip-erase` option carrying the un-erased-bits warning verbatim in substance, and added `--vpe-as-vpp`, `--pulse-us` and `--skip-sdp-unlock`. Description steps 1-2 corrected to match.
- Added the database-supplied per-byte pulse-delay explanation (extending the existing EEPROM-configuration section) and a program-VCC ceiling paragraph (~6.25 V, hardware-bound, timing/pulse-count/verify fidelity not silicon-margin fidelity) to the host README.
- `DBG_PULSE_DELAY_MISMATCH`'s format string corrected from "Mismatch, retrying with increased pulse delay from %d to %d" (describes a deleted adaptive retry-escalation loop) to "Pulse delay mismatch: expected %d, got %d" — id, name and the two-`u8` param list unchanged; the orphaned `MSG_INFO_RETRIES` (0x51) left byte-unchanged. Propagated via `sync_to_subrepos.sh` to all three catalog copies (one sha256 digest) and regenerated: `firestarter/include/messages.h` took a zero-line diff (identifier-only), `firestarter_app/firestarter/messages.py` took exactly one changed line (the format string), both captured pre-commit.
- `146-check-close03-docs.py` now exits `rc=0` with no argv and no env override, printing a `PASS:` line naming all four scanned targets (`firestarter/doc/PROTOCOLS.md`, `firestarter/CLAUDE.md`, `firestarter/README.md`, `firestarter_app/README.md`). Both non-vacuity legs (emptied seam, missing-path seam) re-run and confirmed still failing in this session. `146-DOC-CHECK-RECORD.md` §8 records all of it; §§1-7 untouched (diff is 107 insertions, 0 deletions).
- Both sub-repo suites run after committing: `firestarter` 314 passed in 14.51s (matches `146-06`'s recorded baseline exactly), `firestarter_app` 1590 passed + 1 warning + 30 snapshots passed in 232.46s (no prior `146-CITATIONS.md` §0 host-suite baseline existed; recorded here as that baseline).

## Task Commits

Each task was committed atomically, per repository:

1. **Task 1: Host README write-surface + adjacency corrections** — `eca71b2` (docs, inside `firestarter_app`)
2. **Task 2: Catalog wording correction + regen** — three commits, one per repository:
   - `firestarter`: `f8ac643` (docs — catalog copy only; `messages.h` diff was genuinely zero lines)
   - `firestarter_app`: `3cf429f` (docs — catalog copy + regenerated `messages.py`)
   - meta: `878e60dc` (docs — canonical catalog)
3. **Task 3: Doc-checker GREEN + §8** — `8584d96c` (docs, meta — `146-DOC-CHECK-RECORD.md` only)

**Plan metadata commit:** pending (STATE.md + ROADMAP.md, hand-edited, separate final commit per the state_and_roadmap_protocol).

## Files Created/Modified

- `firestarter_app/README.md` — write options list brought to shipped surface; two adjacency defects (A-1, A-2) corrected; database-supplied pulse and 6.25 V ceiling text added.
- `tools/catalog/messages.toml` (canonical) — `DBG_PULSE_DELAY_MISMATCH` format string corrected.
- `firestarter/tools/catalog/messages.toml`, `firestarter_app/tools/catalog/messages.toml` — synced copies of the above (byte-identical to canonical).
- `firestarter_app/firestarter/messages.py` — regenerated; exactly one changed line (the format string at line 1072).
- `firestarter/include/messages.h` — regenerated; zero-line diff (not committed as a change since nothing changed).
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-DOC-CHECK-RECORD.md` — §8 appended.

## Decisions Made

- Replacement wording for `DBG_PULSE_DELAY_MISMATCH` chosen as neutral fact-description ("Pulse delay mismatch: expected %d, got %d") rather than any wording implying the retry-escalation behavior the pre-Phase-141 loop had — matches the register's C-7 instruction ("wording fix, not behaviour") without inventing new claims about what the (currently unreferenced) id would report if it were ever wired up again.
- Extended the existing EEPROM-configuration section for the database-supplied-pulse topic rather than duplicating it in the Write section, per the plan's `read_first` guidance pointing at that section as the style donor.
- Committed the firmware regen as catalog-only (no `messages.h` change to stage) rather than treating the zero-line diff as an error — this is the plan's own predicted and required shape.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' acceptance criteria were met on the numbers measured (see verification output below), no Rule 4 architectural questions arose, and no auto-fixes were needed under Rules 1-3.

## Issues Encountered

None.

## Verification Evidence (measured, not predicted)

**Task 1:**
- `--no-blank-check`, `--skip-erase`, `--vpe-as-vpp`, `--skip-sdp-unlock`, `--pulse-us` all present; `--ignore-blank-check` count = 0.
- `6.25` count = 1; `\bpro[v]en\b` count = 0.
- Commit `eca71b2` inside `firestarter_app` on branch `gsd/v1.31-27c-programming-algorithm-fidelity`; file list = README.md only; source/tool/test/packaging numstat empty. Host porcelain: 7 before, 7 after (untouched pre-existing untracked paths).

**Task 2:**
- Canonical catalog `git diff -U0`: exactly 2 changed lines (1 removed, 1 added), both the format line.
- Pre-commit numstat: `tools/catalog/messages.toml` 1/1; `firestarter/include/messages.h` empty (0 lines); `firestarter_app/firestarter/messages.py` 1/1 (hunk confirmed as the format line at 1072).
- sha256 of all three catalog copies: `cd5a0bb99a74d4f701248cb5cabb527a92187691e16f4f5d36c23e69e5855ffa` (1 distinct digest).
- Stale format string count in canonical catalog: 0. Orphaned `MSG_INFO_RETRIES` count: 1 (present, unedited).
- Ahead-counts after: meta 264 (baseline ≥233), `firestarter` 63 (baseline ≥61), `firestarter_app` 18 (baseline ≥16). All rose, none fell — no push.

**Task 3:**
- `python3 146-check-close03-docs.py` (no argv, no seam): `rc=0`, `PASS:` line naming all 4 targets.
- `FIRESTARTER_DOCSCAN_TARGETS_146=""`: `rc=1`, 0 `PASS:` lines.
- `FIRESTARTER_DOCSCAN_TARGETS_146` naming one real + one nonexistent path: `rc=1`, missing path named.
- `146-check-close03-docs.py` byte-unchanged (empty `git status --porcelain` for that file).
- `firestarter` suite: 314 passed in 14.51s, rc=0 (matches `146-06` baseline of 314 exactly).
- `firestarter_app` suite: 1590 passed, 1 warning, 30 snapshots passed, in 232.46s, rc=0.
- Sub-repo porcelains before and after both suites: `firestarter` 0/0, `firestarter_app` 7/7.
- `146-DOC-CHECK-RECORD.md` §8 added: `grep -c '^## 8\.'` = 1; diff = 107 insertions, 0 deletions (§§1-7 untouched).

## Submodule pointer / ahead-count table

| Item | Before this plan | After this plan |
|---|---|---|
| `firestarter` submodule tip | `f82479b` | `f8ac643` |
| `firestarter` inner porcelain | 0 | 0 |
| `firestarter` upstream-ahead | 62 | 63 |
| `firestarter_app` inner porcelain | 7 | 7 (untouched) |
| `firestarter_app` upstream-ahead | 16 | 18 |
| meta upstream-ahead | 263 | 264 (pending +1 for this SUMMARY commit and +1 for the STATE/ROADMAP commit) |

Meta submodule *pointers* (`.gitignore`-tracked `firestarter` / `firestarter_app` gitlink entries) are left untouched per the hard prohibitions — 146-13 owns the re-pin decision.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- CLOSE-03's five documentation topics are now present across all four sub-repo documentation targets; the checker that gates this is GREEN and its failure capability has been re-demonstrated.
- The remaining CLOSE-03 judgment work (whether the prose is *correct*, not merely present) is explicitly deferred to plan 146-12's blocking operator wording review — this plan does not claim that review is discharged.
- CLOSE-03 itself remains unticked, as required — only plan 146-13 may tick any `CLOSE-*` requirement.
- No blockers for downstream plans identified.

## Self-Check: PASSED

All claimed created/modified files exist on disk and all cited commit hashes (across meta, `firestarter`
and `firestarter_app`) resolve in `git log --oneline --all`. No missing items.

---
*Phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation*
*Completed: 2026-08-17*
