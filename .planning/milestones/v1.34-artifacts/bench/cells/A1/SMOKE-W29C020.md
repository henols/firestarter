# D-09 smoke check — W29C020 addressability, A1 control arm only

These two invocations sit **outside** the `P-01`...`P-11` step list — a one-time, non-destructive
addressability proof run once for the whole milestone, on A1's control arm only, before the
milestone's first 262144 B write. Repeating it at later positions/cells would break positional
symmetry across the twelve sweep positions.

## Invocation 1 — chip-id (log `16_smoke_id_w29c020`)

`FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/control/.venv/bin/firestarter -p /dev/ttyACM1 id w29c020`

Exit code **0**. Output: `Chip ID check passed for W29C020: (main done) (0.09s)`. The DB records
W29C020 as chip id `0xDA45`; the app confirmed a match against the seated part without naming the
raw id byte pair in its own success line. No forbidden flag used (`-f` was never passed, though it
exists as an option on `id`).

## Invocation 2 — standalone blank check (log `17_smoke_blank_w29c020`)

`FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/control/.venv/bin/firestarter -p /dev/ttyACM1 blank w29c020`

Exit code **1**. Output: `ERROR: Not blank, at 0x000000, v: 0x00`. **This is a valid, expected
outcome, not a failure** — the standalone `blank` command's own purpose here is only to prove the
part answers and is addressable, which it did (a genuine not-blank content report, not a
"chip does not respond" or "chip-id mismatch" refusal). No forbidden flag used (`-f` was never
passed, though it exists as an option on `blank`; `-b`/`--no-blank-check`/`--skip-erase` belong to
`write` and were never invoked here at all).

**Read as follows, per this cell's own instruction:** a not-blank result is a perfectly good
outcome — it proves addressability, which is the whole point. A chip-id mismatch refusal or a
non-responding chip would have been the seating/pin-1 signal this check exists to catch; neither
happened. No re-seat was needed, no forbidden flag was reached for, and `write -b` was never
substituted for this observation.

## Free fact captured while the part was in

Since Phase 153, `-b`/`--no-blank-check` is **unread** on protocols `0x0D` and `0x05`, and
W29C020 is algorithm `0x05` — so the upcoming `write` for this position performs **no** pre-write
blank check on this part at all, regardless of any flag. This standalone `blank` invocation is
therefore the **only** blank observation the whole milestone will ever have for W29C020.

## Verdict

**W29C020 proven addressable on this rig** (D-09 satisfied) before the milestone's first
262144-byte write, which follows immediately as position 2 (`A1__control__w29c020`).
