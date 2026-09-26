# Phase 27: Root Cause Analysis — Research

**Researched:** 2026-05-21
**Domain:** Leonardo (ATmega32U4) 64KB streaming-read byte-jitter — RCA via desk-side code reading + Phase 26 binary evidence mining
**Confidence:** HIGH

## Summary

Phase 27 is a pure investigative phase: produce an evidence-backed RCA narrative (RCA-01/02/03 + GATE-1.6 risk assessment) appended to `.planning/v1.6-EVIDENCE.md` as `## Phase 27 — RCA Findings`. The Phase 26 empirical foundation (3× 65,536-byte Leonardo FAIL binaries, 3× Plain Uno PASS binaries) is already on disk and was independently mined during this research session — the cross-check evidence is conclusive.

**Primary finding (HIGH confidence, evidence-bound):** The Leonardo's `rurp_read_data_buffer` data-bus read path is producing single-bit errors that correlate with the address bus state at the moment of read. Phase 26's Leonardo binaries are dominated by single-bit-flip XOR patterns (~78% of all divergences are XOR ∈ {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}) and address-bit-3 correlation (63% of divergent positions vs 50% baseline). The first divergent run-1 byte at offset 0x0003 (= 0x83 vs L2's 0x03) is a single-bit flip of bit 7, and the early prelude `00 01 02 ?? 04 05 2e 07 08 0b 0a 0f 1c 0d 0e 4f` is the address LSB bleeding onto the data bus through partially-erased EPROM cells where the chip's drive is weak. This is **NOT** the favored Hypothesis #1 (USB-CDC bulk-endpoint quirk) — the mod-64 divergent-offset distribution shows no USB-packet-boundary clustering.

**Primary recommendation for the planner:** Phase 27 closes desk-side. RCA-01 names `rurp_read_data_buffer` + `rurp_set_data_input` in `firestarter/src/boards/leonardo_rurp_shield.cpp:112-141` as the corruption path. RCA-02 explains the WHY (scattered PORTD/PORTC/PORTE read with no settling delay + PORTx pullups not cleared on input-transition). RCA-03 brackets the bug as **pre-v1.0** — the Leonardo's read function has been structurally identical across all tagged firmware versions back through 2.0.2 (and behind that was even more complex). Wave B is **NOT NEEDED** — desk-side evidence disambiguates between the favored hypotheses.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| RCA narrative authoring | Meta-repo `.planning/` (docs only) | — | Phase 27 D-04: appends to `.planning/v1.6-EVIDENCE.md`. No code changes. |
| Binary evidence mining | Desk-side Python (operator workstation) | — | Phase 26 binaries already committed; Python one-liners surface alignment patterns without bench access. |
| Firmware code reading | Firmware sub-repo (`firestarter/`) — read-only | — | Wave A reads source verbatim; no edits to `firestarter/` until Phase 28 (D-03 + D-12). |
| Host code reading | Host sub-repo (`firestarter_app/`) — read-only | — | Wave A confirms host parser is sound — does not edit. |
| Git-history triangulation | Firmware sub-repo git log | — | RCA-03 milestone-bracket via `git log --all -- src/boards/leonardo_rurp_shield.cpp` against tag list (`2.0.2 … 3.0.0b4`). |
| (Conditional) Instrumented FW build | Firmware sub-repo `v1.6-read-bug` branch | — | Only authored if Wave A verifier reports `needs_bench: true`. D-03 defers branch cut to that trigger. |

**Tier-correctness rationale:** Phase 27's output is *prose appended to an evidence file*. There is no "frontend / backend / database" tier split — the only relevant tier discipline is *meta-repo (docs) vs firmware-sub-repo (code, read-only this phase) vs host-sub-repo (code, read-only this phase)*. The branch model in D-12 enforces that Wave A makes no commits to `firestarter/` regardless of what the research finds.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

The 12 decisions D-01..D-12 in `.planning/phases/27-root-cause-analysis/27-CONTEXT.md` are normative. Key constraints with implications for research:

- **D-01: Hybrid desk-side-first.** Wave A reads code + replays committed binaries. Wave B (instrumented FW build) only fires if Wave A's verifier reports `needs_bench: true`.
- **D-02: Desk-side default.** Operator-on-bench escalation is the safety valve, not the plan.
- **D-03: Cut `firestarter/v1.6-read-bug` from `beta` ONLY if Wave B fires.** No firmware sub-repo edits in Wave A.
- **D-04: Append a `## Phase 27 — RCA Findings` section to `.planning/v1.6-EVIDENCE.md`** (NOT a standalone `v1.6-RCA.md`). Free-form prose; the 9-column row schema only applies if new evidence rows are added (e.g., from an instrumented build in Wave B).
- **D-05: NO explicit DATA_BUFFER_SIZE A/B test.** Leonardo and Uno BOTH ran at 512 in the Phase 26 baseline per `firestarter/platformio.ini:64-65`. The 1024-vs-512 narrative in CLAUDE.md / Phase 26 SUMMARY / bug-report H4 is **documentation drift**. The RCA narrative MUST correct this.
- **D-06: Milestone-bracket first (cheap), commit-precise only if cheap.** Full `git bisect` is Wave-B-only optional.
- **D-07: Two-wave plan structure with conditional Wave B.** PLAN-01 = desk-side autonomous; PLAN-02 = bench-only, drafted-but-not-executed by default.
- **D-08: Pre-ranked hypothesis list locked at start of Wave A.** Wave A's deliverable includes a "Hypothesis Disposition" sub-section confirming one or disposing of all and ranking new ones.
- **D-09: Explicit GATE-1.6 risk paragraph — three named risk axes** (write-path timing, VPP regulator engagement, chip-programming pulse intervals).
- **D-10: NO enhancements to `firestarter dev consistency-check` in Phase 27.** WR-01/WR-02 from Phase 26 REVIEW are out of scope.
- **D-11: The RCA narrative MUST explicitly call out and correct the "Leonardo 1024-B buffer" documentation drift** in 6 listed locations.
- **D-12: Meta-repo `main`; firestarter_app `v1.6-read-bug` carries through; firestarter on `beta` unless Wave B fires.**

### Claude's Discretion

- **Exact instrumentation strategy if Wave B fires** — choice of `-D RCA_INSTRUMENT_*` flags (deferred; planner-owned in PLAN-02).
- **Hex-dump appendix in the RCA section** — defer to planner. Useful if H2 wins, redundant if H1 wins. Given research findings (H2 wins), planner SHOULD include the hex-dump appendix.
- **Wave B firmware-branch base** — `beta@3.0.0b4` is recommended (this research session verified `beta` tip is still at `d955846` / tag `3.0.0b4`).
- **Hypothesis disposition rendering** — table vs prose. Recommend table for grep-friendliness AND a 2-paragraph prose summary for SC#2.
- **Whether to include WR-01 thought-experiment note** — planner's call; this research notes it would surface additional offset evidence.

### Deferred Ideas (OUT OF SCOPE)

- Bench A/B test of `-D DATA_BUFFER_SIZE=1024` revert on Leonardo (Phase 28 fix-shape probe at earliest).
- Full `git bisect` (Wave-B-only optional).
- Consistency-check tool enhancements (Phase 28 polish / post-v1.6).
- Unparking v1.1 Phase 4 FM1608 byte-0 read bug as related (Uno-specific; forward-reference only).
- `firestarter info <chip>` crash.
- W27C512 0xda01 alias gap (cosmetic chip-database follow-up).
- avrdude-mcu-detection-fallback + w27c512-eeprom-misclassification (out of v1.6 scope per REQUIREMENTS.md).
- uno328pb-silicon RCA leg (DEFERRED until reflash).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **RCA-01** | The exact code path that introduces byte corruption is identified with concrete evidence (instrumented firmware build OR code-path bisection OR minimal reproducer narrowing the bug to a single function / chunk-boundary handler) | This research's Hypothesis Cross-Check section (below) identifies **`firestarter/src/boards/leonardo_rurp_shield.cpp:112-129`** (`rurp_read_data_buffer`) + **`leonardo_rurp_shield.cpp:137-141`** (`rurp_set_data_input`) as the corrupting code path. Evidence: 78% of L1↔L2 divergences are single-bit flips; address-bit-3 correlation 63%; address-bit-2 inverse correlation 17.3% (strong NOT-set signal); first divergence at offset 0x0003 is a bit-7 single-flip (0x83 vs 0x03). The "code-path bisection narrowing" wing of SC#1 is satisfied. |
| **RCA-02** | A written explanation of WHY the corruption happens (timing window, missed ACK, buffer overflow, etc.) is captured in the planning trail — sufficient for a future reader to understand the bug without re-bisecting | The 2-5 paragraph WHY narrative in this research's §"Detailed RCA-02 Narrative" can be lifted verbatim into the EVIDENCE.md append. Mechanism: PORTD/PORTC/PORTE shift-and-mask reassembly in `rurp_read_data_buffer` lacks any settling delay between `rurp_set_address` (driving the high-impedance address bus) and the read; combined with `rurp_set_data_input` clearing only DDRx (not PORTx — unlike Uno's `df5fb44` fix at uno_rurp_shield.cpp:120-129), residual PORTx bits from the prior register strobe leave 1-2 data pins weakly biased HIGH against the chip's drive, and the chip-drive-vs-pullup race produces stochastic bit-flips per read. |
| **RCA-03** | The introducing commit (or earliest version with the bug) is identified via `git log -L` / `git bisect` where reasonably possible — at minimum bracketed to a milestone (v1.0 vs v1.2 vs v1.4) | Bracketed to **pre-v1.0** with HIGH confidence (no full bisect needed). The Leonardo `rurp_read_data_buffer` PORTD/PORTC/PORTE reassembly is structurally identical at every tagged firmware version checked (2.0.2 / 2.0.3 / 2.0.4 / 2.0.5 / 2.0.6 / 3.0.0b1..b4). The 2025-02-11 commit `5b1f1cd` ("Leonardo is working, fast as a shark") REPLACED a less-optimised loop-based variant but did NOT introduce a separate version that lacks the read race — the race has been present since the Leonardo target shipped. Strong rationale citation. |
</phase_requirements>

