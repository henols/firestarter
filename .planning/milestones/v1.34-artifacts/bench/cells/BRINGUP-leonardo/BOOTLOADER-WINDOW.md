# BRINGUP-leonardo — Bootloader-Entry Measurement (Caterina, avr109, 1200-baud touch)

**Target:** `leonardo` (ATmega32U4, Caterina 4096 B bootloader, `avr109` programmer, 57600 baud)
**Port:** `/dev/ttyACM0`
**Purpose:** Measure — not assume — whether this specific Leonardo's Caterina bootloader
re-enumerates on a NEW serial node or the SAME one after the 1200-baud touch, for the READ
direction specifically (the write direction's same-node behaviour was already recorded once,
historically, for a different session — `.planning/debug/resolved/fw-update-blocked-release-fw.md:283`).
`touch_1200.py`'s own `--selftest` states plainly that this is unproven until this bring-up.

---

## Attempt 0 — identity probe with NO touch (a genuine measurement, not skipped)

Before touching the board at all, `probe_board.py` was run directly against the port to see
whether the application firmware answers an `avr109` handshake. It does not — and, on the very
first attempt, this tripped a real tool bug rather than a clean failure:

```
python3 .planning/milestones/v1.34-artifacts/tools/probe_board.py --target leonardo --port /dev/ttyACM0 \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out .../probe_pretouch_attempt.json   # cwd: /workspaces
```

- **First run:** crashed with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xaa in
  position 564` inside `subprocess.run`'s `text=True` decoding. **Rule 1 bug, fixed in-phase**:
  `probe_board.py`'s `run_avrdude()` used `text=True` with the strict default `'utf-8'` error
  handler; a Leonardo running its application firmware (not the bootloader) answers an `avr109`
  handshake attempt with raw, non-protocol serial bytes that are not valid UTF-8, and avrdude
  echoes some of that into its own diagnostic text. Fixed by adding `errors="replace"` to both
  `probe_board.py`'s `run_avrdude()` and `judge_readback.py`'s `run_avrdude_read()` /
  `run_objcopy_normalize()` (the same subprocess-decode pattern), so a device answering with
  garbage bytes produces a reported `FAIL:` line instead of a raw traceback. Both tools'
  `--selftest` re-run clean after the fix (12 tool selftests total across the two files, all
  PASS).
- **Second run (post-fix):** exited cleanly, rc=1, **~6.0 s** elapsed:
  `FAIL: neither parse route matched avrdude stderr: 'Error: initialization failed  (rc = -1) ...'`
  — avrdude's own retry/backoff before giving up on a non-responding avr109 handshake. This is
  the expected, informative negative: **the application firmware does not speak avr109; the
  bootloader must be entered first**, even for identity.

---

## Measurement cycle 1 — `touch_1200.py --wait-new-port` (testing for a NEW node)

```
python3 .planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --wait-new-port --timeout-s 3 \
  --settle-s 2.0 --out .../touch_measure1.json   # cwd: /workspaces
