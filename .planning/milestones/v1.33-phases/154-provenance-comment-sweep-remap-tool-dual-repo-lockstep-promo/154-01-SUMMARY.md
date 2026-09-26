---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "01"
subsystem: infra
tags: [git-preservation, platformio, avr, byte-identity, sha256, baseline, uv, cpython311, pytest, branching]

requires: []
provides:
  - "wip/v1.33-size-reduction-survey-preserved @ a6b46f8 in firestarter — the ONLY committed ref carrying Phases 155-158's implemented size-reduction work, verified byte-identical to beta + the recorded recovery patch"
  - "gsd/v1.33-source-hygiene-firmware-size-reduction forked from beta in both sub-repos, with the pre-sweep anchor shas FW_PRE_SHA=8695ee5 and APP_PRE_SHA=6bfa645"
  - ".planning/v1.33/baseline-pre-sweep.md — the pre-sweep byte-identity pair for uno/uno328pb/leonardo, the four suite baselines, the five git anchors, and every producing command"
  - "Clean-tree suite baselines that supersede all of RESEARCH.md's dirty-tree numbers: 172/172 native, 172/172 native_nodevtools, 323 pass / 0 fail firmware gates, 1970 pass / 0 fail host suite"
  - "Discharge of research assumption A2 (the -g absence probe, now measured per env with a non-vacuous denominator) and research assumption A5 (all 13 dirty-tree failures were the dirt)"
affects: [154-02, 154-03, 154-04, 154-05, 154-06, 154-07, 154-08, 154-09, 154-10, 154-11, 154-12, 155, 156, 157, 158, 159]

tech-stack:
  added: []
  patterns:
    - "Commit-then-verify-then-switch: preserve a dirty tree by committing it to a named side branch and proving the commit equals a recorded recovery patch BEFORE the tree stops being dirty, reducing a destructive reset to a plain branch switch"
    - "Tree comparison over patch-text comparison: git archive + git apply + diff -r, because git diff output differs in its index lines even when content is identical"
    - "Non-vacuous grep: always record the denominator beside a zero-count assertion"

key-files:
  created:
    - .planning/v1.33/baseline-pre-sweep.md
    - .planning/phases/154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo/deferred-items.md
  modified:
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "D-12 precondition 1 discharged by COMMIT, never by reset — no reset --hard, clean, checkout --, restore, stash or force-push ran anywhere in this plan"
  - "The preservation oracle is a recursive TREE diff, not a patch-text diff — patch texts differ in their index lines even when content is identical"
  - "SWEEP-05 recorded as BOTH the sha256(.elf)/sha256(.hex) pair AND the Flash:/RAM: figures, for all three AVR targets — strengthening the requirement rather than substituting for it"
  - "The -g absence probe runs on a cold tree with its compile-line denominator recorded, because pio run -v on a built target makes the grep vacuously 0"
  - "ROADMAP.md and STATE.md updated by HAND, not by the GSD roadmap/requirements verbs, which normalise whole files — v1.33's ROADMAP and REQUIREMENTS are hand-authored"
  - "SWEEP-05 and SWEEP-13 NOT ticked in REQUIREMENTS.md — this plan delivers only their before-half and their anchors; plan 12 completes both"

patterns-established:
  - "Preservation-before-reset: the safe form of any 'reset the dirty tree' instruction is commit → verify by tree diff → switch"
  - "Measure both sides: where a fresh measurement disagrees with a recorded research figure, print both plus the command and explain the delta; never silently adopt either"
  - "Anchor commit-count criteria to a recorded pre-sweep sha, never to HEAD~1"

requirements-completed: []

