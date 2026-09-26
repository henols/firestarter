---
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
plan: "06"
subsystem: infra
tags: [platformio, pytest, size-baseline, ci-gates, jsmn, avr-objdump, measurement, landing-record]

# Dependency graph
requires:
  - phase: 158-01
    provides: "158-before-figures.md -- the pre-phase cold ledger, the default-mode RED shape and the --rebuild exit-1 shape both flips in this record are checked against"
  - phase: 158-02
    provides: "jsmntok_t narrowed to 6 B, ARM built on both sides -- the post-LAND-05 cold position this record's ledger re-measures"
  - phase: 158-03
    provides: "LAND-06 decline record (measured mask cost, witnessed division sites, enumerated coverage gap) -- transcribed here since the mask exists in no committed tree"
  - phase: 158-04
    provides: "size_baseline.json re-recorded, *_v158* severance -- the committed fixtures this record's cold rebuilds are proven byte-identical against"
  - phase: 158-05
    provides: "BASE-01's native inventory axis fixed 141->184, both docstrings corrected, floors raised 8/31 -- the state this record's --rebuild flip and LEG 11 confirm"
provides:
  - "158-after-figures.md: all twelve phase-gate legs re-run on the final committed tree (firestarter 2ccda8d), each with its expected shape stated in advance"
  - "Both polarity flips (default mode RED->GREEN; --policy merge05 --rebuild exit1->exit0) recorded with before and after shapes side by side"
  - "LAND-04, LAND-06, LAND-07, LAND-08 discharged by this record alone (no code change for any of the four)"
  - "All thirteen corrections (C-1..C-13) and all ten decisions (OD-1..OD-10) closed out with verdicts"
  - "Per-requirement discharge attribution and the three scope-correction figures handed to plan 07; citation line-shifts and gitlink sha pairs handed to Phase 159"
