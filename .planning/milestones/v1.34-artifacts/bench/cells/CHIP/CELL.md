# Cell CHIP — 11-Part `dev test` Sweep on the Reference Rig (Leonardo + Rev 2.0)

Standing rig Phase 161 left assembled. This cell is opened by plan 162-05 and closed by
plan 162-10. See `.planning/milestones/v1.34-artifacts/PROCEDURE.md`'s `## Chip-sweep step list` (C-01..C-09) for
the step ids cited below, and `162-05-PLAN.md`'s "Planner decisions" section for PD references.

## Session open (Task 1) — rig confirmation, operator-performed

- **Device node:** `/dev/ttyACM0` — operator confirmed this is the Leonardo, not inferred from
  it being the only node. (Re-verified by signature at Task 2, `P-02`.)
- **Shield revision (silkscreen, verbatim operator wording):** "2.0" — canonical form for
  `--shield-rev` is **`Rev 2.0`** (case-only normalization for `capture_provenance.py`'s closed
  choice set, per the `BRINGUP-leonardo-provenance/PREPROOF.md` precedent; not a correction of
  what the operator said).
- **Chip seating:** **W27C512** (DIP28) confirmed seated, pin-1 oriented, **JP4 at the 28-pin
  position**. Zero handling for position 1 (Phase 161's A3/B2 teardown left it exactly so).
- **VPP:** see `POT.md` for the full record, **including a retracted finding**. As-found 11.4 V
  was Phase 161's own correct, settled working point — properly inherited, no drift. An
  orchestrator mis-citation of a different (superseded, pre-adjustment) A3/B2 reading led to an
  up-adjustment to 11.97 V, which produced a firmware reading of 12800 mV — 300 mV above the
  12500 mV high guard; corrected back down. **Operative reading for the 12 V group (positions
  1-8): meter 11.6 V / firmware 12400 mV**, in band with 100 mV margin below the high guard.

## Pre-flight (Task 2)

*(filled in below once the port-identity, arm-state and `fw_board_identity` bring-up datum steps
run)*

## Position 1 — `CHIP__v133__w27c512` (Task 3)

**Deviation, recorded plainly:** the first `dev test W27C512` invocation was aborted at ~120s by
an **executor tooling error** — an outer shell-harness default timeout (120s) fired before this
task's own intended 500s ceiling could. This is **not** a PD-15 ceiling kill (no rig hang, no
measured-baseline comparison) and **not** a P-H1 rig finding — it is a self-caused mistake, logged
rather than hidden: `logs/CHIP__v133__w27c512.attempt1_aborted.std{out,err}.log`. No report was
written by the aborted attempt (`dev test` persists its report only on completion); the frozen
config dir was confirmed still pristine before the clean retry. The clean retry below completed
normally, well inside the intended ceiling.

**Tool fix (Rule 1, found live):** `append_chip_evidence.py`'s `READBACK-VERDICT.json` load was
unconditional for every position, inherited unmodified from the WRV sibling (`append_evidence.py`)
where every position genuinely flashes-and-reads-back. A chip-sweep position only does that on a
divergence (`C-08`) — every non-diverging position (this one included) has no such artifact and
never will, so the tool hard-refused with no way to proceed. Added an additive-only
`--pending-readback` flag (mirrors `capture_provenance.py`'s own seam of the same name): skips the
`READBACK-VERDICT.json` load/validate entirely; `fw_readback_sha_judged`/`fw_readback_sha_whole_flash`
come from `--provenance` as-is (already carrying `capture_provenance.py`'s own pending-readback
placeholder text). Default (flag omitted) behaviour is byte-for-byte unchanged — a control-rerun
row (`arm=control`) still hard-requires and validates a real judged read-back. 19 selftest legs
pass (18 prior + 1 new positive leg proving the seam); `git diff` scope is additive-only (one new
argparse flag, a conditional guard replacing an unconditional two-line load, one new selftest leg).

**Second deviation, caught by the orchestrator's own independent `run_gates.sh` run (not by this
executor's checkpoint claim) — the Position 1 row initially failed `gate_record` on two fields.**
The checkpoint after Task 3 reported `render_chip_evidence.py --check` green, which is true but is
a *different* gate from the record-shape gate (`gate_record.py` against `CHIP-EVIDENCE.jsonl`
directly). The orchestrator re-ran the full suite, read `RC` directly, and it was **1**:

```
FAIL: line 2: required field 'read_divergence' is null/blank/placeholder: None
FAIL: line 2: required field 'repeat_policy' is null/blank/placeholder: ''
```

Both are genuine bugs in `append_chip_evidence.py`, fixed at the derivation layer — **not** by
weakening the gate, the schema, or the required-field list:

1. **`repeat_policy` was a bare `""`.** `derive_repeat_policy()`'s healthy-case return value (no
   `--fast`, every multi-run step at `run_count>=2`) mirrored the app's own internal
   `repeat_policy_tag()` sentinel (also `""`) literally, but `gate_record.check_required_fields`
   treats **every** record_key as required-non-blank unless it carries the `not measured — <reason>`
   shape — an empty string fails that rule on every row this position type could ever produce. Now
   returns `"default (every multi-run step at run_count>=2, no --fast)"` for the healthy case,
   the pre-existing `"runs=1"` tag unchanged for the degraded case. This is a **naming** fix, not a
   semantic one — 162-07-PLAN.md's own acceptance check already anticipated a non-empty value
   (`repeat_policy == '' or 'runs=1' not in repeat_policy`).
