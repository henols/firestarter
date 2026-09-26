# Phase 123: Non-Regression Baselines & Gate Hardening - Research

**Researched:** 2026-07-30
**Domain:** Build-measurement baselines, fail-closed source-scanning gates, planted-fixture checker discipline (Python/pytest + PlatformIO/avr-gcc)
**Confidence:** HIGH — every load-bearing number in this document was measured in this session on this machine, not recalled.

---

## Summary

This phase is almost entirely *measurement* and *mechanism*, and both were verifiable directly. I
rebuilt all three AVR targets from clean, ran both native test environments, ran both host suites,
compiled a macro-redefinition fixture against both candidate compilers, and empirically tested the
git behaviour behind D-12's flagged trap. Nine of the ten questions posed to research are now
answered with measured facts rather than inference.

**The single highest-value result: the two native environments agree exactly — `pio test -e native`
and `pio test -e native_nodevtools` both report 141 test cases / 17 suites, all passing.** D-04's
live risk to Phase 124 does not materialise. MERGE-06 as currently worded is satisfiable and needs
no amendment. Phase 124 can be planned against a single `{141, 17}` pair, while the baseline JSON
still records them separately per D-04's letter.

The AVR flash/RAM figures in ROADMAP/BASE-01 are all confirmed byte-exact, and the one genuinely
missing number (uno328pb RAM) is now measured at 1579 B. But three CONTEXT/ROADMAP framings are
wrong in ways that change the plan: **BASE-06's "hold macro-redefinition warnings at zero" is
already true for the AVR builds and already false by 360 for the native builds**; **D-12's git trap
is worse than stated — git refuses the nested `.git` silently at exit 0**; and **D-08's naming
convention holds for only 4 of the 7 existing checkers**, so a repo-wide convention meta-test goes
red on arrival. A fourth correction affects both D-06 and D-14: in both firmware workflows
`pytest tests/ -v` runs *before* `pio run`, so the AVR toolchain is not installed when the new tests
execute.

**Primary recommendation:** Plan the baseline comparator and the four checkers exactly as CONTEXT
specifies, but (a) scope BASE-06's zero-tolerance rule to the three AVR envs and give the two native
envs a watermark of 360, (b) use host `g++` for the BASE-06 fixture compile, (c) build the D-12
fixture as a committed tree with a non-`.git` marker filename that the pytest materialises into a
`tmp_path` copy, and (d) scope D-08's meta-test to checkers introduced in v1.23 rather than
repo-wide.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Baseline record (BASE-01)**

- **D-01:** The baseline is **machine-readable JSON plus a comparator script** that rebuilds and
  exits non-zero on violation — not a prose table. This is what turns MERGE-05's *"Leonardo flash
  must not grow / Uno-class ≤ 64 B"* into an exit code instead of a human comparing two numbers.
- **D-02:** Baseline JSON and comparator live in the **firmware repo** (`firestarter/`), with the
  paired pytest in `firestarter/tests/`. The comparator must run `pio` builds, so it belongs where
  the build is; it supersedes `firestarter/scripts/check_uno_ram.sh`'s hardcoded `RAM_FLOOR=545`.
- **D-03:** **Every number is re-measured in this phase** on a clean build, each recorded with the
  firmware tree SHA plus the pio/toolchain version that produced it. The ROADMAP figures
  (Leonardo 26072/2014, Uno 23932/1573, uno328pb 23976, native 141/17) are a **cross-check only** —
  where a fresh measurement disagrees, the measured number wins and the discrepancy is recorded
  explicitly in the JSON's meta block. Note `uno328pb` has **no RAM figure anywhere**; it must be
  measured regardless.
- **D-04:** `native` and `native_nodevtools` each get **their own `{cases, suites}` pair**, plus a
  recorded measured fact of whether the two agree. MERGE-06 (Phase 124) reads as if they are equal;
  both carry 17 `test_filter` entries but `native_nodevtools` compiles without `-D DEV_TOOLS`, so
  case counts may legitimately differ. **If they differ, MERGE-06 as currently worded is
  unsatisfiable and Phase 124 must be told, not left to discover it.**

**Checker home & execution surface (BASE-04…BASE-08)**

- **D-05:** MERGE-07's *"gates run, never skip"* is discharged by a **local run with recorded
  verbatim evidence** in the phase artifact — the `122-NONREGRESSION.md` pattern. **No cross-repo
  CI leg is added.** Standalone-CI skipping (commit `81fa53c`, a deliberate v1.22 decision) stands:
  with no sibling, the skip is honest. A CI leg would also test against `beta` — the wrong tree —
  for the whole milestone, since the matching firmware commit lives on an unpushed milestone branch.
- **D-06:** **Scan-target-follows-home.** BASE-04/05/06 → `firestarter/scripts/` +
  `firestarter/tests/`, where they run in firmware CI unconditionally (`build.yml:108` and
  `beta-build.yml:66` both run `pytest tests/ -v`). BASE-07 → `.planning/phases/123-…/`, alongside
  v1.22's `check_permitted_claims.py`, because its scan targets are meta-repo closing artifacts.
  **No new checker becomes cross-repo**, so none inherits the skip class BASE-02/03 exists to kill.
- **D-07:** Checkers whose real scan target does not exist yet (BASE-04 scans
  `platform/py32f071/CMakeLists.txt`; BASE-05 scans for `RURP_*_PROVISIONAL` — **neither exists at
  Phase 123**) use a **coarse-key arm**, mirroring BASE-02's own `../firestarter/.git` idiom one
  level down: `platform/py32f071/` directory present ⇒ **armed**, and a missing or unresolvable
  fine-grained target is then a **hard failure**. Directory absent ⇒ checker reports **UNARMED**
  with a notice naming Phase 124. **No manual arm-flip** — it self-arms the moment the merge lands,
  and a rename inside the port cannot disarm it.
- **D-08:** BASE-08 is enforced by a **convention-derived meta-test**:
  `scripts/check_X.py` ⇒ `tests/test_check_X.py` ⇒ `tests/fixtures/planted_X*`, with a **hardcoded
  floor count** so a zero-match glob fails instead of passing vacuously. No registry file — the
  filesystem convention is the single source of truth, matching the host repo's existing
  checker↔test pairs.

**Fail-closed blast radius (BASE-02, BASE-03)**

- **D-09:** **All 7** proxy-carrying modules are rekeyed to `../firestarter/.git` in one pass, plus
  a **recurrence lint** over `tests/` forbidding the bare `not <file>.exists()` absence idiom from
  reappearing — with its own planted fixture per BASE-08. Which firmware file a 52-commit merge
  renames cannot be predicted, and without the lint the idiom returns in the next gate written.
- **D-10:** The skip census enforces a **committed allow-list of skip reasons** — an unrecognised
  reason fails the run; the firmware-absent reason additionally fails whenever `../firestarter/.git`
  exists. **No pinned skip count**: this suite already has environment-dependent behaviour (the
  no-programmer-found tests flip with a live board attached), so a count would be flaky and get
  bumped reflexively until it meant nothing. The allow-list doubles as documentation of every
  legitimate skip reason.
- **D-11:** Rename detection is **centralised**: one committed inventory of every cross-repo scan
  path, plus a single test that resolves all of them when `../firestarter/.git` exists and fails
  **naming each missing path**. The 7 modules' `skipif` then keys purely on `.git` (coarse and
  honest). This avoids re-creating the seven-way duplication that produced the fail-open idiom, and
  directly supplies Phase 124's *"manifest paths resolve"* artifact.
- **D-12:** The planted fixture is a **committed minimal fake firmware sibling** (repo-presence
  marker + deliberately incomplete file set) reached through an **env seam** defaulting to
  `../firestarter` — the same `FIRESTARTER_*_SRC` idiom v1.22's checkers use. Not monkeypatched
  constants (which prove the assertion fires, not that real resolution detects a real missing file)
  and not `tmp_path`-only (BASE-08 demands a *committed* fixture).
  **⚠ Planner trap:** a nested `.git` **directory** cannot be committed — the presence marker must
  be a committable form (a `.git` gitfile containing `gitdir:`, or an indirected marker the checker
  accepts).

**Gate shapes (BASE-06, BASE-07)**