coverage:
  - id: D1
    description: "The 11 dirty firestarter files are recoverable from a named committed ref, proven byte-identical to the recorded recovery patch before the tree stopped being dirty"
    requirement: "SWEEP-13"
    verification:
      - kind: integration
        ref: "git archive beta | tar -x && git apply firmware-size-reduction-measured.patch && diff -r /tmp/gsd-154-preserve/beta_plus /tmp/gsd-154-preserve/preserved  (empty output, exit 0)"
        status: pass
      - kind: integration
        ref: "git -C firestarter diff --shortstat beta..wip/v1.33-size-reduction-survey-preserved  ->  11 files changed, 229 insertions(+), 231 deletions(-)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both sub-repos on gsd/v1.33-source-hygiene-firmware-size-reduction forked from beta, with pre-sweep anchor shas recorded"
    requirement: "SWEEP-13"
    verification:
      - kind: integration
        ref: "git -C <repo> branch --show-current == gsd/v1.33-source-hygiene-firmware-size-reduction && git -C <repo> rev-list --left-right --count HEAD...beta == '0\t0'  (both repos)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Pre-sweep byte-identity pair recorded for uno, uno328pb and leonardo: sha256(.elf), sha256(.hex), Flash:, RAM:"
    requirement: "SWEEP-05"
    verification:
      - kind: integration
        ref: "rm -rf .pio/build/<env> && pio run -e <env> && sha256sum .pio/build/<env>/firestarter_<env>.{elf,hex}  — 3 envs, 6 hashes, each cold-built twice and hashing identically"
        status: pass
    human_judgment: false
  - id: D4
    description: "Pre-sweep test baseline for all three firmware CI legs plus the full host suite, taken on the clean tree"
    verification:
      - kind: integration
        ref: "pio test -e native (172/172); pio test -e native_nodevtools (172/172); pytest tests/ (323 pass / 0 fail); FIRESTARTER_FW_ROOT=/workspaces/firestarter /tmp/gsd-154-venv311/bin/python -m pytest tests/ -o addopts=\"\" -q (1970 pass / 0 fail)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The four F3 blob-sha gates recorded green, giving plan 07's sidecar regeneration a proven-green starting point"
    verification:
      - kind: integration
        ref: "cd firestarter && pytest tests/test_eprom_params_citations.py tests/test_protocol_branch_inventory.py tests/test_golden_trace_identity.py tests/test_golden_trace_identity_eprom_v131.py -q  ->  29 passed, exit 0"
        status: pass
    human_judgment: false

duration: 16min
completed: 2026-08-23
status: complete
---

# Phase 154 Plan 01: Preserve, Branch, Baseline Summary

**The 11 uncommitted firmware size-reduction files were made safe by commit-then-verify — proven byte-identical to `beta` plus the recorded recovery patch by an empty recursive tree diff *before* the tree stopped being dirty — after which the "reset" reduced to a plain branch switch, both sub-repos forked off `beta`, and every pre-sweep number this phase will compare against was measured on the clean tree with its producing command recorded beside it.**

## Performance

- **Duration:** 16 min
- **Started:** 2026-08-23T01:34:00Z
- **Completed:** 2026-08-23T01:50:07Z
- **Tasks:** 3 of 3
- **Files modified:** 2 created + 2 modified in meta; 11 files preserved (unchanged) in one `firestarter` commit

## Accomplishments

