# Phase 202: One comparison engine, on the host - Research

**Researched:** 2026-09-20
**Domain:** Python host CLI — streaming byte comparison, pytest harness design, memory-bound assertions
**Confidence:** HIGH (every load-bearing claim is a file read or a command run in this session)

## Summary

CONTEXT.md's seventeen decisions are settled and this research does not revisit them. It answers
the four questions the phase description directed budget at, and it changes the shape of two of
them. The headline: **both "hard" harness problems named in CONTEXT.md's `<deferred>` section are
substantially easier than flagged, and a third problem nobody flagged is genuinely hard.**

Criterion 1's wire-level assertion needs no new framework. `tests/test_eprom_operations.py:1196-1216`
already contains the exact idiom — patch `SerialCommunicator.find_and_connect`, capture the composed
`command_dict`, assert on `command_dict["cmd"]` — and a companion helper `_capture_written_frames`
at `:1164-1179` records every byte the host writes. Criterion 2's memory bound is a stdlib
`tracemalloc` measurement with no precedent in either sub-repo but a measured **5000x separation**
between the streaming and materialised shapes, which makes any threshold in the 64 KiB–1 MiB band
unflakeable. Both were measured, not reasoned about.

The unflagged problem is **runtime, not memory**. A naive per-byte Python accumulator over 512 KB
takes **19.8 s** — measured — which is unacceptable in a 174 s suite and worse in production. The
fix is structural and must reach the plan: a C-level `exp == payload` fast path per chunk makes a
clean 512 KB verify cost **0.002 s**, and a *per-chunk* (not per-device) offset list brings the
pathological case to 1.9 s. D-02 forbids a device-sized offset list; it does not forbid a
chunk-sized one, and the distinction is worth ~11x.

**Primary recommendation:** build the accumulator around a three-tier per-chunk path — `payload.count(0xFF)`
for the blank ratio, `exp == payload` memcmp to skip matching chunks entirely, and a bounded
per-chunk offset list only for chunks that differ. Prove criterion 1 with the existing
`find_and_connect` capture idiom, criterion 2 with `tracemalloc.get_traced_memory()` and a 1 MiB
ceiling, and D-03 with a parametrised corpus comparing whole `Fingerprint` objects by `==`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Streaming compare + fingerprint accumulation | Host library (`firestarter/compare.py`, new) | — | D-01 locks this; import-light, no `serial_comm`/`database` pull |
| Chip byte delivery, per-chunk ack | Host service (`eprom_operations._main_phase_read_data`) | Firmware (`CMD_READ`) | Existing, reused; firmware unchanged this phase |
| Abort in flight (stop acking) | Host service (`_main_phase_read_data` loop) | Firmware (`op_wait_for_ack` 1 s timeout) | D-06; the *decision* to stop is the engine's, the *mechanism* is the read loop's |
| Region resolution + conflict refusal | Host CLI (`cli_handlers`) | Host service (`_setup_operation`) | D-17 requires refusal **before the port opens** — CLI tier |
| Exit-code mapping (0/1/2) | Host CLI (`cli_handlers.verify` / `.blank`) | — | D-10/D-11 scope it to two commands; `map_typed_errors` stays untouched |
| Report rendering | Host CLI | — | D-05 separates "compare → structured result" from "render" |

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md`, both read this session:

- **Milestone work forks off `beta`; never commit to `beta` or `main`.** Current branch is
  `v1.41-verification-to-host`. [VERIFIED: /workspaces/CLAUDE.md § "Milestone close and branch protection"]
- **A push to `beta` in `firestarter_app` publishes to PyPI**, with no path filter, and a PyPI
  version can never be reused. [VERIFIED: firestarter_app/CLAUDE.md:32-37]
- **CI runs Python 3.11; the devcontainer runs later.** `firestarter_app/CLAUDE.md:15-17` states
  verbatim: *"A later interpreter turns some snapshot failures into collection errors, so a green
  local run does not prove a green CI run. Run the suite on 3.11 before you trust it."*
  [VERIFIED: firestarter_app/CLAUDE.md:15-17]
- **Comments in product source are allowed again** (rule removed 2026-09-19). D-02, D-08 and D-12
  each carry reasoning that belongs at its site. [VERIFIED: /workspaces/CLAUDE.md]
- **`tools/` is outside every CI gate** — no ruff, no mypy, no coverage. Anything the phase needs
  gated must live under `firestarter/` or `tests/`. [VERIFIED: firestarter_app/CLAUDE.md:42-44]
- **Messages are generated only in the meta repo.** Not touched by this phase, but `MSG_ERR_TIMEOUT`
  is consumed from the synced `firestarter/messages.py` — never hand-edit it.
  [VERIFIED: /workspaces/CLAUDE.md § Cross-repo obligations]

No project skills directory exists under `firestarter_app/`. `/workspaces/.claude/skills/` and
`/workspaces/.agents/skills/` exist but carry no rules binding this phase.

---

# Question 1 — Wire-level "ordinal never sent" assertion (criterion 1, CMP-01/CMP-02)

**Finding: the harness exists. No new framework is needed. Two complementary seams, both in use today.**

## Seam A — command-dict capture (the right one for criterion 1)

Every chip operation composes its command dict in `_setup_operation` and hands it to
`SerialCommunicator.find_and_connect`. The ordinal is a plain dict key:

```python
# firestarter/eprom_operations.py:471-473  (read this session)
command_dict = eprom_data_dict.copy()  # Work with a copy for the command
command_dict["cmd"] = cmd
command_dict["flags"] = eprom_data_dict.get("flags", 0) | operation_flags
```

```python
# firestarter/eprom_operations.py:521-525
self.comm = SerialCommunicator.find_and_connect(
    command_dict,
    self.config,
    fault_inject_outgoing=fault_inject_outgoing,
)
```
[VERIFIED: firestarter_app/firestarter/eprom_operations.py:457-525]

The existing test idiom patches that classmethod and captures the dict. Verbatim, from
`tests/test_eprom_operations.py:1196-1216`:

```python
captured: dict = {}

def _fake_find_and_connect(command_dict, config, **kwargs):
    captured["command_dict"] = command_dict
    return make_comm()

fake_serial.feed(build_frame(MSG_INIT_DONE, b""))
fake_serial.feed(build_frame(MSG_MAIN_DONE, b""))
fake_serial.feed(build_frame(MSG_END_DONE, b""))
written = _capture_written_frames(fake_serial)

operator = EpromOperator(ConfigManager())
with patch(
    "firestarter.serial_comm.SerialCommunicator.find_and_connect",
    side_effect=_fake_find_and_connect,
):
    ok = operator.sdp_unlock("at28c256", _at28c256_programmer_dict())

assert ok is True
assert captured["command_dict"]["cmd"] == 9
```
[VERIFIED: firestarter_app/tests/test_eprom_operations.py:1196-1216]

This pattern is used at five sites in that file (`:404-421`, `:435-452`, `:469-486`, `:1198-1215`,
`:1226-1243`, `:1308-1354`, `:1394-…`). **For criterion 1 the assertion inverts trivially:**

```python
assert captured["command_dict"]["cmd"] == COMMAND_READ          # == 1
assert captured["command_dict"]["cmd"] not in (COMMAND_VERIFY, COMMAND_BLANK_CHECK)  # 6, 4
```

Ordinals, read verbatim from `firestarter/constants.py`:

```python
COMMAND_READ = 1            # constants.py:49
COMMAND_BLANK_CHECK = 4     # constants.py:52
COMMAND_VERIFY = 6          # constants.py:54
```
[VERIFIED: firestarter_app/firestarter/constants.py:49-54]

**Strengthening note for the planner.** A capture that only asserts the *final* dict proves one
call. If the plan wants "neither ordinal is sent **at all**", collect into a `list` rather than
overwriting a single key, and assert over the whole list. The `side_effect` callable is invoked
once per `find_and_connect`, so `captured.append(command_dict)` gives a complete call log for the
whole command. This is a one-line change to the existing idiom and closes the gap between "the last
command was READ" and "no command was VERIFY".

## Seam B — byte-level write recorder

`tests/test_eprom_operations.py:1164-1179`, verbatim:

```python
def _capture_written_frames(fake_serial):
    """Wrap fake_serial.write to record every chunk the host writes.

    Returns the list the wrapper appends to; the original write behavior
    (buffering into the BytesIO-backed fake) is preserved so the state
    machine's own send_ack()/get_response() flow is unaffected.
    """
    written: list = []
    original_write = fake_serial.write

    def _wrapped(data: bytes) -> int:
        written.append(bytes(data))
        return original_write(data)

    fake_serial.write = _wrapped
    return written
