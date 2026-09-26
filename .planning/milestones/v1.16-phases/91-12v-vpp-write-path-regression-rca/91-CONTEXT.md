# Phase 91: 12V-VPP Write-Path Regression RCA - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning
**Source:** Operator inline handoff (autonomous-control grant) + Phase 90 bench evidence

<domain>
## Phase Boundary

Root-cause and fix the reproducible **12V-VPP write-path regression** surfaced by the
Phase 90 bench on recompose firmware `a296195` (Phase-89 primitive recompose). On
Leonardo + RURP Rev 2.0:

- **All 4 READ paths** are byte-identical to the v1.15 baseline (read path is
  behavior-preserving).
- **5V / no-VPP write paths PASS:** W29C020 (0x05, flash4), FM1608 (0x28, SRAM/FRAM).
- **12V-VPP write paths FAIL-INVESTIGATE:**
  - **SST39SF040** (0x06, FLASH-AMD-ALT, flash3, 524288 B) — write A: firmware-level
    `Operation timed out` (RC=1); write B: reports "successful (~177s)" but `verify`
    fails — chip holds deterministically-wrong content `ebca6266…`. Uses primitives
    **P4/P7, NOT P3**.
  - **W27C512** (0x07, EPROM-STD, 65536 B) — `write -b` RC=1 `bad bytes:921 @0x000000`,
    reproducible across reseat, on a clean 12.0–12.1 V VPP rail. Uses **P3
    `vpp_check_window`** (−402 B, the single biggest recompose change).

The common axis is the **12V-VPP write path**. A P3-only explanation does NOT cover
both chips (0x06/flash3 has no P3). The two symptoms differ (bad-bytes-at-start vs
write-A-timeout + wrong-content), so the RCA must explain both.

This phase delivers: (a) a controlled A/B that attributes the regression
(recompose-causal vs pre-existing; firmware vs host), (b) a mechanism explanation for
both symptoms, (c) a proposed fix (or documented accepted deferral), and (d)
disposition of the 0x06/0x07 PROTOCOL-LEDGER rows.

</domain>

<decisions>
## Implementation Decisions (operator-locked)

### Autonomy & interaction
- **Operator has left the bench and handed full autonomous control.** Do NOT ask
  questions — the operator cannot answer. Keep working until the issues are fixed and
  the SST39SF040 is confirmed working. Make and record reasonable engineering calls.

### Bench hardware (fixed for this session)
- **Controller:** Leonardo on `/dev/ttyACM0` (confirmed: `firestarter fw` →
  `leonardo`, fw version string `3.0.0b10`).
- **Shield:** **RURP Rev 2.0** — operator-stated; `firestarter hw` reports
  "Rev 2.0-class" (consistent). Treat Rev 2.0 as ground truth; no shield swap this
  session.
- **Chip seated:** **SST39SF040 (0x06)** is in the socket. Operator has measured all
  pins — the IC is **properly seated**. Therefore a blank/contact-fault read is NOT a
  seating problem; do not attribute failures to seating.

### Firmware reflashing (authorized)
- I MAY reprogram the Leonardo (sideload firmware) **with the SST39SF040 left in the
  socket** — the operator authorized this explicitly, and per project rule the
  **Leonardo is EXEMPT from chip-out-before-sideload** (only Uno-class boards need
  chip-out). This unblocks the A/B (flash b10 vs a296195) without operator presence.

### Scope split — SST39SF040 now, W27C512 deferred
- **SST39SF040 (0x06):** full bench work is in-scope this session — reproduce the
  failure, run the A/B, apply the fix, and **confirm write+verify works** on the bench.
  This is the phase's must-prove deliverable.
- **W27C512 (0x07):** bench re-validation is **DEFERRED to operator return** (it
  requires a chip swap, which only the operator can do). The RCA *analysis* and *fix
  design* for 0x07 are still in-scope now (code/diff analysis + shared-axis reasoning),
  but its bench PASS/graduation waits for the operator. Leave a ready-to-run W27C512
  bench checklist for operator return.

### A/B method (recompose-causality + fw-vs-host isolation)
- Firmware A/B: `firestarter@a296195` (recompose, current) vs **`firestarter@a1953c2`
  (tag `3.0.0b10`, v1.15 baseline)**. Build with `pio run -e leonardo`, flash with
  `pio run -t upload -e leonardo`, confirm `firestarter fw` before each silicon op.
- Host A/B: `firestarter_app@e46549f` (current v1.16) vs **`98b3a92` (v1.15 host)**.
- Isolate fw vs host: vary one axis at a time. Read paths are known-clean, so the
  fault is on the 12V-VPP **write** path specifically.

### Evidence & safety conventions (inherited from Phase 90 / v1.15)
- Write-cycle method = the v1.15 **`write -b` direct path** (`write -b A` → `verify A`
  → `write -b B` → `verify B` → `consistency-check N=3`). Do NOT use `dev write-cycle`
  (blank-check fails on flash). PASS = write-cycle-final SHA byte-identical to the
  v1.15 baseline.
