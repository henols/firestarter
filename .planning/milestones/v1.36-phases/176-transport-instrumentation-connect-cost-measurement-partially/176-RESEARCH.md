# Phase 176: Transport Instrumentation + Connect-Cost Measurement — Research

**Researched:** 2026-09-04
**Domain:** Python host transport instrumentation (`firestarter_app/firestarter/serial_comm.py`, `diagnostic_report.py`) + one bench-measured per-board-class artifact
**Confidence:** HIGH for everything code-reachable; LOW for the bench half (no board is attached to this container right now)

---

## Summary

This is a small, sharply-bounded host-only phase with one loud structural obstacle and one honesty
trap. Every fact below was read out of the working tree at `firestarter_app @ a9c0bde` (branch
`gsd/v1.36-dev-test-fidelity`) this session, with line ranges and verbatim quotes.

**The good news.** REQUIREMENTS.md's line citations are *correct at HEAD* — the two re-sync sites
really are at `serial_comm.py:485-490` and `:500-505`. (ROADMAP.md's backlog-999.36 copy at
`:520-526` / `:536-541` is the stale one; do not use it.) `dedup_fingerprint` provably does not read
`transport_health`, so nothing this phase does can re-key a single filed report, and the Phase 174
re-key ledger carries **no** Phase 176 row — correctly, because none is needed.

