---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "12"
subsystem: infra
tags: [byte-identity, sha256, avr, citation-manifest, retarget, staleness-marker, dual-repo-commit, phase-gate, gate-hazards]

requires:
  - phase: 154-01
    provides: "FW_PRE_SHA / APP_PRE_SHA as the commit-count anchors, the pre-sweep byte-identity pair for all three AVR targets, the four clean-tree suite baselines, and the pio-cwd trap"
  - phase: 154-02
    provides: "survey_provenance.py as the hit oracle, the pre-sweep corpus baseline, and sweep-gate-dispositions.md's 22-gate overlap column — re-checked here against the ACTUAL swept set"
  - phase: 154-03
    provides: "The 5 SWEEP-07 planted controls with their RED-before results recorded leg by leg, and the four planted fixtures this plan commits"
  - phase: 154-04
    provides: "The 13,692-row pre-sweep citation manifest with retarget:false on every row and the field present TO BE FLIPPED here, plus citation_paths.py"
  - phase: 154-05
    provides: "remap_citations.py's build_map / LineMap / map_point clamp — used here in ANALYSIS ONLY — and the measured proof that the tool is a no-op before the sweep"
  - phase: 154-06
    provides: "eeprom_28c.cpp swept, the _PAIR_RE collision removed by construction, and the prove-by-clean-clone pattern"
  - phase: 154-07
    provides: "firestarter/{src,include} swept, both eprom_params.cpp sidecars re-derived, the D6 line-pin repair, and the corrected file_hits verify-leg schema"
  - phase: 154-08
    provides: "firestarter/test swept under D-04's narrow treatment, with the ID-first eligibility rule and the named-abstention pattern"
  - phase: 154-09
    provides: "The shipped host package swept, the AST + comment-free-token invariance oracle, the serial_comm.py host no-touch region, and blocker D7"
  - phase: 154-10
    provides: "firestarter_app/tools swept and the corrected trailing-inline-comment verify leg"
  - phase: 154-11
    provides: "firestarter_app/tests swept, SWEEP-04 discharged, and the D7 gate retarget that unblocked this plan's phase gate"
provides:
  - "SWEEP-05's after-half: the post-sweep hash pair AND size pair for uno / uno328pb / leonardo, all six hashes and all six size figures identical to plan 01 character for character"
  - "SWEEP-10 settled: 815 retarget:true rows against the real diff, 786 reflowed / 29 deleted, 0 with a null new target, source_text byte-unchanged on every row, row count 13,692 before and after"
  - "The sibling post-diff deliverable: the per-file keep/delete ratio at 10.7 : 1 reflow-to-delete, 117 of 143 files pure 1-for-1 reflow — which MEASURES D-01's central premise rather than restating it"
  - ".planning/v1.33/CITATIONS-STALE.md — the SWEEP-12 marker, naming all 143 swept files and Phase 159 / REMAP-04 as the close-blocking closer"
  - ".planning/v1.33/sweep-outcome-record.md — the phase's authoritative after-side record: 15 sections, every residual attributed, the coverage ceiling stated, the nine deferred items and three gate-hazard classes carried forward"
  - "Exactly one commit per sub-repo: firestarter 2ad5b32 and firestarter_app bc9d592, each anchored rev-list --count <PRE_SHA>..HEAD == 1, both landed BEFORE the phase gate"
  - "The phase gate green at or above baseline: native 172/172, native_nodevtools 172/172, firmware gates 323/0, the four F3 blob-sha gates 29/29, full host suite 1976 passed / 0 failed / 0 skipped"
  - "The Ruling D overlap column re-checked against the ACTUAL swept set: one no-overlap row UPGRADED, and BOTH EXPOSURE rows confirmed LIVE over swept text"
affects: [155, 156, 157, 158, 159]

tech-stack:
  added: []
  patterns:
    - "Re-measure the 'before' side with the same committed tool against a git-archive export of the pre-sweep sha, rather than quoting an earlier plan's narrative — it makes the before/after pair one measurement, not two claims"
    - "When a plan's literal criterion collides with the phase's own exemption, report the criterion at its literal value AND the strictly stronger total measurement beside it; never reinterpret the criterion silently"
    - "Exclude the already-unreadable rows from a post-diff subset and NAME them, rather than folding them in to inflate a deliverable count"
    - "Keep a manifest's pre-change anchor and record the post-change choice in a declared sibling key — advancing the anchor on a subset while its siblings stay put is a landmine for the consumer"

key-files:
  created:
    - .planning/v1.33/sweep-outcome-record.md
    - .planning/v1.33/CITATIONS-STALE.md
  modified:
    - .planning/v1.33/sweep-citation-manifest.jsonl
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
  committed_in_subrepos:
    - "firestarter 2ad5b32 — 93 paths (src 17, include 15, test 58, tests/golden 2, tests/test_config_schema_pinned.py 1)"
    - "firestarter_app bc9d592 — 60 paths (56 modified + 4 new planted fixtures)"

key-decisions:
  - "SWEEP-13 is DELIBERATELY LEFT UNTICKED. Three of its four clauses are mechanically proven; the one-meta-commit clause is measurably NOT met (9 path-scoped commits, because plans 02/04/05 committed .planning/v1.33/ artifacts — plan 04 on the orchestrator's explicit instruction), and T-154-53 dispositioned a history rewrite as declined. A false tick is worse than an open box."
  - "target_line is NOT advanced on the 815 retarget rows. Every row keeps its pre-154 anchor, because Phase 159 maps a composite pre-154 -> post-158 diff and a row advanced to post-154 while its 12,877 siblings stayed pre-154 would be silently mis-mapped by the very tool this phase built. The hand-chosen target lives in retarget_new_line."
  - "SWEEP-03's literal criterion (--assert-tokens-zero D-# exiting 0) is unsatisfiable together with Ruling B's exemption. Reported at its literal value (exit 1, 4 violations, all in the exempt eprom.cpp) AND discharged by the stronger total measurement (34 -> 4, all 30 permitted lines gone, the exempt file proven byte-identical)."
  - "The 267 rows whose endpoint was already unreadable pre-sweep are EXCLUDED from the retarget subset and named, not folded in. The largest cluster is 231 citations binding by bare basename to a 38-line main.py at lines 194-416 — stale before this phase started."
  - "The generator's self-check reports 815 violations by design: 'retarget must be false in a pre-sweep manifest' is its PRE-sweep invariant firing correctly on a post-sweep file. Reported as the expected signal with every other clause shown clean, rather than suppressed."
  - "ROADMAP.md / REQUIREMENTS.md / STATE.md hand-edited only; roadmap.update-plan-progress and the requirements verbs were NOT run, per this milestone's binding constraint carried from plans 01-11."