```
[VERIFIED: firestarter_app/tests/test_eprom_operations.py:1164-1179]

**Important limitation — state it in the plan, do not let a task assume otherwise.** When
`find_and_connect` is patched out (Seam A), the initial command frame is *never written to
`fake_serial`*, because `send_json_command` is called inside the real `find_and_connect`. So Seam B
records **only** the acks and data frames of the MAIN/END phases, not the command. Seam B therefore
cannot by itself prove "ordinal 6 never went on the wire" — Seam A can. Use Seam B for its actual
strength, which the existing tests use it for: asserting the **absence** of `#`-prefixed data frames
and `DONE` round-trips, i.e. proving the *shape* of the exchange.

## The fake serial port

`tests/conftest.py:133-193` defines `_FakeSerial`, a `BytesIO`-backed stand-in, exposed as the
`fake_serial` fixture (`:188-191`) and paired with a `make_comm` factory (`:193-…`) that builds a
`SerialCommunicator` via `__new__`, bypassing `__init__` so no real port is opened. Its docstring,
verbatim:

> Implements only the surface that `SerialCommunicator._read_and_parse_lines` consumes: `read(n)`
> returning up to n bytes (b'' on empty — matches pyserial timeout-empty semantics), `is_open`,
> `in_waiting`, `port`, `timeout`, `write(...)`, `flush()`, and `close()`.

[VERIFIED: firestarter_app/tests/conftest.py:133-193]

`build_frame(msg_id, params)` (`conftest.py:120-131`) assembles wire frames for the test to
`feed()` into the fake — this is how a test scripts the firmware's side of the exchange.
[VERIFIED: firestarter_app/tests/conftest.py:120-131]

## The deeper seam, if a plan wants it

`SerialCommunicator.send_json_command(command_dict)` at `serial_comm.py:241` is where the dict
becomes COBS+CRC8 bytes; `send_bytes` at `:220` is the raw write.
[VERIFIED: firestarter_app/firestarter/serial_comm.py:220-266]
Eight test modules patch `send_json_command` directly
(`test_protocol_not_implemented_production_path.py:176,277,339`, `test_fw_update_path_gate.py:57`,
`test_hw_revision_gate.py:363`, `test_probe_spurious_setup_ack.py:81,111,135`,
`test_fwguard.py:52`). This is the seam to use if a plan wants to assert on the *encoded frame*
rather than the dict — but for CMP-01/CMP-02 the dict assertion is stronger and simpler, because
the ordinal is a first-class value there rather than a byte pattern inside a COBS payload.

**Verdict on CONTEXT.md's `<deferred>` flag:** criterion 1's harness cost is **low**. The idiom,
the fixtures and a worked five-site precedent all exist. What is *new* is only the assertion.

---

# Question 2 — Peak-memory measurement on a 512 KB part (criterion 2, CMP-03)

## Precedent: none

An exhaustive filesystem walk of `firestarter_app/` and `firestarter_fw/` (all `.py`, `.cpp`, `.h`,
`.toml`, `.yml`, `.cfg`, `.ini`, `.md` files, excluding `.git`/`__pycache__`/`node_modules`/`.pio`/`build`)
searching for `tracemalloc|getsizeof|getrusage|peak_memory|memory_profiler|max_rss|psutil` returned
**149 hits, every one of them inside a `.venv*/site-packages/` directory** (pytest's own plugins,
mypy, pygments, packaging). **Zero hits in `firestarter_app/firestarter/`, `firestarter_app/tests/`,
`firestarter_app/tools/`, or anywhere under `firestarter_fw/`.**
[VERIFIED: exhaustive `os.walk` over both sub-repos, output pasted in session, search terms as listed]

This walk was done in Python deliberately: the devcontainer's `grep` is **ugrep 7.8.4**, which
honours `.gitignore` and silently under-scans. A `grep`-only negative here would not have been
trustworthy. [VERIFIED: `grep --version` → `ugrep 7.8.4`; recorded trap in user memory]

`psutil` is **not** a dependency of `firestarter_app` — it appears only inside mypy's stub tables.
So the measurement must use stdlib `tracemalloc`. `pytest` ships a `tracemalloc` plugin
(`_pytest/tracemalloc.py`) but it only supports the `PYTHONTRACEMALLOC`-driven warning machinery;
it offers no assertion API. Use `tracemalloc` directly.

## Measured: the mechanism works, with enormous margin

Run this session on `.venv311/bin/python` (Python 3.11.16), simulating `_main_phase_read_data`
delivering 1024-byte chunks over a 512 KiB device:

```
streaming     peak=    4,231 B  (     4.1 KiB)  t=19.80s
materialised  peak=22,571,672 B  ( 22042.6 KiB)  t= 0.25s
noise floor   peak=       88 B
```

**Separation is ~5,300x.** The materialised shape's 22 MB is dominated by `_diff_offsets`' list of
524,288 Python ints (~28 B each plus list slots) — precisely the object D-02 names as the one thing
that must not survive.

**Noise floor is 88 bytes.** `tracemalloc.get_traced_memory()` traces Python allocations only, not
the interpreter's RSS, so it is immune to GC timing, other tests' residue, and CI machine variance.
A threshold anywhere between 64 KiB and 1 MiB sits 16x above the worst measured streaming peak and
22x below the materialised peak. **This assertion cannot realistically flake.**

Recommended ceiling: **1 MiB (1_048_576)**, stated as a named constant with the measurement in a
comment. It is ~12x the worst measured streaming peak (86 KB, below) and ~21x below the
materialised shape, so it fails loudly on a regression to materialisation and never on noise.

## Measured: the realistic accumulator, including D-16's range cap

A second run modelled the actual shape the phase needs — per-chunk bounded offset list, coalesced
ranges with a cap `N=64`, per-bit counters over only the bits that can vary
(`range(8, (SIZE-1).bit_length())`):

```
all-match (clean verify)         peak=   4,043B t=  0.00s total=524288 bad=0      ranges=0  +extra=0
one bad byte at 0x400 only       peak=   5,099B t=  0.01s total=524288 bad=1      ranges=1  +extra=0
worst: every byte differs        peak=  86,738B t=  2.26s total=524288 bad=524288 ranges=1  +extra=0
alternating (max range count)    peak=  48,074B t=  1.97s total=524288 bad=262144 ranges=64 +extra=262080
```

All four cases are **under 87 KB and flat in device size**. The "alternating" row is exactly D-16's
stated worst case — a 512 KB part producing ~262,144 coalesced ranges — and it retains 64 ranges
while counting 262,080 more from running counters. **D-16's design is measured to work.**

## The unflagged problem: runtime

**A naive per-byte Python loop over 512 KB costs 19.8 s.** Measured. The suite is 2,106 tests in
174.58 s (measured, `.venv311`, `-o addopts=""`), so one such test would add ~11%. Worse, that cost
is paid in *production* on every real 512 KB verify.

Three strategies were benchmarked:

```
clean compare, C-level memcmp fast path          peak=   3,315 B  t= 0.002s
worst case, int-XOR + per-offset bit loop        peak=   7,347 B  t=21.416s
worst case, per-chunk offset list + per-bit sum  peak=  86,430 B  t= 1.890s
```

**This is the single most important design finding in this document.** D-02 forbids "a materialised
list of every mismatching offset" — a *device-sized* list. A **per-chunk** offset list, whose length
is bounded by the chunk size (≤1024) and which is discarded at chunk boundary, is **not** that
object: peak stays at 86 KB and flat, and it is **11x faster** than avoiding lists entirely. Prescribe
it explicitly, or an executor reading D-02 literally will write the 21-second version and it will
pass every memory assertion.

## Does the 512 KB case need real hardware?

**No, and it must not.** The phase is bench-no. `_main_phase_read_data`'s contract is
`process_data_chunk_callback(address, payload)` — a synthetic generator yielding
`(address, bytes)` pairs exercises the accumulator identically. Cost: **~0.0 s for the clean case,
~2.3 s worst case**, versus a real 512 KB read at 250000 baud which would take on the order of
tens of seconds and require a bench board.

