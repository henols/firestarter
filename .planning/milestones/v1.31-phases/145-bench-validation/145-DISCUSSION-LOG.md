# Phase 145: Bench Validation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-15
**Phase:** 145-Bench Validation
**Areas discussed:** Bench inventory & the 0x07 part, The 0x07 evidence bar, Which 143/144 hand-offs get bench-proven, Disposition & failure rules

---

## Bench inventory & the 0x07 part

**Q: Which part carries BENCH-01's required 0x07 proof?**

| Option | Description | Selected |
|--------|-------------|----------|
| W27C512 (Winbond) | EEPROM, 12 V, chip-id 0xda08. Electrically erasable — a full 64K erase→write→read-back can repeat N times. | ✓ |
| TMS27C512 (TI) | UV-EPROM, 13 V. Closer to the 27C family gh#15 is about, but one-shot with no eraser on hand. | |
| Both — W27C512 first, TMS27C512 once | Repeatable proof plus one true-UV data point, at the cost of an irreversible part. | |

**User's choice:** W27C512 (Winbond)
**Notes:** Repeatability is what makes N≥3 affordable; the TMS27C512 is deliberately not spent.

**Q: Which of the opportunistic parts are physically on the bench right now?**

| Option | Description | Selected |
|--------|-------------|----------|
| AM27C020 (0x08) | The v1.18 Phase 99 part; still marginal (60/64 then 0/64), no eraser. | |
| M2716 or M2732 (0x0B) | 25 V NMOS. Phase 79 parked its graduation "when a part is on hand". | |
| Neither — both get skipped-with-reason | BENCH-02 discharged by two honest skip records naming the missing part. | ✓ |

**User's choice:** Neither — both get skipped-with-reason
**Notes:** Phase 145 becomes a 0x07-only bench phase plus the inherited hand-offs.

**Q: Which shield revision will be under the Leonardo?**

| Option | Description | Selected |
|--------|-------------|----------|
| Rev 2.2 | Newest board; R41=10k confirmed post-Phase-35. | |
| Rev 2.0 | The board Phase 99 (AM27C020) and Phase 79 (VPE rail) both ran on. | ✓ |
| Modified Rev 0 | Carries the Phase 44 read-path fault history. | |
| Decide at the bench | Record whichever board is seated at run time. | |

**User's choice:** Rev 2.0
**Notes:** Asked rather than inferred — the EEPROM `hw_revision` byte cannot distinguish the three boards. Choosing Rev 2.0 keeps this phase's figures comparable to Phases 79 and 99.

**Q: If plain `write` turns out NOT to erase the W27C512 on the 0x07 path, what carries BENCH-01?**

| Option | Description | Selected |
|--------|-------------|----------|
| Pure 1→0 into a 0xFF region | Phase 99's shape: every target bit is a legal bit-clear, isolating the program path with no erase dependency. | ✓ |
| Write the chip's own content back | Phase 53-07's non-destructive trick — but no bit flips, so it proves transport, not programming. | |
| Stop and report BENCH-01 unmet | Treat "no erase on 0x07" as blocking; leaves the milestone's only silicon claim empty. | |

**User's choice:** Pure 1→0 into a 0xFF region
**Notes:** `write -b` is explicitly ruled out as a workaround — it sets `FLAG_SKIP_ERASE` and can report success while producing bad bytes.

**Q: What must the 0x08 / 0x0B skip records contain?**

| Option | Description | Selected |
|--------|-------------|----------|
| Full disposition record | Missing part, last known bench state with numbers, and an explicit "NOT inferred from the 0x07 result". | ✓ |
| Minimal skip line | Names the missing part and nothing else. | |
| Full record + backlog item | As full, plus a tracked backlog entry for part acquisition. | |

**User's choice:** Full disposition record

---

## The 0x07 evidence bar

**Q: What does BENCH-01's write cover?**

| Option | Description | Selected |
|--------|-------------|----------|
| Full 64K chip | 64 blocks, per-block VPE hold, a genuinely long write that doubles as the CAP-03 budget proof. | ✓ |
| Full 64K + one region run | Full-chip for BENCH-01 plus a short region run for cheap repeats. | |
| One region only | Fast and chip-sparing, but would not exercise the long-write timeout path at all. | |

**User's choice:** Full 64K chip