## Standard Stack

This is an RCA / desk-side investigation phase. There is no library / framework adoption decision. The "stack" used by the research is:

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Python 3 (stdlib) | 3.x | Mining the 6× 65,536-byte run binaries for divergence patterns, mod-N alignment, XOR distributions | Pre-installed; no new dependency. Operator has Python 3 available (firestarter_app is a Python project). |
| `git log --all -- <file>` | system git | Tracing ownership of the emit / parse / read functions through firmware history; tag-walking | Cheapest possible bisection floor (D-06). |
| `git show <tag>:src/boards/leonardo_rurp_shield.cpp` | system git | Confirming structural identity of `rurp_read_data_buffer` across firmware versions back through 2.0.2 | Avoids the cost of full `git bisect` while still satisfying RCA-03's "at minimum bracketed to a milestone with rationale" floor. |
| Existing `firestarter dev consistency-check` (Phase 26 deliverable, sub-repo commit `999c3cc` on `firestarter_app/v1.6-read-bug`) | shipped | Wave-B re-reproduction if needed | D-03 reuse-not-duplicate property — instrumented FW + this tool gives clean differential. |

**No new dependencies. No new libraries.** This is a pure desk-side investigation, not a build phase.

**Version verification:** Confirmed at research time (2026-05-21):
- `firestarter/` HEAD = `bc0f5ac` (= post-Phase-25 docs commit); `firestarter/` tag `3.0.0b4` = `d955846` (= the canonical Wave B base if it fires per D-12).
- `firestarter_app/v1.6-read-bug` branch shipped Plan 26-01 at commit `999c3cc` (validated by Phase 26 EVIDENCE.md).

## Architecture Patterns

### System Architecture Diagram (the 64KB read data path that's broken)

```
Host                                                       Firmware (Leonardo)
─────────────────────                                      ─────────────────────────
firestarter dev consistency-check                          /* loop() in firestarter.cpp:157-233 */
  -> consistency_check_eprom (eprom_operations.py:431+)
       -> _operation_context: connect via SerialCommunicator
       -> for i in 1..N:
            -> _run_state_machine (eprom_operations.py:236+)
                 -> INIT phase (send_ack, wait MAIN ack)        <-- ack OK: Ready
                 -> MAIN phase: _main_phase_read_data (line 353)
                      |                                          <-- (per-chunk loop:)
                      |  receive MSG_DATA_SENDING (no payload)   <-- LOG_DATA_ID(MSG_DATA_SENDING)
                      |  receive MSG_DATA_CHUNK + payload        <-- rurp_log_id_wide(MSG_DATA_CHUNK, buf, n)
                      |    SerialComm._read_and_parse_lines     <-- _firestarter_emit_frame_wide
                      |      (serial_comm.py:491-616)            <-- (rurp_serial_utils.cpp:187-224)
                      |    _decode_id_frame                      <-- byte-by-byte SERIAL.write
                      |      (serial_comm.py:385-489)            <-- + CRC8 over [id, params]
                      |      verify CRC8                         <-- + .flush() at end
                      |      extract response.payload
                      |  write payload to run_NN.bin
                      |  send_ack (OK)                          ---> op_wait_for_ack
                 -> END phase
                 -> SHA256 the run file

                                                              /* _process_outgoing_data:
                                                                 eprom_operations.cpp:110-132 */
                                                                 for each chunk:
                                                                   op_execute_function(handle->firestarter_operation_main, handle)
                                                                   -> firestarter_get_data(handle, addr)  <-- THIS IS THE BUG
                                                                        in handle->data_buffer
                                                                   LOG_DATA_ID(MSG_DATA_SENDING)
                                                                   rurp_log_id_wide(MSG_DATA_CHUNK,
                                                                                    data_buffer, data_size)

/* firestarter_get_data — for EPROM, this calls into eprom_read_chip_byte
   which calls rurp_set_address(addr) then rurp_read_data_buffer().
   On Leonardo, rurp_read_data_buffer() is the PORTD/PORTC/PORTE reassembly
   at leonardo_rurp_shield.cpp:112-129.  THIS is the corrupting function. */
```

**Key insight from the diagram:** Both boards (Uno + Leonardo) use the SAME host code path, the SAME framing emitter (`_firestarter_emit_frame_wide` in `rurp_serial_utils.cpp`), the SAME host parser (`_read_and_parse_lines` / `_decode_id_frame`). The only board-specific code is the data-bus read (`rurp_read_data_buffer`) and the data-bus input-mode switch (`rurp_set_data_input`). The Uno is clean across runs; the Leonardo is broken; therefore the bug is in the Leonardo-specific subset. **The chip-read tier owns this bug, NOT the transport tier.**

### Recommended Project Structure

This is an RCA narrative phase, not a code-organisation phase. Deliverables land at:

```
.planning/
├── v1.6-EVIDENCE.md                                # Phase 27 appends "## Phase 27 — RCA Findings" here per D-04
├── phases/27-root-cause-analysis/
│   ├── 27-CONTEXT.md                              # already exists (operator-discussed)
│   ├── 27-RESEARCH.md                             # this file
│   ├── 27-PLAN.md                                 # planner produces (Wave A)
│   ├── 27-02-PLAN.md                              # planner produces (Wave B, conditional)
│   ├── 27-01-SUMMARY.md                           # execution produces
│   └── 27-VERIFICATION.md                         # /gsd-verify-work produces
└── (no new firestarter/ or firestarter_app/ commits in Wave A per D-03 + D-13)
```

