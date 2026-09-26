# Phase 52: Lockstep Contract + Round-Trip Tests - Context

**Gathered:** 2026-06-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 52 **proves and pins** the dual-repo COBS framing contract. It does NOT add or
change any transport behavior — the frame contract, codec, and recovery posture were
locked in Phases 49–51. This phase exists to make the firmware (C++) and host (Python)
framing implementations **provably byte-compatible inverses** and to **freeze that contract
in both repos' test suites** so it cannot silently drift.

**What "proven" means here:** for representative payloads — data blocks AND JSON command
frames, including the delimiter-laden and pathological all-`0x00` cases — both directions
round-trip byte-exact: `host-encode → fw-decode` and `fw-encode → host-decode`. The CRC8-CCITT
(poly `0x07`) byte-level contract is asserted byte-for-byte (SC4), and firmware/host constant
parity stays guarded with CI green in both repos.

**In scope:**
- A **shared frozen golden-vector** corpus that anchors host↔firmware byte-compatibility.
- Codegen of that corpus into BOTH sub-repos (vendored-catalog model, mirroring the v1.2
  message-catalog mechanism): C++ PROGMEM header for the Unity suite + Python module for pytest.
- Vector assertions in both repos exercising BOTH legs per vector (encode==frame AND decode==payload).
- Extension of the existing constant-parity test to cover `CMD_FRAME_MAX`.
- A CRC8 known-answer assertion in each suite (SC4).
- Each repo's own CI green (drift gate + vector suite + parity test).

**Out of scope (later phases / non-goals — do NOT pull forward):**
- **Bench / real-hardware byte-exactness** (Uno/Leonardo/uno328pb, fault-injection resync) → **Phase 53** (XACT-01/02/03).
- **Any decoder behavior change**, including WR-01 (frame-level deadline on the firmware decoder
  byte-wait) — that is a behavior change, not a contract test; stays deferred.
- **New framing behavior, mechanism changes, or contract changes** — the contract is frozen
  (Phase 49 ADR §4); this phase only pins it.
- A randomized/fuzz sweep as part of the golden vectors — the corpus is the deterministic
  boundary set; property-style fuzz, if ever wanted, is a separate per-repo test (deferred).

</domain>

<decisions>
## Implementation Decisions

### Carried forward — LOCKED upstream (Phase 49 ADR + Phases 50/51; do NOT re-litigate)
- **Frame contract = `[COBS-encoded(payload + CRC8 byte)][0x00 delimiter]`** — CRC8 appended to
  the raw payload *before* COBS encoding, and is itself COBS-encoded (ADR §4.1/§4.3). Same contract
  on the data path (Phase 50) and command channel (Phase 51). **These tests pin this; they do not change it.**
- **CRC8-CCITT poly `0x07`, seed `0x00`, no reflection, no final XOR**, over the raw payload.
  Existing CRC8 tables reused unchanged both repos (D-05): firmware PROGMEM table + host
  `frame_parser.py` `_crc8_ccitt()`.
- **Atomic single-write** + **full-frame consumption (incl. trailing `0x00`) before parse** (SAFE-01).

### Cross-repo proof mechanism
- **D-01: Shared frozen golden vectors are the cross-repo anchor.** A canonical set of
  `(payload → exact framed bytes)` is the single source of truth. BOTH the firmware Unity suite
  and the host pytest assert against the **same** frozen bytes. If each implementation matches the
  frozen vector, the two implementations match each other transitively — no live cross-toolchain run
  needed (which the submodule structure fights). Chosen over independent-round-trips-plus-synced-constant
  (drift-prone) and a live cross-language harness (needs both toolchains in one CI job, slow/flaky).
- **D-02: Each vector is exercised on BOTH legs in each repo** — `encode(payload) == frame` AND
  `decode(frame) == payload`. One **valid-payload** vector set therefore proves all four directions
  (host↔fw, both ways). This directly pins the `host-encode → fw-decode` leg the phase exists to prove.
- **D-03: The golden set is valid-payload-only.** Negative cases (corrupted-CRC → reject;
  truncated → bounded recovery) stay in the EXISTING per-repo suites
  (`test_cobs_cmd_frame.cpp` already has CRC8-reject + drain-to-`0x00` resync; host `test_cobs.py`).
  The golden set is the positive byte-contract; failure behavior is not couched in the byte-vector format.