patterns-established:
  - "Non-vacuous zero and non-vacuous pass, again: every count in this record carries its denominator, and the not-applied assertion first asserts the citation-bearing set has 1,228 entries so it cannot pass by being empty"
  - "A deliverable count is reported with its exclusions named, its causes broken out, and its manual-review half attached to a reviewable artifact rather than laundered into an automated leg"

requirements-completed: [SWEEP-01, SWEEP-03, SWEEP-05, SWEEP-07, SWEEP-10, SWEEP-12]

coverage:
  - id: D1
    description: "SWEEP-05's after-half: the post-sweep hash pair AND size pair for all three AVR targets, equal to plan 01's pre-sweep record"
    requirement: "SWEEP-05"
    verification:
      - kind: integration
        ref: "cd firestarter && for e in uno uno328pb leonardo; do rm -rf .pio/build/$e && pio run -e $e; sha256sum .pio/build/$e/firestarter_$e.{elf,hex}; done -> 6 hashes and 6 Flash:/RAM: figures, all identical to baseline-pre-sweep.md §2 character for character"
        status: pass
    human_judgment: false
  - id: D2
    description: "The actual swept set is produced from git diff --name-only against both pre-sweep shas, its size reported beside the candidate-set size, and all 27 untouched candidates attributed by name"
    requirement: "SWEEP-05"
    verification:
      - kind: integration
        ref: "fw 93 + app 56 = 149 modified paths = 147 source + 2 golden JSON; 143 are sweep edits and the 4 that are not are named; candidate 171 (169 at the pre-sweep shas, +2 plan-03 fixtures), swept 144, untouched 27, every one attributed"
        status: pass
    human_judgment: false
  - id: D3
    description: "SWEEP-03's before/after pair, and the honest reporting of the one place its literal form cannot hold"
    requirement: "SWEEP-03"
    verification:
      - kind: integration
        ref: "survey regex over git-archive exports of FW_PRE_SHA vs the working tree: D-# hit lines in firestarter/{src,include} 34 across 9 files -> 4 across 1 file, the one file being the Ruling-B-exempt src/proms/eprom.cpp which git diff --quiet proves byte-identical. --assert-tokens-zero D-# exits 1 with exactly those 4, reported at its literal value."
        status: pass
      - kind: integration
        ref: "retention: grep -roE 'D-[0-9]+' test | wc -l = 386 -> 386 (firmware); 1515 -> 1536 (app) with all +21 traced per file to plan 03's NEW fixtures and legs, zero pre-existing occurrences lost"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every one of the 198 residual hits is attributed to one of four permitted classes; no unattributed residual"
    requirement: "SWEEP-01"
    verification:
      - kind: integration
        ref: "survey_provenance.py --json: 651 -> 198 hits. Per-group attribution table in sweep-outcome-record.md §4 sums exactly: fw-src 23, fw-include 1, fw-test 70, app-pkg 19, app-tests 84, app-tools 1"
        status: pass
    human_judgment: false
  - id: D5
    description: "The D-08 retarget subset is settled against the real diff, its count reported, nothing dropped, original cited texts preserved"
    requirement: "SWEEP-10"
    verification:
      - kind: integration
        ref: "815 retarget:true rows of 9,343 considered; 786 reflowed / 29 deleted; 0 null new targets; source_text/source_text_end byte-unchanged on every row asserted against a pre-update snapshot; row count 13,692 before and after"
        status: pass
      - kind: integration
        ref: "generator self_check() on the updated file: 13,692 records re-read, 815 violations, ALL of them the single pre-sweep-invariant clause; every other clause clean"
        status: pass
      - kind: manual
        ref: "Whether each hand-chosen target is the RIGHT first surviving code line is a per-citation judgment (154-VALIDATION.md lists it as one of the six manual-only items). Reviewable artifact: the 815-row set with per-row retarget_cause / retarget_new_line / retarget_new_text / retarget_reason."
        status: pass
    human_judgment: true
  - id: D6
    description: "The staleness marker exists, names the swept files and the counts, and points at the close-blocking closer"
    requirement: "SWEEP-12"
    verification:
      - kind: integration
        ref: "CITATIONS-STALE.md contains REMAP-04, Phase 159, remap_citations.py, sweep-citation-manifest.jsonl, retarget, REMAP-01 and 1,302; lists all 143 swept paths individually plus the 6 modified-but-not-swept ones; six headed sections"
        status: pass
    human_judgment: false
  - id: D7
    description: "SWEEP-07's RED-after half, re-proven leg by leg against plan 03's recorded before-results"
    requirement: "SWEEP-07"
    verification:
      - kind: unit
        ref: "each of the 5 legs run individually with a -k selector: 5 x '1 passed, 11 deselected'. Modules test_sdp_table_parity.py 8 passed and test_dispatch_mirror.py 4 passed = 12, exactly plan 03's and plan 11's figures"
        status: pass
      - kind: unit
        ref: "the fail-open leg AST-checked: 0 raises-wrapper occurrences in its body, and its docstring still contains the literal 'fail-open'"
        status: pass
    human_judgment: false
  - id: D8
    description: "Exactly one commit per sub-repo, anchored to the plan-01 shas, both landed before the host suite; the phase gate at or above baseline"
    requirement: "SWEEP-13"
    verification:
      - kind: integration
        ref: "git -C firestarter rev-list --count 8695ee52..HEAD == 1 (2ad5b32); git -C firestarter_app rev-list --count 6bfa6453..HEAD == 1 (bc9d592); both porcelain-clean; 0 deletions in either; the app repo's 7 pre-existing untracked entries still ??"
        status: pass
      - kind: integration
        ref: "gate AFTER both commits: pio test -e native 172/172, native_nodevtools 172/172, pytest tests/ 323 passed / 0 failed, the four F3 blob-sha gates 29 passed, full host suite 1976 passed / 0 failed / 0 skipped in 234.34s"
        status: pass
    human_judgment: false
  - id: D9
    description: "The archived-milestones/ clause discharged by a verified absence with cause, and the remap tool proven not applied"
    requirement: "SWEEP-13"
    verification:
      - kind: integration
        ref: "git diff --name-only -- .planning/milestones is empty against both the working tree and the meta pre-sweep sha 717757f36; carried forward as a REMAP-01 note with the 1,302 figure"
        status: pass
      - kind: integration
        ref: "not-applied assertion, non-vacuous by construction: the manifest's citation-bearing planning-document set has 1,228 entries (asserted > 100 first), and its intersection with the modified .planning set outside .planning/v1.33/ is EMPTY"
        status: pass
    human_judgment: false
  - id: D10
    description: "The one-meta-commit clause of SWEEP-13 is NOT met; the actual count is recorded with its cause and no meta history was rewritten"
    requirement: "SWEEP-13"
    verification:
      - kind: integration
        ref: "git log --oneline 717757f36..HEAD -- .planning/v1.33 | wc -l == 8 BEFORE this plan's commit, so 9 after. The 8 are enumerated by sha and plan (02 x3, 04 x3, 05 x2). SWEEP-13 left unticked, T-154-53 declined the rewrite."
        status: pass
    human_judgment: false

