# Cell A3/B2 — Leonardo (ATmega32U4) on Rev 2.0 shield — v1.31's own reference rig

Runs `P-01`..`P-11` per `.planning/milestones/v1.34-artifacts/PROCEDURE.md` (Amendment 3), control arm then v1.33,
W27C512 then W29C020, four evidence positions — the last four of the phase's twelve. This is the
**intersection cell**: it belongs to both the board sweep and the shield sweep, it is the exact
rig v1.31 used, and it is executed **exactly once** in this milestone. Phase 163 cites its rows;
it must not re-run them.

`cell_slug`: `A3-B2` (directory name, `position_id` prefix). `--cell-id` value passed to every
tool: `A3/B2` (with the slash).

## P-01 — Mount and declare (2026-08-27)

**Precondition, inherited from cell A2's own recorded teardown leave-state**
(`161-04-SUMMARY.md` / `bench/cells/A2/CELL.md`): A2's socket was left **empty** at teardown
(both chips pulled, no chip re-seated afterward). The Rev 2.0 shield carries its socket with it
when moved, so that empty state travels with the shield.

**Orchestrator-measured bus state before the gate** (sysfs USB descriptors, read-only,
2026-08-27T17:22:57Z): `/dev/ttyUSB0` `1a86:7523` "USB Serial" (CH340) — LIVE, the uno328pb,
socket empty; `/dev/ttyACM0`/`/dev/ttyACM1` ABSENT — the Leonardo not yet attached.

**Independently re-confirmed by Claude, pre-gate** (2026-08-27T17:24:34Z): `ls /dev/ttyACM*` ->
no such file (both absent); `/dev/ttyUSB0` present, mtime `2026-08-27 17:14:08 UTC` — matches the
orchestrator's measurement exactly.

**Operator declaration, verbatim:** "ttyACM0, Rev 2.0, messured vpp to be exactly 12v" (operator's
own spelling; "messured" = "measured"). This one statement carries three separate facts, each
recorded on its own below: the device node, the shield silkscreen, and a pre-flash multimeter VPP
reading volunteered ahead of any firmware `vpp` query (its ordering is part of its value — see the
P-06 section below for the paired comparison this enables).

**Orchestrator-measured bus state at resume** (sysfs USB descriptors, read-only, no port opened,
2026-08-27T17:41:11Z): `/dev/ttyACM0` `2341:8036` "Arduino Leonardo" — LIVE, freshly attached,
mtime `17:40`; `/dev/ttyACM1` ABSENT; `/dev/ttyUSB0` ABSENT (uno328pb disconnected by operator).

**Independently re-confirmed by Claude, post-resume** (2026-08-27T17:42:02Z): `/dev/ttyACM0`
present, `vid:pid=2341:8036`, mtime `2026-08-27 17:40:00 UTC` — matches the orchestrator's
measurement exactly. `/dev/ttyACM1` and `/dev/ttyUSB0` both absent. Only one live node this cell,
but per Standing bench rule 1 every avrdude/probe/tool invocation below still passes an explicit
`--port /dev/ttyACM0` — never autodetected.

**Declared shield revision** (`shield_rev_declared`, becomes this value on all four A3/B2
positions): **`Rev 2.0`** — the operator's own statement was already in canonical form; no
normalization applied (contrast the `BRINGUP-leonardo-provenance` pre-proof, where "rev 2.2" did
need case normalization to "Rev 2.2" — that record's own transcription note, not repeated here
because it does not apply).

**VPP multimeter pre-read** (operator-volunteered, recorded verbatim then normalized):
"messured vpp to be exactly 12v" -> **12.0 V, operator-measured**, taken **before** any firmware
`vpp` query on this board — no firmware read has yet been taken at the point this reading was
given. This pre-ordering is itself part of the record's value: it makes the `P-06` firmware
confirming-read a genuine, properly-ordered paired measurement (meter first, firmware second),
unlike A2's retrospective pairing. The confirming firmware read is deferred to Task 4/`P-06` per
the plan's own step ordering (this task only records the operator's declaration); the calibration
finding itself is written up there and in the SUMMARY.