### Vector representation + home
- **D-04: Codegen into both repos, mirroring the v1.2 message-catalog mechanism.** A canonical
  vector catalog (e.g. `tools/catalog/frame-vectors.toml`) + a `codegen.py` are **vendored
  byte-identical into each sub-repo's `tools/catalog/`**; each repo's `codegen.py` emits its own
  artifact — a C++ PROGMEM header for the Unity suite and a Python module for pytest. Each repo's
  CI runs `<regen> && git diff --exit-code` as a **drift gate** (proven v1.2 pattern). The
  single-source guarantee is tool-enforced within each repo; cross-repo identity is held by paired
  commits (see D-09 / accepted risk).
- Chosen over a flat hex file read at runtime (each repo needs its own parser; weaker tooling) and
  hand-embedded literals (a literal can be mistyped in one repo with nothing to catch it).

### Golden-vector corpus
- **D-05: Corpus = ROADMAP-mandated cases + COBS-boundary stress.** Concretely:
  - **Mandated:** a representative data block; a representative JSON command frame; a delimiter-laden
    payload (`0x00` scattered through it); the pathological **all-`0x00`** payload.
  - **COBS run-length boundary stress:** **253 / 254 / 255** consecutive non-zero bytes — exactly the
    block boundary where the Phase-50 **CR-01** encoder byte-drop hid. This is the highest-value
    addition: it targets the boundary where framing bugs actually live.
  - **Edge payloads:** empty payload; lone single-`0x00` payload.
  - **Data blocks at BOTH buffer sizes:** 512 B (Uno / uno328pb) and 1024 B (Leonardo), with
    all-`0xFF` and all-`0x00` content.
- Chosen over mandated-cases-only (skips the 254-run class that already produced a real bug) and an
  exhaustive randomized sweep (heavy to freeze as deterministic vectors; better as a separate per-repo
  fuzz test if ever wanted — see Deferred).

### CRC8 byte-level assertion (SC4)
- **D-06:** SC4 is satisfied two ways: (a) the golden frame bytes **embed** the CRC8, so matching a
  vector proves poly `0x07` end-to-end; (b) a small **known-answer test** (fixed input → known CRC8
  byte) in each suite, mirroring the existing independent `ref_crc8` reference already used in
  `test_cobs_cmd_frame.cpp` / `test_rurp_log_id.cpp`. Confirms framing layered on top WITHOUT a
  polynomial change (D-05 upstream).

### Constant-parity guard (SC3)
- **D-07: Extend the existing test, pin `CMD_FRAME_MAX` to the Uno floor.** Add `CMD_FRAME_MAX` to
  the existing skipif-guarded `firestarter_app/tests/test_revision_constants_parity.py` (the proven
  Phase-34/36 TEST-04 pattern). Assert host `CMD_FRAME_MAX == 512` against the firmware Uno
  `DATA_BUFFER_SIZE` floor, with an explicit comment that the firmware macro is **board-parameterized**
  (`#define CMD_FRAME_MAX DATA_BUFFER_SIZE` → 512 Uno/uno328pb, 1024 Leonardo) and that **512 is the
  binding minimum the host must not exceed**. The delimiter `0x00` and CRC8 poly `0x07` are NOT named
  constants — they are pinned by golden vectors + the KAT (D-06), not the parity test.
  - **Note for the planner:** the host hardcoding `512` while firmware uses board-variant
    `DATA_BUFFER_SIZE` was surfaced and judged acceptable for v1.10 (512 floor pinned); it is NOT
    treated as a bug to fix here. If a Leonardo command frame >512 B ever becomes legitimate, revisit.

### CI scope (SC3)
- **D-08: Each repo's own CI, independently.** `firestarter` CI runs the Unity vector suite + the
  codegen drift gate; `firestarter_app` CI runs the pytest vector tests + the parity test + its
  codegen drift gate. No meta-level CI (the meta-repo tracks only `.planning/`). "Green across both
  repos" = verify both sub-repo CIs pass before phase close. Mirrors the v1.2 catalog model.

### Accepted risk
- **D-09: Cross-repo catalog drift is an accepted, paired-commit-mitigated risk.** With per-repo CI
  (D-08) and the vendored-catalog model (D-04), the ONE thing no CI structurally catches is the two
  vendored vector catalogs drifting from each other — and that byte-identity is exactly what makes the
  "shared" golden vectors actually shared. Operator chose per-repo CI over a meta-level catalog-diff
  check (informed call, 2026-06-02). Mitigation: **paired commits in both sub-repos on the
  `v1.10-serial-transport-hardening` branch** — the same lockstep discipline that has held for the v1.2
  `messages.toml` since v1.2. Recorded so it is a conscious call, not a blind spot.