Recommended test shape: drive the accumulator directly with a synthetic chunk generator, assert
`tracemalloc` peak < 1 MiB. Keep the *pathological* 2.3 s case to a single test; use the clean and
single-mismatch cases (0.00–0.01 s) for the rest.

**Verdict on CONTEXT.md's `<deferred>` flag:** criterion 2's harness cost is **low** and the
measurement is robust. The *real* work flagged here is the accumulator's inner-loop shape, which
CONTEXT.md did not anticipate.

---

# Question 3 — The D-03 corpus equality test

## `Fingerprint` — exact field list

```python
@dataclass
class Fingerprint:
    """Verdict + raw evidence for a single expected-vs-actual byte compare."""

    total: int
    bad: int
    bad_pct: float
    classification: str
    evidence: dict = field(default_factory=dict)
```
[VERIFIED: firestarter_app/firestarter/chip_test.py:152-160]

`evidence` always carries exactly four keys, verbatim from `chip_test.py:195-200`:

```python
evidence: dict = {
    "ff_ratio": ff_ratio,
    "repeat_divergent": repeat_divergent,
    "first_offset": first_offset,
    "bit_clustering": {},
}
```
plus two more keys set **only** on the address-line path (`chip_test.py:229-230`):
`"suspected_line"` and `"cluster_score"`.
[VERIFIED: firestarter_app/firestarter/chip_test.py:195-231]

`bit_clustering` is a dict keyed by bit index `k`, value = cluster score, populated for
`k in range(8, (cmp_len-1).bit_length())` and only when `bad and cmp_len > (1 << 8)`.
[VERIFIED: firestarter_app/firestarter/chip_test.py:216-227]

## `classify_fingerprint` — exact signature

```python
def classify_fingerprint(
    expected: bytes,
    actual: bytes,
    *,
    repeat_divergent: bool | None = None,
    addr_base: int = 0,
) -> Fingerprint:
```
[VERIFIED: firestarter_app/firestarter/chip_test.py:162-168]

## The rule comment D-02 cites — quoted verbatim

`chip_test.py:105-116`:

```
# ---------------------------------------------------------------------------
# Shared byte-diff-offset helper -- reused, not reimplemented
# ---------------------------------------------------------------------------
#
# Mirrors the exact divergence math in `consistency_check_eprom`
# (eprom_operations.py:842-863): cmp_len / diff_offsets / pct / first
# divergence offset. This is the ONE divergence primitive `classify_fingerprint`
# consumes -- do NOT add a second parallel divergence implementation
# elsewhere in this codebase. The math is small enough to
# copy rather than import, keeping this module import-light (no dependency
# on eprom_operations.py).
```
[VERIFIED: firestarter_app/firestarter/chip_test.py:105-116]

## Bucket ordering — exact, and the code disagrees with its own docstring

The docstring at `chip_test.py:178-187` states the order as: 1 blank/contact, 2 address-line,
3 match, 4 transport, 5 indeterminate. **The executed order in the body is the same**, but note
`match` is checked *after* address-line (`chip_test.py:233`), which is deliberate — the docstring
says so verbatim: *"match -- zero mismatches, checked AFTER buckets 1 and 2 so an all-0xFF perfect
compare stays blank/contact rather than silently re-keying that population."*
[VERIFIED: firestarter_app/firestarter/chip_test.py:178-187, 205-262]

Constants, verbatim from `chip_test.py:139-143`:

```python
FP_BLANK_CONTACT = "blank/contact"
FP_ADDRESS_LINE = "address-line"
FP_TRANSPORT = "transport"
FP_INDETERMINATE = "indeterminate"
FP_MATCH = "match"
```

Thresholds, verbatim from `chip_test.py:148-151`:

```python
_FF_RATIO_THRESHOLD = 0.98  # blank/contact: >= this fraction of actual == 0xFF
_BIT_CLUSTER_THRESHOLD = 0.9  # address-line: >= this fraction of mismatches
```
[VERIFIED: firestarter_app/firestarter/chip_test.py:139-151]

## How the five buckets are exercised today

All in `tests/test_chip_test.py` (read this session):

| Test | Line | Bucket | Shape |
|------|------|--------|-------|
| `test_fp_blank_near_all_ff` | 173 | blank/contact | 256 B pattern vs all-`0xFF` |
| `test_fp_address_line_bit_a8` | 183 | address-line | 0x400 region, every byte with A8 set flipped, `addr_base=0` |
| `test_fp_address_line_absolute_addr_base` | 198 | address-line | same fault, `addr_base=0x8000` — pins Pitfall 3 |
| `test_fp_transport_scattered_repeatable` | 235 | transport | 1024 B, 16 hand-picked scattered offsets, `repeat_divergent=True` |
| `test_fp_indeterminate_ambiguous` | 250 | indeterminate | identical bytes, `repeat_divergent=False` |
| `test_fingerprint_evidence_fields` | 263 | (evidence keys) | 64 B, one flipped byte |
| `test_classify_fingerprint_still_returns_blank_contact_for_an_all_ff_perfect_compare` | 1447 | blank/contact | `b"\xff"*4096` vs itself — pins bucket-1-before-match |
| `test_synthesized_and_measured_fingerprints_share_one_evidence_key_set` | 1408 | match | asserts `sorted(synth.evidence) == sorted(measured.evidence)` |
| `test_diff_offsets_unequal_length` | 163 | (primitive) | unequal lengths compare over common prefix, never raise |

`_SCATTERED_OFFSETS` (`test_chip_test.py:214-231`) is a module-level list of 16 offsets reused by
both the transport and indeterminate tests, with a comment stating *"verified: max clustering ~0.81"*.
**Reuse this list in the corpus** — it is the only hand-tuned input in the suite that is known to sit
below the 0.9 cluster threshold, and re-deriving one risks accidentally landing in address-line.
[VERIFIED: firestarter_app/tests/test_chip_test.py:163-272, 1408-1455]

Additional `classify_fingerprint` usage lives in `tests/test_chip_test_sdp_leg.py` (`:186, 954,
1195-1204, 1228-1253, 1280`) and `Fingerprint` is constructed directly in
`tests/test_diagnostic_report.py` (`:82, 185, 666, 724, 1867`).

## Fixture idiom: parametrised, not property-based

**Parametrised wins for this repo.** Grounds:

1. **No property-based dependency exists.** `pyproject.toml`'s `[test]` extra is
   `pytest`, `syrupy`, `ruff`, `mypy`, `pytest-cov`, `types-pyserial` — **no `hypothesis`**.
   [VERIFIED: firestarter_app/pyproject.toml, `[project.optional-dependencies] test`]
   Adding it would mean a new CI dependency for one test, on a package that would need its own
   legitimacy gate.
2. **The existing bucket tests are already a corpus in all but name** — nine hand-shaped
   `(expected, actual, kwargs, expected_bucket)` cases with documented rationale for each shape.
   A `@pytest.mark.parametrize` corpus is the same data, restructured.
3. **Exact equality is achievable and is the right assertion.** Every `Fingerprint` field derives
   from integer counters through deterministic arithmetic (`bad_pct = 100.0 * bad / cmp_len`,
   `ff_ratio = ff_count / cmp_len`, `score = max(set_count, clear_count) / bad`). Identical integer
   inputs give bit-identical floats. `Fingerprint` is a plain `@dataclass`, so `==` is field-wise;
   `evidence` is a dict, and dict equality is insertion-order-insensitive, so a streamed path that
   builds `bit_clustering` in a different key order still compares equal.
   [VERIFIED: firestarter_app/firestarter/chip_test.py:152-262]

**Recommended corpus assertion:** `assert streamed_fp == batch_fp` on the whole dataclass, for every
case. Not field-by-field — a whole-object compare catches a field the refactor forgets to populate,
which a field list written by the same author would also forget to check.

## Four traps the corpus must cover

1. **`bit_clustering` requires `max_bit` which is only known at the end.** The batch code computes
   `max_bit = (cmp_len - 1).bit_length()` after the compare and iterates `range(8, max_bit)`. A
   streaming accumulator must count *all* candidate bits online (e.g. 8..31) and emit only
   `range(8, max_bit)` at finalisation. Emitting a key outside that range breaks dict equality.
   [VERIFIED: firestarter_app/firestarter/chip_test.py:216-227]
