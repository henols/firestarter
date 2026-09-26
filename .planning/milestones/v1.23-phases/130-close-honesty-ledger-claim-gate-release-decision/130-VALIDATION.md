---
phase: 130
slug: close-honesty-ledger-claim-gate-release-decision
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-02
---

# Phase 130 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `130-RESEARCH.md` § Validation Architecture. `workflow.nyquist_validation` is
> absent from `.planning/config.json` → treated as **enabled**.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (both sub-repos + the meta `.planning/` checkers); PlatformIO Unity for `pio test -e native` |
| **Config file** | `firestarter_app/pyproject.toml`; `firestarter/platformio.ini` (`[env:native]`); **none** for `.planning/phases/**` checkers (no `conftest.py`, no `pytest.ini`) |
| **Quick run command** | claim gate: `cd .planning/phases/123-non-regression-baselines-gate-hardening && python3 -m pytest test_check_permitted_claims.py -q` (~0.3 s) |
| **Full suite command** | `cd firestarter && python3 -m pytest tests/ -q` (221) · `cd firestarter_app && python3 -m pytest tests/ -q` (1303) · both `.planning/` checker suites |
| **Estimated runtime** | quick ~0.3–0.6 s · firmware ~7 s · app ~116 s |

**Additional gate commands (all read-only, all verified available this session):**

| Gate | Command |
|------|---------|
| `[SHARED:S*]` cross-repo sync (41 legs) | `cd firestarter && FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q` |
| Decision parse (C-1 regression) | `node -e '…extractDecisions(130-CONTEXT.md)'` → assert `outcome !== "could-not-parse"` and 16 ids |
| Firmware native suite | `cd firestarter && pio test -e native` |
| App codegen drift | `cd firestarter_app && python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check && git diff --exit-code firestarter/messages.py` |

---

## Sampling Rate

- **After every task commit:** the relevant quick run — claim-gate suite for CLOSE-02 tasks, the
  41-leg sync gate for D-11 tasks, the decision parser for the C-1 regression, the new CLOSE-01
  checker for R-N tasks.
- **After every plan wave:** `firestarter` `pytest tests/` + `pio test -e native`; `firestarter_app`
  `pytest tests/`; both `.planning/` checker suites.
- **Phase gate:** every suite green **on the exact tree that gets merged** (CONTEXT constraint 9),
  captured in `130-NONREGRESSION.md`, **before** `130-DECISION.md` is committed — and therefore
  before any push.
- **Max feedback latency:** 1 s for every per-task quick run; ~120 s for the per-wave app suite.

---

## Per-Task Verification Map

Plan/task ids are assigned by the planner; the rows below fix the requirement → command mapping the
planner must honour. Threat refs are omitted — no `security` capability hook is active at
`plan:pre`; access-control controls are recorded under Manual-Only below.

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|---|---|---|---|---|---|
| CLOSE-01 | Every R-N superseded figure is corrected, or provably inside a labeled correction/history block | unit (new checker) | `python3 .planning/phases/130-…/check_record_corrections.py` | ❌ Wave 0 (D-08) | ⬜ pending |
| CLOSE-01 | The checker exits non-zero on a planted stale figure **and** on a mislabeled block | unit (new fixtures) | `python3 -m pytest .planning/phases/130-…/test_check_record_corrections.py -q` | ❌ Wave 0 (D-08 / BASE-08) | ⬜ pending |
| CLOSE-01 | The checker is not defeated by criterion 1's own needle quote (`ROADMAP.md:2468`) nor by v1.22-archive history | unit (two dedicated legs) | same suite | ❌ Wave 0 (**C-7, C-8**) | ⬜ pending |
| CLOSE-01 | `130-CONTEXT.md` stays parseable — all 16 `D-NN` ids extract | unit (regression) | `node -e '…extractDecisions…'` | ✅ green (fixed pre-planning) | ✅ green |
| CLOSE-02 | All four contracted artifacts exist and carry the required caveat with zero forbidden matches | unit (existing, **mis-targeted**) | `cd .planning/phases/123-… && python3 check_permitted_claims.py` | ⚠️ points at the wrong directory — **C-2** | ❌ red |
| CLOSE-02 | D-15 all-or-nothing arming fails on three-of-four | unit (existing, **RED**) | `python3 -m pytest test_check_permitted_claims.py -q` | ⚠️ 1 failed / 9 passed — **C-3** | ❌ red |
| CLOSE-02 | `[SHARED:S4]` stays byte-identical across both record copies after D-11's §5(a)+§5(d) edit | integration (existing) | `FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q` | ✅ 41/41 green | ✅ green |
| CLOSE-03 | v1.24–v1.27 byte-unchanged | one-shot, deliberately **not** a checker (D-16) | `sha256sum` of each entry line before/after + `git diff -U0 -- .planning/ROADMAP.md`, recorded in `130-NONREGRESSION.md` | ❌ procedure, not code | ⬜ pending |
| CLOSE-03 | The renumber landed; no `v1.23 Binary Command Protocol` remains in the `## Milestones` list | grep assertion in a plan task | `grep -n 'v1.2[3-8]' .planning/ROADMAP.md` | ❌ | ⬜ pending |
| CLOSE-04 | `130-DECISION.md` committed **before** any push | structural (plan ownership) | `git log --oneline -- .planning/phases/130-…/130-DECISION.md` predates both `origin/beta` moves | ❌ | ⬜ pending |
| CLOSE-04 | The observed cut tag is **read**, never computed | procedure | `gh release list --repo henols/firestarter --limit 3` (and `…firestarter_app…`) | ✅ command verified read-only | ⬜ pending |
| CLOSE-04 | `firestarter_py32f071.hex` present in the **real** b15 assets (D-03) | procedure | `gh release view <observed> --repo henols/firestarter --json assets` | ✅ command verified (b14 → 3 AVR hexes, no py32) | ⬜ pending |
| CLOSE-04 | PyPI resolution verified directly from a clean temp env | procedure | `python3 -m venv /tmp/v && /tmp/v/bin/pip download --no-deps --pre firestarter==<observed> -d /tmp/d` | ❌ | ⬜ pending |
| CLOSE-04 | Both channels verified public before the phase claims the cut complete | committed transcript (`115-VALIDATION.md` / `122-CHANNELS.md` shape) | recorded in `130-NONREGRESSION.md` | ❌ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Three of these are **pre-existing REDs that predate this phase** — they are not this phase's damage,
and Phase 129's lesson applies: fix locators only, with a RED-preserving proof.

