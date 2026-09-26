# Phase 53: Byte-Exact Bench Verification (hardware-gated) - Context

**Gathered:** 2026-06-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 53 is the **hardware-gated capstone** of v1.10. It proves on real bench hardware that the
hardened COBS transport (locked + pinned green in Phases 49–52) is **byte-exact**, that its resync
behavior **recovers within one packet under fault injection**, and that the unstable **uno328pb**
re-test is recorded as **transport-exoneration** — closing the milestone's central claim that serial
corruption is ruled out as a confounder for the deferred v1.9 read-bug RCA.

**This phase adds NO transport behavior.** The frame contract, codec, CRC8, and resync posture are
frozen upstream. Phase 53 delivers: a **fault-injection harness**, a **write-leg byte-identity
procedure** (the existing `dev consistency-check` only covers reads), the **operator-witnessed bench
runs**, and a **milestone evidence artifact** the resumed RCA can treat as a settled variable.

**In scope:**
- Operator-witnessed **N=5 consecutive framed read AND write transfers, byte-identical**, on a clean
  Uno (512 B) and clean Leonardo (1024 B). (XACT-01 / SC1)
- A **fault-injection harness** demonstrating resync **within one packet** in BOTH directions
  (firmware decoder via host→fw corruption on the wire; host decoder via a fw→host receive-path hook).
  (XACT-02 / SC2)
- **uno328pb re-test** on the hardened firmware, recording the failure shape and a structured
  transport-exoneration verdict. (XACT-03 / SC3)
- A **milestone evidence artifact** (hashes, fault-injection log, uno328pb before/after, operator
  attestation) sufficient for the resumed v1.9 RCA. (SC4)

**Out of scope (do NOT pull forward):**
- **Any per-shield hardware fix or read-bug RCA** — that is deferred v1.9 Phase 45+. This phase
  EXONERATES the transport; it does not diagnose or fix Bug A / Bug B.
- **Any transport behavior, mechanism, or contract change** — frozen (Phase 49 ADR §4); pinned (Phase 52).
- **Transparent corrupted-frame recovery** — the locked posture is bounded-desync + fail-fast
  (Phase 50 D-01); "recovers within one packet" means the *next* frame decodes clean, NOT that the
  corrupted frame is salvaged.

</domain>

<decisions>
## Implementation Decisions

### Carried forward — LOCKED upstream (Phases 49–52; do NOT re-litigate)
- **Frame contract = `[COBS(payload + CRC8)][0x00 delimiter]`**; CRC8-CCITT poly `0x07`, seed `0x00`,
  no reflection, no final XOR, over the raw payload (Phase 49 ADR §4.1/§4.3; pinned by Phase 52 golden vectors).
- **Resync = bounded-desync + fail-fast** (Phase 50 D-01): on CRC8/COBS failure the receiver discards
  bytes to the next `0x00` and surfaces a clean error **immediately** (no 2 s timeout cascade); the
  *following* frame re-anchors. There is NO transparent auto-recovery of the corrupted frame.
- **`len_u16` length prefix was REMOVED** (Phase 50) — the delimiter provides boundaries. XACT-02's
  "or length field" wording is therefore moot; the only corruptible structural elements are the
  **CRC8 byte** and the **`0x00` delimiter**.
- **Transport-exoneration scope** (v1.9-COBS-DECISION §2.0): a green re-test rules serial out as a
  confounder; it is NOT a hardware fix. Bug A (Modified Rev 0) is read-path-causal (Phase 44);
  Bug B (Rev 2.0) is un-root-caused. Both stay deferred to v1.9 Phase 45+.

### Fault-injection harness (XACT-02 / SC2)
- **D-01: Inject in BOTH directions.**
  - **host→fw command frame** — the host deliberately corrupts an outgoing command frame before send,
    exercising the **firmware decoder** on the real wire: it must drain-to-`0x00`, surface a clean
    error immediately, and accept the next command frame. This is the primary on-hardware demonstration.
  - **fw→host read frame** — a **host receive-path hook** mutates a received frame, exercising the
    **host decoder** resync (the actual read-bug confounder direction). Acknowledged: this leg is close
    to the Phase 50 unit coverage, but it is included so both decoders are demonstrated on the bench path.
