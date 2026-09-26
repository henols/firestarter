---
phase: 137
slug: close-honesty-ledger-claim-gate-gh12-followup
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-05
approved: 2026-08-05
---

# Phase 137 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `.planning/research/PITFALLS.md` (P-11, P-12, P-21, P-25) and `.planning/research/SUMMARY.md`'s
> Phase 136/close section, measured against `firestarter_app@<current tip>` on
> `gsd/v1.30-sdp-surface-retirement`, and the meta repo on
> `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`.
> Modeled on `134-VALIDATION.md`/`136-VALIDATION.md`'s shape.

---

## ⚠ This phase must NOT be executed under `--auto`/`--chain`

Plan 137-05 (CLOSE-06) carries a `checkpoint:human-action` gate — this project's own established
practice (`reference_auto_mode_autoapproves_outward_facing_gates`) is that `--auto`/`--chain` silently
auto-approve every `checkpoint:human-verify` gate but never a `checkpoint:human-action` gate. Plan
137-05's review task is typed `human-action` specifically so this holds structurally, not merely by
convention — but the correct operational instruction remains: dispatch this phase without either flag.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (meta repo)** | pytest (stdlib-only scanner + subprocess-based paired tests, no `conftest.py`) |
| **Framework (submodule)** | pytest (+ `pytest-cov`, `syrupy`), `firestarter_app/pyproject.toml` |
| **Config file (submodule)** | `firestarter_app/pyproject.toml` (`addopts = "-ra -q"`) |
| **Meta-repo quick run** | `cd /workspaces && python3 -m pytest .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/test_check_permitted_claims_v130.py -o addopts="" -q` |
| **Submodule quick run** | `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/test_check_diagnostic_report_claims.py -o addopts="" -q` |
| **Submodule full suite** | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` |
| **Estimated runtime** | ~5s meta quick · ~10s submodule quick · ~150s submodule full |

⚠ **Always pass `-o addopts=""`.** `addopts` is `-ra -q` in the submodule's `pyproject.toml`; doubling
`-q` suppresses the count line and a green run looks contentless.

⚠ **`tools/ci_replica_venv.sh` is the only local path to a real mypy count** — the devcontainer's own
mypy exits 2 against numpy, and the devcontainer is py3.12 while CI is py3.9/3.11.

⚠ **The meta repo runs no pytest workflow at all.** Nothing in CI ever runs
`test_check_permitted_claims_v130.py` — this project's own history (`123-…`'s checker suite sitting RED
for weeks, undetected) is the reason plan 137-01's Task 3 and plan 137-06's Task 1 both require the
suite to be run and its output recorded as an explicit, human-legible acceptance criterion, not a CI
green checkmark.

⚠ **Two repos, two branches, worktree isolation OFF phase-wide.** All six plans run strictly
sequentially (wave 1→6), even where `files_modified` sets don't overlap — there is exactly one
`firestarter_app` checkout and no worktree to isolate a second one in.

---

## Sampling Rate

- **After every task commit:** the relevant quick run above (meta or submodule, whichever the task
  touched).
- **After every plan wave:** for submodule-touching plans (137-02, and the final CI-parity in 137-06),
  `tools/ci_replica_venv.sh` (all 5 legs). Record `mypy errors: N (watermark: 35)` and `checked N
  source files` every time — entering this phase the baseline is 33/35, headroom 2, checked 132, suite
  1504 (Phase 136.1's own closing measurement).
- **Before the phase is considered done:** `tools/ci_parity.sh` AND `tools/ci_replica_venv.sh` both
  green, plus `137-CI-PARITY.md`'s Before/After record (plan 137-06 Task 2) — this is also the
  ROADMAP's own cross-cutting instruction ("run the CI-parity recipe one final time over the whole
  milestone diff before closing").
- **Max feedback latency:** ~10s per commit · ~150s per full-suite run.

---

## Per-Task Verification Map

Wave numbers are pre-assigned by the planner (1→6, one plan per wave — worktree isolation is OFF
phase-wide, so waves express real dependency order, not parallelism).

| Req | Wave | Behaviour to prove | Test Type | Automated Command | File Exists | Status |
|-----|------|--------------------|-----------|--------------------|-------------|--------|
| CLOSE-02 | 1 | The claim gate's default targets resolve strictly inside this phase's own directory and carry this phase's own number prefix (the two mandatory P-11 legs) | unit (subprocess) | `python3 -m pytest test_check_permitted_claims_v130.py -k "resolve_inside_this_phase_directory or basenames_are_this_milestones" -o addopts=""` | ❌ new | ⬜ pending |
| CLOSE-02 (mechanism) | 1 | Arming: zero-of-four → UNARMED+exit 0; partial → hard fail; vocabulary + proximity window correctly classify 3 planted fixtures | unit (subprocess) | `python3 -m pytest test_check_permitted_claims_v130.py -o addopts=""` | ❌ new | ⬜ pending |
| CLOSE-03 | 2 | `diagnostic_report.py`'s string literals scanned; planted violation flips the gate; real source stays clean | unit (subprocess) + AST | `.venv/ci-replica/bin/python -m pytest tests/test_check_diagnostic_report_claims.py -o addopts=""` | ❌ new | ⬜ pending |
| CLOSE-04 | 3 | The honesty ledger carries all six mandated corrections, the P-21 tripwire, and both operator-batch items; passes the claim gate alone | doc + gate scan | `FIRESTARTER_CLAIMSCAN_TARGETS_V130=137-LEDGER.md python3 check_permitted_claims.py` | ❌ new | ⬜ pending |
| CLOSE-05, RELOCK-07 | 4 | Release notes state a withdrawal, never name `write --sdp-relock` as available; RELOCK-07's stale label fixed at every live occurrence + all four citation sites | doc + gate scan + grep | `FIRESTARTER_CLAIMSCAN_TARGETS_V130=137-RELEASE-NOTES-app.md python3 check_permitted_claims.py` | ❌ new | ⬜ pending |
| CLOSE-06 | 5 | Reviewed gh#12 reply frozen; posting gated on BOTH operator real-time authorization AND a fresh mechanical shipped-check | checkpoint:human-action + doc | `FIRESTARTER_CLAIMSCAN_TARGETS_V130=137-GH12-COMMENT.md python3 check_permitted_claims.py` | ❌ new | ⬜ pending |
| CLOSE-01 | 6 | The claim gate, run with NO arguments, is armed and green against all four real artifacts | unit (subprocess) + doc | `python3 check_permitted_claims.py` (no args) | (uses files from waves 1,3,4,5) | ⬜ pending |
| — | 6 | Whole-milestone CI-parity recipe, run one final time | full suite + shell script | `tools/ci_parity.sh && tools/ci_replica_venv.sh` | ✅ exists (edited) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

There is no Wave 0, matching Phase 134/136's own precedent: the six plans occupy waves 1→6, and every
`❌ new` row above is created by the plan that owns its requirement, in the same wave, paired with its
verification in the same commit. Plan 137-01's mechanism is provably correct via fixtures BEFORE the
four real artifacts exist (the "UNARMED" state is a legitimate, tested, non-failing state) — this
phase's version of the "no plan depends on test scaffolding from a later wave" discipline.

---

## Non-Vacuity Obligations

A pre-authored gate proves nothing until it is seen to fail. This project has shipped unreachable-green
gates before (v1.23 P129/P130, and this exact claim-gate class in v1.23's own P-11 defect) — treat that
as the standing failure mode to guard against. Each must be **observed RED once**, then restored
**byte-identically**:

| # | Planted break | What must go RED |
|---|---------------|-------------------|
| 1 | Plan 137-01: `_DEFAULT_TARGETS`'s `"137-LEDGER.md"` entry temporarily renamed to `"130-LEDGER.md"` | `test_default_target_basenames_are_this_milestones` |
| 2 | Plan 137-01: one `_DEFAULT_TARGETS` entry temporarily pointed at a path outside `_HERE` (e.g. joined against `os.pardir`) | `test_default_targets_resolve_inside_this_phase_directory` |
| 3 | Plan 137-01: `FORBIDDEN_PATTERNS`'s `should-now-work` entry temporarily removed | `test_planted_forbidden_phrase_flips_checker_to_failure` |
| 4 | Plan 137-02: one `FORBIDDEN_PATTERNS` entry temporarily removed from the host-side copy | `test_planted_violation_flips_checker_to_failure` |
| 5 | Plan 137-06: `_DEFAULT_TARGETS` temporarily reverted to a stale/partial state after all four artifacts exist | `test_armed_and_green_against_the_four_real_artifacts` |

---

## Manual-Only Verifications

**Exactly one, and it is the phase's whole reason for a `checkpoint:human-action` gate:**

- **Plan 137-05, Task 2 — the operator's wording judgement and posting-timing authorization.** A string
  scan (the claim gate) cannot detect an implied overclaim, a misleading omission, or wrong tone — and
  cannot know, in real time, whether the beta has actually shipped. Both require the operator's own
  judgement. This is explicitly the same three-way split every prior close phase in this project's
  history has documented (v1.22 `122-LEDGER.md`, v1.23's `130-…`): mechanically checkable / requires
  human judgement / inherently unverifiable in-phase (the causal SDP claim, permanently, until real
  silicon is on the bench).

Everything else in this phase is automatable — the claim gate, the host-side gate, the CI-parity
recipe, and the documentation edits are all machine-verifiable.

---

## Validation Sign-Off

- [x] Every task has an `<automated>` verify, EXCEPT plan 137-05's Task 2, which is the phase's one
      `checkpoint:human-action` gate and carries a `<human-check>` instead, per this project's own
      Nyquist-rule exception for judgement-only verifications — measured 2026-08-05: 6 plans, 15 tasks
      total, 14/15 carry an `<automated>` command, 1/15 carries `<human-check>`.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — the one non-automated
      task (137-05 Task 2) is immediately preceded and followed by automated tasks.
- [x] Wave 0 covers all MISSING references — satisfied by the same mechanism 134/136-VALIDATION.md
      recorded: there is no Wave 0; each `❌ new` file is created by the plan that owns its requirement,
      in the same wave.
- [x] No watch-mode flags — grepped all six plans for `--watch` / `ptw` / `pytest-watch` /
      `--looponfail`: zero hits.
- [x] Feedback latency < 15s (per commit) — per the Test Infrastructure table above.
- [ ] Every non-vacuity obligation above observed RED, then restored byte-identically — execution-time
      obligation; cannot be discharged before the code exists. 5 such proofs planned.
- [ ] mypy headroom recorded at every submodule-touching wave merge (start: 33/35, headroom 2, from
      Phase 136.1's own closing measurement) — execution-time obligation.
- [x] `nyquist_compliant: true` set in frontmatter (the one exception is a judgement-only checkpoint,
      not a missing test).

**Requirement coverage:** 7/7 (CLOSE-01…06, RELOCK-07). Tick ownership is fully disjoint — CLOSE-02
solely by plan 137-01; CLOSE-03 solely by 137-02; CLOSE-04 solely by 137-03; CLOSE-05 AND RELOCK-07
solely by 137-04 (two requirements, one plan, both documentation-only and closely related); CLOSE-06
solely by 137-05; CLOSE-01 solely by 137-06 (it is the only requirement that can be discharged after
all four closing artifacts exist, so it is necessarily the phase's last tick). No requirement is
claimable by two plans.

**Approval:** approved 2026-08-05 by Claude, planning this phase directly (standard planning mode, no
`/gsd-discuss-phase` CONTEXT.md exists for this phase; the operator's own standing instruction across
phases 136 → 136.1 → 137, recorded in `.planning/v1.30-OPERATOR-BATCH.md`'s header, is to drive all
phases in order without stopping mid-flight to ask). No `gsd-plan-checker` verdict exists yet for this
phase at the time this file is written — this sign-off records what was verified directly during
planning: requirement coverage 7/7 with disjoint tick ownership, 14/15 tasks carrying an automated
verify (the 15th being the phase's sole, deliberate, judgement-only gate), the five non-vacuity
obligations named up front, and the CLOSE-06 posting-timing design (deferred pending the beta push
unless both a live mechanical check and a fresh operator authorization agree) reasoned through
explicitly rather than left as an assumption baked into a later plan.
