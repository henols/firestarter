---
phase: 125-vpp-control-seam
plan: "06"
subsystem: firmware-ci
tags: [non-regression, evidence-artifact, claim-gate, requirements-close, vpp, py32f071]

# Dependency graph
requires:
  - phase: 125-vpp-control-seam
    plan: "01"
    provides: "the landed VPP control capability seam (include/rurp_vpp.h, src/rurp_vpp.cpp, platform/py32f071/CMakeLists.txt naming), the pre-phase pin"
  - phase: 125-vpp-control-seam
    plan: "02"
    provides: "the 10-case parametrized compile-and-run harness (tests/test_vpp_seam_manual_on_every_board.py)"
  - phase: 125-vpp-control-seam
    plan: "03"
    provides: "the 4-case PR #45 non-ancestry gate (tests/test_pr45_non_ancestry.py)"
  - phase: 125-vpp-control-seam
    plan: "04"
    provides: "Criterion 4's AVR measurement (0 B flash/RAM delta, non-vacuity, D-16 Branch A)"
  - phase: 125-vpp-control-seam
    plan: "05"
    provides: "ARM CI evidence (run 30652530756, head SHA 2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7)"
provides:
  - "125-NONREGRESSION.md — the phase's re-executed evidence artifact, every row from this closing session, never copied from the five prior plans' SUMMARY files"
  - "VPP-01, VPP-02 and VPP-03 ticked in .planning/REQUIREMENTS.md, each against a row re-executed in this session"
  - "the claim gate run with the artifact named explicitly through FIRESTARTER_CLAIMSCAN_TARGETS, exit 0, canonical caveat present verbatim"
affects: [126, 127]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Re-execution over transcription: every figure in the closing evidence artifact was produced by a command run in this session, with the prior plan's own claim recorded alongside it for comparison, never assumed correct from prose."
    - "Object-hash-only untouched-ness proof (never a diff, never a filtered diff): worktree hash + HEAD-tree hash, side by side, for both the 3 pinned files and the 4 must-not-touch files."

key-files:
  created:
    - .planning/phases/125-vpp-control-seam/125-NONREGRESSION.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "No firmware change in this plan. Both firmware-repo commits already existed (from Plans 125-01/02/03); this plan re-verified them read-only. Firmware git status --porcelain stayed 0 lines and HEAD stayed 2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7 throughout — the same SHA Plan 125-05's ARM run cites."
  - "Meta-repo gitlinks for firestarter/firestarter_app were NOT bumped in either commit, per this project's standing policy (gitlink bumps happen at milestone close, not per-plan) — git status showed 'M firestarter'/'M firestarter_app' throughout and neither was staged in either of this plan's two commits."
  - "Traceability table row (REQUIREMENTS.md line 163, 'VPP-01 … VPP-03 | Phase 125 | Pending') was deliberately left unchanged — the plan's Task 3 acceptance criteria required the commit's diff to touch only the three VPP checkbox lines, and the traceability row is not one of them."
  - "One informational, non-load-bearing figure discrepancy recorded rather than silently reconciled: src/rurp_vpp.cpp.o measured 4448 bytes on uno this session vs. Plan 125-04's recorded 4460 bytes — object byte size is a function of toolchain/tree state at measurement time (Plan 125-04 itself recorded an analogous discrepancy against RESEARCH's cross-check figure); does not affect the flash/RAM delta, which is 0 B in both sessions."

requirements-completed: [VPP-01, VPP-02, VPP-03]

