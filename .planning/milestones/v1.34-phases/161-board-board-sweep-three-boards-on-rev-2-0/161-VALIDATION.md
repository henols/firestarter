---
phase: 161
slug: board-board-sweep-three-boards-on-rev-2-0
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-27
---

# Phase 161 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `161-RESEARCH.md` § Validation Architecture (line 1230).

This is a **hardware evidence phase**, not a software-feature phase. It ships no product code —
both submodules stay byte-unchanged. There is no unit-test framework in the ordinary sense: the
"tests" are the rig's own gates plus the 12 evidence positions.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `bash .planning/v1.34/tools/run_gates.sh` — 11 Python `--selftest` suites + 5 live gates |
| **Config file** | `.planning/v1.34/rig-pins.json` (constants) + `bench/EVIDENCE.jsonl` line 1 (`_schema`) |
| **Quick run command** | `bash .planning/v1.34/tools/run_gates.sh --quick` (skips `check_rebuild` / `check_arms` only) |
| **Full suite command** | `bash .planning/v1.34/tools/run_gates.sh` |
| **Estimated runtime** | quick ~seconds; full suite ~1 min (dominated by the two rebuild/arm gates) |

**Exit-code discipline (binding):** measure `run_gates.sh`'s exit code **directly, never through a
pipe**. Baseline measured green during research: 11/11 selftests, 5/5 live gates, `EXIT=0`.

**Wave 0 will add a 12th tool** (`append_evidence.py`, D-05). `run_gates.sh` discovers every `*.py`
under `tools/` and **fails the suite** if one does not advertise `--selftest` — so the new tool's
selftest is not optional, and the suite becomes 12/12 the moment the file lands.

---

## Sampling Rate

- **Per position** (12x): `judge_wrv.py` (the oracle) → `append_evidence.py` → `render_evidence.py`.
  Records are written as each position completes (D-03), so a kill mid-cell leaves a consistent,
  resumable state.
- **Per cell / per wave** (3x — D-01 makes a wave equal a cell, D-04 designates the gate):
  full `bash .planning/v1.34/tools/run_gates.sh`, exit code measured directly.
- **Before `/gsd-verify-work`:** full suite green **and** all 12 rows present in `EVIDENCE.jsonl`.
- **Max feedback latency:** one position (~5–20 min, chip-dependent). This is bench-bound, not
  compute-bound; the ceiling is set by D-08's stall kill, not by the gate.

---

## Per-Task Verification Map

Populated 2026-08-27 from the five `*-PLAN.md` files. **52 tasks total: 30 `auto` and 22
`checkpoint:human-verify`.** Every `auto` task carries at least one `<automated>` leg; every
checkpoint task is an operator-physical step at `P-01` / `P-03` / `P-05` / `P-06` / `P-08` or a
`P-10`/`P-11` repeat, and by design carries a `<resume-signal>` rather than an automated leg.

