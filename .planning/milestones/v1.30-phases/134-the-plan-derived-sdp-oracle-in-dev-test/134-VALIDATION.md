---
phase: 134
slug: the-plan-derived-sdp-oracle-in-dev-test
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-04
approved: 2026-08-04
---

# Phase 134 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `134-RESEARCH.md` §8 (Validation Architecture), measured against
> `firestarter_app@57e8eb5` on `gsd/v1.30-sdp-surface-retirement`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (+ `pytest-cov`, `syrupy` — 30 snapshots) |
| **Config file** | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`, `addopts = "-ra -q"`) |
| **Quick run command** | `.venv/ci-replica/bin/python -m pytest tests/test_chip_test_sdp_leg.py tests/test_op_registration_parity.py -o addopts="" -q` |
| **Full suite command** | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` |
| **Estimated runtime** | ~10 s quick · ~143 s full (1338 passed, 81.84 % cov) |

⚠ **Always pass `-o addopts=""`.** `addopts` is `-ra -q`; doubling `-q` suppresses the count line and a
green run looks contentless.

⚠ **`tools/ci_replica_venv.sh` is the only local path to a real mypy count** — the devcontainer's own
mypy exits 2 against numpy, and the devcontainer is py3.12 while CI is py3.9/3.11.

⚠ **`tools/ci_parity.sh` has no no-board leg.** The no-board condition is ambient — record the board
state, never claim a leg.

⚠ **Leg 1 points `FIRESTARTER_FW_ROOT` at an empty dir.** The devcontainer's sibling layout otherwise
masks CI-only test defects. Run it before any push.

---

## Sampling Rate

- **After every task commit:** quick run above (~10 s). `test_op_registration_parity.py` is in *every*
  commit's quick set because it fails at **collection**, not at assertion — otherwise a slow-to-notice RED.
- **After every plan wave:** `tools/ci_replica_venv.sh` (all 5 legs). Record
  `mypy errors: N (watermark: 35)` and `checked N source files` **every time** — headroom is **2**.
- **Before `/gsd-verify-work`:** `tools/ci_parity.sh` **and** `tools/ci_replica_venv.sh` both green,
  plus the before/after record in `134-CI-PARITY.md` (the 131/133 shape).
- **Max feedback latency:** 10 s per commit · 143 s per wave.

---

## Per-Task Verification Map

Wave letters follow `134-RESEARCH.md` §3.2 (A → B → C1‖C2 → D → E‖ → F); plan IDs are assigned by the
planner and this table is re-keyed at execution time.

