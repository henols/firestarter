# Phase 53: Byte-Exact Bench Verification (hardware-gated) — Research

**Researched:** 2026-06-02
**Domain:** Fault-injection harness + write-leg verification procedure + bench evidence artifact
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Carried forward — LOCKED upstream (Phases 49–52; do NOT re-litigate):**
- Frame contract = `[COBS(payload + CRC8)][0x00 delimiter]`; CRC8-CCITT poly `0x07`, seed `0x00`, no reflection, no final XOR, over the raw payload. Pinned by Phase 52 golden vectors.
- Resync = bounded-desync + fail-fast (Phase 50 D-01): on CRC8/COBS failure the receiver discards bytes to the next `0x00` and surfaces a clean error immediately (no 2 s timeout cascade); the *following* frame re-anchors. NO transparent auto-recovery of the corrupted frame.
- `len_u16` length prefix REMOVED (Phase 50). The only corruptible structural elements are the **CRC8 byte** and the **`0x00` delimiter**.
- Transport-exoneration scope (v1.9-COBS-DECISION §2.0): a green re-test rules serial out as a confounder; it is NOT a hardware fix.

**D-01: Inject in BOTH directions.**
- host→fw command frame deliberately corrupted before send — exercises firmware decoder on the real wire.
- fw→host read frame mutated via a host receive-path hook — exercises the host decoder resync.