coverage:
  - id: D1
    description: "125-NONREGRESSION.md exists, structured per Phase 124's template (header, re-execution pledge, numbered claims, recorded-vs-observed tables, per-criterion command/expected/observed rows), every row sourced from this session's own re-execution"
    verification:
      - kind: other
        ref: "Self-check: file exists at .planning/phases/125-vpp-control-seam/125-NONREGRESSION.md; every figure cross-checked against this session's own command output during authoring"
        status: pass
    human_judgment: false
  - id: D2
    description: "Criterion 3 proved exclusively by object-hash comparison (worktree + HEAD-tree) for the 3 pinned files and the 4 must-not-touch files — never a diff, never a filtered diff — all 7 confirmed equal to Plan 125-01's pre-phase pin"
    verification:
      - kind: unit
        ref: "git hash-object <7 paths> && git rev-parse HEAD:<7 paths>, this session, in /workspaces/firestarter"
        status: pass
    human_judgment: false
  - id: D3
    description: "Criterion 4 re-measured this session: 3 cold AVR builds, 0 B flash/RAM delta on all three targets, non-vacuity proven both directions, both gates exit 0, D-16 Branch A re-confirmed still not taken"
    verification:
      - kind: integration
        ref: "rm -rf .pio/build/<env> && pio run -e <env> (uno/uno328pb/leonardo); avr-nm symbol counts; check_size_baseline.py / check_build_warnings.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "ARM CI evidence independently re-derived read-only (gh run view 30652530756, git fetch + rev-parse), head SHA string-equal across three independent sources, no new beta-build.yml run cut"
    verification:
      - kind: unit
        ref: "gh run view 30652530756 --repo henols/firestarter --json ...; gh run list --workflow beta-build.yml; git fetch origin v1.23-py32f071-integration"
        status: pass
    human_judgment: false
  - id: D5
    description: "The claim gate exits 0 against 125-NONREGRESSION.md with the target named explicitly through FIRESTARTER_CLAIMSCAN_TARGETS, and the canonical 'no PY32F071 hardware exists' caveat is present verbatim"
    verification:
      - kind: unit
        ref: "FIRESTARTER_CLAIMSCAN_TARGETS=<abs path> python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py"
        status: pass
    human_judgment: false
  - id: D6
    description: "VPP-01, VPP-02 and VPP-03 ticked in .planning/REQUIREMENTS.md, each against a row this session re-executed, addressing every clause of the requirement's prose — this is the only plan in the phase permitted to tick them"
    verification:
      - kind: unit
        ref: "grep -c '^- \\[x\\] \\*\\*VPP-0' .planning/REQUIREMENTS.md == 3; grep -c '^- \\[ \\] \\*\\*VPP-0' .planning/REQUIREMENTS.md == 0"
        status: pass
    human_judgment: false

duration: 28min
completed: 2026-07-31
status: complete
---

# Phase 125 Plan 06: Closing Non-Regression Sweep + Requirement Ticks Summary

**Every one of the phase's verification rows re-executed fresh in this closing session (never copied from the five prior plans' SUMMARYs), written into `125-NONREGRESSION.md` in Phase 124's row shape, passed through the real claim gate with its target named explicitly (exit 0, canonical caveat present verbatim), and VPP-01/VPP-02/VPP-03 ticked in `REQUIREMENTS.md` — the only plan in the phase permitted to do so.**

## Performance

- **Duration:** ~28 min
- **Completed:** 2026-07-31
- **Tasks:** 3 (Task 1 read-only re-execution; Task 2 write the evidence artifact + run the claim gate; Task 3 tick the three requirements)
- **Files modified:** 2 in the meta repo (1 new, 1 modified); 0 in the firmware or host repos

## Accomplishments

