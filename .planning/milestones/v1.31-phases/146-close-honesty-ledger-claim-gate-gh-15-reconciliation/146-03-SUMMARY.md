---
phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation
plan: 03
subsystem: planning-records
tags: [close, gh15, arm, py32f071, ci-provenance, honesty]
status: complete
requires:
  - "firestarter/.github/actions/build-py32f071/action.yml — the single place holding the ARM toolchain install, the cmake configure and the cmake build, reproduced locally so the observed build is the one CI would run"
  - "firestarter/platform/py32f071/CMakeLists.txt — the ARM manifest, including the two v1.31-registered translation units and the pinned FetchContent GIT_TAG"
  - ".planning/STATE.md:2043 — the Phase 145 MERGE-05 adjudication, the cited source of the three AVR sizes (§2 does not re-measure them)"
  - ".planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-check-claims.py — used in positional-argument mode to measure the box-9 sentence"
  - ".planning/phases/139-gh-15-correction-outward/139-check-claims.py:98-128 — the forbidden-vocabulary set, cited by location and never reproduced"
provides:
  - "146-ARM-BUILD-RECORD.md — the observed ARM outcome under exactly one of three named arms, the CI-never-ran measurement with per-row commands, the mandatory scoping caveat, and the quotable box-9 sentence plan 146-09 consumes"
  - "arm-build/ — eight raw artifacts (ci-state.txt, tool-versions.txt, packages.txt, toolchain-install.log, configure.log, build.log, build-oracle.txt, sha256sums.txt) the record is written from"
  - "the measured fact that the ARM py32f071 target compiles against this milestone's code, including both previously-blind TU registrations"
  - "the measured fact that neither repository's CI has run any v1.31 code beyond Phase 138, with its own oracles"
affects:
  - "146-09 (gh#15 box 9 grading — must lift §3's sentence WITH its caveat)"
  - "146-08 (the ledger's never-run evidence tier)"
  - "146-10 / 146-11 (both release bodies — the ARM target's verification status)"
  - "146-05 (owns the record gate's pre-existing R-15 hit this plan disproves but deliberately leaves in place)"
tech-stack:
  added: []
  patterns:
    - "reproduce CI's own build invocation locally rather than paraphrasing it, and apply CI's own success oracle rather than a substitute"
    - "record a plan-internal contradiction and substitute an equivalent oracle, instead of manufacturing state to satisfy the criterion's letter"
    - "measure a claim sentence against the phase's own gate with a live negative control, rather than asserting it is clean"
key-files:
  created:
    - ".planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-ARM-BUILD-RECORD.md"
    - ".planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/arm-build/ci-state.txt"
    - ".planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/arm-build/tool-versions.txt"
    - ".planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/arm-build/packages.txt"
    - ".planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/arm-build/toolchain-install.log"
    - ".planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/arm-build/configure.log"
    - ".planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/arm-build/build.log"
    - ".planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/arm-build/build-oracle.txt"
    - ".planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/arm-build/sha256sums.txt"
  modified:
    - ".planning/ROADMAP.md (exactly one line — this plan's own checkbox)"
    - ".planning/STATE.md (six lines in place, seven appended decision lines)"
decisions:
  - "OD-A discharged on the GREEN arm: the ARM toolchain installed here and py32f071 compiled against this milestone's code"
  - "The green is recorded as a DELTA against a never-compiled target and explicitly not as CI parity; the caveat is a labelled paragraph and travels with the box-9 sentence"
  - "The box-9 sentence was MEASURED against the phase's own claim gate with a live negative control, not asserted clean"
  - "The inference-based box-9 fallback is REPLACED, not published alongside the observation"
  - "No backlog stub filed — 999.32 belonged to the RED arm alone"
  - "A contradiction in this plan's own acceptance criteria (the non-zero-porcelain negative control) was recorded with substituted oracles rather than worked around"
  - "The record gate's pre-existing R-15 hit, which this plan's observation disproves, was left verbatim for 146-05"
metrics:
  duration: "~25 min"
  completed: 2026-08-17
  tasks: 2
  commits: 3
  files_created: 9
  files_modified: 2
