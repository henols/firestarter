# Phase 134: The Plan-Derived SDP Oracle in `dev test` - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-04
**Phase:** 134-the-plan-derived-sdp-oracle-in-dev-test
**Areas discussed:** The un-acked opt-out / oracle verdict axis, Baseline-transition shape & leg
composition, The HELD field & report surface, Exit codes & the N-of-M banner

**Area selection:** all four offered areas were selected.

---

## The un-acked opt-out / oracle verdict axis

### Q1 — How should the leg establish that the inhibited-write experiment actually ran as designed?

| Option | Description | Selected |
|--------|-------------|----------|
| Bool as precondition only (Rec.) | `write_eprom() is True` proves validity (reachable only when the state machine succeeded AND the `0x86` ack was seen); `False` ⇒ marginal, never BAD. Read-back alone decides OK vs BAD. No ring-fence change. | ✓ |
| Add a narrow ack seam | Retain observed message IDs on `EpromOperator` after `_disconnect_programmer` so ack-missing and transport-failed are distinguishable. Additive and read-only, but a behavioural edit inside the ring-fenced `eprom_operations.py`. | |
| Read-back only, ignore the bool | Purest LEG-05 reading. Cost: on firmware that silently auto-unlocked, the read-back equals B and the leg reports BAD — accusing the chip when the host's flag was ignored. | |

**User's choice:** Bool as precondition only → **D-01**
**Notes:** Driven by a live measurement: `_operation_context`'s `finally` calls
`_disconnect_programmer()`, which sets `self.comm = None`, so `comm.seen_message_ids` is gone by the time
`write_eprom` returns. Research's truth-table branch 5 ("the ack readable as a *separate* signal") is
therefore unbuildable as written. Flagged at the time that this overturns research P-03 prevention 4's
test spec, resolved in Q3.

### Q2 — `write_eprom` returned False (precondition failed) but the read-back equals pattern B. What verdict?

| Option | Description | Selected |
|--------|-------------|----------|
| marginal — unattributable (Rec.) | Most likely cause is the opt-out not being honoured: firmware auto-unlocked then wrote B. Calling that BAD accuses the chip of leaking when the host's flag was ignored. Exit 2, reason naming both causes. | ✓ |
| BAD — the part is unprotected | A full change to B is a hard fact regardless of cause; louder, never lets a real leak hide behind an unobserved ack. Cost: over-attribution — a chip-fault report for a host-side cause. | |
| marginal, but BAD if a partial change | Split by read-back shape: fully-B ⇒ marginal, partially-changed ⇒ BAD (not what a clean auto-unlock-then-write produces). Most discriminating; one more truth-table arm and fixture. | |

**User's choice:** marginal — unattributable → **D-02**

### Q3 — How should the "verdict is read-back-driven, not bool-driven" proof be built, given the precondition policy overturns P-03's spec?

| Option | Description | Selected |
|--------|-------------|----------|
| Full 2×2 cross product (Rec.) | `(True,A)⇒OK` · `(True,B)⇒BAD` · `(False,A)⇒marginal` · `(False,B)⇒marginal`. The first two hold the bool CONSTANT — a stronger proof than P-03's, since a bool-driven implementation cannot yield two verdicts from one bool. Record P-03 prevention 4's `(False,A)⇒OK` as overturned. | ✓ |
| Three legs, bool held constant | Same core proof minus `(False,B)`; one fewer fixture, but the polarity pin no longer shows suppression in both read-back directions. | |
| Follow P-03 literally | Keep `(True,B)⇒BAD` and `(False,A)⇒OK` — requires abandoning the precondition policy. Listed for completeness; contradicts D-01/D-02. | |

**User's choice:** Full 2×2 cross product → **D-03**

### Q4 — LEG-08 permits BAD or marginal for a degenerate read-back. Which, and decided how?

