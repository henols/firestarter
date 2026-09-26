# Phase 143: Host Timeout, Progress & Pulse Override - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-12
**Phase:** 143-host-timeout-progress-pulse-override
**Areas offered:** Timeout budget shape, Where progress comes from, What HOST-03 adds, `--pulse-us` surface & bounds
**Areas selected:** Timeout budget shape, Where progress comes from, `--pulse-us` surface & bounds
**Areas not selected (decided by Claude):** What HOST-03 adds

**Order note:** the progress area was taken **first**, out of the order selected, because a firmware-side
heartbeat resets the host's response-timeout window on its own — so the progress mechanism constrains
what HOST-01 can be. Flagged to the operator before proceeding.

---

## Where progress comes from (HOST-02)

### Q1 — where does progress during a long block come from?

| Option | Description | Selected |
|--------|-------------|----------|
| Firmware DATA progress (`0xE0`) | Emit the existing `MSG_DATA_PROGRESS` from the per-byte loop. Real moving bar, no new message id, resets the host timeout window. Cost: dual-repo; `eprom.cpp` touched so the blob-SHA-pinned D-13 golden must be re-derived and the trace shifts; spends Leonardo's 2130 B; `_main_phase_send_data`'s strict OK/MAIN/ERROR loop must learn a DATA branch with `ack_data=False`. | ✓ |
| Firmware INFO heartbeat | One INFO line every N bytes. Visible by default (post D-09/F-120-02 promotion) and invisible to `get_response`'s filter, so the host needs zero change. Cheapest firmware option. Cost: log lines scrolling, not a bar that moves. | |
| Host-side only, no firmware | Poll `get_response` with a short timeout in a new outer loop, ticking between calls. Stays single-repo; zero flash; ring-fenced generator untouched. Cost: bar shows elapsed/activity, not real bytes programmed; abandoning the generator each cycle risks dropping a mid-flight frame's accumulator. | |

**User's choice:** Firmware DATA progress (`0xE0`)
**Notes:** Recorded as **D-02**. Consequence: the phase becomes dual-repo, materialising hand-off H2 —
recorded as **D-01**, with the roadmap's "independent of 140–142 (different repo)" framing named as a
correction rather than worked around. `0xBF` stays free.

### Q2 — what paces the emission inside the byte loop?

| Option | Description | Selected |
|--------|-------------|----------|
| Time-bounded (`millis()` since last) | Bounds the inter-frame gap by construction regardless of pulse width, so HOST-01's timeout needs no host-side parameter table. Cost: a `millis()` call and a `uint32_t` of state in the hot loop. | ✓ |
| Byte-count (every N bytes) | Cheapest in flash, trivially testable by counting frames per block. Cost: gap unbounded in wall-clock (~3.5 min of silence per frame at `--pulse-us 65535`), forcing a host-computed worst-case budget. | |
| Both: N bytes OR X ms | Best user-facing behaviour and still lets the timeout be small. Cost: most flash, two code paths to test. | |

**User's choice:** Time-bounded
**Notes:** Recorded as **D-03**. This is the decision HOST-01 hangs off.

### Q3 — how does the host reconcile absolute firmware progress with a relatively-driven bar?

Presented after confirming a live defect: `set_progress` (`eprom_operations.py:268-270`) calls
`start(total)` on any differing total, and `start()` closes and re-creates the tqdm bar and zeroes
`current_step`. The write bar starts at `file_size`; `0xE0`'s only existing emitter sends
`handle->mem_size`. A short file or `--address` write would rebuild the bar on every frame.

| Option | Description | Selected |
|--------|-------------|----------|
| Apply `current`, ignore frame total | Firmware keeps `0xE0`'s existing `(address, mem_size)` semantics — one id, one meaning. Host sets position absolutely and never consults the total, so the rebuild path is unreachable. Cost: host must subtract the write's start address. | ✓ |
| Firmware sends block-relative | `(bytes_done, block_size)` added to the host's pre-block baseline. No offset arithmetic. Cost: `0xE0` gains a second payload meaning depending on emitter. | |
| Fix `set_progress`'s rebuild | Update total in place; arguably fixes a latent defect for all callers. Cost: shared code on read and blank-check paths — blast radius beyond this phase's scope. | |

**User's choice:** Apply `current`, ignore frame total
**Notes:** Recorded as **D-04**; the rejected `set_progress` fix is preserved as a deferred idea. The
forced companions — `ack_data=False` and the new DATA branch in `_main_phase_send_data` — are recorded
as **D-05**.

### Q4 — flash posture for the firmware half (F-142-08 hands over 2130 B against a build-FAILURE ceiling)