---

# Phase 146 Plan 03: ARM Build Observation & CI-Never-Ran Measurement Summary

**One-liner:** The ARM `py32f071` target compiles against v1.31 code — arm **GREEN**, exactly one
`firestarter_py32f071.hex` under the firmware repo's own oracle — recorded as a local delta against a
target no CI run has ever compiled, never as CI parity, with the firmware repository byte-unchanged.

## Which arm was taken

**Arm GREEN.** Observed, not inferred:

| Item | Measured |
|---|---|
| toolchain install | `apt-get update` rc=0; `apt-get install -y cmake ninja-build gcc-arm-none-eabi binutils-arm-none-eabi` rc=0 |
| `cmake … -G Ninja -DCMAKE_BUILD_TYPE=Release` | rc=0 |
| `cmake --build` | rc=0, 44/44 ninja edges, link completed |
| composite-action oracle (`action.yml:102-107`) | **PASS** — exactly **one** `firestarter_*.hex` |
| hex | 78769 B, sha256 `5b0b55a2d71282a1899d3a931c673357912e1993a942934c26e67f61a4bebf8e` |
| `arm-none-eabi-size` on the `.elf` | text 27872, data 112, bss 5888, dec 33872 |
| SDK resolved by `FetchContent` | `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` — byte-identical to the `GIT_TAG` pinned at `platform/py32f071/CMakeLists.txt:17` |
| the two blind-registered TUs | `eprom_params.cpp.obj` and `eprom_budget.cpp.obj` both produced |

Arm **RED** and arm **NOT OBSERVED** are each marked `NOT TAKEN` in `146-ARM-BUILD-RECORD.md` §3, with
the reason each did not fire stated rather than left blank. Exactly two arms carry that marker
(`grep -c 'NOT TAKEN'` = 2).

## The box-9 sentence plan 146-09 must use

Quoted verbatim from `146-ARM-BUILD-RECORD.md` §3. **The mandatory scoping caveat travels with it** — a
box-9 grading that reproduces this without the caveat is an overclaim, and the record says so in those
terms:

> **met-as-corrected.** All four firmware build targets build against this milestone's code: the three
> AVR targets are measured at this tip — uno 24920 B, uno328pb 24970 B, leonardo 27002 B, RAM
> 1573/1579/2014 — each carrying MERGE-05's admitted, SHA-attributed +96 B defect-fix exemption (cited
> from `.planning/STATE.md:2043`, not re-measured here), and the ARM `py32f071` CMake target — which did
> not exist when this issue was filed — was compiled against this milestone's code for the first time in
> Phase 146 plan 146-03, emitting exactly one `firestarter_py32f071.hex` (78769 B, sha256
> `5b0b55a2d71282a1899d3a931c673357912e1993a942934c26e67f61a4bebf8e`) under the firmware repository's
> own composite-action oracle; that ARM result is a local **delta** against a target no CI run has ever
> compiled against any v1.31 code — it is **not CI parity**, and no PY32F071 circuit board exists
> anywhere in this project, so it establishes nothing about hardware.

**That sentence was measured, not assumed clean.** `python3 146-check-claims.py <scratch copy>` reported
**zero forbidden-phrase matches**; its only complaint was the two required 6.25 V caveat labels, which
the gate demands of any basename absent from its `_CAVEAT_RULES` map by fail-closed default (expected on
a scratch fragment, satisfied in `146-GH15-RECONCILIATION.md`, which the map covers). A **negative
control** — a deliberately non-compliant sentence — returned two forbidden matches (`verified-on-silicon`,
`proven-unqualified`) from the same invocation, so the scan was live and not vacuous.

## Firmware porcelain, both required readings

| Point in time | `git -C /workspaces/firestarter status --porcelain \| wc -l` |
|---|---|
| immediately after `cmake` configure | **0** |
| **immediately after the build, before any cleanup** | **0** |
| at the end of this plan | **0** |