- **Task 1 (read-only, no commit):** re-ran every verification row against the live trees in this session — all seven Criterion-3 object hashes (worktree + `HEAD`-tree) matched the pre-phase pin exactly; all ten PR #45 commits re-checked by hand (existence exit 0, ancestry exit 1, all ten) independently of the pytest module; the two seam files' live blob hashes confirmed to differ from PR #45's two recorded blobs; both new pytest modules re-run (`test_pr45_non_ancestry.py` 4 passed, `test_vpp_seam_manual_on_every_board.py` 10 collected / 10 passed); the whole firmware `tests/` suite re-run at **86 passed**; three fresh cold AVR builds (uno/uno328pb/leonardo) reproduced **0 B flash/RAM delta** on every figure, with non-vacuity re-proven in both directions (`.o` present, 0 seam symbols vs. 5 unrelated `vpp` symbols per env); both `check_size_baseline.py` and `check_build_warnings.py` re-run against this session's own fresh logs, both exit 0; D-16's Branch A (comparator green, re-baseline not taken) re-confirmed via both baseline files' blob hashes still matching `HEAD`; all three native environments re-run cold (`native`/`native_nodevtools` 141/141, 17 suites; `native_pinmap_provisional` 10/10, 1 suite); the manifest gate re-run at **24 enforced sources**, exit 0; the convention floors re-confirmed unchanged (`FLOOR=5`, `FIXTURE_FLOOR=10`); the whole host suite re-run at **1158 passed**, 0 failed, 0 skipped (via zero skip/fail/error string matches plus an independent dot-count of 1158 across 17 progress-report lines — this session's pytest invocation does not print a final "N passed" summary line, an environment quirk already documented identically in `124-NONREGRESSION.md` H13); the parity module re-run at **13 passed**; the cross-repo path inventory re-evaluated and confirmed to contain none of this phase's new/edited paths; the ARM evidence independently re-derived read-only (`gh run view 30652530756`, head SHA string-equal across three sources, no new `beta-build.yml` run cut).
- **Task 2:** wrote `.planning/phases/125-vpp-control-seam/125-NONREGRESSION.md` reusing Phase 124's structure — header block, re-execution pledge, `§1` numbered claims, `§2` recorded-vs-observed tables, per-criterion command/expected/observed sections (Criterion 1/2/3/4, non-regression rows), the three Phase-125-specific decisions (Option A's measured reason, the AVR-permanent framing, the PR #47 divergence sentence), then ran the real claim gate with the artifact named explicitly through `FIRESTARTER_CLAIMSCAN_TARGETS` — first run found the caveat present via the gate's own whitespace-tolerant, case-insensitive `REQUIRED_CAVEAT_PATTERN` but this document's own case-sensitive verify command (`grep -c 'no PY32F071 hardware exists'`) initially returned 0 because the only occurrence used capitalized "**No** PY32F071..." at the start of a sentence; added a second, exact-case occurrence ("As stated at the top of this document, no PY32F071 hardware exists...") and re-ran — **exit 0**, zero forbidden-phrase matches, caveat count 1 (case-sensitive). Committed in the meta repo only.
- **Task 3:** ticked exactly three checkboxes (`VPP-01`, `VPP-02`, `VPP-03`) in `.planning/REQUIREMENTS.md` — confirmed via `git diff` that only those three lines changed, checkbox character only, requirement text byte-identical otherwise. Re-asserted the firmware repo's porcelain (0 lines) and `HEAD` (`2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, unchanged, still the SHA Plan 125-05's ARM run cites) as the post-commit corroboration for Criterion 3, named explicitly to the firmware repo (the host repo's porcelain is separately, legitimately non-empty and not this row's subject). Committed in the meta repo only.

## Task Commits

1. **Task 1: Re-execute every verification row against the live trees** — read-only, no commit (no files modified; every acceptance criterion verified against live output during the task itself)
2. **Task 2: Write `125-NONREGRESSION.md` and prove it carries no forbidden claim** — `3be45b5` (docs, meta repo `/workspaces`)
3. **Task 3: Tick VPP-01, VPP-02 and VPP-03, and record the post-commit corroboration** — `eaa5990` (docs, meta repo `/workspaces`)

**Plan metadata:** meta-repo commit for this SUMMARY + STATE.md + ROADMAP.md (see final commit below).

## Files Created/Modified

- `.planning/phases/125-vpp-control-seam/125-NONREGRESSION.md` — new, the phase's closing evidence artifact (444 lines)
- `.planning/REQUIREMENTS.md` — 3 lines changed (checkbox character only, VPP-01/02/03)

## Re-Execution Pledge — Every Row, This Session, Independent Sourcing

Every figure below was produced by a command run in **this session**; where a prior plan's SUMMARY made
the same claim, both are stated so the comparison is explicit rather than assumed.

### Criterion 3 — the seven object hashes, worktree and `HEAD`-tree, this session

| Path | Worktree hash (this session) | `HEAD`-tree hash (this session) | Plan 125-01's pre-phase value | Match |
|---|---|---|---|---|
| `src/boards/rurp_common.cpp` | `5de1c8a1494200d8b2db210c3fd9d2d577a19b2b` | same | `5de1c8a1494200d8b2db210c3fd9d2d577a19b2b` | ✅ |
| `include/rurp_types.h` | `d3fe5203a91527bdb7b20a33843c81065e21c613` | same | `d3fe5203a91527bdb7b20a33843c81065e21c613` | ✅ |
| `src/rurp_config_utils.cpp` | `6705fd46e07a2d359d161dc2e7728cb4e45f89c7` | same | `6705fd46e07a2d359d161dc2e7728cb4e45f89c7` | ✅ |
| `include/rurp_shield.h` | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` | same | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` | ✅ |
| `platformio.ini` | `f4e720ba75a8c618cc23bac045ab65084d41a0a4` | same | `f4e720ba75a8c618cc23bac045ab65084d41a0a4` | ✅ |
| `include/messages.h` | `dc7dbfc6b7ad3d767f7dad1ecbe13a53ca1eb346` | same | `dc7dbfc6b7ad3d767f7dad1ecbe13a53ca1eb346` | ✅ |
| `scripts/baseline/size_baseline_base01.json` | `b940c91655600a57ad7ef67cba723943af929daf` | same | `b940c91655600a57ad7ef67cba723943af929daf` | ✅ |

