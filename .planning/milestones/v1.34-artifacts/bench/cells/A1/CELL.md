# Cell A1 — Arduino Uno (ATmega328P) on Rev 2.0 shield

Runs `P-01`..`P-11` per `.planning/milestones/v1.34-artifacts/PROCEDURE.md` (Amendment 3), control arm then v1.33,
W27C512 then W29C020, four evidence positions. This cell inherits an occupied socket (the only
inherited-state cell in the milestone) and is the milestone's first 262144 B write/read on
silicon.

## P-01 — Mount and declare (2026-08-27T13:16:22Z)

**Enumeration before presenting the gate** (2026-08-27T13:14:06Z, Claude, sysfs mtimes):
- `/dev/ttyACM0` — Leonardo, mtime 13:02:11Z
- `/dev/ttyUSB0` — uno328pb (CH340), mtime 12:48:34Z
- No `ttyACM1` — the A1 Uno was off the bus, as expected.

**Enumeration on resume** (2026-08-27T13:16:22Z orchestrator sysfs descriptors, re-confirmed
independently by Claude at the same timestamp):
- `/dev/ttyACM0` — `2341:8036` "Arduino Leonardo", serial (empty), mtime 13:02
- `/dev/ttyACM1` — `2341:0043`, product (empty), serial `55736303739351B040E1`, mtime 13:15:37Z
  — **this is A1's Uno**, identity confirmed by serial descriptor, not by node number. The
  recorded serial `55736303739351B040E1` is byte-identical to the descriptor recorded before
  this board was set aside at the end of Phase 161 Plan 02, and the node's mtime advanced
  (12:48 area -> 13:15), consistent with a fresh re-enumeration of the same physical unit.
- `/dev/ttyUSB0` — CH340 "USB Serial" (uno328pb), serial (empty), mtime 12:48

Reported node matched the post-resume enumeration; no stop condition.

**THREE live nodes for the whole of this cell.** `/dev/ttyACM0` (Leonardo) and `/dev/ttyUSB0`
(uno328pb) are two stationary boards that will appear in every before/after enumeration this cell
runs — they are not a re-enumeration of the board under test. Every avrdude / `probe_board.py` /
`capture_provenance.py` / `firestarter` invocation in this cell carries an explicit
`--port /dev/ttyACM1` (or `-p`), never autodetected.

**Operator declaration, recorded verbatim:**
- Board: Uno, on `/dev/ttyACM1`
- Shield silkscreen: **"Rev 2.0"** (`shield_rev_declared`) — already the canonical value, no
  normalization applied. Silkscreen is authoritative; the A3 ADC band cannot distinguish
  Rev 2.0 / Rev 2.2 / Modified Rev 0.
- Socket: **EMPTY**, W27C512 removed — operator-confirmed in words: "socket empty"

**`$PORT` for this cell:** `/dev/ttyACM1`
**`$SHIELD_REV` for this cell:** `Rev 2.0`

`P-03` (Uno-class chip-out, control-arm pass) is satisfied by this same confirmation — the
socket was emptied here at `P-01`, so Task 3's `P-03` reference is a one-line no-op
re-confirmation, not a second gate (D-02: no artificial park prompt).

**Pre-cell arm integrity capture** (log `00_check_arms_pre_cell`, before the board was
reconnected — this tool never touches the device): `check_arms.py` exit 0, both arms verified
(SHA+porcelain+file-probe+dep-freeze+interpreter+config-sha+cli-surface). `control` HEAD
`6bfa6453d1bac232eb81ab35fa7f14b50b0b291a`, `v133` HEAD `cb189a9b001e9e34fb7651535de339761301d06`,
`config_dir_sha` `77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0` — matches the
frozen pinned value. See `check_arms_pre_cell.json`.

