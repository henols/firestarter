---
artifact: write-program-stall finding
type: bench-evidence
status: localized, root-cause OPEN (needs firmware-side debug)
scope: SEPARATE from v1.9 read-RCA (write/program path; GATE-1.8 ring-fenced reads)
recorded: 2026-06-01
operator_witnessed: true
---

# Write/Program Stall — both controllers (2026-06-01)

## Observation

Full write_test (port-aware copy) run on both assemblies:

| Assembly | Write result |
|----------|--------------|
| Uno + Rev 2.0 (3.0.0b5) | **every write → "Timeout waiting for a significant response"** |
| Leonardo + Rev 0 (3.0.0b6) | blank-check writes abort "Not blank"; the one `-b` (skip-blank-check) **program attempt → same Timeout** |

Reads and blank-checks (the *outgoing*-data path) work on both. Only **programming
(the incoming-data path) stalls.** Not controller-specific, not firmware-version
specific, NOT introduced by the 44-02 read-timing knobs (read-path only).

## Localization (verbose trace, Leonardo, `write -f -b`)

```
INIT: (init done)                         ← init OK
WARN: VPP is high: 13.0V > 12.0V          ← VPP ~1V over the 12.0V target
WARN: Chip ID 0xda01 does not match 0xda08
Main start                                ← enters write MAIN phase
Communication error during WRITE: Timeout ← firmware never emits the data request
```

The write MAIN phase is **pull-based**: `_process_incoming_data()`
(`firestarter/src/eprom_operations.cpp:57-74`) is supposed to emit
`MSG_OK_REQ_DATA` when `op_get_message()` returns `OP_MSG_INCOMPLETE`, prompting
the host to send the first chunk. The host enters "Main start", sends OK, and
**never receives `MSG_OK_REQ_DATA`** → times out. So the firmware enters write
MAIN but does not complete the data-request handshake.

## Candidate root causes (untested)

1. **Warning-desync:** the two `WARN:` lines emitted during INIT
   (`VPP high`, `chip-id mismatch`) may desync the host's response parser at the
   INIT→MAIN boundary, so the host misreads/ misses `MSG_OK_REQ_DATA`.
2. **`op_get_message()` blocking:** if it blocks reading host data before the
   request is sent, firmware↔host deadlock (firmware waits for data, host waits
   for request). Read path uses `_process_outgoing_data` and is unaffected.
3. **VPP-high gate:** VPP reading 13.0V > 12.0V target — a guard/wait in the
   program path could stall (note: actual VPP rail metered 12.2V; the 13.0V is the
   Leonardo's +0.7V calibration offset, so this may be a *false* over-voltage).

## Recommended next step

This is a **separate write/program bug**, outside the v1.9 read-RCA scope. It needs
firmware-side instrumentation (debug logging around the INIT→MAIN transition and
`op_get_message`) — a structured `/gsd-debug` session, not more black-box bench
runs. Capture a clean repro: `firestarter -v -p <PORT> write -f -b W27C512 <1KB>`
stalls reproducibly at "Main start".

## Note

Chip-ID `0xda01` (vs `0xda08`) is stable across all session chips — possibly a
data-bus-integrity artifact of the test chips / Rev 0 shield, or genuinely
non-W27C512 silicon. Worth confirming with a known-good W27C512 on a known-good
assembly before deep firmware debugging, to rule out a bad-chip confound.