```

- **Devices before:** `['/dev/ttyACM0']`
- **Devices after** (polled for up to 3 s past the 2.0 s settle): `['/dev/ttyACM0']` — **no new
  node ever appeared**.
- **Result:** `FAIL: timed out after 3.0s waiting for a NEW serial port ... (before=['/dev/ttyACM0']
  after=['/dev/ttyACM0'])`, rc=1, ~5.27 s elapsed (2.0 s settle + ~3.0 s poll + overhead).
- An identity-probe attempt immediately following this cycle (started ~5.3 s after the touch,
  itself taking up to ~6 s to fail) found the bootloader had already reverted to the
  application (`Error: initialization failed`) — the combined ~11 s from touch onset exceeded
  the window. **This is the informative failure that determined the correct procedure below**:
  `--wait-new-port` burns window time polling for a node that this board never produces on the
  read chain, and must not be used here.

---

## Measurement cycle 2 — `touch_1200.py` bare mode (reuse `--port`, no wait)

```
python3 .planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out .../touch_measure2.json   # cwd: /workspaces
```

- **Devices before:** `['/dev/ttyACM0']`
- **Devices after** (immediately, no poll): `['/dev/ttyACM0']` — confirms cycle 1's finding
  independently.
- Touch itself: rc=0, `OK: use port /dev/ttyACM0`, **2.243 s** elapsed (the 2.0 s settle plus
  process/serial overhead).
- **Immediately following**, `probe_board.py --target leonardo --port /dev/ttyACM0` ran within
  the same shell block with no added delay: rc=0, **1.244 s** elapsed,
  `OK: board identified as atmega32u4 via route1 (signature 0x1e9587)` — matching the known-good
  leonardo signature and the operator's declaration. **Total elapsed from touch onset to a
  successful, parsed identity result: 3.487 s.**

**Branch taken, stated explicitly:** the bootloader-entry behaviour of this Leonardo, measured
for the read direction specifically, is **SAME NODE** — Caterina returns on `/dev/ttyACM0`, the
identical node the application uses, never a new one. `touch_1200.py`'s `--wait-new-port` mode
(PlatformIO's own upload-path shape) is the WRONG mode for this board's read chain; the bare
mode (settle only, reuse `--port`) is the one that works, and every read-affecting invocation
below uses it. Settle interval used: **2.0 s** (the value copied from
`firestarter_app/firestarter/avr_tool.py:117-124`'s `_trigger_reset`, unchanged). Measured time
from touch to a responsive programmer: **3.487 s** (Attempt 2's identity probe).

---

## Event 1 — control arm flashed via PlatformIO, then the independent read-back proof

PlatformIO owns the flash step and performs its own touch/port-wait internally — see the
"Bonus fact for plan 10" note in `BRINGUP-uno/CROSSFLASH.md`: `leonardo.json`'s
`"use_1200bps_touch": true` / `"wait_for_upload_port": true`. This event is recorded in full in
`CROSSFLASH.md`; the read-chain timing relevant to this window measurement is:

```
python3 .planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out .../touch_for_read_event1.json                                          # cwd: /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target leonardo --port /dev/ttyACM0 \
  --flashed-arm control --expect-arm control \
  --out-dir .../BRINGUP-leonardo --pins .planning/milestones/v1.34-artifacts/rig-pins.json            # cwd: /workspaces
```

- Touch: rc=0, 2.261 s elapsed.
- Read + judge (`judge_readback.py`, immediately following, no added delay): rc=0, **1.617 s**
  elapsed. `avrdude`'s own read of the full 32768 B flash took **0.31 s** once started
  (`avrdude_read.stderr.log`: `Reading | ##...## | 100% 0.31s`) — the read itself is fast; the
  remainder of the 1.617 s is avrdude connection setup plus the `avr-objcopy` normalize step.
- **Total elapsed from touch onset to a completed, judged verdict: 3.878 s.**

**Branch A is taken: the full read completes.** `flash_readback.bin` is exactly **32768 bytes**
(`readback_size_bytes: 32768`); `judged_match: true`; `judged_span_bytes: 28170` (the **control**
arm's own `leonardo` hex extent, `hex_span_expected_by_arm.control`); `sha_actual_judged` ==
`sha_expected_judged` == `d734ad490329d530...` (identical — `judged_span_policy` is `hex-extent`
with zero vector exclusions on this target, so an exact byte match is expected, unlike
`uno328pb`'s vector-exclusion case); `sha_whole_flash_unjudged` = `334f9144d44a4e53...` (32768 B,
UNJUDGED, recorded but never consumed in the `judged_match` decision, per D-02).

**Timing margin, stated as a number (this task's own requirement):** the read chain completed
in **3.878 s** from touch onset, against a Caterina inactivity window RESEARCH.md's Pitfall 5
describes as "roughly 8 s" — **more than 4 s of margin**, and that window is an *inactivity*
timer (it resets on continuous communication), not a hard session cap, so the true margin for a
continuously-communicating session is larger still. Compared against the two proven baselines
from plans 08/09: `uno`'s read+objcopy took ~5.5 s (three timed runs, 5.493–5.505 s); `uno328pb`'s
took ~4.07 s. **`leonardo`'s read+objcopy (1.617 s) is faster than both other chains**, despite
running at the lowest baud (57600 vs 115200) — avrdude's avr109/Caterina block-read path is
evidently efficient per byte, and the dominant cost in the other two chains' baselines is
plausibly connection/handshake overhead rather than raw transfer time. This is recorded as an
observation, not re-derived into a general claim about avr109 performance beyond this board.

No retry loop and no timeout escalation appear anywhere above: Attempt 0 and Measurement cycle 1
are recorded as the informative failures they were (the wrong-mode attempt, and the pre-touch
attempt), not discarded, and exactly one further touch cycle (Measurement cycle 2) established
the working procedure, which Event 1 then used once, successfully, on the first prompt attempt.