**Q: What is the compare oracle for read-back?**

| Option | Description | Selected |
|--------|-------------|----------|
| SHA-256 of source vs read-back | Independent of the CLI's own verify logic (the Phase 99 pattern). | |
| The CLI's own verify | Cheapest, but the thing under test judges itself. | |
| Both, recorded separately | Each verdict on its own line so a disagreement between them is visible. | ✓ |

**User's choice:** Both, recorded separately

**Q: How many runs, and what makes the result trustworthy?**

| Option | Description | Selected |
|--------|-------------|----------|
| N≥3 write cycles, all pass | Three independent erase→write→read-back cycles. | |
| 1 write + N≥3 read-backs | Proves read stability but not program repeatability. | |
| N≥3 writes + read stability per write | Three write cycles, each followed by repeated reads. | ✓ |

**User's choice:** N≥3 writes + read stability per write
**Notes:** Program repeatability and read repeatability are different failure modes; 0x08's history is a part that reads stably and programs unreliably.

**Q: Is there a pre-v1.31 control run on the old firmware?**

| Option | Description | Selected |
|--------|-------------|----------|
| No control — absolute proof only | The milestone claims fidelity, not improvement; no BENCH requirement asks for a differential. | ✓ |
| Yes — one control run | A before/after data point, at the cost of a reflash cycle and an invited comparative claim. | |

**User's choice:** No control — absolute proof only

**Q: What gets written across the three cycles?**

| Option | Description | Selected |
|--------|-------------|----------|
| A different image each cycle | Forces real erase-then-program transitions every cycle. | ✓ |
| Same image all three cycles | Cycles 2–3 could pass without any bit flipping — the false-green `write -b` produces. | |
| Different image + one all-0x00 cycle | Harshest bit coverage, hardest on the part. | |

**User's choice:** A different image each cycle

**Q: What pattern makes a failure diagnosable?**

| Option | Description | Selected |
|--------|-------------|----------|
| Address-derived pattern | A mismatch says WHICH address is wrong and whether the failure is address- or data-shaped. | |
| Pseudo-random via tools/gen_test_image.py | Reuses the shipped generator; harder to read structurally. | |
| You decide | Claude's call, with the attributability constraint binding. | ✓ |

**User's choice:** You decide
**Notes:** Constraint recorded in CONTEXT.md — a mismatch must be attributable to an address, not merely counted.

---

## Which 143/144 hand-offs get bench-proven

**Q: Which inherited hand-offs does Phase 145 actually discharge?** *(multi-select)*

| Option | Description | Selected |
|--------|-------------|----------|
| Real progress-bar motion | HOST-02's user-visible claim, never seen on a board. | ✓ |
| Long write survives, no timeout | The CAP-03 budget path on real hardware; near-zero marginal cost. | |
| --pulse-us on real silicon | HOST-04 end to end, including above the 4687 µs residual-gap threshold. | |
| Measure A1 (per-pulse overhead) | Convert the [ASSUMED] ~20-60 µs/pulse into a measured figure. | |

**User's choice:** Real progress-bar motion only
**Notes:** Follow-up established that "long write survives" was excluded as a separate *work item*, not as a *claim* — see the next question. `--pulse-us` and A1 were later folded back as stretch items.

**Q: The 64K write either completes or times out — should the record claim timeout survival?**

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — free, so state it | BENCH-01's completion IS the evidence the CAP-03 budget path holds on hardware. | ✓ |
| No — leave it unclaimed | Phase 146's ledger would carry 143's H4 as still-unproven. | |

**User's choice:** Yes — free, so state it

**Q: How is "real bar motion" captured as evidence?**

| Option | Description | Selected |
|--------|-------------|----------|
| Timestamped stderr capture, frames counted | >1 update inside a single 1024-byte block IS intra-block motion — a checkable claim. | |
| Operator eyes-on, witnessed statement | Honest, matches the 99-03 style, but not independently reproducible. | |
| Both | Machine-counted frames as primary, plus eyes-on that the bar moved smoothly rather than bursting at the end. | ✓ |

**User's choice:** Both

**Q: Where do the excluded hand-offs (`--pulse-us` on silicon, A1) land?**