### Claude's Discretion
- Exact catalog filename/format (`frame-vectors.toml` vs `.json`) and the codegen emit shape, provided
  it matches the v1.2 determinism contract (sorted, no timestamps, LF, upper-case hex).
- Exact symbol names for the generated C++ vector array(s) and Python vector module members.
- Where vector assertions live within each suite (extend `test_cobs_*` files vs a new
  `test_frame_vectors` / `test_lockstep_contract` suite) — planner's call.
- Exact set of representative JSON command payloads (e.g. which real `{...}` commands) and the precise
  data-block content patterns beyond the all-`0xFF` / all-`0x00` extremes.
- Whether the KAT input(s) for D-06 reuse an existing fixture or add a dedicated one.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The frozen contract (read FIRST — this is the binding spec the tests pin)
- `.planning/v1.10-FRAMING-DECISION.md` — Phase-49 decision ADR. For Phase 52 specifically:
  - §4.1 — Delimiter + streaming-COBS scheme + atomic-write mandate (the encode shape vectors must match).
  - §4.3 — Frame layout table (`[COBS(payload+CRC8)][0x00]`; CRC8 placement) — the byte-exact contract.
  - §4.4 — CRC8-before-parse security mandate (pinned indirectly: the golden set is valid-only, negative
    cases stay in per-repo suites per D-03).

### Prior phase context (the framing primitives + test substrate these vectors exercise)
- `.planning/phases/51-command-channel-framing-migration-breaking-wire-change/51-CONTEXT.md`
  — command-channel framing decisions; `CMD_FRAME_MAX` / D-06 resync posture; the
  `test_cobs_cmd_frame` Unity suite this phase's vectors complement.
- `.planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-CONTEXT.md`
  — data-path COBS encode/decode + CRC8 helpers; the **CR-01 254-run byte-drop** (the boundary class
  the corpus stress-tests per D-05).
- `.planning/phases/49-framing-mechanism-decision-cobs-0x00-vs-slip-0xc0/49-CONTEXT.md`
  — mechanism-decision context (COBS selected; D-05 keep-CRC8 lock).

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — **LOCK-01** (byte-compatible round-trip, both directions, incl.
  delimiter / all-delimiter) + **LOCK-02** (pin contract in `test_messages` Unity + host parser tests;
  preserve constant parity; CI green both repos). These are the two requirements this phase closes.