`git -C /workspaces/firestarter diff --numstat` produced **no output** at every point, including for
`.gitignore` specifically. `firestarter/build`, `firestarter/configure.log`, `firestarter/build.log` and
`firestarter/tool-versions.txt` do not exist. Absolute paths used throughout, per the prior-wave hand-off
that a relative `git -C firestarter …` leg passes vacuously from the wrong cwd.

## Deviations from Plan

### Auto-fixed / recorded issues

**1. [Rule 1 — plan-internal contradiction] The task's negative control is structurally unreachable under the same task's own mandate**
- **Found during:** Task 1, at the point of measuring the post-build porcelain
- **Issue:** Task 1's acceptance criteria require the firmware porcelain to be **non-zero** immediately
  after the build, as a negative control proving the build wrote something — while the *same* task's
  action mandates directing the build directory outside the firmware repository. With `-B` pointing at
  `/tmp`, nothing is ever written inside `firestarter/`, so the honest measurement is 0 at both points
  and the stated control can never fire.
- **Fix:** The contradiction is **recorded, not worked around**. No artifact was created inside the
  repository to satisfy the criterion's letter, and nothing was added to `.gitignore`. Equivalent
  out-of-tree oracles were substituted and recorded in both `arm-build/ci-state.txt` and
  `146-ARM-BUILD-RECORD.md` §3: **43** object files, **166308537** bytes of build tree, four emitted
  images with recorded sha256 digests, and the two named `.obj` files for the previously-uncompiled
  translation units. None of those is producible by a build that never ran.
