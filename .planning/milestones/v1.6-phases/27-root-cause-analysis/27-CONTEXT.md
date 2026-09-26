# Phase 27: Root Cause Analysis — Context

**Gathered:** 2026-05-21
**Status:** Ready for research / planning
**Source:** /gsd:discuss-phase 27 (Auto Mode — gray areas auto-resolved with recommended options; no AskUserQuestion prompts per harness Auto Mode)

<domain>
## Phase Boundary

Phase 27 delivers **a written, evidence-backed root-cause explanation of the Leonardo 64KB-read byte-jitter** sufficient that Phase 28 can write a targeted fix + unit test without re-running the bisection. The empirical scope has been narrowed twice by Phase 26:

1. The bug is **Leonardo-only** (ATmega32U4 + native USB-CDC). Plain Uno (328P + external USB-to-UART bridge) is clean — 3 byte-identical 64KB reads at SHA-256 `8d2124eb7c994f717ace1b2b79c52fa95153aa82c6a4891a323ad924ef409759` (`.planning/v1.6-EVIDENCE.md:16`).
2. The Leonardo jitter rate is **2.1% byte-divergence at 64KB** (1349 / 65536 bytes between consecutive reads), NOT the ~57.8% from the pre-existing bug-report (which was captured on a misidentified board; not comparable). First divergence at offset `0x0003`. ~3.2% of byte positions are flicker-prone across 3 runs; ~96.8% of positions are stable (independently re-derived from `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_0[1-3].bin`).