metrics:
  duration: ~95min
  completed: 2026-08-23
  tasks: 4
  files_changed: 6
  commits: 3

status: complete
---

# Phase 154 Plan 12: Landing — the three commits, the after-pair, and the 815-row retarget subset Summary

**Landed the phase: all six hashes and all six size figures for `uno` / `uno328pb` / `leonardo` are identical to plan 01's pre-sweep record character for character, so SWEEP-05's revert rule never fired; the D-08 retarget subset is settled against the real diff at **815** rows with per-row cause, hand-chosen target and reason, nothing dropped and every `source_text` byte-unchanged; the SWEEP-12 marker is planted naming all 143 swept files and `Phase 159` / `REMAP-04` as the close-blocking closer; the three commits were made in D-11 order with each sub-repo anchored `rev-list --count <PRE_SHA>..HEAD == 1`; and the phase gate — run only AFTER both sub-repo commits — is green at or above baseline on every leg, with the full host suite at **1976 passed / 0 failed / 0 skipped**. SWEEP-13 is deliberately left UNTICKED, because three of its four clauses are proven and the fourth measurably is not.**

## Performance

- **Duration:** ~95 min
- **Completed:** 2026-08-23
- **Tasks:** 4 of 4
- **Commits:** 3 (`firestarter` `2ad5b32`, `firestarter_app` `bc9d592`, meta)

---

## The commit shas come first, deliberately

SWEEP-13's ordering clause is only *evidence* if the commits are recorded before the suite output. So:

| Repo | Commit | Committed at | `rev-list --count <PRE_SHA>..HEAD` |
|---|---|---|---|
| `firestarter` | **`2ad5b322a37ba4a88afd09cc946f5c4114e51483`** (`2ad5b32`) | 2026-08-23T07:12:42Z | **1** ✓ |
| `firestarter_app` | **`bc9d59293b9a08b16d6d7eb16eaf6c6f53e88e65`** (`bc9d592`) | 2026-08-23T07:13:29Z | **1** ✓ |

Both anchored to plan 01's recorded shas (`8695ee52…`, `6bfa6453…`), **never** to `HEAD~1` —
`git rev-list --count HEAD ^HEAD~1` is a tautology that always prints 1 and proves nothing.

**Route taken: direct commit, no squash.** Both sub-repo HEADs were still *at* their pre-sweep
shas when this plan started, because plans 03 and 06-11 each deliberately left their work
uncommitted per D-11. So `git reset --soft` was never needed and never run, and no reflog
recovery path was required. Recorded because the plan offered both routes.

**Staging was path-scoped in both repos, never `git add -A` or `git add .`:**

```bash
git -C firestarter     add -- src include test tests/golden tests/test_config_schema_pinned.py   # 93 paths
git -C firestarter_app add -- firestarter tests tools                                            # 60 paths
```

| Check | Result |
|---|---|
| `git -C firestarter status --porcelain` after | **empty** |
| `git -C firestarter_app status --porcelain --untracked-files=no` after | **empty** |
| The app repo's **7** pre-existing untracked entries still `??` | **7 of 7** — `SECURITY.md`, `write_test_port.sh`, `.planning/config.json`, `datasheets/{M27C1001,M27C512,W27C512,W27E257}.pdf` |
| Plan 03's **4** planted fixtures staged as **new** | 4 of 4 (`git diff --cached --diff-filter=A`) |
| The **D7 fix** `tests/test_parse_gate_admission.py` in the app commit | **present** — plan 11 flagged it explicitly, and the gate depends on it |
| Deletions in either commit | **0** in both (`git diff --diff-filter=D --name-only HEAD~1 HEAD` empty) |
| `wip/v1.33-size-reduction-survey-preserved` | **`a6b46f8b12e81c62d9958945eb0bdbb8c16ae699`** — intact |
| Anything pushed | **nothing.** All three repos hold their commits locally |

`__pycache__` is gitignored in the app repo, verified before staging, so `git add -- tests`
could not sweep byte-compiled caches in.

---

## The phase gate — run only AFTER both commits, and green on every leg

| Leg | Baseline (plan 01) | Now | Verdict |
|---|---|---|---|
| `pio test -e native` | 172 / 172 | **172 test cases: 172 succeeded** | at baseline |
| `pio test -e native_nodevtools` | 172 / 172 | **172 test cases: 172 succeeded** | at baseline |
| `pytest tests/` (firmware gates) | 323 / 0 | **323 passed** in 11.38 s | at baseline |
| the four F3 blob-sha gates | 29 / 0 | **29 passed** | at baseline |
| full host suite, CPython 3.11.16 | 1970 / 0 → **1976** expected | **1976 passed / 0 failed / 0 skipped** in 234.34 s, 32 snapshots passed | at baseline + 6 |

**The 7 red firmware legs and the 11 red host legs of plans 06-11 cleared on the commits, for
real.** Plans 06, 07, 08, 09, 10 and 11 each measured that class and each proved it benign in a
throwaway `git clone --shared`; this is the first run where the proof is the live tree rather
than a clone. The 7 were 5 `_git_porcelain` legs plus the 2 blob-sha gates whose message read
`recorded=7817c142… observed=5dffe841…` — the sidecar right and `HEAD` stale, exactly the
uncommitted state D-11 mandates.

The host total is **1,976**, not 1,975: plan 03 added 5 legs to plan 01's 1,970, and plan 11
added leg 5 to `test_parse_gate_admission.py` as the committed checkable negative for the D7
retarget. Arithmetic against plan 11's clean-clone reading closes exactly.

Editable-install sanity check first, per the sibling-worktree trap: the venv resolves
`firestarter.__file__` to `/workspaces/firestarter_app/firestarter/__init__.py` — the live tree.
`-o addopts=""` is mandatory (`pyproject.toml` sets `addopts = "-ra -q"`, and that plus a
command-line `-q` suppresses the count line).

### SWEEP-07's RED-after half, leg by leg

Each leg run **individually with its `-k` selector**, against the committed tree:

| Leg | Asserts | Plan 03's before-result | Now |
|---|---|---|---|
| `test_planted_comment_misanchor_is_detected` | gate goes **RED** on the plant | PASS | **1 passed** |
| `test_planted_comment_brace_break_is_detected` | gate goes **RED** on the plant | PASS | **1 passed** |
| `test_extracted_slice_is_anchored_on_the_real_declaration` | the live extraction anchors inside the **real, swept** `eeprom_28c.cpp` | PASS | **1 passed** |
| `test_planted_missing_hex_is_detected` | gate goes **RED** on the plant | PASS | **1 passed** |
| `test_planted_comment_only_hex_is_NOT_detected` | gate deliberately does **NOT** detect — the recorded fail-open | PASS, no raises-wrapper | **1 passed** |

