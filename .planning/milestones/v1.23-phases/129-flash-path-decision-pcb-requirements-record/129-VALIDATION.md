---
phase: 129
slug: flash-path-decision-pcb-requirements-record
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-02
plans_assigned: 2026-08-02
---

# Phase 129 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `129-RESEARCH.md` §"Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` — firmware repo, `firestarter/tests/` (stdlib + pytest only) |
| **Config file** | **none** — no `conftest.py`, `pytest.ini`, `pyproject.toml`, `setup.cfg` or `tox.ini` anywhere in the firmware repo. Per-module path resolution is the house convention (see `tests/test_vpp_seam_manual_on_every_board.py` docstring). |
| **Quick run command** | `python -m pytest tests/test_flash_path_record_sync.py -v` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds (quick) / ~30 seconds (full, 21 existing modules + 1 new) |

**CI status — must be stated in the new module's docstring.** This module will run in **NO CI leg on this branch**. `pytest tests/ -v` exists only in `build.yml` (main) and `beta-build.yml` (beta); `py32f071.yml` — the only workflow that fires here — has no pytest step. **The local run is the evidence.** Same disposition as Phase 126's `test_config_storage_design_vendored.py`.

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_flash_path_record_sync.py -v`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite green **plus** the D-13 byte-identity sequence re-run on the final tree, both recorded in `129-NONREGRESSION.md`
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

Task IDs assigned 2026-08-02. All node ids below live in
`firestarter/tests/test_flash_path_record_sync.py`. `TestFlashPathRecordSyncFailsClosed` is
abbreviated `FC` and `TestFlashPathRecordSync` is abbreviated `LV`.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 129-01/T2 | 129-01 | 1 | D-03 | T-129-06 | Presence keyed on an unrenameable `.git` marker; the absent-claim names the resolved marker path | unit | `python -c` import assertions + `pytest tests/ -q` at `190 passed` | ❌ W1 creates | ⬜ pending |
| 129-01/T3 | 129-01 | 1 | D-03 | T-129-02 | A parse returning empty raises, naming `vacuously true`; it never compares equal to another empty parse | unit | `pytest tests/test_flash_path_record_sync.py::FC::test_empty_extraction_is_not_a_vacuous_pass -x` | ❌ W1 creates | ⬜ pending |
| 129-01/T3 | 129-01 | 1 | D-03 | T-129-02 | Planted divergence between two synthetic copies is detected (F-14 mode 1) | unit | `…::FC::test_planted_divergence_in_synthetic_copies_is_detected -x` | ❌ W1 creates | ⬜ pending |
| 129-01/T3 | 129-01 | 1 | D-03 | T-129-06 | Absent meta root skips **auditably** (reason names the resolved marker); present root + missing target **raises**, never skips (F-14 mode 3, both halves) | unit, subprocess | `…::FC::test_absent_meta_root_skip_is_auditable_not_silent -x`, `…::FC::test_present_root_with_missing_target_raises_not_skips -x`, `…::FC::test_absent_meta_claim_can_never_be_false -x` | ❌ W1 creates | ⬜ pending |
| 129-01/T3 | 129-01 | 1 | D-03 | T-129-02 | A renamed marker is a refusal, and a duplicated marker refuses to guess (F-14 mode 4) | unit | `…::FC::test_renamed_marker_yields_a_refusal_not_a_guess -x`, `…::FC::test_duplicate_marker_refuses_to_guess -x` | ❌ W1 creates | ⬜ pending |
| 129-01/T3 | 129-01 | 1 | D-03 | T-129-06 | A dirty sibling tree is detected, and `git` is required rather than optional (F-14 mode 5) | unit | `…::FC::test_dirty_tree_is_detected -x`, `…::FC::test_git_binary_is_required_not_optional -x` | ❌ W1 creates | ⬜ pending |
| 129-02/T2 | 129-02 | 2 | PCB-01…05 | T-129-02 | The 31 content and parity legs exist **before** either record, and their RED is `MissingScanTargetError` rather than a skip | RED ledger | `pytest …::LV -q` → `31 failed`; `grep -c MissingScanTargetError` ≥ 20 | ❌ W2 creates | ⬜ pending |
| 129-03/T3 | 129-03 | 3 | PCB-01 | T-129-03 | Both copies name all three tiers and carry the non-retirement sentence verbatim | content gate | `…::LV::test_three_tiers_and_non_retirement[meta] -x`, `…[fw] -x` (fw discharged W6) | ❌ W2 creates | ⬜ pending |
| 129-04/T1 | 129-04 | 4 | PCB-02 | T-129-05 | Every checklist row is `- [ ]` + `*Why:*` + `*Breaks if omitted:*` (D-16); R1…R7 present incl. F-10's package row; `### Deliberately undecided` names socket/ZIF/connector/power budget | structural gate | `…::LV::test_pcb_checklist_rows_are_wellformed[meta] -x`, `…[fw] -x` (fw discharged W6) | ❌ W2 creates | ⬜ pending |
| 129-04/T2 | 129-04 | 4 | PCB-03 | — | The record contains the literal reserved addresses and symbols read from the linker script | content gate | `…::LV::test_flash_budget_cites_reserved_map[meta] -x`, `…[fw] -x` | ❌ W2 creates | ⬜ pending |
| 129-04/T2 | 129-04 | 4 | PCB-03 | T-129-09 | The bootloader figure never appears without a cost token within two lines either side, and at least one occurrence exists (D-10) | proximity gate | `…::LV::test_bootloader_figure_carries_its_cost[meta] -x`, `…[fw] -x` | ❌ W2 creates | ⬜ pending |
| 129-05/T1 | 129-05 | 5 | PCB-04 | T-129-01 | The record names `0x1209`, the interim `1209:0001`, the verbatim ship gate, and `0x36B7`'s Puya provenance with its SDK path and pinned SHA | content gate | `…::LV::test_vid_pid_decision_and_ship_gate[meta] -x`, `…[fw] -x` | ❌ W2 creates | ⬜ pending |
| 129-05/T2 | 129-05 | 5 | PCB-05 | — | The socket instruction is present verbatim in both records **and** in `platform/py32f071/README.md`, with the provisional-map direction hazard stated | content gate | `…::LV::test_socket_empty_instruction_present` (3 legs: meta, fw, readme) | ❌ W2 creates | ⬜ pending |
| 129-05/T4 | 129-05 | 5 | PCB-01…05 | T-129-03 | Every durable artifact carries the required silicon caveat and zero forbidden-phrase matches near a py32 token | claim gate | `python3 .planning/phases/123-…/check_permitted_claims.py <explicit paths>` → exit 0, `PASS:` | ✅ exists | ⬜ pending |
| 129-06/T1 | 129-06 | 6 | PCB-01…05 | T-129-06 | The five shared bodies are byte-identical between the two copies, each proven non-vacuous per copy per key first | parity gate | `…::LV::test_shared_sections_match` (5), `…::LV::test_fw_extract_is_non_vacuous` (5) | ❌ W2 creates | ⬜ pending |
| 129-06/T3 | 129-06 | 6 | PCB-01…05 | T-129-06 | A planted mutation of the **real** subset is detected, the real blob SHA is unchanged, and the tree is clean afterwards | planted RED | `…::LV::test_planted_mutation_of_the_real_subset_is_detected -x` | ❌ W2 creates | ⬜ pending |
| 129-07/T2 | 129-07 | 7 | PCB-03 | T-129-12 | The linker comment names both record layers and no longer carries the clause C-1 corrected; the region line, symbols and both guards are byte-unchanged | cross-file gate | `…::LV::test_linker_comment_cross_references_record -x`; diff-scoped negative greps | ❌ W2 creates | ⬜ pending |
| 129-07/T3 | 129-07 | 7 | PCB-03 | T-129-13 | The comment-only edit changes no emitted byte, with the relink confirmed from the build log (D-13) | build delta | `sha256sum` before/after pair + `diff before.txt after.txt` empty + `Linking` log line | ✅ proven in C-3 | ⬜ pending |
| 129-08/T1 | 129-08 | 8 | PCB-01 | T-129-14 | The seed's frontmatter keeps its four-field schema, its `status` value changed, and its body links the record and names FUT-N05 (D-17/D-18) | content gate | `…::LV::test_seed_status_is_no_longer_dormant -x` | ❌ W2 creates | ⬜ pending |
| 129-09/T1 | 129-09 | 9 | PCB-01…05 | T-129-16 | Every row re-executed in the closing session; the full suite green at `221 passed`, the gate module at `41 passed`, zero skipped | full sweep | `pytest tests/ -q -rs`, `pytest tests/test_flash_path_record_sync.py -v` | ❌ W2 creates | ⬜ pending |
| 129-09/T2 | 129-09 | 9 | PCB-01…05 | T-129-17 | `129-NONREGRESSION.md` passes the claim gate when scanned **directly**, without quoting its own forbidden phrases (the Phase 125 self-reference trap) | claim gate | `check_permitted_claims.py` with all three artifacts on argv → exit 0 | ✅ exists | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/tests/test_flash_path_record_sync.py` — the D-03 sync gate, covering PCB-01…PCB-05 content assertions and the five F-14 fail-open modes
- [ ] `firestarter/tests/meta_presence.py` — meta-repo presence helper mirroring `firestarter_app/tests/fw_presence.py` (unrenameable marker, `FIRESTARTER_META_ROOT` seam, `MissingScanTargetError`)
- [ ] Toolchain install for D-13's evidence, if executors run in a fresh container:
      `sudo apt-get install -y --no-install-recommends gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib && pip install cmake ninja`
- [ ] No framework install needed — pytest is already used by 21 modules

---

## Manual-Only Verifications

No gate can judge these. They belong in UAT; Phase 130's CLOSE-02 honesty ledger consumes them.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The rationale lines are useful to a schematic author | PCB-02 | Usefulness is a judgement, not a string match | Read the checklist as if starting a schematic; can each row be acted on without further research? |
| The rejected-route table is fair | PCB-01 | Fairness of a comparison is not machine-checkable | Check each rejected route states a real cost, not a strawman |
| The record's stated edges are the *right* edges | PCB-02 | Requires domain judgement about what was omitted | Confirm connector choice, socket/ZIF and power budget are named as undecided rather than silently absent |
| The corrected C-1 framing reads as an honest correction, not a retcon | PCB-03 | Tone and provenance judgement | Confirm the record says what was previously believed, what is true, and how it was established |
| Any behavioural claim about PY32F071 silicon | all | **No board exists** — the milestone ceiling | Every such claim must carry `[UNVERIFIED-UNTIL-SILICON]` |

---

## Security Domain

`security_enforcement` is not disabled in `.planning/config.json`. The phase adds no runtime code, no network surface, no parser, and no data path.

| Pattern | STRIDE | Mitigation |
|---|---|---|
| Shipping another company's USB vendor identity (`0x36B7` = Puya) | Spoofing | C-2 + D-09's ship gate; `1209:0001` as the interim identity |
| USB PID collision with every unmodified Puya CDC example | Spoofing / DoS | Same |
| A gate that passes without observing anything | Tampering (undetected) | Planted-violation fixture + per-parse non-vacuity (F-14) |
| An agent performing an outward-facing publish action | Elevation of Privilege | **Structural** separation — no `git push`, no `gh workflow run`, no PR filing. Not a checkpoint: `--auto`/`--chain` auto-approve checkpoints. |
| A future reader trusting a false silicon claim in a durable record | Repudiation / Information Disclosure | Per-claim tags + `[UNVERIFIED-UNTIL-SILICON]` + a `## Claim ceiling` section |
| Bricking a board via option bytes with no SWD | DoS (physical) | PCB-02's SWD-pads row, justified by Open Question 1 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify — every task in all nine plans carries one; verified by `gsd-tools query verify.plan-structure` on each plan (9/9 valid, 0 errors, 0 warnings)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — 28 of 28 tasks have one
- [x] Wave 0 covers all MISSING references — the two MISSING artifacts (`tests/meta_presence.py`, `tests/test_flash_path_record_sync.py`) are both created in Wave 1 by plan `129-01`; the toolchain install is a Wave 7 preflight step inside `129-07` Task 1, and is idempotent
- [x] No watch-mode flags — every command is a single-shot `pytest`, `grep`, `cmake --build` or `sha256sum`
- [x] Feedback latency < 30s — quick module run ~5 s, full suite ~6 s measured at plan time (180 passed in 5.99 s); the only slow step is the Wave 7 ARM build, which is evidence rather than sampling
- [x] `nyquist_compliant: true` set in frontmatter

**Deliberate deviation from the Wave 0 convention.** The gate module is authored across **two**
waves rather than one: `129-01` lands the machinery and the ten fail-closed fixtures GREEN, and
`129-02` lands the 31 content and parity legs **RED**, before either record exists. The RED window
spans waves 2 through 8 and is discharged one documented group per wave, with each plan's
`<automated>` verify scoped to the node ids it turns green plus an exact expected total. This is
Phase 123's doctrine applied literally — a gate authored after the content it judges can only bless
what already happened — and it is why the phase is serial.

**Expected suite totals per wave** (deterministic because the phase is serial; a departure from any
of these is an unexpected regression, not a rounding error):

| After wave | `pytest tests/ -q` |
|---|---|
| baseline (pre-phase) | `180 passed` |
| 1 | `190 passed` |
| 2 | `31 failed, 190 passed` |
| 3 | `29 failed, 192 passed` |
| 4 | `24 failed, 197 passed` |
| 5 | `20 failed, 201 passed` |
| 6 | `2 failed, 219 passed` |
| 7 | `1 failed, 220 passed` |
| 8 | `221 passed` |
| 9 | `221 passed` |

**Approval:** planner-approved 2026-08-02; execution pending.
