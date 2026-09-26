# Phase 49: Framing Mechanism Decision (COBS `0x00` vs SLIP `0xC0`) - Context

**Gathered:** 2026-06-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 49 produces a **binding, evidence-backed decision record** that chooses the serial
framing mechanism — streaming COBS (`0x00` delimiter, COBS-DECISION §4.3) vs SLIP/RFC-1055
(`0xC0` delimiter, §4.2) — and resolves the SERIAL_ON_IO `0x00` bus-aliasing safety question
(SAFE-01 / COBS-DECISION Open Q2/Q3) **before any implementation phase commits to a delimiter
byte**. The deliverable is a decision artifact plus a frozen frame contract — **not code**.

The decision is load-bearing because framing the command channel (Phase 51) means the host
now actively emits delimiter bytes on the host→fw direction — so the host-side `0x00` timing
guarantee is real, not theoretical.

**In scope:** mechanism choice; SAFE-01 resolution (code/architectural proof); the full frame
contract (delimiter, escape/run-length scheme, frame layout, CRC8 placement, per-file change
map); the standalone v1.10 decision ADR.

**Out of scope (later phases):** implementing the framing layer (Phase 50), command-channel
migration (Phase 51), round-trip/lockstep tests (Phase 52), bench verification (Phase 53). No
code changes to `rurp_serial_utils.cpp` / `serial_comm.py` / `frame_parser.py` in this phase.

</domain>

<decisions>
## Implementation Decisions

### Locked upstream (carried from `v1.9-COBS-DECISION.md` — do NOT re-litigate)
- **ADOPT a custom framing layer; REJECT all off-the-shelf libraries** (§2, §4). The entire
  §4 candidate survey (PacketSerial, nanocobs, cobs-c/python, SerialTransfer, MIN) is settled.
- **CRC8-CCITT poly 0x07, seed 0x00, no reflection, no final XOR — kept unchanged** (D-05).
  No polynomial swap. Framing layers on top of the existing CRC8 byte.
- **Uno-fit filter binding** (D-04): streaming encode only, **no second ~512 B encode buffer**,
  ~545 B free-RAM ceiling. **Both finalists (streaming COBS §4.3, SLIP §4.2) already pass this**
  — so RAM is *not* a differentiator between them.
- **Lockstep dual-repo mandate**: any framing change touches `rurp_serial_utils.cpp` (fw) +
  `serial_comm.py`/`frame_parser.py` (host) + `test_messages` contract together.

### Mechanism Posture
- **D-01 (posture):** **Neutral, evidence-driven.** Phase 49 builds the full COBS-vs-SLIP
  comparison from scratch and the decision record picks the winner on merit. No thumb on the
  scale toward either finalist — COBS stays genuinely in contention.
- **D-02 (criteria weighting):** **Let the evidence rank them.** Do NOT pre-weight a single
  criterion. Score *all* criteria — safety (bus-aliasing risk class), provable byte-exactness
  (ease of round-trip + fault-injection proof), implementation simplicity (smallest auditable
  dual-repo diff), and overhead (COBS bounded +1/254 vs SLIP 2× worst case) — and let the
  aggregate ranking decide. Present the scored matrix in the record.

### SAFE-01 Bus-Aliasing Resolution
- **D-03 (proof rigor):** **Code/architectural proof only.** Resolve the host-side `0x00`-silence
  question (can the host emit a `0x00` frame-boundary byte during the programmer↔communication
  mode transition window?) via static analysis of `serial_comm.py` + the `com_mode` gate in
  `uno_rurp_shield.cpp` + the mode-transition sequence. **Resolved entirely within Phase 49 —
  no hardware.** Any bench confirmation is NOT a Phase 49 obligation.
- **D-04 (decisive fallback):** **Inconclusive proof → SLIP wins.** If the static analysis
  cannot conclusively prove host `0x00`-silence in the window, that counts as decisive evidence
  in the neutral matrix: SLIP `0xC0` is selected because it sidesteps the risk entirely
  (consistent with COBS-DECISION §5 Q2: "if the proof is unavailable, SLIP is the safer choice").
  The decision still lands in Phase 49 — no escalation to bench, no blocking.

### Decision Artifact
- **D-05 (artifact):** Write a **new standalone ADR — `.planning/v1.10-FRAMING-DECISION.md`**
  (filename proposed; planner may finalize) that resolves COBS-DECISION §2.0 / Q2 / Q3 and
  records the binding mechanism choice + frame contract. It **cross-references
  `v1.9-COBS-DECISION.md` as its input** and supersedes that doc's DEFER line for the mechanism
  question. The v1.9 doc stays **immutable** (the survey/constraints record); clean milestone
  separation.

### Contract Depth
- **D-06 (frozen contract):** Lock the **full frame contract** so Phases 50–52 implement against
  a frozen spec, nothing left to decide:
  - chosen **delimiter byte** (`0x00` or `0xC0`),
  - **escape / run-length scheme** (COBS run-length encoding, or SLIP `0xC0→0xDB 0xDC` /
    `0xDB→0xDB 0xDD` escaping),
  - **exact frame layout** — how the CRC8 byte and any length field sit relative to the payload
    and the delimiter,
  - **per-file change map**: what changes in `rurp_serial_utils.cpp`, `serial_comm.py`,
    `frame_parser.py`, and the `test_messages` Unity contract.

### Claude's Discretion
- Exact ADR filename and section structure (within the cross-link + immutability constraints).
- The specific scoring scale / matrix presentation format for D-02 (as long as all four criteria
  are scored and the aggregate ranking is shown).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The binding decision input (read first)