**4-RED / 1-GREEN, unchanged.** Modules in full: `test_sdp_table_parity.py` **8 passed** and
`test_dispatch_mirror.py` **4 passed** = **12**, exactly plan 03's and plan 11's recorded
post-addition totals.

The GREEN leg was also AST-checked rather than trusted, because it is the one that could be
silently "fixed" into a RED leg by a well-meaning future editor: **0** raises-wrapper
occurrences in its body, and its docstring still contains the literal `fail-open`.

---

## Task 1 — the post-sweep outcome record

`.planning/v1.33/sweep-outcome-record.md`, 15 sections. The headline measurements:

### SWEEP-05's after-pair (Ruling E: hash pair AND size pair, three targets)

| env | `.elf` sha256 | `.hex` sha256 | Flash: | RAM: | matches plan 01? |
|---|---|---|---|---|---|
| uno | `1cfa946f…31ecca` | `be6e4ac8…05c095` | 26026 / 32768 | 1575 / 2048 | **yes** |
| uno328pb | `6650baec…d98d8c` | `7b86c1aa…20ebba` | 26074 / 32768 | 1581 / 2048 | **yes** |
| leonardo | `fcca68e9…2d7aef` | `2b9ad44e…b0ee88` | 28170 / 32768 | 2016 / 2560 | **yes** |

**Six hashes and six size figures, character for character.** The measured artifact is
`firestarter_uno.elf` (and siblings), **not** `firmware.elf` — `name_firmware.py` rewrites
`PROGNAME`, so an oracle hard-coding `firmware.elf` measures nothing. Cold-built per target,
with `cd /workspaces/firestarter` first (deferred item **D1**: the gitignored stray
`/workspaces/platformio.ini` kills any meta-root `pio` call). Leonardo Caterina headroom
unchanged at 502 B — the figure Phases 155-158 exist to widen.

### The actual swept set versus the candidate set

| Quantity | Value |
|---|---|
| Candidate set at the pre-sweep shas | **169** files |
| Candidate set in the manifest header | **171** — the +2 being two of plan 03's fixtures, which carry 4 hits each and existed at generation time but not at `APP_PRE_SHA` |
| Candidate files **actually swept** | **144** |
| Candidate files **untouched** | **27**, all attributed by name |
| Modified paths | **149** = 93 (`firestarter`) + 56 (`firestarter_app`) = 147 source + 2 golden JSON |
| Of the 147 source files, **sweep** edits | **143** |
| Of the 147, **not** sweep edits | **4**, named individually |

The 4 non-sweep source edits are `tests/test_config_schema_pinned.py` (plan 07's D6 line-pin
repair), `tests/test_sdp_table_parity.py` and `tests/test_dispatch_mirror.py` (plan 03's
SWEEP-07 legs), and `tests/test_parse_gate_admission.py` (plan 11's D7 retarget). Plus the 2
golden sidecars re-derived in lockstep for `eprom_params.cpp`.

The 27 untouched candidates break down as: **4** Ruling B blob-sha exemptions, **3** D-02
`CAP-0N` vocabulary exemptions, **2** plan-03 fixtures untouched by mandate, **2** named survey
false positives, **3** named narrow-treatment abstentions, and **13** files whose every hit is
an ID-first line that D-03 **retains** and D-04's eligibility rule therefore gives zero
operations. Every one is listed with its hit count and cause in the record's §2.

### The corpus, and SWEEP-03's before/after pair

Both sides measured with the **same** committed tool: the "before" side against `git archive`
exports of `FW_PRE_SHA` / `APP_PRE_SHA`, the "after" side against the live tree.

| Group | pre | post | | Group | pre | post |
|---|---|---|---|---|---|---|
| `fw-src` | 102 | **23** | | `app-pkg` | 132 | **19** |
| `fw-include` | 27 | **1** | | `app-tests` | 131 | **84** |
| `fw-test` | 216 | **70** | | `app-tools` | 43 | **1** |
| `fw-lib` | 0 | 0 | | **TOTAL** | **651** | **198** |

Of the 198 survivors, **8** are hits in two of plan 03's *new* fixtures, which did not exist
pre-sweep. Like-for-like: **651 → 190, i.e. 461 of 651 hits (71%) removed.**

**SWEEP-03's `D-#` pair, measured directly:**

| `D-#` hit lines in `firestarter/{src,include}` | Files | Value |
|---|---|---|
| at `FW_PRE_SHA` | 9 | **34** |
| in the working tree | 1 | **4** |

All 4 survivors are in `src/proms/eprom.cpp`, the Ruling-B blob-sha-exempt path, and
`git diff --quiet` on it exits 0 — so they are provably the *same 4 lines* it carried before
the sweep, and **all 30 in files the phase was permitted to edit are gone (30 of 30)**.

Retention side: `firestarter/test` is **386 → 386**, exactly unchanged across plan 08's ~143
line rewrites in 58 files. `firestarter_app/tests` is **1515 → 1536**, and a per-file diff
attributes **all +21** to plan 03's new test infrastructure (two new fixtures × 9, plus 3 new
legs in `test_sdp_table_parity.py`) — **zero** pre-existing occurrences lost.

### The residual, fully attributed — 198 of 198

Every remaining hit falls in exactly one of four permitted classes: a D-02-exempt `CAP-0` line,
a retained ID in a test file (D-03), one of the four Ruling B exempted files, or a recorded
abstention / named survey false positive. The per-group table in the record's §4 sums exactly.
**No unattributed residual.**

Two survivor classes are policy, not accident, and are stated as such: the **8** survey false
positives across three classes were left **unreworded** (rewriting correct English or correct
domain vocabulary to satisfy a regex is a worse outcome than a documented non-zero), and
stripping a narrative prefix routinely **exposes** a new hit because the line then begins with
the retained ID the prefix sat in front of — measured on both sides (14 `host_stubs.cpp` files
in plan 08, 8 rows in plan 11).

### The SWEEP-13 archived-`milestones/` clause, and the record-gate correction

```bash
git diff --name-only -- .planning/milestones                       # (empty)
git diff --name-only 717757f36… -- .planning/milestones            # (empty)
```

Discharged as **the collision's absence, with cause** — verified against both the working tree
and the meta pre-sweep sha, not restated from research: *no archived record was edited; the
citation repair is deferred to Phase 159 per D-01, so the archived-record hazard belongs to
**REMAP-01**, not to this phase.* Carried forward onto REMAP-01, where **1,302** `milestones/`
citations do get rewritten.

Record-gate folklore corrected by measurement so the next phase does not inherit a stale
number: `STATE.md`'s longest line is **2,965** characters (file 2,743 lines), not the remembered
52k; there is no `.planning`-level record-gate script; and **600** s is the timeout sized by the
actual slowest leg (the 234 s host suite), not by the 300 s folklore.

