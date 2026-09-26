---
phase: 162
slug: 162-chip-11-part-dev-test-sweep-on-the-reference-rig
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-27
---

# Phase 162 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `162-RESEARCH.md` §"Validation Architecture". This is a meta-repo bench phase —
> there is no `pytest` suite. The rig's own gate suite is the equivalent, and it is fail-closed
> (discovery globs every `*.py` under `tools/` and exits 1 if one lacks `--selftest`).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `run_gates.sh` + per-tool `--selftest` (stdlib `python3`, no third-party runner) |
| **Config file** | `.planning/v1.34/tools/run_gates.sh` — discovery is `find -maxdepth 1 -name '*.py'`; no separate config |
| **Quick run command** | `bash .planning/v1.34/tools/run_gates.sh --quick` |
| **Full suite command** | `bash .planning/v1.34/tools/run_gates.sh` |
| **Estimated runtime** | ~10–30 seconds (desk gates); live-arm gates add the board round-trip |
| **Exit-code rule** | Taken **directly**, never through a pipe — `bash …/run_gates.sh; RC=$?` |
| **Measured baseline (pre-phase)** | `tool self-tests run: 12 / 12`; `render_steps.py` diff empty, control=11 / v133=11 lines; `ALL GATES PASSED` |
| **Target after this phase** | `tool self-tests run: 14 / 14`; **7** live gates (5 today + 2 new); `render_steps` still 11 lines per arm |

---

## Sampling Rate

- **After every task commit:** `bash .planning/v1.34/tools/run_gates.sh --quick` (exit code direct)
- **After every position** — tighter than a wave, because a chip position is a physical event that
  cannot be replayed: the appender's own refusals run *before* the row is written, and
  `render_chip_evidence.py --check` runs immediately *after* the append (the Amendment-3
  append-then-re-render pair, applied to the sibling file)
- **After every plan wave** — a wave is a pot/JP4 group: full `bash .planning/v1.34/tools/run_gates.sh`,
  plus the frozen-config-dir pristine assertion, plus `gate_record.py --jsonl …/CHIP-EVIDENCE.jsonl`
- **Before `/gsd-verify-work`:** full suite green at `14 / 14`, 7 live gates, both counting rules
  evaluating true, and `EVIDENCE.jsonl`'s `position_count_expected: 20` / row state unchanged from
  the pre-phase snapshot
- **Max feedback latency:** ~30 s for desk gates; one position (~6–12 min) for bench-coupled legs

---

## Per-Task Verification Map

Task IDs are assigned by the planner. This table is the requirement-level contract the planner must
map every task onto — no task may claim a requirement that is not represented here.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 0 | CHIP-01 | — | N/A | integration | `python3 .planning/v1.34/tools/render_chip_evidence.py --jsonl .planning/v1.34/bench/CHIP-EVIDENCE.jsonl --target .planning/v1.34/bench/CHIP-EVIDENCE.md --check` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | CHIP-01 | — | N/A | unit | the `derive_plan` probe (RESEARCH R5), run and committed as a one-shot record | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | CHIP-02 | — | N/A | unit | appender `--selftest` leg 8 — no row carries a null `fw_board_identity` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | CHIP-02 | — | N/A | integration | `python3 -c "import json;rows=[json.loads(l) for l in open('.planning/v1.34/bench/CHIP-EVIDENCE.jsonl')][1:];assert all(r['fw_board_identity'] for r in rows if not r.get('named_absence'))"` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | CHIP-03 | — | N/A | unit | appender `--selftest` leg 11 — `divergence_verdict` is exactly `same` or `diverges: <non-empty>` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | CHIP-03 | — | N/A | integration | `gate_record.py --jsonl .planning/v1.34/bench/CHIP-EVIDENCE.jsonl --pins …` (field presence) + a domain script over `divergence_verdict` / `prior_disposition_source` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | CHIP-04 | — | N/A | integration | the `chip_sc04_rule` counting script (RESEARCH R4) — control re-run for every `diverges`, none for any `same` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | CHIP-05 | — | N/A | integration | script asserting `known_carried != "no"` and `prior_disposition` non-empty for `w27e512`, `w27e040`, `w29c040`, `am27c020`, `fm1608` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | *(rig)* | — | Frozen config dir pristine before and after every run | unit + per-wave | the SHA round-trip leg (RESEARCH R3) | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | *(rig)* | — | `EVIDENCE.jsonl` untouched — 20 expected, non-bring-up row count unchanged | integration | the WRV assertion script (RESEARCH R4) against the pre-phase snapshot | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | *(rig)* | — | `## Step list` byte-unchanged; still renders 11 arm-identical lines | integration | the two legs in RESEARCH R6 (`render_steps.py --arm control` vs `--arm v133` empty diff + `wc -l == 11`) | ⚠️ partly — diff leg exists in `run_gates.sh`; the line-count and git-section checks are new | ⬜ pending |
| TBD | TBD | 1..N | *(rig)* | — | Every recorded argv is free of forbidden flags and uses a pinned `argv0` | unit | `gate_record.check_commands`, delegated by the appender **before** the write | ✅ exists | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Wave 0 exists because the researcher found **four rig defects that falsify or block the sweep**
before any part is seated. It is not optional scaffolding.

- [ ] `.planning/v1.34/tools/append_chip_evidence.py` — with the 16 `--selftest` legs specified in
      RESEARCH R3; covers CHIP-01 / 02 / 03 / 05