2. **Tie-breaking on `suspected_line`.** Selection is `if score > best_score` scanning `k` ascending
   from 8, so ties resolve to the **lowest** bit. A streamed path iterating bits in a different order
   picks a different line on a tie. Include a tie case in the corpus.
   [VERIFIED: firestarter_app/firestarter/chip_test.py:220-227]
3. **The `cmp_len > (1 << 8)` guard.** Regions of exactly 256 bytes never enter address-line
   clustering at all, so `bit_clustering` stays `{}`. `tests/test_chip_test_sdp_leg.py:1228-1253`
   already depends on this. Include a 256-byte case and a 257-byte case.
   [VERIFIED: firestarter_app/firestarter/chip_test.py:214; tests/test_chip_test_sdp_leg.py:1228-1253]
4. **Zero-length and unequal-length inputs.** `_diff_offsets` compares `min(len(expected), len(actual))`
   and never raises; `classify_fingerprint(A, b"")` returns `total=0, bad=0` — which
   `tests/test_chip_test_sdp_leg.py:1193-1197` documents verbatim as a *"measured trap"*: *"an empty
   read-back reads as PERFECT equality; only the length gate stops it (P-02)."* The streamed path
   must reproduce this, including `ff_ratio = 0.0` on `cmp_len == 0`.
   [VERIFIED: firestarter_app/firestarter/chip_test.py:118-131; tests/test_chip_test_sdp_leg.py:1193-1197]

## ⚠ An existing test will silently become theatre

`tests/test_chip_test.py:2294-2305`, verbatim:

```python
def test_generate_pattern_and_classify_fingerprint_source_unchanged():
    import inspect

    import firestarter.chip_test as chip_test_mod

    gen_src = inspect.getsource(chip_test_mod.generate_pattern)
    assert "_WRITE_REGION_START" not in gen_src
    assert "_UV_WRITE_REGION_LENGTH" not in gen_src

    classify_src = inspect.getsource(chip_test_mod.classify_fingerprint)
    assert "_WRITE_REGION_START" not in classify_src
    assert "_UV_WRITE_REGION_LENGTH" not in classify_src
```
[VERIFIED: firestarter_app/tests/test_chip_test.py:2294-2305]

**Good news:** it pins two constant *names* out of the source, not a hash — so D-02's rewrite does
not break it.

**Bad news:** once `classify_fingerprint` becomes a thin delegating wrapper, `inspect.getsource` returns
a handful of lines that trivially contain neither name, and the test passes **vacuously**. Its guard —
that region constants never leak into the classifier — silently stops being enforced, because the
logic has moved to `compare.py` which this test does not inspect. The plan should either extend the
assertion to cover the new module's accumulator source, or delete the test with a stated reason.
Leaving it as-is is the worst of the three: a green test that guards nothing.

---

# Question 4 — Test and CI constraints that bind the plan

## Exact CI invocation

`.github/workflows/ci.yml`, job `ci`, runner `ubuntu-latest`, verbatim step order:

| # | Step | Command |
|---|------|---------|
| 1 | Set up Python | `actions/setup-python@v5` with `python-version: '3.11'` |
| 2 | Install | `pip install -e .[test]` |
| 3 | ruff lint | `ruff check firestarter/ tests/` |
| 4 | ruff format check | `ruff format --check firestarter/ tests/` |
| 5 | pytest + coverage | `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |
| 6 | Smoke test | `pip install -e . && firestarter --help` |

A second job `ci-py32` installs `.[test,py32]` and runs `pytest tests/test_pyusb_api_surface.py -q`.
[VERIFIED: firestarter_app/.github/workflows/ci.yml]

Triggers: `push` on `branches: ['**']` and `pull_request`, both with
`paths-ignore: ['**.md', '.gitignore', 'docs/**', '.vscode/**', '.editorconfig']`.
**CI runs on the milestone branch** — `v1.41-verification-to-host` matches `'**'`.
[VERIFIED: firestarter_app/.github/workflows/ci.yml]

## Running the suite on Python 3.11 — the exact command

Three ready-made 3.11 virtualenvs exist in the working tree, all with `pytest`, `ruff`, `mypy` and
`coverage` installed and `firestarter` resolving to the working tree:

| venv | Python |
|------|--------|
| `firestarter_app/.venv311` | 3.11.16 |
| `firestarter_app/.venv-ci-188` | 3.11.16 |
| `firestarter_app/.venv/ci-replica` | 3.11.16 |

The devcontainer default `python3` is **3.12.14**, and there is **no `python3.11` on `PATH`**.
[VERIFIED: run this session — `python3 -V` → 3.12.14; `command -v python3.11` → not found;
each venv's `bin/python -V` and `bin/` contents listed]

**Prescribed command, run and confirmed green this session:**

```bash
cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/ \
    --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```

Measured result: **2106 passed in 174.58s**, **TOTAL coverage 85.42%**,
`Required test coverage of 70% reached.`, 36 snapshots passed.
[VERIFIED: command run this session, output pasted]

For a fast subset while iterating (note `-o addopts=""` — `addopts` is `-ra -q`, and doubling `-q`
suppresses the count line):

```bash
.venv311/bin/python -m pytest tests/test_chip_test.py -q -k "fingerprint" -o addopts=""
```
Measured: `12 passed, 150 deselected in 0.10s`.
[VERIFIED: command run this session]

## ruff

```toml
[tool.ruff]
target-version = "py311"
line-length = 88
extend-exclude = ["tests/golden", "tests/fixtures"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
extend-ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```
[VERIFIED: firestarter_app/pyproject.toml, `[tool.ruff]` block]

**Select set is exactly `E, F, I, UP` with `E501` ignored.** A `# noqa:` for any other code (`BLE001`,
`B008`, `SIM105`, …) is **inert** — it silences nothing and is dead text. `UP` is live, so
`typing.Tuple`/`Dict` need `# noqa: UP006` (the existing code does exactly this at
`eprom_operations.py:466`). `I` is live, so import ordering in the new `compare.py` is gated.

## mypy — and what happens to a new `firestarter/compare.py`

**mypy is NOT a CI gate.** It runs only in `.pre-commit-config.yaml`, hook order
`ruff-check` → `ruff-format` → `mypy`, via `mirrors-mypy` rev `v2.1.0` with
`additional_dependencies: types-pyserial>=3.5.0.20260519`.
[VERIFIED: firestarter_app/.pre-commit-config.yaml; firestarter_app/CLAUDE.md:39-40]

Global settings (`[tool.mypy]`): `python_version = "3.11"`, `ignore_missing_imports = true`,
`disallow_untyped_defs = false`, `check_untyped_defs = false`, `exclude = ["^tests/fixtures/"]`.
[VERIFIED: firestarter_app/pyproject.toml `[tool.mypy]`]

**Strict-island module list, verbatim** (`disallow_untyped_defs = true`, `check_untyped_defs = true`):

```python
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
    "firestarter.log_capture",
]
```
**`cli_handlers` IS in the strict list — CONTEXT.md's claim is confirmed.**
`chip_test` is **not** in it, and is not in the `follow_imports = "silent"` list either.
[VERIFIED: firestarter_app/pyproject.toml, `[[tool.mypy.overrides]]` Phase 42 D-06 block]

**A new `firestarter/compare.py` would be in NEITHER list**, so it inherits the lenient global
settings. Probed empirically this session: a scratch `firestarter/_scratch_probe.py` containing both
an untyped `def untyped_fn(a, b)` and a genuine annotated type error produced:

```
firestarter/_scratch_probe.py:7: error: Incompatible return value type (got "str", expected "int")  [return-value]
Found 1 error in 1 file (checked 1 source file)
```

The untyped def raised **no** error; only the real type error in the annotated function did. (Probe
file removed; `git status --porcelain firestarter/` clean afterwards.)
[VERIFIED: command run this session, output pasted]