- **D-02: Fault forms = corrupted CRC8 byte + dropped/missing `0x00` delimiter** (mirrors the Phase 50
  D-02 fault set: a corrupted-CRC frame AND a flipped/missing delimiter). A **spurious/extra `0x00`**
  mid-frame is OPTIONAL — planner's discretion to add if cheap.
- **D-03: Pass criterion = clean immediate error + next transfer succeeds byte-exact.** Assert both:
  (a) the corrupted frame surfaces an immediate error (sub-second — NOT a 2 s timeout cascade), and
  (b) the very next framed transfer on the same open connection completes byte-exact. Matches the
  Phase 50 D-01 bounded-desync + fail-fast contract.
  - **Discretion (planner):** optionally record the *measured* time-to-error (e.g. `<200 ms`) as a
    quantitative line in the artifact, as concrete evidence the 2 s cascade is gone.

### Byte-identity + write leg (XACT-01 / SC1)
- **D-04: N=5 consecutive transfers per clean board** (Uno + Leonardo), all SHA-256-identical —
  reproducing the GATE-1.8d W27C512 N=5 baseline depth. Use `dev consistency-check --runs 5` for the
  read leg. **N=5 is the floor.**
- **D-05: "Reproduces the GATE-1.8d baselines" = self-consistency mandatory + baseline-hash-match if
  the original chip is available.**
  - **Mandatory:** all N read runs SHA-256-identical to each other.
  - **Strong form (record which was achieved):** if the **original W27C512** (same contents) is on the
    bench, ALSO byte-match the stored baseline binaries at
    `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/run_0X.bin` — proving the
    hardened path reads identical bytes to the pre-hardening baseline. If that chip is unavailable,
    self-consistency alone satisfies SC1 and the artifact states so explicitly.
- **D-06: WRITE leg proven via write→read-back→compare, N cycles.** Erase, write a known source image
  through the framed write path, read it back, assert read-back SHA-256 == source-image SHA-256. Repeat
  N=5 cycles; all cycles byte-identical. An **independent host-side compare** — not reliance on the
  firmware's built-in verify pass.
- **D-07: Clean-board proof targets shield Rev 2.0** — reads clean per Phase 44 and matches the
  GATE-1.8d Leonardo baseline lineage. Per `user_shield_revisions`, the operator is STILL asked to
  confirm the actual silkscreen rev on the bench at session time (the EEPROM `hw_revision` byte cannot
  distinguish revs); the confirmed rev is recorded in the artifact.

### uno328pb re-test recording (XACT-03 / SC3)
- **D-08: N=5 with explicit timeout-retry logging.** Match the clean-board depth, but LOG raw timeouts
  and retries rather than aborting — capture the failure shape honestly. Per
  `project_uno328pb_bench_instability_27_04`: never trust N=1; retry on timeout.
- **D-09: Cite the documented pre-hardening "before" shape + capture the hardened "after" shape.** The
  pre-hardening behavior (timeouts + ~99 % `0xff`-drift) is already characterized in project memory and
  `.planning/v1.6-EVIDENCE.md` — do NOT re-flash old firmware. Re-run only on the hardened firmware and
  compare the "after" shape against that documented baseline. (Fewer sideload cycles → less chip-out risk.)
- **D-10: Record a STRUCTURED exoneration verdict block** stating: (1) observed hardened failure shape
  (timeout count / `0xff`-drift %), (2) whether the shape changed vs the documented before-shape, and
  (3) the explicit line: *"transport-exoneration per v1.9-COBS-DECISION §2.0 — NOT a per-shield
  hardware fix; the actual RCA stays deferred to v1.9 Phase 45+."* So the resumed RCA cannot misread a
  green/changed result as a fix.

