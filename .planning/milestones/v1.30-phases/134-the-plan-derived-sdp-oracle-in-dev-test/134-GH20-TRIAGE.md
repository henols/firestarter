# 134-GH20-TRIAGE: gh#20 triaged against the baseline-transition gate

**LEG-18's finding artifact.** Records what this phase's leg would now do on gh#20's exact bench —
it does **not** diagnose the reporter's chip and does **not** establish that a lock inhibited any
write. The public reply is Phase 137's (CLOSE-06), behind a blocking operator wording review. This
document is recorded, not posted.

**Re-verified read-only, 2026-08-04**, at plan `134-11` execution time:
`gh issue view 20 --repo henols/firestarter_prom` — **state OPEN, unchanged**, 0 comments, no label,
no assignee. Every field below is byte-identical to `134-RESEARCH.md` §4.8's live capture; nothing
changed on the issue between research and this triage.

---

## 1. The report, as measured

`gh issue view 20 --repo henols/firestarter_prom`:

| Field | Value |
|---|---|
| state | **OPEN**, created 2026-07-30T16:44:03Z |
| title | `[dev test] at28c256 — FAIL (00e121446ceb)` |
| host | `3.0.0b14` |
| hw_revision | `Rev 2.3` |
| chip | `at28c256` |
| protocol | `13` |
| schema_version | `1.2` |
| steps | `id NA` (no chip-id in DB entry) · `read OK` · **`blank-check BAD`** · **`write BAD`** (fingerprint `indeterminate`) · **`verify BAD`** (fingerprint `indeterminate`) · `erase NA` (protocol 0x0D has no erase operation; each page write auto-erases internally) |
| banner | **`n_ran 4, m_applicable 4`** — reads as "4 of 4 ran", i.e. complete |
| voltage | `vpp 11800 mV` / `vpe 13700 mV` (before == after, both directions) |
| dedup_fingerprint | **`00e121446ceb`** |
| db_diff | `current_support_status: supported`, `proposed_disposition: suggests community-fail signal (advisory)`, `ladder_state: community-fail` |

No comments, no label, no assignee, no linked PR. Nothing about the issue's state changed since
`134-RESEARCH.md` §4.8 captured it.

---

## 2. The triage against the baseline gate

