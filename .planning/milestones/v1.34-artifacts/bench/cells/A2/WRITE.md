# Cell A2 — WRITE.md

Per-position write observations, control arm first then v1.33 — the record Backlog 999.2's
prediction is judged against, not asserted from.

## Position 5 (1 of 4): `A2__control__w27c512`

**Command:** `timeout --signal=INT 165 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config
/workspaces/.v1.34-arms/control/.venv/bin/firestarter -p /dev/ttyUSB0 write w27c512
reads/A2__control__w27c512/written.bin` (log `12_write_control_w27c512`).

**Ceiling:** 165 s (4x the measured healthy 41.010 s baseline). **Basis: not needed** — the write
did not run anywhere near the ceiling; the app's own internal per-response communication timeout
fired first, at 15.813 s wall-clock. Wrapper exit code: **1** (the process exited on its own with
an error; the external `timeout` wrapper's SIGINT never had to fire — **124 was NOT the exit
code**, so the D-08 ceiling itself was not what ended this attempt, the app's own internal
serial-response timeout was).

**Wall-clock:** 15.813 s (measured by `date +%s.%N` either side of the write command).
**App-reported figure:** `not measured — the write failed before any success line
("Write to {CHIP} successful ({t:.2f}s)") was emitted; the host printed a failure line instead
(quoted below)`.