`CONFIG_VERSION` re-read this session: `include/rurp_shield.h:46` — `#define CONFIG_VERSION "VER06"`, literal.

### The ten PR #45 exit-code pairs, this session (independent of the pytest module)

| SHA | existence exit | ancestry exit |
|---|---:|---:|
| `04fd9b3` | 0 | 1 |
| `fc0b2c7` | 0 | 1 |
| `86f351a` | 0 | 1 |
| `768580f` | 0 | 1 |
| `05f4a77` | 0 | 1 |
| `b964ee6` | 0 | 1 |
| `9134f2a` | 0 | 1 |
| `d285b83` | 0 | 1 |
| `71278d0` | 0 | 1 |
| `a47228d` | 0 | 1 |

### The two blob inequalities, this session

| File | Live worktree blob | PR #45's recorded blob | Equal? |
|---|---|---|---|
| `include/rurp_vpp.h` | `48f9f061ddf0affe743a4020f755ae3688e3fe8c` | `c982173813b38ec745b59d6e02817f2504d6c6b4` | no |
| `src/rurp_vpp.cpp` | `5d8b645db14636e895f37582e7a2847e4aa7bae9` | `fcbe009dffcd46139802f8779865a1d7aa331880` | no |

### Module case counts and the verbatim whole-suite output, this session

- `test_pr45_non_ancestry.py -q` → **4 passed** (prior claim, Plan 125-03: 4 passed — matches)
- `test_vpp_seam_manual_on_every_board.py --collect-only -q` → **10 collected / 7 functions**; `-q` → **10 passed** (prior claim, Plan 125-02: 10 collected / 10 passed — matches)
- `pytest tests/ -q`:
  ```
  ........................................................................ [ 83%]
  ..............                                                           [100%]
  86 passed in 4.31s
  ```
  (prior claim, Plan 125-03: 86 passed — matches)

### The three AVR targets, non-vacuity pairs, this session

| Env | Flash used/total | RAM used/total | Δ (both) | `.o` size (this session) | `.o` size (Plan 125-04) | seam symbols | unrelated `vpp` symbols |
|---|---|---|---:|---:|---:|---:|---:|
| uno | 23954/32256 | 1573/2048 | 0 | 4448 B | 4460 B | 0 | 5 |
| uno328pb | 24004/32384 | 1579/2048 | 0 | 4460 B | 4460 B | 0 | 5 |
| leonardo | 26016/28672 | 2014/2560 | 0 | 4460 B | 4460 B | 0 | 5 |

`check_size_baseline.py` (default mode) → `size-exit=0`. `check_build_warnings.py` → `warn-exit=0`. D-16
Branch A re-confirmed: `scripts/baseline/size_baseline.json` blob `9cc5204bb437735d77523e62512c1d2cadfc668f`
(worktree == `HEAD`); `scripts/baseline/size_baseline_base01.json` blob
`b940c91655600a57ad7ef67cba723943af929daf` (worktree == `HEAD`, frozen Phase-124 reference untouched).

### Native environments and gates, this session

- `native` (cold): **141 test cases: 141 succeeded**, 17 suites, all PASSED
- `native_nodevtools` (cold): **141 test cases: 141 succeeded**, 17 suites, all PASSED
- `native_pinmap_provisional` (cold): **10 test cases: 10 succeeded**, 1 suite, all PASSED
- `check_cmake_manifest.py`: `PASS: ... -- 24 enforced source(s) resolved`, exit 0
- `tests/test_checker_convention.py`: `FLOOR = 5` (line 123), `FIXTURE_FLOOR = 10` (line 124), unchanged, 7 passed

