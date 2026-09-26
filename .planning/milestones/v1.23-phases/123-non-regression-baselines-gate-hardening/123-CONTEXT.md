# Phase 123: Non-Regression Baselines & Gate Hardening - Context

**Gathered:** 2026-07-30
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers the **measurement and enforcement scaffolding** that every later v1.23
phase is judged against:

1. A recorded, machine-readable flash/RAM/native-count baseline (BASE-01).
2. A fail-**closed** replacement for the cross-repo skip proxy that currently fails **open**
   (BASE-02, BASE-03).
3. Four new checkers — CMake manifest drift, orphan provisional macro, warning count,
   permitted claims — each proven able to fail on a committed planted violation
   (BASE-04…BASE-08).

**No firmware code moves in this phase.** The ordering rule `123 → 124` is load-bearing: a gate
authored after the change it detects can only bless what already happened. Nothing here merges,
cherry-picks or renames a firmware file; that is Phase 124's job.

**Explicitly NOT in this phase:** any py32 source landing, any `platform/py32f071/` content, the
ARM CI trigger, the pin-map refusal guard restructure, and any host DFU work. Those are Phases
124 and 127.

</domain>

<decisions>
## Implementation Decisions

### Baseline record (BASE-01)

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

### Checker home & execution surface (BASE-04…BASE-08)

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

### Fail-closed blast radius (BASE-02, BASE-03)

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

### Gate shapes (BASE-06, BASE-07)

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone contract (read first)

- `.planning/REQUIREMENTS.md` — BASE-01…BASE-08 verbatim; §"Validation Ceiling" is the **source of
  the forbidden-phrase table** D-16 implements; §"Operator Decisions Locked at Definition" must not
  be re-litigated.
- `.planning/ROADMAP.md` §"v1.23 — PY32F071 Integration" (lines 1957–2019) — phase goal, the five
  success criteria, the non-regression invariant, and the load-bearing `123 → 124` ordering rule.
- `.planning/PROJECT.md` §"Current Milestone: v1.23 PY32F071 Integration" (from line 36) — the
  research-corrections block, including the fail-open gate reproduction (A-7) and the hollow
  `RURP_PY32F071_PINMAP_CONFIGURED` guard (finding 5).
- `.planning/research/SUMMARY.md` — 4 streams, corrections R-1…R-18, adjudications A-1…A-7.

### Direct precedents to copy

- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/check_permitted_claims.py`
  — the checker BASE-07 is modelled on: explicit non-pattern default target list, `FIRESTARTER_CLAIMSCAN_TARGETS`
  env seam with `os.environ.get(...)` and **no default** so "absent" and "present-but-empty" stay
  distinguishable, fixtures deliberately unreachable from the default set, and the "explicit
  non-claim" docstring convention.
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/test_check_permitted_claims.py`
  and its `fixtures/` — the paired-pytest + planted-fixture shape BASE-08 generalises.
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-NONREGRESSION.md`
  — the "recorded verbatim evidence" artifact shape D-05 adopts (command, expected, observed, per row).
- `firestarter/scripts/check_uno_ram.sh` — the pio-output-parsing idiom D-13 reuses, and the
  hardcoded `RAM_FLOOR=545` that D-02's baseline supersedes.

### Files this phase modifies or measures

- `firestarter_app/tests/test_revision_constants_parity.py` (19 skipif legs),
  `test_dispatch_mirror.py` (2), `test_sdp_bus_config_drift.py` (2),
  `test_check_no_log_in_sdp_window.py` (1), `test_sdp_table_parity.py` (1),
  `test_check_is_memory_cmd_no_ifdef.py` (1), `test_gen_validation_header.py` (1) — the **7**
  proxy-carrying modules of D-09. (Research said six; measured count is seven.)
- `firestarter/platformio.ini` — `[env:native]` and `[env:native_nodevtools]` `test_filter` lists
  (17 entries each, **read and confirmed**). A stale comment in `[env:native_nodevtools]` still says
  "the FULL 16-entry list" — worth correcting while nearby, but not a requirement.
- `firestarter/.github/workflows/build.yml:108` and `beta-build.yml:66` — the existing
  `pytest tests/ -v` steps that make D-06's firmware-repo home CI-live.
- `firestarter_app/.github/workflows/ci.yml` — single `actions/checkout`, no firmware sibling. This
  is why D-05 chooses local evidence over a CI leg. **Not modified by this phase.**

### Existing baseline/checker inventory (do not duplicate)

- `firestarter_app/tools/baseline/chip_database.baseline.json` and `dispatch_baseline.json` — the
  `meta`-block-plus-data JSON convention D-01 follows.
- `firestarter_app/tools/check_*.py` — six existing checker↔test naming pairs that establish D-08's
  convention.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`check_uno_ram.sh`** — already runs `pio run -e uno`, parses the `RAM: … (used N bytes from M
  bytes)` line, and exits 1 below a floor. Its parser is directly reusable for D-01's comparator
  across all three AVR envs and both `Flash:`/`RAM:` lines; its hardcoded floor is exactly what the
  baseline JSON replaces.
- **v1.22's `check_permitted_claims.py`** — the env-seam + fail-closed + never-vacuous shape is
  reusable almost verbatim for BASE-07; only the phrase table, the target list and D-16's proximity
  scoping change.
- **`firestarter_app/tests/fixtures/planted_*`** (7 committed fixtures) — the naming and placement
  convention D-08 formalises, and proof the "committed planted violation" pattern already works in
  this project.
- **`tools/check_mypy_watermark.py`** — the watermark idiom D-13 borrows for the total-warning count.

### Established Patterns

- **Checker + paired pytest + committed fixture + env seam.** Every gate in this project is a
  standalone `check_*.py` with an env override so its test can aim it at deliberately-violating
  fixtures without touching a real file, and fixtures live where the default target list can never
  reach them. Deviating from this shape is the anti-pattern.
- **Coarse-key arming.** BASE-02's `../firestarter/.git` key is the general form: decide *whether a
  gate applies* from something structural and un-renameable, then treat a missing fine-grained
  target as a **failure**, never a skip. D-07 and D-15 both apply this same shape one level down.
- **Assert counts, never "tests pass."** A suite that stops being collected also reports green —
  hence D-04's per-env case/suite pairs and D-08's floor count.
- **`firestarter/tests/` vs `firestarter/test/`.** `test/` holds PlatformIO native suites (globbed
  into builds); `tests/` holds Python script tests and is PIO-invisible. D-14 depends on this.

### Integration Points

- **Phase 124 consumes this phase's output**, not the reverse. Everything written here must be
  readable by a later phase without recomputation: the baseline JSON (MERGE-05/06), the central scan
  inventory (MERGE-07), and the armed-on-arrival checkers (MERGE-02/04).
- **Both sub-repos are still on `beta`** — no v1.23 milestone branch exists in either yet
  (`git branch --show-current` → `beta` in both). Per ROADMAP the sub-repos fork off `beta`; the
  branch must be created and checked out **before** any executor writes into a submodule, and this
  is verified with `git` at execute time rather than assumed.
- **The two py32 git worktrees** (`firestarter_py32_ci/`, `firestarter_app_py32/`) are gitignored
  checkouts of the same two repos, never gitlinked. This phase should not write into them.

</code_context>

<specifics>
## Specific Ideas

- The operator consistently chose the shape that **produces an exit code over the shape that
  produces a number a human reads** (D-01, D-08, D-13) and the shape that **cannot be silently
  forgotten over the shape that is explicit but manual** (D-07's self-arming key over an arm-flip
  constant). Where a further choice arises during planning that this CONTEXT does not settle, resolve
  it the same way.
- Three decisions deliberately go **one step past the literal requirement text**, each for a stated
  reason, and the planner should keep them rather than trim back to the requirement wording:
  the recurrence lint (D-09), the skip-reason allow-list (D-10), and the total-warning watermark
  (D-13, which the requirement's own stated purpose demands).
- D-04 carries a **live risk to Phase 124** that must be surfaced, not absorbed: if the two native
  envs report different case counts, MERGE-06's wording is unsatisfiable and needs amending before
  Phase 124 plans against it.

</specifics>

<deferred>
## Deferred Ideas

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

### Reviewed Todos (not folded)

- **`prove-pio-dev-flag-fails-closed.md`** — tagged `resolves_phase: 999.15`. Empirically proving
  `-D DEV_TOOLS=${sysenv.VAR}` fails OPEN is the same *discipline* as this phase but a different
  mechanism (PlatformIO env-var expansion, not a checker). Its v1.23 echo — ARM `DEV_TOOLS`-off as
  an explicit commented CMake decision — is Phase 124's MERGE-08. Stays in the backlog.
- **`correct-v128-py32-roadmap-prior-art.md`** — already tagged `resolves_phase: 130`, owned by
  CLOSE-03. Not pulled forward.

</deferred>

---

*Phase: 123-non-regression-baselines-gate-hardening*
*Context gathered: 2026-07-30*
