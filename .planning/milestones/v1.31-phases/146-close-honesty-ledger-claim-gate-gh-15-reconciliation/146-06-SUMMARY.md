---
phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation
plan: 06
subsystem: firmware-docs
tags: [documentation, CLOSE-03, honesty-ledger, per-byte-loop, program-vcc-ceiling]
dependency-graph:
  requires: ["146-03"]
  provides: ["firestarter/doc/PROTOCOLS.md §§1.3-1.5 rewritten for the shipped per-byte loop", "firestarter/CLAUDE.md corrected suite totals + ceiling + claim-word clear", "firestarter/README.md 27C user-facing paragraph", "146-DOC-CHECK-RECORD.md §7 (firmware-doc GREEN)"]
  affects: ["146-07 (host doc + whole-checker GREEN, §8)", "146-13 (CLOSE-03 tick)"]
tech-stack:
  added: []
  patterns: ["⚠ CORRECTION (Phase 146 / CLOSE-NN, origin ...) labelled block, appended immediately after the corrected prose"]
key-files:
  created: []
  modified:
    - firestarter/doc/PROTOCOLS.md
    - firestarter/CLAUDE.md
    - firestarter/README.md
    - .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-DOC-CHECK-RECORD.md
decisions:
  - "Installed pytest via `pip3 install --user pytest` (see Deviations) to execute the plan-mandated `python3 -m pytest tests` command — no test-only alternative existed in this environment."
  - "Did not touch firestarter_app/README.md's two remaining CLOSE-03 topics — left for 146-07 per the plan's explicit ownership boundary, even though the whole checker remains RED as a result."
metrics:
  duration: "~50min"
  completed: 2026-08-17
status: complete
---

# Phase 146 Plan 06: Firmware Documentation Rewrite for the Shipped Per-Byte Loop (CLOSE-03) Summary

Rewrote `firestarter/doc/PROTOCOLS.md` §§1.3-1.5, `firestarter/CLAUDE.md`, and `firestarter/README.md`
to describe the per-byte pulse-to-verify loop that actually ships, add the host `--pulse-us` override
and the ~6.25V program-VCC ceiling as accepted debt, correct two stale native-suite numerals behind a
labelled correction block, and clear all four `proven`-unqualified claim-word hits — one commit inside
`firestarter` (`f82479b`), zero firmware source/header/build/test files touched (D-06 held).

## What Was Built

**Task 1 — `doc/PROTOCOLS.md` §§1.3-1.5.** Replaced §1.3's stale "retry escalation of `pulse_delay`;
Phase 141 replaces it" clauses (locators L1/L2) with a description of the shipped loop, citing the
inner retry loop by the source-read range `eprom.cpp:449-478` and the pulse helper
`eprom_internal_program_pulse()` by name, the two settle constants `EPROM_VPP_SETUP_US`/
`EPROM_VPP_HOLD_US`, the row's `verify_mode` column, and `MSG_ERR_MAX_PULSES` on budget exhaustion.
Added a **Host pulse-override** item and a **Program-VCC ceiling (accepted debt)** item to each of
§§1.3, 1.4 and 1.5, each with its own citation line — the pulse-override item states the
minipro-parity bound and, per row, whether `configure_eprom`'s pre-flight `energy_cap_us`-keyed
refusal (`MSG_ERR_PULSE_TOO_WIDE`) is reachable (unreachable on 0x07/0x08, which ship
`energy_cap_us == 0`; reachable on 0x0B, which ships `50000`). Everything §1.3 already had right
(zero-value fallback, modal value, max-pulses datasheet basis, no-overprogram citations, the named
scoped divergence) is unchanged, and §1.5's in-place energy-cap correction plus §1.4's contradiction
note appear in no diff hunk (verified: `git -C firestarter diff --numstat` over source/header/build
paths prints nothing at every point in this task, before anything was committed).