---

## Task 2 — the D-08 retarget subset, settled

Plan 04 generated the manifest **pre-sweep** with `retarget: false` on all 13,692 rows, because
the real diff did not exist yet. It exists now.

### The count: 815

| Quantity | Value |
|---|---|
| Manifest rows | **13,692** — unchanged, nothing added, nothing removed |
| Rows resolving into the **actual** swept set | **9,343** |
| — endpoint survived (fixed point or shifted) | 8,261 |
| — endpoint already unreadable pre-sweep (`text_status` ≠ `read`) | **267**, named and excluded |
| — **`retarget: true`** | **815** |
| Of the 815, rows with a **null** new target | **0** |

| Cause | Rows | | Group | Rows |
|---|---|---|---|---|
| comment **reflowed** (`replace`) | **786** | | fw-src | 486 |
| comment **deleted** (`delete`) | **29** | | app-pkg | 265 |
| | | | app-tools | 30 |
| | | | fw-include | 23 |
| | | | fw-test | 8 |
| | | | app-tests | 3 |

Across **41** target files and **294** planning documents. Heaviest: `eeprom_28c.cpp` 205,
`database.py` 144, `firestarter.cpp` 115, `json_parser.c` 48 — the expected ordering, since
`eeprom_28c.cpp` was swept as its own plan (−46 comment lines) and `database.py` carries the
condensed reversal record (65 → 56).

**Both `delete` and `replace` count as non-surviving**, per `remap_citations.py`'s own contract:
a reflowed comment can no longer match its recorded `source_text` at the destination, so mapping
it positionally would manufacture false green — which is exactly why such a row is *flagged*
rather than renumbered.

### Nothing dropped, and the texts preserved

| Assertion | Result |
|---|---|
| Row count before / after | **13,692 / 13,692** |
| `source_text` and `source_text_end` byte-unchanged on **every** row | asserted programmatically against a snapshot taken before the update |
| Every retarget row carries a `retarget_reason` | **815 of 815** |
| Rows with a null new target lacking a reason | **0** (and the null-plus-reason path is implemented anyway, so a future regeneration cannot fail open) |
| Written atomically | temp file + `os.replace` |

Five keys were added to the 815 rows and **declared** in the header under
`_schema.retarget_subset`: `retarget_cause`, `retarget_new_line`, `retarget_new_line_end`,
`retarget_new_text`, `retarget_reason`.

**The new-target rule:** walk **forward** from the cited line in the pre-sweep file to the first
non-comment, non-blank line that still survives, and record its post-sweep number — a comment
describes the code below it, so that walk *is* "the first surviving code line the comment
described". A range's end uses the same walk, clamped to be ≥ the new start.

### The one deliberate departure, and why it is safer

**`target_line` / `target_line_end` are NOT rewritten.** The plan's action text says to set the
new target, i.e. to advance `target_line`. Declined, for two measured reasons:

1. Every one of the manifest's 13,692 rows records its **pre-sweep** target — the header's
   stated invariant. Phase 159 maps a **composite pre-154 → post-158** diff whose old side is
   pre-154. A row advanced to its post-**154** value while its 12,877 siblings stayed pre-154
   would be silently mis-mapped by the very tool this phase built. That is a landmine.
2. D-08 requires `source_text` be preserved unchanged; preserving the text while moving the line
   makes the pair internally inconsistent.

Nothing is lost — the chosen target is recorded, named, reviewable, and carries its reason.

### Validity after the hand edit, reported honestly

The generator's `self_check()` re-reads **13,692** records and reports **815** violations, and
every one is the single clause `retarget must be false in a pre-sweep manifest`. That clause is
the generator's **pre-sweep** invariant firing correctly on a post-sweep file — the expected
signal, not a defect. Every other clause — JSONL validity line by line, the 14 required keys,
the variant enum, both endpoints present on every range record, resolution-versus-resolved-path
consistency — is **clean on all 13,692 rows**, which is what "a hand edit cannot leave the file
invalid" actually needed to prove.

### The 267 exclusions, named rather than buried

Their endpoint was already unreadable *before* the sweep, so the sweep cannot have deleted a
line they never resolved to. The manifest already labels each by `text_status` and Phase 159's
oracle must skip a non-`read` row by name — a contract that predates this plan. The largest
cluster is instructive: **231** citations bind by bare basename to
`firestarter_app/firestarter/main.py`, a **38-line** file, at lines 194-416. Stale before this
phase started; not sweep damage. Folding them into the 815 would have inflated a deliverable
with pre-existing rot.

### The sibling deliverable — the per-file keep/delete ratio

Over the **143 sweep-edited source files**:

| Quantity | Value |
|---|---|
| Comment lines pre / post | **15,678 / 15,571** (net **−107**) |
| Comment lines rewritten in place / removed | 1,150 / 1,264 |
| **KEEP : DELETE** (surviving : net removed) | **145.5 : 1** |
| **REFLOW : DELETE** (rewritten in place : net removed) | **10.7 : 1** |
| Files with insertions **==** deletions (pure 1-for-1 reflow) | **117 of 143** |
| Files with net comment deletion | **25 of 143** |
| Files with net comment **growth** | **1** — `src/proms/memory.cpp` (+4) |

**This measures D-01's central premise rather than restating it.** D-01 predicted that "the
dominant operation is not delete-vs-keep at all — it is strip the label, keep whatever sentence
follows." Measured: 117 of 143 files are pure line rewrites and reflow outnumbers deletion
**10.7 to 1**. The single growth case is the step-3 guard working as designed — `memory.cpp`'s
surviving invariant needed more lines to stand alone once its label was gone.

---

## Task 3 — the SWEEP-12 staleness marker

`.planning/v1.33/CITATIONS-STALE.md`, six headed sections, 313 lines. No *marker* precedent
exists in this project, so the shape is new and kept short and unambiguous.

| Section | Content |
|---|---|
| 1. What is stale | `.planning/` citations into the named files are knowingly stale **by deliberate decision (D-01)**, not by oversight |
| 2. Which files | **All 143 swept source files listed individually**, plus the 6 modified-but-not-a-sweep paths so the set is exact, plus the 171 / 144 / 27 candidate / actual / untouched split so the difference reads as intentional |
| 3. How many citations | 13,692 rows, 9,343 into the actual swept set, 7,249 shifting, **815** `retarget: true`, 267 pre-stale, 1,228 citing documents — with pointers to the manifest and to its Ruling G reconciliation |
| 4. Who closes it | **`Phase 159` / `REMAP-04`**, and its removal is **close-blocking**: the milestone cannot close while the file exists. D-10's measurements restated as *why the window is safe* — 723 citations otherwise remapped twice, 41% of that rework from four added `#include` lines, and one composite mapping avoiding the range-shrinking hazard |
| 5. What the closer needs | The manifest, `remap_citations.py`, its tests, the shared resolver, the survey, this record — plus **three hard requirements**: skip the 815 by name, `target_line` is still the pre-154 anchor, pass the composite shas on argv not from the header |
| 6. The hazard handed forward | Phase 154 edited nothing under `.planning/milestones/` (verified), but Phase 159 rewrites **1,302** citations that live there, so the archived-record gate hazard belongs to **REMAP-01** |