### Milestone evidence artifact (SC4) — captured by default (not separately discussed)
- **D-11:** Artifact lives under `.planning/v1.10/bench-verification/`, mirroring the
  `.planning/v1.6/consistency-check-runs/` layout (per-run binaries + a summary doc). Contents:
  SHA-256 hashes for every read/write run (clean boards + uno328pb), the fault-injection log (both
  directions, incl. the optional error-latency note), the uno328pb before/after shape + structured
  exoneration verdict (D-10), and an **operator-witness attestation** (which boards, which confirmed
  shield rev per D-07, date). Planner refines exact filenames/structure.

### Claude's Discretion
- Exact fault-injection harness implementation (host debug flag / test-only wedge vs a dedicated dev
  subcommand), and the fw→host receive-path hook mechanism — provided it does not alter production
  transport code paths.
- Whether to record the measured time-to-error number (D-03 discretion) and the optional spurious-`0x00`
  fault form (D-02).
- Exact artifact filenames, directory sub-structure, and summary-doc format under
  `.planning/v1.10/bench-verification/` (D-11).
- The precise source image used for the write-leg cycles (D-06) and the data-block content patterns.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The frozen contract + exoneration scope (read FIRST)
- `.planning/v1.10-FRAMING-DECISION.md` §4 — frozen frame contract (`[COBS(payload+CRC8)][0x00]`,
  CRC8 placement, atomic-write mandate). The byte-exact contract this phase proves on hardware.
- `.planning/v1.9-COBS-DECISION.md` §2.0 — the **transport-exoneration scope note**: what a green
  post-hardening re-test does and does NOT conclude (Bug A read-path-causal; Bug B un-root-caused;
  RCA deferred). XACT-03's verdict wording (D-10) is bound to this section.

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — **XACT-01** (byte-exact clean-board, read+write, reproduce GATE-1.8d),
  **XACT-02** (fault-injection resync within one packet), **XACT-03** (uno328pb re-test, exoneration).
- `.planning/ROADMAP.md` — Phase 53 entry (Goal + 4 Success Criteria + Depends-on Phases 50/51/52).

### Bench baseline substrate (the N=5 depth + hash-match target — D-04 / D-05)
- `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/run_0X.bin` — the stored
  GATE-1.8d W27C512 N=5 Leonardo baseline binaries; the strong-form hash-match target if the original
  chip is on the bench.
- `.planning/v1.6-EVIDENCE.md` — Phase 29 v2 Bug A/Bug B characterization + the documented uno328pb
  pre-hardening failure shape (the "before" reference for D-09).

### Prior-phase decisions this phase rests on
- `.planning/phases/52-lockstep-contract-round-trip-tests/52-CONTEXT.md` — the proven-green byte
  contract (the precondition: transport is a settled variable).
- `.planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-CONTEXT.md`
  — D-01 resync = bounded-desync + fail-fast (the behavior XACT-02 demonstrates on hardware); D-02
  fault set the bench mirrors.
- `.planning/phases/49-framing-mechanism-decision-cobs-0x00-vs-slip-0xc0/49-CONTEXT.md` — mechanism
  decision (COBS `0x00`, keep-CRC8 lock).

### Code substrate (host CLI — `v1.10-serial-transport-hardening` branch in `firestarter_app/`)
- `firestarter_app/firestarter/cli_handlers.py` (~line 1030) — `dev consistency-check` command
  (`--runs`, `--output-dir`, per-run binaries, SHA-256 divergence, 3-way verdict). The read-leg +
  uno328pb substrate; the write-leg procedure (D-06) and fault-injection harness (D-01) build alongside it.
- `firestarter_app/firestarter/eprom_operations.py` (~line 497) — `consistency_check_eprom()`
  (read N-times + hash compare); the write→read-back→compare cycle (D-06) reuses its read/compare machinery.
- `firestarter_app/firestarter/frame_parser.py` / `firestarter_app/firestarter/serial_comm.py` — host
  COBS encode/decode + `_crc8_ccitt()`; where the host→fw outgoing-frame corruption and the fw→host
  receive-path hook (D-01) attach.