- **The irreversible step was made non-destructive.** `PRE_DIRTY_SHA` `8695ee5`'s 11 modified files were staged with `git add -u` (never `-A`, never `.`) and committed to `wip/v1.33-size-reduction-survey-preserved` @ **`a6b46f8`**. The preservation was then verified by a **recursive tree diff** — `git archive beta` + `git apply` the recorded recovery patch, versus `git archive a6b46f8` — which produced **no output and exit 0**. `git diff --shortstat beta..a6b46f8` reports exactly `11 files changed, 229 insertions(+), 231 deletions(-)`, matching the patch's own `git apply --stat`. Only after that did the branch switch happen, and because the dirt was already committed the switch carried **no discard semantics**.
- **No destructive git command ran.** The reflog for this plan contains exactly three entries: two `checkout: moving from …` and one `commit:`. No `reset --hard`, `checkout --`, `restore`, `clean`, `stash` or force-push. (Two `reset: moving to HEAD` entries dated 2026-08-22 predate this plan.)
- **Both sub-repos forked off `beta`** onto `gsd/v1.33-source-hygiene-firmware-size-reduction`, each at `0\t0` against `beta`. `FW_PRE_SHA` = `8695ee52c27a4bee4387c5c489afd5f3d7275e8a`, `APP_PRE_SHA` = `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a`. These are the SWEEP-13 anchors; plan 12 measures commit counts against them, never against `HEAD~1`.
- **Byte-identity pair recorded for all three AVR targets**, both hashes and both size figures. The artifact is `firestarter_<env>.elf` (`name_firmware.py` rewrites `PROGNAME`). Each env was cold-built **twice** — plain and verbose — and hashed **identically** both times on both `.elf` and `.hex`, which is free extra reproducibility evidence beyond what the plan asked for.
- **Research assumption A2 discharged for all three envs, not extrapolated.** The `-g` probe was found to be *vacuous* as written — `pio run -v` on an already-built target prints no compile lines at all, so the grep returns `0` whether or not `-g` is present. Re-run on a cold tree per env with the project-source compile-line count recorded as the denominator: **25 compile lines, 0 carrying `-g`**, on `uno`, `uno328pb` and `leonardo` alike.
- **Research finding F8 confirmed and assumption A5 upgraded from Medium to VERIFIED.** The clean tree gives **323 pass / 0 fail** (firmware gates) and **1970 pass / 0 fail** (host suite) against F8's dirty-tree `317 pass / 6 fail` and `1963 pass / 7 fail`. Totals are **identical on both sides** (317+6=323, 1963+7=1970), so all 13 failures were the dirt and not one was a latent defect. A5 no longer rests on mechanism plus a single spot check.
- **The four F3 blob-sha gates recorded green** (29 passed, exit 0), so plan 07's sidecar regeneration has a proven-green starting point and any post-regeneration redness is attributable.

## Task Commits

1. **Task 1: preserve the dirty firestarter tree on a named ref and verify it** — `a6b46f8` in the **`firestarter` sub-repo** (`wip`) — `wip(v1.33): preserve size-reduction-survey working tree before the provenance sweep`. 11 files, 229 insertions, 231 deletions. No meta-repo file changed, so no meta commit.
2. **Task 2: fork the milestone branch off beta in both sub-repos** — **git refs only, no commit.** `gsd/v1.33-source-hygiene-firmware-size-reduction` created at `8695ee5` (`firestarter`) and `6bfa645` (`firestarter_app`); no file content was edited in either repo, so there is nothing to commit. This is the plan's own `<files>` declaration ("git refs only").
3. **Task 3: record the pre-sweep byte-identity pair and the suite baselines** — **deliberately uncommitted**, per D-11. `.planning/v1.33/baseline-pre-sweep.md` is written to disk and read by every intervening plan, but the meta-repo `.planning/v1.33/` deliverables land in **one** commit made by plan 12. The plan states this explicitly: *"Do NOT commit this file to the meta repo in this plan."*

**Plan metadata:** see the `docs(154-01)` commit — SUMMARY.md, STATE.md and ROADMAP.md only. `.planning/v1.33/baseline-pre-sweep.md` is **excluded** from it by design.

## Files Created/Modified

- `.planning/v1.33/baseline-pre-sweep.md` **(created, uncommitted by design)** — the authoritative pre-sweep record: 5 git anchors, 3 AVR hash+size rows, the per-env `-g` probe with its denominator, 4 suite baselines, the F3 gate result, a full reconciliation table against RESEARCH.md, the preservation-verification transcript, and the environment traps.
- `.planning/phases/154-…/deferred-items.md` **(created)** — 2 out-of-scope discoveries logged, not fixed: the malformed `/workspaces/platformio.ini` and F7's module-count delta.
- `.planning/phases/154-…/154-01-SUMMARY.md` **(created)** — this file.
- `.planning/ROADMAP.md` **(modified — 3 hand edits, 3 insertions / 2 deletions, zero reformatting)** — ticked `154-01-PLAN.md`, flipped v1.33 checklist item 5 "Branches" from `◆ PARTIAL` to `✅ DONE` with the new shas and the do-not-delete warning, added a `| 154 | v1.33 | 1/12 | In Progress |` row.
- `.planning/STATE.md` **(modified — 9 hand edits)** — Current Position advanced to Plan 2 of 12, the stale "Phase 154 has not been discussed or planned" paragraph corrected, Branch posture rewritten with the preserved ref, 7 decisions added, a Performance Metrics row, and the Session block repointed. Re-read through `gsd-tools query state.json` afterwards to confirm the body-scraped fields still parse.
- `firestarter`: 11 files **preserved unchanged** in commit `a6b46f8` (`include/firestarter.h`, `include/memory_utils.h`, `src/boards/rurp_common.cpp`, `src/json_parser.c`, `src/proms/{eeprom_28c,eprom,flash_intel,flash_utils,memory}.cpp`, `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`, `test/native/avr/test_val_5v_page/test_val_5v_page.cpp`).