**In scope:**
- An RCA narrative artifact pinpointing the corrupting code path on the Leonardo side with concrete evidence (RCA-01).
- A 2-5 paragraph WHY explanation of the corruption mechanism — sufficient for a future maintainer to recognize similar symptoms without re-bisecting (RCA-02).
- Introducing-commit triangulation: at minimum a milestone-bracket (v1.0 / v1.2 / v1.4 / v1.5) with rationale; full `git bisect` only if cheap (RCA-03).
- A GATE-1.6 risk assessment paragraph: whether the candidate fix is likely to perturb the write path, VPP regulator engagement, or chip-programming pulse intervals (ROADMAP SC#4).
- A fix sketch sufficient for Phase 28 to plan against — not the implementation itself.
- Hypothesis disposition: each of the four bug-report hypotheses + the post-Phase-26 additions either disproven or retained as the favored explanation, with evidence.

**Out of scope:**
- The fix implementation itself — Phase 28 owns it.
- Multi-board bench cycle / N≥5 consecutive-read verification — Phase 29 owns it.
- Documentation cleanup / milestone close — Phase 30 owns it.
- Plain Uno or uno328pb-silicon RCA — Plain Uno is clean (Phase 26 evidence); uno328pb-silicon row is DEFERRED until reflash.
- New chip support, new board target, new firmware features beyond RCA instrumentation.
- Consistency-check tool enhancements (REVIEW WR-01 FAIL-without-divergence edge case, WR-02 `Board: unknown-board` cosmetic) — Phase 28 polish or post-v1.6.
- `firestarter info <chip>` crash, `0xda01` W27C512 alias gap — explicitly out of v1.6 scope per Phase 26 follow-up annotations.

</domain>

<spec_lock>
## Locked Requirements (no SPEC.md — anchored in REQUIREMENTS.md + ROADMAP.md)

There is no Phase 27 SPEC.md; the locked requirement set comes from `.planning/REQUIREMENTS.md` §"Root Cause (RCA)" and `.planning/ROADMAP.md` §"Phase 27: Root Cause Analysis":

- **RCA-01** — Exact code path identified with concrete evidence (instrumented FW build OR code-path bisection OR minimal reproducer narrowing to a single function / chunk-boundary handler).
- **RCA-02** — 2-5 paragraph WHY narrative in the planning trail (timing window, missed ACK, buffer overflow, CRC8 false-positive, MAGIC_PREAMBLE collision, MSG_DATA_CHUNK length-field handling, host-side pyserial input-buffer overflow at 250000 baud, USB-CDC bulk-endpoint quirk, etc.).
- **RCA-03** — Introducing commit (or earliest version) identified via `git log -L` / `git bisect` where reasonably possible; at minimum milestone-bracketed (v1.0 / v1.2 / v1.4 / v1.5) with rationale.

ROADMAP Success Criteria layer on top:
- **SC#1** — The RCA artifact contains one of (a) instrumented-build log pinpointing the corruption boundary, (b) bisection narrowing to a single function, or (c) scope/logic-analyzer trace.
- **SC#2** — 2-5 paragraph WHY (RCA-02 verbatim, restated for emphasis).
- **SC#3** — Introducing-commit citation OR milestone-bracket with rationale (RCA-03 verbatim).
- **SC#4** — Explicit GATE-1.6 risk assessment: does the candidate fix risk perturbing write-path timing / VPP regulator / chip-programming pulse intervals?

</spec_lock>

<decisions>
## Implementation Decisions

### Investigation approach

- **D-01: Hybrid desk-side-first, bench-only-if-needed.**
  Phase 27 starts as a pure desk-side investigation: read code, instrument with thought-experiments, compare Leonardo vs Plain Uno emit paths, replay the Phase 26 evidence binaries (already committed under `.planning/v1.6/consistency-check-runs/`). Only escalate to an instrumented firmware build + bench run if desk-side reading does not yield a high-confidence answer. The escalation path is gated, not assumed.
  Rationale (closes the biggest gray area):
  - **Cheap before expensive.** An instrumented FW build requires: cutting `firestarter/v1.6-read-bug` branch, adding `-D RCA_INSTRUMENT_*` build flags, flashing the Leonardo, running a fresh bench session, capturing logs. That's 1-2 hours of operator-on-bench time. Desk-side code reading + replay of the committed binaries is 0 minutes of bench time and may resolve the question outright — the Leonardo bench evidence is already on disk.
  - **Strong starting signal already exists.** First-divergence offset `0x0003`, plus the run_1 anomaly (`00 01 02 83 04 05 2e 07 08 0b 0a 0f 1c 0d 0e 4f` — values that look like address-counter-low-byte bleed, NOT EPROM content) — are concrete hex evidence the researcher can analyze against the firmware emit code (`firestarter/src/eprom_operations.cpp:_process_outgoing_data` + `firestarter/src/boards/rurp_serial_utils.cpp:_firestarter_emit_frame_wide`) and host parse code (`firestarter_app/firestarter/serial_comm.py:_read_and_parse_lines` + `_decode_id_frame`).
  - **ROADMAP SC#1 explicitly enumerates three options (a/b/c) as ALTERNATIVES, not all-of-three.** Code-path narrowing is one of them; the artifact is satisfied by any single method that pins the corruption to a single function / chunk-boundary handler with evidence.
  - **GATE-1.6 risk reduction.** Cutting `firestarter/v1.6-read-bug` later means fewer commits on a branch that may not even ship; we avoid premature firmware-side churn that would have to be reverted.

  **Escalation triggers** (any one of these flips Phase 27 to "needs bench"):
  - Desk-side analysis cannot disambiguate between ≥2 named hypotheses with similar evidence weight after research.
  - Researcher identifies a candidate fix but the GATE-1.6 risk assessment is non-trivial AND only bench evidence can prove the candidate is correct without first writing the fix.
  - The committed Leonardo binaries' divergence pattern is internally inconsistent with every desk-side hypothesis the researcher generates (i.e., the existing evidence is insufficient).

  **Output the planner needs:** PLAN.md specifies a single Wave A (desk-side, autonomous) that produces a draft RCA. Wave B (operator-on-bench, autonomous: false) is **conditional** — included in the plan structure as a skeleton, executed only if Wave A's verifier reports `needs_bench: true`. Same shape as Phase 12's Wave 0 / Wave 1 split.

### Bench dependency profile

- **D-02: Desk-side default; bench escalation reserved.**
  Phase 27 is expected to close entirely desk-side based on the Phase 26 evidence already on disk + code-reading against the two sub-repos. The conditional bench escalation (D-01 Wave B) is the safety valve, not the plan. This mirrors Phase 26's actual outcome (Plan 26-01 desk-side + Plan 26-02 bench-only) where the bench wave was the operator-confirmation step, not the discovery step.
  Rationale:
  - Phase 26 already produced the empirical evidence Phase 27 needs to consume (committed binaries + bench logs + 9-column row in EVIDENCE.md).
  - The 3-shield A/B/C triage already proved the bug is **transport-layer, not RURP-shield-specific** (memory `[[user-shield-revisions]]` references the same finding). No new hardware A/B is needed to bracket the bug at the silicon-transport layer.
  - The operator does NOT need to be on bench during desk-side Wave A. This matches the v1.6 milestone bench-dependency profile (`.planning/STATE.md` "Bench-gated vs desk-side split" — Phase 27 listed as "largely desk-side with optional bench instrumentation").

### Firmware sub-repo branch flow

- **D-03: Cut `firestarter/v1.6-read-bug` from `beta` ONLY if Wave B fires.**
  Phase 26 D-13 explicitly deferred the firmware sub-repo `v1.6-read-bug` branch to Phase 28 because Phase 26 was host-CLI-only. Phase 27 inherits the same posture: no firmware-sub-repo edits in Wave A. If Wave B fires (instrumented build), the planner cuts `firestarter/v1.6-read-bug` off `beta@3.0.0b4` (the same tip Phase 26 referenced) at the start of Wave B, lands the instrumentation flags as a single commit, and the branch then carries through to Phase 28 for the fix. If Wave B does not fire, the firmware branch is still deferred to Phase 28.
  Rationale: keeps the firmware sub-repo's `beta` branch clean of in-flight instrumentation; instrumentation lives on a branch that may merge to fix, not a branch that may also bypass the fix.
  Memory consistency: matches `[[feedback_branching]]` — milestone work on `v1.6-read-bug` in all 3 repos, not committed directly to `beta`/`main`.

### RCA artifact placement

- **D-04: Append a `## Phase 27 — RCA Findings` section to `.planning/v1.6-EVIDENCE.md` (NOT a standalone `v1.6-RCA.md`).**
  - ROADMAP SC#1 explicitly lists this option: "A written RCA artifact (`.planning/v1.6-RCA.md` or section in `.planning/v1.6-EVIDENCE.md` — fixed at execution time)".
  - The Phase 26 EVIDENCE.md already includes a forward-annotation HTML comment exactly where the Phase 27 section appends (line 20: `<!-- Phase 27 RCA appends a section here: ## Phase 27 — RCA Findings. -->`).
  - The cross-phase evidence-accretion artifact stays a single file across all 4 v1.6 phases (26 baseline → 27 RCA → 28 fix commits → 29 post-fix inversion). One file is easier for Phase 30's milestone close to archive than two.
  - Schema clarification: the Phase 26 9-column row schema applies to **evidence rows**, not narrative prose. The Phase 27 section is free-form prose (RCA narrative + hypothesis disposition + introducing-commit citation + GATE-1.6 risk paragraph + fix sketch). If Phase 27 ALSO appends new evidence rows (e.g., instrumented-build log row), those rows use the 9-column schema. (Resolves the apparent contradiction in the line-20 HTML comment.)

### Buffer-size A/B test scope

- **D-05: NO explicit DATA_BUFFER_SIZE A/B test in Phase 27.**
  Critical Phase-26 documentation drift caught during this discuss: the Leonardo firmware that ran Phase 26 was compiled with `-D DATA_BUFFER_SIZE=512` (per `firestarter/platformio.ini:64-65`, "TEMP: 512 to match Uno for buffer-size A/B test (was 1024)"), NOT 1024 as the bug-report and several planning docs imply. **Both the Plain Uno and the Leonardo ran at 512 in the Phase 26 baseline**, so buffer-size delta is NOT the differentiator between PASS and FAIL.
  Rationale:
  - The A/B test was already implicitly run (current 512 = jitter present at 2.1%; historical 1024 would need a fresh build to compare). Going back to 1024 is a separate experiment that doesn't belong in RCA — it's a fix-shape probe (Phase 28 territory).
  - RCA scope is "find the cause", not "find a workaround". A buffer-size revert from 512 to 1024 is a workaround if it masks the bug; the RCA must explain WHY the symptom would change at all.
  - Phase 27 narrative MUST explicitly cite the 512-vs-1024 documentation drift and correct the historical bug-report's hypothesis #4 ("Leonardo's 1024-byte buffer") so future readers don't chase the wrong premise.

  **Captured for hypothesis disposition:** the bug-report's hypothesis #4 ("Leonardo's 1024-byte DATA_BUFFER vs Uno's 512-byte") is partially refuted by Phase 27's docs check — at 512 on both boards, the Leonardo still jitters and the Uno still doesn't. The hypothesis collapses to "32U4 silicon / transport difference, not buffer size".

### Introducing-commit triangulation strategy

- **D-06: Milestone-bracket first (cheap), commit-precise only if cheap.**
  Researcher establishes the bug's earliest observable version by reading the firmware history of the four files that own the Leonardo emit path: `firestarter/src/eprom_operations.cpp`, `firestarter/src/boards/rurp_serial_utils.cpp` (especially `_firestarter_emit_frame_wide`), `firestarter/src/boards/leonardo_rurp_shield.cpp`, `firestarter/include/firestarter.h` (DATA_BUFFER_SIZE default). The Phase 6 / v1.2 message-ID rework (PROJECT.md §"v1.2") is a strong candidate boundary — it introduced `_firestarter_emit_frame_wide` (MSG_DATA_CHUNK W-04 path). If the bug exists pre-v1.2, the read path before that wasn't framed by MSG_DATA_CHUNK and the bisection target shifts.
  Rationale:
  - ROADMAP SC#3 explicitly allows milestone-bracket as the floor: "at minimum bracketed to a milestone (v1.0 vs v1.2 vs v1.4) with rationale".
  - `git bisect` requires the operator to flash older firmware versions to bench-confirm each test point — that's bench-gated, expensive, and overlaps with D-01's escalation criteria. Only worth doing if Wave B fires AND the bisection is the cheapest way to disambiguate.
  - Memory `[[project_uno328pb_correction]]` already notes the v1.5 baseline magnitude (~57.8%) is unreliable as a historical anchor — the bug was always there at SOME magnitude on Leonardo, but the magnitude attributed to the misidentified board can't be trusted.

  **Output the planner needs:** PLAN.md task list includes a desk-side "Trace ownership of the emit/parse functions through firmware git history; bracket to milestone" task. Full `git bisect` is a Wave-B-only optional task.

### Plan structure

- **D-07: Two-wave plan structure with conditional Wave B.**
  - **Wave A — Plan 27-01 (desk-side, autonomous: true):** RCA-via-code-reading + hypothesis disposition + introducing-commit milestone-bracket + GATE-1.6 risk paragraph + fix sketch. Reads from the Phase 26 binaries + sub-repo source. Produces the Phase 27 section in `.planning/v1.6-EVIDENCE.md`. Closes RCA-01/02/03 if the verifier accepts the desk-side narrative.
  - **Wave B — Plan 27-02 (operator-on-bench, autonomous: false, CONDITIONAL):** Cut `firestarter/v1.6-read-bug` off `beta@3.0.0b4`. Add `-D RCA_INSTRUMENT_*` build flags. Flash Leonardo. Run instrumented version of `firestarter dev consistency-check` against the same chip. Capture log. Append additional findings to `## Phase 27 — RCA Findings`. Closes any RCA-01/02/03 gaps Wave A could not close. Only authored if Wave A verifier reports `needs_bench: true`.
  - Plan 27-02 is **drafted but not executed** by default. The planner produces both plans in a single planning pass; the executor decides at Wave A verification time whether to enter Wave B.
  - This mirrors Phase 12's Wave 0 desk-side scaffold + later-wave bench plan structure and Phase 26's 26-01 desk-side / 26-02 bench split.

### Hypothesis prioritization

- **D-08: Pre-ranked hypothesis list locked at start of Wave A.**
  The Phase 26 narrowing already eliminates several hypotheses from the original bug-report. Wave A enters with this ranked list (most-likely first), and the RCA narrative either confirms one or disposes of all and ranks newly-generated hypotheses:

  | Rank | Hypothesis | Status going in | Reasoning |
  |------|------------|-----------------|-----------|
  | 1 | **ATmega32U4 USB-CDC bulk-endpoint quirk** — `SERIAL_PORT.write(byte)` byte-at-a-time + `.flush()` interacts badly with the 32U4's dual-bank 64-byte endpoint FIFO. The 4-byte MAGIC_PREAMBLE + 2-byte length + 1-byte ID = 7 prelude bytes BEFORE the 512-byte payload would land near a 64-byte bank boundary at offset 0x3F mid-frame. | favored | Leonardo-specific. First-divergence at `0x0003` is suspiciously aligned with the first endpoint-boundary region of the payload (offset 0x0003 inside payload = 0x000A inside the byte-by-byte write stream after the 7-byte prelude = early in first USB packet). No equivalent code path on the Uno (hardware UART, no endpoint banks). |
  | 2 | **Leonardo data-bus read path returning address-bit-bleed rather than chip data** — `leonardo_rurp_shield.cpp:rurp_read_data_buffer` scatters across PORTD/PORTC/PORTE; if `rurp_set_data_input` doesn't fully disconnect data lines OR if pin-reassembly timing races against address-counter increments, what arrives in `handle->data_buffer` may be partial address-counter bleed instead of chip data. | favored (second) | Leonardo run_1 first 16 bytes are `00 01 02 83 04 05 2e 07 08 0b 0a 0f 1c 0d 0e 4f` — values that look like address-counter low-byte values with occasional anomaly bytes (`83` at offset 3, `2e` at offset 6, `4f` at offset 15) — NOT EPROM content. Plain Uno's first 16 bytes (`37 d4 71 0e ab 48 e5 82 1f bc 59 f6 93 30 cd 6a`) look like genuine EPROM content. **If hypothesis #2 holds, the bug is on the chip-read path (parallel-bus read), NOT the serial-transport path.** This significantly changes the fix shape. |
  | 3 | **Firmware MAIN-state `op_wait_for_ack` race on 32U4** — host's ACK may arrive before the firmware's USB-CDC TX buffer has fully flushed to the host's pyserial RX buffer; if `flush()` returns before the actual USB transaction completes (a documented Arduino USB-CDC issue at certain CDC_RX_BUFFER_SIZE settings), the next chunk's prelude may collide with stale TX data on the wire. | retained | Mid-protocol race; would explain mid-stream sporadic byte errors but doesn't easily explain first-byte (offset 0x0003) corruption unless there's a startup race specifically. |
  | 4 | **MSG_DATA_CHUNK CRC8 false-positive** — bug-report hypothesis 1; if CRC8 mismatch is silently ignored on a corrupted-but-CRC-matching frame, the host accepts garbage. | unlikely | CRC8 is computed on `[id, params]` (8-bit accumulator, poly 0x07). For 512 random bytes, false-positive rate is ~1/256 = 0.4% per frame. At 128 chunks per 64KB read, expected false-positives = 0.5 per read, which fits ~~the 2.1%/128 = ~0.016% per chunk number~~ — actually doesn't fit; the false-positive rate is too high. RETAIN as fallback but expect to dispose. |
  | 5 | **MAGIC_PREAMBLE collision** — bug-report carry-forward. | very unlikely | The host parser is length-authoritative after preamble match; even a payload-byte sequence matching `AA 55 AA 55` doesn't cause re-sync mid-frame. |
  | 6 | **Bug-report hypothesis #4 (Leonardo's 1024-byte DATA_BUFFER)** | refuted by Phase 27 docs check | Per D-05: Leonardo is currently compiled at DATA_BUFFER_SIZE=512, same as Uno. Buffer-size delta is NOT the discriminator. |
  | 7 | **328PB-specific timing (bug-report hypothesis #3)** | out of scope | The board in Phase 26 was a Plain Uno + wrong FW per operator clarification; no true 328PB silicon in the evidence set. Defer to Phase 29 if reflash happens. |

  Wave A's deliverable includes a "Hypothesis Disposition" sub-section that either confirms one of #1–#5 or generates a new #8+ and disposes of the prior list. The ranked-up-front approach lets the researcher target which evidence to mine from the binaries rather than narrating speculatively.

### GATE-1.6 risk assessment

- **D-09: Explicit GATE-1.6 risk paragraph in the RCA narrative — three named risk axes.**
  ROADMAP SC#4 names the three risk axes verbatim: **write-path timing, VPP regulator engagement, chip-programming pulse intervals**. The Phase 27 RCA narrative must contain a paragraph that addresses each:
  - **Write-path timing:** Does the candidate fix touch any code path also used by `_process_incoming_data` / `eprom_write` / `op_wait_for_ack`? If yes, name the function and explain the divergence guard.
  - **VPP regulator engagement:** Does the candidate fix touch code in `rurp_shield.h` (REGULATOR / VPE_TO_VPP / P1_VPP_ENABLE bits) or `rurp_set_control_pin`? Unlikely if the fix is in `rurp_serial_utils.cpp`, but the paragraph must say so explicitly.
  - **Chip-programming pulse intervals:** Does the candidate fix introduce blocking delays (`delay()` / `delayMicroseconds()`) into the write path? If the fix involves a tighter `flush()` or per-byte spin, it does NOT touch the write path's pulse loop, but the paragraph must state this affirmatively.

  If any axis carries non-trivial risk, the paragraph flags it as a **mandatory Phase 28 mitigation item** (RCA hands off a constraint, not a fait accompli). If all three are clear, the paragraph says so explicitly so Phase 28's planner has the green light.

### Diagnostic-tool enhancement scope

- **D-10: NO enhancements to `firestarter dev consistency-check` in Phase 27.**
  Phase 26 REVIEW.md flagged WR-01 (FAIL-without-divergence edge case in the run_01 vs run_02 hardcode) and WR-02 (hardcoded `unknown-board` in verdict block). Phase 27 explicitly does NOT fix either:
  - WR-01: out-of-scope for RCA; Phase 28 polish or deferred.
  - WR-02: out-of-scope for RCA; Phase 28 polish or deferred.
  Rationale: Phase 27's mandate is to find the cause, not improve the tooling. The Phase 29 stdout-regex contract doesn't depend on either WARNING, so neither blocks the milestone.

### Documentation drift correction

- **D-11: The RCA narrative MUST explicitly call out and correct the "Leonardo 1024-B buffer" documentation drift.**
  Locations where the drift exists (planner / researcher must audit and correct each, OR cite the correction inline in the RCA narrative if direct edits are out of scope):
  - `.planning/ROADMAP.md` — no explicit "1024" in the v1.6 phase narrative (clean).
  - `.planning/phases/26-*/26-02-SUMMARY.md:147` — says "Leonardo's 1024-byte DATA_BUFFER_SIZE vs Uno's 512-byte (the chunked-transfer code in ... eprom_operations.py may have a buffer-boundary edge case)" — incorrect; both are 512.
  - `.planning/todos/pending/large-read-data-jitter-uno328pb.md:57` — bug-report hypothesis #4 — incorrect.
  - `firestarter/CLAUDE.md` (sub-repo, NOT meta-repo) — Board differences note says Uno 512, Leonardo 1024 — incorrect.
  - `firestarter_app/CLAUDE.md` — does not state buffer sizes directly (clean).
  - `CLAUDE.md` (meta-repo) — says "Uno has a 512-byte data buffer; Leonardo has 1024 bytes" — incorrect.
  - `firestarter/platformio.ini:64-65` — DOES carry the "TEMP: 512 ... (was 1024)" comment; this is the source of truth.
  Rationale: ROADMAP SC#2's "future maintainer encountering similar symptoms can reach for the same fix pattern without re-bisecting" is undermined if planning docs continue to anchor on the wrong buffer size. The RCA narrative is the most-readable place to crystallize the correction; downstream phases (28 polish, 30 docs-update) execute the cleanup.

### Branch flow

- **D-12: Meta-repo `main`; firestarter_app `v1.6-read-bug` carries through; firestarter on `beta` unless Wave B fires.**
  - Meta-repo (`.planning/`): branch `main` per existing convention. Phase 27 artifacts (this CONTEXT.md, RESEARCH.md, PLAN.md, PLAN-02.md if drafted, RCA section in EVIDENCE.md) commit to `main` as they're created. Same as Phase 26.
  - `firestarter_app/`: branch `v1.6-read-bug` already exists from Phase 26 (cut from `beta@3.0.0b4`). Phase 27 does NOT modify firestarter_app code in Wave A. If Wave B fires AND requires host-side instrumentation (e.g., a `dev consistency-check --rca-trace` flag), edits land on the existing `v1.6-read-bug` branch.
  - `firestarter/`: branch `v1.6-read-bug` NOT cut yet. Only cut if Wave B fires. Cut off `beta@3.0.0b4` then (same base as Phase 26's host-side cut would have used).
  - Memory `[[feedback_branching]]` invariant honored: no commits go to `beta`/`main` of either sub-repo within Phase 27 itself.

### Claude's Discretion

- **Exact instrumentation strategy** if Wave B fires — toggle which prelude bytes get logged (`-D RCA_LOG_PREAMBLE`, `-D RCA_LOG_LEN`, `-D RCA_LOG_FIRST_N_BYTES=N`), or a single coarse-grained `-D RCA_TRACE_CHUNK_BOUNDARIES`. Planner chooses based on Wave A's hypothesis ranking outcome.
- **Whether the RCA section also includes a hex-dump appendix** showing the run_1/run_2/run_3 first 256 bytes side-by-side. Researcher's call — useful if hypothesis #2 (address-bit-bleed) wins; redundant if hypothesis #1 (USB-CDC) wins. Defer to the planner.
- **Wave B firmware-branch base** — `beta@3.0.0b4` is the recommended base, but if Phase 26 closure has advanced `beta` (it hasn't as of 2026-05-21; the Phase 26 bench session used `3.0.0b4` directly), the planner may pick the current `beta` HEAD instead.
- **Hypothesis disposition rendering format** — table vs prose. Table is more grep-friendly; prose is more readable for the 2-5 paragraph SC#2 deliverable. Researcher's call; the locked deliverable is hypothesis disposition existing in some form.
- **Whether the consistency-check tool's stdout includes the run_01 hex header.** Phase 26 REVIEW.md WR-01 fix would touch this; Phase 27 does NOT add it (D-10), but the researcher may add a thought-experiment note ("if WR-01 were fixed, the FAIL block would show run_2 vs run_3 divergence detail, surfacing additional offsets the current output misses") into the RCA section as future-tooling guidance.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before researching or planning.**

### Phase scope + requirements (authoritative)
- [.planning/ROADMAP.md](.planning/ROADMAP.md) §"Phase 27: Root Cause Analysis" — goal + Success Criteria 1–4 + Plans = TBD
- [.planning/ROADMAP.md](.planning/ROADMAP.md) §"Structural Notes" — bench-gated-vs-desk-side split + cross-cutting evidence accretion pattern + GATE-1.6 non-regression
- [.planning/REQUIREMENTS.md](.planning/REQUIREMENTS.md) §"Root Cause (RCA)" — RCA-01 / RCA-02 / RCA-03 verbatim + traceability table at file end
- [.planning/PROJECT.md](.planning/PROJECT.md) §"Current Milestone: v1.6 Fix the Read Bug" — milestone goal, locked decisions, Definition of Done, GATE-1.6 non-regression
- [.planning/STATE.md](.planning/STATE.md) — current position; updated after this phase commits

### Phase 26 evidence (the empirical foundation Phase 27 reasons from)
- [.planning/v1.6-EVIDENCE.md](.planning/v1.6-EVIDENCE.md) — Pre-fix consistency-check baseline rows (uno PASS, leonardo FAIL, uno328pb DEFERRED) + Verdict section + Scope changes captured during the bench session + Hardware metadata snapshot + Phase 27 entry conditions. The Phase 27 RCA section appends here per D-04.
- [.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-CONTEXT.md](.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-CONTEXT.md) — D-01..D-13 decisions; especially D-03 (reuse-not-duplicate read state machine) which Phase 27 trusts: the consistency-check tool exercises the bug-path code verbatim.
- [.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-VERIFICATION.md](.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-VERIFICATION.md) — 8/8 must-haves verified; the override entry documents WHY the uno328pb leg is DEFERRED.
- [.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md](.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md) §"Next Phase Readiness" — Phase 27 scope inputs the bench operator stated explicitly; lines 140-153.
- [.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/](.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/) — 3× 65,536-byte run binaries (Leonardo FAIL evidence). Phase 27 reads these to extract divergence patterns.
- [.planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/](.planning/v1.6/consistency-check-runs/W27C512-uno-20260521-133418/) — 3× 65,536-byte run binaries (Plain Uno PASS reference). Same chip family (W27C512 0xda08 vs Leonardo's 0xda01); side-by-side comparison reveals whether Leonardo's binary content even looks like genuine EPROM data.
- [.planning/v1.6/bench-logs/W27C512-leonardo-20260521-134210.log](.planning/v1.6/bench-logs/W27C512-leonardo-20260521-134210.log) — full tee'd Leonardo stdout from the FAIL run.
- [.planning/v1.6/bench-logs/W27C512-uno-20260521-133418.log](.planning/v1.6/bench-logs/W27C512-uno-20260521-133418.log) — Plain Uno PASS log.

### Bug evidence + hypothesis source
- [.planning/todos/pending/large-read-data-jitter-uno328pb.md](.planning/todos/pending/large-read-data-jitter-uno328pb.md) — original bug-report; 4 hypotheses in §"Hypotheses". Phase 27 disposes of each. **NOTE per D-11:** hypothesis #4 buffer-size narrative is incorrect documentation drift; Leonardo currently runs at DATA_BUFFER_SIZE=512.

### Firmware sub-repo — the code paths Phase 27 reads
- [firestarter/src/eprom_operations.cpp](firestarter/src/eprom_operations.cpp) — `_process_outgoing_data` (lines 110-132): the MAIN-state per-chunk send loop. Calls `rurp_log_id_wide(MSG_DATA_CHUNK, data_buffer, data_size)` and `op_wait_for_ack` per chunk.
- [firestarter/src/boards/rurp_serial_utils.cpp](firestarter/src/boards/rurp_serial_utils.cpp) §`_firestarter_emit_frame_wide` (lines 190-227) — wide-frame emitter; writes 4-byte preamble + 2-byte length + 1-byte ID + N payload bytes (one at a time, no batch SERIAL_PORT.write of the buffer) + 1-byte CRC + 0x0A anchor, then `.flush()`. **This is the prime hypothesis-#1 suspect.**
- [firestarter/src/boards/leonardo_rurp_shield.cpp](firestarter/src/boards/leonardo_rurp_shield.cpp) §`rurp_read_data_buffer` (lines 112-129) — Leonardo's parallel-bus read; scatters across PORTD/PORTC/PORTE. **This is the prime hypothesis-#2 suspect.**
- [firestarter/src/boards/leonardo_rurp_shield.cpp](firestarter/src/boards/leonardo_rurp_shield.cpp) §`rurp_set_data_input` (lines 137-141) — clears DDR bits to switch data lines to input; does NOT clear PORTx pull-ups (compare to `uno_rurp_shield.cpp:120-129` which explicitly clears PORTD=0x00 before clearing DDRD).
- [firestarter/src/boards/uno_rurp_shield.cpp](firestarter/src/boards/uno_rurp_shield.cpp) §`rurp_set_data_input` (lines 128-137) — Uno reference; comment block names the FM1608 byte-0 read failure as a known-related issue. Phase 27 evidence may reopen the FM1608 carry-forward as a related symptom.
- [firestarter/src/firestarter.cpp](firestarter/src/firestarter.cpp) — top-level loop + dispatch (lines 157-233); `eprom_read` case at line 181.
- [firestarter/include/firestarter.h](firestarter/include/firestarter.h) §`DATA_BUFFER_SIZE` (lines 18-19) — defaults to 512; `firestarter/platformio.ini:64-65` overrides for Leonardo (back to 512 from former 1024 — see D-05).
- [firestarter/platformio.ini](firestarter/platformio.ini) §`[env:leonardo]` (lines 57-65) — the canonical Leonardo build config; the "TEMP: 512" comment is the source-of-truth that exposes the documentation drift.
- [firestarter/CLAUDE.md](firestarter/CLAUDE.md) §"Architecture" — firmware-side dispatch chain. **NOTE per D-11:** "Board differences" note says "Leonardo 1024-B" — incorrect; must be reconciled with `platformio.ini`.

### Host sub-repo — the code paths Phase 27 reads
- [firestarter_app/firestarter/eprom_operations.py](firestarter_app/firestarter/eprom_operations.py) §`_main_phase_read_data` (line 353) — host-side MAIN-state read handler; parses `MSG_DATA_CHUNK` responses + extracts `response.payload`.
- [firestarter_app/firestarter/eprom_operations.py](firestarter_app/firestarter/eprom_operations.py) §`read_eprom` (line 391+) — full-chip read public API; the diagnostic loops this N times (Phase 26 D-03).
- [firestarter_app/firestarter/eprom_operations.py](firestarter_app/firestarter/eprom_operations.py) §`consistency_check_eprom` (line 431+) — the diagnostic that captured Phase 26 evidence; reuses the read state machine verbatim.
- [firestarter_app/firestarter/serial_comm.py](firestarter_app/firestarter/serial_comm.py) §`_read_and_parse_lines` (lines 491-616) — always-on byte-stream reader. Magic-preamble dispatch logic at lines 538-602. Reads 1 byte at a time via `self.connection.read(1)`. **Phase 27 reasons about whether this loop can lose bytes under high USB-CDC throughput.**
- [firestarter_app/firestarter/serial_comm.py](firestarter_app/firestarter/serial_comm.py) §`_decode_id_frame` (lines 385-489) — CRC8 verification; MSG_DATA_CHUNK payload extraction (lines 482-486). The hypothesis-#4 CRC8 false-positive analysis lands here.
- [firestarter_app/firestarter/serial_comm.py](firestarter_app/firestarter/serial_comm.py) §`MAGIC_PREAMBLE` (line 50) — `b'\xAA\x55\xAA\x55'` — matches firmware.
- [firestarter_app/CLAUDE.md](firestarter_app/CLAUDE.md) §"Wire Protocol" — JSON command shape + response prefix-tag convention.

### v1.4/v1.5 introducing-commit-search reference
- [.planning/MILESTONES.md](.planning/MILESTONES.md) — milestone histories; v1.2 (message-ID rework, introduced `_firestarter_emit_frame_wide` per Phase 6/7/8) is the strongest candidate boundary for RCA-03 milestone-bracket.
- `firestarter/` sub-repo git history — Phase 6/7/8/9 commits (visible via `git log --oneline -- src/boards/rurp_serial_utils.cpp src/eprom_operations.cpp`). The `_firestarter_emit_frame_wide` function originated in Phase 8 Plan 08-01 (W-04 MSG_DATA_CHUNK widening).

### Project memory (always-on guidance)
- `[[user_firestarter_repo_layout]]` — meta-repo + 2 sub-repos; `.planning/` tracked here only.
- `[[feedback_branching]]` — `v1.6-read-bug` branches in all 3 repos; sub-repos fork off `beta`, meta-repo off `main`. **Phase 27 D-03 + D-12:** firestarter sub-repo branch only cut if Wave B fires.
- `[[project_bench_findings_v15]]` — 328PB-Uno on `/dev/ttyUSB0`, urclock bootloader; W27C512 + SST27SF512 are the bench chips already validated.
- `[[user_shield_revisions]]` — operator owns Rev 2.2, Rev 2.0, modified Rev 0; EEPROM hw_revision byte can't distinguish 2.0 vs 2.2 — ASK when "swap the shield" comes up. **Phase 26 found the bug is shield-invariant** per the 3-shield triage; Phase 27 inherits that finding and does not propose shield rotation.
- `[[project_uno328pb_correction]]` — third board is actually a Plain Uno with wrong FW; Phase 26 baseline misidentification correction; Phase 27 explicitly excludes uno328pb-silicon investigation.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **The Phase 26 consistency-check binaries themselves** (`.planning/v1.6/consistency-check-runs/W27C512-{uno,leonardo}-*/run_*.bin`) — Phase 27's primary evidence base. Each binary is 65,536 bytes (full W27C512). Python one-liners surface divergence patterns without re-running on bench. **Independently verified during this discuss:** Leonardo run_1 first 16 bytes (`00 01 02 83 04 05 2e 07 08 0b 0a 0f 1c 0d 0e 4f`) look like address-bit-bleed; Plain Uno run_1 first 16 bytes (`37 d4 71 0e ab 48 e5 82 1f bc 59 f6 93 30 cd 6a`) look like genuine EPROM content. Strong starting signal for hypothesis #2.
- **`_firestarter_emit_frame_wide`** ([firestarter/src/boards/rurp_serial_utils.cpp:187-224](firestarter/src/boards/rurp_serial_utils.cpp#L187-L224)) — the wide-frame emitter shared by both boards. Writes byte-at-a-time via `SERIAL_PORT.write(b)` then `.flush()` at end. **The shared-vs-board-specific layering is the diagnostic seam Phase 27 reasons across:** Plain Uno → external USB-to-UART bridge (different transport silicon); Leonardo → 32U4 native USB-CDC. Same emitter code, different downstream transport. If the bug is in the emitter, it should manifest on both boards — and it doesn't. So the bug is in the transport silicon's interaction with the emitter's write pattern (hypothesis #1) or in the chip-read path BEFORE the emitter even runs (hypothesis #2).
- **Per-board `rurp_read_data_buffer`** ([firestarter/src/boards/leonardo_rurp_shield.cpp:112-129](firestarter/src/boards/leonardo_rurp_shield.cpp#L112-L129) vs [firestarter/src/boards/uno_rurp_shield.cpp:112-114](firestarter/src/boards/uno_rurp_shield.cpp#L112-L114)) — vastly different complexity. Uno reads `PIND` directly (8 bits already mapped 1:1 to data bus). Leonardo reassembles 8 bits from PORTD/PORTC/PORTE via 8 separate bit-shift expressions. **If hypothesis #2 holds, the bug is in the Leonardo's reassembly.**
- **Per-board `rurp_set_data_input`** ([firestarter/src/boards/leonardo_rurp_shield.cpp:137-141](firestarter/src/boards/leonardo_rurp_shield.cpp#L137-L141) vs [firestarter/src/boards/uno_rurp_shield.cpp:120-129](firestarter/src/boards/uno_rurp_shield.cpp#L120-L129)) — Uno explicitly clears `PORTD = 0x00` BEFORE clearing DDR (comment cites FM1608 byte-0 read failure as related); Leonardo does NOT clear PORTx before clearing DDR. **Possible Leonardo-specific data-input weak-pullup leakage**: residual PORTx bits from the previous `rurp_write_data_buffer` call may keep data lines weakly biased HIGH against the chip's drive, especially on bits that are HIGH in the address counter. This fits the hypothesis-#2 evidence: address-counter LSBs bleeding into data reads.
- **`com_mode` gate** ([firestarter/src/boards/uno_rurp_shield.cpp:19,82-97](firestarter/src/boards/uno_rurp_shield.cpp#L19)) — Uno's strong override of `rurp_log_id` + `rurp_log_id_wide` gates emit behind `com_mode`. Leonardo uses the weak default (no gate) per `rurp_serial_utils.cpp:231,277` because the 32U4 data bus doesn't share pins with the UART. **Defensible asymmetry — not a bug source** — but Phase 27 should explicitly note the asymmetry exists so the researcher doesn't waste cycles bisecting it.

### Established Patterns

- **State-machine prefix tags (`OK:`, `INIT:`, `MAIN:`, `END:`, `ERROR:`)** are message-IDs since v1.2 (Phase 6/7/8). The pre-v1.2 text-format firmware emitted these as ASCII prefixes; post-v1.2 emits via the ID-framed wire protocol (4-byte preamble + length + body + CRC + anchor). RCA-03 milestone-bracket pivots on this boundary: pre-v1.2 the read path didn't use `_firestarter_emit_frame_wide` (hadn't been written yet); post-v1.2 it does. If the bug is in `_firestarter_emit_frame_wide`, RCA-03 brackets to v1.2 or later. If the bug is in `rurp_read_data_buffer`, RCA-03 brackets to pre-v1.2 (the Leonardo read path is structurally similar across all firmware versions).
- **3-phase state machine INIT → MAIN → END** is the host-firmware protocol surface; both sub-repos parse it identically. Phase 27 reasons about MAIN-state per-chunk send pattern (firmware emits `MSG_DATA_SENDING` then `MSG_DATA_CHUNK` per chunk; host expects this exact ordering).
- **Cross-phase evidence accretion** (`.planning/v1.{3,5,6}-{BENCH-RESULTS,EVIDENCE}.md`) — Phase 27 appends to `.planning/v1.6-EVIDENCE.md` per D-04; this mirrors v1.3's BENCH-RESULTS append pattern across phases 12/13/14.
- **Wave A desk-side autonomous + Wave B operator-on-bench non-autonomous** — Phase 12 Wave 0 + Wave 1, Phase 26 Plan 26-01 + 26-02. Phase 27 inherits the same split via D-07.

### Integration Points

- **Phase 26 consistency-check tool ↔ Phase 27 RCA.** The tool is Phase 27's primary instrumentation: its committed binaries are the evidence base, and any Wave B re-run uses the same tool to compare instrumented-FW vs production-FW. The tool's D-03 reuse-not-duplicate property is load-bearing for Phase 27: if Wave B's instrumented build still produces different SHAs from the production build, the differential isolates which instrumentation flag matters.
- **`.planning/v1.6-EVIDENCE.md` schema ↔ Phase 27 narrative.** Phase 27 appends a `## Phase 27 — RCA Findings` section. Per D-04, this is free-form prose; the 9-column row schema only applies if NEW evidence rows are added (e.g., from an instrumented build).
- **Phase 28's fix planning ↔ Phase 27's hypothesis disposition + GATE-1.6 risk.** Phase 27's RCA narrative is Phase 28's authoritative input. If the narrative names the bug location and the fix sketch is concrete, Phase 28's planner has the foundation. If Phase 27 ends with multiple un-disposed hypotheses, Phase 28's planner inherits ambiguity — undesirable.
- **NO new test files in Phase 27.** Unity / pytest test creation is Phase 28's FIX-02 deliverable. Phase 27 does not pre-build a test; the test would be speculative without a confirmed bug location.

</code_context>

<specifics>
## Specific Ideas

- **"The Leonardo binaries are not the chip data — they're predominantly address-counter bleed."** First 16 bytes look like `00 01 02 ?? 04 05 2e 07 08 0b 0a 0f 1c 0d 0e 4f` across runs — that's address-LSB-bleed with sporadic anomaly bytes. If true, the fix is in the chip-read path (`leonardo_rurp_shield.cpp:rurp_read_data_buffer` or `rurp_set_data_input`), NOT the serial-transport path. This rewrites Phase 27's prior of "USB-CDC quirk" and points the planner at the data-bus reassembly code. Researcher MUST verify against the bench evidence before accepting hypothesis #2.
- **"Plain Uno's binary content is the reference truth."** The Uno W27C512 binary (`37 d4 71 0e ab 48 e5 82 1f bc 59 f6 93 30 cd 6a ...`) has no recognizable pattern — that's expected for a programmed EPROM. The Leonardo binary's recognizable counter pattern is the smoking gun. Cross-chip caveat: Leonardo had a different physical W27C512 (chip ID 0xda01) than the Uno (0xda08); the two chips MAY have different programmed content, so byte-for-byte equality is not expected. But Leonardo's content looking like address-counter values rather than EPROM-shaped random data is content-independent evidence.
- **"DATA_BUFFER_SIZE was already swapped from 1024 to 512 as a 'TEMP' A/B test (commit ca6a9e5).** That swap has been in `firestarter/platformio.ini` for many phases — it's not Phase-26-introduced. So the Leonardo's 2.1% jitter is the 512-buffer rate; the historical 1024-buffer rate may have differed. Phase 27 must capture this so the RCA narrative doesn't reason about a 1024-byte phantom that hasn't shipped in months.
- **"The first divergence at offset 0x0003 + the run_1 anomaly bytes at offsets 3, 6, 15 = candidate cross-check."** If hypothesis #2 (address-bit-bleed) wins, the anomaly bytes are positions where the chip momentarily drove the bus strongly enough to override the pull-up leakage. If hypothesis #1 (USB-CDC quirk) wins, the anomaly bytes should align with USB-packet boundaries (offset 0x0003 inside the payload = byte 10 of the byte-by-byte write stream after the 7-byte prelude). Researcher cross-checks both predictions against the committed binaries.
- **"Phase 27 is the natural place to write the FM1608 link if it materializes."** v1.1 Phase 4's FM1608 byte-0 read bug (parked since 2026-05-18) has the same symptom shape (LSB data line returning wrong values; cleared `rurp_set_data_input` was one of 8 attempted fixes that DIDN'T work). If Phase 27 RCA implicates the data-input path on Leonardo, the FM1608 bug may be in the same family. Researcher captures this as a forward-reference if applicable; does NOT pre-commit to unparking FM1608 (it's Uno-specific, this is Leonardo-specific — likely distinct root causes).

</specifics>

<deferred>
## Deferred Ideas

- **Bench A/B test of `-D DATA_BUFFER_SIZE=1024` revert on Leonardo.** Out of Phase 27 scope (D-05). Could be Phase 28's first fix-shape experiment IF hypothesis #2 wins; deferred until then.
- **Full `git bisect` across firmware history to commit-precise the introducing commit.** D-06 floors RCA-03 at milestone-bracket; full bisection is Wave-B optional only. Could be reopened post-v1.6 as a "historical curiosity" doc-update item.
- **Consistency-check tool enhancements (Phase 26 REVIEW WR-01 / WR-02).** Defer to Phase 28 polish or post-v1.6. Phase 27 explicitly does NOT touch the tool (D-10).
- **Unparking v1.1 Phase 4 FM1608 byte-0 read bug** as related to Phase 27 RCA. The FM1608 bug is Uno-specific (parked because operator had only one Uno R3 board with the bug, and 8 attempted fixes didn't help); Phase 27's bug is Leonardo-specific. Different boards, different silicon, likely different root causes. Forward-reference if Phase 27 RCA implicates the data-input path family; don't unpark proactively.
- **`firestarter info <chip>` crash** (`TypeError: '<=' not supported between instances of 'list' and 'int'` at `ic_layout.py:167`). Out of v1.6 scope per Phase 26 follow-up; carry-forward.
- **W27C512 chip-database alias gap (`0xda01` accept).** Out of v1.6 scope per Phase 26 follow-up; carry-forward.
- **avrdude-mcu-detection-fallback + w27c512-eeprom-misclassification** — v1.5 backlog carryforwards; explicitly out of v1.6 scope per `.planning/REQUIREMENTS.md` §"Future Requirements".
- **uno328pb-silicon RCA leg.** DEFERRED until operator reflashes the third board. Phase 29 carries the multi-board verification; if uno328pb-silicon is reflashed before Phase 29, Phase 27 RCA may need a follow-up addendum.

### Reviewed Todos (not folded)

No matching todos surfaced by phase-scoped search beyond `large-read-data-jitter-uno328pb.md` itself (which IS the v1.6 source backlog item; Phase 30 / DOC-01 moves it out of `pending/`). The W27C512-alias and `firestarter info` crash items are Phase 26 SUMMARY follow-ups, not pending todos.

</deferred>

---

*Phase: 27-root-cause-analysis*
*Context gathered: 2026-05-21 via /gsd:discuss-phase 27 (Auto Mode — gray areas auto-resolved with recommended options; no AskUserQuestion prompts per harness Auto Mode)*