- [ ] **Repoint `_DEFAULT_TARGETS`** in `.planning/phases/123-…/check_permitted_claims.py` at the
      Phase 130 directory, in the **same commit** that writes the artifacts — covers **C-2**. Update
      the docstring's four resolved paths. Do **not** switch to explicit `argv` /
      `FIRESTARTER_CLAIMSCAN_TARGETS`: arming applies only to the default set, so the all-or-nothing
      guarantee would be lost.
- [ ] **Narrow `test_check_permitted_claims.py:301-304`'s side-effect glob** from `130-*.md` to the
      four contracted names, then prove the narrowed guard **still fires** when a `130-LEDGER.md` is
      planted in the real directory — covers **C-3**. Do not delete the guard.
- [ ] **New `check_record_corrections.py` + `test_check_record_corrections.py` + `fixtures/`** —
      the R-N phrase table, label-awareness for **correction and history** blocks, a self-reference
      exemption for the success-criteria region, and both planted-violation fixtures (D-08 / BASE-08).
- [x] **`130-CONTEXT.md` decision-label rewrap** — covers **C-1**; landed pre-planning at `0f9a709`,
      verified `outcome: parsed`, 16/16 ids, all trackable.
- [ ] Framework install: **none needed** — pytest, node, `gh`, `pio`, `pip`/`venv` all present.
      `arm-none-eabi-gcc`/`cmake`/`ninja` are absent but installable; per D-07 a local ARM build
      supports **delta / byte-identity** claims only, never an absolute size.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|---|---|---|---|
| The outbound `--no-ff` merge and push of `beta` in both sub-repos | CLOSE-04 | Outward-facing and irreversible — the push auto-fires CI and cuts a public prerelease. Standing structural gate: **no task may run `git push`**. `--auto`/`--chain` auto-approves human-verify checkpoints and `autonomous: false` does not protect it, so the gate is **which plan owns the command**, not a flag | Operator runs the merge + push per the sequence recorded in `130-DECISION.md`, after that file is committed |
| The PyPI `workflow_dispatch` of `firestarter_app`'s `publish.yml` | CLOSE-04 | Outward-facing. Standing structural gate: **no task may run `gh workflow run`**. The `tag` input flows into `ref:`, so it must carry the **observed** tag read from `gh release list` | Operator dispatches with the observed tag; no literal `3.0.0b15` may appear in any command intended to be run verbatim (constraint 5) |
| Wording review of `130-RELEASE-NOTES-fw.md` and `130-RELEASE-NOTES-app.md` | CLOSE-02 | D-02, blocking. The claim scanner's own docstring says a green run is the **mechanizable half only** — it cannot detect an implied overclaim, a misleading omission, or wrong tone | Operator reads both drafts and approves before either body reaches a public release |
| Posting both b15 release bodies | CLOSE-02, CLOSE-04 | Outward-facing; follows the D-02 review | Operator posts after approval |
| Whether a caveated disclosure of the non-allocated `1209:0001` constitutes "advertising a USB identity" under §5(c) | CLOSE-02 | Judgment on registry terms, not a testable property (research C-5, A3). Resolved pre-planning: §5(c) stays **byte-unchanged**; the tension is carried as an owned residual | Reasoning recorded in `130-DECISION.md` and as a negative-space row in `130-LEDGER.md`; operator may overrule at the D-02 review |

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` verify or a named Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without an automated verify
- [ ] Wave 0 covers all MISSING references (C-2, C-3, D-08 checker)
- [ ] No watch-mode flags
- [ ] Feedback latency < 120 s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
