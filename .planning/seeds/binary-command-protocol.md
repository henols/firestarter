---
title: Binary command protocol (replace jsmn/JSON framing)
trigger_condition: RAM/throughput becomes the binding constraint, or the next protocol-layer milestone opens
planted_date: 2026-07-02
status: dormant
---

# Binary command protocol (replace jsmn/JSON framing)

Replace the jsmn-tokenized JSON command layer with a fixed-layout binary command
decoder, to reclaim RAM (and some flash) and — via a larger `DATA_BUFFER_SIZE` —
speed up programming.

Full measurement rationale: `.planning/notes/binary-protocol-savings-analysis.md`.

## Why (payoff)

- **~512 B RAM reclaimed** (the `static jsmntok_t tokens[64]` array,
  `firestarter.cpp:53`). This is the real prize — a fixed-offset binary format
  needs no token array.
- **~1–1.5 KB flash net** (after a small binary decoder replaces jsmn +
  `json_parser.c`).
- **Faster programming, indirectly:** reclaimed RAM → bigger `DATA_BUFFER_SIZE`
  → fewer ack round-trips on the data path. Commands themselves are tiny and
  infrequent, so the command-frame shrink is not the point.

## Biggest win: the Unos

Uno = 2048 B RAM, buffer currently 512 B; the token array is ~25% of SRAM.
Reclaiming it could ~double the Uno buffer (512 → ~1024). Leonardo (2560 B,
buffer 1024 B) also benefits (→ ~1536, stack margin permitting).

## Scope / shape (rough)

- Fixed-layout binary command frames decoded straight into `firestarter_handle_t`
  (no tokenizer, no string key compares, no `key_parsers` table).
- The address-line / static-high arrays become fixed byte arrays — the current
  jsmn token hog disappears.
- Rides on the existing COBS transport (v1.10) + ack-based chunking (CAP-01);
  this changes the *command* encoding, not the framing/transport.
- Delete `lib/jsmn/`, `src/json_parser.c`, `include/json_parser.h`; retire the
  `parse_json` path in `firestarter.cpp`.

## Cost / risk

- **Breaking wire change** — host (`serial_comm.py`) and firmware must land in
  lockstep (CLAUDE.md protocol-parity rule). Another breaking protocol change on
  the heels of v1.20's `type`-axis removal.
- Loses JSON's human-debuggability on the wire (mitigable with a decode helper).
- Native dispatch tests + golden traces assume JSON input → must be reworked.
- De-risk the *speed* half first (spike below) before committing.

## Next steps when triggered

1. **Spike:** measure real programming-time delta from bumping
   `DATA_BUFFER_SIZE` (e.g. Uno 512→1024, Leonardo 1024→1536) *before* any
   protocol rewrite — confirms the speed payoff is worth a breaking change.
2. A/B stub build to pin the exact flash delta (LTO blocks static measurement).
3. If both check out, scope as a protocol-layer milestone with lockstep host+fw.

## Related

- Note: `binary-protocol-savings-analysis.md`
- Todo: `remove-dead-json-init-sizeof-pointer-bug.md`
- Prior protocol milestones: v1.10 (COBS), v1.12 (dispatch), v1.16 (rebuild),
  v1.19 (naming), v1.20 (protocol-only dispatch)