| Plan | Task | Type | Automated verification |
|------|------|------|------------------------|
| 161-01 | 1 `append_evidence.py` | auto | `append_evidence.py --selftest` exit 0; bad-usage exit 2; AST + sibling-import structure check |
| 161-01 | 2 Amendment 3 | auto | `render_steps.py` control-vs-v133 byte-identical at 11 steps; amendment content token check |
| 161-01 | 3 gate re-confirm | auto | `run_gates.sh` exit 0 read from `$?`, 12 selftest passes, tool discovered; `ls tools/*.py` = 12; both sub-repo porcelains empty |
| 161-02 | 1 `P-01` uno328pb mount | checkpoint | operator-physical (node + bare-board confirmation) |
| 161-02 | 2 D-10 pre-proof | auto | `judged_match` true + `judged_span_bytes` == runtime `hex_span_expected_by_arm.v133` + 2 exclusions; probe identity; 32768 B read-back; porcelains |
| 161-02 | 3 `P-01` Leonardo mount | checkpoint | operator-physical (node + declared shield) |
| 161-02 | 4 Leonardo pre-proof | auto | provenance `captured_at_step==2` **or** a declared partial proof; no `--wait-new-port` in the touch record; `run_gates.sh` exit 0 |
| 161-02 | 5 record + handover | auto | `EVIDENCE.jsonl` unchanged; `~/.firestarter` tree sha == baseline; PREPROOF content check |
| 161-03 | 1 `P-01` mount + chip OUT | checkpoint | operator-physical (Pitfall 1) |
| 161-03 | 2 `P-02` identity + 4x provenance | auto | probe `connected_part` == `targets.uno.mcu`; 4 records with `captured_at_step==2` and image fields == `IMAGE-PLAN.json` |
| 161-03 | 3 `P-04` control flash | auto | `judged_match` + span == runtime `…by_arm.control` **and** != the legacy scalar; HEAD == `arms.control.fw_sha`, porcelain empty |
| 161-03 | 4 `P-05`+`P-06` | checkpoint | operator-physical (seat + pot) |
| 161-03 | 5 `P-07` pos 1 | auto | image size + sha == plan row; verdict `read_count` == file count, `size_violations` empty; row present with non-null duration; `render_evidence --check` |
| 161-03 | 6 `P-08` | checkpoint | operator-physical (chip swap) |
| 161-03 | 7 D-09 smoke + `P-09` pos 2 | auto | 262144 B image sha; `expect_size` 262144; smoke record content; row duration shape; `--check` |
| 161-03 | 8 `P-10`→`P-03` | checkpoint | operator-physical (chip out) |
| 161-03 | 9 `P-04` v133 + preservation | auto | six preserved artifacts; span == runtime `…by_arm.v133`; the two arms' judged SHAs differ; control provenance not overwritten |
| 161-03 | 10 `P-05` | checkpoint | operator-physical |
| 161-03 | 11 `P-07` pos 3 | auto | 3 `run_*.bin`, `read_count==3`, 3 `read_shas`; mask differs from pos 1; `--check` |
| 161-03 | 12 `P-08` | checkpoint | operator-physical |
| 161-03 | 13 `P-09` pos 4 | auto | 3 x 262144 B reads; empty `size_violations`; mask differs from pos 2; `--check` |
| 161-03 | 14 `P-11` chip out | checkpoint | operator-physical (Pitfall 1) |
| 161-03 | 15 `P-11` teardown | auto | 4 A1 rows, one per `position_id`, outcome in domain, duration non-null; `~/.firestarter` baseline; arms distinguishable; identity stable; `gate_record --jsonl`; `run_gates.sh` exit 0; porcelains |
| 161-04 | 1 `P-01` shield move | checkpoint | operator-physical |
| 161-04 | 2 `P-02` | auto | probe `atmega328pb` / `0x1e9516`; 4 records cross-checked against masks 20–23 |
| 161-04 | 3 `P-04` control | auto | `judged_match` + span 26074 via runtime lookup + 2 vector exclusions; **no** raw-span SHA comparison |
| 161-04 | 4 `P-05`+`P-06` | checkpoint | operator-physical |
| 161-04 | 5 `P-07` pos 5 | auto | image sha; `incomplete-read-set` when the read set is empty; row duration shapes; substantive verdict prose; `--check` |
| 161-04 | 6 `P-08` + safety judgement | checkpoint | operator-physical (D-07 carve-out) |
| 161-04 | 7 `P-09` pos 6 | auto | 262144 B image sha, mask 21/stamp 32; verdict fields; `--check` |
| 161-04 | 8 `P-10`→`P-03` | checkpoint | operator-physical |
| 161-04 | 9 `P-04` v133 | auto | span 23000 via runtime lookup; two arms' spans differ; provenance patched per arm |
| 161-04 | 10 `P-05` | checkpoint | operator-physical |
| 161-04 | 11 `P-07` pos 7 | auto | mask 22 differs from 20; `read_count` == file count; `--check` |
| 161-04 | 12 `P-08` + safety judgement | checkpoint | operator-physical |
| 161-04 | 13 `P-09` pos 8 | auto | mask 23 differs from 21; `expect_size` 262144; `--check` |
| 161-04 | 14 `P-11` chip out | checkpoint | operator-physical |
| 161-04 | 15 `P-11` teardown | auto | 4 A2 rows complete; spans 26074/23000; `CELL.md` content; `~/.firestarter`; `gate_record`; `run_gates.sh` exit 0; porcelains |
| 161-05 | 1 `P-01` shield move | checkpoint | operator-physical |
| 161-05 | 2 `P-02` via the 161-02 sequence | auto | probe `atmega32u4` / `0x1e9587`; `cell_id` with slash, `cell_slug`/`position_id` with the dash; masks 24–27; no `--wait-new-port` |
| 161-05 | 3 `P-04` control | auto | span 28170 via runtime lookup and != the legacy scalar; 32768 B read-back |
| 161-05 | 4 `P-05`+`P-06` | checkpoint | operator-physical |
| 161-05 | 5 `P-07` pos 9 | auto | image sha mask 24; verdict fields; row `cell_id == "A3/B2"`; `--check` |
| 161-05 | 6 `P-08` | checkpoint | operator-physical |
| 161-05 | 7 `P-09` pos 10 | auto | mask 25/stamp 32; verdict fields; `--check` |
| 161-05 | 8 `P-10`→`P-04` v133 (chip seated) | auto | six preserved artifacts; spans 28170 vs 25098 differ; provenance patched per arm |
| 161-05 | 9 `P-05` swap back | checkpoint | operator-physical |
| 161-05 | 10 `P-07` pos 11 + BOARD-04 comparison | auto | 3 reads; mask 26 differs from 24; comparison paragraph token check (`0.37`, `106.06`, `spread`, `PR #55`, `both`); `--check` |
| 161-05 | 11 `P-08` | checkpoint | operator-physical |
| 161-05 | 12 `P-09` pos 12 | auto | 3 x 262144 B reads; mask 27 differs from 25; `--check` |
| 161-05 | 13 `P-11` D-11 leave-state swap | checkpoint | operator-physical |
| 161-05 | 14 `P-11` teardown + reconciliation | auto | **12 sweep rows, 4 per cell, no duplicate `position_id` anywhere**; A3/B2 exactly one per (arm x chip); spans 28170/25098; `CELL.md` tokens; `~/.firestarter`; `gate_record`; `run_gates.sh` exit 0; porcelains |