- `.planning/v1.9-COBS-DECISION.md` — the verified (2026-06-01) evaluation: ADOPT custom layer,
  REJECT libraries, KEEP CRC8 (D-05), Uno-fit filter (D-04). **Specifically:**
  - §2.0 — Revision Note (why DEFER→ADOPT; "rule out confounder" rationale)
  - §4.2 — SLIP/RFC-1055 candidate (Uno-fit PASS, `0xC0`, no bus-aliasing)
  - §4.3 — Hand-rolled streaming COBS candidate (Uno-fit PASS, `0x00`, ~6 B stack)
  - §5 Q2/Q3 — the host-side `0x00` timing guarantee + SLIP-vs-COBS open questions Phase 49 closes
  - §1.4 / `0x00` bus-aliasing note — the `com_mode` gate analysis (verified present in
    `uno_rurp_shield.cpp` lines 85-97)

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — **SAFE-01** (the one requirement this phase satisfies);
  binding inputs section (D-04/D-05 restated); v1.10 Non-Goals.
- `.planning/ROADMAP.md` — Phase 49 entry (Goal, 4 Success Criteria, Depends-on); v1.10
  milestone framing; Phases 50–53 (the consumers of this phase's frozen contract).

### Serial-path code to analyze (read, do NOT modify in Phase 49)
- `firestarter/src/boards/uno_rurp_shield.cpp` — `com_mode` gate / `rurp_log_id` strong override
  (lines ~85-97); `rurp_set_programmer_mode()` PD0-as-output transition (SERIAL_ON_IO).
- `firestarter_app/firestarter/serial_comm.py` — host TX path; the mode-transition window where
  SAFE-01 asks whether the host can emit `0x00` (D-03 static proof target).
- `firestarter/src/boards/rurp_serial_utils.cpp` — current `[len_u16][xor][payload]` data framing
  + CRC8-CCITT table (lines ~109-131); the per-file change map target.
- `firestarter_app/firestarter/frame_parser.py` — `_build_crc8_table()` (CRC8 poly 0x07 contract).
- `firestarter/src/firestarter.cpp` (~lines 162-172) — current `{`-peek command-ingest path
  (relevant to the Phase 51 command-channel framing the SAFE-01 question is load-bearing for).
- `test_messages` Unity suite (firmware) — the frame contract pinned by tests.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **CRC8-CCITT table (both repos)** — `rurp_serial_utils.cpp` PROGMEM table + `frame_parser.py`
  `_build_crc8_table()`. Reused unchanged under whatever framing is chosen (D-05). The frame
  contract appends/layers the existing CRC8 byte, not a new checksum.
- **`com_mode` gate** (`uno_rurp_shield.cpp`) — the existing architecture that prevents the
  *firmware* from emitting any frame bytes (incl. a `0x00` delimiter) during programmer mode.
  This is the firmware half of the SAFE-01 proof; Phase 49's static analysis adds the host half.

### Established Patterns
- **Four coexisting framings on one 250000-baud line** (COBS-DECISION §1.1): host→fw JSON
  command, host→fw data block, fw→host data block, fw→host log/telemetry. The frame contract
  must state which framings the chosen mechanism applies to and how it coexists with the rest.
- **Streaming-encode constraint** (D-04): the reference snippet in COBS-DECISION §3 shows a
  zero-extra-buffer streaming COBS encoder (~6 B stack). The contract must be expressible
  streaming for both finalists — RAM is not a differentiator.
- **Breaking lockstep upgrades** precedent — v1.2 Message-ID rework (no mixed-version interop);
  the framing migration follows the same dual-repo, no-interop pattern.

### Integration Points
- Phase 49 produces NO code, but its frozen contract is the direct input to Phase 50
  (`rurp_serial_utils.cpp` + `serial_comm.py`/`frame_parser.py`), Phase 51 (command channel),
  and Phase 52 (`test_messages` + host parser tests pin the contract).

</code_context>

<specifics>
## Specific Ideas

- The decision record must read "we picked X because the scored matrix ranks it highest on
  [criteria]" — NOT "we picked one". Success criterion 1 explicitly rejects a bare assertion.
- SAFE-01 resolution language must mirror COBS-DECISION §5 Q2/Q3 phrasing so the supersession
  is traceable: the v1.10 ADR closes the exact open questions the v1.9 doc left open.
- Overhead framing for the matrix: COBS adds at most +1 byte per 254-byte run; SLIP can expand
  up to 2× in a pathological all-`0xC0` payload. Both fit; this is a tie-breaker input, not a gate.

</specifics>

<deferred>
## Deferred Ideas

- **Hardware/bench confirmation of the SAFE-01 timing guarantee** — explicitly NOT in Phase 49
  (D-03 keeps it a static proof). If any residual hardware confidence is wanted, it rides the
  Phase 53 bench gate, not this decision phase.
- **Implementing the chosen framing** — Phase 50 (data path) / Phase 51 (command channel).

### Reviewed Todos (not folded)
- `serial-cobs-resync-data-path.md` — the v1.10 starting-evidence todo. Reviewed but **not
  folded into Phase 49**: it was re-pointed to **Phase 50** (implementation) in commit `70fc917`
  ("eval done, impl is v1.10"). The evaluation it asked for is complete (`v1.9-COBS-DECISION.md`);
  Phase 49 only makes the mechanism call. The todo closes when Phase 50 ships.

</deferred>

---

*Phase: 49-framing-mechanism-decision-cobs-0x00-vs-slip-0xc0*
*Context gathered: 2026-06-01*