affects: ["158-07 (ROADMAP/REQUIREMENTS scope-correction, the only remaining plan of this phase)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Phase-gate landing record: every one of the twelve legs re-measured on the final tree, with the expected shape stated before the run, never merely re-stated from an earlier plan's SUMMARY except where the artifact (a masked probe) no longer exists in any tree"
    - "Polarity-flip discharge: a RED-to-GREEN or exit1-to-exit0 flip is only evidence when both shapes are quoted in the same document"

key-files:
  created:
    - .planning/v1.33/158-after-figures.md
  modified: []

key-decisions:
  - "LAND-06's mask-cost figures (+22/+24/+22 B, the two __udivmodsi4 sites before/after) were transcribed from plan 03's SUMMARY rather than re-derived, per this plan's own carve-out: the mask exists only inside a torn-down worktree and cannot be re-created on the final tree without re-running a discarded worktree. The two probes that ARE re-derivable on the shipped tree (2 __udivmodsi4 calls still present inside flash_5v_page_write_execute; jsmntok_t sizeof 6 B on AVR) were re-run this session and confirmed identical to the historical figures."
  - "LAND-07's token-arithmetic script (/tmp/gsd-158/land07_tokens.py, surviving from plan 01's session in the same container) was re-run rather than transcribed, since pinouts.json and chip_database.json are unaffected by any Phase 158 code change and the re-run costs nothing; it reproduced 50/14, 51/13, 55/9 exactly."
  - "check_build_warnings.py's bare invocation (no args) again exits 1 via its own never-vacuous guard, exactly as 158-before-figures.md already documented -- recorded as the actual observed behavior for both the bare and the --log-qualified invocation, rather than treating the plan's own verify-block assumption of a bare exit-0 as ground truth."

requirements-completed: [LAND-01, LAND-02, LAND-03, LAND-04, LAND-05, LAND-06, LAND-07, LAND-08]

# Coverage metadata
coverage:
  - id: D1
    description: "All twelve phase-gate legs re-run on the final committed tree (firestarter 2ccda8d), each with command, exit status and salient output recorded, and CI-invoked vs local-run-obligation marked"
    verification:
      - kind: other
        ref: "158-after-figures.md S11 (the gate ledger); LEG 1 cold builds byte-identical to captured_build_v158_*.log; LEG 2/3 pio test both 184/184/17; LEG 4/5 check_build_warnings.py/check_no_heap_or_64bit_symbols.py exit 0 (qualified invocation); LEG 6/7/8 check_size_baseline.py PASS; LEG 9 pytest tests/ 360 passed 0 skipped; LEG 10 host suite 1976 passed; LEG 11 12 passed across the two named modules; LEG 12 lines 697/709 quoted, checker byte-unchanged"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both polarity flips (default mode RED->GREEN for LAND-01; --policy merge05 --rebuild exit1->exit0 for LAND-03) recorded with the before shape quoted from 158-before-figures.md and the after shape quoted from this session's own run, in the same document"
    requirement: "LAND-01"
    verification:
      - kind: other
        ref: "158-after-figures.md S3 (LAND-01 flip) and S5 (LAND-03 flip)"
        status: pass
    human_judgment: false
  - id: D3
    description: "LAND-04, LAND-06, LAND-07, LAND-08 discharged as record-only criteria, each with a named section carrying a reproducible command and its exact output"
    verification:
      - kind: other
        ref: "158-after-figures.md S6 (LAND-04, both clauses w/ grep+line-number evidence), S8 (LAND-06, measured cost + witnessed divisions + enumerated gap + disconnection paragraph), S9 (LAND-07, three re-derived bounds), S10 (LAND-08, the data-point corpus)"
        status: pass
    human_judgment: false
  - id: D4
    description: "All thirteen corrections C-1 through C-13 closed out with a verdict, and all ten decisions OD-1 through OD-10 recorded with their declined alternative's cost"
    verification:
      - kind: other
        ref: "158-after-figures.md S13 (13 correction rows, mechanically counted) and S14 (10 OD bullets, mechanically counted)"
        status: pass
    human_judgment: false
  - id: D5
    description: "ROADMAP.md, REQUIREMENTS.md, STATE.md and CITATIONS-STALE.md left byte-unchanged by this plan; the firestarter gitlink not staged or re-pinned; the after-figures record is a single-path commit"
    verification:
      - kind: other
        ref: "git diff --quiet HEAD -- .planning/ROADMAP.md .planning/REQUIREMENTS.md .planning/v1.33/CITATIONS-STALE.md .planning/STATE.md (empty, checked before and after the commit); git show --stat --name-only --format= HEAD lists exactly one path"
        status: pass
    human_judgment: false

# Metrics
duration: ~55min
completed: 2026-08-24
status: complete
---

# Phase 158 Plan 06: The landing record -- all twelve gate legs, both polarity flips, thirteen corrections Summary

**All twelve phase-gate legs re-run on the final committed tree (`firestarter` `2ccda8d`) and written into `.planning/v1.33/158-after-figures.md`: both polarity flips (default mode RED->GREEN, `--policy merge05 --rebuild` exit1->exit0) recorded with before and after shapes side by side, LAND-04/06/07/08 discharged by the record alone, and all thirteen corrections plus ten decisions closed out with verdicts.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-24T10:49:00Z
- **Completed:** 2026-08-24T11:02:00Z
- **Tasks:** 2 (Task 1 measurement-only, no commit; Task 2 the single-path commit)
- **Files modified:** 1 (`.planning/v1.33/158-after-figures.md`, net-new)

## Accomplishments

- Confirmed `git -C firestarter status --porcelain` empty and the exact six-commit distribution
  the plan predicted (two from plan 02, one from plan 04, three from plan 05; none from plans 01,
  03 or 06). `FW_POST_SHA` = `2ccda8d43c8161a34fb5f83b9ab12c37a443bf22`. Meta HEAD before this
  plan's own commit: `0e1dbaa1ce65736412a05584f31715f645b0acfb`.
- Re-ran three cold `pio run` builds (`rm -rf .pio/build/<env>` + one `pio run -e <env>` each):
  zero `warning:` lines each, and both `Flash:`/`RAM:` figures byte-identical to the committed
  `captured_build_v158_{uno,uno328pb,leonardo}.log` fixtures (`COLD-MATCHES-FIXTURES` confirmed
  mechanically). Composed cold-to-cold delta against `158-before-figures.md` S2: `-138/-138/-136 B`
  flash, `-128 B` RAM on all three targets, attributed entirely to LAND-05. Leonardo's final
  Caterina headroom against `28672`: **3574 B** (up from `3438 B` pre-LAND-05, correction C-13).
- Ran `pio test -e native` and `-e native_nodevtools`: both `184 test cases: 184 succeeded`,
  17 suites, matching `size_baseline.json`'s recorded value exactly. No D-04 re-run needed (no
  case-count mismatch this session).
- Ran the qualified `check_build_warnings.py --log ...` (exit 0, `PASS: uno/uno328pb/leonardo:
  macro_redefinition=0`) and `check_no_heap_or_64bit_symbols.py` (exit 0, `PASS: heap=0,64bit=0,
  anchors=2/2` all three targets). Recorded the bare invocation's actual exit-1 behavior (its own
  never-vacuous guard) alongside the qualified invocation's exit-0 result, per the honesty
  convention `158-before-figures.md` already established.