Sampling continuity: the longest run without an automated leg is two consecutive checkpoint
tasks, which never occurs — every checkpoint is followed immediately by an `auto` task whose
first verify leg covers the physical action's consequences.

The requirement-level map below is the contract those rows satisfy.

| Req | Behaviour that must be TRUE | Type | Automated command | Infra exists? | Status |
|-----|-----------------------------|------|-------------------|---------------|--------|
| BOARD-01 | A1's 4 positions each hold a verdict or a **named** absence | evidence | `gate_record.py --jsonl bench/EVIDENCE.jsonl` + row-count assertion over `cell_id == "A1"` | ✅ (row filter is new, trivial) | ⬜ pending |
| BOARD-02 | A2's 4 positions; the failure **observed** on both arms, not asserted from Backlog 999.2 | evidence + human | same, plus each A2 row's `verdict` naming the observed stop point and exact host output | ✅ / prose is human by D-05 | ⬜ pending |
| BOARD-03 | A3/B2's 4 positions | evidence | same, filtered on `cell_id == "A3/B2"` | ✅ | ⬜ pending |
| BOARD-04 | A measured write duration on every position | evidence | assert `write_duration_wallclock_s` non-null on all 12 rows (a real float **or** the `"not measured — <reason>"` shape) | ✅ via `gate_record.py` field presence | ⬜ pending |
| SC#2 | Provenance captured **before** the cell's first test step; arm confirmed by on-device read-back | mechanism | `captured_at_step == 2` on all 12 `provenance_*.json`; `READBACK-VERDICT.judged_match == true` per flash | ✅ | ⬜ pending |
| SC#5 | A3/B2 executed exactly once in the milestone | arithmetic | exactly 4 rows with `cell_id == "A3/B2"`, one per (arm x chip); `render_evidence.append_row_to_file` structurally refuses a duplicate `position_id` | ✅ | ⬜ pending |
| D-05 | Zero machine-readable fields transcribed by hand | mechanism | `append_evidence.py --selftest` — negative legs must **refuse** a field taken from the wrong position's provenance | ❌ **Wave 0** | ⬜ pending |
| Amendment 3 | The procedure stays arm-agnostic after the edit | gate | `render_steps.py --arm control` vs `--arm v133` diff empty (3rd live leg of `run_gates.sh`) | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] *(planned — 161-01 Task 1)* `.planning/v1.34/tools/append_evidence.py` — the tool itself (D-05). Derives every
      machine-readable field from `provenance_<position>.json`, `WRV-VERDICT.json` and
      `READBACK-VERDICT.json`; only 5 of the 40 schema columns are human-supplied.
- [x] *(planned — 161-01 Task 1 `<behavior>`, 10 named negative legs)* Its `--selftest`, with **named negative legs**, not just a happy path:
      missing `WRV-VERDICT.json`; `position_id` disagreeing across the three artifacts;
      `image_sha` != `written_sha`; a bare `not measured` in `blank_state`; an empty `verdict`;
      `outcome` derived as `validated` while `sha_verdict_judged != "match"`.
- [x] *(planned — 161-01 Task 2, four clauses)* `PROCEDURE.md` **Amendment 3** (research recommends four clauses: D-06 per-position append,
      D-12 leave-state, per-position artifact paths, `~/.firestarter` baseline restatement) plus a
      `run_gates.sh` re-confirmation that the `render_steps` arm diff stays empty.