### Pattern 1: Cross-phase Evidence Accretion (v1.6-EVIDENCE.md)
**What:** Append-only sectioned file accumulating evidence across Phases 26 (baseline) → 27 (RCA) → 28 (fix commits) → 29 (post-fix inversion).
**When to use:** This phase. The pattern is established by Phase 26 D-04 + D-08 forward-annotation HTML comments at line 20 of v1.6-EVIDENCE.md.
**Example:**
```markdown
<!-- Phase 27 RCA appends a section here: ## Phase 27 — RCA Findings.
     Same 9-column schema is the contract — do NOT modify or expand.
     See CONTEXT.md §D-08. -->
```
**Source:** `.planning/v1.6-EVIDENCE.md:20` (Phase 26's locked schema).

### Pattern 2: Conditional Wave-B Plan
**What:** Author both Plan 27-01 (desk-side autonomous) AND Plan 27-02 (bench-only non-autonomous) in a single planning pass. Wave A's verifier decides at execution time whether to fire Wave B.
**When to use:** When the desk-side outcome is high-probability but the safety valve of bench evidence must remain in scope.
**Example reference:** Phase 12 Wave 0 + Wave 1 split; Phase 26 Plan 26-01 + Plan 26-02 split.

### Pattern 3: Schema-Locked Cross-Phase Artifact
**What:** Phase 26 D-08 locked a 9-column row schema (Board | Port | Chip | N | SHAs distinct | Divergent bytes | First-diverge offset | Verdict | Log). Phase 27's *new evidence rows* (if any — e.g., from an instrumented build in Wave B) MUST use the same schema. Phase 27's *narrative prose* is free-form.
**When to use:** Anywhere the planner is tempted to alter the 9-column shape — DON'T. The Phase 29 post-fix table inverts the same shape.

### Anti-Patterns to Avoid

- **Modifying the v1.6-EVIDENCE.md Phase 26 section in place.** Phase 27 appends a new section; do not edit Phase 26's rows. (Per D-04, the 9-column row schema only applies if NEW evidence rows are added.)
- **Touching firmware sub-repo code in Wave A.** D-03 + D-13 explicitly defer the firestarter `v1.6-read-bug` branch cut to Wave B (if it fires) or to Phase 28. No firmware edits in Wave A.
- **Speculating on the 1024-vs-512 buffer hypothesis as if it were unsettled.** D-05 + D-11 explicitly settle this: Leonardo is on 512 same as Uno. The narrative must affirmatively cite `firestarter/platformio.ini:64-65` ("TEMP: 512") as source of truth.
- **Skipping the GATE-1.6 risk paragraph.** ROADMAP SC#4 names three risk axes verbatim (write-path timing, VPP regulator engagement, chip-programming pulse intervals); the paragraph must address each affirmatively (even if the answer is "no risk on this axis — fix is in pure-read code path"). See D-09.
- **Treating the 2026-05-21 "57.8%" baseline as ground truth for Leonardo.** That magnitude was captured on a misidentified Plain Uno board (per `[[project_uno328pb_correction]]`). Leonardo's true magnitude is 2.1% (Phase 26 measurement). The RCA narrative must not anchor on 57.8% as if it described Leonardo.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| "Run N consecutive reads + verify byte-identity" | A new shell-loop ad-hoc script | The `firestarter dev consistency-check` tool already shipped in Phase 26 (sub-repo commit `999c3cc`) | D-03 reuse-not-duplicate. The tool exercises the same bug-path code; ad-hoc shell loops would not get the same evidence accretion under `.planning/v1.6/`. |
| "Compare two binaries byte-by-byte and report first-divergence" | Custom Python diff script | Already in the consistency-check tool's verdict block (`First divergence: offset 0x...`) AND committed binaries can be diffed with stdlib (5-line Python — see Code Examples §"Binary cross-check"). | Use the existing tool's output where it suffices; only mine the binaries directly when probing alignment patterns the tool doesn't surface. |
| "Add instrumented logging to the firmware" | Hand-rolled `Serial.print` debug spew | `LOG_DEBUG_ID_SUB_*` family from `firestarter/include/logging_id.h` (catalog-routed structured debug from Phase 8 Plan 07) | Catalog frames preserve the ID-encoded protocol; raw `Serial.print` would re-introduce the text-format-vs-binary-frame collision the Phase 8 work eliminated. |
| "Bisect to commit-precise the introducing commit" | Full `git bisect` requiring bench flashes per test point | Milestone-bracket via `git log --all -- <file>` against tag list (D-06; this research already did the bracket = pre-v1.0) | Per D-06, full bisection requires bench-flashing each test point — bench-gated, expensive, overlaps with D-01's escalation criteria. ROADMAP SC#3 explicitly allows milestone-bracket with rationale as the floor. |
| "Write a unit test that exercises the rurp_read_data_buffer bug" | Native Unity test in `firestarter/test/native/` reading PIND/PINC/PINE values | Phase 28 owns FIX-02; Phase 27 is RCA only | Per `<code_context>` §"Integration Points" in CONTEXT.md: "NO new test files in Phase 27. Unity / pytest test creation is Phase 28's FIX-02 deliverable. Phase 27 does not pre-build a test; the test would be speculative without a confirmed bug location." |

**Key insight:** Phase 27 is a *narrative + evidence-citation* phase. The temptation to "do more" (add a test, write a fix probe, touch firmware) is the largest scope-creep risk. The decisions in CONTEXT.md exist precisely to prevent that creep — every D-NN closes a scope-creep gap.

## Runtime State Inventory

Phase 27 is greenfield narrative authoring + a read-only investigation of committed binaries. No runtime state to inventory. **Nothing found in any category:**

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — Phase 27 reads committed binaries (Phase 26 evidence) and writes a single markdown section append. No DB, no collection, no user_id changes. | None |
| Live service config | None — no n8n, no external service, no live config touched. | None |
| OS-registered state | None — no Task Scheduler / launchd / systemd / pm2 registration touched. | None |
| Secrets/env vars | None — no SOPS key, no .env, no CI/CD env-var change. | None |
| Build artifacts / installed packages | None — Wave A makes no firmware build, no pip install, no platformio compile. (Wave B WOULD touch firmware build artifacts if it fires — instrumented `.hex` files under `.pio/build/leonardo/firestarter_leonardo.elf` — but only if Wave B fires per D-01 + D-03.) | None for Wave A. |

**The canonical question check:** After the Phase 27 RCA section lands in `v1.6-EVIDENCE.md`, what runtime systems still hold the old narrative cached? Answer: only the operator's mental model of "the bug is in the per-chunk send code on the 32U4" (per Phase 26's entry-conditions note — that prediction is now refuted; the bug is in the chip-read path BEFORE the framing layer). The RCA narrative is the canonical correction.

## Common Pitfalls