- Ran the canonical `--policy merge05 --avr-log` invocation (exit 0, three negative flash deltas
  `-1872/-1874/-1808` against positive allowances `788/788/724`, three negative RAM deltas `-139`
  against a `2` B tolerance) -- LAND-02's one-sidedness evidence, captured verbatim.
- Ran the canonical `--policy merge05 --rebuild` invocation: **exit 0**, full `PASS:` line covering
  all three AVR targets plus both native envs -- the LAND-03 polarity flip, recorded alongside
  `158-before-figures.md` S4's own exit-1 shape (`native: cases baseline=141 observed=184` x2, zero
  AVR lines).
- Ran default mode against the live `size_baseline.json`: **exit 0**, full `PASS:` line -- the
  LAND-01 polarity flip, recorded alongside `158-before-figures.md` S4's own 8-line RED shape.
- Ran `pytest tests/ -q -o addopts=""` from `/workspaces/firestarter`: **360 passed, 0 skipped**
  (pre-phase 355 + plan 02's 5 new legs, reconciled exactly). Ran the host suite from
  `/workspaces/firestarter_app` on the committed firmware tree (after deleting any `.rej`/`.orig`
  file, of which there were none): **1976 passed, 1 warning, 32 snapshots, 249.17s, 0 skipped**.
- Ran the source-contract module (`tests/test_jsmn_token_layout_source_contract_v158.py`, 5 passed)
  and the convention module (`tests/test_checker_convention.py`, 7 passed) by name -- 12 total.
- Quoted `scripts/check_size_baseline.py` lines `697`/`709` verbatim and proved the whole checker
  source byte-unchanged across the entire phase (`git diff 785e644 HEAD -- scripts/
  check_size_baseline.py` empty), pinning all six MERGE-05 literals.
- Re-derived, on the final tree, the two figures the plan forbids transcribing: `avr-nm`+
  `avr-objdump` symbol-range disassembly confirmed **2** `__udivmodsi4` calls still present inside
  `flash_5v_page_write_execute` on the shipped `uno` ELF (LAND-06 was declined, so they must be
  present -- confirmed); a `sizeof(jsmntok_t)` probe compiled directly against the real,
  committed `lib/jsmn/src/jsmn.h` confirmed **6 B** on AVR (`avr-gcc -mmcu=atmega328p -Os`) and
  **12 B** on the native host toolchain, both matching the historical figures exactly.
- Re-ran the LAND-07 token-arithmetic script (`/tmp/gsd-158/land07_tokens.py`, surviving from plan
  01's session): reproduced `50/14`, `51/13`, `55/9` exactly, refuting the criterion's `57`/`7`.
- Wrote `.planning/v1.33/158-after-figures.md` (16 numbered `##` sections, 13 correction rows,
  10 OD decision bullets, all mechanically counted) and committed it as a single-path commit
  (`b0ee57cd`, meta repo), leaving `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md` and
  `.planning/v1.33/CITATIONS-STALE.md` byte-unchanged, with nothing staged and the `firestarter`
  gitlink untouched.

## Task Commits

1. **Task 1: Run the full phase-gate ledger on the final committed tree** -- no commit
   (measurement-only task; logs land under `/tmp/gsd-158/land/`, no tracked file touched)
2. **Task 2: Write and commit the after-figures record** -- `b0ee57cd` (docs, meta repo)

## Files Created/Modified

- `.planning/v1.33/158-after-figures.md` -- the phase's landing record: git anchors, the phase
  ledger COLD before/after, per-requirement sections for LAND-01 through LAND-08 (each carrying
  its own evidence), the full twelve-leg gate ledger, the coverage ceilings in final form, the
  thirteen-row corrections ledger, the ten decisions, handoffs to plan 07 and to Phase 159, and a
  self-verification section naming the re-derivation command for every figure.

## Decisions Made

- LAND-06's mask-cost figures were transcribed from plan 03's SUMMARY (the mask exists in no
  committed tree and re-creating it would mean re-running a discarded worktree, which this plan's
  own prohibitions treat as the exempted case) -- while the two probes that ARE re-derivable on the
  shipped tree (the `__udivmodsi4` call-site count, the `sizeof` probe) were re-run this session and
  confirmed identical.
- LAND-07's token-arithmetic script was re-run rather than transcribed, since its inputs
  (`pinouts.json`, `chip_database.json`) are unaffected by any Phase 158 code change and the
  re-run cost nothing; the reproduced figures (50/14, 51/13, 55/9) match `158-before-figures.md`
  exactly, confirming no drift occurred between plan 01's measurement and this plan's own.
- Recorded `check_build_warnings.py`'s bare-invocation exit-1 behavior honestly (its own
  never-vacuous guard) rather than forcing the plan's own verify-block assumption of exit 0 to
  appear true -- matching the precedent `158-before-figures.md` already set for the identical
  discrepancy.

## Deviations from Plan

### Recorded discrepancy (honesty convention, not a deviation)

**The plan's own automated `<verify>` block for Task 1 assumes `python3 scripts/
check_build_warnings.py` (bare, no arguments) exits 0.** As already documented in
`158-before-figures.md` (plan 01) and reconfirmed identically this session, the bare invocation
exits **1** via the script's own documented never-vacuous guard (`FAIL: no envs examined -- supply
--log ENV=PATH or --rebuild`), because a bare invocation supplies neither `--log` nor `--rebuild`
and therefore examines zero envs by construction. The qualified invocation
(`--log uno=... --log uno328pb=... --log leonardo=...`, fed this session's own cold logs) exits 0
with `PASS: uno/uno328pb/leonardo: macro_redefinition=0`. Both behaviors are recorded in
`158-after-figures.md` S11 (LEG 4) rather than silently forcing the plan's original assumption to
appear true. This is a plan-authoring gap already known from plan 01, not a new firmware or
checker defect, and it does not affect LAND-04's discharge (which rests on the `.github/` grep and
the `build.yml:161` line number, both independently confirmed).

---

**Total deviations:** 0 auto-fixed; 1 honesty-convention discrepancy recorded (no code change,
matching an already-known and already-documented discrepancy from plan 01).
**Impact on plan:** None -- LAND-04's discharge is unaffected; the record states the actual
observed behavior for both invocations.

## Issues Encountered

- The host suite (`pytest tests/` from `/workspaces/firestarter_app`) took ~249 s to complete and
  was run in the background to avoid the foreground 120 s command timeout; its result (1976
  passed, 0 skipped) was confirmed via the redirected log file once the background task completed.
  No functional issue -- consistent with `157-after-figures.md`'s own recorded runtime for the same
  suite (234.89 s).

## User Setup Required

None -- no external service configuration required. No packages were installed (zero npm/pip/
cargo/apt invocations this plan).

## Next Phase Readiness

- Plan 07 (the only remaining plan of this phase) has, from `158-after-figures.md` S15: the
  per-requirement discharge attribution naming which plan discharged each of LAND-01 through
  LAND-08 and which record section holds its evidence; the three ROADMAP/REQUIREMENTS figures to
  scope-correct in place with their correction ids (`172`->`184` C-1; flat `+22 B`->`+22/+24/+22 B`
  C-3; `57`/`7`->`50/14, 51/13, 55/9` C-4/C-5); the `**Measured**` line's figures
  (`-138/-138/-136 B` flash, `-128 B` RAM, attributed to LAND-05); the ARM outcome verbatim
  ("verified locally... both the pre-narrowing and post-narrowing `py32f071` builds succeeded");
  and the FLOOR carry-forward closure trailing note.
- Phase 159 has, from the same section: the citation line-shifts this phase introduced by file
  (`jsmn.h` +11, `test_check_size_baseline.py` +6, `test_checker_convention.py` +8,
  `meta_presence.py` +2, both baseline JSONs +1 each); the untouched close-blocking
  `CITATIONS-STALE.md` marker; both gitlink sha pairs with the `git commit -- <path>` pathspec
  trap named.
- `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/v1.33/CITATIONS-STALE.md` and
  `.planning/STATE.md` are byte-unchanged by this plan (confirmed via `git diff --quiet HEAD --
  ...` before and after the commit); the `firestarter` gitlink remains drifted and untouched.
- No blockers.

---
*Phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only*
*Completed: 2026-08-24*

## Self-Check: PASSED

- FOUND: `.planning/v1.33/158-after-figures.md`
- FOUND: commit `b0ee57cd` (`git log --oneline --all | grep b0ee57cd`)
- FOUND: `.planning/phases/158-residual-optimizations-cold-baseline-re-record-firmware-only/158-06-SUMMARY.md` (this file)
- CONFIRMED: `git -C /workspaces/firestarter status --porcelain` empty; no firmware file modified by this plan