**Uno-class chip-out precondition satisfied:** the signature probe (`P-02`, Task 2) may now run.
From the moment the W27C512 is seated again (Task 4, `P-05`/`P-06`) no avrdude operation of any
kind may run on this board until the chip comes out again (`P-03`/`P-10` window for the second
arm).

## P-05 / P-06 — Seat W27C512, pot confirmed by measurement (2026-08-27)

Operator: "Uno on /dev/ttyACM1, rev 2.0 shield and W27C512 seated" — W27C512 (DIP28) seated,
board/shield re-confirmed. Pot not separately declared by the operator; `P-06` settled instead by
Claude's single confirming `vpp` read: `VPP: 12.0V, Internal VCC: 5.1V`, matching the 12.0 V
target to the precision this project records it at. Full detail in `POT.md`.

**Avrdude window now closed:** the W27C512 is seated. From this point no avrdude operation of any
kind (upload, read-back, or signature probe) may run on this board until the chip comes out again
at Task 6's swap (`P-08`).

## P-08 — Swap to W29C020 (2026-08-27, operator)

Operator: "W29C020 seated". W27C512 (DIP28) removed, W29C020 (DIP32) seated on the Uno at
`/dev/ttyACM1`. **Pot not touched** — `P-06`'s single confirming read (12.0 V) stands for the
whole cell; no second `vpp` invocation was run for this swap.

## P-05 (second arm) — Seat W27C512 again (2026-08-27, operator)

Operator: "W27C512 seated". W27C512 (DIP28) re-seated on the Uno at `/dev/ttyACM1` for the v1.33
arm's two positions. **Pot not touched** — `P-06`'s single confirming read (12.0 V) continues to
stand for the whole cell; no second `vpp` invocation.

**Avrdude window closed again** from this confirmation: no upload, read-back or signature probe
may run on this board until the chip comes out at Task 12's swap (`P-08`, second arm).

## P-08 (second arm) — Swap to W29C020 again (2026-08-27, operator)

Operator: "W29C020 seated". W27C512 removed, W29C020 (DIP32) seated again on the Uno at
`/dev/ttyACM1`, for the v1.33 arm's last position. **Pot not touched** — `P-06`'s single
confirming read continues to stand for the whole cell. No D-09 smoke re-run (one-time,
A1-control-only bring-up datum; repeating it here would break positional symmetry).

## P-09/P-11 — Second-arm smoke, teardown, per-cell gate, and cell close (2026-08-27)

### Position summary (all four)

| # | `position_id` | arm | chip | wall-clock write (s) | app-reported (s) | reads | verdict |
|---|---|---|---|---|---|---|---|
| 1 | `A1__control__w27c512` | control | w27c512 | 41.305 | 37.48 | 1 | match |
| 2 | `A1__control__w29c020` | control | w29c020 | **97.937** | 94.47 | 1 | match (**first 262144B write/read on silicon**) |
| 3 | `A1__v133__w27c512` | v133 | w27c512 | 41.037 | 37.48 | 3 (distinct_read_shas=1) | match |
| 4 | `A1__v133__w29c020` | v133 | w29c020 | 97.916 | 94.48 | 3 (distinct_read_shas=1) | match |

**D-09 smoke outcome:** W29C020 chip-id matched, standalone `blank` reported not-blank at
`0x000000` — a valid, expected addressability proof (see `SMOKE-W29C020.md`).

**No escalation was due.** Both v1.33 positions (`A1__v133__w27c512`, `A1__v133__w29c020`)
recorded `distinct_read_shas == 1` with no disagreement — no retroactive control-arm escalation
was scheduled or run.

