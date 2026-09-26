# 138-BASELINE: Phase 138 Pre-Change Baseline — PREP-03 / PREP-04

**Owner requirements:** PREP-03 (pre-change golden-trace/flash-RAM/suite-count baseline) and PREP-04
(live pulse-width distribution), both discharged **here**, by this plan (138-07), citing the five
per-plan artifacts Plans 01 through 06 produced. **Status:** CI evidence obtained — the operator
pushed all three v1.31 branches and dispatched the app's `Host CI` workflow; every measurement below
cites its owning artifact by filename and section.

This document copies `131-CI-BASELINE.md`'s nine-section narrative shape (see that file for the
precedent), adapted to a multi-repo, multi-source phase baseline, plus a tenth **Hand-off** section
(Task 3).

---

## 1. The runs

Two outward actions occurred, both taken by the **operator**, per Task 1's `checkpoint:human-action`
gate: pushing `gsd/v1.31-27c-programming-algorithm-fidelity` to `origin` in all three repos, and
dispatching `firestarter_app`'s `ci.yml` (`Host CI`) against that branch. The operator's Task 1 reply,
quoted verbatim: *"The operator authorized the orchestrator to perform the pushes and the dispatch on
their behalf. All three branches are pushed and all three CI runs are complete and green. Response:
pushed and dispatched."* No agent ran `git push`, `gh workflow run`, `gh pr create`, `gh pr merge` or
`git merge` at any point in this plan. Every command in this section, in §2, and in §8's re-verification
is a read-only `gh run view`, `gh run list`, or `git ls-remote` call, re-run independently by this plan
rather than accepted from the orchestrator's gate-clearance evidence on trust alone.

**`henols/firestarter` — two runs fired by the single push** (see §1a for why this is two, not one):

| Field | Run A | Run B |
|---|---|---|
| Run id | `31299694430` | `31299694466` |
| Workflow | `Firestarter CI` (`build.yml`) | `PY32F071 firmware` (`py32f071.yml`) |
| URL | https://github.com/henols/firestarter/actions/runs/31299694430 | https://github.com/henols/firestarter/actions/runs/31299694466 |
| Event | `push` | `push` |
| Head branch | `gsd/v1.31-27c-programming-algorithm-fidelity` | `gsd/v1.31-27c-programming-algorithm-fidelity` |
| Head SHA | `fb7949c0bdd575177262a76af506cec3b73ea28b` | `fb7949c0bdd575177262a76af506cec3b73ea28b` |
| Created | `2026-08-09T06:48:12Z` | `2026-08-09T06:48:12Z` |
| Conclusion | `success` (terminal) | `success` (terminal) |

**`henols/firestarter_app` — one run, dispatch-produced (see §1a for why the push itself fired none):**

| Field | Value |
|---|---|
| Run id | `31300205900` |
| Workflow | `Host CI` (`ci.yml`) |
| URL | https://github.com/henols/firestarter_app/actions/runs/31300205900 |
| Event | `workflow_dispatch` |
| Head branch | `gsd/v1.31-27c-programming-algorithm-fidelity` |
| Head SHA | `4d18b645ab18a2d2465f0f623062e9249eb24132` |
| Created | `2026-08-09T07:01:43Z` |
| Conclusion | `success` (terminal) |

All three rows were independently re-verified by this plan via
`gh run view <id> --repo <repo> --json event,headBranch,headSha,conclusion,url,createdAt,workflowName`
— the ids, branches, SHAs, and conclusions returned match the orchestrator's Task-1 gate-clearance
evidence exactly; nothing above was copied from that evidence without a fresh read.

**Production method, stated per repo, no implied symmetry:** the firmware's two runs are
**push-produced** — `build.yml` and `py32f071.yml` both carry a push trigger and neither carries
`workflow_dispatch` restricted enough to matter here (see §1a); a push is the *only* route to a
firmware CI run for either workflow. The app's one run is **dispatch-produced** — `ci.yml` does carry
`workflow_dispatch`, and (per §1a Correction 2) the push route produced **zero** runs for this
particular branch, making the dispatch the only route that actually worked this time. **Neither
firmware gate runs in CI**: `check_size_baseline.py` and `check_build_warnings.py` are local-run
obligations (§5 below is what discharges them), and nothing in `build.yml` or `py32f071.yml` invokes
either script against the live tree — `build.yml`'s own `pytest tests/ -v` step tests the checkers
*against fixtures*, not the checkers *against this branch's build output*. A CI run recorded in this
section cannot substitute for §5's cold local measurement, and this document does not imply otherwise.

