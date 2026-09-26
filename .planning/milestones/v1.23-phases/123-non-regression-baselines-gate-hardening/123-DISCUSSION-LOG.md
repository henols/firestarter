# Phase 123: Non-Regression Baselines & Gate Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-30
**Phase:** 123-non-regression-baselines-gate-hardening
**Areas discussed:** Baseline record (home, format, freshness) · Checker home & execution surface · Fail-closed blast radius · Gate shapes (warning-count + empty-target claims gate)

---

## Todo cross-reference

13 pending todos keyword-matched Phase 123; 11 were pure keyword noise and were not presented.

| Option | Description | Selected |
|--------|-------------|----------|
| Fold neither | `prove-pio-dev-flag-fails-closed` is `resolves_phase: 999.15` (PlatformIO env-var expansion, not a checker; its v1.23 echo is Phase 124 MERGE-08). `correct-v128-py32-roadmap-prior-art` is `resolves_phase: 130` (CLOSE-03). | ✓ |
| Fold `prove-pio-dev-flag-fails-closed` | Adjacent "prove a gate fails closed" discipline, different mechanism | |
| Fold `correct-v128-py32-roadmap-prior-art` | Pull one CLOSE-03 line item forward | |

**User's choice:** Fold neither.

---

## Baseline record — home, format, freshness

### Shape

| Option | Description | Selected |
|--------|-------------|----------|
| JSON + comparator script | Machine-readable baseline plus a checker that rebuilds, parses the pio size report, exits non-zero on violation; makes MERGE-05's ≤ 64 B rule an exit code | ✓ |
| Markdown artifact only | `122-NONREGRESSION.md` shape; cheapest and most readable, but "cite by reading" stays a human act | |
| JSON source of truth + generated Markdown | Most durable; adds a generator plus a drift check | |

### Repo

| Option | Description | Selected |
|--------|-------------|----------|
| Firmware repo | `firestarter/baselines/` + `scripts/`, pytest in `firestarter/tests/`; comparator runs where the build is; supersedes `check_uno_ram.sh`'s `RAM_FLOOR=545` | ✓ |
| Host repo (`firestarter_app`) | Joins existing `tools/baseline/` JSONs and the mature harness — but makes the comparator cross-repo, i.e. silently skipped in CI | |
| Meta repo phase dir | Sees both sub-repos and survives sub-repo branch churn — but never executed by any CI | |

### Freshness

| Option | Description | Selected |
|--------|-------------|----------|
| Re-measure all, with provenance | Clean builds; tree SHA + toolchain version per number; roadmap figures are a cross-check, measured number wins on disagreement, discrepancy recorded | ✓ |
| Transcribe, measure only the gaps | Fastest; inherits research numbers from a possibly different tree | |
| Re-measure, numbers only | Fresh but no provenance; can't separate a regression from a toolchain difference | |

### Native counts

| Option | Description | Selected |
|--------|-------------|----------|
| Per-env pairs + record the relationship | Separate `{cases, suites}` for `native` and `native_nodevtools`, plus whether they agree as a measured fact | ✓ |
| One shared pair asserted for both | Literally what MERGE-06 says; unsatisfiable if the envs differ | |
| Per-env pairs, no relationship | Safe but drops the DEV_TOOLS-invariance signal | |

