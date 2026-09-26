# Phase 138: Preconditions & Baseline - Research

**Researched:** 2026-08-08
**Domain:** Git/GitHub branch-state verification · PlatformIO cold-build measurement · native Unity stub-layer instrumentation · frozen-fixture inventory gating · reproducible database re-derivation
**Confidence:** HIGH (nearly every load-bearing claim below was measured live this session, not recalled)

---

## Summary

This phase is a **measurement** phase, and the single most important research finding is that
**four of the branch/ancestry facts CONTEXT.md recorded as "verified during this discussion" are
now stale or wrong.** They were plausibly true when the discussion ran; they are not true now.
Every one was re-verified read-only this session:

1. **`firestarter_app`'s v1.30 PR was opened and merged.** PR **#44** (`gsd/v1.30-sdp-surface-retirement` → `beta`) is `MERGED`, `mergedAt 2026-08-05T21:13:01Z`, merge commit **`568e58b`** — a **squash** (single parent `16a313a`). `git merge-base --is-ancestor` exits 1 *because it was squashed*, not because the content is missing. **Zero files** exist on the v1.30 branch that are absent from `beta`. PREP-01's literal success criterion ("`--is-ancestor` exits 0") is therefore **not satisfiable without a redundant re-merge that provably conflicts** (`git merge-tree` shows `tests/test_chip_test_sdp_leg.py` *added in both* with different blobs).
2. **Both submodules' cached `origin/beta` refs are stale.** The firmware's live `beta` tip is **`6fab4ea`**, not `3085084` (2 commits ahead, one touching `src/firestarter.cpp` +37/−1). The app's live `beta` tip is **`4d18b64`** (`3.0.0b20`), not `04f63de`.
3. **`check_size_baseline.py` is GREEN at `3085084` and RED at the live beta tip.** Measured both ways: exit **0** at `3085084`; exit **1** at `6fab4ea` with `flash_used` **+34 B on all three AVR targets**. D-07's contingency fires — but not for the v1.23-era reason CONTEXT.md predicted.
4. **A local `beta` branch DOES exist in the firmware repo** (CONTEXT.md says it does not), and it is pinned at `3085084`. The app's local `beta` is at `25b7255`, **4+ commits behind** `origin/beta`.

The second most important finding is mechanical: **D-02's "third opt-in stub layer intercepting
`delay()`/`delayMicroseconds()`" cannot be built the way the other two recorder layers were built.**
`delay()` and `delayMicroseconds()` are *not* unstubbed — they are **free functions defined in
ArduinoFake's `FunctionFake.cpp`** that forward to a fakeit mock, and **every suite that reaches them
already mocks them** with `When(Method(ArduinoFake(), delay)).AlwaysReturn()`. A definition in
`host_stubs_common.inc` would be a duplicate-symbol link error. The only supported seam is fakeit's
`.AlwaysDo(lambda)` — a pattern already used in-repo with argument capture. This makes the flag-off
byte-exactness contract *trivially* satisfiable (nothing in the shared `.inc` changes for existing
suites) but relocates part of the layer into the new suite's `setUp()`.

The third finding is a hard blocker the plan must design around: **the pre-change 27C write loop
cannot be traced without also modelling chip read-back**, because `eprom_write_execute` runs up to
`NUMBER_OF_RETRIES = 20` full program+verify passes and the default stub `rurp_read_data_buffer()`
returns `0` — so any non-zero target byte never verifies and the 512-entry strobe recorder overflows
on the first fixture. There is a proven in-repo remedy (`h.firestarter_get_data = mock_get_data_keyed`).

**Primary recommendation:** Plan Phase 138 as **five independent measurement tracks** (branch-state
adjudication · firmware size/suite baseline · trace instrumentation + fixture · host suite baseline ·
pulse-distribution script), and make the *first* task of the branch track a **fail-closed
re-verification + finding-recording** task rather than a merge task — because the merge PREP-01
describes has already happened by another route and re-doing it would conflict. Every number in
§"Measured Baseline (this session)" below is directly reusable; the plan should re-measure and
compare rather than copy, but a divergence from these figures is itself a finding.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Golden-trace freeze (PREP-03)**

- **D-01:** Phase 138 **captures a real write-path trace fixture**, it does not merely record blob
  SHAs. Run the *current* (pre-change) program loop under the recording stub, dump the ordered
  register-write sequence, and commit it. This is the only option under which Phase 144's TEST-06
  criterion — "every changed strobe attributable to a named decision" — is reachable at all; a
  blob-SHA inventory proves file identity and would have left TEST-06 with nothing to diff.
  *Rejected:* blob-SHA inventory only; deferring capture to Phase 144.

- **D-02:** The capture **adds a timing layer**. A third opt-in stub layer intercepts `delay()` /
  `delayMicroseconds()` and interleaves timing entries into the ordered strobe stream.
  **Rationale — this is the crux of the phase.** Neither existing recorder can see time:
  `HOST_STUBS_RECORD_BUS` records `(reg, data)` pairs; `HOST_STUBS_REAL_REGISTER_UTILS` records
  ordered `(kind, pin, value)` strobes; `delay()` / `delayMicroseconds()` are not stubbed at all in
  `host_stubs_common.inc`. v1.31 changes pulse **width** and pulse **count** and adds an overprogram
  pulse — a register/strobe-only trace is blind to every one of those.
  *Rejected:* strobes-only with cadence proven solely by TEST-01 unit tests.

- **D-03:** The trace covers a **small synthetic block, all three protocols** (`0x07`, `0x08`,
  `0x0B`). The recorders cap at 256 (`RECORD_BUS`) / 512 (`REAL_REGISTER_UTILS`) entries, so a real
  512-byte block would overflow both immediately — the fixture must be a deliberately-chosen 4–8
  byte block. The bytes are **chosen, not arbitrary**: exercise an already-matching byte, an `0xFF`
  byte, and a byte needing multiple pulses. *Rejected:* `0x07`-only.

- **D-04:** The fixture is **immutable + gated by an inventory**. It lands under
  `firestarter/test/native/avr/_shared/` as a v1.31-frozen fixture, pinned by a committed inventory
  JSON under `firestarter/tests/golden/` read by a python gate — the exact `sdp_expected.h` +
  `sdp_expected_inventory.json` + `test_golden_trace_identity.py` triple already proven in this repo.
  *Rejected:* planning-artifact-only.

- **Hard constraint carried into planning:** the new stub layer must be **opt-IN** and flag-off must
  leave all pre-existing native suites **byte-exact**, per the Phase 116 D-05/D-07 precedent already
  documented in `host_stubs_common.inc`.

**Baseline form (PREP-03)**

- **D-05:** **Frozen JSON + planning record.** Re-measure **cold** at `beta` @ `3085084` and commit an
  immutable `firestarter/scripts/baseline/size_baseline_v131.json` alongside the existing BASE-01 —
  **never rewriting the live `size_baseline.json`**. Pair it with a `.planning/` narrative artifact in
  the style of `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md`.

- **D-06:** Evidence is **local cold measurement AND an operator-dispatched CI run** per repo. The
  agent takes cold local measurements and reads the CI runs **read-only**, recording run ids.
  **Cold-measurement procedure is not optional:** `rm -rf .pio/build/<env>` then a *single* `pio`
  invocation with an extended timeout. Never guess a figure down from prose or from a warm re-run.

- **D-07:** If re-measurement shows `check_size_baseline.py` is **already RED** — **record it, do not
  fix it.** Capture the discrepancy as a named finding with an explicit owner.
  *Rejected:* fixing it in Phase 138.

**Branch bases (PREP-01, PREP-02)**

- **D-08:** **PREP-01 runs as agent-opens-PR, operator-merges.** An agent opens the PR from the
  staged `.planning/v1.30-PR-BODY.md`; the operator reviews and merges; the phase then verifies with
  `git merge-base --is-ancestor`. **Known and accepted consequence:** `beta-release.yml` fires on
  **every** push to `beta` with no paths-ignore filter, so this merge **will cut a new app
  pre-release**. Planning must not treat the resulting version bump as an anomaly.

- **D-09:** All three repos use the **identical branch slug**:
  `gsd/v1.31-27c-programming-algorithm-fidelity` in meta, `firestarter`, and `firestarter_app` alike.
  *Rejected:* a shorter sub-repo slug.

**Pulse distribution (PREP-04)**

- **D-10:** PREP-04 ships as a **committed reproducible script** plus its committed output, following
  136.1's reproducible re-derivation pattern — not a one-off measurement pasted into markdown.
  *Rejected:* one-off measurement into a markdown artifact.

- **D-11:** The artifact must state **which layer it counts**. The database field is `pulse_duration`
  — a *string* like `"100 us"` — parsed into the integer-µs wire field `pulse-delay` by
  `_parse_pulse_duration` at `firestarter_app/firestarter/database.py:128`. REQUIREMENTS.md says
  `pulse_duration` and PROJECT.md says `pulse_delay`; **both are correct at different layers.**
  Absent / unparseable / zero values get their own explicit bucket rather than being silently dropped
  from the denominator.

### Claude's Discretion

- Where the PREP-04 script lives (`firestarter_app/tools/` vs the phase directory) — planner's call,
  subject to the project's "skills must own their scripts" rule where applicable.
- The exact synthetic byte pattern and block length for the trace fixture, within the 256/512 entry
  caps and D-03's three required cases.
- Plan sequencing and wave structure. Note the real dependency shape: PREP-01 gates only the **app**
  half of PREP-02; the firmware/meta halves of PREP-02, all of PREP-03's firmware measurement, and
  all of PREP-04 are independent of it and need not wait on the operator merge.

### Deferred Ideas (OUT OF SCOPE)

- **Repairing the (possibly RED) live `size_baseline.json`** — per D-07 this phase records the
  discrepancy and names an owner rather than fixing it.
- **Authoring the *new*-cadence trace** — Phase 138 freezes only the pre-change trace. TEST-06 in
  Phase 144 authors the new one and reviews the diff.
- All four keyword-matched todos (`prove-pio-dev-flag-fails-closed.md`, the VPP-skip todo,
  `at28c256-write-path-failure-gh20.md`, the `dev test` triage skill) — deliberately **not folded**.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim from REQUIREMENTS.md) | Research Support |
|----|--------------------------------------------|------------------|
| **PREP-01** | `firestarter_app`'s `gsd/v1.30-sdp-surface-retirement` is merged into `origin/beta` and the merge is verified (`git merge-base --is-ancestor` exits 0) before any v1.31 host work forks — v1.30 is recorded as shipped but its PR was staged and never opened. | §"Branch & Ancestry Ground Truth" — the PR **was** opened as #44 and **squash**-merged `568e58b`; `--is-ancestor` exits 1 by construction; content-equivalence is provable three independent ways; a re-merge conflicts. Requires an adjudication, not a merge. |
| **PREP-02** | Milestone branches exist in all three repos off their decided bases — firmware off `beta` @ `3085084`, app off the updated `beta`, meta off the v1.30 tip — each verified by naming the base commit, not assumed. | §"Branch & Ancestry Ground Truth" — meta branch already exists off `d0f0c6a0` (the real v1.30 tip) but is **unpushed with no upstream**; no `gsd/v1.31*` exists on any remote; `3085084` is **no longer** the firmware beta tip (`6fab4ea` is). |
| **PREP-03** | A pre-change baseline is committed **before** any `eprom.cpp` edit: the existing golden register traces frozen as a historical artifact, per-target flash/RAM usage, and full native + host suite counts. | §"Measured Baseline (this session)" gives every figure; §"Trace Capture Mechanism (D-02)" gives the instrumentation design; §"Frozen-Fixture Triple" gives the gate contract; §"Cold Measurement Protocol" gives the exact commands and the 540 000 ms timeout. |
| **PREP-04** | The live per-protocol `pulse_duration` distribution is re-derived from the shipped `chip_database.json` and committed as C2's evidence — measured in this milestone, not restated from the seed. | §"Pulse Distribution (PREP-04)" — measured live, reproduces the seed's C2 figures exactly; the DB blob is **identical on all four candidate trees**, so PREP-04 does **not** depend on PREP-01; all four D-11 buckets are empirically **zero** and that is itself the finding. |
</phase_requirements>

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| PREP-01 v1.30 landing adjudication | GitHub API (read-only) + local git plumbing | `.planning/` narrative record | The merge already happened server-side; only GitHub's PR record and git plumbing can distinguish "squash-merged" from "never merged". Nothing in either sub-repo's code is involved. |
| PREP-02 branch creation | Local git in each of 3 repos | Remote push (outward) | Branch creation is local; only the push is outward-facing. Meta's half is already done locally. |
| PREP-03 AVR flash/RAM | PlatformIO AVR toolchain (`pio run -e uno\|uno328pb\|leonardo`) | `scripts/check_size_baseline.py` gate | The linker is the only authority on flash/RAM. The gate turns the figure into an exit code. |
| PREP-03 native suite counts | PlatformIO native env (`pio test -e native…`) | `check_size_baseline.py` `compare_native` | Case/suite counts come only from `pio test` SUMMARY rows; nothing else emits them. |
| PREP-03 firmware python gates | `firestarter/tests/` pytest + **git history** | — | These gates walk git history; they are not runnable outside a real checkout (measured: 7 fail in a detached tree). |
| PREP-03 host suite counts | `firestarter_app` pytest under **py3.11** | CI `ci.yml` run (dispatchable) | The devcontainer's py3.12 is not the CI interpreter; the `.venv/ci-replica` py3.11.15 venv is the parity tier. |
| PREP-03 trace capture | Firmware **native test** tier (`test/native/avr/`) | `firestarter/tests/` python gate tier | Instrumentation belongs in `test/`, never in `src/`. The immutability gate belongs in the python tier because only python can read git blob SHAs. |
| PREP-04 pulse distribution | `firestarter_app` data tier (`chip_database.json` + `database.py`) | meta `.planning/` script + output | The datum and its parser both live in the app; the reproducible script and its committed output are planning artifacts written for a public audience. |
| Baseline narrative | meta `.planning/` | — | Human-citable prose belongs in the meta repo, mirroring `131-CI-BASELINE.md`. |