**Planner decision point (not settled by CONTEXT.md):** `compare.py` is a brand-new module consumed
by a strict module (`cli_handlers`) and by `chip_test`. The repo has a stated precedent for adding a
new module to the strict list from birth — `pyproject.toml`'s own comment says *"a ninth added by
Phase 132 D-02 (RETIRE-03): the new sdp_honesty module joins from birth, as a deliberate
strengthening"*. Adding `"firestarter.compare"` to that list is cheap now and expensive later. **This
is an open question, flagged in the Assumptions Log** — D-01 does not decide it.

Baseline check: `mypy firestarter/main.py firestarter/cli_handlers.py` currently reports
**`Success: no issues found in 2 source files`**. Any new typing error in `cli_handlers` is a
regression against a green baseline, not a pre-existing wart.
[VERIFIED: command run this session]

A stale watermark comment sits at `pyproject.toml` (`# mypy_error_watermark = 35 ... Prior: 29`),
commented out. It is inert; do not treat it as a gate.

## Coverage

```toml
[tool.coverage.run]
source = ["firestarter"]
omit = ["firestarter/data/*", "firestarter/avr_tool.py"]

[tool.coverage.report]
show_missing = true
```
[VERIFIED: firestarter_app/pyproject.toml]

`source = ["firestarter"]` is the whole package, so **a new `firestarter/compare.py` counts toward
the floor automatically** — no config change needed.

**The floor is not a binding constraint.** Measured total is **85.42%** against a **70%** floor, over
6,140 statements with 895 missed. Arithmetic: adding a ~200-statement module at **0%** coverage
would give 5245/6340 = **82.7%** — still 12.7 points clear of the floor. The plan does not need a
coverage-defence task.

`tests/test_coverage_floor_v18.py` exists but is a historical margin-restoration module from Phase 43
targeting `frame_parser`/`codec`/`chip_resolver`/`main`/`config` branches. It imposes no new
constraint on this phase.
[VERIFIED: firestarter_app/tests/test_coverage_floor_v18.py:1-27]

**Coverage detail worth knowing:** `verify_eprom`'s uncovered lines today are `2159-2160, 2171, 2188`
(the `OSError` branch, the `not cmd_data` early return, and the failure log) and `check_eprom_blank`
(2325-2360) is **covered**. `eprom_operations.py` overall sits at 72%.
[VERIFIED: coverage report from the run this session]

---

# Secondary confirmations

## `_main_phase_read_data` — signature and calling shape ✅ confirmed

```python
def _main_phase_read_data(
    self,
    progress: ClassProgressHandler,
    start_addr: int,
    end_addr: int,
    process_data_chunk_callback: Callable,
):
```
[VERIFIED: firestarter_app/firestarter/eprom_operations.py:869-875]

Per-chunk body, verbatim (`eprom_operations.py:905-912`):

```python
if response.payload is not None:
    # MSG_DATA_CHUNK: the raw chip bytes are in response.payload.
    payload = response.payload
    if not payload:
        logger.warning("Received MSG_DATA_CHUNK with empty payload.")
        continue
    process_data_chunk_callback(start_addr, payload)
    start_addr += len(payload)
    progress.update(len(payload))
    self.comm.send_ack()
```

**Confirmed: it delivers `(address, payload)` per chunk and acks each one.** `start_addr` is
advanced by the host, so the address handed to the callback is absolute.
[VERIFIED: firestarter_app/firestarter/eprom_operations.py:905-912]

`read_eprom` drives it like this (`eprom_operations.py:952-963`):

```python
def _write_to_file(address, data_chunk):
    file_handle.seek(address)
    file_handle.write(data_chunk)

is_ok, _ = self._run_state_machine(
    op_name,
    main_phase_handler=self._main_phase_read_data,
    start_addr=cmd_data.get("address", 0),
    end_addr=cmd_data.get("memory-size", 0),
    process_data_chunk_callback=_write_to_file,
)
```
[VERIFIED: firestarter_app/firestarter/eprom_operations.py:952-963]

The region is `[cmd_data["address"], cmd_data["memory-size"])`. `consistency_check_eprom` drives the
same handler at `:1086` and `:1255`; `read_eprom` at `:962`; a hexdump path at `:1887`.
[VERIFIED: grep of `process_data_chunk_callback` in eprom_operations.py]

**CMP-08 maps onto existing code with no new plumbing:** `_setup_operation` already honours `size`
for reads —

```python
if cmd == COMMAND_READ and size:
    read_size = parse_size(size) or 0
    command_dict["memory-size"] = addr + read_size
```
[VERIFIED: firestarter_app/firestarter/eprom_operations.py:493-501]

Since `verify`/`blank` now issue `COMMAND_READ`, `-a`/`-s` flow through unchanged. D-17's *refusal*
cases (file shorter than `--size`; region past chip end) are the genuinely new logic, and D-17
requires them to fire **before the port opens** — i.e. in `cli_handlers`, ahead of
`_operation_context`.

## ⚠ Gap: `_main_phase_read_data` cannot be reused *entirely* unchanged

CONTEXT.md describes `_main_phase_read_data` as *"the existing chunk-callback read path this phase
reuses unchanged."* **The read path is reusable, but the abort is not expressible through it today.**

`process_data_chunk_callback`'s return value is **discarded** (`eprom_operations.py:909` — the call
is a bare statement). The loop then unconditionally `send_ack()`s at `:912`. There is no way for the
comparison engine to say "stop acking" from inside the callback.

D-06 requires the host to **stop acking while continuing to read**, so that the firmware's
`op_wait_for_ack` times out after 1 s, `_process_outgoing_data` returns false, and `loop()` runs
`command_done()` to leave the port clean. Simply raising out of the callback would unwind the loop
*without* consuming the resulting `ERROR` frame, leaving unread bytes on the port — which is the
opposite of what D-06 buys.

**The planner must choose a mechanism.** Two shapes fit the existing code:
- **(a)** Honour the callback's return value: `if process_data_chunk_callback(...) is False: stop_acking = True`,
  then guard the `send_ack()` and keep looping until the `ERROR`/`MAIN` response arrives. Smallest
  diff; changes a callback contract shared by four call sites, all of which currently return `None`
  (falsy — so a naive `if not cb(...)` would break every existing caller; test for `is False`).
- **(b)** Add an optional `abort_predicate` / `stop_event` keyword to `_main_phase_read_data`,
  leaving the callback contract untouched.

This is real work that CONTEXT.md's phrasing understates. It is **not** a re-litigation of D-06 —
the mechanism is confirmed; what is missing is the host-side plumbing to trigger it.

## D-08's discrimination maps onto an existing seam ✅

`MSG_ERR_TIMEOUT = 0xA8`. [VERIFIED: firestarter_app/firestarter/messages.py:101]

An `ERROR` response in the read loop goes to `_raise_for_error_response(response, ...)`
(`eprom_operations.py:895`), which raises `EpromOperationError(message, error_code=response.id)`
(`eprom_operations.py:107`). `_run_state_machine` catches it and records the id
(`eprom_operations.py:626-631`):

```python
except EpromOperationError as e:
    logger.error(f"Programmer error during {operation_name}: {e}")
    self.last_firmware_error_code = e.error_code
    self.last_firmware_error_message = str(e)
    return False, str(e)
```
[VERIFIED: firestarter_app/firestarter/eprom_operations.py:91-108, 626-631]

So D-08's "accept only `MSG_ERR_TIMEOUT`, only within a bounded window after the stop" becomes:
after `_run_state_machine` returns `(False, msg)`, check the intent flag **and**
`operator.last_firmware_error_code == MSG_ERR_TIMEOUT` **and** the elapsed-time window. No new
error plumbing is needed. Note `_run_state_machine` clears both fields at entry
(`eprom_operations.py:602-604`), so a stale value from a previous operation cannot leak in.

## Firmware evidence for D-06 ✅ spot-confirmed (not modified)

```cpp
bool op_wait_for_ack(firestarter_handle_t* handle) {
    unsigned long timeout = millis() + 1000;
    while (millis() < timeout) {
        op_message_type msg_type = op_get_message(handle);
        if (msg_type == OP_MSG_ACK) {
            return true;
        }
        if (msg_type == OP_MSG_ERROR) {
            return false;
        }
        delay(10);
    }
    LOG_ERROR_ID(MSG_ERR_TIMEOUT);
    return false;
}
```
[VERIFIED: firestarter_fw/src/operation_utils.cpp:94-108]

