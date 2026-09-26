# Phase 176: Transport Instrumentation + Connect-Cost Measurement — Pattern Map

**Mapped:** 2026-09-04
**Files analyzed:** 10 (1 new module, 4 modified production, 4 modified test/fixture, 1 new `.planning` artifact)
**Analogs found:** 10 / 10 (7 exact, 3 role-match)

All paths below are relative to `/workspaces/firestarter_app/` unless prefixed with `.planning/`.
Every analog named here was confirmed git-TRACKED inside the `firestarter_app` submodule with
`git ls-files --` this session. No path is a gitignored mirror. The stale `build/lib/firestarter/`
copy is deliberately excluded (RESEARCH Pitfall 8).

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/transport_counters.py` **(NEW)** | utility (process-lifetime sink) | event-driven (write-only from transport) | `firestarter/channel.py` (leaf-module shape) + `firestarter/config.py::ConfigManager` (process-lifetime survival) | role-match |
| `firestarter/serial_comm.py` | service (transport) | streaming / byte-loop | itself — `_decode_id_frame` seam at `:327-405` is the in-file precedent for "touch the override, not the fence" | exact |
| `firestarter/cli_handlers.py` | controller (orchestrator) | request-response | `cli_handlers.py:2379-2392` (`read_programmer_identity` → `AutoCapture`) and `_make_sampler` at `:2194-2218` | exact |
| `firestarter/diagnostic_report.py` | model (serialisation + policy) | transform | `TransportHealth` / `_transport_dict` / `_is_transport_suspect` — extend in place | exact |
| `firestarter/eprom_operations.py` (new `measure_connect_cost`) | service (bench harness) | batch measurement | `EpromOperator.measure_command_nak_latency` at `:1517` + `_write_nak_latency_log` at `:1634` | exact |
| `firestarter/cli_handlers.py` (bench subcommand, IF added) | controller | request-response | `dev_fault_inject` at `:1562-1626` | exact |
| `tests/test_serial_comm.py` (SHA re-pin + counter tests) | test | — | `test_read_and_parse_lines_ringfence_unchanged` at `:430-460`; seam tests at `:464+`, `:336-367` | exact |
| `tests/test_diagnostic_report.py` | test | — | `test_transport_not_measured` at `:550-561` | exact |
| `tests/test_blast_radius_invariance.py` | test (pin) | — | `_AUTO_CAPTURE_KEYS` + `test_to_dict_auto_capture_key_list_is_pinned` at `:430-441` | exact |
| `.planning/phases/176-.../176-MEASUREMENT.md` **(NEW)** | doc (bench artifact) | — | `.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-MEASUREMENT.md` | exact |

`tests/fixtures/reports/*.json` (16 files) are **regenerated, never edited** — see Shared Pattern D.

---

## Pattern Assignments

### `firestarter/transport_counters.py` (NEW — utility, event-driven)

**The key analog question, answered.** There is **no module-level mutable sink anywhere in this
package today** — `/usr/bin/grep -rn "^ *global " firestarter/*.py` returns **zero hits**. So this
file has no exact analog and must be assembled from two:

**Analog 1 — what already survives `EpromOperator.comm = None` AND is already written to from
inside the transport:** `ConfigManager`, a class-attribute-keyed singleton
(`firestarter/config.py:84-97`):

```python
    _instances: dict[
        str, "ConfigManager"
    ] = {}  # Stores instances, keyed by config file path
    _initialized_configs: dict[
        str, bool
    ] = {}

    def __new__(cls, config_filename: Optional[str] = None, *args, **kwargs):
        actual_filename = config_filename or CONFIG_FILE_DEFAULT
        instance_key = os.path.join(HOME_PATH, actual_filename)

        if instance_key not in cls._instances:
            cls._instances[instance_key] = super(ConfigManager, cls).__new__(cls)  # noqa: UP008
        return cls._instances[instance_key]
```

The proof it is the right analog is the single call site inside the transport
(`firestarter/serial_comm.py:913`):

```python
            config_manager.remember_port(port_name)  # never promotes a typed --port
```

`_probe_port` writes into a process-lifetime object from deep inside the connect path, and that
write outlives every `SerialCommunicator`. That is exactly the lifetime the counters need
(RESEARCH §2). **Copy the lifetime, not the persistence** — `ConfigManager` writes to disk; the
counter sink must not.

**Analog 2 — leaf-module shape, imports and docstring discipline:** `firestarter/channel.py:1-38`
and `firestarter/sdp_capability.py:1-30`. Both are small, dependency-light modules whose module
docstring carries the whole rationale (no `#` comments needed) and whose import purity is stated
explicitly:

```python
from __future__ import annotations

import logging
import os

logger = logging.getLogger("Channel")
```

and, from `sdp_capability.py:19-24` — the import-purity note pattern to imitate (as a **docstring**
sentence in the new file, not a comment):

> `Import purity: the module's top-level import set is a subset of {"__future__", "typing"} — no click, no serial, no firestarter.* imports.`

For `transport_counters.py` the equivalent invariant is: **imports nothing from
`firestarter.serial_comm` and nothing from `firestarter.diagnostic_report`** — that is what keeps
the import graph acyclic and the orchestrator-only contract intact.

**Suggested shape (comments-free, per the hard project rule; mypy-annotatable):**

```python
def record_response_timeout() -> None:
    ...


def reset() -> None:
    ...


def snapshot() -> dict[str, int]:
    ...
```

**Anti-pattern explicitly rejected by the codebase's own words** — do NOT copy
`serial_comm.py:179-185`:

```python
        # Bounded record of every id frame
        # successfully decoded on this connection. ...
        # Per-connection instance state, not shared across connections.
        self.seen_message_ids: set[int] = set()
```

That comment names the exact property (per-connection) that disqualifies it here.

---

### `firestarter/serial_comm.py` (service, streaming)

**Analog: the file's own `_decode_id_frame` override seam, `:327-352`.** It is the established
in-file pattern for adding behaviour without touching the ring-fenced generator, and it says so in
its own docstring — verbatim (`:346-349`):

```python
        The ring-fenced _read_and_parse_lines body is not touched; only this
        override seam is used.
        """
        result = codec.decode_id_frame(frame_len, body)
```

Site C's increment goes immediately after that `result = ...` line. Every CAP-01/02/03 field was
added at this same seam — copy that precedent verbatim in the plan's justification.

**Sites A and B, current code (ring-fenced), `:485-490` and `:500-505`:**

```python
                if len(len_bytes) < 2:
                    logger.warning(
                        "Magic preamble seen but length bytes not received "
                        "before timeout — re-syncing."
                    )
                    continue
```

```python
                if len(body) != frame_len:
                    logger.warning(
                        f"Frame body truncated: expected {frame_len} bytes, "
                        f"got {len(body)} — re-syncing."
                    )
                    continue
```

**Type-annotation pattern (mypy strict island):** every new helper in this file needs a full
signature; the file's existing style for a transport method is `def _decode_id_frame(self,
frame_len: int, body: bytes) -> Optional[LogMessage]:` — note `Optional[...]`, not `X | None`, in
this module.

---

### `firestarter/cli_handlers.py` (controller, request-response)

**Analog: the identity-threading block at `:2369-2392`** — the same "threaded IN, never fetched"
family the counts join. Verbatim, the construction site:

```python
    identity = app.hardware_manager.read_programmer_identity()
    auto_capture = AutoCapture(
        host_version=version,
        fw_board_identity=identity.fw_board_identity,
        hw_revision=identity.hw_revision,
        chip=chip,
        protocol=None,
    )
    transport = TransportHealth()
    report = DiagnosticReport(
        auto_capture=auto_capture,
        transport=transport,
        plan=plan,
    )
```

**Analog for the post-`run_plan` write-back — the assign-in-handler seam, `:2404-2418`:**

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
    report.banner = count_applicable(plan, results)
```

`report.transport = TransportHealth(...)` is the next line in exactly that family. The seam is
already named in this file's own prose: *"the derive-in-engine / assign-in-handler seam ... this
line only ASSIGNS it, matching every other derived field above and below (never computed
inline here)."*

**Analog for "an object that outlives the torn-down connection and writes into the report":**
`_make_sampler` at `:2194-2218` — a closure over `report` that `run_plan` calls back:

```python
    def _sampler(phase: str) -> None:
        vpp = app.hardware_manager.sample_vpp_mv()
        vpe = app.hardware_manager.sample_vpe_mv()
        if phase == "before":
            report.vpp_before_mv = vpp
            report.vpe_before_mv = vpe
        elif phase == "after":
            report.vpp_after_mv = vpp
            report.vpe_after_mv = vpe

    return _sampler
```

This is the *closest live precedent* for late-mutating `report` with values that could not exist at
construction time. A planner choosing between "mutate `report.transport` in place" and "re-assign"
should note this file already does both (`report.vpp_before_mv = ...` field-mutation via the
sampler; `report.results = ...` assignment), so either is idiomatic.

---

### `firestarter/diagnostic_report.py` (model, transform)

**Analog: the file itself — extend the three existing structures in place.** All three are quoted
verbatim in RESEARCH §3 (`:101-117`, `:605-617`, `:120-132`); do not re-derive them.

**The house additive-siblings rule, verbatim from `:224-236`** — the reasoning a plan must reuse
for "add new keys, never repurpose `retries`":

```python
    # The empty-default direction is the whole point and is deliberate.
    # Slot/fixed runs stay untagged, so every ALREADY-FILED report's
    # fingerprint remains byte-identical and no historical `count_agreeing`
    # group is re-keyed or reset.
```

**The tier contract, verbatim from `:15-18`** — the one rule a plan must not break:

```python
ORCHESTRATOR ONLY: this module imports no transport or hardware class, sets no
VPP, builds no wire dict, passes no force flag and adds no firmware dispatch.
`fw_board_identity` and `hw_revision` are threaded IN as input -- this module
never fetches them and never opens a connection.
```

Extend that sentence rather than replacing it: the transport counts become the third member of the
threaded-in family. Enforced by `test_report_module_is_orchestrator_only`
(`tests/test_diagnostic_report.py:569+`), an **AST scan**, not a grep.

---

### `firestarter/eprom_operations.py::measure_connect_cost` (service, batch measurement)

**Analog: `EpromOperator.measure_command_nak_latency` at `:1517`.** Copy four things:

**1. Port resolution — pin one port, never let discovery inflate the number (`:1543-1550`):**

```python
        if port is None:
            port = self.config.get_value("port")
        if not port:
            logger.error(
                "measure_command_nak_latency: no serial port resolved "
                "(pass -p <port> or set config.port)."
            )
            return False
```

**2. Timestamped output directory (`:1552-1557`):**

```python
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            output_dir = f"fault-inject-latency-{fault_form}-{timestamp}"
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
```

**3. Timing + teardown discipline (`:1585-1613`):**

```python
                _t0 = time.monotonic()
                comm.send_json_command(fw_cmd)
                ...
                nak_latency_s = time.monotonic() - _t0
        except (SerialError, SerialTimeoutError) as e:
            detail = f"{type(e).__name__}: {e}"
            logger.error(f"measure_command_nak_latency: {detail}")
        finally:
            if comm is not None:
                comm.disconnect()
```

Note the file uses `time.monotonic()`, not `perf_counter`, for this exact measurement — and
`time.time()` everywhere else. **Follow the local precedent (`time.monotonic()`) unless the plan
records a reason;** RESEARCH's `perf_counter` suggestion is correct in principle but is not what the
one existing latency harness does, and consistency inside the file is worth more here.

**4. The artifact writer — a `@staticmethod _write_*_log` with a banded verdict (`:1634-1665`):**

```python
    @staticmethod
    def _write_nak_latency_log(
        output_path: Path,
        fault_form: str,
        port: str,
        ...
        nak_latency_s: Optional[float],
        detail: str,
    ) -> None:
        """Write the per-frame NAK latency log (53-04 harness refinement)."""
        log_path = output_path / f"fault-inject-{fault_form}-latency.txt"
        latency_str = (
            f"{nak_latency_s:.3f}s" if nak_latency_s is not None else "unmeasured"
        )
        if nak_latency_s is None:
            verdict = "UNKNOWN"
        elif nak_latency_s < 1.0:
            verdict = "SUB-SECOND (fast-fail)"
```

The `"unmeasured"` string when the value is `None` is the same honesty discipline as
`NOT_MEASURED` — reuse the shape.

**Note:** `eprom_operations.py` is **excluded** from mypy strict (GATE-1.8d), so a method here does
not carry the annotation burden `serial_comm.py` does. It is also **not** a `dev_test` handler, so
`tools/check_devtest_orchestrator.py:152-165`'s `_HANDLER_FUNCTION_NAMES` is **not** triggered by
this route (HYG-04 satisfied by construction).

---

### `firestarter/cli_handlers.py` bench subcommand (IF one is added)

**Analog: `dev_fault_inject` at `:1562-1626`.** Copy the whole decorator stack and the
`sys.exit(0 if ok else 1)` tail:

```python
    @dev.command(name="fault-inject")
    @click.argument("eprom", shell_complete=_complete_eprom)
    @click.option(
        "--mode",
        type=click.Choice(["cycle", "latency"]),
        default="cycle",
        help="cycle = read-cycle resync demo (default); latency = per-frame firmware NAK "
        "latency on an established single-port connection (53-04 refinement; no chip needed).",
    )
    @click.pass_obj
    @map_typed_errors
    def dev_fault_inject(
        app: AppContext,
        ...
    ) -> None:
        """Demonstrate COBS resync: inject a corrupted frame and assert recovery on the next.
        ...
        """
        if mode == "latency":
            ok = app.eprom_operator.measure_command_nak_latency(
                fault_form=fault_form,
                output_dir=output_dir,
            )
            sys.exit(0 if ok else 1)
```

Three load-bearing details: the block sits **inside the `if _DEV_TOOLS_ENABLED:` gate**
(`:1553`-ish and again at `:1636`), `@click.pass_obj` + `@map_typed_errors` are both required, and
**the Click docstring is user-facing `--help` text** — it is not a comment and is not covered by the
no-comments rule. Prefer extending `dev fault-inject` with a new `--mode` value over adding a new
subcommand: the channel-gate tables in `channel.py:39-46` count subcommands explicitly, so a new
one has a second registration site.

---

### `tests/test_serial_comm.py` (test)

**Analog A — the ring-fence pin's re-pin ritual, `:430-460`.** The docstring is where the
justification lives; the Phase 65-01 paragraph inside it is the literal template for the Phase 176
paragraph:

```
    Pinned SHA-256 (2026-06-11): 6d9e4fe4b67b78c110418305113b275174f16b2ecc9e0f55fbf5d9a623398184
    (Updated from 544433068cb14ac14677939435cb4f0ea78783b503315ed645b5f88c5c44a444
     at Phase 65-01: Response now carries id=decoded.id for ProtocolNotImplementedError
     typed-raise dispatch. Change is in-scope for v1.12 host graceful handling — not
     a transport-path change, only adds id plumbing to the Response construction.)
```

and the assertion message to leave intact (`:455-460`):

```python
        f"GATE-1.8d VIOLATION: _read_and_parse_lines body has changed!\n"
        f"  Pinned digest:  {_PINNED_SHA256}\n"
        f"  Actual digest:  {actual_digest}\n"
        "Any change to this generator body must be flagged and deferred to v1.9 "
        "per the ring-fence protocol (see serial_comm.py header comment)."
```

**Analog B — driving `_decode_id_frame` directly with a hand-built body, `:473-499`.** This is the
cheapest Site-C trigger and the file already does it:

```python
    from firestarter.frame_parser import _crc8_ccitt
    from firestarter.messages import MSG_OK_READY

    params = b"\x02\x00"
    msg_id_byte = bytes([MSG_OK_READY])
    crc = _crc8_ccitt(msg_id_byte + params)
    body = msg_id_byte + params + bytes([crc])
    frame_len = len(body)

    result = comm._decode_id_frame(frame_len, body)
```

XOR the final CRC byte by 1 to flip this into the `result is None` path.

---

### `tests/test_diagnostic_report.py` (test)

**Analog: `test_transport_not_measured` at `:550-561`** — the exact shape any new-field assertion
must extend, including the `!= 0` line that is the whole point:

```python
def test_transport_not_measured():
    from firestarter.diagnostic_report import NOT_MEASURED

    report = _build_report()
    d = report.to_dict()

    transport = d["transport_health"]
    for key in ("cobs_errors", "crc_failures", "retries", "timeouts"):
        assert transport[key] == NOT_MEASURED
        assert transport[key] != 0

    assert transport["transport_suspect"] is False
```

Add new key names to that tuple in the same commit as the dataclass fields.

---

### `tests/test_blast_radius_invariance.py` (test — pin)

**Analog: `_AUTO_CAPTURE_KEYS` and its test at `:430-441`** — it already models the
"update deliberately in the same commit" assertion message the transport pin should gain:

```python
def test_to_dict_auto_capture_key_list_is_pinned() -> None:
    d = build_shape(_TRACER_SHAPE_ID).to_dict()
    keys = sorted(d["auto_capture"])
    assert keys == _AUTO_CAPTURE_KEYS, (
        f"to_dict()['auto_capture'] keys drifted from the pinned D-07 shape; "
        f"expected {_AUTO_CAPTURE_KEYS}, got {keys}"
    )
    assert "canonical_part_number" not in keys, (
        "auto_capture gained canonical_part_number -- RPT-F1 landed; "
        "update _AUTO_CAPTURE_KEYS deliberately in the same commit"
    )
```

The pin to move (`:144-150`) and its own test (`:443-449`) are quoted in RESEARCH §8. Note the
comparison is `sorted(...)` element-wise, so new keys must be inserted in **sorted** position in
`_TRANSPORT_HEALTH_KEYS`.

---

### `.planning/phases/176-.../176-MEASUREMENT.md` (NEW — doc)

**Analog:**
`/workspaces/.planning/phases/118-observe-auto-unlock-visible-opt-out-able-fw-half/118-MEASUREMENT.md`
(git-tracked in the meta repo). Its full section order, read this session:

```
# Phase 118 Plan 07 — OBS-04 Leonardo SDP Emit Duration Measurement
**Written:** 2026-07-28 (Plan 118-07)
**Firmware build uploaded:** `firestarter` HEAD `1880054` on branch `...`
## 1. What was measured, and what it is not
## 2. Provenance block
## 3. Raw captured log
## 4. The number
## 5. Socket state, stated plainly
## 6. Validation ceiling
## 7. Downstream consumers
## Disposition
```

**§1's opening sentence is the load-bearing pattern** — verbatim:

> `**The subject of this measurement is the emitter, never the chip.**`

176's equivalent: *the subject is the host's connect sequence and the board's reset/enumeration
behaviour, never the chip* — and §5 ("Socket state, stated plainly") becomes trivially satisfiable
because the socket is empty for every connect-cost run.

**§2's provenance discipline is mandatory** (standing project rule: `ttyACM*` numbers shuffle).
Verbatim shape to copy:

```
$ firestarter -p /dev/ttyACM0 -v fw
INFO   :Firmware     : 122: Current firmware version: 3.0.0b13, for controller: leonardo on port /dev/ttyACM0
```

followed by an explicit sentence naming which port was selected **and which were not driven
further**, plus:

```
$ cd /workspaces/firestarter && git status --short
(clean — no output)
$ git rev-parse --short HEAD
1880054
```

For 176 the build identity is `firestarter_app` HEAD, not firmware HEAD. **Two board classes → two
clearly separated sections, with an explicit "these are never blended" sentence** (success
criterion 3).

---

## Shared Patterns

### A. No comments in source — docstrings only
**Source:** operator hard rule; visible throughout `channel.py`, `sdp_capability.py`,
`snapshot_report_shapes.py`, all of which carry long module docstrings and zero explanatory `#`.
**Apply to:** every production line this phase adds.
**Caveat, twice-load-bearing:** Click command docstrings (`dev_fault_inject:1603-1610`) are
user-facing `--help` text and MUST be written; test docstrings are where a re-pin's justification
lives and MUST be written. Only `#` comments are forbidden. Note the existing source is full of
comments the operator did not write — do not "clean up" neighbouring lines.

### B. Threaded in, never fetched
**Source:** `firestarter/diagnostic_report.py:15-18` (module docstring, quoted above).
**Apply to:** the `cli_handlers.py` read and the `diagnostic_report.py` change.
**Enforced by:** `test_report_module_is_orchestrator_only` (AST scan, not grep) —
`tests/test_diagnostic_report.py:569+`.

### C. The fake serial, never a Mock
**Source:** `tests/conftest.py:140-238`.
**Apply to:** all four counter tests.
`_FakeSerial.read` (`:157-161`) is why a `Mock` cannot substitute — it reproduces pyserial's
`b""`-on-timeout semantics, which is the branch `_read_and_parse_lines` keys on:

```python
    def read(self, n: int = 1) -> bytes:
        self._buf.seek(self._read_pos)
        data = self._buf.read(n)
        self._read_pos = self._buf.tell()
        return data
```

and the test-side injector (`:186-191`):

```python
    def feed(self, data: bytes) -> None:
        """Append bytes to the readable buffer (test-side injection)."""
        self._buf.seek(self._write_pos)
        self._buf.write(data)
        self._write_pos = self._buf.tell()
```

**Forcing each path, concretely:**
- Site A: `fake_serial.feed(MAGIC_PREAMBLE_REF)` and nothing else, then
  `list(comm._read_and_parse_lines(0.05))` — `read(2)` returns `b""`.
- Site B: `fake_serial.feed(MAGIC_PREAMBLE_REF + struct.pack(">H", 8) + b"\x01\x02")`.
- Site C: `comm._decode_id_frame(len(body), body)` with the CRC byte XOR'd — pattern from
  `tests/test_serial_comm.py:473-499`.
- Site D: `comm.get_response(timeout=0.02)` with nothing fed —
  `tests/test_serial_characterization.py:105-123`.

**`make_comm` bypasses `__init__` via `__new__`** and hand-mirrors eleven attributes
(`tests/conftest.py:211-236`). A module-level sink needs **zero** additions there; a per-instance
counter needs one per counter, plus every other test that constructs a communicator by `__new__`
(e.g. `test_fault_inject_incoming_subclass` at `:336-367`, which already has to hand-set
`comm.seen_message_ids = set()` for exactly this reason). That asymmetry is the strongest
mechanical argument for the module sink.

**Never monkeypatch `time.time`** — named an anti-pattern by
`test_timeout_raises_on_empty`'s own docstring. Use the tiny-real-clock 20 ms technique.

**Never hand-pack a frame** — use `conftest.build_frame(msg_id, params)` (`:127-137`), which uses a
table-free reference CRC8 so a test cannot pass tautologically on a production-table bug.

### D. Report snapshots are regenerated, never edited
**Source:** `tools/snapshot_report_shapes.py:1-28` (module docstring).
**Apply to:** the 16 `tests/fixtures/reports/*.json` files, in the same commit as the key addition.

```
Exit codes:
  0 -- wrote every target (or, under --check, every target already matched
       a fresh regeneration)
  1 -- --check found drift, or a --check target does not exist
  2 -- a --shape value is not in tests.fixtures.report_shapes.SHAPE_IDS
```

Procedure: `./.venv311/bin/python tools/snapshot_report_shapes.py`, then
`... --check` to prove zero drift, then `git diff --stat` to confirm 16 files × one added line.
`_generated_by` is the do-not-edit banner and is asserted absolutely by a live test.

### E. Python 3.11, and `-o addopts=""`
**Source:** `pyproject.toml:105-107` (`addopts = "-ra -q"`), CI pins 3.11.
**Apply to:** every verification command in every plan:
`./.venv311/bin/python -m pytest <files> -o addopts="" -q`.
A bare `-q` doubles and suppresses the `N passed` line, making a verification leg vacuous.

### F. Anti-vacuity transcripts
**Source:** `.planning/phases/174-blast-radius-invariance-harness/174-PATTERNS.md`
§"Anti-vacuity (applies to EVERY new test file)"; both 174 and 175 VERIFICATIONs cite transcripts
by name.
**Apply to:** every counter test — weaken the increment, observe RED, transcribe to
`evidence/176-NN-*.txt`.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `firestarter/transport_counters.py` (module-level mutable sink specifically) | utility | event-driven | **No module-level mutable state exists in this package.** Zero `global` statements across all 31 modules (`/usr/bin/grep -rn "^ *global " firestarter/*.py`). The two analogs above supply *lifetime* (`ConfigManager` class-attribute singleton) and *file shape* (`channel.py`) separately; the combination is new. A planner choosing the class-attribute form over module-level functions has a **real in-tree precedent** (`ConfigManager._instances`) and should note that RESEARCH's "Alternatives considered" table argues against a `ClassVar` on `SerialCommunicator` specifically — not against a `ClassVar` on a dedicated new class. |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tests/`,
`firestarter_app/tools/`, `.planning/phases/*/`
**Files scanned:** 31 production modules listed, 8 read in full or in targeted ranges, 5 test
modules, 2 tools, 1 `.planning` artifact
**Tracked-source check:** `git ls-files --` run inside `firestarter_app` for all 11 named source
analogs — all tracked, none a mirror. `build/lib/firestarter/` excluded by name.
**Pattern extraction date:** 2026-09-04
