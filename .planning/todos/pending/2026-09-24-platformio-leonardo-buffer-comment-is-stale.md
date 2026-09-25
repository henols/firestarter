---
created: 2026-09-24T00:00:00Z
title: platformio.ini Leonardo comment says the host reads DATA_BUFFER_SIZE from the identity string
area: firmware
found_in_phase: exploration (CLAUDE.md audit)
files:
  - firestarter_fw/platformio.ini (lines 67-69 — the stale comment above `-D DATA_BUFFER_SIZE=1024`)
  - firestarter_fw/include/firestarter.h (lines 40-43 — states the identity string no longer carries it)
  - firestarter_app/firestarter/eprom_operations.py (`_calculate_buffer_size` — reads `firmware_max_chunk`)
---

## Problem

The `[env:leonardo]` comment in `firestarter_fw/platformio.ini` says: "The host reads
DATA_BUFFER_SIZE from the FW identity string and sizes its chunks to 1022". That mechanism was
removed. `firestarter.h` says the identity string is now `<version>:<board>` only. The buffer size
is sent as a u16 param on every `MSG_OK_READY` ack. The host reads that value
(`firmware_max_chunk`) and falls back to 512 when it is absent.

## Fix

Rewrite the comment to name the `MSG_OK_READY` ack as the transport. Check the "1022" figure against
the value `_calculate_buffer_size` really returns before keeping it.