```cpp
    if (!op_wait_for_ack(handle)) {
        return false;
    }
```
[VERIFIED: firestarter_fw/src/eprom_operations.cpp:170-172]

Confirms D-06's stated cost precisely: **up to 1 s**, polled at 10 ms.

## CLI option spelling for CMP-08 ✅

`read` (`cli_handlers.py:529-557`), verbatim:
```python
@click.option("-f", "--force", is_flag=True, help="Force, even if the chip id doesn't match.")
@click.option("-a", "--address", default=None, help="Read start address in dec/hex")
@click.option("-s", "--size", default=None, help="Size of the data to read in dec/hex")
```

`verify` (`cli_handlers.py:794-822`) — **already has `-a/--address`**, verbatim:
```python
@click.option("-a", "--address", default=None, help="Verify start address in dec/hex")
@click.option("-f", "--force", is_flag=True, help="Force, even if the VPP or chip id doesn't match.")
```

`blank` (`cli_handlers.py:824-841`) — **has only `-f/--force`**:
```python
@click.option("-f", "--force", is_flag=True, help="Force, even if the VPP or chip id doesn't match.")
```
[VERIFIED: firestarter_app/firestarter/cli_handlers.py:529-557, 794-841]

**Delta CMP-08 requires:** `verify` gains `-s/--size` and `--full`; `blank` gains `-a/--address`,
`-s/--size` and `--full`. Match `read`'s spelling exactly: short flag + long flag, `default=None`,
help text ending `"in dec/hex"`.

Both commands end `sys.exit(0 if ok else 1)` and carry `@click.pass_obj` + `@map_typed_errors`.
`map_typed_errors` (`cli_handlers.py:190-229`) maps eleven typed exceptions to `click.ClickException`.
**`ClickException.exit_code` is 1 and `UsageError.exit_code` is 2** — which is exactly the collision
D-10 accepts. The exit-2 path must therefore be produced *without* routing through `map_typed_errors`'
`ClickException` conversion for these two commands.
[VERIFIED: firestarter_app/firestarter/cli_handlers.py:190-229, 794-841]

---

## Standard Stack

No new runtime dependencies. Everything this phase needs is stdlib or already installed.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `tracemalloc` | stdlib (3.11) | Peak-allocation assertion for criterion 2 | Only stdlib option; traces Python allocations so it is immune to RSS noise. Measured floor 88 B |
| `pytest` | `>=8.0` (installed 3.11 venvs) | Test runner | Already the suite's runner; `parametrize` is the corpus idiom |
| `click` | `>=8.1` | CLI options + exit codes | Already the CLI framework |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `unittest.mock.patch` | stdlib | `find_and_connect` capture for criterion 1 | The existing five-site idiom |
| `syrupy` | `>=5.0,<7` | Snapshot assertions | Only if the plan snapshots the two output lines. 36 snapshots exist; note CLAUDE.md's warning that a later interpreter turns snapshot failures into collection errors |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `tracemalloc` | `resource.getrusage(RUSAGE_SELF).ru_maxrss` | Measures process RSS — contaminated by every prior test, monotonic (never decreases), and platform-variable units. Unusable for a per-test bound |
| `tracemalloc` | `psutil` | **Not a dependency**; would need adding to `[test]` and a legitimacy gate, for strictly worse data than stdlib |
| parametrised corpus | `hypothesis` property tests | **Not a dependency.** Would add a CI dep for one test. Also a poor fit: the five buckets are threshold-defined regions, and random inputs land in `indeterminate` overwhelmingly |
| per-chunk offset list | pure-counter streaming (no lists) | **Measured 11x slower** (21.4 s vs 1.9 s worst case) for ~79 KB less peak. Bad trade |
| per-chunk offset list | `int.from_bytes` big-int XOR | Locates differing bytes but still needs a per-offset loop to extract them; measured no faster (21.4 s) |

**Installation:** none required.

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** Every library named above is either
Python stdlib (`tracemalloc`, `unittest.mock`, `os`, `inspect`) or already a declared dependency in
`firestarter_app/pyproject.toml` (`pytest`, `click`, `syrupy`), verified by reading that file this
session. No registry lookups were required and no new names are introduced.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### Data flow

```
cli_handlers.verify / .blank
  │  D-17: resolve region, refuse conflicts  ── BEFORE the port opens ──► exit 2
  │
  ├─► compare.compare_region(...)                       [firestarter/compare.py — NEW, D-01]
  │     │  expected = pull callback (D-04): file.seek for verify, b"\xff"*n for blank
  │     │
  │     └─► eprom_operations.read_eprom-shaped drive of _main_phase_read_data
  │            │  per chunk: (address, payload)
  │            ▼
  │         Accumulator.feed(address, expected_chunk, payload)
  │            ├─ ff += payload.count(0xFF)              ── C level
  │            ├─ if expected == payload: return         ── C memcmp, the common case
  │            ├─ offs = [per-chunk offsets]             ── bounded by chunk size
  │            ├─ bad, first_offset, per-bit set_count   ── running counters
  │            └─ coalesce into ranges, cap at N (D-16)  ── overflow → counters only
  │            │
  │            └─ default mode & bad > 0 ──► signal abort ──► stop acking (D-06)
  │                                                            firmware times out ≤1 s
  │                                                            command_done() → port clean
  ▼
  CompareResult { ranges[], extra_ranges, extra_bytes, fingerprint, compared_range }   ← D-05
  │
  ├─► classify_fingerprint(...)  delegates here (D-02)   [chip_test.py, reimplemented]
  │
  └─► render (D-13 + D-14)  ── separate from compare, per D-05
        "Mismatch 0xSTART-0xEND (N bytes)"
        "address-line, 2305 bad of 65536 compared of 65536"
```

### Recommended structure
```
firestarter/
├── compare.py          # NEW (D-01): accumulator + CompareResult + Fingerprint construction.
│                       #   Import-light: stdlib only. NO eprom_operations, NO chip_test,
│                       #   NO serial_comm, NO database.
├── chip_test.py        # classify_fingerprint reimplemented to delegate to compare.py (D-02)
├── eprom_operations.py # verify_eprom / check_eprom_blank rewritten; _main_phase_read_data
│                       #   gains an abort signal (see the Gap above)
└── cli_handlers.py     # new options, region resolution, exit-code 0/1/2 (D-10, D-11, D-17)
```

### Pattern 1: three-tier per-chunk accumulation
**What:** Descend to per-byte work only for chunks that actually differ.
**When:** Every chunk.
**Why:** Measured 0.002 s vs 19.8 s over 512 KB.

```python
# Measured this session on Python 3.11.16, 512 KiB / 1024-B chunks.
def feed(self, address: int, expected: bytes, actual: bytes) -> None:
    self.ff_count += actual.count(0xFF)        # C level
    self.total += len(actual)
    if expected == actual:                     # C memcmp — the overwhelmingly common case
        self._close_open_range()
        return
    offs = [address + i for i in range(len(actual)) if expected[i] != actual[i]]
    if self.first_offset is None:
        self.first_offset = offs[0]
    self.bad += len(offs)
    for k in self._candidate_bits:             # only bits that can vary in this region
        mask = 1 << k
        self._set_count[k] += sum(1 for o in offs if o & mask)
    self._coalesce(offs)
    # `offs` goes out of scope here — never device-sized. This satisfies D-02.
```

### Pattern 2: finalisation reproduces the batch shape exactly
`max_bit` is not known until the compare ends, so accumulate all candidate bits online and emit only
`range(8, (cmp_len - 1).bit_length())` at finalisation, iterating `k` ascending so ties resolve to
the lowest bit — matching `chip_test.py:216-227`.

### Anti-Patterns to Avoid
- **A device-sized offset list.** The object D-02 names. Measured 22 MB at 512 KB.
- **A nested per-offset × per-bit loop.** Measured 21.4 s. Hoist the bit loop outside and use
  `sum(... for o in offs)` per bit — measured 1.9 s.
- **`blank` allocating `b"\xff" * memory_size`.** D-04 forbids it; the pull callback returns
  `b"\xff" * length` per chunk, which is at most one chunk's worth.
- **Widening `map_typed_errors` to emit exit 2.** D-11 forbids it — it is shared by ~20 commands
  including `write`.