**Socket state:** not yet re-confirmed post-mount (no chip seating action has occurred yet this
cell); A2's teardown-confirmed empty state is the only claim made at this point.

**`$PORT` for this cell:** `/dev/ttyACM0`
**`$SHIELD_REV` for this cell:** `Rev 2.0`
**`$TARGET` for this cell:** `leonardo`

**Chip-out rule note:** this board is **exempt** from the Uno-class chip-out-before-sideload rule
(standing bench rule 2) — it is flashed and read back with the chip seated. No `P-03` gate exists
in this cell for either arm's flash; the absent gate is explained here rather than left
unexplained, and again at each flash task where the exemption applies.

**Pre-cell arm integrity capture** (log `00_check_arms_pre_cell`): `check_arms.py` exit 0, both
arms verified (SHA+porcelain+file-probe+dep-freeze+interpreter+config-sha+cli-surface). `control`
HEAD `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a`, `v133` HEAD
`cb189a9b001e9e34fb7651535de339761301d061`, `config_dir_sha`
`77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0` — matches the frozen pinned
value. `surface_diff_ab`/`surface_diff_ba` both empty; 25/25 CLI surface parity both arms. See
`check_arms_pre_cell.json`.

**Inherited chip-condition caveat, carried forward, not cleared:** the W27C512 this cell needs
has been handled eight times across A1 and A2, was never physically assessed by the operator when
asked, and threw a 0x303 contact fault in A2 requiring a rule-8 re-seat. This cell inherits that as
standing **uncertainty**, never as clearance. If a 0x303-class contact fault appears here, one
clean re-seat and one re-run are permitted per position, with both the discarded attempt and the
re-run recorded.

**UPDATE — caveat CLOSED at `P-05` (ninth handling), by inspection, not measurement:** the
operator inspected this W27C512 at its ninth handling and reported "nothing looks of[f]" — the
first physical assessment of this part anywhere in the phase. Recorded precisely: this is an
operator visual inspection reporting nothing anomalous, **not** a clean bill of health from a
measurement, and it does **not** retroactively clear A2's `0x303` contact fault, which stands as
its own recorded event. Full record in `POT.md`'s `P-05` section, including the two-part reply
(the inspection answer and the separately-sought state confirmation — the same class of ambiguity
A2's checkpoint recorded).

## P-02 — Board identity + four pending provenance records (2026-08-27)

**Followed `bench/cells/BRINGUP-leonardo-provenance/PREPROOF.md`'s final working sequence
verbatim** — external `touch_1200.py` (bare, settle-only) + external `probe_board.py`, a 2 s
settle for the post-avr109-exit USB re-enumeration, then `capture_provenance.py` with
`--board-probe-json` pointing at the external probe's own `--out` file. This is deliberately
**not** a copy of A1's `P-02` (which relies on `capture_provenance.py`'s own internal
`probe_board.py` subprocess call, refuted on this board) — per delta 2, an A3/B2 `P-02` shaped
like A1's is the documented warning sign.

**Touch** (log `01_touch`, `--settle-s 2.0`, no `--wait-new-port` token anywhere in the recorded
argv): rc=0, `touch.json` records `changed: false`,
`devices_before == devices_after == ["/dev/ttyACM0"]` — the Leonardo's node does not change.