| Req | Wave | Behaviour to prove | Test Type | Automated Command | File Exists | Status |
|-----|------|--------------------|-----------|-------------------|-------------|--------|
| LEG-01 | A | 43 ALLOW chips derive 6 SDP steps; **no new CLI option** | unit | `pytest tests/test_chip_test_sdp_leg.py -k "derive and allow" -o addopts=""` | ❌ W0 | ⬜ pending |
| LEG-02 | A | 41 REFUSE chips get 6 NA steps carrying `sdp_capability()`'s reason | unit | `… -k "derive and refuse"` | ❌ W0 | ⬜ pending |
| LEG-03 | A | A≠B at **every** byte; neither all-`0x00`/all-`0xFF`; B ≠ `generate_pattern(region)` | unit | `… -k "pattern_b"` | ❌ W0 | ⬜ pending |
| LEG-04 | B | B→verify→A→verify before any lock | unit | `… -k "baseline_transition"` | ❌ W0 | ⬜ pending |
| LEG-05 | B | Verdict comes from read-back equality, never the write's bool | unit | `… -k "oracle_readback"` | ❌ W0 | ⬜ pending |
| **LEG-06** | B + C2 + E2 | write succeeds after lock ⇒ **BAD** ⇒ **exit 1** | unit + CLI | `… -k "lock_leaked"` **and** `pytest tests/test_dev_test_cmd.py -k "exit" -o addopts=""` | ❌ W0 | ⬜ pending |
| LEG-07 | E1 | partial read-back change ⇒ BAD (gh#11) | unit | `… -k "partial_readback"` | ❌ W0 | ⬜ pending |
| LEG-08 | E1 | 4 degenerate fixtures (empty / short / all-`0x00` / all-`0xFF`) never read as equality | unit ×4 | `… -k "degenerate"` | ❌ W0 | ⬜ pending |
| LEG-12 | C1 + E3 | `HELD`/`NOT-HELD`/`NOT-RUN(reason)` in **both** surfaces; **no boolean anywhere** in `to_dict()` | unit + CLI | `pytest tests/test_diagnostic_report.py -k "hold" -o addopts=""` | ❌ W0 | ⬜ pending |
| LEG-13 | E2 | NA/SKIPPED oracle drops N-of-M (M 4→10) — **pinning test only, no new counting logic** | unit | `pytest tests/test_chip_test.py -k "count_applicable and sdp" -o addopts=""` | ❌ W0 | ⬜ pending |
| LEG-14 | E4 | scoped constants: "rewrite" present, "erase" absent, + planted-violation non-vacuity leg | unit | `pytest tests/test_sdp_recovery_wording.py -o addopts=""` | ❌ W0 (new file) | ⬜ pending |
| LEG-16 | E1 | no-op-write fixture ⇒ baseline step BAD | unit | `… -k "dead_write_path"` | ❌ W0 | ⬜ pending |
| LEG-17 | E2 | R1…R6 (+R7): `sdp_lock.assert_not_called()` **and** a visible `NOT-RUN` reason | CLI ×6 | `pytest tests/test_dev_test_cmd.py -k "laundering" -o addopts=""` | ❌ W0 | ⬜ pending |
| LEG-18 | F | gh#20 finding recorded; backlog item filed with a **named owner** | doc | manual — record + backlog check | ❌ W0 | ⬜ pending |
| — | all | **op-parity gate green** (LEG-15 stays ticked) | unit ×7 | `pytest tests/test_op_registration_parity.py -o addopts=""` | ✅ exists | ⬜ **must stay green through Wave A** |
| — | all | Phase 133's LEG-09/10/11 proofs unchanged | unit | `pytest tests/test_chip_test_sdp_leg.py -o addopts=""` | ✅ exists | ⬜ **regression floor** |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_sdp_recovery_wording.py` — LEG-14's scoped constant grep + planted-violation leg (**new file**)
- [ ] Degenerate-read-back fixtures ×4 and the dead-write-path operator double — LEG-08, LEG-16
- [ ] A synthetic nonzero-`chip-id` DB entry fixture — D-17's R1/R2 causal chain
- [ ] No framework install needed; no `conftest.py` change expected beyond reusing
      `make_app_context` (`tests/conftest.py:229`) and `app_context` (`:325`)

---

## Non-Vacuity Obligations

A pre-authored gate proves nothing until it is seen to pass. This project has shipped unreachable-green
gates twice (v1.23 P129/P130). Each must be **observed RED once**, then restored **byte-identically**:

| # | Planted break | What must go RED |
|---|---------------|------------------|
| 1 | **P-01:** make B = `generate_pattern(region)` | the every-byte assertion |
| 2 | **LEG-06:** invert the OK/BAD arms | **two** tests (D-03's polarity pin), not one |
| 3 | **LEG-16:** make the fixture's write real | the baseline step goes OK, failing the fixture's test |
| 4 | **LEG-14:** plant a constant saying "erase" | the scoped grep |
| 5 | **D-14:** revert the precedence to `max` | the mixed-run exit-1 test |
| 6 | **D-08:** remove the gate-set membership | a dead-write-path run observed emitting `sdp_lock` |
| 7 | **Parity gate:** no new leg needed | confirm `test_altered_registry_copy_fails_parity_non_vacuous` (`:753`) still passes after `_ALL_OPS` grows to 13 |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| gh#20 triage finding recorded + backlog item filed with a named owner | LEG-18 | A record/documentation obligation, not a runtime behaviour | Record the finding in the phase record; file the underlying AT28C256 write failure to backlog with an owner; verify by reading both artifacts |
| **The causal claim "the lock inhibited the write"** | — | **⚠ Evidence Ceiling — NOT provable this milestone.** A locked die is unrepresentable in either repo's stubs; no fixture simulates real inhibition. Fixtures pin the host's *response* to a scripted read-back. | **Not to be verified, claimed, or smoothed over in any artifact.** Real silicon is missing with no fallback. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — **measured 2026-08-04: 11/11 plans,
      every task. `134-05/06/07/09` carry 2 tasks / 2 `<automated>`; the other seven carry 3 / 3.
      Zero tasks without one.**
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — **trivially satisfied:
      there are zero gaps, so the longest run without automated verify is 0.**
- [x] Wave 0 covers all MISSING references — **satisfied by a DIFFERENT mechanism than the checklist
      assumes, recorded rather than silently ticked. There is no wave 0: the 11 plans occupy waves
      1→9. Every `❌ W0` row in the coverage table above is created by the plan that owns its
      requirement, in the same wave, as the paired `test(...)` commit — the same feat+test pairing
      Phase 133 used. The obligation is met; the wave number in the column header is not.**
- [x] No watch-mode flags — **grepped all 11 plans for `--watch` / `ptw` / `pytest-watch` /
      `--looponfail`: zero hits. Every verify is a one-shot `pytest … -o addopts="" -q`.**
- [x] Feedback latency < 10 s (per commit) — **per the Test Infrastructure table above: quick run
      ~10 s. Plans verify against targeted modules with `-k`, not the ~143 s full suite.**
- [ ] Every non-vacuity obligation above observed RED, then restored byte-identically — **execution-time
      obligation; cannot be discharged before the code exists. 13 such proofs in Phase 133 for
      comparison.**
- [ ] mypy headroom recorded at every wave merge (start: 33/35, **2 slots**) — **execution-time
      obligation, one record per wave merge.**
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-08-04 by Claude, driving the phase under the operator's standing
instruction to run 134/136/137 without handing off mid-flight.

**⚠ CORRECTED 2026-08-04T15:20Z — the caveat below was true when written and is now FALSE.** A
concurrent `/gsd-plan-phase 134` session was still running when this file was approved; it had not
yet committed its verdict. It has since done so (commit `b0e489fa`): **`gsd-plan-checker` returned
`## VERIFICATION PASSED` — 11/11 plans, ZERO blockers, ZERO warnings**, having explicitly cleared
one-writer-per-file across all 9 waves, disjoint tick ownership, the Evidence Ceiling honesty check,
all 7 non-vacuity obligations, and the `test_op_registration_parity.py` collection-time trap.
Requirement coverage 14/14 and decision coverage 18/18 both passed. So a plan-checker verdict for
Phase 134 **does** exist and **has** been read. The "no such artifact" observation applied only to
Phase 133. The original text is kept below rather than deleted, because the honesty ledger in Phase
137 should be able to see what was claimed and when.

**What this approval does NOT assert.** No `gsd-plan-checker` verdict was read. No plan-checker
artifact exists for Phase 134 — and none existed for Phase 133 either; that verdict is only ever
reported in-session and hand-copied into `STATE.md`, which for 134 still reads `status: ready` /
"Phase 134 context gathered" from the discuss session. So the checker's result is unavailable from
disk, and this sign-off does not stand in for it. What was verified directly instead: requirement
coverage is 14/14 with no requirement claimed twice (LEG-01…08, 12, 13, 14, 16, 17, 18 across 8 of
the 11 plans; `134-04`, `134-06` and `134-08` tick nothing), the ROADMAP tags allowed requirement IDs
per plan, and the automated-verify facts measured above.