**What these three runs are *not*:** none has `headBranch: beta` — `git ls-remote --heads origin beta`
in both submodules (re-run this plan, §8 below) returns `6fab4eafdcd0981d24fddc3ff177abc5c74e313c`
(firmware) and `4d18b645ab18a2d2465f0f623062e9249eb24132` (app), byte-identical to
`138-BRANCH-BASES.md` §3's recorded tips — **`beta` moved in neither repo as a result of anything in
this plan, and no pre-release was cut.** None of the three is `131-CI-BASELINE.md`'s prior app run
`30822281624` — a different phase, a different milestone, a different repo state — named here only for
contrast with this document's own shape, never reused as evidence.

### 1a. Two empirical corrections to `138-RESEARCH.md`'s CI Evidence (D-06) trigger table

**Correction 1 — the firmware repo fires TWO push-triggered workflows, not one.**
`138-RESEARCH.md`'s own "CI Evidence (D-06)" table names exactly two `firestarter` workflows,
`build.yml` (`Firestarter CI`) and `beta-build.yml` — it does not enumerate `py32f071.yml` at all.
`gh run list --repo henols/firestarter --branch gsd/v1.31-27c-programming-algorithm-fidelity
--json databaseId,event,headSha,conclusion,workflowName,createdAt` (re-run this plan) returns
**exactly two** runs, both `push`-triggered at the identical `headSha` and `createdAt`: `31299694430`
(`Firestarter CI`) and `31299694466` (`PY32F071 firmware`). Read live,
`/workspaces/firestarter/.github/workflows/py32f071.yml:27-28` carries `push: branches: ['**']` with
**no path filter on the push trigger itself** (a `paths:` filter exists only on its separate
`pull_request` trigger, lines 29-35) — so it fires on every branch push exactly as `build.yml` does,
independently. `138-RESEARCH.md`'s trigger table is **incomplete for the one workflow it omits, not
wrong about the one it names** — `build.yml`'s own row is accurate. This document's §1 table above is
the corrected, complete two-workflow record for a firmware push; `138-RESEARCH.md` itself is left
unedited, per this project's standing convention of appending a correction in a later, citing document
rather than rewriting a prior research artifact in place. Carried forward as **F-138-10** (§7).