| Option | Description | Selected |
|--------|-------------|----------|
| Predict first, then measure | A predictions note before the firmware edit (141-PREDICTIONS.md pattern), then measure cold. Early tripwire on the Leonardo ceiling. | |
| Measure and record only | Phase 141/142's standing posture: measure cold, MERGE-05 stays RED, Phase 144 owns reconciliation. Cost: an overrun is discovered at the end. | |
| Hard gate at a named ceiling | Explicit in-phase budget with a shrink ladder ready. Cost: departs from prior posture and pulls Phase 144 work forward. | |

**User's choice:** *Other (free text)* — "don't care about the ceiling of Leonardo, the important thing
is that it fits in the flash"
**Notes:** Recorded as **D-22**: measure cold and record, MERGE-05 stays RED and is Phase 144 / TEST-08's,
`size_baseline.json` read-only, **no** predictions artifact and **no** shrink ladder unless the build
actually overruns. The single binding constraint is that `leonardo` still builds.

---

## Timeout budget shape (HOST-01)

### Q1 (asked) — what carries the response timeout now that a heartbeat exists?

| Option | Description | Selected |
|--------|-------------|----------|
| Write-path constant, global untouched | Separate write-path timeout; `DEFAULT_RESPONSE_TIMEOUT` stays 10 s elsewhere. Covers old firmware, no `max_pulses` host-side. | |
| Leave 10 s, heartbeat is the mechanism | Zero host change; heartbeat resets the window with 10–20× margin. Cost: a new host against pre-heartbeat firmware still times out and cannot version-detect it. | |
| Raise the global constant | One constant, every path covered. Cost: every other command's dead-board detection slows to the same value. | |

**User's choice:** *None of the above* — "I was thinking wrong, in the datasheets it says how many
[pulses] that shall be", clarified on follow-up as **"25 for 0x07/0x08, 255 for 0x0B"**.
**Notes:** The question's premise was rejected rather than answered. The operator's point: the pulse count
is datasheet-specified — already Phase 140's `max_pulses` column — so the worst-case block time is
**deterministic** and the budget should be *derived*, not picked. The question was reframed rather than
re-asked. Claude flagged two arithmetic corrections before re-asking: `0x0B`'s 255 pulses is not its real
bound (`energy_cap_us = 50000` bites first — H4 measured exactly 50 ms/byte on every shipped width, so 255
over-estimates ~2.5×), and the overprogram term is exactly 0 today because all three rows ship
`overprogram_factor = 0`. Both recorded as **D-11**.

### Q2 (reframed) — where does the host get the datasheet pulse counts?

| Option | Description | Selected |
|--------|-------------|----------|
| Firmware advertises the budget | Firmware computes the per-block worst case from the table plus the live `pulse_delay` and reports it in the write ack (the CAP-01 `firmware_max_chunk` pattern). Single source of truth; no datasheet value duplicated; self-corrects when the table changes. Cost: a param appended to an existing ack. | ✓ |
| Mirror the columns in `constants.py` | Established home for firmware-mirrored constants; no wire change. Cost: second definition site for datasheet values; Phase 144's parity leg must be authored to compare them; silently under-estimates when a row gains an overprogram factor. | |
| Fixed generous constant | Smallest diff. Cost: discards the determinism; `--pulse-us 65535` on `0x07` is ~28 min per block. | |