**The obstacle.** Both re-sync sites sit *inside* `_read_and_parse_lines`, which is ring-fenced by a
`DO NOT MODIFY — v1.9 RCA territory` header **and** by a live SHA-256 source pin
(`tests/test_serial_comm.py:430-460`). Any character added to that function turns that test RED. The
other two sites (`_decode_id_frame` returning `None`, and `get_response`'s timeout) are *outside* the
fence and are free. A plan must decide, explicitly, how it gets past the fence — §7 gives three
options and a recommendation.

**The honesty trap, and it is the real content of MEAS-03.** Three of the four existing counter
slots are misleading targets. `cobs_errors` is genuinely unreachable — `cobs_decode` exists but is
called from tests only, never from production. `retries` has no host-side transport retry loop at
all; the only "retries" in the system is `MSG_INFO_RETRIES` (0x51), a **firmware write-pulse** count,
and wiring it into `TransportHealth.retries` would blame the *link* for a marginal *chip* and trip
`_is_transport_suspect` at 5. And `get_response`'s timeout fires **once per failed port probe** on
every ordinary connect, so a naive process-global `timeouts` counter would report link sickness on a
perfectly healthy rig with three boards attached. These three findings are what MEAS-02's threshold
re-derivation has to be argued against.

**Primary recommendation:** Put the counters in a new module-level, process-lifetime, explicitly
resettable sink (`firestarter/transport_counters.py`) with **four new, precisely-named** keys —
never by overloading `retries`/`cobs_errors`. Wire the two free sites directly, get past the ring
fence by deliberately re-pinning the SHA with the reasoning recorded in the test docstring (the
Phase 65-01 precedent, already in that docstring), snapshot the connect-cost measurement as
`176-MEASUREMENT.md` per the Phase 118 shape, and regenerate all 16 committed report snapshots in
the same commit as the `_TRANSPORT_HEALTH_KEYS` pin update.

---

## User Constraints

**There is no `176-CONTEXT.md`.** The user chose to plan without one, so there are **no
phase-level locked decisions**. Everything below marked "Claude's Discretion" is genuinely open and
should be surfaced at plan-check.

### Locked Decisions (milestone-level — from `.planning/REQUIREMENTS.md`, binding on this phase)

These are not this phase's own decisions, but they constrain it and no phase may re-litigate them
[VERIFIED: `.planning/REQUIREMENTS.md:107-113` read this session]:

- **HYG-02** — *"No new runtime dependency is added. The shipped set stays `pyserial, requests,
  tqdm, click, rich, packaging`."* This phase installs nothing.
- **HYG-03** — *"A decision is recorded that `dedup_fingerprint` must **not** be refactored to hash
  `to_dict()`."* Directly relevant: adding a `transport_health` key is safe *only because* the hash
  does not read `to_dict()`.
- **HYG-04** — *"Any new `dev_test` helper is registered in
  `tools/check_devtest_orchestrator.py:152-164`, which silently does not scan what is not listed."*
- **RPT-C2** (verbatim) — *"`_is_transport_suspect`'s present-AND-elevated rule is unchanged —
  absent data still cannot fabricate suspicion."*
- **Out of Scope** — *"64 KiB `Empty input` investigation — Backlog 999.37 | Depends on RPT-C1's
  counters existing first."* This phase builds the instrument; it does not run the investigation.
- **Success criteria are stated in operation counts, never in seconds** (§"No-Information
  Operations" preamble). MEAS-01 is the *one* declared exception — it exists precisely to produce
  the seconds figure the rest of the milestone is forbidden from assuming.

### Claude's Discretion (open — no CONTEXT.md fixed these)

1. Counter storage mechanism and lifetime (module sink vs class attribute vs handler) — §2.
2. How to get past the `_read_and_parse_lines` ring fence — §7.
3. New key names, and whether to reuse or retire the existing `retries`/`cobs_errors` slots — §4.
4. Whether `_SUSPECT_THRESHOLD` moves, and to what — §3, §9.
5. The bench artifact's file name and location (a precedent shape is named in §6).

### Deferred Ideas (OUT OF SCOPE)

- **R4-01** — `EpromOperator` leasing one validated link per plan. MEAS-01 *gates whether it is
  worth scoping*; it does not authorise scoping it here.
- **PRUNE-08** — Phase 180 consumes MEAS-01's number. Not this phase.
- **999.37** — the 64 KiB `Empty input` investigation.

---

## Project Constraints (from CLAUDE.md)

| Directive | Source | Consequence for this phase |
|---|---|---|
| **NO comments in source, at all** | Operator hard rule (broadened 2026-08-29); `174-PATTERNS.md` §"No comments, docstrings only" | Every line this phase adds to `serial_comm.py` / `diagnostic_report.py` / new modules carries **zero** `#` comments. Docstrings only. A plan cannot override this. |
| Serial protocol changes must stay in sync between `serial_comm.py` and `firestarter/src/firestarter.cpp` | `/workspaces/CLAUDE.md` §Key Architecture Points | **Not triggered** — this phase adds no wire field and sends no new command. Host-only per REQUIREMENTS.md §Scope. |
| Constants/flag bits duplicated between `constants.py` and `firestarter.h` | `/workspaces/CLAUDE.md` | Not triggered — the counters are host-local, not protocol constants. |
| Tooling gate: `ruff check` + `ruff format --check` + mypy watermark + `pytest --cov-fail-under=70` | `firestarter_app/CLAUDE.md` §Tooling gate; `.github/workflows/ci.yml` | All four run on every push to every branch. |
| `firestarter.serial_comm` is mypy **strict** (`disallow_untyped_defs = true`) | `firestarter_app/pyproject.toml:196-208` | Any new function/method added to `serial_comm.py` needs full type annotations. `diagnostic_report.py` is in **neither** list (default settings). `eprom_operations.py` is deliberately excluded per GATE-1.8d. |
| `main` is protected in all three repos; this project's base branch is `beta` | `/workspaces/CLAUDE.md` §Milestone close | Work lands on `gsd/v1.36-dev-test-fidelity` in **both** meta and `firestarter_app`; both are already on that branch. |

Verbatim, from `pyproject.toml:196-208` [VERIFIED: `firestarter_app/pyproject.toml:196-208`]:

```toml
module = [
    "firestarter.main",
    "firestarter.cli_handlers",
    "firestarter.chip_resolver",
    "firestarter.frame_parser",
    "firestarter.codec",
    "firestarter.address_parser",
    "firestarter.exceptions",
    "firestarter.serial_comm",
    "firestarter.sdp_honesty",
]
disallow_untyped_defs = true
check_untyped_defs = true
```

---

## Phase Requirements

| ID | Description (verbatim from REQUIREMENTS.md) | Research Support |
|----|---------------------------------------------|------------------|
| **RPT-C1** | "The two re-sync events at `serial_comm.py:485-490` and `:500-505`, `_decode_id_frame` returning `None`, and `get_response`'s timeout each increment a real counter reachable by the report." | §1 (all four sites quoted at HEAD, line numbers confirmed), §2 (lifetime), §7 (ring fence) |
| **RPT-C2** | "`transport_health` reports those real counts. `NOT_MEASURED` remains **only** for a counter genuinely not wired, and `_is_transport_suspect`'s present-AND-elevated rule is unchanged — absent data still cannot fabricate suspicion." | §3 (`_transport_dict`, `_is_transport_suspect` quoted; "unchanged" defined concretely), §8 (the 174 pin that must move in the same commit) |
| **MEAS-01** | "Per-connect cost is measured **per board class** (Uno 512 B, Leonardo 1024 B), not as one number. On Uno-class boards the DTR auto-reset and bootloader wait are likely the dominant term." | §6 (what a connect is, the 2.5 s structural floor, artifact precedent, the environment gap) |
| **MEAS-02** | "`_SUSPECT_THRESHOLD = 5` is either justified against real counts or re-derived once RPT-C1's counters exist — it was chosen while the counters were dormant and has never been exercised." | §9 (the probe-timeout inflation argument — the strongest available basis) |
| **MEAS-03** | "Which of `retries` / `timeouts` are genuinely wireable is traced end to end. Anything not actually wired keeps `NOT_MEASURED`." | §4 (both traced end to end; `retries` dead-ends, `timeouts` is live-but-noisy; `cobs_errors` traced too and found dead) |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Detecting a re-sync / decode failure / timeout | **Transport** (`serial_comm.py`) | — | These are byte-stream events. Only the reader sees them. |
| Holding the counts across a torn-down connection | **Process-lifetime sink** (new module) | — | `EpromOperator.comm` is `None` after every call (§2), so per-instance state cannot survive to the report. |
| Deciding what a count *means* | **Report** (`diagnostic_report.py`) | — | `_is_transport_suspect` already owns this and RPT-C2 forbids changing its rule. |
| Reading the counts into a report | **Orchestrator** (`cli_handlers.py:2387`) | — | The `DiagnosticReport` construction site. `diagnostic_report.py` is contractually forbidden from importing any transport class (module docstring: *"ORCHESTRATOR ONLY: this module imports no transport or hardware class"*). |
| Measuring per-connect wall-clock | **Bench harness** (dev-only, `eprom_operations.py` precedent) + **`.planning/` artifact** | — | `measure_command_nak_latency` (§6) is the established shape. |

**The one tier rule a plan must not break:** `diagnostic_report.py` must not import `serial_comm`.
Its own docstring makes this a contract, and `tests/test_diagnostic_report.py` carries an
orchestrator-only structural scan (SAFE-02) around line 565. The counts must be *threaded in* at
`cli_handlers.py`, exactly as `fw_board_identity` and `hw_revision` already are.

---

## 1. The Four Instrumentation Sites — exact current code

All four verified against the working tree this session. **REQUIREMENTS.md's line numbers are
correct at HEAD; ROADMAP.md's are stale.**

### Site A — re-sync #1: length bytes not received

[VERIFIED: `firestarter_app/firestarter/serial_comm.py:485-490`] — verbatim:

```python
                if len(len_bytes) < 2:
                    logger.warning(
                        "Magic preamble seen but length bytes not received "
                        "before timeout — re-syncing."
                    )
                    continue
```

**What must change:** one increment between the `logger.warning(...)` call and the `continue`.
**Blocker:** inside the ring fence (§7).

### Site B — re-sync #2: frame body truncated

[VERIFIED: `firestarter_app/firestarter/serial_comm.py:500-505`] — verbatim:

```python
                if len(body) != frame_len:
                    logger.warning(
                        f"Frame body truncated: expected {frame_len} bytes, "
                        f"got {len(body)} — re-syncing."
                    )
                    continue
```

**What must change:** one increment before the `continue`. **Blocker:** inside the ring fence.

### Site C — `_decode_id_frame` returns `None`

The **host wrapper** `SerialCommunicator._decode_id_frame` is at `serial_comm.py:327`, is **outside**
the ring fence (its own docstring says so), and ends
[VERIFIED: `firestarter_app/firestarter/serial_comm.py:346-349, 405`] — verbatim:

```python
        The ring-fenced _read_and_parse_lines body is not touched; only this
        override seam is used.
        """
        result = codec.decode_id_frame(frame_len, body)
```
...
```python
        return result
```

**What must change:** immediately after `result = codec.decode_id_frame(...)`, an
`if result is None: <increment>`. **No blocker — this is the cheapest of the four.** The consumer
at `:518-519` is `decoded = self._decode_id_frame(frame_len, body)` / `if decoded is not None:`,
so a `None` today is silently dropped with no counter and no yield.

`codec.decode_id_frame` returns `None` on **five distinct causes**
[VERIFIED: `firestarter_app/firestarter/codec.py:183-185`] — verbatim from its docstring:

> `Returns a LogMessage on success. Returns None (with a `logger.warning`) on shape mismatch / CRC fail / unknown ID / format-render error — the outer read loop continues to the next byte (DoS resilience per T-06-12).`

The five arms, each `return None`, are at `codec.py:187-192` (short/truncated), `:199-204`
(CRC mismatch), `:206-209` (unknown ID), `:217-223` (`wire_format != "id_frame"` rejection), and a
fifth at the `_decode_param` overrun arm below `:229`. **This matters for naming:** a single counter
here is *not* a CRC-failure counter. Calling it `crc_failures` would be a fabrication, exactly the
class of dishonesty RPT-C2 exists to prevent.

### Site D — `get_response` timeout

[VERIFIED: `firestarter_app/firestarter/serial_comm.py:546-559`] — verbatim:

```python
    def get_response(self, timeout: float = DEFAULT_RESPONSE_TIMEOUT) -> Response:
        """
        Waits for and returns the next significant (i.e., not INFO or DEBUG)
        response from the programmer.
        """
        for response in self._read_and_parse_lines(timeout):
            if response.type and response.type not in NON_RESPONSE_PREFIXES:
                return response

        # If the generator finishes without yielding a significant response, it's a timeout.  # noqa: E501
        logger.warning(f"Timeout waiting for a response from {self.port_name}.")
        raise SerialTimeoutError(
            f"Timeout waiting for a significant response from {self.port_name}."
        )
```

**What must change:** one increment beside the `logger.warning`, before the `raise`.
**No blocker** — `get_response` is outside the ring fence. **But see §9: this site is noisy.**

`DEFAULT_RESPONSE_TIMEOUT = 10` and `DEFAULT_SERIAL_TIMEOUT = 1.0`
[VERIFIED: `firestarter_app/firestarter/serial_comm.py:65-66`] — verbatim:

```python
DEFAULT_SERIAL_TIMEOUT = 1.0  # seconds for read operations
DEFAULT_RESPONSE_TIMEOUT = 10  # seconds for waiting for a specific response
```

---

## 2. Where counters live now, and what their lifetime must be

**There is no counter surface today.** Grepping the whole package for `cobs_errors|crc_failures|
retries|timeouts|TransportHealth` returns hits in exactly two production files:
`diagnostic_report.py` (the dataclass, the `NOT_MEASURED` substitution, `_is_transport_suspect`) and
`cli_handlers.py` (the import and the one construction site). `serial_comm.py` has **zero** hits.

`SerialCommunicator` does carry per-instance state that a naive design would imitate
[VERIFIED: `firestarter_app/firestarter/serial_comm.py:179-185`] — verbatim:

```python
        # Bounded record of every id frame
        # successfully decoded on this connection. Populated by the
        # _decode_id_frame override below. A set of integers only — nothing
        # sized from frame content is ever allocated here, mirroring
        # the defensive posture of the firmware_max_chunk plausibility clamp
        # above. Per-connection instance state, not shared across connections.
        self.seen_message_ids: set[int] = set()
```

**"Per-connection instance state, not shared across connections" is exactly why this pattern cannot
be copied here.**

### `EpromOperator.comm` really is `None` after every call — confirmed

[VERIFIED: `firestarter_app/firestarter/eprom_operations.py:540-547`] — verbatim:

```python
        finally:
            # This block ensures disconnection happens even if errors occur
            self._disconnect_programmer()

    def _disconnect_programmer(self):
        if self.comm:
            self.comm.disconnect()
            self.comm = None
```

And the orchestrator states the consequence itself
[VERIFIED: `firestarter_app/firestarter/cli_handlers.py:2369-2378`] — verbatim:

```python
    # EpromOperator.comm is a transient per-operation connection torn down
    # after every operator call (see 112-02-SUMMARY.md) -- there is no live
    # comm to read programmer_info off of after run_plan returns without
    # opening a new, extraneous connection, which would violate the
    # orchestrator-only contract.
```

The construction order at the sole production site seals it
[VERIFIED: `firestarter_app/firestarter/cli_handlers.py:2387-2392, 2404-2412`] — verbatim:

```python
    transport = TransportHealth()
    report = DiagnosticReport(
        auto_capture=auto_capture,
        transport=transport,
        plan=plan,
    )
```
...
```python
    results = run_plan(
        plan,
        app.eprom_operator,
        app.db,
        runs=1 if fast else 2,
        allow_single_run=fast,
        sampler=sampler,
    )
    report.results = results
```

`TransportHealth()` is built with all-`None` defaults **before** `run_plan`, and nothing ever
assigns to it afterwards. So two things are true and a plan needs both:

1. **The counter must outlive every `SerialCommunicator` instance** — a `dev test` run creates and
   destroys on the order of a dozen to thirty of them (§6).
2. **The report must be *updated* after `run_plan` returns**, not just constructed before it —
   either by mutating `report.transport` in place or by re-assigning it. `TransportHealth` is a
   plain `@dataclass` with no `frozen=True`, so in-place field assignment is legal
   [VERIFIED: `firestarter_app/firestarter/diagnostic_report.py:101-117`].

### Required lifetime

**Process-lifetime, explicitly resettable, reset at the start of the measured window.** Not
per-instance (destroyed too early), not per-`EpromOperator` (three of the connects in a `dev test`
run come from `hardware_manager`, not the operator — §6). The reset point matters: a `reset()` at
the top of `dev_test` before `read_programmer_identity()` gives "counts for this whole command";
a reset immediately before `run_plan` gives "counts for the plan only" and excludes the identity
read's own connect. **Either is defensible; the plan must pick one and say which, because the
number means something different in each case.**

---

## 3. `transport_health` and `_is_transport_suspect` — current shape

### The dataclass

[VERIFIED: `firestarter_app/firestarter/diagnostic_report.py:101-117`] — verbatim:

```python
@dataclass
class TransportHealth:
    """Best-effort transport-health counters.

    Every counter defaults to `None` -- "not measured" -- because no
    COBS-decode-error / CRC-failure / retry / timeout counter is reachable
    from the operator or serial-transport layer today (RESEARCH §Transport
    Counter Survey: verified NONE exist). `transport_suspect` defaults
    `False` and can only be set `True` by `_is_transport_suspect` below --
    never inferred from absent data.
    """

    cobs_errors: int | None = None
    crc_failures: int | None = None
    retries: int | None = None
    timeouts: int | None = None
    transport_suspect: bool = False
```

### How `NOT_MEASURED` is produced — one place, and only one

[VERIFIED: `firestarter_app/firestarter/diagnostic_report.py:605-617`] — verbatim:

```python
    def _transport_dict(self) -> dict[str, Any]:
        """Substitute NOT_MEASURED for any None counter -- the ONE place in
        this module that knows the sentinel string (Pitfall 3)."""
        th = self.transport
        return {
            "cobs_errors": NOT_MEASURED if th.cobs_errors is None else th.cobs_errors,
            "crc_failures": (
                NOT_MEASURED if th.crc_failures is None else th.crc_failures
            ),
            "retries": NOT_MEASURED if th.retries is None else th.retries,
            "timeouts": NOT_MEASURED if th.timeouts is None else th.timeouts,
            "transport_suspect": _is_transport_suspect(th),
        }
```

With [VERIFIED: `firestarter_app/firestarter/diagnostic_report.py:48-57`] — verbatim:

```python
SCHEMA_VERSION = "1.7"  # baked into to_dict() output
NOT_MEASURED = "not measured"  # honest fallback, never a false 0
# Distinct from NOT_MEASURED: this field was never ASKED, rather than asked and
# empty. Reusing NOT_MEASURED would conflate the two.
NOT_REPORTED = "not reported"

# Elevated-counter threshold for `transport_suspect` (dormant today -- no
# transport counter is reachable per RESEARCH §Transport Counter Survey; a
# future phase that adds real counters activates this without a redesign).
_SUSPECT_THRESHOLD = 5
```

Note `SCHEMA_VERSION = "1.7"`. **RPT-E1 bumps it to `2.0` in Phase 181, not here.** A key added by
this phase to `transport_health` therefore ships under `1.7` unless the plan argues otherwise —
`test_schema_version_is_pinned` (`tests/test_blast_radius_invariance.py:470`) will hold it there.

### The present-AND-elevated rule

[VERIFIED: `firestarter_app/firestarter/diagnostic_report.py:120-132`] — verbatim:

```python
def _is_transport_suspect(th: TransportHealth) -> bool:
    """True only when a counter is PRESENT (not None) AND elevated.

    Absent counters can never fabricate suspicion -- mirrors the
    honest `indeterminate` fingerprint bucket. Since no counter is reachable
    today (RESEARCH §Transport Counter Survey), this always returns False in
    production; it exists so a future counter source activates it without a
    redesign.
    """
    for value in (th.cobs_errors, th.crc_failures, th.retries, th.timeouts):
        if value is not None and value >= _SUSPECT_THRESHOLD:
            return True
    return False
```

### What "unchanged" means concretely, so a plan can assert it

RPT-C2 says the rule is unchanged. That is four assertable propositions, and a plan should write
them as four tests:

1. **`None` never contributes.** For every counter field, a `TransportHealth` with that field `None`
   and all others `None` returns `False` — *including at values that would trip if present*. The
   guard clause `value is not None and value >= _SUSPECT_THRESHOLD` must keep both conjuncts in
   that order.
2. **`0` is present, not absent.** `TransportHealth(timeouts=0)` returns `False` — but for the
   *elevation* reason, not the *presence* reason. This is the distinction a wired counter makes
   newly observable and it has never been tested.
3. **The comparison stays `>=`, not `>`.** A counter at exactly `_SUSPECT_THRESHOLD` must return
   `True`. Assert the boundary at 4 / 5 / 6.
4. **Any one counter suffices.** It is an `or` across fields (a `for` with an early `return True`),
   not an `and` and not a sum.

**Scope note for the planner:** if this phase adds a *new* field to `TransportHealth`, the tuple at
`:129` must be extended too — otherwise the new counter is reported in the JSON but can never raise
suspicion. Extending that tuple is *not* a change to the rule (the rule is "present AND elevated");
it is a change to the rule's *domain*. Say so explicitly in the plan, or a reviewer will read it as
an RPT-C2 violation.

---

## 4. MEAS-03 — end-to-end reachability trace

This is the requirement's actual deliverable. All four existing slots traced, not just the two named.

### `timeouts` — **WIREABLE**, but noisy. Verdict: wire it, and scope it.

End-to-end path:

```
_read_and_parse_lines(timeout)          serial_comm.py:418
  └─ while time.time() - start_time < timeout   :446
       (loop exits, generator returns)
get_response(timeout)                   serial_comm.py:546
  └─ for response in self._read_and_parse_lines(timeout):   :551
  └─ (generator exhausted, no significant response)
  └─ logger.warning(...)                :556      ← INCREMENT HERE
  └─ raise SerialTimeoutError(...)      :557-559
```

Two live consumers of that exception:

- `expect_ack` → `get_response` (`:568`), used by `_probe_port` (`:840`), the write/read state
  machines (`eprom_operations.py:769, 858, 613, 668`), and the hardware manager.
- `_probe_port`'s handler [VERIFIED: `firestarter_app/firestarter/serial_comm.py:926-931`] —
  verbatim:

```python
        except (SerialError, FirmwareOutdatedError) as e:
            logger.debug(f"Probe failed for {port_name}: {e}")
            if communicator:
                communicator.disconnect()
            if isinstance(e, FirmwareOutdatedError):
                raise
```

`SerialTimeoutError` is a subclass of `SerialError`
[VERIFIED: `firestarter_app/firestarter/exceptions.py:13-22`] — verbatim:

```python
class SerialError(Exception):
    """Custom exception for serial communication errors."""

    pass


class SerialTimeoutError(SerialError):
    """Custom exception for serial timeouts."""

    pass
```

**Therefore: a probe of a non-responding candidate port produces exactly one `get_response` timeout,
swallowed into `return None`, on every connect that has to walk past a wrong port.** On the project's
own three-board rig (`/dev/ttyACM0` leonardo, `/dev/ttyACM1` uno, `/dev/ttyUSB0` uno328pb — the
exact fleet recorded in `.planning/phases/118-.../118-MEASUREMENT.md` §2) this is not hypothetical.
This is the single most important finding in §4 and it drives §9.

Mitigating factor, in the code's favour: `_probe_port` calls
`config_manager.remember_port(port_name)` on success (`:913`), and `find_and_connect` tries the
remembered port first, so after the *first* successful connect in a session the later ~30 connects
normally hit on probe #1 with no timeout. The inflation is bounded and front-loaded, not per-connect
— **but it is not zero, and it is not measured.** MEAS-01's bench run is the opportunity to measure
it, and a plan should take that opportunity (§6).

### `retries` — **NOT WIREABLE as a transport counter.** Verdict: keep `NOT_MEASURED`.

There is **no host-side retry loop anywhere in the transport.** `serial_comm.py` contains no
`for attempt`, no `max_attempts`, no backoff, no re-send. `_read_and_parse_lines` re-syncs by
`continue`-ing the byte loop; it never re-requests anything. `expect_ack` loops
(`while True:` at `:567`) but that is *waiting for the next frame*, not retrying a send.

The word "retries" appears in three unrelated places, and none of them is a transport retry:

1. `MSG_INFO_RETRIES` (0x51) [VERIFIED: `firestarter_app/firestarter/messages.py:251-259`] —
   verbatim:

```python
    0x51: MessageDef(
        id=0x51,
        name="MSG_INFO_RETRIES",
        severity=SEVERITY_INFO,
        format="Number of retries: %d",
        params=(("u8", "dec"),),
        param_bytes=1,
        wire_format="id_frame",
    ),
```

2. `MSG_ERR_WRITE_FAILED` (0xB1) [VERIFIED: `firestarter_app/firestarter/messages.py:637-645`] —
   verbatim: `format="Failed to write memory, 0x%06x, retries: %d, bad bytes: %d",`

3. `cli_handlers.py:1777, 1790, 1842, 1950, 2046` — a `"retry_count"` key in the **voltage-
   calibration** cell dicts, an unrelated domain.

(1) and (2) are **firmware write-pulse retries** — a chip/programming-margin signal that arrives as
an INFO/ERROR id frame. They *are* observable at `_decode_id_frame` (and `MSG_INFO_RETRIES` already
lands in `seen_message_ids`). **But routing them into `TransportHealth.retries` would be actively
harmful:** it would make a marginal AT28C256 needing 3 write retries read as a *link* fault, and at
five retries it would flip `transport_suspect` to `True` — sending a triager hunting a cable while
the chip is the actual finding. That is the precise inversion RPT-C2's whole framing forbids.

**MEAS-03's answer for `retries`: not wireable to a transport meaning. It stays `NOT_MEASURED`.
Record the firmware-retry finding as the *reason*, so a later phase does not "fix" it.**

### `cobs_errors` — **NOT WIREABLE.** Verdict: keep `NOT_MEASURED`.

COBS on this link is **outbound only**. `cobs_encode` is called at `serial_comm.py:249`
(`send_json_command`) and `eprom_operations.py:807` (data-chunk frames). `cobs_decode` is defined at
`frame_parser.py:105` and — verified by grepping the whole tree — is called from **tests only**
(`test_cobs.py`, `test_serial_comm.py`, `test_even_block.py`, `test_frame_vectors.py`,
`test_lock_status_wire.py`). Zero production call sites. The **inbound** path is
magic-preamble + length + CRC8 framing, not COBS. A COBS decode error is therefore an event the
host cannot have. `NOT_MEASURED` here is correct and this phase should say so and move on.

### `crc_failures` — reachable in principle, but **not by the Site-C counter**.

`codec.decode_id_frame` does detect CRC mismatch specifically
[VERIFIED: `firestarter_app/firestarter/codec.py:198-204`] — verbatim:

```python
    crc_expected = _crc8_ccitt(bytes([msg_id]) + params_bytes)
    if crc_expected != crc_received:
        logger.warning(
            f"CRC mismatch for ID 0x{msg_id:02x}: "
            f"expected 0x{crc_expected:02x}, got 0x{crc_received:02x}"
        )
        return None
```

But the caller only sees `None`, which conflates five causes (§1 Site C). Two lawful routes:

- **(a) Cheap and honest:** count Site C under a *new* key with a name that says what it is —
  `decode_failures` — and leave `crc_failures` at `NOT_MEASURED` with the reason recorded
  ("reachable only by changing `codec.decode_id_frame`'s return type; out of scope").
- **(b) Precise and more invasive:** have `decode_id_frame` also increment a CRC-specific counter at
  `:199-204`. `codec.py` is mypy-strict and is itself described as "Read-path-adjacent — behavior
  preserved verbatim from serial_comm.py per Ring-fenced" (`codec.py:173-174`), so this is a
  second, softer ring fence. It is **not** under the SHA pin, so it is cheaper than §7's problem.

**Recommendation: (a).** It satisfies RPT-C1 literally ("`_decode_id_frame` returning `None` …
increment**s** a real counter") and keeps `crc_failures` honest. Route (b) can be a follow-up.

### MEAS-03 summary table

| Slot | Wireable? | Increment site | Disposition |
|---|---|---|---|
| `cobs_errors` | **No** — host never COBS-decodes | none exists | `NOT_MEASURED`, reason recorded |
| `crc_failures` | Only via `codec.py` change | `codec.py:199-204` | `NOT_MEASURED` under route (a); optional follow-up |
| `retries` | **No transport meaning** — the only retries are firmware write-pulse retries | n/a | `NOT_MEASURED`, reason recorded |
| `timeouts` | **Yes** | `serial_comm.py:556` | Wire it. Scope + reset semantics must be stated (§9) |
| *(new)* re-sync: length | Yes | `serial_comm.py:485-490` | Ring fence (§7) |
| *(new)* re-sync: body truncated | Yes | `serial_comm.py:500-505` | Ring fence (§7) |
| *(new)* `decode_failures` | Yes | `serial_comm.py:349` (`_decode_id_frame` wrapper) | Free — no fence |

---

## 5. How to test each path independently

### The existing fake serial — use it, do not build one

`tests/conftest.py` already ships everything needed. Two fixtures
[VERIFIED: `firestarter_app/tests/conftest.py:140-238`]:

- `_FakeSerial` (`:140-193`) — a `BytesIO`-backed stand-in. Its docstring, verbatim:

> `Implements only the surface that `SerialCommunicator._read_and_parse_lines` consumes: `read(n)` returning up to n bytes (b'' on empty — matches pyserial timeout-empty semantics), `is_open`, `in_waiting`, `port`, `timeout`, `write(...)`, `flush()`, and `close()`.`

  Key detail: `read(n)` returns `b""` when exhausted, which is exactly the pyserial timeout-empty
  semantics `_read_and_parse_lines` branches on at `:454`.

- `fake_serial` fixture (`:196-199`) and `make_comm` factory fixture (`:202-238`), which builds a
  `SerialCommunicator` via `__new__` to bypass the real port open, verbatim from `:211-216`:

```python
    def _factory():
        instance = SerialCommunicator.__new__(SerialCommunicator)
        instance.connection = fake_serial
        instance.port_name = "/dev/null"
        instance.baud_rate = 250000
        instance.timeout = 0.1
```

- `build_frame(msg_id, params)` (`:127-137`) assembles a correct wire frame with a **table-free
  reference CRC8** so a test cannot pass tautologically on a bug in the production lookup table.

**`make_comm` bypasses `__init__`, so it does not set any attribute `__init__` sets.** If the
counters are per-instance, `make_comm` must be extended (it already mirrors seven `__init__`
attributes for exactly this reason, `:218-235`). **This is another argument for a module-level
sink: a module sink needs no `make_comm` change at all.**

### Cheapest honest trigger for each of the four paths

All four are driven purely by bytes fed to `fake_serial` — no board, no monkeypatching of
`time.time` (the suite forbids that; see `test_timeout_raises_on_empty`'s docstring).

| Path | Trigger | Why it is honest |
|---|---|---|
| **A — length bytes missing** | `fake_serial.feed(MAGIC_PREAMBLE_REF)` and nothing more, then drive `_read_and_parse_lines(0.05)` to exhaustion. `self.connection.read(2)` returns `b""` → `len(len_bytes) < 2`. | Exercises the real branch through the real byte loop. |
| **B — body truncated** | `feed(MAGIC_PREAMBLE_REF + struct.pack(">H", 8) + b"\x01\x02")` — a declared length of 8 with only 2 body bytes available. `read(8)` returns 2 → `len(body) != frame_len`. | Same. |
| **C — decode returns `None`** | Two options. **Cheapest:** call `comm._decode_id_frame(len(body), body)` directly with a CRC-flipped body — `tests/test_serial_comm.py:336-367` already does exactly this shape for the fault-injection subclass. **Most end-to-end:** feed a complete, well-formed frame with the last (CRC) byte XOR'd by 1 and drive the generator. | The end-to-end form also proves the generator's `if decoded is not None` drop is what the counter now observes. |
| **D — response timeout** | `comm.get_response(timeout=0.02)` with nothing fed. Already an existing test. | See below. |

Path D's existing test, verbatim [VERIFIED: `firestarter_app/tests/test_serial_characterization.py:105-123`]:

```python
def test_timeout_raises_on_empty(make_comm, fake_serial):
    """Pin: with no data fed, get_response(timeout=0.02) raises SerialTimeoutError
    and completes in well under 0.5 seconds.

    Uses the tiny-real-clock technique (RESEARCH Pattern 5): a 20 ms timeout is
    long enough for the generator loop to spin through several empty reads, short
    enough that the test completes in < 25 ms total. No time.time monkeypatching
    (per binding constraint 7 / RESEARCH anti-pattern).
    """
    comm = make_comm()
    # No data fed — get_response must raise SerialTimeoutError quickly
    start = time.time()
    with pytest.raises(SerialTimeoutError):
        comm.get_response(timeout=0.02)
```

**The "tiny-real-clock" 20 ms technique is the house pattern for all four legs. Copy it.**

### The "+1 and nothing else moved" assertion shape

The success criterion demands *"that path's counter increases by exactly one while no other counter
moves."* The cleanest shape, given a module sink exposing a `snapshot() -> dict[str, int]`:

```
before = counters.snapshot()
<trigger exactly one path>
after = counters.snapshot()
assert after[target] == before[target] + 1
assert {k: v for k, v in after.items() if k != target} == \
       {k: v for k, v in before.items() if k != target}
```

The second assertion is the load-bearing half and is what makes the leg non-vacuous. Note a real
interaction the planner must design around: **Path B (truncated body) does *not* reach
`_decode_id_frame`, but Path C's end-to-end form *does* pass through the generator, and a whole
`get_response` call that never yields will *also* trip Path D.** So the C and D legs must be
isolated deliberately — drive `_read_and_parse_lines` directly (not `get_response`) for A/B/C, and
use `get_response` only for D.

### Existing test files a plan will touch

| File | Why |
|---|---|
| `tests/test_serial_comm.py` | Home of the ring-fence SHA pin (`:430`) and the `_decode_id_frame` seam tests (`:464+`). New counter tests fit here or in a new module. |
| `tests/test_serial_characterization.py` | Home of `test_timeout_raises_on_empty`; a **mypy strict-island** module (`pyproject.toml:180-183`). |
| `tests/test_diagnostic_report.py:550-561` | `test_transport_not_measured` asserts all four counters == `NOT_MEASURED` on a default-constructed report. Stays green **only if the dataclass defaults remain `None`** — see §10 Pitfall 4. |
| `tests/test_blast_radius_invariance.py:144-150, 443-449` | The pinned `transport_health` key list — §8. |
| `tests/conftest.py:202-238` | `make_comm`, if and only if counters are per-instance. |

Baseline measured this session: `pytest tests/test_diagnostic_report.py tests/test_serial_comm.py
tests/test_serial_characterization.py tests/test_decoder.py -o addopts="" -q` → **155 passed in
0.78 s** [VERIFIED: run in `.venv311` this session].

---

## 6. MEAS-01 — the bench measurement and its artifact

### What "a connect" is, precisely

`SerialCommunicator.find_and_connect(...)` [VERIFIED: `firestarter_app/firestarter/serial_comm.py:942-1057`].
Per candidate port it calls `_probe_port` (`:796-940`), which does, in order:

1. `SerialCommunicator(port=..., baud_rate=...)` (`:817`) → `serial.Serial(...)` then
   `time.sleep(CONNECTION_STABILIZE_DELAY)` [VERIFIED: `serial_comm.py:191-197`] — verbatim:

```python
            self.connection = serial.Serial(
                port=self.port_name,
                baudrate=self.baud_rate,
                timeout=self.timeout,
            )
            time.sleep(CONNECTION_STABILIZE_DELAY)  # Allow port to stabilize
```

   with [VERIFIED: `serial_comm.py:78`] — verbatim: `CONNECTION_STABILIZE_DELAY = 2.0  # seconds after opening port`

2. `communicator.consume_remaining_input()` (`:822`) — default `timeout: float = 0.5`
   [VERIFIED: `serial_comm.py:585`], which exhausts the generator for the full 0.5 s window.
3. `communicator.send_json_command(command_to_send)` + `expect_ack()` (`:839-840`).
4. The version gate and the shield-revision gate (`:853-909`) — pure policy, no extra round trip
   (CAP-02 folded the old `CMD_FW_VERSION` pre-probe away; see the comment at `:824-829`).

**Structural floor, board-independent: `2.0 + 0.5 = 2.5 s` before a single command byte is sent.**
This is a *host-side constant*, not a board property — and it is the first thing the measurement
should separate out, because it means the Uno-vs-Leonardo *difference* rides entirely on what
happens inside and around those two fixed sleeps.

**Uno-class dominant term (hypothesis to be tested, not assumed):** opening the port asserts DTR,
which auto-resets the ATmega328P and drops it into the optiboot bootloader, which waits before
handing off to the sketch. The 2.0 s stabilize sleep is presumably *why* that constant exists and
is presumably sized to cover it — so on an Uno the bootloader wait may be entirely *inside* the
2.0 s and invisible, or it may push past it and cost more. **Measurement is the only way to know,
which is exactly why MEAS-01 exists.** [ASSUMED — the DTR/optiboot mechanism is training knowledge;
this repo contains no measurement of it, and `CONNECTION_STABILIZE_DELAY`'s comment gives no
derivation.]

**Leonardo-class:** native USB CDC; opening a port does not reset the MCU (the 1200-baud touch
does), so no bootloader wait is expected — but USB re-enumeration may substitute. Also
[ASSUMED] for the same reason. Note the project fact that a Leonardo's 1200-baud touch reappears on
the *same* device node (`project_v134_phase160_closed_measured_rig_facts.md`), which matters for the
harness's port-identity discipline, not for the cost itself.

### How many connects a run makes

From `.planning/notes/dev-test-sequence-cost-model.md` [CITED: `.planning/notes/dev-test-sequence-cost-model.md:17-23, 109-119`], verbatim:

> `The **connect model** is a stronger claim, because it is derived structurally from the code rather than fitted to the log — and it then reproduces the observed count exactly (**13 predicted, 13 observed**). Its per-connect *cost* is unmeasured: `/dev/ttyACM0` was in use during the session, so the model reports counts only and no seconds are attributed to connection overhead anywhere below.`

and

> `Every connect is a `_setup_operation` → [`find_and_connect`](../../firestarter_app/firestarter/serial_comm.py#L943) → `_disconnect_programmer` round trip; `EpromOperator.comm` is torn down after`

The same note's closing section, verbatim [CITED: `.planning/notes/dev-test-sequence-cost-model.md:167-171`]:

> `## What this note does not establish`
> `- Per-connect cost in seconds (port busy; counts only).`
> `- Whether `erase` scales with device size.`
> `- Any rate for an Uno-class board (512 B buffer).`

**MEAS-01 fills the first and third of those bullets exactly.** The plan should update this note —
or write a sibling — rather than leaving the "does not establish" list stale.

Two independent connect sources per run, both must be in scope:

- `EpromOperator._setup_operation` (`eprom_operations.py:491`) — one per plan step.
- `hardware_manager` sampler reads — `_make_sampler` (`cli_handlers.py:2194-2218`) calls
  `sample_vpp_mv()` and `sample_vpe_mv()`, each of which does its own `find_and_connect`
  (`hardware.py:283, 406`), at both the `before` and `after` phases. The cost note calls this
  "the sampler costs 4 connects per write step" (§4 heading). Plus
  `read_programmer_identity()` (`cli_handlers.py:2379` → `hardware.py`).

### The measurement harness — a precedent already exists in-tree

`EpromOperator.measure_command_nak_latency` [VERIFIED: `firestarter_app/firestarter/eprom_operations.py:1517`],
docstring verbatim (excerpt):

> `Unlike fault_inject_cycle (which corrupts the connection-SETUP frame and so triggers find_and_connect's multi-port retry — inflating the latency), this opens ONE pinned port directly, then on the SAME open connection: ...`

and

> `Returns True iff baseline OK AND the corrupted frame surfaced an error (no silent accept) AND the clean recovery transfer succeeded. Writes fault-inject-<fault_form>-latency.txt with the precise per-frame latency.`

**Copy this shape.** It is a dev-only `EpromOperator` method (`:1517`), it pins one port explicitly
(`-p <port>` / `config.port`), it writes a timestamped artifact via a `_write_*_log` helper
(`:1635`), and it already carries the exact warning MEAS-01 needs to heed: *multi-port retry inflates
the number*. A per-connect measurement that does not pin the port measures the discovery walk, not
the connect.

**Suggested method shape:** `measure_connect_cost(samples: int, port: str) -> bool` — N repetitions
of `find_and_connect` → `disconnect`, each timed, reporting min/median/max per port, run once per
board class, never blended. Reported **per board class as two artifacts** (success criterion 3).

**HYG-04 check:** a *dev test handler* helper must be registered. A method on `EpromOperator` is
**not** a `dev_test` handler helper, so `_HANDLER_FUNCTION_NAMES` is not triggered by this route.
If instead a helper function is added to `cli_handlers.py` alongside `dev_test`, it **must** be added
to [VERIFIED: `firestarter_app/tools/check_devtest_orchestrator.py:152-165`] — verbatim:

```python
_HANDLER_FUNCTION_NAMES = frozenset(
    {
        "dev_test",
        "_verdict_code",
        "_overall_exit_code",
        "_dev_test_exit_code",
        "_sanitize_chip_token",
        "_is_uv_eprom",
        "_resolve_write_scope",
        "_chip_id_fields",
        "_is_interactive",
        "_make_sampler",
    }
)
```

### Artifact shape — follow the established precedent

Real precedents found under `.planning/` [VERIFIED: filesystem listing this session]:

| Precedent | Shape |
|---|---|
| `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-MEASUREMENT.md` | **Best match.** A per-phase measurement doc with §1 "What was measured, and what it is not", §2 "Provenance block" (per-port `controller:` identity verified *by command* before driving anything, build sha, clean working tree), then the numbers. |
| `.planning/phases/09-.../09-MEASUREMENT.md`, `.../07-FLASH-MEASUREMENT.md`, `.../119-MEASUREMENT.md`, `.../138-06-FIRMWARE-MEASUREMENT.md` | Same `NNN[-PP]-MEASUREMENT.md` naming family. |
| `.planning/phases/145-bench-validation/145-BENCH-LOG.md` | Per-run bench log. |
| `.planning/v1.34/bench/EVIDENCE.md` + `EVIDENCE.jsonl` | Milestone-level machine-readable + narrative pair. |

**Recommended: `176-MEASUREMENT.md` in the phase directory, following 118's section order,** with
the two board classes in two clearly separate sections and an explicit "these are never blended"
sentence. 118's §1 opens verbatim with:

> `**The subject of this measurement is the emitter, never the chip.**`

MEAS-01's equivalent sentence should be: *the subject is the host's connect sequence and the board's
reset/enumeration behaviour, never the chip* — the socket can be empty for every one of these runs.

118's §2 provenance discipline is **mandatory** here per the standing project rule that `ttyACM*`
numbers shuffle across replug: verify each port's `controller:` identity by command before driving
it, or the two board classes silently swap.

---

## 7. The ring fence — the phase's one real structural obstacle

### What it is

[VERIFIED: `firestarter_app/firestarter/serial_comm.py:407-417`] — verbatim:

```python
    # =================================================================
    # DO NOT MODIFY — v1.9 RCA territory
    # The body of this generator is the host-side baseline for v1.9's
    # read-bug RCA. Phase 26 baseline binaries (.planning/v1.6/
    # consistency-check-runs/W27C512-leonardo-20260526-*-v2*/) were
    # captured against this exact body. Structural-only changes here
    # (e.g. type hints on the signature) are OK; any change to the
    # byte-by-byte read loop, the magic-preamble dispatch, the
    # frame-length read, or the timeout reset semantics MUST be
    # flagged and deferred to v1.9 alongside binary re-validation.
    # =================================================================
```

And it is **mechanically enforced** [VERIFIED: `firestarter_app/tests/test_serial_comm.py:430-460`] —
verbatim (excerpt):

```python
def test_read_and_parse_lines_ringfence_unchanged() -> None:
    """Ring-fence compliance: _read_and_parse_lines body source is byte-identical
    to the GATE-1.8d pinned snapshot.

    This test is GREEN today — the snapshot is captured from the current body.
    It goes RED if ANY change is made to the generator body (per GATE-1.8d:
    any change must be flagged and deferred to v1.9 alongside binary re-validation).

    Pinned SHA-256 (2026-06-11): 6d9e4fe4b67b78c110418305113b275174f16b2ecc9e0f55fbf5d9a623398184
    (Updated from 544433068cb14ac14677939435cb4f0ea78783b503315ed645b5f88c5c44a444
     at Phase 65-01: Response now carries id=decoded.id for ProtocolNotImplementedError
     typed-raise dispatch. Change is in-scope for v1.12 host graceful handling — not
     a transport-path change, only adds id plumbing to the Response construction.)
    """
    import hashlib
    import inspect

    from firestarter.serial_comm import SerialCommunicator

    _PINNED_SHA256 = "6d9e4fe4b67b78c110418305113b275174f16b2ecc9e0f55fbf5d9a623398184"

    src = inspect.getsource(SerialCommunicator._read_and_parse_lines)
    actual_digest = hashlib.sha256(src.encode("utf-8")).hexdigest()
```

Verified GREEN at HEAD this session (`89 passed` for that test plus the whole 174 module).
`inspect.getsource` covers the `def` line, docstring and body — **not** the block comment above the
`def`. So editing the header comment alone would not move the digest; editing any body line will.

### Is the deferral target still live? Partly.

- **v1.9 Read-Bug RCA is still PAUSED.** [CITED: `.planning/ROADMAP.md:15`] verbatim:
  *"⏸ **v1.9 Read-Bug RCA + Fix** — Phases 44-48 (PAUSED 2026-06-01 at Phase 44 — v1.10 inserted
  ahead; resumes at Phase 45)."* Five milestones later it has never resumed.
- **The baseline binaries the fence protects still exist on disk** —
  `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-155021-v2` and siblings
  [VERIFIED: filesystem listing this session].
- **But v1.10 already exonerated the transport and re-baselined.** [CITED: `.planning/MILESTONES.md:1375`]
  verbatim: *"N=5 read self-consistency (verdict 0) + N=5 write→read-back==source (verdict 0) on
  clean Uno (512 B) and Leonardo (1024 B), Rev 2.0, on the shipped post-55 contract
  (self-consistency form per D-05 — **neither chip was the original GATE-1.8d baseline**)."*
- **And there is already a precedent for a deliberate re-pin**, recorded in the test's own
  docstring: Phase 65-01 re-pinned it, with the reasoning that its change was "not a transport-path
  change, only adds id plumbing".

### Three options, with the recommendation

| Option | What it costs | Verdict |
|---|---|---|
| **1. Re-pin the SHA deliberately, in the same commit, with the reasoning recorded in the docstring the way Phase 65-01 did.** Argue that a counter increment beside a `logger.warning` in a re-sync branch changes none of the four things the header names — the byte-by-byte read loop, the magic-preamble dispatch, the frame-length read, or the timeout reset semantics. | One re-pin, one docstring paragraph, and a reviewer's judgement call. | **RECOMMENDED.** Exactly the established precedent, satisfies RPT-C1 literally, and the argument is sound: the increment adds no read, no branch on wire bytes, no `start_time` write. |
| **2. Do not touch the body — count via a `logging.Handler`/`Filter` attached to the `SerialComm` logger, keyed on the two warning messages.** | Zero body change, zero re-pin. But it makes the two prose strings load-bearing (Site A is a constant string; Site B is an f-string so only a prefix match works), and it silently mis-counts if anyone rewords a warning. It also couples the counters to logging configuration. | **Fallback only.** Honest but fragile, and it trades a checkable pin for an uncheckable prose dependency. |
| **3. Defer Sites A and B; wire only C and D.** | Cheapest. But RPT-C1 names all four explicitly, so the phase would close with two of its four named sites unmet. | **Rejected** unless the operator explicitly re-scopes RPT-C1. |

**A plan MUST make this an explicit, named decision with a `checkpoint:human-verify` before the
re-pin lands.** The fence is a deliberate operator-era safety marker; silently re-pinning it inside
an autonomous run is precisely the kind of thing this project's discipline exists to prevent.

---

## 8. Phase 174's oracle — what runs it, and what goes red

### The command

[VERIFIED: `.planning/phases/174-blast-radius-invariance-harness/174-VERIFICATION.md:93`] — verbatim:

```
pytest tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py tests/test_devtest_issue_corpus.py tests/test_part_number_delta_drift.py -o addopts="" -q
```
→ recorded result `122 passed in 11.10s`. Phase 175 re-ran the two-module subset and recorded
`114 passed` [CITED: `.planning/phases/175-.../175-VERIFICATION.md:99`]. Verified green at HEAD this
session for `tests/test_blast_radius_invariance.py` alone (88 tests, within the 89 total).

### What goes red when a new counter appears in the report

**Not the frozen hashes.** `dedup_fingerprint` provably does not read `transport_health`
[VERIFIED: `firestarter_app/firestarter/diagnostic_report.py:211-240`] — verbatim, the entire input
construction:

```python
    ac = report.auto_capture
    parts = [ac.chip or "", str(ac.protocol or "")]
    for result in report.results:
        cls = result.fingerprint.classification if result.fingerprint else ""
        parts.append(f"{result.op}={result.verdict}:{cls}")
```
...
```python
    canonical = "|".join(parts)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
```

Plus `repeat_policy_tag` and `coverage_tag` appended only when non-empty. **No `transport` read.**
Therefore `FROZEN_HASHES` does not move, `test_dedup_fingerprint_is_frozen` stays green, and
**this phase needs no re-key ledger row and no `MILESTONES.md` row.** Confirmed independently: the
ledger's six rows are owned by Phases 177, 178, 179, 181 and `rejected` — **there is no `p176` owner**
[VERIFIED: `firestarter_app/tests/fixtures/rekey_ledger.py:26-77`, grep for `p176` returns nothing].

**Two things DO go red if a key is added:**

1. **`test_to_dict_transport_health_key_list_is_pinned`**
   [VERIFIED: `firestarter_app/tests/test_blast_radius_invariance.py:144-150`] — the pin, verbatim:

```python
_TRANSPORT_HEALTH_KEYS = [
    "cobs_errors",
    "crc_failures",
    "retries",
    "timeouts",
    "transport_suspect",
]
```

   This is a **sorted element-wise equality**, so an added key fails it. Per D-07's stated intent
   this is the gate working as designed — [CITED: `.planning/phases/174-.../174-CONTEXT.md:102-108`],
   verbatim: *"It also means Phase 181's three key deletions ... are measured against a gate that
   predates them, rather than landing in the same phase as their own gate."* The same reasoning
   applies to an addition. **Update `_TRANSPORT_HEALTH_KEYS` deliberately, in the same commit as
   the production change.** (Note the neighbouring `_AUTO_CAPTURE_KEYS` test at `:430-441` even
   models the pattern with an explicit "update deliberately in the same commit" assertion message.)

2. **All 16 committed report snapshots.** Every one of `tests/fixtures/reports/*.json` carries a
   full `transport_health` block [VERIFIED: `tests/fixtures/reports/gh20-at28c256-fail.json`, read
   this session] — verbatim:

```json
{"cobs_errors": "not measured", "crc_failures": "not measured", "retries": "not measured", "timeouts": "not measured", "transport_suspect": false}
```

   `test_committed_snapshot_matches_a_fresh_regeneration`
   (`test_blast_radius_invariance.py:566`) is parametrised over all 16 and compares against a fresh
   regeneration. **Re-baseline procedure:** run `python3 tools/snapshot_report_shapes.py` to
   rewrite all 16, then `python3 tools/snapshot_report_shapes.py --check` to prove zero drift.
   The tool's exit codes [VERIFIED: `firestarter_app/tools/snapshot_report_shapes.py:24-28`] —
   verbatim:

```
Exit codes:
  0 -- wrote every target (or, under --check, every target already matched
       a fresh regeneration)
  1 -- --check found drift, or a --check target does not exist
  2 -- a --shape value is not in tests.fixtures.report_shapes.SHAPE_IDS
```

   Because the snapshots normalise the one volatile field (`generated` → `1970-01-01T00:00:00Z`)
   and stamp `_generated_by`, the regeneration is deterministic and the resulting diff should be
   exactly 16 files × one added line each. **Any other diff is a signal, not noise.**

**If instead the phase adds no key and only *populates* `timeouts` in production**, neither gate
moves — `build_shape` constructs `TransportHealth()` with defaults, so the snapshots keep reading
`"not measured"`. That is a genuinely cheaper path and the plan should weigh it: it satisfies
RPT-C2's "surfaces the real count" for `timeouts` at zero oracle cost, but leaves the three re-sync/
decode counters with nowhere honest to go.

---

## 9. MEAS-02 — the `_SUSPECT_THRESHOLD = 5` re-derivation

The threshold has never been exercised: `_is_transport_suspect`'s own docstring says *"this always
returns False in production"*, and the only test touching it asserts `transport_suspect is False`
(`test_diagnostic_report.py:561`). There is no test at 4/5/6.

**The strongest available basis for re-derivation is §4's probe-timeout finding, and it is a real
argument, not a formality:**

- Under a naive process-global `timeouts` counter, a `dev test` run on a three-board rig where the
  remembered port is wrong pays one timeout per wrong candidate per connect. The cost note's model
  puts a `dev test` run at ~13 connects for a six-step chip and the AT28C256's SDP leg at
  "12 connects for roughly 3 KB" [CITED: `.planning/notes/dev-test-sequence-cost-model.md:146`],
  with R4-01 citing "32 connects for one at28c256 run"
  [CITED: `.planning/REQUIREMENTS.md:122`]. **At 32 connects, a threshold of 5 is crossed by the
  sixth wrong-port probe — reporting a healthy rig as transport-suspect.**
- Three lawful responses, each defensible, and the plan must pick one and record the basis
  (success criterion 4 demands the basis, not merely a number):
  1. **Scope the counter so probe failures do not count.** Increment `timeouts` only for
     `get_response` calls made on an *established* connection — i.e. not from inside `_probe_port`.
     This is the honest fix and it makes `5` defensible unchanged, which is a legitimate MEAS-02
     outcome ("justified against real counts").
  2. **Keep the counter global and raise the threshold**, deriving the new value from the measured
     per-run probe-timeout count on the actual rig. This requires the MEAS-01 bench run to *also*
     record probe-timeout counts — a near-free addition to that harness, and the plan should ask
     for it.
  3. **Make the threshold per-counter** rather than one shared constant, since a single re-sync is
     far more alarming than a single probe timeout. Most work; most honest.
- **Whatever is chosen, MEAS-02's deliverable is the recorded basis.** A plan that changes `5` to
  some other integer without an argument has not met the criterion; a plan that *keeps* `5` with
  the scoping argument above **has**.

**Do not derive the threshold from `.planning` prose alone.** The bench run in §6 is the natural
place to observe a real count, and it is the only place in this phase where a real count exists.

---

## Standard Stack

**No new library. Nothing to install.** HYG-02 forbids a new runtime dependency, the counters are
plain integers, and every needed test facility already exists in-tree.

### Core (already present, all pinned by `pyproject.toml`)

| Component | Purpose | Why standard here |
|---|---|---|
| `dataclasses` (stdlib) | `TransportHealth` is already a `@dataclass`; new fields go in as `int \| None = None` | Matches the existing shape exactly; no `frozen=True`, so post-`run_plan` assignment is legal |
| `pytest` + `tests/conftest.py::_FakeSerial`/`make_comm` | All four paths are byte-triggerable without a board | Already the house pattern for this module (§5) |
| `inspect` + `hashlib` (stdlib) | The ring-fence pin | Already in `test_serial_comm.py` |
| `time.perf_counter` (stdlib) | Per-connect timing | Correct clock for a duration; `time.time()` is used elsewhere in this file but `perf_counter` is the right tool for an interval measurement |

### Alternatives considered

| Instead of | Could use | Tradeoff |
|---|---|---|
| A module-level counter sink | A `ClassVar` counter on `SerialCommunicator` | Works (survives instance teardown, and the file already declares CAP-02 identity fields at class level for a related reason at `:115-128`), but pollutes the transport class's namespace, is harder to reset cleanly in tests, and `make_comm`'s `__new__` path makes class-vs-instance shadowing a live footgun. |
| A module-level counter sink | `contextvars` / thread-local | The CLI is single-threaded and single-process. Real complexity for no benefit. |
| Counting in code | A `logging.Handler` counting warnings | Avoids the ring fence (§7 option 2) but makes prose load-bearing. Fallback only. |
| `perf_counter` | `time.time()` | `time.time()` is wall-clock and can step. For a 2.5 s interval either works; `perf_counter` is simply correct. |

---

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.**

HYG-02 [VERIFIED: `.planning/REQUIREMENTS.md:108`] verbatim: *"**HYG-02**: No new runtime dependency
is added. The shipped set stays `pyserial, requests, tqdm, click, rich, packaging`."* Every module
used by this phase is either stdlib or already in that set. The Package Legitimacy Gate was
therefore not run and no `[SLOP]`/`[SUS]` verdicts exist to report. If a plan proposes a package,
that plan has violated HYG-02 and should be rejected at plan-check before any legitimacy check is
needed.

---

## Architecture Patterns

### Recommended shape

```
firestarter/transport_counters.py   (NEW — module-level sink, no imports from serial_comm)
  ├─ four module-level ints
  ├─ record_*() incrementers        ← called from serial_comm
  ├─ reset() -> None
  └─ snapshot() -> dict[str, int]   ← read by cli_handlers

firestarter/serial_comm.py          (increments only; never reads back)
  ├─ :349  _decode_id_frame  → record on `result is None`         [free]
  ├─ :485  re-sync length            [ring fence — §7]
  ├─ :500  re-sync body truncated    [ring fence — §7]
  └─ :556  get_response timeout      [free, but scope it — §9]

firestarter/cli_handlers.py         (the ONLY reader)
  ├─ ~:2380  transport_counters.reset()        ← before the measured window
  └─ ~:2412  report.transport = TransportHealth(**snapshot-derived kwargs)
                                                  after run_plan returns

firestarter/diagnostic_report.py    (serialisation + policy; imports NOTHING transport)
  ├─ TransportHealth: new int|None fields
  ├─ _transport_dict(): new NOT_MEASURED substitutions
  └─ _is_transport_suspect(): extend the scanned tuple (domain, not rule)
```

**Data flow, one direction only:** `serial_comm` writes → sink → `cli_handlers` reads → threads into
`DiagnosticReport`. `diagnostic_report.py` never imports `serial_comm`; `serial_comm.py` never
imports `diagnostic_report`. This preserves the orchestrator-only contract *and* keeps the import
graph acyclic.

### Pattern 1 — thread values in, never fetch them

The file already models this exactly [VERIFIED: `firestarter_app/firestarter/diagnostic_report.py:15-18`] — verbatim:

```python
ORCHESTRATOR ONLY: this module imports no transport or hardware class, sets no
VPP, builds no wire dict, passes no force flag and adds no firmware dispatch.
`fw_board_identity` and `hw_revision` are threaded IN as input -- this module
never fetches them and never opens a connection.
```

The transport counts are the third member of that family. Follow it.

### Pattern 2 — additive siblings, never replacement

The house rule the whole milestone rests on. `coverage_tag`'s comment states it exactly
[VERIFIED: `firestarter_app/firestarter/diagnostic_report.py:224-236`] — verbatim excerpt:

```python
    # The empty-default direction is the whole point and is deliberate.
    # Slot/fixed runs stay untagged, so every ALREADY-FILED report's
    # fingerprint remains byte-identical and no historical `count_agreeing`
    # group is re-keyed or reset.
```

Applied here: **add new keys beside `cobs_errors`/`crc_failures`/`retries`/`timeouts`; never
repurpose one of the four.** Repurposing `retries` to carry firmware write-retries would be the
project's single worst available move (§4).

### Pattern 3 — anti-vacuity is mandatory

[CITED: `.planning/phases/174-.../174-PATTERNS.md:678` §"Anti-vacuity (applies to EVERY new test
file)"]. Every counter test in this phase needs an observed-RED transcript: weaken the increment
(delete it, or make it unconditional) and *see* the test fail, transcribed into
`evidence/176-NN-*.txt`. Phase 174 and 175 both did this and both VERIFICATIONs cite the transcripts
by name. A plan that asserts RED without a transcript will not survive verification here.

### Anti-patterns to avoid

- **Defaulting the new counters to `0` instead of `None`.** Breaks
  `test_transport_not_measured` and — worse — fabricates a measurement for any code path that
  builds a `TransportHealth` without a real run. `None` means "not measured"; `0` means "measured,
  and it was zero". RPT-C2 turns on exactly that distinction.
- **Reading counters inside `diagnostic_report.py`.** Breaks the orchestrator-only contract and the
  SAFE-02 structural scan.
- **Counting the probe walk as transport health** (§9).
- **Naming the Site-C counter `crc_failures`** (§1 Site C, §4).
- **Writing explanatory comments.** Hard project rule. Docstrings only.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| A fake serial port for tests | A new mock/`Mock(spec=serial.Serial)` | `tests/conftest.py::_FakeSerial` + `fake_serial` + `make_comm` (`:140-238`) | Already models pyserial's `b""`-on-timeout semantics exactly, which is the branch `_read_and_parse_lines` keys on. A `Mock` will not. |
| A wire frame for a test | Hand-packed bytes | `tests/conftest.py::build_frame(msg_id, params)` (`:127-137`) | Uses a **table-free** reference CRC8 so a test cannot pass tautologically on a bug in the production table. |
| A "deterministic clock" for timeout tests | `monkeypatch` on `time.time` | The tiny-real-clock technique — `timeout=0.02` (§5) | Explicitly named an anti-pattern by the existing test's docstring ("No time.time monkeypatching / per binding constraint 7"). |
| A report snapshot | Hand-editing `tests/fixtures/reports/*.json` | `python3 tools/snapshot_report_shapes.py` | The files carry a `_generated_by` do-not-edit banner asserted absolutely by a live test. |
| A per-connect timing harness | A fresh script | Copy `EpromOperator.measure_command_nak_latency` (`eprom_operations.py:1517`) | Already pins one port (avoiding the multi-port-retry inflation trap it documents), already writes a timestamped artifact. |
| A "which board am I talking to" check | Assume `/dev/ttyACM0` | `firestarter -p <port> -v fw` and read `controller:` (118-MEASUREMENT §2) | Node numbers shuffle across replug. Standing project rule. |

**Key insight:** everything this phase needs already exists in-tree. The risk is not missing tooling
— it is reaching for a `Mock` or a hand-written fixture and silently losing the fidelity the
existing helpers were built to guarantee.

---

## Common Pitfalls

### Pitfall 1 — The ring-fence pin (the big one)
**What goes wrong:** a plan adds two counter lines at `:485-490` / `:500-505` and
`test_read_and_parse_lines_ringfence_unchanged` goes RED with a `GATE-1.8d VIOLATION` message.
**Why:** the pin is a SHA-256 of `inspect.getsource(...)`, so *any* character change trips it.
**How to avoid:** make the fence an explicit plan decision with a human-verify checkpoint (§7).
**Warning sign:** a plan that touches those lines without mentioning `_PINNED_SHA256`.

### Pitfall 2 — Adding a `transport_health` key without moving the 174 pin and the 16 snapshots
**What goes wrong:** `test_to_dict_transport_health_key_list_is_pinned` plus 16 parametrised
snapshot tests all go RED at once, which reads like a catastrophe and is actually one line of
intent.
**How to avoid:** same commit — update `_TRANSPORT_HEALTH_KEYS`, run
`tools/snapshot_report_shapes.py`, then `--check` (§8).
**Warning sign:** a plan with a production-change task and a separate later gate-update task.

### Pitfall 3 — A per-instance counter that is destroyed before the report reads it
**What goes wrong:** counters live on `SerialCommunicator`; `_disconnect_programmer()` sets
`self.comm = None`; the report reads zeros or `None`.
**How to avoid:** process-lifetime sink (§2). **Warning sign:** any `self._resync_count` in a plan.

### Pitfall 4 — `0` vs `None`
**What goes wrong:** new fields default to `0`; `test_transport_not_measured` goes RED, and every
synthetic report claims a measurement it never made.
**How to avoid:** dataclass defaults stay `None`; production assigns the real int (which may
legitimately be `0`) at `cli_handlers.py` after `run_plan`.

### Pitfall 5 — Counting the port-discovery walk as link sickness
**What goes wrong:** `transport_suspect: true` on a perfectly healthy three-board rig (§4, §9).
**Warning sign:** an unscoped increment at `serial_comm.py:556`.

### Pitfall 6 — Python 3.12 in the devcontainer vs 3.11 in CI
**What goes wrong:** work verified under the devcontainer default (`python3 --version` →
**3.12.14**, measured this session) passes locally and reddens `Host CI`, which pins
`python-version: '3.11'` in **both** jobs [VERIFIED: `firestarter_app/.github/workflows/ci.yml`].
This has **provably broken beta CI before** (project memory).
**How to avoid:** use the existing `firestarter_app/.venv311` (`Python 3.11.16`, verified this
session, and `import firestarter` resolves to
`/workspaces/firestarter_app/firestarter/__init__.py` — the editable install is intact).
Every verification command in the plan should be `./.venv311/bin/python -m pytest ...`.

### Pitfall 7 — Doubled `-q` hides the count line
`pyproject.toml:105-107` [VERIFIED] — verbatim:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q"
```
A plan writing `pytest ... -q` gets `-q -q`, which suppresses the `N passed` line entirely — so a
verification step "proves" nothing. **Always `-o addopts=""`.** Phase 174's and 175's VERIFICATION
commands already do.

### Pitfall 8 — `grep` in this devcontainer is `ugrep` and honours `.gitignore`
It silently under-scans. `build/lib/firestarter/` in this repo is a **stale copy** of the package
that a careless grep will match (it still carries the old `diagnostic_report.py`). Use
`/usr/bin/grep` for any evidence-producing scan, and never cite a `build/` path.

### Pitfall 9 — mypy strict on `serial_comm.py`
`disallow_untyped_defs = true` for `firestarter.serial_comm`. Any helper added there needs a full
signature. The gate is `python tools/check_mypy_watermark.py` and it also enforces
`MIN_CHECKED_SOURCE_FILES = 120` [VERIFIED: `firestarter_app/tools/check_mypy_watermark.py:48`], so
a truncated run exits 2 rather than falsely passing.

### Pitfall 10 — `dev test` reports are consumed by two skills
`.claude/skills/devtest-triage/scripts/devtest_issues.py` and
`.claude/skills/devtest-rootcause/scripts/seed_debug_session.py` read report JSON. A new
`transport_health` key is additive and should not break either (both parsers match
`schema_version` by presence only), but a plan should say it checked rather than assume.

---

## Code Examples

### The four increment sites, in the recommended shape

Site C — free, no fence, `serial_comm.py` around `:349`:

```python
        result = codec.decode_id_frame(frame_len, body)
        if result is None:
            transport_counters.record_decode_failure()
```

Site D — free, `serial_comm.py` around `:556`:

```python
        transport_counters.record_response_timeout()
        logger.warning(f"Timeout waiting for a response from {self.port_name}.")
        raise SerialTimeoutError(
            f"Timeout waiting for a significant response from {self.port_name}."
        )
```

Sites A and B — inside the fence, one line each before the existing `continue`.

### The orchestrator read, `cli_handlers.py`

```python
    transport_counters.reset()
    identity = app.hardware_manager.read_programmer_identity()
    ...
    results = run_plan(...)
    report.results = results
    report.transport = TransportHealth(**transport_counters.snapshot())
```

(The exact `**snapshot()` spelling only works if the sink's key names match the dataclass field
names exactly; an explicit keyword construction is safer and mypy-strict-friendly, since
`cli_handlers` is in the strict island.)

### The "+1 and nothing else moved" test

```python
def test_body_truncated_resync_increments_only_its_own_counter(make_comm, fake_serial):
    """Feeding a magic preamble with a declared length longer than the bytes
    available trips serial_comm.py:500-505 exactly once and moves no other counter."""
    comm = make_comm()
    transport_counters.reset()
    before = transport_counters.snapshot()
    fake_serial.feed(MAGIC_PREAMBLE_REF + struct.pack(">H", 8) + b"\x01\x02")
    list(comm._read_and_parse_lines(0.05))
    after = transport_counters.snapshot()
    assert after["resync_body_truncated"] == before["resync_body_truncated"] + 1
    assert {k: v for k, v in after.items() if k != "resync_body_truncated"} == {
        k: v for k, v in before.items() if k != "resync_body_truncated"
    }
```

---

## Runtime State Inventory

**Not applicable — this is not a rename, refactor or migration phase.** No stored data, no live
service config, no OS-registered state, no secrets and no build artifacts carry a string this phase
changes. Two adjacent items are worth naming so nobody mistakes them for runtime state:

- **`tests/fixtures/reports/*.json` (16 files)** are committed *test fixtures*, not runtime state,
  but they are regenerated by a tool and must be regenerated in the same commit as a key addition
  (§8).
- **`~/.firestarter/config.json`** carries the remembered `port` (via
  `config_manager.remember_port`), which affects how many probe timeouts a connect pays (§9). A
  bench run's numbers are therefore sensitive to it. Do **not** delete that directory (standing
  project finding: the app writes there despite `FIRESTARTER_CONFIG_DIR`); instead pin `-p <port>`
  explicitly, as `measure_command_nak_latency` already does.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Python 3.11 venv | Every unit-test leg (CI parity) | ✓ | `.venv311` → 3.11.16 | Devcontainer 3.12.14 — **do not use for verification** |
| Editable `firestarter` install in `.venv311` | Test runs | ✓ | resolves to `/workspaces/firestarter_app/firestarter/__init__.py` | — |
| `pytest` + suite | RPT-C1/C2, MEAS-02, MEAS-03 | ✓ | 155 passed across the 4 relevant modules, 0.78 s | — |
| `tools/snapshot_report_shapes.py` | Re-baselining the 16 snapshots | ✓ | in-tree | — |
| **Arduino Uno-class board (512 B)** | **MEAS-01** | **✗** | — | **None. This is a hard gate.** |
| **Arduino Leonardo-class board (1024 B)** | **MEAS-01** | **✗** | — | **None. This is a hard gate.** |
| `dialout` group membership | Driving a board when one is attached | ✓ | user `vscode` is in `dialout` | — |

**Missing dependencies with no fallback:**

- **No serial device is attached to this container right now.** `ls /dev/ttyACM* /dev/ttyUSB*` →
  `No such file or directory` [VERIFIED: run this session]. MEAS-01 cannot execute until the
  operator attaches an Uno-class board and a Leonardo-class board. The container *does* have
  `dialout` group membership and this project has USB passthrough, so once a board is attached an
  agent can drive it directly — **photos, multimeter readings and chip handling remain
  operator-only, but MEAS-01 needs none of those** (the socket can be empty for every connect-cost
  run, which is a genuine scheduling advantage worth stating in the plan).

**Planning consequence:** the phase splits cleanly into a fully-autonomous software half
(RPT-C1, RPT-C2, MEAS-02's argument, MEAS-03) and a blocked bench half (MEAS-01, plus MEAS-02's
optional empirical leg). **A plan should sequence the software half first and gate MEAS-01 behind a
`checkpoint:human-verify` that asks the operator to attach and identify both boards** — matching the
ROADMAP's own "partially hardware-gated" framing and the milestone's note that MEAS-01 "has lead
time".

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| Text-prefix wire protocol (`OK:`, `DATA:` …) | Magic-preamble + u16 length + CRC8 id frames; text kept for `OK`/`DATA` only | v1.2 / Phase 6 D-05 | Both re-sync sites are id-frame-path only. A text-path line never re-syncs. |
| Dedicated `CMD_FW_VERSION` pre-probe on every connect (2 extra acks) | CAP-02 folds identity + hw revision into the `MSG_OK_READY` operation-setup ack | Phase ~55+ | A connect is now **one** command exchange. MEAS-01 measures the post-CAP-02 shape. |
| Raw JSON on the command channel | COBS `0x00` + CRC8 framing, **outbound only** | v1.10 | Why `cobs_errors` is unreachable inbound (§4). |
| `_calculate_buffer_size` raising `FirmwareOutdatedError` on absent advertisement | Returns 512, the safe Uno floor | CAP-01 | The "Uno 512 / Leonardo 1024" board classes in MEAS-01 are the `firmware_max_chunk` advertisement, not a host guess. |

**Deprecated / outdated in the sources a planner may consult:**

- **`ROADMAP.md:5283`'s `serial_comm.py:520-526` / `:536-541` citations are STALE.** They come from
  the 2026-08-23 backlog-999.36 sweep. `REQUIREMENTS.md:91`'s `:485-490` / `:500-505` are correct at
  HEAD. Use REQUIREMENTS.md.
- `diagnostic_report.py:104-110`'s docstring claim that *"no COBS-decode-error / CRC-failure /
  retry / timeout counter is reachable"* conflates **reachable** with **existing**. §4 shows
  `timeouts` was always reachable and nobody wired it; `cobs_errors` and `retries` genuinely are
  not. **That docstring must be corrected by this phase** — leaving it is exactly the "the code
  knew the field was dead, wrote it down, and shipped it anyway" pattern the milestone was scoped
  against.
- `.planning/notes/dev-test-sequence-cost-model.md`'s "What this note does not establish" list goes
  stale the moment MEAS-01 lands. Update it or supersede it.

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. This
phase adds no network surface, no authentication, no session, no access control and no
cryptography. The applicable slice is narrow but real.

### Applicable ASVS categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | No identity surface. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | no | Local CLI, single user. |
| V5 Input Validation | **yes** | The counters observe **attacker-influenceable input**: a hostile or malfunctioning board controls the byte stream that drives all four sites. The existing defensive posture must be preserved. |
| V6 Cryptography | no | CRC8 is an integrity check, not a security control, and `dedup_fingerprint`'s own docstring says so ("A non-secret dedup id, not a security control"). Do not "upgrade" it. |
| V7 Error Handling & Logging | **yes** | The counters are a logging/observability surface reachable from the wire. |

### Threat patterns for this change

| Pattern | STRIDE | Mitigation |
|---|---|---|
| Unbounded growth of a wire-driven counter | Denial of Service | Plain `int` — Python ints are arbitrary-precision, so there is no overflow, but a hostile board can drive the count arbitrarily high. That is acceptable (memory cost is O(log n)) and is strictly better than the existing `seen_message_ids` set, which is bounded by construction. **Do not store anything sized from frame content** — the file's own defensive rule (`serial_comm.py:179-185`, `:364-368`). |
| A hostile board suppressing suspicion | Tampering | `_is_transport_suspect` reads counts the *host* increments, never a value the board sends. Preserve this: never populate a `TransportHealth` field from a wire parameter (which is a second reason not to route `MSG_INFO_RETRIES` into `retries`). |
| Report field used to mislead a triager | Spoofing / Repudiation | Exactly what RPT-C2's `NOT_MEASURED`-vs-`0` rule prevents. A fabricated `0` is the security-relevant failure here. |
| Counter increments leaking into a hot loop | DoS (self-inflicted) | Site C runs per frame; on a 64 KiB read that is thousands of calls. An `int += 1` is negligible, but a `logging` call or a lock would not be. Keep the incrementers trivial. |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | On Uno-class boards, opening the port asserts DTR, resetting the ATmega328P into optiboot, and the bootloader wait is the dominant per-connect term. | §6, MEAS-01 | Low — MEAS-01 exists to test this. If wrong, the measurement simply reports a different dominant term and the requirement is still met. **Must not be written into the plan as an established fact.** |
| A2 | Leonardo-class boards do not reset on port open (only on the 1200-baud touch), so they pay no bootloader wait. | §6 | Same as A1. |
| A3 | `CONNECTION_STABILIZE_DELAY = 2.0` was sized to cover the Uno bootloader wait. | §6 | Low. The constant's comment gives no derivation and no `.planning/` document explains it. If the plan wants to *reduce* it based on MEAS-01, that is a separate, riskier change and out of this phase's scope. |
| A4 | Adding a counter increment beside a `logger.warning` in a re-sync branch does not change "the byte-by-byte read loop, the magic-preamble dispatch, the frame-length read, or the timeout reset semantics". | §7 option 1 | **Medium — this is the phase's key judgement call.** It is my reading of the fence's own wording, not an operator ruling. Needs a human-verify checkpoint. |
| A5 | The 16 snapshot regeneration produces exactly one added line per file and nothing else. | §8 | Low — mechanically checkable by `git diff` before commit. Stated so a plan verifies rather than assumes. |
| A6 | Neither triage skill breaks on an added `transport_health` key. | Pitfall 10 | Low — both parsers match `schema_version` by presence only (a live fixture carries `"9.9-future"`). Cheap to confirm; the plan should confirm rather than assume. |
| A7 | A single `dev test` run makes ~13–32 connects depending on chip. | §9 | Low — sourced from `.planning/notes/dev-test-sequence-cost-model.md` (13 predicted / 13 observed, structurally derived) and `REQUIREMENTS.md:122` (32 for at28c256), but both are the *model*, re-measurable during MEAS-01. |

---

## Open Questions

1. **How does the phase get past the ring fence?**
   - Known: the pin is real, green, and mechanically enforced; a re-pin precedent exists (Phase 65-01,
     recorded in the test's own docstring); the v1.9 RCA it defers to has been paused since
     2026-06-01 and v1.10 already re-baselined against different chips.
   - Unclear: whether the operator regards the fence as spent. Nobody has ruled on it.
   - **Recommendation:** §7 option 1 (deliberate re-pin, reasoning recorded), gated behind an
     explicit `checkpoint:human-verify`. Do **not** let `--auto`/`--chain` auto-approve it.

2. **What is the counter's measurement window — the whole `dev test` command, or `run_plan` only?**
   - Known: the identity read (`cli_handlers.py:2379`) happens *before* the report is built and
     costs its own connect.
   - Unclear: which the operator wants the number to mean.
   - **Recommendation:** reset before the identity read (whole-command scope), and say so in the
     field's documentation. It is the number a triager reading a filed issue will assume.

3. **Does `timeouts` count probe failures, or only established-connection timeouts?**
   - This is MEAS-02's real content (§9). **Recommendation:** exclude probe failures, which lets
     `_SUSPECT_THRESHOLD = 5` stand on a recorded argument — a legitimate MEAS-02 outcome — and
     record probe-timeout counts separately during the MEAS-01 bench run as the corroborating
     evidence.

4. **Is `crc_failures` wired via route (b), or left `NOT_MEASURED`?**
   - **Recommendation:** left `NOT_MEASURED` with the reason recorded; a single Site-C counter named
     `decode_failures` satisfies RPT-C1 without pretending to a precision it does not have.

5. **When can MEAS-01 run?** No board is attached. This needs an operator action and has lead time
   (the ROADMAP already says so). It does **not** block the other four requirements.

---

## Sources

### Primary (HIGH confidence) — read this session, quoted verbatim
- `firestarter_app/firestarter/serial_comm.py` — lines 1-100, 100-220, 320-610, 640-760, 796-1040, 1040-1136
- `firestarter_app/firestarter/diagnostic_report.py` — lines 1-150, 160-240, 300-370, 540-620
- `firestarter_app/firestarter/cli_handlers.py` — lines 2194-2218, 2355-2415
- `firestarter_app/firestarter/eprom_operations.py` — lines 373-553, 1510-1560, 1600-1625, 2196-2230
- `firestarter_app/firestarter/codec.py:171-231`; `firestarter/exceptions.py:1-110`; `firestarter/messages.py:248-260, 636-648`
- `firestarter_app/tests/conftest.py:100-245`; `tests/test_serial_comm.py:420-465`; `tests/test_serial_characterization.py:100-160`; `tests/test_diagnostic_report.py:540-565`
- `firestarter_app/tests/test_blast_radius_invariance.py:1-160, 420-470`; `tests/fixtures/rekey_ledger.py:1-80`; `tests/fixtures/reports/gh20-at28c256-fail.json`
- `firestarter_app/tools/snapshot_report_shapes.py:1-50`; `tools/check_devtest_orchestrator.py:140-166`; `tools/check_mypy_watermark.py`
- `firestarter_app/pyproject.toml:105-235`; `firestarter_app/.github/workflows/ci.yml`
- `/workspaces/tools/rekey/check_rekey_ledger.py:1-45`
- Live runs in `.venv311` this session: ring-fence pin + blast-radius module (**89 passed**); the four transport/report modules (**155 passed in 0.78 s**)
- Environment probes this session: `ls /dev/ttyACM* /dev/ttyUSB*` (none), `python3 --version` (3.12.14), `.venv311/bin/python --version` (3.11.16), `id` (dialout present)

### Secondary (MEDIUM confidence) — project planning documents
- `.planning/REQUIREMENTS.md` §Decisions, §Report Fidelity, §Measurement, §Hygiene, §Future Requirements, §Out of Scope
- `.planning/ROADMAP.md:235, 300-340, 411-415, 5283-5284` and `:11-15` (v1.9 pause)
- `.planning/STATE.md` frontmatter + `:265-300`
- `.planning/notes/dev-test-sequence-cost-model.md` (the connect model and its stated gaps)
- `.planning/phases/174-blast-radius-invariance-harness/` — `174-CONTEXT.md:102-108` (D-07), `174-VERIFICATION.md:93`, `174-PATTERNS.md`
- `.planning/phases/175-structural-sentinel-over-derive-plan/175-VERIFICATION.md:93-100`
- `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-MEASUREMENT.md` (artifact precedent)
- `.planning/MILESTONES.md:1375, 1387` (v1.10 transport exoneration and re-baseline; GATE-1.8d history)

### Tertiary (LOW confidence)
- The Uno DTR-auto-reset / optiboot-wait and Leonardo native-USB-CDC mechanisms (A1, A2) are training
  knowledge. **No in-repo measurement of either exists**, which is precisely why MEAS-01 was written.
  They are stated as hypotheses to be tested, never as findings.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| The four instrumentation sites | **HIGH** | All four read at HEAD, quoted verbatim, line numbers independently confirmed against REQUIREMENTS.md and the stale ROADMAP copy identified. |
| Counter lifetime requirement | **HIGH** | `_disconnect_programmer` and the `cli_handlers.py` construction order both read directly. |
| `transport_health` / `_is_transport_suspect` shape | **HIGH** | Read and quoted in full; the "unchanged" rule decomposed into four assertable propositions. |
| MEAS-03 reachability trace | **HIGH** | `cobs_decode` call sites enumerated tree-wide; `retries` traced to two firmware message ids and one unrelated CLI key; `timeouts` traced through `expect_ack` → `_probe_port`'s exception clause with the subclass relationship confirmed in `exceptions.py`. |
| Test approach | **HIGH** | Existing fixtures read; the timeout leg already exists; baseline measured (155 passed). |
| Phase 174 oracle interaction | **HIGH** | Pin, snapshots, tool exit codes and the ledger's ownership all read; `dedup_fingerprint`'s full input construction quoted, proving no `transport` read. |
| Ring-fence resolution | **MEDIUM** | The fence, the pin and the 65-01 precedent are all verified facts; whether a counter increment is in-scope for the fence is a judgement (A4) that needs an operator ruling. |
| MEAS-01 bench specifics | **LOW** | No board attached; the Uno/Leonardo dominant-term hypotheses (A1, A2) are training knowledge, not measurement. The *structural* 2.5 s floor and the definition of a connect are HIGH. |

**Reading method note (for auditability):** under this session's auto-mode directive, source files
were opened with a mixture of the `Read` tool and `sed -n`/`cat` through Bash. Both print the file's
actual bytes; every `[VERIFIED: path:lines]` tag above is accompanied by a verbatim quote so the
citation is checkable rather than merely precise-looking.

**Research date:** 2026-09-04
**Valid until:** 2026-10-04 for the structural findings (the app is on a milestone branch with only
test-only commits since 174/175). **Immediately invalidated** by any commit touching
`serial_comm.py`, `diagnostic_report.py:100-135`, `diagnostic_report.py:600-620`, or
`tests/test_blast_radius_invariance.py:144-150` — re-verify the line numbers and the pinned SHA
before planning if any of those have moved.