## Measurements

### Byte-identity pair (SWEEP-05, before-half)

| env | `.elf` sha256 | `.hex` sha256 | Flash: | RAM: |
|---|---|---|---|---|
| uno | `1cfa946f…31ecca` | `be6e4ac8…f05c095` | 26026 / 32768 | 1575 / 2048 |
| uno328pb | `6650baec…4ed98d8c` | `7b86c1aa…e43e20ebba` | 26074 / 32768 | 1581 / 2048 |
| leonardo | `fcca68e9…8672d7aef` | `2b9ad44e…effb0ee88` | 28170 / 32768 | 2016 / 2560 |

Full 64-char hashes are in `.planning/v1.33/baseline-pre-sweep.md` §2. Leonardo Caterina headroom: `28672 − 28170 = 502 B`.

### Suite baselines, clean tree

| Leg | Result | Wall |
|---|---|---|
| `pio test -e native` | 172 passed / 0 failed | 52.4 s |
| `pio test -e native_nodevtools` | 172 passed / 0 failed | 64.4 s |
| `pytest tests/` (firmware gates) | 323 passed / 0 failed | 11.2 s |
| host suite, CPython 3.11.16 | 1970 passed / 0 failed | 263.3 s |
| the 4 F3 blob-sha gates | 29 passed / 0 failed | 0.1 s |

## Requirement contributions (partial — NOT ticked)

Per the execution instruction, neither requirement this plan carries was ticked in `REQUIREMENTS.md`; both are only **completed** by plan 12.

- **SWEEP-05** — *before-half delivered.* The measured pair exists for all three AVR targets, in both the hash form and the `Flash:`/`RAM:` form. The requirement's actual claim ("byte-identical **before and after**") cannot be discharged until plan 12 takes the after-half and compares. **Left unticked.**
- **SWEEP-13** — *anchors and branches delivered.* Both sub-repos are branched and both pre-sweep anchor shas are recorded, which is what the commit-count criteria will be measured against. The requirement's actual claim ("one commit per sub-repo plus one meta commit; both sub-repo commits land before the host suite runs") is discharged by plan 12. **Left unticked.**

## Decisions Made