**Both read-back proofs, arm-specific judged spans (the value that distinguishes the arms):**
`READBACK-VERDICT` control (preserved in `readback_control/`): `judged_match=true`,
`judged_span_bytes=26026`, `sha_actual_judged=f60fa76ff808b5ca0454e0bff0698f605a57a61069f6c7b8061e61b27ac3fa23`.
`READBACK-VERDICT` v133 (preserved in `readback_v133/`, also the cell-root copy at teardown):
`judged_match=true`, `judged_span_bytes=22952`,
`sha_actual_judged=dc2ae8a15be600b3d22539d06e4e3fa779af56e2835d3068610fcd3a8775f853`. **The two
arms' judged read-back SHAs differ** — itself evidence the A/B is a real firmware difference,
not one image relabeled under two names.

**Derived D-08 W29C020 ceiling for every later W29C020 position: 391.748 s** (4x position 2's
measured control-arm wall-clock, 97.937 s). **A1's 262144 B control-arm read baseline: 73.344 s**
wall-clock — a comparison baseline for A2/A3-B2, not a portable constant (the Uno moves 512 B
chunks per transfer where the Leonardo moves 1024 B).

**BOARD-04 non-claims, carried and not re-derived:**
1. v1.31's **0.37 s** figure is a **spread** (max minus min across three app-reported,
   success-only figures: 106.06 / 105.69 / 106.06 s) on **Leonardo + Rev 2.0**, not a duration.
   A1 is a **Uno**, so no comparison against v1.31's figure is drawn here at all — that
   comparison is valid only on cell A3/B2. Every A1 wall-clock figure is a **single write per
   position — a data point, not a spread.**
2. v1.34's much faster W27C512 figures (~41 s vs v1.31's 106 s) are **PR #55's per-byte
   VPE-settle amortisation**, present in **both** arms' merge bases — not a v1.33 effect.

### Teardown

**v133 read-back set preserved** into `readback_v133/` (all six cell-root artifacts, mirroring
`readback_control/` from Task 9) — both arms' firmware evidence now survive side by side.

**Teardown signature probe** (`board_probe_teardown.json`, a distinct path from `P-02`'s
`board_probe.json`): `connected_part=atmega328p`, `board_signature=0x1e950f` — **unchanged** from
`P-02`. Board identity stable across the whole cell.

**Config-dir check, two assertions in order:**

