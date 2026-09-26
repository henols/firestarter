# Phase 48: COBS Evaluation + Post-RCA Cleanup + Milestone Close — Research

**Researched:** 2026-06-01
**Domain:** Serial framing evaluation (COBS-01) + Python mypy strict typing (TYPE-01) + milestone-close procedure
**Confidence:** HIGH (serial data-path verified against live code; mypy errors measured directly; watermark and branch state confirmed from current working tree)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**COBS-01 — Serial Robustness Evaluation**
- D-01: PacketSerial-the-library = REJECT (locked, not re-openable). RAM-blocked on Uno.
- D-02: Re-open the robustness investigation FROM SCRATCH — fresh comparative survey, lightweight alternatives. Do not merely formalize the 2026-05-27 todo.
- D-03: No preset candidate list — researcher surveys the field.
- D-04: BINDING FILTER = must fit the Uno RAM budget (no second ~512 B encode buffer; must stream or encode in-place). `0x00`-vs-bus-aliasing is a secondary correctness filter.
- D-05: Expected outcome = reject-library / defer-the-resync-concept, but genuinely re-derivable. Keep CRC8-CCITT regardless.
- D-06: Decision doc home = standalone `.planning/v1.9-COBS-DECISION.md` (ADR-style).

**TYPE-01 — Lift the eprom_operations.py mypy ring-fence**
- D-07: Target = FULL strict parity. Move `firestarter.eprom_operations` into the Phase-42 strict-island block (~L131 in pyproject.toml), alongside the other 8 v1.8 modules.
- D-08: Strictly behavior-preserving. Annotations/casts/guards only. Order of preference: (1) behavior-preserving annotation, (2) single documented `# type: ignore[code]`, never (3) logic change.
- D-09: Hard-gated on Phase 46 (read path fixed). Research is fine now.

**Branch Promotion & Milestone Close**
- D-10: Coordinated lockstep beta tag (e.g. `3.0.0b8`) on BOTH sub-repos.
- D-11: Beta-only promotion — sub-repos merge to `beta`; meta merges to `main`. No stable `3.0.1` this milestone.
- D-12: Beta promotion NOT hard-gated on a perfect Phase 47 acceptance pass.

### Claude's Discretion
- COBS decision doc internal structure / ADR format.
- Exact beta tag number (`3.0.0b8` assumed; confirm against actual prior tags at cut).
- MILESTONES.md v1.9 entry structure (must cover RCA findings, fix summary, acceptance result, COBS decision).
- Execution order of the three workstreams.

### Deferred Ideas (OUT OF SCOPE)
- Adopting any COBS/lightweight-framing layer — explicit non-goal of v1.9.
- Stable `3.0.1` promotion — deferred to operator authorization (D-11).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| COBS-01 | Evaluate COBS framing/resync on the serial data path; record adopt/defer/reject verdict with rationale referencing the current serial data-path shape post-v1.8 | COBS survey section below; streaming encoder analysis; Uno RAM verification (73.4% used, 545 B free) |
| TYPE-01 | Lift `eprom_operations.py` mypy strict-mode overrides; move module into the Phase-42 strict-island block; fix all surfaced strict errors; suite stays green | Error catalog: 53 strict errors measured; error category breakdown; pyproject.toml block structure confirmed |
</phase_requirements>

---

## Summary

Phase 48 closes v1.9 with three independent workstreams: a from-scratch serial framing evaluation (COBS-01), a mechanical mypy strict-mode upgrade (TYPE-01), and the milestone documentation + branch promotion. Research effort is weighted heavily toward COBS-01 — the other two are well-understood mechanical tasks.

**COBS-01 verdict, re-derived:** The from-scratch survey confirms the `serial-cobs-resync-data-path.md` conclusion but with a corrected understanding of the streaming approach. No off-the-shelf library fits the Uno RAM+frame-size constraints without either (a) a second ~514-byte encode buffer (PacketSerial, cobs-c, nanocobs standard mode) or (b) re-chunking frames to ≤254 bytes (SerialTransfer, nanocobs tinyframe, COBS-CPP). The streaming-to-Serial insight (emit encoded bytes directly without materializing the COBS form) eliminates the second-buffer problem and the 254-byte cap simultaneously, but produces ~40 lines of hand-rolled code — making the custom path smaller and less disruptive than any library adoption. The SERIAL_ON_IO `0x00` bus-aliasing risk on the Uno (PD0 doubles as UART RX and data-bus bit 0) is real and non-trivially proven safe. The "resync on garbled byte" win is genuine but the 2-second timeout desync has not been observed in the field. Combined with the milestone-sized dual-repo rewrite cost, the verdict is: **library = REJECT; custom streaming path = DEFER to a future protocol-quality milestone; keep existing framing + CRC8-CCITT intact.**

**TYPE-01:** mypy strict mode surfaces 53 errors in `eprom_operations.py` (measured live against current codebase). The dominant categories are `[no-untyped-def]` (missing annotations), `[type-arg]` (bare `dict`/`Callable` without type parameters), and `[union-attr]` (accessing `.send_ack()` etc. on `self.comm: SerialCommunicator | None`). The `[union-attr]` errors are GATE-1.8d-sensitive: many occur inside methods that are only called from within a `with self._operation_context(...)` block where `self.comm` is guaranteed non-None by the context manager's yield guard, making a narrowing assert or `assert self.comm is not None` the behavior-preserving fix (not a logic change). The one genuine code issue is `checksum.to_bytes(1)` missing the `byteorder` argument (Python 3.9 requires `to_bytes(1, "big")`) — adding `"big"` is purely behavior-preserving. The watermark is currently 26 (at watermark). After moving `eprom_operations` to the strict island, the watermark will need updating.

