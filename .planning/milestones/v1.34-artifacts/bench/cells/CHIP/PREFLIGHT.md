# CHIP cell — PREFLIGHT.md (Task 2)

Standing bench rule 1: port identity is re-verified for **this session**, never inherited from
Phase 161. Four steps, in order, all before any part runs.

## One — P-02: re-verify port identity by signature

**A genuine node shuffle was observed and worked through live**, not assumed away: the first
touch+probe attempt raced the post-avr109-exit re-enumeration window (the gap introduced by an
interim `cat` of `touch.json` let the Caterina bootloader session time out before `probe_board.py`
ran, producing `FAIL: neither parse route matched avrdude stderr` — the exact known failure shape
this board gives when the touch window has already closed). A retry then hit the board sitting on
`/dev/ttyACM1` momentarily (a genuine renumbering after the killed avrdude process), which a
second touch bounced back to `/dev/ttyACM0`, followed by one transient `[Errno 5] Input/output
error` on an immediate re-open. None of these were silently retried past — each is logged below
via its command and outcome. The **working, successful sequence** (touch, then probe, immediately
back to back with no interposed command) is the one whose result is authoritative:

```
python3 .planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 --out $CELL_DIR/touch.json
python3 .planning/milestones/v1.34-artifacts/tools/probe_board.py --target leonardo --port /dev/ttyACM0 --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out $CELL_DIR/board_probe.json
```

Result (`touch.json`): `changed: false`, `devices_before == devices_after == ["/dev/ttyACM0"]`,
`wait_new_port: false` — no `--wait-new-port` token anywhere, per the standing prohibition.

Result (`board_probe.json`, **authoritative**): `board_signature: 0x1e9587`,
`connected_part: atmega32u4`, `mcu_matches: true`, `signature_route: route1`. Matches
`rig-pins.json`'s `targets.leonardo.mcu` exactly.

**Non-authoritative controller line** (`hw`, 2 s settle after the probe, per the
`BRINGUP-leonardo-provenance/PREPROOF.md` working sequence):

```
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -v -p /dev/ttyACM0 hw
```

rc=0. Reported hardware revision: `Rev 2.0-class, Override HW: Rev 2.0-class` — matches the
operator's declared silkscreen `Rev 2.0` (Task 1). No `I: FW: ` line is emitted by this arm's `hw`
call (a previously-measured, disclosed limitation — `capture_provenance.py`'s own
`_interpret_hw_probe` records this exact shape as `controller_string: "not measured — <reason>"`,
never a hard failure on an `rc=0` `hw` call); this probe is non-authoritative by design and the
signature probe above is the identity of record.

## Two — arm state (`check_arms.py`)

```
python3 .planning/milestones/v1.34-artifacts/tools/check_arms.py --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --expect-config-sha 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0 \
  --out $CELL_DIR/check_arms_pre_cell.json
```

`check_arms OK: 2 arms verified (SHA+porcelain+file-probe+dep-freeze+interpreter+config-sha+cli-surface)`,
rc=0. The **v1.33** arm is confirmed on the board (Phase 161 left it flashed, no re-flash needed):
`head == cb189a9b001e9e34fb7651535de339761301d061` (== `rig-pins.json` `arms.v133.app_sha`),
`porcelain_clean: true`. `config_dir_sha` recomputed = the pinned value, matched. `surface_diff_ab`
and `surface_diff_ba` are both empty (25/25 commands on each arm).

## Three — the `fw_board_identity` pre-flight bring-up datum

Called directly through the **v1.33 arm's own** `.venv/bin/python -P`, with `FIRESTARTER_CONFIG_DIR`
inline and the port set as a **transient** value (`persist=False`, mirroring `cli.py`'s own
`-p`/`--port` handling at `cli_handlers.py:402` — never the persisting default, which would write
inside the frozen config dir):

```
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/v133/.venv/bin/python -P -c "
import json
from firestarter.config import ConfigManager
from firestarter.hardware import HardwareManager
cm = ConfigManager()
cm.set_value('port', '/dev/ttyACM0', persist=False)
hw = HardwareManager(cm)
identity = hw.read_programmer_identity()
print(json.dumps({'fw_board_identity': identity.fw_board_identity, 'hw_revision': identity.hw_revision}))
"
```

**Result: `fw_board_identity = "3.0.0b22:leonardo"` — non-null.** No `P-H1`; this is the CHIP-02
hard requirement discharged before any part has run. `hw_revision = "Rev 2.0-class, Override HW:
Rev 2.0-class"`, consistent with steps One and Two above.

## Four — config-dir digest, before and after the identity probe

- **Pre-probe digest:** `77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0`
- **Post-probe digest:** `77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0`

Equal to each other and to the pinned `arms-provenance.json` `config_dir_sha`. Both digests were
computed over `config_dir` contents (`.gitkeep`, `config.json` — no `reports/` entry). The
transient-port form left no write behind.

## Honesty ledger — `~/.firestarter/config.json` against the Amendment-4 baseline

| Field | Amendment-4 baseline | Measured now (Task 2) | Changed? |
|---|---|---|---|
| file count / size | 1 file, 30 bytes | 1 file, 30 bytes | No |
| `config.json` sha256 | `b323867c1f01b22a705dd9caf003ab7302a249fe46772f5b02e44aaa2760dd7` | `b323867c1f01b22a705dd9caf003ab7302a249fe46772f5b02e44aaa2760dd79` | No |
| tree sha (relpath+content) | `423546cd37b5b45d9654e5acd07bd7e2a3c9e1df77e4d5feb79951bf37329951` | `423546cd37b5b45d9654e5acd07bd7e2a3c9e1df77e4d5feb79951bf37329951` | No |
| mtime | `1787854674` (2026-08-27 18:17:54 UTC) | `1787951597` (2026-08-28 21:13:17 UTC) | **Yes — recurrence** |

**Recorded as a standing `P-H1` finding handed to Phase 165, per the shared conventions — not
fixed, not deleted.** Content, size and tree digest are byte-identical to the baseline; only the
mtime advanced (touched, not modified), consistent with the pattern already seen in all three of
Phase 161's cells and again before this phase began. Most likely cause: one of this task's
sub-process probes (`check_arms.py` shells to each arm's own venv interpreter without an inline
`FIRESTARTER_CONFIG_DIR`, per that tool's own design — it verifies the **arms**, not the frozen
dir) touching the unset-default path. The sandbox denies deletion of this directory; it is not
attempted.

## CLOSE-04 issue-count "before" figure (carried forward)

From `.planning/milestones/v1.34-artifacts/bench/cells/CHIP/PRE-PHASE.md` (plan 162-01, Task 3, Part B):
**issue count: 37** (`gh issue list --repo henols/firestarter_prom --state all --limit 1000`,
authenticated as `henols`). This is the figure plan 162-10 must diff against at phase end.

## Argv discipline

Every probe above uses the arm's absolute `venv_bin`/`venv_python` path from `rig-pins.json`, no
forbidden flag anywhere, and the identity probe's interpreter invocation carries `-P`. No
`touch.json` in this cell records `wait_new_port: true`.

## Status

Port re-verified by signature for this session. v1.33 arm confirmed on the board at its pinned
SHA. **`fw_board_identity` proven non-null before any part runs.** Frozen config dir provably
unchanged by the probe. `CHIP-EVIDENCE.jsonl` still holds exactly one line (schema only) — no row
appended yet.