### Host repo, this session

- `pytest -q` (whole suite): **1158 passed**, 0 failed, 0 skipped — confirmed via zero skip/fail/error string matches in the captured output plus an independent dot-count of exactly 1158 across the 17 progress-report lines (this pytest environment does not print a final "N passed in Ys" summary line here — a pre-existing condition, identically documented in `124-NONREGRESSION.md` H13's own dot-count workaround for the same suite)
- `test_revision_constants_parity.py -q`: **13 passed** — matches Phase 124's recorded count exactly
- The parity module's single parsed firmware header: `firestarter_app/tests/test_revision_constants_parity.py:145` (`FIRMWARE_HEADER = fw_path("include", "firestarter.h")`); `_extract_defines` at `:288`; `_find_header_guard_line_indices` at `:242` — `include/rurp_shield.h` appears only in this module's docstring, so this phase's new header and source are inert to it, a checked fact
- `scan_paths.ALL_CROSS_REPO_PATHS` re-evaluated: 6 entries, none is this phase's new/edited paths — **no inventory entry expected, checked, not omitted**

### ARM evidence, independently re-derived read-only this session (not accepted from Plan 125-05's prose)

- `gh run view 30652530756 --repo henols/firestarter --json ...` → `conclusion=success`, `headSha=2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, `event=workflow_dispatch`
- `git -C /workspaces/firestarter rev-parse HEAD` = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7` — string-equal
- `git fetch origin v1.23-py32f071-integration:refs/remotes/origin/v1.23-py32f071-integration` then `git rev-parse origin/v1.23-py32f071-integration` = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7` — string-equal
- `gh run list --workflow beta-build.yml --limit 5` → newest run `30551682616`, `createdAt=2026-07-30T14:26:12Z`, predating the `py32f071.yml` run's `createdAt=2026-07-31T17:47:12Z` — **no new beta prerelease cut**

### The claim gate, invoked with the artifact named explicitly, exit code and rewording

```
$ cd /workspaces && FIRESTARTER_CLAIMSCAN_TARGETS="/workspaces/.planning/phases/125-vpp-control-seam/125-NONREGRESSION.md" \
    python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py
```

First invocation: `PASS: scanned ../125-vpp-control-seam/125-NONREGRESSION.md; 1 file(s) carry the
required silicon caveat`, **exit 0**, zero forbidden-phrase matches — the gate's own
`REQUIRED_CAVEAT_PATTERN` is whitespace-tolerant and case-insensitive, so it matched the document's
capitalized "**No** PY32F071 hardware exists." at the header. This document's own literal
`grep -c 'no PY32F071 hardware exists'` (case-sensitive, per the plan's acceptance criterion) initially
returned **0** because that was the only occurrence and it used capital "No". **One rewording applied:**
added a second, exact-lowercase-case sentence ("As stated at the top of this document, no PY32F071
hardware exists, and the ARM statement above is scoped strictly to 'configures and builds'...") in the
Criterion 1 ARM section. Re-ran: `grep -c` → **1**; gate re-run → **exit 0** unchanged. Neither the
gate's `FORBIDDEN_PATTERNS` table nor its target-resolution logic was edited — only the artifact's own
prose was reworded, per the plan's explicit instruction.

## The Three Ticks, Justified Per-Clause Against Named Rows

- **VPP-01** (`include/rurp_vpp.h` and `src/rurp_vpp.cpp` are hand-authored — nothing cherry-picked from
  PR #45): discharged by 125-NONREGRESSION.md's Criterion 1 — the ten-commit non-ancestry proof (all 10
  existence-exit-0, ancestry-exit-1, re-checked by hand independently of the pytest module), the two
  blob-hash inequalities against PR #45's recorded blobs, and `05f4a77`'s/`9134f2a`'s specific
  descriptions (the `CONFIG_VERSION` bump and the AVR voltage-measurement reroute this phase's
  dependency-free construction never touches) — all named in the requirement's prose and all discharged.
  Maps to ROADMAP Success Criterion 1.
- **VPP-02** (`rurp_set_vpp_target_mv()` returns `MANUAL_ADJUSTMENT_REQUIRED` on every board, asserted
  by a native test across each board macro-set): discharged by 125-NONREGRESSION.md's Criterion 2 — the
  10-case harness including the four-board parametrized leg (`uno`/`leonardo`/`uno328pb`/`py32f071`,
  10 passed), the forced-capability and unset-and-non-AVR guard legs, and the drift leg confirming the
  real anchors are literally present in `platformio.ini`/`CMakeLists.txt`. Maps to ROADMAP Success
  Criterion 2.
- **VPP-03** (diff gate proves the three files untouched and `CONFIG_VERSION` still `"VER06"`, with the
  AVR flash delta measured rather than asserted): discharged by 125-NONREGRESSION.md's Criterion 3 (all
  seven object hashes equal, `CONFIG_VERSION` literal `VER06`, no diff of any kind anywhere) and
  Criterion 4 (three cold AVR builds this session, 0 B flash/RAM delta measured — not merely asserted —
  with two-directional non-vacuity). Maps to ROADMAP Success Criterion 3/4.

**Post-commit corroboration for Criterion 3 (post-commit, firmware repo named explicitly):**
`git -C /workspaces/firestarter status --porcelain` = **0 lines**, re-checked at the end of Task 3 after
this plan's two meta-repo commits. `/workspaces/firestarter_app`'s porcelain is separately,
legitimately non-empty (`M .gitignore`; untracked `.coverage`, `.planning/config.json`, `SECURITY.md`,
`write_test_port.sh`) — unrelated, pre-existing, and not this row's subject. Firmware `HEAD`
re-asserted equal to `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, unchanged from Plan 125-05's cited
ARM-run head SHA — the ARM evidence still describes the branch tip.

## Decisions Made

- **No firmware or host repo change in this plan.** All work is meta-repo-only (`125-NONREGRESSION.md` +
  `REQUIREMENTS.md`). Firmware `git status --porcelain` stayed 0 lines and `HEAD` stayed
  `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7` throughout this entire session.
- **Meta-repo gitlinks (`firestarter`, `firestarter_app`) were not bumped**, in either of this plan's two
  commits — consistent with this project's standing policy that gitlink bumps happen at milestone close
  (or a deliberate separate action), not per closing-plan. `git status` showed `M firestarter`/
  `M firestarter_app` throughout; neither was staged.
- **Traceability table row left unchanged.** `REQUIREMENTS.md`'s `| VPP-01 … VPP-03 | Phase 125 |
  Pending |` row (line 163) still reads "Pending" — Task 3's acceptance criteria required the commit's
  diff to touch only the three checkbox lines, and the traceability row is a separate line outside that
  scope. Recorded here rather than silently left inconsistent.
- **One rewording applied to the claim-gate artifact** (see above) — an exact-case second occurrence of
  the canonical caveat sentence, added because the document's original occurrence was capitalized at the
  start of a sentence and the plan's literal case-sensitive verify command required a lowercase match.
  The gate's own pattern (case-insensitive) had already accepted the capitalized form; the rewording
  satisfies the plan's stricter literal `grep` command, not a gate failure.

## Deviations from Plan

**1. [Informational, not a deviation] Object-file byte size differs from Plan 125-04's recorded figure
on `uno` only.** `src/rurp_vpp.cpp.o` measured **4448 bytes** on `uno` this session vs. Plan 125-04's
recorded **4460 bytes** (uno328pb and leonardo both matched at 4460 B in both sessions). Per this
project's own established pattern (Plan 125-04 recorded an identical-shape discrepancy against
RESEARCH's cross-check figure), the object's byte size is a function of toolchain/tree state at
measurement time and is explicitly non-load-bearing — it does not affect the flash or RAM delta, which
is 0 B in every measurement this phase has ever taken. Recorded in `125-NONREGRESSION.md`'s
re-execution pledge and in this SUMMARY rather than silently reconciled.

**2. [Informational, not a deviation] The claim-gate artifact needed one rewording to satisfy the
plan's own literal `grep -c` verify command.** See "Decisions Made" above — the gate itself passed on
the first invocation (its own pattern is case-insensitive); the rewording was to satisfy the plan's
stricter case-sensitive acceptance check, and is recorded as a rewording per the plan's instruction to
record each one.

No other deviations. All three tasks' acceptance criteria were independently re-checked against live
command output before each commit.

## Known Stubs

None. This plan writes documentation-only artifacts (an evidence document and two requirement
checkboxes); there is no UI, no data path, and no hardcoded empty value anywhere in what this plan
produced.

## Threat Flags

None. This plan's threat model (see `125-06-PLAN.md` `<threat_model>`) is fully addressed:
T-125-37 (copied-not-re-executed evidence) is mitigated by the re-execution pledge plus the
prior-claim-alongside-this-session's-observation shape used throughout; T-125-38 (a vacuous
untouched-ness diff) is mitigated by object-hash-only proof, both worktree and `HEAD`-tree, for all
seven files; T-125-39/T-125-40 (a forbidden claim reaching a stranger, or the gate being narrowed to
let it through) are mitigated by the real gate run with the target named explicitly, iterated to exit
0 by rewording the artifact's own prose, never the gate; T-125-41 (a green gate that scanned nothing)
is mitigated by explicitly naming the artifact and recording that a present-but-empty value would mean
zero targets, not a silent fall-back; T-125-42 (ticking a partly-discharged requirement) is mitigated
by the per-clause justification above; T-125-43 (overclaiming four independent per-board facts) is
mitigated by the explicit bound recorded in `125-NONREGRESSION.md`'s Criterion 2 section; T-125-44 (an
ARM citation no longer describing the branch tip) is mitigated by this plan committing nothing in the
firmware repo and re-asserting `HEAD` equality in Task 3; T-125-45 (claiming CI coverage this branch
lacks) is mitigated by the explicit statement that no CI leg runs either new pytest module, with the
verbatim local run as the only evidence. No new security-relevant surface was introduced — this plan
adds a documentation artifact and two requirement checkboxes only.

## Issues Encountered

None beyond the object-byte-size and gate-rewording items already documented above under Deviations,
both resolved within their originating tasks.

## User Setup Required

None — no external service configuration required.

## Claim Ceiling Compliance

This SUMMARY makes no claim that the firmware runs on a PY32F071, that closed-loop VPP works, that the
pin map is correct/verified/validated, or an unqualified bench-validated/hardware-validated/
silicon-verified claim. **No PY32F071 hardware exists.** The only ARM statement made anywhere in this
SUMMARY or in `125-NONREGRESSION.md` is that the target configures and builds, cited by CI run URL and
head SHA — independently re-derived read-only in this session, never asserted from a relayed message
or a prior SUMMARY's prose. AVR manual VPP control is stated as permanent (D-05), never hedged as "for
now" or "pending hardware." The divergence between this branch's `RURP_HAS_VPP_DAC=0` and the closed
`origin/feature/py32f071-full-support`'s `1` is recorded as a deliberate fact, not a gap.

## Next Phase Readiness

- Phase 125 (VPP Control Seam) is closed: `125-NONREGRESSION.md` exists as the phase's re-executed
  evidence artifact, the claim gate exits 0 against it with the target named explicitly, and VPP-01,
  VPP-02 and VPP-03 are all ticked in `.planning/REQUIREMENTS.md`.
- No blockers for Phase 126 (Flash-Persistent Config): Criterion 3's pin on `src/rurp_config_utils.cpp`
  is what makes any Phase-126 regression there attributable, and this plan's object-hash re-hash
  confirms that file is still byte-identical to its pre-Phase-125 value at the moment Phase 125 closes.
- Firmware `HEAD` (`2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`) is unchanged from Plan 125-05's ARM-run
  citation — that citation still describes the branch tip as Phase 126 begins.
- No push, no `gh workflow run`, and no firmware/host commit was made by this plan — only two meta-repo
  `docs(125-06)` commits.

---
*Phase: 125-vpp-control-seam*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `.planning/phases/125-vpp-control-seam/125-06-SUMMARY.md`
- FOUND: `.planning/phases/125-vpp-control-seam/125-NONREGRESSION.md`
- FOUND: meta commit `3be45b5` (`git log --oneline --all` in `/workspaces`)
- FOUND: meta commit `eaa5990` (`git log --oneline --all` in `/workspaces`)
- FOUND: `.planning/REQUIREMENTS.md` shows `ticked-vpp=3`, `unticked-vpp=0`
- Firmware repo `/workspaces/firestarter`: `git status --porcelain` = 0 lines; `HEAD` = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7` (unchanged, no firmware commit expected — this plan writes meta-repo artifacts only)