**Milestone close:** The next beta tag in sequence is `3.0.0b8` (confirmed: `firestarter` sub-repo latest tag = `3.0.0b6`; `firestarter_app` latest = `3.0.0b7`; both sub-repos are on `v1.9-read-bug-rca` branch, ahead of `beta`). The v1.8 MILESTONES.md entry is the format precedent for v1.9.

**Primary recommendation:** Execute COBS-01 first (independent, produces the decision doc), then TYPE-01 after Phase 46 ships, then milestone close after Phase 47.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| COBS evaluation / decision doc | Planning artifacts (meta-repo) | — | Output is a `.planning/v1.9-COBS-DECISION.md` ADR; no code change this milestone |
| Serial framing (existing) | Firmware (`rurp_serial_utils.cpp`) | Host (`serial_comm.py`, `frame_parser.py`) | Dual-repo lockstep; CRC8 lives in both tiers; GATE-1.8d ring-fence guards host read path |
| mypy strict typing (TYPE-01) | Host app (`firestarter_app/`) | pyproject.toml config | Pure annotation change; no firmware touch |
| Milestone documentation | Meta-repo (`.planning/MILESTONES.md`) | — | MILESTONES.md lives only in meta-repo |
| Branch promotion | Both sub-repos → `beta`; meta → `main` | — | Coordinated lockstep tag per D-10/D-11 |

---

## Standard Stack

Phase 48 installs NO new external packages. All work uses the existing toolchain.

### Existing Toolchain (confirmed present)
| Tool | Version | Purpose | How Used in Phase 48 |
|------|---------|---------|----------------------|
| `mypy` | ≥2.1.0 (per pyproject.toml) | Static type checking | Run on `eprom_operations.py` during TYPE-01; watermark updated |
| `pytest` | ≥8.0 | Test suite | Confirm suite stays green after TYPE-01 changes |
| `ruff` | ≥0.15.14 | Linting + formatting | Any annotation additions must pass ruff |
| `pio run -e uno` | PlatformIO | Firmware build | Confirm RAM/flash baseline for COBS-01 decision |

### No New Libraries
COBS-01 is a decision document only — no firmware or host code changes. TYPE-01 is annotation-only changes to `eprom_operations.py` and `pyproject.toml`. No packages are installed.

---

## Package Legitimacy Audit

No external packages are installed in this phase.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| *(none)* | — | — | — | — | — | N/A — no installs this phase |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram — Current Serial Data Path

