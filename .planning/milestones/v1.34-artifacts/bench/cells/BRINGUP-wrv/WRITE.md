# BRINGUP-wrv — Write Record (Plan 12, Task 1)

**Cell:** `BRINGUP-wrv` (Uno + Rev 2.0, provenance/bring-up position — excluded from the
20-position sweep reconciliation per its `BRINGUP-` cell-id prefix)
**Position id:** `BRINGUP-wrv__v133__w27c512`
**Board state entering this task:** Uno (ATmega328P) + Rev 2.0 shield, v1.33 arm flashed and
proven on-device (plan 11, `READBACK-VERDICT.json`: `judged_match=true`,
`judged_span_bytes=22952`), **W27C512 seated**, pot confirmed at 12.0V by one reading, port
`/dev/ttyACM0`. No avrdude firmware operation (upload, read-back, or signature probe) ran
against this board while the chip was seated.

## Stated target (from plan 11's gate, carried forward)

**12.0 V (12000 mV)** — `rig-pins.json` `chips.w27c512.vpp_mv`, identical to `chips.w29c020.vpp_mv`.

**Operator's report (plan 11, verbatim):** `"pot set"`.

**Single confirming reading (plan 11, Claude-taken, exactly one):** VPP 12.0 V, internal VCC
4.7 V — in band, matching the target exactly. No operator instrument reading was provided; the
single confirming reading is the only rail measurement recorded for this cell. See
`POT.md` for the full record, including the deviation note about the `vpp` CLI's continuous-print
behaviour. No pot re-adjustment was needed or performed in this task (the guard did not fire —
see below), so no new confirming reading was taken here; the plan-11 reading stands for the
whole cell per `PROCEDURE.md` P-06 ("the pot is set once per cell, not once per chip").

## Step 1 — regenerate and verify the image

Generator invocation (literal argv, cwd `/workspaces`):

```
python3 .planning/milestones/v1.34-artifacts/tools/gen_addr_image.py 65536 36 .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin --stamp-width 16
```

**Generator's printed verdict line (verbatim):**

```
.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin: 65536 bytes, mask=0x24, stamp_width=16, sha256=fff15da9f46d04b366b4b8bf42a91cd2f67a8f57a1cfccac26351c5325b35726, 0xFF_count=128
```

- **mask:** `0x24` (decimal `36` — `bench/IMAGE-PLAN.json`'s recorded value for
  `BRINGUP-wrv__v133__w27c512`, `36`, is the decimal spelling of `0x24`; the mask-assignment
  rule's `0x10 + index` range is expressed as decimal integers in that file throughout)
- **stamp_width:** `16` (this part is 65536 B / 16 address bits — the full-space width per
  `IMAGE-PLAN.json`'s `stamp_width_rule`)
- **sha256:** `fff15da9f46d04b366b4b8bf42a91cd2f67a8f57a1cfccac26351c5325b35726` — **verified equal**
  to the hash recorded for this position in `bench/IMAGE-PLAN.json` (`sha256` field of the
  `BRINGUP-wrv__v133__w27c512` entry) before the file was written to the chip. Written image size
  is exactly 65536 bytes (`len(data) == row['size_bytes'] == 65536` — verified).

## Why a distinct per-position image is the insurance here

This project has standing recorded evidence
(`reference_devtest_write_repeat_emits_no_pulses_27c.md`) that a second write to an
already-correct chip can be a near-no-op on a large fraction of the inventory (LOOP-06 skips
bytes that already match), because the write path only re-programs bytes that differ from what
is already on the chip. If this position's image happened to be the same bytes some other
position (or some earlier bring-up run) already wrote to this exact chip, this write could be a
near-no-op — emitting few or no programming pulses — and the read-back would still verify green,
because the chip already held the right bytes for the wrong reason. A distinct,
address-attributable image per position (this cell's own `mask=0x24`, verified against its own
recorded hash) makes that scenario detectable rather than a silent coincidence: a stale-content
pass would read back as the sha of a *different* mask's image, immediately recognisable against
the recorded per-position hash table in `IMAGE-PLAN.json`, rather than passing unnoticed. In this
run the read-back did land on `written.bin`'s own sha (see Task 2 / `WRV-VERDICT.json`), so the
insurance was not needed to catch a problem here — but it is what makes that a *proven* absence of
the failure mode rather than an assumed one.

## Step 2 — physical-part identity note (shared DB row)

The `w27c512` database row (`part_number: "W27C512,W27E512"`) is **shared with W27E512**, one of
this project's four known-dead parts (stuck erase bit @0x3d, D-32 silicon wear) — same DB row,
different physical silicon. `provenance.json`'s `chip` field is `"w27c512"` and `chip_package` is
`"DIP28"`, naming the **physical part actually seated on this bench** (confirmed by the operator
across plans 11 and this cell's continuity — no chip swap occurred between plans), not merely
"whichever part this DB row happens to also cover." No W27E512 was ever seated on this board in
this cell; the record's silence on W27E512 is a because-it-does-not-apply silence, stated
explicitly here rather than left to be inferred.

## Step 3 — the write

**Literal command (cwd `/workspaces`):**

```
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 write w27c512 .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin
```

No `--force`/`-f`, no `-b`/`--no-blank-check`, no `--skip-erase` — checked against
`rig-pins.json`'s `forbidden_flags` list; none present. `FIRESTARTER_CONFIG_DIR` is set inline on
this command's own line, never by a session-level `export` (standing bench rule 9).

**Exit code:** `0` (success).

**Wall-clock duration (judged measure), monotonic clock around the whole command:**
`41.010 s` (start `2026-08-27T08:18:59.924Z`, end `2026-08-27T08:19:40.935Z`).

**App's own reported duration (second, unjudged datum):**
`37.48s` — from the command's own stdout line `Write to W27C512 successful (37.48s).`

The two durations differ (41.010s wall-clock vs. 37.48s app-reported) because the wall-clock
measure includes process start-up and the serial connect handshake (`Connecting...Connecting...
OK`), which the app's own in-process timer does not — this is the exact distinction
`PROCEDURE.md`'s write-duration-definition section calls out, and it is why wall-clock, not the
app's figure, is the judged measure here.

**High-voltage init guard:** did **not** fire. No `VPP is high: ... > 12.0V` line appears
anywhere in the captured stdout/stderr (`logs/10_write_w27c512.stdout.log`,
`logs/10_write_w27c512.stderr.log`) — the pot was already in band from plan 11's confirming
reading, so no re-adjustment or restart was needed.

**Re-seat:** none requested, none performed. No contact-fault symptom (blank/`0x303`-class
reading) occurred anywhere in this task.

**Write failure:** none. The write succeeded cleanly on the first attempt.

## Logs

- `logs/09_gen_addr_image.stdout.log` / `.stderr.log` — the generator invocation
- `logs/10_write_w27c512.stdout.log` / `.stderr.log` — the write invocation (stderr carries the
  tqdm progress-bar stream, consistent with the measurement-traps note that write-progress is
  time-keyed per block and carries no reliable per-byte rate)