- **Assuming `if not callback(...)` detects an abort.** All four existing callbacks return `None`,
  which is falsy. Test `is False`, or use a separate keyword.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Fake serial port | A new mock | `conftest.fake_serial` + `make_comm` (`conftest.py:133-193`) | Already models pyserial timeout-empty semantics and the `in_waiting` contract |
| Wire frame construction | Hand-built bytes | `conftest.build_frame(msg_id, params)` (`:120-131`) | CRC8 reference is deliberately table-free to catch production-table regressions |
| Recording host writes | A new wrapper | `_capture_written_frames` (`test_eprom_operations.py:1164-1179`) | Preserves the underlying write so the state machine still runs |
| Capturing the command dict | A new patch target | The `find_and_connect` `side_effect` idiom (`:1196-1216`) | Five worked sites already |
| Divergence math | A second implementation | Delegate to the one accumulator (D-02) | `chip_test.py:105-116` states the rule in source |
| Peak memory | RSS sampling / `psutil` | `tracemalloc.get_traced_memory()` | Stdlib; 88 B noise floor; immune to other tests |
| Address/size parsing | New parsers | `address_parser.parse_address` / `parse_size` | Already wired through `_setup_operation` |
| Scattered-offset test data | New random offsets | `_SCATTERED_OFFSETS` (`test_chip_test.py:214-231`) | Hand-tuned and verified to cluster at ~0.81, below the 0.9 threshold |

**Key insight:** this repo's test suite is unusually rich in purpose-built seams, and the two things
CONTEXT.md flagged as homeless are both already furnished. The genuine new work is the accumulator's
inner loop and the abort plumbing — neither of which was flagged.

## Common Pitfalls

### Pitfall 1: the 20-second inner loop
**What goes wrong:** A literal reading of D-02 ("no materialised list") produces a per-byte,
per-bit nested loop. 512 KB costs 19.8–21.4 s, in tests and in production.
**Why:** D-02 forbids a *device-sized* list; the obvious way to avoid lists entirely is the slow way.
**How to avoid:** `expected == actual` memcmp fast path + per-chunk bounded offset list.
**Warning signs:** a single test taking >5 s; `verify` on a 512 KB part feeling slower than `read`.

### Pitfall 2: the source-pin test becomes theatre
**What goes wrong:** `test_generate_pattern_and_classify_fingerprint_source_unchanged` keeps passing
after `classify_fingerprint` becomes a wrapper, while guarding nothing.
**How to avoid:** extend it to inspect the accumulator's source in `compare.py`, or delete it with a
stated reason. Do not leave it.

### Pitfall 3: `bit_clustering` key-set mismatch
**What goes wrong:** the streamed path emits bit keys outside `range(8, max_bit)`, so
`Fingerprint.__eq__` fails on `evidence` even though every count is right.
**How to avoid:** accumulate all candidate bits, filter at finalisation. Cover with a corpus case
whose `cmp_len` is not a power of two.

### Pitfall 4: `ClickException` exits 1, not 2
**What goes wrong:** the exit-2 path is implemented by raising a typed error, `map_typed_errors`
converts it to `ClickException`, and the process exits 1 — silently defeating D-10.
**How to avoid:** produce exit 2 with `sys.exit(2)` (or a `ClickException` subclass overriding
`exit_code`) on a path that does not pass through `map_typed_errors`' conversion.
**Warning signs:** a test asserting exit 2 that passes only because `UsageError` fired for another reason.

### Pitfall 5: the abort is mistaken for a fault (D-08)
**What goes wrong:** the deliberate stop yields `MSG_ERR_TIMEOUT` (0xA8), wire-identical to a genuine
timeout, and the run reports exit 2 instead of exit 1.
**How to avoid:** intent flag + `last_firmware_error_code == MSG_ERR_TIMEOUT` + bounded window.
**Warning signs:** a mismatching chip reporting "transport error" instead of a mismatch.

### Pitfall 6: `-o addopts=""` is needed to see the count
**What goes wrong:** `addopts = "-ra -q"`; adding another `-q` suppresses the `N passed` line.
**How to avoid:** `pytest ... -o addopts=""` when you need the count.
[VERIFIED: firestarter_app/pyproject.toml `[tool.pytest.ini_options]`; recorded in user memory]

### Pitfall 7: `grep` under-scans
**What goes wrong:** the devcontainer `grep` is ugrep 7.8.4, which honours `.gitignore`. A negative
result may be a filtered result.
**How to avoid:** for any load-bearing negative claim, use a Python `os.walk` or `grep --no-ignore`.

### Pitfall 8: a green 3.12 run proves nothing
**What goes wrong:** the devcontainer default is Python 3.12.14; CI pins 3.11. Snapshot failures
become collection errors across that boundary.
**How to avoid:** `.venv311/bin/python -m pytest ...`.

## Runtime State Inventory

**Not applicable — this is not a rename, refactor-by-string-replacement, or migration phase.** It
adds a module and rewrites two functions; no stored data, service config, OS registration, secret
name, or build artifact carries a string this phase changes.

One adjacent note, stated because it is easy to assume otherwise: `COMMAND_VERIFY` (6) and
`COMMAND_BLANK_CHECK` (4) in `constants.py` become unreferenced by the verify/blank paths but
**stay in place** — Phases 204/205 remove them. `COMMAND_NAMES` still dereferences both
(`constants.py:87-93`), and `constants.py:61-62` warns those entries are *"load-bearing, not
cosmetic"* because `_setup_operation` indexes `COMMAND_NAMES[cmd]`. Do not prune them here.
[VERIFIED: firestarter_app/firestarter/constants.py:49-93]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 | CI parity | ✓ (venvs only) | 3.11.16 | none needed — three venvs present |
| Python 3.11 on `PATH` | convenience | ✗ | — | `.venv311/bin/python` |
| `python3` (default) | devcontainer | ✓ | 3.12.14 | **do not use for the suite** |
| `pytest` | test suite | ✓ | in all three 3.11 venvs | — |
| `ruff` | lint gate | ✓ | in all three 3.11 venvs | — |
| `mypy` | pre-commit | ✓ | in all three 3.11 venvs | — |
| `coverage` | floor gate | ✓ | in all three 3.11 venvs | — |
| `tracemalloc` | criterion 2 | ✓ | stdlib | — |
| `hypothesis` | (rejected) | ✗ | — | `pytest.mark.parametrize` |
| `psutil` | (rejected) | ✗ | — | `tracemalloc` |
| Bench hardware | — | n/a | — | **phase is bench-no**; synthetic chunk generator |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** `python3.11` is not on `PATH` — use `.venv311/bin/python`.
[VERIFIED: commands run this session]

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. This
phase is a local CLI tool with no network surface, no authentication, no session, no access control
and no cryptography. Most ASVS categories do not apply.

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No identity in a local serial CLI |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | No multi-user model |
| V5 Input Validation | **yes** | D-17's refusals ARE the validation: `--size` vs file length, region vs chip end. Parse via existing `address_parser` |
| V6 Cryptography | no | None involved; CRC8 is integrity, not security |

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via `input_file` | Tampering | Pre-existing surface, unchanged by this phase — `verify` already accepts a path |
| Unbounded memory from a hostile/faulty device | Denial of Service | **This is CMP-03.** The streaming bound is the mitigation; measured flat at ≤87 KB |
| Unbounded output volume on a bad part | Denial of Service | **This is D-16.** Range cap `N` with exact counters in the tail line |

Both DoS-shaped concerns are already requirements. No additional security work is indicated.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Firmware compares (`CMD_VERIFY`, `CMD_BLANK_CHECK`) | Host reads + compares | This phase | Firmware keeps both ordinals until Phase 204/205 |
| `_diff_offsets` materialises every offset | Streaming accumulator | This phase (D-02) | 22 MB → ~4 KB at 512 KB, measured |
| Single-address mismatch report | Coalesced `start–end` ranges + bucket | This phase (D-13/D-14) | CMP-04 amended 2026-09-20, commit `81414f98` |
| `sys.exit(0 if ok else 1)` everywhere | 0/1/2 on `verify`/`blank` only | This phase (D-10/D-11) | Other ~20 commands unchanged; deferred as backlog |