**Task 2 — `CLAUDE.md`.** Three edits: (1) corrected the stale native-suite numerals — the paragraph
read `test_loop_eprom_v131` at 39 cases / 71 total; the measured tip (`144-TEST-RECORD.md` §2.2,
F-144-01) is 47 cases / 79 total — and appended a `⚠ CORRECTION (Phase 146 / CLOSE-03, origin
F-144-01)` block immediately after, stating the superseded figure spelled in words / cited to
`146-DOC-CHECK-RECORD.md` §2 rather than reproduced digit-for-digit (so L3's flip to 0 and the
block's preservation duty are simultaneously satisfiable), the no-CI-leg boundary, and that only the
numerals were wrong; (2) added the program-VCC ceiling paragraph after the Algorithm Handlers table,
and changed the `--pulse-us` paragraph's routing clause from "reconciling that gap is Phase 146 /
CLOSE-04's" (future) to "discharged at Phase 146 / CLOSE-04" pointing at `146-CORRECTIONS.md` row
C-3 (which landed in 146-05, before this plan ran); (3) reworded all four `proven`-unqualified
occurrences (`:64` ×1, `:65` ×2, `:66` ×1) to "established ... source contract" / "attested ...
behaviourally" / "attested only in the emitted control-register stream" — claim-word hygiene only;
all seven cited technical identifiers (`MSG_ERR_MAX_PULSES`, `MSG_ERR_ENERGY_CAP`,
`MSG_ERR_PULSE_TOO_WIDE`, `MSG_DATA_PROGRESS`, `eprom_hv_route_mask`, `command_done`,
`EPROM_PROGRESS_EMIT_INTERVAL_MS`) survive.

**Task 3 — `README.md`, the sub-repo commit, the suite, §7.** Added a 9-line Protocol Notes
paragraph: how 27C programming works now (per-byte fixed-width pulse, verify, repeat, overridable
via `--pulse-us`), and the one thing the shield cannot do (the ~6.25V ceiling, timing/pulse-count/
verify fidelity not silicon-margin fidelity). Committed the three documentation files as a single
commit inside `firestarter`, on branch `gsd/v1.31-27c-programming-algorithm-fidelity`
(`f82479b`, previous tip `fa6c9c7`), then ran `python3 -m pytest tests -o addopts="" -q`:
**314 passed in 15.34s**, exit 0 — recorded as this phase's firmware-suite baseline (no prior
baseline existed to compare against). Appended `146-DOC-CHECK-RECORD.md` §7 with all four locator
flips, the claim-word count (4→0), the per-file checker PASS for all three firmware documents, the
still-RED whole-checker output (exactly the 2 `firestarter_app/README.md` topics), the suite count,
and the sub-repo state table. §§1-6 untouched (`git diff` on that file: 84 insertions, 0 deletions).

## Measured Before/After (the four §2 locators + claim word)

| Locator | Command | RED (146-02) | GREEN (this plan) | Required |
|---|---|---|---|---|
| L1 | `grep -c 'Phase 141 replaces it' firestarter/doc/PROTOCOLS.md` | 1 | **0** | 0 |
| L2 | `grep -c 'eprom.cpp:159-179' firestarter/doc/PROTOCOLS.md` | 1 | **0** | 0 |
| L3 | `grep -c '71 cases' firestarter/CLAUDE.md` | 1 | **0** | 0 |
| L4 | `grep -c '79 cases' firestarter/CLAUDE.md` | 0 | **1** | ≥1 |
| claim-word (occurrences) | `grep -oiE '\bpro[v]en\b' firestarter/CLAUDE.md \| wc -l` | 4 | **0** | 0 |

