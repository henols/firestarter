# Phase 54: Even-Block Data Transfers (full-buffer-aligned host→fw chunks) - Context

**Gathered:** 2026-06-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 54 makes the **host→fw write/verify data block** a full, **even, buffer-sized block**
(512 on Uno/uno328pb, 1024 on Leonardo) instead of today's `buffer − 2` (510 / 1022), so a
chip-sized transfer divides into **whole blocks with no odd-sized final remainder chunk** — saving
one write round on a full chip (a 65536-byte image is 128×512 or 64×1024 exactly, vs 128×510 + a
256-byte partial last write today). It does this by **decoupling the on-wire data-block size from
the COBS decode-buffer cap** while keeping the Phase 52 lockstep contract **green at the new block
size** (golden vectors regenerated in lockstep — see D-01/D-09 on contract mutability).

**The constraint being loosened (verified in code):** the firmware decoder
(`rurp_communication_read_data` in `rurp_serial_utils.cpp`) decodes COBS **in-place into
`data_buffer[DATA_BUFFER_SIZE]`**, caps committed payload at `DATA_BUFFER_SIZE − 1` (the CR-01
NUL-slot reservation — `data_buffer` doubles as a NUL-terminated C string on the **command/JSON**
path), and holds CRC8 in a 1-byte lookahead. The host (`eprom_operations.py::_calculate_buffer_size`,
~line 163) therefore sizes chunks at `advertised_buffer − 2`. Phase 54 changes the chunk-size ↔
decode-cap relationship so a full block fits.

**In scope:**
- Host→fw **write AND verify** data blocks transfer at the full even buffer size — no `buffer − 2`
  reduction — verified on the wire (frame sizes) on Uno + Leonardo.
- Decouple the on-wire data-block size from the COBS decode-buffer cap (mechanism chosen by research —
  D-01).
- Firmware identity string advertises an **explicit effective-decode-capacity field** so the host
  sizes chunks dynamically/per-board with no hardcoded constant (D-04).
- Keep the Phase 52 lockstep contract + round-trip tests green at the new block size; pin a
  full-buffer round-trip regression (D-07).
- Post-change RAM-fit report on Uno + uno328pb as a hard close gate (D-08).

**Out of scope (do NOT pull forward):**
- **The fw→host read path** — EPROM reads already transfer full-buffer blocks over the unchanged
  `MSG_DATA_CHUNK` magic-preamble framing (Phase 50 D-06). Phase 54 touches only the **write-receive
  (host→fw) decode path**. Do not re-frame reads.
- **WR-01 frame-level decoder byte-wait deadline** — a distinct decoder *behavior* change (see Deferred);
  not part of even-block sizing even though Phase 54 edits the same decoder.
- **Block-level retransmit / ACK** — still the Phase 50 D-01 fail-fast posture; not added here.

</domain>

<decisions>
## Implementation Decisions

### Decoupling mechanism (the crux)
- **D-01: Mechanism is research's call — capture all candidates, RESEARCH.md scores + recommends,
  planner locks.** Candidates to evaluate:
  1. **Data-path NUL-skip (zero-RAM, promising):** lift the `DATA_BUFFER_SIZE − 1` NUL-slot
     reservation ONLY on the write-receive path (raw EPROM bytes need no C-string NUL); CRC8 stays in
     lookahead (never written). A full `DATA_BUFFER_SIZE` payload then fits `data_buffer[DATA_BUFFER_SIZE]`
     exactly with **zero RAM growth**; the command/JSON path keeps `DATA_BUFFER_SIZE − 1`.
     **Research must confirm `data_buffer` is never read as a NUL-terminated string on the write-receive path.**
  2. **Grow the decode buffer** to hold a full block + reservation (roadmap option a) — spends scarce
     Uno RAM against the ~545 B free-RAM ceiling.
  3. **CRC8 (and/or length) out-of-band** so it never rides the lookahead (roadmap option b).
- **D-02: Breaking the frame contract is PERMITTED for Phase 54.** Operator (2026-06-04) explicitly
  relaxed the Phase 49/52 "frozen contract" status for this phase: CRC8-out-of-band and frame-layout
  changes are on the table if research finds them best. "Green" (SC4) means the lockstep contract +
  golden vectors are **updated together** at the new size — NOT that the bytes are unchanged.
- **D-03: Optimise for "as dynamic as possible."** Operator preference: prefer a board-parameterized /
  runtime-negotiated solution with **no hardcoded per-board constants**; the full-block size derives
  from the firmware-advertised capacity at runtime. No tie-breaker priority imposed on research beyond
  this dynamism preference (RAM, contract stability, and diff risk weighed on merits).