| Option | Description | Selected |
|--------|-------------|----------|
| Length gate BAD, content marginal (Rec.) | Empty/wrong-length ⇒ BAD (P-02's explicit "`VERDICT_BAD`, never `SKIPPED`"); correct-length degenerate CONTENT (all-`0xFF`/all-`0x00`) routes through `classify_fingerprint` ⇒ marginal, so a contact fault reads as a contact fault. | ✓ |
| All four arms BAD | Loudest; keeps `_FF_RATIO_THRESHOLD`'s tunable number out of the oracle entirely. Cost: a loose socket files as a chip-fault report. | |
| All four arms marginal | Cleanest semantics, BAD reserved for the two attributable findings. Cost: an empty read-back becomes non-blocking — the shape P-02 warns reads as passing. | |

**User's choice:** Length gate BAD, content marginal → **D-04**
**Notes:** Carried into CONTEXT without a further question — routing content-degeneracy through
`classify_fingerprint` creates the non-laundering obligation (a fully-B read-back must be *provably*
unable to reclassify as `blank/contact`). Measured: `B = ~A`, `A` holds ~1 zero byte over 256, so `B`'s
`ff_ratio ≈ 0.004` vs the `0.98` threshold. Captured as **D-05**, a mandated test rather than an argument.

---

## Baseline-transition shape & leg composition

### Q1 — How should the baseline transition be shaped in the plan?

| Option | Description | Selected |
|--------|-------------|----------|
| Two ops — B then A (Rec.) | `write-baseline-b` + `write-baseline-a`, each folding write + read-back into its own single-run arm. Failing direction legible in the op string on the CONSOLE table (`reason` is not rendered there). Leg stays contiguous; shipped write/verify untouched. Cost: 4 new op strings this phase. | ✓ |
| One op — `sdp-baseline` | Single step doing write-B → verify → write-A → verify, detail in `reason`. Smallest vocabulary growth. Cost: console shows only `sdp-baseline BAD` — and this step decides whether a lock is emitted. | |
| Reuse write/verify + one new B op | Closest to research §1.1's "reuse". Costs: leg no longer contiguous, and the A direction's verdict comes from `verify_eprom`'s bool via `_dispatch_multi_run` — the boolean-oracle path P-03 exists to avoid. | |

**User's choice:** Two ops — B then A → **D-07**
**Notes:** Stated before the question: research §1.1's "reuse the existing write + verify, add no op"
cannot satisfy LEG-16 — the shipped pair writes A only, so on a chip already holding A with a dead write
path `verify_eprom` returns True and the step reports OK. The B direction is what makes the gate real.

### Q2 — What is the leg's actual step composition, and what happens to criterion 1's "four"?

| Option | Description | Selected |
|--------|-------------|----------|
| Six steps, correct the "four" (Rec.) | `write-baseline-b · write-baseline-a · sdp-lock · write-inhibited · sdp-unlock · write-restored`. Criterion 1 / LEG-01 / LEG-02's "four" recorded as measured-wrong, both readings in the record; count assertion and REFUSE-chip NA test pin SIX. | ✓ |
| Five steps — drop write-restored | Honours the ROADMAP's own enumeration most closely. Cost: the run ends on `sdp-unlock OK`, an emission claim on a family whose state is unreadable, so LEG-12's NOT-HELD has no evidence behind it. | |
| Exactly four — honour it literally | One folded `sdp-baseline` plus lock/inhibited/unlock; no correction needed. Pays both other costs. | |

**User's choice:** Six steps, correct the "four" → **D-06**
**Notes:** Raised proactively rather than resolved quietly: the ROADMAP's four steps omit
`write-restored` entirely while research §2.3 specifies it, and it is the only step producing evidence
the part was left writable. Research §3.1's happy-path wording ("the unlock sequence was emitted **and
the part accepted a write afterwards**") is unsupportable without it.

### Q3 — How is "a failed baseline must prevent the lock" wired, and what closes it?

| Option | Description | Selected |
|--------|-------------|----------|
| Own gate, closes on not-OK (Rec.) | `_baseline_closes_sdp_gate` mirroring `_id_step_closes_gate`, keyed on a new `_SDP_LEG_OPS` set, with its OWN reason string. Closes on any baseline verdict that is not OK. No change to 133's frozen `_dispatch_sdp` signature. | ✓ |
| Reuse the destructive gate | Zero new machinery, already covered by 133's proofs. Cost: SKIPPED steps would render `_DESTRUCTIVE_GATE_REASON`'s chip-ID wording — actively misleading here. | |
| Precondition inside the lock arm | Keeps the gate next to the decision. Cost: reopens the `_dispatch_sdp` signature 133 D-01 deliberately pinned as a forward contract. | |

**User's choice:** Own gate, closes on not-OK → **D-08**
**Notes:** Framed with gh#20's live data (write BAD / verify BAD on a real b14 bench). Recorded in
CONTEXT that this creates a **seventh** route to a non-running oracle on top of research's R1–R6, which
fails closed under D-08 + D-15 but must be tested in the same family and named as the seventh.

### Q4 — How should `_ALWAYS_WRITES_NOTICE` be made both accurate and unable to re-stale?

| Option | Description | Selected |
|--------|-------------|----------|
| Static prose + derived test (Rec.) | One notice, printed first (D-04 ordering and its committed test untouched). Rewrite to name the SDP lock, the completed-run unlocked state, and the aborted-run recovery in the word "rewrite". Add a test that DERIVES the plan for a representative ALLOW chip and asserts the notice's number matches — P-08 prevention 2. | ✓ |
| Two-part notice | Static line first, plus a per-chip line after `derive_plan` (verified safe on ordering — nothing energises until `read_hardware_revision_value`, and ALLOW chips are never UV). More honest per run; a second surface to keep true. | |
| Derived count in the first line | Most accurate. Rejected on measurement: forces the notice after `write_scope` resolution and `derive_plan`, breaking D-04's printed-FIRST guarantee and its committed test. | |

**User's choice:** Static prose + derived test → **D-09**
**Notes:** Measured that an ALLOW chip now takes **6 write passes** over its 256-byte region (A×2 at
`runs=2`, then B, A, B, A) against a notice promising "written twice".

---

## The HELD field & report surface

### Q1 — How should the HELD / NOT-HELD / NOT-RUN(reason) field be carried?

| Option | Description | Selected |
|--------|-------------|----------|
| Named field + schema 1.3 (Rec.) | Three-valued STRING field on `DiagnosticReport`, rendered in the console report and emitted in `to_dict()`, `SCHEMA_VERSION` 1.2→1.3. Guarded by a test that no boolean named `locked`/`protection_enabled` exists (P-06 prevention 3). `parse_devtest_issue.py` verified tolerant. | ✓ |
| Derive at render time, no field | Research §3.2's discipline intact, no bump. Cost: if the SDP steps are absent entirely (route R6) the field renders NOTHING — the exact invisibility LEG-12 closes. | |
| Field + JSON, no schema bump | Smallest diff. Cost: the artifact shape changes while its own version claims it did not. | |

**User's choice:** Named field + schema 1.3 → **D-10**
**Notes:** Framed as a direct LEG-12-vs-research conflict — LEG-12 requires the field in both surfaces;
research §3.2 says "no new `to_dict()` field". The requirement wins; the shape was the open part.

### Q2 — The `dedup_fingerprint` reset for all 43 ALLOW chips

| Option | Description | Selected |
|--------|-------------|----------|
| Accept and record it (Rec.) | Six new steps necessarily re-key every ALLOW chip; b14/b15-era reports stop grouping and N≥2 counts reset. Name gh#20's orphaned `00e121446ceb` inside the LEG-18 finding; hand the cost to Phase 137's release notes. | ✓ |
| Exclude SDP steps from the hash | Preserves continuity and the promotion ladder. Cost: two reports differing only in SDP outcome dedup as identical — a leaked lock groups with a held one. | |
| Carry a legacy fingerprint too | Continuity without blinding dedup. Cost: a second field and hash nothing else needs. | |

**User's choice:** Accept and record it → **D-11**

### Q3 — Where does LEG-14's gate live and what exactly does it scan?

| Option | Description | Selected |
|--------|-------------|----------|
| Scoped pytest, hand off to 137 (Rec.) | Hoist the SDP recovery wording into named constants; scan THOSE only — "rewrite" present, "erase" absent, plus a non-vacuity leg. Record a note handing Phase 137's CLOSE-03 the constant names. | ✓ |
| Author 137's tools/ scanner now | Front-loads the mechanism and puts it where CI runs tools. Cost: builds another phase's requirement inside this one, and CLOSE-02's target-resolution legs would be authored against an existing tool. | |
| Whole-report grep | The most literal reading. Rejected on measurement: fires on `derive_plan`'s erase-NA reason and on `_ALWAYS_WRITES_NOTICE`, both correct text — RED on clean source, needing exemptions on day one (the 133 D-14 `_sample` shape). | |

**User's choice:** Scoped pytest, hand off to 137 → **D-13**

### Q4 — Does the recovery line print on the happy path, or only when the part may still be locked?

| Option | Description | Selected |
|--------|-------------|----------|
| Both forms — neutral + loud (Rec.) | Loud when the part may still be locked; NEUTRAL one-liner on the happy path affirming the part was left unlocked and that this is evidence, not a guarantee. Via `click.echo`, matching `_ALWAYS_WRITES_NOTICE`. Research §3.2's own position. | ✓ |
| Loud only, silent when fine | Max signal, no dismissal risk. Cost: the report never affirms the end state; the HELD field becomes the only place to find it. | |
| One always-loud line | One string to keep honest. Cost: a warning firing on every successful run is the shape users learn to skim. | |

**User's choice:** Both forms — neutral + loud → **D-12**
**Notes:** The Ctrl-C residual inherited from 133 D-07 is recorded rather than closed: neither form
prints after an abort because `results = run_plan(...)` never completes. The mitigation is D-09's
rewritten notice, printed up front — explicitly **not** a `finally` handler.

---

## Exit codes & the N-of-M banner

### Q1 — LEG-06's "exits 1" is unreachable on any run that also has a marginal step

| Option | Description | Selected |
|--------|-------------|----------|
| Fix the precedence (Rec.) | Replace the naive `max` so BAD outranks marginal — restoring what the source comment AND the `dev_test` docstring already claim. Test a mixed BAD+marginal run at exit 1, plus a non-vacuity leg; audit existing tests asserting exit 2 on mixed runs. | ✓ |
| Leave it, scope LEG-06's test | Zero blast radius. Cost: the milestone's headline finding can arrive wearing the inconclusive code; criterion 2's "exit code 1" satisfied only conditionally. | |
| Fix it, and fix the docstring only | Make the prose true instead of changing behaviour. Cost: LEG-06 and criterion 2 would need a requirement-text amendment. | |

**User's choice:** Fix the precedence → **D-14**
**Notes:** Surfaced as a live defect found during this session, not a design question:
`_VERDICT_EXIT_CODES` maps `marginal → 2` and `BAD → 1` and the code is `max(...)`, so `max(1,2) = 2` —
marginal beats BAD, contradicting both the source comment at `cli_handlers.py:1885-1887` and `dev_test`'s
docstring. The truth table locked in this session has three marginal arms, so the collision is common.

### Q2 — An ALLOW chip whose oracle did not run: both the N-of-M drop and a non-green exit

| Option | Description | Selected |
|--------|-------------|----------|
| SKIPPED + exit floor of 2 (Rec.) | Step stays SKIPPED so it stays out of `_RAN_VERDICTS` and the ratio drops (LEG-13); one non-verdict term in the exit computation raises an ALLOW+NOT-RUN run to at least 2. No change to `_RAN_VERDICTS`/`count_applicable`. Cost: the exit stops being a pure function of verdicts. | ✓ |
| marginal + narrow `_RAN_VERDICTS` | Keeps the exit computation pure. Cost: edits a shipped counting rule shared by every op to accommodate one step; 133's parity gate has an exemption row pointing at it. | |
| SKIPPED, exit 0, trust the field | No exit-map change; LEG-12's wording anticipates exit 0. Cost: the command returns 0 and a reporter files it as PASS — the P-04 shape. | |

**User's choice:** SKIPPED + exit floor of 2 → **D-15**
**Notes:** Raised the interaction rather than resolving it silently — recording a non-running oracle as
`marginal` would have satisfied the exit requirement while breaking LEG-13, because
`_RAN_VERDICTS = {OK, BAD, MARGINAL}` counts marginal as *ran*. Also measured and recorded: for ALLOW
chips the SDP steps carry `supported=True`, so `count_applicable` already includes them in M and already
excludes a SKIPPED result from N — **LEG-13 needs a pinning test, not new counting logic.**

### Q3 — LEG-17's R1/R2, which research measured as structurally vacuous

| Option | Description | Selected |
|--------|-------------|----------|
| Synthetic chip-id, labelled (Rec.) | Drive R1/R2 through a synthetic DB entry with a NONZERO chip-id so the full chain (id step → mismatch → gate closes → `sdp_lock` not called → NOT-RUN rendered) is exercised; label them in-source and in the record as unreachable in production today. | ✓ |
| Force the gate flag directly | Simpler fixture. Cost: proves the gate, not the route — the id-step→gate causation goes untested. | |
| Test four, record R1/R2 unreachable | Most literal about the evidence ceiling. Cost: LEG-17 says six and would be ticked at four. | |

**User's choice:** Synthetic chip-id, labelled → **D-17**
**Notes:** All 43 ALLOW chips have `chip-id == 0`, so the id step is NA and an NA id step does not close
the gate. Recorded that requirements and report text must not claim "the leg is gated by chip ID" —
research §2.6 flags that as a v1.22 C-5 class overclaim.

### Q4 — How is the gh#20 triage discharged, and where does the reply happen?

| Option | Description | Selected |
|--------|-------------|----------|
| Record in 134, reply at 137 (Rec.) | Write the finding into this phase's record; file the underlying AT28C256 write failure as a backlog item with a named owner; hand the public reply to Phase 137 behind CLOSE-06's blocking operator wording review. | ✓ |
| Comment on gh#20 in this phase | Answers the reporter while context is fresh. Cost: an outward-facing claim about an unclosed milestone, before the claim gate policing that wording is armed. | |
| Record only, no reply planned | Satisfies LEG-18 literally, smallest surface. Cost: a community member who filed a real report gets no response and nothing schedules one. | |

**User's choice:** Record in 134, reply at 137 → **D-16**
**Notes:** LEG-18's own text says the finding is "recorded", not posted — the posting is a separate act.
gh#20 was read in full during the session: AT28C256, host `3.0.0b14`, Rev 2.3, `blank-check`/`write`/
`verify` all BAD, fingerprint `indeterminate`, banner `4 of 4`, VPP 11.8 V / VPE 13.7 V.

---

## Claude's Discretion

Two areas taken on measurement rather than asked, both recorded with their reasoning in CONTEXT.md:

- **D-18** — The SDP leg is gated on `write_execute`; all six steps go to `locked_destructive` when
  `write_scope="none"` (research R5's own prevention text). Self-consistent because
  `locked_destructive` entries count toward M, so `N < M` and the banner fires, matching D-15's polarity.
  Noted that `write_scope="none"` is unreachable from `dev test` since Phase 121's reversal, so this is
  library/test surface — stated rather than implied to gate a live path.
- **D-19** — The inhibited-write payload gets its own named generator (`B = bytes(~x & 0xFF for x in A)`)
  plus a lint-style test asserting it is *not* `generate_pattern`'s output for the plan's region, and
  P-01's five committed assertions including "differ at **every** byte". A nonce/timestamp is rejected —
  it breaks reproducibility and the `dedup_fingerprint` hash.

Also captured without a question: **D-05**, the non-laundering test obligation created by D-04's use of
`classify_fingerprint`.

## Deferred Ideas

- The `tools/check_*.py` host-side string-literal claim scanner over `diagnostic_report.py` — Phase 137,
  CLOSE-03 (D-13 hands it the constant names).
- The gh#20 public reply — Phase 137, behind CLOSE-06's blocking operator wording review (D-16).
- The underlying AT28C256 write/verify/blank-check failure in gh#20 — to be filed as a backlog item with
  a named owner (D-16).
- The `dedup_fingerprint` discontinuity's outward description — Phase 137 release notes, CLOSE-05 (D-11).
- `write --sdp-relock` — Backlog 999.28 by operator decision 2026-08-03.
- Ratcheting the mypy watermark to the measured count — still unowned (133-RECORD residual 4), now at 2
  of headroom.
- Adding this phase's new test modules to the mypy test strict-island — measure first (133-RECORD
  residual 5).
- 133 D-07's forfeited report on Ctrl-C — no owner; explicitly not adopted here.
- Refreshing `.planning/codebase/TESTING.md` — a `/gsd-map-codebase` task; severely stale today.
- The four pre-existing `ruff` failures in `tools/` — outside CI's ruff scope; a lint-debt sweep.

## Scope creep

None raised. Every candidate expansion that surfaced (the ack seam into `eprom_operations.py`, authoring
Phase 137's `tools/` scanner early, commenting on gh#20 now) was presented as an option, weighed, and
declined in favour of the in-scope alternative.