- [x] **Not needed** — planner decision PD-1 (`161-01-PLAN.md`) keeps `written.bin` and
      `run_NN.bin` under `cells/<slug>/reads/<position_id>/`, which `git check-ignore` measured as
      already ignored by `cells/*/reads/`. RESEARCH's `positions/<id>/` proposal was rejected
      because PATTERNS measured it as **not** ignored. No `bench/.gitignore` edit is required.

---

## Manual-Only Verifications

The operator-physical steps. Per CONTEXT D-02 — *"I dont want any handover until a real physical
action is needed"* — `human-verify` checkpoints belong at these steps and **nowhere else**.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Shield mounted on the correct board; silkscreen revision declared | SC#2 | `hw_revision` cannot distinguish Rev 2.2 / Rev 2.0 / modified Rev 0 — the operator reads the silkscreen | `P-01`; `capture_provenance.py` refuses to run without an operator-declared shield revision |
| Chip OUT before an Uno-class sideload / signature probe | safety | Physical socket action; Uno-class chip-out rule (Leonardo exempt) | `P-03` — and, per research Pitfall 6, also **before `P-02`** on A1/A2, because `probe_board.py` is an avrdude signature probe |
| Chip 1 seated (W27C512, DIP28) | BOARD-01…03 | Physical socket action, pin-1 orientation | `P-05` |
| VPP pot set to 12.0 V | BOARD-01…03 | Operator adjusts the pot solo — state the target, wait, take ONE read | `P-06` (single confirming `vpp` read; never a monitor loop) |
| Chip 2 swapped in (W29C020, DIP32) | BOARD-01…03 | Physical socket action, different package width | `P-08` |
| The above repeated across the arm switch | SC#1 | Same physical actions, second arm | `P-10` |
| A2's observed failure symptom — where the program stops, what the host printed | BOARD-02 / SC#3 | Prose observation; D-05 leaves `verdict` and `anomalies` human by design | Recorded into the position's row as the human fields |

---

## Claims This Phase CANNOT Validate — record as non-claims

1. **Any electrical claim.** Program-window VPP/VCC *under load* stays unmeasured (DTR-reset-on-close
   tooling gap). v1.34 makes no electrical claim.
2. **8 bytes on uno328pb.** Under `vector-exclusion`, `[0,4)` and `[100,104)` — 8 of 26074 judged
   bytes — are excluded from every comparison. A fault confined to those 8 bytes is invisible on A2.
   *(Disclosed §6 limit — carry it, do not re-raise it.)*
3. **A duration-to-spread comparison against v1.31.** v1.31's 0.37 s is a *spread* (max−min across
   three app-reported figures), not a duration. Also: v1.34's ~3x faster W27C512 figures are PR #55's
   VPE-settle amortisation, present in **both** arms — not a v1.33 effect.
4. **Python 3.11.** Both arms run devcontainer 3.12.14, not the app-CI floor. *(Disclosed §6.)*
5. **Stable-channel reachability.** `dev consistency-check` is in `BETA_ONLY_DEV_COMMANDS`; the
   judged SHA is unaffected, but the read-set command is a dev-channel-only surface. *(Disclosed §6.)*
6. **Byte-level re-check of a clean position.** A clean-match read set is re-checkable by SHA only —
   the bytes stay local unless the position failed, in which case they are committed with `git add -f`.
7. **Cause.** This phase *records*. Phase 165 classifies and fixes, on the v1.33 PR branch.

---

## Validation Sign-Off

- [x] All 30 `auto` tasks have `<automated>` verify legs; the 22 checkpoints are operator-physical by D-02
- [x] Every `<automated>` leg's constants are **arm-aware** — `hex_span_expected_by_arm`, never the
      legacy scalar `hex_span_expected` (Phase 160 recorded this defect recurring 4x; 12 positions
      means one wrong constant is twelve false results)
- [x] Sampling continuity: no 2 consecutive tasks without an automated verify
- [x] Wave 0 covers all MISSING references — plan 161-01, wave 1, ahead of every cell
- [x] No watch-mode flags; every `run_gates.sh` leg captures `$?` directly, never through a pipe
- [x] `human-verify` appears at P-01 / P-03 / P-05 / P-06 / P-08, their P-10 repeats, and the two P-11 operator actions the decisions themselves require (the Uno-class teardown chip-out, and D-11's swap-back on A3/B2) — nowhere else
- [x] This phase must **not** run under `--auto` / `--chain` / any auto-advance mode (Standing bench
      rule 7): those auto-approve the very checkpoints every physical step depends on, and
      `autonomous: false` on a plan is not self-protecting against that
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** planner-complete 2026-08-27 (5 plans, 52 tasks); operator approval pending