### Firmware advertisement / where the −2 dies
- **D-04: Firmware advertises an explicit effective-decode-capacity field.** Extend the identity
  string (today `"<ver>:<board>:<DATA_BUFFER_SIZE>"`) with a max-data-chunk field
  (e.g. `"<ver>:<board>:<buf>:<maxchunk>"`); the host uses **exactly** what the firmware reports as
  the decodable data-block size. This makes the buffer-RAM-size ↔ usable-chunk decoupling explicit on
  the wire and future-proof. The existing `_calculate_buffer_size()` `−2` reduction is removed in
  favour of the advertised value. (Exact field name/format = planner discretion; the existing
  split-on-`:` parsing is the precedent.)

### Breaking-change / lockstep posture
- **D-05: Beta lockstep, no mixed-version interop.** Carries Phase 50 D-03: host + firmware upgrade
  together on `v1.10-serial-transport-hardening`; **no support for old-FW × new-host pairings**, so the
  host may assume the new capacity field is present (no fallback branch, no graceful `buf−2` degrade).
  Document the breaking wire change. Beta-only; nothing promoted to stable without operator authorization.

### Verification gates
- **D-06: Verify leg moves with the write leg.** Both write and verify send host→fw data blocks through
  the same chunk-sizing path; the full-buffer change covers both (confirm in implementation, not a
  separate mechanism).
- **D-07: Pin a full-buffer round-trip regression (SC4).** Lean on the proven Phase 52 mechanism —
  extend the vendored `frame-vectors` golden-vector corpus (which already carries 512 & 1024 all-`0xFF`
  / all-`0x00` data blocks) with full-buffer-as-data-CHUNK round-trip vectors at the new even size, so
  the same per-repo drift gate pins it in both repos. A lightweight assertion that a 64 KB image
  divides into whole even blocks with **no remainder chunk** is welcome. (Exact test shape = Claude's
  discretion per D-09.)
- **D-08: RAM report is a hard phase-close gate (SC3).** Capture `pio run -e uno` (and uno328pb) RAM
  reports and assert under the ~545 B free-RAM ceiling as a hard close criterion — **even if the chosen
  mechanism is the zero-growth data-path NUL-skip** (D-01 candidate 1). Mirrors Phase 50's post-change
  RAM report.

### Claude's Discretion
- **D-09:** Exact regression-test shape and home (extend `frame-vectors` corpus vs a dedicated EVEN
  test vs both) — operator left this to Claude. Recommendation: extend the Phase 52 corpus + add a
  small no-remainder/division assertion.
- Exact identity-string capacity-field name and format (D-04).
- Internal decoder/encoder naming and the precise decode-in-place cap parameterization for the chosen
  mechanism (D-01), provided the Uno RAM gate (D-08) holds.
- Whether to record measured on-wire frame sizes as quantitative evidence for SC1.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The contract being modified (read FIRST — Phase 54 LOOSENS the CR-01 cap; per D-02 the frame layout is mutable)
- `.planning/v1.10-FRAMING-DECISION.md` §4 — frozen frame contract (`[COBS(payload + CRC8)][0x00]`,
  CRC8 placement, atomic-write mandate). The byte-exact contract Phase 54 may change at the new block
  size; §4.5 RAM confirmation is the ceiling D-08 re-checks.
- `.planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-CONTEXT.md` —
  origin of the CR-01 `DATA_BUFFER_SIZE − 1` NUL-slot cap + the decode-in-place algorithm Phase 54
  loosens; D-01 fail-fast resync (preserved); D-06 (reads stay on `MSG_DATA_CHUNK` — out of scope here).
- `.planning/phases/52-lockstep-contract-round-trip-tests/52-CONTEXT.md` — the golden-vector / vendored
  `frame-vectors` mechanism D-07 extends; D-07 there pinned `CMD_FRAME_MAX` (the command-path cap that
  must stay correct when the data-path cap changes).
- `.planning/phases/53-byte-exact-bench-verification-hardware-gated/53-CONTEXT.md` — the per-board buffer
  negotiation Phase 54 builds on (FW advertises `DATA_BUFFER_SIZE`; host sizes chunks).

### Requirements & roadmap
- `.planning/ROADMAP.md` — Phase 54 entry (Goal + 4 Success Criteria + Depends-on Phases 50/51/52/53).
- `.planning/REQUIREMENTS.md` — Phase 54 requirement is **TBD** (define in planning, e.g. EVEN-01).

### Code to change — firmware (`v1.10-serial-transport-hardening` branch in `firestarter/`)
- `firestarter/src/boards/rurp_serial_utils.cpp` — `rurp_communication_read_data()` (decode-in-place,
  CR-01 cap ~`DATA_BUFFER_SIZE − 1`, CRC8 lookahead, drain-to-`0x00` resync). The cap/mechanism subject
  of D-01.
- `firestarter/include/firestarter.h` — `DATA_BUFFER_SIZE` (line 17, 512 default; 1024 Leonardo),
  `CMD_FRAME_MAX` (line 24), and the `FW_VERSION` identity string (lines 26-35, the `:<DATA_BUFFER_SIZE>`
  field D-04 extends).