**Tier misassignment this map prevents:** putting the trace-capture timing hook in
`host_stubs_common.inc` (the shared *stub* tier) when the seam that actually exists is in the
per-suite *test* tier (fakeit `setUp()`). See §"Trace Capture Mechanism (D-02)".

---

## Branch & Ancestry Ground Truth

> Every row below was produced this session with **read-only** commands. No branch was created,
> switched, pushed, fetched or merged; no PR was opened.

### The v1.30 landing — PREP-01's real state

| Fact | Value | How verified |
|------|-------|--------------|
| PR **#44** `gsd/v1.30-sdp-surface-retirement` → `beta` | **`MERGED`**, `mergedAt 2026-08-05T21:13:01Z` | `gh pr view 44 --repo henols/firestarter_app --json state,mergedAt,mergeCommit` [VERIFIED: GitHub API] |
| Merge commit | **`568e58b`** — title `v1.30 — SDP Surface Retirement & Behavioral Lock Proof (#44)` | same |
| Merge style | **Squash** — `parents=[16a313a]`, single parent; body is the concatenated branch commit messages | `git log -1 --format='%h parents=[%p]' 568e58b` [VERIFIED] |
| `git merge-base --is-ancestor gsd/v1.30-… origin/beta` | **exit 1** | measured [VERIFIED] |
| `git rev-list --count origin/beta..gsd/v1.30-…` | **85** | measured [VERIFIED] |
| `git cherry origin/beta gsd/v1.30-…` | **85 `+`, 0 `-`** — patch-ids all differ (expected after a squash) | measured [VERIFIED] |
| Files present on the v1.30 branch and **absent** from `beta` | **none** (`comm -23` of both `git ls-tree -r --name-only` lists is empty) | measured [VERIFIED] |
| Files present on `beta` and absent from the branch | `tests/test_hw_revision_gate.py` (from PR #45) | measured [VERIFIED] |
| `git diff --stat gsd/v1.30-… origin/beta` | 12 files / +719 −207 — **all** attributable to beta's four later PRs (#45, #46, #48, #49) + the version bump | measured [VERIFIED] |
| Re-merge conflict risk | `git merge-tree` reports 3 overlaps: `firestarter/chip_test.py` and `tests/conftest.py` *changed in both*, **`tests/test_chip_test_sdp_leg.py` *added in both* with different blobs** — the last is always a conflict under git's default merge | measured [VERIFIED] |

**Consequence the plan must own:** PREP-01's stated criterion (`--is-ancestor` exits 0) is
unreachable without re-merging content that is already present, and that re-merge is *guaranteed* to
conflict. The honest discharge is a **content-equivalence adjudication** — three independent oracles
(GitHub PR state, empty `comm -23`, restricted `git diff`) — recorded as a named finding, with the
requirement's wording corrected rather than force-satisfied. D-08's "agent opens PR, operator
merges" is a **no-op** now; and its "known and accepted consequence" (a new pre-release) **already
happened** — `beta` is at `3.0.0b20` and four `Apply automatic changes` auto-commits sit on it.

### Live tips vs local caches (all three repos)

| Repo | Local cached `origin/beta` | **Live `beta` on GitHub** | Drift | Local `beta` branch |
|------|---------------------------|--------------------------|-------|---------------------|
| `firestarter` | `3085084` (fetch cache 2026-08-07 11:47) | **`6fab4ea`** | **2 ahead** | **exists**, at `3085084` |
| `firestarter_app` | `04f63de` (fetch cache 2026-08-07 17:55) | **`4d18b64`** (`3.0.0b20`) | **2 ahead** | exists, at `25b7255` (≥4 behind) |
| meta (`firestarter_prom`) | `origin/main` @ `8c586d4` | `8c586d4` | in sync | n/a |

Live tips read with `gh api repos/<owner>/<repo>/git/refs/heads/beta --jq '.object.sha'`
[VERIFIED: GitHub API].

**Firmware drift detail** (`gh api repos/henols/firestarter/compare/3085084...6fab4ea`):

| Commit | Message | Files |
|--------|---------|-------|
| `b1737b2` | `feat(protocol): carry HW revision + FW identity in the MSG_OK_READY ack (#49)` | `src/firestarter.cpp` **+37 −1** |
| `6fab4ea` | `Apply automatic changes` | `include/version.h` +1 −1 |

`src/firestarter.cpp` is AVR-compiled surface (it is *excluded* from every native env's
`build_src_filter`), so this drift moves AVR flash but **not** native suite counts. Measured:
**+34 B flash on all three targets, RAM unchanged** (§"Measured Baseline").

**App drift detail** (`04f63de...4d18b64`): `0e4b0e6` = PR #50
`fix(dev test): run blank-check after erase…` (+94 `firestarter/chip_test.py`, 4 test files,
+144 new `tests/test_chip_test_blank_check_order.py`), then `4d18b64` = version bump to `3.0.0b20`.

### v1.31 branch existence

| Repo | `gsd/v1.31-27c-programming-algorithm-fidelity` local | on remote | Fork base |
|------|------------------------------------------------------|-----------|-----------|
| meta | **exists**, HEAD `84727a74`, 8 commits ahead of base | **absent** (`git ls-remote --heads origin 'gsd/v1.31*'` empty) | **`d0f0c6a0`** = tip of `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof` — i.e. the real v1.30 tip [VERIFIED] |
| `firestarter` | absent | absent | — |
| `firestarter_app` | absent | absent | — |

Meta's v1.31 branch has **no upstream configured** (`git rev-parse --abbrev-ref @{u}` → fatal). Note
the meta repo carries **two** v1.30-named branches — `gsd/v1.30-sdp-surface-retirement` @ `00af5771`
(2026-08-03) and `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof` @ `d0f0c6a0` — and the
v1.31 branch descends from the **longer-named** one. This is exactly the divergence D-09 exists to
prevent recurring; PREP-02's "meta off the v1.30 tip" must name `d0f0c6a0`, not `00af5771`.

### Working-tree state (read-only observations, do not "fix" without a decision)

- The **app submodule worktree is checked out on `fix/dev-test-blank-check-after-erase` @ `7fe8dea`**
  — which is PR #50's head, now merged. It is **not** `beta` and **not** the v1.30 branch. Any host
  measurement taken in place, today, measures that third tree.
- The **firmware submodule worktree is on local `beta` @ `3085084`.**
- The **meta index's submodule gitlinks are stale**: `firestarter` → `0933bd7` (an older beta commit,
  2026-08-02) and `firestarter_app` → `cc036e8` (the v1.30 branch tip), against worktrees at
  `3085084` / `7fe8dea`. That is why `git status` shows `M firestarter` / `M firestarter_app`.
  Whether PREP-02 should advance these gitlinks is an **open question** (§Open Questions Q3).

---

## Measured Baseline (this session)