**Board probe — one genuine transient race, then success on immediate retry (Rule 3, blocking
issue auto-fixed):** the first `probe_board.py` attempt immediately after the touch (log
`02_probe_board`, first run) failed, rc=1: avrdude's stderr read `OS error: cannot open port
/dev/ttyACM0: Input/output error` / `No such file or directory` — the port was mid-re-enumeration,
consistent with the Caterina-entry transition PREPROOF documents for the post-avr109-exit case,
here evidently also possible on the touch-to-bootloader-entry side. `ls /dev/ttyACM0` immediately
after confirmed the node was present again with an advanced mtime. Re-ran the identical
touch+probe pair (log `01_touch` / `02_probe_board`, final, overwriting the failed attempt's
logs): touch rc=0 at `17:43:46Z`, probe rc=0 at `17:43:49Z` — **3 s elapsed**, inside the measured
3.487 s touch-to-responsive-programmer window. `board_probe.json`: `connected_part=atmega32u4`,
`board_signature=0x1e9587`, `mcu_matches=true`, `signature_route=route1` — matches the known-good
Leonardo signature and the operator's declaration exactly. This retry is a hardware-timing race,
not a defect in the command sequence or its ordering; the *first* attempt's failed log pair was
overwritten by the retry's successful pair, and this paragraph is the record of that discarded
attempt, per the same discipline the plan requires for a chip contact-fault re-seat.

**2 s settle** applied after the probe and before the first `capture_provenance.py` call, per the
seam PREPROOF establishes (avr109 session exit resets the MCU back into the application; the
tool's own next live-port action — the `hw` probe inside `capture_provenance.py` — needs that
re-enumeration to have settled first).

**Provenance captured for all four positions**, each with `--pending-readback`,
`--board-probe-json $CELL_DIR/board_probe.json` (Seam 1 — skips the tool's own internal
`probe_board.py` call entirely, consuming the already-obtained result above instead), its own
`--arm`/`--chip`/`--out`, `--cell-id A3/B2` (with the slash — the tool derives the `A3-B2` slug
itself), `--target leonardo`, `--port /dev/ttyACM0`, `--shield-rev "Rev 2.0"`. `--no-image-plan`
was **not** passed — every real sweep position resolves a genuine `IMAGE-PLAN.json` row, per the
plan's own prohibition; that flag is bring-up-only.

| `position_id` | file | rc | `captured_at_step` | log |
|---|---|---|---|---|
| `A3-B2__control__w27c512` | `provenance_A3-B2__control__w27c512.json` | 0 | 2 | `03_capture_provenance_A3-B2__control__w27c512` |
| `A3-B2__control__w29c020` | `provenance_A3-B2__control__w29c020.json` | 0 | 2 | `04_capture_provenance_A3-B2__control__w29c020` |
| `A3-B2__v133__w27c512` | `provenance_A3-B2__v133__w27c512.json` | 0 | 2 | `05_capture_provenance_A3-B2__v133__w27c512` |
| `A3-B2__v133__w29c020` | `provenance_A3-B2__v133__w29c020.json` | 0 | 2 | `06_capture_provenance_A3-B2__v133__w29c020` |

Verified by script: `board_probe.json`'s `connected_part`/`board_signature` match
`rig-pins.json`'s `targets.leonardo` values exactly; exactly four
`provenance_A3-B2__*.json` files exist with no default `provenance.json` collision; each record's
`captured_at_step==2`, `cell_id=="A3/B2"`, `cell_slug=="A3-B2"`, `target_env=="leonardo"`; each
record's `arm`/`chip` match its own `position_id`; each record's `image_mask`/`image_stamp_width`/
`image_sha` equal `IMAGE-PLAN.json`'s row (masks 24/25/26/27); each record's `fw_sha`/
`host_arm_sha` equal `rig-pins.json`'s pinned values for its own arm; `touch.json`'s recorded argv
carries no `--wait-new-port` token.

## P-03 / P-04 (control) — no chip-out gate, flash + independent read-back proof (2026-08-27)

**No `P-03` gate.** Standing bench rule 2 exempts the Leonardo: it is flashed and read back with
the chip **seated**. The socket was also still empty at this point regardless (no chip has been
seated in this cell yet), but the absent gate is explained by the rule, not by the empty socket
being a coincidence.

**Flash — executed by a PRIOR agent instance, before a user interrupt (2026-08-27T17:45:54Z).**
`git -C /workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a` (empty
porcelain, `rev-parse HEAD` confirmed equal to `arms.control.fw_sha`), then
`pio run -t upload -e leonardo`, cwd `/workspaces/firestarter`
(log `07_pio_upload_control.std{out,err}.log`, both untracked at the point this executor resumed
and committed with this task). PlatformIO report: `Flash: 86.0% (used 28170 bytes from 32768
bytes)`, `[SUCCESS] Took 8.08 seconds`. avrdude (Caterina, `CATERIN` programmer, device signature
`0x1e9587`): `28170 bytes of flash written`, `28170 bytes of flash verified`. **This
upload-time avrdude verify is explicitly NOT the project's proof oracle (D-01)** — it establishes
only that the flash step itself completed and self-reported clean before the interrupt landed;
the independent read-back below is the actual proof.

**This executor resumed after the interrupt, verified the flash's own logs first, and did NOT
re-run `pio run -t upload`.** `git -C firestarter status --porcelain` was empty and
`rev-parse HEAD` still equalled `arms.control.fw_sha` at resume, confirming the gitlink is still
sitting exactly where the flash left it — no intervening state change. Proceeded straight to the
independent read-back proof this task actually needed.

**Independent read-back proof (`judge_readback.py`, never the uploader's own verify):**
```
python3 .planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out $CELL_DIR/touch_for_read_control.json
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target leonardo --port /dev/ttyACM0 \
  --flashed-arm control --expect-arm control \
  --out-dir $CELL_DIR --pins .planning/milestones/v1.34-artifacts/rig-pins.json