| Option | Description | Selected |
|--------|-------------|----------|
| Open hand-offs, no v1.31 owner | Recorded as explicitly not discharged; Phase 146 cannot run a bench. | |
| Backlog items | Same, plus real queued backlog entries. | |
| Fold in if the bench goes well | Stretch items, attempted only if the required runs complete cleanly. | ✓ |

**User's choice:** Fold in if the bench goes well
**Notes:** If not reached, they must still be recorded as explicitly-not-discharged with no v1.31 owner — never silently dropped.

---

## Disposition & failure rules

**Q: If the REQUIRED 0x07 run fails, what does Phase 145 do?**

| Option | Description | Selected |
|--------|-------------|----------|
| Bounded in-phase triage, then stop | A named triage budget before halting. | |
| Stop immediately, hand to /gsd-debug | First failure halts; root-causing gets its own session with its own state. | ✓ |
| Record and continue to Phase 146 | Let the ledger report the silicon claim as unmet, no remediation. | |

**User's choice:** Stop immediately, hand to /gsd-debug
**Notes:** Combined with the pass rule below, one physically-attributable failure may be re-seated and re-run once before the halt applies.

**Q: What about a run that happens but is inconclusive?**

| Option | Description | Selected |
|--------|-------------|----------|
| Name a third state explicitly | "Attempted — inconclusive", the shape Phase 99 called DEFER. | |
| Two states only | Anything not a clean pass is a fail; anything not attempted is a skip. | ✓ |

**User's choice:** Two states only
**Notes:** Under this taxonomy Phase 99's own 60/64 result would be a **fail**, not a qualified pass. Decided before any run so a partial result cannot be argued into the friendlier bucket.

**Q: How is BENCH-03 (no support_status changes) proven?**

| Option | Description | Selected |
|--------|-------------|----------|
| Machine-checked diff over the milestone range | Whole-milestone diff, which is what the requirement's wording says. | ✓ |
| Recorded git-diff statement | Same evidence, no committed gate. | |
| Committed test + the diff | More durable, but new gate code in a bench phase. | |

**User's choice:** Machine-checked diff over the milestone range
**Notes:** Measured during discussion — `chip_database.json` already has zero diff from the app's v1.31 base `4d18b645`.

**Q: What exactly counts as BENCH-01 passing?**

| Option | Description | Selected |
|--------|-------------|----------|
| 3/3 cycles byte-exact, both oracles | Strict; anything less halts the phase. | |
| 3/3 byte-exact, one clean re-seat allowed | One failure attributable to a named physical cause may be discarded and re-run once, with both recorded. | ✓ |
| 2/3 with the miss characterized | Softer bar; risks recording a marginal part as validated. | |

**User's choice:** 3/3 byte-exact, one clean re-seat allowed

**Q: What's the `--force` policy, given the known W27C512 VPP-high init guard?**

| Option | Description | Selected |
|--------|-------------|----------|
| No --force; adjust the pot instead | Strongest evidence; Phase 99 recorded "--force used? No" as load-bearing. | |
| --force allowed, disclosed per command | Faster; every affected run carries a qualifier. | |
| No --force, and treat a blocked run as a bench fault | If the guard fires that's a setup problem to fix before spending the chip. | ✓ |

**User's choice:** No --force, and treat a blocked run as a bench fault
**Notes:** This withdraws, for this phase, the standing "use force and ignore vpp" permission recorded from earlier bench sessions.

---

## Claude's Discretion

- The write-image pattern for the three cycles (binding constraint: a mismatch must be attributable to an address, not merely counted).
- The pre-flight gate structure and the bench-record filename and section order (99-03-BENCH-LOG.md is the house precedent).
- The stderr capture and per-block frame-counting method for the bar-motion claim.
- Plan decomposition and wave structure, including where the D-03 erase-capability determination sits relative to the first spend.
- The exact read-back command forms.

## Deferred Ideas

- A true-UV `0x07` data point on the TMS27C512 — reachable only by consuming an irreversible part.
- `0x08` and `0x0B` bench validation — blocked on parts, not code. `0x08` additionally carries FUT-08 (uninstrumented program-window VPP droop).
- `--pulse-us` on real silicon and the A1 per-pulse-overhead measurement — stretch items; no v1.31 owner if unreached.
- The `--pulse-us` above-4687 µs budget-mechanism proof.
- A pre-v1.31 differential control run — rejected by decision, not deferred for time.