**Deprecated/outdated:** the no-comments-in-source rule (removed 2026-09-19 — comments are allowed
and D-02/D-08/D-12 warrant them). The `# mypy_error_watermark = 35` note in `pyproject.toml` is
commented out and inert.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `ClickException.exit_code == 1` and `UsageError.exit_code == 2` in the installed Click | Pitfall 4 | Taken from D-10's own stated reasoning and Click's documented contract; **not** re-read from the installed `click` source this session. If wrong, the exit-code design needs rework. Cheap to confirm: `python -c "import click; print(click.ClickException.exit_code, click.UsageError.exit_code)"` |
| A2 | A parametrised corpus fits this repo better than property-based testing | Question 3 | Judgement, grounded in the verified absence of `hypothesis` from `[test]` and the verified shape of the nine existing bucket tests. If the planner disagrees, adding `hypothesis` is a new CI dependency needing a legitimacy gate |
| A3 | `N = 64` for D-16's range cap and `1 MiB` for the memory ceiling | Questions 2, Pattern 1 | Both are explicitly Claude's discretion per CONTEXT.md. `1 MiB` is grounded in measurement (12x above worst observed peak); `N = 64` is a round number used to make the measurement concrete, not a derived value |
| A4 | `firestarter.compare` should join the mypy strict list from birth | Question 4 | **Open — D-01 does not decide it.** The `sdp_honesty` precedent (verified in `pyproject.toml`'s own comment) favours joining. Risk if skipped: the module is never type-gated, and adding it later means fixing accumulated errors at once |
| A5 | The corpus can reach the `transport` bucket by calling `classify_fingerprint(repeat_divergent=True)` directly | Question 3 | Verified that `test_fp_transport_scattered_repeatable` does exactly this. CMP-F2 records that the bucket is unreachable *in production* (`_dispatch_multi_run` always runs with `runs=1`), which does not block a direct-call corpus case |

## Open Questions (RESOLVED)

> All four were disposed of during planning (5 plans, commit `592a6d6d`). Each carries its
> resolution and the plan task that owns it. Nothing here is still open.

1. **How does the engine signal "stop acking" through `_main_phase_read_data`?**
   - What we know: the callback's return value is discarded (`eprom_operations.py:909`) and
     `send_ack()` is unconditional (`:912`). All four existing callbacks return `None`.
   - What's unclear: whether to honour a callback return (`is False`) or add an explicit
     `abort_predicate` keyword.
   - Recommendation: the planner should decide this explicitly in a task, not leave it to an
     executor. Prefer the explicit keyword — it leaves the four existing callers untouched and makes
     the abort readable at the call site. **This is the phase's one genuine unplumbed seam.**
   - **RESOLVED:** explicit keyword, as recommended. `202-04-PLAN.md` Task 1 ("An additive abort
     seam in the read loop") adds `abort_predicate: Callable[[], bool] | None = None` to
     `_main_phase_read_data`. The four existing callers are unchanged and the chunk callback's
     return value stays ignored, so no existing behaviour moves. `202-04` Task 2 consumes it.

2. **Does `firestarter.compare` join the mypy strict-island list?**
   - What we know: it lands in neither override list by default, so it inherits lenient global
     settings (probed empirically). `sdp_honesty` has a stated precedent for joining from birth.
   - Recommendation: add it. The cost is writing annotations in a brand-new file; the alternative is
     an untyped module consumed by a strict one.
   - **RESOLVED:** it joins, from birth. `202-01-PLAN.md` Task 2 adds `firestarter.compare` to the
     `disallow_untyped_defs = true` override block in `pyproject.toml`, following the
     `sdp_honesty` joins-from-birth precedent recorded in that block's own comment.

3. **Does the range cap `N` apply to the default mode as well as `--full`?**
   - What we know: D-16 scopes the cap to `--full`; D-13 says the default produces exactly one range
     line, so the cap is moot there.
   - Recommendation: implement the cap in the accumulator (one code path) and let the default's
     single-range behaviour fall out of the abort, not out of a separate cap.
   - **RESOLVED:** one code path, as recommended. `MAX_RETAINED_RANGES` (= 64) lives in the
     accumulator, declared in `202-01-PLAN.md`; `202-02-PLAN.md` Task 3 tests its boundary and the
     honesty of the `extra_ranges` counter. The default's single-range behaviour falls out of the
     abort, not a second cap.

4. **What does the progress bar do on an aborted read, and does `blank` show one?**
   - Explicitly left to Claude's discretion by CONTEXT.md; raised and declined during discussion.
     Flagged only so the planner allocates it rather than discovering it mid-execution.
   - **RESOLVED:** allocated, not discovered. `202-04-PLAN.md` Task 2 stops the bar at the compared
     byte count and never advances it to the region total on an abort, with the reason recorded at
     the site; the same plan's threat table cites it under T-202-08 (an aborted compare must not
     read as a clean pass).

## Sources

### Primary (HIGH confidence) — files read in this session
- `/workspaces/.planning/phases/202-one-comparison-engine-on-the-host/202-CONTEXT.md` — D-01…D-17
- `/workspaces/.planning/REQUIREMENTS.md:54-61, 113-114, 135-142` — CMP-01…08, CMP-F1/F2
- `/workspaces/.planning/ROADMAP.md:215-274` — milestone section, Phase 202 detail
- `/workspaces/.planning/STATE.md:8, 11` (grepped) — phase status and discussion summary
- `/workspaces/CLAUDE.md`, `/workspaces/firestarter_app/CLAUDE.md`
- `firestarter_app/pyproject.toml` — ruff, mypy, coverage, pytest, dependencies
- `firestarter_app/.github/workflows/ci.yml`, `beta-release.yml`, `publish.yml`
- `firestarter_app/.pre-commit-config.yaml`
- `firestarter_app/firestarter/chip_test.py:105-305`
- `firestarter_app/firestarter/eprom_operations.py:91-108, 457-545, 587-700, 860-971, 973-1060, 2144-2200, 2325-2375`
- `firestarter_app/firestarter/cli_handlers.py:190-232, 529-560, 794-845`
- `firestarter_app/firestarter/serial_comm.py:200-300` (+ function index)
- `firestarter_app/firestarter/constants.py:49-93`, `firestarter/messages.py:101, 109`
- `firestarter_app/tests/conftest.py:1-240`, `tests/fake_chip.py:1-90`
- `firestarter_app/tests/test_eprom_operations.py:1164-1250`
- `firestarter_app/tests/test_chip_test.py:160-275, 1400-1420, 2294-2325`
- `firestarter_app/tests/test_chip_test_sdp_leg.py:1190-1215`
- `firestarter_app/tests/test_coverage_floor_v18.py:1-30`
- `firestarter_fw/src/operation_utils.cpp:94-108`, `src/eprom_operations.cpp:157-180`

### Primary (HIGH confidence) — commands run in this session, output pasted
- `tracemalloc` benchmarks: streaming vs materialised; three accumulator strategies; realistic
  accumulator with D-16 cap across four fault patterns
- `.venv311/bin/python -m pytest tests/ --cov=firestarter --cov-fail-under=70` → 2106 passed,
  174.58 s, 85.42%
- `.venv311/bin/mypy firestarter/_scratch_probe.py` (probe, file removed) and
  `mypy firestarter/main.py firestarter/cli_handlers.py` → Success
- Exhaustive `os.walk` memory-tooling search over both sub-repos
- `grep --version` → ugrep 7.8.4; `python3 -V` → 3.12.14; per-venv `python -V`

### Secondary (MEDIUM confidence)
- None. No web sources were consulted; every claim is grounded in this repository.

### Tertiary (LOW confidence)
- A1 (Click exit-code values) — training knowledge, consistent with D-10's stated reasoning, not
  re-read from the installed package.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; every library verified present in `pyproject.toml`
- Architecture: HIGH — every seam read at cited lines; the one gap (abort plumbing) is stated as a gap
- Pitfalls: HIGH — Pitfalls 1, 6, 7, 8 are measured or run; 2, 3, 4, 5 are read from source
- Memory measurement: HIGH — measured, with the noise floor and the separation both quantified
- Corpus design: MEDIUM-HIGH — the inputs and traps are verified; the parametrised-vs-property
  recommendation is judgement (A2)

**Research date:** 2026-09-20
**Valid until:** 2026-10-20 (30 days — the codebase is the source of truth and moves only with this
milestone; re-verify line numbers if Phase 202 planning slips past a merge of v1.40's three PRs)