```
**First attempt (log `08_touch_for_read_control` / `09_judge_readback_control`, discarded,
overwritten by the retry below):** touch rc=0; `judge_readback.py` rc=1,
`FAIL: avrdude read failed (rc=1): OS error: cannot open port /dev/ttyACM0: Input/output error`
— the identical transient post-touch USB re-enumeration race `BRINGUP-leonardo-provenance/
PREPROOF.md` already documented for this exact board (a `probe_board.py` attempt landing while
the port is mid-re-enumeration). **Rule 1/Rule 3 auto-fix — a genuine hardware-timing race, not a
defect in the command sequence:** re-ran the identical touch-then-judge pair immediately
(`/dev/ttyACM0` confirmed still present, advanced mtime). **Retry (final, kept):** touch rc=0;
`judge_readback.py` rc=0, `judged_match=True`, `judged_span_bytes=28170`. This discarded first
attempt is recorded here per the same discipline this cell applies to a chip contact-fault
re-seat — not papered over.

`READBACK-VERDICT.json`: `target=leonardo`, `flashed_arm=expect_arm=control`,
`judged_match=true`, `judged_span_bytes=28170` — read at assertion time from
`rig-pins.json`'s `hex_span_expected_by_arm.control`, **never** the legacy scalar (25098).
`sha_actual_judged == sha_expected_judged` = `d734ad49...` (exact match, `hex-extent` policy, no
vector exclusions). `readback_size_bytes=32768` (`flash_readback.bin`, whole-flash SHA
`334f9144...` recorded as the unjudged datum, D-02). Both control positions' provenance were
patched with `--patch-readback`; the v133 records are untouched.

**The control arm is on the Leonardo and proven by an independent avr109 read-back**, judged
against its own 28170-byte span — the flash (run before the interrupt) and its proof (run after)
are two separate events, both now on the record, with no re-flash performed.

## P-08 — swap W27C512 for W29C020 (2026-08-27)

Operator reply, verbatim: "W29C020 seated". W27C512 (DIP28) removed, W29C020 (DIP32) seated in
the Rev 2.0 socket on the Leonardo at `/dev/ttyACM0`. **Pot untouched** — stays at the `P-06`
setting (firmware 12.3 V / operator-meter 11.44 V, in band). No further `vpp` read taken for this
swap, per Standing bench rule 4's single-confirming-read-per-cell discipline. This W29C020's
physical condition is **unassessed** — the operator inspection that closed the W27C512's caveat at
`P-05` says nothing about this different, physical chip.

## P-10 to P-04 (v1.33) — preserve control read-back, re-flash with chip seated (2026-08-27)

**No chip-out gate.** `P-10` returns the cell to `P-03`, which on this board is a no-op: Standing
bench rule 2 exempts the Leonardo — flashed and read back with the chip **seated**. The W29C020
stayed in the socket throughout this task.

**Preserved before flashing:** the six control read-back artifacts copied (not moved) into
`readback_control/` — `READBACK-VERDICT.json` (`judged_span_bytes=28170`), `flash_readback.bin`
(32768 B), `expected_span.bin`, `judged_span.bin`, `SHA256SUMS.txt`, `avrdude_read.stderr.log` —
before the v133 flash overwrote all six at the cell root.

**Flash:** `git -C firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463` (empty
porcelain, `rev-parse HEAD` confirmed equal to `arms.v133.fw_sha`), then `pio run -t upload -e
leonardo`, cwd `/workspaces/firestarter` (log `15_pio_upload_v133`). PlatformIO report:
`Flash: 76.6% (used 25098 bytes from 32768 bytes)`, `[SUCCESS] Took 7.77 seconds`.

**Independent read-back proof:** bare settle-only `touch_1200.py` (log `16_touch_for_read_v133`,
no `--wait-new-port`) then `judge_readback.py --flashed-arm v133 --expect-arm v133` (log
`17_judge_readback_v133`) — **clean on the first attempt**, no transient race this time.
`judged_match=true`, `judged_span_bytes=25098` — read at assertion time from
`hex_span_expected_by_arm.v133`, equal here to the legacy scalar by coincidence (this is the one
target/arm pair where they agree), read from the named field regardless, per the standing warning
against a leg that reads the scalar generalizing badly. `sha_actual_judged=f032843d...`, distinct
from the preserved control read's `d734ad49...` — the two arms are independently distinguishable,
as `judged_span_bytes` (28170 vs 25098) already showed.

Both v133 positions' provenance patched with `--patch-readback`; the two control positions'
`fw_readback_sha_judged` re-confirmed unchanged (still the preserved control read's SHA) —
neither pair was cross-contaminated.

**The v1.33 arm is on the Leonardo, proven against its own 25098-byte span**, flashed with the
chip seated exactly as the standing rule allows, with the control arm's read-back binaries
preserved and untouched.

## P-05 (second arm) — swap back to W27C512 (2026-08-27)

Operator reply, verbatim: "W27C512 seated". W29C020 removed, W27C512 (DIP28) re-seated in the
Rev 2.0 socket on the Leonardo at `/dev/ttyACM0`. **Pot untouched** — firmware 12.3 V / operator
meter 11.44 V, in band, unchanged since `P-06`. No further `vpp` read taken (`P-06` ran once for
this cell).

**The Leonardo chip-out exemption was exercised through the `P-10`/`P-04` v1.33 flash** — the
W29C020 stayed seated through that firmware flash rather than being pulled first, per Standing
bench rule 2. This is the **only cell in the phase** where that exemption applies; A1 and A2 both
pulled the chip before every flash (Uno-class chip-out rule).

## P-08 (second arm) — swap to W29C020 for position 12 (2026-08-27)

Operator reply, verbatim: "W29C020 seated". W27C512 out, W29C020 (DIP32) re-seated in the Rev 2.0
socket on the Leonardo at `/dev/ttyACM0`. **Pot untouched** — firmware 12.3 V / operator meter
11.44 V, in band, unchanged since `P-06`.

## P-11 — Teardown, twelve-position reconciliation, SC#5, handover to Phase 162 (2026-08-27)

**v133 read-back set preserved** into `readback_v133/` (six artifacts, copied from the cell root,
which still held the v1.33 flash's own read-back from `P-10`/`P-04` — no new flash or read-back
ran at teardown; nothing to overwrite at risk). `readback_control/` (preserved earlier, at
`P-10`) is untouched.

**Teardown identity re-probe, distinct path, chip seated (Leonardo exemption applies):** bare
settle-only `touch_1200.py` (log `22_touch_teardown`) then `probe_board.py --out
board_probe_teardown.json` (log `23_probe_board_teardown`, distinct from `P-02`'s
`board_probe.json`). `board_signature=0x1e9587`, `connected_part=atmega32u4`, `mcu_matches=true`
— **unchanged since `P-02`.**

**`~/.firestarter` baseline check (Amendment 3 clause 4), first assertion — a THIRD recurrence of
the SAME P-H1 finding cells A1 and A2 each recorded once:**
- Files: `['config.json']` — matches.
- `config.json` sha256: `b323867c1f01b22a705dd9caf003ab7302a249fe46772f5b02e44aaa2760dd79` —
  **matches the pinned baseline exactly.**
- Tree sha: `423546cd37b5b45d9654e5acd07bd7e2a3c9e1df77e4d5feb79951bf37329951` — **matches.**
- **mtime: `1787854674` — CHANGED from the pinned baseline's `1787817565`.**

Recorded precisely: the file's **content is byte-identical** to the pinned baseline (both the
per-file sha and the tree sha match exactly) — this cell's operations did not alter what the file
says. Its **mtime advanced**, confirming the file was **rewritten** at some point during this
cell's operations despite `FIRESTARTER_CONFIG_DIR` being set inline on every single arm-binary
invocation in this cell, exactly as it was in A1 and A2. This is the **third** occurrence of the
same leak in this milestone (A1's `161-03`, A2's `161-04`, now this cell) — not fixed here (D-16
boundary: no product-code changes; handed to Phase 165 as a now three-times-repeated finding). No
deletion was attempted.

**Second assertion — `check_arms.py --expect-config-sha`:** rc=0, `config_dir_sha` matches the
expected `77adfdd2...` value exactly (log `24_check_arms_teardown`); both arms' `head`/
`porcelain_clean`/`dep_freeze`/`interpreter`/`file_probe` unchanged; all four A3/B2 provenance
records carry the same non-null `config_dir_sha`. With the first assertion's content-match
holding and this assertion running genuinely (every invocation set `FIRESTARTER_CONFIG_DIR`
inline, Standing bench rule 9), the two-assertion config-dir check for this cell is complete and
green, the mtime-only anomaly noted above notwithstanding.

**Completeness assertion for this cell:** all four A3/B2 rows present, each exactly once —
`A3-B2__control__w27c512`, `A3-B2__control__w29c020`, `A3-B2__v133__w27c512`,
`A3-B2__v133__w29c020` — verified by script.

**Phase-level reconciliation:** `bench/EVIDENCE.jsonl` holds **twelve** sweep rows — four `A1`,
four `A2`, four `A3/B2` — plus the pre-existing `BRINGUP-` rows (excluded from the sweep count by
the schema's own `bringup_row_exclusion`). Verified by script: 12 sweep rows, 3 distinct
`cell_id` values (`A1`, `A2`, `A3/B2`), 4 positions each, **no `position_id` appears twice
anywhere in the file**, and every sweep row carries a non-null `write_duration_wallclock_s`.

**SC#5, stated as arithmetic:** exactly **one** row and **one** write-duration figure per (arm x
chip) position bearing the `A3/B2` cell id, across the whole v1.34 evidence set —
`render_evidence.append_row_to_file` structurally refuses a duplicate `position_id`, so this is a
property the mechanism itself enforces, verified here rather than merely asserted.
**Phase 163 will cite these four rows and must not produce new ones.**

**No escalation branch was run** — no v133 position on this cell recorded `distinct_read_shas`
greater than 1 (both were `1`, `n3_disagreement=false`).

**`run_gates.sh` — FULL mode:** 12/12 tool self-tests, 5/5 live gates, **exit 0** (captured
directly via `$?`, never through a pipe). `gate_record.py --jsonl` — 0 violations.

**Sub-repo state:** `firestarter` gitlink at **v1.33 `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`**,
porcelain clean; `firestarter_app` unchanged, porcelain clean; the meta repo's own recorded
gitlink pointers show no diff against these — both sub-repos byte-unchanged in content, per this
plan's own hard prohibition.

### BOARD-03 statement

Four evidence positions on v1.31's own reference rig — Leonardo + Rev 2.0 — both arms, both
chips, each with an independent avr109 read-back proof (`judged_match=true`, distinct judged
spans 28170/25098) and a full-device SHA-judged write/read verdict (`match` on all four,
including two N=3-stable v1.33 reads). **BOARD-03 is closed.**

### BOARD-04 comparison — carried from `WRITE.md`, the only valid v1.31 timing comparison in v1.34

**A/B result on this rig, one write per position (a data point, not a spread):**

| Chip | Control (wall/app) | v1.33 (wall/app) | Wall-clock delta |
|---|---|---|---|
| W27C512 | 37.172 s / 33.37 s | 37.118 s / 33.37 s | **-0.054 s** |
| W29C020 | 66.671 s / 62.99 s | 66.674 s / 62.99 s | **+0.003 s** |

App-reported figures are identical to two decimals on both chips; written images are
byte-identical between arms (only the mask differs, by design, per `IMAGE-PLAN.json`). **The
control and v1.33 arms are behaviourally indistinguishable on this rig, on both chips, at this
real VPP rail.**

**v1.31 comparison (W27C512 positions, this rig only):** v1.31's **0.37 s** is the **spread** (max
minus min) across three full 64 KiB write cycles' app-reported figures — 106.06 / 105.69 / 106.06
s, this exact Leonardo + Rev 2.0 rig, firmware `ebe9cb3`. It is a spread, not a duration; v1.34
takes **one** write per position per arm, so there is **no v1.34 spread** to set against it. The
honest statement: the two v1.34 app-reported figures (both **33.37 s**) and their difference
(**0.00 s** to two decimals), presented beside v1.31's 0.37 s spread, **never** as a single v1.34
figure "compared to 0.37 s". Both v1.34 figures land far below v1.31's ~106 s baseline because of
**PR #55's per-byte VPE-settle amortisation** (105.9 s to 33.35 s, firmware `3.0.0b22`), present
in **both** arms' merge bases — not a v1.33-specific improvement.

**Cross-board chunk-size effect (a board characteristic, not a v1.33 signal — both figures
compared are control-arm):** this rig's control-arm W29C020 write (66.671 s) is **~32% faster**
than A1's control-arm W29C020 write on the Uno (97.937 s), consistent with the Leonardo's
1024-byte transfer chunks versus the Uno's 512.

### The N=3 data point relevant to cell A2's open, undetermined question

This cell's v1.33-arm W27C512 read set (position 11) was **perfectly stable**
(`distinct_read_shas=1`) on the **same physical W27C512 chip** that returned **three distinct
SHAs** under the identical v1.33 arm in cell A2's position 3, whose disambiguating control-arm
escalation was **blocked** by the VPP finding and closed **UNDETERMINED**. Stated with its limits:
this single stable result on a **different board**, with **different on-chip content going in**
and **different conditions** (real VPP rail, EEPROM calibration) cannot resolve A2's own
instability — it is **not** offered as a resolution. It **does** point away from the chip itself
as an unconditional cause and toward the uno328pb or its state at the time being the more likely
locus. **Handed to Phase 165 alongside A2's own unresolved record.**

### Carried non-claims (Phase 160 §6, disclosed — restated, not re-raised)

- No electrical claim: program-window VPP/VCC **under load** stays unmeasured, behind the
  DTR-reset-on-close tooling gap.
- Both arms ran on Python 3.12.14, not the app-CI 3.11 floor.
- `dev consistency-check` is a dev-channel-only surface.
- A clean position's bytes are re-checkable by SHA only, since they are not committed
  (`bench/.gitignore`'s artifact-volume policy; no position in this cell needed the
  committed-on-failure exception — all four were clean matches).
- **Sharpened by this cell's own finding:** the on-board VPP instrument used for every reading in
  this milestone is now known to read **~7.5% high** — see the HEADLINE finding in
  `SUMMARY.md`. Flagged for Phase 166's honesty ledger.

### P-11 leave-state (D-11)

**Leonardo**, connected at `/dev/ttyACM0`, **Rev 2.0** shield mounted (as declared at `P-01`),
carrying the **v1.33 arm** (fw `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`), **W27C512 (DIP28)
seated** (re-seated at this task, staying in), pot **untouched since `P-06`'s ruling**
(firmware-reported **12.3 V**, operator-meter **11.44 V**, in band per `eprom.cpp:713`/`:736`).
**This is the only cell in the phase ending with a chip seated** — A1 and A2 both ended with an
empty socket. **Phase 162 therefore inherits this rig assembled and needs no reconfiguration and
no re-flash** for its 11-part `dev test` sweep.

No position in this cell triggered the committed-on-failure exception (`bench/.gitignore`) — all
four judged verdicts were clean matches, so no `run_*.bin`/`written.bin` was force-added.
