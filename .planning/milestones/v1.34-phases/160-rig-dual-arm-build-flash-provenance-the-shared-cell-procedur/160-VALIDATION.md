---
phase: 160
slug: rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-26
validated: 2026-08-27
---

# Phase 160 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `160-RESEARCH.md` § "Validation Architecture". Every figure below was
> measured in the devcontainer during research unless the row says otherwise.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | **None.** The meta repo has no `pyproject.toml`, no `pytest.ini`, no `tests/`, and `pytest` is not importable from `python3`. Do not introduce one — this phase adds no package. |
| **Established convention** | Standalone `python3` gate scripts: `def main() -> int` + `raise SystemExit(main())`, asserted by **exit code**. Precedents: `.planning/v1.18/bench/check_{verdict,graduation,signature,pre01,diff07}.py`, `.planning/phases/145-bench-validation/tools/extract_frames.py`, `.planning/phases/145-bench-validation/images/gen_addr_image.py`. |
| **Config file** | none — each gate is invoked explicitly by path |
| **Quick run command** | `python3 .planning/v1.34/tools/<gate>.py [args] ; echo rc=$?` |
| **Full suite command** | `bash .planning/v1.34/tools/run_gates.sh` — runs every gate, fails on the first non-zero. **Does not exist yet; Wave 0 creates it.** |
| **Bin-level oracles** | `sha256sum` + `cmp` + `stat -c%s`, exactly as the `SHA256SUMS.txt` precedent does |
| **Estimated runtime** | Host-side gates: seconds. On-device legs: bounded by the bench, not by the suite — measure and record during bring-up. |

---

## Sampling Rate

- **Per task commit:** the gate(s) that task touches, exit code asserted.
- **Per wave merge:** `run_gates.sh` — every gate green.
- **Phase gate, before `/gsd-verify-work`:** `run_gates.sh` green **and** both falsification tests **observed**, not merely authored —
  - D-03: the deliberate wrong-arm cross-flash MISMATCH recorded on **all three** targets, plus the corrected match;
  - D-17: reconstruction of the bring-up run from the record alone, diffed against the prescription.
- **Max feedback latency:** host-side gates must stay under ~10 s each; no three consecutive implementation tasks may lack an automated check.
- **Gate birth rule (standing project discipline):** every gate above is observed **red** against a deliberately broken input — a truncated read-back, a null provenance field, a hand-edited `EVIDENCE.md`, an `outcome: inconclusive` — before it is trusted green. A gate written but never seen to fail proves nothing in this repo (`reference_gate_authored_before_content_can_be_unreachable`, and `check_permitted_claims.py` which scanned nothing and exited 0).

---

## Per-Task Verification Map