### Bench-operation protocols (hardware-gated — MANDATORY at each bench task)
- Per `feedback_chip_out_before_sideload` — chip OUT of socket before any firmware sideload.
- Per `feedback_verify_port_identity_each_task` — verify `controller:` identity per port at every task.
- Per `user_shield_revisions` — ASK the operator which silkscreen rev is on the bench (D-07).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`dev consistency-check`** (`cli_handlers.py` ~1030 / `eprom_operations.py:497`) — already does
  N-consecutive reads + SHA-256 divergence + per-run binaries + 3-way verdict (`0=PASS/1=FAIL/2=hw-error`)
  and supports `--runs`, `--output-dir`, `--read-settling`, `--read-strobe`. Directly serves the read
  leg (D-04) and the uno328pb re-test (D-08); its read/compare machinery is the basis for the write-leg
  write→read-back→compare cycle (D-06).
- **Phase 50 resync unit tests** (host `test_cobs.py`; firmware `test_cobs_*` Unity suites) — the
  behavior the bench fault-injection harness demonstrates on real hardware; the fault forms mirror
  Phase 50 D-02.
- **GATE-1.8d baseline binaries** (`.planning/v1.6/consistency-check-runs/`) — the N=5 depth reference
  and the strong-form hash-match target (D-05).

### Established Patterns
- **3-way verdict contract** (`0=PASS / 1=FAIL / 2=hw-error`) — must be preserved; the uno328pb
  timeout/hw-error case maps to `2`, not collapsed to `1` (the v1.6 RCA diagnostic depends on this).
- **Hardware-gated bench protocol** — chip-out-before-sideload, per-port identity verification,
  operator-confirmed shield rev. All bench steps are operator-authorized and operator-witnessed.

### Integration Points
- Fault-injection (D-01) must attach WITHOUT altering production transport code paths (a test-only
  wedge / debug flag / dev subcommand), so the byte-exact contract proven in Phase 52 stays untouched.
- The Phase 53 artifact (D-11) is the direct hand-off to the resumed v1.9 Phase 45+ RCA: it lets the
  RCA treat the serial transport as a settled, byte-exact variable.

</code_context>

<specifics>
## Specific Ideas

- "Recovers within one packet" is explicitly the **bounded-desync + fail-fast** posture (Phase 50 D-01),
  NOT transparent corrupted-frame recovery. The bench harness proves *the next frame decodes clean*,
  with an immediate error on the bad one — never a 2 s hang.
- The uno328pb result is the milestone's most load-bearing nuance: a green OR changed shape must be
  recorded as **transport-exoneration, not a fix** (D-10), or the resumed RCA could draw the wrong
  conclusion. The structured verdict block exists to make that misread impossible.
- The clean-board proof deliberately reproduces the **Rev 2.0 Leonardo** GATE-1.8d lineage (D-07) so
  the byte-identity claim ties back to a known-clean, already-baselined combination.

</specifics>

<deferred>
## Deferred Ideas

- **v1.9 read-bug RCA + per-shield fix (Bug A Modified Rev 0, Bug B Rev 2.0)** — explicitly deferred to
  v1.9 Phase 45+. Phase 53 exonerates the transport so this RCA can resume on solid ground; it does NOT
  diagnose or fix the hardware here.
- **A/B re-flash of pre-hardening firmware on the uno328pb** for a fresh "before" capture — rejected for
  Phase 53 (D-09 cites the documented before-shape instead) to minimize sideload/chip-out cycles. Could
  be revisited if the documented before-shape proves insufficient contrast.
- **Spurious/extra-`0x00` fault form + measured error-latency number** — optional planner discretion
  (D-02 / D-03); not mandated.
- **WR-01 — frame-level deadline on the firmware COBS decoder byte-wait** — a decoder behavior change,
  out of v1.10 scope; remains a pending todo.

None of the above are in Phase 53 scope.

</deferred>

---

*Phase: 53-byte-exact-bench-verification-hardware-gated*
*Context gathered: 2026-06-02*