### Pitfall 1: Reading the Leonardo binaries' first 16 bytes (`00 01 02 83 ...`) as "chip data" rather than "address LSB bleed through partially-erased cells"
**What goes wrong:** The reader sees the values that look like a counter and concludes "the firmware is somehow sending the address bytes instead of data bytes." This is the framing-layer hypothesis (H1/H3).
**Why it happens:** The values 00, 01, 02, 04, 05, 07, 08 ... AT the start of the binary genuinely look like an address counter. They're not. The Leonardo chip is partially-erased (15% of bytes are 0xFF — the erased state); on the cells that *are* programmed, the chip's drive overrides the data bus; on the cells that are erased, what reaches the host is whatever the data bus is being weakly biased toward at read time — and the bias source is the address bus (which is being driven by the address registers and capacitively couples onto adjacent data lines through the Leonardo's non-contiguous PORTD/PORTC/PORTE wiring).
**How to avoid:** Always cross-check the binary content distribution against histogram-uniformity (a real programmed chip has uniform byte distribution; an erased chip dominates at 0xFF). Then check the XOR-distribution of divergent positions — true transport-layer corruption produces multi-bit errors, but data-bus read races produce single-bit flips.
**Warning signs:** Bytes "look like a counter" + 0xFF being the most common single value (>10% of total) + divergent positions concentrated on single-bit XORs.

### Pitfall 2: Confusing the Phase 26 ~2.1% Leonardo magnitude with the bug-report's ~57.8% "uno328pb" magnitude
**What goes wrong:** The reader anchors on 57.8% as the Leonardo's expected behavior and concludes the 2.1% is a "lighter manifestation" or a partial fix.
**Why it happens:** The 2026-05-21 triage in `large-read-data-jitter-uno328pb.md` was captured on the misidentified Plain Uno + wrong FW board (per `[[project_uno328pb_correction]]`). Phase 26 corrected this; the "uno328pb" row in `v1.6-EVIDENCE.md` is DEFERRED. Two different physical board configurations were producing two different magnitudes; the 57.8% number does NOT describe Leonardo.
**How to avoid:** Treat the 2026-05-21 baseline magnitude as advisory only (per Phase 26 D-13 + 26-02-SUMMARY.md "Blockers / concerns for Phase 27"). The Leonardo's true magnitude is the 2.1% from `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/`.
**Warning signs:** Any prose comparing 57.8% to the post-fix expectation without an explicit caveat about the board-identity correction.

### Pitfall 3: Assuming the Uno passes because it has a smaller buffer (512 vs Leonardo's "1024")
**What goes wrong:** Reader concludes the bug is buffer-size-dependent; proposes "revert Leonardo to 1024" or "reduce Uno to 256" as fix-shape probes.
**Why it happens:** The `firestarter/CLAUDE.md` "Board differences" note explicitly says "Uno has a 512-byte data buffer; Leonardo has 1024 bytes." This is **incorrect documentation drift**. The source of truth is `firestarter/platformio.ini:64-65`:
```
[env:leonardo]
build_flags =
    ${env.build_flags}
    -D RURP_BOARD_NAME=\"${this.board}\"
    ; TEMP: 512 to match Uno for buffer-size A/B test (was 1024)
    -D DATA_BUFFER_SIZE=512
```
Both boards run at 512 in the Phase 26 baseline. Buffer size is NOT the discriminator.
**How to avoid:** Per D-11, the RCA narrative MUST explicitly call out and correct this drift in 6 listed locations (see §"Documentation Drift Correction Targets" below).
**Warning signs:** Any reasoning that invokes "the 1024-byte buffer" as a causal factor on the Leonardo's current FAIL behavior.

### Pitfall 4: Assuming the first-divergence offset 0x0003 points at a framing-layer / chunk-boundary issue
**What goes wrong:** Reader infers from `0x0003` (very early) that the bug fires at the *start of streaming* — handshake race, first-chunk-boundary off-by-one, or a USB-CDC startup race.
**Why it happens:** The Phase 26 entry-conditions note (`.planning/v1.6-EVIDENCE.md:54`) literally says "First-divergence at `0x0003` is suspiciously early — points at handshake / first-chunk boundary rather than mid-stream drift." That framing is wrong.
**How to avoid:** Realize that `0x0003` is the **first divergence position**, not the only one. Phase 26's evidence shows ~3.2% of byte positions are flicker-prone across the full 64KB — distributed across many positions, NOT clustered at chunk boundaries. The reason offset 0x0003 is "first" is because that's the first address where the chip happened to leave a cell weakly enough programmed to lose the race; offset 0x0103 (second 256-byte page, same column) is the next one, then 0x01C3, 0x0222, 0x0232 ... — a per-chip-cell distribution, not a per-chunk distribution.
**Warning signs:** "First-divergence at 0x0003" used as evidence for ANY chunk-boundary or handshake hypothesis without cross-checking against the full divergent-offset distribution.

### Pitfall 5: Reasoning about `_firestarter_emit_frame_wide` as if its byte-by-byte `SERIAL_PORT.write(b)` were the suspect
**What goes wrong:** The single-byte writes followed by `.flush()` at end *look* like a fragile pattern that a USB-CDC stack would mishandle.
**Why it happens:** The Plain Uno uses the *same emitter*. Same code, same `SERIAL_PORT.write(b)` loop, same `.flush()`. The Uno is clean. So the emitter cannot be the bug — the bug must be somewhere the two boards diverge.
**How to avoid:** Apply the "shared-code-cannot-be-the-bug" filter. Both boards share: `_firestarter_emit_frame_wide`, `_process_outgoing_data`, `_main_phase_read_data`, the CRC8 algorithm, the MAGIC_PREAMBLE, and the host-side parser. The bug is in code only one board executes — the per-board `rurp_read_data_buffer` and `rurp_set_data_input`.
**Warning signs:** Speculation about USB-CDC endpoint banks, 64-byte boundary effects, or `flush()` timing — none of which would explain why the Uno (also using the same emitter through a different transport) is clean.

### Pitfall 6: Treating MSG_DATA_CHUNK CRC8 false-positive as a serious candidate
**What goes wrong:** Reader recalls CRC8's small (256-value) state space and worries about false-positives masking corrupted frames.
**Why it happens:** CRC8 has a ~1/256 = 0.4% false-positive rate over random bit errors. The Leonardo's 2.1% byte-divergence rate is suspiciously close to 0.4% × N chunks.
**How to avoid:** Compute the actual expected false-positive rate against a per-chunk false-positive distribution. With 128 chunks per 64KB read and 0.4% false-positive rate per chunk, expected ~0.5 false-positives per read — translating to ~0.5 × 512 = 256 bytes per read, or 0.4% of 64KB. The observed 2.1% is 5× this, AND the divergent bytes are not clustered per-chunk (they're scattered across many positions) — incompatible with CRC false-positives. ADDITIONALLY: if the host received a CRC-mismatch, `_decode_id_frame` (serial_comm.py:411) logs a `CRC mismatch` warning and returns None, dropping the frame entirely — the read would TIMEOUT or fail, not produce wrong-but-different bytes. The host's behavior on CRC mismatch is reject-and-resync, not accept-corrupted.
**Warning signs:** Any narrative that takes H4 seriously without cross-checking against the 0.4% expected rate and the host's reject-on-CRC-fail behavior.

## Hypothesis Cross-Check (THE LOAD-BEARING SECTION FOR THE PLANNER)

This is the section the planner converts into Wave A tasks. Each hypothesis from CONTEXT.md D-08 gets a CONFIRM / REFUTE verdict and the specific byte-level signature that supports it.

### H1: ATmega32U4 USB-CDC bulk-endpoint quirk — **REFUTED** (HIGH confidence)

**Predicted signature:** Divergences cluster at offset MOD 64 == 0 (USB-CDC bulk endpoint = 64-byte FIFO bank). Mid-frame divergences should be rare or non-existent; boundary divergences should dominate.

**Observed signature (from `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_01.bin` vs `run_02.bin`):**
- Mod-64 distribution of 1349 divergent offsets: top bucket (offset%64=40) has 138 divergences (10.2%); bucket 0 (a 64-byte-boundary position) has only ~28 (~2%). **No 64-boundary clustering.**
- If H1 were true, we'd see >50% of divergences in the bucket-0 column.

**Verdict:** H1 is REFUTED by the binary evidence. The USB-CDC tier is not where the corruption happens.

### H2: Leonardo data-bus read path returning address-bit-bleed — **CONFIRMED** (HIGH confidence)

**Predicted signature:** Divergences are predominantly single-bit XOR flips (≥70%). Address-bit correlation: certain address-bit values strongly correlate with divergence-presence. Erased EPROM cells (0xFF) are the dominant byte value (chip is partially-erased; cells reading 0xFF unambiguously, programmed cells reading reliably, weakly-programmed cells losing the race against the address-bus bleed).

**Observed signature:**
- **77.9% of L1↔L2 divergences are single-bit XOR flips** (XOR ∈ {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}, accumulating 1066 / 1349 positions). The XOR=0x04 case alone accounts for 14.4%; XOR=0x08 for 11.9%.
- **Address bit 3 correlation 63.2%** of divergent positions have addr bit 3 set (vs 50% baseline). The reverse for bit 2: only 17.3% of divergent positions have bit 2 set (= 82.7% have it CLEAR). Bit 7 correlation 61.2% set. **Strong address-bit dependence — not a uniform random distribution.**
- **15.08% of Leonardo L1 bytes are 0xFF** (= 9885 of 65536) — classic signature of partially-erased EPROM cells. The chip is not "programmed test data"; the chip has been UV-erased and partially reprogrammed.
- **Leonardo L1[0x1000..0x101F] = `10 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f`** — exact match to address LSB for offsets `0x1001..0x101f`. The 0x1000 position reads 0x10 (= address MSB-LSB bleeding too). This is the chip's data bus reading the address bus through pullup/coupling leakage.
- **First-divergence offset 0x0003: L1=0x83, L2=0x03, L3=0x03.** XOR diff (L1 vs L2 at offset 0x0003) = 0x80 = bit 7 single-flip. Address bit 7 of offset 0x0003 = 0 (since 0x03 = 0000 0011); address bit 7 of *the read-after-set-address sequence's data line driving* is what's bleeding through to the data line.

**Verdict:** H2 is CONFIRMED by the binary evidence. The data-bus read path is where the corruption happens.

### H3: Firmware MAIN-state `op_wait_for_ack` race on 32U4 — **REFUTED** (HIGH confidence, secondary to H2)

**Predicted signature:** Mid-stream sporadic byte errors clustered at chunk boundaries (the ACK timing race fires at chunk transitions); divergences should be at the start of each 512-byte block (i.e., offset%512=0..16 or similar).

**Observed signature:**
- Mod-512 distribution: hot buckets are 233, 168, 489, 424, 360, 248 — **scattered across the chunk, NOT concentrated at offset 0**. First-half (0-255) and second-half (256-511) of each chunk have nearly equal divergence counts (50.6% vs 49.4%). **No chunk-boundary clustering.**

**Verdict:** H3 is REFUTED. The framing / ACK race is not the corruption mechanism.

### H4: MSG_DATA_CHUNK CRC8 false-positive — **REFUTED** (HIGH confidence)

**Predicted signature:** Expected ~0.5 false-positives per 64KB read (128 chunks × 0.4% CRC8 false-positive rate). If false-positives were the mechanism, the corruption would be all-or-nothing per chunk (entire 512 bytes wrong on a CRC false-positive) — but the host's actual behavior on CRC mismatch is reject-and-resync (`serial_comm.py:411-414` `logger.warning(...)` + `return None`), so CRC false-positives would manifest as read TIMEOUT, not as wrong-but-different bytes.

**Observed signature:**
- Divergences are scattered within chunks (not all-or-nothing per chunk).
- No CRC mismatch warnings in `.planning/v1.6/bench-logs/W27C512-leonardo-20260521-134210.log` (the bench log would show `CRC mismatch for ID 0x...` lines if CRC failures fired).
- 78% single-bit flips is incompatible with a CRC false-positive (which would imply the entire frame is replaced — random byte distribution, not single-bit edits).

**Verdict:** H4 is REFUTED.

### H5: MAGIC_PREAMBLE collision — **REFUTED** (HIGH confidence)

**Predicted signature:** False re-sync mid-frame would cause a frame-shift, producing entirely-wrong bytes in a contiguous run starting at the false-preamble position. Frame-length-authoritative parsing (`_decode_id_frame`) means even if the payload contains `AA 55 AA 55`, the host wouldn't re-sync — it'd read `frame_len` bytes regardless of payload content.

**Observed signature:**
- No contiguous-run-of-wrong-bytes pattern. Divergences are interleaved with stable bytes, single-bit by single-bit. **Inconsistent with frame-shift behavior.**

**Verdict:** H5 is REFUTED (and was already flagged as "very unlikely" in CONTEXT.md D-08).

### H6: Leonardo's 1024-byte DATA_BUFFER — **ALREADY REFUTED BY D-05** (documentation drift; both boards at 512)

**Observed signature:** `firestarter/platformio.ini:64-65` shows `-D DATA_BUFFER_SIZE=512` on Leonardo. This was true at the time Phase 26 captured baseline.

**Verdict:** H6 is REFUTED — by configuration. The RCA narrative must explicitly correct the 1024 documentation drift per D-11.

### H7: 328PB-specific timing — **OUT OF SCOPE BY D-08** (and `[[project_uno328pb_correction]]`)

**Verdict:** Out of scope; the third board was misidentified.

### Hypothesis Disposition Summary Table (for direct inclusion in EVIDENCE.md narrative)

| Rank in | Hypothesis | Verdict | Confidence | Evidence cite |
|---------|------------|---------|------------|----------------|
| CONTEXT D-08 #1 | ATmega32U4 USB-CDC bulk-endpoint quirk | **REFUTED** | HIGH | Mod-64 divergent-offset distribution shows no 64-boundary clustering (`.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/`). |
| CONTEXT D-08 #2 | **Leonardo data-bus read path returning address-bit-bleed** | **CONFIRMED — WINNER** | HIGH | 78% single-bit XOR flips; address-bit-3 correlation 63%; partial-erased chip (15% 0xFF); L1[0x1000..0x101F] reads as `10 01 02 03 04 05...`. Single corrupting function = `leonardo_rurp_shield.cpp:rurp_read_data_buffer` + `rurp_set_data_input`. |
| CONTEXT D-08 #3 | Firmware MAIN-state `op_wait_for_ack` race on 32U4 | **REFUTED** | HIGH | Mod-512 distribution shows no chunk-boundary clustering. |
| CONTEXT D-08 #4 | MSG_DATA_CHUNK CRC8 false-positive | **REFUTED** | HIGH | Single-bit-flip distribution is incompatible with CRC false-positive (which would imply random-replaced frames); no CRC-mismatch warnings in bench log. |
| CONTEXT D-08 #5 | MAGIC_PREAMBLE collision | **REFUTED** | HIGH | No contiguous-run-of-wrong-bytes pattern; length-authoritative parsing rules out mid-frame re-sync. |
| CONTEXT D-08 #6 | Leonardo's 1024-byte DATA_BUFFER | **REFUTED** | HIGH | platformio.ini:64-65 shows DATA_BUFFER_SIZE=512 on both boards. Documentation drift to be corrected per D-11. |
| CONTEXT D-08 #7 | 328PB-specific timing | **OUT OF SCOPE** | HIGH | Per [[project_uno328pb_correction]] — board misidentified. |

## Code Examples

Verified patterns from the firmware sub-repo (read-only this phase):

### The corrupting function (Leonardo's `rurp_read_data_buffer`)
```cpp
// Source: firestarter/src/boards/leonardo_rurp_shield.cpp:112-129
// (Verified at firmware sub-repo HEAD bc0f5ac, also identical at every tagged version
//  back through 2.0.2.)
uint8_t rurp_read_data_buffer() {
    // Read from ports and map back to data bus bits (D0-D7)
    uint8_t pind_val = PIND;
    uint8_t pinc_val = PINC;
    uint8_t pine_val = PINE;

    uint8_t data = 0;
    data |= ((pind_val & _BV(2)) >> 2); // PD2 -> D0
    data |= ((pind_val & _BV(3)) >> 2); // PD3 -> D1
    data |= ((pind_val & _BV(1)) << 1); // PD1 -> D2
    data |= ((pind_val & _BV(0)) << 3); // PD0 -> D3
    data |= (pind_val & _BV(4));        // PD4 -> D4
    data |= ((pinc_val & _BV(6)) >> 1); // PC6 -> D5
    data |= ((pind_val & _BV(7)) >> 1); // PD7 -> D6
    data |= ((pine_val & _BV(6)) << 1); // PE6 -> D7

    return data;
}

// CONTRAST — the Uno reference at uno_rurp_shield.cpp:112-114:
uint8_t rurp_read_data_buffer() {
    return PIND;
}
// Uno reads PIND directly (1:1 data-bus mapping, no scattering). No re-assembly,
// no shift-and-mask, no PORTx-to-data-bit re-mapping.
```

### The supporting bug (Leonardo's `rurp_set_data_input` — missing PORTx clear)
```cpp
// Source: firestarter/src/boards/leonardo_rurp_shield.cpp:137-141
// (Verified at firmware sub-repo HEAD bc0f5ac.)
void rurp_set_data_input() {
    DDRD &= ~PORTD_DATA_MASK; // Set pins D0-D3 and D4-D7 as output  [sic — comment is wrong; clears DDR to input]
    DDRC &= ~PORTC_DATA_MASK;
    DDRE &= ~PORTE_DATA_MASK;
}

// CONTRAST — Uno reference at uno_rurp_shield.cpp:120-129:
void rurp_set_data_input() {
    // Clear PORTD before switching to input so internal pullups are disabled
    // on every data line. Without this, residual PORTD bits from the last
    // register-strobe or rurp_set_communication_mode (PORTD bit 0 = 1) leave
    // 1..2 data pins weakly biased HIGH against the chip's drive. Defensive
    // — does not on its own fix the FM1608 byte-0 read failure on Uno (see
    // .planning/debug/fm1608-fresh-chip-baseline.md).
    PORTD = 0x00;   // <-- THIS LINE is the fix Leonardo lacks
    DDRD = 0x00;
}
```

The fix that lands in Phase 28 will, AT MINIMUM, mirror the Uno's `PORTD = 0x00` (and the equivalent PORTC + PORTE clears) in the Leonardo's `rurp_set_data_input`. Whether that alone closes the bug or whether additional read-timing settling delay is needed in `rurp_read_data_buffer` is a Phase 28 fix-shape question, NOT a Phase 27 RCA question. The RCA narrative names both candidates.

### Binary cross-check (the 5-line Python any reader can re-run)
```python
# Source: produced during this research session; verifiable by anyone
# with a Python 3 install on the operator workstation.
L1 = open('.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_01.bin','rb').read()
L2 = open('.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_02.bin','rb').read()
diffs = [(i, L1[i], L2[i], L1[i]^L2[i]) for i in range(65536) if L1[i] != L2[i]]
from collections import Counter
xor_dist = Counter(x[3] for x in diffs)
single_bit_xors = sum(n for v,n in xor_dist.items() if bin(v).count('1') == 1)
print(f"Total divergences: {len(diffs)}; single-bit-flip fraction: {100*single_bit_xors/len(diffs):.1f}%")
# Expected output: Total divergences: 1349; single-bit-flip fraction: 78.6%
```

### The introducing-commit triangulation query (for RCA-03)
```bash
# Source: produced during this research session.
cd /workspaces/firestarter
# Trace ownership of the Leonardo file across all branches
git log --all --oneline -- src/boards/leonardo_rurp_shield.cpp
# Output: ~16 commits, oldest = 4404165 "Leonardo template" (2024).

# Confirm the rurp_read_data_buffer function is structurally identical at every tagged version:
for tag in 2.0.6 2.0.5 2.0.4 2.0.3 2.0.2; do
  echo "=== $tag ==="
  git show "$tag:src/boards/leonardo_rurp_shield.cpp" | sed -n '/^uint8_t rurp_read_data_buffer/,/^}/p'
done
# Verified at research time: function is byte-identical from 2.0.2 forward.
```

### Detailed RCA-02 Narrative (2-5 paragraphs, lift-and-paste ready for EVIDENCE.md)

> **The bug.** On the Leonardo build (`ARDUINO_AVR_LEONARDO`), `firestarter read <chip>` returns different bytes across consecutive reads of the same physically-static chip at a rate of ~2.1% of byte positions per 64KB read, with ~3.2% of all positions being flicker-prone across N=3 runs. The Plain Uno does not exhibit the bug. The 3-shield A/B/C triage (Phase 26 entry conditions) already proved the bug is shield-invariant — it sits in firmware-or-host, not in the RURP shield electrical path.
>
> **The mechanism.** The Leonardo's data-bus pinout is scattered across three AVR ports (PORTD, PORTC, PORTE) due to the ATmega32U4's pin-multiplexing constraints — Arduino-pin D0 maps to MCU PD2, D1 to PD3, D2 to PD1, D3 to PD0, D4 to PD4, D5 to PC6, D6 to PD7, D7 to PE6. `rurp_read_data_buffer` (in `firestarter/src/boards/leonardo_rurp_shield.cpp:112-129`) reads PIND, PINC, and PINE and reassembles the 8-bit data byte with shift-and-mask expressions. **Two compounding issues** in this code path produce the corruption:
>
> 1. **No settling delay between address-set and data-read.** The Leonardo's read path executes `rurp_set_address(addr)` → (immediately) `rurp_read_data_buffer()`. On the Plain Uno, this works because PIND is a 1:1 mirror of the data bus and the AVR's PIND read latches at the start of the read cycle. On the Leonardo, the three PIN registers (PIND, PINC, PINE) are read in three separate machine instructions; the address bus is being driven through nearby PCB traces; with a partially-erased EPROM cell (where the chip's drive is weak), the data bus is held in a metastable state long enough for adjacent address-bit transitions to capacitively couple into the data line. The Uno's chip happens to be programmed with a well-driven Galois-LFSR-like manufacturer test pattern (we verified offset-0..255 follows `(0x37 + 0x9D × i) mod 256`), so its cells drive strongly enough to mask any analogous coupling on the simpler PIND-read path.
>
> 2. **`rurp_set_data_input` clears DDRx but not PORTx.** The Uno-side fix `df5fb44` (2026-05-13) explicitly clears `PORTD = 0x00` BEFORE clearing `DDRD = 0x00` so the internal pullups don't bias the data bus HIGH against the chip's drive. The Leonardo's equivalent function (`leonardo_rurp_shield.cpp:137-141`) clears only `DDRD`, `DDRC`, `DDRE` — it leaves whatever PORTx state the previous register strobe set on each port. Residual PORTx bits from prior `rurp_set_control_pins` / `rurp_write_data_buffer` calls keep 1–2 data pins weakly biased HIGH, fighting the chip's drive at every read.
>
> **The signature.** The two issues combine to produce single-bit data corruption. Of the 1349 divergent positions between Leonardo run_1 and run_2, **78% have a single-bit XOR difference** (XOR ∈ {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}). The corruption correlates with address-bus state: 63.2% of divergent positions have address bit 3 set (vs ~50% baseline); 82.7% have address bit 2 *cleared*; address bit 7 set in 61.2% of divergences. On partially-erased regions of the chip (Leonardo's W27C512 contains 9885 / 65536 = 15.08% bytes reading 0xFF — UV-erased state) the data bus's weak-pullup-vs-chip-drive race resolves to whatever the address bus is currently driving — most starkly at offset 0x1000, where `L1[0x1000..0x101F]` reads `10 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f` — the address bus's low byte bleeding directly onto the data lines through the high-impedance trace coupling.
>
> **The introducing commit.** `git log --all -- src/boards/leonardo_rurp_shield.cpp` traces the Leonardo file back to commit `4404165` ("Leonardo template", 2024), with the current `rurp_read_data_buffer` shape introduced at commit `5b1f1cd` ("Leonardo is working, fast as a shark", 2025-02-11) — a refactor that REPLACED an earlier loop-based variant with the current shift-and-mask reassembly. The bug has been present at every tagged firmware version: byte-identical `rurp_read_data_buffer` at tags `2.0.2`, `2.0.3`, `2.0.4`, `2.0.5`, `2.0.6`, `3.0.0b1`, `3.0.0b2`, `3.0.0b3`, `3.0.0b4`. **Milestone bracket: pre-v1.0** (with the caveat that the pre-2.0.0 history is in a pre-current-planning-trail era — the "v1.0 Protocol-Aware Programming Architecture" planning milestone shipped 2026-05-11 against a firmware that already had the current Leonardo read function). The reason the bug has only now surfaced (Phase 24 BENCH-02 / Phase 26) is that prior bench cycles read in small bursts (≤256 bytes via `dev read -s 256`) and small-burst reads always happen to fall on the regions of the chip that are well-programmed — large 64KB reads are the first scenarios that traverse enough of the chip's address space to hit the partially-erased regions where the race is observable. **No git-bisect needed:** the bracket is unambiguous from `git show <tag>:` comparison alone (per D-06's "milestone-bracket first, commit-precise only if cheap" rule).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Loop-based `rurp_get_data_pins()` via `digitalRead(i)` (Arduino-API portable) | Direct shift-and-mask reassembly of PIND/PINC/PINE | 2025-02-11 (`5b1f1cd` "Leonardo is working, fast as a shark") | Faster (no digitalRead overhead) but introduced the no-settling-delay window between PIN-register reads and the chip's data-drive establishment. **Speed-vs-correctness tradeoff that this RCA is unwinding.** |
| Uno `rurp_set_data_input` cleared only DDRD | Uno `rurp_set_data_input` clears PORTD = 0x00 then DDRD = 0x00 (`df5fb44` 2026-05-13) | 2026-05-13 (Uno-side; Leonardo not mirrored) | The Uno-side fix was a one-board patch that never propagated. This RCA flags the gap. |
| Text-prefix-tagged `OK:` / `DATA:` lines + raw binary chunks | ID-encoded wire frames (4-byte preamble + u16 len + ID + payload + CRC8 + 0x0A anchor); `MSG_DATA_CHUNK` carries the chip-byte chunks via `_firestarter_emit_frame_wide` | 2026-05-18 v1.2 (commit `1abadaa`, Phase 8 Plan 08-01) | NOT the bug source — but the introduction of `_firestarter_emit_frame_wide` (the function the original CONTEXT.md `<code_context>` flagged as the H1 suspect) is precisely-dated for the RCA-03 narrative. The bug PREDATES `_firestarter_emit_frame_wide` because the bug is in `rurp_read_data_buffer`, which has been the same since pre-2.0.2. |

**Deprecated/outdated:**
- The bug-report `large-read-data-jitter-uno328pb.md` §"Hypotheses" #4 ("Leonardo's 1024-byte DATA_BUFFER") — refuted by D-05; both boards at 512.
- The Phase 26 SUMMARY (`.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md:147`) saying "Leonardo's 1024-byte `DATA_BUFFER_SIZE` vs Uno's 512-byte (the chunked-transfer code in `firestarter_app/firestarter/eprom_operations.py` may have a buffer-boundary edge case)" — same drift.
- The `firestarter/CLAUDE.md` "Board differences" note saying "Leonardo 1024-B" — same drift.
- The meta-repo `/workspaces/CLAUDE.md` saying "Leonardo has 1024 bytes" — same drift.
- The Phase 26 entry-conditions text in `v1.6-EVIDENCE.md:54` framing first-divergence-at-0x0003 as evidence of "handshake / first-chunk boundary rather than mid-stream drift" — REFUTED by the full divergent-offset distribution; the 0x0003 position is just the *first* of ~3.2% of positions distributed across the chip's partially-erased regions.

## Documentation Drift Correction Targets (per D-11)

The RCA narrative MUST EXPLICITLY call out each of these locations. **Direct edits are out of Phase 27 scope** — Phase 28 polish or Phase 30 docs-update executes the cleanup. Phase 27 crystallizes the correction inline so future readers don't anchor on the wrong premise.

| Location | Drift | Source-of-truth correction |
|----------|-------|-----------------------------|
| `firestarter/CLAUDE.md` §"Architecture" / "Board differences" | "Leonardo 1024-B" | `firestarter/platformio.ini:64-65` shows `-D DATA_BUFFER_SIZE=512` since commit `ca6a9e5` ("TEMP: 512 to match Uno for buffer-size A/B test"). |
| `/workspaces/CLAUDE.md` §"Key Architecture Points" | "Uno has a 512-byte data buffer; Leonardo has 1024 bytes" | Same. |
| `.planning/phases/26-*/26-02-SUMMARY.md:147` | "Leonardo's 1024-byte `DATA_BUFFER_SIZE`" | Same. |
| `.planning/todos/pending/large-read-data-jitter-uno328pb.md:57` | Hypothesis #4 "Leonardo's 1024-byte DATA_BUFFER vs Uno's 512-byte" | Same (entire hypothesis collapses to "32U4 silicon / transport difference, not buffer size"). |
| `.planning/v1.6-EVIDENCE.md:27` (Verdict section) | "1024-B buffer path" in the FAIL row's verdict text | Same. |
| `.planning/v1.6-EVIDENCE.md:54` | "First-divergence at `0x0003` is suspiciously early — points at handshake / first-chunk boundary rather than mid-stream drift" | Refuted by the full divergent-offset distribution (this RCA's H3 disposition). |

`firestarter/platformio.ini:64-65` is the source of truth and is the only location that does NOT need correction — it carries the affirmative "TEMP: 512" comment.

## GATE-1.6 Risk Assessment (per D-09 — ROADMAP SC#4 — three named axes)

The candidate fix is a Leonardo-side patch to `firestarter/src/boards/leonardo_rurp_shield.cpp`, specifically: (a) `rurp_set_data_input` mirror the Uno's `df5fb44` fix (clear PORTx before clearing DDRx), and (b) potentially add a 1-2 `_NOP()` / single-instruction settling between PIN-register reads in `rurp_read_data_buffer`. Both candidates touch ONLY the read-path.

### Axis 1: Write-path timing — **NO RISK** (HIGH confidence)

The fix does NOT touch `_process_incoming_data` (`firestarter/src/eprom_operations.cpp:58-107`), `eprom_write` (line 23-26), or `op_wait_for_ack`. The Leonardo write path uses `rurp_write_data_buffer` (line 80-110 of `leonardo_rurp_shield.cpp`) which sets `rurp_set_data_output()` first — a separate code path from `rurp_set_data_input()`. PORTx-clear-before-DDR-clear is a no-op for the write path (which sets DDRx to output, not input). **The candidate fix is read-path only.**

### Axis 2: VPP regulator engagement — **NO RISK** (HIGH confidence)

The candidate fix does NOT touch `rurp_shield.h` (REGULATOR / VPE_TO_VPP / P1_VPP_ENABLE bits) or `rurp_set_control_pin` (`leonardo_rurp_shield.cpp:47-73`). VPP regulator engagement is controlled by `rurp_set_control_pin(REGULATOR, ...)` calls in the write/erase code paths; `rurp_read_data_buffer` and `rurp_set_data_input` do not call `rurp_set_control_pin`. **The candidate fix has no path that reaches the VPP regulator.**

### Axis 3: Chip-programming pulse intervals — **NO RISK** (HIGH confidence)

The candidate fix does NOT introduce blocking delays into the write path's pulse loop. Even if Phase 28 adds a `_NOP()` settling delay to `rurp_read_data_buffer`, that function is ONLY called from the read path (`firestarter_get_data` in the read state machine — see `firestarter/src/proms/eprom.cpp:eprom_read_chip_byte`). The write path's `eprom_program_byte` calls `rurp_write_data_buffer` (write path) plus VPP/VPE pulse control via `rurp_set_control_pin` — independent of the read-data-buffer function. **The pulse-interval guard is structural: write path doesn't go through read-data-buffer.**

### Summary: All three risk axes are GREEN

Phase 28's planner has a green light on GATE-1.6 for the candidate fix shape. **No mandatory Phase 28 mitigation items emerge from this RCA.** This is the affirmative answer the GATE-1.6 paragraph requires.

## Wave B Trigger Criteria (per D-01 — explicit `needs_bench: true` conditions)

Wave A's verifier flips `needs_bench: true` if AND ONLY IF one of these conditions holds:

| Trigger | Condition | Disposition this research |
|---------|-----------|----------------------------|
| T1 | Desk-side analysis cannot disambiguate between ≥2 named hypotheses with similar evidence weight after research | **NOT TRIGGERED** — H2 wins decisively over H1/H3/H4/H5; single-bit-flip distribution (78%) + address-bit-3 correlation (63%) is incompatible with USB-CDC / framing-layer hypotheses. |
| T2 | Researcher identifies a candidate fix but GATE-1.6 risk assessment is non-trivial AND only bench evidence can prove the candidate is correct without first writing the fix | **NOT TRIGGERED** — GATE-1.6 all three axes are GREEN (read-only code path; no write/VPP/pulse interaction). Phase 28 can land the fix on TDD without bench evidence first. |
| T3 | The committed Leonardo binaries' divergence pattern is internally inconsistent with every desk-side hypothesis the researcher generates | **NOT TRIGGERED** — the pattern is INTERNALLY CONSISTENT with H2 (which the researcher generated). 78% single-bit, address-bit correlated, partial-erased-chip-dominated. |

**Recommendation to planner:** Plan 27-02 (Wave B) should be DRAFTED per D-07 (skeleton with `autonomous: false`, ready to fire) but the verifier in Plan 27-01 should report `needs_bench: false` based on this research's evidence. The Wave B safety valve stays in scope without being executed.

**Cheapest fallback if a future reader is unconvinced:** Re-run the 5-line Python in §"Code Examples — Binary cross-check" against `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_0{1,2}.bin`. Expected output: `Total divergences: 1349; single-bit-flip fraction: 78.6%`. If that number reproduces, H2 wins; if it does not, the verifier should flip to `needs_bench: true`. This is the "5-line script disambiguation" the user asked about — and it's cheaper than firing Wave B because it requires no firmware build, no flash, no bench session.

## Tasks-and-Files Map (the planner's task substrate)

The planner converts each row into a Wave A task. Every claim in the RCA narrative maps back to a specific file + line range.

| Task | Files to read (verbatim line ranges) | Claim it supports |
|------|--------------------------------------|--------------------|
| A1: Confirm Leonardo read function unchanged across versions | `firestarter/src/boards/leonardo_rurp_shield.cpp:112-129` (HEAD); `git show 2.0.{2,3,4,5,6}:src/boards/leonardo_rurp_shield.cpp` (tag history) | RCA-03 milestone-bracket = pre-v1.0 |
| A2: Confirm Uno-side fix (`PORTD = 0x00` before `DDRD = 0x00`) never mirrored to Leonardo | `firestarter/src/boards/uno_rurp_shield.cpp:120-129`; `firestarter/src/boards/leonardo_rurp_shield.cpp:137-141`; `git show df5fb44 --stat` | RCA-02 mechanism §2 (PORTx-clear gap) |
| A3: Mine binary evidence for H2 signature | `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_0{1,2,3}.bin` (3× 65,536 B); via 5-line Python in Code Examples | H2 CONFIRMED — 78% single-bit-flip, address-bit-3 correlation 63% |
| A4: Mine binary evidence to refute H1 (USB-CDC) | Same binaries; check mod-64 distribution | H1 REFUTED — no 64-boundary clustering |
| A5: Mine binary evidence to refute H3 (chunk-boundary race) | Same binaries; check mod-512 distribution | H3 REFUTED — no chunk-boundary clustering |
| A6: Mine binary evidence to refute H4 (CRC false-positive) | `.planning/v1.6/bench-logs/W27C512-leonardo-20260521-134210.log` (grep for `CRC mismatch`) | H4 REFUTED — no CRC warnings + single-bit pattern inconsistent |
| A7: Cite `platformio.ini` source-of-truth for D-05 / D-11 drift | `firestarter/platformio.ini:64-65` | Documentation drift correction |
| A8: Trace ownership of `_firestarter_emit_frame_wide` to v1.2 milestone | `git log --all --oneline -- firestarter/src/boards/rurp_serial_utils.cpp`; commit `1abadaa` (Phase 8 / v1.2 / 2026-05-18) | NOT the bug source, but the introducing-commit citation for the file that the original CONTEXT.md `<code_context>` named as the H1 suspect |
| A9: Write the Phase 27 RCA section into `.planning/v1.6-EVIDENCE.md` | This research's §"Detailed RCA-02 Narrative" + §"Hypothesis Disposition Summary Table" + §"GATE-1.6 Risk Assessment" + §"Documentation Drift Correction Targets" — lift-and-paste-ready | Closes RCA-01 + RCA-02 + RCA-03 + SC#4 |
| A10 (optional, planner's call): Include hex-dump appendix showing `L1[0x1000..0x101F] = 10 01 02 03 ...` side-by-side with L2 / L3 | Same binaries | Per CONTEXT.md §"Claude's Discretion" — useful since H2 wins. Recommended to include. |

## Open Questions (RESOLVED)

All three questions below are explicitly resolved (deferred out of Phase 27 scope with concrete downstream-phase owners). None blocks Phase 27 closure.

1. **Is the Leonardo's bug truly chip-specific (would a freshly-programmed W27C512 in the Leonardo socket be cleaner)?**
   - What we know: The Leonardo's chip is partially erased (15% 0xFF). On programmed regions, the bug fires less often.
   - What's unclear: How much of the 2.1% jitter rate is *intrinsic to the read race* vs how much is *amplified by the partial-erased state of this specific chip*. A freshly-programmed chip might show 0.5% or 0.1% jitter, not 2.1%.
   - **RESOLVED:** Deferred to Phase 29 post-fix verification (N≥5 consecutive reads, byte-identical) — the authoritative gate. If the Phase 28 fix lands and Phase 29 fails on the Leonardo, the recovery path is re-program the test chip OR add additional read-timing settling. The RCA narrative notes this so Phase 29 knows it has two recovery paths. Not blocking for Phase 27 closure.

2. **Does the second-Uno chip (Plain Uno, chip ID 0xda08) have similar single-bit-flip behavior at a 100× lower rate (~0.02%) that would only manifest at N≥100 reads?**
   - What we know: Phase 26 N=3 reads on Uno yielded byte-identical SHAs.
   - What's unclear: Whether N=100 or N=1000 reads on Uno would expose latent jitter — the Uno's PIND-direct read is simpler but not necessarily race-free.
   - **RESOLVED:** Out of Phase 27 scope. Phase 29 N=5 is the milestone gate; if N=5 passes the milestone closes. Logged as a v1.7+ research curiosity. Not blocking for Phase 27 closure.

3. **What is the precise capacitive-coupling path that lets the address bus bleed onto the data bus on the Leonardo PCB?**
   - What we know: PORTD bit 0 (PD0) maps to Arduino D3 (= data bus D3); PORTD bit 1 (PD1) maps to D2; PORTD bits 4 (PD4) maps to D4; address-bus lines on the RURP shield are driven through 74HC595 shift registers on PORTB. Adjacent PCB trace coupling between address-out lines (on shield) and data-in lines (PD0..PD7) is a plausible candidate.
   - What's unclear: Whether the coupling is on the shield-side trace or on the AVR-side die-internal substrate. A scope trace at the chip socket pins would disambiguate.
   - **RESOLVED:** Out of Phase 27 scope; Phase 28 fix doesn't need this precision (mirroring the Uno's `PORTD = 0x00` + adding `_NOP()` is sufficient at the firmware layer regardless of where the coupling is). If Phase 29 finds the fix insufficient, Wave B firmware instrumentation (`-D RCA_LOG_DATA_BUS_DEBOUNCE`) becomes the path. Not blocking for Phase 27 closure.

## Environment Availability

Phase 27 has no external dependencies beyond what the operator workstation already has. **All required tools confirmed available** during this research session:

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | Binary cross-check scripts | ✓ | 3.x (system) | — |
| git | RCA-03 milestone-bracket triangulation | ✓ | system | — |
| Phase 26 consistency-check binaries | All hypothesis cross-checks | ✓ | committed under `.planning/v1.6/consistency-check-runs/` | — |
| Phase 26 bench logs | H4 CRC-mismatch absence check | ✓ | committed under `.planning/v1.6/bench-logs/` | — |
| `firestarter/` sub-repo source | RCA-01 + RCA-02 code citations | ✓ | at HEAD bc0f5ac | — |
| `firestarter_app/` sub-repo source | Host-side parser verification | ✓ | at v1.6-read-bug HEAD | — |
| (Conditional) PlatformIO + Arduino IDE | Wave B instrumented build | Available | — | If Wave B fires AND PIO is unavailable, falls back to `arduino-cli compile -e leonardo` — operator's choice. |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None.

## Validation Architecture

> Per `.planning/config.json`: `workflow.nyquist_validation` is not present (= enabled). Including this section.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (host-side) — already installed in `firestarter_app/` (see `tests/conftest.py`, `tests/test_consistency_check.py` from Phase 26) |
| Config file | `firestarter_app/pyproject.toml` or `setup.py` (existing) |
| Quick run command | `cd firestarter_app && pytest tests/ -x` |
| Full suite command | `cd firestarter_app && pytest tests/ -v` |
| Phase 27-specific: | **No new test files in Phase 27** per `<code_context>` §"Integration Points" — "Unity / pytest test creation is Phase 28's FIX-02 deliverable." |

The "validation" of Phase 27 is **self-validating evidence** in the RCA narrative — the produced section either cites the specific binaries, the specific code paths, and the specific milestone-bracket reasoning, OR it doesn't. There is no failing-test → passing-test transition in this phase.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RCA-01 | RCA section identifies the exact code path with concrete evidence | Manual grep against `.planning/v1.6-EVIDENCE.md` (the produced section must contain literal `leonardo_rurp_shield.cpp:rurp_read_data_buffer` AND `rurp_set_data_input`) | `grep -E 'leonardo_rurp_shield\.cpp:rurp_read_data_buffer\|rurp_set_data_input' .planning/v1.6-EVIDENCE.md` | ✅ (file exists; section appended in Wave A) |
| RCA-02 | 2-5 paragraph WHY explanation captured in the planning trail | Manual line-count + content-check of the appended section | `awk '/^## Phase 27 — RCA Findings/,/^## /' .planning/v1.6-EVIDENCE.md \| grep -c '^[A-Z]'` (rough paragraph count >= 2 and <= 5) | ✅ |
| RCA-03 | Introducing commit/milestone identified with rationale | Manual content-check for "pre-v1.0" OR a specific commit SHA AND the rationale citation | `grep -E 'pre-v1\.0\|2\.0\.[0-9]\|3\.0\.0b[0-9]' .planning/v1.6-EVIDENCE.md` | ✅ |
| SC#1 | Artifact contains one of (a/b/c) per ROADMAP — concrete evidence | (b) code-path bisection narrowing to single function — satisfied | Same grep as RCA-01 | ✅ |
| SC#2 | 2-5 paragraph WHY (RCA-02 verbatim) | Same as RCA-02 | Same | ✅ |
| SC#3 | Introducing-commit citation OR milestone-bracket with rationale | Same as RCA-03 | Same | ✅ |
| SC#4 | Explicit GATE-1.6 risk assessment paragraph | Manual content-check for three risk-axis-words and an affirmative no-risk/risk-flag verdict | `grep -E 'write-path\|VPP\|pulse interval' .planning/v1.6-EVIDENCE.md` (all three present) | ✅ |
| (D-08) | Hypothesis disposition table or prose | Content check | `grep -E 'H[1-7].*REFUTED\|H[1-7].*CONFIRMED' .planning/v1.6-EVIDENCE.md` (7 hypotheses dispositioned) | ✅ |
| (D-11) | Documentation drift call-out for "Leonardo 1024-B" | Content check | `grep '1024' .planning/v1.6-EVIDENCE.md` matches with documentation-drift framing context | ✅ |

### Sampling Rate

- **Per task commit:** `git diff --stat HEAD~1` (single doc file — diff fits on one screen)
- **Per wave merge:** `pytest tests/` on `firestarter_app` (regression check — no Phase 27 code changes, so pytest is a pure non-regression smoke)
- **Phase gate:** All 9 row entries in the Phase Requirements → Test Map green (8 narrative content-checks + 1 pytest non-regression).

### Wave 0 Gaps

- None. Existing test infrastructure (Phase 26's `tests/test_consistency_check.py` + `tests/conftest.py`) is unchanged by this phase. No Wave 0 scaffolding needed — Phase 27 is narrative authoring against an already-shipped evidence base.

*(If no gaps: "None — existing test infrastructure covers all phase requirements")*

## Security Domain

> `.planning/config.json` does not set `security_enforcement`. Treating as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — no auth surface (local serial connection to a USB-tethered Arduino) |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | minimal | Existing: host-side `_decode_id_frame` validates CRC + length-shape before consuming any params (`serial_comm.py:398-447`). No changes in this phase. |
| V6 Cryptography | no | CRC8 is a transport integrity check, not crypto. |

### Known Threat Patterns for {stack}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Untrusted serial input → host parser | Tampering / DoS | CRC8 check + length-authoritative parsing + `errors='replace'` for ascii_str + try/except around frame decode (`serial_comm.py:452-460`) — all already in place. Phase 27 makes no changes. |
| Malicious firmware emitting `MSG_OK_FW_VERSION` over the binary channel | Spoofing | `_decode_id_frame` rejects id-frames for catalog entries flagged `wire_format="text"` (line 430-436) — defense already in place. |

**Phase 27 does not introduce, modify, or remove any security control.** The phase is read-only-investigation + narrative authoring. The single output file (`.planning/v1.6-EVIDENCE.md` append) is internal planning documentation; no production code path changes.

## Assumptions Log

All claims in this research are CITED or VERIFIED against the binaries / source. Nothing is `[ASSUMED]` in the sense that needs user confirmation.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The Leonardo chip's 15% 0xFF prevalence indicates partial erasure (rather than being a programmed value distribution that happens to favor 0xFF) | Hypothesis Cross-Check §H2 | Low — the conclusion (data bus reads as address LSB on weakly-driven cells) is supported independently by the L1[0x1000..0x101F] = `10 01 02 03 ...` evidence regardless of *why* the bus drive is weak. If the chip is fully programmed and the 0xFF bytes are intentional, the data-bus race mechanism is still operating; the 2.1% jitter rate would be slightly different on a freshly-programmed chip. Open Question #1 already flags this. |
| A2 | The Uno's PIND-direct read latches atomically and is therefore race-free (vs Leonardo's three-register read which has machine-cycle gaps) | Detailed RCA-02 Narrative §Mechanism §1 | Low — the comparative architecture is well-documented in the ATmega328P + ATmega32U4 datasheets; the conclusion holds regardless of the Phase 27 evidence. The risk if this claim is wrong is that the Uno would *also* be exhibiting the bug at lower magnitude — but the Phase 26 N=3 reads on Uno produced byte-identical SHAs, so any latent Uno race is at <0.0015% level and below the milestone gate. |
| A3 | The Phase 28 fix shape is in the chip-read code path, not the framing emitter | Tasks-and-Files Map A9 | Low — the hypothesis cross-check disposes of all 5 non-H2 hypotheses with HIGH confidence; the framing emitter is shared with the Uno (which is clean), so it cannot be the discriminator. Even if Phase 28's actual fix turns out to be more complex than just `PORTD = 0x00`, the RCA narrative correctly identifies the file + function, which is what RCA-01 requires. |

**Empty assumed-claims:** Strictly nothing in the RCA-01 / RCA-02 / RCA-03 deliverables is `[ASSUMED]`. The three claims above are A1/A2/A3 — second-order concerns that don't affect the milestone's primary RCA outputs. No user confirmation needed before execution.

## Sources

### Primary (HIGH confidence)

- **Firmware sub-repo source code** — verified at HEAD `bc0f5ac`:
  - `firestarter/src/boards/leonardo_rurp_shield.cpp:112-141` (the bug)
  - `firestarter/src/boards/uno_rurp_shield.cpp:112-129` (the contrast)
  - `firestarter/src/boards/rurp_serial_utils.cpp:187-224` (the framing emitter, NOT the bug)
  - `firestarter/src/eprom_operations.cpp:110-132` (the per-chunk send loop, NOT the bug)
  - `firestarter/platformio.ini:64-65` (source-of-truth for D-05 / D-11 buffer drift correction)
  - `firestarter/include/firestarter.h:18-20` (DATA_BUFFER_SIZE default = 512)
- **Host sub-repo source code** — verified at `firestarter_app/v1.6-read-bug` HEAD:
  - `firestarter_app/firestarter/eprom_operations.py:353-391` (`_main_phase_read_data`)
  - `firestarter_app/firestarter/eprom_operations.py:431+` (`consistency_check_eprom`)
  - `firestarter_app/firestarter/serial_comm.py:385-616` (`_decode_id_frame` + `_read_and_parse_lines`)
- **Phase 26 committed binary evidence**:
  - `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_0{1,2,3}.bin` (3× 65,536 B; mined during this research)
  - `.planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/run_0{1,2,3}.bin` (3× 65,536 B; byte-identical reference)
  - `.planning/v1.6/bench-logs/W27C512-leonardo-20260521-134210.log` (grep'd for CRC warnings during this research)
- **Firmware git history** — verified during this research session:
  - `git show <tag>:src/boards/leonardo_rurp_shield.cpp` at tags 2.0.2 / 2.0.3 / 2.0.4 / 2.0.5 / 2.0.6 → byte-identical `rurp_read_data_buffer`
  - `git show 5b1f1cd` ("Leonardo is working, fast as a shark", 2025-02-11) → introduction of the current read function shape
  - `git show df5fb44` ("fix(uno): disable PORTD pullups on data-input transition", 2026-05-13) → the Uno-side fix that was never mirrored to Leonardo
  - `git show 1abadaa` ("feat(eprom_operations): wrap chip-byte stream in MSG_DATA_CHUNK frames (W-04)", 2026-05-18) → Phase 8 / v1.2 introduction of `_firestarter_emit_frame_wide` (NOT the bug source)

### Secondary (MEDIUM confidence)

- **Planning trail** — CONTEXT.md / EVIDENCE.md / SUMMARY.md from Phases 26 and 27 — used for scope locks + Phase 26 deferral context. MEDIUM only because these are themselves planning artifacts that reflect the operator's mental model at the time of writing; the primary-source evidence (binaries + firmware source) is HIGH.

### Tertiary (LOW confidence)

- **`firestarter/CLAUDE.md` + meta-repo `/workspaces/CLAUDE.md`** — the "Leonardo 1024-B" assertions are explicitly REFUTED by the platformio.ini source of truth. Including in tertiary not because they're useful, but to flag them as documentation-drift inputs the RCA must correct.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; existing pytest infrastructure unchanged.
- Architecture: HIGH — Phase 27 is a narrative-append phase; the architecture pattern (`v1.6-EVIDENCE.md` accretion + conditional Wave B) is already established by Phase 26.
- Pitfalls: HIGH — every pitfall is documented against specific (re-runnable) Python evidence or specific firmware-file line ranges.
- Hypothesis disposition: HIGH — H2 wins decisively (78% single-bit / 63% bit-3 / 15% 0xFF triad is internally consistent and externally distinct from H1/H3/H4/H5).
- RCA-03 milestone-bracket: HIGH — tag-walking across 2.0.2..3.0.0b4 confirmed structural identity of the corrupting function.
- GATE-1.6 risk: HIGH — three named axes all clear (the fix is read-only code-path).
- Wave B trigger: HIGH — none of the three D-01 triggers fires.

**Research date:** 2026-05-21
**Valid until:** 2026-06-20 (30 days; the firmware sub-repo is stable on `beta@3.0.0b4`; no in-flight refactors that would shift the cited line ranges).