- [ ] `.planning/v1.34/tools/render_chip_evidence.py` — with `--check`, deterministic, no timestamp;
      covers CHIP-01
- [ ] `.planning/v1.34/bench/CHIP-EVIDENCE.jsonl` line 1 `_schema` — the 9 `locked_columns`
      **byte-copied** from `EVIDENCE.jsonl` (Phase 166 CLOSE-01 asserts them uniformly), the
      chip-specific extension columns, and both counting rules; covers CHIP-01 / 04
- [ ] `.planning/v1.34/tools/run_gates.sh` — two new live gates
      (`render_chip_evidence --check`, `gate_record --jsonl CHIP-EVIDENCE.jsonl`), taking the suite
      to 14/14 selftests and 7 live gates
- [ ] `.planning/v1.34/rig-pins.json` — `chips` map extended to the eleven parts with `chip_token`;
      `_CHIP_CHOICES` in `capture_provenance.py` derived from it rather than hardcoded (+ a selftest
      leg). **Without this, `capture_provenance.py` exits 2 on nine of ten parts** (argparse
      `choices=["w27c512","w29c020"]`, before pins are even read)
- [ ] `.planning/v1.34/PROCEDURE.md` — Amendment 4: §Scope correction + header, the chip-sweep step
      list, `$CHIP` / `$CHIP_TOKEN` tokens, P-06 supersession, P-11 retarget, `~/.firestarter` mtime
      re-pin, and the config-dir copy-out obligation. **`## Step list` cannot host `C-NN` IDs** —
      `render_steps.py`'s `_STEP_ID_RE` is `^P-\d\d$` and `validate_steps()` raises, reddening the gate
- [ ] `render_steps.py` — optional second-section support if RESEARCH R6 option (A) is taken
      (+ 2 selftest legs)
- [ ] The desk-provable answers to R2 (three commands) and R5 (the `derive_plan` probe), run and
      **committed as records** before the first part is seated
- [ ] A pre-phase snapshot of `EVIDENCE.jsonl`'s row count + `position_count_expected`, to diff
      against at the phase gate
- [ ] The `~/.firestarter/config.json` mtime re-pin — it has **already drifted**
      (`1787817565` → `1787854674`, measured live), so P-11 assertion (1) is unconditionally red
      before the phase starts and would book a false `P-H1` at every position

---

## Manual-Only Verifications

Everything below needs the physical bench and cannot be proven at the desk. Per CONTEXT.md
`<specifics>`, `human-verify` checkpoints belong at the chip swap, the JP4 change and the pot
adjustment — **and nowhere else**. No artificial park prompts.

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Pre-flight `fw_board_identity` is non-null before any part runs | CHIP-02 | Needs the board; a null is a `P-H1` halt and an opened defect, not a carried gap | One `read_programmer_identity` probe as a bring-up datum, **outside** the numbered step list, ~10 s (CONTEXT.md Claude's Discretion) |
| Each part is correctly seated and the socket makes contact | CHIP-01 | Chip handling is operator-only | Operator seats the part; one clean re-seat permitted per position with **both** attempts recorded (standing bench rule 8) |
| JP4 is on the correct 28-pin / 32-pin position | CHIP-01 | Physical jumper | Operator moves JP4 — twice in the sweep (into DIP32 at part 5, back to DIP28 at part 10); recorded per position |
| VPP pot is at the group target and the meter reading is taken | CHIP-01 | Operator adjusts the pot and reads the meter **solo**; no live monitor loops | State the target, wait, take **ONE** read. Two pot events: the 12 V group, then the 13 V pair. A blank or `0x303` firmware reading is a **contact fault**, not a voltage — that is `P-H1` |
| Firmware VPP reading per part is in band | CHIP-01 | Needs the seated part and a live arm | One firmware VPP read per part at its own seating; record `vpp_target_mv`, `vpp_real_mv`, `vpp_firmware_mv`, `vpp_shortfall_mv`. In band = the `+500 mV` guard does not fire, never an exact match |
| Each flash lands the intended arm | CHIP-04 | D-17's interleaved re-flashes; the arm is confirmed by on-device read-back, never assumed | Every re-flash carries its own `P-04` read-back proof (`judge_readback.py`, avrdude `-A` explicit) against `hex_span_expected_by_arm` — Leonardo control 28170 / v133 25098 |
| Nothing was filed to `henols/firestarter_prom` (CLOSE-04) | *(rig)* | The criterion explicitly refuses assertions | Capture an issue-count **before/after** as pasted command output, not a code citation (CONTEXT.md D-10) |
| The 2516's absence is a hardware fact | CHIP-01 | Operator declaration, 2026-08-27 | Recorded as a named absence: unsupported on Rev 2.0, "only 2.2 and above is supporting and there must be more work done before we can test it." **Not seated, not read, not written** |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Every `<automated>` leg was **read before being trusted** — Phase 160's hardcoded
      arm-agnostic-constant defect recurred four times; here one wrong constant is ten false results
- [ ] No literal `&amp;&amp;` in any `<automated>` block (recorded planner defect: 30/37 legs unrunnable)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all ❌ MISSING references above
- [ ] No watch-mode flags; no live monitor loops on the pot
- [ ] No `--auto` / `--chain` / any auto-advance mode — those auto-approve the `human-verify`
      checkpoints every physical step depends on, and `autonomous: false` is **not** self-protecting
- [ ] Feedback latency < 30 s for desk gates
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