Filled at phase close (Plan 13, Task 2) — one row per task, all thirty-eight tasks across the
thirteen plans, in plan and task order, from the first plan's scaffold task to this plan's
sign-off gate. Threat Ref/Secure Behavior name the single most directly-mitigated threat from
that task's own plan's threat register where one applies clearly to that specific task; a task
whose plan-level register has no single-task binding is not present in this phase (every task
below has one). "Automated Command" reproduces the verbatim leading text of that task's first
`<automated>` verify leg (truncated with `...` where the full script is long — the complete,
exact text lives in the cited plan's own `<verify>` block); a checkpoint task's row instead
names its gate type and carries no borrowed command. "File Exists" and "Status" are `n/a` for
a manual gate (no dedicated artifact file of its own) and `✅`/`✅ green` for every completed
`auto` task; Task 3 of this plan (`160-13-03`) is the one exception — a `checkpoint:human-verify`
gate this plan reaches but does not sign off, so its Status is `⬜ pending`.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 160-01-01 | 01 | 1 | RIG-01, RIG-02 | T-160-04 | SHAs re-read live at exec time; mismatch stops the plan | integration | `python3 -c "import json,sys,os;p=json.load(open('.planning/v1.34/rig-pins.json'));req=['schema_version','milestone','phase','arms_root','firmware_repo...` | ✅ | ✅ green |
| 160-01-02 | 01 | 1 | RIG-01, RIG-02 | T-160-SC | blocking-human package-legitimacy gate before install | manual | `MANUAL GATE (checkpoint:human-verify, gate=blocking-human) -- no automated command` | n/a | ✅ green |
| 160-01-03 | 01 | 1 | RIG-01, RIG-02 | T-160-01 | arm named by absolute venv path + D-08 triple; dep-set diff empty | integration | `bash -c 'set -e; P=.planning/v1.34/rig-pins.json; C=$(python3 -c "import json;print(json.load(open(\"$P\"))[\"arms\"][\"control\"][\"worktree\"])"); V...` | ✅ | ✅ green |
| 160-02-01 | 02 | 2 | RIG-01 | T-160-13 | arm in filename + fw_sha in manifest; arms' images hash differently | integration | `bash -c 'set -e; cd /workspaces/.planning/v1.34/images; test "$(ls *.hex \| wc -l)" -eq 6; sha256sum -c SHA256SUMS.txt; python3 -c "import json;m=json....` | ✅ | ✅ green |
| 160-02-02 | 02 | 2 | RIG-01 | T-160-12 | check_rebuild.py exits non-zero on missing/empty images dir | unit | `python3 .planning/v1.34/tools/check_rebuild.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-02-03 | 02 | 2 | RIG-01 | T-160-10 | all six pairs measured; every divergence carries a measured cause | integration | `python3 -c "import json;r=json.load(open('.planning/v1.34/images/REBUILD-CHECK.json'));e=r['results'];assert len(e)==6,len(e);pairs={(x['arm'],x['env'...` | ✅ | ✅ green |
| 160-03-01 | 03 | 2 | RIG-02, RIG-04 | T-160-14 | distinct mask per position recorded in IMAGE-PLAN.json | unit | `python3 .planning/v1.34/tools/gen_addr_image.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-03-02 | 03 | 2 | RIG-02, RIG-04 | T-160-16 | check_arms.py re-verifies SHA/porcelain/file/deps/config-sha on demand | unit | `python3 .planning/v1.34/tools/check_arms.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-03-03 | 03 | 2 | RIG-02, RIG-04 | T-160-14 | 21 distinct positions, address-attributable, reproducible SHA | integration | `python3 -c " import json,subprocess,tempfile,os,re p=json.load(open('.planning/v1.34/bench/IMAGE-PLAN.json')); pos=p['positions'] assert len(pos)==21,...` | ✅ | ✅ green |
| 160-04-01 | 04 | 2 | RIG-02, RIG-05 | T-160-20 | avrdude signature probe, two parse routes, hard fail if neither parses | unit | `python3 .planning/v1.34/tools/probe_board.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-04-02 | 04 | 2 | RIG-02, RIG-05 | T-160-22 | every field required/non-null; probe failure is a hard non-zero exit | unit | `python3 .planning/v1.34/tools/capture_provenance.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-04-03 | 04 | 2 | RIG-02, RIG-05 | T-160-21 | gate_record rejects any argv0 not one of the two absolute arm paths | unit | `python3 .planning/v1.34/tools/gate_record.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-05-01 | 05 | 2 | RIG-01, RIG-04 | T-160-30 | independent avrdude read-back, never the uploader's own verify | unit | `python3 .planning/v1.34/tools/judge_readback.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-05-02 | 05 | 2 | RIG-01, RIG-04 | T-160-34 | full-device SHA vs written image; app's 0/1/2 recorded unjudged | unit | `python3 .planning/v1.34/tools/judge_wrv.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-05-03 | 05 | 2 | RIG-01, RIG-04 | T-160-37 | touch_1200.py exits non-zero on every serial failure path | unit | `python3 .planning/v1.34/tools/touch_1200.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-06-01 | 06 | 3 | RIG-03 | T-160-40 | PROCEDURE.md's step list carries zero arm-conditional text | integration | `python3 -c " import re,sys t=open('.planning/v1.34/PROCEDURE.md').read() steps=[f'P-{i:02d}' for i in range(1,12)] for s in steps+['P-H1','P-H2']: n=l...` | ✅ | ✅ green |
| 160-06-02 | 06 | 3 | RIG-03 | T-160-42 | substitution tokens emitted literally, never expanded; empty diff gate | falsification | `python3 .planning/v1.34/tools/render_steps.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-07-01 | 07 | 4 | RIG-05 | T-160-50 | schema pins expected count + bring-up exclusion + reconciliation | unit | `python3 -c " import json,re lines=open('.planning/v1.34/bench/EVIDENCE.jsonl','rb').read().decode().splitlines() assert len(lines)==1, f'expected head...` | ✅ | ✅ green |
| 160-07-02 | 07 | 4 | RIG-05 | T-160-47 | --check re-renders and byte-compares EVIDENCE.md against the record | unit | `python3 .planning/v1.34/tools/render_evidence.py --selftest; echo "selftest rc=$?"` | ✅ | ✅ green |
| 160-07-03 | 07 | 4 | RIG-05 | T-160-52 | exit 2 on missing/empty tools dir; hard fail if a tool lacks --selftest | integration | `bash .planning/v1.34/tools/run_gates.sh; echo "run_gates rc=$?"` | ✅ | ✅ green |
| 160-08-01 | 08 | 5 | RIG-01 | T-160-55 | signature probe authoritative, cross-checked vs operator declaration | manual | `MANUAL GATE (checkpoint:human-action, gate=blocking) -- no automated command` | n/a | ✅ green |
| 160-08-02 | 08 | 5 | RIG-01 | T-160-56 | independent read-back judged against the named arm's hex extent | on-device | `bash -c 'set -e; D=.planning/v1.34/bench/cells/BRINGUP-uno; test "$(stat -c%s $D/flash_readback.bin)" -eq 32768; python3 -c " import json v=json.load(...` | ✅ | ✅ green |
| 160-08-03 | 08 | 5 | RIG-01 | T-160-57 | real cross-flash MISMATCH observed and recorded with differing-byte count | falsification | `bash -c 'set -e; python3 .planning/v1.34/tools/gate_record.py --jsonl .planning/v1.34/bench/EVIDENCE.jsonl; python3 .planning/v1.34/tools/render_evide...` | ✅ | ✅ green |
| 160-09-01 | 09 | 6 | RIG-01 | T-160-66 | signature probe authoritative, cross-checked vs operator declaration | manual | `MANUAL GATE (checkpoint:human-action, gate=blocking) -- no automated command` | n/a | ✅ green |
| 160-09-02 | 09 | 6 | RIG-01 | T-160-63 | bootloader interrogation recorded before the comparator is armed | on-device | `python3 -c " import json p=json.load(open('.planning/v1.34/bench/cells/BRINGUP-uno328pb/probe.json')) assert '328pb' in str(p.get('connected_part','')...` | ✅ | ✅ green |
| 160-09-03 | 09 | 6 | RIG-01 | T-160-67 | real cross-flash MISMATCH observed and recorded on this target | falsification | `bash -c 'set -e; D=.planning/v1.34/bench/cells/BRINGUP-uno328pb; test "$(stat -c%s $D/flash_readback.bin)" -eq 32768; python3 -c " import json v=json....` | ✅ | ✅ green |
| 160-10-01 | 10 | 7 | RIG-01 | T-160-77 | signature probe authoritative; this is the milestone's reference rig | manual | `MANUAL GATE (checkpoint:human-action, gate=blocking) -- no automated command` | n/a | ✅ green |
| 160-10-02 | 10 | 7 | RIG-01 | T-160-72 | two explicit branches only: proven full read or named alternative | on-device | `bash -c 'set -e; D=.planning/v1.34/bench/cells/BRINGUP-leonardo; python3 -c " import json,os v=json.load(open(\"$D/READBACK-VERDICT.json\")) pins=json...` | ✅ | ✅ green |
| 160-10-03 | 10 | 7 | RIG-01 | T-160-73 | real cross-flash MISMATCH observed, completing all three targets | falsification | `python3 -c " import json rows=[json.loads(l) for l in open('.planning/v1.34/bench/EVIDENCE.jsonl') if l.strip()] hdr=rows[0]['_schema']; data=rows[1:]...` | ✅ | ✅ green |
| 160-11-01 | 11 | 8 | RIG-02 | T-160-82 | --shield-rev required, closed value set, no default; operator declares | manual | `MANUAL GATE (checkpoint:human-action, gate=blocking) -- no automated command` | n/a | ✅ green |
| 160-11-02 | 11 | 8 | RIG-02 | T-160-81 | provenance captured at the step before the flash; captured_at_step records it | on-device | `bash -c 'set -e; D=.planning/v1.34/bench/cells/BRINGUP-wrv; python3 .planning/v1.34/tools/gate_record.py --cell $D/provenance.json; python3 -c " impor...` | ✅ | ✅ green |
| 160-11-03 | 11 | 8 | RIG-02 | T-160-87 | monitors don't route to socket; one confirming read, no monitor loop | manual | `MANUAL GATE (checkpoint:human-action, gate=blocking) -- no automated command` | n/a | ✅ green |
| 160-12-01 | 12 | 9 | RIG-04 | T-160-92 | distinct per-position image regenerated and verified against its hash pre-write | on-device | `python3 -c " import json,hashlib D='.planning/v1.34/bench/cells/BRINGUP-wrv' plan=json.load(open('.planning/v1.34/bench/IMAGE-PLAN.json')) row=[e for ...` | ✅ | ✅ green |
| 160-12-02 | 12 | 9 | RIG-04 | T-160-91 | judged verdict is full-device SHA vs written image, not the app's exit code | on-device | `python3 -c " import json,hashlib,glob,os D='.planning/v1.34/bench/cells/BRINGUP-wrv' v=json.load(open(f'{D}/WRV-VERDICT.json')) plan=json.load(open('....` | ✅ | ✅ green |
| 160-12-03 | 12 | 9 | RIG-04 | T-160-97 | config-dir SHA recomputed and compared at teardown | integration | `python3 -c " import json rows=[json.loads(l) for l in open('.planning/v1.34/bench/EVIDENCE.jsonl') if l.strip()] hdr=rows[0]['_schema']; data=rows[1:]...` | ✅ | ✅ green |
| 160-13-01 | 13 | 10 | RIG-05 | T-160-102 | fresh context, two inputs only; diff states zero values from outside them | falsification | `bash -c 'set -e; R=.planning/v1.34/bench/cells/BRINGUP-wrv/RECONSTRUCTION.md; D=.planning/v1.34/bench/cells/BRINGUP-wrv/RECONSTRUCTION-DIFF.md; grep -...` | ✅ | ✅ green |
| 160-13-02 | 13 | 10 | RIG-05 | T-160-106 | todo annotation is additive only; status/resolves_phase left unchanged | unit | `bash -c 'set -e; T=.planning/todos/pending/avrdude-mcu-detection-fallback.md; grep -qx "status: pending" "$T"; grep -qx "resolves_phase: null" "$T"; g...` | ✅ | ✅ green |
| 160-13-03 | 13 | 10 | RIG-05 | T-160-109 | gate document names falsification artifacts; suite result alone insufficient | manual | `MANUAL GATE (checkpoint:human-verify, gate=blocking) -- no automated command` | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Sampling-continuity walk (checked, not asserted):** walking all 38 rows in order, counting
checkpoint tasks as neither breaking nor satisfying a run of automated-verify tasks: the
longest run of consecutive non-checkpoint (`auto`) tasks without an automated leg is **zero**
— every `auto` task row above carries a non-empty `<automated>` command. The checkpoint tasks
(`160-01-02`, `160-08-01`, `160-09-01`, `160-10-01`, `160-11-01`, `160-11-03`, `160-13-03`)
never appear three-in-a-row (the closest run is the two consecutive `160-11-01`/`160-11-03`,
separated by the auto task `160-11-02`), so no run of three consecutive *implementation*
(`auto`) tasks ever lacks an automated check. **No gap found.**

### Requirement → test map (research-measured)

| Req | Behavior | Test type | Automated command | Exists? |
|-----|----------|-----------|-------------------|---------|
| RIG-01 SC#1 | six images build from named SHAs; each has a recorded hash | integration | `cd /workspaces/firestarter && rm -rf .pio/build/$E && pio run -e $E` then `sha256sum -c SHA256SUMS.txt` | ✅ built plan 02, all 6 byte-identical |
| RIG-01 SC#1 | rebuild reproduces the hash, or the divergence is recorded with a measured cause | integration | `python3 tools/check_rebuild.py --images … --expect SHA256SUMS.txt` | ✅ built + exercised plan 02, all 6 pairs measured |
| RIG-01 SC#2 | read-back over the hex extent equals the flashed image | integration, on-device | `python3 tools/judge_readback.py --hex … --readback … --objcopy …` | ✅ built plan 05, on-device plans 08-10 |
| RIG-01 SC#2 | the check is **proven able to fail** | falsification, on-device | the D-03 cross-flash: same `judge_readback.py`, **observed** non-zero, artifact committed | ✅ observed MISMATCH on all 3 targets, plans 08/09/10 |
| RIG-03 SC#3 | the two arms' step lists diff empty | unit | `diff <(render_steps.py --arm control) <(render_steps.py --arm v133)` must be empty | ✅ built plan 06, empty diff confirmed through plan 13 |
| RIG-03 | the two arms' CLI surfaces are identical | unit | AST / `--help` diff across all 25 commands | ✅ AST diff empty both directions (plan 03); `--help` variant recorded in `ARM-CLI-SURFACE.md` |
| RIG-04 | full-device SHA equality vs the written image, never an exit code | integration, on-device | `python3 tools/judge_wrv.py --written … --reads … --expect-size 65536\|262144` | ✅ built plan 05, on-device (65536 B) plan 12 |
| RIG-04 | N=3 resolving to one SHA; a disagreement recorded as a disagreement | integration, on-device | same tool; counts `run_*.bin` (fewer than N on a hw error) and emits `disagreement` rather than retrying | ✅ built + selftest-exercised plan 05; on-device (clean match) plan 12 |
| RIG-02 / RIG-05 | every required provenance field present and non-null | unit | `python3 tools/gate_record.py <cell>/provenance.json` | ✅ built plan 04, green on the real `BRINGUP-wrv` record through plan 13 |
| RIG-05 | every recorded command line re-parses into the prescribed set | unit | same gate: assert `argv[0]` ∈ {the two absolute arm binaries}; reject bare `firestarter` | ✅ built plan 04, exercised live on real cells (plans 08-12) |
| RIG-05 | reconstruction from the record alone matches the prescription | manual, once | fresh context given only the bring-up record + PROCEDURE.md; output diffed against the prescription (D-17) | ✅ done plan 13 (three rounds) — `RECONSTRUCTION.md` / `RECONSTRUCTION-DIFF.md` |
| D-18 | no cell outcome is ever `inconclusive` | unit | `gate_record.py` asserts `outcome ∈ {validated, skipped-with-reason}` | ✅ built plan 04, enforced on the canonical record through plan 13 |
| D-15 | `EVIDENCE.md` is byte-identical to a fresh render of `EVIDENCE.jsonl` | unit | `render_evidence.py --check` | ✅ built plan 07, green through plan 13 |
| D-07 | the shared config dir is unchanged after each cell | unit | recompute the tree SHA, compare against the recorded value | ✅ built plan 03 (`check_arms.py`), exercised at every cell's teardown |
| Pitfall 8 | the two arm venvs resolve identical dependency versions | unit | `diff` of the two `pip freeze` outputs must be empty | ✅ built + confirmed empty plan 01, re-confirmed by `check_arms.py` through plan 13 |

---

## Wave 0 Requirements

Reconciled at phase close (Plan 13, Task 2) against `.planning/v1.34/tools/` as it actually
exists: the list below names all twelve files under that directory (the original ten, plus
two additions the strategy document itself flagged as gaps in the recommended tool list —
each noted below). Every entry corresponds to a file that exists and is marked complete.

- [x] `.planning/v1.34/tools/run_gates.sh` — the "full suite" runner (plan 07)
- [x] `tools/judge_readback.py` — RIG-01 SC#2 (`-A` read, `avr-objcopy` normalize, span compare, whole-flash datum recorded unjudged per D-02) (plan 05)
- [x] `tools/judge_wrv.py` — RIG-04 (full-device SHA, file-count guard, app-verdict disagreement flag) (plan 05)
- [x] `tools/capture_provenance.py` — RIG-02 / RIG-05 (`--shield-rev` required-or-refuse; `python -P` on the `__file__` probe per Pitfall 1) (plan 04; extended plan 13 with `image_mask`/`image_stamp_width`/`image_sha` per the D-17 reconstruction's record-insufficiency finding)
- [x] `tools/gate_record.py` — D-17 script gate (field presence + command re-parse + `outcome` domain) (plan 04)
- [x] `tools/render_evidence.py` — D-15, with a `--check` mode so "never hand-edited" is enforced (plan 07)
- [x] `tools/probe_board.py` — D-14 signature probe, both parse routes, plus `-xshowvector` on `uno328pb` (Pitfall 3) (plan 04)
- [x] `tools/touch_1200.py` — Leonardo bootloader entry (pyserial) (plan 05)
- [x] `tools/gen_addr_image.py` — copied from Phase 145 with its D-16 boundary comment intact; stamp-width decision made before generating images (16-bit stamp repeats every 64 KiB on the 256 KiB W29C020) (plan 03)
- [x] `tools/check_rebuild.py` — SC#1's reproduce-or-record-the-cause clause (plan 02)
- [x] **`tools/check_arms.py`** (addition 1 of 2, plan 03) — the requirement→test map above names "the two host arms including the dependency-set equality and config-directory checks" (RIG-02/RIG-03/D-07/Pitfall 8) but the original ten-item list assigned this behaviour to no tool; this is that tool — SHA/porcelain/`__file__`/dependency-set/config-dir-SHA/CLI-surface verification, on demand and at every cell's teardown.
- [x] **`tools/render_steps.py`** (addition 2 of 2, plan 06) — RIG-03 SC#3's requirement-to-test row ("the two arms' step lists diff empty") named a behaviour the original ten-item list omitted entirely; this tool renders `PROCEDURE.md`'s step list per arm and is the SC#3 empty-diff gate itself.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Reconstruction of a cell run from the record alone | RIG-05 SC#5 (D-17) | Automating it would let the record's author also be its reader — the whole point is that a party with no session memory can rebuild the run | Give a fresh context only the bring-up record + `PROCEDURE.md`; have it emit the command set and physical setup; diff against what the procedure prescribes; **zero fields may come from session memory** |
| Chip insertion / removal, photography, multimeter readings, pot adjustment | RIG-02, RIG-03 | Standing bench rule — operator-only | `PROCEDURE.md` names the operator step and the single reading; Claude drives serial/CLI only (Phase 145 D-19) |
| Shield revision declaration | RIG-05 | `hw_revision` cannot distinguish Rev 2.2 / Rev 2.0 / modified Rev 0; the A3 ADC check collides on 10 kΩ | Operator declares it; `capture_provenance.py` requires `--shield-rev` and refuses to infer |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or a declared manual gate — confirmed by the
      Per-Task Verification Map above: every `auto` row carries a non-empty Automated
      Command, and every `checkpoint:*` row is marked `manual` with its gate type.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — walked, not
      asserted; see the "Sampling-continuity walk" note above. No gap found.
- [x] Wave 0 covers all MISSING references — reconciled against `.planning/v1.34/tools/` as
      it exists today (twelve files); see the Wave 0 Requirements section above.
- [x] No watch-mode flags — no `--watch` flag appears in any tool, task, or command cited in
      this phase (`grep -rn "\-\-watch\b"` over the phase's plans and `.planning/v1.34/tools/`
      returns nothing besides unrelated "watchdog" substrings, none present here).
- [x] Every gate observed **red** once against a deliberately broken input — every tool's own
      `--selftest` mode carries negative legs exercised at authoring time (plans 02-07), and
      every live gate has a corresponding real-world red observation: the D-03 cross-flash
      MISMATCH on all three targets (plans 08-10), the plan-12 Task 2 verify-leg defect and
      the plan-9/12 record findings caught by `gate_record.py`/the reconstruction itself
      (plan 13). No gate in this phase has been trusted green without first being seen red.
- [x] Both falsification tests (D-03 cross-flash, D-17 reconstruction) observed, not authored
      — D-03: three real MISMATCH observations plus corrections, one per target (plans 08,
      09, 10). D-17: three fresh-context reconstruction rounds against `BRINGUP-wrv`'s real
      record (plan 13, `RECONSTRUCTION.md` / `RECONSTRUCTION-DIFF.md`).
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** This validation strategy's own compliance is complete as of Plan 13, Task 2.
This is **not** the phase's operator sign-off — that is Plan 13 Task 3's separate
`checkpoint:human-verify` gate (`PHASE-160-GATE.md`), which remains `pending` until the
operator responds. Do not read this section's completion as phase closure.