- **D-13:** BASE-06 = **parse build output**: zero tolerance for macro-redefinition, **plus** a
  recorded **total-warning watermark** stored in the same BASE-01 baseline JSON, so any new warning
  of any kind fails. **Measured during discussion:** `gcc` has no `-Wmacro-redefined` — `cc1`
  rejects `-Werror=macro-redefined` outright (*"no option '-Wmacro-redefined'; did you mean
  '-Wbuiltin-macro-redefined'?"*); that spelling is Clang's. The warning is emitted by the
  preprocessor by default and is behind no named `-W` option, so **no targeted `-Werror` exists on
  avr-gcc** and blanket `-Werror` would make framework-header warnings fatal. The watermark is what
  delivers BASE-06's stated purpose (*"the next real warning is not buried"*), which the literal
  zero-macro rule alone does not.
- **D-14:** The BASE-06 planted fixture is a **committed `.cpp` under `firestarter/tests/fixtures/`
  compiled by a real compiler inside the pytest**, whose output is fed to the same parser the gate
  uses — proving both that a compiler still emits the warning and that the parser catches it.
  `firestarter/tests/` is PIO-invisible (PlatformIO globs `test/`, `src/`, `lib/`), so no real build
  is polluted and `platformio.ini` is untouched. **Known gap to record in the plan:** pio wraps
  compiler output, so the fixture exercises the warning line verbatim but not pio's surrounding
  framing.
- **D-15:** `check_permitted_claims.py` ships with the v1.23 closing artifacts **named in a
  committed default list** — recording the scan contract seven phases before anyone writes them —
  armed **all-or-nothing** per D-07: zero named targets exist ⇒ UNARMED notice, exit 0; **any one
  exists ⇒ armed**, and then every named target must exist, so a half-written close is a hard
  failure. Criterion 5's *"empty target list ⇒ non-zero"* property is proven **by the fixture
  pytest through the env seam**, not by the default run — which is exactly how criterion 5 words it.
- **D-16:** Forbidden phrases are **proximity-scoped**: a phrase fires only when it co-occurs with
  a `py32`/`PY32F071` token in the same line or sentence. v1.23's artifacts are largely a
  non-regression story about AVR targets that genuinely **are** bench-validated from earlier
  milestones, so an unconditional literal match on *"bench-validated"* would fire on every one of
  those legitimate sentences. **The fixture must pin both directions** — a py32 violation that
  fires AND a legitimate AVR sentence that does not.

### Claude's Discretion

- Exact JSON schema/key names for the baseline file, and the parser's regex for pio's `Flash:` /
  `RAM:` report lines (`check_uno_ram.sh` already parses the `RAM:` line — reuse its shape).
- Exact filenames for the four new checkers and their fixtures, subject to D-08's naming convention.
- Whether the required-caveat half of the claims gate (v1.22's checker also asserted a required
  silicon caveat is present in each target) is carried forward — default is **yes**, mirroring
  v1.22's two-part shape, adapted to the v1.23 "no PY32F071 PCB exists" caveat.
- Plan/wave decomposition and commit granularity.

### Deferred Ideas (OUT OF SCOPE)

- **A cross-repo CI leg** that checks out the firmware sibling so the nine gates run automatically
  forever (considered and rejected for this phase under D-05). Blocked on two real problems: GitHub
  Actions cannot check out above the workspace, and during v1.23 the matching firmware commit lives
  on an unpushed milestone branch, so the leg would score against `beta` — the wrong tree. Revisit
  after v1.23 merges to `beta`, when app and firmware `beta` are once again in lockstep.
- **ARM flash/RAM as a checked-in baseline with a RAM ceiling** — already tracked as **FUT-ARMSIZE**
  in REQUIREMENTS.md §Future Requirements. Not addable here: `arm-none-eabi-gcc`, `cmake` and
  `ninja` are absent from this devcontainer, and CI only logs `arm-none-eabi-size` output.
- **Correcting the stale `[env:native_nodevtools]` comment** ("the FULL 16-entry list" — the list
  is 17). Trivial, adjacent, not a requirement; fold in only if a plan already edits that file.
- **`prove-pio-dev-flag-fails-closed.md`** (backlog 999.15) — stays in the backlog.
- **`correct-v128-py32-roadmap-prior-art.md`** — owned by Phase 130 / CLOSE-03. Not pulled forward.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BASE-01 | A committed baseline file records flash **and RAM** for all three AVR targets (Leonardo 26072/2014, Uno 23932/1573, uno328pb 23976) plus the native case **and** suite counts (141 cases / 17 suites), so every later delta is judged against a recorded number rather than a remembered one | §Measured Baseline (all six AVR numbers + both native pairs measured this session); §Parse Targets (verbatim `Flash:`/`RAM:`/summary line formats + recommended regexes); §Baseline JSON Schema |
| BASE-02 | The host suite's "firmware absent" proxy is split — repo presence is keyed on `../firestarter/.git`, and a present repo with a missing scan target is a **hard failure**, never a skip | §The Seven Proxy-Carrying Modules (exact constants, exact leg counts, exact scan paths); §Correction C-15 (module-level import-time evaluation forces subprocess-based tests) |
| BASE-03 | A skip-census assertion fails the suite if any skip reason claims the firmware checkout is absent while `../firestarter/.git` exists | §Skip Census — Measured Today (0 skips across the 7 modules, 0 across the full 1134-test suite with the sibling present); §Pitfall 4 |
| BASE-04 | A CMake source-list drift gate verifies every path named in `platform/py32f071/CMakeLists.txt` resolves in the tree, with an explicit commented `PY32_EXCLUDED` allow-list so a reader can tell deliberate omissions from rename damage | §BASE-04: The Real CMake Manifest (verbatim three-list structure, the three incompatible path idioms, the confirmed `flash_type_3/4` defect, the deliberate-omission set, and the fact `PY32_EXCLUDED` does not yet exist) |
| BASE-05 | An orphan-provisional-macro checker asserts every `RURP_*_PROVISIONAL`-style flag has at least one consumer outside its own definition | §BASE-05: The Orphan Macro (confirmed absent from `beta`, confirmed present with exactly zero consumers on the py32 branch; recommended match pattern) |
| BASE-06 | A warning-count gate holds macro-redefinition warnings at zero, so the next real warning is not buried | §BASE-06: Warning Inventory — **Correction C-4**, the load-bearing finding: 0 on AVR, 360 on each native env; §Compiler Choice (host `g++`, not avr-g++, and why) |
| BASE-07 | `check_permitted_claims.py` with a v1.23 phrase table mechanically forbids the Validation Ceiling's forbidden claims across every closing artifact, and fails closed when its target list is empty | §BASE-07: Copying v1.22's Checker (exact env-seam contract, the two fail-closed guards and their ordering bug, the research-supplied phrase table, D-16 proximity scoping design) |
| BASE-08 | Every checker introduced in this milestone ships with a committed planted-violation fixture and a pytest proving the checker exits non-zero on it | §BASE-08: The Convention Is Not Universal — **Correction C-9** (4 of 7 conform); §D-12 Fixture Mechanism — **Correction C-5** (git refuses `.git` silently at exit 0) |
</phase_requirements>

---

## Corrections to CONTEXT.md and ROADMAP

Prior phases (121, 122) each found real errors inside supposedly-locked decisions. This phase is no
different: nine corrections, five of which change the plan.

| # | Claim | Status | Evidence |
|---|-------|--------|----------|
| **C-1** | D-04: the two native envs "may legitimately differ", and if they do, MERGE-06 is unsatisfiable | **FALSIFIED — good news** | Both envs report **141 test cases: 141 succeeded**, 17 suites. Phase 124 needs no amendment. [VERIFIED: `pio test -e native` / `-e native_nodevtools`, this session] |
| **C-2** | BASE-06: "holds macro-redefinition warnings at zero" | **HALF FALSE — plan-changing** | AVR clean builds: **0** warnings of any kind. `pio test -e native`: **360** macro-redefinition warnings (8 macros × 45 TUs); `native_nodevtools`: **360** identical. Zero is unreachable on native without remediation. [VERIFIED: measured] |
| **C-3** | D-12: "a nested `.git` **directory** cannot be committed" | **TRUE BUT UNDERSTATED — plan-changing** | Git refuses **any** path component named `.git`, file or directory, and does so **silently at exit 0**. `git add x/.git` → rc 0, nothing staged. `git add -f` → rc 0, nothing staged. This is a fail-open of the exact class this phase exists to kill. [VERIFIED: measured] |
| **C-4** | D-06: new firmware-repo checkers "run in firmware CI unconditionally" | **OVERSTATED — plan-changing** | `build.yml` triggers on push/PR to **`main` only**; `beta-build.yml` on push to **`beta` only**. The v1.23 milestone branch fires **neither**. They become CI-live only after merge to `beta`. Reinforces D-05's local-evidence choice. [VERIFIED: workflow `on:` blocks] |
| **C-5** | D-14: the fixture is compiled "by a real compiler inside the pytest" | **NEEDS PINNING — plan-changing** | In both workflows `pytest tests/ -v` runs **before** `pio run`, so the avr-gcc toolchain is not installed at pytest time. The fixture must compile with host `g++`. [VERIFIED: `build.yml:108` vs `:122`; `beta-build.yml:66` vs `:80`] |
| **C-6** | D-08: `check_X.py ⇒ test_check_X.py` matches "the host repo's existing checker↔test pairs"; code_context says "six existing checker↔test naming pairs" | **FALSIFIED — plan-changing** | There are **7** checkers, and only **4** conform. `check_dispatch.py` → `test_check_dispatch_invariants.py` (different name); `check_sdp_capability_invariants.py` → `test_check_sdp_capability.py` (different name); `check_mypy_watermark.py` → **no test at all**. A repo-wide convention meta-test goes RED on arrival. [VERIFIED: filesystem enumeration] |
| **C-7** | canonical_refs: per-module skipif leg counts (19/2/2/1/1/1/1 = 27) | **WRONG NUMBERS, RIGHT MODULE SET** | Measured decorator legs: 8/2/3/1/3/1/6 = **24**. The 7-module set is correct. Collected tests across those 7 modules = **49**. [VERIFIED: grep + pytest collection] |
| **C-8** | ROADMAP/PROJECT: "the **nine** cross-repo source-scanning gates" vs `122-NONREGRESSION.md`'s "eleven-row gate table" | **BOTH CORRECT — reconciled** | 9 distinct gates presented as 11 rows (three gates contribute both a checker row and a pytest row). But `test_gen_validation_header.py` (6 legs) is a proxy-carrying module **absent** from the eleven-row table — so D-11's 7-module inventory is a **superset** of the 9-gate set, not the same set. [VERIFIED: cross-read] |
| **C-9** | code_context: "Both sub-repos are still on `beta`" | **CONFIRMED, and no lag** | Both on `beta`; `git rev-list --left-right --count beta...origin/beta` → `0 0` in **both** repos. No `v1.23` branch exists in either. Meta is on `gsd/v1.23-py32f071-integration`. [VERIFIED: measured] |

Two further notes, non-blocking:

- `/workspaces/CLAUDE.md` states *"Neither sub-repo is committed here."* A `.gitmodules` exists
  registering **both** `firestarter` and `firestarter_app` as submodules, and `git status` shows a
  modified `firestarter_app` gitlink. The meta repo does track gitlinks (consistent with v1.22's
  close, which bumped them). Treat CLAUDE.md as stale on this point. [VERIFIED: `.gitmodules`]
- The knowledge graph at `.planning/graphs/graph.json` is **701 h old and 515 commits behind**
  (`built_at_commit f4150b8` vs `current fc9b994`). Treat any semantic relationship from it as
  approximate; this research relied on direct measurement instead. [VERIFIED: `gsd-tools graphify status`]

---

## Measured Baseline (BASE-01)

All figures below were produced in this session by `pio run -t clean -e <env>` followed by
`pio run -e <env>`, and by `pio test -e <env>`. Nothing is recalled.

### Provenance / meta block

| Field | Measured value |
|-------|----------------|
| Firmware tree SHA | `5c9160a34b665878b05403ab014b959926feb6bf` (branch `beta`, level with `origin/beta`) |
| Host app tree SHA | `e7d3ee8c8a41cd20e9159ab43b5cd969603d773e` (branch `beta`, level with `origin/beta`) |
| PlatformIO Core | `6.1.19` |
| Platform | `atmelavr 5.2.0` |
| Toolchain | `toolchain-atmelavr @ 1.70300.191015` → **avr-gcc / avr-g++ 7.3.0** |
| Framework (uno, leonardo) | `framework-arduino-avr @ 5.3.0` |
| Framework (uno328pb) | `framework-arduino-avr-minicore @ 3.1.2` |
| Host Python | 3.12.13 |
| Host g++ | Debian 14.2.0-19 (`g++ 14.2.0`) |

### AVR flash and RAM — clean build, all three targets

| Env | Flash used | Flash total | Flash free | RAM used | RAM total | RAM free | vs ROADMAP |
|-----|-----------:|------------:|-----------:|---------:|----------:|---------:|------------|
| `uno` | **23932** | 32256 | 8324 | **1573** | 2048 | 475 | matches 23932/1573 exactly |
| `uno328pb` | **23976** | 32384 | 8408 | **1579** | 2048 | 469 | flash matches 23976; **RAM was never recorded anywhere — 1579 is new** |
| `leonardo` | **26072** | 28672 | 2600 | **2014** | 2560 | 546 | matches 26072/2014 exactly |

[VERIFIED: `pio run -t clean -e X && pio run -e X`, all three, this session]

Two cross-checks against the planning record, both consistent:
- Leonardo free flash **2600 B** matches research adjudication A-1 exactly ("2600 B on `beta`"),
  confirming the stale 2992 B figure is indeed superseded. [VERIFIED]
- Leonardo RAM free **546 B** matches PROJECT.md correction 3's "2014/2560, 546 B free". [VERIFIED]

**No discrepancies to record in the meta block.** D-03 anticipated a possible disagreement between
measured and ROADMAP figures; there is none. The meta block should still record the measurement
provenance, and should state affirmatively that the ROADMAP cross-check passed 5/5 with the sixth
number (uno328pb RAM) supplied for the first time.

### Native case and suite counts — the D-04 question, resolved

| Env | Suites | Cases | Result | Duration |
|-----|-------:|------:|--------|---------:|
| `native` | **17** | **141** | 141 succeeded, 0 failed, 0 errored | 17.46 s |
| `native_nodevtools` | **17** | **141** | 141 succeeded, 0 failed, 0 errored | 20.86 s |

**The two environments agree exactly.** [VERIFIED: `pio test -e native`, `pio test -e native_nodevtools`, this session]

Why they agree, so the planner can record the *reason* and not just the number: the divergence D-04
feared would come from a suite compiling a different set of `RUN_TEST` cases under `-D DEV_TOOLS`.
`platformio.ini`'s own comment for `[env:native_nodevtools]` already records the measured basis —
*"no test file references DEV_TOOLS or CMD_DEV_* anywhere"* — so there is no conditional case in any
suite. The 17 `test_filter` entries and 17 `-I` entries are identical between the two envs (read and
counted: 17 each, in both blocks). [VERIFIED: `platformio.ini:102-119` and `:202-219`]

**Consequence for Phase 124:** MERGE-06's wording (*"`pio test -e native` and `-e native_nodevtools`
report the BASE-01 case **and suite** counts"*) is satisfiable as written. **No amendment is needed
and none should be requested.** The plan should still record both pairs separately in the JSON per
D-04's letter, plus an explicit `envs_agree: true` fact, so that a future divergence is detected
rather than assumed away.

**Stale-comment note (deferred idea, confirmed):** `[env:native_nodevtools]` says *"the FULL 16-entry
list"* (line ~193) and *"all 16 suites"* (line ~195) — three stale references, not one, and the real
count is 17. Fold in only if a plan already edits `platformio.ini`.

### Other suite counts, for cross-phase reference

| Suite | Command | Measured |
|-------|---------|---------:|
| Firmware script tests | `cd firestarter && python3 -m pytest tests/ -q` | **8 passed** (0.04 s) |
| Host app suite | `cd firestarter_app && python3 -m pytest tests/ -q` | **1134 passed**, 29 snapshots, **0 skipped**, across 70 files |
| The 7 proxy modules alone | `pytest <7 modules> -rs -q` | **49 passed, 0 skipped** |

[VERIFIED: measured this session, no board attached]

The 1134 figure matches `122-NONREGRESSION.md`'s observed count exactly, confirming the "1150"
baseline quoted in earlier v1.22 artifacts remains the wrong number and 1134 is correct. Note the
memory-recorded environment artifact does **not** apply here: no `/dev/ttyACM*` or `/dev/ttyUSB*`
device is attached, so `test_no_programmer_found_*` are green.

---

## Parse Targets — verbatim formats the comparator must match (BASE-01)

### pio size-report lines

Verbatim, from the clean builds (leading whitespace preserved; the bar-graph column is variable):

```
RAM:   [========  ]  76.8% (used 1573 bytes from 2048 bytes)
Flash: [=======   ]  74.2% (used 23932 bytes from 32256 bytes)
```

```
RAM:   [========  ]  78.7% (used 2014 bytes from 2560 bytes)
Flash: [========= ]  90.9% (used 26072 bytes from 28672 bytes)
```

The format is **identical across all three AVR envs** — only the numbers and the bar fill change.
Both lines are anchored at column 0.

**`check_uno_ram.sh`'s parser still matches.** It does `grep -E '^RAM:'` then
`grep -o 'used [0-9]* bytes'` / `grep -o 'from [0-9]* bytes'`. Both greps hit against today's output
unchanged. [VERIFIED: format compared byte-for-byte against the script's documented sample]

Recommended Python regex for the comparator, covering both lines in one pattern:

```python
SIZE_RE = re.compile(
    r"^(?P<kind>RAM|Flash):\s+\[[^\]]*\]\s+[\d.]+%\s+"
    r"\(used (?P<used>\d+) bytes from (?P<total>\d+) bytes\)",
    re.MULTILINE,
)
```

Fail-closed rule to carry over from `check_uno_ram.sh` (its exit code 2): if either line is absent
from the captured output, that is a **parse failure**, distinct from a size regression, and must not
be reported as a pass. `check_uno_ram.sh` already gets this right and the comparator should keep the
three-way exit taxonomy (0 = within baseline, 1 = regression, 2 = could not parse / tool error) —
the same shape `tools/check_mypy_watermark.py` uses.

### pio test summary line

Verbatim:

```
================ 141 test cases: 141 succeeded in 00:00:17.464 ================
```

Recommended regex:

```python
CASES_RE = re.compile(r"^=+\s+(?P<total>\d+) test cases:\s+(?P<ok>\d+) succeeded", re.MULTILINE)
```

**Suite count is not printed as a number anywhere.** It must be derived by counting rows in the
`SUMMARY` table — lines matching `^\s*(native|native_nodevtools)\s+native/avr/\S+\s+(PASSED|FAILED|ERRORED)`.
Recommended regex:

```python
SUITE_RE = re.compile(r"^\s*\S+\s+(?P<suite>native/avr/\S+)\s+(?P<status>PASSED|FAILED|ERRORED|IGNORED)\s", re.MULTILINE)
```

Counting rows (rather than counting `test_filter` entries in `platformio.ini`) is the load-bearing
choice: A-4's failure mode is *"0 passing / 17 suites ERRORED"*, in which `test_filter` still has 17
entries but every suite errored. The comparator must assert **both** `len(suites) == 17` **and**
`all(status == "PASSED")` **and** `cases == 141`. Asserting only the suite count reproduces the
project's own "assert counts, never 'tests pass'" anti-pattern in mirror image.

---

## BASE-06: Warning Inventory — the load-bearing correction

### Measured warning counts

| Build | Command | Total `warning:` lines | Macro-redefinition | Other |
|-------|---------|-----------------------:|-------------------:|------:|
| `uno` | `pio run -t clean -e uno && pio run -e uno` | **0** | **0** | 0 |
| `uno328pb` | same | **0** | **0** | 0 |
| `leonardo` | same | **0** | **0** | 0 |
| `native` | `pio test -e native` | **360** | **360** | 0 |
| `native_nodevtools` | `pio test -e native_nodevtools` | **360** | **360** | 0 |

[VERIFIED: measured this session, full clean rebuilds]

The 360 on each native env decomposes as **8 distinct macros × 45 translation units**:

| Macro | Occurrences |
|-------|------------:|
| `PSTR` | 45 |
| `memcpy_P` | 45 |
| `pgm_read_byte` | 45 |
| `pgm_read_dword` | 45 |
| `pgm_read_ptr` | 45 |
| `pgm_read_word` | 45 |
| `strcpy_P` | 45 |
| `strlen_P` | 45 |

Cause, read from the emitted diagnostics: each suite's own
`test/native/avr/<suite>/avr/pgmspace.h` host shim defines these macros, and
`.pio/libdeps/native/ArduinoFake/src/arduino/pgmspace.h` then redefines them. Verbatim sample:

```
.pio/libdeps/native/ArduinoFake/src/arduino/pgmspace.h:106:9: warning: "pgm_read_ptr" redefined
  106 | #define pgm_read_ptr(addr) (*(const void * const *)(addr))
      |         ^~~~~~~~~~~~
test/native/avr/test_messages/avr/pgmspace.h:48:9: note: this is the location of the previous definition
   48 | #define pgm_read_ptr(addr) (*(void**)(addr))
      |         ^~~~~~~~~~~~
```

### What this means for BASE-06 — three viable shapes, one recommended

BASE-06 says *"holds macro-redefinition warnings at zero, so the next real warning is not buried"*.
The irony is exact: on the native envs, 360 warnings **are** the burial.

| Option | Description | Assessment |
|--------|-------------|------------|
| **A (recommended)** | Zero-tolerance scoped to the **three AVR envs** (already true, so it holds a real invariant from day one) + a **watermark of 360** for each native env in the same baseline JSON, so any *new* warning of any kind on native fails | Requirement-faithful, zero remediation cost, delivers D-13's stated purpose. Records the 360 as a known, characterised debt rather than hiding it. |
| B | Zero-tolerance across all five envs, with a Phase-123 remediation task deduplicating the pgmspace shims | Large, touches 17 suite directories and `_shared/`, risks golden-trace churn — exactly the "no firmware code moves" boundary this phase declares. **Reject.** |
| C | Watermark-only everywhere, no zero rule | Weaker than the requirement text. **Reject.** |

**Recommendation: Option A.** It is the only shape that satisfies BASE-06's literal text (there *is*
a zero-held macro-redefinition rule), satisfies D-13's stated purpose (a new warning of any kind
fails), and respects the phase boundary (no firmware source moves). The plan must state explicitly,
in prose and in the JSON, that the 360 is a *characterised pre-existing* count on the native envs and
not a regression — otherwise a later phase reading only the number will mistake it for damage.