```
host (Python)                          firmware (C++)
─────────────────────────────────────────────────────────────────
JSON command (ASCII, `{`-prefixed)  →  firestarter.cpp:162-172
                                       peek for `{`; discard junk

host→fw data block                  →  rurp_serial_utils.cpp:44-79
  [len_u16 big-endian][xor][payload]   2 s timeout; xor checksum

fw→host data block                  ←  rurp_serial_utils.cpp:81-93
  [len_u16][xor][payload]              same structure

fw→host log/telemetry frame         ←  rurp_serial_utils.cpp:92-224
  [0xAA55AA55][len_u16][id]            magic preamble + CRC8-CCITT
  [params][crc8][0x0A]                 poly 0x07, seed 0x00

host demux (all 4 framings)         ←→  serial_comm.py:_read_and_parse_lines
  magic-preamble dispatch                (GATE-1.8d ring-fence — DO NOT MODIFY)
  CRC8-CCITT verify                     frame_parser.py:_crc8_ccitt

test_messages (Unity)               pins the frame contract between the two repos
```

**SERIAL_ON_IO bus-aliasing (Uno only):** PD0 doubles as UART RX and data-bus bit 0. During programming, `rurp_set_programmer_mode()` switches PD0 to output mode, ends Serial, and sets `com_mode = false`. The strong override `rurp_log_id()` in `uno_rurp_shield.cpp` gate-checks `com_mode` before emitting any frame — so no bytes are emitted while PORTD drives the data bus. A COBS `0x00` delimiter would only appear in frames, which are gated by the same `com_mode` guard. The risk of a bus-driven `0x00` creating a false COBS frame boundary only exists if the framing layer bypasses `rurp_log_id` and writes directly to `SERIAL_PORT` during programmer mode — an architectural constraint, not an unsolvable problem, but one that requires explicit proof for any COBS adoption path. [VERIFIED: live code review of `uno_rurp_shield.cpp` + `rurp_serial_utils.cpp`]

### Recommended Project Structure (Phase 48 outputs)

```
.planning/
├── v1.9-COBS-DECISION.md       # ADR-style COBS evaluation (COBS-01 deliverable)
├── MILESTONES.md               # v1.9 entry appended (milestone-close deliverable)
└── phases/48-*/                # RESEARCH.md + PLAN.md files

firestarter_app/
├── firestarter/eprom_operations.py   # annotations added (TYPE-01)
└── pyproject.toml                    # eprom_operations moved to strict-island block
                                      # watermark comment updated
```

### Anti-Patterns to Avoid

- **Logic change masquerading as annotation:** Any change to a conditional branch, a loop body, or a return value is a GATE-1.8d violation. The only permitted changes are annotations, assert guards, and narrowing casts that do not alter runtime behavior.
- **Blanket `# type: ignore`:** D-08 requires individually-justified, per-error-code ignores. Never `# type: ignore` without the error code and a rationale comment.
- **Adding the module to the wrong pyproject.toml block:** `eprom_operations` must move FROM the `follow_imports = "silent"` block (~L151) INTO the strict-island `[[tool.mypy.overrides]]` block (~L131). Moving it only partially (e.g. removing from silent but not adding to strict) creates a gap.
- **Re-evaluating PacketSerial:** D-01 is locked. The COBS decision doc should reference the D-01 REJECT disposition but not re-argue it.

---

## COBS-01 Research: From-Scratch Survey

### Candidate Enumeration

The survey covers every plausible lightweight serial-resync mechanism for a 250000-baud, 512-byte-max-frame, 2048-byte-RAM AVR system. PacketSerial is excluded per D-01.

#### Candidate 1: SLIP / RFC-1055 Byte-Stuffing

**What it is:** Simple Link-layer IP protocol (RFC-1055, 1988). Two special bytes: `0xC0` (frame end) and `0xDB` (escape). Any `0xC0` in payload becomes `0xDB 0xDC`; any `0xDB` becomes `0xDB 0xDD`. No checksum in the protocol itself.

**Uno-fit analysis:**
- Encoding: streaming — emit one byte at a time, no second buffer. Zero extra RAM beyond a state byte. [ASSUMED — SLIP encoding is inherently streaming; no authoritative embedded library was checked for hidden buffers]
- Frame size: no limit. A 512-byte payload may expand to at most 1024 bytes in the worst case (all bytes are `0xC0` or `0xDB`).
- Resync: `0xC0` delimiter provides packet boundary. A garbled byte corrupts one packet; resync on next `0xC0`.

**`0x00` bus-aliasing concern:** SLIP uses `0xC0` as delimiter, not `0x00`. No collision with bus-driven `0x00`. SLIP avoids the secondary filter entirely.

**CRC8 coexistence:** SLIP has no built-in checksum. The existing CRC8-CCITT layer can be layered on top unchanged — CRC byte appended before SLIP escaping.

**Integration cost:** Requires replacing the existing `[len_u16][xor][payload]` data-block framing and the `[magic_preamble][len_u16][id][params][crc8][0x0A]` log framing with SLIP-escaped equivalents. Dual-repo rewrite of `rurp_serial_utils.cpp` + `serial_comm.py` + `frame_parser.py` + `test_messages` contract. Milestone-sized.

**Verdict:** Fits Uno RAM (streaming). Resync win is real. But integration cost is milestone-sized and adopting COBS this milestone is an explicit non-goal. **DEFER.**

#### Candidate 2: Hand-Rolled Streaming COBS Encoder/Decoder

**What it is:** Custom ~40-line C encoder (firmware side) + ~30-line Python decoder (host side) that stream COBS bytes directly to/from the serial port without materializing the encoded form. No library dependency.

**The streaming-to-Serial insight (from the 2026-05-27 todo, CORRECTION section):** COBS needs to emit `code_byte + run_bytes` groups. If the code byte and run bytes are written directly to `SERIAL_PORT.write()` byte-by-byte as we scan through `data_buffer`, the encoded form never exists in memory simultaneously. RAM cost is 3 local variables (`i`, `run_start`, `run_len`). The 254-byte run limit applies per *internal run*, not per frame — a 512-byte frame is encoded as up to `⌈512/254⌉ + 1 = 3` groups, all streaming.

**Uno-fit analysis:**
- Encoding: streaming to Serial, ~3 bytes stack overhead. Fits. [VERIFIED: streaming logic reviewed; no second buffer needed]
- Frame size: no limit imposed by this approach. 512-byte Uno frames and 1024-byte Leonardo frames both work.
- Resync: `0x00` delimiter provides packet boundary. One garbled byte → corrupt one packet → resync on next `0x00`.

**`0x00` bus-aliasing concern:** The `0x00` delimiter is only emitted by the COBS framing layer, not by the payload encoder. During programmer mode, `com_mode = false` gates all serial output — the delimiter cannot be emitted while PORTD drives the bus. However, a host-driven `0x00` byte (e.g. in the JSON command path or data-block path) that arrives while the firmware is in programmer mode would need explicit handling. This is a solvable architectural concern but requires proof, not assumption. [ASSUMED — the `com_mode` gate analysis is from code review; the host-side timing guarantees would need bench verification]

**CRC8 coexistence:** CRC8-CCITT byte is appended to the payload before COBS encoding. The existing CRC8 table in `rurp_serial_utils.cpp` and `frame_parser.py` is reused unchanged.

**Integration cost:** ~40 lines firmware + ~30 lines Python. Still requires dual-repo rewrite of `rurp_serial_utils.cpp` + `serial_comm.py` + `test_messages` frame contract. Lower LOC than any library but still a coordinated dual-repo change.

**Verdict:** Smallest possible COBS implementation; fits Uno. Integration cost is lower than libraries but still milestone-sized (dual-repo, `test_messages` rewrite). The resync win is real but the 2-second timeout desync has not been reported as a field problem. **DEFER pending field evidence that the resync win justifies the rewrite cost.**

#### Candidate 3: nanocobs (charlesnicholson/nanocobs)

**What it is:** C99 COBS implementation, no malloc, no libc. Two API modes: standard (encodes into separate destination buffer) and tinyframe (in-place, but payload capped at ≤253 bytes). Latest version v0.2.0, February 2026. [VERIFIED: WebFetch from github.com/charlesnicholson/nanocobs confirmed status, API modes, and no-malloc claim]

**Uno-fit analysis:**
- Standard mode (`cobs_encode`): encodes into a separate `COBS_ENCODE_MAX(n)` destination buffer. For n=512, `COBS_ENCODE_MAX(512) ≈ 514` bytes. With 545 B free RAM (see Environment Availability), this does NOT fit. **ELIMINATED by D-04 binding filter.**
- Tinyframe mode (`cobs_encode_tinyframe`): encodes in-place, zero extra RAM — but enforces payload ≤ 253 bytes. A 512-byte frame requires re-chunking into ≤253-byte segments, each with its own CRC and delimiter. This changes the `eprom_operations.py` data-block loop, the firmware's `rurp_communication_read_data` timeout window, and the `test_messages` contract. **Fits Uno RAM but forces re-chunking — higher integration cost than the custom streaming path.**

**CRC8 coexistence:** nanocobs has no checksum. CRC8-CCITT can be layered on top but requires explicit design.

**Verdict:** Standard mode fails Uno RAM filter (D-04). Tinyframe mode fits RAM but forces re-chunking to ≤253 bytes — more LOC and more integration surface than hand-rolled streaming. **ELIMINATE standard mode (D-04 filter). DEFER tinyframe mode as runner-up if library adoption is preferred over hand-rolled code.**

#### Candidate 4: cobs-c + cobs-python (cmcqueen)

**What it is:** C codec (`cobs-c`, MIT, v0.5.0, 2018) paired with Python `cobs` package (PyPI, latest 1.2.2, 2023). Same author — byte-identical COBS encoding. cobs-python requires Python ≥3.10 (confirmed from repository). [VERIFIED: WebFetch from github.com/cmcqueen/cobs-python confirmed version and Python version requirement]

**Uno-fit analysis:**
- C encoder: writes into a separate output buffer — same second-buffer problem as nanocobs standard mode. NOT streaming. **ELIMINATED by D-04 binding filter.**
- Python host side: `cobs.cobs.encode()`/`decode()` — works on Python ≥3.10. Note: cobs-python requires Python ≥3.10; firestarter_app targets Python ≥3.9. **ELIMINATED — Python version incompatibility with pyproject.toml `requires-python = ">=3.9"`.**

**Verdict:** Eliminated on both firmware RAM (D-04) and Python version constraint. [VERIFIED: cobs-python Python requirement from GitHub; pyproject.toml Python constraint from live file]

#### Candidate 5: SerialTransfer + pySerialTransfer (PowerBroker2)

**What it is:** Arduino C++ library (SerialTransfer, latest v3.1.5, July 2025) paired with Python library (pySerialTransfer, latest v2.6.11, PyPI confirmed). Uses CRC-8 poly 0x9B. Payload capped at 1–254 bytes by design (single-byte length field). [VERIFIED: WebFetch from github.com/PowerBroker2/SerialTransfer confirmed 254-byte limit and CRC poly; pip index confirmed pySerialTransfer v2.6.11 exists on PyPI]

**Uno-fit analysis:**
- 254-byte payload cap forces re-chunking of 512-byte frames into ≥2 packets. Changes `eprom_operations.py` loop, firmware `rurp_communication_read_data`, and frame contract.
- Swaps CRC8 poly from 0x07 (current, CCITT) to 0x9B. Breaks `test_messages` suite which asserts poly 0x07 byte-for-byte. Requires rewriting `frame_parser.py` CRC table.
- Replaces ALL framing including the JSON command path — the most disruptive adoption path.

**Verdict:** 254-byte cap; CRC poly swap; replaces all framing. Largest dual-repo diff. **ELIMINATE.** (Still fits Uno RAM via its internal buffering, but cost/benefit is worst of all candidates.)

#### Candidate 6: MIN Protocol (min-protocol/min)

**What it is:** Microcontroller Interconnect Network protocol. Uses CRC32. Has transport-layer retransmission buffers. [ASSUMED — from the todo survey and general knowledge; WebFetch of the GitHub page returned no RAM details]

**Uno-fit analysis:** CRC32 (4 bytes) replaces CRC8 (1 byte) — higher overhead per frame. Transport retransmission buffers require additional RAM — confirmed as "RAM heavy" in the todo survey. With 545 B free RAM on Uno, any retransmission buffer (even minimal) almost certainly collides. [ASSUMED — specific buffer sizes not verified against live code; ELIMINATE based on training-knowledge consensus and todo survey]

**Verdict:** CRC32 overhead; retransmission RAM buffers; overkill for this use case. **ELIMINATE.**

### Comparative Verdict Table

| Candidate | Fits Uno RAM? | Frame ≤ 512 B? | Resync? | CRC8 coexists? | Integration Cost | Verdict |
|-----------|--------------|---------------|---------|----------------|-----------------|---------|
| PacketSerial | No (~514 B buffer) | No | Yes | No | — | LOCKED REJECT (D-01) |
| SLIP/RFC-1055 | Yes (streaming) | Yes | Yes (`0xC0`) | Yes (layer on top) | Milestone-sized dual-repo | DEFER |
| Hand-rolled streaming COBS | Yes (~3 bytes stack) | Yes | Yes (`0x00`) | Yes (layer on top) | Milestone-sized dual-repo; ~70 lines | DEFER |
| nanocobs standard | No (~514 B) | No | Yes | Must add | — | ELIMINATED (D-04) |
| nanocobs tinyframe | Yes (in-place) | ≤253 B only | Yes | Must add | Re-chunk + dual-repo | DEFER (runner-up) |
| cobs-c + cobs-python | No (second buffer) | No | Yes | Must add | — | ELIMINATED (D-04 + Py 3.9) |
| SerialTransfer | Yes (internal) | ≤254 B only | Yes | CRC poly swap | Largest diff | ELIMINATE |
| MIN protocol | Probably No | ~255 B | Yes (CRC32) | CRC swap | — | ELIMINATE |

### COBS-01 Decision: REJECT libraries / DEFER the concept

**Adopt:** No candidate reaches "adopt" — the custom streaming path is the only Uno-fitting, 512-byte-capable option, and it is ~70 lines of hand-rolled code plus a milestone-sized dual-repo rewrite.

**Defer:** The automatic-resync concept is valid. If the 2-second timeout desync is observed in field use, the recommended future path is the hand-rolled streaming COBS encoder/decoder (custom streaming C + Python, ~70 lines, zero extra RAM, no library dependency, CRC8-CCITT preserved). SLIP is a simpler alternative if the `0x00` delimiter concern ever proves architectural (no `0x00` in payload concern with SLIP since it uses `0xC0`).

**Reject libraries:** Every off-the-shelf library either fails the Uno RAM filter (D-04), forces re-chunking to ≤254 bytes, swaps the CRC polynomial, or replaces all framing.

**v1.9-COBS-DECISION.md structure (ADR-style, suggested):**
1. Context — the 4-framing wire map, resync motivation, Uno RAM baseline
2. Decision — REJECT libraries, DEFER concept
3. Consequences — no wire change this milestone; future milestone uses streaming COBS
4. Candidate Survey — per-candidate analysis with Uno-fit verdict
5. Open Questions for future milestone

---

## TYPE-01 Research: mypy Strict Errors in eprom_operations.py

### Current State (verified live)

- **pyproject.toml strict-island block (L131-L145):** Contains 8 modules (`main`, `cli_handlers`, `chip_resolver`, `frame_parser`, `codec`, `address_parser`, `exceptions`, `serial_comm`). `disallow_untyped_defs = true; check_untyped_defs = true`. [VERIFIED: live file read]
- **pyproject.toml non-strict-silenced block (L147-L163):** Contains `firestarter.eprom_operations` + 9 others. `follow_imports = "silent"`. [VERIFIED: live file read]
- **Watermark:** `# mypy_error_watermark = 26` (at watermark — `python tools/check_mypy_watermark.py` reports OK at 26). [VERIFIED: live run]
- **Test suite:** 387 tests pass (including 29 syrupy snapshots). [VERIFIED: `pytest` run]
- **Current Uno RAM:** 73.4% used (1503 / 2048 bytes), 545 B free; Flash 69.7% (22492 / 32256 bytes). [VERIFIED: `pio run -e uno` live run — slight increase from the 553 B free baseline in the todo, due to Phase 44 read-timing knobs addition]

### Strict-Mode Error Catalog (53 errors measured directly)

Running `mypy firestarter/eprom_operations.py --strict --no-error-summary` (note: Python 3.9 version warning from mypy 2.1.0 is cosmetic; errors are real):

| Category | Count | Representative Lines | Behavior-Preserving Fix |
|----------|-------|---------------------|------------------------|
| `[no-untyped-def]` — missing annotation | 16 | L60, L78, L105, L111, L122, L132, L143, L227, L252, L259, L322, L395, L479, L594, L739 | Add return type / parameter type annotations |
| `[type-arg]` — bare generic `dict`/`Callable`/`Dict` | 15 | L158, L174, L179, L230, L262, L400, L453, L502, L705, L807, L843, L879, L915, L938, L958 | `dict[str, Any]` or `Dict[str, Any]` (keep UP035 noqa for 3.9 compat) |
| `[union-attr]` — `self.comm: SerialCommunicator \| None` access | 9 | L306, L310, L334, L346, L369, L390, L393, L420, L438 | `assert self.comm is not None` at start of each affected method (behavior-preserving since the methods are unreachable without prior `_setup_operation` success) |
| `[no-untyped-call]` — calling untyped helper | 9 | L223, L250, L269, L300, L329, L650, L774, L802, L838 | Annotate `ClassProgressHandler`, `_disconnect_programmer`, `extract_hex_to_decimal`, `get_value` |
| `[no-any-return]` — returning `Any` from typed function | 2 | L320, L355 | Add explicit `Optional[str]` return type or cast |
| `[call-arg]` — missing positional arg | 1 | L381: `checksum.to_bytes(1)` → `checksum.to_bytes(1, "big")` | Add `"big"` (Python 3.9 requires it; Python 3.11+ made it optional; this IS a bug fix, but behavior-identical on any byte value ≤ 255) |

**The `[call-arg]` at L381 is the only genuine code issue** (not purely an annotation change). `checksum.to_bytes(1)` works on Python 3.11+ but raises `TypeError` on Python 3.9 (the declared minimum). Adding `"big"` is the correct fix. This is behavior-preserving: for values 0–255, `to_bytes(1, "big")` == `to_bytes(1, "little")` (single byte, no endianness effect).

### union-attr Pattern Analysis

The 9 `[union-attr]` errors all arise from `self.comm` being declared as `SerialCommunicator | None`. The methods that access `self.comm` directly are:

- `_execute_phase()` — only called from `_run_state_machine()`, which has an early return on `not self.comm` (L267-268)
- `_main_phase_simple()`, `_main_phase_send_data()`, `_main_phase_read_data()` — only called from within the `if main_phase_handler:` branch of `_run_state_machine()`, where `self.comm` is guaranteed non-None

The behavior-preserving fix is `assert self.comm is not None` at the top of each affected method. Precedent: `serial_comm.py` uses `# type: ignore[union-attr]` on the GATE-1.8d ring-fenced read-loop lines (L254, L286, L301, L316, L409). For `eprom_operations.py` methods where the None-case is architecturally unreachable (not just ring-fenced), `assert self.comm is not None` is preferable to `# type: ignore` because it documents the invariant and fails loudly if violated.

**`_disconnect_programmer()` (L252) annotation:** This method accesses `self.comm` safely (it null-checks before using). Adding `-> None` annotation fixes the `[no-untyped-def]` error; the `[no-untyped-call]` errors at call sites resolve once the callee is annotated.

### pyproject.toml Change (exact)

Move `"firestarter.eprom_operations"` from the `[[tool.mypy.overrides]]` block with `follow_imports = "silent"` (~L151) to the strict-island `[[tool.mypy.overrides]]` block (~L134), alongside the existing 8 modules. Update the `# mypy_error_watermark = 26` comment to the new count (expected: 26 − 10 current visible errors + residual strict ignores ≤ 2, so likely 16–18; must be measured after fixes are applied).

**Also remove** `"firestarter.eprom_operations"` from the `follow_imports = "silent"` block (currently at L152). If left in both blocks, the last matching block wins (mypy processes overrides top-to-bottom, last match wins) — leaving it in the silent block last would silently override the strict island. [VERIFIED: pyproject.toml block structure confirmed from live file; mypy docs behavior `[ASSUMED]` but consistent with how Phase 42 strict-island was set up]

### ClassProgressHandler as Untyped Caller Source

`ClassProgressHandler` is defined in `eprom_operations.py` itself (L104-L145) and is entirely unannotated. Adding return-type annotations to its 4 methods (`start`, `update`, `set_progress`, `close`) eliminates both the `[no-untyped-def]` errors on those methods AND the `[no-untyped-call]` errors at the 5 call sites in `EpromOperator`.

### extract_hex_to_decimal and get_value (Cross-Module Calls)

`extract_hex_to_decimal` in `firestarter/utils.py` is unannotated and still in the `follow_imports = "silent"` block. The `[no-untyped-call]` error at L983 can be resolved with either:
1. Annotating `utils.py` (not in scope for TYPE-01 — utils.py is not moving to strict island this phase)
2. A single `# type: ignore[no-untyped-call]` with justification: `# type: ignore[no-untyped-call]  # utils.py not yet in strict island`

Similarly for `get_value` (external to eprom_operations — from `firestarter/hardware.py` or similar). Use option 2 (documented ignore) per D-08 escape hatch.

---

## Milestone Close Research

### Beta Tag Sequence (confirmed)

| Sub-repo | Current branch | Latest beta tag | Next tag |
|----------|---------------|-----------------|----------|
| `firestarter` (firmware) | `v1.9-read-bug-rca` | `3.0.0b6` | `3.0.0b8` |
| `firestarter_app` (host) | `v1.9-read-bug-rca` | `3.0.0b7` | `3.0.0b8` |
| meta-repo | `v1.9-read-bug-rca` | — (meta doesn't tag) | merge to `main` |

[VERIFIED: `git tag --sort=-creatordate` on both sub-repos; both on `v1.9-read-bug-rca` branch]

Both sub-repos ship with v1.9 changes (firmware: read-timing knobs from Phase 44 + fix from Phase 46; host: TYPE-01 annotations + Phase 44 knob params), so `3.0.0b8` is the next lockstep tag (skipping `b7` on firmware, which was `firestarter_app`-only in v1.8).

### MILESTONES.md v1.9 Entry Format

The v1.8 entry (confirmed read, ~100 lines) is the closest format precedent. The v1.6 entry is the "diagnostic + revert" close precedent (partial success). The v1.9 entry must cover:

1. **Header line** — phases, plans, timeline, ship tag, commit counts (meta + both sub-repos)
2. **Delivered** — RCA findings (Bug A = Rev 0 shield read-path fault, read-strobe-causal; Bug B TBD from Phase 45), fix summary (Phase 46 short-strobe or equivalent), acceptance gate result (Phase 47)
3. **Key Accomplishments** — one entry per phase (44 through 48)
4. **COBS decision** — reference to `v1.9-COBS-DECISION.md`
5. **TYPE-01 outcome** — mypy strict on 9 modules (8 + eprom_operations)
6. **Branch Strategy** — sub-repos `v1.9-read-bug-rca` → `beta` merge; meta → `main`; stable `3.0.1` deferred per D-11
7. **Stats table** — phases, plans, requirements, commits, test count, mypy strict modules, coverage

**Conditional content:** Phases 45/46/47 outcomes are unknown at planning time (they haven't been executed). The milestone-close plan must include a task to fill in these fields after Phase 47 completes. The planner should structure the MILESTONES.md task as "fill in the template including Phase 45-47 outcomes from their summary files."

### Branch Promotion Procedure (per v1.6/v1.8 precedent)

1. Autonomous: write MILESTONES.md entry, update STATE.md, commit to meta-repo
2. Autonomous: archive phase directories (`.planning/v1.9-archive.sh` mirroring v1.8/v1.6 pattern)
3. Operator-authorized HUMAN-UAT: merge `v1.9-read-bug-rca` → `beta` in `firestarter` sub-repo; cut `3.0.0b8` tag; merge `v1.9-read-bug-rca` → `beta` in `firestarter_app` sub-repo; cut `3.0.0b8` tag; merge meta-repo `v1.9-read-bug-rca` → `main`

**No stable promotion in this plan** — stable is operator-gated (D-11).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Counting mypy errors | Custom parser | `python tools/check_mypy_watermark.py` | Already exists; reads watermark from pyproject.toml comment |
| Type narrowing for `SerialCommunicator \| None` | Complicated isinstance chain | `assert self.comm is not None` | Standard Python narrowing; mypy understands it; zero runtime cost in success path |
| COBS encoding (if ever adopted) | Standard mode with second buffer | Custom streaming encoder (~15 lines) | Only Uno-fitting approach at 512-byte frame size |
| Branch promotion | Manual git commands | Follow the v1.8 Plan 43-03 HUMAN-UAT.md pattern | Established operator-authorized checklist pattern with UAT verification |

---

## Common Pitfalls

### Pitfall 1: Moving eprom_operations to strict island but forgetting to remove it from the silent block

**What goes wrong:** If `firestarter.eprom_operations` remains in the `follow_imports = "silent"` block at L152 AND is added to the strict-island block at L134, mypy applies the LAST matching override. The silent block appears later in the file — the strict-island override is silently defeated.

**How to avoid:** Remove the entry from the silent block atomically with adding it to the strict block. Verify with `mypy firestarter/eprom_operations.py --no-error-summary` — if the strict block is active, you will see errors; if the silent block won, you will see none.

### Pitfall 2: Watermark comment syntax — mypy treated as MISSING if format changes

**What goes wrong:** `check_mypy_watermark.py` uses the regex `r"^\s*#\s*mypy_error_watermark\s*=\s*(\d+)"`. Any deviation (e.g., adding a semicolon, the wrong prefix, or a TOML key instead of a comment) exits with code 2 ("configuration error"), which blocks CI.

**How to avoid:** Keep the watermark as a comment line: `# mypy_error_watermark = N`. Update `N` to the new error count after applying TYPE-01 fixes. Run `python tools/check_mypy_watermark.py` to confirm before committing.

### Pitfall 3: assert-narrowing for self.comm may introduce dead-code warnings if mypy infers it redundant

**What goes wrong:** If mypy can already prove `self.comm is not None` in a particular scope (e.g., inside `_operation_context` after the yield guard), an `assert self.comm is not None` may trigger a `[redundant-assert]` warning in strict mode.

**How to avoid:** Run mypy after adding each assert to confirm it narrows without triggering new errors. If a `[redundant-assert]` appears, the existing narrowing was already correct — remove the assert and use the existing narrowed type directly. Alternatively, narrow at the `EpromOperator` level by using a `@property` that raises on None, but only if the assert approach fails cleanly.

### Pitfall 4: `to_bytes(1)` at L381 — the only genuine runtime bug

**What goes wrong:** On Python 3.9 (the declared minimum), `int.to_bytes(length)` without `byteorder` is a `TypeError`. The existing test suite may not cover the write path with a real file (hardware-gated), so this could pass CI on 3.11+ but fail in production on 3.9.

**How to avoid:** Fix `checksum.to_bytes(1)` → `checksum.to_bytes(1, "big")`. This is behavior-preserving: for a 1-byte value, big-endian and little-endian produce the same byte. Confirm the test suite passes after the fix.

### Pitfall 5: Treating the COBS survey as confirmation rather than derivation

**What goes wrong:** If the decision doc simply restates the 2026-05-27 todo conclusions without re-deriving them from the current code, it fails D-02 (fresh comparative survey) and D-05 (genuinely re-derivable).

**How to avoid:** The decision doc must reference the current Uno RAM baseline (73.4%, 545 B free, measured 2026-06-01) and the current framing code in `rurp_serial_utils.cpp` post-Phase-44. The 2026-05-27 todo is explicitly "starting evidence to re-verify," not the answer.

### Pitfall 6: Milestone-close plan omits Phase 45/46/47 outcome placeholders

**What goes wrong:** The v1.9 MILESTONES.md entry is written before Phases 45/46/47 complete, leaving holes or inaccurate summary lines.

**How to avoid:** Structure the MILESTONES.md task to fill a template that explicitly marks Phase 45-47 fields as "populated from `evidence/` and SUMMARY.md files at close time." The planner should not pre-fill outcome fields that are conditionally determined by future bench work.

---

## Code Examples

### TYPE-01: Adding assert narrowing for self.comm (behavior-preserving)

```python
# Source: Pattern from serial_comm.py strict-island (Phase 42 D-06) + Python narrowing docs
def _execute_phase(
    self, phase_name: str, progress: ClassProgressHandler
) -> Optional[str]:
    """Executes a single phase (INIT or END) of the state machine."""
    assert self.comm is not None  # narrowing: method only called from _run_state_machine after None check
    self.comm.send_ack()
    # ... rest of body unchanged
```

### TYPE-01: Annotating ClassProgressHandler methods

```python
# Source: existing code patterns in Phase 42 strict-island modules
def start(self, total_steps: int) -> None:
    self.total_steps = total_steps
    # ...

def update(self, completed_steps: int) -> None:
    # ...

def set_progress(self, current: int, total: int) -> None:
    # ...

def close(self) -> None:
    # ...
```

### TYPE-01: Fixing to_bytes at L381 (behavior-preserving)

```python
# Source: Python docs — int.to_bytes(length, byteorder) — Python 3.9 requires byteorder
header = (
    b"#" + len(data_chunk).to_bytes(2, "big") + checksum.to_bytes(1, "big")
)
```

### TYPE-01: Documented residual ignore for cross-module untyped calls

```python
# Source: D-08 escape hatch pattern; analogous to Phase 42 D-06 serial_comm.py ignores
result = extract_hex_to_decimal(value)  # type: ignore[no-untyped-call]  # utils.py not yet in strict island; lift when utils moves to strict
```

### COBS streaming encoder (reference — for future milestone decision doc)

```c
// Source: serial-cobs-resync-data-path.md CORRECTION section (2026-05-29)
// Zero-extra-buffer streaming COBS encoder for AVR. Reads data_buffer[0..N-1],
// emits COBS-encoded bytes directly to SERIAL_PORT. RAM cost: ~6 bytes stack.
size_t i = 0;
while (i < N) {
    size_t run_start = i;
    uint8_t run_len = 0;
    while (i < N && data_buffer[i] != 0 && run_len < 254) { run_len++; i++; }
    SERIAL_PORT.write((uint8_t)(run_len + 1));
    SERIAL_PORT.write(&data_buffer[run_start], run_len);
    if (i < N && data_buffer[i] == 0) i++;
}
SERIAL_PORT.write((uint8_t)0x00);  // frame delimiter
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact for Phase 48 |
|--------------|------------------|--------------|---------------------|
| `eprom_operations.py` in non-strict mypy | Move to strict-island block | TYPE-01 (this phase) | 53 strict errors to resolve; watermark update needed |
| PacketSerial drop-in | REJECTED (D-01) | v1.9 planning | Sets the starting point for from-scratch survey |
| 553 B free RAM (Uno, from 2026-05-27 todo) | 545 B free RAM (current, 2026-06-01) | Phase 44 read-timing knobs added | Slightly less headroom; COBS second-buffer constraint unchanged |

**Deprecated/outdated in the todo substrate:**
- The CRUX claim that "in-place COBS ≤ 254 B and 512 B single frame are mutually exclusive" is corrected by the streaming-to-Serial insight: the 254 B limit is per internal COBS *run*, not per frame. Streaming eliminates the second-buffer requirement for any frame size. The RESEARCH.md for Phase 48 supersedes this framing.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | SLIP encoding can be implemented streaming (no second buffer) | COBS survey — Candidate 1 | Low — SLIP is architecturally byte-streaming; confirmed by algorithm description |
| A2 | MIN protocol has retransmission buffers that exceed 545 B free RAM on Uno | COBS survey — Candidate 6 | Low — even if RAM fits, CRC32 overhead alone disqualifies MIN |
| A3 | mypy last-matching-override wins for duplicate module entries in pyproject.toml | TYPE-01 pitfall 1 | Medium — if first-match wins instead, the guidance reverses; verify by testing both |
| A4 | `0x00`-delimiter bus-aliasing is gated by `com_mode` such that no false COBS frame boundaries can occur during programmer mode | COBS survey — Candidate 2 | Medium — code review confirms `com_mode` gates all `rurp_log_id` emissions; host-side timing guarantee requires bench verification |
| A5 | pySerialTransfer on PyPI is the Python counterpart of SerialTransfer Arduino library | COBS survey — Candidate 5 | Low — pip index confirmed version exists; same author (PowerBroker2) confirmed via GitHub |

---

## Open Questions (RESOLVED)

1. **Is the 2-second timeout desync observed in the field?**
   - What we know: The 2-second timeout fires if a length-prefixed data block is interrupted. The desync cascades until the next JSON command peek.
   - What's unclear: Whether this ever manifests during normal bench use (the consistency-check runs are 64KB reads in good conditions).
   - Recommendation: If Phase 46/47 bench sessions ever see timeout desync, document it in the COBS decision doc as field evidence pushing toward the resync concept.
   - **RESOLVED:** No field reports exist; the COBS decision proceeds without field evidence — the resync win is deferred to a future milestone on that basis.

2. **Will the watermark after TYPE-01 fixes land at or below 26?**
   - What we know: Currently 26 errors visible (watermark = 26). Moving `eprom_operations` to strict island adds ~53 errors visible to mypy --strict, but the non-strict modules that call into `eprom_operations` may produce additional cross-module type errors.
   - What's unclear: Exact post-fix watermark.
   - Recommendation: Run `python tools/check_mypy_watermark.py` after each TYPE-01 fix batch to track progress; set the new watermark to the measured post-fix count.
   - **RESOLVED:** Measured at execution time via `tools/check_mypy_watermark.py`; the watermark is updated to the post-fix count in 48-02.

3. **Phase 45/46/47 outcomes for the MILESTONES.md entry**
   - What we know: Phase 44 = Bug A RCA complete (Rev 0 shield read-path fault, read-strobe-causal). Phase 45-47 are not yet executed.
   - What's unclear: Bug B root cause, fix candidate, acceptance gate result.
   - Recommendation: Structure the milestone-close plan to populate Phase 45-47 fields from their SUMMARY.md and evidence files at Phase 48 execution time.
   - **RESOLVED:** Populated from the Phase 45/46/47 SUMMARY.md files at 48-03 close time via the placeholder mechanism in 48-03 Task 1.