**Correction 2 — the app repo's push fired NO run at all, despite `ci.yml` carrying
`push: branches: ['**']`.** `gh run list --repo henols/firestarter_app --branch
gsd/v1.31-27c-programming-algorithm-fidelity --json databaseId,event,headSha,conclusion,workflowName,createdAt`
(re-run this plan) returns **exactly one** run total for this branch — the `workflow_dispatch` run
`31300205900` — with **no** `push`-triggered run anywhere in the list, confirmed both by the
orchestrator's pre-dispatch `gh run list` (empty) and by this plan's own post-dispatch re-run (still
only the one dispatch-produced run). Mechanism, read live from
`firestarter_app/.github/workflows/ci.yml:16-23`: the push trigger carries `paths-ignore`
(`**.md`, `.gitignore`, `docs/**`) alongside `branches: ['**']`, but the branch itself was created by
the operator's push pointing at the **existing** `beta` tip (`4d18b645…`) with **zero new commits** on
top of it. A GitHub push event that introduces no new commits computes no changed-file list for
`paths-ignore` to evaluate — so no run is queued, not because the (nonexistent) changed paths matched
an ignore rule, but because there were no changed paths to evaluate at all. `138-RESEARCH.md`'s own
table states plainly that `ci.yml` **is** `workflow_dispatch`-able ("the shape `131-CI-BASELINE.md`
recorded") but frames that fact only as a *convenience*, not as the *only working route* for a
zero-diff branch creation — this section is what turns that from an assumption into an empirically
confirmed mechanism. Carried forward as **F-138-11** (§7).

Neither correction changes §1's evidence itself — the app run is legitimately dispatch-produced and
both firmware runs are legitimately push-produced, exactly as recorded above. They correct only the
*completeness* of the trigger table this plan's own `<read_first>` cited, and are restated in §8's
divergence table.

---

## 2. Fail-closed preconditions, re-verified before writing this file

All eighteen checks below (six per run, three runs) were read from three separate
`gh run view <id> --repo <repo> --json event,headBranch,headSha,conclusion,url,createdAt,workflowName`
calls — the same three calls reproduced in §1. **Terminality is keyed on `conclusion` throughout this
document, never on `outcome`** — in the GitHub Actions API, `outcome` is a step-level, pre-`continue-on-error`
result that can read a still-running or error-suppressed run as final, while `conclusion` is the run's
own terminal field; this is the only sentence in this document where the word `outcome` appears. No
condition below failed.

**Run `31299694430` (`Firestarter CI`, push, firmware):**
- run id is numeric — pass
- `gh run view` resolves it — pass
- `event` is `push` (the expected trigger — `build.yml` has no `workflow_dispatch`) — pass
- `headBranch` is `gsd/v1.31-27c-programming-algorithm-fidelity` — pass
- `headSha` begins `fb7949c0` (the pushed firmware tip, §1 and §8) — pass
- `conclusion` is terminal and non-null: `success` — pass

**Run `31299694466` (`PY32F071 firmware`, push, firmware):**
- run id is numeric — pass
- `gh run view` resolves it — pass
- `event` is `push` (the trigger that actually fired this run, per §1a) — pass
- `headBranch` is `gsd/v1.31-27c-programming-algorithm-fidelity` — pass
- `headSha` begins `fb7949c0` — pass
- `conclusion` is terminal and non-null: `success` — pass

**Run `31300205900` (`Host CI`, workflow_dispatch, app):**
- run id is numeric — pass
- `gh run view` resolves it — pass
- `event` is `workflow_dispatch` (the expected trigger — `ci.yml` has one, and per §1a Correction 2
  the push route produced no run for this branch) — pass
- `headBranch` is `gsd/v1.31-27c-programming-algorithm-fidelity` — pass
- `headSha` begins `4d18b645` (the app's fork base / live `beta` tip, §3 below) — pass
- `conclusion` is terminal and non-null: `success` — pass

---

## 3. Branch bases

The three verified bases (cited from `138-BRANCH-BASES.md` §4):

| Repo | Branch | Base commit (full SHA) |
|---|---|---|
| meta (`/workspaces`) | `gsd/v1.31-27c-programming-algorithm-fidelity` | `d0f0c6a056efaa3537909d8ff90492f3792403f1` |
| `firestarter` | `gsd/v1.31-27c-programming-algorithm-fidelity` | `30850845f9c0994706f28d2a74fccc3adbb4b387` (`3085084`) |
| `firestarter_app` | `gsd/v1.31-27c-programming-algorithm-fidelity` | `4d18b645ab18a2d2465f0f623062e9249eb24132` |

**PREP-01 verdict, one paragraph, citing F-138-01** (`138-BRANCH-BASES.md` §2): PREP-01 is discharged
as **content equivalence, not ancestry**. A GitHub squash merge (PR **#44**, single-parent commit
`568e58b`) makes `git merge-base --is-ancestor` a structural false negative — the squash commit's only
parent is `beta`'s pre-merge tip, so none of the 85 source-branch commits are its ancestors, even
though their content is present. An empty forward `comm -23` over both branches' `git ls-tree`
listings is the load-bearing proof: zero files on the v1.30 app branch are absent from `beta`. No
re-merge occurred, and `git merge-tree` proves one would conflict
(`tests/test_chip_test_sdp_leg.py`, added independently on both sides with different blobs) — so none
is required either.

---

## 4. The frozen trace

**Fixture:** `firestarter/test/native/avr/_shared/eprom_v131_expected.h`, committed blob SHA
`ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` (cited from `138-03-TRACE-CAPTURE.md` §8, the Plan 05 Freeze
record appended to that same file).

**Three frozen arrays:**

| Array | Chip / pinout | Entries | strobe_count() | timing_count() | % of 512 cap |
|---|---|---|---|---|---|
| `EPROM_V131_TRACE_PROTO_07` | AM27C512 / DIP28_27512 | **198** | 142 | 56 | 38.7% |
| `EPROM_V131_TRACE_PROTO_08` | AM27C020 / DIP32_27C020 | **221** | 157 | 64 | 43.2% |
| `EPROM_V131_TRACE_PROTO_0B` | AM2716 / DIP24_2716 | **201** | 142 | 59 | 39.3% |

(cited from `138-03-TRACE-CAPTURE.md` §2). All three are comfortably below the plan's own 60% ceiling,
and both `HOST_STUBS_MAX_STROBES`/`HOST_STUBS_MAX_TIMINGS` are pinned at 512 entries each
(`firestarter/test/native/avr/_shared/host_stubs_common.inc`) — the recorder headroom this baseline
inherits. Each protocol converges in exactly 3 passes (`138-03-TRACE-CAPTURE.md` §2), and the adaptive
pulse-growth formula (`pulse_delay = org_delay + org_delay*retries/20`) is directly visible in the
timing stream (100/105/110 µs for `0x07`/`0x08`; 500/525/550 µs for `0x0B`).

**Two independent mechanisms pin the fixture** (D-04, `138-03-TRACE-CAPTURE.md` §8 / `138-05-SUMMARY.md`):
(a) the fixture's own committed blob SHA compared against the inventory's recorded `blob_sha`
(`test_blob_sha_matches_the_recorded_inventory`, reads `git rev-parse HEAD:<path>` — the **committed**
blob, never the live file), and (b) the per-array name/entry-count and consumer-inclusion checks
against `firestarter/tests/golden/eprom_v131_trace_inventory.json`, read by the parallel six-assertion
gate `firestarter/tests/test_golden_trace_identity_eprom_v131.py`. Both mechanisms were independently
proven non-vacuous by three distinct planted breaks (blob SHA, inventory entry count,
consumer-inclusion), each observed RED on exactly one leg while the other five stayed green, then
cleanly restored (`138-03-TRACE-CAPTURE.md` §8's break-class table) — a change to either mechanism
alone is visible.

**Consumer:** Phase 144 / TEST-06 diffs the *new* (post-v1.31) trace against this frozen one. A future
divergence there is **expected work** — the pulse cadence legitimately changes under v1.31 — **not
evidence of a regression.**

---

## 5. Size and suite counts

**AVR flash/RAM, cold** (`138-06-FIRMWARE-MEASUREMENT.md` §2, measured tree `67d60615ed4449e55352746d7cc7b2c1af999368`):

| Target | Flash used / total / free | RAM used / total / free |
|---|---|---|
| `uno` | 23954 / 32256 / 8302 | 1573 / 2048 / 475 |
| `uno328pb` | 24004 / 32384 / 8380 | 1579 / 2048 / 469 |
| `leonardo` | 26016 / 28672 / 2656 | 2014 / 2560 / 546 |

All three are byte-identical to the live `size_baseline.json`'s own recorded figures — positive
evidence that the trace/timing instrumentation (Plans 03/05) is invisible to every AVR target, since
AVR builds exclude `test/`.

**Four-env native suite counts, cold** (`138-06-FIRMWARE-MEASUREMENT.md` §3):

| Env | Cases | Succeeded | Suites | All PASSED |
|---|---|---|---|---|
| `native` | 141 | 141 | 17 | yes |
| `native_nodevtools` | 141 | 141 | 17 | yes |
| `native_pinmap_provisional` | 10 | 10 | 1 | yes |
| `native_trace_v131` | 5 | 5 | 1 | yes |

The two **pinned** envs (`native`, `native_nodevtools`) hold at exactly 141/17 with the new
`HOST_STUBS_RECORD_TIMING` guard present but undefined — the behavioural flag-off proof.

**Warning watermarks, cold** (`138-06-FIRMWARE-MEASUREMENT.md` §4):

| Env | macro_redefinition | total | Watermark / policy | State |
|---|---|---|---|---|
| `uno` / `uno328pb` / `leonardo` | 0 | 0 | `== 0` | matches |
| `native` | 1166 | 1166 | `<= 1166` | matches exactly, no headroom |
| `native_nodevtools` | 1166 | 1166 | `<= 1166` | matches exactly |
| `native_pinmap_provisional` | 138 | 138 | `<= 138` | matches exactly |
| `native_trace_v131` | 140 | 140 | not in either live baseline | recorded only — see F-138-05 |

**Verbatim live-gate verdicts** (`138-06-FIRMWARE-MEASUREMENT.md` §5, all against the live,
un-rewritten `scripts/baseline/size_baseline.json` — the default seam, not the new freeze):
- `check_size_baseline.py` default seam (3 AVR logs + `native` + `native_nodevtools`): `PASS`, exit `0`.
  Supplementary run adding `native_pinmap_provisional`: `PASS`, exit `0`.
- `check_size_baseline.py --policy merge05` against BASE-01: `PASS`, exit `0` — `uno` +22/64 B (42 B
  headroom), `uno328pb` +28/64 B (36 B headroom), `leonardo` −56/0 B (36 B shrink margin under the
  must-not-grow ceiling). **This measured tree's own headroom** — smaller at the live `beta` tip, per
  F-138-02/F-138-04.
- `check_build_warnings.py` (`native`/`native_nodevtools`): `PASS`, exit `0`, both `== 1166`.
  Supplementary run adding `native_pinmap_provisional`: `PASS`, exit `0`, `== 138`. AVR envs:
  `PASS`, exit `0`, `macro_redefinition == 0` on all three.

**Firmware python gate suite** (`138-06-FIRMWARE-MEASUREMENT.md` §6, run **in place** inside
`/workspaces/firestarter`): `python3 -m pytest tests/ -q` → **227 passed, 0 failed, 0 skipped**
(221 pre-existing + 6 new from `test_golden_trace_identity_eprom_v131.py`).

**Host suite, CI-parity interpreter** (`138-04-HOST-BASELINE.md` §3, measured **in place** inside
`/workspaces/firestarter_app`, commit `4d18b645ab18a2d2465f0f623062e9249eb24132`, interpreter
`.venv/ci-replica/bin/python`, version `3.11.15`):
`.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` → **1539 collected, 1539 passed,
0 skipped, 0 failed, 1 warning, 180.89s**. Snapshot tests: `30 snapshots passed`.

---

## 6. The pulse distribution

Cited from `138-02-PULSE-DISTRIBUTION.md` (Runs 2/3, which agree exactly except for their provenance
line) — the live per-protocol `pulse_duration` distribution re-derived from the shipped
`chip_database.json` via the production parser (`firestarter.database._parse_pulse_duration`, never
reimplemented), blob SHA `ebd1eaac01698f64dc0861f8478b8931493d3bab`:

| Protocol | n | Modal value | Modal share | Distinct values |
|---|---|---|---|---|
| `0x07` | 170 | 100 µs (×113) | 66.5% | 5 |
| `0x08` | 127 | 100 µs (×104) | 81.9% | 6 |
| `0x0B` | 32 | 500 µs (×21) | 65.6% | 3 |

**Whole-database partition:** 329 chips on `{0x07,0x08,0x0B}` + 417 chips on every other protocol =
**746** total chips scanned, with **zero** crossover in either direction (a target-protocol id leaking
into "other," or an entry misfiled into the wrong target bucket). All six D-11 raw-string buckets
(`absent`, `non-string`, `empty`, `algorithm-controlled`, `unparseable`, `explicit-zero`) measure zero
for all three protocols on the real shipped database — a self-tested finding, not an unverified
absence: the script was observed to **fail**, for an attributable reason, against a deliberately
planted single-protocol synthetic database before its passing runs against the real data were trusted
(`138-02-PULSE-DISTRIBUTION.md` Run 1).

**Consumer:** Phase 139 / ISSUE-01 quotes this table's underlying verbatim script output directly into
a public GitHub comment on gh#15, as C2's evidence that pulse width is data, not a per-protocol
constant.

---

## 7. Findings register

Every finding raised anywhere in Phase 138, with a named owner and a disposition. Every disposition
below is **recorded, not fixed** (D-07), except F-138-01 and F-138-09/F-138-10/F-138-11, which are
adjudications or documentation-completeness notes rather than defects.

| ID | Mechanism | Owner | Disposition |
|---|---|---|---|
| F-138-01 | GitHub squash merge makes `--is-ancestor` a structural false negative; PREP-01 discharged via four-oracle content equivalence instead of ancestry | n/a (adjudication) | Recorded in `138-BRANCH-BASES.md` §2; requirement wording corrected in place; no re-merge performed or needed. |
| F-138-02 | Firmware `beta` drifted 2 commits ahead of the decided fork base (`b1737b2`, uniform +34 B flash on all three AVR targets); MERGE-05 uno-class headroom down to 8 B (`uno`) / 2 B (`uno328pb`) at the live tip | Phase 144/TEST-08 (delta reconciliation); Phase 143/144 (headroom); henols (escalation if exhausted) | Recorded, not fixed. This baseline's measured tree (`67d6061`) forks from the clean, undrifted base, not the drifted live tip. |
| F-138-03 | Meta submodule gitlinks (`firestarter`, `firestarter_app`) deliberately not advanced to the v1.31 checkouts | henols | Recorded, not fixed (OD-3); the three base commits are named in `138-BRANCH-BASES.md` §4 and this document's §3 instead. |
| F-138-04 | `check_size_baseline.py`'s verdict is base-dependent: exit 0 (GREEN) at the decided fork base `3085084`→`67d6061`, exit 1 (RED) at the live `beta` tip `6fab4ea` (+34 B uniform, `b1737b2`) | Phase 144/TEST-08; Phase 143/144; henols | Recorded, not fixed (D-07). This document's §5 stands on the GREEN reading deliberately — Phase 138 exists to define "before," and a broken reference base would make every downstream delta unattributable. |
| F-138-05 | `check_size_baseline.py`'s `compare_native` raises an uncaught `KeyError` (exit 1, the *regression* code) rather than exit 2 (the *configuration-error* code) for an env absent from the baseline; `NATIVE_ENVS` is hardcoded and `--rebuild` never reaches `native_pinmap_provisional`/`native_trace_v131` | henols; candidate consumer Phase 144 | Recorded, not fixed (D-07). `native_trace_v131`'s own counts are recorded directly in `size_baseline_v131.json`, never passed to either live gate for a real pass/fail evaluation. |
| F-138-06 | `host_stubs_common.inc`'s pre-existing strobe-recorder block comment claims composability with `HOST_STUBS_RECORD_BUS` the actual `#ifdef`/`#elif` structure does not provide, and understates the pinned suite count (states 14, real count is 17) | henols | Recorded, not fixed — the old comment's byte-level stability is load-bearing for the 17 dependent suites; the correction lives in `138-03-TRACE-CAPTURE.md` §6 and in this plan's own new block's (correct) comment, not by rewriting the old one. |
| F-138-07 | `firestarter_app/tools/gen_sdp_bus_config.py` emits only 5 rows (all `0x0D`) and its `validate_rows` rejects any pinout carrying `static-high-pins`, which `DIP24_2716` (AM2716, protocol `0x0B`) has | henols | Recorded, not fixed — this phase derived the three trace `bus_config` rows through the generator's own `derive_row` function directly (§4) instead of extending its emission surface, which two frozen SDP suites already consume. |
| F-138-08 | The captured write-path trace shows no `CTRL_VPP_REGULATOR_ENABLE` clear anywhere on the converged success path, for any of the three protocols — `eprom_write_execute`'s VPP-regulator disable sits only on the retry-exhausted failure path | Phase 142 / VPP-03 | Applies; recorded, not fixed — Phase 138's fence forbids editing `eprom.cpp`. |
| F-138-09 | Reserved, conditional finding for an outstanding CI-evidence gap, for the case the operator held the push/dispatch | n/a | **Does not apply.** The operator pushed and dispatched (Task 1's `pushed and dispatched` reply, §1); all three runs are recorded with a non-null `conclusion`. No gap exists to own. |
| F-138-10 | `138-RESEARCH.md`'s CI Evidence (D-06) trigger table names only `build.yml`/`beta-build.yml` for the firmware repo; a second workflow, `py32f071.yml`, also carries an unfiltered `push: branches: ['**']` and fired alongside `build.yml` on the same push | henols (documentation completeness — not a defect in the workflow itself) | Recorded here (§1a); `138-RESEARCH.md` is left unedited per this project's standing convention — this document is the corrected, complete record for future citation. |
| F-138-11 | `firestarter_app`'s `ci.yml` push trigger produced zero runs for the v1.31 branch despite `push: branches: ['**']`, because the branch was created pointing at the existing `beta` tip with zero new commits, leaving no changed-files list for `paths-ignore` to evaluate | henols (mechanism confirmation — not a defect) | Recorded here (§1a) as an empirically confirmed mechanism, not merely an assumed one; `workflow_dispatch` is confirmed as the only route to an app CI run for a zero-diff branch push. |

---

## 8. Divergence check against research

Re-verification commands re-run by this plan: `git -C /workspaces/firestarter ls-remote --heads origin
beta` → `6fab4eafdcd0981d24fddc3ff177abc5c74e313c`; `git -C /workspaces/firestarter_app ls-remote
--heads origin beta` → `4d18b645ab18a2d2465f0f623062e9249eb24132`; both byte-identical to
`138-BRANCH-BASES.md` §3's recorded tips — **`beta` moved in neither repo across this entire phase.**

| Figure class | This phase's measured figure | `138-RESEARCH.md`'s recorded figure | Result |
|---|---|---|---|
| Firmware `beta` tip | `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` | same | Agree — no divergence |
| App `beta` tip | `4d18b645ab18a2d2465f0f623062e9249eb24132` (`3.0.0b20`) | same | Agree — no divergence |
| AVR sizes @ fork base `3085084`→`67d6061` | uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014 | Identical figures, `138-RESEARCH.md`'s "Measured Baseline (this session)" row | Agree — zero divergence |
| Native suite counts (pinned envs) | `native`/`native_nodevtools` both 141 cases / 17 suites | Identical | Agree — zero divergence |
| Host suite pass/skip split @ commit `4d18b64` | **1539 passed / 0 skipped**, measured in place in `/workspaces/firestarter_app` (`138-04-HOST-BASELINE.md` §3) | **1493 passed / 46 skipped**, measured in a directory named `app_beta_live` | **DIVERGES.** Collected totals agree exactly (1539 = 1539); the passed/skipped split does not. **The measured number (1539/0, this phase's own in-place figure) wins, and both values stand, unreconciled.** `138-04-HOST-BASELINE.md` §7's own offered (explicitly unconfirmed) mechanism — a differently-named checkout defeating the `requires_fw` sibling-repo marker — is repeated here for context, not as a correction to either figure. |
| Pulse distribution (`0x07`/`0x08`/`0x0B`) | n=170/127/32, histograms exactly as `138-02-PULSE-DISTRIBUTION.md` §"Reconciliation" | Identical, per the seed's C2 table and `138-RESEARCH.md` | Agree — zero divergence |
| CI trigger table, firmware push | **Two** push-triggered workflows fire (`build.yml` + `py32f071.yml`) | Names only `build.yml`/`beta-build.yml` | **DIVERGES (completeness, not a wrong value) — F-138-10.** This document's §1 is the corrected, complete record. |
| CI trigger table, app push route | App push produces **zero** runs for a zero-new-commit branch creation | States `ci.yml` carries `push: branches: ['**']` but does not state the zero-diff-branch no-run behavior | **DIVERGES (an unstated mechanism, now empirically confirmed) — F-138-11.** |

**The rule, stated explicitly, verbatim:** where a figure measured in this phase differs from a figure
`138-RESEARCH.md` recorded, **the measured number wins and both are recorded without reconciliation.**
No figure in this document was adjusted, rounded, or silently reconciled to make two sources agree —
including the 1539-vs-1493 host-suite split and both CI-trigger-table completeness corrections.

---

## 9. What this baseline is — and is not

**This baseline IS** the pre-change input Phases 139, 144 and 146 cite: TEST-06 diffs the new
(post-v1.31) golden trace against §4's frozen fixture; TEST-08 measures its flash/RAM/suite-count delta
against §5's figures and `firestarter/scripts/baseline/size_baseline_v131.json`; ISSUE-01 quotes §6's
pulse distribution verbatim into the gh#15 public comment; Phase 146's honesty ledger inherits §7's
findings register whole.

**This baseline is NOT:**
- **Not a claim that CI is broadly green.** The three runs in §1 succeeded; that says nothing about any
  other workflow, any other branch, or CI health project-wide — `beta-build.yml` and
  `beta-release.yml` were not dispatched by this phase and carry no run id in this document.
- **Not a claim of datasheet conformance of any kind.** No datasheet was consulted anywhere in this
  document — §6's pulse distribution measures what the shipped database **contains**, not what any
  datasheet prescribes; §4's trace measures what the current, pre-change code **does**, not what it
  should do.
- **Not a repair of any gate.** `check_size_baseline.py`, `check_build_warnings.py`,
  `gen_sdp_bus_config.py`, and `host_stubs_common.inc`'s stale block comment are all left exactly as
  found — F-138-04 through F-138-07 are recorded, none is fixed.
- **Not a measurement of any tree other than the SHAs this document names:** meta
  `b6aa1dcb23ef9931105752ed6dd6badccf6719de` (post-push tip), firmware `fb7949c0bdd575177262a76af506cec3b73ea28b`
  (pushed tip; the size/native/trace figures in §4-§5 were measured at `67d60615ed4449e55352746d7cc7b2c1af999368`,
  four instrumentation-only commits ahead of the fork base `30850845f9c0994706f28d2a74fccc3adbb4b387`
  the size gate's GREEN reading stands on), app `4d18b645ab18a2d2465f0f623062e9249eb24132`. The live
  `beta` tip's own flash/RAM figures (F-138-02/F-138-04) are quoted from `138-RESEARCH.md`, explicitly
  labelled research-measured, and were not rebuilt by this phase.
- **Not evidence about silicon behaviour.** Nothing in this document touches bench hardware, the
  ~6.25 V program-VCC evidence ceiling, or any physical chip.

**What this baseline does not establish — stated as plainly as what it does:**
1. **Nothing about bench hardware.** No chip was programmed, read, or blank-checked by anything in
   this phase.
2. **Nothing about the new (post-v1.31) write-loop cadence.** Phase 144 authors and reviews that
   trace; this document freezes only the pre-change one (§4).
3. **Nothing about the live firmware `beta` tip beyond what F-138-02 and F-138-04 carry** — both
   explicitly labelled research-measured, neither rebuilt by this phase.
4. **Nothing about the host suite's behaviour under Python 3.9**, the lowest interpreter
   `firestarter_app`'s CI matrix supports — §5's host figures are measured only under the CI-parity
   interpreter, 3.11.15.
5. **No reconciliation of the 1539-vs-1493 host-suite divergence (§8).** Both figures stand,
   attributed to their own command and location, by design — not resolved here.

---

## 10. Hand-off

What each downstream phase consumes from this document, by exact artifact:

| Downstream | Consumes |
|---|---|
| **Phase 139 / ISSUE-01** | §6's pulse-distribution table and, through it, `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md`'s verbatim script output — quoted directly into the public gh#15 comment as C2's evidence. |
| **Phase 143 / 144** | §7's **F-138-02** — the MERGE-05 uno-class headroom warning (8 B `uno` / 2 B `uno328pb` remaining at the live `beta` tip before the band fails). |
| **Phase 144 / TEST-06** | §4's frozen fixture path (`firestarter/test/native/avr/_shared/eprom_v131_expected.h`), its committed blob SHA (`ca3e09f164e6e1c541ecb63d15bbebf5bce41d70`), and its two-mechanism identity gate (`firestarter/tests/test_golden_trace_identity_eprom_v131.py` + `firestarter/tests/golden/eprom_v131_trace_inventory.json`) — the diff target for the new (post-v1.31) trace. |
| **Phase 144 / TEST-08** | `firestarter/scripts/baseline/size_baseline_v131.json`, read through `check_size_baseline.py`'s/`check_build_warnings.py`'s existing `--baseline` seam (never the default `FIRESTARTER_SIZE_BASELINE` seam, which stays pointed at the live, unmodified `size_baseline.json`) — §5's AVR/native/warning figures are that file's contents. |
| **Phase 146** | §7's whole findings register (F-138-01 through F-138-11), each already carrying an owner and a recorded-not-fixed disposition, for the honesty ledger to inherit without re-deriving. |

**The three branch names and bases, restated:** all three repos carry the identical slug
`gsd/v1.31-27c-programming-algorithm-fidelity` (D-09) — meta off `d0f0c6a056efaa3537909d8ff90492f3792403f1`,
firmware off `30850845f9c0994706f28d2a74fccc3adbb4b387` (the decided, undrifted fork base — §3), app off
`4d18b645ab18a2d2465f0f623062e9249eb24132` (the live post-merge `beta` tip at the time PREP-02 was
adjudicated). All three are now also pushed to `origin` (§1) at their respective current tips: meta
`b6aa1dcb23ef9931105752ed6dd6badccf6719de`, firmware `fb7949c0bdd575177262a76af506cec3b73ea28b`
(carrying `size_baseline_v131.json` on top of the `67d6061` measured tree), app
`4d18b645ab18a2d2465f0f623062e9249eb24132` (unchanged — no new app commit this phase).

**The app worktree is left checked out on its v1.31 branch** (`gsd/v1.31-27c-programming-algorithm-fidelity`,
at `4d18b645ab18a2d2465f0f623062e9249eb24132`), exactly as `138-04-HOST-BASELINE.md` §5 left it and as
later Wave 3 plans (Phase 143) expect it — no further branch setup is needed there.

---

*Phase: 138-preconditions-baseline — Plan 07, Task 2 (§§1-9) / Task 3 (§10)*
*Recorded: 2026-08-09, from three independently re-verified `gh run view` calls and two
`gh run list`/`git ls-remote` re-checks (this plan), and from the five per-plan artifacts
`138-BRANCH-BASES.md`, `138-02-PULSE-DISTRIBUTION.md`, `138-03-TRACE-CAPTURE.md`,
`138-04-HOST-BASELINE.md`, and `138-06-FIRMWARE-MEASUREMENT.md`.*