**Notes:** Measured during discussion — both envs carry **17** `test_filter` entries (roadmap's "17 suites" confirmed by reading), while a stale `[env:native_nodevtools]` comment still says "the FULL 16-entry list". The 141 *case* count can only come from an actual run.

---

## Checker home & where gates actually run

### Execution surface

| Option | Description | Selected |
|--------|-------------|----------|
| Local run with recorded evidence | Gates hard-fail locally where the rename bug actually bites; "gates ran" proven by verbatim command + output in the phase artifact (122-NONREGRESSION.md pattern); CI keeps skipping honestly | ✓ |
| Add a cross-repo CI leg | Automatic forever — but Actions can't check out above the workspace, and the matching firmware commit is on an unpushed branch, so the leg would score against `beta` (wrong tree) and it reverses `81fa53c` | |
| Both | Most durable; adds unscoped work to a phase whose premise is "nothing moves yet" | |

### Checker homes

| Option | Description | Selected |
|--------|-------------|----------|
| Scan-target-follows-home | BASE-04/05/06 → firmware repo (firmware CI already runs `pytest tests/`); BASE-07 → meta phase dir where its targets live. No new checker becomes cross-repo. | ✓ |
| All four in the host repo | Most mature harness — but deliberately makes three new checkers cross-repo, i.e. CI-skipped | |
| All four in the meta phase dir | One place to look; never executed by any CI | |

### Dormancy (targets that don't exist until Phase 124)

| Option | Description | Selected |
|--------|-------------|----------|
| Coarse-key, hard-fail on the fine target | `platform/py32f071/` present ⇒ armed, missing fine target ⇒ hard failure; absent ⇒ UNARMED notice. Self-arms at the merge; mirrors BASE-02's own idiom | ✓ |
| Explicit arm-flip at Phase 124 | Maximally reviewable; one more step that can be forgotten, leaving a green dormant gate | |
| Fail closed from Phase 123 onward | Never dormant; firmware CI red for the whole phase, which normalises red | |

### BASE-08 enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| Convention-derived meta-test | `check_X.py` ⇒ `test_check_X.py` ⇒ `planted_X*`, with a hardcoded floor count so a zero-match glob fails | ✓ |
| Explicit checker registry | Handles multi-fixture checkers and named exceptions; second source of truth that can drift | |
| Satisfied by inspection | Cheapest; leaves the one requirement with no mechanism, in a phase about mechanisms | |

**Notes:** Mid-area correction — `firestarter/tests/` is **not** a thin harness. `build.yml:108` and `beta-build.yml:66` both run `pytest tests/ -v`, so firmware-repo checkers run in CI unconditionally with no sibling and no skip class. This changed the recommendation from the host repo to scan-target-follows-home.

---

## Fail-closed blast radius

### Rekey scope

| Option | Description | Selected |
|--------|-------------|----------|
| All 7 modules + a recurrence lint | Rekey everything to `../firestarter/.git`, plus a source-scan gate forbidding the bare `not <file>.exists()` idiom from returning, with its own fixture | ✓ |
| All 7 modules, no lint | Nothing fail-open today; nothing stops it coming back tomorrow | |
| Only modules v1.23 will disturb | Requires predicting which files a 52-commit merge renames — the exact prediction the finding says you can't make | |

### Census strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Reason allow-list | Every skip reason must be allow-listed; firmware-absent reason additionally fails when `.git` exists; allow-list doubles as documentation | ✓ |
| Reason-only (literal BASE-03) | Smallest; a novel skip reason still passes unnoticed | |
| Reason + pinned skip count | Strongest signal, but flaky here (no-programmer-found tests flip with a live board attached) and would get bumped reflexively | |

### Failure mechanics

| Option | Description | Selected |
|--------|-------------|----------|
| Central target inventory | One committed inventory + one test resolving all paths when `.git` exists, failing with each missing path named; modules' skipif keys purely on `.git`; supplies Phase 124's "manifest paths resolve" artifact | ✓ |
| Per-module guard | Direct attribution; recreates the seven-way duplication that caused the bug, and import-time failure can mask collection | |
| Per-module dedicated resolve test | Clear attribution, no masking, still seven copies | |

### Planted fixture form

| Option | Description | Selected |
|--------|-------------|----------|
| Committed fake sibling + env seam | Minimal fake firmware sibling with a presence marker and an incomplete file set, reached via a `FIRESTARTER_*`-style env seam; real tree untouched | ✓ |
| `tmp_path` built at test time | No fake-`.git` awkwardness; nothing committed, so BASE-08's "committed fixture" is only weakly satisfied | |
| monkeypatch the path constants | Cheapest; proves the assertion fires against a patched constant, not that real resolution detects a real missing file | |

**Notes:** Measured inventory is **7** proxy-carrying modules (~27 `skipif` legs), not the six research reported — `test_revision_constants_parity.py` alone carries 19. Trap flagged for the planner: a nested `.git` *directory* cannot be committed, so the presence marker needs a committable form.

---

## Gate shapes: warning-count + empty-target claims gate

### Warning-count mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Parse + zero-floor + total watermark | Zero macro-redefinitions plus a recorded total-warning watermark in the baseline JSON; reuses `check_uno_ram.sh` parsing and the mypy-watermark idiom; delivers BASE-06's stated purpose | ✓ |
| Parse, macro-redefinition only | Exactly the literal wording; the next real warning still gets buried, which is the reason the requirement exists | |
| Blanket `-Werror` on the AVR envs | Compiler-enforced, undriftable; makes framework-header warnings fatal and likely breaks all three builds | |

**Notes:** Tested before offering — `gcc -Werror=macro-redefined` is rejected by `cc1` (*"no option '-Wmacro-redefined'; did you mean '-Wbuiltin-macro-redefined'?"*). That spelling is Clang's; GCC emits `"FOO" redefined` by default behind no named `-W` option. So no targeted `-Werror` route exists on avr-gcc.

### Warning fixture

| Option | Description | Selected |
|--------|-------------|----------|
| Real compiler on a committed fixture | Committed `.cpp` under `firestarter/tests/fixtures/` (PIO-invisible), compiled in the pytest, output fed to the gate's own parser; no `platformio.ini` change | ✓ |
| Captured build-log text fixture | Hermetic and exercises pio's exact framing; proves nothing about whether the compiler still spells it that way after a toolchain bump | |
| Dedicated throwaway PlatformIO env | Full-pipeline fidelity; a build per test run and an env that must never reach `default_envs` | |

### Claims gate arming

| Option | Description | Selected |
|--------|-------------|----------|
| Named list + all-or-nothing arming | Closing artifacts named in a committed default list (records the contract 7 phases early); none exist ⇒ UNARMED exit 0; any exists ⇒ armed and all must exist; "empty ⇒ non-zero" proven by fixture via the env seam | ✓ |
| No default list — explicit invocation only | Never spuriously red; the scan contract isn't recorded until close, so Phase 130 could scan four files instead of five | |
| Create skeleton closing artifacts now | Armed and green from day one; commits near-empty close artifacts that read as done work | |

### Forbidden-phrase scoping

| Option | Description | Selected |
|--------|-------------|----------|
| Proximity-scoped to py32 | A phrase fires only when co-occurring with a `py32`/`PY32F071` token in the same line/sentence; fixture must pin both directions | ✓ |
| Literal match + allow-listed lines | Simple regex, auditable exceptions; every legitimate AVR sentence needs an entry and the list gets padded | |
| Literal match, no exceptions | Ungameable; forces every AVR claim to be reworded, fighting the non-regression narrative in every artifact | |

**Notes:** The trap surfaced here is real — v1.23's artifacts are largely an AVR non-regression story, and those AVR targets genuinely *are* bench-validated from earlier milestones.

---

## Claude's Discretion

- Baseline JSON schema/key names and the `Flash:`/`RAM:` parser regex (reuse `check_uno_ram.sh`'s shape).
- Exact checker/fixture filenames, subject to the D-08 naming convention.
- Whether the required-caveat half of v1.22's claims gate carries forward — default **yes**, adapted to the "no PY32F071 PCB exists" caveat.
- Plan/wave decomposition and commit granularity.

## Deferred Ideas

- **Cross-repo CI leg** checking out the firmware sibling — blocked on Actions' inability to check out above the workspace and on the matching firmware commit living on an unpushed branch during v1.23. Revisit once v1.23 merges to `beta`.
- **ARM flash/RAM baseline with a RAM ceiling** — already tracked as FUT-ARMSIZE; `arm-none-eabi-gcc`/`cmake`/`ninja` absent from this devcontainer.
- **Stale `[env:native_nodevtools]` comment** ("FULL 16-entry list" — it's 17). Fold in only if a plan already edits `platformio.ini`.

### Reviewed Todos (not folded)

- `prove-pio-dev-flag-fails-closed.md` — `resolves_phase: 999.15`; its v1.23 echo is Phase 124 MERGE-08.
- `correct-v128-py32-roadmap-prior-art.md` — `resolves_phase: 130`, owned by CLOSE-03.
