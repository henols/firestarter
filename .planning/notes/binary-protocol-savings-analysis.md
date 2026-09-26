---
title: Binary protocol vs jsmn/JSON — flash & RAM savings analysis
date: 2026-07-02
context: Captured during /gsd-explore 2026-07-02. Measurement-backed answer to "how much flash can be saved by removing the JSON parser for a binary protocol?" Companion to seed binary-command-protocol.md.
---

# Binary protocol vs jsmn/JSON — what's actually reclaimable

Measured against the current firmware (`firestarter/`, meta branch
`gsd/v1.20-protocol-only-dispatch-*`), Leonardo `pio run -e leonardo`.

## Starting assumption was wrong

The command parser is **not ArduinoJson**. It is **jsmn** (`lib/jsmn/`, a
minimalist tokenizer, ~366 lines) plus a hand-written `src/json_parser.c`
(~366 lines). So the "JSON is a flash hog" intuition does not apply — jsmn is
already tiny. The savings ceiling is modest for flash and more interesting for RAM.

## Measured baseline (Leonardo)

- Flash: **25316 / 28672 bytes = 88.3%** → ~3356 B free
- RAM:   **1998 / 2560 bytes = 78%** → ~562 B free

## What the JSON layer costs (LTO build → some parts inlined into `main`)

| Component | Where | Size |
|---|---|---|
| `jsoneq_` (PROGMEM key compare) | flash code | 264 B |
| `key_parsers` dispatch table | flash | 64 B |
| JSON field-name strings (`"algorithm"`, `"memory-size"`, …) | flash | ~110 B |
| `parse_json` + `jsmn_parse` bodies | inlined into `main` | est. ~700–1200 B |
| **jsmn token array** `static jsmntok_t tokens[64]` (`firestarter.cpp:53`) | **RAM (.bss)** | **512 B** |

Exact flash figure is blocked by LTO inlining — pinning it needs an A/B stub build.

## Bottom line

- **RAM reclaim ~512 B — the real prize.** A binary format with fixed offsets
  needs no token array at all.
- **Flash reclaim ~1–1.5 KB net** (a binary decoder still costs ~150–300 B).
- **Speed is an *indirect* payoff:** commands are tiny and infrequent, so the
  smaller command frame barely matters. The win is that reclaimed RAM feeds a
  larger `DATA_BUFFER_SIZE`, which cuts ack round-trips on the *data* path.

## The token array can't be cheaply trimmed

`NUMBER_JSNM_TOKENS = 64` (= 512 B). A full `write`/`read` command carries
`bus-config` with a 20-element `address_lines` array + `static-high`, and each
array element is its own jsmn token, so a real command is ~45–50 tokens. Only
~15 tokens of slack → trimming buys maybe ~96 B and is risky. Binary reclaims
the *whole* 512 B because the address array becomes fixed bytes, not tokens.
This is exactly the structured data JSON is worst at.

## Where the win is biggest: the Unos

- **Uno**: 2048 B RAM total, current `DATA_BUFFER_SIZE` = 512 B. The 512 B token
  array is ~25% of SRAM. Reclaiming it could roughly **double** the Uno buffer
  (512 → ~1024) — the largest relative win.
- **Leonardo**: 2560 B RAM, buffer already 1024 B. Also benefits, but realistic
  growth is ~1024 → ~1536 (must keep stack margin; currently only 562 B free).

## Caveats on the speed claim

1. You cannot pour all 512 B into the buffer — stack headroom is required.
2. Actual speedup depends on the ack-turnaround-to-transfer ratio at 250k baud —
   measurable but currently unknown → see the spike in the seed's next-steps.

## Incidental find (latent bug)

`json_parser.c:42` `json_init()` computes `sizeof(tokens)/sizeof(tokens[0])` on
a **pointer** parameter → evaluates to `0`, passing `num_tokens=0` to jsmn.
Appears dead (live path in `firestarter.cpp:56` calls `jsmn_parse` directly with
`NUMBER_JSNM_TOKENS`), but it is a latent trap. Tracked as a todo.