- **Files modified:** none in either sub-repo; the substitution is recorded in the meta-repo artifacts
- **Commit:** `974ea3d6` (the recorded note), `283c31ba` (the record's §3 paragraph)

**2. [Rule 2 — missing measurement] The plan asks for the record gate's `exempt hits by verdict` tally before and after, but that tally is unobtainable while the gate is RED**
- **Found during:** Task 2 verification
- **Issue:** `check_record_corrections.py` prints the `PASS:` line carrying `exempt hits by verdict`
  **only on its success path**. The gate is RED at phase start from a pre-existing cause, so no tally is
  printed by a default run — the criterion as written cannot be satisfied from that invocation.
- **Fix:** Captured the equivalent tally through the checker's own `--explain` mode instead, before and
  after every write this plan made, and recorded both. Unchanged across this plan:
  `{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'unlabeled': 1, 'superseded': 12}`.
- **Commit:** recorded in `STATE.md`'s decision lines and in this summary

### Not a deviation, but stated so it is not read as one

**The Phase 130 record gate exits 1, and that is the pre-existing phase-start condition — not a
regression from this plan.** Measured before any of this plan's writes and again after all of them: rc=1
both times, with **byte-identical output** (`diff` clean), naming one unlabelled `arm-toolchain-absent`
hit at `.planning/STATE.md:11`. Plan 146-01 bisected it to planning commit `d2c212f1`; **146-05 owns the
repair.** Task 2's verify leg asserting rc=0 therefore fails from that cause alone.

There is a live irony worth naming rather than burying: the stale sentence the gate flags is precisely a
claim that the ARM toolchain was unavailable here — **which this plan's observation disproves.** It was
nonetheless left **verbatim**, for two reasons: 146-05 owns it, and an exemption placed inside
`last_activity_desc` is destroyed by the next state write (146-01's own finding). This plan added **no
second copy** of that text; the new `last_activity_desc` states the disproof and points at the preserved
sentence by role rather than repeating its wording.

**The body's `Last activity:` narrative in `STATE.md` still reads `146-01 COMPLETE`.** That staleness
predates this plan (146-02 did not update it) and was deliberately not repaired here — the canonical
field is frontmatter `last_activity_desc`, which now carries the full 146-03 record. Named so a later
plan is not surprised by it.

## Authentication Gates

None. All `gh` calls were read-only (`gh run list` only) and already authenticated. No workflow was
dispatched, nothing was pushed, merged or tagged (D-01).

## What §1 measured (the fact that bounds box 9, the ledger and both release bodies)

| Field | firmware | host |
|---|---|---|
| local HEAD | `fa6c9c7` | `68820a6` |
| remote milestone-branch tip | `fb7949c` | `4d18b64` |
| local-only / behind, against that tip | **61 / 0** | **16 / 0** |
| against `origin/beta` | 66 / 2 | 16 / 0 |
| last CI run on the branch, and the ref it ran | 2026-08-09T06:48Z on `fb7949c` — *PY32F071 firmware* and *Firestarter CI* both success | 2026-08-09T07:01Z on `4d18b64` — *Host CI* success, `workflow_dispatch` |

Both TU-registering commits measured **non-ancestors** of `fb7949c`: `3207632` (`eprom_params.cpp`,
Phase 140) and `e9f6a92` (`eprom_budget.cpp`, Phase 143). `grep -c 'py32'` over
`firestarter/platformio.ini` prints **0** — the printed integer is the assertion, since grep exits 1 on a
zero count — so no PlatformIO environment, local or CI, could ever have compiled them either.

`py32f071.yml:27-28` fires on `push: branches: ['**']` with no `continue-on-error`, so the first push of
this branch runs the loud ARM gate on 61 unseen commits at once. Recorded as
`/gsd-complete-milestone`'s concern, not this phase's.

The Phase 143 and Phase 144 "green CI" statements are recorded as **local CI-replica runs, not CI runs**,
with the requirement that the distinction survives into the ledger.

## Requirements

**No requirement was ticked.** `CLOSE-04` is shared by plans 146-03, 146-05, 146-09, 146-12 and 146-13,
and **only 146-13** may tick `CLOSE-01`…`CLOSE-05`. `.planning/REQUIREMENTS.md` is byte-unchanged
(`git diff --numstat` produces no output for it) and no ROADMAP coverage row moved.

## Shared-file blast radius

| File | Change | Proof |
|---|---|---|
| `.planning/ROADMAP.md` | **1 line** — this plan's own checkbox, `- [ ]` → `- [x]` at line 592 | `git diff --numstat` = `1 1`; `diff` against a pre-write snapshot shows only line 592 |
| `.planning/STATE.md` | 6 lines changed in place (8, 9, 11, 16, 17, 115) + 7 appended decision lines | `git diff --numstat` = `13 6`; line-map from a pre-write snapshot |
| `.planning/REQUIREMENTS.md` | **none** | `git diff --numstat` produces no output |

`roadmap.update-plan-progress 146` was run and snapshot-diffed; `state.advance-plan` was **not** called
(the ninth-occurrence defect recorded in STATE.md). Every state edit was made by hand.

## Known Stubs

None. This plan produces records, not code.

## Threat Flags

None. No firmware, host or build-configuration byte was created, edited or deleted by this plan; the
only durable outputs are meta-repo records. The build introduced no network endpoint, auth path or
schema, and the one network act was the `FetchContent` clone of the SDK already pinned by SHA in the
manifest.

## Verification

| Leg | Result |
|---|---|
| `arm-build/ci-state.txt` exists and records `ls-remote`/`rev-list` measurements | PASS |
| firmware porcelain 0 lines (absolute path) | PASS |
| `arm-build/` non-empty, `ci-state.txt` non-empty | PASS |
| no `build/`, `configure.log`, `build.log`, `tool-versions.txt` in `firestarter/` | PASS |
| `OD-A` cited in the record | PASS |
| all three arms named (`grep -cE 'Arm (GREEN\|RED\|NOT OBSERVED)'` = 3) | PASS |
| exactly two arms marked `NOT TAKEN` (count = 2) | PASS |
| `does not establish` non-claims section present | PASS |
| firmware byte-unchanged and clean (`diff --numstat` empty, porcelain 0) | PASS |
| box-9 sentence: zero forbidden hits, with a live negative control | PASS |
| `grep -c '999.32'` over `ROADMAP.md` = 0 (RED arm did not fire) | PASS |
| Phase 130 record gate exits 0 | **FAIL — rc=1 from the pre-existing phase-start cause**, output byte-identical before and after this plan; owned by 146-05 |

## Self-Check: PASSED

All nine created files found on disk; all three commits found in `git log`. The one failing verification
leg is reported as failing, with its pre-existing cause named, rather than reported as a pass.