**D-02: Fault forms = corrupted CRC8 byte + dropped/missing `0x00` delimiter.** Spurious extra `0x00` mid-frame is OPTIONAL (planner's discretion).

**D-03: Pass criterion = clean immediate error + next transfer byte-exact.** Error must be sub-second (NOT a 2 s timeout cascade). Both claims must be asserted.

**D-04: N=5 consecutive transfers per clean board** (Uno + Leonardo), all SHA-256-identical.

**D-05: Self-consistency mandatory.** Strong form (if original W27C512 chip available): ALSO byte-match GATE-1.8d baselines at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/run_0X.bin`.

**D-06: Write leg = write→read-back→compare, N=5 cycles.** Independent host-side SHA-256 compare — not firmware verify.

**D-07: Clean-board proof targets shield Rev 2.0.** Operator MUST confirm actual silkscreen rev at bench time.

**D-08: N=5 with explicit timeout-retry logging** for uno328pb. LOG raw timeouts and retries — do NOT abort.

**D-09: Cite documented pre-hardening "before" shape.** Do NOT re-flash old firmware. Hardened "after" shape is the only new capture.

**D-10: Record a STRUCTURED exoneration verdict block** stating: (1) observed hardened failure shape, (2) whether shape changed vs before-shape, (3) explicit exoneration line per v1.9-COBS-DECISION §2.0.

**D-11:** Artifact lives under `.planning/v1.10/bench-verification/`, mirroring `.planning/v1.6/consistency-check-runs/` layout.

### Claude's Discretion
- Exact fault-injection harness implementation (host debug flag / test-only wedge vs dedicated dev subcommand) and the fw→host receive-path hook mechanism — must NOT alter production transport code paths.
- Whether to record measured time-to-error number (D-03 discretion) and optional spurious-`0x00` fault form (D-02).
- Exact artifact filenames, directory sub-structure, and summary-doc format under `.planning/v1.10/bench-verification/` (D-11).
- Precise source image used for write-leg cycles (D-06) and data-block content patterns.

### Deferred Ideas (OUT OF SCOPE)
- v1.9 read-bug RCA + per-shield fix (Bug A Modified Rev 0, Bug B Rev 2.0) — deferred to v1.9 Phase 45+.
- A/B re-flash of pre-hardening firmware on the uno328pb for fresh "before" capture.
- Spurious/extra-`0x00` fault form + measured error-latency number (optional).
- WR-01 — frame-level deadline on the firmware COBS decoder byte-wait — out of v1.10 scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| XACT-01 | Transport proven byte-exact on a clean board — N consecutive framed read AND write transfers are byte-identical on Uno (512 B) and Leonardo (1024 B); hardened path reproduces GATE-1.8d W27C512 N=5 baselines | `dev consistency-check --runs 5` covers read leg; new `dev write-cycle` or equivalent covers write leg; both call existing `_operation_context` + `_run_state_machine` |
| XACT-02 | Resync proven under fault injection — deliberately corrupted byte recovers within one packet via the delimiter, not a 2-second timeout cascade, demonstrated by a host-side or bench fault-injection harness | Fault-injection wedge attaches at `send_json_command()` (host→fw outgoing) and at `_read_and_parse_lines()` receive path (fw→host); both paths reachable without altering production code via a `_fault_inject_` env-var or dev-subcommand mode |
| XACT-03 | uno328pb re-test recorded — consistency-check read re-run on the hardened firmware; result documents whether hardened transport changes the failure shape with explicit transport-exoneration per COBS-DECISION §2.0 | `dev consistency-check --runs 5` with timeout mapped to verdict 2 (not 1); before-shape already documented in `.planning/v1.6-EVIDENCE.md`; planner cites it verbatim |
</phase_requirements>

---

## Summary

Phase 53 is a purely operational and instrumentation phase — the transport code itself is frozen. All three requirements (XACT-01/02/03) demand concrete bench execution supported by:

1. A **fault-injection harness** that can corrupt outgoing frames (host→fw, primary) and incoming frames (fw→host, secondary) without touching any production transport code path.
2. A **write-leg N-cycle procedure** that chains `erase_eprom` + `write_eprom` + a read-back SHA-256 compare, reusing the exact same state-machine infrastructure that `consistency_check_eprom()` uses for its read loop.
3. **Structured operator-witnessed bench runs** with pre-defined pass criteria, timeout-retry logging for uno328pb, and a firm evidence-artifact layout under `.planning/v1.10/bench-verification/`.

The key research findings are: (a) all required entry-points exist and are locatable to exact functions and line numbers; (b) the cleanest fault-injection seam is a `_debug_corrupt_outgoing_frame()` wrapper on `send_json_command()` enabled by a dev-subcommand flag or env-var, not production-path pollution; (c) the fw→host direction's cleanest hook is a mutating shim between the COBS-delimiter detection and `_crc8_ccitt` verification inside a test-only subclass or monkey-patched `_read_and_parse_lines`; (d) the write-leg fits naturally as a new `dev write-cycle` subcommand that calls existing `erase_eprom`, `write_eprom`, and the read machinery from `consistency_check_eprom()`.

**Primary recommendation:** Implement the fault-injection harness as a `dev fault-inject` subcommand (or a `--fault-inject` flag on `dev consistency-check`) that sets a per-invocation hook in `serial_comm.py`, rather than altering any `frame_parser.py` production path.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Fault-injection host→fw (D-01 primary) | Host CLI (Python) | — | The host assembles the outgoing COBS frame in `send_json_command()`; corruption inserted there is already on the wire before the firmware sees it |
| Fault-injection fw→host (D-01 secondary) | Host CLI (Python) | — | The host decoder in `_read_and_parse_lines()` is where the receive-path hook must mutate data; no firmware change needed |
| Write-leg byte-identity (D-06) | Host CLI (Python) | Firmware (no change) | Host calls erase/write/read through existing state machine; independent SHA-256 compare is purely host-side |
| Read-leg byte-identity (D-04) | Host CLI (Python) | Firmware (no change) | `dev consistency-check --runs 5` unchanged |
| uno328pb re-test (D-08/09/10) | Host CLI (Python) | Firmware (hardened v1.10) | Re-run existing command on hardened firmware; timeout maps to verdict 2 |
| Evidence artifact (D-11) | Host (file I/O) | — | Directory layout + summary doc written by the operator/harness post-run |
| Bench protocol (D-07) | Operator | Claude (task scripts) | Shield rev confirmation, port identity, chip-out before sideload are operator manual steps |

---

## Standard Stack

This phase adds NO new dependencies. All implementation uses existing installed packages.

### Core (already installed)

| Library | Version | Purpose | Why Used |
|---------|---------|---------|-----------|
| `hashlib` (stdlib) | Python 3.x | SHA-256 comparison for read-back and baseline hash-match | Already used in `consistency_check_eprom()` — `hashlib.sha256(run_path.read_bytes()).hexdigest()` |
| `click` | (project version) | CLI subcommand for `dev fault-inject` or `dev write-cycle` | All `dev` subcommands use Click; pattern established in `cli_handlers.py` |
| `pyserial` | (project version) | Serial I/O; `send_bytes()` is the injection point for host→fw corruption | Already the transport layer |

### No New Packages

This phase does not install external packages. The Package Legitimacy Audit section is therefore omitted per the "Skip condition" in the protocol.

---

## Architecture Patterns

### System Architecture Diagram

```
                 Phase 53 Operational Flow
                 ========================

CLEAN-BOARD READ LEG (XACT-01):
  [Operator bench] → dev consistency-check --runs 5
       ↓
  consistency_check_eprom() → _run_state_machine() × 5
       ↓
  per-run SHA-256 compare → verdict 0/1/2
       ↓
  OPTIONAL: sha256(run_01.bin) vs GATE-1.8d baseline bins

WRITE LEG (XACT-01 D-06):
  [Operator bench] → dev write-cycle --runs 5 --source <image>
       ↓
  erase_eprom() → write_eprom(source_image) → consistency_check_read() × 5
       ↓
  sha256(readback) vs sha256(source_image) per cycle

FAULT-INJECTION HOST→FW (XACT-02 primary):
  dev fault-inject (or --fault-inject flag)
       ↓
  send_json_command() → [hook] corrupt CRC8 byte or drop 0x00 delimiter
       ↓
  firmware decoder → detects CRC8 mismatch → drains to 0x00 → returns error
       ↓
  host receives error response (sub-second, not 2 s timeout)
       ↓
  next transfer → normal operation, byte-exact

FAULT-INJECTION FW→HOST (XACT-02 secondary):
  _read_and_parse_lines() → [hook] mutate received COBS body
       ↓
  cobs_decode() or _crc8_ccitt() raises ValueError / mismatch
       ↓
  host surfaces clean error (not a hang) → next frame decodes clean

UNO328PB RE-TEST (XACT-03):
  dev consistency-check --runs 5 [timeout-retry logging enabled]
       ↓
  timeouts → verdict 2 (hw-error), NOT verdict 1 (FAIL)
       ↓
  structured exoneration verdict block written to artifact
```

### Recommended Project Structure (additions to existing layout)

```
firestarter_app/firestarter/
├── cli_handlers.py         # add: dev write-cycle subcommand (~50 lines)
│                           # add: dev fault-inject subcommand OR --fault-inject flag
├── eprom_operations.py     # add: write_cycle_eprom() method (~80 lines)
│                           # reuses: _operation_context, _run_state_machine,
│                           #         _main_phase_send_data, _main_phase_read_data
├── serial_comm.py          # add: _fault_inject_hook (None by default)
│                           #      inject point in send_json_command()
│                           #      inject point in _read_and_parse_lines() receive path

.planning/v1.10/bench-verification/
├── clean-board/
│   ├── run_01.bin ... run_05.bin   # per-run binaries (Uno + Leonardo read leg)
│   └── write-cycle/
│       ├── cycle_01_readback.bin ... cycle_05_readback.bin
│       └── source_image.bin
├── fault-injection/
│   └── fault-inject-log.txt        # log of corrupt-frame errors + recovery evidence
├── uno328pb/
│   ├── run_01.bin ... run_05.bin   # or timeout log if no complete runs
│   └── exoneration-verdict.txt
└── SUMMARY.md                      # operator attestation + SHA table + verdict block
```

---

## Specific Question Answers

### Question 1: Write-Leg (D-06)

**Cleanest approach: a new `dev write-cycle` subcommand with a new `write_cycle_eprom()` method.**

The existing `consistency_check_eprom()` method (eprom_operations.py:497–696) performs the read leg as N calls to `_run_state_machine(..., main_phase_handler=self._main_phase_read_data, ...)` inside an `_operation_context` with `COMMAND_READ`. The write-leg procedure needs the same infrastructure plus erase and write phases.

**Exact entry points the write-leg calls:**

| Step | Entry Point | File | Location |
|------|-------------|------|---------|
| 1. Erase | `erase_eprom(eprom_name, eprom_data_dict, operation_flags)` | `eprom_operations.py` | Line 910 — uses `COMMAND_ERASE` → `_run_state_machine()` with no main handler |
| 2. Write | `write_eprom(eprom_name, eprom_data_dict, input_file_path, operation_flags)` | `eprom_operations.py` | Line 838 — uses `COMMAND_WRITE` → `_run_state_machine(..., main_phase_handler=self._main_phase_send_data, ...)` |
| 3. Read-back N times | `consistency_check_eprom()` read loop machinery | `eprom_operations.py` | Lines 573–631 — the `_operation_context(COMMAND_READ)` + `_run_state_machine(_main_phase_read_data)` block is the reuse seam |
| 4. SHA-256 compare | `hashlib.sha256(run_path.read_bytes()).hexdigest()` vs `hashlib.sha256(open(source_image,'rb').read()).hexdigest()` | New code in `write_cycle_eprom()` | Independent host-side, does NOT use firmware verify |

**Why NOT a flag on `dev consistency-check`:** The existing command has a single `COMMAND_READ` operation context and no write-setup path. Adding erase/write as a flag would significantly complicate the existing clean-path code. A separate `dev write-cycle` subcommand following the same Click pattern is cleaner and keeps the existing command's reuse-not-duplicate guarantee untouched (per consistency_check_eprom docstring line 525: "Do NOT refactor into a parallel read implementation").

**Implementation sketch for `write_cycle_eprom()`:**
```python
def write_cycle_eprom(self, eprom_name, eprom_data_dict, source_image_path,
                      runs=5, output_dir=None, operation_flags=0):
    """
    Erase → write source_image → read-back N times → SHA-256 compare.
    Returns 0 (all cycles match source), 1 (mismatch), 2 (hw-error).
    """
    source_sha = hashlib.sha256(Path(source_image_path).read_bytes()).hexdigest()

    for cycle_i in range(1, runs + 1):
        # Step 1: Erase
        if not self.erase_eprom(eprom_name, eprom_data_dict, operation_flags):
            return 2

        # Step 2: Write
        if not self.write_eprom(eprom_name, eprom_data_dict, source_image_path,
                                operation_flags):
            return 2

        # Step 3: Read-back — reuse _operation_context + _run_state_machine
        readback_path = output_path / f"cycle_{cycle_i:02d}_readback.bin"
        with self._operation_context(eprom_name, eprom_data_dict,
                                     COMMAND_READ, operation_flags) as (cmd_data, _, op_name):
            if not cmd_data:
                return 2
            with open(readback_path, "wb") as fh:
                def _writer(address, data_chunk, _fh=fh, _start=cmd_data.get("address",0)):
                    _fh.seek(address - _start)
                    _fh.write(data_chunk)
                is_ok, _ = self._run_state_machine(
                    op_name,
                    main_phase_handler=self._main_phase_read_data,
                    start_addr=cmd_data.get("address", 0),
                    end_addr=cmd_data.get("memory-size", 0),
                    process_data_chunk_callback=_writer,
                )
        if not is_ok:
            return 2

        # Step 4: Independent host-side SHA-256 compare
        readback_sha = hashlib.sha256(readback_path.read_bytes()).hexdigest()
        if readback_sha != source_sha:
            return 1  # mismatch — byte-identity broken

    return 0  # all cycles match source image
```

[VERIFIED: pattern matches existing _operation_context usage at lines 580–614 of eprom_operations.py]

---

### Question 2: Fault-Injection Harness (D-01/D-02/D-03)

**The cleanest seam is a per-instance `_fault_inject_hook` attribute on `SerialCommunicator` (or `EpromOperator`), set only when the `dev fault-inject` subcommand is active.**

#### host→fw outgoing-command corruption (primary)

**Injection point:** `serial_comm.py:send_json_command()` (lines 156–175).

The method assembles:
```python
json_bytes = json.dumps(command_dict, separators=(",", ":")).encode("ascii")
crc = _crc8_ccitt(json_bytes)
body = cobs_encode(json_bytes + bytes([crc]))
frame = body + b"\x00"
return self.send_bytes(frame)
```

**Hook insertion** (immediately before `self.send_bytes(frame)`, after frame is assembled):
```python
if self._fault_inject_outgoing:
    frame = self._fault_inject_outgoing(frame)
```

**Fault forms at this seam:**

| Fault Form | Corruption | Implementation |
|------------|-----------|----------------|
| Corrupted CRC8 byte | Flip one bit in `frame[-2]` (last byte before delimiter 0x00) | `frame = frame[:-2] + bytes([frame[-2] ^ 0x01]) + b"\x00"` |
| Dropped 0x00 delimiter | Remove the trailing `\x00` | `frame = frame[:-1]` — firmware waits for delimiter until inter-byte timeout fires |

This approach leaves `send_json_command()` production logic completely unchanged; the hook only fires when `self._fault_inject_outgoing` is not None (default None = off).

**Default state:** `self._fault_inject_outgoing = None` — production path completely unaffected.

#### fw→host receive-path mutation (secondary)

**Injection point:** `serial_comm.py:_read_and_parse_lines()` generator (lines 240–363).

The GATE-1.8d ring-fence comment (lines 229–238) explicitly states: "Structural-only changes here (e.g. type hints on the signature) are OK; any change to the byte-by-byte read loop... MUST be flagged."

**This means the receive-path hook MUST NOT modify `_read_and_parse_lines()` body.** The cleanest approach that respects the ring-fence is a **test-only subclass** of `SerialCommunicator` or a **post-receive mutation hook applied in `EpromOperator`** rather than inside the generator body.

Option A (preferred — ring-fence safe): Add a `_fault_inject_incoming_frame` attribute to `SerialCommunicator`. After the generator yields a `Response` with a `payload`, the `_main_phase_read_data` handler in `eprom_operations.py` calls `process_data_chunk_callback(start_addr, payload)`. A thin wrapper callback applied by the `dev fault-inject` command can mutate the payload bytes BEFORE the SHA-256 is computed on the host side. This exercises the host decoder's CRC8 verification on a mutated payload.

Option B (also ring-fence safe): At the COBS-frame receive path inside `_read_and_parse_lines()`, the body bytes are passed to `self._decode_id_frame(frame_len, body)` (line 340). A subclass can override `_decode_id_frame` to inject a one-bit mutation in `body` before decoding, then pass the mutated body to the real decoder. This causes `_crc8_ccitt` to fail, which `codec.decode_id_frame` surfaces as None, which `_read_and_parse_lines` then handles as a re-sync.

**Recommended: Option B** — it exercises the actual COBS+CRC8 path closest to where real corruption would occur.

```python
class FaultInjectingSerialCommunicator(SerialCommunicator):
    """Test-only subclass; not imported in production."""
    def __init__(self, *args, corrupt_incoming_frame=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._corrupt_incoming_frame = corrupt_incoming_frame
        self._fault_fired = False

    def _decode_id_frame(self, frame_len, body):
        if self._corrupt_incoming_frame and not self._fault_fired:
            self._fault_fired = True  # corrupt once, then recover
            body = body[:-1] + bytes([body[-1] ^ 0x01])  # flip CRC8 byte
        return super()._decode_id_frame(frame_len, body)
```

This subclass is created only within the `dev fault-inject` command scope — never in production. The ring-fence body of `_read_and_parse_lines` is byte-identical.

#### Asserting D-03 (clean immediate error + next transfer byte-exact)

**Time-to-error assertion:**

The host→fw direction surfaces immediately because `send_bytes()` returns and then `get_response()` awaits a firmware `ERROR:` or `OK:` response. With the hardened bounded-desync posture (Phase 50 D-01), the firmware drains to the next `0x00` and returns an error message instead of hanging for 2 s. The host-side timer is:

```python
t0 = time.time()
# send corrupted frame via send_json_command() with fault hook
error_response = comm.get_response(timeout=2.0)  # expect ERROR: within sub-second
latency = time.time() - t0
assert latency < 1.0, f"Expected sub-second error, got {latency:.3f}s"
assert error_response.type == "ERROR"
```

**Next-transfer success assertion:**

After the corrupted-frame error, send a normal (uncorrupted) frame and assert `byte_exact_result == source_sha`. The connection is NOT closed and reopened between the corrupt frame and the recovery frame — the resync proves recovery on the SAME open connection.

---

### Question 3: uno328pb Re-Test (D-08/D-09/D-10)

**Pre-hardening "before" shape (D-09) — verified in `.planning/v1.6-EVIDENCE.md`:**

The documented pre-hardening uno328pb failure shape is sourced from Plan 27-04 (2026-05-26 bench session). Key datapoints:

| Metric | Pre-hardening value | Source |
|--------|---------------------|--------|
| Per-run byte-value distribution | 99.4% `0xff` (floating bus pattern) | `.planning/v1.6-EVIDENCE.md` §"Plan 27-04 bench A/B test results", pre-fix uno328pb row |
| Within-session stability | 100% of 65536 positions unstable across N=5 | Same section |
| Pairwise divergence (run_01 vs run_02) | 0.47% | Same — though run_01 vs run_03 = 99.99% (chaotic) |
| Timeout pattern | 1st attempt timed out at run_05; 2nd attempt required `--runs 3` after 4× N=5 timeouts | `.planning/v1.6-EVIDENCE.md` §"Bench-instability finding" |
| Firmware at time of pre-fix reading | `fdb1ed5` (v1.6-read-bug~2 = pre-Phase-28) | Same; `.hex` SHA = `d9e51b7e…` (byte-identical to post-fix uno328pb build = 62,854 B) |
| Description | "floating bus / chaotic, not structured EPROM data" | Same |

The REQUIREMENTS.md's "timeout + ~99% 0xff-drift instability" phrasing maps to: most runs return ~99.4% `0xff` bytes (bus floats high) plus occasional chaotic runs. This is the pre-hardening ground truth the D-10 verdict block must cite verbatim.

**`dev consistency-check --runs 5` covers D-08:** The 3-way verdict contract already maps hardware/timeout errors to verdict 2 (not 1) per the docstring at line 515: `"2 -- hardware / serial / timeout error"`. The `_run_state_machine` catch block (lines 292–294 of eprom_operations.py) returns `(False, str(e))` on `SerialTimeoutError`, which then maps to `return 2` at lines 620–624 of `consistency_check_eprom()`. Timeout-retry logging means the caller should loop around the outer `for i in range(1, runs + 1):` block with a retry counter, logging each timeout as `logger.warning("Run {i}: timeout — retrying")` before returning verdict 2.

**D-10 structured exoneration verdict block — template:**

```
## uno328pb Transport-Exoneration Verdict

Board: uno328pb (/dev/ttyUSB0 — verify controller: at session start)
Shield: Rev 2.2 (operator-confirmed silkscreen)
Firmware: v1.10-serial-transport-hardening tip

Pre-hardening "before" shape (from .planning/v1.6-EVIDENCE.md Plan 27-04, 2026-05-26):
  - Per-run: ~99.4% 0xff (floating bus); 100% positions unstable across N=5
  - Timeout pattern: 1st attempt timed out at run_05; required N=3 after 4× N=5 timeouts
  - Pairwise divergence (run_01 vs run_02): 0.47% nominal, 99.99% run_01 vs run_03

Observed hardened "after" shape:
  - [FILL AT BENCH: N completed runs, timeout count, retry count]
  - [FILL AT BENCH: per-run SHA-256 distribution, 0xff%, 0x00%]
  - [FILL AT BENCH: pairwise divergence if runs completed]

Shape changed vs before-shape: [YES/NO/PARTIAL — describe]

Verdict: transport-exoneration per v1.9-COBS-DECISION §2.0 — NOT a per-shield
hardware fix; the actual RCA stays deferred to v1.9 Phase 45+.

[If shape changed or same, the conclusion is identical: this result characterizes
whether COBS hardening affected the uno328pb failure mode. It does not diagnose
the hardware cause (Bug B, Rev 2.0 /CE-OE timing, ATmega328PB-specific read
protocol). Those remain v1.9 Phase 45+ scope.]
```

---

### Question 4: Evidence Artifact Layout (D-11)

**GATE-1.8d baseline directories — confirmed to exist:**

```
.planning/v1.6/consistency-check-runs/
├── W27C512-leonardo-20260526-155021-v2/          # run_01.bin..run_05.bin
│   run_01.bin SHA: 8e064f447ef7e721...
├── W27C512-leonardo-20260526-155617-v2-rev20/    # run_01.bin..run_05.bin (Rev 2.0 canonical)
│   run_01.bin SHA: 19710f6e52434292...            ← GATE-1.8d Rev 2.0 reference
└── W27C512-leonardo-20260526-160035-v2-rep/      # run_01.bin..run_05.bin (replication)
    run_01.bin SHA: b1874d1ee835d74e...
```

Total: **15 baseline binary files** across 3 directories (5 runs × 3 sessions). [VERIFIED: directory listing confirmed, SHA prefixes captured]

The `W27C512-leonardo-20260526-155617-v2-rev20/` directory is the **Rev 2.0 canonical baseline** (Rev 2.0 shield, same shield class as D-07 target). The SHA `19710f6e…` is the strong-form hash-match target for D-05.

**Phase 53 artifact layout mirrors this:**

```
.planning/v1.10/bench-verification/
├── clean-board-uno/
│   └── read-leg/
│       ├── run_01.bin ... run_05.bin
│       └── sha256sums.txt
├── clean-board-leonardo/
│   └── read-leg/
│       ├── run_01.bin ... run_05.bin
│       └── sha256sums.txt          # compare vs v1.6 baselines (D-05)
│   └── write-leg/
│       ├── source_image.bin
│       ├── cycle_01_readback.bin ... cycle_05_readback.bin
│       └── sha256sums.txt
├── fault-injection/
│   ├── fault-inject-outgoing-log.txt   # host→fw corruption: error type, latency, recovery
│   └── fault-inject-incoming-log.txt   # fw→host mutation: error type, recovery
├── uno328pb/
│   ├── run_01.bin ... run_0X.bin       # however many completed before timeout(s)
│   ├── timeout-retry-log.txt
│   └── exoneration-verdict.txt         # D-10 structured block
└── SUMMARY.md
    # Contents:
    # - Operator attestation: boards, shield revs (D-07), date
    # - SHA-256 table for all read/write runs
    # - GATE-1.8d baseline hash-match result (strong-form or self-consistency-only)
    # - Fault-injection summary: both directions, error latency, recovery confirmed
    # - uno328pb before/after shape comparison + exoneration verdict
    # - Explicit milestone claim: "transport is a settled variable for v1.9 RCA"
```

---

### Question 5: Bench Protocol (Hardware-Gated)

**Every bench task MUST encode these preconditions as MANDATORY steps:**

1. **Chip-out before sideload** (per `feedback_chip_out_before_sideload`): Any task that calls `pio run -t upload`, `avrdude`, or `firestarter fw -i` MUST begin with an operator confirmation that the chip is OUT of the socket. `pio run -t upload` drives the data/address/control bus during flash; voltage swings can damage EPROMs/SRAMs in socket.

2. **Per-port controller-identity verification** (per `feedback_verify_port_identity_each_task`): Every bench task MUST begin with `firestarter -p <port> fw` and verify the `controller:` substring matches the expected board. ACM numbers shuffle across USB unplug/replug. Run this query at the START of each task, not once at session start.

3. **Operator-confirmed shield rev** (per `user_shield_revisions` and D-07): The EEPROM `hw_revision` byte cannot distinguish Rev 2.2 / Rev 2.0 / Modified Rev 0. The operator MUST declare which silkscreen rev is physically on the bench. For Phase 53, the D-07 target is **Rev 2.0** for the clean-board proof. Record the declared rev in the artifact.

4. **uno328pb board on `/dev/ttyUSB0`** (per `project_bench_findings_v15`): programmer_id="urclock"; sideload via `pio run -e uno328pb -t upload --upload-port /dev/ttyUSB0` or `avrdude -c urclock -b 115200`. Verify controller reports `uno328pb` (Case A) before attempting reads.

**Bench tasks are operator-witnessed / NOT autonomous.** Claude cannot drive the physical bench independently (chip handling, multimeter, USB insertion). Bench execution tasks in the plan must include explicit `[OPERATOR: do X]` steps and must not be marked as fully autonomous.

---

### Question 6: Validation Architecture (Nyquist split)

See the `## Validation Architecture` section below.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SHA-256 of binary files | Custom hash loop | `hashlib.sha256(path.read_bytes()).hexdigest()` | Already used in `consistency_check_eprom()` at line 631 |
| COBS encode/decode | Rewrite | `cobs_encode()` / `cobs_decode()` in `frame_parser.py` (lines 58–128) | Phase 52 golden-vector pinned; canonical implementation |
| CRC8-CCITT | Rewrite | `_crc8_ccitt()` in `frame_parser.py` (line 50–55) | 256-byte lookup table; pinned by `test_messages` Unity suite |
| Read-N-times-and-compare loop | New implementation | `consistency_check_eprom()` (eprom_operations.py:497) | Reuse-not-duplicate per docstring line 525; the RCA diagnostic uses this exact path |
| Write-then-erase | New state machine | `write_eprom()` (line 838) + `erase_eprom()` (line 910) | Both call `_run_state_machine`; no new state machine needed |
| Serial port management | Custom serial handling | `SerialCommunicator` (serial_comm.py:90) | Established, tested, contains the atomic-write mandate |

---

## Common Pitfalls

### Pitfall 1: Corrupting the CRC8 of a Non-Existent Byte Position
**What goes wrong:** The host→fw COBS frame is `COBS(json_bytes + CRC8_byte) + 0x00`. The CRC8 byte is the LAST byte of the pre-COBS payload, which becomes `frame[-2]` (second to last, since `frame[-1]` = `0x00` delimiter). Corrupting `frame[-1]` removes the delimiter, which is a DIFFERENT fault form. Corrupting `frame[-3]` hits a COBS-encoded body byte, not the CRC.
**How to avoid:** Identify CRC8 position by reversing COBS decode: `cobs_decode(frame[:-1])[-1]` is the CRC8 byte's position. OR: Since the CRC8 byte is always the last pre-COBS byte, the encoded CRC8 is always in the last COBS run code group — `frame[-2]` is the byte immediately before the `0x00` delimiter, which is the encoded CRC8 byte.

### Pitfall 2: Closing the Serial Connection Between Corrupt and Recovery Frames
**What goes wrong:** D-03 requires "next transfer on the same open connection." If the fault-injection harness closes and reopens the port, the recovery is not demonstrated to be part of the COBS resync — it's just a fresh connection.
**How to avoid:** The fault-injection harness must keep the connection alive across the corrupt frame and the recovery frame. Use `_operation_context` if possible, or hold `self.comm` explicitly between two sequential operations.

### Pitfall 3: Mapping uno328pb Timeouts to Verdict 1 (FAIL) Instead of Verdict 2 (hw-error)
**What goes wrong:** `_run_state_machine` catches `SerialTimeoutError` and returns `(False, str(e))`. The caller in `consistency_check_eprom()` maps `is_ok == False` to `return 2`. But a naive outer retry loop might re-enter the loop and eventually produce a `return 1` (divergent SHAs) if some runs complete and others don't.
**How to avoid:** Any partial run (timeout before completion) must be logged as a retry and the run slot re-attempted, NOT counted as a divergent run. Only runs that complete fully (65,536 bytes for W27C512) contribute to the SHA comparison. Incomplete runs → verdict 2 path.

### Pitfall 4: fw→host Hook Modifying `_read_and_parse_lines()` Body (Ring-Fence Violation)
**What goes wrong:** `_read_and_parse_lines()` is ring-fenced by the GATE-1.8d comment at lines 229–238 of serial_comm.py. Any change to its body "MUST be flagged and deferred to v1.9 alongside binary re-validation."
**How to avoid:** Use Option B (subclass `SerialCommunicator`, override `_decode_id_frame`) or Option A (mutation wrapper in the callback chain in `eprom_operations.py`). NEVER modify `_read_and_parse_lines()` body for Phase 53.

### Pitfall 5: `--fault-inject` Flag on `dev consistency-check` Contaminating the Read Baseline
**What goes wrong:** If the fault-injection flag shares a code path with the normal read path, a configuration mistake could corrupt production reads and produce a misleading baseline binary.
**How to avoid:** Implement fault injection as a SEPARATE subcommand (`dev fault-inject`) rather than a flag on `dev consistency-check`. The clean-board read leg runs zero fault-injection code. The fault-injection subcommand has its own distinct connection lifecycle.

### Pitfall 6: Write-Leg Source Image Selection
**What goes wrong:** Writing a blank (all-`0xff`) image is a degenerate test — the chip may already be blank, making "erase success" non-verifiable. Writing all-`0x00` is also degenerate because a floating bus reads as `0xff`, masking corruption.
**How to avoid:** Use a non-trivial pattern: a previously-read image with known content (e.g., the GATE-1.8d W27C512 content), or a generated pattern such as `bytes(range(256)) * (chip_size // 256)`. The write-leg source image SHA must be pre-computed and recorded in the artifact.

### Pitfall 7: `dev consistency-check` Output Dir Naming Collision with GATE-1.8d Baseline
**What goes wrong:** The default output dir is `consistency-check-<chip>-unknown-board-<TS>/`. If run output is stored in `.planning/v1.6/consistency-check-runs/` it would be adjacent to the GATE-1.8d baselines, causing confusion.
**How to avoid:** Phase 53 stores ALL artifacts under `.planning/v1.10/bench-verification/`, never under `.planning/v1.6/`. Use `--output-dir .planning/v1.10/bench-verification/clean-board-<board>/read-leg/`.

---

## Code Examples

### Existing consistency_check_eprom() Read Loop (Reuse Seam for Write Leg)

```python
# Source: firestarter_app/firestarter/eprom_operations.py lines 573–631
# [VERIFIED: live code read 2026-06-02]

for i in range(1, runs + 1):
    run_path = output_path / f"run_{i:02d}.bin"
    with self._operation_context(eprom_name, eprom_data_dict,
                                 COMMAND_READ, operation_flags) as (cmd_data, _, op_name):
        if not cmd_data:
            return 2
        with open(run_path, "wb") as fh:
            def _writer(address, data_chunk, _fh=fh, _start=cmd_data.get("address",0)):
                _fh.seek(address - _start)
                _fh.write(data_chunk)
            is_ok, _ = self._run_state_machine(
                op_name,
                main_phase_handler=self._main_phase_read_data,
                start_addr=cmd_data.get("address", 0),
                end_addr=cmd_data.get("memory-size", 0),
                process_data_chunk_callback=_writer,
            )
    if not is_ok:
        return 2

    sha = hashlib.sha256(run_path.read_bytes()).hexdigest()
    results.append((i, sha, run_path.stat().st_size))
```

### Existing send_json_command() Frame Assembly (Fault-Injection Hook Point)

```python
# Source: firestarter_app/firestarter/serial_comm.py lines 156–175
# [VERIFIED: live code read 2026-06-02]

def send_json_command(self, command_dict: dict) -> int:
    json_bytes = json.dumps(command_dict, separators=(",", ":")).encode("ascii")
    crc = _crc8_ccitt(json_bytes)
    body = cobs_encode(json_bytes + bytes([crc]))
    frame = body + b"\x00"
    # >>> FAULT INJECTION HOOK: if self._fault_inject_outgoing: frame = self._fault_inject_outgoing(frame)
    return self.send_bytes(frame)
```

### COBS Encode/Decode (Canonical; Do Not Re-Implement)

```python
# Source: firestarter_app/firestarter/frame_parser.py lines 58–128
# [VERIFIED: live code read 2026-06-02]

def cobs_encode(payload: bytes) -> bytes:
    """Returns encoded body WITHOUT trailing 0x00 delimiter."""
    # ... (full implementation at frame_parser.py:58–100)

def cobs_decode(encoded: bytes) -> bytes:
    """Decodes COBS body (NO trailing 0x00). Raises ValueError on malformed input."""
    # ... (full implementation at frame_parser.py:103–128)
    # ValueError is the resync signal for the host decoder
```

### _decode_id_frame Override for fw→host Fault Injection

```python
# Pattern for FaultInjectingSerialCommunicator (test-only, dev subcommand scope only)
# [VERIFIED: _decode_id_frame wrapper at serial_comm.py:225-227 calls codec.decode_id_frame]

class FaultInjectingSerialCommunicator(SerialCommunicator):
    def __init__(self, *args, corrupt_incoming_once=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._corrupt_incoming_once = corrupt_incoming_once
        self._fault_fired = False

    def _decode_id_frame(self, frame_len: int, body: bytes):
        if self._corrupt_incoming_once and not self._fault_fired:
            self._fault_fired = True
            # Flip last byte (CRC8) in the raw body before decode
            body = body[:-1] + bytes([body[-1] ^ 0x01])
        return super()._decode_id_frame(frame_len, body)
```

---

## Runtime State Inventory

> Omitted — this is a greenfield instrumentation phase, not a rename/refactor/migration. No stored data, live service config, OS-registered state, or stale build artifacts are affected.

---

## Validation Architecture

This section is required for Nyquist; `workflow.nyquist_validation` is absent from config.json (treated as enabled).

### Hardware-Gated vs Software-Verifiable Split

Phase 53 has two distinct verification classes. The planner MUST encode both.

| Success Criterion | Verification Class | Automated? | How Verified |
|---|---|---|---|
| `dev write-cycle` subcommand exists and produces correct per-cycle SHA-256 comparison | Software-verifiable | Yes | Unit test: mock `erase_eprom`/`write_eprom` returns True, mock read-back returns known bytes, assert return value 0/1/2 |
| Fault-injection hook in `send_json_command()` is callable and does not affect production path when None | Software-verifiable | Yes | Unit test: hook=None → frame unmodified; hook=corrupt_crc8 → frame[-2] flipped |
| Fault-injection hook does NOT modify `_read_and_parse_lines()` body | Software-verifiable (code review) | Yes (automated lint) | `git diff HEAD -- serial_comm.py` shows zero changes in body of `_read_and_parse_lines` |
| XACT-01 read leg: N=5 byte-identical on Uno | Hardware-gated | No | Operator runs `dev consistency-check W27C512 --runs 5 --output-dir ...`; records SHAs |
| XACT-01 read leg: N=5 byte-identical on Leonardo | Hardware-gated | No | Same command on Leonardo; compare vs GATE-1.8d baselines if original chip present |
| XACT-01 write leg: N=5 write→read-back cycles, all SHA = source | Hardware-gated | No | Operator runs `dev write-cycle W27C512 --runs 5 --source <image>` |
| XACT-02 host→fw: corrupted frame returns sub-second error + next frame byte-exact | Hardware-gated | No | Operator runs `dev fault-inject W27C512 --direction outgoing`; observes error timing and recovery |
| XACT-02 fw→host: mutated incoming frame returns error + next frame byte-exact | Hardware-gated | No | Operator runs `dev fault-inject W27C512 --direction incoming` |
| XACT-03 uno328pb: runs attempted with timeout-retry logging + exoneration verdict | Hardware-gated | No | Operator runs `dev consistency-check W27C512 --runs 5` on uno328pb; logs captured |
| Artifact under `.planning/v1.10/bench-verification/` contains all required files | Software-verifiable (post-bench) | Semi | `ls .planning/v1.10/bench-verification/` + `wc -c *.bin` checks; automatable as a verify script |

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (project version, installed via `pip install -e '.[test]'`) |
| Config file | `pyproject.toml` (project root of `firestarter_app/`) |
| Quick run command | `pytest tests/ -x -q --no-header 2>/dev/null` |
| Full suite command | `pytest tests/ --cov=firestarter --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| XACT-01 (software part) | `write_cycle_eprom()` returns 0 when all cycles match | unit | `pytest tests/test_eprom_operations.py -k test_write_cycle -x` | Wave 0 — new file |
| XACT-02 (software part) | `send_json_command()` hook fires when set, does nothing when None | unit | `pytest tests/test_serial_comm.py -k test_fault_inject -x` | Wave 0 — new tests |
| XACT-02 (software part) | `FaultInjectingSerialCommunicator._decode_id_frame` flips CRC8 byte once | unit | `pytest tests/test_serial_comm.py -k test_fault_inject_incoming -x` | Wave 0 — new tests |
| XACT-01 (hardware part) | N=5 byte-identical reads on Uno + Leonardo | operator-witnessed | (no automated command — bench only) | N/A |
| XACT-01 write leg (hardware) | N=5 write→read-back cycles match source | operator-witnessed | (no automated command — bench only) | N/A |
| XACT-02 (hardware part) | Sub-second error + recovery on both directions | operator-witnessed | (no automated command — bench only) | N/A |
| XACT-03 (hardware part) | uno328pb runs captured + exoneration verdict written | operator-witnessed | (no automated command — bench only) | N/A |

### Sampling Rate

- **Per task commit:** `pytest tests/ -x -q --no-header 2>/dev/null`
- **Per wave merge:** `pytest tests/ --cov=firestarter --cov-fail-under=70`
- **Phase gate:** Full suite green + `.planning/v1.10/bench-verification/SUMMARY.md` exists before `/gsd-verify-work`

### Wave 0 Gaps

- `tests/test_eprom_operations.py` — add `test_write_cycle_eprom_pass`, `test_write_cycle_eprom_mismatch`, `test_write_cycle_eprom_hw_error` (covers XACT-01 software part)
- `tests/test_serial_comm.py` — add `test_fault_inject_outgoing_none`, `test_fault_inject_outgoing_corrupt_crc8`, `test_fault_inject_outgoing_drop_delimiter`, `test_fault_inject_incoming_subclass` (covers XACT-02 software part)
- `tests/test_cli_handlers.py` — add invocation smoke tests for `dev write-cycle` and `dev fault-inject` (if subcommand approach chosen)

---

## Project Constraints (from CLAUDE.md)

The following directives from `./CLAUDE.md` and `firestarter_app/CLAUDE.md` apply to Phase 53:

| Directive | Impact on Phase 53 |
|-----------|-------------------|
| `serial_comm.py` ↔ `rurp_serial_utils.cpp` lockstep mandate | Phase 53 adds NO firmware changes; host-only changes do not trigger this. Verify no firmware edits occur. |
| Constants duplicated between `constants.py` (Python) and `firestarter.h` (C++) | No new constants in Phase 53. Verify any fault-injection flag values are dev-only and not added to shared constants. |
| Uno buffer = 512 B, Leonardo buffer = 1024 B | Write-leg source image must fit in the chip size (W27C512 = 65536 B), chunked per `_calculate_buffer_size()`. No change to chunking logic needed. |
| `ruff check` + `ruff format --check` + `mypy` strict (8 modules including `serial_comm.py`, `cli_handlers.py`) | New subcommands in `cli_handlers.py` and any new methods in `eprom_operations.py` must pass ruff + mypy strict. `FaultInjectingSerialCommunicator` if in `serial_comm.py` must have full type annotations. |
| `pytest --cov-fail-under=70` | New code must have test coverage; see Wave 0 gaps above. Coverage floor is currently 71.28% (Phase 52 close). |
| `_read_and_parse_lines` GATE-1.8d ring-fence | Body of `_read_and_parse_lines()` in `serial_comm.py` MUST NOT change. Fault-injection for fw→host uses subclass or callback wrapper only. |
| Phase 52 byte-identity contract pinned by golden vectors | `cobs_encode`, `cobs_decode`, `_crc8_ccitt` implementations are frozen. Fault injection only calls them — never modifies them. |
| Chip OUT before any firmware sideload | Mandatory precondition in every bench task that sideloads firmware. |
| Verify `controller:` per port at every bench task | Mandatory first step in every bench task. |
| ASK operator which silkscreen shield rev before bench work | D-07 requires Rev 2.0 for clean-board proof; MUST be operator-declared, not assumed from EEPROM. |

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact on Phase 53 |
|--------------|------------------|--------------|---------------------|
| `[len_u16][xor][payload]` data-block framing | `[COBS(payload+CRC8)][0x00]` framing | Phase 50 | Fault injection targets CRC8 byte and 0x00 delimiter (not len_u16) |
| JSON command without integrity check | COBS+CRC8 framed command; CRC8 verified before JSON parse | Phase 51 | host→fw fault injection corrupts the CRC8 to test firmware's decode-and-verify path |
| Round-trip tests in Phase 52 | Phase 52 golden vectors pinned; test suite green 422/422 host, 39/39 firmware | Phase 52 | The contract Phase 53 proves on hardware is already pinned in software |
| `send_ack()` / `send_done()` plaintext | These remain plaintext — NOT framed (Phase 51 scope clarification) | Phase 51 | Fault-injection subcommand targets JSON command frames, not ACK/DONE strings |

**Deprecated/outdated:**
- `len_u16` length prefix: removed by Phase 50. XACT-02's "or length field" wording in REQUIREMENTS.md is therefore moot — the only corruptible structural elements are CRC8 and the `0x00` delimiter (per locked context D-02).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `frame[-2]` is always the encoded CRC8 byte in the host→fw COBS frame | Code Examples — fault injection | If the CRC8 byte is encoded differently in a 254-run, `frame[-2]` might not be the CRC8; fix: use `cobs_decode(frame[:-1])[-1]` to confirm position | [ASSUMED: based on COBS encoding algorithm analysis — the CRC8 is the last byte of the payload and is always in the final COBS run] |
| A2 | `erase_eprom` is a prerequisite for `write_eprom` on W27C512 | Write-leg discussion | W27C512 is an EEPROM that may be electrically erasable without separate command; if firmware handles this internally, an explicit erase call may be optional | [ASSUMED: standard EEPROM write procedure; verify by checking `COMMAND_ERASE` path in firmware for W27C512 algorithm] |
| A3 | The `dev write-cycle` run time (erase+write+read-back N=5 on W27C512 64 KB) is within operator patience | Bench protocol | If erase is slow (~seconds per cycle × 5 cycles), operator may interrupt; document expected duration | [ASSUMED: typical EEPROM erase is < 20 ms per byte for W27C512; 5 cycles should be < 10 minutes total] |

---

## Open Questions (RESOLVED)

> All three are handled by plan structure rather than left open — Q1 and Q2 are operator/hardware contingencies the plans encode both paths for; Q3 is a design choice the planner made. None block execution.

1. **W27C512 chip availability for D-05 strong-form hash match**
   - What we know: GATE-1.8d baselines exist at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-155617-v2-rev20/`; Rev 2.0 canonical SHA `19710f6e…`
   - What's unclear: Whether the exact same physical chip that produced those baselines is still on the bench (chip may have been partially-written or worn since 2026-05-26)
   - Recommendation: Planner should include a task to verify chip ID matches `0xda08` before attempting hash match; record in artifact which form (strong or self-consistency-only) was achieved
   - **RESOLVED:** Plan 53-03 Task 2 encodes both paths per D-05 — strong-form GATE-1.8d hash-match if the original chip is present, self-consistency-only otherwise, with the achieved form recorded in the artifact. No pre-bench answer required; contingency is in the plan.

2. **uno328pb sideload port at Phase 53 bench time**
   - What we know: Historically `/dev/ttyUSB0`, urclock programmer_id, ATmega328PB Case A confirmed
   - What's unclear: USB device assignment at time of execution (ACM numbers shuffle)
   - Recommendation: Every bench task must include port-identity verification step before any operation
   - **RESOLVED:** Every bench task (53-03/04/05 Task 1) mandates per-port `controller:` identity verification at task start before any operation. Port shuffle is handled operationally, not as a planning unknown.

3. **Fault-injection subcommand vs flag implementation choice (planner's discretion)**
   - What we know: Context D says "planner's discretion" on exact mechanism
   - What's unclear: Whether adding a `dev fault-inject` subcommand vs `--fault-inject` flag on `dev consistency-check` is cleaner in context of mypy strict and test coverage requirements
   - Recommendation: Separate subcommand is cleaner (avoids complicating the ring-fenced read path's test surface)
   - **RESOLVED:** Planner chose the separate `dev fault-inject` subcommand (Plan 53-02 Task 3), keeping the ring-fenced read path's test surface untouched.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 (devcontainer) | All host CLI tasks | Yes | 3.12.x | — |
| `pytest` | Unit tests | Yes (via `pip install -e '.[test]'`) | Project version | `pip install -e '.[test]'` |
| `ruff` | CI gate | Yes (devcontainer) | Project version | — |
| `mypy` | CI gate | Yes (devcontainer) | Project version | — |
| Arduino Uno on `/dev/ttyACM*` | XACT-01/02 clean-board | Operator-dependent | — | Operator connects before bench task |
| Arduino Leonardo on `/dev/ttyACM*` | XACT-01/02 clean-board | Operator-dependent | — | Operator connects before bench task |
| uno328pb on `/dev/ttyUSB0` | XACT-03 | Operator-dependent | — | Task deferred until operator connects |
| Rev 2.0 RURP shield | D-07 clean-board target | Operator-dependent (must ask) | — | Operator declares silkscreen rev at session start |
| W27C512 EPROM chip | All bench tasks | Operator-dependent | — | Operator supplies chip; ID verified via `firestarter id W27C512` |
| v1.10 hardened firmware on boards | All bench tasks | Operator must sideload | Current branch tip | `pio run -e <env> -t upload` (chip OUT first) |

**Missing dependencies with no fallback:**
- None blocking software development tasks.
- Bench hardware (boards, shield, chip) blocks XACT-01/02/03 hardware tasks — these are explicitly operator-gated.

**Missing dependencies with fallback:**
- None additional.

---

## Sources

### Primary (HIGH confidence)
- `firestarter_app/firestarter/cli_handlers.py` lines 1030–1117 — `dev consistency-check` exact signature, flags, 3-way verdict contract [VERIFIED: live code read 2026-06-02]
- `firestarter_app/firestarter/eprom_operations.py` lines 497–696 — `consistency_check_eprom()` implementation, lines 838–933 — `write_eprom()` and `erase_eprom()` entry points [VERIFIED: live code read 2026-06-02]
- `firestarter_app/firestarter/frame_parser.py` lines 28–128 — `_crc8_ccitt()`, `cobs_encode()`, `cobs_decode()` canonical implementations [VERIFIED: live code read 2026-06-02]
- `firestarter_app/firestarter/serial_comm.py` lines 135–175 — `send_bytes()`, `send_json_command()` implementations; lines 229–363 — `_read_and_parse_lines()` ring-fence + receive path [VERIFIED: live code read 2026-06-02]
- `.planning/v1.6-EVIDENCE.md` — uno328pb pre-hardening failure shape (Plan 27-04 section): 99.4% 0xff, 100% unstable positions, 4× N=5 timeouts, 0.47% pairwise divergence [VERIFIED: live doc read 2026-06-02]
- `.planning/v1.6/consistency-check-runs/` — GATE-1.8d baseline directory listing confirmed; 15 files across 3 v2* dirs; Rev 2.0 canonical SHA `19710f6e…` verified [VERIFIED: directory listing + sha256sum 2026-06-02]
- `.planning/phases/53-byte-exact-bench-verification-hardware-gated/53-CONTEXT.md` — all D-01 through D-11 decisions [VERIFIED: live doc read 2026-06-02]
- `.planning/REQUIREMENTS.md` — XACT-01/02/03 text [VERIFIED: live doc read 2026-06-02]
- `.planning/v1.10-FRAMING-DECISION.md` §4 — frozen frame contract [VERIFIED: live doc read 2026-06-02]
- `.planning/v1.9-COBS-DECISION.md` §2.0 — transport-exoneration scope [VERIFIED: live doc read 2026-06-02]

### Secondary (MEDIUM confidence)
- None needed — all claims verified from live codebase.

### Tertiary (LOW confidence / assumed)
- A1–A3 in Assumptions Log above.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; all tools verified in live codebase
- Code substrate / entry points: HIGH — exact line numbers and signatures confirmed from live code
- Architecture patterns: HIGH — write-leg pattern is direct generalization of verified `consistency_check_eprom()` loop
- Fault-injection seams: HIGH — confirmed injection points; ring-fence constraint confirmed from live code
- uno328pb before-shape: HIGH — exact metrics cited from `.planning/v1.6-EVIDENCE.md` Plan 27-04
- GATE-1.8d baselines: HIGH — directory listing + SHA-256 prefix confirmed live
- Bench protocol: HIGH — all memory notes verified from context

**Research date:** 2026-06-02
**Valid until:** 2026-07-02 (stable codebase; Phase 52 frozen; no external dependencies)