1. **Commit-then-verify-then-switch, per Ruling C.** The plan's own framing. Worth restating because it is the reason no risk was taken: the only crossing where information can be destroyed is working-tree → history, and this plan crossed it in the safe direction.
2. **A tree comparison, not a patch-text comparison.** `git diff` output embeds `index <blob>..<blob>` lines, which differ between two histories even when content is identical, so comparing the generated patch against the recorded patch would have produced a **false RED** on a correct preservation. Archiving both trees and running `diff -r` compares what actually matters. This was the plan's instruction and it was the right one.
3. **Both SWEEP-05 forms recorded, not one substituted for the other.** Ruling E. The hash pair is strictly stronger (a size figure is a 5-digit integer that cannot detect a size-neutral code change); the `Flash:`/`RAM:` figures are what the requirement literally asks for. Recording both means the strengthening is additive.
4. **The `-g` probe was rewritten to be non-vacuous.** See Deviations #1.
5. **ROADMAP.md and STATE.md edited by hand.** `roadmap.update-plan-progress` was **not** run. See Deviations #3.
6. **`.planning/v1.33/baseline-pre-sweep.md` left uncommitted, per the plan's explicit instruction and D-11.** Flagged as a standing risk below.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] The `-g` absence probe as written was vacuous and would have passed on a tree that *did* compile with `-g`**
- **Found during:** Task 3
- **Issue:** The plan specifies `pio run -v -e <env> 2>&1 | grep -c ' -g '`. Run in sequence after the recorded cold build, the target is already up to date, so `pio run -v` prints no compile lines at all — the grep returns `0` unconditionally. A test that returns PASS regardless of the property under test is not a test. This is the same failure shape as `reference_max_27c020_size_fake_firmware_parity` (a gate that cannot fail) and `reference_gate_authored_before_content_can_be_unreachable`.
- **Fix:** The probe now runs on a **cold** tree (`rm -rf .pio/build/<env>` immediately before `pio run -v -e <env>`), and the **denominator** — the count of project-source compile lines — is recorded beside the numerator so a `0` cannot be misread as vacuous. Measured: **25 compile lines, 0 with `-g`** on each of the three envs.
- **Files modified:** `.planning/v1.33/baseline-pre-sweep.md` §2 (the probe, its denominator table, and the reason)
- **Verification:** denominator is 25, not 0, on all three envs — the grep had something to scan. Research assumption A2 is now genuinely discharged for `uno328pb` and `leonardo` rather than extrapolated from `uno`.
- **Committed in:** not committed (task 3's artifact is uncommitted by design, per D-11)

**2. [Rule 2 — Missing critical functionality] `native_nodevtools` was absent from the plan's baseline list, leaving one of the three firmware CI legs unmeasured**
- **Found during:** Task 3
- **Issue:** The plan's action text lists three baselines: `pio test -e native`, `pytest tests/`, and the host suite. But this project's firmware CI is **`native` + `native_nodevtools` + `pytest tests/`** (`reference_v131_firmware_native_gate_gotchas`), and the plan's own success criterion says "the **three** firmware CI legs". Taking only two of three would leave a CI leg with no pre-sweep value to compare against at plan 12.
- **Fix:** Ran `pio test -e native_nodevtools` as a fourth baseline and recorded it: **172 passed / 0 failed**, 64.4 s.
- **Files modified:** `.planning/v1.33/baseline-pre-sweep.md` §3
- **Verification:** all three CI legs now have a recorded clean-tree value; exit 0 on each.
- **Committed in:** not committed (as above)

**3. [Rule 3 — Blocking] `roadmap.update-plan-progress` would have reformatted a hand-authored file, so ROADMAP.md was hand-edited instead**
- **Found during:** state updates
- **Issue:** The execution instruction says to update ROADMAP.md via `gsd-tools query roadmap.update-plan-progress`. But `STATE.md` and this milestone's own ROADMAP checklist item 2 both state, as a binding constraint, that v1.33's `ROADMAP.md` and `REQUIREMENTS.md` are **hand-authored and must never be regenerated** — the GSD verbs run `_normalizeMd` over the whole file and would reformat six phase entries, five D-labels and 31 requirements (`reference_gsd_requirements_roadmap_verbs_reformat_whole_file`). Running the verb would have destroyed hand-authored content to satisfy a bookkeeping step.
- **Fix:** Three surgical hand edits, snapshotted before and diffed after. `git diff --numstat` reports **3 insertions / 2 deletions** — exactly the three intended changes, zero reformatting.
- **Files modified:** `.planning/ROADMAP.md`
- **Verification:** `git diff --numstat .planning/ROADMAP.md` → `3 2`; snapshot kept at `/tmp/gsd-154-logs/ROADMAP.before.md`. STATE.md likewise hand-edited and then re-read through `gsd-tools query state.json`, which parsed every body-scraped field correctly.
- **Committed in:** the `docs(154-01)` plan-metadata commit

### Measurement deltas recorded, not adopted

Neither of these is a fix; both are cases where a fresh measurement disagreed with a recorded figure and **both sides were printed**.

**4. uno `Flash:` and `RAM:` differ from RESEARCH.md by exactly the size-reduction work.** Research recorded `Flash: 23088 / RAM: 1562`; the clean tree measures `Flash: 26026 / RAM: 1575`. Delta `+2938 B` flash / `+13 B` RAM — **exactly** the preserved work's measured `−2938 B` / `−13 B`. Research measured the *reduced* firmware against the dirty tree. The clean figures also match `.planning/notes/firmware-size-reduction-survey.md`'s own pre-reduction baseline (`uno flash=26026 ram=1575`, `leonardo flash=28170 ram=2016`) **to the byte on both targets**, independently corroborating that this is the correct pre-sweep state. Nothing was adjusted; both are in the reconciliation table.

**5. `firestarter_app` carries 7 pre-existing untracked entries, not the 3 the plan named.** Measured: `.planning/config.json`, `SECURITY.md`, four `datasheets/*.pdf`, and `write_test_port.sh` (unlisted by the plan). All harmless to every gate — verified by grep that **all** porcelain assertions target the *firmware* repo. The T-154-03 constraint is therefore recorded against the real list: **every `git add` in `firestarter_app` throughout this phase must be path-scoped; `git add -A` / `git add .` would sweep all 7 unrelated items into the SWEEP-13 commit.**

---

**Total deviations:** 3 auto-fixed (1 × Rule 1, 1 × Rule 2, 1 × Rule 3) + 2 measurement deltas recorded.
**Impact on plan:** No scope creep. Rule 1 turned a tautological check into a real one; Rule 2 filled a genuine gap between the plan's action text and its own success criterion; Rule 3 chose a project-level hard constraint over a workflow default. The plan's substance was executed exactly as written.

## Issues Encountered

**`pio` cannot be invoked with cwd `/workspaces`.** Discovered while capturing tool versions. `/workspaces/platformio.ini` exists as an untracked, **gitignored** (`.gitignore:20`) 21 KB stray with a duplicate `[platformio]` section at line 26, so every `pio` invocation from the meta root dies with `InvalidProjectConfError` — even a bare `pio --version`. Because it is gitignored it is invisible to `git status`, which is why no prior phase tripped it. Resolved for this phase by convention: **every** `pio` call is preceded by `cd /workspaces/firestarter`. Recorded as a TRAP in `baseline-pre-sweep.md` §6 and logged to `deferred-items.md`; not fixed, as it is untracked by all three repos and outside a comment-text phase's scope.

**Research finding F7 says 9 porcelain-asserting modules; measured 7.** Grep finds 4 in `firestarter_app/tests/` and 3 in `firestarter/tests/`. F7's load-bearing half is fully confirmed — all 7 assert on the **firmware** repo — so the conclusion (app untracked files are harmless) stands. Delta logged to `deferred-items.md`, corrected in neither direction.

## Standing risk for downstream plans

`.planning/v1.33/baseline-pre-sweep.md` is **uncommitted** from plan 01 until plan 12, per D-11 and the plan's explicit instruction. Two consequences the intervening plans must respect:

1. **Do not lose it.** It is the sole record of every pre-sweep number and cannot be reconstructed after the sweep. No destructive command runs in this phase, so the file is safe as long as that holds.
2. **`gsd-tools query commit` with no `--files` stages the ENTIRE working tree** and would sweep this file into whichever plan ran it, breaking D-11's one-meta-commit rule. Every commit in plans 02-11 must pass explicit `--files`.

## Self-Check: PASSED

Created files verified present on disk:
- `FOUND: .planning/v1.33/baseline-pre-sweep.md`
- `FOUND: .planning/phases/154-…/deferred-items.md`

Commits verified present in git:
- `FOUND: a6b46f8` — `git -C firestarter rev-parse --verify wip/v1.33-size-reduction-survey-preserved` exits 0 and prints `a6b46f8b12e81c62d9958945eb0bdbb8c16ae699`

Refs verified:
- `FOUND: gsd/v1.33-source-hygiene-firmware-size-reduction` in `firestarter` @ `8695ee5`, `0\t0` vs `beta`
- `FOUND: gsd/v1.33-source-hygiene-firmware-size-reduction` in `firestarter_app` @ `6bfa645`, `0\t0` vs `beta`

All three tasks' `<automated>` verify blocks re-run at plan end: **T1 exit 0, T2 exit 0, T3 exit 0.**

No forbidden git command ran: reflog contains no `reset --hard`, `checkout --`, `restore`, `clean`, `stash` or force-push created by this plan.