**The stop point, precisely.** The host prints two separate `tqdm` progress bars for this
operation — one for the protocol's INIT phase, one for MAIN (per `eprom_operations.py`'s
`_execute_phase()`/`_main_phase_simple()` structure, three-phase INIT/MAIN/END protocol per
project `CLAUDE.md`). The **first** bar (INIT) reached **100% (`0x10000/0x10000 bytes`)** — the
full 65536 B image was queued/transferred to the host-side protocol layer without incident. The
**second** bar (MAIN — the actual chip-programming phase) restarted at **0%** and reached only
**`1%|  | 0x0200/0x10000 bytes`** (512 bytes — exactly one Uno-class buffer block,
`_write_block_timeout()`'s own 512 B floor) before the host's serial layer raised a timeout. **The
last progress frame, verbatim:** `1%|          | 0x0200/0x10000 bytes` (appeared twice in
succession in the captured stderr, then no further frames).

**Backlog 999.2 predicted a hang "deterministically on the FIRST program block."** What was
**observed** here: the MAIN phase's progress stopped at exactly the first block boundary
(0x0200 = 512 B), matching that prediction's block-position claim precisely. It is **not** a
hang without termination, though — the app's own internal per-response read timeout
(`serial_comm.py get_response()`, `DEFAULT_RESPONSE_TIMEOUT`/the firmware-advertised MAIN-phase
budget) fired and the process exited cleanly with an error, well before the external 165 s
D-08 ceiling was ever approached. This is a faster, more precisely bounded failure than the
raw "it hung" description — a real difference worth recording, not softened into "the same
thing happened."

**Exactly what the host printed** (stdout, in full):
```
Connecting...Connecting... OK      
Writing /workspaces/.planning/milestones/v1.34-artifacts/bench/cells/A2/reads/A2__control__w27c512/written.bin to W27C512
Timeout waiting for a response from /dev/ttyUSB0.
Communication error during WRITE: Timeout waiting for a significant response from /dev/ttyUSB0.
Write to W27C512 failed.
```
(stderr held only the two `tqdm` progress bars quoted above; no separate error text on stderr.)

**Read attempted anyway** (the READ path is predicted to work on this board even after a failed
write): `firestarter -p /dev/ttyUSB0 read w27c512 reads/A2__control__w27c512/run_01.bin` (log
`13_read_control_w27c512`), rc=0, "Read complete (14.60s)". The READ path **did** work, confirming
that half of the 999.2 prediction too.

**What the read-back actually shows (a measurement, not an inference):** of the 65536 B read, 431
bytes are non-`0xFF`, and every one of them is **contiguous from offset 0x0000 through 0x01AE**
(431 bytes, entirely inside the first 512 B block) — the remaining 65105 bytes, including all of
the second block onward, read back fully erased (`0xFF`). This is a precise, on-chip measurement
of exactly how far the MAIN phase got before the timeout: partway through programming the first
block (431 of 512 bytes, ~84%), never reaching the second block. This is a stronger, more exact
statement than "stopped on the first block" alone.

**Judged verdict** (`judge_wrv.py`, `WRV-VERDICT_A2__control__w27c512.json`): `sha_verdict_judged
== "mismatch"` (expected — the write never completed); `read_count == 1`; `distinct_read_shas ==
1`; `size_violations == []`; `app_verdict_unjudged == 0` (the **read** command's own exit code —
the read mechanically succeeded even though the bytes it returned don't match the intended
image); `verdict_disagreement == true` — the app's read-exit-code (0, success) disagrees with the
judged SHA verdict (mismatch), exactly the kind of disagreement D-11/the Recording discipline says
is itself a finding, never resolved by preferring one field over the other. **Outcome:
`skipped-with-reason`** (computed by `append_evidence.py`, never hand-set).

**Comparison basis:** 15.813 s elapsed against the measured healthy 41.010 s W27C512 baseline —
the failure is roughly 2.6x **faster** than a healthy write, not slower; it never got close to
using its 165 s ceiling.

## Position 6 (2 of 4): `A2__control__w29c020`

**The first algorithm-`0x05` (5V page-write) program ever attempted on this board.** Explicitly
NOT predictable from position 1's result — a materially different electrical/firmware path
(page-write with polled verify, not the 27C-family program-pulse path) — and it was not
pre-judged either way before running.

**Command:** `timeout --signal=INT 392 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config
/workspaces/.v1.34-arms/control/.venv/bin/firestarter -p /dev/ttyUSB0 write w29c020
reads/A2__control__w29c020/written.bin` (log `17_write_control_w29c020`).

**Ceiling:** **391.748 s (derived: 4x A1's measured control-arm W29C020 wall-clock, 97.937 s** —
`161-03-SUMMARY.md`). Not the 165 s W27C512 ceiling, not the 600 s absolute fallback (A1's own
control-arm W29C020 completed, so a derivation exists and is used). **Not needed** — the write
did not run anywhere near this ceiling either; wall-clock **4.019 s**, wrapper exit code **1**
(never 124 — the ceiling never fired here, same fact-pattern as position 1 but a much shorter
elapsed time).

**Wall-clock:** 4.019 s. **App-reported figure:** `not measured — the write failed before any
success line was emitted`.

**A DIFFERENT failure mechanism from position 1 — record which, do not conflate.** Position 1
ended in the *host's* own serial-response timeout (no reply from the firmware at all). This
position ended in a **firmware-reported error**, relayed by the host: the firmware's own verify
(data-poll) loop timed out and reported the last value it actually read. **Exactly what the host
printed** (stdout, in full):
```
Connecting...Connecting... OK      
Writing /workspaces/.planning/milestones/v1.34-artifacts/bench/cells/A2/reads/A2__control__w29c020/written.bin to W29C020
ERROR: Timeout verifying 0x15 at 0x00007f (got 0x13)
Programmer error during WRITE: Timeout verifying 0x15 at 0x00007f (got 0x13)
Write to W29C020 failed.
```
(stderr held only the `tqdm` byte-progress frames; **last progress frame, verbatim:**
`0%|          | 0x0200/0x40000 bytes` — 512 bytes into the 262144 B device, appeared twice
before the error. `0x40000` = 262144.)

**Stop point, precisely:** the firmware reports the verify failure at device offset **0x00007f**
(127 decimal), expecting to see `0x15` (this position's mask byte) written, and instead still
reading `0x13` after its own internal poll gave up. `0x13` (19 decimal) is **A1__v133__w29c020`'s
own mask** — this is the same physical W29C020 chip previously used in cell A1, and byte 0x7f had
not actually been reprogrammed to this position's value at the point the verify gave up.

**Read attempted anyway.** Unlike position 1, the READ path did **NOT** work cleanly here:
`firestarter -p /dev/ttyUSB0 read w29c020 reads/A2__control__w29c020/run_01.bin` (log
`18_read_control_w29c020`), rc=**1**, wall-clock 43.945 s, host printed `Timeout waiting for a
response from /dev/ttyUSB0. Communication error during READ: Timeout waiting for a significant
response from /dev/ttyUSB0.` — a genuinely different observation from position 1's "the READ path
works on this board" statement; it is **not** re-asserted here, it is contradicted by this
position's own measurement. The read produced a **partial** file: **113152 of 262144 bytes**
before it, too, timed out.

**What the partial read-back shows (a measurement):** of the 113152 bytes actually returned, only
292 are `0xFF` (blank) — the overwhelming majority (112860 bytes) are non-blank, i.e. this is
**not** simply an erased chip. Byte at offset **0x7f reads `0x13`** in this read-back — an exact
match to the firmware's own quoted "got 0x13," an independent on-chip confirmation of the same
fact the error message reported. Diffing the partial read against a freshly-generated copy of
**`A1__v133__w29c020`'s own image** (mask `0x13`/19, the value the stop-point byte matches)
shows a partial correlation (~65%, 74117/113152 bytes identical) — consistent with, but not
conclusively proving, that this physical chip still carries substantial residual content from
its earlier use in cell A1, since this position's own write essentially never got past its first
page and the read itself was also cut short by a communication timeout (which could itself
corrupt the transferred bytes independent of the chip's actual content). **Recorded as an
observation for Phase 165, not asserted as a proven root cause.**

**Judged verdict** (`judge_wrv.py`, `WRV-VERDICT_A2__control__w29c020.json`): `sha_verdict_judged
== "mismatch"`; `size_violations` non-empty (`run_01.bin` is 113152 bytes, not 262144);
`app_verdict_unjudged == 1` (the read command's own exit code, a failure) — **agrees** with the
judged mismatch this time (`verdict_disagreement == false`), unlike position 1 where the two
disagreed.

**Comparison basis:** neither this write's 4.019 s nor this read's 43.945 s (partial, failed) is
compared against A1's healthy 97.937 s write / 73.344 s read baselines as if they were the same
kind of measurement — both of A2's figures here are failures, not completions, and are recorded
as such rather than forced into a like-for-like comparison with a completed baseline.

## Position 7 (3 of 4): `A2__v133__w27c512` — the A/B half of the observed W27C512 failure

**This is the position this cell exists for.** Two attempts, both recorded — Standing bench rule 8
permits exactly one clean re-seat when a failure is attributable to a named physical cause; both
the discarded attempt and the re-run are recorded, never just the re-run.

### Attempt 1 — chip-ID mismatch at INIT (suspected contact fault, discarded)

**Write** (log `26_write_v133_w27c512`): rc=1, wall-clock 4.077 s.
```
Connecting...Connecting... OK      
Writing .../A2__v133__w27c512/written.bin to W27C512
ERROR: Chip ID 0x303 does not match expected ID 0xda08
Programmer error during WRITE: Programmer error during init: Chip ID 0x303 does not match expected ID 0xda08
Write to W27C512 failed.
```
**Read follow-up** (log `27_read_attempt1_v133_w27c512`): rc=1, wall-clock 4.026 s, identical
INIT-phase chip-ID failure; produced a **0-byte** file (`attempt1_run_01.bin`, kept for the
record, not counted as a judged read).

**Mechanism: neither a host-side timeout nor a firmware program/verify error — a firmware-reported
chip-identification failure before either operation began.** `0x303` (`0x0303`) matches this
project's own standing finding that a reading in this pattern is the signature of a **contact
fault**, not a rail or electrical fault (this project has hit the identical pattern before in a
different context — VPP/VPE monitor reads that don't route through the socket). Judged
attributable to a suspected bad contact under Standing bench rule 8 — **one** clean re-seat was
performed.

**What the operator reported at the re-seat, stated precisely, not embellished:** "reseated" —
the chip was removed and re-seated, but **no specific physical defect (bent pin, splayed lead,
misorientation) was identified or reported by inspection.** The named cause remains "suspected bad
contact, inferred from the `0x303` signature," not a confirmed/observed defect. **Rig-wear
context:** this is the same physical W27C512 that had, by this point, been inserted **four times**
across cells A1 and A2 (A1: control seat, v133 re-seat; A2: control seat, this v133 seat) before
this rule-8 re-seat made five.

### Attempt 2 (the re-run — Standing bench rule 8's one permitted re-run)

**Write** (log `28_write_v133_w27c512_rerun`): rc=1, wall-clock **10.245 s**.
```
Connecting...Connecting... OK      
Writing .../A2__v133__w27c512/written.bin to W27C512
ERROR: Byte at 0x000179 failed to program within 25 pulses
Programmer error during WRITE: Byte at 0x000179 failed to program within 25 pulses -- the write
aborted at this address: bytes before this block were already programmed, this block is only
partially programmed, and no later block was attempted. The firmware stops accepting blocks for
this write and its address counter does not advance, so re-running the write repeats the whole
file from the start. A byte that will not converge like this usually means insufficient program
voltage or a worn or failing cell, not a timing problem.
Write to W27C512 failed.
```

**This run got PAST the INIT chip-ID check** (the re-seat resolved that specific fault) and past
the full 65536 B INIT-phase transfer (progress bar 1 reached 100%, `0x10000/0x10000`). The MAIN
phase's progress bar restarted at 0% and last showed `1%|  | 0x0200/0x10000 bytes` before the
firmware's own error arrived — but the error message itself is more precise than the progress
frame: it names the exact failing address, **`0x000179`** (377 decimal, still within the first
512 B block), and states plainly (firmware's own words) that this looks like "insufficient
program voltage or a worn or failing cell, not a timing problem."

**Mechanism, and how it differs from the control-arm baseline:**

| | Position 1 (control, baseline) | Position 3 attempt 2 (v133, this run) |
|---|---|---|
| Ends via | host-side serial-response timeout (no firmware reply) | **firmware-reported** byte-program-convergence failure |
| Wall-clock | 15.813 s | **10.245 s** |
| Stop point | first-block boundary, 0x0200 (512 B) | named exact address **0x000179** (377 B) |
| On-chip evidence | 431/512 bytes of block 1 actually written | not yet measured (read attempted below) |
| Read afterward | worked cleanly (rc=0) | see below |

**This is NOT the same failure mode as the control arm's.** The control-arm failure was a
communication-layer timeout with no firmware diagnosis attached; this run's failure is a
firmware-*diagnosed* programming-pulse convergence failure with an explicit, named address and an
explicit hypothesis (insufficient VPP or a worn/failing cell) from the firmware itself. Recorded
as a genuinely different mechanism, not softened into "the same kind of thing happened." **Caveat,
stated honestly rather than asserting causation:** this difference cannot be cleanly attributed to
the v1.33 firmware alone from a single data point — the chip had also just been re-seated a fifth
time and had accumulated four prior insertions, so chip/contact wear is a live, undismissed
alternative explanation alongside a genuine firmware-behavior difference. Both possibilities are
left open for Phase 165, not resolved here.

**Read set** (v1.33 arm's normal three-run form): `dev consistency-check w27c512 --runs 3
--output-dir reads/A2__v133__w27c512 --keep-files` (log `29_devcheck_v133_w27c512`), rc=1,
wall-clock 53.716 s (3 runs, ~17.7-17.8 s each). **Result: `Consistency check: FAIL` — 3 distinct
SHAs, no two reads agreed.** First divergence at offset **0x001A** (26 decimal — inside the same
first block the write failed in), 23 of 65536 bytes divergent between run 1 and run 2 (0.0% by
proportion, but a real, non-zero instability). This is a genuinely new observation: **the chip's
own read-back is unstable** on this position, consistent with (though not proof of) the firmware's
own "worn or failing cell" hypothesis for the write failure.

**Judged verdict** (`judge_wrv.py`, `WRV-VERDICT_A2__v133__w27c512.json`): `sha_verdict_judged ==
"disagreement"` (`n3_disagreement == true`, `distinct_read_shas == 3`); `app_verdict_unjudged ==
1` (the app's own consistency-check FAIL) — **agrees** with the judged disagreement
(`verdict_disagreement == false`).

**Escalation rule (per 161-03-PLAN's shared conventions):** because `distinct_read_shas > 1`, a
retroactive three-run `dev consistency-check` on the **control arm's** matching position
(`A2__control__w27c512`) is **scheduled for `P-11`/Task 15**, to arbitrate whether this instability
is new (this position/chip-wear specific) or was always present and simply never surfaced because
position 1 only ever took a single read. Not run here — no second row is ever written for an
existing `position_id`; the escalation, if it fires, produces a separate artifact
(`WRV-VERDICT_A2__control__w27c512__escalated.json`) at teardown.

**Comparison basis:** neither of this position's two write attempts (4.077 s / 10.245 s) nor its
failed read set (53.716 s wall-clock across 3 attempts, none completing cleanly) is compared
against A1's or this cell's own healthy baselines as if it were a completed measurement — all are
failures, recorded as such.

## Position 8 (4 of 4): `A2__v133__w29c020` — closing the A/B square

**Command:** `timeout --signal=INT 392 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config
/workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyUSB0 write w29c020
reads/A2__v133__w29c020/written.bin` (log `33_write_v133_w29c020`).

**Ceiling:** 391.748 s (derived, 4x A1's 97.937 s). **Not needed** — wall-clock **14.288 s**,
wrapper exit code **1** (never 124).

**A FOURTH, distinct mechanism — earlier than any prior position.** This write failed before
reaching even the INIT phase's device handshake — a bare **connect** failure:
```
Connecting...
Timeout waiting for a response from /dev/ttyUSB0.
Connecting... Failed  
Failed to setup operation WRITE for w29c020: No compatible programmer answered on /dev/ttyUSB0.
If a board is attached there, its firmware may predate the current command framing, which makes
it answer 'Bad JSON' instead of an ack -- every 2.x release, and 3.0.0 pre-releases before b8.
Such a board can still be reflashed directly: firestarter --port /dev/ttyUSB0 fw --board <board>
--install
```
No progress bar of any kind appeared (stderr empty) — the failure is earlier than position 3
attempt 1's chip-ID mismatch (which at least completed the connect handshake before failing on the
chip probe).

**Immediately checked afterward:** a plain `hw` command (no chip operation) against the same board
succeeded cleanly (log `34_hw_probe_after_connect_fail`, rc=0, `Hardware revision: Rev 2.0-class`)
— the board itself was not wedged; the failure was specific to the `write` command's own setup
handshake at that moment, not a lasting connection loss. **No re-run was performed** — Standing
bench rule 8's one-clean-re-seat allowance is specific to a suspected chip-contact fault and was
already spent on position 3; nothing here points at the chip (no chip-ID probe was even reached),
and no other rule in this procedure licenses a retry of a transient connect failure. Recorded as
observed, not chased.

**App-reported figure:** `not measured — the write failed before establishing a connection, let
alone emitting a success line`.

**Read attempted anyway** (v1.33 arm's normal three-run form): `dev consistency-check w29c020
--runs 3 --output-dir reads/A2__v133__w29c020 --keep-files` (log `35_devcheck_v133_w29c020`),
rc=**2**, wall-clock 14.697 s. **Run 1 of 3 failed with a communication timeout partway through**
(`Timeout waiting for a response... Run 1: hardware/serial error -- read incomplete`) — the tool
aborted after the first run's own hard failure, never attempting runs 2 or 3. Last progress frame:
`2%|▏  | 0x1000/0x40000 bytes` (4096 of 262144 bytes) before the timeout. The read produced a
**partial 4096-byte file**, not the full 262144, not an empty directory.

**What the partial read-back shows:** of 4096 bytes, only 16 are `0xFF` — overwhelmingly
non-blank. Diffed against a freshly-generated copy of **`A1__v133__w29c020`'s own image** (mask
`0x13`/19 — the same value position 2's stop-byte matched): **4061 of 4096 bytes identical
(99.1%)**. This is a materially stronger correlation than position 2's ~65% (which was likely
diluted by that read's own mid-transfer corruption) and further reinforces — without proving —
that this physical W29C020 chip still carries content from its earlier use in cell A1, essentially
untouched, because none of A2's own three write attempts on this chip (control mask 0x15, this
position mask 0x17) has gotten far enough to overwrite more than a handful of bytes. **Still
recorded as an observation for Phase 165, not a confirmed root cause** — a partial read's own
corruption from its own timeout remains an unexcluded confound, even at 99.1%.

**Judged verdict** (`judge_wrv.py`, `WRV-VERDICT_A2__v133__w29c020.json`): `sha_verdict_judged ==
"incomplete-read-set"` (only 1 of the intended 3 reads landed, `distinct_read_shas == 1` because
there is only one file to compare); `size_violations` non-empty (4096 bytes, not 262144);
`app_verdict_unjudged == 2` (the app's own consistency-check hard-error code) — **agrees** with
the judged incomplete-read-set (`verdict_disagreement == false`). **No N=3 disagreement to record
here** — the read set never reached three files, so this position does not itself trigger the
escalation rule (unlike position 3); it is a different failure shape (incompleteness, not
disagreement among complete reads).

### Closing the square — all four A2 positions, mechanism by mechanism

| # | Position | Mechanism | Wall-clock (write) | Stop point |
|---|---|---|---|---|
| 5 | `A2__control__w27c512` | host-side serial-response timeout, no firmware reply | 15.813 s | first-block boundary (0x0200); 431/512 B of block 1 actually written |
| 6 | `A2__control__w29c020` | **firmware-reported** verify-timeout (data-poll) | 4.019 s | byte 0x7f (page-write verify) |
| 7 | `A2__v133__w27c512` | attempt 1: chip-ID mismatch at INIT (contact fault); attempt 2 (rule-8 re-run): **firmware-reported** program-convergence failure | 4.077 s / 10.245 s | attempt 2: byte 0x000179 |
| 8 | `A2__v133__w29c020` | **connect-level** failure — no device handshake reached at all | 14.288 s | never reached INIT/chip-ID |

**No two of the four positions failed by the identical mechanism.** Every one of A2's four
positions **did stop the chip-program path**, consistent with Backlog 999.2's overall prediction
that this board cannot complete a program — but the specific point and manner of failure varied
position to position, which is itself the more precise, more useful record than "it hangs" alone.
**No completion occurred on either arm** — Backlog 999.2 is not contradicted by an unexpected
success anywhere in this cell.

**VPP note, carried from Task 12's record:** position 3's firmware diagnosis named "insufficient
program voltage or a worn or failing cell" as a candidate. This position's own failure (a
connect-level timeout) offers no independent evidence either way on VPP specifically — it is
recorded as a **separate, named Phase 165 hypothesis** (see `CELL.md`), not resolved by this
position.