> These are real measurements, not targets. The plan should **re-measure** and treat any divergence
> as a finding. Toolchain: PlatformIO Core **6.1.19**, avr-gcc **7.3.0**, platform-atmelavr **5.2.0**
> (matching `size_baseline.json`'s recorded `meta` block exactly).

### Firmware AVR flash/RAM

| Env | @ `3085084` (= local HEAD) | @ live beta `6fab4ea` | Δ | `size_baseline.json` records |
|-----|---------------------------|----------------------|---|------------------------------|
| `uno` | flash **23954**/32256 · RAM **1573**/2048 | flash **23988** · RAM 1573 | **+34** flash, 0 RAM | 23954 / 1573 |
| `uno328pb` | flash **24004**/32384 · RAM **1579**/2048 | flash **24038** · RAM 1579 | **+34** flash, 0 RAM | 24004 / 1579 |
| `leonardo` | flash **26016**/28672 · RAM **2014**/2560 | flash **26050** · RAM 2014 | **+34** flash, 0 RAM | 26016 / 2014 |

`uno` was measured **both cold** (`rm -rf .pio/build/uno` then a single `pio run -e uno`) **and warm**
— **identical, 23954/1573 both ways**. That is expected and worth stating in the baseline artifact:
**warm-vs-cold contamination affects the *warning* watermark, not the size figures.** The live-tip
figures were measured in a **cold, freshly-extracted tree** (`gh api …/tarball/6fab4ea`), so they are
cold by construction.

### Firmware native suites

| Env | cases | succeeded | suites | all PASSED |
|-----|-------|-----------|--------|-----------|
| `native` | **141** | 141 | **17** | yes |
| `native_nodevtools` | **141** | 141 | **17** | yes |
| `native_pinmap_provisional` | **10** | 10 | **1** | yes |

All three match `size_baseline.json` exactly. `test_flash_intel_vpp` — the KNOWN-FLAKY suite named in
`platformio.ini` — is **not** in any env's `test_filter`, so it contributes 0 to these counts.

### Firmware python gate suite (`firestarter/tests/`)

| Where measured | Result |
|----------------|--------|
| real checkout `/workspaces/firestarter` (meta repo present at `/workspaces`) | **221 passed, 0 failed, 0 skipped** in 8.8 s |
| detached tarball tree (no `.git`, no meta sibling) | **7 failed, 182 passed, 32 skipped** |

The 7 failures are all git-history or meta-presence gates: `test_check_landing_range`,
`test_checker_convention`, `test_flash_geometry_recorded_before_linker`,
`test_flash_path_record_sync`, **`test_golden_trace_identity::test_blob_sha_matches_the_recorded_inventory`**,
and two in `test_pr45_non_ancestry`. This is the **fail-closed contract working as designed** — and it
means PREP-03 must state *where* it measured, because the pass/skip split is location-dependent.

### Gate outcomes (D-07's question, answered)

| Invocation | Tree | Exit | Output |
|------------|------|------|--------|
| `check_size_baseline.py` default mode, 3 AVR + 2 native logs | `3085084` | **0 — GREEN** | `PASS: uno(flash=23954/32256,ram=1573/2048), uno328pb(…24004…), leonardo(…26016…), native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)` |
| `check_size_baseline.py` default mode, 3 AVR logs | live beta `6fab4ea` | **1 — RED** | `FAIL:` / `uno: flash_used baseline=23954 observed=23988` / `uno328pb: … 24004 … 24038` / `leonardo: … 26016 … 26050` |
| `check_size_baseline.py --policy merge05 --baseline …base01.json` | live beta `6fab4ea` | **0 — GREEN** | `uno(flash=23988[+56<=64]) uno328pb(24038[+62<=64]) leonardo(26050[-22<=0])` |
| `check_build_warnings.py --log native=… --log native_nodevtools=…` (warm logs) | `3085084` | **0 — PASS (INFO arm)** | `observed=998 is 168 below watermark 1166 — re-measure and lower total_watermark…` |

**D-07 verdict, both readings stated honestly:** the live baseline is **GREEN at the decided base
`3085084`** and **RED at the live beta tip `6fab4ea`**, with a uniform **+34 B flash** delta on all
three targets attributable to `b1737b2` (`MSG_OK_READY` ack payload). Whichever base PREP-02 picks,
the finding must be recorded and **not fixed** (D-07). The `--policy merge05` band is *also* worth
recording as a v1.31 risk: uno-class is already at **+56** and **+62** against BASE-01's **64 B** band
— **8 B and 2 B of headroom** left before TEST-08's comparison fails on arrival.

The **998 vs 1166** warning figure is live confirmation of `meta.warm_vs_cold_correction`: my
`pio test` runs reused an Aug-2 `.pio/build` cache and reproduced the recorded **warm** figure exactly.

### Host suite (`firestarter_app`)

| Tree | Interpreter | Collected | Result |
|------|-------------|-----------|--------|
| live beta `4d18b64` (`3.0.0b20`) | `.venv/ci-replica` **py 3.11.15** | **1539** | **1493 passed · 46 skipped · 0 failed** · 179 s |
| cached `origin/beta` `04f63de` | py 3.11.15 | 1532 | (collect-only) |
| `gsd/v1.30-sdp-surface-retirement` `cc036e8` | py 3.11.15 | **1508** | (collect-only) — matches `v1.30-PR-BODY.md`'s "1508 passed" exactly |
| current worktree `7fe8dea` (fix branch) | py 3.11.15 | 1539 | (collect-only) |

**Two tests require the checkout directory to be literally named `firestarter_app`**:
`tests/test_gen_validation_header.py::test_validate_spec_called_before_emission` and
`tests/test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing`. Both resolve
`_HERE.parent.parent / "firestarter_app"`. Measured in a directory named `app_beta_live` they FAIL;
renaming the directory to `firestarter_app` flips both to PASS with no other change. This is the
mirror image of the recorded "devcontainer sibling layout masks CI-only defects" trap.

---

## Pulse Distribution (PREP-04)

### The parser — `firestarter_app/firestarter/database.py:128`

```python
def _parse_pulse_duration(pulse_str: str) -> int:
    if not pulse_str:
        return 0
    parts = pulse_str.split()
    if len(parts) == 2 and parts[1] == "us":
        try:
            return int(parts[0])
        except ValueError:
            pass
    return 0
```

Consumed at `database.py:417` — `"pulse-delay": _parse_pulse_duration(programming.get("pulse_duration", ""))`
— and forwarded to the wire at `database.py:555`. Measured edge cases [VERIFIED: executed live]:

| Input | Returns | Note |
|-------|---------|------|
| `'100 us'` | `100` | the only accepted shape |
| `'  100   us  '` | `100` | `.split()` collapses whitespace |
| `''` / `None` | `0` | falsy short-circuit |
| `'Algorithm Controlled'` | `0` | 3 parts ≠ 2 |
| `'100us'` | `0` | space is mandatory |
| `'100 US'` | `0` | **case-sensitive** |
| `'100 µs'`, `'1 ms'` | `0` | only the literal `us` |
| `'0 us'` | `0` | **indistinguishable from unparseable** |
| `'-5 us'` | **`-5`** | **no sign or bounds check** |
| `'65536 us'` | `65536` | no uint16 ceiling check at this layer |
| `100` (int) | **raises `AttributeError`** | annotated `str`, never runtime-checked |

**This is precisely why D-11 requires explicit buckets:** the parsed integer `0` is a four-way
collision (`"0 us"`, `""`, `"Algorithm Controlled"`, malformed). **The PREP-04 script must bucket from
the RAW string, never from the parsed int.**

### Measured distribution — blob `ebd1eaac01698f64dc0861f8478b8931493d3bab`

The `chip_database.json` blob is **byte-identical** on the worktree, app `HEAD`, cached `origin/beta`,
**and** `gsd/v1.30-sdp-surface-retirement`. `database.py` is likewise identical (`b8c0582c…`) across
all three refs. **Therefore PREP-04 does not depend on PREP-01 at all** — one of the strongest
sequencing facts in this research.

| Protocol | n | Distribution (parsed µs × count) |
|----------|---|----------------------------------|
| `0x07` | **170** | 100 ×113 · 200 ×27 · 1000 ×22 · 500 ×4 · 50 ×4 |
| `0x08` | **127** | 100 ×104 · 50 ×11 · 10 ×7 · 200 ×2 · 1000 ×2 · 20 ×1 |
| `0x0B` | **32** | 500 ×21 · 1000 ×6 · 200 ×5 |

**Reproduces the seed's C2 figures exactly** — every count, every value. C2 is confirmed independently
this milestone, not restated.

**D-11's buckets, measured:**

| Bucket | `0x07` | `0x08` | `0x0B` |
|--------|--------|--------|--------|
| key absent | 0 | 0 | 0 |
| empty string | 0 | 0 | 0 |
| `"Algorithm Controlled"` | 0 | 0 | 0 |
| other unparseable → 0 | 0 | 0 | 0 |
| explicit `"0 us"` | 0 | 0 | 0 |

**All four buckets are empty, and that is the finding** — not an omission. State it explicitly:
*"every one of the 329 chips on `0x07`/`0x08`/`0x0B` carries a numerically-parseable `"N us"` string;
the denominator is complete and no chip was dropped."*

**A clean whole-database partition, worth quoting publicly:** 746 chips total; **329** on
`0x07`/`0x08`/`0x0B`, **all** numeric; **417** on every other protocol, **all** `"Algorithm
Controlled"`. `329 + 417 = 746` exactly, with **zero** crossover in either direction. Whole-DB raw
histogram: `Algorithm Controlled` 417 · `100 us` 217 · `200 us` 34 · `1000 us` 30 · `500 us` 25 ·
`50 us` 15 · `10 us` 7 · `20 us` 1; `pulse_duration` key **never** missing (0 of 746).

**C1's adjudication, for the script's citation** — `firestarter_app/doc/infoic-field-dictionary.md`
§`pulse_delay` carries the table `AM2716 | 0x0B | 0x1F4 | 500 µs | 50000 µs (×100 wrong)` and names
BUG-2/DEC-03 explicitly. That is the `file:line` ISSUE-01 needs.

### The 136.1 script pattern (D-10)

`.planning/phases/136.1-sdp-partition-provenance/136.1-check-blast-radius.py` — read live. Shape to copy:

- `#!/usr/bin/env python3`, **stdlib only** (`json`, `os`, `subprocess`, `sys`).
- Module docstring that: names the plan/requirement; enumerates the numbered assertions; states the
  exit-code contract; and states its **own non-vacuity obligation** ("it must be capable of failing,
  not merely of passing").
- **Env-var seams, not argparse** — `PRE_DB_REF`, `PRE_DB_PATH`, `POST_DB_PATH`, `SUBMODULE_DIR`
  (default `/workspaces/firestarter_app`) — each documented in the docstring, so the script stays
  "re-runnable later as a standing regression proof, not a one-shot with hardcoded temp paths".
- `main()` prints a `"=" * 78` banner, a labelled summary block, then `VIOLATIONS: N` and
  `RESULT: PASS|FAIL`; returns 0 / 1; `sys.exit(main())`.
- **Committed in the phase directory** as `<phase>-<name>.py` (meta repo).
- **Output committed alongside** as `<phase>-<PLAN>-<NAME>.md` (`136.1-01-BLAST-RADIUS.md`), which
  records the **verbatim** stdout of **two** runs — each preceded by its literal `$ cd … && python3 …`
  command line — then a short prose paragraph reconciling the numbers against an independent source.

Both the script and its output artifact landed in the **same meta commit** (`3624205`), and the
script's invocation is named in the plan's `<verify>` block as the reproducible command.

---

## Trace Capture Mechanism (D-02) — the crux, corrected

### What actually exists today

| Layer | Guard | Storage | Cap | Readback API | Who defines the guard |
|-------|-------|---------|-----|--------------|----------------------|
| `(reg,data)` recorder | `HOST_STUBS_RECORD_BUS` | `static bus_record_entry_t s_bus_recording[256]` | **256** | `clear_bus_recording()`, `bus_recording_count()`, `recorded_reg(i)`, `recorded_data(i)` | `test_val_eprom`, `test_val_sram`, `test_val_eeprom28c`, `test_val_nor_unlock`, `test_val_5v_page`, `test_val_flash_intel` (6 suites) |
| ordered strobe recorder | `HOST_STUBS_REAL_REGISTER_UTILS` | `static strobe_entry_t s_strobes[512]` (`{uint8_t kind; uint8_t pin; uint8_t value;}`) | **512** | `clear_strobes()`, `strobe_count()`, `strobe_overflowed()`, `strobe_kind/pin/value(i)` | `test_sdp_harness`, `test_eeprom28c_sdp` (2 suites) |
| timing recorder | — | **does not exist** | — | — | — |

**Correction 1 — the two layers do NOT compose.** `host_stubs_common.inc`'s own comment claims
`HOST_STUBS_REAL_REGISTER_UTILS` "composes with, does not replace, `HOST_STUBS_RECORD_BUS`", but the
preprocessor structure at lines 81/131/153 is `#ifdef … #elif defined(HOST_STUBS_RECORD_BUS) … #else`.
Defining **both** yields **only** the strobe recorder; the `(reg,data)` array is not compiled. The
comment is true at the *conceptual* level (the real `rurp_write_to_register` decomposes into recorded
strobes) and false at the *preprocessor* level. A fixture that wants both views must reconstruct
`(reg,data)` from the strobe stream. [VERIFIED: source read]

**Correction 2 — `delay()`/`delayMicroseconds()` are already mocked, just not in the `.inc`.**
They are **free functions defined in `ArduinoFake/src/FunctionFake.cpp`**:

```cpp
void delay(unsigned long value)            { ArduinoFakeInstance(Function)->delay(value); }
void delayMicroseconds(unsigned int us)    { ArduinoFakeInstance(Function)->delayMicroseconds(us); }
```

declared `virtual` in `FunctionFake.h`. **Eight** suites already mock them in `setUp()` with
`When(Method(ArduinoFake(), delay)).AlwaysReturn();` — including `test_val_eprom` (line 61) and both
SDP suites — because, as `test_val_eeprom28c.cpp` records, *"ArduinoFake ABORTS (SIGABRT) on any
unmocked"* virtual. **A definition of `delay()` in `host_stubs_common.inc` would be a duplicate-symbol
link error against `FunctionFake.cpp.o`.** [VERIFIED: ArduinoFake 0.4.0 source in `.pio/libdeps/`]

### The seam that does exist

fakeit's `.AlwaysDo(lambda)` — already used in-repo with **argument capture**
(`test/native/avr/test_messages/serial_read_mock.h:94` captures `(char* buf, size_t length)`).
So the timing layer splits cleanly across two tiers:

- **Shared `.inc` tier (new opt-in guard, e.g. `HOST_STUBS_RECORD_TIMING`):** the storage array, an
  `extern "C" void timing_push(uint8_t kind, uint32_t us)` entry point, and the readback accessors.
  All inside `#ifdef` — **flag-off is byte-exact for all 17 pre-existing suites by construction,
  because not one line outside the new `#ifdef` block changes.**
- **New suite's `setUp()` tier:** installs the hooks.

```cpp
/* In the NEW suite's setUp() — replaces .AlwaysReturn() with a recording hook. */
When(Method(ArduinoFake(), delay)).AlwaysDo([](unsigned long ms) {
    timing_push(TIMING_KIND_DELAY_MS, (uint32_t)ms);
});
When(Method(ArduinoFake(), delayMicroseconds)).AlwaysDo([](unsigned int us) {
    timing_push(TIMING_KIND_DELAY_US, (uint32_t)us);
});
```

### Interleaving: one array with a tag, or two arrays with sequence numbers?

The brief asks which the existing readback code can consume with least churn. **Answer: two arrays
with sequence numbers, recommended — for three measured reasons.**

| Option | Mechanics | Churn on existing consumers | Verdict |
|--------|-----------|----------------------------|---------|
| **A — extend `strobe_entry_t`** with a `uint32_t us` field and a third `kind` | one array, naturally ordered | Grows the struct **inside** the `HOST_STUBS_REAL_REGISTER_UTILS` block, which **both SDP suites compile**. `sdp_expected.h`'s `sdp_strobe_t` is a hand-mirrored copy of that struct and `sdp_first_divergence`/`sdp_assert_stream_equals` compare positionally. Behaviour-neutral but it perturbs a **frozen, blob-SHA-pinned** artifact's consumer path. | **avoid** |
| **B — separate `s_timings[]` carrying `{kind, us, seq}` where `seq = s_strobe_count` at push time** | two arrays; the merged ordered stream is reconstructed by the *test* walking strobes and splicing timings at their `seq` boundary | **Zero** change to `strobe_entry_t`, `sdp_expected.h`, or either SDP suite. New guard is purely additive. | **recommended** |
| **C — a third unified array written by both `strobe_push` and `timing_push`** | one array, but `strobe_push` (a `static` in the `.inc`) must gain a conditional write | Touches the existing recorder's hot path under a new `#ifdef` — provable but strictly more edit surface than B. | acceptable fallback |

Under **B**, the new fixture's own comparator is a *new* helper in the *new* fixture header (mirroring
`sdp_assert_stream_equals` but over the merged stream) — so **`test_val_eprom/`'s current readback code
needs no change at all.** That matters: `test_val_eprom` uses `HOST_STUBS_RECORD_BUS` (not the strobe
recorder), asserts only on `CONTROL_REGISTER` VPP bits, and never calls
`firestarter_operation_main` — its 6 cases and 256-entry cap are untouched by anything above.

### What the trace will actually contain — and why the pulse is invisible today

**The program pulse is not in `eprom.cpp`.** It is at `src/proms/memory.cpp:329`:

```cpp
void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_chip_input();                                  // strobe: PIN OUTPUT_ENABLE(0x04)=1
    address = mem_util_remap_address_bus(handle, address, WRITE_FLAG);
    handle->firestarter_set_address(handle, address);    // strobes: LSB/MSB/CTRL latches (with elision)
    rurp_write_data_buffer(data);                       // strobe: DATA
    delayMicroseconds(3);                               // TIMING — invisible today
    rurp_chip_enable();                                 // strobe: PIN CHIP_ENABLE(0x20)=0
    delayMicroseconds(handle->pulse_delay);             // ← THE PROGRAM PULSE. TIMING — invisible today
    rurp_chip_disable();                                // strobe: PIN CHIP_ENABLE(0x20)=1
}
```

CONTEXT.md cites `eprom.cpp:283 delayMicroseconds(handle->pulse_delay)` — that is the **erase** pulse
inside `eprom_internal_erase`, a different call site. The **program** pulse is `memory.cpp:329`.
Both are in scope of the phase fence's "or any file on the EPROM write path": **`memory.cpp` is on
the write path and must not be edited in Phase 138 either.**

`rurp_chip_enable/disable/input/output` are `static inline` in `include/rurp_shield.h` routing through
`rurp_set_control_pin(CHIP_ENABLE=0x20 | OUTPUT_ENABLE=0x04, state)` — so **they already appear in the
strobe stream**. Register constants: `LEAST_SIGNIFICANT_BYTE 0x01`, `MOST_SIGNIFICANT_BYTE 0x02`,
`OUTPUT_ENABLE 0x04`, `CONTROL_REGISTER 0x08`, `CHIP_ENABLE 0x20`.

The real `rurp_register_utils.h` also injects timing of its own: `delayMicroseconds(1)` after **every
non-elided** register latch (`rurp_internal_write_to_register`) and `delayMicroseconds(4)` whenever
`CTRL_VPP_P1_ENABLE` transitions set→clear. **The timing stream will be dominated by 1 µs latch
entries.** The plan must decide explicitly whether to record all of them (faithful, noisy, and it
proves interleaving) or to filter — and say which, in the fixture's header comment.

### The blocker: the loop will overflow the recorder unless read-back is modelled

`eprom_write_execute` (`eprom.cpp:141-190`):

- `memset(mismatch_bitmask, 0xFF, …)` → the **first pass programs every byte**, including
  already-matching and `0xFF` ones (LOOP-06's "skip" behaviour is a v1.31 *change*, not current).
- `for (int w = 0; w < NUMBER_OF_RETRIES /* 20 */; w++)`: `program_mismatched_bytes` (which itself
  does `set_control_register(CTRL_VPE_ENABLE,1)` + **`delay(10)`** + per-byte `set_data` + disable),
  then `verify_and_update_mask` re-verifies **all** `data_size` bytes every pass.
- The default stub `rurp_read_data_buffer()` returns **`0`** (`host_stubs_common.inc:185`, **unguarded**).

So any non-zero target byte never verifies → 20 passes → for an 8-byte block the verify legs alone
emit ≈ 8 × 6 × 20 ≈ **960 strobes**, overflowing the 512 cap and setting `s_strobe_overflow`.

**Entry-budget arithmetic** (steady state, small consecutive block, MSB/CTRL elided):

| Operation | strobes | timing entries |
|-----------|---------|----------------|
| program one byte (`memory_set_data`) | ≈ **7** (OE, LSB triple, DATA, CE↓, CE↑) | ≈ **3** (latch 1 µs, settle 3 µs, **pulse**) |
| verify one byte (real `memory_get_data`) | ≈ **6** | ≈ **2** |
| per-pass VPE assert + release | ≈ 6 | ≈ 3 (incl. `delay(10)`) |
| one-time VPP enable + `delay(500)` | ≈ 3 | ≈ 2 |

⇒ **4-byte block, 3 passes ≈ 174 strobes; 8-byte block, 3 passes ≈ 232 strobes.** Both fit in 512
with margin. **20 passes does not.** D-03's 4–8 byte guidance is sound *conditional on convergence*.

**Two ways to make the loop converge — both must be a plan decision, not an accident:**

| Option | Mechanism | Precedent | Cost |
|--------|-----------|-----------|------|
| **R1 — replace the handle's read function pointer** `h.firestarter_get_data = mock_get_data_keyed` with a **stateful, address-keyed, pulse-counting** mock (returns `0xFF` virgin, converges to target after N pulses) | pure test-tier; **no `.inc` change** | **proven in-repo**: `test_sdp_harness.cpp:570-617`, `test_eeprom28c_sdp.cpp:404-433` | the verify read's **bus activity is not traced** (the mock bypasses `memory_get_data`) — halves the entry budget but loses verify-path fidelity |
| **R2 — add `HOST_STUBS_CUSTOM_READ_DATA_BUFFER`** opt-out so the suite supplies a stateful `rurp_read_data_buffer()` | keeps the **real** `memory_get_data` in the trace | none — `rurp_read_data_buffer` at `host_stubs_common.inc:185` is currently **unguarded**, so this is a genuine (small) `.inc` change | one more additive guard; still flag-off byte-exact |

**Recommendation: R2 for fidelity, R1 as the de-risked fallback.** TEST-06's "every changed strobe
attributable to a named decision" is materially stronger if the verify read is in the stream, because
LOOP-01 ("verifies after each pulse") and LOOP-08 ("VPE survives the verify read") are *verify-path*
claims. If the plan takes R1, say plainly in the fixture header that the verify read is out of frame.

**Two more traps for the new suite**, both recorded in the SDP suites' own comments:

1. `lsb_address`, `msb_address`, `control_register` are **non-`static` globals in
   `rurp_register_utils.h` initialised to `0xff`**, and they **persist across Unity cases in one
   binary**. `0xff` ORs `CTRL_VPP_REGULATOR_ENABLE` into the first address write of any case that
   does not reset them. Both SDP suites define
   `extern "C" void reset_register_cache(uint8_t, uint8_t, rurp_register_t)` and call it per case.
   **The new suite must do the same** or its first-case trace is contaminated and its later cases
   diverge from its first.
2. `configure_memory()` **overwrites both** `firestarter_get_data` **and** `firestarter_set_data`
   (`test_sdp_harness.cpp:613-617`) — any mock pointer must be installed **after** `configure_memory`.

**Unresolved input the plan must source: `handle->bus_config`.** `memory_set_data` calls
`mem_util_remap_address_bus(handle, address, WRITE_FLAG)`. `test_val_eprom` gets away with
`firestarter_handle_t h = {}` because it never reaches that path. The new suite does. The repo already
generates `test/native/avr/_shared/sdp_bus_config.h` from `firestarter_app/firestarter/data/pinouts.json`
via `tools/gen_sdp_bus_config.py`, but it carries **only 5 rows, all 28C pinouts** — none for
`DIP28_27C256` / `DIP32_27C020` / `DIP24_2716`. Options: extend that generator (principled, cross-repo,
respects "generated files are never hand-edited") or supply a documented minimal identity bus_config
in the fixture. **See Open Question Q1.**

### Where a new suite can live — and the count it must not break

There are **three** native environments, not two:

| Env | `test_filter` entries | In `default_envs`? |
|-----|----------------------|--------------------|
| `[env:native]` | **17** | no |
| `[env:native_nodevtools]` | **17** (identical list) | no |
| `[env:native_pinmap_provisional]` | **1** (`native/avr/test_pinmap_provisional`) | no |

Adding a suite requires **two lines per env** (`test_filter` **and** a matching
`-I test/native/avr/<dir>` in `build_flags`) — a suite directory is invisible until both are present
(corrected in v1.22 Phase 119 D-04).

**Hard constraint, spelled out in `platformio.ini:269-275` itself:** both pinned envs are held at
*exactly* 17 entries / 141 cases, and that pair is asserted by `check_size_baseline.py`'s
`compare_native` against `size_baseline.json`. **Adding the trace suite to either pinned env turns the
live size gate RED for a reason unrelated to size** — and D-05 forbids rewriting the live baseline to
absorb it. The precedent is already set: Phase 124 created a **dedicated third env** naming only its
own suite. **Recommendation: a fourth env** (e.g. `[env:native_trace_v131]`) with a 1-entry
`test_filter`, not in `default_envs`, deriving `build_flags` from `${env:native.build_flags}` exactly
as `native_pinmap_provisional` does.

**Measured caveat for a fourth env** — `check_size_baseline.py` handles an unknown env **worse** than
its sibling does:

```
$ python3 scripts/check_size_baseline.py --native-log native_trace_v131=<log>   # exit 1, uncaught traceback
  File ".../check_size_baseline.py", line 278, in compare_native
    rec = baseline["native_envs"][env]
KeyError: 'native_trace_v131'

$ python3 scripts/check_build_warnings.py --log native_trace_v131=<log>          # exit 2, clean message
ERROR: env 'native_trace_v131' not found in baseline warnings.avr or warnings.native -- configuration error, not a pass
```

`check_size_baseline.py` raises an **uncaught `KeyError` → exit 1**, i.e. it reports a *regression*
where its own documented taxonomy promises exit 2 (*tool/format failure*). This is a **second D-07-class
finding: record it, do not fix it.** It is harmless in practice because `NATIVE_ENVS` is hardcoded to
`("native","native_nodevtools")`, so `--rebuild` never reaches the new env — which in turn means the
new env's counts and warnings are simply **unmeasured by the live gates**, and the plan should record
them only in the new `size_baseline_v131.json`.

---

## Frozen-Fixture Triple (D-04) — the exact contract to satisfy

### `firestarter/tests/golden/sdp_expected_inventory.json` — schema

```json
{
  "meta": {
    "source": "test/native/avr/_shared/sdp_expected.h",
    "recorded_by": "Phase 124 Plan 03",
    "requirement": "MERGE-06",
    "blob_sha": "dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83",
    "recorded_at_head": "17c7614d7d3ec1701cd618711a366dc11253299f",
    "why_two_checks": "A whole-file blob match alone cannot distinguish 'unchanged' from 'an array deleted together with the assertions that consumed it' …",
    "how_to_update": "…re-derive this inventory from the file with an independent parse (never hand-edit the numbers) AND state in the commit message which array changed and why…"
  },
  "arrays": [ { "name": "SDP_SHIPPED_DIP28_28C256", "entries": 54 }, … ]
}
```

### `firestarter/tests/test_golden_trace_identity.py` — the six assertions

1. `test_blob_sha_matches_the_recorded_inventory` — `git rev-parse HEAD:<fixture>` == `meta.blob_sha`.
2. `test_array_names_match_the_recorded_inventory` — **ordered** name list from an independent regex
   parse of the live file == ordered names in the JSON.
3. `test_array_entry_counts_match_the_recorded_inventory` — positional `(name, entries)` equality,
   failing with the **first diverging index and both values**, never a bare "lists differ".
4. `test_inventory_is_non_vacuous` — `len(arrays) >= 9` **and** every `entries >= 1`.
5. `test_consuming_suites_still_include_the_fixture` — each named consumer `.cpp` still contains the
   literal `_shared/sdp_expected.h` (the load-bearing link: "if both consumers stopped including it,
   the blob could stay byte-identical while nothing exercised it").
6. `test_git_is_required_not_optional` — **self-scanning**: no line in this module's own source starts
   with `pytest.skip` or `@pytest.mark.skipif`, so a missing `git` FAILS rather than skips.

`_resolve_git()` fails closed via a plain `assert` on `shutil.which($GIT or "git")`. `_parse_arrays()`
strips `/* */` and `//` comments before counting `{…}` entries, so a commented-out entry cannot inflate
a count. `_ARRAY_DECL_RE` is `static const sdp_strobe_t\s+(\w+)\[\]\s*=\s*\{(.*?)\};` — **SDP-typed**.

**What a new fixture must supply.** Every constant in that module is hard-wired to SDP:
`_FIXTURE_PATH`, `_INVENTORY_JSON`, `_CONSUMERS`, `_ARRAY_DECL_RE`, and the literal `>= 9`.
**Recommendation: author a parallel module** (e.g. `tests/test_golden_trace_identity_eprom_v131.py`
+ `tests/golden/eprom_v131_trace_inventory.json`) copying all six checks with new constants, rather
than parameterising the existing load-bearing gate — check 6 scans *its own source file*, so
refactoring it into a shared helper risks hollowing out its self-enforcement.

**Two-commit dance is avoidable.** `git rev-parse HEAD:<path>` reads from `HEAD`, so the naive
sequence is commit-fixture → read SHA → commit-inventory. **Measured: `git hash-object <path>` returns
the identical SHA without committing** (`dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83` both ways), so the
fixture and its inventory can land in **one** commit.

### The recorded "byte-identical criterion" trap applies here

Do **not** write an acceptance criterion of the form "empty `git diff`" or "byte-identical file" for
the pre-existing suites' outputs — a later `#if` guard legitimately changes bytes and breaks such a
criterion. Instead: scope the flag-off proof to **assertions-unchanged** plus **named blob SHAs**, and
prove byte-exactness *behaviourally* by re-running the pinned envs and re-asserting **141 cases /
17 suites / all PASSED on both** (which is exactly what `check_size_baseline.py`'s `compare_native`
already does, and which the numbers in §"Measured Baseline" pin).

### `sdp_expected.h` — the form to copy

Header guard; `#include <stdint.h> <unity.h> "firestarter.h"`; `extern "C"` recorder-accessor
declarations "declared once here so both suites get them from a single place"; a **locally-named
mirror struct** (`sdp_strobe_t`) with a comment stating it "matches `host_stubs_common.inc`'s
`strobe_entry_t` exactly … given its own name here since the recorder's own struct is TU-local";
`#define`d mirrors of the TU-local `enum`; a `first_divergence()` that **never counts**; an
`assert_stream_equals()` that checks `overflowed()==0`, then length, then element-by-element, failing
with `"diverges at index %d -- expected {…}, recorded {…}"`; a `snapshot()` helper for
stream-vs-stream comparison; then the literal arrays, each preceded by a comment recording **how it
was empirically obtained** and **what non-obvious behaviour it encodes** (the shipped array documents
that write #4's address latch is **elided** by the LSB/MSB cache — "a raw call-log golden would assert
6 phantom entries here that the shield never sees").

---

## Cold Measurement Protocol (D-06) — exact, from `size_baseline.json`'s own `meta`

**AVR envs** (`uno`, `uno328pb`, `leonardo`) — `meta.note`, verbatim intent:

```bash
pio run -t clean -e <env>      # then, as ONE uninterrupted invocation:
pio run -e <env>               # capture the FULL build log
```

**Native envs** (`native`, `native_nodevtools`, `native_pinmap_provisional`):

```bash
rm -rf .pio/build/<env>
pio test -e <env>              # a SINGLE invocation, extended timeout
```

**Required timeout: `540000` ms (9 min).** `meta.note` names this figure explicitly and records the
trap: *"a default 2-minute Bash timeout truncates the toolchain build mid-compile and silently
contaminates the measurement."* 540 000 ms is inside the tool's 600 000 ms ceiling.

**Warm figures are contamination for warnings, not for sizes.** `meta.warm_vs_cold_correction`
records BASE-01's 360 as a warm figure vs 456 cold on a byte-identical tree, and post-landing
`native` COLD **1166** / WARM **998**. I reproduced **998** exactly from a warm cache this session —
the trap is live, not historical. Conversely `uno` measured **23954/1573 cold and warm** — identical.
So: **AVR size figures may be taken warm; every warning watermark must be cold.**

**`check_size_baseline.py --rebuild` is NOT a cold measurement for native.** `_rebuild_avr()` does
`pio run -t clean` first, but `_rebuild_native()` runs a bare `pio test -e <env>` with **no
`rm -rf`** — a warm run. Harmless for `compare_native` (which only reads cases/suites/status) but it
must **not** be used to source a warning watermark.

**`FIRESTARTER_SIZE_BASELINE`**: `os.environ.get("FIRESTARTER_SIZE_BASELINE", str(REPO_ROOT /
"scripts" / "baseline" / "size_baseline.json"))`. An explicit `--baseline PATH` **takes precedence
over the env var** (`baseline_path = baseline_arg or FIRESTARTER_SIZE_BASELINE`). Same seam name is
read by `check_build_warnings.py` — one file, two consumers.

### `size_baseline_base01.json` — the schema `size_baseline_v131.json` should copy

```
meta { generated, phase, generated_by, firmware_tree_sha, host_app_tree_sha,
       platformio_core, platform_atmelavr, toolchain_atmelavr, avr_gcc,
       framework_arduino_avr, framework_arduino_avr_minicore,
       roadmap_cross_check, supersedes, consumed_by, note }
avr_targets { uno|uno328pb|leonardo : { flash_used, flash_total, flash_free,
                                        ram_used, ram_total, ram_free } }
native_envs { <env> : { cases, succeeded, suites, all_passed } }
envs_agree            (bool)
envs_agree_note       (prose, states the MEASURED reason the envs agree)
warnings { avr { <env>: { macro_redefinition, total } },
           native { <env>: { macro_redefinition, total_watermark } },
           policy { avr_rule: "== 0", native_rule: "<= total_watermark" },
           counting_command, note }
```

BASE-01 differs from the live file in exactly two ways: it has **no** `native_pinmap_provisional`
entry (that env postdates it) and **no** `meta.deltas_vs_base01` block. For `size_baseline_v131.json`,
carry BASE-01's shape plus a `meta.deltas_vs_*` block naming the base it was measured at and its
delta against **both** BASE-01 and the live baseline — because the two now disagree (§"Gate outcomes").

**Warning-count command**, verbatim from `warnings.counting_command`:

```bash
pio test -e <env> 2>&1 | grep -cE 'warning: *"[^"]+" +redefined'   # macro-redefinition count
pio test -e <env> 2>&1 | grep -cE 'warning:'                        # total
```

---

## CI Evidence (D-06) — a measured asymmetry

| Repo | Workflow | Trigger | `workflow_dispatch`? | Runs `pio test`? | AVR sizes in log? | Runs the size/warning gates? |
|------|----------|---------|---------------------|------------------|-------------------|------------------------------|
| `firestarter` | `build.yml` (`Firestarter CI`) | `push: branches: ['**', '!beta']` + `pull_request`, with `paths-ignore` | **NO** | yes — `native` **and** `native_nodevtools` | **yes** — `pio run` (step *Build PlatformIO Project*) is **deliberately outside the publish boundary**, so it builds `default_envs = uno, uno328pb, leonardo` on every branch | **no** — `pytest tests/ -v` tests the *checkers against fixtures*; neither gate is invoked against the live tree |
| `firestarter` | `beta-build.yml` | `push: beta` | yes | yes | yes | no |
| `firestarter_app` | `ci.yml` | `push: branches: ['**']` + `pull_request`, with `paths-ignore` | **YES** (line 33) | `pytest --cov … --cov-fail-under=70` | n/a | n/a |
| `firestarter_app` | `beta-release.yml` | **`push: beta`, no `paths-ignore`** | yes (`beta_version` input) | `pytest tests/ -v` | n/a | n/a |

**Consequences for D-06:**

- The **app**'s `ci.yml` **is** `workflow_dispatch`-able — exactly the shape `131-CI-BASELINE.md`
  recorded (`event: workflow_dispatch`, `headBranch: beta`). The operator can dispatch it; the agent
  reads it with `gh run view … --json event,headBranch,headSha,conclusion,url,createdAt`.
- The **firmware**'s `build.yml` **cannot be dispatched** — it has no `workflow_dispatch` trigger.
  Its run is produced by **pushing** the v1.31 branch (which the trigger `['**', '!beta']` covers).
  So "operator-dispatched CI run" reads differently per repo, and the plan must say which.
- Neither firmware gate runs in CI, so **`check_size_baseline.py` / `check_build_warnings.py` are
  local-run obligations.** A CI run cannot substitute for the local cold measurement; state that
  plainly rather than implying CI coverage.
- `paths-ignore` on both repos excludes `**.md` — **a commit touching only markdown fires no CI**.
  A plan that expects a run id from a docs-only push will wait forever.

**`beta-release.yml`, confirmed for D-08** — header comment verbatim: *"EVERY merge to beta cuts a
pre-release. The paths-ignore list that used to sit here … meant a merge touching only those paths
bumped no version and published nothing."* Pipeline: `update_version.py` → `git-auto-commit-action@v5`
(*"Commit updated version"*) → resolve post-bump SHA → `action-gh-release` (`prerelease: true`,
`make_latest: false`) → a **`pypi` job** that calls `publish.yml`. **The post-merge fork base is the
auto-commit, not the merge commit** — and empirically every recent app/firmware `beta` tip is a commit
titled `Apply automatic changes`. No publish loop: GITHUB_TOKEN pushes do not re-trigger workflows.

Bump rule (`.github/scripts/update_version.py`): base = `major.minor.patch` of the current
`__version__`, then `git tag --list "<base>b*"` → `max(N)+1`, or the explicit `BETA_VERSION` input if
given (validated against `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$`). Current state: `beta` is already at
**`3.0.0b20`** with 19 `3.0.0b*` tags in the local cache — so a *further* push would produce `b21`.

---

## `131-CI-BASELINE.md` — the narrative-artifact shape to copy

187 lines, nine numbered sections:

1. **§1 The run** — a `| Field | Value |` table: run id, URL, `event`, `headBranch`, `headSha`
   (*"exactly the fork base"*), `created`, `conclusion`. Plus a paragraph stating **who** dispatched
   it and that *"No agent ran `gh workflow run`; every command in this document … is a read-only
   `gh run view` / `gh run list` call"*, and explicitly naming the **wrong/stale run it is not**.
2. **§2 Fail-closed precondition, re-verified before writing the file** — a checklist of **six**
   conditions each marked `pass`, read from one `gh run view --json event,headBranch,headSha,conclusion,url,createdAt`
   call: id is numeric · `gh run view` resolves it · `event` is `workflow_dispatch` · `headBranch`
   is right · `headSha` begins with the fork base · id is not the prior run · **`conclusion` is
   terminal** — closing with *"keying on `conclusion` per the v1.23 lesson that `outcome` and
   `conclusion` are distinct fields"*.
3. **§3 Per-step statuses** — a numbered table, with job ids named, and sibling jobs explicitly
   scoped out.
4. **§4 The verbatim gate output** — a fenced block of *"the **only substantive lines** that step
   emitted, quoted verbatim, in order"*.
5. **§5 A named correction (F-07)** where the plan's expected output was **structurally absent** —
   with the *mechanism* (a regex that stops before the clause), the four required handling actions,
   and *"Running mypy locally to manufacture one would violate D-12's 'read, never compute' rule"*.
6. **§6 Resolved tool versions**, *"Both read from the log, never invoked locally."*
7. **§7 What this number is — and is not** — *"an input to Phase 132's watermark … not a Phase 131
   claim, achievement, or fix"*, and *"Any artifact … claiming CI is green as a result of Phase 131 …
   is an overclaim."*
8. **§8 Divergence check against research's number** — states the rule that *had* they differed,
   **the measured number wins and both are recorded without reconciliation**.
9. **§9 Not established by this run.**

Footer: `*Phase: … — Plan NN, Task N*` / `*Recorded: <date>, from the real run dispatched by the
operator per <HANDOFF>.*`

**The `outcome` vs `conclusion` distinction is the load-bearing detail.** In the GitHub API,
*step*-level results expose `conclusion`; `outcome` is the pre-`continue-on-error` result. Keying a
terminality precondition on `outcome` can read a still-running or error-suppressed run as final.
Use `conclusion`, and assert it is non-`null`.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| Comparing measured sizes/counts to a record | a bespoke comparison script or eyeballed table | `scripts/check_size_baseline.py` via `--avr-log`/`--native-log` (+ `FIRESTARTER_SIZE_BASELINE` or `--baseline`) | Already covers the never-vacuous guard, a 3-way exit taxonomy, and `all_passed` (not just counts) |
| Warning-count policy | a fresh grep pipeline | `scripts/check_build_warnings.py` + `warnings.counting_command` | Exact-zero on AVR + watermark on native is already characterised; a new pipeline would recount known debt as damage |
| Fixture immutability | "committed, therefore frozen" | the `blob_sha` + per-array inventory + non-vacuity + consumer-inclusion + no-skip quintet | A blob match alone cannot see an array deleted **together with** its assertions |
| Trace comparison | sub-sequence scan or entry counting | ordered full-stream positional equality naming the first diverging index | `116-RESEARCH §F5`: shipped and fixed streams have *identical length* and, on one pinout, identical address bytes — counting cannot discriminate them |
| Intercepting `delay()` | a definition in `host_stubs_common.inc` | fakeit `When(Method(ArduinoFake(), delay)).AlwaysDo(λ)` | ArduinoFake **defines** those free functions; a second definition is a link error |
| Chip read-back in the write loop | a hand-rolled memory array in the test body | the proven `h.firestarter_get_data = mock_get_data_keyed` pointer swap (or a guarded `rurp_read_data_buffer` opt-out) | Two suites already do this, including the `configure_memory`-overwrites-the-pointer gotcha |
| Reproducible re-derivation | a number pasted into markdown | the `136.1-check-blast-radius.py` shape: stdlib, env-var seams, banner + `VIOLATIONS:` + `RESULT:`, exit 0/1, output committed verbatim | D-10; and PREP-04's output is destined for a public GitHub comment |
| Deciding whether a branch landed | `git merge-base --is-ancestor` alone | ancestry **plus** `git cherry`, `comm -23` of `ls-tree` lists, restricted `git diff`, and the GitHub PR record | Squash merges make ancestry a **false negative** — the exact trap PREP-01 walked into |
| Adding a native suite | appending to `[env:native]`'s `test_filter` | a dedicated fourth env (the `native_pinmap_provisional` precedent) | The two pinned envs are held at exactly 17/141 by a live gate |

**Key insight:** almost nothing in Phase 138 is new machinery. The phase's risk is not *building* the
wrong thing — it is **measuring the wrong tree**, or measuring warm and recording it as cold.

---

## Runtime State Inventory

> Phase 138 is a measurement phase, but its measurements are *runtime-state-sensitive* in exactly the
> way a rename phase is. Every category below was checked; none is speculative.

| Category | Items found | Action required |
|----------|-------------|-----------------|
| **Stored data / caches** | `.pio/build/{uno,uno328pb,leonardo,native,native_nodevtools,native_pinmap_provisional}` all present and **warm** (dated Aug 1–6, older than HEAD). Reproduced the warm warning figure **998** vs the recorded cold **1166**. | Every warning measurement **must** be preceded by `rm -rf .pio/build/<env>`; size figures may be warm (verified identical for `uno`). |
| **Live service config (git refs not in the worktree)** | Both submodules' cached `origin/beta` are **2 commits stale**; the app's local `beta` is **≥4 behind**; the firmware has a local `beta` CONTEXT.md says does not exist; no `gsd/v1.31*` on any remote; meta's v1.31 branch has **no upstream**. | Every base commit must be re-resolved against the **live** ref (`gh api …/git/refs/heads/beta`) at execution time, never from a cached `origin/beta` and never from a hardcoded `3085084`. |
| **OS-registered / directory-name-dependent state** | Two app tests resolve `_HERE.parent.parent / "firestarter_app"` and FAIL if the checkout directory is named anything else (measured both ways). Firmware `tests/` needs a real `.git` **and** a resolvable meta root (`FIRESTARTER_META_ROOT`) — 7 fail / 32 skip without them. | Measure host and firmware suites **in place**, in `/workspaces/firestarter_app` and `/workspaces/firestarter`, and record the location in the artifact. |
| **Secrets / env vars** | `FIRESTARTER_SIZE_BASELINE` (both gates), `FIRESTARTER_FW_ROOT`, `FIRESTARTER_META_ROOT` (binds at **import**, so it must be set in a child process, never monkeypatched). No secret is renamed or read by this phase. | None — but any invocation that overrides a seam must state so beside the figure it produced. |
| **Build artifacts / installed packages** | `.venv/ci-replica` (py **3.11.15**) exists and is the CI-parity interpreter; ambient `python3` is **3.12.13** with `pytest 9.1.1`; the app is installed **editable** into the venv, so a run launched from another directory can silently import the *worktree* package (`PYTHONPATH` proved decisive). | Pin the interpreter explicitly (`.venv/ci-replica/bin/python -m pytest`) and record which `firestarter/__init__.py` was imported (`3.0.0b20` in my run). |

**The canonical question, answered:** after the plan names its base commits, what still holds the old
truth? **Three cached `origin/beta` refs, six warm PlatformIO build caches, and a `size_baseline.json`
measured at a commit 57 commits behind the live beta tip.**

---

## Common Pitfalls

### Pitfall 1: Reading a squash merge as "never merged"
**What goes wrong:** `git merge-base --is-ancestor` exits 1; a plan concludes the work is unmerged
and re-merges it.
**Why:** GitHub's squash merge creates a single new commit with none of the branch commits as
ancestors, and `git cherry` reports every commit as `+` because patch-ids differ.
**How to avoid:** treat ancestry as **one** of four oracles. Add `comm -23` on `ls-tree -r --name-only`
(files present on the branch but not on the target), a `git diff --stat branch target` you can
attribute line-by-line, and `gh pr view <N> --json state,mergedAt,mergeCommit`.
**Warning signs:** the target branch has **more** tests than the "unmerged" branch (1532 vs 1508);
`git merge-tree` reports *added in both*.

### Pitfall 2: Recording a warm warning count as the baseline
**What goes wrong:** the watermark is set to the warm figure; the next **cold** CI run exceeds it and
goes RED for no code reason.
**Why:** PlatformIO reuses `.pio/build/<env>`; a warm re-run recompiles only some TUs, so
macro-redefinition warnings from the shim/ArduinoFake collision are emitted far fewer times.
**How to avoid:** `rm -rf .pio/build/<env>` then a single `pio test -e <env>` at `timeout: 540000`.
**Warning signs:** `998` (warm) instead of `1166` (cold) — reproduced live this session.

### Pitfall 3: A default 2-minute Bash timeout truncating a cold build
**What goes wrong:** the toolchain build dies mid-compile; the partial log still parses; a
contaminated figure gets committed.
**Why:** a cold AVR + native build exceeds 120 s comfortably.
**How to avoid:** `timeout: 540000` on **every** cold invocation; verify the log ends with
`[SUCCESS]` and a `N test cases:` line before parsing it.
**Warning signs:** no `RAM:`/`Flash:` pair (→ `check_size_baseline.py` exit 2), or a missing
`N test cases:` line.

### Pitfall 4: The recorder overflowing silently in the middle of the fixture
**What goes wrong:** the trace's tail is dropped, the prefix stays valid, and a naive comparator
still matches on the prefix.
**Why:** `strobe_push` sets `s_strobe_overflow = 1` and drops the tail; the 20-pass retry loop
generates ~960 strobes for an 8-byte block whose bytes never verify.
**How to avoid:** model read-back so the loop converges (R1/R2 above); assert
`strobe_overflowed() == 0` **first**, as `sdp_assert_stream_equals` already does; keep the block at
4–8 bytes and record the measured entry count in the inventory.
**Warning signs:** `strobe_count() == 512` exactly.

### Pitfall 5: The persistent `0xff` register cache contaminating the first case
**What goes wrong:** the first case's trace shows the VPP regulator enabled on a path that never
enables it; later cases produce a different stream from the same input.
**Why:** `lsb_address`/`msb_address`/`control_register` are **non-`static` globals initialised `0xff`**
in `rurp_register_utils.h`, persisting across Unity cases in one binary; `0xff` includes
`CTRL_VPP_REGULATOR_ENABLE (0x80)`.
**How to avoid:** define and call `reset_register_cache(lsb, msb, ctrl)` in every case, exactly as
both SDP suites do — and state whether a case seeds non-zero **deliberately**.
**Warning signs:** case 1 and case 2 disagree on an identical drive.

### Pitfall 6: Mocking the handle's function pointers before `configure_memory()`
**What goes wrong:** the mock is silently discarded and the real path runs.
**Why:** `configure_memory()` assigns **both** `firestarter_get_data` and `firestarter_set_data`.
**How to avoid:** install mocks **after** `configure_memory(&h)`, and re-assign **both** if either is
mocked (`test_sdp_harness.cpp:613-617` records this exact correction).

### Pitfall 7: Adding the new suite to a pinned native env
**What goes wrong:** `check_size_baseline.py` goes RED on cases/suites, and D-05 forbids rewriting the
live baseline to absorb it.
**How to avoid:** a dedicated fourth env, `test_filter` naming only the new suite, **not** in
`default_envs`; and do not pass that env name to either gate (`check_size_baseline.py` raises an
uncaught `KeyError` → exit 1, not the documented exit 2).

### Pitfall 8: Measuring the host suite on the wrong tree or interpreter
**What goes wrong:** the recorded count belongs to a feature branch, or to py3.12 rather than CI's
py3.11.
**Why:** the app worktree is currently on `fix/dev-test-blank-check-after-erase`; the ambient
interpreter is 3.12.13; the package is installed **editable**, so a run from elsewhere can import the
worktree copy.
**How to avoid:** `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q`, run **in**
`/workspaces/firestarter_app`, with the branch and `firestarter.__version__` recorded beside the count.

### Pitfall 9: Doubling `-q` and losing the count line
**What goes wrong:** the summary count disappears from the output.
**Why:** `pyproject.toml` sets `addopts = "-ra -q"`; adding another `-q` reaches `-qq`.
**How to avoid:** `-o addopts=""` whenever the count is the datum. (Measured: works.)

### Pitfall 10: Writing an "empty git diff" acceptance criterion for flag-off
**What goes wrong:** the criterion breaks the moment a later `#if` guard legitimately changes bytes.
**How to avoid:** scope flag-off proof to **assertions-unchanged** plus **named blob SHAs**, and prove
behaviour by re-asserting 141 cases / 17 suites / all PASSED on **both** pinned envs.

---

## Code Examples

### Read-only branch adjudication (four oracles, no writes)

```bash
# Source: measured live this session, firestarter_app
git merge-base --is-ancestor gsd/v1.30-sdp-surface-retirement origin/beta ; echo "ancestry=$?"   # 1
git cherry origin/beta gsd/v1.30-sdp-surface-retirement | awk '{print $1}' | sort | uniq -c      # 85 '+'
comm -23 <(git ls-tree -r --name-only gsd/v1.30-sdp-surface-retirement | sort) \
         <(git ls-tree -r --name-only origin/beta | sort)                                        # EMPTY
git diff --stat gsd/v1.30-sdp-surface-retirement origin/beta                                     # 12 files, all attributable
gh pr view 44 --repo henols/firestarter_app --json state,mergedAt,mergeCommit                    # MERGED / 568e58b
gh api repos/henols/firestarter/git/refs/heads/beta --jq '.object.sha'                           # LIVE tip, not the cache
git merge-tree $(git merge-base origin/beta gsd/v1.30-sdp-surface-retirement) \
               origin/beta gsd/v1.30-sdp-surface-retirement | grep -E '^(changed|added) in both'
```

### Cold size + suite measurement, then the gate

```bash
# Source: size_baseline.json meta.note (procedure) + measured this session (figures)
cd /workspaces/firestarter
for e in uno uno328pb leonardo; do
  pio run -t clean -e "$e"
  pio run -e "$e" > "/tmp/$e.log" 2>&1          # timeout: 540000
done
for e in native native_nodevtools native_pinmap_provisional; do
  rm -rf ".pio/build/$e"
  pio test -e "$e" > "/tmp/$e.log" 2>&1          # timeout: 540000
done
python3 scripts/check_size_baseline.py \
  --avr-log uno=/tmp/uno.log --avr-log uno328pb=/tmp/uno328pb.log --avr-log leonardo=/tmp/leonardo.log \
  --native-log native=/tmp/native.log --native-log native_nodevtools=/tmp/native_nodevtools.log
python3 scripts/check_build_warnings.py --log native=/tmp/native.log --log native_nodevtools=/tmp/native_nodevtools.log
```

### Host suite count, CI-parity interpreter

```bash
# Source: measured this session — 1493 passed / 46 skipped / 0 failed at beta 4d18b64
cd /workspaces/firestarter_app
.venv/ci-replica/bin/python --version                                   # 3.11.15
.venv/ci-replica/bin/python -c "import firestarter; print(firestarter.__file__, firestarter.__version__)"
.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q           # never add a second -q
```

### Pulse distribution, bucketing from the RAW string (D-11)

```python
# Source: measured this session against blob ebd1eaac01698f64dc0861f8478b8931493d3bab
import collections, json, sys
sys.path.insert(0, "/workspaces/firestarter_app")
from firestarter.database import _parse_pulse_duration   # the SAME parser the CLI uses

TARGETS = {0x07, 0x08, 0x0B}
db = json.load(open("firestarter/data/chip_database.json"))
hist = collections.defaultdict(collections.Counter)
buckets = collections.defaultdict(collections.Counter)

for _mfr, ics in db.items():
    for ic in ics:
        prog = ic.get("programming", {}) or {}
        alg = prog.get("algorithm")
        if alg not in TARGETS:
            continue
        raw = prog.get("pulse_duration", None)           # bucket from RAW, never from the parsed int
        if raw is None:                    buckets[alg]["absent"] += 1
        elif not isinstance(raw, str):     buckets[alg][f"non-string:{type(raw).__name__}"] += 1
        elif raw == "":                    buckets[alg]["empty"] += 1
        elif raw == "Algorithm Controlled":buckets[alg]["algorithm-controlled"] += 1
        else:
            us = _parse_pulse_duration(raw)
            if us == 0 and raw.strip() != "0 us":  buckets[alg][f"unparseable:{raw!r}"] += 1
            elif us == 0:                          buckets[alg]["explicit-zero"] += 1
            else:                                  hist[alg][us] += 1
```

### The timing hook (new suite `setUp()`)

```cpp
/* Source: fakeit 'AlwaysDo' with arg capture, per test_messages/serial_read_mock.h:94.
 * host_stubs_common.inc supplies timing_push() behind HOST_STUBS_RECORD_TIMING. */
extern "C" void    clear_timings();
extern "C" int     timing_count();
extern "C" int     timing_overflowed();
extern "C" uint8_t timing_kind(int i);      /* DELAY_MS | DELAY_US */
extern "C" uint32_t timing_us(int i);
extern "C" int     timing_after_strobe(int i);   /* s_strobe_count at push time -> interleave key */

void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    When(Method(ArduinoFake(), delay)).AlwaysDo([](unsigned long ms) {
        timing_push(TIMING_KIND_DELAY_MS, (uint32_t)ms);
    });
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysDo([](unsigned int us) {
        timing_push(TIMING_KIND_DELAY_US, (uint32_t)us);
    });
    clear_strobes();
    clear_timings();
    reset_register_cache(0x00, 0x00, 0x00);   /* Pitfall 5 — non-static 0xff globals */
}
```

### Single-commit fixture + inventory (no two-commit dance)

```bash
# Source: measured — both return dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83
git rev-parse HEAD:test/native/avr/_shared/sdp_expected.h
git hash-object      test/native/avr/_shared/sdp_expected.h    # same SHA, no commit needed
```

---

## State of the Art (what changed since CONTEXT.md was written)

| CONTEXT.md / roadmap claim | Current reality | Verified how | Impact |
|---------------------------|-----------------|--------------|--------|
| "`gsd/v1.30-…` is **NOT** an ancestor of `origin/beta` … PREP-01 is genuinely open" | Ancestry is still 1, but PR **#44** is **MERGED** (squash `568e58b`, 2026-08-05). Content-equivalent; a re-merge conflicts. | `gh pr view 44`; `comm -23`; `git merge-tree` | PREP-01 becomes an **adjudication + wording correction**, not a merge |
| "`firestarter`'s `origin/beta` tip **is exactly `3085084`** … no drift" | Live tip is **`6fab4ea`**, 2 ahead (incl. `src/firestarter.cpp` +37) | `gh api …/refs/heads/beta` | PREP-02's firmware base needs an explicit decision: the *decided* `3085084` or the *live* tip |
| "There is no local `beta` branch in the firmware repo" | A local `beta` **exists** and is at `3085084` | `git branch --list` | A plan that forks "off `origin/beta`" and one that forks "off `beta`" would get different commits once the cache is refreshed |
| "`delay()` / `delayMicroseconds()` are not stubbed at all" | Not in `host_stubs_common.inc` — but **defined by ArduinoFake** and already mocked in **8** suites' `setUp()` | ArduinoFake `FunctionFake.{h,cpp}`; `grep` of `test/` | The timing layer's seam is fakeit `.AlwaysDo`, not a `.inc` definition |
| "`HOST_STUBS_REAL_REGISTER_UTILS` composes with `HOST_STUBS_RECORD_BUS`" (the `.inc`'s own comment) | `#ifdef … #elif …` — defining both yields **only** the strobe recorder | `host_stubs_common.inc:81/131/153` | A fixture wanting `(reg,data)` must derive it from strobes |
| `eprom.cpp:283` is the program pulse | `:283` is the **erase** pulse; the **program** pulse is `memory.cpp:329` | source read | `memory.cpp` is also on the write path and also must not be edited in 138 |
| The size gate "is plausibly already RED … since the live baseline was measured at Phase 124's tree (`2bd7187`)" | `2bd7187` **is** an ancestor of beta (57 commits behind) yet the gate is **GREEN at `3085084`** and **RED only at `6fab4ea`** (+34 B ×3) | ran the gate both ways | D-07 still fires, but the finding's owner and cause are `b1737b2`, not v1.23-era debt |
| BASE-01 native watermark 360 | Live baseline records **1166 cold / 998 warm**; I reproduced **998** warm | `check_build_warnings.py` | Never cite 360; and never source a watermark from a warm run |

**Deprecated / superseded:**
- The premise *"v1.30's PR was staged and never opened"* — appears in `REQUIREMENTS.md` (PREP-01),
  `ROADMAP.md` §Branch model, `STATE.md` §BLOCKING PRECONDITION, and `CONTEXT.md`. **All four are now
  stale.** `.planning/v1.30-PR-BODY.md` remains on disk as an unused draft.
- The 141/17 figure is *env-scoped*, not repo-scoped: there are **three** native envs (141/17,
  141/17, 10/1), and BASE-01 records only the first two.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | The strobe/timing entry-budget arithmetic (≈7 strobes + 3 timings per programmed byte; 4-byte × 3-pass ≈ 174) is **derived from source**, not measured by running a fixture — no fixture exists to run. | Trace Capture Mechanism | If the real count is materially higher, the chosen block length may overflow. Mitigation: the plan must **dump and count empirically** before freezing (which D-01's "author it empirically" already requires). |
| A2 | Recommending **R2** (a `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` opt-out) over **R1** (pointer swap) on fidelity grounds is a judgement, not a measurement. | Trace Capture Mechanism | R2 is a slightly larger `.inc` change. Either satisfies D-02/D-04; R1 has direct precedent. Planner's call. |
| A3 | `handle->bus_config` must be non-degenerate for the write-path trace to be meaningful. I read `mem_util_remap_address_bus`'s call sites but did **not** execute a zero-`bus_config` remap. | Trace Capture Mechanism | If a zeroed `bus_config` happens to be an identity remap, the sourcing problem in Q1 evaporates. Cheap to settle: one probe in the plan's first trace task. |
| A4 | The next app pre-release after a further `beta` push would be `3.0.0b21`. Derived from the tag-scan rule + 19 cached `3.0.0b*` tags. | CI Evidence | A tag landing between now and execution shifts the number. Never hardcode it; read `firestarter/__init__.py` on the post-bump tip. |
| A5 | The GitHub-API `outcome` vs `conclusion` distinction is described from training knowledge plus `131-CI-BASELINE.md`'s in-repo statement of the v1.23 lesson; I did not re-read GitHub's API reference this session. | `131-CI-BASELINE.md` shape | Low — the in-repo record is authoritative for this project's practice regardless. |
| A6 | "Squash merges make `--is-ancestor` a false negative" is standard git behaviour, asserted from knowledge **and** consistent with every measurement here (single parent, 85 `+` in `git cherry`, empty `comm -23`). | Branch & Ancestry | None material — the four oracles stand on their own. |

---

## Open Questions (RESOLVED)

> All five were settled before planning completed. Each carries an inline
> **RESOLVED** marker naming its resolver: an operator decision taken during the planning run
> (OD-1/OD-2/OD-3, recorded in the plan-phase dispatch context) or the plan and task that settles it.
> The questions' substance below is left exactly as researched; only the resolution markers are added.

1. **Where does the trace fixture's `bus_config` come from?**
   - *Known:* `memory_set_data` → `mem_util_remap_address_bus(handle, address, WRITE_FLAG)`.
     `test/native/avr/_shared/sdp_bus_config.h` is generated by `tools/gen_sdp_bus_config.py` from
     `firestarter_app/firestarter/data/pinouts.json` but carries only **5 rows, all 28C**.
   - *Unclear:* whether to extend that generator to emit 27C rows (cross-repo, principled, honours
     "generated files are never hand-edited") or to document a minimal in-fixture bus_config.
   - *Recommendation:* probe a zeroed `bus_config` first (A3). If degenerate, prefer **extending the
     generator** — it is the only route that keeps the trace's addresses traceable to `pinouts.json`.
   - **RESOLVED — plan `138-03` Task 3.** A3's probe was settled from source rather than by execution:
     `mem_util_remap_address_bus` opens with `config.address_mask & address` (`src/proms/memory.cpp:358`),
     so a zeroed `bus_config` collapses every address to 0 — **degenerate, not identity**. The generator
     is **not** extended (it lives in `firestarter_app/tools/`, not the firmware repo, and its
     `validate_rows` rejects a pinout carrying `static-high-pins`, which `DIP24_2716` does — that is an
     app-repo change regenerating a header two frozen SDP suites consume, outside this phase's fence).
     Instead the plan derives each row through the generator's own `derive_row` — the host's live
     `EpromDatabase.get_eprom()` plus `convert_to_programmer()` path — for AM27C512 / AM27C020 / AM2716,
     translating the residual fields exactly as `src/json_parser.c:401-436` does, with the derivation
     command recorded beside each literal. The generator gap is carried as finding **F-138-07** with an
     owner.

2. **Which firmware base does PREP-02 name — `3085084` (decided) or `6fab4ea` (live)?**
   - *Known:* the roadmap and CONTEXT lock `3085084`; the live tip is 2 ahead; the size gate is GREEN
     at the former and RED at the latter (+34 B ×3); MERGE-05's uno-class band has only **8 B / 2 B**
     of headroom left at the live tip.
   - *Recommendation:* **operator decision, surfaced explicitly in the plan.** Forking at `3085084`
     keeps the gate green and the baseline citable but deliberately omits a landed protocol change
     that Phase 143/144 will meet anyway. Do not silently pick one.
   - **RESOLVED — OD-2** (operator, during the planning run). Firmware forks at the **decided base
     `3085084`**: a base whose own size gate arrives RED would make every downstream TEST-08 delta measure
     against a broken reference, and D-07 forbids fixing it. The drift to the live tip, the uniform flash
     delta and the MERGE-05 band headroom are carried forward as finding **F-138-02** with explicit
     owners (Phase 144 / TEST-08 and Phase 143/144), recorded in `138-BRANCH-BASES.md` section 5 by plan
     `138-01` Task 2.

3. **Should PREP-02 advance the meta repo's submodule gitlinks?**
   - *Known:* the index points at `firestarter`→`0933bd7`, `firestarter_app`→`cc036e8`, both stale
     against the worktrees; `CLAUDE.md` says the sub-repos are "not committed here" yet `.gitmodules`
     and the gitlinks exist.
   - *Unclear:* whether "milestone branches exist … verified by naming the base commit" implies the
     meta repo should record those tips.
   - *Recommendation:* record the base commits in the **narrative artifact**; leave the gitlinks
     alone unless the operator asks — a gitlink bump is a meta commit with no stated requirement.
   - **RESOLVED — OD-3** (operator, during the planning run). The gitlinks are **not** advanced. The three
     verified base commits are named in the narrative artifact only, and the resulting `M firestarter` /
     `M firestarter_app` status lines are recorded as expected rather than as dirt, under finding
     **F-138-03** in `138-BRANCH-BASES.md` section 6 (plan `138-01` Task 2).

4. **How is PREP-01 discharged given the requirement's premise is false?**
   - *Recommendation:* a named finding (`F-138-01`) with the four-oracle evidence, an explicit
     "requirement wording superseded by measurement" note, and the corrected criterion
     (**content-equivalence**, not ancestry). This mirrors `131-CI-BASELINE.md` §5's F-07 handling and
     §8's "the measured number wins" rule.
   - **RESOLVED — OD-1** (operator, during the planning run), implemented by plan `138-01` Tasks 1 and 3.
     PREP-01 is discharged as **F-138-01**, a content-equivalence adjudication with all four oracles
     re-run live at execution; the requirement's wording is corrected in place from ancestry to content
     equivalence; **D-08 is a no-op** — no PR is opened and no operator merge is requested, because the
     pre-release D-08 predicted already happened.

5. **Is the `check_size_baseline.py` unknown-env `KeyError` in scope to record?**
   - *Recommendation:* yes — as a **second** D-07-class finding with an owner, not a fix. It becomes
     load-bearing the moment a fourth native env exists.
   - **RESOLVED — plan `138-06` Task 3.** Recorded as finding **F-138-05** with owner `henols`, covering
     both the uncaught `KeyError` exiting 1 where the script's own taxonomy promises 2 **and** the
     hardcoded `NATIVE_ENVS` that makes the phase's new fourth env invisible to both live gates. The
     gate-blindness is stated as accepted-and-recorded with its compensating control (the env's counts
     live in `size_baseline_v131.json` and in `envs_agree_note`, and the env is never passed to either
     checker). Neither checker is modified — D-07.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `pio` (PlatformIO Core) | all firmware measurement | ✓ | **6.1.19** (matches baseline `meta`) | none — blocking |
| avr-gcc toolchain | AVR flash/RAM | ✓ | **7.3.0** (matches baseline) | none — blocking |
| `platform-atmelavr` | AVR builds | ✓ | **5.2.0** (matches baseline) | none |
| ArduinoFake | native suites | ✓ | **0.4.0** (`lib_deps` pin `^0.4.0`) | none |
| `git` | fixture blob SHA, history gates | ✓ | on PATH | **none — gates fail closed by design** |
| `gh` CLI, authenticated | live tips, PR state, CI run ids | ✓ | logged in as `henols` (`gho_…`) | none for CI evidence |
| `python3` (ambient) | firmware `tests/` | ✓ | **3.12.13**, `pytest 9.1.1` | — |
| `.venv/ci-replica/bin/python` | host suite at CI parity | ✓ | **3.11.15** | ambient 3.12 **masks CI** — do not substitute |
| Bench hardware | — | n/a | — | Phase 138 needs none |
| Network (GitHub API + tarballs) | live-tip verification | ✓ | — | none — a stale cache is exactly the trap |

**Missing dependencies with no fallback:** none.
**Notable:** `gh workflow run` is blocked by the auto-mode classifier (recorded), which is *why* D-06
makes CI dispatch an operator action; read-only `gh run view` / `gh api` work fine and were used
throughout this research.

---

## Validation Architecture

### Test framework

| Property | Value |
|----------|-------|
| Framework (firmware native) | PlatformIO **Unity** (`test_framework = unity`), 3 native envs |
| Framework (firmware gates) | **pytest** (stdlib + pytest only; **no `conftest.py` anywhere** — a recorded house rule) |
| Framework (host) | **pytest** + `pytest-cov` + snapshot plugin, `addopts = "-ra -q"`, `testpaths = ["tests"]` |
| Config files | `firestarter/platformio.ini`; `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run (firmware gates) | `cd /workspaces/firestarter && python3 -m pytest tests/ -q` → **221 passed, 8.8 s** |
| Quick run (host, targeted) | `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/<file> -o addopts="" -q` |
| Full suite (firmware) | `pio test -e native` · `-e native_nodevtools` · `-e native_pinmap_provisional` (≈50 s each warm) |
| Full suite (host) | `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` → **179 s** |

### Phase requirements → test map

| Req | Behaviour | Test type | Automated command | Exists? |
|-----|-----------|-----------|-------------------|---------|
| PREP-01 | v1.30 content is on `beta` (four oracles) | integration (git/gh) | `git merge-base --is-ancestor …; git cherry …; comm -23 …; gh pr view 44 --json state,mergedAt,mergeCommit` | ✅ commands exist; ❌ no committed checker |
| PREP-02 | each v1.31 branch names a **verified** base commit | integration (git) | `git rev-parse <branch>` + `git merge-base --is-ancestor <base> <branch>` per repo | ✅ |
| PREP-03 AVR | flash/RAM equal the committed record | unit (gate) | `python3 scripts/check_size_baseline.py --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…` | ✅ exit-code gate |
| PREP-03 native | 141/141/17 + all PASSED on both pinned envs | unit (gate) | same script, `--native-log native=… --native-log native_nodevtools=…` | ✅ |
| PREP-03 warnings | native ≤ watermark, AVR == 0 | unit (gate) | `python3 scripts/check_build_warnings.py --log <env>=<log>` | ✅ |
| PREP-03 fixture immutability | blob SHA + per-array inventory + non-vacuity + consumer inclusion + no-skip | unit (pytest) | `python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q` | ❌ **Wave 0** |
| PREP-03 trace content | ordered merged strobe+timing stream equals the frozen fixture, overflow == 0 | unit (Unity) | `pio test -e native_trace_v131` | ❌ **Wave 0** |
| PREP-03 flag-off byte-exactness | all 17 pre-existing suites unchanged with the new guard undefined | integration | `pio test -e native && pio test -e native_nodevtools` → re-assert 141/17/all-PASSED via the gate | ✅ (mechanism exists) |
| PREP-03 host counts | host suite count recorded at a named tree + interpreter | integration | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` | ✅ |
| PREP-04 | distribution re-derived, buckets explicit, reproducible | unit (script, self-checking) | `python3 .planning/phases/138-preconditions-baseline/138-pulse-distribution.py` | ❌ **Wave 0** |

### Sampling rate

- **Per task commit:** the narrowest thing that can go RED — the gate or single pytest module the task
  touched (`check_size_baseline.py …`, or `pytest tests/test_golden_trace_identity_eprom_v131.py -q`).
- **Per wave merge:** `pio test -e native && pio test -e native_nodevtools && pio test -e native_pinmap_provisional`
  + `python3 -m pytest tests/ -q` (firmware) and the full host suite (host waves).
- **Phase gate:** every gate green **and** the three native envs at their recorded counts **and** the
  new fixture's identity module green, before `/gsd-verify-work`.

### Wave 0 gaps

- [ ] `firestarter/test/native/avr/_shared/host_stubs_common.inc` — additive `HOST_STUBS_RECORD_TIMING`
      block (storage + `timing_push` + accessors), plus (if R2) a `HOST_STUBS_CUSTOM_READ_DATA_BUFFER`
      opt-out guard around the currently-unguarded `rurp_read_data_buffer` — covers PREP-03
- [ ] `firestarter/test/native/avr/_shared/eprom_v131_expected.h` — frozen fixture + comparator over
      the merged stream — covers PREP-03
- [ ] `firestarter/test/native/avr/test_trace_eprom_v131/{host_stubs.cpp,test_trace_eprom_v131.cpp}` —
      the new suite (incl. `reset_register_cache` and the pulse-counting read-back model)
- [ ] `firestarter/platformio.ini` — `[env:native_trace_v131]` (1-entry `test_filter`, matching `-I`,
      **not** in `default_envs`, `build_flags` from `${env:native.build_flags}`)
- [ ] `firestarter/tests/golden/eprom_v131_trace_inventory.json` + `firestarter/tests/test_golden_trace_identity_eprom_v131.py`
- [ ] `firestarter/scripts/baseline/size_baseline_v131.json` — new immutable freeze (BASE-01 schema)
- [ ] `.planning/phases/138-preconditions-baseline/138-BASELINE.md` — narrative artifact in
      `131-CI-BASELINE.md` shape
- [ ] `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` + its committed verbatim
      output artifact — covers PREP-04
- [ ] No framework install needed — Unity, pytest, and the CI-parity venv all exist.

---

## Security Domain

| ASVS category | Applies | Standard control |
|---------------|---------|------------------|
| V2 Authentication | no | Phase 138 authenticates nothing; `gh` uses the operator's existing token |
| V3 Session management | no | — |
| V4 Access control | **yes (process, not code)** | Outward actions are operator-gated: PR merge, CI dispatch, branch push. The agent uses **read-only** `gh api` / `gh run view` / `gh pr view` only |
| V5 Input validation | **yes (weakly)** | The PREP-04 script parses a **committed, generated** JSON. It must not `eval`, must not follow paths outside its documented seams, and must fail loudly on a non-string `pulse_duration` (measured: `_parse_pulse_duration(100)` raises `AttributeError`) |
| V6 Cryptography | no (consumes only) | Blob identity uses git SHA-1 object hashing via `git hash-object` / `git rev-parse` — never a hand-rolled digest |
| V12 Files & resources | **yes** | Cold measurement deletes `.pio/build/<env>` — a gitignored build dir. Never `rm -rf` anything tracked; `firestarter_app/.planning/codebase/` is a recorded do-not-delete |
| V14 Configuration | **yes** | Env seams (`FIRESTARTER_SIZE_BASELINE`, `FIRESTARTER_FW_ROOT`, `FIRESTARTER_META_ROOT`) must be set in a **child process** (the last binds at import), and any override must be stated beside the figure it produced |

| Threat | STRIDE | Mitigation |
|--------|--------|-----------|
| A baseline figure recorded from a warm build and cited as cold | **Tampering** (of the record) | `rm -rf .pio/build/<env>` + single invocation at `timeout: 540000`; record warm **and** cold where they differ, as the live baseline already does |
| A "verified" branch base read from a stale cached `origin/beta` | **Spoofing** (of provenance) | Resolve every base against the live ref via `gh api …/git/refs/heads/beta`; name the SHA in the artifact |
| A frozen fixture silently gutted together with its assertions | **Tampering** | The five-part inventory gate: blob SHA · ordered names · positional entry counts · non-vacuity floor · consumer-inclusion |
| A gate that examined nothing reporting PASS | **Repudiation** | Both checkers' never-vacuous guards (exit 1 on zero envs compared) — retain, never bypass |
| A `git` absence turning the identity pin into a silent skip | **Tampering** | `_resolve_git()`'s plain `assert` + the self-scanning `test_git_is_required_not_optional`; copy both into the new module |
| An unauthorised outward action (merge/dispatch/post) | **Elevation of privilege** | D-06/D-08: agent opens at most a PR and reads runs; merge, dispatch and issue posts are operator-only. `gh workflow run` is additionally blocked by the auto-mode classifier |

---

## Project Constraints (from CLAUDE.md)

**Meta `/workspaces/CLAUDE.md`:**
- The meta repo tracks **only** `.planning/` and `.claude/`; neither sub-repo's content is committed
  here. → the trace fixture, `size_baseline_v131.json`, and any firmware/host code land **inside the
  submodules**, on the milestone branch, committed there; only narrative artifacts and the PREP-04
  script/output land in meta.
- Protocol changes must stay in sync between `firestarter_app/firestarter/serial_comm.py` and
  `firestarter/src/firestarter.cpp`. → Phase 138 changes no protocol; note that the *live beta drift*
  (`b1737b2`) is exactly such a change, already landed on the firmware side.
- Constants/flag bits are duplicated between `constants.py` and `include/firestarter.h` — change both
  together. → not touched in 138.
- `chip_database.json` user overrides live in `~/.firestarter/database.json`. → **PREP-04 must read
  the shipped `firestarter/data/chip_database.json` directly, or construct `EpromDatabase(skip_local_override=True)`;
  a plain `EpromDatabase()` merges the operator's local overrides and would silently skew the
  distribution.**

**`firestarter/CLAUDE.md`:**
- `pio test -e native` / `-e native <filter>` are the documented native invocations.
- **A new suite needs `test_filter` *and* a matching `-I` entry, in *every* env that should run it**
  (explicitly corrected under "Reuse pattern for future native tests").
- `include/messages.h` is **codegen-generated** — never hand-edit (not touched in 138).
- `doc/SHIELD-REVISIONS.md` and `platform/py32f071/FLASH-PATH-AND-PCB.md` are lockstep clones of meta
  records (not touched in 138).

**`firestarter_app/CLAUDE.md`** (read via the submodule): `chip_database.json` is **generated** —
never hand-edit; fix the decode function instead. → PREP-04 **reads only**.

**Global user instruction:** `/graphify` maps to the installed graphify skill. Not triggered here.

---

## Sources

### Primary (HIGH confidence — read or executed this session)

- `firestarter/test/native/avr/_shared/host_stubs_common.inc` (all 272 lines) — both recorder layers,
  the opt-IN contract, the `#ifdef/#elif` non-composition, the unguarded `rurp_read_data_buffer`
- `firestarter/test/native/avr/_shared/sdp_expected.h` — frozen-fixture form, comparators, array format
- `firestarter/tests/golden/sdp_expected_inventory.json` — inventory schema
- `firestarter/tests/test_golden_trace_identity.py` (all 246 lines) — the six assertions, fail-closed git
- `firestarter/scripts/baseline/size_baseline.json` — `meta.note`, `meta.warm_vs_cold_correction`,
  `envs_agree_note`, `warnings.counting_command`
- `firestarter/scripts/baseline/size_baseline_base01.json` — the freeze schema
- `firestarter/scripts/check_size_baseline.py` (all 488 lines) — seam, modes, `AVR_ENVS`/`NATIVE_ENVS`,
  `_rebuild_native`'s missing clean, `compare_native`'s `KeyError`
- `firestarter/scripts/check_build_warnings.py` (header) — the shared seam, policy, exit taxonomy
- `firestarter/platformio.ini` (all 291 lines) — 3 native envs, the 17/141 hard constraint, the
  third-env precedent
- `firestarter/src/proms/eprom.cpp`, `firestarter/src/proms/memory.cpp`,
  `firestarter/include/rurp_register_utils.h`, `firestarter/include/rurp_shield.h`
- `firestarter/test/native/avr/test_val_eprom/{host_stubs.cpp,test_val_eprom.cpp}`,
  `test_sdp_harness/host_stubs.cpp`, `test_eeprom28c_sdp/host_stubs.cpp`
- `firestarter/.pio/libdeps/native/ArduinoFake/src/{FunctionFake.h,FunctionFake.cpp,fakeit.hpp}` — 0.4.0
- `firestarter/.github/workflows/{build.yml,beta-build.yml}`
- `firestarter_app/firestarter/database.py`, `firestarter_app/firestarter/data/chip_database.json`
- `firestarter_app/doc/infoic-field-dictionary.md` §`pulse_delay` — C1's adjudication table
- `firestarter_app/.github/workflows/{beta-release.yml,ci.yml}`, `.github/scripts/update_version.py`
- `firestarter_app/pyproject.toml` — `addopts = "-ra -q"`, `requires-python >= 3.9`, ruff `py39`
- `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md` (all 187 lines)
- `.planning/phases/136.1-sdp-partition-provenance/136.1-check-blast-radius.py` + `136.1-01-BLAST-RADIUS.md`
- `.planning/{ROADMAP.md,REQUIREMENTS.md,STATE.md,v1.30-PR-BODY.md}`,
  `.planning/phases/138-preconditions-baseline/{138-CONTEXT.md,138-DISCUSSION-LOG.md}`
- **GitHub API (read-only)**: `gh pr view 44`, `gh pr list --state all`,
  `gh api repos/henols/{firestarter,firestarter_app}/git/refs/heads/beta`,
  `gh api …/compare/<a>...<b>`, `gh api …/tarball/<sha>`, `gh api …/contents/firestarter/__init__.py?ref=beta`
- **Live measurements**: 3 AVR envs at two commits · 3 native envs · both firmware gates in 3
  invocations · firmware `tests/` in 2 locations · host suite at 4 refs · the pulse distribution ·
  11 `_parse_pulse_duration` edge cases

### Secondary (MEDIUM confidence)

- In-repo prose records used for *rationale* rather than fact: `platformio.ini`'s Phase-119/124
  comments, `size_baseline.json`'s `envs_agree_note`, `131-CI-BASELINE.md` §5's F-07 narrative.

### Tertiary (LOW confidence — flagged, not relied on)

- Standard git squash-merge semantics and the GitHub `outcome`/`conclusion` distinction (A5, A6) —
  asserted from knowledge, corroborated by in-repo records and by every measurement here. No external
  documentation was fetched this session; none was needed, since every dependent claim is separately
  measured.

---

## Metadata

**Confidence breakdown:**
- **Branch/ancestry facts:** HIGH — every row measured live with read-only commands plus the GitHub API;
  four CONTEXT.md claims falsified with named evidence.
- **Baseline figures & gate outcomes:** HIGH — all figures produced by real builds/tests this session;
  both gates actually executed; RED and GREEN each demonstrated on a named tree.
- **Pulse distribution:** HIGH — measured against a blob SHA that is identical on all four candidate
  trees; reproduces the seed's C2 numbers exactly; all D-11 buckets enumerated empirically.
- **Trace mechanism (existing state):** HIGH — read every relevant line of the `.inc`, both SDP suites,
  ArduinoFake's `delay` definition, and the two write-path TUs.
- **Trace mechanism (recommended design):** MEDIUM — the seam and the precedents are verified; the
  entry-budget arithmetic (A1), the R1-vs-R2 choice (A2), and the `bus_config` requirement (A3) are
  reasoned from source and must be settled empirically in the plan's first trace task.
- **CI mechanics:** HIGH — every trigger, `paths-ignore`, dispatch capability, and publish boundary
  read from the workflow files; the app/firmware dispatch asymmetry is a source-level fact.
- **Pitfalls:** HIGH — 6 of 10 were reproduced live (warm-vs-cold 998/1166; squash false negative;
  directory-name dependence; git-absence fail-closed; `KeyError` vs exit 2; `-o addopts=""`).

**Research date:** 2026-08-08
**Valid until:** **≈3 days for the branch/tip facts** — both submodules' `beta` moved twice within the
36 hours before this research, and the app's `beta` moved *after* its own fetch cache was written.
**Re-verify every SHA at execution time.** ~30 days for the mechanism, schema, and pitfall findings.