- Commit per-dir `SHA256SUMS.txt` + a bench log, not multi-MB binaries (v1.15
  convention).
- VPP/VPE monitors are measure-only and do not route voltage to the socket — safe to
  read with a chip seated.
- Both failing chips are rewritable/recoverable; the SST39SF040 currently holds the
  wrong `ebca6266…` content from Phase 90 — overwriting it during fix-validation is
  expected and fine.
- **Submodule gitlinks stay PINNED at b10** in the meta repo (D-06) — do NOT bump
  gitlinks per-phase. The fix commits land inside the sub-repo on the v1.16 branch.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Regression evidence (what failed, exact symptoms)
- `.planning/v1.16/ledger/bench/BENCH-LOG.md` — per-chip read+write SHA verdicts, exact
  failure strings, VPP rail readings, reseat-reproducibility.
- `.planning/phases/90-per-protocol-bench-validation-ledger/90-04-SUMMARY.md` — Phase 90
  disposition, failure axis, RCA scope handed forward.
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` — the 0x06/0x07 FAIL-INVESTIGATE
  rows to disposition.

### Firmware under investigation (recompose, the suspected regression source)
- `firestarter/src/proms/primitives.cpp` + `firestarter/include/primitives.h` — the
  P3/P4/P5/P7 shared primitives introduced by the Phase-89 recompose.
- `firestarter/src/proms/eprom.cpp` — `eprom_check_vpp` / W27C512 (0x07) write path
  (uses P3 `vpp_check_window`).
- `firestarter/src/proms/flash_type_3.*` / flash3 — SST39SF040 (0x06) write path (uses
  P4/P7).
- The git diff `a1953c2..a296195` restricted to the VPP-application / write-init /
  polling path is the primary RCA artifact.

### Project rules
- `.planning/ROADMAP.md` — Phase 91 section (goal + 3 success criteria).
- `.planning/REQUIREMENTS.md` — LEDGER-02 (graduate on-hand silicon to PASS).
- `firestarter/CLAUDE.md` — firmware build/flash conventions (PlatformIO, 250000 baud).

</canonical_refs>

<requirements>
## Phase Requirement IDs (set at planning)

- **RCA-91** — The regression is attributed to a specific cause via controlled A/B
  (recompose-causal vs pre-existing; firmware vs host isolated), and BOTH symptoms are
  explained (W27C512 bad-bytes-@0x0 at clean 12.0V; SST39SF040 write-A-timeout +
  deterministically-wrong write-B). Covers Success Criteria 1 + 2.
- **FIX-91** — A fix is proposed and applied (or a documented, accepted deferral); the
  SST39SF040 (0x06) write+verify is bench-confirmed byte-identical to the v1.15
  baseline on Leonardo + Rev 2.0; the W27C512 (0x07) bench re-validation is left as a
  ready-to-run operator checklist (deferred); the 0x06/0x07 PROTOCOL-LEDGER rows are
  dispositioned. Covers Success Criterion 3 and advances **LEDGER-02** for 0x06.

</requirements>

<specifics>
## Specific Ideas / Leads

- **Primitive-recompose suspicion:** the recompose extracted P3 `vpp_check_window`
  (−402 B). W27C512 is the only failing chip that exercises P3 — its failure at
  write-start (~921 bytes) is consistent with a VPP-gate engage/settle timing change at
  write-init. But flash3 (SST39SF040) has no P3, so look for a *shared* change across
  the recompose's VPP-application / regulator-routing / poll-readback path that touches
  both the EPROM and flash3 write paths — e.g. P4/P5/P7, regulator bit ordering, or a
  shared timing/delay default that the recompose altered.
- **Read is clean, write is not:** the fault is specifically in the write-direction
  12V-VPP sequencing — VPP enable/settle, write-strobe/pulse timing, or post-write
  polling/readback — not in addressing or data-bus integrity.
- **A/B is decisive:** if b10 fw + current host writes SST39SF040 clean, the regression
  is firmware (recompose) — the most likely outcome given reads are clean and 5V writes
  pass. If b10 fw still fails, suspect host or pre-existing hardware.

</specifics>

<scope_fence>
## Out of Scope / Deferred

- **W27C512 (0x07) bench re-validation / graduation** — deferred to operator return
  (chip swap required). RCA analysis + fix design for 0x07 remain in-scope now.
- **No shield swap, no other chips** this session — only the seated SST39SF040.
- **No gitlink bump** in the meta repo (stay pinned at b10).
- **No new programming capability / no new chips** — this is a regression fix only.
- Do not promote any beta/stable tag — milestone close is operator-gated.

</scope_fence>

<deferred>
## Deferred Ideas

- W27C512 0x07 bench PASS + ledger graduation → operator-return bench checklist.
- Any broader recompose audit beyond the 12V-VPP write path → only if the RCA points
  there.

</deferred>

---

*Phase: 91-12v-vpp-write-path-regression-rca*
*Context gathered: 2026-06-26 via operator inline autonomous-control handoff*