**Also fold into the plan:** because the AVR counts are genuinely zero, the AVR half of the gate is
strictly stronger than a watermark and should be spelled as `avr_warning_total == 0` for all three,
not `<= 0`.

### Compiler choice for the D-14 fixture — pinned

D-13's discussion-time finding is confirmed exactly, on **both** candidate compilers:

| Compiler | Version | Emits on `#define FOO 1` / `#define FOO 2` | `-Wmacro-redefined` accepted? |
|----------|---------|--------------------------------------------|-------------------------------|
| host `g++` | Debian 14.2.0-19 | `redef.cpp:2:9: warning: "FOO" redefined` | **No** — `unrecognized command-line option '-Wmacro-redefined'; did you mean '-Wbuiltin-macro-redefined'?` |
| `avr-g++` | 7.3.0 (`~/.platformio/packages/toolchain-atmelavr/bin/avr-g++`) | `redef.cpp:2:0: warning: "FOO" redefined` | **No** — `cc1plus: error: -Werror=macro-redefined: no option -Wmacro-redefined` |

[VERIFIED: both compiled this session against a two-line fixture]

**Use host `g++`.** Two independent reasons:

1. **CI ordering (Correction C-5).** In `build.yml` the step order is `pio test -e native` (:91) →
   `pio test -e native_nodevtools` (:102) → `pip install pytest` (:105) → **`pytest tests/ -v` (:108)**
   → version bump (:113) → **`pio run` (:122)**. `beta-build.yml` has the same shape (`pytest tests/ -v`
   at :66, `pio run` after the version bump). The AVR toolchain is installed by `pio run`, i.e.
   **after** the pytest that would invoke it. A fixture pytest shelling out to
   `~/.platformio/packages/toolchain-atmelavr/bin/avr-g++` would pass locally and fail in CI with
   "no such file". This is precisely the local-green/CI-red asymmetry the phase exists to prevent.
2. `g++` is guaranteed present on `ubuntu-latest` and is already the compiler the native envs use, so
   the fixture exercises the same diagnostic the 360 real warnings come from.

**Parser regex — version-independent.** Note the two compilers differ in the location prefix
(`:2:9:` on gcc 14 vs `:2:0:` on gcc 7.3) but share the diagnostic tail exactly. Anchor on the tail,
never on the column:

```python
MACRO_REDEF_RE = re.compile(r'warning:\s*"(?P<macro>[^"]+)"\s+redefined')
```

This matches every one of the 360 real native warnings and both fixture compilations. A regex that
included `:\d+:\d+:` would still work, but would silently narrow if a future toolchain changes column
reporting — an avoidable fragility in a gate whose whole point is not failing open.

**Fail-closed requirement for the fixture pytest:** if `g++` is not on `PATH`, the test must **fail**,
not skip. A skip here recreates the BASE-02 class inside the very phase that kills it. Recommend
resolving the compiler via `shutil.which(os.environ.get("CXX", "g++"))` and asserting it is not None
with an explicit message.

**Known gap to record (D-14, confirmed):** pio wraps compiler output in its own framing (`Compiling
.pio/build/...`, progress bars, the `[SUCCESS]` banner). The fixture proves the *warning line* is
parsed correctly but does not prove the parser survives pio's surrounding framing. Mitigation
available at near-zero cost: also feed the parser a committed **captured excerpt** of real
`pio test -e native` output (a dozen lines around one of the 360 warnings) as a second fixture. This
closes the gap D-14 flags as open, and the raw material for it already exists in this session's
measurements.

---

## BASE-02 / BASE-03 / D-11: The Seven Proxy-Carrying Modules

### The module set is right; the leg counts are not (Correction C-7)

| Module | Decorator legs (measured) | CONTEXT claimed | Proxy constant | Keyed on |
|--------|--------------------------:|----------------:|----------------|----------|
| `tests/test_revision_constants_parity.py` | **8** | 19 | `FW_ABSENT` (:138) | `firestarter/include/firestarter.h` |
| `tests/test_dispatch_mirror.py` | **2** | 2 | `FW_ABSENT` (:52) | `firestarter/doc/PROTOCOLS.md` **AND** a firmware dispatch test path (:37) — compound `and` |
| `tests/test_sdp_bus_config_drift.py` | **3** | 2 | `_FW_HEADER_ABSENT` (:42) | `_COMMITTED_HEADER` (:25) |
| `tests/test_check_no_log_in_sdp_window.py` | **1** | 1 | `_FW_ABSENT` (:72) | `firestarter/src/proms/eeprom_28c.cpp` (:63) |
| `tests/test_sdp_table_parity.py` | **3** + 1 inline `if _FW_ABSENT:` (:299) | 1 | `_FW_ABSENT` (:54) | `firestarter/src/proms/eeprom_28c.cpp` (:48) |
| `tests/test_check_is_memory_cmd_no_ifdef.py` | **1** | 1 | `_FW_ABSENT` (:65) | `firestarter/include/firestarter.h` (:56) |
| `tests/test_gen_validation_header.py` | **6** | 1 | `_FW_HEADER_ABSENT` (:37) | `_COMMITTED_HEADER` (:22) |
| **Total** | **24 decorator legs + 1 inline guard** | 27 | | |

[VERIFIED: `grep -cE '^@(pytest\.mark\.skipif|_requires_fw|_requires_fw_header)'` per file, plus manual read]

Collected tests across those seven modules: **49**, all passing, **0 skipped** with the sibling
present. [VERIFIED: `pytest <7 modules> -rs -q`]

Three details the plan must not miss:

1. **`test_sdp_table_parity.py:299` carries a bare inline `if _FW_ABSENT: return`**, not a decorator.
   A rekey pass that only rewrites `@pytest.mark.skipif` decorators will leave this one behind, and
   it is invisible to the decorator grep. It is also exactly the shape D-09's recurrence lint must
   catch.
2. **`test_dispatch_mirror.py`'s proxy is compound**: `FW_ABSENT = not (_PROTOCOLS_MD.exists() and _FW_DISPATCH_TEST.exists())`.
   Two scan paths behind one flag — so rekeying it to `.git` moves **two** paths into the D-11
   inventory, not one.
3. **`test_gen_validation_header.py` (6 legs) is not in v1.22's eleven-row gate table** (Correction
   C-8). D-11's inventory is a superset of MERGE-07's nine gates. The plan should say which set each
   artifact covers, so Phase 124 does not conflate them.

### The complete cross-repo scan-path inventory (D-11's committed target list)

This is the material for D-11's single committed inventory. Two populations:

**A. Paths resolved from `tests/` (the 7 proxy modules):**

| Path | Resolved by |
|------|-------------|
| `../firestarter/include/firestarter.h` | `test_revision_constants_parity.py`, `test_check_is_memory_cmd_no_ifdef.py` |
| `../firestarter/src/proms/eeprom_28c.cpp` | `test_check_no_log_in_sdp_window.py`, `test_sdp_table_parity.py` |
| `../firestarter/doc/PROTOCOLS.md` | `test_dispatch_mirror.py` |
| firmware dispatch test path (`test_dispatch_mirror.py:37-38`) | `test_dispatch_mirror.py` |
| `_COMMITTED_HEADER` (validation header) | `test_gen_validation_header.py`, `test_sdp_bus_config_drift.py` |
| `firestarter/data/pinouts.json` (host-local, **not** cross-repo — `_REAL_PINOUTS`, `test_sdp_bus_config_drift.py:24`) | `test_sdp_bus_config_drift.py` |

**B. Tools that resolve into `../firestarter` (11 files, the checker side):**

`tools/check_dispatch.py`, `tools/build_db.py`, `tools/gen_validation_header.py`,
`tools/check_no_log_in_sdp_window.py`, `tools/check_no_community_support_status_write.py`,
`tools/check_devtest_orchestrator.py`, `tools/check_is_memory_cmd_no_ifdef.py`,
`tools/check_sdp_capability_invariants.py`, `tools/diff_db.py`, `tools/gen_sdp_bus_config.py`,
`tools/audit_coverage_matrix.py`. [VERIFIED: `grep -ln 'firestarter"' tools/*.py`]

**Planner note:** D-11 says "one committed inventory of every cross-repo scan path". Population B is
larger than population A and is where a rename actually bites hardest (`check_devtest_orchestrator.py`
resolves three firmware-side host files by name). The inventory should cover **both** populations, and
the single resolving test should iterate the union. Restricting it to the 7 test modules would leave
11 tools unguarded.

**Careful — one path in the list is not cross-repo.** `_REAL_PINOUTS` points at
`firestarter_app/firestarter/data/pinouts.json` — same repo, different `firestarter` (the Python
package directory shares the name with the sibling repo). A mechanical "any path containing
`firestarter`" sweep will wrongly pull it in. This name collision is a real trap: `_FA_DIR.parent / "firestarter"`
is the sibling **repo**, while `_APP_DIR / "firestarter"` is the **package**. Both appear in
`test_sdp_bus_config_drift.py`, four lines apart.

### Skip census — measured today (BASE-03, D-10)

| Scope | Skips observed |
|-------|---------------:|
| The 7 proxy modules, sibling present | **0** |
| Full host suite (1134 tests), sibling present, no board attached | **0** |

[VERIFIED: `pytest -rs -q`, this session]

Research's own census (`SUMMARY.md` A-7) recorded **33 skips with no sibling repo (30 firmware-keyed),
3 with the merged sibling**. My run observed 0 with the merged sibling. The delta is explainable and
worth recording: the 3 residual skips A-7 saw are environment-dependent, and A-7 itself names two of
them (`test_gen_validation_header.py::test_validate_spec_called_before_emission`,
`test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing`) as **known path
artifacts, proven identical on a pristine `beta` worktree — "do not chase them"**. Today they pass.

**This is exactly why D-10 rejects a pinned count.** The census number moved from 3 to 0 between two
sessions on the same tree with no code change. An allow-list of *reasons* is stable where a count is
not. The measurement above is strong evidence D-10 chose correctly, and the plan should cite it as
such.

**Starting content for the allow-list**, derived from the reason strings actually present in the
source:

| Reason string (verbatim) | Legitimacy |
|--------------------------|-----------|
| `"firestarter firmware checkout absent"` | Legitimate **only** when `../firestarter/.git` does not exist. Fails the run whenever it does. This is BASE-03's whole assertion. |
| (the `_requires_fw` / `_requires_fw_header` reasons in the other five modules) | Same class — the plan must read each verbatim and either normalise them to one string or list all variants. Do **not** assume they are identical; five modules wrote their own. |

Recommendation: **normalise all seven modules to one shared marker** exported from a single helper
(D-09 already calls for one pass over all seven), so the allow-list has one firmware-absent entry
rather than five near-duplicates. That also makes the recurrence lint's job tractable.

---

## D-12: The Committed Repo-Presence Marker — mechanism, measured

### The trap is real and worse than CONTEXT states (Correction C-3)

Measured in a scratch repo:

| Command | Exit code | Effect |
|---------|----------:|--------|
| `git add -A` with `fake_fw/.git` present as a **file** | 0 | `fake_fw/marker.txt` staged; **`.git` silently omitted** |
| `git add fake_fw/.git` | **0** | **nothing staged, no message** |
| `git add -f fake_fw/.git` | **0** | **nothing staged, no message** |
| `git update-index --add fake_fw/.git` | 0 | prints `Ignoring path fake_fw/.git`, nothing staged |

[VERIFIED: measured this session in an isolated `git init` repo]

Git's path-validation refuses any path component named `.git` regardless of whether it is a file or a
directory, and — critically — **`git add` reports success**. CONTEXT's suggested workaround (*"a
`.git` gitfile containing `gitdir:`"*) **does not work**. An executor following it would run
`git add`, see exit 0, run the test locally against the working tree (which does have the file), see
green, and commit a fixture that is not in the index. CI, or any fresh clone, would then behave
differently. That is the same silent-fail-at-exit-0 pathology as A-7's proxy, reproduced inside this
phase's own fixture.

### Two mechanisms that do work

**Mechanism 1 (recommended) — committed tree + runtime marker materialisation.**

Commit the fake sibling *without* the marker, and have the pytest copy it into `tmp_path` and create
the `.git` there:

```python
src = _HERE / "fixtures" / "fake_firestarter"     # committed, deliberately incomplete
fake = tmp_path / "firestarter"
shutil.copytree(src, fake)
(fake / ".git").write_text("gitdir: /nonexistent\n")   # marker exists only at runtime
```

Verified working end to end this session: the committed tree stages cleanly, `copytree` succeeds, the
materialised `.git` returns `True` from `.exists()`, the present scan target resolves, and the
deliberately-omitted scan target does not. [VERIFIED: measured]

This satisfies BASE-08's *committed planted-violation fixture* requirement — the **violation** (the
deliberately-missing scan target, and the incomplete file set) is committed and reviewable in the
diff. Only the un-committable marker byte is synthesised, and it carries no test semantics beyond
"a repo is here". Document that distinction in the fixture's README so a future reader does not
mistake the runtime step for a `tmp_path`-only fixture of the kind D-12 rejects.

Note the checker only ever calls `.exists()` on the marker — it never shells `git` — so a one-line
gitfile pointing at a nonexistent gitdir is entirely sufficient. No real repo is needed.

**Mechanism 2 — indirect the marker name.** Have the shared helper resolve
`marker = fw_root / os.environ.get("FIRESTARTER_FW_MARKER", ".git")`, so the test can commit
`fixtures/fake_firestarter/GITDIR_MARKER` and point the seam at it. Verified committable. [VERIFIED]

Mechanism 2 is simpler to commit but **weakens the production path**: the marker name becomes
env-overridable in real runs, which is one more knob that can be set wrong. Mechanism 1 keeps the
production key hardcoded to `.git` and confines all indirection to the *root path*. **Prefer
Mechanism 1**, consistent with the operator's recorded preference for the shape that cannot be
silently misconfigured.

### The import-time evaluation trap (Correction C-15)

`FW_ABSENT`, `_FW_ABSENT`, `_FW_HEADER_ABSENT` and every path constant in all seven modules are
**module-level**, evaluated at import time (e.g. `test_revision_constants_parity.py:135-138`).
`pytest.mark.skipif` likewise binds at collection. Consequences the plan must encode:

- An env seam read into a module-level constant is read **once, at import**. `monkeypatch.setenv`
  inside a test function has **no effect** on it.
- Therefore the planted-fixture tests for BASE-02/BASE-03 must invoke pytest (or the checker) as a
  **subprocess** with the env var set in the child's environment — exactly what v1.22's
  `test_check_permitted_claims.py::_run_scanner` does, and exactly why its docstring says *"never an
  in-process import"*.
- The shared helper introduced by D-09 must read its env seam at module scope too, so behaviour is
  consistent between the seven modules and the helper.

This is not hypothetical: it is the single most likely way a plan produces a green test that proves
nothing.

---

## BASE-04: The Real CMake Manifest

Read from `/workspaces/firestarter_py32_ci/platform/py32f071/CMakeLists.txt` (branch
`feature/py32f071-release-assets`, the 53-commit tip). [VERIFIED: file read this session]

### Structure — three source lists, three incompatible path idioms