No mechanical close-block is added here — REMAP-04 owns that. `154-VALIDATION.md` specifies the
check against this file as the literal `REMAP-04` plus ≥1 swept path, deliberately weak because
the enforcement lives downstream.

---

## The remap tool was NOT applied

| Check | Result |
|---|---|
| Citation-bearing `.planning/` documents modified outside `.planning/v1.33/` | **NONE** |
| Non-vacuity of that assertion | the citation-bearing set is asserted to have **> 100** entries first; it has **1,228** |
| `.planning/` paths modified at all | `config.json` (the GSD harness's own `_auto_chain_active` flag, **not** citation-bearing — verified absent from all 1,228 `planning_file` values), plus the four `.planning/v1.33/` artifacts |
| Rows the tool rewrote | **0** — the tool was used in **analysis only**; `build_map`/`LineMap` were imported to compute the subset, never `--apply` |
| `wip/v1.33-size-reduction-survey-preserved` | `a6b46f8` — reachable, never deleted or force-updated |

Computing the retarget subset is analysis, not application. Phase 159 applies the tool once,
over the composite diff (D-01 / D-10).

---

## Ruling D — the overlap column re-checked against the ACTUAL swept set

SWEEP-06's requirement text was **not** expanded; the 22 non-comment-stripping firmware-repo
gates stay recorded as a **named exposure** and "22 gates need planted controls" stays filed as
a follow-on phase. But plan 02 measured that column against the **candidate** set, so it was
re-checked here path by path against the **actual** swept set:

- **8 of 9 `no-overlap` rows hold.** No `platform/` path changed at all, and rows 2 and 13's
  named source files are verified unchanged.
- **One upgrade — row 5, `test_checker_convention.py`.** Its recorded cause read "the sweep's
  globs are `firestarter/{src,include,test}` … this gate scans `scripts/` + `tests/`, neither of
  which the sweep touches." True of the candidate set, **false of the actual changed set**,
  which contains **three** `tests/` paths (both golden sidecars plus the D6 pin repair).
  Upgraded to **`overlaps — control`**: the mechanism is checker/test filename and naming
  convention, never content, so the overlap is real but harmless — and it is measured green in
  the real tree.
- **Both `EXPOSURE` rows are now CONFIRMED LIVE, not hypothetical.** All four files whose
  expected `#error "…"` text is extracted by a raw, unstripped, first-match-wins `re.search`
  — `include/rurp_vpp.h`, `src/rurp_vpp.cpp`, `include/boards/py32f071_pinmap_guard.h`,
  `include/boards/py32f071_rurp_shield.h` — **are in the actual swept set**. That upgrades the
  follow-on filing from "a shape that could bite" to "a shape now sitting over swept text with
  no control", and it is the single most important line in this record for Phases 155-158, all
  of which shift lines in those same files.

---

## What must not be buried — the ceiling, the residuals, the hazards

### The coverage ceiling

The byte-identity oracle covers the **129** shipped-firmware hit lines and **zero** of the 216
`firestarter/test` hits or the 306 host hits. **The host repo has no compiled byte-identity
oracle at all.** Plan 09 built an AST + comment-free-token invariance oracle to cover source
invariance on that side (50 of 50 modified Python files identical on both digests across plans
09/10/11, proven non-vacuous against four controls first) — and that is **source** invariance,
**not runtime behaviour**. Nothing in this phase proves the runtime behaviour of 21,197 lines of
Python unchanged the way three matching AVR image hashes prove it for the firmware. Both halves
of that sentence are load-bearing. Three py32-only headers are edited but compiled by none of
the three AVR targets; their invariance rests on plan 07's comment-stripped-equality measurement.

### The measured un-swept remainder

**The corpus was always regex-defined** — `survey_provenance.py` requires the token immediately
after a comment opener. So **D5** (152 firmware mid-comment lines with no survey hit to anchor
them) and **D8** (236 app-pkg mid-comment lines + 335 non-comment-line token occurrences) are
*measured* remainders, recorded as **scope, not failure**. This phase must not be read as "all
provenance removed" when a measured remainder exists. What it did is narrower and true:
**461 of the 651 regex-defined hits (71%) are gone, and every one of the 198 survivors is
attributed by name.** D8 also names a genuine product-surface leak the sweep cannot fix:
`chip_test.py`'s `_SDP_LOCKED_REASON` ships `(D-18)` into a `dev test` report a community tester
reads — a behaviour change with a snapshot to re-pin.

All nine deferred items D1-D9 are carried into the record's §11 as named residuals with their
causes. **D7 is RESOLVED** (plan 11's gate retarget).

### Three recurring gate-hazard classes, named because they will bite Phases 155-158

All three fire on a **line shift** or a **comment-text edit**, and all three were found by
**execution**, not inspection:

| Class | Instance | Why inspection misses it |
|---|---|---|
| **Exact-line-number pins** | `test_config_schema_pinned.py`'s `_C14_CONSUMER_SITES` (**D6**) — the only executable line-number pin over swept firmware paths in either repo. Current pins: `firestarter.cpp` 38/115/121, `hardware_operations.cpp` 106/118 | The module's *other* mechanism is genuinely comment-safe, so a reviewer reading the disposition row stops there |
| **Comment-text pins via `inspect.getsource()`** | `test_serial_comm.py`'s ring-fence digest over `serial_comm.py:455-581` — the only one of 19 `inspect.getsource` call sites whose result is **digested** | `inspect.getsource()` returns raw source **including comments**, so no comment-stripping audit of the source can find it; it must be found by **running** the suite. The comment documenting the ring fence was itself *inside* the ring fence |
| **Provenance-label pins** | `test_parse_gate_admission.py` asserted the literal `"Phase 151"` in firmware source (**D7**, fixed) | It fails **closed** on the sweep's intended outcome — the inverse of the usual fail-open shape. Grep the **host** test suite for a label before deleting it from firmware source |

### Ruling B's exemptions

Four blob-sha-pinned paths left un-swept, each with the sidecar pinning it —
`eprom.cpp` / `protocol_branch_inventory.json`, `eprom_params.h` /
`eprom_params_citations.json`, `_shared/eprom_v131_expected.h` /
`eprom_v131_trace_inventory.json`, `_shared/sdp_expected.h` / `sdp_expected_inventory.json`.
All four verified byte-identical (`git diff --quiet` exits 0).

**Two sidecars WERE re-derived**, for the one file Ruling B chose to sweep rather than exempt:
`src/proms/eprom_params.cpp` is **double-pinned**, and `5dffe841…ae22da → 7817c142…fb4465`
landed in **both** `eprom_params_citations.json` and `protocol_branch_inventory.json`, with each
sidecar's *other* pin asserted unchanged as a literal. Updating only the first would have left a
gate RED for a reason a reader would misdiagnose as sweep damage. Proven right by the four F3
gates running **29/29** post-commit.

### Ruling G's reconciliation, carried forward

Plan 04's reconciliation is carried forward rather than collapsed into a single number: measured
**10,169** swept-targeting / **7,076** shifting against the recorded **10,054** / **6,939**
(+1.1% / +2.0%), every delta traced to `.planning/` growth plus an 11-file wider candidate set,
with four subtrees reproducing the recorded figure **exactly**. **One item stays explicitly
part-unexplained** — the 1,073 / 955 / 1,351 spread on unresolved citations is a definitional
spread *inside* the recorded research, not a discrepancy this run can close. Also carried: that
records are not occurrences (a `colon_list` expands one occurrence into N records, so 678 vs 274
reads as +147% when the real delta is +0.7%), and that the fixture-exclusion rule turned out to
be defence in depth on this tree rather than the load-bearing disambiguator research predicted.

---

## Requirements

**Ticked (6):**

- **SWEEP-01** — the five keep-examples all shown with their surviving sentence quoted, and
  D-01's premise now **measured** at 10.7 : 1 reflow-to-delete.
- **SWEEP-03** — the before/after pair on both sides: 34 → 4 stripped (30 of 30 permitted lines
  gone, the exempt file proven byte-identical), 386 → 386 and 1515 → 1536 retained with all +21
  traced and zero lost.
- **SWEEP-05** — the measured pair, strengthened to a hash pair, on three targets.
- **SWEEP-07** — RED-before (plan 03) and RED-after (here), re-proven leg by leg.
- **SWEEP-10** — **815**, with the keep/delete ratio as its sibling deliverable.
- **SWEEP-12** — the marker planted and pointing at its close-blocking closer.

**Left UNTICKED — SWEEP-13.** Three of its four clauses are mechanically proven: one commit per
sub-repo (`rev-list --count <PRE_SHA>..HEAD == 1` in both), both landing before the host suite,
and the archived-`milestones/` clause discharged as a verified absence with cause. **The fourth
is measurably not met.** `git log --oneline <meta-pre-sweep>..HEAD -- .planning/v1.33 | wc -l`
was already **8** before this plan committed, so it is **9**, not 1:

| Plan | Commits | Cause |
|---|---|---|
| 154-02 | 3 (`3ee003f6`, `9c7605ea`, `1680c30a`) | the survey tool plus its two records |
| 154-04 | 3 (`1f48b5d1`, `b56b88e6`, `9a78bc6d`) | the resolver, generator, manifest and report — **on the orchestrator's explicit instruction** that D-11's one-commit rule constrains the sub-repos, not meta |
| 154-05 | 2 (`7fedf886`, `39455a8c`) | the remap tool and its 21 legs |

Threat **T-154-53** dispositioned rewriting meta history to force a single commit as
**accept/declined** — meta history carries GSD's own doc commits and rewriting it in a chained
run is the larger risk. SWEEP-13 asks for the outcome recorded either way, and this is it.
**A false tick is worse than an open box.** Re-tick only if the clause is amended to
path-scoped-per-plan, or if a future phase consolidates deliberately.

---

## Deviations from Plan

### Auto-fixed / reported rather than reinterpreted

**1. [Rule 3 — Blocking] Task 1's acceptance criterion "`--assert-tokens-zero D-#` exits 0" is
unsatisfiable together with this phase's own Ruling B exemption**

- **Found during:** Task 1, first run of the SWEEP-03 oracle.
- **Issue:** the leg exits **1** with 4 violations, all inside `src/proms/eprom.cpp` — the
  blob-sha-pinned path Ruling B forbids this phase from editing. `survey_provenance.py` has no
  exclusion flag, so no invocation of it can reach 0 while the exemption stands. The criterion
  and the phase's own ruling cannot both hold.
- **Fix:** the criterion is reported **at its literal value** (exit 1, all four lines quoted)
  and the requirement discharged by the strictly stronger **total** measurement instead: `D-#`
  hit lines in `firestarter/{src,include}` go 34 across 9 files → 4 across 1 file, with
  `git diff --quiet` proving that file byte-identical, so all 30 in permitted files are gone and
  the 4 survivors are the same 4 lines it carried pre-sweep. Nothing is claimed to be zero that
  is not.
- **Files:** `sweep-outcome-record.md` §3, `REQUIREMENTS.md` SWEEP-03.

**2. [Rule 1 — Bug] A naive retarget computation over-counted by 267, because 231 of them target
a 38-line file at lines 194-416**

- **Found during:** Task 2, first pass — 1,082 rows, with `main.py` implausibly heading the
  per-file table at 232 despite that file changing by a single comment line.
- **Issue:** the first pass tested endpoint survival without first checking the endpoint's
  `text_status`. Rows whose cited line was already past EOF, unresolved, rejected or ambiguous
  *before* the sweep read as "non-surviving", so pre-existing citation rot was about to be
  reported as sweep damage — and as part of a headline deliverable count.
- **Fix:** the determination is restricted to endpoints whose `text_status` is `read`. The 267
  excluded rows are counted and named, with their largest cluster called out explicitly. Count
  corrected 1,082 → **815**.
- **Verification:** `815 + 267 + 8,261 = 9,343`, the considered total, closes exactly.

**3. [Rule 2 — Missing critical] The plan's own verify leg for Task 2 is vacuous as written**

- **Found during:** Task 2 verification.
- **Issue:** the leg asserts that every retarget row with a **null `target_line`** carries a
  `retarget_reason`. Since `target_line` is deliberately never null (see the departure below),
  that assertion passes over an empty set and measures nothing.
- **Fix:** the leg is run as written **and** re-expressed against the field that genuinely can
  be null (`retarget_new_line`), plus a total assertion that **all 815** rows carry a reason
  regardless. Reported with the null-new-target count (**0**) so the zero is not mistaken for a
  vacuous pass.

**4. [Rule 3 — Blocking] "Re-run the generator's schema self-check" needed restating, because
that self-check is a PRE-sweep checker**

- **Issue:** `build_citation_manifest.self_check()` treats `retarget is not False` as a
  violation — correctly, for a pre-sweep manifest. Running it on the updated file reports 815
  violations, which a careless reading would call a defect.
- **Fix:** it is run and reported as **exactly 815 violations, all of the single pre-sweep-invariant
  clause**, with every other clause shown clean on all 13,692 rows. That is what "a hand edit
  cannot leave the file invalid" actually needed to prove.

### Deliberate departures

**5. `target_line` is NOT advanced on the 815 retarget rows.** The action text says to set the
new target. Declined: Phase 159's old side is pre-154, so advancing a subset while its 12,877
siblings stay pre-154 would be silently mis-mapped by this phase's own tool; and preserving
`source_text` while moving the line makes the pair internally inconsistent. The hand-chosen
target is recorded in `retarget_new_line` with a per-row reason. Declared in the manifest header.

**6. One meta commit instead of the usual artifact-commit-then-docs-commit pair.** The success
criterion is "exactly ONE meta commit", so the `.planning/v1.33/` artifacts and the
SUMMARY/STATE/ROADMAP/REQUIREMENTS updates ride in a single commit rather than two.

**7. `roadmap.update-plan-progress` and the requirements verbs deliberately not run.** v1.33's
`ROADMAP.md` and `REQUIREMENTS.md` are hand-authored and the GSD verbs normalise whole files.
All three files were edited by surgical hand replacement with a uniqueness assertion on every
`old` string: `REQUIREMENTS.md` **14 insertions / 14 deletions**, `ROADMAP.md` **2 / 2**,
`STATE.md` **20 / 14** — zero reformatting. `STATE.md` was re-read through
`gsd-tools query state.json` afterwards and every body-scraped field parses (`status: completed`,
`completed_plans: 12`, `stopped_at` intact).

**8. Nothing pushed.** Landing means committing locally; pushing is the operator's call.

**9. [Rule 2 — Missing critical functionality] The meta commit also bumps both submodule
gitlinks, which the plan's `--files` list did not name.** Without it, meta `HEAD` would assert
"Phase 154 COMPLETE" while its gitlinks still pointed at `firestarter 8695ee5` /
`firestarter_app 6bfa645` — trees containing **none** of the sweep. That is precisely the gap
Phase 149 left and this project had to close retroactively, so it is a correctness requirement
rather than bookkeeping. Bumped to `firestarter 2ad5b322…` and `firestarter_app bc9d5929…`,
both verified equal to their repo's `HEAD`, and folded into the **same** commit by
`git commit --amend --no-edit` so the "exactly ONE meta commit" criterion still holds. The
amend ran with **no pathspec**, because `git commit -- <path>` discards a staged gitlink update.
The commit is local and unpushed, so the amend rewrote nothing shared.

`firestarter_app` still shows ` M` in meta's `git status`: that is **untracked content only** —
the 7 pre-existing untracked entries inside the sub-repo — not a sha mismatch.
`git diff --ignore-submodules=untracked -- firestarter_app` is empty and the gitlink equals the
app repo's `HEAD` exactly.

---

## Issues Encountered

None beyond the four items above. No architectural decision was needed and no checkpoint was
reached. No forbidden git command ran in any repo: no `reset --hard`, `git clean`,
`git checkout -- <path>`, `git restore`, `git stash`, force-push or branch deletion. All three
repos are ordinary checkouts (`.git` is a directory in each), so no worktree hazard applied, and
the `git reset --soft` squash route the plan offered was never needed because both sub-repo HEADs
were still at their pre-sweep shas.

---

## Handoff Notes

- **Phases 155-158** must read the three gate-hazard classes above before their first edit. All
  three fire on a line shift, and both Ruling D `EXPOSURE` rows are now **live over swept text**.
  The current D6 pins are `firestarter.cpp` 38/115/121 and `hardware_operations.cpp` 106/118.
- **`wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8`** in `firestarter` remains the ONLY
  ref carrying Phases 155-158's implemented work. Verified reachable at the end of this plan.
  **Do not delete or force-update it.**
- **Phase 159** inherits: skip the **815** `retarget: true` rows by name plus the 267 non-`read`
  rows; `target_line` on every row is still the **pre-154** anchor and the post-154 choice is in
  `retarget_new_line`; pass the composite shas on argv, **not** from the header (deferred item
  **D3** — the app side's `source_text` came from a working tree already carrying plan 03's
  edits, so its old anchor is the **plan-12 app commit** `bc9d592`); `.planning/STATE.md`'s 15
  bindings need a regeneration or an exclusion (**D4**); and **REMAP-01** owns the archived-record
  hazard for its 1,302 `milestones/` citations.
- **REMAP-04** removes `.planning/v1.33/CITATIONS-STALE.md`, and that removal is
  **close-blocking** for milestone v1.33.
- **Follow-on phases still filed, not built:** planted controls for the 22 firmware-repo
  fail-open gates (starting with the two now-live `EXPOSURE` rows); a `--token-anywhere` sweep
  deciding D5 and D8 together for both repos; the `_SDP_LOCKED_REASON` product-surface ID leak;
  amending `sweep-gate-dispositions.md` §B row 6 (D6) and row 5 (this plan's upgrade); and the
  `ruff` hygiene pass on `firestarter_app/tools` (D9).

## User Setup Required

None.

---

## Self-Check: PASSED

Created files verified present on disk:

- `FOUND: .planning/v1.33/sweep-outcome-record.md`
- `FOUND: .planning/v1.33/CITATIONS-STALE.md`
- `FOUND: .planning/phases/154-…/154-12-SUMMARY.md` (this file)
- `FOUND: .planning/v1.33/baseline-pre-sweep.md` (held uncommitted since plan 01; committed here)

Commits verified present in git:

- `FOUND: 2ad5b32` — `git -C firestarter rev-parse HEAD` = `2ad5b322a37ba4a88afd09cc946f5c4114e51483`
- `FOUND: bc9d592` — `git -C firestarter_app rev-parse HEAD` = `bc9d59293b9a08b16d6d7eb16eaf6c6f53e88e65`
- `FOUND: a6b46f8` — `wip/v1.33-size-reduction-survey-preserved`, intact

Gitlinks verified: `git ls-tree HEAD firestarter firestarter_app` reports
`2ad5b322a37ba4a88afd09cc946f5c4114e51483` and `bc9d59293b9a08b16d6d7eb16eaf6c6f53e88e65`,
each equal to its sub-repo's `HEAD` — meta no longer asserts a completion it does not point at.

Anchored counts re-verified: `git -C firestarter rev-list --count 8695ee52…..HEAD` = **1**;
`git -C firestarter_app rev-list --count 6bfa6453…..HEAD` = **1**. Both porcelain-clean; the app
repo's 7 pre-existing untracked entries still `??`.

Task verify blocks re-run at plan end: Task 1 (three-target cold build + the literal-token checks
+ the empty `milestones/` diff) — pass, with the `--assert-tokens-zero` leg reported at its
literal exit 1 and its 4 exempt-file violations named. Task 2 (row count, texts preserved,
reasons present, schema re-scan) — pass. Task 3 (marker literals + ≥1 swept path) — pass, 7 of 7
literals present. Task 4 (both porcelains, all three firmware CI legs, the F3 gates, the full
host suite) — pass, **1976 passed / 0 failed / 0 skipped**.