On this exact bench — `blank-check`, `write`, and `verify` all `BAD`, indicating the write path
never took effect — this phase's leg's `write-baseline-b` step would itself report `BAD` (a
write that does not change the read-back). `_baseline_closes_sdp_gate` (`chip_test.py`, D-08/D-20)
closes on **any** non-OK baseline verdict — BAD, marginal, SKIPPED, or NA — precisely because a
dead write path is as disqualifying as a chip-ID mismatch for the decision to send an irreversible
command. Once closed, `sdp-lock`, `write-inhibited`, `sdp-unlock`, and `write-restored` all render
`SKIPPED` with the reason **"no lock was emitted — baseline gate closed"** (D-20's own wording,
never `_DESTRUCTIVE_GATE_REASON`'s chip-ID phrasing) — no lock is ever emitted against this bench.

A leg without the baseline gate (i.e. D-08/D-20 absent) would instead dispatch `sdp-lock` for real
against a part whose write path never worked, and would report the misleading close `sdp-unlock OK`
— an emission claim about a part that was never proven writable in the first place, on a family
whose protection state cannot be read back afterward. That is gh#20's exact hazard, reproduced live
by `134-04-SUMMARY.md`'s non-vacuity obligation #6: with `OP_SDP_LOCK` temporarily removed from
`_SDP_LEG_GATED_OPS`, a dead-write-path run against `AT28C256` was observed to call
`operator.sdp_lock` for real (verbatim transcript in that plan's SUMMARY). The gate that prevents
this is committed and named:

- **Gate test:** `tests/test_chip_test_sdp_leg.py::test_baseline_gate_closes_dead_write_path_allow_chip_full_leg`
  (plan `134-04`) — the committed proof that a dead-write-path double against `AT28C256` closes the
  gate and skips all four gated ops.
- **D-20's unlock-inclusion test:** `tests/test_chip_test_sdp_leg.py::test_leg09_destructive_gate_never_skips_the_explicit_unlock_step`
  (plan `134-04`) — proves the baseline gate's inclusion of `sdp-unlock` does not weaken LEG-09's
  distinct destructive-gate guarantee.

---

## 3. The banner change

Today, gh#20's own banner reads **`n_ran 4, m_applicable 4`** — "4 of 4 ran" — which reads as a
complete, uneventful run. Under this phase's leg, plan `134-10`'s pinning test
(`tests/test_chip_test.py::test_count_applicable_sdp_gated_allow_chip_ratio_drops`) measured the
identical dead-write-path shape (an `AT28C256`-class ALLOW chip, gated baseline) and found
`m_applicable == 10`, `n_ran == 6` — the banner would read **"6 of 10 ran"**, not the "5 of 10"
`134-CONTEXT.md`'s D-20 narrative originally stated (see §6 below for the correction). Either
reading drops the ratio well below "complete" — the point this phase's leg exists to make visible.

---

## 4. D-11's cost, named

The six added SDP-leg steps re-key every ALLOW chip's `dedup_fingerprint` (`diagnostic_report.py`,
which hashes `op=verdict:cls` per step). gh#20's own `dedup_fingerprint` **`00e121446ceb`** is
**orphaned** by this phase's leg: a resubmitted report from the same bench, once this phase's code
is live, would hash differently and stop grouping with this b14-era report — the accumulated
N-greater-or-equal-2 promotion count this specific fingerprint may have been accruing resets, along
with the same reset for all other 43 ALLOW chips.

This cost is **accepted and recorded**, not fixed here (plan `134-06`'s own decision, D-11).
Excluding the SDP steps from the hash was considered and rejected at design time — a leaked lock
would then dedup identically with a genuinely held one, blinding the exact mechanism gh#20's own
triage depends on. The **outward description of this discontinuity is Phase 137's release notes**
(CLOSE-05) — this document only names the specific orphaned id so that release-note author has the
concrete instance to cite.

---

## 5. What this does NOT establish — the Evidence Ceiling

Restated verbatim from `133-RECORD.md` §6, because it governs this triage exactly as it governed
Phase 133's proofs:

> **This phase proves that the mechanism cannot strand a chip or lose a report to a transport
> error, and that the op registries fail closed. It proves NOTHING about SDP behaviour on
> silicon.**
>
> - **A locked die is unrepresentable in either repo's stubs.** Both the host repo's fixtures and
>   the firmware repo's native test harness model the *bus*, never the die's *protection state* —
>   no test anywhere in this phase can simulate real SDP inhibition. Fixtures can only pin the
>   host's *response* to a scripted read-back.
> - **Protection state is not readable on this family.**
> - **`0x0D` stays `UNVERIFIED`** at the database level.
> - **No AT28C part has ever been in operator inventory.**

Applied to gh#20 specifically: this triage explains what the tool would now **do** on that bench —
close the gate, skip the lock, render the drop — it does **not** diagnose the reporter's chip, and
it does **not** establish that any lock ever inhibited any write on that hardware (no lock was ever
attempted against it in the first place; the reporter's failure is entirely in the pre-lock
baseline write path). No fixture in this phase, or in Phase 133, simulates real SDP inhibition.

**The leg is explicitly NOT protected by the chip-ID gate.** gh#20's own `id` step reports `NA`
("no chip-id in DB entry") — `AT28C256`, like all 43 measured SDP-ALLOW chips, has `chip-id == 0`
in the shipped database (re-measured live by plan `134-10`'s
`test_all_sdp_allow_chips_have_zero_chip_id_measured_live`), so the destructive chip-ID gate is
**structurally vacuous** for this entire population. What actually protects gh#20's bench from a
false lock is the **baseline-transition gate** (§2 above), not chip identity. Saying otherwise —
"the leg is gated by chip ID" — is the v1.22 C-5 overclaim class (`grep -ci 'gated by chip[- ]id'
tests/ firestarter/ -r` returns 0 in the shipped tree, confirmed by plan `134-10`).

---

## 6. Corrected reading, carried forward from the phase's own record

`134-CONTEXT.md`'s D-20 stated gh#20's shape would produce `n_ran=5, m_applicable=10`. The actual
measured value, run live against the identical dead-write-path shape by three independent plans
(`134-04`, `134-07`, `134-10`), is **`n_ran=6, m_applicable=10`** — because `write-baseline-a` is
never itself gated (only the four `_SDP_LEG_GATED_OPS` members are skipped once the gate closes;
D-08's own design) and reports OK against a dead-write-path double (its expected read-back is
pattern A, which the double always returns). Both readings are carried here rather than silently
reconciled to the stale "5", per this project's standing practice.

---

## 7. Hand-off

The **public reply to gh#20 is Phase 137's** (CLOSE-06), behind its blocking operator wording-review
gate, alongside the gh#12 reply. This phase — and this document — record the finding only (D-16).
No write-shaped GitHub-CLI or git-publishing action of any kind was run to produce this document;
the GitHub CLI was invoked exactly once, in its read-only view form, to re-verify the issue's
current state (§1 above).

---

*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Recorded: 2026-08-04, plan 134-11.*