### Code to change — host (`v1.10-serial-transport-hardening` branch in `firestarter_app/`)
- `firestarter_app/firestarter/eprom_operations.py` — `_calculate_buffer_size()` (~line 163, the
  `fw_buf − 2` reduction D-04 replaces with the advertised effective capacity); `_main_phase_send_data`
  (write send path, ~line 388) where `cobs_encode(data_chunk + crc8)` is built.
- `firestarter_app/firestarter/serial_comm.py` — `firmware_buffer_size` capture from the identity
  string (~line 114-118); add the new capacity field parse (D-04).
- `firestarter_app/firestarter/frame_parser.py` — `cobs_encode` / `_crc8_ccitt` (reused; touched only
  if D-01 picks CRC8-out-of-band).

### Lockstep / regression mechanism (D-07)
- `firestarter/tools/catalog/frame-vectors.toml` + `firestarter_app/tools/catalog/frame-vectors.toml` —
  the vendored golden-vector catalog (byte-identical both repos) to extend with full-buffer round-trip
  vectors; each repo's `codegen.py` + `<regen> && git diff --exit-code` drift gate pins it.

### Bench / RAM gate (D-08)
- `pio run -e uno` and the uno328pb env — RAM report; ~545 B free-RAM ceiling per Phase 50 D-04 /
  FRAMING-DECISION §4.5.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Per-board buffer negotiation** (Phase 53) — FW already advertises `DATA_BUFFER_SIZE` in the identity
  string; host already parses it into `firmware_buffer_size`. D-04 extends this exact channel rather than
  inventing a new one.
- **`frame-vectors` golden-vector catalog + codegen drift gate** (Phase 52) — already carries 512 & 1024
  data blocks; the natural home for the D-07 full-buffer regression, vendored byte-identical in both repos.
- **Decode-in-place + 1-byte CRC8 lookahead** (`rurp_communication_read_data`) — the algorithm whose
  NUL-slot reservation is the single thing standing between `buffer − 2` and a full block (D-01 candidate 1).

### Established Patterns
- **Identity-string split-on-`:`, ignore trailing fields** — older hosts already tolerate extra fields,
  the precedent for the D-04 capacity field (though D-05 means no old-host support is required).
- **`data_buffer` doubles as a NUL-terminated C string on the command/JSON path** — the *reason* the cap
  is `DATA_BUFFER_SIZE − 1`; this is exactly why a data-path-only NUL-skip (D-01 candidate 1) can be
  zero-cost, and why research must verify the write-receive path never treats `data_buffer` as a string.
- **Breaking lockstep upgrade, no mixed-version interop** — v1.2 Message-ID + Phase 50 D-03 precedent;
  D-05 follows it.

### Integration Points
- `_calculate_buffer_size()` (host) ↔ identity-string capacity field (firmware) — the dynamic
  negotiation seam D-03/D-04 make authoritative; no hardcoded per-board chunk constant survives.
- The chosen decode-cap change must keep the Phase 52 lockstep contract green (regenerate vectors,
  D-07) and the command/JSON path's `DATA_BUFFER_SIZE − 1` cap intact.

</code_context>

<specifics>
## Specific Ideas

- The motivating arithmetic: on a 65536-byte chip, 510-byte chunks = 128×510 + a 256-byte partial last
  write (one extra round trip); a full 512-byte even block = 128×512 exactly, no remainder. SC1/SC2 are
  about removing that remainder chunk and the round it costs.
- Operator's two steers (2026-06-04): **(1)** breaking the frame contract is acceptable here — don't let
  the Phase 49/52 "frozen" status block the cleanest mechanism; **(2)** make it **as dynamic as
  possible** — advertise the effective capacity and derive everything per-board at runtime, no hardcoded
  512/510/1024/1022.
- The data-path NUL-skip is the standout candidate precisely because the write-receive buffer carries
  raw EPROM bytes (no string semantics) — full block, zero RAM. Research validates; planner locks.

</specifics>

<deferred>
## Deferred Ideas

- **WR-01 — frame-level deadline on the firmware COBS decoder byte-wait**
  (`.planning/todos/pending/cobs-decoder-framelevel-deadline-wr01.md`) — a decoder *behavior* change.
  Phase 54 edits the same decoder, making it the natural future home, but it is distinct from even-block
  sizing and was not raised here. Belongs to a dedicated fix.
- **CRC8-out-of-band as a permanent contract** beyond what's needed for even blocks — only adopt if D-01
  research picks it on merits; not a standalone goal.

### Reviewed Todos (not folded)
- **WR-01 (frame-level decoder deadline)** — reviewed; not folded. Reason: behavior change, not
  even-block sizing; out of EVEN scope despite touching the same decoder.
- **`avrdude-mcu-detection-fallback`** + **`w27c512-eeprom-misclassification`** — unrelated to transport
  framing / block sizing; no Phase 54 overlap.

</deferred>

---

*Phase: 54-even-block-data-transfers-full-buffer-aligned-host-fw-chunks*
*Context gathered: 2026-06-04*