**User's choice:** Firmware advertises the budget
**Notes:** Recorded as **D-07**. Verified afterwards and recorded as **D-08**: `MSG_OK_READY` is already a
length-discriminated variable-length blob (`param_bytes=-1`) extended twice (CAP-01, CAP-02) **without any
`messages.toml` change** — so CAP-03 needs no catalog edit, no codegen, no new message id, and `0xBF` stays
free. The `ver_end`-offset hazard (CAP-02's tail is itself variable-length) is named in the same decision.

### Q3 — what happens when the budget field is absent (older firmware)?

| Option | Description | Selected |
|--------|-------------|----------|
| Generous fixed fallback | Follows CAP-01's precedent (absent means safe default, never an error — Phase 54 D-05 was reversed for this). Old firmware survives a slow write. Cost: a dead board hangs for the fallback on old firmware. | ✓ |
| Keep today's 10 s | No new constant; dead board still reports fast. Cost: HOST-01 satisfied only against matching firmware. | |
| Refuse the write | Never programs under an unreasoned timeout. Cost: hard regression — writes that work today stop working. | |

**User's choice:** Generous fixed fallback
**Notes:** Recorded as **D-10** with a **derived** default of 120 s (>2× the worst shipped-database block:
`0x0B` 51.2 s, `0x07`/`0x08` 25.6 s) and an explicit residual non-claim — the realistic absent case is a
mid-milestone v1.31 build (new loop, no CAP-03, on the bench now), on which a `--pulse-us` above ~4700 µs
can still time out.

### Q4 — where does the safety margin live?

| Option | Description | Selected |
|--------|-------------|----------|
| Firmware includes it | The advertised number is already padded for verify passes, VPE settle and serial time — firmware is the only side that knows them. Host uses it verbatim. Cost: padding policy invisible to a host-side reader. | ✓ |
| Host multiplies by a factor | Policy visible and cheap to test in Python; wire value stays a clean derived number. Cost: two contributors to the final timeout. | |
| You decide | Let research pick based on measured verify/settle cost. | |

**User's choice:** Firmware includes it
**Notes:** Recorded as **D-09**, with the reason stated: a too-*tight* budget causes a spurious timeout on
a **working** write — a false failure on real silicon, worse than a generous ceiling.

---

## `--pulse-us` surface & bounds (HOST-04, HOST-05)

**Not discussed — delegated.** The question set (announcement volume, bounds mechanism, and the `0x0B`
over-cap disposition) was presented and the operator declined it: *"you decide"*. All items resolved by
Claude and recorded inline in CONTEXT.md as **D-14** through **D-18**:

| Item | Resolution | Reasoning source |
|---|---|---|
| Plumbing | Shallow-copy the DB dict inside `write_eprom`, set the existing `"pulse-delay"` key | `read_settling_us` / `read_strobe_us` precedent, `eprom_operations.py:765-777` |
| Bounds | `click.IntRange(1, 65535)` — refuses at parse time, structurally before any serial byte | HOST-05's own wording; no hand-rolled check needed |
| Bound provenance | minipro parity (`-o pulse=N` is uint16), **not** the wire type — `extract_long` is unclamped (H3) | H3, deferred to Phase 146 / CLOSE-04 |
| `0x0B` over-cap (50001–65535) | Left to the firmware's existing `MSG_ERR_PULSE_TOO_WIDE` pre-flight; no host mirror of `energy_cap_us` | `eprom.cpp:95-110`, whose own comment names itself this phase's backstop; consistent with D-07 |
| Announcement | Mandatory default-visible report line naming database pulse → override | v1.22 D-04 precedent, `cli_handlers.py:616-628`; provenance for Phase 145's evidence |
| Command scope | `write` only | Requirement text; nothing else emits a program pulse (same reasoning as `--skip-sdp-unlock`, D-17 v1.22) |

---

## Claude's Discretion

- **The whole `--pulse-us` area** — operator said "you decide". Resolved as **D-14…D-18** above.
- **HOST-03's scope** — not selected as a discussion area. Resolved as **D-19…D-21** from the hand-offs
  rather than invented: the render machinery already exists (`messages.py:747-762`,
  `_raise_for_error_response`), what was missing is that the 10 s timeout fired first; the delta is a hint
  on the `_boot_block_hint_message` seam plus a proving test, no expectation of the dead
  `MSG_ERR_WRITE_FAILED` (F-141-06), and the hint must state the aborted-block semantics without offering
  a retry (§4 of the loop record).
- **The advertised budget's encoding** — recorded default `uint16_t` seconds, ceiling-rounded with a 1 s
  floor, appended after CAP-02's variable-length identity tail; `uint32_t` ms is the alternative.
- **D-03's time-bound constant, the per-frame payload source, and the emission call site in the loop** —
  subject to D-23 (one plan, one commit for `eprom.cpp`) and D-22 (it must fit).
- **Plan decomposition and wave structure.** The two halves are separable: the host's D-10 fallback path
  is testable with no firmware change at all.
- **D-12** (leave `DEFAULT_RESPONSE_TIMEOUT` at 10 s for non-write paths) and **D-13** (do not touch the
  GATE-1.8d ring-fenced `_read_and_parse_lines`) were decided by Claude as consequences, not asked.

## Deferred Ideas

Full list with reasons in CONTEXT.md `<deferred>`. Raised or surfaced during this discussion:

- Fixing `set_progress`'s rebuild-on-differing-total — the rejected Q3 option, kept as a real latent defect.
- Intra-block progress for non-EPROM write families — D-06's explicit non-claim.
- A combined byte-count-OR-time cadence — D-03's rejected third option.
- Host-side warning for a `--pulse-us` above `0x0B`'s energy cap — free if CAP-03 ever advertises the cap.
- Reconciling H3's unclamped `extract_long` — Phase 146 / CLOSE-04.
- Correcting the roadmap's "Phase 143 is independent of 140–142" prose — Phase 146 / CLOSE-04.
- Seven keyword-matched todos reviewed, **none folded** — the four scoring 0.9 matched on bare-word
  overlap only and belong to other protocol families or subsystems.