- `.planning/ROADMAP.md` — Phase 52 entry (Goal + 4 Success Criteria + Depends-on); Phase 53 (bench,
  which consumes this phase's green contract).

### Established mechanism to mirror (codegen + vendored-catalog model — D-04)
- `firestarter/tools/catalog/messages.toml` + `firestarter/tools/catalog/codegen.py` — the v1.2
  message-catalog codegen; vendored byte-identical in `firestarter_app/tools/catalog/`. The
  `frame-vectors` catalog + codegen follow this exact pattern (header `firestarter/include/messages.h`
  / module `firestarter_app/firestarter/messages.py` are the emit-target analogs).
- `firestarter/tools/catalog/codegen.py` docstring — the determinism contract (LCAT-05) + `--check`
  drift gate (LCI-04) the vector codegen must replicate.

### Code to change / extend — firmware (`v1.10-serial-transport-hardening` branch in `firestarter/`)
- `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` — existing command-frame
  decode + CRC8-reject + resync Unity suite; the independent `ref_crc8` reference reused for the KAT (D-06).
- `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp` — data-path frame Unity suite.
- `firestarter/include/firestarter.h` — `CMD_FRAME_MAX` (~line 26, `#define CMD_FRAME_MAX DATA_BUFFER_SIZE`) — the parity subject (D-07).
- `firestarter/src/boards/rurp_serial_utils.cpp` — COBS decode + CRC8 PROGMEM primitives the vectors exercise.

### Code to change / extend — host (`v1.10-serial-transport-hardening` branch in `firestarter_app/`)
- `firestarter_app/tests/test_cobs.py` — existing COBS encode/decode pytest suite (394 lines); vector
  assertions extend/complement it.
- `firestarter_app/tests/test_revision_constants_parity.py` — the skipif-guarded parity test to EXTEND
  with `CMD_FRAME_MAX` (D-07).
- `firestarter_app/firestarter/frame_parser.py` — COBS encode/decode + `_crc8_ccitt()` the vectors exercise.
- `firestarter_app/firestarter/constants.py` — `CMD_FRAME_MAX = 512` (~line 28), the host side of the parity assertion.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **v1.2 codegen mechanism** (`tools/catalog/codegen.py` + `messages.toml`, vendored byte-identical in
  both repos) — directly cloneable for the `frame-vectors` catalog: deterministic emit, `--check` drift
  gate, dual C++/Python output, per-repo CI integration already proven.
- **Existing COBS/CRC8 framing tests** — firmware `test_cobs_data_frame` + `test_cobs_cmd_frame` Unity
  suites; host `test_cobs.py`. Vector assertions extend these rather than starting from scratch.
- **Independent `ref_crc8`** (in `test_cobs_cmd_frame.cpp`, copied from `test_rurp_log_id.cpp`) — a
  table-free reference CRC8 the KAT (D-06) can reuse, keeping the assertion independent of the production PROGMEM table.
- **`test_revision_constants_parity.py` skipif pattern** (Phase 34/36 TEST-04) — the parity-guard
  mechanism to extend for `CMD_FRAME_MAX`; `skipif` keys on firmware-header presence so host-only CI skips cleanly.

### Established Patterns
- **Vendored-catalog + per-repo codegen drift gate** — the cross-repo "single source" is a byte-identical
  vendored copy in each repo; lockstep held by paired commits, not automated cross-repo diff (D-04 / D-09).
- **`<regen> && git diff --exit-code` CI drift gate** — the v1.2 mechanism that fails CI if generated
  artifacts drift from the catalog.
- **Firmware/host constant parity** (CLAUDE.md) — duplicated constants must change together; guarded by parity tests.

### Integration Points
- Golden vectors are the direct input to Phase 53 bench verification (a green Phase 52 contract is the
  precondition for treating the transport as a settled, byte-exact variable on hardware).
- This phase touches NO production transport code paths — only tests, the new vector catalog/codegen, and
  the parity test extension. The codec/contract itself is frozen.

</code_context>

<specifics>
## Specific Ideas

- The **CR-01 254-run boundary** (Phase 50 encoder byte-drop, caught in post-execution review) is the
  motivating reason the corpus must include 253/254/255-run vectors (D-05). The contract test should make
  that class of bug impossible to reintroduce silently in either repo.
- "Shared frozen golden vectors" is the load-bearing choice: the proof rests on both implementations
  matching ONE set of bytes, so the bytes — and the two vendored catalogs that produce them — are the
  asset to protect (hence D-09 calling out cross-repo identity explicitly).
- The contract is **frozen** — every Phase-52 test is a *pin*, never a *change*. If a test reveals the two
  implementations disagree, the bug is in an implementation (or a catalog drift), not in the contract.

</specifics>

<deferred>
## Deferred Ideas

- **Meta-level cross-repo catalog-diff CI check** — would catch the D-09 drift risk automatically;
  operator chose per-repo CI + paired-commit discipline instead (2026-06-02). Recorded in case a future
  milestone wants the stronger guarantee.
- **Randomized/property-style fuzz sweep** of the codec (seeded, many lengths/patterns) — out of the
  deterministic golden-vector scope (D-05); could be added later as a separate per-repo test if desired.
- **WR-01 — frame-level deadline on the firmware COBS decoder byte-wait**
  (`.planning/todos/pending/cobs-decoder-framelevel-deadline-wr01.md`) — a decoder *behavior* change,
  not a contract test; explicitly out of scope for this test-only phase. Stays a pending todo.
- **Fixing the host `CMD_FRAME_MAX = 512` vs firmware `DATA_BUFFER_SIZE` board-variance** — judged
  acceptable for v1.10 (512 floor pinned per D-07); revisit only if a >512 B Leonardo command frame
  becomes legitimate.
- **Re-framing the fw→host response direction** — out of v1.10 scope (ADR §4.2); not a Phase 52 concern.

### Reviewed Todos (not folded)
- **WR-01 (frame-level decoder deadline)** — reviewed; not folded. Reason: behavior change, not a
  contract/round-trip test; belongs to a fix phase, not Phase 52.
- **`avrdude-mcu-detection-fallback`** + **`w27c512-eeprom-misclassification`** — unrelated to transport
  framing; no Phase 52 overlap.

</deferred>

---

*Phase: 52-lockstep-contract-round-trip-tests*
*Context gathered: 2026-06-02*