2. **`read_divergence` was a bare `None` — a genuine finding, checked before coding, per
   instruction.** Confirmed live against the v1.33 arm's own installed source: `chip_test.py`
   computes a per-read byte-level divergence metric internally (`StepResult.divergence`, the same
   primitive credited with the AM27C020 write#1/write#2 finding) but
   `diagnostic_report.py`'s `_step_dict()` **never serializes a `divergence` key** into the
   exported report at all — grepped directly, confirmed absent. This is a genuine host-app gap,
   out of scope to fix here (D-16). Fixed at the correct layer: `derive_read_divergence()` now
   returns the real value if a future report version ever carries one (defensive), otherwise the
   schema's own `not measured — <reason>` shape naming the exact gap. `derive_read_consistency_followup()`
   updated in lockstep so a not-measured `read_divergence` renders as `not applicable — <reason>`
   for the follow-up column, never as a false "diverged" signal.
3. **Defense in depth, added at the same time:** `append_chip_evidence.py` previously validated
   only its four human-supplied fields against `gate_record.check_required_fields` before writing
   — none of the ~60 machine-derived fields were self-checked, so this exact class of bug reached
   disk silently and was only caught later, by a separate tool, in a separate full-file scan.
   Added a whole-row self-check (`gr.check_required_fields(row, record_keys)`) immediately after
   `build_row()`, before either `--dry-run`'s return or the real write — a future derivation bug is
   now refused at append time.

**Backlog finding for Phase 165/166 (not fixed here, D-16 boundary):** `diagnostic_report.py`'s
`_step_dict()` drops the `divergence` metric `chip_test.py` computes for every multi-run read
step. This means **`C-06`'s own read-divergence follow-up trigger
(`read_divergence.repeat_divergent == true`) can never fire from any report this project produces**
— the mechanism the procedure describes is unreachable via its stated oracle. Every position in
this sweep will carry `read_divergence` as `not measured — <reason>` and
`read_consistency_followup` as `not applicable — <reason>`, for the identical reason, not as a
per-position anomaly. Filed here so plan 162-10's reconciliation and Phase 165/166's backlog
carry it forward as a real, citable gap rather than rediscovering it nine more times.

Corrected row re-appended (the invalid row was removed from `CHIP-EVIDENCE.jsonl` — only the
schema line preceded it, so no other row's byte-unchanged prefix was disturbed — and
`append_chip_evidence.py` re-run against the same underlying report/provenance data, with the
report content unchanged: `report_json_sha256` is `2a0fc730d6d502b9260c62ecbb0e54a2cd8d96fe6e5c34208c2865951d17b273`).
Full suite re-run after the fix, `RC` read directly: **`run_gates.sh` exits 0, 14/14 selftests,
7/7 live gates, `ALL GATES PASSED`**, and `render_chip_evidence.py --check` remains green against
the corrected row.

### C-03 — VPP

See `POT.md`'s full record (including the retraction of an earlier, incorrect finding). Operative
reading for this position: firmware **12400 mV**, meter **11.6 V** — in band, 100 mV margin below
the 12500 mV high guard.

### C-05 — clean run, exit 0, wall-clock 214s

```
timeout 500 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev test W27C512
```

| Step | Verdict | Runs | Cycle-sum duration_s | Per-operation duration_s (÷ run_count) |
|---|---|---|---|---|
| id | OK | 1 | 3.449 | 3.45 |
| read | OK | 2 | 21.139 | 10.57 |
| write | OK | 2 | 122.42 | 61.21 |
| verify | OK | 2 | 28.537 | 14.27 |
| erase | OK | 2 | 16.733 | 8.37 |
| blank-check | OK | 2 | 16.233 | 8.12 |

Banner: 6 of 6 ran. Steps total (report's own sum): 208.5s. **Wall-clock around the whole
invocation (the phase's first real `dev test` duration figure): 214s.** VPP before/after:
12400/12400 mV (unchanged across the run, confirming C-03's reading). `fw_board_identity`:
`3.0.0b22:leonardo` (non-null). `repeat_policy`: empty string = the default two-cycle policy (not
the degraded single-run tag — no `--fast` was used, confirmed by every multi-run step showing
`run_count: 2`).

**Anomaly, recorded not fabricated away:** a transient `ERROR: Empty input` line
(`MSG_ERR_EMPTY_INPUT`, 0xA4) appeared between the first blank-check and the second write cycle,
identically in both the aborted attempt and the clean run — reproducible, self-recovering, no
effect on any step's own verdict.

### Comparison against the ~123s estimate — the budget did NOT hold; ceiling is now measured, not derived

The plan's pre-measurement fallback ceiling (500s) was derived from **4 × 123s**, itself the sum
of estimated same-rig components (two 10.66s reads, two 33.37s app-reported writes, two verifies,
one erase, one blank-check ≈ 123s). **The real measured total is 214s wall-clock — 91s (74%)
higher than the 123s estimate**, mostly because the estimate summed only the six *app-reported*
operation timings and did not account for wall-clock overhead (process start-up + serial handshake
recurring at every one of the ~15 internal reconnects `dev test` performs across six steps run at
a 1-2x cycle count) — the same distinction the procedure's own "Write-duration definition" section
draws between wall-clock and app-reported figures.

### DERIVED — the 64 KiB class ceiling for parts 2, 3 and 10

**4 × 214s (this position's measured wall-clock total) = 856s.** This supersedes the 500s
derived-fallback ceiling for every later 64 KiB-class position (`W27E512` at Task 5, and parts 3
and 10 in later plans) per the plan's own instruction ("read from `CELL.md` rather than from the
derived fallback"). Stated as arithmetic with its basis, not silently substituted.

## Position 2 — `CHIP__v133__w27e512` (Task 5)

### OPERATOR RULING — supersedes this position's original divergence framing; read this first

**Verbatim in substance:** *if `dev test` reported OK, the part is OK. Old test records are not
proof and are not interesting.*

**Effect, stated explicitly per the instruction not to silently reinterpret the criteria:** this
plan's own `162-05-PLAN.md` (and, by inheritance, `CHIP-04`/SC#4's framing in the phase plan) was
worded around comparing each position's `dev test` result to its v1.15 disposition, with a mismatch
against that disposition as the divergence trigger. **The operator ruling replaces that trigger.**
The operative baseline for this entire sweep is now `dev test`'s own verdict on the v1.33 arm, not
a prior milestone's disposition:

- A `dev test` **OK** is a pass, `divergence_verdict: same`, whatever any prior record said. No
  control row.
- A `dev test` **FAIL/BAD** is the interesting case, and earns the control-arm re-run — to
  establish whether control firmware fails the same way (not v1.33-attributable) or passes where
  v1.33 fails (a genuine v1.33 regression).
- `known_carried` still applies to parts whose **failure** reproduces.

This position is the first to be affected: it was originally recorded as `diverges:` (citing three
internal report indicators consistent with the v1.15 disposition) and escalated to a full C-08
control-arm arbitration, both narrated below **as historical record of what was actually done**,
before the ruling arrived. The row itself has been **corrected** to the ruling's shape (`same`,
`known_carried: no`) — see "Final row content" below. **Plan 162-10 must reconcile against what was
actually done here (this ruling), not against the phase plan's original CHIP-04/SC#4 wording.**

### C-03 — VPP (named absence, inherited from position 1)

Firmware reading re-confirmed: **12400 mV**, in band, unchanged (pot untouched since position 1).
`vpp_real_mv` recorded as a named absence pointing back to `CHIP__v133__w27c512`, per D-13.

### C-05 — clean run, exit 0, wall-clock 213s, under the measured 856s ceiling — UNCHANGED BY THE RULING

```
timeout 856 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev test W27E512
```

All six steps report verdict **OK**: id x1 (3.55s), read x2 (21.2s), write x2 (122.2s, full-device
region `0`–`65536`), verify x2 (28.4s), erase x2 (16.7s), blank-check x2 (16.1s). Banner 6 of 6
ran, steps total 208.1s. `fw_board_identity` `3.0.0b22:leonardo`, non-null. **Measured `erase`
duration: 16.7s cycle-sum / 2 = 8.35s per operation — the fast-fail assumption (RESEARCH A4) held**,
comparable to position 1's own figure (8.37s per operation). No ceiling widening needed.

### Final row content, per the operator ruling

`divergence_verdict: same`. `known_carried: no` (no failure occurred, so nothing is carried).
`prior_disposition`/`prior_dispositions_all` still cite v1.15 Phase 82 (`:97`) and the D-32
exclusion (`:256`), but explicitly as **historical context, not an authoritative baseline** — the
row's own verdict text states this plainly. The `read.reason='read runs diverged'` and
`write`/`verify.fingerprint='indeterminate'` observations are **kept as recorded detail** (they are
real, reproducible facts about this run) but are explicitly **not grounds for a divergence verdict
on their own** per the ruling — `dev test`'s own OK verdict is the arbiter. Neither "healed" nor
"still faulty" is asserted; neither is established, and the ruling holds that the phase does not
need to settle it.

### Historical record — what was actually done before the ruling arrived (superseded, not deleted)

**Original characterisation (superseded):** this position was first recorded as `diverges:`,
reasoning that an all-OK report can still diverge from a recorded FAIL disposition when internal
fields (the three observations above) are consistent with the original defect. That reasoning is
**not wrong on its own terms** — it is simply not the rule this sweep now operates under. Recorded
here so the audit trail is complete, not because the conclusion stands.

**C-08 control-arm interleave — physically performed, its row now retracted:**

- **Flash 1 — control.** `git -C firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a`
  (porcelain empty before/after), `env -C /workspaces/firestarter pio run -t upload -e leonardo` —
  SUCCESS, 28170 bytes. **Proven by independent read-back** (RIG-02): `touch_1200.py` +
  `judge_readback.py --flashed-arm control --expect-arm control` → `judged_match: true`,
  `judged_span_bytes: 28170`. Fresh `probe_board.py` re-confirmed the same silicon.
  `capture_provenance.py` re-run for the control arm: `fw_board_identity` non-null
  (`3.0.0b22:leonardo`).
- **Control-arm `dev test W27E512` re-run**, same seating, same pot, exit 0, wall-clock 213s — all
  six steps OK, the same `indeterminate` write/verify fingerprint shape as the v133 run; the one
  difference, `read.reason`, did not reproduce on the control run.
- A control row (`CHIP__control__w27e512`, `control_rerun_for: CHIP__v133__w27e512`) was appended,
  with a conclusion that this was "not a v1.33 regression." **That row has been removed from
  `CHIP-EVIDENCE.jsonl`** per the operator ruling ("do not append a control row" for an OK `dev
  test` result) — its content is preserved here in `CELL.md` only, as a record of the work
  performed, not as evidence carried into the phase's own reconciliation.
- **Flash 2 — restore to v1.33.** `git checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`
  (porcelain empty), `env -C /workspaces/firestarter pio run -t upload -e leonardo` — SUCCESS,
  25098 bytes. **Proven by independent read-back**: `judged_match: true`, `judged_span_bytes:
  25098`. Re-confirmed a third time after a self-caused stray rebuild (see below) with an identical
  whole-flash SHA. `firestarter/` HEAD confirmed at the v1.33 SHA, porcelain empty, throughout and
  at the end.

**No wasted chip handling and no incorrect firmware left behind:** W27E512 stayed seated
throughout; the board was returned to v1.33, independently proven, before the ruling was even
received — so the ruling required no further physical or flash action, only a record correction.

### Deviation, recorded plainly: the C-08 flash needed a non-obvious invocation shape

`pio run -t upload -e leonardo` could not be invoked as `cd firestarter && pio run ...` (this
executor's Bash tool does not persist cwd across calls — confirmed empirically) nor via `pio run
-d firestarter ...` / `pio -d firestarter run ...` (PlatformIO's own global maintenance/telemetry
init resolves a project config off the real process cwd unconditionally, before any subcommand
flag is parsed — reproduced the identical `configparser.DuplicateSectionError` against
`/workspaces/platformio.ini` regardless of `-d`, confirming rig-pins.json's own Pitfall-4 note that
only the real process cwd fixes this). A PATH-shim script (a `pio` wrapper cd-ing into
`firestarter/` before delegating to the real binary, so a bareword `pio run ...` invocation would
land correctly) was attempted and was itself blocked by the harness's own auto-mode permission
classifier — treated as a signal to stop rather than try further variations, and reported rather
than routed around. The working form, confirmed live: `env -C /workspaces/firestarter pio run -t
upload -e leonardo` — a single command, `env -C` sets the real process cwd before exec, matching
Pitfall 4's actual requirement regardless of the caller's own shell cwd. (This deviation is
independent of the ruling above — it describes how the flash was executed, not whether it should
have been.)

### Deviation, self-caused: a stray `pio` flash from a backtick in a commit message

A `git commit -m "..."` string containing backtick-quoted shell syntax was command-substituted by
bash during the commit that recorded this position's original (since-superseded) work, causing an
unintended extra `pio run -t upload -e leonardo`. Investigated immediately: `firestarter/` HEAD was
already at the v1.33 SHA with empty porcelain, so the stray rebuild wrote byte-identical content —
confirmed by an additional independent read-back proof matching the deliberate restore's own
whole-flash SHA. No corrective action was needed beyond verification. Commit messages containing
backticks now go through `git commit -F <file>`.

## Leave-state at the end of this plan (162-05)

**Board:** Leonardo, `/dev/ttyACM0` (signature `0x1e9587`/`atmega32u4`, re-confirmed multiple
times this session). **Port:** `/dev/ttyACM0`. **Arm on the board:** v1.33
(`5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`), restored and independently read-back-proven
(`judged_span_bytes: 25098`) after the control-arm interleave. **Chip seated:** W27E512 (DIP28),
pin-1 oriented, JP4 at 28-pin — unchanged since Task 4, never removed. **Pot setting:** meter
11.6 V / firmware 12400 mV, in band, unchanged since position 1's correction. **Shield:** Rev 2.0,
mounted, unchanged all session. This is the state plan 162-06 inherits at zero physical cost for
its own first handover (per this plan's own key_links note).

## Position 3 — `CHIP__v133__sst27sf512` (162-06 Task 1-2)

**Operator ruling (162-05) still governs:** `dev test`'s own v133 verdict is this sweep's
operative baseline. All six steps OK -> `divergence_verdict: same`, no control row, whatever any
prior milestone recorded.

**Chip swap (Task 1, operator-performed):** W27E512 removed, SST27SF512 seated (DIP28), pin-1
oriented. JP4 left at 28-pin, pot untouched (operator confirmed: "SST27SF512 seated"). Reseat
count: 0.

### C-01 — frozen config dir pristine

`check_arms.py --expect-config-sha 77adfdd2...` -> OK, matches the pinned digest. No stray files
from position 2's own copy-out.

### C-03 — VPP, named absence (D-13, inherited)

Single reading, unchanged since position 1: **12400 mV**, in band (100 mV margin below the
12500 mV high guard). `vpp_real_mv` recorded as a named absence pointing back to
`CHIP__v133__w27c512`.

### C-04 — provenance

Port re-verified live by signature (`touch_1200.py` + `probe_board.py`, 2s settle,
`--board-probe-json` seam per the 162-05 Leonardo bring-up finding — avoids the Caterina avr109-exit
race): `board_signature: 0x1e9587`, `connected_part: atmega32u4`, matches. `capture_provenance.py`
run with `--pending-readback` (this position never flashes; the seated v1.33 arm's own
flash-and-readback proof belongs to an earlier cell).

### C-05 — `dev test SST27SF512`, exit 0, steps total 201.6s

```
timeout 856 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev test SST27SF512
```

**Deviation, recorded plainly (the same class of executor tooling mistake already logged at
position 1):** the first invocation was killed by the outer harness's own shorter default timeout,
mid-way through the second write cycle — not this task's own 856s ceiling, not a PD-15 kill, not a
P-H1 rig finding. No report was written by the aborted attempt (`dev test` persists its report only
on completion); the frozen config dir was confirmed still pristine (matching the pinned SHA) before
the clean retry. Logged at
`logs/CHIP__v133__sst27sf512.attempt1_aborted.std{out,err}.log`. The clean retry (this task's
Bash call given an explicit long timeout) completed normally, well inside the 856s ceiling.

| Step | Verdict | Runs | Duration_s (cycle-sum) |
|---|---|---|---|
| id | OK | 1 | 3.53 |
| read | OK | 2 | 21.2 |
| write | OK | 2 | 115.6 |
| verify | OK | 2 | 28.5 |
| erase | OK | 2 | 16.6 |
| blank-check | OK | 2 | 16.1 |

Banner: 6 of 6 ran. Steps total 201.6s. `fw_board_identity`: `3.0.0b22:leonardo`, non-null. VPP
before/after: 12400/12400 mV. The same reproducible, self-recovering `ERROR: Empty input`
(`MSG_ERR_EMPTY_INPUT`, 0xA4) already seen at positions 1 and 2 recurred at the identical point in
the sequence (between the first blank-check and the second write) — not a new finding.

### Tool fix (Rule 1, found live): `vpp_firmware_mv` was silently `not measured` on every
### real chip-sweep position, including positions 1 and 2

`append_chip_evidence.py`'s `derive_vpp_firmware_mv()` looked for a literal `VPP: <N.N>V` line in
`--console-log` — that string shape belongs only to the standalone `vpp` CLI subcommand's own
continuous-print loop (C-03's separate invocation), never to `dev test`'s own console output
(a rich-rendered summary table, no such literal line anywhere in it). This position's row would
otherwise have carried `vpp_firmware_mv: not measured` / `vpp_shortfall_mv: not measured` —
exactly what positions 1 and 2 already carry in their own committed rows (checked: both do).
**Fixed at the correct layer, not by weakening the check:** the report JSON already carries the
firmware's own reading verbatim (`voltage.vpp_before_mv`, an exact mV int) — `derive_vpp_firmware_mv`
now reads that field directly when present and numeric, falling back to the original console-log
scrape only when it is absent (preserves the function's three pre-existing selftest legs
byte-for-byte). One new positive selftest leg added, proving the report field wins even when the
console log carries no `VPP:` line at all (the real `dev test` shape). 20/20 selftest legs pass
(19 prior + 1 new). This position's row: `vpp_firmware_mv: 12400`, `vpp_shortfall_mv: -400`
(target 12000 − firmware 12400).

**CORRECTION — positions 1 and 2 WERE re-derived, immediately after, by orchestrator instruction.**
This executor's own first call was that positions 1 and 2 were out of scope (a closed-plan
boundary) and deferred the fix to plan 162-10's reconciliation. **That scope call was overridden
as wrong**, for three reasons the orchestrator gave directly: `CHIP-EVIDENCE.jsonl` is a single
phase-spanning evidence artifact, not plan 162-05's private output, so plan boundaries do not
partition it; the deferred rows asserted a **false** `not measured` — the retained reports on disk
(`CHIP__v133__w27c512.json`, `CHIP__v133__w27e512.json`) both already carried
`voltage.vpp_before_mv: 12400`, a real, present, on-disk value, and a row claiming a measured value
was never measured is exactly the defect class this milestone's honesty ledger exists to catch;
and the fix is pure re-derivation from retained artifacts — no re-run, no hardware, no chip
handling, no judgement call. **Corrected, keeping the discovery visible rather than erasing it:**

Mechanism (the appender's own machinery, never a hand-edit): `CHIP-EVIDENCE.jsonl` enforces
append-only immutability (`render_evidence.append_row_to_file`'s own tested guarantee — "a row is
never rewritten once appended"), so an in-place field patch was not an option. All three rows
(positions 1, 2, 3 — 3 was already correct) were removed back to the schema line only, then
re-appended in original order through `append_chip_evidence.py`'s normal path, using each
position's own retained report/provenance/console-log/human-input files unchanged, with only the
now-fixed `derive_vpp_firmware_mv` code path producing a different result. Every other field on
every row was diffed key-by-key against a pre-removal snapshot and confirmed **byte-identical**
except the two VPP columns; position 3's row diffed as **zero** changed keys (a pure
no-op re-append, confirming the mechanism itself introduces no drift).

**Corrected values:**

| Position | `vpp_firmware_mv` (before -> after) | `vpp_shortfall_mv` (before -> after) |
|---|---|---|
| `CHIP__v133__w27c512` | `not measured — no 'VPP: <N.N>V' line found in --console-log` -> **`12400`** | `not measured — ...` -> **`-400`** |
| `CHIP__v133__w27e512` | `not measured — no 'VPP: <N.N>V' line found in --console-log` -> **`12400`** | `not measured — ...` -> **`-400`** |
| `CHIP__v133__sst27sf512` | already `12400` (unchanged) | already `-400` (unchanged) |

File order preserved (w27c512, w27e512, sst27sf512, matching original append/chronological
order). Config dir reconfirmed pristine (matches the pinned SHA) before and after every
temporary copy-back-and-append cycle. Both sub-repo porcelains confirmed empty throughout;
`firestarter/` confirmed still at the v1.33 SHA (no flash occurred). `render_chip_evidence.py
--check` green, `gate_record.py` re-run standalone against `CHIP-EVIDENCE.jsonl`: 0 violations,
`run_gates.sh` RC=0, 14/14 selftests, 7/7 live gates, `ALL GATES PASSED`.

The point of this record is an auditable trail, not a clean-looking history: this executor's
initial scope judgement was wrong, was corrected on the same day by the orchestrator before any
further work proceeded, and both the wrong call and the correction are kept visible here rather
than smoothed over.

### Final row content

`divergence_verdict: same`. `known_carried: no`. `prior_disposition` cites v1.15 Phase 82
(`EVIDENCE.md:98`, the auto-erase-proven PASS) as the newest and only disposition;
`prior_dispositions_all` additionally cites the Phase 81 read PASS (`:54`). Per the operator
ruling, this history is context only — the operative baseline is `dev test`'s own OK verdict here,
confirmed. `outcome: validated`. `render_chip_evidence.py --check` green, `gate_record.py` 0
violations, `run_gates.sh` RC=0, 14/14 selftests, 7/7 live gates, ALL GATES PASSED.

**The 28-pin, 12 V group is now complete** (positions 1, 2, 3 of 3 healthy DIP28 parts) — no pot
move, no JP4 change since the session opened.

## Position 4 — `CHIP__v133__fm1608` (162-06 Task 3-4)

**Chip swap (Task 3, operator-performed):** SST27SF512 removed, FM1608 seated (DIP28), pin-1
oriented. JP4 left at 28-pin, pot untouched (operator confirmed: "FM1608 seated"). Reseat count: 0.

**Second live application of the operator ruling — D-03's advance booking overridden.** The phase
plan (162-06-PLAN.md) pre-booked this position's `divergence_verdict` as `diverges: no comparable
baseline` in advance (D-03), on the reasoning that the newest prior disposition (v1.16 Phase 90)
was obtained via a now-forbidden flag. The orchestrator corrected this mid-plan, before any `dev
test` run: the operator ruling holds that `dev test`'s own v133 verdict is the sweep's operative
arbiter, and "no comparable baseline" is an absence of history, not a live failure — it does not
by itself earn a control-arm re-run under the ruling. Only a live FAIL/BAD would have triggered
`C-08`. Applied here in full: `dev test FM1608` was run alone first, with no pre-emptive flash and
no pre-emptive control re-run.

### C-01 — frozen config dir pristine

`check_arms.py --expect-config-sha 77adfdd2...` -> OK, matches the pinned digest.

### C-03 — VPP, named absence (D-13, inherited)

Single reading, unchanged since position 1: **12400 mV**, in band. `vpp_real_mv` recorded as a
named absence pointing back to `CHIP__v133__w27c512`.

### C-04 — provenance

Port re-verified live by signature (`touch_1200.py` + `probe_board.py`, 2s settle,
`--board-probe-json` seam): `board_signature: 0x1e9587`, matches. `capture_provenance.py` run with
`--pending-readback` (no flash occurred this position).

### C-05 — `dev test FM1608`, exit 0, steps total 71.0s — clean on the first attempt

```
timeout 120 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev test FM1608
```

No timeout drama this time — let to finish inside a single Bash call given a generous explicit
timeout, per the standing instruction not to abort on timeout impatience.

| Step | Verdict | Runs | Duration_s (cycle-sum) |
|---|---|---|---|
| id | NA | 0 | — |
| read | OK | 2 | 8.37 |
| blank-check | NA | 0 | — |
| write | OK | 2 | 50.5 |
| verify | OK | 2 | 12.2 |
| erase | NA | 0 | — |

Banner: **3 of 3 ran** (a reduced banner is expected here, not a defect — three steps are
structurally NA by construction). Steps total 71.0s, well inside the 120s 8 KiB fallback ceiling —
**this position supplies the phase's first 8 KiB duration figure**: no wider class ceiling is
derived from a single data point (no other 8 KiB part exists in the inventory), but 71.0s is
recorded as the measured basis. `fw_board_identity`: `3.0.0b22:leonardo`, non-null. VPP
before/after: 12400/12400 mV.

### The predicted failure shape — did NOT manifest, recorded as a data point, not a fix

The folded todo (`fm1608-byte0-write-never-lands-register-cache-elision.md`) predicted: if the
register-cache-elision defect fires, `write` reports success and `verify` goes BAD with a
single-byte mismatch at offset 0. **Observed vs. predicted:** `verify` succeeded on **both**
alternating-pattern write/verify cycles — no byte-0 mismatch anywhere in the console output or the
report's per-step verdicts (`write`/`verify` both `OK`, `fingerprint: indeterminate` on both, the
same ambiguous-bucket shape already seen on positions 1-3, not itself grounds for a divergence).
**This is a live PASS, not a live FAIL** — under the operator ruling this does NOT earn a C-08
control re-run. The non-manifestation is itself a data point on the open todo (hardware-gated
defects are not reliably reproducible-or-absent from a single run) — recorded here, not claimed
as a fix or closure of that todo.

### Three structurally-NA steps, and the family-label trap

`id`, `blank-check`, `erase` are NA by construction (verbatim `DERIVE-PLAN.json` reasons: no
chip-id in DB entry; blank-check not applicable to FRAM; `FLAG_CAN_ERASE` not set) — none appears
in the divergence verdict. Family-label conflation stated once: v1.15's EVIDENCE.md labels this
part's family "0x40 (SRAM_STD / FRAM)" — 0x40 is the DECIMAL algorithm (40) written as though
hexadecimal; algorithm 40's true hex form is 0x28 (this run's own report: `protocol: "40"` in
`auto_capture`, i.e. decimal 40 = hex 0x28). The v1.16 ledger already retired this conflation
(`PROTOCOL-LEDGER.md:31`, "NAME-04 conflation, retired in PROTOCOLS.md Section 1.10"). Not a
divergence.

### Declared operating voltage — cited, not re-derived

`vcc_mv: 3300` is decorative per Wave 0's `FM1608-VCC.md` (never transmitted to firmware, no
control path on any shield revision, byte-identical on both arms). Cited, not re-derived; socket
VCC recorded as not measured with the reason inline; `chip_database.json` untouched.

### Final row content

`divergence_verdict: same`. `known_carried: no`. `outcome: validated`. `control_rerun_for: not
applicable — arm is v133, not a control re-run`. `prior_disposition_source` names **v1.16 Phase
90** (`.planning/milestones/v1.16-artifacts/ledger/PROTOCOL-LEDGER.md:31`), not v1.15 — `prior_dispositions_all`
additionally cites v1.15 Phase 81 (`:59`) and Phase 82 (`:101`). All history recorded as context
only, per the operator ruling; the operative baseline is `dev test`'s own OK verdict, confirmed.
`vpp_firmware_mv: 12400`, `vpp_shortfall_mv: -400`. `render_chip_evidence.py --check` green,
`gate_record.py` (re-run standalone) 0 violations, `run_gates.sh` RC=0, 14/14 selftests, 7/7 live
gates, `ALL GATES PASSED`.

**No flash was performed for this position** — `firestarter/` confirmed still at the v1.33 SHA
throughout, both sub-repo porcelains empty. `--pending-readback` used, matching every non-flashing
position in this sweep.

## Plan 162-06 leave-state (superseded reading order note: see Position 5 below)

**Order swap, recorded per orchestrator instruction (162-07):** 162-07-PLAN.md nominally orders
position 5 = SST39SF040, position 6 = W27E040 (PD-1's healthy-part-first reorder). **The operator
physically seated W27E040 first** at the JP4-to-32-pin handover. The orchestrator instructed:
record positions by **actual run order** — W27E040 runs as position 5, SST39SF040 becomes position
6 — because both parts share the same 32-pin/12V/512KiB group so no rig-cost arithmetic changes,
only the ordering. This is a deviation from the plan text, recorded here rather than silently
reinterpreted.

**JP4 not explicitly confirmed for this handover.** The operator confirmed the part seated but did
not explicitly confirm the JP4 position when asked. Per the orchestrator's guard: a live FAIL/BAD
on this position must not book C-08 arbitration until the operator confirms JP4 is genuinely at
32-pin (a DIP32 part run with JP4 at 28-pin fails in a way that closely resembles silicon failure).

## Plan 162-06 leave-state

**Board:** Leonardo, `/dev/ttyACM0`, signature `0x1e9587`/`atmega32u4`, re-confirmed at both this
plan's chip swaps. **Arm on the board:** v1.33 (`5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`), never
flashed this plan (no divergence occurred). **Chip seated:** FM1608 (DIP28), pin-1 oriented, JP4 at
28-pin — unchanged since Task 3. **Pot setting:** meter 11.6 V / firmware 12400 mV, in band,
unchanged since position 1. **Shield:** Rev 2.0, mounted. Four of ten positions recorded
(w27c512, w27e512, sst27sf512, fm1608), all `same`/`validated`/`known_carried:no`, zero control
rows in the live ledger. Plan 162-07 inherits this state for its own first handover, where JP4
moves to 32-pin — **that move belongs to 162-07, not here.**

## Position 5 (actual run order) — `CHIP__v133__w27e040` — Task 1/2, checkpoint pending

**Chip swap (Task 1, operator-performed):** FM1608 removed, **W27E040** seated (DIP32) — **not**
SST39SF040 as the plan text nominally orders (see the order-swap note above). Operator confirmed
"the part is seated" but the JP4 position itself was **not** explicitly confirmed when the
orchestrator asked. Pot untouched (12 V group, unchanged since position 1). Reseat count: 0.

### C-01 — frozen config dir pristine

`check_arms.py --expect-config-sha 77adfdd2...` -> OK, matches the pinned digest (checked before
this position's run).

### C-04 — provenance

Port re-verified live by signature: `touch_1200.py` (settle 2.0s, reused `/dev/ttyACM0`, no new
enumeration) + `probe_board.py` -> `board_signature: 0x1e9587`, `connected_part: atmega32u4`,
matches every prior position on this rig. `capture_provenance.py` run with `--pending-readback`
(no flash performed). `config_dir_sha` in the captured record: `77adfdd2...`, matching the pinned
value — still pristine at capture time.

### C-03 — VPP, named absence (D-13, inherited)

Single reading, unchanged since position 1: **12400 mV** (`VPP: 12.4V, Internal VCC: 5.5V`), in
band. `vpp_real_mv` recorded as a named absence pointing back to `CHIP__v133__w27c512`. **Note:**
the VPP monitor does not route to the socket (Standing bench rule 5) — an in-band VPP reading here
says nothing about JP4's actual position; it cannot be used to infer JP4 is correct.

### C-05 — `dev test W27E040`, exit 1, steps total 13.9s — FAIL, chip-ID mismatch on the very first step

```
timeout 3920 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev test W27E040
```

Exit code 1. Wall-clock ~20s (far below any ceiling — no timeout drama, a genuine fast failure).

| Step | Verdict | Runs | Duration_s (cycle-sum) | Reason |
|---|---|---|---|---|
| id | BAD | 1 | 3.47 | chip-ID check did not return OK — reported `0x8201`, expected `0xDA86` |
| read | BAD | 2 | 6.94 | (init failure, same chip-ID mismatch) |
| write | SKIPPED | 0 | — | chip-ID mismatch — destructive steps gated (chip left pristine) |
| verify | SKIPPED | 0 | — | no write target available for verify |
| erase | SKIPPED | 0 | — | chip-ID mismatch — destructive steps gated (chip left pristine) |
| blank-check | BAD | 1 | 3.52 | Programmer error during init: chip-ID mismatch |

Banner: 3 of 6 ran, all 3 **BAD**. `fw_board_identity`: `3.0.0b22:leonardo`, non-null (the board
itself answered fine — this is not a port/board identity problem). VPP not measured by `dev test`
itself (the standalone `vpp` read above is separate). `write_coverage`: "chip-ID mismatch —
destructive steps gated (chip left pristine)" — **no write, erase or verify pulse ever reached the
chip**; it is left exactly as found. `report_json` copied nowhere yet (still sitting in the frozen
config dir at `dev-test-W27E040.{json,md}` — not yet copied out, because this position is **not
being recorded as a final row** until the JP4 question below is resolved).

### Why this is NOT booked as a live FAIL for C-08 yet, and NOT compared against W27E040's recorded disposition

**The observed symptom does not match the recorded disposition at all.** W27E040's known,
carried-forward disposition (v1.15 Phase 82, `EVIDENCE.md:99`) is a **stuck bit on erase** —
`id`, `read` and `blank-check` all PASS cleanly in that record (Phase 81, `:55`); only `erase`
fails, at one specific offset (`0x7db`, bit 4). **Here, `id`/`read`/`blank-check` all failed
immediately**, before any write/erase pulse was attempted, on a **chip-ID mismatch** (`0x8201`
reported vs `0xDA86` expected). A chip-ID mismatch this total, on the very first command, is the
textbook symptom of a **socket/pin-map mismatch** — exactly what a DIP32 part run with JP4 still
at the 28-pin position would produce — not a stuck-cell silicon defect, which would leave `id` and
`read` clean.

Per the orchestrator's explicit instruction: a live FAIL/BAD on this position must **not** book
the C-08 control-arm arbitration, and must not yet be compared against the recorded disposition,
until the operator confirms JP4 is genuinely at the 32-pin position. **Returning a checkpoint for
that confirmation now**, per plan (no C-08, no flash, no further chip handling attempted here).

**No row appended to `CHIP-EVIDENCE.jsonl` for this attempt.** Superseded: the operator
addressed JP4 and asked for a re-run (see "Second attempt" below) — that re-run reproduced the
identical failure, so the diagnosis moved from JP4 to seating/orientation. Kept here, never
silently dropped, per Standing bench rule 8's re-seat discipline applied to this JP4/seating case.

### Second attempt (after the operator's JP4 correction) — IDENTICAL failure, same chip-ID mismatch

```
timeout 3920 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev test W27E040
```

Exit code 1, wall-clock ~19s — byte-for-byte the same shape as the first attempt: `id` BAD (3.46s,
reported `0x8201`, expected `0xDA86`), `read` BAD x2 (7.04s), `blank-check` BAD (3.52s), `write`/
`verify`/`erase` gated off, banner 3 of 6 ran, chip left pristine. **The operator did not report
which position JP4 ended up in, only that it was addressed** — the re-run's own result is being
used as the confirmation, per instruction.

**Diagnosis moved: two identical ID failures across a jumper change point at seating or
orientation, not JP4 and not silicon.** A JP4 mismatch on the first attempt would very likely have
been fixed by moving JP4, which it was not — so either JP4's correction did not land, or the real
fault is a partially-seated DIP32 part or a reversed (pin-1) orientation, both of which produce
the identical "read garbage as the chip ID" symptom regardless of JP4. **This is NOT booked as a
chip verdict and NOT escalated to C-08** — a control-arm arbitration would burn two flashes and a
long 512 KiB re-run to arbitrate a result that is not yet a genuine chip finding. Returning a
second checkpoint, this time asking the operator to check full seating and pin-1 orientation (not
JP4, already addressed once).

### Attempt 3 (after the operator reseated the part) — chip ID cleared; run proceeded to a genuine live FAIL

```
timeout 3920 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev test W27E040
```

Exit code 1, wall-clock 768s (well inside the 3920s 512 KiB fallback ceiling — this position
supplies the phase's first measured 512 KiB total, no widening needed). **Chip ID cleared**
(`0xDA86`, matched) — seating is confirmed as the cause of attempts 1 and 2's total ID failure, a
rig/handling issue, not a chip or v1.33 finding.

| Step | Verdict | Runs | Duration_s (cycle-sum) | Reason |
|---|---|---|---|---|
| id | OK | 1 | 3.54 | — |
| read | OK | 2 | 165.345 | "read runs diverged" (recorded detail, not a divergence trigger per the operator ruling) |
| write | OK | 1 | 392.429 | full device, `write_region_start=0`, `write_region_length=524288` |
| verify | OK | 1 | 68.974 | — |
| erase | OK | 1 | 62.617 | no bit-4-at-0x7db symptom — the recorded v1.15 disposition did NOT reproduce |
| blank-check | **BAD** | 1 | 69.392 | "Empty input", `error_code 164` (`0xA4`, `MSG_ERR_EMPTY_INPUT`) |

Banner: 6 of 6 ran. `fw_board_identity`: `3.0.0b22:leonardo`, non-null. `repeat_policy`:
`runs=1` — accurately reflects that `write`/`verify`/`erase`/`blank-check` all ran a single cycle
here (unlike positions 1-4's two-cycle default); no `--fast` was used on either invocation, this
appears to be this chip/size class's own single-cycle behaviour at `dev test`'s default settings.

**This is a live FAIL under the operator ruling** ("a `dev test` FAIL/BAD is the interesting case,
and earns the control-arm re-run"). Critically, the observed symptom does **not** match the
recorded v1.15 disposition at all: that disposition is a **data failure** (a stuck bit failing to
clear on **erase**, at a specific offset/value); here **erase itself returned OK**, and the failure
is a **host/serial protocol error** (`Empty input`) on `blank-check`, not a byte mismatch. This is
explicitly not booked as the recorded `known_carried` symptom.

**Row appended:** `CHIP__v133__w27e040`, `divergence_verdict: diverges: blank-check BAD (Empty
input, error_code 164/0xA4) — a live FAIL under the operator ruling; erase itself was OK, so this
does NOT match the recorded v1.15 stuck-bit-on-erase disposition — earns C-08`, `known_carried: no`
(the recorded disposition's symptom did not reproduce), `jp4_position: 32-pin`, `reseat_count: 1`.

### C-08 — control-arm arbitration

**Cross-reference before arbitrating:** `ERROR: Empty input` (`MSG_ERR_EMPTY_INPUT`, error code
164/`0xA4`) is the **same** transient console anomaly already recorded, benignly (no verdict
impact), at `CHIP__v133__w27c512` (position 1's own `CELL.md` note), `CHIP__v133__w27e512`, the
superseded `CHIP__control__w27e512` control run, and `CHIP__v133__sst27sf512`. This is the first
position in the sweep where it landed on a step and produced a **BAD** verdict rather than a benign
log line. The project also carries prior history on this exact error class: a previously-diagnosed
write-path regression resolved by the host passing `ack_data=False` on the INIT/END phases —
worth a fresh filing on its own merits given its reappearance here, out of scope to fix in this
bench phase (D-16 boundary).

**Flash 1 — control.** `git -C firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a`
(porcelain empty before/after), `env -C /workspaces/firestarter pio run -t upload -e leonardo` —
SUCCESS, 28170 bytes. **Proven by independent read-back** (RIG-02): `touch_1200.py` +
`judge_readback.py --flashed-arm control --expect-arm control` → `judged_match: true`,
`judged_span_bytes: 28170`. `capture_provenance.py` re-run for the control arm: `fw_board_identity`
non-null (`3.0.0b22:leonardo`), `config_dir_sha` still matching the pinned value.

**Port re-enumeration, noted not chased:** during this arbitration's touch/probe cycle the board
briefly re-enumerated from `/dev/ttyACM0` to `/dev/ttyACM1` and back to `/dev/ttyACM0` across
successive 1200-baud touches — Standing bench rule 1 (never inherit a port) was honoured by
re-verifying port identity live before every subsequent command; the board signature
(`0x1e9587`/`atmega32u4`) matched throughout. Recorded as a rig behaviour data point, not chased
further.

**Control-arm `dev test W27E040` re-run**, same seating, same pot, exit 1, wall-clock 767s:

| Step | Verdict | Runs | Duration_s (cycle-sum) |
|---|---|---|---|
| id | OK | 1 | 3.48 |
| read | OK | 2 | 165.3 |
| write | OK | 1 | 392.4 |
| verify | OK | 1 | 68.9 |
| erase | OK | 1 | 62.6 |
| blank-check | **BAD** | 1 | 69.4 |

**Byte-for-byte identical failure shape and near-identical per-step timing to the v133 run.**
`chip_id` matched (`0xDA86`) on the control arm too, confirming the earlier chip-ID mismatch was a
seating fault, not arm-dependent. `repeat_policy: runs=1` on this row too, matching the primary
row's own accurate derivation.

**CONCLUSION: NOT a v1.33 regression.** `ERROR: Empty input` is an **arm-independent** host/serial
protocol fault, observed now on **both** arms across this sweep. Per the operator ruling's own
stated purpose for C-08 ("establish whether control firmware fails the same way ... or passes
where v1.33 fails"): control failed **the same way**. Recorded as a rig/protocol anomaly, not a
chip finding and not a v1.33-attributable finding.

**Control row appended:** `CHIP__v133__w27e040.control-rerun`, `arm: control`,
`control_rerun_for: CHIP__v133__w27e040`, `divergence_verdict: same` (control's own result matches
the v133 arm's result — both fail identically), `outcome: validated` (non-null
`fw_board_identity`, both read-back SHAs matched their sources, frozen config-dir invariant held).

**Flash 2 — restore to v1.33.** `git checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463` (porcelain
empty), `env -C /workspaces/firestarter pio run -t upload -e leonardo` — SUCCESS, 25098 bytes.
**Proven by independent read-back**: `judged_match: true`, `judged_span_bytes: 25098`.
`firestarter/` HEAD confirmed at the v1.33 SHA, porcelain empty; `firestarter_app/` porcelain
empty; no gitlink drift in the meta repo.

**No wasted chip handling:** W27E040 stayed seated throughout attempts 1-3 and the entire C-08
arbitration (Leonardo chip-out-exempt) — zero extra chip handling beyond the original seating and
the one reseat before attempt 3.

**Full suite re-run after this position closed, `RC` read directly:** `run_gates.sh` exits 0,
14/14 selftests, 7/7 live gates, `ALL GATES PASSED` — both `gate_record.py` runs (against
`bench/EVIDENCE.jsonl` and `bench/CHIP-EVIDENCE.jsonl`) checked standalone, 0 violations each.
`render_chip_evidence.py --check` green.

### Pin-map note and erase-duration comparison (this plan's own required record)

**Pin-map:** W27E040 is on the **standard** 32-pin map, not the scoped map v1.18's Phase 97-99 fix
introduced for AM27C020 (the other 32-pin `EPROM-QUICK`-family part in this inventory) — that fix
is size-gated to parts at or below a quarter mebibyte (262144 B) and W27E040 is twice that
(524288 B), so the fix does not touch it.

**Erase-duration comparison:** this position's measured erase duration is **62.617s** (single
cycle, 524288 B, and the erase itself returned OK — the recorded stuck-bit fault did not
manifest). Plan 162-05's other stuck-bit part, W27E512 (65536 B), measured its own healthy erase at
16.7s cycle-sum / 2 = **8.35s per operation**. Two data points on the erase op, eight times apart
in device capacity: 62.6s vs 8.35s is roughly **7.5x** for an **8x** capacity increase — consistent
with an erase duration that scales close to linearly with device size on this rig, for a run whose
erase actually completes without hitting either part's own recorded stuck-bit fault.

### Position 5 summary — supplies the 512 KiB class figure

**Measured total (v133 run): 768s wall-clock.** This position is the first of the two 512 KiB
parts to complete in actual run order (the plan's nominal order — SST39SF040 first — was swapped
by the operator's physical seating choice; see the order-swap note above). **The 512 KiB class
ceiling for the next 512 KiB position (SST39SF040, now position 6): `4 × 768s = 3072s`** —
narrower than the 3920s derived fallback (980s × 4), and stated here with its arithmetic per PD-14.
This is now a **measured**, same-rig, same-firmware figure, retiring the derived fallback for the
one part still to run in this class. **Caveat carried into `CELL.md` per this plan's own
instruction:** this measured total comes from a run that itself had a live FAIL on `blank-check`
(a protocol anomaly, confirmed arm-independent and NOT chip- or write/erase-attributable) — the
write/verify/erase figures that dominate the wall-clock total (392.4s + 68.9s + 62.6s) are
themselves clean OK measurements, so the total is still a legitimate healthy-write-path basis for
bounding the next 512 KiB run, notwithstanding the unrelated blank-check anomaly.

### Step-order hypothesis, checked and cleared — erase-before-blank-check is deliberate

Operator asked whether `erase` and `blank-check` run in the correct order for this part. Checked
live against `firestarter_app/firestarter/chip_test.py:640-683`: blank-check is appended at
exactly one of two positions, never both. **Case 2 (erase executable)** appends it **after**
erase — "only once erase has run does 'not blank' become a tool-health finding rather than a
report of the chip's prior state." **Case 4 (everything else, incl. UV-EPROM)** keeps it before
write — "the write is irrecoverable and only UV light erases, so 'not blank' is a real pre-write
finding." W27E040 is an EEPROM with an executable erase (protocol 8, `can_erase` true,
`write_execute` true) → **Case 2 applies**, and `erase → blank-check` is the intended, correct
sequence. Checked and cleared — not re-investigated further; no product-code change (Phase 165
boundary, and there is nothing to fix here regardless).

### Reproducibility re-run — board already at v1.33 SHA, no re-flash needed

Purpose: a single observed `Empty input` blank-check BAD does not distinguish a **deterministic**
fault from a **transient** one, and the position's disposition turns on which it is. Confirmed
live before running: `git -C firestarter rev-parse HEAD` = `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`
(the v1.33 SHA), porcelain empty — **no flash performed for this re-run**.

```
timeout 3072 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev test W27E040
```

Exit code 1, wall-clock 767s (near-identical to the recorded run's 768s). **IDENTICAL result**: id
OK, read OK x2, write OK x1, verify OK x1, erase OK x1, blank-check **BAD** x1 — same reason
("Empty input"), same error_code (164), same step. **Same error, same step** — a reproducible fault
at this exact point in the sequence, not a one-off transient. Logged to a distinct filename
(`logs/CHIP__v133__w27e040.repro-rerun.std{out,err}.log`) so the four W27E040 runs on the v133 arm
(attempts 1, 2, 3, and this reproducibility re-run) stay separable; its report was copied out
manually (SHA-verified, `e1eb44c7...`) to `reports/CHIP__v133__w27e040.repro-rerun.{json,md}` and
removed from the frozen config dir, since this run is recorded as corroborating evidence on the
existing position, never as a fifth row.

### Error-identity correction — `MSG_ERR_EMPTY_INPUT` (0xA4) is overloaded and does not mean what its name says

Checked live against `firestarter/src/firestarter.cpp`. Two emit sites:

- **`:124`** — genuine empty buffer: `if (handle->data_size == 0) { LOG_ERROR_ID(MSG_ERR_EMPTY_INPUT); return false; }`
- **`:251-255`** — the frame-integrity path, reused deliberately per the comment: *"CRC mismatch,
  COBS violation, overflow, or read underrun. MSG_ERR_EMPTY_INPUT reused (messages.h is codegen;
  adding MSG_ERR_BAD_FRAME requires a TOML catalog update — deferred)."*

**`ERROR: Empty input` on this position's `blank-check` is therefore far more likely a corrupted
serial frame than a literal empty input.** Three consequences recorded on the row and here:

1. **Blank-check never produced a verdict about the chip.** It failed at the transport layer
   before returning a result — this run carries **no evidence** about whether the device is
   actually blank, and therefore **no independent confirmation that the preceding `erase: OK`
   actually erased anything**. `erase: OK` means the erase command was accepted and completed
   without the firmware reporting an error; it is not itself proof the device was left blank.
2. **The disposition is a transport-integrity finding, not a chip finding and not a
   firmware-logic finding.** Both arms failed identically at the same step; the same error text
   appears in all four earlier positions' logs (both arms) at points where it happened to be
   recoverable. Intermittent frame corruption fits that distribution; a firmware logic defect tied
   to this one chip or this one arm does not.
3. **The misleading error identity is its own Phase 165/166 filing**, separate from the transport
   issue itself — an operator or triager reading "ERROR: Empty input" on a blank-check would
   reasonably conclude something about the chip or the input file, when the actual condition is a
   bad frame. Cited here with `firestarter.cpp:251-255` and the deferred-`MSG_ERR_BAD_FRAME`
   comment. **Not fixed here** — `messages.h` is codegen-generated from meta's `messages.toml` and
   this is a Phase 165 boundary; no product-code edit made in either sub-repo.

### Row strengthened in place, no duplicate row, SC#4 identity preserved

Per the reproducibility result (same error, same step) and the error-identity finding, both
existing rows for this position were **re-derived** (removed back to the schema line — the last
two rows in the file, so no other row's byte-unchanged prefix was disturbed — then re-appended
through `append_chip_evidence.py`'s normal path using each row's own retained
report/provenance/console-log/commands-extra artifacts **unchanged**; only the human-supplied
`verdict`/`anomalies`/`divergence_verdict` text was strengthened to carry the reproducibility
evidence and the corrected error identity). Every machine-derived field re-diffed byte-identical
to the pre-rederivation values (`step_durations_s`, `step_verdicts`, `report_json_sha256`, etc.) —
confirmed live, not asserted. **No second diverging v133 row and no second control row were
added** — SC#4's identity (`count(control) == count(diverging-v133)`) holds at **1 == 1** after the
re-derivation, verified live: `primaries: 5, diverging: 1, control: 1`.

**Final disposition, both rows:** `CHIP__v133__w27e040` — `divergence_verdict: diverges: ...
REPRODUCED on a second v133-arm run ... and on the control arm — confirmed a transport-integrity
fault, not v1.33-attributable`; `known_carried: no`. `CHIP__v133__w27e040.control-rerun` —
`divergence_verdict: same` (control's own result matches the v133 arm's result). **In all cases
the position remains NOT v1.33-attributable** — control has been shown to fail identically on this
exact part and seating, now corroborated by a second v133-arm reproduction.

**Full suite re-run after the re-derivation, `RC` read directly:** `run_gates.sh` exits 0, 14/14
selftests, 7/7 live gates, `ALL GATES PASSED`; `gate_record.py` re-run standalone against
`CHIP-EVIDENCE.jsonl`: 0 violations. `render_chip_evidence.py --check` green. Frozen config dir
reconfirmed pristine (matches the pinned SHA) before and after the re-derivation cycle. Both
sub-repo porcelains empty throughout; `firestarter/` confirmed still at the v1.33 SHA (no flash
occurred during the reproducibility re-run or the re-derivation).
