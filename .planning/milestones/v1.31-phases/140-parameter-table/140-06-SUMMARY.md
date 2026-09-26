---
phase: 140-parameter-table
plan: 06
subsystem: firmware
tags: [documentation, eprom, protocols, claude-md, citations, table-04, table-01, gh-15]

# Dependency graph
requires:
  - phase: 140-parameter-table (140-05)
    provides: "tests/golden/eprom_params_citations.json — the D-14 machine-readable citation sidecar every corrected claim in this plan points at"
  - phase: 140-parameter-table (140-04)
    provides: "the D-11 native-env exception precedent (native_trace_v131) this plan documents a second instance of (native_params_v131) inside firestarter/CLAUDE.md"
provides:
  - "firestarter/doc/PROTOCOLS.md: a datasheet-path note under '## 1. Real Protocol Buckets' (F-140-08) plus corrected 27C write-algorithm paragraphs and citation lines in §§1.3 (0x07), 1.4 (0x08) and 1.5 (0x0B), each pointing at tests/golden/eprom_params_citations.json"
  - "firestarter/CLAUDE.md: corrected Algorithm Handlers Notes/VPP cells for 0x07/0x08/0x0B plus the D-11 native-env exception appended to the 'Reuse pattern for future native tests' section"
affects: [140-07-requirements-flip, 146-close-reconciliation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Self-describing datasheet citation (vendor, part, document number, revision/date, section/figure) replaces repo-path citations that do not resolve on this branch (F-140-08) — the same form 140-05's sidecar already uses"

key-files:
  created: []
  modified:
    - firestarter/doc/PROTOCOLS.md
    - firestarter/CLAUDE.md

key-decisions:
  - "Preserved every sentence in the §1.4/§1.5 write-algorithm paragraphs not named for removal (the 32-pin address-line note, the INV-03 cross-link, the VPP-pin-varies-by-revision note, the A13-hardwired note) — the plan named specific phrases and citation lines to remove, not a full paragraph rewrite; this is a correction pass, not a docs refactor (critical hazard #8)"
  - "0x0B's VPP cell corrected from '12–18V direct' to '12–25V direct' rather than a wider prose rewrite — the database carries vpp values up to 25V on this row and TI TMS 2516 specifies +25V; 12V is still the floor, so only the ceiling was wrong"
  - "Kept exactly one eprom_params_citations.json pointer per corrected section (not one per sentence) — satisfies the >=4-total / >=1-per-section acceptance criterion without diluting the prose with redundant pointers"

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "doc/PROTOCOLS.md gains a datasheet-path note (§1, F-140-08) and corrected 27C write-algorithm paragraphs + citation lines in §§1.3 (0x07), 1.4 (0x08) and 1.5 (0x0B), each pointing at tests/golden/eprom_params_citations.json"
    requirement: "TABLE-04"
    verification:
      - kind: other
        ref: "grep -c 'eprom_params_citations.json' doc/PROTOCOLS.md -> 4; negative greps for '3× overpulse' / '3 × retry_count' (U+00D7, verified present pre-edit and absent post-edit) / 'Same Intelligent Programming' / 'Programming Algorithm; `datasheets' -> PROTOCOLS_CORRECTED"
        status: pass
      - kind: other
        ref: "git diff (run BEFORE commit) -- doc/PROTOCOLS.md carries '-' lines containing '3× overpulse', '3 × retry_count' and 'Same Intelligent Programming' -> REMOVALS_PROVEN_IN_DIFF (see Removal Proof section below)"
        status: pass
      - kind: unit
        ref: "cd firestarter_app && python3 -m pytest tests/test_dispatch_mirror.py tests/test_fw_presence.py -o addopts=\"\" -q -> 9 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "firestarter/CLAUDE.md Algorithm Handlers rows for 0x07/0x08/0x0B corrected (pulse-width-is-a-database-datum framing, DQ7-not-used-here note, 12-25V VPP, 50ms per-byte energy cap) plus the D-11 native-env exception appended to 'Reuse pattern for future native tests'"
    requirement: "TABLE-01"
    verification:
      - kind: other
        ref: "grep -c 'eprom_params_citations.json' CLAUDE.md -> 3; grep -q native_params_v131 -> found; negative greps for '1ms pulse, DQ7 verify' / '12–18V direct' / '500µs pulse, 24-pin' -> CLAUDE_CORRECTED"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_flash_path_record_sync.py -q -> 41 passed (post-commit; see Issues Encountered for the expected transient pre-commit porcelain failure)"
        status: pass
      - kind: other
        ref: "git diff -- CLAUDE.md | grep -c 'SHARED:S' -> 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both repositories' full pytest suites remain green after the documentation edits, and only the two intended files changed across this plan's two commits"
    verification:
      - kind: other
        ref: "cd firestarter && python3 -m pytest tests/ -q -> 244 passed, 0 failed"
        status: pass
      - kind: other
        ref: "cd firestarter_app && python3 -m pytest tests/ -o addopts=\"\" -q -> 1547 passed, 1 warning (pre-existing Click MultiCommand DeprecationWarning, unrelated to this plan), 0 failed"
        status: pass
      - kind: other
        ref: "git diff --stat HEAD~2 HEAD lists exactly CLAUDE.md and doc/PROTOCOLS.md (80 insertions, 9 deletions); git diff --quiet -- src/ include/ platformio.ini tests/ -> ONLY_DOCS_CHANGED; git diff --quiet HEAD~2 HEAD -- src/proms/eprom.cpp -> EPROM_CPP_UNCHANGED_D10"
        status: pass
    human_judgment: false

duration: ~13min
completed: 2026-08-10
status: complete
---

# Phase 140 Plan 06: Reconcile doc/PROTOCOLS.md and CLAUDE.md with the Shipped Citations Summary

**Removed the false "1 ms pulse × N + 3× overpulse" / "Same Intelligent Programming algorithm" claims and their nonexistent-section citations from `doc/PROTOCOLS.md` §§1.3/1.4/1.5 and the stale "1ms pulse, DQ7 verify" / "12–18V direct" claims from `CLAUDE.md`'s Algorithm Handlers table, replacing all of it with the datasheet-grounded facts 140-05's citation sidecar already ships, plus the D-11 native-env exception CLAUDE.md's own reuse-pattern section was missing.**

## Performance

- **Duration:** ~13 min (approximate — continued directly from the 140-05 session; STATE.md `last_updated` at plan start was `2026-08-10T02:25:20Z`, this plan's second and final task commit landed at `2026-08-10T02:38Z`)
- **Started:** ~2026-08-10T02:25:00Z (approximate)
- **Completed:** 2026-08-10T02:38:16Z
- **Tasks:** 3 (Task 3 was verification-only — see Task Commits)
- **Files modified:** 2 (both planned: `doc/PROTOCOLS.md`, `CLAUDE.md`)

## Accomplishments

- **`doc/PROTOCOLS.md`** (`0a4b659`):
  - Added a note under `## 1. Real Protocol Buckets` stating the `datasheets/<slug>/<file>.pdf` paths cited throughout §1 do not resolve on this branch (F-140-08), naming the `v1.16-protocol-first-architecture-rebuild` recovery branch, the `git show` recovery command, and pointing per-value attribution at `tests/golden/eprom_params_citations.json`.
  - §1.3 (0x07): removed "JEDEC Intelligent Programming (1 ms pulse × N + 3× overpulse) ... apply overpulse = 3 × retry_count pulses" and the nonexistent `W27C512.pdf p.7 §6.2 Programming Algorithm` citation. Replaced with: pulse width is a database datum (modal 100 µs, 113/170 chips; 1000 µs is only the `pulse_delay==0` fallback); no overprogram pulse on this row (Winbond W27C512 Rev A4, ST M27C512 Rev 3 §2.6, Microchip 27C512A DS11173G §1.6); `max_pulses=25`; the named F-140-05 Intel-family (22-chip) divergence recorded as a Phase 146 follow-up; and that the firmware's present loop is retry escalation, not an Intel 3N margin pulse.
  - §1.4 (0x08): removed "Same Intelligent Programming algorithm as 0x07" and its citation. Replaced with: Intel Quick-Pulse / AMD Flashrite / ST PRESTO II family; no overprogram (`overprogram_factor=0`, resolved from ST M27C1001 verbatim + AMD Am27C020 + Winbond W27C020); this both agrees with `PROJECT.md`'s prose and contradicts `PROJECT.md`'s own throughput table (D-06, named not silently fixed); `max_pulses=25`; 100 µs modal (104/127 chips).
  - §1.5 (0x0B): removed "Same Intelligent Programming pulse algorithm" and its citation. Replaced with: TI TMS 2516's single 50 ms pulse per location (`t_w(PR)`=45/50/55 ms), no final full-array pass, no overprogram; the firmware's actual looped pulse-verify with a 50 ms per-byte accumulated-energy cap (D-02); and the F-140-07 correction — recorded, not applied — that the published "100 × 500 µs is the classic 2716 total programming time" justification is wrong (the datasheet's own total for all bits is 100 seconds), naming Phase 146 / CLOSE-04 as the owner of reconciling the posted text.
  - Every other paragraph ("Erase model", "VPP behavior", "Pin roles") and every other section (§0, §2, §3, §§1.1/1.2/1.6-1.12) is byte-unchanged — confirmed by full diff review (see Removal Proof below).
- **`CLAUDE.md`** (`e2e25b5`):
  - Algorithm Handlers `0x07` Notes cell: removed "1ms pulse, DQ7 verify"; replaced with the database-datum pulse-width framing, `verify_mode`, `max_pulses=25`, no-overprogram, and an explicit statement that DQ7 polling is a flash-family mechanism not used on this row.
  - `0x08` Notes cell: removed "100µs pulse"; replaced with the equivalent facts for this row (D-06's three-vendor no-overprogram resolution).
  - `0x0B` VPP cell: corrected "12–18V direct" to "12–25V direct" (the DB carries `vpp` up to 25 V on this row; TI TMS 2516 specifies +25 V). Notes cell: removed "500µs pulse, 24-pin"; replaced with the database-datum framing plus the 50 ms per-byte accumulated-energy cap.
  - Appended a labelled D-11 exception to "Reuse pattern for future native tests": `native_params_v131` is added to **neither** pinned native env, naming all five constraints (not folded into either `test_filter`, not in `default_envs`, not fed to `check_size_baseline.py` — F-138-05 uncaught `KeyError` — nor to `check_build_warnings.py`, and no CI leg of either repository — F-140-11).
  - No `[SHARED:S1]`-`[SHARED:S5]` marker section, Protocol Dispatch section, Hardware Revision Documentation section, or PY32F071 section touched.
- **Both suites confirmed green (Task 3):** firmware `pytest tests/ -q` → **244 passed**, 0 failed; app `pytest tests/ -o addopts="" -q` → **1547 passed**, 1 pre-existing unrelated warning, 0 failed (baseline 1539 + plan 140-03's 8 = 1547, exactly as predicted).
- **D-10 confirmed:** `git diff --quiet HEAD~2 HEAD -- src/proms/eprom.cpp` exits 0 — byte-unchanged.
- **Scope containment confirmed:** `git diff --stat HEAD~2 HEAD` lists exactly two files (`CLAUDE.md`, `doc/PROTOCOLS.md`, 80 insertions / 9 deletions); `git diff --quiet -- src/ include/ platformio.ini tests/` exits 0 (`ONLY_DOCS_CHANGED`).

## Task Commits

Each task was committed atomically inside `firestarter/` (submodule):

1. **Task 1: Correct doc/PROTOCOLS.md 1.3/1.4/1.5 and add the datasheet-path note** — `0a4b659` (fix, firestarter)
2. **Task 2: Correct CLAUDE.md's Algorithm Handlers rows and record the D-11 native-env exception** — `e2e25b5` (fix, firestarter)
3. **Task 3: Prove both repositories' suites are still green after the doc edits** — no additional commit. This task's own `<action>` text is verification-and-recording only (run both suites in full, confirm scope containment) — it names no further edit instruction and no file changed between Task 2's commit and the end of Task 3. This mirrors the 140-04 Task 3 and 140-05 Task 3 precedent (both were also observe-and-record steps with no new commit); named here per this project's "name the divergence" convention rather than silently treating the plan's Task 3 `<files>` tag as producing a commit it does not.

**Plan metadata:** this SUMMARY's own commit (docs: complete plan) — see final commit below.

## Files Created/Modified

- `firestarter/doc/PROTOCOLS.md` (+64/-6 lines) — datasheet-path note under §1; corrected write-algorithm paragraphs and citation lines in §§1.3, 1.4, 1.5.
- `firestarter/CLAUDE.md` (+16/-3 lines) — corrected Algorithm Handlers Notes/VPP cells for 0x07/0x08/0x0B; D-11 exception appended to "Reuse pattern for future native tests".

## Decisions Made

- See `key-decisions` in frontmatter: preserved all non-targeted sentences in the §1.4/§1.5 write-algorithm paragraphs (32-pin address-line note, INV-03 cross-link, VPP-pin-varies-by-revision note, A13-hardwired note) rather than rewriting the paragraphs wholesale; corrected the 0x0B VPP cell's ceiling only (12–18V → 12–25V, floor of 12V was already correct); kept exactly one `eprom_params_citations.json` pointer per corrected section rather than one per sentence.

## Deviations from Plan

None — plan executed exactly as written. All four `doc/PROTOCOLS.md` changes and all four `CLAUDE.md` changes match the plan's `<action>` text; every acceptance criterion in both tasks was verified before committing.

## Issues Encountered

**Expected transient porcelain failure in `test_flash_path_record_sync.py` (not a defect — named in this plan's critical hazard #7):** running `python3 -m pytest tests/test_flash_path_record_sync.py -q` immediately after editing (but before committing) `CLAUDE.md` produced `1 failed, 40 passed` — `test_planted_mutation_of_the_real_subset_is_detected`'s final assertion, `_git_porcelain(_FW_REPO_ROOT) == ""`, correctly detected the uncommitted `M CLAUDE.md` in the working tree. This is the exact whole-repo-cleanliness assertion the plan's own critical hazards section names. Committing `CLAUDE.md` (Task 2's commit, `e2e25b5`) and re-running produced a clean `41 passed` — no code or test change was needed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `doc/PROTOCOLS.md` and `CLAUDE.md` no longer contradict `tests/golden/eprom_params_citations.json` — the repository's own guidance documents agree with the shipped, gate-enforced parameter table.
- The D-11 native-env exception is now recorded in the exact section (`CLAUDE.md` § "Reuse pattern for future native tests") whose "add to both pinned envs" instruction it overrides, for both `native_trace_v131` (Phase 138, not previously recorded in CLAUDE.md) and `native_params_v131` (Phase 140) — a future editor of that section will find the override where they would otherwise be misled by it.
- Per this plan's own `<requirement_completion>` scope, **no requirement checkbox is flipped by this plan** — TABLE-04 spans 140-05/140-06, TABLE-01 spans 140-01/140-04/140-05; only plan 140-07 may flip any `TABLE-*` checkbox in `.planning/REQUIREMENTS.md` or `.planning/ROADMAP.md`. Neither file's checkboxes were touched here.
- The three named divergences this plan surfaced in prose (F-140-05 in §1.3, D-06 in §1.4, F-140-07 in §1.5) are now on record in **two** places — the gate-enforced sidecar (140-05) and the human-readable protocol/CLAUDE docs (this plan) — both pointing at each other, so a future reader hitting either one is routed to the other.
- No blockers for plan 140-07 (the requirement-flip plan) or Phase 146 (CLOSE-03/CLOSE-04, which reconciles the posted gh#15 text and `PROJECT.md`'s throughput table against the corrections this plan recorded but did not apply to either).

---

## Removal Proof (git diff, captured BEFORE commit — critical hazard #2)

Pre-edit baseline (confirms the U+00D7 multiplication-sign trap named in critical hazard #1 — the ASCII-`x` forms match zero hits both before and after edit, which would have made a naive assertion vacuous):

```
$ grep -c '3× overpulse' doc/PROTOCOLS.md        # 1
$ grep -c '3 × retry_count' doc/PROTOCOLS.md     # 1
$ grep -c '3x overpulse' doc/PROTOCOLS.md        # 0
$ grep -c '3 x retry_count' doc/PROTOCOLS.md     # 0
$ grep -c 'Same Intelligent Programming' doc/PROTOCOLS.md   # 2
$ grep -c 'eprom_params_citations.json' doc/PROTOCOLS.md    # 0
```

Post-edit, pre-commit (working tree still uncommitted, as the `git diff` leg requires):

```
$ grep -c 'eprom_params_citations.json' doc/PROTOCOLS.md && ! grep -q '3× overpulse' doc/PROTOCOLS.md \
  && ! grep -q '3 × retry_count' doc/PROTOCOLS.md \
  && ! grep -q 'Programming Algorithm; `datasheets' doc/PROTOCOLS.md \
  && ! grep -q 'Same Intelligent Programming' doc/PROTOCOLS.md && echo PROTOCOLS_CORRECTED
4
PROTOCOLS_CORRECTED

$ git diff -- doc/PROTOCOLS.md | grep -q '^-.*3× overpulse' \
  && git diff -- doc/PROTOCOLS.md | grep -q '^-.*3 × retry_count' \
  && git diff -- doc/PROTOCOLS.md | grep -q '^-.*Same Intelligent Programming' && echo REMOVALS_PROVEN_IN_DIFF
REMOVALS_PROVEN_IN_DIFF

$ grep -c 'v1.16-protocol-first-architecture-rebuild' doc/PROTOCOLS.md
2
```

`git diff --stat -- doc/PROTOCOLS.md` at that same pre-commit moment: `1 file changed, 64 insertions(+), 6 deletions(-)`.

CLAUDE.md's equivalent leg (also grep-based, no git-diff removal-proof required by the plan for this file):

```
$ grep -c 'eprom_params_citations.json' CLAUDE.md && grep -q 'native_params_v131' CLAUDE.md \
  && ! grep -q '1ms pulse, DQ7 verify' CLAUDE.md \
  && ! grep -q '12–18V direct' CLAUDE.md \
  && ! grep -q '500µs pulse, 24-pin' CLAUDE.md && echo CLAUDE_CORRECTED
3
CLAUDE_CORRECTED

$ git diff --stat -- CLAUDE.md
 CLAUDE.md | 19 ++++++++++++---
 1 file changed, 16 insertions(+), 3 deletions(-)

$ git diff -- CLAUDE.md | grep -c 'SHARED:S'
0
```

## Full Suite Results (Task 3)

```
$ cd /workspaces/firestarter && python3 -m pytest tests/ -q
244 passed in ~12s

$ cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts="" -q
1547 passed, 1 warning in 193.92s (0:03:13)
```

The one warning is a pre-existing `DeprecationWarning` on `click.MultiCommand` in
`tests/test_click_group_gate_hook.py`, unrelated to this plan's documentation-only changes.

Scope-containment and D-10 legs, run after both task commits:

```
$ git status --porcelain
(empty)

$ git diff --stat HEAD~2 HEAD
 CLAUDE.md        | 19 ++++++++++++---
 doc/PROTOCOLS.md | 70 +++++++++++++++++++++++++++++++++++++++++++++++++++-----
 2 files changed, 80 insertions(+), 9 deletions(-)

$ git diff --quiet -- src/ include/ platformio.ini tests/ && echo ONLY_DOCS_CHANGED
ONLY_DOCS_CHANGED

$ git diff --quiet HEAD~2 HEAD -- src/proms/eprom.cpp && echo EPROM_CPP_UNCHANGED_D10
EPROM_CPP_UNCHANGED_D10
```

---

*Phase: 140-parameter-table*
*Completed: 2026-08-10*

## Self-Check: PASSED

Files verified present on disk:
- FOUND: `firestarter/doc/PROTOCOLS.md`
- FOUND: `firestarter/CLAUDE.md`
- FOUND: `.planning/phases/140-parameter-table/140-06-SUMMARY.md`

Commits verified present in git history (firestarter):
- FOUND: `0a4b659` (fix: correct doc/PROTOCOLS.md 27C write-algorithm claims)
- FOUND: `e2e25b5` (fix: correct CLAUDE.md Algorithm Handlers rows + record D-11 exception)