1. **`~/.firestarter` — CHANGED — P-H1.** Measured: `config.json` mtime advanced from the
   Amendment 3 pinned baseline's `1787817565` (2026-08-27T07:59:25Z) to
   2026-08-27T13:24:25.033327651Z; content is now `{"port": "/dev/ttyACM1"}`
   (sha256 `77d3cdab64576fea13c5e5a1c89deb281a128e91f7ea82d332e9bd07f758af9c`), differing from the
   pinned baseline sha. File count remains exactly one (`config.json`), so this is a content
   change, not a new/removed file. **No deletion was attempted** (the sandbox denies it and
   deleting destroys the evidence).

   **Investigation performed, cause not identified:** every bench-tool source this plan is
   permitted to read (`check_arms.py`, `capture_provenance.py`, `judge_readback.py`,
   `probe_board.py`) was checked for an internal subprocess call to the `firestarter` CLI.
   `check_arms.py`'s `probe_cli_surface()`/`check_file_probe()` only `import firestarter` for
   static introspection or `__file__` resolution — neither invokes a real CLI command, so neither
   can call `ConfigManager.remember_port()` (the sole writer of the `"port"` key, per
   `firestarter/config.py`'s own docstring). `capture_provenance.py`'s internal `hw` call
   (`probe_controller_string`) passes explicit `-p <port>` and inherits `capture_provenance.py`'s
   own process environment — every invocation of `capture_provenance.py` in this cell had
   `FIRESTARTER_CONFIG_DIR` set inline on that same command line, so this internal call should
   have both the correct config dir and a *transient* (not-persisted) port. `judge_readback.py`
   and `probe_board.py` never `import firestarter` at all — both shell out to `avrdude`/
   `avr-objcopy` directly. Every **direct** CLI invocation this plan made (the `hw`, `vpp`, `id`,
   `blank`, `write`, `read`, `dev consistency-check` commands) carried both an explicit `-p` and
   an inline `FIRESTARTER_CONFIG_DIR=` prefix. No in-scope source explains a non-transient
   `remember_port()` write to the *default* config dir. This is out of scope to root-cause
   further here — investigating or fixing `firestarter_app`'s `ConfigManager`/`serial_comm.py`
   internals is product code, forbidden by this plan's D-16 boundary (RCA and fixes belong to
   Phase 165).

   **Impact assessment:** this does **not** invalidate any of A1's four judged verdicts. Every
   write/read/judge command that produced a judged result set `FIRESTARTER_CONFIG_DIR` inline
   directly on its own command line (never relying on inheritance through an unprefixed
   ancestor process), and the judged oracles (`judge_wrv.py`, `judge_readback.py`) read raw
   bytes and avrdude output directly — neither ever consults the CLI's `ConfigManager`, database,
   or pin-map. Assertion (2) below (the frozen `FIRESTARTER_CONFIG_DIR` content SHA) is
   independently confirmed unchanged, which is the assertion whose failure *would* indicate a
   judged result used the wrong database/pin-map.

   **This mirrors the identical, previously-unresolved finding from Phase 160 Plan 12** ("a
   stray `~/.firestarter` directory... traced circumstantially to an unlogged plan-11
   invocation" — `STATE.md`, prior session note) — recurring under the frozen-baseline detector
   Amendment 3 installed specifically to catch this class of drift. Handed to Phase 165, not
   fixed here.

2. **Frozen `FIRESTARTER_CONFIG_DIR` content SHA — unchanged, confirmed.**
   `check_arms.py --expect-config-sha 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0`
   -> matched (`check_arms_teardown.json`). All four A1 provenance records carry a non-null,
   matching `config_dir_sha` (`77adfdd2...`) — proof each capture genuinely consulted the pinned
   dir, not a silently-omitted field.

**Completeness assertion:** all four `position_id`s present in `bench/EVIDENCE.jsonl`, each
exactly once, `cell_id == "A1"`, `outcome` in `{validated, skipped-with-reason}` (all four
`validated`), each with a non-null `write_duration_wallclock_s`. `gate_record.py --jsonl`: 0
violations.

**Per-cell gate (D-04):** `bash run_gates.sh` — **exit 0** (captured directly via `$?`, never
through a pipe), **12/12 tool selftests, ALL GATES PASSED (5/5 live gates)**.

**Sub-repo porcelain:** both `firestarter/` and `firestarter_app/` confirmed
`git status --porcelain` empty. **`firestarter` gitlink:** confirmed at HEAD
`5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463` (the originally pinned v133 SHA) with meta's own
`git diff --stat -- firestarter` **empty** — the cell ends on the v1.33 arm exactly as required,
no gitlink diff to commit.

**Force-added positions:** **none.** All four positions judged a clean `match` — the
commit-on-failure exception (force-adding a non-clean position's `reads/<position_id>/`
contents) was not triggered for any position in this cell.

### P-11 leave-state (cell-agnostic declaration, this cell's concrete values)

| Field | Value |
|---|---|
| Board | Arduino Uno (ATmega328P, signature `0x1e950f`) |
| Port | `/dev/ttyACM1` (identity-confirmed by serial `55736303739351B040E1`, not node number) |
| Arm on the board | **v1.33** (fw `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`) |
| Chip seated | **None** — socket confirmed empty at both Task 14's chip-out and this teardown probe |
| Pot | **12.0 V**, untouched since `P-06`'s single confirming read; not re-verified at teardown per procedure (no second `vpp` invocation is prescribed at `P-11`) |
| Shield | **Rev 2.0** (operator-declared, silkscreen-authoritative) |

This is A1's own accurate leave-state, whatever it is — it is **not** staged toward any later
cell's needs (A3/B2 needs a Leonardo + Rev 2.0, not this board, and no attempt was made to
arrange that here).