| List | Entries | Path idiom | Resolvable in the tree? |
|------|--------:|------------|-------------------------|
| `FIRESTARTER_COMMON_SOURCES` (:36-53) | 16 | `"${REPOSITORY_ROOT}/src/..."`, where `REPOSITORY_ROOT` = `${CMAKE_CURRENT_LIST_DIR}/../..` (:32) | **Yes** — this is the list BASE-04 exists for |
| `PY32_PLATFORM_SOURCES` (:55-63) | 7 | **bare relative paths** (`src/main.cpp`, `startup/startup_py32f071.s`), implicitly relative to `platform/py32f071/` | **Yes**, once the correct base is applied |
| `PY32_SDK_SOURCES` (:65-80) | 14 | `"${PY32_SDK_ROOT}/..."`, where `PY32_SDK_ROOT` = `${py32f071_sdk_SOURCE_DIR}` — a **FetchContent download directory** (:13-23, pinned `GIT_TAG 0ed2f4b…`) | **NO — never, by design.** These paths exist only after a network `cmake` configure. |

**This is the biggest correction to a naive BASE-04 design.** A gate that asserts "every path named in
the file resolves in the tree" would fail on all 14 SDK paths, permanently, with no defect present.
The gate must scope by variable:

- **Enforce** `FIRESTARTER_COMMON_SOURCES` (rebase `${REPOSITORY_ROOT}` → firmware repo root).
- **Enforce** `PY32_PLATFORM_SOURCES` (rebase against `platform/py32f071/`).
- **Structurally exempt** `PY32_SDK_SOURCES` — and say *why* in a comment, because "these are not
  checked" is otherwise indistinguishable from an oversight. This exemption is a property of
  FetchContent, not an allow-list entry, and should not be conflated with `PY32_EXCLUDED`.

The same reasoning applies to `target_include_directories` (:89-103), which mixes all three idioms.
Recommend the gate parse **only the three `set(... )` source lists** and not include paths — include
directories that do not exist are a warning-class problem, not the rename-damage class BASE-04 targets.

### The confirmed defect (C-1 / MERGE-02)

Lines 46-47, verbatim:

```cmake
    "${REPOSITORY_ROOT}/src/proms/flash_type_3.cpp"
    "${REPOSITORY_ROOT}/src/proms/flash_type_4.cpp"
```

Against `beta`'s tree these do not exist; the files are `src/proms/flash_nor_unlock.cpp` and
`src/proms/flash_5v_page.cpp` (renamed by v1.19 Phase 104). [VERIFIED: both trees enumerated]
Every other one of the 16 `FIRESTARTER_COMMON_SOURCES` entries resolves against `beta` today. So the
gate, once armed, reports **exactly 2 violations** — a precise, non-vacuous first firing, and a very
good acceptance assertion for Phase 124 to flip to 0.

### `PY32_EXCLUDED` does not exist yet — this phase must define its format

`grep -n PY32_EXCLUDED` on the py32 branch: **absent**. [VERIFIED]

So BASE-04's allow-list is a **new contract this phase authors and Phase 124 populates**. That makes
the format a Phase-123 deliverable, not a Phase-124 discovery. The reverse-direction check it enables:
which firmware sources exist in the tree but are *not* named in the CMake list. Measured against
`beta`, the deliberate omissions are:

| Tree file | Omitted because |
|-----------|-----------------|
| `src/boards/uno_rurp_shield.cpp` | AVR board implementation |
| `src/boards/leonardo_rurp_shield.cpp` | AVR board implementation |
| `src/boards/rurp_common.cpp` | AVR-specific common |
| `src/dev_tools.cpp` | `DEV_TOOLS` off on ARM (this is MERGE-08's "explicit commented decision") |
| `src/rurp_config_utils.cpp` | Phase 126's per-platform config backend split |

Recommended commented format (readable, greppable, and it survives a CMake parse as pure comment):

```cmake
# PY32_EXCLUDED: src/boards/uno_rurp_shield.cpp      -- AVR board impl, no ARM analogue
# PY32_EXCLUDED: src/dev_tools.cpp                   -- DEV_TOOLS deliberately off on ARM (MERGE-08)
```

with the gate matching `^#\s*PY32_EXCLUDED:\s*(?P<path>\S+)\s*--\s*(?P<reason>.+)$` and **requiring
the reason** — an entry without a stated reason should fail, otherwise the allow-list degrades into a
silencer. Note `src/rurp_config_utils.cpp`'s exclusion will need revisiting in Phase 126; the reason
text is the place to say so.

Criterion 3 requires the gate to *exit zero* against a fixture whose omission is allow-listed, so the
fixture set needs **two** CMakeLists fixtures: one with a mismatched path (non-zero) and one with an
omission plus its `PY32_EXCLUDED` line (zero). Plus, per D-07, a third arming case: `platform/py32f071/`
absent ⇒ UNARMED, exit 0.

---

## BASE-05: The Orphan Provisional Macro

**Confirmed absent from `beta`.** `grep -rn PROVISIONAL --include=*.h --include=*.cpp --include=*.c`
over the firmware tree returns nothing. [VERIFIED]

**Confirmed present with exactly zero consumers on the py32 branch.**
`include/boards/py32f071_rurp_shield.h`:

```c
37: #define RURP_PY32F071_PINMAP_CONFIGURED 1
38: #define RURP_PY32F071_PINMAP_PROVISIONAL 1
...
71: #if !RURP_PY32F071_PINMAP_CONFIGURED
72: #error "Configure the PY32F071 Firestarter wiring in include/boards/py32f071_rurp_shield.h"
73: #endif
```

A repo-wide grep for `RURP_PY32F071_PINMAP_PROVISIONAL` across the entire py32 worktree returns
**exactly one hit — its own definition at line 38.** [VERIFIED]

This is a very strong result for the plan:

1. **The checker is not vacuous today** (nothing matches on `beta`, so D-07's UNARMED path fires) —
   and it is **not vacuous after Phase 124 either**: landed unchanged, the branch contains one macro
   with zero consumers, so the checker fires immediately with a real, non-planted violation.
2. **BASE-05 is therefore the mechanism that forces MERGE-04 to actually wire the guard.** Phase 124
   cannot land the port and leave the provisional flag decorative; the gate blocks it. Worth stating
   explicitly in the plan, because it converts BASE-05 from a speculative lint into the enforcement
   arm of a requirement in the next phase.
3. PROJECT.md research finding 5 is confirmed in full: `RURP_PY32F071_PINMAP_CONFIGURED` is `#define`d
   `1` at :37 and tested with `#if !…` at :71 in the **same header**, so the `#error` is structurally
   dead. That half is MERGE-04's problem, not BASE-05's — BASE-05 targets the `PROVISIONAL` flag.

### Recommended match pattern

BASE-05 says *"every `RURP_*_PROVISIONAL`-style flag"*. Recommend:

- **Definition pattern:** `^\s*#\s*define\s+(?P<macro>RURP_[A-Z0-9_]*_PROVISIONAL)\b`
- **Consumer pattern:** any other occurrence of the same identifier anywhere under `include/`, `src/`,
  `platform/`, `test/` — excluding the defining line itself and excluding `#undef`.
- **Scope:** the whole firmware repo, not just `platform/py32f071/`. The `RURP_*` prefix is what
  bounds it; restricting to the platform directory would miss a provisional flag introduced in shared
  code, which is the more dangerous case.

**Arming (D-07):** BASE-05's coarse key is `platform/py32f071/` present. But note an asymmetry the
plan should decide deliberately: unlike BASE-04, BASE-05's pattern is repo-wide and would be
*meaningful* even without the port (a `RURP_AVR_SOMETHING_PROVISIONAL` could appear tomorrow). Two
defensible readings:

- **(a)** Follow D-07 literally: unarmed until `platform/py32f071/` exists. Simple, consistent.
- **(b)** Always armed, but report "0 provisional macros found" as a pass rather than a vacuous-empty
  failure.

D-07 is locked and reading (a) is what it says. Recommend **(a)**, with a comment recording that (b)
was considered — because (b)'s "zero matches is a pass" is precisely the vacuous shape D-08's floor
count exists to forbid, and reconciling the two would need a special case. Consistency with D-07 wins.

---

## BASE-07: Copying v1.22's `check_permitted_claims.py`

Source: `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/check_permitted_claims.py`
(223 lines), `test_check_permitted_claims.py` (204 lines, 7 tests), `fixtures/` (4 files:
`clean_control.md`, `clean_control_second.md`, `planted_forbidden_claim.md`, `planted_missing_caveat.md`).
[VERIFIED: all read this session]

### The env-seam contract, verbatim

```python
FIRESTARTER_CLAIMSCAN_TARGETS = os.environ.get("FIRESTARTER_CLAIMSCAN_TARGETS")   # NO default
```

Read at **module scope**, with `os.environ.get(...)` and deliberately **no default**, so `None`
(absent) and `""` (present-but-empty) stay distinguishable. `resolve_targets(argv)` then applies
three-level precedence, checking `is not None` rather than truthiness:

```python
if argv:                                   return list(argv)                    # positional wins
if FIRESTARTER_CLAIMSCAN_TARGETS is not None:
    return [p for p in FIRESTARTER_CLAIMSCAN_TARGETS.split(os.pathsep) if p]    # "" -> []
return list(_DEFAULT_TARGETS)
```

Carry this verbatim. The `is not None` check is the load-bearing line: a truthiness check would make
`FIRESTARTER_CLAIMSCAN_TARGETS=""` fall back to the real defaults, which is exactly the vacuous pass
criterion 5 forbids.

### The fail-closed / never-vacuous idioms

Two distinct guards, in this order in `main()`:

1. **Fail-closed on a missing target** (:164-170) — `missing = [t for t in targets if not os.path.isfile(t)]`,
   exit 1 naming the missing paths.
2. **Never-vacuous on zero targets** (:172-181) — `if not targets: ... return 1`, with a comment
   noting guard 1 is *"vacuously satisfied by an empty list"*, so this is the real never-vacuous guard.

**A latent ordering wart to fix while copying, not to replicate.** Guard 1 runs first and is vacuously
true for an empty list; guard 2 catches it. The behaviour is correct but the ordering is fragile — if
someone later adds an early `return 0` between them, or changes guard 1 to short-circuit, the empty
case silently passes. **Recommend hoisting the `if not targets` check above the missing-target check**
in the v1.23 copy. The observable behaviour is identical (both exit 1 with a distinguishable message),
and v1.22's own test 5 asserts the *specific* never-vacuous message string, so the assertion still
holds. This is a genuine hardening, not a style change.

Other idioms to carry:
- **Explicit non-pattern default target list** with a comment stating fixtures must be unreachable
  from it (:41-56). Never glob, never tree-walk.
- **The "explicit non-claim" docstring convention** (:24-30) — the module docstring states what a
  green run does *not* prove. v1.23's equivalent must say a green claim-scan is the mechanizable half
  only, and cannot detect implied overclaim, misleading omission, or tone.
- **Subprocess-only tests** (`test_check_permitted_claims.py:38-57`) — never `import` the scanner.
- **The anti-skip PASS line** naming every scanned file, with a paired test (test 6) asserting both
  basenames appear.
- **The precedence pin** (test 7): env seam points at the violation, argv at the clean control, run
  must pass — so a future silent inversion is caught.

### What changes for v1.23

| Element | v1.22 | v1.23 |
|---------|-------|-------|
| Env var name | `FIRESTARTER_CLAIMSCAN_TARGETS` | Recommend keeping the same name (one idiom, different phase dir) — the checkers never coexist in one process |
| `_DEFAULT_TARGETS` | 5 explicit Phase-122 artifacts | Per D-15: the v1.23 closing artifacts, named now, armed all-or-nothing |
| Arming | none (all 5 existed) | **New**, per D-15: zero named targets exist ⇒ UNARMED notice + exit 0; **any one exists ⇒ armed**, then every named target must exist |
| Phrase table | 8 AT28C/silicon patterns | v1.23 table, below |
| Required caveat | `"no AT28C silicon was tested"` | `"no PY32F071 hardware exists"` (research-supplied) |
| Scoping | unconditional literal match | **D-16 proximity scoping** to a `py32`/`PY32F071` token |

### The v1.23 phrase table — already specified by research

`.planning/research/SUMMARY.md` §"Phase 123" (line 260) supplies the table and the caveat directly.
Use it rather than re-deriving from REQUIREMENTS §Validation Ceiling, and cross-check the two agree:

| Label | Pattern (from research) | REQUIREMENTS §Validation Ceiling source |
|-------|-------------------------|------------------------------------------|
| `runs-on-py32` | `runs on (a \|the )?PY32` | *"the firmware runs on a PY32F071"* |
| `works-end-to-end` | `works end[- ]to[- ]end` | *"the install works end to end"* |
| `silicon-verified` | `silicon[- ]verified` | *"silicon-verified" unqualified* |
| `bench-validated` | unqualified `bench[- ]validated` | *"bench-validated"* |
| `hardware-validated` | `hardware[- ]validated` | *"hardware-validated"* |
| `flashed-a-py32` | `flashed (a\|the) PY32` | (derived from *"the install works end to end"*) |
| `closed-loop-vpp` | `closed[- ]loop VPP (works\|verified)` | *"closed-loop VPP works"* |
| `pin-map-correct` | `pin map (is )?(correct\|verified\|validated)` | *"the pin map is correct/verified/validated"* |

The two sources agree on all eight; `flashed-a-py32` is research's addition and is a reasonable
narrowing of the end-to-end claim. Required caveat: **`"no PY32F071 hardware exists"`**.

### D-16 proximity scoping — design

D-16 is the substantive new behaviour. The problem it solves is concrete: v1.23's artifacts will say
things like *"the Leonardo target remains bench-validated from v1.15"*, which is **true** and must not
fire. Recommended implementation:

- Split the text into sentences (or fall back to lines — see below), then for each sentence, fire a
  forbidden pattern only if the same sentence also matches `PY32F071|py32|PY32`.
- **Sentence splitting is the risk.** Markdown tables, bullet lists and code blocks have no reliable
  sentence terminators, and a naive `re.split(r'[.!?]')` mangles version numbers (`v1.23`), file names
  (`check_permitted_claims.py`) and decimals. **Recommend line-scoped, not sentence-scoped**, with the
  fallback that a match on a line lacking a py32 token still fires if the *previous or next* line
  carries one — a 3-line window. This is simple, deterministic, has no tokenizer to get wrong, and
  matches how these artifacts are actually written (tables and bullets, one claim per line).
- If the planner prefers sentence scope, it must be paired with a fixture proving a markdown table row
  is handled, or it will silently under-fire.

**Both-directions fixture (D-16, mandatory).** The fixture set needs at minimum:

| Fixture | Expectation |
|---------|-------------|
| `planted_py32_overclaim.md` | contains e.g. *"the PY32F071 target is bench-validated"* on one line ⇒ **exit non-zero**, naming `bench-validated` |
| `clean_avr_bench_control.md` | contains e.g. *"Leonardo remains bench-validated from v1.15"* with **no** py32 token nearby ⇒ **exit 0** |
| `planted_missing_caveat.md` | lacks *"no PY32F071 hardware exists"* ⇒ exit non-zero |
| `clean_control.md` / `clean_control_second.md` | clean, carry the caveat ⇒ exit 0, both named in the PASS line |

The second row is the one that does not exist in v1.22 and is the whole point of D-16. Without it the
proximity scoping is asserted, not proven.

**Inherited interaction, carry the comment forward.** v1.22's docstring records that an honest negated
phrasing (*"nothing is silicon-verified here"*) **will** trip the `silicon-verified` pattern, and that
the correct response is to reword the artifact, not narrow the pattern. Under D-16 this gets sharper:
*"nothing about the PY32F071 is silicon-verified"* contains both a py32 token and a forbidden phrase,
so it fires. Keep the comment, updated — the canonical caveat sentence exists precisely so authors
have an approved way to say this.

---

## BASE-08: The Convention Is Not Universal (Correction C-6)

D-08 grounds its meta-test in *"the host repo's existing checker↔test pairs"* and code_context says
there are *"six existing checker↔test naming pairs"*. Measured:

| Checker | Expected test by convention | Actual |
|---------|------------------------------|--------|
| `tools/check_devtest_orchestrator.py` | `tests/test_check_devtest_orchestrator.py` | **conforms** |
| `tools/check_is_memory_cmd_no_ifdef.py` | `tests/test_check_is_memory_cmd_no_ifdef.py` | **conforms** |
| `tools/check_no_community_support_status_write.py` | `tests/test_check_no_community_support_status_write.py` | **conforms** |
| `tools/check_no_log_in_sdp_window.py` | `tests/test_check_no_log_in_sdp_window.py` | **conforms** |
| `tools/check_dispatch.py` | `tests/test_check_dispatch.py` | **VIOLATES** — the test is `tests/test_check_dispatch_invariants.py` |
| `tools/check_sdp_capability_invariants.py` | `tests/test_check_sdp_capability_invariants.py` | **VIOLATES** — the test is `tests/test_check_sdp_capability.py` |
| `tools/check_mypy_watermark.py` | `tests/test_check_mypy_watermark.py` | **VIOLATES — no test exists at all** (0 references anywhere in `tests/`) |

[VERIFIED: filesystem enumeration + `grep -rln` per checker]

**7 checkers, 4 conforming, 3 violating.** A repo-wide convention meta-test fails on arrival with 3
pre-existing violations. Three options:

| Option | Assessment |
|--------|-----------|
| **A (recommended)** | Scope the meta-test to **checkers introduced in v1.23**. This is what BASE-08 literally says: *"Every checker introduced in **this milestone**"*. Requirement-faithful and immediately green. |
| B | Repo-wide with a committed grandfather allow-list of the 3 | Honest, and documents the debt, but the allow-list is a silencer with no expiry and `check_mypy_watermark.py`'s missing test is a genuine gap that would then be blessed. |
| C | Repo-wide plus remediating all 3 now | Out of phase scope (`check_mypy_watermark.py` needs a real test written), and unrelated to v1.23. |

**Recommend A**, with a one-line note in the meta-test's docstring recording that 3 pre-existing
checkers do not conform and are deliberately out of scope, naming them. That keeps the finding from
being lost without expanding the phase.

**Scoping mechanism.** "Introduced in v1.23" needs a mechanical definition, or the meta-test is
subjective. Two workable forms:
- **(i)** The v1.23 checkers all live in `firestarter/scripts/` + `firestarter/tests/` (D-06), a
  directory pair that today contains **one** shell script and **no** Python checkers. So
  "every `firestarter/scripts/check_*.py` has `firestarter/tests/test_check_*.py` and
  `firestarter/tests/fixtures/planted_*`" is *exactly* the v1.23 set, with no allow-list needed.
  The host-repo checkers are structurally out of reach because they live in `firestarter_app/tools/`.
- **(ii)** An explicit committed list, which D-08 rejects ("no registry file").

**Recommend (i).** It makes D-06's home choice do double duty: scan-target-follows-home also gives
BASE-08 a clean, registry-free scope boundary. This is a genuinely elegant consequence of D-06 that
the plan should state, because it removes the only real friction in D-08.

**Floor count (D-08).** The meta-test needs a hardcoded floor so a zero-match glob fails. Note the
number of checkers landing in `firestarter/scripts/` this phase depends on the plan's own
decomposition — the baseline comparator plus BASE-04, BASE-05 and BASE-06 gives **4** if the
comparator counts as a checker, 3 if not. BASE-07 lives in the meta repo and is **not** in this glob.
BASE-02/03's recurrence lint lives in `firestarter_app/` and is likewise **not** in it. The plan must
pick the floor after fixing filenames, and the meta-test's assertion should be `>= FLOOR` with the
floor equal to the number actually shipped, so an accidental deletion fails.

**A second glob the meta-test must also floor:** `firestarter/tests/fixtures/planted_*`. Today that
directory does not exist. `firestarter/tests/` currently contains only `__init__.py`, `golden/`, and
`test_update_version.py`. [VERIFIED]

---

## Where the Firmware-Repo Checkers Plug In (D-06)

### Confirmed CI wiring, with one important qualification

| Workflow | pytest step | Trigger |
|----------|-------------|---------|
| `firestarter/.github/workflows/build.yml` | line **108**: `pytest tests/ -v` | `push` + `pull_request` to **`main` only** |
| `firestarter/.github/workflows/beta-build.yml` | line **66**: `pytest tests/ -v` | `push` to **`beta` only**, plus `workflow_dispatch` |

[VERIFIED: both files read this session]

CONTEXT's claim that the step exists at those exact lines is **correct**. But the qualification in
Correction C-4 matters: **neither workflow fires on the v1.23 milestone branch.** The new checkers
become CI-live only when the branch merges to `beta` (Phase 130). During the milestone they are
local-run-only — which is precisely why D-05's recorded-local-evidence choice is right, and the plan
should say so rather than implying continuous CI coverage from Phase 123 onward.

There are only two workflows in the firmware repo. `py32f071.yml` does **not** exist on `beta` — it
arrives with the port in Phase 124 (MERGE-03). [VERIFIED: `ls .github/workflows/`]

### What `firestarter/tests/` contains and what a new test may assume

```
firestarter/tests/
├── __init__.py                # tests/ IS a package
├── golden/                    # golden artifacts
└── test_update_version.py     # 8 tests, all passing
```

`firestarter/scripts/` contains exactly one file: `check_uno_ram.sh`. [VERIFIED]

**Hard constraints for any new test here:**

1. **No `conftest.py`, no `pytest.ini`, no `pyproject.toml`, no `setup.cfg` anywhere in the firmware
   repo.** [VERIFIED: `find -maxdepth 2`] And this is a *deliberate house rule*, not an omission —
   `test_update_version.py:28` carries the comment *"Self-contained sys.path injection — NOT in
   conftest.py per 15-PATTERNS.md Critical Note 4."* A new checker test must do its own path
   resolution, not add a conftest. Deviating would contradict a recorded pattern decision.
2. **Stdlib + pytest only.** CI does `pip install pytest` (build.yml:105, beta-build.yml:~63) — no
   `-r requirements`, no extras. No `pytest-mock`, no `pyyaml`, no `syrupy`. Use `subprocess`,
   `pathlib`, `shutil`, `json`, `re`, `tempfile`, and pytest's built-in `tmp_path`.
3. **No lint gate at all** in the firmware repo — no ruff, no mypy, no format check. (Contrast the
   host repo, which runs `ruff check`, `ruff format --check` and a mypy watermark on
   `firestarter/ tests/`.) So firmware-side checker style is unconstrained by CI; match the existing
   file's style by hand.
4. **`firestarter/tests/` is genuinely PIO-invisible — confirmed.** PlatformIO's unit-test discovery
   globs `test_dir`, which defaults to `test/` (the repo's real native suites live at
   `test/native/avr/…`, all 17 of them listed in `test_filter`). `platformio.ini` sets no `test_dir`
   override, and `build_src_filter` in both native envs is explicitly
   `+<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>` — no path
   under `tests/`. A `.cpp` fixture under `firestarter/tests/fixtures/` therefore cannot reach any
   build. D-14's premise holds. [VERIFIED: `platformio.ini` read in full; `test/` contains only
   `README` and `native/`]

### Both baseline-comparator invocation shapes have a cost

The comparator must run `pio` builds (D-02). Two placements:

| Placement | Behaviour |
|-----------|-----------|
| As a pytest under `firestarter/tests/` (runs at build.yml:108) | Runs **before** `pio run` (:122), so it triggers the AVR toolchain download itself. On a cold `~/.platformio/.cache` that is a multi-minute step. The cache key is `${{ runner.os }}-pio` over `~/.cache/pip` and `~/.platformio/.cache` (build.yml:37-42), so warm runs are cheap. |
| As a separate CI step after `pio run` | Reuses the build that already happened; near-zero added time. But it is a workflow edit, and CONTEXT does not scope one. |

**Recommendation:** ship the comparator as a **standalone script** (`firestarter/scripts/check_size_baseline.py`)
that can either run the builds itself or parse a supplied log, plus a pytest that exercises its
**parser and comparison logic against committed captured-output fixtures** — not one that shells out
to `pio`. That keeps `pytest tests/ -v` fast and deterministic, gives BASE-08 its planted-violation
fixture naturally (a captured log with an inflated Flash number), and leaves the real build
invocation to a human or a later workflow edit. It also side-steps the cold-toolchain cost entirely.
This is a discretionary call (CONTEXT leaves plan decomposition open) but it is the shape that makes
the gate fast, hermetic and fixture-testable at once.

---

## Branch Creation Required Before Any File Is Written (Question 10)

Measured state, this session:

| Repo | Current branch | vs `origin/<branch>` | v1.23 branch exists? |
|------|----------------|----------------------|----------------------|
| `/workspaces` (meta) | `gsd/v1.23-py32f071-integration` | — | **yes**, already checked out |
| `/workspaces/firestarter` | `beta` @ `5c9160a` | `0 0` — **exactly level**, no lag | **no** |
| `/workspaces/firestarter_app` | `beta` @ `e7d3ee8` | `0 0` — **exactly level**, no lag | **no** |

[VERIFIED: `git fetch origin` then `git rev-list --left-right --count beta...origin/beta` in both]

**Required before any executor writes into a submodule:**

1. `git -C firestarter checkout -b <v1.23 milestone branch> beta` — needed for BASE-01 (baseline JSON +
   comparator), BASE-04, BASE-05, BASE-06 and their fixtures/tests.
2. `git -C firestarter_app checkout -b <v1.23 milestone branch> beta` — needed for BASE-02, BASE-03,
   the D-09 rekey of all 7 modules, the recurrence lint, the D-11 inventory, and the D-12 fixture.

Both fork off `beta`, per the ROADMAP's standing policy, and **no `ff-only` catch-up is needed** —
`beta` is already level with `origin/beta` in both repos. (Recorded memory warns that local `beta`
often lags `origin/beta`; today it does not. Re-verify at execute time rather than trusting this
reading.)

BASE-07 writes only into `.planning/phases/123-…/` in the meta repo, which is already on the correct
branch.

**Do not write into the two py32 worktrees.** `/workspaces/firestarter_py32_ci` (branch
`feature/py32f071-release-assets`) and `/workspaces/firestarter_app_py32` (branch
`feature/py32f071-fw-install`) are gitignored working checkouts, never gitlinked. They are the
**read source** for BASE-04's CMake syntax and BASE-05's macro — read-only in this phase.

**Two hazards recorded in project memory that apply directly here:**

- `gsd-tools query commit` can silently switch milestone branches when `current_milestone` is stale
  and `branching_strategy` is `milestone` (`.planning/config.json` confirms
  `"branching_strategy": "milestone"`). Check `HEAD` in all three repos after every gsd commit.
- `--auto`/`--chain` auto-approves `checkpoint:human-verify`. Nothing in this phase is
  outward-facing (no push, no PyPI, no public comment), so the ordinary risk is low — but the
  branch-creation step is a good candidate for an explicit non-auto gate, since creating it in the
  wrong repo or off the wrong base silently poisons every later commit.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Flash/RAM measurement + baseline record (BASE-01) | Firmware repo build tooling (`firestarter/scripts/`) | Firmware repo test (`firestarter/tests/`) | The comparator must parse `pio` output; it belongs where the build is (D-02) |
| Native case/suite count record (BASE-01) | Firmware repo build tooling | — | Same output stream, same parser |
| Cross-repo scan-target resolution (BASE-02/03, D-11) | Host repo test infrastructure (`firestarter_app/tests/`) | Host repo `tools/` (11 scanners resolve into `../firestarter`) | The proxy lives in the host suite; the sibling repo is the resource being probed |
| CMake manifest drift (BASE-04) | Firmware repo scripts | — | Scan target `platform/py32f071/CMakeLists.txt` is firmware-side (D-06) |
| Orphan macro detection (BASE-05) | Firmware repo scripts | — | Scan target is firmware C/C++ source (D-06) |
| Build-warning parsing (BASE-06) | Firmware repo scripts | Firmware repo test (fixture compile via host `g++`) | Warnings come from the firmware build (D-06); the fixture compile is a host-toolchain concern |
| Claim/phrase scanning (BASE-07) | Meta repo phase directory | — | Scan targets are meta-repo closing artifacts (D-06, D-15) |
| Checker↔test↔fixture convention (BASE-08) | Firmware repo test | — | D-06's home choice makes `firestarter/scripts/` the exact v1.23 checker set |
| Milestone branch creation | Git / VCS tier, both sub-repos | — | Structural precondition, not a code concern |

**Cross-tier hazard to note:** BASE-02/03 live in the host repo but their *subject* is the firmware
repo. That is the only genuinely cross-tier capability in the phase, and it is the one that already
failed open. Every other new checker is deliberately single-tier (D-06), so none inherits the skip
class.

---

## Standard Stack

### Core

| Tool | Version | Purpose | Why standard |
|------|---------|---------|--------------|
| `pytest` | (whatever CI's bare `pip install pytest` resolves) | Test runner for all planted-fixture proofs | Already the runner in both repos' CI [VERIFIED: `build.yml:105`, `beta-build.yml`] |
| Python stdlib `subprocess` | 3.12 local / CI's python | Invoke checkers as real processes, never in-process import | v1.22's `_run_scanner` idiom; the only way to prove an *exit code* [VERIFIED: `test_check_permitted_claims.py:38-57`] |
| Python stdlib `re` | — | All parsing (pio size lines, test summary, warnings, CMake `set()` lists, macro definitions) | No parser dependency is installable in firmware CI |
| Python stdlib `json` | — | Baseline file format | Matches `tools/baseline/*.json`'s `meta`-block convention [VERIFIED] |
| `pio` (PlatformIO Core) | 6.1.19 | Produces the output the comparator parses | Already the build system |
| host `g++` | 14.2.0 | Compiles the BASE-06 macro-redefinition fixture | Guaranteed present; avr-g++ is **not** installed at pytest time in CI (Correction C-5) |

### Supporting

| Tool | Purpose | When to use |
|------|---------|-------------|
| `shutil.copytree` + `tmp_path` | Materialise the D-12 fake sibling with a runtime `.git` marker | The only mechanism that works — see §D-12 |
| `shutil.which` | Fail-closed compiler resolution for BASE-06's fixture | Must **fail**, never skip, if absent |
| `git rev-parse HEAD` | Baseline provenance | Recorded in the JSON `meta` block per D-03 |

### Deliberately NOT used

| Instead of | Do not use | Why |
|------------|-----------|-----|
| stdlib `re` for CMake | a CMake parser library | Not installable in firmware CI (`pip install pytest` only) |
| `monkeypatch.setenv` | — for env seams | Module-level constants bind at import; monkeypatch has no effect (Correction C-15) |
| `avr-g++` | — for the BASE-06 fixture | Not installed when `pytest tests/ -v` runs in CI |
| `conftest.py` | — in `firestarter/tests/` | Explicit recorded house rule (`test_update_version.py:28`) |
| blanket `-Werror` | — for BASE-06 | Would make framework-header warnings fatal (D-13, confirmed) |
| `-Werror=macro-redefined` | — | Does not exist on gcc; Clang-only spelling (D-13, confirmed on both compilers) |

**Installation:** none. Every dependency is already present in both repos' CI and in this
devcontainer. No package is added by this phase, so the Package Legitimacy Audit is not applicable —
see §Package Legitimacy Audit.

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.**

Every tool the phase uses is either already a CI dependency (`pytest`, `platformio`) or Python
stdlib (`re`, `json`, `subprocess`, `pathlib`, `shutil`, `tempfile`, `os`, `sys`). No `pip install`,
`npm install` or equivalent is introduced by any BASE requirement, and the firmware repo's CI
deliberately installs only bare `pytest`.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

If a plan proposes adding any dependency (for example a CMake or TOML parser), that proposal must run
the legitimacy gate before the plan is accepted, and should be treated as a scope expansion — the
firmware CI's `pip install pytest` step would also need editing, which no BASE requirement authorises.

---

## Architecture Patterns

### System diagram — what this phase builds and what consumes it

```
                     ┌──────────────────────── PHASE 123 (this phase) ────────────────────────┐
                     │                                                                        │
  pio run -e {uno,   │   ┌─────────────────┐      captured stdout      ┌──────────────────┐   │
  uno328pb,leonardo} ├──►│  size/warning   ├──────────────────────────►│  BASE-01 JSON    │   │
  pio test -e        │   │  output parser  │                           │  (firmware repo) │   │
    {native,         ├──►│  (regex, stdlib)│      counts + watermark   │  meta + numbers  │   │
     native_nodev}   │   └────────┬────────┘                           └────────┬─────────┘   │
                     │            │                                             │             │
                     │            │ same parser                                 │ read by     │
                     │            ▼                                             │ comparator  │
                     │   ┌─────────────────┐                           ┌────────▼─────────┐   │
                     │   │ BASE-06 warning │◄──── committed captured   │ comparator script│   │
                     │   │ gate            │      log fixture +        │ exit 0 / 1 / 2   │   │
                     │   └─────────────────┘      g++ fixture compile  └──────────────────┘   │
                     │                                                                        │
  platform/py32f071/ │   ┌─────────────────┐                                                  │
    (ABSENT today)   ├──►│ D-07 coarse-key ├──► ARMED ──► BASE-04 CMake drift ──┐              │
                     │   │ arming probe    │                                    │              │
                     │   │ dir present?    ├──► ARMED ──► BASE-05 orphan macro ─┤              │
                     │   └─────────────────┘                                    │              │
                     │            └────────────► UNARMED notice, exit 0 ────────┘              │
                     │                                                                        │
  ../firestarter/    │   ┌─────────────────┐                                                  │
    .git             ├──►│ shared presence ├──► present ──► scan target missing = HARD FAIL   │
    (repo marker)    │   │ helper (D-09)   │                (BASE-02)                         │
                     │   │ ONE call site   ├──► absent  ──► honest skip                       │
                     │   │ x 7 modules     │                                                  │
                     │   └────────┬────────┘                                                  │
                     │            │                                                           │
                     │            ├──► D-11 central scan-path inventory ──► resolve-all test  │
                     │            └──► BASE-03 skip census (reason allow-list)                │
                     │                                                                        │
  v1.23 closing      │   ┌─────────────────┐                                                  │
  artifacts          ├──►│ BASE-07 claims  ├──► D-16 proximity scope ──► exit 0 / 1           │
  (ABSENT today)     │   │ gate (meta repo)│    (py32 token in window?)                       │
                     │   └─────────────────┘                                                  │
                     │                                                                        │
                     │   ┌──────────────────────────────────────────────────────────────┐     │
                     │   │ BASE-08 meta-test: for each firestarter/scripts/check_*.py    │     │
                     │   │   assert tests/test_check_*.py AND tests/fixtures/planted_*   │     │
                     │   │   assert count >= FLOOR  (never-vacuous)                      │     │
                     │   └──────────────────────────────────────────────────────────────┘     │
                     └────────────────────────────────┬───────────────────────────────────────┘
                                                      │ consumed by (never recomputed)
                                                      ▼
                          PHASE 124: MERGE-05 (flash/RAM deltas vs BASE-01)
                                     MERGE-06 (141/17 vs BASE-01)
                                     MERGE-07 (nine gates RUN, not skip)
                                     MERGE-02/04 (armed-on-arrival checkers fire)
```

Read the arrows as data flow. The load-bearing property is the bottom edge: everything Phase 124
verifies against is *read from a file this phase commits*, never recomputed or remembered.

### Component responsibilities

| Component | Home | Responsibility |
|-----------|------|----------------|
| Size/count/warning parser | `firestarter/scripts/` | Turn `pio` stdout into structured numbers; exit 2 on unparseable input |
| Baseline JSON | `firestarter/` (path at planner discretion) | The single recorded truth for flash, RAM, cases, suites, warning watermarks |
| Comparator | `firestarter/scripts/` | Read JSON, compare to fresh (or supplied) measurement, exit non-zero on violation |
| Shared FW-presence helper | `firestarter_app/tests/` (one module) | The single `../firestarter/.git` probe; the seven modules import it |
| Scan-path inventory | `firestarter_app/tests/` | One committed list; one test resolving all of it |
| Recurrence lint | `firestarter_app/tools/` or `tests/` | Forbid the bare `not <file>.exists()` absence idiom |
| Four checkers | `firestarter/scripts/` (3) + meta phase dir (1) | Per D-06 |
| Fixtures | `firestarter/tests/fixtures/`, `firestarter_app/tests/fixtures/`, meta `fixtures/` | Committed planted violations, per BASE-08 |

### Pattern 1: Checker + paired pytest + committed fixture + env seam

**What:** Every gate is a standalone `check_*.py` with an env override so its test can aim it at
deliberately-violating fixtures, where fixtures live somewhere the default target list can never
reach.

**When to use:** every new checker in this phase, without exception. Deviating is the anti-pattern.

**Example** (verbatim shape from v1.22, `check_permitted_claims.py:60-68` + `:136-149`):

```python
# Source: .planning/phases/122-.../check_permitted_claims.py
# NO default -- "absent" and "present-but-empty" must stay distinguishable.
FIRESTARTER_CLAIMSCAN_TARGETS = os.environ.get("FIRESTARTER_CLAIMSCAN_TARGETS")

def resolve_targets(argv):
    if argv:
        return list(argv)
    if FIRESTARTER_CLAIMSCAN_TARGETS is not None:   # `is not None`, NOT truthiness
        return [p for p in FIRESTARTER_CLAIMSCAN_TARGETS.split(os.pathsep) if p]
    return list(_DEFAULT_TARGETS)
```

### Pattern 2: Subprocess-invoked planted-fixture test

**What:** the test runs the checker as a real process and asserts on the exit code, never imports it.

**When to use:** every BASE-08 proof. Mandatory here for a second reason beyond v1.22's — module-level
constants make in-process env manipulation ineffective (Correction C-15).

```python
# Source: .planning/phases/122-.../test_check_permitted_claims.py:38-57
def _run_scanner(targets=None, argv=None):
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS"] = targets   # "" is reachable
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS", None)   # genuinely absent
    return subprocess.run([sys.executable, str(_SCANNER), *(argv or [])],
                          cwd=str(_HERE), capture_output=True, text=True, env=env)
```

### Pattern 3: Coarse-key arming (D-07, D-15)

**What:** decide *whether a gate applies* from something structural and un-renameable; then treat a
missing fine-grained target as a **failure**, never a skip.

**When to use:** BASE-02 (`../firestarter/.git`), BASE-04/05 (`platform/py32f071/` directory),
BASE-07 (all-or-nothing over the named closing artifacts).

```python
# Recommended shape, generalising BASE-02's idiom one level down.
ARMED = (FW_ROOT / "platform" / "py32f071").is_dir()
if not ARMED:
    print("UNARMED: platform/py32f071/ absent -- this gate arms when Phase 124 lands the port.")
    return 0
missing = [p for p in fine_grained_targets if not p.exists()]
if missing:
    print(f"FAIL: armed but {len(missing)} target(s) unresolvable: {missing}")
    return 1          # a rename inside the port CANNOT disarm this gate
```

### Pattern 4: Three-way exit taxonomy

**What:** `0` = pass, `1` = real violation, `2` = tool/config/parse error. A broken tool must never be
mistaken for a clean tree.

**Precedent:** `check_uno_ram.sh` (exit 2 = "could not parse the RAM line") and
`tools/check_mypy_watermark.py` (exit 2 = watermark comment missing OR mypy unparseable, with an
explicit comment naming the gate-bypass guard it prevents). [VERIFIED: both read]

Carry it into every new checker. It is the difference between "the build got smaller" and "pio
changed its output format and we stopped measuring".

### Anti-patterns to avoid

- **`not <file>.exists()` as a proxy for repo presence.** The defect this phase exists to kill. D-09's
  recurrence lint must forbid its reappearance.
- **Asserting "tests pass" instead of counts.** A suite that stops being collected also reports green.
  Assert `141` and `17` and `all PASSED`, all three.
- **Path-scoped `git diff` as an untouched-proof.** Passes vacuously on a wrong path (the v1.22
  `src/flash_utils.h` trap). Use `git status --porcelain` empty, or literal blob SHAs.
- **Glob or tree-walk for a checker's default target list.** v1.22's comment spells out why: the
  `fixtures/` directory would poison every default-mode run.
- **`monkeypatch.setenv` against a module-level constant.** Silently ineffective.
- **`git add`-ing a path containing `.git` and trusting exit 0.** Measured: exit 0, nothing staged.
- **Skipping when a tool is absent.** Every "tool missing" branch in this phase must fail, not skip —
  a skip here re-creates the exact class BASE-02/03 remove.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| Parsing pio's `RAM:`/`Flash:` lines | A new bespoke parser | The `check_uno_ram.sh` regex shape (`used (\d+) bytes from (\d+) bytes`), lifted into Python | Already proven against this exact output; its format is unchanged [VERIFIED] |
| Fail-closed / never-vacuous claim scanner | A fresh checker | Copy `.planning/phases/122-.../check_permitted_claims.py` and change only the phrase table, target list and scoping | The env-seam contract, the two guards, the anti-skip PASS line and the precedence pin are all subtle and all already correct |
| Planted-fixture pytest shape | A fresh test module | Copy `test_check_permitted_claims.py`'s 7-test structure | It already covers clean-pass, planted-violation, fail-closed, never-vacuous, anti-skip and precedence |
| A watermark gate | A new mechanism | `tools/check_mypy_watermark.py`'s shape (watermark stored as a comment, three-way exit, explicit gate-bypass guard) | Already the house idiom for exactly this problem |
| Baseline file layout | A new schema | `tools/baseline/*.json`'s `{"meta": {...}, "<data>": [...]}` convention | D-01 names it; two existing files establish it [VERIFIED] |
| Committing a `.git` marker | Any `git add` variant | Commit the tree without it; materialise `.git` in `tmp_path` at test time | Git refuses silently at exit 0 — measured |
| A CMake parser | A dependency or a full parser | Targeted `re` over the three `set(NAME ...)` blocks | Firmware CI installs only bare pytest |
| Sentence segmentation for D-16 | A tokenizer | A 3-line proximity window | Markdown tables and bullets have no reliable sentence terminators |

**Key insight:** every mechanism this phase needs already exists somewhere in this project, and in
every case the existing version encodes a lesson learned the hard way (v1.12's hollow GATE-03, v1.17's
`--ours` trap, v1.22's `src/flash_utils.h` vacuous diff, four fail-closed incidents in Phases 117/118).
A hand-rolled replacement will be missing exactly the guard that was added after the incident. Copy
first; adapt only the parts the requirement forces.

---

## Common Pitfalls

### Pitfall 1: Committing the `.git` marker and believing `git add`'s exit 0

**What goes wrong:** the executor stages `fixtures/fake_firestarter/.git`, sees exit 0, runs the test
locally against the working tree (which has the file), sees green, and commits. The index has no
marker. A fresh clone or CI behaves differently.
**Why it happens:** git's path validation refuses any component named `.git` and `git add` reports
success anyway. Even `git add -f` reports success and stages nothing. [VERIFIED: measured]
**How to avoid:** commit the tree without the marker; materialise it in `tmp_path`. Then add a
verification step: after committing, run `git ls-files <fixture dir>` and assert the expected file
list — do not trust `git add`'s exit code.
**Warning signs:** `git status` shows the fixture dir as fully staged but `git ls-files` omits a file;
the test passes locally and fails on a fresh clone.

### Pitfall 2: Writing the BASE-06 gate to demand zero on the native envs

**What goes wrong:** the gate is authored to BASE-06's literal text, is run against `pio test -e native`,
and reports 360 violations on a tree with no defect. Either the phase stalls on a remediation nobody
scoped, or the gate gets weakened reflexively until it means nothing.
**Why it happens:** the requirement text does not name a scope, and the AVR builds — the natural place
to look — are genuinely at zero, so a spot check confirms the premise before the native envs are tried.
**How to avoid:** scope zero-tolerance to the three AVR envs and watermark the two native envs at 360.
Record in the JSON that 360 is characterised pre-existing debt from duplicate `pgmspace.h` shims, not
damage.
**Warning signs:** a plan task that says "assert zero macro-redefinition warnings" without naming which
envs.

### Pitfall 3: Invoking avr-g++ from a pytest

**What goes wrong:** green locally (the toolchain is installed here), red in CI with "no such file",
because `pytest tests/ -v` runs before `pio run` installs it.
**Why it happens:** the local devcontainer has already run `pio run`, so `~/.platformio/packages/toolchain-atmelavr/`
exists and nothing signals that CI's ordering differs.
**How to avoid:** use host `g++`; anchor the parser regex on the `warning: "NAME" redefined` tail so it
is version-independent across gcc 7.3 and gcc 14.
**Warning signs:** any plan task referencing a path under `~/.platformio/packages/`.

### Pitfall 4: A skip-census assertion that is itself skippable

**What goes wrong:** the census test carries a `skipif` (or lives in a module that does), so under the
exact conditions it exists to detect, it does not run.
**Why it happens:** the census naturally lives beside the modules it audits, and those all carry the
proxy.
**How to avoid:** the census test must carry **no** skip marker of any kind. It should also assert its
own liveness — e.g. that it observed at least one test outcome — so a collection change cannot silence
it. `test_sdp_bus_config_drift.py:121-124` already documents this discipline for a sibling case
("unconditionally (no FW_ABSENT skip) since it never touches the committed header").
**Warning signs:** the census module importing the shared presence helper for anything other than
reading `../firestarter/.git`'s existence.

### Pitfall 5: Missing the non-decorator skip guard

**What goes wrong:** the D-09 rekey pass rewrites all `@pytest.mark.skipif` decorators, the grep comes
back clean, and `test_sdp_table_parity.py:299`'s inline `if _FW_ABSENT: return` still keys on the old
file proxy.
**Why it happens:** every audit of this suite has counted decorators.
**How to avoid:** grep for the *constant names* (`FW_ABSENT`, `_FW_ABSENT`, `_FW_HEADER_ABSENT`), not
the decorator, and assert every occurrence is accounted for. There are 7 constants across 7 modules
and at least one non-decorator use.
**Warning signs:** a rekey task whose acceptance criterion is a decorator count.

### Pitfall 6: Asserting every CMake path resolves, including the SDK

**What goes wrong:** BASE-04's gate reports 14 permanent violations from `PY32_SDK_SOURCES`, whose paths
live in a FetchContent download directory that exists only after a networked `cmake` configure.
**Why it happens:** the three source lists look homogeneous; only the variable prefix distinguishes them.
**How to avoid:** scope by variable — enforce `FIRESTARTER_COMMON_SOURCES` and `PY32_PLATFORM_SOURCES`,
structurally exempt `PY32_SDK_SOURCES` with a comment saying why. Do not express the exemption as a
`PY32_EXCLUDED` entry; it is a different concept.
**Warning signs:** a fixture whose expected violation count includes SDK paths.

### Pitfall 7: The `firestarter` name collision in the host repo

**What goes wrong:** a mechanical sweep for cross-repo paths pulls in
`firestarter_app/firestarter/data/pinouts.json` (the Python **package**), and the D-11 inventory then
claims a same-repo file is cross-repo — or worse, the rekey makes a local-file test depend on the
firmware sibling.
**Why it happens:** `_FA_DIR.parent / "firestarter"` (sibling repo) and `_APP_DIR / "firestarter"`
(package) appear four lines apart in `test_sdp_bus_config_drift.py`.
**How to avoid:** build the inventory from `.parent.parent` / `.parent.parent.parent`-rooted
expressions, and hand-verify each entry resolves outside the app repo.
**Warning signs:** an inventory entry that still resolves when the firmware sibling is renamed away.

### Pitfall 8: A repo-wide BASE-08 meta-test

**What goes wrong:** RED on arrival with 3 pre-existing violations in `firestarter_app/tools/`.
**Why it happens:** D-08 and CONTEXT both describe the convention as already universal; it is 4 of 7.
**How to avoid:** scope to `firestarter/scripts/check_*.py`, which by D-06 is exactly the v1.23 set and
needs no allow-list.
**Warning signs:** a meta-test globbing `**/check_*.py` or `firestarter_app/tools/`.

---

## Code Examples

### Parsing pio size output, both lines, all three envs

```python
# Verified against measured output from uno, uno328pb and leonardo clean builds.
SIZE_RE = re.compile(
    r"^(?P<kind>RAM|Flash):\s+\[[^\]]*\]\s+[\d.]+%\s+"
    r"\(used (?P<used>\d+) bytes from (?P<total>\d+) bytes\)",
    re.MULTILINE,
)

def parse_sizes(text):
    found = {m.group("kind"): (int(m.group("used")), int(m.group("total")))
             for m in SIZE_RE.finditer(text)}
    if set(found) != {"RAM", "Flash"}:          # exit-2 territory, NOT a pass
        raise ParseError(f"expected RAM and Flash lines, found {sorted(found)}")
    return found
```

### Parsing pio test counts — cases, suites and statuses together

```python
# Verified against measured `pio test -e native` and `-e native_nodevtools` output.
CASES_RE = re.compile(r"^=+\s+(?P<total>\d+) test cases:\s+(?P<ok>\d+) succeeded", re.MULTILINE)
SUITE_RE = re.compile(
    r"^\s*\S+\s+(?P<suite>native/avr/\S+)\s+(?P<status>PASSED|FAILED|ERRORED|IGNORED)\s",
    re.MULTILINE,
)

def parse_native(text):
    m = CASES_RE.search(text)
    if not m:
        raise ParseError("no 'N test cases:' summary line")
    suites = SUITE_RE.findall(text)
    if not suites:
        raise ParseError("no per-suite SUMMARY rows")
    # A-4's failure mode is 0 passing / 17 ERRORED -- assert all three facts.
    return {"cases": int(m.group("total")),
            "succeeded": int(m.group("ok")),
            "suites": len(suites),
            "all_passed": all(s[1] == "PASSED" for s in suites)}
```

### Macro-redefinition detection — version- and compiler-independent

```python
# Verified: matches all 360 real native warnings, and both g++ 14.2.0 and
# avr-g++ 7.3.0 fixture output (which differ in the ':line:col:' prefix).
MACRO_REDEF_RE = re.compile(r'warning:\s*"(?P<macro>[^"]+)"\s+redefined')
```

### D-12 fake sibling: committed tree, runtime marker

```python
# Verified end-to-end in an isolated repo this session.
def _materialise_fake_sibling(tmp_path):
    src = _HERE / "fixtures" / "fake_firestarter"       # committed, deliberately incomplete
    fake = tmp_path / "firestarter"
    shutil.copytree(src, fake)
    (fake / ".git").write_text("gitdir: /nonexistent\n")  # cannot be committed; created here
    return fake

def test_present_repo_missing_scan_target_is_hard_failure(tmp_path):
    fake = _materialise_fake_sibling(tmp_path)
    env = {**os.environ, "FIRESTARTER_FW_ROOT": str(fake)}
    r = subprocess.run([sys.executable, "-m", "pytest",
                        "tests/test_sdp_table_parity.py", "-q"],
                       capture_output=True, text=True, env=env, cwd=str(_APP_DIR))
    assert r.returncode != 0, "a present repo with a missing scan target must FAIL, not skip"
    assert "SKIP" not in r.stdout.upper()
```

Note the subprocess: `FW_ABSENT` and friends bind at import, so an in-process `monkeypatch.setenv`
would not change them (Correction C-15).

### CMake source-list extraction, scoped by variable

```python
SET_BLOCK_RE = re.compile(r"set\(\s*(?P<name>\w+)\s+(?P<body>[^)]*)\)", re.DOTALL)
PATH_RE = re.compile(r'"?(?P<path>[$\w{}/.\-]+\.(?:cpp|c|s|S))"?')

ENFORCED = {"FIRESTARTER_COMMON_SOURCES", "PY32_PLATFORM_SOURCES"}
# PY32_SDK_SOURCES is structurally exempt: ${PY32_SDK_ROOT} is a FetchContent
# download dir that exists only after a networked `cmake` configure. This is a
# property of FetchContent, NOT a PY32_EXCLUDED allow-list entry.
```

---

## State of the Art

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| `check_uno_ram.sh`'s hardcoded `RAM_FLOOR=545` (Phase 49/50 baseline) | Machine-readable baseline JSON + comparator across all three AVR envs, flash **and** RAM | This phase (D-02) | The floor is superseded. Note the coincidence: Uno free RAM today is **475 B**, which is *below* the 545 B floor — the script would fail if run. Measured: 2048 − 1573 = 475. The script is evidently not in CI (it is not referenced by either workflow) and its floor is stale by two milestones. **The plan should note this explicitly** rather than silently replacing a gate that is currently red. |
| Six modules / 33 legs (research A-7) | Seven modules / 24 decorator legs + 1 inline guard | Measured this session | The rekey pass is one module larger than research recorded |
| `mem_type` + `protocol` dual dispatch | `protocol`-only (v1.20) | v1.20 | `firestarter_py32_ci/CLAUDE.md` still documents the **old** dual-axis dispatch — that file is stale relative to `beta`'s CLAUDE.md. Do not use the py32 worktree's CLAUDE.md as a reference for anything but py32 specifics. |
| `flash_type_3.cpp` / `flash_type_4.cpp` | `flash_nor_unlock.cpp` / `flash_5v_page.cpp` | v1.19 Phase 104 | The CMake manifest still names the old files — BASE-04's first real firing |
| Leonardo free flash "2992 B" | **2600 B** on `beta` | Superseded by Phase 119's +392 B | Confirmed by measurement; budget against 2600 |

**Deprecated / stale in-tree:**
- `firestarter/scripts/check_uno_ram.sh` — floor `545` vs measured free `475`; not referenced by either
  workflow. Superseded by D-02.
- `[env:native_nodevtools]`'s "16-entry list" comments (three occurrences) — the list is 17.
- `/workspaces/CLAUDE.md`'s "Neither sub-repo is committed here" — a `.gitmodules` registers both.
- `/workspaces/firestarter_py32_ci/CLAUDE.md` — documents the pre-v1.20 `mem_type` fallback chain.

---

## Runtime State Inventory

This phase writes new files and rekeys existing test modules. It is not a rename/migration phase, but
the inventory is answered explicitly because D-09's rekey touches seven modules and because "what
still holds the old shape after the edit" is exactly this phase's subject matter.

| Category | Items found | Action required |
|----------|-------------|-----------------|
| Stored data | **None** — no database, no datastore, no persisted keys are touched. Verified: the phase's only new persistent artifact is the BASE-01 JSON, which is created, not migrated. | none |
| Live service config | **None** — no external service configuration is read or written. The two GitHub workflows are read for step-ordering facts but **not modified** by any BASE requirement. Verified by reading both files. | none |
| OS-registered state | **None** — no task scheduler, pm2, systemd or launchd registration. Verified: no such mechanism exists in either sub-repo. | none |
| Secrets / env vars | **New env-var names introduced**, not changed: the D-12 seam (`FIRESTARTER_FW_ROOT` or similar) and the BASE-07 seam (reuse `FIRESTARTER_CLAIMSCAN_TARGETS`). No existing secret or env var is renamed. `FIRESTARTER_CONFIG_DIR` and the `FIRESTARTER_*_SRC` seams already in the tree are untouched. | Document each new seam name in its checker's docstring |
| Build artifacts | `.pio/build/{uno,uno328pb,leonardo,native,native_nodevtools}/` were **cleaned and rebuilt** in this session to produce the baseline. These are gitignored and regenerate on demand. No installed package (pip egg-info, npm global) carries a name this phase changes. | none |
| **Stale in-repo state (the real answer)** | Three items whose current content contradicts the tree: `check_uno_ram.sh`'s floor (545 vs 475 free), `platformio.ini`'s "16-entry list" comments (×3), and the two stale CLAUDE.md claims | Only the first is in scope (superseded by D-02, and the plan must say so rather than leaving a red gate behind). The rest are deferred/noted. |

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `pio` (PlatformIO Core) | BASE-01 measurement, BASE-06 warning capture | yes | 6.1.19 | — |
| `avr-gcc` / `avr-g++` | AVR builds (via pio) | yes | 7.3.0 (`toolchain-atmelavr 1.70300.191015`) | — |
| host `g++` | BASE-06 fixture compile | yes | 14.2.0 (Debian 14.2.0-19) | none needed; must **fail** if absent, never skip |
| `python3` | all checkers | yes | 3.12.13 | — |
| `pytest` | all planted-fixture proofs | yes | installed in both repos | — |
| `git` | branch creation, D-12 fixture verification | yes | — | — |
| `arm-none-eabi-gcc` | **not required by this phase** | **no** | — | Out of scope; FUT-ARMSIZE. BASE-04 parses CMake **text**, never configures it |
| `cmake` | **not required by this phase** | **no** | — | Same — BASE-04 is a text gate, not a configure |
| `ninja` | **not required by this phase** | **no** | — | Same |
| Attached programmer board | not required | **no** (`/dev/ttyACM*`, `/dev/ttyUSB*` absent) | — | Beneficial: `test_no_programmer_found_*` are green |

**Missing dependencies with no fallback:** none. Every tool this phase needs is present.

**Missing dependencies with fallback:** `arm-none-eabi-gcc`, `cmake` and `ninja` are absent, which is
the recorded reason ARM sizing is out of scope (FUT-ARMSIZE). BASE-04 is designed as a **textual**
manifest gate precisely so it does not need them — this is worth stating in the plan, because a reader
may assume a CMake gate requires CMake.

---

## Validation Architecture

`workflow.nyquist_validation` is absent from `.planning/config.json`, so this section is included
(absent = enabled). [VERIFIED: config read]

### Test framework

| Property | Value |
|----------|-------|
| Framework (both repos) | `pytest` |
| Config file (firmware) | **none** — no `pytest.ini`, `pyproject.toml`, `setup.cfg` or `conftest.py`. Deliberate: `test_update_version.py:28` records the no-conftest house rule. |
| Config file (host) | `firestarter_app/pyproject.toml` (`[tool.ruff]`, mypy watermark comment); `tests/conftest.py` exists |
| Quick run (firmware) | `cd firestarter && python3 -m pytest tests/ -q` — **0.04 s**, 8 tests |
| Quick run (host, 7 modules) | `cd firestarter_app && python3 -m pytest tests/test_revision_constants_parity.py tests/test_dispatch_mirror.py tests/test_sdp_bus_config_drift.py tests/test_check_no_log_in_sdp_window.py tests/test_sdp_table_parity.py tests/test_check_is_memory_cmd_no_ifdef.py tests/test_gen_validation_header.py -q` — **49 tests, sub-second** |
| Quick run (meta, BASE-07) | `cd .planning/phases/123-… && python3 -m pytest test_check_permitted_claims_v123.py -q` |
| Full suite (firmware native) | `cd firestarter && pio test -e native && pio test -e native_nodevtools` — ~38 s combined |
| Full suite (host) | `cd firestarter_app && python3 -m pytest tests/ -q` — 1134 tests |
| Full suite (host gates) | `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/ && python tools/check_mypy_watermark.py` |

[VERIFIED: all commands run this session; durations measured]

### Phase requirements → test map

| Req | Behavior | Test type | Automated command | File exists? |
|-----|----------|-----------|-------------------|--------------|
| BASE-01 | Baseline JSON records 6 AVR numbers + 2 native pairs + watermarks | unit | `pytest firestarter/tests/test_check_size_baseline.py -q` | ❌ Wave 0 |
| BASE-01 | Parser extracts used/total from both `RAM:` and `Flash:` lines | unit | same module, fixture-driven against committed captured pio output | ❌ Wave 0 |
| BASE-01 | Comparator exits non-zero on an inflated flash figure | unit (planted) | same module, `fixtures/planted_flash_regression.log` | ❌ Wave 0 |
| BASE-01 | Comparator exits **2** on unparseable input | unit (planted) | same module, `fixtures/planted_unparseable.log` | ❌ Wave 0 |
| BASE-02 | Present repo + missing scan target ⇒ **hard failure**, not skip | integration (subprocess + committed fake sibling) | `pytest firestarter_app/tests/test_fw_presence_helper.py -q` | ❌ Wave 0 |
| BASE-02 | Absent repo (no `.git`) ⇒ honest skip | integration (subprocess) | same module | ❌ Wave 0 |
| BASE-02 | All 7 modules key on `.git`, none on a single file | unit (source scan) | recurrence lint, `pytest firestarter_app/tests/test_no_file_absence_proxy.py -q` | ❌ Wave 0 |
| BASE-03 | Skip reason "firmware absent" while `.git` exists ⇒ suite fails | integration (subprocess) | `pytest firestarter_app/tests/test_skip_census.py -q` | ❌ Wave 0 |
| BASE-03 | Unrecognised skip reason ⇒ fails | unit | same module | ❌ Wave 0 |
| BASE-04 | Mismatched source path ⇒ exit non-zero | unit (planted) | `pytest firestarter/tests/test_check_cmake_manifest.py -q` | ❌ Wave 0 |
| BASE-04 | Omission listed in `PY32_EXCLUDED` ⇒ exit 0 | unit (planted) | same module | ❌ Wave 0 |
| BASE-04 | `platform/py32f071/` absent ⇒ UNARMED, exit 0 | unit | same module | ❌ Wave 0 |
| BASE-05 | `RURP_*_PROVISIONAL` with zero consumers ⇒ exit non-zero | unit (planted) | `pytest firestarter/tests/test_check_orphan_provisional.py -q` | ❌ Wave 0 |
| BASE-05 | Same macro with ≥1 consumer ⇒ exit 0 | unit (planted control) | same module | ❌ Wave 0 |
| BASE-06 | One macro redefinition in compiled output ⇒ exit non-zero | unit (planted, real `g++` compile) | `pytest firestarter/tests/test_check_build_warnings.py -q` | ❌ Wave 0 |
| BASE-06 | AVR envs hold at zero; native envs hold at watermark | unit (captured-log fixture) | same module | ❌ Wave 0 |
| BASE-06 | Parser survives pio's surrounding framing | unit (captured real-output fixture) | same module | ❌ Wave 0 |
| BASE-07 | Forbidden phrase near a py32 token ⇒ exit non-zero | unit (planted) | `pytest .planning/phases/123-…/test_check_permitted_claims.py -q` | ❌ Wave 0 |
| BASE-07 | Same phrase with **no** py32 token nearby ⇒ exit 0 (D-16 both-directions) | unit (clean control) | same module | ❌ Wave 0 |
| BASE-07 | Empty target list ⇒ exit non-zero, never falls back to defaults | unit | same module | ❌ Wave 0 |
| BASE-07 | Missing required caveat ⇒ exit non-zero | unit (planted) | same module | ❌ Wave 0 |
| BASE-07 | Zero named targets exist ⇒ UNARMED, exit 0; any one exists ⇒ all must (D-15) | unit | same module | ❌ Wave 0 |
| BASE-08 | Every `firestarter/scripts/check_*.py` has a paired test + planted fixture | meta-test | `pytest firestarter/tests/test_checker_convention.py -q` | ❌ Wave 0 |
| BASE-08 | Zero-match glob fails (floor count) | meta-test | same module | ❌ Wave 0 |

*(Filenames are illustrative — D-08's convention and exact naming are Claude's discretion per CONTEXT.)*

### Sampling rate

- **Per task commit:** the quick run for the repo touched — `python3 -m pytest tests/ -q` in the
  firmware repo (0.04 s today), or the 7-module quick run in the host repo (sub-second).
- **Per wave merge:** full host suite (`pytest tests/ -q`, expect **1134 passed, 0 skipped**) plus the
  host gate trio (ruff / ruff-format / mypy watermark) if any host `.py` changed; firmware
  `pytest tests/ -q` plus both native envs if any firmware file changed.
- **Phase gate:** both native envs at **141/17 all PASSED**; all three AVR clean builds at the recorded
  flash/RAM; host suite at 1134/0-skipped; every new checker's planted-fixture test green; and the
  D-05 verbatim-evidence artifact (the `122-NONREGRESSION.md` shape) recorded before `/gsd-verify-work`.

**A sampling subtlety specific to this phase.** Several new tests *prove a failure*. Their green state
means "the checker correctly exited non-zero". A plan task that reports "all tests pass" without
naming which assertion fired is indistinguishable from a checker that silently passed everything —
the v1.12 hollow-GATE-03 mode. Every planted-fixture test must assert **both** the non-zero exit
**and** a distinctive substring of the failure message, exactly as v1.22's tests assert
`"should-now-work"` and `"missing required silicon caveat"` by name.

### Wave 0 gaps

- [ ] `firestarter/tests/fixtures/` — **directory does not exist**; every firmware-side planted fixture
      needs it created
- [ ] `firestarter/scripts/*.py` — **no Python checker exists there yet**; the directory holds only
      `check_uno_ram.sh`
- [ ] Committed captured-pio-output fixtures (size lines, test summary, a real macro-redefinition
      excerpt) — the raw material was measured this session and should be captured verbatim into
      fixtures rather than re-measured later
- [ ] `firestarter_app/tests/fixtures/fake_firestarter/` — the committed incomplete sibling tree
- [ ] Shared FW-presence helper module in `firestarter_app/tests/` — does not exist; seven modules
      currently each roll their own
- [ ] D-11 central scan-path inventory — does not exist
- [ ] `.planning/phases/123-…/fixtures/` — needs the four-to-five claim-gate fixtures including the
      D-16 clean AVR control that has no v1.22 analogue
- [ ] **No framework install needed** — pytest is present in both repos

---

## Security Domain

`security_enforcement` is not present in `.planning/config.json`, so this section is included
(absent = enabled).

### Applicable ASVS categories

| ASVS category | Applies | Standard control |
|---------------|---------|------------------|
| V2 Authentication | **no** | This phase adds no authentication surface — it writes build-measurement scripts and test gates |
| V3 Session Management | **no** | No sessions |
| V4 Access Control | **no** | No access-control surface. Note the phase does **not** push, publish, or comment publicly |
| V5 Input Validation | **yes** | Every checker parses untrusted-ish text (build logs, CMake files, markdown). Controls: anchored `re` patterns, explicit exit-2 on unparseable input, no `eval`/`exec`, no shell string interpolation |
| V6 Cryptography | **no** | No cryptography. (Phase 126's CRC32 config slots are *not* cryptographic and are out of this phase) |
| V12 Files & Resources | **yes** | Checkers read files by path from env-supplied roots. Controls: `pathlib` joins only, no user-controlled path reaching a shell, fixtures confined to committed directories |
| V14 Configuration | **yes** | New env seams (`FIRESTARTER_*`) become part of the gate's trust surface |

### Known threat patterns for this stack

| Pattern | STRIDE | Standard mitigation |
|---------|--------|---------------------|
| Command injection via `subprocess` with `shell=True` and an interpolated path | Tampering | **Always pass a list**, never `shell=True`. v1.22's `_run_scanner` already does this — copy it verbatim |
| Env-seam abuse: a checker's scan targets fully overridable, so CI could be pointed at a clean fixture | Tampering / Repudiation | The seam is a **test affordance**, not a production knob. Mitigate by documenting it, by keeping the default list explicit and non-pattern-based, and by D-15's all-or-nothing arming so an emptied list cannot pass |
| Gate that fails open on absent input | Repudiation ("the gates were green") | The phase's entire subject. Exit non-zero on missing target; exit 2 on parse failure; never skip on a missing tool |
| Path traversal through an env-supplied root | Tampering | `pathlib` resolution plus an assertion that the resolved fixture root is inside the repo, for the test-side seams |
| Regex denial of service on a large build log | DoS | The recommended patterns have no nested quantifiers over unbounded alternation. Keep it that way; avoid `(\s*\w+)*`-shaped constructs |
| A committed fixture that is not actually committed (the `.git` trap) | Repudiation | Verify with `git ls-files`, never with `git add`'s exit code — measured to be misleading |

**The dominant security-relevant risk in this phase is integrity of the verification record, not
confidentiality or availability.** Every mitigation above serves one property: a green gate must mean
the gate ran. That is also the phase's stated purpose, so the security controls and the functional
requirements coincide rather than compete.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | Recommending Option A for BASE-06 (zero on AVR + watermark 360 on native) is the requirement-faithful reading | §BASE-06 | If the operator intended zero everywhere, the phase needs an unscoped remediation touching 17 suite directories — a large scope change. **Worth an explicit confirmation**, since it reinterprets a requirement's scope. |
| A2 | The 360 native macro-redefinition warnings are pre-existing debt, not a recent regression | §BASE-06 | If recent, a bisect is warranted before watermarking. Mitigating evidence: the duplicate `pgmspace.h` shim design is documented in `firestarter/CLAUDE.md` as the intended host-shim mechanism, so the duplication is architectural. Not verified by bisect. |
| A3 | Reusing the env var name `FIRESTARTER_CLAIMSCAN_TARGETS` for the v1.23 claim gate is safe | §BASE-07 | The two checkers never coexist in one process (different phase directories), so a collision is not reachable. If a future run scanned both phases at once, one seam would aim both. Low risk, easily avoided by suffixing. |
| A4 | A 3-line proximity window is the right D-16 scope | §BASE-07 | If v1.23 artifacts separate a claim from its py32 subject by more than a line either way, the gate under-fires. This is a design recommendation, not a measured fact — the artifacts do not exist yet. The both-directions fixture bounds the risk. |
| A5 | Shipping the baseline comparator as fixture-tested parser logic (rather than a pytest that shells `pio`) | §Where the checkers plug in | A discretionary decomposition call within CONTEXT's stated discretion. If the operator wants the comparator to actually rebuild in CI, a workflow edit is needed, which CONTEXT does not scope. |
| A6 | BASE-05 should follow D-07's arming literally (option (a)) rather than always-armed (option (b)) | §BASE-05 | D-07 is locked and (a) is what it says, so this is low risk. Recorded because (b) is defensible and the plan should not silently discard it. |
| A7 | `check_uno_ram.sh` is not invoked by CI | §State of the Art | Verified by reading both workflow files — no step references it. If it is invoked by some other mechanism (a git hook, an operator habit), it is currently failing (floor 545 vs free 475) and the plan's supersession note becomes more urgent, not less. |

**All other claims in this document were measured in this session or read directly from a committed
file, and are tagged accordingly.**

---

## Open Questions

1. **BASE-06's intended scope — AVR only, or all five environments?**
   - **What we know:** AVR is at 0; native is at 360; the requirement text names no scope; D-13's
     stated purpose ("the next real warning is not buried") is served by Option A.
   - **What's unclear:** whether the operator, writing BASE-06, had the native envs in mind.
   - **Recommendation:** plan for Option A, and surface it as an explicit, one-line confirmation in the
     plan rather than a silent interpretation. It reinterprets requirement scope, which is exactly the
     class of decision the project's own history says should be checked (C-5 in v1.22 reached a locked
     decision unchecked).

2. **Does the BASE-01 comparator need to rebuild, or is parsing a supplied log sufficient?**
   - **What we know:** D-01 says the comparator "rebuilds and exits non-zero on violation". D-02 says
     it lives in the firmware repo "because the comparator must run `pio` builds".
   - **What's unclear:** whether "rebuilds" is a hard behavioural requirement or a rationale for the
     home choice. A `pio`-shelling pytest in `pytest tests/ -v` would pay a cold-toolchain cost on a
     cache miss.
   - **Recommendation:** implement **both** — a script that can rebuild (satisfying D-01 literally) and
     a pytest that exercises the parser/comparison against committed fixtures (fast, hermetic,
     BASE-08-compliant). This costs little and forecloses the question.

3. **What are the v1.23 closing-artifact filenames BASE-07 names in its default list?**
   - **What we know:** D-15 requires them named now, seven phases early, armed all-or-nothing.
   - **What's unclear:** Phase 130's artifact names are not yet fixed. v1.22's set was
     `122-LEDGER.md`, `122-RELEASE-NOTES-fw.md`, `122-RELEASE-NOTES-app.md`, `122-GH11-COMMENT.md`,
     `122-GH12-COMMENT.md`. CLOSE-02 (honesty ledger) and CLOSE-04 (release decision) imply at least
     `130-LEDGER.md` and a release-decision artifact.
   - **Recommendation:** derive the list from CLOSE-01…CLOSE-04's text, and record in the checker's
     docstring that Phase 130 must either produce exactly these names or amend the list in the same
     commit that renames one. D-15's all-or-nothing arming makes a half-written close a hard failure,
     which is the intent — but it also means a *renamed* artifact is a hard failure, so the coupling
     must be documented where Phase 130 will read it.

4. **Floor count for D-08's meta-test.**
   - **What we know:** the glob is `firestarter/scripts/check_*.py`; the count depends on the plan's own
     file decomposition (3 or 4).
   - **Recommendation:** set the floor last, after filenames are fixed, and assert `>= FLOOR` with
     FLOOR equal to the number actually shipped.

---

## Sources

### Primary (HIGH confidence) — measured or read this session

- `pio run -t clean -e {uno,uno328pb,leonardo}` + `pio run -e …` — flash/RAM and warning counts
- `pio test -e native`, `pio test -e native_nodevtools` — case counts, suite counts, warning counts
- `python3 -m pytest tests/ -q` in both sub-repos — 8 and 1134
- `pytest <7 proxy modules> -rs -q` — 49 passed, 0 skipped
- `g++ -c` and `avr-g++ -c` on a two-line macro-redefinition fixture — diagnostic text and
  `-Wmacro-redefined` rejection, both compilers
- `git init` scratch repo — `git add` / `git add -f` / `git update-index --add` behaviour on a `.git` path
- `git fetch origin` + `git rev-list --left-right --count beta...origin/beta` — both sub-repos
- `firestarter/platformio.ini` (full read) — `test_filter` × 2, `build_src_filter`, `default_envs`
- `firestarter/.github/workflows/build.yml`, `beta-build.yml` — triggers, full step ordering, cache config
- `firestarter/scripts/check_uno_ram.sh` — parser shape, `RAM_FLOOR`
- `firestarter/tests/` — full inventory, `test_update_version.py`'s no-conftest rule
- `firestarter_py32_ci/platform/py32f071/CMakeLists.txt` — full read, three source lists
- `firestarter_py32_ci/include/boards/py32f071_rurp_shield.h` — the two macros, the dead `#error`
- `.planning/phases/122-.../check_permitted_claims.py`, `test_check_permitted_claims.py`, `fixtures/`
- `.planning/phases/122-.../122-NONREGRESSION.md` — the eleven-row gate table, the 1134/1150 delta note
- `firestarter_app/tests/*.py` (the 7 proxy modules), `tools/*.py`, `pyproject.toml`, `.gitignore`
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/PROJECT.md`, `.planning/STATE.md`,
  `.planning/research/SUMMARY.md`, `.planning/config.json`
- `/workspaces/CLAUDE.md`, `firestarter/CLAUDE.md`

### Secondary (MEDIUM confidence)

- `.planning/research/SUMMARY.md` A-1/A-5/A-7 and the Phase-123 delivers block — cross-checked against
  my own measurements; agreed on Leonardo 2600 B and 141/17, differed on the skip census (3 vs 0) and
  the module count (6 vs 7), both differences explained above.

### Tertiary (LOW confidence)

- `.planning/graphs/graph.json` — **not used**. 701 h stale, 515 commits behind; would have been
  actively misleading for a file-level question. Noted for the record.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| BASE-01 numbers | **HIGH** | Every figure measured this session on clean builds; 5 of 6 cross-check exactly against the ROADMAP, the sixth was never recorded before |
| Native env agreement (D-04) | **HIGH** | Both envs run to completion, 141/141, 17 suites each; mechanism explained by an in-tree recorded measurement |
| Parse targets | **HIGH** | Verbatim output captured; existing script's regex verified still matching |
| Warning inventory | **HIGH** | Full clean rebuilds; counts decomposed by macro and by TU |
| Git `.git` refusal (D-12) | **HIGH** | Four command variants measured in an isolated repo; working mechanism verified end to end |
| CI step ordering (C-5) | **HIGH** | Both workflow files read in full |
| Proxy-module inventory | **HIGH** | Enumerated by grep and by pytest collection; constants read individually |
| CMake manifest structure | **HIGH** | File read in full on the correct branch |
| Orphan macro (BASE-05) | **HIGH** | Repo-wide grep on both trees, exactly one hit |
| D-08 convention violation | **HIGH** | Filesystem enumeration plus per-checker reverse grep |
| BASE-07 phrase table | **MEDIUM** | Supplied by research and cross-checked against REQUIREMENTS §Validation Ceiling; both agree, but the target artifacts do not exist yet |
| D-16 proximity design | **MEDIUM** | A design recommendation; the artifacts it will scan are unwritten. Bounded by the both-directions fixture requirement |
| Plan decomposition recommendations | **MEDIUM** | Within CONTEXT's stated discretion; not requirement-determined |

**Research date:** 2026-07-30
**Valid until:** the measured numbers are valid for firmware `5c9160a` / app `e7d3ee8` and go stale the
moment Phase 124 merges. Re-measure rather than re-cite after any firmware commit. The mechanism
findings (git behaviour, compiler diagnostics, CI ordering, module inventory) are stable for ~30 days.