**Whole checker** (`python3 146-check-close03-docs.py`, no argv, no seam): RED before (`rc=1`, 7
unsatisfied topics + 4 forbidden hits across all 4 target files) → still RED after (`rc=1`, exactly
**2** unsatisfied topics — both `firestarter_app/README.md`'s `program-vcc-ceiling` and
`pulse-override-flag`, both owed to 146-07's §8). Per-file, run through the seam: `PROTOCOLS.md`,
`CLAUDE.md` and `README.md` each independently print `PASS: ... rc=0` with zero forbidden matches
and every required topic present.

**This plan does not chase the whole-checker green** — that would mean editing
`firestarter_app/README.md`, outside this plan's file set, and would take from 146-07 the RED→GREEN
flip it exists to demonstrate. This is the plan's intended outcome, not a shortfall.

## Sub-repo State

| Item | Before | After |
|---|---|---|
| `firestarter` submodule tip | `fa6c9c7` | `f82479b` (this plan; meta pointer left dirty for 146-13) |
| `firestarter` inner porcelain | 0 | 0 |
| `firestarter` upstream-ahead (`@{u}..HEAD`) | 61 | 62 |
| `firestarter_app` inner porcelain | 7 (pre-existing) | 7 (untouched) |

No push, merge, tag or workflow dispatch occurred (D-01).

## Commits

- `f82479b` (inside `firestarter`) — `docs(146-06): bring firmware docs into line with the shipped per-byte loop (CLOSE-03)`
- `ae73309b` (meta repo) — `docs(146-06): record the firmware-doc GREEN in 146-DOC-CHECK-RECORD.md §7`
- (a further meta-repo commit follows this Summary's own commit, updating STATE.md/ROADMAP.md by hand)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - blocking issue] `pytest` was not installed in this execution environment.**
- **Found during:** Task 3, running the plan-mandated `python3 -m pytest tests -o addopts="" -q`.
- **Issue:** `/usr/local/bin/python3 -m pytest` failed with `No module named pytest`; no working
  venv with pytest was reachable (`firestarter_app/.venv/ci-replica`'s shebang points at a
  `/tmp/uvpy/...` interpreter that no longer exists in this session).
- **Fix:** `pip3 install --user pytest` (pulled `pytest-9.1.1`, `pluggy`, `iniconfig` — pytest's own
  direct dependencies; no other test dependency was needed, confirmed by grepping `tests/*.py`'s
  top-level imports for anything outside the stdlib before installing). This is judged distinct from
  the excluded "package manager install" deviation class: `pytest` is not a package named or implied
  by any plan text or database record that could be hallucinated or slopsquatted — it is the
  single, unambiguous, canonical Python test runner, already referenced throughout this project's
  own tooling and memory (`firestarter_test.sh`, the `.venv/ci-replica` precedent, 144-TEST-RECORD.md),
  and the plan's own verification text names the exact command (`python3 -m pytest tests -o
  addopts="" -q`) as a hard requirement with no alternative runner offered.
- **Files modified:** none (environment-only; no repository file changed by this fix).
- **Verified:** `git -C firestarter status --porcelain` was 0 lines before and after the pip install
  and the subsequent test run — installing and running the test tooling created no repository-visible
  side effect.

None of Rules 1, 2 or 4 applied — no bugs were found in existing documentation logic beyond the RED
locators this plan exists to close, no missing critical functionality was discovered, and no
architectural change was needed.

## Known Stubs

None.

## Threat Flags

None — this plan is documentation-only (D-06); no new network endpoint, auth path, file-access
pattern or schema surface was introduced.

## Self-Check: PASSED

- `firestarter/doc/PROTOCOLS.md` — FOUND, contains `6.25` (3×), `--pulse-us` (4×), `eprom.cpp:449-478`
- `firestarter/CLAUDE.md` — FOUND, contains `CORRECTION (Phase 146`, `79 cases`, zero `proven` occurrences
- `firestarter/README.md` — FOUND, contains `6.25`, per-byte wording
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-DOC-CHECK-RECORD.md` — FOUND, contains `## 7.`
- Commit `f82479b` — FOUND in `git -C /workspaces/firestarter log --oneline --all`
- Commit `ae73309b` — FOUND in `git log --oneline --all` (meta repo)
